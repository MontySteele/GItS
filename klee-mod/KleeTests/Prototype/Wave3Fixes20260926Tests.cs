#nullable enable

using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The wave-3 seat round's fixes (2026-09-26) that still stand: A Five-Century
/// Act's face, the Ancient's retired keyword under the Klee arm, and the
/// Pneuma and Thunderous Applause faces. The re-founding (2026-10-04) retired
/// the rest with the performer bars (why an act could not pay is one reason
/// now, a short star; the hit and Let the People Rejoice labels went with
/// absorption). The page halves are
/// <c>tier0/tests/test_wave3_fixes_2026_09_26.py</c>.
/// </summary>
public class Wave3Fixes20260926Tests
{
    private static string Description(List<(string, string)>? loc) =>
        loc!.Single(row => row.Item1 == "description").Item2;

    [Fact]
    public void A_five_century_act_says_it_returns_only_to_a_free_seat()
    {
        // The re-founding (sec.10): no Fanfare on the return.
        const string face =
            "The first time each turn a performer [gold]Bow[/gold]s and "
          + "leaves, it returns at the back if a seat is free.";
        Assert.Equal(face, Description(new ProtoFsFiveCenturyAct().Localization));
        Assert.Equal(face, Description(new FiveCenturyActPower().Localization));
    }

    [Fact]
    public void Jumpy_dumpty_mk_omega_drops_the_burst_keyword_under_the_arm()
    {
        // BaseLib assigns the custom keywords' values at registration, so
        // headless they are all one value: the pin is the count.
        var arm = new JumpyDumptyMkOmega().CanonicalKeywords.ToList();
        Assert.Equal(new[] { KleeKeywords.AppliesPyro }, arm);
    }

    [Fact]
    public void The_pneuma_tip_says_it_gains_fanfare()
    {
        // The re-founding (sec.8): "Arkhe Alignment's Pneuma mode: Gain 2
        // Fanfare."
        var printed = string.Concat(Il.Strings(
            typeof(ArmKeywordTips).GetMethod(nameof(ArmKeywordTips.ForPneuma),
                                             HeadlessGame.All)!));
        Assert.Contains("Gain ", printed);
        Assert.DoesNotContain("front performer", printed);
    }

    [Fact]
    public void Thunderous_applause_names_its_amount()
    {
        Assert.Contains(
            "draw [blue]{Amount}[/blue]",
            Description(new ThunderousApplausePower().Localization));
    }
}
