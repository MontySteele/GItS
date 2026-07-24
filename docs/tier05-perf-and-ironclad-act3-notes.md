# Tier 0.5: runtime pass + the Ironclad act-3 diagnosis (2026-07-24)

Two asks, one session:

1. Why is the Ironclad anchor's act-3 winrate so low — is the sim unusually
   punishing, or is the pilot bad?
2. The sims take minutes. Can they be faster?

(2) is **shipped** and is a pure speedup — every measurement in the repo is
byte-identical before and after. (1) is a **diagnosis only**: it lands on
one outright bug and two calibration decisions, and calibration is red-pen
by standing convention (§10.8), so nothing here was tuned unilaterally.

---

## Part 1 — the act-3 diagnosis

### 1.0 Verdict

**The pilot is not the problem. The world is** — for three separable
reasons, in descending order of how load-bearing they are:

| # | cause | kind |
|---|---|---|
| A | `test_subject`'s phase-2 attack ramps from the wrong turn, opening at **84 damage/turn instead of the authored 30** | **BUG** |
| B | the §4 roster swap to raw StS2 statlines dropped `PROGRESSION_GAP_COMPENSATOR` and nothing replaced it — the two sides of every fight are now on different scales | calibration (red-pen) |
| C | `ref_ironclad` has **6 draftable cards and zero rares**; it cannot cash any of the §10.8.1 fixes | instrument scope |

All numbers below: `ref_ironclad`, seed 11, `--realistic`, current HEAD.
Baseline for reference: **2.6% win at 500 runs**, funnel 38% / 13% / 3%.

### 1.1 The pilot is doing its job (300 runs, 12 183 player turns)

An instrument aimed at the decision that actually kills runs — ending a turn
with damage incoming that block still in hand would have absorbed:

| measure | value |
|---|---|
| turns that took damage | 7 321 (60.1%) |
| ...of those, turns ending with a PLAYABLE block card unplayed | **0** |
| HP the unplayed block would have saved | **0** of 63 016 HP lost |
| spare energy at end of turn | 0.05 / turn |
| spec `pilot_regret` | 4 205 / 37 883 plays (11.1%) |

The pilot spends essentially all of its energy and never sits on block while
being hit. The 11.1% `pilot_regret` rate is the scorer preferring scaling and
tempo over raw immediate value (playing Inflame over a Strike registers as
"regret" by that metric) — it is not evidence of misplay, and `pilot_regret`
cannot see the errors a greedy pilot would actually make (sequencing, saving
block for the turn after). It remains a weak instrument; it is just not the
one pointing at the problem here.

Instrument: `tools/pilot_error_audit.py` (committed — it is the
instrument `pilot_regret` was supposed to be, and the next character will
want it too).

### 1.2 Cause A — a real bug: `test_subject`'s phase-2 ramp (BUG, act3_pool.yaml:234)

`combat._enemy_turn` computes a ramping intent as

```python
amount = intent["amount"] + intent.get("ramp", 0) * max(0, state.turn - intent.get("ramp_after", 0))
```

`state.turn` is the **global combat turn**, and `ramp_after` defaults to 0.
That is right for `byrdonis` and the frozen `punisher`, whose ramps are meant
to start at combat start. It is wrong for an intent that first appears in a
boss's **second phase**: Multi-Claw has already been "ramping" through all of
phase 1 before it is ever used.

`test_subject` is the only ramping intent inside a `phases:` block in the
whole content tree, so this is its blast radius entirely. The sheet's own
comment states the intent:

> P2's grow-a-hit-per-turn Multi-Claw is ramp 3 per hit (30 -> 39 -> 48 vs
> real 30 -> 40 -> 50)

Measured (400 HP dummy player, so the curve is visible rather than fatal):

| combat turn | raw enemy damage | |
|---|---|---|
| 1–5 | 14–20 | phase 1 |
| 6 | **84** | phase 2 opens (authored: 30) |
| 8 | **102** | |
| 10 | **120** | |
| 12 | **138** | |

Against 80 max HP and a measured block ceiling of ~17–21, that is not a
fight. Isolated, at FULL HP, with the real decks and relics of runs that
actually reached act 3 (median 29 cards, 12 relics):

| act-3 encounter | win |
|---|---|
| boss `test_subject` | **0.0%** |
| boss `aeonglass` | 81.1% |
| elite `knight_gang` | 51.4% |
| easy `devoted_sculptor` | 49.3% |
| everything else | 80–100% |

`test_subject` is 1 of 2 bosses in the act-3 pool, drawn 50/50 per run — so
roughly **half of every run that survives to the final boss loses to a boss
no line of play can beat**. Observed at 600 runs: 74 reached act 3, 24
reached the final boss, 13 won (54%) — right where a coin-flip between an
unwinnable boss and an 81% boss predicts.

**SHIPPED 2026-07-24** (user ruling). Two parts:

