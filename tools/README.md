# tools/ index

Added 2026-07-26 (tech-debt audit §6 — orphan status was undiscoverable).
Every script, mapped to what actually runs it. "validate" = invoked by
`klee-mod/build/validate.ps1` at deploy; "pytest" = exercised by the suite;
"manual" = a live instrument run by hand; details and known gaps per tool:
`docs/tech-debt-audit-2026-07-26.md`.

## Deploy gates (validate.ps1)
| script | gate |
|---|---|
| `lint_handwritten_parity.py` | S6 |
| `gen_roster_cards.py` (`--check`) | S6a — thin CLI over `gen_klee_cards.py`; path-invoked only (not importable as a module) |
| `lint_pool_membership.py` | S6b |
| `lint_ancient_coverage.py` | S6d |
| `lint_constant_parity.py` | S6e + pytest (`test_sheet_lints.py`) — the dual-wired model the others should follow |
| `build_pck.ps1` | S6c reads its contract output |
| `lint_vendor_pin.py` | not a validate.ps1 rule (the bridge is a harness, not shipped) but gated three ways: CI, `test_vendor_pin.py`, and `klee-mod/build/deploy_bridge.ps1` refuses to install a drifted snapshot |

## Suite-gated (pytest only — no deploy gate)
`lint_r_citations.py` (also CI-gated; the clause-bearing R-number citations in
`canon_role_tempo.py` against the clauses `DECISIONS.md` declares — S4's F14
plus its four siblings, graduated to a check at five instances. Scoped to that
one file **on purpose**; widening it is a separate decision),
`lint_strict_domination.py`, `lint_unique_names.py`, `lint_upgrade_coverage.py`,
`lint_kokomi_decksize.py`, `lint_companion_shop_coverage.py`,
`lint_sheet_comments.py` (currently gated on furina-cards.yaml ONLY — 35 open
findings on the other five sheets, see audit §3.8), `art_coverage.py`
(invariants, deliberately not completeness), `art_lint.py` (unit-level only;
its L12 pixel gate is dead on clean checkouts — audit §3.7),
`extract_base_game_pool.py`, `build_official_sheet.py` (+ its thin
`build_ironclad_sheet.py` entry point, kept because validate.ps1 and the
generated game_ref headers name it),
`realistic_axis_scores.py`, `burst_defense.py`, `char_stills.py` (library,
byte-pinned), `gen_furina_stills.py` (byte-pinned, skip-guarded),
`real_battery_calibration.py` + `klee_survival_sprint.py` (digest only).

## Advisory (CI-visible, never blocking)
`patch_sentinel.py` — asks whether the INSTALLED sts2.dll still agrees with the
`game_ref/` baselines (cards, character facts) and with its own relic/DLL
snapshots in `.sentinel/`. Its CI job is `continue-on-error` and prints
"skipped" on a runner, because a runner has neither the game nor the
baselines; the real run is local. **Findings are alarms for a [USER]-gated
pass and are never auto-acted on** — see `docs/patch-sentinel.md`. Its diff
core is suite-gated on synthetic fixtures
(`tier0/tests/test_patch_sentinel.py`).

## Manual live instruments
`gen_klee_cards.py` (the roster codegen itself), `art_fetch.py`,
`art_process.py`, `art_hunt.py`, `art_contact_sheet.py`,
`gen_kokomi_stills.py` (NO byte-pin twin, unlike Furina's),
`gen_transition_wipe.py`, `cut_combat_layers.py`, `cut_salon_members.py`,
`encounter_audit.py`, `pilot_error_audit.py`, `measure_realistic_act1.py`,
`dump_claimed_sources.py` (owns the committed
`docs/art-claimed-sources.tsv`; regenerate after any plan.tsv change —
nothing enforces freshness yet).

## archive/
One-shot experiments whose results were ratified, and superseded tools.
Kept for reproducibility of the records that cite them; nothing imports
them. R67 (2026-07-26) deleted `PROGRESSION_GAP_COMPENSATOR`, whose only
remaining reader was `roster_scale_gap.py` here — so that script no longer
runs, which is the normal end state for an archived one-shot: it is the
record of what was measured, not a thing to re-measure with.

R68 (2026-07-26) moved three Furina experiment scripts here from `tier05/`:
`exp_furina_achievability.py` (hardcodes `SCREENS = 10` from RUNTEMPLATE 2 —
it runs, it prints numbers, and it describes no world that exists),
`exp_furina_modes.py` and `exp_furina_pass3.py` (both self-declared archived
in their own docstrings while still sitting in the live directory). They keep
their hand-rolled seeds and configs deliberately: those ARE the historical
record. `tier05/cells.py` governs anything run from today forward.

Scripts here are invoked by path (`python tools/archive/<name>.py`), not as
`-m` modules, and each inserts the repo root on `sys.path` itself. Note that
the older arrivals — `banner_variance_cells.py` and anything else using
`parent.parent` — compute that root as `tools/` rather than the repo, a
leftover from being moved without their bootstrap being updated. They will
not import until that line is fixed.
