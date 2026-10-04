using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;

namespace KleeMod.Powers;

/// <summary>Where a performer's damage act lands.</summary>
public enum StageTarget
{
    /// <summary>Every enemy (Chevalmarin, Neuvillette).</summary>
    All,

    /// <summary>A random enemy (Crabaletta, Clorinde, Navia, Wriothesley).
    /// Oratrice's Verdict picks it while it stands.</summary>
    Random,

    /// <summary>A random enemy with an aura, if any (Lynette).</summary>
    Aura,
}

/// <summary>
/// THE BOARD HALF of the stage: everything an act, a Bow or a line does to
/// the game, as commands. The rules (<see cref="StageDirector"/>) decide what
/// and in what order; this does it. The game's implementation is
/// <see cref="GameStageBoard"/>; the headless pins hand the director a board
/// that records the calls, so every rule edge is testable without a combat.
/// </summary>
public interface IStageBoard
{
    /// <summary>Furina is dead or the combat is over or ending: nothing more
    /// resolves.</summary>
    bool Over { get; }

    Task Block(StagePerformer who, int amount);

    Task Damage(StagePerformer who, StageTarget target, int amount,
                Element element);

    /// <summary>Lyney: a Trick into her hand.</summary>
    Task AddTrick();

    /// <summary>Chevreuse: Energy next turn.</summary>
    Task EnergyNextTurn(int amount);

    Task Draw(int amount);

    /// <summary>Clorinde's line: Electro damage to a random enemy.</summary>
    Task ClorindeLine(int amount);

    /// <summary>Critics' Darling: damage to a random enemy, no element.
    /// </summary>
    Task CriticsHit(int amount);

    /// <summary>Stagehand's Gloves: Block after a Bow.</summary>
    Task GlovesBlock(int amount);

    /// <summary>The performer's body moves (a lunge), before its act.
    /// </summary>
    Task Lunge(StageSeat? seat);

    /// <summary>The bodies catch up with the seats.</summary>
    Task Sync();
}

/// <summary>What a summon did (rule 4).</summary>
public enum StageSummonResult
{
    Seated,
    Repeat,
    Evict,
    WalkOn,
}

/// <summary>
/// THE STAGE'S RULES, IN ORDER (v2, the re-founding): acts front to back,
/// the free Bow and its Fanfare, overflow and the walk-on, a guest's repeat,
/// the Cue, the Spend and Clorinde's line, Critics' Darling. Every method is
/// the sim's twin of the same name in <c>tier0/engine/furina_v2.py</c> (the
/// reference) and <c>tier0/engine/furina_stage.py</c>.
///
/// IT OWNS NO STATE: the seats and the numbers are the ledger's, the board
/// half is the board's. So the game and the headless pins run the very same
/// rules.
/// </summary>
public sealed class StageDirector
{
    private readonly FurinaStageLedger _stage;
    private readonly IStageBoard _board;

    public StageDirector(FurinaStageLedger stage, IStageBoard board)
    {
        _stage = stage;
        _board = board;
    }

    public FurinaStageLedger Stage => _stage;

    // ---- Fanfare ------------------------------------------------------------

    /// <summary>Gain Fanfare, then settle Critics' Darling.</summary>
    public async Task<int> Gain(int amount, string source = "")
    {
        var gained = _stage.Gain(amount, source);
        await Settle();
        return gained;
    }

    /// <summary>A card's Spend N (the mode the chooser offered). Clorinde's
    /// line answers a Spend that moved Fanfare. Returns what was paid.
    /// </summary>
    public async Task<int> Spend(int price)
    {
        if (!_stage.Spend(price)) return 0;
        await ClorindeLine();
        await Settle();
        return price;
    }

    /// <summary>"Spend all your Fanfare." Returns what was spent (0 held is
    /// no Spend).</summary>
    public async Task<int> SpendAll()
    {
        var spent = _stage.SpendAll();
        if (spent > 0) await ClorindeLine();
        await Settle();
        return spent;
    }

    private async Task ClorindeLine()
    {
        if (!_stage.OnStage(StagePerformer.Clorinde) || _board.Over) return;
        await _board.ClorindeLine(FurinaStageLaw.ClorindeSpendDamage);
    }

    /// <summary>Critics' Darling: every change to her Fanfare since the last
    /// settle deals its size to a random enemy, once per copy.</summary>
    public async Task Settle()
    {
        var changes = _stage.TakeChanges();
        var copies = _stage.Mods.CriticsDarling;
        if (copies <= 0) return;
        foreach (var change in changes)
        {
            for (var i = 0; i < copies; i++)
            {
                if (_board.Over) return;
                await _board.CriticsHit(change);
            }
        }
    }

