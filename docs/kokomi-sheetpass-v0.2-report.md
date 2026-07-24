# Kokomi Sheet Pass v0.2/v0.3 — Report, Act-Sim Diagnosis & Charge-Curve Pass

**Date:** 2026-07-24. Governing rulings: R51 (elite axes A2+A6, stability
band, debuff texture) and R52 (batch closure of every kickoff gate).
Predecessors: docs/kokomi-kickoff-v1.md, docs/kokomi-roster-v0.1-report.md.
Suite: 634 passed at repo root. Nothing in this report is ratified; every
number is PROPOSED and every §4 lever is a red-pen ask.

## 1. What this pass shipped

- **sango_prayer rework** (R52 ask 1): the heal-12 is gone — now Weak 2 to
  ALL + Block 5, still Rare + Exhaust. Zero heals remain in her pool and a
  new in-suite gate (`test_law2_no_heals_anywhere_in_her_pool`) keeps it so.
- **R51 texture pair**: `exposing_current` (uncommon attack, Exhaust,
  6 dmg + Vulnerable 2) and `tidal_lure` (uncommon skill, Block 4, Sly:
  Vulnerable 1). A second gate
  (`test_r51_debuffs_ride_exhaust_or_sly_pieces_only`) enforces the ruling
  shape: enemy debuffs only on exhaust/Sly pieces, never at common.
- **Raiden Shogun** (R52 ask 9): `raiden_musou_no_hitotachi`, 5★ Rare,
  18 single-target electro, deliberately shapeless — the executioner
  jackpot beside Itto's bruiser. Conscript-fishable at natural odds (N5).
- **docs/kokomi-upgrades.yaml** (NEW): full coverage of both sheets under a
  resource-curve law — no upgrade moves a Charge line or conscript count
  (machine-checked). Registered in `UPGRADE_SHEETS` (worknote §10).
- **DRAFTER_VERSION 6 → 7**: the tier05 static scorer prices conscript
  (1.5/transform), gain_charge (0.5/point), and Sly riders (half face).
  Klee/Furina/Ironclad decks carry none of these ops — bit-identical for
  them; anchors below were re-measured in the v7 world anyway.
- **tier05 runner**: `--character kokomi` (generic/commander/priest/assist,
  default priest).
- **Shared-tool fix**: lint_strict_domination was blind to Sly lists and
  flagged plain-Block commons as dominating tidal_lure; Sly effects now
  count as their own benefit dimension.

## 2. Labeled worlds measured this pass

### 2.1 Tier-0 battery v0.2 (seed 20260719, 300 fights/encounter)

|            | A1  | A2  | A3  | A4  | A5  | A6  | A7  |
|------------|-----|-----|-----|-----|-----|-----|-----|
| starter    | 1.3 | 4.8 | 1.5 | 0.5 | 3.4 | 1.8 | 1.8 |
| commander  | 1.9 | 5.8 | 3.5 | 0.5 | 3.5 | 2.2 | 1.3 |
| priest     | 2.3 | 6.7 | 3.4 | 0.5 | 3.2 | **3.4** | 1.1 |
| assist     | 1.0 | 5.5 | 3.4 | 0.5 | 3.8 | 1.7 | 0.8 |
| **median** | 1.9 | **5.8** | 3.4 | 0.5 | 3.5 | 2.2 | 1.1 |

A4 collapsed to floor everywhere — that is R51 working as ruled (the heal
is gone; ward prevention feeds the stability band, not an axis). Priest A6
moved 2.8 → 3.4 from the texture pair; the MEDIAN A6 (2.2) is still far
from elite — closing that is authoring work for the next dose (§4).
Constraint A2>A1 holds in every column.

### 2.2 Act 1–3 realistic runs (DRAFTER v7, RUNTEMPLATE 5, 500 runs/plan, seed 42)

| plan            | run wr | act1 cleared | note |
|-----------------|--------|--------------|------|
| kokomi/priest   | 0.0%   | **0%** | 381/467 die at the first Elite |
| kokomi/commander| 0.0%   | **0%** | 324/489 die at the first Elite |
| kokomi/assist   | 0.0%   | **0%** | same wall |
| kokomi/generic  | 0.0%   | **0%** | same wall |
| klee/demolition | 3.4%   | 83%  | anchor, same instrument |
| furina/salon    | 10.4%  | 57%  | anchor, same instrument |
| real_ironclad   | 3.6%   | 59%  | anchor, same instrument |

