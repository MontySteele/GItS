using System;
using Godot;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod.Vfx;

/// <summary>
/// THE FACE OF FURINA'S TWO HUD COUNTERS, the Fanfare gauge
/// (<see cref="FanfareCounter"/>) and the Drained counter
/// (<see cref="DrainedCounter"/>).
///
/// THE ASK (the 2026-10-11 playtest, on the gold and red numbers centred on
/// the busy round glyphs: "that's not really legible, either"). The ruled
/// design, [USER]: "Yep, sounds good!":
/// <list type="bullet">
/// <item>the number takes the base game's style for a number over art, a
/// cream fill with a dark outline and a soft drop shadow;</item>
/// <item>it is larger and sits in the circle's bottom-right corner, where
/// the base game puts a power icon's amount;</item>
/// <item>the colour that tells the two apart moves off the number onto a
/// thin ring around the circle, red for Drain and gold for Fanfare;</item>
/// <item>Fanfare at 0 is the same style with a grey fill, not faded gold.
/// </item>
/// </list>
///
/// THE STYLE IS THE POWER ICON'S AMOUNT LABEL, <c>%AmountLabel</c> in
/// <c>res://scenes/combat/power.tscn</c> (the 0.111.0 pck, lines 47-66):
/// font <see cref="FontPath"/> at <see cref="AmountFontSize"/>, outline
/// <see cref="AmountOutlineSize"/> in <see cref="OutlineColour"/>, shadow
/// <see cref="ShadowColour"/> at (<see cref="AmountShadowOffset"/>,
/// <see cref="AmountShadowOffset"/>), right-aligned in the rect
/// <see cref="AmountRectOnIcon"/> over a <see cref="PowerIconSide"/>-px icon.
/// The HP bar's "75/78" (<c>health_bar.tscn</c> <c>%HpLabel</c>) and the
/// energy orb's "1/3" are the same recipe: the cream fill
/// (<c>StsColors.cream</c>), a dark outline, a translucent black shadow.
/// The counter is a power icon drawn at the star counter's size, so every
/// number scales by <see cref="Scale"/> = side / 40: the same proportions,
/// larger.
///
/// RING, NOT OUTLINE. A red or gold OUTLINE on a cream fill is a light
/// edge on light text (cream on #EFC851 is about 1.4:1), which is the
/// legibility the ask is about. The outline stays the power label's dark
/// brown and the colour goes on a ring (<see cref="RingWidth"/>).
/// </summary>
public static class FurinaCounterFace
{
    /// <summary>The power icon's side in <c>power.tscn</c> (<c>Icon</c>,
    /// 40 x 40).</summary>
    public const float PowerIconSide = 40f;

    /// <summary><c>%AmountLabel</c>'s <c>font_size</c>.</summary>
    public const int AmountFontSize = 18;

    /// <summary><c>%AmountLabel</c>'s <c>outline_size</c>.</summary>
    public const int AmountOutlineSize = 10;

    /// <summary><c>%AmountLabel</c>'s <c>shadow_offset_x</c> and
    /// <c>shadow_offset_y</c>.</summary>
    public const int AmountShadowOffset = 3;

    /// <summary><c>%AmountLabel</c>'s rect on the 40-px icon: offsets
    /// left -56, top 21, right 44, bottom 44, right-aligned and vertically
    /// centred, so the number's right edge overhangs the icon by 4 px and
    /// its middle sits at 32.5 of 40, the bottom-right corner.</summary>
    public static readonly Rect2 AmountRectOnIcon =
        new(new Vector2(-56f, 21f), new Vector2(100f, 23f));

    /// <summary><c>%AmountLabel</c>'s font.</summary>
    public const string FontPath = "res://themes/kreon_bold_glyph_space_one.tres";

    /// <summary><c>%AmountLabel</c>'s <c>font_outline_color</c>.</summary>
    public static readonly Color OutlineColour = new(0.12f, 0.10208f, 0.0816f, 1f);

    /// <summary><c>%AmountLabel</c>'s <c>font_shadow_color</c>.</summary>
    public static readonly Color ShadowColour = new(0f, 0f, 0f, 0.188235f);

    /// <summary>The fill: the cream every base number over art uses
    /// (<c>StsColors.cream</c>, #FFF6E2).</summary>
    public static Color Fill => StsColors.cream;

