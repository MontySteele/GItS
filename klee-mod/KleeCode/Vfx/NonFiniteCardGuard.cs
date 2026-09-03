using System;
using System.Collections.Generic;
using System.Text;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Helpers;
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
/// AND SINCE THE SECOND PASS THERE IS A FOURTH DOOR, which is a different kind
/// of door: it stops the number being MADE rather than refusing it once it
/// exists. `MathHelper.BezierCurve` is a quadratic with no clamp, and
/// `NCardFlyVfx.PlayAnim`'s loop structurally evaluates it past t = 1, where
/// it extrapolates as t^2 -- so one stalled frame is a position in the
/// billions. The clamp holds t at 1, which is the endpoint `PlayAnim` assigns
/// on its own next line; every other caller in the assembly asks for t inside
/// [0, 1] and cannot feel it. See
/// <see cref="MathHelper_BezierCurve_ExtrapolationGuard_Patch"/> for the whole
/// argument, including what it costs.
///
/// THE TRIGGER IS STILL NOT REPRODUCED, and that is stated rather than hidden:
/// three targeted reproductions on the seat's own seed, encounter, ascension,
/// hand and pacing (at Instant and at normal animation speed) produced a
/// byte-identical play sequence and NO non-finite line, so what stalls the
/// frame is environmental and unproven. The MECHANISM is now read off the
/// decompile; the frame that fires it is what the log line is for. What the
/// guards buy is that the next occurrence costs a log line instead of a
/// session -- and the line carries the node chain and its transforms, which is
/// the reading that was missing when this was first investigated.
///
/// SO THE LINE IS THE INSTRUMENT, and it is written to settle the row rather
/// than to record that something happened. One line per catch, at most once a
/// second per node, carrying: the node's PATH in the scene, the card's id and
/// printed title, the engine's pacing (`Engine.TimeScale`, the frame delta,
/// fps), the position and its MAGNITUDE, and the flying card's own curve --
/// its start, end, arc and duration, the t one frame at this pacing advances
/// (`tStep`), and the t the observed position actually sits at (`tNow`),
/// recovered by inverting the quadratic. Those last two are the row's
/// hypothesis stated as two numbers: a `tNow` in the hundreds beside a `tStep`
/// to match confirms it and names the frame; a `tNow` near 1 at an ordinary
/// 16 ms delta refutes it, and the source is something else.
///
/// SHIPPED, NOT QUARANTINED. The failing code is the base game's and is reached
/// by every character on every card play; scoping the guard to one prototype
/// arm would leave the hang in place everywhere else. On finite input every
/// patch here is a two-comparison no-op that changes nothing.
/// </summary>
internal static class NonFiniteCardGuard
{
    /// <summary>
    /// ONE REPORT PER NODE PER SECOND. The condition prints every frame while
    /// it lasts -- 286 engine errors in the recorded session -- so a reporter
    /// without a limit would be the same denial of service in a different
    /// file.
    ///
    /// WHY THIS REPLACED A ONCE-PER-PROCESS LATCH, which is what the first
    /// pass shipped. The latch bought silence at the price of the reading: the
    /// FIRST catch printed and every later one was dropped -- including a catch
    /// on a different node, a different card, or a different door. The row's
    /// open question is WHICH of those the source is, so an instrument that can
    /// only ever answer once is the wrong one. Per node per second keeps the
    /// flood bounded -- a trail node lives about as long as one card flight, so
    /// the worst case is a line or two per flight -- and still lets a second,
    /// different source name itself.
    /// </summary>
    internal const long ReportIntervalMsec = 1000;

    /// <summary>
    /// When each node last printed. Every card play builds a fresh trail, so
    /// these keys are transient and the map needs a bound of its own; see
    /// <see cref="MayReport"/>.
    /// </summary>
    private static readonly Dictionary<ulong, long> LastReportMsec = new();

    /// <summary>
    /// How many nodes the limiter remembers. Small on purpose: the map exists
    /// to stop a per-frame flood from ONE node, and forgetting a node costs at
    /// most one extra line.
    /// </summary>
    private const int MaxTrackedNodes = 64;

    /// <summary>Test seam: forget the limiter. The mod never calls it.</summary>
    internal static void ResetForTests()
    {
        lock (LastReportMsec)
        {
            LastReportMsec.Clear();
        }
    }

