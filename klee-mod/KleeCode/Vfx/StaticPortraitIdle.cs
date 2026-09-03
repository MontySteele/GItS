using System.Collections.Generic;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.RestSite;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;
using MegaCrit.Sts2.Core.Random;
using KleeMod.Patches;

namespace KleeMod.Vfx;

/// <summary>
/// `EB-38`. THE REST SITE AND THE SHOP DRAW OUR CHARACTERS AS A PHOTOGRAPH.
///
/// In combat a modded character is a layered scene driven by an AnimationTree
/// (<see cref="CreatureAnimationRouter"/>, animation sprint 1/2). Out of
/// combat there is no such scene: `Klee.CustomRestSiteAnimPath` and
/// `CustomMerchantAnimPath` hand BaseLib a one-node `.tscn` whose root is a
/// bare `Sprite2D` over `model/combat_model.png`, and BaseLib's
/// `NRestSiteCharacterFactory` / `NMerchantCharacterFactory` build the rest of
/// the node tree around that texture. The base cast is a Spine rig at both
/// surfaces and idles there -- `NRestSiteCharacter._Ready` starts
/// `overgrowth_loop` / `hive_loop` / `glory_loop`, `NMerchantCharacter._Ready`
/// starts `relaxed_loop` -- and every one of those doors is gated on a
/// `SpineSprite`. Ours has none, so ours is a still picture beside four
/// breathing ones. That is the whole of this row.
///
/// WHAT SHIPS: a Node2D WE add above the texture, breathing on a Tween.
///
/// ABOVE the texture, not on it. The sprite is the game's node -- BaseLib
/// made it, the merchant indexes it as `GetChild(0)` and the rest site's
/// `FlipX` walks its own children looking for one -- so its transform is not
/// ours to write. We insert a pivot at the sprite's index, reparent the sprite
/// under it with its local transform untouched, and animate the PIVOT. The
/// pivot sits at the parent's origin, which is the character's ground anchor
/// at both surfaces (the factories place the sprite relative to it), so a
/// scale on the pivot grows the character from its feet rather than from the
/// middle of the picture.
///
/// ON A TWEEN, not a `_Process` loop. A per-frame driver for a two-node
/// cosmetic is banned here for the reason `KleeCombatVfx` gives by example:
/// the engine already owns the clock, a bound Tween dies with the node it
/// animates, and nothing has to remember to stop. <see cref="Plan"/> is the
/// whole animation as data and <see cref="Attach"/> plays exactly that list,
/// so what `KleeTests` pins is what ships rather than a restatement of it.
///
/// WHO GETS IT: every spine-less portrait, which today is Klee, Furina and
/// Kokomi and nothing else. The test is the game's own -- the same
/// `GetClass() != "SpineSprite"` comparison `NRestSiteCharacter`'s
/// `GetChildSpineNodes` filter and `MegaSpineBinding`'s validator make, held
/// once at <see cref="MerchantSpineBinding.SpineClass"/> -- asked of the whole
/// portrait subtree. A real rig answers yes and we do nothing, so the base
/// cast is untouched and this is inert for it.
///
/// SHIPPED, NOT QUARANTINED, on `MerchantSpineBindingPatch.cs`'s precedent and
/// for its reason: the gap is every spine-less character's, all three of ours
/// are, and scoping it to one prototype arm would leave two of them a
/// photograph. Nothing in this file reads an arm flag.
///
/// OUT OF SCOPE, and not covered for free: the character-select splash
/// (`char_select_bg_klee.tscn`) and the card trail are different scenes
/// reached through different factories, and neither goes through these two
/// `_Ready` methods. The combat layer is untouched -- this file names no
/// `NCreature` and no `NCreatureVisuals`.
/// </summary>
internal static class StaticPortraitIdle
{
    /// <summary>
    /// The node we add. Named, not anonymous, because the name is how a
    /// second `_Ready` on the same instance recognises its own work, and how
    /// an operator reading the remote-scene tree knows which node is the
    /// mod's.
    /// </summary>
    internal const string PivotName = "GentleIdle";