She loses ~10 HP per NORMAL fight (median HP by fight: 87% → 71% → 56%;
anchors lose 3–7) and then dies at node 4 with an on-time deck of ~13.

## 3. Diagnosis: the elites are checks, and she fails all three

Killer attribution (300-run probe, priest): ~83% of deaths are the act-1
elite pool, split evenly between bygone_effigy and phantasmal_gardener,
byrdonis close behind — **all three kill her**, so this is not (only) the
Gardener AoE wall. The pool is three explicit checks:

- **byrdonis** — ramp clock (Swoop 17 +2 ramp, +1 Str/turn). She is a slow
  scaler by law; she drowns.
- **bygone_effigy** — burst check (127 HP, 2-turn sleep, then 23/turn).
  Her engine is offline at node 4 (time-to-online: 2–5% of runs).
- **phantasmal_gardener ×4** — AoE check with **Skittish 6** (first hit
  per body per turn gains 6 Block). This ZEROES surging_shoal: her only
  AoE prints 4, below the Skittish threshold. As authored it is a trap
  card in this fight — the exact fight it was added for.

Counterfactual arms (300 runs each, priest, act-1 clear):

| arm | act1 |
|-----|------|
| baseline | 0.0% |
| vigil_of_the_deep in starter (prevention from fight 1) | 0.0% |
| 2× surging_shoal in starter (AoE access) | 0.0% |
| ward + AoE | 0.0% |
| Burst meter 50→40→30→20 bracket | 0.0 / 0.0 / 0.0 / 0.3% |
| fully smithed starter (all + forms) | 5.0% |
| 3× pulsing_current+ added (frontload) | 1.0% |
| 2× ritual_purification + pearl_barrage (engine head start) | **0.0%** |
| everything (smithed + frontload + engine) | 12.7% |

**Defense does not move the wall. AoE access does not move the wall. Burst
cadence does not move the wall. Only raw output moves it — and even the
"everything" arm reaches 12.7% vs anchors' 57–83%.** The binding
constraint is damage throughput, by roughly an order of magnitude.

The sharpest line: the engine head start alone moved NOTHING. Fuel is not
the problem — even the v0.1 starter banks 7 Charge/fight. **The identity
"converts card economy into damage" has almost no conversion sites below
Rare.** §2.2's rate limits (readers are Rare / Exhaust / cost ≥ 2, plus
the kit Garment at +1 per 4 Charge) mean the priest lane's actual damage
is her dreadful basics until a Rare shows — and the run template's checks
arrive at node 4, long before the rarity ladder does.

Furina survived act 1 without frontload because Salon members deal free
damage EVERY turn from fight 1. Kokomi's structural analogues — conscripts
(one-shot, Exhaust) and Charge readers (Rare-gated) — both discharge
instead of ticking. That is the design gap, stated plainly.

## 4. Ruling asks (red-pen; nothing below is implemented)

- **P1 — open sub-Rare Charge conversion (the big one).** Amend the §2.2
  rate-limit posture to allow small "N + 1 per M Charge" readers at
  uncommon (and possibly one at common), so the engine's fuel has on-curve
  spend sites. This is the identity-true fix: it makes the elite fights a
  race her declared A2 can actually run. Proposed shape for discussion:
  uncommon attack, 5 + 1 per 4 Charge, single target, no Exhaust — the
  Rare nuke and kit Garment keep their premium reads.
- **P2 — printed-floor reprice.** Her plain cards (4/6/7) sit below the
  elite bills AND below Skittish 6. Candidates: surging_shoal 4 → 7-to-all
  (it must clear Skittish to be the Gardener answer it was added to be),
  pulsing_current / waterspout one step up. A1 stays her weakest axis
  RELATIVELY; the absolute floor still has to pay act-1 bills.
- **P3 — a ticking body for the commander.** Conscripts Exhaust; Furina's
  members tick. Options: a persistent-recruit mode at Uncommon+ (the
  Gorou-banner shape as a summon), or accept that commander's damage story
  also routes through P1. Design conversation, not a number.
