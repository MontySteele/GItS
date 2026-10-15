using System;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE REVIEW R4, items 1 to 8 (review/active/yae-review-r4-2026-10-15.md).
/// Sim twin: <c>tier0/tests/test_yae_review_r4.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR4Tests : IDisposable
{
    public YaeReviewR4Tests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    [Fact]
    public void The_publish_grid_never_has_to_pick_so_the_game_cannot_answer_it()
    {
        // Item 1: a grid of one card with a minimum of one was answered by
        // the game; the minimum is zero, the pick is confirmed by hand, and
        // the grid may be closed. At most `max` picks resolve.
        var prefs = Il.CallSequence(typeof(YaePublishReward).GetMethod(nameof(YaePublishReward.Prefs))!).ToList();
        Assert.Contains(prefs, c => c.Contains("set_RequireManualConfirmation"));
        Assert.Contains(prefs, c => c.Contains("set_Cancelable"));
        var il = Il.CallSequence(typeof(YaePublishReward).GetMethod("OnSelect",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!).ToList();
        Assert.Contains(il, c => c.Contains("Take"));
    }

    [Fact]
    public void A_refreshed_oldest_takes_the_planting_cards_red_ink()
    {
        var ledger = Fresh();
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk));
        Assert.Equal(YaeAnnotation.RedInk, ledger.Standing[0].Annotation);
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None));
        Assert.Equal(YaeAnnotation.RedInk, ledger.Standing[0].Annotation);
    }

    [Fact]
    public void A_deadline_edit_that_keeps_red_ink_keeps_the_three()
    {
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk);
        var s = ledger.Standing[0];
        var before = YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotation, s.KeepsRedInk);
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Oldest, 1,
                                          YaeAnnotation.DeadlineExtension, keepRedInk: true));
        Assert.Equal(YaeAnnotation.DeadlineExtension, s.Annotation);
        Assert.Equal(before, YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotation, s.KeepsRedInk));
        // An Edit that does not keep it ends it.
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.FoxFire);
        Assert.False(s.KeepsRedInk);
        // Nothing to keep on a plain Sakura.
        var t = Fresh();
        t.Plant(YaeLaw.PlantLevel);
        t.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension, keepRedInk: true);
        Assert.False(t.Standing[0].KeepsRedInk);
    }

    [Fact]
    public void An_edit_with_nothing_to_edit_says_so()
    {
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!),
                        c => c.Contains(nameof(YaeEditing.SayNothing)));
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!),
                        c => c.Contains(nameof(YaeEditing.SayNothing)));
        Assert.Equal(0, Fresh().EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.RedInk));
    }

    [Fact]
    public void Every_edit_prompt_warns_it_replaces()
    {
        foreach (var a in YaeAnnotationText.All)
        {
            Assert.EndsWith(YaeEditing.ReplacesWarning, YaeEditing.EditPromptTextFor(a));
        }
    }

    // The Seven Glamours, 2026-10-15 ([USER]: "it looks obviously OP - I
    // thought it was Publishing one card per fight, not the whole hand"):
    // one card, chosen, on a kill. Behaviour (kill, no kill, Minion): the sim
    // twin's test_seven_glamours_*.

    [Fact]
    public void The_seven_glamours_publishes_one_chosen_card()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.PublishFromHand))!).ToList();
        Assert.Contains(calls, c => c.Contains("CardSelectCmd.FromHand"));
        Assert.Equal(1, calls.Count(c => c.Contains(nameof(YaeEditing.PublishLayer))));
    }

    [Fact]
    public void The_seven_glamours_publishes_only_on_a_fatal_kill()
    {
        var card = typeof(global::KleeMod.Cards.Prototype.Generated.ProtoYmTheSevenGlamours);
        var onPlay = Il.CallSequence(card.GetMethod("OnPlay", HeadlessGame.All)!).ToList();
        Assert.Contains(onPlay, c => c.Contains("DamageCmd.Attack"));
        Assert.Contains(onPlay, c => c.Contains("YaeCards.Publish"));
        // Hand of Greed's gate: the snapshot asks each enemy's powers
        // whether its death triggers Fatal (MinionPower says no).
        var lambdas = card.GetNestedTypes(HeadlessGame.All)
            .SelectMany(t => t.GetMethods(HeadlessGame.All))
            .SelectMany(Il.CallSequence);
        Assert.Contains(lambdas, c => c.Contains("ShouldOwnerDeathTriggerFatal"));
    }
}
