using System.Collections.Generic;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// `EB-377`: the BASE GAME'S words a quarantined face names, defined on the
/// face that names them.
///
/// THE GAP, AND WHY IT LOOKED LIKE ONLY ONE WORD. The round-9 Kokomi seat
/// reported `Weak`, `Frail`, `Slow` and `Minion` correctly defined and
/// `Vulnerable` defined on no screen at all -- which reads as one missing
/// table row and is not. Those four arrive as POWERS on a body, and a status
/// row carries the game's own hover tip with it; a word a CARD names carries
/// nothing until something is already wearing it. So the one screen where the
/// definition decides a purchase -- a reward, a shop, a hand before the debuff
/// exists -- is exactly the screen that has none. `Exposed Flank+` was bought
/// "on a genre assumption" (r9 run 2, act 1, (c) 6).
///
/// WHY THE BASE GAME DOES NOT ALREADY DO THIS. `CardModel.HoverTips` walks the
/// card's declared `Keywords`; it never reads the printed description. A
/// generated prototype row declares Exhaust, Ethereal, Innate, Retain, Sly and
/// its aura keyword and nothing else, so `[gold]Vulnerable[/gold]` in a body is
/// a word with no declaration behind it and hovers nothing. The attach here is
/// <see cref="ArmKeywordTips"/>' bargain exactly: DERIVED from the golded span
/// in the row's own built description by `gen_klee_cards.emit`, so a new row
/// that prints one of these words carries its definition because it printed the
/// word and not because somebody remembered.
///
/// QUARANTINED, LIKE ITS SIBLING, and that is a scope decision rather than a
/// technical one. The file sits under `Cards/Prototype/`, which
/// `KleeCode.csproj` Compile-Removes from a release build, and the attach is
/// gated on `CharacterProfile.arm_keyword_tips` -- true only on the prototype
/// surface. A release build is untouched: eighty shipped faces print `Weak`
/// today and widening the attach to them is a change to the shipped surface,
/// which this row was not filed against.
///
/// THE NUMBERS ARE THE BASE GAME'S STRUCTURAL RATES, not this mod's dials, so
/// they are written out rather than interpolated from a `*OverhaulLaw`: there
/// is no mod constant to interpolate. They are held in step from the sim side
/// instead -- `blindplay_shape.VULNERABLE_TAKEN_PCT` and its two neighbours are
/// pinned to `tier0.constants`, and the page glossary and these bodies are
/// pinned to each other by
/// `test_the_base_keyword_glossary_is_the_mods_own_tooltip_text`.
/// </summary>
public static class BaseKeywordTips
{
    /// <summary>The hover-tip title table, the same one every other tip in the
    /// mod titles itself from.</summary>
    private const string Table = "card_keywords";

    // `KLEEMOD-BASE_` and not the bare word, for `KLEEMOD-ARM_`'s reason one
    // file over: the base game owns a keyword id for each of these already,
    // and a shared key would have one definition silently overwrite the other
    // at the loc merge. These titles are the same words, which is correct
    // rather than a collision -- they are the same rules, restated where the
    // card is.
    public const string VulnerableKey = "KLEEMOD-BASE_VULNERABLE";
    public const string WeakKey = "KLEEMOD-BASE_WEAK";
    public const string FrailKey = "KLEEMOD-BASE_FRAIL";
    public const string StrengthKey = "KLEEMOD-BASE_STRENGTH";
    public const string DexterityKey = "KLEEMOD-BASE_DEXTERITY";

    /// <summary>
    /// The word the row was filed for. Both halves matter and neither is on
    /// the card: the multiplier is what a player prices the Plan with, and the
    /// decay is why `Exposed Flank` played directly and `Exposed Flank`
    /// planned are two different cards (r9 run 2, act 1, finding 2 -- "the
    /// Vulnerable case is the sharpest").
    /// </summary>
    public static IEnumerable<IHoverTip> ForVulnerable(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, VulnerableKey,
            "The wearer takes 50% more damage from every hit. One stack falls "
          + "off at the end of each of its turns.");

    /// <summary>The mirror one debuff over, and the one the Plan tip's second
    /// sentence assumes a reader already knows.</summary>
    public static IEnumerable<IHoverTip> ForWeak(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, WeakKey,
            "The wearer deals 25% less damage. One stack falls off at the end "
          + "of each of its turns.");

    /// <summary>The third duration debuff. No quarantined face prints it
    /// today; the row exists because the attach is derived and a face that
    /// prints it tomorrow must not have to remember this.</summary>
    public static IEnumerable<IHoverTip> ForFrail(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, FrailKey,
            "The wearer gains 25% less [gold]Block[/gold]. One stack falls "
          + "off at the end of each of its turns.");

    /// <summary>
    /// The undecaying half of the pair, and the word `ArmKeywordTips.ForPlan`
    /// now says does NOT reach a Plan (`EB-380`) -- a sentence that cannot be
    /// read by somebody who was never told what Strength does.
    /// </summary>
    public static IEnumerable<IHoverTip> ForStrength(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, StrengthKey,
            "Adds its amount to every [gold]Attack[/gold] hit the wearer "
          + "lands. It does not decay.");

    /// <summary>Strength's Block twin.</summary>
    public static IEnumerable<IHoverTip> ForDexterity(
        IEnumerable<IHoverTip> inherited, CardModel card) =>
        With(inherited, DexterityKey,
            "Adds its amount to every [gold]Block[/gold] the wearer gains. It "
          + "does not decay.");

    /// <summary>
    /// One tip, appended after whatever the card already carries -- the same
    /// order <see cref="ArmKeywordTips"/> appends in, and these go after those:
    /// a word the arm invented is the one a player has never met, and a base
    /// word restated is the thing you read third.
    /// </summary>
    private static IEnumerable<IHoverTip> With(
        IEnumerable<IHoverTip> inherited, string key, string body)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(new LocString(Table, key + ".title"), body);
    }
}
