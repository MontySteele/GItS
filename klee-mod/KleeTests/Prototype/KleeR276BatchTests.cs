using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// R276 (`review/ruled/klee-review-2026-09-23.md` pick 1): R271 sec.7's Mines
/// batch and slice two, built together -- Hair Trigger, Explosive Frags, Where
/// Did I Put It? and Big Bounce (Nova Burst; cut by the Klee status package's
/// sec.5, 2026-10-01, with its pins).
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="PoolPassThreeTests"/>' terms. Hair Trigger's rule is pure and is
/// run against real piles. A Mine going off, a bounce and a look at the draw
/// pile need a live combat, so those are pinned off the compiled methods and
/// say so. The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_klee_overhaul_rules.py</c>, its R276 block.
///
/// NO NUMBER HERE IS QUOTABLE (R215 B): every one is a starting value.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeR276BatchTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- Hair Trigger ----------------------------------------------------

    [Fact]
    public void Hair_trigger_makes_every_bomb_on_the_enemy_a_mine()
    {
        // REAL. "Your Bombs on this enemy become a Mine." Every charge keeps
        // its size and its place in the order; another enemy's pile and
        // another Klee's pile on the same enemy are untouched (R205).
        var klee = Seat.Klee();
        var other = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);

        var mine = ProtoBombs.Place(a, klee.Creature,
                                    new ProtoBombs.Charge(6),
                                    new ProtoBombs.Charge(4, PayloadMineAll: 3));
        var theirs = ProtoBombs.Place(a, other.Creature, new ProtoBombs.Charge(5));
        var elsewhere = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(7));

        ProtoBombPower.MineAllOn(a, klee.Creature);

        Assert.Equal(new[] { 6, 4 }, mine.Charges.Select(c => c.Size));
        Assert.All(mine.Charges, c => Assert.True(c.IsMine));
        Assert.Equal(3, mine.Charges.Last().PayloadMineAll);
        Assert.All(theirs.Charges, c => Assert.False(c.IsMine));
        Assert.All(elsewhere.Charges, c => Assert.False(c.IsMine));
    }

    [Fact]
    public void Hair_trigger_is_a_free_common_that_aims_and_draws()
    {
        // Seat round 2026-09-23: 0 Energy and a card (2 upgraded).
        var card = new ProtoKoHairTrigger();
        Assert.Equal(CardRarity.Common, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.StartsWith(
            "Your [gold]Bombs[/gold] on the enemy become [gold]Mines[/gold]. Draw ",
            Face(card));
        Assert.Contains(Il.Calls(Il.Method("ProtoKoHairTrigger", "OnUpgrade")),
                        c => c.Contains("UpgradeValueBy"));
        Assert.Contains("ProtoBombPower.MineAllOn",
                        Il.Calls(Il.Method("ProtoKoHairTrigger", "OnPlay")));
    }

    // ---- Explosive Frags -------------------------------------------------

    [Fact]
    public void Explosive_frags_is_read_where_a_charge_goes_off_after_its_hit()
    {
        // STRUCTURAL: an explosion needs a live combat. The rule's site is the
        // ONE place a charge goes off, so any Mine -- the enemy's attack or a
        // card's Set off -- reaches it, and it is read AFTER the hit.
        var explode = Il.CallSequence(Il.Method("ProtoBombPower", "Explode"))
            .ToList();
        var hit = explode.FindIndex(c => c == "ElementalHit.DealWithoutDealerMods");
        var frags = explode.FindIndex(c => c == "MineFragsPower.OnMineWentOff");
        Assert.True(hit >= 0 && frags > hit);

        var pay = Il.Calls(Il.Method("MineFragsPower", "OnMineWentOff"));
        Assert.Contains(pay, c => c.StartsWith("PowerCmd.Apply"));
    }

    [Fact]
    public void Explosive_frags_prints_two_and_upgrades_to_three()
    {
        var card = new ProtoKoExplosiveFrags();
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(2m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(3m, Upgraded<ProtoKoExplosiveFrags>()
                             .DynamicVars["PowerAmount"].BaseValue);
        Assert.Contains("Whenever a [gold]Mine[/gold] goes off", Face(card));
        // The IL reader names the call and not its generic argument, so the
        // pin is the apply itself; the power is the one `MineFragsPower`
        // class the arm has for the rule.
        Assert.Contains(Il.Calls(Il.Method("ProtoKoExplosiveFrags", "OnPlay")),
                        c => c.StartsWith("PowerCmd.Apply"));
    }

    // ---- Where Did I Put It? ---------------------------------------------

    [Fact]
    public void A_set_off_card_is_one_whose_body_prints_a_set_off()
    {
        // The mark the filter reads, derived by the codegen from the row's own
        // `set_off` op, anywhere in its body (Perfect Timing's lives in a
        // conditional). A placer is not one.
        Assert.IsAssignableFrom<ISetOffCard>(new ProtoKoKapow());
        Assert.IsAssignableFrom<ISetOffCard>(new ProtoKoCountdown());
        Assert.IsAssignableFrom<ISetOffCard>(new ProtoKoPerfectTiming());
        Assert.False(new ProtoKoPop() is ISetOffCard);
        Assert.False(new ProtoKoHairTrigger() is ISetOffCard);
    }

    // Where Did I Put It?'s pin left with the row (Klee final pass,
    // 2026-10-02: cut). `ScryTake`'s Set off filter stays registered
    // (BACKLOG).

    // ---- the pool --------------------------------------------------------

    [Fact]
    public void The_four_are_offered_and_the_five_cuts_are_gone()
    {
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"))
            .ToList();
        foreach (var name in new[]
                 {
                     "ProtoKoHairTrigger", "ProtoKoExplosiveFrags",
                     // Where Did I Put It? cut, Cover Your Ears! in its slot
                     // (Klee final pass, 2026-10-02).
                     "ProtoKoCoverYourEars",
                 })
        {
            Assert.Contains(slice, c => c.Contains(name));
        }
        foreach (var name in new[]
                 {
                     "ProtoKoLongFuse", "ProtoKoExplosivesWorkshop",
                     "ProtoKoSugarRush", "ProtoKoKindling",
                     "ProtoKoCatalyticConverter", "ProtoKoWhereDidIPutIt",
                 })
        {
            Assert.DoesNotContain(slice, c => c.Contains(name));
        }
    }
}
