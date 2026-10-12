using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Multiplayer.Game.Lobby;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Abyss;

/// <summary>
/// THE SEAT LANES' SPIRAL ABYSS (2026-10-12): <c>python -m understudy.embark
/// --abyss</c> sets <see cref="EnvVar"/> on the launched game, and the run the
/// embark then starts from the ordinary character select carries the
/// <see cref="SpiralAbyss"/> modifier, exactly as a run started from the Abyss
/// button does. Seats only: a measurement instrument, never a player's switch.
/// Unset or empty, nothing here does anything.
///
/// WHY THE STANDARD SCREEN AND NOT THE CUSTOM ONE. The embark drives the
/// character select through the bridge (character, seed, ascension), and the
/// bridge has no reader for the Custom screen. So the modifier rides the
/// Standard lobby, along the same three seams the Custom screen's own run
/// passes through:
///
/// 1. <c>StartRunLobby.BeginRunForAllPlayers</c> runs on the host (or the
///    singleplayer lobby) only. With the variable set it hands on a modifier
///    list carrying a fresh <c>ToMutable()</c> of the canonical SpiralAbyss --
///    what a ticked Custom tickbox holds -- and leaves the lobby's own list
///    alone. The list goes to every client inside <c>LobbyBeginRunMessage</c>
///    (as <c>SerializableModifier</c>s, SavedProperties included), so in
///    co-op the HOST decides and both games build the same run; the client
///    needs no variable.
/// 2. <c>NCharacterSelectScreen.BeginRun</c> drops a Standard run's modifiers
///    (it logs an error and passes <c>Array.Empty</c>). A list carrying the
///    Abyss is carried past it instead, and the screen sees an empty one.
/// 3. <c>RunState.CreateForNewRun</c> takes the carried list, and the
///    Custom screen's <see cref="GameMode.Custom"/>, in place of the empty
///    list and <see cref="GameMode.Standard"/> the Standard screen passes.
///
/// From there the run is the Abyss button's run: the modifier's
/// <c>AfterRunCreated</c> clears its record, the choice page goes over Neow
/// (<see cref="AbyssChoicePage"/>), and the save carries the modifier.
/// </summary>
public static class AbyssLane
{
    /// <summary>The variable <c>understudy.embark --abyss</c> sets.</summary>
    public const string EnvVar = "GITS_ABYSS";

    /// <summary>Whether <paramref name="raw"/> asks for the Abyss: 1, true,
    /// yes or on, any case. Anything else, empty included, is no. PURE.</summary>
    public static bool ParseFlag(string? raw) =>
        (raw ?? string.Empty).Trim().ToLowerInvariant() is "1" or "true" or "yes" or "on";

    /// <summary>Whether this process's environment asks for the Abyss.</summary>
    public static bool Requested()
    {
        try
        {
            return ParseFlag(Environment.GetEnvironmentVariable(EnvVar));
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>Whether the lobby beginning a run should add the Abyss: asked
    /// for, a Standard lobby (a Custom lobby has its own tickbox and a Daily
    /// its own roll), not a client (only the host begins a run), and not
    /// already carried. PURE.</summary>
    public static bool ShouldAdd(bool requested, GameMode mode, bool isClient, bool alreadyHas) =>
        requested && mode == GameMode.Standard && !isClient && !alreadyHas;

    /// <summary>A new list: <paramref name="modifiers"/> and then
    /// <paramref name="abyss"/>. The lobby's own list is never touched.
    /// PURE.</summary>
    public static List<ModifierModel> With(IEnumerable<ModifierModel> modifiers, ModifierModel abyss)
    {
        var list = modifiers.ToList();
        list.Add(abyss);
        return list;
    }

    public static bool Carries(IEnumerable<ModifierModel>? modifiers) =>
        modifiers != null && modifiers.Any(m => m is SpiralAbyss);

    /// <summary>The list held between the character select's
    /// <c>BeginRun</c> and the run's creation, or null.</summary>
    private static List<ModifierModel>? _carried;

    /// <summary>Seam 2: hold a list carrying the Abyss, and answer what the
    /// Standard screen should see (empty where held). Any other list clears
    /// the hold and passes untouched.</summary>
    public static IReadOnlyList<ModifierModel> Hold(IReadOnlyList<ModifierModel> modifiers)
    {
        if (!Carries(modifiers))
        {
            _carried = null;
            return modifiers;
        }
        _carried = modifiers.ToList();
        return Array.Empty<ModifierModel>();
    }

    /// <summary>Seam 3: the held list and <see cref="GameMode.Custom"/> in
    /// place of an empty Standard run's, spending the hold; anything else
    /// passes untouched.</summary>
    public static void Release(ref IReadOnlyList<ModifierModel> modifiers, ref GameMode gameMode)
    {
        var held = _carried;
        if (held == null) return;
        if (modifiers.Count != 0 || gameMode != GameMode.Standard) return;
        _carried = null;
        modifiers = held;
        gameMode = GameMode.Custom;
    }
}

/// <summary>Seam 1, on the host or the singleplayer lobby.</summary>
[HarmonyPatch(typeof(StartRunLobby), "BeginRunForAllPlayers")]
internal static class StartRunLobby_BeginRunForAllPlayers_AbyssLane_Patch
{
    [HarmonyPrefix]
    private static void Prefix(StartRunLobby __instance, ref List<ModifierModel> modifiers)
    {
        try
        {
            if (!AbyssLane.ShouldAdd(
                    AbyssLane.Requested(), __instance.GameMode,
                    __instance.NetService.Type == NetGameType.Client,
                    AbyssLane.Carries(modifiers)))
            {
                return;
            }
            modifiers = AbyssLane.With(modifiers, ModelDb.Modifier<SpiralAbyss>().ToMutable());
            Log.Info($"[{KleeMod.ModId}] {AbyssLane.EnvVar}: this run carries the Spiral Abyss.");
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] {AbyssLane.EnvVar} could not add the Spiral Abyss: {e}");
        }
    }
}

/// <summary>Seam 2, on every player's character select.</summary>
[HarmonyPatch(typeof(NCharacterSelectScreen), nameof(NCharacterSelectScreen.BeginRun))]
internal static class NCharacterSelectScreen_BeginRun_AbyssLane_Patch
{
    [HarmonyPrefix]
    private static void Prefix(ref IReadOnlyList<ModifierModel> modifiers)
    {
        try
        {
            modifiers = AbyssLane.Hold(modifiers);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss lane hold failed: {e}");
        }
    }
}

/// <summary>Seam 3, where the run is built.</summary>
[HarmonyPatch(typeof(RunState), nameof(RunState.CreateForNewRun))]
internal static class RunState_CreateForNewRun_AbyssLane_Patch
{
    [HarmonyPrefix]
    private static void Prefix(ref IReadOnlyList<ModifierModel> modifiers, ref GameMode gameMode)
    {
        try
        {
            AbyssLane.Release(ref modifiers, ref gameMode);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Spiral Abyss lane release failed: {e}");
        }
    }
}
