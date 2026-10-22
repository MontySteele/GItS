using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI REVIEW (2026-10-13), section 4.A ("Build now"), the C# side:
/// Tide Wall's face and live total, the Block a waiting Attack Plan lands in,
/// Grand Design's and Change of Plans' gates, Treatise's and Tidal Riposte's
/// words, the live Plan badge and the first-Plan mark, Frail on the printed
/// Block numbers, the rarity swap and Kurage's Wake's three Stings. Sim and
/// page twin: <c>tier0/tests/test_kokomi_review_2026_10_13.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiReviewTests
{
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

    private static string PowerText(ILocalizationProvider power) =>
        power.Localization!.Single(r => r.Item1 == "description").Item2;

    private static KokomiPlan.Entry Entry(params KokomiPlan.Planned[] clauses)
        => new(null, clauses);

    /// <summary>A Kokomi seat inside a combat whose hook listeners are her own
    /// powers: <c>Hook.ModifyBlock</c> then folds her Frail and Dexterity
    /// exactly as it does in game (<c>FurinaSpendRoundFixesTests.Build</c>'s
    /// board, one character over).</summary>
    private static Seat InCombat(Seat seat)
    {
        seat.WithCombatState();
        var listeners = seat.Creature.Powers.Cast<AbstractModel>().ToList();
        var run = DispatchProxy.Create<IRunState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        ((FurinaSpendAllPreviewWeakTests.ListenerProxy)(object)run).Listeners =
            listeners;
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        ((FurinaSpendAllPreviewWeakTests.ListenerProxy)(object)combat).Listeners =
            listeners;
        Seat.Force(seat.Player, "RunState", run);
        seat.Creature.CombatState = combat;
        return seat;
    }

    /// <summary>A combat in progress: <c>Hook.ModifyBlock</c> walks no
    /// listener while <c>CombatManager</c> says the combat is over
    /// (<c>FurinaSpendRoundFixesTests.InCombat</c>).</summary>
    private static void Running(Action body)
    {
        var field = typeof(CombatManager).GetField("_turnState", HeadlessGame.All)!;
        var saved = field.GetValue(CombatManager.Instance);
        var turn = System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(field.FieldType);
        Seat.Set(turn, "IsInProgress", true);
        field.SetValue(CombatManager.Instance, turn);
        try
        {
            body();
        }
        finally
        {
            field.SetValue(CombatManager.Instance, saved);
        }
    }

    private static T InHand<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        Seat.Force(seat.Player, "RunPiles", Array.Empty<CardPile>());
        ((List<CardModel>)typeof(CardPile)
            .GetField("_cards", HeadlessGame.All)!
            .GetValue(seat.Player.PlayerCombatState!.Hand)!).Add(card);
        return card;
    }

    // ---- 1. Tide Wall ---------------------------------------------------------

    [Fact]
    public void Tide_wall_face_names_the_turn_it_lands()
    {
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold].\nOr [gold]plan[/gold]: "
          + "Gain {PlanBlock:diff()} [gold]Block[/gold], plus the biggest "
          + "attack an enemy intends when this is carried out.",
            Face(new ProtoKkTideWall()));
    }

    [Fact]
    public void Tide_wall_still_reads_the_intent_at_carry_out()
    {
        // Confirmed, not changed: the carry-out asks the board when it runs.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "ResolveOne")),
                        c => c.Contains("KokomiOverhaulKit.MostIntendedDamage"));
        Assert.Equal((KokomiPlan.Kind.BlockMaxIntent, 4),  // defence pass
            new ProtoKkTideWall().PlanClauses
                .Select(c => (c.Kind, c.Amount)).Single());
    }

    [Fact]
    public void A_tide_wall_plans_live_total_folds_frail_and_dexterity()
    {
        var wall = Entry(new KokomiPlan.Planned(
            KokomiPlan.Kind.BlockMaxIntent, 6, KokomiPlan.Aim.Self));
        Running(() =>
        {
            // No enemy intends anything on this board, so the total is the 6.
            Assert.Equal(6, KokomiPlan.LiveBlock(
                wall, InCombat(Seat.Kokomi()).Creature));
            Assert.Equal(4, KokomiPlan.LiveBlock(
                wall, InCombat(Seat.Kokomi().WithPower<FrailPower>(2)).Creature));
            Assert.Equal(9, KokomiPlan.LiveBlock(
                wall,
                InCombat(Seat.Kokomi().WithPower<DexterityPower>(3)).Creature));
        });
    }

    [Fact]
    public void Only_a_plan_that_reads_the_board_has_a_live_total()
    {
        var kokomi = InCombat(Seat.Kokomi()).Creature;
        Assert.Null(KokomiPlan.LiveBlock(Entry(new KokomiPlan.Planned(
            KokomiPlan.Kind.Block, 12, KokomiPlan.Aim.Self)), kokomi));
        Assert.Null(KokomiPlan.LiveBlock(Entry(new KokomiPlan.Planned(
            KokomiPlan.Kind.BlockMaxIntent, 6, KokomiPlan.Aim.Self)),
            Seat.Kokomi().Creature));
        // The wire carries it.
        Assert.Contains(Il.Strings(Il.Method("KokomiPlan", "QueueRow")),
                        s => s == "block_now");
    }

    // ---- 2. a waiting Attack Plan into Block ----------------------------------

    [Fact]
    public void The_strip_caption_says_what_the_plan_meets()
    {
        Assert.Equal("Block 29",
            KokomiPlan.StripCaption(true, false, 29, 0, false));
        Assert.Equal("into 8 Block",
            KokomiPlan.StripCaption(false, false, null, 8, true));
        Assert.Equal("into Block",
            KokomiPlan.StripCaption(false, false, null, 0, true));
        Assert.Equal("Now-line",
            KokomiPlan.StripCaption(true, true, 29, 8, true));
        Assert.Equal("Plan line",
            KokomiPlan.StripCaption(true, false, null, 0, false));
        Assert.Null(KokomiPlan.StripCaption(false, false, null, 0, false));
    }

    [Fact]
    public void Kept_block_reads_the_games_own_clear_rule()
    {
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "KeptBlockAhead")),
                        c => c.Contains("Hook.ShouldClearBlock"));
        // A Block Plan writes nothing at a body.
        Assert.Equal(0, KokomiPlan.KeptBlockAhead(Entry(new KokomiPlan.Planned(
            KokomiPlan.Kind.Block, 12, KokomiPlan.Aim.Self)),
            Seat.Kokomi().Creature));
    }

    [Fact]
    public void The_strip_paints_the_caption_and_the_first_mark()
    {
        var paint = Il.Calls(Il.Method("KokomiPlanStrip", "Paint"));
        Assert.Contains(paint, c => c.Contains("KokomiPlan.StripCaption"));
        Assert.Contains(Il.Strings(Il.Method("KokomiPlanStrip", "Build")),
                        s => s == "First");
        // Redrawn after every play, so the captions follow the board.
        Assert.Contains(
            Il.Calls(Il.Method("ProtoBakeKuragePower", "AfterCardPlayed")),
            c => c.Contains("KokomiPlanStrip.Refresh"));
    }

    // ---- 3. Grand Design -------------------------------------------------------

    [Fact]
    public void Grand_design_needs_another_card_to_plan()
    {
        var self = new ProtoKkGrandDesign();
        Assert.False(KokomiRefounding.AnyOtherToPlan(
            new CardModel[] { self, new ProtoKkShoalCall() }, self));
        Assert.True(KokomiRefounding.AnyOtherToPlan(
            new CardModel[] { self, new ProtoKkTideWall() }, self));
        // Itself is never the card it plans.
        Assert.False(KokomiRefounding.AnyOtherToPlan(
            new CardModel[] { self }, self));
        Assert.Contains(Il.Calls(Il.Method("ProtoKkGrandDesign", "get_IsPlayable")),
                        c => c.Contains("KokomiRefounding.AnyToPlan"));
        Assert.Equal("no card in your hand can be planned",
                     ((IUnplayableReasonCard)new ProtoKkGrandDesign())
                        .UnplayableReason);
    }

    // ---- 4. Change of Plans ----------------------------------------------------

    [Fact]
    public void Change_of_plans_needs_a_waiting_plan()
    {
        Assert.StartsWith(
            "Can only be played if a [gold]Plan[/gold] is waiting. ",
            Face(new ProtoKkChangeOfPlans()));
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKkChangeOfPlans", "get_IsPlayable")),
            c => c.Contains("KokomiPlan.PlansHeld"));
        Assert.Equal("no Plan is waiting",
                     ((IUnplayableReasonCard)new ProtoKkChangeOfPlans())
                        .UnplayableReason);
    }

    // ---- 5. Treatise -----------------------------------------------------------

    [Fact]
    public void Treatise_names_what_counts_and_masterstroke_is_always_planned()
    {
        const string card = "The first time each turn you play a "
          + "[gold]Plan[/gold] card or a [gold]Companion[/gold] without "
          + "planning it, draw 1 card.";
        Assert.Equal(card, Face(new ProtoKkTreatise()));
        Assert.StartsWith(card[..^"draw 1 card.".Length],
                          PowerText(new TreatisePower()));
        // The rule the words describe: a written play draws nothing, and
        // Masterstroke can only be played on the Bake-Kurage.
        Assert.Contains(Il.Calls(Il.Method("TreatisePower", "AfterCardPlayed")),
                        c => c.Contains("KokomiPlan.PlayedOnPet"));
        Assert.Equal(KokomiTargets.PetOnly,
                     new ProtoKkMasterstroke().TargetType);
    }

    // ---- 6. the Plan badge -----------------------------------------------------

    [Fact]
    public void The_badge_is_pinned_to_the_queue_depth()
    {
        var seat = Seat.Kokomi().WithPower<PendingPlansPower>(1);
        KokomiPlan.PinBadge(seat.Creature, 2);
        Assert.Equal(2, seat.Creature.Powers.OfType<PendingPlansPower>()
                                           .Single().Amount);
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "RefreshBadge")),
                        c => c.Contains("KokomiPlan.PinBadge"));
    }

    // ---- 7. Frail on the printed Block -----------------------------------------

    [Fact]
    public void Tide_walls_plan_block_is_a_block_var()
    {
        var block = Assert.IsType<UnsourcedBlockVar>(
            new ProtoKkTideWall().DynamicVars["PlanBlock"]);
        Assert.Equal(ValueProp.Move, block.Props);
        Assert.Equal(4, block.IntValue);   // Kokomi defence pass, 2026-10-22
    }

    [Fact]
    public void Tide_walls_plan_block_previews_through_the_payouts_fold()
    {
        // `UnsourcedBlockVar` runs the carry-out's own `Hook.ModifyBlock`
        // call (Frail x0.75 on a `Move` Block, Dexterity added), so the
        // printed 6 reads 4 under Frail as the now-line's 4 reads 3. The
        // numeric fold is pinned on the live total above, which walks the
        // same listeners.
        Assert.Contains(
            Il.Calls(typeof(UnsourcedBlockVar).GetMethod("UpdateCardPreview")!),
            c => c.Contains("Hook.ModifyBlock"));
    }

    [Theory]
    [InlineData(typeof(ProtoVkFrostWard), 5)]
    [InlineData(typeof(ProtoVkBarbaraShowBegin), 6)]
    public void Varkas_flat_block_folds_frail_without_gaining_block(
        Type type, int printed)
    {
        var card = (CardModel)Activator.CreateInstance(type)!;
        var vk = Assert.IsType<CardBlockNumberVar>(card.DynamicVars["VkBase"]);
        Assert.Equal(printed, vk.IntValue);
        // Not a BlockVar: BaseLib reads GainsBlock off one, and Nimble's
        // eligibility is not what this fix is about (`lint_enchant_parity`).
        Assert.False(card.GainsBlock);

        Running(() =>
        {
            var seat = InCombat(Seat.Varka().WithPower<FrailPower>(2));
            Seat.Set(card, "IsMutable", true);
            Seat.Set(card, "Owner", seat.Player);
            Seat.Force(seat.Player, "RunPiles", Array.Empty<CardPile>());
            vk.UpdateCardPreview(card, CardPreviewMode.Normal, null, true);
            Assert.Equal(printed * 0.75m, vk.PreviewValue);
        });
    }

    // ---- 8. Tidal Riposte --------------------------------------------------------

    [Fact]
    public void Tidal_riposte_stores_for_the_next_attack()
    {
        // The Kokomi card paper v2 (2026-10-18, sec.2 change 4).
        Assert.Equal(
            "Whenever you fully [gold]Block[/gold] an enemy's attack, your "
          + "next Attack deals {PowerAmount:diff()} additional damage.",
            Face(new ProtoKkTidalRiposte()));
        Assert.EndsWith("additional damage.", PowerText(new TidalRipostePower()));
    }

    // ---- 9. the rarity swap --------------------------------------------------------

    [Fact]
    public void Shoal_call_is_common_and_brine_sting_uncommon()
    {
        Assert.Equal(CardRarity.Common, new ProtoKkShoalCall().Rarity);
        Assert.Equal(CardRarity.Uncommon, new ProtoKkBrineSting().Rarity);
    }

    // ---- 10. Kurage's Wake ---------------------------------------------------------

    [Fact]
    public void Kurages_wake_plans_three_stings()
    {
        var wake = new ProtoKkKuragesWake();
        Assert.Equal((KokomiPlan.Kind.AddStings, 3),
            wake.PlanClauses.Select(c => (c.Kind, c.Amount)).Single());
        // The Kokomi upgrade pass (2026-10-19): 3 [4].
        Assert.Contains("[gold]plan[/gold]: Add {PlanCards:diff()} [gold]Stings[/gold]",
                        Face(wake));
        Assert.Equal(4, Upgraded<ProtoKkKuragesWake>().PlanClauses.Single().Amount);
    }
}
