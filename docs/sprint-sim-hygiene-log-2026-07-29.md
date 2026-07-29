# Sprint log — the sim-hygiene pass (2026-07-29)

Delegated Python-sim pass, four tasks, one of them a version bump. No `klee-mod/`
file, no yaml sheet value, no ratified band, and no `DECISIONS.md` entry was
touched — the ledger entry for the repricing is the user's to write, because
every number below is **PROPOSED**.

**World at open:** `RT7 / D12 / P3 / C4`. **World at close:** `RT7 / D13 / P3 / C4`.
The bump is Task 1's; the other three tasks are behaviour-identical by
construction and were verified so before the bump landed.

**Suite:** `python -m pytest -q` from the repo root — **1412 passed, 1 skipped**
(1410 before the pass; +2 are the op-parity green/red pair).

---

## Task 1 — the drafter op repricing (DRAFTER_VERSION 12 → 13)

### What was wrong

`tier05/draft.py::_static_power` is the offer-time power estimate: what a card
is worth on a reward screen, before any combat state exists. It worked by
enumerating ops, and it enumerated **10 of the engine's 56**. The other **46
were priced at exactly zero** — not approximately zero, not conservatively low,
but invisible. A card whose whole printed text was `detonate`, `salon_bow`,
`add_card`, `apply_aura`, `block_next_turn` or `copy_companion_in_hand` read to
every drafting arm as blank cardboard, and `_static_power` feeds `score_offer`
on *every* arm, so this biased every run-layer winrate in the repo.

Measured, pool-wide: **187 of 461 committed cards priced at 0.0** under the v12
scorer. Under v13 that is **133**, so **54 cards became visible to the drafter**
that previously were not.

