using System;
using System.Text;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Vfx;

/// <summary>
/// EB-292. THE CARD TRAIL MAY NOT BE ASKED TO FILL AN INFINITE DISTANCE.
///
/// THE DEFECT, from a blind seat's session on 0.2.2001+proto.dirty. The game
/// reached a 41 GB working set and stopped answering the bridge mid-fight.
/// `godot.log` carries three signatures, and they are one failure:
///
///   ERROR: Offset is non-finite   at: sample_baked (scene/resources/curve.cpp)
///   ERROR: Condition "!std::isfinite(p_size.x) || !std::isfinite(p_size.y)"
///          is true.  at: set_size ... NCard.UpdateTypePlaqueSizeAndPosition()
///   System.OutOfMemoryException   at NCardTrail.CreatePoint / _Process
///
/// WHY IT IS UNBOUNDED, which is the part that turns a cosmetic error into a
/// lost session. `NCardTrail.CreatePoint` fills long gaps between trail points
/// by walking the gap at a FIXED 48 px spacing:
///
///     for (float d = 48f; d &lt; distance - 12f; d += 48f) { AddPoint(...); }
///
/// The loop's bound is the distance the followed node moved since the last
/// frame. A finite distance gives finite work. **An infinite one never
/// terminates**: `d` stays finite, `d &lt; infinity` is always true, and every
/// iteration appends a point to a `Line2D` and a float to a `List&lt;float&gt;`
/// until the process is out of memory. There is no cap in the loop and no
/// validation on the position that feeds it, so ONE non-finite frame is the
/// whole hang. A NaN position does not hang -- every comparison against NaN is
/// false -- but it does poison the `Line2D`'s width-curve offsets, which is the
/// `sample_baked` error printed once per point per frame for as long as the
/// trail lives.
///
/// WHAT THIS FILE DOES, AND WHAT IT DELIBERATELY DOES NOT. It refuses the
/// non-finite VALUE at the three doors the recorded session came through, and
/// it names what it caught. It does NOT invent a position: a refused point is
/// a point not drawn, which is a frame of missing trail nobody can see, and the
/// alternative -- substituting a number -- would draw a streak across the
/// screen from wherever the engine thought the card was.
///
/// THE SOURCE OF THE NON-FINITE NUMBER IS NOT NAMED HERE, and that is stated
/// rather than hidden: three targeted reproductions on the seat's own seed,
/// encounter, ascension, hand and pacing (at Instant and at normal animation
/// speed) produced a byte-identical play sequence and NO non-finite line, so
/// the trigger is environmental and was not reproduced. What the guard buys is
/// that the next occurrence costs a log line instead of a session -- and the
/// line carries the node chain and its transforms, which is the reading that
/// was missing when this was first investigated.
///
/// SHIPPED, NOT QUARANTINED. The failing code is the base game's and is reached
/// by every character on every card play; scoping the guard to one prototype
/// arm would leave the hang in place everywhere else. On finite input every
/// patch here is a two-comparison no-op that changes nothing.
/// </summary>
internal static class NonFiniteCardGuard
{
    /// <summary>
    /// One report per process. The condition prints every frame while it lasts
    /// -- 286 engine errors in the recorded session -- so a reporter without a
    /// latch would be the same denial of service in a different file.
    /// </summary>
    private static bool _reported;

    /// <summary>Test seam: forget the latch. The mod never calls it.</summary>
    internal static void ResetForTests() => _reported = false;

    /// <summary>
    /// Is this a number the scene can be given? The whole predicate, in one
    /// place, so the three patches below cannot disagree about what "finite"
    /// means. `float.IsFinite` is false for both NaN and either infinity, which
    /// is the distinction that matters: NaN produces the error spam and
    /// infinity produces the unbounded loop.
    /// </summary>
    internal static bool IsFinite(Vector2 v) =>
        float.IsFinite(v.X) && float.IsFinite(v.Y);

