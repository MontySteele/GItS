using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME, ROUND TWO -- the blind act-1 seat's run, pinned
/// (`review/qa/furina-reframe-round-2-2026-09-04/opus-act1.md`).
///
/// `EB-382`, and the whole of this file's first section, is a row whose
/// SUSPECT was wrong and whose OBSERVATION was right. The seat watched banked
/// Encore vanish across three turn boundaries and, seeing a Salon member on
/// stage each time, read the correlation as causation: "a member on stage
/// appears to eat all remaining Encore at turn start". The row filed the
/// turn-start hooks accordingly.
///
/// THE TURN START SPENDS NOTHING, which is what section 1 says twice over --
/// behaviourally, on the row's own board at each of the three amounts it
/// reports, and structurally, over every hook that runs in the two turn-start
/// broadcasts. THE SPEND IS THE SHIPPED ABSORPTION (section 2): Encore eats
/// damage that gets past Block, which is what the buffer is for, and the arm's
/// METER leg retires the Fanfare that used to mark it -- so under the arm the
/// buffer empties with no mark on any surface at all.
///
/// The seat's own numbers reconcile against absorption exactly. Fight 1, turn
/// 2 into turn 3: the intent read `2x4` after the Shatter un-froze it, so 8
/// damage arrived, HP went 57 -> 53 and Encore went 4 -> 0. Four absorbed,
/// four to HP, eight in total. The "control case" the seat read as "no member,
/// so nothing ate it" is the turn its own record calls "Took 0 damage".
///
/// The sim's half is `tier0/tests/test_furina_reframe_round2.py`, the same
/// sections in the same order. The legibility half -- the page saying what
/// spends Encore, which is the gap that made an ordinary buffer read as a
/// confiscation -- is `understudy.blindplay_notes.METER_RULES`.
/// </summary>
public class FurinaReframeRoundTwoTests
{
    // ==================================================================
    // Fixtures. Lifted from FurinaReframeRuleTests, whose reasoning for
    // every reflective step is written out there.
    // ==================================================================

    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool manual = false, bool evoke = false, bool meter = false,
                     bool spotlight = false, bool burst = false,
                     bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = manual;
            FurinaReframe.EvokeEnabled = evoke;
            FurinaReframe.MeterEnabled = meter;
            FurinaReframe.SpotlightEnabled = spotlight;
            FurinaReframe.BurstEnabled = burst;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.EvokeEnabled = _evoke;
            FurinaReframe.MeterEnabled = _meter;
            FurinaReframe.SpotlightEnabled = _spotlight;
            FurinaReframe.BurstEnabled = _burst;
        }
    }

    /// <summary>The seat's board: a Furina with a company on stage and a
    /// KNOWN buffer, because the amount is what the row is about.</summary>
    private static Seat Stage(int encore, params SalonMember[] members)
    {
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        Seat.Force(power, "Amount", members.Length);
        ((System.Collections.IList)seat.Creature.Powers).Add(power);
        Seat.Force(power, "IsMutable", true);
        Seat.Force(power, "Owner", seat.Creature);

        Company()[seat.Creature] = members.ToList();
        FurinaResources.GainEncore(seat.Creature, encore);
        return seat;
    }

    private static IDictionary<Creature, List<SalonMember>> Company() =>
        (IDictionary<Creature, List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", HeadlessGame.All)!
            .GetValue(null)!;

    private static SalonMemberPower PowerOf(Seat seat) =>
        seat.Creature.Powers.OfType<SalonMemberPower>().First();

    // ==================================================================
    // 1. `EB-382` -- the turn start spends nothing
    // ==================================================================

    [Theory]
    [InlineData(4)]
    [InlineData(3)]
    [InlineData(1)]
    public void A_staged_turn_start_spends_no_encore_under_the_arm(int banked)
    {
        // The row's own scenario, at each of the three amounts it reports.
        // REAL: the suppressed branch returns before anything a combat is
        // needed for.
        using var _ = new Arm(manual: true);
        var seat = Stage(banked, SalonMember.Chevalmarin);

        PowerOf(seat).AfterPlayerTurnStart(default, seat.Player)
            .GetAwaiter().GetResult();

        Assert.Equal(banked, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void The_empty_stage_is_not_what_carried_the_control_turn()
    {
        // The seat read its control case as "no member, so nothing ate it".
        // An empty stage and a staged one carry the same buffer across the
        // same boundary, so the member was never the variable.
        using var _ = new Arm(manual: true);
        var staged = Stage(1, SalonMember.Chevalmarin);
        var empty = Stage(1);

        PowerOf(staged).AfterPlayerTurnStart(default, staged.Player)
            .GetAwaiter().GetResult();
        PowerOf(empty).AfterPlayerTurnStart(default, empty.Player)
            .GetAwaiter().GetResult();

        Assert.Equal(1, FurinaResources.Encore(staged.Creature));
        Assert.Equal(1, FurinaResources.Encore(empty.Creature));
    }

    [Theory]
    [InlineData("SalonMemberPower", "AfterPlayerTurnStart")]
    [InlineData("FurinaResourceHooks", "BeforeSideTurnStart")]
    [InlineData("FurinaResourceHooks", "AfterPlayerTurnStart")]
    public void No_turn_start_hook_takes_encore_itself(string type, string method)
    {
        // STRUCTURAL, and it is the half that covers the hooks a headless
        // harness cannot run: the two broadcasts a player turn opens with hold
        // the decay, the block flush, the Spotlight reset, the deferred draws
        // and the kit grant, and NONE of them reduces the buffer. The Salon
        // hook's own delegation to `PerformMember` is what pays the shipped
        // upkeep, and `SalonVerbTests` pins that it stays there.
        var calls = Il.Calls(Il.Method(type, method));

        Assert.DoesNotContain("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("FurinaResources.AbsorbDamage", calls);
        Assert.DoesNotContain("FurinaResources.SpendEncoreOrHp", calls);
    }

    // ==================================================================
    // 2. `EB-382` -- where it actually goes
    // ==================================================================

    [Fact]
    public void Absorption_is_the_spend_the_seat_saw()
    {
        // Fight 1's arithmetic, reproduced: 8 damage past Block against 4
        // banked Encore leaves 4 to reach HP and empties the buffer.
        using var _ = new Arm(manual: true, meter: true);
        var seat = Stage(4, SalonMember.Chevalmarin);

        var reachedHp = FurinaResources.AbsorbDamage(seat.Creature, 8m);

        Assert.Equal(4m, reachedHp);
        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void The_arm_leaves_that_spend_no_receipt()
    {
        // WHY IT READ AS A DISAPPEARANCE. The shipped engine printed one
        // Fanfare per point absorbed, so an emptying buffer had a mark on the
        // meter beside it. The reframe's §4.1 retires that leg, and nothing
        // replaced the mark -- which is the whole of the finding, and why the
        // repair is a sentence on the page rather than a change to the rule.
        using var _ = new Arm(manual: true, meter: true);
        var seat = Stage(4, SalonMember.Chevalmarin);

        FurinaResources.AbsorbDamage(seat.Creature, 4m);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void The_shipped_engine_still_prints_that_receipt()
    {
        // The flag-off half: absorption is a Fanfare source in a release
        // build, which is what made the same spend visible before the arm.
        using var _ = new Arm(master: false);
        var seat = Stage(4, SalonMember.Chevalmarin);

        FurinaResources.AbsorbDamage(seat.Creature, 4m);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.True(FurinaResources.Fanfare(seat.Creature) > 0);
    }
}
