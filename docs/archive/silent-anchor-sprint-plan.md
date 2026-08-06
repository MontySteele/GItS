> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/silent-anchor-sprint-plan.md` — new path: `docs/archive/silent-anchor-sprint-plan.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Silent Anchor — sprint plan (execution brief)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

2026-07-27. Design + rationale: `docs/silent-anchor-kickoff-v1.md` (read
it first; §5's wiring table and §6's gap table are the map). Executor:
Opus. Ratification asks A1–A5 in the kickoff are [USER]-only — build up to
them, never through them.

House rules that bind every track: full-suite gate (`python -m pytest -q`
from repo ROOT, green claims name their scope); no decompiled data or
base-game numbers in committed files; DSL gaps are implemented or logged
UNIMPLEMENTED, never approximated; null results are binding; one variable
per measurement window.

## Track A — tooling generalisation (blockers first)

- **A-1** `tools/extract_base_game_pool.py`: replace the module constant
  `ID_PREFIX = "ic_"` with a character-derived prefix (`ic_`, `si_`, ...).
  Ironclad output must be byte-identical after the change (re-run
  `--emit-sheet`, diff against the existing snapshot) — this is a refactor,
  not a re-measurement.
- **A-2** Generalise `tools/build_ironclad_sheet.py` into a
  character-parameterised assembler (keep a thin `ironclad` entry point or
  migrate call sites). Non-negotiable carry-overs: fail-closed before any
  write; doc-1/supplement disjointness errors; `--split` recovery;
  `--verify` ordered-list comparison. Existing Ironclad tests
  (`test_extract_base_game_pool.py`, `test_real_ironclad.py`,
  `test_ironclad_upgrades.py`) stay green untouched.
- **A-3** Extend the extractor's structural translator only where it is
  character-neutral (e.g. new Cmd shapes met in Silent sources). Anything
  card-specific belongs in pass files, not the tool.

Gate: full suite green; Ironclad artifacts verified unchanged.

## Track B — first extraction (measurement, local machine only)

- **B-1** `python tools/extract_base_game_pool.py Silent` → summary stats
  (pool size settles the 89-vs-91 question; defensive density; effect
  vocabulary; powers referenced).
- **B-2** `--emit-sheet` → `game_ref/silent-cards.yaml` snapshot + upgrade
  companion. Record the emitted/excluded split and the FULL exclusion
  reason histogram in the sprint log — that histogram is Track C's
  priority order and a headline DSL measurement in its own right.
- **B-3** Extract Silent char facts (hp, starting deck, relic) the same way
  `ironclad_char_facts.yaml` was produced; hold the relic decision for ask
  A1 — wire the hook only after the ruling.

Gate: artifacts exist in game_ref/ (gitignored); nothing committed but the
sprint log's aggregate numbers (counts and reasons are fine; card rows and
values are not).

## Track C — DSL parity growth (histogram-ordered; the P0s are known)

Per-power protocol, identical to how Ironclad's dial grew: implement in
the parity layer (`tier0/engine/refpowers.py` pattern) → adversarial
verification pass against the decompiled source → ONLY THEN add to
`SUPPORTED_POWERS` and re-run `--emit-sheet` so the excluded count moves
honestly. One power per commit, each with its data-free effect-pin tests
(the `test_ic_effects.py` model — runs on CI without game data).

- **C-1 (P0)** Chosen discard: new op (or `select:` mode on `discard`),
  load-time vocabulary entry, pilot decision surface. Survivor blocks the
  starting deck without it.
- **C-2 (P0)** Poison with VERIFIED base-game semantics (tick timing,
  decay, stacking — from the DLL, not memory or wiki). The existing
  generic `dot` is mod-side and stays untouched; do not silently retime it
  (Klee-world behaviour is load-bearing).
- **C-3 (P0)** Dexterity: additive block-gain modifier hung off the
  `refpowers.gain_block` chokepoint; audit interaction order with Frail.
- **C-4 (P1)** Sly, restricted form per ask A4 — pending that ruling,
  prototype behind the exclusion list (cards stay excluded until ruled).
  Disambiguate the two Slys in comments at every touchpoint
  (effects.py discard hook, state.py field, Kokomi kickoff refs).
- **C-5 (P1)** Thorns audit; Weak/Frail coverage check against actual
  Silent card usage.
