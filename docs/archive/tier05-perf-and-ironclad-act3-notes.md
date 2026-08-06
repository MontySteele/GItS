> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/tier05-perf-and-ironclad-act3-notes.md` — new path: `docs/archive/tier05-perf-and-ironclad-act3-notes.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Tier 0.5: runtime pass + the Ironclad act-3 diagnosis (2026-07-24)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Two asks, one session:

1. Why is the Ironclad anchor's act-3 winrate so low — is the sim unusually
   punishing, or is the pilot bad?
2. The sims take minutes. Can they be faster?

(2) is **shipped** and is a pure speedup — every measurement in the repo is
byte-identical before and after. (1) shipped one bug fix and one coverage
hole, and **weakened nothing**: the difficulty claim an early draft of this
document made did not survive its own re-measurement, and §1.3 keeps both the
retraction and the method error that produced it on the record.

---

## Part 1 — the act-3 diagnosis

### 1.0 Verdict

**The pilot is not the problem. The world is** — for three separable
reasons, in descending order of how load-bearing they are:

| # | cause | kind |
|---|---|---|
| A | `test_subject`'s phase-2 attack ramps from the wrong turn, opening at **84 damage/turn instead of the authored 30** | **BUG** — fixed |
| B | ~~the rosters are 20–30% over-tuned~~ **RETRACTED (§1.3)**. They are not. The median encounter is 99–100% winnable for act-appropriate decks; difficulty is **bimodal**, concentrated in three bosses. Runs die to the **HP ledger** — the anchor's act 1 costs ~92 HP and returns ~44 against an 80 HP pool | measurement error, corrected |
| C | `ref_ironclad` has **6 draftable cards, zero rares, and had zero upgrade coverage**; it cannot cash any of the §10.8.1 fixes | instrument scope — upgrades fixed |

**No enemy was weakened.** An early draft of this document recommended a
per-act difficulty multiplier; §1.3.1 is why that was wrong and what the
correct method showed instead.

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

Instrument: `tools/encounter_audit.py` — every encounter replayed at full HP
against the real decks that reach that act. (`tools/archive/roster_scale_gap.py` is
the fixed-deck variant; it compares a roster against the frozen tier 0
battery, and must NOT be used to ask whether a roster is over-tuned — see
§1.3.1.)

### 1.3 Cause B — RETRACTED, and what replaced it

**This section originally claimed the act rosters were 20–30% over-tuned and
recommended a per-act enemy multiplier. That was wrong, the method was the
reason, and the correction is more useful than the claim was.**

#### 1.3.1 The methodology error

The original evidence ran a FIXED deck — `starter`, and `starter` + the
10-card package — against every act's roster, and reported that the package
deck wins 0% against both act-2 bosses and everything in act 3. What that
actually measured is that **an act-1 deck cannot beat act-3 content**, which
is not a finding; it is the premise of a progression system.

Re-run with **act-appropriate decks** — the real decks and relics of runs that
reached each act, at full HP — the picture inverts. `tools/encounter_audit.py`,
300 runs/character, seed 11, realistic:

| act | median encounter | the exceptions |
|---|---|---|
| 1 | **100%** | `vantom` 82%, `bygone_effigy` 92%, `lagavulin` 94% |
| 2 | **100%** | `knowledge_demon` 31%, `kaiser_crab` 39% — *both bosses*; every other encounter 98–100% |
| 3 | **99%** | `test_subject` 0.4%, `devoted_sculptor` 56%, `knight_gang` 56%, `aeonglass` 71% |

Same act-3 elites that read 0% under the fixed-deck method read **83–100%**
for the decks that actually reach them. The rosters are fine. Difficulty is
**bimodal**: nearly everything is free, and it is concentrated in a handful of
bosses.

A global multiplier is therefore exactly the wrong shape — it would make an
already-free roster freer in order to rescue three encounters. Retracted. The
`ACT_DIFFICULTY_SCALE` dial built for it was reverted the same day rather than
left inert, because a knob whose stated rationale has been falsified is worse
than no knob.

#### 1.3.2 What actually kills runs: the HP ledger

If every fight is winnable at full HP but only 43% of anchor runs clear act 1,
the runs are dying to attrition. They are:

| character | N cost | E cost | B cost | rest returns | act-1 ledger |
|---|---|---|---|---|---|
| ref_ironclad (80 HP) | 6 | **34** | 30 | 22 | 4N + 2E cost ~92, 2 rests return ~44 → **net −48** |
| klee (62 HP) | 7 | 20 | 20 | 19 | ~68 spent, ~38 returned → net −30 |
| furina (60 HP) | 4 | 22 | 16 | 18 | ~60 spent, ~36 returned → net −24 |

Median HP loss per fight, act 1. The anchor's act-1 template costs more HP
than it has, and the two rests return under half of it. The consequence is
visible node by node:

| node | arrive at | deaths |
|---|---|---|
| 4E (first elite) | 80/80 | 12% |
| 8E (second elite) | **38/80** | **37%** |
| 10B (boss) | 51/80 | 20% |

