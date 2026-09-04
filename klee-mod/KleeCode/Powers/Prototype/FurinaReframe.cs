using System.Collections.Generic;
using System.Linq;
// ALIASED, not imported: the base game ships its own
// `MegaCrit.Sts2.Core.Models.Cards.DramaticEntrance`, so a plain import of
// Furina's generated namespace makes the name ambiguous. The alias says
// which one this seam means at every use.
using FurinaGen = KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Powers;

/// <summary>
/// THE FURINA REFRAME SWITCH, C# side. Twin of the sim's
/// <c>tier0/engine/furina_reframe.py</c>, and a PORT of it: every rule below
/// is the one that module already implements, every number below is read from
/// it by <c>tools/lint_constant_parity.py</c>, and nothing here was decided
/// on this side of the wire.
///
/// The countersigned design is <c>review/ruled/furina-reframe-2026-08-29.md</c>
/// (R220 A, its <c>F</c>-picks answered by R224) plus
/// <c>review/ruled/furina-spotlight-options-2026-08-30.md</c> sec.5 (R228
/// option 1) and the slot-6 ruling of 2026-08-30 (the aimed Evoke). R220 B
/// sequenced the C# leg last; this is that leg, and NOTHING IN IT IS ON.
///
/// WHY THE FLAGS LIVE HERE AND NOT IN <c>FurinaResourceConstants</c>. The sim
/// gives the reason for its own half in as many words -- the packet's sec.6.1
/// says the master flag is "sim-side a module constant in the reframe module,
/// <b>not</b> in <c>constants.py</c>", because a flag in <c>constants.py</c>
/// is read by the parity gate and the constant census while a flag in a module
/// the shipped engine only branches on is quarantined machinery. The same
/// argument lands the same way here: the switch is in <c>Powers/Prototype/</c>,
/// which <c>KleeCode.csproj</c> <c>Compile Remove</c>s out of a release build,
/// and <c>FurinaResourceConstants</c> is untouched.
///
/// FIVE FLAGS, NOT ONE, BECAUSE THE SIM HAS FIVE. The master is AND-ed into
/// every leg, so one flip returns the shipped engine no matter what else is
/// set -- that is the sim's <c>test_the_master_flag_gates_every_leg</c> and it
/// is pinned again here. Each leg is independently settable so a headless pin
/// can exercise ONE rule and assert the other three are still shipped, which
/// is the shape the sim's paired tests take.
///
/// TWO SWITCHES, NOT ONE, AND THEY DO DIFFERENT JOBS -- the same arrangement
/// <see cref="KleeOverhaul"/>, <see cref="CompanionOverhaul"/> and
/// <see cref="KokomiOverhaul"/> make, for the same reasons:
///
///   * <c>-p:PrototypeCards=true</c> (defines <c>PROTOTYPE_CARDS</c>) is the
///     QUARANTINE. It compiles <c>Powers/Prototype/**</c> -- this file
///     included -- so a release build contains no type from this arm at all,
///     and every seam that calls in from a shipped file is itself inside
///     <c>#if PROTOTYPE_CARDS</c>.
///   * <c>-p:FurinaReframe=true</c> (defines <c>FURINA_REFRAME</c>) is the
///     ARM. It only moves the five defaults below. The rules compile either
///     way, because the headless pins have to exercise the rules AND assert
///     the flag-off wiring in one build.
///
/// WHAT THE ARM MOVES, exhaustively -- the four ruled sentences the sim slice
/// implements and nothing else. Every seam is one <c>if</c> on one of the four
/// <c>*LiveFor</c> readers below.
///
/// MANUAL (<see cref="ManualLiveFor"/>), four seams:
///   * <c>SalonMemberPower.AfterPlayerTurnStart</c> -- members stop
///     auto-playing. There is no end-of-turn Salon path, so suppressing this
///     one broadcast removes the automatic engine entirely (packet sec.2.2).
///   * <c>FurinaResourceHooks.AfterCardPlayed</c> -- a Companion play makes
///     the FRONT member perform and then rotate (sec.4.3, <c>F3</c> (1) /
///     <c>F4</c> (1)).
///   * <c>SalonMemberPower.Deploy</c>, twice -- the member that ENTERS
///     performs at once, and a deploy onto a full stage EVOKES the front
///     member to make room (sec.4.2, all three RULED).
///
/// EVOKE (<see cref="EvokeLiveFor"/>), three seams:
///   * <c>SalonMemberPower.Bow</c> -- the Focus term is applied
///     <see cref="FurinaReframeLaw.EvokeFocusMult"/> times instead of once
///     (<c>F6</c> (1)), on the Focus term ALONE and never on the printed base.
///   * <c>SalonMemberPower.BowLeftmost</c> -- the bow takes the member the
///     card NAMES, front when it names none (<c>F5</c> as the slot-6 ruling
///     revised it).
///   * the Encore price (<c>F7</c> (1)) is the card's shipped Encore cost and
///     needed no port: the playability gate and the spend are shipped
///     machinery in both engines and they already run before the op resolves.
///
/// METER (<see cref="MeterLiveFor"/>), six seams -- two that mint and four
/// that stop:
///   * <c>SalonMemberPower.PerformMember</c> mints the small amount, at the
///     ONE implementation of a member performing rather than at its three
///     callers, exactly as the sim puts it inside <c>salon_member_act</c>.
///   * <c>SalonMemberPower.Bow</c>, evoked, mints the larger one.
///   * <c>FurinaResources.SpendEncore</c>, <c>FurinaResources.AbsorbDamage</c>,
///     <c>FurinaResourceHooks.AfterCurrentHpChanged</c> and
///     <c>SpotlightSystem.NotePlay</c> mint NOTHING (sec.4.1 retires all four
///     shipped legs, and with them the shipped invariant "every point of
///     damage past Block prints exactly 1 Fanfare").
///
/// SPOTLIGHT (<see cref="SpotlightLiveFor"/>), two seams:
///   * <c>SpotlightSystem.CenterStageActive</c> is False -- Center Stage
///     retires (R228 (1)).
///   * <c>EtherealSpotlight</c> stops offering a choice and
///     <c>SpotlightSystem.DesignateOneMode</c> aims Guest Cast for
///     <see cref="FurinaReframeLaw.SpotlightDesignateEncoreCost"/> Encore.
///     Guest Cast itself and <c>GuestCastBaseMultiplier</c> are KEPT: the pick
///     moved what the selector IS, not what it pays.
///
/// FLAG OFF IS BYTE-IDENTICAL, and that is the acceptance condition. Every one
/// of those seams is an early branch on one of the readers below, so with the
/// arm off the upkeep runs, a Companion play touches nothing, a deploy
/// performs nobody, a bow is the shipped bow to the digit, all four mint legs
/// pay and the selector runs its shipped heuristic. It is pinned by
/// <c>KleeTests/Prototype/FurinaReframeRuleTests.cs</c> and by the sim's own
/// <c>tier0/tests/test_furina_reframe_slice1.py</c> rather than intended.
/// </summary>
public static class FurinaReframe
{
    /// <summary>
    /// The arm's default: <c>-p:FurinaReframe=true</c> turns it on. Mirrors
    /// the sim's five module flags, which all ship <c>False</c>.
    ///
    /// ONE PROPERTY MOVES ALL FIVE, deliberately. The sim has no compile step,
    /// so "the slice is on" there means flipping the master and the four legs
    /// together -- which is what every one of its fixtures does. A property
    /// that moved only the master would build an arm that compiles and does
    /// nothing, and a dev build nobody can tell apart from a release build is
    /// the failure <c>EB-257</c> already cost a run to.
    /// </summary>
    public const bool DefaultEnabled =
#if FURINA_REFRAME
        true;
#else
        false;
#endif

