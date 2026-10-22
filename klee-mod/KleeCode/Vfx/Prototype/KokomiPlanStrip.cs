using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.ControllerInput;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.addons.mega_text;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// THE PENDING PLANS, FACE UP, IN ORDER (slice draft 6 sec.5, the UI list).
///
/// IT IS THE `EB-198` STRIP RE-POINTED, not a second element, and that is why
/// this file is short: <see cref="KurageMemoryCard"/> settled the hard
/// questions -- where a HUD element can live without colliding with the relic
/// column, how it is built and freed through
/// <c>TrackedDisplayBridge.Registry</c>, why the local seat is the only seat,
/// and that a MOD card's thumbnail is <c>CustomCardModel.CustomPortrait</c> and
/// never <c>CardModel.Portrait</c> (its own header records that live catch).
/// Everything here reuses those answers.
///
/// WHAT CHANGED IS WHAT THERE IS TO SHOW. The memory arm had ONE front card and
/// a bank, and the interesting fact was affordability -- so it drew one
/// thumbnail with a coloured ring. Draft 6 has no bank and no price: what the
/// player needs is WHICH Plans are waiting and IN WHAT ORDER, because "three
/// Plans land together the next morning" is the moment the kit is built around
/// (brief sec.3). So this draws a COLUMN, front at the top, one thumbnail per
/// pending Plan.
///
/// A COLUMN OF FOUR, PAGED. <see cref="MaxDrawn"/> thumbnails fit the band;
/// a longer queue draws a page of four and says "+N" under them. Clicking
/// "+N" turns to the next four (release fix, 2026-10-14: seats queued eight
/// Plans in one turn and a human could inspect and flip only the first
/// four); the last page says "Back" and returns to the front. Every page's
/// pictures hover and flip exactly as the first page's do. Both the strip
/// and <c>PendingPlansPower</c>'s badge read <c>KokomiPlan.Pending</c>, so
/// the two cannot disagree.
///
/// ON THE JELLYFISH IS WHERE THE SLICE ASKS FOR IT, and the honest report is
/// that this is a SCREEN-EDGE HUD element, not a node parented to the pet.
/// The reading taken, and why: a creature-parented strip is a
/// <c>Node2D</c> that has to track a creature node the combat room can move,
/// scale and tween (<c>NCreature.DoScaleTween</c>), and the memory arm's own
/// §14.5 records that the creature-tracked version was the one that misread.
/// The pet sits beside her at the left of the field and this element sits at
/// the left edge of the screen, so they read as one column in practice --
/// whether they actually do is a live question and nothing headless can answer
/// it.
///
/// CLICK A TWO-LINE PLAN TO FLIP IT (a Plan stays open, pick 5 (a),
/// 2026-10-01): "Plans carry out on their Plan line; click a waiting Plan to
/// flip it." The strip is the surface because it is already the one place
/// each waiting Plan has its own clickable picture (the hover below), so the
/// flip needs no new screen. A left click on a two-line Plan asks
/// <see cref="KokomiPlan.RequestFlip"/>, which goes through the game's action
/// queue so a co-op peer flips the same Plan; a second click flips it back.
/// Under each two-line Plan a caption says the line it will be carried out
/// as ("Plan line" / "Now-line"), and a flipped picture is tinted. A picture
/// on a later page flips the Plan at its own queue position, read off the
/// picture when clicked (<see cref="IndexMeta"/>).
///
/// NO CONTROLLER FOCUS, still (`EB-300`): the strip, the pager included, is
/// out of the focus graph. A controller player reaches the Plans through the
/// Plans view instead (<see cref="KokomiPlanView"/>, 2026-10-14): the game's
/// "peek" button (the left stick press by default) opens a card grid of every
/// waiting Plan, where A flips one. While a controller is in use the strip
/// draws that button's glyph and "Plans" under the column, so the player can
/// find it; the hint is a picture and a word, out of the walk like the rest.
/// With a keyboard the hint names the peek key ("Space: Plans", "S: Plans"),
/// and a click on the hint opens the same view (2026-10-16), so the mouse
/// has a door too. A click is not focus: the hint stays out of the walk.
/// </summary>
internal static class KokomiPlanStrip
{
    private const string RootName = "KleeModKokomiPlanStrip";

    private const float ThumbWidth = 92f;
    private const float ThumbHeight = 124f;
    private const float ThumbGap = 6f;
    private const float EdgeMargin = 24f;
    private const int CountFontSize = 30;

    /// <summary>How many Plans get a picture. A fifth would run off the band.</summary>
    internal const int MaxDrawn = KokomiPlanPages.PerPage;

