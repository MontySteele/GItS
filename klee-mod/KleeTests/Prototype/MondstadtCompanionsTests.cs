using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE MONDSTADT COMPANION REVIEW (2026-10-03,
/// <c>review/active/mondstadt-companions-2026-10-03.md</c>, both picks ruled
/// at their defaults): Mona's Stellaris Phantasm, Noelle's Breastplate,
/// Sucrose's Wind Spirit Creation and Amber's Fiery Rain. The cards are
/// generated; these pin the numbers and the shape the sheet rows now carry.
/// Sim twin: <c>tier0/tests/test_mondstadt_companions.py</c>.
/// </summary>
[Collection(CompanionOverhaulArm.Name)]
public class MondstadtCompanionsTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    [Fact]
    public void Stellaris_phantasm_applies_vulnerable_now_for_one()
    {
        var card = new ProtoMcMonaStellarisPhantasm();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Equal(
            "Apply [gold]Hydro[/gold] and {PowerAmount:diff()} [gold]Vulnerable[/gold] to ALL enemies.",
            Face(card));
        Assert.Equal(3m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(4m, Upgraded<ProtoMcMonaStellarisPhantasm>()
            .DynamicVars["PowerAmount"].BaseValue);
        // On play, not a promise for next turn: the omen power is gone.
        var play = Il.Calls(Il.Method("ProtoMcMonaStellarisPhantasm", "OnPlay"));
        Assert.Contains(play, c => c.Contains("PowerCmd.Apply"));
        Assert.DoesNotContain(play, c => c.Contains("Omen"));
        Assert.Null(typeof(ProtoMcMonaStellarisPhantasm).Assembly
            .GetType("KleeMod.Powers.StellarisOmenPower"));
    }

    [Fact]
    public void Breastplate_gains_eight_upgrades_to_eleven_and_keeps_its_rider()
    {
        var card = new ProtoMcNoelleBreastplate();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(8m, card.DynamicVars["CalculationBase"].BaseValue);
        Assert.Equal(11m, Upgraded<ProtoMcNoelleBreastplate>()
            .DynamicVars["CalculationBase"].BaseValue);
        Assert.Equal(4m, card.DynamicVars["BranchBlock"].BaseValue);
    }

    [Fact]
    public void Wind_spirit_creation_swirls_all_for_one_and_is_not_exhaust()
    {
        var card = new ProtoMcSucroseGust();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.DoesNotContain(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal(
            "[gold]Swirl[/gold] ALL enemies. Draw {Cards:diff()} card{Cards:plural:|s}.",
            Face(card));
        Assert.Equal(1m, card.DynamicVars.Cards.BaseValue);
        Assert.Equal(2m, Upgraded<ProtoMcSucroseGust>().DynamicVars.Cards.BaseValue);
    }

    [Fact]
    public void Fiery_rain_deals_three_per_hit_and_upgrades_to_four()
    {
        var card = new ProtoMcAmberFieryRain();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Equal(3m, card.DynamicVars["CalculationBase"].BaseValue);
        Assert.Equal(4m, Upgraded<ProtoMcAmberFieryRain>()
            .DynamicVars["CalculationBase"].BaseValue);
        Assert.Contains("3 times", Face(card));
    }

    // ---- sec.4, the Klee-only companions (ruled 2026-10-03) -------------

    [Fact]
    public void Klees_three_own_companions_have_no_owner_and_ride_her_pool()
    {
        foreach (var card in new CardModel[]
                 {
                     new ProtoMcJeanLionsFang(), new ProtoMcPruneHexhunterChime(),
                     new ProtoMcAlbedoDustOfPurification(),
                 })
        {
            var companion = Assert.IsAssignableFrom<global::KleeMod.Cards.ICompanionCard>(card);
            Assert.Null(companion.PersonalPool);
        }
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"));
        Assert.Contains(slice, c => c.Contains("ProtoMcJeanLionsFang"));
        Assert.Contains(slice, c => c.Contains("ProtoMcPruneHexhunterChime"));
        Assert.Contains(slice, c => c.Contains("ProtoMcAlbedoDustOfPurification"));
        Assert.Contains(slice, c => c.Contains("ProtoKoKitchenAlchemy"));
    }

    [Fact]
    public void Four_rows_join_the_shared_roster_and_the_cut_classes_are_gone()
    {
        Assert.Null(new ProtoMcQiqiHeraldOfFrost().PersonalPool);
        Assert.Null(new ProtoMcFischlSinfulHex().PersonalPool);
        Assert.Null(new ProtoMcSucroseMollisFavonius().PersonalPool);
        Assert.Null(new ProtoMcNicoleLadderOfAscent().PersonalPool);
        var assembly = typeof(ProtoMcQiqiHeraldOfFrost).Assembly;
        foreach (var gone in new[]
                 {
                     "ProtoMcBarbaraFrontRowSeat", "ProtoMcDionaShakenNotPurred",
                     "ProtoMcNoelleIGotYourBack", "ProtoMcKaeyaColdBloodedStrike",
                     "ProtoMcSayuSilencersSecret", "ProtoMcYaoyaoYueguiThrowingMode",
                     "ProtoKoSecondSurprise", "ProtoKoSolitaryConfinement",
                     "ProtoKoOnceMore",
                 })
        {
            Assert.Null(assembly.GetType("KleeMod.Cards.Prototype.Generated." + gone));
        }
    }
}
