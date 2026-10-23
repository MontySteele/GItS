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
/// YAE REVIEW R6, items 1 to 5 (review/active/yae-review-r6-2026-10-15.md).
/// Sim and page twin: <c>tier0/tests/test_yae_review_r6.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR6Tests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    [Fact]
    public void Serialization_is_per_edit()
    {
        Assert.Equal("Whenever you [gold]Edit[/gold] a card, gain {PowerAmount:diff()} "
                     + "[gold]Block[/gold].", Face(new ProtoYmSerialization()));
        var power = new SerializationPower();
        Assert.Equal("Whenever you [gold]Edit[/gold] a card, gain [blue]{Amount}[/blue] "
                     + "[gold]Block[/gold].",
                     power.Localization!.First(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void Manuscript_pile_draws_then_edits_red_ink()
    {
        Assert.Equal("Draw {Cards:diff()} cards. [gold]Edit[/gold] a card in your [gold]Hand[/gold]: "
                     + "[gold]Red Ink[/gold].", Face(new ProtoYmManuscriptPile()));
        var calls = Il.CallSequence(typeof(ProtoYmManuscriptPile).GetMethod(
            "OnPlay", HeadlessGame.All)!).ToList();
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        var edit = calls.FindIndex(c => c.Contains("YaeCards.Edit"));
        Assert.True(draw >= 0 && edit > draw, string.Join(", ", calls));
        Assert.DoesNotContain(calls, c => c.Contains("YaeCards.Extend"));
    }

    [Fact]
    public void Meditations_says_nothing_to_publish()
    {
        Assert.Equal("Nothing to Publish.", YaeEditing.NothingToPublishText);
        var calls = Il.CallSequence(typeof(MeditationsOfAYako).GetMethod(
            nameof(MeditationsOfAYako.TryModifyRewards))!).ToList();
        Assert.Contains(calls, c => c.Contains("Flash"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.SayNothing)));
        // The seat page's read.
        Assert.Contains(Il.Calls(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Snapshot))!),
                        c => c.Contains(nameof(MeditationsOfAYako.NothingToPublish)));
    }

    [Fact]
    public void Reprint_says_each_one_adds_a_play()
    {
        Assert.Equal("The first time this card is played each combat, play it once "
                     + "more for each Reprint.",
                     YaeAnnotationText.Rule(YaeAnnotation.Reprint));
    }

    [Fact]
    public void The_seat_sakura_tip_names_its_target_and_the_player_tip_stays_short()
    {
        Assert.Equal("A Sakura strikes Kitsune Pounce's target when Pounce makes it "
                     + "strike, else the enemy Foxfire Lure marked this turn, else "
                     + "(with Hunting Gaze) the last enemy your Attacks hit, else a "
                     + "random enemy.", ArmKeywordTips.YaeSakuraTargetRule);
        Assert.True(ArmKeywordTips.YaeSakuraTip.Length <= 100);
    }
}
