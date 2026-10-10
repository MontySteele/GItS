using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>A seat and the guest standing in it: a name, a key and a body.
/// </summary>
public sealed class StageSeat
{
    internal StageSeat(StagePerformer who)
    {
        Who = who;
        Key = System.Threading.Interlocked.Increment(ref _nextKey);
    }

    private static int _nextKey;

    public StagePerformer Who { get; }

    /// <summary>Which seat. Unique per seat object, never reused.</summary>
    public int Key { get; }

    /// <summary>The body this seat is wearing, or null until
    /// <c>FurinaStagePets.Sync</c> has fielded one (always null headless).
    /// </summary>
    public Creature? Pet { get; internal set; }

    /// <summary>The pool to 75's guest rule (sec.3): an upgraded Guest Star
    /// raises its guest's line or act. True when any card that brought or
    /// moved this guest was upgraded.</summary>
    public bool Upgraded { get; internal set; }

    /// <summary>The Guest Star cards this guest holds (sec.3): each exhausted
    /// when played, and each goes to the discard pile when the guest leaves
    /// the stage. Empty headless unless a pin hands one in.</summary>
    public List<CardModel> Cards { get; } = new();
}

/// <summary>
/// ONE THING THE KIT DID, for the blind-play page (`EB-735`). The record's
/// shape is the wire's (<see cref="FurinaStageLedger.Snapshot"/>). Events:
/// <c>arrive</c>, <c>act</c>, <c>leave</c>, <c>gain</c>, <c>spend</c>,
/// <c>drain</c> and <c>repay</c>. <see cref="Fanfare"/> is her Fanfare after
/// the beat; <see cref="Moved"/> what the beat moved, measured on the board.
/// </summary>
public readonly record struct StageBeat(
    string Event, StagePerformer Who, int Seat, int Fanfare, int Moved,
    string Reason, string Target = "", string TargetId = "", int Each = -1,
    int Hp = -1, int Struck = -1, string By = "", int SeatKey = -1,
    int Dealt = -1, int TargetHp = -1, int Blocked = -1, int Caught = 0,
    int Standing = -1, string Source = "");

/// <summary>ONE SPEND, for the play telemetry (the Spend round,
/// 2026-10-10): what it was for (the card, or the Power or relic resolving;
/// "" for a guest's act), what left the bank, the bank before it, and for a
/// "Spend up to X" its cap (-1 otherwise; <see
/// cref="FurinaStageLedger.MarkUpTo"/>).</summary>
public readonly record struct StageSpendRecord(string Source, int Spent,
                                               int Before, int Cap);

/// <summary>The curtain call's parts
/// (<see cref="FurinaStageLedger.CurtainCallOf"/>): the HP returned, the part
/// of it drained past the line, and the past-line HP lost.</summary>
public readonly record struct CurtainCallParts(int Back, int PastBack,
                                               int Lost);

/// <summary>
/// What the kit reads off Furina's powers, in one record, so a headless pin
/// can set them (<see cref="FurinaStageLedger.ModsOverride"/>) and the game
/// reads them live (<see cref="FurinaStage.ModsOf"/>).
/// </summary>
public sealed record StageMods
{
    /// <summary>Seats: three.</summary>
    public int Capacity { get; init; } = FurinaStageLaw.Seats;

    /// <summary>Universal Revelry copies: each Drain or Repay of N gains N
    /// more Fanfare per copy (the pool-40 paper, sec.2).</summary>
    public int Revelry { get; init; }

    /// <summary>Ousia Surge: cards drawn on the first Drain each turn.
    /// </summary>
    public int OusiaSurge { get; init; }

    /// <summary>A Five-Century Act copies: any makes the HP drained past the
    /// line return at the curtain call too (2026-10-09).</summary>
    public int FiveCenturyAct { get; init; }

    /// <summary>Critics' Darling copies: each Drain or Repay of N deals N per
    /// copy to a random enemy.</summary>
    public int CriticsDarling { get; init; }

    /// <summary>Bis! copies: any keeps half of a spend-all.</summary>
    public int Bis { get; init; }

    /// <summary>Salon's Encore: damage to ALL enemies per Drain.</summary>
    public int SalonsEncore { get; init; }

    /// <summary>Thunderous Applause: damage to ALL enemies per Spend.</summary>
    public int Thunderous { get; init; }

    // ---- the pool to 75 (review/active/furina-pool-growth-2026-10-09.md) --

    /// <summary>Grand Entrance: Repay per Guest Star played (copies add).
    /// </summary>
    public int GrandEntrance { get; init; }

    /// <summary>Showstopper copies: each buys one more round of acts at the
    /// end of her turn for Spend 5.</summary>
    public int Showstopper { get; init; }

    /// <summary>Crescendo: cards drawn on the first Spend each turn.</summary>
    public int Crescendo { get; init; }

    /// <summary>Standing Room Only: Strength per spend-all of at least 1.
    /// </summary>
    public int StandingRoomOnly { get; init; }

    /// <summary>Hymn of Renewal: Strength per Repay of 4 or more HP.</summary>
    public int HymnOfRenewal { get; init; }

    /// <summary>The Masquerade copies (the block gap, 2026-10-09): each Drain
    /// gains the HP it actually drained as Block, per copy.</summary>
    public int Masquerade { get; init; }

