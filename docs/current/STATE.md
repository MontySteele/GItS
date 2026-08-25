# STATE

> **What currently ships** — roster, systems, versions, and active workstreams.
> Snapshot only: how a stamp reached its current value lives in the commit
> messages that carry it, not here. Open decisions live in
> [`docs/current/QUEUE.md`](QUEUE.md); engineering tasks in
> [`docs/current/BACKLOG.md`](BACKLOG.md); normative rules in
> [`docs/current/LAW.md`](LAW.md); measurement law and active registrations in
> [`docs/current/EXPERIMENTS.md`](EXPERIMENTS.md); how-to commands in
> [`docs/current/OPERATIONS.md`](OPERATIONS.md).

## Live cell

**`RT12 / D16 / P9 / C14`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **4**. Numbers are never comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable
(`EXPERIMENTS.md`).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | The run-layer half of the window-2 correctness batch (`EB-104`): the shop receives the run's Featured Banner, potion capacity is derived from held relics on read, the rest-site heal floors, Book of Five Rings counts event deck-adds through one door, and event card-reward screens roll rarity through `RARITY_ODDS`. |
| `D` `DRAFTER_VERSION` | **16** | `tier0/constants.py` | `EB-118` Phase 2's two formerly-inert drafter terms are live: `STATIC_ETHEREAL_SHARE` now prices a shipped card (`big_badda_boom` 8.0000 → 4.8000 base, 8.0000 upgraded), and `choose_one`'s `MAX(modes)` arbitration is reachable but moves no number. The share is **RATIFIED at 0.6 (R205)**; the read and the rank plateau are recorded at the constant in `tier05/draft.py`. `D15` beneath it is `EB-43` — the spotlight limb of `core_complete`/`_core_progress` requires a machinery payoff. |
| `P` `POLICY_VERSION` | **9** | `tier05/draft.py` | The `EB-118` Phase-2C mode-chooser flip: `MODE_CHOOSER_ENABLED` is `True` and `effects._chosen_mode` asks `policy.choose_mode` — argmax of the pilot's per-op valuations over the live board, minus the TRUE HP an overdrawing `spend_encore` costs, ties to the lowest index. `PILOT_WEIGHTS_VERSION` 4 labels the weight set now that `MODE_OVERDRAW_HP_VALUE` is read; no weight VALUE has moved from the hand-picked vector. Phase-2A's `PILOT_POLICIES_ENABLED = True` (Klee bomb placement, Kokomi chosen exhaust) is inside this value at `P8`. |
| `C` `CONSTANTS_VERSION` | **14** | `tier0/constants.py` | `deep_breath`'s mode 2 is `spend_encore 3` + `draw 3` (R205); mode 1 and every frame field are unchanged. The world beneath it is `C13`, the `EB-118` Phase-2 sheet-and-engine integration window — `big_badda_boom` (Ethereal carrier, R201's kill rider), the twelve `place_bomb` rows leaving `target: random_enemy`, `bomb_damage_per_rotation` as a new engine power with a once-per-turn latch, `lasting_impression`'s `{encore: +2}`, and `deep_breath`'s conversion to `choose_one` — and it is the world the standing baseline below was read in. |

**Standing baseline:** `review/active/sitting-reads-2026-08-24-c13-d16.md` —
twelve arms, taken at `RT12/D16/P7/C13`, with §8's dated addendum carrying the
two `real_*` floor rows (`real_ironclad` 5.5% win / 67.2% act-1, `real_silent`
1.3% / 54.4%) after `game_ref/` was restored. It is a `P7`/`C13` reading: the
`P8` and `P9` activation windows closed above it, and the read they owe is
R202 step (iii)'s single Phase-2 post-read (in flight, below). Under **R207** a
published standing table is owed at a meaningful product milestone or when a
pending decision needs one; intermediate attribution is by commit-hash scratch
comparison, which is not citable the way a stamped baseline is
(`EXPERIMENTS.md`). Version stamps themselves are unchanged: every change to a
published-world variable still bumps its stamp.

Pinned, and NOT part of the run-cell stamp:

- `A6_INSTRUMENT_VERSION = 2` (`tier0/harness/axes.py`) — the scorecard's
  application-uptime term (`0.5*aoe + 0.3*debuff + 0.2*uptime`), anchored
  ADDITIVELY so `ref_ironclad` stays exactly 3.00. v1 and v2 A6 numbers are
  discontinuous by design.
- Heuristic pilot weights live in `content/pilots/archetypes.yaml` and
  `pilot/policy.py`; `STOKE_*` are deliberately NOT in `constants.py`.
- `RUN_NODE_TEMPLATE = "NNNRETN$ERB"` is DEAD as of `RT` v6, kept only as the
  archived-world name and for tests that pin a node sequence.
