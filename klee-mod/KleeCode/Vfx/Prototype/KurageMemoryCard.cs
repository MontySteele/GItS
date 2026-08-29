using System.Collections.Generic;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens;

namespace KleeMod.Vfx;

/// <summary>
/// THE KURAGE MEMORY CARD -- [USER]'s direction, `M61` = option 3
/// (review/active/kokomi-kurage-memory-2026-08-29.md §14; §14.8 is the pick,
/// §14.1 is [USER]'s five quotes and IS the spec). This retires the
/// `kokomi_memory` strip that used to draw the whole queue as text into the
/// shared gauge's one label.
///
/// WHAT IT DRAWS, AND IT IS TWO THINGS. At the left edge of the screen: the
/// FRONT memory's card portrait, ringed blue when the bank pays its price and
/// red when it does not, and the Charge count under it, large. That is the
/// whole resting element -- no bar, no "(price)" line, no second and third
/// card. An empty queue draws the Charge count ALONE, which is the state the
/// blind tester could not tell from a block (§14.2 frame 2).
///
/// THE DIVISION OF LABOUR IS THE POINT (§14.3): the HUD answers "does the next
/// one fire" and the pile answers "how far do I get". The first is a fact --
/// one comparison, `bank &gt;= front.Price` -- and needs no forecast. The
/// second IS a forecast, so it lives behind a click, on a surface the player
/// opened on purpose, where a wrong prediction cannot be read as a lie. The
/// forecast itself is <see cref="KurageMemory.Affordability"/> and is never
/// re-derived here.
///
/// LOCAL SEAT ONLY, and that is a ruled loss rather than an oversight. There
/// is exactly one `NCombatUi` and `Activate` binds it with
/// `LocalContext.GetMe(state)`; a partner gets a compact
/// `NMultiplayerPlayerState` widget, not a second HUD. [USER], asked directly:
/// "Local only is fine (partner doesn't need to see the queue)". So at a
/// Kokomi + Kokomi table the partner's memory is not shown at all, where the
/// creature-tracked strip used to show it over her head (§14.5).
///
/// NO NEW SCENE AND NO NEW ART, which is why option 3 won: the thumbnail is
/// `CardModel.Portrait`, one cached `Texture2D` property that works for
/// base-game cards in the queue as well as ours; the ring, the badge and the
/// count are plain Godot `Panel`/`Label` nodes; and the queue viewer is the
/// GAME'S own `NCardPileScreen` over a `CardPile` we build. Nothing here needs
/// a pck rebuild, so an iteration on the look is a C# build.
///
/// QUARANTINED. `Vfx/Prototype/**` is Compile Remove'd without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
internal static class KurageMemoryCard
{
    /// <summary>Node name, so a rebuilt combat UI can find and free its own
    /// element rather than accumulating one per Activate.</summary>
    private const string RootName = "KleeKurageMemoryCard";

    // -- geometry. Screen-space, in the game's 1920x1080 design resolution.

    /// <summary>Distance from the left edge. Inside the relic inventory's
    /// column but BELOW it -- see the anchor note on <see cref="Build"/>.</summary>
    private const float EdgeMargin = 30f;

    private const float ThumbWidth = 104f;

    /// <summary>The card face's own aspect (`NCard.defaultSize` is 300x422),
    /// so the portrait is not stretched.</summary>
    private const float ThumbHeight = ThumbWidth * 422f / 300f;

    /// <summary>The ring is the card's whole state, so it is thick enough to
    /// read at thumbnail size without a second cue.</summary>
    private const int RingWidth = 4;

    private const int CountFontSize = 52;

    /// <summary>Godot's own theme entry for a `Panel`'s stylebox.
    /// `ThemeConstants` (the game's cache of theme StringNames) has groups for
    /// Label, RichTextLabel, Control and the containers, but none for Panel, so
    /// this is spelled here rather than borrowed from a group that does not
    /// exist.</summary>
    private static readonly StringName PanelStyleBox = "panel";

    private const int BadgeFontSize = 22;

    // -- colours. THE GAME'S OWN, never invented (§14.3).

