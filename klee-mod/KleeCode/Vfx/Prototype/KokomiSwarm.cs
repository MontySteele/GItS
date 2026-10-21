using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.TestSupport;

namespace KleeMod.Vfx;

/// <summary>
/// THE VISIBLE SWARM (art polish, 2026-10-21; Kokomi taste and art paper,
/// Part 2 item 3, pick 5 (a)). Each waiting Planned Sting or Ward is a small
/// jellyfish orbiting the Bake-Kurage: coral-pink for a Sting, pale blue for
/// a Ward. At most <see cref="KokomiFxMath.SwarmCap"/> are drawn, shared
/// between the two kinds in proportion, and a "+N" says how many more wait.
/// When a Sting or Ward is carried out its jellyfish darts at its target (a
/// Ward's into Kokomi) and is gone.
///
/// STATE-DRIVEN, NEVER COUNTED UP. Every redraw reads the queue the strip
/// reads (<c>KokomiPlan.Showing</c>: the morning's remaining Plans during a
/// drain, the pending queue otherwise) and reconciles the drawn jellyfish to
/// it (<see cref="KokomiFxMath.Reconcile"/>), so a Plan flipped, cancelled,
/// cashed or carried out, a reload, or a new combat cannot leave the swarm
/// out of step. It rides the strip's one funnel
/// (<c>KokomiPlanStrip.Refresh</c>, called on every queue move) and the
/// combat UI's setup seam, for every seat's Bake-Kurage rather than the local
/// one alone: a co-op partner's swarm is on the field for everyone.
///
/// Shown where the strip shows (<c>KokomiOverhaul.StripShowsFor</c>): on
/// Kokomi, and on another character only once that character has written a
/// Plan, when the strip already draws those Plans. The swarm is a child of
/// the Bake-Kurage's creature node, so it leaves with the pet.
/// </summary>
internal static class KokomiSwarm
{
    private const string RootName = "KleeModKurageSwarm";
    private const string KindMeta = "kleemod_swarm_kind";
    private const string HiddenMeta = "kleemod_swarm_hidden";
    private const string LeavingMeta = "kleemod_swarm_leaving";
    private const string PhaseMeta = "kleemod_swarm_phase";
    private const string ClockMeta = "kleemod_swarm_clock";

    /// <summary>The orbit: an ellipse round the Bake-Kurage's middle, one
    /// turn every <see cref="Period"/> seconds.</summary>
    private const float RadiusX = 62f;
    private const float RadiusY = 24f;
    private const float Period = 7f;

    /// <summary>Which jellyfish a Plan's card draws as, if any. The two
    /// generated cards only (<c>KokomiRefounding.IsJellyfish</c>'s pair).</summary>
    internal static SwarmKind KindOf(CardModel? card) => card switch
    {
        ProtoKkSting => SwarmKind.Sting,
        ProtoKkWard => SwarmKind.Ward,
        _ => SwarmKind.None,
    };

    /// <summary>Build or refresh every seat's swarm (combat UI setup).</summary>
    public static void SetupAll(CombatState? state)
    {
        if (state == null) return;
        foreach (var player in state.Players)
        {
            Refresh(player.Creature);
        }
    }

    /// <summary>Redraw one seat's swarm from its queue.</summary>
    public static void Refresh(Creature? kokomi)
    {
        if (kokomi?.Player is not { } player) return;
        if (TestMode.IsOn || NCombatRoom.Instance is not { } room) return;
        try
        {
            var pet = BakeKuragePet.Of(kokomi);
            var petNode = pet == null ? null : room.GetCreatureNode(pet);
            if (petNode == null || !GodotObject.IsInstanceValid(petNode)) return;
            var root = petNode.GetNodeOrNull<Node2D>(RootName);
            if (pet!.IsDead || !KokomiOverhaul.StripShowsFor(kokomi))
            {
                root?.QueueFree();
                return;
            }
            var stings = 0;
            var wards = 0;
            foreach (var entry in KokomiPlan.Showing(player))
            {
                switch (KindOf(entry.Source))
                {
                    case SwarmKind.Sting: stings++; break;
                    case SwarmKind.Ward: wards++; break;
                }
            }
            if (root == null)
            {
                if (stings + wards == 0) return;
                root = Build(petNode);
            }
            var (s, w) = KokomiFxMath.SwarmSplit(stings, wards);
            Match(root, SwarmKind.Sting, s);
            Match(root, SwarmKind.Ward, w);
            var (_, more) = KokomiFxMath.SwarmShown(stings + wards);
            if (root.GetNodeOrNull<Label>("More") is { } label)
            {
                label.Visible = more != null;
                label.Text = more ?? string.Empty;
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] Kurage swarm skipped: {e.Message}");
        }
    }