    private static readonly Color CountColor = StsColors.cream;

    /// <summary>A flipped Plan's tint: the picture reads as "not the Plan
    /// line" at a glance, and the caption says which line it is.</summary>
    private static readonly Color FlippedTint = new(0.65f, 0.85f, 1f);

    // 14 since the Kokomi review (2026-10-13): "into 12 Block" fits the
    // 92-pixel picture.
    private const int LineFontSize = 14;

    /// <summary>The button hint's row: the glyph is this square.</summary>
    private const float HintHeight = 32f;

    /// <summary>The caption under a two-line Plan.</summary>
    internal const string PlanLineCaption = "Plan line";
    internal const string NowLineCaption = "Now-line";

    /// <summary>A flipped Plan Opening Gambit's double would have reached
    /// (Kokomi Balance suite 4, 2026-10-21).</summary>
    internal const string NowLineNotDoubledCaption = "Now, not doubled";

    /// <summary>The mark on the top picture: the Plan carried out first
    /// (Kokomi review 2026-10-13).</summary>
    internal const string FirstCaption = "First";

    /// <summary>The page the strip is showing, on the root node.</summary>
    private const string PageMeta = "kleemod_plan_page";

    /// <summary>The queue position a picture is drawing, on the picture, so
    /// a click on any page flips the Plan it shows.</summary>
    private const string IndexMeta = "kleemod_plan_index";

    /// <summary>One element per seat, freed by the shared display skeleton the
    /// way the gauges are.</summary>
    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    /// <summary>Is the Plan strip the element this seat should have? On
    /// Kokomi from turn one; on anyone else from their first Plan written
    /// (the off-character rule, 2026-10-18: <see cref="KokomiOverhaul.StripShowsFor"/>).</summary>
    private static bool Live(Creature? creature) =>
        KokomiOverhaul.StripShowsFor(creature);

    /// <summary>Build for the LOCAL seat and nothing else. Called from the same
    /// `NCombatUi.Activate` postfix the gauges and the memory card use, so
    /// there is one combat-lifecycle entry point rather than three that can
    /// disagree about when a room is live.</summary>
    public static void Setup(CombatState? state)
    {
        var me = TryGetMe(state);
        var creature = me?.Creature;
        if (me == null || !Live(creature)) return;
        if (NCombatRoom.Instance?.Ui is not { } ui) return;

        Displays.Discard(me);
        var root = Build(me);
        ui.AddChildSafely(root);
        Displays.Set(me, root);
        // THE CONTROLLER'S DOOR (2026-10-14): the peek button opens the Plans
        // view, bound for exactly this root's life.
        KokomiPlanView.Bind(root, me);
        WireDeviceSwitch(root, me);
        Paint(root, me);
    }

    /// <summary>Re-read the queue and redraw. Driven by
    /// <c>KokomiPlan.RefreshStrip</c>, which fires on every queue move --
    /// exactly the funnel the memory arm's strip rides, and for the same
    /// reason: no polling anywhere.</summary>
    public static void Refresh(Creature? creature)
    {
        // THE VISIBLE SWARM (2026-10-21) rides this funnel for EVERY seat --
        // a partner's jellyfish are on the field for everyone -- so it is
        // redrawn before the local-seat gate below.
        KokomiSwarm.Refresh(creature);
        var player = creature?.Player;
        if (player == null || !LocalContext.IsMe(player)) return;
        if (!Live(creature)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            // Stale or never built (mid-combat reload): rebuild in place, the
            // reference-bridge idiom `GaugeBridge.Refresh` uses.
            Setup(creature!.CombatState as CombatState);
            root = Displays.Get(player);
            if (root == null) return;
        }
        Paint(root, player);
        KokomiPlanView.Refresh(player);
    }

    /// <summary>Teardown, character-scoped like every other door into a
    /// prototype HUD element (EB-225 / R225 item 6).</summary>
    public static void DiscardAll(CombatState? state)
    {
        var me = TryGetMe(state);
        // Any seat whose kit came up may hold a strip, so the teardown asks
        // the wider gate rather than the strip's own.
        if (me == null || !KokomiOverhaul.LiveFor(me.Creature)) return;
        KokomiPlanView.Close();
        Displays.Discard(me);
    }

    private static Player? TryGetMe(CombatState? state)
    {
        // `LocalContext.GetMe` THROWS for "not in this combat" rather than
        // answering null -- the catch `KurageMemoryCard.TryGetMe` records at
        // length, which ended two whole-fight blind sessions. Same guard here.
        if (state == null || LocalContext.NetId is not { } netId) return null;
        try
        {
            return state.GetPlayer(netId);
        }
        catch (System.InvalidOperationException)
        {
            return null;
        }
    }

