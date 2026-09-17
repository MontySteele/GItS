using System;
using Godot;
using HarmonyLib;
using KleeMod.Teyvat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
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
/// SCOPE: MODDED PLAYER BODIES, AND SINCE THE MOTION PASS ALSO A DRESSED
/// TEYVAT BODY. <see cref="Covers"/> is the player arm and is unchanged: it
/// refuses a pet and refuses anything that is not the player, so Furina's
/// performers keep the death behaviour they have today. <see
/// cref="CoversDressedBody"/> is the second arm, and it is drawn as narrowly
/// as the first.
///
/// WHY AN ENEMY ARM AT ALL, WHEN R213 FROZE ENEMY BEHAVIOUR. R213 froze what
/// an enemy DOES -- its intents, its moves, its numbers. A dressed Teyvat body
/// now carries a death CLIP (`pck-src/teyvat/motion/&lt;set&gt;.tres`), and
/// with the base's spine gate false the game reports its death animation as
/// zero seconds long, so <c>Hook.AfterDeath</c> tears the body out of the
/// arena before one frame of that clip has drawn. Reporting the clip's real
/// length is not a behaviour change; it is the same repair this file already
/// makes for a player, applied where the same gate has the same effect.
///
/// AND IT IS OFF UNLESS THE ARM IS ON. The second arm is gated on
/// <c>TeyvatFrame.Enabled</c> AND on the creature's dressed visuals scene
/// living under <c>res://teyvat/creature_visuals/</c>. With the arm off
/// <c>TeyvatFrame.CurrentActEntry</c> is null, the registry lookup cannot
/// answer, and every calibration deploy and every release package takes
/// exactly the path it takes today. An UNDRESSED enemy is refused on the same
/// lookup even with the arm on.
///
/// Both arms also refuse whenever the base already returned a length, so this
/// can only ever fill a zero in, never shorten a real animation; and the
/// dressed arm reports the base's own zero rather than a fallback when there
/// is no clip to measure, so a body with no motion is untouched.
///
/// AND THE SECOND SEAM, CLOSED BY `EB-797`: the private
/// <c>NCreature.AnimDie(bool, CancellationToken)</c> (<c>:1002-1018</c>) waits
/// <c>min(GetCurrentAnimationTimeRemaining() + 0.5, 20)</c> behind the SAME
/// spine gate, so the engine's own internal death wait was skipped for a
/// spine-less body too. <see cref="ModdedDeathWaitSeam"/> reports that body's
/// own remaining, on the death path only -- and the path is exactly this
/// file's coverage, because the two covered branches of <see cref="Cover"/>
/// are the only places the mark is ever set.
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
    /// The pck directory every dressed Teyvat body's visuals scene lives in
    /// (<c>tools/gen_teyvat_creature_scenes.py</c>'s <c>RES_ROOT</c>). A scene
    /// path under it is the definition of "dressed" here: the registry that
    /// answers it is the same one <c>MonsterVisualsPathPatch</c> swaps the
    /// path from, so the two cannot disagree.
    /// </summary>
    internal const string TeyvatVisualsRoot = "res://teyvat/creature_visuals/";

    /// <summary>
    /// The DRESSED-BODY arm. Pure, so the whole gate is headless-testable:
    /// the arm is on, the base's spine gate was false, the base measured
    /// nothing, and this creature draws through a Teyvat scene.
    /// </summary>
    internal static bool CoversDressedBody(
        bool armEnabled, bool hasSpineAnimation, string? visualsScene, float baseLength)
        => armEnabled
            && !hasSpineAnimation
            && baseLength <= 0f
            && visualsScene != null
            && visualsScene.StartsWith(TeyvatVisualsRoot, StringComparison.Ordinal);

    /// <summary>
    /// The length to report given the clip we measured (<c>0</c> when there was
    /// no clip to measure). Pure, for the same reason.
    /// </summary>
    internal static float LengthFor(float clipLength)
        => clipLength > 0f
            ? MathF.Min(clipLength, MaxDeathAnimLength)
            : FallbackDeathAnimLength;

    /// <summary>
    /// The same, for a dressed body -- except that with NO clip to measure it
    /// hands back the base's own answer rather than a fallback. A player with
    /// no tree is still a modded body and wants a wait; an enemy with no clip
    /// is an enemy this pass has not touched, and the quietest thing to do
    /// with it is nothing.
    /// </summary>
    internal static float DressedLengthFor(float clipLength, float baseLength)
        => clipLength > 0f ? MathF.Min(clipLength, MaxDeathAnimLength) : baseLength;

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
    /// The dressed scene this creature draws through, or <c>null</c>.
    ///
    /// READ OFF THE REGISTRY, not off <c>Node.SceneFilePath</c>. BaseLib's
    /// <c>NCreatureVisualsFactory</c> builds a FRESH <c>NCreatureVisuals</c>
    /// and reparents our children onto it (see
    /// <c>Teyvat/TeyvatVisuals</c>), so the live node is not the node the
    /// scene instantiated and its <c>SceneFilePath</c> is not ours to trust.
    /// <c>TeyvatFrame.StillPortraits</c> is the same table
    /// <c>MonsterVisualsPathPatch</c> swapped the path from, so it answers the
    /// question the path was going to answer, and answers it the same way with
    /// the arm off: <c>CurrentActEntry</c> is null and there is no lookup.
    /// </summary>
    private static string? DressedVisualsScene(Creature entity)
    {
        var dressing = TeyvatFrame.CurrentActEntry;
        var entry = entity.Monster?.Id.Entry;
        if (dressing == null || entry == null)
        {
            return null;
        }

        return TeyvatFrame.StillPortraits.TryGetValue((dressing, entry), out var scene)
            ? scene
            : null;
    }

    /// <summary>
    /// The seam itself: the base's death sound, and a real length in place of
    /// the zero. Returns <paramref name="baseLength"/> untouched for every
    /// creature this does not cover.
    /// </summary>
    internal static float Cover(NCreature creature, float baseLength)
    {
        var entity = creature.Entity;
        if (entity == null)
        {
            return baseLength;
        }

        if (entity.Player != null
            && Covers(
                creature.HasSpineAnimation,
                entity.IsPlayer,
                entity.IsPet,
                baseLength))
        {
            SfxCmd.PlayDeath(entity.Player);
            var clip = DeathClipLength(creature);
            // `EB-797`. THE MARK, SET HERE AND NOWHERE ELSE. It is what scopes
            // `ModdedDeathWaitSeam` -- the engine's own `AnimDie` wait -- to
            // the bodies this file already covers, so no undressed enemy, no
            // pet and no other caller of `GetCurrentAnimationTimeRemaining`
            // can reach it.
            ModdedDeathWaitSeam.NoteDeathStarted(creature, clip);
            return LengthFor(clip);
        }

        // THE DRESSED-BODY ARM, AND NO SOUND ON IT. `SfxCmd.PlayDeath` takes a
        // `Player` and is the PLAYER's death sting; a monster's death audio is
        // the base game's own and is not on this path at all. All this arm
        // does is stop reporting zero for a clip that exists.
        if (CoversDressedBody(
                TeyvatFrame.Enabled,
                creature.HasSpineAnimation,
                DressedVisualsScene(entity),
                baseLength))
        {
            var clip = DeathClipLength(creature);
            ModdedDeathWaitSeam.NoteDeathStarted(creature, clip);
            return DressedLengthFor(clip, baseLength);
        }

        return baseLength;
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
