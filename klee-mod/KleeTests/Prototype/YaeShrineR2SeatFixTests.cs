using System;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// SHRINE-R2 SEAT FIXES (lane 4, 2026-10-14), AS REVIEW R3 LEFT THEM:
///   1. The Wildfire clause's "to each enemy" lives on as a Foxfire Sakura's
///      words in the plain Tenko clause; the typed Tenko is gone.
///   2. #1308's "an Edit never reaches a Published card" is REPLACED (review
///      r3, pick 2 (a)): an Edit on a Published card fills its temporary
///      slot, which a later Edit replaces and a Publish moves onto the stack.
/// The sim half is <c>tier0/tests/test_yae_shrine_r2_seat_fixes.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeShrineR2SeatFixTests : IDisposable
{
    public YaeShrineR2SeatFixTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
    }

    private static T Mutable<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    [Fact]
    public void A_foxfire_sakura_reads_per_enemy()
    {
        Assert.Equal("18 to each enemy", YaeShrineFace.Amount(YaeSakuraKind.Foxfire, "18"));
        Assert.DoesNotContain("ALL", YaeShrineFace.TenkoWords(12, 18));
        Assert.Equal(" (Sakura: 12 damage in total)", YaeShrineFace.TenkoWords(12));
    }

    [Fact]
    public void Edit_reaches_a_published_card_for_every_annotation()
    {
        var editor = Mutable(new ProtoYmFoxfireLure());
        var plain = Mutable(new StrikeIronclad());
        foreach (var a in YaeAnnotationText.All)
        {
            Assert.True(YaeEditing.EditReaches(plain, editor, a), a.ToString());
        }
        // The Published filter is gone from the chooser and Reborn.
        var published = $"{nameof(YaeEditing)}.{nameof(YaeEditing.Published)}";
        Assert.DoesNotContain(published, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditReaches))!));
        var reaches = $"{nameof(YaeEditing)}.{nameof(YaeEditing.EditReaches)}";
        Assert.Contains(reaches, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!));
        Assert.Contains(reaches, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!));
    }

    [Fact]
    public void An_edit_keeps_the_stack_and_replaces_only_the_temporary_slot()
    {
        // Annotate reads the card's stack and hands it to the fresh model.
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Annotate))!).ToList();
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.Stack)));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.Apply)));
        Assert.Equal(new[] { YaeAnnotation.RedInk, YaeAnnotation.Footnote },
                     YaeLayers.All(new[] { YaeAnnotation.RedInk }, YaeAnnotation.Footnote));
    }
}
