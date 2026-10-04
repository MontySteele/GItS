using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>A seat and the performer standing in it. Performers have no bars
/// (rule 1 of the re-founding): a seat is a name, a key and a body.</summary>
public sealed class StageSeat
{
    internal StageSeat(StagePerformer who)
    {
        Who = who;
        Key = System.Threading.Interlocked.Increment(ref _nextKey);
    }

    private static int _nextKey;

    public StagePerformer Who { get; }

    /// <summary>Which seat, told apart from a twin (the trio can be cloned).
    /// Unique per seat object, never reused.</summary>
    public int Key { get; }

    /// <summary>The body this seat is wearing, or null until
    /// <c>FurinaStagePets.Sync</c> has fielded one (always null headless).
    /// </summary>
    public Creature? Pet { get; internal set; }
}

/// <summary>
/// ONE THING THE STAGE DID, for the blind-play page (`EB-735`). The record's
/// shape is the wire's (<see cref="FurinaStageLedger.Snapshot"/>), kept from
/// the bar era so the page keeps reading it; the re-founding files these
/// events: <c>arrive</c>, <c>act</c>, <c>skip</c> (a star that could not
/// pay), <c>pay</c>, <c>bow</c>, <c>leave</c>, <c>walk_on</c>, <c>cue</c>,
/// <c>move</c>, <c>gain</c> and <c>spend</c>.
/// <see cref="Fanfare"/> is FURINA'S Fanfare after the beat (the one number);
/// <see cref="Moved"/> is what the beat moved, measured on the board.
/// </summary>
public readonly record struct StageBeat(
    string Event, StagePerformer Who, int Seat, int Fanfare, int Moved,
    string Reason, string Target = "", string TargetId = "", int Each = -1,
    int Hp = -1, int Struck = -1, string By = "", int SeatKey = -1,
    int Dealt = -1, int TargetHp = -1, int Blocked = -1, int Caught = 0,
    int Standing = -1, string Source = "");

/// <summary>
/// What the stage reads off Furina's powers and relics, in one record, so a
/// headless pin can set them (<see cref="FurinaStageLedger.ModsOverride"/>)
/// and the game reads them live (<see cref="FurinaStage.ModsOf"/>).
/// </summary>
public sealed record StageMods
{
    /// <summary>Rule 6: Rehearsal stacks.</summary>
    public int Rehearsal { get; init; }

    /// <summary>Seats: 3, or 4 under Sold Out.</summary>
    public int Capacity { get; init; } = FurinaStageLaw.Seats;

    /// <summary>Thunderous Applause: cards drawn per Bow.</summary>
    public int BowDraw { get; init; }

    /// <summary>Curtain Call Bouquet: a Bow's act resolves this many times.
    /// </summary>
    public int BowActs { get; init; } = 1;

    /// <summary>Stagehand's Gloves: Block per Bow.</summary>
    public int BowBlock { get; init; }

    /// <summary>A Five-Century Act is in play.</summary>
    public bool FiveCentury { get; init; }

    /// <summary>Critics' Darling copies.</summary>
    public int CriticsDarling { get; init; }

    /// <summary>Star Billing: cards drawn when a Guest Star joins.</summary>
    public int StarBilling { get; init; }

    /// <summary>Star Turn copies.</summary>
    public int StarTurn { get; init; }

    /// <summary>Full House: extra acts on a full stage.</summary>
    public int FullHouse { get; init; }

    /// <summary>Palais Ledger: Fanfare off each Spend N.</summary>
    public int SpendDiscount { get; init; }

    public static readonly StageMods None = new();
}

/// <summary>
/// THE STAGE ITSELF (v2, the re-founding): the seats front first, Furina's
/// one Fanfare number, the flow counts and every once-a-turn latch -- every
/// rule that is arithmetic rather than an engine command. The ordering of
/// acts, Bows and summons is <see cref="StageDirector"/>'s; this class is
/// synchronous so the headless pins can ask it anything.
///
/// PER FURINA AND PER COMBAT, keyed by combat identity (the overhaul ledgers'
/// rule, R205): in co-op the other seat's stage is not hers, and pets live
/// one combat.
/// </summary>
public sealed class FurinaStageLedger
{
    private static object? _combat;

    private static readonly Dictionary<Creature, FurinaStageLedger> _byFurina =
        new();

    private readonly List<StageSeat> _seats = new();

