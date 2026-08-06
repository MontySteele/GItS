# Atlas: tier0-harness-tests

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `tier0/harness/` (axes, metrics, report, runner) and `tier0/tests/`.

## 1. Purpose

`tier0/harness/` is the measurement half of the Tier-0 Monte Carlo balance
simulator: `metrics.py` turns a finished fight's event log into a `FightStats`
record, `axes.py` folds a whole encounter battery into the seven-axis scorecard
normalized so `ref_ironclad/starter = 3.0`, `runner.py` is the CLI + scoring
orchestration, and `report.py` is terminal presentation only. `tier0/tests/`
(1236 tests; 1556 with `tier05/tests`) is not a unit-test suite for the engine —
it is the repo's *gate wall*: engine pins, sheet/content lints, C#-parity
regressions, art-pipeline checks, encoding and convention lints, frozen-battery
calibration bands, and the understudy contracts, all executed from pytest.

What this module is explicitly NOT: it is not a source of ratified truth about
designs. Seven-axis numbers are **reportable but not load-bearing** until the
axis-validity session rules (`tier0/harness/axes.py:9-22`, D3). And the thing it
sits next to — `understudy/` — drives the real game and "is not a simulator and
it must never become one" (`understudy/README.md:11`); nothing in this module may
be re-implemented there, only delegated to (`understudy/adapter.py:1-16`).

## 2. Entry points

Run everything from the repo root with `PYTHONPATH=.` (`tier0/README.md:20`).

```sh
# battery summary / 7-axis scorecard / round-3 median identity / per-fight CSV
PYTHONPATH=. python3 -m tier0.harness.runner --character klee --deck reaction_package --pilot reaction --fights 1000
PYTHONPATH=. python3 -m tier0.harness.runner --score --character klee --deck demolition_package
PYTHONPATH=. python3 -m tier0.harness.runner --report-character --character furina --fights 1000
PYTHONPATH=. python3 -m tier0.harness.runner --csv out.csv --character klee

python3 -m pytest tier0/tests -q                 # 1236 tests
python3 -m pytest tier0/tests tier05/tests -q    # what CI runs (.github/workflows)
GITS_REFERENCE_MODE=committed-only python3 -m pytest tier0/tests -q   # fresh-clone mode
```

Library-level: `runner.run_battery`, `runner.run_full_battery`,
`runner.score_config`, `runner.score_character` (`tier0/harness/runner.py:27,50,57,115`);
`axes.raw_axes` / `axes.normalize` / `axes.heuristic_flags`
(`tier0/harness/axes.py:83,204,253`); `metrics.extract` / `merge_stages` /
`summarize` (`tier0/harness/metrics.py:114,69,228`).

CI's `lints` job invokes the standalone lints directly (`.github/workflows/*.yml`):
`tools/lint_handwritten_parity.py`, `lint_constant_parity.py`, `lint_op_parity.py`,
`gen_roster_cards.py --check`, `lint_pool_membership.py`, `lint_ancient_coverage.py`,
`suggest_role_tempo_tags.py --check`, `lint_role_tempo_coverage.py --gate`,
`lint_roster_registry.py`, `lint_vendor_pin.py`, `art_coverage.py`.

## 3. Key invariants

- **The anchor is `("ref_ironclad", "starter")` and the baseline always uses the
  `generic` pilot** — a floating anchor makes scores incomparable across runs
  (`tier0/harness/runner.py:24,57-69`). Pinned in `tier0/tests/test_anchor_lock.py:1-16`.
- **Baseline scores exactly 3.0 on every axis** by construction
  (`tier0/harness/axes.py:204-229`; asserted `tier0/tests/test_axes.py:39-41`).
- **A ratio axis with a zero baseline raises, never scores.** `_anchor()` refuses
  rather than dividing by an epsilon that clamps to `SCORE_CAP` = a fake 10.0
  (`tier0/harness/axes.py:179-201`). A7 inverts, so its *raw* value is the guarded
  divisor (`tier0/harness/axes.py:220-225`).
- **A6's application-uptime term is anchored ADDITIVELY, not as a ratio** — the
  Ironclad applies no auras, so its uptime baseline is legitimately 0
  (`tier0/harness/axes.py:212-219`; `A6_INSTRUMENT_VERSION = 2` at
  `tier0/harness/axes.py:41`). v1 and v2 A6 numbers are discontinuous by design and
  must never be compared unlabeled (`tier0/harness/axes.py:36-40`).
