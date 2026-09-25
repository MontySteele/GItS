using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>Why a performer left the stage. Since 2026-09-25 every performer
/// at 0 Fanfare bows (rule 7), so only a rotation leaves without one.
/// </summary>
public enum StageDeparture
{
    /// <summary>Rotated off the front to make room (rule 3). No bow: the
    /// performer still holds its Fanfare, so it never reached 0.</summary>
    Rotated,

    /// <summary>Emptied by an enemy's hit (rule 7). BOWS since 2026-09-25
    /// ([USER]: "Stage members bow out when they are destroyed or replaced,
    /// not just when you deliberately spend them down to 0"). The bow is paid
    /// after the hit is dealt (<see cref="FurinaStageLedger.TakePendingHitBows"/>),
    /// so it never softens the hit that caused it.</summary>
    Struck,

    /// <summary>Emptied by Spend, Final Bow, Let the People Rejoice or a
    /// full-stage summon (rule 7). Bows (rule 9).</summary>
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

    public bool Bows => Cause != StageDeparture.Rotated;
}

/// <summary>What a Spend did. <see cref="Fired"/> is the rider's own question
/// -- R276: a rider fires only when the back performer can pay the whole
/// price, and never on an empty stage.</summary>
public readonly struct StageSpend
{
    public StageSpend(bool fired, int paid, StageExit? exit)
    {
        Fired = fired;
        Paid = paid;
        Exit = exit;
    }

    public bool Fired { get; }

    /// <summary>What the back performer paid: the whole ask when the rider
    /// fired, 0 when it did not.</summary>
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

    /// <summary>
    /// R276 batch two, <i>A Five-Century Act</i>: a performer that took its
    /// Bow and came straight back "re-enters without acting that turn". True
    /// from that return until the end-of-turn sweep has passed it by
    /// (<see cref="FurinaStage.EndOfTurnActs"/> skips a resting seat and then
    /// clears the flag). Nothing else sets it.
    /// </summary>
    public bool Resting { get; internal set; }
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
/// this file's method names -- and, since 2026-09-25, `raise`, `regain` and
/// `hit`: a bar going up, and an attack the lead absorbed (whose DEALER rides
/// in <paramref name="Target"/> / <paramref name="TargetId"/>).</param>
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
/// <param name="Target">`EB-743`. WHOSE BODY, for the one act and the one bow
/// that pick one: Crabaletta's. The game's printed title, empty on every beat
/// that aims at nobody or at everybody -- the page's line for Chevalmarin
/// says "every enemy" out of the performer's identity and needs no field for
/// it.</param>
/// <param name="TargetId">The same body's `Creature.CombatId`. THE ID IS THE
/// HANDLE AND THE TITLE IS THE FALLBACK, `KokomiPlan.MovedOn`'s split
/// verbatim: the page names a live body with its own numbered name and one
/// this beat KILLED with the title recorded here, since a dead body is off
/// the next board entirely.</param>
/// <param name="Each">Round four: WHAT EACH ENEMY LOST, for the one act that
/// hits every enemy (Chevalmarin's). A seat read "8 across every enemy" as
/// one 8 when it was 2 to each of four. Filled only where every enemy lost
/// the same amount, measured as <paramref name="Moved"/> is; -1 on every other
/// beat and on an uneven sweep, where the page falls back to the total.</param>
/// <param name="Hp">2026-09-25: FURINA'S HP AFTER the one beat that is about
/// her rather than a performer, <see cref="FurinaStageLedger.HitFurinaEvent"/>
/// -- the part of an enemy's hit that got past her Block and the front
/// performer's bar. -1 on every other beat.</param>
public readonly record struct StageBeat(
    string Event, StagePerformer Who, int Seat, int Fanfare, int Moved,
    string Reason, string Target = "", string TargetId = "", int Each = -1,
    int Hp = -1);


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
/// 3-bar lead and land 3 on her, does a 3x2 flurry leave her whole, is a
/// Spend 3 from a 1-bar back performer refused.
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
/// PER FURINA AND PER COMBAT, keyed the way
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

    /// <summary>The event name of <see cref="NoteHitOnFurina"/>'s beat.
    /// </summary>
    public const string HitFurinaEvent = "hit_furina";

    /// <summary>
    /// 2026-09-25 (the afternoon seat round). THE PART OF A HIT THAT REACHED
    /// HER. The log filed every hit on a performer and none on Furina, so
    /// both seats misjudged how much of an attack got through: "the stage log
    /// lists hits on performers only, never hits on Furina, so every HP loss
    /// I had to infer". This beat is the last step of the damage order --
    /// her Block, then the front performer's bar, then her HP -- filed with
    /// what her HP actually lost (<paramref name="lost"/>) and where it ended
    /// (<paramref name="hpAfter"/>), and the dealer the way a performer's
    /// hit beat names it. Nothing filed for a hit that took no HP.
    ///
    /// <see cref="StageBeat.Who"/> carries no meaning on this beat (the
    /// wire's view prints Furina); it is Usher only because the field has no
    /// empty value.
    /// </summary>
    public void NoteHitOnFurina(int lost, int hpAfter, string dealer = "",
                                string dealerId = "")
    {
        if (lost <= 0) return;
        Note(new StageBeat(HitFurinaEvent, StagePerformer.Usher, -1, 0, lost,
                           "", dealer, dealerId, -1, hpAfter));
    }

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

    /// <summary>The front performer, the SHIELD: the one that absorbs
    /// (rule 6) and the one that regenerates (rule 4).</summary>
    public StageSeat? Lead => _seats.Count > 0 ? _seats[0] : null;

    /// <summary>The back-most performer, the BANK: where a Raise lands
    /// (rule 5) and what Spend and the readers draw from (rule 8, R276). The
    /// LEAD when it is alone.</summary>
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
    /// A RANDOM SUMMON ON A FULL STAGE, first half: the LEAD takes a Bow and
    /// leaves, and the other two step forward. Returns the leaving seat --
    /// bar, body and all -- for <see cref="RecastToBack"/> to put back, or
    /// null (and nothing moves) on a stage that is not full.
    ///
    /// THE RULE, 2026-09-25, in [USER]'s words: "treat this like a Defect orb
    /// summon? the stage members rotate, ... bows, and their remaining
    /// fanfare transfers to the newest member", and asked which seat leaves,
    /// the lead. It replaces rule 3's full-stage rotation (the front leaving
    /// WITHOUT a bow) for the random summons, and it was filed off a
    /// first-time co-op player's "if the stage is full, then summoning a new
    /// actor doesn't do anything": a random summon had no one free to roll.
    ///
    /// THE BAR IS NOT SPENT. The leave beat files the bar the performer walks
    /// off with as <see cref="StageBeat.Moved"/>, and the seat object keeps
    /// it, because the newcomer takes it (<see cref="RecastToBack"/>).
    /// </summary>
    public StageSeat? BowFromFront()
    {
        if (!IsFull || Lead is not { } lead) return null;
        _seats.RemoveAt(0);
        Note(new StageBeat("leave", lead.Who, -1, 0, lead.Fanfare, "recast"));
        return lead;
    }

    /// <summary>
    /// A RANDOM SUMMON ON A FULL STAGE, second half: the newcomer enters the
    /// BACK seat holding the leaver's remaining Fanfare.
    ///
    /// THE NEWCOMER IS THE LEAVER, and the method says so by taking the
    /// leaving SEAT rather than a performer. Three performers stand in three
    /// seats, so on a full stage the only one free to arrive is the one who
    /// just bowed: in play the lead takes its Bow and moves to the back seat,
    /// keeping its Fanfare. Handing the same seat back keeps the same BODY,
    /// so <c>FurinaStagePets.Sync</c> moves a performer rather than killing
    /// one and fielding its twin.
    ///
    /// IT DOES NOT ACT ON ARRIVAL (`EB-738` stands) and it is not resting: it
    /// acts once at the end of the turn like everyone else.
    ///
    /// False (and nothing moves) if a seat is no longer free, which nothing
    /// between the two halves can cause today: the Bow's readers Raise on a
    /// stage of two and summon nobody.
    /// </summary>
    public bool RecastToBack(StageSeat seat)
    {
        if (IsFull) return false;
        seat.Resting = false;
        _seats.Add(seat);
        Note(new StageBeat("arrive", seat.Who, _seats.Count - 1, seat.Fanfare,
                           0, ""));
        return true;
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
        NoteRaise(seat, amount);
        return amount;
    }

    /// <summary>
    /// 2026-09-25 (opus-furina-l2b, (c) 4). EVERY BAR THAT GOES UP IS A BEAT.
    /// The page printed "Nothing this page can count landed off it" under
    /// Rising Applause and filed nothing on the stage log, so the seat read
    /// every Raise off the stage line and did the arithmetic itself. The beat
    /// carries what landed (<see cref="StageBeat.Moved"/>) and the bar after
    /// it (<see cref="StageBeat.Fanfare"/>), and the page prints "a -> b"
    /// from the two. <paramref name="what"/> is <c>raise</c>, or
    /// <c>regain</c> for rule 4's regen and Pneuma, which are not Raises.
    /// </summary>
    private void NoteRaise(StageSeat seat, int amount, string what = "raise")
    {
        Note(new StageBeat(what, seat.Who, _seats.IndexOf(seat),
                           seat.Fanfare, amount, ""));
    }

    /// <summary>
    /// ROUND FOUR: RAISE ON AN EMPTY STAGE SUMMONS. When a Raise finds nobody
    /// on stage, a performer arrives HOLDING THE RAISE AMOUNT -- not rule 3's
    /// 1 -- and nothing else is raised. It is the same for every Raise,
    /// whichever seat the face names (the back, the lead, every performer),
    /// and for the Raise powers; <paramref name="who"/> is the caller's random
    /// roll, since an empty stage leaves all three free.
    ///
    /// THE LEDGER HALF ONLY. <see cref="Raise"/>, <see cref="RaiseLead"/> and
    /// <see cref="RaiseAll"/> stay "0 on an empty stage", because two callers
    /// must not summon: Arkhe Alignment's Pneuma prints "the lead REGAINS",
    /// which presumes a lead, and A Rapt Audience can never meet an empty
    /// stage. The summoning door is <see cref="FurinaStage.Raise"/> and its two
    /// siblings, which ask this first.
    ///
    /// Returns the seat, or null (and nothing moves) on an occupied stage or a
    /// Raise of nothing.
    /// </summary>
    public StageSeat? SummonOnEmpty(StagePerformer who, int amount)
    {
        if (amount <= 0 || !IsEmpty) return null;
        var seat = new StageSeat(who, amount);
        _seats.Add(seat);
        Note(new StageBeat("arrive", who, 0, amount, 0, ""));
        return seat;
    }

    /// <summary>
    /// RULE 8, as R276 ruled it (picks 1 and 2). Spend N pays from the BACK
    /// performer -- the bank, the seat a Raise fills -- and only IN FULL:
    ///
    ///   * enough on the bar: pays N, the rider fires, the performer stays;
    ///   * EXACTLY enough: pays N, the rider fires, and the emptied performer
    ///     leaves with a BOW (rule 7 second clause, rule 9);
    ///   * NOT enough, or an empty stage: the rider CANNOT fire, nothing is
    ///     paid, and the card plays at its base number. The chooser never
    ///     offers the mode on such a board (<see cref="CanSpend"/>), so this
    ///     branch is the ledger's own refusal rather than a path a play takes.
    ///
    /// THE BACK AND NOT THE LEAD. Three rounds found the bank a player builds
    /// with Raise was never the bar Spend took from; the lead is the shield
    /// (rule 6) and the back is the bank. With one performer on stage it is
    /// both, and the list's last seat is its first.
    /// </summary>
    public StageSpend Spend(int amount)
    {
        if (Back is not { } back) return new StageSpend(false, 0, null);
        if (amount <= 0) return new StageSpend(true, 0, null);
        if (back.Fanfare < amount) return new StageSpend(false, 0, null);

        back.Fanfare -= amount;
        // The per-play record, written where the payment happens rather than
        // by the caller: `stage_spent` is what a payoff on the SAME card
        // multiplies, and by the time it resolves the bar is gone.
        SpentThisPlay = amount;
        if (back.Fanfare > 0) return new StageSpend(true, amount, null);

        _seats.RemoveAt(_seats.Count - 1);
        Note(new StageBeat("leave", back.Who, -1, 0, amount, "spend"));
        return new StageSpend(
            true, amount, new StageExit(back.Who, StageDeparture.Spent));
    }

    /// <summary>R276 pick 1: can the back performer pay N IN FULL? The one
    /// question a Spend mode's gate asks, and false on an empty stage.
    /// </summary>
    public bool CanSpend(int amount) =>
        Back is { } back && back.Fanfare >= amount;

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
    /// A LEAD EMPTIED HERE BOWS, AFTER THE HIT (rule 7, 2026-09-25). This
    /// method runs inside the engine's damage modifier, before the hit has
    /// been dealt, and a bow is awaited work -- so the exit is QUEUED here and
    /// paid by <c>FurinaStage.Flush</c> at <c>AfterDamageReceived</c>, which
    /// the engine fires once per hit, after that hit's HP loss and before the
    /// next hit of the same attack. Usher's Fanfare therefore never reduces
    /// the hit that emptied him, and does meet the next one.
    ///
    /// SYNCHRONOUS ON PURPOSE. Its caller is
    /// <c>FurinaResourceHooks.ModifyHpLostBeforeOsty</c>, which the engine
    /// calls per damage instance and which returns a number rather than
    /// awaiting one. The pet's own HP bar and the departure's teardown are
    /// flushed a hook later, in <c>AfterDamageReceived</c>, exactly as
    /// <c>FlushFanfareDeltaBlock</c> already defers the shipped kit's Block.
    /// </summary>
    public StageAbsorb Absorb(int incoming, string dealer = "",
                              string dealerId = "")
    {
        if (incoming <= 0 || Lead is not { } lead)
        {
            return new StageAbsorb(0, incoming < 0 ? 0 : incoming, null);
        }

        var absorbed = lead.Fanfare < incoming ? lead.Fanfare : incoming;
        lead.Fanfare -= absorbed;
        var reached = incoming - absorbed;
        // 2026-09-25 (opus-furina-l2b, (c) 4). THE HIT ITSELF IS A BEAT, and
        // not only the departure it may cause. The log filed a `leave` when a
        // hit emptied the lead and nothing when it merely drained it, so the
        // seat reconstructed every Fanfare change across the enemies' turn by
        // arithmetic. Filed BEFORE the leave, which is the order it happened
        // in; `Target` / `TargetId` name the DEALER here, the handle-and-title
        // pair the act beats use for the body they hit.
        if (absorbed > 0)
        {
            Note(new StageBeat("hit", lead.Who, 0, lead.Fanfare, absorbed, "",
                               dealer, dealerId));
        }
        if (lead.Fanfare > 0) return new StageAbsorb(absorbed, reached, null);

        _seats.RemoveAt(0);
        Note(new StageBeat("leave", lead.Who, -1, 0, absorbed, "hit"));
        var exit = new StageExit(lead.Who, StageDeparture.Struck);
        _pendingHitBows.Add(exit);
        return new StageAbsorb(absorbed, reached, exit);
    }

    private readonly List<StageExit> _pendingHitBows = new();

    /// <summary>The bows owed by hits since the last flush, oldest first, taken
    /// once (rule 7, 2026-09-25). <c>FurinaStage.Flush</c> pays them after
    /// the hit is dealt, or drops them when that hit killed Furina or ended
    /// the combat. Usually one; an attack on Furina and a Guest of Honor ally
    /// in the same damage call can leave two.</summary>
    public IReadOnlyList<StageExit> TakePendingHitBows()
    {
        if (_pendingHitBows.Count == 0) return System.Array.Empty<StageExit>();
        var owed = _pendingHitBows.ToList();
        _pendingHitBows.Clear();
        return owed;
    }

    /// <summary>
    /// RULE 4. The LEAD regains <see cref="FurinaStageLaw.LeadRegen"/> at the
    /// start of Furina's turn, from her SECOND turn on. Only the lead; bars
    /// have no cap.
    ///
    /// THE TURN NUMBER IS THE ARGUMENT rather than a counter of its own, for
    /// the retired reframe's opening grant's reason: the seat's
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
        NoteRaise(lead, FurinaStageLaw.LeadRegen, "regain");
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
        NoteRaise(seat, amount);
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

    // ---- R276 batch two ----------------------------------------------

    /// <summary>
    /// <i>Step Forward</i>: the BACK performer moves to the front seat, bar
    /// and all, and the others shift back one seat -- Scene Change run the
    /// other way. With one performer on stage nothing moves.
    /// </summary>
    public void StepForward()
    {
        if (_seats.Count < 2) return;
        var back = _seats[^1];
        _seats.RemoveAt(_seats.Count - 1);
        _seats.Insert(0, back);
        Note(new StageBeat("rotate", back.Who, 0, back.Fanfare, 0, ""));
    }

    /// <summary><i>Hold Your Places</i>: Raise N on the LEAD performer, the
    /// shield -- the one card that raises the front seat. Returns what landed
    /// (0 on an empty stage).</summary>
    public int RaiseLead(int amount, string what = "raise")
    {
        if (amount <= 0 || Lead is not { } lead) return 0;
        lead.Fanfare += amount;
        NoteRaise(lead, amount, what);
        return amount;
    }

    /// <summary><i>Gala Dinner</i>: Raise N on EVERY performer. Returns the
    /// total that landed.</summary>
    public int RaiseAll(int amount)
    {
        if (amount <= 0) return 0;
        foreach (var seat in _seats)
        {
            seat.Fanfare += amount;
            NoteRaise(seat, amount);
        }
        return amount * _seats.Count;
    }

    /// <summary>
    /// <i>Bravura</i>: spend ALL of the back performer's Fanfare. The bar is
    /// emptied exactly, so the performer always leaves with a Bow (rule 9).
    /// On an empty stage nothing is spent and the card deals 0.
    /// </summary>
    public StageSpend SpendAllOfBack()
    {
        if (Back is not { } back) return new StageSpend(false, 0, null);
        var paid = back.Fanfare;
        back.Fanfare = 0;
        SpentThisPlay = paid;
        _seats.RemoveAt(_seats.Count - 1);
        Note(new StageBeat("leave", back.Who, -1, 0, paid, "spend"));
        return new StageSpend(
            true, paid, new StageExit(back.Who, StageDeparture.Spent));
    }

    /// <summary>
    /// <i>A Five-Century Act</i>: a performer that took its Bow returns to
    /// the back-most empty seat at <see cref="FurinaStageLaw.SummonFanfare"/>
    /// and RESTS -- it does not act at the end of this turn. False (and
    /// nothing moves) on a full stage.
    /// </summary>
    public bool ReturnToBack(StagePerformer who)
    {
        if (IsFull) return false;
        _seats.Add(new StageSeat(who, FurinaStageLaw.SummonFanfare)
        {
            Resting = true,
        });
        Note(new StageBeat("arrive", who, _seats.Count - 1,
                           FurinaStageLaw.SummonFanfare, 0, ""));
        return true;
    }

    /// <summary>
    /// <i>Arkhe Alignment</i>'s two halves: this turn's multipliers on the
    /// performers' act DAMAGE (Ousia) and act BLOCK (Pneuma). 1 is "no
    /// Alignment this turn"; the one choice a turn sets its half to 1 plus
    /// the copy count (one copy x2, two x3). Reset at the end of her turn,
    /// after the sweep they are for.
    /// </summary>
    public int ActDamageMultiplier { get; set; } = 1;

    /// <inheritdoc cref="ActDamageMultiplier"/>
    public int ActBlockMultiplier { get; set; } = 1;

    /// <summary>The end of the turn the multipliers were for.</summary>
    public void ResetActMultipliers()
    {
        ActDamageMultiplier = 1;
        ActBlockMultiplier = 1;
    }

    /// <summary>A resting performer has sat out one sweep and is a performer
    /// like any other again.</summary>
    public void EndRest()
    {
        foreach (var seat in _seats) seat.Resting = false;
    }

    /// <summary>The event name of <see cref="Fade"/>'s beat.</summary>
    public const string FadeEvent = "fade";

    /// <summary>
    /// RULE 12, THE APPLAUSE FADES (draft 3, 2026-09-25). At the end of
    /// Furina's turn, AFTER the acts, each performer behind the front (the
    /// middle and back seats) loses <see cref="FurinaStageLaw.FadeLoss"/> of
    /// its bar: half of its Fanfare above
    /// <see cref="FurinaStageLaw.FadeThreshold"/>, rounded down. The front
    /// never fades, so a lone performer never does; the loss never takes a
    /// bar below the threshold, so it never empties a performer and never
    /// causes a Bow. [USER] ruled out a flat halving ("taking away half from
    /// the back means it's hard to build up fanfare").
    ///
    /// One beat per performer that lost Fanfare, carrying the loss
    /// (<see cref="StageBeat.Moved"/>) and the bar after it, so the seat page
    /// prints "The applause fades: Chevalmarin 9 → 7". Returns the total lost.
    /// Sim twin: <c>furina_stage.fade</c>.
    /// </summary>
    public int Fade()
    {
        var total = 0;
        for (var i = 1; i < _seats.Count; i++)
        {
            var seat = _seats[i];
            var loss = FurinaStageLaw.FadeLoss(seat.Fanfare);
            if (loss <= 0) continue;
            seat.Fanfare -= loss;
            total += loss;
            Note(new StageBeat(FadeEvent, seat.Who, i, seat.Fanfare, loss, ""));
        }
        return total;
    }

    // ---- the per-play spend record -----------------------------------
    //
    // WHY A RECORD AND NOT A LIVE READ: by the time <i>Final Bow</i>'s Block
    // or <i>Let the People Rejoice</i>'s damage resolves, the bar it is
    // measuring is GONE -- the card emptied it a statement earlier. So what
    // the payoff multiplies is what this play TOOK, written here as it is
    // taken.

    /// <summary>What this play has taken off the bars so far. 0 at every
    /// moment no card is in flight, which is what makes the readers' faces a
    /// FORECAST off the bars rather than a memory of the last spend.</summary>
    public int SpentThisPlay { get; private set; }

    /// <summary>
    /// ROUND THREE'S STALE FORECAST. <i>Let the People Rejoice</i> printed
    /// "Deal 2 damage to ALL" with the stage reading Usher 12 and no Weak: the
    /// 2 was an EARLIER card's spend, still sitting in this record while the
    /// Rare sat in hand. `EB-747` opened the record at
    /// <c>BeforeCardPlayed</c> and never closed it, so between two plays the
    /// forecast read the last play's number instead of the bars.
    ///
    /// SO THE RECORD IS A STACK, which is <c>combat.SAVED_PER_CARD</c>'s shape
    /// one engine over (<c>stage_spent_this_card</c> is saved and restored
    /// around a free play "for its neighbour's reason exactly: a free play that
    /// spent inside an outer card would otherwise hand the outer card its
    /// number"). <see cref="BeginPlay"/> pushes and zeroes,
    /// <see cref="EndPlay"/> pops -- and the OUTERMOST pop lands on 0 rather
    /// than on what it found, because outside a play there is no play to have
    /// spent anything.
    /// </summary>
    private readonly List<int> _spendStack = new();

    /// <summary>A fresh, empty record for one card play.</summary>
    public void BeginPlay()
    {
        _spendStack.Add(SpentThisPlay);
        SpentThisPlay = 0;
    }

    /// <summary>Close the record this play opened: the enclosing play's number
    /// where there is one, and 0 where there is not.</summary>
    public void EndPlay()
    {
        if (_spendStack.Count == 0)
        {
            SpentThisPlay = 0;
            return;
        }
        var enclosing = _spendStack[_spendStack.Count - 1];
        _spendStack.RemoveAt(_spendStack.Count - 1);
        SpentThisPlay = _spendStack.Count == 0 ? 0 : enclosing;
    }

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

    /// <summary>
    /// <i>Let the People Rejoice</i>'s "then return with 1", after the bows:
    /// each member of the company, in seat order, takes the back-most EMPTY
    /// seat at <see cref="FurinaStageLaw.SummonFanfare"/>. A member finds no
    /// seat when the stage is full, and does not come back a SECOND time when
    /// it is already standing (2026-09-25: Usher's Bow, or a Thunderous
    /// Applause Raise, summons a random performer onto the stage the card
    /// emptied, and the one it picks may be a member of the company). So the
    /// stage never holds two of the same performer after the card. Returns
    /// how many came back.
    /// </summary>
    public int ReturnCompany(IEnumerable<StagePerformer> company)
    {
        var back = 0;
        foreach (var who in company)
        {
            if (IsFull) break;
            if (SeatOf(who) != null) continue;
            Summon(who);
            back++;
        }
        return back;
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
    /// <i>Final Bow</i>: the BACK performer leaves AND BOWS, with no Spend to
    /// earn it (R276: the readers draw from the bank, as Spend does). The one
    /// card that grants a bow outright -- rule 9 buys a bow with a Spend, and
    /// this face pays for it with a card and an Exhaust instead.
    /// <paramref name="bar"/> is what it left with, which is the Block the
    /// card gains.
    /// </summary>
    public StageExit? FinalBow(out int bar)
    {
        bar = 0;
        if (Back is not { } back) return null;
        bar = back.Fanfare;
        _seats.RemoveAt(_seats.Count - 1);
        SpentThisPlay = bar;
        Note(new StageBeat("leave", back.Who, -1, 0, bar, "final_bow"));
        return new StageExit(back.Who, StageDeparture.Spent);
    }

    /// <summary>Test and teardown seam: the stage is empty at the end of a
    /// combat because pets live one combat (rule 1). The combat-identity check
    /// in <see cref="For"/> is what does this in a real run.</summary>
    public void Clear()
    {
        ResetActMultipliers();
        _seats.Clear();
        _pendingCurtainCall.Clear();
        _pendingHitBows.Clear();
        _beats.Clear();
        _spendStack.Clear();
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
    /// <c>KokomiPlan.Snapshot</c>'s for the reason that one is:
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
        // R276 batch two: the Block the end-of-turn acts will give, with this
        // turn's Arkhe multiple and Full House's extra acts in it -- the page's
        // "after the acts" line reads this rather than assuming 3 per Usher.
        snapshot["act_block"] = FurinaStage.ForecastActBlock(creature);
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
                // 2026-09-25: the hit beat that is about HER, not a performer.
                ["member"] = beat.Event == HitFurinaEvent
                    ? "furina" : FurinaStage.Name(beat.Who),
                ["name"] = beat.Event == HitFurinaEvent
                    ? "Furina" : DisplayName(beat.Who),
                ["seat"] = beat.Seat,
                ["fanfare"] = beat.Fanfare,
                ["moved"] = beat.Moved,
                ["reason"] = beat.Reason,
                // `EB-743`: who a Crabaletta act or bow landed on. Empty
                // strings on every other beat, which the page reads as "this
                // beat named no body".
                ["target"] = beat.Target,
                ["target_id"] = beat.TargetId,
                // Round four: the per-enemy figure of Chevalmarin's act, -1
                // where there is none (see `StageBeat.Each`).
                ["each"] = beat.Each,
                // 2026-09-25: her HP after a hit that reached her; -1 on
                // every other beat (see `StageBeat.Hp`).
                ["hp"] = beat.Hp,
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
