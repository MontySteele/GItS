# EXPERIMENTS

Standing measurement law, plus pointers to the active registrations. The
registration packets themselves live under `review/active/` — one home, not two.

## Measurement law

### Stamp law
- **Every published number is world-stamped, and worlds are not comparable.**
  `RUNTEMPLATE`, `DRAFTER_VERSION`, and `POLICY` bumps archive their
  predecessors; check the stamp before quoting anything (R68).
- Run experiments through a `Cell` (`tier05/cells.py`) — it carries the stamp a
  report needs to be citable. **A report without a stamp is not citable.**
- **Frozen calibration surfaces must not be retuned.** The encounter battery,
  the pilots' `block: 1.2`, and `understudy/policy_v0.py` are frozen; editing one
  retroactively moves every archived number measured against it.

### Instrument visibility — one variable per window (D4)
- A prediction must **name the instrument that can SEE the changed object**, and
  confirm it can. The sim is one-seat; a C#-only change never gets a sim
  prediction; `support` is never linted because no instrument sees it.
- Change one variable per measurement window. The drafter/constants version is
  part of the variable set — a scorer change **is** a version bump in the same
  edit (`DRAFTER_VERSION` in `tier0/constants.py`).

### Versioning
- The run-cell stamp is `RT/D/P/C`, read live via `tier05/cells.py`:
  `RUNTEMPLATE_VERSION`, `DRAFTER_VERSION`, `CONSTANTS_VERSION` in
  `tier0/constants.py`, and `POLICY_VERSION` in `tier05/draft.py`. The
  scorecard's `A6_INSTRUMENT_VERSION` lives separately in `tier0/harness/axes.py`
  and is not part of the run-cell stamp. v1 and v2 A6 numbers are discontinuous
  and must never be compared unlabeled.

### Pre-registration + blind grading
- A measurement that a playtest will grade is **pre-registered from design
  intent**, with its contamination stated, and **never revised against the
  playtest that grades it** (D5 — the Kokomi stability band, which lands DARK,
  `band = None`).
- Pre-registration drafts are a [USER]-gated class; the grade goes in blind.

## Active registrations (pointers — packets live in `review/active/`)
- **EB-118 card-connectivity instrument** — static pre-registration at
  `review/active/eb118-richness-phase0-2026-08-23.md` §2, [USER]-approved
  2026-08-23. Deterministic, sheets-only, moves no `RT/D/P/C` version; eight
  pools (five canon via the `game_ref/` extraction surfaces, three mod) under
  one frozen classifier; honest mod-only stop when canon is absent. **Built
  (`tools/card_connectivity_report.py`) and calibration-run 2026-08-23 —
  descriptive only, NOT the baseline; no threshold is registered; the archived
  run was taken under classifier `v1`, before the same-day `v2` completion
  grounded the last three canon detectors, so it is not a `v2` read** —
  directional predictions only
  (§2.4); an absolute gate may be proposed only after the frozen classifier
  has read all five canon pools. Baseline protocol (§2.3): primary baseline is
  taken immediately before the first `EB-118` sheet edit, after `EB-69` lands;
  classifier frozen for the whole batch, vocabulary revisions re-run BOTH
  sides. Registered blind spots at §2.6 (the `decide%` gaps, the lowest-HP
  target heuristic, the `_worst_card` exhaust proxy).
