using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA ROUND 7, `EB-451` -- A MEMBER'S ROLL SKIPS A MINION.
///
/// THE FIND. Fight 7 held the run's ONE paid performance: members had gone dry
/// (three-quarters, no Encore) in every earlier fight, the seat paid for a wet
/// one, and the roll aimed it at the 6-HP Eye with Teeth, whose own status line
/// says it revives at full. The rule was printed -- "the member picks its own
/// enemy at random, never the card's target" -- and the outcome still handed
/// the Encore economy's payoff to the roll at the moment it was worth most.
///
/// THE SHAPE IS R250'S. That ruling made a Plan aim a non-Minion unless it is
/// aimed, over the same evidence (a decoy absorbing the one hit that mattered);
/// the r7 packet's §4 applies the same shape to the member roll as an F
/// default. <see cref="SalonMemberPower.AimPool"/> is the twin of
/// <c>KokomiPlan.FrontEnemy</c> down to the all-Minion fallback, and the sim's
/// is <c>effects.salon_aim_pool</c>.
///
/// NOT ARM-SCOPED, and the pins say so: the roll under test is the shipped
/// kit's as well as the reframe's, because <see cref="SalonMemberPower.PerformMember"/>
/// and the bow are one implementation each. The arm's own PARAGRAPH is where
/// the sentence goes, because the arm's paragraph is the only one that has ever
/// described the aim at all.
/// </summary>
public class FurinaReframeRoundSevenTests
{
    /// <summary>Turn the reframe's MANUAL leg on for one test -- the leg whose
    /// rules paragraph carries the aim sentence -- and put every flag back
    /// after it. `FurinaReframeBurstTests.Arm`'s reasoning, and all six flags
    /// for its reason.</summary>
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

    /// <summary>A body on the board. The harness builds REAL `Creature`s, and
    /// a Minion is one wearing the base game's own `MinionPower` -- the mark
    /// the Kin's Followers and the Amalgam already carry, which is why the rule
    /// reads it instead of inventing a second flag.</summary>
    private static Creature Body(bool minion = false)
    {
        var seat = Seat.Klee(maxHp: 20);
        if (minion) seat = seat.WithPower<MinionPower>(1);
        return seat.Creature;
    }

    // ==================================================================
    // 1. THE POOL -- what the roll may pick
    // ==================================================================

    [Fact]
    public void A_minion_is_out_of_the_pool_while_a_non_minion_stands()
    {
        var eye = Body(minion: true);
        var kin = Body();

        var pool = SalonMemberPower.AimPool(new[] { eye, kin });

        // The r7 board, and the whole of the find: 20 rolls over this pool
        // cannot reach the reviving body, because it is not in it.
        Assert.Equal(new[] { kin }, pool);
    }

    [Fact]
    public void Board_order_survives_the_filter()
    {
        var first = Body();
        var decoy = Body(minion: true);
        var last = Body();

        Assert.Equal(new[] { first, last },
                     SalonMemberPower.AimPool(new[] { first, decoy, last }));
    }

    [Fact]
    public void An_all_minion_board_keeps_every_body()
    {
        // `KokomiPlan.FrontEnemy`'s fallback, and the same argument: a
        // performance that lands on nothing is worse than one that lands on
        // the decoy. Getting this wrong would silently delete the Salon on a
        // board of adds.
        var a = Body(minion: true);
        var b = Body(minion: true);

        Assert.Equal(new[] { a, b }, SalonMemberPower.AimPool(new[] { a, b }));
    }

    [Fact]
    public void An_empty_or_absent_board_is_answered_and_not_thrown_at()
    {
        // `PerformMember` uses this list as its "can the stage act at all"
        // test, so the empty answer has to stay empty and the null answer null.
        Assert.Empty(SalonMemberPower.AimPool(Array.Empty<Creature>())!);
        Assert.Null(SalonMemberPower.AimPool(null));
    }

    [Fact]
    public void The_pool_reads_the_games_own_minion_mark()
    {
        // STRUCTURAL, the pin `KokomiOverhaulRuleTests` takes for the Plan's
        // aim: if the predicate is ever rewritten against something other than
        // `MinionPower`, this fails rather than the rule quietly widening.
        var pool = Il.Method("SalonMemberPower", "AimPool");
        Assert.Contains("SalonMemberPower.IsNotMinion", Il.Calls(pool));

        var isNotMinion = Il.Method("SalonMemberPower", "IsNotMinion");
        Assert.Contains(Il.CallSequence(isNotMinion),
                        c => c.Contains("MinionPower"));
    }

    // ==================================================================
    // 2. THE TWO ROLLERS -- one implementation each, both through the pool
    // ==================================================================

    [Fact]
    public void Both_rollers_draw_from_the_pool_and_not_from_the_board()
    {
        // The performance and the bow are the only two places a member picks a
        // body (`FurinaReframeLedger`'s "THE TARGET IS PICKED HERE AND NOWHERE
        // ELSE" note names both). A fix on one of them is half a fix.
        Assert.Contains("SalonMemberPower.AimPool",
                        Il.Calls(Il.Method("SalonMemberPower", "PerformMember")));
        Assert.Contains("SalonMemberPower.AimPool",
                        Il.Calls(Il.Method("SalonMemberPower", "Bow")));
    }

    // ==================================================================
    // 3. THE SENTENCE
    // ==================================================================

    [Fact]
    public void The_arms_rules_paragraph_says_the_roll_skips_a_minion()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();

        var rules = SalonMemberTips.SalonRulesBody(seat.Creature);

        Assert.Contains("picks its own enemy, never a [gold]Minion[/gold] "
                      + "while another enemy stands", rules);
    }

    [Fact]
    public void The_shipped_paragraph_still_states_no_aim_at_all()
    {
        // The shipped rules paragraph has never described the aim -- it is
        // about the cap and the bow order -- so the clause has nowhere to go
        // there and does not go anywhere. The BEHAVIOUR is shared; the sentence
        // is the arm's because the sentence it qualifies is the arm's.
        using var _ = new Arm(master: false);
        var seat = Seat.Furina().WithCombatState();

        var rules = SalonMemberTips.SalonRulesBody(seat.Creature);

        Assert.DoesNotContain("Minion", rules);
        Assert.Contains("bows the OLDEST member out", rules);
    }
}
