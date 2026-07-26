# Missed requirements — recap audit, 2026-07-26

Findings from a full read of all 89 project docs, cross-checked against the
code (`tier0/`, `tier05/`, `klee-mod/KleeCode/`, `tools/`, the design-sheet
YAMLs, `art/plan.tsv`) and against the two live ledgers
(`open-playtest-items.md`, `red-pen-2026-07-26.md`).

**Inclusion rule:** an item appears here only if it was (a) required, directed,
or owed by a doc, (b) verifiably never built / never done, and (c) tracked in
*neither* live ledger. Items already tracked elsewhere are not repeated here —
this log exists to catch what fell through, not to mirror the queues.

Each item cites its source and the evidence of absence. Nothing here is a
ruling; disposition (build / waive / re-file) is [USER]'s.

---

## Tier 1 — design-identity gaps (features a charter declares that don't exist)

### 1.1 Furina: co-op Fanfare partner-flux + the Hot Hands exclusion audit
- **Source:** `furina-kickoff-v0.1.md` §4 declares partner HP/Encore flux
  counting toward Fanfare as *"the first ally-coupled mechanic"*, with a
  mandatory audit: *"exclude or discount self-inflicted partner damage (Klee's
  Hot Hands) or Fanfare farms itself."* Also `archive/furina-predesign-notes.md`
  Part 2.
- **What happened:** deferred to "Tier 2" by `archive/furina-sprint-1-report.md`
  §5. **There is no Tier 2** (the repo has `tier0/`, `tier05/`, `tier1/`).
  Co-op has since shipped and been playtested.
- **Evidence:** zero partner/ally coupling in
  `klee-mod/KleeCode/Powers/FurinaResources.cs` or `tier0/engine/resources.py`;
  absent from `open-playtest-items.md` §4 (the co-op section) and the red-pen.

