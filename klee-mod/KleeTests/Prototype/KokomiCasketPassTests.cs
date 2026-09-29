using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE CASKET PASS (2026-09-28). The Tamakushi Casket counts the Plans the
/// Bake-Kurage carries out; Open the Casket turns the count into Strength;
/// Feint and Sango Isshin read the turn's carry-outs; thirteen rows join the
/// offer and six leave it.
///
/// [USER], in his words: "an artifact that grants / tracks an alternative
/// energy that builds by 1 for every Plan played, and adds one 0-cost Retain /
/// Exhaust card that converts that energy into Strength." Counting is "when
/// it's carried out"; "1 strength per point seems fine"; "the casket keeps
/// counting."
///
/// The ledger arithmetic runs for real on a headless seat; anything that
/// awaits a command (the Strength, the hand move, the drain) is pinned off
/// the compiled methods and their order. Sim twin:
/// <c>tier0/tests/test_kokomi_casket_pass.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiCasketPassTests : IDisposable
{
    // The arm switch is one static; the rules below are the arm's, so they
    // run with it on and put it back (the shipped-kits build ships it off).
    private readonly bool _kokomi = KokomiOverhaul.Enabled;

    public KokomiCasketPassTests() => KokomiOverhaul.Enabled = true;

    public void Dispose() => KokomiOverhaul.Enabled = _kokomi;

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", HeadlessGame.All)!.GetValue(card)!)
        .ToList();

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- A. the relic ------------------------------------------------------

    [Fact]
    public void The_casket_counts_one_per_carry_out_while_she_holds_it()
    {
        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi().WithRelic<TamakushiCasket>();
        Assert.Equal(0, KokomiOverhaulLedger.For(seat.Creature).CasketCount);

        TamakushiCasket.NoteCarriedOut(seat.Creature);
        TamakushiCasket.NoteCarriedOut(seat.Creature);
        Assert.Equal(2, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
        Assert.Equal(1, KokomiOverhaulLaw.CasketPerPlan);

        // A Kokomi without the relic adds nothing: it is the relic's sentence.
        KokomiOverhaulLedger.ResetAll();
        var bare = Seat.Kokomi();
        TamakushiCasket.NoteCarriedOut(bare.Creature);
        Assert.Equal(0, KokomiOverhaulLedger.For(bare.Creature).CasketCount);
    }

    [Fact]
    public void The_count_is_added_once_per_carry_out_so_a_doubled_plan_adds_twice()
    {
        // `ResolveEntry` is one CARRY-OUT (the drain calls it `times` times for
        // Second Wave and Nereid's Ascension), and the relic's add sits in it
        // beside Sango Isshin's fact -- not in the drain, which is once per
        // ENTRY.
        var entry = Seq("KokomiPlan", "ResolveEntry");
        var fact = entry.FindIndex(c => c.Contains("NotePlanCarriedOut"));
        var add = entry.FindIndex(c => c.Contains("TamakushiCasket.NoteCarriedOut"));
        Assert.True(fact >= 0 && add > fact);
        Assert.DoesNotContain(Seq("KokomiPlan", "Drain"),
                              c => c.Contains("TamakushiCasket.NoteCarriedOut"));
        // And the ledger's per-turn count moves with each carry-out too.
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(Seat.Kokomi().Creature);
        ledger.RollTo(2);
        ledger.NotePlanCarriedOut();
        ledger.NotePlanCarriedOut();
        Assert.Equal(2, ledger.PlansCarriedOutThisTurn);
        ledger.RollTo(3);
        Assert.Equal(0, ledger.PlansCarriedOutThisTurn);
    }

    [Fact]
    public void The_casket_empties_on_open_and_keeps_counting()
    {
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(Seat.Kokomi().Creature);
        ledger.RollTo(1);
        ledger.AddToCasket(3);
        Assert.Equal(3, ledger.EmptyCasket());
        Assert.Equal(0, ledger.CasketCount);
        ledger.AddToCasket(1);
        Assert.Equal(1, ledger.CasketCount);
        // The turn roll never touches it: the count is per combat.
        ledger.RollTo(2);
        Assert.Equal(1, ledger.CasketCount);
        // Nothing takes it down but the open.
        ledger.AddToCasket(-5);
        Assert.Equal(1, ledger.CasketCount);
        ledger.DoubleCasket();
        Assert.Equal(2, ledger.CasketCount);
    }

    [Fact]
    public void The_relic_face_the_token_and_the_counter()
    {
        var face = string.Concat(Il.Strings(
            Il.Method("TamakushiCasket", "get_Localization")));
        Assert.Contains("[gold]Open the Casket[/gold] in hand", face);
        Assert.Contains(" carries out adds ", face);
        Assert.DoesNotContain("debuff", face);
        // The debuff strike is gone.
        Assert.Null(typeof(TamakushiCasket).GetMethod("Strike", HeadlessGame.All));
        // The token is dealt before the first hand draw, RadiantPearl's site.
        var deal = Il.Calls(Il.Method("TamakushiCasket", "BeforeHandDraw"));
        Assert.Contains(deal, c => c.Contains("CreateCard"));
        Assert.Contains(deal, c => c.Contains("CardPileCmd.AddGeneratedCardsToCombat"));
        // The count is on the icon, the base game's counter idiom.
        Assert.Contains(Il.Calls(Il.Method("TamakushiCasket", "get_DisplayAmount")),
                        c => c.Contains("get_CasketCount"));
        // The companion slot is kept.
        Assert.NotNull(typeof(TamakushiCasket).GetMethod(
            "TryModifyCardRewardOptions", HeadlessGame.All
            | System.Reflection.BindingFlags.DeclaredOnly));
    }

    // ---- B. Open the Casket -----------------------------------------------

    [Fact]
    public void Open_the_casket_is_a_zero_cost_retain_exhaust_token()
    {
        var card = new OpenTheCasket();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Token, card.Rarity);
        Assert.Contains(CardKeyword.Retain, card.Keywords);
        Assert.Contains(CardKeyword.Exhaust, card.Keywords);
        Assert.Equal("Gain [gold]Strength[/gold] equal to the [gold]Casket[/gold]'s "
                   + "count, then empty it.", Face(card));
        // In no pool: the offer is the Slice, and the token is not in it.
        Assert.DoesNotContain(Seq("KokomiOverhaulRoster", "Slice"),
                              c => c.Contains("OpenTheCasket"));
    }

    [Fact]
    public void Opening_empties_first_and_grants_strength_equal_to_the_count()
    {
        Assert.Contains(Il.Calls(Il.Method("OpenTheCasket", "OnPlay")),
                        c => c.Contains("KokomiOverhaulKit.OpenCasket"));
        var open = Seq("KokomiOverhaulKit", "OpenCasket");
        var empty = open.FindIndex(c => c.Contains("EmptyCasket"));
        var strength = open.FindIndex(c => c.Contains("PowerCmd.Apply"));
        Assert.True(empty >= 0 && strength > empty);
        Assert.Equal(1, KokomiOverhaulLaw.CasketStrengthPerPoint);
    }

    // ---- C. the re-keyed payoffs ------------------------------------------

    [Fact]
    public void Feint_is_four_plus_three_per_carry_out_and_plans_vulnerable()
    {
        var card = new ProtoKkFeint();
        Assert.Equal(4m, Var(card, "CalculationBase"));
        Assert.Equal(3m, Var(card, "ExtraDamage"));
        var up = Upgraded<ProtoKkFeint>();
        Assert.Equal(6m, Var(up, "CalculationBase"));
        Assert.Equal(3m, Var(up, "ExtraDamage"));
        Assert.Equal((KokomiPlan.Kind.ApplyVulnerable, 1),
                     (card.PlanClauses.Single().Kind, card.PlanClauses.Single().Amount));
        Assert.Equal(2, up.PlanClauses.Single().Amount);
    }

    [Fact]
    public void Sango_isshin_is_eight_plus_six_to_all_per_carry_out()
    {
        // 2026-09-29: a base of 8, so the Rare is not dead on turn 1 or after
        // a turn with no Plans. 10, plus 8 per Plan, upgraded.
        var card = new ProtoKkSangoIsshin();
        var up = Upgraded<ProtoKkSangoIsshin>();
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Equal(8m, Var(card, "CalculationBase"));
        Assert.Equal(6m, Var(card, "ExtraDamage"));
        Assert.Equal(10m, Var(up, "CalculationBase"));
        Assert.Equal(8m, Var(up, "ExtraDamage"));
    }

    // ---- D, E. the numbers ------------------------------------------------

    [Fact]
    public void The_moved_numbers()
    {
        Assert.Equal(CardRarity.Uncommon, new ProtoKkSecondWave().Rarity);
        Assert.Equal(7m, new ProtoKkSecondWave().DynamicVars.Damage.BaseValue);
        Assert.Equal(4m, new ProtoKkPincer().DynamicVars.Damage.BaseValue);
        Assert.Equal(5m, Upgraded<ProtoKkPincer>().DynamicVars.Damage.BaseValue);
        Assert.Equal(7m, new ProtoKkOpeningGambit().DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded<ProtoKkOpeningGambit>().DynamicVars.Damage.BaseValue);
        Assert.Equal(7m, new ProtoKkDeepCurrent().DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded<ProtoKkDeepCurrent>().DynamicVars.Damage.BaseValue);
        var riptide = new ProtoKkRiptide();
        Assert.Equal(11m, riptide.DynamicVars.Damage.BaseValue);
        Assert.Equal(3m, riptide.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal((KokomiPlan.Kind.Energy, 2),
                     (riptide.PlanClauses[0].Kind, riptide.PlanClauses[0].Amount));
    }

    // ---- G. the thirteen --------------------------------------------------

    [Fact]
    public void The_commons()
    {
        var volley = new ProtoKkMassedVolley();
        Assert.Equal(3m, volley.DynamicVars.Damage.BaseValue);
        Assert.Equal(4m, Upgraded<ProtoKkMassedVolley>().DynamicVars.Damage.BaseValue);
        Assert.Equal("Deal {Damage:diff()} damage 3 times.", Face(volley));

        var arrow = new ProtoKkSignalArrow();
        Assert.Equal(7m, arrow.DynamicVars.Damage.BaseValue);
        var arrowPlan = arrow.PlanClauses.Single();
        Assert.Equal((KokomiPlan.Kind.Damage, 3, 2, KokomiPlan.Aim.AllEnemies),
                     (arrowPlan.Kind, arrowPlan.Amount, arrowPlan.Times, arrowPlan.Aim));
        var arrowUp = Upgraded<ProtoKkSignalArrow>();
        Assert.Equal(10m, arrowUp.DynamicVars.Damage.BaseValue);
        Assert.Equal(4, arrowUp.PlanClauses.Single().Amount);

        var shoal = new ProtoKkSurgingShoal();
        Assert.Equal(2, shoal.EnergyCost.Canonical);
        Assert.Equal(14m, shoal.DynamicVars.Damage.BaseValue);
        Assert.Equal(22, shoal.PlanClauses.Single().Amount);
        var shoalUp = Upgraded<ProtoKkSurgingShoal>();
        Assert.Equal(18m, shoalUp.DynamicVars.Damage.BaseValue);
        Assert.Equal(28, shoalUp.PlanClauses.Single().Amount);

        var diver = new ProtoKkPearlDiver();
        Assert.Equal(1m, diver.DynamicVars.Cards.BaseValue);
        Assert.Equal(2m, Upgraded<ProtoKkPearlDiver>().DynamicVars.Cards.BaseValue);
        Assert.Equal((KokomiPlan.Kind.CasketGain, 2),
                     (diver.PlanClauses.Single().Kind, diver.PlanClauses.Single().Amount));

        var press = new ProtoKkPressTheAdvantage();
        Assert.Equal(6m, Var(press, "PlainDamage"));
        Assert.Equal(10m, Var(press, "BranchDamage"));
        var pressUp = Upgraded<ProtoKkPressTheAdvantage>();
        Assert.Equal(8m, Var(pressUp, "PlainDamage"));
        Assert.Equal(13m, Var(pressUp, "BranchDamage"));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkPressTheAdvantage", "OnPlay")),
                        c => c.Contains("KokomiPlan.PlansHeld"));

        var shell = new ProtoKkShellOfSanctuary();
        Assert.Equal(1m, shell.DynamicVars.Cards.BaseValue);
        Assert.Equal(9m, Var(shell, "PlanBlock"));
        Assert.Equal(12m, Var(Upgraded<ProtoKkShellOfSanctuary>(), "PlanBlock"));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkShellOfSanctuary", "OnPlay")),
                        c => c.Contains("KokomiPlan.Schedule"));
        Assert.Contains("[gold]Dusk[/gold] [gold]Plan[/gold]", Face(shell));

        var glass = new ProtoKkDriftglass();
        Assert.Equal(5m, Var(glass, "CalculationBase"));
        Assert.Equal(1m, Var(glass, "ExtraDamage"));
        Assert.Equal(7m, Var(Upgraded<ProtoKkDriftglass>(), "CalculationBase"));

        // Commons never increase deck size (LAW): none of the seven creates a card.
        foreach (var type in new[] { "ProtoKkMassedVolley", "ProtoKkSignalArrow",
                                     "ProtoKkSurgingShoal", "ProtoKkPearlDiver",
                                     "ProtoKkPressTheAdvantage",
                                     "ProtoKkShellOfSanctuary", "ProtoKkDriftglass" })
        {
            Assert.DoesNotContain(Il.Calls(Il.Method(type, "OnPlay")),
                                  c => c.Contains("CreateCard")
                                    || c.Contains("AddGeneratedCard"));
        }
    }

    [Fact]
    public void The_uncommons_and_the_rare()
    {
        var returns = new ProtoKkWhatTheTokoyoReturns();
        Assert.Equal(1, returns.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, returns.Keywords);
        Assert.Equal(0, Upgraded<ProtoKkWhatTheTokoyoReturns>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkWhatTheTokoyoReturns", "OnPlay")),
                        c => c.Contains("KokomiOverhaulKit.FetchOpenCasket"));
        Assert.Contains(Il.Calls(Il.Method("KokomiOverhaulKit", "FetchOpenCasket")),
                        c => c.Contains("CardPileCmd.Add"));

        var judgment = new ProtoKkDepthsJudgment();
        Assert.Equal(2, judgment.EnergyCost.Canonical);
        Assert.Equal(0m, Var(judgment, "CalculationBase"));
        Assert.Equal(3m, Var(judgment, "ExtraDamage"));
        Assert.Equal(4m, Var(Upgraded<ProtoKkDepthsJudgment>(), "ExtraDamage"));
        Assert.Contains("{CalculatedDamage:diff()}", Face(judgment));

        var turn = new ProtoKkTideturn();
        Assert.Equal(4m, Var(turn, "ExtraDamage"));
        Assert.Equal(5m, Var(Upgraded<ProtoKkTideturn>(), "ExtraDamage"));

        var signal = new ProtoKkMoonSignal();
        Assert.Equal(CardType.Power, signal.Type);
        Assert.Equal(1, signal.EnergyCost.Canonical);
        Assert.Equal(0, Upgraded<ProtoKkMoonSignal>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Contains("PowerCmd.Apply<MoonSignalPower>",
                        string.Join(" ", Seq("ProtoKkMoonSignal", "OnPlay")));
        Assert.Equal(2, KokomiOverhaulLaw.MoonSignalThreshold);

        var current = new ProtoKkPearlCurrent();
        Assert.Equal(2m, current.DynamicVars.Damage.BaseValue);
        var currentPlan = current.PlanClauses.Single();
        Assert.Equal((2, 3, KokomiPlan.Aim.AllEnemies),
                     (currentPlan.Amount, currentPlan.Times, currentPlan.Aim));
        var currentUp = Upgraded<ProtoKkPearlCurrent>();
        Assert.Equal(3m, currentUp.DynamicVars.Damage.BaseValue);
        Assert.Equal(3, currentUp.PlanClauses.Single().Amount);

        var took = new ProtoKkWhatTheTokoyoTook();
        Assert.Equal(CardRarity.Rare, took.Rarity);
        Assert.Equal(2, took.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, took.Keywords);
        Assert.Equal(1, Upgraded<ProtoKkWhatTheTokoyoTook>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkWhatTheTokoyoTook", "OnPlay")),
                        c => c.Contains("KokomiOverhaulKit.DoubleCasket"));
    }

    [Fact]
    public void Moon_signal_reads_the_queue_before_the_morning_drains_it()
    {
        // "If 2 or more Plans are waiting" could never be true after a drain
        // empties the queue, so the read is taken first and handed in.
        var turn = Seq("ProtoBakeKuragePower", "AfterPlayerTurnStart");
        var read = turn.FindIndex(c => c.Contains("KokomiPlan.PlansHeld"));
        var signal = turn.FindIndex(c => c.Contains("MoonSignalPower.Signal"));
        var drain = turn.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        Assert.True(read >= 0 && signal > read && drain > signal);
    }

    [Fact]
    public void A_plan_can_gain_the_casket()
    {
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("KokomiOverhaulKit.GainCasket"));
        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi();
        KokomiOverhaulKit.GainCasket(seat.Creature, 2);
        Assert.Equal(2, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
    }

    [Fact]
    public void Shell_guard_is_five_block_plus_one_per_point_in_the_casket()
    {
        // Re-aimed by the main session (2026-09-28) after the Casket pass
        // left its strike clause dead: Uncommon Skill, cost 1, base 8
        // upgraded, the in-combat Block preview like Pneuma Refrain's.
        var card = new ProtoKkShellGuard();
        Assert.Equal((CardType.Skill, CardRarity.Uncommon, 1),
                     (card.Type, card.Rarity, card.EnergyCost.Canonical));
        Assert.Equal(5m, Var(card, "CalculationBase"));
        Assert.Equal(1m, Var(card, "CalculationExtra"));
        var up = Upgraded<ProtoKkShellGuard>();
        Assert.Equal(8m, Var(up, "CalculationBase"));
        Assert.Equal(1m, Var(up, "CalculationExtra"));
        Assert.Equal("Gain {CalculationBase:diff()} [gold]Block[/gold], plus "
                   + "{CalculationExtra:diff()} for each point in the "
                   + "[gold]Casket[/gold].{InCombat:\n(Gains "
                   + "{CalculatedBlock:diff()} [gold]Block[/gold])|}",
                     Face(card));
        Assert.Contains("CasketCount",
                        string.Join(" ", typeof(ProtoKkShellGuard)
                            .GetNestedTypes(HeadlessGame.All)
                            .SelectMany(t => t.GetMethods(HeadlessGame.All))
                            .Where(m => m.GetMethodBody() != null)
                            .SelectMany(Il.Calls)));
    }

    // ---- F. the offer -----------------------------------------------------

    [Fact]
    public void The_offer_is_forty_six_rows_with_the_thirteen_and_without_the_six()
    {
        var slice = Seq("KokomiOverhaulRoster", "Slice");
        Assert.Equal(46, slice.Count(c => c.StartsWith("ModelDb.Card")));
        foreach (var row in new[] { "ProtoKkMassedVolley", "ProtoKkSignalArrow",
                                    "ProtoKkSurgingShoal", "ProtoKkPearlDiver",
                                    "ProtoKkPressTheAdvantage",
                                    "ProtoKkShellOfSanctuary", "ProtoKkDriftglass",
                                    "ProtoKkWhatTheTokoyoReturns",
                                    "ProtoKkDepthsJudgment", "ProtoKkTideturn",
                                    "ProtoKkMoonSignal", "ProtoKkPearlCurrent",
                                    "ProtoKkWhatTheTokoyoTook" })
        {
            Assert.Contains(slice, c => c.EndsWith("<" + row + ">",
                                                   StringComparison.Ordinal));
        }
        foreach (var gone in new[] { "TideChart", "CleansingWave", "Ripple",
                                     "WellLaid", "SeaSaltPrayer", "SaltLine" })
        {
            Assert.DoesNotContain(slice, c => c.Contains("ProtoKk" + gone));
        }
    }

    // ---- H. the retired Garment tip ---------------------------------------

    [Fact]
    public void No_arm_attack_carries_the_retired_garment_tip()
    {
        foreach (var type in typeof(ProtoKkFeint).Assembly.GetTypes()
                     .Where(t => t.Name.StartsWith("ProtoKk", StringComparison.Ordinal)
                              && t.Namespace == typeof(ProtoKkFeint).Namespace))
        {
            var tips = type.GetMethod("get_ExtraHoverTips", HeadlessGame.All
                | System.Reflection.BindingFlags.DeclaredOnly);
            if (tips == null) continue;
            Assert.DoesNotContain(Il.Calls(tips),
                                  c => c.Contains("ForGarmentAttack"));
        }
    }
}