    public static readonly StageMods None = new();
}

/// <summary>
/// THE KIT'S STATE (the Salon's Tab, 2026-10-05): the guest seats front
/// (oldest) first, her one Fanfare number, the HP loan's line and drained
/// ledger, the turn's flow counts and every once-a-turn latch -- every rule
/// that is arithmetic rather than an engine command. The order of acts,
/// Drains and Repays is <see cref="StageDirector"/>'s; this class is
/// synchronous so the headless pins can ask it anything.
///
/// PER FURINA AND PER COMBAT, keyed by combat identity: in co-op the other
/// seat's ledger is not hers, and the loan lives one combat.
/// </summary>
public sealed class FurinaStageLedger
{
    private static object? _combat;

    private static readonly Dictionary<Creature, FurinaStageLedger> _byFurina =
        new();

    private readonly List<StageSeat> _seats = new();

    /// <summary>This Furina's ledger for this combat, created on first ask.
    /// Creation CAPTURES HER ENTRY HP (Kokomi's ledger's rule): the first ask
    /// comes at the combat's start at the latest (the turn-open hook), before
    /// any HP can move.</summary>
    public static FurinaStageLedger For(Creature furina)
    {
        var combat = (object?)furina.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byFurina.Clear();
        }
        if (!_byFurina.TryGetValue(furina, out var ledger))
        {
            ledger = new FurinaStageLedger
            {
                _furina = furina,
                EntryHp = (int)furina.CurrentHp,
                EntryMaxHp = (int)furina.MaxHp,
            };
            _byFurina[furina] = ledger;
        }
        return ledger;
    }

    /// <summary>This Furina's ledger for her current combat if one exists,
    /// else null. Creates nothing and captures nothing, so a READER (the play
    /// telemetry) can ask without moving the entry HP the line is read from.
    /// </summary>
    public static FurinaStageLedger? Peek(Creature furina)
    {
        var combat = (object?)furina.CombatState;
        if (combat == null || !ReferenceEquals(_combat, combat)) return null;
        return _byFurina.TryGetValue(furina, out var ledger) ? ledger : null;
    }

    /// <summary>Every Furina with a ledger in the current combat (the curtain
    /// call's walk at the combat's end).</summary>
    public static IReadOnlyCollection<Creature> Furinas => _byFurina.Keys;

    /// <summary>Test seam: forget every ledger.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byFurina.Clear();
    }

    /// <summary>A free-standing ledger with no Furina, for the headless pins.
    /// </summary>
    public static FurinaStageLedger Detached() => new();

    private Creature? _furina;

    /// <summary>The Furina this ledger is hers; null on a detached one.
    /// </summary>
    public Creature? Furina => _furina;

    // ---- the mods ------------------------------------------------------

    /// <summary>Test seam: the mods a headless pin sets. Null in the game.
    /// </summary>
    public StageMods? ModsOverride { get; set; }

    public StageMods Mods =>
        ModsOverride ?? (_furina != null ? FurinaStage.ModsOf(_furina)
                                         : StageMods.None);

    public int Capacity => Mods.Capacity;

    // ---- the seats -----------------------------------------------------

    /// <summary>The stage, FRONT (oldest) FIRST.</summary>
    public IReadOnlyList<StageSeat> Seats => _seats;

    public StageSeat? Lead => _seats.Count > 0 ? _seats[0] : null;

    public bool IsEmpty => _seats.Count == 0;

    public bool IsFull => _seats.Count >= Capacity;

    public IEnumerable<StagePerformer> Company => _seats.Select(s => s.Who);

    public int IndexOf(StageSeat seat)
    {
        for (var i = 0; i < _seats.Count; i++)
        {
            if (ReferenceEquals(_seats[i], seat)) return i;
        }
        return -1;
    }

    public bool Holds(StageSeat seat) => IndexOf(seat) >= 0;

    public bool OnStage(StagePerformer who) => _seats.Any(s => s.Who == who);

    public StageSeat? SeatOf(StagePerformer who) =>
        _seats.FirstOrDefault(s => s.Who == who);

    public int SeatIndexOf(StagePerformer who)
    {
        for (var i = 0; i < _seats.Count; i++)
        {
            if (_seats[i].Who == who) return i;
        }
        return -1;
    }

    /// <summary>A newcomer takes the back seat. Null on a full stage (the
    /// caller makes room first).</summary>
    public StageSeat? Seat(StagePerformer who, bool upgraded = false)
    {
        if (IsFull) return null;
        var seat = new StageSeat(who) { Upgraded = upgraded };
        _seats.Add(seat);
        Note(new StageBeat(ArriveEvent, who, _seats.Count - 1, Fanfare, 0, "",
                           SeatKey: seat.Key));
        return seat;
    }

    /// <summary>Take the guest in <paramref name="index"/> off the stage.
    /// </summary>
    public StageSeat? Unseat(int index, string reason)
    {
        if (index < 0 || index >= _seats.Count) return null;
        var seat = _seats[index];
        _seats.RemoveAt(index);
        Note(new StageBeat(LeaveEvent, seat.Who, -1, Fanfare, 0, reason,
                           SeatKey: seat.Key));
        return seat;
    }

    /// <summary>The pool to 75's duplicate copy (sec.3): the guest in
    /// <paramref name="index"/> moves to the newest seat (the back), with no
    /// act. Its seat object, key and body stay its own.</summary>
    public StageSeat? MoveToBack(int index)
    {
        if (index < 0 || index >= _seats.Count) return null;
        var seat = _seats[index];
        _seats.RemoveAt(index);
        _seats.Add(seat);
        Note(new StageBeat(MoveEvent, seat.Who, _seats.Count - 1, Fanfare, 0,
                           "moved", SeatKey: seat.Key));
        return seat;
    }

    /// <summary>Clear the stage and every count (a pin's fresh board).
    /// </summary>
    public void Clear()
    {
        _seats.Clear();
        _beats.Clear();
        Fanfare = 0;
        GainedThisTurn = 0;
        SpentThisTurn = 0;
        SpentThisPlay = 0;
        DrainedAbove = 0;
        DrainedPast = 0;
        DrainedThisTurn = 0;
        HpLostSinceLastTurn = 0;
        RepayLeftThisPlay = 0;
        RepayedThisPlay = false;
        RepaidThisTurn = 0;
        DrainsThisCombat = 0;
        DrainedThisCombat = 0;
        RepaysThisTurn = 0;
        RepaidThisPlay = 0;
        SpendsThisTurn = 0;
        CharlotteDrewThisTurn = false;
        LynetteFiredThisTurn = false;
        OusiaDrewThisTurn = false;
        Draining = false;
        Opened = false;
        _fountains.Clear();
        FountainSeen = 0;
        _spends.Clear();
        PeakFanfare = 0;
        PlayingCard = "";
        CardPlaying = false;
        Acting = 0;
        _upToCap = -1;
        PastLost = 0;
        HighStakesDealt = 0;
    }

    /// <summary>The combat's opening has been recorded.</summary>
    public bool Opened { get; set; }

    /// <summary>Record the opening once: the entry HP and Max HP the line
    /// is read from (both snapshotted, so the line does not move when her
    /// Max HP changes mid-fight). True the first time.</summary>
    public bool Open(int entryHp, int entryMaxHp)
    {
        if (Opened) return false;
        Opened = true;
        EntryHp = entryHp;
        EntryMaxHp = entryMaxHp;
        return true;
    }

    // ---- the HP loan (rules 1, 2 and the curtain call) ------------------

    /// <summary>The HP she started this combat with.</summary>
    public int EntryHp { get; set; }

    /// <summary>The Max HP she started this combat with (the line's
    /// quarter, 2026-10-09).</summary>
    public int EntryMaxHp { get; set; }

    /// <summary>Rule 1: the Drain line, her entry HP minus 1/4 of her entry
    /// Max HP (2026-10-09). Lyney on stage lowers it by 10. A Drain may go
    /// past it; what it drains past it is <see cref="DrainedPast"/>.</summary>
    public int Line => FurinaStageLaw.LineOf(
        EntryHp, EntryMaxHp, OnStage(StagePerformer.Lyney));

    /// <summary>Where <see cref="Line"/> comes from, in words (2026-10-05).
    /// </summary>
    public string LineWhy => FurinaStageLaw.LineWhy(
        OnStage(StagePerformer.Lyney));

    /// <summary>Can she Drain <paramref name="amount"/> at
    /// <paramref name="hp"/>? Never refused for the line (2026-10-09); only
    /// a Drain that would take her to 0 HP or below is.</summary>
    public bool CanDrain(int amount, int hp) =>
        amount > 0 && hp - amount >= FurinaStageLaw.DrainFloor;

    /// <summary>A guest act's Drain (the drain-line round, 2026-10-09): how
    /// much of <paramref name="amount"/> fits at <paramref name="hp"/>
    /// without going past the line. 0 when she is at or below it.</summary>
    public int GuestDrainRoom(int amount, int hp) =>
        System.Math.Max(0, System.Math.Min(amount, hp - Line));

    /// <summary>Would a Drain of <paramref name="amount"/> at
    /// <paramref name="hp"/> go past the line? (The face's warning.)
    /// </summary>
    public bool PastLine(int amount, int hp) =>
        amount > 0 && hp - amount < Line;

    /// <summary>HP lost to her Drains and not yet repaid: both parts.
    /// </summary>
    public int Drained => DrainedAbove + DrainedPast;

    /// <summary>Drained HP taken while she stood above the line: it returns
    /// at the curtain call.</summary>
    public int DrainedAbove { get; private set; }

    /// <summary>Drained HP taken past the line: it stays lost at the curtain
    /// call (unless A Five-Century Act is in play). A Repay returns this
    /// part first.</summary>
    public int DrainedPast { get; private set; }

    /// <summary>HP drained this turn (the page and the pins read it).
    /// </summary>
    public int DrainedThisTurn { get; private set; }

    /// <summary>Neuvillette's act (2026-10-09): every HP she lost since her
    /// last turn ended -- to her Drains and to anything else (an enemy's
    /// hit, a status). The window opens at the end of her turn, after the
    /// guests act, so the enemies' turn counts; on her first turn it counts
    /// from the combat's start.</summary>
    public int HpLostSinceLastTurn { get; private set; }

    /// <summary>HP repaid this turn.</summary>
    public int RepaidThisTurn { get; private set; }

    /// <summary>A Drain's own HP loss is resolving: the HP-loss hook must not
    /// count it, because the Drain counts it itself.</summary>
    public bool Draining { get; set; }

    /// <summary>Drains made this combat, every one (Undercurrent's count).
    /// </summary>
    public int DrainsThisCombat { get; private set; }

    /// <summary>HP drained this combat, GROSS: every Drain's HP, above and
    /// past the line, and no Repay lowers it (High Stakes' count, the Spend
    /// round 2, 2026-10-10: the net count sat near 0 because Salon Solitaire
    /// Repays every turn). Mirrors <c>Ftd.drained_this_combat</c>.</summary>
    public int DrainedThisCombat { get; private set; }

    /// <summary>Repays that returned HP this turn (Rising Tide's count).
    /// </summary>
    public int RepaysThisTurn { get; private set; }

    /// <summary>HP THIS card play's Repays returned (Grand Absolution's
    /// "that much").</summary>
    public int RepaidThisPlay { get; private set; }

    /// <summary>THE REPAY FLOOR (2026-10-09): what THIS card play's Repays
    /// could not return, N minus the HP returned (Surging Waters', Hydro
    /// Lance's and Cleansing Torrent's damage reads it).</summary>
    public int RepayLeftThisPlay { get; private set; }

    /// <summary>A Repay has resolved in this card play (so
    /// <see cref="RepayLeftThisPlay"/> is a fact, not a forecast).</summary>
    public bool RepayedThisPlay { get; private set; }

    /// <summary>A Drain of <paramref name="amount"/> taken from
    /// <paramref name="hpBefore"/>: the part that stayed at or above the line
    /// is <see cref="DrainedAbove"/>, the rest <see cref="DrainedPast"/>.
    /// </summary>
    public void NoteDrain(int amount, int hpBefore)
    {
        if (amount <= 0) return;
        var above = System.Math.Max(0,
            System.Math.Min(amount, hpBefore - Line));
        DrainedAbove += above;
        DrainedPast += amount - above;
        DrainedThisTurn += amount;
        DrainedThisCombat += amount;
        HpLostSinceLastTurn += amount;
        DrainsThisCombat++;
    }

    /// <summary>HP lost to anything but a Drain (Neuvillette's act counts it).
    /// </summary>
    public void NoteHpLost(int amount)
    {
        if (amount <= 0) return;
        HpLostSinceLastTurn += amount;
    }

    /// <summary>The end of her turn, after the guests act: the
    /// since-her-last-turn window opens again.</summary>
    public void CloseTurn() => HpLostSinceLastTurn = 0;

    /// <summary>Rule 2: how much a Repay of <paramref name="amount"/> returns
    /// at this HP: never more than she drained, never past Max HP. Clamps the
    /// ledger first (HP + drained never exceeds Max HP); the clamp takes the
    /// past-line part first, the order a Repay returns it in.</summary>
    public int RepayRoom(int amount, int hp, int maxHp)
    {
        var over = Drained - System.Math.Max(0, maxHp - hp);
        if (over > 0)
        {
            var past = System.Math.Min(over, DrainedPast);
            DrainedPast -= past;
            DrainedAbove = System.Math.Max(0, DrainedAbove - (over - past));
        }
        return System.Math.Max(0, System.Math.Min(amount, Drained));
    }

    /// <summary>A Repay returned <paramref name="amount"/>: the past-line
    /// part first, then the above-line part (2026-10-09).</summary>
    public void NoteRepay(int amount)
    {
        if (amount <= 0) return;
        var past = System.Math.Min(amount, DrainedPast);
        DrainedPast -= past;
        DrainedAbove = System.Math.Max(0, DrainedAbove - (amount - past));
        RepaidThisTurn += amount;
        RepaysThisTurn++;
        RepaidThisPlay += amount;
    }

    /// <summary>The Repay floor: a card play's Repay of
    /// <paramref name="amount"/> returned <paramref name="back"/>; what it
    /// could not return is recorded for the card's damage.</summary>
    public void NoteRepayLeft(int amount, int back)
    {
        RepayedThisPlay = true;
        RepayLeftThisPlay += System.Math.Max(0, amount - back);
    }

    /// <summary>THE CURTAIN CALL (sec.16; the Drain line rule, 2026-10-09):
    /// the HP that returns when the combat ends -- the above-line part, up
    /// to Max HP; the past-line part too with A Five-Century Act in play.
    /// Empties the ledger: the past-line part is lost.</summary>
    public int CurtainCall(int hp, int maxHp) => CurtainCallOf(hp, maxHp).Back;

    /// <summary>The curtain call in its three parts (the Spend round,
    /// 2026-10-10: the page said only what returned). <c>Back</c> is the HP
    /// returned; <c>PastBack</c> the part of it drained past the line (A
    /// Five-Century Act; the above-line part returns first); <c>Lost</c> the
    /// past-line HP not Repaid that does not return (none with A Five-Century
    /// Act). Empties the ledger.</summary>
    public CurtainCallParts CurtainCallOf(int hp, int maxHp)
    {
        var five = Mods.FiveCenturyAct > 0;
        var owed = DrainedAbove + (five ? DrainedPast : 0);
        var back = System.Math.Max(0, System.Math.Min(owed, maxHp - hp));
        var parts = new CurtainCallParts(
            back,
            five ? System.Math.Max(0,
                       System.Math.Min(DrainedPast, back - DrainedAbove))
                 : 0,
            five ? 0 : DrainedPast);
        PastLost += parts.Lost;
        DrainedAbove = 0;
        DrainedPast = 0;
        return parts;
    }

    /// <summary>The play telemetry's <c>past_lost</c> (the Spend round 2,
    /// 2026-10-10): HP drained past the line that the curtain call did not
    /// return. Before the curtain call (a death) it is the past-line HP
    /// still owed, which nothing will return.</summary>
    public int PastLostAtClose => PastLost + DrainedPast;

    /// <summary>What the curtain call left lost (its <c>Lost</c> part).
    /// </summary>
    public int PastLost { get; private set; }

    /// <summary>The play telemetry's <c>high_stakes_bonus</c> (the Spend
    /// round 2, 2026-10-10): the damage High Stakes added to her Attack hits
    /// this combat, each hit's bonus capped at what the hit dealt.</summary>
    public int HighStakesDealt { get; private set; }

    /// <summary>A High Stakes bonus of <paramref name="amount"/> landed.
    /// </summary>
    public void NoteHighStakes(int amount)
    {
        if (amount > 0) HighStakesDealt += amount;
    }

    // ---- Fanfare: one number on Furina (rule 3) ------------------------

    /// <summary>Her Fanfare. No cap, no fade.</summary>
    public int Fanfare { get; private set; }

    /// <summary>Fanfare gained this turn.</summary>
    public int GainedThisTurn { get; private set; }

    /// <summary>Fanfare her Spends took this turn.</summary>
    public int SpentThisTurn { get; private set; }

    /// <summary>What THIS card play's spend-all took (`stage_spent`).
    /// </summary>
    public int SpentThisPlay { get; private set; }

    /// <summary>Gain Fanfare. Universal Revelry no longer multiplies a gain
    /// (the pool-40 paper, sec.2): it adds its own gain to a Drain or a Repay
    /// (<see cref="StageDirector"/>'s loop readers). Returns what was
    /// gained.</summary>
    public int Gain(int amount, string source = "")
    {
        if (amount <= 0) return 0;
        var gained = amount;
        Fanfare += gained;
        GainedThisTurn += gained;
        Note(new StageBeat(GainEvent, default, -1, Fanfare, gained, source));
        return gained;
    }

    /// <summary>Spends made this turn (the "first Spend each turn" of
    /// Navia's line and Crescendo).</summary>
    public int SpendsThisTurn { get; private set; }

    /// <summary>Navia's line (the pool to 75): what the next Spend is
    /// discounted by -- 2 (3 upgraded) while she is on stage and no Spend has
    /// been made this turn, else 0.</summary>
    public int NaviaDiscount
    {
        get
        {
            if (SpendsThisTurn > 0) return 0;
            var seat = SeatOf(StagePerformer.Navia);
            if (seat == null) return 0;
            return seat.Upgraded ? FurinaStageLaw.NaviaLineDiscountUpgraded
                                 : FurinaStageLaw.NaviaLineDiscount;
        }
    }

    /// <summary>What a Spend of <paramref name="price"/> takes now: the
    /// price less Navia's discount, never below 0.</summary>
    public int PriceOf(int price) =>
        System.Math.Max(0, price - NaviaDiscount);

    /// <summary>Can a Spend of <paramref name="price"/> be paid?</summary>
    public bool CanSpend(int price) =>
        price >= 0 && Fanfare >= PriceOf(price);

    /// <summary>A Spend N. A Spend of 0 moves nothing and is no Spend. Navia
    /// on stage makes the first Spend each turn cost 2 less (her line; a
    /// Spend discounted to 0 is still that Spend). True when it was paid.
    /// </summary>
    public bool Spend(int price)
    {
        if (price <= 0) return false;
        var pay = PriceOf(price);
        if (Fanfare < pay) return false;
        var discount = price - pay;
        Fanfare -= pay;
        SpentThisTurn += pay;
        SpendsThisTurn++;
        Note(new StageBeat(SpendEvent, default, -1, Fanfare, pay, ""));
        if (discount > 0) NoteLine(StagePerformer.Navia, discount);
        return true;
    }

    /// <summary>What a "Spend up to <paramref name="cap"/>" would count now:
    /// the cap, or all she holds plus Navia's free points if that is less.
    /// A read (the face's preview and the director's Spend agree).</summary>
    public int UpToOf(int cap) =>
        cap <= 0 ? 0 : System.Math.Min(cap, Fanfare + NaviaDiscount);

    /// <summary>
    /// "Spend up to X" (the Spend paper, 2026-10-10, pick 1): spends X, or
    /// all she holds if that is less, and never fails. It is a Spend only
    /// when at least 1 was spent; it is not a spend-all, so Bis! and Standing
    /// Room Only ignore it. Navia's line makes the first 2 [3] points of the
    /// first Spend each turn free: they count as spent and are not taken.
    /// Returns what counts as spent (0: no Spend).
    /// <paramref name="forPlay"/> records it as this card play's
    /// `stage_spent`; a guest's act (Navia's half-Spend, Freminet's quarter)
    /// leaves the play's record alone.
    /// </summary>
    public int SpendUpTo(int cap, bool forPlay = true)
    {
        if (forPlay) SpentThisPlay = 0;
        var counted = UpToOf(cap);
        if (counted <= 0) return 0;
        var free = System.Math.Min(counted, NaviaDiscount);
        var pay = counted - free;
        Fanfare -= pay;
        SpentThisTurn += pay;
        SpendsThisTurn++;
        // The play telemetry's Spend record carries a card's "up to X" cap
        // (the Spend round, 2026-10-10). A guest's share-Spend has no
        // printed cap and records -1.
        if (forPlay) MarkUpTo(cap);
        Note(new StageBeat(SpendEvent, default, -1, Fanfare, pay, ""));
        if (free > 0) NoteLine(StagePerformer.Navia, free);
        if (forPlay) SpentThisPlay = counted;
        return counted;
    }

    /// <summary>Center of Attention's free "Spend up to X": the full X counts
    /// for the card and nothing is taken (the Spend paper's reading of "takes
    /// no Fanfare"). Like its free Spend N, it moves nothing, so it is no
    /// Spend.</summary>
    public int SpendUpToFree(int cap)
    {
        SpentThisPlay = System.Math.Max(0, cap);
        return SpentThisPlay;
    }

    /// <summary>A guest's LINE fired (the pool to 75, sec.3: a line gets a
    /// log line of its own, so it is not read as a second act).</summary>
    public void NoteLine(StagePerformer who, int moved)
    {
        var seat = SeatOf(who);
        Note(new StageBeat(LineEvent, who, seat == null ? -1 : IndexOf(seat),
                           Fanfare, moved, "line",
                           SeatKey: seat?.Key ?? -1));
    }

    /// <summary>"Spend all your Fanfare." Nothing held is no Spend. Bis!
    /// keeps half of it, rounded down: the spend and what it pays for are
    /// the whole bank, and half the bank is back after. Navia's first Spend
    /// each turn keeps 2 (3 upgraded): the card reads the whole bank, and
    /// that much stays.</summary>
    public int SpendAll()
    {
        var held = Fanfare;
        SpentThisPlay = 0;
        if (held <= 0) return 0;
        var keep = System.Math.Min(held, NaviaDiscount);
        var pay = held - keep;
        Fanfare -= pay;
        SpentThisTurn += pay;
        SpendsThisTurn++;
        Note(new StageBeat(SpendEvent, default, -1, Fanfare, pay, ""));
        if (keep > 0) NoteLine(StagePerformer.Navia, keep);
        SpentThisPlay = held;
        var kept = Mods.Bis > 0 ? held / 2 : 0;
        if (kept > 0)
        {
            Fanfare += kept;
            Note(new StageBeat(GainEvent, default, -1, Fanfare, kept, "Bis!"));
        }
        return held;
    }

    // ---- Fountain of Lucine: Repays owed at the start of later turns -----

    private readonly List<int[]> _fountains = new();

    /// <summary>How much of <c>FountainOfLucinePower</c>'s applied total
    /// the schedule has taken in (it schedules lazily at her turn start).
    /// </summary>
    public int FountainSeen { get; set; }

    /// <summary>Owe a Repay of <paramref name="amount"/> at the start of
    /// each of her next <paramref name="turns"/> turns.</summary>
    public void ScheduleRepay(int amount, int turns)
    {
        if (amount <= 0 || turns <= 0) return;
        _fountains.Add(new[] { amount, turns });
    }

    /// <summary>The Repays due at this turn start, one per scheduled play;
    /// each counts down a turn and leaves when spent.</summary>
    public List<int> TakeDueRepays()
    {
        var due = _fountains.Select(f => f[0]).ToList();
        foreach (var f in _fountains) f[1]--;
        _fountains.RemoveAll(f => f[1] <= 0);
        return due;
    }

    /// <summary>The Repay owed at her next turn start, all plays together.
    /// </summary>
    public int RepayDueNext => _fountains.Sum(f => f[0]);

    /// <summary>Is any Repay still owed?</summary>
    public bool OwesRepays => _fountains.Count > 0;

    /// <summary>A fresh per-play spend record (every card play).
    /// <paramref name="card"/> is the card's name as the play telemetry
    /// writes it, so a Spend during the play is filed under it.</summary>
    public void BeginPlay(string card = "")
    {
        PlayingCard = card ?? "";
        CardPlaying = true;
        SpentThisPlay = 0;
        RepaidThisPlay = 0;
        RepayLeftThisPlay = 0;
        RepayedThisPlay = false;
    }

    /// <summary>The play is over: the record closes with it. The Salon's Tab
    /// seat round (2026-10-05): it used to stand until the NEXT play opened,
    /// so a spend-all face in hand read the last play's spend at 0 Fanfare
    /// ("Deals 113").</summary>
    public void EndPlay()
    {
        PlayingCard = "";
        CardPlaying = false;
        SpentThisPlay = 0;
        RepaidThisPlay = 0;
        RepayLeftThisPlay = 0;
        RepayedThisPlay = false;
    }

    /// <summary>A card of hers is resolving (<see cref="BeginPlay"/> to
    /// <see cref="EndPlay"/>).</summary>
    public bool CardPlaying { get; private set; }

    /// <summary>Guest acts resolving now (an act can run inside a card play:
    /// Encore!, Final Bow).</summary>
    public int Acting { get; set; }

    /// <summary>
    /// CHARLOTTE'S LINE (the Spend round 2, 2026-10-10): "The first time one
    /// of your cards Repays each turn, draw 1 card." Is the Repay resolving
    /// now one of her cards'? A card play is open, and no Power, relic
    /// (<see cref="Cause"/>) or guest act (<see cref="Acting"/>) is the one
    /// Repaying inside it. Her own act and Salon Solitaire, at the end of
    /// her turn, drew a card she then discarded.
    /// </summary>
    public bool CardRepaying => CardPlaying && Cause.Length == 0 && Acting == 0;

    // ---- the once-a-turn latches ---------------------------------------

    /// <summary>Charlotte's line has drawn this turn.</summary>
    public bool CharlotteDrewThisTurn { get; set; }

    /// <summary>Lynette's line has paid this turn.</summary>
    public bool LynetteFiredThisTurn { get; set; }

    /// <summary>Ousia Surge has drawn this turn.</summary>
    public bool OusiaDrewThisTurn { get; set; }

    /// <summary>The top of her turn: the flow counts and latches reset. They
    /// held through the end-of-turn sequence and the enemies' turn.</summary>
    public void OpenTurn()
    {
        GainedThisTurn = 0;
        SpentThisTurn = 0;
        DrainedThisTurn = 0;
        RepaidThisTurn = 0;
        RepaysThisTurn = 0;
        SpendsThisTurn = 0;
        SpentThisPlay = 0;
        RepaidThisPlay = 0;
        RepayLeftThisPlay = 0;
        RepayedThisPlay = false;
        CharlotteDrewThisTurn = false;
        LynetteFiredThisTurn = false;
        OusiaDrewThisTurn = false;
    }

    // ---- the performance log (`EB-735`) --------------------------------

    private readonly List<StageBeat> _beats = new();

    /// <summary>What the kit did since she last ended a turn, in order.
    /// </summary>
    public IReadOnlyList<StageBeat> Beats => _beats;

    public void Note(StageBeat beat)
    {
        Observe(beat);
        if (beat.SeatKey < 0 && beat.Seat >= 0 && beat.Seat < _seats.Count
            && _seats[beat.Seat].Who == beat.Who)
        {
            beat = beat with { SeatKey = _seats[beat.Seat].Key };
        }
        if (beat.Standing < 0) beat = beat with { Standing = _seats.Count };
        if (beat.Source.Length == 0 && Cause.Length > 0)
        {
            beat = beat with { Source = Cause };
        }
        _beats.Add(beat);
    }

    /// <summary>The power or relic whose effect is resolving now, stamped on
    /// every beat filed meanwhile.</summary>
    public string Cause { get; private set; } = "";

    public System.IDisposable CausedBy(string title) =>
        new CauseScope(this, title);

    private sealed class CauseScope : System.IDisposable
    {
        private readonly FurinaStageLedger _ledger;
        private readonly string _was;

        internal CauseScope(FurinaStageLedger ledger, string title)
        {
            _ledger = ledger;
            _was = ledger.Cause;
            ledger.Cause = title ?? "";
        }

        public void Dispose() => _ledger.Cause = _was;
    }

    public void ClearBeats() => _beats.Clear();

    // ---- the fight's Fanfare record (the play telemetry) ----------------
    //
    // THE SPEND ROUND (2026-10-10, "Next round: telemetry first"): per fight,
    // her peak Fanfare and every Spend with the bank before it. Read off the
    // beats every Fanfare move already files (a gain, Bis!'s return and each
    // Spend all go through `Note`), so no Spend path needs a second call and
    // a new one is counted the day it files its beat. The ledger lives one
    // combat, so these are per fight. A read for `PlayTelemetry`; nothing
    // the kit's rules ask.

    private readonly List<StageSpendRecord> _spends = new();

    private int _upToCap = -1;

    /// <summary>The most Fanfare she held at once this combat.</summary>
    public int PeakFanfare { get; private set; }

    /// <summary>Every Spend this combat, in order.</summary>
    public IReadOnlyList<StageSpendRecord> Spends => _spends;

    /// <summary>The card being played, as the telemetry names it; "" between
    /// plays (<see cref="BeginPlay"/>).</summary>
    public string PlayingCard { get; private set; } = "";

    /// <summary>
    /// THE HOOK FOR "SPEND UP TO X" (the Spend paper's build, #1016): call
    /// it just before the up-to Spend files its beat, and the next Spend
    /// recorded carries <paramref name="cap"/> as its cap (-1, the default,
    /// for every other Spend).
    /// </summary>
    public void MarkUpTo(int cap) => _upToCap = cap;

    private void Observe(StageBeat beat)
    {
        if (beat.Fanfare > PeakFanfare) PeakFanfare = beat.Fanfare;
        if (beat.Event != SpendEvent) return;
        var source = beat.Source.Length > 0 ? beat.Source
                   : Cause.Length > 0 ? Cause
                   : PlayingCard;
        _spends.Add(new StageSpendRecord(source, beat.Moved,
                                         beat.Fanfare + beat.Moved,
                                         _upToCap));
        _upToCap = -1;
    }

    public const string ArriveEvent = "arrive";
    public const string ActEvent = "act";
    public const string LeaveEvent = "leave";
    public const string GainEvent = "gain";
    public const string SpendEvent = "spend";
    public const string DrainEvent = "drain";
    public const string RepayEvent = "repay";

    /// <summary>A Power dealt damage (Critics' Darling, Salon's Encore,
    /// Thunderous Applause): the Power is the beat's source, the reach
    /// ("all" or "random") its reason (the drain-line round, 2026-10-09).
    /// </summary>
    public const string HitEvent = "hit";

    /// <summary>A guest's line fired (the pool to 75, sec.3).</summary>
    public const string LineEvent = "line";

    /// <summary>A duplicate Guest Star moved its guest to the newest seat.
    /// </summary>
    public const string MoveEvent = "repeat";

    // ---- the wire ------------------------------------------------------

    /// <summary>
    /// `EB-735`. THE WIRE'S VIEW: a plain dictionary of primitives the bridge
    /// reaches by reflection (<c>vendor/STS2_MCP/gits/GitsFurinaStage.cs</c>)
    /// and <c>understudy/blindplay_board.furina_stage</c> reads. EMPTY is
    /// "this seat is not playing it"; populated is her kit, populated even
    /// with nobody on stage.
    /// </summary>
    public static Dictionary<string, object?> Snapshot(Player? player)
    {
        var snapshot = new Dictionary<string, object?>();
        var creature = player?.Creature;
        if (creature == null || !FurinaStage.LiveFor(creature))
        {
            return snapshot;
        }
        var ledger = For(creature);
        snapshot["live"] = true;
        snapshot["fanfare"] = ledger.Fanfare;
        snapshot["gained_this_turn"] = ledger.GainedThisTurn;
        snapshot["spent_this_turn"] = ledger.SpentThisTurn;
        snapshot["drained"] = ledger.Drained;
        snapshot["drained_past"] = ledger.DrainedPast;
        // The Spend round (2026-10-10): A Five-Century Act is in play, so the
        // past-line part returns after combat and the page says so.
        snapshot["past_returns"] = ledger.Mods.FiveCenturyAct > 0;
        snapshot["entry_hp"] = ledger.EntryHp;
        snapshot["entry_max_hp"] = ledger.EntryMaxHp;
        snapshot["drain_line"] = ledger.Line;
        snapshot["drain_line_why"] = ledger.LineWhy;
        snapshot["capacity"] = ledger.Capacity;
        StageForecast? forecast;
        try
        {
            forecast = FurinaStage.Forecast(creature);
        }
        catch (System.Exception)
        {
            forecast = null;
        }
        snapshot["seats"] = ledger.Seats
            .Select((seat, index) => (object?)new Dictionary<string, object?>
            {
                ["member"] = FurinaStage.Name(seat.Who),
                ["name"] = DisplayName(seat.Who),
                ["seat"] = index,
                ["seat_key"] = seat.Key,
                ["guest"] = true,
                ["upgraded"] = seat.Upgraded,
                ["price"] = 0,
                ["entity_id"] = seat.Pet?.CombatId.ToString(),
            })
            .ToList();
        snapshot["log"] = ledger.Beats
            .Select(beat => (object?)new Dictionary<string, object?>
            {
                ["event"] = beat.Event,
                ["member"] = FurinaStage.Name(beat.Who),
                ["name"] = DisplayName(beat.Who),
                ["seat"] = beat.Seat,
                ["seat_key"] = beat.SeatKey,
                ["fanfare"] = beat.Fanfare,
                ["moved"] = beat.Moved,
                ["reason"] = beat.Reason,
                ["target"] = beat.Target,
                ["target_id"] = beat.TargetId,
                ["each"] = beat.Each,
                ["struck"] = beat.Struck,
                ["by"] = beat.By,
                ["by_member"] = beat.By.ToLowerInvariant(),
                ["dealt"] = beat.Dealt,
                ["target_hp"] = beat.TargetHp,
                ["blocked"] = beat.Blocked,
                ["standing"] = beat.Standing,
                ["source"] = beat.Source,
            })
            .ToList();
        snapshot["forecast"] = ForecastSnapshot(forecast, ledger.Fanfare);
        return snapshot;
    }

    private static Dictionary<string, object?>? ForecastSnapshot(
        StageForecast? forecast, int fanfare)
    {
        if (forecast == null) return null;
        return new Dictionary<string, object?>
        {
            // No guest act moves Fanfare or gives Block directly (Charlotte's
            // Repay prints its Fanfare as it lands): the page's two figures.
            ["fanfare_after"] = fanfare,
            ["block"] = 0,
            ["acts"] = forecast.Cues
                .Select(cue => (object?)new Dictionary<string, object?>
                {
                    ["member"] = FurinaStage.Name(cue.Who),
                    ["name"] = DisplayName(cue.Who),
                    ["seat_key"] = cue.Key,
                    ["kind"] = cue.Kind.ToString().ToLowerInvariant(),
                    ["amount"] = cue.Amount,
                    ["element"] = cue.Element,
                    ["target"] = cue.Target,
                    ["times"] = 1,
                    ["price"] = 0,
                    ["skips"] = false,
                })
                .ToList(),
        };
    }

    /// <summary>The name a guest prints, off one table so the page and the
    /// bodies agree.</summary>
    public static string DisplayName(StagePerformer who) => who.ToString();
}
