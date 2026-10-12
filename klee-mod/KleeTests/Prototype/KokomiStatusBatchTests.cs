using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI STATUS BATCH (2026-10-01, ruled). Paper
/// <c>review/active/kokomi-status-batch-2026-10-01.md</c>: "the 7 removals
/// are good", "Agreed on the Plan text change". Seven cards built (Kelp Wall,
/// Tidecleanse, Sea Glass Harvest, Turning Tide, Flotsam Surge, Abyssal
/// Salvage, and Riptide Ruin, the Rare in the cut Coral Sanctuary's place)
/// and the Sea Glass token, so the pool is 78. A Plan line under a now-line
/// prints "Or plan:" (a Plan-only card keeps "Plan:") and the Plan tip opens
/// "Instead of the line above". What awaits
/// a command is pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_kokomi_status_batch.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiStatusBatchTests : IDisposable
{

    public KokomiStatusBatchTests() { }

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
        // Turning Tide and Abyssal Salvage left in the re-founding (2026-10-12).
        "ProtoKkKelpWall", "ProtoKkTidecleanse", "ProtoKkSeaGlassHarvest",
        "ProtoKkFlotsamSurge", "ProtoKkRiptideRuin",
    };

    // ---- the offer -----------------------------------------------------------

    [Fact]
    public void The_seven_rows_have_the_papers_types_costs_and_rarities()
    {
        var shapes = new (CardModel Card, CardType Type, int Cost, CardRarity Rarity)[]
        {
            (new ProtoKkKelpWall(), CardType.Skill, 1, CardRarity.Common),
            (new ProtoKkTidecleanse(), CardType.Skill, 0, CardRarity.Common),
            (new ProtoKkSeaGlassHarvest(), CardType.Skill, 1, CardRarity.Uncommon),
            (new ProtoKkFlotsamSurge(), CardType.Attack, 1, CardRarity.Uncommon),
            (new ProtoKkRiptideRuin(), CardType.Attack, 2, CardRarity.Rare),
        };
        foreach (var (card, type, cost, rarity) in shapes)
        {
            Assert.Equal(type, card.Type);
            Assert.Equal(cost, card.EnergyCost.Canonical);
            Assert.Equal(rarity, card.Rarity);
        }
    }

    // ---- the face says "or" ----------------------------------------------------

    [Fact]
    public void The_starters_oath_prints_or_plan()
    {
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold].\nOr "
                   + "[gold]plan[/gold]: Deal {PlanDamage:diff()} [gold]Hydro[/gold] damage to "
                   + "ALL enemies.", Face(new ProtoKkKuragesOath()));
        Assert.Contains("\nOr [gold]plan[/gold]: ",
                        Face(new ProtoKkSlackWater()));
    }

    [Fact]
    public void A_plan_only_card_keeps_plan_with_no_or()
    {
        // The main session's call (2026-10-01): "or" only under a now-line.
        Assert.Equal("Play on the [gold]Bake-Kurage[/gold].\n[gold]Plan[/gold]: "
                   + "Deal {PlanDamage:diff()} [gold]Hydro[/gold] damage.",
                     Face(new ProtoKkMasterstroke()));
        Assert.DoesNotContain("Or [gold]", Face(new ProtoKkBraceForTheTide()));
    }

    [Fact]
    public void The_plan_tip_opens_instead_of_the_line_above()
    {
        var tip = string.Join("", Il.Strings(Il.Method("ArmKeywordTips",
                                                       "ForPlan")));
        Assert.StartsWith("Instead of the line above, play it on the ",
                          tip.Substring(tip.IndexOf("Instead", StringComparison.Ordinal)));
    }

    // ---- the next hand -------------------------------------------------------------

    [Fact]
    public void Plans_are_carried_out_after_the_draw_so_they_read_that_hand()
    {
        // Rule 2: the morning drain is AfterPlayerTurnStart, which follows the
        // hand draw; each clause body reads the hand when it runs.
        Assert.Contains(Seq("ProtoBakeKuragePower", "AfterPlayerTurnStart"),
                        c => c.Contains("KokomiPlan.ResolveAll"));
        var one = Seq("KokomiPlan", "ResolveOne");
        foreach (var body in new[] { "KokomiStatusBatch.BlockPerStatus",
                                     "KokomiStatusBatch.TransformStatuses" })
        {
            Assert.Contains(one, c => c.Contains(body));
        }
        Assert.Contains(Seq("KokomiStatusBatch", "HandStatuses"),
                        c => c.Contains("GetPile"));
        Assert.Contains(Seq("KokomiStatusBatch", "BlockPerStatus"),
                        c => c.Contains("KokomiStatusBatch.StatusesInHand"));
    }

    [Fact]
    public void A_status_or_curse_is_read_off_the_cards_own_type()
    {
        Assert.True(KokomiStatusBatch.IsStatusOrCurse(
            new MegaCrit.Sts2.Core.Models.Cards.Dazed()));
        Assert.True(KokomiStatusBatch.IsStatusOrCurse(
            new MegaCrit.Sts2.Core.Models.Cards.Wound()));
        Assert.False(KokomiStatusBatch.IsStatusOrCurse(new ProtoKkAmbush()));
        Assert.False(KokomiStatusBatch.IsStatusOrCurse(null));
    }

    // ---- Kelp Wall ---------------------------------------------------------------------

    [Fact]
    public void Kelp_wall_plans_nine_plus_three_per_status_twelve_upgraded()
    {
        var card = new ProtoKkKelpWall();
        Assert.Equal(1m, card.DynamicVars.Cards.BaseValue);
        var clauses = card.PlanClauses;
        Assert.Equal(2, clauses.Count);
        // The Kokomi card pass (2026-10-11): Plan 9 [12].
        Assert.Equal((KokomiPlan.Kind.Block, 9), (clauses[0].Kind, clauses[0].Amount));
        Assert.Equal((KokomiPlan.Kind.BlockPerStatusInHand, 3),
                     (clauses[1].Kind, clauses[1].Amount));
        var up = Upgraded<ProtoKkKelpWall>().PlanClauses;
        Assert.Equal((12, 3), (up[0].Amount, up[1].Amount));
        Assert.Contains("plus 3 for each status or curse in your hand",
                        Face(card));
        Assert.Contains(Seq("KokomiStatusBatch", "BlockPerStatus"),
                        c => c.Contains("CreatureCmd.GainBlock"));
    }

    // ---- Tidecleanse ------------------------------------------------------------------------

    [Fact]
    public void Tidecleanse_exhausts_up_to_two_three_upgraded_then_applies_weak()
    {
        // The re-founding (2026-10-12): no Plan line; the Exhaust is the
        // now-line, first, then the Weak.
        var card = new ProtoKkTidecleanse();
        Assert.False(typeof(IPlannedCard).IsAssignableFrom(card.GetType()));
        Assert.Equal(2m, card.DynamicVars["KkAmount"].BaseValue);
        Assert.Equal(3m, Upgraded<ProtoKkTidecleanse>()
                             .DynamicVars["KkAmount"].BaseValue);
        var play = Seq("ProtoKkTidecleanse", "OnPlay");
        var exhaust = play.FindIndex(c => c.Contains("KokomiCards.ExhaustStatuses"));
        var weak = play.FindIndex(c => c.Contains("WeakPower"));
        Assert.True(exhaust >= 0 && weak > exhaust, string.Join(", ", play));
        Assert.DoesNotContain(play, c => c.Contains("CardPileCmd.Draw"));
        Assert.Contains(Seq("KokomiCards", "ExhaustStatuses"),
                        c => c.Contains("KokomiStatusBatch.ExhaustStatuses"));
        var body = Seq("KokomiStatusBatch", "ExhaustStatuses");
        Assert.Contains(body, c => c.Contains("CardSelectCmd.FromHand"));
        Assert.Contains(body, c => c.Contains("CardCmd.Exhaust"));
    }

    [Theory]
    [InlineData(0, 2, 0)]
    [InlineData(1, 2, 1)]
    [InlineData(2, 2, 2)]
    [InlineData(5, 2, 2)]
    [InlineData(5, 3, 3)]
    public void Tidecleanse_takes_every_one_up_to_its_number(int held, int cap,
                                                             int taken)
    {
        Assert.Equal(taken, KokomiStatusBatch.ExhaustCount(held, cap));
    }

    // ---- Sea Glass Harvest and the token ------------------------------------------------------

    [Fact]
    public void Sea_glass_harvest_is_compact_on_the_next_hand_curses_included()
    {
        var card = new ProtoKkSeaGlassHarvest();
        // The Kokomi card pass (2026-10-11): 10 [13] Block.
        Assert.Equal(10m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(13m, Upgraded<ProtoKkSeaGlassHarvest>().DynamicVars.Block.BaseValue);
        Assert.Equal(KokomiPlan.Kind.TransformStatusesInHand,
                     Assert.Single(card.PlanClauses).Kind);
        Assert.Contains("[gold]Sea Glass[/gold]{IfUpgraded:show:+|}", Face(card));
        var body = Seq("KokomiStatusBatch", "TransformStatuses");
        Assert.Contains(body, c => c.Contains("get_IsTransformable"));
        Assert.Contains(body, c => c.Contains("CreateCard"));
        Assert.Contains(body, c => c.Contains("CardCmd.Upgrade"));
        Assert.Contains(body, c => c.Contains("CardCmd.Transform"));
        // Sea Glass+ is read off the writing card when the Plan is carried out.
        Assert.Contains(Seq("KokomiPlan", "ResolveOne"),
                        c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void Sea_glass_is_a_zero_cost_exhaust_token_of_one_energy_two_upgraded()
    {
        var glass = new SeaGlass();
        Assert.Equal(0, glass.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Token, glass.Rarity);
        Assert.Contains(CardKeyword.Exhaust, glass.CanonicalKeywords);
        Assert.Equal(1, SeaGlass.EnergyFor(false));
        Assert.Equal(2, SeaGlass.EnergyFor(true));
        Assert.Contains(Seq("SeaGlass", "OnPlay"),
                        c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.DoesNotContain(Seq("SeaGlass", "OnPlay"),
                              c => c.Contains("CardPileCmd.Draw"));
    }

    // ---- Turning Tide ----------------------------------------------------------------------------

    // ---- Flotsam Surge ------------------------------------------------------------------------------

    [Fact]
    public void Flotsam_surge_hits_all_for_thirteen_and_discards_two_dazed()
    {
        var card = new ProtoKkFlotsamSurge();
        Assert.Equal(13m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(17m, Upgraded<ProtoKkFlotsamSurge>().DynamicVars.Damage.BaseValue);
        var play = Seq("ProtoKkFlotsamSurge", "OnPlay");
        Assert.Contains(play, c => c.Contains("CreateCard<Dazed>")
                                 || c.Contains("Dazed"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        Assert.Equal(Element.Hydro,
                     Assert.IsAssignableFrom<IElementalCard>(card).Element);
    }

    // ---- Riptide Ruin ------------------------------------------------------------------------------

    [Fact]
    public void Riptide_ruin_hits_all_twice_for_nine_and_discards_three_dazed()
    {
        var card = new ProtoKkRiptideRuin();
        Assert.Equal(9m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(12m, Upgraded<ProtoKkRiptideRuin>().DynamicVars.Damage.BaseValue);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        var play = Seq("ProtoKkRiptideRuin", "OnPlay");
        Assert.Contains(play, c => c.Contains("WithHitCount"));
        Assert.Contains(play, c => c.Contains("Dazed"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.AddGeneratedCardToCombat"));
        Assert.Contains("ALL enemies twice. Add 3 [gold]Dazed[/gold]",
                        Face(card));
        Assert.Equal(Element.Hydro,
                     Assert.IsAssignableFrom<IElementalCard>(card).Element);
    }

    // ---- Abyssal Salvage ------------------------------------------------------------------------------

}
