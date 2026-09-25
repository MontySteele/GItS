using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE FURINA STAGE SWITCH, C# side, and the arm that REPLACES the reframe.
///
/// The design is <c>review/active/furina-stage-brief-2026-09-08.md</c> --
/// sec.3 is the rules, sec.10 the defaults it discloses, and every number in
/// <see cref="FurinaStageLaw"/> is one of that section's. Nothing here was
/// decided on this side of the wire; where the brief left a number to the sim
/// it is marked as such on the constant.
///
/// TWO SWITCHES, NOT ONE, exactly as the four arms before it arrange
/// themselves and for their reasons:
///
///   * <c>-p:PrototypeCards=true</c> (defines <c>PROTOTYPE_CARDS</c>) is the
///     QUARANTINE. It compiles <c>Powers/Prototype/**</c>, <c>Cards/Prototype/**</c>
///     and <c>Vfx/Prototype/**</c>, so a release build contains no type from
///     this arm at all and every seam that calls in from a shipped file is
///     itself inside <c>#if PROTOTYPE_CARDS</c>.
///   * <c>-p:FurinaStage=true</c> (defines <c>FURINA_STAGE</c>) is the ARM. It
///     moves ONE default, <see cref="Enabled"/>. The rules compile either way,
///     because the headless pins have to exercise the rules AND assert the
///     flag-off wiring in one build -- the argument
///     <c>KleeTests.csproj</c> already makes for <c>PROTOTYPE_CARDS</c>.
///
/// ONE FLAG, NOT FIVE, and the difference from the retired reframe is
/// the shape of the thing being switched. The reframe was four independent
/// edits to a shipped engine, so each leg had to be settable on its own to
/// pin "this rule moved and the other three did not". The stage is not an edit
/// to anything: with the flag off there is no stage, no performer, no relic
/// and no card, and every seam below is one early return. A per-leg flag would
/// describe a state no board can be in.
///
/// WHAT THE ARM MOVES, exhaustively. Every seam is one <c>if</c> on
/// <see cref="LiveFor"/>:
///
///   * <c>Furina.StartingRelics</c> -- Salon Solitaire replaces the Ethereal
///     Spotlight (brief sec.3 rule 2).
///   * <c>Furina.StartingDeck</c> -- the two kit slots become three: Salon
///     Debut, Curtain Rise, Rising Applause (sec.7's named starter).
///   * <c>FurinaResourceHooks.ModifyHpLostBeforeOsty</c> -- the damage order,
///     sec.3 rule 6. The one seam that touches a SHIPPED file's behaviour, and
///     it returns the shipped number with the arm off.
///   * <c>FurinaStageHooks</c> -- the lead's regen at her turn start (rule 4)
///     and the performers' acts at her turn end (rule 10), an arm-only
///     listener that does nothing on a board with no stage.
///
/// FURINA'S OWN HP IS TOUCHED BY NOTHING HERE (sec.3 rule 11), and that is
/// worth stating as a property of the code and not only of the design: no path
/// in this arm heals, drains or caps her bar. What the arm adds is three bars
/// that are not hers.
///
/// AND IT IS ALSO THE VERB SURFACE THE GENERATED CARDS CALL, which is the
/// `EB-723` / `EB-725` reconciliation. The sim's leg wrote a <c>FurinaStage</c>
/// of its own -- a seat list plus the card verbs, "written so the generated
/// cards compile", with no pet, no damage-order hook and no strip -- and its
/// own header said to absorb or replace it. This is that absorption: the SEATS
/// are <see cref="FurinaStageLedger"/>'s, which is the one seat model and the
/// only writer of a bar, and every verb below is the sim leg's signature
/// re-implemented over it. So <c>FurinaStage.Summon(...)</c> in a generated
/// card and <c>FurinaStageLedger.For(...).Summon(...)</c> in a pin are two
/// doors into one rule rather than two rules that agree today.
///
/// EVERY VERB SYNCS THE BODIES, and that is why the sync is inside the verb
/// rather than at its call sites: there are seventeen call sites and the
/// codegen writes them. A generated card that summons gets the pet, the
/// seat-ordered line and the strip redraw without knowing any of them exist.
///
/// THE NUMBERS ARE <see cref="FurinaStageLaw"/>'s -- the sim leg's own file,
/// kept whole, because <c>tools/lint_constant_parity.py</c> mirrors it by
/// value against <c>tier0/engine/furina_stage.py</c>. This branch's own copy
/// of the eleven is DELETED rather than reconciled: two declarations of one
/// number is exactly the drift that gate exists to refuse.
///
/// THE REFRAME IS GONE (`EB-726`, R269). It was built beside this arm rather
/// than in place of it so that `EB-725` stayed reviewable; once the Stage had
/// its seat rounds the brief's sec.2 retirement was taken whole, and this is
/// the only Furina arm in the tree.
/// </summary>
public static class FurinaStage
{
    /// <summary>
    /// The arm's default: <c>-p:FurinaStage=true</c> turns it on, and a
    /// release package never passes it.
    /// </summary>
    public const bool DefaultEnabled =
#if FURINA_STAGE
        true;
#else
        false;
#endif

    /// <summary>The master, and the only flag. Settable so one build can pin
    /// both sides of it.</summary>
    public static bool Enabled { get; set; } = DefaultEnabled;

    /// <summary>
    /// Is the stage live for THIS creature? Identity is
    /// <see cref="FurinaResources.IsFurina"/>, which is what
    /// <c>tools/lint_prototype_patch_scope.py</c> requires of anything running
    /// on every seat at the table under the one prototype switch: in co-op the
    /// other seat is not hers and must not grow a stage.
    /// </summary>
    /// <remarks>`EB-727`: this used to carry its own null test in front of
    /// the identity read, because <c>FurinaResources.IsFurina</c>
    /// dereferenced its argument and threw for a caller with no creature.
    /// The predicate answers for the absent case itself now, so the local
    /// guard is gone rather than duplicated here.</remarks>
    public static bool LiveFor(Creature? creature) =>
        Enabled && FurinaResources.IsFurina(creature);

