using System;
using Godot;
using HarmonyLib;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.HoverTips;

namespace KleeMod.Vfx;

/// <summary>
/// The chart's open/closed state and its text conversion, with no Godot in
/// it, so the headless suite drives it. <see cref="ReactionChart"/> owns the
/// nodes and asks this what to do.
/// </summary>
public sealed class ReactionChartState
{
    public bool IsOpen { get; private set; }

    /// <summary>The button: open if closed, close if open. Answers the new state.</summary>
    public bool Toggle()
    {
        IsOpen = !IsOpen;
        return IsOpen;
    }

    /// <summary>Close. Answers whether anything closed (a second close is a no-op).</summary>
    public bool Close()
    {
        var was = IsOpen;
        IsOpen = false;
        return was;
    }

    /// <summary>A click outside the panel, or Esc: closes an open chart and
    /// answers whether the input was the chart's to take.</summary>
    public bool OnDismiss() => Close();

    /// <summary>The game's tags to Godot's: a plain RichTextLabel has no
    /// [gold] or [blue], it prints them as text.</summary>
    public static string ToGodotBbcode(string text) => text
        .Replace("[gold]", "[color=#efc851]").Replace("[/gold]", "[/color]")
        .Replace("[blue]", "[color=#87ceeb]").Replace("[/blue]", "[/color]");
}

/// <summary>
/// THE ELEMENTAL REACTIONS CHART ([USER], 2026-10-22: "hover tooltips are a
/// good idea if you're about to trigger one, but it would help to have some
/// way to find them all in-game").
///
/// THE BUTTON sits in the top bar's right-hand row (<c>RightAlignedStuff</c>,
/// an HBoxContainer in <c>scenes/ui/top_bar.tscn</c>), immediately left of
/// the Map button: four aura gems in a square, hovering the game's own tip
/// "Elemental Reactions". It is added once per top bar, found again by name,
/// so a reused bar never grows a second one.
///
/// THE CHART is a CanvasLayer child of the top bar: a dimmed full-screen
/// backdrop and a centred panel, the four aura elements as rows and the six
/// elements as columns, each cell the reaction and its effect in
/// <see cref="ReactionGuide"/>'s words. A click outside the panel, the button
/// again (the backdrop covers it, so the click lands on the backdrop) or Esc
/// closes it, and closing frees every node, so a closed chart blocks no
/// input. Being the bar's child, it goes when the run's UI goes.
///
/// NOTHING HERE MAY THROW INTO THE GAME: every entry point is wrapped, and a
/// failure logs once and leaves the bar as the game built it.
/// </summary>
public static class ReactionChart
{
    /// <summary>The title row key (`KleeMod.InjectLocStrings` registers it).</summary>
    public const string TitleKey = "KLEEMOD-REACTION_CHART";

    internal const string ButtonName = "KleeReactionChartButton";
    internal const string LayerName = "KleeReactionChartLayer";

    /// <summary>Above the run's screens and the top bar; the game's own
    /// modal popups are not expected while the chart is up.</summary>
    internal const int CanvasLayerIndex = 90;

    /// <summary>The button's hover body, a keyed row (`ReactionGuide`).</summary>
    internal static string ButtonTipBody => ReactionGuide.Label(ReactionGuide.ButtonTipRow);

    private static readonly ReactionChartState State = new();
    private static CanvasLayer? _layer;
    private static bool _warned;

    // ---- The button ----------------------------------------------------

