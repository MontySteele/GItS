using System.Linq;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// DEATH TEARDOWN, pinned on the BASE GAME because that is whose machinery
/// decides it. STRUCTURAL, and labelled: reproducing it needs a live combat, a
/// kill and a hook broadcast.
///
/// Moved here from <c>BombInstancingTests</c> when the old shipped
/// <c>BombPower</c> those tests covered was deleted (2026-10-19). The three
/// facts outlive it: <c>ProtoBombPower</c> and <c>KleeOverhaulSweep</c> lean
/// on the same kill order in their own notes. The finding (sts2.dll v0.107.1):
///   1. death runs INLINE inside the damage command;
///   2. the kill detaches the corpse from the combat AND strips its powers;
///   3. the hook broadcast re-tests every listener against the combat before
///      handing it the hook, and for a power that test reads the owner's
///      `CombatState`.
/// If a game update moves any of these three, the finding is stale and this
/// test is the notice.
/// </summary>
public class DeathTeardownEngineTests
{
    [Fact]
    public void Death_resolves_inside_the_damage_command()
    {
        var damage = Game("CreatureCmd")
            .GetMethods(HeadlessGame.All)
            .Where(m => m.Name == "Damage")
            .Select(Il.Calls)
            .ToList();

        Assert.Contains(
            damage,
            calls => calls.Contains("CreatureCmd.Kill")
                     && calls.Contains("Hook.AfterDamageReceived"));
    }

    [Fact]
    public void A_kill_detaches_the_corpse_and_strips_its_powers()
    {
        var calls = Il.Calls(
            Game("CreatureCmd")
                .GetMethod("KillWithoutCheckingWinCondition", HeadlessGame.All)!);

        Assert.Contains("ICombatState.RemoveCreature", calls);
        Assert.Contains("Creature.RemoveAllPowersAfterDeath", calls);
    }

    [Fact]
    public void The_hook_broadcast_retests_every_listener_against_the_combat()
    {
        var iterator = Il.Calls(
            Game("CombatState").GetMethod("IterateHookListeners", HeadlessGame.All)!);
        var contains = Il.Calls(
            Game("CombatState").GetMethod("Contains", HeadlessGame.All)!);

        Assert.Contains("Creature.get_Powers", iterator);
        Assert.Contains("CombatState.Contains", iterator);
        Assert.Contains("Creature.get_CombatState", contains);
    }

    private static System.Type Game(string typeName) =>
        typeof(Creature).Assembly.GetTypes().First(t => t.Name == typeName);
}
