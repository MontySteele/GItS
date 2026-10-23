using System;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;

namespace KleeMod.Vfx;

/// <summary>
/// THE NATION PIP ON A COMPANION CARD (card frames stage 1, 2026-10-19).
///
/// [USER], 2026-10-19: "we need a quick way of distinguishing the character
/// cards". The kits got their own frame tints (<see cref="CardFrameColors"/>);
/// the shared companions keep the Colorless frame (legacy review pick 4) and
/// get this instead: a round pip in the nation's element colour carrying the
/// nation's initial, so a Mondstadt companion and an Inazuma one read apart
/// at a glance.
///
/// WHICH CARDS. Every <see cref="ICompanionCard"/> that declares a
/// <see cref="ICompanionCard.Nation"/> -- the shared companions and the
/// kit-own ones (Klee's three, Gorou's four, Varka's Knights) alike, since
/// all of them are companions from somewhere. A nation with no row in
/// <see cref="StyleFor"/> draws nothing.
///
/// WHY A DRAWN PIP AND NOT A CREST. No emblem art ships (Tier F official art
/// may not enter the repo), and a crest small enough for this slot would need
/// drawing by hand to stay readable. The pip is two Godot nodes built here,
/// so it needs no texture and nothing in the pck; a crest image can replace
/// it later without moving the slot.
///
/// WHERE. The element gem (<see cref="ElementBadge"/>) sits immediately to
/// the LEFT of the type plaque; this sits immediately to the RIGHT, mirrored
/// with the same anchors-on-the-plaque geometry, so the two never overlap
/// and the divider reads "element - type - nation". Same hook, same pooled
/// `NCard` rules (repaint every time, hide when the card has no nation,
/// never throw into the turn loop).
/// </summary>
public static class NationEmblem
{
    /// <summary>The node's name on the plaque, so a pooled `NCard` reuses it.</summary>
    internal const string NodeName = "KleeNationEmblem";

    internal const string LabelName = "Initial";

    /// <summary>
    /// The game's own Kreon Bold, the slab serif its card titles are set in
    /// ([USER], 2026-10-22: "The 'I' on Inazuma cards looks kind of like an
    /// l"). The theme font is a sans whose capital I is a bare stroke; Kreon's
    /// I carries a slab top and bottom, and M, L and F stay the same family.
    /// A missing resource falls back to the theme font, as before.
    /// </summary>
    public const string FontPath = "res://themes/kreon_bold_shared.tres";

    /// <summary>Slightly smaller than the 48px element gem: the gem is a
    /// rules affordance, the pip is a tag.</summary>
    internal const float Side = 40f;

    /// <summary>Same gap as the gem on the other side, so the row is even.</summary>
    internal const float Gap = ElementBadge.Gap;

    /// <summary>One nation's pip: its element colour and its initial.</summary>
    public readonly record struct Style(Color Fill, string Initial);

    /// <summary>
    /// The four nations' pips, each in its archon's element: Mondstadt Anemo
    /// teal, Liyue Geo gold, Inazuma Electro violet, Fontaine Hydro blue.
    /// Liyue has no companion yet; its row is here so the first one draws.
    /// </summary>
    public static Style? StyleFor(string? nation) => nation switch
    {
        "mondstadt" => new Style(new Color("3FB894"), "M"),
        "liyue" => new Style(new Color("D9A62E"), "L"),
        "inazuma" => new Style(new Color("9A5FD9"), "I"),
        "fontaine" => new Style(new Color("3A86D9"), "F"),
        _ => null,
    };

    /// <summary>The nation a card's face shows, or null.</summary>
    public static string? NationOf(CardModel? card) =>
        card is ICompanionCard companion ? companion.Nation : null;

    private static bool _warned;

    /// <summary>Put the pip on, take it off, and never throw at the caller
    /// (this runs inside the turn loop; see <see cref="ElementBadge.Paint"/>).</summary>
    internal static void Paint(NCard nCard)
    {
        try
        {
            PaintUnguarded(nCard);
        }
        catch (Exception e) when (e is ObjectDisposedException or InvalidOperationException)
        {
            if (!_warned)
            {
                _warned = true;
                Log.Warn($"[{KleeMod.ModId}] nation emblem: {e.Message}; "
                       + "the card draws without its pip.");
            }
        }
    }

    private static void PaintUnguarded(NCard nCard)
    {
        CardModel? card = nCard.Model;
        if (card == null || !nCard.IsNodeReady())
        {
            return;
        }

        // `IsNodeReady` on the plaque too: an unready parent defers AddChild,
        // and a second paint in the same frame would build a second pip.
        var plaque = nCard.GetNodeOrNull<Control>(ElementBadge.PlaquePath);
        if (plaque == null || !plaque.IsNodeReady())
        {
            return;
        }

        var pip = plaque.GetNodeOrNull<Panel>(NodeName);
        string? nation = NationOf(card);
        Style? style = StyleFor(nation);
        if (style == null)
        {
            if (pip != null && GodotObject.IsInstanceValid(pip))
            {
                pip.Visible = false;
            }

            return;
        }

        if (pip == null)
        {
            pip = Build();
            plaque.AddChildSafely(pip);
        }

        if (!GodotObject.IsInstanceValid(pip))
        {
            return;
        }

        // A pooled card arrives wearing the last card's pip: restyle only
        // when the nation changed, otherwise just show it.
        if (!pip.HasMeta(NodeName) || pip.GetMeta(NodeName).AsString() != nation)
        {
            pip.SetMeta(NodeName, nation!);
            pip.AddThemeStyleboxOverride("panel", Disc(style.Value.Fill));
            var label = pip.GetNodeOrNull<Label>(LabelName);
            if (label != null)
            {
                label.Text = style.Value.Initial;
            }
        }

        pip.Visible = true;
    }

    private static Font? LoadFont() =>
        ResourceLoader.Exists(FontPath) ? ResourceLoader.Load<Font>(FontPath) : null;

    private static StyleBoxFlat Disc(Color fill)
    {
        var box = new StyleBoxFlat
        {
            BgColor = fill,
            BorderColor = new Color(0.1f, 0.08f, 0.07f, 0.95f),
            AntiAliasing = true,
        };
        box.SetBorderWidthAll(3);
        box.SetCornerRadiusAll((int)(Side / 2f));
        return box;
    }

    /// <summary>The pip, anchored to the plaque's RIGHT edge and vertically
    /// centred on it: the mirror of <see cref="ElementBadge"/>'s gem.</summary>
    private static Panel Build()
    {
        var pip = new Panel
        {
            Name = NodeName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            AnchorLeft = 1f,
            AnchorRight = 1f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = Gap,
            OffsetRight = Gap + Side,
            OffsetTop = -Side / 2f,
            OffsetBottom = Side / 2f,
        };
        var label = new Label
        {
            Name = LabelName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        };
        label.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        if (LoadFont() is { } font)
        {
            label.AddThemeFontOverride("font", font);
        }
        label.AddThemeFontSizeOverride("font_size", 26);
        label.AddThemeColorOverride("font_color", Colors.White);
        label.AddThemeColorOverride("font_outline_color", new Color(0.1f, 0.08f, 0.07f));
        label.AddThemeConstantOverride("outline_size", 6);
        pip.AddChild(label);
        return pip;
    }
}

/// <summary>The same arming point as <see cref="ElementBadge"/>: every redraw
/// on every surface that renders an `NCard`.</summary>
[HarmonyPatch(typeof(NCard), "UpdateStarCostVisuals")]
internal static class NCard_UpdateStarCostVisuals_KleeNationEmblem_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance) => NationEmblem.Paint(__instance);
}
