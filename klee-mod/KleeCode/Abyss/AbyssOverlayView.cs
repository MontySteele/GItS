using System;
using System.Collections.Generic;
using Godot;

namespace KleeMod.Abyss;

/// <summary>What the Blessing screen draws, as plain strings and textures.
/// The game glue fills it from <see cref="AbyssOverlayContent"/>; the render
/// rig fills it from the same strings and the art files.</summary>
public sealed class AbyssOverlayViewData
{
    public string Title = "";
    public string Whisper = "";
    public string WholeRunTag = "";
    public string IfPassedLabel = "";
    public string BlessingsLabel = "";
    public string ShadowsLabel = "";
    public List<Card> Cards = new();
    public List<StripIcon> Blessings = new();
    public List<StripIcon> Shadows = new();

    public sealed class Card
    {
        public string BlessingName = "";
        public string BlessingText = "";
        public string ShadowName = "";
        public string ShadowText = "";
        public Texture2D? BlessingIcon;
        public Texture2D? ShadowIcon;
    }

    public sealed class StripIcon
    {
        public string Name = "";
        public string Text = "";
        public Texture2D? Icon;
    }
}

/// <summary>The game's fonts, handed in (the game's Kreon in the run; the rig
/// loads the same files from the game's pack). Null falls back to the
/// theme's.</summary>
public sealed class AbyssOverlayFonts
{
    public Font? Bold;
    public Font? Regular;
}

/// <summary>
/// THE BLESSING SCREEN'S NODES (Godot only: no game type, so the render rig in
/// <c>tools/abyss_overlay_rig</c> compiles this same file). A full-screen
/// modal over the Ancient's room: a darkened backdrop, the title and the
/// whisper line, three tall cards side by side and, top right, the strip of
/// Blessings taken and Shadows in force.
///
/// A CARD: a cream upper half (the Blessing icon in a gold diamond, its name,
/// its text, a "Whole run" tag) over a dark lower band with a crimson edge
/// ("If passed", the Shadow's badge, name and text). Text is never shrunk:
/// every text node fits its content, so a long text makes the card taller,
/// and <see cref="EqualizeSections"/> gives the three upper halves one height
/// so the cream/dark line runs straight across.
///
/// THE CLICKABLE is made by the caller (<c>makeHit</c>): the game's
/// <c>NClickableControl</c> in the run, so hover, controller focus and
/// <c>ForceClick</c> are the game's own; a plain control in the rig. It is the
/// card slot's top child, the size of the card, and draws nothing.
/// </summary>
public sealed class AbyssOverlayView
{
    public const string RootName = "KleeModAbyssBlessingOverlay";

    /// <summary>The bridge's contract: the clickable of card i is named
    /// this.</summary>
    public static string CardNodeName(int index) => $"AbyssCard{index}";

    // ---- Measures, at 1920x1080 --------------------------------------------
    internal const float CardWidth = 400f;
    internal const float CardGap = 44f;
    internal const float Lift = 14f;
    internal const int TitleSize = 54;
    internal const int WhisperSize = 26;
    internal const int NameSize = 30;
    /// <summary>The card text: the Ancient option button's 24 (the base card
    /// description is 21), and never auto-shrunk.</summary>
    internal const int BodySize = 24;
    internal const int SmallSize = 20;
    internal const int ResultSize = 30;
    internal const float IconSize = 76f;
    internal const float DiamondSize = 110f;
    internal const float BadgeSize = 48f;
    internal const float StripIconSize = 48f;

    // ---- Palette: the game's (StsColors) and the screenshot's cream --------
    public static readonly Color Cream = new("FFF6E2");
    public static readonly Color Gold = new("EFC851");
    public static readonly Color PanelCream = new("F2E4C4");
    public static readonly Color PanelCreamEdge = new("C9A65A");
    public static readonly Color InkDark = new("3A2A18");
    public static readonly Color InkName = new("2A1C0E");
    public static readonly Color DiamondFill = new("E7D3A6");
    public static readonly Color DiamondEdge = new("B8913E");
    public static readonly Color ShadowBand = new("17131C");
    public static readonly Color Crimson = new("B3263A");
    public static readonly Color CrimsonText = new("F06A6A");
    public static readonly Color FocusGlow = new("78FFFEC0");
    public static readonly Color Backdrop = new(0f, 0f, 0f, 0.78f);