- **payoff-reach re-registration** — the `RARITY_ODDS` fence. Q18 countersigned
  (R121); **predictions COMMITTED 2026-08-13 (R186)** as the registration's
  `## 6`, before any sprint number was read — step (2) of the countersigned
  execution order is executed and `Q-C` is closed. Committed: the ruled aims
  (R185), Q-A under its observational reading and Q-B under its arithmetic
  reading with direction and threshold, the two-leg instrument, the sample
  plan at the ratified cell (n=600/arm, seed 11, `hunter`, `assigned`,
  realistic), controls C1 and C2, a 4h ceiling and tripwires T1–T4.
  **§6.5 was AMENDED pre-run 2026-08-23 (`M28` ratified, R196):** `T3` no
  longer fires on realized reach above the canonical TOP supply ceiling of 3
  — reach and offer above the canonical figures are REPORTED at raw value plus
  multiple, with no new band above TOP — and `T3` is now a single
  classifier-integrity condition over reward-pool base ids, **implemented
  2026-08-24 (`EB-120`)**. `P5(a)`/`P5(b)`,
  the aims, the Q-A/Q-B predictions and `P12` are untouched. **UNRUN,
  and it does not run yet:** §6.6's approved P12 is **settle first** — the
  freeze begins only after the open `RT`/`C` window (`M14`'s batch: `EB-70`,
  the `EB-82` conversion, the `EB-85` batch, `EB-69`) lands and a dependency
  re-check passes; if the world moved, §6 is re-stamped before the freeze.
  **Window status 2026-08-13: the world moved twice and the window is still
  open.** First the `EB-82` conversion and the `EB-85` batch landed together
  under one coordinated bump, `RUNTEMPLATE` 10 → **11**. Then window 2 of the
  correctness batch (`EB-104`, all twelve members) landed under a second
  coordinated bump, `RUNTEMPLATE` 11 → **12** for its five run-layer fixes and
  `CONSTANTS` 9 → **10** for its seven tier0 engine fixes. `C` then moved once
  more, outside that batch: the Artifact-coexistence + Kokomi-rotation ruling
  landed 2026-08-23, `CONSTANTS` 10 → **11**, [USER] pulling the staged branch
  into this same open window. So the live stamp is `RT12/D14/P7/C11`, and
  §6.6's `RT10` line records what was verified on 2026-08-12, not what ships. **THE SETTLE-FIRST BATCH IS EMPTY.** `EB-70` LEFT the window at R195 ([USER] paused the starter-offer retune pending the Klee-rework design sweep R134 originally routed it to — it will not land before the freeze, and when it is eventually taken up it re-baselines in whatever world then exists), and `EB-69` LANDED at R198: the ruled 14-card Kokomi fill, `S4-G11`'s eye-read discharged for that pile, the sheet at 76 rows (5/31/26/14, 70 draftable), **and no version integer moved** — it is settle-first CONTENT, so `RT`/`D`/`P`/`C` are exactly where the last bump left them at `RT12/D14/P7/C11`.
  **`M14`'s re-stamp — the first of the two unblocked registration acts — is DONE (2026-08-24).** The shop-rerun packet is re-stamped `RT11/D14/P7/C9` → `RT12/D14/P7/C11`, its §2 window list carries the three items that cell can see (`RT12`, `C10`→`C11`, and `EB-69` itself), and what remains on `M14` is the slate entry and the countersign, both [USER] acts. **§6.6's `P12` freeze — the second act — is NOT taken here and is the next thing owed after this bullet.**
  **THE DEPENDENCY RE-CHECK HAS NOW RUN AGAINST THE POST-`EB-69` WORLD (2026-08-24) — the FOURTH re-take of the fence, and the first that is NOT byte-identical.** All four fingerprint items were re-taken at the live `RT12/D14/P7/C11`:
  **(1) `RARITY_ODDS` — UNMOVED**, `{common 0.60, uncommon 0.35, rare 0.05}`.
  **(2) `DRAFTER_VERSION = 14` — UNMOVED.** `D` did not move and must not be re-pinned.
  **(3) `rewards.character_pool` — five of six pools byte-identical, id lists included:** `klee 29/28/14`, `furina 23/35/18`, `real_ironclad 19/32/20`, `real_silent 20/35/25`, `ref_ironclad 4/2/—`. **`kokomi` MOVED, by design: 27/20/9 → 31/26/13**, 56 → 70 draftable cards — the fourteen `EB-69` rows, less `ceremonial_garment` which carries `kit_card: true`. This is the fill doing exactly what it was ruled to do; §6.1 already stated both Kokomi pool figures in advance and said the official static read is taken after the fill.
  **(4) `exp_payoff_reach.static_leg` — the six Klee and Furina rows identical to the digit** (supply 10/8/7 · 9/10/14, offer and counterfactual unchanged), **the three Kokomi rows MOVED**: priest supply 13 → 14 (offer 0.1606 → 0.1270), commander 5 → 6 (0.0683 → 0.0578), assist 3 → 5 (0.0406 → 0.0385). The offer term falls on all three even where supply rises, because the pool denominator grew faster than the payoff numerator — arithmetic, recorded, not graded.
  **THE MOVEMENT IS AUTHORIZED, NOT A VIOLATION.** `kokomi/assist`'s 3 → 5 is precisely the move R197 admitted when it amended R190's fence (§6.8), recorded **before** the fill landed and with both figures on the record; the other two Kokomi rows are the same fill classified honestly under the same registered predicate. §6.5 already put the official `P5` read after this point and already said the three Kokomi arms may move on either axis. **Nothing here is a `P5` grade** — these are fingerprint figures, taken as the three previous re-takes took them, and the grade is the freeze's own step. The six Klee and Furina rows are exactly as stable as §6.6's ordering-(i) argument predicted, and the fence itself — the odds table and the drafter pin — never moved across any of the four re-takes.
  **The once-only rule held.** §6 is re-stamped once, when the last of the
  batch lands, rather than after each item — re-stamping a registration per
  item is how a one-variable window turns into four. The fence was
  fingerprinted at every bump so it did not have to be re-derived later:
  byte-identical across `RT10 → RT11`, byte-identical again across
  `RT11/C9 → RT12/C10`, byte-identical a third time across `C10 → C11` (the
  2026-08-23 ruling, `cb8be0c`, which edited no card sheet and moved no
  offer-time price), and moved for the first time — in Kokomi's three rows
  only, and by authorization — at this fourth re-take. `EB-112` was the one
  batch member that could have reached the fence and did not: it makes an
  event card screen consult `RARITY_ODDS` instead of bypassing it, and
  `static_leg` is arithmetic over the reward pools and the odds table, so
  neither the constant nor any static-leg output moves.
  **What is owed next, in order:** §6.6's `P12` freeze — which re-stamps §6
  (and `T1`'s registered stamp string with it) to `RT12/D14/P7/C11` and then
  freezes — and only then steps (3)–(6). Neither is taken here.
  Owed before the run and named in §6.4/§6.5: the generic reach reader
  (`tier05/exp_payoff_reach.py`) and the `blind` control policy — **both built
  2026-08-13** — and the amended `T3` plus §6.1's above-scale reporting, both
  **built 2026-08-24 (`EB-120`)**. The `M28` fallback was not needed: `T3` is
  implemented entirely off the one shared predicate
  (`draft.is_on_plan_payoff`), so all four tripwires stand. Reader and printer
  only, `D` and `P` unmoved, and the static leg's supply, offer and
  counterfactual figures identical to the digit across the build.
  Steps (3)–(6) run in order and none reorders →
  `review/active/payoff-reach-reregistration.md` §6.
- **EB-17p force-first-copy paired winrate** — **RUN AND GRADED 2026-08-10.**
  Countersigned complete (`N` = 2400 pairs, Strike filler, 4h ceiling, §6.1b
  co-primary), §8 predictions committed ahead of the run (`eb67706`), graded
  blind in §13: **3 PREDICTED / 1 SPLIT / 1 MISS** (`borrowed_brilliance`, wrong
  sign). §11.1's disclosed 12-pair read was **ruled immaterial (R173)** and the
  registered range ran unchanged. **The measurement is closed.** §8.1's redesign
  trigger fired for `borrowed_brilliance` and `elemental_ecstasy`, and **R180
  (2026-08-12) split the two**: `elemental_ecstasy` goes to redesign;
  `borrowed_brilliance` is **remeasured first**, by re-running the registered
  **five-card** sweep re-registered under `P7` — never a narrowed single-card
  experiment. **That re-registration is now DRAFTED and has its own pointer
  below**; it is a NEW packet beside this one. **R101b: this registration and
  its results file stay unedited** — there is no re-grade of §13 →
  `review/active/eb17p-registration-draft-2026-08-08.md` §13, §13.8;
  `review/active/eb17p-results-2026-08-10.txt`; QUEUE `M17`.
- **Force-first-copy paired winrate, re-registered under `P7` (`M17`)** —
  **DRAFT, awaiting [USER] countersign at QUEUE `M17`, unrun.** R180 ordered
  the **registered five-card** sweep re-run under `P7` — never a narrowed
  single-card experiment — because §13.8's `borrowed_brilliance` anomaly was
  pilot refusal that `P7` (R176) resolved, and because §13's Δ figures are `P6`
  reads. The draft is the parent's instrument and arm set unchanged, re-stamped
  to `RT10/D14/P7/C9`, with a new descriptive `Q4` on the bare-form play rate.
  **PARTLY FILLED 2026-08-13 (R189), and deliberately NOT countersigned:**
  `N` = 2,400 pairs/card, a 4-hour stop-and-report ceiling, §8.1's redesign
  trigger carried forward unchanged, and the `Q4` materiality threshold at 5%
  — the last recorded as [USER]'s chosen threshold, **not** evidence-derived.
  **§8's per-arm prediction table and the direction half of `Q4` stay blank**,
  so the packet is not cleared to launch; the countersign is withheld until the
  post-window restamp, because predictions are filled against the settled world
  and the `RT`/`C` window is open. R189 also chose the **route** —
  measure-first, so this sweep runs before the `elemental_ecstasy` redesign
  (Option `C2`), which lands after the graded read as its own `C` bump.
  **Sequencing:** it runs *after* the payoff-reach sprint's graded read, per the
  approved settle-first plan, and before the staged `EB-43`/D15 landing (its own
  S3) →
  `review/active/m17-sweep-reregistration-p7-2026-08-13.md`; companion redesign
  options packet `review/active/m17-elemental-ecstasy-redesign-2026-08-13.md`.
- **Shop companion channel re-run (`S4-G10` / `C9`)** — **DRAFT, awaiting
  [USER] countersign at QUEUE `M14`, unrun.** The packet is in HEAD as of the
  `shop-floor-2026-08-10` merge. The channel's world moved ([USER] restored slot 2's
  Uncommon floor, `CONSTANTS_VERSION` 9) and the instrument's two defects were
  repaired, both on 2026-08-10; the packet asks to re-measure in the new world.
  Predictions are explicit [USER] slots and are still blank →
  `review/active/shop-rerun-registration-2026-08-10.md`.
