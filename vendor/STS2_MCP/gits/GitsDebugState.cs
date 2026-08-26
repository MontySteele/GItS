// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// EB-142: A DEV-ONLY DOOR FOR SETTING UP A BOARD, SO A SCENARIO CAN BE RUN.
//
// WHY THIS EXISTS. `gits/GitsGiveCard.cs` (EB-52) made a chosen CARD reachable;
// it did not make a chosen BOARD reachable. A targeted correctness check --
// "put Powder Charge in hand, put two Sparks in the bank, put a bomb on the
// enemy, play it, assert the detonate bonus is +4" -- is one grant and three
// numbers, and the three numbers were the part nobody could arrange. Reaching
// Sparks 2 by playing Klee cards takes a fight; reaching it here takes one
// POST. The alternative is what the repo did instead, which is to assert the
// arithmetic in tier0 and hope the C# agrees -- and `lint_constant_parity`
// exists precisely because hoping is not a check.
//
// THE DESIGN CONSTRAINT, INHERITED FROM GitsSeed AND GitsGiveCard.
// GitsSeed SELECTS which run the generators produce. GitsGiveCard SELECTS a
// card the game's own pools already contain and hands it to the game's own
// acquisition machinery. This file is held to the same line, one step down:
// every write here goes through the game's OWN mutator for that number, and
// there is no mutator here that the game does not already have.
//
//   set_hp        -> CreatureCmd.SetCurrentHp(creature, amount)
//                    the command, not the private `CurrentHp` setter, so
//                    AfterCurrentHpChanged fires and a relic that watches HP
//                    (Red Skull) sees the change the same way it sees a hit.
//   set_energy    -> PlayerCmd.SetEnergy(amount, player)
//   set_block     -> creature.LoseBlockInternal / GainBlockInternal
//                    THE ONE HOOK-FREE WRITE, and deliberately so: there is no
//                    `CreatureCmd.SetBlock`, and routing a debug set through
//                    GainBlock would run the Dexterity / ModifyBlockGained
//                    chain, so a caller asking for 0 Block on an enemy would
//                    get whatever the chain made of 0. A setup verb has to
//                    land the number it was given or it is not a setup verb.
//   set_resource  -> the registered CustomResource's own `Amount` setter,
//                    which is the property BaseLib's own gain/spend paths
//                    write (`SparkPower.Spend` ends in `power.Amount -= n`).
//
// WHAT IS DELIBERATELY *NOT* HERE, and both are follow-ups rather than
// oversights:
//   * enemy spawning -- the encounter is generated content and choosing one
//     is `GitsSeed`'s job (pick the run), not this file's. A scenario that
//     needs two enemies routes to a fight that has two.
//   * status / power application -- `PowerCmd.Apply` needs a
//     PlayerChoiceContext and an applier, and "who applied this Vulnerable"
//     is load-bearing for half the powers in the game. A route that made one
//     up would be minting state rather than selecting it. Until that is
//     designed, a scenario applies a status by PLAYING the card that applies
//     it, which is also the more honest test.
//
// REFLECTION FOR THE RESOURCE HALF ONLY, and for the reason
// `gits/GitsResources.cs` states: BaseLib's `CustomResourcePatches` registry is
// `internal`, and BaseLib is a Workshop mod that may not be installed at all. A
// compile-time reference would make the bridge refuse to load without it. That
// file's private registry probe is reused here rather than re-walked -- one
// cache, one failure mode. GitsResources.cs stays a READ-ONLY serialiser; the
// write lives here, where a reader looking for "who can move a meter" finds it.
//
// WHAT A RUN THAT USED THIS IS, AND IS NOT. Exactly what GitsGiveCard says,
// for exactly the same reason: its board is not a board the game's own play
// produced, so nothing measured on it -- not a winrate, not an HP curve, not a
// damage average -- is comparable to any other run, and it is not a measurement
// of anything at all. Every successful write carries a `guardrail` field saying
// so, and `understudy/bridge.py` stamps the same sentence on the harness log.
// Guardrail-7 is unchanged and this route cannot weaken it: a bot cannot see
// the screen either way, and this route emits no claim about look or feel.
//
// REFUSALS, AND WHY EACH ONE IS HERE.
//   * no run in progress   -- there is no player to write to.
//   * multiplayer          -- IDENTICAL to give_card's refusal and for the
//                             identical reason: these writes do not go through
//                             the action-queue synchronizer, so peers would
//                             diverge. Upstream hard-blocks SP/MP mismatch at
//                             dispatch; this route sits outside that dispatcher
//                             (like speed, seed and give_card) so it checks
//                             itself.
//   * no combat in progress -- every op here writes combat state. Out of
//                             combat there is no energy, no block and no
//                             resource to move, and a silent no-op wearing an
//                             `ok` is the failure give_card's combat-pile
//                             refusal already names.
//   * unknown creature      -- refused with the name echoed and the living
//                             entity ids listed, because the id the caller
//                             wants is the one the WIRE just handed it.
//   * unknown resource      -- refused with the registered ids listed. No
//                             fuzzy match: a near-miss write moves the wrong
//                             meter and the log says the right one moved.
//   * hp <= 0               -- refused. `SetCurrentHp(0)` leaves a creature at
//                             zero without running the death path, which is a
//                             wedged fight wearing an `ok` (EB-91's shape).
//                             Killing something is a play's job.
//
//   GET  /api/v1/gits/debug_state
//        -> { status, message, guardrail, run_in_progress, combat_in_progress,
//             ops, resources, creatures }
//   POST /api/v1/gits/debug_state
//        { "op": "set_resource", "resource": "KLEEMOD_SPARK", "amount": 2,
//          "why": "EB-142 spark-gate scenario" }
//        { "op": "set_energy", "amount": 3, "why": "..." }
//        { "op": "set_hp",    "who": "player"|"JAW_WORM_0", "amount": 30, ... }
//        { "op": "set_block", "who": "player"|"JAW_WORM_0", "amount": 0,  ... }
//        -> { status, message, guardrail, op, who, before, after, why }
//
// `why` IS REQUIRED AND IS LOGGED. A board change nobody can account for later
// is worse than no scenario: the same rule `harness give-card --why` follows,
// and the same reason. It is echoed on the response so the harness row and the
// game log carry one string.
//
// TWO OPS ANSWER WITH AN `after`, TWO ANSWER `queued`, AND THE RESPONSE SAYS
// WHICH. `set_resource` and `set_block` are synchronous writes -- a property
// set and two internal calls -- so the response carries the before/after pair
// the write actually produced. `set_hp` and `set_energy` go through async
// COMMANDS that run health-bar and energy visuals, and awaiting one from inside
// the main-thread frame drain is the deadlock GitsGiveCard's header describes;
// those are queued through the game's own no-await helper and answer
// `queued: true` with the value requested, which the caller confirms by reading
// the next state -- the same contract `play_card` and `give_card` already have.
// `queued` is a FIELD and not a convention: a caller that treats the two the
// same way is a caller whose next assertion races the visual.
//
// PIN NOTE. This adds one `else if` arm to `McpMod.HandleRequest` -- the
// fourth, after speed (W2), seed (P1.5) and give_card (EB-52) -- marked in-file
// with `GItS LOCAL EDIT`. Routed from McpMod.HandleRequest; recorded in
// PROVENANCE.md, which also carries what it means for a pin refresh.

