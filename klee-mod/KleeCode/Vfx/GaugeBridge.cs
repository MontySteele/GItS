using HarmonyLib;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// The combat UI's one setup seam for the mod's tracked displays: the
/// end-of-turn docket, Kokomi's Plan strip, Klee's Spark counter and
/// Furina's Fanfare gauge. The
/// overhead Burst gauges and Kokomi's Charge row it used to build went with
/// the shipped kits (legacy cleanup stage 5).
/// </summary>
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Activate))]
internal static class NCombatUi_Activate_GaugeSetup
{
    [HarmonyPostfix]
    public static void Postfix(CombatState state)
    {
        if (NCombatRoom.Instance is not { } combatRoom)
        {
            return;
        }

        foreach (var player in state.Players)
        {
            TurnEndPreviewBridge.Setup(combatRoom, player);
        }

        KokomiPlanStrip.Setup(state);
        SparkCounter.Setup(state);
        FanfareCounter.Setup(state);
        DrainedCounter.Setup(state);
    }
}
