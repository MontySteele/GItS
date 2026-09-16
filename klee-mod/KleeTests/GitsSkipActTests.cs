#nullable enable

using System.Collections.Generic;
using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-771. THE DECISION `skip_act` MAKES, PINNED HEADLESSLY.
///
/// The op presses the boss-rewards Proceed button one floor early --
/// `RunManager.Instance.ActChangeSynchronizer.SetLocalPlayerReady()` -- so the
/// act it lands in is `RunState.Acts[CurrentActIndex + 1]`, the dressed face
/// this seed's own act roll already chose at embark. Everything the op decides
/// before making that call is in `vendor/STS2_MCP/gits/GitsSkipAct.cs`, which
/// is deliberately free of Godot, Harmony and game types so this file can
/// compile THAT source (not a fork of it), exactly as `GitsForceEventTests`
/// does for the event cursor.
///
/// WHAT THESE PINS ARE FOR. Three of the four refusals are states that are
/// EXPENSIVE to reach deliberately with a live game -- a run standing in an
/// event's own sub-combat, a run in its victory room, a run in its last act --
/// which is to say they are exactly the refusals that would otherwise be
/// discovered by an attended session losing its run to them. The fourth, the
/// last act, is the one that would not look like a failure at all: the native
/// `EnterNextAct` does not refuse there, it opens The Architect's room, so an
/// op without this check would answer `ok` and put the run somewhere nobody
/// asked for. EB-771 adds no act-4 path.
/// </summary>
public class GitsSkipActTests
{
    /// <summary>A three-act run with the Teyvat arm on: act 1 Mondstadt, and
    /// the act-2/act-3 faces this seed's roll chose out of each pair.</summary>
    private static List<string> Acts() => new()
    {
        "MONDSTADT", "NATLAN", "FONTAINE"
    };

    private static GitsSkipAct.Decision OnMap(int index)
        => GitsSkipAct.Decide(Acts(), index, inCombat: false,
                              inVictoryRoom: false, roomDepth: 1);

    // ------------------------------------------------------- the happy path

    [Fact]
    public void ItStepsOneActAndNamesTheFaceTheRunAlreadyHolds()
    {
        var d = OnMap(0);
        Assert.True(d.Allowed);
        Assert.Equal("", d.Refusal);
        Assert.Equal(0, d.FromIndex);
        Assert.Equal(1, d.ToIndex);
        Assert.Equal("MONDSTADT", d.FromAct);
        // READ OUT OF THE RUN'S LIST, never rolled here. The act roll happened
        // once at embark; if this value came from anywhere else the op would
        // be minting a run shape instead of reaching one.
        Assert.Equal("NATLAN", d.ToAct);
        Assert.Equal(3, d.ActCount);
    }

    [Fact]
    public void ItStepsFromActTwoToActThreeTheSameWay()
    {
        var d = OnMap(1);
        Assert.True(d.Allowed);
        Assert.Equal(1, d.FromIndex);
        Assert.Equal(2, d.ToIndex);
        Assert.Equal("NATLAN", d.FromAct);
        Assert.Equal("FONTAINE", d.ToAct);
    }

    // ------------------------------------------------------- the refusals --

    [Fact]
    public void TheLastActIsRefusedAndNoActFourIsInvented()
    {
        // `RunManager.EnterNextAct` does NOT advance here -- it enters
        // The Architect's event room. An op that let the native call run would
        // answer ok and land the run somewhere it was not asked to go.
        var d = OnMap(2);
        Assert.False(d.Allowed);
        Assert.Equal(GitsSkipAct.LastActRefusal, d.Refusal);
        Assert.Equal(2, d.FromIndex);
        Assert.Equal(-1, d.ToIndex);
        Assert.Equal("MONDSTADT", Acts()[0]);   // the list itself is untouched
        Assert.Contains("act-4", d.Refusal);
    }

    [Fact]
    public void ACombatInProgressIsRefusedInItsOwnWords()
    {
        // `skip_act` sits on `GitsDebugStateOutOfCombatOps`, which bypasses the
        // route's GENERIC combat refusal -- so this refusal has to be made
        // here or it is not made at all.
        var d = GitsSkipAct.Decide(Acts(), 0, inCombat: true,
                                   inVictoryRoom: false, roomDepth: 1);
        Assert.False(d.Allowed);
        Assert.Contains("combat", d.Refusal);
        Assert.Equal(-1, d.ToIndex);
    }

    [Fact]
    public void AStackedSubRoomIsRefused()
    {
        // `CurrentRoomCount > 1` is an event that started its own fight: the
        // run still expects to return to the room underneath.
        var d = GitsSkipAct.Decide(Acts(), 0, inCombat: false,
                                   inVictoryRoom: false, roomDepth: 2);
        Assert.False(d.Allowed);
        Assert.Contains("sub-room", d.Refusal);
    }

    [Fact]
    public void TheVictoryRoomIsRefused()
    {
        var d = GitsSkipAct.Decide(Acts(), 0, inCombat: false,
                                   inVictoryRoom: true, roomDepth: 1);
        Assert.False(d.Allowed);
        Assert.Contains("victory room", d.Refusal);
    }

    // ------------------------------------------- shapes that cannot crash --

    [Fact]
    public void ARunWithNoActsIsARefusalAndNotAnIndexError()
    {
        var d = GitsSkipAct.Decide(new List<string>(), 0, false, false, 1);
        Assert.False(d.Allowed);
        Assert.Equal(0, d.ActCount);
        Assert.Equal(-1, d.ToIndex);
    }

    [Fact]
    public void ANullActListIsARefusalAndNotAThrow()
    {
        var d = GitsSkipAct.Decide(null!, 0, false, false, 1);
        Assert.False(d.Allowed);
        Assert.Equal(0, d.ActCount);
    }

    [Theory]
    [InlineData(-1)]
    [InlineData(3)]
    [InlineData(99)]
    public void AnIndexOutsideTheActListIsARefusalNamingIt(int index)
    {
        var d = GitsSkipAct.Decide(Acts(), index, false, false, 1);
        Assert.False(d.Allowed);
        Assert.Contains(index.ToString(), d.Refusal);
        Assert.Equal(-1, d.ToIndex);
    }

    [Fact]
    public void CombatIsCheckedBeforeTheLastActSoTheLoudestProblemIsNamedFirst()
    {
        // Both are true; the caller most needs to hear the one it can act on
        // right now, and a run in a fight has not yet learned it is in the
        // last act.
        var d = GitsSkipAct.Decide(Acts(), 2, inCombat: true,
                                   inVictoryRoom: false, roomDepth: 1);
        Assert.False(d.Allowed);
        Assert.Contains("combat", d.Refusal);
    }

    [Fact]
    public void ASingleActRunCanNeverSkip()
    {
        var d = GitsSkipAct.Decide(new List<string> { "MONDSTADT" }, 0,
                                   false, false, 1);
        Assert.False(d.Allowed);
        Assert.Equal(GitsSkipAct.LastActRefusal, d.Refusal);
    }
}
