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
}
