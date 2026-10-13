using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI JELLYFISH BUILD (2026-10-12,
/// <c>review/ruled/kokomi-jellyfish-growth-2026-10-12.md</c>, ruled at all
/// defaults: "Good with all defaults." and "I'm actually totally fine with
/// 0-cost plans"). Stings and Wards cost 0 and keep their Plan lines, the
/// generators are at the Silent's rates (Shoal Call is Blade Dance), Endless
/// Shoal is the Uncommon "a Sting per Plan carried out", and All Streams Flow
/// to the Sea (Rare) and The Shape of Water (Uncommon) count Stings PLAYED
/// (face-up, never written or carried out). Measured Breath and Spring Tide
/// are cut. Sim twin:
/// <c>tier0/tests/test_kokomi_jellyfish_build_2026_10_12.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiJellyfishBuildTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static int Var<T>(string name, bool upgraded = false)
        where T : CardModel, new() =>
        (upgraded ? Upgraded<T>() : new T()).DynamicVars[name].IntValue;

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static List<string> Slice() =>
        Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    private static KokomiOverhaulLedger RolledLedger(int round = 3)
    {
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(Seat.Kokomi().Creature);
        ledger.RollTo(round);
        return ledger;
    }

    // ---- the tokens ---------------------------------------------------------

    [Fact]
    public void The_sting_costs_0_and_keeps_its_plan_line()
    {
        var sting = new ProtoKkSting();
        Assert.Equal(0, sting.EnergyCost.Canonical);
        Assert.Equal(0, Upgraded<ProtoKkSting>().EnergyCost.Canonical);
        Assert.Equal((4, 6), (Var<ProtoKkSting>("Damage"),
                              Var<ProtoKkSting>("Damage", true)));
        Assert.Equal((3, 4), (Var<ProtoKkSting>("PlanDamage"),
                              Var<ProtoKkSting>("PlanDamage", true)));
        Assert.Single(sting.PlanClauses);
        Assert.True(KokomiRefounding.CanBeWritten(sting));
    }

    [Fact]
    public void The_ward_costs_0_and_keeps_its_plan_line()
    {
        var ward = new ProtoKkWard();
        Assert.Equal(0, ward.EnergyCost.Canonical);
        Assert.Equal((4, 6), (Var<ProtoKkWard>("Block"),
                              Var<ProtoKkWard>("Block", true)));
        Assert.Equal((1, 2), (Var<ProtoKkWard>("PlanPowerAmount"),
                              Var<ProtoKkWard>("PlanPowerAmount", true)));
        Assert.Single(ward.PlanClauses);
        Assert.True(KokomiRefounding.CanBeWritten(ward));
    }

    // ---- the generators -------------------------------------------------------

    [Fact]
    public void The_generators_are_at_the_silents_rates()
    {
        Assert.Equal((6, 8), (Var<ProtoKkJellyfishDrift>("Damage"),
                              Var<ProtoKkJellyfishDrift>("Damage", true)));
        Assert.Equal((6, 9), (Var<ProtoKkWatatsumiDrill>("Damage"),
                              Var<ProtoKkWatatsumiDrill>("Damage", true)));
        Assert.Equal((5, 8), (Var<ProtoKkBubbleWard>("Block"),
                              Var<ProtoKkBubbleWard>("Block", true)));
    }

    [Fact]
    public void Shoal_call_is_blade_dance()
    {
        var call = new ProtoKkShoalCall();
        Assert.Equal((CardRarity.Uncommon, 1),
                     (call.Rarity, call.EnergyCost.Canonical));
        Assert.Contains(CardKeyword.Exhaust, call.CanonicalKeywords);
        Assert.Equal((3, 4), (Var<ProtoKkShoalCall>("KkAmount"),
                              Var<ProtoKkShoalCall>("KkAmount", true)));
        Assert.DoesNotContain(Seq("KokomiCards", "ShoalCall"),
                              c => c.Contains("get_IsUpgraded"));
    }

    // ---- Endless Shoal ----------------------------------------------------------

    [Fact]
    public void Endless_shoal_is_an_uncommon_power_at_1_innate_upgraded()
    {
        var card = new ProtoKkEndlessShoal();
        Assert.Equal((CardType.Power, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal("Whenever the [gold]Bake-Kurage[/gold] carries out a "
                   + "[gold]Plan[/gold], add a [gold]Sting[/gold] to your "
                   + "[gold]Hand[/gold].", Face(card));
        var up = Upgraded<ProtoKkEndlessShoal>();
        Assert.Equal(1, up.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Innate, up.Keywords);
    }

    [Fact]
    public void Endless_shoal_pays_a_sting_per_carry_out_of_any_plan()
    {
        // Once per CARRY-OUT: `OnCarriedOut` is called from the tail of
        // `ResolveEntry`, which the drain runs once per carry-out -- so a Plan
        // carried out twice (Nereid's Ascension, Second Wave) gives two
        // Stings. Any Plan: no jellyfish test is left in the payoff.
        var calls = Seq("KokomiRefounding", "OnCarriedOut");
        Assert.Contains(calls, c => c.Contains("KokomiCards.AddJellyfish"));
        Assert.DoesNotContain(calls, c => c.Contains("IsJellyfish"));
        Assert.DoesNotContain(calls, c => c.Contains("CloneCard"));
        Assert.Contains("KokomiRefounding.OnCarriedOut",
                        Seq("KokomiPlan", "ResolveEntry"));
        var drain = Seq("KokomiPlan", "Drain");
        Assert.Contains(drain, c => c.Contains("KokomiPlan.ResolveEntry"));
        Assert.Contains(drain, c => c.Contains("KokomiPlan.CarryOutTimes"));
    }

    // ---- what "played" means -----------------------------------------------------

    [Fact]
    public void A_played_sting_counts_this_combat_and_this_turn()
    {
        var ledger = RolledLedger();
        ledger.NoteStingPlayed();
        ledger.NoteStingPlayed();
        Assert.Equal((2, 2), (ledger.StingsPlayedThisCombat,
                              ledger.StingsPlayedThisTurn));
        ledger.RollTo(4);
        Assert.Equal((2, 0), (ledger.StingsPlayedThisCombat,
                              ledger.StingsPlayedThisTurn));
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Only_a_face_up_sting_play_is_counted()
    {
        // Treatise's reading: a write on the Bake-Kurage is not a play, and
        // neither is a carry-out.
        var hook = Seq("ProtoBakeKuragePower", "AfterCardPlayed");
        var pet = hook.FindIndex(c => c.Contains("KokomiPlan.PlayedOnPet"));
        var carrying = hook.FindIndex(c => c.Contains("KokomiPlan.IsCarryingOut"));
        var note = hook.FindIndex(c => c.Contains("NoteStingPlayed"));
        Assert.True(pet >= 0 && carrying >= 0 && note > pet && note > carrying,
                    string.Join(" ", hook));
    }

    // ---- the growth cards -----------------------------------------------------------

    private static List<string> VarCalls(Type card) =>
        Il.Calls(card.GetMethod("get_CanonicalVars", HeadlessGame.All)!)
            .Concat(card.GetNestedTypes(HeadlessGame.All)
                .SelectMany(t => t.GetMethods(HeadlessGame.All))
                .Where(m => m.GetMethodBody() != null)
                .SelectMany(Il.Calls))
            .ToList();

    [Fact]
    public void All_streams_is_a_rare_that_counts_stings_played_this_combat()
    {
        var card = new ProtoKkAllStreamsFlow();
        Assert.Equal((CardType.Attack, CardRarity.Rare, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(4m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(2m, card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(8m, Upgraded<ProtoKkAllStreamsFlow>()
                             .DynamicVars.CalculationBase.BaseValue);
        var vars = VarCalls(typeof(ProtoKkAllStreamsFlow));
        Assert.Contains(vars, c => c.Contains("get_StingsPlayedThisCombat"));
        Assert.Contains("{InCombat:", Face(card));
    }

    [Fact]
    public void The_shape_of_water_counts_stings_played_this_turn()
    {
        var card = new ProtoKkTheShapeOfWater();
        Assert.Equal((CardType.Attack, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(0m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(6m, card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(8m, Upgraded<ProtoKkTheShapeOfWater>()
                             .DynamicVars.ExtraDamage.BaseValue);
        var vars = VarCalls(typeof(ProtoKkTheShapeOfWater));
        Assert.Contains(vars, c => c.Contains("get_StingsPlayedThisTurn"));
        Assert.Contains("{InCombat:", Face(card));
    }

    // ---- the pool ---------------------------------------------------------------------

    [Fact]
    public void The_pool_stays_78_with_the_cuts_gone_and_the_new_cards_last()
    {
        var slice = Slice();
        Assert.Equal(78, slice.Count);
        Assert.Equal(78, slice.Distinct().Count());
        Assert.DoesNotContain("ProtoKkMeasuredBreath", slice);
        Assert.DoesNotContain("ProtoKkSpringTide", slice);
        Assert.Contains("ProtoKkEndlessShoal", slice);
        Assert.Equal(new[] { "ProtoKkAllStreamsFlow", "ProtoKkTheShapeOfWater" },
                     slice.Skip(slice.Count - 6).Take(2));
        Assert.Null(typeof(KokomiCards).GetMethod("DrawIfNoPlan"));
        var asm = typeof(ProtoKkSting).Assembly;
        var rarity = slice
            .Select(n => (CardModel)Activator.CreateInstance(
                asm.GetType("KleeMod.Cards.Prototype.Generated." + n)!)!)
            .GroupBy(c => c.Rarity)
            .ToDictionary(g => g.Key, g => g.Count());
        // The Kokomi level pass (2026-10-12): Change of Plans C -> U.
        Assert.Equal(20, rarity[CardRarity.Common]);
        Assert.Equal(38, rarity[CardRarity.Uncommon]);
        Assert.Equal(20, rarity[CardRarity.Rare]);
    }
}

/// <summary>The jellyfish build's telemetry (the paper's first check line):
/// Stings made, played, written and lost per fight.</summary>
[Collection(CombatInProgressSwitch.Name)]
public class KokomiJellyfishTelemetryTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public KokomiJellyfishTelemetryTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
    }

    public void Dispose() => Invoke("ResetForTest");

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    [Fact]
    public void A_kokomi_fight_writes_its_sting_counts()
    {
        var kokomi = Seat.Kokomi();
        Invoke("OpenSeatForTest", kokomi.Player, 1, 0);
        Invoke("RecordEtherealLost", kokomi.Player, true);
        Invoke("RecordEtherealLost", kokomi.Player, false);
        var r = JsonDocument.Parse((string)Invoke("JsonForTest", kokomi.Player)!)
            .RootElement;
        Assert.Equal(2, r.GetProperty("ethereal_lost").GetInt32());
        Assert.Equal(1, r.GetProperty("stings_lost").GetInt32());
        foreach (var key in new[] { "stings_made", "stings_played",
                                    "stings_written" })
        {
            Assert.Equal(0, r.GetProperty(key).GetInt32());
        }
    }

    [Fact]
    public void The_counts_are_written_where_stings_are_made_written_and_lost()
    {
        Assert.Contains(Il.CallSequence(Il.Method("KokomiCards", "AddJellyfish")),
                        c => c.Contains("NoteStingsMade"));
        Assert.Contains(Il.CallSequence(Il.Method("KokomiPlan", "Schedule")),
                        c => c.Contains("NoteStingWritten"));
        var ledger = new KokomiOverhaulLedger();
        ledger.NoteStingsMade(3);
        ledger.NoteStingWritten();
        Assert.Equal((3, 1), (ledger.StingsMadeThisCombat,
                              ledger.StingsWrittenThisCombat));
    }
}
