using System.Runtime.CompilerServices;
using Godot;
using KleeMod.Teyvat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// `EB-816`, THE SECOND HALF OF A [USER] LOOK ON `0.2.3656` (2026-09-17):
/// "I just got into a fight with a group of slimes, and it's a little weird to
/// see them all bobbing at the exact same time at high speed."
///
/// TWO CAUSES, AND THIS FILE OWNS ONE OF THEM. *At high speed* was the clip --
/// `bounce`'s idle ran a whole squash-and-stretch cycle in one second, and
/// `tools/gen_teyvat_creature_scenes.py` now gives it two with a rest at the
/// bottom. *At the exact same time* is this: every dressed body's
/// %AnimationTree is a fresh instance of the same scene playing the same
/// shared `AnimationLibrary`, started at the same frame from the same zero, so
/// three anemo slimes are three copies of one metronome. No amount of clip
/// authoring fixes that, because nothing about the clip is wrong -- what is
/// wrong is that all three are at the same point of it.
///
/// WHAT THIS DOES. Once per creature instance, it pushes that instance's tree
/// a random fraction of the idle INTO the idle and gives its AnimationPlayer a
/// speed within a tenth of nominal, both drawn from <see cref="For"/>.
///
/// DETERMINISTIC, AND PER SLOT. The seed is the creature node's index among
/// its siblings -- its arena slot -- so the same fight on the same seed draws
/// the same bodies at the same offsets. A random draw would have done the
/// visual job just as well and would have made every look unrepeatable; a
/// [USER] look that says "the middle one is wrong" has to be reproducible.
///
/// WHAT IT CANNOT REACH. It is gated twice (<see cref="Covers"/>): the Teyvat
/// arm is on, AND this creature draws through a scene under
/// <c>res://teyvat/creature_visuals/</c>, read off the same registry
/// <see cref="ModdedPlayerDeathSeam.CoversDressedBody"/> reads. With the arm
/// off -- every calibration deploy, every release package -- the gate is shut
/// before any node is touched, so base enemies, the three player bodies and
/// Furina's performers are byte-identical to what they are today.
///
/// TIMING, SAID PLAINLY. <see cref="AnimationPlayer.SpeedScale"/> is the
/// player's own global multiplier: it is not an idle-only lever, so on a body
/// that honours it the attack, hurt and death clips run at the same +/-10% the
/// idle does. That is deliberate and it is the whole tolerance this row claims
/// -- a 1.2 s death clip becomes 1.09-1.33 s. Nothing downstream measures a
/// wall-clock constant: <see cref="ModdedPlayerDeathSeam"/> reads the clip's
/// own authored length and <see cref="ModdedDeathWaitSeam"/> reads the tree's
/// live remaining, so both follow the scale rather than fight it. A per-state
/// scale (an <c>AnimationNodeTimeScale</c> wrapping the idle state) would be
/// idle-only and is the fallback if the +/-10% on a death ever reads wrong; it
/// costs a graph change in all 123 generated scenes, which is not worth paying
/// before the look says it is.
///
/// AND THE KNOWN UNKNOWN, WRITTEN HERE RATHER THAN CLAIMED AWAY. An
/// <c>AnimationTree</c> with <c>active = true</c> drives the assigned
/// <c>AnimationPlayer</c>'s animations itself; the Godot 4 docs say the player
/// "is not able to play animations" while the tree is active, and
/// <c>speed_scale</c> is <c>AnimationPlayer</c>'s own property, not
/// <c>AnimationMixer</c>'s. So the speed line may well be INERT on these
/// bodies until a running-game look says otherwise, and the phase advance is
/// the half that is doing the work. <c>AnimationMixer.Advance(delta)</c> --
/// "manually advance the animations by the specified time" -- is documented to
/// work whatever the callback mode, and the scenes already ship
/// <c>active = true</c>, so nothing here has to arm the tree first.
/// </summary>
internal static class IdleDesync
{
    /// <summary>The idle clip's name in our convention combat scenes -- the
    /// state the router rests in.</summary>
    internal const string IdleClipName = "idle";

    /// <summary>The unique nodes this reaches, the same <c>%</c>-lookups the
    /// router and both death seams use.</summary>
    internal const string AnimationTreePath = "%AnimationTree";

    internal const string AnimationPlayerPath = "%AnimationPlayer";

    /// <summary>The narrowest speed band that still breaks a visible lockstep,
    /// and the widest that cannot be read as a wrong animation.</summary>
    internal const float MinSpeedScale = 0.90f;

    internal const float MaxSpeedScale = 1.10f;

    /// <summary>
    /// WHO HAS ALREADY BEEN OFFSET. A weak table keyed on the node, the same
    /// shape <see cref="ModdedDeathWaitSeam"/> uses: the entry disappears with
    /// the body, so a run that spawns four hundred creatures leaves nothing
    /// behind and no freed node is ever looked up.
    /// </summary>
    private static readonly ConditionalWeakTable<NCreature, object> Offset = new();

    private static readonly object Mark = new();

    /// <summary>
    /// The additive step of the golden-ratio sequence: <c>round(2^32 / phi)</c>,
    /// the 32-bit Fibonacci constant. See <see cref="For"/>.
    /// </summary>
    internal const uint GoldenStep = 2654435769u;