The first elite is faced at full HP and kills 12%. The *same class of fight*
faced at 38/80 kills 37%. Nothing about the elite changed — the HP economy
did. That is the whole act-1 funnel.

#### 1.3.3 Where that points (all still red-pen)

None of these weaken an enemy:

1. **The template's heal economy vs real StS.** We run 11 nodes with **2
   rests, no ? rooms, no events, and 2 mandatory elites with no pathing
   agency**. Real StS act 1 is ~15 nodes where the player *chooses* whether to
   take an elite at all and has more heal opportunities. We have strictly more
   forced elites and strictly fewer heal sources than the game we are
   modelling. §10.8.1 already lists the pathing half as an honesty item; the
   heal half is new here.
   Caveat from the arms: naively cutting to one elite per act raises act-1
   clears 37% → 65% but *lowers* overall winrate to 1.2%, because elites are
   also the reward economy. Agency, not deletion.
2. **The three genuinely out-of-scale bosses.** `test_subject`,
   `knowledge_demon`, `kaiser_crab`. Each should be audited against its own
   §10.9 skip list the way the Multi-Claw ramp was — `test_subject`'s sheet
   already says "P3 Intangible skipped (the 300 bar carries the weight)",
   i.e. HP was inflated to stand in for a skipped mechanic, which is the
   fake-it-quietly pattern the house rules forbid.
3. **The anchor's per-fight cost is the outlier, not the roster's damage.** An
   elite costs the anchor 34 HP (43% of its pool) against Klee's 20 (32%) and
   Furina's 22 (37%). That is the six-card, zero-rare pool of §1.4 showing up
   as HP, and it is an argument about the instrument, not about the enemies.

#### 1.3.4 Corrections to earlier claims in this document

- "The package deck wins 0% against act-2/3 content" — true but **misleading**;
  it is an act-1 deck. Act-appropriate decks win 83–100% on those same fights.
- "The anchor sees Prismatic Gem in ~20% of runs" — **wrong**, repeated from
  §10.8.1's archived measurement of an older world without re-measuring.
  Measured today: **44–50%** of runs reaching act 2 already hold it (plus
  Happy Flower, Lantern and Hot Cocoa on top). The proposal to guarantee an
  energy boon every act boundary was therefore a straight buff, not a
  correction, and is dropped.
- "The calibration chain is broken" — the *chain* observation stands (cards
  are calibrated against the frozen battery, rosters are raw StS2, the
  compensator is dead code). The *conclusion* that the rosters are
  consequently over-tuned does not survive §1.3.1.

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

### 1.5 What shipped from all this

| change | kind | status |
|---|---|---|
| phase-relative `ramp` + `ramp_per_use` (§1.2) | bug | **shipped** |
| `ref_ironclad` upgrade sheet (§1.5.1) | coverage hole | **shipped** |
| `tools/pilot_error_audit.py`, `tools/encounter_audit.py` | instruments | **shipped** |
| per-act enemy difficulty dial | calibration | **retracted** (§1.3.1) |
| guaranteed act-boundary energy boon | design | **dropped** (§1.3.4) |
| unlock the rest smith band | calibration | **not shipped** — measured trap: upgrades rise, act-1 clears fall everywhere (Klee 82% → 68%) because both template rests sit directly before an elite or boss |

#### 1.5.1 The anchor's missing upgrade axis (SHIPPED)

`ref_ironclad` had **0/6 draft pool and 0/10 starter** cards upgradable. Klee
and Furina are 71/71 + 10/10; Kokomi 31/31 + 10/10. So rest-site smithing,
Sand Castle, Yummy Cookie, War Paint and Whetstone were **all dead branches on
the one character the world is calibrated against** — 0 upgraded cards and 0
smiths out of 683 rests in 300 runs, while every character it anchors gained
1–2 upgrades a run.

`docs/ref-ironclad-upgrades.yaml`, real base-game numbers (Strike+ 6→9,
Defend+ 5→8, Bash+ 8→10 with 3 Vulnerable, Inflame+ 2→3 Str, Shrug It Off+
8→11, Cleave+ 8→11, Metallicize+ 3→4, Heavy Blade+ +4, Pommel Strike+ draw 2).
The tier 0 battery builds from plain deck ids and never upgrades, so the
frozen scorecard and the anchor lock are untouched. Anchor act-1 clear
**36.7% → 42.8%**.

#### 1.5.2 Open, in order

1. Audit the three out-of-scale bosses against their §10.9 skip lists
   (§1.3.3 item 2). This is the same class of work as the Multi-Claw ramp and
   it is where the difficulty actually lives.
2. Decide the template's heal/elite economy deliberately (§1.3.3 item 1) —
   a structural question about node composition and pathing agency, not a
   difficulty dial.
3. Re-instrument on `real_ironclad`, not `ref_ironclad`, before reading any
   "can an average player clear this" claim. Needs `game_ref/` rebuilt.

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
