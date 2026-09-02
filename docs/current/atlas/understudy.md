# Atlas: understudy

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `understudy/` — the bot playtest apparatus. Tests live at
`tier0/tests/test_understudy_{rng,soak,policy_v1,hangwatch,give_card,frames,scenario}.py`.

## 1. Purpose

`understudy/` drives the **real game** — a live STS2 process — through the
vendored STS2MCP HTTP bridge on `localhost:15526`, so a bot (or an LLM) can
play GItS unattended and file defects, crashes, soft-locks and per-fight
telemetry. Two policies fly it: `policy_v0`, the counterfactual arm that
delegates every decision to the live tier0/tier05 entry points, and
`policy_v1`, R93's seven revisions and the arm the soak runs. It is explicitly
**not a simulator and must never become one** (`understudy/README.md:11`) —
tier0/tier05 are the simulator and nothing here re-implements them; the adapter
exists so the sim's own scoring functions can be *called* rather than retyped
(`adapter.py:1-18`). It authors no design: bots file defects and telemetry,
never balance conclusions (`docs/understudy-kickoff-brief.md:103-110`).

## 2. Entry points

Run from the repo root. Everything is stdlib — no `requests` (`bridge.py:3-6`).
Live verbs need the bridge deployed (`klee-mod\build\deploy_bridge.ps1`),
`steam_appid.txt` in the game root, Steam running, the game launched from its exe.

```sh
# Phase-0 measurement loop (LLM-driven, one run, fully logged)
python3 -m understudy.harness begin                       # stamp seed + speed
python3 -m understudy.harness state [--raw]               # screen + policy_v0
python3 -m understudy.harness act '{"action":"end_turn"}' --why "one line"
python3 -m understudy.harness auto --max-steps 25         # walk mechanical screens
python3 -m understudy.harness give-card KLEEMOD-UNHEARD_CONFESSION --why "EB-52(a)"
GITS_UNDERSTUDY_CAPTURE=1 python3 -m understudy.harness frame --label salon-stage


# P1 soak: N unattended policy_v1 runs, setup/teardown automatic
python3 -m understudy.soak --runs 20 --report
python3 -m understudy.soak --runs 1 --no-setup            # attach to a live game
python3 -m understudy.soak --runs 1 --allow-hazard-events # EB-1: lift the register

# EB-142 targeted scenario: give a card, set the board, play it, assert
# (ATTENDED ONLY -- never in a soak)
python3 -m understudy.scenario check                      # parse only, no game
python3 -m understudy.scenario run understudy/scenarios/spark-gate-refusal.yaml \
    --why "EB-142: does the Spark gate show as unplayable"

# Reading output
python3 -m understudy.report [<stamp>]                    # morning report
python3 -m understudy.analyze understudy/logs/phase0-<seed>.jsonl

# EB-149 independent seat: OpenAI's Codex CLI as a design-BLIND grader
# (no game involved; needs a one-time `codex login`)
python3 -m understudy.seat check                          # path, version, login
python3 -m understudy.seat grade <turn-id> [--model M] [--grader-id ID]
python3 -m understudy.seat grade <turn-id> --dry-run      # prompt + argv only
python3 -m understudy.seat review <prompt-file> [--out F] # NOT blind

# EB-167/EB-168 blind play: ANY screen design-blind, and a seat that plays it
# (`observe`/`act` need no codex; `--raw-file` needs no game either)
python3 -m understudy.blindplay observe [--raw-file <state.json>]
python3 -m understudy.blindplay act 'play "Coral Guard"' [--dry-run]
python3 -m understudy.blindplay session [--model M] --max-actions 40

python3 -m pytest tier0/tests/test_understudy_*.py -q     # game never involved
```

