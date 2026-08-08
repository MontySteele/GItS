// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// Understudy P1.5, spec item 1: CHOSEN SEEDS. R95 accepted read-back seeds for
// the P1 soak and gated chosen seeds at "the first cross-build comparison";
// R104 promoted that gate to NEXT. This file is the mechanism.
//
// WHAT UPSTREAM ALREADY HAS, AND WHY IT REFUSES
//
// `menu_select` takes an optional `seed`, and `ExecuteCharacterSelectMenuOption`
// applies it with `charSelect.Lobby.SetSeed(seed)` -- but only after a
// `charSelect.Lobby == null` guard whose failure message is "Seeded embark is
// not supported for standard singleplayer from this API". Phase-0 hit exactly
// that message and recorded the whole seed route as unreachable.
//
// THE GUARD IS NOT WHAT THE GAME DOES. Decompiled v0.107.1:
//
//   NCharacterSelectScreen.InitializeSingleplayer()
//       _lobby = new StartRunLobby(GameMode.Standard,
//                                  new NetSingleplayerGameService(), this, 1);
//
//   StartRunLobby.SetSeed(string? seed)
//       if ((uint)(NetService.Type - 1) > 1u) throw;   // Singleplayer=1, Host=2
//
// (That is the NetService guard, and it is the one this file read. It is NOT
// the only guard in `SetSeed` -- see the EB-15 note below, which cost four
// live runs to find: a second check refuses `GameMode.Standard` outright.)
//
// So singleplayer DOES have a lobby and SetSeed DOES accept singleplayer. The
// upstream guard is defensive, not descriptive. This file therefore does not
// fight it: it sets the seed through its OWN endpoint, before the embark that
// upstream's `confirm` performs, and leaves upstream's arm untouched.
//
// TWO ROUTES, BOTH FIRST-PARTY, ONE PREFERENCE
//
//   route "lobby"           charSelect.Lobby.SetSeed(seed)
//   route "debug_override"  NGame.Instance.DebugSeedOverride = seed
//
// Both land at the same line, `StartRunLobby.BeginRunForAllPlayersIfAllReady`:
//
//   string seed = NGame.Instance?.DebugSeedOverride != null
//       ? NGame.Instance.DebugSeedOverride
//       : (Seed == null ? SeedHelper.GetRandomSeed()
//                       : SeedHelper.CanonicalizeSeed(Seed));
//
// `lobby` is preferred because it is the channel the game's own Custom-run
// screen uses and it is scoped to the run being started. `debug_override` is
// the fallback for the moment the lobby genuinely is null; it is GLOBAL and
// STICKY, which is why `Clear` exists and why the harness is expected to call
// it.
//
// EB-15: ON THE STANDARD SINGLEPLAYER ARM THE PREFERENCE IS ACADEMIC -- THE
// LOBBY ROUTE CANNOT FIRE, AND THE REASON IS NOT THE GUARD NAMED ABOVE. Four
// live runs took `debug_override`; the fourth read the endpoint's own report
// on both sides of the POST and the game said why in godot.log:
//
//   [STS2 MCP][GItS] seed: lobby route failed
//       (Seed should not be changed in standard mode!)
//
// So the lobby is NOT null (`on_char_select: true`, and `lobby_seed` reads
// back the seed afterwards because SetSeed assigns `Seed` and THEN throws).
// `StartRunLobby.SetSeed` refuses on the GameMode, not on `NetService.Type`,
// and `InitializeSingleplayer` builds its lobby with `GameMode.Standard` --
// so every standard singleplayer run fails this route by construction. The
// stranded `Lobby.Seed` is harmless: `DebugSeedOverride` outranks it at
// BeginRun and `Clear` empties both channels.
//
// The arm is KEPT rather than deleted, because it is the route a Custom-run
// or a hosted lobby would take and it reports itself accurately either way.
// Nobody should read "two routes work" out of this file.
//
// NCharacterSelectScreen.AfterInitialized() sets DebugSeedOverride = null
// when the screen opens, so a seed set while ON character select survives to
// embark and a seed set before it does not -- the endpoint reports which route
// fired so a caller never has to guess.
//
// NOTE ON CANONICALISATION. The lobby route canonicalises for us at BeginRun;
// the debug route does NOT. Both are canonicalised here instead, through the
// game's own SeedHelper, so the seed the caller asked for and the seed the run
// reads back are the same string on both routes.
//
// NOTHING HERE IS A RULES CHANGE. A seed selects which run the generators
// produce. It does not alter a generator, a constant, a reward table or a
// pilot. Choosing the run is the entire point: one variable per measurement
// window.
//
//   GET  /api/v1/gits/seed
//        -> { status, chosen, route, lobby_seed, debug_override, on_char_select }
//   POST /api/v1/gits/seed   { "seed": "SSRWEGLNRG" }
//        -> same shape; `route` is the route that actually fired.
//   POST /api/v1/gits/seed   { "seed": null }   (or {"clear": true})
//        -> clears BOTH channels and reports the cleared state.
//
// Routed from McpMod.HandleRequest - see PROVENANCE.md.

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>The seed this endpoint last asked for, or null. Reported back
    /// so a caller can tell "nobody chose" from "the game rolled its own".</summary>
    private static string? _gitsChosenSeed;

    private static NCharacterSelectScreen? GitsSeedCharSelect()
    {
        var tree = Engine.GetMainLoop() as SceneTree;
        if (tree?.Root == null) return null;
        var screen = FindFirst<NCharacterSelectScreen>(tree.Root);
        return screen != null && IsNodeVisible(screen) ? screen : null;
    }

    private static Dictionary<string, object?> GitsSeedReport(
        string message, string route)
    {
        var charSelect = GitsSeedCharSelect();
        string? lobbySeed = null;
        try { lobbySeed = charSelect?.Lobby?.Seed; }
        catch { /* the lobby is torn down asynchronously; a read may race it */ }

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = message,
            ["chosen"] = _gitsChosenSeed,
            ["route"] = route,
            ["lobby_seed"] = lobbySeed,
            ["debug_override"] = NGame.Instance?.DebugSeedOverride,
            ["on_char_select"] = charSelect != null
        };
    }

    private static Dictionary<string, object?> GitsSeedClear()
    {
        _gitsChosenSeed = null;
        try
        {
            var charSelect = GitsSeedCharSelect();
            // SetSeed(null) is the lobby's own "no chosen seed" state -- it is
            // what a lobby starts in, and BeginRun falls back to a random seed
            // on it. Guarded because SetSeed throws on a CLIENT lobby.
            if (charSelect?.Lobby != null) charSelect.Lobby.SetSeed(null);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] seed clear: lobby refused ({ex.Message})");
        }
        if (NGame.Instance != null) NGame.Instance.DebugSeedOverride = null;
        return GitsSeedReport("chosen seed cleared on both channels", "none");
    }

    private static Dictionary<string, object?> GitsSeedApply(string seed)
    {
        // The game's own canonicalisation, so a caller may pass lower case,
        // 'O' or 'I' and still read back what it asked for.
        seed = SeedHelper.CanonicalizeSeed(seed);
        _gitsChosenSeed = seed;

        var charSelect = GitsSeedCharSelect();
        if (charSelect?.Lobby != null)
        {
            try
            {
                charSelect.Lobby.SetSeed(seed);
                // The debug override wins over the lobby seed at BeginRun, so a
                // stale one left by an earlier call would silently outrank the
                // route that just succeeded.
                if (NGame.Instance != null) NGame.Instance.DebugSeedOverride = null;
                return GitsSeedReport($"seed '{seed}' set on the run lobby", "lobby");
            }
            catch (Exception ex)
            {
                GD.PrintErr($"[STS2 MCP][GItS] seed: lobby route failed ({ex.Message}); "
                            + "falling back to the debug override");
            }
        }

        if (NGame.Instance == null)
            return Error("No NGame instance; neither seed route is reachable");

        NGame.Instance.DebugSeedOverride = seed;
        return GitsSeedReport(
            $"seed '{seed}' set on the global debug override (STICKY - clear it "
            + "when the run has started)", "debug_override");
    }

    private static void HandleGitsSeed(
        HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod == "GET")
            {
                var readTask = RunOnMainThread(() => GitsSeedReport("current", "none"));
                SendJson(response, readTask.GetAwaiter().GetResult());
                return;
            }

            if (request.HttpMethod != "POST")
            {
                SendError(response, 405, "Method not allowed");
                return;
            }

            string body;
            using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
                body = reader.ReadToEnd();

            Dictionary<string, JsonElement>? parsed;
            try
            {
                parsed = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(body);
            }
            catch
            {
                SendError(response, 400, "Invalid JSON");
                return;
            }

            if (parsed == null)
            {
                SendError(response, 400, "Missing body");
                return;
            }

            bool clear = parsed.TryGetValue("clear", out var clearElem)
                         && clearElem.ValueKind == JsonValueKind.True;
            string? seed = null;
            if (parsed.TryGetValue("seed", out var seedElem))
            {
                seed = seedElem.ValueKind == JsonValueKind.String
                    ? seedElem.GetString()
                    : null;
                if (seedElem.ValueKind == JsonValueKind.Null) clear = true;
            }
            else if (!clear)
            {
                SendError(response, 400, "Missing 'seed' field (send null to clear)");
                return;
            }

            if (clear || string.IsNullOrWhiteSpace(seed))
            {
                var clearTask = RunOnMainThread(GitsSeedClear);
                SendJson(response, clearTask.GetAwaiter().GetResult());
                return;
            }

            var applyTask = RunOnMainThread(() => GitsSeedApply(seed!.Trim()));
            SendJson(response, applyTask.GetAwaiter().GetResult());
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] seed endpoint failed: {ex}");
            try { SendError(response, 500, $"Seed control failed: {ex.Message}"); }
            catch { /* response may already be closed */ }
        }
    }
}