    private static Node2D Build(NCreature petNode)
    {
        var root = new Node2D { Name = RootName };
        var more = new Label
        {
            Name = "More",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            Size = new Vector2(60f, 26f),
            Position = new Vector2(-30f, RadiusY + 14f),
            Visible = false,
        };
        more.AddThemeFontSizeOverride("font_size", 18);
        more.AddThemeColorOverride("font_color", new Color(0.86f, 0.98f, 1f));
        more.AddThemeColorOverride("font_outline_color", new Color(0.04f, 0.2f, 0.27f));
        more.AddThemeConstantOverride("outline_size", 6);
        root.AddChildSafely(more);
        petNode.AddChildSafely(root);
        // One clock for the whole swarm: a looping tween that places every
        // jellyfish each frame. It is the swarm's own, so it dies with it.
        KokomiPlanFx.WhenInTree(root, () =>
        {
            root.GlobalPosition = KokomiPlanFx.Centre(petNode);
            var clock = root.CreateTween().SetLoops();
            clock.TweenMethod(Callable.From<float>(t => Tick(root, petNode, t)),
                              0f, 1f, Period);
            root.SetMeta(ClockMeta, true);
        });
        return root;
    }

    private static IEnumerable<Node2D> Jellies(Node2D root, SwarmKind kind) =>
        root.GetChildren().OfType<Node2D>()
            .Where(n => n.HasMeta(KindMeta) && n.GetMeta(KindMeta).AsInt32() == (int)kind
                        && !n.HasMeta(LeavingMeta));

    private static bool Hidden(Node2D n) =>
        n.HasMeta(HiddenMeta) && n.GetMeta(HiddenMeta).AsBool();

    /// <summary>Bring one kind's jellyfish to <paramref name="wanted"/>.</summary>
    private static void Match(Node2D root, SwarmKind kind, int wanted)
    {
        var all = Jellies(root, kind).ToList();
        var visible = all.Where(n => !Hidden(n)).ToList();
        var hidden = all.Where(Hidden).ToList();
        var (unhide, add, removeHidden, removeVisible) =
            KokomiFxMath.Reconcile(visible.Count, hidden.Count, wanted);
        for (var i = 0; i < unhide; i++)
        {
            hidden[i].SetMeta(HiddenMeta, false);
            hidden[i].Visible = true;
        }
        for (var i = 0; i < removeHidden; i++)
        {
            hidden[unhide + i].QueueFree();
        }
        for (var i = 0; i < removeVisible; i++)
        {
            Leave(visible[visible.Count - 1 - i]);
        }
        for (var i = 0; i < add; i++)
        {
            var jelly = Jelly(kind);
            jelly.SetMeta(KindMeta, (int)kind);
            jelly.SetMeta(PhaseMeta, 0f);
            jelly.Modulate = new Color(1, 1, 1, 0);
            jelly.Scale = new Vector2(0.4f, 0.4f);
            root.AddChildSafely(jelly);
            KokomiPlanFx.WhenInTree(jelly, () =>
            {
                Sway(jelly);
                var tw = jelly.CreateTween().SetParallel(true);
                tw.TweenProperty(jelly, "modulate:a", 1f, 0.25f);
                tw.TweenProperty(jelly, "scale", Vector2.One, 0.25f)
                  .SetTrans(Tween.TransitionType.Back).SetEase(Tween.EaseType.Out);
            });
        }
    }

