# S20 — player-count surface census (1 / 2 / 3-player)

> **This decides nothing.** It is an inventory of what the repo can prove today
> about solo versus co-op seats. It is not a promise that co-op is supported, not
> a support level, not a scope commitment, and not a plan. Every row is either a
> **defect** (something is wrong and could be fixed without a taste call) or a
> **[USER] scope call** (something is absent or one-sided and only [USER] can say
> whether that matters). Those two are kept strictly apart.

Read on 2026-08-26 against the primary checkout at HEAD `223a4ff`
(`review/dispatch3/PREFLIGHT.md`). Downfall comparisons are pinned to
`lamali292/Downfall@32e6113`, read from the local depth-1 clone, reference-only.

## What this does NOT establish

No test was run for this file. Nothing here was verified by playing the game,
launching it, or building the C# project — [USER] is playtesting on `0.2-1155`
and the charter forbids touching the installation. Test counts and coverage
claims below are read from source and from the suite's own record; where a claim
needed a live two-seat table to check, it is marked UNKNOWN rather than assumed.
No number here is a measurement, and no row grades whether co-op is good.

---

## 0. A skew in the family name, stated first

This family was dispatched as "1 / 2 / 3-player". The base game's own lobby
reports **`max_players: 4`** (`vendor/STS2_MCP/McpMod.StateBuilder.cs:783` reads
`lobby.MaxPlayers`; the wire example shows `"max_players": 4` at
`vendor/STS2_MCP/docs/raw-full.md:288`). Repo prose reasons about 4-seat tables
too — e.g. `docs/current/dossiers/enemies/crusher.md:103` prices Crusher "~1004
at 4 players".

Nothing in `klee-mod/` or `tier0/` caps, asserts, or branches on a seat count of
any size: the mod enumerates `state.Players` and `run.Players` without a bound
(`klee-mod/KleeCode/Vfx/GaugeBridge.cs:420`,
`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:201-205`). So "1/2/3" is the
dispatch's framing, not the game's or ours. **Whether the ceiling we care about
is 2, 3, or 4 is a [USER] scope call**, and it changes nothing below except how
many rows a reader should imagine.

---

## 1. Joined case matrix

Status vocabulary: **WORKS** = evidenced in repo as implemented *and* checked by
something; **DEFECT** = evidenced wrong or evidenced as a known hole with a
repair direction; **UNKNOWN** = the repo does not answer it; **NOT-SUPPORTED-BY-
DESIGN** = a ruling or a structural fact says it will not exist.

"Not reproducible tonight — needs the game" is used literally where it applies.

