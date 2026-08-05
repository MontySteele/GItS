# understudy/ — the bot playtest apparatus

Opened 2026-08-04 by the Understudy sprint. Brief:
`docs/understudy-kickoff-brief.md`. P0 findings and the three ratified
rulings: `docs/understudy-p0-findings.md`. Phase-0 measurement:
`docs/understudy-phase0-report.md`. The Phase-0 skim response, signed:
`docs/understudy-countersign-2026-08-04.md` (R93–R97 in `tier0/DECISIONS.md`).

This directory drives the **real game** through the vendored STS2MCP bridge
(`vendor/STS2_MCP/`). It is not a simulator and it must never become one.

| file | what it is |
|---|---|
| `bridge.py` | stdlib HTTP client for `localhost:15526`; the wire contract is `vendor/STS2_MCP/docs/raw-simplified.md` |
| `adapter.py` | wire JSON -> tier0 engine objects, with its fidelity losses enumerated in the module docstring |
| `deckwatch.py` | the deck reconstructed from combat piles; the wire hides it everywhere else |
| `policy_v0.py` | the counterfactual arm: delegates every decision to the live tier0/tier05 entry points, and returns *nothing* where it cannot delegate faithfully. **Frozen** — it is one arm of a published measurement, and editing it would retroactively move a quoted number |
| `policy_v1.py` | R93's seven approved revisions. The policy the soak flies |
| `naming.py` | revision #7: resolved card / target / option NAMES per action |
| `rng.py` | the dedicated policy stream, and the refusal that keeps a game seed out of it |
| `harness.py` | `begin` / `state` / `act` — the Phase-0 measurement loop |
| `soak.py` | **P1**: N unattended policy_v1 runs, telemetry, watchdog, reversibility |
| `report.py` | the morning report — defects, outliers, curves. No LLM |
| `analyze.py` | the Phase-0 divergence analysis |
| `logs/` | per-run decision JSONL; `phase0-<seed>.jsonl` (committed), `soak/` (gitignored) |

## The two rules this directory exists under

**Guardrail-7.** Every number a bot or an LLM produces here is a
**bot-limited floor**, in exactly the sense pilot-limited already means in
tier 0.5. No winrate, no HP curve and no damage figure from this directory is
a balance conclusion, and none of them are quotable as one. The apparatus
files defects and telemetry; it authors no design.

**No fun, ever.** A JSON-state agent cannot see the screen. Legibility,
readability, feel and fun remain [USER]-only instruments and nothing in this
directory may be read as evidence about them.

## Running the Phase-0 loop

Prerequisites: the bridge installed (`klee-mod\build\deploy_bridge.ps1`),
`steam_appid.txt` in the game root, Steam running, the game launched
directly from its exe.

```
python -m understudy.harness begin           # stamp the seed and speed
python -m understudy.harness state           # read the screen + policy_v0
python -m understudy.harness act '{"action":"end_turn"}' --why "..."
```

`act` recomputes the counterfactual at the current state *before* posting, so
a log line can never pair a choice with a policy answer from a screen that has
since moved.

## What policy_v0 will not answer

Three decision classes return no counterfactual and are excluded from the M2
denominator: events, boss-relic picks, and the Crystal Sphere minigame. The
reasons are in `policy_v0.NO_COUNTERFACTUAL`, and they are all the same
reason — the sim scores those by ids the wire does not carry, so any answer
would be a guess contributing noise to a number about judgment.

## policy_v1 — the seven revisions (R93)

| # | revision | where | what it changed |
|---|---|---|---|
| 1 | free expiring cards first | `_free_expiring` | a playable 0-cost Ethereal card is played before anything is scored |
| 2 | block-panic gate + kill line | `_gated_ladder` | the panic rung must show the Block on offer can dent the incoming, or that a kill removes more |
| 3 | map one ply deeper | `_map` | `leads_to` is on the wire; the reduction goes from depth 1 to depth 2, summed undiscounted as `route._plan` sums it |
| 4 | the potion arm | `_potion_arm` | `tier0.engine.potions.try_use_potions` is run against the reconstruction and the drink read back out of the diff |
| 5 | `next_fight` into the rest arm | `_rest` | the flag comes from the map lookahead in the memo instead of being hard-coded False |
| 6 | in-combat choice overlay | `_choice_overlay` | Center Stage vs Guest Cast on deck composition; other choose screens fall back to `score_offer` |
| 7 | resolved card NAMES | `naming.py` | every posted action carries the identity of what it names — **the P1 blocker** |

Two numbers live in `policy_v1` and nowhere else: `BLOCK_MATTERS_FRACTION` and
`COMPANION_SHARE_FOR_GUEST_CAST`. They are **bot-policy dials, not balance
constants**. They do not belong in `tier0/constants.py`, they are recorded per
run in the log so a log stays self-describing when they move, and no number
downstream of them is quotable as evidence about the game.

Draft, shop and the deck-management overlays were deliberately NOT revised:
Phase-0's divergences there were diagnosed as gaps in the SIM's scoring, and
R96 routed all three to their chartered streams. Re-deciding them inside
Understudy would be authoring design, which bots do not do.

## Running a soak (P1)

```
python -m understudy.soak --runs 20 --report
```

Setup and teardown are automatic and logged: `steam_appid.txt` created and
deleted, the bridge deployed and removed via
`klee-mod/build/deploy_bridge.ps1`, the speed setting captured and restored.
The reversibility ledger is written to
`understudy/logs/soak/reversibility-<stamp>.json` **before** each change lands
— a ledger written after the change is empty exactly when the process dies
mid-change, which is the one moment anybody needs it.