Library level: `bridge.get_state/post/current_seed/set_speed/give_card`
(`bridge.py`); `policy_v0.counterfactual(state)`
(`policy_v0.py:459`); `policy_v1.decide(state, memo)` (`policy_v1.py:1022`);
`naming.describe(state, action)` / `hand_names` (`naming.py:114,237`);
`adapter.build_combat_state` / `deck_cards` (`adapter.py:198,292`);
`rng.policy_rng(label)` (`rng.py:38`); `scenario.load` /
`scenario.Runner(scenario, why, wire=bridge)` (`scenario.py`);
`soak.run_scripted(policy, stamp, ...)` — the setup/swap/teardown seam the
two probes and `scenario.py` share; `seat.guard(events, rollout, stderr)` /
`seat.fill_identity(raw, grader_id, model)` / `seat.build_prompt(packet_md,
sha)` (`seat.py`); `blindplay.observe(state)` / `blindplay.act(state,
command)` / `blindplay.Session(thread, wire=…).run()`, with
`blindplay.ScriptedWire` and `blindplay.ScriptedThread` as the shipped doubles
that run the whole loop without the game or codex (`blindplay.py`).

## 3. Key invariants

- **The seam: nothing in `tier0/`, `tier05/`, the drafter or any sheet is
  modified, monkeypatched, or read for anything but its public entry points.**
  policy_v1 adds ordering and gating around the sim's valuation functions,
  never a new way to price a card (`policy_v1.py:9-17`; `adapter.py:11-15`;
  R93's scope clause, `tier0/DECISIONS.md:3214-3216`).
- **policy_v0 invents nothing.** Where a decision class cannot be delegated
  faithfully it returns *no* counterfactual and says why; the three are
  `event`, `relic_select`, `crystal_sphere` and they are excluded from the M2
  denominator (`policy_v0.py:7-13,57-69`).
- **The game seed is recorded, never consumed.** `policy_rng` raises
  `GameSeedLeak` on any label that looks like a game seed (≥6 chars, alnum, no
  lowercase) — deliberately over-eager (`rng.py:38-51,63-72`). The understudy
  stream offset is 7e9, clear of tier05's 1e9/2e9/3e9 (`rng.py:24-31`).
- **Readiness is the `options` key on a `menu` state, never `GET /`.** The HTTP
  server answers ~20 s before the menu has buttons (`soak.py:224-250`;
  `bridge.py:12-14`).
- **Every failure to reach the bridge is a `BridgeError`,** including
  `ConnectionResetError` — an `OSError`, not a `URLError` (`bridge.py:54-63`).
- **The reversibility ledger is written BEFORE each change lands,** and
  teardown walks it in reverse with every step independently guarded
  (`soak.py:100-133,271-294`).
- **Counterfactual and choice are computed at the same state:** `act`
  recomputes policy_v0 before POSTing, and each step of a planned sequence gets
  its own (`harness.py:255-303`). **Names are resolved before the POST, once,
  in `decide`** — one frame later `card_index: 2` is a different card
  (`naming.py:14-17`; `policy_v1.py:1061-1065`; `soak.py:593,605`).
- **Log schema:** `soak-<stamp>-index.json`, `soak-<stamp>-run<NNN>.jsonl`
  (one JSON object per line, `record` discriminates: `run_begin`,
  `seed_read_back`, `decision`, `fight`, `defect`, `forced_default`,
  `game_over`, `run_end`), `reversibility-<stamp>.json` (`understudy/README.md`
  "Telemetry schema"; `soak.py:511-517`). Adding keys is free; **renaming or
  repurposing one is a shared-schema change** once Track B reads it
  (`soak.py:367-371`; `naming.py:31-33`).
- **A blind seat's blindness is PROVEN FROM THE TRANSCRIPT, never assumed
  from the sandbox** (`seat.py`). `--sandbox read-only` stops writing, not
  reading, and the `--json` stdout stream does not show tool-call attempts at
  all — measured, 0.150.1: a run in which the model attempted three shell
  commands emitted only `agent_message`. So `seat.guard` reads three sources
  — the stdout stream, codex's session rollout (which is why `--ephemeral` is
  NOT passed to `grade`), and stderr — as an ALLOWLIST at every layer, where
  an unknown event, item or rollout payload type REFUSES. A missing rollout
  refuses too: no evidence is not good evidence. The scratch `-C` root is an
  empty temp dir OUTSIDE the repo, because codex reads `AGENTS.md` from its
  working root.
