using System;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- what rounds four's two seat rounds sent back, as the
/// main session ruled it:
///
///   * RAISE ON AN EMPTY STAGE SUMMONS. With nobody on stage, a Raise summons
///     a random performer holding the Raise amount (not the usual 1), and
///     nothing else is raised -- for every Raise (back, lead, every
///     performer) and the Raise powers (the Ancient's turn-start Raise,
///     Thunderous Applause). Arkhe Alignment's Pneuma prints "the lead
///     REGAINS" and does not summon.
///   * Tutti! costs 1, 0 upgraded.
///   * Chevalmarin's act files the per-enemy figure, so the page prints "2 to
///     every enemy" and not the four hits' total.
///   * The Ousia and Pneuma tips ride Arkhe Alignment's power too.
///
/// THE EMPTY-STAGE VERB IS PINNED IN TWO HALVES, the batch-two file's split:
/// the ledger's move headlessly, and the verb's wiring structurally, because
/// fielding the body (<c>FurinaStagePets.Sync</c>) needs a live combat.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageRoundFourTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        return (seat, stage);
    }

    private static string RepoFile(string relativePath,
                                   [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relativePath);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relativePath);
    }

    // ---- the ledger's half ------------------------------------------------

    [Fact]
    public void An_empty_stage_summons_one_performer_holding_the_raise()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        // Gala Dinner's 3: ONE performer at 3, not three, and not at 1.
        var seat = stage.SummonOnEmpty(StagePerformer.Chevalmarin, 3);

        Assert.NotNull(seat);
        Assert.Single(stage.Seats);
        Assert.Equal(StagePerformer.Chevalmarin, stage.Lead!.Who);
        Assert.Equal(3, stage.Lead!.Fanfare);
        var arrive = stage.Beats.Last();
        Assert.Equal("arrive", arrive.Event);
        Assert.Equal(3, arrive.Fanfare);
    }

    [Fact]
    public void An_occupied_stage_is_raised_and_summons_nobody()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 2));

        Assert.Null(stage.SummonOnEmpty(StagePerformer.Crabaletta, 3));
        Assert.Single(stage.Seats);
        Assert.Equal(2, stage.Lead!.Fanfare);
    }

    [Fact]
    public void A_raise_of_nothing_summons_nobody()
    {
        using var _ = new Arm();
        var (_, stage) = Stage();

        Assert.Null(stage.SummonOnEmpty(StagePerformer.Usher, 0));
        Assert.Empty(stage.Seats);
    }

    [Fact]
    public void An_occupied_stage_takes_the_raise_through_the_verbs()
    {
        // The verbs' non-summoning path runs headlessly: nobody is fielded.
        using var _ = new Arm();
        var (seat, stage) = Stage(
            (StagePerformer.Usher, 2), (StagePerformer.Crabaletta, 1));

        Assert.Equal(3, FurinaStage.Raise(seat.Creature, 3).Result);
        Assert.Equal(4, stage.Back!.Fanfare);
        Assert.Equal(2, FurinaStage.RaiseLead(seat.Creature, 2).Result);
        Assert.Equal(4, stage.Lead!.Fanfare);
        Assert.Equal(2, FurinaStage.RaiseAll(seat.Creature, 1).Result);
        Assert.Equal(new[] { 5, 5 },
                     stage.Seats.Select(s => s.Fanfare).ToArray());
    }

    [Fact]
    public void Pneuma_regains_on_the_lead_and_summons_nobody_on_an_empty_stage()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage();

        ArkheAlignmentPower.Choose(seat.Creature, pneuma: true);

        Assert.Empty(stage.Seats);
        Assert.Equal(2, stage.ActBlockMultiplier);
    }

    // ---- the verbs' wiring (structural) ------------------------------------

    [Theory]
    [InlineData("Raise")]
    [InlineData("RaiseLead")]
    [InlineData("RaiseAll")]
    public void Every_raise_verb_asks_the_empty_stage_first(string verb)
    {
        var calls = Il.Calls(Il.Method("FurinaStage", verb));
        Assert.Contains("FurinaStage.SummonForRaise", calls);
    }

    [Fact]
    public void The_empty_stage_summon_fields_a_random_body()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "SummonForRaise"));
        Assert.Contains("FurinaStage.RollFree", calls);
        Assert.Contains("FurinaStageLedger.SummonOnEmpty", calls);
        Assert.Contains("FurinaStagePets.Sync", calls);
    }

    [Fact]
    public void The_raise_powers_raise_through_the_summoning_verb()
    {
        // The Ancient's turn-start Raise, and Thunderous Applause.
        Assert.Contains("FurinaStage.Raise", Il.Calls(
            Il.Method("StageRaisePerTurnPower", "AfterPlayerTurnStart")));
        Assert.Contains("FurinaStage.Raise",
                        Il.Calls(Il.Method("FurinaStage", "AfterBow")));
    }

    [Fact]
    public void Pneuma_regains_and_does_not_raise()
    {
        var choose = Il.Calls(Il.Method("ArkheAlignmentPower", "Choose"));
        Assert.Contains("FurinaStage.RegainLead", choose);
        Assert.DoesNotContain("FurinaStage.RaiseLead", choose);
        Assert.DoesNotContain(
            "FurinaStage.SummonForRaise",
            Il.Calls(Il.Method("FurinaStage", "RegainLead")));
    }

    [Fact]
    public void The_generated_raises_are_awaited()
    {
        foreach (var card in new[]
                 {
                     "ProtoFsStandingOvation", "ProtoFsWarmReception",
                     "ProtoFsHoldYourPlaces", "ProtoFsGalaDinner",
                 })
        {
            var src = RepoFile(Path.Combine(
                "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
                card + ".cs"));
            Assert.Contains("await FurinaStage.Raise", src);
        }
    }

    // ---- Tutti! -----------------------------------------------------------

    [Fact]
    public void Tutti_costs_one_and_zero_upgraded()
    {
        var src = RepoFile(Path.Combine(
            "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
            "ProtoFsTutti.cs"));
        Assert.Contains("base(1, CardType.Skill", src);
        Assert.Contains("EnergyCost.UpgradeBy(-1)", src);
    }

    // ---- Chevalmarin's per-enemy figure ------------------------------------

    [Fact]
    public void An_even_sweep_files_what_each_enemy_lost()
    {
        Assert.Equal(2, FurinaStage.EvenLoss(
            new[] { 20, 15, 30, 9 }, new[] { 18, 13, 28, 7 }));
    }

    [Fact]
    public void An_uneven_sweep_or_no_enemy_files_no_single_figure()
    {
        // A Vulnerable body took 3 where the others took 2.
        Assert.Equal(-1, FurinaStage.EvenLoss(
            new[] { 20, 15 }, new[] { 18, 12 }));
        Assert.Equal(-1, FurinaStage.EvenLoss(
            Array.Empty<int>(), Array.Empty<int>()));
    }

    [Fact]
    public void The_wire_log_carries_the_per_enemy_figure()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Chevalmarin, 3));
        stage.ClearBeats();
        stage.Note(new StageBeat("act", StagePerformer.Chevalmarin, 0, 3, 8,
                                 "", Each: 2));

        var snapshot = FurinaStageLedger.Snapshot(seat.Player);
        var log = (System.Collections.Generic.List<object?>)snapshot["log"]!;
        var row = (System.Collections.Generic.Dictionary<string, object?>)
            log.Single()!;

        Assert.Equal(8, row["moved"]);
        Assert.Equal(2, row["each"]);
    }

    [Fact]
    public void A_beat_with_no_per_enemy_figure_says_so()
    {
        Assert.Equal(-1, new StageBeat("act", StagePerformer.Usher, 0, 3, 3,
                                       "").Each);
    }

    // ---- the Arkhe tips ---------------------------------------------------

    [Fact]
    public void The_arkhe_power_carries_the_ousia_and_pneuma_tips()
    {
        var calls = Il.Calls(Il.Method("ArkheAlignmentPower",
                                       "get_ExtraHoverTips"));
        Assert.Contains("ArmKeywordTips.ForOusia", calls);
        Assert.Contains("ArmKeywordTips.ForPneuma", calls);
    }
}
