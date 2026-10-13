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
        // Varka co-op fixes (2026-10-11): 6 [8] + 2 [3], was 4 [6] + 3 [4].
        Assert.Equal(6m, Var(songs, "VkBase"));
        Assert.Equal(2m, Var(songs, "VkPer"));
        Assert.Equal(8m, Var(Upgraded<ProtoVkBarbaraShowBegin>(), "VkBase"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkBarbaraShowBegin>(), "VkPer"));
        var body = Calls("VarkaCards", "GleefulSongs");
        Assert.Contains("ElementalHit.ApplyOnly", body);
        Assert.Contains("ReactionEffects.get_TotalResolved", body);
        Assert.Contains("VarkaCards.GainCardBlock", body);
    }

    [Fact]
    public void Rippling_guard_blocks_and_applies_the_current_element()
    {
        // The Varka Block paper (2026-10-12, pick 2 (a)): "Gain 7 [10] Block.
        // Apply your current element to an enemy." Without one, nothing lands
        // (VarkaCards.ApplyCurrentElement returns on Element.None).
        var guard = new ProtoVkRipplingGuard();
        Assert.Equal(CardRarity.Common, guard.Rarity);
        Assert.Equal(TargetType.AnyEnemy, guard.TargetType);
        Assert.Equal(7m, Var(guard, "Block"));
        Assert.Equal(10m, Var(Upgraded<ProtoVkRipplingGuard>(), "Block"));
        var body = Il.Calls(Il.Method("ProtoVkRipplingGuard", "OnPlay"));
        Assert.Contains("CreatureCmd.GainBlock", body);
        Assert.Contains("VarkaCards.ApplyCurrentElement", body);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", body);
        Assert.Null(typeof(VarkaCards).GetMethod("RipplingGuard"));
    }

    [Fact]
    public void Whisper_of_water_is_the_base_blur()
    {
        // The Hydro paper (2026-10-10): "Your Block is not removed at the
        // start of your next turn" -- the game's own BlurPower, one stack.
        var play = Calls("ProtoVkBarbaraWhisperOfWater", "OnPlay");
        Assert.Contains(
            Il.CallSequence(Il.Method("ProtoVkBarbaraWhisperOfWater", "OnPlay")),
            c => c.Contains("PowerCmd.Apply<BlurPower>"));
        Assert.Contains("CreatureCmd.GainBlock", play);
        Assert.DoesNotContain(play, c => c.Contains("VarkaCards"));
        Assert.False(new ProtoVkBarbaraWhisperOfWater().DynamicVars.ContainsKey("VkAmount"));
        // The Varka review (2026-10-12): a Knight's face ends in its switch line.
        // The card text pass (2026-10-12, rule 6): "Next turn," opens it.
        Assert.EndsWith("Next turn, your [gold]Block[/gold] is not removed."
                        + "{InCombat:{VarkaSwitch}|}",
                        new ProtoVkBarbaraWhisperOfWater().Localization!
                            .Single(p => p.Item1 == "description").Item2);
    }

    [Fact]
    public void Tidal_bulwark_is_hydros_body_slam()
    {
        // The Hydro paper (2026-10-10): an Attack, 1, Hydro's Body Slam.
        // Varka text pass (2026-10-13), ruled (a): "Deal Hydro damage equal to
        // your Block, plus 2 [3] for each Hydro Oath." No Block of its own;
        // one Hydro hit through VarkaCards.TidalBulwark, so it reacts.
        var card = new ProtoVkTidalBulwark();
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.False(card.DynamicVars.TryGetValue("Block", out _));
        Assert.Equal(2m, Var(card, "VkPer"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkTidalBulwark>(), "VkPer"));
        Assert.IsType<VarkaTidalBulwarkDamageVar>(card.DynamicVars["VkHit"]);
        var play = Calls("ProtoVkTidalBulwark", "OnPlay");
        Assert.Contains("VarkaCards.TidalBulwark", play);
        Assert.DoesNotContain("CreatureCmd.GainBlock", play);
        var body = Calls("VarkaCards", "TidalBulwark");
        Assert.Contains("VarkaCards.ElementHit", body);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", body);
        var face = card.Localization!.Single(p => p.Item1 == "description").Item2;
        Assert.StartsWith("Deal [gold]Hydro[/gold] damage equal to your [gold]Block[/gold]", face);
        Assert.DoesNotContain("Apply", face);
        Assert.Contains("(Deals {VkHit:diff()} damage)", face);
        Assert.Equal(14, VarkaCards.TidalBulwarkDamage(10, 2m, 2));
        Assert.Equal(0, VarkaCards.TidalBulwarkDamage(0, 3m, 0));
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
        // Varka last pass (2026-10-12): Retain.
        Assert.Contains(CardKeyword.Retain, battery.CanonicalKeywords);
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
        // Varka round 3 (2026-10-10): the floor 5 [6], each aura 3 [4].
        Assert.Equal(5m, Var(ward, "VkBase"));
        Assert.Equal(3m, Var(ward, "VkPer"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkFrostWard>(), "VkBase"));
        Assert.Equal(4m, Var(Upgraded<ProtoVkFrostWard>(), "VkPer"));
        var body = Calls("VarkaCards", "FrostWard");
        Assert.Contains("AuraCmd.Find", body);
        Assert.Contains("PowerCmd.Apply", body);
        Assert.Contains("VarkaCards.GainCardBlock", body);
        // Varka round 3 (2026-10-10): "Gain 5 [6] Block. For each enemy
        // with an aura, apply 1 Weak and gain 3 [4] additional Block."
        Assert.Contains("VarkaCards.FrostWardBlock", body);
        Assert.Equal(5, VarkaCards.FrostWardBlock(5, 3, 0));
        Assert.Equal(11, VarkaCards.FrostWardBlock(5, 3, 2));
        Assert.Equal(10, VarkaCards.FrostWardBlock(6, 4, 1));
    }

    [Fact]
    public void Sworn_brotherhood_and_stormward_carry_round_3_numbers()
    {
        // Varka round 3 (2026-10-10): Sworn Brotherhood 2 [3] Oath of the
        // current element; Stormward Stance no Oath gate. The Varka Block
        // paper (2026-10-12): Stormward Stance 4 [6], was 3 [5].
        Assert.Equal(2m, Var(new ProtoVkSwornBrotherhood(), "PowerAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkSwornBrotherhood>(), "PowerAmount"));
        Assert.Equal(4m, Var(new ProtoVkStormwardStance(), "PowerAmount"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkStormwardStance>(), "PowerAmount"));
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
