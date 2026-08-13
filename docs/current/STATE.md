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

Live sim inventory (`docs/current/atlas/tier0-pilot-roster.md` §2): **303 cards
in the loader index** (of which 3 are acquisition-only Ancient side-sheet rows,
leaving the 300 the atlas quotes), **5 character sheets** (3 roster + 2
reference), **6 encounters, 15 pilot weight sets**. The battery encounters are
frozen (`content/encounters/battery.yaml`, FROZEN 2026-07-19). Card sheets:
`docs/klee-cards.yaml`, `docs/furina-cards.yaml`, `docs/kokomi-cards.yaml` (all
three carry the `tempo_band:` field, **220 personal rows** total — 76 / 82 /
62). Balance numbers (HP, decks, bands) live in
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
- **Kokomi** — **61 of 62** generated, 1 blocked (`ceremonial_garment`,
  hand-written) (`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json`).

## Version / world stamps

The run-cell stamp is **`RT/D/P/C`**, read live via `tier05/cells.py`. Numbers
are never comparable across a stamp boundary unless labeled.

| stamp | value | source | meaning |
|---|---|---|---|
| `C` `CONSTANTS_VERSION` | **10** | `tier0/constants.py` | The **tier0 engine half of the window-2 correctness batch** (`EB-104`, 2026-08-13), seven combat-kernel behavior fixes landed together and stamped once at the end of the window. `EB-95` player-side duration debuffs tick at the **enemy** side-turn end, and the first tick is skipped only when a **monster** applied the debuff (the authority's own predicate); enemy-owned Vulnerable/Weak/Frail keep ticking at their own turn end. `EB-96` a sleeping enemy is a side-turn **participant** — block clear, turn-start and turn-end hooks all run, while `advance_intent` and the Nemesis Intangible toggle stay suppressed; this moves a **frozen calibration-battery** number and two Act-1 bodies (3.545 → 3.653 mean turns, 79.70 → 79.50 mean end HP over 400 seeded fights). `EB-97` the Fanfare cap reads **live** max HP in both engines and recomputes on `gain_max_hp`, with a named C# cap constant so the parity lint can see the term. `EB-98` `masque_red_death` stops paying the flat-attack rider its 2026-07-25 redesign deleted. `EB-99` Guest Star generation applies the `personal_pool` filter in both engines. `EB-100` Encore Performance asks whether a card is **lit**, not who is designated, so it copies under the Orobas both-modes relic. `EB-101` Supporting Cast's first-play draw resolves **after** the triggering card, matching `SpotlightSystem`'s `BeforeCardPlayed`/`AfterCardPlayed` split. **No card sheet was edited**, so R179/M15's card-sheet clause is checked and not invoked — this bump rests on CONSTANTS 5's comparability criterion, with C6(a)/C7 as the direct precedent. Every pre-window combat number for every character is archive. C9's "further errata may join" clause was **spent** — it holds only until a number is published under the stamp, and the twelve-arm table of 2026-08-13 was published at `C9`. C9 was the slot-2 rarity floor restored ([USER] 2026-08-10, S4-G10 close-out): the shop's wildcard companion slot rolls Uncommon-or-better again in **both** engines, so Commons leave the paid channel and the 50-gold band is unreachable. Every §4.7 shop number taken under C6–C8 is archive. The `exp_shop_companion_channel` instrument repairs land inside the same window deliberately, so the corrected cell has one world to cite; further errata may join C9 until a number is quoted under it. **Erratum joined 2026-08-10 under that clause (no number had been published): the X7/X8 rarity promotions (R161, R162)** — `friendly_visit`, `chain_fuse`, `careful_arrangement` all Common → Uncommon, costs and numbers unchanged; Klee's pool now reads 29 Common / 28 Uncommon (was 32/25, total still 76) and `secret_stash`'s derived demolition-Common add-pool drops two entries. C8 was EB-30m/R127's `charge_per_turn` / `encore_per_turn` income powers (latent at the bump). |
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | The **run-layer half of the window-2 correctness batch** (`EB-104`, 2026-08-13), five fixes batched into one bump for the same reason v8 batched two — all `RUNTEMPLATE` content, one window, none quotable alone. `EB-102` `resolve_shop` finally receives the run's **Featured Banner**, so the shop can no longer sell a 5-star the banner excluded from every reward screen; it changes which card `rng.choice` lands on, so every §4.7 shop-channel figure taken under `C9` renumbers, and it lands **before** the `M14` shop rerun as that row required. `EB-103` potion capacity is derived from held relics **on read**, so a mid-run Potion Belt is visible to `resolve_event` and its grant is no longer dropped unlogged. `EB-110` the rest-site heal **floors** where it rounded, matching the authority's truncation through `SetCurrentHpInternal` — 2.39 HP/run of one-directional sim-generous bias removed from the HP ledger. `EB-111` Book of Five Rings counts **event** deck-adds through a single `note_add` door, not only shop buys and reward picks (88 uncounted adds across 64 book-holding runs in 300). `EB-112` event card-reward screens roll rarity through **`RARITY_ODDS`** like any other reward screen — 20.0% Rare per offer becomes 5.0% on three shipped options in acts 1 and 2 for every character; **`RARITY_ODDS` itself is unmoved**, only the site that failed to consult it. No drafter or pilot code moved, so `D` and `P` are untouched and the payoff-reach `D14` pin stands; `C` moved in the same window on its own ground (the engine half above), each field once, together, at the end. No v11 run-layer number carries across. **Re-baselined at the bump** — the twelve-arm standing table, `review/active/sitting-reads-2026-08-13.md`. v11 was the coordinated 2026-08-13 window (`EB-82` + `EB-85`), batched into one bump because both are `RUNTEMPLATE` content and neither was quotable alone — `M14` enumerates the window and asked for exactly one bump at the end of it. **(a) `EB-82`:** `grave_of_the_forgotten` joins the **act-3** event pool (2 own → 3 own), so act-3 event odds move for every character, and its Accept branch grants `forgotten_soul` — an **event** relic no reward, Neow or Ancient roll can reach — which arms `damage_per_exhaust` mid-run and puts damage into every later fight of that run. **(b) `EB-85`:** five places where tier0 modelled an enchantment differently from the class `sts2.dll` v0.107.1 ships, each re-verified against the binary first. Three move what an enchant event may **target** — Nimble gates on `GainsBlock` not `type == "skill"`, Swift has no type override at all (Self-Help Book's third reading was locked on Klee's printed starter for all of v10), and Nimble never rides `block_next_turn` — and two move what it **pays**: the Nimble rider is collected on every Block gain rather than once per card play, and Perfect Fit refuses the opening shuffle instead of acting as a free Innate. Enchantments stay post-draft only and no drafter or pilot code moved, so `D` and `P` are untouched and the payoff-reach `D14` pin stands; `C` did not move either, because the window's other two branches (`EB-70`, `EB-83`) wrote no code. No v10 enchant number and no v10 act-3 number carries across. v10 was R82 reopened ([USER] 2026-08-10, M7): the enchant events. |
| `D` `DRAFTER_VERSION` | **14** | `tier0/constants.py` | Generic-limb `core_complete` now requires an on-plan payoff. Held at 14 — the payoff-reach registration's pin (R121, six-step order; R125 widened the shield under the restores-not-redefines argument, no bump). |
| `P` `POLICY_VERSION` | **7** | `tier05/draft.py` | R176: the pilot values `copy_companion_in_hand` / `replay_next_companion` (EB-17p's 40,396 draws / 0 plays was pilot scoring, not an unreachable condition) — every Klee tier0.5 number moves; the payoff-reach `DRAFTER_VERSION=14` pin is untouched. v6 was EB-29t's Enrage/Intangible reads; v5 was EB-24p's `reaction_triggered_this_turn` read; v4 was R124's both-Spotlight-modes read. |

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
  pipeline, and since 2026-08-13 a headless C# test project (`KleeTests/`,
  `EB-105`). Co-op therefore has a **partial** automated backstop, not none and
  not a full one: per-seat ownership and attribution are testable; multiplayer
  transport and anything needing a live `CombatState` are still play-only
  (`klee-mod/KleeTests/README.md`).
  (`docs/current/atlas/klee-mod-cards.md`, `klee-mod-runtime.md`,
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
- **Payoff-reach re-registration** — R121, pinned at DRAFTER_VERSION 14.
  Predictions committed 2026-08-13 (R186); the sprint is unrun and waits on the
  settle-first freeze (EXPERIMENTS).

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
