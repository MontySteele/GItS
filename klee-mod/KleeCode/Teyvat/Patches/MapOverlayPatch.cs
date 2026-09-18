using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;

namespace KleeMod.Teyvat.Patches;

/// <summary>
/// THE MAP SCREEN GETS THE NATION OVERLAY -- the one seam
/// <see cref="KleeMod.Teyvat.MapOverlay"/> hangs off.
///
/// WHY `Open` AND NOT `_Ready`. The overlay's content depends on WHICH ACT the
/// run is standing in, and the act changes under a map screen that was built
/// once. `_Ready` fires at construction; `Open` fires every time the screen is
/// shown, which is exactly the moment the question "which face is this" has an
/// answer. `MapOverlay.Attach` is idempotent for precisely that reason: it
/// removes the overlay it added last time before adding this one, so a screen
/// reused across two acts never carries Mondstadt's mark into Liyue.
///
/// This is also the seam public sources already use for a map-screen overlay --
/// `review/dispatch3/s12-public-patterns/s12c-act-map.md`, the "Map-screen
/// overlay" row: sts2-concept-map postfixes `NMapScreen.Open` and attaches its
/// own Godot node as a child so visibility follows the screen, and
/// Act4FinalAscent does the same on `_Ready`. Both are named there with commit
/// pins; neither was copied.
///
/// THE TARGET IS RESOLVED RATHER THAN DECLARED, because the arity of `Open` is
/// not in this repo. `game_ref/` holds no decompile of the map screen, so
/// `[HarmonyPatch(typeof(NMapScreen), "Open")]` would be a bet on there being
/// exactly one overload -- and Harmony raises on an ambiguous match, which
/// would fail the whole boot rather than this one dressing. `TargetMethods`
/// takes every declared `Open` instead, and falls back to `_Ready` if the name
/// ever moves; arming zero methods is reported by
/// `KleePatchBootstrap` as the failure it is, loudly and on its own.
///
/// ARM OFF IS BYTE-IDENTICAL. The postfix's first statement is
/// `MapOverlay.Attach`, whose first question is
/// <see cref="KleeMod.Teyvat.MapOverlay.ShouldAttach"/>, which leads with
/// `TeyvatFrame.Enabled`. With the flag off the method adds nothing, removes
/// nothing that was never added, and never touches the scene tree.
/// </summary>
[HarmonyPatch]
internal static class NMapScreen_Open_TeyvatOverlay_Patch
{
    private static IEnumerable<MethodBase> TargetMethods()
    {
        var opens = AccessTools.GetDeclaredMethods(typeof(NMapScreen))
            .Where(m => m.Name == "Open")
            .Cast<MethodBase>()
            .ToList();
        if (opens.Count > 0)
        {
            return opens;
        }

        var ready = AccessTools.DeclaredMethod(typeof(NMapScreen), "_Ready");
        return ready != null ? new MethodBase[] { ready } : Array.Empty<MethodBase>();
    }

    private static void Postfix(NMapScreen __instance) => MapOverlay.Attach(__instance);
}
