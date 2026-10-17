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
/// The Klee/Varka cleanup batch (2026-10-14, staged on <c>klee-next</c>;
/// review/active/klee-varka-cleanup-2026-10-14.md). [USER]: "Otherwise
/// agreed on these." Three never-taken cards made worth a draft:
/// Lizard-Tail Gunpowder draws a plain card, Taste Test exhausts instead of
/// adding two Confiscated (upgrade cost 2 -> 1), Exquisite Compound grows
/// each Bomb by 7 [10]. Sim twin:
/// <c>tier0/tests/test_klee_cleanup_2026_10_14.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeCleanup20261014Tests
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
    public void Lizard_tail_gunpowder_places_a_bomb_and_draws_one_card()
    {
        Assert.Equal("Place a [gold]Bomb[/gold] {BombSize:diff()}. Draw 1 card.",
                     Face(new ProtoKoAmmoScavenging()));
        Assert.Equal(1m, new ProtoKoAmmoScavenging().DynamicVars.Cards.BaseValue);
        Assert.Equal(1m, Upgraded<ProtoKoAmmoScavenging>().DynamicVars.Cards.BaseValue);

        var play = Il.Calls(Il.Method("ProtoKoAmmoScavenging", "OnPlay"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.Draw"));
        Assert.DoesNotContain(play, c => c.Contains("DrawPerSetOff"));
    }

    [Fact]
    public void Taste_test_exhausts_adds_no_confiscated_and_upgrades_to_one_energy()
    {
        Assert.Contains(CardKeyword.Exhaust, new ProtoKoTasteTest().CanonicalKeywords);
        Assert.Equal((2, 1), (new ProtoKoTasteTest().EnergyCost.Canonical,
                              Upgraded<ProtoKoTasteTest>().EnergyCost.GetWithModifiers(CostModifiers.None)));
        Assert.DoesNotContain("Confiscated", Face(new ProtoKoTasteTest()));
        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoKoTasteTest", "OnPlay")),
                              c => c.Contains("AddGeneratedCardToCombat"));
    }

    [Fact]
    public void Exquisite_compound_grows_each_bomb_by_seven_ten_upgraded()
    {
        Assert.Equal((7m, 10m), (new ProtoKoCarefulArrangement().DynamicVars["Grow"].BaseValue,
                                 Upgraded<ProtoKoCarefulArrangement>().DynamicVars["Grow"].BaseValue));
    }
}