    /// <summary>
    /// May this node's catch be printed at <paramref name="nowMsec"/>?
    ///
    /// The clock is a parameter rather than a read inside, so the limiter is a
    /// pure function of (node, time) and can be asserted headlessly. It is why
    /// the callers read <c>Environment.TickCount64</c> and not Godot's
    /// <c>Time.GetTicksMsec</c>: the second needs an engine this test host has
    /// no way to build.
    /// </summary>
    internal static bool MayReport(ulong nodeKey, long nowMsec)
    {
        lock (LastReportMsec)
        {
            if (LastReportMsec.TryGetValue(nodeKey, out var last)
                && nowMsec >= last
                && nowMsec - last < ReportIntervalMsec)
            {
                return false;
            }

            if (LastReportMsec.Count >= MaxTrackedNodes)
            {
                LastReportMsec.Clear();
            }

            LastReportMsec[nodeKey] = nowMsec;
            return true;
        }
    }

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
    /// Say what was caught, with the node chain that produced it, at most once
    /// a second per node.
    ///
    /// EVERY READ IS GUARDED. This runs on a scene that is already in a state
    /// the engine calls impossible, and a reporter that threw would replace a
    /// drawn-wrong frame with a lost run.
    /// </summary>
    internal static void Report(string what, Node? node) =>
        Report(what, node, detail: null);

    /// <summary>
    /// THE SOURCE HUNT'S INSTRUMENT (`EB-292`, second pass). The first live
    /// catch printed the node chain and nothing else, and the chain alone
    /// cannot decide between the three candidate origins -- so this adds, in
    /// one line, exactly the readings that separate them.
    ///
    /// WHAT THE DECOMPILE ALREADY RULES OUT, so the log does not have to.
    /// `NCardTrail` INTEGRATES NOTHING: <c>_Process</c> forces its own
    /// <c>GlobalPosition</c> to zero and hands <c>CreatePoint</c> the raw
    /// <c>_parent.GlobalPosition</c>; <c>delta</c> is used only to age points.
    /// One level up, <c>NCardTrailVfx._Process</c> copies
    /// <c>_nodeToFollow.GlobalPosition</c> -- the played <c>NCard</c> Control
    /// -- verbatim. So a velocity integrated while paused is not a mechanism
    /// this code has, and the followed position IS the card's.
    ///
    /// THE HYPOTHESIS, which is what the extra readings test.
    /// <c>NCardFlyVfx.PlayAnim</c> drives the card with
    /// <c>_card.GlobalPosition = MathHelper.BezierCurve(_startPos, _endPos, c,
    /// time / _duration)</c>, where <c>time += _speed * GetProcessDeltaTime()</c>
    /// and <c>_speed += _accel * GetProcessDeltaTime()</c>. The loop tests
    /// <c>time / _duration &lt;= 1</c> at the TOP and advances <c>time</c>
    /// inside, so the last iteration always evaluates the curve at a t that has
    /// already overshot -- by one frame's delta over
    /// <c>_duration in [1, 1.75]</c>. The curve is a QUADRATIC
    /// (<c>(1-t)^2 v0 + 2(1-t)t c0 + t^2 v1</c>) and is not clamped, so past
    /// t = 1 it EXTRAPOLATES: |position| grows as t^2 times a control-point
    /// offset the same method sets as high as 500 + 400 px. t near 10^3
    /// therefore lands near 10^9, which is the magnitude the live catch
    /// recorded (-8.8e9, -4.9e8). And <c>GetProcessDeltaTime()</c> is
    /// TIME-SCALED: the seat's session holds <c>Engine.TimeScale</c> at 3
    /// (`understudy/soak.py` TIME_SCALE) on top of FastMode=Instant, so one
    /// stalled frame is three stalled frames' worth of t.
    ///
    /// So the readings below are the hypothesis's own terms: the followed node
    /// and its owner card name WHICH card was mid-flight, the time scale and
    /// the frame delta say how far one frame could have carried t, and the
    /// distance says how far it did. A catch whose delta is an ordinary 16 ms
    /// at TimeScale 1 falsifies this outright, which is the point of logging
    /// it.
    ///
    /// AND THE THIRD PASS ADDS THE TWO THE SECOND STILL COULD NOT SAY. The
    /// flight's OWN dials -- <c>_startPos</c>, <c>_endPos</c>, <c>_arcDir</c>,
    /// <c>_duration</c>, <c>_speed</c> -- are instance fields on the
    /// <c>NCardFlyVfx</c> that is a SIBLING of the trail's own vfx (see
    /// <see cref="FlightOf"/>), so both halves of the hypothesis become
    /// arithmetic instead of inference: <c>tStep</c> is how far one frame at
    /// this delta advances t (<c>_speed * delta / _duration</c>), and
    /// <c>tNow</c> is the t the observed position actually sits at, recovered
    /// by inverting the quadratic (<see cref="RecoverBezierT"/>). `time`
    /// itself is a LOCAL of an async method and lives in a state machine no
    /// handle here reaches, which is why it is recovered rather than read.
    /// </summary>
    internal static void Report(string what, Node? node, string? detail)
    {
        // `Environment` is spelled out: Godot has a type of that name too, and
        // this file has both namespaces open.
        if (!MayReport(KeyOf(node), System.Environment.TickCount64)) return;
        Log.Warn($"[{KleeMod.ModId}] EB-292: refused a non-finite {what}; "
               + $"the card trail would have allocated without bound. "
               + $"Path: {PathOf(node)} | Node chain: {Chain(node)}"
               + (string.IsNullOrEmpty(detail) ? "" : $" | {detail}")
               + $" | {Pacing(node)}");
    }