    public Control Root { get; }

    private readonly List<CardNodes> _cards = new();
    private readonly Label _result;
    private readonly List<(Control Node, AbyssOverlayViewData.StripIcon Data)> _strip = new();

    public IReadOnlyList<(Control Node, AbyssOverlayViewData.StripIcon Data)> StripIcons => _strip;

    public int CardCount => _cards.Count;

    public Control Hit(int index) => _cards[index].Hit;

    /// <summary>Where co-op vote markers go, under card i's text.</summary>
    public Control VoteSlot(int index) => _cards[index].VoteSlot;

    private sealed class CardNodes
    {
        public MarginContainer Slot = null!;
        public Control Hit = null!;
        public Panel Outline = null!;
        public PanelContainer Upper = null!;
        public Control VoteSlot = null!;
        public bool Focused;
        public bool Chosen;
        public Tween? Tween;
    }

    private AbyssOverlayView(Control root, Label result)
    {
        Root = root;
        _result = result;
    }

    public static AbyssOverlayView Build(
        AbyssOverlayViewData data, AbyssOverlayFonts fonts, Func<int, Control> makeHit)
    {
        var root = new Control
        {
            Name = RootName,
            MouseFilter = Control.MouseFilterEnum.Stop,
        };
        root.SetAnchorsPreset(Control.LayoutPreset.FullRect);

        var backdrop = new ColorRect { Color = Backdrop, MouseFilter = Control.MouseFilterEnum.Ignore };
        backdrop.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        root.AddChild(backdrop);

        var center = new CenterContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        center.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        // The run's top bar owns the top ~80 px.
        center.OffsetTop = 70f;
        root.AddChild(center);

        var column = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        column.AddThemeConstantOverride("separation", 10);
        center.AddChild(column);

        var title = MakeLabel(data.Title, fonts.Bold, TitleSize, Cream);
        title.HorizontalAlignment = HorizontalAlignment.Center;
        title.AddThemeColorOverride("font_outline_color", new Color(0.12f, 0.08f, 0.05f));
        title.AddThemeConstantOverride("outline_size", 10);
        column.AddChild(title);

        var whisper = MakeLabel(data.Whisper, fonts.Regular, WhisperSize, Gold);
        whisper.HorizontalAlignment = HorizontalAlignment.Center;
        column.AddChild(whisper);

        column.AddChild(new Control { CustomMinimumSize = new Vector2(0, 18), MouseFilter = Control.MouseFilterEnum.Ignore });

        var row = new HBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore, Alignment = BoxContainer.AlignmentMode.Center };
        row.AddThemeConstantOverride("separation", (int)CardGap);
        column.AddChild(row);

        var result = MakeLabel("", fonts.Bold, ResultSize, Gold);
        result.HorizontalAlignment = HorizontalAlignment.Center;
        result.AddThemeColorOverride("font_outline_color", new Color(0, 0, 0, 0.8f));
        result.AddThemeConstantOverride("outline_size", 8);
        result.CustomMinimumSize = new Vector2(0, ResultSize + 16);
        result.Modulate = new Color(1, 1, 1, 0);
        column.AddChild(result);

        var view = new AbyssOverlayView(root, result);
        for (var i = 0; i < data.Cards.Count; i++)
        {
            view._cards.Add(BuildCard(row, data, data.Cards[i], fonts, makeHit(i), i));
        }

