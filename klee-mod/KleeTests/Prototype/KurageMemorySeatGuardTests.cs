using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE SEAT THAT IS NOT IN THE COMBAT YET, and the two blind-play sessions it
/// ended (`KLEESPARK-W1`, `KLEESPARK-W2`, both `termination: tool_blocked` at
/// the first frame of their SECOND Monster room).
///
/// The whole defect is one wrong reading of one game API.
/// <c>LocalContext.GetMe(ICombatState)</c> looks like a lookup that answers
/// null on a miss. It is not: its entire body is "no <c>NetId</c> -> null;
/// otherwise <c>state.GetPlayer(NetId.Value)</c>, and a miss THROWS
/// <c>InvalidOperationException("Local player not found in combat.")</c>".
/// `KurageMemoryCard` called it from three places, each with an `is null`
/// guard underneath that could never fire, and one of those three is a
/// Harmony postfix on <c>NCombatUi.Deactivate</c> — which
/// <c>NCombatRoom._Ready</c> calls while the NEXT combat room is still being
/// built and its combat still has no players in it.
///
/// What that cost, off `%APPDATA%\SlayTheSpire2\logs\godot.log` for W2:
/// the throw escaped `_Ready`, so the room never finished readying and
/// `CombatVfxContainer` stayed null; `NCombatUi.Activate` ran a frame later,
/// `TrackedDisplayBridge.Spawn` NRE'd on the null container, and THAT escaped
/// `CombatManager.SetUpCombat` — `[ERROR] GameAction MoveToMapCoordAction 1
/// MapCoord (0, 2) completed with exception`. The fight was never set up, so
/// the bridge answered `state_type: monster` with no `battle` block forever
/// and the blind-play driver reported the screen blocked.
///
/// Both halves are pinned here, because either one alone still loses the run.
/// </summary>
public class KurageMemorySeatGuardTests
{

    /// <summary>A combat that exists but holds no seats — the state
    /// `NCombatRoom._Ready` hands our Deactivate postfix on the way into the
    /// next fight.</summary>
    private static CombatState EmptyFight()
    {
        var fight = (CombatState)RuntimeHelpers.GetUninitializedObject(
            typeof(CombatState));
        foreach (var name in new[] { "_allies", "_enemies", "_escapedCreatures" })
        {
            typeof(CombatState)
                .GetField(name, BindingFlags.Instance | BindingFlags.NonPublic)!
                .SetValue(fight, new List<Creature>());
        }
        return fight;
    }

    /// <summary>The game's contract, pinned so nobody re-reads it as a
    /// null-answering lookup a third time.</summary>
    [Fact]
    public void GetMe_throws_rather_than_answering_null_when_the_seat_is_absent()
    {
        var previous = LocalContext.NetId;
        LocalContext.NetId = 7UL;
        try
        {
            var thrown = Assert.Throws<InvalidOperationException>(
                () => LocalContext.GetMe(EmptyFight()));
            Assert.Equal("Local player not found in combat.", thrown.Message);
        }
        finally
        {
            LocalContext.NetId = previous;
        }
    }

}
