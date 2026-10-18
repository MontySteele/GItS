// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// A DEAD ENEMY THAT IS COMING BACK (seat page backlog, 2026-10-18; the base
// control seats, Ironclad and Necrobinder, 2026-09-26).
//
// `BuildBattleState` sends living enemies only, so a Decimillipede segment
// that died and is waiting to Reattach vanished from every page, and its
// return read as a new body. The game keeps such a creature in
// `CombatState.Enemies` (`ReattachPower.ShouldCreatureBeRemovedFromCombat
// AfterDeath` answers false) and plans its moves: on death it is set to
// `DEAD_MOVE` (nothing), whose follow-up is `REATTACH_MOVE` (heal by the
// Reattach amount, if any other segment still lives; decompiled
// `DecimillipedeSegment`, `ReattachPower`).
//
// So this lists every dead enemy still in the combat with a planned move:
// its name, its combat id, its max HP, the move it will make next and, where
// it holds a Reattach, the HP it comes back with. A separate key, so the
// living list, its entity ids and every target handle are unchanged.

using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;

namespace STS2_MCP;

public static class GitsRevivingEnemies
{
    /// <summary>The wire key, inside `battle`.</summary>
    public const string Key = "reviving";

    /// <summary>The dead enemies still planning a move; empty where there
    /// are none. Each read is guarded.</summary>
    public static List<Dictionary<string, object?>> Build(
        IEnumerable<Creature> enemies)
    {
        var out_ = new List<Dictionary<string, object?>>();
        foreach (var creature in enemies)
        {
            try
            {
                if (creature.IsAlive) continue;
                if (creature.Monster?.NextMove is not MoveState move) continue;
                var row = new Dictionary<string, object?>
                {
                    ["combat_id"] = creature.CombatId,
                    ["name"] = creature.Monster.Title?.GetFormattedText(),
                    ["max_hp"] = creature.MaxHp,
                    ["move_id"] = move.Id,
                };
                var reattach = creature.Powers.FirstOrDefault(
                    p => p.GetType().Name == "ReattachPower");
                if (reattach != null) row["revive_hp"] = reattach.Amount;
                out_.Add(row);
            }
            catch (Exception)
            {
                // A creature this cannot read is left off, as before.
            }
        }
        return out_;
    }
}
