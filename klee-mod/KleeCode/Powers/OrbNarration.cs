using System;
using HarmonyLib;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// SEAT PAGE BACKLOG (2026-10-19): "Orb passives and evokes at the start and
/// end of a turn are narrated nowhere; `ResolutionLedger` files card plays
/// only." A Defect control seat could not tell a Lightning passive from an
/// enemy's own damage. Each orb that fires now files one page event
/// (<see cref="ResolutionLedger.NoteOrb"/>), and the page prints it under
/// "Since last page" ("Lightning orb: passive x3").
///
/// THREE DOORS, read off the base game (0.111 decompile): every passive that
/// counts the hooks goes through <c>OrbModel.TriggerPassive</c> (the turn-end
/// and turn-start triggers call it); <c>OrbCmd.Passive</c> with
/// <c>countAffectedByHooks: false</c> calls <c>OrbModel.Passive</c> directly,
/// so that door is filed there; and every evoke goes through the private
/// <c>OrbCmd.Evoke</c> (EvokeNext, EvokeLast). Names only: what the orb then
/// did is the board's, and a hit inside a card play is already on that play's
/// line. Display only; nothing here changes a number.
/// </summary>
public static class OrbNarration
{
    /// <summary>The orb's printed title, or "" and never a throw.</summary>
    internal static string Named(OrbModel? orb)
    {
        try { return orb?.Title.GetFormattedText() ?? string.Empty; }
        catch (Exception) { return string.Empty; }
    }

    internal static void Passive(OrbModel? orb)
    {
        if (orb == null) return;
        ResolutionLedger.NoteOrb(Named(orb), evoked: false);
    }

    internal static void Evoked(OrbModel? orb)
    {
        if (orb == null) return;
        ResolutionLedger.NoteOrb(Named(orb), evoked: true);
    }
}

/// <summary>A passive that counts the hooks (<see cref="OrbNarration"/>).
/// </summary>
[HarmonyPatch(typeof(OrbModel), nameof(OrbModel.TriggerPassive))]
internal static class OrbModel_TriggerPassive_Narration_Patch
{
    private static void Prefix(OrbModel __instance) =>
        OrbNarration.Passive(__instance);
}

/// <summary>A passive that skips the hooks: <c>OrbCmd.Passive</c> calls
/// <c>OrbModel.Passive</c> itself only when <c>countAffectedByHooks</c> is
/// false; otherwise it goes through <c>TriggerPassive</c>, filed above.
/// </summary>
[HarmonyPatch(typeof(OrbCmd), nameof(OrbCmd.Passive))]
internal static class OrbCmd_Passive_Narration_Patch
{
    private static void Prefix(OrbModel orb, bool countAffectedByHooks)
    {
        if (!countAffectedByHooks) OrbNarration.Passive(orb);
    }
}

/// <summary>Every evoke (<see cref="OrbNarration"/>).</summary>
[HarmonyPatch(typeof(OrbCmd), "Evoke")]
internal static class OrbCmd_Evoke_Narration_Patch
{
    private static void Prefix(OrbModel evokedOrb) =>
        OrbNarration.Evoked(evokedOrb);
}
