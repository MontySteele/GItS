using System.Collections.Generic;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Tests.Harness;

/// <summary>
/// The overhaul's Bake-Kurage, for the slice-one rule pins.
///
/// Same shape and the same reason as <see cref="ProtoBombs"/> one file over:
/// the real installer is <c>KokomiTide.Install</c>, which routes through
/// <c>PowerCmd.Apply</c> and needs a live <c>CombatState</c> -- outside the
/// headless boundary (README). So the power is allocated the way
/// <see cref="Seat.WithPower{T}"/> allocates any power and the fields the rule
/// code reads are seeded: <c>_owner</c>, <c>_applier</c> and <c>_amount</c>.
///
/// What is bypassed is the APPLY pipeline. What is exercised is everything the
/// rules do to a jellyfish once it exists: the Tide going up, the whole of it
/// coming off, and the badge that shows it.
/// </summary>
internal static class ProtoKurage
{
    /// <summary>Stand-in for the registered id (see <see cref="Bombs.Id"/> for
    /// why a test seeds one at all).</summary>
    internal static readonly ModelId Id = new("POWER", "KOKOMI_PROTO_KURAGE_TEST");

    /// <summary>Put a jellyfish on <paramref name="kokomi"/>, holding
    /// <paramref name="tide"/>.</summary>
    internal static ProtoBakeKuragePower Field(Creature kokomi, int tide = 0)
    {
        var kurage = (ProtoBakeKuragePower)RuntimeHelpers
            .GetUninitializedObject(typeof(ProtoBakeKuragePower));

        Seat.Force(kurage, "Id", Id);
        Field(kurage, "_owner", kokomi);
        Field(kurage, "_applier", kokomi);
        Field(kurage, "_amount", 1);
        Seat.Set(kurage, "IsMutable", true);

        var powers = (List<PowerModel>)typeof(Creature)
            .GetField("_powers", HeadlessGame.All)!
            .GetValue(kokomi)!;
        powers.Add(kurage);

        if (tide > 0) kurage.AddTide(tide);
        return kurage;
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

        throw new System.InvalidOperationException(
            $"{target.GetType().Name}.{field} is gone -- the game's shape "
            + "changed under this harness.");
    }
}
