using System;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Combat;
using Xunit;
using static KleeMod.Tests.Prototype.FurinaSpendAllPreviewWeakTests;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S HP LEGIBILITY PASS (2026-10-19,
/// <c>review/active/furina-hp-legibility-2026-10-19.md</c>, all picks (a)):
/// the returning HP (the bar's segment and the hover line), where each Drain
/// card's Drain lands, the turn's coming drains, Facade's count, and the
/// Rising Applause telemetry row. Fanfare's tip (change 5) is not built: the
/// text lint allows no parentheses in a tip. No number or
/// rule moves.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaHpLegibilityTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public FurinaHpLegibilityTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
        FurinaSweep.ClearAll();
    }

    public void Dispose()
    {
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
        FurinaSweep.ClearAll();
    }

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    /// <summary>A ledger opened at 78 of 78: a 19 HP buffer.</summary>
    private static FurinaStageLedger Ledger(StageMods? mods = null)
    {
        var ledger = FurinaStageLedger.Detached();
        ledger.ModsOverride = mods ?? StageMods.None;
        ledger.Open(78, 78);
        return ledger;
    }

    // ---- change 2: every Drain card says where its Drain lands --------------

    [Fact]
    public void The_drain_tag_has_three_forms_and_keeps_the_five_century_one()
    {
        Assert.Equal("\n(Returns after combat)",
                     FurinaStageFacePreview.DrainTag(4, 0));
        Assert.Equal("\n(Past your line: lost unless you Repay)",
                     FurinaStageFacePreview.DrainTag(0, 4));
        Assert.Equal("\n(2 returns, 3 past your line)",
                     FurinaStageFacePreview.DrainTag(2, 3));
        // Under A Five-Century Act the past-line part returns too.
        Assert.Equal("\n(Past your Drain buffer: returns after combat)",
                     FurinaStageFacePreview.DrainTag(2, 3, pastReturns: true));
        Assert.Equal(FurinaStageFacePreview.PastLineReturns,
                     FurinaStageFacePreview.DrainTag(0, 4, pastReturns: true));
        Assert.Equal(FurinaStageFacePreview.ReturnsTag,
                     FurinaStageFacePreview.DrainTag(4, 0, pastReturns: true));
        Assert.Equal("", FurinaStageFacePreview.DrainTag(0, 0));
    }

    [Fact]
    public void A_drain_card_in_hand_tags_inside_split_and_past()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsOusiaPledge());          // Drain 3
            var ledger = FurinaStageLedger.For(b.Furina.Creature);
            var hp = (int)b.Furina.Creature.CurrentHp;
            Assert.Equal(FurinaStageFacePreview.ReturnsTag,
                         FurinaStageFacePreview.DrainLine(b.Card, 3));
            // 1 HP of buffer left: 1 returns, 2 past.
            ledger.NoteDrain(ledger.BufferLeft - 1, hp);
            Assert.Equal("\n(1 returns, 2 past your line)",
                         FurinaStageFacePreview.DrainLine(b.Card, 3));
            // None left: all past.
            ledger.NoteDrain(1, hp);
            Assert.Equal(FurinaStageFacePreview.PastLineLost,
                         FurinaStageFacePreview.DrainLine(b.Card, 3));
            ledger.ModsOverride = new StageMods { FiveCenturyAct = 1 };
            Assert.Equal(FurinaStageFacePreview.PastLineReturns,
                         FurinaStageFacePreview.DrainLine(b.Card, 3));
        });
    }

    // ---- change 1: the returning HP -----------------------------------------

    [Fact]
    public void The_returning_hp_is_the_drain_inside_the_buffer()
    {
        var ledger = Ledger();
        Assert.Equal(19, ledger.Buffer);
        ledger.NoteDrain(4, 78);
        Assert.Equal(4, ledger.ReturningAt(74, 78));
        // Past the line: only the 19 inside the buffer returns.
        ledger.NoteDrain(20, 74);
        Assert.Equal(19, ledger.DrainedAbove);
        Assert.Equal(5, ledger.DrainedPast);
        Assert.Equal(19, ledger.ReturningAt(54, 78));
        // Never past Max HP.
        Assert.Equal(2, ledger.ReturningAt(76, 78));
        // It is the curtain call's own number, read without emptying it.
        Assert.Equal(ledger.ReturningAt(54, 78),
                     ledger.CurtainCallOf(54, 78).Back);
    }

    [Fact]
    public void Under_a_five_century_act_the_past_line_drain_returns_too()
    {
        var ledger = Ledger(new StageMods { FiveCenturyAct = 1 });
        ledger.NoteDrain(24, 78);
        Assert.Equal(5, ledger.DrainedPast);
        Assert.Equal(24, ledger.ReturningAt(54, 78));
        Assert.Equal(24, ledger.CurtainCallOf(54, 78).Back);
    }

    [Fact]
    public void The_bar_segment_spans_current_hp_to_the_returning_hp()
    {
        var span = FurinaReturningHpBar.Span(50, 78, 4)!.Value;
        Assert.Equal(50f / 78, span.Left, 5);
        Assert.Equal(54f / 78, span.Right, 5);
        Assert.Equal(1f, FurinaReturningHpBar.Span(76, 78, 4)!.Value.Right, 5);
        Assert.Null(FurinaReturningHpBar.Span(50, 78, 0));
        Assert.Null(FurinaReturningHpBar.Span(78, 78, 4));
        Assert.Null(FurinaReturningHpBar.Span(0, 78, 4));
        Assert.Equal(0, FurinaReturningHpBar.Returning(null));
    }

    // ---- changes 1 and 3: the Drained counter's hover -------------------------

    [Fact]
    public void The_hover_says_what_returns_and_the_drains_to_come()
    {
        Assert.Equal("Returns after combat: [blue]7[/blue]",
                     DrainedCounter.ReturnsLine(7));
        Assert.Equal("At end of turn: guests Drain [blue]2[/blue]\n"
                     + "Next turn: Regina Drains [blue]3[/blue]\n",
                     DrainedCounter.ComingLines(2, 3));
        Assert.Equal("", DrainedCounter.ComingLines(0, 0));
        var body = DrainedCounter.HoverBody(7, 12, returning: 7, guestDrain: 2,
                                            reginaDrain: 3);
        Assert.Contains(".\nReturns after combat: [blue]7[/blue]\n"
                        + "At end of turn: guests Drain [blue]2[/blue]\n"
                        + "Next turn: Regina Drains [blue]3[/blue]\n"
                        + ArmKeywordTipsDrainBody(), body);
        Assert.DoesNotContain("At end of turn",
                              DrainedCounter.HoverBody(7, 12, returning: 7));
    }

    private static string ArmKeywordTipsDrainBody() =>
        (string)typeof(ArmKeywordTips).GetField("DrainBody", HeadlessGame.All)!
            .GetRawConstantValue()!;

    [Fact]
    public void The_coming_drains_read_lyney_and_regina_from_their_sources()
    {
        var ledger = Ledger();
        Assert.Equal(0, DrainedCounter.GuestDrainAtTurnEnd(ledger, 78));
        ledger.Seat(StagePerformer.Lyney);
        Assert.Equal(FurinaStageLaw.LyneyActDrain,
                     DrainedCounter.GuestDrainAtTurnEnd(ledger, 78));
        // Stopped at the line: 1 HP of buffer left.
        ledger.NoteDrain(ledger.BufferLeft - 1, 78);
        Assert.Equal(1, DrainedCounter.GuestDrainAtTurnEnd(ledger, 50));
        // Never to 0 HP.
        Assert.Equal(0, DrainedCounter.GuestDrainAtTurnEnd(ledger, 1));

        Assert.Equal(FurinaStageLaw.ReginaDrain,
                     DrainedCounter.ReginaDrainNextTurn(1, 10));
        Assert.Equal(4, DrainedCounter.ReginaDrainNextTurn(2, 4));
        Assert.Equal(1, DrainedCounter.ReginaDrainNextTurn(1, 10, 9));
        Assert.Equal(0, DrainedCounter.ReginaDrainNextTurn(0, 10));
        Assert.Equal(0, DrainedCounter.ReginaDrainNextTurn(1, 2, 2));
    }

    // ---- change 4: Facade ------------------------------------------------------

    [Fact]
    public void Facade_says_drain_counts_and_prints_its_count_in_combat()
    {
        var face = ((BaseLib.Abstracts.CustomCardModel)new ProtoFsFacade())
            .Localization!.Single(p => p.Item1 == "description").Item2;
        Assert.StartsWith(
            "Gain [gold]Block[/gold] equal to the HP you have lost this "
            + "combat, Drain included, up to {FsAmount:diff()}.", face);
        Assert.EndsWith("{InCombat:{StageLost}|}", face);
        Assert.Equal("\n(Lost this combat: 7)",
                     FurinaStageFacePreview.LostThisCombatWords(7));
        Assert.Equal("", FurinaStageFacePreview.LostThisCombat(new ProtoFsFacade()));
        InCombat(() =>
        {
            var b = Build(new ProtoFsFacade());
            Assert.Equal("\n(Lost this combat: 0)",
                         FurinaStageFacePreview.LostThisCombat(b.Card));
            FurinaSweep.NoteHpLoss(b.Furina.Creature, 5);
            Assert.Equal("\n(Lost this combat: 5)",
                         FurinaStageFacePreview.LostThisCombat(b.Card));
        });
    }

    // ---- the starter pick's telemetry row ----------------------------------------

    [Fact]
    public void A_rising_applause_play_files_the_other_spend_cards_in_hand()
    {
        var furina = Seat.Furina(80).WithCombatState();
        var combat = DispatchProxy.Create<ICombatState, ListenerProxy>();
        furina.Creature.CombatState = combat;
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        FurinaStageLedger.For(furina.Creature).Gain(12);
        Invoke("RecordRisingApplausePlay", furina.Player, 2,
               new[] { "Bravura", "Bring the House Down+" });
        Invoke("RecordRisingApplausePlay", furina.Player, 3,
               Array.Empty<string>());
        var root = JsonDocument.Parse(
            (string)Invoke("JsonForTest", furina.Player)!).RootElement;
        var rows = root.GetProperty("rising_applause_plays")
            .EnumerateArray().ToArray();
        Assert.Equal(2, rows.Length);
        Assert.Equal(2, rows[0][0].GetInt32());
        Assert.Equal(12, rows[0][1].GetInt32());
        Assert.Equal(new[] { "Bravura", "Bring the House Down+" },
                     rows[0][2].EnumerateArray().Select(v => v.GetString()));
        Assert.Equal(0, rows[1][2].GetArrayLength());

        // Anyone else writes no key.
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("RecordRisingApplausePlay", klee.Player, 1, new[] { "Strike" });
        var kr = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.False(kr.TryGetProperty("rising_applause_plays", out _));
    }
}
