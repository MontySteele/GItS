using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;

namespace KleeMod.Powers;

/// <summary>Where a hit lands.</summary>
public enum StageTarget
{
    /// <summary>Every enemy.</summary>
    All,

    /// <summary>A random enemy.</summary>
    Random,

    /// <summary>A random enemy with an aura; none, and nothing is hit
    /// (Lynette's act).</summary>
    Aura,
}

/// <summary>
/// THE BOARD HALF of the kit: everything a Drain, a Repay, an act or a line
/// does to the game, as commands. The rules (<see cref="StageDirector"/>)
/// decide what and in what order; this does it. The game's implementation is
/// <see cref="GameStageBoard"/>; the headless pins hand the director a board
/// that records the calls and keeps an HP number, so every rule edge is
/// testable without a combat.
/// </summary>
public interface IStageBoard
{
    /// <summary>Furina is dead or the combat is over or ending.</summary>
    bool Over { get; }

    /// <summary>Furina's HP now.</summary>
    int Hp { get; }

    /// <summary>Furina's Max HP now.</summary>
    int MaxHp { get; }

    /// <summary>A Drain's HP loss: unblockable and unpowered. Returns the HP
    /// actually lost.</summary>
    Task<int> LoseHp(int amount);

    /// <summary>A Repay's HP back. Returns the HP actually regained.</summary>
    Task<int> Heal(int amount);

    /// <summary>A guest's act or line: unpowered, in its element.</summary>
    Task Damage(StagePerformer who, StageTarget target, int amount,
                Element element);

    /// <summary>A Power's hit (Salon's Encore, Endless Waltz, Thunderous
    /// Applause): unpowered, no element.</summary>
    Task PowerHit(string source, StageTarget target, int amount);

    Task Draw(int amount);

    /// <summary>The guest's body moves (a lunge), before its act.</summary>
    Task Lunge(StageSeat? seat);

    /// <summary>The bodies catch up with the seats.</summary>
    Task Sync();
}

/// <summary>What a guest summon did (rule 5).</summary>
public enum StageSummonResult
{
    Seated,
    Repeat,
    Evict,
}

/// <summary>How a summon makes room, decided before it happens: the seat it
/// touches (<see cref="Index"/>: the guest that acts and leaves on an
/// eviction, the guest that acts and stays on a repeat; -1 otherwise).
/// </summary>
public readonly record struct StageRoom(StageSummonResult Kind, int Index);

/// <summary>
/// THE KIT'S RULES, IN ORDER (the Salon's Tab, 2026-10-05). Every method is
/// the sim's twin of the same name in <c>tier0/engine/furina_tide.py</c>.
///
/// IT OWNS NO STATE: the seats and the numbers are the ledger's, the board
/// half is the board's. So the game and the headless pins run the very same
/// rules.
/// </summary>
public sealed class StageDirector
{
    public const string SalonsEncoreTitle = "Salon's Encore";
    public const string EndlessWaltzTitle = "Endless Waltz";
    public const string ThunderousTitle = "Thunderous Applause";

    private readonly FurinaStageLedger _stage;
    private readonly IStageBoard _board;

    public StageDirector(FurinaStageLedger stage, IStageBoard board)
    {
        _stage = stage;
        _board = board;
    }

    public FurinaStageLedger Stage => _stage;

    // ---- Fanfare (rule 3) --------------------------------------------------

    /// <summary>Gain Fanfare (Universal Revelry multiplies it).</summary>
    public int Gain(int amount, string source = "") =>
        _stage.Gain(amount, source);

    /// <summary>A Spend N. Thunderous Applause answers a Spend that moved
    /// Fanfare. Returns what was paid.</summary>
    public async Task<int> Spend(int price)
    {
        if (!_stage.Spend(price)) return 0;
        await Thunderous();
        return price;
    }

    /// <summary>"Spend all your Fanfare": one Spend. Returns what was spent
    /// (0 held is no Spend).</summary>
    public async Task<int> SpendAll()
    {
        var spent = _stage.SpendAll();
        if (spent > 0) await Thunderous();
        return spent;
    }

