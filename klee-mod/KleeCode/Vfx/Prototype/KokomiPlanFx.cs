using System;
using System.Collections.Generic;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.TestSupport;

namespace KleeMod.Vfx;

/// <summary>
/// KOKOMI'S PLAN EFFECTS (art polish, 2026-10-21; [USER], "Agreed on all 5
/// defaults": Kokomi taste and art paper, pick 5 (a), items 2, 3 and 6).
///
/// A carried-out Plan used to be the Bake-Kurage's tween lunge and the base
/// game's speech bubble. Now, inside the same lunge:
///
///   * the Plan's thumbnail flies from the Plan strip into the Bake-Kurage
///     (the local seat's strip only; 0.18 s);
///   * the Bake-Kurage pulses: a scale bump and a Hydro-cyan glow (0.3 s);
///   * then a water bolt arcs to the target for a damage Plan (lands as the
///     hold ends, with a splash), a ripple runs across the enemies for an AoE
///     one, and a pearl-shell flash blooms on Kokomi for a Block one;
///   * a Sting's or Ward's own jellyfish leaves the swarm and darts at its
///     target(s) or into Kokomi (<see cref="KokomiSwarm"/>);
///   * a small caption over the Bake-Kurage names the card and its number,
///     in place of the bubble. The words the blind page reads are the wire's
///     <c>carried_out[].line</c> (<c>KokomiPlan.Snapshot</c>), never the
///     bubble's node, so the page is unchanged.
///
/// Also here: the Hydro sigil ring under Kokomi on her cast and power clips
/// (<see cref="OnTravel"/>) and the pearl flash when the Tamakushi Casket
/// pays Block (<see cref="CasketPearl"/>).
///
/// NOTHING HERE IS AWAITED. The lunge's own hold (<c>KurageBeat.Act</c>,
/// 0.35 s, halved in Fast) is still the only wait; every effect is built of
/// built-in nodes and tweens parented to the combat room's VFX container,
/// timed to fit inside that hold and end by 0.6 s, halved in Fast and skipped
/// in Instant, the way <c>CreatureCmd.TriggerAnim</c> scales its own hold.
/// No new art: the shapes are gradient textures and lines built in code.
/// Inert headless (<c>TestMode</c>, no combat room), and every body is inside
/// a catch, the rule every display bridge in this mod keeps.
/// </summary>
internal static class KokomiPlanFx
{
    internal static readonly Color Hydro = new(0.45f, 0.9f, 1f);
    internal static readonly Color HydroDeep = new(0.12f, 0.55f, 0.85f);
    internal static readonly Color Pearl = new(1f, 0.93f, 0.95f);
    internal static readonly Color PearlBlush = new(1f, 0.74f, 0.82f);
    internal static readonly Color StingPink = new(1f, 0.5f, 0.55f);
    internal static readonly Color WardBlue = new(0.68f, 0.86f, 1f);
    private static readonly Color CaptionInk = new(0.86f, 0.98f, 1f);
    private static readonly Color CaptionOutline = new(0.04f, 0.2f, 0.27f);

    private const string CaptionMeta = "kleemod_kurage_caption";

    private static Texture2D? _blob;
    private static Texture2D? _ring;

    // ---- the gates ---------------------------------------------------------

    /// <summary>The speed factor for this frame's effects, or null to skip
    /// them (headless, no room, Instant mode).</summary>
    internal static float? Speed()
    {
        if (TestMode.IsOn || NCombatRoom.Instance == null) return null;
        string mode;
        try
        {
            mode = SaveManager.Instance?.PrefsSave?.FastMode.ToString() ?? "Normal";
        }
        catch
        {
            mode = "Normal";
        }
        return KokomiFxMath.SpeedFactor(mode);
    }

    private static NCreature? NodeOf(Creature? creature)
    {
        if (creature == null) return null;
        var node = NCombatRoom.Instance?.GetCreatureNode(creature);
        return node != null && GodotObject.IsInstanceValid(node) ? node : null;
    }

