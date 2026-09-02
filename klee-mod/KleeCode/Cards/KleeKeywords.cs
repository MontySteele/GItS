using BaseLib.Patches.Content;
using KleeMod.Elements;
using KleeMod.Powers;
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
    // by many cards), these are actual card properties -- so the element they
    // name is a card's PROPERTY and belongs on the face as such.
    //
    // POSITION `None`, NOT `After` ([USER], 2026-09-01, after playing Klee:
    // "instead of saying 'applies pyro' - maybe make it a card indicator as
    // well to remove text overhead? That would be a universal shift"). `After`
    // is what printed the sentence: BaseLib's GenEnumValues puts an `After`
    // keyword into `AutoKeywordText.AdditionalAfterKeywords`, from there into
    // the base game's `CardKeywordOrder.afterDescription`, and
    // `CardModel.BuildDescription` appends its card text as a line of the
    // rules box. `None` removes that line and nothing else.
    //
    // THE TIP SURVIVES THE FLIP, and that is a property of the base game
    // rather than of this file: `CardModel.HoverTips` walks `Keywords` and
    // calls `HoverTipFactory.FromKeyword` on every one of them: it never reads
    // the printed text. Bomb, Confiscated and the eight reaction previews
    // below have ridden `None` since they were written and have always
    // hovered; these four now join them.
    //
    // WHAT DRAWS THE ELEMENT INSTEAD: `Vfx/ElementBadge.cs`, which reads THESE
    // keywords off the card and paints the aura's own icon beside the type
    // plaque. One declaration, so the gem and the tip cannot disagree.
    //
    // ONE SWITCH, EVERY SHEET. There is one keyword per element and all four
    // sheets plus both quarantined arms declare the same four, so this flip is
    // the whole of the removal on 114 faces (Klee 36 generated + 5 written,
    // Furina 9, Kokomi 20, the prototype surface 44).
    [CustomEnum("applies_pyro")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword AppliesPyro;

    [CustomEnum("applies_hydro")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword AppliesHydro;

    [CustomEnum("applies_electro")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword AppliesElectro;

    [CustomEnum("applies_cryo")]
    [KeywordProperties(AutoKeywordPosition.None)]
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

    // B5 (playtest-2, 2026-07-28): the salon-deploy cards used to render one
    // boilerplate paragraph that named no member and restated the cap rules on
    // every copy. The face now names WHO takes the stage; these carry what
    // that member DOES, and the cap rules, so the paragraph does not have to
    // be reprinted eight times.
    //
    // Auto=None: cards opt in through ExtraHoverTips, and a deploy card asks
    // for exactly the members it deploys.
    [CustomEnum("salon_crabaletta")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword SalonCrabaletta;

    [CustomEnum("salon_usher")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword SalonUsher;

    [CustomEnum("salon_chevalmarin")]
    [KeywordProperties(AutoKeywordPosition.None)]
    public static CardKeyword SalonChevalmarin;

    public static CardKeyword SalonMemberKeyword(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => SalonCrabaletta,
        SalonMember.Usher => SalonUsher,
        SalonMember.Chevalmarin => SalonChevalmarin,
        _ => CardKeyword.None,
    };

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
