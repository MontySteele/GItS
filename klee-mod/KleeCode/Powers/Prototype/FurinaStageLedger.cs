using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

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

/// <summary>
/// What the kit reads off Furina's powers, in one record, so a headless pin
/// can set them (<see cref="FurinaStageLedger.ModsOverride"/>) and the game
/// reads them live (<see cref="FurinaStage.ModsOf"/>).
/// </summary>
public sealed record StageMods
{
    /// <summary>Seats: three.</summary>
    public int Capacity { get; init; } = FurinaStageLaw.Seats;

    /// <summary>Universal Revelry copies: every Fanfare gain is multiplied by
    /// one more than this (sec.17).</summary>
    public int Revelry { get; init; }

    /// <summary>Salon's Encore: damage to ALL enemies per Drain.</summary>
    public int SalonsEncore { get; init; }

    /// <summary>Endless Waltz copies: each Repay of N deals N this many times.
    /// </summary>
    public int EndlessWaltz { get; init; }

    /// <summary>Thunderous Applause: damage to ALL enemies per Spend.</summary>
    public int Thunderous { get; init; }

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
            };
            _byFurina[furina] = ledger;
        }
        return ledger;
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
    public StageSeat? Seat(StagePerformer who)
    {
        if (IsFull) return null;
        var seat = new StageSeat(who);
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
        Drained = 0;
        DrainedThisTurn = 0;
        RepaidThisTurn = 0;
        CharlotteDrewThisTurn = false;
        LynetteFiredThisTurn = false;
        Draining = false;
        Opened = false;
    }

    /// <summary>The combat's opening has been recorded.</summary>
    public bool Opened { get; set; }

    /// <summary>Record the opening once: the entry HP the line is read from.
    /// True the first time.</summary>
    public bool Open(int entryHp)
    {
        if (Opened) return false;
        Opened = true;
        EntryHp = entryHp;
        return true;
    }

    // ---- the HP loan (rules 1, 2 and the curtain call) ------------------

    /// <summary>The HP she started this combat with.</summary>
    public int EntryHp { get; set; }

    /// <summary>Rule 1: the lowest HP a Drain may reach.</summary>
    public int Line => FurinaStageLaw.LineOf(EntryHp);

    /// <summary>Can she Drain <paramref name="amount"/> at
    /// <paramref name="hp"/>? Not below the line.</summary>
    public bool CanDrain(int amount, int hp) =>
        amount > 0 && hp - amount >= Line;

    /// <summary>HP lost to her Drains and not yet repaid.</summary>
    public int Drained { get; private set; }

    /// <summary>HP drained this turn (the page and the pins read it).
    /// </summary>
    public int DrainedThisTurn { get; private set; }

    /// <summary>HP repaid this turn.</summary>
    public int RepaidThisTurn { get; private set; }

    /// <summary>A Drain's own HP loss is resolving: the HP-loss hook must not
    /// count it, because the Drain counts it itself.</summary>
    public bool Draining { get; set; }

    public void NoteDrain(int amount)
    {
        if (amount <= 0) return;
        Drained += amount;
        DrainedThisTurn += amount;
    }

    /// <summary>Rule 2: how much a Repay of <paramref name="amount"/> returns
    /// at this HP: never more than she drained, never past Max HP. Clamps the
    /// ledger first (HP + drained never exceeds Max HP).</summary>
    public int RepayRoom(int amount, int hp, int maxHp)
    {
        Drained = System.Math.Min(Drained, System.Math.Max(0, maxHp - hp));
        return System.Math.Max(0, System.Math.Min(amount, Drained));
    }

    public void NoteRepay(int amount)
    {
        if (amount <= 0) return;
        Drained = System.Math.Max(0, Drained - amount);
        RepaidThisTurn += amount;
    }

    /// <summary>THE CURTAIN CALL (sec.16): the HP that returns when the
    /// combat ends -- every drained HP, up to Max HP. Empties the ledger.
    /// </summary>
    public int CurtainCall(int hp, int maxHp)
    {
        var back = System.Math.Max(0, System.Math.Min(Drained, maxHp - hp));
        Drained = 0;
        return back;
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

    /// <summary>Gain Fanfare: <paramref name="amount"/> times one more than
    /// her Universal Revelry copies (sec.17: "You gain twice as much
    /// Fanfare."; a second copy makes it three times). Returns what was
    /// gained.</summary>
    public int Gain(int amount, string source = "")
    {
        if (amount <= 0) return 0;
        var gained = amount * (1 + System.Math.Max(0, Mods.Revelry));
        Fanfare += gained;
        GainedThisTurn += gained;
        Note(new StageBeat(GainEvent, default, -1, Fanfare, gained, source));
        return gained;
    }

    /// <summary>Can a Spend of <paramref name="price"/> be paid?</summary>
    public bool CanSpend(int price) => price >= 0 && Fanfare >= price;

    /// <summary>A Spend N, at the full price only. A Spend of 0 moves nothing
    /// and is no Spend. True when it was paid.</summary>
    public bool Spend(int price)
    {
        if (price <= 0 || Fanfare < price) return false;
        Fanfare -= price;
        SpentThisTurn += price;
        Note(new StageBeat(SpendEvent, default, -1, Fanfare, price, ""));
        return true;
    }

    /// <summary>"Spend all your Fanfare." Nothing held is no Spend.</summary>
    public int SpendAll()
    {
        var held = Fanfare;
        SpentThisPlay = 0;
        if (held <= 0 || !Spend(held)) return 0;
        SpentThisPlay = held;
        return held;
    }

    /// <summary>A fresh per-play spend record (every card play).</summary>
    public void BeginPlay() => SpentThisPlay = 0;

    // ---- the once-a-turn latches ---------------------------------------

    /// <summary>Charlotte's line has drawn this turn.</summary>
    public bool CharlotteDrewThisTurn { get; set; }

    /// <summary>Lynette's line has paid this turn.</summary>
    public bool LynetteFiredThisTurn { get; set; }

    /// <summary>The top of her turn: the flow counts and latches reset. They
    /// held through the end-of-turn sequence and the enemies' turn.</summary>
    public void OpenTurn()
    {
        GainedThisTurn = 0;
        SpentThisTurn = 0;
        DrainedThisTurn = 0;
        RepaidThisTurn = 0;
        CharlotteDrewThisTurn = false;
        LynetteFiredThisTurn = false;
    }

    // ---- the performance log (`EB-735`) --------------------------------

    private readonly List<StageBeat> _beats = new();

    /// <summary>What the kit did since she last ended a turn, in order.
    /// </summary>
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

    public const string ArriveEvent = "arrive";
    public const string ActEvent = "act";
    public const string LeaveEvent = "leave";
    public const string GainEvent = "gain";
    public const string SpendEvent = "spend";
    public const string DrainEvent = "drain";
    public const string RepayEvent = "repay";

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
        snapshot["entry_hp"] = ledger.EntryHp;
        snapshot["drain_line"] = ledger.Line;
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
