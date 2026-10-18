using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The damage previews pass (2026-10-13). [USER]: "Are there any other cards,
/// in any pool, that don't show how much damage they actually do when
/// accounting for conditional modifiers?" Display only: each card gains an
/// in-combat "(Deals N damage)" line over a var nothing in play reads. The
/// number itself needs a live combat (the headless boundary,
/// <c>KleeTests/README.md</c>), so these pin the wiring and the pure
/// arithmetic each var folds through the game's hooks.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class DamagePreviews20261013Tests
{
    private static string Face(object model) =>
        ((ILocalizationProvider)model).Localization!
            .Single(l => l.Item1 == "description").Item2;

    private static void Line(CardModel card, string token)
    {
        Assert.EndsWith("{InCombat:\n(Deals {" + token + ":diff()} damage)|}",
                        Face(card));
    }

    [Fact]
    public void Each_card_prints_its_live_total_over_its_own_var()
    {
        var finale = new ProtoKoFireworksFinale();
        var shoal = new ProtoKkShoalOfSpears();
        var bravura = new ProtoFsBravura();
        foreach (var card in new CardModel[] { finale, shoal, bravura })
        {
            Line(card, HitsTotalDamageVar.Token);
            Assert.Contains(card.DynamicVars.Values,
                            v => v is HitsTotalDamageVar);
        }
        var simmer = new ProtoKoSimmer();
        var taste = new ProtoKoTasteTest();
        Line(simmer, BombReadDamageVar.Token);
        Line(taste, BombReadDamageVar.Token);
        Assert.Equal(ProtoBombPower.BombRead.Largest,
                     simmer.DynamicVars.Values.OfType<BombReadDamageVar>()
                         .Single().Read);
        Assert.Equal(ProtoBombPower.BombRead.TargetTotalDouble,
                     taste.DynamicVars.Values.OfType<BombReadDamageVar>()
                         .Single().Read);

        var team = new ProtoKoTeamEffort();
        Line(team, CompanionBonusDamageVar.Token);
        Assert.Equal(6, team.DynamicVars.Values
            .OfType<CompanionBonusDamageVar>().Single().Bonus);

        var pressure = new ProtoKkDrowningPressure();
        Line(pressure, DebuffsAfterDamageVar.Token);
        Assert.Contains(pressure.DynamicVars.Values,
                        v => v is DebuffsAfterDamageVar);

        // Noelle already had the calculated var; only the line was missing.
        Line(new ProtoMcNoelleSweepingTime(), "CalculatedDamage");

        var boom = new ProtoKoBigBaddaBoom();
        Assert.EndsWith("{InCombat:\n(Then deals {BombEcho:diff()} damage)|}",
                        Face(boom));
        Assert.Contains(boom.DynamicVars.Values,
                        v => v is SetOffEchoDamageVar);

        var bigOne = new ProtoKoTheBigOne();
        Assert.EndsWith("{InCombat:\n([gold]Bombs[/gold]: {SetOffBombs:diff()} "
                        + "damage)|}", Face(bigOne));
        Assert.Equal(4, bigOne.DynamicVars.Values.OfType<SetOffBombsVar>()
                             .Single().Multiplier);
    }

    [Fact]
    public void A_counted_hit_totals_one_folded_hit_per_hit()
    {
        // Each hit truncates on its own: 5 x 0.75 Weak = 3.75 lands 3 a hit.
        Assert.Equal(9m, DamagePreview.HitsTotal(3.75m, 3));
        Assert.Equal(21m, DamagePreview.HitsTotal(7m, 3));
        Assert.Equal(0m, DamagePreview.HitsTotal(7m, 0));
    }

    [Fact]
    public void The_big_ones_line_is_the_badge_under_its_own_multiplier()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(3));

        Assert.Equal(8, DamagePreview.SetOffOn(enemy.Creature, klee.Creature));
        Assert.Equal(32, DamagePreview.SetOffOn(enemy.Creature, klee.Creature, 4));
        Assert.Equal(pile.PredictedSetOffDamage(), pile.PredictedSetOffDamage(1));

        // A badge doubles, the x4 multiplies, then the Vulnerable: as SetOff.
        klee.WithPower<BoomBadgePower>(1);
        enemy.WithPower<VulnerablePower>(1);
        Assert.Equal(60 + 36,
                     DamagePreview.SetOffOn(enemy.Creature, klee.Creature, 4));
        Assert.Equal(0, DamagePreview.SetOffOn(null, klee.Creature, 4));
    }

    [Fact]
    public void Big_badda_booms_second_hit_takes_the_vulnerable_back_out()
    {
        // The ledger's own arithmetic (`EchoBase`): the card's hit then pays
        // the Vulnerable once, so it lands what the Bombs dealt.
        Assert.Equal(12m, SetOffEchoDamageVar.EchoBase(12, false));
        Assert.Equal(KleeOverhaulLedger.EchoBase(18, true),
                     SetOffEchoDamageVar.EchoBase(18, true));
        Assert.Equal(0m, SetOffEchoDamageVar.EchoBase(0, true));
    }

    [Fact]
    public void Simmer_and_taste_test_read_the_bombs_the_play_reads()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(3));
        Assert.Equal(16m, ProtoBombPower.BombReadDamage(
            enemy.Creature, klee.Creature, 0m,
            ProtoBombPower.BombRead.TargetTotalDouble));
        Assert.Equal(0m, ProtoBombPower.BombReadDamage(
            null, klee.Creature, 0m, ProtoBombPower.BombRead.TargetTotalDouble));
    }

    [Fact]
    public void Drowning_pressure_counts_its_own_weak_and_vulnerable()
    {
        Assert.Equal((2, true), DamagePreview.AfterOwnDebuffs(0, 0));
        Assert.Equal((5, true), DamagePreview.AfterOwnDebuffs(3, 0));
        // Artifact negates the Weak first, then the Vulnerable.
        Assert.Equal((4, true), DamagePreview.AfterOwnDebuffs(3, 1));
        Assert.Equal((3, false), DamagePreview.AfterOwnDebuffs(3, 2));
        Assert.Equal(1.5m, ReactionConstants.VulnerableTakenMult);
    }

    [Fact]
    public void Team_efforts_bonus_joins_the_hit_only_after_a_companion()
    {
        Assert.Equal(6m, CompanionBonusDamageVar.Raw(6m, 6, false));
        Assert.Equal(12m, CompanionBonusDamageVar.Raw(6m, 6, true));
        Assert.Equal(15m, CompanionBonusDamageVar.Raw(9m, 6, true));
    }
}