    /// <summary>
    /// How far a followed node may travel in one frame before the trail's
    /// gap-filling loop is refused.
    ///
    /// A SECOND BOUND, and it is not redundant with <see cref="IsFinite"/>: a
    /// position that is merely ENORMOUS (a transform inverted through a
    /// zero scale lands there) is finite, passes every check above, and still
    /// asks the loop for `distance / 48` points. The design resolution is
    /// 1920x1080 and the loop's own spacing is 48 px, so 100,000 px is a
    /// travel no real card play produces and still only ~2,000 points if
    /// something legitimate ever approaches it.
    /// </summary>
    internal const float MaxTrailTravelPx = 100_000f;

    /// <summary>
    /// Would filling the gap from <paramref name="from"/> to
    /// <paramref name="to"/> be bounded work? Pure, so the arithmetic that
    /// decides a hang can be asserted headlessly.
    /// </summary>
    internal static bool IsDrawableTravel(Vector2 from, Vector2 to)
    {
        if (!IsFinite(from) || !IsFinite(to)) return false;
        var distance = from.DistanceTo(to);
        return float.IsFinite(distance) && distance <= MaxTrailTravelPx;
    }

    /// <summary>
    /// Say what was caught, once, with the node chain that produced it.
    ///
    /// EVERY READ IS GUARDED. This runs on a scene that is already in a state
    /// the engine calls impossible, and a reporter that threw would replace a
    /// drawn-wrong frame with a lost run.
    /// </summary>
    internal static void ReportOnce(string what, Node? node)
    {
        if (_reported) return;
        _reported = true;
        Log.Warn($"[{KleeMod.ModId}] EB-292: refused a non-finite {what}; "
               + $"the card trail would have allocated without bound. "
               + $"Node chain: {Chain(node)}");
    }

    /// <summary>The node and its ancestors, each with the transform numbers
    /// that could carry the non-finite value in.</summary>
    private static string Chain(Node? node)
    {
        if (node == null) return "(no node)";
        var sb = new StringBuilder();
        var current = node;
        for (var depth = 0; depth < 8 && current != null; depth++)
        {
            if (depth > 0) sb.Append(" <- ");
            sb.Append(Describe(current));
            try
            {
                current = GodotObject.IsInstanceValid(current)
                    ? current.GetParent() : null;
            }
            catch (Exception)
            {
                break;
            }
        }
        return sb.ToString();
    }

    private static string Describe(Node node)
    {
        try
        {
            if (!GodotObject.IsInstanceValid(node)) return "(freed)";
            var name = node.Name.ToString();
            return node switch
            {
                Control c =>
                    $"{name}[Control size={c.Size} scale={c.Scale} "
                  + $"gpos={c.GlobalPosition}]",
                Node2D n =>
                    $"{name}[Node2D pos={n.Position} scale={n.Scale} "
                  + $"gpos={n.GlobalPosition}]",
                _ => $"{name}[{node.GetType().Name}]",
            };
        }
        catch (Exception e)
        {
            return $"(unreadable: {e.GetType().Name})";
        }
    }
}

/// <summary>
/// THE HANG ITSELF. `NCardTrail.CreatePoint` is handed the followed node's
/// global position every frame; a non-finite or absurd one makes its
/// gap-filling loop unbounded (see <see cref="NonFiniteCardGuard"/>). Refusing
/// the point leaves the trail one frame short and leaves `_lastPointPosition`
/// on its last good value, so a scene that recovers draws normally again.
/// </summary>
[HarmonyPatch(typeof(NCardTrail), "CreatePoint")]
internal static class NCardTrail_CreatePoint_NonFiniteGuard_Patch
{
    /// <summary>
    /// The trail's own record of where the last point went. Read so the guard
    /// can refuse the ENORMOUS-but-finite travel too -- the shape a transform
    /// inverted through a zero scale produces, which is finite, passes every
    /// `IsFinite` check and still asks the loop for `distance / 48` points.
    ///
    /// Resolved through <c>AccessTools</c> rather than Harmony's `___field`
    /// injection so a rename degrades to "check the point only" instead of
    /// throwing at patch time: the finite check is the half that stops the
    /// unbounded loop, and it must survive a field this file does not own.
    /// </summary>
    private static readonly AccessTools.FieldRef<NCardTrail, Vector2?>? LastPoint =
        Resolve();

