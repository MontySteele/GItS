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
/// applicable meter — Klee's Burst, Furina's Encore. Bridge skeleton follows
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
    private sealed class GaugeSpec
    {
        public required string Key { get; init; }

        public required Color FillColor { get; init; }

        /// <summary>Anchor offset relative to the creature node's origin.</summary>
        public required Vector2 AnchorOffset { get; init; }

        /// <summary>Bar renders full at this many points (display only).</summary>
        public required int VisualSpan { get; init; }

        /// <summary>Null for the unbounded Encore buffer: label shows the raw count.</summary>
        public int? LabelMax { get; init; }

        public required Func<Creature, bool> AppliesTo { get; init; }

        public required Func<Creature, int> ReadValue { get; init; }

        /// <summary>(previous, current) -> threshold-crossing flash.</summary>
        public required Func<int, int, bool> ShouldFlash { get; init; }
    }

    private static readonly GaugeSpec[] Specs =
    {
        // Burst ready: flash when the meter first reaches the cast gate.
        new()
        {
            Key = "burst",
            FillColor = new Color(1.0f, 0.45f, 0.15f),
            AnchorOffset = new Vector2(-100f, -250f),
            VisualSpan = BurstConstants.KleeMax,
            LabelMax = BurstConstants.KleeMax,
            AppliesTo = creature => creature.Player?.Character is Klee,
            ReadValue = KleeBurstResource.AmountFor,
            ShouldFlash = (previous, current) =>
                previous < BurstConstants.KleeMax
                && current >= BurstConstants.KleeMax,
        },
        // Encore empty: flash when a spend/absorb drains the buffer to zero
        // (the overdraw moment — further costs start hitting HP).
        new()
        {
            Key = "encore",
            FillColor = new Color(0.35f, 0.75f, 1.0f),
            AnchorOffset = new Vector2(-100f, -250f),
            VisualSpan = 20,
            LabelMax = null,
            AppliesTo = FurinaResources.IsFurina,
            ReadValue = FurinaResources.Encore,
            ShouldFlash = (previous, current) => previous > 0 && current <= 0,
        },
    };

    private const float BarFullWidth = 60f;
    private const string PreviousValueMeta = "kleemod_gauge_value";

    private static readonly Dictionary<(Player Player, string Key), Node2D>
        Displays = new();

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

            string? scenePath = KleePck.Path("shared/gauge.tscn");
            if (scenePath == null)
            {
                if (!_warnedMissingScene)
                {
                    _warnedMissingScene = true;
                    MegaCrit.Sts2.Core.Logging.Log.Warn(
                        $"[{KleeMod.ModId}] shared/gauge.tscn missing from pck; "
                        + "gauges disabled (falling back to badge powers only)");
                }
                return;
            }

            var display = ResourceLoader
                .Load<PackedScene>(scenePath)
                .Instantiate<Node2D>();
            combatRoom.CombatVfxContainer.AddChildSafely(display);

            if (display.GetNodeOrNull<ColorRect>("%BarFill") is { } fill)
            {
                fill.Color = spec.FillColor;
            }

            // Script-less tracking: the creature node drives the gauge's
            // global position through the engine's transform propagation.
            var creatureNode = combatRoom.GetCreatureNode(creature);
            if (creatureNode != null)
            {
                var anchor = new RemoteTransform2D
                {
                    Position = spec.AnchorOffset,
                    UpdateRotation = false,
                    UpdateScale = false,
                    UseGlobalCoordinates = true,
                };
                creatureNode.AddChildSafely(anchor);
                anchor.RemotePath = anchor.GetPathTo(display);
            }

            Displays[(player, spec.Key)] = display;
            RefreshDisplay(display, spec, creature, allowFlash: false);
        }
    }

    /// <summary>
    /// Re-read the authoritative value and redraw every gauge this creature
    /// owns. Call sites are the resource mutation funnels — enumerated in
    /// docs/animation-sprint-1-log.md (Track C). If a future mutator bypasses
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

    private static Node2D? GetDisplay(Player player, GaugeSpec spec)
    {
        var display = Displays.GetValueOrDefault((player, spec.Key));
        if (display != null && GodotObject.IsInstanceValid(display))
        {
            return display;
        }

        Displays.Remove((player, spec.Key));
        return null;
    }

    private static void DiscardDisplay(Player player, GaugeSpec spec)
    {
        if (Displays.TryGetValue((player, spec.Key), out var old)
            && GodotObject.IsInstanceValid(old))
        {
            old.QueueFree();
        }
        Displays.Remove((player, spec.Key));
    }

    private static void RefreshDisplay(
        Node2D display, GaugeSpec spec, Creature creature, bool allowFlash)
    {
        int value = spec.ReadValue(creature);

        if (display.GetNodeOrNull<ColorRect>("%BarFill") is { } fill)
        {
            float pct = Mathf.Clamp(value / (float)spec.VisualSpan, 0f, 1f);
            fill.Size = new Vector2(BarFullWidth * pct, fill.Size.Y);
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
        }
    }
}
