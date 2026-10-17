using Godot;

namespace KleeMod.Cards;

/// <summary>
/// PUBLIC ADDRESS, Kokomi's own Curse (<c>review/active/kokomi-story-2026-10-16.md</c>,
/// pick 2 (a)): "It is Unplayable and leaves after 3 combats. Its text: *"She
/// has promised a speech when she gets home."*" A <see cref="StoryCurse"/>,
/// which holds the clock; its text is the line above the clock's sentence.
///
/// ONLY THE PROMISED RITE GIVES IT (The Serpent's Bones, "Promise him a rite
/// at home."). It is a member of her pool (<c>KokomiCardPool.GenerateAllCards</c>)
/// and not of her offer (<c>KokomiOverhaulRoster.OfferablePool</c>), so
/// nothing generates it.
///
/// ITS PICTURE IS BORROWED: Orders from the Shrine's (BACKLOG "Art owed,
/// Kokomi's story").
/// </summary>
public sealed class PublicAddress : StoryCurse
{
    public const string TitleText = "Public Address";

    /// <summary>The paper's text for the card.</summary>
    public const string Text = "She has promised a speech when she gets home.";

    protected override string CurseTitle => TitleText;

    protected override string? FlavorLine => Text;

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("proto_kk_orders_from_the_shrine");
}
