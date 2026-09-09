using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>Why a performer left the stage. Only one of the three earns a bow.
/// </summary>
public enum StageDeparture
{
    /// <summary>Rotated off the front to make room (rule 3). No bow: a bow is
    /// earned by Spend alone (sec.10 default 5).</summary>
    Rotated,

    /// <summary>Emptied by a hit (rule 7, first clause). No bow.</summary>
    Struck,

    /// <summary>Emptied by Spend (rule 7, second clause). Bows (rule 9).
    /// </summary>
    Spent,
}

/// <summary>One performer leaving, and how. The <c>Bows</c> read is the rule
/// rather than a field, so no caller can record a departure and then decide
/// for itself whether a bow was earned.</summary>
public readonly struct StageExit
{
    public StageExit(StagePerformer who, StageDeparture cause)
    {
        Who = who;
        Cause = cause;
    }

    public StagePerformer Who { get; }

    public StageDeparture Cause { get; }

    public bool Bows => Cause == StageDeparture.Spent;
}

/// <summary>What a Spend did. <see cref="Fired"/> is the rider's own question
/// -- rule 8 says a rider fires IN FULL whenever anybody is on stage, however
/// little they can pay, and cannot fire at all on an empty one.</summary>
public readonly struct StageSpend
{
    public StageSpend(bool fired, int paid, StageExit? exit)
    {
        Fired = fired;
        Paid = paid;
        Exit = exit;
    }

    public bool Fired { get; }

    /// <summary>What the lead actually had. Never more than the ask, often
    /// less, and never the reason the rider does or does not fire.</summary>
    public int Paid { get; }

    public StageExit? Exit { get; }
}

/// <summary>What one attack's post-Block remainder did to the stage.</summary>
public readonly struct StageAbsorb
{
    public StageAbsorb(int absorbed, int reachedFurina, StageExit? exit)
    {
        Absorbed = absorbed;
        ReachedFurina = reachedFurina;
        Exit = exit;
    }

    public int Absorbed { get; }

    public int ReachedFurina { get; }

    public StageExit? Exit { get; }
}

/// <summary>What a summon did: who arrived, and who rotated off to make room.
/// </summary>
public readonly struct StageSummon
{
    public StageSummon(StagePerformer arrived, int atFanfare, StageExit? exit)
    {
        Arrived = arrived;
        AtFanfare = atFanfare;
        Exit = exit;
    }

    public StagePerformer Arrived { get; }

    /// <summary>The bar the newcomer took the back seat with -- normally
    /// <see cref="FurinaStageLaw.SummonFanfare"/>, and the LEAVER'S bar on a
    /// rotation (rule 3, "pools are never lost to rotation").</summary>
    public int AtFanfare { get; }

    public StageExit? Exit { get; }
}

/// <summary>A seat and the performer standing in it. Mutable because the bar
/// moves every turn; the LIST is what carries the seat order.</summary>
public sealed class StageSeat
{
    internal StageSeat(StagePerformer who, int fanfare)
    {
        Who = who;
        Fanfare = fanfare;
    }

    public StagePerformer Who { get; }

    /// <summary>The bar. No cap (rule 4); zero means the performer is leaving
    /// and the ledger removes it in the same call.</summary>
    public int Fanfare { get; internal set; }

    /// <summary>
    /// THE BODY THIS SEAT IS WEARING, or null until
    /// <c>FurinaStagePets.Sync</c> has fielded one -- which is always, in a
    /// headless pin.
    ///
    /// ON THE SEAT AND NOT LOOKED UP BY KIND, because duplicates are legal:
    /// two Crabalettas may stand on the stage at once (the summon Commons name
    /// their performer and nothing forbids naming one twice, exactly as the
    /// shipped <i>Grand Gala</i> deploys Crabaletta twice one arm over). A
    /// reconciler that matched a pet to a seat by MODEL TYPE would hand the
    /// front seat's bar to the back seat's body on the turn one of them left.
    /// </summary>
    public Creature? Pet { get; internal set; }
}

