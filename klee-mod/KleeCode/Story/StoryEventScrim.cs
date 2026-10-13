using System;
using System.Linq;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Events;

namespace KleeMod.Story;

/// <summary>
/// THE STORY PAGE'S TEXT SCRIM (owner, 2026-10-13: "the event has a yellow
/// title and the text is in white, over a white-blue background that's hard
/// to make out").
///
/// HOW THE BASE GAME KEEPS EVENT TEXT READABLE. Its layout
/// (<c>scenes/events/default_event_layout.tscn</c>) has no scrim at all: a
/// full-screen <c>Portrait</c>, then the title and description in a column
/// that starts just left of centre and runs right, with only a soft drop
/// shadow (black at 50%, offset 3,2, no outline). The readability is in the
/// ART: every base event picture is painted dark, subject on the left, an
/// empty dark field on the right where the text lands (decoded from the
/// pack: the text column's mean luminance is 0.00 to 0.13 across Wellspring,
/// Sunken Statue, Tea Master, Trial and six others).
///
/// OUR PORTRAITS ARE CARD ART, painted bright for a card frame (the same
/// column measures 0.35 to 0.81 across the six story portraits). So the
/// story page adds what base art carries in itself: a dark field on the
/// right, as a horizontal gradient laid over the portrait and under the
/// text. The text keeps base's own colours and shadow untouched.
///
/// The numbers live here, free of Godot, so the suite can read them; the
/// node is built by <see cref="NEventLayout_InitializeVisuals_StoryScrim_Patch"/>.
/// </summary>
public static class StoryEventScrim
{
    public const string NodeName = "StoryTextScrim";

    /// <summary>Dark navy-black, the tone of base event fields.</summary>
    public static readonly float[] Rgb = { 0.02f, 0.025f, 0.05f };

    /// <summary>
    /// (offset across the screen, alpha). Clear over the left third where
    /// the picture's subject shows, full by 0.46 -- the text column starts
    /// at 0.485 of the layout (centre minus 38 px of 2560). At 0.82 a white
    /// field (1.0) drops to 0.18 and the brightest story portrait's column
    /// (0.81) to 0.15, inside base's range.
    /// </summary>
    public static readonly (float Offset, float Alpha)[] Stops =
    {
        (0.00f, 0.00f),
        (0.28f, 0.00f),
        (0.46f, 0.82f),
        (1.00f, 0.82f),
    };

    /// <summary>The column's luminance under the scrim's full alpha.</summary>
    public static float Dimmed(float luminance) => luminance * (1f - Stops.Max(s => s.Alpha));
}

[HarmonyPatch(typeof(NEventLayout), "InitializeVisuals")]
internal static class NEventLayout_InitializeVisuals_StoryScrim_Patch
{
    [HarmonyPostfix]
    private static void Postfix(NEventLayout __instance, EventModel ____event, TextureRect? ____portrait)
    {
        if (____event is not StoryEventModel || ____portrait == null) return;
        try
        {
            if (__instance.GetNodeOrNull(StoryEventScrim.NodeName) != null) return;
            var scrim = Build();
            __instance.AddChild(scrim);
            // Directly over the picture, under the VFX and the text column.
            __instance.MoveChild(scrim, ____portrait.GetIndex() + 1);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: text scrim not added: {e.Message}");
        }
    }

    private static TextureRect Build()
    {
        var rgb = StoryEventScrim.Rgb;
        var gradient = new Gradient
        {
            Offsets = StoryEventScrim.Stops.Select(s => s.Offset).ToArray(),
            Colors = StoryEventScrim.Stops.Select(s => new Color(rgb[0], rgb[1], rgb[2], s.Alpha)).ToArray(),
        };
        var rect = new TextureRect
        {
            Name = StoryEventScrim.NodeName,
            Texture = new GradientTexture2D
            {
                Gradient = gradient,
                Width = 256,
                Height = 4,
                FillFrom = new Vector2(0f, 0f),
                FillTo = new Vector2(1f, 0f),
            },
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        rect.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        // The layout sits 39 px up the screen (its scene's offset_top and
        // offset_bottom); reach the screen's bottom edge as VfxContainer does.
        rect.OffsetBottom = 39f;
        return rect;
    }
}
