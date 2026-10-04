using System.Collections.Generic;
using System.Linq;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// `EB-272`: the QUARANTINED ARMS' KEYWORDS, defined once each.
///
/// THE GAP, and it is the same gap one register row over from Charge and
/// Burst. Every shipped keyword on a face has somewhere a player can read it
/// -- `Block` and `Exhaust` are the base game's, `Applies Pyro` and the eight
/// reaction previews are <see cref="KleeKeywords"/>' -- and not one word the
/// three prototype arms invented had anything at all. [USER] hit it live on
/// the dev build the day this row was filed ("Set Off has no tooltip text"),
/// and both Kokomi seats in round one inferred `Exert` from watching their own
/// HP drop, which is the only way the rule was ever stated to them. The
/// Casket's `Mend` read as BROKEN at full HP for the same reason: the
/// entry-HP bound is real, it is enforced in <see cref="KokomiRules.Mend"/>,
/// and it was printed nowhere.
///
/// A MISSING HOVER TIP RENDERS AS NOTHING AT ALL. There is no wrong number to
/// notice, no exception and no visual seam -- so this class is only half the
/// fix. The other half is that the ATTACH IS DERIVED, not remembered:
/// `gen_klee_cards.emit` reads the `[gold]Keyword[/gold]` tokens out of the
/// row's own built description and attaches the matching call from the table
/// in `ARM_KEYWORDS`. A new row that prints an arm keyword carries its
/// definition because it printed the word, not because somebody remembered.
///
/// WHY A SEPARATE CLASS FROM <see cref="KleeCardTooltips"/> AND
/// <see cref="KokomiRiderTips"/>. It lives under `Cards/Prototype/`, which
/// `KleeCode.csproj` REMOVES from a release build, for the same reason the
/// arms' powers do: these sentences describe rules that exist only under
/// `-p:PrototypeCards=true`, and several of them quote a `*OverhaulLaw`
/// constant that is not compiled otherwise. A release build contains neither
/// the text nor the keys.
///
/// WHAT THESE ARE NOT. They are NOT the badge. `ProtoBombPower` prints the
/// Bomb rules on the ENEMY, live, with the pile's own numbers in them, and
/// `PendingPlansPower` does the same for the Plans she is holding. Those stay
/// exactly as they are. A badge can only be read once the thing exists on
/// the board; the card-side keyword is what a player reads in HAND, in a
/// reward, in a shop and on the blind-play page -- which is where the word was
/// first met and where it explained nothing.
///
/// THE NUMERALS ARE INTERPOLATED FROM THE CONSTANTS THEY QUOTE (`EB-89`), so a
/// retune of `KleeOverhaulLaw.BombGrowth` cannot leave one of these
/// sentences telling a player a retired number.
/// </summary>
public static class ArmKeywordTips
{
    /// <summary>The hover-tip title table, the same one every other tip in the
    /// mod titles itself from.</summary>
    private const string Table = "card_keywords";

    // The keys. `KLEEMOD-ARM_` and not the bare word, because two of these
    // words already have a SHIPPED keyword with a DIFFERENT rule: `Bomb` is
    // `KLEEMOD-BOMB` (the shipped Bomb detonates by itself, this one never
    // does) and `Swirl` is `KLEEMOD-SWIRL_PREVIEW` (a board-aware preview,
    // raised only while a matching aura is out). A shared key would have made
    // one arm silently overwrite the other's definition at the loc merge.
    public const string BombKey = "KLEEMOD-ARM_BOMB";
    public const string SetOffKey = "KLEEMOD-ARM_SET_OFF";
    public const string SparkKey = "KLEEMOD-ARM_SPARK";
    public const string MineKey = "KLEEMOD-ARM_MINE";
    public const string GroundedKey = "KLEEMOD-ARM_GROUNDED";
    public const string OzKey = "KLEEMOD-ARM_OZ";
    public const string MendKey = "KLEEMOD-ARM_MEND";
    public const string PlanKey = "KLEEMOD-ARM_PLAN";
    public const string DuskKey = "KLEEMOD-ARM_DUSK";
    public const string CasketKey = "KLEEMOD-ARM_CASKET";
    // THE CASKET PASS (2026-09-28): the relic's token, named by What the
    // Tokoyo Returns.
    public const string OpenTheCasketKey = "KLEEMOD-ARM_OPEN_THE_CASKET";
    public const string SwirlKey = "KLEEMOD-ARM_SWIRL";
    // 2026-09-25 (the afternoon Klee seats): `Companion` is printed golded on
    // Klee's readers and on the Kokomi and Furina arms' faces, and nothing on
    // screen said what one is.
    public const string CompanionKey = "KLEEMOD-ARM_COMPANION";
    // VARKA (the Oath rework): his three words. `Swirl` is the shared rule
    // and already has its row above.
    public const string OathKey = "KLEEMOD-ARM_VARKA_OATH";
    public const string CurrentElementKey = "KLEEMOD-ARM_VARKA_CURRENT_ELEMENT";
    public const string KnightKey = "KLEEMOD-ARM_VARKA_KNIGHT";
    // ELEMENT IDENTITIES sec.7 (2026-10-01): a rider that titles no keyword,
    // a fact about THIS card on THIS board -- playing it would switch his
    // current element. Four times in one round a seat lost the Oath it was
    // building to a card of another element and noticed only later.
    public const string ElementSwitchKey = "KLEEMOD-ARM_VARKA_ELEMENT_SWITCH";
    // FURINA, THE STAGE (v2, the re-founding, 2026-10-04). The faces print
    // `Spend`, `Fanfare`, `Bow`, `Cue`, `Rehearsal` and `front performer`;
    // the summon, the Guest Star keyword and each performer's tip attach off
    // the row's own ops (`gen_klee_cards.stage_summon_tip_calls`,
    // `stage_guest_tip_calls`). The back performer and the fade retired with
    // the bars.
    public const string SpendKey = "KLEEMOD-ARM_STAGE_SPEND";
    public const string SpendShortKey = "KLEEMOD-ARM_STAGE_SPEND_SHORT";
    public const string FanfareKey = "KLEEMOD-ARM_STAGE_FANFARE";
    public const string BowKey = "KLEEMOD-ARM_STAGE_BOW";
    public const string CueKey = "KLEEMOD-ARM_STAGE_CUE";
    public const string RehearsalKey = "KLEEMOD-ARM_STAGE_REHEARSAL";
    public const string FrontPerformerKey = "KLEEMOD-ARM_STAGE_FRONT";
    // R276 batch two: Arkhe Alignment's two halves.
    public const string OusiaKey = "KLEEMOD-ARM_STAGE_OUSIA";
    public const string PneumaKey = "KLEEMOD-ARM_STAGE_PNEUMA";
    public const string SummonKey = "KLEEMOD-ARM_STAGE_SUMMON";
    public const string UsherKey = "KLEEMOD-ARM_STAGE_USHER";
    public const string ChevalmarinKey = "KLEEMOD-ARM_STAGE_CHEVALMARIN";
    public const string CrabalettaKey = "KLEEMOD-ARM_STAGE_CRABALETTA";
    public const string GuestStarKey = "KLEEMOD-ARM_STAGE_GUEST_STAR";
    public const string NeuvilletteKey = "KLEEMOD-ARM_STAGE_NEUVILLETTE";
    public const string ClorindeKey = "KLEEMOD-ARM_STAGE_CLORINDE";
    public const string NaviaKey = "KLEEMOD-ARM_STAGE_NAVIA";
    public const string ChevreuseKey = "KLEEMOD-ARM_STAGE_CHEVREUSE";
    public const string WriothesleyKey = "KLEEMOD-ARM_STAGE_WRIOTHESLEY";
    public const string SigewinneKey = "KLEEMOD-ARM_STAGE_SIGEWINNE";
    public const string CharlotteKey = "KLEEMOD-ARM_STAGE_CHARLOTTE";
    public const string LynetteKey = "KLEEMOD-ARM_STAGE_LYNETTE";
    public const string LyneyKey = "KLEEMOD-ARM_STAGE_LYNEY";
    public const string EscoffierKey = "KLEEMOD-ARM_STAGE_ESCOFFIER";

