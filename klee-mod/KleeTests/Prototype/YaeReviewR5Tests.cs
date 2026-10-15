using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE REVIEW R5, items 2, 5 and 6 (review/active/yae-review-r5-2026-10-15.md).
/// Sim and page twin: <c>tier0/tests/test_yae_review_r5.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR5Tests
{
    [Fact]
    public void Inked_branches_plus_says_nothing_to_edit_once()
    {
        // Item 2: the hand half may stay quiet; it speaks by default.
        var edit = typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!;
        var quiet = edit.GetParameters().Single(p => p.Name == "sayNothing");
        Assert.True(quiet.HasDefaultValue);
        Assert.Equal(true, quiet.DefaultValue);
        // EditSakura still has its own Sakura bubble and still Edits the hand.
        var calls = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.EditSakura))!).ToList();
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.SayNothing)));
        Assert.Contains(calls, c => c.Contains("YaeEditing.Edit"));
    }

    [Fact]
    public void The_full_shrine_tip_is_the_long_form()
    {
        Assert.Equal("Planting makes your oldest Sakura act. If the new Sakura is "
                     + "the same kind, the oldest stays and gains a Level. If not, "
                     + "the oldest withers and the new one takes its place.",
                     ArmKeywordTips.YaeFullShrineTip);
    }

    [Fact]
    public void Meditations_says_the_annotation_was_made_that_fight()
    {
        Assert.Equal("After an elite or boss fight, you may [gold]Publish[/gold] "
                     + "an Annotation you made that fight.",
                     MeditationsOfAYako.DescriptionText);
        Assert.Equal("After an elite or boss fight, you may [gold]Publish[/gold] "
                     + "up to 2 Annotations you made that fight.",
                     EnlightenedBlessing.DescriptionText);
    }
}

/// <summary>
/// YAE REVIEW R5, PICK 1 (a), ruled 2026-10-15 ([USER]: "For 1332 - agreed on
/// (a)"): Bestseller and Print Run count the cards you Edited this combat
/// (<see cref="YaeShrineLedger.Edits"/>), not the Annotated cards in hand.
/// Sim twin: the pick-1 tests in <c>tier0/tests/test_yae_review_r5.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR5Pick1Tests : IDisposable
{
    public YaeReviewR5Pick1Tests()
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

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    [Fact]
    public void Bestseller_and_print_run_are_8_and_6_plus_2_per_edit_upgraded_10_and_8_plus_3()
    {
        foreach (var (card, lo, hi) in new (CardModel, int, int)[]
                 { (new ProtoYmBestseller(), 8, 10), (new ProtoYmPrintRun(), 6, 8) })
        {
            Assert.Equal(lo, (int)card.DynamicVars["YmBase"].BaseValue);
            Assert.Equal(2, (int)card.DynamicVars["YmPer"].BaseValue);
            Assert.Contains("plus {YmPer:diff()} for each card you [gold]Edited[/gold] this combat.",
                            Face(card));
            Upgrade(card);
            Assert.Equal(hi, (int)card.DynamicVars["YmBase"].BaseValue);
            Assert.Equal(3, (int)card.DynamicVars["YmPer"].BaseValue);
        }
    }

    [Fact]
    public void The_payoffs_read_the_edit_count_not_the_hand()
    {
        foreach (var name in new[] { nameof(YaeCards.DamagePerEdit), nameof(YaeCards.BlockPerEdit) })
        {
            var calls = Il.Calls(typeof(YaeCards).GetMethod(name)!);
            Assert.Contains(calls, c => c.Contains("YaeShrine.Edits"));
            Assert.DoesNotContain(calls, c => c.Contains("IsAnnotated"));
        }
        Assert.Contains(Il.Calls(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Edits))!),
                        c => c.Contains("get_Edits"));
        Assert.Contains(Il.Calls(Il.Method("ProtoYmBestseller", "OnPlay")),
                        c => c.Contains(nameof(YaeCards.DamagePerEdit)));
        Assert.Contains(Il.Calls(Il.Method("ProtoYmPrintRun", "OnPlay")),
                        c => c.Contains(nameof(YaeCards.BlockPerEdit)));
    }

    [Fact]
    public void The_count_starts_at_0_each_combat_and_each_sakura_edited_counts()
    {
        var ledger = Fresh();
        Assert.Equal(0, ledger.Edits);
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        // Inked Branches: "Edit every Sakura: Red Ink" counts each Sakura.
        Assert.Equal(3, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.RedInk));
        Assert.Equal(3, ledger.Edits);
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Newest, 1, YaeAnnotation.FoxFire));
        Assert.Equal(4, ledger.Edits);
        // An Annotation with no Sakura reading Edits none and counts none.
        Assert.Equal(0, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.Footnote));
        Assert.Equal(4, ledger.Edits);
        // A new combat is a new ledger (the test seam stands for it).
        YaeShrineLedger.ResetAll();
        Assert.Equal(0, Fresh().Edits);
    }

    [Fact]
    public void Each_card_an_edit_annotates_counts_and_a_publish_does_not()
    {
        // "Edit up to N cards" notes one Edit per card it Annotates (a 2-card
        // Edit adds 2), Reborn one per card; the Publish paths note none.
        Assert.Contains(Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!),
                        c => c.Contains("NoteEdit"));
        Assert.Contains(Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!),
                        c => c.Contains("NoteEdit"));
        var note = typeof(YaeShrineLedger).GetMethod("NoteEdit", HeadlessGame.All)!;
        var ledger = Fresh();
        note.Invoke(ledger, null);
        note.Invoke(ledger, null);
        Assert.Equal(2, ledger.Edits);
        foreach (var name in new[] { nameof(YaeEditing.PublishFromHand),
                                     nameof(YaeEditing.PublishLayer),
                                     nameof(YaeEditing.PublishToDeck) })
        {
            Assert.DoesNotContain(Il.Calls(typeof(YaeEditing).GetMethod(name)!),
                                  c => c.Contains("NoteEdit"));
        }
    }
}