    private async Task Thunderous()
    {
        var damage = _stage.Mods.Thunderous;
        if (damage <= 0 || _board.Over) return;
        await _board.PowerHit(ThunderousTitle, StageTarget.All, damage);
    }

    /// <summary>Rule 3: HP lost to anything but a Drain (a hit past Block, a
    /// status, a card's own HP cost) prints 1 Fanfare a point.</summary>
    public int OnHpLost(int amount)
    {
        if (amount <= 0 || _stage.Draining) return 0;
        return _stage.Gain(amount, "HP lost");
    }

    /// <summary>Lynette's line: "The first time each turn an enemy makes you
    /// lose HP, gain that much Fanfare again."</summary>
    public int OnEnemyHit(int hpLost)
    {
        if (hpLost <= 0 || !_stage.OnStage(StagePerformer.Lynette)
            || _stage.LynetteFiredThisTurn)
        {
            return 0;
        }
        _stage.LynetteFiredThisTurn = true;
        return _stage.Gain(hpLost, "Lynette");
    }

    // ---- the HP loan (rules 1 and 2) ---------------------------------------

    /// <summary>Rule 1: can she Drain <paramref name="amount"/> now?</summary>
    public bool CanDrain(int amount) => _stage.CanDrain(amount, _board.Hp);

    /// <summary>
    /// Rule 1, Drain N: lose N HP (never below the line), mark it drained,
    /// gain that much Fanfare, then the Drain readers -- Salon's Encore,
    /// Wriothesley's line. False (nothing happens) when it would cross the
    /// line.
    /// </summary>
    public async Task<bool> Drain(int amount)
    {
        if (!CanDrain(amount)) return false;
        int lost;
        _stage.Draining = true;
        try
        {
            lost = await _board.LoseHp(amount);
        }
        finally
        {
            _stage.Draining = false;
        }
        if (lost <= 0) return true;
        _stage.NoteDrain(lost);
        _stage.Note(new StageBeat(FurinaStageLedger.DrainEvent, default, -1,
                                  _stage.Fanfare, lost, ""));
        _stage.Gain(lost, "Drain");
        var encore = _stage.Mods.SalonsEncore;
        if (encore > 0 && !_board.Over)
        {
            await _board.PowerHit(SalonsEncoreTitle, StageTarget.All, encore);
        }
        if (_stage.OnStage(StagePerformer.Wriothesley) && !_board.Over)
        {
            await _board.Damage(StagePerformer.Wriothesley, StageTarget.Random,
                                lost, Element.Cryo);
        }
        return true;
    }

    /// <summary>
    /// Rule 2, Repay N: regain up to N drained HP (never more than drained,
    /// never past Max HP), gain that much Fanfare, then the Repay readers --
    /// Endless Waltz, Clorinde's line, Charlotte's line. Returns HP repaid.
    /// </summary>
    public async Task<int> Repay(int amount)
    {
        var room = _stage.RepayRoom(amount, _board.Hp, _board.MaxHp);
        if (room <= 0 || _board.Over) return 0;
        var back = await _board.Heal(room);
        if (back <= 0) return 0;
        _stage.NoteRepay(back);
        _stage.Note(new StageBeat(FurinaStageLedger.RepayEvent, default, -1,
                                  _stage.Fanfare, back, ""));
        _stage.Gain(back, "Repay");
        for (var i = 0; i < _stage.Mods.EndlessWaltz; i++)
        {
            if (_board.Over) break;
            await _board.PowerHit(EndlessWaltzTitle, StageTarget.Random, back);
        }
        if (_stage.OnStage(StagePerformer.Clorinde) && !_board.Over)
        {
            await _board.Damage(StagePerformer.Clorinde, StageTarget.Random,
                                FurinaStageLaw.ClorindePerRepay * back,
                                Element.Electro);
        }
        if (_stage.OnStage(StagePerformer.Charlotte)
            && !_stage.CharlotteDrewThisTurn && !_board.Over)
        {
            _stage.CharlotteDrewThisTurn = true;
            await _board.Draw(FurinaStageLaw.CharlotteLineDraw);
        }
        return back;
    }

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public Task<int> RepayAll() => Repay(_stage.Drained);

