using System;
using BaseLib.Utils;
using HarmonyLib;

namespace KleeMod.Patches;

/// <summary>
/// THE MOD'S NAME ON BASELIB'S SOURCE LABELS (contact sheet, 2026-10-22:
/// "KleeMod" at the bottom left of every story event, and "WhatMod: KleeMod"
/// in tooltips).
///
/// BaseLib (not the base game) labels modded events, monsters, ancients and
/// tooltips with the mod they came from, through
/// <c>BaseLib.Utils.WhatMod.FindModName(Type)</c>. On game 0.111.0 its
/// assembly-to-mod map is never filled: the game's <c>Mod</c> carries an
/// <c>assemblies</c> list, and BaseLib's <c>CheckAssembly</c> returns before
/// it records the list's assemblies (installed BaseLib, decompiled
/// 2026-10-22). So it falls back to matching the type's ROOT NAMESPACE
/// against a manifest id, finds none ("KleeMod" is not "klee"), and prints
/// the namespace. Renaming the id or the namespace is a one-way door (saves,
/// Workshop, every type name); naming our own types here is not.
///
/// The postfix answers only for a type from this assembly, and only when
/// BaseLib already chose to print a name (its own show/hide settings run
/// before it is called). Every other mod's label is untouched.
/// </summary>
// Character scope: types from this assembly only; any other type returns
// BaseLib's own answer unchanged.
[HarmonyPatch(typeof(WhatMod), nameof(WhatMod.FindModName), new[] { typeof(Type) })]
public static class WhatMod_FindModName_TeyvatSpire_Patch
{
    /// <summary>The player-facing name of this mod.</summary>
    public const string DisplayName = "Teyvat Spire";

    [HarmonyPostfix]
    public static void Postfix(Type type, ref string? __result)
    {
        __result = Rename(type, __result);
    }

    /// <summary>Pure: our own types read "Teyvat Spire"; everything else,
    /// and a name BaseLib chose not to print, passes through.</summary>
    public static string? Rename(Type? type, string? result)
    {
        if (result == null || type == null) return result;
        return ReferenceEquals(type.Assembly, typeof(KleeMod).Assembly)
            ? DisplayName
            : result;
    }
}
