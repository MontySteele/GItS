using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Relics;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// Suite (b): pure logic that needs no combat -- the localization builders.
///
/// WHY THIS IS WORTH A TEST. The tooltip text is the one projection of the
/// balance constants that `lint_constant_parity` structurally cannot see: it
/// compares named consts between the engines and has no opinion about prose.
/// Both of these descriptions were literal strings once, and both went stale
/// against a repricing. M24's own note records the consequence: signing the
/// six salon numbers is a ONE-file edit only because the power interpolates
/// SalonConstants instead of restating it.
///
/// The power models are allocated uninitialised -- their real constructors
/// register with the game's model tables, and these properties are pure
/// string builders that read nothing off the instance.
/// </summary>
public class InterpolationPinTests
{
    private static T Bare<T>() => (T)RuntimeHelpers.GetUninitializedObject(typeof(T));

    private static string Loc<T>(T model, string key) where T : notnull
    {
        var rows = (System.Collections.Generic.List<(string, string)>)
            model.GetType()
                .GetProperty("Localization", Harness.HeadlessGame.All)!
                .GetValue(model)!;
        return rows.First(r => r.Item1 == key).Item2;
    }

    [Fact]
    public void Salon_member_description_prints_the_live_constants()
    {
        var body = Loc(Bare<SalonMemberPower>(), "description");

        Assert.Contains($"spends {SalonConstants.TickEncoreCost} Encore", body);
        Assert.Contains($"Crabaletta deals {SalonConstants.CrabalettaTick} Hydro", body);
        Assert.Contains($"Usher gains {SalonConstants.UsherTick} Block", body);
        Assert.Contains($"Chevalmarin deals {SalonConstants.ChevalmarinTick} Hydro", body);
        Assert.Contains($"+1 per {SalonConstants.FocusPerFanfare} [gold]Fanfare[/gold]", body);
        Assert.Contains($"Maximum {SalonConstants.MemberSlots}", body);
        Assert.Contains($"Crabaletta deals {SalonConstants.CrabalettaBow}", body);
        Assert.Contains($"Usher gains {SalonConstants.UsherBow} ", body);
        Assert.Contains($"grants {SalonConstants.ChevalmarinBowEncore} Encore", body);
    }

    [Fact]
    public void Salon_member_description_carries_all_six_M24_numbers()
    {
        // The blunt version of the test above, and the one that would catch a
        // repricing that edited the constants and a hand-typed sentence at the
        // same time. Written as values, not as the constants, so it fails on
        // a repricing until somebody looks at it.
        var body = Loc(Bare<SalonMemberPower>(), "description");
        foreach (var n in new[] { "6 Hydro", "3 Block", "2 Hydro", "14", "9 ", "3 Encore" })
        {
            Assert.Contains(n, body);
        }
    }

    [Fact]
    public void Pearl_of_insight_panel_prints_the_doubled_numbers_it_actually_grants()
    {
        // EPOCH 2 / D1's exact defect, from the other direction: the panel
        // said doubled and the funnel granted base. Both now read the relic.
        var body = Loc(Bare<PearlOfInsightRelic>(), "description");

        Assert.Contains($"gain {PearlOfInsightRelic.ChargePerExhaust} [gold]Charge[/gold]", body);
        Assert.Contains($"and {PearlOfInsightRelic.BurstPerExhaust} Burst Energy", body);
        Assert.Contains("gain 2 [gold]Charge[/gold]", body);
        Assert.Contains("and 4 Burst Energy", body);
    }

    [Fact]
    public void Pearl_of_wisdom_panel_prints_the_base_numbers()
    {
        var body = Loc(Bare<PearlOfWisdomRelic>(), "description");

        Assert.Contains($"gain {KokomiConstants.ChargePerExhaust} [gold]Charge[/gold]", body);
        Assert.Contains($"and {KokomiConstants.BurstPerExhaust} Burst Energy", body);
    }

    [Fact]
    public void Salon_member_display_names_are_the_ruled_stage_names()
    {
        // B5's ruled grammar: the FACE names who takes the stage.
        Assert.Equal("Mademoiselle Crabaletta",
            global::KleeMod.Cards.SalonMemberTips.DisplayName(SalonMember.Crabaletta));
        Assert.Equal("Gentilhomme Usher",
            global::KleeMod.Cards.SalonMemberTips.DisplayName(SalonMember.Usher));
        Assert.Equal("Surintendante Chevalmarin",
            global::KleeMod.Cards.SalonMemberTips.DisplayName(SalonMember.Chevalmarin));
    }
}