    // `EB-378`. NOT A KEYWORD, and the only key here that is not: it titles a
    // RIDER on the rows whose element arrives with the jellyfish rather than
    // with the play. It lives in this class because it is a sentence about the
    // Plan, which is this class's word and this quarantine's rule.
    public const string PlanElementKey = "KLEEMOD-ARM_PLAN_ELEMENT";

    // `EB-709`. A RIDER AND NOT A KEYWORD, beside `PlanElementKey` for that
    // key's reason: it is a sentence about the one card that doubles a
    // carry-out, printed where that card is met.
    public const string PlanTwiceKey = "KLEEMOD-ARM_PLAN_TWICE";

    // `EB-575`. THE FOURTH KEY HERE THAT TITLES NO KEYWORD, and the only one
    // whose sentence appears and disappears with the board. A `Set off` or a
    // merge played with no Bomb anywhere is ACCEPTED, charges its Energy and
    // its Spark, and does its own line or nothing at all -- silently, while a
    // Spark-priced card the bank cannot afford prints CANNOT BE PLAYED. The
    // r21 lane-1 seat played Careful Arrangement on a bare board and Fwoosh!
    // on another, and read both as blanks the game charged for. Furina's
    // empty-stage rider is the same shape one arm over
    // (<see cref="KleeMod.Cards.FurinaRiderTips.ForCompanionPerform"/>).
    public const string EmptyFieldKey = "KLEEMOD-ARM_EMPTY_FIELD";

    // `EB-573`. THE FIFTH KEY HERE THAT TITLES NO KEYWORD. Careful
    // Arrangement's face promises the merged charge is "a Mine if any of them
    // was" and says nothing about RIDERS -- and `ProtoBombPower.MergeAllTo`
    // sums `PayloadMineAll` across every charge it takes, so Jumpy Dumpty's
    // Mine-on-ALL survives the merge and grows in bulk. The r21 lane-1 seat
    // met a Bomb 21 that was Jumpy's Bomb 8 two merges ago still dropping Mine
    // 3 on ALL, called it a large part of the kit's ceiling, and said it was
    // "completely undiscoverable except by accident".
    public const string MergeRidersKey = "KLEEMOD-ARM_MERGE_RIDERS";

    // ----------------------------------------------------------- Klee ------
    //
    // The four sentences are the ruled brief's sec.3 rules 1, 2, 4 and 6, as
    // slice one prints them (`review/active/klee-overhaul-slice-1-2026-09-01.md`
    // sec.2, "Keywords with tooltips: Bomb, Set off, Spark, Mine").