    // ==================================================================
    // THE VERB SURFACE. Every member below carries the sim leg's signature,
    // so the seventeen generated `proto_fs_` cards call it unchanged; every
    // BODY is the ledger's move, then the payout, then the body sync.
    // ==================================================================

    /// <summary>The three, in the order the brief prints them. STRINGS at this
    /// boundary because the sheet and the codegen speak strings
    /// (<c>gen_klee_cards.FURINA_STAGE_MEMBERS</c>); the enum is what the
    /// rules use, and <see cref="Parse"/> is the one crossing.</summary>
    public static readonly string[] Performers =
        { "usher", "chevalmarin", "crabaletta" };

    /// <summary>A sheet name to a performer. An unknown name reads as Usher
    /// rather than throwing, because the codegen already refuses an unknown
    /// member at EMIT -- <c>FURINA_STAGE_MEMBERS</c> is a closed set checked
    /// there -- so a miss here cannot come from a row, and a card mid-play is
    /// the wrong place to discover a typo the build should have caught.
    /// </summary>
    public static StagePerformer Parse(string member) => member switch
    {
        "chevalmarin" => StagePerformer.Chevalmarin,
        "crabaletta" => StagePerformer.Crabaletta,
        _ => StagePerformer.Usher,
    };

    /// <summary>A performer to its sheet name.</summary>
    public static string Name(StagePerformer who) =>
        who.ToString().ToLowerInvariant();

    /// <summary>The seats, front first. Never null: an absent stage is an
    /// empty one, which every rule here already answers for.</summary>
    public static IReadOnlyList<StageSeat> Of(Creature? owner) =>
        owner == null
            ? System.Array.Empty<StageSeat>()
            : FurinaStageLedger.For(owner).Seats;

    public static StageSeat? Lead(Creature? owner) =>
        owner == null ? null : FurinaStageLedger.For(owner).Lead;

    public static StageSeat? Back(Creature? owner) =>
        owner == null ? null : FurinaStageLedger.For(owner).Back;

    public static int LeadFanfare(Creature? owner) => Lead(owner)?.Fanfare ?? 0;

    public static int BackFanfare(Creature? owner) => Back(owner)?.Fanfare ?? 0;

    /// <summary>Is anybody on stage? The `stage_occupied` predicate.</summary>
    public static bool Occupied(Creature? owner) => Of(owner).Count > 0;

    /// <summary>
    /// R276 pick 1, and the gate every Spend mode asks: can the BACK performer
    /// pay <paramref name="amount"/> IN FULL? False on an empty stage and on a
    /// bar short of the price, and in both cases the chooser does not offer the
    /// Spend mode and the card plays its base mode.
    /// </summary>
    public static bool CanSpend(Creature? owner, int amount) =>
        LiveFor(owner) && FurinaStageLedger.For(owner!).CanSpend(amount);

    /// <summary>The live lead bar, for the `stage_lead_fanfare` count
    /// (<i>Pneuma Refrain</i>, the shield reader).</summary>
    public static int LeadFanfare(CardModel? card) =>
        LeadFanfare(card?.Owner?.Creature);

    /// <summary>The live back bar, for `stage_back_fanfare` (<i>Ousia
    /// Surge</i>, the bank reader).</summary>
    public static int BackFanfare(CardModel? card) =>
        BackFanfare(card?.Owner?.Creature);

    /// <summary>R276 batch two: how many performers are on stage, for the
    /// `stage_count` count (<i>Ensemble Piece</i>).</summary>
    public static int Count(CardModel? card) =>
        Of(card?.Owner?.Creature).Count;

    /// <summary>A fresh, empty per-play spend record.</summary>
    public static void BeginPlay(Creature? owner)
    {
        if (owner != null) FurinaStageLedger.For(owner).BeginPlay();
    }

    /// <summary>Close the per-play spend record. Round three's stale forecast
    /// is what this exists for -- see <see cref="FurinaStageLedger.EndPlay"/>.
    /// </summary>
    public static void EndPlay(Creature? owner)
    {
        if (owner != null) FurinaStageLedger.For(owner).EndPlay();
    }

    /// <summary>What THIS play took off the bars, for the `stage_spent` count.
    /// A per-play record and not a live read, for the reason the sim leg
    /// gives: by the time <i>Final Bow</i>'s Block or the Rare's damage
    /// resolves, the bar it is measuring is gone.</summary>
    public static int Spent(CardModel? card) =>
        card?.Owner?.Creature is { } owner
            ? FurinaStageLedger.For(owner).SpentThisPlay
            : 0;

    /// <summary>The whole company's bars added up -- <i>Let the People
    /// Rejoice</i>'s number, before it takes it.</summary>
    public static int TotalFanfare(Creature? owner)
    {
        var total = 0;
        foreach (var seat in Of(owner)) total += seat.Fanfare;
        return total;
    }

    /// <summary>
    /// `EB-747`. WHAT <i>FINAL BOW</i> PRINTS, IN PREVIEW AND AT RESOLUTION.
    ///
    /// THE FIND (round two, sec.4). "<i>Ousia Surge</i> dealt 0 on an empty
    /// stage at full cost with no refusal ... the readers print a rule where a
    /// number is known." Two of the four readers could not print one at all,
    /// because <see cref="Spent"/> is a per-PLAY record and is 0 until the
    /// card has already emptied the bar it is measuring -- the very reason
    /// that record exists (<c>FurinaStageLedger.SpentThisPlay</c>).
    ///
    /// SO THE READER ANSWERS THE SAME QUESTION AT TWO MOMENTS. Before the
    /// play, nothing has been spent and the number the card is ABOUT to take
    /// is the back performer's live bar (R276: the bow comes from the bank); during the play, the bar is gone and what the
    /// card took is the record. One expression, so the previewed number and
    /// the resolved number cannot differ -- which is what a CalculatedVar is
    /// for.
    ///
    /// IT NEEDS <see cref="BeginPlay"/> TO BE CALLED, and until this row it
    /// was not: the record was written by each spending op and never reset, so
    /// a stale amount from an earlier card would have been previewed as this
    /// card's forecast. `FurinaStageHooks.BeforeCardPlayed` clears it now.
    ///
    /// 0 ON AN EMPTY STAGE, in both moments, which is the row's own
    /// acceptance.
    /// </summary>
    public static int SpentOrBackFanfare(CardModel? card)
    {
        var spent = Spent(card);
        return spent > 0 ? spent : BackFanfare(card);
    }

