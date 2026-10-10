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
/// THE KLEE DESIGN REVIEW (2026-10-08, ruled,
/// review/active/klee-design-review-2026-10-08.md, all five picks at the
/// defaults). [USER]: "Nope, this all looks good. I'm now in agreement with
/// all picks." Rule 1 grows 2, rule 4 opens with 3, every drafted placer
/// prints 2 bigger, Fire! Fire! and Blasting Spree in for Playdate and Pop!
/// (Pop! kept in her CardPool for Klee Can Explain!). 78 and 25 / 32 / 21
/// held (<see cref="PoolCountTests"/>). Sim twin:
/// <c>tier0/tests/test_klee_design_review.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeDesignReviewTests
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

    private static List<string> SliceTypes() =>
        Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    [Fact]
    public void The_rules_grow_two_and_open_with_three()
    {
        Assert.Equal(2, KleeOverhaulLaw.BombGrowth);
        Assert.Equal(4, KleeOverhaulLaw.BombGrowth * KleeOverhaulLaw.AliceMultiplier);
        Assert.Equal(3, KleeOverhaulLaw.OpeningSpark);
        Assert.Contains("Start each combat with 3.", ArmKeywordTips.SparkBody(true));
    }

    [Fact]
    public void Two_out_two_in_after_the_tempo_five()
    {
        var slice = SliceTypes();
        Assert.Equal(78, slice.Count);
        Assert.Equal(new[] { "ProtoKoFireFire", "ProtoKoBlastingSpree" },
                     slice.Skip(73).Take(2).ToArray());
        Assert.DoesNotContain("ProtoKoPlaydate", slice);
        Assert.DoesNotContain("ProtoKoPop", slice);
        Assert.Null(typeof(ProtoKoPop).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoKoPlaydate"));
        // Pop! stays compiled and Common: Klee Can Explain! creates it.
        Assert.Equal(CardRarity.Common, new ProtoKoPop().Rarity);
        Assert.Equal(5m, new ProtoKoPop().DynamicVars["BombSize"].BaseValue);
    }

    [Fact]
    public void The_two_have_the_papers_shapes_numbers_and_faces()
    {
        var fire = new ProtoKoFireFire();
        Assert.Equal((CardType.Attack, 1, CardRarity.Common),
                     (fire.Type, fire.EnergyCost.Canonical, fire.Rarity));
        Assert.Equal(TargetType.AnyEnemy, fire.TargetType);
        Assert.True(fire is ISetOffCard);
        Assert.Equal((7m, 10m), (fire.DynamicVars["BombSize"].BaseValue,
            Upgraded<ProtoKoFireFire>().DynamicVars["BombSize"].BaseValue));
        Assert.Equal("Place a [gold]Bomb[/gold] {BombSize:diff()} on the enemy. "
                   + "[gold]Set off[/gold] the enemy.", Face(fire));
        var play = Il.CallSequence(Il.Method("ProtoKoFireFire", "OnPlay")).ToList();
        Assert.True(play.IndexOf("ProtoBombPower.Place")
                    < play.IndexOf("ProtoBombPower.SetOffAimed"));

        var spree = new ProtoKoBlastingSpree();
        Assert.Equal((CardType.Skill, 1, CardRarity.Common),
                     (spree.Type, spree.EnergyCost.Canonical, spree.Rarity));
        Assert.Equal((4m, 6m), (spree.DynamicVars["BombSize"].BaseValue,
            Upgraded<ProtoKoBlastingSpree>().DynamicVars["BombSize"].BaseValue));
        Assert.Equal("Place a [gold]Bomb[/gold] {BombSize:diff()} on ALL enemies. "
                   + "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold].",
                     Face(spree));
        var calls = Il.Calls(Il.Method("ProtoKoBlastingSpree", "OnPlay"));
        Assert.Contains("ProtoBombPower.PlaceOnAll", calls);
        Assert.DoesNotContain(calls, c => c.Contains("SetOff"));
    }

    [Fact]
    public void Every_drafted_placer_prints_two_bigger()
    {
        var rows = new (CardModel Card, CardModel Up, string Var, decimal Base, decimal Plus)[]
        {
            (new ProtoKoMineToss(), Upgraded<ProtoKoMineToss>(), "BombSize", 9m, 12m),
            (new ProtoKoBangBang(), Upgraded<ProtoKoBangBang>(), "BombSize", 6m, 8m),
            (new ProtoKoAmmoScavenging(), Upgraded<ProtoKoAmmoScavenging>(), "BombSize", 6m, 9m),
            (new ProtoKoBoobyTrap(), Upgraded<ProtoKoBoobyTrap>(), "BombSize", 7m, 10m),
            (new ProtoKoCovenErrand(), Upgraded<ProtoKoCovenErrand>(), "BombSize", 10m, 12m),
            (new ProtoKoWitchesCircle(), Upgraded<ProtoKoWitchesCircle>(), "PowerAmount", 5m, 7m),
            (new ProtoKoBombsAway(), Upgraded<ProtoKoBombsAway>(), "BombSize", 6m, 8m),
            (new ProtoKoHidingSpot(), Upgraded<ProtoKoHidingSpot>(), "BombSize", 5m, 7m),
            (new ProtoKoJumpyDumptyMkIii(), Upgraded<ProtoKoJumpyDumptyMkIii>(), "BombSize", 4m, 5m),
            (new ProtoKoMineAllMine(), Upgraded<ProtoKoMineAllMine>(), "BombSize", 6m, 8m),
            (new ProtoKoPartyPoppers(), Upgraded<ProtoKoPartyPoppers>(), "PowerAmount", 5m, 6m),
            (new ProtoKoSecretBase(), Upgraded<ProtoKoSecretBase>(), "PowerAmount", 6m, 8m),
            (new ProtoKoWindblumeFireworks(), Upgraded<ProtoKoWindblumeFireworks>(), "BombSize", 8m, 10m),
            (new ProtoKoDodoco(), Upgraded<ProtoKoDodoco>(), "PowerAmount", 5m, 7m),
            (new ProtoKoFindersKeepers(), Upgraded<ProtoKoFindersKeepers>(), "PowerAmount", 6m, 8m),
        };
        foreach (var (card, up, name, b, plus) in rows)
        {
            Assert.Equal((b, plus), (card.DynamicVars[name].BaseValue,
                                     up.DynamicVars[name].BaseValue));
        }
        // The starter does not move (pick 4 (a)).
        Assert.Equal(8m, new ProtoKoJumpyDumpty().DynamicVars["BombSize"].BaseValue);
    }
}
