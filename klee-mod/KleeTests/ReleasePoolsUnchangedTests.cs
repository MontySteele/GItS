#if !PROTOTYPE_CARDS
using System;
using System.Linq;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE RELEASE BUILD'S POOLS ARE THE POOLS AS THEY SHIPPED. Klee's and
/// Furina's own relics and potions
/// (<c>review/active/relics-potions-klee-furina-2026-09-27.md</c>) exist only
/// under <c>PROTOTYPE_CARDS</c>, and their pools move only under their arms;
/// this file is compiled only WITHOUT the switch, so it is the one place that
/// can say a release build still borrows the Silent's potions for all three
/// and offers every member of each relic pool. The arm-off half inside a dev
/// build is <c>Prototype/ArmRelicsPotionsTests</c>'.
/// </summary>
public class ReleasePoolsUnchangedTests
{
    [Theory]
    [InlineData(typeof(global::KleeMod.Klee))]
    [InlineData(typeof(global::KleeMod.Furina))]
    [InlineData(typeof(global::KleeMod.Kokomi))]
    public void Every_character_borrows_the_silent_potion_pool(Type character)
    {
        var calls = Il.CallSequence(
            character.GetProperty("PotionPool")!.GetGetMethod()!);
        Assert.Equal(new[] { "ModelDb.PotionPool<SilentPotionPool>" },
                     calls.Where(c => c.StartsWith("ModelDb.")).ToArray());
    }

    [Theory]
    [InlineData(typeof(global::KleeMod.KleeRelicPool))]
    [InlineData(typeof(global::KleeMod.FurinaRelicPool))]
    [InlineData(typeof(global::KleeMod.KokomiRelicPool))]
    public void No_relic_pool_filters_its_offer(Type pool)
    {
        Assert.Equal(typeof(RelicPoolModel),
                     pool.GetMethod("GetUnlockedRelics")!.DeclaringType);
    }
}
#endif
