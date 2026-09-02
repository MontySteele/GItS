using System.Collections.Generic;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;

namespace KleeMod.Patches;

/// <summary>
/// `EB-274`. ENTERING A SHOP AS ONE OF OUR CHARACTERS THROWS, EVERY TIME.
///
///     InvalidOperationException: Expected BoundObject to be a SpineSprite,
///     but it is a Sprite2D!
///       at MegaSpineBinding..ctor
///       at NMerchantCharacter._Ready
///
/// One line per shop, in the Kokomi round-one log of 2026-09-02 and in the
/// Klee session log of 2026-09-01 21:08 -- so it is not a Kokomi defect and
/// never was. It is a defect of every character whose merchant portrait is a
/// picture.
///
/// WHY IT HAPPENS, from the game's own two methods:
///
///     public override void _Ready() =&gt;
///         this.RunWhenSpineReady(new MegaSprite(GetChild(0)), ...);
///     public void PlayAnimation(string anim, bool loop = false) =&gt;
///         new MegaSprite(GetChild(0)).GetAnimationState()...
///
/// Both build a <c>MegaSprite</c> on child 0 UNCONDITIONALLY, and
/// <c>MegaSpineBinding</c>'s constructor validates: <c>BoundObject.GetClass()
/// != SpineClassName</c> throws. Every base-game merchant portrait is a real
/// Spine rig; ours is a <c>Sprite2D</c>, because BaseLib's scene-conversion
/// factory builds the whole <c>NMerchantCharacter</c> tree around a bare
/// texture node (`Klee.CustomMerchantAnimPath`, and `tools/build_pck.ps1`
/// writes the three one-node scenes). There is no Spine data to give it: the
/// 2026-08-05 spine investigation measured that the MegaDot editor our pack
/// build runs has no Spine importer at all, so a `.tscn` naming SpineSprite
/// can only be made to load by borrowing a base-game rig -- which is art we do
/// not have and would not ship.
///
/// SO THE BINDING IS SKIPPED, WHICH IS THE ROW'S SECOND OPTION IN ITS OWN
/// WORDS ("or skip the binding for a non-Spine merchant"). Both methods do
/// exactly ONE thing -- start, or set, the `relaxed_loop` idle -- so a
/// prefix that refuses them loses the idle and nothing else. That was already
/// the state of the world: `Klee.CustomMerchantAnimPath` has carried the
/// comment "the sprite still renders, only the relaxed_loop idle is lost.
/// Unfixable without patching game code -- accepted" since 2026-07-20. What
/// changes is that the loss now costs nothing in the log, instead of an
/// exception the Godot bridge swallows and prints with a stack trace that
/// reads like a fault.
///
/// THE GUARD IS THE GAME'S OWN QUESTION, ASKED FIRST. <c>MegaSprite</c>'s
/// <c>SpineClassName</c> is <c>"SpineSprite"</c> and the validator compares it
/// to <c>GetClass()</c>; <see cref="BindsSpine"/> asks the same comparison of
/// the same node before the constructor can throw on it. A real Spine merchant
/// answers true and runs the original untouched, so the base cast is
/// byte-identical in behaviour and this is inert for every character but ours.
///
/// AND IT IS THE GAME'S OWN GUARD, NOT AN INVENTED ONE. The merchant's sibling
/// <c>NRestSiteCharacter</c> reaches the identical constructor through
/// <c>GetChildSpineNodes()</c>, whose whole filter is
/// <c>if (!(current.GetClass() != "SpineSprite"))</c> -- so the rest site drops
/// non-Spine children and has never thrown on our portraits, which is exactly
/// why the campfire works today and the shop does not. This prefix asks the
/// merchant the question the rest site already asks.
///
/// SHIPPED, NOT QUARANTINED, on `Vfx/NonFiniteCardGuard.cs`'s and
/// `CustomTargetControllerNavigationPatch.cs`'s precedent and for their reason:
/// the failing code is the base GAME's, reached by any character whose
/// merchant portrait is not a Spine rig, and all three of ours are. Scoping it
/// to one prototype arm would leave the throw armed for Klee and Furina, which
/// is where it was first logged. It is flag-independent by construction --
/// there is no arm read anywhere in this file -- which is also what the row's
/// acceptance asks for: a shop entered as Kokomi AND as Klee logs no
/// exception, with `KOKOMI_OVERHAUL` on or off.
/// </summary>
internal static class MerchantSpineBinding
{
    /// <summary>
    /// <c>MegaSprite.SpineClassName</c>, which is the string
    /// <c>MegaSpineBinding.ValidateBoundObject</c> compares <c>GetClass()</c>
    /// against before it throws. Held as a constant rather than read off the
    /// protected property because the property is an instance member of the
    /// very object we are refusing to construct.
    /// </summary>
    internal const string SpineClass = "SpineSprite";