- **P4 — prevention on curve (stability band).** An uncommon lesser ward
  (e.g., 3, same latch) so the stability identity exists before a Rare
  shows. The probe says defense alone fixes nothing — this is for the
  band's sake AFTER P1/P2 land, not the wall's.
- **P5 — re-bracket the meter and statline knobs after P1–P3**, then
  re-run this instrument. Meter movement is meaningless while the Garment
  bonus is +1–2 damage per attack at node-4 Charge levels.

## 6. v0.3 charge-curve pass (user-directed, same day)

USER DIRECTION (verbatim intent): StS is built on "big numbers clear act 1;
multipliers and velocity clear act 3" — and this project has repeatedly
priced multiplicative scaling too defensively. Benchmark: a Regent Common
is "deal 7 damage, Forge 7, 1 cost" where Forge permanently feeds the
finisher meter and grants finisher access. Question: is Kokomi's kit
underpriced in Charge relative to that power level?

### 6.1 Audit: yes, on both axes at once

- Her best Charge common (ritual_purification) paid 1 energy + a net card
  for 3 meter and ZERO damage; the benchmark common pays nothing and gets
  7 + 7. Her RARE accelerant (prayer_to_the_moon, 5 meter) generated less
  than the benchmark COMMON.
- The read side was decoration: GARMENT_CHARGE_DIVISOR 4 made a node-4
  bank worth +2 damage per attack; the only other reader was a
  once-per-fight Rare. Access-weighted, a Charge point bought ~1 damage.
- Compounded: ~1/6 to 1/12 of the benchmark's scaling throughput per
  common, with sub-Strike baselines under it. This audit is what the §3
  "order of magnitude" measurement looks like in card terms.

### 6.2 The dose ladder (every arm 300 runs/plan unless noted)

| world | act1 clear | run |
|-------|-----------|-----|
| v0.2 (pre-pass) | 0.0% | 0.0% |
| v0.3 reprice alone (basics 6, Regent commons, /2 divisor, riptide_strike) | 1.0% | 0.0% |
| + any accrual knob (funnel ×2, Regent-parity riders, meter 40/30) | ≤3.2% | 0.0% |
| + starter swaps S3 (tide_reading→surging_shoal, 1 recall→waterspout) | 4.2% | 0.0% |
| + waters_edge 7 | 5.8% | 0.0% |
| **+ meter 50→10 (the decisive lever)** | **33–47%** | **2–3%** |
| meter bracket at S3: 15 / 12 / 10 / 8 | 22 / 26 / 33 / 43% | — |

The finding under the finding: no *scaling-rate* knob could fire before
node 4. What closed the wall was making the Burst FAST-CYCLING — meter 10
fires the Garment nearly every fight, which is Kokomi's structural
analogue of Furina's guaranteed run-start Salon Member (the thing her 57%
act-1 world rides on). Anchor correlation that predicted this: act-1
clear tracks tier0 starter winrate (Klee 99.9%→83%, IC 59.6%→59%, Furina
51.8%→57%, Kokomi-v0.1 30.5%→0%).

### 6.3 Landed v0.3 world (ALL PROPOSED, [USER] red-pen)

Cards: waters_edge 4→7 (kaboom parity); pulsing_current = "deal 7, feed 1"
(the Regent shape); waterspout 7→10; surging_shoal 4→7 (clears Skittish 6);
ritual_purification line 2→4; pearl_barrage base 3→5; exposing_current
6→8; nereids 10→12; depths_judgment base 8→10; prayer_to_the_moon 4→7;
NEW riptide_strike (uncommon, 5 + 1 per 2 Charge, single target — the
on-curve reader). Constants: GARMENT_CHARGE_DIVISOR 4→2. Kit: Garment
splash 5→7. Character: burst_max 50→10; starter S3 swaps.
(cleansing_tide 12 was tried and reverted — it strictly dominated
shell_of_sanctuary and Block is provably not her constraint.)

