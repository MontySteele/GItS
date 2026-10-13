using Godot;

namespace KleeMod.Cards;

/// <summary>
/// OVERDUE REPORTS, Varka's own Curse
/// (<c>review/active/varka-story-2026-10-13.md</c> sec.3): "Unplayable.
/// After 3 combats, remove this from your deck." Jean always catches up with
/// him eventually. A <see cref="StoryCurse"/>, built like Klee's Confinement.
///
/// ONLY DISPATCH FROM MONDSTADT GIVES IT ("Sign them later."). It is a member
/// of Varka's pool (<c>VarkaCardPool.GenerateAllCards</c>) and not of his
/// offer (<c>VarkaRoster.OfferablePool</c>), so nothing generates it.
///
/// ITS PICTURE IS BORROWED: Behind Jean's Desk's (Jean at her desk), as
/// Confinement borrows Sorry, Jean's; no art row of its own is owed.
/// </summary>
public sealed class OverdueReports : StoryCurse
{
    public const string TitleText = "Overdue Reports";

    protected override string CurseTitle => TitleText;

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("proto_ko_behind_jeans_desk");
}
