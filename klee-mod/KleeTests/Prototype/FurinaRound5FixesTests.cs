using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA WHOLE-RUN ROUND 5 (2026-10-11), the review's no-approval changes:
/// Lyney's badge in the Drain buffer's words, and two telemetry reads (the
/// Spend cards in hand at each turn start by name, and the enemies alive as
/// each Spend card is played). No rule or number moves. Python twin:
/// <c>tier0/tests/test_furina_round_5_fixes.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaRound5FixesTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public FurinaRound5FixesTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    public void Dispose()
    {
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    // ---- Lyney in buffer words -------------------------------------------------

    [Fact]
    public void Lyneys_badge_says_his_buffer_is_larger()
    {
        var text = StagePerformerBadge.ActText(StagePerformer.Lyney);
        Assert.StartsWith("Your [gold]Drain[/gold] buffer is "
                          + FurinaStageLaw.LyneyLineDrop + " HP larger. Act: ",
                          text);
        Assert.DoesNotContain("HP lower", text);
        // The rule it names: he adds 10 to her buffer.
        Assert.Equal(FurinaStageLaw.BufferOf(80) + FurinaStageLaw.LyneyLineDrop,
                     FurinaStageLaw.BufferOf(80, lyney: true));
    }

    [Fact]
    public void Lyneys_face_names_his_acts_drain()
    {
        var face = ((BaseLib.Abstracts.CustomCardModel)new ProtoFsGuestStarLyney())
            .Localization!.Single(p => p.Item1 == "description").Item2;
        Assert.Contains("Act: [gold]Drain[/gold] "
                        + FurinaStageLaw.LyneyActDrain + " and deal ", face);
    }

    // ---- telemetry: the Spend cards by name, and the enemies alive --------------

    private static (Seat Seat, JsonElement Root) FurinaRecord(Action<Seat> fill)
    {
        var furina = Seat.Furina(80).WithCombatState();
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        furina.Creature.CombatState = combat;
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        FurinaStageLedger.For(furina.Creature);
        fill(furina);
        var root = JsonDocument.Parse(
            (string)Invoke("JsonForTest", furina.Player)!).RootElement;
        return (furina, root);
    }

    [Fact]
    public void The_spend_cards_in_hand_are_named_in_hand_order()
    {
        var names = (string[])Invoke("SpendCardNames", new List<CardModel>
        {
            new ProtoFsTidalFlourish(), new ProtoFsCurtainRise(),
            new ProtoFsBravura(), new ProtoFsShowstopper(),
        })!;
        // Tidal Flourish and Bravura; a headless card has no title to
        // read, so the names are the fallback and only the count is pinned.
        Assert.Equal(2, names.Length);
        Assert.Empty((string[])Invoke("SpendCardNames",
                                      new object?[] { null })!);
    }

    [Fact]
    public void A_furina_fight_writes_the_names_at_each_turn_start()
    {
        var (_, r) = FurinaRecord(f =>
        {
            Invoke("RecordSpendCardNamesTurnStart", f.Player, 1,
                   Array.Empty<string>());
            Invoke("RecordSpendCardNamesTurnStart", f.Player, 2,
                   new[] { "Standing Ovation", "Spirited Aria+" });
        });
        var rows = r.GetProperty("spend_card_names_turn_start")
            .EnumerateArray().ToArray();
        Assert.Equal(2, rows.Length);
        Assert.Equal(1, rows[0][0].GetInt32());
        Assert.Equal(0, rows[0][1].GetArrayLength());
        Assert.Equal(2, rows[1][0].GetInt32());
        Assert.Equal(new[] { "Standing Ovation", "Spirited Aria+" },
                     rows[1][1].EnumerateArray().Select(v => v.GetString()));
    }

    [Fact]
    public void A_furina_fight_writes_each_spend_card_play_with_enemies_alive()
    {
        var (_, r) = FurinaRecord(f =>
        {
            Invoke("RecordSpendCardPlay", f.Player, 1, "Standing Ovation", 4);
            Invoke("RecordSpendCardPlay", f.Player, 3, "Bravura+", 1);
        });
        var rows = r.GetProperty("spend_card_plays").EnumerateArray().ToArray();
        Assert.Equal(2, rows.Length);
        Assert.Equal(1, rows[0][0].GetInt32());
        Assert.Equal("Standing Ovation", rows[0][1].GetString());
        Assert.Equal(4, rows[0][2].GetInt32());
        Assert.Equal("Bravura+", rows[1][1].GetString());
        Assert.Equal(1, rows[1][2].GetInt32());
        // A play at 0 Fanfare spends nothing: no `fanfare_spends` row, and
        // its `spend_card_plays` row still stands.
        Assert.Equal(0, r.GetProperty("fanfare_spends").GetArrayLength());
    }

    [Fact]
    public void Anyone_else_writes_neither_key()
    {
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("RecordSpendCardNamesTurnStart", klee.Player, 1,
               new[] { "Strike" });
        Invoke("RecordSpendCardPlay", klee.Player, 1, "Strike", 2);
        var kr = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.False(kr.TryGetProperty("spend_card_names_turn_start", out _));
        Assert.False(kr.TryGetProperty("spend_card_plays", out _));
    }
}
