using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-727` -- THE IDENTITY PREDICATE ANSWERS FOR THE ABSENT CASE.
///
/// <c>FurinaResources.IsFurina</c> used to take a non-nullable
/// <c>Creature</c> and dereference it, so a caller holding no creature -- a
/// compendium page, a card on a shelf, a hook fired on a board being torn
/// down -- got a NullReferenceException where the honest answer is "no".
/// Several call sites do hold a <c>Creature?</c>; two of them had each grown
/// their own null test in front of the call, which is the shape that ends in
/// the first caller that forgets one crashing.
///
/// So the guard is at the SOURCE, and this is what pins it there. The two
/// derived predicates are pinned on the prototype side, where their types
/// are compiled: <c>FurinaStageRuleTests.The_arm_is_hers_alone</c> and
/// <c>FurinaReframeRuleTests</c> both already ask them for null.
/// </summary>
public class FurinaIdentityNullTests
{
    [Fact]
    public void IsFurina_answers_false_for_no_creature()
    {
        Assert.False(FurinaResources.IsFurina(null));
    }

    [Fact]
    public void IsFurina_still_answers_for_the_seats()
    {
        // The negative half alone would pass on a predicate that had been
        // made null-safe by always answering false.
        Assert.True(FurinaResources.IsFurina(Seat.Furina().Creature));
        Assert.False(FurinaResources.IsFurina(Seat.Klee().Creature));
        Assert.False(FurinaResources.IsFurina(Seat.Kokomi().Creature));
    }
}
