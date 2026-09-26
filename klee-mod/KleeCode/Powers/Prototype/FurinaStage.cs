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
public static partial class FurinaStage
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
        "neuvillette" => StagePerformer.Neuvillette,
        "clorinde" => StagePerformer.Clorinde,
        "navia" => StagePerformer.Navia,
        "chevreuse" => StagePerformer.Chevreuse,
        "wriothesley" => StagePerformer.Wriothesley,
        "sigewinne" => StagePerformer.Sigewinne,
        "charlotte" => StagePerformer.Charlotte,
        "lynette" => StagePerformer.Lynette,
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
    /// <see cref="FurinaStageLaw.SummonFanfare"/>; on a FULL stage recast
    /// (<see cref="RecastFromFront"/>): the front Bows and leaves, and the
    /// newcomer takes the back seat holding its Fanfare. Named and random
    /// alike since the trio can be cloned (2026-09-25): a named summon used to
    /// rotate the front off with no Bow, which [USER]'s "Stage members bow
    /// out when they are destroyed or replaced" had already ruled out.
    ///
    /// <para>THE TRIO CAN BE CLONED (2026-09-25; [USER]: "Let's allow for
    /// copies and then check the balance."). A named summon always summons,
    /// even when that performer is already on stage -- the old "if he's
    /// already on stage, he gains 3 Fanfare" clause is gone from the faces and
    /// from here.</para>
    ///
    /// <para><paramref name="member"/> of <c>"random"</c> rolls uniformly
    /// from all three of the trio (<see cref="RollAny"/>), on stage or not.
    /// ON A FULL STAGE the lead takes a Bow and leaves, and the roll arrives
    /// at the back holding its Fanfare (<see cref="RecastFromFront"/>,
    /// 2026-09-25): before that rule a random summon with all three seated
    /// summoned nobody, and a first-time player read the card as doing
    /// nothing.</para>
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
                                    Creature? owner, string member)
    {
        if (!LiveFor(owner)) return;
        var ledger = FurinaStageLedger.For(owner!);

        var random = member == "random";
        if (ledger.IsFull)
        {
            await RecastFromFront(choiceContext, owner!,
                                  random ? null : Parse(member));
            return;
        }
        var who = random ? RollAny(owner!) : Parse(member);
        if (random) NoteSummoned(who);

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
    ///      because the summon is filling the seat it would return to;
    ///   3. the newcomer -- a uniform roll over the trio since the trio can be
    ///      cloned (2026-09-25) -- enters the back seat holding the lead's
    ///      remaining Fanfare. Where the roll lands on the performer who just
    ///      bowed, the same seat goes back (<see cref="FurinaStageLedger.RecastToBack"/>)
    ///      and keeps its body; otherwise a new body arrives
    ///      (<see cref="FurinaStageLedger.ArriveAtBack"/>).
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
    /// <remarks>THE RECAST ADDS (2026-09-25, the Guest Cast's review): the
    /// newcomer arrives holding its OWN arrival Fanfare
    /// (<paramref name="arrival"/>: 1 for the trio, a Guest Star's N) plus
    /// the leaver's remaining Fanfare. Otherwise a guest cast onto a front
    /// at 1 would arrive unable to pay.</remarks>
    private static async Task RecastFromFront(
        PlayerChoiceContext choiceContext, Creature owner,
        StagePerformer? named = null,
        int arrival = FurinaStageLaw.SummonFanfare)
    {
        var ledger = FurinaStageLedger.For(owner);
        if (ledger.BowFromFront() is not { } leaver) return;
        var who = named ?? RollAny(owner);
        if (named == null) NoteSummoned(who);
        // The leaver bows HOLDING its bar (Navia reads it), which then goes to
        // the newcomer: a recast moves Fanfare, it does not spend it.
        await Bow(choiceContext, owner,
                  new StageExit(leaver.Who, StageDeparture.Spent,
                                leaver.Fanfare, 0, leaver.LostSinceAct),
                  mayReturn: false);
        if (who == leaver.Who)
        {
            ledger.RecastToBack(leaver, arrival);
        }
        else
        {
            ledger.ArriveAtBack(who, leaver.Fanfare + arrival);
        }
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

    /// <summary>
    /// 2026-09-25 evening: WHO A RANDOM SUMMON ROLLED, on the card's own
    /// resolution row. The seat page's "What you played" section printed Take
    /// the Stage, Understudy and Double Casting with no performer, and the
    /// seat had to find the arrival on the stage log. Filed only while a card
    /// is resolving (<see cref="ResolutionLedger.NoteSummon"/>'s rule).
    /// </summary>
    private static void NoteSummoned(StagePerformer who) =>
        ResolutionLedger.NoteSummon(Name(who),
                                    FurinaStageLedger.DisplayName(who));

    /// <summary>A uniform roll over the three of the trio, on stage or not
    /// (2026-09-25: the trio can be cloned; [USER]: "Let's allow for copies
    /// and then check the balance."). One roll for the random summons, the
    /// full-stage recast and the empty-stage Raise.</summary>
    private static StagePerformer RollAny(Creature owner)
    {
        var trio = Performers.Select(Parse).ToList();
        var roll = owner.Player?.RunState.Rng.CombatTargets;
        return roll != null ? roll.NextItem(trio) : trio[0];
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
        var who = RollAny(owner);
        if (ledger.SummonOnEmpty(who, amount) == null) return false;
        NoteSummoned(who);
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
            await Perform(choiceContext, owner, seat);
        }
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// Rule 6's middle term with <i>A Rapt Audience</i> on it (R276 batch
    /// two). The ledger absorbs as it always has; then, if an ENEMY's hit
    /// took Fanfare off a lead that was not also the back performer, each
    /// Rapt Audience Raises its Amount on the back performer: a fixed 2 (3
    /// upgraded) per hit, copies adding (2026-09-26 balance review; it was a
    /// share of what the lead lost, which scaled with the bank).
    /// Synchronous, for <see cref="FurinaStageLedger.Absorb"/>'s reason; the
    /// bars reach the bodies, and a lead this hit emptied takes its Bow, at
    /// the flush that follows every hit (<see cref="Flush"/>).
    /// </summary>
    /// <remarks>2026-09-25 night: a lead this hit empties Bows before the
    /// rest of the hit reaches her, so the Block of that Bow is spent on it
    /// here (<see cref="FurinaStageLedger.Absorb"/>). <paramref name="bowCatches"/>
    /// is false for a hit on another player (Guest of Honor): her Bow Block
    /// is hers, and cannot catch their hit.</remarks>
    public static int AbsorbHit(Creature target, int incoming,
                                Creature? dealer, bool bowCatches = true)
    {
        var ledger = FurinaStageLedger.For(target);
        var twoOrMore = ledger.Seats.Count >= 2;
        var lead = ledger.Lead;
        // 2026-09-25: WHO hit the lead, for the log's hit beat -- title and
        // combat id, the pair `NoteBeat` files for the body an act lands on.
        var result = ledger.Absorb(
            incoming, dealer?.Monster?.Title.ToString() ?? "",
            dealer?.CombatId.ToString() ?? "", bowCatches);
        // What the hit took off the lead, shown on the lead as the base game
        // shows HP loss (the fade's number, below, is the same pop). The body
        // is still standing: a lead this hit emptied leaves at the flush.
        Vfx.FurinaStageLossPop.Show(lead, result.Absorbed);
        if (!twoOrMore || result.Absorbed <= 0
            || dealer is not { IsEnemy: true })
        {
            return result.ReachedFurina;
        }
        foreach (var rapt in target.Powers.OfType<RaptAudiencePower>()
                     .ToList())
        {
            ledger.Raise((int)rapt.Amount);
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
        var exits = ledger.TakePendingCurtainExits();
        var company = exits.Select(exit => exit.Who).ToList();
        foreach (var exit in exits)
        {
            // R276 batch two: the card's own "then returns at 1" is the
            // return, so A Five-Century Act does not return them a second
            // time -- a performer returns once.
            await Bow(choiceContext, owner!, exit, mayReturn: false);
        }
        // "Then returns at 1": to an EMPTY seat, and a returnee that finds
        // none does not return. Round four made that reachable -- Thunderous
        // Applause's Raise between the bows now summons onto the stage this
        // card emptied -- and a return that ROTATED would push that performer
        // off. The sim's `bow_and_return` has always read the clause this way.
        // One of each GUEST (2026-09-25): a guest already back does not
        // return twice (`FurinaStageLedger.ReturnCompany`).
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
    /// bar. ONE implementation for every caller -- the end-of-turn sweep,
    /// <i>Bis!</i>, <i>Tutti!</i> and, since draft 3 (2026-09-25), the
    /// <see cref="Bow"/> -- so an act cannot mean two things.</summary>
    /// <remarks>BY SEAT and not by name since the trio can be cloned
    /// (2026-09-25): two Ushers are two seats, and the beat files the one
    /// that acted.</remarks>
    public static async Task Perform(PlayerChoiceContext choiceContext,
                                     Creature? owner, StageSeat seat)
    {
        if (!LiveFor(owner)) return;
        // A seat that left mid-sweep (a guest's payment emptied it, and it
        // took its Bow) does not also act.
        if (!FurinaStageLedger.For(owner!).Holds(seat)) return;
        await Act(choiceContext, owner!, seat.Who,
                  FurinaStageLedger.ActEvent, seat);
    }

    /// <summary>
    /// The act itself, filed as <paramref name="beat"/>: <c>act</c> from
    /// <see cref="Perform"/>, <c>bow</c> from <see cref="Bow"/>.
    ///
    /// NO ACT CARRIES AN ELEMENT (draft 3, 2026-09-25; [USER]: "removing the
    /// Hydro application from the end-of-turn effects on Chevalmarin and
    /// Crabaletta"). The two damage acts go out through
    /// <see cref="ElementalHit.DealUnelemented"/>, unpowered: no aura set,
    /// none consumed, no reaction, and Furina's Strength and Weak stay out of
    /// it (`EB-495` D3). Sim twin: <c>furina_stage.perform</c>.
    /// </summary>
    private static async Task Act(PlayerChoiceContext choiceContext,
                                  Creature owner, StagePerformer who,
                                  string beat, StageSeat? seat = null,
                                  StageExit? exit = null)
    {
        // THE GUEST CAST (2026-09-25), rule 4: EVERY ACT PAYS, first. The
        // Fanfare half is the ledger's (so the forecast runs the same move);
        // an act that cannot pay does nothing. A Bow is free (rule 5): the
        // ledger is handed no seat and takes no payment. The trio never pay.
        var owed = new List<StageExit>();
        var bowing = seat == null;
        if (!FurinaStageLedger.For(owner).ActFanfare(
                who, bowing ? null : seat, exit, owed))
        {
            Vfx.FurinaStageStrip.Refresh(owner);
            return;
        }
        if (IsGuest(who))
        {
            await GuestAct(choiceContext, owner, who, beat, seat, exit);
            await BowTheOwed(choiceContext, owner, owed);
            return;
        }
        // `EB-735`, and `EB-511`'s lesson: the beat files WHAT THE BOARD LOST,
        // measured across the act, and never the clause's own printed figure.
        // Crabaletta prints 5 and a Vulnerable makes it 7; a receipt quoting
        // the 5 sends a reader looking for two damage nothing accounts for.
        var before = Ledger(owner);
        Creature? hit = null;
        // R276 batch two, ARKHE ALIGNMENT: this turn's doubling of the acts'
        // printed numbers (Ousia the damage, Pneuma the Block). 1 and 1 on
        // every turn nobody chose.
        var stage = FurinaStageLedger.For(owner);
        var dmg = stage.ActDamageMultiplier;
        var blk = stage.ActBlockMultiplier;
        var each = -1;
        var struck = -1;
        var shot = HitShot.None;
        // 2026-09-25 night: a hit's Bow whose Block the rest of that hit
        // already spent (`StageExit.Caught`) gains only what is left of it.
        var caught = exit?.Caught ?? 0;
        switch (who)
        {
            case StagePerformer.Usher:
            {
                var block = FurinaStageLaw.ActUsherBlock * blk - caught;
                if (block > 0)
                {
                    await CreatureCmd.GainBlock(
                        owner, block, ValueProp.Unpowered, null, fast: true);
                }
                break;
            }
            case StagePerformer.Chevalmarin:
                // Round four: what EACH enemy was dealt, so the page prints
                // "2 damage to each of 4 enemies" and not the total of four
                // hits as one number. 2026-09-25 evening: DEALT, before the
                // enemy's Block, and not what its HP lost -- against four
                // Phantasmal Gardeners a Skittish Block ate one Gardener's 2
                // and the page printed "6 in total, split across the
                // enemies", which a seat could not tell from a bug. The act
                // did hit all four for 2; the beat's `Moved` still says what
                // their HP lost.
                var targets = Enemies(owner).ToList();
                var dealt = new List<int>(targets.Count);
                foreach (var enemy in targets)
                {
                    dealt.Add(await ElementalHit.DealUnelemented(
                        choiceContext, enemy,
                        FurinaStageLaw.ActChevalmarinDamage * dmg, owner,
                        powered: false));
                }
                each = Even(dealt);
                struck = targets.Count;
                break;
            case StagePerformer.Crabaletta:
                if (RandomEnemy(owner) is { } target)
                {
                    // `EB-743`: WHICH body, because Crabaletta picks its own.
                    // Held before the hit lands so a killing act still names
                    // what it killed -- the retired reframe's rule one arm
                    // over, and the reason the mod sends a title at all.
                    hit = target;
                    shot = HitShot.Before(target);
                    shot = shot.Dealt(await ElementalHit.DealUnelemented(
                        choiceContext, target,
                        FurinaStageLaw.ActCrabalettaDamage * dmg, owner,
                        powered: false));
                }
                break;
        }
        // Rule 6 of the Guest Cast: every act resets the performer's loss
        // count (only Wriothesley reads it).
        if (seat != null) seat.LostSinceAct = 0;
        NoteBeat(owner, beat, who, before, hit, each, struck, seat, shot,
                 caught);
    }

    /// <summary>
    /// 2026-09-25 night (the granted-guest seat round): ONE BODY'S HIT, as
    /// the page prints it. "Wriothesley acted: 1 Cryo to Wriggler" was his
    /// 14 into a body with 1 HP left: the beat filed what the HP lost. This
    /// carries the hit as dealt (after the target's modifiers, before its
    /// Block), the body's HP before it, and what its Block took.
    /// </summary>
    internal readonly record struct HitShot(int Hit, int HpBefore,
                                            int BlockBefore)
    {
        public static readonly HitShot None = new(-1, -1, -1);

        public static HitShot Before(Creature target) =>
            new(-1, target.CurrentHp, target.Block);

        public HitShot Dealt(int dealt) => this with { Hit = dealt };

        /// <summary>What of the hit the body's Block took.</summary>
        public int Blocked =>
            Hit < 0 ? -1 : System.Math.Min(System.Math.Max(0, BlockBefore),
                                           Hit);
    }

    /// <summary>2026-09-25 evening: the one figure every enemy was dealt, or
    /// -1 where there were none or they differ (a Vulnerable on one of them).
    /// Measured off each hit, as every beat's number is (`EB-511`); the page
    /// prints the total on a -1.</summary>
    public static int Even(IReadOnlyList<int> dealt)
    {
        if (dealt.Count == 0) return -1;
        foreach (var figure in dealt)
        {
            if (figure != dealt[0]) return -1;
        }
        return dealt[0];
    }

    /// <summary><i>Bis!</i>: the lead performer acts <paramref name="times"/>
    /// times now (twice since the 2026-09-26 balance review). Each act
    /// resolves in full before the next, and a guest's act pays each time
    /// (rule 4); a lead that left after an act (it paid its last Fanfare)
    /// does not act again -- <see cref="Perform"/> asks the ledger whether
    /// the seat still holds it, and the next performer does not inherit the
    /// repeat.</summary>
    public static async Task PerformLead(PlayerChoiceContext choiceContext,
                                         Creature? owner, int times = 1)
    {
        // A resting returnee does not act this turn (R276 batch two).
        if (Lead(owner) is not { Resting: false } lead) return;
        for (var i = 0; i < times; i++)
        {
            if (owner!.IsDead) return;
            if (!FurinaStageLedger.For(owner).Holds(lead)) return;
            await Perform(choiceContext, owner, lead);
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
                // A guest that paid its last Fanfare, or was taxed out, has
                // left and Bowed; it does not act again (rule 4).
                if (!ledger.Holds(seat)) break;
                await Perform(choiceContext, owner, seat);
            }
        }
        await FurinaStagePets.Sync(owner);
        ledger.EndRest();
        ledger.ResetActMultipliers();
        // Rule 12 (draft 3, 2026-09-25): THE APPLAUSE FADES, after the acts.
        FadeAndShow(owner!);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// Rule 12, SEEN. The ledger's <see cref="FurinaStageLedger.Fade"/>, then
    /// the bars onto the bodies, then ONE loss number per performer that faded
    /// (<see cref="Vfx.FurinaStageLossPop"/>), in seat order. [USER], on
    /// 0.2.3820+proto: "I didn't notice any Fanfare decaying" -- the bar was
    /// the only trace. No rule moves here; the loss is measured across the
    /// ledger's own call. Returns each fading performer and what it lost.
    /// </summary>
    public static IReadOnlyList<(StageSeat Seat, int Loss)> FadeAndShow(
        Creature owner)
    {
        if (!LiveFor(owner)) return System.Array.Empty<(StageSeat, int)>();
        var ledger = FurinaStageLedger.For(owner);
        var before = ledger.Seats.Select(seat => (Seat: seat, Bar: seat.Fanfare))
            .ToList();
        if (ledger.Fade() <= 0) return System.Array.Empty<(StageSeat, int)>();
        FurinaStagePets.SyncBars(owner);
        var faded = before
            .Where(b => b.Seat.Fanfare < b.Bar)
            .Select(b => (b.Seat, b.Bar - b.Seat.Fanfare))
            .ToList();
        foreach (var (seat, loss) in faded) Vfx.FurinaStageLossPop.Show(seat, loss);
        return faded;
    }

    /// <summary>
    /// What the end-of-turn sweep will give her in Block, forecast off the
    /// same rules the sweep runs: every Usher not resting acts
    /// <see cref="FurinaStageLaw.ActUsherBlock"/> times this turn's Arkhe
    /// multiple, once plus Full House's extra acts on a full stage. The seat
    /// page prints it as "after the acts" (the wire's `act_block`).
    /// </summary>
    /// <remarks>2026-09-25 night (the granted-guest seat round): ONE BLOCK
    /// NUMBER. This counted 3 per Usher standing, while the forecast's attack
    /// line ran the sweep, in which a guest's payment can empty an Usher and
    /// his Bow gives 3 more ("after the acts: Block 3" beside "after the
    /// acts' Block of 6" on one screen). It is now the forecast's own Block
    /// after the acts, less the Block she holds.</remarks>
    public static int ForecastActBlock(Creature? owner)
    {
        if (!LiveFor(owner)) return 0;
        var forecast = Forecast(owner!, null);
        return forecast.BlockAfterActs - (int)owner!.Block;
    }

    /// <summary>Full House's extra acts: the sum of its stacks.</summary>
    private static int FullHouseActs(Creature owner) =>
        (int)owner.Powers.OfType<FullHousePower>().Sum(p => p.Amount);

    /// <summary>
    /// Rule 9, the curtain call: performed ONCE by a performer that reached 0
    /// Fanfare, whatever emptied it -- a Spend, a hit (paid at
    /// <see cref="Flush"/>, right after the hit), or a summon on a full
    /// stage. It
    /// takes the EXIT rather than the performer so a rotation cannot be
    /// mistaken for a departure at a call site --
    /// <see cref="StageExit.Bows"/> is the ledger's own read of rule 7, and a
    /// departure that earned no bow returns here without paying.
    ///
    /// THE BOW IS THE PERFORMER'S ACT, ONCE MORE (draft 3, 2026-09-25; [USER]
    /// ruled the Stage review's pick 1, one effect per performer, since
    /// Chevalmarin's old Bow was "strictly worse than the end-of-turn
    /// effect"): Usher 3 Block, Chevalmarin 2 to every enemy, Crabaletta 5 to
    /// a random enemy -- <see cref="Act"/> itself, filed as a <c>bow</c>.
    /// ONE act: Ousia and Pneuma double it like any act, and Full House does
    /// not repeat it (only <see cref="EndOfTurnActs"/> loops). A hit's Bow on
    /// the enemy's turn is paid then, between that enemy's hits ([USER],
    /// 2026-09-25: "I think it would be better to have the performer bow
    /// immediately (during the opponent's turn) instead of at the start of
    /// your turn").
    /// </summary>
    public static async Task Bow(PlayerChoiceContext choiceContext,
                                 Creature owner, StageExit exit,
                                 bool mayReturn = true)
    {
        if (!exit.Bows || !LiveFor(owner)) return;
        await Act(choiceContext, owner, exit.Who,
                  FurinaStageLedger.BowEvent, null, exit);
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
                                 Creature? hit = null, int each = -1,
                                 int struck = -1, StageSeat? acting = null,
                                 HitShot? shot = null, int caught = 0)
    {
        var after = Ledger(owner);
        // A hit's Bow whose Block the rest of that hit already spent: the
        // Block it GAVE is what she gained now plus what it caught.
        var moved = (after.Block - before.Block)
                    + (before.EnemyHp - after.EnemyHp) + caught;
        var one = shot ?? HitShot.None;
        var ledger = FurinaStageLedger.For(owner);
        // The seat that acted, where the caller knows it (two Ushers are two
        // seats since the trio can be cloned); else the first of that name.
        var seat = acting != null
            ? IndexOfSeat(ledger, acting)
            : ledger.SeatIndexOf(who);
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
            each, Struck: struck,
            Dealt: one.Hit, TargetHp: one.Hit < 0 ? -1 : one.HpBefore,
            Blocked: one.Blocked, Caught: caught));
    }

    private static int IndexOfSeat(FurinaStageLedger ledger, StageSeat seat)
    {
        for (var i = 0; i < ledger.Seats.Count; i++)
        {
            if (ReferenceEquals(ledger.Seats[i], seat)) return i;
        }
        return -1;
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
    /// lands BETWEEN the hits of a multi-hit attack, on the enemy's turn.
    /// Since 2026-09-25 night the Block of that Bow has already met the rest
    /// of the hit that emptied the performer ("a performer emptied by a hit
    /// Bows before the rest of that hit reaches you";
    /// <see cref="StageExit.Caught"/>), and what is left of it meets the next
    /// hit. [USER], 2026-09-25
    /// evening, overruling the start-of-turn wait #676 built: "I think it
    /// would be better to have the performer bow immediately (during the
    /// opponent's turn) instead of at the start of your turn."
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

    // THE GUEST CAST (2026-09-25, review/active/furina-guest-batch-2026-09-25.md):
    // eight Fontaine characters who reach the Stage through Furina's own
    // Guest Star cards. Performers in every other way; one of each on stage.
    Neuvillette,
    Clorinde,
    Navia,
    Chevreuse,
    Wriothesley,
    Sigewinne,
    Charlotte,
    Lynette,
}
