using System;
using System.Collections.Generic;
using System.Globalization;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// FURINA'S FANFARE GAUGE IN THE ENERGY AREA.
///
/// THE ASK. [USER], on Furina v2 (PR #892): Fanfare should come "out of the
/// tooltip and into a proper UI gauge like stars and bombs have". Fanfare is
/// one number on Furina, a second resource the way the Regent's Stars are, so
/// it is drawn where the base game draws Stars: beside the energy orb.
///
/// THE PATTERN IS KLEE'S SPARK COUNTER (<see cref="SparkCounter"/>), reused
/// rather than re-derived. That file already answered every question this one
/// would ask: why the game's own <c>%StarCounter</c> node cannot simply be
/// shown (it reads <c>PlayerCombatState.Stars</c> and its tip says STAR), why
/// the badge is a SIBLING of <c>%EnergyCounterContainer</c> and not a child
/// (`EB-815`), and where above the panel it lands. This file calls its
/// <see cref="SparkCounter.SideOf"/>, <see cref="SparkCounter.Build"/> and
/// <see cref="SparkCounter.Apply"/>, so the two resources share one placement
/// rule and one node shape. A Furina holding Sparks (Klee's cards work for
/// anyone, 2026-10-04) shows both in one row above the orb: this gauge in the
/// first slot, the Spark counter in the next (<see cref="SparkCounter.SlotFor"/>).
///
/// WHAT IT SHOWS. The face is the number alone, red at zero and cream
/// otherwise (<c>NStarCounter.SetStarCountText</c>'s pair). Hovering it shows
/// this turn's gained and spent counts, the ones Ousia Surge, Pneuma Refrain,
/// Bring the House Down and Navia read, under the Fanfare keyword's own title
/// and definition (<see cref="ArmKeywordTips.FanfareBody"/>).
///
/// THE OLD BADGE. <see cref="FanfarePower"/> stays on her creature as a model,
/// so the rules, the wire and a co-op partner's power row keep it; on her own
/// screen its status-strip node is suppressed (<see cref="HidesBadge"/>), the
/// way <see cref="SparkGauge.HidesBadge"/> suppresses Klee's, so the number is
/// not drawn twice. Rehearsal keeps its own Power badge.
///
/// THE FEED is <see cref="FurinaStage.RefreshBadges"/>, the funnel every
/// Fanfare move already took to redraw the old badge. No <c>_Process</c>.
///
/// THE GLYPH is <see cref="GlyphPath"/>, the board sigil the Fanfare badge
/// already wore (<c>KleePowerIcons</c>). There is no dedicated Fanfare icon.
/// </summary>
public static class FanfareCounter
{
    /// <summary>The node this file owns, and the handle its teardown uses.</summary>
    internal const string RootName = "KleeModFanfareCounter";

    /// <summary>The Fanfare glyph: the sigil her Fanfare badge wears.</summary>
    public const string GlyphPath = "furina/powers/center_stage.png";

    private const string HoverShownMeta = "kleemod_fanfare_hover_shown";

    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    private static bool _warnedGlyph;

    /// <summary>Does this creature get the gauge? Furina, whose stage is
    /// live from her first combat (<see cref="FurinaStage.LiveFor"/>).</summary>
    public static bool AppliesTo(Creature? creature) =>
        FurinaResources.IsFurina(creature);

    /// <summary>The number the gauge draws: her Fanfare, the ledger's.</summary>
    public static int Read(Creature? creature) => FurinaStage.FanfareOf(creature);

    /// <summary>The hover's body for a turn's flow counts. Pure.</summary>
    public static string HoverBody(int gained, int spent) =>
        "This turn: gained [blue]"
      + gained.ToString(CultureInfo.InvariantCulture)
      + "[/blue], spent [blue]"
      + spent.ToString(CultureInfo.InvariantCulture)
      + "[/blue].\n" + ArmKeywordTips.FanfareBody;

    /// <summary>The hover's body for her, read off the ledger now.</summary>
    public static string HoverBody(Creature? creature)
    {
        if (creature == null || !FurinaStage.LiveFor(creature))
        {
            return HoverBody(0, 0);
        }
        var ledger = FurinaStageLedger.For(creature);
        return HoverBody(ledger.GainedThisTurn, ledger.SpentThisTurn);
    }

    /// <summary>
    /// Is this the Fanfare badge on her OWN screen, where the gauge draws the
    /// same number? A co-op partner still sees it on her creature. Never
    /// throws: a canonical power has no owner to ask.
    /// </summary>
    public static bool HidesBadge(PowerModel power)
    {
        if (power is not FanfarePower) return false;
        Creature? owner;
        try
        {
            owner = power.IsMutable ? power.Owner : null;
        }
        catch (Exception)
        {
            return false;
        }
        return owner != null && AppliesTo(owner) && LocalContext.IsMe(owner);
    }

