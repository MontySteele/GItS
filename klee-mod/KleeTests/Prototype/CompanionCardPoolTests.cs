using KleeMod;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The shared companions' own pool (legacy review pick 4, [USER] 2026-10-18:
/// "Shared companions move to their own pool with a neutral frame, out of
/// Klee's"). The neutral frame is the base game's Colorless look, read off
/// <see cref="ColorlessCardPool"/> itself so a Steam move that renames it
/// fails here rather than on a card face.
/// </summary>
public class CompanionCardPoolTests
{
    // ALLOCATED, NOT CONSTRUCTED (the BaseBasicsTests idiom): the constructor
    // registers the pool with BaseLib, and the base pools are the game's boot.
    // Every property read here is a literal expression body.
    private static T Pool<T>() where T : CardPoolModel =>
        (T)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(typeof(T));

    [Fact]
    public void Companions_wear_the_colorless_frame_and_orb()
    {
        var colorless = Pool<ColorlessCardPool>();
        var companion = Pool<CompanionCardPool>();
        Assert.Equal(colorless.EnergyColorName, companion.EnergyColorName);
        Assert.Equal(colorless.CardFrameMaterialPath,
                     companion.CardFrameMaterialPath);
        Assert.Equal(colorless.DeckEntryCardColor, companion.DeckEntryCardColor);
        Assert.NotEqual(Pool<KleeCardPool>().CardFrameMaterialPath,
                        companion.CardFrameMaterialPath);
    }

    [Fact]
    public void The_pool_is_shared_so_the_engine_sees_it_but_is_not_a_colorless_rule()
    {
        var companion = Pool<CompanionCardPool>();
        // BaseLib's ModelDbSharedCardPoolsPatch appends IsShared pools to
        // ModelDb.AllSharedCardPools; without it CardModel.Pool cannot find
        // the card and throws "You monster!".
        Assert.True(companion.IsShared);
        // IsColorless is a RULE in the base game (Heirloom Hammer copies only
        // a Colorless card); the move changes the frame, not the rules.
        Assert.False(companion.IsColorless);
    }
}