    private static Control Build(Player me)
    {
        var height = MaxDrawn * ThumbHeight + (MaxDrawn - 1) * ThumbGap
                     + CountFontSize + 8f;
        var root = new Control
        {
            Name = RootName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            // `EB-300`, THE STRIP'S HALF. It is display only: nothing in it may
            // enter the controller's focus graph, or a player walking the HUD
            // lands on a picture of a card with no way back to the hand.
            // `FocusMode` already defaults to `None` on every Control -- this
            // states it rather than inheriting it, because the invariant is the
            // point and a node added here later should read the rule off its
            // neighbours. `SetFocusBehaviorRecursive` below is the belt to this
            // brace, and it is the game's OWN seam for the same job:
            // `NCombatRoom.RestrictControllerNavigation` takes the orb manager
            // out of the walk with exactly that call.
            FocusMode = Control.FocusModeEnum.None,
            // Left edge, vertically centred -- the anchor
            // `KurageMemoryCard.Build` argues for, so the two elements occupy
            // the same band and a resize moves them together.
            AnchorLeft = 0f,
            AnchorRight = 0f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = EdgeMargin,
            OffsetRight = EdgeMargin + ThumbWidth,
            OffsetTop = -height / 2f,
            OffsetBottom = height / 2f,
        };

        for (var i = 0; i < MaxDrawn; i++)
        {
            var thumb = new TextureRect
            {
                Name = "Plan" + i,
                // HOVER SHOWS THE CARD (co-op playtest 2026-09-30: "mousing
                // over the Plan cards shows only icons"). The mouse is all it
                // takes; focus stays off (`EB-300`, below).
                MouseFilter = Control.MouseFilterEnum.Stop,
                FocusMode = Control.FocusModeEnum.None,
                ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered,
                Position = new Vector2(0f, i * (ThumbHeight + ThumbGap)),
                Size = new Vector2(ThumbWidth, ThumbHeight),
                Visible = false,
            };
            WireHover(thumb);
            WireClick(thumb, me);
            var line = new Label
            {
                Name = "Line",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                FocusMode = Control.FocusModeEnum.None,
                HorizontalAlignment = HorizontalAlignment.Center,
                Position = new Vector2(0f, ThumbHeight - LineFontSize - 8f),
                Size = new Vector2(ThumbWidth, LineFontSize + 6f),
                Visible = false,
            };
            line.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                          LineFontSize);
            line.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                       CountColor);
            thumb.AddChildSafely(line);
            // THE KOKOMI REVIEW (2026-10-13): "after Change of Plans I could
            // not tell which Plan was first" (B2). The top picture says so.
            var first = new Label
            {
                Name = "First",
                Text = FirstCaption,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                FocusMode = Control.FocusModeEnum.None,
                HorizontalAlignment = HorizontalAlignment.Center,
                Position = new Vector2(0f, 2f),
                Size = new Vector2(ThumbWidth, LineFontSize + 6f),
                Visible = false,
            };
            first.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                           LineFontSize);
            first.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                        CountColor);
            thumb.AddChildSafely(first);
            root.AddChildSafely(thumb);
        }

        var count = new Label
        {
            Name = "Count",
            // THE PAGER (release fix, 2026-10-14): "+N" is clickable and
            // turns to the next four Plans.
            MouseFilter = Control.MouseFilterEnum.Stop,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            Position = new Vector2(
                0f, MaxDrawn * (ThumbHeight + ThumbGap) + 4f),
            Size = new Vector2(ThumbWidth, CountFontSize + 8f),
        };
        count.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       CountFontSize);
        count.AddThemeColorOverride(ThemeConstants.Label.FontColor, CountColor);
        WirePager(count, root, me);
        root.AddChildSafely(count);

        // THE BUTTON HINT (2026-10-14): the peek glyph and "Plans" for a
        // controller, the peek key and "Plans" for a keyboard (2026-10-16).
        // A left click on it opens the Plans view (the mouse's door); no
        // focus, ever (`EB-300`).
        var hint = new Control
        {
            Name = "PadHint",
            MouseFilter = Control.MouseFilterEnum.Stop,
            FocusMode = Control.FocusModeEnum.None,
            Size = new Vector2(ThumbWidth, HintHeight),
            Visible = false,
        };
        var glyph = new TextureRect
        {
            Name = "Glyph",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            Size = new Vector2(HintHeight, HintHeight),
        };
        hint.AddChildSafely(glyph);
        var words = new Label
        {
            Name = "Words",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            VerticalAlignment = VerticalAlignment.Center,
            Position = new Vector2(HintHeight + 4f, 0f),
            Size = new Vector2(ThumbWidth - HintHeight - 4f, HintHeight),
        };
        words.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       LineFontSize + 4);
        words.AddThemeColorOverride(ThemeConstants.Label.FontColor, CountColor);
        hint.AddChildSafely(words);
        WireHintClick(hint, words, me);
        root.AddChildSafely(hint);
        // The whole subtree, in one call, AFTER the children exist -- the
        // recursive flag is a property of the node it is set on and is read
        // through the tree, so setting it last covers what was added above and
        // anything a future edit adds beside them.
        root.SetFocusBehaviorRecursive(
            Control.FocusBehaviorRecursiveEnum.Disabled);
        return root;
    }

    /// <summary>
    /// Draw the queue: front at the top, in writing order.
    ///
    /// AN EMPTY QUEUE DRAWS NOTHING AT ALL -- no thumbnails and no count. The
    /// memory arm's `EB-198` lesson was that a HUD element showing a number
    /// over an empty state reads as a state; nothing pending is nothing to say.
    /// </summary>
    private static void Paint(Control root, Player player)
    {
        // `SHOWING`, NOT `PENDING` (`EB-317`). The two are the same list at
        // every moment but one: during the morning drain the real queue is
        // empty -- it is cleared in a single move, so a Plan written
        // mid-resolution waits for the next turn -- while the column keeps
        // drawing the Plans not carried out YET, and shortens by one as each
        // is. The seat report this row is made of was "the panel simply reads
        // empty"; this is the half of the repair the HUD owns.
        var pending = KokomiPlan.Showing(player);
        var count = root.GetNodeOrNull<Label>("Count");
        var page = KokomiPlanPages.ClampPage(
            root.HasMeta(PageMeta) ? root.GetMeta(PageMeta).AsInt32() : 0,
            pending.Count);
        root.SetMeta(PageMeta, page);
        var start = KokomiPlanPages.PageStart(page, pending.Count);

        for (var slot = 0; slot < MaxDrawn; slot++)
        {
            var thumb = root.GetNodeOrNull<TextureRect>("Plan" + slot);
            if (thumb == null) continue;
            var line = thumb.GetNodeOrNull<Label>("Line");
            var first = thumb.GetNodeOrNull<Label>("First");
            var i = start + slot;
            if (i >= pending.Count)
            {
                thumb.Visible = false;
                SetCard(thumb, null);
                if (thumb.HasMeta(IndexMeta)) thumb.RemoveMeta(IndexMeta);
                if (line != null) line.Visible = false;
                if (first != null) first.Visible = false;
                continue;
            }
            thumb.Visible = true;
            thumb.Texture = Portrait(pending[i].Source);
            SetCard(thumb, pending[i].Source);
            thumb.SetMeta(IndexMeta, i);
            // PICK 5 (a): the line a two-line Plan will be carried out as.
            var entry = pending[i];
            var flipped = entry.TwoLine && entry.Now;
            thumb.Modulate = flipped ? FlippedTint : Colors.White;
            // THE KOKOMI REVIEW (2026-10-13): the first Plan is marked, and
            // the caption reads the board -- Tide Wall's live total, or the
            // Block an Attack Plan will land in (`KokomiPlan.StripCaption`).
            if (first != null)
            {
                var mark = KokomiPlanPages.PositionCaption(i, page, pending.Count);
                first.Visible = mark != null;
                first.Text = mark ?? string.Empty;
            }
            if (line != null)
            {
                var kokomi = player.Creature;
                var caption = KokomiPlan.StripCaption(
                    entry.TwoLine, flipped,
                    KokomiPlan.LiveBlock(entry, kokomi),
                    KokomiPlan.KeptBlockAhead(entry, kokomi),
                    KokomiPlan.DefendsAhead(entry, kokomi),
                    // THE POOL OVERHAUL (2026-10-13): a Counter or Chain
                    // Plan's number as it stands.
                    KokomiPlan.LiveLine(entry, kokomi, i),
                    // Kokomi Balance suite 4 (2026-10-21): a flip that
                    // loses Opening Gambit's double says so.
                    KokomiPlan.LosesDoubleAt(pending, i));
                line.Visible = caption != null;
                line.Text = caption ?? string.Empty;
            }
        }

        // Not while the morning runs: a Plan's choice screen owns the key then.
        PaintHint(root, page, pending.Count,
                  !ReferenceEquals(pending, KokomiPlan.Pending(player)));
        if (count == null) return;
        count.Text = KokomiPlanPages.PagerCaption(page, pending.Count);
    }

    /// <summary>
    /// THE BUTTON HINT: the peek button's glyph (the game's own, so a
    /// remapped button shows its new glyph) and "Plans", under the last
    /// picture or under the pager. Hidden for an empty queue and while the
    /// morning carries the Plans out (a Plan's choice screen owns the key).
    /// </summary>
    private static void PaintHint(Control root, int page, int count,
                                  bool draining)
    {
        var hint = root.GetNodeOrNull<Control>("PadHint");
        if (hint == null) return;
        try
        {
            var input = NControllerManager.Instance?.InputType
                        ?? InputType.MouseAndKeyboard;
            // The game's own current key for peek in either keyboard mode, so
            // a remap in its input settings shows here.
            var key = input != InputType.Controller
                      && NInputManager.Instance is { } inputs
                ? KokomiPlanViewRows.KeyName(
                    inputs.GetCurrentHotkey(MegaInput.peek))
                : null;
            var text = KokomiPlanViewRows.HintShown(count, draining)
                ? KokomiPlanViewRows.HintText(input, key)
                : null;
            hint.Visible = text != null;
            if (text == null) return;
            var glyph = hint.GetNodeOrNull<TextureRect>("Glyph");
            if (glyph != null)
            {
                glyph.Texture = input == InputType.Controller
                    ? NInputManager.Instance?.GetHotkeyIcon(MegaInput.peek)
                    : null;
                glyph.Visible = glyph.Texture != null;
            }
            var words = hint.GetNodeOrNull<Label>("Words");
            if (words != null)
            {
                words.Text = text;
                words.Position = new Vector2(
                    glyph is { Visible: true } ? HintHeight + 4f : 0f, 0f);
                // The click target covers the words, "Space: Plans" included,
                // which run wider than a picture.
                hint.Size = new Vector2(
                    Math.Max(ThumbWidth,
                             words.Position.X + words.GetMinimumSize().X),
                    HintHeight);
            }
            var drawn = Math.Min(
                count - KokomiPlanPages.PageStart(page, count), MaxDrawn);
            var row = KokomiPlanViewRows.HintRow(drawn, count);
            hint.Position = new Vector2(0f, row <= MaxDrawn
                ? row * (ThumbHeight + ThumbGap)
                : MaxDrawn * (ThumbHeight + ThumbGap) + CountFontSize + 12f);
        }
        catch (Exception e)
        {
            hint.Visible = false;
            Log.Warn($"[{KleeMod.ModId}] plan strip: hint skipped: {e}");
        }
    }

    /// <summary>
    /// Repaint when the player picks up a controller or the mouse, so the
    /// hint follows the device. Connected to this root and disconnected as it
    /// leaves the tree, the way the game's own buttons pair the two.
    /// </summary>
    private static void WireDeviceSwitch(Control root, Player me)
    {
        var devices = NControllerManager.Instance;
        if (devices == null) return;
        var repaint = Callable.From(() =>
        {
            if (GodotObject.IsInstanceValid(root)) Paint(root, me);
        });
        devices.Connect(NControllerManager.SignalName.ControllerDetected, repaint);
        devices.Connect(NControllerManager.SignalName.MouseDetected, repaint);
        root.TreeExiting += () =>
        {
            if (!GodotObject.IsInstanceValid(devices)) return;
            devices.Disconnect(NControllerManager.SignalName.ControllerDetected, repaint);
            devices.Disconnect(NControllerManager.SignalName.MouseDetected, repaint);
        };
    }

    /// <summary>
    /// THE PAGER: a left click on "+N" (or "Back") turns the strip to the next
    /// page and repaints. Display only -- no Plan moves, so nothing goes
    /// through the action queue and a co-op peer's strip is untouched.
    /// </summary>
    /// <summary>
    /// THE MOUSE'S DOOR (2026-10-16): a left click on the hint opens the
    /// Plans view, through the same <see cref="KokomiPlanView.TryOpen"/> the
    /// peek key uses, so every refusal (not her turn, a card being aimed,
    /// another screen up) holds for the click too. The words turn gold under
    /// the pointer, the base game's highlight.
    /// </summary>
    private static void WireHintClick(Control hint, Label words, Player me)
    {
        hint.MouseEntered += () =>
            words.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                        StsColors.gold);
        hint.MouseExited += () =>
            words.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                        CountColor);
        hint.GuiInput += input =>
        {
            if (input is not InputEventMouseButton
                {
                    ButtonIndex: MouseButton.Left, Pressed: true,
                })
            {
                return;
            }
            hint.AcceptEvent();
            KokomiPlanView.TryOpen(me);
        };
    }

    private static void WirePager(Label pager, Control root, Player me)
    {
        pager.GuiInput += input =>
        {
            if (input is not InputEventMouseButton
                {
                    ButtonIndex: MouseButton.Left, Pressed: true,
                })
            {
                return;
            }
            try
            {
                var queue = KokomiPlan.Showing(me);
                if (queue.Count <= MaxDrawn) return;
                var page = root.HasMeta(PageMeta)
                    ? root.GetMeta(PageMeta).AsInt32() : 0;
                root.SetMeta(PageMeta, KokomiPlanPages.NextPage(page, queue.Count));
                Paint(root, me);
                pager.AcceptEvent();
            }
            catch (Exception e)
            {
                Log.Warn($"[{KleeMod.ModId}] plan strip: page skipped: {e}");
            }
        };
    }

    // ------------------------------------------------------------------
    // THE HOVER: the whole card, the way the base game previews one
    // ------------------------------------------------------------------

    /// <summary>The card each thumbnail is drawing, keyed by node instance id.
    /// Written by <see cref="Paint"/> alone, so a hover always shows the Plan
    /// the picture is of.</summary>
    private static readonly Dictionary<ulong, CardModel> Cards = new();

    /// <summary>Whether THIS thumbnail owns a live tip set. On the node, so it
    /// dies with it. `NHoverTipSet.CreateAndShow` keys its registry by owner and
    /// ADDS, so a second show without a remove throws -- the Furina cue's
    /// lesson (`FurinaStageCueNodes`).</summary>
    private const string HoverShownMeta = "kleemod_plan_hover_shown";

    /// <summary>
    /// PICK 5 (a): a left click on the picture of a waiting two-line Plan
    /// flips it. The picture carries its queue position (<see cref="IndexMeta"/>,
    /// written by <see cref="Paint"/>, so a later page flips its own Plan), and <see cref="KokomiPlan.RequestFlip"/>
    /// refuses a Plan-only one, a click outside her turn, and a click during
    /// the morning drain (<see cref="KokomiPlan.Showing"/> differs from the
    /// queue then). Any failure is logged and swallowed: a click must never
    /// throw into the UI.
    /// </summary>
    private static void WireClick(TextureRect thumb, Player me)
    {
        thumb.GuiInput += input =>
        {
            if (input is not InputEventMouseButton
                {
                    ButtonIndex: MouseButton.Left, Pressed: true,
                })
            {
                return;
            }
            try
            {
                if (!ReferenceEquals(KokomiPlan.Showing(me),
                                     KokomiPlan.Pending(me)))
                {
                    return;
                }
                if (!thumb.HasMeta(IndexMeta)) return;
                var slot = thumb.GetMeta(IndexMeta).AsInt32();
                var why = KokomiPlan.RequestFlip(me, slot);
                if (why == null) thumb.AcceptEvent();
            }
            catch (Exception e)
            {
                Log.Warn($"[{KleeMod.ModId}] plan strip: flip skipped: {e}");
            }
        };
    }

    private static void WireHover(TextureRect thumb)
    {
        thumb.MouseEntered += () => ShowHover(thumb);
        thumb.MouseExited += () => ClearHover(thumb);
        thumb.TreeExiting += () => Cards.Remove(thumb.GetInstanceId());
    }

    /// <summary>Point a thumbnail at a card, or at nothing. A changed card
    /// takes down the tip of the old one: the column shortens under the mouse
    /// during the morning drain.</summary>
    private static void SetCard(TextureRect thumb, CardModel? card)
    {
        var id = thumb.GetInstanceId();
        Cards.TryGetValue(id, out var was);
        if (card == null) Cards.Remove(id);
        else Cards[id] = card;
        if (!ReferenceEquals(was, card)) ClearHover(thumb);
    }

    /// <summary>
    /// THE CARD PREVIEW AND ITS KEYWORD TIPS, the set the base game shows over
    /// a hand card (<c>NCardHolder</c>: <c>Model.HoverTips</c>) with the card
    /// itself in front, as <c>HoverTipFactory.FromCard</c> renders it for an
    /// "add a card" preview. Placed by the base game's own rule
    /// (<c>HoverTip.GetHoverTipAlignment</c>), which puts it to the right of a
    /// left-edge element.
    /// </summary>
    private static void ShowHover(TextureRect thumb)
    {
        try
        {
            if (!thumb.Visible
                || !Cards.TryGetValue(thumb.GetInstanceId(), out var card))
            {
                return;
            }
            ClearHover(thumb);
            var tips = new List<IHoverTip> { HoverTipFactory.FromCard(card) };
            tips.AddRange(card.HoverTips);
            NHoverTipSet.CreateAndShow(
                thumb, tips, HoverTip.GetHoverTipAlignment(thumb));
            thumb.SetMeta(HoverShownMeta, true);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plan strip: hover skipped: {e}");
        }
    }

    private static void ClearHover(TextureRect thumb)
    {
        if (!thumb.HasMeta(HoverShownMeta)) return;
        thumb.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(thumb);
    }

    /// <summary>
    /// The card's picture, OURS FIRST -- the correction `EB-198`'s live
    /// acceptance forced on the memory strip, restated here rather than
    /// re-learned: a MOD card has no `PortraitPath` to load, and its art is a
    /// runtime `ImageTexture` handed over as
    /// <c>CustomCardModel.CustomPortrait</c>.
    /// </summary>
    /// <summary>
    /// THE FRONT PICTURE, for the carry-out's thumbnail flight
    /// (<c>KokomiPlanFx</c>, 2026-10-21): the texture of
    /// <paramref name="source"/>, the global rectangle of the strip's top
    /// slot, and the node the strip hangs from. Null for a seat with no strip
    /// on screen (another player's, or none built), so only the local seat
    /// sees its Plans fly.
    /// </summary>
    internal static (Texture2D Texture, Rect2 Rect, Node Layer)? FrontThumb(
        Creature? creature, CardModel? source)
    {
        var player = creature?.Player;
        if (player == null || !LocalContext.IsMe(player)) return null;
        var root = Displays.Get(player);
        if (root == null || !GodotObject.IsInstanceValid(root) || !root.Visible) return null;
        var layer = root.GetParent();
        var slot = root.GetNodeOrNull<TextureRect>("Plan0");
        var texture = Portrait(source);
        if (layer == null || slot == null || texture == null) return null;
        return (texture, new Rect2(slot.GlobalPosition, slot.Size), layer);
    }

    private static Texture2D? Portrait(CardModel? card)
    {
        if (card == null) return null;
        if (card is CustomCardModel custom && custom.CustomPortrait != null)
        {
            return custom.CustomPortrait;
        }
        return card.HasPortrait ? card.Portrait : null;
    }
}

