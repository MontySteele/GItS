using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Tests.Harness;

/// <summary>
/// Overhaul Bomb piles, for the slice-one rule pins.
///
/// The same factory <see cref="Bombs"/> is for the shipped Bomb, and for the
/// same reason: the real placer is <c>ProtoBombPower.Place</c>, which routes
/// through <c>PowerCmd.Apply</c> and needs a live <c>CombatState</c> -- outside
/// the headless boundary (README). So a pile is allocated the way
/// <see cref="Seat.WithPower{T}"/> allocates any power, and the fields the rule
/// code reads are seeded: <c>_owner</c>, <c>_applier</c>, <c>_amount</c> and
/// <c>_charges</c>.
///
/// What is bypassed is the APPLY pipeline. What is exercised is everything the
/// rules do to a pile once it exists: growth, the take, the Mine split, the
/// single removal, and the totals the badge shows.
/// </summary>
internal static class ProtoBombs
{
    /// <summary>Stand-in for the registered id (see <see cref="Bombs.Id"/> for
    /// why a test seeds one at all).</summary>
    internal static readonly ModelId Id = new("POWER", "KLEE_PROTO_BOMB_TEST");

    private static readonly Type ChargeType =
        typeof(ProtoBombPower).GetNestedType("ProtoCharge", HeadlessGame.All)
        ?? throw new InvalidOperationException(
            "ProtoBombPower.ProtoCharge is gone -- the power's shape changed "
            + "under this harness.");

    /// <summary>One charge: size, Mine flag, payload.</summary>
    internal readonly record struct Charge(
        int Size, bool IsMine = false, int PayloadMineAll = 0);

    /// <summary>
    /// Put ONE pile on <paramref name="owner"/>, placed by
    /// <paramref name="applier"/>, carrying <paramref name="charges"/>.
    /// Call it twice with two appliers to build the two-Klee board R205 is
    /// about; pass no charges for an emptied pile.
    /// </summary>
    internal static ProtoBombPower Place(
        Creature owner, Creature applier, params Charge[] charges)
    {
        var bomb = (ProtoBombPower)RuntimeHelpers
            .GetUninitializedObject(typeof(ProtoBombPower));

        Seat.Force(bomb, "Id", Id);
        Field(bomb, "_owner", owner);
        Field(bomb, "_applier", applier);
        Field(bomb, "_amount", charges.Length);
        Field(bomb, "_charges", Charges(charges));
        Seat.Set(bomb, "IsMutable", true);

        var powers = (List<PowerModel>)typeof(Creature)
            .GetField("_powers", HeadlessGame.All)!
            .GetValue(owner)!;
        powers.Add(bomb);

        return bomb;
    }

    private static object Charges(IReadOnlyList<Charge> charges)
    {
        var list = (IList)Activator.CreateInstance(
            typeof(List<>).MakeGenericType(ChargeType))!;
        foreach (var charge in charges)
        {
            list.Add(Activator.CreateInstance(
                ChargeType, charge.Size, charge.IsMine, charge.PayloadMineAll));
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
