using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Models;

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

    /// <summary>A Power's hit (Salon's Encore, Thunderous Applause,
    /// Critics' Darling): unpowered, no element.</summary>
    Task PowerHit(string source, StageTarget target, int amount);

    /// <summary>Furina gains Block (Sigewinne's and Freminet's lines,
    /// Freminet's act, the Repay floor): unpowered.</summary>
    Task Block(int amount);

    /// <summary>Furina gains Vigor (the Repay floor of Soothing Waters and
    /// Pneuma Tides): the base game's <c>VigorPower</c>.</summary>
    Task Vigor(int amount);

    /// <summary>Vulnerable on an enemy (Chevreuse's line).</summary>
    Task Vulnerable(StageTarget target, int amount);

    /// <summary>Weak on an enemy (Chevreuse's upgraded line).</summary>
    Task Weak(StageTarget target, int amount);

    /// <summary>Furina gains Strength (Standing Room Only, Hymn of Renewal,
    /// Regina of All Waters).</summary>
    Task Strength(int amount);

    Task Draw(int amount);

    /// <summary>The guest's body moves (a lunge), before its act.</summary>
    Task Lunge(StageSeat? seat);

    /// <summary>A guest's LINE fired: a small cue on its body, distinct from
    /// an act's lunge (the pool to 75, sec.3).</summary>
    Task LineCue(StageSeat? seat);

    /// <summary>The guest left the stage: its Guest Star cards go from the
    /// exhaust pile to the discard pile (the pool to 75, sec.3).</summary>
    Task ReturnCards(StageSeat seat);

    /// <summary>The bodies catch up with the seats.</summary>
    Task Sync();
}

/// <summary>What a guest summon did (rule 5).</summary>
public enum StageSummonResult
{
    Seated,

    /// <summary>A duplicate copy: the guest already on stage moves to the
    /// newest seat, with no act (the pool to 75, sec.3).</summary>
    Repeat,

    /// <summary>A full stage: the oldest guest leaves (no act) and the new
    /// one takes the back seat.</summary>
    Evict,
}

/// <summary>
/// THE REPAY FLOOR (ruled 2026-10-09): "Repay N. Gain X for any HP it could
/// not Repay." What a Repay pays for the part of N it could not return.
/// The damage cards' floor (Surging Waters, Hydro Lance, Cleansing Torrent)
/// is their own damage, read off
/// <see cref="FurinaStageLedger.RepayLeftThisPlay"/>, so it is not here.
/// </summary>
public enum StageFloor
{
    /// <summary>No floor: a plain Repay.</summary>
    None,

    /// <summary>"Gain 1 Block for any HP it could not Repay."</summary>
    Block,

    /// <summary>"Gain 1 Vigor for any HP it could not Repay."</summary>
    Vigor,
}

/// <summary>How a summon makes room, decided before it happens: the seat it
/// touches (<see cref="Index"/>: the guest that leaves on an eviction, the
/// guest that moves on a repeat; -1 otherwise).
/// </summary>
public readonly record struct StageRoom(StageSummonResult Kind, int Index);

/// <summary>
/// THE KIT'S RULES, IN ORDER (the Salon's Tab, 2026-10-05; the guest rule of
/// the pool to 75, <c>review/active/furina-pool-growth-2026-10-09.md</c>
/// sec.3). Every method is the sim's twin of the same name in
/// <c>tier0/engine/furina_tide.py</c>.
///
/// IT OWNS NO STATE: the seats and the numbers are the ledger's, the board
/// half is the board's. So the game and the headless pins run the very same
/// rules.
/// </summary>
public sealed class StageDirector
{
    public const string SalonsEncoreTitle = "Salon's Encore";
    public const string ThunderousTitle = "Thunderous Applause";
    public const string RevelryTitle = "Universal Revelry";
    public const string CriticsDarlingTitle = "Critics' Darling";
    public const string GrandEntranceTitle = "Grand Entrance";
    public const string ShowstopperTitle = "Showstopper";
    public const string PneumaTidesTitle = "Pneuma Tides";
    public const string ReginaTitle = "Regina of All Waters";
    public const string MasqueradeTitle = "The Masquerade";

    private readonly FurinaStageLedger _stage;
    private readonly IStageBoard _board;

    public StageDirector(FurinaStageLedger stage, IStageBoard board)
    {
        _stage = stage;
        _board = board;
    }

    public FurinaStageLedger Stage => _stage;

