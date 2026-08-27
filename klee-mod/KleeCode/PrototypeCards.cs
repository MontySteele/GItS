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
/// 2. POOL. Under the flag, the rows go into each character's OFF-POOL list,
///    which is the engine's own idiom and the only runtime-legal shape.
///    <c>CardModel.Pool</c> walks <c>ModelDb.AllCardPools</c> and falls through
///    to <c>MockCardPool</c> -- which throws InvalidOperationException("You
///    monster!") in a shipped build -- so a card in NO pool crashes the moment
///    it is drawn or previewed (see <c>KleeOffPoolCards</c> for the crash of
///    record and <c>tools/lint_pool_membership.py</c> for the gate). Off-pool
///    means IN <c>GenerateAllCards</c>, so Pool resolves and the card has a
///    frame and an energy colour, and OUT of <c>GetUnlockedCards</c>, which is
///    the SOLE path into reward rolls (<c>CardCreationOptions.GetPossibleCards</c>)
///    and card transforms (<c>CardFactory</c>). Nothing else generates from a
///    pool, so "not in a reward pool" is a property of the code, not a promise.
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
}
