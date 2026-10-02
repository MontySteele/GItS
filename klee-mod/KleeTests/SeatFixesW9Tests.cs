#nullable enable

using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// 2026-10-01 seat round, hygiene fixes: the screen tells the truth.
/// </summary>
public class SeatFixesW9Tests
{
    // ---- Vigor on a per-target ALL-enemies attack ------------------------

    [Fact]
    public void Aoe_vigor_pays_the_first_hit_natively_and_carries_to_the_rest()
    {
        // Crashing Waves with Vigor 8 previewed 16 to ALL and landed
        // 16/8/8/8. The first command takes Vigor the base game's way; each
        // later one adds the Vigor read before the sweep.
        var seat = Seat.Furina().WithPower<VigorPower>(8);
        var carry = AoeVigor.Begin(seat.Creature);
        Assert.Equal(new[] { 0, 8, 8, 8 },
                     Enumerable.Range(0, 4).Select(_ => carry.Next()).ToArray());
    }

    [Fact]
    public void Aoe_vigor_without_vigor_adds_nothing()
    {
        var carry = AoeVigor.Begin(Seat.Furina().Creature);
        Assert.Equal(new[] { 0, 0, 0 },
                     Enumerable.Range(0, 3).Select(_ => carry.Next()).ToArray());
    }

    [Theory]
    [InlineData("Cards/Prototype/Generated/ProtoFsCrashingWaves.cs")]
    [InlineData("Cards/Prototype/Generated/ProtoKkRiptide.cs")]
    public void Per_target_aoe_attacks_carry_vigor(string file)
    {
        var src = Source(file);
        Assert.Contains("var aoeVigor = AoeVigor.Begin(Owner.Creature);", src);
        Assert.Contains("+ aoeVigor.Next())", src);
    }

    private static string Source(string relative,
                                 [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here)!;
        var root = Path.GetFullPath(Path.Combine(dir, "..", "KleeCode"));
        return File.ReadAllText(Path.Combine(root, relative));
    }
}
