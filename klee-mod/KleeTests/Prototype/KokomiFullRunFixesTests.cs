using System;
using System.Linq;
using System.Text.Json;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI WHOLE-RUN ROUND'S TELEMETRY
/// (<c>review/records/kokomi-fullrun-round-2026-10-10.md</c>, "What changes"
/// item 3): per Kokomi fight, the Casket's count as each turn opens and the
/// Plans written and carried out. The card retunes are pinned where each row
/// was already pinned; the page fixes in
/// <c>tier0/tests/test_kokomi_fullrun_fixes_2026_10_10.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class KokomiFullRunFixesTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public KokomiFullRunFixesTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
        KokomiOverhaulLedger.ResetAll();
    }

    public void Dispose()
    {
        Invoke("ResetForTest");
        KokomiOverhaulLedger.ResetAll();
    }

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    [Fact]
    public void A_kokomi_fight_writes_the_casket_at_each_turn_start_and_her_plan_counts()
    {
        var kokomi = Seat.Kokomi().WithRelic<TamakushiCasket>();
        Invoke("OpenSeatForTest", kokomi.Player, 1, 0);

        // No ledger yet: the read creates none and the count reads 0.
        Invoke("RecordTurnStartForTest", 1);
        Assert.Null(KokomiOverhaulLedger.Peek(kokomi.Creature));

        var ledger = KokomiOverhaulLedger.For(kokomi.Creature);
        ledger.NotePlanWritten();
        ledger.NotePlanWritten();
        ledger.NotePlanCarriedOut();
        TamakushiCasket.NoteCarriedOut(kokomi.Creature);
        ledger.RollTo(2);   // the per-turn counts roll; the per-combat ones do not
        ledger.NotePlanWritten();
        Invoke("RecordTurnStartForTest", 2);

        var r = JsonDocument.Parse((string)Invoke("JsonForTest", kokomi.Player)!)
            .RootElement;
        var rows = r.GetProperty("casket_turn_start").EnumerateArray()
            .Select(row => row.EnumerateArray().Select(v => v.GetInt32()).ToArray())
            .ToArray();
        Assert.Equal(new[] { new[] { 1, 0 }, new[] { 2, 1 } }, rows);
        Assert.Equal(3, r.GetProperty("plans_written").GetInt32());
        Assert.Equal(1, r.GetProperty("plans_carried_out").GetInt32());

        // Anyone else writes none of the three keys.
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("RecordTurnStartForTest", 1);
        var kr = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.False(kr.TryGetProperty("casket_turn_start", out _));
        Assert.False(kr.TryGetProperty("plans_written", out _));
        Assert.False(kr.TryGetProperty("plans_carried_out", out _));
    }
}