    /// <summary>The grey fill of an empty Fanfare gauge
    /// (<c>StsColors.lightGray</c>, 0.75 grey).</summary>
    public static Color EmptyFill => StsColors.lightGray;

    /// <summary>How much larger than a power icon the counter is.</summary>
    public static float Scale(float side) => side / PowerIconSide;

    public static int FontSize(float side) =>
        Mathf.RoundToInt(AmountFontSize * Scale(side));

    public static int OutlineSize(float side) =>
        Mathf.RoundToInt(AmountOutlineSize * Scale(side));

    public static int ShadowOffset(float side) =>
        Mathf.RoundToInt(AmountShadowOffset * Scale(side));

    /// <summary>The number's rect on a counter of this side. Pure.</summary>
    public static Rect2 AmountRect(float side)
    {
        var k = Scale(side);
        return new Rect2(AmountRectOnIcon.Position * k,
                         AmountRectOnIcon.Size * k);
    }

    /// <summary>The ring's width: one 32nd of the side, never under 2 px
    /// (4 px on the 128-px star-counter square).</summary>
    public static int RingWidth(float side) =>
        Math.Max(2, Mathf.RoundToInt(side / 32f));

    private static bool _warnedFont;

    /// <summary>Restyle <see cref="SparkCounter.Build"/>'s centred count as
    /// the power amount label, scaled to <paramref name="side"/>, and put a
    /// ring of <paramref name="ring"/> round the glyph, under the number.
    /// </summary>
    public static void Dress(Control root, float side, Color ring)
    {
        if (root.GetNodeOrNull<Label>("Count") is not { } count) return;

        var rect = AmountRect(side);
        count.Position = rect.Position;
        count.Size = rect.Size;
        count.HorizontalAlignment = HorizontalAlignment.Right;
        count.VerticalAlignment = VerticalAlignment.Center;
        count.ClipText = false;

        if (LoadFont() is { } font)
        {
            count.AddThemeFontOverride(ThemeConstants.Label.Font, font);
        }
        count.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       FontSize(side));
        count.AddThemeConstantOverride(ThemeConstants.Label.OutlineSize,
                                       OutlineSize(side));
        count.AddThemeColorOverride(ThemeConstants.Label.FontOutlineColor,
                                    OutlineColour);
        count.AddThemeColorOverride(ThemeConstants.Label.FontShadowColor,
                                    ShadowColour);
        count.AddThemeConstantOverride("shadow_offset_x", ShadowOffset(side));
        count.AddThemeConstantOverride("shadow_offset_y", ShadowOffset(side));
        count.AddThemeColorOverride(ThemeConstants.Label.FontColor, Fill);

        var box = new StyleBoxFlat
        {
            DrawCenter = false,
            BorderColor = ring,
            AntiAliasing = true,
        };
        box.SetBorderWidthAll(RingWidth(side));
        box.SetCornerRadiusAll(Mathf.CeilToInt(side / 2f));
        var panel = new Panel
        {
            Name = "Ring",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            Position = Vector2.Zero,
            Size = new Vector2(side, side),
        };
        panel.AddThemeStyleboxOverride("panel", box);
        root.AddChildSafely(panel);
        // Over the glyph, under the number.
        root.MoveChild(panel, count.GetIndex());
    }

    /// <summary>Paint the number: its fill only. The outline, shadow and
    /// ring are <see cref="Dress"/>'s and never change.</summary>
    public static void SetFill(Control root, Color fill)
    {
        if (root.GetNodeOrNull<Label>("Count") is { } count)
        {
            count.AddThemeColorOverride(ThemeConstants.Label.FontColor, fill);
        }
    }

    /// <summary>Loaded fresh at each build, never cached across a scene
    /// (`EB-222`); a font that will not load leaves the theme's.</summary>
    private static Font? LoadFont()
    {
        try
        {
            var font = ResourceLoader.Load<Font>(FontPath);
            if (font != null && GodotObject.IsInstanceValid(font)) return font;
        }
        catch (Exception e)
        {
            if (!_warnedFont)
            {
                _warnedFont = true;
                Log.Warn($"[{KleeMod.ModId}] counter face: {FontPath} would "
                       + $"not load ({e.GetType().Name}: {e.Message}); the "
                       + "theme's font stands in.");
            }
        }
        return null;
    }
}
