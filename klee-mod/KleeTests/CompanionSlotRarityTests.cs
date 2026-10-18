using System;
using System.IO;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE COMPANION SLOT ROLLS LIKE THE CARDS BESIDE IT ([USER] 2026-10-18,
/// legacy review pick 3: "Agreed on all 6 legacy picks"). Its rarity comes
/// from the base game's own <c>CardFactory.RollForRarity</c> on the reward's
/// own odds (regular, elite or boss, with the rare pity counter), and it gets
/// the native reward card's upgrade roll (<c>CardFactory.RollForUpgrade</c>).
/// After a boss it is a Rare, an Uncommon when no Rare can be offered.
///
/// STRUCTURAL, and it has to be: `Roll` needs a live `Player` and `RunState`
/// to hand back a card, which is outside the headless boundary (KleeTests
/// README). What is real here is that both base methods resolve on the
/// shipped assembly and that `Roll` spends them.
/// </summary>
public class CompanionSlotRarityTests
{
    private const BindingFlags All = HeadlessGame.All;

    [Fact]
    public void Both_base_rolls_resolve_on_the_shipped_assembly()
    {
        foreach (var (field, method) in new[]
                 {
                     ("BaseRollForRarity", "RollForRarity"),
                     ("BaseRollForUpgrade", "RollForUpgrade"),
                 })
        {
            var resolved = (Delegate?)typeof(CompanionSlot)
                .GetField(field, All)!.GetValue(null);
            Assert.NotNull(resolved);
            Assert.Equal(method, resolved!.Method.Name);
            Assert.Equal("CardFactory", resolved.Method.DeclaringType!.Name);
        }
    }

    [Fact]
    public void The_slot_rolls_the_rewards_own_rarity_then_upgrades()
    {
        var roll = typeof(CompanionSlot).GetMethod("Roll", All)!;
        var calls = Il.Calls(roll);
        Assert.Contains(calls, c => c.Contains("CompanionSlot.RollRarity"));
        Assert.Contains(calls, c => c.Contains("get_RngOverride"));
        Assert.Contains(calls, c => c.Contains("RollForUpgradeFn.Invoke"));

        var rarity = Il.Calls(typeof(CompanionSlot).GetMethod("RollRarity", All)!);
        Assert.Contains(rarity, c => c.Contains("get_RarityOdds"));
        Assert.Contains(rarity, c => c.Contains("RollForRarityFn.Invoke"));

        var body = Source("CompanionSlot.cs").Replace("\r\n", "\n");
        Assert.Contains("upgrade(player, card, 0m, rng);", body);
        Assert.Contains("CardCreationFlags.NoUpgradeRoll", body);
        Assert.Contains("odds == CardRarityOddsType.BossEncounter", body);
        Assert.Contains(": CardRarity.Uncommon;", body);
    }

    [Fact]
    public void The_reward_slot_asks_the_same_offerability_rule_as_the_shop()
    {
        // Audit 2026-10-18: Roll tested PersonalPool alone and skipped
        // IsHiddenFrom, so Yae's reward slot could offer her own Sesshou
        // Sakura while the shop and the sim hid it. Both surfaces now go
        // through CompanionPool.IsOfferable.
        var roll = typeof(CompanionSlot).GetMethods(All | BindingFlags.DeclaredOnly)
            .Where(m => m.Name == nameof(CompanionSlot.Roll) && m.GetMethodBody() != null);
        Assert.NotEmpty(roll);
        Assert.All(roll, m => Assert.Contains(Il.Calls(m), c => c.EndsWith(".IsOfferable")));
    }

    [Fact]
    public void A_five_star_is_offerable_whatever_the_seed()
    {
        // NO FEATURED BANNER ([USER] 2026-10-18, "Agreed on (a)!" -- scrap
        // the banner everywhere). The banner was the one offer filter keyed on
        // the player's seed and a companion's star: it let only three
        // five-stars per nation be offered in a given run. STRUCTURAL, for
        // the headless reason above: neither offer surface -- the reward
        // slot nor the shop's eligible set, lambdas included -- reads the
        // seed or the star, so no seed can take a five-star out of a run.
        // Rarity, nation weighting, personal pools and IsHiddenFrom remain.
        foreach (var owner in new[] { typeof(CompanionSlot), typeof(CompanionPool) })
        {
            var methods = new[] { owner }
                .Concat(owner.GetNestedTypes(All))
                .SelectMany(t => t.GetMethods(All | BindingFlags.DeclaredOnly))
                .Where(m => m.GetMethodBody() != null);
            foreach (var method in methods)
            {
                var calls = Il.Calls(method);
                Assert.DoesNotContain(calls, c => c.EndsWith(".get_Seed"));
                Assert.DoesNotContain(calls, c => c.EndsWith(".get_Star"));
            }
        }
        Assert.Null(typeof(CompanionSlot).Assembly
                        .GetType("KleeMod.CompanionBanner"));
    }

    /// <summary>A source file under `klee-mod/KleeCode`.</summary>
    private static string Source(string relativePath)
    {
        var relative = Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', Path.DirectorySeparatorChar));
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, relative);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = dir.Parent;
        }
        throw new FileNotFoundException(relative);
    }
}
