using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// tier0 predicate <c>hp_lost_since_last_turn</c>: has this player lost any
/// HP since the END of their previous turn? Shinobu's Grass Ring of
/// Sanctification reads it (2026-09-23, [USER]: "agreed on a)").
///
/// WHY NOT <see cref="CurtainCallHooks.HpLostThisTurn"/>. That window opens
/// at the top of the player's turn, so the enemy turn -- where nearly all HP
/// is lost -- was already wiped by the time a card could ask, and the clause
/// never paid on the player's own turn. This window opens where the player's
/// turn ENDS (<c>AfterSideTurnEnd(Player)</c>, after every end-of-turn
/// effect), so the enemy turn counts; on the first turn of combat it counts
/// from the start of combat (<c>BeforeCombatStart</c> clears it).
///
/// ANY PLAYER, NOT ONLY FURINA. Fed from <see cref="KleeElementalHooks"/>,
/// the global combat listener, rather than from Furina's HP funnel.
///
/// SIM MIRROR: <c>state.hp_lost_since_last_turn</c>, incremented in
/// <c>resources.note_player_hp_loss</c> and zeroed at the end of
/// <c>combat._player_turn</c>.
/// </summary>
public static class HpLossWindow
{
    private static readonly Dictionary<Creature, int> Lost = new();

    /// <summary>Record true HP loss on a player creature.</summary>
    public static void Note(Creature creature, int amount)
    {
        if (amount <= 0 || creature.Player == null) return;
        Lost[creature] = (Lost.TryGetValue(creature, out var v) ? v : 0) + amount;
    }

    /// <summary>The player's turn has ended: the next window opens now.</summary>
    public static void ResetAtTurnEnd(Creature creature)
    {
        Lost.Remove(creature);
        Purge();
    }

    /// <summary>A new combat: every window starts empty.</summary>
    public static void ClearAll() => Lost.Clear();

    /// <summary>How much HP this creature has lost in the current window.</summary>
    public static int LostAmount(Creature creature) =>
        Lost.TryGetValue(creature, out var v) ? v : 0;

    /// <summary>tier0 predicate <c>hp_lost_since_last_turn</c>.</summary>
    public static bool LostSinceLastTurn(Creature creature) =>
        LostAmount(creature) > 0;

    /// <summary>Drop keys whose combat is gone, so the map cannot grow across
    /// a run (<c>CurtainCallHooks.Purge</c>'s shape).</summary>
    private static void Purge()
    {
        foreach (var stale in Lost.Keys
                     .Where(creature => creature.CombatState == null)
                     .ToList())
        {
            Lost.Remove(stale);
        }
    }
}
