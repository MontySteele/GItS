using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA WAVE (2026-10-13, <c>review/records/furina-wave-2026-10-13.md</c>,
/// "To change now"): one Drain number on the counter's hover and the card
/// face, a no-choice Drain that stops at the line says so in the stage log,
/// Rising Applause's rider teaches Fanfare, Crashing Waves previews what its
/// Spend buys, and Final Bow says its acts are in turn. No number or rule
/// moves. Python twin: <c>tier0/tests/test_furina_wave_2026_10_13.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaWaveTests
{
    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static string BankDamageBody => TipText.Named("BankDamageBody");

    // ---- 1. one Drain number -------------------------------------------------

    [Fact]
    public void The_counters_hover_prints_the_buffer_left_and_no_line_number()
    {
        // A buffer of 19 from 78, 4 of it drained: 15 left.
        var kit = StageKit.At(78, 78);
        Run(kit.Director.Drain(4));
        Assert.Equal(15, kit.Stage.BufferLeft);
        var body = DrainedCounter.HoverBody(kit.Stage.Drained,
                                            kit.Stage.BufferLeft);
        Assert.StartsWith("Drain buffer: [blue]15[/blue] HP left. ", body);
        Assert.DoesNotContain("Drain line", body);
        Assert.DoesNotContain(kit.Stage.Line.ToString(), body);
    }

    [Fact]
    public void The_face_warns_past_the_buffer_with_no_number()
    {
        // Her HP legibility pass (2026-10-19): the all-past and inside tags
        // carry no number either; only the split names its two parts.
        Assert.DoesNotContain(FurinaStageFacePreview.PastLineLost,
                              char.IsDigit);
        Assert.DoesNotContain(FurinaStageFacePreview.ReturnsTag,
                              char.IsDigit);
        Assert.Equal("\n(Past your Drain buffer: returns after combat)",
                     FurinaStageFacePreview.PastLineReturns);
    }

    [Fact]
    public void Lyneys_drain_stopped_at_the_line_leaves_a_stopped_beat()
    {
        // A buffer of 29 with Lyney on stage, all of it drained: his act's
        // Drain 2 has no room, so the log says it was stopped.
        var kit = StageKit.At(78, 78, StagePerformer.Lyney);
        Run(kit.Director.Drain(29));
        kit.Stage.ClearBeats();
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        var stopped = kit.Stage.Beats
            .Where(b => b.Event == FurinaStageLedger.StoppedEvent).ToList();
        Assert.Single(stopped);
        Assert.Equal(StagePerformer.Lyney, stopped[0].Who);
        Assert.Equal(FurinaStageLaw.LyneyActDrain, stopped[0].Moved);
        Assert.Equal(FurinaStageLedger.StoppedAtBuffer, stopped[0].Reason);
        // The damage lands either way, as before.
        Assert.Contains("damage Lyney All 5 Pyro", kit.Board.Log);
    }

    [Fact]
    public void A_drain_with_room_leaves_no_stopped_beat()
    {
        var kit = StageKit.At(78, 78, StagePerformer.Lyney);
        kit.Stage.ClearBeats();
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.DoesNotContain(kit.Stage.Beats,
                              b => b.Event == FurinaStageLedger.StoppedEvent);
    }

    [Fact]
    public void Reginas_stop_names_the_power()
    {
        // 17 of the 19 drained: the first copy drains 2 of its 3 and is
        // stopped for 1; the second finds no room and is stopped for 3.
        var kit = StageKit.At(78, 78);
        Run(kit.Director.Drain(17));
        kit.Stage.ClearBeats();
        Assert.Equal(1, Run(kit.Director.Regina(2)));
        var stopped = kit.Stage.Beats
            .Where(b => b.Event == FurinaStageLedger.StoppedEvent).ToList();
        Assert.Equal(new[] { 1, 3 }, stopped.Select(b => b.Moved));
        Assert.All(stopped, b => Assert.Equal(StageDirector.ReginaTitle, b.Source));
    }

    // ---- 2. Rising Applause ----------------------------------------------------

    [Fact]
    public void Rising_applause_says_lost_hp_becomes_fanfare()
    {
        Assert.StartsWith("Whenever you lose HP, gain that much "
                          + "[gold]Fanfare[/gold]. ",
                          BankDamageBody);
    }

    // ---- 3. Crashing Waves -------------------------------------------------------

    [Fact]
    public void Crashing_waves_says_what_the_bank_buys()
    {
        Assert.Equal("", FurinaStageFacePreview.SpendUpToHitsWords(0));
        Assert.Equal("\n(Spends 2: no extra hit)",
                     FurinaStageFacePreview.SpendUpToHitsWords(2));
        Assert.Equal("\n(Spends 6: 1 more hit)",
                     FurinaStageFacePreview.SpendUpToHitsWords(6));
        Assert.Equal("\n(Spends 16: 4 more hits)",
                     FurinaStageFacePreview.SpendUpToHitsWords(16));
        // Co-op seat (2026-10-16): a spend that empties the bank says so.
        Assert.Equal("\n(Spends all 6: 1 more hit)",
                     FurinaStageFacePreview.SpendUpToHitsWords(6, all: true));
        // Off a combat the face adds nothing.
        Assert.Equal("", FurinaStageFacePreview.SpendUpToHits(
            new ProtoFsCrashingWaves(), 16));
    }

    // ---- A Spend mode she cannot pay (BACKLOG) -------------------------------------

    [Fact]
    public void A_spend_mode_says_when_fanfare_is_short()
    {
        // The chooser drops a Spend mode she cannot pay and the plain side
        // plays; the face says so in hand. Off a combat it adds nothing.
        Assert.Equal("\n(Not enough Fanfare)",
                     FurinaStageFacePreview.NotEnoughFanfare);
        Assert.Equal("", FurinaStageFacePreview.SpendShort(
            new ProtoFsBubbleAria(), 3));
        Assert.Contains(Il.Calls(Il.Method("FurinaStageFacePreview",
                                           "SpendShort")),
                        c => c.Contains("FurinaStage.CanSpend"));
    }
}