/// <summary>
/// THE STRIP'S PAGES (release fixes, 2026-10-14), the arithmetic alone so it
/// is pinned headlessly: four Plans a page, "+N" turns to the next four, the
/// last page says "Back".
/// </summary>
public static class KokomiPlanPages
{
    /// <summary>Plans on one page of the strip (<c>KokomiPlanStrip.MaxDrawn</c>).</summary>
    public const int PerPage = 4;

    /// <summary>The pager under the column on its last page.</summary>
    public const string BackCaption = "Back";

    /// <summary>How many pages a queue of <paramref name="count"/> needs (at
    /// least one).</summary>
    public static int PageCount(int count) =>
        count <= PerPage ? 1 : (count + PerPage - 1) / PerPage;

    /// <summary>A page still on the queue: one past the end (the morning
    /// drain shortens it) falls back to the front.</summary>
    public static int ClampPage(int page, int count) =>
        page >= 0 && page < PageCount(count) ? page : 0;

    /// <summary>The page a click on the pager turns to: the next, and from
    /// the last back to the front.</summary>
    public static int NextPage(int page, int count) =>
        (ClampPage(page, count) + 1) % PageCount(count);

    /// <summary>The queue position of the first picture on a page.</summary>
    public static int PageStart(int page, int count) =>
        ClampPage(page, count) * PerPage;