    internal static void AddButton(NTopBar bar)
    {
        try
        {
            if (bar.Map is not Control map || map.GetParent() is not Control row) return;
            if (row.GetNodeOrNull(ButtonName) != null) return;

            var button = new CenterContainer
            {
                Name = ButtonName,
                CustomMinimumSize = new Vector2(64, 80),
                MouseFilter = Control.MouseFilterEnum.Stop,
                MouseDefaultCursorShape = Control.CursorShape.PointingHand,
            };
            var grid = new GridContainer { Columns = 2, MouseFilter = Control.MouseFilterEnum.Ignore };
            grid.AddThemeConstantOverride("h_separation", 2);
            grid.AddThemeConstantOverride("v_separation", 2);
            foreach (var element in ReactionGuide.AuraElements)
            {
                grid.AddChild(Gem(element, 24));
            }
            button.AddChild(grid);

            button.MouseEntered += () => Hover(button, grid, true);
            button.MouseExited += () => Hover(button, grid, false);
            button.GuiInput += e => ButtonInput(button, e);

            row.AddChild(button);
            row.MoveChild(button, map.GetIndex());
        }
        catch (Exception e)
        {
            Warn("the top bar button was not added", e);
        }
    }

    private static void Hover(Control button, Control grid, bool on)
    {
        try
        {
            if (!GodotObject.IsInstanceValid(button)) return;
            grid.Modulate = on ? new Color(1.3f, 1.3f, 1.3f) : Colors.White;
            NHoverTipSet.Remove(button);
            if (!on) return;
            var tip = new HoverTip(new LocString("card_keywords", TitleKey + ".title"), ButtonTipBody);
            NHoverTipSet.CreateAndShow(button, tip, HoverTip.GetHoverTipAlignment(button));
        }
        catch (Exception e)
        {
            Warn("the button's hover was skipped", e);
        }
    }

    private static void ButtonInput(Control button, InputEvent e)
    {
        try
        {
            if (e is InputEventMouseButton { ButtonIndex: MouseButton.Left, Pressed: false })
            {
                button.AcceptEvent();
                NHoverTipSet.Remove(button);
                if (State.Toggle()) Open(button);
                else Close();
            }
        }
        catch (Exception ex)
        {
            Warn("the chart did not open", ex);
            State.Close();
        }
    }

    // ---- The chart -----------------------------------------------------

    private static void Open(Control button)
    {
        Close(keepState: true);
        var bar = FindBar(button);
        if (bar == null)
        {
            State.Close();
            return;
        }

        var layer = new CanvasLayer { Name = LayerName, Layer = CanvasLayerIndex };
        var backdrop = new ColorRect
        {
            Color = new Color(0f, 0f, 0f, 0.72f),
            MouseFilter = Control.MouseFilterEnum.Stop,
            FocusMode = Control.FocusModeEnum.All,
        };
        backdrop.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        backdrop.GuiInput += BackdropInput;
        layer.AddChild(backdrop);

        var center = new CenterContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        center.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        backdrop.AddChild(center);
        center.AddChild(Panel());

        _layer = layer;
        bar.AddChildSafely(layer);
        if (backdrop.IsInsideTree()) backdrop.GrabFocus();
        else backdrop.Connect(Node.SignalName.TreeEntered,
            Callable.From(() => { if (GodotObject.IsInstanceValid(backdrop)) backdrop.GrabFocus(); }),
            (uint)GodotObject.ConnectFlags.OneShot);
        layer.TreeExiting += () =>
        {
            if (ReferenceEquals(_layer, layer)) { _layer = null; State.Close(); }
        };
    }

    private static void BackdropInput(InputEvent e)
    {
        try
        {
            var dismiss = e is InputEventMouseButton { ButtonIndex: MouseButton.Left, Pressed: false }
                || (e is InputEventKey { Pressed: true, Keycode: Key.Escape })
                || e.IsActionPressed("ui_cancel");
            if (!dismiss) return;
            _layer?.GetViewport()?.SetInputAsHandled();
            if (State.OnDismiss()) Close();
        }
        catch (Exception ex)
        {
            Warn("the chart's input was skipped", ex);
        }
    }

    /// <summary>Free the chart. Safe to call when nothing is open.</summary>
    internal static void Close(bool keepState = false)
    {
        try
        {
            if (!keepState) State.Close();
            var layer = _layer;
            _layer = null;
            if (layer != null && GodotObject.IsInstanceValid(layer)) layer.QueueFree();
        }
        catch (Exception e)
        {
            Warn("the chart did not close cleanly", e);
        }
    }

