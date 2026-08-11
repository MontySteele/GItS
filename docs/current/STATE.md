# STATE

> **What currently ships** — roster, systems, versions, and active workstreams.
> Snapshot only. Open decisions live in [`docs/current/QUEUE.md`](QUEUE.md);
> engineering tasks in [`docs/current/BACKLOG.md`](BACKLOG.md); normative rules
> in [`docs/current/LAW.md`](LAW.md); how-to commands in
> [`docs/current/OPERATIONS.md`](OPERATIONS.md).

## Lifecycle

- **Tier 0 v0.1 — LOCKED.** Frozen v2 errata implemented — non-boss Frozen is
  **soft control** (−50% next action + Shatter on the first Attack hit); bosses
  take **Vulnerable 2** instead (§2.2; R44). The v0.1 scorecard baseline and
  median identity are regression-locked (`test_errata.V02_MEDIAN`).
- **Tier 0.5 M5 — SHIPPED.** The M5–M8 archive world was the v1 run template;
  the live run model is now the real StS2 map (see Versions below). Older
  run-layer numbers are archived, never compared across template versions
  unlabeled.
- **Kokomi meter-20 — RATIFIED (R139, 2026-08-10)** on the fresh
  `RT9/D14/P6/C8` read (`review/active/sitting-reads-2026-08-08.md` §3). **The
  current build is the comparison baseline from now on** — the dead v0.3 W1
  comparator is not rebuilt, and later Kokomi numbers are compared against this
  state, not against the archived world.
- **Roster slot 4 — Zhongli countersigned (R108), not yet scheduled.** The deep
  dive is unblocked; the pre-slot-4 gate is the roster registry (`tier0/roster.py`).

## Roster

Ship order is stable and meaningful (`tier0/roster.py`); reports print it.

| id | display | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|
| `klee` | Klee | Mondstadt | Pyro, catalyst-grade (all attacks apply) | demolition | demolition, spark, reaction |
| `furina` | Furina | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Klee is the compatibility baseline character. Companion pools ship per nation:
`docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml`,
`docs/inazuma-companions.yaml`.

