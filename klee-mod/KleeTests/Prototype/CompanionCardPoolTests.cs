using System.Collections.Generic;
using System.Reflection;
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
    public void The_pool_is_shared_so_the_engine_sees_it_and_colorless_like_the_base_one()
    {
        var companion = Pool<CompanionCardPool>();
        // BaseLib's ModelDbSharedCardPoolsPatch appends IsShared pools to
        // ModelDb.AllSharedCardPools; without it CardModel.Pool cannot find
        // the card and throws "You monster!".
        Assert.True(companion.IsShared);
        // IsColorless as ColorlessCardPool answers it: Heirloom Hammer copies
        // a companion as it copies a base Colorless card. The kit pools stay
        // characters' pools.
        Assert.Equal(Pool<ColorlessCardPool>().IsColorless, companion.IsColorless);
        Assert.True(companion.IsColorless);
        Assert.False(Pool<KleeCardPool>().IsColorless);
    }

    [Fact]
    public void Hammer_and_gem_read_IsColorless_and_shop_pricing_does_not()
    {
        // The flag is safe to set because the base game's readers are a copy
        // filter (Heirloom Hammer) and a reward-pool guard (Prismatic Gem),
        // and the shop's Colorless surcharge is a TYPE test on
        // ColorlessCardPool, not the flag. STRUCTURAL, off the shipped IL
        // (lambdas included): a Steam move that starts pricing by the flag
        // fails here.
        const string flag = "CardPoolModel.get_IsColorless";
        Assert.Contains(flag, CallsIn(
            typeof(MegaCrit.Sts2.Core.Models.Cards.HeirloomHammer)));
        Assert.Contains(flag, CallsIn(
            typeof(MegaCrit.Sts2.Core.Models.Relics.PrismaticGem)));
        Assert.DoesNotContain(flag, CallsIn(
            typeof(MegaCrit.Sts2.Core.Entities.Merchant.MerchantCardEntry)));
        Assert.DoesNotContain(flag, CallsIn(
            typeof(MegaCrit.Sts2.Core.Entities.Merchant.MerchantInventory)));
    }

    private static HashSet<string> CallsIn(System.Type type)
    {
        const BindingFlags all = BindingFlags.Instance | BindingFlags.Static
            | BindingFlags.Public | BindingFlags.NonPublic
            | BindingFlags.DeclaredOnly;
        var found = new HashSet<string>();
        var types = new Stack<System.Type>();
        types.Push(type);
        while (types.Count > 0)
        {
            var t = types.Pop();
            foreach (var nested in t.GetNestedTypes(all)) types.Push(nested);
            foreach (var m in t.GetMethods(all))
            {
                found.UnionWith(global::KleeMod.Tests.Harness.Il.Calls(m));
            }
        }
        return found;
    }
}
