using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
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
        // The Sakura Levels paper (2026-10-17): Levels carry over.
        Assert.Equal("Planting makes the Sakura closest to withering act. Same "
                     + "kind: it refreshes and gains a Level. Other kind: it "
                     + "withers, and the new one takes its Level if higher.",
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
    public void Bestseller_is_8_plus_2_per_edit_upgraded_10_plus_3()
    {
        // Since 2026-10-15 on the calculated rail (Perfected Strike's): the
        // base is CalculationBase, the per-Edit slope ExtraDamage, and in
        // combat the face adds the total. (Print Run, its Block twin, was
        // cut by the dedupe, 2026-10-16.)
        foreach (var (card, perVar, lo, hi, total) in new (CardModel, string, int, int, string)[]
                 { (new ProtoYmBestseller(), "ExtraDamage", 8, 10,
                    "{InCombat:\n(Deals {CalculatedDamage:diff()} damage)|}") })
        {
            Assert.Equal(lo, (int)card.DynamicVars["CalculationBase"].BaseValue);
            Assert.Equal(2, (int)card.DynamicVars[perVar].BaseValue);
            Assert.Contains($"plus {{{perVar}:diff()}} for each card you [gold]Edited[/gold] this combat.",
                            Face(card));
            Assert.EndsWith(total, Face(card));
            Upgrade(card);
            Assert.Equal(hi, (int)card.DynamicVars["CalculationBase"].BaseValue);
            Assert.Equal(3, (int)card.DynamicVars[perVar].BaseValue);
        }
    }

    /// <summary>The calculated var's multiplier, the "for each" count the
    /// game multiplies the slope by (`CalculatedVar._multiplierCalc`).</summary>
    private static decimal Multiplier(CardModel card, string name) =>
        ((Func<CardModel, Creature?, decimal>)typeof(CalculatedVar)
            .GetField("_multiplierCalc", HeadlessGame.All)!
            .GetValue(card.DynamicVars[name])!)(card, null);

    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    [Fact]
    public void The_faces_total_is_base_plus_per_for_each_edit_this_combat()
    {
        // 0 Edits: the base. 3 Edits: base + 3 x per (8 + 3 x 2 = 14
        // damage), the number the play pays.
        var seat = Seat.Yae();
        var bestseller = Owned<ProtoYmBestseller>(seat);
        var ledger = YaeShrineLedger.For(seat.Creature);
        Assert.Equal(0, ledger.Edits);
        Assert.Equal(0m, Multiplier(bestseller, "CalculatedDamage"));
        var note = typeof(YaeShrineLedger).GetMethod("NoteEdit", HeadlessGame.All)!;
        for (var i = 0; i < 3; i++) note.Invoke(ledger, null);
        Assert.Equal(3m, Multiplier(bestseller, "CalculatedDamage"));
        Assert.Equal(14m, bestseller.DynamicVars["CalculationBase"].BaseValue
                          + bestseller.DynamicVars["ExtraDamage"].BaseValue
                            * Multiplier(bestseller, "CalculatedDamage"));
        // Out of a fight the game computes no multiplier: the base, and the
        // face's {InCombat:} clause is hidden.
        Assert.Equal(8m, ((CalculatedVar)bestseller.DynamicVars["CalculatedDamage"]).Calculate(null));
        // Someone who is not Yae counts none.
        var other = Owned<ProtoYmBestseller>(Seat.Klee());
        Assert.Equal(0m, Multiplier(other, "CalculatedDamage"));
    }

    [Fact]
    public void The_payoffs_read_the_edit_count_not_the_hand()
    {
        Assert.Contains(Il.Calls(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Edits))!),
                        c => c.Contains("get_Edits"));
        // The plays pay the calculated var (the number the face shows).
        Assert.Contains(Il.Calls(Il.Method("ProtoYmBestseller", "OnPlay")),
                        c => c.Contains("CalculatedDamage"));
    }

    [Fact]
    public void The_seat_page_snapshot_carries_the_edit_count_only_for_yae_in_a_fight()
    {
        // Outside a fight (no CombatState in this harness) the map is empty,
        // so a map-screen poll never resets her ledger; another character's
        // is always empty.
        Assert.Empty(YaeShrine.Snapshot(Seat.Yae().Player));
        Assert.Empty(YaeShrine.Snapshot(Seat.Klee().Player));
        Assert.Empty(YaeShrine.Snapshot(null));
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