    /// <summary>`StsColors.blue` (87CEEB). The engine has no "affordable"
    /// colour -- affordability is drawn in `cream` on a cost badge -- so this
    /// is the closest existing BLUE, and it is the one [USER]'s direction asks
    /// for by name. Its outline partner is `defaultStarCostOutline` (175561),
    /// the same blue-black the star badge wears when it is payable.</summary>
    private static readonly Color RingBlue = StsColors.blue;

    private static readonly Color RingBlueDeep = StsColors.defaultStarCostOutline;

    /// <summary>`StsColors.red` with `unplayableEnergyCostOutline` -- literally
    /// `CardCostHelper.GetStarCostColor`'s InsufficientResources arm, the same
    /// pair `SparkCostBadge` uses. The engine's own "you cannot pay this".</summary>
    private static readonly Color RingRed = StsColors.red;

    private static readonly Color RingRedDeep = StsColors.unplayableEnergyCostOutline;

    /// <summary>The empty state has no card and therefore no affordability;
    /// the count is drawn in the game's neutral text colour so it does not
    /// claim a state it does not have.</summary>
    private static readonly Color CountNeutral = StsColors.cream;

    /// <summary>One element, one seat: the key is the local Player. Registered
    /// through the shared skeleton so a combat teardown frees it exactly the
    /// way it frees the gauges.</summary>
    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    /// <summary>
    /// Build the element for the LOCAL seat and nothing else.
    ///
    /// Called from the `NCombatUi.Activate` postfix `GaugeBridge` already
    /// installs -- the same hook, so there is one combat-lifecycle entry point
    /// rather than two that can disagree about when a room is live.
    /// </summary>
    public static void Setup(CombatState state)
    {
        var me = LocalContext.GetMe(state);
        var creature = me?.Creature;
        if (me == null || !KokomiResources.IsKokomi(creature))
        {
            // Not our seat's character: draw nothing at all. A Furina at this
            // table has no memory and must not get an empty one.
            return;
        }

        if (NCombatRoom.Instance?.Ui is not { } ui)
        {
            return;
        }

        Discard(me);
        var root = Build();
        ui.AddChildSafely(root);
        Displays.Set(me, root);
        Paint(root, me, creature!);
    }

