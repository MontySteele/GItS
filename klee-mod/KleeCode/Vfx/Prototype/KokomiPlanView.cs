using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.ControllerInput;
using MegaCrit.Sts2.Core.Entities.Actions;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens.Capstones;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Nodes.Screens.Overlays;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.addons.mega_text;

namespace KleeMod.Vfx;

/// <summary>
/// THE PLANS VIEW: every waiting Plan, inspectable and flippable on a
/// controller (2026-10-14). [USER]: "I do actually play on controller and
/// I've never flipped a plan myself - let's handle that focus change sooner
/// rather than later so it's accessible during my runs."
///
/// THE STRIP STAYS OUT OF THE FOCUS WALK (`EB-300`'s invariant, kept). The
/// controller reaches the Plans through a MODAL instead: the base game's own
/// card grid (<c>NSimpleCardSelectScreen</c>, the screen every "choose a card
/// from this list" effect opens), which is already controller-ready -- the
/// D-pad walks the grid, A presses a card, Y presses Confirm, and closing it
/// hands focus back to the combat screen's default control, the hand, exactly
/// as closing the draw-pile view does.
///
/// THE ENTRY IS A BUTTON, NOT A FOCUSABLE NODE: the game's "peek" action
/// (<c>MegaInput.peek</c>, the left stick press by default, remappable in the
/// game's own input settings). Read off the decompile: every other controller
/// action is already bound on the combat screen (Y end turn, X potions, the
/// triggers and bumpers the four piles, Back the map), and peek is bound only
/// by the peek button of a card-selection screen, which is disabled while the
/// hand is in play mode. The binding goes through <c>NHotkeyManager</c> --
/// the seam the pile buttons use -- so any screen that opens on top (a pile
/// view, a hand selection with its own peek button, the pause menu) wins the
/// button while it is open, and nothing here outlives the strip it is bound
/// to. The strip draws the button's glyph and "Plans" under the column while a
/// controller is in use (<see cref="KokomiPlanStrip"/>).
///
/// KEYBOARD AND MOUSE (2026-10-16; in-game check: "opens only on the left
/// stick press, no keyboard key and no key hint"). Peek is not a controller
/// action alone: the game binds it on the keyboard too -- Space in mouse and
/// keyboard play, S in keyboard-only play (<c>NInputManager</c>'s
/// <c>DefaultHotkeyInputMap</c> and <c>DefaultKbOnlyInputMap</c>), both
/// remappable in the game's own input settings. In combat no other default
/// keyboard action sits on either key (the numbers pick cards, E ends the
/// turn, A/S/D/X or A/D/Q/F the piles, M or Tab the map), and peek's only
/// other combat user is a card selection's peek button, which pushes its own
/// binding on top while it is up. So the same binding serves every device;
/// the view used to refuse a mouse player and now does not. The strip names
/// the key ("Space: Plans") and the hint itself is clickable, so a mouse
/// player opens the same view with a click.
///
/// IN THE VIEW: the Plans in queue order, the first at the top left, each with
/// a caption under its card -- "1. Plan line", "2. Now-line", "3. Plan only".
/// A on a two-line Plan asks <see cref="KokomiPlan.RequestFlip"/> (the
/// strip's own co-op-safe request, through the action queue) and the view
/// stays open: the caption repaints when the flip lands, through the same
/// <c>KokomiPlanStrip.Refresh</c> funnel the strip rides. A on a Plan-only
/// card flips nothing and the prompt says why. B or Confirm closes.
///
/// WHAT IS NOT KNOWN HEADLESSLY: where the caption sits on a grid card at
/// 1280x720, and that the grid's own holders are built before the first frame
/// is read (they are decorated on every frame while the view is open, so a
/// late holder is caught a frame later).
///
/// THE MORNING'S CHOICES COME FIRST (co-op softlock, 2026-10-17). [USER]: "I
/// seem to have caused a softlock by opening the list of plans at the
/// beginning of the turn when the plans were trying to play. I had to save and
/// restart the fight to fix it." A Plan that asks for a card (Read the
/// Field's "Put a Draw Pile card into your Hand") runs inside her turn-start
/// hook, as a hook action that pauses for her choice and pushes the game's
/// own pile screen. That screen has a peek button bound to the same key the
/// strip advertised as "Space: Plans" (<c>NPeekButton.Hotkeys</c>, pushed on
/// top of the strip's binding by <c>NButton.RegisterHotkeys</c>), so the key
/// meant for the Plans toggled the morning's choice into peek mode: the grid
/// and its prompt hidden, the overlay still up, the turn held. Three guards
/// now, all local UI and none of them synced state: the hint is not drawn
/// while the morning runs (<see cref="KokomiPlanViewRows.HintShown"/>); the
/// view refuses to open while one of her actions is queued, running or
/// waiting on a choice, or while any action is running
/// (<see cref="KokomiPlanViewRows.OpenBlockedByActions"/>); and an open view
/// closes itself the moment a choice of hers begins, from the game's own
/// pause-for-choice (the patch at the foot of this file) and on every frame
/// as a backstop (<see cref="KokomiPlanViewRows.ChoiceTakesOver"/>), so the
/// choice screen always reaches her.
///
/// QUARANTINED with the strip: `Vfx/Prototype/**`.
/// </summary>
internal static class KokomiPlanView
{
    /// <summary>The grid's prompt, merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c> like every other selection prompt.</summary>
    internal const string PromptKey =
        "KLEEMOD-KOKOMI_PLAN_VIEW.selectionScreenPrompt";

