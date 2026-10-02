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
