using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI ROUND 4 A-LIST (2026-10-13; review
/// <c>review/active/kokomi-review-r4-2026-10-13.md</c> section 5A), the C#
/// side: Moon's Reflection's empty-pile gate and its reason, and Vigor
/// looking past Opening Gambit's and Second Wave's now-line. Sim and page
/// twin: <c>tier0/tests/test_kokomi_round4_alist_2026_10_13.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRound4AListTests
{
    [Fact]
    public void Moons_reflection_is_unplayable_while_the_exhaust_pile_is_empty()
    {
        // Moon's Reflection left with the Kokomi pool overhaul (2026-10-13);
        // its gate stays, and a canonical copy of any card fails it open.
        Assert.Null(typeof(KokomiPlan).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoKkMoonsReflection"));
        Assert.True(KokomiRefounding.AnyExhausted(new ProtoKkTidecleanse()));
    }

    [Fact]
    public void Vigor_looks_past_the_two_skills_now_lines()
    {
        Assert.True(KokomiSkillVigor.Exempt(new ProtoKkOpeningGambit()));
        Assert.True(KokomiSkillVigor.Exempt(new ProtoKkSecondWave()));
        Assert.False(KokomiSkillVigor.Exempt(new ProtoKkPincer()));
        Assert.False(KokomiSkillVigor.Exempt(null));

        decimal bonus = 4m;
        Assert.False(KokomiSkillVigor.ModifyPrefix(new ProtoKkOpeningGambit(), ref bonus));
        Assert.Equal(0m, bonus);
        bonus = 4m;
        Assert.True(KokomiSkillVigor.ModifyPrefix(new ProtoKkPincer(), ref bonus));
        Assert.Equal(4m, bonus);

        Task done = null!;
        Assert.False(KokomiSkillVigor.BeforeAttackPrefix(new ProtoKkSecondWave(), ref done));
        Assert.Same(Task.CompletedTask, done);
        Assert.True(KokomiSkillVigor.BeforeAttackPrefix(new ProtoKkPincer(), ref done));
    }

    [Fact]
    public void The_vigor_patches_name_methods_the_game_has()
    {
        foreach (var name in new[] { "VigorPower_SkillNowLine_Modify_Patch",
                                     "VigorPower_SkillNowLine_BeforeAttack_Patch" })
        {
            var patch = typeof(KokomiSkillVigor).Assembly.GetTypes()
                .Single(t => t.Name == name);
            var target = patch.GetCustomAttributes<HarmonyPatch>()
                .Single().info;
            Assert.Equal(typeof(VigorPower), target.declaringType);
            Assert.NotNull(typeof(VigorPower).GetMethod(target.methodName,
                BindingFlags.Public | BindingFlags.Instance));
        }
    }
}
