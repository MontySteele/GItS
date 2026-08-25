using System;
using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Suite (c): the co-op seams, which is why this project exists.
///
/// THE STANDING GAP. tier 0.5 models ONE seat, so no sim run can ever
/// disagree with the mod about a two-seat board -- the repo records this in
/// three places (BombPower.cs, CompanionPowers.cs:46, TurnEndSequencer.cs)
/// and every co-op defect found so far was found by playing. Each test below
/// converts one class of that from play-only to testable.
///
/// EB-130 narrowed the BombPower one: two seats PLACING two piles is pinned in
/// BombInstancingTests; two seats DETONATING on one enemy still needs a live
/// CombatState and stays play-only.
///
/// WHAT IS AND IS NOT COVERED. These test per-seat OWNERSHIP AND ATTRIBUTION:
/// that two seats' resources, relic effects, identity gating and telemetry
/// rows are keyed apart. They do NOT test the multiplayer TRANSPORT -- lockstep
/// RNG agreement, remote-seat selection round trips, or anything that needs a
/// second peer. That half is still play-only; see README.md.
/// </summary>
public class CoopSeamTests
{
    [Fact]
    public void Two_seats_hold_independent_fanfare_meters()
    {
        var a = Seat.Furina().WithCombatState();
        var b = Seat.Furina().WithCombatState();

        FurinaResources.GainFanfare(a.Creature, 12);

        Assert.Equal(12, FurinaResources.Fanfare(a.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(b.Creature));
    }

    [Fact]
    public void A_seat_s_fanfare_ceiling_is_its_own_max_hp_not_the_table_s()
    {
        // Two Furinas at different max HP -- legal in co-op, and the pair the
        // audit's H3 divergence would desynchronise.
        var healthy = Seat.Furina(60).WithCombatState();
        var hurt = Seat.Furina(36).WithCombatState();

        FurinaResources.GainFanfare(healthy.Creature, 500);
        FurinaResources.GainFanfare(hurt.Creature, 500);

        Assert.Equal(30, FurinaResources.Fanfare(healthy.Creature));
        Assert.Equal(18, FurinaResources.Fanfare(hurt.Creature));
    }

    [Fact]
    public void Furina_resource_hooks_do_not_fire_for_a_non_furina_seat()
    {
        // The mixed table: one Furina, one Klee. A generated Furina card that
        // reached the Klee seat must not grant her HP-loss engine.
        var furina = Seat.Furina().WithCombatState();
        var klee = Seat.Klee().WithCombatState();

        FurinaResources.GainFanfare(furina.Creature, 10);
        FurinaResources.GainFanfare(klee.Creature, 10);

        Assert.True(FurinaResources.IsFurina(furina.Creature));
        Assert.False(FurinaResources.IsFurina(klee.Creature));
        Assert.Equal(10, FurinaResources.Fanfare(furina.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(klee.Creature));
    }

    [Fact]
    public void Exhaust_accrual_reads_the_relics_of_the_seat_that_exhausted()
    {
        // Relics are RUN state and per-seat. Kokomi A holds the upgraded
        // starter, Kokomi B does not; the exhaust funnel must pay each seat
        // its own rate. `ExhaustCharge`/`ExhaustBurst` are internal, so they
        // are reached by reflection rather than by widening the mod's surface
        // for a test.
        var withPearl = Seat.Kokomi().WithRelic<PearlOfInsightRelic>();
        var without = Seat.Kokomi();

        Assert.Equal(2, ExhaustCharge(withPearl));
        Assert.Equal(4, ExhaustBurst(withPearl));
        Assert.Equal(1, ExhaustCharge(without));
        Assert.Equal(2, ExhaustBurst(without));
    }

    [Fact]
    public void Both_spotlight_modes_is_a_per_seat_relic_query()
    {
        // R2's upgraded starter. Two Furinas, one holding The Curtain Never
        // Falls: the mode must not leak across the table.
        var upgraded = Seat.Furina().WithRelic<CurtainNeverFalls>();
        var plain = Seat.Furina();

        Assert.True(SpotlightSystem.BothModes(upgraded.Creature));
        Assert.False(SpotlightSystem.BothModes(plain.Creature));
    }

    [Fact]
    public void Salon_tick_scaling_is_read_off_the_acting_seat()
    {
        // Fanfare is the Focus analogue, and Focus is per-creature. A stage
        // on the loaded seat must not scale off the other seat's meter.
        var loaded = Seat.Furina().WithCombatState();
        var empty = Seat.Furina().WithCombatState();
        FurinaResources.GainFanfare(loaded.Creature, 20);

        Assert.Equal(8, SalonMemberPower.TickValue(
            loaded.Creature, SalonMember.Crabaletta, paid: true));
        Assert.Equal(6, SalonMemberPower.TickValue(
            empty.Creature, SalonMember.Crabaletta, paid: true));
    }

    [Fact]
    public void The_salon_company_is_keyed_per_creature()
    {
        // The company is a static Dictionary<Creature, List<SalonMember>>.
        // A dictionary keyed on the wrong thing is exactly how a co-op stage
        // would show one seat the other's members; pin that the key is the
        // creature and that two seats resolve to two entries.
        var field = typeof(SalonMemberPower)
            .GetField("Company", HeadlessGame.All)!;
        var keyType = field.FieldType.GetGenericArguments()[0];
        Assert.Equal(typeof(MegaCrit.Sts2.Core.Entities.Creatures.Creature), keyType);

        var a = Seat.Furina();
        var b = Seat.Furina();
        Assert.Empty(SalonMemberPower.CompanyOf(a.Creature));
        Assert.Empty(SalonMemberPower.CompanyOf(b.Creature));

        var company = (System.Collections.IDictionary)field.GetValue(null)!;
        Assert.True(company.Contains(a.Creature));
        Assert.True(company.Contains(b.Creature));
        Assert.NotSame(company[a.Creature], company[b.Creature]);
    }

    [Fact]
    public void A_telemetry_fight_row_carries_the_seat_count_and_this_seat_s_index()
    {
        // EB-18's join keys. The understudy reader groups co-op rows by
        // (run_instance, fight_index) and separates the seats by seat_index;
        // a renamed or dropped key is a silent cross-session schema break,
        // which is why ToJson is hand-rolled rather than reflected.
        //
        // ToJson itself CANNOT be called headless -- it reaches Godot's
        // ProjectSettings through its intent lookup, which kills the process
        // (README, the headless boundary). So the row is pinned two ways that
        // between them cover the rename: the FIELDS the writer fills, and the
        // KEY LITERALS the serializer emits.
        var type = typeof(global::KleeMod.Diagnostics.PlayTelemetryHooks).Assembly
            .GetTypes().First(t => t.Name == "FightRecord");

        Assert.Equal(typeof(int), type.GetField("Seats")!.FieldType);
        Assert.Equal(typeof(int), type.GetField("SeatIndex")!.FieldType);

        var emitted = Il.Strings(type.GetMethod("ToJson", HeadlessGame.All)!);
        Assert.Contains(",\"seats\":", emitted);
        Assert.Contains(",\"seat_index\":", emitted);
        Assert.Contains(",\"fight_index\":", emitted);
        Assert.Contains("run_instance", emitted);
    }

    private static int ExhaustCharge(Seat seat) => Funnel("ExhaustCharge", seat);

    private static int ExhaustBurst(Seat seat) => Funnel("ExhaustBurst", seat);

    private static int Funnel(string name, Seat seat)
    {
        var method = typeof(KokomiResources).Assembly.GetTypes()
            .SelectMany(t => t.GetMethods(HeadlessGame.All))
            .First(m => m.Name == name && m.GetParameters().Length == 1);
        return (int)method.Invoke(null, new object[] { seat.Creature })!;
    }
}
