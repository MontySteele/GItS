using System;
using System.Collections.Generic;
using System.Globalization;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Powers;
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
/// FURINA'S "DRAINED N" COUNTER, BESIDE THE FANFARE GAUGE (the Salon's Tab,
/// 2026-10-05, proposal sec.16, "Screen": "Drain room must be readable before
/// any play: the line, and how much is drained. The cheapest honest reading
/// is a second counter beside Fanfare: 'Drained N', whose hover says 'You can
/// Drain down to M HP'.").
///
/// BUILT THE WAY <see cref="FanfareCounter"/> IS, which is built the way
/// Klee's Spark counter is (<see cref="SparkCounter"/>): the same node shape,
/// the same placement rule, one slot up the column above the energy orb
/// (<see cref="Slot"/>: directly above the Fanfare gauge; the Spark counter
/// moves one slot further for a Furina holding Sparks). It sat one slot to
/// the RIGHT until the 2026-10-11 playtest ("The Drain gauge also overlaps
/// with the Block indicator; we need to move it."): see
/// <see cref="SparkCounter.PlaceInColumn"/>. The face is the drained HP in
/// the base game's style for a number over art, cream with a dark outline in
/// the glyph's bottom-right corner (<see cref="FurinaCounterFace"/>), inside
/// a thin red ring (<see cref="RingColour"/>); the hover is the Drain
/// buffer left and the Drain rule. No HP-bar tick: the counter is the reading.
///
/// THE FEED is <see cref="FurinaStage.RefreshBadges"/>, the funnel every
/// Drain, Repay and turn already takes. No <c>_Process</c>.
/// </summary>
public static class DrainedCounter
{
    /// <summary>The node this file owns, and the handle its teardown uses.</summary>
    internal const string RootName = "KleeModDrainedCounter";

    /// <summary>The glyph: the Salon member's sigil (the Salon takes the
    /// HP). There is no dedicated Drained icon.</summary>
    public const string GlyphPath = "furina/powers/salon_member.png";

    /// <summary>Its place in the column: above the Fanfare gauge.</summary>
    public const int Slot = 1;

    /// <summary>The hover's title key (registered in
    /// <c>KleeMod.InjectLocStrings</c>).</summary>
    public const string TitleKey = "KLEEMOD-ARM_STAGE_DRAINED";

    private const string HoverShownMeta = "kleemod_drained_hover_shown";

    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    private static bool _warnedGlyph;

    /// <summary>Does this creature get the counter? Furina.</summary>
    public static bool AppliesTo(Creature? creature) =>
        FurinaResources.IsFurina(creature);

    /// <summary>The number the counter draws: her drained HP.</summary>
    public static int Read(Creature? creature) => FurinaStage.DrainedOf(creature);

    /// <summary>The hover's first sentence. Pure. THE FURINA WAVE
    /// (2026-10-13, `review/records/furina-wave-2026-10-13.md`, "To change
    /// now" 1): ONE Drain number, the buffer she has left, and that Drain
    /// inside it returns after combat -- the seat page's words
    /// (<c>blindplay_render.STAGE_DRAIN_BUFFER_LINE</c>). Four seats read
    /// the buffer and the "Drain line 59 HP" it replaced as two numbers for
    /// one rule; the line keeps its meaning in words ("past your line", the
    /// words Lyney's act and Regina of All Waters print), never as a second
    /// number. At a line of 0 her HP is inside the buffer, so all of it
    /// returns (the Spend round 2, 2026-10-10); under A Five-Century Act the
    /// part past it returns too (the Spend round, 2026-10-10).
    /// </summary>
    public static string BufferSentence(int bufferLeft, bool lineZero = false,
                                        bool pastReturns = false) =>
        "Drain buffer: [blue]"
      + bufferLeft.ToString(CultureInfo.InvariantCulture) + "[/blue] HP left. "
      + (lineZero
            ? "Your HP is inside it, so all your [gold]Drain[/gold] returns "
              + "after combat."
         : pastReturns
            ? "All your [gold]Drain[/gold] returns after combat, past it too."
            : "[gold]Drain[/gold] inside it returns after combat; past it "
              + "(past your line), only [gold]Repay[/gold] returns.");