    // ---- Fanfare (rule 3) --------------------------------------------------

    /// <summary>Gain Fanfare (a relic, a potion).</summary>
    public int Gain(int amount, string source = "") =>
        _stage.Gain(amount, source);

    /// <summary>A Spend N. Thunderous Applause, Chevreuse's line and
    /// Crescendo answer a Spend. Returns the price when the Spend was made
    /// (Navia's line may take less from the bank), 0 when it was not.
    /// </summary>
    public async Task<int> Spend(int price)
    {
        var navia = _stage.NaviaDiscount > 0 && price > 0
            ? _stage.SeatOf(StagePerformer.Navia) : null;
        if (!_stage.Spend(price)) return 0;
        if (navia != null) await _board.LineCue(navia);
        await AfterSpend();
        return price;
    }

    /// <summary>"Spend all your Fanfare": one Spend. Returns what the card
    /// reads (the whole bank; 0 held is no Spend). Standing Room Only answers
    /// a spend-all of at least 1.</summary>
    public async Task<int> SpendAll()
    {
        var navia = _stage.NaviaDiscount > 0 && _stage.Fanfare > 0
            ? _stage.SeatOf(StagePerformer.Navia) : null;
        var spent = _stage.SpendAll();
        if (spent > 0)
        {
            if (navia != null) await _board.LineCue(navia);
            await AfterSpend();
            var sro = _stage.Mods.StandingRoomOnly;
            if (sro > 0 && !_board.Over) await _board.Strength(sro);
        }
        return spent;
    }

    private async Task AfterSpend()
    {
        await Thunderous();
        await Chevreuse();
        var crescendo = _stage.Mods.Crescendo;
        if (crescendo > 0 && _stage.SpendsThisTurn == 1 && !_board.Over)
        {
            await _board.Draw(crescendo);
        }
    }

    /// <summary>Chevreuse's line: "Whenever you Spend, apply 1 Vulnerable to
    /// a random enemy." Upgraded: also 1 Weak.</summary>
    private async Task Chevreuse()
    {
        var seat = _stage.SeatOf(StagePerformer.Chevreuse);
        if (seat == null || _board.Over) return;
        _stage.NoteLine(StagePerformer.Chevreuse,
                        FurinaStageLaw.ChevreuseLineVulnerable);
        await _board.LineCue(seat);
        await _board.Vulnerable(StageTarget.Random,
                                FurinaStageLaw.ChevreuseLineVulnerable);
        if (seat.Upgraded && !_board.Over)
        {
            await _board.Weak(StageTarget.Random,
                              FurinaStageLaw.ChevreuseLineWeakUpgraded);
        }
    }

    /// <summary>The readers of a Drain or a Repay of
    /// <paramref name="amount"/> (never of a hit): Universal Revelry gains
    /// that much more Fanfare per copy, and Critics' Darling deals that much
    /// per copy to a random enemy. Neither triggers itself.</summary>
    private async Task LoopReaders(int amount)
    {
        var revelry = _stage.Mods.Revelry;
        if (revelry > 0) _stage.Gain(amount * revelry, RevelryTitle);
        var critics = _stage.Mods.CriticsDarling;
        if (critics > 0 && !_board.Over)
        {
            await PowerHit(CriticsDarlingTitle, StageTarget.Random,
                           amount * critics);
        }
    }

    /// <summary>A Power's hit (Critics' Darling, Salon's Encore, Thunderous
    /// Applause), with a line in the stage log naming the Power (the
    /// drain-line round, 2026-10-09: Critics' Darling's damage did not show
    /// in the play log, so a seat could not see it).</summary>
    private async Task PowerHit(string title, StageTarget target, int amount)
    {
        if (amount <= 0) return;
        await _board.PowerHit(title, target, amount);
        _stage.Note(new StageBeat(FurinaStageLedger.HitEvent, default, -1,
                                  _stage.Fanfare, amount,
                                  target == StageTarget.All ? "all" : "random",
                                  Source: title));
    }

    private async Task Thunderous()
    {
        var damage = _stage.Mods.Thunderous;
        if (damage <= 0 || _board.Over) return;
        await PowerHit(ThunderousTitle, StageTarget.All, damage);
    }