    /// <summary>What the pager says: "+N" for the Plans after this page,
    /// "Back" on the last page of a long queue, nothing for a short one.</summary>
    public static string PagerCaption(int page, int count)
    {
        if (count <= PerPage) return string.Empty;
        var after = count - (ClampPage(page, count) + 1) * PerPage;
        return after > 0 ? "+" + after : BackCaption;
    }

    /// <summary>The mark at the top of a picture: "First" on the front Plan
    /// of a queue of two or more, "Plan N" on every picture of a later page
    /// (its place in the order), nothing otherwise.</summary>
    public static string? PositionCaption(int index, int page, int count)
    {
        if (index == 0) return count > 1 ? KokomiPlanStrip.FirstCaption : null;
        return ClampPage(page, count) > 0 ? "Plan " + (index + 1) : null;
    }
}

/// <summary>The element dies with the combat, like the gauges and the memory
/// card do -- one teardown per HUD element, on the game's own hook.</summary>
// lint: no-seat: pure static teardown of this file's own registry. It reaches
// `DiscardAll`, which resolves the seat through the guarded `TryGetMe` and
// then asks `KokomiOverhaul.LiveFor` -- the character scope is one call in and
// spelled there rather than restated here.
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_KokomiPlanStrip_Patch
{
    [HarmonyPostfix]
    public static void Postfix() =>
        KokomiPlanStrip.DiscardAll(KokomiRules.Combat as CombatState);
}

