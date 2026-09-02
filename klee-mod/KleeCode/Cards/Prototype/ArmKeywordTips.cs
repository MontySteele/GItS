using System.Collections.Generic;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
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
    public const string MendKey = "KLEEMOD-ARM_MEND";
    public const string PlanKey = "KLEEMOD-ARM_PLAN";
    public const string SwirlKey = "KLEEMOD-ARM_SWIRL";

    // ----------------------------------------------------------- Klee ------
    //
    // The four sentences are the ruled brief's sec.3 rules 1, 2, 4 and 6, as
    // slice one prints them (`review/active/klee-overhaul-slice-1-2026-09-01.md`
    // sec.2, "Keywords with tooltips: Bomb, Set off, Spark, Mine").

    /// <summary>Rule 1. Deliberately NOT the badge's paragraph: the badge
    /// speaks about one enemy's live pile, this speaks about the word.
    ///
    /// THE SECOND SENTENCE IS <c>EB-287</c>. The r3 Opus seat called the
    /// stacking "the single most important interaction in the deck and I only
    /// found it by gambling a card on it", because nothing printed said what
    /// happens when a second Bomb lands where one already is. It says what is
    /// TRUE and stops there: the charges share one pile and one badge total
    /// and one <i>Set off</i> pops all of them, but they stay separate charges
    /// and each grows on its own -- fusing them into a single charge is
    /// Careful Arrangement's whole card, and a tip claiming the kit did it for
    /// free would print that card as a blank.</summary>
    public static IEnumerable<IHoverTip> ForBomb(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BombKey,
            "A numbered charge on an enemy. It grows by "
          + KleeOverhaulLaw.BombGrowth + " at the start of your turn and never "
          + "goes off by itself. A Bomb placed on an enemy that already has "
          + "one joins it there: the badge shows their total, and a single "
          + "[gold]Set off[/gold] pops them all.");

    /// <summary>Rule 2, and the one [USER] named ("Set Off has no tooltip
    /// text"). The ORDER clause is the load-bearing half: the explosions land
    /// BEFORE the rest of the card, which is what makes a cooked pile worth
    /// more than the Attack printed beside it.</summary>
    public static IEnumerable<IHoverTip> ForSetOff(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SetOffKey,
            "Every [gold]Bomb[/gold] on the target goes off, one at a time, "
          + "each a Pyro hit for its size, before the rest of the card.");

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
        const string shared =
            "Some cards cost [gold]Sparks[/gold] instead of energy. No cap; "
          + "gone at the end of combat.";
        if (!KleeOverhaul.Enabled) return shared;
        // R242 pick 1 put the opening bank INTO rule 4, and the tip is where a
        // player meets the word: a Spark-priced card in an opening hand is
        // exactly the moment the r4 seat found unplayable by construction, and
        // the sentence that fixes it belongs beside the one that was already
        // there rather than on a relic the player may not have read.
        return "You start each combat with " + KleeOverhaulLaw.OpeningSpark
             + " and gain " + KleeOverhaulLaw.SparkPerExplosion
             + " whenever a [gold]Bomb[/gold] goes off. " + shared;
    }

    /// <summary>
    /// Rule 6, and its SECOND sentence is `EB-291`.
    ///
    /// The Bomb badge learned to say "after [gold]Weak[/gold]" at `EB-287`.
    /// The Mine, which fires on its own during the ENEMY's turn and so is
    /// never in front of a player at the moment it matters, said nothing at
    /// all. The r4 Opus seat left a Gremlin Merc at 3 HP under a "Mine 3" as a
    /// deliberate free kill, the Mine dealt 2, and the enemy survived and hit
    /// him: "The Mine has no equivalent... no number, no Weak note."
    ///
    /// It states the RULE rather than a number, because a keyword tip is read
    /// in hand where there is no pile to quote: a Mine IS a Bomb, so it is the
    /// same Pyro hit for its own size and the same modifiers move it. The live
    /// arithmetic stays where it can be right -- on the badge.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off when its enemy attacks "
          + "you, before the hit lands. It is the same Pyro hit for its own "
          + "size, so [gold]Weak[/gold] shrinks it exactly as it shrinks a "
          + "[gold]Set off[/gold]; the enemy's badge prints the number.");

    // ---------------------------------------------------------- Kokomi -----
    //
    // Her TWO, and the slice's own rules section is what makes it two
    // (`review/active/kokomi-overhaul-slice-1-2026-09-01.md` draft 6 sec.2,
    // "Keywords with tooltips: Plan, Mend"). Draft 2 printed six; Tide, Surge,
    // Exert and Garment left with the rules they named.

    /// <summary>
    /// RULE 2, and it is the whole kit in three sentences. The SECOND is the
    /// load-bearing half: a player who has never read the brief has to be able
    /// to find "play it on the jellyfish" from the card in their hand, which is
    /// the slice's own first acceptance sentence (sec.1).
    ///
    /// THE THIRD IS `EB-293`. "instead" presumes a normal play to do instead
    /// of, and a card with no now-line has none -- its target type is
    /// <c>KokomiTargets.PetOnly</c> and the jellyfish is the only legal drop.
    /// The r2 Opus seat could not tell: "Plan-only cards never say what happens
    /// if you play them normally... I never risked finding out." The row's own
    /// face now leads with "Play on the Bake-Kurage." (the codegen's
    /// <c>_plan_only_line</c>) and the word's definition says why some rows
    /// carry that line and others do not.
    /// </summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "Play this on the [gold]Bake-Kurage[/gold] instead and the "
          + "jellyfish carries out the [gold]Plan[/gold] line at the start of "
          + "your next turn. The cost is paid now either way, and planned hits "
          + "land on the front enemy unless the line says every enemy. A card "
          + "with nothing but a [gold]Plan[/gold] line can only be played on "
          + "the jellyfish, and says so.");

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
            "Anemo meets an existing aura: the aura is consumed and copied "
          + "onto all enemies. An enemy carrying no aura is unchanged.");

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
}
