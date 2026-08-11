# Volatility read — 2026-08-10

**What this is.** A fresh reading of the five HP-volatility metrics, for every
character and plan on the roster, in the current world. It exists so that
QUEUE item `S4-G6` — declaring Kokomi's HP-stability band — can be decided with
current numbers on the table instead of stale ones.

**What this is NOT.** It is not a proposed band. It contains no candidate
numbers and no recommendation. The `band` field in the code is still `None` and
stays `None` until [USER] rules.

---

## 1. Read this first — where the band comes from

The band is declared from **design intent**. That is DEC-D5, clauses 2–4, in
plain terms:

- The declaration may be **informed by observation** — tables like this one.
- It must be **recorded as a design-intent declaration**, not as a number read
  off a measurement.
- It **may not be revised against the grading playtest**. Once declared, it
  stands, and the playtest either passes it or fails it.

So this table is input to a judgement, not the judgement. Picking a threshold
straight off the numbers below would be drawing the target around the shot.

**Why a fresh read was needed.** The band was nearly declared on 2026-08-05
against numbers from world `RT7/D13/P3/C4`. All four stamp boundaries have moved
since; the old numbers are not comparable to today's, and the comparator used
in that prep was mislabelled. The candidate bands A–D from 2026-08-05 died with
their data. They are not carried forward here.

**One inherited error, flagged so it is not inherited again.** Two archived
documents — `docs/archive/sprint-kokomi-instrument-log-2026-07-29.md` and
`docs/sitting-prep-2026-08-05.md` §7c — call Klee "the roster's declared
HP-volatility pole". That is wrong. The standing declaration is
`docs/current/characters/kokomi-kickoff-v1.md:30`: **Furina = HP volatility,
Kokomi = HP stability.** Klee is not a pole in either direction. Those archived
files are frozen history and are not edited (R101b). The one place the mislabel
survived into live code, a comment in `tier05/exp_kokomi_stability.py`, was
corrected in the same commit as this file.

---

## 2. How the run was made

