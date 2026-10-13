using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE VARKA WAVE'S DEFECTS (<c>review/records/varka-wave-2026-10-13.md</c>,
/// "To change"), the C# halves pinned by their call graph. The generated
/// text halves are <c>tier0/tests/test_varka_wave_defects_2026_10_13.py</c>.
/// </summary>
public class VarkaWaveDefectsTests
{
    [Fact]
    public void Stoke_the_flames_says_what_it_added_on_the_attacks_play_line()
    {
        // "I never saw the number change in the log, and could not tell if
        // Four Winds' Pyro half qualified." It does; now the power flashes
        // and files a `stoked` event on that play's own row.
        Assert.Equal("stoked", ResolutionLedger.Stoked);
        var after = Il.CallSequence(
            Il.Method("StokeTheFlamesPower", "AfterCardPlayed")).ToList();
        Assert.Contains("ResolutionLedger.NoteEventOnPlay", after);
        Assert.Contains("PowerModel.Flash", after);
    }

    [Fact]
    public void An_enemy_power_is_subscribed_once_however_often_it_is_watched()
    {
        // "Ravenous fired x2" on one death: the watched set is cleared at
        // BeforeCombatStart after a power applied as the room was built had
        // already subscribed, so a second sweep subscribed it again. Watch
        // unsubscribes first.
        var watch = Il.CallSequence(Il.Method("PlayTelemetryHooks", "Watch")).ToList();
        var remove = watch.IndexOf("PowerModel.remove_Flashed");
        var add = watch.IndexOf("PowerModel.add_Flashed");
        Assert.True(remove >= 0 && add > remove, string.Join(", ", watch));
    }
}
