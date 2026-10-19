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
    public void Her_offer_is_seventy_eight_and_the_coop_tier_is_five()
    {
        var slice = Cards("KokomiOverhaulRoster", "Slice");
        // 78 since pool completion; since the re-founding (2026-10-12) it
        // ends with Gorou's four, her own cards. 79 with Kokomi v3
        // (2026-10-18).
        Assert.Equal(79, slice.Count);
        Assert.Equal(new[]
            {
                "ProtoMiGorouInuzaka", "ProtoMiGorouWarBanner",
                "ProtoMiGorouJuuga", "ProtoMiGorouCrystalCollapse",
            },
            slice.Skip(75).ToArray());
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

        // (Kurage School and Patient Tide left in the re-founding, 2026-10-12;
        // Spring Tide in the jellyfish build, 2026-10-12.)

        // The Rare pass (2026-10-04): 4 [5] a hit; since the re-founding one
        // hit per Plan waiting. Kokomi round 2 (2026-10-12): 5 [6].
        Assert.Equal(7, new ProtoKkShoalOfSpears().DynamicVars["Damage"].IntValue);   // the pool sweep, 2026-10-18
        Assert.Equal(9, Upgraded<ProtoKkShoalOfSpears>().DynamicVars["Damage"].IntValue);
        // The Kokomi level pass (2026-10-12): Sea's Reproach 5 [7] at 1
        // Energy on both faces.
        Assert.Equal(1, new ProtoKkSeasReproach().EnergyCost.Canonical);
        Assert.Equal(1, UpCost<ProtoKkSeasReproach>());
        Assert.Equal(5, new ProtoKkSeasReproach().DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(7, Upgraded<ProtoKkSeasReproach>().DynamicVars["PowerAmount"].IntValue);
        // (Watatsumi Resistance left with the Kokomi pool overhaul,
        // 2026-10-13.)
        Assert.Equal(8, new ProtoKkKuragesMercy().DynamicVars["KkAmount"].IntValue);
        Assert.Equal(12, Upgraded<ProtoKkKuragesMercy>().DynamicVars["KkAmount"].IntValue);
        Assert.True(Exhausts(new ProtoKkKuragesMercy()));
        Assert.Contains("[gold]Mend[/gold]", Face(new ProtoKkKuragesMercy()));
    }

    [Fact]
    public void Body_slam_is_priced_once()
    {
        // Paper sec.6: Tidal Rebuke keeps no Exhaust, Noelle's Sweeping Time
        // upgrades to cost 1. The Kokomi level pass (2026-10-12): Coral Crash
        // is Body Slam's price, 1 [0], and the "+4" upgrade went.
        var crash = new ProtoKkCoralCrash();
        Assert.Equal((CardRarity.Common, 1), (crash.Rarity, crash.EnergyCost.Canonical));
        Assert.Equal(0, UpCost<ProtoKkCoralCrash>());
        Assert.Equal(0m, crash.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(0m, Upgraded<ProtoKkCoralCrash>()
                             .DynamicVars.CalculationBase.BaseValue);
        var rebuke = new ProtoKkTidalRebuke();
        // The Kokomi level pass (2026-10-12): 2 [1], Noelle's price, and Retain.
        Assert.Equal((CardRarity.Rare, 2), (rebuke.Rarity, rebuke.EnergyCost.Canonical));
        Assert.Equal(1, UpCost<ProtoKkTidalRebuke>());
        Assert.Contains(CardKeyword.Retain, rebuke.CanonicalKeywords);
        Assert.False(Exhausts(rebuke));
        Assert.Equal(TargetType.AllEnemies, rebuke.TargetType);
        Assert.Equal(1, UpCost<ProtoMcNoelleSweepingTime>());
    }

    // ---- Kokomi: the rules ------------------------------------------------

    [Fact]
    public void A_card_she_is_handed_exhausts()
    {
        // The Rare pass (2026-10-04), carried by the re-founding (2026-10-12):
        // a card she is handed Exhausts when played, as a Shiv does. The
        // jellyfish cards print it (Ethereal too); a generated Companion is
        // given both by the one helper.
        foreach (var card in new CardModel[] { new ProtoKkSting(), new ProtoKkWard() })
        {
            Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
            Assert.Contains(CardKeyword.Ethereal, card.CanonicalKeywords);
        }
        var generate = Seq("KokomiCompanionPlan", "Generate");
        Assert.Equal(2, generate.Count(c => c.Contains("AddKeyword")));
    }

    [Fact]
    public void Spring_tide_left_with_its_mid_turn_drain()
    {
        // The jellyfish build (2026-10-12) cut Spring Tide; its verb and
        // the mid-turn drain went with it.
        Assert.Null(typeof(KokomiCards).GetMethod("SpringTide"));
        Assert.Null(typeof(KokomiPlan).GetMethod("ResolveAllNow"));
        Assert.Null(typeof(KokomiCards).Assembly
            .GetType("KleeMod.Cards.Prototype.Generated.ProtoKkSpringTide"));
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
    public void Watatsumi_resistance_adds_a_sting_per_companion_written()
    {
        // The re-founding (2026-10-12): paid on WRITING a Companion, in
        // Stings, from the one place a Plan is written.
        Assert.Null(typeof(WatatsumiResistancePower).GetMethod(
            "AfterCardPlayed", HeadlessGame.All
            | System.Reflection.BindingFlags.DeclaredOnly));
        var written = Seq("KokomiRefounding", "OnWritten");
        Assert.Contains(written, c => c.Contains("WatatsumiResistancePower"));
        Assert.Contains(written, c => c.Contains("KokomiCards.AddJellyfish"));
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
        Assert.DoesNotContain(Seq("ProtoKkMasterstroke", "OnPlay"),
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
