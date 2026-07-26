using System;
using System.Collections.Generic;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// On-creature tracked gauges (animation sprint 1, Track C): one shared
/// script-less scene (res://shared/gauge.tscn), instantiated once per
/// applicable meter — Klee's Burst, Furina's Burst, Kokomi's Burst and her
/// uncapped Charge counter. Bridge skeleton follows
/// HexaghostVisualsBridge (dictionary + IsInstanceValid staleness + lazy
/// re-Setup + instantiate into NCombatRoom.CombatVfxContainer; pattern
/// mirrored from the Downfall reference, not copied).
///
/// Deviations from the reference, both forced by house rules:
/// - The reference scene carries a C# script whose _Process re-anchors the
///   display to its creature every frame. Our scenes are script-less and the
///   sprint plan bans _Process polling, so tracking is a RemoteTransform2D
///   child of the creature node pushing its global position into the gauge
///   root — engine-side transform propagation, no per-frame script.
/// - C1's "exposed knobs" (max, fill color, threshold, anchor offset) cannot
///   be scene exports without a script; they live in <see cref="GaugeSpec"/>
///   here and the bridge applies them at Setup/Refresh.
///
/// Visuals read state, never own it: Refresh re-reads the authoritative
/// resource (KleeBurstResource / EncoreResource) and redraws. The previous
/// value kept in node metadata exists only to detect threshold CROSSINGS for
/// the flash; it is display state, not game state.
/// </summary>
public static class GaugeBridge
{
    /// <summary>
    /// The cross-character overhead Burst slot, in creature space.
    ///
    /// Animation sprint 2, C1 ruling: this anchor is a CONVENTION, not a
    /// per-character choice — the overhead slot means "Burst" for everybody,
    /// which is exactly why Encore was evicted from it. Both rigs clear it:
    /// Klee's tallest layer (the smoke plume) tops out ~-277 and Furina's
    /// combat box tops out at -280, so -300 clears both with room for the
    /// label. Measure any new character's rig before assuming it still fits.
    /// </summary>
    private static readonly Vector2 OverheadBurstAnchor = new(0f, -300f);

    /// <summary>
    /// A SECOND ROW, above the convention slot, for a character-specific
    /// resource that is not Burst. Kokomi's Charge is the first tenant.
    ///
    /// Above rather than below on purpose: the Burst slot is a cross-character
    /// convention and must not be evicted or shifted by a character who
    /// happens to carry a second meter, and everything below -300 is inside
    /// somebody's rig. Measure a new character's rig before assuming this row
    /// is clear for them too.
    /// </summary>
    private static readonly Vector2 SecondRowAnchor = new(0f, -340f);

    /// <summary>
    /// Per-character skin, applied by the bridge at Setup (C2). Skinning is
    /// parameter-driven against ONE scene rather than per-character scene
    /// variants; the variants remain the sanctioned fallback if a future skin
    /// outgrows what a script-less scene can carry by parameter alone. What a
    /// parameter CAN reach is every node property in shared/gauge.tscn:
    /// colours, sizes, visibility, and textures on %CapIcon.
    /// </summary>
    private sealed class GaugeSkin
    {
        public required Color FillColor { get; init; }

        public required Color TrackColor { get; init; }

        /// <summary>Ribbon/banner backing plate. Null leaves it hidden.</summary>
        public Color? RibbonColor { get; init; }

        /// <summary>pck-relative texture for the end cap. Null hides it.</summary>
        public string? CapIconPath { get; init; }
    }

    private sealed class GaugeSpec
    {
        public required string Key { get; init; }

        public required GaugeSkin Skin { get; init; }

        /// <summary>Anchor offset relative to the creature node's origin.</summary>
        public required Vector2 AnchorOffset { get; init; }

        /// <summary>
        /// Bar renders full at this many points (display only). NULL means the
        /// resource has no "full" at all -- the bar is hidden and the gauge
        /// renders as a bare counter. Kokomi's Charge is the case: it is
        /// uncapped and never spent, so a bar would sit pinned at maximum for
        /// most of a run while the true reading is "this only goes up". A
        /// meter that lies about its own ceiling is worse than no meter.
        /// </summary>
        public required int? VisualSpan { get; init; }

        /// <summary>Null for an unbounded buffer: label shows the raw count.</summary>
        public int? LabelMax { get; init; }

        public required Func<Creature, bool> AppliesTo { get; init; }

        public required Func<Creature, int> ReadValue { get; init; }

        /// <summary>(previous, current) -> threshold-crossing flash.</summary>
        public required Func<int, int, bool> ShouldFlash { get; init; }
    }

