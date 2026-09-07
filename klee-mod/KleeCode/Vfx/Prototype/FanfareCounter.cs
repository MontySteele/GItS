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
/// FANFARE IN THE ENERGY AREA (`EB-628`), on <see cref="SparkCounter"/>'s
/// pattern and for the same reason one character over.
///
/// THE FIND. [USER]'s own Furina act-1 run under the reframe, 2026-09-07: the
/// Encore and Fanfare displays "need rethinking", and what was overhead was a
/// bar reading "10/70" -- the shipped Burst meter's shape, a value over a
/// ceiling. Under the arm that shape is wrong twice: `EB-365` (R251) already
/// retired the Burst meter here, and Fanfare's own cap is a demoted safety rail
/// (`FurinaResources.FanfareCap`, half her max HP) that F-A5 measured as never
/// binding. A denominator nobody reaches is a number that means nothing, and
/// under the arm the ONE thing Fanfare does is give member numbers +1 per
/// <see cref="SalonConstants.FocusPerFanfare"/>. So the display stops being a
/// fraction of a ceiling and becomes a count with its next step beside it.
///
/// WHY THE ENERGY AREA. Because that is where the eye is when a decision is
/// priced, and it is where the base game puts a character resource: the
/// Regent's `%StarCounter` sits beside `%EnergyCounterContainer`, and
/// `NCombatUi.Activate` moves the orb out of its way. `EB-621` read that
/// geometry off the live scene for Klee's Spark bank; this reuses that
/// reading rather than a second guess at it -- the rect is copied from
/// `%StarCounter`'s own anchors and offsets, and the orb takes the base game's
/// own displacement.
///
/// ONE BADGE IN THAT CORNER, EVER, and that is why this takes the star
/// counter's rect rather than an offset from it. The Spark badge is Klee's
/// under her arm and this is Furina's under hers; the two are different
/// characters and the local seat is one of them, so there is no seat on which
/// both draw and no overlap to offset around. The game makes room for one
/// counter beside the orb; each arm's badge takes it.
///
/// THE THRESHOLD IS THE SECOND LINE, and it is the whole reason the badge is
/// not just a number. "6" tells a player nothing they can act on; "+1 at 10"
/// tells them the member numbers on the strip go up in four. It is computed
/// from <see cref="SalonConstants.FocusPerFanfare"/>, the same constant
/// <see cref="SalonMemberPower.TickValue"/> divides by, so a retune cannot
/// leave the badge quoting a retired step.
///
/// THE FEED IS THE FUNNEL THAT ALREADY EXISTS.
/// <c>FurinaResources.SyncMeters</c> is where the Fanfare badge power, the
/// Spotlight display and the Salon stage are all refreshed; this hangs there
/// too. One funnel, so the badge and the strip cannot come from different
/// reads. There is no <c>_Process</c> anywhere in this file.
///
/// FURINA'S SEAT, UNDER THE METER LEG, AND THE LOCAL SEAT ONLY. The scope is
/// <c>FurinaReframe.MeterLiveFor</c> -- Fanfare's own leg, the one that makes
/// a performance the only thing that mints -- and the element is built for the
/// local seat: a co-op partner's screen is their own energy area.
///
/// WHAT NOTHING HEADLESS CAN ANSWER. Whether the badge lands where the star
/// counter lands and whether the threshold line reads beside it. Godot nodes
/// cannot be built in the test host (KleeTests README, the headless boundary),
/// so the pins below are the DECISIONS. The look is a frame on the next
/// `+proto` deploy.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class FanfareCounter
{
    /// <summary>The node this file owns, and the handle its teardown uses.</summary>
    internal const string RootName = "KleeModFanfareCounter";

    /// <summary>The Fanfare glyph, the one the meter badge already wears
    /// (<c>KleePowerIcons</c>). Same resource, same glyph, wherever it
    /// appears.</summary>
    public const string GlyphPath = "furina/powers/fanfare.png";

    /// <summary>
    /// The base game's own displacement of the energy orb when a resource
    /// counter shares its corner (<c>NCombatUi.Activate</c>, v0.111.0).
    /// <see cref="SparkCounter.EnergyCounterOffset"/> by value -- one literal
    /// read off the assembly, and the badge that moved it first owns it.
    /// </summary>
    internal static readonly Vector2 EnergyCounterOffset =
        SparkCounter.EnergyCounterOffset;

    private const float FallbackSide = 72f;
    private const int CountFontSize = 40;
    private const int StepFontSize = 16;

    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    private static bool _warnedGlyph;

    /// <summary>Does this seat get the badge? Fanfare's own leg, and nothing
    /// else: off the meter leg the shipped four mint legs are live and the
    /// shipped Fanfare badge on the status strip is the honest surface.
    /// </summary>
    public static bool AppliesTo(Creature? creature) =>
        FurinaReframe.MeterLiveFor(creature);

    /// <summary>The number the badge draws, through the accessor every reader
    /// in the kit uses (<c>FurinaResources.ReadableFanfare</c>) -- the same one
    /// <see cref="SalonMemberPower.TickValue"/> divides for the member bonus,
    /// so the badge and the strip cannot disagree.</summary>
    public static int Read(Creature creature) =>
        FurinaResources.ReadableFanfare(creature);

    /// <summary>
    /// The Fanfare at which member numbers go up by one more.
    ///
    /// The NEXT multiple of <see cref="SalonConstants.FocusPerFanfare"/> above
    /// what is held -- strictly above, so a badge sitting exactly on a
    /// threshold points at the next one rather than at itself.
    /// </summary>
    public static int NextThreshold(Creature creature)
    {
        var step = SalonConstants.FocusPerFanfare;
        if (step <= 0) return 0;
        return (Read(creature) / step + 1) * step;
    }

    /// <summary>The line beside the count: what the next step buys and where
    /// it is. Written as the packet writes it.</summary>
    public static string StepText(Creature creature) =>
        $"+1 at {NextThreshold(creature)}";

    /// <summary>
    /// Build the badge for the LOCAL seat. Called from the
    /// <c>NCombatUi.Activate</c> postfix `GaugeBridge` installs, so there is
    /// one combat-lifecycle entry point rather than another that can disagree
    /// about when a room is live.
    /// </summary>
    public static void Setup(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !AppliesTo(me.Creature)) return;
        if (NCombatRoom.Instance?.Ui is not { } ui) return;

        // `%StarCounter` is in every character's combat scene -- Regent is the
        // only one that SHOWS it -- so it resolves for Furina too, and it is
        // the geometry being mirrored rather than a widget being borrowed.
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

    /// <summary>Re-read the meter and redraw. Driven by
    /// <c>FurinaResources.SyncMeters</c> -- the funnel the Fanfare badge power
    /// and the Salon display already ride.</summary>
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
    /// length, which ended two whole-fight blind sessions. Same guard here, in
    /// this file, because the scope lint reads a patch's SAME-FILE closure.
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
            Log.Warn($"[{KleeMod.ModId}] fanfare counter: no local seat in "
                   + $"this combat ({e.GetType().Name}: {e.Message}); drawing "
                   + "nothing.");
            return null;
        }
    }

    // ----------------------------------------------------------- drawing --

    /// <summary>
    /// The node tree: a glyph with the count centred on it and the next
    /// threshold under it.
    ///
    /// THE RECT IS COPIED, NOT CHOSEN -- `EB-621`'s reading verbatim. Anchors
    /// and offsets are what a Godot Control's position and size actually ARE,
    /// so copying those four pairs reproduces `%StarCounter`'s box exactly and
    /// follows a resize the same way it does.
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

        // UNDER the glyph rather than centred on it: the count is the reading
        // and the step is the footnote, and a footnote over a number is two
        // numbers on one glyph.
        var step = new Label
        {
            Name = "Step",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            Position = new Vector2(0f, side.Y),
            Size = new Vector2(side.X, StepFontSize + 4f),
        };
        step.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                      StepFontSize);
        root.AddChildSafely(step);

        root.SetFocusBehaviorRecursive(
            Control.FocusBehaviorRecursiveEnum.Disabled);
        return root;
    }

    /// <summary>
    /// Draw the meter.
    ///
    /// ZERO IS DRAWN, NOT HIDDEN -- `NStarCounter`'s own posture and
    /// `EB-621`'s: a resource the kit's numbers are priced against has to be
    /// on screen from turn one, or the player learns it is there only once
    /// they already have some. The colour at zero is `StsColors.red` and
    /// otherwise `StsColors.cream`, which is `NStarCounter.SetStarCountText`'s
    /// own pair.
    /// </summary>
    private static void Paint(Control root, Creature? creature)
    {
        if (creature == null || !GodotObject.IsInstanceValid(root)) return;

        var fanfare = Read(creature);

        if (root.GetNodeOrNull<Label>("Count") is { } count)
        {
            count.Text = fanfare.ToString();
            count.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                fanfare == 0 ? StsColors.red : StsColors.cream);
        }

        if (root.GetNodeOrNull<Label>("Step") is { } step)
        {
            step.Text = StepText(creature);
            step.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                       StsColors.cream);
        }

        if (root.GetNodeOrNull<TextureRect>("Icon") is { } icon)
        {
            SetGlyph(icon);
        }
    }

    /// <summary>
    /// The Fanfare glyph, RESOLVED FRESH ON EVERY PAINT and never held across
    /// a scene. `EB-222`: the engine preloads a room's assets and frees them
    /// with the room, so a cached <c>Texture2D</c> becomes a corpse the next
    /// combat hands to <c>TextureRect.SetTexture</c>. Losing the glyph is
    /// noise; throwing here would be a run.
    /// </summary>
    private static void SetGlyph(TextureRect icon)
    {
        try
        {
            var path = KleePck.Path(GlyphPath);
            var texture = path == null
                ? null
                : ResourceLoader.Load<Texture2D>(path);

            if (texture == null || !GodotObject.IsInstanceValid(texture))
            {
                if (!_warnedGlyph)
                {
                    _warnedGlyph = true;
                    Log.Warn($"[{KleeMod.ModId}] fanfare counter: no live "
                           + $"{GlyphPath}; drawing the number with no "
                           + "glyph.");
                }
                icon.Visible = false;
                return;
            }

            icon.Texture = texture;
            icon.Visible = true;
        }
        catch (Exception e)
        {
            if (!_warnedGlyph)
            {
                _warnedGlyph = true;
                Log.Warn($"[{KleeMod.ModId}] fanfare counter: the glyph could "
                       + $"not be drawn ({e.GetType().Name}: {e.Message}); "
                       + "drawing the number alone.");
            }
        }
    }

    /// <summary>
    /// Free the badge when the combat UI stands down. BY NODE, NOT BY SEAT --
    /// `EB-225`'s rule and <see cref="SparkCounter.Hide"/>'s reasoning
    /// verbatim: `NCombatUi.Deactivate` runs while the NEXT room is being
    /// built and the combat still held may have no seats in it.
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
/// teardown per HUD element.</summary>
// lint: no-seat: pure static teardown. It frees, by name, the one child node
// this file added to the combat UI, and touches no run state, no player and no
// creature -- so there is no seat to resolve and no character to scope to. The
// scope lives at the only door that BUILDS the node (`Setup`, through
// `AppliesTo`); naming a seat here is exactly what `EB-225` shows a teardown
// must not have to do.
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_KleeFanfareCounter_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCombatUi __instance) =>
        FanfareCounter.Hide(__instance);
}
