# STS2_MCP — provenance

upstream: https://github.com/Gennadiyev/STS2MCP
pin: 55e0648
pin-subject: Fix game API compatibility with STS2 v0.107 (#123)
pin-date: 2026-07-29
license: MIT
license-holder: Yikun Ji (Kunologist)
vendored: 2026-08-04
vendored-by: Understudy sprint, work item W1
ruling: docs/archive/understudy-p0-findings.md ruling 1, RATIFIED by [USER] 2026-08-04

## Why this pin and not a release

The latest tagged release is **0.4.0, dated 2026-05-05**, and it predates our
game build. The pin above is the commit that carries the v0.107 compatibility
fix, and v0.107.1 is exactly what we ship against. Installing the release
binary instead of building this snapshot is the one way to reproduce the
version-pin failure the kickoff brief worried about — P0 stop-and-surface
item 2 says so, and this paragraph is where a hurried session is meant to
read it.

The in-tree `mod_manifest.json` still says `"version": "0.4.0"` and
`McpMod.Version` still says `0.4.0`; upstream did not bump either on this
commit. Neither string is a version pin. **This file is the pin.**

## Environment it was verified against

| Thing | Value |
|---|---|
| Game | v0.107.1, commit 59260271, dated 2026-06-18 |
| main_assembly_hash | -1555940892 |
| Toolchain | .NET SDK 9.0.316, `net9.0` |
| Build | `dotnet build -c Release` against `data_sts2_windows_x86_64` — 0 warnings, 0 errors |

## What was pruned from the snapshot

Carried: the C# mod (11 `McpMod.*.cs` files), `STS2_MCP.csproj`,
`mod_manifest.json`, `LICENSE`, `README.md`, and `docs/raw-simplified.md` +
`docs/raw-full.md` — the wire protocol, which is the contract `understudy/`
codes against and the thing a future session will actually need to read.

Dropped, and why:

- `mcp/` (the optional Python MCP server, `server.py` + `pyproject.toml` +
  `uv.lock`). We speak the HTTP API directly from `understudy/`; an MCP
  wrapper is a second client we would have to keep working for no gain.
- `build.ps1`. Superseded by `klee-mod/build/deploy_bridge.ps1`, which reads
  `GameDir` from our `local.props` like every other build path in this repo
  instead of an `STS2_GAME_DIR` environment variable, and which owns the
  install and uninstall steps upstream leaves to the reader.
- `STS2_MCP.sln`, `.github/`, `.claude/`, `AGENTS.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `.gitignore`, `docs/teaser.png` — upstream project
  furniture, not code we build or run.

Pruning is recorded rather than hidden: `UPSTREAM_MANIFEST.tsv` lists exactly
what we carry, and `tools/lint_vendor_pin.py` fails if the tree and the list
disagree in either direction.

## What we changed

**Four lines across two upstream files, plus EB-92's two guards in a third.** Everything of substance lives in
`gits/`, which the pin lint excludes from the upstream hash list entirely.

| File | Status | Change |
|---|---|---|
| `McpMod.cs` | `gits-modified` | Three `else if` arms on the `HandleRequest` route chain — `/api/v1/gits/speed` (W2), `/api/v1/gits/seed` (P1.5) and `/api/v1/gits/give_card` (EB-52) — marked in-file with `GItS LOCAL EDIT`. Nothing else in the file is touched. |
| `McpMod.Wiki.cs` | `gits-modified` | EB-92 (2026-08-13) — two guards in the result formatter, marked in-file with `GItS LOCAL EDIT`. Every mod-card query answered `500 ... Canonical model of type <generated class> used in incorrect place`, a different class each time: the formatter walks `ModelDb.AllCards` (where mod cards live) and reads properties off the CANONICAL instance, and one throwing card took the whole search down — including the base-game rows that had formatted fine. `BuildWikiResultSafely` degrades a throwing candidate to one row carrying id/name/score/`error`, and the hover-tip read degrades to empty. Neither guard fixes the throwing card, and the degraded row names it. Upstreamable as-is: any mod's custom model can do this. |
| `McpMod.StateBuilder.cs` | `gits-modified` | One line in `BuildPlayerState`, inside the live-combat block: `state["resources"] = GitsResourceSnapshot(combatState)`. Marked in-file with `GItS LOCAL EDIT`. P1.5 spec item 2. |
| `gits/GitsSpeed.cs` | GItS addition | Work item W2 — the speed affordance. EB-87 (2026-08-12): the captured original `FastMode` is persisted to `GitsSpeed.original.conf` in the mod directory (next to the `STS2_MCP.conf` this file's neighbours already write — JSON content under a `.conf` name, because ModManager parses every `*.json` under `mods/` as a manifest), a later process restores from that sidecar instead of re-capturing, and a successful disable deletes it. `PrefsSave.FastMode` persists to `prefs.save` (not `settings.save` — corrected 2026-08-13 by the round-2 correctness audit, along with the mechanism: prefs are flushed only by `NGame.Quit()` or `NSettingsScreen.OnSubmenuClosed`, neither reachable from a `TerminateProcess` kill, and `NGame` demotes a persisted `Instant` to `Fast` on every non-editor boot, so no second process can read `Instant` back. The reproducible laundering is one step narrower: after a flush, a second process captures the demoted `Fast` and "restores" a `Normal` user to `Fast`. The sidecar is the right fix for that; only its stated justification was wrong). `TimeScale` is deliberately not persisted — `Engine.TimeScale` starts at its default in every process, so the live capture is already the right original. |
| `gits/GitsSeed.cs` | GItS addition | P1.5 item 1 — the chosen-seed endpoint. Documents in-file why upstream's own `charSelect.Lobby == null` refusal does not describe the game. |
| `gits/GitsResources.cs` | GItS addition | P1.5 item 2 — a reflection-only reader for BaseLib's custom-resource registry. No compile-time BaseLib reference; a missing BaseLib yields an empty map. |
| `gits/GitsGiveCard.cs` | GItS addition | EB-52 — the dev-only card-injection route. Selects a card out of `ModelDb.AllCards` and hands it to the game's own acquisition path; mints nothing. **EB-91 (2026-08-13): the CARD SCOPE now follows the pile.** Deck grants are created in `player.RunState`; combat-pile grants in `player.Creature.CombatState`, which is what every in-combat generator does (`CollisionCourse`, `CardFactory.GetForCombat`). A run-scoped card handed to `AddGeneratedCardToCombat` arrived in hand and read back fine, then threw `must be added to a CombatState before playing it` out of `CardPileCmd.AddDuringManualCardPlay` and wedged the fight. The `route` field, which reported the static string `card_pile_cmd` for both branches, now names the branch that ran (`run_state_create+card_pile_add` / `combat_state_create+add_generated_to_combat`) and a `scope` field says `run`/`combat`. |

Everything else is byte-identical to `55e0648`.

The route arms are edits rather than Harmony patches because upstream's
routing is a plain if/else chain in one method: patching it would mean
rewriting the same chain from outside, in more code, less legibly, to protect
a purity we can simply record instead. The `BuildPlayerState` line is an edit
for the same reason and one more: a resources map attached out-of-band by a
patch would not be ATOMIC with the state read it belongs to, and a meter read
a frame after the hand it describes is a different measurement.

## The additions, and what they do NOT change

**No addition changes a rule.** Each one SELECTS state the game's own
generators can produce, or reports state the game already holds:

- `GitsSeed` selects which run the game's own generators produce, through the
  game's own `StartRunLobby.SetSeed` / `NGame.DebugSeedOverride`.
- `GitsResources` is a serialiser that never writes an `Amount`.
- `GitsGiveCard` selects a card that is already in `ModelDb.AllCards` — the
  same registry `McpMod.Wiki.cs` enumerates — and hands it to the game's own
  acquisition machinery: `RunState.CreateCard(canonical, player)` then
  `CardPileCmd.Add(card, PileType.Deck)`, which is exactly what
  `CardReward.OnSelected` and `CardPileCmd.AddCursesToDeck` run. It never
  constructs a card object of its own, and in-combat grants take the
  combat scope's `CreateCard` then `AddGeneratedCardToCombat`, which is the
  pair every in-combat generator in the game runs and which writes the
  combat-history row too.

No constant, generator, reward table or pilot is touched by any of them.

**`GitsGiveCard` is dev-only in a way the wire says out loud.** A run that
used it is no longer a run the generators produced, so nothing measured on it
is comparable to anything; every successful grant carries a `guardrail` field
saying so, and `understudy/bridge.py` stamps the same sentence on the harness
log. It refuses multiplayer outright (the pile add does not go through the
action-queue synchronizer, so peers would diverge) and refuses a combat pile
when no combat is in progress (the game's own path would return an empty list,
i.e. a silent no-op wearing an `ok`).

## Refreshing the pin

1. `git clone https://github.com/Gennadiyev/STS2MCP && git checkout <new sha>`
2. Copy the carried files over this directory (the list is
   `UPSTREAM_MANIFEST.tsv`, `status == upstream`).
3. Re-apply the `McpMod.cs` route arms above — there are **three** of them now
   (speed, seed, give_card), all inside one marked block. A refresh that
   re-applies two of three leaves a handler in `gits/` that nothing routes to,
   and the pin lint cannot see that: it checks hashes and markers, not whether
   a route exists. Grep the refreshed `McpMod.cs` for `gits/` and count.
4. Update `pin`, `pin-subject`, `pin-date` and the environment table here.
5. `python tools/lint_vendor_pin.py --write`, and **read the diff** — if it
   touches more than you meant, that is the finding.
6. Rebuild and re-verify against the game version in the table.

**What a refresh may break in `gits/`, which the lint also cannot see.** These
files name game APIs by hand, and upstream STS2MCP is not what would move them
— the GAME is. `GitsGiveCard` binds `ModelDb.AllCards`, `ICardScope.CreateCard`
on both `RunState` and `Creature.CombatState`, `CardPileCmd.Add` /
`AddGeneratedCardToCombat`, `CardCmd.Upgrade` and `LocalContext.GetMe`
(note `ICombatState` declares `CreateCard` itself and does not derive from
`ICardScope`, so the combat scope is reached with `as` — a game-side merge of
those two interfaces would silently turn the grant into the refusal branch); `GitsSeed` binds `StartRunLobby.SetSeed`,
`NGame.DebugSeedOverride` and `SeedHelper.CanonicalizeSeed`. A game-version
bump is the event that invalidates those, and the check is the build: it fails
loudly, which is the good case.

Upstreaming the speed endpoint stays open; MIT does not require it and this
sprint did not spend time on it.
