#nullable enable

using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// ONE MACHINE, SEVERAL CO-OP PAIRS. The game hosts and dials `--fastmp` on a
/// literal 33771; `--gitsFastmpPort N` moves it per process. The contract:
/// no argument changes nothing, only the fastmp literal is moved, and a bad
/// value is refused out loud with the game's port left standing.
/// </summary>
public class GitsFastMpPortTests
{
    [Fact]
    public void NoArgumentLeavesTheGamesPort()
    {
        var choice = GitsFastMpPort.Resolve(33771, false, null);
        Assert.Equal(33771, choice.Port);
        Assert.Equal("game", choice.Source);
        Assert.Equal(33771, GitsFastMpPort.GameDefault);
        Assert.Equal("gitsFastmpPort", GitsFastMpPort.ArgName);
    }

    [Fact]
    public void TheArgumentMovesTheFastmpPort()
    {
        var choice = GitsFastMpPort.Resolve(33771, true, " 33772 ");
        Assert.Equal(33772, choice.Port);
        Assert.Equal("arg", choice.Source);
    }

    [Fact]
    public void AnotherRequestedPortIsLeftAlone()
    {
        var choice = GitsFastMpPort.Resolve(40000, true, "33772");
        Assert.Equal(40000, choice.Port);
        Assert.Equal("game", choice.Source);
    }

    [Fact]
    public void AnUnusableValueIsRefusedAndSaysSo()
    {
        foreach (var bad in new string?[] { null, "", "abc", "0", "70000", "-5" })
        {
            var choice = GitsFastMpPort.Resolve(33771, true, bad);
            Assert.Equal(33771, choice.Port);
            Assert.Equal("game", choice.Source);
            Assert.Contains("REFUSED", choice.Note);
        }
    }
}
