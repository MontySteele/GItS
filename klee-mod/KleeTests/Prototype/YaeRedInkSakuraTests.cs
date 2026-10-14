using System;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// RED INK ON A PLANTING CARD, AND THE DEAD-EDIT FILTER (ruled 2026-10-14,
/// <c>review/active/yae-design-axes-2026-10-14.md</c>). [USER]: "Hmm, let's
/// do both. Make the Sakura work, but also try to block dead edits when we
/// can." Pure decisions read by value, and the call graph pinned to prove
/// the live sites take them. Sim twin:
/// <c>tier0/tests/test_yae_red_ink_sakura.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeRedInkSakuraTests : IDisposable
{
    public YaeRedInkSakuraTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
    }

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    // ---- 1. inheritance -----------------------------------------------------

    [Fact]
    public void Only_red_ink_on_a_card_that_only_plants_inherits()
    {
        Assert.True(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, false, false, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.FoxFire, false, false, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.DeadlineExtension, false, false, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, false, true, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, true, false, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, false, false, false));
    }

    [Fact]
    public void A_red_ink_plant_plants_a_red_ink_sakura()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk));
        var s = Assert.Single(ledger.Standing);
        Assert.Equal(YaeAnnotation.RedInk, s.Annotation);
        Assert.Equal(YaeLaw.SakuraBase + s.Level + YaeLaw.RedInkAmount,
                     YaeShrineLedger.StrikeSize(YaeTenkoKind.Thunder, s.Level, s.Annotation));
    }

    [Fact]
    public void Twin_sakuras_two_plants_both_inherit()
    {
        // YaeShrine.Plant plants n one at a time, each with the inherited
        // Annotation: Twin Sakura's two.
        var ledger = Fresh();
        for (var i = 0; i < 2; i++) ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk);
        Assert.All(ledger.Standing, s => Assert.Equal(YaeAnnotation.RedInk, s.Annotation));
        Assert.Equal(2, ledger.Count);
    }

    [Fact]
    public void A_full_shrine_plant_that_feeds_the_oldest_inherits_nothing()
    {
        var ledger = Fresh();
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk));
        Assert.All(ledger.Standing, s => Assert.Equal(YaeAnnotation.None, s.Annotation));
    }

    [Fact]
    public void The_planting_verbs_pass_the_cards_inheritance()
    {
        foreach (var verb in new[] { nameof(YaeCards.Plant), nameof(YaeCards.PlantLevel) })
        {
            var calls = Il.Calls(typeof(YaeCards).GetMethod(verb)!);
            Assert.Contains($"{nameof(YaeAnnotationReach)}.{nameof(YaeAnnotationReach.Inherited)}", calls);
        }
        // The Sakura Seal Annotation's plant passes nothing: a card holds one
        // Annotation, and it is Sakura Seal.
        Assert.DoesNotContain($"{nameof(YaeAnnotationReach)}.{nameof(YaeAnnotationReach.Inherited)}",
            Il.Calls(typeof(SakuraSealAnnotation).GetMethod("OnPlay")!));
    }

    // ---- the card facts -----------------------------------------------------

    [Fact]
    public void The_planting_cards_carry_the_marker_and_only_plant()
    {
        foreach (var card in new CardModel[]
                 { new ProtoYmYakanEvocation(), new ProtoYmTwinSakura(), new ProtoYmGraftedBranch() })
        {
            Assert.True(YaeAnnotationReach.Plants(card), card.GetType().Name);
            Assert.False(YaeAnnotationReach.DealsDamage(card), card.GetType().Name);
            Assert.False(YaeAnnotationReach.GivesBlock(card), card.GetType().Name);
        }
        Assert.False(YaeAnnotationReach.Plants(new ProtoYmProofread()));
        Assert.False(YaeAnnotationReach.Plants(new StrikeIronclad()));
    }

    [Fact]
    public void Twin_sakura_upgraded_gives_block_so_red_ink_rides_the_block()
    {
        var twin = new ProtoYmTwinSakura();
        Upgrade(twin);
        Assert.True(YaeAnnotationReach.GivesBlock(twin));
        Assert.True(YaeAnnotationReach.Affects(twin, YaeAnnotation.RedInk));
    }

    [Fact]
    public void Print_runs_own_block_counts_without_moving_nimble()
    {
        var run = new ProtoYmPrintRun();
        Assert.False(run.GainsBlock);                 // Nimble unchanged
        Assert.True(YaeAnnotationReach.GivesBlock(run));
    }

    // ---- 2. the dead-edit filter --------------------------------------------

    [Fact]
    public void Red_ink_skips_a_pure_utility_card_and_footnote_takes_it()
    {
        var lure = new ProtoYmFoxfireLure();
        Assert.False(YaeAnnotationReach.Affects(lure, YaeAnnotation.RedInk));
        foreach (var a in new[] { YaeAnnotation.Footnote, YaeAnnotation.DeadlineExtension,
                                  YaeAnnotation.FoxFire, YaeAnnotation.SakuraSeal,
                                  YaeAnnotation.Royalties })
        {
            Assert.True(YaeAnnotationReach.Affects(lure, a), a.ToString());
        }
        foreach (var card in new CardModel[]
                 { new StrikeIronclad(), new DefendIronclad(), new ProtoYmYakanEvocation(),
                   new ProtoYmTwinSakura(), new ProtoYmGraftedBranch(), new ProtoYmKitsuneFlash(),
                   new ProtoYmPrintRun() })
        {
            Assert.True(YaeAnnotationReach.Affects(card, YaeAnnotation.RedInk), card.GetType().Name);
        }
    }

    [Fact]
    public void The_edit_chooser_reborn_and_the_publish_offer_take_the_filter()
    {
        var affects = $"{nameof(YaeAnnotationReach)}.{nameof(YaeAnnotationReach.Affects)}";
        Assert.Contains(affects, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!));
        Assert.Contains(affects, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!));
        Assert.Contains(affects, Il.Calls(typeof(YaeEditing).GetMethod(
            nameof(YaeEditing.PublishChoices), new[] { typeof(Player) })!));
    }

    [Fact]
    public void The_red_ink_rule_says_where_it_goes()
    {
        Assert.EndsWith("If it only plants, the [gold]Sakura[/gold] gets it.",
                        YaeAnnotationText.TipBody(YaeAnnotation.RedInk, false));
    }
}
