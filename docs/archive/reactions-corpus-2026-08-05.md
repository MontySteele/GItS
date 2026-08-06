> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/reactions-corpus-2026-08-05.md` — new path: `docs/archive/reactions-corpus-2026-08-05.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Reactions corpus — 2026-08-05

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Last Call, Round Two, **Track H**: the measurement harvest for a future
reactions design session. Measurement only — no constant moved, no design
question answered here. Every number below is a count or a ratio of counts.

**World stamp (every row).** `RT7 / D14 / P3 / C4` — RUNTEMPLATE 7,
**DRAFTER_VERSION 14**, POLICY 3, CONSTANTS 4. D14 landed tonight and repaired
seven archetypes (`assist`, `commander`, `demolition`, `generic`, `priest`,
`salon`, `spark`); every cohort arm below overlaps at least one of them, so
**no row here is comparable to any pre-v14 number** and none is offered as one.
The tier 0 battery surface does not draft, so DRAFTER_VERSION is inert there
and is stamped only for provenance.

---

## ERRATUM — 2026-08-06: the battery surface's per-fight denominators

**Every per-fight rate in §3 and §3.1 as first published was measured per
RECORD, and the `gauntlet` encounter is two combats behind one record.** Track
O's instrument red-team (`docs/instrument-redteam-2026-08-05.md`, finding
**O-1** / slice 12, TOP-5 #1) found that `runner.run_battery` merges the
gauntlet's two stages into one `FightStats` while `aura_profile`,
`payoff_profile` and `summarize` divided their per-fight rates by
`len(all_stats)`. The numerator covered 3500 combats; the denominator counted
3000 records. At the **2026-08-06 sitting** O-1 was classified
unambiguous-correct-behavior — *per-combat denominators are correct* — and the
instrument was fixed (`FightStats.stages` / `.combats` /
`metrics.per_combat`, pinned by
`tier0/tests/test_pin_o1_combat_denominators.py`).

§3 and §3.1 below are **republished from a re-run of the same battery, same
arms, same `--fights 500`, same `seed = 20260805`**. The tables as first
published are preserved verbatim in **Appendix E**, and the original TSV
`docs/reactions-corpus-battery-2026-08-05.tsv` is **left untouched**; the
corrected run is written alongside it as
`docs/reactions-corpus-battery-2026-08-05-corrected.tsv` (one added column,
`n_combats`). The **cohort surface (§2, §2.1, §2.2, §4.1) is not affected and
was not re-run** — tier 0.5 records one `FightStats` per combat and never
merges stages.

What moved, and what did not:

- **Unmoved, byte-for-byte** across all 91 battery rows: every pooled count
  (`amp`, `splash`, `dot`, `reactions`, aura ops, aura applications, payoff
  evaluations and fires) and every ratio of sums (`pooled share` and its
  bootstrap CI). Verified row by row against the original TSV: **0
  differences.** The fix moved no fight — it is a denominator, not a sim
  change.
- **Moved**: `react/fight`, `aura ops/fight`, `aura apps/fight`, the per-fight
  **mean** share and its CI, and `fights_with_any_reaction_damage`. Gauntlet
  rows are exactly halved (every gauntlet fight in this battery reached stage
  2, so 500 records = 1000 combats); `all` rows are multiplied by 3000/3500,
  i.e. the published figures were **16.7% overstated**. Example, the arm O
  drove: `all` aura applications/fight **7.6987 published → 6.5989
  corrected**.

**Qualitative movements, stated and not re-graded** (interpretation still
belongs to the reactions design session):

1. **The gauntlet is not the aura-richest encounter.** In 9 of the 12 arms
   that applied any aura, `gauntlet` carried the largest aura
   applications/fight in the published table; corrected, it is the largest in
   **none of them**. On `klee/reaction_weighted` it moves from 12.026 (rank 1
   of 6) to 6.013 (rank 4 of 6, below `tank_boss` 9.486, `attrition` 9.45 and
   `swarm` 6.136). The same reordering happens in every arm — the gauntlet row
   was the only one carrying two combats' events on one record.
2. **The starved-fights figure is no longer erased.** `aura_starved_fights` is
   not a published column here, but it is the same instrument: on
   `klee/reaction_weighted` gauntlet it read 0.0000 and reads **0.0030**
   corrected, because a starved stage merged with a reacting stage recorded
   `reactions > 0`.
3. **The per-fight mean share moves UP on the reacting arms, not down** —
   `klee/reaction_weighted` `all` goes 0.1909 → 0.1975 — because the two
   gauntlet stages are each individually a fight, and averaging them
   separately weights them as two. It is the one moved column whose direction
   is not simply "smaller".

Nothing else in this document is restated, and no reading of these numbers is
revised here.

---

## 1. What was measured, and with what

Three instruments, all log-side, all report-only:

| instrument | what it counts | landed |
|---|---|---|
| D1 `metrics.reaction_share`, `tier05.reaction_telemetry` | reaction-attributable vs base damage, split `amp` / `splash` / `dot` | Track D (main `8daedb7`) |
| H1 `metrics.aura_profile` | aura-applying **op** resolutions, and aura **applications** by source and element | this track |
| H2 `metrics.payoff_profile` | conditional payoff-rider evaluations and fires, keyed by predicate | this track |