- **Every blind-play observation is SCRUBBED, and the allowlist is what makes
  that possible** (`blindplay.py`). Each screen is copied field by field —
  printed faces, printed intents, meters that hold something, pile counts — and
  the finished structure AND the rendered page both go through
  `qa_packet.assert_blind`. A leak raises and the page is never shown. The one
  exemption is the wire's own screen NAME, passed one token at a time through
  `qa_packet.leaks(..., allow=…)` so a refusal can say what it refused; no
  other rule is ever exempt. Ids exist only long enough to build the POST.
- **An unknown screen is `TOOL-BLOCKED`, never a heuristic** (`blindplay.py`).
  An unrecognised `state_type`, an `overlay`, the crystal-sphere minigame and a
  registered EB-1 hazard event all render as `TOOL-BLOCKED: <state_type>` and
  stop the driver. There is no first-button fallback in the file:
  `soak._mechanical_action` has one because a soak must keep moving
  (`soak.py:1928`), and a blind tester must not.
- **The seat's identity fill has an exact limit:** `grader.id`,
  `grader.kind` and `grader.model` only — the three facts about the SEAT that
  a model cannot know. `turn_id`, `packet_sha256`, `designed_these_cards`,
  `chosen_line` and all four answers are byte-for-byte the model's,
  `form-raw.json` is kept beside the filled copy, and
  `test_understudy_seat` proves the wrapper cannot move a fourth field.
- **Encoding is declared on every text read/write** here, even though the
  repo's gate scans only `tier0`/`tier05`/`tools`
  (`tools/lint_text_encoding.py:43`). **Determinism:** every arm sorts, none
  rolls; ties break on offered index (`policy_v1.py:29-35,644-648`).

## 4. Rulings that shaped it

- **R93** (`tier0/DECISIONS.md:3179`) — all seven policy_v1 revisions approved
  unamended; #7 (resolved card NAMES) is a **P1 blocker**, no soak launches
  without it; #2's block-panic insight is routed to the pilot backlog and
  **`tier0/pilot/policy.py` is not changed for it**; all seven live in
  `understudy/`.
- **R94** (`:3220`) — Phase 2's default sampling tier amended from draft-picks
  to hard-state turn sampling (sequencing is 88% of decisions, 28% agreement on
  independent turn-openers). Thresholds are P2 work, not set.
- **R95** (`:3266`) — seeds are **read-back**, not chosen: the game generates,
  the harness records from `GET /api/v1/compendium`. Therefore **no P1 soak
  number is comparable to another build's**; the Custom-screen arm is mandatory
  before any build-vs-build number is quoted.
- **R96** (`:3302`) — the three Phase-0 observations about the SIM
  (`score_offer` = 0.0 on The Gallery Stirs; Vulnerable priced flat;
  `_reaction_value` has no defensive term) are **routed to their chartered
  streams, not acted on here** — which is why draft, shop and the
  deck-management overlays were left unrevised (`policy_v1.py:1069-1076`).
- **R97** (`:3339`) — 5a: readiness watches `options`, never the health
  endpoint. 5b: the leftover profile run may be abandoned freely, so the soak
  abandons ANY resumable run rather than negotiating (`soak.py:751-758`). 5d:
  the five adapter defects stay **measurement history, not open defects** —
  any future adapter against this wire meets the same five.
- **R87(1)** (`:2834,2852`) — the "pilot-limited floor" precedent Guardrail-7
  extends to bots.
- **R70** (`:2209`) — "latest is not a version"; the vendored bridge is pinned
  to commit `55e0648` (`vendor/STS2_MCP/PROVENANCE.md`; `soak.py:201`).
- **R68** (`:2122`) — single-source-of-truth discipline; Furina's plan→pilot
  mapping is read from tier05, not chosen here (`policy_v0.py:51-55`).
- **D4** (`:2446`) — instrument-visibility law: a quantitative claim used as
  rationale carries its measurement or is marked UNMEASURED. Hence M1 reported
  as *marginal* chars/decision with its omitted denominator stated
  (`harness.py:27-41`), and Guardrail-7 restated in every report
  (`report.py:33-39`).

## 5. Traps

- **`policy_v0.py` is FROZEN.** It is one arm of a published measurement;
  editing it retroactively moves a quoted number. Pinned red by
  `tier0/tests/test_understudy_policy_v1.py:377-390` (a 0-cost Ethereal card
  must keep having *no* privilege there).
