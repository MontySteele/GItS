using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Diagnostics;

/// <summary>
/// 2026-10-06 -- WHAT REACTIONS ARE WORTH, PER SEAT, FOR TELEMETRY ONLY.
///
/// Three per-combat, per-seat tallies that <see cref="PlayTelemetry"/> samples
/// into each fight row (`reactions_by_type`, `amp_bonus_damage`,
/// `debuffs_from_reactions`), so a paired co-op round (two kit characters
/// whose elements react, against a base pair) can be read.
///
/// CREDITED THE WAY <c>ReactionEffects.ResolvedThisCombat</c> IS: to
/// <c>dealer.Player</c>, keyed by the combat instance and cleared when it
/// changes. A reaction with no dealer (or a pet dealer, which has no
/// <c>Player</c>) belongs to no seat, so `reactions_by_type` sums to the
/// seat's `reactions_by_turn` total.
///
/// MEASUREMENT ONLY. Nothing here is read by a card, a relic or a formula;
/// every entry point is a read of numbers the engine already computed, and
/// every entry point swallows its own exception (PlayTelemetry rule 2) so a
/// tally can never throw into the damage path.
/// </summary>
internal static class ReactionTally
{
    private static ICombatState? _combat;
    private static readonly Dictionary<Player, Dictionary<string, int>> ByType = new();
    private static readonly Dictionary<Player, Dictionary<string, decimal>> AmpBonus = new();
    private static readonly Dictionary<Player, Dictionary<string, int>> Debuffs = new();

    private static readonly IReadOnlyDictionary<string, int> NoCounts =
        new Dictionary<string, int>();
    private static readonly IReadOnlyDictionary<string, decimal> NoBonus =
        new Dictionary<string, decimal>();

    /// <summary>A reaction resolved, dealt by <paramref name="dealer"/>.</summary>
    internal static void NoteReaction(ICombatState? combat, Creature? dealer,
                                      Reaction reaction)
    {
        try
        {
            if (reaction == Reaction.None) return;
            if (Seat(combat, dealer) is not { } player) return;
            Add(ByType, player, reaction.ToString(), 1);
        }
        catch (Exception e)
        {
            Warn("NoteReaction", e);
        }
    }

    /// <summary>
    /// An amplified hit landed: <paramref name="dealt"/> is what reached HP
    /// plus Block, AFTER the amplifier <paramref name="mult"/>. The bonus filed
    /// is <c>dealt - dealt / mult</c>: the hit after the multiplier minus the
    /// hit before it, as dealt. A killing hit's `dealt` is capped at the HP
    /// the target had, so its bonus is too. The card's own damage credit is
    /// untouched; this is a second, overlapping reading of the same hit.
    /// </summary>
    internal static void NoteAmplified(ICombatState? combat, Creature? dealer,
                                       Reaction reaction, decimal mult, int dealt)
    {
        try
        {
            if (reaction is not (Reaction.Vaporize or Reaction.Melt)) return;
            if (mult <= 1m || dealt <= 0) return;
            if (Seat(combat, dealer) is not { } player) return;
            AddBonus(player, reaction.ToString(), dealt - dealt / mult);
        }
        catch (Exception e)
        {
            Warn("NoteAmplified", e);
        }
    }

    /// <summary>Stacks of <paramref name="power"/> a reaction put on an enemy
    /// (the target's stack after the apply minus before, so an Artifact that
    /// ate it files nothing).</summary>
    internal static void NoteDebuff(ICombatState? combat, Creature? dealer,
                                    string power, int stacks)
    {
        try
        {
            if (stacks <= 0) return;
            if (Seat(combat, dealer) is not { } player) return;
            Add(Debuffs, player, power, stacks);
        }
        catch (Exception e)
        {
            Warn("NoteDebuff", e);
        }
    }

    /// <summary>The stack of <typeparamref name="T"/> on <paramref name="c"/>,
    /// 0 with none or on any error. A read.</summary>
    internal static int Stacks<T>(Creature? c) where T : PowerModel
    {
        try
        {
            if (c == null) return 0;
            var p = c.Powers.OfType<T>().FirstOrDefault();
            return p == null ? 0 : (int)p.Amount;
        }
        catch (Exception)
        {
            return 0;
        }
    }

    internal static IReadOnlyDictionary<string, int> TypesFor(
        ICombatState? combat, Player? player) => Read(ByType, combat, player);

    internal static IReadOnlyDictionary<string, int> DebuffsFor(
        ICombatState? combat, Player? player) => Read(Debuffs, combat, player);

    internal static IReadOnlyDictionary<string, decimal> AmpBonusFor(
        ICombatState? combat, Player? player)
    {
        if (combat == null || player == null || !ReferenceEquals(combat, _combat))
            return NoBonus;
        return AmpBonus.TryGetValue(player, out var d) ? d : NoBonus;
    }

    private static IReadOnlyDictionary<string, int> Read(
        Dictionary<Player, Dictionary<string, int>> map,
        ICombatState? combat, Player? player)
    {
        if (combat == null || player == null || !ReferenceEquals(combat, _combat))
            return NoCounts;
        return map.TryGetValue(player, out var d) ? d : NoCounts;
    }

    /// <summary>The seat to credit, after rolling the per-combat maps over
    /// when the combat instance changed (so they hold one combat's players at
    /// most, the bomb counters' rule).</summary>
    private static Player? Seat(ICombatState? combat, Creature? dealer)
    {
        if (combat == null) return null;
        if (!ReferenceEquals(combat, _combat))
        {
            _combat = combat;
            ByType.Clear();
            AmpBonus.Clear();
            Debuffs.Clear();
        }
        return dealer?.Player;
    }

    private static void Add(Dictionary<Player, Dictionary<string, int>> map,
                            Player player, string key, int n)
    {
        if (!map.TryGetValue(player, out var d))
        {
            d = new Dictionary<string, int>();
            map[player] = d;
        }
        d[key] = (d.TryGetValue(key, out var v) ? v : 0) + n;
    }

    private static void AddBonus(Player player, string key, decimal n)
    {
        if (!AmpBonus.TryGetValue(player, out var d))
        {
            d = new Dictionary<string, decimal>();
            AmpBonus[player] = d;
        }
        d[key] = (d.TryGetValue(key, out var v) ? v : 0m) + n;
    }

    private static void Warn(string where, Exception e) =>
        Log.Warn($"[{KleeMod.ModId}] reaction tally {where} skipped "
               + $"({e.GetType().Name}: {e.Message})");
}