H1 and H2 are new. They read events the engine already emitted, plus two
emit-only additions: an `aura_op` row at each aura-verb op, and a `source` key
on `aura_applied`. `FightStats` is sim-local (the Py↔C# parity schema is
`understudy/soak.py`'s), so nothing here crosses that boundary. Pinned by
`tier0/tests/test_track_h_telemetry.py`, including a same-seed identity test:
the counters do not move a fight.

### Definitions, fixed here

- **amp** — the Vaporize/Melt multiplier's *delta* over the unamplified hit.
  The base hit belongs to a base op; only the uplift is the reaction's.
- **splash** — Overload's explosion, overkill-clamped at the emit site.
- **dot** — Electro-Charged ticking on an *enemy*. Not inside
  `total_damage_dealt`, so the denominator is widened for it.
- **pooled share** — `sum(reaction) / sum(all)` over the cell's fights. A
  6-damage fight does not weigh as much as a 300-damage one.
- **per-fight mean share** — the mean of per-fight shares. A different
  question; both are quoted because quoting one without saying which is
  unreadable.
- **aura ops** — resolutions of an aura-applying *verb* (`apply_aura`,
  `swirl`, `refresh_all_auras`). Counts the op, not its effect: an op that
  resolves into nothing still counts here.
- **aura applications** — `aura_applied` events, i.e. auras that actually
  landed, from any source (`hit`, `apply_aura_op`, `swirl_op`,
  `swirl_spread`).
- **payoff evaluated / fired** — evaluations of a payoff predicate and the
  subset that took the `then` branch. Evaluations, not plays: a card that
  repeats itself evaluates twice in one play.

### Track D caveat, carried forward unchanged

**`amp` over-reads on overkill and on blocked hits.** `amp_delta` is emitted
inside `reactions._react` as `out - damage`, *before* the hit is clamped
against the enemy's remaining HP and block in `effects.deal_damage_to_enemy`.
`splash` and `dot` are clamped at their emit sites; `amp` is not. The over-read
is therefore largest on decks that amplify into low-HP or blocked bodies. This
is **pre-existing** (it predates Track D, which preserved it deliberately
rather than silently redefining the ratified A6 input) and Track H preserves it
too. Any amp figure below is an upper bound on landed amp damage.

Two further limits, said plainly:

- This is a share of **damage**. Superconduct's Vulnerable, Frozen's halved
  action, Crystallize's block and Courtroom Drama's stand are reactions doing
  work that no column here counts.
- tier 0 models **one seat**. Nothing below is a co-op measurement.

## 2. Cohort surface — tier 0.5, 3 acts, `--realistic`

`n = 3000 runs` per arm, `seed = 20260805`, route `hunter`, policy `assigned`,
all registered acts, relics + potions on. Fight counts vary by arm because a
run's length varies (deaths end runs early). CI method: 95% **percentile
bootstrap** over fights, 2000 resamples, on the pooled share (a ratio of sums,
so a ratio bootstrap resampling the (numerator, denominator) pair per fight);
95% **normal approximation**, mean ± 1.96 SE, on the per-fight mean. Fights
within a run share a deck, so the fight-level bootstrap is mildly
anticonservative on this surface — labelled, not silently widened.

| arm | n fights | pooled share [95% CI] | per-fight mean [95% CI] | amp | splash | dot | react/fight | aura ops/fight | aura apps/fight | auras wasted | reaction payoff fired/eval | aura payoff fired/eval |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `klee/demolition` | 46206 | 0.0583 [0.0577, 0.0589] | 0.0589 [0.0584, 0.0594] | 207965 | 94988 | 2891 | 1.9627 | 0.7807 | 3.8401 | 9427 | 6319/12891 (49%) | 304/4206 (7%) |
| `klee/spark` | 43567 | 0.0658 [0.0652, 0.0665] | 0.0650 [0.0645, 0.0656] | 215584 | 96048 | 3312 | 2.1363 | 0.8397 | 4.0638 | 9949 | 7853/14317 (55%) | 283/4254 (7%) |
| `klee/reaction` | 47930 | 0.1147 [0.1138, 0.1157] | 0.1122 [0.1114, 0.1130] | 446233 | 179136 | 9829 | 3.3343 | 1.6407 | 5.2345 | 11104 | 16062/31446 (51%) | 1017/8575 (12%) |
| `furina/salon` | 38814 | 0.0429 [0.0423, 0.0435] | 0.0426 [0.0420, 0.0432] | 137099 | 11301 | 38808 | 2.5949 | 2.097 | 4.6847 | 26559 | 57/80 (71%) | absent |
| `furina/spotlight` | 35684 | 0.0674 [0.0666, 0.0682] | 0.0615 [0.0607, 0.0623] | 177631 | 34539 | 34432 | 2.83 | 2.7604 | 4.7624 | 24251 | 374/552 (68%) | absent |
| `furina/fanfare` | 33900 | 0.0492 [0.0485, 0.0498] | 0.0467 [0.0460, 0.0474] | 127156 | 20929 | 21623 | 2.3528 | 2.0253 | 4.3828 | 26910 | 46/82 (56%) | absent |
| `kokomi/commander` | 32099 | 0.0489 [0.0481, 0.0497] | 0.0399 [0.0393, 0.0406] | 34770 | 3275 | 121782 | 1.202 | 0.4144 | 3.3961 | 18528 | absent | absent |
| `kokomi/priest` | 28439 | 0.0201 [0.0195, 0.0208] | 0.0160 [0.0155, 0.0165] | 14174 | 385 | 41159 | 0.477 | 0.1951 | 2.8276 | 17485 | absent | absent |
| `kokomi/assist` | 24375 | 0.0275 [0.0267, 0.0284] | 0.0207 [0.0201, 0.0213] | 13194 | 567 | 45886 | 0.6061 | 0.2606 | 3.0029 | 16510 | absent | absent |
| `ref_ironclad/generic` | 46683 | 0.0005 [0.0004, 0.0005] | 0.0004 [0.0003, 0.0004] | 227 | 1000 | 1507 | 0.0127 | 0.1365 | 0.3194 | 7701 | absent | absent |

`absent` in a payoff column means **no card carrying that predicate was ever
evaluated** in the arm — which is not the same as "evaluated and never fired",
and the corpus keeps them apart on purpose (§5).

### 2.1 Cut by act

| arm | act | n fights | pooled share [95% CI] | amp | splash | dot | react/fight | aura ops/fight | aura apps/fight | reaction payoff fired/eval |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `klee/demolition` | 1 | 24236 | 0.0539 [0.0534, 0.0545] | 92743 | 12662 | 285 | 1.3697 | 0.3189 | 2.9041 | 2250/4839 (46%) |
| `klee/demolition` | 2 | 17358 | 0.0596 [0.0587, 0.0605] | 87374 | 54396 | 1637 | 2.4465 | 1.1816 | 4.7183 | 3157/6357 (50%) |
| `klee/demolition` | 3 | 4612 | 0.0644 [0.0627, 0.0661] | 27848 | 27930 | 969 | 3.2578 | 1.699 | 5.4538 | 912/1695 (54%) |
| `klee/spark` | 1 | 23939 | 0.0577 [0.0572, 0.0583] | 97710 | 13453 | 254 | 1.4857 | 0.3603 | 3.0325 | 2941/5539 (53%) |
| `klee/spark` | 2 | 16193 | 0.0691 [0.0680, 0.0702] | 93136 | 57336 | 1892 | 2.7587 | 1.3146 | 5.1661 | 3963/7149 (55%) |
| `klee/spark` | 3 | 3435 | 0.0788 [0.0764, 0.0812] | 24738 | 25259 | 1166 | 3.736 | 1.9415 | 6.0544 | 949/1629 (58%) |
| `klee/reaction` | 1 | 24483 | 0.0959 [0.0950, 0.0969] | 143467 | 45838 | 1754 | 2.4444 | 0.9779 | 3.9442 | 7180/12840 (56%) |
| `klee/reaction` | 2 | 18175 | 0.1257 [0.1242, 0.1272] | 218885 | 94046 | 5509 | 4.0958 | 2.2277 | 6.4496 | 6911/14645 (47%) |
| `klee/reaction` | 3 | 5272 | 0.1241 [0.1214, 0.1270] | 83881 | 39252 | 2566 | 4.8418 | 2.6954 | 7.0374 | 1971/3961 (50%) |
| `furina/salon` | 1 | 21655 | 0.0440 [0.0431, 0.0448] | 60394 | 6054 | 8495 | 2.1375 | 1.6636 | 4.0161 | 4/6 (67%) |
| `furina/salon` | 2 | 12690 | 0.0448 [0.0438, 0.0458] | 57158 | 4267 | 19879 | 3.1493 | 2.6013 | 5.5756 | 24/39 (62%) |
| `furina/salon` | 3 | 4469 | 0.0368 [0.0353, 0.0382] | 19547 | 980 | 10434 | 3.2374 | 2.765 | 5.3949 | 29/35 (83%) |
| `furina/spotlight` | 1 | 21979 | 0.0583 [0.0572, 0.0593] | 77110 | 15231 | 8691 | 2.1971 | 2.0665 | 3.9773 | 44/62 (71%) |
| `furina/spotlight` | 2 | 11680 | 0.0763 [0.0749, 0.0777] | 83018 | 16568 | 20505 | 3.7846 | 3.8041 | 6.0203 | 237/349 (68%) |
| `furina/spotlight` | 3 | 2025 | 0.0729 [0.0698, 0.0758] | 17503 | 2740 | 5236 | 4.1936 | 4.2716 | 6.0286 | 93/141 (66%) |
| `furina/fanfare` | 1 | 21045 | 0.0460 [0.0451, 0.0469] | 59142 | 10251 | 6371 | 2.0019 | 1.7595 | 3.9271 | 5/9 (56%) |
| `furina/fanfare` | 2 | 11176 | 0.0529 [0.0517, 0.0539] | 59438 | 9221 | 11889 | 2.9126 | 2.4532 | 5.1696 | 31/57 (54%) |
| `furina/fanfare` | 3 | 1679 | 0.0478 [0.0453, 0.0505] | 8576 | 1457 | 3363 | 3.0244 | 2.5086 | 4.8582 | 10/16 (62%) |
| `kokomi/commander` | 1 | 19807 | 0.0357 [0.0348, 0.0366] | 13083 | 734 | 40595 | 0.7359 | 0.2331 | 2.7312 | absent |
| `kokomi/commander` | 2 | 10312 | 0.0593 [0.0580, 0.0606] | 17670 | 2010 | 63278 | 1.8816 | 0.6854 | 4.4617 | absent |
| `kokomi/commander` | 3 | 1980 | 0.0646 [0.0615, 0.0677] | 4017 | 531 | 17909 | 2.3253 | 0.8167 | 4.498 | absent |
| `kokomi/priest` | 1 | 18745 | 0.0146 [0.0138, 0.0153] | 6245 | 126 | 14149 | 0.2855 | 0.1116 | 2.43 | absent |
| `kokomi/priest` | 2 | 8218 | 0.0255 [0.0244, 0.0266] | 6573 | 199 | 21137 | 0.8065 | 0.3402 | 3.6031 | absent |
| `kokomi/priest` | 3 | 1476 | 0.0274 [0.0249, 0.0300] | 1356 | 60 | 5873 | 1.0745 | 0.4478 | 3.5596 | absent |
| `kokomi/assist` | 1 | 17778 | 0.0189 [0.0180, 0.0197] | 6310 | 214 | 18260 | 0.3745 | 0.1614 | 2.6177 | absent |
| `kokomi/assist` | 2 | 6092 | 0.0396 [0.0379, 0.0414] | 6521 | 323 | 23571 | 1.1815 | 0.5163 | 4.0266 | absent |
| `kokomi/assist` | 3 | 505 | 0.0508 [0.0445, 0.0573] | 363 | 30 | 4055 | 1.8178 | 0.6693 | 4.2119 | absent |
| `ref_ironclad/generic` | 1 | 22389 | 0.0002 [0.0001, 0.0003] | 21 | 231 | 145 | 0.0042 | 0.0653 | 0.1919 | absent |
| `ref_ironclad/generic` | 2 | 17771 | 0.0006 [0.0005, 0.0006] | 162 | 547 | 771 | 0.0188 | 0.1973 | 0.4415 | absent |
| `ref_ironclad/generic` | 3 | 6523 | 0.0007 [0.0005, 0.0008] | 44 | 222 | 591 | 0.0251 | 0.2151 | 0.424 | absent |

### 2.2 Aura provenance and reaction mix (cohort, pooled over all acts)

| arm | aura ops | applications by source | applications by element | reactions by name |
|---|---|---|---|---|
| `klee/demolition` | apply_aura=19605;refresh_all_auras=826;swirl=15644 | apply_aura_op=5979;hit=154006;swirl_spread=17452 | cryo=4530;electro=3367;hydro=7909;pyro=161631 | electrocharged=456;frozen=518;melt=27715;overload=12243;superconduct=288;swirl=12882;vaporize=36585 |
| `klee/spark` | apply_aura=19909;refresh_all_auras=853;swirl=15820 | apply_aura_op=5773;hit=153328;swirl_spread=17945 | cryo=4199;electro=3523;hydro=7735;pyro=161589 | electrocharged=524;frozen=501;melt=28389;overload=12340;superconduct=269;swirl=13328;vaporize=37720 |
| `klee/reaction` | apply_aura=47272;refresh_all_auras=887;swirl=30481 | apply_aura_op=15772;hit=199199;swirl_spread=35918 | cryo=12750;electro=8087;hydro=20565;pyro=209487 | electrocharged=1655;frozen=2531;melt=46007;overload=22797;superconduct=1043;swirl=25277;vaporize=60504 |
| `furina/salon` | apply_aura=30507;refresh_all_auras=4003;swirl=46882 | apply_aura_op=14046;hit=122925;swirl_spread=44861 | cryo=33476;electro=6038;hydro=109054;pyro=33264 | electrocharged=6367;frozen=29999;melt=4182;overload=1299;superconduct=1510;swirl=30693;vaporize=26670 |
| `furina/spotlight` | apply_aura=37209;refresh_all_auras=1202;swirl=60091 | apply_aura_op=19933;hit=100608;swirl_spread=49401 | cryo=44285;electro=12682;hydro=60535;pyro=52440 | electrocharged=5789;frozen=19773;melt=10464;overload=4331;superconduct=3961;swirl=35473;vaporize=21196 |
| `furina/fanfare` | apply_aura=17632;refresh_all_auras=1724;swirl=49302 | apply_aura_op=9279;hit=99616;swirl_spread=39683 | cryo=40100;electro=8590;hydro=52793;pyro=47095 | electrocharged=3763;frozen=16569;melt=8657;overload=2636;superconduct=2546;swirl=28172;vaporize=17417 |
| `kokomi/commander` | apply_aura=5975;swirl=7327 | apply_aura_op=1953;hit=99242;swirl_spread=7817 | cryo=623;electro=9177;hydro=96120;pyro=3092 | electrocharged=22361;frozen=2430;melt=39;overload=389;superconduct=95;swirl=5757;vaporize=7511 |
| `kokomi/priest` | apply_aura=3468;swirl=2081 | apply_aura_op=1016;hit=76975;swirl_spread=2424 | cryo=277;electro=2429;hydro=76510;pyro=1199 | electrocharged=7161;frozen=1419;melt=16;overload=48;superconduct=9;swirl=1774;vaporize=3139 |
| `kokomi/assist` | apply_aura=4099;swirl=2253 | apply_aura_op=1194;hit=69341;swirl_spread=2660 | cryo=381;electro=2792;hydro=68763;pyro=1259 | electrocharged=7819;frozen=1775;melt=7;overload=68;superconduct=32;swirl=1913;vaporize=3160 |
| `ref_ironclad/generic` | apply_aura=4559;swirl=1812 | apply_aura_op=4160;hit=10621;swirl_spread=128 | electro=5439;hydro=4226;pyro=5244 | electrocharged=225;overload=129;swirl=93;vaporize=146 |

## 3. Battery surface — tier 0, frozen 6-encounter battery

`n = 500 fights per encounter` (3000 per arm), `seed = 20260805`, authored
decks, each character's own archetype pilot. Same CI method as §2; fights here
are independent, so the bootstrap is not anticonservative on this surface.

**Corrected 2026-08-06 per the erratum above (O-1).** The `n` column now reads
`combats (records)`: `gauntlet` is a two-stage encounter, so 500 attempts of it
are 1000 combats, and 3000 attempts per arm are 3500 combats. Every `/fight`
column below divides by COMBATS. The counts and the pooled share are unchanged
from the 2026-08-05 publication; the pre-correction table is Appendix E.

| arm (authored deck / pilot) | n combats (records) | pooled share [95% CI] | per-fight mean [95% CI] | amp | splash | dot | react/fight | aura ops/fight | aura apps/fight | reaction payoff | aura payoff |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `klee/starter` / generic | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 2.5229 | absent | absent |
| `klee/demolition_weighted` / demolition | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 2.492 | absent | absent |
| `klee/spark_weighted` / spark | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 2.786 | absent | absent |
| `klee/reaction_weighted` / reaction | 3500 (3000) | 0.1811 [0.1779, 0.1842] | 0.1975 [0.1933, 0.2018] | 19755 | 53225 | 1281 | 4.7549 | 1.5403 | 6.5989 | 218/5031 (4%) | 249/4727 (5%) |
| `furina/starter` / generic | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 1.3357 | absent | absent |
| `furina/salon_weighted` / salon | 3500 (3000) | 0.0018 [0.0014, 0.0022] | 0.0013 [0.0010, 0.0016] | 148 | 0 | 595 | 0.1606 | 0.8389 | 1.9783 | absent | absent |
| `furina/spotlight_weighted` / spotlight | 3500 (3000) | 0.0955 [0.0929, 0.0983] | 0.0876 [0.0848, 0.0904] | 30800 | 5547 | 2319 | 2.8197 | 2.1397 | 5.698 | 159/244 (65%) | absent |
| `furina/fanfare_weighted` / fanfare | 3500 (3000) | 0.0005 [0.0003, 0.0007] | 0.0003 [0.0002, 0.0005] | 60 | 0 | 133 | 0.0391 | 0.1034 | 0.4837 | absent | absent |
| `kokomi/starter` / generic | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 3.0514 | absent | absent |
| `kokomi/commander_weighted` / commander | 3500 (3000) | 0.0661 [0.0640, 0.0682] | 0.0569 [0.0548, 0.0590] | 4228 | 1076 | 21807 | 1.8251 | 0.4363 | 4.5383 | absent | absent |
| `kokomi/priest_weighted` / priest | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 3.0971 | absent | absent |
| `kokomi/assist_weighted` / assist | 3500 (3000) | 0.0065 [0.0058, 0.0072] | 0.0053 [0.0047, 0.0058] | 404 | 0 | 2140 | 0.1771 | 0.0434 | 3.5869 | absent | absent |
| `ref_ironclad/starter` / generic | 3500 (3000) | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | absent | absent |

Seven battery arms recorded **zero reactions** across 3000 fights (3500
combats) each — `klee/starter`, `klee/demolition_weighted`,
`klee/spark_weighted`, `furina/starter`, `kokomi/starter`,
`kokomi/priest_weighted`, `ref_ironclad/starter`. All seven also recorded zero
aura *ops*. Six of the seven still put auras up (**1.34–3.10**
applications/fight — as published, on record denominators, 1.56–3.61 — every
one of them sourced `hit`); `ref_ironclad/starter` applied none at all.

### 3.1 Cut by encounter (arms with any reaction or payoff activity)

Corrected 2026-08-06 (O-1); `n` is `combats (records)`, and only the `gauntlet`
rows differ from the 2026-08-05 publication, on the `/fight` columns and on
`n`. Pre-correction table: Appendix E.

| arm | encounter | n | pooled share [95% CI] | amp | splash | dot | react/fight | aura ops/fight | aura apps/fight | reaction payoff | aura payoff |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| `klee/reaction_weighted` | attrition | 500 (500) | 0.2287 [0.2229, 0.2345] | 3782 | 13082 | 289 | 7.246 | 2.19 | 9.45 | 35/1034 (3%) | 44/983 (4%) |
| `klee/reaction_weighted` | burst_check | 500 (500) | 0.1482 [0.1428, 0.1538] | 1654 | 2793 | 0 | 2.474 | 0.688 | 3.232 | 20/404 (5%) | 14/372 (4%) |
| `klee/reaction_weighted` | gauntlet | 1000 (500) | 0.2027 [0.1953, 0.2101] | 4644 | 13814 | 295 | 3.731 | 1.281 | 6.013 | 66/1173 (6%) | 78/1113 (7%) |
| `klee/reaction_weighted` | punisher | 500 (500) | 0.1493 [0.1453, 0.1535] | 2962 | 5393 | 232 | 5.08 | 1.784 | 5.862 | 39/784 (5%) | 35/715 (5%) |
| `klee/reaction_weighted` | swarm | 500 (500) | 0.2903 [0.2737, 0.3068] | 1640 | 8459 | 61 | 2.368 | 0.732 | 6.136 | 23/390 (6%) | 35/405 (9%) |
| `klee/reaction_weighted` | tank_boss | 500 (500) | 0.1263 [0.1234, 0.1291] | 5073 | 9684 | 404 | 8.654 | 2.826 | 9.486 | 35/1246 (3%) | 43/1139 (4%) |
| `furina/salon_weighted` | attrition | 500 (500) | 0.0040 [0.0025, 0.0058] | 29 | 0 | 274 | 0.38 | 1.266 | 3.752 | absent | absent |
| `furina/salon_weighted` | burst_check | 500 (500) | 0.0003 [0.0000, 0.0007] | 0 | 0 | 8 | 0.034 | 0.646 | 1.218 | absent | absent |
| `furina/salon_weighted` | gauntlet | 1000 (500) | 0.0006 [0.0003, 0.0009] | 24 | 0 | 30 | 0.072 | 0.585 | 1.808 | absent | absent |
| `furina/salon_weighted` | punisher | 500 (500) | 0.0011 [0.0006, 0.0016] | 27 | 0 | 34 | 0.14 | 0.884 | 1.32 | absent | absent |
| `furina/salon_weighted` | swarm | 500 (500) | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.006 | 0.3 | 2.29 | absent | absent |
| `furina/salon_weighted` | tank_boss | 500 (500) | 0.0026 [0.0019, 0.0035] | 68 | 0 | 249 | 0.42 | 1.606 | 1.652 | absent | absent |
| `furina/spotlight_weighted` | attrition | 500 (500) | 0.1232 [0.1166, 0.1295] | 6779 | 1898 | 565 | 5.358 | 3.728 | 9.142 | 55/82 (67%) | absent |
| `furina/spotlight_weighted` | burst_check | 500 (500) | 0.0950 [0.0879, 0.1019] | 2535 | 245 | 71 | 1.522 | 1.19 | 2.624 | 8/17 (47%) | absent |
| `furina/spotlight_weighted` | gauntlet | 1000 (500) | 0.0769 [0.0713, 0.0825] | 5597 | 1049 | 334 | 1.685 | 1.481 | 4.981 | 25/34 (74%) | absent |
| `furina/spotlight_weighted` | punisher | 500 (500) | 0.0914 [0.0858, 0.0970] | 4243 | 673 | 288 | 2.782 | 2.26 | 4.546 | 20/27 (74%) | absent |
| `furina/spotlight_weighted` | swarm | 500 (500) | 0.0545 [0.0451, 0.0648] | 1471 | 424 | 12 | 0.646 | 0.722 | 5.478 | 4/8 (50%) | absent |
| `furina/spotlight_weighted` | tank_boss | 500 (500) | 0.1065 [0.1014, 0.1117] | 10175 | 1258 | 1049 | 6.06 | 4.116 | 8.134 | 47/76 (62%) | absent |
| `furina/fanfare_weighted` | attrition | 500 (500) | 0.0008 [0.0003, 0.0014] | 13 | 0 | 48 | 0.09 | 0.16 | 1.186 | absent | absent |
| `furina/fanfare_weighted` | burst_check | 500 (500) | 0.0000 [0.0000, 0.0001] | 1 | 0 | 0 | 0.016 | 0.062 | 0.318 | absent | absent |
| `furina/fanfare_weighted` | gauntlet | 1000 (500) | 0.0002 [0.0000, 0.0005] | 6 | 0 | 11 | 0.012 | 0.068 | 0.274 | absent | absent |
| `furina/fanfare_weighted` | punisher | 500 (500) | 0.0002 [0.0000, 0.0005] | 6 | 0 | 7 | 0.018 | 0.082 | 0.296 | absent | absent |
| `furina/fanfare_weighted` | swarm | 500 (500) | 0.0001 [0.0000, 0.0003] | 0 | 0 | 4 | 0.006 | 0.052 | 0.248 | absent | absent |
| `furina/fanfare_weighted` | tank_boss | 500 (500) | 0.0008 [0.0004, 0.0013] | 34 | 0 | 63 | 0.12 | 0.232 | 0.79 | absent | absent |
| `kokomi/commander_weighted` | attrition | 500 (500) | 0.0866 [0.0815, 0.0918] | 908 | 216 | 5369 | 2.846 | 0.584 | 5.886 | absent | absent |
| `kokomi/commander_weighted` | burst_check | 500 (500) | 0.0240 [0.0204, 0.0277] | 359 | 72 | 290 | 1.198 | 0.318 | 2.184 | absent | absent |
| `kokomi/commander_weighted` | gauntlet | 1000 (500) | 0.0579 [0.0535, 0.0622] | 889 | 346 | 4117 | 1.506 | 0.403 | 4.93 | absent | absent |
| `kokomi/commander_weighted` | punisher | 500 (500) | 0.0728 [0.0679, 0.0778] | 578 | 96 | 3514 | 1.63 | 0.436 | 2.826 | absent | absent |
| `kokomi/commander_weighted` | swarm | 500 (500) | 0.0324 [0.0265, 0.0387] | 317 | 244 | 573 | 1.384 | 0.372 | 7.016 | absent | absent |
| `kokomi/commander_weighted` | tank_boss | 500 (500) | 0.0769 [0.0726, 0.0812] | 1177 | 102 | 7944 | 2.706 | 0.538 | 3.996 | absent | absent |
| `kokomi/assist_weighted` | attrition | 500 (500) | 0.0134 [0.0113, 0.0157] | 179 | 0 | 824 | 0.414 | 0.072 | 4.04 | absent | absent |
| `kokomi/assist_weighted` | burst_check | 500 (500) | 0.0035 [0.0022, 0.0051] | 30 | 0 | 76 | 0.13 | 0.042 | 1.542 | absent | absent |
| `kokomi/assist_weighted` | gauntlet | 1000 (500) | 0.0034 [0.0023, 0.0048] | 60 | 0 | 238 | 0.108 | 0.032 | 4.13 | absent | absent |
| `kokomi/assist_weighted` | punisher | 500 (500) | 0.0040 [0.0025, 0.0056] | 18 | 0 | 194 | 0.086 | 0.024 | 2.552 | absent | absent |
| `kokomi/assist_weighted` | swarm | 500 (500) | 0.0026 [0.0015, 0.0041] | 38 | 0 | 53 | 0.132 | 0.04 | 5.662 | absent | absent |
| `kokomi/assist_weighted` | tank_boss | 500 (500) | 0.0073 [0.0060, 0.0088] | 79 | 0 | 755 | 0.262 | 0.062 | 3.052 | absent | absent |

## 4. Payoff-op triggers — the audit's ≈0 claim, with counts

The 2026-07-26 audit's standing claim is that reaction payoff ops are unused,
at roughly zero triggers. The predicate vocabulary that constitutes them:

- reaction payoff: `reaction_triggered_by_this`, `reaction_triggered_this_turn`
- aura payoff: `target_has_nonpyro_aura`

Carried by five loaded cards: `boom_goes_the_dynamite`, `perfect_timing`,
`prune_witch_hunt` (`reaction_triggered_by_this`); `audience_participation`,
`chevreuse_vanguards_valor` (`reaction_triggered_this_turn`); `sizzle`,
`elemental_ecstasy` (`target_has_nonpyro_aura`).

The counts, cohort surface, n=3000 runs/arm:

| predicate | evaluations | fires | arms where it was evaluated |
|---|---:|---:|---|
| `reaction_triggered_by_this` | 59 368 | 30 711 | klee ×3, furina ×3 |
| `reaction_triggered_this_turn` | 0 | 0 | none |
| `target_has_nonpyro_aura` | 17 035 | 1 604 | klee ×3 |

Battery surface, n=3000 fights (3500 combats)/arm — these are COUNTS and are
unmoved by the O-1 correction: `reaction_triggered_by_this` 5275
evaluations / 377 fires (klee `reaction_weighted`, furina
`spotlight_weighted`); `target_has_nonpyro_aura` 4727 / 249 (klee
`reaction_weighted`); `reaction_triggered_this_turn` 0 / 0.

### 4.1 Draft reach of the payoff cards (cohort, runs out of 3000 whose deck held the card)

| arm | payoff cards drafted |
|---|---|
| `klee/demolition` | reaction_triggered_by_this:boom_goes_the_dynamite=229;reaction_triggered_by_this:perfect_timing=190;reaction_triggered_by_this:prune_witch_hunt=1215;reaction_triggered_this_turn:chevreuse_vanguards_valor=5;target_has_nonpyro_aura:elemental_ecstasy=595;target_has_nonpyro_aura:sizzle=272 |
| `klee/spark` | reaction_triggered_by_this:boom_goes_the_dynamite=222;reaction_triggered_by_this:perfect_timing=170;reaction_triggered_by_this:prune_witch_hunt=1213;reaction_triggered_this_turn:chevreuse_vanguards_valor=1;target_has_nonpyro_aura:elemental_ecstasy=525;target_has_nonpyro_aura:sizzle=238 |
| `klee/reaction` | reaction_triggered_by_this:boom_goes_the_dynamite=214;reaction_triggered_by_this:perfect_timing=155;reaction_triggered_by_this:prune_witch_hunt=947;reaction_triggered_this_turn:chevreuse_vanguards_valor=25;target_has_nonpyro_aura:elemental_ecstasy=426;target_has_nonpyro_aura:sizzle=222 |
| `furina/salon` | reaction_triggered_this_turn:audience_participation=290;reaction_triggered_this_turn:chevreuse_vanguards_valor=19 |
| `furina/spotlight` | reaction_triggered_this_turn:audience_participation=222;reaction_triggered_this_turn:chevreuse_vanguards_valor=100 |
| `furina/fanfare` | reaction_triggered_this_turn:audience_participation=247 |
| `kokomi/commander` | reaction_triggered_this_turn:chevreuse_vanguards_valor=1 |
| `kokomi/priest` | none |
| `kokomi/assist` | reaction_triggered_this_turn:chevreuse_vanguards_valor=1 |
| `ref_ironclad/generic` | none |

## 5. Instrument gaps found

1. **`reaction_triggered_this_turn` evaluated exactly zero times on both
   surfaces, and it is not a draft-reach failure.** Its two carriers *are*
   drafted at measurable rates — `audience_participation` in 222–290 of 3000
   Furina runs per arm, `chevreuse_vanguards_valor` in up to 100 — and the
   predicate still never evaluated once across 108 398 Furina cohort fights.
   Isolated by direct probe: a deck of ten `audience_participation` over 50
   `punisher` fights played it **0 times**. The mechanism is in
   `tier0/pilot/policy.py::_active_effects`, which yields nothing for a
   conditional whose predicate it does not recognise; both reaction predicates
   are on that unrecognised list ("mid-resolution predicates deliberately keep
   their historic top-level-only valuation"). A card whose entire body sits
   inside such a conditional therefore scores zero and is never played.
   `reaction_triggered_by_this` escapes this only because its three carriers
   also print top-level damage. **Consequence for reading this corpus: the
   zero in the `reaction_triggered_this_turn` row is a measurement of the
   pilot, not of the predicate.**
2. **`aura_ops` and `aura_applications` cannot be joined per card.** The
   `aura_op` event carries the card id, but the counters on `FightStats` are
   pooled by op name only. A per-card cut needs the raw log
   (`tier05.conditional_telemetry` reads it that way for conditionals).
3. **No non-damage reaction payoff is counted anywhere.** Superconduct's
   Vulnerable, Frozen's halved action, Crystallize's block and Courtroom
   Drama's stand have no counter on any surface. An arm can read 0.02 share
   and still be winning fights on reactions.
4. **Swirl's spread re-applies to the swirled target itself.** Two enemies,
   one swirl → two `swirl_spread` applications. Pinned as observed behaviour
   in `test_swirl_spread_is_attributed_to_swirl_and_not_to_the_hit`; whether
   the re-application is intended is not a question this track opens.
5. **The `amp` over-read (§1) is unquantified.** Nothing in the corpus
   measures how much of the amp column would survive clamping, because the
   clamped counterfactual is not emitted.

## 6. Regeneration

Raw per-fight corpora are **not** committed: the repo has no convention for
storing them (no per-fight CSV is tracked anywhere; the curated-table
convention is `docs/*.tsv`, as in `docs/role-tempo-review.tsv` and
`docs/s7-divergences.tsv`). The two aggregate tables follow that convention and
the exact commands that produce them are below. Both are deterministic
functions of their seeds.

```sh
# cohort surface -> docs/reactions-corpus-cohort-2026-08-05.tsv
PYTHONPATH=. python -m tier05.exp_reactions_corpus --cohort \
    --runs 3000 --seed 20260805 --jobs 0 \
    --tsv docs/reactions-corpus-cohort-2026-08-05.tsv

# battery surface, as published 2026-08-05 (record denominators, superseded;
# the file is kept as it was written and is NOT regenerated by this command
# any more -- the instrument now denominates per combat)
#   docs/reactions-corpus-battery-2026-08-05.tsv
#
# battery surface, corrected 2026-08-06 (O-1, per-combat denominators)
# -> docs/reactions-corpus-battery-2026-08-05-corrected.tsv
PYTHONPATH=. python -m tier05.exp_reactions_corpus --battery \
    --fights 500 --seed 20260805 \
    --tsv docs/reactions-corpus-battery-2026-08-05-corrected.tsv

# the same counters on any single battery config, printed
PYTHONPATH=. python -m tier0.harness.runner --character klee \
    --deck reaction_weighted --pilot reaction --fights 500 \
    --reaction-share --aura-payoff
```

The bootstrap runs on its own dedicated RNG stream — one generator per row,
seeded `BOOTSTRAP_SEED (8_050_000) + 1000 * arm_index (+ cut)` — constructed
after every fight in the arm has resolved. It draws nothing from
`CombatState.rng` and cannot perturb a fight.

---

## Appendix E — §3 and §3.1 exactly as published on 2026-08-05

Preserved unaltered for the paper trail. **Superseded** by the corrected
tables above: every `/fight` column here divides by RECORDS, so each `gauntlet`
row and each `all` row counts two combats as one fight (O-1; see the erratum at
the top of this document). The counts, the pooled shares and their CIs are
identical in both versions. The TSV these were written from is
`docs/reactions-corpus-battery-2026-08-05.tsv`, also preserved unaltered.

### E.1 — §3 as published

| arm (authored deck / pilot) | n fights | pooled share [95% CI] | per-fight mean [95% CI] | amp | splash | dot | react/fight | aura ops/fight | aura apps/fight | reaction payoff | aura payoff |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `klee/starter` / generic | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 2.9433 | absent | absent |
| `klee/demolition_weighted` / demolition | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 2.9073 | absent | absent |
| `klee/spark_weighted` / spark | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 3.2503 | absent | absent |
| `klee/reaction_weighted` / reaction | 3000 | 0.1811 [0.1779, 0.1842] | 0.1909 [0.1870, 0.1949] | 19755 | 53225 | 1281 | 5.5473 | 1.797 | 7.6987 | 218/5031 (4%) | 249/4727 (5%) |
| `furina/starter` / generic | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 1.5583 | absent | absent |
| `furina/salon_weighted` / salon | 3000 | 0.0018 [0.0014, 0.0022] | 0.0014 [0.0011, 0.0018] | 148 | 0 | 595 | 0.1873 | 0.9787 | 2.308 | absent | absent |
| `furina/spotlight_weighted` / spotlight | 3000 | 0.0955 [0.0929, 0.0983] | 0.0908 [0.0880, 0.0937] | 30800 | 5547 | 2319 | 3.2897 | 2.4963 | 6.6477 | 159/244 (65%) | absent |
| `furina/fanfare_weighted` / fanfare | 3000 | 0.0005 [0.0003, 0.0007] | 0.0004 [0.0002, 0.0005] | 60 | 0 | 133 | 0.0457 | 0.1207 | 0.5643 | absent | absent |
| `kokomi/starter` / generic | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 3.56 | absent | absent |
| `kokomi/commander_weighted` / commander | 3000 | 0.0661 [0.0640, 0.0682] | 0.0584 [0.0563, 0.0606] | 4228 | 1076 | 21807 | 2.1293 | 0.509 | 5.2947 | absent | absent |
| `kokomi/priest_weighted` / priest | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 3.6133 | absent | absent |
| `kokomi/assist_weighted` / assist | 3000 | 0.0065 [0.0058, 0.0072] | 0.0056 [0.0050, 0.0063] | 404 | 0 | 2140 | 0.2067 | 0.0507 | 4.1847 | absent | absent |
| `ref_ironclad/starter` / generic | 3000 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | absent | absent |

### E.2 — §3.1 as published

| arm | encounter | n | pooled share [95% CI] | amp | splash | dot | react/fight | aura ops/fight | aura apps/fight | reaction payoff | aura payoff |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| `klee/reaction_weighted` | attrition | 500 | 0.2287 [0.2229, 0.2345] | 3782 | 13082 | 289 | 7.246 | 2.19 | 9.45 | 35/1034 (3%) | 44/983 (4%) |
| `klee/reaction_weighted` | burst_check | 500 | 0.1482 [0.1428, 0.1538] | 1654 | 2793 | 0 | 2.474 | 0.688 | 3.232 | 20/404 (5%) | 14/372 (4%) |
| `klee/reaction_weighted` | gauntlet | 500 | 0.2027 [0.1953, 0.2101] | 4644 | 13814 | 295 | 7.462 | 2.562 | 12.026 | 66/1173 (6%) | 78/1113 (7%) |
| `klee/reaction_weighted` | punisher | 500 | 0.1493 [0.1453, 0.1535] | 2962 | 5393 | 232 | 5.08 | 1.784 | 5.862 | 39/784 (5%) | 35/715 (5%) |
| `klee/reaction_weighted` | swarm | 500 | 0.2903 [0.2737, 0.3068] | 1640 | 8459 | 61 | 2.368 | 0.732 | 6.136 | 23/390 (6%) | 35/405 (9%) |
| `klee/reaction_weighted` | tank_boss | 500 | 0.1263 [0.1234, 0.1291] | 5073 | 9684 | 404 | 8.654 | 2.826 | 9.486 | 35/1246 (3%) | 43/1139 (4%) |
| `furina/salon_weighted` | attrition | 500 | 0.0040 [0.0025, 0.0058] | 29 | 0 | 274 | 0.38 | 1.266 | 3.752 | absent | absent |
| `furina/salon_weighted` | burst_check | 500 | 0.0003 [0.0000, 0.0007] | 0 | 0 | 8 | 0.034 | 0.646 | 1.218 | absent | absent |
| `furina/salon_weighted` | gauntlet | 500 | 0.0006 [0.0003, 0.0009] | 24 | 0 | 30 | 0.144 | 1.17 | 3.616 | absent | absent |
| `furina/salon_weighted` | punisher | 500 | 0.0011 [0.0006, 0.0016] | 27 | 0 | 34 | 0.14 | 0.884 | 1.32 | absent | absent |
| `furina/salon_weighted` | swarm | 500 | 0.0000 [0.0000, 0.0000] | 0 | 0 | 0 | 0.006 | 0.3 | 2.29 | absent | absent |
| `furina/salon_weighted` | tank_boss | 500 | 0.0026 [0.0019, 0.0035] | 68 | 0 | 249 | 0.42 | 1.606 | 1.652 | absent | absent |
| `furina/spotlight_weighted` | attrition | 500 | 0.1232 [0.1166, 0.1295] | 6779 | 1898 | 565 | 5.358 | 3.728 | 9.142 | 55/82 (67%) | absent |
| `furina/spotlight_weighted` | burst_check | 500 | 0.0950 [0.0879, 0.1019] | 2535 | 245 | 71 | 1.522 | 1.19 | 2.624 | 8/17 (47%) | absent |
| `furina/spotlight_weighted` | gauntlet | 500 | 0.0769 [0.0713, 0.0825] | 5597 | 1049 | 334 | 3.37 | 2.962 | 9.962 | 25/34 (74%) | absent |
| `furina/spotlight_weighted` | punisher | 500 | 0.0914 [0.0858, 0.0970] | 4243 | 673 | 288 | 2.782 | 2.26 | 4.546 | 20/27 (74%) | absent |
| `furina/spotlight_weighted` | swarm | 500 | 0.0545 [0.0451, 0.0648] | 1471 | 424 | 12 | 0.646 | 0.722 | 5.478 | 4/8 (50%) | absent |
| `furina/spotlight_weighted` | tank_boss | 500 | 0.1065 [0.1014, 0.1117] | 10175 | 1258 | 1049 | 6.06 | 4.116 | 8.134 | 47/76 (62%) | absent |
| `furina/fanfare_weighted` | attrition | 500 | 0.0008 [0.0003, 0.0014] | 13 | 0 | 48 | 0.09 | 0.16 | 1.186 | absent | absent |
| `furina/fanfare_weighted` | burst_check | 500 | 0.0000 [0.0000, 0.0001] | 1 | 0 | 0 | 0.016 | 0.062 | 0.318 | absent | absent |
| `furina/fanfare_weighted` | gauntlet | 500 | 0.0002 [0.0000, 0.0005] | 6 | 0 | 11 | 0.024 | 0.136 | 0.548 | absent | absent |
| `furina/fanfare_weighted` | punisher | 500 | 0.0002 [0.0000, 0.0005] | 6 | 0 | 7 | 0.018 | 0.082 | 0.296 | absent | absent |
| `furina/fanfare_weighted` | swarm | 500 | 0.0001 [0.0000, 0.0003] | 0 | 0 | 4 | 0.006 | 0.052 | 0.248 | absent | absent |
| `furina/fanfare_weighted` | tank_boss | 500 | 0.0008 [0.0004, 0.0013] | 34 | 0 | 63 | 0.12 | 0.232 | 0.79 | absent | absent |
| `kokomi/commander_weighted` | attrition | 500 | 0.0866 [0.0815, 0.0918] | 908 | 216 | 5369 | 2.846 | 0.584 | 5.886 | absent | absent |
| `kokomi/commander_weighted` | burst_check | 500 | 0.0240 [0.0204, 0.0277] | 359 | 72 | 290 | 1.198 | 0.318 | 2.184 | absent | absent |
| `kokomi/commander_weighted` | gauntlet | 500 | 0.0579 [0.0535, 0.0622] | 889 | 346 | 4117 | 3.012 | 0.806 | 9.86 | absent | absent |
| `kokomi/commander_weighted` | punisher | 500 | 0.0728 [0.0679, 0.0778] | 578 | 96 | 3514 | 1.63 | 0.436 | 2.826 | absent | absent |
| `kokomi/commander_weighted` | swarm | 500 | 0.0324 [0.0265, 0.0387] | 317 | 244 | 573 | 1.384 | 0.372 | 7.016 | absent | absent |
| `kokomi/commander_weighted` | tank_boss | 500 | 0.0769 [0.0726, 0.0812] | 1177 | 102 | 7944 | 2.706 | 0.538 | 3.996 | absent | absent |
| `kokomi/assist_weighted` | attrition | 500 | 0.0134 [0.0113, 0.0157] | 179 | 0 | 824 | 0.414 | 0.072 | 4.04 | absent | absent |
| `kokomi/assist_weighted` | burst_check | 500 | 0.0035 [0.0022, 0.0051] | 30 | 0 | 76 | 0.13 | 0.042 | 1.542 | absent | absent |
| `kokomi/assist_weighted` | gauntlet | 500 | 0.0034 [0.0023, 0.0048] | 60 | 0 | 238 | 0.216 | 0.064 | 8.26 | absent | absent |
| `kokomi/assist_weighted` | punisher | 500 | 0.0040 [0.0025, 0.0056] | 18 | 0 | 194 | 0.086 | 0.024 | 2.552 | absent | absent |
| `kokomi/assist_weighted` | swarm | 500 | 0.0026 [0.0015, 0.0041] | 38 | 0 | 53 | 0.132 | 0.04 | 5.662 | absent | absent |
| `kokomi/assist_weighted` | tank_boss | 500 | 0.0073 [0.0060, 0.0088] | 79 | 0 | 755 | 0.262 | 0.062 | 3.052 | absent | absent |

---

Interpretation deferred to the reactions design session.
