using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE STATUS PACKAGE (2026-10-01, ruled). Paper
/// <c>review/active/klee-status-package-2026-10-01.md</c>: "1) I think a) is
/// fine - we can keep tho the game's conventions 2) and 3) agreed on your
/// defaults". Eight pool cards in (Dazed on the fair loaders, Confiscated on
/// the busted ones, and the payoffs), eight out, and Albedo's Klee stand-in
/// is Dust of Purification. A status is Status type or Status rarity. What
/// awaits a command is pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_klee_status_package.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeStatusPackageTests
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

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static readonly string[] Package =
    {
        "ProtoKoForbiddenFun", "ProtoKoItWasntMe", "ProtoKoLisasTreats",
        "ProtoKoRedKnight", "ProtoKoFindersKeepers", "ProtoKoKleeCanExplain",
        "ProtoKoDamageReport", "ProtoKoSolitaryConfinement",
    };

    [Fact]
    public void The_offer_is_seventy_eight_with_the_eight_last_and_the_eight_gone()
    {
        var slice = Seq("KleeOverhaulRoster", "Slice")
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();
        Assert.Equal(78, slice.Count);
        Assert.Equal(Package, slice.Skip(70).ToArray());
        foreach (var gone in new[] { "PocketFireworks", "RapidFire",
                                     "FlameDance", "DodocoCover", "CarefulNow",
                                     "SplitCharge", "FishFry",
                                     "FriendshipBracelet" })
        {
            Assert.DoesNotContain(slice, c => c == "ProtoKo" + gone);
            Assert.Null(typeof(ProtoKoPop).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated.ProtoKo" + gone));
        }
        Assert.Null(typeof(ProtoKoPop).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoMcAlbedoTectonicTide"));
    }

    [Fact]
    public void The_eight_rows_have_the_papers_types_costs_and_rarities()
    {
        var shapes = new (CardModel Card, CardType Type, int Cost, CardRarity Rarity)[]
        {
            (new ProtoKoForbiddenFun(), CardType.Attack, 0, CardRarity.Common),
            (new ProtoKoItWasntMe(), CardType.Skill, 0, CardRarity.Common),
            (new ProtoKoLisasTreats(), CardType.Skill, 0, CardRarity.Uncommon),
            (new ProtoKoRedKnight(), CardType.Attack, 2, CardRarity.Rare),
            (new ProtoKoFindersKeepers(), CardType.Power, 1, CardRarity.Uncommon),
            (new ProtoKoKleeCanExplain(), CardType.Skill, 1, CardRarity.Uncommon),
            (new ProtoKoDamageReport(), CardType.Power, 1, CardRarity.Rare),
            (new ProtoKoSolitaryConfinement(), CardType.Power, 1, CardRarity.Rare),
            (new ProtoMcAlbedoDustOfPurification(), CardType.Skill, 1, CardRarity.Rare),
        };
        foreach (var (card, type, cost, rarity) in shapes)
        {
            Assert.Equal(type, card.Type);
            Assert.Equal(cost, card.EnergyCost.Canonical);
            Assert.Equal(rarity, card.Rarity);
        }
    }

    [Fact]
    public void The_papers_numbers_and_their_upgrades()
    {
        Assert.Equal((10m, 14m), (new ProtoKoForbiddenFun().DynamicVars.Damage.BaseValue,
                                  Upgraded<ProtoKoForbiddenFun>().DynamicVars.Damage.BaseValue));
        Assert.Equal((6m, 9m), (new ProtoKoItWasntMe().DynamicVars.Block.BaseValue,
                                Upgraded<ProtoKoItWasntMe>().DynamicVars.Block.BaseValue));
        Assert.Equal((2m, 3m), (new ProtoKoLisasTreats().DynamicVars["Energy"].BaseValue,
                                Upgraded<ProtoKoLisasTreats>().DynamicVars["Energy"].BaseValue));
        Assert.Equal((22m, 28m), (new ProtoKoRedKnight().DynamicVars.Damage.BaseValue,
                                  Upgraded<ProtoKoRedKnight>().DynamicVars.Damage.BaseValue));
        Assert.Equal((5m, 7m), (new ProtoKoFindersKeepers().DynamicVars["PowerAmount"].BaseValue,
                                Upgraded<ProtoKoFindersKeepers>().DynamicVars["PowerAmount"].BaseValue));
        Assert.Equal((6m, 8m), (new ProtoKoKleeCanExplain().DynamicVars.Block.BaseValue,
                                Upgraded<ProtoKoKleeCanExplain>().DynamicVars.Block.BaseValue));
        Assert.Equal((5m, 7m), (new ProtoKoDamageReport().DynamicVars["PowerAmount"].BaseValue,
                                Upgraded<ProtoKoDamageReport>().DynamicVars["PowerAmount"].BaseValue));
        Assert.Equal((6m, 8m), (new ProtoMcAlbedoDustOfPurification().DynamicVars["Grow"].BaseValue,
                                Upgraded<ProtoMcAlbedoDustOfPurification>().DynamicVars["Grow"].BaseValue));
        Assert.DoesNotContain(CardKeyword.Innate,
                              new ProtoKoSolitaryConfinement().Keywords);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKoSolitaryConfinement>().Keywords);
    }

    [Fact]
    public void The_loaders_shuffle_dazed_or_add_confiscated_to_the_draw_pile()
    {
        foreach (var dazed in new[] { "ProtoKoForbiddenFun", "ProtoKoItWasntMe" })
        {
            Assert.Contains(Seq(dazed, "OnPlay"), c => c.Contains("Dazed"));
            Assert.Contains("Shuffle a [gold]Dazed[/gold] into your draw pile.",
                            Face((CardModel)Activator.CreateInstance(
                                typeof(ProtoKoPop).Assembly.GetType(
                                    "KleeMod.Cards.Prototype.Generated." + dazed)!)!));
        }
        foreach (var confiscated in new[] { "ProtoKoLisasTreats", "ProtoKoRedKnight" })
        {
            var play = Seq(confiscated, "OnPlay");
            Assert.Contains(play, c => c.Contains("Confiscated"));
            Assert.Contains(play, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        }
    }

    [Fact]
    public void A_status_is_status_type_or_status_rarity()
    {
        Assert.True(KleeStatusPackage.IsStatus(
            new MegaCrit.Sts2.Core.Models.Cards.Dazed()));
        Assert.True(KleeStatusPackage.IsStatus(new Confiscated()));
        Assert.True(KleeStatusPackage.IsConfiscated(new Confiscated()));
        Assert.False(KleeStatusPackage.IsStatus(new ProtoKoPop()));
        Assert.False(KleeStatusPackage.IsStatus(null));
    }

    [Fact]
    public void The_payoffs_call_their_bodies()
    {
        Assert.Contains(Seq("ProtoKoKleeCanExplain", "OnPlay"),
                        c => c.Contains("KleeStatusPackage.TransformStatusesInto"));
        var transform = Seq("KleeStatusPackage", "TransformStatusesInto");
        Assert.Contains(transform, c => c.Contains("CardCmd.Transform"));
        Assert.Contains(Seq("ProtoMcAlbedoDustOfPurification", "OnPlay"),
                        c => c.Contains("KleeStatusPackage.ExhaustStatusesGrowLargest"));
        var dust = Seq("KleeStatusPackage", "ExhaustStatusesGrowLargest");
        Assert.Contains(dust, c => c.Contains("CardCmd.Exhaust"));
        Assert.Contains(dust, c => c.Contains("ProtoBombPower.GrowLargest"));
        Assert.Contains(Seq("FindersKeepersPower", "AfterCardPlayed"),
                        c => c.Contains("ProtoBombPower.PlaceOnRandom"));
        Assert.Contains(Seq("DamageReportPower", "AfterCardDrawn"),
                        c => c.Contains("ElementalHit.DealUnelemented"));
    }

    [Fact]
    public void Solitary_confinement_frees_confiscated_and_nothing_else()
    {
        var power = new SolitaryConfinementPower();
        Assert.False(power.TryModifyEnergyCostInCombat(
            new ProtoKoPop(), 1m, out var other));
        Assert.Equal(1m, other);
    }

    [Fact]
    public void Makers_of_dazed_and_confiscated_carry_their_tips()
    {
        Assert.Contains(Il.Strings(Il.Method("KleeCardTooltips", "ForCard"))
                            .Concat(Seq("KleeCardTooltips", "ForCard")),
                        c => c.Contains("Dazed"));
        Assert.Contains("Pop!", Face(new ProtoKoKleeCanExplain()));
        Assert.Contains("[gold]Confiscated[/gold]", Face(new ProtoKoSolitaryConfinement()));
    }
}