- Engine: `ramp` now counts from the turn the enemy entered its **current
  phase** (`Enemy.phase_start_turn`, stamped by `_settle_phases`). Unphased
  enemies keep `phase_start_turn = 0`, i.e. combat start, so Byrdonis, the
  frozen PUNISHER and every single-bar roster enemy are bit-identical.
- Content: Multi-Claw moves from `ramp: 3` to a new `ramp_per_use: 3`. The
  real move gains a **hit each time it is taken**, which a turn ramp cannot
  express — under a turn ramp the value depends on how many non-attack beats
  sit between two uses, so adding a beat silently retunes the enemy. It now
  delivers the sheet's authored 30 → 39 → 48 exactly.

Both ramp shapes are read through one helper (`Enemy.ramped_amount`) used by
the enemy turn **and** the pilot's incoming-damage estimate; those were
duplicated formulas, and a pilot that mispredicts incoming damage blocks
against the wrong number.

Blast radius, verified by digest: runs at `--acts 1` and `--acts 2` are
**byte-identical** before and after; only act 3 moves.

**It did not rescue act 3, and that is the finding.** Against the real decks
of act-3 arrivals, `test_subject` goes 0.0% → **0.7%**; run winrate is flat
inside noise (2.6% → 2.2% at 600 runs). Those decks chew a median of **47% of
its 600 HP** before dying, in a 9-turn fight. The ramp was a real bug on top
of a scale problem, not the scale problem — which is §1.3. For contrast the
other act-3 boss, `aeonglass`, is 512 HP but spends 3 of its 5 beats on
block/inject/buff: real decks take it to **100% of its HP pool** over 15
turns and win 81%. Damage-per-beat density, not HP, is what separates them.

Instruments: `tools/roster_scale_gap.py` (committed; the standing
battery-vs-roster scale check) and `scratchpad/act3_arrivals.py` (one-shot:
replays act-3 encounters against the real decks of act-3 arrivals).

### 1.3 Cause B — the calibration chain is broken

The card sheets are still calibrated against the **frozen tier 0 battery**
(`PUNISHER` 115 HP / atk 9 ramp +2 is pinned at "starter wins ~50–60%";
measured 55.3%). The tier 0.5 act rosters were swapped to **raw StS2
statlines** with `PROGRESSION_GAP_COMPENSATOR` explicitly not carried over
(`acts.py` header, `model.build_node_encounter`) — that constant is now dead
code, and it was originally grid-searched *specifically* so the anchor's run
completion landed at 45%±10 (frozen at 47.9%).

Same decks, 300 fights each, full HP, no run-layer power:

| deck | battery `punisher` | battery `tank_boss` | a1 `bygone_effigy` | a2 bosses | a3 elites | a3 bosses |
|---|---|---|---|---|---|---|
| starter (the 3.0 anchor) | **55.3%** | 0.3% | 1.0% | 0% | 0% | 0% |
| starter + 10-card package | **100%** | **98.3%** | 93.3% | **0%** | **0%** | **0%** |

The package deck — the deck that beats the frozen tank boss 98.3% of the
time — wins **zero** fights against either act-2 boss, all three act-3
elites, and both act-3 bosses, starting at full HP with a fresh deck. That is
not attrition and it is not the pilot; those fights are outside the scale the
cards were built against.

Counterfactual arms, 400 runs each, same seeds:

| arm | win | cleared a1 / a2 / a3 |
|---|---|---|
| baseline | 3.0% | 36.8 / 13.2 / 3.0 |
| 1 elite per act (was 2) | 1.2% | 65.2 / 13.0 / 1.2 |
| restore elite compensator ×0.8 | 9.2% | 93.0 / 36.2 / 9.2 |
| restore boss compensator ×0.7 | 7.2% | 48.5 / 33.5 / 7.2 |
| **restore both (the pre-§4 world)** | **18.5%** | 97.5 / 77.8 / 18.5 |
| all enemies ×0.9 | 14.0% | 85.5 / 47.8 / 14.0 |
| all enemies ×0.8 | 30.8% | 99.0 / 78.8 / 30.8 |
| all enemies ×0.7 | 43.8% | 100 / 94.2 / 43.8 |

Restoring the dropped compensator alone reproduces §10.8.1's "all four
proxies" figure (18.0%) — a plausible dumb-pilot A0 shape — which is a good
sign that it is the same missing lever seen from a different angle.

Note the **1-elite arm is a trap**: it nearly doubles act-1 clears (36.8% →
65.2%) and *lowers* the winrate, because elites are also the reward economy —
fewer elites means fewer relics and a more bloated deck at the act-2 boss.
"Forced 2 elites/act with no pathing agency" is on §10.8.1's honesty list,
but it is not a lever that can be pulled on its own.

Arms archived in `scratchpad/arms.py`.

### 1.4 Cause C — the anchor cannot draft