- **C-6 (P2, histogram-gated)** Envenom/Thousand-Cuts-style triggers,
  Intangible, After Image: implement only if the histogram shows them
  gating a material card count; otherwise UNIMPLEMENTED entries with
  stated reasons (stampede/hellraiser precedent).
- **C-7** Hand-translation supplements `game_ref/silent_pool_pass1..N.yaml`
  for structurally-untranslatable-but-expressible cards, disjoint from
  doc 1, numbers from the DLL. Assemble `silent_pool.yaml` +
  `silent-upgrades.yaml` + `char_real_silent.yaml` via the Track A tool.

Gate: full suite green after every power lands; emitted+supplemented
coverage fraction reported against total pool.

## Track D — sim wiring (mirror real_ironclad exactly)

- **D-1** `tier0/content/loader.py`: `EXTERNAL_CARD_SHEETS["silent_pool.yaml"]
  = "real_silent"`; pass layers in `EXTERNAL_CARD_LAYERS`;
  `silent-upgrades.yaml` in `upgrades.EXTERNAL_UPGRADE_SHEETS`.
- **D-2** `tier0/roster.py` REFERENCE_IDS += `real_silent` (keep
  `ref_silent`); `tier05/rewards.NO_COMPANION_CHARACTERS` += `real_silent`;
  `tier05/runner.CHARACTER_PLANS` patch += `real_silent`.
- **D-3** `silent` pilot in `tier0/content/pilots/archetypes.yaml` with
  PLACEHOLDER-flagged weights + the C-1 discard heuristic (ask A3 red-pen
  before its numbers are quoted).
- **D-4** Tests, both halves of the contract:
  - skip-guarded `test_real_silent.py` mirroring `test_real_ironclad.py`
    (tagging, id collisions incl. `si_` vs `ic_` vs mod ids, ownership
    filter, no companions, char facts, pool count pin, upgrade coverage);
  - CI half in `test_anchor_lock.py`: fresh-clone load has no `si_` cards,
    `real_silent` absent, anchor untouched; `committed-only` mode ignores
    a present silent pool (`test_local_reference_mode.py` pattern);
    digest test gains a silent-layer clause.
- **D-5** Axis run: `real_silent` through the tier0 harness and a tier05
  battery; report the 7-axis statline next to ref_silent's predicted shape
  (A1 ≈ 2, A5 ≈ 4.5, A2 superlinear — ref_silent.yaml header). Divergence
  is a FINDING about the construct, not something to tune away.

Gate: full suite green locally AND the CI workflow green (no game_ref on
the runner — total-absence behaviour is the point of D-4's second half).

## Track E — distinctness anchor + ratification package

- **E-1** Run `tools/card_distinctness_report.py` (+ `--families`,
  `--by-rarity`): the two-anchor table, with Silent's coverage fraction
  printed beside her row.
- **E-2** Draft the ruling for ask A2: uniq/maxclu/neardup thresholds
  confirmed or revised against both anchors; the vocab/top% concentration
  question answered with Silent's actual numbers (either direction is
  binding). Deliver as a decision-ready ask, PROPOSED until red-penned.

## Track F — bookkeeping

- **F-1** reserved-card-names.txt bulk Silent pass per ask A5's ruling.
- **F-2** Sprint log `docs/silent-anchor-sprint-log-<date>.md`: B's
  histogram, C's dial movements with verification notes, D's statline,
  E's table, and every deviation from this plan.
- **F-3** Kickoff doc bumped to v1 with rulings recorded; memory update.

## Order and dependencies

A → B → C (histogram-ordered; C-1..C-3 may start immediately, they are
already known-P0) → C-7 assembles → D wires → E measures → F records.
B before any C dial change (the first histogram must be measured against
the CURRENT dial, or the "how much can the DSL hold" number is lost).
D-5 and E-1 are separate measurement windows: pool landing, power landings,
and pilot changes each move the digest — label runs, never compare across
unlabeled worlds.

## Definition of done

1. `OFFICIAL:silent` row from the assembled pool, coverage fraction stated.
2. `real_silent` builds, drafts, and scores end-to-end on this machine;
   fresh-clone/CI behaviour proven unchanged.
3. Two-anchor gate ruling drafted and delivered (not self-ratified).
4. Zero decompiled data committed; full suite green at repo root with the
   count named; asks A1–A5 each resolved or explicitly parked by [USER].
