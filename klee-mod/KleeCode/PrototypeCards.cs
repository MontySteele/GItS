using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// The seam between the generated prototype surface (`docs/prototype-surface.yaml`,
/// `Cards/Prototype/Generated`) and the character pools. Since legacy cleanup
/// stage 5 the surface is the current kits and every build compiles it.
///
/// POOL. Each character's <c>GenerateAllCards</c> lists every row its owner
/// holds, so <c>CardModel.Pool</c> resolves and the card wears its owner's
/// frame and energy colour (a card in NO pool throws "You monster!" on draw;
/// <c>tools/lint_pool_membership.py</c>). What may be OFFERED is each kit's
/// roster (<c>KleeOverhaulRoster.OfferablePool</c> and its siblings),
/// returned from <c>FilterThroughEpochs</c>, which feeds
/// <c>GetUnlockedCards</c> -- the sole path into reward rolls and transforms.
/// A token, a starter row or a mode face is a member and never offered.
///
/// GRANT. A scenario's <c>give:</c> step (<c>gits/GitsGiveCard.cs</c>, EB-52)
/// matches <c>ModelDb.AllCards</c> on <c>Id.Entry</c>, which is why the pool
/// must hold the card: an unregistered class is ungrantable.
///
/// Split <c>For(characterId)</c> rather than one flat list because
/// <c>CardModel.Pool</c> supplies the card frame and the energy icon.
/// </summary>
public static class PrototypeCards
{
    /// <summary>Prototype rows owned by <paramref name="characterId"/>.</summary>
    public static IReadOnlyList<CardModel> For(string characterId)
    {
        return Cards.Prototype.Generated.PrototypeRoster.For(characterId);
    }
}