### 1.2 Furina: cross-player Spotlight selector passing
- **Source:** `furina-kickoff-v0.1.md` §3.1 and §11.5 ("Appendix A.4's
  engineering, arriving early").
- **What happened:** deferred with "solo path first" in the sprint-1 docs.
  Co-op is live, so the deferral condition has lapsed; no implementation and
  no tracking anywhere.
- **Evidence:** no hit in `klee-mod/KleeCode/`; `csharp-build-spec` §C4
  (co-op hardening) never names it; absent from both ledgers.

### 1.3 Kokomi: the stability-band instrument was never built
- **Source:** `kokomi-kickoff-v1.md` §3 (max HP-loss variance across the
  battery), restated `archive/kokomi-roster-v0.1-report.md` §3.2/§5. **R51 made
  it the entire home of her healer fantasy** — "moves entirely to the stability
  band … in the act-level realistic sims" (`tier0/DECISIONS.md:1279`).
- **Evidence:** no variance/flatness metric exists. `tier05/run_metrics.py`
  has only `survival_profile` (median HP pct, near-death rate — generic,
  pre-Kokomi); `tier0/harness/metrics.py` has mean `hp_delta` only. No Kokomi
  report since sheetpass v0.2 quotes an HP-flatness number, and no band was
  ever declared. The last measured numbers are three world-changes stale.
- **Weight:** with the band unbuilt, the ruled backstop for LAW 2 (no heals)
  is unmeasurable — her core fantasy currently has no instrument.

### 1.4 Kokomi: the multiplicative-read cell was registered twice and never measured
- **Source:** `archive/kokomi-roster-v0.1-report.md` §5 ("one measurement
  covers the set"), escalated to "now hot" in
  `archive/kokomi-sheetpass-v0.2-report.md` §6.5.
- **Evidence:** every mention in the repo is a registration; none is a
  measurement. Risk has *grown* since: `KURAGE_PULSE_PER_CHARGE = 4`
  (`tier0/constants.py:307`) put a per-point bank reader on a **basic** card
  alongside `all_streams_flow`, the Garment, and `nereids_ascension`, all
  reading the same uncapped Charge bank. R56's "watched in act 3" is a winrate
  check, not this cell.

### 1.5 Furina: Q3 — the innate-on-upgrade Encore card was measured green and never shipped
- **Source:** verbatim [USER] directive (2026-07-24), carried only by
  `archive/furina-sheet-pass-4-plan.md`: *"one Encore card should upgrade to
  Innate, to solve 'I have no Encore, so half my cards don't work.'"* Q3a
  proved the pipeline supports it; Q3b/c/d measured it green (+0.4pt, A1 flat,
  no first-fire domination).
- **Evidence:** `docs/furina-upgrades.yaml:12` is still
  `aria_of_recompense: {encore: +3}`; zero `innate` keys in the sheet and zero
  `Innate` in `klee-mod/KleeCode/Cards/Furina/`. No later doc waives it; it is
  in no backlog. The directive was orphaned when its host doc went stale.

---

## Tier 2 — instruments and telemetry that rulings or gates depend on

### 2.1 `route_regret` — advertised in code, never written
- **Source:** `sts2-map-and-events-research.md` §4.2 mandates it as a day-one
  countermeasure to the route-policy confounder ("without it, 'runs got
  better' is unfalsifiable").
- **Evidence:** `tier05/route.py:13` *documents it as existing* ("…
  `route_regret` (run_metrics) samples the road not taken") but
  `tier05/run_metrics.py` defines no such function; repo-wide the name exists
  only in prose. Comparator `draft_regret` is fully built and tested.
- **Weight:** §3.7.5's "relics are underpriced" finding rests on a
  hunter-vs-cautious gap that is exactly the comparison §4.2 says needs this
  instrument to be readable.

### 2.2 Klee: played-when-drawn / dead-in-hand / force-first-copy telemetry
- **Source:** `archive/klee-survival-sprint-plan.md` §4 makes it a
  precondition ("Do not use raw pick rate as the redesign trigger…"), re-owed
  as next-step 3 of `archive/klee-survival-sprint-report.md`, which also makes
  it a live gate: bodyless draw/resource engines may not be buffed without it.
- **Evidence:** zero matches for `played_when_drawn` / `dead_in_hand` /
  `force_first_copy` across `tier0/`, `tier05/`, `tools/`;
  `tools/archive/klee_dead_cards.py` measures offered/picked only.

### 2.3 The mod's per-fight telemetry (C2) was never built
- **Source:** `archive/csharp-build-spec.md` §C2: JSON-lines per fight
  (reactions by type, detonations, sparks, burst cast, damage by source, HP
  delta, turns), "in the slice from day one."
- **What happened:** `tier1/analyze.py` was built instead and explicitly
  declines the writer — but it reads per-**run** RunHistory, a different
  granularity. The spec's calibration targets (reactions/fight, burst cast
  rate) have no data source.
- **Live cost, already visible:** `open-playtest-items.md` §1 item 2 (corpse
  detonation, open since 2026-07-21) is *"cannot be settled from the repo"* —
  exactly the question a per-fight detonation counter answers for free.

### 2.4 The sim-pipeline-step → C#-hook sweep is still owed
- **Source:** `klee-mod/DECISIONS.md:1421` — three separate parity defects
  (Superconduct, Shatter, aura tick ordering) reduce to PRE/POST hook
  misplacement; *"no pass has ever systematically mapped each sim pipeline
  step to its C# hook. That sweep is owed."*
- **Evidence:** no sweep doc, no hook-map test, no lint;
  `archive/klee-pass-4-plan.md:250` explicitly deferred it out of scope and
  nothing picked it up.

### 2.5 Klee pass-4 ask A5: the scorecard invariants were never encoded
- **Source:** `archive/klee-pass-4-plan.md` §3.4 / ask A5 — encode the ≤4.0 A2
  ceiling and the "exactly two elite axes, specifically A1+A6" pairing (as
  suite failures or report flags; the ask was *which*, not *whether*).
- **Evidence:** `tier0/harness/axes.py:168-180` `heuristic_flags` still only
  counts axes ≥4.0 without checking which. The invariant currently passes by
  coincidence (A1 4.77, A6 4.05), so the regression risk is live.

---

## Tier 3 — balance and content items flagged for action, then dropped

### 3.1 Lagavulin Matriarch's Soul Siphon half (player stat-drain)
- **Source:** `run-model-rework-plan.md` §10.9 — "the single highest-leverage
  backlog item for boss identity"; §10.8 already measured the consequence
  (she is the *softer* Act-1 boss, 94–97% win-given-reached vs Vantom's
  67–85%, because her anti-turtle teeth are missing).
- **Evidence:** no stat-drain op anywhere in `tier05/` or `tier0/engine/`;
  in neither ledger. Silently biases the Act-1 boss split every act-funnel
  number is read against.

### 3.2 Kokomi P4: prevention on curve
- **Source:** `archive/kokomi-sheetpass-v0.2-report.md` §4 P4 (an uncommon
  lesser ward). P1/P2/P5 landed in v0.3; P4 did not.
- **Evidence:** the only `prevent_exhaust_ward` in her pool is
  `vigil_of_the_deep`, **rare** (`docs/kokomi-cards.yaml:395`). The R58
  +20-card fill added none. `kurages_oath` is Block-per-pulse — a different
  mechanic that never references P4. (Related, weaker: P3 "a ticking body for
  the commander" — no persistent recruit above the basic `bake_kurage`, and
  neither P3 option was ever explicitly chosen.)

### 3.3 `kurages_oath` = 12: flagged "too strong" and absent from every watch list
- **Source:** `archive/kokomi-v0.4-report.md` §8.4/§8.5 — [USER]: *"I feel
  like that's too strong, but we can rebalance later. First knob back."*
  Logged in R56.
- **Evidence:** still 12 (`docs/kokomi-cards.yaml:170`), and — the actual
  miss — it is absent from `open-playtest-items.md` and from
  `kokomi-playtest-protocol.md`'s standing-flags list (which names only
  `KuragePulsePerCharge` and `burst_max`), so the one playtest that could
  judge it won't be told to look.

### 3.4 Klee: two dead-card reworks never landed and were never waived
- **Source:** `archive/klee-design-review.md` Bucket 3 (four solo-fixable dead
  cards; both measured **0% pick rate** in generic *and* their own archetype).
  Two landed in altered form; two did not:
  - **`study_of_explosions`** — still `scry_discard 2 + burst_energy 5`
    (`docs/klee-cards.yaml:76`).
  - **`secret_stash`** — still `add_card` only (`docs/klee-cards.yaml:212`).
- **Evidence:** the survival sprint re-scoped dead-card work to companion
  cards and never names these two; DRAFTER v3's dead-card exit list names
  only Sweet Dreams / Trip Wire / Surprise Visit.

### 3.5 Two tier0.5 spec features: `choose3` slot mode and the Prune signature event
- **Source:** `archive/tier05-draft-sim-spec.md` §3 — "Slot modes (**build all
  three now**): `standard`, `choose3`, `pity(k)`"; and the node-2 free
  take-or-skip signature-companion (Prune) event, deferred verbatim by M7 and
  M8 and never picked up.
- **Evidence:** `tier05/model.py:246-250` raises `ValueError` on a standalone
  `choose3` (it exists only as pity's payload); no event in `tier05/events.py`
  offers Prune — the only Prune references are tests asserting she must *not*
  appear in rewards. The design premise partially survived elsewhere
  (`KleeStartingCompanions.cs`), but nothing records the spec items as dropped.

### 3.6 Furina: post-Salon-v2 numbers that were never re-ratified
Three related items, all flagged in code comments and on no live list:
- **A2 deck bands** — `tier0/content/characters/furina.yaml` still ships
  `salon 7.6 / fanfare 4.2 / spotlight 4.3` under a comment declaring them
  **"STALE SINCE THE SALON-V2 REWORK"**; salon A2 measured 8.9 at R40. The
  band is law until moved, and it is knowingly ~1.3 wrong.
  (`archive/furina-salon-rework-plan.md` §6(c) committed to the re-measure;
  `archive/furina-sheet-pass-3-report.md` ask 3 asked independently.)
- **`SPOTLIGHT_BASE_MULT` ratification** — `tier0/constants.py:81` is still
  `PLACEHOLDER` ("Window-zero forced-arm sweep {1.25, 1.5} decides") even
  though W0 ran at pass 3 and returned dose evidence favouring 1.5
  (pass-3 ask 5, never ruled).
- **The drafter's salon-deploy blindness** — `tier05/draft.py:_static_power`
  has no `salon_member` term, so cross-plan the members are invisible
  (§6(d) of the rework plan; the sibling AoE blindness was fixed, this one
  wasn't).

### 3.7 Furina: the A6 route ruling (sheet-pass-3 ask 2)
- **Source:** `archive/furina-sheet-pass-3-report.md` §8 — A6 median 3.5 vs
  declared 4.2, mechanism decomposed, three routes put to red-pen
  (`tier0/DECISIONS.md` entry 93 records the ask).
- **Evidence:** no subsequent ruling touches Furina's A6; one of her two
  declared elite axes has been measurably short since 2026-07-20 with no
  disposition.

### 3.8 Klee: the Kaboom Beetle Swarm ruling never happened
- **Source:** `klee-mod/DECISIONS.md:1131` — QUEUED, three named options,
  *"Sheet unchanged until ruled."*
- **Evidence:** sheet unchanged; `test_beetle_swarm_bonus_reads_live_bomb_state_per_hit`
  pins the *current* behaviour, so drift hasn't settled it either. In neither
  ledger's desk queue.

### 3.9 Out-of-scale boss audit (`test_subject`, `knowledge_demon`, `kaiser_crab`)
- **Source:** `tier05-perf-and-ironclad-act3-notes.md` §1.5.2 item 1 / §1.3.3
  item 2 — `test_subject`'s sheet inflates HP to stand in for a skipped
  mechanic (*"P3 Intangible skipped (the 300 bar carries the weight)"*),
  which is the fake-it-quietly pattern the house rules forbid.
- **Evidence:** still verbatim at `tier05/content/act3_pool.yaml:217-222`;
  `test_subject` appears in no other doc and no ledger.

---

## Tier 4 — art surface

### 4.1 Three shipped cards render the BETA placeholder and are invisible to the coverage tool
- **Cards:** `spotlight_center_stage`, `spotlight_guest_cast`, `confiscated`.
- **Source:** `animation-sprint-2-log.md` §"Also found, not fixed" — "Needs a
  plan.tsv row and a hunt; not started." Still true.
- **Evidence:** zero rows in `art/plan.tsv` for any of the three; art keys
  live at `klee-mod/KleeCode/Cards/Furina/SpotlightCards.cs:80,110` and
  `Cards/Confiscated.cs`. **Structural blind spot:** `tools/art_coverage.py`
  bills from the canonical sheets, and these are a C#-only selector pair plus
  a token — which is how "art bill 0 missing" and "all 78 portraits resolve"
  both passed while three cards ship placeholder art.

### 4.2 The character-icon `_outline` asset was never produced
- **Source:** billed in `art-asset-manifest.md` ("Character icon 88×88 —
  1 (+outline) — 2"); independently rediscovered as a defect in
  `animation-sprint-2-log.md` Playtest 2 Finding 1.
- **Evidence:** no outline row in `art/plan.tsv` or `art/SOURCES.tsv`;
  `Klee.cs:146`, `Furina.cs:84`, `Kokomi.cs:134` all return the *fill*
  `char_icon.png` for `CustomIconOutlineTexturePath`.

### 4.3 The salon member sprite-scale fix was written up and never applied
- **Source:** `animation-sprint-2-log.md` Playtest 2 Finding 2, with the fix
  supplied as a code block in the log.
- **Evidence:** `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs:185-186` still
  sets only `Texture`/`Visible`; no `Scale` anywhere in the file or in
  `salon_stage.tscn` — 121×144 art into a 34×36 ghost on a 62px pitch.
- **Weight:** blocks the tracked D5 capture from being judgeable (silhouette
  legibility is D5's acceptance question).

### 4.4 The Fontaine Rares sprint's four [USER] close-out items are on no tracker
- **Source:** `fontaine-rares-banner-sprint-log.md` §"Open, and owned by
  [USER]" items 3–6: the companion art picks
  (`art/contact_sheet_companions.html` — Navia / Clorinde / Neuvillette /
  Arlecchino, provisional rank-1 live), the v1.7 lore/naming eyes-on audit
  (non-delegable), the C2 grading countersign, and close-out ratification.
- **Evidence:** that log is not in `open-playtest-items.md`'s "Sources swept"
  list, and §6.1's taste-pass enumeration omits these four shortlists.
  (Design note also parked there: Neuvillette graded WEAK/DEFERRED with the
  "different facet" question open.)

### 4.5 Animation Track F3 and the sprint-1 "polish sprint" deferral
- **Source:** `animation-sprint-2-plan.md` Track F3 (rest/merchant gentle
  idles, both characters) — log says "not started"; `open-playtest-items.md`
  §3 lists only B5/D5/E2/F2. Behind it, sprint-1's Non-goals deferred the
  `selection_screen` / merchant / rest-site / `card_trail` convention scenes
  "to a polish sprint after the in-combat layer proves out" — the layer is
  approved and frozen, and no polish sprint was ever opened.

### 4.6 Smaller art residuals (recorded here so they exist somewhere)
- `no_holding_back` still uses the `Klee Multi Wish` source that L6 flagged as
  trimming 76% of the image — the same clipping round 3 rejected for
  `the_big_one` (`art/plan.tsv:139`; `archive/klee-art-redpen-round3.md`).
- The `kaboom == spark_knight_style` `PENDING_RED_PEN` collision is still
  parked in `tools/art_lint.py:179-186` and, unlike its two siblings, is in no
  ledger.
- Furina's energy counter: `Furina.cs:97` still points at
  `ironclad_energy_counter.tscn`, and `energy_icon_74/22` have no plan rows —
  owed-and-documented in `furina-art-pass-requirements.md` §8 (kept current),
  listed here only because the blocker scene is easy to lose.

---

## Tier 5 — process debts (records that were directed and never written)

- **Kokomi kickoff §0:** the slot-4 (Zhongli) ruling and Itto's consequent
  Inazuma eligibility were directed to be recorded in DECISIONS.md. Never
  recorded — the ruling survives only in the kickoff and a comment in
  `docs/inazuma-companions.yaml:4`. (The consequence was built; the record
  was not.)
- **Furina legibility sprint:** its DECISIONS entry was deferred "until
  commit" and never landed — zero hits for the sprint's terms in either
  DECISIONS log. A whole shipped C#/codegen sprint has no decision record
  (`archive/furina-legibility-sprint-log.md` open item 3).
- **R29d — the eyes-on naming/lore pass** ("before ship, no substitute") is
  still recorded as OWED at `tier0/DECISIONS.md:471` but is on no live list.
  The ride-along instance (`lasting_impression`) was ratified 2026-07-26; the
  general pass was not.
- **Klee pass-4 ask A3:** the §3.4 archetype-band deviation (28/22/14 vs the
  principles' "15–20 tagged cards") was never amended or accepted on record —
  `tier0/tests/test_klee.py:52-71` still carries the verbatim "QUEUED FOR
  USER" docstring, and the principles amendment log has no entry for it.
- **Shop channel §7.6 / §7.7:** five of the seven [USER] close-out items are
  tracked in `open-playtest-items.md` §6.2; these two are not — **§7.6, the
  R60 phase-2 fantasy-leak grading**, is the gate on the deferred
  full-base-colorless-removal sprint (principles §4.7 amendment 2 records it
  as "Deferred, not rejected", blocking on this grading), and §7.7 is the
  Track D fallback taste check (low stakes; recorded as a mod/sim divergence).
- **Convergence-cell membership drift:** the owed cell (tracked in
  `red-pen-2026-07-26.md`) is defined over three cards, but
  `docs/furina-cards.yaml:127` added `standing_room_only` to the watchlist —
  whoever builds the cell should build it over four. Similarly, catalyst
  Kokomi was never added to the hydro-convergence watchlist after R52 ruled
  her a catalyst.
- **Two stale sheet comments that lints can't catch:** `warmup_act` still says
  "(Crackle parity)" though Crackle gained `discard_for_sparks`
  (`docs/furina-cards.yaml:116` — redpen flag 6 directed this update);
  `docs/mondstadt-companions.yaml:4` still asserts "Companion cards NEVER
  scale" though 16 companion upgrade deltas ship (the contradiction was
  resolved the other way at `klee-mod/DECISIONS.md:1524`).

---

## Ledger corrections (tracked items that are already done)

Items `open-playtest-items.md` §6 still lists as open that have since closed —
recorded here and in that file's dated addendum:

1. **"Kokomi kickoff §202: Raiden Shogun's disposition"** — closed by R52;
   `raiden_musou_no_hitotachi` is authored and shipped
   (`docs/inazuma-companions.yaml`), red-pen passes at `81ba9d5`/`e80f955`.
2. **"Furina's starter has no upgraded form … needs a ruling, not code"** —
   ruled (R2) and implemented (queue 3, `477b282`); `NO_UPGRADED_FORM` is now
   an empty dict by design.
3. **"Every number in that sprint is PROPOSED"** — the red-pen session
   happened 2026-07-26; all seven numbers ratified and applied.
4. **"`blazing_delight` has no rank-1 plan row"** — closed at `6f1b969`;
   `art/plan.tsv:123` carries the row and the L12 allowlist entry is gone.
5. **"Orobas is not modelled in the sim"** — Klee's variant now is
   (`touch_of_orobas_klee`, real `combat_start_spark` hook, queue 2). The
   residual gap is narrower: Furina's R2 upgraded form and Kokomi's variant.

Also noted while auditing (not doc issues, but found by the audit):

- `tier0/tests/test_art_coverage.py::test_stale_file_is_not_counted_as_coverage`
  fails on any checkout without the gitignored art tree (`ImageGen/images/`) —
  the "have:" list it asserts on is empty in a fresh clone. Its own docstring
  warns about machine-dependent tests; it currently is one.
- `tier05/route.py:13` documents `route_regret` as existing (see §2.1) — the
  docstring should stop advertising an unbuilt instrument.
- `kokomi-playtest-protocol.md`'s build pin (`750a9cc`) is 63 commits stale,
  and its "do not report art / all personal art is Klee's" instruction now
  contradicts `open-playtest-items.md` §2.2, which asks the tester to judge
  the new shell art. Read §2.2 as authoritative.