    /// <summary>The master. Every leg below is AND-ed with it, so one flip
    /// returns the shipped engine. Mirrors <c>FURINA_REFRAME</c>.</summary>
    public static bool Enabled { get; set; } = DefaultEnabled;

    /// <summary>Members stop auto-playing; the Companion trigger fires; a
    /// deploy performs; a deploy onto a full stage Evokes. Mirrors
    /// <c>FURINA_REFRAME_MANUAL</c>.</summary>
    public static bool ManualEnabled { get; set; } = DefaultEnabled;

    /// <summary>The Evoke verb, its Focus multiplier and its aim. Mirrors
    /// <c>FURINA_REFRAME_EVOKE</c>.</summary>
    public static bool EvokeEnabled { get; set; } = DefaultEnabled;

    /// <summary>Fanfare minted by performance, and only by performance.
    /// Mirrors <c>FURINA_REFRAME_METER</c>.</summary>
    public static bool MeterEnabled { get; set; } = DefaultEnabled;

    /// <summary>R228 (1): one mode, priced. Mirrors
    /// <c>FURINA_REFRAME_SPOTLIGHT</c>.</summary>
    public static bool SpotlightEnabled { get; set; } = DefaultEnabled;

    /// <summary>
    /// R251 (2026-09-04), <c>EB-365</c>: THE SHIPPED BURST METER RETIRES UNDER
    /// THIS ARM, and only under this arm. Mirrors <c>FURINA_REFRAME_BURST</c>.
    ///
    /// The round-one seat's meter read <c>78/70</c>, over its own cap, and
    /// <i>Let the People Rejoice</i> arrived off that overflow to take the boss
    /// from 28 to 14 -- the clutch turn of the run, and the shipped kit's
    /// rather than the reframe's. R220 B had sequenced the Burst fold last, so
    /// the shipped meter still ran beside the reframe's own; the round-one
    /// pick's new fact is that it will sit inside every Furina read until it
    /// goes.
    ///
    /// ARM-ONLY, and that is the whole scope. The SHARED retirement
    /// (<c>EB-199</c> / <c>EB-200</c>) still owns the shipped engines -- the
    /// resource class, the <c>Burst Energy</c> keyword id, the constants, the
    /// kit-grant machinery and every other character's meter are untouched
    /// here. What this leg does is Kokomi's <c>EB-297</c> and <c>EB-327</c> one
    /// character over: under the flag the meter does not DRAW, nothing FEEDS it
    /// (<c>EB-266</c>'s reaction funnel included), and the kit card is never
    /// GRANTED.
    /// </summary>
    public static bool BurstEnabled { get; set; } = DefaultEnabled;

