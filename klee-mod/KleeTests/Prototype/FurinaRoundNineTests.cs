using System;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA ROUND 9, the rows filed against words the board did not carry: a
/// rule a seat could only find by running the experiment twice, and a half of
/// a card that went missing in silence.
/// </summary>
public class FurinaRoundNineTests
{
    /// <summary>Turn the reframe's MANUAL leg on for one test and put every
    /// flag back after it -- `FurinaReframeRoundSevenTests.Arm` verbatim, and
    /// for its reason: the six flags are process-global statics.</summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = master;
            FurinaReframe.EvokeEnabled = false;
            FurinaReframe.MeterEnabled = false;
            FurinaReframe.SpotlightEnabled = false;
            FurinaReframe.BurstEnabled = false;
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

    // ==================================================================
    // `EB-476` -- is a performance an Attack? Two experiments, two answers
    // ==================================================================
    //
    // THE FIND (Furina r9 (c) 3). "A member performance is an Attack for
    // Vulnerable but not for Frozen. Vulnerable 2 turned Crabaletta's 6 into
    // 9... but a Frozen enemy survived two performances without Shattering."
    // The seat ran the experiment twice and could not name the class the
    // performance belongs to.
    //
    // BOTH OBSERVATIONS ARE ONE RULE, `EB-343`'s. A performance goes out
    // through `ElementalHit.Deal`, which reaches `CreatureCmd.Damage` as
    // `ValueProp.Unpowered` with no dealer and no card source. Every gate that
    // asks `IsPoweredAttack()` refuses it -- the Shatter, an enemy's on-Attack
    // trigger -- and `SimDamagePipeline.TargetMods`, which reads the target's
    // Vulnerable, asks nothing of the kind. The arm's Salon paragraph now says
    // it in one sentence.

    [Fact]
    public async Task A_frozen_enemy_keeps_frozen_through_a_performance()
    {
        // THE PROPS A PERFORMANCE CARRIES, handed to the Shatter's own hook:
        // `ElementalHit.Deal` passes `ValueProp.Unpowered`, `dealer: null` and
        // `cardSource: null`, and `FrozenPower.AfterDamageReceived` refuses on
        // the first two of its three guards. Run rather than reasoned about --
        // the refusal returns before any command, which is exactly why it is
        // reachable headless while a real Shatter is not.
        var enemy = Seat.Klee(30).WithPower<FrozenPower>(1);
        var frozen = enemy.Creature.Powers.OfType<FrozenPower>().Single();

        await frozen.AfterDamageReceived(
            null!, enemy.Creature, default!, ValueProp.Unpowered, null, null);

        Assert.Single(enemy.Creature.Powers.OfType<FrozenPower>());

        // AND THE GATE IS THE REASON, not the harness: the same hook reads
        // `IsPoweredAttack`, which `ValueProp.Unpowered` fails.
        Assert.Contains(
            Il.Calls(Il.Method("FrozenPower", "AfterDamageReceived")),
            c => c.Contains("IsPoweredAttack"));
    }

    [Fact]
    public void A_performance_goes_out_through_the_unpowered_elemental_funnel()
    {
        // `PerformMember` is the ONE implementation of a member acting, and
        // the funnel it uses is what decides both halves of the sentence.
        Assert.Contains(
            Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
            c => c.Contains("ElementalHit.Deal"));

        // The Vulnerable half: `Deal` runs the target's modifiers, and
        // `TargetMods` reads `VulnerablePower` with no powered-attack gate.
        Assert.Contains(
            Il.Calls(Il.Method("ElementalHit", "Deal")),
            c => c.Contains("SimDamagePipeline.TargetMods"));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("SimDamagePipeline", "TargetMods")),
            c => c.Contains("IsPoweredAttack"));
    }

    [Fact]
    public void The_arms_salon_paragraph_names_the_class_a_performance_is_in()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();

        var rules = SalonMemberTips.SalonRulesBody(seat.Creature);

        Assert.Contains(
            "A performance is not an [gold]Attack[/gold]: "
          + "[gold]Vulnerable[/gold] moves it, [gold]Shatter[/gold] and "
          + "on-Attack triggers do not.", rules);
    }

    [Fact]
    public void The_shipped_paragraph_takes_no_such_sentence()
    {
        // The shipped kit's members act on their own turn and its paragraph
        // has never described what a performance IS, so the clause has nowhere
        // to go there -- `FurinaReframeRoundSevenTests`' own split, one
        // sentence over.
        using var _ = new Arm(master: false);
        var seat = Seat.Furina().WithCombatState();

        Assert.DoesNotContain(
            "not an [gold]Attack[/gold]",
            SalonMemberTips.SalonRulesBody(seat.Creature));
    }
}