/// <summary>
/// ONE THING THE STAGE DID, for the page (`EB-735`).
///
/// THE FIND (round one, sec.2). Nothing on the blind-play page named a
/// performer, a seat or a bar, so in some 550 actions no seat ever knew who was
/// on stage; each learned the roster from one glossary line and inferred bars
/// by firing readers and reading the result backwards. The BOARD half of that
/// row is the seats and their bars, which the ledger already holds. This is
/// the other half: what happened to them, in the order it happened, because a
/// bar that moved between two screens is a fact no snapshot of the bars can
/// carry.
///
/// THE NUMBER IS WHAT THE BOARD LOST, not what the rule printed -- `EB-511`'s
/// lesson one kit over, where a receipt quoting a clause's own figure sent a
/// seat looking for four damage a Vulnerable had made six. Crabaletta's act
/// prints 5 and files what the enemy's HP actually fell by; the Usher's files
/// the Block Furina actually gained. A beat with no number files 0 and the
/// page prints none.
/// </summary>
/// <param name="Event">`arrive`, `act`, `bow`, `leave` or `rotate` -- the
/// five moments the row names, in the page's own vocabulary rather than in
/// this file's method names.</param>
/// <param name="Who">The performer. `Name` is the sheet name; the page prints
/// the display name it gets from the seat list.</param>
/// <param name="Seat">The seat this happened in, front = 0, or -1 where the
/// performer is no longer standing in one.</param>
/// <param name="Fanfare">The bar AFTER the beat -- what the seat would read if
/// it looked now.</param>
/// <param name="Moved">What the board lost or gained, measured; 0 where the
/// beat moved no number.</param>
/// <param name="Reason">Why a `leave` happened: `hit`, `spend`, `rotated` or
/// `final_bow`. Empty on every other event.</param>
public readonly record struct StageBeat(
    string Event, StagePerformer Who, int Seat, int Fanfare, int Moved,
    string Reason);