    /// <summary>
    /// The limiter's key. A freed or missing node all shares bucket zero,
    /// which is the conservative direction: it rate-limits together rather
    /// than not at all.
    /// </summary>
    private static ulong KeyOf(Node? node)
    {
        try
        {
            return node != null && GodotObject.IsInstanceValid(node)
                ? node.GetInstanceId() : 0UL;
        }
        catch (Exception)
        {
            return 0UL;
        }
    }

    /// <summary>
    /// The node's path in the scene tree -- the reading that says WHERE in the
    /// scene the catch happened, which the name chain alone does not (two
    /// trails on two cards render identical chains).
    /// </summary>
    private static string PathOf(Node? node)
    {
        try
        {
            if (node == null) return "(no node)";
            if (!GodotObject.IsInstanceValid(node)) return "(freed)";
            return node.IsInsideTree()
                ? node.GetPath().ToString() : "(not in tree)";
        }
        catch (Exception e)
        {
            return $"(unreadable: {e.GetType().Name})";
        }
    }

    /// <summary>
    /// The engine's own pacing dials at the moment of the catch. Guarded like
    /// everything else here: this runs on a scene the engine has already
    /// called impossible.
    /// </summary>
    private static string Pacing(Node? node)
    {
        try
        {
            // The frame delta is per-node in Godot's API and identical for
            // every node in the tree, so a catch that arrives with no node --
            // the clamp door is a static helper and has none -- reads it off
            // the tree's own root rather than going without the one number the
            // row's hypothesis turns on.
            var paced = node != null && GodotObject.IsInstanceValid(node)
                ? node : TreeRoot();
            var delta = paced != null
                ? paced.GetProcessDeltaTime().ToString("G6")
                : "(no node)";
            return $"timeScale={Engine.TimeScale:G6} maxFps={Engine.MaxFps} "
                 + $"fps={Engine.GetFramesPerSecond():G6} frameDelta={delta}";
        }
        catch (Exception e)
        {
            return $"pacing unreadable: {e.GetType().Name}";
        }
    }