- **The adapter's enumerated fidelity losses are the map, not a TODO list**
  (`adapter.py:20-50`): base-game cards get text-derived stubs and are
  systematically undervalued; only the statuses tier0 names are carried; auras
  are read only when the wire reports them; intent ramps and multi-phase bosses
  are structurally invisible (incoming is this-turn-accurate, future-turn-blind);
  relic hooks, pile ORDER, exhaust contents and orbs are not carried at all.
- **The five wire facts that cost sessions** (R97/5d): enemies live under
  `battle` (`adapter.py:272-281`); intent damage is only in the `label` string
  (`adapter.py:165-180`); the hand's field is `target_type`, not `target`
  (`policy_v0.py:134-137`); the aura is `"Cryo Aura"`, not `"cryo"`
  (`adapter.py:183-195`); the label already folds in the attacker's Strength, so
  **all** enemy powers are dropped (`adapter.py:229-245`).
- **Three more, and each cost a blind RUN** (`EB-262`/`EB-263`/`EB-259`, all
  found on `klee-overhaul-r1`). A SHOP item carries its printed name under its
  category's own key — `card_name` / `relic_name` / `potion_name`, never
  `name` — beside `price`, `is_stocked` (false is SOLD) and `can_afford`
  (`McpMod.StateBuilder.cs:1636`). An opened CHEST's relics are
  `treasure.relics` and a relic-select screen's are `relic_select.relics`;
  neither is a top-level key. And an EVENT room has no proceed button at all —
  `ExecuteProceed` walks rewards, rest, both merchants and the treasure room
  and stops (`McpMod.Actions.cs:600-663`) — so leaving an event is
  `choose_event_option` on the option the screen prints *Proceed*.
- **`deckwatch` snapshots are accepted only at round 1 or when strictly larger** —
  otherwise the victory-screen union (3 cards) replaces the real deck (13)
  (`deckwatch.py:45-54`). Out of combat the wire carries no deck, so the draft
  counterfactual reads a snapshot as old as the last fight
  (`deckwatch.py:13-18`; `adapter.py:314-322`).