/// <summary>
/// THE ICON DECLUTTER (2026-10-19, [USER]: "can we do a search over all of the
/// things in each kit that still print a status icon and see if they're
/// 'really' needed? I've noticed that our characters tend to make a lot of
/// icons."). Two of her badges say what another surface already draws, so
/// they are kept off her OWN status strip, the way Klee's Spark and Furina's
/// Fanfare badges are; a co-op partner still sees both.
///
/// <list type="bullet">
/// <item><see cref="PendingPlansPower"/>, the Plan count, carries no rule:
/// the strip draws one picture per waiting Plan (and "+N"), and the Plans view
/// lists them, off the same queue.</item>
/// <item><see cref="ProtoBakeKuragePower"/>, the presence marker: its two
/// facts ("Enemies can't target it. It holds your Plans ...") move onto the
/// jellyfish's own hover (<see cref="Creature_HoverTips_BakeKurage_Patch"/>),
/// which is where a player looks for what the jellyfish is. Hidden only once
/// the jellyfish is on the field, so the sentence always has a home.</item>
/// </list>
///
/// Suppressed at the container, never through <c>IsVisibleInternal</c>: the
/// seat bridge's power list skips an invisible power, and the seat page reads
/// both. Never throws: a canonical power has no owner to ask.
/// </summary>
public static class KokomiBadges
{
    public static bool HidesBadge(PowerModel power)
    {
        if (power is not (PendingPlansPower or ProtoBakeKuragePower)) return false;
        Creature? owner;
        try
        {
            owner = power.IsMutable ? power.Owner : null;
        }
        catch (Exception)
        {
            return false;
        }
        if (owner == null || !KokomiOverhaul.LiveFor(owner)) return false;
        if (!LocalContext.IsMe(owner)) return false;
        return power is PendingPlansPower
            ? KokomiOverhaul.StripShowsFor(owner)
            : BakeKuragePet.Of(owner) != null;
    }

