using System;
using System.IO;
using System.Text.RegularExpressions;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// The self-check's R11 (no Basic Strike/Defend for Large Capsule's
/// unguarded First()) logged six findings at every boot (godot.log
/// 2026-10-16): Klee, Furina and Kokomi "have no Basic card tagged Strike or
/// Defend". All five kits start on the base pair now, and every one is
/// answered by <c>ArmStarterBasics</c>, the seam Large Capsule and Fasten ask
/// first; the rule let only Varka and Yae through. ModelDb is not built in
/// this host (README, the headless boundary), so the rule cannot run here:
/// this pins its shape, that it asks the seam per tag and names no single
/// character.
/// </summary>
public class SelfCheckR11Tests
{
    private static string R11Block()
    {
        var src = RepoFile("klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs");
        var start = src.IndexOf("foreach (var tag in new[] { CardTag.Strike, CardTag.Defend })",
            StringComparison.Ordinal);
        Assert.True(start >= 0, "the R11 loop moved");
        var end = src.IndexOf("Fail(\"R11\"", start, StringComparison.Ordinal);
        Assert.True(end > start, "the R11 failure moved");
        return src.Substring(start, end - start);
    }

    [Fact]
    public void R11_asks_the_starter_seam_for_each_tag_for_every_character()
    {
        var block = R11Block();
        Assert.Contains("ArmStarterBasics.StrikeFor(character)", block);
        Assert.Contains("ArmStarterBasics.DefendFor(character)", block);
        Assert.DoesNotMatch(new Regex(@"character is Powers\.I\w+Character"), block);
        Assert.DoesNotContain("break;", block);
    }

    private static string RepoFile(string relativePath)
    {
        var relative = relativePath.Replace('/', Path.DirectorySeparatorChar);
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, relative);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = dir.Parent;
        }

        throw new FileNotFoundException(relative);
    }
}
