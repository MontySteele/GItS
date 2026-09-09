using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-637`, `EB-644`: THE CARD UNDER THE CURSOR MOVES THE PANEL.
///
/// THE FIND. GPT's review of the third pass's frames, 2026-09-07: "FRONT
/// identifies position, but doesn't yet explain the trigger. Companion hover
/// should make that connection." And `EB-637`'s row before it: a card in hand
/// should explain its action on the panel -- a Companion highlights the front
/// member that performs; a Deploy on a full stage marks who leaves.
///
/// WHAT IS REAL HERE. The classification (by the marker interfaces the rules
/// themselves read, never by name), the word every seat gets for every hover
/// on every stage shape (one pure function, exhaustively), the Spotlight's
/// pip count, the generator's mark on every deploy row, and the wiring: four
/// postfixes on the game's own hover tracker, delegating to the panel, scoped
/// to Furina by the predicate the mod already owns.
///
/// WHAT NOTHING HERE CAN VERIFY: whether a lit chip reads as lit at combat
/// scale, and whether the hover arrives in time to matter. Godot nodes cannot
/// be built in this host (KleeTests README); the look is a frame on the next
/// `+proto` deploy, and the scenario runner has no hover step, so the hover
/// frames are [USER]'s own hand.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class SalonPanelHoverTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static readonly int Slots = SalonConstants.MemberSlots;

    /// <summary>An uninitialized card of the class, MUTABLE so that its
    /// `Owner` read answers null the way a hand card with no owner would,
    /// rather than refusing as a canonical model does.</summary>
    private static CardModel Blank<T>() where T : CardModel
    {
        var card = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        Seat.Force(card, "IsMutable", true);
        return card;
    }

    // === 1. what kind of card this is, to the stage ======================

    [Fact]
    public void A_card_is_classified_by_its_marker_and_never_by_its_name()
    {
        // `ICompanionCard` is what `SalonMemberPower.CompanionPlayTrigger`
        // reads; `ISalonDeployCard` is what the generator writes on a row that
        // applies the member power; the Spotlight is its own class. A Furina
        // card that is none of these does nothing to the stage.
        Assert.Equal(SalonPanel.HoverKind.None, SalonPanel.KindOf(null));
        Assert.Equal(SalonPanel.HoverKind.Companion,
                     SalonPanel.KindOf(Blank<GuestNeuvilletteDroplets>()));
        Assert.Equal(SalonPanel.HoverKind.Deploy,
                     SalonPanel.KindOf(Blank<SalonDebut>()));
        Assert.Equal(SalonPanel.HoverKind.Spotlight,
                     SalonPanel.KindOf(Blank<EtherealSpotlight>()));
        Assert.Equal(SalonPanel.HoverKind.None,
                     SalonPanel.KindOf(Blank<AriaOfRecompense>()));

        // And the deploy count is the card's own mark: one for the starter,
        // two for Endless Waltz, none for anything that is not a deploy.
        Assert.Equal(1, SalonPanel.DeployCountOf(Blank<SalonDebut>()));
        Assert.Equal(2, SalonPanel.DeployCountOf(Blank<EndlessWaltz>()));
        Assert.Equal(0, SalonPanel.DeployCountOf(Blank<AriaOfRecompense>()));
        Assert.Equal(0, SalonPanel.DeployCountOf(null));
    }

    [Fact]
    public void Every_generated_deploy_row_carries_the_mark()
    {
        // The generator's promise, read off the generated files rather than
        // trusted: a class whose body calls `SalonMemberPower.Deploy(` declares
        // `ISalonDeployCard`, and a class that declares it calls Deploy.
        // Both generated trees: Furina's shipped rows and the arm's `proto_`
        // rows, which deploy too.
        var files = new[]
            {
                Path.Combine("klee-mod", "KleeCode", "Cards", "Furina",
                             "Generated"),
                Path.Combine("klee-mod", "KleeCode", "Cards", "Prototype",
                             "Generated"),
            }
            .SelectMany(dir => Directory.GetFiles(Find(dir), "*.cs"))
            .ToArray();
        Assert.NotEmpty(files);

        var deploys = 0;
        foreach (var file in files)
        {
            var source = File.ReadAllText(file);
            var calls = source.Contains("SalonMemberPower.Deploy(");
            var marked = source.Contains("ISalonDeployCard");
            Assert.True(calls == marked,
                $"{Path.GetFileName(file)}: deploys={calls} marked={marked}");
            if (marked)
            {
                deploys++;
                Assert.Contains("public int SalonDeployCount =>", source);
            }
        }

        // NINE SINCE `EB-723`, and it was twelve. The Furina reframe's
        // three deploy rows left `docs/prototype-surface.yaml` with the
        // rest of that arm under R213 B's deletion rule, so the floor
        // follows the shipped sheet's nine. It is a FLOOR and not an
        // equality for its original reason: the pin is that the mark
        // and the call cannot come apart, which the loop above checks
        // per file, and this line only refuses a run that found none.
        Assert.True(deploys >= 9, $"only {deploys} deploy rows are marked");
    }

    // === 2. the word on every seat ======================================

    [Theory]
    [InlineData(3, "FRONT", "", "")]
    [InlineData(1, "FRONT", "", "")]
    [InlineData(0, "", "", "")]
    public void With_no_card_chip_zero_says_front_and_nothing_else_speaks(
        int count, string c0, string c1, string c2)
    {
        var kind = SalonPanel.HoverKind.None;
        Assert.Equal(c0, SalonPanel.SlotWord(0, count, Slots, kind, 0));
        Assert.Equal(c1, SalonPanel.SlotWord(1, count, Slots, kind, 0));
        Assert.Equal(c2, SalonPanel.SlotWord(2, count, Slots, kind, 0));
    }

    [Fact]
    public void A_companion_turns_front_into_performs()
    {
        // The trigger, on the seat it fires: a Companion performs the FRONT
        // member, so chip 0 says PERFORMS while one is under the cursor and
        // the other chips say nothing.
        var kind = SalonPanel.HoverKind.Companion;
        Assert.Equal("PERFORMS", SalonPanel.SlotWord(0, 3, Slots, kind, 0));
        Assert.Equal("", SalonPanel.SlotWord(1, 3, Slots, kind, 0));
        Assert.Equal("", SalonPanel.SlotWord(2, 3, Slots, kind, 0));
        // An empty stage has nobody to perform.
        Assert.Equal("", SalonPanel.SlotWord(0, 0, Slots, kind, 0));
    }

    [Fact]
    public void A_deploy_says_who_leaves_a_full_stage_and_which_seat_fills()
    {
        // `SalonMemberPower.Deploy`'s loop, closed: on a full stage the front
        // member is replaced; on a stage with room the first empty seat is
        // taken; a two-member deploy onto a two-of-three stage does one of
        // each. The panel's words agree with the rule seat by seat.
        var kind = SalonPanel.HoverKind.Deploy;

        // Full stage, one deploy: the front leaves, nothing enters visibly.
        Assert.Equal("LEAVES", SalonPanel.SlotWord(0, 3, Slots, kind, 1));
        Assert.Equal("", SalonPanel.SlotWord(1, 3, Slots, kind, 1));
        Assert.Equal("", SalonPanel.SlotWord(2, 3, Slots, kind, 1));

        // Full stage, two deploys: two leave.
        Assert.Equal("LEAVES", SalonPanel.SlotWord(0, 3, Slots, kind, 2));
        Assert.Equal("LEAVES", SalonPanel.SlotWord(1, 3, Slots, kind, 2));
        Assert.Equal("", SalonPanel.SlotWord(2, 3, Slots, kind, 2));

        // Two of three, one deploy: nobody leaves, seat 3 fills, FRONT stays.
        Assert.Equal("FRONT", SalonPanel.SlotWord(0, 2, Slots, kind, 1));
        Assert.Equal("", SalonPanel.SlotWord(1, 2, Slots, kind, 1));
        Assert.Equal("ENTERS", SalonPanel.SlotWord(2, 2, Slots, kind, 1));

        // Two of three, two deploys: the front leaves AND seat 3 fills.
        Assert.Equal("LEAVES", SalonPanel.SlotWord(0, 2, Slots, kind, 2));
        Assert.Equal("", SalonPanel.SlotWord(1, 2, Slots, kind, 2));
        Assert.Equal("ENTERS", SalonPanel.SlotWord(2, 2, Slots, kind, 2));

        // Empty stage, one deploy: seat 1 fills.
        Assert.Equal("ENTERS", SalonPanel.SlotWord(0, 0, Slots, kind, 1));
        Assert.Equal("", SalonPanel.SlotWord(1, 0, Slots, kind, 1));

        // And the words agree with the rule's own closed form.
        using var _ = new Arm();
        var seat = Stage(SalonMember.Crabaletta, SalonMember.Usher,
                         SalonMember.Chevalmarin);
        Assert.True(SalonMemberPower.WillReplace(seat.Creature, 1));
        Assert.Equal("LEAVES", SalonPanel.SlotWord(
            0, SalonPanel.Company(seat.Creature).Count,
            SalonPanel.Slots(seat.Creature), kind, 1));
    }

    [Fact]
    public void Only_the_hover_words_light_a_chip()
    {
        Assert.True(SalonPanel.Highlighted("PERFORMS"));
        Assert.True(SalonPanel.Highlighted("LEAVES"));
        Assert.True(SalonPanel.Highlighted("ENTERS"));
        Assert.False(SalonPanel.Highlighted("FRONT"));
        Assert.False(SalonPanel.Highlighted(""));

        // Every word fits a chip at tier 3, and every word is measured into
        // the chip's width -- a word that widened the box would move the panel.
        foreach (var word in SalonPanel.SlotWords)
        {
            Assert.True(
                FurinaBoardScale.TextWidth(word, FurinaBoardScale.Tier3FontSize)
                    <= SalonPanel.ChipInnerWidth(Slots),
                $"{word} does not fit a chip");
        }
    }

    // === 3. the footer and the pips ======================================

    [Fact]
    public void The_footer_is_the_front_members_price_on_a_full_stage_only()
    {
        // Always a ROW -- the panel's height never moves -- and text only when
        // a deploy would reach the front member. Bright while a Deploy is
        // under the cursor, dim otherwise: that is the whole of the emphasis.
        var full = new List<SalonMember>
        {
            SalonMember.Chevalmarin, SalonMember.Usher, SalonMember.Crabaletta,
        };
        Assert.Equal(SalonPanel.ReplaceText(SalonMember.Chevalmarin),
                     SalonPanel.FooterText(full, Slots));
        Assert.Equal("", SalonPanel.FooterText(full.Take(2).ToList(), Slots));
        Assert.Equal("", SalonPanel.FooterText(new List<SalonMember>(), Slots));

        var source = Source("Vfx/Prototype/SalonPanel.cs");
        Assert.Contains(
            "hover == HoverKind.Deploy ? StsColors.cream : DryText", source);
        Assert.Contains("footer.Text = FooterText(company, slots);", source);
    }

    [Fact]
    public void The_spotlight_tints_the_pips_it_would_spend_and_only_on_hover()
    {
        // `EB-641` took the standing Spotlight mark off the pips -- a claim
        // about one card in a hand that may not hold it. On HOVER the claim is
        // true, so the price is tinted then and never otherwise.
        using var _ = new Arm();
        var seat = Stage(SalonMember.Crabaletta);
        Assert.Equal(0, SalonPanel.SpendPips(seat.Creature));

        var source = Source("Vfx/Prototype/SalonPanel.cs");
        Assert.Contains("pip.Color = i < spend ? PipSpend : PipFull;", source);
        Assert.Contains(
            "if (HoverFor(owner) != HoverKind.Spotlight) return 0;", source);
        Assert.Contains("FurinaReframeLaw.SpotlightDesignateEncoreCost", source);
        Assert.DoesNotContain("SpotlightPips", source);
    }

    // === 4. the front chip's own line ====================================

    [Fact]
    public void The_front_chip_says_the_trigger_in_words_on_its_own_hover()
    {
        // For the player who has not picked up a Companion yet: the rule, as
        // a hover on the chip itself, and the chip is switched to `Pass` so a
        // tooltip can show at all (a control that ignores the mouse shows
        // none) while the click still goes through.
        Assert.Equal("Performs when you play a Companion", SalonPanel.FrontTip);
        Assert.DoesNotContain(".", SalonPanel.FrontTip);

        var source = Source("Vfx/Prototype/SalonPanel.cs");
        Assert.Contains(
            "chip.TooltipText = occupied && front ? FrontTip : string.Empty;",
            source);
        Assert.Contains("? Control.MouseFilterEnum.Pass", source);
    }

    // === 5. the wiring ===================================================

    [Fact]
    public void The_signal_is_the_games_own_hover_tracker_four_postfixes()
    {
        // `NPlayerHand` tells `HoveredModelTracker` about every hover, every
        // pick-up and every release; the panel reads it there rather than
        // patching the hand's private handlers. One postfix each, delegating.
        var source = Source("Vfx/Prototype/SalonPanel.cs");
        foreach (var door in new[]
                 {
                     "OnLocalCardHovered", "OnLocalCardUnhovered",
                     "OnLocalCardSelected", "OnLocalCardDeselected",
                 })
        {
            Assert.Contains(
                $"nameof(HoveredModelTracker.{door}))]", source);
        }

        Assert.Contains("SalonPanel.NoteHovered(cardModel);", source);
        Assert.Contains("SalonPanel.NoteUnhovered();", source);
        Assert.Contains("SalonPanel.NoteSelected(cardModel);", source);
        Assert.Contains("SalonPanel.NoteDeselected();", source);

        // The four reach one repaint, and the repaint is FURINA-SCOPED by
        // the predicate the mod already owns -- the tracker is every seat's.
        var repaint = typeof(SalonPanel).GetMethod("RepaintForHover", All);
        Assert.NotNull(repaint);
        Assert.Contains(Il.Calls(repaint!),
                        c => c.EndsWith("FurinaResources.IsFurina",
                                        StringComparison.Ordinal));
        foreach (var name in new[]
                 {
                     "NoteHovered", "NoteUnhovered", "NoteSelected",
                     "NoteDeselected",
                 })
        {
            var note = typeof(SalonPanel).GetMethod(name, All);
            Assert.NotNull(note);
            Assert.Contains(Il.Calls(note!),
                            c => c.EndsWith("SalonPanel.RepaintForHover",
                                            StringComparison.Ordinal));
        }
    }

    [Fact]
    public void The_played_card_wins_over_the_hovered_one_and_the_fight_forgets()
    {
        // Picking a card up unfocuses the hand under it, so the preview would
        // vanish at the moment it matters if the hover alone were read. The
        // selected card wins; and the teardown forgets both, so the next
        // fight's panel does not open showing a card from the last one.
        Assert.Null(SalonPanel.ActiveCard);
        Note("NoteHovered", Blank<SalonDebut>());
        Assert.IsType<SalonDebut>(SalonPanel.ActiveCard);
        Note("NoteSelected", Blank<GuestNeuvilletteDroplets>());
        Assert.IsType<GuestNeuvilletteDroplets>(SalonPanel.ActiveCard);
        Note("NoteUnhovered");
        Assert.IsType<GuestNeuvilletteDroplets>(SalonPanel.ActiveCard);
        Note("NoteDeselected");
        Assert.Null(SalonPanel.ActiveCard);

        // The teardown forgets both. `Hide` reaches for the live room and is
        // not callable here (the headless boundary), so the forgetting is
        // pinned as the teardown's own first lines.
        var source = Source("Vfx/Prototype/SalonPanel.cs");
        var hide = source.Substring(source.IndexOf("internal static void Hide()",
                                                   StringComparison.Ordinal));
        hide = hide.Substring(0, hide.IndexOf("try", StringComparison.Ordinal));
        Assert.Contains("_hoveredCard = null;", hide);
        Assert.Contains("_selectedCard = null;", hide);
        Assert.Contains("_lastHoverOwner = null;", hide);
    }

    // --- harness ---------------------------------------------------------

    /// <summary>The panel's hover doors are `internal` (the postfixes are
    /// their only callers), so the pin reaches them by name.</summary>
    private static void Note(string door, params object?[] args) =>
        typeof(SalonPanel).GetMethod(door, All)!.Invoke(null, args);

    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;

        internal Arm()
        {
            FurinaReframe.Enabled = true;
            FurinaReframe.ManualEnabled = true;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
        }
    }

    private static Seat Stage(params SalonMember[] members)
    {
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        Seat.Force(power, "Amount", members.Length);
        ((System.Collections.IList)seat.Creature.Powers).Add(power);
        Seat.Force(power, "IsMutable", true);
        Seat.Force(power, "Owner", seat.Creature);

        ((IDictionary<MegaCrit.Sts2.Core.Entities.Creatures.Creature,
                      List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", All)!
            .GetValue(null)!)[seat.Creature] = members.ToList();
        return seat;
    }

    private static string Source(string relativePath) =>
        File.ReadAllText(Find(Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', Path.DirectorySeparatorChar))));

    private static string Find(string relative)
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, relative);
            if (File.Exists(candidate) || Directory.Exists(candidate))
            {
                return candidate;
            }

            dir = dir.Parent;
        }

        throw new FileNotFoundException(relative);
    }
}
