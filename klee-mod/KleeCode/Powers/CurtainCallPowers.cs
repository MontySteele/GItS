using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;

namespace KleeMod.Powers;

/// <summary>
/// The Curtain Call sweep's surviving activity windows (R85): the per-turn
/// HP-lost and intent reads their callers ask. The Salon and Encore halves
/// went with the shipped kits (legacy cleanup stage 5); Courtroom Drama's
/// first-reaction window and Quick Change's first-Attack draw went with their
/// powers, which no row applied (icon declutter leftovers, 2026-10-19).
/// </summary>
public static class CurtainCallHooks
{
    // Per-turn window, keyed by owner. Cleared at the top of Furina's turn;
    // a key whose combat is gone is dropped on every reset.
    private static readonly Dictionary<Creature, int> HpLost = new();

    private static int Get(Dictionary<Creature, int> map, Creature creature) =>
        map.TryGetValue(creature, out var value) ? value : 0;

    public static void ResetTurn(Creature creature)
    {
        HpLost.Remove(creature);
        Purge();
    }

    public static void NoteHpLost(Creature creature, int amount)
    {
        if (amount <= 0) return;
        HpLost[creature] = Get(HpLost, creature) + amount;
    }

    public static bool HpLostThisTurn(Creature creature) =>
        Get(HpLost, creature) > 0;

    public static bool EnemyIntendsAttack(Creature owner)
    {
        var enemies = owner.CombatState?.HittableEnemies;
        if (enemies == null) return false;
        return enemies.Any(IntendsAttack);
    }

    public static bool IntendsAttack(Creature enemy) =>
        enemy.Monster != null
        && !enemy.IsStunned
        && enemy.Monster.NextMove.Intents.Any(
            intent => intent.IntentType == IntentType.Attack);

    private static void Purge()
    {
        foreach (var stale in HpLost.Keys
                     .Where(creature => creature.CombatState == null)
                     .ToList())
        {
            HpLost.Remove(stale);
        }
    }
}