    /// <summary>
    /// Whose engine this is. Every leg is character-scoped, which is the sim's
    /// <c>is_furina</c> and its stated reason: the reframe is one character's
    /// redesign and a roster-wide branch would be a different (and much
    /// larger) change than the one that was countersigned. In co-op the other
    /// seat may be Klee, and a bare flag read would suppress HIS turn-start.
    /// </summary>
    public static bool IsFurina(Creature? creature) =>
        creature != null && FurinaResources.IsFurina(creature);

    /// <summary>Is the MANUAL leg live for this creature?</summary>
    public static bool ManualLiveFor(Creature? creature) =>
        Enabled && ManualEnabled && IsFurina(creature);

    /// <summary>Is the EVOKE leg live for this creature?</summary>
    public static bool EvokeLiveFor(Creature? creature) =>
        Enabled && EvokeEnabled && IsFurina(creature);

    /// <summary>Is the METER leg live for this creature?</summary>
    public static bool MeterLiveFor(Creature? creature) =>
        Enabled && MeterEnabled && IsFurina(creature);

    /// <summary>Is the one-mode SPOTLIGHT leg live for this creature?</summary>
    public static bool SpotlightLiveFor(Creature? creature) =>
        Enabled && SpotlightEnabled && IsFurina(creature);

    /// <summary>Is the shipped Burst meter RETIRED for this creature? The one
    /// question the display guard, the income funnel and the kit grant all ask,
    /// so "she has no Burst meter under the arm" is one decision rather than
    /// three that can be retired by halves. Mirrors
    /// <c>furina_reframe.burst_retired</c>.</summary>
    public static bool BurstRetiredFor(Creature? creature) =>
        Enabled && BurstEnabled && IsFurina(creature);