        // Left/right walk between the cards, wrapping, the way the game's
        // option list wraps up/down.
        for (var i = 0; i < view._cards.Count; i++)
        {
            var hit = view._cards[i].Hit;
            var left = view._cards[(i + view._cards.Count - 1) % view._cards.Count].Hit;
            var right = view._cards[(i + 1) % view._cards.Count].Hit;
            hit.FocusNeighborLeft = hit.GetPathTo(left);
            hit.FocusNeighborRight = hit.GetPathTo(right);
            hit.FocusNeighborTop = hit.GetPathTo(hit);
            hit.FocusNeighborBottom = hit.GetPathTo(hit);
        }

        if (data.Blessings.Count > 0 || data.Shadows.Count > 0)
        {
            root.AddChild(view.BuildStrip(data, fonts));
        }
        return view;
    }

    private static CardNodes BuildCard(
        HBoxContainer row, AbyssOverlayViewData data, AbyssOverlayViewData.Card card,
        AbyssOverlayFonts fonts, Control hit, int index)
    {
        var nodes = new CardNodes();
        // The slot's top margin is the lift's headroom: a hover moves it to
        // the bottom, so the card rises without the row moving.
        var slot = new MarginContainer
        {
            Name = $"AbyssCardSlot{index}",
            CustomMinimumSize = new Vector2(CardWidth, 0),
            MouseFilter = Control.MouseFilterEnum.Ignore,
            SizeFlagsVertical = Control.SizeFlags.Fill,
        };
        SetLift(slot, 0f);
        row.AddChild(slot);
        nodes.Slot = slot;

        var body = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        body.AddThemeConstantOverride("separation", 0);
        slot.AddChild(body);

        // ---- Upper half: the Blessing ----
        var upper = new PanelContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        upper.AddThemeStyleboxOverride("panel", Box(PanelCream, PanelCreamEdge, 3, 3, 3, 0, 14, 14, 0, 0, 22, 20));
        body.AddChild(upper);
        nodes.Upper = upper;

        var up = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        up.AddThemeConstantOverride("separation", 10);
        upper.AddChild(up);

        var diamond = new Control
        {
            CustomMinimumSize = new Vector2(0, DiamondSize * 1.42f + 6f),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        up.AddChild(diamond);
        var frameSide = DiamondSize;
        var holderWidth = CardWidth - 44f;
        var frame = new Panel
        {
            Size = new Vector2(frameSide, frameSide),
            Position = new Vector2((holderWidth - frameSide) / 2f, (DiamondSize * 1.42f + 6f - frameSide) / 2f),
            PivotOffset = new Vector2(frameSide / 2f, frameSide / 2f),
            Rotation = Mathf.Pi / 4f,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        frame.AddThemeStyleboxOverride("panel", Box(DiamondFill, DiamondEdge, 4, 4, 4, 4, 6, 6, 6, 6, 0, 0));
        diamond.AddChild(frame);
        var inner = new Panel
        {
            Size = new Vector2(frameSide - 18f, frameSide - 18f),
            Position = new Vector2((holderWidth - frameSide + 18f) / 2f, (DiamondSize * 1.42f + 6f - frameSide + 18f) / 2f),
            PivotOffset = new Vector2((frameSide - 18f) / 2f, (frameSide - 18f) / 2f),
            Rotation = Mathf.Pi / 4f,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        inner.AddThemeStyleboxOverride("panel", Box(new Color(0, 0, 0, 0), new Color(DiamondEdge, 0.55f), 2, 2, 2, 2, 4, 4, 4, 4, 0, 0));
        diamond.AddChild(inner);
        var icon = new TextureRect
        {
            Texture = card.BlessingIcon,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            Size = new Vector2(IconSize, IconSize),
            Position = new Vector2((holderWidth - IconSize) / 2f, (DiamondSize * 1.42f + 6f - IconSize) / 2f),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        diamond.AddChild(icon);

        var name = MakeLabel(card.BlessingName, fonts.Bold, NameSize, InkName);
        name.HorizontalAlignment = HorizontalAlignment.Center;
        name.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        up.AddChild(name);

        up.AddChild(MakeText(card.BlessingText, fonts, BodySize, InkDark, centered: true));

        // The tag sits at the foot of the cream half, whatever the text's length.
        up.AddChild(new Control { SizeFlagsVertical = Control.SizeFlags.ExpandFill, MouseFilter = Control.MouseFilterEnum.Ignore });
        var tagRow = new CenterContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        var tag = new PanelContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        tag.AddThemeStyleboxOverride("panel", Box(new Color("5A4326"), new Color("5A4326"), 0, 0, 0, 0, 10, 10, 10, 10, 12, 3));
        tag.AddChild(MakeLabel(data.WholeRunTag, fonts.Bold, SmallSize - 2, PanelCream));
        tagRow.AddChild(tag);
        up.AddChild(tagRow);

        // ---- Lower half: the Shadow if passed ----
        var lower = new PanelContainer
        {
            MouseFilter = Control.MouseFilterEnum.Ignore,
            SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        };
        lower.AddThemeStyleboxOverride("panel", Box(ShadowBand, Crimson, 3, 5, 3, 3, 0, 0, 14, 14, 22, 18));
        body.AddChild(lower);

        var low = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        low.AddThemeConstantOverride("separation", 8);
        lower.AddChild(low);

        var passed = MakeLabel(data.IfPassedLabel.ToUpperInvariant(), fonts.Bold, SmallSize, CrimsonText);
        passed.HorizontalAlignment = HorizontalAlignment.Center;
        low.AddChild(passed);

        var shadowRow = new HBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore, Alignment = BoxContainer.AlignmentMode.Center };
        shadowRow.AddThemeConstantOverride("separation", 10);
        shadowRow.AddChild(new TextureRect
        {
            Texture = card.ShadowIcon,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            CustomMinimumSize = new Vector2(BadgeSize, BadgeSize),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        });
        var shadowName = MakeLabel(card.ShadowName, fonts.Bold, NameSize - 2, Gold);
        shadowName.VerticalAlignment = VerticalAlignment.Center;
        shadowRow.AddChild(shadowName);
        low.AddChild(shadowRow);

        low.AddChild(MakeText(card.ShadowText, fonts, BodySize, Cream, centered: true));

        var votes = new HBoxContainer
        {
            Name = "Votes",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Alignment = BoxContainer.AlignmentMode.Center,
            CustomMinimumSize = new Vector2(0, 40),
            SizeFlagsVertical = Control.SizeFlags.ShrinkEnd | Control.SizeFlags.Expand,
        };
        votes.AddThemeConstantOverride("separation", 6);
        low.AddChild(votes);

        // ---- Outline (focus / chosen) and the clickable, on top ----
        var outline = new Panel { MouseFilter = Control.MouseFilterEnum.Ignore, Modulate = new Color(1, 1, 1, 0) };
        outline.AddThemeStyleboxOverride("panel", Box(new Color(0, 0, 0, 0), FocusGlow, 4, 4, 4, 4, 16, 16, 16, 16, 0, 0, expand: 5));
        slot.AddChild(outline);

        hit.Name = CardNodeName(index);
        hit.MouseFilter = Control.MouseFilterEnum.Stop;
        hit.FocusMode = Control.FocusModeEnum.All;
        slot.AddChild(hit);

        nodes.Hit = hit;
        nodes.Outline = outline;
        nodes.VoteSlot = votes;
        return nodes;
    }

    private Control BuildStrip(AbyssOverlayViewData data, AbyssOverlayFonts fonts)
    {
        var panel = new PanelContainer { Name = "AbyssStrip", MouseFilter = Control.MouseFilterEnum.Ignore };
        panel.AddThemeStyleboxOverride("panel", Box(new Color(0.06f, 0.05f, 0.08f, 0.82f), new Color(Gold, 0.55f), 2, 2, 2, 2, 10, 10, 10, 10, 16, 10));
        panel.SetAnchorsPreset(Control.LayoutPreset.TopRight);
        panel.GrowHorizontal = Control.GrowDirection.Begin;
        panel.OffsetRight = -28f;
        panel.OffsetLeft = -28f;
        panel.OffsetTop = 112f;

        var col = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        col.AddThemeConstantOverride("separation", 6);
        panel.AddChild(col);
        AddStripRow(col, data.BlessingsLabel, data.Blessings, fonts, Gold);
        AddStripRow(col, data.ShadowsLabel, data.Shadows, fonts, CrimsonText);
        return panel;
    }

    private void AddStripRow(
        VBoxContainer col, string label, List<AbyssOverlayViewData.StripIcon> icons,
        AbyssOverlayFonts fonts, Color colour)
    {
        if (icons.Count == 0) return;
        var row = new HBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore };
        row.AddThemeConstantOverride("separation", 6);
        col.AddChild(row);
        var name = MakeLabel(label, fonts.Bold, SmallSize, colour);
        name.CustomMinimumSize = new Vector2(104, 0);
        name.VerticalAlignment = VerticalAlignment.Center;
        row.AddChild(name);
        foreach (var entry in icons)
        {
            var node = new TextureRect
            {
                Texture = entry.Icon,
                ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
                CustomMinimumSize = new Vector2(StripIconSize, StripIconSize),
                // Hover only: the strip never enters the controller's walk.
                MouseFilter = Control.MouseFilterEnum.Stop,
                FocusMode = Control.FocusModeEnum.None,
            };
            row.AddChild(node);
            _strip.Add((node, entry));
        }
    }

    // ---- State -------------------------------------------------------------

    /// <summary>Hover or controller focus: the card lifts and is outlined.</summary>
    public void SetCardFocused(int index, bool focused)
    {
        if (index < 0 || index >= _cards.Count) return;
        var card = _cards[index];
        if (card.Focused == focused) return;
        card.Focused = focused;
        Animate(card);
    }

    /// <summary>This player's pick (or vote): outlined in gold until it
    /// changes.</summary>
    public void SetCardChosen(int index)
    {
        for (var i = 0; i < _cards.Count; i++)
        {
            var chosen = i == index;
            if (_cards[i].Chosen == chosen) continue;
            _cards[i].Chosen = chosen;
            Animate(_cards[i]);
        }
    }

    /// <summary>After the pick: the others grey out.</summary>
    public void DimAllBut(int index)
    {
        for (var i = 0; i < _cards.Count; i++)
        {
            _cards[i].Slot.Modulate = i == index ? Colors.White : new Color(0.6f, 0.6f, 0.6f, 0.75f);
        }
    }

    public void ShowResult(string line)
    {
        _result.Text = line;
        var tween = Root.CreateTween();
        tween.TweenProperty(_result, "modulate:a", 1f, 0.2);
    }

    public void FadeIn()
    {
        Root.Modulate = new Color(1, 1, 1, 0);
        var tween = Root.CreateTween();
        tween.TweenProperty(Root, "modulate:a", 1f, 0.25);
    }

    /// <summary>Fade the whole screen out; <paramref name="done"/> runs when
    /// it has.</summary>
    public void FadeOut(double seconds, Action done)
    {
        var tween = Root.CreateTween();
        tween.TweenProperty(Root, "modulate:a", 0f, seconds);
        tween.TweenCallback(Callable.From(done));
    }

    /// <summary>One height for the three cream halves, so the line between
    /// Blessing and Shadow runs straight across. Run after a layout pass
    /// (the texts' heights depend on their width).</summary>
    public void EqualizeSections()
    {
        var tallest = 0f;
        foreach (var c in _cards)
        {
            c.Upper.CustomMinimumSize = Vector2.Zero;
        }
        foreach (var c in _cards)
        {
            tallest = Math.Max(tallest, c.Upper.GetCombinedMinimumSize().Y);
        }
        foreach (var c in _cards)
        {
            c.Upper.CustomMinimumSize = new Vector2(0, tallest);
        }
    }

    /// <summary>Equalize on each of the next few frames, until the texts have
    /// settled at their width.</summary>
    public void EqualizeOverFrames(int frames = 4)
    {
        var tree = Root.GetTree();
        if (tree == null) return;
        var left = frames;
        void Step()
        {
            if (!GodotObject.IsInstanceValid(Root) || --left < 0)
            {
                tree.ProcessFrame -= Step;
                return;
            }
            EqualizeSections();
        }
        tree.ProcessFrame += Step;
    }

    private void Animate(CardNodes card)
    {
        card.Tween?.Kill();
        var lifted = card.Focused ? Lift : 0f;
        var outlineA = card.Focused || card.Chosen ? 1f : 0f;
        var outline = card.Chosen ? Gold : FocusGlow;
        if (card.Outline.GetThemeStylebox("panel") is StyleBoxFlat box) box.BorderColor = outline;
        var from = card.Slot.GetThemeConstant("margin_bottom");
        card.Tween = card.Slot.CreateTween().SetParallel();
        card.Tween.TweenMethod(Callable.From<float>(v => SetLift(card.Slot, v)), (float)from, lifted, 0.12)
            .SetEase(Tween.EaseType.Out).SetTrans(Tween.TransitionType.Quad);
        card.Tween.TweenProperty(card.Outline, "modulate:a", outlineA, 0.12);
    }

    private static void SetLift(MarginContainer slot, float lift)
    {
        slot.AddThemeConstantOverride("margin_top", (int)(Lift - lift));
        slot.AddThemeConstantOverride("margin_bottom", (int)lift);
    }

    // ---- Builders ------------------------------------------------------------

    private static Label MakeLabel(string text, Font? font, int size, Color colour)
    {
        var label = new Label { Text = text, MouseFilter = Control.MouseFilterEnum.Ignore };
        if (font != null) label.AddThemeFontOverride("font", font);
        label.AddThemeFontSizeOverride("font_size", size);
        label.AddThemeColorOverride("font_color", colour);
        return label;
    }

    /// <summary>A text that grows to fit (never shrinks its font).</summary>
    private static RichTextLabel MakeText(string text, AbyssOverlayFonts fonts, int size, Color colour, bool centered)
    {
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
        if (fonts.Regular != null) label.AddThemeFontOverride("normal_font", fonts.Regular);
        if (fonts.Bold != null) label.AddThemeFontOverride("bold_font", fonts.Bold);
        label.AddThemeFontSizeOverride("normal_font_size", size);
        label.AddThemeFontSizeOverride("bold_font_size", size);
        label.AddThemeColorOverride("default_color", colour);
        label.AddThemeConstantOverride("line_separation", -2);
        return label;
    }

    private static StyleBoxFlat Box(
        Color bg, Color border, int left, int top, int right, int bottom,
        int rTopLeft, int rTopRight, int rBottomRight, int rBottomLeft,
        int padX, int padY, int expand = 0)
    {
        var box = new StyleBoxFlat
        {
            BgColor = bg,
            BorderColor = border,
            BorderWidthLeft = left,
            BorderWidthTop = top,
            BorderWidthRight = right,
            BorderWidthBottom = bottom,
            CornerRadiusTopLeft = rTopLeft,
            CornerRadiusTopRight = rTopRight,
            CornerRadiusBottomRight = rBottomRight,
            CornerRadiusBottomLeft = rBottomLeft,
            ContentMarginLeft = padX,
            ContentMarginRight = padX,
            ContentMarginTop = padY,
            ContentMarginBottom = padY,
            AntiAliasing = true,
        };
        if (expand > 0)
        {
            box.ExpandMarginLeft = expand;
            box.ExpandMarginRight = expand;
            box.ExpandMarginTop = expand;
            box.ExpandMarginBottom = expand;
        }
        return box;
    }
}
