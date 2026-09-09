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
/// ONE FLAG, NOT FIVE, and the difference from <see cref="FurinaReframe"/> is
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
/// THE REFRAME IS NOT DELETED BY THIS BRANCH, and that is disclosed rather
/// than assumed: brief sec.2 retires <c>FURINA_REFRAME</c>, but the brief is
/// OPEN (its sec.11 picks are unruled) and the reframe's surface is a sim
/// engine module, twenty-odd sheet rows and some five thousand lines of pins.
/// Building this arm BESIDE it is the reversible move; the two are
/// independent switches and a build carrying both is not a supported
/// configuration of the design, only of the compiler.
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
    /// <remarks>The null test is FIRST and is load-bearing:
    /// <c>FurinaResources.IsFurina</c> dereferences its argument, so a caller
    /// with no creature -- a compendium page, a card on a shelf, a hook fired
    /// on a board being torn down -- would throw rather than answer.</remarks>
    public static bool LiveFor(Creature? creature) =>
        creature != null && Enabled && FurinaResources.IsFurina(creature);

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

    /// <summary>Rule 8's one refusal, and the predicate every Spend card's
    /// `conditional` branches on: with no performer on stage the rider cannot
    /// fire and the card plays at its base number. The question is OCCUPANCY
    /// and never size -- a bar of any size pays the whole rider.</summary>
    public static bool Occupied(Creature? owner) => Of(owner).Count > 0;

    /// <summary>The live lead bar, for the `stage_lead_fanfare` count
    /// (<i>Ousia Surge</i>).</summary>
    public static int LeadFanfare(CardModel? card) =>
        LeadFanfare(card?.Owner?.Creature);

    /// <summary>The live back bar, for `stage_back_fanfare` (<i>Pneuma
    /// Refrain</i>).</summary>
    public static int BackFanfare(CardModel? card) =>
        BackFanfare(card?.Owner?.Creature);

    /// <summary>A fresh, empty per-play spend record.</summary>
    public static void BeginPlay(Creature? owner)
    {
        if (owner != null) FurinaStageLedger.For(owner).BeginPlay();
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
    /// is the lead's live bar; during the play, the bar is gone and what the
    /// card took is the record. One expression, so the previewed number and
    /// the resolved number cannot differ -- which is what a CalculatedVar is
    /// for.
    ///
    /// IT NEEDS <see cref="BeginPlay"/> TO BE CALLED, and until this row it
    /// was not: the record was written by each spending op and never reset, so
    /// a stale amount from an earlier card would have been previewed as this
    /// card's forecast. `FurinaStageHooks.BeforeCardPlayed` clears it now,
    /// which is `FurinaDrain.BeginPlay`'s site one arm over.
    ///
    /// 0 ON AN EMPTY STAGE, in both moments, which is the row's own
    /// acceptance.
    /// </summary>
    public static int SpentOrLeadFanfare(CardModel? card)
    {
        var spent = Spent(card);
        return spent > 0 ? spent : LeadFanfare(card);
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
        if (FurinaStageLedger.For(owner!).OpenWith(StagePerformer.Usher) == null)
        {
            return;
        }
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
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
    /// on stage; with all three seated it summons nobody.</para>
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
            var seated = ledger.Company.ToHashSet();
            var free = Performers.Select(Parse)
                .Where(p => !seated.Contains(p)).ToList();
            if (free.Count == 0) return;
            var roll = owner!.Player?.RunState.Rng.CombatTargets;
            who = roll != null ? roll.NextItem(free) : free[0];
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

    /// <summary>Rule 5. Raise lands on the back-most performer, which is the
    /// lead when it is alone. Returns what landed.</summary>
    public static int Raise(Creature? owner, int amount)
    {
        if (!LiveFor(owner)) return 0;
        var raised = FurinaStageLedger.For(owner!).Raise(amount);
        if (raised > 0)
        {
            FurinaStagePets.SyncBars(owner);
            Vfx.FurinaStageStrip.Refresh(owner);
        }
        return raised;
    }

    /// <summary>
    /// Rule 8's payment leg, for a rider the CARD has already decided fires
    /// (its `conditional` asked <see cref="Occupied"/>). The lead pays what it
    /// has; if that empties it, it bows.
    ///
    /// <para>Returns WHAT WAS PAID and not what was asked, which is the number
    /// the brief's sec.13 report buckets on -- and never a reason to scale the
    /// rider down (sec.10 default 4).</para>
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
            await Bow(choiceContext, owner!,
                      new StageExit(who, StageDeparture.Spent));
        }
        foreach (var who in company) ledger.Summon(who);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary><i>Final Bow</i>: the lead takes a bow and leaves. A BOW
    /// WITHOUT A SPEND, and the one card that grants one -- rule 9 earns a bow
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
        switch (Parse(member))
        {
            case StagePerformer.Usher:
                await CreatureCmd.GainBlock(
                    owner!, FurinaStageLaw.ActUsherBlock,
                    ValueProp.Unpowered, null, fast: true);
                break;
            case StagePerformer.Chevalmarin:
                foreach (var enemy in Enemies(owner!))
                {
                    await ElementalHit.Deal(
                        choiceContext, enemy, Elements.Element.Hydro,
                        FurinaStageLaw.ActChevalmarinDamage, owner,
                        powered: false);
                }
                break;
            case StagePerformer.Crabaletta:
                if (RandomEnemy(owner!) is { } target)
                {
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.ActCrabalettaDamage, owner,
                        powered: false);
                }
                break;
        }
        NoteBeat(owner!, "act", Parse(member), before);
    }

    /// <summary><i>Bis!</i>: the lead performer performs its act now.
    /// </summary>
    public static async Task PerformLead(PlayerChoiceContext choiceContext,
                                         Creature? owner)
    {
        if (Lead(owner) is { } lead)
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
        foreach (var who in Of(owner).Select(s => s.Who).ToList())
        {
            if (owner!.IsDead) return;
            await Perform(choiceContext, owner, Name(who));
        }
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// Rule 9, the curtain call: performed ONCE by a performer emptied by a
    /// Spend. It takes the EXIT rather than the performer so the two ways of
    /// leaving cannot be confused at a call site --
    /// <see cref="StageExit.Bows"/> is the ledger's own read of rule 7, and a
    /// departure that earned no bow returns here without paying.
    /// </summary>
    public static async Task Bow(PlayerChoiceContext choiceContext,
                                 Creature owner, StageExit exit)
    {
        if (!exit.Bows || !LiveFor(owner)) return;
        var before = Ledger(owner);
        switch (exit.Who)
        {
            case StagePerformer.Usher:
                await CreatureCmd.GainBlock(
                    owner, FurinaStageLaw.BowUsherBlock,
                    ValueProp.Unpowered, null, fast: true);
                break;
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
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        FurinaStageLaw.BowCrabalettaDamage, owner,
                        powered: false);
                }
                break;
        }
        NoteBeat(owner, "bow", exit.Who, before);
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
                                 (int Block, int EnemyHp) before)
    {
        var after = Ledger(owner);
        var moved = (after.Block - before.Block)
                    + (before.EnemyHp - after.EnemyHp);
        var ledger = FurinaStageLedger.For(owner);
        var seat = ledger.SeatIndexOf(who);
        ledger.Note(new StageBeat(
            what, who, seat,
            seat >= 0 ? ledger.Seats[seat].Fanfare : 0,
            moved < 0 ? 0 : moved, ""));
    }

    /// <summary>Rule 6's flush: the ledger moved synchronously inside
    /// <c>ModifyHpLostBeforeOsty</c> because the engine wanted a number back,
    /// and this is where the bodies catch up. Nothing is paid out -- a
    /// performer emptied by a hit takes no bow (rule 7).</summary>
    public static async Task Flush(Creature? owner)
    {
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

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
