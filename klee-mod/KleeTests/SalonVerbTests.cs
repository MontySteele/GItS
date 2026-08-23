using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-118 §5.5 -- the Salon queue-manipulation verbs, C# half.
///
/// TWO KINDS OF PIN, both labelled where they are used.
///
/// BEHAVIOURAL, on real objects: the rotation itself, the leftmost reads and
/// their empty-stage answers. None of those needs a live CombatState, because
/// none of them resolves an act.
///
/// STRUCTURAL (Harness/Il.cs, and see README's headless boundary): anything
/// that RESOLVES -- PerformMember, PerformLeftmost, the turn-start upkeep --
/// needs a combat the harness cannot build. What the packet's hard requirement
/// is actually about is readable without one: that the on-demand verb and the
/// upkeep call the SAME method, and that the rotation calls none of it.
/// </summary>
public class SalonVerbTests
{
    // ---------------------------------------------------------------
    // THE HARD REQUIREMENT: no duplicate Salon-resolution implementation.
    // ---------------------------------------------------------------

    [Fact]
    public void The_turn_start_upkeep_resolves_through_PerformMember()
    {
        // Structural pin. The upkeep must not carry a tick body of its own:
        // the spend, the hit and the block all live in PerformMember, so the
        // hook's own call set is the delegation and nothing else.
        var upkeep = Il.Method("SalonMemberPower", "AfterPlayerTurnStart");
        var calls = Il.Calls(upkeep);

        Assert.Contains("SalonMemberPower.PerformMember", calls);
        Assert.DoesNotContain("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("SalonMemberPower.TickValue", calls);
        Assert.DoesNotContain("ElementalHit.Deal", calls);
    }

    [Fact]
    public void Perform_now_resolves_through_the_same_PerformMember()
    {
        // The other half of the same fact: if either side grew its own copy
        // of the tick body, one of these two tests fails.
        var performNow = Il.Method("SalonMemberPower", "PerformLeftmost");
        var calls = Il.Calls(performNow);

        Assert.Contains("SalonMemberPower.PerformMember", calls);
        Assert.DoesNotContain("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("ElementalHit.Deal", calls);
    }

    [Fact]
    public void The_member_action_pays_the_standard_bill()
    {
        // The bill itself, pinned once, in the one place it is spelled: the
        // Encore upkeep, the scaled amount, the hit or the Block, the burst
        // particle. tier0's byte-for-byte pair covers the arithmetic; this
        // covers "the shared method is the one that pays it".
        var calls = Il.Calls(Il.Method("SalonMemberPower", "PerformMember"));

        Assert.Contains("FurinaResources.Encore", calls);
        Assert.Contains("FurinaResources.SpendEncore", calls);
        Assert.Contains("SalonMemberPower.TickValue", calls);
        Assert.Contains("ElementalHit.Deal", calls);
        Assert.Contains("CreatureCmd.GainBlock", calls);
        Assert.Contains("FurinaResources.GainBurst", calls);
    }

    [Fact]
    public void Perform_now_takes_no_bow_and_does_not_move_the_queue()
    {
        // A performance is not a bow: no Bow call, and no counter apply --
        // the company is not mutated, so the mirror cannot need one.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "PerformLeftmost"));

        Assert.DoesNotContain("SalonMemberPower.Bow", calls);
        Assert.DoesNotContain("PowerCmd.Apply", calls);
    }

    [Fact]
    public void Rotate_performs_nothing_drains_nothing_and_bows_nobody()
    {
        // The rotate contract, structurally: it may touch the company list and
        // the visual layer, and nothing else.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "RotateLeftmost"));

        Assert.DoesNotContain("SalonMemberPower.PerformMember", calls);
        Assert.DoesNotContain("SalonMemberPower.Bow", calls);
        Assert.DoesNotContain("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("FurinaResources.GainBurst", calls);
        Assert.DoesNotContain("ElementalHit.Deal", calls);
        Assert.DoesNotContain("CreatureCmd.GainBlock", calls);
        Assert.DoesNotContain("PowerCmd.Apply", calls);
    }

    [Fact]
    public void Rotate_is_synchronous_because_it_resolves_nothing()
    {
        // Not a style point: a verb that awaited something would be a verb
        // that could resolve something. The signature is the guarantee.
        var rotate = typeof(SalonMemberPower)
            .GetMethod(nameof(SalonMemberPower.RotateLeftmost), HeadlessGame.All)!;

        Assert.Equal(typeof(void), rotate.ReturnType);
        Assert.DoesNotContain(rotate.GetParameters(),
            p => p.ParameterType.Name == "PlayerChoiceContext");
    }

    // ---------------------------------------------------------------
    // BEHAVIOURAL -- real Creature, real company list.
    // ---------------------------------------------------------------

    [Fact]
    public void Rotate_moves_the_leftmost_member_to_the_back()
    {
        var seat = Stage(SalonMember.Crabaletta, SalonMember.Usher,
                         SalonMember.Chevalmarin);

        SalonMemberPower.RotateLeftmost(seat.Creature, 1);

        Assert.Equal(
            new[] { SalonMember.Usher, SalonMember.Chevalmarin,
                    SalonMember.Crabaletta },
            SalonMemberPower.CompanyOf(seat.Creature));
    }

    [Fact]
    public void Rotate_preserves_identity_and_the_counter_mirror()
    {
        var seat = Stage(SalonMember.Usher, SalonMember.Usher,
                         SalonMember.Chevalmarin);

        SalonMemberPower.RotateLeftmost(seat.Creature, 2);

        Assert.Equal(3, SalonMemberPower.CompanyOf(seat.Creature).Count);
        Assert.Equal(2, SalonMemberPower.CompanyOf(seat.Creature)
            .Count(m => m == SalonMember.Usher));
        Assert.Equal(3, SalonMemberPower.Count(seat.Creature));
    }

    [Fact]
    public void Rotate_is_inert_on_an_empty_stage()
    {
        var seat = Seat.Furina().WithCombatState();

        SalonMemberPower.RotateLeftmost(seat.Creature, 2);

        Assert.Empty(SalonMemberPower.CompanyOf(seat.Creature));
    }

    [Fact]
    public void The_leftmost_read_names_the_next_performer()
    {
        var seat = Stage(SalonMember.Chevalmarin, SalonMember.Crabaletta);

        Assert.Equal(SalonMember.Chevalmarin,
            SalonMemberPower.LeftmostMember(seat.Creature));

        SalonMemberPower.RotateLeftmost(seat.Creature, 1);

        Assert.Equal(SalonMember.Crabaletta,
            SalonMemberPower.LeftmostMember(seat.Creature));
    }

    [Fact]
    public void The_leftmost_read_is_null_on_an_empty_stage()
    {
        var seat = Seat.Furina().WithCombatState();

        Assert.Null(SalonMemberPower.LeftmostMember(seat.Creature));
        Assert.Equal(0, SalonMemberPower.LeftmostActValue(seat.Creature));
    }

    [Fact]
    public void The_leftmost_act_value_is_the_members_scaled_tick()
    {
        // The reward half, against TickValue's own pins in
        // DerivationPinTests: 6 printed, +2 from 20 held Fanfare, and the
        // meter is dry so it resolves at three-quarters (8 * 0.75 -> 6).
        var seat = Stage(SalonMember.Crabaletta);
        FurinaResources.GainFanfare(seat.Creature, 20);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.Equal(
            SalonMemberPower.TickValue(
                seat.Creature, SalonMember.Crabaletta, paid: false),
            SalonMemberPower.LeftmostActValue(seat.Creature));

        FurinaResources.GainEncore(seat.Creature, SalonConstants.TickEncoreCost);

        Assert.Equal(
            SalonMemberPower.TickValue(
                seat.Creature, SalonMember.Crabaletta, paid: true),
            SalonMemberPower.LeftmostActValue(seat.Creature));
    }

    /// <summary>
    /// A seat with a company on stage, WITHOUT running Deploy (which needs a
    /// live combat -- see the headless boundary).
    ///
    /// Two things are seeded because the shipped code reads two: the private
    /// per-Creature company list, which carries identity, and the counter
    /// power, which carries the count and which CompanyFor uses to detect a
    /// stale list from a previous combat. The power is allocated uninitialised
    /// for the same reason Seat.WithRelic does it -- a CustomResources-backed
    /// model's constructor registers with BaseLib's model tables, which a test
    /// has no business mutating.
    /// </summary>
    private static Seat Stage(params SalonMember[] members)
    {
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        // The BACKING FIELD, not the setter: PowerModel.Amount's setter is
        // shadowed get-only on the derived power, and the value here is a
        // fixture, not an application -- an apply would need the command
        // pipeline this harness cannot run.
        Seat.Force(power, "Amount", members.Length);
        // Creature.Powers is exposed read-only; the game's own applier
        // writes the backing list, which is what a seeded stage needs.
        ((System.Collections.IList)seat.Creature.Powers).Add(power);

        var company = (IDictionary<Creature, List<SalonMember>>)
            typeof(SalonMemberPower)
                .GetField("Company", HeadlessGame.All)!
                .GetValue(null)!;
        company[seat.Creature] = members.ToList();

        return seat;
    }
}