    /// <summary>The scene tree's root window, or null if there is no tree --
    /// which is the normal answer in a headless host.</summary>
    private static Node? TreeRoot()
    {
        try
        {
            var root = (Engine.GetMainLoop() as SceneTree)?.Root;
            return root != null && GodotObject.IsInstanceValid(root)
                ? root : null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// The node a trail FOLLOWS, and the card that owns it -- the two readings
    /// the first catch could not supply, because both live on nodes the guard
    /// is not handed. Resolved reflectively through <c>AccessTools</c> so a
    /// rename in either engine type degrades to a named miss rather than a
    /// throw inside a reporter.
    /// </summary>
    internal static string FollowedBy(NCardTrail? trail)
    {
        try
        {
            if (trail == null || !GodotObject.IsInstanceValid(trail))
            {
                return "followed=(no trail)";
            }
            var parent = AccessTools
                .FieldRefAccess<NCardTrail, Node2D>("_parent")?.Invoke(trail);
            var followed = parent != null && GodotObject.IsInstanceValid(parent)
                ? Describe(parent) : "(unreadable)";

            // The trail's own owner is the NCardTrailVfx two levels up, whose
            // `_nodeToFollow` is the played card. `NCard.Model` names it.
            var vfx = parent?.GetParent() as NCardTrailVfx;
            var card = vfx == null ? null : AccessTools
                .FieldRefAccess<NCardTrailVfx, Control>("_nodeToFollow")
                ?.Invoke(vfx);
            var cardName = card switch
            {
                null => "(no card)",
                NCard n when GodotObject.IsInstanceValid(n) =>
                    $"{NameOf(n)} gpos={n.GlobalPosition} "
                  + $"|gpos|={n.GlobalPosition.Length():G6} size={n.Size}",
                _ => Describe(card),
            };
            return $"followed={followed} card={cardName} "
                 + FlightOf(vfx, card);
        }
        catch (Exception e)
        {
            return $"followed unreadable: {e.GetType().Name}";
        }
    }

    /// <summary>
    /// The card's id AND its printed title. The id alone is what the first two
    /// passes logged, and on the prototype surface an id is a
    /// `KLEEMOD-PROTO_KK_...` token that has to be looked up before it names a
    /// card anyone recognises. `Title` is a localisation lookup on a virtual
    /// member, so it is read inside the guard like everything else here.
    /// </summary>
    private static string NameOf(NCard card)
    {
        try
        {
            var model = card.Model;
            if (model == null) return "(no model)";
            string? title = null;
            try
            {
                title = model.Title;
            }
            catch (Exception)
            {
                // A model whose locale entry is missing still has an id, and
                // the id is the half the register row is written against.
            }
            return string.IsNullOrEmpty(title)
                ? model.Id.ToString()
                : $"{model.Id} \"{title}\"";
        }
        catch (Exception e)
        {
            return $"(card unreadable: {e.GetType().Name})";
        }
    }

    /// <summary>
    /// THE FLIGHT'S OWN DIALS, which is the reading that decides the row.
    ///
    /// HOW IT IS REACHED. `NCardFlyVfx._Ready` builds the trail vfx and adds it
    /// to its OWN parent (<c>GetParent().AddChildSafely(_vfx)</c>), so the
    /// flight and the trail are SIBLINGS and the flight holds the trail in
    /// <c>_vfx</c> and the card in <c>_card</c>. Matching on either is enough,
    /// and both are tried: a scene that reparented one of them still matches on
    /// the card.
    ///
    /// WHAT IT PRINTS AND WHY EACH ONE IS THERE. <c>start</c>/<c>end</c>/
    /// <c>arc</c> reconstruct the exact curve `PlayAnim` is evaluating;
    /// <c>dur</c>/<c>speed</c> with the frame delta give <c>tStep</c>, how far
    /// ONE frame at this pacing advances t; and <c>tNow</c> is the t the card's
    /// observed position actually sits at, recovered by inverting the
    /// quadratic. A tNow near 1 with a small tStep REFUTES the row's
    /// hypothesis; a tNow in the hundreds with a tStep to match confirms it and
    /// names the frame that did it.
    /// </summary>
    internal static string FlightOf(NCardTrailVfx? vfx, Control? card)
    {
        try
        {
            var fly = FindFlight(vfx, card);
            if (fly == null) return "flight=(unmatched)";

            var start = Field<NCardFlyVfx, Vector2>(fly, "_startPos");
            var end = Field<NCardFlyVfx, Vector2>(fly, "_endPos");
            var arc = Field<NCardFlyVfx, float>(fly, "_arcDir");
            var duration = Field<NCardFlyVfx, float>(fly, "_duration");
            var speed = Field<NCardFlyVfx, float>(fly, "_speed");
            var accel = Field<NCardFlyVfx, float>(fly, "_accel");
            if (start is not { } v0 || end is not { } v1 || arc is not { } a
                || duration is not { } dur || speed is not { } spd)
            {
                return "flight=(fields unreadable)";
            }

            var control = FlightControlPoint(v0, v1, a);
            var live = card != null && GodotObject.IsInstanceValid(card);
            var delta = live ? (float)card!.GetProcessDeltaTime() : float.NaN;
            var at = live ? card!.GlobalPosition : Vector2.Zero;

            return $"flight=[start={v0} end={v1} control={control} arc={a:G6} "
                 + $"dur={dur:G6} speed={spd:G6} accel={accel?.ToString("G6") ?? "?"} "
                 + $"tStep={OvershootPerFrame(spd, delta, dur):G6} "
                 + $"tNow={RecoverBezierT(v0, v1, control, at):G6}]";
        }
        catch (Exception e)
        {
            return $"flight unreadable: {e.GetType().Name}";
        }
    }

    /// <summary>
    /// The sibling <c>NCardFlyVfx</c> driving this trail, by the trail vfx it
    /// owns or by the card both follow.
    /// </summary>
    private static NCardFlyVfx? FindFlight(NCardTrailVfx? vfx, Control? card)
    {
        if (vfx == null || !GodotObject.IsInstanceValid(vfx)) return null;
        var container = vfx.GetParent();
        if (container == null || !GodotObject.IsInstanceValid(container))
        {
            return null;
        }
        foreach (var child in container.GetChildren())
        {
            if (child is not NCardFlyVfx fly
                || !GodotObject.IsInstanceValid(fly))
            {
                continue;
            }
            var owned = AccessTools
                .FieldRefAccess<NCardFlyVfx, NCardTrailVfx?>("_vfx")?.Invoke(fly);
            if (ReferenceEquals(owned, vfx)) return fly;
            var flown = AccessTools
                .FieldRefAccess<NCardFlyVfx, NCard>("_card")?.Invoke(fly);
            if (card != null && ReferenceEquals(flown, card)) return fly;
        }
        return null;
    }

    /// <summary>One field of one engine type, or null if it no longer
    /// resolves. Every reflective read in this file goes through a shape like
    /// this so a rename degrades to a named miss.</summary>
    private static TField? Field<TObject, TField>(TObject instance, string name)
        where TObject : class
        where TField : struct
    {
        try
        {
            // Returned rather than assigned to a local on purpose:
            // `FieldRefAccess` THROWS on a dead name, and the bootstrap
            // contract's lint reads an assignment as the field-initializer
            // shape that turns that throw into a
            // TypeInitializationException. The catch below is what makes this
            // site legitimate, and the spelling is what makes that visible.
            return AccessTools.FieldRefAccess<TObject, TField>(name)
                              .Invoke(instance);
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// How far past its own curve a flight has to run before the clamp SAYS
    /// so. The clamp itself bites at t = 1 -- past there the curve is
    /// extrapolating and every caller in the game asks for t in [0, 1] -- but
    /// the last iteration of `PlayAnim`'s loop always overshoots a little by
    /// construction, so a reporter that printed at 1 would print once per card
    /// play forever.
    ///
    /// FOUR IS WHERE THE OVERSHOOT STOPS BEING ARITHMETIC AND STARTS BEING A
    /// STALL. One frame advances t by `_speed * delta / _duration`; with
    /// `_speed` in [1.1, ~4] and `_duration` in [1, 1.75], reaching 4 needs a
    /// frame of roughly two seconds of scaled time -- two thirds of a second
    /// of wall clock at the seat's `Engine.TimeScale` of 3. Nothing healthy
    /// produces that, and the row's whole question is what does.
    /// </summary>
    internal const float ExtrapolationReportT = 4f;

    /// <summary>
    /// The limiter bucket the clamp door reports in. It is not a node -- the
    /// clamp is a prefix on a static helper -- so it takes a key no instance
    /// id can collide with.
    /// </summary>
    private const ulong ExtrapolationKey = ulong.MaxValue;

    /// <summary>
    /// THE SOURCE DOOR'S REPORT. Where the trail guard says "something handed
    /// me an impossible position", this says WHICH FLIGHT ran past its curve
    /// and BY HOW MUCH -- t is read here rather than recovered, because the
    /// clamp is standing inside the call that uses it.
    ///
    /// It prints the position the unclamped curve WOULD have produced, and its
    /// magnitude, so the line can be held against the (-8.8e9, -4.9e8) the
    /// first live catch recorded without needing that catch to happen again.
    /// </summary>
    internal static void ReportExtrapolation(Vector2 v0, Vector2 v1, Vector2 c0,
                                             float t)
    {
        if (!MayReport(ExtrapolationKey, System.Environment.TickCount64)) return;
        try
        {
            var would = Bezier(v0, v1, c0, t);
            Log.Warn($"[{KleeMod.ModId}] EB-292: clamped a card flight that had "
                   + $"run past the end of its own curve. t={t:G6} (clamped to "
                   + $"1); the curve at that t is {would} "
                   + $"|pos|={would.Length():G6}. "
                   + $"curve=[start={v0} end={v1} control={c0}] | "
                   + $"{FlightNamed(v0, v1)} | {Pacing(null)}");
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] EB-292: clamped a card flight at "
                   + $"t={t:G6}; the rest of the reading was unreadable "
                   + $"({e.GetType().Name}).");
        }
    }

    /// <summary>
    /// How many nodes the clamp's report walks looking for the flight that
    /// owns a curve. Bounded because this runs while the engine is already
    /// having a bad frame, and it is only ever reached once a second.
    /// </summary>
    private const int MaxNodesScanned = 4000;

    /// <summary>
    /// WHICH CARD IS ON THIS CURVE. The clamp sees four numbers and no node,
    /// so the card is found the only way available: the live `NCardFlyVfx`
    /// whose `_startPos` and `_endPos` ARE those numbers. They are copied from
    /// the same fields the caller passed, so the match is exact rather than
    /// approximate.
    /// </summary>
    private static string FlightNamed(Vector2 start, Vector2 end)
    {
        try
        {
            var root = TreeRoot();
            if (root == null) return "flight=(no tree)";
            var budget = MaxNodesScanned;
            var fly = FindFlightByCurve(root, start, end, ref budget);
            if (fly == null) return "flight=(unmatched)";

            var card = AccessTools
                .FieldRefAccess<NCardFlyVfx, NCard>("_card")?.Invoke(fly);
            var duration = Field<NCardFlyVfx, float>(fly, "_duration");
            var speed = Field<NCardFlyVfx, float>(fly, "_speed");
            var accel = Field<NCardFlyVfx, float>(fly, "_accel");
            var delta = (float)fly.GetProcessDeltaTime();
            var step = duration is { } dur && speed is { } spd
                ? OvershootPerFrame(spd, delta, dur) : float.NaN;

            return $"card={(card == null || !GodotObject.IsInstanceValid(card)
                            ? "(no card)" : NameOf(card))} "
                 + $"flight=[path={PathOf(fly)} dur={duration?.ToString("G6") ?? "?"} "
                 + $"speed={speed?.ToString("G6") ?? "?"} "
                 + $"accel={accel?.ToString("G6") ?? "?"} tStep={step:G6}]";
        }
        catch (Exception e)
        {
            return $"flight unreadable: {e.GetType().Name}";
        }
    }

