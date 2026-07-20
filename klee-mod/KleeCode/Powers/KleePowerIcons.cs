using HarmonyLib;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// Routes our powers' icons to klee.pck textures.
///
/// PowerModel's icon surface is NON-virtual -- PackedIconPath is a plain
/// getter, and Icon, IconPath and the preloader all resolve through it or
/// through ResolvedBigIconPath -- and our powers deliberately derive from the
/// raw PowerModel rather than BaseLib's CustomPowerModel (they are combat
/// mechanics owned by our own systems, not pool content), so BaseLib's
/// CustomPackedIconPath redirect never sees them. Patching the two PATH
/// getters fixes every consumer at once; returning a texture from get_Icon
/// alone would leave IconPath string consumers pointing at the atlas.
///
/// Each mapping is gated through KleePck.Path, so a missing pack (or a
/// missing per-element aura file) falls through to the original getter and
/// behaves exactly like today's placeholder state.
/// </summary>
internal static class KleePowerIcons
{
    internal static string? PathFor(PowerModel power) => power switch
    {
        SparkPower => KleePck.Path("klee/powers/spark.png"),
        BombPower => KleePck.Path("klee/powers/bomb.png"),
        BurstMeterPower => KleePck.Path("klee/powers/burst.png"),
        BombDamageUpPower => KleePck.Path("klee/powers/bomb_damage_up.png"),
        DetonationSplashPower => KleePck.Path("klee/powers/detonation_splash.png"),
        DetonationVulnPower => KleePck.Path("klee/powers/detonation_vuln.png"),
        BombAndSparkPerTurnPower => KleePck.Path("klee/powers/bomb_and_spark_per_turn.png"),
        SparkPerTurnPower => KleePck.Path("klee/powers/spark_per_turn.png"),
        ZeroCostAttacksUpPower => KleePck.Path("klee/powers/zero_cost_attacks_up.png"),
        SparkThresholdDownPower => KleePck.Path("klee/powers/spark_threshold_down.png"),
        ReactionBonusSparkEnergyPower => KleePck.Path("klee/powers/reaction_bonus_spark_energy.png"),
        AmpReactionUpPower => KleePck.Path("klee/powers/amp_reaction_up.png"),
        AuraPower aura => KleePck.Path(
            "klee/powers/aura_" + aura.Element.ToString().ToLowerInvariant() + ".png"),
        _ => null,
    };
}

[HarmonyPatch(typeof(PowerModel), nameof(PowerModel.PackedIconPath), MethodType.Getter)]
internal static class PowerModel_PackedIconPath_KleeIcons_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel __instance, ref string __result)
    {
        var path = KleePowerIcons.PathFor(__instance);
        if (path == null)
        {
            return true;
        }
        __result = path;
        return false;
    }
}

/// <remarks>
/// Also bypasses PowerModel's _resolvedBigIconPath cache for our powers,
/// which is fine: KleePck.Path caches its own existence check.
/// </remarks>
[HarmonyPatch(typeof(PowerModel), nameof(PowerModel.ResolvedBigIconPath), MethodType.Getter)]
internal static class PowerModel_ResolvedBigIconPath_KleeIcons_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel __instance, ref string __result)
    {
        var path = KleePowerIcons.PathFor(__instance);
        if (path == null)
        {
            return true;
        }
        __result = path;
        return false;
    }
}