    /// <summary>
    /// One full breath, in seconds: in for <see cref="HalfPeriodSeconds"/> and
    /// out for the same. Slow on purpose -- the point is that a player reads
    /// the portrait as alive without ever looking at it directly, and anything
    /// faster reads as a fidget at rest-site distance.
    /// </summary>
    internal const float PeriodSeconds = 2.4f;

    /// <summary>Half a breath: the duration of every step in the plan.</summary>
    internal const float HalfPeriodSeconds = 1.2f;

    /// <summary>
    /// Peak vertical scale. 1.5% of a 280px portrait is ~4px of chest, which
    /// is the smallest move that is legible at the campfire's zoom and the
    /// largest that cannot be mistaken for the art wobbling. Horizontal scale
    /// is deliberately NOT touched: a matched x/y pulse reads as a zoom, not a
    /// breath.
    /// </summary>
    internal const float ScaleYPeak = 1.015f;

    /// <summary>
    /// Pixels the pivot rises at the top of the breath. It cancels most of the
    /// downward half of the scale, so the feet stay planted and the head does
    /// the moving.
    /// </summary>
    internal const float RiseYPixels = 2f;

    /// <summary>
    /// One tweened property: where it goes, over how long, and whether it runs
    /// beside the previous step or after it.
    /// </summary>
    internal readonly struct IdleStep
    {
        internal IdleStep(string property, float to, float seconds, bool parallel)
        {
            Property = property;
            To = to;
            Seconds = seconds;
            Parallel = parallel;
        }

        /// <summary>A Godot property path on the pivot, e.g. `scale:y`.</summary>
        internal string Property { get; }

        internal float To { get; }

        internal float Seconds { get; }

        /// <summary>
        /// True = joins the previous step (`Tween.Parallel()`, which affects
        /// the next tweener only). False = starts a new one, which is Godot's
        /// default and therefore needs no call.
        /// </summary>
        internal bool Parallel { get; }
    }

    /// <summary>
    /// The whole animation, as data. Two steps of <see cref="HalfPeriodSeconds"/>,
    /// each moving scale and position together, looped forever with a sine
    /// ease in and out -- so the extremes are held a moment and the crossings
    /// are quick, which is what breathing does and what a linear ramp does
    /// not.
    ///
    /// Read as a sequence: rise and swell over 1.2s, settle back over 1.2s.
    /// </summary>
    internal static IReadOnlyList<IdleStep> Plan() => new[]
    {
        new IdleStep("scale:y", ScaleYPeak, HalfPeriodSeconds, parallel: false),
        new IdleStep("position:y", -RiseYPixels, HalfPeriodSeconds, parallel: true),
        new IdleStep("scale:y", 1f, HalfPeriodSeconds, parallel: false),
        new IdleStep("position:y", 0f, HalfPeriodSeconds, parallel: true),
    };

    /// <summary>
    /// Should this portrait get an idle? PURE, and it takes the two questions
    /// already answered rather than a node, so the decision is assertable
    /// headlessly -- `Node.GetClass()` is a native call and is outside the
    /// KleeTests boundary (README, "The headless boundary").
    ///
    /// A rig answers <paramref name="hasSpineNode"/> true and keeps its own
    /// idle. A portrait with no `Sprite2D` at all is a tree shape we did not
    /// build and do not understand, and is left alone rather than guessed at.
    /// </summary>
    internal static bool WantsIdle(bool hasSpineNode, bool hasSprite) =>
        !hasSpineNode && hasSprite;

    /// <summary>
    /// Said ONCE per process, on `MerchantSpineBinding.NoteOnce`'s precedent:
    /// one line per rest site would be log volume, and the only thing worth
    /// saying is that the idle armed at all.
    /// </summary>
    private static readonly HashSet<string> Said = new();

    internal static void NoteOnce(string what)
    {
        if (!Said.Add(what)) return;
        Log.Info($"[{KleeMod.ModId}] {what}. EB-38.");
    }

    /// <summary>Test seam: forget what has been said. The mod never calls
    /// it.</summary>
    internal static void ResetAll() => Said.Clear();

