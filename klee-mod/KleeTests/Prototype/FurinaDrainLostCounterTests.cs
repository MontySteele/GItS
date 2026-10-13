using KleeMod.Powers;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE "LOST FOR GOOD" COUNTER (the quarter-line round, 2026-10-10,
/// <c>review/records/furina-quarter-line-round-2026-10-10.md</c>, "What to
/// change" 1): wherever her drained HP is shown, the part past the Drain line
/// is named in one phrase, "Drained 12 HP (4 past your line: lost unless you
/// Repay)". Seats learned that cost only by losing the HP. Seat-page twin:
/// <c>tier0/tests/test_furina_drain_lost_counter.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaDrainLostCounterTests
{
    [Fact]
    public void The_phrase_names_the_part_past_the_line()
    {
        Assert.Equal("Drained [blue]12[/blue] HP ([blue]4[/blue] past your "
                     + "line: lost unless you [gold]Repay[/gold])",
                     DrainedCounter.DrainedPhrase(12, 4));
    }

    [Fact]
    public void Nothing_past_the_line_reads_as_today()
    {
        Assert.Equal("Drained [blue]12[/blue] HP",
                     DrainedCounter.DrainedPhrase(12, 0));
        Assert.Equal("Drained [blue]0[/blue] HP",
                     DrainedCounter.DrainedPhrase(0, 0));
        Assert.DoesNotContain("past your line:",
                              DrainedCounter.HoverBody(5, 13, past: 0));
    }

    [Fact]
    public void The_hover_reads_both_parts_off_the_ledger()
    {
        // A buffer of 19 from 78 of 78 (the Drain buffer, 2026-10-11), 16
        // of it drained: a Drain of 7 takes 3 within it and 4 past it.
        var kit = StageKit.At(78, 78);
        Assert.True(StageKit.Run(kit.Director.Drain(16)));
        Assert.Equal(3, kit.Stage.BufferLeft);
        Assert.Equal(59, kit.Stage.Line);
        Assert.True(StageKit.Run(kit.Director.Drain(7)));
        Assert.Equal((19, 4), (kit.Stage.DrainedAbove, kit.Stage.DrainedPast));

        var body = DrainedCounter.HoverBody(kit.Stage.Drained,
                                            kit.Stage.BufferLeft,
                                            kit.Stage.Line <= 0,
                                            kit.Stage.DrainedPast);
        Assert.Contains("\n" + DrainedCounter.DrainedPhrase(23, 4) + ".\n",
                        body);

        // A Repay returns the past-line part first: once it is back, the
        // phrase drops.
        Assert.Equal(4, StageKit.Run(kit.Director.Repay(4)));
        Assert.Equal(0, kit.Stage.DrainedPast);
        var after = DrainedCounter.HoverBody(kit.Stage.Drained,
                                             kit.Stage.BufferLeft,
                                             kit.Stage.Line <= 0,
                                             kit.Stage.DrainedPast);
        Assert.Contains("\nDrained [blue]19[/blue] HP.\n", after);
        Assert.DoesNotContain("past your line:", after);
    }
}
