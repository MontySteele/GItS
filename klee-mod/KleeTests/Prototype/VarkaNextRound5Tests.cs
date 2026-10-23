using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// <c>varka-next</c> (Varka round 5, <c>review/records/varka-round-5-2026-10-13.md</c>,
/// "What to change" 3 and 4; staging paper
/// <c>review/active/varka-next-2026-10-13.md</c>): Eula's Icetide Vortex is
/// an Attack, and Twin Gales pays a matched element twice. The sim halves are
/// in <c>tier0/tests/test_varka_next_2026_10_13.py</c>.
/// </summary>
public class VarkaNextRound5Tests
{
    private static string Face(object model) =>
        model is CustomCardModel card
            ? card.Localization!.First(r => r.Item1 == "description").Item2
            : ((ILocalizationProvider)model).Localization!
                .First(r => r.Item1 == "description").Item2;

    [Fact]
    public void Icetide_vortex_is_an_attack_with_the_same_cost_and_numbers()
    {
        var eula = new ProtoVkEulaIcetideVortex();
        Assert.Equal(CardType.Attack, eula.Type);
        Assert.Equal(1, eula.EnergyCost.Canonical);
        Assert.Equal(8m, eula.DynamicVars.CalculationBase.BaseValue);
        // The upgrade's +3 (8 [11]) is pinned off the IL; the sim pins 11.
        Assert.Contains(Il.Calls(Il.Method("ProtoVkEulaIcetideVortex", "OnUpgrade")),
                        c => c.Contains("UpgradeValueBy"));
        // The other damage Knights are Attacks too.
        Assert.Equal(CardType.Attack, new ProtoVkKaeyaFrostgnaw().Type);
    }

    [Fact]
    public void Twin_gales_reads_the_new_words_on_the_card_and_the_power()
    {
        const string words = "Your [gold]Swirls[/gold] also pay the element "
            + "they [gold]Swirl[/gold]. If that is your [gold]current "
            + "element[/gold], it pays twice.";
        Assert.Equal(words, Face(new ProtoVkTwinGales()));
        Assert.Equal(words, Face(new TwinGalesPower()));
    }

    [Fact]
    public void Twin_gales_pays_the_swirled_element_even_when_it_is_current()
    {
        // The matched case no longer skips the second payout: OnSwirl no
        // longer compares the Swirled element with the current one.
        var calls = Il.Calls(Il.Method("VarkaOath", "OnSwirl")).ToList();
        Assert.Contains(calls, c => c.Contains("VarkaOath.IsOathElement"));
        Assert.Equal("Cryo (" + VarkaLaw.SwirlCryoVulnerable
                     + " Vulnerable) twice",
                     VarkaOath.TwinGalesPaid(Element.Cryo, Element.Cryo, 1));
    }
}