    internal const string PromptText =
        "Waiting Plans, first at the top left. Choose a Plan to flip it.";

    private const string CaptionName = "KleeModPlanViewCaption";
    private const int CaptionFontSize = 26;

    private static readonly Color CaptionColor = StsColors.cream;

    /// <summary>The strip's flipped tint, so the two read alike.</summary>
    private static readonly Color FlippedTint = new(0.65f, 0.85f, 1f);

    /// <summary>The open view, or null. One at a time, local seat only.</summary>
    private static NSimpleCardSelectScreen? _screen;

    private static Player? _owner;

    /// <summary>The tree <see cref="OnFrame"/> was added to, so it is taken
    /// off that tree once and only once (an unsubscribe from a tree it was
    /// never on logs "Attempt to disconnect a nonexistent connection").</summary>
    private static SceneTree? _frameTree;

    /// <summary>The game's per-player action queues. Private in the game;
    /// read only, to see whether one of her own actions is still on them.
    /// Null if a game update renames it, and then the scan finds nothing and
    /// the other guards stand.</summary>
    private static readonly FieldInfo? QueuesField =
        AccessTools.Field(typeof(ActionQueueSet), "_actionQueues");

    private static bool _scanWarned;

    /// <summary>The cards the view shows, in queue order.</summary>
    private static readonly List<CardModel> Shown = new();

    /// <summary>B's binding while the view is open (one instance, so it is
    /// the one removed).</summary>
    private static readonly Action CloseAction = Close;

    /// <summary>Is this the screen this file opened? The click patch acts on
    /// nothing else.</summary>
    internal static bool Owns(NCardGridSelectionScreen? screen) =>
        screen != null && ReferenceEquals(screen, _screen)
        && KokomiResources.IsKokomi(_owner?.Creature);

    /// <summary>
    /// Bind the entry button to one strip's lifetime. Each strip root gets
    /// its own action, removed when that root leaves the tree, so a rebuilt
    /// strip whose old root is freed a frame later never takes the new
    /// binding down with it.
    /// </summary>
    internal static void Bind(Control root, Player me)
    {
        var hotkeys = NHotkeyManager.Instance;
        if (hotkeys == null) return;
        Action open = () => TryOpen(me);
        hotkeys.PushHotkeyPressedBinding(MegaInput.peek, open);
        root.TreeExiting += () =>
            NHotkeyManager.Instance?.RemoveHotkeyPressedBinding(
                MegaInput.peek, open);
    }