using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Reflection;
using System.Text.Json;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Runs;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>The sentence every successful write carries, and it is a field
    /// on the wire rather than a comment for the reason GitsGiveCard's is: a
    /// caveat outside the record is a caveat lost the moment two records are
    /// concatenated.</summary>
    private const string GitsDebugStateGuardrail =
        "DEV ROUTE. This combat's board was set by hand, so it is not a board "
        + "the game's own play produced and nothing measured on it is "
        + "comparable to any other run. Use it for a targeted correctness "
        + "check, never for a number.";

    private static readonly string[] GitsDebugStateOps =
        { "set_resource", "set_energy", "set_hp", "set_block" };

    // ------------------------------------------------------- resources ----

    /// <summary>
    /// Set one registered CustomResource's amount on `playerCombatState`, and
    /// report `(ok, before, after)`.
    ///
    /// Walks the SAME registry `GitsResourceSnapshot` reads, through the same
    /// cached probe in gits/GitsResources.cs -- one lookup, one failure mode,
    /// and a bridge without BaseLib refuses here instead of throwing.
    /// </summary>
    private static (bool ok, int before, int after) GitsDebugSetResource(
        object? playerCombatState, string resourceId, int amount)
    {
        if (playerCombatState == null) return (false, 0, 0);
        var registry = GitsResourceRegistry();
        if (registry == null) return (false, 0, 0);
        try
        {
            if (registry.GetValue(null) is not IEnumerable handlers)
                return (false, 0, 0);
            foreach (var handler in handlers)
            {
                if (handler == null) continue;
                try
                {
                    var getter = handler.GetType().GetProperty("GetResource")
                        ?.GetValue(handler) as Delegate;
                    if (getter == null) continue;
                    var resource = getter.DynamicInvoke(playerCombatState);
                    if (resource == null) continue;
                    var type = resource.GetType();
                    var id = type.GetProperty("Id")?.GetValue(resource) as string;
                    if (!string.Equals(id, resourceId,
                                       StringComparison.OrdinalIgnoreCase))
                        continue;
                    var prop = type.GetProperty("Amount");
                    if (prop == null || !prop.CanWrite) return (false, 0, 0);
                    var before = prop.GetValue(resource) is int b ? b : 0;
                    prop.SetValue(resource, amount);
                    var after = prop.GetValue(resource) is int a ? a : amount;
                    return (true, before, after);
                }
                catch
                {
                    // One misbehaving mod's resource must not cost the write
                    // every other mod's. Skip it and keep walking -- the same
                    // rule the read side follows.
                }
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] debug_state resource write failed: {ex.Message}");
        }
        return (false, 0, 0);
    }

    // ------------------------------------------------------- creatures ----

    /// <summary>
    /// The entity id the WIRE hands out for an enemy, synthesised exactly the
    /// way `McpMod.StateBuilder.BuildEnemyState` synthesises it
    /// (`{monster id}_{ordinal}`, counted over the same living-enemy list in
    /// the same order). A caller names an enemy by the string the last GET
    /// gave it; if the two spellings ever diverge, a scenario's target is a
    /// creature nobody chose.
    /// </summary>
    private static Dictionary<string, Creature> GitsDebugLivingEnemies(
        CombatState combat)
    {
        var byId = new Dictionary<string, Creature>(
            StringComparer.OrdinalIgnoreCase);
        var counts = new Dictionary<string, int>();
        foreach (var creature in combat.Enemies)
        {
            if (!creature.IsAlive) continue;
            var baseId = SafeGetText(() => creature.Monster?.Id.Entry);
            if (string.IsNullOrWhiteSpace(baseId)) baseId = "unknown";
            counts.TryGetValue(baseId, out var n);
            counts[baseId] = n + 1;
            byId[$"{baseId}_{n}"] = creature;
        }
        return byId;
    }

    /// <summary>`who` -> the creature it names, or null. "player" (and the
    /// empty string) is the local player's creature; anything else is matched
    /// against the wire's entity ids first and the display title second, for
    /// the reason `soak._hazard_event` states: an id is the thing itself, a
    /// title is loc data a wording pass moves.</summary>
    private static Creature? GitsDebugResolve(
        string who, Player player, CombatState combat, out string resolved)
    {
        var key = (who ?? "").Trim();
        if (key.Length == 0 || string.Equals(key, "player",
                                             StringComparison.OrdinalIgnoreCase))
        {
            resolved = "player";
            return player.Creature;
        }
        var living = GitsDebugLivingEnemies(combat);
        if (living.TryGetValue(key, out var byId))
        {
            resolved = key;
            return byId;
        }
        foreach (var (id, creature) in living)
        {
            if (string.Equals(SafeGetText(() => creature.Monster?.Title), key,
                              StringComparison.OrdinalIgnoreCase))
            {
                resolved = id;
                return creature;
            }
        }
        resolved = key;
        return null;
    }

    // ------------------------------------------------------------ apply ---

    private static Dictionary<string, object?> GitsDebugStateApply(
        string op, string who, string resourceId, int amount, string why)
    {
        if (!RunManager.Instance.IsInProgress)
            return Error("No run in progress; there is no player to write to.");

        if (IsMultiplayerRun())
            return Error("debug_state is refused in multiplayer: these writes "
                         + "do not go through the action-queue synchronizer, "
                         + "so peers would diverge.");

        if (!CombatManager.Instance.IsInProgress)
            return Error("No combat in progress. Every op here writes combat "
                         + "state, and out of combat the write would silently "
                         + "do nothing.");

        var runState = RunManager.Instance.DebugOnlyGetState();
        if (runState == null) return Error("No run state");

        var player = LocalContext.GetMe(runState);
        if (player == null) return Error("Could not find local player");

        var combat = CombatManager.Instance.DebugOnlyGetState();
        if (combat == null) return Error("No combat state");

        object? before;
        object? after;
        bool queued = false;
        string target = "player";

        switch (op)
        {
            case "set_resource":
            {
                if (string.IsNullOrWhiteSpace(resourceId))
                    return Error("set_resource needs a 'resource' id, e.g. "
                                 + "KLEEMOD_SPARK.");
                var combatState = player.PlayerCombatState;
                var (ok, was, now) =
                    GitsDebugSetResource(combatState, resourceId, amount);
                if (!ok)
                {
                    var known = GitsResourceSnapshot(combatState).Keys.ToList();
                    return Error(
                        $"No registered custom resource '{resourceId}'. "
                        + (known.Count == 0
                            ? "No custom resources are registered at all "
                              + "(BaseLib missing?)."
                            : "Registered: " + string.Join(", ", known) + "."));
                }
                target = resourceId;
                before = was;
                after = now;
                break;
            }

            case "set_energy":
            {
                var combatState = player.PlayerCombatState;
                if (combatState == null)
                    return Error("No player combat state; energy has no home.");
                before = combatState.Energy;
                // The game's own command, which is what a relic and an energy
                // potion both call. Clamped at zero only: MaxEnergy is a
                // display bound, not a cap the game enforces on the value.
                // Queued rather than awaited -- see the header.
                after = Math.Max(0, amount);
                queued = true;
                TaskHelper.RunSafely(
                    PlayerCmd.SetEnergy(Math.Max(0, amount), player));
                break;
            }

            case "set_hp":
            {
                var creature = GitsDebugResolve(who, player, combat, out target);
                if (creature == null)
                    return Error(GitsDebugUnknownCreature(who, combat));
                if (amount <= 0)
                    return Error(
                        "set_hp refuses 0 or less: SetCurrentHp leaves a "
                        + "creature at zero WITHOUT running the death path, "
                        + "which wedges the fight. Killing something is a "
                        + "play's job.");
                before = creature.CurrentHp;
                after = Math.Min(amount, creature.MaxHp);
                queued = true;
                TaskHelper.RunSafely(CreatureCmd.SetCurrentHp(
                    creature, Math.Min(amount, creature.MaxHp)));
                break;
            }

            case "set_block":
            {
                var creature = GitsDebugResolve(who, player, combat, out target);
                if (creature == null)
                    return Error(GitsDebugUnknownCreature(who, combat));
                var wanted = Math.Max(0, amount);
                before = creature.Block;
                // Hook-free on purpose (see the header): a setup verb has to
                // land the number it was given, and GainBlock would run the
                // ModifyBlockGained chain over it.
                creature.LoseBlockInternal(creature.Block);
                if (wanted > 0) creature.GainBlockInternal(wanted);
                after = creature.Block;
                break;
            }

            default:
                return Error($"Unknown op '{op}'. One of: "
                             + string.Join(", ", GitsDebugStateOps) + ".");
        }

        // EVERY WRITE IS LOGGED WITH ITS REASON, the same shape give_card logs
        // a grant. A board change with no stated reason is a change nobody can
        // account for when the log is read back.
        GD.Print($"[STS2 MCP][GItS] debug_state: {op} {target} "
                 + $"{before} -> {after}{(queued ? " (queued)" : "")} "
                 + $"| why: {why}");

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = $"{op} {target}: {before} -> {after}"
                          + (queued ? "; queued, read the next state to confirm"
                                    : ""),
            ["guardrail"] = GitsDebugStateGuardrail,
            ["op"] = op,
            ["who"] = target,
            ["before"] = before,
            ["after"] = after,
            ["queued"] = queued,
            ["why"] = why
        };
    }

    private static string GitsDebugUnknownCreature(string who, CombatState combat)
        => $"No living creature named '{who}'. Use \"player\", or one of the "
           + "entity ids the last GET reported: "
           + string.Join(", ", GitsDebugLivingEnemies(combat).Keys) + ".";

    private static Dictionary<string, object?> GitsDebugStateDescribe()
    {
        bool inRun, inCombat;
        try { inRun = RunManager.Instance.IsInProgress; }
        catch { inRun = false; }
        try { inCombat = CombatManager.Instance.IsInProgress; }
        catch { inCombat = false; }

        var resources = new List<string>();
        var creatures = new List<string> { "player" };
        try
        {
            if (inRun && inCombat)
            {
                var runState = RunManager.Instance.DebugOnlyGetState();
                var player = runState == null ? null : LocalContext.GetMe(runState);
                if (player != null)
                    resources = GitsResourceSnapshot(player.PlayerCombatState)
                        .Keys.ToList();
                var combat = CombatManager.Instance.DebugOnlyGetState();
                if (combat != null)
                    creatures.AddRange(GitsDebugLivingEnemies(combat).Keys);
            }
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] debug_state describe failed: {ex.Message}");
        }

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = "POST { op, amount, why, who?, resource? } to set up "
                          + "a board through the game's own mutators. Ops: "
                          + string.Join(", ", GitsDebugStateOps) + ".",
            ["guardrail"] = GitsDebugStateGuardrail,
            ["run_in_progress"] = inRun,
            ["combat_in_progress"] = inCombat,
            ["ops"] = GitsDebugStateOps.ToList(),
            ["resources"] = resources,
            ["creatures"] = creatures
        };
    }

    private static void HandleGitsDebugState(
        HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod == "GET")
            {
                var readTask = RunOnMainThread(GitsDebugStateDescribe);
                SendJson(response, readTask.GetAwaiter().GetResult());
                return;
            }

            if (request.HttpMethod != "POST")
            {
                SendError(response, 405, "Method not allowed");
                return;
            }

            string body;
            using (var reader = new StreamReader(request.InputStream,
                                                 request.ContentEncoding))
                body = reader.ReadToEnd();

            Dictionary<string, JsonElement>? parsed;
            try
            {
                parsed = JsonSerializer
                    .Deserialize<Dictionary<string, JsonElement>>(body);
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

            string? op = GitsDebugStr(parsed, "op");
            if (string.IsNullOrWhiteSpace(op))
            {
                SendError(response, 400, "Missing 'op'");
                return;
            }

            // REQUIRED, not defaulted. The one field this route will not
            // invent for you: `--why` is how a board change stays accountable
            // after the session that made it, and a blank default would make
            // "nobody said" indistinguishable from "nobody was asked".
            string? why = GitsDebugStr(parsed, "why");
            if (string.IsNullOrWhiteSpace(why))
            {
                SendError(response, 400,
                          "Missing 'why'. Every write here is logged with its "
                          + "reason; a board change nobody can account for "
                          + "later is worse than no scenario.");
                return;
            }

            int amount = 0;
            if (parsed.TryGetValue("amount", out var amountElem)
                && amountElem.ValueKind == JsonValueKind.Number
                && amountElem.TryGetInt32(out var parsedAmount))
                amount = parsedAmount;

            string who = GitsDebugStr(parsed, "who") ?? "player";
            string resource = GitsDebugStr(parsed, "resource") ?? "";

            var applyTask = RunOnMainThread(
                () => GitsDebugStateApply(op!.Trim(), who.Trim(),
                                          resource.Trim(), amount, why!.Trim()));
            SendJson(response, applyTask.GetAwaiter().GetResult());
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] debug_state endpoint failed: {ex}");
            try { SendError(response, 500, $"debug_state failed: {ex.Message}"); }
            catch { /* response may already be closed */ }
        }
    }

    private static string? GitsDebugStr(
        Dictionary<string, JsonElement> parsed, string key)
        => parsed.TryGetValue(key, out var elem)
           && elem.ValueKind == JsonValueKind.String
               ? elem.GetString()
               : null;
}
