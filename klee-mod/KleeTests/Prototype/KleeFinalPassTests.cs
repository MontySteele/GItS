using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE FINAL PASS (2026-10-02, ruled). Paper
/// <c>review/active/klee-final-pass-2026-10-02.md</c>, "Ruled": HP 70;
/// Kitchen Alchemy unchanged; Cover Your Ears! in (Uncommon Skill, 0 Energy
/// and 2 Sparks, Exhaust: "ALL enemies lose 6 [8] Strength this turn.");
/// Blast Shield to Common; Where Did I Put It? cut. Sim twin:
/// <c>tier0/tests/test_klee_final_pass.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeFinalPassTests
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

    [Fact]
    public void Klee_starts_on_seventy()
    {
        Assert.Equal(70, new global::KleeMod.Klee().StartingHp);
    }

    [Fact]
    public void Cover_your_ears_is_an_uncommon_free_skill_priced_two_sparks()
    {
        var card = new ProtoKoCoverYourEars();
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Contains(CardKeyword.Exhaust, card.Keywords);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Equal((6m, 8m),
            (card.DynamicVars["StrengthLoss"].BaseValue,
             Upgraded<ProtoKoCoverYourEars>().DynamicVars["StrengthLoss"].BaseValue));
        Assert.Equal(
            "ALL enemies lose {StrengthLoss:diff()} [gold]Strength[/gold] this turn.",
            Face(card));
    }

    [Fact]
    public void Cover_your_ears_spends_then_applies_piercing_wails_temporary_strength()
    {
        // STRUCTURAL: the play needs a live combat. The Spark price first,
        // then the card's own TemporaryStrengthPower on every hittable enemy
        // -- Piercing Wail's call -- and never a permanent StrengthPower.
        var play = Seq("ProtoKoCoverYourEars", "OnPlay");
        var spend = play.FindIndex(c => c.Contains("SparkPower.Spend"));
        var loss = play.FindIndex(c => c.Contains("PowerCmd.Apply<ProtoKoCoverYourEarsPower>"));
        Assert.True(spend >= 0 && loss > spend);
        Assert.DoesNotContain(play, c => c.Contains("PowerCmd.Apply<StrengthPower>"));
    }

    [Fact]
    public void Its_power_is_a_negative_temporary_strength_named_for_the_card()
    {
        Assert.True(typeof(TemporaryStrengthPower)
            .IsAssignableFrom(typeof(ProtoKoCoverYourEarsPower)));
        var power = new ProtoKoCoverYourEarsPower();
        Assert.Equal(PowerType.Debuff, power.Type);
        // The origin is the card (its title is the card's); ModelDb is not
        // populated headless, so the getter's one call is the pin.
        Assert.Contains(Seq("ProtoKoCoverYourEarsPower", "get_OriginModel"),
                        c => c.Contains("ModelDb.Card") && c.Contains("ProtoKoCoverYourEars"));
    }

    [Fact]
    public void Blast_shield_is_common_and_where_did_i_put_it_is_gone()
    {
        Assert.Equal(CardRarity.Common, new ProtoKoBlastShield().Rarity);
        Assert.Null(typeof(ProtoKoCoverYourEars).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoKoWhereDidIPutIt"));
        var slice = Seq("KleeOverhaulRoster", "Slice");
        Assert.Contains(slice, c => c.Contains("ProtoKoCoverYourEars"));
        Assert.DoesNotContain(slice, c => c.Contains("ProtoKoWhereDidIPutIt"));
    }
}