    /// <summary>
    /// Would <c>new MegaSprite(child)</c> survive? PURE, and it takes the
    /// class NAME rather than the node, so the one decision this file makes is
    /// assertable headlessly -- `Node.GetClass()` is a native call and is
    /// outside the KleeTests boundary (README, "The headless boundary").
    ///
    /// A null name is a node the caller could not reach at all (a merchant with
    /// no children), and that is refused for the same reason a Sprite2D is:
    /// <c>GetChild(0)</c> on an empty node is itself an error, and the game's
    /// two methods index it without checking.
    /// </summary>
    internal static bool BindsSpineClass(string? childClass) =>
        childClass == SpineClass;

    /// <summary>
    /// The live form: does this merchant node carry a Spine child the game may
    /// bind? Null-safe and child-count-safe, because the whole point is to be
    /// asked before the game indexes.
    /// </summary>
    internal static bool BindsSpine(Node? merchant)
    {
        if (merchant == null || merchant.GetChildCount() == 0) return false;
        var child = merchant.GetChild(0);
        return child != null && BindsSpineClass(child.GetClass());
    }

    /// <summary>
    /// Said ONCE per process, not once per shop. The row's complaint is log
    /// volume that "reads like a fault in the console"; replacing one
    /// exception per shop with one warning per shop would be the same defect
    /// in a quieter font.
    /// </summary>
    private static readonly HashSet<string> Said = new();

    internal static void NoteOnce(string what)
    {
        if (!Said.Add(what)) return;
        Log.Info(
            $"[{KleeMod.ModId}] merchant portrait is not a Spine rig; skipping "
          + $"{what} (the idle animation, and nothing else). EB-274.");
    }

    /// <summary>Test seam: forget what has been said. The mod never calls
    /// it.</summary>
    internal static void ResetAll() => Said.Clear();
}

/// <summary>
/// `EB-274`, the throw itself. <c>_Ready</c> builds the binding to start the
/// idle loop; with no Spine child there is no idle to start, so the whole
/// method is skipped rather than half-run.
/// </summary>
[HarmonyPatch(typeof(NMerchantCharacter), "_Ready")]
internal static class NMerchantCharacter_Ready_SpineGuard_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(NMerchantCharacter __instance)
    {
        if (MerchantSpineBinding.BindsSpine(__instance)) return true;
        MerchantSpineBinding.NoteOnce("the merchant's idle animation");
        return false;
    }
}

/// <summary>
/// `EB-274`, the same constructor reached from the other side.
/// <c>PlayAnimation</c> is public and is what <c>_Ready</c>'s callback calls,
/// so leaving it unguarded would move the throw from boot to whenever anything
/// asks the merchant to emote.
/// </summary>
[HarmonyPatch(typeof(NMerchantCharacter), "PlayAnimation")]
internal static class NMerchantCharacter_PlayAnimation_SpineGuard_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(NMerchantCharacter __instance)
    {
        if (MerchantSpineBinding.BindsSpine(__instance)) return true;
        MerchantSpineBinding.NoteOnce("a merchant animation request");
        return false;
    }
}