    /// <summary>
    /// The live form. Walks the portrait subtree once, and on a spine-less one
    /// inserts the pivot and starts the breath.
    /// </summary>
    internal static void Attach(Node? portrait, string surface)
    {
        if (portrait == null || !GodotObject.IsInstanceValid(portrait)) return;

        Sprite2D? sprite = null;
        bool hasSpineNode = false;

        foreach (var node in Descendants(portrait))
        {
            // Already ours: a second _Ready on the same instance, or a factory
            // that ran the tree twice. Idempotent by name.
            if (node.Name.ToString() == PivotName) return;

            if (node.GetClass() == MerchantSpineBinding.SpineClass)
            {
                hasSpineNode = true;
                break;
            }

            if (sprite == null && node is Sprite2D found)
            {
                sprite = found;
            }
        }

        if (!WantsIdle(hasSpineNode, sprite != null)) return;

        var parent = sprite!.GetParent();
        if (parent == null) return;

        // Index first: AddChild appends, and Reparent then takes the sprite
        // out from under `parent`, so the pivot has to be moved back to where
        // the sprite drew or the portrait changes z-order.
        int index = sprite.GetIndex();
        var pivot = new Node2D { Name = PivotName };
        parent.AddChild(pivot);

        // keepGlobalTransform: false -- the pivot is at the parent's origin
        // with an identity transform, so the sprite's LOCAL transform is
        // already correct under it and nothing about the game's node is
        // rewritten.
        sprite.Reparent(pivot, keepGlobalTransform: false);
        parent.MoveChild(pivot, index);

        var tween = pivot.CreateTween()
            .SetLoops()
            .SetTrans(Tween.TransitionType.Sine)
            .SetEase(Tween.EaseType.InOut);

        foreach (var step in Plan())
        {
            if (step.Parallel)
            {
                tween.Parallel();
            }

            tween.TweenProperty(pivot, step.Property, step.To, step.Seconds);
        }

        // Start somewhere in the cycle rather than at its top. This is the
        // game's own move, made the game's own way: both `_Ready` methods we
        // are standing in for finish with
        // `SetTrackTime(GetAnimationEnd() * Rng.Chaotic.NextFloat())`, because
        // a co-op rest site with two portraits breathing in lockstep reads as
        // a mechanism. `CustomStep` on a paused Tween is the documented manual
        // form; play resumes from wherever it left it.
        tween.Pause();
        tween.CustomStep(Rng.Chaotic.NextFloat() * PeriodSeconds);
        tween.Play();

        NoteOnce($"gentle idle attached to the {surface} portrait "
               + "(spine-less character; the base cast keeps its own rig)");
    }

    /// <summary>
    /// Every node under <paramref name="root"/>, depth first. The portrait
    /// trees BaseLib generates are five or six nodes, so there is nothing to
    /// cache and no depth to guard.
    /// </summary>
    private static IEnumerable<Node> Descendants(Node root)
    {
        foreach (var child in root.GetChildren())
        {
            yield return child;
            foreach (var grandchild in Descendants(child))
            {
                yield return grandchild;
            }
        }
    }
}

/// <summary>
/// `EB-38`, the campfire. `NRestSiteCharacter._Ready` is where the base cast's
/// act loop is started and is the first moment the whole portrait tree exists
/// -- BaseLib's factory has filled in `ControlRoot`, `%Hitbox` and the thought
/// anchors by then, and the node is inside the tree, which `CreateTween` and
/// `Reparent` both require.
/// </summary>
[HarmonyPatch(typeof(NRestSiteCharacter), "_Ready")]
internal static class NRestSiteCharacter_Ready_GentleIdle_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NRestSiteCharacter __instance)
        => StaticPortraitIdle.Attach(__instance, "rest site");
}

/// <summary>
/// `EB-38`, the shop. A POSTFIX, and it runs even though `EB-274`'s prefix on
/// this same method returns false for our portraits: Harmony skips the
/// ORIGINAL when a prefix refuses, never the postfixes. That is the whole
/// reason the idle can be added here at all -- the method whose body we are
/// replacing the effect of is the one that is being skipped.
/// </summary>
[HarmonyPatch(typeof(NMerchantCharacter), "_Ready")]
internal static class NMerchantCharacter_Ready_GentleIdle_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NMerchantCharacter __instance)
        => StaticPortraitIdle.Attach(__instance, "merchant");
}
