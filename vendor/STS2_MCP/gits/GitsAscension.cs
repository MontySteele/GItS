// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// CHOSEN ASCENSION, the sibling of GitsSeed.cs. A base-game CONTROL run is
// only comparable to a mod run at the same ascension, and without this the
// ascension is whatever the character's saved `PreferredAscension` says (the
// last level a person used): Silent embarked at A5 on every lane.
//
// WHY THE LEVEL MOVES WHEN A CHARACTER IS PICKED. Decompiled:
//
//   StartRunLobby.SetLocalCharacter(character)
//       -> SetSingleplayerAscensionAfterCharacterChanged(character.Id)
//          MaxAscension = stats.MaxAscension;
//          SyncAscensionChange(Math.Min(stats.PreferredAscension, MaxAscension));
//
// So a level set BEFORE the pick is overwritten by the pick. It goes on at
// the same moment as the seed: character chosen, confirm not yet fired. The
// embark then reads `_lobby.Ascension` (NCharacterSelectScreen, the
// singleplayer arm of the embark: `int ascensionToEmbark = _lobby.Ascension`).
//
// THE SETTER IS THE CLICK'S OWN PATH. An arrow press is
//
//   NAscensionPanel.IncrementAscension() -> SetAscensionLevel(Ascension + 1)
//       -> EmitSignal(AscensionLevelChanged)
//   NCharacterSelectScreen.OnAscensionPanelLevelChanged()
//       -> _lobby.SyncAscensionChange(_ascensionPanel.Ascension)
//
// and this endpoint calls `SetAscensionLevel(n)` on the screen's private
// `_ascensionPanel` (read by reflection, by name), so the signal, the lobby
// sync, the panel's text and its arrows all move exactly as they would for a
// person. Route "panel". If the lobby did not follow (the panel field was not
// found, or the panel already read n while the lobby did not, in which case
// `SetAscensionLevel` emits nothing) it falls back to the public
// `StartRunLobby.SyncAscensionChange(n)` directly. Route "lobby".
//
// ONE SIDE EFFECT, AND IT IS THE GAME'S. `SyncAscensionChange` calls
// `UpdatePreferredAscension`, which writes the new level into the profile's
// progress save as that character's PreferredAscension -- exactly what a
// click does. A lane profile is disposable; on lane 0 a chosen level becomes
// the owner's next default for that character.
//
// REFUSALS: not on character select, no lobby, a level below 0 or above the
// maximum (the panel's `_maxAscension`, else the lobby's `MaxAscension`,
// which is the value the screen copies into the panel), and a lobby already
// beginning its run (`SyncAscensionChange` would only log a warning).
//
// NOTHING HERE IS A RULES CHANGE. It selects which of the game's own
// ascension levels the run starts at, through the game's own control.
//
//   GET  /api/v1/gits/ascension
//        -> { status, message, route, requested, on_char_select,
//             lobby_ascension, panel_ascension, panel_max, lobby_max, max }
//   POST /api/v1/gits/ascension   { "ascension": 0 }
//        -> same shape; `lobby_ascension` is the read-back the embark uses.
//
// Routed from McpMod.HandleRequest - see PROVENANCE.md.

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text.Json;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;

namespace STS2_MCP;

public static partial class McpMod
{
    private static NAscensionPanel? GitsAscensionPanel(NCharacterSelectScreen? charSelect)
    {
        if (charSelect == null) return null;
        try { return GetInstanceFieldValue(charSelect, "_ascensionPanel") as NAscensionPanel; }
        catch { return null; }
    }

    private static int? GitsAscensionPanelMax(NAscensionPanel? panel)
    {
        if (panel == null) return null;
        try { return GetInstanceFieldValue(panel, "_maxAscension") is int max ? max : null; }
        catch { return null; }
    }

    private static Dictionary<string, object?> GitsAscensionReport(
        string message, string route, int? requested)
    {
        var charSelect = GitsSeedCharSelect();
        var panel = GitsAscensionPanel(charSelect);
        int? lobbyAscension = null, lobbyMax = null;
        bool? beginning = null;
        try
        {
            var lobby = charSelect?.Lobby;
            if (lobby != null)
            {
                lobbyAscension = lobby.Ascension;
                lobbyMax = lobby.MaxAscension;
                beginning = GetInstanceFieldValue(lobby, "_isBeginningRun") as bool?;
            }
        }
        catch { /* the lobby is torn down asynchronously; a read may race it */ }
        int? panelMax = GitsAscensionPanelMax(panel);

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = message,
            ["route"] = route,
            ["requested"] = requested,
            ["on_char_select"] = charSelect != null,
            ["lobby_ascension"] = lobbyAscension,
            ["panel_ascension"] = panel?.Ascension,
            ["panel_max"] = panelMax,
            ["lobby_max"] = lobbyMax,
            ["max"] = panelMax ?? lobbyMax,
            ["beginning_run"] = beginning
        };
    }

    private static Dictionary<string, object?> GitsAscensionApply(int ascension)
    {
        var charSelect = GitsSeedCharSelect();
        if (charSelect == null)
            return Error("Not on character select; pick the character first, "
                         + "then set the ascension before the confirm");
        var lobby = charSelect.Lobby;
        if (lobby == null)
            return Error("Character select has no run lobby");
        if (GetInstanceFieldValue(lobby, "_isBeginningRun") is true)
            return Error("The lobby is already beginning its run; the ascension is fixed");

        var panel = GitsAscensionPanel(charSelect);
        int max = GitsAscensionPanelMax(panel) ?? lobby.MaxAscension;
        if (ascension < 0)
            return Error($"Ascension {ascension} is below 0");
        if (ascension > max)
            return Error($"Ascension {ascension} is above this character's maximum "
                         + $"of {max} (the panel's own limit; unlock it by play)");

        string route = "none";
        if (lobby.Ascension != ascension && panel != null)
        {
            // The click's path: the signal carries it to the lobby.
            panel.SetAscensionLevel(ascension);
            route = "panel";
        }
        if (lobby.Ascension != ascension)
        {
            try
            {
                lobby.SyncAscensionChange(ascension);
                // AscensionChanged() on the screen repaints the panel from the
                // lobby, so the two agree whichever route fired.
                route = "lobby";
            }
            catch (Exception ex)
            {
                GD.PrintErr($"[STS2 MCP][GItS] ascension: lobby refused ({ex.Message})");
                return Error($"The lobby refused ascension {ascension}: {ex.Message}");
            }
        }

        string message = lobby.Ascension == ascension
            ? $"ascension {ascension} set (route {route})"
            : $"asked for ascension {ascension}, the lobby reads {lobby.Ascension}";
        return GitsAscensionReport(message, route, ascension);
    }

    private static void HandleGitsAscension(
        HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod == "GET")
            {
                var readTask = RunOnMainThread(
                    () => GitsAscensionReport("current", "none", null));
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

            if (parsed == null
                || !parsed.TryGetValue("ascension", out var elem)
                || elem.ValueKind != JsonValueKind.Number
                || !elem.TryGetInt32(out int ascension))
            {
                SendError(response, 400, "Missing or non-integer 'ascension' field");
                return;
            }

            var applyTask = RunOnMainThread(() => GitsAscensionApply(ascension));
            SendJson(response, applyTask.GetAwaiter().GetResult());
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] ascension endpoint failed: {ex}");
            try { SendError(response, 500, $"Ascension control failed: {ex.Message}"); }
            catch { /* response may already be closed */ }
        }
    }
}