| item | value |
| --- | --- |
| command | `PYTHONPATH=. python -m tier05.exp_kokomi_stability --runs 600 --jobs 0` |
| stamp | `cell=kokomi-stability[jobs=0,runs=600] seed=11 runs=600 RT9/D14/P6/C8` |
| world | RT9 / D14 / P6 / C8 |
| runs per arm | 600 |
| seed | 11 (the current default — the canonical cell's) |
| route / policy | hunter / assigned, realistic (relics + potions), all registered acts |

This is a **descriptive re-read** in the current world, the same class as the
other 2026-08-08 sitting re-reads. Checked against `docs/current/EXPERIMENTS.md`:
no prediction is made, nothing is graded, no band moves, so no pre-registration
is required.

The instrument script previously ran six arms. It now runs the same twelve arms
as `tier05/exp_roster_anchors.py`, so a stability row and a winrate row for the
same arm always come from the same arm list and the same world. Each arm is an
independent run; adding arms does not change any other arm's numbers.

---

## 3. The five metrics, in plain words

Every value is a **fraction of maximum HP**. **Lower means flatter** in all five.

| short name | code name | what it means |
| --- | --- | --- |
| lossSD | `hp_loss_sd_pct` | How much the HP lost per fight varies from fight to fight. The headline flatness number. |
| inFtSD | `within_fight_sd_pct` | How jagged the HP line is *inside* one fight, round by round. Averaged per fight, so it is not just the slow slide of attrition. |
| wrstRnd | `worst_round_drop_pct` | The biggest fall in a single round. This is the spike a shield is meant to eat. |
| <50% | `round_share_below_50` | Share of all rounds that ended below half HP. |
| <30% | `round_share_below_30` | Share of all rounds that ended below 30% HP. Time spent in danger. |

The round in which a character dies is excluded from all five. Dying is what the
winrate table measures; a round ending at 0 HP would sit under every threshold
and drown the signal.

---

## 4. THE FRESH TABLE — RT9/D14/P6/C8, n=600, seed 11

| character | plan | max HP | lossSD | inFtSD | wrstRnd | <50% | <30% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| klee | demolition | 62 | 0.204 | 0.079 | 0.129 | 0.418 | 0.183 |
| klee | spark | 62 | 0.206 | 0.081 | 0.131 | 0.416 | 0.191 |
| klee | reaction | 62 | **0.201** | 0.077 | 0.127 | 0.411 | 0.176 |
| furina | salon | 60 | 0.236 | **0.072** | 0.108 | **0.314** | **0.143** |
| furina | spotlight | 60 | 0.227 | 0.074 | 0.111 | 0.336 | 0.151 |
| furina | fanfare | 60 | 0.243 | 0.075 | 0.106 | 0.333 | 0.153 |
| kokomi | priest | 70 | 0.234 | 0.081 | 0.119 | 0.439 | 0.217 |
| kokomi | commander | 70 | 0.227 | 0.079 | 0.117 | 0.414 | 0.199 |
| kokomi | assist | 70 | 0.242 | 0.084 | 0.119 | 0.459 | 0.229 |
| ref_ironclad | generic | 80 | 0.248 | 0.094 | 0.134 | 0.328 | 0.145 |
| real_ironclad | generic | 80 | 0.232 | 0.092 | 0.131 | 0.369 | 0.166 |
| real_silent | generic | 70 | 0.245 | 0.073 | **0.101** | 0.368 | 0.167 |

Bold marks the lowest (flattest) value in each column.

---

## 5. The archived table — RT7/D13/P3/C4, n=600, seed 20260729 — **STALE**

These are the 2026-07-29 numbers, reproduced only so the movement is visible.
**They are not comparable to §4.** All four stamp boundaries have moved, and the
seed is different too. Do not quote them as current, and do not read a trend
into a single pair of numbers.

| character | plan | max HP | lossSD | inFtSD | wrstRnd | <50% | <30% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| kokomi | priest | 70 | 0.234 | 0.082 | 0.119 | 0.417 | 0.203 |
| kokomi | commander | 70 | 0.231 | 0.079 | 0.115 | 0.407 | 0.193 |
| kokomi | assist | 70 | 0.246 | 0.085 | 0.119 | 0.424 | 0.216 |
| klee | reaction | 62 | 0.204 | 0.079 | 0.127 | 0.419 | 0.183 |
| furina | salon | 60 | 0.223 | 0.071 | 0.107 | 0.314 | 0.133 |
| ref_ironclad | generic | 80 | 0.248 | 0.095 | 0.135 | 0.332 | 0.145 |

The archived run covered six arms. The other six arms in §4 have no stale
counterpart on this instrument.

---

## 6. What the fresh table says — facts only

### Which arm is flattest now

No single arm is flattest on all five. Split by column:

- **furina / salon** is flattest on three of the five: `inFtSD` (0.072),
  `<50%` (0.314) and `<30%` (0.143). It is the closest thing to an overall
  flattest arm in this table.
- **klee / reaction** is flattest on `lossSD` (0.201). All three Klee arms
  (0.201–0.206) sit below every other arm on that column.
- **real_silent** is flattest on `wrstRnd` (0.101), just under the three Furina
  arms (0.106–0.111).

Note the disagreement between columns, because it matters for a band written
against one of them: the character with the smallest fight-to-fight spread
(Klee) spends noticeably more rounds under half HP than Furina does. "Flat"
is not one property.

### Where Kokomi's arms sit

- **`lossSD`** — 0.227 to 0.242. Mid-pack, and the column where she is most
  ordinary. All three Klee arms (0.201–0.206) are flatter than all three Kokomi
  arms. The Furina arms interleave with hers (commander 0.227 is below salon
  0.236; assist 0.242 is above it). `ref_ironclad` (0.248) and `real_silent`
  (0.245) are above every Kokomi arm; `real_ironclad` (0.232) sits between
  commander and priest.
- **`inFtSD`** — 0.079 to 0.084. Jaggier than every Furina arm (0.072–0.075)
  and than `real_silent` (0.073). Against Klee the two sets interleave narrowly
  (Klee 0.077–0.081, Kokomi 0.079–0.084), with kokomi/assist at 0.084 the
  jaggiest character arm in the table. Only the two Ironclad anchors
  (0.092, 0.094) are jaggier still.
- **`wrstRnd`** — 0.117 to 0.119. Below all three Klee arms (0.127–0.131) and
  below both Ironclad anchors; above all three Furina arms (0.106–0.111) and
  above `real_silent` (0.101). This is her best relative showing of the five.
- **`<50%`** — 0.414 to 0.459. Assist (0.459) is the highest value of any arm
  in the table and priest (0.439) is the second highest; commander (0.414) is
  fifth, just under the Klee arms (0.411–0.418). Every Furina arm and both
  Ironclad anchors spend clearly less time under half.
- **`<30%`** — 0.199 to 0.229. Kokomi holds the **three highest values in the
  table**. Assist (0.229) is the highest; the next non-Kokomi arm is klee/spark
  at 0.191.

Summarised without judgement: **on time-spent-low she is the worst on the
roster (the three highest `<30%` values, and two of the three highest `<50%`
values, are hers); on worst-single-round she is better than Klee and the
Ironclads but worse than Furina; on the other two columns she is mid-pack.**
The three
Kokomi arms cluster closely on every column, so this reads as a property of the
character rather than of one plan.

The character the standing kickoff line names as her opposite — **Furina, the
declared HP-volatility pole** — reads **flatter than Kokomi on four of the five
columns** (all but `lossSD`, where the two overlap). That is the same shape of
finding the 2026-07-29 log reported, and it survives the move to the current
world.

### One column that is Kokomi's alone

`prev/ft`, the ward-prevention feed, is non-zero only for Kokomi
(priest 0.85, commander 0.79, assist 0.47 raw HP per fight). It is reported,
never credited to an axis, and it is not one of the five band metrics. It is
noted here only because it is the one place her kit visibly does something no
other arm does.

### Movement against the stale table

Again: different world **and** different seed, so a difference here has at least
two possible causes and neither can be separated from the other. Read this as
"how much did the printed number move", nothing more.

- **Mostly still.** `lossSD`, `inFtSD` and `wrstRnd` moved by 0.005 or less on
  every one of the six arms that has a stale counterpart. `ref_ironclad` is
  essentially unchanged on all five.
- **The time-spent-low columns drifted up for Kokomi.** `<50%` moved
  +0.022 for priest (0.417 → 0.439) and **+0.035 for assist** (0.424 → 0.459),
  the largest single movement in the comparison. `<30%` moved up
  +0.013 to +0.014 for priest and assist.
- **Klee/reaction drifted slightly down** on both time-low columns
  (`<50%` 0.419 → 0.411, `<30%` 0.183 → 0.176).
- **Furina/salon** moved up on `lossSD` (0.223 → 0.236) and on `<30%`
  (0.133 → 0.143), while `<50%` sat at exactly 0.314 in both worlds.
- Net effect on the ordering: the gap between Kokomi and Furina on the
  time-spent-low columns is **wider** now than it was in the archived table.

---

## 7. Still owed

**The band declaration itself — [USER], QUEUE `S4-G6`.** From design intent,
recorded as such, before the grading playtest
(`docs/current/playtest/kokomi-playtest-protocol.md`, unrun), and not revised
against it. Nothing in this document is a candidate.
