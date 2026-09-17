using System;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// THE SPARK BANK IN THE ENERGY AREA (`EB-621`).
///
/// THE FIND. [USER]'s own Klee act-1 run on `0.2.2888+proto`: "Sparks show
/// only as a buff icon and need a resource badge of their own, like Regent's
/// Stars, beside Energy, so the bank is read where the price is paid."
///
/// WHAT THIS IS NOT. It is not a second reading of `EB-281`. That row moved
/// the bank OFF the status strip and onto an OVERHEAD gauge on Klee's own
/// creature (<see cref="SparkGauge"/>, the `klee_spark` spec in
/// <see cref="GaugeBridge"/>), which is where a Burst meter goes. The finding
/// here is about WHERE THE EYE IS: a price is paid at the bottom-left corner,
/// beside the energy orb, and that is where the base game puts a resource that
/// buys cards. The overhead gauge and the badge both stay; nothing is removed
/// by this file, exactly as the row says ("the buff icon may stay").
///
/// WHAT THE BASE GAME ACTUALLY DOES, read off the pinned v0.111.0 assembly
/// (`docs/current/research/regent-stars-economy.md` §5.2, and the type itself
/// decompiled again for this build):
///
///   - <c>Nodes.Combat/NStarCounter.cs</c> is a plain <c>Control</c> sitting in
///     the combat UI scene under the unique name <c>%StarCounter</c>. It is in
///     EVERY character's combat scene; what differs per character is whether it
///     is shown.
///   - <c>NCombatUi._Ready</c> binds it (<c>GetNode&lt;NStarCounter&gt;
///     ("%StarCounter")</c>) beside <c>%EnergyCounterContainer</c>.
///   - <c>NCombatUi.Activate</c> calls <c>_starCounter.Initialize(me)</c> and
///     then, <b>only</b> when <c>me.Character.ShouldAlwaysShowStarCounter</c>,
///     MOVES THE ENERGY ORB OUT OF ITS WAY:
///     <c>EnergyCounterContainer.SetPosition(new Vector2(100f, 806f),
///     keepOffsets: true)</c>. The energy counter is created and parented after
///     that line, and then -- <b>unconditionally, for every character</b> --
///     <c>_starCounter.Reparent(_energyCounter)</c>. THAT LAST LINE IS WHAT
///     `EB-815` IS ABOUT; see below.
///   - The counter itself is a glyph with a number centred on it. It subscribes
///     to <c>PlayerCombatState.StarsChanged</c> -- no polling -- and
///     <c>SetStarCountText</c> paints the number <c>StsColors.red</c> at zero
///     and <c>StsColors.cream</c> otherwise. <c>RefreshVisibility</c> keeps it
///     on screen from turn one for a character that always shows it, even at 0.
///
/// `EB-815`: WHY THE FIRST READING OF THAT LIST DREW THE BADGE ON THE ORB.
/// The original build of this file mirrored <c>%StarCounter</c> by copying its
/// four anchor/offset pairs and parenting into <c>star.GetParent()</c>, then
/// applied the orb displacement above as its anti-overlap measure. Both halves
/// are defeated by <c>Reparent</c>, which has already run by the time this
/// file's <c>Activate</c> POSTFIX does:
///
///   1. <c>star.GetParent()</c> is <c>_energyCounter</c> -- the orb node ITSELF
///      -- so the badge was added INSIDE the energy counter's subtree, and the
///      offsets it copied were relative to the orb's own rect. It landed on the
///      orb by construction.
///   2. The displacement was therefore INERT. Moving
///      <c>EnergyCounterContainer</c> translates every descendant, the badge
///      included, by the same vector; the orb-to-badge delta never changed. It
///      was self-cancelling at every window size, which is why the overlap was
///      scale-INDEPENDENT rather than a scale or aspect bug.
///
/// SO THE MIRROR IS NOW OF THE ENERGY PANEL'S RECT, not of the star counter's
/// box. <see cref="Place"/> puts the badge ABOVE <c>%EnergyCounterContainer</c>
/// with <see cref="PanelMargin"/> clear of its top edge, and
/// <see cref="Apply"/> hangs it off the panel's own PARENT -- a SIBLING of the
/// panel, never a descendant -- carrying the panel's anchor pair. Sharing the
/// anchors is what makes it survive a resize with no <c>_Process</c> and no
/// resize hook: any viewport change moves panel and badge by the same vector,
/// so the margin holds in the panel's own units. A pixel constant would be a
/// guess about a scene we do not ship; the panel node is the fact. The star
/// counter is still read, but only for its SIZE (<see cref="Build"/>), which is
/// the one thing about it the reparent does not make a lie.
///
/// ABOVE RATHER THAN BESIDE, and that is a reading of the frame rather than a
/// preference: at the bottom-left corner the space to the RIGHT of the orb is
/// where the creature's own health bar runs, and the space above it is empty
/// under every act dressing. The right of the panel is kept as the FALLBACK for
/// a viewport with no room above, and both candidates are held inside the
/// viewport.
///
/// THE DISPLACEMENT IS GONE, not repaired. With the badge out of the orb's
/// subtree, moving the shipped energy orb for Klee would be a real eviction
/// that nothing asked for -- the badge no longer needs the room.
/// <see cref="EnergyCounterOffset"/> survives as the FALLBACK rect alone, for
/// the case where the panel cannot be resolved at all.
///
/// WHY NOT SIMPLY SHOW THE GAME'S STAR COUNTER. Because it would lie. Its
/// glyph is a star, its hover tip is <c>STAR_COUNT.description</c>, and the
/// number it reads is <c>PlayerCombatState.Stars</c> -- a resource Klee neither
/// gains nor spends. Feeding Sparks into that field to borrow the widget would
/// put a second, forkable copy of the bank on the player object. The bank stays
/// exactly where it is (<see cref="SparkPower"/>'s stack); this draws it.
///
/// THE FEED IS THE FUNNEL THAT ALREADY EXISTS. <c>SparkPower.SyncGauge</c>
/// fires on every mutation of the bank -- the gains, the spends and the
/// <c>AfterPowerAmountChanged</c> net for a bank moved by something that is not
/// this mod -- and calls <see cref="SparkGauge.Refresh"/>, which now calls
/// <see cref="Refresh"/>. One funnel, so the badge, the overhead gauge and the
/// `spark` meter ledger cannot come from different reads. There is no
/// <c>_Process</c> anywhere in this file.
///
/// KLEE'S SEAT, UNDER THE ARM, AND NOBODY ELSE'S. The scope is
/// <see cref="SparkGauge.AppliesTo"/> verbatim -- one predicate for the gauge
/// and the badge rather than two that can drift -- which is
/// <c>KleeOverhaul.Enabled &amp;&amp; character is IKleeCharacter</c>. And the
/// element is built for the LOCAL seat only: a co-op partner's screen is their
/// own energy area and must not gain Klee's bank.
///
/// WHAT NOTHING HEADLESS CAN ANSWER. Whether the badge lands where the star
/// counter lands, and whether the displaced energy orb reads well beside it.
/// Godot nodes cannot be built in the test host (KleeTests README, the
/// headless boundary), so the pins below are the DECISIONS -- the scope, the
/// number, the funnel, the geometry source and the arm gate. The look is a
/// frame on the next `+proto` deploy.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class SparkCounter
{
    /// <summary>The node this file owns, and the handle its teardown uses.</summary>
    internal const string RootName = "KleeModSparkCounter";

    /// <summary>
    /// The base game's own displacement of the energy orb when a star counter
    /// shares its corner (<c>NCombatUi.Activate</c>, v0.111.0). Copied as a
    /// literal because it IS a literal there.
    ///
    /// `EB-815`: THIS IS NOW A FALLBACK ANCHOR AND NOTHING ELSE. The file no
    /// longer applies the displacement -- see the class docstring for why it
    /// was inert and why the badge no longer needs the room. The number stays
    /// because it is still the best guess at where the energy corner IS when
    /// <c>%EnergyCounterContainer</c> cannot be resolved at all.
    /// </summary>
    internal static readonly Vector2 EnergyCounterOffset = new(100f, 806f);

    /// <summary>
    /// The gap the badge keeps from the energy panel, IN THE PANEL'S OWN UNITS
    /// (the game's 1920x1080 design resolution, which is the space the panel's
    /// offsets are already in). Not a screen offset: <see cref="Apply"/> adds
    /// it to the panel's own edge, so it is a margin rather than a position.
    /// </summary>
    internal const float PanelMargin = 12f;

    /// <summary>Fallback square when <c>%StarCounter</c> reports no size yet.
    /// Used for the CHILDREN only; the root's rect is always the star
    /// counter's own.</summary>
    private const float FallbackSide = 72f;

    private const int CountFontSize = 40;

    /// <summary>One element, one seat, freed through the shared display
    /// skeleton exactly as the gauges and the Kurage card are.</summary>
    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    private static bool _warnedGlyph;

    /// <summary>
    /// Does this seat get the badge? <see cref="SparkGauge.AppliesTo"/> and
    /// nothing else. `EB-281` already settled who owns a Spark display and
    /// spelled the co-op reason at length; a second copy of that predicate here
    /// would be a second thing to keep true.
    /// </summary>
    public static bool AppliesTo(Creature? creature) =>
        creature != null && SparkGauge.AppliesTo(creature);

    /// <summary>The number the badge draws: the bank, right now, through the
    /// same accessor the overhead gauge reads
    /// (<see cref="SparkGauge.Read"/> -> <see cref="SparkPower.SparksAtPlay"/>).
    /// The two displays are one read.</summary>
    public static int Read(Creature creature) => SparkGauge.Read(creature);

    /// <summary>
    /// Build the badge for the LOCAL seat. Called from the
    /// <c>NCombatUi.Activate</c> postfix `GaugeBridge` already installs, so
    /// there is one combat-lifecycle entry point rather than a fourth that can
    /// disagree about when a room is live.
    /// </summary>
    public static void Setup(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !AppliesTo(me.Creature)) return;
        if (NCombatRoom.Instance?.Ui is not { } ui) return;

        // `%StarCounter` is in every character's combat scene -- Regent is the
        // only one that SHOWS it -- so this resolves for Klee too. It is read
        // for its SIZE alone: `NCombatUi.Activate` has already reparented it
        // INTO the energy orb, so its anchors and offsets describe a box inside
        // the orb and copying them is what drew the badge on the orb (`EB-815`).
        var star = ui.GetNodeOrNull<Control>("%StarCounter");

        // THE PANEL IS THE FACT WE MIRROR, and the badge is its SIBLING rather
        // than its descendant -- that is the whole of the fix. A descendant
        // rides every move of the panel, which is what made the old
        // displacement self-cancelling.
        var panel = ui.EnergyCounterContainer;
        var parent = panel?.GetParent() ?? (Node)ui;

        Displays.Discard(me);
        var side = SideOf(star);
        var root = Build(side);
        parent.AddChildSafely(root);
        Displays.Set(me, root);

        Apply(root, panel, side, ui.GetViewportRect().Size);

        Paint(root, me.Creature);
    }

    /// <summary>
    /// Re-read the bank and redraw. Driven by <see cref="SparkGauge.Refresh"/>,
    /// i.e. by <c>SparkPower</c>'s own mutation funnels -- no polling.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (player == null || !LocalContext.IsMe(player)) return;
        if (!AppliesTo(creature)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            // Stale or never built (a mid-combat reload): rebuild in place,
            // the reference-bridge idiom `GaugeBridge.Refresh` uses.
            Setup(creature!.CombatState as CombatState);
            root = Displays.Get(player);
            if (root == null) return;
        }

        Paint(root, creature!);
    }

    /// <summary>
    /// The local seat, or null when the combat cannot name one.
    ///
    /// `LocalContext.GetMe` THROWS for "not in this combat" rather than
    /// answering null -- the catch `KurageMemoryCard.TryGetMe` records at
    /// length, which ended two whole-fight blind sessions. Same guard here,
    /// in this file, because the scope lint reads a patch's SAME-FILE closure.
    /// </summary>
    private static Player? TryGetMe(CombatState? state)
    {
        if (state == null) return null;
        try
        {
            return LocalContext.GetMe(state);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] spark counter: no local seat in this "
                   + $"combat ({e.GetType().Name}: {e.Message}); drawing "
                   + "nothing.");
            return null;
        }
    }

    // ----------------------------------------------------------- drawing --

    /// <summary>
    /// THE BADGE'S SIZE, and the one thing still taken from
    /// <c>%StarCounter</c>. Its POSITION is a lie under the reparent (see the
    /// class docstring) but its size is the base game's own answer to "how big
    /// is a resource badge in this corner", which is a question we should not
    /// re-answer. A star counter that has not been laid out yet reports no
    /// size, and then the fallback square stands in.
    ///
    /// Square by construction: the glyph is square and the count is centred on
    /// it, so one number is the whole box and <see cref="Place"/> takes a
    /// scalar rather than a vector.
    /// </summary>
    private static float SideOf(Control? star) =>
        star != null && star.Size.X > 0f && star.Size.Y > 0f
            ? Mathf.Min(star.Size.X, star.Size.Y)
            : FallbackSide;

    /// <summary>
    /// WHERE THE BADGE GOES, as a pure function of the energy panel's rect, the
    /// badge's side and the viewport -- no nodes, so it is the half of this file
    /// the headless suite can actually hold (`EB-815`,
    /// <c>SparkCounterPinTests</c>). The old geometry was pinned as SOURCE TEXT,
    /// which is why a placement defect could sit under a green suite: a test
    /// that asserts a line of code exists cannot fail on where a box lands.
    ///
    /// ABOVE the panel, left edges aligned, <see cref="PanelMargin"/> clear of
    /// its top edge. If there is no room above -- a viewport shorter than the
    /// panel's own top margin -- it falls to the RIGHT of the panel, vertically
    /// centred on it. Both candidates are then held inside the viewport.
    ///
    /// Everything here is in the panel's own coordinate space, which is the
    /// space its parent lays out in; the combat UI root spans the viewport, so
    /// the containment check below is in the same units the viewport is.
    /// </summary>
    internal static Rect2 Place(Rect2 energy, float side, Vector2 viewport)
    {
        var box = new Vector2(side, side);

        var above = new Vector2(energy.Position.X,
                                energy.Position.Y - PanelMargin - side);
        if (above.Y >= 0f)
        {
            return new Rect2(Hold(above, side, viewport), box);
        }

        var right = new Vector2(energy.End.X + PanelMargin,
                                energy.Position.Y + (energy.Size.Y - side) / 2f);
        return new Rect2(Hold(right, side, viewport), box);
    }

    /// <summary>
    /// Keep the box on screen WITHOUT ever pushing it back across the panel:
    /// each axis is clamped only where the viewport is actually big enough to
    /// hold the box. A viewport smaller than the badge has no answer that is
    /// both on screen and clear of the panel, and in that case staying clear of
    /// the panel is the one that matters -- an unreadable number in the corner
    /// beats a readable one painted over the energy cost.
    /// </summary>
    private static Vector2 Hold(Vector2 at, float side, Vector2 viewport) =>
        new(viewport.X > side ? Mathf.Clamp(at.X, 0f, viewport.X - side) : at.X,
            viewport.Y > side ? Mathf.Clamp(at.Y, 0f, viewport.Y - side) : at.Y);

    /// <summary>
    /// Put <see cref="Place"/>'s answer on the node, IN THE PANEL'S OWN ANCHOR
    /// SPACE. The badge takes the panel's anchor pair and the panel's offsets
    /// shifted by the placement delta, so the two are pinned to the same corner
    /// of the viewport and a resize moves them by one vector. That is what makes
    /// the margin hold at every window size with no <c>_Process</c> and no
    /// resize hook -- and it is why the badge must be the panel's SIBLING: a
    /// descendant would take the panel's motion TWICE.
    ///
    /// With no panel to read there is nothing to be relative TO, and the corner
    /// literal is the honest guess rather than nothing on screen.
    /// </summary>
    private static void Apply(
        Control root, Control? panel, float side, Vector2 viewport)
    {
        if (panel == null)
        {
            var guess = Place(
                new Rect2(EnergyCounterOffset, new Vector2(side, side)),
                side, viewport);
            root.AnchorLeft = 0f;
            root.AnchorTop = 0f;
            root.AnchorRight = 0f;
            root.AnchorBottom = 0f;
            root.OffsetLeft = guess.Position.X;
            root.OffsetTop = guess.Position.Y;
            root.OffsetRight = guess.End.X;
            root.OffsetBottom = guess.End.Y;
            return;
        }

        var rect = new Rect2(panel.Position, panel.Size);
        var delta = Place(rect, side, viewport).Position - rect.Position;

        root.AnchorLeft = panel.AnchorLeft;
        root.AnchorRight = panel.AnchorLeft;
        root.AnchorTop = panel.AnchorTop;
        root.AnchorBottom = panel.AnchorTop;
        root.OffsetLeft = panel.OffsetLeft + delta.X;
        root.OffsetTop = panel.OffsetTop + delta.Y;
        root.OffsetRight = root.OffsetLeft + side;
        root.OffsetBottom = root.OffsetTop + side;
    }

    /// <summary>
    /// The node tree: a glyph with the count centred on it, in a square of
    /// <paramref name="squareSide"/>. The GEOMETRY is <see cref="Apply"/>'s, so
    /// the placement rule lives in one pure function rather than half here and
    /// half at the call site.
    /// </summary>
    private static Control Build(float squareSide)
    {
        var root = new Control
        {
            Name = RootName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            // `EB-300`: display only, never in the controller's focus graph.
            FocusMode = Control.FocusModeEnum.None,
        };

        var side = new Vector2(squareSide, squareSide);

        var icon = new TextureRect
        {
            Name = "Icon",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            Position = Vector2.Zero,
            Size = side,
        };
        root.AddChildSafely(icon);

        // Centred ON the glyph, which is the star counter's own arrangement
        // (`%CountLabel` sits over `Icon`, not beside it).
        var count = new Label
        {
            Name = "Count",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            Position = Vector2.Zero,
            Size = side,
        };
        count.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       CountFontSize);
        root.AddChildSafely(count);

        root.SetFocusBehaviorRecursive(
            Control.FocusBehaviorRecursiveEnum.Disabled);
        return root;
    }

    /// <summary>
    /// Draw the bank.
    ///
    /// ZERO IS DRAWN, NOT HIDDEN. That is <c>ShouldAlwaysShowStarCounter</c>'s
    /// posture and the reason it exists: a resource a whole kit is priced
    /// against has to be on screen from turn one, or the player learns it is
    /// there only once they already have some. The colour at zero is
    /// <c>StsColors.red</c> and otherwise <c>StsColors.cream</c>, which is
    /// <c>NStarCounter.SetStarCountText</c>'s own pair.
    /// </summary>
    private static void Paint(Control root, Creature? creature)
    {
        if (creature == null || !GodotObject.IsInstanceValid(root)) return;

        var sparks = Read(creature);

        if (root.GetNodeOrNull<Label>("Count") is { } count)
        {
            count.Text = sparks.ToString();
            count.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                sparks == 0 ? StsColors.red : StsColors.cream);
        }

        if (root.GetNodeOrNull<TextureRect>("Icon") is { } icon)
        {
            SetGlyph(icon);
        }
    }

    /// <summary>
    /// The Spark glyph, RESOLVED FRESH ON EVERY PAINT and never held across a
    /// scene. `EB-222`: the engine preloads a room's assets and frees them with
    /// the room, so a cached <c>Texture2D</c> becomes a corpse the next combat
    /// hands to <c>TextureRect.SetTexture</c> -- which is how a stuck room and
    /// a dead run happened once already. <see cref="MeterCostBadge"/> carries
    /// the full account; this is the same rule, and the same promise that the
    /// visual layer never throws at its caller.
    /// </summary>
    private static void SetGlyph(TextureRect icon)
    {
        try
        {
            var path = KleePck.Path(SparkGauge.GlyphPath);
            var texture = path == null
                ? null
                : ResourceLoader.Load<Texture2D>(path);

            if (texture == null || !GodotObject.IsInstanceValid(texture))
            {
                if (!_warnedGlyph)
                {
                    _warnedGlyph = true;
                    Log.Warn($"[{KleeMod.ModId}] spark counter: no live "
                           + $"{SparkGauge.GlyphPath}; drawing the number "
                           + "with no glyph.");
                }
                icon.Visible = false;
                return;
            }

            icon.Texture = texture;
            icon.Visible = true;
        }
        catch (Exception e)
        {
            // The number is the half of the display the bank actually lives
            // in. Losing the glyph is noise; throwing here would be a run.
            if (!_warnedGlyph)
            {
                _warnedGlyph = true;
                Log.Warn($"[{KleeMod.ModId}] spark counter: the glyph could "
                       + $"not be drawn ({e.GetType().Name}: {e.Message}); "
                       + "drawing the number alone.");
            }
        }
    }

    /// <summary>
    /// Free the badge when the combat UI stands down.
    ///
    /// BY NODE, NOT BY SEAT, and that is the whole reason this signature takes
    /// no state. `NCombatUi.Deactivate` runs while the NEXT room is being built
    /// and the combat we still hold may have no seats in it -- the shape that
    /// ended two blind sessions (`EB-225`). A teardown that has to name a seat
    /// to free its own node is a teardown that can throw out of `_Ready`. This
    /// one asks the UI for a child THIS mod named and frees it; the registry's
    /// <c>IsInstanceValid</c> staleness then answers null for it, and
    /// <see cref="Setup"/> discards anything left over at the next combat.
    /// </summary>
    internal static void Hide(NCombatUi? ui)
    {
        if (ui == null || !GodotObject.IsInstanceValid(ui)) return;
        if (ui.FindChild(RootName, recursive: true, owned: false)
            is { } node && GodotObject.IsInstanceValid(node))
        {
            node.QueueFree();
        }
    }
}

/// <summary>The badge dies with the combat, on the game's own hook -- one
/// teardown per HUD element, the shape every other element in this tree
/// takes.</summary>
// lint: no-seat: pure static teardown. It frees, by name, the one child node
// this file added to the combat UI, and touches no run state, no player and no
// creature -- so there is no seat to resolve and no character to scope to. The
// scope lives at the only door that BUILDS the node (`Setup`, through
// `SparkGauge.AppliesTo`); naming a seat here is exactly what `EB-225` shows a
// teardown must not have to do.
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_KleeSparkCounter_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCombatUi __instance) =>
        SparkCounter.Hide(__instance);
}
