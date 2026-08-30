#nullable enable

using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// TWO GAME INSTANCES, ONE INSTALL, AND THE ONE THING THAT COULD NOT COME
/// FROM THE CONF FILE.
///
/// A live experiment (2026-08-29) proved two SlayTheSpire2.exe processes run
/// side by side out of one Steam install once each has its own APPDATA. The
/// bridge port was the hole: `STS2_MCP.conf` sits beside the mod dll INSIDE
/// the shared game directory, so two processes read one conf, want one port,
/// and the second listener loses. `STS2_MCP_PORT` is the per-process source,
/// and this is its contract: env, then conf, then the default -- with the
/// conf behaviour byte-identical to upstream's when the variable is absent,
/// which is the compatibility claim the whole single-instance funnel rests on.
/// </summary>
public class GitsPortPrecedenceTests
{
    private const string Conf = "{ \"port\": 15599 }";

    [Fact]
    public void TheEnvironmentWinsOverTheConf()
    {
        var choice = GitsPort.Resolve("15527", Conf);
        Assert.Equal(15527, choice.Port);
        Assert.Equal("env", choice.Source);
    }

    [Fact]
    public void TheConfWinsWhenTheEnvironmentIsAbsentOrBlank()
    {
        foreach (var absent in new string?[] { null, "", "   " })
        {
            var choice = GitsPort.Resolve(absent, Conf);
            Assert.Equal(15599, choice.Port);
            Assert.Equal("conf", choice.Source);
        }
    }

    [Fact]
    public void TheDefaultIsTheLastResort()
    {
        foreach (var noConf in new string?[] { null, "", "{}", "not json" })
        {
            var choice = GitsPort.Resolve(null, noConf);
            Assert.Equal(GitsPort.DefaultPort, choice.Port);
            Assert.Equal("default", choice.Source);
        }
        Assert.Equal(15526, GitsPort.DefaultPort);
    }

    /// <summary>
    /// AN UNUSABLE ENVIRONMENT VALUE FALLS THROUGH, AND SAYS SO. Binding the
    /// default silently would put a lane's bridge on the other lane's port,
    /// which is the failure this whole file exists to prevent -- so the note
    /// names the value that was refused.
    /// </summary>
    [Theory]
    [InlineData("0")]
    [InlineData("-1")]
    [InlineData("70000")]
    [InlineData("fifteen")]
    public void AnUnusableEnvironmentValueFallsThroughToTheConfAndIsNamed(
        string bad)
    {
        var choice = GitsPort.Resolve(bad, Conf);
        Assert.Equal(15599, choice.Port);
        Assert.Equal("conf", choice.Source);
        Assert.Contains(bad, choice.Note);
        Assert.Contains(GitsPort.EnvVar, choice.Note);
    }

    [Fact]
    public void TheEnvironmentVariableNameIsTheOneUnderstudySets()
    {
        // `understudy/instances.py` spells this string too; the Python suite
        // asserts the two agree, and this is the other half of that pin.
        Assert.Equal("STS2_MCP_PORT", GitsPort.EnvVar);
    }
}
