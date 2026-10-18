using Godot;

namespace KleeMod.Cards;

/// <summary>
/// STAGE FRIGHT, Furina's own Curse (<c>review/active/furina-story-2026-10-15.md</c>
/// sec.1, pick 2 (a)): "Unplayable; removed after 3 combats, like Klee's
/// Confinement and Varka's Overdue Reports." A <see cref="StoryCurse"/>, which
/// holds the clock.
///
/// ONLY HER STORY EVENTS GIVE IT. It is a member of her pool
/// (<c>FurinaCardPool.GenerateAllCards</c>) and not of her offer
/// (<c>FurinaStageRoster.OfferablePool</c>), so nothing generates it.
///
/// ITS PICTURE is its own (`curse_stage_fright` in art/plan.tsv, the art
/// gaps pass 2026-10-18): a show cancelled.
/// </summary>
public sealed class StageFright : StoryCurse
{
    public const string TitleText = "Stage Fright";

    protected override string CurseTitle => TitleText;

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("curse_stage_fright");
}