    /// <summary>The middle of a creature's hitbox, in the room's global
    /// space (the base game's own <c>GetTopOfHitbox</c> and
    /// <c>GetBottomOfHitbox</c>).</summary>
    internal static Vector2 Centre(NCreature node) =>
        (node.GetTopOfHitbox() + node.GetBottomOfHitbox()) * 0.5f;

    // ---- the carry-out -----------------------------------------------------

    /// <summary>
    /// KURAGE'S OATH CARRIED OUT AS A PLAN plays her Nereid's Ascension clip
    /// (art polish, 2026-10-21, pick 5 (a): "It also plays for Kurage's Oath
    /// carried out"): she raises her arms as the Bake-Kurage carries the
    /// Oath out. Display only, never awaited: the trigger goes to her own
    /// creature node, which <c>CreatureAnimationRouter</c> routes to her
    /// <c>ascension</c> state (a scene without it lunges, as for an attack).
    /// Inert headless (no creature node) and for every other Plan.
    /// </summary>
    public static void OathCall(Creature kokomi, CardModel? source)
    {
        if (!CardPlayMotion.IsAscensionCarryOut(source)) return;
        try
        {
            kokomi.GetCreatureNode()?.SetAnimationTrigger(CardPlayMotion.AscensionTrigger);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Kurage's Oath clip skipped: {e.Message}");
        }
    }

