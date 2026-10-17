using System;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.ControllerInput;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE PLANS VIEW (2026-10-14). [USER]: "I do actually play on controller and
/// I've never flipped a plan myself - let's handle that focus change sooner
/// rather than later so it's accessible during my runs."
///
/// The game's peek button (left stick press by default) opens a card grid of
/// every waiting Plan; A flips a two-line Plan through the strip's own
/// co-op-safe request and the view stays open; B or Confirm closes. The strip
/// itself stays out of the focus walk (`EB-300`).
///
/// Headless: which Plans the view shows, in what order, which flip, what each
/// caption says, and where the strip's hint sits are pure; the wiring is
/// pinned off the compiled methods (<c>Il</c>). How the grid looks, and that
/// the button reaches the view in a live combat, are live questions.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPlanViewTests
{
    private static readonly KokomiPlan.Planned[] OneHit =
    {
        new(KokomiPlan.Kind.Damage, 7, KokomiPlan.Aim.AllEnemies),
    };

    private static KokomiPlan.Entry Plan(CardModel? card, bool now = false,
                                         CardModel? writer = null) =>
        new(card, OneHit, Writer: writer, Now: now);

    // ---- what the view shows, and in what order -----------------------------

    [Fact]
    public void The_view_shows_every_plan_with_a_card_in_queue_order()
    {
        var oath = new ProtoKkKuragesOath();
        var stroke = new ProtoKkMasterstroke();
        var oath2 = new ProtoKkKuragesOath();
        var queue = new[] { Plan(oath), Plan(stroke), Plan(oath2) };
        Assert.Equal(new[] { 0, 1, 2 }, KokomiPlanViewRows.Shown(queue));
        Assert.Same(oath, KokomiPlanViewRows.Face(queue[0]));
    }

    [Fact]
    public void A_plan_with_no_card_is_left_out_and_a_written_plan_shows_its_writer()
    {
        var writer = new ProtoKkMasterstroke();
        var oath = new ProtoKkKuragesOath();
        var queue = new[] { Plan(null), Plan(null, writer: writer), Plan(oath) };
        Assert.Equal(new[] { 1, 2 }, KokomiPlanViewRows.Shown(queue));
        Assert.Same(writer, KokomiPlanViewRows.Face(queue[1]));
        Assert.Equal(1, KokomiPlanViewRows.QueueIndex(queue, writer));
    }

    [Fact]
    public void One_card_names_one_plan()
    {
        // The grid answers a press with the card, so a card on two Plans is
        // shown once and names the first.
        var oath = new ProtoKkKuragesOath();
        var queue = new[] { Plan(oath), Plan(oath, now: true) };
        Assert.Equal(new[] { 0 }, KokomiPlanViewRows.Shown(queue));
        Assert.Equal(0, KokomiPlanViewRows.QueueIndex(queue, oath));
    }

    [Fact]
    public void A_pressed_card_no_longer_waiting_names_no_plan()
    {
        var queue = new[] { Plan(new ProtoKkKuragesOath()) };
        Assert.Equal(-1, KokomiPlanViewRows.QueueIndex(queue, new ProtoKkKuragesOath()));
        Assert.Equal(-1, KokomiPlanViewRows.QueueIndex(queue, null));
        Assert.Empty(KokomiPlanViewRows.Shown(Array.Empty<KokomiPlan.Entry>()));
    }

    // ---- which plans flip, and what each caption says -----------------------

    [Fact]
    public void Only_a_two_line_plan_flips()
    {
        Assert.True(KokomiPlanViewRows.Flippable(Plan(new ProtoKkKuragesOath())));
        Assert.False(KokomiPlanViewRows.Flippable(Plan(new ProtoKkMasterstroke())));
        Assert.False(KokomiPlanViewRows.Flippable(
            Plan(null, writer: new ProtoKkKuragesOath())));
    }

    [Fact]
    public void Each_caption_says_its_place_and_the_line_it_will_carry_out_as()
    {
        Assert.Equal("1. Plan line",
            KokomiPlanViewRows.Caption(0, Plan(new ProtoKkKuragesOath())));
        Assert.Equal("2. Now-line",
            KokomiPlanViewRows.Caption(1, Plan(new ProtoKkKuragesOath(), now: true)));
        Assert.Equal("3. Plan only",
            KokomiPlanViewRows.Caption(2, Plan(new ProtoKkMasterstroke())));
        // A Plan-only entry never reads as flipped, whatever it holds.
        Assert.Equal("Plan only", KokomiPlanViewRows.LineCaption(
            Plan(new ProtoKkMasterstroke(), now: true)));
    }

    [Fact]
    public void The_prompt_after_a_flip_names_the_line_it_flips_to()
    {
        Assert.EndsWith("flipping to its now-line.",
            KokomiPlanViewRows.FlipSent(Plan(null)));
        Assert.EndsWith("flipping to its Plan line.",
            KokomiPlanViewRows.FlipSent(Plan(null, now: true)));
    }

    // ---- the strip's button hint --------------------------------------------

    [Fact]
    public void The_hint_shows_for_every_device_and_names_the_keyboard_key()
    {
        Assert.Equal("Plans",
            KokomiPlanViewRows.HintText(InputType.Controller, null));
        Assert.Equal("S: Plans",
            KokomiPlanViewRows.HintText(InputType.KeyboardOnlyMode, "S"));
        Assert.Null(KokomiPlanViewRows.HintText(InputType.KeyboardOnlyMode, ""));
        // Mouse and keyboard (2026-10-16): the peek key is named, and with no
        // key the clickable hint still says "Plans".
        Assert.Equal("Space: Plans",
            KokomiPlanViewRows.HintText(InputType.MouseAndKeyboard, "Space"));
        Assert.Equal("Plans",
            KokomiPlanViewRows.HintText(InputType.MouseAndKeyboard, null));
    }

    [Theory]
    [InlineData(Godot.Key.Space, "Space")]   // peek, mouse and keyboard
    [InlineData(Godot.Key.S, "S")]           // peek, keyboard only
    [InlineData(Godot.Key.Key7, "7")]
    [InlineData(Godot.Key.None, null)]       // unbound
    public void The_hint_prints_the_key_by_its_plain_name(Godot.Key key, string name)
    {
        Assert.Equal(name, KokomiPlanViewRows.KeyName(key));
    }

    [Theory]
    [InlineData(1, 1, 1)]
    [InlineData(3, 3, 3)]
    [InlineData(4, 4, 4)]
    [InlineData(4, 8, 5)]   // a pager: under it
    [InlineData(1, 5, 5)]   // a short last page: still under the pager
    public void The_hint_sits_under_the_last_picture_or_under_the_pager(
        int drawn, int count, int row)
    {
        Assert.Equal(row, KokomiPlanViewRows.HintRow(drawn, count));
    }

    // ---- the wiring ----------------------------------------------------------

    [Fact]
    public void A_press_in_the_view_flips_through_the_co_op_safe_request()
    {
        var picked = Il.Calls(Il.Method("KokomiPlanView", "OnPicked"));
        Assert.Contains("KokomiPlanViewRows.QueueIndex", picked);
        Assert.Contains("KokomiPlan.RequestFlip", picked);
        // The click patch acts on its own screen alone, and then skips the
        // grid's own selection so the view stays open.
        var prefix = Il.Calls(Il.Method(
            "NSimpleCardSelectScreen_OnCardClicked_KokomiPlanView_Patch", "Prefix"));
        Assert.Contains("KokomiPlanView.Owns", prefix);
        Assert.Contains("KokomiPlanView.OnPicked", prefix);
    }

    [Fact]
    public void The_peek_button_opens_the_view_only_on_her_own_quiet_turn()
    {
        var bind = Il.Calls(Il.Method("KokomiPlanView", "Bind"));
        Assert.Contains("NHotkeyManager.PushHotkeyPressedBinding", bind);
        Assert.Contains("NHotkeyManager.RemoveHotkeyPressedBinding", bind);
        Assert.Contains("KokomiPlanView.TryOpen", bind);
        // The game's own peek action, remappable in its input settings.
        Assert.Contains("peek", Il.StaticFieldsRead(Il.Method("KokomiPlanView", "Bind")));
        var open = Il.Calls(Il.Method("KokomiPlanView", "TryOpen"));
        // Any device opens it (2026-10-16): no controller-only gate.
        Assert.DoesNotContain("NControllerManager.get_IsUsingDirectionalNavigation", open);
        Assert.Contains("KokomiOverhaul.LiveFor", open);
        Assert.Contains("KokomiPlan.Showing", open);
        Assert.Contains("KokomiPlanView.ScreenBusy", open);
        Assert.Contains("KokomiPlanViewRows.Shown", open);
        Assert.Contains("NSimpleCardSelectScreen.Create", open);
        Assert.Contains("NOverlayStack.Push", open);
        // B closes it.
        Assert.Contains("NHotkeyManager.PushHotkeyPressedBinding", open);
        var busy = Il.Calls(Il.Method("KokomiPlanView", "ScreenBusy"));
        Assert.Contains("NTargetManager.get_IsInSelection", busy);
        Assert.Contains("NPlayerHand.get_InCardPlay", busy);
    }

    [Fact]
    public void The_strip_binds_refreshes_and_closes_the_view_and_stays_out_of_the_walk()
    {
        Assert.Contains("KokomiPlanView.Bind",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Setup")));
        Assert.Contains("KokomiPlanView.Refresh",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Refresh")));
        Assert.Contains("KokomiPlanView.Close",
                        Il.Calls(Il.Method("KokomiPlanStrip", "DiscardAll")));
        Assert.Contains("KokomiPlanStrip.PaintHint",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Paint")));
        // The hint names the game's current peek key, so a remap shows.
        var hint = Il.Calls(Il.Method("KokomiPlanStrip", "PaintHint"));
        Assert.Contains("NInputManager.GetCurrentHotkey", hint);
        Assert.Contains("peek", Il.StaticFieldsRead(Il.Method("KokomiPlanStrip", "PaintHint")));
        Assert.Contains("KokomiPlanViewRows.KeyName", hint);
        // The mouse's door: a click on the hint opens the same view.
        Assert.Contains("KokomiPlanStrip.WireHintClick",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Build")));
        // `EB-300` kept: the whole strip, hint included, is out of focus.
        Assert.Contains("Control.SetFocusBehaviorRecursive",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Build")));
    }
}
