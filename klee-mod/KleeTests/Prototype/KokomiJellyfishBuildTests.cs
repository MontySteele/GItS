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
        // Ward and Casket (2026-10-18, [USER]: "Ward should stop giving
        // Block... change it to 'draw 1. Plan: draw 1'"): Draw 1. Plan: Draw
        // 1 (2 upgraded). No Block, no Weak.
        Assert.Equal((1, 1), (Var<ProtoKkWard>("Cards"),
                              Var<ProtoKkWard>("Cards", true)));
        Assert.Equal((1, 2), (Var<ProtoKkWard>("PlanCards"),
                              Var<ProtoKkWard>("PlanCards", true)));
        Assert.False(ward.DynamicVars.ContainsKey("Block"));
        Assert.False(ward.DynamicVars.ContainsKey("PlanPowerAmount"));
        var clause = Assert.Single(ward.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Draw, clause.Kind);
        Assert.Contains("CardPileCmd.Draw",
                        Il.Calls(Il.Method("ProtoKkWard", "PlayNowLine")));
        Assert.DoesNotContain("CreatureCmd.GainBlock",
                              Il.Calls(Il.Method("ProtoKkWard", "PlayNowLine")));
        Assert.True(KokomiRefounding.CanBeWritten(ward));
    }

    // ---- the generators -------------------------------------------------------

    [Fact]
    public void The_generators_are_at_the_silents_rates()
    {
        Assert.Equal((6, 8), (Var<ProtoKkJellyfishDrift>("Damage"),
                              Var<ProtoKkJellyfishDrift>("Damage", true)));
        // The pool sweep (2026-10-18): Drill 8 [11].
        Assert.Equal((8, 11), (Var<ProtoKkWatatsumiDrill>("Damage"),
                              Var<ProtoKkWatatsumiDrill>("Damage", true)));
        // The pool sweep (2026-10-18): Bubble Ward 7 [10].
        Assert.Equal((7, 10), (Var<ProtoKkBubbleWard>("Block"),
                              Var<ProtoKkBubbleWard>("Block", true)));
    }

    [Fact]
    public void Shoal_call_is_blade_dance()
    {
        var call = new ProtoKkShoalCall();
        // Common since the Kokomi review (2026-10-13), as Blade Dance is.
        Assert.Equal((CardRarity.Common, 1),
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
                   + "[gold]Plan[/gold] that is not a [gold]Sting[/gold] or "
                   + "[gold]Ward[/gold], add a [gold]Sting[/gold] to your "
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
        // Stings. Since the Kokomi card paper v2 (2026-10-18) a Sting's or
        // Ward's Plan pays nothing: the jellyfish test is back, on the line.
        var calls = Seq("KokomiRefounding", "OnCarriedOut");
        Assert.Contains(calls, c => c.Contains("KokomiCards.AddJellyfish"));
        Assert.Contains(calls, c => c.Contains("IsJellyfish"));
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
        // The pool overhaul (2026-10-13): 5 [7], plus 5 for each Elemental
        // Reaction she triggered this combat (was 4 [8] plus 2 per Sting).
        // The numbers pass (kokomi-review-r5-2026-10-14): base 10 [12].
        var card = new ProtoKkAllStreamsFlow();
        Assert.Equal((CardType.Attack, CardRarity.Rare, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(10m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(5m, card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(12m, Upgraded<ProtoKkAllStreamsFlow>()
                             .DynamicVars.CalculationBase.BaseValue);
        var vars = VarCalls(typeof(ProtoKkAllStreamsFlow));
        Assert.Contains(vars, c => c.Contains("get_ReactionsThisCombat"));
        Assert.Contains("{InCombat:", Face(card));
    }

    [Fact]
    public void The_shape_of_water_counts_stings_played_this_turn()
    {
        var card = new ProtoKkTheShapeOfWater();
        Assert.Equal((CardType.Attack, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(5m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(5m, card.DynamicVars.ExtraDamage.BaseValue);
        var up = Upgraded<ProtoKkTheShapeOfWater>();
        Assert.Equal(7m, up.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(7m, up.DynamicVars.ExtraDamage.BaseValue);
        var vars = VarCalls(typeof(ProtoKkTheShapeOfWater));
        Assert.Contains(vars, c => c.Contains("get_StingsPlayedThisTurn"));
        Assert.Contains("{InCombat:", Face(card));
    }

    /// <summary>Kokomi review (2026-10-13), pick (a): a base hit, "Deal 5 [7]
    /// Hydro damage, plus 5 [7] for each Sting you played this turn." Both
    /// numbers print with diff(); the hit is base + per x Stings (0 Stings: 5,
    /// 2 Stings: 15; upgraded 7 and 21). The sim twin plays it.</summary>
    [Theory]
    [InlineData(false, 0, 5)]
    [InlineData(false, 2, 15)]
    [InlineData(true, 0, 7)]
    [InlineData(true, 2, 21)]
    public void The_shape_of_water_has_a_base_hit(bool upgraded, int stings, int dealt)
    {
        var card = upgraded ? Upgraded<ProtoKkTheShapeOfWater>() : new ProtoKkTheShapeOfWater();
        Assert.Equal(
            "Deal {CalculationBase:diff()} [gold]Hydro[/gold] damage, plus {ExtraDamage:diff()} "
            + "for each [gold]Sting[/gold] you played this turn."
            + "{InCombat:\n(Deals {CalculatedDamage:diff()} damage)|}",
            Face(card));
        Assert.Equal(dealt,
            card.DynamicVars.CalculationBase.IntValue
            + card.DynamicVars.ExtraDamage.IntValue * stings);
    }

    // ---- the pool ---------------------------------------------------------------------

    [Fact]
    public void The_pool_stays_78_with_the_cuts_gone_and_the_new_cards_last()
    {
        var slice = Slice();
        Assert.Equal(79, slice.Count); // Kokomi v3 (2026-10-18): Unbroken Tide
        Assert.Equal(79, slice.Distinct().Count());
        Assert.DoesNotContain("ProtoKkMeasuredBreath", slice);
        Assert.DoesNotContain("ProtoKkSpringTide", slice);
        Assert.Contains("ProtoKkEndlessShoal", slice);
        Assert.Equal(new[] { "ProtoKkAllStreamsFlow", "ProtoKkTheShapeOfWater" },
                     slice.Skip(slice.Count - 7).Take(2));   // Unbroken Tide after (Kokomi v3)
        Assert.Null(typeof(KokomiCards).GetMethod("DrawIfNoPlan"));
        var asm = typeof(ProtoKkSting).Assembly;
        var rarity = slice
            .Select(n => (CardModel)Activator.CreateInstance(
                asm.GetType("KleeMod.Cards.Prototype.Generated." + n)!)!)
            .GroupBy(c => c.Rarity)
            .ToDictionary(g => g.Key, g => g.Count());
        // The Kokomi level pass (2026-10-12): Change of Plans C -> U.
        // Kokomi v3 (2026-10-18): Unbroken Tide (U).
        Assert.Equal(20, rarity[CardRarity.Common]);
        Assert.Equal(39, rarity[CardRarity.Uncommon]);
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