    /// <summary>
    /// The button, the key or a click on the strip's hint. Opens only where
    /// opening cannot interrupt anything: her own play phase, not mid-drain,
    /// the hand in play mode with no card being aimed, and no other screen
    /// up. Any device may open it. Anything else is a no-op, never a throw
    /// into the UI.
    /// </summary>
    internal static void TryOpen(Player me)
    {
        try
        {
            if (_screen != null && GodotObject.IsInstanceValid(_screen)) return;
            if (!KokomiOverhaul.LiveFor(me.Creature)) return;
            if (me.PlayerCombatState?.Phase != PlayerTurnPhase.Play) return;
            if (!ReferenceEquals(KokomiPlan.Showing(me), KokomiPlan.Pending(me)))
            {
                return;
            }
            if (ScreenBusy()) return;
            if (ActionsBusy(me)) return;

            var queue = KokomiPlan.Pending(me);
            Shown.Clear();
            foreach (var i in KokomiPlanViewRows.Shown(queue))
            {
                Shown.Add(KokomiPlanViewRows.Face(queue[i])!);
            }
            // The grid hands its first card's owner to its pile buttons; a
            // card with none would throw inside the screen's _Ready.
            if (Shown.Count == 0 || !HasOwner(Shown[0])) return;

            var prefs = new CardSelectorPrefs(new LocString("cards", PromptKey), 0, 1);
            var screen = NSimpleCardSelectScreen.Create(Shown, prefs);
            _screen = screen;
            _owner = me;
            // Only THIS screen's exit lets go: a view reopened before the
            // old one is freed keeps its own hold.
            screen.TreeExiting += () =>
            {
                if (_screen == null || ReferenceEquals(_screen, screen)) Forget();
            };
            NOverlayStack.Instance!.Push(screen);
            NHotkeyManager.Instance?.PushHotkeyPressedBinding(
                MegaInput.cancel, CloseAction);
            if (screen.GetTree() is { } tree)
            {
                tree.ProcessFrame += OnFrame;
                _frameTree = tree;
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plans view: open skipped: {e}");
            Forget();
        }
    }

    private static bool ScreenBusy()
    {
        if (NOverlayStack.Instance is not { } overlays || overlays.ScreenCount > 0)
        {
            return true;
        }
        if (NCapstoneContainer.Instance?.InUse == true) return true;
        var hand = NCombatRoom.Instance?.Ui?.Hand;
        if (hand == null || hand.CurrentMode != NPlayerHand.Mode.Play
            || hand.InCardPlay)
        {
            return true;
        }
        return NTargetManager.Instance.IsInSelection;
    }

    /// <summary>One of her own actions queued, running or waiting on a
    /// choice, or any action running: the view waits.</summary>
    private static bool ActionsBusy(Player me) =>
        KokomiPlanViewRows.OpenBlockedByActions(ActionStates(), me.NetId);

    /// <summary>
    /// Every action the game holds right now, as (owner, state): the one the
    /// executor is running and everything on the per-player queues (a hook
    /// action paused for a choice sits at the front of its owner's queue).
    /// Read only. A scan that cannot read the queues answers what it has.
    /// </summary>
    private static List<(ulong Owner, GameActionState State)> ActionStates()
    {
        var states = new List<(ulong Owner, GameActionState State)>();
        var run = RunManager.Instance;
        if (run == null) return states;
        if (run.ActionExecutor?.CurrentlyRunningAction is { } running)
        {
            states.Add((running.OwnerId, running.State));
        }
        try
        {
            if (run.ActionQueueSet is { } set
                && QueuesField?.GetValue(set) is IEnumerable queues)
            {
                foreach (var queue in queues)
                {
                    if (queue == null) continue;
                    if (Traverse.Create(queue).Field("actions").GetValue()
                        is not IEnumerable actions)
                    {
                        continue;
                    }
                    foreach (var action in actions)
                    {
                        if (action is GameAction a) states.Add((a.OwnerId, a.State));
                    }
                }
            }
        }
        catch (Exception e)
        {
            if (!_scanWarned)
            {
                _scanWarned = true;
                Log.Warn($"[{KleeMod.ModId}] plans view: action scan skipped: {e}");
            }
        }
        return states;
    }

    /// <summary>
    /// THE GAME'S PAUSE-FOR-CHOICE (the patch below): a choice of hers is
    /// beginning, so an open view gets out of its way before its screen or
    /// hand selection comes up. A choice of the other seat's leaves it open.
    /// Never throws into the game's action code.
    /// </summary>
    internal static void OnChoiceBegun(GameAction? action)
    {
        try
        {
            if (_screen == null || action == null || _owner is not { } me) return;
            if (action.OwnerId != me.NetId) return;
            if (!KokomiResources.IsKokomi(me.Creature)) return;
            Close();
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plans view: choice close skipped: {e}");
        }
    }

    private static bool HasOwner(CardModel card)
    {
        try
        {
            return card.Owner != null;
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>
    /// A press on a card in the view (the click patch below). A two-line
    /// Plan is flipped through the strip's own request; anything else says
    /// why in the prompt. The view stays open either way.
    /// </summary>
    internal static void OnPicked(CardModel card)
    {
        try
        {
            if (_owner is not { } me) return;
            var queue = KokomiPlan.Pending(me);
            var index = KokomiPlanViewRows.QueueIndex(queue, card);
            if (index < 0)
            {
                SetPrompt("That Plan is no longer waiting.");
                return;
            }
            // Read BEFORE the request: a flip that resolves at once must not
            // turn the message round.
            var before = queue[index];
            var why = KokomiPlan.RequestFlip(me, index);
            SetPrompt(why == null
                ? KokomiPlanViewRows.FlipSent(before)
                : Capitalise(why) + ".");
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plans view: flip skipped: {e}");
        }
    }

    private static string Capitalise(string s) =>
        s.Length == 0 ? s : char.ToUpperInvariant(s[0]) + s.Substring(1);

    private static void SetPrompt(string text)
    {
        var label = _screen?.GetNodeOrNull<Control>("%BottomText")
            ?.GetNodeOrNull<MegaRichTextLabel>("%BottomLabel");
        if (label != null) label.Text = text;
    }

    /// <summary>The queue moved (a flip landed): repaint every caption.
    /// Driven by <c>KokomiPlanStrip.Refresh</c>.</summary>
    internal static void Refresh(Player? player)
    {
        if (_screen == null || !ReferenceEquals(player, _owner)) return;
        Decorate(repaint: true);
    }

    /// <summary>Every frame while the view is open: close it if a choice of
    /// hers has begun (the backstop to <see cref="OnChoiceBegun"/>), else
    /// caption the grid.</summary>
    private static void OnFrame()
    {
        try
        {
            if (_owner is { } me
                && KokomiPlanViewRows.ChoiceTakesOver(
                    ActionStates(), me.NetId,
                    NCombatRoom.Instance?.Ui?.Hand?.IsInCardSelection == true))
            {
                Close();
                return;
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plans view: choice check skipped: {e}");
        }
        Decorate(repaint: false);
    }

    /// <summary>
    /// Give each grid card its caption. The grid builds its holders
    /// asynchronously, so this runs every frame while the view is open and
    /// adds what is missing; a repaint rewrites every caption.
    /// </summary>
    private static void Decorate(bool repaint)
    {
        try
        {
            if (_screen == null || !GodotObject.IsInstanceValid(_screen)
                || _owner is not { } me)
            {
                return;
            }
            var grid = _screen.GetNodeOrNull<NCardGrid>("%CardGrid");
            if (grid == null) return;
            var queue = KokomiPlan.Pending(me);
            foreach (var card in Shown)
            {
                var holder = grid.GetCardHolder(card);
                if (holder == null) continue;
                var caption = holder.GetNodeOrNull<Label>(CaptionName);
                if (caption != null && !repaint) continue;
                caption ??= AddCaption(holder);
                var index = KokomiPlanViewRows.QueueIndex(queue, card);
                var flipped = index >= 0 && queue[index].TwoLine && queue[index].Now;
                caption.Text = index < 0
                    ? string.Empty
                    : KokomiPlanViewRows.Caption(index, queue[index]);
                caption.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                    flipped ? FlippedTint : CaptionColor);
                if (holder.CardNode is { } node)
                {
                    node.Modulate = flipped ? FlippedTint : Colors.White;
                }
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plans view: caption skipped: {e}");
        }
    }

    /// <summary>A caption straddling the bottom edge of the card, which a
    /// grid holder draws centred on its own origin (<c>NCard.defaultSize</c>
    /// 300x422).</summary>
    private static Label AddCaption(Control holder)
    {
        var size = NCard.defaultSize;
        var label = new Label
        {
            Name = CaptionName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            Position = new Vector2(-size.X / 2f, size.Y / 2f - 18f),
            Size = new Vector2(size.X, CaptionFontSize + 14f),
        };
        label.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       CaptionFontSize);
        label.AddThemeStyleboxOverride("normal", new StyleBoxFlat
        {
            BgColor = new Color(0f, 0f, 0f, 0.75f),
            CornerRadiusTopLeft = 8,
            CornerRadiusTopRight = 8,
            CornerRadiusBottomLeft = 8,
            CornerRadiusBottomRight = 8,
        });
        holder.AddChildSafely(label);
        return label;
    }

    /// <summary>B: close the view. Confirm closes it through the screen's own
    /// button; both end in <see cref="Forget"/>.</summary>
    internal static void Close()
    {
        var screen = _screen;
        // Let go first, so a second B before the screen is freed is a no-op.
        Forget();
        try
        {
            if (screen != null && GodotObject.IsInstanceValid(screen)
                && NOverlayStack.Instance is { } overlays)
            {
                overlays.Remove(screen);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] plans view: close skipped: {e}");
        }
    }

    /// <summary>Drop every hold this view has: B's binding, the frame hook,
    /// the screen. Idempotent.</summary>
    private static void Forget()
    {
        NHotkeyManager.Instance?.RemoveHotkeyPressedBinding(
            MegaInput.cancel, CloseAction);
        // Off the tree it was added to, once: a second Forget (Close, then the
        // screen's own exit) finds nothing to take off.
        var tree = _frameTree;
        _frameTree = null;
        if (tree != null && GodotObject.IsInstanceValid(tree))
        {
            tree.ProcessFrame -= OnFrame;
        }
        _screen = null;
        _owner = null;
        Shown.Clear();
    }
}

/// <summary>
/// THE VIEW'S RULES, pure so they are pinned headlessly: which Plans it
/// shows and in what order, which it can flip, what each caption says, and
/// where the strip's button hint sits.
/// </summary>
public static class KokomiPlanViewRows
{
    /// <summary>The caption on a Plan with one line.</summary>
    public const string PlanOnlyCaption = "Plan only";

    /// <summary>The words beside the button glyph under the strip.</summary>
    public const string HintCaption = "Plans";

    /// <summary>The card a Plan is shown as: its own card, or the card that
    /// wrote it where it holds none. Null shows nothing.</summary>
    public static CardModel? Face(KokomiPlan.Entry entry) =>
        entry.Source ?? entry.Writer;

    /// <summary>
    /// The queue positions the view shows, in queue order (the first Plan
    /// first). A Plan with no card to show is left out, and a card already
    /// shown is not shown twice -- the grid answers a press with the card, so
    /// one card must name one Plan.
    /// </summary>
    public static IReadOnlyList<int> Shown(IReadOnlyList<KokomiPlan.Entry> queue)
    {
        var shown = new List<int>();
        for (var i = 0; i < queue.Count; i++)
        {
            var face = Face(queue[i]);
            if (face != null && QueueIndex(queue, face) == i) shown.Add(i);
        }
        return shown;
    }

    /// <summary>The queue position a pressed card names: the first Plan shown
    /// as it, or -1 where none is waiting any more.</summary>
    public static int QueueIndex(IReadOnlyList<KokomiPlan.Entry> queue,
                                 CardModel? card)
    {
        if (card == null) return -1;
        for (var i = 0; i < queue.Count; i++)
        {
            if (ReferenceEquals(Face(queue[i]), card)) return i;
        }
        return -1;
    }

    /// <summary>
    /// Do the game's actions keep the view shut? Yes while any action is
    /// running, and while one of her own (<paramref name="me"/>) is queued,
    /// running, paused for a choice or about to resume -- the turn-start hook
    /// that carries out the Plans is one of hers, and its choice must reach
    /// her first. The other seat's queued or choosing actions do not.
    /// </summary>
    public static bool OpenBlockedByActions(
        IEnumerable<(ulong Owner, GameActionState State)> actions, ulong me)
    {
        foreach (var (owner, state) in actions)
        {
            if (state == GameActionState.Executing) return true;
            if (owner == me && Live(state)) return true;
        }
        return false;
    }

    /// <summary>
    /// Must an open view close for a choice? Yes once one of her own actions
    /// is gathering a choice, or her hand has gone into a selection.
    /// </summary>
    public static bool ChoiceTakesOver(
        IEnumerable<(ulong Owner, GameActionState State)> actions, ulong me,
        bool handSelecting)
    {
        if (handSelecting) return true;
        foreach (var (owner, state) in actions)
        {
            if (owner == me && state == GameActionState.GatheringPlayerChoice)
            {
                return true;
            }
        }
        return false;
    }

    private static bool Live(GameActionState state) => state is
        GameActionState.WaitingForExecution or GameActionState.Executing
        or GameActionState.GatheringPlayerChoice
        or GameActionState.ReadyToResumeExecuting;

    /// <summary>
    /// Is the strip's "Plans" hint drawn? Only with Plans waiting and not
    /// while the morning is carrying them out: a Plan's choice screen takes
    /// the same key for its own peek button then (2026-10-17).
    /// </summary>
    public static bool HintShown(int count, bool draining) =>
        count > 0 && !draining;

    /// <summary>Can a press flip this Plan? Only a two-line one.</summary>
    public static bool Flippable(KokomiPlan.Entry entry) => entry.TwoLine;

    /// <summary>The line a Plan will be carried out as.</summary>
    public static string LineCaption(KokomiPlan.Entry entry) =>
        !entry.TwoLine ? PlanOnlyCaption
        : entry.Now ? KokomiPlanStrip.NowLineCaption
        : KokomiPlanStrip.PlanLineCaption;

    /// <summary>The caption under a card in the view: its place and its
    /// line, "1. Plan line".</summary>
    public static string Caption(int index, KokomiPlan.Entry entry) =>
        $"{index + 1}. {LineCaption(entry)}";

    /// <summary>The prompt after a flip was sent: the line it is flipping
    /// to (the caption repaints when it lands).</summary>
    public static string FlipSent(KokomiPlan.Entry before) =>
        $"{before.Title}: flipping to its "
        + (before.Now ? "Plan line." : "now-line.");

    /// <summary>
    /// The words of the strip's button hint, or null for none. A controller
    /// shows the glyph and "Plans"; keyboard play names the peek key ("S:
    /// Plans" keyboard-only, "Space: Plans" with a mouse, 2026-10-16). A
    /// mouse player whose peek key is unbound still sees "Plans", since the
    /// hint is clickable; keyboard-only play with no key shows nothing.
    /// </summary>
    public static string? HintText(InputType input, string? key) => input switch
    {
        InputType.Controller => HintCaption,
        InputType.KeyboardOnlyMode when !string.IsNullOrEmpty(key) =>
            $"{key}: {HintCaption}",
        InputType.MouseAndKeyboard => string.IsNullOrEmpty(key)
            ? HintCaption
            : $"{key}: {HintCaption}",
        _ => null,
    };

    /// <summary>
    /// A bound key's name as the hint prints it: "Space", "S", a number key
    /// as its digit ("Key1" is "1"); an unbound key (<c>Key.None</c>) is
    /// null.
    /// </summary>
    public static string? KeyName(Key key)
    {
        if (key == Key.None) return null;
        var name = key.ToString();
        return name.Length == 4 && name.StartsWith("Key", StringComparison.Ordinal)
            && char.IsDigit(name[3])
            ? name.Substring(3)
            : name;
    }

    /// <summary>
    /// Where the hint sits in the strip's column, in picture rows from the
    /// top: under the last picture drawn, or under the pager where there is
    /// one (<see cref="KokomiPlanPages.PerPage"/> rows plus the pager's).
    /// </summary>
    public static int HintRow(int drawn, int count) =>
        count > KokomiPlanPages.PerPage
            ? KokomiPlanPages.PerPage + 1
            : Math.Clamp(drawn, 0, KokomiPlanPages.PerPage);
}

/// <summary>
/// A press on a card in the Plans view flips it instead of selecting it, so
/// the view stays open and never completes with a "selection". Every other
/// card grid in the game is untouched: the prefix answers true (run the
/// original) for any screen this mod did not open as the Plans view.
/// </summary>
// Character scope: `Owns` answers true only for the screen `TryOpen` opened,
// and only while its owner is Kokomi; every other grid runs the original.
[HarmonyPatch(typeof(NSimpleCardSelectScreen), "OnCardClicked")]
internal static class NSimpleCardSelectScreen_OnCardClicked_KokomiPlanView_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(NSimpleCardSelectScreen __instance, CardModel card)
    {
        if (!KokomiPlanView.Owns(__instance)) return true;
        KokomiPlanView.OnPicked(card);
        return false;
    }
}

/// <summary>
/// A choice is beginning: the game pauses the chooser's action here, on every
/// peer, before the choice screen or hand selection comes up. The postfix
/// closes the local Plans view if the choice is its owner's. Local UI only;
/// the action, the queue and the choice are untouched.
/// </summary>
// Character scope: `OnChoiceBegun` acts only while this mod's Plans view is
// open (a Kokomi seat's), and only for its owner's action; otherwise it
// returns at once.
[HarmonyPatch(typeof(ActionQueueSet), nameof(ActionQueueSet.PauseActionForPlayerChoice))]
internal static class ActionQueueSet_PauseActionForPlayerChoice_KokomiPlanView_Patch
{
    [HarmonyPostfix]
    public static void Postfix(GameAction action) =>
        KokomiPlanView.OnChoiceBegun(action);
}