    /// <summary>`EB-747`, <i>Let the People Rejoice</i>'s half of the same
    /// rule: the whole stage's bars before the card takes them, and what it
    /// took after.</summary>
    public static int SpentOrTotalFanfare(CardModel? card)
    {
        var spent = Spent(card);
        return spent > 0 ? spent : TotalFanfare(card?.Owner?.Creature);
    }

    /// <summary>Rule 2, the relic's opening. Idempotent on a lit stage.
    /// </summary>
    public static async Task OpenCombat(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        await InstallBadge(owner);
        if (FurinaStageLedger.For(owner!).OpenWith(StagePerformer.Usher) == null)
        {
            return;
        }
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// THE STAGE BADGE on Furina (<see cref="StageSummaryPower"/>, 2026-09-25):
    /// the board's rules where a player hovers first. Idempotent, and asked
    /// from two places -- the relic's combat open and every turn start
    /// (<c>FurinaStageHooks</c>) -- for <c>KokomiRules.Install</c>'s reason: a
    /// fight whose setup order ever moves still gets the badge.
    /// </summary>
    public static async Task InstallBadge(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        if (owner!.Powers.OfType<StageSummaryPower>().Any()) return;
        await PowerCmd.Apply<StageSummaryPower>(
            new ThrowingPlayerChoiceContext(), owner, 1,
            applier: owner, cardSource: null, silent: true);
    }

    /// <summary>
    /// Rule 3. Fill the back-most empty seat at
    /// <see cref="FurinaStageLaw.SummonFanfare"/>; on a FULL stage rotate, the
    /// front leaving with no bow and the newcomer taking its bar.
    ///
    /// <para><paramref name="ifPresentRaise"/> is the three named Commons'
    /// second clause -- "Summon Usher. If he is already on stage, Raise 3 on
    /// him instead" -- and it is the ONE Raise in the kit that does not go to
    /// the back seat, which is why it is written on the face.</para>
    ///
    /// <para><paramref name="member"/> of <c>"random"</c> rolls one who is not
    /// on stage. ON A FULL STAGE the lead takes a Bow and moves to the back
    /// seat keeping its Fanfare (<see cref="RecastFromFront"/>, 2026-09-25):
    /// before that rule a random summon with all three seated summoned
    /// nobody, and a first-time player read the card as doing nothing.</para>
    ///
    /// <para>AND THE NEWCOMER DOES NOT ACT ON ARRIVAL (`EB-738`, round one's
    /// one E default). Rule 3 reads "a newcomer performs with the others at
    /// the end of that turn, never on arrival", and this side had read the
    /// draft's older wording as an act on play: three seats watched every
    /// summon deal damage and apply Hydro with nothing on its face, and a
    /// summon turn performed twice. There is no code for the rule and that
    /// absence IS the rule -- <see cref="EndOfTurnActs"/> walks whoever is on
    /// stage when it fires, so a performer summoned during the turn is
    /// standing there once. It stays awaited because the bodies are.</para>
    /// </summary>
    public static async Task Summon(PlayerChoiceContext choiceContext,
                                    Creature? owner, string member,
                                    int ifPresentRaise = 0)
    {
        if (!LiveFor(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);

        StagePerformer who;
        if (member == "random")
        {
            if (ledger.IsFull)
            {
                await RecastFromFront(choiceContext, owner!);
                return;
            }
            if (RollFree(owner!, ledger) is not { } rolled) return;
            who = rolled;
        }
        else
        {
            who = Parse(member);
            if (ledger.SeatOf(who) is { } already)
            {
                if (ifPresentRaise > 0)
                {
                    ledger.RaiseSeat(already, ifPresentRaise);
                    FurinaStagePets.SyncBars(owner);
                    Vfx.FurinaStageStrip.Refresh(owner);
                }
                return;
            }
        }

        ledger.Summon(who);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// A RANDOM SUMMON ON A FULL STAGE (2026-09-25). [USER]'s words: "treat
    /// this like a Defect orb summon? the stage members rotate, ... bows, and
    /// their remaining fanfare transfers to the newest member" -- and the seat
    /// that leaves is the LEAD. So:
    ///
    ///   1. the lead takes a Bow and leaves, and the other two step forward
    ///      (<see cref="FurinaStageLedger.BowFromFront"/>);
    ///   2. the Bow is a real one: its departure effect fires, and so does
    ///      every Bow reader -- Thunderous Applause draws and Raises -- but
    ///      A FIVE-CENTURY ACT DOES NOT RETURN IT (<c>mayReturn: false</c>),
    ///      because the summon is already bringing it back;
    ///   3. the newcomer enters the back seat holding the lead's remaining
    ///      Fanfare (<see cref="FurinaStageLedger.RecastToBack"/>). Three
    ///      performers stand in three seats, so the one free to arrive is the
    ///      one who just bowed: in play the lead takes its Bow and moves to
    ///      the back seat, keeping its Fanfare, and keeps its body too.
    ///
    /// THE ORDER IS BOW, THEN READERS, THEN ARRIVAL -- <see cref="AfterBow"/>'s
    /// own order ("applause then return") -- so Thunderous Applause's Raise
    /// lands on the stage of two the bow left, on the performer who is then
    /// the back one, and the returning performer arrives after it holding
    /// exactly the bar it left with.
    ///
    /// IT DOES NOT ACT ON ARRIVAL (`EB-738` stands): it acts once at the end
    /// of the turn with everyone else. <i>Double Casting</i> on a full stage
    /// runs this twice, so two performers bow.
    /// </summary>
    private static async Task RecastFromFront(
        PlayerChoiceContext choiceContext, Creature owner)
    {
        var ledger = FurinaStageLedger.For(owner);
        if (ledger.BowFromFront() is not { } leaver) return;
        await Bow(choiceContext, owner,
                  new StageExit(leaver.Who, StageDeparture.Spent),
                  mayReturn: false);
        ledger.RecastToBack(leaver);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary><i>Scene Change</i>: the front performer moves to the back
    /// seat, bar and all. A pure reorder -- no bow, no act, nothing lost.
    /// </summary>
    public static void SceneChange(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).SceneChange();
        FurinaStagePlacement.Reflow(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>A random performer who is not on stage, or null with all
    /// three seated; on an empty stage, any of the three. One roll for the
    /// random summons and the empty-stage Raise.</summary>
    private static StagePerformer? RollFree(Creature owner,
                                            FurinaStageLedger ledger)
    {
        var seated = ledger.Company.ToHashSet();
        var free = Performers.Select(Parse)
            .Where(p => !seated.Contains(p)).ToList();
        if (free.Count == 0) return null;
        var roll = owner.Player?.RunState.Rng.CombatTargets;
        return roll != null ? roll.NextItem(free) : free[0];
    }

    /// <summary>
    /// ROUND FOUR: RAISE ON AN EMPTY STAGE SUMMONS. Asked first by every
    /// Raise verb below, so the rule is one door whichever seat a face names:
    /// with nobody on stage, a random performer arrives holding
    /// <paramref name="amount"/> and nothing else is raised (Gala Dinner on an
    /// empty stage fields ONE performer at 3). True when it summoned, and the
    /// caller then returns without raising. The arrival performs at the end of
    /// the turn with the others, never on arrival (rule 3, `EB-738`).
    /// </summary>
    private static async Task<bool> SummonForRaise(Creature owner, int amount)
    {
        var ledger = FurinaStageLedger.For(owner);
        if (amount <= 0 || !ledger.IsEmpty) return false;
        if (RollFree(owner, ledger) is not { } who) return false;
        if (ledger.SummonOnEmpty(who, amount) == null) return false;
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
        return true;
    }

    /// <summary>Rule 5. Raise lands on the back-most performer, which is the
    /// lead when it is alone; on an empty stage it summons (round four).
    /// Returns what landed.</summary>
    public static async Task<int> Raise(Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        if (await SummonForRaise(owner!, amount)) return amount;
        var raised = FurinaStageLedger.For(owner!).Raise(amount);
        if (raised > 0)
        {
            FurinaStagePets.SyncBars(owner);
            Vfx.FurinaStageStrip.Refresh(owner);
        }
        return raised;
    }

    /// <summary>R276 batch two, <i>Hold Your Places</i>: Raise on the LEAD
    /// performer, the one Raise in the kit that lands on the shield. On an
    /// empty stage it summons (round four).</summary>
    public static async Task<int> RaiseLead(Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        if (await SummonForRaise(owner!, amount)) return amount;
        var raised = FurinaStageLedger.For(owner!).RaiseLead(amount);
        if (raised > 0)
        {
            FurinaStagePets.SyncBars(owner);
            Vfx.FurinaStageStrip.Refresh(owner);
        }
        return raised;
    }

    /// <summary>Arkhe Alignment's Pneuma: "the lead REGAINS N". A regain like
    /// rule 4's and not a Raise, so it does NOT summon on an empty stage --
    /// there is no lead to regain anything (round four; flagged in the PR).
    /// </summary>
    public static int RegainLead(Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        var raised = FurinaStageLedger.For(owner!).RaiseLead(amount, "regain");
        if (raised > 0)
        {
            FurinaStagePets.SyncBars(owner);
            Vfx.FurinaStageStrip.Refresh(owner);
        }
        return raised;
    }

    /// <summary>R276 batch two, <i>Gala Dinner</i>: Raise on EVERY
    /// performer. On an empty stage it summons ONE performer holding the
    /// amount (round four).</summary>
    public static async Task<int> RaiseAll(Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        if (await SummonForRaise(owner!, amount)) return amount;
        var raised = FurinaStageLedger.For(owner!).RaiseAll(amount);
        if (raised > 0)
        {
            FurinaStagePets.SyncBars(owner);
            Vfx.FurinaStageStrip.Refresh(owner);
        }
        return raised;
    }

    /// <summary>R276 batch two, <i>Step Forward</i>: the back performer takes
    /// the front seat -- Scene Change run the other way.</summary>
    public static void StepForward(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        FurinaStageLedger.For(owner!).StepForward();
        FurinaStagePlacement.Reflow(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// R276 batch two, <i>Bravura</i>: spend ALL of the back performer's
    /// Fanfare. The bar is emptied exactly, so the performer takes its Bow.
    /// Returns what was spent (0 on an empty stage), which the card's damage
    /// reads through `stage_spent`.
    /// </summary>
    public static async Task<int> SpendAllOfBack(
        PlayerChoiceContext choiceContext, Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var result = FurinaStageLedger.For(owner!).SpendAllOfBack();
        if (!result.Fired) return 0;
        if (result.Exit is { } exit) await Bow(choiceContext, owner!, exit);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
        return result.Paid;
    }

    /// <summary>
    /// THE CO-OP SET, <i>Share the Spotlight</i>: "Your back performer gives
    /// all its Fanfare to another player as Block, then takes a Bow."
    ///
    /// <see cref="SpendAllOfBack"/>'s move with the payout in the middle: the
    /// bar leaves EXACTLY, so this is an exact emptying and the performer
    /// takes a real Bow -- its departure effect, Thunderous Applause, and A
    /// Five-Century Act's return all fire (<see cref="Bow"/>). The Block lands
    /// FIRST, because the face prints it first. It is the card's Block
    /// (<c>ValueProp.Move</c> with the play attached), the same pipeline Final
    /// Bow's "Block equal to its Fanfare" and the base game's Lift take, so her
    /// Dexterity is what folds into it.
    ///
    /// AN EMPTY STAGE DOES NOTHING, and the card is still playable (the
    /// design's own words). Returns what was given.
    /// </summary>
    public static async Task<int> ShareTheSpotlight(
        PlayerChoiceContext choiceContext, Creature? owner, Creature? ally,
        CardPlay? cardPlay)
    {
        if (!LiveFor(owner)) return 0;
        var result = FurinaStageLedger.For(owner!).SpendAllOfBack();
        if (!result.Fired) return 0;
        if (ally is { IsAlive: true } && result.Paid > 0)
        {
            await CreatureCmd.GainBlock(
                ally, result.Paid, ValueProp.Move, cardPlay);
        }
        if (result.Exit is { } exit) await Bow(choiceContext, owner!, exit);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
        return result.Paid;
    }

    /// <summary>R276 batch two, <i>Tutti!</i>: every performer performs its
    /// act now, front first. The cast is snapshotted, as the end-of-turn
    /// sweep's is. A Five-Century Act's returnee "re-enters without acting
    /// that turn", so a resting performer sits this out too.</summary>
    public static async Task PerformAll(PlayerChoiceContext choiceContext,
                                        Creature? owner)
    {
        if (!LiveFor(owner)) return;
        foreach (var seat in Of(owner).ToList())
        {
            if (owner!.IsDead) return;
            if (seat.Resting) continue;
            await Perform(choiceContext, owner, Name(seat.Who));
        }
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// Rule 6's middle term with <i>A Rapt Audience</i> on it (R276 batch
    /// two). The ledger absorbs as it always has; then, if an ENEMY's hit
    /// took Fanfare off a lead that was not also the back performer, each
    /// Rapt Audience Raises its share of what the lead lost on the back
    /// performer -- half rounded up, or all of it upgraded
    /// (<see cref="RaptAudiencePower"/>'s Amount is the percentage).
    /// Synchronous, for <see cref="FurinaStageLedger.Absorb"/>'s reason; the
    /// bars reach the bodies, and a lead this hit emptied takes its Bow, at
    /// the flush that follows every hit (<see cref="Flush"/>).
    /// </summary>
    public static int AbsorbHit(Creature target, int incoming,
                                Creature? dealer)
    {
        var ledger = FurinaStageLedger.For(target);
        var twoOrMore = ledger.Seats.Count >= 2;
        // 2026-09-25: WHO hit the lead, for the log's hit beat -- title and
        // combat id, the pair `NoteBeat` files for the body an act lands on.
        var result = ledger.Absorb(
            incoming, dealer?.Monster?.Title.ToString() ?? "",
            dealer?.CombatId.ToString() ?? "");
        if (!twoOrMore || result.Absorbed <= 0
            || dealer is not { IsEnemy: true })
        {
            return result.ReachedFurina;
        }
        foreach (var rapt in target.Powers.OfType<RaptAudiencePower>()
                     .ToList())
        {
            var raise = (int)System.Math.Ceiling(
                result.Absorbed * rapt.Amount / 100m);
            ledger.Raise(raise);
        }
        return result.ReachedFurina;
    }

    /// <summary>
    /// WHAT OF A HIT GOT PAST HER BLOCK, AS THE ENGINE WILL COUNT IT
    /// (2026-09-25, the afternoon seat round's Weak off-by-one).
    ///
    /// THE FIND. A Weakened 11 against 6 Block was filed as 3 on Usher where
    /// the seat computed 2. The seat was right. The engine does not round a
    /// modified hit: <c>Hook.ModifyDamage</c> hands back 11 x 0.75 = 8.25,
    /// Block takes 6, and <c>ModifyHpLostBeforeOsty</c> is handed 2.25 -- and
    /// the engine's own <c>Creature.LoseHpInternal</c> then TRUNCATES that
    /// (<c>(int)Math.Clamp(amount, 0, ...)</c>), so without a stage she would
    /// have lost 2. This seam rounded the 2.25 UP, and Usher paid 3.
    ///
    /// SO THE STAGE COUNTS THE HIT THE WAY THE ENGINE DOES: truncated, and
    /// never below 0. A fractional remainder costs the front performer
    /// nothing, as it would have cost Furina nothing.
    /// </summary>
    public static int HpLossThroughBlock(decimal amount) =>
        amount <= 0m ? 0 : (int)System.Math.Floor(amount);

    /// <summary>
    /// 2026-09-25: file the part of an enemy's hit that reached Furina's HP on
    /// the stage log (<see cref="FurinaStageLedger.NoteHitOnFurina"/>), off the
    /// engine's own result for that hit. Called from
    /// <c>AfterDamageReceived</c>, once per hit, BEFORE the flush pays any
    /// Bow that hit earned -- so the log reads the hit on the performer, its
    /// leaving, the part that reached her, then the Bow.
    /// </summary>
    public static void NoteHitOnFurina(Creature target, DamageResult result,
                                       Creature? dealer)
    {
        if (!LiveFor(target) || dealer is not { IsEnemy: true }) return;
        if (!ReferenceEquals(result.Receiver, target)) return;
        FurinaStageLedger.For(target).NoteHitOnFurina(
            result.UnblockedDamage, target.CurrentHp,
            dealer.Monster?.Title.ToString() ?? "",
            dealer.CombatId.ToString());
    }

    /// <summary>
    /// Rule 8's payment leg, for a Spend mode the chooser offered (its gate
    /// asked <see cref="CanSpend"/>). The BACK performer pays the whole price;
    /// if that empties it exactly, it bows (R276 picks 1 and 2).
    ///
    /// <para>Returns what was paid: the price, or 0 where the ledger refused
    /// a bar short of it.</para>
    /// </summary>
    public static async Task<int> Spend(PlayerChoiceContext choiceContext,
                                        Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        var result = FurinaStageLedger.For(owner!).Spend(amount);
        if (!result.Fired) return 0;
        if (result.Exit is { } exit) await Bow(choiceContext, owner!, exit);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
        return result.Paid;
    }

    /// <summary><i>Let the People Rejoice</i>, first clause: "Spend all
    /// Fanfare on stage." Empties every bar, remembers who was standing and
    /// returns the total. THE BOWS ARE <see cref="CurtainCall"/>'s, because
    /// the printed order puts the card's own area damage between them.
    /// </summary>
    public static int CollectAll(Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var total = FurinaStageLedger.For(owner!).CollectAll();
        FurinaStagePlacement.Reflow(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
        return total;
    }

    /// <summary>The same card's third clause: "Every performer takes a bow,
    /// then returns at 1." Two loops because the sentence is two -- every bow
    /// lands on the board the card left, and only then does anybody come back.
    /// </summary>
    public static async Task CurtainCall(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);
        var company = ledger.TakePendingCurtainCall();
        foreach (var who in company)
        {
            // R276 batch two: the card's own "then returns at 1" is the
            // return, so A Five-Century Act does not return them a second
            // time -- a performer returns once.
            await Bow(choiceContext, owner!,
                      new StageExit(who, StageDeparture.Spent),
                      mayReturn: false);
        }
        // "Then returns at 1": to an EMPTY seat, and a returnee that finds
        // none does not return. Round four made that reachable -- Thunderous
        // Applause's Raise between the bows now summons onto the stage this
        // card emptied -- and a return that ROTATED would push that performer
        // off. The sim's `bow_and_return` has always read the clause this way.
        // And never a second copy (2026-09-25): Usher's Bow summons a random
        // performer onto that same empty stage, and one it picked is already
        // back (`FurinaStageLedger.ReturnCompany`).
        ledger.ReturnCompany(company);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary><i>Final Bow</i>: the back performer takes a bow and leaves
    /// (R276: readers draw from the bank). A BOW WITHOUT A SPEND, and the one card that grants one -- rule 9 earns a bow
    /// with a Spend, and this face pays for it with a card and an Exhaust
    /// instead. Returns the bar it left with, which is the Block the card
    /// gains.</summary>
    public static async Task<int> FinalBow(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var exit = FurinaStageLedger.For(owner!).FinalBow(out var bar);
        if (exit == null) return 0;
        await Bow(choiceContext, owner!, exit.Value);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
        return bar;
    }

    /// <summary>Rule 4's move. The TURN TEST is inside, on the seat's own
    /// <c>PlayerCombatState.TurnNumber</c> -- per player, so a co-op partner's
    /// turn cannot pay hers, and an extra first turn cannot pay twice.
    /// </summary>
    public static async Task RegenLead(Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var turn = owner!.Player?.PlayerCombatState?.TurnNumber ?? 0;
        if (FurinaStageLedger.For(owner).Regen(turn) <= 0) return;
        FurinaStagePets.SyncBars(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>Rule 10: one performer's flat act, from any seat, reading no
    /// bar. ONE implementation and two callers -- the end-of-turn sweep and
    /// <i>Bis!</i> -- so an act cannot mean two things. A newcomer's arrival
    /// was the third until `EB-738` removed it.</summary>
    public static async Task Perform(PlayerChoiceContext choiceContext,
                                     Creature? owner, string member)
    {
        if (!LiveFor(owner)) return;
        // `EB-735`, and `EB-511`'s lesson: the beat files WHAT THE BOARD LOST,
        // measured across the act, and never the clause's own printed figure.
        // Crabaletta prints 5 and a Vulnerable makes it 7; a receipt quoting
        // the 5 sends a reader looking for two damage nothing accounts for.
        var before = Ledger(owner);
        Creature? hit = null;
        // R276 batch two, ARKHE ALIGNMENT: this turn's doubling of the acts'
        // printed numbers (Ousia the damage, Pneuma the Block). 1 and 1 on
        // every turn nobody chose.
        var stage = FurinaStageLedger.For(owner!);
        var dmg = stage.ActDamageMultiplier;
        var blk = stage.ActBlockMultiplier;
        var each = -1;
        switch (Parse(member))
        {
            case StagePerformer.Usher:
                await CreatureCmd.GainBlock(
                    owner!, FurinaStageLaw.ActUsherBlock * blk,
                    ValueProp.Unpowered, null, fast: true);
                break;
            case StagePerformer.Chevalmarin:
                // Round four: what EACH enemy lost, so the page prints "2 to
                // every enemy" and not the total of four hits as one number.
                var targets = Enemies(owner!).ToList();
                var hpBefore = targets.Select(e => e.CurrentHp).ToList();
                foreach (var enemy in targets)
                {
                    await ElementalHit.Deal(
                        choiceContext, enemy, Elements.Element.Hydro,
                        FurinaStageLaw.ActChevalmarinDamage * dmg, owner,
                        powered: false);
                }
                each = EvenLoss(hpBefore,
                                targets.Select(e => e.CurrentHp).ToList());
                break;
            case StagePerformer.Crabaletta:
                if (RandomEnemy(owner!) is { } target)
                {
                    // `EB-743`: WHICH body, because Crabaletta picks its own.
                    // Held before the hit lands so a killing act still names
                    // what it killed -- the retired reframe's rule one arm
                    // over, and the reason the mod sends a title at all.
                    hit = target;
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.ActCrabalettaDamage * dmg, owner,
                        powered: false);
                }
                break;
        }
        NoteBeat(owner!, "act", Parse(member), before, hit, each);
    }

    /// <summary>Round four: the one loss every enemy took, or -1 where there
    /// were none or they differ (a Vulnerable, a kill). Measured, as every
    /// beat's number is (`EB-511`); the page prints the total on a -1.
    /// </summary>
    public static int EvenLoss(IReadOnlyList<int> before,
                               IReadOnlyList<int> after)
    {
        if (before.Count == 0 || before.Count != after.Count) return -1;
        var first = before[0] - after[0];
        for (var i = 1; i < before.Count; i++)
        {
            if (before[i] - after[i] != first) return -1;
        }
        return first;
    }

    /// <summary><i>Bis!</i>: the lead performer performs its act now.
    /// </summary>
    public static async Task PerformLead(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        // A resting returnee does not act this turn (R276 batch two).
        if (Lead(owner) is { Resting: false } lead)
        {
            await Perform(choiceContext, owner, Name(lead.Who));
        }
    }

    /// <summary>Rule 10's sweep at the end of Furina's turn: EACH performer
    /// performs, in seat order, front first. The company is snapshotted so a
    /// cast that changes mid-sweep cannot skip or double an act.</summary>
    public static async Task EndOfTurnActs(PlayerChoiceContext choiceContext,
                                           Creature? owner)
    {
        if (!LiveFor(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);
        // R276 batch two, FULL HOUSE: with all three seats filled each
        // performer acts once more per copy (its Amount), every repeat
        // resolving in full before the next performer's.
        var times = 1 + (ledger.IsFull ? FullHouseActs(owner!) : 0);
        foreach (var seat in Of(owner).ToList())
        {
            // A Five-Century Act's returnee re-enters without acting.
            if (seat.Resting) continue;
            for (var i = 0; i < times; i++)
            {
                if (owner!.IsDead) return;
                await Perform(choiceContext, owner, Name(seat.Who));
            }
        }
        ledger.EndRest();
        ledger.ResetActMultipliers();
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// What the end-of-turn sweep will give her in Block, forecast off the
    /// same rules the sweep runs: every Usher not resting acts
    /// <see cref="FurinaStageLaw.ActUsherBlock"/> times this turn's Arkhe
    /// multiple, once plus Full House's extra acts on a full stage. The seat
    /// page prints it as "after the acts" (the wire's `act_block`).
    /// </summary>
    public static int ForecastActBlock(Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var ledger = FurinaStageLedger.For(owner!);
        var times = 1 + (ledger.IsFull ? FullHouseActs(owner!) : 0);
        var ushers = ledger.Seats.Count(
            s => s.Who == StagePerformer.Usher && !s.Resting);
        return ushers * FurinaStageLaw.ActUsherBlock
               * ledger.ActBlockMultiplier * times;
    }

    /// <summary>Full House's extra acts: the sum of its stacks.</summary>
    private static int FullHouseActs(Creature owner) =>
        (int)owner.Powers.OfType<FullHousePower>().Sum(p => p.Amount);

    /// <summary>
    /// Rule 9, the curtain call: performed ONCE by a performer that reached 0
    /// Fanfare, whatever emptied it -- a Spend, a hit (paid at
    /// <see cref="Flush"/>, after the hit), or a summon on a full stage. It
    /// takes the EXIT rather than the performer so a rotation cannot be
    /// mistaken for a departure at a call site --
    /// <see cref="StageExit.Bows"/> is the ledger's own read of rule 7, and a
    /// departure that earned no bow returns here without paying.
    /// </summary>
    public static async Task Bow(PlayerChoiceContext choiceContext,
                                 Creature owner, StageExit exit,
                                 bool mayReturn = true)
    {
        if (!exit.Bows || !LiveFor(owner)) return;
        var before = Ledger(owner);
        Creature? hit = null;
        switch (exit.Who)
        {
            case StagePerformer.Usher:
                // 2026-09-25: Fanfare to the FRONT performer, not Block to
                // Furina -- a hit made him bow on the enemy's turn and the
                // Block expired unused. He has already left, so the front is
                // whoever stands there now, and on the stage he emptied the
                // Raise summons a random performer holding it (round four's
                // rule, the door Thunderous Applause uses). The bow beat is
                // filed FIRST so the log reads the bow, then the gain it paid.
                NoteBeat(owner, "bow", exit.Who, before);
                await RaiseLead(owner, FurinaStageLaw.BowUsherFanfare);
                await AfterBow(choiceContext, owner, exit.Who, mayReturn);
                return;
            case StagePerformer.Chevalmarin:
                foreach (var enemy in Enemies(owner))
                {
                    await ElementalHit.ApplyOnly(
                        choiceContext, enemy, Elements.Element.Hydro, owner);
                }
                break;
            case StagePerformer.Crabaletta:
                if (RandomEnemy(owner) is { } target)
                {
                    hit = target;                        // `EB-743`
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.BowCrabalettaDamage, owner,
                        powered: false);
                }
                break;
        }
        NoteBeat(owner, "bow", exit.Who, before, hit);
        await AfterBow(choiceContext, owner, exit.Who, mayReturn);
    }

    /// <summary>
    /// R276 batch two: what a Bow sets off, after the bowing performer has
    /// left and its departure effect has resolved.
    ///
    ///   * <see cref="ThunderousApplausePower"/>, each copy: draw 1 card and
    ///     Raise its Amount on the back performer (round four: on an empty
    ///     stage the Raise summons a random performer holding it).
    ///   * <see cref="FiveCenturyActPower"/>, any number of copies: the
    ///     performer returns to the back-most empty seat at 1 and rests
    ///     through this turn's acts. Once -- and not at all from <i>Let the
    ///     People Rejoice</i>, whose own return is the return.
    ///
    /// THE ORDER IS APPLAUSE THEN RETURN, so the applause's Raise lands on the
    /// stage the bow left; a returnee arrives after it at 1.
    /// </summary>
    private static async Task AfterBow(PlayerChoiceContext choiceContext,
                                       Creature owner, StagePerformer who,
                                       bool mayReturn)
    {
        foreach (var applause in owner.Powers
                     .OfType<ThunderousApplausePower>().ToList())
        {
            if (owner.Player is { } player)
            {
                await CardPileCmd.Draw(choiceContext, 1m, player);
            }
            // Round four: on the empty stage a bow can leave, this Raise
            // summons a random performer holding the amount.
            await Raise(owner, (int)applause.Amount);
        }
        if (mayReturn && owner.Powers.OfType<FiveCenturyActPower>().Any()
            && FurinaStageLedger.For(owner).ReturnToBack(who))
        {
            await FurinaStagePets.Sync(owner);
            Vfx.FurinaStageStrip.Refresh(owner);
        }
    }

    /// <summary>Furina's Block and the board's total HP, as one pair, taken
    /// either side of an act or a bow. The DIFFERENCE is what the beat files
    /// (`EB-735`): a payout that gains Block files the Block, one that deals
    /// damage files the HP the board actually lost, and one that does neither
    /// -- Chevalmarin's bow, which only leaves an aura -- files 0 and the page
    /// prints no number for it.</summary>
    private static (int Block, int EnemyHp) Ledger(Creature? owner)
    {
        if (owner == null) return (0, 0);
        var hp = Enemies(owner).Sum(e => e.CurrentHp);
        return (owner.Block, hp);
    }

    /// <summary>File one act or bow, with what the board actually did.
    /// The LEDGER is the one writer of the log, exactly as it is the one
    /// writer of a bar; this is the door for the two beats whose number lives
    /// on the board rather than in it.</summary>
    private static void NoteBeat(Creature owner, string what,
                                 StagePerformer who,
                                 (int Block, int EnemyHp) before,
                                 Creature? hit = null, int each = -1)
    {
        var after = Ledger(owner);
        var moved = (after.Block - before.Block)
                    + (before.EnemyHp - after.EnemyHp);
        var ledger = FurinaStageLedger.For(owner);
        var seat = ledger.SeatIndexOf(who);
        ledger.Note(new StageBeat(
            what, who, seat,
            seat >= 0 ? ledger.Seats[seat].Fanfare : 0,
            moved < 0 ? 0 : moved, "",
            // `EB-743`. WHO IT LANDED ON, for the one act and the one bow that
            // pick a body. Title AND combat id, the retired ledger's pair
            // one arm over: the id is the handle the page names a live body
            // by, and the title is the fallback for one this beat KILLED,
            // which is off the next board entirely.
            hit?.Monster?.Title.ToString() ?? "",
            hit?.CombatId.ToString() ?? "",
            each));
    }

    /// <summary>
    /// Rule 6's flush: the ledger moved synchronously inside
    /// <c>ModifyHpLostBeforeOsty</c> because the engine wanted a number back,
    /// and this is where the bodies catch up.
    ///
    /// AND WHERE A HIT'S BOW IS PAID (rule 7, 2026-09-25: "Stage members bow
    /// out when they are destroyed or replaced, not just when you deliberately
    /// spend them down to 0"). The engine calls <c>AfterDamageReceived</c>
    /// once per hit, inside <c>CreatureCmd.Damage</c>, after that hit's HP
    /// loss and before <c>AttackCommand</c> deals the next hit. So the bow
    /// lands BETWEEN the hits of a multi-hit attack: it cannot soften the hit
    /// that emptied the performer, and the performer Usher's Fanfare lands
    /// on meets the next one.
    /// The bow is the same <see cref="Bow"/> a Spend takes, readers and A
    /// Five-Century Act's return included.
    ///
    /// NO BOW FOR A DEAD FURINA OR A FINISHED COMBAT. The engine skips
    /// <c>AfterDamageReceived</c> for a target the hit killed, so a hit that
    /// killed Furina never reaches here for her; the check below also covers
    /// a flush reached through a Guest of Honor ally, and the hit that ended
    /// the fight. What is owed is dropped rather than kept for later.
    /// </summary>
    public static async Task Flush(PlayerChoiceContext choiceContext,
                                   Creature? owner)
    {
        if (owner != null && LiveFor(owner))
        {
            var owed = FurinaStageLedger.For(owner).TakePendingHitBows();
            if (!owner.IsDead && !CombatOver())
            {
                foreach (var exit in owed)
                {
                    if (owner.IsDead || CombatOver()) break;
                    await Bow(choiceContext, owner, exit);
                }
            }
        }
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>The engine's own "skip this effect" test: combat is over, or
    /// ending because every primary enemy or every player is down.</summary>
    private static bool CombatOver() =>
        MegaCrit.Sts2.Core.Combat.CombatManager.Instance.IsOverOrEnding;

    private static IEnumerable<Creature> Enemies(Creature owner) =>
        owner.CombatState?.HittableEnemies.ToList()
        ?? Enumerable.Empty<Creature>();

    private static Creature? RandomEnemy(Creature owner)
    {
        var targets = Enemies(owner).ToList();
        if (targets.Count == 0) return null;
        var rng = owner.Player?.RunState.Rng.CombatTargets;
        return rng == null ? targets[0] : rng.NextItem(targets);
    }
}

/// <summary>
/// THE THREE PERFORMERS. Genshin's Salon Solitaire summons Surintendante
/// Chevalmarin, Mademoiselle Crabaletta and the Gentilhomme Usher; the brief's
/// sec.2 table keeps the three and gives each an act and a bow.
///
/// A NEW ENUM RATHER THAN <c>SalonMember</c>, which spells the same three
/// names one arm over. They are different things wearing one cast list: a
/// <c>SalonMember</c> is a POWER on Furina with a tick value and an Encore
/// price, a performer here is a PET with a bar. Sharing the enum would have
/// made every reader of either arm ask which rule a value carried, and the two
/// arms' rules contradict each other on every clause.
/// </summary>
public enum StagePerformer
{
    Usher,
    Chevalmarin,
    Crabaletta,
}