- **`card_select` is three screens wearing one name** (upgrade/remove,
  Spotlight choose, multi-select grid). `select_card` **toggles**;
  `preview_showing` is not a reliable landed-selection signal; a multi-select
  screen needs a *different* card each visit; selection state is per-visit and
  cleared on leaving the screen (`policy_v1.py:108-117,978-984,1031-1037`).
  **On the wire only** — since EB-14 (2026-08-12) the mod
  writes the same `selectors` rows from inside the game and spells the screen
  with its concrete class name, because that side can tell the three apart
  (`klee-mod/KleeCode/Diagnostics/SelectionTelemetry.cs`;
  `understudy/README.md` §"Telemetry schema" carries the four declared limits
  on the human feed's column).
- **Two dials live in `policy_v1` and nowhere else** —
  `BLOCK_MATTERS_FRACTION`, `COMPANION_SHARE_FOR_GUEST_CAST`. Bot-policy dials,
  not balance constants; they must not migrate to `tier0/constants.py`, and are
  logged per run (`policy_v1.py:70-90`; `soak.py:701-707`).
- **`end_turn` IS ASYNCHRONOUS, and the frame it leaves behind looks playable**
  (`EB-175`). `ExecuteEndTurn` calls `PlayerCmd.EndTurn` and answers
  `ok Ending turn` at once; a GET 55 ms later still reads `state_type:
  monster`, `turn: player` and the round UNCHANGED, with the hand already
  discarded to zero and energy still full. The one field that tells the truth
  is `battle.is_play_phase`, which is **false** on that frame and true again
  a quarter-second later on the real next round. `blindplay.transient` counts
  it as a transition beside `unknown` and a missing `state_type`, and
  `blindplay.settle` rides all three out on every LIVE read (the driver's and
  the CLI's) and on no saved one. Neither ends a turn on anybody's behalf.
- **A stall is a small cycle, not only a frozen frame:** at most 2 distinct
  fingerprints across 12 posted actions (`soak.py:79-87,569-587`). A mechanical
  action that changes nothing is likewise not mechanical (`soak.py:926-949`).
- **A dead wire is TWO failures, and `bridge_unreachable` is only one of them.**
  A process that is alive and spinning (EB-1) files `unresponsive_spin` instead,
  on a log-growth / message-pump probe (`hangwatch.py`); `bridge_unreachable` is
  harness-side, so filing a spin under it makes the instrument blame its own
  wire for a build defect it just caught. Neither `unresponsive_spin` nor
  `hazard_event` is in `_HARNESS_SIDE` — both are the soak working.
- **`soak.HAZARD_EVENTS` is a register of screens the driver refuses to drive**
  (`PUNCH_OFF`, EB-1). The hazard is room ENTRY, so the guard cannot prevent the
  first hang and does not try: it prevents the second, by stopping the run so
  the restart path's `abandon_run` clears the poisoned save. The map on the wire
  carries a node's `type` only, never which event, so avoiding the room is not
  available at all. `--allow-hazard-events` lifts it.
- **`frames.py` is OFF unless `GITS_UNDERSTUDY_CAPTURE=1`** (env-only, same
  precedent as `GITS_ILSPY_TREE`), captures the game WINDOW and never the
  desktop, writes to the gitignored `understudy/logs/frames/`, and stamps
  `frames.GUARDRAIL` on every manifest row: a frame is MATERIAL for a person,
  and no look / legibility / readability / fun claim may be derived from one
  here. The soak takes no pictures.
- **`give-card` is on the ATTENDED harness and must stay there.** The soak's
  claim is that its runs are generated runs; the absence is pinned by
  `tier0/tests/test_understudy_give_card.py`. Every grant carries the sentence
  saying the run is no longer comparable to any other (`bridge.GRANT_GUARDRAIL`).
- **`scenario.py` is the same door widened, under the same rule** (EB-142). It
  grants a card AND writes a board (`/api/v1/gits/debug_state`:
  `set_resource`, `set_energy`, `set_hp`, `set_block`, `set_power` (EB-146)
  and `clear_hand` (EB-165), each through the game's own mutator, `why`
  REQUIRED and logged), so a
  scenario run is comparable to nothing. Attendedness is pinned by
  `tier0/tests/test_understudy_scenario.py`, which walks `soak.py`'s imports
  with the AST rather than grepping — `soak.py` NAMES `scenario.py` in the
  comment explaining why `run_scripted` was factored out, and a substring pin
  would read that explanation as the violation it is explaining. **It asserts
  numbers only** — HP, Block, power stacks, resource amounts, `prompt`,
  `can_play`, `unplayable_reason`, printed text — and a failed assert is a
  DEFECT, never a design finding.
- **A scenario posts its OWN actions, unlike the two probes.**
  `soak._mechanical_action` claims `hand_select` BEFORE `policy_v1.decide` is
  asked and answers it with card 0 + confirm. A scenario whose question is
  WHICH card gets exhausted (`the_tide_remembers` scales off the exhausted
  card's cost) cannot live with that, so the runner executes the whole scenario
  inline at the first combat screen and hands combat back afterwards. Stated
  cost: the driver's watchdog and per-action telemetry do not see those posts.
- **Sparks are a POWER and not a resource, which is why there are two write
  ops.** `SparkPower` (`klee-mod/KleeCode/Powers/SparkPower.cs`) is not one of
  BaseLib's registered CustomResources — that registry reaches Fanfare, Encore,
  Charge, the two Bursts and the three Spotlight meters and stops there. EB-146
  added **`set_power`**, which resolves out of `ModelDb.AllPowers` by the wire's
  own `power.Id.Entry` (`SPARK_POWER`) or the printed Title and writes through
  `PowerCmd.Apply` / `ModifyAmount` / `Remove` with **`applier: null`**
  (`SparkPower.Spend`'s precedent: a bookkeeping write stays out of the
  `ModifyPowerAmountGiven` chain). The receive chain still runs, so Artifact
  still eats a debuff, and the response reports the amount REQUESTED with
  `queued: true` — the landed number is read off the next state.
  `set-power-sparks.yaml` exercises it; the two Klee scenarios that earn their
  Sparks by playing Sparkly Treasure were deliberately NOT converted, because a
  scenario whose subject is the RULE is more honest earning the bank.
- **`set_power` writes `Amount`; the wire prints `DisplayAmount`.** Equal for
  most powers, deliberately unequal for `BombPower` (`Amount` = bomb count,
  badge = total pending detonation damage, ruled 2026-07-20). An
  `expect: {power: ...}` reads the badge — which is why
  `powder-charge-detonate-bonus.yaml` asserts a Pop! bomb at **5**, and why its
  first live run's failure was the FILE and not the game.
- **The count is ALL `set_power` writes.** A power carrying a payload beside
  its stack count is not set by setting the count: `BombPower`'s per-bomb
  damages live in a private list only `BombPower.Place` grows, so
  `set_power BOMB_POWER 2` is two bombs that display nothing and detonate for
  nothing. Plain counters and durations only (Spark, Vulnerable, Weak,
  Strength); for a payload power, play the card that places it. The op cannot
  detect the difference and does not pretend to — nothing in `PowerModel`
  declares "I keep state the stack count does not describe".
- **`clear_hand` empties a hand without discarding it** (EB-165). The game
  deals its own opening hand over the granted one, so a turn declaring
  `exact_hand: true` opens its staging with this op and `export_packet`
  refuses a packet whose live hand is not the declared multiset. The cards go
  to the BOTTOM of the draw pile through `CardPileCmd.Add` — the pile move
  underneath `CardCmd.Discard` and `CardCmd.Exhaust`, so no on-discard or
  on-exhaust trigger fires and no history row is written. What still fires is
  `Hook.AfterCardChangedPiles`, which every pile move in the game runs; there
  is no route out of hand beneath it, and a setup verb that punched through
  would be writing a board the game cannot produce. Draw rather than discard
  because a discard pile is read by cards; bottom rather than top so a draw
  played during the turn pulls what the seed would have dealt next. It takes
  no `who` and no `amount`, and `scenario.py` waits for the hand to actually
  empty rather than trusting the queued answer — the next step is normally a
  grant.
- **A board write resolves its creature selector; it did not always.**
  `set_hp` / `set_block` / `set_power` take the `play` target's vocabulary (an
  entity id, a display name, `first` / `lowest_hp` / `highest_hp`) and
  `scenario.py` resolves it against the latest GET before posting, because the
  bridge knows only entity ids and `"player"`. The first live run posted the
  literal string and got `No living creature named 'first'` (EB-146). The step
  record carries the selector AND the resolved id. `set_resource` /
  `set_energy` take no `who` at all and the parser refuses one: the bridge
  writes both to the player's combat state and ignores the field.
- **Ordering traps in the driver:** the character stays in `options` after
  being picked, so pick once then `confirm` or loop forever
  (`soak.py:810-820`); a play the bridge rejected is not re-offered this turn
  (`soak.py:614-620`; `policy_v1.py:118-127`); a defect run is not trusted to
  leave clean state, so the game is relaunched (`soak.py:1156-1168`); two
  harness-side defects of the same shape halt the soak
  (`soak.py:1144-1155,1186-1187`).
- **`understudy/logs/soak/` is gitignored** (per-machine output);
  `logs/phase0-SSRWEGLNRG.jsonl` is committed and is the whole surviving
  Phase-0 measurement — R97/5b says the live save it came from may be deleted.
- **No number from here is balance evidence** (Guardrail-7), and **no fun,
  legibility or readability claim, ever** — a JSON-state agent cannot see the
  screen (`understudy/README.md:27-38`; `soak.py:13-27`; `report.py:33-39`).
  The report prints defects first, outliers second, curves third *on purpose*
  (`report.py:6-12`).

## 6. Reading order

1. `understudy/README.md` — the map, the two rules, and the full telemetry schema.
2. `understudy/adapter.py:1-50` — what crosses the wire faithfully and what does not.
3. `understudy/policy_v0.py:1-35,459-481` — the delegation commitment and the dispatch.
4. `understudy/policy_v1.py:1-130,1022-1079` — the seven revisions, the dials, the Memo, `decide`.
5. `understudy/soak.py:1-100,463-600` — Guardrail-7, the ledger, the watchdog.
6. `tier0/DECISIONS.md` R93–R97 (`:3179-3371`) — the rulings, in one sitting.
