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
/// `EB-272`: the PROTOTYPE ARMS' KEYWORDS, defined once each.
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
/// <see cref="KokomiRiderTips"/>. It lives under `Cards/Prototype/` beside
/// the arms' powers, because these sentences describe the arms' rules and
/// several of them quote a `*OverhaulLaw` constant.
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

    /// <summary>The loc table every arm tip title lives in, for the
    /// Masterpiece's per-layer tips (review r3). A property, so the key scan
    /// (public string constants) never counts it as a key.</summary>
    public static string KeywordTable => Table;

    // The keys. `KLEEMOD-ARM_` and not the bare word, because two of these
    // words already have a SHIPPED keyword with a DIFFERENT rule: `Bomb` is
    // `KLEEMOD-BOMB` (the shipped Bomb, whose keyword left with the text pass
    // of 2026-10-08) and `Swirl` is `KLEEMOD-SWIRL_PREVIEW` (a board-aware
    // preview, raised only while a matching aura is out). A shared key would have made
    // one arm silently overwrite the other's definition at the loc merge.
    public const string BombKey = "KLEEMOD-ARM_BOMB";
    public const string SetOffKey = "KLEEMOD-ARM_SET_OFF";
    public const string SparkKey = "KLEEMOD-ARM_SPARK";
    public const string MineKey = "KLEEMOD-ARM_MINE";
    public const string OzKey = "KLEEMOD-ARM_OZ";
    public const string MendKey = "KLEEMOD-ARM_MEND";
    public const string PlanKey = "KLEEMOD-ARM_PLAN";
    // (`Dusk`, `Tamakushi Casket` and `Open the Casket` left with the rules
    // they named, the Kokomi re-founding, 2026-10-12.)
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
    // The card text pass (2026-10-12): Boreas's Fang's reshuffle clause,
    // moved off the relic's face into this hover.
    public const string AscensionReturnKey = "KLEEMOD-ARM_VARKA_ASCENSION_RETURN";
    // Design-session call (2026-10-13), A RIDER AND NOT A KEYWORD: Four
    // Winds' Ascension's element hit gains no Oath, and that is the rule.
    public const string AscensionNoOathKey = "KLEEMOD-ARM_VARKA_ASCENSION_NO_OATH";
    // The Furina wave (2026-10-13), A RIDER AND NOT A KEYWORD: Final Bow's
    // acts happen one after another.
    public const string FinalBowInTurnKey = "KLEEMOD-ARM_STAGE_FINAL_BOW_IN_TURN";
    // Klee text-only fixes (2026-10-13), RIDERS AND NOT KEYWORDS: what four
    // faces left a seat unsure of, each read off the code.
    public const string BigBaddaBoomTotalKey = "KLEEMOD-ARM_KLEE_BIG_BADDA_BOOM_TOTAL";
    public const string BoomBadgeTurnKey = "KLEEMOD-ARM_KLEE_BOOM_BADGE_TURN";
    public const string LionsFangLastTurnKey = "KLEEMOD-ARM_KLEE_LIONS_FANG_LAST_TURN";
    public const string PassTheMatchActingKey = "KLEEMOD-ARM_KLEE_PASS_THE_MATCH_ACTING";
    // ELEMENT IDENTITIES sec.7 (2026-10-01): a rider that titles no keyword,
    // a fact about THIS card on THIS board -- playing it would switch his
    // current element. Four times in one round a seat lost the Oath it was
    // building to a card of another element and noticed only later.
    public const string ElementSwitchKey = "KLEEMOD-ARM_VARKA_ELEMENT_SWITCH";
    // FURINA, THE SALON'S TAB (2026-10-05). The faces print `Spend`,
    // `Fanfare`, `Drain` and `Repay`; a Guest Star card carries the guest's
    // own tip off its `stage_guest` op (`gen_klee_cards.stage_guest_tip_calls`).
    public const string SpendKey = "KLEEMOD-ARM_STAGE_SPEND";
    public const string FanfareKey = "KLEEMOD-ARM_STAGE_FANFARE";
    public const string DrainKey = "KLEEMOD-ARM_STAGE_DRAIN";
    public const string RepayKey = "KLEEMOD-ARM_STAGE_REPAY";
    // FURINA, THE SWEEP (2026-10-14): Ousia / Pneuma's two faces.
    public const string FlipKey = "KLEEMOD-ARM_STAGE_FLIP";
    // THE SPEND OUTLET PAPER (2026-10-12), and NOT A KEYWORD ROW: a rider on
    // her starter spend-all, the card two seats played for 0 to 4 damage.
    public const string BankDamageKey = "KLEEMOD-ARM_STAGE_BANK_DAMAGE";
    public const string SummonKey = "KLEEMOD-ARM_STAGE_SUMMON";
    public const string GuestStarKey = "KLEEMOD-ARM_STAGE_GUEST_STAR";
    public const string CharlotteKey = "KLEEMOD-ARM_STAGE_CHARLOTTE";
    public const string WriothesleyKey = "KLEEMOD-ARM_STAGE_WRIOTHESLEY";
    public const string LynetteKey = "KLEEMOD-ARM_STAGE_LYNETTE";
    public const string ClorindeKey = "KLEEMOD-ARM_STAGE_CLORINDE";
    public const string LyneyKey = "KLEEMOD-ARM_STAGE_LYNEY";
    public const string SigewinneKey = "KLEEMOD-ARM_STAGE_SIGEWINNE";
    public const string ChevreuseKey = "KLEEMOD-ARM_STAGE_CHEVREUSE";
    // The pool to 75's four guests (2026-10-09).
    public const string OldestGuestKey = "KLEEMOD-ARM_STAGE_OLDEST_GUEST";
    public const string FreminetKey = "KLEEMOD-ARM_STAGE_FREMINET";
    public const string NaviaKey = "KLEEMOD-ARM_STAGE_NAVIA";
    public const string NeuvilletteKey = "KLEEMOD-ARM_STAGE_NEUVILLETTE";
    public const string EscoffierKey = "KLEEMOD-ARM_STAGE_ESCOFFIER";
    // THE TEXT PASS OF 2026-10-08: three golded words that hovered nothing.
    // `Elemental Reaction` is printed on 13 faces across every kit; `Sakura`
    // and `Lightfall Sword` are placed objects with badges, the shape Bomb and
    // Mine already have.
    public const string ElementalReactionKey = "KLEEMOD-ARM_ELEMENTAL_REACTION";
    public const string SakuraKey = "KLEEMOD-ARM_SAKURA";
    /// <summary>YAE MIKO (2026-10-13): her two words, Sakura (on
    /// <see cref="SakuraKey"/>, read for her cards) and Edit.</summary>
    public const string EditKey = "KLEEMOD-ARM_YAE_EDIT";
    /// <summary>YAE MIKO (2026-10-14): Tenko, split out of her Sakura tip;
    /// review r3 (ruled 2026-10-14) made it one plain rule again.</summary>
    public const string TenkoKey = "KLEEMOD-ARM_YAE_TENKO";
    /// <summary>YAE MIKO, REVIEW R3 (ruled 2026-10-14): the two Sakura kinds
    /// a card names, and the full-shrine plant every planting card carries.
    /// </summary>
    public const string FoxfireSakuraKey = "KLEEMOD-ARM_YAE_FOXFIRE_SAKURA";
    public const string KitsuneSakuraKey = "KLEEMOD-ARM_YAE_KITSUNE_SAKURA";
    public const string FullShrineKey = "KLEEMOD-ARM_YAE_FULL_SHRINE";
    public const string LightfallSwordKey = "KLEEMOD-ARM_LIGHTFALL_SWORD";

    // THE TEXT PASS OF 2026-10-08, and NOT A KEYWORD ROW: the Plan tip a
    // PLAN-ONLY card carries in place of <see cref="PlanKey"/>. That tip
    // opens "Play this line ... instead" and says "click to flip lines"; a
    // plan-only card has no line above and nothing to flip (Kokomi review,
    // 2026-10-08, sec.5). Same title, so the hover still reads "Plan".
    public const string PlanOnlyKey = "KLEEMOD-ARM_PLAN_ONLY";

    // THE KOKOMI ROUND-1 FIXES (2026-10-12), and NOT A KEYWORD ROW: the Plan
    // tip a card carries when its face NAMES Plans but prints no Plan line of
    // its own (Press the Advantage, Treatise, Breakwater ...). PlanKey's
    // "Instead of the line above, play it on the Bake-Kurage" told a seat
    // Press the Advantage could be written, and the jellyfish refused it.
    // Same title, so it reads "Plan".
    public const string PlanNoLineKey = "KLEEMOD-ARM_PLAN_NO_LINE";

    // `EB-378`. NOT A KEYWORD, and the only key here that is not: it titles a
    // RIDER on the rows whose element arrives with the jellyfish rather than
    // with the play. It lives in this class because it is a sentence about the
    // Plan, which is this class's word and this arm's rule.
    public const string PlanElementKey = "KLEEMOD-ARM_PLAN_ELEMENT";

    // `EB-709`. A RIDER AND NOT A KEYWORD, beside `PlanElementKey` for that
    // key's reason: it is a sentence about the one card that doubles a
    // carry-out, printed where that card is met.
    public const string PlanTwiceKey = "KLEEMOD-ARM_PLAN_TWICE";

    // KOKOMI ROUND 2 (2026-10-12), A RIDER AND NOT A KEYWORD: Nereid's
    // Ascension carries its first Plan out twice, and a seat could not tell
    // that the Plan's debuffs double too.
    public const string NereidsTwiceKey = "KLEEMOD-ARM_PLAN_TWICE_DEBUFFS";

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
    /// playing, and the live number is on the badge. Vulnerable came back
    /// (2026-10-18, suite 6 lane 5: no page said an enemy's Vulnerable
    /// raises a Bomb), and the jump lost "to another" to fit. The growth is still
    /// interpolated from its Law constant (`EB-89`). The history of the old
    /// wording is in git.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBomb(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BombKey,
            "Deals its size in [gold]Pyro[/gold] damage when "
          + "[gold]Set off[/gold]. [gold]Vulnerable[/gold] raises it. Grows by "
          + KleeOverhaulLaw.BombGrowth
          + " at the start of your turn. If its enemy dies, it jumps.");

    /// <summary>
    /// Rule 2, the word [USER] named ("Set Off has no tooltip text"). The
    /// order inside the pile (`EB-432`, oldest first) and the aim of a random
    /// Set off (`EB-516`) stay; the text pass of 2026-09-25 dropped the Block,
    /// when-hit and aura clauses as edge cases a player learns by playing.
    /// 2026-10-13 (text-only fix on main): a seat read Ka-pow!'s Set off as
    /// reaching past its target, so the tip says the other enemies' Bombs stay
    /// (<c>ProtoBombPower.SetOff</c> takes the target's pile only).
    /// </summary>
    public static IEnumerable<IHoverTip> ForSetOff(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SetOffKey,
            "Every [gold]Bomb[/gold] on the enemy goes off, oldest first. "
          + "Bombs on other enemies stay. "
          + "A random Set off picks an enemy with Bombs.");

    /// <summary>Rule 4. The gain rate is read from
    /// <see cref="KleeOverhaulLaw.SparkPerExplosion"/>, which is also
    /// Pounding Surprise's whole body under this arm. The opening bank is
    /// Klee's kit rule, so it is printed only to a Klee
    /// (<see cref="KleeOpensWithASpark"/>).</summary>
    public static IEnumerable<IHoverTip> ForSpark(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SparkKey, TipAudience.Seat
            ? SparkBody(KleeOpensWithASpark(card))
            : PlayerTips.SparkBody(KleeOpensWithASpark(card)));

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
    /// alternative cost is live in every build. So the shared clauses are
    /// unconditional and the kit rule joins
    /// them only under the arm that owns it.
    ///
    /// KLEE'S CARDS ON ANYONE (2026-10-04, [USER]: "Klee's cards need to work
    /// universally like Regent's"). The opening Spark is paid by Klee's kit
    /// (<c>KleeOverhaulOpening.GrantSpark</c>), not by her cards, so a card of
    /// hers in anyone else's hand prints the word and the price and not a bank
    /// that player will never be given. PUBLIC for the sweep in KleeTests.
    /// </summary>
    public static string SparkBody(bool openingBank)
    {
        const string word =
            "Some cards cost [gold]Sparks[/gold] instead of Energy, with no cap. ";
        const string shared = "Gone after combat.";
        // R242 pick 1 put the opening bank INTO rule 4, and the tip is where a
        // player meets the word: a Spark-priced card in an opening hand is
        // exactly the moment the r4 seat found unplayable by construction, and
        // the sentence that fixes it belongs beside the one that was already
        // there rather than on a relic the player may not have read.
        if (!openingBank) return word + shared;
        return word + "Start each combat with " + KleeOverhaulLaw.OpeningSpark
             + ". " + shared;
    }

    /// <summary>
    /// Rule 6. A Mine IS a Bomb, so the one thing this word adds is when else
    /// it goes off. The text pass of 2026-09-25 dropped "the hit still lands
    /// unless the Mine kills" and the Bomb tip's edge cases; the Bomb tip
    /// prints beside this one on every face that says Mine. 2026-10-03: a
    /// blind seat read a Mine as failing because a Set off had already spent
    /// it, so the tip now says a Set off spends it too. 2026-10-13 (text-only
    /// fix on main): an enemy's attack pops its Mines and leaves its plain
    /// Bombs (<c>ProtoBombPower.TakeMines</c>), and the tip now says so.
    /// 2026-10-23 ("On Klee - agreed on all."): the tip says a Mine uses up
    /// the enemy's aura, which it never did; "Otherwise, it waits" left. The
    /// ruled wording's parenthesis became its own sentence (rule 14).
    /// </summary>
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off by itself when its enemy "
          + "attacks you, using up the enemy's aura. The enemy's other Bombs "
          + "stay.");

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
    /// the retired `ForGrounded` left its Block number to the Power card's own line.
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
            "Fischl's raven. While you hold Oz, at Your Side, he makes an "
          + "[gold]Electro[/gold] hit at the end of your turn.");

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
    /// clause is in git. Spec and census:
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
    ///
    /// KOKOMI V2 SEATS (2026-10-18): two seats wrote Flank and Tide Wall
    /// expecting the enemy's intent as it stood, and the Plan read it the
    /// next morning. "and read enemies then" says when; to fit the 135
    /// ceiling the flip instruction left this tip, and it stays on the
    /// Bake-Kurage's own ("Click a waiting Plan to flip it."), where the
    /// flip is done.
    ///
    /// SAYS WHEN, AND THE FLIP IS BACK (2026-10-18,
    /// review/active/open-design-items-2026-10-18.md, ruled; [USER]: "Ok,
    /// agreed on all defaults"): "After enemies act and you draw" names the
    /// moment the Plans happen, which "next turn ... read enemies then" only
    /// implied, and "Click one to flip it." returns. 135 visible characters,
    /// the ceiling.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "Play it on the [gold]Bake-Kurage[/gold] instead. After enemies "
          + "act and you draw, Plans happen in order; [gold]Block[/gold] "
          + "lasts that turn. Click one to flip it.");

    /// <summary>The text pass of 2026-10-08: <see cref="ForPlan"/> for a
    /// card with no line above its Plan. Attached by
    /// <c>gen_klee_cards.emit</c> in ForPlan's place on a plan-only row.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlanOnly(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanOnlyKey,
            "Play the card on the [gold]Bake-Kurage[/gold]. Plans happen next "
          + "turn in order, and their [gold]Block[/gold] lasts that turn.");

    /// <summary>The Kokomi round-1 fixes (2026-10-12): <see cref="ForPlan"/>
    /// for a card that names Plans and has no Plan line, so cannot be
    /// written. Attached by <c>gen_klee_cards.emit</c> in ForPlan's place on
    /// a row with no <c>plan:</c>.</summary>
    public static IEnumerable<IHoverTip> ForPlanNoLine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanNoLineKey,
            "A card with a Plan line can be played on the "
          + "[gold]Bake-Kurage[/gold] to happen next turn. This card has no "
          + "Plan line.");

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
    /// face-up. Every such Skill of hers now prints Hydro and declares it on
    /// the card (Opening Gambit and Second Wave; since 2026-10-05 the element
    /// lives on the card, never on the character), so a row with a face-up
    /// hit carries the gem and no sentence.
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
    /// Kokomi round 2 (2026-10-12): on Nereid's Ascension, what "twice"
    /// covers. Its doubled carry-out doubled a Plan's debuffs and the Tainted
    /// it caused (Kokomi round 1, lane 3), and no face said so.
    /// `gen_klee_cards.emit` raises it off the row's
    /// <c>kk_nereids_ascension</c> power.
    /// </summary>
    public static IEnumerable<IHoverTip> ForNereidsTwice(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NereidsTwiceKey,
            "Twice means twice: the [gold]Plan[/gold]'s debuffs, and any "
          + "Tainted it causes, double too. A [gold]Plan[/gold] carried out "
          + "early is carried out once.");

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
    /// The text pass of 2026-10-08. The noun is golded on 13 faces across all
    /// four kits and hovered nothing; the board-aware previews in
    /// <see cref="KleeCardTooltips"/> say what each pair does, and appear only
    /// while an aura is out.
    /// </summary>
    public static IEnumerable<IHoverTip> ForElementalReaction(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ElementalReactionKey,
            "An element meets another element's aura on an enemy. The aura is "
          + "consumed and the pair's effect happens.");

    /// <summary>The text pass of 2026-10-08: Yae's placed totem, which has a
    /// badge (<c>SesshouSakuraPower</c>) and no tip. "Up to 3" is read at
    /// the fire, not the placing.</summary>
    ///
    /// YAE MIKO (2026-10-13): the same word on her own cards is her shrine,
    /// a different object (it levels and withers), so her cards and her
    /// Sakura badge carry her tip (<see cref="YaeSakuraTip"/>). Tenko was
    /// in this tip (pick 6 (a)) until [USER] (2026-10-14): "I think the
    /// Sakura tooltip is overly verbose, and Sakura and Tenko should be cut
    /// into separate tips" (<see cref="ForTenko"/>).
    public static IEnumerable<IHoverTip> ForSakura(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SakuraKey,
            card is ICharacterCard { CharacterId: Powers.YaePrototype.CharacterId }
                ? (TipAudience.Seat ? YaeSakuraTip + " " + YaeSakuraTargetRule : YaeSakuraTip)
                : "A totem that stays at your side all combat. At most 3 fire "
                + "each turn.");

    /// <summary>Yae's Sakura: the strike, the timer, the cap and the
    /// full-shrine plant (paper sec.2, shrine r2; the numbers are
    /// <see cref="Powers.YaeLaw"/>'s). [USER] (2026-10-14): "I still feel
    /// like that Sakura tooltip can be condensed further somehow". Shrine r2:
    /// a plant no longer levels the others; with 3 standing it refreshes and
    /// levels the oldest (<c>YaeShrineLedger.Plant</c>). Condensed
    /// 2026-10-14: the full-shrine rule is printed on the plant cards, and the
    /// cap moves with Sakura Channeling, so both leave the tip; "random"
    /// went to fit the 100-character cap. The Sakura Levels paper
    /// (<c>review/active/yae-sakura-levels-2026-10-17.md</c>, pick 1 (a),
    /// 2026-10-17): 1 + 2 per Level; "once more" became "again" to stay
    /// under the cap.</summary>
    public static readonly string YaeSakuraTip =
        $"At the end of your turn, strikes an enemy for {Powers.YaeLaw.SakuraBase} "
      + $"+ {Powers.YaeLaw.SakuraPerLevel} per Level. Lasts "
      + $"{Powers.YaeLaw.SakuraTurns} turns, then strikes again.";

    /// <summary>Yae review r6, item 5: which enemy a Sakura strikes
    /// (<c>YaeShrine.Aim</c>: the aim Kitsune Pounce passes, else the Lure,
    /// else Hunting Gaze's last enemy attacked (the refill, 2026-10-16), else
    /// random), in one sentence. The seat's hover adds it to
    /// <see cref="YaeSakuraTip"/>; the player's hover stays under the
    /// 100-character cap (<c>tools/lint_hover_tips.py</c>), where Foxfire
    /// Lure's and Kitsune Pounce's own faces say it. The page's twin is
    /// <c>blindplay_notes.SAKURA_TARGET_RULE</c>.</summary>
    public static readonly string YaeSakuraTargetRule =
        "A Sakura strikes Kitsune Pounce's target when Pounce makes it strike, "
      + "else the enemy Foxfire Lure marked this turn, else (with Hunting Gaze) "
      + "the last enemy your Attacks hit, else a random enemy.";

    /// <summary>
    /// YAE MIKO (2026-10-13): the Edit tip; Publish is the relic's word,
    /// said here once. It is the general rule only. [USER] (2026-10-14):
    /// "the 'Edit' tooltip seems unnecessarily long; no need to show the
    /// text for every possible edit if the card can only apply one." The
    /// Annotation a card applies is its own tip (<see cref="ForAnnotation"/>)
    /// and its own selection prompt (<c>YaeEditing.EditPromptTextFor</c>).
    /// </summary>
    public static IEnumerable<IHoverTip> ForEdit(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, EditKey, YaeEditTip);

    public static readonly string YaeEditTip =
        "Give a card an Annotation for this combat, replacing its last. "
      + "Published ones stay and add up.";

    /// <summary>One Annotation's tip key, titled by its name.</summary>
    public static string KeyOf(Powers.YaeAnnotation annotation) =>
        "KLEEMOD-ARM_YAE_" + annotation.ToString().ToUpperInvariant();

    /// <summary>
    /// The one Annotation a face names, titled by its name: its card reading
    /// (<c>YaeAnnotationText.Rule</c>), or its Sakura reading on a card that
    /// Edits a Sakura (<paramref name="onSakura"/>, from the row's own
    /// effect). Codegen attaches one per Annotation the face golds.
    /// </summary>
    public static IEnumerable<IHoverTip> ForAnnotation(
        IEnumerable<IHoverTip> inherited, CardModel? card,
        Powers.YaeAnnotation annotation, bool onSakura) =>
        With(inherited, KeyOf(annotation),
             Powers.YaeAnnotationText.TipBody(annotation, onSakura));

    /// <summary>
    /// YAE MIKO, REVIEW R3 (ruled 2026-10-14): Tenko is one plain rule
    /// again, the paper's words. The typed Tenko and its double effect left:
    /// one action per Sakura, and the mix of kinds decides what it does.
    /// </summary>
    public static IEnumerable<IHoverTip> ForTenko(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, TenkoKey, YaeTenkoTip);

    public static readonly string YaeTenkoTip =
        "Every [gold]Sakura[/gold] acts now. Refresh them to at least "
      + $"{Powers.YaeLaw.SakuraTurns} turns.";

    /// <summary>Review r3: a Foxfire Sakura, named on the card that plants
    /// one (Foxfire Sweep).</summary>
    public static IEnumerable<IHoverTip> ForFoxfireSakura(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, FoxfireSakuraKey, YaeFoxfireSakuraTip);

    public static readonly string YaeFoxfireSakuraTip =
        "A [gold]Sakura[/gold] that hits ALL enemies for "
      + $"{Powers.YaeLaw.FoxfireBase} + its Level when it acts.";

    /// <summary>Review r3: the decoy ("Yae does not shield. A fox illusion
    /// draws the blow."), named on Shrine Maiden's Guard.</summary>
    public static IEnumerable<IHoverTip> ForKitsuneSakura(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, KitsuneSakuraKey, YaeKitsuneSakuraTip);

    public static readonly string YaeKitsuneSakuraTip =
        "A fox decoy [gold]Sakura[/gold]. When it acts, you gain "
      + $"{Powers.YaeLaw.KitsuneBase} + its Level [gold]Block[/gold].";

    /// <summary>
    /// Review r3 (amended after GPT's review): the full-shrine plant by
    /// kind. It was printed on the plant cards ("with the shrine full, your
    /// oldest strikes, refreshes and gains a Level"); with kinds it has two
    /// branches, so every planting card carries it as a tip (codegen,
    /// off the row's plant op) instead.
    /// </summary>
    public static IEnumerable<IHoverTip> ForFullShrine(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, FullShrineKey, YaeFullShrineTip);

    /// <summary>Yae review r5, item 5: four of five seats could not read
    /// the short form until it bit them. The title says "Full shrine".
    /// The Sakura Levels paper (pick 1 (a), 2026-10-17): Levels carry over
    /// on a replace, so the new one starts at the higher of the two Levels.
    /// </summary>
    public static readonly string YaeFullShrineTip =
        "Planting makes the Sakura closest to withering act. Same kind: it "
      + "refreshes and gains a Level. Other kind: it withers, and the new "
      + "one takes its Level if higher.";

    /// <summary>The text pass of 2026-10-08: Eula's blade, a counter on the
    /// enemy (<c>LightfallSwordPower</c>) with a badge and no tip.</summary>
    public static IEnumerable<IHoverTip> ForLightfallSword(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LightfallSwordKey,
            "A blade hung over an enemy. Its badge counts down the turns "
          + "until it falls.");

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
    /// Wolf's Gravestone's Four Winds' Ascension (the Fang's until Starter
    /// (a), 2026-10-13) goes to the discard pile when played and comes back
    /// when he draws it. The card text pass
    /// (2026-10-12) moved the clause off the relic's face into this hover.
    /// </summary>
    public static IEnumerable<IHoverTip> ForAscensionReturn(
        IEnumerable<IHoverTip> inherited) =>
        With(inherited, AscensionReturnKey,
            "When played, it goes to your [gold]Discard Pile[/gold] and comes "
          + "back after a reshuffle.");

    /// <summary>
    /// Design-session call (2026-10-13): Four Winds' Ascension's element hit
    /// gains no Oath (<see cref="VarkaCards.AscensionHit"/> passes
    /// <c>credit: false</c>), where Barbara's hit does; a payoff does not feed
    /// its own scaling. `gen_klee_cards.emit` raises it off the row's
    /// <c>ascension_hit</c> effect.
    /// </summary>
    /// <summary>
    /// The Furina wave (2026-10-13, "To change now" 4): Final Bow's guest
    /// acts one act at a time, each resolving before the next
    /// (<c>StageDirector</c>'s act loop). A seat read
    /// "It acts twice" as one blow: the second kill set off the first kill's
    /// Crab Rage. `gen_klee_cards.emit` raises it off the row's
    /// <c>final_bow</c> effect.
    /// </summary>
    public static IEnumerable<IHoverTip> ForFinalBowInTurn(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FinalBowInTurnKey,
            "Its acts happen one after another, not all at once.");

    /// <summary>
    /// Klee text-only fix (2026-10-13): Big Badda Boom's second hit is
    /// <see cref="KleeMod.Powers.ProtoBombPower.DealSetOffTotal"/>, the
    /// ledger's total for THIS play only, counted before Block (each
    /// explosion's <c>ElementalHit.Deal</c> return), and a Boom Badge doubles
    /// the charge before it lands, so the total carries it once.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBigBaddaBoomTotal(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BigBaddaBoomTotalKey,
            "Only the [gold]Bombs[/gold] this card sets off count, including "
          + "damage to [gold]Block[/gold]. A doubled [gold]Bomb[/gold] counts "
          + "its doubled damage.");

    /// <summary>
    /// Klee text-only fix (2026-10-13): Boom Badge's card Retains, while
    /// <see cref="KleeMod.Powers.BoomBadgePower"/> is removed at the end of
    /// the turn it was played. A seat played it on a turn with no Set off.
    /// </summary>
    public static IEnumerable<IHoverTip> ForBoomBadgeTurn(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BoomBadgeTurnKey,
            "Retain keeps the card, not the doubling. The doubling lasts only "
          + "the turn you play it.");

    /// <summary>
    /// Klee text-only fix (2026-10-13): Lion's Fang reads
    /// <c>KleeOverhaulLedger.SetOffLastTurn</c>, a whole round, so a Mine
    /// answering an attack on the enemies' turn switches it off. A seat lost
    /// Jean+ to Dodoco+'s Mine and the face did not say why.
    /// </summary>
    public static IEnumerable<IHoverTip> ForLionsFangLastTurn(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LionsFangLastTurnKey,
            "Mines that go off on the enemies' turn count too.");

    /// <summary>
    /// Klee text-only fix (2026-10-13): Pass the Match's power lasts the
    /// turn and waits for the chosen player's next Attack, so a player who
    /// has ended their turn can never spend it (three co-op seats,
    /// `review/records/coop-paired-round-2026-10-09.md`).
    /// </summary>
    public static IEnumerable<IHoverTip> ForPassTheMatchActing(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PassTheMatchActingKey,
            "Choose a player who has not ended their turn. If they have, it "
          + "does nothing.");

    public static IEnumerable<IHoverTip> ForAscensionNoOath(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, AscensionNoOathKey, "This hit does not gain Oath.");

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
          + "own, others the current.");

    /// <summary>
    /// THE ONE ELEMENT HIS CARDS READ (sec.3), and what his Swirls pay for
    /// it. The numbers are <see cref="VarkaLaw"/>'s, the ones his badge
    /// prints.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCurrentElement(
        IEnumerable<IHoverTip> inherited, CardModel? card) =>
        With(inherited, CurrentElementKey,
            "The last [gold]Pyro[/gold], [gold]Hydro[/gold], [gold]Cryo[/gold] or "
          + "[gold]Electro[/gold] you applied. Swirls pay it: [gold]Pyro[/gold] "
          + VarkaLaw.SwirlPyroDamage + " damage, [gold]Hydro[/gold] "
          + VarkaLaw.SwirlHydroBlock + " [gold]Block[/gold], [gold]Cryo[/gold] "
          + VarkaLaw.SwirlCryoVulnerable + " [gold]Vulnerable[/gold], [gold]Electro[/gold] "
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
        "One of Varka's Companions. Playing one makes its element your "
      + "current element. [gold]Geo[/gold] does not.";

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
    ///
    /// THE TOOLTIP TRIM (2026-10-14): a player reads <see cref="PlayerTips"/>'
    /// words for the key where it has some; a blind seat
    /// (<see cref="TipAudience.Seat"/>) reads <paramref name="body"/>.
    private static IEnumerable<IHoverTip> With(
        IEnumerable<IHoverTip> inherited, string key, string body)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(new LocString(Table, key + ".title"),
                                  PlayerTips.For(key, body));
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

    /// <summary>
    /// Does this card's holder start each combat with Klee's Spark? Her kit
    /// pays it (<c>KleeOverhaulOpening.GrantSpark</c>), so the answer is the
    /// OWNER's character when the card has one. With no owner (a compendium
    /// or a reward shelf) it falls back to the run, as
    /// <see cref="KleesRuleBelongsHere"/> does, and prints when nothing
    /// answers. Never throws.
    /// </summary>
    public static bool KleeOpensWithASpark(CardModel card)
    {
        Player? owner = null;
        try
        {
            if (card.IsMutable) owner = card.Owner;
        }
        catch (System.Exception)
        {
            owner = null;
        }
        if (owner != null) return owner.Character is IKleeCharacter;
        return KleeAmongTheRunsPlayers() ?? true;
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

    // ------------------------------------- Furina, the Salon's Tab --------
    //
    // THE SALON'S TAB (2026-10-05, review/active/furina-research-proposal-
    // 2026-10-05.md sec.16). Short and plain: one or two sentences each, the
    // rule and nothing else. The guests' tips are their badges' sentences
    // (<see cref="StagePerformerBadge.ActText"/>).

    /// <summary>Rule 3's price: a Spend N takes N of her Fanfare, and the
    /// card or its Spend mode can't be played with less (Furina suite 1:
    /// Quick Flourish, "Spend 4", read as playable under 4). "Spend up to X" (the Spend paper,
    /// 2026-10-10) takes X or all she has, and never fails.</summary>
    public static IEnumerable<IHoverTip> ForSpend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SpendKey,
            "Pay that much [gold]Fanfare[/gold]. With less, you cannot play "
          + "the card or its Spend mode. " + SpendUpToSentence);

    /// <summary>The Spend tip's second sentence (the Spend paper,
    /// 2026-10-10), shared with the seat glossary.</summary>
    internal const string SpendUpToSentence =
        "Spend up to X pays X, or all you have if that is less.";

    /// <summary>Rule 3's definition, shared by the keyword tip and the
    /// Fanfare gauge's hover (<c>Vfx.FanfareCounter</c>). The pool-75 round
    /// (2026-10-09): a seat banked 30 for a fight that never came. Her
    /// ledger lives one combat (<see cref="FurinaStageLedger.For"/>), so the
    /// tip says it resets.
    /// The 2026-10-11 playtest: "the tooltips for Fanfare and Drain are
    /// rather verbose (Drain moreso)".</summary>
    internal const string FanfareBody =
        "Gain 1 for each HP you lose, [gold]Drain[/gold] included, or [gold]Repay[/gold]. "
      + "[gold]Spend[/gold] uses it. Resets after each combat.";

    /// <summary>Furina's sweep (2026-10-14): Ousia / Pneuma's "Flip", one
    /// sentence in the base game's style (`FurinaFlip`).</summary>
    internal const string FlipBody =
        "Turn this card to its other face; it starts each combat on Ousia.";

    /// <summary>Ousia / Pneuma: what "Flip" does.</summary>
    public static IEnumerable<IHoverTip> ForFlip(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FlipKey, FlipBody);

    /// <summary>Rule 3: Fanfare is one number on Furina.</summary>
    public static IEnumerable<IHoverTip> ForFanfare(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FanfareKey, FanfareBody);

    /// <summary>Rule 1 and the curtain call, shared by the keyword tip and
    /// the Drained counter's hover (<c>Vfx.DrainedCounter</c>). The Drain
    /// line rule (ruled 2026-10-09): a Drain may go past the line, and what
    /// it drains past it stays lost unless Repaid. The Drain buffer
    /// (2026-10-11): the line is the first 1/4 of her Max HP she drains each
    /// combat, counted in HP drained, so a hit never uses it up.
    /// The 2026-10-11 playtest ("the tooltips for Fanfare and Drain are
    /// rather verbose (Drain moreso)"): one sentence. The buffer left lives
    /// on the Drained counter's hover
    /// (<c>Vfx.DrainedCounter.BufferSentence</c>; since the Furina wave,
    /// 2026-10-13, the line is words there, never a second number).</summary>
    internal const string DrainBody =
        "Lose N HP. Each combat, the first 1/4 of your Max HP drained returns "
      + "after combat. That is your line: past it, only [gold]Repay[/gold] "
      + "returns.";

    /// <summary>Rule 1: Drain N. The in-combat "Your Drain line is N" suffix
    /// (the pool-75 round, 2026-10-09) is off the tip since the 2026-10-11
    /// playtest: with it the tip ran past the 135-character ceiling, and the
    /// Drained counter's hover already names the line and where it comes
    /// from.</summary>
    public static IEnumerable<IHoverTip> ForDrain(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, DrainKey, DrainBody);

    /// <summary>Rule 2: Repay N. The pool to 75 (Hymn of Renewal's reading,
    /// the paper's Review section): a Repay counts the HP it returns.
    /// furina-next paper 3 (2026-10-16): the rule is one line, "Any HP a
    /// Repay cannot return becomes Block."
    /// </summary>
    internal const string RepayBody =
        "Regain that much drained HP; a Repay counts the HP it returns. "
      + "Any HP a Repay cannot return becomes [gold]Block[/gold].";

    public static IEnumerable<IHoverTip> ForRepay(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, RepayKey, RepayBody);

    /// <summary>The Spend outlet paper (2026-10-12, sec.2 item 4, hygiene):
    /// two seats played Rising Applause at 0 to 4 damage. A rider about
    /// THIS card, derived from the clause (<c>gen_klee_cards.
    /// starter_spends_the_bank</c>): a starter whose damage is the
    /// Fanfare its spend-all took. THE FURINA WAVE (2026-10-13, "To change
    /// now" 2): it opens with where Fanfare comes from. Turn 1 of fight 1
    /// was no decision in all six runs: at 0 Fanfare the card read as "a
    /// worse Defend", and nothing said lost HP becomes Fanfare.</summary>
    public static IEnumerable<IHoverTip> ForBankDamage(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BankDamageKey, BankDamageBody);

    /// <summary><see cref="ForBankDamage"/>'s words.</summary>
    internal const string BankDamageBody =
        "Whenever you lose HP, gain that much [gold]Fanfare[/gold]. Its "
      + "damage is the [gold]Fanfare[/gold] you hold: play it when "
      + "the bank is worth it.";

    /// <summary>Rule 5 (the pool to 75, sec.3): where a guest goes. Since
    /// 2026-10-11 the guest a full stage pushes out acts once as it leaves
    /// ("(b) a guest who's pushed out takes a bow").</summary>
    public static IEnumerable<IHoverTip> ForSummon(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SummonKey,
            "A guest joins at the back. On a full stage, the oldest guest "
          + "acts once and leaves; its card goes to your [gold]Discard "
          + "Pile[/gold].");

    /// <summary>The Guest Star keyword (the pool to 75, sec.3).</summary>
    public static IEnumerable<IHoverTip> ForGuestStar(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, GuestStarKey,
            "Exhausts. Acts at the end of your turn. When it leaves, this "
          + "card goes to your [gold]Discard Pile[/gold].");

    /// <summary>The pool to 75 (sec.5): "Oldest guest" is the one a fourth
    /// summon would remove.</summary>
    public static IEnumerable<IHoverTip> ForOldestGuest(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, OldestGuestKey,
            "The guest on stage longest: the one a fourth summon would "
          + "remove.");

    // A guest's own tip: its line and act, upgraded on an upgraded card (the
    // pool to 75: an upgrade raises the line or the act).

    public static IEnumerable<IHoverTip> ForCharlotte(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, CharlotteKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Charlotte, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForWriothesley(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, WriothesleyKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Wriothesley, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForLynette(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LynetteKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Lynette, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForClorinde(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ClorindeKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Clorinde, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForLyney(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, LyneyKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Lyney, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForSigewinne(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SigewinneKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Sigewinne, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForChevreuse(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ChevreuseKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Chevreuse, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForFreminet(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FreminetKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Freminet, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForNavia(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NaviaKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Navia, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForNeuvillette(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, NeuvilletteKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Neuvillette, card.IsUpgraded)));

    public static IEnumerable<IHoverTip> ForEscoffier(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, EscoffierKey,
             PlayerTips.Guest(card, StagePerformerBadge.ActText(StagePerformer.Escoffier, card.IsUpgraded)));
}