    /// <summary>
    /// How many times an Evoke applies the Focus term. ONE when the leg is
    /// off, which is what makes an evoked bow resolve exactly like the shipped
    /// bow in a release world. Mirrors <c>evoke_focus_mult</c>.
    /// </summary>
    public static int EvokeFocusMult(Creature? creature) =>
        EvokeLiveFor(creature) ? FurinaReframeLaw.EvokeFocusMult : 1;

    // ------------------------------------------------------------------
    // The aimed Evoke -- the slot-6 ruling, 2026-08-30.
    // ------------------------------------------------------------------

    /// <summary>
    /// The named member is not on the stage. Mirrors
    /// <c>furina_reframe.EVOKE_TARGET_ABSENT</c>: the caller says so out loud
    /// (D4) and takes the front, which is what an unaimed Evoke does.
    /// </summary>
    public const int EvokeTargetAbsent = -1;

    /// <summary>
    /// NO AIM IS THE FRONT. The sim writes its sentinel out as the string
    /// <c>"front"</c> so that "unstated" and "front" are the same word on a
    /// face and in a row; C# spells the aim as a nullable
    /// <see cref="SalonMember"/>, so the sentinel is <c>null</c> and this is
    /// the name for it. Both engines mean one rule, not two.
    /// </summary>
    public static readonly SalonMember? EvokeTargetFront = null;

    /// <summary>
    /// Which member the dedicated Evoke takes: the index into the company.
    ///
    /// THE RULE, from the slot-6 ruling (2026-08-30, [USER]): the dedicated
    /// Evoke lets the card CHOOSE which member it removes, and the FRONT is
    /// what it takes when nothing is named. The full-stage deploy path is
    /// untouched and stays automatic-front -- it never calls this -- because
    /// the same ruling keeps the overflow Evoke as the reward for filling the
    /// stage, and what Encore buys is the deliberate aim the free route
    /// structurally lacks.
    ///
    /// FLAG-GATED, so the shipped bow cannot be aimed: with
    /// <see cref="EvokeEnabled"/> off this returns 0 whatever is named, which
    /// is the front member the shipped bow has always popped.
    ///
    /// A TYPO CANNOT REACH HERE, which is the one place the two engines differ
    /// in SHAPE rather than in rule. The sim's op reads a member NAME off a
    /// row and raises <c>ValueError</c> on an unknown one, because a typo that
    /// quietly degraded into "the front member" is the failure an aimed Evoke
    /// could hide for a whole sprint. C# spells the aim as an enum, so the
    /// refusal is the type system's and there is no unknown name to raise on.
    /// </summary>
    public static int EvokeTargetIndex(
        Creature? owner, IReadOnlyList<SalonMember> company, SalonMember? named)
    {
        if (named is not { } aim || !EvokeLiveFor(owner)) return 0;
        for (var i = 0; i < company.Count; i++)
        {
            if (company[i] == aim) return i;
        }
        return EvokeTargetAbsent;
    }

    // ------------------------------------------------------------------
    // The mints. Both live here rather than at the seams, because sec.4.1's
    // rule is positive ("a member performing mints Fanfare, and nothing else
    // does") and a rule stated positively should have one home. Same argument
    // and same shape as the sim's `mint_for_performance` / `mint_for_evoke`.
    // ------------------------------------------------------------------

