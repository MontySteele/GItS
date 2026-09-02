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
/// entry-HP bound is real, it is enforced in <see cref="KokomiTide.Mend"/>,
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
/// `ProtoBakeKuragePower` does the same for the Tide on the jellyfish. Those
/// stay exactly as they are. A badge can only be read once the thing exists on
/// the board; the card-side keyword is what a player reads in HAND, in a
/// reward, in a shop and on the blind-play page -- which is where the word was
/// first met and where it explained nothing.
///
/// THE NUMERALS ARE INTERPOLATED FROM THE CONSTANTS THEY QUOTE (`EB-89`), so a
/// retune of `KleeOverhaulLaw.BombGrowth` or `KokomiOverhaulLaw.GarmentMend`
/// cannot leave one of these sentences telling a player a retired number.
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
    public const string TideKey = "KLEEMOD-ARM_TIDE";
    public const string SurgeKey = "KLEEMOD-ARM_SURGE";
    public const string ExertKey = "KLEEMOD-ARM_EXERT";
    public const string MendKey = "KLEEMOD-ARM_MEND";
    public const string PlanKey = "KLEEMOD-ARM_PLAN";
    public const string GarmentKey = "KLEEMOD-ARM_GARMENT";
    public const string SwirlKey = "KLEEMOD-ARM_SWIRL";

    // ----------------------------------------------------------- Klee ------
    //
    // The four sentences are the ruled brief's sec.3 rules 1, 2, 4 and 6, as
    // slice one prints them (`review/active/klee-overhaul-slice-1-2026-09-01.md`
    // sec.2, "Keywords with tooltips: Bomb, Set off, Spark, Mine").

    /// <summary>Rule 1. Deliberately NOT the badge's paragraph: the badge
    /// speaks about one enemy's live pile, this speaks about the word.</summary>
    public static IEnumerable<IHoverTip> ForBomb(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, BombKey,
            "A numbered charge on an enemy. It grows by "
          + KleeOverhaulLaw.BombGrowth + " at the start of your turn and never "
          + "goes off by itself.");

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
        return "You gain " + KleeOverhaulLaw.SparkPerExplosion + " whenever a "
             + "[gold]Bomb[/gold] goes off. " + shared;
    }

    /// <summary>Rule 6.</summary>
    public static IEnumerable<IHoverTip> ForMine(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MineKey,
            "A [gold]Bomb[/gold] that also goes off when its enemy attacks "
          + "you, before the hit lands.");

    // ---------------------------------------------------------- Kokomi -----
    //
    // Her six are the slice's own rules section, verbatim
    // (`review/active/kokomi-overhaul-slice-1-2026-09-01.md` sec.2,
    // "Keywords with tooltips: Tide, Surge, Exert, Mend, Plan, Garment").

    /// <summary>Rules 1 and 2.</summary>
    public static IEnumerable<IHoverTip> ForTide(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, TideKey,
            "The [gold]Bake-Kurage[/gold] is always on the field and holds "
          + "[gold]Tide[/gold], starting at 0, never resetting on its own. "
          + "Her cards add Tide.");

    /// <summary>Rule 3.</summary>
    public static IEnumerable<IHoverTip> ForSurge(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, SurgeKey,
            "The jellyfish deals Hydro damage equal to the [gold]Tide[/gold] "
          + "to the target; Tide is 0.");

    /// <summary>Rule 5, and the one both round-one seats had to infer from
    /// watching their own HP drop.</summary>
    public static IEnumerable<IHoverTip> ForExert(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, ExertKey,
            "[gold]Exert N[/gold]: on Skills and Powers only, never Attacks. "
          + "Lose N HP, Block first.");

    /// <summary>
    /// THE BOUND IS THE WHOLE POINT OF THIS ROW'S SECOND HALF. The Casket read
    /// as broken at full HP because a Mend at the ceiling does nothing and
    /// nothing on screen said there was a ceiling. The sentence is
    /// <see cref="KokomiTide.Mend"/>'s own ("never above the HP you entered the
    /// fight with"), so the rule and its only explanation are one line apart.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMend(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, MendKey,
            "[gold]Mend N[/gold]: heal N HP, never above the HP you entered "
          + "the fight with.");

    /// <summary>Rule 8.</summary>
    public static IEnumerable<IHoverTip> ForPlan(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, PlanKey,
            "[gold]Plan[/gold]: happens at the start of her next turn.");

    /// <summary>Rule 6. Distinct from `KLEEMOD-GARMENT_RIDER`, which is raised
    /// on her ATTACKS and only while the state is UP: this one is the word's
    /// definition and is raised by the face that grants it.</summary>
    public static IEnumerable<IHoverTip> ForGarment(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, GarmentKey,
            "For a stated number of turns, each Attack that hits "
          + "[gold]Mends[/gold] " + KokomiOverhaulLaw.GarmentMend + ".");

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
    /// (the Charge rate, the Garment window, a reaction preview) stay at the
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
