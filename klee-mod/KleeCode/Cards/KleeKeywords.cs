using BaseLib.Patches.Content;
using KleeMod.Elements;
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
    /// entries ship in the pck and have a DLL-side playtest fallback in
    /// KleeMod.InjectLocStrings (key = KLEEMOD-ELEMENTAL_SKILL from the
    /// namespace prefix + the CustomEnum name).
    ///
    /// DISPLAY ONLY: gameplay still reads the ISkillTagCard marker
    /// (KleeElementalHooks), never this keyword. Codegen emits both from the
    /// same sheet tag, and the parity lint holds hand-written cards to it.
    /// </summary>
    [CustomEnum("elemental_skill")]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword ElementalSkill;

    // Elemental application badges. Unlike Bomb (which is merely referenced
    // by many cards), these are actual card properties, so After gives every
    // aura-applying card one compact, consistent label below its rules text.
    [CustomEnum("applies_pyro")]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword AppliesPyro;

    [CustomEnum("applies_hydro")]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword AppliesHydro;

    [CustomEnum("applies_electro")]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword AppliesElectro;

    [CustomEnum("applies_cryo")]
    [KeywordProperties(AutoKeywordPosition.After)]
    public static CardKeyword AppliesCryo;

    // Referenced-term tips. Auto=None keeps these out of rules text; cards
    // opt into them through ExtraHoverTips, including combat-aware reaction
    // previews that only appear while the matching aura is on the board.
    [CustomEnum("bomb")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword Bomb;

    [CustomEnum("confiscated")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword Confiscated;

    [CustomEnum("vaporize_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword VaporizePreview;

    [CustomEnum("melt_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword MeltPreview;

    [CustomEnum("overload_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword OverloadPreview;

    [CustomEnum("superconduct_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword SuperconductPreview;

    [CustomEnum("electro_charged_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword ElectroChargedPreview;

    [CustomEnum("frozen_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword FrozenPreview;

    [CustomEnum("frozen_boss_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword FrozenBossPreview;

    [CustomEnum("swirl_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword SwirlPreview;

    [CustomEnum("crystallize_preview")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword CrystallizePreview;

    public static CardKeyword AuraApplication(Element element) => element switch
    {
        Element.Pyro => AppliesPyro,
        Element.Hydro => AppliesHydro,
        Element.Electro => AppliesElectro,
        Element.Cryo => AppliesCryo,
        _ => CardKeyword.None,
    };

    public static CardKeyword ReactionPreview(Reaction reaction) => reaction switch
    {
        Reaction.Vaporize => VaporizePreview,
        Reaction.Melt => MeltPreview,
        Reaction.Overload => OverloadPreview,
        Reaction.Superconduct => SuperconductPreview,
        Reaction.ElectroCharged => ElectroChargedPreview,
        Reaction.Frozen => FrozenPreview,
        Reaction.Swirl => SwirlPreview,
        Reaction.Crystallize => CrystallizePreview,
        _ => CardKeyword.None,
    };
}