/// <summary>
/// THE STAGE ITSELF: three seats, front first, and every rule in brief sec.3
/// that is arithmetic rather than an engine command.
///
/// WHY THE RULES LIVE HERE AND NOT ON THE PET. The performers ARE pets and
/// their bars ARE the pets' HP bars on screen -- but a pet is a
/// <c>Creature</c> in a live <c>CombatState</c>, and <c>KleeTests</c> runs
/// with no combat, no scene tree and no <c>PlayerChoiceContext</c>
/// (KleeTests/README.md, "the headless boundary"). A rule written against the
/// pet would have been a rule no pin could ask a question of, and this arm's
/// whole acceptance is questions about rules: does a 12 through Block 6 kill a
/// 3-bar lead and land 3 on her, does a 3x2 flurry leave her whole, does a
/// Spend 3 from a 1-bar lead fire in full.
///
/// SO THE LEDGER IS CANONICAL AND THE PET MIRRORS IT.
/// <see cref="FurinaStagePets"/> pushes each seat's <see cref="StageSeat.Fanfare"/>
/// onto its pet as max-and-current HP after every change. That is safe rather
/// than merely convenient, and by construction: enemies cannot target a pet at
/// all (<c>MonsterModel.PerformMove</c> is handed
/// <c>CombatState.PlayerCreatures</c>, which is <c>Where(c =&gt; c.IsPlayer)</c>,
/// and a pet has no <c>Player</c> -- the finding written out in
/// <c>BakeKuragePet</c>), so nothing in the game can move a performer's HP
/// behind the ledger's back. Every point a performer loses comes through
/// <see cref="Absorb"/> or <see cref="Spend"/>.
///
/// PER FURINA AND PER COMBAT, keyed the way <c>FurinaReframeLedger</c>,
/// <c>KleeOverhaulLedger</c> and <c>KokomiOverhaulLedger</c> are keyed and for
/// their reason (R205): in co-op the other seat's stage is not hers, and pets
/// live one combat (rule 1), so a table that outlived the combat would field a
/// stage the fight never summoned.
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
            ledger = new FurinaStageLedger();
            _byFurina[furina] = ledger;
        }
        return ledger;
    }

    /// <summary>Test seam: forget every stage. The mod never calls it -- the
    /// combat-identity check above is what clears a real run.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byFurina.Clear();
    }

    // ---- the performance log (`EB-735`) ------------------------------

    private readonly List<StageBeat> _beats = new();

    /// <summary>
    /// What the stage has done since she last ended a turn, in order.
    ///
    /// THE WINDOW IS THE TURN BREAK AND NOT THE TURN, deliberately, and the
    /// page says so in one line. A turn's own plays are watched as they happen
    /// -- every card resolves on a screen the seat asked for -- and the two
    /// things a seat CANNOT watch both land in the break: the end-of-turn
    /// sweep (rule 10) and what the enemies' attacks took off the lead
    /// (rule 6). Clearing at the start of her turn would wipe both a moment
    /// before the only screen that could have printed them, which is
    /// `SALON_ARRIVAL_NOTE`'s defect one arm over. So the clear is at
    /// <c>BeforeSideTurnEnd</c>, immediately before the sweep it is about.
    /// </summary>
    public IReadOnlyList<StageBeat> Beats => _beats;

    /// <summary>File one beat. THE ONE WRITER is this method, and the callers
    /// are this class's own moves plus <see cref="FurinaStage"/>'s two payout
    /// sites -- the acts and the bows, which are the only beats whose NUMBER
    /// lives on the board rather than in this file.</summary>
    public void Note(StageBeat beat) => _beats.Add(beat);

    /// <summary>The turn boundary, and the only one this log has.</summary>
    public void ClearBeats() => _beats.Clear();

    /// <summary>The seat this performer is standing in, front = 0, or -1.
    /// </summary>
    public int SeatIndexOf(StagePerformer who)
    {
        for (var i = 0; i < _seats.Count; i++)
        {
            if (_seats[i].Who == who) return i;
        }
        return -1;
    }

    /// <summary>The stage, FRONT FIRST. The head of the list is the lead, and
    /// that is the whole of the seat order: rule 6 reads
    /// <c>[0]</c>, rule 5 reads the last, and rule 3 moves the head off and
    /// appends. A second field naming the front is a second source of truth
    /// for a fact the list already carries (`EB-506`, one arm over).</summary>
    public IReadOnlyList<StageSeat> Seats => _seats;

    /// <summary>The front performer: the one that absorbs (rule 6), the one
    /// that Spend pays from (rule 8) and the one that regenerates (rule 4).
    /// </summary>
    public StageSeat? Lead => _seats.Count > 0 ? _seats[0] : null;

    /// <summary>The back-most performer, which is the LEAD when it is alone
    /// (rule 5's second sentence).</summary>
    public StageSeat? Back => _seats.Count > 0 ? _seats[^1] : null;

    public bool IsEmpty => _seats.Count == 0;

    public bool IsFull => _seats.Count >= FurinaStageLaw.Seats;

    /// <summary>Every performer on stage, front to back. What the acts walk
    /// (rule 10, "from any seat") and what the strip draws.</summary>
    public IEnumerable<StagePerformer> Company => _seats.Select(s => s.Who);

    /// <summary>
    /// RULE 3. A summon fills the back-most empty seat at
    /// <see cref="FurinaStageLaw.SummonFanfare"/>; on a FULL stage the front
    /// performer leaves without a bow, the other two step forward and the
    /// newcomer takes the back seat WITH THE LEAVER'S FANFARE.
    ///
    /// THE POOL IS NOT LOST, which is the clause that makes rotation a play
    /// and not a punishment: a three-seat stage carrying 8 on the front hands
    /// that 8 to whoever arrives. The bar moves, the performer does not.
    ///
    /// THE NEWCOMER PERFORMS AT THE END OF THE TURN AND NOT ON ARRIVAL
    /// (`EB-738`), and there is no code for it, which is the point: the acts
    /// fire at the END of her turn over whoever is on stage then (rule 10), so
    /// a performer summoned during the turn is standing there when they fire,
    /// exactly once. Pinned rather than commented, because "the rule needs no
    /// code" and "the rule is missing" look identical.
    /// </summary>
    public StageSummon Summon(StagePerformer who)
    {
        if (!IsFull)
        {
            _seats.Add(new StageSeat(who, FurinaStageLaw.SummonFanfare));
            Note(new StageBeat("arrive", who, _seats.Count - 1,
                               FurinaStageLaw.SummonFanfare, 0, ""));
            return new StageSummon(who, FurinaStageLaw.SummonFanfare, null);
        }

        var leaver = _seats[0];
        _seats.RemoveAt(0);
        _seats.Add(new StageSeat(who, leaver.Fanfare));
        // TWO BEATS AND NOT ONE, because a rotation is two things happening to
        // two performers: the front leaves with no bow (rule 3) and the
        // newcomer takes its bar. A page printing one line for the pair would
        // be the sentence the seat had to reverse-engineer.
        Note(new StageBeat("leave", leaver.Who, -1, 0, 0, "rotated"));
        Note(new StageBeat("arrive", who, _seats.Count - 1, leaver.Fanfare,
                           0, ""));
        return new StageSummon(
            who, leaver.Fanfare,
            new StageExit(leaver.Who, StageDeparture.Rotated));
    }

    /// <summary>
    /// RULE 5. "Raise N Fanfare on the back performer" -- the back-most, which
    /// is the lead when it is alone. Returns what it raised, which is 0 on an
    /// empty stage and N otherwise: bars have no cap (rule 4), so a Raise
    /// never lands short.
    ///
    /// THE BACK AND NOT THE LEAD, and it is a lever rather than a detail:
    /// sec.8's second failure mode is the cast becoming a second life bar, and
    /// Refill landing at the back is what stops a Defend-priced Refill topping
    /// up the buffer that is currently eating the hits.
    /// </summary>
    public int Raise(int amount)
    {
        if (amount <= 0 || Back is not { } seat) return 0;
        seat.Fanfare += amount;
        return amount;
    }

    /// <summary>
    /// RULE 8. Spend N pays from the LEAD. Three clauses, and the second is
    /// the one that surprises:
    ///
    ///   * enough on the bar: pays N, the rider fires, the performer stays;
    ///   * NOT enough: THE RIDER STILL FIRES IN FULL, the lead pays what it
    ///     has, and it leaves with a BOW (rule 7 second clause, rule 9).
    ///     `Paid` is what it had, and no caller may price the rider off it --
    ///     that is sec.10 default 4, "as [USER] said";
    ///   * empty stage: the rider CANNOT fire, and the card plays at its base
    ///     number. Not a refusal and not a whiff: the card is fine, the rider
    ///     is not there.
    ///
    /// A lead emptied EXACTLY by a Spend that it could afford still bows: it
    /// was emptied by Spend, which is the whole of rule 7's test.
    /// </summary>
    public StageSpend Spend(int amount)
    {
        if (Lead is not { } lead) return new StageSpend(false, 0, null);
        if (amount <= 0) return new StageSpend(true, 0, null);

        var paid = lead.Fanfare < amount ? lead.Fanfare : amount;
        lead.Fanfare -= paid;
        // The per-play record, written where the payment happens rather than
        // by the caller: `stage_spent` is what a payoff on the SAME card
        // multiplies, and by the time it resolves the bar is gone.
        SpentThisPlay = paid;
        if (lead.Fanfare > 0) return new StageSpend(true, paid, null);

        _seats.RemoveAt(0);
        Note(new StageBeat("leave", lead.Who, -1, 0, paid, "spend"));
        return new StageSpend(
            true, paid, new StageExit(lead.Who, StageDeparture.Spent));
    }

    /// <summary>
    /// RULE 6, the middle term of the damage order: Furina's Block, then the
    /// LEAD's bar, then Furina.
    ///
    /// PER ATTACK, AND IT NEVER RUNS ON. The lead absorbs what one attack put
    /// through her Block, up to its bar, and the remainder reaches HER -- not
    /// the middle seat. That is what makes the two intents different plays: a
    /// big single hit rips through the lead and lands on her, a flurry is
    /// resolved hit by hit and can kill the lead while leaving her whole.
    /// Nothing in this method loops, and that absence is the rule.
    ///
    /// A LEAD EMPTIED HERE TAKES NO BOW (rule 7, first clause). The bow is
    /// bought with a Spend; a performer that merely died did not buy one.
    ///
    /// SYNCHRONOUS ON PURPOSE. Its caller is
    /// <c>FurinaResourceHooks.ModifyHpLostBeforeOsty</c>, which the engine
    /// calls per damage instance and which returns a number rather than
    /// awaiting one. The pet's own HP bar and the departure's teardown are
    /// flushed a hook later, in <c>AfterDamageReceived</c>, exactly as
    /// <c>FlushFanfareDeltaBlock</c> already defers the shipped kit's Block.
    /// </summary>
    public StageAbsorb Absorb(int incoming)
    {
        if (incoming <= 0 || Lead is not { } lead)
        {
            return new StageAbsorb(0, incoming < 0 ? 0 : incoming, null);
        }

        var absorbed = lead.Fanfare < incoming ? lead.Fanfare : incoming;
        lead.Fanfare -= absorbed;
        var reached = incoming - absorbed;
        if (lead.Fanfare > 0) return new StageAbsorb(absorbed, reached, null);

        _seats.RemoveAt(0);
        Note(new StageBeat("leave", lead.Who, -1, 0, absorbed, "hit"));
        return new StageAbsorb(
            absorbed, reached,
            new StageExit(lead.Who, StageDeparture.Struck));
    }

    /// <summary>
    /// RULE 4. The LEAD regains <see cref="FurinaStageLaw.LeadRegen"/> at the
    /// start of Furina's turn, from her SECOND turn on. Only the lead; bars
    /// have no cap.
    ///
    /// THE TURN NUMBER IS THE ARGUMENT rather than a counter of its own, for
    /// <c>FurinaReframeOpening</c>'s reason one arm over: the seat's
    /// <c>PlayerCombatState.TurnNumber</c> is per-PLAYER, so a co-op partner's
    /// turn cannot pay hers, and an extra first turn cannot pay twice.
    ///
    /// WHY NOT TURN ONE. The relic opens the fight with Usher at
    /// <see cref="FurinaStageLaw.OpeningFanfare"/> (rule 2). A regen on turn
    /// one would make that opening a 4 the relic never printed.
    /// </summary>
    public int Regen(int turnNumber)
    {
        // "FROM HER SECOND TURN ON" IS A RULE AND NOT A CONSTANT, which is how
        // the sim states it too (`furina_stage.turn_start_regen`: `if not
        // active(p) or state.turn < 2`). There is no `REGEN_FROM_TURN` in
        // `furina_stage`, so a constant here would be a number this side of
        // the wire invented -- exactly what `lint_constant_parity` exists to
        // refuse -- and the two engines would state one rule two ways.
        if (turnNumber < 2) return 0;
        if (Lead is not { } lead) return 0;
        lead.Fanfare += FurinaStageLaw.LeadRegen;
        return FurinaStageLaw.LeadRegen;
    }

    /// <summary>
    /// The relic's opening (rule 2), and the ONE entry that is not a summon:
    /// Usher takes the FRONT seat at <see cref="FurinaStageLaw.OpeningFanfare"/>
    /// rather than the back-most empty one at 1. It is idempotent on a
    /// non-empty stage, so a relic and a kit install that both make the
    /// sentence true cost one list check between them -- the belt
    /// <c>TamakushiCasket</c> wears for the same reason.
    /// </summary>
    public StageSeat? OpenWith(StagePerformer who)
    {
        if (!IsEmpty) return null;
        var seat = new StageSeat(who, FurinaStageLaw.OpeningFanfare);
        _seats.Add(seat);
        Note(new StageBeat("arrive", who, 0, FurinaStageLaw.OpeningFanfare,
                           0, ""));
        return seat;
    }

    /// <summary>The seat this performer is sitting in, or null. What the three
    /// NAMED summon Commons ask before fielding a second copy: "Summon Usher.
    /// If he is already on stage, Raise 3 on him instead."</summary>
    public StageSeat? SeatOf(StagePerformer who) =>
        _seats.FirstOrDefault(s => s.Who == who);

    /// <summary>
    /// The named summons' second clause, and the ONE Raise in the kit that
    /// does not go to the back seat -- it raises HIM, wherever he is sitting,
    /// which is why the face says so.
    ///
    /// A METHOD HERE rather than a caller writing <c>seat.Fanfare += n</c>,
    /// because the ledger is the only writer of a bar: that is what makes the
    /// pet mirror safe (this class's header) and what keeps every bar move
    /// inside one file a pin can read.
    /// </summary>
    public int RaiseSeat(StageSeat seat, int amount)
    {
        if (amount <= 0) return 0;
        seat.Fanfare += amount;
        return amount;
    }

    /// <summary>
    /// <i>Scene Change</i> (sec.12): the front performer moves to the back
    /// seat, bar and all.
    ///
    /// A PURE REORDER, and the difference from rule 3's rotation is the whole
    /// card: a rotation happens because somebody ARRIVED and the front had to
    /// go, so a body leaves; this moves the same bodies around the same seats.
    /// No bow, no act, nothing lost, nobody summoned.
    /// </summary>
    public void SceneChange()
    {
        if (_seats.Count == 0) return;
        var front = _seats[0];
        _seats.RemoveAt(0);
        _seats.Add(front);
        Note(new StageBeat("rotate", front.Who, _seats.Count - 1,
                           front.Fanfare, 0, ""));
    }

    // ---- the per-play spend record -----------------------------------
    //
    // WHY A RECORD AND NOT A LIVE READ: by the time <i>Final Bow</i>'s Block
    // or <i>Let the People Rejoice</i>'s damage resolves, the bar it is
    // measuring is GONE -- the card emptied it a statement earlier. So what
    // the payoff multiplies is what this play TOOK, written here as it is
    // taken. `FurinaDrain.Amount` is the same shape one arm over.

    /// <summary>What this play has taken off the bars so far.</summary>
    public int SpentThisPlay { get; private set; }

    /// <summary>A fresh, empty record for one card play.</summary>
    public void BeginPlay() => SpentThisPlay = 0;

    /// <summary>
    /// <i>Let the People Rejoice</i>, first clause: "Spend all Fanfare on
    /// stage." Empties every bar and REMEMBERS who was standing, because the
    /// same card's third clause brings them back -- and the printed order puts
    /// the card's own area damage between the two, so the bows cannot happen
    /// here (<see cref="TakePendingCurtainCall"/>).
    /// </summary>
    public int CollectAll()
    {
        var total = _seats.Sum(s => s.Fanfare);
        _pendingCurtainCall = _seats.Select(s => s.Who).ToList();
        foreach (var seat in _seats)
        {
            Note(new StageBeat("leave", seat.Who, -1, 0, seat.Fanfare,
                               "spend"));
        }
        _seats.Clear();
        SpentThisPlay = total;
        return total;
    }

    /// <summary>Who <see cref="CollectAll"/> left waiting, taken once. Empty
    /// at every moment no card is mid-Rejoice.</summary>
    public IReadOnlyList<StagePerformer> TakePendingCurtainCall()
    {
        var company = _pendingCurtainCall;
        _pendingCurtainCall = new List<StagePerformer>();
        return company;
    }

    private List<StagePerformer> _pendingCurtainCall = new();

    /// <summary>
    /// <i>Final Bow</i>: the lead leaves AND BOWS, with no Spend to earn it.
    /// The one card that grants a bow outright -- rule 9 buys a bow with a
    /// Spend, and this face pays for it with a card and an Exhaust instead.
    /// <paramref name="bar"/> is what it left with, which is the Block the
    /// card gains.
    /// </summary>
    public StageExit? FinalBow(out int bar)
    {
        bar = 0;
        if (Lead is not { } lead) return null;
        bar = lead.Fanfare;
        _seats.RemoveAt(0);
        SpentThisPlay = bar;
        Note(new StageBeat("leave", lead.Who, -1, 0, bar, "final_bow"));
        return new StageExit(lead.Who, StageDeparture.Spent);
    }

    /// <summary>Test and teardown seam: the stage is empty at the end of a
    /// combat because pets live one combat (rule 1). The combat-identity check
    /// in <see cref="For"/> is what does this in a real run.</summary>
    public void Clear()
    {
        _seats.Clear();
        _pendingCurtainCall.Clear();
        _beats.Clear();
        SpentThisPlay = 0;
    }

    /// <summary>
    /// `EB-735`. THE WIRE'S VIEW OF THE STAGE.
    ///
    /// WHAT THE SEATS SAW, which was nothing (round one, sec.2): "one
    /// anonymous pool with three names". The bridge publishes pets and the
    /// page draws Kokomi's one; Furina's three had no renderer, so three seats
    /// played some 550 actions without ever knowing who was on stage or what a
    /// bar held, and every finding in that round is read through the hole.
    ///
    /// A PLAIN DICTIONARY OF PRIMITIVES, and the shape is
    /// <see cref="FurinaReframeLedger.Snapshot"/>'s for the reason that one is:
    /// the bridge (<c>vendor/STS2_MCP/gits/GitsFurinaStage.cs</c>) reaches it
    /// by REFLECTION, because this file is Compile Remove'd from a release
    /// build and a compile-time reference would make the bridge refuse to load
    /// without it. The field names here ARE the contract, and
    /// <c>understudy/blindplay_board.furina_stage</c> reads them.
    ///
    /// THREE STATES, NOT TWO, the same split every other GItS block on this
    /// wire makes: an ABSENT key is "no Stage in this build", an EMPTY map is
    /// "the rule is here and this seat is not playing it" (a Klee, a Kokomi, a
    /// flag-off Furina), and a populated map is her stage -- populated even
    /// with nobody standing, because "the stage is empty" is the fact a seat
    /// spending a rider most needs and the one an absent key cannot state.
    ///
    /// THE SEAT INDEX IS EMITTED rather than left to the list's order, even
    /// though the list IS in seat order. The page prints the lead by name and
    /// the row's own acceptance is "three named bars in seat order"; a reader
    /// reconstructing the seat from an array index has to be told, somewhere,
    /// that the array is ordered -- and this is that somewhere, said once, in
    /// the data.
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
        snapshot["seats"] = ledger.Seats
            .Select((seat, index) => (object?)new Dictionary<string, object?>
            {
                ["member"] = FurinaStage.Name(seat.Who),
                ["name"] = DisplayName(seat.Who),
                ["seat"] = index,
                ["fanfare"] = seat.Fanfare,
                // The body's combat id, so the page's block and the `pets`
                // list on the same wire name one creature rather than two
                // things that happen to agree.
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
                ["fanfare"] = beat.Fanfare,
                ["moved"] = beat.Moved,
                ["reason"] = beat.Reason,
            })
            .ToList();
        return snapshot;
    }

    /// <summary>The name a performer prints, off the body's own model rather
    /// than a second table: <c>UsherMonster.DisplayName</c> is what the pet's
    /// health bar is labelled with in game, and the page must not name the
    /// same creature differently.</summary>
    public static string DisplayName(StagePerformer who) => who switch
    {
        StagePerformer.Chevalmarin => "Surintendante Chevalmarin",
        StagePerformer.Crabaletta => "Mademoiselle Crabaletta",
        _ => "Gentilhomme Usher",
    };
}