    /// <summary>The marker whose sentence the jellyfish's own hover shows:
    /// its owner's, or null (not her jellyfish, or no marker yet).</summary>
    public static ProtoBakeKuragePower? PetMarker(Creature? pet)
    {
        if (!BakeKuragePet.Is(pet)) return null;
        var owner = pet!.PetOwner?.Creature;
        if (owner == null || !KokomiOverhaul.LiveFor(owner)) return null;
        return KokomiRules.Marker(owner);
    }

    /// <summary>The tips the jellyfish's own hover adds (<see cref="PetMarker"/>'s),
    /// or none. Never throws.</summary>
    public static IReadOnlyList<IHoverTip> PetTips(Creature? pet)
    {
        try
        {
            return PetMarker(pet)?.HoverTips.ToList()
                ?? (IReadOnlyList<IHoverTip>)Array.Empty<IHoverTip>();
        }
        catch (Exception)
        {
            return Array.Empty<IHoverTip>();
        }
    }
}

/// <summary>Her Plan count and Bake-Kurage marker stay off her own status
/// strip (<see cref="KokomiBadges"/>); a co-op partner still sees them.</summary>
[HarmonyPatch(typeof(NPowerContainer), "Add")]
internal static class NPowerContainer_Add_KokomiBadges_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel power) =>
        !KokomiBadges.HidesBadge(power);
}

/// <summary>Hovering the jellyfish shows what its marker badge said. The game's
/// creature hover lists the creature's own powers' tips, and the jellyfish
/// carries none, so the marker's are appended after them. It resolves no
/// seat; the scope is <c>KokomiOverhaul.LiveFor</c> in
/// <see cref="KokomiBadges.PetMarker"/>.</summary>
[HarmonyPatch(typeof(Creature), nameof(Creature.HoverTips), MethodType.Getter)]
internal static class Creature_HoverTips_BakeKurage_Patch
{
    [HarmonyPostfix]
    public static void Postfix(Creature __instance,
                               ref IEnumerable<IHoverTip> __result)
    {
        var extra = KokomiBadges.PetTips(__instance);
        if (extra.Count == 0) return;
        __result = __result.Concat(extra).ToList();
    }
}