This is the same defect class the repo has now found four separate times —
v6 (AoE blindness, the Furina-0% diagnosis), v7 (Kokomi's three verbs), v8
(`summon_kurage`), v9 (fanfare floor grants) — each time by noticing one
character drafting badly and tracing it back, and each time fixed for that one
character's verbs. Task 2 is what stops the fifth discovery from being
necessary.

### The prices

All 56 ops are now classified in `tier05/draft.py::STATIC_OP_PRICING`, one line
of rationale each, and computed in `_op_price` (the 10 that need the card, the
deck or the recursion stay in `effect_power`'s own branches). Magnitudes follow
the file's existing idiom: **one unit is one point of printed damage or Block**,
and nothing is priced at what it would be worth in a solved deck — only at what
an offer screen can defend without combat state. New named constants, with the
one-line rationale each was given:

| Op(s) | Price | Rationale |
| --- | --- | --- |
| `block_next_turn` | `STATIC_DELAYED_BLOCK_SHARE 0.8` × amount | real printed Block, one turn late; it cannot answer the attack in front of you |
| `buff_next_attack` | `STATIC_NEXT_ATTACK_SHARE 0.8` × amount | flat damage on the next Attack; nearly always spent, discounted for needing one |
| `chain_attack` | its own damage line × `STATIC_CHAIN_ATTACK_MULT 1.25` | a chain that kills nothing *is* the base volley; the drafter cannot see enemy HP |
| `detonate` | `STATIC_DETONATE_VALUE 3.0` + printed bonus, AoE-scaled | the payoff that makes half-price bomb placement real |
| `move_bombs` | `STATIC_BOMB_MOVE_VALUE 1.0` + bonus×0.5 | consolidation onto one body |
| `modify_bombs` | bonus × `STATIC_BOMB_DAMAGE_SHARE` | one neutral bomb, the existing bomb idiom |
| `chance_bomb_per_detonation` | chance × bomb damage × bomb-damage share | one neutral detonation |
| `apply_aura` | `STATIC_AURA_VALUE 2.0`, AoE-scaled | the reaction plan's entry token, at the Weak/Vulnerable magnitude |
| `swirl` | `STATIC_SWIRL_VALUE 1.5`, AoE-scaled | spreads an aura it did not apply; worth less, and nothing alone |
| `refresh_all_auras` | `STATIC_AURA_REFRESH_VALUE 1.0` | extends what is on the board; dead on a clean one |
| `gain_encore` | `STATIC_ENCORE_VALUE 0.3` per point | between the Fanfare floor (0.2, pays only through drafted readers) and Charge (0.5, read by a kit state) |
| `spend_encore` | the same rate, **negative** | an overdraw is a printed cost and must read as one |
| `salon_bow` | `STATIC_SALON_BOW_VALUE 2.0` per bow | one conservative bow, not the stage it implies |
| `spotlight_designate` | `STATIC_SPOTLIGHT_DESIGNATE_VALUE 1.5` | the universal half of what `_is_spotlight_access` already pays |
| `generate_guest_star`, `generate_from_pool`, `add_card` | `STATIC_GENERATED_CARD_VALUE 2.0` per token | a conjured card still costs energy to play; rarity deliberately not differentiated |
| — off-hand destination | × `STATIC_OFFPILE_CARD_SHARE 0.5` | same card, later, maybe not this fight |
| — `status`-rarity add | `−STATIC_STATUS_CARD_COST 2.0` | self-inflicted bloat is a printed cost |
| `copy_companion_in_hand`, `copy_spotlighted_in_hand`, `copy_companions_played_this_combat`, `replay_next_companion` | `STATIC_CARD_COPY_VALUE 3.0` (+`STATIC_FREE_COPY_BONUS 1.0` at `cost_override: 0`) | duplicates something the player *chose*, so above a conjured token |
| `autoplay_from_exhaust`, `autoplay_from_draw` | `STATIC_AUTOPLAY_VALUE 2.0` | a card played free, but not one the player picked |
| `extra_card_screen` | `STATIC_EXTRA_SCREEN_VALUE 2.0` | real run-layer value, discounted for firing only on a win |
| `discard` (random) | `−STATIC_RANDOM_DISCARD_COST 0.5` per card | a `chosen` discard is selection, not loss, and prices at zero |
| `exhaust_from` | `STATIC_EXHAUST_VALUE 0.5`, or `STATIC_STATUS_EXHAUST_VALUE 1.5` filtered | thinning vs. removing a Status/Curse |
| `scry_discard` | `STATIC_SCRY_VALUE 0.5` | exactly one worst card leaves, however many are seen |
| `recall_to_draw` | `STATIC_RECALL_VALUE 1.0` per card | a *chosen* card from discard onto the top of draw |
| `upgrade_in_hand` | `STATIC_UPGRADE_VALUE 1.5` | combat-scoped here, so under a full card |
| `grant_sly_this_turn` | `STATIC_GRANT_SLY_VALUE 0.5` | one turn of the rider `STATIC_SLY_SHARE` already half-prices |
| `heal` | `STATIC_HEAL_SHARE 0.5` per point | R52 healing law converts healing to Block; run HP level is invisible at offer time |
| `gain_max_hp` | `STATIC_MAX_HP_VALUE 1.0` per point | permanent HP *and* an immediate heal of the same size |
| `repeat_this` | multiplies the card's own total at `STATIC_REPEAT_SHARE 0.5` | it re-resolves the card, so it is a multiplier, not a term; every printed use sits behind a condition |

### The deliberate zeros are not oversights

Each is a **named constant** with its measurement or its reason at the
constant, so the next pass starts from a dial rather than from a rediscovery:

- **`draw` / `draw_while` / `draw_to_hand_size` / `energy` / `cost_mod` /
  `gain_spark` / `burst_energy`** — `STATIC_DRAW_VALUE`, `STATIC_ENERGY_VALUE`,
  `STATIC_SPARK_VALUE`, `STATIC_BURST_VALUE`, all `0.0`. The v3 header records
  the sweep in its own words: *"a measured sweep rejected flat draw/energy/
  Spark/Burst proxies: raising them monotonically reduced Klee's real-run
  result."* Honouring a measurement beats honouring a symmetry. `cost_mod` is
  priced *through* `STATIC_ENERGY_VALUE` so a future sweep moves them together.
- **`raise_fanfare_cap`** — `STATIC_FANFARE_CAP_VALUE 0.0`. The op's own
  docstring carries the measurement: read-at-cap under 1% under every pilot.
  Measured inert, not unpriced. It becomes live the moment floors stack.
- **`crash_fanfare`** — `STATIC_CRASH_FANFARE_VALUE 0.0`, and this one is a
  judgement call worth arguing with. The Final Verdict's crash is the *price*
  of a damage line the static scorer still cannot see (`bonus_formula:
  1_per_1_fanfare`). Priced symmetrically with `gain_fanfare_floor` it would be
  −6.0, which at cost 2 makes the sheet's only Hyperbeam undraftable — on a
  bookkeeping asymmetry, not on a valuation. Held at zero, and this line is the
  reason the formula reader must land before the dial moves.
- **`strip_block`** — `STATIC_STRIP_BLOCK_VALUE 0.0`. The op's docstring says
  it: enemies rarely carry Block in tier0, and whether they *should* is a
  question about the encounter set. A nonzero price would answer it by fiat.
- **`transform_in_hand`** — `0.0`. Its value is entirely the destination card;
  no committed card prints the op today.
- **`remember_card`** — `0.0`. It writes a payload a POWER later reads, and the
  self-power branch already prices the power. Paying here too is double-count.

### The D12 → D13 table

Same script, same cell, same seed, back to back on this machine, both stamps
printed by the harness itself:

```
python -m tier05.exp_roster_anchors --runs 600 --jobs 0
```

| character | plan | **D12** win / act-1 | **D13** win / act-1 | Δ win |
| --- | --- | --- | --- | --- |
| klee | demolition | 7.5% / 82.0% | 7.0% / 82.0% | −0.5 |
| klee | spark | 6.8% / 79.5% | 7.5% / 78.7% | +0.7 |
| klee | reaction | 11.7% / 85.8% | 9.7% / 85.2% | −2.0 |
| furina | **salon** | 10.8% / 58.3% | **11.0% / 59.3%** | **+0.2** |
| furina | **spotlight** | 2.3% / 57.5% | **3.3% / 61.7%** | **+1.0** |
| furina | **fanfare** | 1.8% / 55.3% | **2.8% / 56.0%** | **+1.0** |
| kokomi | priest | 2.8% / 43.3% | 3.0% / 42.2% | +0.2 |
| kokomi | commander | 2.5% / 52.7% | 3.5% / 52.3% | +1.0 |
| kokomi | assist | 0.0% / 34.7% | 0.5% / 34.3% | +0.5 |
| ref_ironclad | generic | 10.2% / 68.0% | 10.7% / 67.8% | +0.5 |
| real_ironclad | generic | 7.8% / 68.0% | 7.7% / 68.7% | −0.1 |
| real_silent | generic | 2.0% / 60.8% | 1.7% / 59.3% | −0.3 |

- **D12 row stamp:** `cell=roster-anchors[jobs=0,runs=600] seed=11 runs=600 RT7/D12/P3/C4`
- **D13 row stamp:** `cell=roster-anchors[jobs=0,runs=600] seed=11 runs=600 RT7/D13/P3/C4`

The D12 column reproduced the fanfare-compensation sprint's published Furina
rows (10.8 / 2.3 / 1.8) and all nine non-Furina rows exactly, which is what
makes the pair a comparison rather than two measurements.

**No arm separates at n=600.** Every Δ above sits inside overlapping 95% Wilson
intervals — the widest case, fanfare 1.8% [1.0, 3.3] vs 2.8% [1.8, 4.5], is a
+56% relative move that is still noise at this sample size. The act-1 column,
which is the tighter instrument, separates nowhere either (spotlight 57.5%
[53.5, 61.4] → 61.7% [57.7, 65.5] is the closest thing to a signal in the
table). **Nothing here is a ratified number and nothing here should be quoted
as a movement without a larger n.**

### The design question this bears on

The live question was *"does everything feed Salon by construction"*. On this
evidence the answer is **not obviously yes, and the repricing is directional
evidence against it**:

- **Salon moved least of the three Furina arms** (+0.2 win, +1.0 act-1) — it
  was already drafting well, which is consistent with its plan being built out
  of verbs the v12 scorer could already see (damage, Block, self-powers).
- **Spotlight and fanfare each moved +1.0 win**, the two largest Furina moves
  in the table, and spotlight took the table's largest act-1 move (+4.2). Both
  are plans assembled out of verbs that were literally invisible
  (`spotlight_designate`, `copy_spotlighted_in_hand`, `salon_bow`,
  `gain_encore`, `generate_guest_star`). Part of what read as "these archetypes
  are weak" was the drafter refusing to draft them.
- **The size of the correction does not close the gap.** Fanfare at 2.8% is
  still at the roster floor (real_silent 1.7–2.0%), and spotlight at 3.3% is
  still a third of salon. Repricing moves them; it does not rescue them. The
  compensation sprint's REPORT-AND-STOP finding survives this bump.

Read carefully: the honest summary is *"the fanfare and spotlight arms were
partly suppressed by the drafter's blindness, not only by design — but not
enough of it to change the ruling."* Confirming the direction needs a larger n
than this pass ran.

### Version-bump procedure (mirroring D11 → D12)

- `DRAFTER_VERSION 12 → 13` in `tier0/constants.py`, with the full
  what-changed / why-it-is-not-bookkeeping / what-is-archived stanza the v6–v12
  entries each carry.
- Stamp consumers needed **no** edit: `tier05/cells.py::versions` reads
  `C.DRAFTER_VERSION` live at call time and never stores it, which is exactly
  the property R68 added it for. `exp_roster_anchors` prints the live stamp on
  both tables above with no code change.
- Two stamp-sensitive tests were **re-homed, not re-banded** (the D11→D12
  precedent — annotate the world change, never invent a ratified band):
  - `test_m5::test_drafter_v3_values_klee_visible_utility` — Sweet Dreams 2.0 →
    2.5. The card prints `refresh_all_auras` beside its conditional Block; the
    v3 claim the test makes is untouched, only the count of priced verbs moved.
  - `test_m5::test_skip_is_a_real_pick` — the offer was Borrowed Brilliance,
    which was below the skip bar *only because* `copy_companion_in_hand` was
    unpriced. Under v13 it scores 1.33 and is correctly taken, so keeping it
    would have pinned the defect instead of the claim. Re-homed onto Casting
    Call, whose whole printed text is `raise_fanfare_cap` — a **measured** zero,
    which is a different thing from an unpriced one.
- Every pre-v13 roster number in this repo is archived by house rule and is
  incomparable with v13 output. The D12 column above is the last v12 reading
  and exists only as the paired half of this table.

---

## Task 2 — the op-parity lint

`tools/lint_op_parity.py`, built in the pattern of
`tools/lint_constant_parity.py` and carrying the same discipline: every key of
`tier0.engine.effects.OPS` must appear in `tier05.draft.STATIC_OP_PRICING` with
a one-line rationale — **including the zeros, which must say ZERO and say why**.
An op in the registry with no entry is a FINDING, not a skip. It also sweeps
`_static_power` over all 461 committed cards, so a table entry with no
implementation behind it fails here rather than in the middle of a 7,200-run
measurement.

Green:

```
$ python tools/lint_op_parity.py
op parity OK: 56 registered ops, 56 priced, 461 cards priced without error (DRAFTER_VERSION 13)
```

Red, demonstrated — this is `test_the_op_parity_lint_still_catches_a_newly_registered_op`,
which registers a fictional op in-process, asserts the finding, and restores the
registry in a `finally`:

```
UNPRICED OP: 'chorus_of_the_unpriced' is registered in tier0.engine.effects.OPS
but has no entry in tier05.draft.STATIC_OP_PRICING. Every op needs a price and a
one-line rationale -- including a deliberate zero, which must say ZERO and say
why. A card built on an unpriced op is worth nothing to the drafter, silently.
```

Wired in both places the sibling lints are:

- **CI** — `.github/workflows/repo.yml`, `lints` job, next to `constant parity`.
- **pytest** — `tier0/tests/test_sheet_lints.py`, green test *and* red test, for
  the reason the constant-parity test states: the retune happens in Python and
  the person doing it runs the suite; making them wait for CI is one round trip
  too late.

`_op_price` also **raises** rather than returning a silent `0.0` for an unknown
op, so the failure mode is loud even in the window before the lint runs.

---

## Task 3 — statistics unification

New module `tier05/stats.py`: **one** `percentile`, **one** `wilson95`.

### The percentile — and which convention was load-bearing

Five hand-rolled copies existed under **two incompatible conventions**, and two
of them carried docstrings swearing they matched a third that they did not:

| copy | convention | docstring claim |
| --- | --- | --- |
| `tier05/run_metrics.py` | linear interpolation | — |
| `tools/realistic_axis_scores.py` | linear interpolation | — |
| `tools/real_battery_calibration.py` | linear interpolation | — |
| `tier05/elite_blitz.py` | **nearest-rank** | *"matching … run_metrics"* |
| `tier05/kurage_telemetry.py` | **nearest-rank** | *"Matches run_metrics"* |

Both wrong ones said, in their own words, *"two percentile definitions in one
report is how a moved tail gets argued about instead of acted on."* They were
right, and they were the second definition.

**Standardised on linear interpolation** (numpy default, type 7), for three
reasons in this order: it is what the oldest and most-read surface
(`run_metrics.survival_profile`, whose HP bands appear in every survival report
on record) has always computed; it is what the two nearest-rank copies
*declared* they were computing, so it honours their intent rather than their
arithmetic; and it is the standard definition.

**The stop-condition was checked and not triggered. No ratified band moved.**
Every ratified band in this repo is a **winrate** band, and a winrate is a
ratio, not a quantile — no locked band takes a percentile as an input, so there
was no locked number for the two conventions to disagree about. What *did* move
is **Kokomi pulse telemetry**, which is reported and has never been ratified:

| reading | old (nearest-rank) | new (linear) |
| --- | --- | --- |
| `kurage_telemetry.aggregate` p95, on the pooling fixture | 500 | 28.8 |
| `elite_blitz.aggregate` `p95_pulse`, on the hierarchy fixture | 100 | 14.5 |

Both fixture assertions were **re-homed with the change named in them**, not
deleted, and both tests' actual claims survive untouched: pooling over pulses
rather than combats (a mean of per-combat p95s would be 252, and `max` still
asserts the huge pulse is visible), and the p95-over-largest-body relation. A
grep of `docs/` found **no** doc quoting a `p95_pulse`, so no published number
is silently contradicted.

### The Wilson interval

Three copies, two return shapes:

- `tier05/run_metrics._wilson95` → `(lo, hi)` — canonical
- `tier05/exp_shop_companion_channel.wilson` → `(lo, hi)`, clamped to `[0, 1]`
- `tools/measure_realistic_act1.wilson` → `(p, lo, hi)` — the odd shape
- (`tools/klee_survival_sprint._wilson` was a third copy, unified in the same
  pass although the brief only named two)

Unified to `stats.wilson95(k, n) -> (lo, hi)`. The point estimate is `k / n`,
which every caller already has, so returning it here only gave two call sites
two different tuple shapes; `measure_realistic_act1` now computes `p` on its own
line. The `[0, 1]` clamp is **kept** — analytically the Wilson interval is
already inside the unit interval, so it is a float-error guard, never a
correction, and it is the cheaper of two identical answers.

No number moves: all four implementations were the same arithmetic.

---

## Task 4 — pilot weights into constants

Fourteen inline float literals moved out of `tier0/pilot/policy.py` into named
constants in `tier0/constants.py`. **MOVED, NOT RETUNED** — every value is
byte-identical to the literal it replaced.

`PILOT_REACTION_TRIGGER_VALUE 6.0`, `PILOT_REACTION_SEED_VALUE 2.0`,
`PILOT_DRAW_WHILE_VALUE 2.0`, `PILOT_SPARK_VALUE 0.7`, `PILOT_BURST_DIVISOR 10.0`,
`PILOT_ENCORE_VALUE 0.8`, `PILOT_SPOTLIGHT_DESIGNATE_SEQUENCING 20.0`,
`PILOT_SPOTLIGHT_DESIGNATE_GENERATOR 0.1`, `PILOT_SPOTLIGHT_DESIGNATE_OPENING 4.0`,
`PILOT_SPOTLIGHT_DESIGNATE_REDESIGNATE 0.3`, `PILOT_SPOTLIGHT_BOOST_COMBAT 3.0`,
`PILOT_SPOTLIGHT_BOOST_TURN 1.5`, `PILOT_SPOTLIGHT_BOOST_EARLY 0.3`,
`PILOT_GUEST_STAR_VALUE 2.5`, `PILOT_SPOTLIGHT_COPY_VALUE 3.5`,
`PILOT_SETUP_TAPER_TURNS 12.0`.

The four-value spotlight-designate ladder and the three-value boost ladder were
moved whole rather than cherry-picking the two literals the brief named: half a
ladder in constants and half inline is worse than either.

**Verified behaviour-identical by seed**, before the D13 bump landed and while
D12 was still live: `python -m tier05.exp_roster_anchors --runs 100 --jobs 0`,
all 12 arms, byte-identical table before and after the move (`diff` clean).

Why they belong in `constants.py`: this file is what a version stamp labels. A
pilot weight only reachable by reading a function body cannot be swept (the R67
`KNOB_READS` machinery hooks module attributes), cannot be diffed against a
prior world, and cannot be cited in a ruling. Their calibration history is
unchanged and still recorded at the call sites.

---

## Still owed

1. **[USER] red pen on all 33 v13 prices.** They are PROPOSED. The ones most
   worth arguing with, in order: `STATIC_ENCORE_VALUE 0.3` (it makes
   `spend_encore` cards read negative — Limelight now scores −0.3);
   `STATIC_CRASH_FANFARE_VALUE 0.0` (a cost priced at zero because its paired
   benefit is invisible); `STATIC_CARD_COPY_VALUE 3.0` (the largest new
   constant, and the one with the least evidence behind it).
2. **`bonus_formula` is still priced at zero — 20 printed uses.**
   `1_per_4_fanfare` ×8, `1_per_2_fanfare` ×4, `2_per_salon_member` ×2,
   `1_per_2_charge` ×2, and one each of `2_per_detonation_this_combat`,
   `2_per_companion_played_this_turn`, `1_per_3_encore`, `1_per_1_fanfare`.
   This is the *same defect in a different grammar*: it is how Furina's readers
   and Kokomi's Charge payoffs print their damage, and the offer scorer sees
   none of it. Deliberately excluded from D13 so the table above stays
   attributable to the op change the user accepted. It is the direct blocker on
   `STATIC_CRASH_FANFARE_VALUE`.
3. **Self `apply_power` for non-engine powers is still zero — `salon_member`
   ×15.** Deploying a Salon member is Furina's core verb and reads as blank
   cardboard at offer time. Excluded on purpose: pricing it would inflate the
   salon arm in the same measurement that is being used to ask whether
   everything feeds Salon by construction. It should land in a pass that is not
   also answering that question.
4. **133 of 461 cards still price at 0.0** to the offer scorer (down from 187).
   Items 2 and 3 are most of the remainder; the rest are Curses, Statuses and
   kit cards, which *should* be zero.
5. **A larger-n confirmation of the fanfare/spotlight movement.** Nothing in
   the D12→D13 table separates at 600 runs. The +1.0 moves are directional
   only.
6. **`DECISIONS.md` entry.** Not written — the ledger belongs to the user, and
   a MEASUREMENT-class entry here would be recording numbers that are still
   PROPOSED.