- **The regret margins (`M13`)** — **DRAFT, §7 PARTLY FILLED 2026-08-12
  (R181), awaiting [USER] countersign at QUEUE `M13`, unrun.** `ROUTE_REGRET_MARGIN` and its drafter
  twin (`draft.DRAFT_REGRET_MARGIN`, the `+1.0`) have no recorded derivation;
  R164 ruled that the measurement is pre-registered and that **`+1.0` is not
  ratified**. The distribution printer `tools/regret_distribution.py` landed
  first and made a registration possible at all —
  the margin-free gap distribution for both numbers, on a read-only pass over
  finished runs, with no stamp movement. The packet's §7 predictions are
  explicit [USER] slots and are still blank, and its §6 lays out four
  derivation options at equal weight — including the upper-percentile
  derivation, whose circularity is stated there rather than assumed away.
  **R181 settled the scope slots:** control `C2` authorised (build owed before
  the run), control `C3` declined so `Q5` is dropped and Option B is
  unavailable, both sample rates reported separately, and **Option D — no
  margin — retained as the standing answer** unless the result shows a margin
  has utility. The predictions themselves are still blank →
  `review/active/regret-margin-registration-2026-08-12.md`.
- **Charge reads per turn (`EB-78`)** — **DRAFT, unrun, §5's prediction slots
  blank as [USER]'s.** R188 (2026-08-13) ruled **no** Charge read budget and
  returned `X9` to the watch register; a watch trigger needs the quantity it
  watches, and *how many reads a turn contains* was recorded nowhere until the
  instrument landed on 2026-08-13 (`resources.note_charge_read`, emit-only,
  tagged per source so the workshop's unsettled §6 scope boundary is not
  settled by construction). Descriptive: it grades no design and cannot on its
  own fire a nerf. §5.1 is where "repeatable reads dominant" becomes a number,
  and it is a [USER] slot. Sequenced after the payoff-reach graded read; it
  moves no version and opens no window →
  `review/active/charge-reads-per-turn-registration-2026-08-13.md`.
- **Kokomi stability band (D5)** — no band is declared yet (the declaration
  is QUEUE `S4-G6`; until it lands, the band rides DARK, `band = None`); its
  grading playtest is `docs/current/playtest/kokomi-playtest-protocol.md`
  (unrun; Answers block still blank).

New registrations add a pointer here and land their packet under
`review/active/`; when a registration is graded and closed, both leave HEAD.