    // ---- the act ----------------------------------------------------------

    /// <summary>
    /// One performer's act. A star pays unless <paramref name="free"/> (its
    /// Bow); a star that cannot pay SKIPS and nothing is spent. Chevreuse
    /// acts once a turn, every act counted (sec.8). <paramref name="onStage"/>
    /// is whether the performer stands on the stage as it acts (Neuvillette's
    /// line reaches only his acts on stage: not his eviction Bow). Returns
    /// whether it acted.
    /// </summary>
    public async Task<bool> Act(StagePerformer who, StageSeat? seat,
                                bool free = false, bool onStage = true)
    {
        if (_board.Over) return false;
        if (who == StagePerformer.Chevreuse && _stage.ChevreuseActedThisTurn)
        {
            _stage.Note(new StageBeat(FurinaStageLedger.SkipEvent, who,
                                      SeatIndex(seat), _stage.Fanfare, 0,
                                      "once"));
            return false;
        }
        var price = FurinaStageLaw.PriceOf(who);
        if (!free && price > 0 && !_stage.TryPay(who, price))
        {
            _stage.Note(new StageBeat(FurinaStageLedger.SkipEvent, who,
                                      SeatIndex(seat), _stage.Fanfare, 0,
                                      "short"));
            return false;
        }
        if (who == StagePerformer.Chevreuse) _stage.ChevreuseActedThisTurn = true;
        await _board.Lunge(seat);
        var r = _stage.Rehearsal;
        var mult = System.Math.Max(1, _stage.ActDamageMultiplier);
        int Dmg(int printed) => (printed + r) * mult;
        var moved = 0;
        switch (who)
        {
            case StagePerformer.Usher:
                moved = FurinaStageLaw.ActUsherBlock + r;
                await _board.Block(who, moved);
                break;
            case StagePerformer.Chevalmarin:
                moved = Dmg(FurinaStageLaw.ActChevalmarinDamage);
                await _board.Damage(who, StageTarget.All, moved, Element.None);
                break;
            case StagePerformer.Crabaletta:
                moved = Dmg(FurinaStageLaw.ActCrabalettaDamage);
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.None);
                break;
            case StagePerformer.Neuvillette:
                moved = Dmg(FurinaStageLaw.ActNeuvilletteDamage)
                        + (onStage ? FurinaStageLaw.NeuvilletteHydroBonus : 0);
                await _board.Damage(who, StageTarget.All, moved, Element.Hydro);
                break;
            case StagePerformer.Clorinde:
                moved = Dmg(FurinaStageLaw.ActClorindeDamage);
                await _board.Damage(who, StageTarget.Random, moved,
                                    Element.Electro);
                break;
            case StagePerformer.Lyney:
                await _board.AddTrick();
                break;
            case StagePerformer.Escoffier:
                // "Your Salon members act": front to back, each its own act.
                foreach (var salon in _stage.Seats
                             .Where(s => !FurinaStage.IsGuest(s.Who)).ToList())
                {
                    if (_board.Over) break;
                    if (!_stage.Holds(salon)) continue;
                    await Act(salon.Who, salon);
                }
                break;
            case StagePerformer.Navia:
            {
                var printed = FurinaStageLaw.NaviaPerSpent * _stage.SpentThisTurn;
                if (printed > 0)
                {
                    moved = Dmg(printed);
                    await _board.Damage(who, StageTarget.Random, moved,
                                        Element.Geo);
                }
                break;
            }
            case StagePerformer.Charlotte:
                moved = _stage.Gain(FurinaStageLaw.ActCharlotteGain, "Charlotte");
                break;
            case StagePerformer.Lynette:
                moved = Dmg(FurinaStageLaw.ActLynetteDamage);
                await _board.Damage(who, StageTarget.Aura, moved, Element.Anemo);
                break;
            case StagePerformer.Chevreuse:
                moved = FurinaStageLaw.ActChevreuseEnergy;
                await _board.EnergyNextTurn(moved);
                break;
            case StagePerformer.Sigewinne:
                moved = FurinaStageLaw.SigewinneBlock(_stage.HpLossesSince(who)) + r;
                await _board.Block(who, moved);
                break;
            case StagePerformer.Wriothesley:
                moved = Dmg(FurinaStageLaw.WriothesleyDamage(
                    _stage.BlockedSince(who)));
                await _board.Damage(who, StageTarget.Random, moved, Element.Cryo);
                break;
        }
        // Every act resets the readings (Sigewinne's, Wriothesley's).
        _stage.MarkSeated(who);
        _stage.Note(new StageBeat(FurinaStageLedger.ActEvent, who,
                                  SeatIndex(seat), _stage.Fanfare, moved, "",
                                  SeatKey: seat?.Key ?? -1));
        await Settle();
        return true;
    }

    private int SeatIndex(StageSeat? seat) =>
        seat == null ? -1 : _stage.IndexOf(seat);

    // ---- the Bow (rule 3) ---------------------------------------------------

    /// <summary>
    /// A Bow: the performer's act once more, FREE, then 1 Fanfare after it.
    /// Curtain Call Bouquet makes the act resolve twice; Stagehand's Gloves
    /// gives Block and Thunderous Applause draws after it. A performer that
    /// Bows AND LEAVES (<paramref name="leaves"/>) may come back through A
    /// Five-Century Act (<paramref name="mayReturn"/>: not an eviction or a
    /// walk-on, whose summon takes the seat).
    /// </summary>
    public async Task Bow(StagePerformer who, StageSeat? seat, bool leaves,
                          bool mayReturn = false)
    {
        if (_board.Over) return;
        _stage.BowsThisCombat++;
        _stage.Note(new StageBeat(FurinaStageLedger.BowEvent, who,
                                  SeatIndex(seat), _stage.Fanfare, 0,
                                  leaves ? "leaves" : "stays",
                                  SeatKey: seat?.Key ?? -1));
        var mods = _stage.Mods;
        for (var i = 0; i < System.Math.Max(1, mods.BowActs); i++)
        {
            if (_board.Over) return;
            await Act(who, leaves ? null : seat, free: true, onStage: !leaves);
        }
        if (_board.Over) return;
        _stage.Gain(FurinaStageLaw.BowFanfare, "Bow");
        if (mods.BowBlock > 0) await _board.GlovesBlock(mods.BowBlock);
        if (mods.BowDraw > 0 && !_board.Over) await _board.Draw(mods.BowDraw);
        if (leaves && mayReturn && mods.FiveCentury && !_stage.ReturnedThisTurn
            && !_stage.IsFull)
        {
            _stage.ReturnedThisTurn = true;
            _stage.Seat(who);
            await _board.Sync();
        }
        await Settle();
    }

    // ---- summons (rules 2 and 4) --------------------------------------------

    /// <summary>
    /// A Salon summon. A free seat takes it at the back; a full stage Bows
    /// its front-most SALON member to make room; a stage of guests only is a
    /// WALK-ON: the member's free Bow act and 1 Fanfare, no seat.
    /// </summary>
    public async Task<StageSummonResult> SummonSalon(StagePerformer who)
    {
        if (!_stage.IsFull)
        {
            _stage.Seat(who);
            await _board.Sync();
            return StageSummonResult.Seated;
        }
        var salon = _stage.FrontMostSalon();
        if (salon >= 0)
        {
            await Evict(salon);
            _stage.Seat(who);
            await _board.Sync();
            return StageSummonResult.Evict;
        }
        _stage.Note(new StageBeat(FurinaStageLedger.WalkOnEvent, who, -1,
                                  _stage.Fanfare, 0, ""));
        await Bow(who, null, leaves: true);
        return StageSummonResult.WalkOn;
    }

    /// <summary>
    /// A Guest Star. One of each: a guest already on stage Bows (its free
    /// act and 1 Fanfare) and keeps its seat. Otherwise a free seat, else
    /// the front-most Salon member Bows, else (every seat a guest) the front
    /// guest Bows. Then the card's own Fanfare (<paramref name="fanfare"/>),
    /// Guest Book, Star Billing and Star Turn, in that order.
    /// </summary>
    public async Task<StageSummonResult> SummonGuest(StagePerformer who,
                                                     int fanfare,
                                                     int guestBook = 0)
    {
        StageSummonResult result;
        if (_stage.SeatOf(who) is { } here)
        {
            await Bow(who, here, leaves: false);
            result = StageSummonResult.Repeat;
        }
        else if (!_stage.IsFull)
        {
            _stage.Seat(who);
            await _board.Sync();
            result = StageSummonResult.Seated;
        }
        else
        {
            var salon = _stage.FrontMostSalon();
            await Evict(salon >= 0 ? salon : 0);
            _stage.Seat(who);
            await _board.Sync();
            result = StageSummonResult.Evict;
        }
        if (_board.Over) return result;
        _stage.Gain(fanfare, "Guest Star");
        if (guestBook > 0 && !_stage.GuestBookSpent)
        {
            _stage.GuestBookSpent = true;
            _stage.Gain(guestBook, "Guest Book");
        }
        await Settle();
        var mods = _stage.Mods;
        if (mods.StarBilling > 0 && !_board.Over)
        {
            await _board.Draw(mods.StarBilling);
        }
        for (var i = 0; i < mods.StarTurn; i++)
        {
            if (_board.Over || _stage.SeatOf(who) is not { } seat) break;
            await Act(who, seat);
        }
        return result;
    }

    /// <summary>The performer in <paramref name="index"/> Bows and leaves to
    /// make room: off the stage first, then its free Bow act.</summary>
    private async Task Evict(int index)
    {
        var leaver = _stage.Unseat(index, "evicted");
        if (leaver == null) return;
        await _board.Sync();
        await Bow(leaver.Who, null, leaves: true, mayReturn: false);
    }

    // ---- the cards' verbs -------------------------------------------------

    /// <summary>
    /// Rule 7, Cue: the performer in <paramref name="index"/> acts now, as it
    /// would at the end of the turn (a star pays). Lynette's line moves the
    /// first performer Cued each turn to the front before it acts. Bis!'s
    /// <paramref name="times"/> 2 is the one chosen performer twice.
    /// </summary>
    public async Task Cue(int? index, int times = 1)
    {
        if (index is not { } at || at < 0 || at >= _stage.Seats.Count) return;
        var seat = _stage.Seats[at];
        var first = !_stage.CuedThisTurn;
        _stage.CuedThisTurn = true;
        _stage.Note(new StageBeat(FurinaStageLedger.CueEvent, seat.Who, at,
                                  _stage.Fanfare, 0, "", SeatKey: seat.Key));
        if (first && _stage.OnStage(StagePerformer.Lynette)
            && _stage.MoveToFront(at))
        {
            await _board.Sync();
        }
        for (var i = 0; i < System.Math.Max(1, times); i++)
        {
            if (_board.Over || !_stage.Holds(seat)) break;
            await Act(seat.Who, seat);
        }
    }

    /// <summary>Step Forward: the performer in <paramref name="index"/>
    /// moves to the front.</summary>
    public async Task StepForward(int? index)
    {
        if (index is not { } at) return;
        if (_stage.MoveToFront(at)) await _board.Sync();
    }

    /// <summary>Final Bow, Intermission: the performer in
    /// <paramref name="index"/> Bows and leaves (A Five-Century Act may bring
    /// it back).</summary>
    public async Task FinalBow(int? index)
    {
        if (index is not { } at) return;
        var seat = _stage.Unseat(at, "final_bow");
        if (seat == null) return;
        await _board.Sync();
        await Bow(seat.Who, null, leaves: true, mayReturn: true);
    }

    /// <summary>Tutti!, Encore Elixir, Endless Waltz: every performer (or
    /// every guest) acts now, front to back; a star pays.</summary>
    public async Task PerformAll(bool guestsOnly = false, int times = 1)
    {
        foreach (var seat in _stage.Seats.ToList())
        {
            if (guestsOnly && !FurinaStage.IsGuest(seat.Who)) continue;
            for (var i = 0; i < System.Math.Max(1, times); i++)
            {
                if (_board.Over) return;
                if (!_stage.Holds(seat)) break;
                await Act(seat.Who, seat);
            }
        }
    }

    /// <summary>Grand Finale, Let the People Rejoice: every performer Bows
    /// and keeps its seat, front to back.</summary>
    public async Task BowAll()
    {
        foreach (var seat in _stage.Seats.ToList())
        {
            if (_board.Over) return;
            if (!_stage.Holds(seat)) continue;
            await Bow(seat.Who, seat, leaves: false);
        }
    }

    /// <summary>Rule 1: the end of her turn. Every performer acts front to
    /// back, over a snapshot; Full House repeats each act on a full stage.
    /// </summary>
    public async Task EndOfTurn()
    {
        var times = 1 + (_stage.IsFull ? _stage.Mods.FullHouse : 0);
        foreach (var seat in _stage.Seats.ToList())
        {
            for (var i = 0; i < times; i++)
            {
                if (_board.Over) return;
                if (!_stage.Holds(seat)) break;
                await Act(seat.Who, seat);
            }
        }
    }
}