**Reference anchors** (measurement anchors, NOT roster members — no art, no
pool, no C# class): `ref_ironclad`, `real_ironclad`, `ref_silent`, `real_silent`
(`tier0/roster.py:165-171`). The scoring anchor is `("ref_ironclad", "starter")`
under the `generic` pilot, normalized so every axis reads exactly `3.0`.
`real_*` variants depend on a local `game_ref/` tree that is gitignored and
absent on a fresh clone.

## Content inventory

Live sim inventory (`docs/current/atlas/tier0-pilot-roster.md` §2): **301 cards
(3 acquisition-only Ancient side-sheet rows), 5
character sheets** (3 roster + 2 reference), **6 encounters, 15 pilot weight
sets**. The battery encounters are frozen (`content/encounters/battery.yaml`,
FROZEN 2026-07-19). Card sheets: `docs/klee-cards.yaml`, `docs/furina-cards.yaml`,
`docs/kokomi-cards.yaml` (all three carry the `tempo_band:` field, 219 personal
rows total). Balance numbers (HP, decks, bands) live in
`tier0/content/characters/*.yaml`, the ratified artifact — not in the registry.

## Mod card coverage (generated)

Codegen: `tools/gen_roster_cards.py` (`tools/gen_klee_cards.py` per-character).
Manifests are the live coverage ledgers.

Coverage numbers below are read from the live manifests, not prose — the
`docs/` recaps carried stale figures (75/76 and 77/78 for Furina), which is
exactly why STATE reads the artifact.

- **Klee** — the compatibility baseline profile; fully generated.
- **Furina** — **81 of 82** generated, 1 blocked (`let_the_people_rejoice`,
  intentionally hand-written kit machinery)
  (`klee-mod/KleeCode/Cards/Furina/Generated/manifest.json`).
- **Kokomi** — **60 of 61** generated, 1 blocked (`KOKOMI_PROFILE`, catalyst
  Hydro cadence) (`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json`).

## Version / world stamps

The run-cell stamp is **`RT/D/P/C`**, read live via `tier05/cells.py`. Numbers
are never comparable across a stamp boundary unless labeled.

| stamp | value | source | meaning |
|---|---|---|---|
| `C` `CONSTANTS_VERSION` | **9** | `tier0/constants.py` | Slot-2 rarity floor restored ([USER] 2026-08-10, S4-G10 close-out): the shop's wildcard companion slot rolls Uncommon-or-better again in **both** engines, so Commons leave the paid channel and the 50-gold band is unreachable. Every §4.7 shop number taken under C6–C8 is archive. The `exp_shop_companion_channel` instrument repairs land inside the same window deliberately, so the corrected cell has one world to cite; further errata may join C9 until a number is quoted under it. **Erratum joined 2026-08-10 under that clause (no number had been published): the X7/X8 rarity promotions (R161, R162)** — `friendly_visit`, `chain_fuse`, `careful_arrangement` all Common → Uncommon, costs and numbers unchanged; Klee's pool now reads 29 Common / 28 Uncommon (was 32/25, total still 76) and `secret_stash`'s derived demolition-Common add-pool drops two entries. C8 was EB-30m/R127's `charge_per_turn` / `encore_per_turn` income powers (latent at the bump). |
| `RT` `RUNTEMPLATE_VERSION` | **10** | `tier0/constants.py` | R82 reopened ([USER] 2026-08-10, M7): the enchant events. Five events built on Enchant join the pools — Sapphire Seed (act 1), Field of Man-Sized Holes / Stone of All Time / Symbiote (act 2; Symbiote also act 3), Self-Help Book (all acts) — so event-pool odds move in **every** act for **every** character, and the enchantment vocabulary enters the run layer. Enchantments are post-draft only, so `D` and `P` are untouched. v9 event numbers do not carry across. v9 was EB-30m's Darv/Dusty Tome act-2 event (the single Ancient acquisition door, grants upgraded). |
| `D` `DRAFTER_VERSION` | **14** | `tier0/constants.py` | Generic-limb `core_complete` now requires an on-plan payoff. Held at 14 — the payoff-reach registration's pin (R121, six-step order; R125 widened the shield under the restores-not-redefines argument, no bump). |
| `P` `POLICY_VERSION` | **6** | `tier05/draft.py` | EB-29t: Enrage skill tax + Intangible per-hit cap (the promoted Test Subject reads). v5 was EB-24p's `reaction_triggered_this_turn` read; v4 was R124's both-Spotlight-modes read. |

- **Run template string** `RUN_NODE_TEMPLATE = "NNNRETN$ERB"` is DEAD as of v6,
  kept only as the archived-world name and for tests that pin a node sequence.
- **Acts** (`RUN_ACTS`): `act1` (easy_fights 3), `act2` "the Hive" (2),
  `act3` "Glory" (2).
- **Map (StS2 DAG):** `MAP_FLOORS = 16`, `MAP_TREASURE_FLOOR = 8`,
  `MAP_REST_FLOOR = 14`, `MAP_BOSS_FLOOR = 15`, `MAP_MAX_EDGES = 3`,
  `MAP_MAX_FLOOR_WIDTH = 6`, `MAP_PATHS = 6`. Room odds
  `N 0.53 / ? 0.22 / R 0.12 / E 0.08 / $ 0.05`.
- **A6 instrument:** `A6_INSTRUMENT_VERSION = 2` (in `tier0/harness/axes.py`, not
  `constants.py`) — the scorecard's application-uptime term
  (`0.5*aoe + 0.3*debuff + 0.2*uptime`), anchored ADDITIVELY so `ref_ironclad`
  stays exactly 3.00. This is a **scorecard** instrument version, separate from
  the run-cell stamp above; v1 and v2 A6 numbers are discontinuous by design.
- **Pilot policy:** `POLICY_VERSION` lives in `tier05/draft.py` (current value
  in the stamp table above) and enters the cell stamp as `P`. Heuristic weights live in
  `content/pilots/archetypes.yaml` and `pilot/policy.py`; `STOKE_*` are
  deliberately NOT in `constants.py`.

## Mod build environment (pinned)

Per the retired klee-mod DECISIONS ledger (frozen at tag
`pre-simplification-2026-08-06`): Slay the Spire 2 **v0.107.1**, commit `59260271`
(2026-06-18), Steam buildid `23811903`, appid `2868840`, branch `public`.
MegaDot v4.5.1, BaseLib 3.3.7.0, .NET SDK 9.0.316, ilspycmd 8.2.0.7535. The PCK
contract version is `roster-pck-v3`.

## Systems

- **tier0 combat kernel** — op interpreter, powers, statuses, reactions,
  resources; comparability-first and emit-only toward the run layer. 7-axis
  scorecard, anchor `(ref_ironclad, starter) = 3.0`, frozen battery.
  (`docs/current/atlas/tier0-engine.md`, `tier0-harness-tests.md`)
- **tier0.5 run sim + drafter** — run-level model, acts, runner, draft, and the
  real StS2 16-floor map/route policy. (`docs/current/atlas/tier05-sim-core.md`,
  `tier05-economy.md`, `tier05-metrics.md`)
- **understudy** — the bot playtest bridge driving the real game (Guardrail-7,
  no-fun rule). (`docs/current/atlas/understudy.md`)
- **klee-mod** — the C# character mod (`KleeCode/`) plus the PCK build/deploy
  pipeline. (`docs/current/atlas/klee-mod-cards.md`, `klee-mod-runtime.md`,
  `klee-mod-build-pck.md`)
- **vendor STS2_MCP bridge** — the vendored wire contract the understudy speaks.
  (`docs/current/atlas/vendor-sts2-mcp.md`)
- **art pipeline** — `ImageGen/` card/UI/model art staged into the roster mod
  and packed by `tools/build_pck.ps1`. (`docs/current/atlas/tools.md`)

## Active workstreams

Named here for status only. Open items are in
[`docs/current/QUEUE.md`](QUEUE.md); engineering tasks in
[`docs/current/BACKLOG.md`](BACKLOG.md).

- **Enemy remapping** — planned.
- **Art passes** — Furina and Kokomi surfaces (Kokomi's are newest).
- **Animation sprint 2.**
- **Axis-validity tracks** — Track A / Track E logs.
- **Kokomi playtest** — unrun.
- **Payoff-reach re-registration** — R121, running under DRAFTER_VERSION 14.

## Watch register (dormant)

Blessed mechanisms with a named quantity and a named trigger — monitored, not
open decisions, and nothing is tuned on the strength of being watched. Each
returns to [USER] only when its trigger fires: `W1` X4 (block-side Guest Cast),
`W2` X6 (salon power level), `W3` X12 (co-op reaction potency — instrument
unblocked since `O-1` closed; a new reading runs under EXPERIMENTS law),
`W4` X5 (fanfare floor), `W5` `lynette_box_trick` (X7, R161 — deliberately left
alone at its current rarity; as a companion card it is close to "what if I
high-roll a colorless option". **Trigger:** playtest shows it overperforming).
(Migrated from the retired watch-items docket, frozen at tag
`pre-simplification-2026-08-06`; `W5` added 2026-08-10.)
