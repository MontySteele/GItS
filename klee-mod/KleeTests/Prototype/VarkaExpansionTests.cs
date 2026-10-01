using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA, THE EXPANSION (<c>review/active/varka-expansion-2026-10-01.md</c>
/// sec.3, all four picks ruled at the defaults 2026-10-01): the 37 cards and
/// the Knight pass. Pinned the way <see cref="VarkaPrototypeTests"/> pins the
/// Oath rework: the ledger and the payout arithmetic by value, the live sites
/// by their call graph. The sim twin is
/// <c>tier0/tests/test_varka_expansion.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaExpansionTests : IDisposable
{
    public VarkaExpansionTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static VarkaOathLedger FreshLedger() =>
        VarkaOathLedger.For(Seat.Klee().Creature);

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    // ---- the ledger's new counts ------------------------------------------

    [Fact]
    public void Knights_this_combat_outlive_the_turn()
    {
        var ledger = FreshLedger();
        ledger.NoteKnight();
        ledger.NoteKnight();
        ledger.RollTo(9);
        ledger.NoteKnight();
        Assert.Equal(1, ledger.KnightsThisTurn);
        Assert.Equal(3, ledger.KnightsThisCombat);
    }

    [Fact]
    public void A_change_is_remembered_for_its_turn_only()
    {
        var ledger = FreshLedger();
        ledger.RollTo(3);
        Assert.False(ledger.ChangedThisTurn);
        Assert.True(ledger.SetCurrent(Element.Cryo));      // none -> Cryo
        Assert.True(ledger.ChangedThisTurn);
        ledger.RollTo(4);
        Assert.False(ledger.ChangedThisTurn);
        Assert.False(ledger.SetCurrent(Element.Cryo));     // no change
        Assert.False(ledger.ChangedThisTurn);
    }

    [Fact]
    public void Swirls_this_turn_and_static_field_reset_each_round()
    {
        var ledger = FreshLedger();
        ledger.RollTo(1);
        var body = Seat.Klee(30).Creature;
        ledger.NoteSwirl(body);
        ledger.NoteSwirl(body);
        Assert.Equal(2, ledger.SwirlsThisTurn);
        Assert.True(ledger.TakeStaticField());
        Assert.False(ledger.TakeStaticField());
        ledger.RollTo(2);
        Assert.Equal(0, ledger.SwirlsThisTurn);
        Assert.Equal(2, ledger.SwirlsMade);
        Assert.True(ledger.TakeStaticField());
    }

    // ---- Noelle, a Geo Knight ----------------------------------------------

    [Fact]
    public void Noelle_is_a_geo_knight_that_sets_no_element()
    {
        var noelle = new ProtoVkNoelleSteadfastMaid();
        Assert.True(VarkaRules.IsKnight(noelle));
        Assert.Equal(Element.Geo, VarkaOath.KnightElement(noelle));
        Assert.False(VarkaOath.IsOathElement(Element.Geo));
        Assert.All(VarkaOathLedger.Elements,
                   e => Assert.True(VarkaOath.IsOathElement(e)));
        // A Geo SetCurrent is refused by the ledger, and BeginPlay asks
        // before it calls it.
        var ledger = FreshLedger();
        Assert.False(ledger.SetCurrent(Element.Geo));
        Assert.Equal(Element.None, ledger.Current);
        var begin = Il.CallSequence(Il.Method("VarkaOath", "BeginPlay")).ToList();
        var knight = begin.IndexOf("VarkaOathLedger.NoteKnight");
        var ask = begin.IndexOf("VarkaOath.IsOathElement");
        var set = begin.IndexOf("VarkaOath.SetCurrent");
        Assert.True(knight >= 0 && ask > knight && set > ask,
                    string.Join(", ", begin));
        Assert.Equal(9m, Var(noelle, "CalculationBase"));
        Assert.Equal(12m, Var(Upgraded<ProtoVkNoelleSteadfastMaid>(),
                              "CalculationBase"));
    }

    [Fact]
    public void The_pool_knights_are_thirteen_noelle_among_them()
    {
        var pool = Il.CallSequence(Il.Method("VarkaRules", "PoolKnights"))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();
        Assert.Equal(13, pool.Count);
        foreach (var name in new[] { "ProtoVkAmberSharpshooter",
                                     "ProtoVkBarbaraWellspringHymn",
                                     "ProtoVkLisaPulsatingWitch",
                                     "ProtoVkNoelleSteadfastMaid" })
        {
            Assert.Contains($"ModelDb.Card<{name}>", pool);
        }
        var order = Calls("VarkaRules", "AddRandomKnight");
        Assert.Contains("VarkaRules.PoolKnights", order);
        Assert.Contains("CardPileCmd.AddGeneratedCardToCombat", order);
    }

    // ---- the Knight pass ---------------------------------------------------

    [Fact]
    public void The_knight_pass_numbers()
    {
        Assert.Equal(5m, Var(new ProtoVkBarbaraShowBegin(), "CalculationBase"));
        Assert.Equal(7m, Var(Upgraded<ProtoVkBarbaraShowBegin>(), "CalculationBase"));
        Assert.Equal(2m, Var(new ProtoVkMikaStarfrostSwirl(), "PowerAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkMikaStarfrostSwirl>(), "PowerAmount"));
        var razor = new ProtoVkRazorClawAndThunder();
        Assert.Equal(TargetType.AllEnemies, razor.TargetType);
        Assert.Equal(4m, Var(razor, "VkBase"));
        Assert.Equal(3m, Var(razor, "VkAmount"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkRazorClawAndThunder>(), "VkBase"));
        Assert.Contains("VarkaCards.Awakening",
                        Calls("ProtoVkRazorClawAndThunder", "OnPlay"));
        Assert.Contains("PowerCmd.Apply",
                        Calls("ProtoVkKaeyaFrostgnaw", "OnPlay"));
        Assert.Contains("PlayerCmd.GainEnergy",
                        Calls("ProtoVkDilucSearingOnslaught", "OnPlay"));
        Assert.Contains("ReactionEffects.get_TotalResolved",
                        Calls("ProtoVkDilucSearingOnslaught", "OnPlay"));
    }

    [Fact]
    public void Razor_reads_electro_before_his_hits()
    {
        Assert.Equal(7, VarkaCards.AwakeningDamage(4m, 3m, hadElectro: true));
        Assert.Equal(4, VarkaCards.AwakeningDamage(4m, 3m, hadElectro: false));
        var awakening = Calls("VarkaCards", "Awakening");
        Assert.Contains("AuraCmd.Find", awakening);
        Assert.Contains("VarkaCards.ElementHit", awakening);
    }

    [Fact]
    public void Sharpshooter_snapshots_pyro_at_the_top_of_the_play()
    {
        var seq = Il.CallSequence(Il.Method("ProtoVkAmberSharpshooter", "OnPlay"))
            .ToList();
        var find = seq.IndexOf("AuraCmd.Find");
        var firstHit = seq.IndexOf("DamageCmd.Attack");
        Assert.True(find >= 0 && firstHit > find, string.Join(", ", seq));
        Assert.Equal(2, seq.Count(c => c == "DamageCmd.Attack"));
    }

    // ---- the new kinds -----------------------------------------------------

    [Theory]
    [InlineData("ProtoVkPathfindersMark", "VarkaCards.PathfindersMark")]
    [InlineData("ProtoVkCavalryCharge", "VarkaCards.CurrentElementStrike")]
    [InlineData("ProtoVkBlazingCharge", "VarkaCards.BlazingCharge")]
    [InlineData("ProtoVkGlacialEdict", "VarkaCards.GlacialEdict")]
    [InlineData("ProtoVkThunderingVerdict", "VarkaCards.ThunderingVerdict")]
    [InlineData("ProtoVkLisaPulsatingWitch", "VarkaCards.DrawPerEnemy")]
    [InlineData("ProtoVkBarbaraWellspringHymn", "VarkaCards.Cleanse")]
    [InlineData("ProtoVkCrosscurrent", "VarkaCards.Crosscurrent")]
    [InlineData("ProtoVkGrandMastersVerdict", "VarkaCards.DoubleCurrentOath")]
    [InlineData("ProtoVkTempestOfTheFourWinds", "VarkaCards.Tempest")]
    [InlineData("ProtoVkVowOfTheBlade", "VarkaCards.GainCurrentOath")]
    public void Each_kind_is_one_call_from_its_card(string card, string call)
    {
        Assert.Contains(call, Calls(card, "OnPlay"));
    }

    [Fact]
    public void The_payoffs_read_their_own_elements_oath()
    {
        Assert.Contains("VarkaOath.Count", Calls("VarkaCards", "BlazingCharge"));
        Assert.Contains("VarkaOath.Count", Calls("VarkaCards", "GlacialEdict"));
        // Thundering Verdict reads it through its face's per-hit sum.
        Assert.Contains("VarkaHitDamageVar.PerHit", Calls("VarkaCards", "ThunderingVerdict"));
        Assert.Contains("VarkaOath.Count", Calls("VarkaHitDamageVar", "PerHit"));
        Assert.DoesNotContain("VarkaOath.CurrentOath",
                              Calls("VarkaCards", "BlazingCharge"));
        Assert.Equal(1, VarkaCards.GlacialEdictStacks(3, 4));
        Assert.Equal(3, VarkaCards.GlacialEdictStacks(8, 4));
        Assert.Equal(3, VarkaCards.GlacialEdictStacks(6, 3));
        Assert.Equal(4m, Var(new ProtoVkGlacialEdict(), "VkAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkGlacialEdict>(), "VkAmount"));
        Assert.Equal(new[] { Element.Pyro, Element.Hydro, Element.Cryo, Element.Electro },
                     VarkaCards.TempestOrder);
    }

    [Fact]
    public void Pathfinder_reads_its_upgrade_and_rolls_an_element_with_none()
    {
        var mark = Calls("VarkaCards", "PathfindersMark");
        Assert.Contains("CardModel.get_IsUpgraded", mark);
        Assert.Contains("ElementalHit.ApplyOnly", mark);
        Assert.Contains("VarkaOath.Current", mark);
        Assert.Equal(0, new ProtoVkPathfindersMark().EnergyCost.Canonical);
        // Upgraded, it reaches ALL enemies and asks for no target.
        Assert.Equal(TargetType.AnyEnemy, new ProtoVkPathfindersMark().TargetType);
        Assert.Equal(TargetType.AllEnemies,
                     Upgraded<ProtoVkPathfindersMark>().TargetType);
    }

    [Fact]
    public void Crosscurrent_opens_the_pays_twice_window_around_its_swirl()
    {
        var cross = Calls("VarkaCards", "Crosscurrent");
        Assert.Contains("VarkaOathLedger.set_PaysTwice", cross);
        Assert.Contains("ElementalHit.ApplyOnly", cross);
    }

    // ---- the Powers ---------------------------------------------------------

    [Fact]
    public void The_payout_powers()
    {
        Assert.Equal(1, VarkaLaw.AbsoluteZeroWeak);
        Assert.Equal(3, VarkaLaw.EyeOfStormterrorSwirls);
        var swirl = Calls("VarkaOath", "OnSwirl");
        Assert.Contains("VarkaOath.Pay", swirl);
        Assert.Contains("EyeOfStormterrorPower.Draw", swirl);
        Assert.Contains("CreatureCmd.GainBlock", swirl);            // Eye Wall
        Assert.Contains("VarkaOath.IsOathElement", swirl);          // Twin Gales
    }

    [Fact]
    public void Static_field_and_the_banner_sit_at_the_application()
    {
        var note = Il.CallSequence(Il.Method("VarkaOath", "NoteApplication")).ToList();
        var field = note.IndexOf("VarkaOathLedger.TakeStaticField");
        var opens = note.IndexOf("VarkaOathLedger.OpenOathSwitches");
        Assert.True(field >= 0 && opens > field, string.Join(", ", note));
        Assert.Contains("StaticFieldPower.Draw", note);
    }

    [Fact]
    public void Element_change_gain_and_turn_powers_are_paid_where_the_rules_move()
    {
        Assert.Contains("CycleOfSeasonsPower.OnElementChanged",
                        Calls("VarkaOath", "SetCurrent"));
        var start = Il.CallSequence(Il.Method("VarkaOath", "TurnStart")).ToList();
        var vane = start.IndexOf("VarkaOath.Weathervane");
        var bunny = start.IndexOf("VarkaBaronBunnyPower.Fire");
        var order = start.IndexOf("VarkaRules.AddRandomKnight");
        Assert.True(vane >= 0 && bunny > vane && order > bunny,
                    string.Join(", ", start));
        Assert.Contains("VarkaRules.ChooseElement", Calls("VarkaOath", "Weathervane"));
        var end = Calls("VarkaOath", "EndPlay");
        Assert.Contains("AssemblyAtTheCathedralPower.OnKnightPlayed", end);
        Assert.Contains("WolfpackPower.OnAscensionPlayed", end);
        Assert.Contains("CardPileCmd.AddGeneratedCardToCombat",
                        Calls("WolfpackPower", "OnAscensionPlayed"));
    }

    [Fact]
    public void Aegis_pays_half_the_total_per_copy()
    {
        // Varka defence (2026-10-01): half, rounded down, no cap.
        Assert.Equal(9, OathboundAegisPower.BlockFor(18, 1));
        Assert.Equal(20, OathboundAegisPower.BlockFor(41, 1));
        Assert.Equal(40, OathboundAegisPower.BlockFor(41, 2));
        Assert.Equal(0, OathboundAegisPower.BlockFor(1, 1));
    }

    [Fact]
    public void Downburst_alone_spreads_fresh()
    {
        Assert.True(VarkaRules.SpreadArrivesFresh(new ProtoVkDownburst()));
        Assert.False(VarkaRules.SpreadArrivesFresh(new ProtoVkGaleSweep()));
        Assert.False(VarkaRules.SpreadArrivesFresh(null));
        Assert.Contains("VarkaRules.SpreadArrivesFresh",
                        Calls("ReactionEffects", "SwirlPays"));
    }

    [Fact]
    public void Every_expansion_power_says_what_it_does()
    {
        var powers = new PowerModel[]
        {
            new StaticFieldPower(), new UnwaveringBannerPower(),
            new CycleOfSeasonsPower(), new EyeWallPower(),
            new AssemblyAtTheCathedralPower(), new WildfireOathPower(),
            new RetaliatingTidePower(), new AbsoluteZeroPower(),
            new OathUntoDeathPower(), new WolfpackPower(),
            new OathboundAegisPower(), new WeathervanePower(),
            new TwinGalesPower(), new EyeOfStormterrorPower(),
            new TheOrderAnswersPower(),
        };
        foreach (var power in powers)
        {
            var loc = ((BaseLib.Abstracts.ILocalizationProvider)power).Localization!;
            Assert.Contains(loc, kv => kv.Item1 == "title");
            Assert.Contains(loc, kv => kv.Item1 == "description"
                                       && kv.Item2.Length > 10);
        }
    }

    [Fact]
    public void The_cost_and_innate_upgrades()
    {
        Assert.Equal(2, new ProtoVkRetaliatingTide().EnergyCost.Canonical);
        Assert.Equal(1, Upgraded<ProtoVkRetaliatingTide>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Equal(2, new ProtoVkTheOrderAnswers().EnergyCost.Canonical);
        Assert.Equal(1, Upgraded<ProtoVkTheOrderAnswers>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Contains(CardKeyword.Innate, Upgraded<ProtoVkWildfireOath>().Keywords);
        Assert.DoesNotContain(CardKeyword.Innate, new ProtoVkWildfireOath().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoVkGrandMastersVerdict().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoVkDawnPatrol().Keywords);
    }
}