    /// <summary>A jellyfish that is no longer wanted shrinks and fades
    /// (0.2 s). It is out of the count at once.</summary>
    private static void Leave(Node2D jelly)
    {
        jelly.SetMeta(LeavingMeta, Time.GetTicksMsec());
        if (!jelly.IsInsideTree())
        {
            jelly.QueueFree();
            return;
        }
        var tw = jelly.CreateTween().SetParallel(true);
        tw.TweenProperty(jelly, "modulate:a", 0f, 0.2f);
        tw.TweenProperty(jelly, "scale", new Vector2(0.4f, 0.4f), 0.2f);
        tw.Chain().TweenCallback(Callable.From(jelly.QueueFree));
    }

    /// <summary>Place every jellyfish in view on the orbit. Each eases to its
    /// even slot, so a jellyfish arriving or leaving re-spaces the rest
    /// smoothly. The far half of the orbit is dimmer and smaller.</summary>
    private static void Tick(Node2D root, NCreature petNode, float t)
    {
        if (!GodotObject.IsInstanceValid(root) || !GodotObject.IsInstanceValid(petNode)) return;
        root.GlobalPosition = KokomiPlanFx.Centre(petNode);
        var shown = root.GetChildren().OfType<Node2D>()
            .Where(n => n.HasMeta(KindMeta) && !n.HasMeta(LeavingMeta) && !Hidden(n))
            .OrderBy(n => n.GetMeta(KindMeta).AsInt32())
            .ToList();
        for (var i = 0; i < shown.Count; i++)
        {
            var jelly = shown[i];
            var target = KokomiFxMath.SlotPhase(i, shown.Count);
            var phase = jelly.GetMeta(PhaseMeta).AsSingle();
            var gap = target - phase;
            gap -= Mathf.Floor(gap + 0.5f);
            phase += gap * 0.08f;
            jelly.SetMeta(PhaseMeta, phase);
            var a = (t + phase) * Mathf.Tau;
            var front = Mathf.Sin(a);
            jelly.Position = new Vector2(Mathf.Cos(a) * RadiusX,
                                         front * RadiusY + Mathf.Sin(a * 3f) * 3f);
            var depth = 0.78f + 0.22f * (front + 1f) * 0.5f;
            if (jelly.GetNodeOrNull<Node2D>("Body") is { } body)
            {
                body.Scale = new Vector2(depth, depth);
                body.Modulate = new Color(1, 1, 1, 0.55f + 0.45f * (front + 1f) * 0.5f);
            }
        }
    }