    /// <summary>
    /// Re-read the bank and the queue and redraw.
    ///
    /// THE REFRESH PATH IS THE STRIP'S, unchanged: `KurageMemory.RefreshStrip`
    /// calls `GaugeBridge.Refresh(creature)` on every Charge mutation and every
    /// queue move, and `GaugeBridge.Refresh` now calls this. Reusing the funnel
    /// rather than adding one is the whole reason the strip's numbers never
    /// drifted, and there is no polling anywhere in this file.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (player == null || !LocalContext.IsMe(player)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            // Stale or never built (mid-combat reload): rebuild in place, the
            // reference-bridge idiom GaugeBridge.Refresh uses.
            if (KurageMemory.Combat is not { } combat) return;
            Setup(combat);
            root = Displays.Get(player);
            if (root == null) return;
        }

        Paint(root, player, creature!);
    }

    public static void DiscardAll(CombatState? state)
    {
        var me = state == null ? null : LocalContext.GetMe(state);
        if (me != null) Discard(me);
    }

    private static void Discard(Player player) => Displays.Discard(player);

    // ----------------------------------------------------------- drawing --

    /// <summary>
    /// The node tree, built once per combat.
    ///
    /// THE ANCHOR, and it is the one piece of this build the mod has never
    /// done before (§14.7 asked for a spike). The left edge is crowded top and
    /// bottom: the relic inventory occupies the top-left AND GROWS DOWNWARD as
    /// relics accumulate, and the energy orb and draw pile sit at the bottom.
    /// The free band is the middle, and its top boundary moves during a run.
    ///
    /// The game's own answer to that problem is to position off
    /// `NRelicInventory.GetBottomOfInventory()` and subscribe to `RelicsChanged`
    /// and `Viewport.SizeChanged`, which is what
    /// `NMultiplayerPlayerStateContainer` does. This does the SIMPLER thing
    /// that needs neither: it anchors to the left edge, VERTICALLY CENTRED, so
    /// it sits in the middle of the free band by construction and follows a
    /// resize through Godot's own anchor propagation with no signal
    /// subscription and no base-game type. If the live check finds it colliding
    /// with a deep relic column, the relic-relative pattern is the known
    /// upgrade and nothing else about this file changes.
    ///
    /// WHETHER IT CLEARS THE COLUMN IS A LIVE QUESTION. Nothing headless can
    /// answer it; `EB-198`'s acceptance is a frame on a `+proto` dev deploy.
    /// </summary>
    private static Control Build()
    {
        var root = new Control
        {
            Name = RootName,
            MouseFilter = Control.MouseFilterEnum.Stop,
            // Left edge, vertically centred. The offsets are measured from
            // that anchor, so the element keeps its band under any resolution.
            AnchorLeft = 0f,
            AnchorRight = 0f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = EdgeMargin,
            OffsetRight = EdgeMargin + ThumbWidth,
            OffsetTop = -(ThumbHeight + CountFontSize) / 2f,
            OffsetBottom = (ThumbHeight + CountFontSize) / 2f,
        };

        // The ring IS the card's border: a bordered panel with the portrait
        // inset inside it, so there is one node to recolour and no second
        // outline to keep in sync.
        var ring = new Panel
        {
            Name = "Ring",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = Vector2.Zero,
            Size = new Vector2(ThumbWidth, ThumbHeight),
        };
        root.AddChildSafely(ring);

        var thumb = new TextureRect
        {
            Name = "Thumb",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered,
            Position = new Vector2(RingWidth, RingWidth),
            Size = new Vector2(ThumbWidth - 2 * RingWidth,
                               ThumbHeight - 2 * RingWidth),
        };
        ring.AddChildSafely(thumb);

        // The price as a small badge ON the thumbnail. [USER] dropped the
        // parenthesised spend under the number; the badge is what is left, and
        // it says what THIS card costs rather than forecasting anything.
        var badge = new Label
        {
            Name = "Badge",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            HorizontalAlignment = HorizontalAlignment.Right,
            Position = new Vector2(ThumbWidth - 46f, 4f),
            Size = new Vector2(40f, 26f),
        };
        badge.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       BadgeFontSize);
        badge.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                    StsColors.cream);
        ring.AddChildSafely(badge);

        var count = new Label
        {
            Name = "Count",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            HorizontalAlignment = HorizontalAlignment.Center,
            Position = new Vector2(0f, ThumbHeight + 4f),
            Size = new Vector2(ThumbWidth, CountFontSize + 8f),
        };
        count.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       CountFontSize);
        root.AddChildSafely(count);

        root.GuiInput += @event =>
        {
            if (@event is InputEventMouseButton
                { Pressed: true, ButtonIndex: MouseButton.Left })
            {
                OpenQueue();
            }
        };

        return root;
    }

    /// <summary>
    /// Draw the two facts.
    ///
    /// EVERY BRANCH IS A REAL STATE from the mock's four: a payable front
    /// (blue), a blocked front (red), a FREE front (blue -- the old "Charge 1 /
    /// 0" frame that read as a fraction over zero, which is exactly the frame
    /// `EB-198` was filed on), and an empty queue (the count alone, no
    /// thumbnail, no ring).
    /// </summary>
    private static void Paint(Control root, Player player, Creature creature)
    {
        var ring = root.GetNodeOrNull<Panel>("Ring");
        var thumb = ring?.GetNodeOrNull<TextureRect>("Thumb");
        var badge = ring?.GetNodeOrNull<Label>("Badge");
        var count = root.GetNodeOrNull<Label>("Count");
        if (ring == null || thumb == null || badge == null || count == null)
        {
            return;
        }

        var bank = KokomiResources.GetCharge(creature);
        var queue = KurageMemory.Queue(player);
        var front = queue.Count > 0 ? queue[0] : null;

        count.Text = bank.ToString();

        if (front == null)
        {
            // EMPTY IS NOT BLOCKED. No card, no ring, and the count in the
            // neutral colour: an empty memory has no affordability to report
            // and must not borrow the blocked one's red.
            ring.Visible = false;
            count.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                        CountNeutral);
            return;
        }

        var payable = bank >= front.Price;
        var edge = payable ? RingBlue : RingRed;
        var deep = payable ? RingBlueDeep : RingRedDeep;

        ring.Visible = true;
        ring.AddThemeStyleboxOverride(PanelStyleBox,
                                      RingStyle(edge, deep));
        thumb.Texture = front.Card.HasPortrait ? front.Card.Portrait : null;
        badge.Text = front.Price == 0 ? "free" : front.Price.ToString();
        count.AddThemeColorOverride(ThemeConstants.Label.FontColor, edge);
    }

    private static StyleBoxFlat RingStyle(Color edge, Color deep)
    {
        var style = new StyleBoxFlat
        {
            BgColor = deep,
            BorderColor = edge,
        };
        style.SetBorderWidthAll(RingWidth);
        style.SetCornerRadiusAll(6);
        return style;
    }

    // ------------------------------------------------------- the click --

    /// <summary>
    /// Open the whole queue in the GAME'S pile viewer.
    ///
    /// `NCardPileScreen.ShowScreen(pile, hotkeys)` takes any `CardPile`, so we
    /// build one and `AddInternal` the queue's live `CardModel` instances in
    /// order, front first. The pile is held in a static for the screen's
    /// lifetime because `NCardPileScreen._EnterTree` subscribes to its
    /// `ContentsChanged`.
    ///
    /// `PileType.None` DELIBERATELY. `_Ready` switches on `Pile.Type` for its
    /// bottom info text: `Draw` also RE-SORTS the list by rarity, which would
    /// destroy the one thing this view is for -- the ORDER -- and `Discard` /
    /// `Exhaust` would print somebody else's explanatory sentence. `None` hides
    /// the label and logs one benign "CardPileScreen has no info text." line.
    ///
    /// THIS IS NOT `CardSelectCmd`. That route is an awaited CHOICE against a
    /// `PlayerChoiceContext` a HUD click does not have, and pushing a selector
    /// outside resolution is banned mod-wide in a lockstep co-op game. This is
    /// the read-only cousin.
    /// </summary>
    private static void OpenQueue()
    {
        var player = LocalContext.GetMe(KurageMemory.Combat);
        var creature = player?.Creature;
        if (player == null || !KurageMemory.IsLive(creature)) return;

        var queue = KurageMemory.Queue(player);
        if (queue.Count == 0) return;         // nothing to show; do not open

        var pile = new CardPile(PileType.None);
        var states = KurageMemory.Affordability(
            queue, KokomiResources.GetCharge(creature));

        var projection = new Dictionary<CardModel, KurageMemory.EntryState>();
        for (var i = 0; i < queue.Count; i++)
        {
            pile.AddInternal(queue[i].Card);
            // Identity, not id: an Entry holds the live CardModel instance
            // deliberately, so the same instance is what the grid renders.
            projection[queue[i].Card] = states[i];
        }

        KurageMemoryPileRing.Arm(pile, projection);
        NCardPileScreen.ShowScreen(pile, CloseHotkeys);
    }

    private static readonly string[] CloseHotkeys = { "ui_cancel" };
}