    private static readonly GaugeSpec[] Specs =
    {
        // Klee's Burst. Skin: fuse-and-bomb — a warm fuse burning along the
        // track toward the bomb cap, which is lit exactly when the meter is
        // castable.
        new()
        {
            Key = "burst",
            Skin = new GaugeSkin
            {
                FillColor = new Color(1.0f, 0.45f, 0.15f),
                TrackColor = new Color(0.08f, 0.07f, 0.1f, 0.82f),
                CapIconPath = "klee/powers/bomb.png",
            },
            AnchorOffset = OverheadBurstAnchor,
            VisualSpan = BurstConstants.KleeMax,
            LabelMax = BurstConstants.KleeMax,
            AppliesTo = creature => creature.Player?.Character is Klee,
            ReadValue = KleeBurstResource.AmountFor,
            ShouldFlash = (previous, current) =>
                previous < BurstConstants.KleeMax
                && current >= BurstConstants.KleeMax,
        },
        // Furina's Burst, at the SAME overhead slot. Skin: hydro ribbon —
        // a banner plate with swallow-tail ends, deliberately sharing its
        // visual language with the Salon stage's Encore ribbon (D3) so the two
        // hydro meters read as one family and neither reads as Klee's.
        new()
        {
            Key = "furina_burst",
            Skin = new GaugeSkin
            {
                FillColor = new Color(0.35f, 0.75f, 1.0f),
                TrackColor = new Color(0.06f, 0.13f, 0.2f, 0.85f),
                RibbonColor = new Color(0.11f, 0.24f, 0.36f, 0.9f),
            },
            AnchorOffset = OverheadBurstAnchor,
            VisualSpan = FurinaResourceConstants.BurstMax,
            LabelMax = FurinaResourceConstants.BurstMax,
            AppliesTo = FurinaResources.IsFurina,
            ReadValue = FurinaResources.Burst,
            ShouldFlash = (previous, current) =>
                previous < FurinaResourceConstants.BurstMax
                && current >= FurinaResourceConstants.BurstMax,
        },
        // Kokomi's Burst, same overhead slot. Skin: pearl — a pale
        // moon-on-water fill over a deep-trench track. She and Furina are both
        // hydro and must not be confusable, so Furina keeps the ribbon plate
        // (theatre banner) and Kokomi goes plain and cold; the two read as the
        // same family at a glance and as different characters on a look.
        new()
        {
            Key = "kokomi_burst",
            Skin = new GaugeSkin
            {
                FillColor = new Color(0.72f, 0.90f, 0.94f),
                TrackColor = new Color(0.05f, 0.16f, 0.21f, 0.85f),
                CapIconPath = "kokomi/powers/pearl.png",
            },
            AnchorOffset = OverheadBurstAnchor,
            VisualSpan = KokomiConstants.BurstMax,
            LabelMax = KokomiConstants.BurstMax,
            AppliesTo = KokomiResources.IsKokomi,
            ReadValue = KokomiResources.GetBurst,
            ShouldFlash = (previous, current) =>
                previous < KokomiConstants.BurstMax
                && current >= KokomiConstants.BurstMax,
        },
        // Kokomi's Charge, the second row. THE ONE GAUGE WITH NO BAR: Charge is
        // uncapped and never spent (ChargeResource.Spend is a documented
        // no-op), so there is no ceiling to draw against and no threshold to
        // cross. It renders as a bare climbing number, which is the honest
        // reading of the resource and also the neutral one -- a bar would
        // invent a target, and her whole design question is how long a player
        // is willing to keep banking with no target in sight.
        //
        // It has an ambient display AT ALL because it is the one number her
        // scaling cards read and none of them can show it on their face: the
        // Kurage pulse and the Garment rider are both computed at resolve
        // time from a bank the card never prints.
        new()
        {
            Key = "kokomi_charge",
            Skin = new GaugeSkin
            {
                FillColor = new Color(0.44f, 0.78f, 0.84f),
                TrackColor = new Color(0.05f, 0.16f, 0.21f, 0.0f),
            },
            AnchorOffset = SecondRowAnchor,
            VisualSpan = null,
            LabelMax = null,
            AppliesTo = KokomiResources.IsKokomi,
            ReadValue = KokomiResources.GetCharge,
            ShouldFlash = static (_, _) => false,
        },
        // NOTE: Encore has NO spec here. It was evicted from the overhead slot
        // by the C4 verdict (that slot is Burst, cross-character) and re-homes
        // as the ribbon under the Salon stage — see SalonVisualsBridge (D3).
        // Its refresh funnels are unchanged; only the display moved.
    };

    private const float BarFullWidth = 60f;
    private const string PreviousValueMeta = "kleemod_gauge_value";

    private static readonly
        TrackedDisplayBridge.Registry<(Player Player, string Key)> Displays = new();

    private static bool _warnedMissingScene;

    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        if (creature == null)
        {
            return;
        }

