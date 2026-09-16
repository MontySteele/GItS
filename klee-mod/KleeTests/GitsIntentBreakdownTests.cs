using System.Collections.Generic;
using STS2_MCP;
using Xunit;

namespace KleeTests;

/// <summary>
/// `EB-607` / `EB-323`. The two decisions behind an intent's missing facts,
/// pinned headlessly off the same file the bridge compiles.
///
/// WHY HERE. `GitsIntentBreakdown.cs` names no game type, which is what makes
/// it testable at all -- and both of its decisions have exactly one way to look
/// right and be wrong. A breakdown composed for a part that declares no repeat
/// would put a row of zeroes on a page and a reader would take it for a
/// reading; an `IntentType` value filed on the wrong side would tell a seat to
/// block against a buff, or not to block against an attack, and both look
/// identical to every smoke test that does not happen to meet that move.
///
/// ONE FILE, NO FORK: the csproj compiles the vendored source, so a change
/// there that breaks a clause breaks this.
/// </summary>
public class GitsIntentBreakdownTests
{
    [Fact]
    public void ComposePutsAllFiveNumbersOnTheBlock()
    {
        var block = GitsIntentBreakdown.Compose(
            6, 9, 2, new[] { "Strength" });
        Assert.NotNull(block);
        Assert.Equal(6, block![GitsIntentBreakdown.BaseKey]);
        Assert.Equal(9, block[GitsIntentBreakdown.FoldedKey]);
        Assert.Equal(2, block[GitsIntentBreakdown.RepeatsKey]);
        Assert.Equal(18, block[GitsIntentBreakdown.TotalKey]);
        Assert.Equal(new List<string> { "Strength" },
                     block[GitsIntentBreakdown.ModifiersKey]);
    }

    /// <summary>The Fossil Stalker reading: an icon nothing was folded into.
    /// Base and folded agree and the modifier list is empty, which is a FACT
    /// about the board and the thing the r23 seat could not tell from an icon
    /// that had moved.</summary>
    [Fact]
    public void AnIconNothingWasFoldedIntoSaysSoWithAnEmptyList()
    {
        var block = GitsIntentBreakdown.Compose(12, 12, 1, null);
        Assert.NotNull(block);
        Assert.Equal(block![GitsIntentBreakdown.BaseKey],
                     block[GitsIntentBreakdown.FoldedKey]);
        Assert.Empty((List<string>)block[GitsIntentBreakdown.ModifiersKey]!);
    }

    /// <summary>A part that declares no repeat is every non-attack intent, and
    /// a block of zeroes under one would be read as a reading.</summary>
    [Fact]
    public void NoRepeatIsNoBlockAtAll()
    {
        Assert.Null(GitsIntentBreakdown.Compose(0, 0, 0, null));
        Assert.Null(GitsIntentBreakdown.Compose(5, 5, -1, null));
    }

    [Fact]
    public void BlankModifierNamesAreDropped()
    {
        var block = GitsIntentBreakdown.Compose(
            6, 6, 1, new[] { "", "  ", " Strength " });
        Assert.Equal(new List<string> { "Strength" },
                     block![GitsIntentBreakdown.ModifiersKey]);
    }

    [Theory]
    [InlineData("Attack")]
    [InlineData("Debuff")]
    [InlineData("DebuffStrong")]
    [InlineData("StatusCard")]
    [InlineData("CardDebuff")]
    [InlineData("DeathBlow")]
    public void TheseLandOnThePlayer(string type) =>
        Assert.Equal(GitsIntentBreakdown.SideYou,
                     GitsIntentBreakdown.TargetSide(type));

    [Theory]
    [InlineData("Buff")]
    [InlineData("Defend")]
    [InlineData("Heal")]
    [InlineData("Summon")]
    public void TheseLandOnTheEnemysOwnSide(string type) =>
        Assert.Equal(GitsIntentBreakdown.SideEnemy,
                     GitsIntentBreakdown.TargetSide(type));

    /// <summary>The five that settle nothing. NULL keeps the wire key absent
    /// and the page exactly as it was; a guess here is the one failure this
    /// file exists to refuse.</summary>
    [Theory]
    [InlineData("Escape")]
    [InlineData("Sleep")]
    [InlineData("Stun")]
    [InlineData("Hidden")]
    [InlineData("Unknown")]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("SomethingTheGameAddedLater")]
    public void TheseSettleNothingAndSayNothing(string? type) =>
        Assert.Null(GitsIntentBreakdown.TargetSide(type));
}
