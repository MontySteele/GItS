using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// EB-94. The one way a HOVER TIP is allowed to ask a card who owns it.
///
/// <c>CardModel.Owner</c>'s GETTER calls <c>AssertMutable()</c>, so reading it
/// on a CANONICAL model throws <c>CanonicalModelException</c> -- and a `?.` at
/// the call site cannot help, because the throw is inside the property rather
/// than in the dereference. Every hover-tip surface is reached with canonical
/// models: <c>NCardLibraryGrid._Ready</c> fills the compendium straight out of
/// <c>ModelDb.AllCards</c> and hands those models to <c>NCard.Create</c>
/// verbatim, so <c>NCardHolder.CreateHoverTips</c> reads
/// <c>CardNode.Model.HoverTips</c> on a canonical instance every time a player
/// hovers a card in the Card Library. The tips did not merely fail to render;
/// the throw escapes the whole <c>HoverTips</c> getter, so the card lost its
/// keyword tips entirely (measured on the wire as `keywords: 0`).
///
/// The guard is the GAME'S OWN idiom, not an invention: <c>CardModel</c> writes
/// <c>base.IsMutable &amp;&amp; (Owner?.IsOstyAlive ?? false)</c> when it needs
/// the owner from a place a canonical model can reach
/// (<c>CardModel.GetDescriptionForPile</c>, decompile of
/// <c>data_sts2_windows_x86_64/sts2.dll</c>). <c>IsMutable</c> is a public,
/// non-asserting property on <c>AbstractModel</c> (<c>IsCanonical</c> is its
/// negation), so no reflection on the private <c>_owner</c> field is needed --
/// the game's non-asserting readers (<c>Pile</c>, <c>CombatState</c>,
/// <c>RunState</c>) only reach that field because they are declared on
/// <c>CardModel</c> itself.
///
/// Null is the RIGHT answer for a canonical card, not a fallback: every tip
/// body in this mod already has a no-owner branch, because a card in the deck
/// view or a reward screen has no live meter to read and prints its rate
/// alone.
/// </summary>
public static class TipOwner
{
    /// <summary>The creature that owns this card, or null when there is no
    /// owner to read -- including on a canonical model, where asking would
    /// throw.</summary>
    public static Creature? CreatureOf(CardModel? card) =>
        card is { IsMutable: true } ? card.Owner?.Creature : null;
}
