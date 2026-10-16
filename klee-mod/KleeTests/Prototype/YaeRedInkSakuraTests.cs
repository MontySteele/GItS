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
    public void Only_red_ink_on_a_planting_card_inherits()
    {
        // Widened 2026-10-14 (main session, after a GPT design review): a
        // planting card that also deals damage or gives Block passes Red
        // Ink to its Sakura too, keeping its own +3.
        Assert.True(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, false, false, true));
        Assert.True(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, false, true, true));
        Assert.True(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, true, false, true));
        Assert.True(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, true, true, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.FoxFire, false, false, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.DeadlineExtension, false, false, true));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, false, false, false));
        Assert.False(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk, true, true, false));
    }

    [Fact]
    public void A_red_ink_plant_plants_a_red_ink_sakura()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk));
        var s = Assert.Single(ledger.Standing);
        Assert.Equal(new[] { YaeAnnotation.RedInk }, s.Annotations);
        Assert.Equal(YaeLaw.SakuraBase + s.Level + YaeLaw.RedInkAmount,
                     YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotations));
    }

    [Fact]
    public void Twin_sakuras_two_plants_both_inherit()
    {
        // YaeShrine.Plant plants n one at a time, each with the inherited
        // Annotation: Twin Sakura's two.
        var ledger = Fresh();
        for (var i = 0; i < 2; i++) ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk);
        Assert.All(ledger.Standing, s => Assert.Equal(new[] { YaeAnnotation.RedInk }, s.Annotations));
        Assert.Equal(2, ledger.Count);
    }

    [Fact]
    public void A_full_shrine_plant_that_feeds_the_oldest_gives_it_the_red_ink()
    {
        // Yae review r4, item 2: the refreshed oldest Sakura takes the Red
        // Ink (it was inherited by none).
        var ledger = Fresh();
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk));
        Assert.Equal(new[] { YaeAnnotation.RedInk }, ledger.Standing[0].Annotations);
        Assert.All(ledger.Standing.Skip(1), s => Assert.Empty(s.Annotations));
    }

    [Fact]
    public void The_planting_verbs_pass_the_cards_inheritance()
    {
        // Review r3: each verb has a kind-taking overload, which carries the
        // inheritance; the plain one forwards to it. The pool to 78:
        // PlantLevel is one method whose kind (and Grafted Branch's extra
        // turn) are optional, and its new planters carry it too.
        foreach (var verb in new[] { nameof(YaeCards.Plant), nameof(YaeCards.PlantLevel),
                                     nameof(YaeCards.Replant), nameof(YaeCards.PlantMissing),
                                     nameof(YaeCards.PlantUntilFull) })
        {
            var kinded = typeof(YaeCards).GetMethods()
                .Where(m => m.Name == verb)
                .OrderByDescending(m => m.GetParameters().Length).First();
            Assert.Contains($"{nameof(YaeAnnotationReach)}.{nameof(YaeAnnotationReach.Inherited)}",
                            Il.Calls(kinded));
        }
        // The Masterpiece's Sakura Seal plant passes nothing on.
        Assert.DoesNotContain($"{nameof(YaeAnnotationReach)}.{nameof(YaeAnnotationReach.Inherited)}",
            Il.Calls(typeof(YaeMasterpiece).GetMethod("OnPlay")!));
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
    public void Twin_sakura_upgraded_gives_block_and_still_passes_red_ink()
    {
        var twin = new ProtoYmTwinSakura();
        Upgrade(twin);
        Assert.True(YaeAnnotationReach.GivesBlock(twin));
        Assert.True(YaeAnnotationReach.Plants(twin));
        Assert.True(YaeAnnotationReach.Affects(twin, YaeAnnotation.RedInk));
        // Red Ink rides its Block AND reaches both Sakura (2026-10-14).
        Assert.True(YaeAnnotationReach.Inherits(YaeAnnotation.RedInk,
            YaeAnnotationReach.DealsDamage(twin), YaeAnnotationReach.GivesBlock(twin),
            YaeAnnotationReach.Plants(twin)));
    }

    [Fact]
    public void Print_runs_own_block_counts_for_red_ink()
    {
        // Since 2026-10-15 Print Run's Block is a CalculatedBlockVar (its
        // face shows the total in combat), so the game's own GainsBlock
        // answers, as on Expect a Fight; tier0's Nimble predicate agrees.
        var run = new ProtoYmPrintRun();
        Assert.True(run.GainsBlock);
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
                                  YaeAnnotation.Royalties, YaeAnnotation.Reprint })
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
        // The Edit chooser and Reborn read the filter through EditReaches.
        var reaches = $"{nameof(YaeEditing)}.{nameof(YaeEditing.EditReaches)}";
        Assert.Contains(affects, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditReaches))!));
        Assert.Contains(reaches, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!));
        Assert.Contains(reaches, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!));
        Assert.Contains(affects, Il.Calls(typeof(YaeEditing).GetMethod(
            nameof(YaeEditing.PublishChoices), new[] { typeof(Player) })!));
    }

    [Fact]
    public void The_red_ink_rule_says_where_it_goes()
    {
        Assert.EndsWith("If it plants, its [gold]Sakura[/gold] get it too.",
                        YaeAnnotationText.TipBody(YaeAnnotation.RedInk, false));
    }
}