/// <summary>
/// "ALSO RED" IN THE PILE VIEW -- [USER] asked whether it was possible
/// ("otherwise dimmed is fine") and it is, so the dimmed fallback is not built.
///
/// THE MECHANISM IS `SparkCostBadge`'s, on the same class. The pile screen
/// renders every entry as a real `NCard` through `NCardGrid`, and a Harmony
/// postfix on `NCard.UpdateStarCostVisuals` -- private, called from
/// `UpdateVisuals` and `SetPretendCardCanBePlayed`, i.e. from every redraw the
/// game already performs -- reaches each of them with no polling of its own.
/// This paints a ring rather than a badge, and it paints
/// <see cref="KurageMemory.Affordability"/>'s answer, so the pile view and the
/// wire snapshot cannot disagree.
///
/// SCOPED THREE WAYS so an ordinary pile viewer showing the same card is
/// untouched: it is armed only while OUR pile is the open one
/// (<see cref="Arm"/> / <see cref="Disarm"/>), it fires only for a `CardModel`
/// instance that is in the projection, and a card with no ring of ours gets its
/// ring node hidden rather than left painted -- so a pooled `NCard` reused for
/// somebody else's deck cannot inherit a memory colour.
/// </summary>
internal static class KurageMemoryPileRing
{
    private const string RingName = "KleeKurageQueueRing";

