using BaseLib.Patches.Content;
using MegaCrit.Sts2.Core.Entities.Cards;

namespace KleeMod.Cards;

/// <summary>
/// Custom card keywords. BaseLib's GenEnumValues scans the mod assembly for
/// [CustomEnum] CardKeyword fields at ModelDb.Init and assigns each a fresh
/// enum value, so the field is populated before any card model exists --
/// reading it from CanonicalKeywords is always safe.
/// </summary>
public static class KleeKeywords
{
    /// <summary>
    /// Display marker for the sheet's `skill_tag` (playtest finding, sprint of
    /// 2026-07-20: players had no way to see which cards feed the Burst
    /// meter). AutoKeywordPosition.After renders a gold "Elemental Skill."
    /// line after the card text and RichKeyword gives it a hover tip; the loc
    /// entries live in klee/localization/eng/card_keywords.json in the pck
    /// (key = KLEEMOD-ELEMENTAL_SKILL from the namespace prefix + the
    /// CustomEnum name).
    ///
    /// DISPLAY ONLY: gameplay still reads the ISkillTagCard marker
    /// (KleeElementalHooks), never this keyword. Codegen emits both from the
    /// same sheet tag, and the parity lint holds hand-written cards to it.
    /// </summary>
    [CustomEnum("elemental_skill")]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword ElementalSkill;
}
