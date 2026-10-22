using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI V3 (2026-10-18, <c>review/active/kokomi-cards-2026-10-18.md</c>
/// sec.6; [USER]: "Makes sense! ... let's do both."). Tideturn, Feint and
/// Turning Tide stop counting Plans that are Stings or Wards; Breakwater keeps
/// counting every Plan, and Shoal of Spears does again since its exemption
/// (2026-10-20, [USER]: "It's already a Rare."). And Unbroken
/// Tide: "Gain 8 [11] Block. Plan: If you lost no HP since you planned this,
/// deal 12 [16] Hydro damage to ALL enemies." Structural and pure pins (the
/// headless boundary); sim twin <c>tier0/tests/test_kokomi_v3_2026_10_18.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiV3Tests
{
    private const string Tail = ", not Stings or Wards.";

    /// <summary>The Kokomi text audit (2026-10-22, pick 2 (a)): the ruled
    /// spelling, its own sentence. Turning Tide keeps <see cref="Tail"/>:
    /// the sentence would take it past the 120 ceiling.</summary>
    private const string DontCount = ". Stings and Wards don't count.";

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

    private static KokomiPlan.Entry Plan(CardModel? source) =>
        new(source, Array.Empty<KokomiPlan.Planned>());

    // ---- 1. the three faces, word for word ----------------------------------------

    [Fact]
    public void The_three_faces_say_stings_and_wards_dont_count()
    {
        Assert.Equal(
            "Deal {CalculationBase:diff()} [gold]Hydro[/gold] damage, plus "
          + "{ExtraDamage:diff()} for each [gold]Plan[/gold] waiting" + DontCount
          + "{InCombat:\n(Deals {CalculatedDamage:diff()} damage)|}",
            Face(new ProtoKkTideturn()));
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Hydro[/gold] damage.\nOr "
          + "[gold]plan[/gold]: Deal {PlanDamage:diff()} [gold]Hydro[/gold] "
          + "damage for each [gold]Plan[/gold] carried out this turn" + DontCount,
            Face(new ProtoKkFeint()));
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Hydro[/gold] damage.\nOr "
          + "[gold]plan[/gold]: Deal {PlanDamage:diff()} [gold]Hydro[/gold] "
          + "damage to ALL enemies per [gold]Plan[/gold] carried out "
          + "this turn" + Tail,
            Face(new ProtoKkTurningTideChain()));
        // Shoal of Spears is exempt (2026-10-20): every Plan waiting.
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Hydro[/gold] damage to ALL enemies, "
          + "plus once more for each [gold]Plan[/gold] waiting."
          + "{InCombat:\n(Deals {TotalDamage:diff()} damage)|}",
            Face(new ProtoKkShoalOfSpears()));
        Assert.DoesNotContain("Stings", Face(new ProtoKkBreakwater()));
        // Battle Formation stopped counting them in the Kokomi finish pass
        // (2026-10-19, `KokomiFinishPassTests`).
    }

    // ---- 1. the counts --------------------------------------------------------------

    [Fact]
    public void Tideturn_reads_the_count_without_stings_or_wards_and_the_shoal_reads_all()
    {
        // Shoal of Spears, exempt since 2026-10-20: every Plan waiting.
        Assert.Contains(Il.Calls(Il.Method("ProtoKkShoalOfSpears", "OnPlay")),
                        c => c.Contains("KokomiPlan.PlansHeld"));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoKkShoalOfSpears", "OnPlay")),
            c => c.Contains("KokomiPlan.ChainPlansHeld"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ChainPlansHeld")),
                        c => c.Contains("KokomiRefounding.IsJellyfish"));
        // Breakwater keeps every Plan.
        var calls = Il.CallSequence(
            Il.Method("ProtoKkBreakwater", "get_CanonicalVars"));
        Assert.DoesNotContain(calls, c => c.Contains("ChainPlansHeld"));
    }

    [Fact]
    public void A_planned_sting_or_ward_is_not_a_chain_plan_and_a_real_plan_is()
    {
        Assert.True(KokomiRefounding.IsJellyfish(new ProtoKkSting()));
        Assert.True(KokomiRefounding.IsJellyfish(new ProtoKkWard()));
        Assert.False(KokomiRefounding.IsJellyfish(new ProtoKkFeint()));
        var queue = new[]
        {
            Plan(new ProtoKkSting()), Plan(new ProtoKkAmbush()),
            Plan(new ProtoKkWard()), Plan(new ProtoKkFeint()),
        };
        // Feint fourth in the queue: the Ambush and itself.
        Assert.Equal(2, KokomiPlan.ChainPlace(queue, 3, twice: false));
        // A Sting first, so Nereid's Ascension doubles nothing real.
        Assert.Equal(2, KokomiPlan.ChainPlace(queue, 3, twice: true));
        var realFirst = new[]
        {
            Plan(new ProtoKkAmbush()), Plan(new ProtoKkWard()),
            Plan(new ProtoKkFeint()),
        };
        Assert.Equal(3, KokomiPlan.ChainPlace(realFirst, 2, twice: true));
        Assert.Equal(1, KokomiPlan.ChainPlace(realFirst, 0, twice: true));
    }

    [Fact]
    public void The_ledger_counts_carry_outs_two_ways_and_rolls_both()
    {
        var ledger = new KokomiOverhaulLedger();
        ledger.RollTo(3);
        ledger.NotePlanCarryingOut(jellyfish: true);
        ledger.NotePlanCarryingOut(jellyfish: true);
        ledger.NotePlanCarryingOut();
        // Breakwater reads every carry-out; Feint, Turning Tide and (since
        // the Kokomi finish pass, 2026-10-19) Battle Formation the real ones.
        Assert.Equal(3, ledger.PlansCarriedOutThisTurn);
        Assert.Equal(1, ledger.ChainPlansThisTurn);
        ledger.RollTo(4);
        Assert.Equal((0, 0), (ledger.PlansCarriedOutThisTurn,
                              ledger.ChainPlansThisTurn));
        var entry = string.Join(" ", Il.CallSequence(
            Il.Method("KokomiPlan", "ResolveEntry")));
        Assert.Contains("KokomiRefounding.IsJellyfish", entry);
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "AskedFor")),
                        c => c.Contains("get_ChainPlansThisTurn"));
    }

    // ---- 2. Unbroken Tide -------------------------------------------------------------

    [Fact]
    public void Unbroken_tide_prints_the_paper()
    {
        var card = new ProtoKkUnbrokenTide();
        Assert.Equal((CardType.Skill, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold].\nOr [gold]plan[/gold]: "
          + "If you lost no HP since you planned this, deal "
          + "{PlanDamage:diff()} [gold]Hydro[/gold] damage to ALL enemies.",
            Face(card));
        Assert.Equal((8, 11), (card.DynamicVars["Block"].IntValue,
                               Upgraded<ProtoKkUnbrokenTide>()
                                   .DynamicVars["Block"].IntValue));
        Assert.Equal((12, 16), (card.DynamicVars["PlanDamage"].IntValue,
                                Upgraded<ProtoKkUnbrokenTide>()
                                    .DynamicVars["PlanDamage"].IntValue));
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.DamageIfNoHpLostSince, 12,
                      KokomiPlan.Aim.AllEnemies),
                     (clause.Kind, clause.Amount, clause.Aim));
    }

    [Fact]
    public void Unbroken_tide_fires_with_no_hp_lost_and_not_after_hp_was_lost()
    {
        var ledger = new KokomiOverhaulLedger();
        ledger.NoteHpLost(3);                  // before it was written
        var window = ledger.OpenWindow();
        // A fully blocked hit is no HP lost.
        ledger.NoteEnemyHit("1", blocked: 6, unblocked: 0, attack: true);
        Assert.False(ledger.HpLostSince(window));
        ledger.NoteHpLost(1);
        Assert.True(ledger.HpLostSince(window));
        // A later Plan opens on the new total.
        Assert.False(ledger.HpLostSince(ledger.OpenWindow()));
        // No window reads false.
        Assert.False(ledger.HpLostSince(null));
    }

    [Fact]
    public void Unbroken_tide_is_carried_out_off_its_window_and_fed_by_every_hp_loss()
    {
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("HpLostSince"));
        Assert.Contains(
            Il.Calls(Il.Method("ProtoBakeKuragePower", "AfterCurrentHpChanged")),
            c => c.Contains("NoteHpLost"));
    }

    [Fact]
    public void Unbroken_tide_is_in_her_pool_last_before_gorous_four()
    {
        var slice = Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();
        Assert.Equal(79, slice.Count);         // Gorou's four included
        Assert.EndsWith("ProtoKkUnbrokenTide", slice[^5]);
        Assert.EndsWith("ProtoKkTheShapeOfWater", slice[^6]);
    }
}