    /// <summary>Rule 3: HP lost to anything but a Drain (a hit past Block, a
    /// status, a card's own HP cost) prints 1 Fanfare a point.</summary>
    public int OnHpLost(int amount)
    {
        if (amount <= 0 || _stage.Draining) return 0;
        _stage.NoteHpLost(amount);
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
        var gained = _stage.Gain(hpLost, "Lynette");
        _stage.NoteLine(StagePerformer.Lynette, gained);
        return gained;
    }

    // ---- the HP loan (rules 1 and 2) ---------------------------------------

    /// <summary>Rule 1: can she Drain <paramref name="amount"/> now? Only a
    /// Drain to 0 HP or below is refused (2026-10-09).</summary>
    public bool CanDrain(int amount) => _stage.CanDrain(amount, _board.Hp);

    /// <summary>A guest act's Drain of <paramref name="amount"/>, stopped
    /// at the line (the drain-line round, 2026-10-09): the part of it that
    /// fits above the line, 0 when there is no room. The player's own Drains
    /// may still go past the line.</summary>
    public int GuestDrainRoom(int amount) =>
        _stage.GuestDrainRoom(amount, _board.Hp);

    /// <summary>
    /// Rule 1, Drain N: lose N HP, mark it drained -- above the line or past
    /// it (2026-10-09) -- gain that much Fanfare, then the Drain readers --
    /// Salon's Encore, Wriothesley's and Freminet's lines, Ousia Surge. False
    /// (nothing happens) when it would take her to 0 HP or below.
    /// </summary>
    public async Task<bool> Drain(int amount)
    {
        if (!CanDrain(amount)) return false;
        var hpBefore = _board.Hp;
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
        _stage.NoteDrain(lost, hpBefore);
        _stage.Note(new StageBeat(FurinaStageLedger.DrainEvent, default, -1,
                                  _stage.Fanfare, lost, ""));
        _stage.Gain(lost, "Drain");
        await LoopReaders(lost);
        // The Masquerade (the block gap, 2026-10-09): "Whenever you Drain,
        // gain that much Block." The HP actually drained, past the line
        // included; a guest act's Drain arrives here already stopped at the
        // line. A Power's Block: unpowered, as Feel No Pain's.
        var masquerade = _stage.Mods.Masquerade;
        if (masquerade > 0 && !_board.Over)
        {
            await _board.Block(lost * masquerade);
        }
        var encore = _stage.Mods.SalonsEncore;
        if (encore > 0 && !_board.Over)
        {
            await PowerHit(SalonsEncoreTitle, StageTarget.All, encore);
        }
        if (_stage.SeatOf(StagePerformer.Wriothesley) is { } wrio
            && !_board.Over)
        {
            _stage.NoteLine(StagePerformer.Wriothesley, lost);
            await _board.LineCue(wrio);
            await _board.Damage(StagePerformer.Wriothesley, StageTarget.Random,
                                lost, Element.Cryo);
        }
        if (_stage.SeatOf(StagePerformer.Freminet) is { } freminet
            && !_board.Over)
        {
            _stage.NoteLine(StagePerformer.Freminet, lost);
            await _board.LineCue(freminet);
            await _board.Block(lost);
        }
        var surge = _stage.Mods.OusiaSurge;
        if (surge > 0 && !_stage.OusiaDrewThisTurn && !_board.Over)
        {
            _stage.OusiaDrewThisTurn = true;
            await _board.Draw(surge);
        }
        return true;
    }

