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

}