    /// <summary>
    /// A member performed and STAYED: the small amount (a Companion trigger, a
    /// deploy-performs, or a <c>salon_perform</c> card -- all the same act, so
    /// all the same mint).
    ///
    /// LAW:145 IS LIVE HERE, and it is why the amount is a <c>Math.Min</c>
    /// against a second constant rather than the trigger figure alone. The
    /// clause (countersigned R224) permits "a character-owned engine [to]
    /// respond to a Companion play and generate its resource where that
    /// character's kit explicitly declares the trigger and BOUNDS THE AMOUNT
    /// GENERATED PER COMPANION PLAY". Klee's kit declares hers with
    /// <see cref="KleeCompanionSpark.MaxPerPlay"/>; this is the same
    /// declaration for Furina's, and it is a bound rather than a
    /// recommendation -- one performance per play, one trigger mint, capped.
    /// </summary>
    public static void MintForPerformance(Creature? creature)
    {
        if (creature == null || !MeterLiveFor(creature)) return;
        // `Math.Min` and not the trigger figure alone, mirroring the sim's
        // `min(FANFARE_PER_TRIGGER, FANFARE_PER_COMPANION_TRIGGER_MAX)`: the
        // bound has to be APPLIED somewhere or it is a comment, and this is
        // the one site a performance mints at.
        FurinaResources.GainFanfare(
            creature,
            System.Math.Min(FurinaReframeLaw.FanfarePerTrigger,
                            FurinaReframeLaw.FanfarePerCompanionTriggerMax));
    }

    /// <summary>A member performed and LEFT: the larger amount. The ordering
    /// (trigger &lt; Evoke, because an Evoke costs a member) is the RULED half
    /// of the pair; the two figures themselves are prototype seeds.</summary>
    public static void MintForEvoke(Creature? creature)
    {
        if (creature == null || !MeterLiveFor(creature)) return;
        FurinaResources.GainFanfare(creature, FurinaReframeLaw.FanfarePerEvoke);
    }
}

/// <summary>
/// The numbers the reframe's RULES carry, and there are five.
///
/// MIRRORED BY VALUE from <c>tier0/engine/furina_reframe.py</c>, which is why
/// each is a named constant rather than a literal at the call site
/// (<c>tools/lint_constant_parity.py</c> compares all five). They live in the
/// reframe MODULE on the sim side rather than in <c>constants.py</c>, so the
/// lint reads them from there; quarantined is not exempt, for the reason the
/// Kurage's three and the Klee overhaul's five are not -- a prototype played
/// on a number the sim never declared is exactly what that gate exists for.
///
/// PROTOTYPE SEEDS, NOT RULED NUMBERS. The packet's sec.4.1 says so of the
/// small/large pair in as many words: "their ORDERING is ruled: trigger &lt;
/// Evoke, because Evoke costs a member". Under R215 B no number measured on a
/// prototype is quotable. They are placeholders -- but they are the
/// placeholders both engines have to agree on.
/// </summary>
public static class FurinaReframeLaw
{
    /// <summary>A member performing and STAYING. Mirrors
    /// <c>furina_reframe.FANFARE_PER_TRIGGER</c>.</summary>
    public const int FanfarePerTrigger = 2;

    /// <summary>A member performing and LEAVING. Greater than the trigger,
    /// which is the ruled half of the pair. Mirrors
    /// <c>furina_reframe.FANFARE_PER_EVOKE</c>.</summary>
    public const int FanfarePerEvoke = 5;

    /// <summary>
    /// LAW:145's per-Companion-play bound. One performance per play means one
    /// mint, and this is what makes that a bound instead of an accident of the
    /// call site. Mirrors
    /// <c>furina_reframe.FANFARE_PER_COMPANION_TRIGGER_MAX</c>.
    ///
    /// A LITERAL, not <c>= FanfarePerTrigger</c>, even though the sim writes it
    /// that way. <c>lint_constant_parity</c> reads the C# side by parsing the
    /// declaration and only understands a numeric literal, so an expression
    /// here would leave the number unmirrored -- and the sim's own definition
    /// is what makes this safe rather than a second copy: move
    /// <c>FANFARE_PER_TRIGGER</c> there and this literal drifts from a value
    /// derived from it, which is precisely what the gate bites on.
    /// </summary>
    public const int FanfarePerCompanionTriggerMax = 2;

