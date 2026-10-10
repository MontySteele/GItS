using System.IO;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE DRAIN-LINE ROUND'S FOUR CHANGES (2026-10-09,
/// <c>review/records/furina-drain-line-round-2026-10-09.md</c>, "What to
/// change"): every Repay preview with a floor names its payout, a guest
/// act's Drain stops at the line, the curtain-call sentence, and Critics'
/// Darling's hit in the stage log. Sim twin:
/// <c>tier0/tests/test_furina_drain_line_round.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaDrainLineRoundTests
{
    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    // ---- 1. the Repay preview names its payout -----------------------------

    [Fact]
    public void A_short_repay_names_its_payout_on_one_line()
    {
        Assert.Equal("\n(Repays 0, +3 Block)",
                     FurinaStageFacePreview.Line(0, 3, "Block"));
        Assert.Equal("\n(Repays 1, +1 Vigor)",
                     FurinaStageFacePreview.Line(1, 2, "Vigor"));
        Assert.Equal("\n(Repays 2, +2 damage)",
                     FurinaStageFacePreview.Line(2, 4, "damage"));
        // A full Repay, and a card with no payout, keep the plain line.
        Assert.Equal("\n(Repays 3)", FurinaStageFacePreview.Line(3, 3, "Block"));
        Assert.Equal("\n(Repays 0)", FurinaStageFacePreview.Line(0, 2, ""));
    }

    [Fact]
    public void Each_card_with_a_floor_passes_its_payout_and_the_rest_pass_none()
    {
        foreach (var (type, pay) in new[]
                 {
                     ("ProtoFsFountainOfLucine", "PayBlock"),
                     ("ProtoFsHymnOfManyWaters", "PayBlock"),
                     ("ProtoFsGentleCurrent", "PayBlock"),
                     ("ProtoFsGrandEntrance", "PayBlock"),
                     ("ProtoFsPneumaTides", "PayVigor"),
                     ("ProtoFsSurgingWaters", "PayDamage"),
                     ("ProtoFsHydroLance", "PayDamage"),
                     ("ProtoFsCleansingTorrent", "PayDamage"),
                 })
        {
            Assert.Contains($"FurinaStageFacePreview.{pay})", Generated(type));
        }
        foreach (var type in new[] { "ProtoFsSoothingWaters",
                                     "ProtoFsPneumaRefrain",
                                     "ProtoFsBalanceTheBooks",
                                     "ProtoFsGrandAbsolution",
                                     "ProtoFsSingerOfManyWaters",
                                     "ProtoFsRiptideLunge" })
        {
            Assert.DoesNotContain("FurinaStageFacePreview.Pay", Generated(type));
        }
    }

    // ---- 2. a guest act's Drain stops at the line --------------------------

    [Fact]
    public void Lyneys_act_drains_only_the_room_above_the_line()
    {
        // Line 59 from 78, 49 with Lyney on stage. At 50 HP there is 1 HP
        // of room: it drains 1, nothing past the line, and deals its 8.
        var kit = StageKit.At(50, 78, StagePerformer.Lyney);
        Assert.Equal(1, kit.Director.GuestDrainRoom(2));
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(49, kit.Board.Hp);
        Assert.Equal(1, kit.Stage.Drained);
        Assert.Equal(0, kit.Stage.DrainedPast);
        Assert.Contains("damage Lyney All 8 Pyro", kit.Board.Log);
        // At the line: 0 drained, the damage unchanged.
        Assert.Equal(0, kit.Director.GuestDrainRoom(2));
        kit.Board.Log.Clear();
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(49, kit.Board.Hp);
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("lose "));
        Assert.Contains("damage Lyney All 8 Pyro", kit.Board.Log);
    }

    [Fact]
    public void The_players_own_drain_still_goes_past_the_line()
    {
        var kit = StageKit.At(50, 78);
        Assert.True(StageKit.Run(kit.Director.Drain(5)));
        Assert.Equal(45, kit.Board.Hp);
        Assert.Equal(5, kit.Stage.DrainedPast);
    }

    [Fact]
    public void Lyneys_badge_says_his_drain_stops_at_the_line()
    {
        Assert.Contains(", never past your line (none at or below it). Deal 8 "
                        + "[gold]Pyro[/gold] "
                        + "damage to ALL enemies.",
                        StagePerformerBadge.ActText(StagePerformer.Lyney));
    }

    // ---- 3. the curtain-call sentence ---------------------------------------

    [Fact]
    public void The_drain_tip_says_drained_hp_above_the_line_returns()
    {
        var body = (string)typeof(ArmKeywordTips)
            .GetField("DrainBody", HeadlessGame.All)!.GetRawConstantValue()!;
        Assert.Contains("Drained HP above your line returns after combat.",
                        body);
        Assert.DoesNotContain("Drained HP returns after combat", body);
    }

    // ---- 4. Critics' Darling's hit in the stage log -------------------------

    [Fact]
    public void A_power_hit_files_a_stage_beat_naming_the_power()
    {
        var kit = StageKit.With(new StageMods { CriticsDarling = 1 }, 0);
        Run(kit.Director.Drain(4));
        var hit = kit.Stage.Beats.Single(
            b => b.Event == FurinaStageLedger.HitEvent);
        Assert.Equal("Critics' Darling", hit.Source);
        Assert.Equal(4, hit.Moved);
        Assert.Equal("random", hit.Reason);
        // Salon's Encore's hit to ALL is filed the same way.
        var encore = StageKit.With(new StageMods { SalonsEncore = 3 }, 0);
        Run(encore.Director.Drain(2));
        var all = encore.Stage.Beats.Single(
            b => b.Event == FurinaStageLedger.HitEvent);
        Assert.Equal("Salon's Encore", all.Source);
        Assert.Equal("all", all.Reason);
    }
}
