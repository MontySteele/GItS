using System;
using System.Collections.Generic;

namespace KleeMod.Vfx;

/// <summary>What a carried-out Plan looks like on the field: a water bolt
/// at one enemy, a ripple across several, a pearl flash on Kokomi for its
/// Block, or only the Bake-Kurage's pulse.</summary>
public enum PlanBeatLook
{
    Pulse,
    Bolt,
    Ripple,
}

/// <summary>Which of the two jellyfish cards a waiting Plan is, for the
/// swarm round the Bake-Kurage.</summary>
public enum SwarmKind
{
    None,
    Sting,
    Ward,
}

/// <summary>
/// KOKOMI'S EFFECTS, THE ARITHMETIC ALONE (art polish, 2026-10-21; Kokomi
/// taste and art paper, pick 5 (a)). Everything here is pure, so the
/// timings, the swarm's cap and the look a Plan picks are pinned headlessly;
/// <see cref="KokomiPlanFx"/> and <see cref="KokomiSwarm"/> draw them.
/// </summary>
public static class KokomiFxMath
{
    /// <summary>The most jellyfish drawn round the Bake-Kurage. Past this a
    /// "+N" says how many more wait.</summary>
    public const int SwarmCap = 8;

    /// <summary>The whole carry-out effect fits inside the Bake-Kurage's own
    /// lunge (<c>KurageBeat.ActSeconds</c>, 0.35 s) plus a tail that plays
    /// over the damage number. Nothing here is awaited.</summary>
    public const float LongestEffect = 0.6f;

    // The carry-out timeline at standard speed, in seconds from the lunge.
    public const float ThumbFlight = 0.18f;
    public const float PulseAt = 0.12f;
    public const float PulseLength = 0.3f;
    /// <summary>The bolt leaves as the lunge peaks and lands as the hold ends,
    /// so the damage number arrives with it.</summary>
    public const float BoltAt = 0.15f;
    public const float BoltFlight = 0.2f;
    public const float SplashLength = 0.22f;
    public const float RippleAt = 0.15f;
    public const float RippleStagger = 0.05f;
    public const float RippleLength = 0.28f;
    public const float PearlAt = 0.15f;
    public const float PearlLength = 0.35f;
    public const float DartAt = 0.1f;
    public const float DartFlight = 0.22f;
    public const float SigilLength = 0.55f;
    public const float CasketPearlLength = 0.35f;

    /// <summary>The caption stays up long enough to read a card name and a
    /// number. It replaces the 1.4 s speech bubble and blocks nothing.</summary>
    public const float CaptionLength = 1.2f;

    /// <summary>How far an older caption steps up when a new one arrives, so
    /// a morning of four Plans stacks its captions instead of overprinting.</summary>
    public const float CaptionStep = 28f;

    /// <summary>
    /// The game's speed setting as a factor on every effect's timeline.
    /// <c>CreatureCmd.TriggerAnim</c> holds <c>min(w/2, 0.25)</c> in Fast mode
    /// and nothing in Instant, so the effects halve in Fast (they still fit
    /// inside the held beat) and do not play in Instant. Null means "skip".
    /// Mirrors the game's <c>FastModeType</c> by name so it stays pure.
    /// </summary>
    public static float? SpeedFactor(string fastMode) => fastMode switch
    {
        "Instant" => null,
        "Fast" => 0.5f,
        _ => 1f,
    };

    /// <summary>The look a carried-out Plan takes. Damage at one body is a
    /// bolt; at more than one, or at ALL, a ripple. A Plan that deals no
    /// damage pulses the Bake-Kurage only (its Block, if any, flashes on
    /// Kokomi beside whichever look it takes).</summary>
    public static PlanBeatLook LookFor(int damageTargets, bool aimsAtAll)
    {
        if (damageTargets <= 0) return PlanBeatLook.Pulse;
        return aimsAtAll || damageTargets > 1 ? PlanBeatLook.Ripple : PlanBeatLook.Bolt;
    }

    /// <summary>How many jellyfish to draw for <paramref name="count"/>
    /// waiting, and the "+N" under them (null when none is hidden).</summary>
    public static (int Drawn, string? More) SwarmShown(int count)
    {
        if (count <= 0) return (0, null);
        var drawn = Math.Min(count, SwarmCap);
        return (drawn, count > drawn ? "+" + (count - drawn) : null);
    }

    /// <summary>
    /// Split the cap between the two kinds, in proportion, so a swarm of 10
    /// Stings and 2 Wards still shows a Ward. Each kind with any waiting gets
    /// at least one; the rest of the cap goes to the larger.
    /// </summary>
    public static (int Stings, int Wards) SwarmSplit(int stings, int wards)
    {
        stings = Math.Max(0, stings);
        wards = Math.Max(0, wards);
        var (drawn, _) = SwarmShown(stings + wards);
        if (stings + wards <= drawn) return (stings, wards);
        var w = wards == 0 ? 0
            : Math.Max(1, (int)Math.Round(drawn * (double)wards / (stings + wards)));
        var s = stings == 0 ? 0 : Math.Max(1, drawn - w);
        w = Math.Min(wards, drawn - s);
        s = Math.Min(stings, drawn - w);
        return (s, w);
    }

    /// <summary>The orbit slot of jellyfish <paramref name="index"/> of
    /// <paramref name="count"/>, as a fraction of a turn.</summary>
    public static float SlotPhase(int index, int count) =>
        count <= 0 ? 0f : (float)index / count;

    /// <summary>
    /// Reconcile one kind's drawn jellyfish with the count wanted: keep the
    /// ones in view first, then bring back ones hidden by a dart (a Plan
    /// carried out more than once hides one per carry-out before the queue
    /// moves), then add. Returns how many to unhide, add and remove (hidden
    /// ones are removed before visible ones).
    /// </summary>
    public static (int Unhide, int Add, int RemoveHidden, int RemoveVisible)
        Reconcile(int visible, int hidden, int wanted)
    {
        wanted = Math.Max(0, wanted);
        if (visible >= wanted)
        {
            return (0, 0, hidden, visible - wanted);
        }
        var unhide = Math.Min(hidden, wanted - visible);
        var add = wanted - visible - unhide;
        return (unhide, add, hidden - unhide, 0);
    }

    /// <summary>The caption under the Bake-Kurage: the card and its number,
    /// the same words as the wire's <c>line</c> without the pet's name (the
    /// caption sits on the pet).</summary>
    public static string Caption(string card, int? number) =>
        number is { } n ? $"{card}  {n}" : card;

    /// <summary>A point along the bolt's arc at <paramref name="t"/> in [0,1]:
    /// straight in x, lifted by a parabola peaking at <paramref name="lift"/>.</summary>
    public static (float X, float Y) Arc(float fromX, float fromY, float toX,
                                         float toY, float lift, float t)
    {
        t = Math.Clamp(t, 0f, 1f);
        var x = fromX + (toX - fromX) * t;
        var y = fromY + (toY - fromY) * t - lift * 4f * t * (1f - t);
        return (x, y);
    }

    /// <summary>Every timeline's last frame, at standard speed, so a test can
    /// hold all of them to <see cref="LongestEffect"/>.</summary>
    public static IReadOnlyList<float> Ends() => new[]
    {
        ThumbFlight,
        PulseAt + PulseLength,
        BoltAt + BoltFlight + SplashLength,
        RippleAt + RippleStagger * 3 + RippleLength,
        PearlAt + PearlLength,
        DartAt + DartFlight + SplashLength,
        SigilLength,
        CasketPearlLength,
    };
}
