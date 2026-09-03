# Atlas — vendor-sts2-mcp

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `vendor/STS2_MCP/` — **the wire contract only**. The C# screen/action
implementation (`McpMod.StateBuilder.cs`, `McpMod.Actions.cs`, …) is upstream's
and is read here only where it defines the wire. The Python client side is
`docs/current/atlas/understudy.md`.

## 1. Purpose

A pinned, vendored snapshot of [STS2MCP](https://github.com/Gennadiyev/STS2MCP)
(commit `55e0648`, MIT) — a Godot mod that serves the running game's state and
actions over an unauthenticated HTTP API on `localhost:15526`. This directory is
the **contract** `understudy/` codes against: read `state_type`, POST the verb
that `state_type` advertises. It is explicitly **not** ours to improve — it is
upstream's source held byte-identical to its pin, with marked local edit lines
across three upstream files and five files of our own under `gits/`
(`PROVENANCE.md`, "What we changed"). It is also **not a
simulator**: nothing here models the game, so anything the wire does not expose is
structurally invisible rather than approximated.

## 2. Entry points

Nothing here is imported by a Python session. Build/install go through the repo's
own script (never upstream's pruned `build.ps1`); gate and pin work from the repo
root; the wire itself needs the game running with the mod loaded.

```powershell
.\klee-mod\build\deploy_bridge.ps1            # lint pin, dotnet build, install to <GameDir>\mods\STS2_MCP
.\klee-mod\build\deploy_bridge.ps1 -Remove    # the one-command undo
```

```sh
python3 tools/lint_vendor_pin.py              # both-directions manifest check (CI + deploy_bridge)
python3 tools/lint_vendor_pin.py --write      # regenerate UPSTREAM_MANIFEST.tsv — read the diff
PYTHONPATH=. python3 -m pytest tier0/tests/test_vendor_pin.py -q

curl -s http://localhost:15526/                       # {"message": "Hello from STS2 MCP v0.4.0", "status": "ok"}
curl -s 'http://localhost:15526/api/v1/singleplayer?format=json'
curl -s -X POST http://localhost:15526/api/v1/singleplayer -d '{"action":"end_turn"}'
curl -s -X POST http://localhost:15526/api/v1/gits/speed -d '{"enabled":true,"time_scale":4.0}'
```

Route table (the whole surface): `/`, `/api/v1/singleplayer`,
`/api/v1/multiplayer`, `/api/v1/profiles`, `/api/v1/profile`,
`/api/v1/compendium`, `/api/v1/wiki`, and the five GItS forks
`/api/v1/gits/speed`, `/api/v1/gits/seed`, `/api/v1/gits/give_card`,
`/api/v1/gits/debug_state`, `/api/v1/gits/meter_ledger` (`EB-216`, GET only —
the per-play meter ledger) (`McpMod.HandleRequest`). Anything else is 404.

## 3. Key invariants

- **Singleplayer and multiplayer endpoints are mutually exclusive; mismatch is
  HTTP 409**, hard-blocked before dispatch so the non-sync-safe `end_turn` path
  cannot be reached during MP (`McpMod.cs:198-232`;
  `vendor/STS2_MCP/docs/raw-simplified.md:15`). The check is best-effort on the HTTP thread and
  swallows exceptions during run transitions (`McpMod.cs:288-296`).
- **All JSON is snake_case, UTF-8, null-omitting, relaxed-escaped**, set once in
  a single serializer options object used by every response
  (`McpMod.cs:29-35`, `McpMod.Helpers.cs:133-141`).
- **Every action POST body carries `"action"`; a missing one is 400, unparseable
  JSON is 400** (`McpMod.cs:441-456`, and the same shape for MP at `:340-355`).
- **`menu_select` bypasses the run-mode dispatcher on both endpoints**, so
  blocking FTUE/popup/game-over screens can be dismissed in SP and MP alike
  (`McpMod.cs:363-378` MP, `:461-476` SP).
- **All actions execute on the Godot main thread**, queued from the HTTP worker
  and drained at most 10 per frame (`McpMod.cs:127-158`). The HTTP thread blocks
  on the result, so a POST returns only after the frame that ran it.
- **Targets are `entity_id` strings** (e.g. `"JAW_WORM_0"`), synthesized by the
  bridge, not combat ids (`vendor/STS2_MCP/docs/raw-full.md:346`, `vendor/STS2_MCP/docs/raw-simplified.md:113`).
  Every other selector on the wire is an integer `index` into the array the same
  GET response just returned.
- **Whether a play owes a target is the CHOSEN MODE's answer, not the
  card type's** (`EB-184`, `McpMod.Actions.cs` `ExecutePlayCard` +
  `gits/GitsModalTargeting.cs`). `play_card` takes an OPTIONAL `mode`,
  matched against the card's own printed mode labels, read off the card
  by name (`KleeMod.Cards.IModalCard`) with no compile-time reference.
  A named mode that aims still refuses a missing target; a named mode
  that aims at nobody is played at an inert aim the game's own play path
  wants and the mode discards, and the response says so. A play naming
  no mode, or a card that is not modal, reaches upstream's card-type rule
  untouched -- the strict direction, and the same fallback
  `understudy.targeting` takes.
- **Only `localhost`/`127.0.0.1` are bound, with no authentication and
  `Access-Control-Allow-Origin: *`** (`McpMod.cs:94-97`, `:181-183`). Port is
  overridable via `STS2_MCP.conf` next to the DLL, default 15526
  (`McpMod.cs:23-79`).
- **Pin discipline is executable**: PROVENANCE must declare `upstream`/`pin`/
  `license`, the pin must match a git-sha regex, the license must be on the
  permissive list, `status: upstream` files must NOT contain `GItS LOCAL EDIT`
  and `gits-modified` files MUST, and everything under `gits/` must carry
  `GItS LOCAL ADDITION` and stay out of the manifest
  (`tools/lint_vendor_pin.py:15-34`, `:146-229`; `vendor/README.md:29-54`).
- **Every GItS fork SELECTS state the game's own generators can produce; none
  of them mints any.** `GitsSeed` chooses which run the generators make;
  `GitsResources` only serialises; `GitsDebugState` (EB-142/EB-146) writes five
  combat numbers, each through the mutator the game already uses for it and
  none of them a mutator the game lacks; `GitsGiveCard` (EB-52) resolves a card
  out of `ModelDb.AllCards` and hands it to `RunState.CreateCard` +
  `CardPileCmd.Add` — the two lines `CardReward.OnSelected` itself runs — or to
  `AddGeneratedCardToCombat` for a combat pile, so the combat-history row is
  written too. `give_card` is DEV-ONLY: it stamps a `guardrail` field on every
  success saying the run is no longer one the generators produced, refuses
  multiplayer (the pile add bypasses the action-queue synchronizer), and refuses
  a combat pile out of combat (the game's own path would no-op silently).
- **The GItS speed endpoint is off by default, gameplay-inert, and reversible**:
  originals are captured on first apply and restored on `{"enabled": false}`;
  `time_scale` is clamped to [0.1, 20] (`gits/GitsSpeed.cs:8-43`, `:190-223`).
  The captured `FastMode` original outlives the process in a
  `GitsSpeed.original.conf` sidecar in the mod directory — JSON content under a
  `.conf` name, because ModManager parses every `*.json` under `mods/` as a
  manifest — written on enable and deleted by a successful disable
  (EB-87, `:64-160`); `TimeScale` is not persisted because a new process starts
  at the default.

## 4. Rulings that shaped it

- **R70** (`tier0/DECISIONS.md:2209`) — "latest is not a version." The precedent
  that makes a git sha, not a release tag or a Nexus download, the only
  acceptable pin; `lint_vendor_pin.py:19-21` cites it by number.
- **R94** (`tier0/DECISIONS.md:3220`) — Phase 2 samples the LLM at turn-openings
  flagged hard by "cheap triggers computable straight off the wire." Constrains
  what future work may ask of this contract: triggers must be derivable from a
  single GET, not from state the wire does not carry.
- **R95** (`tier0/DECISIONS.md:3266`) — the seed fork. The bridge **cannot start
  a chosen-seed singleplayer run**; seeds are read back after the fact from
  `/api/v1/compendium`. Adding a Custom-screen arm to this fork is MANDATORY
  before any cross-build comparison is quoted.
- **R97/5a** (`tier0/DECISIONS.md:3343-3349`) — readiness is the `options` key in
  the menu state, **never** `GET /`. The HTTP server answers ~5s after launch;
  the menu has no buttons for another ~20.
- **R97/5d** (`tier0/DECISIONS.md:3360-3368`) — the five adapter defects are
  **facts about this wire**, kept as measurement history because any future
  adapter meets the same five.
- **P0 ruling 1**, RATIFIED 2026-08-04 (`docs/archive/understudy-p0-findings.md:224-248`)
  — ADOPT STS2MCP as a pinned vendored fork rather than depend on the release
  binary; writing our own bridge was costed and rejected as the more expensive
  path.
- **P0 ruling 3**, RATIFIED 2026-08-04 (`docs/archive/understudy-p0-findings.md:413-419`)
  — BUILD the speed affordance ourselves inside this fork (`gits/GitsSpeed.cs`),
  ADOPT nothing for speed.

## 5. Traps

- **Upstream `README.md` is stale and partly inapplicable in-tree.** It advertises
  `v0.3.4`, the `mcp/` Python server and `build.ps1` — all pruned
  (`PROVENANCE.md`, "What was pruned"). It is carried because the manifest hashes
  it, not because its instructions run here.
- **`mod_manifest.json:6` and `McpMod.cs:22` both say `0.4.0`. Neither is the
  version pin** — `PROVENANCE.md` is, and says so. Installing the 0.4.0 release
  binary instead of building this snapshot is the one way to reproduce the
  version-pin failure the kickoff brief worried about.
- **Two error shapes, and the docs only describe one.** Action results are
  `{"status": "ok"|"error", "message": …}` (`vendor/STS2_MCP/docs/raw-simplified.md:55`), but
  transport-level failures (400/404/405/409) are `{"error": …}` with **no
  `status` key** (`McpMod.Helpers.cs:152-156`), and GET failures add
  `exception_type` + `stack_trace` (`McpMod.cs:322-328`). `understudy/bridge.py`
  parses HTTP error bodies as JSON and returns them, so a 409 arrives as an
  ordinary dict, not an exception (`understudy/bridge.py:46-51`).
- **`format=markdown` falls back to JSON only on the singleplayer GET**
  (`McpMod.cs:401-411`); the multiplayer GET has no such guard
  (`McpMod.cs:307-310`).
- **`"enabled"` on the speed endpoint is `ValueKind == True`** — a JSON string
  `"true"` or a `1` reads as **false** and silently disables
  (`gits/GitsSpeed.cs:280`). `time_scale` is likewise ignored unless it parses as
  a double (`:282-286`).
- **`PrefsSave.FastMode` persists to `prefs.save`** — NOT `settings.save`, which
  backs `SettingsSave` and never carries FastMode
  (`PrefsSaveManager.fileName = "prefs.save"`, decompile read pinned to
  `klee-mod/KleeTests/bin/Debug/sts2.dll`). Enabling speed and not
  disabling it leaves user-visible state changed; teardown must POST
  `{"enabled": false}` (`gits/GitsSpeed.cs:16-20`). It is also why the capture is
  persisted across processes rather than re-read (`:21-34`) — **on the narrow
  path that actually reaches disk**: prefs are flushed only by `NGame.Quit()`
  (via `_Notification(1006)`, a window close request) and
  `NSettingsScreen.OnSubmenuClosed`, and `NGame` demotes a persisted `Instant`
  to `Fast` on every non-editor boot, so a restarted process can never read
  `Instant` back. What it CAN read back is a laundered `Fast` over a user whose
  original was `Normal`, and the sidecar is what prevents that.
  `understudy/soak_session.py`'s `_read_speed_sidecar` reads it before
  removing the mod directory (`EB-180` moved it out of `soak.py`), so an unreverted change is named in the ledger rather than
  deleted with the file that recorded it.
- **Seeded embark returns an error and does NOT start the run** unless
  `charSelect.Lobby != null` (`McpMod.Actions.cs:1621-1627`) — the mechanism
  behind R95.
- **`state_type: "overlay"` and a menu with no `options` are the two shapes a
  soft-lock takes; neither raises** (`vendor/STS2_MCP/docs/raw-simplified.md:49`,
  `understudy/bridge.py:13-16`).
- **The five wire facts** (R97/5d, `docs/archive/understudy-phase0-report.md:97-104`):
  enemies live under `battle.enemies` not top level; intent damage exists only in
  `label` ("7", "6 x 3") with no numeric field; the hand's field is `target_type`
  not `target`; auras read `"Cryo Aura"` not `"cryo"`; and the intent label
  **already includes the attacker's Strength**.
- **Frozen files.** Every file listed `upstream` in `UPSTREAM_MANIFEST.tsv` must
  stay byte-identical — editing one fails the lint in CI, in
  `tier0/tests/test_vendor_pin.py`, and in `deploy_bridge.ps1:71-75` before it
  builds. A deliberate change means marking it `GItS LOCAL EDIT`, recording it in
  `PROVENANCE.md`, and regenerating the manifest — which is itself generated, so
  hand-editing it defeats the gate (`UPSTREAM_MANIFEST.tsv:1`). The lint has
  **no** opinion on whether the pin is the *right* commit or whether the built
  DLL matches the source (`tools/lint_vendor_pin.py:264-268`).

## 6. Reading order

1. `vendor/STS2_MCP/docs/raw-simplified.md` — the whole contract in 213 lines:
   endpoints, `state_type` table, verb-per-screen.
2. `vendor/STS2_MCP/PROVENANCE.md` — the pin, the environment it was verified
   against (v0.111.0 since EB-171), what was pruned, the marked local edits
   across three upstream files, how to refresh.
3. `vendor/STS2_MCP/McpMod.cs:175-296` — `HandleRequest`: the actual route chain,
   the 409 guard, and the marked local edit.
4. `vendor/STS2_MCP/gits/` — the GItS-authored code; each file's header is its
   contract (`GitsSpeed.cs:1-46`, `GitsSeed.cs:1-93`, `GitsResources.cs:1-46`,
   `GitsGiveCard.cs:1-88`, `GitsDebugState.cs:1-160`).
5. `vendor/README.md` + `tools/lint_vendor_pin.py:1-35` — the vendoring rules and
   their executable half.
6. `vendor/STS2_MCP/docs/raw-full.md` — object-by-object schema, when a field's
   exact name or shape matters.