    /// <summary>Depth-first, budgeted, and it stops at the first match: two
    /// flights cannot share a start AND an end.</summary>
    private static NCardFlyVfx? FindFlightByCurve(Node node, Vector2 start,
                                                  Vector2 end, ref int budget)
    {
        if (budget-- <= 0 || !GodotObject.IsInstanceValid(node)) return null;
        if (node is NCardFlyVfx fly
            && Field<NCardFlyVfx, Vector2>(fly, "_startPos") == start
            && Field<NCardFlyVfx, Vector2>(fly, "_endPos") == end)
        {
            return fly;
        }
        foreach (var child in node.GetChildren())
        {
            var found = FindFlightByCurve(child, start, end, ref budget);
            if (found != null) return found;
        }
        return null;
    }

    /// <summary>
    /// The curve's control point, spelled exactly as `NCardFlyVfx.PlayAnim`
    /// spells it: the midpoint of the flight, pushed off the line by the arc.
    /// Pure, so the recovery below can be checked against a curve this repo
    /// builds itself.
    /// </summary>
    internal static Vector2 FlightControlPoint(Vector2 start, Vector2 end,
                                               float arcDir)
    {
        var control = start + (end - start) * 0.5f;
        control.Y -= arcDir;
        return control;
    }

    /// <summary>
    /// How far ONE frame advances the flight's curve parameter:
    /// <c>time += _speed * GetProcessDeltaTime()</c> over <c>_duration</c>.
    /// This is the row's hypothesis reduced to one number -- a value near 0.02
    /// is an ordinary 16 ms frame and a value in the hundreds is the stall the
    /// row is looking for.
    /// </summary>
    internal static float OvershootPerFrame(float speed, float frameDelta,
                                            float duration)
        => duration == 0f ? float.NaN : speed * frameDelta / duration;

