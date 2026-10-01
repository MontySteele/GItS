using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA, ELEMENT IDENTITIES (<c>review/active/varka-element-identities-2026-10-01.md</c>,
/// picks 1 to 5 ruled at the defaults 2026-10-01, Violet Storm raised to 8
/// [11] and an Attack): Electro's discard-and-spend cards, Thundering Verdict
/// at X, Retaliating Tide, Wildfire Oath's one big hit, and the element-switch
/// warnings. Pinned the way <see cref="VarkaExpansionTests"/> pins the
/// expansion: arithmetic by value, live sites by their call graph. The sim
/// twin is <c>tier0/tests/test_varka_element_identities.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaElementIdentitiesTests : IDisposable
{
    public VarkaElementIdentitiesTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static VarkaOathLedger FreshLedger() =>
        VarkaOathLedger.For(Seat.Klee().Creature);

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    // ---- sec.3: Electro --------------------------------------------------------

    [Fact]
    public void Charged_lunge_is_an_electro_hit_and_a_draw()
    {
        var lunge = new ProtoVkChargedLunge();
        Assert.Equal(CardType.Attack, lunge.Type);
        Assert.Equal(CardRarity.Common, lunge.Rarity);
        Assert.Equal(1, lunge.EnergyCost.Canonical);
        Assert.Equal(6m, Var(lunge, "VkBase"));
        Assert.Equal(9m, Var(Upgraded<ProtoVkChargedLunge>(), "VkBase"));
        var play = Calls("ProtoVkChargedLunge", "OnPlay");
        Assert.Contains("VarkaCards.ElectroStrike", play);
        Assert.Contains("CardPileCmd.Draw", play);
        Assert.Contains("HitElement.Carry", Calls("VarkaCards", "ElementHit"));
    }

    [Fact]
    public void Short_circuit_is_concentrate_with_an_electro_rider()
    {
        var circuit = new ProtoVkShortCircuit();
        Assert.Equal(CardType.Skill, circuit.Type);
        Assert.Equal(CardRarity.Uncommon, circuit.Rarity);
        Assert.Equal(0, circuit.EnergyCost.Canonical);
        Assert.Equal(3m, Var(circuit, "Discards"));
        Assert.Equal(2m, Var(Upgraded<ProtoVkShortCircuit>(), "Discards"));
        var play = Il.CallSequence(Il.Method("ProtoVkShortCircuit", "OnPlay")).ToList();
        var pick = play.IndexOf("CardSelectCmd.FromHandForDiscard");
        var discard = play.IndexOf("CardCmd.Discard");
        var energy = play.IndexOf("PlayerCmd.GainEnergy");
        var apply = play.IndexOf("ElementalHit.ApplyOnly");
        Assert.True(pick >= 0 && discard > pick && energy > discard && apply > energy,
                    string.Join(", ", play));
    }

    [Fact]
    public void Chain_lightning_costs_one_less_per_discard_this_turn()
    {
        var chain = new ProtoVkChainLightning();
        Assert.Equal(2, chain.EnergyCost.Canonical);
        Assert.Equal(8m, Var(chain, "VkBase"));
        Assert.Equal(11m, Var(Upgraded<ProtoVkChainLightning>(), "VkBase"));
        Assert.Contains("VarkaCards.ElectroAll", Calls("ProtoVkChainLightning", "OnPlay"));
        // The discount reads MementoMori's count and prices only itself.
        Assert.Contains("KokomiResources.DiscardsThisTurn",
                        Calls("ProtoVkChainLightning", "TryModifyEnergyCostInCombat"));
        Assert.False(chain.TryModifyEnergyCostInCombat(new ProtoVkSquall(), 1m,
                                                      out var other));
        Assert.Equal(1m, other);
        // Out of combat no discard has happened: the printed 2.
        Assert.True(chain.TryModifyEnergyCostInCombat(chain, 2m, out var own));
        Assert.Equal(2m, own);
    }

    [Fact]
    public void Thundering_verdict_is_an_x_cost_that_hits_all_x_times()
    {
        var verdict = new ProtoVkThunderingVerdict();
        Assert.True(verdict.EnergyCost.CostsX);
        Assert.Equal(6m, Var(verdict, "VkBase"));
        Assert.Equal(1m, Var(verdict, "VkPer"));
        Assert.Equal(8m, Var(Upgraded<ProtoVkThunderingVerdict>(), "VkBase"));
        var body = Calls("VarkaCards", "ThunderingVerdict");
        Assert.Contains("CardModel.ResolveEnergyXValue", body);
        Assert.Contains("VarkaOath.Count", body);
    }

    [Fact]
    public void Violet_storm_discards_the_hand_then_hits_a_random_enemy_per_card()
    {
        var storm = new ProtoVkVioletStorm();
        Assert.Equal(CardType.Attack, storm.Type);
        Assert.Equal(CardRarity.Rare, storm.Rarity);
        Assert.Equal(1, storm.EnergyCost.Canonical);
        Assert.Equal(8m, Var(storm, "VkBase"));
        Assert.Equal(11m, Var(Upgraded<ProtoVkVioletStorm>(), "VkBase"));
        var body = Il.CallSequence(Il.Method("VarkaCards", "VioletStorm")).ToList();
        var discard = body.IndexOf("CardCmd.Discard");
        var hit = body.IndexOf("VarkaCards.ElementHit");
        Assert.True(discard >= 0 && hit > discard, string.Join(", ", body));
        Assert.Contains("Rng.NextItem", Calls("VarkaCards", "VioletStorm"));
    }

    [Fact]
    public void Dawn_patrol_exhausts()
    {
        // Sec.2: the rule's one existing Energy-for-free card gains Exhaust
        // (the expansion already printed it).
        Assert.Contains(CardKeyword.Exhaust, new ProtoVkDawnPatrol().Keywords);
    }

    // ---- sec.4: Retaliating Tide ------------------------------------------------

    [Fact]
    public void Retaliating_tide_deals_its_block_capped_at_hydro_oath()
    {
        Assert.Equal(4, RetaliatingTidePower.DamageFor(10, 4));
        Assert.Equal(3, RetaliatingTidePower.DamageFor(3, 7));
        Assert.Equal(0, RetaliatingTidePower.DamageFor(0, 5));
        Assert.Equal(0, RetaliatingTidePower.DamageFor(9, 0));
        var end = Calls("RetaliatingTidePower", "BeforeSideTurnEnd");
        Assert.Contains("ElementalHit.DealUnelemented", end);
        Assert.Contains("VarkaOath.Count", end);
        // The Aegis pays EARLY, so the Tide reads its Block.
        Assert.Contains("CreatureCmd.GainBlock",
                        Calls("OathboundAegisPower", "BeforeSideTurnEndEarly"));
        Assert.Contains(CardKeyword.Exhaust, new ProtoVkDawnPatrol().Keywords);
        Assert.Equal(CardRarity.Rare, new ProtoVkRetaliatingTide().Rarity);
    }

    // ---- sec.5: Wildfire Oath ---------------------------------------------------

    [Fact]
    public void Wildfire_is_the_pyro_oath_on_one_hit_while_pyro_is_current()
    {
        Assert.Equal(5, VarkaOath.WildfireBonus(Element.Pyro, 5, 1));
        Assert.Equal(10, VarkaOath.WildfireBonus(Element.Pyro, 5, 2));
        Assert.Equal(0, VarkaOath.WildfireBonus(Element.Hydro, 5, 1));
        Assert.Equal(0, VarkaOath.WildfireBonus(Element.Pyro, 5, 0));
        var ledger = FreshLedger();
        ledger.RollTo(2);
        Assert.True(ledger.TakeFirstAttack());
        Assert.False(ledger.TakeFirstAttack());
        ledger.RollTo(3);
        Assert.True(ledger.TakeFirstAttack());
        Assert.Contains("VarkaOathLedger.TakeFirstAttack", Calls("VarkaOath", "BeginPlay"));
        Assert.Contains("VarkaOathLedger.set_WildfireCard", Calls("VarkaOath", "EndPlay"));
        Assert.Contains("VarkaOathLedger.set_WildfireCard",
                        Calls("WildfireOathPower", "BeforeDamageReceived"));
        Assert.Contains("VarkaOath.WildfireBonus",
                        Calls("WildfireOathPower", "ModifyDamageAdditive"));
        // The Swirl payout no longer reads it.
        Assert.DoesNotContain("WildfireOathPower", string.Join(" ", Calls("VarkaOath", "Pay")));
    }

    // ---- sec.7 and the round's faces ----------------------------------------------

    [Fact]
    public void The_ledger_remembers_the_element_it_left_for_that_turn()
    {
        var ledger = FreshLedger();
        ledger.RollTo(1);
        ledger.SetCurrent(Element.Pyro);                    // none -> Pyro
        Assert.False(ledger.LeftThisTurn);
        ledger.SetCurrent(Element.Hydro);
        Assert.True(ledger.LeftThisTurn);
        Assert.Equal(Element.Pyro, ledger.LeftElement);
        ledger.RollTo(2);
        Assert.False(ledger.LeftThisTurn);
        Assert.Equal(typeof(PyroOathLeftPower),
                     OathBadge.WantedLeft(true, Element.Pyro, Element.Hydro));
        Assert.Null(OathBadge.WantedLeft(false, Element.Pyro, Element.Hydro));
        Assert.Null(OathBadge.WantedLeft(true, Element.Pyro, Element.Pyro));
        string Row(Type t, string key) =>
            ((OathLeftPower)RuntimeHelpers.GetUninitializedObject(t))
                .Localization!.First(r => r.Item1 == key).Item2;
        Assert.Equal("Cryo Oath (left)", Row(typeof(CryoOathLeftPower), "title"));
        Assert.Contains("is kept", Row(typeof(CryoOathLeftPower), "description"));
        Assert.Contains("OathBadge.SyncLeft", Calls("OathBadge", "Sync"));
    }

    [Theory]
    [InlineData("ProtoVkBlazingCharge", true)]
    [InlineData("ProtoVkChargedLunge", true)]
    [InlineData("ProtoVkShortCircuit", true)]
    [InlineData("ProtoVkTempestOfTheFourWinds", true)]
    [InlineData("ProtoVkAmberBaronBunny", true)]          // a Knight
    [InlineData("ProtoVkFavoniusDrill", false)]           // his current element
    [InlineData("ProtoVkCavalryCharge", false)]
    [InlineData("ProtoVkNoelleSteadfastMaid", false)]     // Geo
    [InlineData("ProtoVkSquall", false)]                  // Anemo
    public void A_card_that_switches_his_element_carries_the_switch_tip(
        string card, bool tipped)
    {
        var getter = Il.Calls(Il.Method(card, "get_ExtraHoverTips"));
        Assert.Equal(tipped, getter.Contains("ArmKeywordTips.ForElementSwitch"));
    }

    [Fact]
    public void The_switch_tip_prints_only_when_it_would_switch()
    {
        Assert.Contains("VarkaOath.WouldSwitchTo",
                        Calls("ArmKeywordTips", "ForElementSwitch"));
        // Out of a fight (no owner) it says nothing.
        Assert.False(VarkaOath.WouldSwitchTo(null, Element.Pyro));
        Assert.False(VarkaOath.WouldSwitchTo(new ProtoVkBlazingCharge(), Element.Pyro));
        var none = ArmKeywordTips.ForElementSwitch(
            Enumerable.Empty<IHoverTip>(), new ProtoVkBlazingCharge(), Element.Pyro);
        Assert.Empty(none);
        var banner = Calls("VarkaOath", "WouldSwitchTo");
        Assert.Contains("VarkaRules.IsKnight", banner);
    }

    [Fact]
    public void Element_kinds_carry_no_anemo_of_their_own()
    {
        // The round: "Cavalry Charge is tagged Anemo but hits as the current
        // element". A kind's hit carries its own element.
        foreach (var card in new CardModel[]
                 {
                     new ProtoVkCavalryCharge(), new ProtoVkBlazingCharge(),
                     new ProtoVkChargedLunge(), new ProtoVkVioletStorm(),
                 })
        {
            Assert.Equal(Element.None, ((IElementalCard)card).Element);
        }
        // (Which "Applies" keyword each face carries is the codegen's, pinned
        // in tier0/tests/test_varka_element_identities.py: the keywords are
        // registered at runtime and read as None headless.)
        // Northwind Avatar has an Anemo hit of its own and keeps it.
        Assert.Equal(Element.Anemo, ((IElementalCard)new ProtoVkNorthwindAvatar()).Element);
    }
}