- **Named encounter pools are mandatory in battery mode.** A3 reads `attrition`
  and A6's AoE term reads `swarm`; a missing or empty key raises `KeyError` rather
  than silently averaging the whole battery. `battery=False` is a call-site
  declaration for synthetic stats only (`tier0/harness/axes.py:56-81`).
- **Zero turn-10 samples reads A2 = 0.0, not 1.0**, and the denominator rides in
  the raw dict as `A2_samples` — which is *not* an axis and every scorecard
  consumer ignores it (`tier0/harness/axes.py:102-112,157-160`).
- **Reported-vs-credited is a hard line.** Encore absorption credits A4, never A3
  (`tier0/harness/axes.py:120-126`, `metrics.py:30-31`); Kokomi's `prevented`,
  `charge_gained`, `engine_closure_turns` are REPORTED ONLY, never folded into
  `damage_blocked` and never given axis credit — that would be a metric
  redefinition (`tier0/harness/metrics.py:41-48`); `hp_by_round` is reported, never
  banded (`tier0/harness/metrics.py:60`, D5) and is a LIST because ordering is the
  datum, so stage merges concatenate (`tier0/harness/metrics.py:54-61,80-84`).
- **Constraints are HARD on `starter` and on the archetype median, informational
  on package decks** (`tier0/harness/runner.py:79-87,115-137`). Winrate bands are
  only checked at >= `WINRATE_BAND_MIN_FIGHTS` (1000); below that binomial noise
  makes band edges meaningless (`tier0/harness/runner.py:139-145`;
  `tier0/constants.py:575`).
- **Encoding rule: every text read/write declares `encoding=`.** Structural lint,
  not behavioural — an omitted encoding is cp1252 on Windows and UTF-8 on CI
  (`tier0/tests/test_encoding_gate.py:1-22`). The content path (`tier0/content/`,
  `tier0/engine/`, `tier05/`) may carry **zero** debt (same file, `:98-107`).
  `runner.main` reconfigures stdout to UTF-8 with `errors="replace"` for the same
  reason — `hpΔ` and the block-glyph bars kill a cp1252 console *after* the battery
  has been computed (`tier0/harness/runner.py:178-186`; `tier0/harness/report.py:18-20,71`).
- **Tests have one shared fixture module and it is tiny**: `make_enemy`,
  `make_state`, and a `state` fixture (`tier0/tests/conftest.py:8-22`). There is no
  repo-root conftest — everything else each test file builds itself.

## 4. Rulings that shaped it

- **R18** — A6 instrument v2: application uptime enters the utility axis at
  `0.5*aoe + 0.3*debuff + 0.2*uptime`, anchored additively; ref_ironclad must stay
  exactly 3.00 under it (`tier0/DECISIONS.md:408-415,569-576`).
- **D3** — scorecard *invariants* (non-elite <= 4.0 cap, elite-pair identity) are
  pulled; axis numbers are reportable but not load-bearing and no new band may be
  ratified on them; only the three honesty repairs stayed in scope
  (`tier0/DECISIONS.md:2402-2444`).
- **D4** — instrument-visibility law: a prediction must name its instrument and
  confirm it can see the changed object; C#-only changes never get sim predictions
  (`tier0/DECISIONS.md:2446-2460`).
- **D5** — Kokomi's stability band lands DARK (`band = None`), declared from design
  intent with its contamination stated, never revised against the playtest that
  grades it (`tier0/DECISIONS.md:2504-2560`; `tier0/tests/test_stability_band.py`).
- **R67** — no sweep runs outside the gated harness; `KNOB_READS` refuses a cell
  whose swept knob records zero reads, so constants must be read as module
  attributes — `from tier0.constants import X` slips the hook
  (`tier0/DECISIONS.md:2065-2120`).
- **R70** — manifest version is MAJOR-AUTO with overwrite refusal; gate in
  `version.ps1::Test-VersionPolicy`, pinned by
  `tier0/tests/test_manifest_version_gate.py` (`tier0/DECISIONS.md:2209-2265`).
- **R81** — distinctness gate ratified (uniq >= 70, maxclu <= 5, neardup <= 0.40)
  as a red test whose curated known-failing list may only shrink
  (`tier0/DECISIONS.md:2563-2592`; `tier0/tests/test_distinctness_gate.py`).
- **R93** — understudy `policy_v1`'s seven revisions approved, resolved card NAMES
  a P1 blocker, and nothing in `tier0/`/`tier05/` touched — notably
  `tier0/pilot/policy.py` is *not* changed for the block-panic insight
  (`tier0/DECISIONS.md:3179-3218`; `tier0/tests/test_understudy_policy_v1.py`).