    /// <summary><c>F6</c> (1): the Focus term applied N times on an Evoke,
    /// once on a trigger, N printed on the face. One divisor, one number on
    /// screen. Mirrors <c>furina_reframe.EVOKE_FOCUS_MULT</c>.</summary>
    public const int EvokeFocusMult = 3;

    /// <summary>R228 (1): the one-mode selector's price. The packet names the
    /// risk itself -- a THIRD claim on one unbounded buffer, beside the
    /// deferred Block and the Evoke price -- and rules that it is measured
    /// rather than assumed away. Mirrors
    /// <c>furina_reframe.SPOTLIGHT_DESIGNATE_ENCORE_COST</c>.</summary>
    public const int SpotlightDesignateEncoreCost = 2;
}

/// <summary>
/// THE ARM'S ONE POOL SEAM (Furina reframe round 2 pick 1, taken at its
/// default 2026-09-04). Sim twin: <c>furina_reframe.POOL_SUBS</c>, read by
/// <c>tier0.content.loader._pool_substitutions</c> at the one door
/// <c>tier05.rewards.character_pool</c> already reads.
///
/// WHY IT EXISTS. The arm mints Fanfare by performance ALONE -- 2 per trigger
/// and 5 per Evoke -- and across three rounds the meter ranged 0 to 15, while
/// four shipped rows gate on it at 12, 12, 15 and 20. Two of them essentially
/// cannot pay under the arm, and a card whose printed condition the run cannot
/// reach is a dead row rather than a hard one.
///
/// A SWAP AND NOT A SHEET EDIT, which is the same argument
/// <see cref="KurageMemory.SwapOfferedOath"/> makes one character over. The
/// shipped sheet is Balance-stage content and does not move for a prototype
/// arm (R213 B), so the copies are prototype rows carrying the arm's own
/// thresholds (6, 6, 8, 10) and the arm swaps them in HERE, at the offer.
/// Same rarity in and out -- two Uncommons and two Rares -- so the offer odds
/// do not move.
///
/// ONE SEAM, for <c>SwapOfferedOath</c>'s reason verbatim:
/// <c>FilterThroughEpochs</c> feeds <c>GetUnlockedCards</c>, which is the SOLE
/// path into reward rolls, the shop and card transforms. Nothing else
/// generates from a pool, so "every offer surface" is a property of the code
/// and not a list this method has to keep in step with.
///
/// THE SHIPPED ROWS STAY IN THE POOL for <c>CardModel.Pool</c> legality -- a
/// poolless card throws "You monster!" the moment it is drawn, and a player
/// who already holds one must still be able to draw it. They are only
/// unofferable, which is the same in/out split the kit Burst uses.
///
/// WITH THE ARM OFF THIS IS THE IDENTITY FUNCTION, checked at the top rather
/// than assumed by its caller -- the same shape every other reader on this
/// switch takes, and what makes the flag-off pin a property of this method.
/// </summary>
public static class FurinaReframeRoster
{
    /// <summary>The four shipped riders, out; the four arm copies, in.</summary>
    public static IEnumerable<CardModel> SwapOfferedRiders(
        IEnumerable<CardModel> offered)
    {
        if (!FurinaReframe.Enabled) return offered;
        return offered
            .Where(card => card is not FurinaGen.FloridCadenza
                        && card is not FurinaGen.DramaticEntrance
                        && card is not FurinaGen.UniversalRevelry
                        && card is not FurinaGen.FloodOfEmotion)
            .Concat(PrototypeCards.For("furina")
                        .Where(card => card is ProtoFrFloridCadenza
                                            or ProtoFrDramaticEntrance
                                            or ProtoFrUniversalRevelry
                                            or ProtoFrFloodOfEmotion));
    }

