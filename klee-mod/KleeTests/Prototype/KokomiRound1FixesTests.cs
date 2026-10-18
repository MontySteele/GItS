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
/// carry-out; Treatise's trigger (widened to any card that can be written by
/// Kokomi round 2, 2026-10-12); Press the Advantage names Plans, has no Plan line, and its
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
        // The Kokomi level pass (2026-10-12): Kelp Wall's Plan left the status
        // count, so no row spells the clause today; the machinery stays. (A
        // Counter line since the pool overhaul, 2026-10-13.)
        Assert.Equal(KokomiPlan.Kind.DamageBlockedSince,
                     Assert.Single(new ProtoKkKelpWall().PlanClauses).Kind);
        Assert.DoesNotContain("status or curse", Face(new ProtoKkKelpWall()));
    }

    // ---- Sea Glass Harvest ----------------------------------------------------

    [Fact]
    public void Sea_glass_harvest_transforms_the_hand_and_draw_pile()
    {
        Assert.Equal(KokomiPlan.Kind.TransformStatusesYouHave,
                     Assert.Single(new ProtoKkSeaGlassHarvest().PlanClauses)
                         .Kind);
        var body = Il.Calls(Il.Method("KokomiStatusBatch", "TransformStatuses"));
        Assert.Contains(body, c => c.Contains("KokomiStatusBatch.PileStatuses"));
        Assert.DoesNotContain(body,
            c => c.Contains("KokomiStatusBatch.HandStatuses"));
        // Kokomi review r5 (2026-10-14, A8): the hand too; review r6 (item
        // 6): every pile she holds (`KokomiReviewR6Tests`).
        Assert.Contains("Transform every Status and Curse you have",
                        Face(new ProtoKkSeaGlassHarvest()));
    }

    // ---- Tide Wall --------------------------------------------------------------

    [Fact]
    public void Tide_wall_reads_the_intent_at_carry_out()
    {
        // Read in ResolveOne (the morning the Plan is carried out, after the
        // enemies' intents for that turn are up), never stamped at writing.
        // The largest intent since the Kokomi round-3 changes (2026-10-12).
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("KokomiOverhaulKit.MostIntendedDamage"));
        Assert.DoesNotContain(Il.Calls(Il.Method("KokomiPlan", "Schedule")),
                              c => c.Contains("IntendedDamage"));
        var face = Face(new ProtoKkTideWall());
        Assert.Contains("plus the biggest attack an enemy intends", face);
        Assert.DoesNotContain("next turn", face);
    }

    // ---- Treatise ------------------------------------------------------------------

    [Fact]
    public void Treatise_fires_on_any_plan_card_or_companion()
    {
        // Round 1 found a Companion did not trigger it (the seat that "never
        // saw it draw" played Shinobu and Kirara). Kokomi round 2
        // (2026-10-12) widened the gate: a printed Plan line, or a Companion
        // card. Kokomi review r9 pick 1 (a) (2026-10-15) took plain
        // Companions off the Bake-Kurage, so `CanBeWritten` no longer names
        // them and the gate reads `ICompanionCard` itself: the face ("a Plan
        // card or a Companion without planning it") and the cards that count
        // are unchanged. A carry-out is not a play of hers
        // (`KokomiPlan.IsCarryingOut`).
        foreach (var card in new CardModel[]
                 { new ProtoKkKelpWall(), new ProtoKkTideWall(),
                   new ProtoKkKuragesOath(), new ProtoKkSlackWater() })
        {
            Assert.True(card is IPlannedCard { PlanClauses.Count: > 0 },
                        card.GetType().Name);
        }
        foreach (var card in new CardModel[]
                 { new ProtoMiShinobuSanctifyingRing(),
                   new ProtoMiChioriHasode() })
        {
            Assert.IsAssignableFrom<global::KleeMod.Cards.ICompanionCard>(card);
            Assert.False(card is IPlannedCard, card.GetType().Name);
            Assert.False(KokomiRefounding.CanBeWritten(card), card.GetType().Name);
        }
        var calls = Il.CallSequence(Il.Method("TreatisePower", "AfterCardPlayed"))
            .ToList();
        Assert.Contains(calls, c => c.Contains("KokomiRefounding.CanBeWritten"));
        Assert.Contains(typeof(global::KleeMod.Cards.ICompanionCard),
            Il.TypesTested(Il.Method("TreatisePower", "AfterCardPlayed")));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.PlayedOnPet"));
        var carrying = calls.FindIndex(c => c.Contains("KokomiPlan.IsCarryingOut"));
        var claim = calls.FindIndex(
            c => c.Contains("KokomiOverhaulLedger.ClaimOncePerTurn"));
        Assert.True(carrying >= 0 && claim > carrying);
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Draw"));
    }

    // ---- Albedo -- Dust of Purification ------------------------------------------

    [Fact]
    public void Dust_of_purification_carried_out_by_a_plan_reads_the_draw_pile()
    {
        // BACKLOG (Albedo -- Dust of Purification): Sea Glass Harvest's fix.
        // Carried out (before the turn's draw) its exhaust reads the Draw
        // Pile; played face-up it reads the hand. Since Kokomi review r9
        // pick 1 (a) it is no longer written itself; Crystal Collapse's copy
        // is the carry-out that still plays it. Structural pin; the sim
        // twin is behavioural (test_klee_status_package.py).
        var calls = Il.Calls(Il.Method("KleeStatusPackage",
                                       "ExhaustStatusesGrowLargest"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.IsCarryingOut"));
        Assert.Contains(calls, c => c.Contains("KleeStatusPackage.ExhaustStatuses"));
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