Pre-R53 500-run world (waters_edge 7): priest 2.4% run / 40% act1;
commander 2.2% / 56% act1 (at Furina's 57%); generic 0.6% / 30%; assist
0.2% / 24%.

**R53 REVERT (user ruling): waters_edge stays at Strike parity (6) — the
kaboom-parity arm is rejected. COMMITTED WORLD, re-measured (500
runs/plan): priest 2.0% run / 32% act1; commander 1.6% / 49%; generic
0.4% / 26%; assist 0.0% / 20%.** The parity revert costs ~5–8 act-1
points, as the grid predicted; the world stays in the cast's
neighborhood (commander 49% vs Furina 57% / IC 59%). Act-2/3 falloff
keeps Klee's shape (commander 49/20/2 vs Klee 83/28/3). From 0% to this
in one directed pass. R53-world battery: starter A1 4.3 vs A2 3.0 —
the §6.4 constraint violation and TOO_STRONG median PERSIST after the
revert (they belong to the fast-cycle Garment, not the basic); ratified
Klee/Furina bands hold. The §6.4 options remain the open review item,
and the user has flagged an identity-divergence concern for the
card-by-card review.

### 6.4 THE OPEN TENSION (this is the red-pen decision)

The tier0 battery of the landed world (seed 20260719, 300 f/enc):
starter A1 4.7 vs A2 3.0 — **the ruled A2_scaling>A1_frontload constraint
is VIOLATED** — and the archetype median trips TOO_STRONG (A1 4.4 /
A2 4.4 / A6 4.4 all ≥4; commander package warns at 4.4 vs 4.5). The
fast-cycling Garment measures as FRONTLOAD in tier0's ratio instrument:
early windows + a 7-all splash most fights. Mechanically it is
Charge-scaled damage; instrumentally it lands in turns 1–3. (R19 caveat
family: the A1/A2 ratio reads any early damage as frontload — partial
artifact, but TOO_STRONG is an independent tripwire and also fires.)
Ratified Klee/Furina bands all still hold; anchors unmoved.

Compromise arms measured (act1, 300×2 plans): splash 7/turns 3 (landed)
47.3%; splash 7/turns 2 → 39.7%; splash 0/turns 3 → 26.8%; splash 0/
turns 2 → 20.5%. Nothing dominates — the act-1 wall and the A1 axis are
fed by the same early windows.

Options for ruling:
- **O1 — accept and re-declare**: fast-cycle Burst is her real identity
  (guaranteed periodic output, very jellyfish); amend the constraint to
  acknowledge Garment output as engine damage (e.g., exclude kit-Burst
  damage from A1's raw, an instrument change = red-pen by definition),
  or re-declare the elite pair as measured (A6 IS elite now at 4.4).
- **O2 — compromise dose**: splash 7/turns 2 (40% act1) and re-measure
  the battery to see if A1 falls under A2.
- **O3 — bigger meter + compensating starter power**: return toward
  meter 15–20 and buy the difference with starter statline (the grid says
  this costs ~15–20 act-1 points per meter step; steep).

### 6.5 New watchlists from this pass

- **Garment uptime permanence**: at meter 10 the Garment can approach
  always-on in long fights — a permanent multiplier wearing a Burst's
  clothes. Curve exponents stay flat (0.18/-0.40/0.02) and pressure
  deltas ~0.00, so no runaway yet; re-check after any further Charge dose.
- **Multiplicative-read cell now hot**: riptide_strike + Garment + nereids
  all read the same uncapped bank. Fuel-bounded (Charge costs cards), but
  this is the §2.1 anti-stall geometry's live test.
- Priest pilot regret 15.1% (was 7.7% at v0.1) — the pilot may be
  misplaying the reader/burn ordering; instrument before tuning cards.
- Suite note: full root suite is green for everything mine; ONE red
  belongs to the concurrent session's in-flight gen_klee_cards.py edit
  (test_roster_codegen vs their modified generator + regenerated Furina
  .cs files) — not touched, theirs to land.

## 7. v0.2 watchlists carried forward

- Hydro convergence (surging_shoal reprice raises its weight — P2 interacts).
- Multiplicative-read cell (nereids × future sub-Rare readers — P1 must
  keep the Rare read premium or the watchlist cell goes hot).
- Conscript rare-fishing (Raiden now in pool; N5 says leave until sims say
  otherwise — none of the 0% is attributable to her).
- engine_closure noise (unchanged; commander's 972 candidate turns in the
  v0.1 battery remain report-only).
