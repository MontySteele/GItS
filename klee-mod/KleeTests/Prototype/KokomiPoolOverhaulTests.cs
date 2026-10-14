using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI POOL OVERHAUL (2026-10-13,
/// <c>review/active/kokomi-pool-overhaul-2026-10-13.md</c>, picks 1 (a) and
/// 2 (a); [USER]: "On Kokomi, I'm good with default on 1 and 2."). Eight
/// rewrites, six cuts and six new cards, and the readings: Chain counts the
/// Plan being carried out; "since you planned this" is a per-Plan window off
/// the ledger's running totals; Intent is read at landing; a reaction is the
/// card's or the Companion's own hit. Sim twin:
/// <c>tier0/tests/test_kokomi_pool_overhaul_2026_10_13.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPoolOverhaulTests
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

    private static string PowerFace(PowerModel power) =>
        ((ILocalizationProvider)power).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    private static List<string> Slice() =>
        Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    private static KokomiOverhaulLedger Ledger() => new();

    // ---- the pool -----------------------------------------------------------------

    [Theory]
    [InlineData("ProtoKkRiptideGuard", "ProtoKkTurningTideChain")]
    [InlineData("ProtoKkReserves", "ProtoKkBrineSpray")]
    // Jellyfish Current's slot is Kurage Vanguard's since the Kokomi review
    // r6 (2026-10-14, pick 2 (b); `KokomiReviewR6Tests`).
    [InlineData("ProtoKkBraceForTheTide", "ProtoKkKurageVanguard")]
    [InlineData("ProtoKkMoonsReflection", "ProtoKkPreparedRetreat")]
    [InlineData("ProtoKkCeremonialGarment", "ProtoKkBattleFormation")]
    [InlineData("ProtoKkWatatsumiResistance", "ProtoKkTurnabout")]
    public void Each_new_card_takes_the_cut_cards_place(string cut, string added)
    {
        var slice = Slice();
        Assert.Equal(78, slice.Count);
        Assert.DoesNotContain(cut, slice);
        Assert.Contains(added, slice);
        Assert.Null(typeof(ProtoKkSting).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated." + cut));
    }

    [Fact]
    public void The_six_new_cards_print_the_paper()
    {
        var tide = new ProtoKkTurningTideChain();
        Assert.Equal((CardType.Attack, CardRarity.Common, 1),
                     (tide.Type, tide.Rarity, tide.EnergyCost.Canonical));
        // The numbers pass (kokomi-review-r5-2026-10-14): Tide 9 [12] / Plan 5 [6],
        // Spray 8 [10], Retreat 8 [11], Snare Plan 4.
        Assert.Equal((9, 12), (Var<ProtoKkTurningTideChain>("Damage"),
                               Var<ProtoKkTurningTideChain>("Damage", true)));
        var chain = Assert.Single(tide.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.DamagePerPlanThisTurn, 5,
                      KokomiPlan.Aim.AllEnemies),
                     (chain.Kind, chain.Amount, chain.Aim));
        Assert.Equal(6, Assert.Single(
            Upgraded<ProtoKkTurningTideChain>().PlanClauses).Amount);

        var spray = new ProtoKkBrineSpray();
        Assert.Equal((CardType.Attack, CardRarity.Uncommon, 1),
                     (spray.Type, spray.Rarity, spray.EnergyCost.Canonical));
        Assert.Equal((8, 10), (Var<ProtoKkBrineSpray>("Damage"),
                              Var<ProtoKkBrineSpray>("Damage", true)));
        Assert.Equal(2, Var<ProtoKkBrineSpray>("KkAmount"));
        Assert.Contains("If it triggers an [gold]Elemental Reaction[/gold], "
                      + "add {KkAmount} [gold]Stings[/gold]", Face(spray));

        var retreat = new ProtoKkPreparedRetreat();
        Assert.Equal((CardType.Skill, CardRarity.Uncommon, 1),
                     (retreat.Type, retreat.Rarity,
                      retreat.EnergyCost.Canonical));
        Assert.Equal((8, 11), (Var<ProtoKkPreparedRetreat>("Block"),
                               Var<ProtoKkPreparedRetreat>("Block", true)));
        Assert.Equal((1, 2), (Var<ProtoKkPreparedRetreat>("PlanEnergy"),
                              Var<ProtoKkPreparedRetreat>("PlanEnergy", true)));
        Assert.IsType<MegaCrit.Sts2.Core.Localization.DynamicVars.EnergyVar>(
            retreat.DynamicVars["PlanEnergy"]);
        Assert.Equal(KokomiPlan.Kind.EnergyIfAttackedSince,
                     Assert.Single(retreat.PlanClauses).Kind);

        var turnabout = new ProtoKkTurnabout();
        Assert.Equal((CardType.Skill, CardRarity.Rare, 2),
                     (turnabout.Type, turnabout.Rarity,
                      turnabout.EnergyCost.Canonical));
        Assert.Contains(CardKeyword.Exhaust, turnabout.CanonicalKeywords);
        Assert.Equal(1, (int)Upgraded<ProtoKkTurnabout>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.False(turnabout is INowLineCard);
        var taken = Assert.Single(turnabout.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.DamageTakenSince,
                      KokomiPlan.Aim.AllEnemies), (taken.Kind, taken.Aim));

        // Jellyfish Current and Coordinated Tide left with the Kokomi
        // review r6 (2026-10-14, pick 2 (b)).
        var formation = new ProtoKkBattleFormation();
        Assert.Equal((CardType.Power, 1),
                     (formation.Type, formation.EnergyCost.Canonical));
        Assert.Equal(CardRarity.Rare, formation.Rarity);
        Assert.Contains(CardKeyword.Innate,
                        Upgraded<ProtoKkBattleFormation>().Keywords);
    }

    [Fact]
    public void The_rewrites_print_the_paper()
    {
        var kelp = Assert.Single(new ProtoKkKelpWall().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.DamageBlockedSince,
                      KokomiPlan.Aim.FrontEnemy), (kelp.Kind, kelp.Aim));
        // Kokomi review r6 (2026-10-14, item 12): "the Attack damage".
        Assert.Contains("Attack damage you blocked since you planned this",
                        Face(new ProtoKkKelpWall()));
        var field = Assert.Single(new ProtoKkReadTheField().PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DrawPileToHand, field.Kind);
        Assert.Contains(Seq("KokomiPlan", "DrawPileToHand"),
                        c => c.Contains("CardSelectCmd.FromCombatPile"));
        Assert.Equal("Whenever you trigger an [gold]Elemental "
                   + "Reaction[/gold], deal {PowerAmount:diff()} damage to "
                   + "ALL enemies.", Face(new ProtoKkGrandStrategist()));
        // Kokomi review r6 (2026-10-14, item 4): 6 [8].
        Assert.Equal((6, 8), (Var<ProtoKkGrandStrategist>("PowerAmount"),
                              Var<ProtoKkGrandStrategist>("PowerAmount", true)));
    }

    // ---- CHAIN --------------------------------------------------------------------

    [Fact]
    public void The_chain_count_rises_before_the_clauses_run_and_rolls_with_the_turn()
    {
        var entry = string.Join(" ", Seq("KokomiPlan", "ResolveEntry"));
        var count = entry.IndexOf("NotePlanCarryingOut", StringComparison.Ordinal);
        var resolve = entry.IndexOf("KokomiPlan.ResolveOne", StringComparison.Ordinal);
        Assert.True(count >= 0 && resolve > count, entry);
        var ledger = Ledger();
        ledger.RollTo(3);
        ledger.NotePlanCarryingOut();
        ledger.NotePlanCarryingOut();
        Assert.Equal(2, ledger.PlansCarriedOutThisTurn);
        ledger.RollTo(4);
        Assert.Equal(0, ledger.PlansCarriedOutThisTurn);
    }

    // ---- COUNTER ------------------------------------------------------------------

    [Fact]
    public void Each_plan_reads_its_own_window()
    {
        var ledger = Ledger();
        ledger.NoteEnemyHit("1", blocked: 4, unblocked: 2, attack: true);
        var first = ledger.OpenWindow();
        ledger.NoteEnemyHit("2", blocked: 5, unblocked: 4, attack: true);
        var second = ledger.OpenWindow();
        ledger.NoteEnemyHit("2", blocked: 3, unblocked: 0, attack: true);
        // A non-Attack hit is damage dealt her, not an attack or a block.
        ledger.NoteEnemyHit("3", blocked: 2, unblocked: 1, attack: false);

        Assert.Equal(8, ledger.BlockedSince(first));
        Assert.Equal(3, ledger.BlockedSince(second));
        Assert.Equal(9 + 3 + 3, ledger.TakenSince(first));
        Assert.Equal(3 + 3, ledger.TakenSince(second));
        Assert.Equal(new[] { "2" }, ledger.AttackersSince(first).ToArray());
        Assert.True(ledger.AttackedSince(second));
        var last = ledger.OpenWindow();
        Assert.False(ledger.AttackedSince(last));
        Assert.Empty(ledger.AttackersSince(last));
        // No window, nothing read.
        Assert.Equal(0, ledger.BlockedSince(null));
        Assert.Equal(0, ledger.TakenSince(null));
        Assert.False(ledger.AttackedSince(null));
    }

    [Fact]
    public void The_window_opens_when_written_and_the_hits_are_counted_on_the_marker()
    {
        Assert.Contains(Seq("KokomiPlan", "Schedule"),
                        c => c.Contains("OpenWindow"));
        Assert.Contains(Seq("ProtoBakeKuragePower", "AfterDamageReceived"),
                        c => c.Contains("NoteEnemyHit"));
        Assert.Contains(Seq("ProtoBakeKuragePower", "AfterDamageReceived"),
                        c => c.Contains("IsPoweredAttack"));
        // The Counter clauses read the entry's window, and Brine Sting's aim
        // reads its attackers.
        Assert.Contains(Seq("KokomiPlan", "AskedFor"),
                        c => c.Contains("BlockedSince"));
        Assert.Contains(Seq("KokomiPlan", "AskedFor"),
                        c => c.Contains("TakenSince"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("AttackedSince"));
    }

    // ---- INTENT -------------------------------------------------------------------

    [Fact]
    public void Undercurrent_snare_takes_strength_this_turn_from_the_attackers()
    {
        var snare = Assert.Single(new ProtoKkUndercurrentSnare().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.LoseStrengthThisTurn, 4,
                      KokomiPlan.Aim.EnemiesIntendingAttack),
                     (snare.Kind, snare.Amount, snare.Aim));
        Assert.True(typeof(TemporaryStrengthPower)
            .IsAssignableFrom(typeof(UndercurrentSnarePower)));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("PowerCmd.Apply"));
    }

    // ---- BATTLE FORMATION -----------------------------------------------------------

    [Fact]
    public void Battle_formation_pays_once_at_the_second_plan()
    {
        Assert.False(BattleFormationPower.Pays(1));
        Assert.True(BattleFormationPower.Pays(2));
        Assert.True(BattleFormationPower.Pays(3));
        Assert.Equal(1, BattleFormationPower.Draw);
        var ledger = Ledger();
        ledger.RollTo(1);
        Assert.True(ledger.Claim(BattleFormationPower.ClaimKey));
        Assert.False(ledger.Claim(BattleFormationPower.ClaimKey));
        Assert.Contains(Seq("KokomiRefounding", "OnCarriedOut"),
                        c => c.Contains("BattleFormationPower.OnCarriedOut"));
        Assert.Contains("{Amount:energyIcons()}",
                        PowerFace(new BattleFormationPower()));
    }

    // ---- REACTIONS -----------------------------------------------------------------

    [Fact]
    public void A_plan_lines_hit_is_credited_to_the_card_that_wrote_it()
    {
        Assert.Null(KokomiRefounding.CreditedHit);
        var sting = new ProtoKkSting();
        using (KokomiRefounding.CreditHits(sting))
        {
            Assert.Same(sting, KokomiRefounding.CreditedHit);
            using (KokomiRefounding.CreditHits(null))
            {
                Assert.Null(KokomiRefounding.CreditedHit);
            }
            Assert.Same(sting, KokomiRefounding.CreditedHit);
        }
        Assert.Null(KokomiRefounding.CreditedHit);
        Assert.Contains(Seq("KokomiPlan", "Hit"),
                        c => c.Contains("KokomiRefounding.CreditHits"));
    }

    [Fact]
    public void The_reaction_reader_counts_and_pays_the_four_readings()
    {
        var reads = Il.Calls(Il.Method("KokomiRefounding", "OnReaction"));
        Assert.Contains(reads, c => c.Contains("NoteReaction"));
        Assert.Contains(reads, c => c.Contains("ElementalHit.DealUnelemented"));
        Assert.Contains(reads, c => c.Contains("IsCompanionHit"));
        Assert.Contains(reads, c => c.Contains("KokomiCards.AddJellyfish"));
        // Grand Strategist no longer asks whether a Plan is being carried out.
        Assert.DoesNotContain(reads, c => c.Contains("IsCarryingOut"));
        // The one site a reaction resolves hands the card over.
        Assert.Contains(Seq("CompanionOverhaulReactions", "Note"),
                        c => c.Contains("KokomiRefounding.OnReaction"));
        Assert.False(KokomiRefounding.IsCompanionHit(null));
        Assert.False(KokomiRefounding.IsCompanionHit(new ProtoKkSting()));
        Assert.True(KokomiRefounding.IsCompanionHit(
            new ProtoMiShinobuThundergrust()));
        var ledger = Ledger();
        ledger.NoteReaction();
        ledger.NoteReaction();
        Assert.Equal(2, ledger.ReactionsThisCombat);
    }

    [Fact]
    public void Jellyfish_current_and_coordinated_tide_say_what_they_pay()
    {
        Assert.Contains("Whenever a [gold]Sting[/gold] triggers",
                        PowerFace(new JellyfishCurrentPower()));
        Assert.Contains("Whenever a [gold]Companion[/gold] triggers",
                        PowerFace(new CoordinatedTidePower()));
        Assert.Contains("Whenever you trigger",
                        PowerFace(new GrandStrategistPower()));
    }

    [Fact]
    public void Brine_spray_reads_its_own_hit_for_the_reaction()
    {
        var play = Seq("ProtoKkBrineSpray", "OnPlay");
        Assert.Contains(play, c => c.Contains("ReactionEffects.get_TotalResolved"));
        Assert.Contains(play, c => c.Contains("KokomiCards.ShoalCall"));
    }

    [Fact]
    public void All_streams_reads_the_reactions_this_combat()
    {
        var card = new ProtoKkAllStreamsFlow();
        Assert.Equal((10, 5), (card.DynamicVars.CalculationBase.IntValue,
                              card.DynamicVars.ExtraDamage.IntValue));
        Assert.Contains("for each [gold]Elemental Reaction[/gold] you "
                      + "triggered this combat", Face(card));
    }

    // ---- THE LIVE LINES -------------------------------------------------------------

    [Fact]
    public void A_counter_or_chain_plans_live_number_is_the_strips_caption()
    {
        Assert.Equal("Deals 14", KokomiPlan.StripCaption(
            false, false, null, 0, false, KokomiPlan.LiveDeals(14)));
        Assert.Equal("No attack yet", KokomiPlan.StripCaption(
            true, false, null, 0, false, KokomiPlan.NoAttackYet));
        // The flip and Tide Wall's total still come first.
        Assert.Equal("Block 9", KokomiPlan.StripCaption(
            false, false, 9, 0, false, "Deals 3"));
        // No live line: the old captions, unchanged.
        Assert.Null(KokomiPlan.StripCaption(false, false, null, 0, false));
        Assert.Contains(Seq("KokomiPlanStrip", "Paint"),
                        c => c.Contains("KokomiPlan.LiveLine"));
        Assert.Contains("live", Il.Strings(Il.Method("KokomiPlan", "QueueRow")));
    }
}
