using System.Collections.Generic;
using System.Linq;
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
    public const string SwirlKey = "KLEEMOD-ARM_SWIRL";
    // 2026-09-25 (the afternoon Klee seats): `Companion` is printed golded on
    // Klee's readers and on the Kokomi and Furina arms' faces, and nothing on
    // screen said what one is.
    public const string CompanionKey = "KLEEMOD-ARM_COMPANION";
    // THE FURINA STAGE'S SEVEN (`EB-723`, R269). The brief's sec.12 names
    // them: "Spend, Fanfare (the bar), Raise, Bow, the lead, the back
    // performer, Rotate". `Fanfare` collides with the reframe's word by
    // spelling and not by meaning -- there it is a meter, here it is a
    // performer's own bar -- so it takes its own key rather than reusing one
    // that would render the retired arm's sentence.
    //
    // THE TEXT PASS (2026-09-25) retired `Raise` and `Rotate` and renamed the
    // lead to the FRONT performer (review/records/furina-text-pass-2026-09-25.md):
    // their keys left with them, and the front seat took a key of its own so
    // no stale loc title can survive under the old one.
    public const string SpendKey = "KLEEMOD-ARM_STAGE_SPEND";
    public const string FanfareKey = "KLEEMOD-ARM_STAGE_FANFARE";
    public const string BowKey = "KLEEMOD-ARM_STAGE_BOW";
    public const string FrontPerformerKey = "KLEEMOD-ARM_STAGE_FRONT";
    public const string BackPerformerKey = "KLEEMOD-ARM_STAGE_BACK";
    // R276 batch two: Arkhe Alignment's two halves.
    public const string OusiaKey = "KLEEMOD-ARM_STAGE_OUSIA";
    public const string PneumaKey = "KLEEMOD-ARM_STAGE_PNEUMA";
    // 2026-09-25: WHAT A SUMMON DOES AND WHAT EACH PERFORMER DOES. A
    // first-time co-op player "found it very hard to understand ... what each
    // summoned actor actually did". Not golded words: a face prints "Summon
    // Usher", so these attach off the row's `stage_summon` op
    // (`gen_klee_cards.stage_summon_tip_calls`), the way the readers' rider
    // attaches off its multiplier.
    public const string SummonKey = "KLEEMOD-ARM_STAGE_SUMMON";
    public const string UsherKey = "KLEEMOD-ARM_STAGE_USHER";
    public const string ChevalmarinKey = "KLEEMOD-ARM_STAGE_CHEVALMARIN";
    public const string CrabalettaKey = "KLEEMOD-ARM_STAGE_CRABALETTA";
    // THE GUEST CAST (2026-09-25): the Guest Star keyword and one tip per
    // guest, attached off the row's `stage_guest` op
    // (`gen_klee_cards.stage_guest_tip_calls`) the way the trio's are. A key
    // of its own, not the shipped Guest Star generator's: that is another
    // rule under the same two words.
    public const string GuestStarKey = "KLEEMOD-ARM_STAGE_GUEST_STAR";
    public const string NeuvilletteKey = "KLEEMOD-ARM_STAGE_NEUVILLETTE";
    public const string ClorindeKey = "KLEEMOD-ARM_STAGE_CLORINDE";
    public const string NaviaKey = "KLEEMOD-ARM_STAGE_NAVIA";
    public const string ChevreuseKey = "KLEEMOD-ARM_STAGE_CHEVREUSE";
    public const string WriothesleyKey = "KLEEMOD-ARM_STAGE_WRIOTHESLEY";
    public const string SigewinneKey = "KLEEMOD-ARM_STAGE_SIGEWINNE";
    public const string CharlotteKey = "KLEEMOD-ARM_STAGE_CHARLOTTE";
    public const string LynetteKey = "KLEEMOD-ARM_STAGE_LYNETTE";

    // `EB-378`. NOT A KEYWORD, and the only key here that is not: it titles a
    // RIDER on the rows whose element arrives with the jellyfish rather than
    // with the play. It lives in this class because it is a sentence about the
    // Plan, which is this class's word and this quarantine's rule.
    public const string PlanElementKey = "KLEEMOD-ARM_PLAN_ELEMENT";

    // `EB-709`. A RIDER AND NOT A KEYWORD, beside `PlanElementKey` for that
    // key's reason: it is a sentence about the one card that doubles a
    // carry-out, printed where that card is met.
    public const string PlanTwiceKey = "KLEEMOD-ARM_PLAN_TWICE";

    // `EB-418`. THE SECOND KEY HERE THAT TITLES NO KEYWORD, and it names the
    // one Spark income no screen in the game stated: `KleeCompanionSpark`
    // ("Little Hexenzirkul"), the kit rule LAW:145 obliges Klee's own KIT to
    // declare because a Companion card may not print a signature resource on
    // its own face. It sits beside `PlanElementKey` for that key's reason --
    // it is a sentence about the CARD in hand, printed where that card is met.
    public const string CovenSparkKey = "KLEEMOD-ARM_COVEN_SPARK";

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
        if (!KleeOverhaul.Enabled) return word + shared;
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
    /// prints beside this one on every face that says Mine.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off just before its enemy "
          + "attacks.");

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
    /// `ForGrounded` defers its payout to the Power card's own line.
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
    /// What Grounded pays for that is the Power card's own printed line and
    /// moves with its upgrade, so the tip defers to it rather than quoting a
    /// number that a second card would contradict.
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
            "A Power that pays at the start of your turn, but "
          + "only if you played no [gold]Set off[/gold] card last turn. Its "
          + "card prints what it pays.");

    /// <summary>
    /// `EB-418`, AND IT IS THE ONE NUMBER IN THE KIT A SEAT COULD NOT READ OFF
    /// THE SCREEN.
    ///
    /// THE GAP. <see cref="KleeMod.Powers.KleeCompanionSpark"/> -- "Little
    /// Hexenzirkul" -- mints a Spark on every play of one of Klee's OWN
    /// Personal Companions, and it is printed nowhere: LAW:145 forbids the
    /// Companion card from carrying the grant on its face ("Companion cards may
    /// not themselves grant signature resources"), so the rule moved WHOLE into
    /// her kit at `EB-219` and the sentence did not move with it. The
    /// companions packet says so in as many words -- "the kit already pays a
    /// rider neither card prints" -- and the r11 Opus seat met the consequence
    /// as the only unreadable number in five fights: "My Spark went 1 to 2 with
    /// no bomb going off... This is the one number in the kit I could not read
    /// off the screen."
    ///
    /// WHERE IT HAPPENS IS THE CARD, so that is where it prints. The Spark
    /// keyword tip is full -- four sentences and 130 of its 135 characters
    /// since R242 put the opening bank in it -- and in any case it is met on a
    /// Spark-priced Attack rather than on the Companion that pays. A rider on
    /// the Companion's own face is read at the moment the energy is committed,
    /// which is the moment the seat's read was wrong.
    ///
    /// THE THREE LIMBS ARE THE POWER'S OWN, interpolated from the constants the
    /// grant reads (`EB-89`) so a repricing cannot leave this sentence lying.
    /// The CAP is deliberately not printed: it is the sum of the three limbs
    /// (<see cref="KleeMod.Powers.KleeCompanionSpark.MaxPerPlay"/>), so a
    /// fourth clause would state a bound no reachable play can meet.
    /// </summary>
    /// R276 PICK 2: THE RIDER NAMES ANY COMPANION. `EB-642` had pointed it at
    /// the printed Hexerei word; R276 retired the word and every Companion card
    /// pays, so the sentence says "a Companion card" -- the same set
    /// <see cref="KleeMod.Powers.KleeCompanionSpark.PaysKleesSpark"/> tests
    /// under the arm -- and it rides every companion face on Klee's profile.
    /// IT ASKS <see cref="KleesRuleBelongsHere"/>, because a Universal is
    /// drafted by every character, and Klee's rule on a Kokomi shop screen is
    /// `EB-504` exactly.
    ///
    /// 2026-09-23: UNDER THE ARM IT PRINTS NOTHING, because under the arm a
    /// Companion play no longer pays (<see cref="KleeMod.Powers.KleeCompanionSpark"/>,
    /// [USER]: "...worth decreasing now to go back to the old levels and then
    /// see if play is Spark-constrained"). A rider promising income the kit
    /// does not pay is the `EB-418` defect turned inside out. Off the arm it
    /// is unchanged.
    public static IEnumerable<IHoverTip> ForCovenSpark(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        KleeOverhaul.Enabled || !KleesRuleBelongsHere(card) ? inherited :
        With(inherited, CovenSparkKey,
            "Playing a [gold]Companion[/gold] card gives Klee [blue]"
          + KleeCompanionSpark.Base + "[/blue] [gold]Spark[/gold], [blue]"
          + KleeCompanionSpark.ReactionBonus + "[/blue] more if it triggered "
          + "an [gold]Elemental Reaction[/gold] and [blue]"
          + KleeCompanionSpark.UpgradedBonus
          + "[/blue] more if it is upgraded.");

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
    /// NO "INSTEAD", on the coordinator's follow-up: a Plan-only row has no
    /// normal play to be instead of (the r2 seat's finding, `EB-293`), and
    /// "carried out" is the kit's own verb for a Plan where "goes off" is the
    /// Bomb's.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "Play the card on the [gold]Bake-Kurage[/gold] and this happens "
          + "at the start of your next turn. Plans are carried out in the "
          + "order you made them.");

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
    /// one queue, Change of Plans can still hurry it, Treatise still draws on
    /// it), and the tip beside this one says all of that. What a player cannot
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
    /// apart.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MendKey,
            "[gold]Mend N[/gold]: heal N HP, never above the HP you entered "
          + "the fight with.");

    /// <summary>
    /// `EB-625`. WHAT THE CASKET IS, on every face that names it.
    ///
    /// THE FIND ([USER]'s Kokomi act-1 run, 2026-09-07). `Shell Guard` reads
    /// "whenever the [gold]Tamakushi Casket[/gold] strikes" and nothing on
    /// screen says what the Casket is or what makes it strike -- so the card's
    /// whole payout hangs off a proper noun the player has met only as a relic
    /// name. It is `Grounded` and `Oz` one kit over: a face written against a
    /// thing it cannot itself introduce.
    ///
    /// THE RELIC'S OWN SENTENCE, WORD FOR WORD, because the relic already
    /// prints the rule and two spellings of one rule is how a player learns
    /// there are two rules. The number is read off
    /// <see cref="KokomiOverhaulLaw.CasketStrike"/> -- the same constant the
    /// relic's face interpolates and <see cref="TamakushiCasket.Strike"/>
    /// deals -- so a retune cannot leave this quoting a retired number.
    ///
    /// AND IT SAYS "your relic" FIRST, which is the half the relic's own face
    /// cannot say: a player reading Shell Guard in a shop has to know where to
    /// look for the thing before the rule means anything.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCasket(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CasketKey,
            "Your relic. Each debuff you apply is a "
          + KokomiOverhaulLaw.CasketStrike + " [gold]Hydro[/gold] hit on that "
          + "enemy: it reacts, takes its [gold]Vulnerable[/gold], and re-arms "
          + "[gold]Hydro[/gold].");

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
            "The enemy's aura is consumed and copied onto ALL enemies. No "
          + "aura, no effect.");

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
    // Her FIVE seat words since the text pass (2026-09-25; the brief's sec.12
    // once made it seven, with `Raise` and `Rotate`): the faces print
    // `Spend`, `Fanfare`, `Bow`, `front performer` and `back performer`, and
    // every one of them names a rule the SHIPPED engine does not have. A shipped Fanfare is a METER on the player; here
    // it is a performer's own bar, and the two sentences contradict each other
    // on every face -- which is exactly why these live here, behind
    // `PrototypeCards`, and not in <see cref="SalonMemberTips"/>.
    //
    // THE NUMERALS ARE INTERPOLATED FROM <see cref="FurinaStageLaw"/> (`EB-89`),
    // so a retune cannot leave one of these sentences quoting a retired number.

    /// <summary>
    /// Brief sec.3 rule 8 as R276 ruled it: the BACK performer pays, and the
    /// price is paid in full or the Spend mode is not offered. A performer
    /// the Spend empties takes a bow, which the Bow tip now says for every
    /// way of reaching 0 (rule 7, 2026-09-25).
    /// </summary>
    public static IEnumerable<IHoverTip> ForSpend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SpendKey,
            // `EB-746`: SPEND IS A CHOICE ON PLAY. Four of six round-two
            // seats said the card spent for them -- "no verb to decline",
            // "the card decided" -- so the wager brief sec.4 describes never
            // happened at play time. The old last clause goes with the
            // rider: an empty stage does not refuse a Spend now, it simply
            // does not OFFER the mode, which the player meets on the
            // choose-a-card screen rather than in a tip.
            // R276 picks 1 and 2: the bank pays, and only in full.
            // The text pass (2026-09-25): the chooser explains itself (#662),
            // so the tip says what is paid and by whom. The bow clause left
            // with rule 7's 2026-09-25 change: the Bow tip covers it.
            "Pay Fanfare from your [gold]back performer[/gold]. Offered only "
          + "if it can pay in full.");

    /// <summary>
    /// Brief sec.2: "Fanfare is the performer's bar itself ... no counter
    /// beside it." TWO SENTENCES BECAUSE IT IS TWO FACTS, and the second is
    /// the damage order (rule 6), which is the reason a player cares what the
    /// bar is at all.
    /// </summary>
    public static IEnumerable<IHoverTip> ForFanfare(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FanfareKey,
            // The text pass's follow-up (2026-09-25): the EMPTY-STAGE
            // summon lives here, on the word every Fanfare-giving face
            // prints -- Hold Your Places and Gala Dinner carry no back
            // performer tip. "At 0 it leaves" is dropped on purpose.
            "A performer's health. Hits take your [gold]Block[/gold], then "
          + "the front performer's, then you. Gained on an empty stage, it "
          + "summons a performer.");

    /// <summary>
    /// Brief sec.3 rules 7 and 9 together. Since 2026-09-25 a performer at 0
    /// Fanfare bows whatever emptied it -- a Spend, a hit or a full-stage
    /// summon ([USER]: "Stage members bow out when they are destroyed or
    /// replaced, not just when you deliberately spend them down to 0").
    /// </summary>
    public static IEnumerable<IHoverTip> ForBow(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BowKey,
            // Draft 3 (2026-09-25, the Stage review's pick 1): the Bow is the
            // performer's own act once more, so the tip says that and no
            // performer's tip carries a separate Bow. Rule 7's trigger (any
            // exit at 0 Fanfare) is unchanged. THE GUEST CAST (2026-09-25):
            // a guest's act may pay, and its Bow does not -- stated once,
            // here, for every performer.
            "A performer that leaves the stage acts one last time on its way "
          + "out, without paying.");

    /// <summary>
    /// Brief sec.3 rules 4 and 6: the front seat is the one that regenerates
    /// and the one that is hit -- the SHIELD, in R276's words -- and both
    /// facts are about the same seat, which is why one sentence can carry
    /// them.
    /// </summary>
    public static IEnumerable<IHoverTip> ForFrontPerformer(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FrontPerformerKey,
            "Takes hits first. Regains " + FurinaStageLaw.LeadRegen
          + " [gold]Fanfare[/gold] at the start of your turn.");

    /// <summary>
    /// Brief sec.3 rules 5, 6 and 8, from the other end. The back seat is the
    /// BANK (R276): a Raise fills it and a Spend draws from it. Rule 6: the
    /// front absorbs and the rest reaches Furina, so a hit never runs on to
    /// the middle or back seat.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBackPerformer(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BackPerformerKey,
            // `EB-744`: "nothing hits it" WHERE A FLURRY DOES. Rule 6 is
            // per ATTACK -- the lead absorbs one hit up to its bar and leaves
            // at 0, so the next attack of the same turn meets whoever stepped
            // forward. ROUND FOUR: "no single attack reaches it" was still
            // read as "the back is safe", and seats lost the back performer
            // to a second attack in one enemy turn. So the sentence says
            // plainly where hits go, and when they reach the back.
            // The text pass (2026-09-25): the empty-stage summon the
            // retired Raise tip carried is the Fanfare tip's now.
            // Draft 3 (2026-09-25): rule 12, the fade, on the seat it hits.
            // THE GUEST ROUND (2026-09-25, 0.2.3794): "Hits reach it last"
            // was false -- rule 6 never runs a hit on past the front -- and
            // the Opus seat lost Wriothesley's plan to it. A lone performer
            // is both the front and the back, so it is hit then.
            "Gains and Spends [gold]Fanfare[/gold]. Hits reach it only when "
          + "it stands alone. At "
          + "the end of your turn, it loses half its Fanfare above "
          + FurinaStageLaw.FadeThreshold + ".");

    /// <summary>R276 batch two: <i>Arkhe Alignment</i>'s damage half, the
    /// choice a player makes at the start of each turn.</summary>
    public static IEnumerable<IHoverTip> ForOusia(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, OusiaKey,
            "This turn, your performers' acts deal double damage.");

    /// <summary>R276 batch two: <i>Arkhe Alignment</i>'s Block half. The
    /// numeral is <see cref="Powers.ArkheAlignmentPower.PneumaLeadRegain"/>'s
    /// (`EB-89`).</summary>
    public static IEnumerable<IHoverTip> ForPneuma(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PneumaKey,
            "This turn, your performers' acts give double [gold]Block[/gold], "
          + "and your front performer gains "
          + Powers.ArkheAlignmentPower.PneumaLeadRegain
          + " [gold]Fanfare[/gold].");

    /// <summary>
    /// 2026-09-25. WHAT A SUMMON DOES, on every card that summons. ONE
    /// sentence since the trio can be cloned (2026-09-25; [USER]: "Let's
    /// allow for copies and then check the balance."): a named summon always
    /// summons, so named and random summons meet a full stage the same way --
    /// the front performer Bows and leaves and the newcomer ADDS its own
    /// arrival Fanfare to the leaver's (<c>FurinaStage.RecastFromFront</c>). Until then a named Common's face
    /// said what a performer already on stage did, and this tip came in two
    /// variants so as not to contradict it.
    /// </summary>
    public static IEnumerable<IHoverTip> ForSummon(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SummonKey,
            // 2026-09-25 night (the granted-guest seat round): lane 2 only
            // understood "adds its Fanfare" from the log.
            "A performer joins at the back with "
          + FurinaStageLaw.SummonFanfare + " [gold]Fanfare[/gold]. On a full "
          + "stage, the front one [gold]Bow[/gold]s and leaves its Fanfare "
          + "to the newcomer.");

    /// <summary>
    /// 2026-09-25. GENTILHOMME USHER'S ACT, on every card that names him and
    /// on every random summon. The same sentence his body's badge carries
    /// (<c>UsherBadgePower</c>), numbers from <see cref="FurinaStageLaw"/>
    /// (`EB-89`). No Bow clause since draft 3 (2026-09-25): a Bow is the act
    /// once more, which the Bow tip says once for all three.
    /// </summary>
    public static IEnumerable<IHoverTip> ForUsher(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, UsherKey,
            "End of your turn: gain " + FurinaStageLaw.ActUsherBlock
          + " [gold]Block[/gold].");

    /// <summary>2026-09-25. SURINTENDANTE CHEVALMARIN'S ACT, the same
    /// sentence as <c>ChevalmarinBadgePower</c>. Plain damage since draft 3
    /// (2026-09-25): no act applies Hydro.</summary>
    public static IEnumerable<IHoverTip> ForChevalmarin(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ChevalmarinKey,
            "End of your turn: deal " + FurinaStageLaw.ActChevalmarinDamage
          + " damage to ALL enemies.");

    /// <summary>2026-09-25. MADEMOISELLE CRABALETTA'S ACT, the same sentence
    /// as <c>CrabalettaBadgePower</c>. Plain damage since draft 3.</summary>
    public static IEnumerable<IHoverTip> ForCrabaletta(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CrabalettaKey,
            "End of your turn: deal " + FurinaStageLaw.ActCrabalettaDamage
          + " damage to a random enemy.");

    // ------------------------------------------- the Guest Cast -----------
    //
    // 2026-09-25, review/active/furina-guest-batch-2026-09-25.md. A Guest Star
    // card prints "<Name> joins the stage with N Fanfare." and its act lives
    // on the performer's tip and badge, Defect-orb style, not on the face.
    // Each tip below is word for word the build table's, numerals from
    // `FurinaStageLaw` (`EB-89`), and the same sentence as the guest's badge.

    /// <summary>The Guest Star keyword: a guest is a performer, one of each
    /// on stage, and a second copy makes it Bow and return with the new
    /// Fanfare added ([USER], 2026-09-25: "only one Neuvillette allowed -
    /// repeats trigger a Bow and then resummon them, carrying over unused
    /// Fanfare").</summary>
    public static IEnumerable<IHoverTip> ForGuestStar(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, GuestStarKey,
            "A performer who joins the stage, one of each. A second copy "
          + "makes it Bow, then return with the new Fanfare added.");

    public static IEnumerable<IHoverTip> ForNeuvillette(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NeuvilletteKey,
            "End of your turn: pay " + FurinaStageLaw.ActNeuvillettePrice
          + " of his Fanfare to deal " + FurinaStageLaw.ActNeuvilletteDamage
          + " [gold]Hydro[/gold] damage to ALL enemies.");

    public static IEnumerable<IHoverTip> ForClorinde(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ClorindeKey,
            "End of your turn: take " + FurinaStageLaw.ActClorindeTax
          + " Fanfare from each other performer to deal "
          + FurinaStageLaw.ActClorindeDamage
          + " [gold]Electro[/gold] damage to a random enemy.");

    public static IEnumerable<IHoverTip> ForNavia(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NaviaKey,
            "End of your turn: deal [gold]Geo[/gold] damage equal to her "
          + "Fanfare to a random enemy.");

    public static IEnumerable<IHoverTip> ForChevreuse(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ChevreuseKey,
            "End of your turn: [gold]Spend[/gold] "
          + FurinaStageLaw.ActChevreusePrice + " to gain "
          + FurinaStageLaw.ActChevreuseEnergy
          + " [gold]Energy[/gold] next turn.");

    public static IEnumerable<IHoverTip> ForWriothesley(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, WriothesleyKey,
            "End of your turn: deal [gold]Cryo[/gold] damage to a random "
          + "enemy equal to twice the Fanfare he lost to hits since his "
          + "last act.");

    public static IEnumerable<IHoverTip> ForSigewinne(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SigewinneKey,
            "End of your turn: give " + FurinaStageLaw.ActSigewinneGift
          + " of her Fanfare to the performer behind her, or to your front "
          + "performer if she is at the back.");

    public static IEnumerable<IHoverTip> ForCharlotte(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CharlotteKey,
            "End of your turn: each other performer gains "
          + FurinaStageLaw.ActCharlotteGift + " [gold]Fanfare[/gold].");

    public static IEnumerable<IHoverTip> ForLynette(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LynetteKey,
            // 2026-09-25 night (the granted-guest seat round): the act always
            // lands, and Swirls where it finds an aura.
            "End of your turn: deal " + FurinaStageLaw.ActLynetteDamage
          + " [gold]Anemo[/gold] damage to a random enemy, one with an aura "
          + "if any.");
}
