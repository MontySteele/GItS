using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// POOL COMPLETION (2026-10-01, review/active/pool-completion-2026-10-01.md,
/// all picks ruled at the defaults). Kokomi's one Common, seven Rares and two
/// multiplayer cards; Furina's three Uncommons and three Rares; the Body Slam
/// repricing; and each kit's second Ancient (game-side only, so pinned here
/// alone). What awaits a command is pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_pool_completion.py</c>. Readings: the provenance note,
/// "Pool completion, 2026-10-01".
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class PoolCompletionTests : IDisposable
{

    public PoolCompletionTests()
    {
    }

    public void Dispose()
    {
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static int UpCost<T>() where T : CardModel, new() =>
        (int)Upgraded<T>().EnergyCost.GetWithModifiers(CostModifiers.None);

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static List<string> Cards(string type, string method) =>
        Seq(type, method)
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    private static bool Exhausts(CardModel card) =>
        card.CanonicalKeywords.Contains(CardKeyword.Exhaust);

    // ---- Kokomi: the offer ------------------------------------------------

    [Fact]
    public void Her_offer_is_seventy_eight_with_the_eight_last()
    {
        var slice = Cards("KokomiOverhaulRoster", "Slice");
        // The status batch (2026-10-01): seven cut ahead, seven appended.
        Assert.Equal(78, slice.Count);
        Assert.Equal(new[]
            {
                "ProtoKkTidalScreen", "ProtoKkSpringTide", "ProtoKkKurageSchool",
                "ProtoKkShoalOfSpears", "ProtoKkPatientTide",
                "ProtoKkSeasReproach", "ProtoKkTidalRebuke",
                "ProtoKkWatatsumiResistance",
            },
            slice.Skip(63).Take(8).ToArray());
        var multiplayer = Cards("KokomiOverhaulRoster", "MultiplayerSlice");
        Assert.Equal(5, multiplayer.Count);
        Assert.Equal(new[] { "ProtoKkTacticalRelay", "ProtoKkKuragesMercy" },
                     multiplayer.Skip(3).ToArray());
        Assert.Equal(CardMultiplayerConstraint.MultiplayerOnly,
                     new ProtoKkTacticalRelay().MultiplayerConstraint);
        Assert.Equal(CardMultiplayerConstraint.MultiplayerOnly,
                     new ProtoKkKuragesMercy().MultiplayerConstraint);
    }

    [Fact]
    public void The_new_kokomi_rows_print_the_papers_numbers()
    {
        var screen = new ProtoKkTidalScreen();
        Assert.Equal((CardRarity.Common, 1, 7),
                     (screen.Rarity, screen.EnergyCost.Canonical,
                      screen.DynamicVars.Block.IntValue));
        Assert.Equal(10, Upgraded<ProtoKkTidalScreen>().DynamicVars.Block.IntValue);

        foreach (var (card, cost) in new (CardModel, int)[]
                 {
                     (new ProtoKkSpringTide(), 1), (new ProtoKkKurageSchool(), 1),
                 })
        {
            Assert.Equal(CardRarity.Rare, card.Rarity);
            Assert.Equal(cost, card.EnergyCost.Canonical);
            Assert.True(Exhausts(card));
        }
        Assert.Equal(0, UpCost<ProtoKkSpringTide>());
        Assert.Equal(0, UpCost<ProtoKkKurageSchool>());

        Assert.Equal(4, new ProtoKkShoalOfSpears().DynamicVars["ExtraDamage"].IntValue);
        Assert.Equal(5, Upgraded<ProtoKkShoalOfSpears>().DynamicVars["ExtraDamage"].IntValue);
        Assert.Equal(2, new ProtoKkPatientTide().DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(3, Upgraded<ProtoKkPatientTide>().DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(2, new ProtoKkSeasReproach().EnergyCost.Canonical);
        Assert.Equal(1, UpCost<ProtoKkSeasReproach>());
        Assert.Equal(0, UpCost<ProtoKkWatatsumiResistance>());
        Assert.Equal(8, new ProtoKkKuragesMercy().DynamicVars["KkAmount"].IntValue);
        Assert.Equal(12, Upgraded<ProtoKkKuragesMercy>().DynamicVars["KkAmount"].IntValue);
        Assert.True(Exhausts(new ProtoKkKuragesMercy()));
        Assert.Contains("[gold]Mend[/gold]", Face(new ProtoKkKuragesMercy()));
    }

    [Fact]
    public void Body_slam_is_priced_once()
    {
        // Paper sec.6: Coral Crash is Body Slam exactly, Tidal Rebuke keeps
        // no Exhaust, Noelle's Sweeping Time upgrades to cost 1.
        var crash = new ProtoKkCoralCrash();
        Assert.Equal((CardRarity.Common, 1), (crash.Rarity, crash.EnergyCost.Canonical));
        Assert.Equal(0, UpCost<ProtoKkCoralCrash>());
        var rebuke = new ProtoKkTidalRebuke();
        Assert.Equal((CardRarity.Rare, 2), (rebuke.Rarity, rebuke.EnergyCost.Canonical));
        Assert.Equal(1, UpCost<ProtoKkTidalRebuke>());
        Assert.False(Exhausts(rebuke));
        Assert.Equal(TargetType.AllEnemies, rebuke.TargetType);
        Assert.Equal(1, UpCost<ProtoMcNoelleSweepingTime>());
    }

    // ---- Kokomi: the rules ------------------------------------------------

    [Fact]
    public void Spring_tide_drains_the_whole_queue_mid_turn()
    {
        Assert.Contains(Seq("ProtoKkSpringTide", "OnPlay"),
                        c => c.Contains("KokomiCards.SpringTide"));
        Assert.Contains(Seq("KokomiCards", "SpringTide"),
                        c => c.Contains("KokomiPlan.ResolveAllNow"));
        var now = Seq("KokomiPlan", "ResolveAllNow");
        var clear = now.FindIndex(c => c.Contains("List`1.Clear"));
        var drain = now.FindIndex(c => c.Contains("KokomiPlan.Drain"));
        Assert.True(clear >= 0 && drain > clear,
                    "the queue is emptied before the first clause runs");
    }

    [Fact]
    public void Kurage_school_copies_zero_cost_plan_cards_only()
    {
        Assert.True(KokomiCards.IsZeroCostPlan(new ProtoKkNip()));
        Assert.False(KokomiCards.IsZeroCostPlan(new ProtoKkAmbush()));
        Assert.False(KokomiCards.IsZeroCostPlan(new ProtoKkSaltInTheWound()));
        Assert.False(KokomiCards.IsZeroCostPlan(null));
        var calls = Seq("KokomiCards", "KurageSchool");
        Assert.Contains(calls, c => c.Contains("CloneCard"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
    }

    [Fact]
    public void Shoal_of_spears_reads_the_plans_written_this_turn()
    {
        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi();
        var ledger = KokomiOverhaulLedger.For(seat.Creature);
        ledger.NotePlanWritten();
        ledger.NotePlanWritten();
        Assert.Equal(2, ledger.PlansWrittenThisTurn);
        ledger.RollTo(99);
        Assert.Equal(0, ledger.PlansWrittenThisTurn);
        Assert.Contains(Seq("KokomiPlan", "Schedule"),
                        c => c.Contains("KokomiOverhaulLedger.NotePlanWritten"));
    }

    [Theory]
    [InlineData(0, 2, 0)]
    [InlineData(1, 2, 1)]
    [InlineData(5, 2, 2)]
    [InlineData(5, 3, 3)]
    [InlineData(4, 0, 0)]
    public void Patient_tide_keeps_up_to_its_cap(int unspent, int cap, int kept)
    {
        Assert.Equal(kept, PatientTidePower.Kept(unspent, cap));
    }

    [Fact]
    public void Patient_tide_banks_at_turn_end_and_pays_after_the_refill()
    {
        Assert.Contains(Seq("PatientTidePower", "AfterPlayerTurnStart"),
                        c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.Contains(Seq("PatientTidePower", "BeforeSideTurnEnd"),
                        c => c.Contains("PatientTidePower.Kept"));
    }

    [Fact]
    public void Seas_reproach_pays_on_her_weak_and_vulnerable_with_hydro()
    {
        Assert.False(SeasReproachPower.Pays(null, 1m, null, null));
        var calls = Seq("SeasReproachPower", "AfterPowerAmountChanged");
        var pays = calls.FindIndex(c => c.Contains("SeasReproachPower.Pays"));
        var hit = calls.FindIndex(c => c.Contains("ElementalHit.Deal"));
        Assert.True(pays >= 0 && hit > pays);
    }

    [Fact]
    public void Watatsumi_resistance_adds_a_nip_per_companion_play()
    {
        var calls = Seq("WatatsumiResistancePower", "AfterCardPlayed");
        Assert.Contains(calls, c => c.Contains("ProtoKkNip"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
    }

    [Fact]
    public void Tactical_relay_plans_energy_and_an_upgraded_draw_for_each_player()
    {
        var card = new ProtoKkTacticalRelay();
        var clauses = card.PlanClauses;
        Assert.Equal(new[] { KokomiPlan.Kind.EachPlayerEnergy,
                             KokomiPlan.Kind.EachPlayerDraw },
                     clauses.Select(c => c.Kind).ToArray());
        Assert.Equal(new[] { 1, 0 }, clauses.Select(c => c.Amount).ToArray());
        Assert.Equal(new[] { 1, 1 },
                     Upgraded<ProtoKkTacticalRelay>().PlanClauses
                         .Select(c => c.Amount).ToArray());
    }

    [Fact]
    public void Kurages_mercy_mends_each_player_through_the_one_rule()
    {
        var calls = Seq("KokomiCards", "KuragesMercy");
        Assert.Contains(calls, c => c.Contains("KokomiPlan.EachPlayer"));
        Assert.Contains(calls, c => c.Contains("KokomiRules.Mend"));
    }

    // ---- Kokomi: Divine Strategy -----------------------------------------

    [Fact]
    public void A_card_with_a_now_line_asks_divine_strategy_and_a_plan_only_one_does_not()
    {
        Assert.Contains(Seq("ProtoKkAmbush", "OnPlay"),
                        c => c.Contains("DivineStrategyPower.NowLine"));
        Assert.Contains(Seq("ProtoKkTidalScreen", "OnPlay"),
                        c => c.Contains("DivineStrategyPower.NowLine"));
        Assert.DoesNotContain(Seq("ProtoKkNip", "OnPlay"),
                              c => c.Contains("DivineStrategyPower"));
        // Written first, then asked.
        var ambush = Seq("ProtoKkAmbush", "OnPlay");
        Assert.True(ambush.FindIndex(c => c.Contains("KokomiPlan.Schedule"))
                    < ambush.FindIndex(c => c.Contains("DivineStrategyPower.NowLine")));
    }

    [Fact]
    public void Divine_strategy_claims_its_once_only_after_finding_an_aim()
    {
        Assert.Null(DivineStrategyPower.NowLine(null!, null,
                                                DivineStrategyPower.Aim.None));
        var calls = Seq("DivineStrategyPower", "NowLine");
        var aim = calls.FindIndex(c => c.Contains("KokomiPlan.FrontEnemy"));
        var claim = calls.FindIndex(c => c.Contains("ClaimOncePerTurn"));
        Assert.True(aim >= 0 && claim > aim);
    }

    // ---- Furina -----------------------------------------------------------
    //
    // The pool completion's six Furina rows went with the v2 Stage (the
    // Salon's Tab, 2026-10-05) but Interval Bell, which the slice keeps with
    // its v2 text.

    [Fact]
    public void Interval_bells_price_moves_in_the_gate_and_the_payment()
    {
        var calls = Seq("ProtoFsIntervalBell", "OnPlay");
        Assert.Contains(calls, c => c.Contains("FurinaStage.CanSpend"));
        Assert.Contains(calls, c => c.Contains("FurinaStage.Spend"));
        Assert.Contains(calls, c => c.Contains("get_IsUpgraded"));
        Assert.Equal(0, new ProtoFsIntervalBell().EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, new ProtoFsIntervalBell().Rarity);
    }

    /// <summary>The loop fix (2026-10-04): Interval Bell's Spend mode gains
    /// its Energy NEXT turn, through the game's EnergyNextTurnPower. Sim
    /// twin: <c>tier0/tests/test_furina_loop_probe.py</c>.</summary>
    [Fact]
    public void Interval_bells_energy_comes_next_turn()
    {
        var calls = Seq("ProtoFsIntervalBell", "OnPlay");
        Assert.Contains(calls, c => c.Contains("FurinaStage.EnergyNextTurn"));
        Assert.DoesNotContain(calls, c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.Contains(Seq("FurinaStage", "EnergyNextTurn"),
                        c => c.Contains("PowerCmd.Apply")
                             && c.Contains("EnergyNextTurnPower"));
        Assert.Contains("gain 1 [gold]Energy[/gold] next turn instead",
                        Face(new ProtoFsIntervalBell()));
        Assert.All(((IModalCard)Upgraded<ProtoFsIntervalBell>()).ModeLabels
                       .Skip(1),
                   l => Assert.EndsWith("Energy[/gold] next turn instead", l));
    }

    [Fact]
    public void A_chosen_spend_is_free_once_under_center_of_attention()
    {
        Assert.False(CenterOfAttentionPower.Covers(null));
        var spend = Seq("FurinaStage", "Spend");
        var claim = spend.FindIndex(c => c.Contains("CenterOfAttentionPower.TryClaim"));
        var pay = spend.FindIndex(c => c.Contains("StageDirector.Spend"));
        Assert.True(claim >= 0 && pay > claim);
        Assert.DoesNotContain(Seq("FurinaStage", "CanSpend"),
                              c => c.Contains("CenterOfAttentionPower.Covers"));
    }

    // ---- the three Ancients ----------------------------------------------

    [Fact]
    public void Each_kit_has_a_second_ancient_that_installs_its_power()
    {
        foreach (var (card, cost, power) in new (CardModel, int, string)[]
                 {
                     (new AlicesMasterpiece(), 3, "AlicesMasterpiecePower"),
                     (new DivineStrategy(), 2, "DivineStrategyPower"),
                     (new CenterOfAttention(), 2, "CenterOfAttentionPower"),
                 })
        {
            Assert.Equal(CardRarity.Ancient, card.Rarity);
            Assert.Equal(CardType.Power, card.Type);
            Assert.Equal(cost, card.EnergyCost.Canonical);
            Assert.Contains(Seq(card.GetType().Name, "OnPlay"),
                            c => c.Contains(power));
        }
        Assert.Equal(2, UpCost<AlicesMasterpiece>());
        Assert.Equal(1, UpCost<DivineStrategy>());
        Assert.Equal(1, UpCost<CenterOfAttention>());
        Assert.Contains("AlicesMasterpiece", Cards("RosterAncientCards", "get_Klee"));
        Assert.Contains("DivineStrategy", Cards("RosterAncientCards", "get_Kokomi"));
        Assert.Contains("CenterOfAttention", Cards("RosterAncientCards", "get_Furina"));
    }

    [Theory]
    [InlineData(0, 0)]
    [InlineData(1, 0)]
    [InlineData(2, 1)]
    [InlineData(7, 3)]
    [InlineData(12, 6)]
    public void Alices_masterpiece_leaves_half_rounded_down(int size, int half)
    {
        Assert.Equal(half, AlicesMasterpiecePower.Remnant(size));
    }

    [Fact]
    public void Every_explosion_asks_alices_masterpiece_after_the_hit()
    {
        var explode = Seq("ProtoBombPower", "Explode");
        var note = explode.FindIndex(c => c.Contains("NoteExplosion"));
        var remain = explode.FindIndex(c => c.Contains("AlicesMasterpiecePower.Remain"));
        Assert.True(note >= 0 && remain > note);
        Assert.Contains(Seq("AlicesMasterpiecePower", "Remain"),
                        c => c.Contains("ProtoBombPower.Place"));
    }
}