    private static NTopBar? FindBar(Node? node)
    {
        for (var n = node; n != null; n = n.GetParent())
        {
            if (n is NTopBar bar) return bar;
        }
        return null;
    }

    // ---- The panel's nodes ---------------------------------------------

    private static readonly Color Ink = new(0.95f, 0.92f, 0.85f);
    private static readonly Color Muted = new(0.70f, 0.68f, 0.62f);
    private static readonly Color Gold = new(0.94f, 0.78f, 0.32f);

    private static Control Panel()
    {
        var panel = new PanelContainer { MouseFilter = Control.MouseFilterEnum.Stop };
        panel.AddThemeStyleboxOverride("panel", new StyleBoxFlat
        {
            BgColor = new Color(0.10f, 0.11f, 0.15f, 0.97f),
            BorderColor = Gold,
            BorderWidthLeft = 2, BorderWidthTop = 2, BorderWidthRight = 2, BorderWidthBottom = 2,
            CornerRadiusTopLeft = 10, CornerRadiusTopRight = 10,
            CornerRadiusBottomLeft = 10, CornerRadiusBottomRight = 10,
            ContentMarginLeft = 28, ContentMarginRight = 28, ContentMarginTop = 20, ContentMarginBottom = 20,
        });

        var column = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        column.AddThemeConstantOverride("separation", 12);
        panel.AddChild(column);

        column.AddChild(Text(ReactionGuide.Label(ReactionGuide.HeadingRow), 34, Gold, centered: true, width: 0));
        column.AddChild(Text(ReactionGuide.Label(ReactionGuide.LegendRow),
                             20, Muted, centered: true, width: 0));

        var grid = new GridContainer
        {
            Columns = 1 + ReactionGuide.Elements.Count,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        grid.AddThemeConstantOverride("h_separation", 6);
        grid.AddThemeConstantOverride("v_separation", 6);

        grid.AddChild(Text(ReactionGuide.Label(ReactionGuide.CornerRow), 20, Muted, centered: true, width: 120));
        foreach (var hit in ReactionGuide.Elements) grid.AddChild(Header(hit));

        foreach (var aura in ReactionGuide.AuraElements)
        {
            grid.AddChild(Header(aura));
            foreach (var hit in ReactionGuide.Elements) grid.AddChild(Cell(aura, hit));
        }
        column.AddChild(grid);

        foreach (var note in ReactionGuide.Notes)
        {
            column.AddChild(Text(note, 20, Ink, centered: false, width: 0));
        }
        column.AddChild(Text(ReactionGuide.Label(ReactionGuide.CloseRow), 18, Muted, centered: true, width: 0));
        return panel;
    }

    private static Control Header(Element element)
    {
        var box = new VBoxContainer
        {
            MouseFilter = Control.MouseFilterEnum.Ignore,
            CustomMinimumSize = new Vector2(120, 0),
            Alignment = BoxContainer.AlignmentMode.Center,
        };
        var gemRow = new CenterContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        gemRow.AddChild(Gem(element, 34));
        box.AddChild(gemRow);
        box.AddChild(Text(ElementWords.Name(element), 22, ElementColour(element), centered: true, width: 0));
        return box;
    }

    private static Control Cell(Element aura, Element hit)
    {
        var words = ReactionGuide.Cell(aura, hit);
        var same = aura == hit;
        var box = new PanelContainer
        {
            MouseFilter = Control.MouseFilterEnum.Ignore,
            CustomMinimumSize = new Vector2(150, 70),
        };
        var tint = ElementColour(aura);
        box.AddThemeStyleboxOverride("panel", new StyleBoxFlat
        {
            BgColor = same ? new Color(1f, 1f, 1f, 0.03f) : new Color(tint.R, tint.G, tint.B, 0.12f),
            CornerRadiusTopLeft = 6, CornerRadiusTopRight = 6,
            CornerRadiusBottomLeft = 6, CornerRadiusBottomRight = 6,
            ContentMarginLeft = 8, ContentMarginRight = 8, ContentMarginTop = 6, ContentMarginBottom = 6,
        });
        string body;
        if (same) body = words;
        else
        {
            var split = words.IndexOf('\n');
            body = split < 0
                ? words
                : $"[b][color=#{ElementColour(hit).ToHtml(false)}]{words[..split]}[/color][/b]\n{words[(split + 1)..]}";
        }
        box.AddChild(Text(body, 18, same ? Muted : Ink, centered: true, width: 150));
        return box;
    }

    /// <summary>Genshin's element colours, the values
    /// <c>Vfx/Prototype/FurinaStageCueNodes.ElementColour</c> uses (that file
    /// is prototype-only, this one ships in every build).</summary>
    private static Color ElementColour(Element element) => element switch
    {
        Element.Hydro => new Color(0.30f, 0.76f, 0.95f),
        Element.Electro => new Color(0.75f, 0.53f, 0.95f),
        Element.Geo => new Color(0.96f, 0.72f, 0.20f),
        Element.Cryo => new Color(0.62f, 0.87f, 0.93f),
        Element.Anemo => new Color(0.45f, 0.86f, 0.70f),
        Element.Pyro => new Color(0.94f, 0.47f, 0.22f),
        _ => Colors.White,
    };

    private static RichTextLabel Text(string bbcode, int size, Color colour, bool centered, float width)
    {
        var text = ReactionChartState.ToGodotBbcode(bbcode);
        var label = new RichTextLabel
        {
            BbcodeEnabled = true,
            FitContent = true,
            ScrollActive = false,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            Text = centered ? $"[center]{text}[/center]" : text,
        };
        if (width > 0) label.CustomMinimumSize = new Vector2(width - 16, 0);
        var regular = LoadFont("res://themes/kreon_regular_shared.tres");
        var bold = LoadFont("res://themes/kreon_bold_shared.tres");
        if (regular != null) label.AddThemeFontOverride("normal_font", regular);
        if (bold != null) label.AddThemeFontOverride("bold_font", bold);
        label.AddThemeFontSizeOverride("normal_font_size", size);
        label.AddThemeFontSizeOverride("bold_font_size", size);
        label.AddThemeColorOverride("default_color", colour);
        return label;
    }

    /// <summary>An aura gem, the texture resolved fresh each build
    /// (<see cref="ElementBadge"/>'s EB-222 rule: never a texture held in a
    /// static). A missing pack draws an empty square of the right size.</summary>
    private static TextureRect Gem(Element element, int side)
    {
        var rect = new TextureRect
        {
            CustomMinimumSize = new Vector2(side, side),
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        try
        {
            var path = ElementBadge.IconPathFor(element) is { } rel ? KleePck.Path(rel) : null;
            if (path != null && ResourceLoader.Load<Texture2D>(path) is { } texture) rect.Texture = texture;
        }
        catch (Exception e)
        {
            Warn($"the {element} gem was not drawn", e);
        }
        return rect;
    }

    private static Font? LoadFont(string path) =>
        ResourceLoader.Exists(path) ? ResourceLoader.Load<Font>(path) : null;

    private static void Warn(string what, Exception e)
    {
        if (_warned) return;
        _warned = true;
        Log.Warn($"[{KleeMod.ModId}] reaction chart: {what} ({e.GetType().Name}: {e.Message}).");
    }
}

/// <summary>The button goes on when the run's top bar is set up.</summary>
[HarmonyPatch(typeof(NTopBar), nameof(NTopBar.Initialize))]
internal static class NTopBar_Initialize_ReactionChart_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NTopBar __instance) => ReactionChart.AddButton(__instance);
}