- **R97** — soak readiness watches the menu `options` key, never the HTTP health
  endpoint; the five adapter defects are MEASUREMENT HISTORY, not open defects
  (`tier0/DECISIONS.md:3339-3370`; `tier0/tests/test_understudy_soak.py:1-13`).

## 5. Traps

- **Frozen files.** The encounter battery and the pilots' `block: 1.2` are frozen —
  retuning either invalidates every archived number, and
  `tier0/tests/test_axes.py:79-100` fails loudly
  (`tier0/content/encounters/battery.yaml:3`, `punisher.yaml:4`,
  `tier0/content/pilots/archetypes.yaml:186,259`, `tier0/README.md:45-50`). So is
  `understudy/policy_v0.py`: one arm of a published measurement, editing it moves a
  quoted number retroactively (`understudy/README.md` table).
- **The adapter's fidelity losses are enumerated, not assumed**: base-game cards
  become text-derived stubs and are systematically undervalued; only named statuses
  cross; enemy auras are often absent (zeroing `_reaction_value`); intent ramps and
  multi-phase bosses are structurally invisible; relics/pile order/exhaust/orbs are
  not carried at all (`understudy/adapter.py:17-51`). Read this before treating any
  divergence as policy judgment.
- **Debt lists are staleness-gated in both directions.** `test_encoding_gate.DEBT`
  is per-file COUNTS, and a fixed file must LEAVE the list — a zero entry is an
  allowance for the next offence (`tier0/tests/test_encoding_gate.py:26-67,86-95`).
  Same shape for `stale_bands` (`tier0/tests/test_stale_band_annotations.py:29-43`)
  and R81's curated distinctness failures. And a stale-annotated band still FIRES:
  `BAND EXCEEDED` is ratified law until a ruling moves it, the annotation only says
  why (`tier0/harness/runner.py:88-98`).
- **`Image.open` is not a text read.** The encoding lint once keyed on the
  attribute name, producing 20 phantom offences that were live cover for real bare
  `open()` calls; `io.open`/`codecs.open`/`gzip.open` remain in scope
  (`tier0/tests/test_encoding_gate.py:34-42,110-136`).
- **Tests are cwd-sensitive by construction**, and `GITS_REFERENCE_MODE=committed-only`
  hides the gitignored `game_ref/` pool atomically. Subprocess probes pin cwd to the
  repo root — a gate that only passes from one directory is not a gate
  (`tier0/tests/test_local_reference_mode.py:11-40`). CI deliberately does NOT set
  the env var: a runner has no `game_ref/`, and that job asserts the *committed*
  world is sound (`.github/workflows/*.yml`, `pytest` job comment).
- **`heuristic_flags` may report shape but must never become an assertion**
  anywhere in the suite — D3's scope guard lives at
  `tier0/tests/test_axes_honesty.py:196-208`; deleting that test is the act of
  reinstating the pulled invariants.
- **Two fixture hazards.** Reusing one `FightStats` object under two encounter keys
  doubles the A2 sample count and silently changes which battery you measured
  (`tier0/tests/test_axes_honesty.py:140-160`); and `score_config(..., base_stats=)`
  sharing must stay a pure saving — the anchor is a deterministic function of
  `(fights, seed)` and nothing may mutate it, or an archived scorecard depends on
  how many decks were scored beside it (`tier0/harness/runner.py:57-69`; pinned
  `tier0/tests/test_axes.py:24-36`).
- **`extract()` is a single pass over `state.log` keyed on event names** — a new
  engine event with no arm here silently measures nothing
  (`tier0/harness/metrics.py:129-193`).

## 6. Reading order

1. `tier0/README.md` — usage, and the frozen-calibration warning.
2. `tier0/harness/axes.py` — the module docstring carries D3's standing; then
   `raw_axes`, `_named_pool`, `_anchor`, `normalize`.
3. `tier0/harness/metrics.py` — `FightStats` field comments are the reporting-vs-
   axis-credit law; `extract` is the event vocabulary.
4. `tier0/harness/runner.py` — `BASELINE`, `score_config`, `score_character`.
5. `tier0/tests/test_axes_honesty.py` — the three honesty repairs plus the D3 scope
   guard, stated as symptoms.
6. `tier0/tests/test_anchor_lock.py` and `tier0/tests/test_axes.py` — what actually
   holds the divisor still.
