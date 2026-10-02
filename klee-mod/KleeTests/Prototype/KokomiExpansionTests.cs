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
        "ProtoKkWeightOfThePlan", "ProtoKkLull", "ProtoKkUndertideLance",
        "ProtoKkMeasuredBreath", "ProtoKkGrandDesign", "ProtoKkTheLongGame",
        "ProtoKkMasterstroke",
        "ProtoKkDrowningPressure", "ProtoKkSaltInTheWound",
        "ProtoKkUndercurrentSnare", "ProtoKkTidalResonance",
        "ProtoKkAtWatersEdge", "ProtoKkCeremonialGarment",
        "ProtoKkSuffocatingDeep", "ProtoKkCoralCrash", "ProtoKkEveningWatch",
        "ProtoKkBraceForTheTide", "ProtoKkWatatsumisGrace",
        "ProtoKkTidalRiposte", "ProtoKkShoalCall", "ProtoKkKurageSwarm",
    };

    // ---- the offer -------------------------------------------------------

    [Fact]
    public void The_offer_is_seventy_with_the_batch_before_the_payoff_pass()
    {
        var slice = Seq("KokomiOverhaulRoster", "Slice")
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();
        // SEVENTY since the payoff pass (2026-10-01): Second Thoughts cut
        // ahead of the batch, two rows after it; pool completion (2026-10-01)
        // eight more; the status batch (2026-10-01) cut All Streams Flow to
        // the Sea and five rows ahead of the batch, and appended seven.
        Assert.Equal(78, slice.Count);
        Assert.Equal(Batch, slice.Skip(40).Take(21).ToArray());
        Assert.DoesNotContain(slice, c => c.Contains("AllStreams"));
        Assert.DoesNotContain(slice, c => c.Contains("CloudsLikeWaves"));
        Assert.Null(typeof(KokomiOverhaulKit).Assembly
            .GetType("KleeMod.Powers.CloudsLikeWavesPower"));
    }

    [Fact]
    public void The_batch_is_twelve_uncommon_and_ten_rare()
    {
        var asm = typeof(ProtoKkNip).Assembly;
        var rarities = Batch
            .Select(n => ((CardModel)Activator.CreateInstance(
                asm.GetType("KleeMod.Cards.Prototype.Generated." + n)!)!).Rarity)
            .ToList();
        // Pool completion (2026-10-01, paper sec.6): Coral Crash is Common.
        Assert.Equal(11, rarities.Count(r => r == CardRarity.Uncommon));
        Assert.Equal(1, rarities.Count(r => r == CardRarity.Common));
        // The status batch (2026-10-01) cut All Streams Flow to the Sea.
        Assert.Equal(9, rarities.Count(r => r == CardRarity.Rare));
    }

    [Fact]
    public void No_face_in_the_batch_says_morning()
    {
        var asm = typeof(ProtoKkNip).Assembly;
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
    public void A_write_carries_the_energy_the_play_paid()
    {
        Assert.Contains("KokomiPlan.Schedule",
                        Il.Calls(Il.Method("ProtoKkMasterstroke", "OnPlay")));
        Assert.Contains("CardPlay.get_Resources",
                        Il.Calls(Il.Method("ProtoKkMasterstroke", "OnPlay")));
        var entry = new KokomiPlan.Entry(null,
            Array.Empty<KokomiPlan.Planned>(), Paid: 3, Extra: 2);
        Assert.Equal((3, 2), (entry.Paid, entry.Extra));
    }

    [Fact]
    public void Weight_of_the_plan_reads_the_energy_waiting()
    {
        var card = new ProtoKkWeightOfThePlan();
        Assert.Equal((CardType.Attack, 1), (card.Type, card.EnergyCost.Canonical));
        Assert.Contains("Energy", Face(card));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkWeightOfThePlan",
                                           "get_CanonicalVars")),
                        c => c.Contains("KokomiPlan.EnergyWaiting"));
    }

    [Fact]
    public void Lull_and_undertide_lance_plan_their_alone_clauses()
    {
        var lull = Assert.Single(new ProtoKkLull().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.EnergyIfAlone, 2), (lull.Kind, lull.Amount));
        var lance = Assert.Single(new ProtoKkUndertideLance().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.DamageIfAlone, 12, KokomiPlan.Aim.FrontEnemy),
                     (lance.Kind, lance.Amount, lance.Aim));
        Assert.Equal(16, Assert.Single(
            Upgraded<ProtoKkUndertideLance>().PlanClauses).Amount);
        // The drain hands its entry count to every carry-out.
        Assert.Contains(Seq("KokomiPlan", "Drain"),
                        c => c.Contains("ResolveEntry"));
    }

    [Fact]
    public void Masterstroke_is_a_retained_plan_only_attack()
    {
        var card = new ProtoKkMasterstroke();
        Assert.Equal((CardType.Attack, CardRarity.Rare, 3),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.StartsWith("Play on the [gold]Bake-Kurage[/gold].", Face(card));
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Damage, 30), (clause.Kind, clause.Amount));
        Assert.Equal(40, Upgraded<ProtoKkMasterstroke>().PlanClauses.Single().Amount);
    }

    [Fact]
    public void Grand_design_and_kurage_swarm_feed_the_casket()
    {
        Assert.Contains(Seq("KokomiPlan", "ResolveEntry"),
                        c => c.Contains("GrandDesignPower.Note"));
        Assert.Contains(Seq("KokomiPlan", "Schedule"),
                        c => c.Contains("KurageSwarmPower.Note"));
        // 1 more per Energy paid (main session, 2026-09-29).
        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi().WithPower<GrandDesignPower>(1);
        var free = new KokomiPlan.Entry(null,
            Array.Empty<KokomiPlan.Planned>(), Paid: 0);
        var three = new KokomiPlan.Entry(null,
            Array.Empty<KokomiPlan.Planned>(), Paid: 3);
        GrandDesignPower.Note(seat.Creature, free);
        Assert.Equal(0, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
        GrandDesignPower.Note(seat.Creature, three);
        Assert.Equal(3, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
        // Power cost sweep, 2026-09-30: cost stays 1, the upgrade is Innate.
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKkGrandDesign>().Keywords);
        Assert.Equal(1, new ProtoKkGrandDesign().EnergyCost.Canonical);
        Assert.Equal(1, new ProtoKkKurageSwarm().EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKkKurageSwarm>().Keywords);

        KokomiOverhaulLedger.ResetAll();
        var swarm = Seat.Kokomi().WithPower<KurageSwarmPower>(1);
        KurageSwarmPower.Note(swarm.Creature);
        Assert.Equal(1, KokomiOverhaulLedger.For(swarm.Creature).CasketCount);
    }

    [Fact]
    public void The_long_game_reads_the_pre_drain_queue()
    {
        var start = Seq("ProtoBakeKuragePower", "AfterPlayerTurnStart");
        var game = start.FindIndex(c => c.Contains("TheLongGamePower.Signal"));
        var drain = start.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        Assert.True(game >= 0 && drain > game);
        Assert.Equal(1, KokomiOverhaulLaw.LongGameWaiting);
    }

    // ---- Tide Control ---------------------------------------------------------

    [Fact]
    public void Ceremonial_garment_pays_per_debuff_on_an_attack_only()
    {
        var seat = Seat.Kokomi().WithPower<ProtoCeremonialGarmentPower>(1);
        var power = seat.Creature.Powers.OfType<ProtoCeremonialGarmentPower>()
                        .Single();
        var target = Seat.Kokomi()
            .WithPower<WeakPower>(2).WithPower<VulnerablePower>(1).Creature;
        var attack = new ProtoKkMassedVolley();
        Assert.Equal(2m, power.ModifyDamageAdditive(
            target, 10m, ValueProp.Move, seat.Creature, attack, null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 10m, ValueProp.Move, seat.Creature,
            new ProtoKkCoralBulwark(), null));
        Assert.Equal(0m, power.ModifyDamageAdditive(
            target, 10m, ValueProp.Unpowered, seat.Creature, attack, null));
    }

    [Fact]
    public void At_waters_edge_rides_the_one_reaction_site()
    {
        Assert.Contains(Seq("ReactionEffects", "Resolve"),
                        c => c.Contains("KokomiExpansion.OnReaction"));
        Assert.Equal(2, Seq("KokomiExpansion", "OnReaction")
            .Count(c => c.Contains("PowerCmd.Apply")));
    }

    [Fact]
    public void The_tide_control_faces_and_clauses()
    {
        var snare = Assert.Single(new ProtoKkUndercurrentSnare().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.ApplyVulnerable, 1, KokomiPlan.Aim.AllEnemies),
                     (snare.Kind, snare.Amount, snare.Aim));
        Assert.Equal(2, Upgraded<ProtoKkUndercurrentSnare>().PlanClauses
                            .Single().Amount);
        Assert.Equal(1m, new ProtoKkSaltInTheWound().DynamicVars["KkAmount"].BaseValue);
        Assert.Equal(2m, Upgraded<ProtoKkSaltInTheWound>()
                             .DynamicVars["KkAmount"].BaseValue);
        Assert.Contains(Il.Calls(Il.Method("ProtoKkSuffocatingDeep", "OnPlay")),
                        c => c.Contains("KokomiCards.DoubleWeakVulnerable"));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkTidalResonance", "OnPlay")),
                        c => c.Contains("KokomiCards.Resonance"));
    }

    // ---- Dusk Guard ----------------------------------------------------------------

    [Fact]
    public void Evening_watch_and_brace_are_dusk_plans()
    {
        var watch = Assert.Single(new ProtoKkEveningWatch().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.BlockPerAttackingEnemy, 5),
                     (watch.Kind, watch.Amount));
        Assert.Equal(7, Upgraded<ProtoKkEveningWatch>().PlanClauses.Single().Amount);
        var brace = Assert.Single(new ProtoKkBraceForTheTide().PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DoubleBlock, brace.Kind);
        Assert.Contains(CardKeyword.Exhaust,
                        Upgraded<ProtoKkBraceForTheTide>().CanonicalKeywords);
        Assert.Contains("Or [gold]dusk[/gold] [gold]plan[/gold]",
                        Face(new ProtoKkEveningWatch()));
        // Plan-only: no line above to choose, so no "or" (2026-10-01).
        Assert.Contains("\n[gold]Dusk[/gold] [gold]Plan[/gold]: ",
                        Face(new ProtoKkBraceForTheTide()));
        Assert.DoesNotContain("Or [gold]", Face(new ProtoKkBraceForTheTide()));
    }

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
    public void Shoal_call_adds_nips_upgraded_when_it_is()
    {
        var calls = Seq("KokomiCards", "ShoalCall");
        Assert.Contains(calls, c => c.Contains("ProtoKkNip"));
        Assert.Contains(calls, c => c.Contains("get_IsUpgraded"));
        Assert.Contains("{IfUpgraded:show: They are upgraded.|}",
                        Face(new ProtoKkShoalCall()));
    }
}
