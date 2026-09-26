#nullable enable

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the fixes from the granted-guest seat round
/// (2026-09-25 night, 0.2.3809+proto), the mod's pins. The sim's are
/// <c>tier0/tests/test_furina_guest_granted_fixes.py</c>, and the scripted
/// boards below are that file's: each forecast number here is the number the
/// sim's ACTUAL end of turn (or enemy turn) produces on the same board.
///
///   1. A Bow on a killing hit lands before the rest of that hit reaches
///      Furina: Usher's Bow Block catches the overflow.
///   2. The forecast: what the acts deal, the attacks' split hit by hit, and
///      one Block number.
///   3. The log: an arrival names the seat it took; a one-body act files its
///      hit as dealt.
///   5. Lynette's act always lands.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaGuestGrantedFixTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static StagePerformer P(string member) => FurinaStage.Parse(member);

    /// <summary>A stage of these seats, front first, with an empty log.
    /// Guests arrive holding their bar; the trio are summoned and raised.
    /// </summary>
    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (string Member, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (member, fanfare) in seats)
        {
            var who = P(member);
            if (FurinaStage.IsGuest(who))
            {
                stage.GuestArrives(who, fanfare);
            }
            else
            {
                stage.Summon(who);
                stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
            }
        }
        stage.ClearBeats();
        return (seat, stage);
    }

    private static readonly StageForecastEnemy[] OneEnemy =
        { new("Shrinker Beetle", false) };

    private static readonly StageForecastEnemy[] TwoEnemies =
        { new("Inklet", false), new("Inklet", false) };

    // ---- 1. the Bow lands inside the hit ---------------------------------

    [Fact]
    public void Usher_at_3_under_a_single_10_leaves_and_she_takes_4()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3));

        var hit = stage.Absorb(10);

        // 10 - 3 (his bar) - 3 (his Bow's Block, before the rest reaches her).
        Assert.Equal(3, hit.Absorbed);
        Assert.Equal(3, hit.Caught);
        Assert.Equal(10 - 3 - 3, hit.ReachedFurina);
        var owed = Assert.Single(stage.TakePendingHitBows());
        Assert.Equal(3, owed.Caught);
    }

    [Fact]
    public void A_bow_that_gives_no_block_changes_nothing_inside_the_hit()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("crabaletta", 3));

        var hit = stage.Absorb(10);

        Assert.Equal(0, hit.Caught);
        Assert.Equal(7, hit.ReachedFurina);
    }

    [Fact]
    public void A_pneuma_turn_bow_catches_its_doubled_block()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3));
        stage.ActBlockMultiplier = 2;

        var hit = stage.Absorb(10);

        Assert.Equal(6, hit.Caught);
        Assert.Equal(1, hit.ReachedFurina);
    }

    [Fact]
    public void A_hit_on_another_player_is_not_caught_by_her_bow()
    {
        // Guest of Honor: the ally's hit meets Furina's lead, but Usher's
        // Bow Block is hers and lands on her.
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3));

        var hit = stage.Absorb(10, bowCatches: false);

        Assert.Equal(0, hit.Caught);
        Assert.Equal(7, hit.ReachedFurina);
        Assert.Contains("bowCatches: false", RepoFile(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype", "CoopSet.cs")));
    }

    private static string RepoFile(string relativePath,
                                   [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relativePath);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relativePath);
    }

    [Fact]
    public void The_bow_gains_only_the_block_the_hit_left()
    {
        // `Act`'s Usher branch subtracts the exit's caught Block, and the
        // beat files what the Bow gave: what she gained plus what it caught.
        var act = Il.Calls(Il.Method("FurinaStage", "Act"));
        Assert.Contains("StageExit.get_Caught", act);
        Assert.Contains("CreatureCmd.GainBlock", act);
    }

    [Fact]
    public void The_multi_hit_split_walks_the_hits_and_the_next_performer()
    {
        // The sim's board: Usher 3, Crabaletta 4, two hits of 5, no Block.
        // Hit one: Usher takes 3 and leaves; his Bow Block takes the other 2
        // and keeps 1. Hit two: that 1, then Crabaletta takes 4 and leaves.
        // Nothing reaches Furina (the sim's actual enemy turn: HP unchanged).
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3), ("crabaletta", 4));
        // The sweep would give 3 Block first; take the hits as they would
        // arrive past it (8 = 5 + 3) so the enemy turn is the sim's board.
        var forecast = FurinaStage.Forecast(seat.Creature, new[] { 8, 5 },
                                            OneEnemy);

        Assert.Equal(0, forecast.ReachesFurina);
        Assert.Equal(7, forecast.FrontTakes);
        Assert.Equal(
            new[] { (StagePerformer.Usher, 3, true),
                    (StagePerformer.Crabaletta, 4, true) },
            forecast.Takers.Select(t => (t.Who, t.Takes, t.Leaves)).ToArray());
    }

    // ---- 2. the forecast: what the acts deal -----------------------------

    [Fact]
    public void The_forecast_prints_each_acts_damage_and_the_total_on_one_enemy()
    {
        // Lane 2's Beetle: Crabaletta 5, Crabaletta 5, Chevalmarin 2 -- the
        // Beetle ended the turn on 1 HP from 13, and the seat had to add them.
        using var _ = new Arm();
        var (seat, _) = Stage(("crabaletta", 1), ("crabaletta", 5),
                              ("chevalmarin", 2));

        var forecast = FurinaStage.Forecast(seat.Creature, null, OneEnemy);

        Assert.Equal(
            new[] { (StagePerformer.Crabaletta, 5, "", StageForecastAct.Random),
                    (StagePerformer.Crabaletta, 5, "", StageForecastAct.Random),
                    (StagePerformer.Chevalmarin, 2, "", StageForecastAct.All) },
            forecast.Acts.Select(a => (a.Who, a.Amount, a.Element, a.Target))
                .ToArray());
        Assert.Equal(12, forecast.ActTotal);
        Assert.Equal("Shrinker Beetle", forecast.ActTotalTarget);
    }

    [Fact]
    public void A_random_act_on_two_enemies_has_no_total()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("crabaletta", 1), ("chevalmarin", 1));

        var forecast = FurinaStage.Forecast(seat.Creature, null, TwoEnemies);

        Assert.Equal(2, forecast.Acts.Count);
        Assert.Equal(-1, forecast.ActTotal);
    }

    [Fact]
    public void Acts_all_on_all_enemies_total_to_all()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("chevalmarin", 1), ("neuvillette", 6));

        var forecast = FurinaStage.Forecast(seat.Creature, null, TwoEnemies);

        Assert.Equal(
            new[] { (StagePerformer.Chevalmarin, 2, ""),
                    (StagePerformer.Neuvillette, 8, "Hydro") },
            forecast.Acts.Select(a => (a.Who, a.Amount, a.Element)).ToArray());
        Assert.Equal(10, forecast.ActTotal);
        Assert.Equal(StageForecastAct.All, forecast.ActTotalTarget);
    }

    [Fact]
    public void A_guest_that_pays_its_last_fanfare_bows_and_its_bow_is_a_line()
    {
        // Neuvillette at 3 pays 3, leaves, and Bows: 8 to ALL twice.
        using var _ = new Arm();
        var (seat, _) = Stage(("neuvillette", 3), ("usher", 3));

        var forecast = FurinaStage.Forecast(seat.Creature, null, OneEnemy);

        Assert.Equal(new[] { false, true },
                     forecast.Acts.Select(a => a.Bow).ToArray());
        Assert.Equal(16, forecast.ActTotal);
    }

    [Fact]
    public void An_act_that_cannot_pay_has_no_damage_line()
    {
        // Clorinde alone has no one to tax: her act does nothing.
        using var _ = new Arm();
        var (seat, _) = Stage(("clorinde", 4));

        var forecast = FurinaStage.Forecast(seat.Creature, null, OneEnemy);

        Assert.Empty(forecast.Acts);
        Assert.Equal(-1, forecast.ActTotal);
    }

    [Fact]
    public void Navia_wriothesley_and_ousia_read_what_the_act_reads()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("wriothesley", 10), ("navia", 5));
        stage.Absorb(7);                              // he lost 7 to a hit
        stage.ActDamageMultiplier = 2;                // Ousia

        var forecast = FurinaStage.Forecast(seat.Creature, null, OneEnemy);

        Assert.Equal(
            new[] { (StagePerformer.Wriothesley, 2 * 7 * 2, "Cryo"),
                    (StagePerformer.Navia, 5 * 2, "Geo") },
            forecast.Acts.Select(a => (a.Who, a.Amount, a.Element)).ToArray());
    }

    [Fact]
    public void The_acts_ride_the_wire_and_the_strip()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 3), ("crabaletta", 4));

        var wire = (Dictionary<string, object?>)FurinaStageLedger.Snapshot(
            seat.Player)["forecast"]!;
        var acts = (List<object?>)wire["acts"]!;
        var crab = (Dictionary<string, object?>)Assert.Single(acts)!;
        Assert.Equal("crabaletta", crab["member"]);
        Assert.Equal(5, crab["amount"]);
        Assert.Equal("random", crab["target"]);
        Assert.True(wire.ContainsKey("takers"));
        Assert.True(wire.ContainsKey("act_total"));

        var lines = Vfx.FurinaStageStrip.Label(seat.Creature).Split('\n');
        Assert.Contains("Acts: Crab 5 to a random enemy", lines);
    }

    // ---- 2. one Block number ---------------------------------------------

    [Fact]
    public void The_header_and_the_attack_line_read_one_block_number()
    {
        // Lane 1, fight 1 turn 2: Usher at 1 in front, Clorinde behind. The
        // sweep: Usher's act gives 3, then Clorinde's tax empties Usher, and
        // his Bow gives 3 more. "after the acts: Block 3" counted Ushers
        // standing; the forecast ran the sweep and said 6.
        using var _ = new Arm();
        var (seat, _) = Stage(("usher", 1), ("clorinde", 4));

        var forecast = FurinaStage.Forecast(seat.Creature, null);
        var snapshot = FurinaStageLedger.Snapshot(seat.Player);
        var wire = (Dictionary<string, object?>)snapshot["forecast"]!;

        Assert.Equal(6, forecast.BlockAfterActs);
        Assert.Equal(6, FurinaStage.ForecastActBlock(seat.Creature));
        Assert.Equal(6, snapshot["act_block"]);
        Assert.Equal(6, wire["block_after_acts"]);
    }

    // ---- 3. the log -------------------------------------------------------

    [Fact]
    public void An_arrival_names_the_seat_it_took_not_the_one_it_is_pushed_to()
    {
        // Lane 2: Navia joined at the back, Wriothesley then joined at the
        // front, and the log said she "stands in the middle seat".
        // #680 keyed WHICH performer and still read the seat off the board
        // as drawn. Here Crabaletta joins at the front, Navia behind her, and
        // Wriothesley then joins at the front and pushes both back one.
        using var _ = new Arm();
        var (seat, stage) = Stage();
        stage.Summon(StagePerformer.Crabaletta);
        stage.GuestArrives(StagePerformer.Navia, 4);
        stage.GuestArrives(StagePerformer.Wriothesley, 8, atFront: true);

        StageBeat Arrival(StagePerformer who) => stage.Beats.First(
            b => b.Event == "arrive" && b.Who == who);
        // The seat each TOOK: the front of one, the back of two.
        Assert.Equal((0, 1), (Arrival(StagePerformer.Crabaletta).Seat,
                              Arrival(StagePerformer.Crabaletta).Standing));
        Assert.Equal((1, 2), (Arrival(StagePerformer.Navia).Seat,
                              Arrival(StagePerformer.Navia).Standing));
        // Where Crabaletta stands now: the middle of three.
        Assert.Equal(1, stage.IndexOf(
            stage.SeatOf(StagePerformer.Crabaletta)!));

        var log = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["log"]!;
        var row = (Dictionary<string, object?>)log.First(r =>
            ((Dictionary<string, object?>)r!)["member"] as string
               == "crabaletta"
            && ((Dictionary<string, object?>)r!)["event"] as string
               == "arrive")!;
        Assert.Equal((0, 1), (row["seat"], row["standing"]));
    }

    [Fact]
    public void A_one_body_act_files_its_hit_as_dealt()
    {
        // The act beat's number was what the HP lost: "Wriothesley acted: 1
        // Cryo to Wriggler" was a 14 into a body with 1 HP left. The acts
        // need a live combat, so the wiring is what is pinned: each one-body
        // hit takes a shot before and files it on the beat.
        var guest = Il.Calls(Il.Method("FurinaStage", "HitRandom"));
        Assert.Contains("HitShot.Before", guest);
        Assert.Contains("HitShot.Dealt", guest);
        var trio = Il.Calls(Il.Method("FurinaStage", "Act"));
        Assert.Contains("HitShot.Before", trio);
        var beat = new StageBeat("act", StagePerformer.Wriothesley, 0, 0, 1,
                                 "", Dealt: 14, TargetHp: 1, Blocked: 0);
        Assert.Equal((14, 1, 0), (beat.Dealt, beat.TargetHp, beat.Blocked));
    }

    [Fact]
    public void The_new_beat_fields_ride_the_wire()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        stage.Absorb(10);

        var log = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["log"]!;
        foreach (var raw in log)
        {
            var row = (Dictionary<string, object?>)raw!;
            foreach (var key in new[] { "dealt", "target_hp", "blocked",
                                        "caught", "standing" })
            {
                Assert.True(row.ContainsKey(key), key);
            }
        }
    }

    // ---- 5. Lynette's act -------------------------------------------------

    [Fact]
    public void Lynettes_tip_and_badge_are_the_ruled_sentence()
    {
        const string ruled = "End of your turn: deal 3 [gold]Anemo[/gold] "
                             + "damage to a random enemy, one with an aura "
                             + "if any.";
        Assert.Equal(3, FurinaStageLaw.ActLynetteDamage);
        var power = RuntimeHelpers.GetUninitializedObject(
            typeof(LynetteBadgePower));
        var badge = (List<(string, string)>)typeof(LynetteBadgePower)
            .GetProperty("Localization")!.GetValue(power)!;
        Assert.Equal(ruled, badge.Single(r => r.Item1 == "description").Item2);
        var tips = Il.Strings(typeof(ArmKeywordTips).GetMethod(
            "ForLynette", HeadlessGame.All)!);
        Assert.Contains(" [gold]Anemo[/gold] damage to a random enemy, one "
                        + "with an aura if any.", tips);
    }

    [Fact]
    public void Lynettes_act_deals_anemo_damage_through_the_reacting_door()
    {
        var act = Il.Calls(Il.Method("FurinaStage", "GuestAct"));
        Assert.Contains("ElementalHit.Deal", act);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", act);
    }

    [Fact]
    public void Lynettes_forecast_line_prefers_an_aura()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("lynette", 8));

        var bare = FurinaStage.Forecast(seat.Creature, null, OneEnemy);
        var aura = FurinaStage.Forecast(
            seat.Creature, null,
            new[] { new StageForecastEnemy("Toadpole", true),
                    new StageForecastEnemy("Toadpole", false) });

        Assert.Equal((3, "Anemo", StageForecastAct.Random),
                     (bare.Acts[0].Amount, bare.Acts[0].Element,
                      bare.Acts[0].Target));
        Assert.Equal(StageForecastAct.RandomAura, aura.Acts[0].Target);
    }
}
