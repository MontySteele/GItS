using System;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// `EB-159`, THE THIRD AND LAST OF THE SPINE-LESS SEAMS ON A MODDED PLAYER BODY.
///
/// WHAT THE BASE DOES. <c>NCreature.StartDeathAnim(bool)</c> (0.111.0 decompile,
/// <c>Nodes.Combat/NCreature.cs:916-955</c>) drops focus and freezes intents
/// unconditionally, and then puts EVERYTHING the player hears and waits for
/// inside one <c>if (_spineAnimator != null)</c> gate (<c>:933-946</c>): the
/// death SFX <c>SfxCmd.PlayDeath(Entity.Player)</c> (<c>:942</c>), the "Dead"
/// trigger, and the clip measurement <c>a = GetCurrentAnimationLength()</c>
/// whose <c>Mathf.Min(a, 30f)</c> is the method's return value (<c>:945</c>).
/// That return value is the death-animation length handed to
/// <c>Hook.AfterDeath</c> (<c>Commands/CreatureCmd.cs:513, :519</c>).
/// <c>DeathAnimLengthOverride</c>, the only escape hatch, is a
/// <c>MonsterModel</c> property (<c>MonsterModel.cs:321-323</c>) -- a player has
/// none.
///
/// WHY THAT BITES US AND NOBODY ELSE. <c>_spineAnimator</c> is built solely when
/// <c>Visuals.HasSpineAnimation</c> (<c>NCreature.cs:503-513</c>), and every
/// character this mod ships is spine-less: a layered <c>Sprite2D</c> rig driven
/// by an %AnimationTree, or a flat portrait. So a modded player DIES SILENTLY
/// and the returned length is <c>0f</c>, i.e. <c>AfterDeath</c> waits nothing
/// for an animation the tree has only just started playing.
///
/// WHAT THIS DOES. A postfix that fills in exactly the two things the gate
/// skipped, and only where it skipped them: play the base's own death sound and
/// report a real length.
///
/// THE LENGTH, AND WHERE THE NUMBER COMES FROM. The base reads the length off
/// the spine clip it just started, so this reads it off the clip WE just
/// started -- <c>%AnimationPlayer</c>'s "death" animation, which is the clip the
/// router's "Dead" route travels to (<c>CreatureAnimationRouter</c>). That keeps
/// the base's rule ("the death animation's own length is the timing authority")
/// rather than inventing a house number, and it is per-character for free:
/// Klee's death clip is 1.0 s and Furina's 1.2 s
/// (<c>pck-src/{klee,furina}/model/combat.tscn</c>). A body with no clip to
/// measure -- a flat portrait with no tree at all -- has nothing to read, so it
/// falls back to <see cref="FallbackDeathAnimLength"/>. The base's 30 s ceiling
/// is kept as-is.
///
/// SCOPE: MODDED PLAYER BODIES ONLY. <see cref="Covers"/> refuses a pet and
/// refuses anything that is not the player, so Furina's performers and every
/// enemy keep the death behaviour they have today (R213 froze enemy behaviour);
/// it also refuses whenever the base already returned a length, so this can
/// only ever fill a zero in, never shorten a real animation.
///
/// STILL OPEN, and reported rather than quietly left: the private
/// <c>NCreature.AnimDie(bool, CancellationToken)</c> (<c>:1002-1018</c>) waits
/// <c>min(GetCurrentAnimationTimeRemaining() + 0.5, 20)</c> behind the SAME
/// spine gate, so the engine's own internal death wait is still skipped for a
/// spine-less body. That is a second seam with a wider blast radius
/// (<c>GetCurrentAnimationTimeRemaining</c> has other callers) and is not this
/// row's fix, which is the sound and the reported length.
/// </summary>
internal static class ModdedPlayerDeathSeam
{
    /// <summary>
    /// The length reported for a spine-less player body that has no death clip
    /// to measure -- a flat portrait with no %AnimationTree at all. One second:
    /// Klee's shipped death clip, the shorter of the two this mod ships
    /// (<c>pck-src/klee/model/combat.tscn</c>, <c>Animation_death</c>
    /// <c>length = 1.0</c>), so the fallback can never out-wait a real clip.
    /// </summary>
    internal const float FallbackDeathAnimLength = 1.0f;

    /// <summary>The base's own ceiling on a death length, <c>NCreature.cs:945</c>
    /// (<c>Mathf.Min(a, 30f)</c>). Kept rather than re-argued.</summary>
    internal const float MaxDeathAnimLength = 30f;

    /// <summary>The death clip's name in our convention combat scenes. The base
    /// game says "die" and our scenes say "death" -- the router's state table
    /// carries the same skew.</summary>
    internal const string DeathClipName = "death";

    /// <summary>The unique node the length is measured off, the same
    /// <c>%</c>-lookup shape the router uses to find its tree.</summary>
    internal const string AnimationPlayerPath = "%AnimationPlayer";

    /// <summary>
    /// Does this death need the seam filled? Pure, so it is the part a headless
    /// test can hold: spine-less (the base's gate was false), a player and not a
    /// pet (scope), and a base result that measured nothing (so a real length is
    /// never overwritten).
    /// </summary>
    internal static bool Covers(
        bool hasSpineAnimation, bool isPlayer, bool isPet, float baseLength)
        => !hasSpineAnimation && isPlayer && !isPet && baseLength <= 0f;

    /// <summary>
    /// The length to report given the clip we measured (<c>0</c> when there was
    /// no clip to measure). Pure, for the same reason.
    /// </summary>
    internal static float LengthFor(float clipLength)
        => clipLength > 0f
            ? MathF.Min(clipLength, MaxDeathAnimLength)
            : FallbackDeathAnimLength;

    /// <summary>The "death" clip's length off the body's own
    /// <c>%AnimationPlayer</c>, or <c>0</c> when there is none to read.</summary>
    private static float DeathClipLength(NCreature creature)
    {
        var visuals = creature.Visuals;
        if (visuals == null || !GodotObject.IsInstanceValid(visuals))
        {
            return 0f;
        }

        var player = visuals.GetNodeOrNull<AnimationPlayer>(AnimationPlayerPath);
        if (player == null || !player.HasAnimation(DeathClipName))
        {
            return 0f;
        }

        var clip = player.GetAnimation(DeathClipName);
        return clip == null ? 0f : (float)clip.Length;
    }

    /// <summary>
    /// The seam itself: the base's death sound, and a real length in place of
    /// the zero. Returns <paramref name="baseLength"/> untouched for every
    /// creature this does not cover.
    /// </summary>
    internal static float Cover(NCreature creature, float baseLength)
    {
        var entity = creature.Entity;
        if (entity?.Player == null)
        {
            return baseLength;
        }

        if (!Covers(
                creature.HasSpineAnimation,
                entity.IsPlayer,
                entity.IsPet,
                baseLength))
        {
            return baseLength;
        }

        SfxCmd.PlayDeath(entity.Player);
        return LengthFor(DeathClipLength(creature));
    }
}

/// <summary>
/// Postfixed rather than prefixed, like every other door this layer owns: the
/// base runs first and this fills in only what its spine gate skipped.
/// </summary>
[HarmonyPatch(typeof(NCreature), nameof(NCreature.StartDeathAnim))]
internal static class NCreature_StartDeathAnim_ModdedPlayerSeam
{
    [HarmonyPostfix]
    public static void Postfix(NCreature __instance, ref float __result)
        => __result = ModdedPlayerDeathSeam.Cover(__instance, __result);
}