    /// <summary>
    /// One Plan carried out: called just before the lunge, never awaited.
    /// <paramref name="targets"/> are the bodies its damage will land on,
    /// read off the board now (<c>KokomiPlan.BeatShape</c>).
    /// </summary>
    public static void CarryOut(Creature kokomi, Creature? pet,
                                CardModel? source,
                                IReadOnlyList<Creature> targets,
                                bool aimsAtAll, bool blocks)
    {
        if (pet == null || pet.IsDead) return;
        if (Speed() is not { } k) return;
        try
        {
            var room = NCombatRoom.Instance!;
            var petNode = NodeOf(pet);
            if (petNode == null) return;
            var petAt = Centre(petNode);
            var container = room.CombatVfxContainer;

            ThumbFlight(kokomi, source, petNode, k);
            Pulse(petNode, container, petAt, k);

            var swarmKind = KokomiSwarm.KindOf(source);
            var look = KokomiFxMath.LookFor(targets.Count, aimsAtAll);
            if (swarmKind != SwarmKind.None)
            {
                var to = swarmKind == SwarmKind.Ward || targets.Count == 0
                    ? NodeOf(kokomi) : NodeOf(targets[0]);
                KokomiSwarm.Dart(pet, swarmKind, to == null ? null : Centre(to),
                                 container, k);
            }
            if (look == PlanBeatLook.Bolt && swarmKind == SwarmKind.None
                && NodeOf(targets[0]) is { } hit)
            {
                Bolt(container, petAt, Centre(hit), k);
            }
            if (look == PlanBeatLook.Ripple)
            {
                for (var i = 0; i < targets.Count; i++)
                {
                    if (NodeOf(targets[i]) is not { } body) continue;
                    Ripple(container, body.GetBottomOfHitbox(),
                           KokomiFxMath.RippleAt
                           + KokomiFxMath.RippleStagger * Math.Min(i, 3), k);
                }
            }
            if (blocks && NodeOf(kokomi) is { } her)
            {
                PearlFlash(container, Centre(her), KokomiFxMath.PearlAt,
                           KokomiFxMath.PearlLength, k);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Kokomi carry-out effect skipped: {e.Message}");
        }
    }

    /// <summary>
    /// The thumbnail's flight: a copy of the Plan's picture, from the strip's
    /// front slot into the Bake-Kurage, shrinking and fading as it goes. The
    /// strip is the local seat's alone, so only the local seat sees this.
    /// </summary>
    private static void ThumbFlight(Creature kokomi, CardModel? source,
                                    NCreature petNode, float k)
    {
        if (KokomiPlanStrip.FrontThumb(kokomi, source) is not { } front) return;
        var (tex, rect, layer) = front;
        var thumb = new TextureRect
        {
            Name = "KleeModPlanThumbFlight",
            Texture = tex,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered,
            Size = rect.Size,
            PivotOffset = rect.Size * 0.5f,
        };
        if (!Spawn(layer, thumb)) return;
        thumb.GlobalPosition = rect.Position;
        // The pet's point on screen, then into the strip's canvas: the strip
        // lives in the combat UI, the pet in the room.
        var screen = petNode.GetCanvasTransform() * Centre(petNode);
        var into = thumb.GetCanvasTransform().AffineInverse() * screen
                   - rect.Size * 0.5f;
        var d = KokomiFxMath.ThumbFlight * k;
        var tw = thumb.CreateTween().SetParallel(true);
        tw.TweenProperty(thumb, "global_position", into, d)
          .SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.In);
        tw.TweenProperty(thumb, "scale", new Vector2(0.25f, 0.25f), d)
          .SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.In);
        tw.TweenProperty(thumb, "modulate", new Color(0.7f, 1f, 1f, 0f), d)
          .SetTrans(Tween.TransitionType.Expo).SetEase(Tween.EaseType.In);
        tw.Chain().TweenCallback(Callable.From(thumb.QueueFree));
    }

    /// <summary>The Bake-Kurage takes the Plan in: a scale bump on its rig
    /// (a track no clip of its scene animates), a cyan wash on its body's
    /// self-modulate (likewise), and a Hydro glow blooming behind it.</summary>
    private static void Pulse(NCreature petNode, Node container, Vector2 at,
                              float k)
    {
        var delay = KokomiFxMath.PulseAt * k;
        var len = KokomiFxMath.PulseLength * k;
        var rig = petNode.Visuals?.GetNodeOrNull<Node2D>("%Visuals/Rig")
                  ?? petNode.Visuals?.GetNodeOrNull<Node2D>("Visuals/Rig");
        if (rig != null)
        {
            var tw = rig.CreateTween();
            tw.TweenInterval(delay);
            tw.TweenProperty(rig, "scale", new Vector2(1.16f, 1.16f), len * 0.35f)
              .SetTrans(Tween.TransitionType.Back).SetEase(Tween.EaseType.Out);
            tw.TweenProperty(rig, "scale", Vector2.One, len * 0.65f)
              .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.InOut);
            if (rig.GetNodeOrNull<CanvasItem>("Body") is { } body)
            {
                var glow = body.CreateTween();
                glow.TweenInterval(delay);
                glow.TweenProperty(body, "self_modulate",
                                   new Color(0.7f, 1.35f, 1.6f), len * 0.3f);
                glow.TweenProperty(body, "self_modulate", Colors.White, len * 0.7f);
            }
        }
        var bloom = Blob(Hydro, 2.4f, additive: true);
        bloom.Modulate = new Color(1, 1, 1, 0);
        if (!Spawn(container, bloom)) return;
        bloom.GlobalPosition = at;
        var b = bloom.CreateTween();
        b.TweenInterval(delay);
        b.TweenProperty(bloom, "modulate:a", 0.85f, len * 0.3f);
        b.SetParallel(true);
        b.TweenProperty(bloom, "scale", new Vector2(3.2f, 3.2f), len)
         .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.Out);
        b.Chain().TweenProperty(bloom, "modulate:a", 0f, len * 0.4f);
        b.Chain().TweenCallback(Callable.From(bloom.QueueFree));
    }

    /// <summary>A water bolt: a bright head and a short trailing line, along
    /// a shallow arc from the Bake-Kurage to the target, then a splash.</summary>
    private static void Bolt(Node container, Vector2 from, Vector2 to, float k)
    {
        var bolt = new Node2D { Name = "KleeModKurageBolt", Visible = false };
        var head = Blob(Hydro, 0.9f, additive: true);
        bolt.AddChildSafely(head);
        var core = Blob(Colors.White, 0.4f, additive: true);
        bolt.AddChildSafely(core);
        var trail = new Line2D
        {
            Width = 14f,
            DefaultColor = Hydro,
            Antialiased = true,
            TopLevel = true,
            Gradient = new Gradient
            {
                Offsets = new[] { 0f, 1f },
                Colors = new[] { new Color(Hydro, 0f), new Color(Hydro, 0.9f) },
            },
            WidthCurve = Taper(),
            Material = Additive(),
        };
        bolt.AddChildSafely(trail);
        if (!Spawn(container, bolt)) return;
        bolt.GlobalPosition = from;
        var lift = Math.Clamp(Math.Abs(to.X - from.X) * 0.18f, 40f, 140f);
        var points = new List<Vector2>();
        var tw = bolt.CreateTween();
        tw.TweenInterval(KokomiFxMath.BoltAt * k);
        tw.TweenCallback(Callable.From(() => bolt.Visible = true));
        tw.TweenMethod(Callable.From<float>(t =>
        {
            if (!GodotObject.IsInstanceValid(bolt)) return;
            var (x, y) = KokomiFxMath.Arc(from.X, from.Y, to.X, to.Y, lift, t);
            var p = new Vector2(x, y);
            bolt.GlobalPosition = p;
            points.Add(p);
            if (points.Count > 6) points.RemoveAt(0);
            trail.Points = points.ToArray();
        }), 0f, 1f, KokomiFxMath.BoltFlight * k)
          .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.In);
        tw.TweenCallback(Callable.From(() =>
        {
            if (GodotObject.IsInstanceValid(container))
            {
                Splash(container, to, Hydro, k);
            }
            bolt.QueueFree();
        }));
    }

    /// <summary>The bolt's (and a dart's) impact: a ring thrown out flat and a
    /// short white flash.</summary>
    internal static void Splash(Node container, Vector2 at, Color tint, float k)
    {
        var len = KokomiFxMath.SplashLength * k;
        var ring = Ring(tint, 0.5f);
        var flash = Blob(Colors.White, 0.8f, additive: true);
        if (!Spawn(container, ring) | !Spawn(container, flash)) return;
        ring.GlobalPosition = at;
        flash.GlobalPosition = at;
        var tw = ring.CreateTween().SetParallel(true);
        tw.TweenProperty(ring, "scale", new Vector2(2.2f, 1.3f), len)
          .SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.Out);
        tw.TweenProperty(ring, "modulate:a", 0f, len);
        tw.Chain().TweenCallback(Callable.From(ring.QueueFree));
        var fw = flash.CreateTween().SetParallel(true);
        fw.TweenProperty(flash, "scale", new Vector2(1.8f, 1.8f), len * 0.6f);
        fw.TweenProperty(flash, "modulate:a", 0f, len * 0.6f);
        fw.Chain().TweenCallback(Callable.From(flash.QueueFree));
    }

    /// <summary>An AoE Plan's ripple: a flat Hydro ring spreading out at one
    /// enemy's feet, each enemy a beat after the last.</summary>
    private static void Ripple(Node container, Vector2 feet, float at, float k)
    {
        var ring = Ring(Hydro, 0.7f);
        ring.Scale = new Vector2(0.6f, 0.22f);
        ring.Modulate = new Color(1, 1, 1, 0);
        if (!Spawn(container, ring)) return;
        ring.GlobalPosition = feet + new Vector2(0f, -6f);
        var len = KokomiFxMath.RippleLength * k;
        var tw = ring.CreateTween();
        tw.TweenInterval(at * k);
        tw.TweenProperty(ring, "modulate:a", 1f, len * 0.15f);
        tw.SetParallel(true);
        tw.TweenProperty(ring, "scale", new Vector2(3.4f, 1.2f), len)
          .SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.Out);
        tw.TweenProperty(ring, "modulate:a", 0f, len).SetDelay(len * 0.15f);
        tw.Chain().TweenCallback(Callable.From(ring.QueueFree));
    }

    /// <summary>The pearl-shell flash: a soft pearl bloom with a blush rim
    /// and a thin ring opening out, over Kokomi's body (a Block Plan, a
    /// Ward, the Casket).</summary>
    internal static void PearlFlash(Node container, Vector2 at, float delay,
                                    float length, float k)
    {
        var bloom = Blob(Pearl, 1.4f, additive: true);
        var rim = Ring(PearlBlush, 0.9f);
        foreach (var n in new Node2D[] { bloom, rim })
        {
            n.Modulate = new Color(1, 1, 1, 0);
            if (!Spawn(container, n)) return;
            n.GlobalPosition = at;
        }
        var len = length * k;
        var tw = bloom.CreateTween();
        tw.TweenInterval(delay * k);
        tw.TweenProperty(bloom, "modulate:a", 0.95f, len * 0.2f);
        tw.SetParallel(true);
        tw.TweenProperty(bloom, "scale", new Vector2(2.6f, 2.9f), len)
          .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.Out);
        tw.TweenProperty(bloom, "modulate:a", 0f, len * 0.8f).SetDelay(len * 0.2f);
        tw.Chain().TweenCallback(Callable.From(bloom.QueueFree));
        var rw = rim.CreateTween();
        rw.TweenInterval(delay * k);
        rw.TweenProperty(rim, "modulate:a", 1f, len * 0.15f);
        rw.SetParallel(true);
        rw.TweenProperty(rim, "scale", new Vector2(2.4f, 2.8f), len)
          .SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.Out);
        rw.TweenProperty(rim, "modulate:a", 0f, len * 0.85f).SetDelay(len * 0.15f);
        rw.Chain().TweenCallback(Callable.From(rim.QueueFree));
    }

    // ---- the caption -------------------------------------------------------

    /// <summary>
    /// THE LINE, AS A CAPTION. The bubble said "Bake-Kurage: Ambush, 12"; the
    /// caption sits on the Bake-Kurage, so it says "Ambush  12". It rises a
    /// little and fades over 1.2 s, and an older caption still up steps above
    /// the new one. Silent headless; the line itself is recorded by
    /// <c>KokomiPlan.Announce</c> whether or not this draws.
    /// </summary>
    public static void Caption(Creature? speaker, string card, int? number)
    {
        if (speaker == null || speaker.IsDead || string.IsNullOrEmpty(card)) return;
        if (TestMode.IsOn || NCombatRoom.Instance is not { } room) return;
        try
        {
            if (NodeOf(speaker) is not { } node) return;
            var container = room.CombatVfxContainer;
            var who = speaker.CombatId.ToString() ?? "";
            foreach (var child in container.GetChildren())
            {
                if (child is Control old && old.HasMeta(CaptionMeta)
                    && old.GetMeta(CaptionMeta).AsString() == who
                    && GodotObject.IsInstanceValid(old))
                {
                    old.Position += new Vector2(0f, -KokomiFxMath.CaptionStep);
                }
            }
            var label = new Label
            {
                Name = "KleeModKurageCaption",
                Text = KokomiFxMath.Caption(card, number),
                HorizontalAlignment = HorizontalAlignment.Center,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                FocusMode = Control.FocusModeEnum.None,
                Size = new Vector2(260f, 34f),
                Modulate = new Color(1, 1, 1, 0),
            };
            label.SetMeta(CaptionMeta, who);
            label.AddThemeFontSizeOverride("font_size", 22);
            label.AddThemeColorOverride("font_color", CaptionInk);
            label.AddThemeColorOverride("font_outline_color", CaptionOutline);
            label.AddThemeConstantOverride("outline_size", 8);
            if (!Spawn(container, label)) return;
            label.GlobalPosition = node.GetTopOfHitbox() + new Vector2(-130f, -40f);
            var len = KokomiFxMath.CaptionLength;
            var tw = label.CreateTween();
            tw.TweenProperty(label, "modulate:a", 1f, 0.1f);
            tw.Parallel().TweenProperty(label, "position:y", label.Position.Y - 18f, len)
              .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.Out);
            tw.Parallel().TweenProperty(label, "modulate:a", 0f, 0.35f)
              .SetDelay(len - 0.35f);
            tw.Chain().TweenCallback(Callable.From(label.QueueFree));
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Kokomi caption skipped: {e.Message}");
        }
    }

    // ---- her own body ------------------------------------------------------

    /// <summary>
    /// THE HYDRO SIGIL, under Kokomi's feet as her cast, power or Nereid's
    /// Ascension clip starts: a flat ring with a six-point star inside it,
    /// turning a little as it opens and fades (0.55 s). Called from
    /// <c>CreatureAnimationRouter</c> on every state change; inert for anyone
    /// but Kokomi herself and for any other state.
    /// </summary>
    public static void OnTravel(NCreature creature, string? current, string target)
    {
        if (target is not (CreatureAnimationRouter.CastState
                           or CreatureAnimationRouter.PowerState
                           or CreatureAnimationRouter.AscensionState)) return;
        if (current == target) return;
        if (!KokomiResources.IsKokomi(creature.Entity)) return;
        if (Speed() is not { } k) return;
        try
        {
            var container = NCombatRoom.Instance!.CombatVfxContainer;
            var sigil = Sigil();
            sigil.Modulate = new Color(1, 1, 1, 0);
            sigil.Scale = new Vector2(0.55f, 0.55f * 0.32f);
            if (!Spawn(container, sigil)) return;
            sigil.GlobalPosition = creature.GetBottomOfHitbox() + new Vector2(0f, -4f);
            var len = KokomiFxMath.SigilLength * k;
            var tw = sigil.CreateTween();
            tw.TweenProperty(sigil, "modulate:a", 1f, len * 0.2f);
            tw.SetParallel(true);
            tw.TweenProperty(sigil, "scale", new Vector2(1f, 0.32f), len)
              .SetTrans(Tween.TransitionType.Back).SetEase(Tween.EaseType.Out);
            tw.TweenProperty(sigil.GetNode<Node2D>("Spin"), "rotation", 0.6f, len);
            tw.TweenProperty(sigil, "modulate:a", 0f, len * 0.45f).SetDelay(len * 0.55f);
            tw.Chain().TweenCallback(Callable.From(sigil.QueueFree));
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Kokomi sigil skipped: {e.Message}");
        }
    }

    /// <summary>The Tamakushi Casket pays Block: a pearl flash on Kokomi
    /// (0.35 s), beside the relic's own icon flash.</summary>
    public static void CasketPearl(Creature? kokomi)
    {
        if (kokomi == null || kokomi.IsDead) return;
        if (Speed() is not { } k) return;
        try
        {
            if (NodeOf(kokomi) is not { } node) return;
            PearlFlash(NCombatRoom.Instance!.CombatVfxContainer, Centre(node),
                       0f, KokomiFxMath.CasketPearlLength, k);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Casket pearl skipped: {e.Message}");
        }
    }

    // ---- shapes ------------------------------------------------------------

    /// <summary>A soft round glow, 64 px across at scale 1.</summary>
    internal static Sprite2D Blob(Color tint, float scale, bool additive)
    {
        _blob ??= new GradientTexture2D
        {
            Width = 64,
            Height = 64,
            Fill = GradientTexture2D.FillEnum.Radial,
            FillFrom = new Vector2(0.5f, 0.5f),
            FillTo = new Vector2(1f, 0.5f),
            Gradient = new Gradient
            {
                Offsets = new[] { 0f, 0.35f, 1f },
                Colors = new[] { Colors.White, new Color(1, 1, 1, 0.55f), new Color(1, 1, 1, 0f) },
            },
        };
        return new Sprite2D
        {
            Texture = _blob,
            SelfModulate = tint,
            Scale = new Vector2(scale, scale),
            Material = additive ? Additive() : null,
        };
    }

    /// <summary>A thin bright ring, 64 px across at scale 1.</summary>
    internal static Sprite2D Ring(Color tint, float scale)
    {
        _ring ??= new GradientTexture2D
        {
            Width = 96,
            Height = 96,
            Fill = GradientTexture2D.FillEnum.Radial,
            FillFrom = new Vector2(0.5f, 0.5f),
            FillTo = new Vector2(1f, 0.5f),
            Gradient = new Gradient
            {
                Offsets = new[] { 0f, 0.72f, 0.84f, 0.92f, 1f },
                Colors = new[]
                {
                    new Color(1, 1, 1, 0f), new Color(1, 1, 1, 0.12f),
                    Colors.White, new Color(1, 1, 1, 0.2f), new Color(1, 1, 1, 0f),
                },
            },
        };
        return new Sprite2D
        {
            Texture = _ring,
            SelfModulate = tint,
            Scale = new Vector2(scale, scale),
            Material = Additive(),
        };
    }

    /// <summary>The sigil: a ring and a six-point star (two triangles) with
    /// a dot at each point, drawn flat (the caller squashes y for the
    /// ground).</summary>
    private static Node2D Sigil()
    {
        var root = new Node2D { Name = "KleeModHydroSigil" };
        var spin = new Node2D { Name = "Spin" };
        root.AddChildSafely(spin);
        const float r = 92f;
        var outer = new Line2D
        {
            Width = 5f, DefaultColor = Hydro, Antialiased = true,
            Closed = true, Material = Additive(),
        };
        var inner = new Line2D
        {
            Width = 2.5f, DefaultColor = new Color(Hydro, 0.8f), Antialiased = true,
            Closed = true, Material = Additive(),
        };
        var ring = new Vector2[48];
        var ring2 = new Vector2[48];
        for (var i = 0; i < ring.Length; i++)
        {
            var a = Mathf.Tau * i / ring.Length;
            ring[i] = new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * r;
            ring2[i] = new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * (r * 0.78f);
        }
        outer.Points = ring;
        inner.Points = ring2;
        spin.AddChildSafely(outer);
        spin.AddChildSafely(inner);
        for (var t = 0; t < 2; t++)
        {
            var tri = new Line2D
            {
                Width = 3f, DefaultColor = new Color(0.75f, 0.96f, 1f, 0.9f),
                Antialiased = true, Closed = true, Material = Additive(),
            };
            var pts = new Vector2[3];
            for (var i = 0; i < 3; i++)
            {
                var a = -Mathf.Pi / 2f + t * Mathf.Pi + Mathf.Tau * i / 3f;
                pts[i] = new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * (r * 0.78f);
                var dot = Blob(Hydro, 0.28f, additive: true);
                dot.Position = pts[i];
                spin.AddChildSafely(dot);
            }
            tri.Points = pts;
            spin.AddChildSafely(tri);
        }
        var glow = Blob(HydroDeep, 3.2f, additive: true);
        glow.Modulate = new Color(1, 1, 1, 0.5f);
        root.AddChildSafely(glow);
        root.MoveChild(glow, 0);
        return root;
    }

    private static Curve Taper()
    {
        var curve = new Curve();
        curve.AddPoint(new Vector2(0f, 0.1f));
        curve.AddPoint(new Vector2(1f, 1f));
        return curve;
    }

    private static CanvasItemMaterial Additive() =>
        new() { BlendMode = CanvasItemMaterial.BlendModeEnum.Add };

    /// <summary>Add a one-shot effect node and guard it; false when it could
    /// not enter the tree now (then it is freed on arrival and the caller
    /// skips its tweens).</summary>
    internal static bool Spawn(Node parent, Node child)
    {
        parent.AddChildSafely(child);
        Guard(child);
        return child.IsInsideTree();
    }

    /// <summary>Run <paramref name="start"/> now if the node is in the tree,
    /// or once it enters (a deferred add).</summary>
    internal static void WhenInTree(Node node, Action start)
    {
        if (node.IsInsideTree())
        {
            start();
            return;
        }
        void Once()
        {
            node.TreeEntered -= Once;
            start();
        }
        node.TreeEntered += Once;
    }

    /// <summary>The leak guard KleeCombatVfx keeps: a node whose tween never
    /// ran (a room torn down mid-flight) is freed after two seconds.</summary>
    internal static void Guard(Node node)
    {
        if (!node.IsInsideTree())
        {
            // Added deferred (off the main thread): no tween could start, so
            // free it the moment it lands rather than leave it on screen.
            node.TreeEntered += () =>
            {
                if (GodotObject.IsInstanceValid(node)) node.QueueFree();
            };
            return;
        }
        node.GetTree().CreateTimer(2.0).Timeout += () =>
        {
            if (GodotObject.IsInstanceValid(node)) node.QueueFree();
        };
    }
}
