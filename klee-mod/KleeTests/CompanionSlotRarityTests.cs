using System;
using System.IO;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-620` -- THE COMPANION SLOT'S RARITY ROLL, PINNED WHERE THE ROW SAID
/// THERE WAS NONE.
///
/// The row was raised off [USER]'s Klee act-1 run ("a LOT of rares": four
/// Rares in ten picks) on the reading that the fourth reward slot draws a
/// Companion from the roster with no rarity roll at all, so 11 Rare rows of 47
/// would surface at roughly a fifth of offers. THAT PREMISE IS FALSE in both
/// engines and always was: <see cref="CompanionSlot.Roll"/> rolls a
/// rarity on tier0's `RARITY_ODDS` (common .60 / uncommon .35 / rare .05) and
/// draws only inside the rolled tier, and `tier05.rewards.roll_rewards` does
/// the same with `_roll_rarity`. What was missing was a PIN saying so -- the
/// odds constants were already compared by value against tier0
/// (`tools/lint_constant_parity.py`), but nothing asserted that `Roll` spends
/// them, so the roll could have been deleted without a red test.
///
/// STRUCTURAL, and it has to be: `Roll` needs a live `Player` and `RunState`
/// to hand back a card, which is outside the headless boundary (KleeTests
/// README). What is real here is the call graph and the source of the one
/// branch, which is exactly the claim the row disputed.
///
/// WHAT THIS DOES NOT SAY. The odds are tier0's flat table; the base game logs
/// its own card-reward roll with a rising offset ("Card rarity: Rolled X, need
/// &lt; Y for rare (offset = Z)"). Whether the slot should mirror that pity
/// shape instead is a separate question, and it needs the decompile and a
/// run's `godot.log` to answer -- neither is readable from here.
/// </summary>
public class CompanionSlotRarityTests
{
    private const BindingFlags All = HeadlessGame.All;

    [Fact]
    public void The_slot_rolls_a_rarity_before_it_draws()
    {
        var roll = typeof(CompanionSlot).GetMethod("Roll", All)!;
        var calls = Il.Calls(roll);

        // The roll happens, off the run's own Rewards stream.
        Assert.Contains(calls, c => c.Contains("CompanionSlot.RollRarity"));
        Assert.Contains(calls, c => c.Contains("get_Rewards"));

        // And the rarity it produced is what selects the candidate list: the
        // draw reads `tiers[rarity]`, never the whole roster.
        var body = Source("CompanionSlot.cs").Replace("\r\n", "\n");
        Assert.Contains("var rarity = forcedRarity ?? RollRarity(rng);", body);
        Assert.Contains("if (!tiers.TryGetValue(rarity, out var pool)) "
                      + "return null;", body);
        Assert.Contains("NationWeightedChoice(rng, pool, HomeNation(player))",
                        body);
    }

    [Fact]
    public void The_rarity_roll_walks_the_three_tiers_in_sheet_order()
    {
        // The odds themselves are compared by value against tier0 by
        // `lint_constant_parity`; what is asserted here is the WALK -- a
        // cumulative common -> uncommon -> rare comparison, so Rare is the
        // tail of the distribution rather than a third of it.
        var body = Source("CompanionSlot.cs").Replace("\r\n", "\n");
        var start = body.IndexOf("private static CardRarity RollRarity",
                                 StringComparison.Ordinal);
        Assert.True(start > 0, "RollRarity is where the odds are spent");
        var method = body[start..(body.IndexOf("\n    }", start,
                                               StringComparison.Ordinal))];

        Assert.Contains("roll < CommonOdds ? CardRarity.Common", method);
        Assert.Contains("roll < CommonOdds + UncommonOdds "
                      + "? CardRarity.Uncommon", method);
        Assert.Contains(": CardRarity.Rare", method);
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
