using System;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// SHRINE-R2 SEAT FIXES (lane 4, 2026-10-14; main-session decisions,
/// <c>docs/notes/prototype-surface-provenance.md</c>):
///   1. A Wildfire Tenko's live clause reads per enemy, "18 to each enemy",
///      never "18 to ALL" (a seat read that as one volley split).
///   2. An Edit (the chooser and Reborn as Guuji Yae) never reaches a card
///      with a Published Annotation.
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

    /// <summary>A Published deck card: the Annotation hung on the deck card
    /// itself (the model allocated uninitialised, as the other Yae tests do,
    /// so BaseLib's tables are not touched).</summary>
    private static CardModel PublishedDeck<T>() where T : CardModel, new()
    {
        var deck = Mutable(new T());
        var red = (RedInkAnnotation)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(typeof(RedInkAnnotation));
        Seat.Set(deck, "Enchantment", red);
        return deck;
    }

    // ---- 1. the Wildfire clause --------------------------------------------

    [Fact]
    public void Wildfire_reads_per_enemy_and_plain_tenko_is_unchanged()
    {
        Assert.Equal(": 18 to each enemy", YaeShrineFace.TenkoWords(YaeTenkoKind.Wildfire, 18));
        Assert.Equal("18 to each enemy", YaeShrineFace.Amount(YaeTenkoKind.Wildfire, "18"));
        Assert.DoesNotContain("ALL", YaeShrineFace.TenkoWords(YaeTenkoKind.Wildfire, 18));
        Assert.Equal(" (12 damage)", YaeShrineFace.TenkoWords(YaeTenkoKind.Thunder, 12));
    }

    // ---- 2. an Edit never reaches a Published card -------------------------

    [Fact]
    public void A_card_whose_deck_card_is_annotated_is_published()
    {
        var made = Mutable(new StrikeIronclad());
        Assert.False(YaeEditing.Published(made));          // made in combat

        var plainDeck = Mutable(new StrikeIronclad());
        var plain = Mutable(new StrikeIronclad());
        plain.DeckVersion = plainDeck;
        Assert.False(YaeEditing.Published(plain));         // deck card plain

        var published = Mutable(new StrikeIronclad());
        published.DeckVersion = PublishedDeck<StrikeIronclad>();
        Assert.True(YaeEditing.Published(published));
    }

    [Fact]
    public void Edit_reaches_skip_a_published_card_for_every_annotation()
    {
        var editor = Mutable(new ProtoYmFoxfireLure());
        var plain = Mutable(new StrikeIronclad());
        var published = Mutable(new StrikeIronclad());
        published.DeckVersion = PublishedDeck<StrikeIronclad>();
        foreach (var a in new[] { YaeAnnotation.RedInk, YaeAnnotation.Footnote,
                                  YaeAnnotation.DeadlineExtension, YaeAnnotation.FoxFire,
                                  YaeAnnotation.SakuraSeal, YaeAnnotation.Royalties,
                                  YaeAnnotation.Reprint })
        {
            Assert.True(YaeEditing.EditReaches(plain, editor, a), a.ToString());
            Assert.False(YaeEditing.EditReaches(published, editor, a), a.ToString());
        }
    }

    [Fact]
    public void The_edit_chooser_and_reborn_both_take_the_published_filter()
    {
        var published = $"{nameof(YaeEditing)}.{nameof(YaeEditing.Published)}";
        var reaches = $"{nameof(YaeEditing)}.{nameof(YaeEditing.EditReaches)}";
        Assert.Contains(published, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditReaches))!));
        Assert.Contains(reaches, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!));
        Assert.Contains(reaches, Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!));
    }
}