        foreach (var spec in Specs)
        {
            if (!spec.AppliesTo(creature))
            {
                continue;
            }

            DiscardDisplay(player, spec);

            var display = TrackedDisplayBridge.Spawn(
                combatRoom, "shared/gauge.tscn", ref _warnedMissingScene,
                "gauges disabled");
            if (display == null)
            {
                return;
            }

            ApplySkin(display, spec.Skin);
            TrackedDisplayBridge.Track(
                combatRoom, creature, display, spec.AnchorOffset);

            Displays.Set((player, spec.Key), display);
            RefreshDisplay(display, spec, creature, allowFlash: false);
        }
    }

    /// <summary>
    /// Re-read the authoritative value and redraw every gauge this creature
    /// owns. Call sites are the resource mutation funnels — enumerated in
    /// docs/archive/animation-sprint-1-log.md (Track C). If a future mutator bypasses
    /// the funnels, prefer wiring it through them; CustomResource.AmountChanged
    /// exists as an event-driven alternative if the funnels ever multiply.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (creature == null || player == null)
        {
            return;
        }

        foreach (var spec in Specs)
        {
            if (!spec.AppliesTo(creature))
            {
                continue;
            }

            var display = GetDisplay(player, spec);
            if (display == null)
            {
                // Stale or never built (mid-combat reload): rebuild in place,
                // reference-bridge idiom.
                if (NCombatRoom.Instance is not { } room)
                {
                    continue;
                }
                Setup(room, player);
                display = GetDisplay(player, spec);
                if (display == null)
                {
                    continue;
                }
            }

            RefreshDisplay(display, spec, creature, allowFlash: true);
        }
    }

    public static void DiscardDisplays(Player player)
    {
        foreach (var spec in Specs)
        {
            DiscardDisplay(player, spec);
        }
    }

    private static Node2D? GetDisplay(Player player, GaugeSpec spec) =>
        Displays.Get((player, spec.Key));

    private static void DiscardDisplay(Player player, GaugeSpec spec) =>
        Displays.Discard((player, spec.Key));

    /// <summary>
    /// C2's parameter-driven skinning. Every node this touches is optional in
    /// the scene, so an older pck missing the skin nodes still renders a
    /// working bar rather than throwing — same loud-but-degradable posture as
    /// the rest of the sprint's visual layer.
    /// </summary>
    private static void ApplySkin(Node2D display, GaugeSkin skin)
    {
        if (display.GetNodeOrNull<ColorRect>("%BarFill") is { } fill)
        {
            fill.Color = skin.FillColor;
        }

        if (display.GetNodeOrNull<ColorRect>("%BarBack") is { } back)
        {
            back.Color = skin.TrackColor;
        }

        foreach (var name in RibbonNodes)
        {
            if (display.GetNodeOrNull<ColorRect>(name) is not { } ribbon)
            {
                continue;
            }
            ribbon.Visible = skin.RibbonColor is not null;
            if (skin.RibbonColor is { } colour)
            {
                ribbon.Color = colour;
            }
        }

        if (display.GetNodeOrNull<TextureRect>("%CapIcon") is { } cap)
        {
            var texture = skin.CapIconPath is { } relative
                          && KleePck.Path(relative) is { } path
                ? ResourceLoader.Load<Texture2D>(path)
                : null;
            cap.Texture = texture;
            cap.Visible = texture != null;
        }
    }

    private static readonly string[] RibbonNodes =
        { "%Ribbon", "%RibbonTailL", "%RibbonTailR" };

    private static void RefreshDisplay(
        Node2D display, GaugeSpec spec, Creature creature, bool allowFlash)
    {
        int value = spec.ReadValue(creature);

        // A null span is a counter, not a meter: hide the track and the fill
        // rather than drawing a bar with no honest ceiling (see VisualSpan).
        if (display.GetNodeOrNull<ColorRect>("%BarFill") is { } fill)
        {
            fill.Visible = spec.VisualSpan is not null;
            if (spec.VisualSpan is { } span)
            {
                float pct = Mathf.Clamp(value / (float)span, 0f, 1f);
                fill.Size = new Vector2(BarFullWidth * pct, fill.Size.Y);
            }
        }

        if (display.GetNodeOrNull<ColorRect>("%BarBack") is { } track)
        {
            track.Visible = spec.VisualSpan is not null;
        }

        if (display.GetNodeOrNull<Label>("%ValueLabel") is { } label)
        {
            label.Text = spec.LabelMax is { } max ? $"{value}/{max}" : $"{value}";
        }

        int previous = display.HasMeta(PreviousValueMeta)
            ? (int)display.GetMeta(PreviousValueMeta)
            : value;
        display.SetMeta(PreviousValueMeta, value);

        if (allowFlash
            && spec.ShouldFlash(previous, value)
            && display.GetNodeOrNull<AnimationPlayer>("%AnimationPlayer") is { } anim)
        {
            anim.Stop();
            anim.Play("flash");
        }
    }
}

/// <summary>
/// Combat lifecycle entry: NCombatUi.Activate fires once the combat room's
/// node tree (creature nodes, vfx containers) is live — the same surface the
/// Downfall reference patches for its combat UI. Old displays are discarded
/// inside Setup, so a rebuilt room never accumulates gauges.
/// </summary>
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Activate))]
internal static class NCombatUi_Activate_GaugeSetup
{
    [HarmonyPostfix]
    public static void Postfix(CombatState state)
    {
        if (NCombatRoom.Instance is not { } combatRoom)
        {
            return;
        }

        foreach (var player in state.Players)
        {
            GaugeBridge.Setup(combatRoom, player);
            SalonVisualsBridge.Setup(combatRoom, player);
        }
    }
}