    private const int RingWidth = 8;

    /// <summary>Godot's theme entry for a `Panel`'s stylebox; see the twin note
    /// on <see cref="KurageMemoryCard"/>.</summary>
    private static readonly StringName PanelStyleBox = "panel";

    private static CardPile? _pile;

    private static Dictionary<CardModel, KurageMemory.EntryState> _projection
        = new();

    /// <summary>The pile we opened, so `_ExitTree` can tell it from any
    /// other.</summary>
    internal static CardPile? OpenPile => _pile;

    internal static void Arm(
        CardPile pile,
        Dictionary<CardModel, KurageMemory.EntryState> projection)
    {
        _pile = pile;
        _projection = projection;
    }

    internal static void Disarm()
    {
        _pile = null;
        _projection = new Dictionary<CardModel, KurageMemory.EntryState>();
    }

    internal static void Paint(NCard nCard)
    {
        CardModel? card = nCard.Model;
        if (card == null || !nCard.IsNodeReady()) return;

        var ring = nCard.GetNodeOrNull<Panel>(RingName);

        if (_pile == null || !_projection.TryGetValue(card, out var state))
        {
            // Not ours, or ours is closed. Hide any ring this node still
            // carries from a previous open; never leave one painted.
            if (ring != null) ring.Visible = false;
            return;
        }

        if (ring == null)
        {
            ring = new Panel
            {
                Name = RingName,
                MouseFilter = Control.MouseFilterEnum.Ignore,
            };
            nCard.AddChildSafely(ring);
            // FullRect rather than a measured size: the ring then covers the
            // card's own rect whatever `NCard.defaultSize` and Scale are doing,
            // with no geometry of ours to drift against the base game's.
            ring.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        }

        // Payable is blue; RunsOut and Held are BOTH red -- that is the whole
        // of "also red", and it is true because an unaffordable front holds and
        // pays nothing, so nothing behind it fires.
        var blue = state == KurageMemory.EntryState.Payable;
        var style = new StyleBoxFlat
        {
            BgColor = StsColors.transparentBlack,
            BorderColor = blue ? StsColors.blue : StsColors.red,
        };
        style.SetBorderWidthAll(RingWidth);
        style.SetCornerRadiusAll(12);

        ring.Visible = true;
        ring.AddThemeStyleboxOverride(PanelStyleBox, style);
    }
}

/// <summary>The one arming point for the queue ring, deliberately the same hook
/// `SparkCostBadge` uses: every redraw the game already performs.</summary>
[HarmonyPatch(typeof(NCard), "UpdateStarCostVisuals")]
internal static class NCard_UpdateStarCostVisuals_KurageQueueRing_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance)
        => KurageMemoryPileRing.Paint(__instance);
}

/// <summary>
/// Disarm when the viewer leaves the tree. `_ExitTree` rather than
/// `AfterCapstoneClosed` because it fires on every removal path, including the
/// ones a capstone close does not run.
/// </summary>
[HarmonyPatch(typeof(NCardPileScreen), nameof(NCardPileScreen._ExitTree))]
internal static class NCardPileScreen_ExitTree_KurageQueueRing_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCardPileScreen __instance)
    {
        if (KurageMemoryPileRing.OpenPile != null
            && ReferenceEquals(__instance.Pile, KurageMemoryPileRing.OpenPile))
        {
            KurageMemoryPileRing.Disarm();
        }
    }
}

/// <summary>The element dies with the combat, like the gauges do.</summary>
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_KurageMemoryCard_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => KurageMemoryCard.DiscardAll(
        KurageMemory.Combat);
}
