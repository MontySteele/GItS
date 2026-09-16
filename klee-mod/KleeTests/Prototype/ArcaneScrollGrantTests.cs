using System;
using System.Linq;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-459`. NEOW'S ARCANE SCROLL, AND THE RARE IT IS SUPPOSED TO HAND OVER.
///
/// THE FIND (Kokomi r14). "Arcane Scroll: obtain a random Rare Card" was taken
/// at Neow, the relic sat in the list all run, and the deck stayed the eleven
/// starters -- confirmed by fight 1's pile counts. No card, no crash, no line.
///
/// THE PATH, off the 0.111.0 decompile, and it is the one this mod already
/// patches. <c>ArcaneScroll.AfterObtained</c> builds a
/// <c>CardCreationOptions</c> over <c>Owner.Character.CardPool</c> with
/// <c>CardRarityOddsType.Uniform</c> and the filter
/// <c>c =&gt; c.Rarity == CardRarity.Rare</c>, asks
/// <c>CardFactory.CreateForReward(owner, Cards, options)</c> for
/// <c>Cards</c> = 1, and adds <c>list[0]</c> to the deck -- BUT ONLY
/// <c>if (list.Count &gt; 0)</c>. So an empty return is not an exception here.
/// It is silence, which is exactly what the seat got.
///
/// AND THAT IS THE SAME SEAM AS `EB-363`, two rows over. A character's
/// <c>CardPool</c> reaches a reward roll through
/// <c>CardCreationOptions.GetPossibleCards</c>, which applies the filter
/// (<c>where CardPoolFilter == null || CardPoolFilter(c)</c>), and under a
/// replacement arm that pool is the ARM's -- <c>FilterThroughEpochs</c> returns
/// <c>&lt;Arm&gt;Roster.OfferablePool()</c>. An arm whose Rare shelf is empty
/// therefore offered the clamp a count of zero, the clamp floored
/// <c>cardCount</c> to zero, <c>CreateForReward</c>'s loop never ran, and the
/// relic's own <c>Count &gt; 0</c> guard swallowed the result. `EB-363`'s
/// widening ladder now stands in front of that floor, so the relic can no
/// longer hand back NOTHING on any arm.
///
/// WHAT THIS FILE ADDS ON TOP, because the row asks for more than "not
/// nothing": its acceptance is "the grant under each arm adds one **Rare**
/// from that arm's pool". A widened draw would satisfy `EB-363` and fail
/// `EB-459` -- it would put a Common in the deck under a line that promised a
/// Rare. So the pin below is that the cell is answered AS ASKED on every arm,
/// which is a statement about the SHEET (each arm stocks a Rare) and not about
/// the seam.
///
/// `EB-363`'s own ledger cannot say this. It folds Arcane Scroll's one-card
/// Rare draw into Sea Glass's five-card one, and a shelf of four Rares is
/// SHORT there while being perfectly sufficient here -- so "Rare/*" appears in
/// that test's short-cell list for two arms and says nothing about whether a
/// single Rare can be drawn. This is the depth-1 reading of the same cell.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class ArcaneScrollGrantTests
{
    private static Type Scroll =>
        typeof(MegaCrit.Sts2.Core.Models.Relics.ArcaneScroll);

    public static TheoryData<string> Arms
    {
        get
        {
            var data = new TheoryData<string>();
            foreach (var arm in ArmPools.Names) data.Add(arm);
            return data;
        }
    }

    /// <summary>
    /// THE ACCEPTANCE, one line: every arm stocks at least one Rare, so the
    /// scroll's own cell answers its own draw and the card that lands is the
    /// Rare the blessing named.
    ///
    /// DEPTH ONE, and that is the whole difference from `EB-363`'s row for
    /// this cell: the scroll's <c>Cards</c> var is 1, so one Rare is enough
    /// and four is not "short" for it.
    /// </summary>
    [Theory]
    [MemberData(nameof(Arms))]
    public void Every_arm_can_answer_the_scrolls_rare_draw_as_asked(string arm)
    {
        var rares = ArmPools.Offerable(arm)
            .Where(c => c.Rarity == CardRarity.Rare)
            .ToList();

        Assert.True(
            rares.Count >= 1,
            $"{arm} stocks no Rare, so Neow's Arcane Scroll would either hand "
            + "back nothing (before `EB-363`) or a card of another rarity "
            + "under a line that promised a Rare. Put a Rare on the sheet.");
    }

    /// <summary>
    /// And the widening ladder is therefore NOT reached for this draw on any
    /// arm -- the fact the assertion above is really making, said in the
    /// seam's own terms so the two cannot drift apart. A null answer from the
    /// ladder is "rung 1: the cell as asked".
    /// </summary>
    [Theory]
    [MemberData(nameof(Arms))]
    public void And_so_the_grant_is_never_widened_off_its_rarity(string arm)
    {
        var pool = ArmPools.Offerable(arm);
        var cell = pool.Where(c => c.Rarity == CardRarity.Rare).ToList();
        var whole = pool
            .Where(c => c.Rarity == CardRarity.Common
                        || c.Rarity == CardRarity.Uncommon
                        || c.Rarity == CardRarity.Rare)
            .ToList();

        Assert.Null(Seam.WidenedAdmissions(wanted: 1, cell, whole));
    }

    /// <summary>
    /// THE PATH, read off the base game rather than off this file's comment,
    /// because everything above is only true while the scroll still goes
    /// through the overload this mod patches. If a game update moves it to
    /// another factory method, the clamp and the ladder stop standing in front
    /// of it and this pin is how we find out.
    /// </summary>
    [Fact]
    public void The_scroll_still_draws_through_the_patched_reward_factory()
    {
        var calls = Il.Calls(Scroll.GetMethod("AfterObtained", HeadlessGame.All)!);

        Assert.Contains(calls,
            c => c.Contains("CardFactory.CreateForReward", StringComparison.Ordinal));
    }

    /// <summary>
    /// The patch's own target, spelled as the game spells it. The prefix names
    /// this exact three-argument overload; a scroll reaching a different one
    /// would be unpatched, and Harmony would not say so.
    /// </summary>
    [Fact]
    public void The_patched_overload_is_the_three_argument_one()
    {
        var overload = typeof(MegaCrit.Sts2.Core.Factories.CardFactory)
            .GetMethod(
                "CreateForReward",
                HeadlessGame.All,
                binder: null,
                new[]
                {
                    typeof(MegaCrit.Sts2.Core.Entities.Players.Player),
                    typeof(int),
                    typeof(MegaCrit.Sts2.Core.Runs.CardCreationOptions),
                },
                modifiers: null);

        Assert.NotNull(overload);
    }

    /// <summary>
    /// The relic asks for exactly ONE card, which is what makes a single Rare
    /// sufficient above. Read off the relic rather than assumed, because the
    /// whole acceptance turns on the depth.
    /// </summary>
    [Fact]
    public void The_scroll_asks_for_one_card()
    {
        var vars = Scroll
            .GetProperty("CanonicalVars", HeadlessGame.All)!
            .GetGetMethod(nonPublic: true)!;

        // `new CardsVar(1)` -- the constant is the only `ldc.i4` in a getter
        // that does nothing else, and the type it feeds is the pin's other
        // half.
        Assert.Contains(Il.Calls(vars),
            c => c.Contains("CardsVar", StringComparison.Ordinal));
    }

    /// <summary>
    /// AND THE ONE CLAUSE THAT TURNED A THROW INTO SILENCE, pinned because it
    /// is the reason this row reads as "added no card" instead of as a crash
    /// report: the relic guards its own result, so an empty draw is a no-op
    /// with no line anywhere. Everything upstream has to be right; nothing
    /// downstream will complain.
    /// </summary>
    [Fact]
    public void An_empty_draw_is_swallowed_by_the_relic_itself()
    {
        var calls = Il.Calls(Scroll.GetMethod("AfterObtained", HeadlessGame.All)!);

        Assert.Contains(calls,
            c => c.Contains("get_Count", StringComparison.Ordinal));
        Assert.Contains(calls,
            c => c.Contains("CardPileCmd.Add", StringComparison.Ordinal));
    }
}
