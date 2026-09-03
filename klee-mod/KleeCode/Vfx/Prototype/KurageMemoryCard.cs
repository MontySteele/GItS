using System;
using System.Collections.Generic;
using BaseLib.Abstracts;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens;

namespace KleeMod.Vfx;

/// <summary>
/// THE KURAGE MEMORY CARD -- [USER]'s direction, `M61` = option 3
/// (review/ruled/kokomi-kurage-memory-2026-08-29.md §14; §14.8 is the pick,
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
        var me = TryGetMe(state);
        var creature = me?.Creature;
        if (me == null || !KokomiResources.IsKokomi(creature))
        {
            // Not our seat's character: draw nothing at all. A Furina at this
            // table has no memory and must not get an empty one.
            return;
        }
        // NOR UNDER THE OVERHAUL ARM. A dev build compiles the memory and the
        // overhaul together, and the overhaul retires the memory's rules at the
        // funnel -- so this strip would draw a Charge count that never moves
        // beside a queue that can never fill. `KokomiPlanStrip` has the band
        // under that arm; this is the third door where that scope is spelled
        // rather than inferred (`EB-207`'s correction).
        if (KokomiOverhaul.LiveFor(creature)) return;

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
    ///
    /// TWO PREDICATES, NOT ONE (`EB-207`). Being the local seat is not being
    /// KOKOMI's seat, and this entry point used to ask only the first: a Klee
    /// or Furina seat reached the rebuild branch below and was turned away by
    /// <see cref="Setup"/>'s own character test, one call further in. That was
    /// correct and it was INDIRECT -- the scope rule lived in exactly one
    /// place, and the other door into the element leaned on it. It is spelled
    /// at both doors now, because the defect this row is named for was a
    /// second reader (the blind page) making precisely that mistake against
    /// the same rule, and the fix is worth nothing if it holds in one engine.
    /// The predicate is `KokomiResources.IsKokomi`, the one the gauge specs,
    /// `KurageMemory.IsLive` and `Setup` all already ask.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (player == null || !LocalContext.IsMe(player)) return;
        if (!KokomiResources.IsKokomi(creature)) return;
        if (KokomiOverhaul.LiveFor(creature)) return;

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

    /// <summary>
    /// Teardown, and it is CHARACTER-SCOPED like every other door into this
    /// element (EB-225 / R225 item 6). The seat guard alone was never the
    /// whole rule: the one `PROTOTYPE_CARDS` switch compiles Kokomi's memory
    /// and Klee's Sparks together, so a patch of this arm's that asks only
    /// "is there a seat" still runs on a Klee or Furina seat. Nothing was
    /// ever built for one -- <see cref="Setup"/> refuses at the door -- so
    /// the predicate here costs a teardown nothing and says the scope out
    /// loud at the third door rather than leaving it to be inferred from the
    /// first, which is exactly the `EB-207` correction one level up.
    /// </summary>
    public static void DiscardAll(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !KokomiResources.IsKokomi(me.Creature)) return;
        Discard(me);
    }

    private static void Discard(Player player) => Displays.Discard(player);

    /// <summary>
    /// The local seat, or null when the combat cannot name one.
    ///
    /// `LocalContext.GetMe(ICombatState)` DOES NOT ANSWER NULL FOR "not
    /// there". Its whole body is: no `NetId` -> null; otherwise
    /// `state.GetPlayer(NetId.Value)`, and a miss is
    /// `throw new InvalidOperationException("Local player not found in
    /// combat.")`. Every call in this file was written against the first arm
    /// and read the second as impossible -- `me == null` guards that can never
    /// see the case they were guarding.
    ///
    /// IT IS NOT IMPOSSIBLE, and it ended two whole-fight blind sessions
    /// (`KLEESPARK-W1`, `KLEESPARK-W2`) at the first frame of their SECOND
    /// Monster room. `NCombatRoom._Ready` calls `NCombatUi.Deactivate` while
    /// the incoming room is still being built, our Deactivate postfix asked
    /// the combat we still hold for its local seat, the combat had no players
    /// in it yet, and the throw escaped `_Ready`. The room's `_Ready` then
    /// never finished, so `CombatVfxContainer` was null when `Activate` ran a
    /// frame later, the gauge spawn NRE'd out of `CombatManager.SetUpCombat`,
    /// and the fight never started at all: the wire answered `monster` with no
    /// `battle` block for as long as anyone cared to poll it.
    ///
    /// So the resolution is guarded here, once, for all three callers, in the
    /// same shape `SelectionTelemetry` already uses on this API. A visual
    /// element that cannot find its seat draws nothing; it does not take the
    /// room down. The warning is loud because a seat that cannot be resolved
    /// mid-combat would be a real defect -- it is just not one worth ending a
    /// run over.
    ///
    /// `internal` rather than `private` since EB-225: the queue ring below is
    /// a second element in this file that must name the seat to scope itself,
    /// and it must reach the SAME guard rather than a second copy of it.
    /// </summary>
    internal static Player? TryGetMe(CombatState? state)
    {
        if (state == null) return null;
        try
        {
            return LocalContext.GetMe(state);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] kurage memory: no local seat in this "
                   + $"combat ({e.GetType().Name}: {e.Message}); drawing "
                   + "nothing.");
            return null;
        }
    }

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
        thumb.Texture = Portrait(front.Card);
        badge.Text = front.Price == 0 ? "free" : front.Price.ToString();
        count.AddThemeColorOverride(ThemeConstants.Label.FontColor, edge);
    }

    /// <summary>
    /// The card's picture, OURS FIRST.
    ///
    /// `EB-198`'s live acceptance caught §14.5 exactly backwards. That section
    /// read `CardModel.Portrait` off the decompile and concluded it "works for
    /// base-game cards in the queue as well as ours"; the first live frame drew
    /// an empty ring, because a MOD card has no `PortraitPath` to load. Our art
    /// is a runtime `ImageTexture` handed over through BaseLib's portrait patch
    /// as <c>CustomCardModel.CustomPortrait</c> (`RosterArt.CardPortrait`,
    /// KleeArt.cs) and never reaches the base path at all.
    ///
    /// So: the override when the model has one, the base property otherwise --
    /// which keeps the half of §14.5 that WAS right, a base-game card in the
    /// queue drawing its own face with no per-roster art table.
    /// </summary>
    private static Texture2D? Portrait(CardModel card)
    {
        if (card is CustomCardModel custom && custom.CustomPortrait != null)
        {
            return custom.CustomPortrait;
        }

        return card.HasPortrait ? card.Portrait : null;
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
        var player = TryGetMe(KurageMemory.Combat);
        var creature = player?.Creature;
        if (player == null || !KurageMemory.IsLive(creature)) return;

        var queue = KurageMemory.Queue(player);
        if (queue.Count == 0) return;         // nothing to show; do not open

        var pile = new CardPile(PileType.None);
        var states = KurageMemory.Affordability(
            queue, KokomiResources.GetCharge(creature));

        var projection = new Dictionary<CardModel, KurageMemory.EntryState>();
        // `EB-248`: the price sentence beside the state, built from the SAME
        // entry in the same pass, so the band and the ring cannot describe
        // different memories.
        var prices = new Dictionary<CardModel, string>();
        for (var i = 0; i < queue.Count; i++)
        {
            pile.AddInternal(queue[i].Card);
            // Identity, not id: an Entry holds the live CardModel instance
            // deliberately, so the same instance is what the grid renders.
            projection[queue[i].Card] = states[i];
            prices[queue[i].Card] = KurageMemory.PriceText(
                queue[i].Cost, queue[i].Price);
        }

        KurageMemoryPileRing.Arm(pile, projection, prices);
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
///
/// EB-201: WHY THE FIRST CUT DREW NOTHING, off the decompile rather than a
/// guess. The HOOK was never the problem. `NCardGrid.InitGrid` builds each
/// entry with `NCard.Create` / `NGridCardHolder.Create`, adds the holder to the
/// live scroll container and then calls `nCard.UpdateVisuals(_pileType, ...)`,
/// which calls `UpdateStarCostVisuals` unconditionally -- so this postfix runs
/// once per grid card by construction, and the scrolled-window reuse path
/// (`NCardHolder.ReassignToCard`) calls the same `UpdateVisuals` again.
///
/// The GEOMETRY was. An `NCard` is a `Control` whose own rect is NOT the card:
/// `NCardHolder.ConnectSignals` pins `CardNode.Position = Vector2.Zero` and
/// `NCardGrid.UpdateGridPositions` places each holder at the CELL CENTRE, so
/// the face is drawn centred on the node's origin -- and `NCard.GetCurrentSize`
/// returns the CONSTANT `defaultSize * Scale` rather than reading `Size`,
/// carrying the base game's own warning that you want the HOLDER's size
/// instead. A `FullRect` anchor preset therefore sized this ring to the card
/// node's empty rect: a 0x0 Panel, correctly parented, correctly coloured, and
/// zero pixels wide. No error, no exception, no ring -- exactly the frame
/// sec.14.10 captured.
///
/// So the ring now takes its rect from `NCard.defaultSize`, the game's own
/// constant, centred on the origin the holder pins the node to, and is moved to
/// last child so it draws over the face rather than under it. Both halves are
/// the same class of fix -- a rect and a draw order -- and neither re-points
/// the hook.
/// </summary>
/// <summary>
/// The pile view's one sentence, ALONE IN ITS OWN TYPE, and the reason is the
/// headless boundary rather than tidiness.
///
/// A test that reads a `static readonly` field runs the declaring type's
/// STATIC CONSTRUCTOR, and <see cref="KurageMemoryPileRing"/>'s builds a Godot
/// `StringName` -- the same trap <see cref="KurageMemoryCard.RectFor"/> is
/// split out for, and it does not throw, it takes the test HOST down mid-run:
/// the suite reported 90, 117 and 180 of 271 passing on three consecutive
/// invocations with nothing failing. So the sentence lives where reading it
/// initializes nothing but a string.
///
/// THE RATE IS INTERPOLATED, never typed. `lint_prose_constants` reads a
/// hand-typed 1 beside the words "charge" and "exhaust" as
/// `ChargePerExhaust`'s value spelled a second time, and it is right: a rate
/// retune must not leave the one sentence that explains the funnel saying the
/// old number. The RENDERED text is R224's, character for character.
/// </summary>
internal static class KurageMemoryText
{
    /// <summary>R224 item 7's sentence, and nothing added to it
    /// (review/ruled/sitting-2026-08-30.md, item 7).</summary>
    internal static readonly string ChargeSource =
        $"Gain {KokomiConstants.ChargePerExhaust} Charge when a card of "
      + "yours Exhausts";
}

internal static class KurageMemoryPileRing
{
    private const string RingName = "KleeKurageQueueRing";

    private const int RingWidth = 8;

    // ------------------------------------------ the price on the card --

    /// <summary>
    /// `EB-248`. THE PRICE, AND THE COST IT WAS MULTIPLIED FROM, on each card
    /// in the view.
    ///
    /// The ring says whether the bank reaches this entry; it never said what
    /// the entry costs, and the card underneath prints its OWN face -- which,
    /// for a Muster recruit, is not the face the rule priced. So the queue
    /// showed a two and charged a three with nothing on screen joining them,
    /// and `KURAGECAD-W1`'s tester said so unprompted. This band is the join,
    /// and it is <see cref="KurageMemory.PriceText"/>'s sentence, the same one
    /// the strip and the blind page carry.
    ///
    /// IT GOES HERE AND NOT ON THE HUD. §14.3's division of labour is that the
    /// resting element answers "does the next one fire" and the pile answers
    /// "how far do I get"; [USER] dropped the parenthesised spend from under
    /// the HUD badge on exactly that ground, so the derivation lives on the
    /// surface the player opened on purpose, beside every entry rather than
    /// only the front.
    /// </summary>
    private const string PriceName = "KleeKurageQueuePrice";

    private const int PriceFontSize = 26;

    /// <summary>The band's height, in the card's own coordinates.</summary>
    private const float PriceHeight = 36f;

    /// <summary>How far the band sits above the bottom edge of the card face,
    /// clear of the card's own cost star and its frame.</summary>
    private const float PriceInset = 12f;

    // ------------------------------------------- the head of the view --

    /// <summary>
    /// `EB-214` / R224 item 7 (`M55` re-scoped). WHERE THE CHARGE-SOURCE LINE
    /// GOES, and it is here because everywhere else was retired: the blind
    /// run's `P4` half (b) said the Charge sources are not discoverable from
    /// the page, `M55`'s printed option aimed the sentence at the persistent
    /// display's LIST, and `M61` option 3 had already cut that display to one
    /// card, one ring, one number. There is no bar and no always-on list to
    /// hold a sentence, so the line goes at the head of the click-through pile
    /// view -- the only text-bearing memory surface left. "Stir" is NOT built.
    ///
    /// The wording is R224's, verbatim (review/ruled/sitting-2026-08-30.md,
    /// item 7), and it is a rules sentence rather than a live read: the bank
    /// itself is on the HUD, and repeating it here would be the division of
    /// labour §14.3 exists to keep.
    /// </summary>
    private const string HeaderName = "KleeKurageQueueHeader";

    private const int HeaderFontSize = 30;

    /// <summary>Screen-space, in the game's 1920x1080 design resolution: above
    /// the grid, below the screen's own title band.</summary>
    private const float HeaderTop = 22f;

    private const float HeaderHeight = 40f;

    /// <summary>Godot's theme entry for a `Panel`'s stylebox; see the twin note
    /// on <see cref="KurageMemoryCard"/>.</summary>
    private static readonly StringName PanelStyleBox = "panel";

    private static CardPile? _pile;

    private static Dictionary<CardModel, KurageMemory.EntryState> _projection
        = new();

    /// <summary>`EB-248`: each entry's price sentence, keyed by the same live
    /// instance the projection is. Built at <see cref="Arm"/> from the queue
    /// itself, never re-derived here -- the same posture the ring takes toward
    /// <see cref="KurageMemory.Affordability"/>.</summary>
    private static Dictionary<CardModel, string> _prices = new();

    /// <summary>Entries painted since the last <see cref="Arm"/>, so one line
    /// of live evidence says whether the hook reached the grid at all. This is
    /// the reading EB-201 had to deploy twice to get.</summary>
    private static readonly HashSet<string> _painted = new();

    private static bool _reported;

    /// <summary>The pile we opened, so `_ExitTree` can tell it from any
    /// other.</summary>
    internal static CardPile? OpenPile => _pile;

    /// <summary>
    /// The ring's rect in the card node's own coordinates: the card face, from
    /// the base game's constant, CENTRED on the origin -- see the EB-201 note
    /// on the class for why it cannot be an anchor preset. Pure, so the one
    /// thing about this element a headless test can reach is the thing that
    /// was wrong.
    /// </summary>
    internal static Rect2 RingRect() => RectFor(NCard.defaultSize);

    /// <summary>The centring arithmetic, split out from the constant it reads
    /// so a headless test can assert the VALUE. Touching `NCard` at all is not
    /// headless: its static constructor builds `StringName`s and takes the
    /// process down outside the engine, which is why the split exists.</summary>
    internal static Rect2 RectFor(Vector2 cardSize)
        => new Rect2(-cardSize * 0.5f, cardSize);

    /// <summary>`EB-248`: the price band's rect, IN THE RING'S OWN
    /// COORDINATES -- the band is a child of the ring, so it inherits the
    /// ring's placement and its visibility and cannot be left painted on a
    /// pooled card the ring has already released.</summary>
    internal static Rect2 PriceRect() => PriceRectFor(NCard.defaultSize);

    /// <summary>Split from the constant it reads for the same headless reason
    /// <see cref="RectFor"/> is: a test may assert the VALUE without touching
    /// `NCard`.</summary>
    internal static Rect2 PriceRectFor(Vector2 cardSize)
        => new Rect2(new Vector2(0f, cardSize.Y - PriceHeight - PriceInset),
                     new Vector2(cardSize.X, PriceHeight));

    internal static void Arm(
        CardPile pile,
        Dictionary<CardModel, KurageMemory.EntryState> projection,
        Dictionary<CardModel, string> prices)
    {
        _pile = pile;
        _projection = projection;
        _prices = prices;
        _painted.Clear();
        _reported = false;
    }

    /// <summary>
    /// Print the Charge-source line at the head of OUR pile view.
    ///
    /// Called from an `NCardPileScreen._Ready` postfix. Three guards, and they
    /// are the `EB-225` rules rather than caution: the screen must be the one
    /// we armed (so the game's own draw/discard/exhaust viewers are untouched),
    /// the seat is resolved through <see cref="KurageMemoryCard.TryGetMe"/>
    /// (which cannot throw on a combat with no local seat), and the seat must
    /// be KOKOMI's -- one `PROTOTYPE_CARDS` switch also compiles Klee's Sparks,
    /// and a header that ran on a Klee seat would be exactly the cross-arm
    /// shape `EB-194` and `EB-221` were.
    ///
    /// Idempotent by node name: `_Ready` runs once per screen, but a rebuilt
    /// screen reusing the node must not stack two labels.
    /// </summary>
    internal static void Header(NCardPileScreen screen)
    {
        if (_pile == null || !ReferenceEquals(screen.Pile, _pile)) return;

        var me = KurageMemoryCard.TryGetMe(KurageMemory.Combat);
        if (me == null || !KokomiResources.IsKokomi(me.Creature)) return;
        if (screen.GetNodeOrNull<Label>(HeaderName) != null) return;

        var line = new Label
        {
            Name = HeaderName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            HorizontalAlignment = HorizontalAlignment.Center,
            AnchorLeft = 0f,
            AnchorRight = 1f,
            AnchorTop = 0f,
            AnchorBottom = 0f,
            OffsetTop = HeaderTop,
            OffsetBottom = HeaderTop + HeaderHeight,
            Text = KurageMemoryText.ChargeSource,
        };
        line.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                      HeaderFontSize);
        line.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                   StsColors.cream);
        screen.AddChildSafely(line);

        Log.Info($"[{KleeMod.ModId}] kurage pile header: "
               + $"\"{KurageMemoryText.ChargeSource}\".");
    }

    internal static void Disarm()
    {
        _pile = null;
        _projection = new Dictionary<CardModel, KurageMemory.EntryState>();
        _prices = new Dictionary<CardModel, string>();
        _painted.Clear();
        _reported = false;
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

        // EB-225 / R225 item 6: the CHARACTER SCOPE, spelled here rather than
        // inherited from the arming point. The projection is only ever filled
        // by `OpenQueue`, which is Kokomi-gated, so this was true INDIRECTLY
        // -- and indirect is precisely the shape `EB-207` had to correct one
        // level up: one arming door holding the rule for every reader of it.
        // Under a single `PROTOTYPE_CARDS` switch a stale projection left by
        // a previous combat is a Kokomi element painted on a Klee card, and
        // this is one dictionary hit past the early return above, so it costs
        // nothing on the frames that are not ours.
        if (!KurageMemory.IsLive(
                KurageMemoryCard.TryGetMe(KurageMemory.Combat)?.Creature))
        {
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
        }

        // The rect, every paint rather than only on creation: a pooled `NCard`
        // reaches us with whatever the last screen left on it.
        // No anchor preset at all: a `Control` is created with its anchors at
        // zero, so Position and Size ARE the rect and nothing recomputes them
        // against a parent whose own rect is empty. That recompute is the bug.
        var rect = RingRect();
        ring.Position = rect.Position;
        ring.Size = rect.Size;

        // Draw order. The face lives in `%CardContainer`, an earlier child, so
        // last child is over it -- the same idiom `NCard.ActivateRewardScreenGlow`
        // uses in the other direction to put a glow UNDER the frame.
        if (ring.GetParent() == nCard)
        {
            nCard.MoveChildSafely(ring, nCard.GetChildCount() - 1);
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

        PaintPrice(ring, card);
        Report(card);
    }

    /// <summary>
    /// `EB-248`: the price band on one card, built on first sight and
    /// re-texted every paint -- a pooled `NCard` arrives carrying whatever the
    /// last screen left on it, which is the same reason the ring's rect is set
    /// every paint rather than only on creation.
    ///
    /// A card with no price on the map keeps a HIDDEN band rather than a stale
    /// one. That state is not reachable today -- <see cref="Arm"/> fills both
    /// maps from the same queue in the same loop -- and it is written anyway,
    /// because "not reachable" is what the ring assumed before EB-201.
    /// </summary>
    private static void PaintPrice(Panel ring, CardModel card)
    {
        var band = ring.GetNodeOrNull<Panel>(PriceName);
        if (band == null)
        {
            band = new Panel
            {
                Name = PriceName,
                MouseFilter = Control.MouseFilterEnum.Ignore,
            };
            var label = new Label
            {
                Name = "Text",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            };
            label.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                           PriceFontSize);
            label.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                        StsColors.cream);
            band.AddChildSafely(label);
            ring.AddChildSafely(band);
        }

        var text = band.GetNodeOrNull<Label>("Text");
        if (text == null) return;

        if (!_prices.TryGetValue(card, out var price))
        {
            band.Visible = false;
            return;
        }

        var rect = PriceRect();
        band.Position = rect.Position;
        band.Size = rect.Size;
        text.Position = Vector2.Zero;
        text.Size = rect.Size;

        var backing = new StyleBoxFlat { BgColor = StsColors.transparentBlack };
        backing.SetCornerRadiusAll(6);
        band.AddThemeStyleboxOverride(PanelStyleBox, backing);

        text.Text = price;
        band.Visible = true;
    }

    /// <summary>One INFO line per pile open, once the whole projection has been
    /// reached. It is the evidence, not decoration: a silent log is a hook that
    /// did not run, and that is the distinction EB-201 could not make from a
    /// frame.</summary>
    private static void Report(CardModel card)
    {
        _painted.Add(card.Id.ToString() + "#" + card.GetHashCode());
        if (_reported || _painted.Count < _projection.Count) return;

        _reported = true;
        Log.Info($"[{KleeMod.ModId}] kurage pile ring: painted "
               + $"{_painted.Count} of {_projection.Count} entries at "
               + $"{RingRect().Size.X}x{RingRect().Size.Y}.");
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
/// `EB-214`: the Charge-source line, at the head of the view, the first frame
/// the screen is ready. `_Ready` rather than `ShowScreen` because the node tree
/// does not exist until then, and the label needs a parent.
/// </summary>
[HarmonyPatch(typeof(NCardPileScreen), nameof(NCardPileScreen._Ready))]
internal static class NCardPileScreen_Ready_KurageQueueHeader_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCardPileScreen __instance)
        => KurageMemoryPileRing.Header(__instance);
}

/// <summary>
/// Disarm when the viewer leaves the tree. `_ExitTree` rather than
/// `AfterCapstoneClosed` because it fires on every removal path, including the
/// ones a capstone close does not run.
///
/// THE ONE EXEMPT PATCH ON THIS SURFACE (EB-225). It reads no run, no combat
/// and no seat: its whole body compares the screen that is leaving against a
/// static field this file set, and clears static fields. A character test
/// here would be a test of somebody ELSE's identity -- whoever happens to
/// hold a seat while a pile screen closes -- and would leave a stale
/// projection armed on the frame it answered no, which is the defect the
/// scope rule exists to prevent rather than an instance of obeying it.
/// </summary>
// lint: no-seat: pure static teardown of this file's own fields -- it reads
// neither a run nor a seat, and a character test here would leave the ring
// armed on the frame it answered no.
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
