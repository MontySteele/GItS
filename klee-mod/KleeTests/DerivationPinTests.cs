using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Suite (a), second half: derivations that need a real Creature.
///
/// Everything here runs the SHIPPED method against a real game object. No
/// arithmetic is restated -- the expected values are literals, so a formula
/// change fails rather than following along.
/// </summary>
public class DerivationPinTests
{
    // ---------------------------------------------------------------
    // AUDIT FINDING H3 -- AUTHORITY PIN, NOT A FIX.
    //
    // The 2026-08-13 correctness audit found that the Fanfare ceiling is
    // computed from LIVE max HP in the mod and from the sheet's FROZEN
    // printed HP in tier0. LAW.md:189 ("Fanfare is capped at %maxHP") makes
    // the mod's live reading the authority and the sim the deviation, so
    // the repair belongs to the sim (BACKLOG EB-97, window 2).
    //
    // These tests exist to RECORD what the C# side does today, so the
    // window-2 fix has something to converge on and cannot quietly move the
    // authority while claiming to move the deviation. They must NOT be
    // "fixed" -- if EB-97 also gives the mod a named FANFARE_CAP_FRACTION
    // constant, the numbers below stay and only the expression changes.
    // ---------------------------------------------------------------

    [Theory]
    [InlineData(60, 30)]  // the sheet's printed HP
    [InlineData(36, 18)]  // after Decipher's -24 (the audit's failure case)
    [InlineData(52, 26)]  // after the realistic -8
    [InlineData(67, 33)]  // after Eat the Egg's +7 -- integer division truncates
    [InlineData(1, 0)]
    [InlineData(0, 0)]
    public void H3_authority_fanfare_cap_is_half_of_live_max_hp(int maxHp, int cap)
    {
        var seat = Seat.Furina(maxHp);
        Assert.Equal(cap, FurinaResources.FanfareCap(seat.Creature));
    }

    [Fact]
    public void H3_authority_fanfare_cap_tracks_max_hp_inside_one_combat()
    {
        // The leg refuter 1 said the finding UNDER-sells: an in-combat
        // gain_max_hp raises the mod's ceiling immediately, while the sim's
        // stays frozen for the whole run. One creature, two reads.
        var seat = Seat.Furina(60);
        Assert.Equal(30, FurinaResources.FanfareCap(seat.Creature));

        seat.WithMaxHp(36);
        Assert.Equal(18, FurinaResources.FanfareCap(seat.Creature));
    }

    [Fact]
    public void H3_authority_fanfare_cap_clamps_the_meter_on_gain()
    {
        var seat = Seat.Furina(60).WithCombatState();

        FurinaResources.GainFanfare(seat.Creature, 100);

        Assert.Equal(30, FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void Fanfare_cap_is_zero_for_a_seat_that_is_not_furina()
    {
        // Identity gating, not an HP fact: a Klee seat at 80 max HP would
        // read 40 if the guard were dropped.
        var klee = Seat.Klee(80);
        Assert.Equal(0, FurinaResources.FanfareCap(klee.Creature));
    }

    [Fact]
    public void Fanfare_reads_zero_with_no_combat_state()
    {
        // The `?? 0` fallback on every resource accessor. Pinned because the
        // harness relies on it: a seat built without WithCombatState() must
        // read zero rather than throw.
        var seat = Seat.Furina();
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.Equal(0, FurinaResources.Burst(seat.Creature));
    }

    // ---------------------------------------------------------------
    // Salon tick derivation: printed base + the Fanfare Focus term, then
    // the dry cut. SalonMemberTips and the D1 role chip both render this
    // expression, so it is the one place the six M24 numbers become
    // observable values.
    // ---------------------------------------------------------------

    [Fact]
    public void Salon_tick_is_the_printed_base_when_no_fanfare_is_held()
    {
        var seat = Seat.Furina().WithCombatState();

        Assert.Equal(6, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true));
        Assert.Equal(3, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Usher, paid: true));
        Assert.Equal(2, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Chevalmarin, paid: true));
    }

    [Fact]
    public void Salon_tick_gains_one_per_ten_held_fanfare()
    {
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainFanfare(seat.Creature, 30);   // clamped by the cap to 30

        Assert.Equal(30, FurinaResources.Fanfare(seat.Creature));
        Assert.Equal(9, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true));
    }

    [Fact]
    public void A_dry_member_acts_at_three_quarters_truncated()
    {
        var seat = Seat.Furina().WithCombatState();
        FurinaResources.GainFanfare(seat.Creature, 30);

        // 9 * 0.75 = 6.75 -> 6. The truncation is the shipped behaviour and
        // is what the tooltip's "three-quarters" resolves to.
        Assert.Equal(6, SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: false));
    }

    [Fact]
    public void Stage_size_is_the_base_cap_with_no_cap_up_powers()
    {
        var seat = Seat.Furina();
        Assert.Equal(SalonConstants.MemberSlots, SalonMemberPower.SlotsFor(seat.Creature));
        Assert.True(SalonMemberPower.StageIsFull(seat.Creature, 3));
        Assert.False(SalonMemberPower.StageIsFull(seat.Creature, 2));
    }
}
