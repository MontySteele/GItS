using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// The ONE seam between the quarantined prototype surface and the shipped mod
/// (R213 B, BACKLOG EB-147).
///
/// WHAT THE QUARANTINE IS, IN THREE LAYERS, EACH OF WHICH IS ENOUGH ON ITS OWN.
///
/// 1. COMPILE. <c>KleeCode.csproj</c> does <c>Compile Remove="Cards/Prototype/**"</c>
///    unless <c>PrototypeCards=true</c>, which is also what defines
///    <c>PROTOTYPE_CARDS</c>. A release build contains no prototype class, so
///    there is no id a shipped mod could be talked into granting -- not by a
///    reward, not by a transform, not by a hand-typed console id.
///    <c>build/deploy.ps1</c> and <c>build/validate.ps1</c> never set the
///    property.
///
/// 2. POOL. Since legacy cleanup stage 4 (2026-10-01) the rows ARE each
///    character's pool: <c>GenerateAllCards</c> lists every row its owner
///    holds, first, so <c>CardModel.Pool</c> resolves and the card wears its
///    owner's frame and energy colour (a card in NO pool throws "You
///    monster!" on draw; <c>tools/lint_pool_membership.py</c>). What may be
///    OFFERED is each arm's roster (<c>KleeOverhaulRoster.OfferablePool</c>
///    and its siblings), returned from <c>FilterThroughEpochs</c>, which feeds
///    <c>GetUnlockedCards</c> -- the sole path into reward rolls and
///    transforms. A token, a starter row or a mode face is a member and never
///    offered. With an arm off (the <c>-p:ShippedKits=true</c> gate) its
///    owner's rows are filtered out of the offer by <see cref="Ids"/>.
///
/// 3. GRANT. The only door in is <c>gits/GitsGiveCard.cs</c> (EB-52) -- a
///    <c>give:</c> step in an <c>understudy/scenarios/*.yaml</c> file, naming
///    the card by id. That endpoint matches <c>ModelDb.AllCards</c> on
///    <c>Id.Entry</c>, which is exactly why layer 2 has to put the card in a
///    pool: an unregistered class is not merely unrollable, it is ungrantable.
///
/// Split <c>For(characterId)</c> rather than one flat list because
/// <c>CardModel.Pool</c> supplies the card frame and the energy icon: a Kokomi
/// prototype resolved through <c>KleeCardPool</c> would draw wearing Klee's
/// frame, which is a lie about the thing under test.
/// </summary>
public static class PrototypeCards
{
    /// <summary>
    /// Prototype rows owned by <paramref name="characterId"/>. ALWAYS EMPTY in
    /// a default build -- the classes are not compiled, so there is nothing to
    /// return and the call costs one allocation at pool construction.
    /// </summary>
    public static IReadOnlyList<CardModel> For(string characterId)
    {
#if PROTOTYPE_CARDS
        return Cards.Prototype.Generated.PrototypeRoster.For(characterId);
#else
        return System.Array.Empty<CardModel>();
#endif
    }

    private static readonly Dictionary<string, HashSet<ModelId>> IdCache = new();

    /// <summary>The ids of <see cref="For"/>, for an arm-off offer filter.
    /// Empty in a build that compiles no surface.</summary>
    public static HashSet<ModelId> Ids(string characterId)
    {
        if (!IdCache.TryGetValue(characterId, out var ids))
        {
            ids = new HashSet<ModelId>();
            foreach (var card in For(characterId)) ids.Add(card.Id);
            IdCache[characterId] = ids;
        }
        return ids;
    }
}
