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

    // A PLAN STAYS OPEN (2026-10-01): a two-line row's now-line is its own
    // method, `PlayNowLine`, which `OnPlay` calls; a play is both bodies.
    private static System.Collections.Generic.List<string> Play(string type)
    {
        var seq = Il.CallSequence(Il.Method(type, "OnPlay")).ToList();
        var nowLine = typeof(KokomiPlan).Assembly.GetTypes()
            .FirstOrDefault(t => t.Name == type)?.GetMethod("PlayNowLine");
        if (nowLine != null) seq.AddRange(Il.CallSequence(nowLine));
        return seq;
    }

    // ---- Song of Pearls: the empty-queue payoff ---------------------------

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

    // ---- the five rewritten faces -----------------------------------------

    [Fact]
    public void Ambush_applies_vulnerable_now_and_plans_twelve()
    {
        var card = new ProtoKkAmbush();
        Assert.Equal("Apply 2 [gold]Vulnerable[/gold].\nOr [gold]plan[/gold]: "
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
    public void Second_wave_deals_seven_hydro_now_and_nine_upgraded()
    {
        // The Casket pass (2026-09-28): Uncommon, and 7 now (5 before).
        var card = new ProtoKkSecondWave();
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(7m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded<ProtoKkSecondWave>()
            .DynamicVars.Damage.BaseValue);
        var elemental = Assert.IsAssignableFrom<IElementalCard>(card);
        Assert.Equal(Element.Hydro, elemental.Element);
        Assert.Equal(KokomiPlan.Kind.NextPlanExtraCarryOut,
                     Assert.Single(card.PlanClauses).Kind);
    }
}
