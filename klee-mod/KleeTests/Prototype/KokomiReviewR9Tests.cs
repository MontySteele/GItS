using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI REVIEW, ROUND 9 (2026-10-15,
/// <c>review/active/kokomi-review-r9-2026-10-15.md</c>, items 1 to 10;
/// Claude's, Kokomi at Prototype). The mod's halves: Tidecleanse draws, both
/// Orders cost 0, Opening Gambit's doubling in the Plan preview, an
/// overridden element in the card text, a summon's reactions named, Varka's
/// "(no aura: no Swirl)", and the "last carry-out" clearing between fights.
/// Sim and page twin: <c>tier0/tests/test_kokomi_review_r9_2026_10_15.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiReviewR9Tests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    // ---- items 1-3 -------------------------------------------------------------

    [Fact]
    public void Tidecleanse_draws_one_for_each_status_it_exhausts()
    {
        Assert.Contains("Draw 1 card for each.", Face(new ProtoKkTidecleanse()));
        var body = Il.Calls(typeof(KokomiCards).GetMethod(
            "ExhaustStatuses", HeadlessGame.All)!);
        Assert.Contains(body, c => c.Contains("KokomiStatusBatch.ExhaustStatuses"));
        Assert.Contains(body, c => c.Contains("CardPileCmd.Draw"));
    }

    [Fact]
    public void Orders_from_the_shrine_makes_the_pick_cost_zero_this_turn()
    {
        Assert.Contains("It costs 0 this turn and is [gold]Ethereal[/gold].",
                        Face(new ProtoKkOrdersFromTheShrine()));
        Assert.Contains(Il.Calls(typeof(KokomiCards).GetMethod(
            "ChooseCommonCompanion", HeadlessGame.All)!),
            c => c.Contains("SetThisTurn"));
    }

    [Fact]
    public void Sangonomiyas_orders_costs_two_and_its_card_costs_zero()
    {
        var card = new ProtoKkSangonomiyasOrders();
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Contains("It costs 0 and is [gold]Ethereal[/gold].", Face(card));
        var power = Calls("SangonomiyasOrdersPower", "AfterPlayerTurnStartLate");
        Assert.Contains(power, c => c.Contains("SetThisTurn"));
        var rows = ((ILocalizationProvider)new SangonomiyasOrdersPower())
            .Localization!;
        Assert.Contains("costs", rows.First(r => r.Item1 == "description").Item2);
    }

    // ---- item 4 ---------------------------------------------------------------

    private static KokomiPlan.Entry Gambit() => new(null, new[]
    {
        new KokomiPlan.Planned(KokomiPlan.Kind.NextPlanDoubleDamage, 0,
                               KokomiPlan.Aim.Self),
    });

    private static KokomiPlan.Entry Hit(int n) => new(null, new[]
    {
        new KokomiPlan.Planned(KokomiPlan.Kind.Damage, n,
                               KokomiPlan.Aim.FrontEnemy),
    });

    [Fact]
    public void The_plan_after_opening_gambit_shows_the_doubled_number()
    {
        Assert.True(KokomiPlan.WritesDoubleRider(Gambit()));
        Assert.False(KokomiPlan.WritesDoubleRider(Hit(10)));
        Assert.True(KokomiPlan.DoubledBy(Gambit(), Hit(10)));
        Assert.False(KokomiPlan.DoubledBy(Hit(10), Hit(10)));
        Assert.False(KokomiPlan.DoubledBy(null, Hit(10)));
        // No board: the written number, doubled before anything else.
        Assert.Equal(20, KokomiPlan.ForecastFrontDamage(Hit(10), null, true));
        Assert.Equal(10, KokomiPlan.ForecastFrontDamage(Hit(10), null));
        var row = Il.Calls(typeof(KokomiPlan).GetMethod(
            "QueueRow", HeadlessGame.All)!);
        Assert.Contains(row, c => c.Contains("KokomiPlan.ShowQueuedPlanDamage"));
    }

    // ---- item 5 ---------------------------------------------------------------

    [Fact]
    public void An_overridden_element_is_written_into_the_card_text()
    {
        Assert.Equal("Deal 13 [gold]Electro[/gold] damage.",
            OverriddenElementFace.Rewrite("Deal 13 [gold]Hydro[/gold] damage.",
                                          Element.Hydro, Element.Electro));
        Assert.Equal("Apply [gold]Pyro[/gold] to it.",
            OverriddenElementFace.Rewrite("Apply [gold]Hydro[/gold] to it.",
                                          Element.Hydro, Element.Pyro));
        // Not overridden, or nothing printed: untouched.
        const string same = "Deal 13 [gold]Hydro[/gold] damage.";
        Assert.Equal(same, OverriddenElementFace.Rewrite(
            same, Element.Hydro, Element.Hydro));
        Assert.Equal(same, OverriddenElementFace.Rewrite(
            same, Element.None, Element.Electro));
    }

    // ---- item 6 ---------------------------------------------------------------

    [Fact]
    public void A_summons_volley_is_attributed_and_files_its_reactions()
    {
        var summon = Il.Calls(typeof(KokomiPlan).GetMethod(
            "Summon", HeadlessGame.All)!);
        Assert.Contains(summon, c => c.Contains("ReactionLog.Attribute"));
        var note = Il.Calls(typeof(KokomiPlan).GetMethod(
            "NoteReaction", HeadlessGame.All)!);
        Assert.Contains(note, c => c.Contains("ReactionName"));
    }

    // ---- item 7 ---------------------------------------------------------------

    [Fact]
    public void Varka_and_sucrose_say_the_same_words_for_no_aura()
    {
        Assert.Equal("\n(no aura: no Swirl)", VarkaOath.SwirlWords(aura: false));
        Assert.Equal("", VarkaOath.SwirlWords(aura: true));
        Assert.Contains("no aura: no Swirl", SwirlAuraFace.NoAura);
        Assert.Equal("(no aura: no Swirl)", VarkaOath.NoAuraToSwirl.Trim());
    }

    // ---- item 9 ---------------------------------------------------------------

    [Fact]
    public void A_combat_opening_clears_the_last_carry_out()
    {
        Assert.Contains(Il.Calls(typeof(KleeElementalHooks).GetMethod(
            "BeforeCombatStart")!), c => c.Contains("KokomiPlan.ResetFight"));
        KokomiPlan.ResetFight();   // safe with nothing recorded
    }
}