    /// <summary>
    /// WHICH t PRODUCED THIS POSITION. `time` is a local of an async method and
    /// lives in a compiler-generated state machine nothing here holds, so the
    /// only way to read the flight's t is to invert the curve it drew.
    ///
    /// THE ARITHMETIC. A quadratic Bezier is
    /// <c>B(t) = (1-t)^2 v0 + 2(1-t)t c0 + t^2 v1</c>, which regroups per axis
    /// into <c>C t^2 + B t + A</c> with <c>A = v0</c>, <c>B = 2(c0 - v0)</c>,
    /// <c>C = v0 - 2 c0 + v1</c>. Solving on the axis with the larger |C| keeps
    /// the conditioning sane; both roots are then scored by re-evaluating the
    /// curve, because a quadratic reaches most positions twice and only one of
    /// the two also matches the OTHER axis.
    ///
    /// RETURNS NaN WHEN THE POSITION IS NOT ON THIS CURVE, and that is itself a
    /// reading rather than a failure: it says the card's position did not come
    /// from this flight, which refutes the row's hypothesis for that catch. The
    /// answer is checked before it is returned -- solving one axis alone would
    /// always produce SOME t, including for a position the other axis rules
    /// out -- so the recovered t is a t the curve verifiably reaches.
    /// </summary>
    internal static float RecoverBezierT(Vector2 v0, Vector2 v1, Vector2 c0,
                                         Vector2 position)
    {
        if (!IsFinite(v0) || !IsFinite(v1) || !IsFinite(c0)
            || !IsFinite(position))
        {
            return float.NaN;
        }

        var c = v0 - 2f * c0 + v1;
        var b = 2f * (c0 - v0);
        var useX = Math.Abs(c.X) >= Math.Abs(c.Y);
        var quadratic = useX ? c.X : c.Y;
        var linear = useX ? b.X : b.Y;
        var constant = (useX ? v0.X : v0.Y) - (useX ? position.X : position.Y);

        if (Math.Abs(quadratic) < 1e-6f)
        {
            // A degenerate curve -- control point exactly on the midpoint --
            // is a straight line, and t is then one division.
            return Math.Abs(linear) < 1e-9f
                ? float.NaN
                : Verified(v0, v1, c0, -constant / linear, position);
        }

        var discriminant = linear * linear - 4f * quadratic * constant;
        if (discriminant < 0f) return float.NaN;

        var root = MathF.Sqrt(discriminant);
        var first = (-linear + root) / (2f * quadratic);
        var second = (-linear - root) / (2f * quadratic);
        var firstError = Bezier(v0, v1, c0, first).DistanceSquaredTo(position);
        var secondError = Bezier(v0, v1, c0, second).DistanceSquaredTo(position);
        return Verified(v0, v1, c0,
                        firstError <= secondError ? first : second, position);
    }