`rewards.character_pool("ref_ironclad")` is **6 cards**: 4 common, 2
uncommon, **0 rare**. Klee and Furina get 71 each. Consequences:

- Every reward screen for 30 screens offers from the same 6 cards, so the
  deck is starter + duplicates and the "final deck size 19.5" is mostly
  padding.
- §10.8.1's headline fix — forced Rare cards at act boundaries — is a
  **no-op** for this character: `roll_rewards` walks the rare→uncommon→common
  ladder because the tier is empty. Same for the Ancient rare pool's effect
  on his draft.
- That is exactly why the fidelity fixes moved `real_ironclad` (the real
  75-card pool) 9× and barely moved anyone else. **`real_ironclad` needs
  `game_ref/`, which is gitignored and absent from a fresh clone** — so on
  this machine "the Ironclad package" is the 6-card anchor, not the base-game
  character. Any statement of the form "an average player clears the base
  game" should be tested against `real_ironclad`, and cannot be tested here
  at all without rebuilding `game_ref/`.

### 1.5 Recommended order of work (all red-pen)

1. Fix the phase-relative ramp (bug; smallest change, largest correctness
   gain, and it un-breaks half of all act-3 boss draws).
2. Decide the roster-vs-cards scale question deliberately: either re-introduce
   a per-tier compensator for acts 2–3, or rescale the card sheets. The arms
   above size both.
3. Re-instrument on `real_ironclad`, not `ref_ironclad`, before reading any
   "can an average player clear this" claim.

---

## Part 2 — the runtime pass (SHIPPED)

Determinism was the acceptance test throughout: a 165-run, 7-case digest over
every field of `RunResult` (all four characters, both policies, bare and
realistic, 1 and 3 acts) is **identical before and after every commit in this
pass**, and the frozen scorecard/anchor tests still pass unchanged.

| workload | before | after (serial) | after (`--jobs 4`) |
|---|---|---|---|
| `ref_ironclad` 500 runs, realistic | 14.5 s | 7.2 s | **2.4 s** |
| `klee/demolition` 300 runs, realistic | 13.6 s | 7.0 s | **2.2 s** |
| `furina/salon` 300 runs, realistic | 18.8 s | 11.2 s | **3.7 s** |
| `python -m pytest -q` (641 tests) | 200 s | **97 s** | — |

### What changed

1. **`Card.__deepcopy__`** (`engine/state.py`). Card copying was **~48% of
   total runtime**: `loader.get_card` deep-copies on every call and generic
   `copy.deepcopy` walked all ~40 fields through the memo machinery when only
   seven are containers. Hand-rolled copy, pinned field-for-field against
   `copy.deepcopy` in `test_card_copy.py`.
2. **`loader._card_prototype` + `loader.peek_card`**. The upgraded form of a
   card was rebuilt on every `get_card("x+")`; it is a pure function of the
   id, so it is memoized. `peek_card` is the new read-only door: the run
   layer re-derived `[get_card(cid) for cid in deck_ids]` three times per
   reward screen purely to *score* the deck, which was ~70% of all card
   copies in a run. `loader.reset_caches()` is now the one place that drops
   every memoized view (the prototype cache is derived from the card index,
   so clearing one without the other would serve stale prototypes).
3. **Pilot valuation dedupe** (`pilot/policy.py`). The lethal check, the
   scorer and the regret log each independently recomputed
   `_expected_damage` / `_block_value` / `_incoming_damage` for the same
   cards against a state that cannot change mid-decision. Computed once per
   decision and shared. Also: `_spotlight_value` and `_charge_value` are
   skipped when their weight is 0 — every pilot but Furina's zeroes the
   first, every pilot but Kokomi's zeroes the second, and scanning the hand
   for Companions was the most-called thing in a non-Furina fight.
4. **`run_many(jobs=N)` + `--jobs/-j`** (`tier05/model.py`, `runner.py`,
   `ab.py`). Run *i* is a pure function of `seed + i`, so the batch splits
   into contiguous blocks across processes and concatenates back in index
   order. `test_parallel_runs.py` pins that an N-job list is
   element-for-element identical to the serial one. `jobs=0` means one worker
   per CPU. A caller passing its own policy closure (the `exp_*` scripts)
   falls back to serial with a warning rather than failing to pickle.
5. **One anchor battery per `score_character`** (`harness/runner.py`).
   `score_config` re-ran the full `ref_ironclad` baseline battery once per
   deck scored; it is a deterministic function of `(fights, seed)`, so it is
   computed once and handed in. This is most of the test-suite saving.

### Not done

- `pytest-xdist` would cut the suite again (it is dominated by two ~45 s
  battery re-runs) but adds a dependency; say the word.
- The remaining profile is flat — no single call site above ~5%. Further
  gains want either PyPy or a different combat-state representation, neither
  of which is worth it at these times.
