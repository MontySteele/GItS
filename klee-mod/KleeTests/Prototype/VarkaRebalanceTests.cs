using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Entities.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA, THE REBALANCE (<c>review/active/varka-rebalance-2026-10-03.md</c>,
/// every pick ruled 2026-10-03, starters at the sim's variant A) and the Varka
/// part of the AoE trim (<c>review/active/aoe-trim-2026-10-03.md</c> sec.4).
/// Arithmetic by value, live sites by their call graph. The sim twin is
/// <c>tier0/tests/test_varka_rebalance_sim.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaRebalanceTests : IDisposable
{
    public VarkaRebalanceTests()
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

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    // ---- sec.5: four different starter Knights --------------------------------

    [Fact]
    public void The_four_starters_numbers()
    {
        var amber = new ProtoVkAmberFieryRain();
        Assert.Equal(7m, Var(amber, "CalculationBase"));
        Assert.Equal(5m, Var(amber, "Block"));
        Assert.Equal(10m, Var(Upgraded<ProtoVkAmberFieryRain>(), "CalculationBase"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkAmberFieryRain>(), "Block"));
        Assert.Contains("DamageCmd.Attack", Calls("ProtoVkAmberFieryRain", "OnPlay"));

        Assert.Equal(6m, Var(new ProtoVkBarbaraMelodyLoop(), "CalculationBase"));
        Assert.Equal(3m, Var(new ProtoVkBarbaraMelodyLoop(), "BlockNextTurn"));
        Assert.Equal(4m, Var(Upgraded<ProtoVkBarbaraMelodyLoop>(), "BlockNextTurn"));

        Assert.Equal(6m, Var(new ProtoVkLisaLightningRose(), "CalculationBase"));
        Assert.Equal(8m, Var(Upgraded<ProtoVkLisaLightningRose>(), "CalculationBase"));
        Assert.Equal(2m, Var(Upgraded<ProtoVkLisaLightningRose>(), "Cards"));
        Assert.Contains("CardPileCmd.Draw", Calls("ProtoVkLisaLightningRose", "OnPlay"));

        Assert.Equal(5m, Var(new ProtoVkKaeyaGlacialWaltz(), "CalculationBase"));
        Assert.Equal(7m, Var(Upgraded<ProtoVkKaeyaGlacialWaltz>(), "CalculationBase"));
        Assert.Contains("PowerCmd.Apply", Calls("ProtoVkKaeyaGlacialWaltz", "OnPlay"));
    }

    // ---- sec.3: Hydro scales ------------------------------------------------

    [Fact]
    public void Gleeful_songs_pays_per_reacting_enemy()
    {
        var songs = new ProtoVkBarbaraShowBegin();
        Assert.Equal(TargetType.AllEnemies, songs.TargetType);
        Assert.Equal(4m, Var(songs, "VkBase"));
        Assert.Equal(3m, Var(songs, "VkPer"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkBarbaraShowBegin>(), "VkBase"));
        Assert.Equal(4m, Var(Upgraded<ProtoVkBarbaraShowBegin>(), "VkPer"));
        var body = Calls("VarkaCards", "GleefulSongs");
        Assert.Contains("ElementalHit.ApplyOnly", body);
        Assert.Contains("ReactionEffects.get_TotalResolved", body);
        Assert.Contains("VarkaCards.GainCardBlock", body);
    }

    [Fact]
    public void Rippling_guard_counts_the_other_plays_this_turn()
    {
        var guard = new ProtoVkRipplingGuard();
        Assert.Equal(CardRarity.Common, guard.Rarity);
        Assert.Equal(3m, Var(guard, "VkBase"));
        Assert.Equal(2m, Var(guard, "VkPer"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkRipplingGuard>(), "VkPer"));
        Assert.Contains("VarkaOathLedger.get_PlaysThisTurn",
                        Calls("VarkaCards", "RipplingGuard"));
        Assert.Contains("VarkaOathLedger.NotePlay", Calls("VarkaOath", "BeginPlay"));
        var ledger = VarkaOathLedger.For(Seat.Varka().Creature);
        ledger.NotePlay();
        ledger.NotePlay();
        Assert.Equal(2, ledger.PlaysThisTurn);
    }

    [Fact]
    public void Whisper_of_water_echoes_for_two_turns()
    {
        Assert.Equal(2, VarkaLaw.EchoBlockTurns);
        Assert.Equal(4m, Var(new ProtoVkBarbaraWhisperOfWater(), "VkAmount"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkBarbaraWhisperOfWater>(), "VkAmount"));
        var ledger = VarkaOathLedger.For(Seat.Varka().Creature);
        ledger.AddEchoBlock(4, VarkaLaw.EchoBlockTurns);
        Assert.Equal(4, ledger.TakeEchoBlock());
        Assert.Equal(4, ledger.TakeEchoBlock());
        Assert.Equal(0, ledger.TakeEchoBlock());
        Assert.Equal(0, ledger.EchoEntries);
        Assert.Contains("VarkaOathLedger.TakeEchoBlock", Calls("VarkaOath", "TurnStart"));
        Assert.Contains("VarkaCards.EchoBlock", Calls("ProtoVkBarbaraWhisperOfWater", "OnPlay"));
    }

    // ---- sec.4: payoffs that borrow -----------------------------------------

    [Fact]
    public void Kindled_edge_hits_again_on_a_reaction()
    {
        var edge = new ProtoVkKindledEdge();
        Assert.Equal(CardType.Attack, edge.Type);
        Assert.Equal(7m, Var(edge, "VkBase"));
        Assert.Equal(10m, Var(Upgraded<ProtoVkKindledEdge>(), "VkBase"));
        var body = Calls("VarkaCards", "KindledEdge");
        Assert.Contains("VarkaCards.ElementHit", body);
        Assert.Contains("ReactionEffects.get_TotalResolved", body);
        Assert.Contains("DamageCmd.Attack", body);
    }

    [Fact]
    public void Storm_battery_is_cost_1_per_other_card_to_all()
    {
        var battery = new ProtoVkStormBattery();
        Assert.Equal(1, battery.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Uncommon, battery.Rarity);
        Assert.Equal(TargetType.AllEnemies, battery.TargetType);
        Assert.Equal(2m, Var(battery, "VkPer"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkStormBattery>(), "VkPer"));
        Assert.Contains("VarkaCards.ElementHit", Calls("VarkaCards", "StormBattery"));
    }

    [Fact]
    public void Frost_ward_weakens_each_aura_and_blocks_for_each()
    {
        var ward = new ProtoVkFrostWard();
        Assert.Equal(CardRarity.Common, ward.Rarity);
        Assert.Equal(3m, Var(ward, "VkAmount"));
        Assert.Equal(4m, Var(Upgraded<ProtoVkFrostWard>(), "VkAmount"));
        var body = Calls("VarkaCards", "FrostWard");
        Assert.Contains("AuraCmd.Find", body);
        Assert.Contains("PowerCmd.Apply", body);
        Assert.Contains("VarkaCards.GainCardBlock", body);
    }

    [Fact]
    public void The_replaced_cards_are_gone_from_the_pool()
    {
        var pool = Il.CallSequence(Il.Method("VarkaRoster", "Pool"))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();
        Assert.Equal(78, pool.Count);
        foreach (var name in new[] { "ProtoVkRipplingGuard", "ProtoVkKindledEdge",
                                     "ProtoVkStormBattery", "ProtoVkFrostWard" })
        {
            Assert.Contains($"ModelDb.Card<{name}>", pool);
        }
        foreach (var gone in new[] { "ProtoVkWindWall", "ProtoVkCavalryCharge",
                                     "ProtoVkGustWard", "ProtoVkFavoniusDrill" })
        {
            Assert.Null(typeof(ProtoVkKindledEdge).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + gone));
        }
    }

    // ---- sec.2: the Oath rule -----------------------------------------------

    [Fact]
    public void Absolute_zero_pays_cryo_oath_per_debuff_he_applies()
    {
        Assert.Equal(PowerStackType.Counter, new AbsoluteZeroPower().StackType);
        Assert.Equal(4, AbsoluteZeroPower.DamageFor(4, 1));
        Assert.Equal(8, AbsoluteZeroPower.DamageFor(4, 2));
        Assert.Equal(0, AbsoluteZeroPower.DamageFor(0, 1));
        var hook = Calls("AbsoluteZeroPower", "AfterPowerAmountChanged");
        Assert.Contains("SeasReproachPower.Pays", hook);
        Assert.Contains("ElementalHit.DealUnelemented", hook);
        // The Swirl no longer widens.
        Assert.DoesNotContain("Creature.HasPower", Calls("VarkaOath", "Pay"));
    }

    [Fact]
    public void Cycle_of_seasons_hits_one_random_enemy()
    {
        var cycle = Calls("CycleOfSeasonsPower", "OnElementChanged");
        Assert.Contains("Rng.NextItem", cycle);
        Assert.Single(cycle, c => c == "ElementalHit.DealUnelemented");
    }

    // ---- the starter ruling, 2026-10-03 -------------------------------------

    [Fact]
    public void Ascension_costs_2_and_retains_like_sovereign_blade()
    {
        // The Fang creates it with CombatState.CreateCard, which builds the
        // model's canonical keywords, so a generated copy retains too.
        var card = new ProtoVkFourWindsAscension();
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.Contains(CardKeyword.Retain, card.Keywords);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Equal(10m, Var(card, "Damage"));
        // Combo pass pick 3 (2026-10-04): the upgrade is cost 2 to 1.
        Assert.Equal(10m, Var(Upgraded<ProtoVkFourWindsAscension>(), "Damage"));
        Assert.Contains(Calls("BoreasFang", "AddAscension"),
                        c => c.EndsWith(".CreateCard"));
    }

    [Fact]
    public void Windbound_execution_is_0_cost_single_target()
    {
        var card = new ProtoVkWindboundExecution();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Equal(4m, Var(card, "Damage"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkWindboundExecution>(), "Damage"));
        Assert.DoesNotContain(Calls("ProtoVkWindboundExecution", "OnPlay"),
                              c => c.Contains("TargetingAllOpponents"));
    }
}
