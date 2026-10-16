using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI ROUND 7 DISPLAY FIXES (2026-10-14). The wire's two new queue
/// fields: whether a waiting Plan plays a card (which Ringing counts as the
/// turn's one card, the way it counts any auto-play) and where the
/// Vulnerable it applies lands (which a later Plan's hit in the same morning
/// meets). Page twin: <c>tier0/tests/test_kokomi_round7_display_2026_10_14.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRound7DisplayTests
{
    private static KokomiPlan.Entry Of(params KokomiPlan.Planned[] clauses) =>
        new(null, clauses);

    [Fact]
    public void The_queue_row_carries_plays_card_and_vulnerable_aim()
    {
        var keys = Il.Strings(Il.Method("KokomiPlan", "QueueRow"));
        Assert.Contains("plays_card", keys);
        Assert.Contains("vulnerable_aim", keys);
    }

    [Fact]
    public void Only_the_card_playing_clauses_play_a_card()
    {
        Assert.True(KokomiPlan.PlaysACard(Of(new KokomiPlan.Planned(
            KokomiPlan.Kind.ReplayExhausted, 0, KokomiPlan.Aim.Self))));
        Assert.True(KokomiPlan.PlaysACard(Of(new KokomiPlan.Planned(
            KokomiPlan.Kind.PlayCopyOfCompanion, 0, KokomiPlan.Aim.FrontEnemy))));
        Assert.False(KokomiPlan.PlaysACard(Of(new KokomiPlan.Planned(
            KokomiPlan.Kind.Damage, 3, KokomiPlan.Aim.AllEnemies))));
    }

    [Fact]
    public void Vulnerable_aim_names_where_it_lands()
    {
        Assert.Equal("all", KokomiPlan.VulnerableAim(Of(new KokomiPlan.Planned(
            KokomiPlan.Kind.ApplyVulnerable, 2, KokomiPlan.Aim.AllEnemies))));
        Assert.Equal("front", KokomiPlan.VulnerableAim(Of(new KokomiPlan.Planned(
            KokomiPlan.Kind.ApplyVulnerable, 1, KokomiPlan.Aim.FrontEnemy))));
        Assert.Equal("", KokomiPlan.VulnerableAim(Of(new KokomiPlan.Planned(
            KokomiPlan.Kind.Damage, 3, KokomiPlan.Aim.AllEnemies))));
    }
}
