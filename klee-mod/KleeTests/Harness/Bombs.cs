using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Tests.Harness;

/// <summary>
/// Bomb piles, for the R205 per-placer instancing pins.
///
/// WHY A FACTORY. The real placer is <c>BombPower.Place</c>, which routes
/// through <c>PowerCmd.Apply</c> and needs a live <c>CombatState</c> -- outside
/// the headless boundary (README). So a pile is allocated the way
/// <see cref="Seat.WithPower{T}"/> allocates any power, and the four fields the
/// instancing code actually reads are seeded: <c>_owner</c>, <c>_applier</c>,
/// <c>_amount</c> and <c>_damages</c>.
///
/// What is bypassed is the APPLY pipeline. What is exercised is everything
/// downstream of it: the suppression arbiter, <c>ModifyAll</c>, the totals, and
/// the base game's own <c>PowerCmd.FindExistingInstanceForStacking</c> -- which
/// is the mechanism <c>InstancedPerApplier</c> actually acts through, and is a
/// pure function, so it can be called directly.
///
/// THE ID IS SEEDED EXPLICITLY. In game BaseLib assigns it at registration, off
/// <c>Id.Entry</c>; that registration is model-table state a test has no
/// business mutating. The stacking search compares power ids to each other, so
/// what matters is that every pile in a test carries the SAME id -- which is
/// exactly what the game guarantees for two instances of one power.
/// </summary>
internal static class Bombs
{
    /// <summary>Stand-in for the registered id (see class doc).</summary>
    internal static readonly ModelId Id = new("POWER", "KLEE_BOMB_TEST");

    private static readonly Type ChargeType =
        typeof(BombPower).GetNestedType("BombCharge", HeadlessGame.All)
        ?? throw new InvalidOperationException(
            "BombPower.BombCharge is gone -- the power's shape changed under "
            + "this harness.");

    /// <summary>
    /// Put ONE pile on <paramref name="owner"/>, placed by
    /// <paramref name="applier"/>, carrying <paramref name="damages"/>.
    ///
    /// Call it twice with two different appliers to build the two-Klee board
    /// that shape (a) is about. Pass no damages for an emptied pile.
    /// </summary>
    internal static BombPower Place(
        Creature owner, Creature applier, int roundPlaced, params int[] damages)
    {
        var bomb = (BombPower)RuntimeHelpers.GetUninitializedObject(typeof(BombPower));

        Seat.Force(bomb, "Id", Id);
        Field(bomb, "_owner", owner);
        Field(bomb, "_applier", applier);
        Field(bomb, "_amount", damages.Length);
        Field(bomb, "_damages", Charges(roundPlaced, damages));
        // The flag the game's ToMutable would have set; Owner's getter reads it.
        Seat.Set(bomb, "IsMutable", true);

        var powers = (List<PowerModel>)typeof(Creature)
            .GetField("_powers", HeadlessGame.All)!
            .GetValue(owner)!;
        powers.Add(bomb);

        return bomb;
    }

    private static object Charges(int roundPlaced, IReadOnlyList<int> damages)
    {
        var list = (IList)Activator.CreateInstance(
            typeof(List<>).MakeGenericType(ChargeType))!;
        foreach (var damage in damages)
        {
            list.Add(Activator.CreateInstance(ChargeType, damage, roundPlaced));
        }
        return list;
    }

    private static void Field(object target, string field, object value)
    {
        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField(field, HeadlessGame.All);
            if (f == null) continue;
            f.SetValue(target, value);
            return;
        }

        throw new InvalidOperationException(
            $"{target.GetType().Name}.{field} is gone -- the game's shape "
            + "changed under this harness.");
    }
}
