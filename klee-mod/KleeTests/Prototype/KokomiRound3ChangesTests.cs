using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI ROUND-3 CHANGES (2026-10-12), from the Fable round-2 review and
/// <c>review/records/kokomi-round-2-2026-10-12.md</c>: the Plan face folds a
/// Vulnerable only when it will still be up at the morning, Coordinated
/// Tide's hit is named on the Plan results line, Tide Wall reads the largest
/// intent, Treatise's face says writing does not count, Kelp Wall's now-line
/// blocks, and Watchful Shoal is the jellyfish's Accuracy. Sim twin:
/// <c>tier0/tests/test_kokomi_round3_changes_2026_10_12.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRound3ChangesTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static int Var<T>(string name, bool upgraded = false)
        where T : CardModel, new() =>
        (upgraded ? Upgraded<T>() : new T()).DynamicVars[name].IntValue;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- 1. the Plan face and an expiring Vulnerable -----------------------

    [Fact]
    public void A_vulnerable_of_one_is_not_on_the_plan_face()
    {
        // Seats read Oath 13 and saw 9: Vulnerable 1 ticks off at the end of
        // the enemy's turn, before the morning carries the Plan out.
        var one = Seat.Kokomi(60).WithPower<VulnerablePower>(1).Creature;
        Assert.False(KokomiPlan.VulnerableAtMorning(one));
        Assert.Equal(12, KokomiPlan.PlannedDamage(one, 12));
        var two = Seat.Kokomi(60).WithPower<VulnerablePower>(2).Creature;
        Assert.True(KokomiPlan.VulnerableAtMorning(two));
        Assert.Equal(18, KokomiPlan.PlannedDamage(two, 12));
        var none = Seat.Kokomi(60).Creature;
        Assert.Equal(12, KokomiPlan.PlannedDamage(none, 12));
    }

    [Fact]
    public void The_queue_rows_note_and_the_carry_out_read_their_own_vulnerable()
    {
        // "(after Vulnerable)" follows the face's rule.
        Assert.Contains(Seq("KokomiPlan", "RaisedByVulnerable"),
                        c => c.Contains("KokomiPlan.VulnerableAtMorning"));
        // The carry-out is unchanged: `ElementalHit.Deal` runs TargetMods on
        // whatever the body wears then, never the face's rule.
        Assert.DoesNotContain(Il.Calls(Il.Method("ElementalHit", "Deal")),
                              c => c.Contains("VulnerableAtMorning"));
        Assert.Contains(Il.Calls(Il.Method("ElementalHit", "Deal")),
                        c => c.Contains("SimDamagePipeline.TargetMods"));
    }

    // ---- 2. Coordinated Tide on the results line -----------------------------

    [Fact]
    public void Coordinated_tide_hits_inside_the_carry_out_and_is_a_rider()
    {
        // The pool overhaul (2026-10-13): Coordinated Tide no longer hits on
        // a carry-out; it adds a Sting when a Companion's own hit reacts
        // (`KokomiRefounding.OnReaction`). Its carry-out hit and rider are
        // gone.
        var entry = string.Join(" ", Seq("KokomiPlan", "ResolveEntry"));
        Assert.DoesNotContain("KokomiRefounding.CoordinatedTide", entry);
        Assert.DoesNotContain(Il.Strings(Il.Method("KokomiPlan", "ResolveEntry")),
                              s => s == "Coordinated Tide");
        Assert.Null(typeof(KokomiRefounding).GetMethod("CoordinatedTide"));
        Assert.DoesNotContain(Seq("KokomiRefounding", "OnCarriedOut"),
                              c => c.Contains("ElementalHit.Deal"));
    }

    // ---- 3. Tide Wall reads the largest intent ------------------------------

    [Fact]
    public void Tide_wall_reads_the_most_any_enemy_intends()
    {
        Assert.Equal(0, KokomiOverhaulKit.MostIntendedDamage(null));
        var most = Seq("KokomiOverhaulKit", "MostIntendedDamage");
        Assert.Contains(most, c => c.Contains("KokomiOverhaulKit.IntendedDamage"));
        Assert.Contains(most, c => c.Contains("HittableEnemies"));
        Assert.DoesNotContain(most, c => c.Contains("FrontEnemy"));
        Assert.EndsWith("plus the biggest attack an enemy intends on the "
                        + "turn it lands.",
                        Face(new ProtoKkTideWall()));
    }

    // ---- 5. Kelp Wall's now-line --------------------------------------------

    [Fact]
    public void Kelp_wall_now_line_blocks_then_draws()
    {
        Assert.StartsWith(
            "Gain {Block:diff()} [gold]Block[/gold]. Draw 1 card.",
            Face(new ProtoKkKelpWall()));
        // The numbers pass (kokomi-review-r5-2026-10-14): 7 [9].
        Assert.Equal((7, 9), (Var<ProtoKkKelpWall>("Block"),
                              Var<ProtoKkKelpWall>("Block", true)));
        // The pool overhaul (2026-10-13): the Plan prints no number (was the
        // level pass's flat 12 [15]).
        Assert.False(new ProtoKkKelpWall().DynamicVars.ContainsKey("PlanBlock"));
    }

    // ---- 6. Watchful Shoal, the jellyfish's Accuracy -------------------------

    [Fact]
    public void Watchful_shoal_numbers_and_face()
    {
        // Kokomi review r6 (2026-10-14, item 3): 4 [6].
        Assert.Equal((4, 6), (Var<ProtoKkWatchfulShoal>("PowerAmount"),
                              Var<ProtoKkWatchfulShoal>("PowerAmount", true)));
        Assert.Equal(
            "Your [gold]Stings[/gold] deal {PowerAmount:diff()} additional "
          + "damage.",
            Face(new ProtoKkWatchfulShoal()));
        var power = new WatchfulShoalPower().Localization!
            .Single(r => r.Item1 == "description").Item2;
        // Its Ward half left with the Ward's Block (2026-10-18).
        Assert.DoesNotContain("Ward", power);
        // Writing an Ethereal card pays nothing now.
        Assert.DoesNotContain(Seq("KokomiRefounding", "OnWritten"),
                              c => c.Contains("WatchfulShoalPower"));
    }

    [Fact]
    public void A_stings_now_line_takes_the_bonus_and_a_ward_nothing()
    {
        var seat = Seat.Kokomi().WithPower<WatchfulShoalPower>(3);
        var power = seat.Creature.Powers.OfType<WatchfulShoalPower>().Single();
        var enemy = Seat.Klee().Creature;
        Assert.Equal(3m, power.ModifyDamageAdditive(
            enemy, 7m, ValueProp.Move, seat.Creature, new ProtoKkSting(), null));
        // Not another attack, not someone else's hit, not an unpowered one.
        Assert.Equal(0m, power.ModifyDamageAdditive(
            enemy, 7m, ValueProp.Move, seat.Creature, new ProtoKkBrineSting(),
            null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            enemy, 7m, ValueProp.Move, enemy, new ProtoKkSting(), null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            enemy, 7m, ValueProp.Unpowered, seat.Creature, new ProtoKkSting(),
            null));
        // Ward and Casket (2026-10-18): the power no longer adds Block.
        Assert.Equal(0m, power.ModifyBlockAdditive(
            seat.Creature, 7m, ValueProp.Move, new ProtoKkWard(), null));
        Assert.Null(typeof(WatchfulShoalPower).GetMethod("ModifyBlockAdditive",
            System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.Instance
            | System.Reflection.BindingFlags.DeclaredOnly));
    }

    [Fact]
    public void A_written_sting_folds_the_bonus_where_her_strength_folds()
    {
        var seat = Seat.Kokomi().WithPower<WatchfulShoalPower>(3);
        Assert.Equal(3, WatchfulShoalPower.StingBonus(seat.Creature,
                                                      new ProtoKkSting()));
        Assert.Equal(0, WatchfulShoalPower.StingBonus(seat.Creature,
                                                      new ProtoKkWard()));
        Assert.Equal(8, KokomiPlan.Hers(seat.Creature, new ProtoKkSting(), 5));
        Assert.Equal(5, KokomiPlan.Hers(seat.Creature, new ProtoKkWard(), 5));
        Assert.Equal(5, KokomiPlan.Hers(Seat.Kokomi().Creature,
                                        new ProtoKkSting(), 5));
        Assert.Contains(Seq("KokomiPlan", "Hers"),
                        c => c.Contains("WatchfulShoalPower.StingBonus"));
    }
}