    /// <summary>
    /// Rule 2, Repay N: regain up to N drained HP (never more than drained,
    /// never past Max HP; the past-line part first), gain that much Fanfare,
    /// then the Repay readers -- Clorinde's, Charlotte's and Sigewinne's
    /// lines, and Hymn of Renewal (on 4 or more HP actually repaid). Returns
    /// HP repaid.
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
        await LoopReaders(back);
        if (_stage.SeatOf(StagePerformer.Clorinde) is { } clorinde
            && !_board.Over)
        {
            _stage.NoteLine(StagePerformer.Clorinde,
                            FurinaStageLaw.ClorindePerRepay * back);
            await _board.LineCue(clorinde);
            await _board.Damage(StagePerformer.Clorinde, StageTarget.Random,
                                FurinaStageLaw.ClorindePerRepay * back,
                                Element.Electro);
        }
        if (_stage.SeatOf(StagePerformer.Charlotte) is { } charlotte
            && !_stage.CharlotteDrewThisTurn && !_board.Over)
        {
            _stage.CharlotteDrewThisTurn = true;
            _stage.NoteLine(StagePerformer.Charlotte,
                            FurinaStageLaw.CharlotteLineDraw);
            await _board.LineCue(charlotte);
            await _board.Draw(FurinaStageLaw.CharlotteLineDraw);
        }
        if (_stage.SeatOf(StagePerformer.Sigewinne) is { } sigewinne
            && !_board.Over)
        {
            _stage.NoteLine(StagePerformer.Sigewinne, back);
            await _board.LineCue(sigewinne);
            await _board.Block(back);
        }
        var hymn = _stage.Mods.HymnOfRenewal;
        if (hymn > 0 && back >= FurinaStageLaw.HymnThreshold && !_board.Over)
        {
            await _board.Strength(hymn);
        }
        return back;
    }

    /// <summary>
    /// THE REPAY FLOOR (ruled 2026-10-09): "Repay N. Gain X for any HP it
    /// could not Repay." The Repay resolves first; the leftover, N minus the
    /// HP it returned, is paid as Block or Vigor. Returns HP repaid.
    /// </summary>
    public async Task<int> RepayFloor(int amount, StageFloor floor)
    {
        if (amount <= 0) return 0;
        var back = await Repay(amount);
        var left = amount - back;
        if (left <= 0 || _board.Over) return back;
        switch (floor)
        {
            case StageFloor.Block:
                await _board.Block(left);
                break;
            case StageFloor.Vigor:
                await _board.Vigor(left);
                break;
        }
        return back;
    }

    /// <summary>Fountain of Lucine: at the start of her turn, each play still
    /// owed Repays its amount, one Repay per play, each with its Block floor
    /// (2026-10-09).</summary>
    public async Task<int> TurnStartRepays()
    {
        var total = 0;
        foreach (var amount in _stage.TakeDueRepays())
        {
            if (_board.Over) break;
            total += await RepayFloor(amount, StageFloor.Block);
        }
        return total;
    }

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public Task<int> RepayAll() => Repay(_stage.Drained);

    /// <summary>THE CURTAIN CALL (sec.16; the Drain line rule, 2026-10-09):
    /// when the combat ends, the HP drained above the line returns (and the
    /// HP drained past it, with A Five-Century Act). Not a Repay: no
    /// Fanfare, no readers. Returns the HP returned.</summary>
    public async Task<int> CurtainCall()
    {
        var back = _stage.CurtainCall(_board.Hp, _board.MaxHp);
        if (back <= 0) return 0;
        return await _board.Heal(back);
    }

    // ---- the turn-start Powers (the pool to 75) ----------------------------

    /// <summary>Pneuma Tides: "At the start of your turn, Repay 2. Gain 1
    /// Vigor for any HP it could not Repay." One Repay of the summed amount.
    /// </summary>
    public async Task<int> PneumaTides(int amount)
    {
        if (amount <= 0 || _board.Over) return 0;
        return await RepayFloor(amount, StageFloor.Vigor);
    }

    /// <summary>Regina of All Waters: "At the start of your turn, Drain 3. If
    /// you do, gain 1 Strength." Each copy is its own Drain and its own
    /// Strength. Returns the copies that drained.</summary>
    public async Task<int> Regina(int copies)
    {
        var done = 0;
        for (var i = 0; i < copies; i++)
        {
            if (_board.Over || !CanDrain(FurinaStageLaw.ReginaDrain)) break;
            if (!await Drain(FurinaStageLaw.ReginaDrain)) break;
            done++;
            if (!_board.Over) await _board.Strength(1);
        }
        return done;
    }

    // ---- the guests (rule 5, the pool to 75's sec.3) -----------------------

    /// <summary>A guest's act number as its seat holds it: the upgraded
    /// number when an upgraded Guest Star brought it.</summary>
    public static int ActAmount(StagePerformer who, bool upgraded) => who switch
    {
        StagePerformer.Charlotte => upgraded
            ? FurinaStageLaw.CharlotteActRepayUpgraded
            : FurinaStageLaw.CharlotteActRepay,
        StagePerformer.Sigewinne => upgraded
            ? FurinaStageLaw.SigewinneActRepayUpgraded
            : FurinaStageLaw.SigewinneActRepay,
        StagePerformer.Wriothesley => upgraded
            ? FurinaStageLaw.WriothesleyActDamageUpgraded
            : FurinaStageLaw.WriothesleyActDamage,
        StagePerformer.Lynette => upgraded
            ? FurinaStageLaw.LynetteActDamageUpgraded
            : FurinaStageLaw.LynetteActDamage,
        StagePerformer.Clorinde => upgraded
            ? FurinaStageLaw.ClorindeActDamageUpgraded
            : FurinaStageLaw.ClorindeActDamage,
        StagePerformer.Lyney => upgraded
            ? FurinaStageLaw.LyneyActDamageUpgraded
            : FurinaStageLaw.LyneyActDamage,
        StagePerformer.Chevreuse => FurinaStageLaw.ChevreuseActDamage,
        StagePerformer.Freminet => upgraded
            ? FurinaStageLaw.FreminetActDamageUpgraded
            : FurinaStageLaw.FreminetActDamage,
        StagePerformer.Escoffier => upgraded
            ? FurinaStageLaw.EscoffierActDamageUpgraded
            : FurinaStageLaw.EscoffierActDamage,
        // Navia's and Neuvillette's acts read the turn (Fanfare spent, HP
        // drained), not a printed number.
        _ => 0,
    };

    /// <summary>Freminet's act's Block: 6, 9 upgraded.</summary>
    public static int FreminetActBlock(bool upgraded) => upgraded
        ? FurinaStageLaw.FreminetActBlockUpgraded
        : FurinaStageLaw.FreminetActBlock;

    /// <summary>One guest's act, at the end of her turn or bought by a card
    /// (Encore!, Tutti!, Final Bow, Bring the House Down, Showstopper).
    /// Escoffier's line answers every act, his own included.</summary>
    public async Task<bool> Act(StageSeat seat)
    {
        if (_board.Over) return false;
        var who = seat.Who;
        await _board.Lunge(seat);
        var moved = 0;
        var number = ActAmount(who, seat.Upgraded);
        switch (who)
        {
            case StagePerformer.Charlotte:
            case StagePerformer.Sigewinne:
                // "Repay 2. Gain 1 Block for any HP it could not Repay."
                // (the Repay floor, 2026-10-09).
                moved = await RepayFloor(number, StageFloor.Block);
                break;
            case StagePerformer.Wriothesley:
                moved = number;
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.Cryo);
                break;
            case StagePerformer.Lynette:
                moved = number;
                await _board.Damage(who, StageTarget.Aura, moved,
                                    Element.Anemo);
                break;
            case StagePerformer.Clorinde:
                moved = number;
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.Electro);
                break;
            case StagePerformer.Lyney:
                // "Drain 2, never past your line. Deal 8 Pyro damage to
                // ALL enemies." A guest acts with no choice from the
                // player, so its Drain stops at the line (the drain-line
                // round, 2026-10-09): it drains only the room above the
                // line, 0 with none, and the damage lands either way.
                var room = GuestDrainRoom(FurinaStageLaw.LyneyActDrain);
                if (room > 0) await Drain(room);
                if (!_board.Over)
                {
                    moved = number;
                    await _board.Damage(who, StageTarget.All, moved,
                                        Element.Pyro);
                }
                break;
            case StagePerformer.Chevreuse:
                moved = number;
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.None);
                break;
            case StagePerformer.Freminet:
                // "Deal 5 Cryo damage to a random enemy. Gain 6 Block." [8,
                // 9] (the Block, ruled 2026-10-09).
                moved = number;
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.Cryo);
                if (!_board.Over)
                {
                    await _board.Block(FreminetActBlock(seat.Upgraded));
                }
                break;
            case StagePerformer.Navia:
                // "Deal Geo damage to a random enemy equal to the Fanfare you
                // spent this turn." Nothing spent, nothing dealt.
                moved = _stage.SpentThisTurn;
                if (moved > 0)
                {
                    await _board.Damage(who, StageTarget.Random, moved,
                                        Element.Geo);
                }
                break;
            case StagePerformer.Neuvillette:
                // "Deal Hydro damage to ALL enemies equal to the HP you lost
                // since your last turn." (2026-10-09: Drained or taken.)
                moved = _stage.HpLostSinceLastTurn;
                if (moved > 0)
                {
                    await _board.Damage(who, StageTarget.All, moved,
                                        Element.Hydro);
                }
                break;
            case StagePerformer.Escoffier:
                moved = number;
                await _board.Damage(who, StageTarget.All, moved,
                                    Element.Cryo);
                break;
        }
        _stage.Note(new StageBeat(FurinaStageLedger.ActEvent, who,
                                  _stage.IndexOf(seat), _stage.Fanfare, moved,
                                  "", SeatKey: seat.Key));
        if (_stage.SeatOf(StagePerformer.Escoffier) is { } escoffier
            && !_board.Over)
        {
            _stage.NoteLine(StagePerformer.Escoffier,
                            FurinaStageLaw.EscoffierLineRepay);
            await _board.LineCue(escoffier);
            await Repay(FurinaStageLaw.EscoffierLineRepay);
        }
        return true;
    }

    /// <summary>
    /// A Guest Star card (the pool to 75, sec.3). No effect on summon. A
    /// guest already on stage moves to the newest seat with no act; otherwise
    /// it takes a free seat at the back, and on a full stage the oldest guest
    /// leaves first (no act) and its cards go to the discard pile.
    /// <paramref name="card"/> (null headless) is the Guest Star played: it
    /// exhausts, and the seat holds it until its guest leaves.
    /// </summary>
    public async Task<StageSummonResult> SummonGuest(
        StagePerformer who, bool upgraded = false, CardModel? card = null)
    {
        var room = GuestRoom(_stage.Company.ToList(), _stage.Capacity, who);
        if (room.Kind == StageSummonResult.Repeat)
        {
            var moved = _stage.MoveToBack(room.Index)!;
            moved.Upgraded |= upgraded;
            if (card != null) moved.Cards.Add(card);
            await _board.Sync();
            return room.Kind;
        }
        if (room.Kind == StageSummonResult.Evict)
        {
            await Leave(room.Index, "evicted");
        }
        var seat = _stage.Seat(who, upgraded);
        if (seat != null && card != null) seat.Cards.Add(card);
        await _board.Sync();
        return room.Kind;
    }

    /// <summary>The guest in <paramref name="index"/> leaves the stage: its
    /// Guest Star cards go to the discard pile.</summary>
    public async Task<StageSeat?> Leave(int index, string reason)
    {
        var leaver = _stage.Unseat(index, reason);
        if (leaver == null) return null;
        await _board.ReturnCards(leaver);
        await _board.Sync();
        return leaver;
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

    /// <summary>Every guest acts once, oldest first, over a snapshot of the
    /// stage (end of turn, Tutti!, Bring the House Down, Showstopper).
    /// Returns the acts made.</summary>
    public async Task<int> ActAll()
    {
        var acts = 0;
        foreach (var seat in _stage.Seats.ToList())
        {
            if (_board.Over) break;
            if (!_stage.Holds(seat)) continue;
            if (await Act(seat)) acts++;
        }
        return acts;
    }

    /// <summary>Encore!: "Your oldest guest acts." Nothing on an empty stage.
    /// </summary>
    public async Task<bool> ActOldest()
    {
        var lead = _stage.Lead;
        return lead != null && await Act(lead);
    }

    /// <summary>Final Bow: "Choose a guest. It acts twice, then leaves."
    /// [3 times]. Its cards go to the discard pile.</summary>
    public async Task<bool> FinalBow(int index, int times)
    {
        if (index < 0 || index >= _stage.Seats.Count) return false;
        var seat = _stage.Seats[index];
        for (var i = 0; i < times; i++)
        {
            if (_board.Over || !_stage.Holds(seat)) break;
            await Act(seat);
        }
        var at = _stage.IndexOf(seat);
        if (at >= 0) await Leave(at, "final_bow");
        return true;
    }

    /// <summary>
    /// The end of her turn (the pool to 75, sec.3): each guest acts, oldest
    /// first; then each Showstopper copy Spends 5 and the guests act again;
    /// then Salon Solitaire Repays <paramref name="singer"/> (0 without the
    /// relic).
    /// </summary>
    public async Task EndOfTurn(int singer)
    {
        await ActAll();
        for (var i = 0; i < _stage.Mods.Showstopper; i++)
        {
            if (_board.Over || _stage.IsEmpty
                || !_stage.CanSpend(FurinaStageLaw.ShowstopperSpend))
            {
                break;
            }
            using (_stage.CausedBy(ShowstopperTitle))
            {
                if (await Spend(FurinaStageLaw.ShowstopperSpend) <= 0) break;
                await ActAll();
            }
        }
        if (singer > 0 && !_board.Over) await Repay(singer);
        // Neuvillette's window (2026-10-09): what she loses from here on --
        // the enemies' turn first -- counts for his next act.
        _stage.CloseTurn();
    }
}