    /// <summary>
    /// The recovered t, or NaN if the curve at that t does not land on the
    /// position it was recovered from. The tolerance is RELATIVE because the
    /// magnitudes this instrument exists for are around 1e9, where a `float`
    /// has about 64 px of resolution and an absolute epsilon would reject
    /// every real answer.
    /// </summary>
    private static float Verified(Vector2 v0, Vector2 v1, Vector2 c0, float t,
                                  Vector2 position)
    {
        if (!float.IsFinite(t)) return float.NaN;
        var error = Bezier(v0, v1, c0, t).DistanceTo(position);
        var tolerance = 1e-2f * (1f + position.Length());
        return float.IsFinite(error) && error <= tolerance ? t : float.NaN;
    }

    /// <summary>
    /// `MathHelper.BezierCurve`'s arithmetic, re-spelled here rather than
    /// called, so the recovery above can be asserted in a host with no game
    /// assembly loaded.
    /// </summary>
    internal static Vector2 Bezier(Vector2 v0, Vector2 v1, Vector2 c0, float t)
    {
        var inverse = 1f - t;
        return inverse * inverse * v0 + 2f * inverse * t * c0 + t * t * v1;
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

    internal static string Describe(Node node)
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
            NonFiniteCardGuard.Report(
                "card-trail travel", __instance,
                $"from={from} to={pointPos} |to|={pointPos.Length():G6} "
              + $"travel={from.DistanceTo(pointPos):G6} "
              + $"cap={NonFiniteCardGuard.MaxTrailTravelPx:G6} | "
              + NonFiniteCardGuard.FollowedBy(__instance));
            return false;
        }
        NonFiniteCardGuard.Report(
            "card-trail point", __instance,
            $"point={pointPos} |point|={pointPos.Length():G6} | "
          + NonFiniteCardGuard.FollowedBy(__instance));
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
        NonFiniteCardGuard.Report("card type-plaque size", __instance);
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
        NonFiniteCardGuard.Report("card flight destination", node);
        __result = Vector2.Zero;
    }
}

