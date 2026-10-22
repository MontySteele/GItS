using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI TASTE AUDIT (2026-10-21,
/// <c>review/active/kokomi-taste-audit-2026-10-21.md</c>, "Ruled 2026-10-21:
/// all five (a)"; [USER]: "That's a lot of card changes, but we can do that and
/// rerun the balance suite to see how it feels." and "Agreed on all 5
/// defaults."). Ten cards. Structural and pure pins (the headless boundary);
/// sim twin <c>tier0/tests/test_kokomi_taste_audit_2026_10_21.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiTasteAuditTests
{
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

    // ---- "Plan a Sting" -------------------------------------------------------

    [Fact]
    public void Plan_a_sting_writes_its_own_plan_line_and_pays_the_casket_per_sting()
    {
        // Each generated Sting is written through `KokomiPlan.Schedule` with
        // its own Plan line, then the Casket pays for it as for a Sting she
        // Planned herself.
        var seq = Seq("KokomiCards", "PlanJellyfish");
        var schedule = seq.FindIndex(c => c.Contains("KokomiPlan.Schedule"));
        var casket = seq.FindIndex(c => c.Contains("TamakushiCasket.PayForPlanned"));
        Assert.True(schedule >= 0 && casket > schedule, string.Join(" ", seq));
        Assert.Contains(seq, c => c.Contains("get_PlanClauses"));
    }

    [Fact]
    public void The_casket_pays_a_generated_sting_as_a_planned_one()
    {
        // The same rule as a play: a Plan card planned counts, the relic's
        // own Block, raw.
        Assert.True(TamakushiCasket.CountsCard(new ProtoKkSting(), planned: true));
        var pay = Seq("TamakushiCasket", "PayForPlanned");
        // Through `CountsPlanned`, which is `CountsCard(planned: true)` plus
        // a Basic Grand Design plans as itself (Kokomi Balance suite 4).
        Assert.Contains(pay, c => c.Contains("TamakushiCasket.CountsPlanned"));
        Assert.True(TamakushiCasket.CountsPlanned(new ProtoKkSting()));
        Assert.Contains(pay, c => c.Contains("CreatureCmd.GainBlock"));
        // Not gated on a carry-out: Flotsam Surge's Plan writes one inside it.
        Assert.DoesNotContain(pay, c => c.Contains("KokomiPlan.IsCarryingOut"));
    }

    // ---- 1. Shoal Call ------------------------------------------------------------

    [Fact]
    public void Shoal_call_plans_three_and_four_stings()
    {
        var card = new ProtoKkShoalCall();
        Assert.Equal((CardType.Skill, CardRarity.Common, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal(3, card.DynamicVars["KkAmount"].IntValue);
        Assert.Equal(4, Upgraded<ProtoKkShoalCall>().DynamicVars["KkAmount"].IntValue);
        Assert.Contains(Seq("KokomiCards", "PlanStings"),
                        c => c.Contains("KokomiCards.PlanJellyfish"));
    }

    // ---- 2. Kurage Bloom ----------------------------------------------------------

    [Fact]
    public void Kurage_bloom_plans_its_sting_at_the_end_of_her_turn()
    {
        Assert.Equal("At the end of your turn, [gold]Plan[/gold] a [gold]Sting[/gold].",
                     Face(new ProtoKkKurageBloom()));
        // No start-of-turn hook is left on the power.
        Assert.Null(typeof(KurageBloomPower).GetMethod(
            "AfterPlayerTurnStartLate",
            System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.Instance
            | System.Reflection.BindingFlags.DeclaredOnly));
        // The marker's turn end runs it, then Watatsumi's Grace.
        var end = Seq("KokomiTasteAudit", "TurnEnd");
        var bloom = end.FindIndex(c => c.Contains("KokomiCards.PlanJellyfish"));
        // Kokomi defence pass (2026-10-22): Stings and Wards don't count.
        var held = end.FindIndex(c => c.Contains("KokomiPlan.ChainPlansHeld"));
        Assert.True(bloom >= 0 && held > bloom, string.Join(" ", end));
        Assert.Contains("KokomiTasteAudit.TurnEnd",
                        Seq(nameof(ProtoBakeKuragePower), "BeforeSideTurnEnd"));
    }

    // ---- 3. Resolve of Watatsumi --------------------------------------------------

    [Fact]
    public void Resolve_of_watatsumi_adds_to_a_plans_hits_and_block()
    {
        var card = new ProtoKkResolveOfWatatsumi();
        Assert.Equal((CardType.Power, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(2, card.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(3, Upgraded<ProtoKkResolveOfWatatsumi>()
                            .DynamicVars["PowerAmount"].IntValue);
        Assert.Contains(Seq(nameof(ProtoKkResolveOfWatatsumi), "OnPlay"),
                        c => c.Contains("ResolveOfWatatsumiPower"));
        Assert.Equal(0, ResolveOfWatatsumiPower.Bonus(null));
        // Read in the one hit funnel and the three Block clauses.
        Assert.Contains(Seq("KokomiPlan", "Hit"),
                        c => c.Contains("ResolveOfWatatsumiPower.Bonus"));
        Assert.Equal(3, Seq("KokomiPlan", "ResolveOne")
                            .Count(c => c.Contains("ResolveOfWatatsumiPower.Bonus")));
    }

    // ---- 4. Coral Crash (and 8. Undertow) -------------------------------------------
    // `KokomiExpansionTests` and `Round16Tests` hold the clauses and the face.

    // ---- 5. Watatsumi's Grace -----------------------------------------------------

    [Fact]
    public void Watatsumis_grace_face()
    {
        var card = new ProtoKkWatatsumisGrace();
        Assert.Equal((CardRarity.Rare, 1), (card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal("At the end of your turn, gain {PowerAmount:diff()} [gold]Block[/gold] "
                   + "for each [gold]Plan[/gold] waiting. Stings and Wards don't count.",
                     Face(card));
        Assert.Null(typeof(WatatsumisGracePower).GetMethod(
            "AfterPreventingBlockClear",
            System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.Instance
            | System.Reflection.BindingFlags.DeclaredOnly));
    }

    // ---- 6. Sea's Reproach --------------------------------------------------------

    [Fact]
    public void Seas_reproach_reads_intent_after_the_mornings_plans()
    {
        Assert.True(typeof(UpgradeTwinPower).IsAssignableFrom(typeof(SeasReproachPower)));
        Assert.Equal((1, 0), SeasReproachPower.Payout(1, 0));
        Assert.Equal((2, 5), SeasReproachPower.Payout(2, 1));
        var signal = Seq("SeasReproachPower", "Signal");
        Assert.Contains(signal, c => c.Contains("PowerCmd.Apply<WeakPower>")
                                     || c.Contains("PowerCmd.Apply"));
        Assert.Contains(signal, c => c.Contains("ElementalHit.DealUnelemented"));
        var morning = Seq(nameof(ProtoBakeKuragePower), "AfterPlayerTurnStart");
        var resolve = morning.IndexOf("KokomiPlan.ResolveAll");
        var reproach = morning.IndexOf("SeasReproachPower.Signal");
        Assert.True(resolve >= 0 && reproach > resolve, string.Join(" ", morning));
        Assert.Equal("At the start of your turn, apply 1 [gold]Weak[/gold] to each enemy "
                   + "that intends to attack{IfUpgraded:show: and deal 5 damage|}.",
                     Face(new ProtoKkSeasReproach()));
    }

    // ---- 7. Suffocating Deep ------------------------------------------------------

    [Fact]
    public void Suffocating_deep_debuffs_each_attacker()
    {
        var card = new ProtoKkSuffocatingDeep();
        Assert.Equal((CardRarity.Rare, 2), (card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(2, card.DynamicVars["KkAmount"].IntValue);
        var calls = Seq("KokomiCards", "WeakVulnAttackers");
        // The intent read is a method group (`CurtainCallHooks.IntendsAttack`
        // in a `Where`), not a call the sequence lists.
        Assert.Equal(2, calls.Count(c => c.StartsWith("PowerCmd.Apply",
                                                      StringComparison.Ordinal)));
    }

    // ---- 9. Flotsam Surge ---------------------------------------------------------

    [Fact]
    public void Flotsam_surges_plan_hits_all_and_plans_a_sting()
    {
        var card = new ProtoKkFlotsamSurge();
        Assert.Equal((CardRarity.Uncommon, 1), (card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(new[] { KokomiPlan.Kind.Damage, KokomiPlan.Kind.PlanStings },
                     card.PlanClauses.Select(c => c.Kind).ToArray());
        Assert.Equal(new[] { 9, 1 }, card.PlanClauses.Select(c => c.Amount).ToArray());
        Assert.Equal(KokomiPlan.Aim.AllEnemies, card.PlanClauses[0].Aim);
        Assert.Equal(12, Upgraded<ProtoKkFlotsamSurge>().PlanClauses[0].Amount);
        Assert.Contains(Seq("KokomiPlan", "ResolveOne"),
                        c => c.Contains("KokomiCards.PlanJellyfish"));
    }

    // ---- 10. Riptide Ruin ---------------------------------------------------------

    [Fact]
    public void Riptide_ruin_counts_the_plans_carried_out_not_stings()
    {
        var card = new ProtoKkRiptideRuin();
        Assert.Equal((CardRarity.Rare, 2), (card.Rarity, card.EnergyCost.Canonical));
        Assert.Contains(Seq(nameof(ProtoKkRiptideRuin), "OnPlay"),
                        c => c.Contains("KokomiOverhaulLedger.get_ChainPlansThisTurn"));
    }
}