    /// <summary>THE CURTAIN CALL (sec.16): when the combat ends, every
    /// drained HP returns. Not a Repay: no Fanfare, no readers. Returns the
    /// HP returned.</summary>
    public async Task<int> CurtainCall()
    {
        var back = _stage.CurtainCall(_board.Hp, _board.MaxHp);
        if (back <= 0) return 0;
        return await _board.Heal(back);
    }

    // ---- the guests (rule 5) -----------------------------------------------

    /// <summary>One guest's act. <paramref name="seat"/> is null for a guest
    /// that has already left (its once-more act as it goes).</summary>
    public async Task<bool> Act(StagePerformer who, StageSeat? seat)
    {
        if (_board.Over) return false;
        await _board.Lunge(seat);
        var moved = 0;
        switch (who)
        {
            case StagePerformer.Charlotte:
                moved = await Repay(FurinaStageLaw.CharlotteActRepay);
                break;
            case StagePerformer.Wriothesley:
                moved = FurinaStageLaw.WriothesleyActDamage;
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.Cryo);
                break;
            case StagePerformer.Lynette:
                moved = FurinaStageLaw.LynetteActDamage;
                await _board.Damage(who, StageTarget.Aura, moved,
                                    Element.Anemo);
                break;
            case StagePerformer.Clorinde:
                moved = FurinaStageLaw.ClorindeActDamage;
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.Electro);
                break;
        }
        _stage.Note(new StageBeat(FurinaStageLedger.ActEvent, who,
                                  seat == null ? -1 : _stage.IndexOf(seat),
                                  _stage.Fanfare, moved, "",
                                  SeatKey: seat?.Key ?? -1));
        return true;
    }

    /// <summary>
    /// A Guest Star card. A guest already on stage acts and keeps its seat.
    /// Otherwise a free seat at the back; on a full stage the oldest guest
    /// leaves first, acting once more as it goes.
    /// </summary>
    public async Task<StageSummonResult> SummonGuest(StagePerformer who)
    {
        var room = GuestRoom(_stage.Company.ToList(), _stage.Capacity, who);
        if (room.Kind == StageSummonResult.Repeat)
        {
            await Act(who, _stage.Seats[room.Index]);
            return room.Kind;
        }
        if (room.Kind == StageSummonResult.Evict)
        {
            var leaver = _stage.Unseat(room.Index, "evicted");
            await _board.Sync();
            if (leaver != null) await Act(leaver.Who, null);
        }
        _stage.Seat(who);
        await _board.Sync();
        return room.Kind;
    }

    /// <summary>Rule 5 over a company, front (oldest) first. PURE: the
    /// summon above acts on it and the card face previews it
    /// (<see cref="FurinaStageBowPreview"/>), so they cannot drift.</summary>
    public static StageRoom GuestRoom(IReadOnlyList<StagePerformer> company,
                                      int capacity, StagePerformer who)
    {
        for (var i = 0; i < company.Count; i++)
        {
            if (company[i] == who) return new(StageSummonResult.Repeat, i);
        }
        return company.Count < capacity
            ? new(StageSummonResult.Seated, -1)
            : new(StageSummonResult.Evict, 0);
    }

    /// <summary>
    /// The end of her turn: every guest acts, front to back, over a snapshot
    /// of the stage; then Salon Solitaire's Singer Repays
    /// <paramref name="singer"/> (0 without the relic).
    /// </summary>
    public async Task EndOfTurn(int singer)
    {
        foreach (var seat in _stage.Seats.ToList())
        {
            if (_board.Over) return;
            if (!_stage.Holds(seat)) continue;
            await Act(seat.Who, seat);
        }
        if (singer > 0 && !_board.Over) await Repay(singer);
    }
}