    /// <summary>
    /// THE ARM'S ONE STARTER SEAM (R254, round 4 pick 1, 2026-09-04). Slot 8
    /// of <c>Furina.StartingDeck</c>: with the arm on it is the reframe copy
    /// of <i>Aria of Recompense</i>, and otherwise the shipped card, byte for
    /// byte. Sim twin: <c>furina_reframe.STARTER_SUBS</c>, read by
    /// <c>tier0.content.loader._starter_ids</c> -- the ONE seam both the
    /// tier-0 battery and the tier-0.5 run go through.
    ///
    /// [USER], ruling the round-4 packet's sec.6: "maybe a reader in the
    /// starter deck? I still want to leave it at just 2 'good' cards, but they
    /// can be stronger." Her two kit starters stay two, and ONE of them reads
    /// Fanfare: "Gain 5 Encore. If you have at least 3 Fanfare, gain 5 more."
    /// Both numbers are LIFTED rather than picked -- the 5 is Aria's own
    /// printed Encore, the 3 is the Fanfare the seat records show on an Aria
    /// turn -- and the loop it closes is the arm's own: a stage that performs
    /// mints Fanfare, Fanfare pays Encore, Encore pays performances.
    ///
    /// THE BAR MOVED 6 -> 3 (round 6 sec.4, 2026-09-04, a D default). It was
    /// built at the rider copies' 6 and three seat runs never once paid the
    /// second line, because Aria is played BEFORE the stage performs. The four
    /// OFFERED rider copies above keep their own bars, which are read later in
    /// the turn.
    ///
    /// ONE CARD FOR ONE CARD, which is <see cref="KurageMemory.StarterSlotEleven"/>'s
    /// shape one character over and what keeps this a substitution rather than
    /// a starter rework: the deck is still ten.
    ///
    /// THE PRINTED SHEET DOES NOT MOVE. <c>docs/furina-cards.yaml</c> still
    /// says <c>aria_of_recompense</c> and its generated card is untouched;
    /// only this slot moves, and only under the flag. A starter card's text is
    /// a RULE, so [USER] plays the first build that carries it.
    /// </summary>
    public static CardModel StarterAria() =>
        FurinaReframe.Enabled
            ? ModelDb.Card<ProtoFrAriaOfRecompense>()
            : ModelDb.Card<FurinaGen.AriaOfRecompense>();

    /// <summary>
    /// THE ARM'S OTHER STARTER SLOT (<c>EB-416</c>). Slot 9 of
    /// <c>Furina.StartingDeck</c>: with the arm on it is the NAMED <i>Salon
    /// Début</i>, otherwise the shipped card, byte for byte. Sim twin: the
    /// second pair in <c>furina_reframe.STARTER_SUBS</c>.
    ///
    /// A WIRING DEFECT CLOSED, NOT A NEW DECISION. The reframe packet's sec.5
    /// ruled that the starter deploy NAMES its member, and slice 2 built the
    /// row that says so -- <c>proto_fr_salon_debut_named</c>, "Deploy
    /// Mademoiselle Crabaletta". The row was generated, pooled and pinned, and
    /// it was wired into NO starter in either engine, so the arm went on
    /// dealing the shipped card and its RANDOM member. That matters most
    /// exactly here: under <see cref="FurinaReframe.ManualEnabled"/> the front
    /// member is the one a Companion play makes perform, so a random deploy
    /// decides for the player which member their first trigger fires. The
    /// R254 Aria build found the gap while opening this seam.
    ///
    /// ONE CARD FOR ONE CARD, like the slot above it: the deck is still ten
    /// and <c>docs/furina-cards.yaml</c> does not move.
    /// </summary>
    public static CardModel StarterSalonDebut() =>
        FurinaReframe.Enabled
            ? ModelDb.Card<ProtoFrSalonDebutNamed>()
            : ModelDb.Card<FurinaGen.SalonDebut>();
}