| # | Case | Reproduction | Status | Evidence (`file:line`) | Automation candidate (+ seam) | Defect or [USER] scope call |
|---|---|---|---|---|---|---|
| 1 | The run **simulator models exactly one seat**; no sim run can agree or disagree with the mod about a two-seat board | `PYTHONPATH=. python -m pytest tier0/tests/test_coop_ownership.py -q` — it passes by asserting a *structural* filter, and its own docstring states the gap | NOT-SUPPORTED-BY-DESIGN (stated, not accidental) | `tier0/tests/test_coop_ownership.py:9-15`; `tier0/harness/metrics.py:104-106` ("tier0 models ONE seat, so there is no per-seat axis here; a seat dimension is a co-op instrument and is not invented by a one-seat sim"); `tier0/content/loader.py:363`; `tier0/engine/effects.py:2685` | No — a second seat in tier0 is a rewrite, not a test | **[USER] scope call.** Building a two-seat sim is a large one-way spend; the repo currently treats it as out of scope and says so in four places |
| 2 | Per-seat **ownership and attribution** in C# (independent Fanfare meters, per-seat Fanfare ceiling, identity gating on a mixed table, per-seat relic ownership, per-seat salon tick, per-Creature salon company, per-seat telemetry keys, two placers → two bomb piles) | `cd klee-mod/KleeTests && dotnet test --filter CoopSeamTests` (needs `GameDir` + `BaseLibDll` in `klee-mod/local.props`) | WORKS | `klee-mod/KleeTests/CoopSeamTests.cs` — 8 `[Fact]`s (lines 32, 44, 59, 76, 93, 105, 120, 143); coverage list at `klee-mod/KleeTests/README.md:118-136` | Already automated. Not a deploy gate: `deploy.ps1` does not run it and `validate.ps1` only does with `-RunCsharpTests` (`klee-mod/KleeTests/README.md:41-52`) | **[USER] scope call** whether to promote it to a gate — the README says so explicitly and ties it to the CI question |
| 3 | Multiplayer **transport**: lockstep RNG agreement, remote-seat selection round trips, desync, disconnect | Not reproducible tonight — needs two peers and the game | UNKNOWN (play-only) | `klee-mod/KleeTests/README.md:89` ("A second peer \| no transport, no lockstep"), `:138-146`; `klee-mod/KleeTests/CoopSeamTests.cs:24-28` | Partial — see row 10; the STS2MCP `/api/v1/multiplayer` endpoint exists and is unused by us | Neither yet: it is an untested surface, not a known defect |
| 4 | Anything needing a **live `CombatState`** in a two-seat fight: off-seat burst attribution, corpse detonations, co-op ownership of a card actually being played, Salon `Deploy`/`Bow`, **two seats detonating on one enemy** | Not reproducible tonight — needs the game | UNKNOWN (play-only) | `klee-mod/KleeTests/README.md:88` (boundary row), `:140-146`; `klee-mod/KleeCode/Powers/BombPower.cs:672-674` | Yes — the README names the next leg itself: a live-`CombatState` harness (`klee-mod/KleeTests/README.md:12-15`) | **[USER] scope call** (build the harness or not) |
| 5 | A **damage preview mutating per-peer state desyncs the table** — the 2026-07-27 incident: `PreventExhaustWardPower` set a latch inside `ModifyDamageAdditive`, one peer burned a roll off `Rng.CombatTargets` the other did not, host tripped `StateDivergence`, client disconnected | `PYTHONPATH=. python -m pytest tier0/tests/test_reaction_phase_parity.py -k modifiers_are_pure -q` — a repo-wide unkeyed sweep of every damage-modifier override | WORKS (defect found by play, now fenced) | `tier0/tests/test_reaction_phase_parity.py:538-552` (receipt, incl. `godot.log` checksums 576 / 49) and `:474-480`; downstream comments citing it: `klee-mod/KleeCode/Powers/SpotlightSystem.cs:508-511`, `Powers/TurnEndAttribution.cs:47-51`, `Powers/KuragePowers.cs:497` | Already automated (structural sweep, not per-power) | Was a defect; **closed**. Listed because it is the shape every future co-op defect will take |
| 6 | **Shared RNG streams**: any draw one seat makes and the other does not poisons every later draw | Static read; the fallback path is exercised headlessly | WORKS | `klee-mod/KleeCode/Powers/SalonPowers.cs:352-359` (drawn inside the loop from `owner.Player?.RunState.Rng.CombatTargets`, fixed fallback when there is no player), `:326-328`; `klee-mod/KleeCode/KleeStartingCompanions.cs:111-113` (companion roll burns its own `Rng` off seed+slot so "peers and replays agree and no native stream is consumed") | Partial — no test asserts stream choice; a lint over `new Random(` / non-shared streams in play paths is a candidate seam | Neither — currently correct by construction |
| 7 | **Featured Banner is per-player in co-op** (LAW: "per-player in co-op") — implemented keyed on `player.PlayerRng.Seed`, cached by seed | Not reproducible tonight — needs two seats with distinct `PlayerRng` seeds | UNKNOWN (asserted in prose, never checked) | Claim: `klee-mod/KleeCode/CompanionBanner.cs:35-38`; implementation `:63-71`; LAW requirement `docs/current/LAW.md:147-149` | Yes, but blocked: `CoopSeamTests` cannot reach it. The `Seat` harness seeds only `Character`, `_relics`, `PlayerCombatState`, and a test needing a further `Player` field "has left the boundary" (`klee-mod/KleeTests/Harness/Seat.cs:24-29`; `klee-mod/KleeTests/README.md:85`). Seam = extend `Seat` to seed `PlayerRng`, or the live-`CombatState` harness | Neither yet — an **evidence gap**, not a proven defect |
| 8 | **Reaction counts in telemetry are team-wide, not per seat** — in co-op both seats' reactions land in every seat's row | Read a two-seat human-feed row and divide `reactions_by_turn`; not reproducible tonight | DEFECT (known, documented, deliberately not fixed) | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:259-263` ("`TotalResolved` is GLOBAL rather than per-player… a reader who does not know that would divide by the wrong denominator"); repeated in the schema at `understudy/README.md:711` | Yes — the sibling counter shows the fix shape: `_corpseDetonationsByPlayer` is a `Dictionary<Player,int>` and is pinned as such (`tier0/tests/test_eb18_fight_stream.py:328-335`) | **Defect** (analysis hazard, measurement-only surface). Whether it is worth fixing is a small scope call; the hazard itself is not in dispute |
| 9 | **Selection telemetry is local-seat only** — a remote seat's answer arrives as indices through `PlayerChoiceSynchronizer` and never opens a screen in this process, so a partner's row is *absent*, not empty | Static read; declared limit | NOT-SUPPORTED-BY-DESIGN (declared) | `klee-mod/KleeCode/Diagnostics/SelectionTelemetry.cs:99-102`; `understudy/README.md:518-520` | No — the data does not exist in this process | Neither. A **[USER] scope call** only if co-op selection data is ever wanted |
| 10 | The **understudy bot bridge drives singleplayer only** | `grep -n singleplayer understudy/bridge.py` → one endpoint constant, no multiplayer one | NOT-SUPPORTED-BY-DESIGN today | `understudy/bridge.py:27` (`SINGLEPLAYER = f"{BASE}/api/v1/singleplayer"` is the only run endpoint defined); embark path is `main -> singleplayer -> standard -> character -> confirm` (`understudy/soak.py:1509-1517`); BACKLOG states the gate: "a two-seat runtime; the bridge drives singleplayer only" (`docs/current/BACKLOG.md:78`) | **Yes, and the seam already exists upstream.** STS2MCP serves `GET/POST /api/v1/multiplayer` with lobby host/join and a vote-based `end_turn` (`vendor/STS2_MCP/McpMod.cs:216-231`, `:347-378`; wire docs `vendor/STS2_MCP/docs/raw-simplified.md:7-8`, `:206-213`, `:61` for the `multiplayer_join` / `multiplayer_load_lobby` menu flow). It is unused by `understudy/` | **[USER] scope call.** Driving it needs *two* game instances or two machines, and the server binds localhost only with no auth (`docs/current/atlas/vendor-sts2-mcp.md:73-75`) — a real cost, not a small wiring job |
| 11 | The three **GItS debug forks refuse multiplayer**, so no board-setup scenario can run on a co-op table | `curl -X POST .../api/v1/gits/debug_state` during an MP run → error | WORKS (deliberate refusal) | `vendor/STS2_MCP/gits/GitsDebugState.cs:488-489`, `gits/GitsGiveCard.cs:285-286`; reasoning `understudy/bridge.py:196-200`; SP/MP mutual exclusion is a 409 before dispatch (`vendor/STS2_MCP/McpMod.cs:198-231`) | No — refusing is the correct behavior; automating around it would be the defect | Neither. It is the **consequence** of row 10, and it means the scenario harness (`understudy/scenario.py`) can never cover co-op as built |
| 12 | `EB-53` **end-of-turn attribution docket is per seat**, and the visual bridge sets it up for **every** seat, not only the local one | Static read; the co-op capture is explicitly owed | WORKS (code) / owed (capture) | `klee-mod/KleeCode/Vfx/GaugeBridge.cs:420-427` (loops `state.Players`, comment: "EVERY seat, not only the local one"); `klee-mod/KleeCode/Vfx/TurnEndPreviewBridge.cs:68`, `:89`; owed item: `docs/current/BACKLOG.md:78` "**Next action:** capture `C6`'s co-op half" | Yes for the code path; **no** for the capture — it needs a two-seat runtime | **[USER] scope call** (it is already an open BACKLOG row with a stated gate; this census adds nothing to it) |
| 13 | **Relic ids are frozen because renaming one is a co-op desync** — the Orobas upgrade displays as "Dodoco Tales" while the C# type stays `ExplosiveFrags` | Static read | WORKS | `docs/current/atlas/klee-mod-runtime.md:136-140` (R69); `klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:99-118,148` | Yes — an id-stability lint is a candidate seam, and overlaps the save/update/removal family (one-line pointer only) | Neither — a standing constraint, already honored |
| 14 | **Build/handoff hygiene is co-op-shaped**: the mod zips for co-op handoff, deploy refuses to overwrite an existing handoff zip, and a dirty tree is marked "DO NOT hand this build to a co-op partner" | `PYTHONPATH=. python -m pytest tier0/tests/test_manifest_version_gate.py -q` (Windows-only; drives PowerShell) | WORKS | `docs/current/atlas/klee-mod-build-pck.md:11-14`; `tier0/tests/test_manifest_version_gate.py:227-239` and `:243-250`; the defect being pinned (one manifest version for four sprints, silent zip overwrite, "exactly the failure the version field exists to prevent" in lockstep co-op) at `:16-22` | Already automated | Was a defect; **closed**. Overlaps packaging/metadata family — pointer only |
| 15 | **No card in our three pools is multiplayer-only.** The base game has a `CardMultiplayerConstraint` with `MultiplayerOnly` *and* `SingleplayerOnly` faces; our sheets have no such field and our codegen never emits one | `grep -rn MultiplayerConstraint klee-mod/KleeCode` → no hits; `grep -rn multiplayer docs/*-cards.yaml` → no hits | NOT-SUPPORTED-BY-DESIGN today | We only ever *read* the flag, never set it: `tools/extract_base_game_pool.py:120`, `:1654-1668`; base-game examples Flanking/Sneaky (`tier0/tests/test_real_silent.py:19-23`) and Tank/DemonicShield (`tier0/tests/test_refpowers.py:799-802`); the inverse `SingleplayerOnly` (Well Laid Plans) is deliberately not filtered (`tools/extract_base_game_pool.py:1662-1664`) | Yes — a sheet field + one codegen line + a lint. Small, and gated on the call below | **[USER] scope call, and the largest one in this file.** `docs/current/LAW.md:272-275` (R144) says "Co-op mechanics arrive as multiplayer-only CARDS, never as modifications to a character's base kit… co-op depth is added by a few multiplayer-only cards". **Zero such cards exist.** LAW describes the route; nothing has walked it. See §2 |
| 16 | Enemy **HP and move-block scale by player count**; our sim never sees that scaling, so no sim number is a co-op number | Static read of the dossiers | UNKNOWN in sim / documented in dossiers | e.g. `docs/current/dossiers/enemies/axebot.md:88-89`, `bowlbug-egg-.md:43`, `cubex-construct.md:81-82` (Artifact granted as `1 + (players − 1)`), `crusher.md:103-104` | No — this follows from row 1 | Neither. It is the **reason** row 1 matters for balance: every ratified winrate band is a solo number |
| 17 | `SKIP-10.9` lists **per-dealer reaction windows as a ruled co-op divergence (R1)** among un-modelled mechanics | n/a | DORMANT / NO-SPEND | `docs/current/BACKLOG.md:72` | **No — prohibited target (charter §3.2).** Named here only so a reader does not think it was missed | Neither; it is dormant by ruling |

---

## 2. The one asymmetry worth [USER]'s eye

Rows 15 and 1 together are the whole shape of this census:

- LAW promises co-op depth **as multiplayer-only cards** (`docs/current/LAW.md:272-275`, R144), and LAW also promises **"Every character clears solo; co-op is amplified, never required"** (`:271`).
- The solo half is honored and measured. The co-op half has **no cards, no sheet field, no codegen path, and no sim**.
- The base game supports the mechanism, and a released mod uses it: at
  `Downfall@32e6113`, **seven characters each ship exactly five multiplayer-only
  cards** in a dedicated `Cards/Multiplayer/` folder — 35 files, each overriding
  `MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly`. Examples:
  `Downfall@32e6113:AutomatonCode/Cards/Multiplayer/Bluescreen.cs:21`,
  `ChampCode/Cards/Multiplayer/Huddle.cs:17`,
  `GuardianCode/Cards/Multiplayer/SharedFlux.cs`,
  `HexaghostCode/Cards/Multiplayer/CircleFlame.cs`,
  `SneckoCode/Cards/Multiplayer/Sssharing.cs`.
  (Folder listing verified in the pinned clone; the constraint override verified
  by line in the files quoted.)

This file does **not** recommend adding them, does not propose a count, and does
not price it. It records that LAW describes a route nothing has taken, and that
the mechanism to take it is proven to exist in a shipped mod.

**Numbered pick list for [USER] — answer shapes only, no recommendation:**

1. Does the public target include co-op at all? *(yes / no / later)*
2. If yes, what seat ceiling do we design against? *(2 / 3 / 4 / "whatever the base game does")*
3. Does R144's multiplayer-only-card route stay LAW as written, or does it become "co-op is base-kit-identical and we ship no co-op cards"? *(pick one)*
4. Should `KleeTests` become a deploy or CI gate, given it already carries the only co-op coverage that exists? *(yes / no / CI only)* — this is the same question `klee-mod/KleeTests/README.md:41-52` already raises.
5. Is a live-`CombatState` C# harness worth building, which would move rows 4 and 7 from UNKNOWN to testable? *(yes / no / not now)*
6. Is a two-instance / two-machine co-op understudy arm worth building on the already-existing `/api/v1/multiplayer` endpoint? *(yes / no / not now)*

---

## 3. Defects (distinct from the scope calls above)

Only one row on this census is a live defect, and it is a measurement-hygiene
one, not a gameplay one:

| Defect | Where | Why it is a defect and not a taste call | Repair shape (PROPOSED, technical) |
|---|---|---|---|
| Reaction counters in the fight row are team-wide, so a co-op seat's `reactions_by_turn` silently includes the partner's reactions | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:259-263`; schema `understudy/README.md:711` | The field sits beside per-seat fields (`seats`, `seat_index`, `character`) in a row that is written **one per seat** (`PlayTelemetry.cs:201-217`), so the row's own shape implies per-seat and the value is not | Key it the way the corpse counter next to it is already keyed — `Dictionary<Player,int>`, cleared with the total — the pattern pinned at `tier0/tests/test_eb18_fight_stream.py:328-335`. **PROPOSED only; not implemented, not scheduled.** |

Everything else in §1 is either working, dormant by ruling, an evidence gap, or
a scope call.

## 4. UNKNOWN — the repo does not answer these

1. Whether `Player.PlayerRng.Seed` is genuinely distinct per seat in a live co-op run. The banner's per-player claim rests on it (`klee-mod/KleeCode/CompanionBanner.cs:35-38`) and nothing checks it. Not reproducible tonight — needs the game.
2. Whether two seats detonating bombs on one enemy behaves (the placing half is pinned, the damage half is not) — `klee-mod/KleeTests/README.md:140-146`.
3. Whether all peers must have the identical mod build for a co-op run to start at all, and what the failure mode is if they do not. The repo's handoff rules (row 14) *assume* they must, but no cited source in HEAD states the game's behavior on a mod mismatch.
4. Whether two game instances can run on one machine (needed for any local co-op automation), and whether STS2MCP's fixed localhost port 15526 can be moved per instance — the port is overridable via `STS2_MCP.conf` next to the DLL (`docs/current/atlas/vendor-sts2-mcp.md:74-76`), but two installs sharing one machine is untested.
5. Every visual/UI surface at 2+ seats. `klee-mod/KleeTests/README.md:87` puts all Godot objects outside the boundary, so nothing visual is testable at any seat count.

## 5. NON-FINDINGS

- **No seat-count-conditional gameplay branch was found in `klee-mod/KleeCode/`.** Searching for `MultiplayerConstraint`, seat counts, and player-count reads returned per-seat *keying* (dictionaries keyed by `Player` / `Creature`) and unbounded `Players` enumerations, but no code that behaves differently at 1 vs 2 vs 3 seats. If a co-op-conditional behavior exists, it is not expressed as a player-count read.
- **No co-op-specific QUEUE row exists.** `docs/current/QUEUE.md` mentions seats once, at `M26`, and only as the eyes-on question about the per-seat *position* of the end-of-turn docket. There is no open [USER] decision about co-op scope anywhere in the register today — which is itself why §2 is written as a pick list.
- **No localization or accessibility surface was found that varies by seat count.** Those belong to the sibling families; this census found nothing to hand them beyond one-line pointers.

## 6. Pointers to sibling families (not my rows)

- Relic/card **id stability** as a save-and-update concern → save/update/removal family (row 13 here).
- **Handoff zip / manifest version** discipline → packaging/metadata/credits family (row 14 here).
- The `M26` **eyes-on** for the per-seat docket → world/art families; it is an existing QUEUE row and stays there.
