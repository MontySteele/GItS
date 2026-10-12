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
/// THE KOKOMI ROUND-1 FIXES (2026-10-12): the defects the first Plans +
/// Ethereal seat round found. Kelp Wall pays the status count of the hand it
/// was WRITTEN from (the number its preview shows); Sea Glass Harvest
/// transforms the DRAW PILE; Tide Wall's face names the intent it reads at
/// carry-out; Treatise's trigger is a printed Plan line, which a Companion
/// does not have; Press the Advantage names Plans, has no Plan line, and its
/// tip now says so. The suite is headless (no live combat), so behaviour is
/// pinned off the compiled methods and the card objects. Sim twins:
/// <c>tier0/tests/test_kokomi_status_batch.py</c> and
/// <c>test_kokomi_plan.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRound1FixesTests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- Kelp Wall ----------------------------------------------------------

    [Fact]
    public void Kelp_wall_counts_the_hand_when_the_plan_is_written()
    {
        // Schedule stamps the count; ResolveOne pays the stamped count; the
        // body reads the hand only where no writer stamped one.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Schedule")),
                        c => c.Contains("KokomiStatusBatch.StatusesInHand"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("get_WrittenCount"));
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "AskedFor")),
                        c => c.Contains("get_WrittenCount"));
        var stamped = new KokomiPlan.Planned(
            KokomiPlan.Kind.BlockPerStatusInHand, 3, KokomiPlan.Aim.Self)
            with { WrittenCount = 2 };
        Assert.Equal(2, stamped.WrittenCount);
        // The printed clause carries no count: it is stamped at writing.
        Assert.Null(new ProtoKkKelpWall().PlanClauses[1].WrittenCount);
        Assert.Contains("plus 3 for each status or curse in your hand when "
                      + "written.", Face(new ProtoKkKelpWall()));
    }

    // ---- Sea Glass Harvest ----------------------------------------------------

    [Fact]
    public void Sea_glass_harvest_transforms_the_draw_pile()
    {
        Assert.Equal(KokomiPlan.Kind.TransformStatusesInDrawPile,
                     Assert.Single(new ProtoKkSeaGlassHarvest().PlanClauses)
                         .Kind);
        var body = Il.Calls(Il.Method("KokomiStatusBatch", "TransformStatuses"));
        Assert.Contains(body, c => c.Contains("KokomiStatusBatch.PileStatuses"));
        Assert.DoesNotContain(body,
            c => c.Contains("KokomiStatusBatch.HandStatuses"));
        Assert.Contains("Transform every status and curse in your [gold]Draw Pile[/gold]",
                        Face(new ProtoKkSeaGlassHarvest()));
    }

    // ---- Tide Wall --------------------------------------------------------------

    [Fact]
    public void Tide_wall_reads_the_front_intent_at_carry_out()
    {
        // Read in ResolveOne (the morning the Plan is carried out, after the
        // enemies' intents for that turn are up), never stamped at writing.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("KokomiOverhaulKit.IntendedDamage"));
        Assert.DoesNotContain(Il.Calls(Il.Method("KokomiPlan", "Schedule")),
                              c => c.Contains("IntendedDamage"));
        var face = Face(new ProtoKkTideWall());
        Assert.Contains("plus the front enemy's intended damage.", face);
        Assert.DoesNotContain("next turn", face);
    }

    // ---- Treatise ------------------------------------------------------------------

    [Fact]
    public void Treatise_fires_on_a_printed_plan_line_and_not_on_a_companion()
    {
        // TreatisePower's gate is `IPlannedCard { PlanClauses.Count: > 0 }`.
        // Every Kokomi card that prints a Plan line passes it; a Companion,
        // which can be WRITTEN as a Plan but prints no Plan line, does not --
        // the seat that "never saw it draw" played Shinobu and Kirara.
        foreach (var card in new CardModel[]
                 { new ProtoKkKelpWall(), new ProtoKkTideWall(),
                   new ProtoKkKuragesOath(), new ProtoKkSlackWater() })
        {
            Assert.True(card is IPlannedCard { PlanClauses.Count: > 0 },
                        card.GetType().Name);
        }
        foreach (var card in new CardModel[]
                 { new ProtoMiShinobuSanctifyingRing(),
                   new ProtoMiKiraraSurpriseDispatch() })
        {
            Assert.IsAssignableFrom<IWritableCompanion>(card);
            Assert.False(card is IPlannedCard, card.GetType().Name);
        }
        var calls = Il.CallSequence(Il.Method("TreatisePower", "AfterCardPlayed"))
            .ToList();
        Assert.Contains(calls, c => c.Contains("KokomiPlan.PlayedOnPet"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Draw"));
    }

    // ---- Press the Advantage -----------------------------------------------------------

    [Fact]
    public void Press_the_advantage_has_no_plan_line_and_its_tip_says_so()
    {
        // The seat read the Plan tip's "play it on the Bake-Kurage" and the
        // jellyfish refused the card. The card is right (no `plan:` in the
        // sheet, an enemy-only target); the tip was wrong.
        var card = new ProtoKkPressTheAdvantage();
        Assert.False(card is IPlannedCard);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        var tips = Il.Calls(Il.Method("ProtoKkPressTheAdvantage",
                                      "get_ExtraHoverTips"));
        Assert.Contains(tips, c => c.Contains("ArmKeywordTips.ForPlanNoLine"));
        Assert.DoesNotContain(tips,
            c => c.EndsWith("ArmKeywordTips.ForPlan"));
        var text = string.Join("",
            Il.Strings(Il.Method("ArmKeywordTips", "ForPlanNoLine")));
        Assert.Contains("This card has no Plan line.", text);
        // A card WITH a Plan line keeps the writing tip.
        Assert.Contains(Il.Calls(Il.Method("ProtoKkKelpWall",
                                           "get_ExtraHoverTips")),
                        c => c.EndsWith("ArmKeywordTips.ForPlan"));
    }
}
