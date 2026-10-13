using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI EXPANSION, BATCH ONE (2026-09-29). Paper
/// <c>review/active/kokomi-expansion-2026-09-29.md</c>, every pick ruled at
/// its default ([USER]: "The defaults work here"): four decks, 22 rows (12
/// Uncommon, 10 Rare), Watatsumi's Grace in place of The Clouds Like Waves
/// Rippling. The readers run for real on a headless seat; anything that awaits
/// a command (the drain, a draw, a Block gain) is pinned off the compiled
/// methods. Sim twin: <c>tier0/tests/test_kokomi_expansion.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiExpansionTests : IDisposable
{

    public KokomiExpansionTests() { }

    public void Dispose() { }

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

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static readonly string[] Batch =
    {
        // The re-founding (2026-10-12) cut Weight of the Plan, Lull, The Long
        // Game, Salt in the Wound, Tidal Resonance and Kurage Swarm; the
        // jellyfish build (2026-10-12) cut Measured Breath.
        "ProtoKkUndertideLance",
        "ProtoKkGrandDesign",
        "ProtoKkMasterstroke",
        "ProtoKkDrowningPressure",
        "ProtoKkUndercurrentSnare",
        "ProtoKkAtWatersEdge", "ProtoKkCeremonialGarment",
        "ProtoKkSuffocatingDeep", "ProtoKkCoralCrash", "ProtoKkEveningWatch",
        "ProtoKkBraceForTheTide", "ProtoKkWatatsumisGrace",
        "ProtoKkTidalRiposte", "ProtoKkShoalCall",
    };

    // ---- the offer -------------------------------------------------------

    [Fact]
    public void No_face_in_the_batch_says_morning()
    {
        var asm = typeof(ProtoKkMasterstroke).Assembly;
        foreach (var n in Batch)
        {
            var card = (CardModel)Activator.CreateInstance(
                asm.GetType("KleeMod.Cards.Prototype.Generated." + n)!)!;
            Assert.DoesNotContain("morning", Face(card),
                                  StringComparison.OrdinalIgnoreCase);
        }
    }

    // ---- the Big Plan -------------------------------------------------------

    [Fact]
    public void Masterstroke_is_a_retained_plan_only_attack()
    {
        var card = new ProtoKkMasterstroke();
        Assert.Equal((CardType.Attack, CardRarity.Rare, 3),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.StartsWith("Play on the [gold]Bake-Kurage[/gold].", Face(card));
        var clause = Assert.Single(card.PlanClauses);
        // The re-founding (2026-10-12): a flat 42 [54], no Strength rider.
        Assert.Equal((KokomiPlan.Kind.Damage, 42, 1),
                     (clause.Kind, clause.Amount, clause.StrengthTimes));
        Assert.Equal(54, Upgraded<ProtoKkMasterstroke>().PlanClauses.Single().Amount);
    }

    // ---- Tide Control ---------------------------------------------------------

    [Fact]
    public void Ceremonial_garment_pays_per_weak_and_vulnerable_stack()
    {
        var seat = Seat.Kokomi().WithPower<ProtoCeremonialGarmentPower>(1);
        var power = seat.Creature.Powers.OfType<ProtoCeremonialGarmentPower>()
                        .Single();
        var target = Seat.Kokomi()
            .WithPower<WeakPower>(2).WithPower<VulnerablePower>(1).Creature;
        var attack = new ProtoKkPincer();
        // The Kokomi card pass (2026-10-11): stacks, so Weak 2 + Vulnerable 1
        // is 3 (it counted 2 distinct debuffs before).
        Assert.Equal(3m, power.ModifyDamageAdditive(
            target, 10m, ValueProp.Move, seat.Creature, attack, null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 10m, ValueProp.Move, seat.Creature,
            new ProtoKkCoralBulwark(), null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 10m, ValueProp.Unpowered, seat.Creature, attack, null));
    }

    /// <summary>The Kokomi card pass (2026-10-11): "The first time each
    /// turn you deal Hydro damage to an enemy, apply 1 Weak and 1 Vulnerable
    /// to it." Fed from both Hydro doors (a powered hit's
    /// <c>AfterDamageGiven</c> and <c>ElementalHit.Deal</c>), no longer from
    /// the reaction site; the latch is claimed before the two applications,
    /// so it fires once per turn.</summary>
    [Fact]
    public void At_waters_edge_fires_once_per_turn_on_hydro_damage()
    {
        Assert.DoesNotContain(Seq("ReactionEffects", "Resolve"),
                              c => c.Contains("KokomiExpansion"));
        Assert.Null(typeof(KokomiExpansion).GetMethod(
            "OnReaction", HeadlessGame.All));
        var given = Seq("AtWatersEdgePower", "AfterDamageGiven");
        Assert.Contains(given, c => c.Contains("AuraCmd.ElementOfPlay"));
        Assert.Contains(given, c => c.Contains("KokomiExpansion.OnHydroDamage"));
        Assert.Contains(Seq("ElementalHit", "Deal"),
                        c => c.Contains("KokomiExpansion.OnHydroDamage"));
        var hydro = Seq("KokomiExpansion", "OnHydroDamage");
        var claim = hydro.FindIndex(c => c.Contains("ClaimOncePerTurn"));
        var first = hydro.FindIndex(c => c.Contains("PowerCmd.Apply"));
        Assert.True(claim >= 0 && first > claim);
        Assert.Equal(2, hydro.Count(c => c.Contains("PowerCmd.Apply")));

        var ledger = new KokomiOverhaulLedger();
        ledger.RollTo(1);
        Assert.True(ledger.Claim(nameof(AtWatersEdgePower)));
        Assert.False(ledger.Claim(nameof(AtWatersEdgePower)));
        ledger.RollTo(2);
        Assert.True(ledger.Claim(nameof(AtWatersEdgePower)));
        Assert.StartsWith("The first time each turn you deal [gold]Hydro[/gold]",
                          Face(new ProtoKkAtWatersEdge()));
    }

    /// <summary>The Kokomi card pass (2026-10-11, pick 1): Drowning
    /// Pressure counts STACKS of Weak plus stacks of Vulnerable. 2 Weak and 2
    /// Vulnerable read 4, so 3 each deals 12 (before the Vulnerable).</summary>
    [Fact]
    public void Drowning_pressure_counts_weak_and_vulnerable_stacks()
    {
        var target = Seat.Kokomi()
            .WithPower<WeakPower>(2).WithPower<VulnerablePower>(2).Creature;
        Assert.Equal(4, KokomiOverhaulKit.WeakVulnStacks(target));
        Assert.Equal(0, KokomiOverhaulKit.WeakVulnStacks(null));
        var card = new ProtoKkDrowningPressure();
        Assert.Equal(12m, card.DynamicVars["ExtraDamage"].BaseValue
                          * KokomiOverhaulKit.WeakVulnStacks(target));
        Assert.Equal(4m, Upgraded<ProtoKkDrowningPressure>()
                             .DynamicVars["ExtraDamage"].BaseValue);
    }

    [Fact]
    public void The_tide_control_faces_and_clauses()
    {
        var snare = Assert.Single(new ProtoKkUndercurrentSnare().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.ApplyVulnerable, 1, KokomiPlan.Aim.AllEnemies),
                     (snare.Kind, snare.Amount, snare.Aim));
        Assert.Equal(2, Upgraded<ProtoKkUndercurrentSnare>().PlanClauses
                            .Single().Amount);
        // The re-founding (2026-10-12): Undercurrent Snare costs 1.
        Assert.Equal(1, new ProtoKkUndercurrentSnare().EnergyCost.Canonical);
        Assert.Contains(Il.Calls(Il.Method("ProtoKkSuffocatingDeep", "OnPlay")),
                        c => c.Contains("KokomiCards.DoubleWeakVulnerable"));
    }

    // ---- Dusk Guard ----------------------------------------------------------------

    [Fact]
    public void Watatsumis_grace_keeps_up_to_its_cap_the_sturdy_clamp_way()
    {
        var seat = Seat.Kokomi().WithPower<WatatsumisGracePower>(10);
        var grace = seat.Creature.Powers.OfType<WatatsumisGracePower>().Single();
        Assert.False(grace.ShouldClearBlock(seat.Creature));
        Assert.True(grace.ShouldClearBlock(Seat.Kokomi().Creature));
        Assert.Contains(Il.Calls(Il.Method("WatatsumisGracePower",
                                           "AfterPreventingBlockClear")),
                        c => c.Contains("CreatureCmd.LoseBlock"));
        Assert.Equal(15m, Upgraded<ProtoKkWatatsumisGrace>()
                              .DynamicVars["PowerAmount"].BaseValue);
    }

    [Fact]
    public void Tidal_riposte_answers_a_fully_blocked_hit()
    {
        var calls = Il.Calls(Il.Method("TidalRipostePower", "AfterDamageReceived"));
        Assert.Contains(calls, c => c.Contains("ElementalHit.Deal"));
        Assert.Contains(calls, c => c.Contains("DamageResult.get_BlockedDamage"));
        Assert.Contains(calls, c => c.Contains("DamageResult.get_UnblockedDamage"));
    }

    [Fact]
    public void Coral_crash_deals_her_block()
    {
        var card = new ProtoKkCoralCrash();
        // Pool completion (2026-10-01, paper sec.6): Common, 1 [0].
        Assert.Equal((CardType.Attack, CardRarity.Common),
                     (card.Type, card.Rarity));
        Assert.Contains("Block", Face(card));
    }

    // ---- Plan volume -----------------------------------------------------------------

    [Fact]
    public void Shoal_call_is_blade_dance_with_plain_stings()
    {
        // The jellyfish build (2026-10-12): "Add 3 [4] Stings to your hand."
        // Plain Stings on both faces; the upgrade adds one.
        var calls = Seq("KokomiCards", "ShoalCall");
        Assert.Contains(calls, c => c.Contains("KokomiCards.AddJellyfish"));
        Assert.DoesNotContain(calls, c => c.Contains("get_IsUpgraded"));
        Assert.Equal("Add {KkAmount:diff()} [gold]Stings[/gold] to your [gold]Hand[/gold].",
                     Face(new ProtoKkShoalCall()));
    }
}