    /// <summary>
    /// A Sting or Ward carried out: its jellyfish darts from the orbit to
    /// <paramref name="to"/> (the target, or Kokomi for a Ward) and bursts.
    /// One that already left the orbit (the queue moved first, as Change of
    /// Plans does) lends its place; with none in view it leaves from the
    /// Bake-Kurage. The orbit's own count is restored by the next redraw.
    /// </summary>
    public static void Dart(Creature pet, SwarmKind kind, Vector2? to, Node container,
                            float k)
    {
        if (NCombatRoom.Instance is not { } room) return;
        var petNode = room.GetCreatureNode(pet);
        if (petNode == null || !GodotObject.IsInstanceValid(petNode)) return;
        var from = KokomiPlanFx.Centre(petNode);
        var root = petNode.GetNodeOrNull<Node2D>(RootName);
        if (root != null)
        {
            var leaving = root.GetChildren().OfType<Node2D>()
                .Where(n => n.HasMeta(KindMeta) && n.GetMeta(KindMeta).AsInt32() == (int)kind
                            && n.HasMeta(LeavingMeta))
                .OrderByDescending(n => n.GetMeta(LeavingMeta).AsUInt64())
                .FirstOrDefault();
            var visible = Jellies(root, kind).FirstOrDefault(n => !Hidden(n));
            if (leaving != null)
            {
                from = leaving.GlobalPosition;
                leaving.Visible = false;
            }
            else if (visible != null)
            {
                from = visible.GlobalPosition;
                visible.SetMeta(HiddenMeta, true);
                visible.Visible = false;
            }
        }
        var dart = Jelly(kind);
        if (!KokomiPlanFx.Spawn(container, dart)) return;
        dart.GlobalPosition = from;
        Sway(dart);
        var tint = kind == SwarmKind.Ward ? KokomiPlanFx.WardBlue : KokomiPlanFx.StingPink;
        var end = to ?? from + new Vector2(0f, -60f);
        var dir = end - from;
        var tw = dart.CreateTween();
        tw.TweenInterval(KokomiFxMath.DartAt * k);
        tw.TweenProperty(dart, "rotation", dir.Angle() + Mathf.Pi / 2f, 0.06f * k);
        tw.TweenProperty(dart, "global_position", end, KokomiFxMath.DartFlight * k)
          .SetTrans(Tween.TransitionType.Back).SetEase(Tween.EaseType.In);
        tw.TweenCallback(Callable.From(() =>
        {
            if (to != null && GodotObject.IsInstanceValid(container))
            {
                KokomiPlanFx.Splash(container, end, tint, k);
            }
            dart.QueueFree();
        }));
    }

    /// <summary>One small jellyfish, about 24 px: a glowing bell with a
    /// highlight and three swaying tentacles, in the kind's colour.</summary>
    private static Node2D Jelly(SwarmKind kind)
    {
        var tint = kind == SwarmKind.Ward ? KokomiPlanFx.WardBlue : KokomiPlanFx.StingPink;
        var jelly = new Node2D { Name = kind == SwarmKind.Ward ? "Ward" : "Sting" };
        var body = new Node2D { Name = "Body" };
        jelly.AddChildSafely(body);
        var tentacles = new Node2D { Name = "Tentacles", Position = new Vector2(0f, -2f) };
        body.AddChildSafely(tentacles);
        for (var i = -1; i <= 1; i++)
        {
            var line = new Line2D
            {
                Width = 2.4f,
                Antialiased = true,
                Points = new[]
                {
                    new Vector2(i * 5f, 0f),
                    new Vector2(i * 6f + 2f, 6f),
                    new Vector2(i * 5f - 1f, 12f),
                    new Vector2(i * 6f + 1f, 17f),
                },
                Gradient = new Gradient
                {
                    Offsets = new[] { 0f, 1f },
                    Colors = new[] { new Color(tint, 0.9f), new Color(tint, 0f) },
                },
            };
            tentacles.AddChildSafely(line);
        }
        var bell = KokomiPlanFx.Blob(tint, 0.44f, additive: false);
        bell.Scale = new Vector2(0.44f, 0.34f);
        bell.Position = new Vector2(0f, -6f);
        body.AddChildSafely(bell);
        var glow = KokomiPlanFx.Blob(tint, 0.6f, additive: true);
        glow.Position = new Vector2(0f, -4f);
        glow.Modulate = new Color(1, 1, 1, 0.5f);
        body.AddChildSafely(glow);
        var shine = KokomiPlanFx.Blob(Colors.White, 0.12f, additive: true);
        shine.Position = new Vector2(-3f, -9f);
        body.AddChildSafely(shine);
        return jelly;
    }

    /// <summary>The tentacles sway, once the jellyfish is in the tree.</summary>
    private static void Sway(Node2D jelly)
    {
        if (jelly.GetNodeOrNull<Node2D>("Body/Tentacles") is not { } tentacles) return;
        var sway = tentacles.CreateTween().SetLoops();
        sway.TweenProperty(tentacles, "skew", 0.18f, 0.45f)
            .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.InOut);
        sway.TweenProperty(tentacles, "skew", -0.18f, 0.45f)
            .SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.InOut);
    }
}