    /// <summary>THE "LOST FOR GOOD" COUNTER (the quarter-line round,
    /// 2026-10-10, "What to change" 1): the drained count and, when any of
    /// it is past the line, that part in one phrase: "Drained 12 HP (4 past
    /// your line: lost unless you Repay)". Seats learned the cost of
    /// draining past the line only by losing the HP. Pure.</summary>
    public static string DrainedPhrase(int drained, int past,
                                       bool pastReturns = false) =>
        "Drained [blue]" + drained.ToString(CultureInfo.InvariantCulture)
      + "[/blue] HP"
      + (past > 0
            ? " ([blue]" + past.ToString(CultureInfo.InvariantCulture)
              + "[/blue] past your line"
              // The Spend round (2026-10-10): under A Five-Century Act the
              // past-line part returns at the curtain call, so it is not
              // "lost unless you Repay".
              + (pastReturns
                    ? ")"
                    : ": lost unless you [gold]Repay[/gold])")
            : "");

    /// <summary>The hover's body: the buffer left, the drained count (and
    /// how much of it is past the buffer) and the rule. Pure.</summary>
    public static string HoverBody(int drained, int bufferLeft,
                                   bool lineZero = false, int past = 0,
                                   bool pastReturns = false) =>
        BufferSentence(bufferLeft, lineZero, pastReturns) + "\n"
      + DrainedPhrase(drained, past, pastReturns)
      + ".\n" + ArmKeywordTips.DrainBody;

    /// <summary>The hover's body for her, read off the ledger now.</summary>
    public static string HoverBody(Creature? creature)
    {
        if (creature == null || !FurinaStage.LiveFor(creature))
        {
            return HoverBody(0, 0);
        }
        var ledger = FurinaStageLedger.For(creature);
        return HoverBody(ledger.Drained, ledger.BufferLeft, ledger.Line <= 0,
                         ledger.DrainedPast,
                         ledger.Mods.FiveCenturyAct > 0);
    }

    /// <summary>Build the counter for the LOCAL seat, from the
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
        FurinaCounterFace.Dress(root, side, RingColour);
        // The one difference from the Spark badge: this face has a hover.
        root.MouseFilter = Control.MouseFilterEnum.Stop;
        var creature = me.Creature;
        root.MouseEntered += () => ShowHover(root, creature);
        root.MouseExited += () => ClearHover(root);
        root.TreeExiting += () => ClearHover(root);

        parent.AddChildSafely(root);
        Displays.Set(me, root);

        SparkCounter.Apply(root, panel, side, ui.GetViewportRect().Size,
                           Slot);
        Paint(root, creature);
    }

    /// <summary>Re-read her drained HP and redraw. Headless-safe: it returns
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
            Log.Warn($"[{KleeMod.ModId}] drained counter: no local seat in "
                   + $"this combat ({e.GetType().Name}: {e.Message}); drawing "
                   + "nothing.");
            return null;
        }
    }

    /// <summary>THE RING'S COLOUR: the base game's red,
    /// <c>StsColors.red</c> (#FF5555), the HP-loss colour. The 2026-10-11
    /// playtest found the white number "hard to make out" and the red one
    /// on the busy glyph "not really legible, either"; the ruled fix ("Yep,
    /// sounds good!") put the number in the base style and the red on a
    /// ring.</summary>
    public static Color RingColour => StsColors.red;

    /// <summary>The number's fill: the base game's cream at every count
    /// (<see cref="FurinaCounterFace.Fill"/>).</summary>
    public static Color FaceColor => FurinaCounterFace.Fill;

    private static void Paint(Control root, Creature? creature)
    {
        if (creature == null || !GodotObject.IsInstanceValid(root)) return;

        var drained = Read(creature);
        if (root.GetNodeOrNull<Label>("Count") is { } count)
        {
            count.Text = drained.ToString(CultureInfo.InvariantCulture);
        }
        FurinaCounterFace.SetFill(root, FaceColor);

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
                    Log.Warn($"[{KleeMod.ModId}] drained counter: no live "
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
                Log.Warn($"[{KleeMod.ModId}] drained counter: the glyph could "
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
                    new LocString("card_keywords", TitleKey + ".title"),
                    HoverBody(creature)),
            };
            NHoverTipSet.CreateAndShow(
                root, tips, HoverTip.GetHoverTipAlignment(root));
            root.SetMeta(HoverShownMeta, true);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] drained counter: hover skipped: {e}");
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

    /// <summary>Free the counter when the combat UI stands down, by node name,
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

/// <summary>The counter dies with the combat, on the game's own hook.</summary>
// lint: no-seat: pure static teardown. It frees, by name, the one child node
// this file added to the combat UI and touches no run state, player or
// creature. The scope lives at the only door that BUILDS the node (`Setup`,
// through `DrainedCounter.AppliesTo`).
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_FurinaDrainedCounter_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCombatUi __instance) =>
        DrainedCounter.Hide(__instance);
}