    /// <summary>
    /// Rule 1, the word a player reads on nearly every card.
    ///
    /// TEXT PASS 2026-09-25 (the owner: "the existing text is often very
    /// verbose and unintuitive"). Three short sentences: what a Bomb deals,
    /// how it grows, and the jump. The edge cases the old tip carried --
    /// Block stops it, only Vulnerable and the HP cap move it, a second Bomb
    /// stacks beside the first -- are dropped on purpose: they are learned by
    /// playing, and the live number is on the badge. The growth is still
    /// interpolated from its Law constant (`EB-89`). The history of the old
    /// wording is in git.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBomb(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BombKey,
            "Deals its size in [gold]Pyro[/gold] damage when "
          + "[gold]Set off[/gold]. Grows " + KleeOverhaulLaw.BombGrowth
          + " at the start of your turn. If its enemy dies, it jumps to "
          + "another.");

    /// <summary>
    /// Rule 2, the word [USER] named ("Set Off has no tooltip text"). The
    /// order inside the pile (`EB-432`, oldest first) and the aim of a random
    /// Set off (`EB-516`) stay; the text pass of 2026-09-25 dropped the Block,
    /// when-hit and aura clauses as edge cases a player learns by playing.
    /// </summary>
    public static IEnumerable<IHoverTip> ForSetOff(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SetOffKey,
            "Every [gold]Bomb[/gold] on the enemy goes off, oldest first. "
          + "A random Set off picks an enemy with Bombs.");

    /// <summary>Rule 4. The gain rate is read from
    /// <see cref="KleeOverhaulLaw.SparkPerExplosion"/>, which is also
    /// Pounding Surprise's whole body under this arm.</summary>
    public static IEnumerable<IHoverTip> ForSpark(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SparkKey, SparkBody());

    /// <summary>
    /// THE ONE SENTENCE THAT IS NOT THE SAME IN BOTH KLEE ARMS, so it is the
    /// one clause this body decides at runtime rather than printing flat.
    ///
    /// The Sparks arm's rows print `Spark` too (twelve faces of them, from
    /// `Second Helping` to `True Spark Knight`), and under THAT arm the gain
    /// is Pounding Surprise's -- a relic's body, not a kit rule -- so the
    /// overhaul's "you gain one whenever a Bomb goes off" would be a rule
    /// stated about an arm that does not have it. What both arms DO share is
    /// the rest of rule 4, and it is exactly what `SparkPower`'s own retired
    /// face says ("a resource; cards that print a Spark price spend it"): the
    /// alternative cost is live in every prototype build, because
    /// `SparkPower.BaseRuleActive` is `false` whenever `PROTOTYPE_CARDS` is
    /// defined. So the shared clauses are unconditional and the kit rule joins
    /// them only under the arm that owns it.
    /// </summary>
    private static string SparkBody()
    {
        const string word =
            "Some cards cost [gold]Sparks[/gold] instead of Energy, with no cap. ";
        const string shared = "Gone after combat.";
        // R242 pick 1 put the opening bank INTO rule 4, and the tip is where a
        // player meets the word: a Spark-priced card in an opening hand is
        // exactly the moment the r4 seat found unplayable by construction, and
        // the sentence that fixes it belongs beside the one that was already
        // there rather than on a relic the player may not have read.
        return word + "Start each combat with " + KleeOverhaulLaw.OpeningSpark
             + ". " + shared;
    }

    /// <summary>
    /// Rule 6. A Mine IS a Bomb, so the one thing this word adds is when else
    /// it goes off. The text pass of 2026-09-25 dropped "the hit still lands
    /// unless the Mine kills" and the Bomb tip's edge cases; the Bomb tip
    /// prints beside this one on every face that says Mine. 2026-10-03: a
    /// blind seat read a Mine as failing because a Set off had already spent
    /// it, so the tip now says a Set off spends it too.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off just before its enemy "
          + "attacks. Any [gold]Set off[/gold] spends it too.");

    /// <summary>
    /// `EB-446`. A NAME ON ONE FACE THAT BELONGS TO ANOTHER CARD.
    ///
    /// THE GAP. <i>Fischl -- Nightrider</i> prints "If Oz is out, he deals 5
    /// Electro damage to a random enemy" and nothing on the screen says what
    /// puts Oz out. The r7 seat played the card five times and never learned
    /// it: the word reads as an undefined keyword, and the thing it actually
    /// names is a DIFFERENT companion card -- the Power <i>Fischl -- Oz, at
    /// Your Side</i> -- which that run never held and may never be offered.
    ///
    /// SO THE TIP NAMES THE POWER, which is the one fact the reader is missing
    /// and cannot derive. `Grounded`'s shape exactly (`EB-372`): a word one
    /// card is written against, defined on the face that prints it rather than
    /// on the card that grants it, because the attach travels with the WORD
    /// (`gen_klee_cards.arm_keyword_tip_calls`) and not with the deck.
    ///
    /// WHAT IT LEAVES TO THE CARDS. How much Oz deals and for how long are the
    /// two faces' own printed numbers, and both move on an upgrade, so the tip
    /// says what Oz IS and which card puts him out and stops there, the way
    /// `ForGrounded` leaves its Block number to the Power card's own line.
    /// </summary>
    /// `EB-504`, the second of the two words whose rule is Klee's: the Power
    /// that fields Oz is hers, and Fischl's face is drafted by every
    /// character. See <see cref="KleesRuleBelongsHere"/>.
    public static IEnumerable<IHoverTip> ForOz(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        !KleesRuleBelongsHere(card) ? inherited :
        With(inherited, OzKey,
            // A card TITLE is a plain word, never golded
            // (`docs/current/text-conventions.md`, and the lint bites), and
            // the title is quoted WITHOUT its `Fischl --` prefix because the
            // conventions ban a dash of any kind in player text.
            "Fischl's raven, out while you hold the Power Oz, at Your Side. "
          + "He makes an [gold]Electro[/gold]"
          + " hit at the end of your turn while he is out.");

    /// <summary>
    /// KLEE'S SIXTH, `EB-372`, AND IT IS A WORD THE KIT NAMES ON A FACE THE
    /// PLAYER MAY NEVER HAVE OWNED.
    ///
    /// THE GAP. `Grounded` is a Power of Klee's, and Kaeya's Cold-Blooded
    /// Strike is written against it -- "Next turn, Grounded pays even if you
    /// played a Set off card" (`EB-749`) -- as is the buff that card leaves
    /// behind
    /// (<see cref="KleeMod.Powers.ColdBloodedPower"/>). A player who drafted
    /// Kaeya without ever drafting Grounded meets the word on a card face with
    /// nothing anywhere on the screen saying what it is, and the r9 seat read
    /// it as noise in both acts (act 1 sec.(c) 3, act 2 sec.(c) 2).
    ///
    /// IT TRAVELS WITH THE WORD AND NOT WITH THE DECK. The attach is derived
    /// from the printed face (`gen_klee_cards.arm_keyword_tip_calls`), so
    /// Kaeya carries the definition because Kaeya prints the word -- whether or
    /// not the run holds Grounded, which is the state the seat was actually in.
    ///
    /// WHAT IT SAYS AND WHAT IT LEAVES TO THE CARD. The CONDITION is the whole
    /// rule and it is what a Kaeya reader needs: `EB-749` (R271 sec.5.1) moved
    /// it to "you played no Set off card last turn" and the tip moved with it.
    /// It names what Grounded pays (2026-10-02: a seat that never drafted the
    /// Power could not read "its card prints what it pays"): the Spark off
    /// <see cref="KleeOverhaulLaw.GroundedSpark"/>, and Block with no number,
    /// because the upgrade moves the Block.
    ///
    /// KAEYA'S OWN CLAUSE MOVED WITH IT, as a TEXT correction and not a rule
    /// change: the force-pay it describes is untouched, and the sentence now
    /// says what that force-pay does against the condition Grounded actually
    /// has.
    /// </summary>
    /// ONE METHOD WITH AN OPTIONAL CARD, and not an overload: a POWER raises
    /// this tip too -- the buff Kaeya's card leaves behind prints the word for
    /// the rest of the turn, after the card itself has gone -- and every other
    /// attach here ignores its `card` argument anyway. A second entry point
    /// would be a second thing for `ArmKeywordTipTests`' structural pin to
    /// count, and it is the pin that proves every tip goes through `With`.
    public static IEnumerable<IHoverTip> ForGrounded(
        IEnumerable<IHoverTip> inherited, CardModel? card = null) =>
        With(inherited, GroundedKey,
            // A card TYPE is a plain word, never golded
            // (`docs/current/text-conventions.md`, and the lint bites).
            "A Power that gives [gold]Block[/gold] and "
          + KleeOverhaulLaw.GroundedSpark + " [gold]Spark[/gold] at the "
          + "start of your turn, but only if you played no "
          + "[gold]Set off[/gold] card last turn.");

    // ---------------------------------------------------------- Kokomi -----
    //
    // Her TWO, and the slice's own rules section is what makes it two
    // (`review/active/kokomi-overhaul-slice-1-2026-09-01.md` draft 6 sec.2,
    // "Keywords with tooltips: Plan, Mend"). Draft 2 printed six; Tide, Surge,
    // Exert and Garment left with the rules they named.

    /// <summary>
    /// THE 2026-09-25 TEXT PASS, and it is the owner's ask in so many words:
    /// "the existing text is often very verbose and unintuitive". This tip was
    /// the worst string in the kit -- 292 rendered characters against the
    /// 135-character ceiling, four sentences, read under every Kokomi card --
    /// and it carried six seats' edge cases (Strength folding, Vulnerable
    /// timing, "a carry-out is not a hit", non-Minion targeting, standing
    /// Block, the badge as a count). They LEFT the tip and nothing replaced
    /// them: the word now says what a Plan is and in what order Plans happen.
    /// The long forms stay where there is room for them, on the blind-play
    /// panel (`blindplay_notes.PLAN_AIM_NOTE`, `PLAN_BLOCK_NOTE`,
    /// `PLAN_COUNT_NOTE`, `PLAN_WRITTEN_NUMBER_NOTE`), and the history of each
    /// clause is in git. The Dusk timing is stated only on
    /// <see cref="ForDusk"/>. Spec and census:
    /// `review/records/text-pass-2026-09-25/`.
    ///
    /// "INSTEAD OF THE LINE ABOVE" (the status batch, 2026-10-01,
    /// review/active/kokomi-status-batch-2026-10-01.md sec.3, pick 2; [USER]:
    /// "Agreed on the Plan text change"). Both seats on the 78-card build
    /// planned a card expecting its now-line too, so the face prints
    /// "Or plan:" and the tip opens by saying the two halves are a choice.
    /// The second sentence was shortened to keep the tip under 135.
    ///
    /// A PLAN STAYS OPEN (2026-10-01, ruled;
    /// review/active/kokomi-delay-pays-2026-10-01.md), pick 5 (a): "Plans
    /// carry out on their Plan line; click a waiting Plan to flip it." The
    /// Bake-Kurage carries a two-line Plan out as either line; no screen.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "Instead of the line above, play the card on the "
          + "[gold]Bake-Kurage[/gold]: it happens next turn. Click it to flip "
          + "lines. Plans go in the order made.");

    /// <summary>
    /// `EB-643` (R265), THE POOL PASS'S ONE NEW WORD, and it is a rule about
    /// WHEN and nothing else: a Dusk Plan is carried out at the END of the turn
    /// it was written on, before the enemies act, instead of at the start of
    /// her next one.
    ///
    /// A WORD OF ITS OWN RATHER THAN A CLAUSE ON <see cref="ForPlan"/>, for
    /// two reasons and either would do. The Plan tip was at its 135-character
    /// ceiling when this word was added, and since the 2026-09-25 text pass
    /// this tip is the ONE place the Dusk timing is stated. And
    /// the two rows that print the word print it in place of "Plan:", so the
    /// player meets `Dusk` where a definition can sit beside it.
    ///
    /// "BEFORE ENEMIES ACT" IS THE LOAD-BEARING HALF and it is why the whole
    /// rule fits in one sentence: everything else about a Dusk Plan is a Plan
    /// (it is written by playing the card on the jellyfish, it is one entry in
    /// one queue, Change of Plans can still hurry it, the plan bus still rings
    /// on it), and the tip beside this one says all of that. What a player cannot
    /// get from anywhere else is that the Block arrives in time for the swing.
    /// </summary>
    public static IEnumerable<IHoverTip> ForDusk(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, DuskKey,
            "[gold]Dusk[/gold]: the [gold]Bake-Kurage[/gold] carries this "
          + "[gold]Plan[/gold] out at the end of this turn, before enemies "
          + "act.");

    /// <summary>
    /// `EB-378`: WHERE THE AURA CAME FROM, on the rows whose element is the
    /// jellyfish's and not the card's.
    ///
    /// <see cref="KokomiPlan.ResolveAll"/> deals every damaging Plan clause as
    /// <c>ElementalHit.Deal(..., Element.Hydro, ...)</c> whatever the card's
    /// type, so `Kurage's Oath` -- a SKILL -- leaves a Hydro aura on every
    /// enemy it takes, and the sim's twin does the same
    /// (<c>tier0/engine/kokomi_plan</c>, <c>element="hydro"</c>). The round-9
    /// act-1 seat watched that aura appear "from a card whose face says nothing
    /// about an element", and priced no reaction off it.
    ///
    /// R276 PICK 2 RETIRED THE SPLIT THIS SENTENCE USED TO EXPLAIN. It read
    /// "Its own hit applies no aura; the Bake-Kurage carries out the Plan as a
    /// Hydro hit, which does", because her damaging Skills applied nothing
    /// face-up. Under the arm every damaging card of hers applies Hydro, Skills
    /// included (<see cref="CatalystCadence.EveryDamagingCardCarriesElement"/>),
    /// so a row with a face-up hit carries the gem and no sentence.
    ///
    /// ATTACHED ONLY WHERE THE PLAN IS THE CARD'S ONLY HIT -- Kurage's Oath,
    /// Ambush and Feigned Retreat since R276 pick 1: the face-up half blocks,
    /// so the gem
    /// (which means "this face-up hit applies the element", `EB-713`) is not
    /// theirs to wear, and this says the carry-out still lands Hydro.
    /// `gen_klee_cards.emit` raises it from <c>plan_applies_element</c> and
    /// not <c>elemental</c>.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlanElement(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanElementKey,
            "The [gold]Bake-Kurage[/gold] carries out this [gold]Plan[/gold] "
          + "as a [gold]Hydro[/gold] hit: it applies [gold]Hydro[/gold].");

    /// <summary>
    /// `EB-709`: HOW MANY PLANS A DOUBLED CARRY-OUT IS, on the card that
    /// doubles it.
    ///
    /// THE FIND (Kokomi r31 lane 2, (c)). Tide Wall paid 6 and then 9 under
    /// Second Wave, and the seat could not tell from any face whether the
    /// doubled entry counted as one Plan or two for a per-Plan clause. It
    /// counts as TWO, and that is not a choice this row made:
    /// <see cref="KokomiPlan.ResolveAll"/> arms a drain-local counter and
    /// every later carry-out draws off it (`EB-501`, `EB-718`), so Scout
    /// Ahead -> Second Wave -> Battle Plan draws 3.
    ///
    /// ON SECOND WAVE AND NOT ON THE PER-PLAN READERS, which is the whole
    /// point of the row. A reader's own face states its rate truthfully; what
    /// no face said is that ONE card can make the queue longer than the queue
    /// looks. The card that bends the count is where the count is explained,
    /// and it is derived from the clause rather than declared per row, so a
    /// second doubler would carry the sentence the day its row exists.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlanTwice(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanTwiceKey,
            "A [gold]Plan[/gold] carried out twice counts as two. Every "
          + "clause that counts [gold]Plans[/gold] carried out pays for "
          + "both.");

    /// <summary>
    /// THE BOUND IS THE WHOLE POINT OF THIS ROW'S SECOND HALF. The Casket read
    /// as broken at full HP because a Mend at the ceiling does nothing and
    /// nothing on screen said there was a ceiling. The sentence is
    /// <see cref="KokomiRules.Mend"/>'s own ("never above the HP you entered
    /// the fight with"), so the rule and its only explanation are one line
    /// apart. 2026-09-28 (Kokomi seat): "the HP you entered the fight with"
    /// was read beside Yumemizuki's "HP over 70%" as a Max-HP figure; "the HP
    /// you had at the start of this combat" names the cap as a moment.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MendKey,
            "[gold]Mend N[/gold]: heal N HP, but never above the HP you had "
          + "at the start of this combat.");

    /// <summary>
    /// `EB-625`. WHAT THE CASKET IS, on every face that names it -- by its
    /// full name (Shell Guard) or, since the Casket pass (2026-09-28), by the
    /// short one ("the Casket gains 2", "for each point in the Casket").
    ///
    /// THE CASKET PASS REWROTE THE SENTENCE with the relic: it used to be the
    /// debuff strike, and the relic now COUNTS the Plans the Bake-Kurage
    /// carries out. "Your relic" first, which is the half the relic's own face
    /// cannot say; then what fills it and what empties it. The per-Plan number
    /// is read off <see cref="KokomiOverhaulLaw.CasketPerPlan"/>, the constant
    /// the relic adds.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCasket(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CasketKey,
            "Your relic. Each [gold]Plan[/gold] the [gold]Bake-Kurage[/gold] "
          + "carries out adds " + KokomiOverhaulLaw.CasketPerPlan + ". "
          + "[gold]Open the Casket[/gold] turns the count into "
          + "[gold]Strength[/gold].");

    /// <summary>
    /// THE CASKET PASS (2026-09-28). The token the Tamakushi Casket deals into
    /// her opening hand, on the face that names it (What the Tokoyo Returns).
    /// Its own card text, restated, because the card is in no pool and a
    /// player may meet the name before the card.
    /// </summary>
    public static IEnumerable<IHoverTip> ForOpenTheCasket(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, OpenTheCasketKey,
            "1-cost, Retain. Gain [gold]Strength[/gold] equal to the "
          + "Casket's count, then empty it.");

    /// <summary>
    /// `EB-575`. THE BOARD THIS CARD NEEDS, AND WHAT IT DOES WITHOUT IT.
    ///
    /// THE DEFECT (Klee r21 lane 1, (c) 2 and (c) 3). A `Set off` row and the
    /// merge are PLAYABLE with no Bomb on the field: the game takes the
    /// Energy, takes the Spark where one is priced, and resolves nothing at
    /// all. The seat played Careful Arrangement onto a bare board and called
    /// it "a blank that the game charges you for", and the contrast is on the
    /// same screen -- a Spark-priced card the bank is short for prints CANNOT
    /// BE PLAYED and names the price and the bank.
    ///
    /// A RIDER AND NOT A REFUSAL, which is a design fact rather than an
    /// implementation one: setting off nothing is a legal, sometimes correct
    /// play (Bang Bang! places a Bomb, Countdown draws), so what is owed is
    /// the sentence, not a block. Furina's Companion cards carry the same
    /// shape for the same reason
    /// (<see cref="KleeMod.Cards.FurinaRiderTips.ForCompanionPerform"/>,
    /// "No member on stage: performs nobody").
    ///
    /// TWO BODIES, BECAUSE TWO THINGS ARE TRUE. A row with a line of its own
    /// -- Fwoosh!'s 6 damage, Countdown's draw -- still does that line, and
    /// saying "does nothing" there would be false. A row that is nothing BUT
    /// the Bomb work (Careful Arrangement, The Big One, Quick Fuse, Fireworks
    /// Show) does nothing whatever, and saying "only its own line" would send
    /// a player looking for a line that is not there. Which body a card gets
    /// is DERIVED from its effects in `gen_klee_cards.empty_field_tip_arg`, so
    /// a row that gains a line gains the other sentence with it.
    ///
    /// LIVE, AND SILENT WHEN THE FIELD IS NOT EMPTY: it is a sentence about
    /// THIS board, so it prints only while the board is in the state it names,
    /// and nothing at all off a creature or out of combat.
    /// </summary>
    public static IEnumerable<IHoverTip> ForEmptyField(
        IEnumerable<IHoverTip> inherited, CardModel card, bool ownLine)
    {
        if (!FieldIsEmptyFor(card)) return inherited;
        return ownLine
            ? With(inherited, EmptyFieldKey,
                "No [gold]Bomb[/gold] on the field: this card is only its own "
              + "line.")
            : With(inherited, EmptyFieldKey,
                "No [gold]Bomb[/gold] on the field: this card does nothing.");
    }

    /// <summary>
    /// `EB-573`. WHAT THE MERGE KEEPS BESIDES THE MINE.
    ///
    /// THE FIND (Klee r21 lane 1, (c) 4). "A Bomb 21 that was Jumpy's Bomb 8
    /// two merges and two turns ago still dropped Mine 3 on ALL when it went
    /// off. This is a GOOD interaction and a large part of the kit's ceiling,
    /// and it is completely undiscoverable except by accident. Careful
    /// Arrangement's face says the merged charge is 'a Mine if any of them
    /// was'; it says nothing about riders."
    ///
    /// THE CARD SAYS IT AND THE BADGE COUNTS IT. This sentence is the RULE, on
    /// the card that does the merging, where a player decides whether to
    /// merge; <c>ProtoBombPower.RiderSentence</c> is the live number, on the pile
    /// the rule produced. Neither is enough alone -- the rule is unreadable off
    /// a number and the number is unreachable before the play.
    ///
    /// STATIC, unlike <see cref="ForEmptyField"/>: it is a fact about the CARD
    /// and true in a reward screen and a shop as well as in a fight.
    ///
    /// ATTACHED BY THE MERGE OP, not by name
    /// (`gen_klee_cards.reads_the_field`'s sibling), so a second merge row
    /// carries the sentence the day its row exists.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMergeRiders(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MergeRidersKey,
            "The merged [gold]Bomb[/gold] keeps every rider its charges "
          + "carried, and their riders add up.");

    /// <summary>
    /// `EB-575`'s question, on its own so a pin can ask it. Is there a board
    /// here, and is this player's field empty of Bombs?
    ///
    /// THE OWNER'S COMBAT AND NOT THE CARD'S. `CardModel.CombatState` walks the
    /// card's PILE to find one and throws off a board -- it is the read the
    /// headless boundary bites on -- while the owning creature carries the same
    /// answer and answers null out of combat, which is the case this guard
    /// exists for: a reward screen or a deck view has no field to be empty.
    ///
    /// `AnyPlacedBy` IS THE SAME READ the Set off rows' playability gate makes
    /// (R205-scoped: her own charges, on a living body), so the sentence cannot
    /// disagree with the card it rides. It was Grounded's read too until
    /// `EB-749` moved that condition onto the CARDS the player played.
    /// </summary>
    public static bool FieldIsEmptyFor(CardModel? card)
    {
        var owner = TipOwner.CreatureOf(card);
        if (owner?.CombatState == null) return false;
        return !ProtoBombPower.AnyPlacedBy(owner);
    }

    // ------------------------------------------------------- companions ----

    /// <summary>
    /// The companion arm's one invented-looking word, and it is not invented:
    /// `Swirl` is the shared Anemo reaction, printed as a VERB by ten Mondstadt
    /// and Inazuma Universals ("Swirl an enemy's aura"). The eight reaction
    /// PREVIEWS already in <see cref="KleeKeywords"/> are board-aware and
    /// appear only while a matching aura is out, so a face that prints the word
    /// over an aura-less board explained nothing. The sentence is the shipped
    /// preview row's, restated for the verb.
    /// </summary>
    public static IEnumerable<IHoverTip> ForSwirl(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SwirlKey,
            // THE ELEMENT PORT (sec.4 A, 2026-09-28): the preview row's rule,
            // restated for the verb.
            // Amended 2026-10-01: an aura the spread finds already there
            // refreshes. Reworded the same day (the open-Oath round: two
            // seats misread "old ones refresh").
            // Element identities (2026-10-01; the Varka round read it two
            // ways): the flat damage is unblockable
            // (`ReactionEffects.SwirlPays`, `ValueProp.Unblockable`).
            // 2026-10-03, spent auras removed ([USER]: "It seems to generate
            // confusion." ... "agreed ... please proceed"): Swirl removes
            // the aura and the copies are ordinary auras.
            "[gold]Anemo[/gold] meets an aura: remove it, deal "
          + Elements.ReactionConstants.SwirlDamage
          + " unblockable damage to ALL enemies, and apply that element to the others.");

    /// <summary>
    /// 2026-09-25, the afternoon Klee seat round. The Opus seat: "Companion is
    /// never defined on screen, yet three offered cards trigger on it"
    /// (Witches' Circle, Come Back and Play!, Friendship Bracelet). The word is
    /// golded on every face that prints it, so the tip attaches off the
    /// printed word like every row in this class. The seat page's
    /// `Companion` row opens with the same sentence.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCompanion(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CompanionKey,
            "A card titled with a character's name, a dash, then its "
          + "own.");

    // ---------------------------------------------------- Varka -----------

    /// <summary>
    /// WHAT HIS CARDS CHARGE (the Oath rework, sec.3): one count per element.
    /// Applying and Swirling each credit once per card (`TryCredit`); the old
    /// "1 of each, per card" read as one per element (the Varka Oath round). Printed on every Oath reader and on Boreas's Fang.
    /// <paramref name="card"/> may be null for the relic's hover.
    /// </summary>
    public static IEnumerable<IHoverTip> ForOath(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, OathKey,
            "1 Oath per element a card applies, plus 1 per element it "
          + "[gold]Swirls[/gold]. Kept all fight. Element cards read their "
          + "own; others, the current.");

    /// <summary>
    /// THE ONE ELEMENT HIS CARDS READ (sec.3), and what his Swirls pay for
    /// it. The numbers are <see cref="VarkaLaw"/>'s, the ones his badge
    /// prints.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCurrentElement(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, CurrentElementKey,
            "The last Pyro, Hydro, Cryo or Electro you applied. "
          + "Swirls pay it: Pyro " + VarkaLaw.SwirlPyroDamage + " damage, Hydro "
          + VarkaLaw.SwirlHydroBlock + " [gold]Block[/gold], Cryo "
          + VarkaLaw.SwirlCryoVulnerable + " [gold]Vulnerable[/gold], Electro "
          + VarkaLaw.SwirlElectroDamageAll + " to ALL.");

    /// <summary>
    /// ELEMENT IDENTITIES sec.7 (2026-10-01): "The card's hover says
    /// 'Switches your element to Pyro' when it would." Attached by the
    /// codegen to every Varka row whose play makes an element current
    /// (<c>gen_klee_cards.varka_switch_element</c>), and printed only while it
    /// would switch now (<see cref="VarkaOath.WouldSwitchTo"/>): in a fight,
    /// another element current, and for a non-Knight no Unwavering Banner.
    /// </summary>
    public static IEnumerable<IHoverTip> ForElementSwitch(
        IEnumerable<IHoverTip> inherited, CardModel card, Element element)
    {
        if (!VarkaOath.WouldSwitchTo(card, element)) return inherited;
        return With(inherited, ElementSwitchKey,
            "Switches your [gold]current element[/gold] to " + element + ".");
    }

    /// <summary>His personal Companions (sec.6), named on Knightly Guard,
    /// Grand Master's Order, Knights' Roll Call and the rest.
    /// CO-OP NOTES PICK 2 (2026-10-02): every Knight now prints "Knight." as
    /// its first line (<see cref="KleeKeywords.Knight"/>, which shares this
    /// key), so the colon is no longer the only tell and the sentence no
    /// longer leans on it. The keyword's description row and this body are
    /// one constant, <see cref="KnightTipText"/>: the card that IS a Knight
    /// and the card that names one hover the same tip. "(except Geo)" is
    /// Noelle: a Geo Knight sets no element, because Geo keeps no Oath
    /// (<see cref="VarkaOath.BeginPlay"/>).
    /// </summary>
    public static IEnumerable<IHoverTip> ForKnight(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, KnightKey, KnightTipText);

    /// <summary>The Knight tip's one sentence ([USER], co-op notes pick 2,
    /// 2026-10-02). INTERNAL, not public: every public string constant here
    /// is a tip key (`ArmKeywordTipTests`).</summary>
    internal const string KnightTipText =
        "One of Varka's Companions. "
      + "Playing one makes its element your current element (except Geo).";

    // ---------------------------------------------------- Furina ----------
    //
    // THE REFRAME'S FOUR ARE GONE (`EB-723`, R269). `Deploy`, `Evoke`, `Drain`
    // and `Encore` left this class with the eleven `proto_fr_` rows that
    // printed them (Encore's last body with R276's hygiene, once nothing
    // called it): the Stage brief's sec.2 retires that arm by name, R213 B's
    // deletion rule took its rows off `docs/prototype-surface.yaml`, and a
    // tooltip for a word no row prints is a definition of a mechanic that is
    // not there (draft 6's precedent, one character over). The rest of the
    // reframe's C# stands until the branch that owns both halves takes it.
    //
    // WHAT REPLACED THEM is the STAGE's seven, at the foot of this class.

    /// <summary>
    /// One tip, appended after whatever the card already carries.
    ///
    /// APPENDED RATHER THAN PREPENDED so a card's own live-arithmetic riders
    /// (the Charge rate, a reaction preview) stay at the
    /// top of the stack: those say what THIS play will do, and a definition of
    /// a word is the thing you read second.
    /// </summary>
    private static IEnumerable<IHoverTip> With(
        IEnumerable<IHoverTip> inherited, string key, string body)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(new LocString(Table, key + ".title"), body);
    }

    /// <summary>
    /// `EB-504`. IS THERE A KLEE IN THIS RUN FOR KLEE'S RULE TO BE ABOUT?
    ///
    /// THE ROW WAS CLOSED ONCE ON THE PAGE GLOSSARY AND REOPENED ON THE CARD.
    /// The Companion Spark rider rides companion faces the whole roster can
    /// draft (it was the `Hexerei` word until R276); `Oz` is named by Fischl's face, which
    /// every character meets, and the Power that fields him is hers. So the
    /// WORD reaches every run and the RULE reaches one.
    /// `blindplay_notes._ARM_KEYWORD_CHARACTER` gated the page's own glossary
    /// on the r17 finding, and the r18 lane-2 seat then met the same sentence
    /// on Razor's own card: "two Companion cards in a Kokomi run printed
    /// 'Hexerei -- ... Cards of hers pay when you play one.' I could not tell
    /// what is paid, by whom, or whether it applies to me at all, so I refused
    /// both cards partly on that." The card's tip is a second printer.
    ///
    /// THE OWNER FIRST, BECAUSE IT IS THE ONE THAT IS ALWAYS RIGHT. A card in
    /// a hand or a deck belongs to a seat and that seat has a character; only
    /// where there is no owner -- a shelf, a reward, a compendium page -- does
    /// this fall back to the run's player list, which is the same question one
    /// scope out and the one that answers in co-op.
    ///
    /// SILENCE IS NOT EVIDENCE, and it is the page's own direction here
    /// (`absent is not zero`): where NOTHING says who is playing, the rule
    /// prints. A missing tooltip on a Klee run would be the worse failure of
    /// the two, and it is the one this returns true to avoid.
    /// </summary>
    public static bool KleesRuleBelongsHere(CardModel card)
    {
        var inRun = KleeAmongTheRunsPlayers();
        Player? owner = null;
        try
        {
            // A canonical (compendium) copy asserts on `Owner` rather than
            // answering null -- `KokomiPlan.PlanDamageVar`'s guard, verbatim.
            if (card.IsMutable) owner = card.Owner;
        }
        catch (System.Exception)
        {
            owner = null;
        }
        if (owner != null)
        {
            return owner.Character is IKleeCharacter || (inRun ?? false);
        }
        return inRun ?? true;
    }

    /// <summary>Is any seat in this run playing Klee, or does nothing answer?
    /// A state read must never throw (<c>PlayTelemetry.NameOf</c> takes the
    /// same posture), and outside a run there is nothing to read.</summary>
    private static bool? KleeAmongTheRunsPlayers()
    {
        try
        {
            var players = RunManager.Instance?.DebugOnlyGetState()?.Players;
            if (players == null) return null;
            return players.Any(p => p?.Character is IKleeCharacter);
        }
        catch (System.Exception)
        {
            return null;
        }
    }

    // ------------------------------------------- Furina, the Stage --------
    //
    // THE RE-FOUNDING (2026-10-04, review/active/furina-refounding-2026-10-03.md).
    // Short and plain: one or two sentences each, the rule and nothing else.
    // The performers' tips are their badges' sentences
    // (<see cref="StagePerformerBadge.ActText"/>), numbers from
    // <see cref="FurinaStageLaw"/> (`EB-89`).

    /// <summary>Rule 5: a card's Spend N takes N of her Fanfare, and is
    /// offered only when she has it.</summary>
    public static IEnumerable<IHoverTip> ForSpend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SpendKey,
            "Pay that much [gold]Fanfare[/gold]. Offered only if you have "
          + "enough.");

    /// <summary>THE SPEND WARNING, on a Spend mode's face in the chooser: the
    /// stars this Spend would leave unable to pay for their act this turn.
    /// No tip where nobody is left short.</summary>
    public static IEnumerable<IHoverTip> ForSpendShortfall(
        IEnumerable<IHoverTip> inherited, CardModel card, int amount)
    {
        var names = StrandedNames(card, amount);
        return names.Length == 0 ? inherited : With(inherited, SpendShortKey,
            "After this Spend, " + names + " can't pay to act this turn.");
    }

    /// <summary>"Neuvillette", "Neuvillette and Clorinde", "A, B and C";
    /// empty where the Spend strands nobody or the card has no owner yet. A
    /// tip read must never throw.</summary>
    private static string StrandedNames(CardModel card, int amount)
    {
        try
        {
            if (!card.IsMutable || card.Owner?.Creature is not { } owner)
            {
                return "";
            }
            var names = FurinaStage.StrandedBySpend(owner, amount)
                .Select(FurinaStageLedger.DisplayName).ToList();
            if (names.Count <= 1) return names.FirstOrDefault() ?? "";
            return string.Join(", ", names.Take(names.Count - 1))
                 + " and " + names[^1];
        }
        catch (System.Exception)
        {
            return "";
        }
    }

    /// <summary>Rule 5: Fanfare is one number on Furina.</summary>
    public static IEnumerable<IHoverTip> ForFanfare(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FanfareKey,
            "Your applause. Cards and Bows give it. [gold]Spend[/gold] and "
          + "stars' acts use it. It never fades.");

    /// <summary>Rule 3: the free Bow act, then 1 Fanfare.</summary>
    public static IEnumerable<IHoverTip> ForBow(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BowKey,
            "The performer acts once more without paying, then you gain "
          + FurinaStageLaw.BowFanfare + " [gold]Fanfare[/gold].");

    /// <summary>Rule 7: the chosen performer acts now.</summary>
    public static IEnumerable<IHoverTip> ForCue(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CueKey,
            "Choose a performer. It acts now. A star pays as usual.");

    /// <summary>Rule 6: the stage's scaling.</summary>
    public static IEnumerable<IHoverTip> ForRehearsal(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, RehearsalKey,
            "Each one makes your performers' damage and [gold]Block[/gold] "
          + "acts deal 1 more.");

    /// <summary>The seat that acts first at the end of the turn.</summary>
    public static IEnumerable<IHoverTip> ForFrontPerformer(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FrontPerformerKey,
            "The performer in the first seat. Performers act front to back "
          + "at the end of your turn.");

    /// <summary>Arkhe Alignment's damage half.</summary>
    public static IEnumerable<IHoverTip> ForOusia(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, OusiaKey,
            "This turn, your performers' acts deal double damage.");

    /// <summary>Arkhe Alignment's other half (sec.8: "Gain 2 Fanfare").
    /// </summary>
    public static IEnumerable<IHoverTip> ForPneuma(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PneumaKey,
            "Gain " + Powers.ArkheAlignmentPower.PneumaFanfare
          + " [gold]Fanfare[/gold].");

    /// <summary>Rules 2 and 4: where a summon goes, and overflow.</summary>
    public static IEnumerable<IHoverTip> ForSummon(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SummonKey,
            "A performer joins at the back. On a full stage, the front Salon "
          + "member [gold]Bow[/gold]s and leaves first. Guests keep their "
          + "seats.");

    public static IEnumerable<IHoverTip> ForUsher(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, UsherKey, StagePerformerBadge.ActText(StagePerformer.Usher));

    public static IEnumerable<IHoverTip> ForChevalmarin(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ChevalmarinKey,
             StagePerformerBadge.ActText(StagePerformer.Chevalmarin));

    public static IEnumerable<IHoverTip> ForCrabaletta(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CrabalettaKey,
             StagePerformerBadge.ActText(StagePerformer.Crabaletta));

    /// <summary>The Guest Star keyword: one of each; a second copy Bows it.
    /// </summary>
    public static IEnumerable<IHoverTip> ForGuestStar(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, GuestStarKey,
            "One of each on stage. Summoning one already there makes it "
          + "[gold]Bow[/gold] and stay.");

    public static IEnumerable<IHoverTip> ForNeuvillette(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NeuvilletteKey,
             StagePerformerBadge.ActText(StagePerformer.Neuvillette));

    public static IEnumerable<IHoverTip> ForClorinde(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ClorindeKey,
             StagePerformerBadge.ActText(StagePerformer.Clorinde));

    public static IEnumerable<IHoverTip> ForNavia(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NaviaKey,
             StagePerformerBadge.ActText(StagePerformer.Navia));

    public static IEnumerable<IHoverTip> ForChevreuse(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ChevreuseKey,
             StagePerformerBadge.ActText(StagePerformer.Chevreuse));

    public static IEnumerable<IHoverTip> ForWriothesley(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, WriothesleyKey,
             StagePerformerBadge.ActText(StagePerformer.Wriothesley));

    public static IEnumerable<IHoverTip> ForSigewinne(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SigewinneKey,
             StagePerformerBadge.ActText(StagePerformer.Sigewinne));

    public static IEnumerable<IHoverTip> ForCharlotte(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CharlotteKey,
             StagePerformerBadge.ActText(StagePerformer.Charlotte));

    public static IEnumerable<IHoverTip> ForLynette(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LynetteKey,
             StagePerformerBadge.ActText(StagePerformer.Lynette));

    public static IEnumerable<IHoverTip> ForLyney(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LyneyKey,
             StagePerformerBadge.ActText(StagePerformer.Lyney));

    public static IEnumerable<IHoverTip> ForEscoffier(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, EscoffierKey,
             StagePerformerBadge.ActText(StagePerformer.Escoffier));
}
