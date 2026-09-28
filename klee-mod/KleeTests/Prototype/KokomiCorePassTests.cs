using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI CORE PASS (review/active/kokomi-core-pass-2026-09-27.md): eight
/// cards, no rule. Every pure read -- a card's numbers, its upgrade, a cost
/// seam, the Strength fold -- runs for real on a headless seat; anything that
/// awaits a command (a strike, a draw) needs a live combat, so its doors and
/// their ORDER are pinned off the compiled methods. Sim twin: the core-pass
/// tests in <c>tier0/tests/test_kokomi_plan.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiCorePassTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static System.Collections.Generic.List<string> Play(string type) =>
        Il.CallSequence(Il.Method(type, "OnPlay")).ToList();

    // ---- Song of Pearls: the empty-queue payoff ---------------------------

    [Fact]
    public void Song_of_pearls_reads_the_queue_before_the_drain_and_fires_after()
    {
        // "If no Plan waits" is the queue read just before ResolveAll empties
        // it, so a morning that carried a Plan out never also fires it.
        var calls = Il.CallSequence(
            Il.Method("ProtoBakeKuragePower", "AfterPlayerTurnStart")).ToList();
        var read = calls.FindIndex(c => c.Contains("KokomiPlan.PlansHeld"));
        var drain = calls.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        var strike = calls.FindIndex(c => c.Contains("SongOfPearlsPower.Strike"));
        Assert.True(read >= 0 && drain > read && strike > drain);
    }

    [Fact]
    public void Song_of_pearls_strikes_all_enemies_as_a_planned_hit()
    {
        // Hydro, unpowered, her Strength folded in by the same door a Plan's
        // damage takes -- and it is off the plan bus now.
        var calls = Il.CallSequence(Il.Method("SongOfPearlsPower", "Strike"))
            .ToList();
        var fold = calls.FindIndex(c => c.Contains("KokomiPlan.Hers"));
        var deal = calls.FindIndex(c => c.Contains("ElementalHit.Deal"));
        Assert.True(fold >= 0 && deal > fold);
        Assert.Contains(calls, c => c.Contains("get_HittableEnemies"));
        Assert.False(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(SongOfPearlsPower)));
    }

    [Fact]
    public void Song_of_pearls_counts_her_strength_and_stacks()
    {
        var seat = Seat.Kokomi().WithPower<StrengthPower>(2);
        Assert.Equal(6, KokomiPlan.Hers(seat.Creature, null, 4));
        Assert.Equal(4, KokomiPlan.Hers(Seat.Kokomi().Creature, null, 4));
        // Two copies are one power at 8: the amount stacks.
        Assert.Equal(PowerStackType.Counter, new SongOfPearlsPower().StackType);
        // An empty queue is what the read sees on a fresh seat.
        Assert.Equal(0, KokomiPlan.PlansHeld(Seat.Kokomi().Creature));
    }

    [Fact]
    public void Song_of_pearls_card_is_four_and_six_upgraded()
    {
        var card = new ProtoKkSongOfPearls();
        Assert.Equal(4m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(6m, Upgraded<ProtoKkSongOfPearls>()
            .DynamicVars["PowerAmount"].BaseValue);
        Assert.Contains("if no [gold]Plan[/gold] waits", Face(card));
        Assert.Contains("PowerCmd.Apply<SongOfPearlsPower>",
                        string.Join(" ", Play("ProtoKkSongOfPearls")));
    }

    // ---- Treatise: the now-line payoff ------------------------------------

    [Fact]
    public void Treatise_draws_on_a_face_up_plan_card_and_not_on_a_write()
    {
        // "Normally" = not written on the Bake-Kurage. The write test comes
        // BEFORE the claim, so a written card does not spend the turn's draw.
        var calls = Il.CallSequence(Il.Method("TreatisePower", "AfterCardPlayed"))
            .ToList();
        var pet = calls.FindIndex(c => c.Contains("KokomiPlan.PlayedOnPet"));
        var claim = calls.FindIndex(
            c => c.Contains("KokomiOverhaulLedger.ClaimOncePerTurn"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(pet >= 0 && claim > pet && draw > claim);
        Assert.False(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(TreatisePower)));
        Assert.Equal(PowerStackType.Counter, new TreatisePower().StackType);
    }

    [Fact]
    public void Treatise_card_upgrades_to_innate()
    {
        var card = new ProtoKkTreatise();
        Assert.DoesNotContain(CardKeyword.Innate, card.Keywords);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKkTreatise>().Keywords);
        Assert.Equal(
            "Once per turn, when you play a card with a [gold]Plan[/gold] line "
          + "normally, draw 1 card.", Face(card));
    }

    // ---- Chain of Command: the Plan buys a free Companion -----------------

    [Fact]
    public void Chain_of_commands_plan_is_the_first_companion_free()
    {
        var card = new ProtoKkChainOfCommand();
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.FirstCompanionFree, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.Self, clause.Aim);
        Assert.Equal(3m, card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(4m, Upgraded<ProtoKkChainOfCommand>()
            .DynamicVars.ExtraDamage.BaseValue);
        Assert.EndsWith("Next turn, the first Companion card you play costs 0.",
                        Face(card));
        Assert.Contains(
            Il.CallSequence(Il.Method("KokomiPlan", "ResolveOne")),
            c => c.Contains("KokomiOverhaulKit.FirstCompanionFree"));
    }

    [Fact]
    public void The_free_companion_zeroes_a_companion_and_nothing_else()
    {
        var seat = Seat.Kokomi().WithPower<FirstCompanionFreePower>(1);
        var power = seat.Creature.Powers.OfType<FirstCompanionFreePower>()
            .Single();
        var friend = Owned<ProtoMcDionaIcyPaws>(seat);          // a Companion
        Assert.True(power.TryModifyEnergyCostInCombat(friend, 2m, out var cost));
        Assert.Equal(0m, cost);
        var own = Owned<ProtoKkRally>(seat);                    // her own card
        Assert.False(power.TryModifyEnergyCostInCombat(own, 1m, out _));
        Assert.False(power.TryModifyEnergyCostInCombat(friend, 0m, out _));

        var spent = Il.Calls(Il.Method("FirstCompanionFreePower",
                                       "AfterCardPlayed"));
        Assert.Contains(spent, c => c.Contains("get_IsAutoPlay"));
        Assert.Contains(spent, c => c.Contains("PowerCmd.Remove"));
        Assert.Contains(Il.Calls(Il.Method("FirstCompanionFreePower",
                                           "AfterSideTurnEnd")),
                        c => c.Contains("PowerCmd.Remove"));
    }

    // ---- the five rewritten faces -----------------------------------------

    [Fact]
    public void Ambush_applies_vulnerable_now_and_plans_twelve()
    {
        var card = new ProtoKkAmbush();
        Assert.Equal("Apply 2 [gold]Vulnerable[/gold].\n[gold]Plan[/gold]: "
                   + "Deal {PlanDamage:diff()} damage.", Face(card));
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Damage, 12), (clause.Kind, clause.Amount));
        Assert.Equal(15, Assert.Single(
            Upgraded<ProtoKkAmbush>().PlanClauses).Amount);
        Assert.Contains(Play("ProtoKkAmbush"), c => c.Contains("VulnerablePower"));
        Assert.DoesNotContain(Play("ProtoKkAmbush"),
                              c => c.Contains("GainBlock"));
    }

    [Fact]
    public void Cleansing_wave_cleanses_and_draws_now_and_plans_block()
    {
        var card = new ProtoKkCleansingWave();
        Assert.Equal(1m, card.DynamicVars.Cards.BaseValue);
        Assert.Equal(10m, card.DynamicVars["PlanBlock"].BaseValue);
        var up = Upgraded<ProtoKkCleansingWave>();
        Assert.Equal(1m, up.DynamicVars.Cards.BaseValue);
        Assert.Equal(13m, up.DynamicVars["PlanBlock"].BaseValue);
        var play = Play("ProtoKkCleansingWave");
        Assert.Contains(play, c => c.Contains("KokomiOverhaulKit.RemoveOneDebuff"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.Draw"));
        Assert.DoesNotContain(play, c => c.Contains("GainBlock"));
    }

    [Fact]
    public void Ripple_draws_now_and_plans_one_energy()
    {
        var card = new ProtoKkRipple();
        Assert.Equal(1m, card.DynamicVars.Cards.BaseValue);
        Assert.Equal(2m, Upgraded<ProtoKkRipple>().DynamicVars.Cards.BaseValue);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Energy, 1), (clause.Kind, clause.Amount));
    }

    [Fact]
    public void Feigned_retreat_draws_two_discards_one_and_upgrades_its_plan()
    {
        var card = new ProtoKkFeignedRetreat();
        Assert.StartsWith("Draw 2 cards. Discard 1 card.", Face(card));
        Assert.Equal(2m, card.DynamicVars.Cards.BaseValue);
        var up = Assert.Single(Upgraded<ProtoKkFeignedRetreat>().PlanClauses);
        Assert.Equal((12, 18), (up.Amount, up.Alt));
        var play = Play("ProtoKkFeignedRetreat");
        var draw = play.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        var discard = play.FindIndex(c => c.Contains("CardCmd.Discard"));
        Assert.True(draw >= 0 && discard > draw);
    }

    [Fact]
    public void Second_wave_deals_five_hydro_now_and_seven_upgraded()
    {
        var card = new ProtoKkSecondWave();
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(5m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(7m, Upgraded<ProtoKkSecondWave>()
            .DynamicVars.Damage.BaseValue);
        var elemental = Assert.IsAssignableFrom<IElementalCard>(card);
        Assert.Equal(Element.Hydro, elemental.Element);
        Assert.Equal(KokomiPlan.Kind.NextPlanExtraCarryOut,
                     Assert.Single(card.PlanClauses).Kind);
    }
}