/// <summary>
/// THE SOURCE, AND THIS IS THE DOOR THAT SHUTS IT. The three patches above
/// refuse a position that has already gone wrong. This one stops it being
/// produced.
///
/// WHAT THE DECOMPILE SAYS, and it is the row's hypothesis read back verbatim
/// off 0.111.0's `sts2.dll`. `NCardFlyVfx.PlayAnim` is
///
///     float time = 0f;
///     while (time / _duration &lt;= 1f) {
///         await this.AwaitProcessFrame();
///         float num = (float)GetProcessDeltaTime();
///         time += _speed * num;
///         _speed += _accel * num;
///         ...
///         _card.GlobalPosition =
///             MathHelper.BezierCurve(_startPos, _endPos, c, time / _duration);
///     }
///
/// The exit test is at the TOP and `time` advances INSIDE, so the last
/// iteration always evaluates the curve at a t that has already passed 1 --
/// by one frame's `_speed * delta / _duration`. `MathHelper.BezierCurve` is
/// `(1-t)^2 v0 + 2(1-t)t c0 + t^2 v1` with NO clamp, so past t = 1 it stops
/// interpolating and starts extrapolating, and |position| grows as t^2 against
/// control-point offsets the same method sets as far out as 500 + 400 px.
/// `GetProcessDeltaTime()` is TIME-SCALED, and the seat's session runs
/// `Engine.TimeScale` at 3, so a stalled frame counts triple. t near 3,000 --
/// one frame of about twenty minutes of scaled time -- lands at ~1e9, which is
/// the order of the position the first live catch printed.
/// `NCardFlyShuffleVfx.PlayAnim` is the same loop with the same defect.
///
/// WHY THE CLAMP IS SAFE, WHICH IS A CLAIM ABOUT EVERY CALLER AND NOT JUST
/// THIS ONE. `MathHelper.BezierCurve` has six call sites in the assembly:
/// `NTargetingArrow` (t = i/20, i &lt; 19), `NRemoteTargetingIndicator`
/// (t = i/101, i &lt; 100), `NBolasVfx` (a tween from 0 to 1 with a Sine ease,
/// which does not overshoot), and the two fly-vfx loops. Not one of them
/// deliberately extrapolates: for four the clamp can never fire, and for the
/// other two it substitutes `_endPos` -- the value `PlayAnim` itself assigns
/// on the very next line, once the loop it just left has exited. So the clamp
/// hands back the game's own next position, one frame early, and no card rule,
/// number or timing moves.
///
/// WHAT IT COSTS, stated rather than buried: on the one frame per flight where
/// BOTH the position's t and the look-ahead's `(time + 0.05f) / _duration`
/// clamp to 1, their difference is the zero vector and the card's rotation
/// lerps toward a right angle for that frame. By then `PlayAnim` has already
/// driven `_card.Body` to 0.1 scale and fully black (both saturate at a third
/// of the duration), so the frame in question is a black tenth-size card about
/// to be freed.
///
/// AND IT IS NOT A REPLACEMENT FOR THE GUARDS ABOVE. A patched static helper
/// small enough for the JIT to inline at a call site compiled before boot
/// would not bite at all, and the enormous-but-finite position also has a
/// second candidate origin (a transform inverted through a zero scale) that
/// never passes through this method. The trail guard stays the backstop; this
/// is the door that makes the backstop stop being reached.
/// </summary>
[HarmonyPatch(typeof(MathHelper), nameof(MathHelper.BezierCurve))]
internal static class MathHelper_BezierCurve_ExtrapolationGuard_Patch
{
    [HarmonyPrefix]
    public static void Prefix(Vector2 v0, Vector2 v1, Vector2 c0, ref float t)
    {
        // `!(t > 1f)` rather than `t <= 1f` so a NaN t falls through
        // UNTOUCHED: clamping it would invent a position, and the guards above
        // are what the resulting NaN is for.
        if (!(t > 1f)) return;

        if (t > NonFiniteCardGuard.ExtrapolationReportT)
        {
            NonFiniteCardGuard.ReportExtrapolation(v0, v1, c0, t);
        }

        t = 1f;
    }
}