- **Acts** (`RUN_ACTS`): `act1` (easy_fights 3), `act2` "the Hive" (2), `act3`
  "Glory" (2).
- **Map (StS2 DAG):** `MAP_FLOORS = 16`, `MAP_TREASURE_FLOOR = 8`,
  `MAP_REST_FLOOR = 14`, `MAP_BOSS_FLOOR = 15`, `MAP_MAX_EDGES = 3`,
  `MAP_MAX_FLOOR_WIDTH = 6`, `MAP_PATHS = 6`. Room odds
  `N 0.53 / ? 0.22 / R 0.12 / E 0.08 / $ 0.05`.

## Lifecycle

- **Tier 0 v0.1 — LOCKED.** Frozen v2 errata: non-boss Frozen is **soft
  control** (−50% next action + Shatter on the first Attack hit), bosses take
  **Vulnerable 2** instead (§2.2; R44). The v0.1 scorecard baseline and median
  identity are regression-locked (`test_errata.V02_MEDIAN`).
- **Tier 0.5 M5 — SHIPPED.** The live run model is the real StS2 map; the
  M5–M8 archive world was the v1 run template, and its run-layer numbers are
  never compared across template versions unlabeled.
- **Kokomi meter-20 — RATIFIED (R139).** The current build is the comparison
  baseline; the dead v0.3 W1 comparator is not rebuilt.