    private static AccessTools.FieldRef<NCardTrail, Vector2?>? Resolve()
    {
        try
        {
            return AccessTools.FieldRefAccess<NCardTrail, Vector2?>(
                "_lastPointPosition");
        }
        catch (Exception)
        {
            return null;
        }
    }

    [HarmonyPrefix]
    public static bool Prefix(NCardTrail __instance, Vector2 pointPos)
    {
        if (NonFiniteCardGuard.IsFinite(pointPos))
        {
            // The FIRST point of a trail has no predecessor and no gap to
            // fill, so there is nothing to bound; only a travel is refusable.
            var last = LastPoint?.Invoke(__instance);
            if (last is not { } from
                || NonFiniteCardGuard.IsDrawableTravel(from, pointPos))
            {
                return true;
            }
            NonFiniteCardGuard.ReportOnce("card-trail travel", __instance);
            return false;
        }
        NonFiniteCardGuard.ReportOnce("card-trail point", __instance);
        return false;
    }
}

/// <summary>
/// THE ERROR SPAM, and the size that feeds the flight. The base method sets the
/// type plaque from `_typeLabel.Size.X`; when that is non-finite the engine
/// refuses the write and prints a backtrace, and the card's own rect is in the
/// same state -- which matters because `PileType.Play.GetTargetPosition` reads
/// `node.Size` to decide where the card flies to.
///
/// The plaque is read by its scene-unique name rather than through the private
/// field: `%TypeLabel` is what `NCard._Ready` itself resolves, so the two
/// cannot drift, and a scene that no longer carries it makes this patch inert
/// instead of throwing.
/// </summary>
[HarmonyPatch(typeof(NCard), "UpdateTypePlaqueSizeAndPosition")]
internal static class NCard_UpdateTypePlaque_NonFiniteGuard_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(NCard __instance)
    {
        Control? label;
        try
        {
            label = __instance.GetNodeOrNull<Control>("%TypeLabel");
        }
        catch (Exception)
        {
            // The base method is DEFERRED, so it can arrive on a card that has
            // since left the tree and whose unique names no longer resolve.
            // Letting the original run is the pre-guard behaviour.
            return true;
        }
        if (label == null || NonFiniteCardGuard.IsFinite(label.Size))
        {
            return true;
        }
        NonFiniteCardGuard.ReportOnce("card type-plaque size", __instance);
        return false;
    }
}

/// <summary>
/// THE DOOR THE FLIGHT COMES THROUGH. `PileTypeExtensions.GetTargetPosition` is
/// where `NCardFlyVfx.Create` gets the position a played card animates toward,
/// and two of its arms are arithmetic over live geometry -- the play
/// container's size and the card node's own -- so a non-finite rect upstream
/// arrives here as the flight's destination and from there as the trail's
/// per-frame travel.
///
/// `Vector2.Zero` is not an invented answer: it is the value this method
/// already returns for a combat pile outside combat, so a caller that gets it
/// is getting a documented "nowhere" rather than a coordinate this file made
/// up.
/// </summary>
[HarmonyPatch(typeof(PileTypeExtensions),
              nameof(PileTypeExtensions.GetTargetPosition))]
internal static class PileType_GetTargetPosition_NonFiniteGuard_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard? node, ref Vector2 __result)
    {
        if (NonFiniteCardGuard.IsFinite(__result)) return;
        NonFiniteCardGuard.ReportOnce("card flight destination", node);
        __result = Vector2.Zero;
    }
}