    /// <summary>
    /// THE PURE FUNCTION, and the whole of the randomness.
    ///
    /// THE PHASE IS NOT A HASH, AND THAT IS THE DESIGN. A hash gives a
    /// uniformly distributed draw, and a uniform draw of eight samples puts
    /// two of them close together about as often as not -- two slimes a
    /// fiftieth of a cycle apart are two slimes in lockstep, which is the
    /// exact complaint. So the phase is the GOLDEN-RATIO ADDITIVE SEQUENCE
    /// <c>frac(seed / phi)</c>, computed as an unsigned multiply that wraps:
    /// low-discrepancy by construction, so any run of consecutive slots is
    /// spread as evenly as that many points can be. Measured over any eight
    /// consecutive seeds: span 0.854 of the cycle, closest pair 0.090,
    /// ADJACENT slots always 0.382 or 0.618 apart (the three-distance
    /// theorem). It is still a pure deterministic function of the seed and
    /// still unpredictable to an eye; it is simply a better-behaved one.
    ///
    /// THE SPEED IS a hash -- a 32-bit integer mix (the MurmurHash3-family
    /// finalizer with Fibonacci-scrambled input). Speeds need no spread, only
    /// independence from the phase: if the two moved together the slowest body
    /// would always be the least advanced one, which is a pattern an eye
    /// finds.
    ///
    /// Returns a phase as a FRACTION of the idle, not seconds: the caller
    /// multiplies by the clip's own length, so a 2 s bounce and a 12 s
    /// everlasting halo both get a full spread without this function knowing
    /// either number.
    /// </summary>
    internal static (float PhaseFraction, float SpeedScale) For(int seed)
    {
        var slot = unchecked((uint)seed);
        var phase = Unit(unchecked(slot * GoldenStep));
        var speed = MinSpeedScale + Unit(Hash(slot)) * (MaxSpeedScale - MinSpeedScale);
        return (phase, speed);
    }

    /// <summary>The top 24 bits as a float in <c>[0, 1)</c> -- 24 because that
    /// is every bit a <c>float</c> mantissa can hold, so no two distinct
    /// draws collide by rounding.</summary>
    private static float Unit(uint bits) => (bits >> 8) / 16777216f;

    private static uint Hash(uint seed)
    {
        unchecked
        {
            var x = seed * 2654435761u + 0x9E3779B9u;
            x ^= x >> 16;
            x *= 0x7FEB352Du;
            x ^= x >> 15;
            x *= 0x846CA68Bu;
            x ^= x >> 16;
            return x;
        }
    }

    /// <summary>
    /// The gate. Pure, so the whole of it is headless-testable, and drawn as
    /// narrowly as <see cref="ModdedPlayerDeathSeam.CoversDressedBody"/>: the
    /// arm is on and this body draws through a Teyvat scene.
    /// </summary>
    internal static bool Covers(bool armEnabled, string? visualsScene)
        => armEnabled
            && visualsScene != null
            && visualsScene.StartsWith(
                ModdedPlayerDeathSeam.TeyvatVisualsRoot,
                System.StringComparison.Ordinal);

    /// <summary>
    /// The phase in SECONDS for a clip of this length. Pure. A clip that could
    /// not be measured gets no advance at all rather than a guessed one.
    /// </summary>
    internal static float PhaseSecondsFor(float idleLength, float phaseFraction)
        => idleLength > 0f ? idleLength * phaseFraction : 0f;

    /// <summary>
    /// The attach itself, called from <c>CreatureAnimationRouter.Route</c> on
    /// its first sight of this creature.
    ///
    /// WHY THERE. The mod never sees a dressed body instantiated:
    /// <c>MonsterVisualsPathPatch</c> only rewrites a path STRING, and the
    /// scene is instantiated and reparented inside BaseLib's
    /// <c>NCreatureVisualsFactory</c> (see <c>Teyvat/TeyvatVisuals</c>), so
    /// there is no construction hook of ours that holds the tree. The router's
    /// first trigger for a creature is the earliest moment at which both the
    /// creature and its %AnimationTree exist in our hands, and the engine
    /// sets a trigger on every body as combat opens. The weak mark makes it
    /// once per INSTANCE rather than once per trigger.
    /// </summary>
    internal static void Apply(NCreature creature, AnimationTree tree)
    {
        if (creature == null || tree == null || Offset.TryGetValue(creature, out _))
        {
            return;
        }

        var entity = creature.Entity;
        if (entity == null || !Covers(TeyvatFrame.Enabled, DressedVisualsScene(entity)))
        {
            return;
        }

        // MARKED EVEN WHEN THE WORK BELOW FINDS NOTHING TO DO. A body whose
        // player has no idle clip is not going to grow one, and retrying the
        // lookup on every trigger for the rest of the fight would be the only
        // per-frame cost this layer has ever had.
        Offset.Add(creature, Mark);

        var visuals = creature.Visuals;
        if (visuals == null || !GodotObject.IsInstanceValid(visuals))
        {
            return;
        }

        var player = visuals.GetNodeOrNull<AnimationPlayer>(AnimationPlayerPath);
        if (player == null || !player.HasAnimation(IdleClipName))
        {
            return;
        }

        var clip = player.GetAnimation(IdleClipName);
        if (clip == null)
        {
            return;
        }

        var (phaseFraction, speedScale) = For(creature.GetIndex());
        player.SpeedScale = speedScale;

        var phase = PhaseSecondsFor((float)clip.Length, phaseFraction);
        if (phase > 0f)
        {
            tree.Advance(phase);
        }
    }

    /// <summary>The dressed scene this creature draws through, or
    /// <c>null</c> -- <see cref="ModdedPlayerDeathSeam"/>'s own registry read,
    /// so the two gates cannot drift apart.</summary>
    private static string? DressedVisualsScene(Creature entity)
        => ModdedPlayerDeathSeam.DressedVisualsScene(entity);
}
