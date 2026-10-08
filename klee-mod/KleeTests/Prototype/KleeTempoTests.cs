using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE TEMPO PAPER (2026-10-07, ruled,
/// review/active/klee-tempo-paper-2026-10-07.md sec.3). [USER]: "I
/// personally found Blast Shield and Kitchen Alchemy quite useful in my runs,
/// so I'm not sure I buy that they should go. Otherwise agreed." Five out,
/// five in, 78 and 25 / 32 / 21 held (<see cref="PoolCountTests"/>). Sim
/// twin: <c>tier0/tests/test_klee_tempo.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeTempoTests
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

    private static IReadOnlyCollection<string> Play(string type) =>
        Il.Calls(Il.Method(type, "OnPlay"));

    private static List<string> SliceTypes() =>
        Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    [Fact]
    public void Five_out_five_in_between_the_package_and_the_companions()
    {
        var slice = SliceTypes();
        Assert.Equal(78, slice.Count);
        Assert.Equal(new[] { "ProtoKoSimmer", "ProtoKoTasteTest",
                             "ProtoKoTinkering", "ProtoKoDodocoTag",
                             "ProtoKoExplosiveSpark" },
                     slice.Skip(70).Take(5).ToArray());
        foreach (var gone in new[] { "ItWasntMe", "SorryJean", "Grounded",
                                     "SitTight", "PatienceKlee" })
        {
            Assert.DoesNotContain(slice, c => c == "ProtoKo" + gone);
            Assert.Null(typeof(ProtoKoPop).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated.ProtoKo" + gone));
        }
    }

    [Fact]
    public void The_five_have_the_papers_types_costs_and_rarities()
    {
        var shapes = new (CardModel Card, CardType Type, int Cost, CardRarity Rarity)[]
        {
            (new ProtoKoSimmer(), CardType.Attack, 1, CardRarity.Common),
            (new ProtoKoTasteTest(), CardType.Attack, 2, CardRarity.Uncommon),
            (new ProtoKoTinkering(), CardType.Skill, 0, CardRarity.Uncommon),
            (new ProtoKoDodocoTag(), CardType.Attack, 1, CardRarity.Uncommon),
            (new ProtoKoExplosiveSpark(), CardType.Attack, 0, CardRarity.Common),
        };
        foreach (var (card, type, cost, rarity) in shapes)
        {
            Assert.Equal(type, card.Type);
            Assert.Equal(cost, card.EnergyCost.Canonical);
            Assert.Equal(rarity, card.Rarity);
        }
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoSimmer().TargetType);
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoTasteTest().TargetType);
        Assert.Equal(1, new ProtoKoExplosiveSpark().PrintedSparkPrice);
    }

    [Fact]
    public void The_papers_numbers_and_their_upgrades()
    {
        Assert.Equal((4m, 6m), (new ProtoKoSimmer().DynamicVars.Damage.BaseValue,
                                Upgraded<ProtoKoSimmer>().DynamicVars.Damage.BaseValue));
        Assert.Equal((2m, 1m), (new ProtoKoTasteTest().DynamicVars["Stash"].BaseValue,
                                Upgraded<ProtoKoTasteTest>().DynamicVars["Stash"].BaseValue));
        Assert.Equal((2m, 3m), (new ProtoKoTinkering().DynamicVars["Sparks"].BaseValue,
                                Upgraded<ProtoKoTinkering>().DynamicVars["Sparks"].BaseValue));
        Assert.Equal((7m, 10m), (new ProtoKoDodocoTag().DynamicVars.Damage.BaseValue,
                                 Upgraded<ProtoKoDodocoTag>().DynamicVars.Damage.BaseValue));
        Assert.Equal((5m, 7m), (new ProtoKoDodocoTag().DynamicVars.Block.BaseValue,
                                Upgraded<ProtoKoDodocoTag>().DynamicVars.Block.BaseValue));
        Assert.Equal((12m, 16m), (new ProtoKoExplosiveSpark().DynamicVars.Damage.BaseValue,
                                  Upgraded<ProtoKoExplosiveSpark>().DynamicVars.Damage.BaseValue));
    }

    [Fact]
    public void The_faces_print_the_rows()
    {
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Pyro[/gold] damage, plus half your largest "
          + "[gold]Bomb[/gold]'s size. It does not go off. Add a [gold]Dazed[/gold] "
          + "into your [gold]Discard Pile[/gold].",
            Face(new ProtoKoSimmer()));
        Assert.Equal(
            "Deal [gold]Pyro[/gold] damage equal to all your [gold]Bombs[/gold] on "
          + "the enemy. They do not go off. Add {Stash:diff()} "
          + "[gold]Confiscated[/gold] into your [gold]Discard Pile[/gold].",
            Face(new ProtoKoTasteTest()));
        Assert.Equal(
            "Gain {Sparks:diff()} [gold]Sparks[/gold]. Add a [gold]Confiscated[/gold] "
          + "into your [gold]Discard Pile[/gold].",
            Face(new ProtoKoTinkering()));
        Assert.Equal("Deal {Damage:diff()} [gold]Pyro[/gold] damage.",
                     Face(new ProtoKoExplosiveSpark()));
    }

    [Fact]
    public void Simmer_reads_half_the_largest_bomb_and_sets_nothing_off()
    {
        // REAL. The read is the board's largest charge of HERS, halved and
        // rounded down; another Klee's pile is not read.
        var klee = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);
        var other = Seat.Klee().Creature;
        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(6));
        ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(21));
        ProtoBombs.Place(b, other, new ProtoBombs.Charge(40));
        Assert.Equal(14m, ProtoBombPower.BombReadDamage(
            a, klee.Creature, 4m, ProtoBombPower.BombRead.LargestHalf));
        Assert.Equal(4m, ProtoBombPower.BombReadDamage(
            a, Seat.Klee().Creature, 4m, ProtoBombPower.BombRead.LargestHalf));

        var play = Play("ProtoKoSimmer");
        Assert.Contains("ProtoBombPower.DealFromBombs", play);
        Assert.DoesNotContain(play, c => c.Contains("SetOff"));
    }

    [Fact]
    public void Taste_test_reads_every_charge_on_the_target_mines_included()
    {
        var klee = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);
        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(12),
                         new ProtoBombs.Charge(5, IsMine: true));
        ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(30));
        Assert.Equal(17m, ProtoBombPower.BombReadDamage(
            a, klee.Creature, 0m, ProtoBombPower.BombRead.TargetTotal));
        Assert.Equal(0m, ProtoBombPower.BombReadDamage(
            Seat.Klee(200).Creature, klee.Creature, 0m,
            ProtoBombPower.BombRead.TargetTotal));

        var play = Play("ProtoKoTasteTest");
        Assert.Contains("ProtoBombPower.DealFromBombs", play);
        Assert.DoesNotContain(play, c => c.Contains("SetOff"));
    }

    [Fact]
    public void The_hit_is_the_cards_own_attack()
    {
        // STRUCTURAL: the read lands through the same `DealCardDamage` a Set
        // off card's own hit takes -- `DamageCmd.Attack` from the card, so
        // Pyro, Strength and Vulnerable land as on any other Attack of hers.
        Assert.Contains("ProtoBombPower.DealCardDamage",
                        Il.Calls(Il.Method("ProtoBombPower", "DealFromBombs")));
    }
}