    /// <summary>Build the gauge for the LOCAL seat, from the
    /// <c>NCombatUi.Activate</c> postfix <c>GaugeBridge</c> installs.</summary>
    public static void Setup(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !AppliesTo(me.Creature)) return;
        if (NCombatRoom.Instance?.Ui is not { } ui) return;

        var star = ui.GetNodeOrNull<Control>("%StarCounter");
        var panel = ui.EnergyCounterContainer;
        var parent = panel?.GetParent() ?? (Node)ui;

        Displays.Discard(me);
        var side = SparkCounter.SideOf(star);
        var root = SparkCounter.Build(side);
        root.Name = RootName;
        // The one difference from the Spark badge: this face has a hover.
        root.MouseFilter = Control.MouseFilterEnum.Stop;
        var creature = me.Creature;
        root.MouseEntered += () => ShowHover(root, creature);
        root.MouseExited += () => ClearHover(root);
        root.TreeExiting += () => ClearHover(root);

        parent.AddChildSafely(root);
        Displays.Set(me, root);

        SparkCounter.Apply(root, panel, side, ui.GetViewportRect().Size);
        Paint(root, creature);
    }

    /// <summary>Re-read her Fanfare and redraw. Headless-safe: it returns
    /// before any node work when there is no combat room.</summary>
    public static void Refresh(Creature? creature)
    {
        if (!AppliesTo(creature) || NCombatRoom.Instance == null) return;
        var player = creature!.Player;
        if (player == null || !LocalContext.IsMe(player)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            Setup(creature.CombatState as CombatState);
            root = Displays.Get(player);
            if (root == null) return;
        }

        Paint(root, creature);
    }

    /// <summary>The local seat, or null. <c>LocalContext.GetMe</c> throws for
    /// "not in this combat" (`EB-225`), so it is caught here.</summary>
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

    private static void Paint(Control root, Creature? creature)
    {
        if (creature == null || !GodotObject.IsInstanceValid(root)) return;

        var fanfare = Read(creature);
        if (root.GetNodeOrNull<Label>("Count") is { } count)
        {
            count.Text = fanfare.ToString(CultureInfo.InvariantCulture);
            count.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                fanfare == 0 ? StsColors.red : StsColors.cream);
        }

        if (root.GetNodeOrNull<TextureRect>("Icon") is { } icon)
        {
            SetGlyph(icon);
        }
    }

    /// <summary>Resolved fresh on every paint, never cached across a scene
    /// (`EB-222`), and never throws at its caller.</summary>
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
                           + $"{GlyphPath}; drawing the number with no glyph.");
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

    private static void ShowHover(Control root, Creature creature)
    {
        try
        {
            if (!GodotObject.IsInstanceValid(root)) return;
            // NHoverTipSet keys its live set by owner and ADDS: clear first.
            ClearHover(root);
            var tips = new List<IHoverTip>
            {
                new HoverTip(
                    new LocString("card_keywords",
                                  ArmKeywordTips.FanfareKey + ".title"),
                    HoverBody(creature)),
            };
            NHoverTipSet.CreateAndShow(
                root, tips, HoverTip.GetHoverTipAlignment(root));
            root.SetMeta(HoverShownMeta, true);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] fanfare counter: hover skipped: {e}");
        }
    }

    private static void ClearHover(Control root)
    {
        if (!GodotObject.IsInstanceValid(root) || !root.HasMeta(HoverShownMeta))
        {
            return;
        }
        root.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(root);
    }

    /// <summary>Free the gauge when the combat UI stands down, by node name,
    /// never by seat (`EB-225`).</summary>
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

/// <summary>The gauge dies with the combat, on the game's own hook.</summary>
// lint: no-seat: pure static teardown. It frees, by name, the one child node
// this file added to the combat UI and touches no run state, player or
// creature. The scope lives at the only door that BUILDS the node (`Setup`,
// through `FanfareCounter.AppliesTo`).
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_FurinaFanfareCounter_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCombatUi __instance) =>
        FanfareCounter.Hide(__instance);
}

/// <summary>Her Fanfare badge stays off her own status strip, where the
/// gauge draws the same number; a co-op partner still sees it.</summary>
[HarmonyPatch(typeof(NPowerContainer), "Add")]
internal static class NPowerContainer_Add_FurinaFanfareCounter_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel power) =>
        !FanfareCounter.HidesBadge(power);
}
