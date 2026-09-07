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
///     that line.
///   - The counter itself is a glyph with a number centred on it. It subscribes
///     to <c>PlayerCombatState.StarsChanged</c> -- no polling -- and
///     <c>SetStarCountText</c> paints the number <c>StsColors.red</c> at zero
///     and <c>StsColors.cream</c> otherwise. <c>RefreshVisibility</c> keeps it
///     on screen from turn one for a character that always shows it, even at 0.
///
/// SO THAT IS WHAT IS MIRRORED, and the mirror is geometric rather than
/// numeric. This does not hard-code where the star counter lives: it reads
/// <c>%StarCounter</c>'s OWN anchors and offsets off the live scene and copies
/// them, then applies the same energy-orb displacement the base game applies.
/// A pixel constant would be a guess about a scene we do not ship; the node is
/// the fact. The only literal taken from the assembly is
/// <see cref="EnergyCounterOffset"/>, which is the game's own line.
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
    /// literal because it IS a literal there -- the one number in this file
    /// that is not read off the live scene.
    /// </summary>
    internal static readonly Vector2 EnergyCounterOffset = new(100f, 806f);

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
        // only one that SHOWS it -- so this resolves for Klee too, and it is
        // the geometry we are mirroring rather than a widget we are borrowing.
        var star = ui.GetNodeOrNull<Control>("%StarCounter");
        var parent = star?.GetParent() ?? (Node)ui;

        Displays.Discard(me);
        var root = Build(star);
        parent.AddChildSafely(root);
        Displays.Set(me, root);

        // The base game's own second half: with a resource counter in the
        // corner, the energy orb moves. Doing only the first half would stack
        // the badge on the orb.
        ui.EnergyCounterContainer?.SetPosition(EnergyCounterOffset,
                                               keepOffsets: true);

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
    /// The node tree: a glyph with the count centred on it, in the star
    /// counter's own rect.
    ///
    /// THE RECT IS COPIED, NOT CHOSEN. Anchors and offsets are what a Godot
    /// Control's position and size actually ARE, so copying those four pairs
    /// reproduces <c>%StarCounter</c>'s box exactly and follows a resize the
    /// same way it does. When the node cannot be found the badge falls back to
    /// the bottom-left corner with the same displacement the energy orb takes,
    /// which is the honest guess rather than nothing on screen.
    /// </summary>
    private static Control Build(Control? star)
    {
        var root = new Control
        {
            Name = RootName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            // `EB-300`: display only, never in the controller's focus graph.
            FocusMode = Control.FocusModeEnum.None,
        };

        if (star != null)
        {
            root.AnchorLeft = star.AnchorLeft;
            root.AnchorTop = star.AnchorTop;
            root.AnchorRight = star.AnchorRight;
            root.AnchorBottom = star.AnchorBottom;
            root.OffsetLeft = star.OffsetLeft;
            root.OffsetTop = star.OffsetTop;
            root.OffsetRight = star.OffsetRight;
            root.OffsetBottom = star.OffsetBottom;
        }
        else
        {
            root.AnchorLeft = 0f;
            root.AnchorTop = 0f;
            root.AnchorRight = 0f;
            root.AnchorBottom = 0f;
            root.OffsetLeft = EnergyCounterOffset.X - FallbackSide;
            root.OffsetTop = EnergyCounterOffset.Y;
            root.OffsetRight = EnergyCounterOffset.X;
            root.OffsetBottom = EnergyCounterOffset.Y + FallbackSide;
        }

        var side = star != null && star.Size.X > 0f && star.Size.Y > 0f
            ? star.Size
            : new Vector2(FallbackSide, FallbackSide);

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
