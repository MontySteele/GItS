using System.Linq;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
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
