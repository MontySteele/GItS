using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI V2 SEAT FINDINGS (2026-10-18), the mod's half. Three seats
/// could not see a rule that was working: Tidal Riposte's stored bonus
/// ("never visibly paid off"), Pincer's Plan ("I never knew whether it
/// triggered") and a carry-out repeated by Nereid's Ascension ("War Council"
/// printed twice). Each now names itself on the page. Structural pins (the
/// headless boundary); the page half is
/// <c>tier0/tests/test_kokomi_v2_seat_findings_2026_10_18.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiV2SeatFindingsTests
{
    private static string[] Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToArray();

    [Fact]
    public void The_two_receipts_are_spelled_once()
    {
        Assert.Equal("play_bonus", ResolutionLedger.PlayBonus);
        Assert.Equal("doubled_by", ResolutionLedger.DoubledBy);
    }

    [Fact]
    public void Riposte_names_its_bonus_on_the_attack_that_took_it()
    {
        var after = Calls("TidalRiposteChargePower", "AfterCardPlayed");
        Assert.Contains("ResolutionLedger.NoteEventOnPlay", after);
        Assert.Contains("PowerModel.Flash", after);
        Assert.Contains("Tidal Riposte", Il.Strings(
            Il.Method("TidalRiposteChargePower", "AfterCardPlayed")));
        // Only a play whose hit took the bonus says so.
        Assert.Contains("_paid", Il.FieldsWritten(
            Il.Method("TidalRiposteChargePower", "AfterDamageGiven")));
    }

    [Fact]
    public void Pincer_names_itself_on_the_attack_it_played_twice()
    {
        var after = Calls("FirstAttackTwicePower", "AfterCardPlayed");
        Assert.Contains("ResolutionLedger.NoteEventOnPlay", after);
        Assert.Contains("Pincer", Il.Strings(
            Il.Method("FirstAttackTwicePower", "AfterCardPlayed")));
    }

    [Fact]
    public void A_second_carry_out_names_what_bought_it()
    {
        Assert.Empty(KokomiPlan.AgainSources(1, 1, false, null, 0));
        Assert.Equal(new[] { "Nereid's Ascension" },
                     KokomiPlan.AgainSources(2, 1, false, null, 0));
        Assert.Equal(new[] { "A Stunning Stratagem" },
                     KokomiPlan.AgainSources(2, 2, false, null, 0));
        // Drain's order: the base count, the rider before, All Streams.
        Assert.Equal(new[] { "Nereid's Ascension", "Second Wave",
                             "All Streams" },
                     KokomiPlan.AgainSources(2, 1, true, "Second Wave", 1));
        Assert.Contains("again", Il.Strings(
            Il.Method("KokomiPlan", "CarriedOutRow")));
    }

    /// <summary>Kokomi v3 seats (2026-10-18): Following Current's 3 Hydro
    /// lands after the Plan's beat and printed nothing, so seats thought it
    /// never fired. The hit goes on the carry-out's row (`after`); page half
    /// <c>tier0/tests/test_kokomi_following_current_receipt.py</c>.</summary>
    [Fact]
    public void Following_current_puts_its_hit_on_the_carry_out_row()
    {
        var fc = Il.Method("FollowingCurrentPower", "OnCarriedOut");
        Assert.Contains("KurageHydroSources.Hit", Il.Calls(fc));
        Assert.Contains("KokomiPlan.NoteAfter", Il.Calls(fc));
        Assert.Contains("Following Current", Il.Strings(fc));
        Assert.Contains("ElementalHit.Deal",
                        Il.Calls(Il.Method("KurageHydroSources", "Hit")));
        Assert.Contains("after", Il.Strings(
            Il.Method("KokomiPlan", "CarriedOutRow")));
        // NoteAfter amends the recorded row rather than adding a second.
        Assert.DoesNotContain("KokomiPlan.Record",
                              Il.Calls(Il.Method("KokomiPlan", "NoteAfter")));
    }

    /// <summary>Seat page backlog (2026-10-18; Kokomi round 4, lane 1): a
    /// Sting or Ward a carry-out makes into a full hand goes on that Plan's
    /// row (`discarded`), not on the turn's ordinary line, which printed after
    /// the whole morning. Outside a carry-out the old line stands.</summary>
    [Fact]
    public void A_full_hand_discard_inside_a_carry_out_sits_on_its_plan()
    {
        var add = Il.Method("KokomiCards", "AddJellyfish");
        Assert.Contains("KokomiPlan.NoteDiscardedInBeat", Il.Calls(add));
        Assert.Contains("ResolutionLedger.NoteToDiscard", Il.Calls(add));
        Assert.False(KokomiPlan.NoteDiscardedInBeat(null, "Sting"));
        Assert.Contains("discarded", Il.Strings(
            Il.Method("KokomiPlan", "CarriedOutRow")));
    }

    /// <summary>Seat page backlog (2026-10-18): a Companion summon's
    /// end-of-turn hit (Oz, Soumetsu) is logged for every seat and only
    /// Kokomi's page printed it. Off Kokomi the snapshot carries the summon
    /// log alone (no `pet` key), so a Furina or Klee page prints it too.
    /// </summary>
    [Fact]
    public void Off_kokomi_the_snapshot_carries_the_summon_log()
    {
        var snapshot = Il.Method("KokomiPlan", "Snapshot");
        Assert.Contains("KokomiPlan.SummonHits", Il.Calls(snapshot));
        Assert.Contains("summon_hits", Il.Strings(snapshot));
        Assert.Empty(KokomiPlan.Snapshot(null));
    }
}