Steam must be running (the game is launched directly from its exe, which is
why the appid file is needed). Readiness is judged on the `options` key of a
menu state, **never** on `GET /`: the HTTP server answers about 20 seconds
before the main menu has buttons (R97/5a). `--no-setup` attaches to a game you
launched yourself and makes no game-dir changes at all.

Any resumable run found on the profile is abandoned rather than negotiated
with (R97/5b).

---

# Telemetry schema

**SHARED SURFACE TO BE.** The brief pre-registered this as the same telemetry
surface Track B wants out of the sim ("share the schema; write the
cross-session note if Track B has started"). Track B has not started reading
it, so this section is a heads-up rather than a cross-session note under the
D4/D5 rule — but **the moment it does, renaming or repurposing a key below is
a shared-schema change** and takes a cross-session note first, in the house
pattern (`docs/animation-sprint-2-log.md`). Adding keys is free.

Logs live under `understudy/logs/soak/` and are **gitignored**: they are
per-machine run output, not evidence anyone else can reproduce.

## Files

| file | contents |
|---|---|
| `soak-<stamp>-index.json` | one object: the soak's parameters, per-run summaries, the reversibility ledger |
| `soak-<stamp>-run<NNN>.jsonl` | one run; one JSON object per line, `record` discriminates |
| `reversibility-<stamp>.json` | the game-dir change ledger |

## Record types (the `record` field)

### `run_begin`

`character`, `policy`, `dials` — the policy dials in force. Recorded per run so
a log is self-describing when the dials later move.

### `seed_read_back`

`seed` — the game-generated seed, read from `GET /api/v1/compendium` after
embarking. R95's read-back arm. **Never fed to a policy stream**; `rng.py`
refuses a label of that shape and the refusal is the enforcement.

### `decision` — one posted action

| key | meaning |
|---|---|
| `i` | action ordinal within the run |
| `state_type`, `act`, `floor`, `round`, `hp` | where it happened |
| `action` | the exact body POSTed |
| `names` | **revision #7.** Resolved identities: `verb`, `card_id`, `card_name`, `card_cost`, `card_type`, `card_upgraded`, `target_id`, `target_name`, `target_hp`, `potion_slot` / `potion_id` / `potion_name`, `option_index` / `option_name`, `node_kind` / `leads_to_kinds`, `item_name`, `screen_type`. Only applicable keys are present. |
| `hand` | every card in hand by name, index-ordered — the denominator a sequencing decision is read against |
| `mechanical` | true when the screen asked nothing (dialogue, reward pile, single-relic chest) |
| `policy` | policy_v1's own record: `revision` (`v0`, `v1.1`…`v1.6`), `category`, `label`, `rationale`, `notes` |
| `status`, `message` | the bridge's answer |

This is the P1 blocker discharged: **no row in this log needs a human to read
prose to know what was played.** A sequencing divergence can be categorised
from `names.card_name` and `policy.revision` alone, which is precisely what
Phase 0 could not do.

### `fight` — one fight, closed

| key | meaning |
|---|---|
| `act`, `floor`, `kind` | `monster` / `elite` / `boss` |
| `enemies` | `[{name, max_hp}]` as the fight opened |
| `hp_start`, `hp_end`, `hp_lost`, `max_hp` | the HP ledger |
| `turns` | highest round reached |
| `outcome` | `survived` / `died` / `won` / `interrupted` / `superseded` |
| `hp_trajectory` | `[[round, hp, block], ...]`, sampled at each turn opening |
| `incoming_by_turn` | `[[round, telegraphed_damage, n_attacking_enemies], ...]`, read before block |
| `cards_played` | `[[round, card_name], ...]` |
| `potions_used` | `[[round, potion_name], ...]` |
| `damage_by_source` | `{card_or_potion_name: total}` |
| `damage_dealt`, `damage_taken` | totals |

**Attribution rule, stated because all three are approximations that
under-count rather than invent:**

- *damage by source* is the enemy `hp + block` drop observed on the state read
  immediately after an action, credited to the card that action named.
  Anything resolving in the same frame batch lands on the play that triggered
  it — usually right (a summon's hit belongs to the summon card), occasionally
  wrong (a bomb detonating on a later play).
- *damage taken* is the player HP drop across a round boundary, credited to
  the enemy turn as a whole. The wire does not narrate which enemy landed
  which hit.
- *incoming per turn* is the sum of telegraphed attack intents at the player's
  turn opening, before block. Intent ramps are structurally invisible to the
  wire, so this is this-turn-accurate and future-turn-blind — the same limit
  `adapter.py` already declares.

### `defect` — a filed crash, soft-lock, stall or NRE

`kind` is one of `process_died`, `overlay_softlock`, `no_progress`,
`action_ceiling`, `run_timeout`, `bridge_unreachable`, `no_action`,
`menu_loop`, `embark_loop`, `no_embark`, `no_embark_path`,
`unexpected_start_state`. Plus `seed`, `act`/`floor`, `state_dump` (piles
collapsed to counts) and `recent` — the last dozen state fingerprints, which is
what a stall looks like from inside.

The subset in `soak._HARNESS_SIDE` means **the instrument** failed rather than
the build. Two defects of the same harness-side shape halt the soak; that is
the stop-and-surface rule, and it exists so a broken harness does not fill a
night with the same row.

### `forced_default`

A screen policy_v1 declined and the driver walked past to keep the run moving.
Not a defect — but every one is a decision nobody made, so they are counted and
surfaced in the report.

### `game_over` / `run_end`

`won`; then `outcome`, `actions`, `wall_s`, `fights`, `final_act`,
`final_floor`, `defects`, `forced_defaults`, `log`.

## Reading it

```
python -m understudy.report              # the most recent soak
python -m understudy.report <stamp>
```

Defects first, outliers second, curves third. The ordering is deliberate: a
page that opens with a winrate invites the reader to read a winrate, and there
is no winrate here that means anything.