    /// <summary>This Furina's stage for this combat, created on first ask.
    /// </summary>
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
            ledger = new FurinaStageLedger { _furina = furina };
            _byFurina[furina] = ledger;
        }
        return ledger;
    }

    /// <summary>Test seam: forget every stage.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byFurina.Clear();
    }

    /// <summary>A free-standing stage with no Furina, for the forecast's
    /// clone and the headless pins.</summary>
    public static FurinaStageLedger Detached() => new();

    private Creature? _furina;

    /// <summary>The Furina this stage is hers; null on a detached stage.
    /// </summary>
    public Creature? Furina => _furina;

    // ---- the mods ------------------------------------------------------

    /// <summary>Test seam: the mods a headless pin sets. Null in the game,
    /// where they are read live off her powers and relics.</summary>
    public StageMods? ModsOverride { get; set; }

    /// <summary>What her powers and relics make of the rules right now.
    /// </summary>
    public StageMods Mods =>
        ModsOverride ?? (_furina != null ? FurinaStage.ModsOf(_furina)
                                         : StageMods.None);

    public int Rehearsal => Mods.Rehearsal;

    public int Capacity => Mods.Capacity;

    // ---- the seats -----------------------------------------------------

    /// <summary>The stage, FRONT FIRST.</summary>
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

    /// <summary>The seat this performer stands in, front = 0, or -1.</summary>
    public int SeatIndexOf(StagePerformer who)
    {
        for (var i = 0; i < _seats.Count; i++)
        {
            if (_seats[i].Who == who) return i;
        }
        return -1;
    }

    /// <summary>A newcomer takes the back-most free seat. Returns the seat,
    /// or null on a full stage (the caller makes room first).</summary>
    public StageSeat? Seat(StagePerformer who)
    {
        if (IsFull) return null;
        var seat = new StageSeat(who);
        _seats.Add(seat);
        MarkSeated(who);
        Note(new StageBeat(ArriveEvent, who, _seats.Count - 1, Fanfare, 0, "",
                           SeatKey: seat.Key));
        return seat;
    }

    /// <summary>Take the performer in <paramref name="index"/> off the stage
    /// (the others close ranks). Returns it, or null.</summary>
    public StageSeat? Unseat(int index, string reason)
    {
        if (index < 0 || index >= _seats.Count) return null;
        var seat = _seats[index];
        _seats.RemoveAt(index);
        Note(new StageBeat(LeaveEvent, seat.Who, -1, Fanfare, 0, reason,
                           SeatKey: seat.Key));
        return seat;
    }

    /// <summary>Move the performer in <paramref name="index"/> to the front.
    /// True when anyone moved.</summary>
    public bool MoveToFront(int index)
    {
        if (index <= 0 || index >= _seats.Count) return false;
        var seat = _seats[index];
        _seats.RemoveAt(index);
        _seats.Insert(0, seat);
        Note(new StageBeat(MoveEvent, seat.Who, 0, Fanfare, 0, "",
                           SeatKey: seat.Key));
        return true;
    }

    /// <summary>Rule 4: the front-most SALON member's seat, or -1.</summary>
    public int FrontMostSalon()
    {
        for (var i = 0; i < _seats.Count; i++)
        {
            if (!FurinaStage.IsGuest(_seats[i].Who)) return i;
        }
        return -1;
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
        PaidThisTurn = 0;
        SpentThisPlay = 0;
        BowsThisCombat = 0;
        CardsPlayedThisTurn = 0;
        SalonSummonCardsThisTurn = 0;
        CueCardsThisTurn = 0;
        CuedThisTurn = false;
        ChevreuseActedThisTurn = false;
        ReturnedThisTurn = false;
        GuestBookSpent = false;
        VerdictTarget = null;
        ActDamageMultiplier = 1;
        HpLossEvents = 0;
        BlockedTotal = 0;
        _marks.Clear();
        _pendingChanges.Clear();
        Opened = false;
    }

    /// <summary>Salon Solitaire has opened this combat's stage.</summary>
    public bool Opened { get; set; }

    /// <summary>Rule 1: combat opens with Usher on stage -- once, and only
    /// onto an empty stage. True the first time.</summary>
    public bool Open()
    {
        if (Opened) return false;
        Opened = true;
        if (IsEmpty) Seat(StagePerformer.Usher);
        return true;
    }

    // ---- Fanfare: one number on Furina (rule 5) ------------------------

    /// <summary>Furina's Fanfare. No cap, no fade; hits never touch it.
    /// </summary>
    public int Fanfare { get; private set; }

    /// <summary>The flow counts (sec.8): Fanfare gained, and Fanfare a card's
    /// Spend took, since the start of her turn. A star's payment is not a
    /// Spend. They hold through the end-of-turn sequence.</summary>
    public int GainedThisTurn { get; private set; }

    public int SpentThisTurn { get; private set; }

    /// <summary>What the stars' (and Chevreuse's) payments took this turn.
    /// Not a Spend; the page and the seats read it.</summary>
    public int PaidThisTurn { get; private set; }

    /// <summary>What THIS card play's spend-all took (`stage_spent`).
    /// </summary>
    public int SpentThisPlay { get; private set; }

    private readonly List<int> _pendingChanges = new();

    /// <summary>Every change to her Fanfare since the director last settled,
    /// as sizes (Critics' Darling deals each one).</summary>
    public IReadOnlyList<int> PendingChanges => _pendingChanges;

    /// <summary>Take the pending changes.</summary>
    public IReadOnlyList<int> TakeChanges()
    {
        var taken = _pendingChanges.ToList();
        _pendingChanges.Clear();
        return taken;
    }

    /// <summary>Gain Fanfare. Returns what was gained.</summary>
    public int Gain(int amount, string source = "")
    {
        if (amount <= 0) return 0;
        Fanfare += amount;
        GainedThisTurn += amount;
        _pendingChanges.Add(amount);
        Note(new StageBeat(GainEvent, StagePerformer.Usher, -1, Fanfare,
                           amount, source));
        return amount;
    }

    /// <summary>Can a Spend of <paramref name="price"/> be paid?</summary>
    public bool CanSpend(int price) => price >= 0 && Fanfare >= price;

    /// <summary>A card's Spend N, at the full price only. A Spend of 0 moves
    /// nothing and is no Spend. True when it was paid.</summary>
    public bool Spend(int price)
    {
        if (price <= 0 || Fanfare < price) return false;
        Fanfare -= price;
        SpentThisTurn += price;
        _pendingChanges.Add(price);
        Note(new StageBeat(SpendEvent, StagePerformer.Usher, -1, Fanfare,
                           price, ""));
        return true;
    }

    /// <summary>"Spend all your Fanfare." Nothing held is no Spend. Records
    /// what was spent as this play's <see cref="SpentThisPlay"/>.</summary>
    public int SpendAll()
    {
        var held = Fanfare;
        SpentThisPlay = 0;
        if (held <= 0 || !Spend(held)) return 0;
        SpentThisPlay = held;
        return held;
    }

    /// <summary>A star's (or Chevreuse's) payment for its act. NOT a Spend.
    /// False when short: the act is skipped and nothing is taken.</summary>
    public bool TryPay(StagePerformer who, int price)
    {
        if (price <= 0) return true;
        if (Fanfare < price) return false;
        Fanfare -= price;
        PaidThisTurn += price;
        _pendingChanges.Add(price);
        Note(new StageBeat(PayEvent, who, SeatIndexOf(who), Fanfare, price,
                           "", By: DisplayName(who)));
        return true;
    }

    /// <summary>A fresh per-play spend record (every card play).</summary>
    public void BeginPlay() => SpentThisPlay = 0;

    // ---- the turn's counts and latches ---------------------------------

    public int BowsThisCombat { get; set; }

    /// <summary>Cards she has finished playing this turn (Opening Number).
    /// </summary>
    public int CardsPlayedThisTurn { get; set; }

    /// <summary>Salon summon cards played this turn (Escoffier's line).
    /// </summary>
    public int SalonSummonCardsThisTurn { get; set; }

    /// <summary>Cue cards played this turn (Lyney's line).</summary>
    public int CueCardsThisTurn { get; set; }

    /// <summary>A performer has been Cued this turn (Lynette's line moves the
    /// first one).</summary>
    public bool CuedThisTurn { get; set; }

    /// <summary>Chevreuse has made her one act this turn.</summary>
    public bool ChevreuseActedThisTurn { get; set; }

    /// <summary>A Five-Century Act has returned someone this turn.</summary>
    public bool ReturnedThisTurn { get; set; }

    /// <summary>Guest Book's once-a-combat latch.</summary>
    public bool GuestBookSpent { get; set; }

    /// <summary>Oratrice's Verdict: this turn's target for every random pick
    /// a performer makes.</summary>
    public Creature? VerdictTarget { get; set; }

    /// <summary>Arkhe Alignment's or Dual Nature's Ousia: this turn's
    /// multiple of every act's damage.</summary>
    public int ActDamageMultiplier { get; set; } = 1;

    /// <summary>The top of Furina's turn: the flow counts and the once-a-turn
    /// latches reset (sec.8).</summary>
    public void OpenTurn()
    {
        GainedThisTurn = 0;
        SpentThisTurn = 0;
        PaidThisTurn = 0;
        CardsPlayedThisTurn = 0;
        SalonSummonCardsThisTurn = 0;
        CueCardsThisTurn = 0;
        CuedThisTurn = false;
        ChevreuseActedThisTurn = false;
        ReturnedThisTurn = false;
    }

    /// <summary>After the end-of-turn sweep: this turn's Ousia and Verdict
    /// are spent.</summary>
    public void CloseTurn()
    {
        ActDamageMultiplier = 1;
        VerdictTarget = null;
    }

    // ---- Sigewinne's and Wriothesley's readings ------------------------

    /// <summary>Times Furina lost HP this combat (Sigewinne).</summary>
    public int HpLossEvents { get; private set; }

    /// <summary>Damage Furina's Block stopped this combat (Wriothesley).
    /// </summary>
    public int BlockedTotal { get; private set; }

    private readonly Dictionary<StagePerformer, (int Hp, int Blocked)> _marks = new();

    public void NoteHpLoss() => HpLossEvents++;

    public void NoteBlocked(int amount)
    {
        if (amount > 0) BlockedTotal += amount;
    }

    /// <summary>A performer's readings start now (it took its seat, or it
    /// acted).</summary>
    public void MarkSeated(StagePerformer who) =>
        _marks[who] = (HpLossEvents, BlockedTotal);

    /// <summary>HP losses since <paramref name="who"/> last acted or sat.
    /// </summary>
    public int HpLossesSince(StagePerformer who) =>
        HpLossEvents - (_marks.TryGetValue(who, out var m) ? m.Hp : 0);

    /// <summary>Blocked damage since <paramref name="who"/> last acted or
    /// sat.</summary>
    public int BlockedSince(StagePerformer who) =>
        BlockedTotal - (_marks.TryGetValue(who, out var m) ? m.Blocked : 0);

    // ---- the performance log (`EB-735`) --------------------------------

    private readonly List<StageBeat> _beats = new();

    /// <summary>What the stage did since she last ended a turn, in order.
    /// Cleared just before the end-of-turn sweep it is about.</summary>
    public IReadOnlyList<StageBeat> Beats => _beats;

    public void Note(StageBeat beat)
    {
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

    /// <summary>The power whose effect is resolving now, stamped on every
    /// beat filed meanwhile. Empty while a card resolves.</summary>
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

    public const string ArriveEvent = "arrive";
    public const string ActEvent = "act";
    public const string SkipEvent = "skip";
    public const string PayEvent = "pay";
    public const string BowEvent = "bow";
    public const string LeaveEvent = "leave";
    public const string WalkOnEvent = "walk_on";
    public const string CueEvent = "cue";
    public const string MoveEvent = "move";
    public const string GainEvent = "gain";
    public const string SpendEvent = "spend";

    // ---- the wire ------------------------------------------------------

    /// <summary>
    /// `EB-735`. THE WIRE'S VIEW OF THE STAGE: a plain dictionary of
    /// primitives the bridge reaches by reflection
    /// (<c>vendor/STS2_MCP/gits/GitsFurinaStage.cs</c>) and
    /// <c>understudy/blindplay_board.furina_stage</c> reads. An EMPTY map is
    /// "the rule is here and this seat is not playing it"; a populated one is
    /// her stage, populated even with nobody standing.
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
        snapshot["paid_this_turn"] = ledger.PaidThisTurn;
        snapshot["rehearsal"] = ledger.Rehearsal;
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
        snapshot["act_block"] = forecast?.Block ?? 0;
        snapshot["seats"] = ledger.Seats
            .Select((seat, index) => (object?)new Dictionary<string, object?>
            {
                ["member"] = FurinaStage.Name(seat.Who),
                ["name"] = DisplayName(seat.Who),
                ["seat"] = index,
                ["seat_key"] = seat.Key,
                ["guest"] = FurinaStage.IsGuest(seat.Who),
                ["price"] = FurinaStageLaw.PriceOf(seat.Who),
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
        snapshot["forecast"] = ForecastSnapshot(forecast);
        return snapshot;
    }

    private static Dictionary<string, object?>? ForecastSnapshot(
        StageForecast? forecast)
    {
        if (forecast == null) return null;
        return new Dictionary<string, object?>
        {
            ["fanfare_after"] = forecast.FanfareAfter,
            ["block"] = forecast.Block,
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
                    ["times"] = cue.Times,
                    ["price"] = cue.Price,
                    ["skips"] = cue.Skips,
                })
                .ToList(),
        };
    }

    /// <summary>The name a performer prints, off one table so the page and
    /// the bodies agree.</summary>
    public static string DisplayName(StagePerformer who) => who switch
    {
        StagePerformer.Chevalmarin => "Surintendante Chevalmarin",
        StagePerformer.Crabaletta => "Mademoiselle Crabaletta",
        StagePerformer.Usher => "Gentilhomme Usher",
        _ => who.ToString(),
    };
}