- **Roster slot 4 — Zhongli countersigned (R108), not yet scheduled.** The deep
  dive is unblocked; the pre-slot-4 gate is the roster registry
  (`tier0/roster.py`).

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
under the `generic` pilot, normalized so every axis reads exactly `3.0`. The
`real_*` variants depend on a local `game_ref/` tree that is gitignored and
absent on a fresh clone; both pools verify (ironclad 76, silent 87) and both
anchors load. Still owed there: three `*_char_facts.yaml` that no roster arm
reads, a durable-backup location ([USER]'s call), and a guard against the
destroyer — BACKLOG `EB-128`.

## Content inventory

Live sim inventory (`docs/current/atlas/tier0-pilot-roster.md` §2): **317 cards
in the loader index** (3 are acquisition-only Ancient side-sheet rows, leaving
the 314 the atlas quotes), **5 character sheets** (3 roster + 2 reference),
**6 encounters, 15 pilot weight sets**. The battery encounters are frozen
(`content/encounters/battery.yaml`, FROZEN 2026-07-19). Card sheets
`docs/klee-cards.yaml`, `docs/furina-cards.yaml` and `docs/kokomi-cards.yaml`
all carry the `tempo_band:` field and hold **234 personal rows** (76 / 82 / 76);
Kokomi's 76 are **5 basic / 31 common / 26 uncommon / 14 rare, 70 draftable**.
Balance numbers (HP, decks, bands) live in `tier0/content/characters/*.yaml`,
the ratified artifact — not in the registry. Furina's pool carries **zero**
`raise_fanfare_cap` riders: register lint `R7` retired with them, and LAW now
describes `Fanfare Cap +X` as an available explicit verb rather than a rider
every Power carries.

## Mod card coverage (generated)

Codegen: `tools/gen_roster_cards.py` (`tools/gen_klee_cards.py` per-character).
The manifests are the live coverage ledgers, and these figures are read from
them rather than from prose.

- **Klee** — the compatibility baseline profile; fully generated.
- **Furina** — **81 of 82** generated, 1 blocked
  (`let_the_people_rejoice`, intentionally hand-written kit machinery)
  (`klee-mod/KleeCode/Cards/Furina/Generated/manifest.json`).
- **Kokomi** — **70 of 76** generated, 6 blocked
  (`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json`).
  `ceremonial_garment` is hand-written; the other five each name an
  unimplemented C# runtime grammar rather than a defect: `the_gunbai_turns` and
  `raise_the_sashimono` (op `grant_sly_this_turn`), `what_the_tokoyo_took` (an
  `amount_formula` over `discards_this_turn` needs a CalculatedVar bound to that
  count), `gyorin_formation` (`bonus_formula` `1_per_2_charge` on `block` has no
  rider and would render as the bare base), and `what_the_tokoyo_returns` (a Sly
  `recall_to_draw` from **discard**; only the exhaust source is built). Two more
  generate but ship WITHOUT an upgrade under the no-partial-upgrades rule:
  `send_the_runner` and `wheel_the_ranks`. Of the fourteen `EB-69` fill cards
  the sim has all fourteen, the mod nine of them and seven of their upgrades —
  a declared asymmetry, tracked as `EB-122`.

## Mod build environment (pinned)

Slay the Spire 2 **v0.107.1**, commit `59260271` (2026-06-18), Steam buildid
`23811903`, appid `2868840`, branch `public`. MegaDot v4.5.1, BaseLib 3.3.7.0,
.NET SDK 9.0.316, ilspycmd 8.2.0.7535. The PCK contract version is
`roster-pck-v3`; the shipped mod package is `klee` **v0.2**
(`klee-mod/Klee/manifest.json`, `min_game_version` 0.107.1). Pins frozen at tag
`pre-simplification-2026-08-06`.

## Systems

- **tier0 combat kernel** — op interpreter, powers, statuses, reactions,
  resources; comparability-first and emit-only toward the run layer. 7-axis
  scorecard, anchor `(ref_ironclad, starter) = 3.0`, frozen battery.
  **NO axis value gates anything (R204):** the live per-axis deck-band system is
  retired as acceptance law roster-wide — all three characters' `deck_bands` /
  `stale_bands` data, both loader accessors, the `BAND EXCEEDED` emission, and
  the hard deck-band and median-identity tests — with **no replacement bands
  ratified**. Seven-axis values and declared identity comparisons are
  **reportable diagnostics only**: they may identify something to investigate,
  and may not gate a merge, require re-banding, or justify moving a value. The
  per-character identity comparison was demoted, not deleted — it reports
  through `axes.identity_flags` on every deck of every run. Klee's
  frontload-over-scaling identity remains **binding design intent** (LAW).
  **Ratified 1,000-fight `winrate_bands` are UNAFFECTED.** Kokomi's rotation law
  lives at three seams off one predicate (`Card.is_junk`): a Status or a Curse
  is never one of her cards — never conscripted, dropped from the unfiltered
  chosen-Exhaust pool, and paying no Charge and no Burst particle on exhaust by
  any route. Artifact itself is C#-only and unmodelled in sim: `AuraPower` and
  `BombPower` are `Buff`-typed and coexist with Artifact, while `FrozenPower`
  and reaction-applied Vulnerable / Weak / Poison stay real Debuffs.
  (`docs/current/atlas/tier0-engine.md`, `tier0-harness-tests.md`)
- **tier0.5 run sim + drafter** — run-level model, acts, runner, draft, and the
  real StS2 16-floor map/route policy. (`docs/current/atlas/tier05-sim-core.md`,
  `tier05-economy.md`, `tier05-metrics.md`)
- **understudy** — the bot playtest bridge driving the real game (Guardrail-7,
  no-fun rule). (`docs/current/atlas/understudy.md`)
- **klee-mod** — the C# character mod (`KleeCode/`), the PCK build/deploy
  pipeline, and a headless C# test project (`KleeTests/`, `EB-105`). Co-op has a
  **partial** automated backstop: per-seat ownership and attribution are
  testable; multiplayer transport and anything needing a live `CombatState` is
  play-only (`klee-mod/KleeTests/README.md`).
  (`docs/current/atlas/klee-mod-cards.md`, `klee-mod-runtime.md`,
  `klee-mod-build-pck.md`)
- **vendor STS2_MCP bridge** — the vendored wire contract the understudy speaks.
  (`docs/current/atlas/vendor-sts2-mcp.md`)
- **art pipeline** — `ImageGen/` card/UI/model art staged into the roster mod
  and packed by `tools/build_pck.ps1`. (`docs/current/atlas/tools.md`)

## Active workstreams

Status only. Open decisions are in [`QUEUE.md`](QUEUE.md); engineering tasks in
[`BACKLOG.md`](BACKLOG.md).

- **`EB-118` richness pass — Phase 2 is COMPLETE; Phase 3 is the live front.**
  All three Phase-2 windows are closed: the `C13`/`D16` content window with its
  single re-baseline, then 2A's activation on its own `P8`, then 2C's on `P9`
  with `C14` beside it. **IN FLIGHT: R202 step (iii)'s Phase-2 post-read** —
  ONE read over both activation windows, not one per switch — which is step
  (iv)'s W1 pre-state and the last thing between here and Window 1. Phase 3 is
  ratified as a governing plan (R202, amended at R205 and R207) and its nine
  calls, guardrails and priority order live in BACKLOG `EB-118`. **Staged and
  INERT, waiting on windows rather than on work:** `eb118-w1-labels`
  (`184d63d`) and `eb125-w2-bodies` (`e2e6da0`) — merging one IS the pull.
  **Window 3 lands as ONE public `C`/`D` window with one standing read**, its
  per-character attribution taken as commit-hash scratch comparisons (R207).
- **Register diet** — this file's half is DONE; the `BACKLOG.md` half is gated
  on `W2` landing (BACKLOG `EB-131`).
- **Payoff-reach re-registration — RUN AND GRADED 2026-08-24.** R121's
  countersigned six-step order has run end to end. The grade, the controls, the
  tripwires and the two defects the run found (`EB-123`, `EB-124`, both since
  fixed) are in `EXPERIMENTS.md`; the design call it raised (`M37`) is ruled
  (R199) and its authorization is the Phase-3 fence in BACKLOG `EB-118`.
- **Kokomi playtest** — unrun
  (`docs/current/playtest/kokomi-playtest-protocol.md`).
- **Enemy remapping** — planned. **Art passes** — Furina and Kokomi surfaces
  (Kokomi's are newest). **Animation sprint 2.** **Axis-validity tracks** —
  Track A / Track E logs.

## Open [USER] pile (pointers)

Every row below is OPEN in [`QUEUE.md`](QUEUE.md) and owned by [USER]: Kokomi's
stability-band declaration (`S4-G6`), the staged lever-2 pull-or-not
(`S4-G13`) and her protocol playtest (`S4-G14`); the shop-rerun slate entry and
countersign (`M14`); the regret-margin prediction slots (`M13`); the `M17` sweep
countersign and its post-sweep `C2` landing; the name/lore and art eyes-on pile
(`S4-G11`, `S4-G12`/`CC-G1`/`CC-G2`, `S4-G17`, `M16`, `M26`, `M19`, `S8`+`S10`,
Art debt); and the Fontaine Rares close-out (`M10`).

## Watch register (dormant)

Blessed mechanisms with a named quantity and a named trigger — monitored, not
open decisions, and nothing is tuned on the strength of being watched. Each
returns to [USER] only when its trigger fires.

- `W1` X4 (block-side Guest Cast), `W2` X6 (salon power level), `W3` X12 (co-op
  reaction potency — instrument unblocked since `O-1` closed; a new reading
  runs under EXPERIMENTS law), `W4` X5 (fanfare floor).
- **`W5` `lynette_box_trick`** (X7, R161) — deliberately left at its current
  rarity; as a companion card it is close to "what if I high-roll a colorless
  option". **Trigger:** playtest shows it overperforming.
- **`W6` `gyorin_formation` — pre-emptive Block RATE.** Explicitly not a
  single-turn spike: the card is 6 Block now (+1 per 2 Charge) and 6 more at the
  start of the next turn — 12 across two turns, not 12 on one. The worry is 6
  pre-emptive Block *every turn* for as long as it keeps coming around, on a
  character whose Charge bank fills on every rotation and is never spent (R80).
  **Trigger:** her stability number moves materially in the post-fill baseline.
- **`W7` `what_the_tokoyo_took` — upper-tail discard count and realized
  damage.** The reprice (cost 2 → 1, 3-per → 4-per) was ruled as a real power
  increase. A chained turn reaching 6+ discards is 30 damage for 1 energy (33
  upgraded). **The obligation is on the INSTRUMENT:** the post-fill baseline
  must report **p90/p99 per-turn discard count and this card's realized damage
  distribution**, never a worked example. The tail is the whole question.
- **`W8` `send_the_runner` — burst-particle cadence.** Charge is a wash
  (`CHARGE_PER_EXHAUST = 1` replaces the dropped grant exactly), but the card
  now also pays `KOKOMI_BURST_PER_EXHAUST = 2` particles it never paid before —
  at Common, at cost 0, repeatable. **Trigger:** Burst frequency across a run
  reads above the ratified meter-20 cadence (R139) in the post-fill baseline.
- **`W9` `X9` — Kokomi's Charge bank, uncapped and never spent.** R188 ruled
  workshop axis **G**, the null option: **no Charge read budget** — a deferral
  of a nerf, not an endorsement, with the §3.3 double read ruled intended
  deckbuilder stacking. Reads per turn are instrumented and the instrument is
  deliberately inert: `resources.note_charge_read` tallies every resolved read
  onto `CombatState.charge_reads_this_turn` tagged by source and `combat` emits
  one `charge_reads_turn` sample per completed player turn; nothing in engine,
  pilot or drafter reads the tally back, so it is not a budget and cannot become
  one by accident. Declared blind spot: the sample rides `turn_close`, which a
  turn ending in the last kill or the player's death never reaches, so the
  truncation is toward the BUSY end. **Trigger:** a reads-per-turn reading or a
  live playtest shows repeatable reads dominant — "dominant" is not a number
  yet, and §5.1 of
  `review/active/charge-reads-per-turn-registration-2026-08-13.md` is the slot
  that makes it one, and that slot is [USER]'s (BACKLOG `EB-78`).

(Migrated from the retired watch-items docket, frozen at tag
`pre-simplification-2026-08-06`; `W5` added 2026-08-10, `W6`–`W8` at `EB-69`
2026-08-23, `W9` 2026-08-24.)
