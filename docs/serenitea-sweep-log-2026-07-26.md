# "Serenitea Sweep" — tech-debt clearance, landing log (opened 2026-07-26)

Running record for the sprint doc of the same name. Governing inputs:
`docs/tech-debt-audit-2026-07-26.md`, `docs/missed-requirements.md`,
`tier0/DECISIONS.md` R66–R72 + D3, `docs/epoch-1-log-2026-07-26.md`.

Standing discipline, every track: R68 stamp lines on any cited run;
KNOB_READS gate on any sweep; module-alias constant imports only; no sheet
edits outside Track G; predictions graded in writing before any other output
of the same landing is reviewed.

**Epoch numbering.** This sprint's stamped landing is EPOCH 2 (Track D). The
deferred `_static_power` repricing (DRAFTER 11) takes the next integer when
its design session rules — epoch integers are assigned at landing time, never
reserved.

---

## Track A — Fresh-clone green — LANDED

Standalone commit, ahead of every other track, because it is the gate the
later tracks are verified against.

### A1 — `test_stale_file_is_not_counted_as_coverage`

Seeded a COVERED probe alongside the stale probe. The test's negative
assertions ("the covered list does not name the stale probe") were being
evaluated against a list that is empty on any tree without art — a vacuous
assertion wearing a real one's clothes, which is why the module went red on a
bare clone at `assert covered_lines, "report printed no covered list"`.

The covered probe's id is **read from a canonical companion sheet**, not
written as a literal — a literal here would reproduce
`test_bill_is_derived_from_canonical_sheets`'s own failure mode one level up.
It is written only if that path is currently unoccupied and removed only if
this test wrote it, so on a machine that holds the real portrait an
eyes-on-approved file is never overwritten.

Verified in both directions on a real `git clone --depth 1`:

- **pre-fix, no art:** `FAILED ... assert [] :: report printed no covered list`
- **post-fix, no art:** passes
- **post-fix, stale counted as coverage** (mutated `art_coverage.py` to print
  every present stem as `have:`): `FAILED ... assert all(stale.stem not in ln ...)`

### A2 — Sibling audit, bounded — **0 further instances; the third-instance rule does NOT fire**

Nine suite modules reference a gitignored path. Classification:

| Count | Class | Modules |
|---|---|---|
| 1 | Unguarded, fails on a bare clone | `test_art_coverage` — the A1 subject |
| **0** | **Further unguarded siblings** | — |
| 5 | Correctly guarded (`skipif` on the artifact, or monkeypatched onto `tmp_path`) | `test_char_stills`, `test_ironclad_upgrades`, `test_real_ironclad`, `test_measurement_world_digest`, `test_anchor_lock` |
| 1 | Path strings are synthetic fixture data; no filesystem read | `test_art_lint_source_group` |
| 2 | Prose/docstring mention only | `test_manifest_version_gate`, `test_art_coverage` header |

`test_anchor_lock` deserves naming as the *correct* pattern rather than as a
finding: it monkeypatches the absence of `game_ref/` and asserts on it, so a
bare clone is the case under test rather than the case that breaks it.

**Noted, not fixed, out of A2's bounded scope** (a weaker class, recorded so
it is not re-discovered as new): `test_local_reference_mode` asserts that
committed-only mode does *not* see `game_ref/`. Its pass/fail is
machine-independent — it never goes red on a bare clone — but on a tree
without `game_ref/` it is vacuously true and carries no evidence. That is
"the assertion is empty here", not "the test reports the machine". If a
third instance of the *A1* class ever appears, the fix is the lint the sprint
doc specifies (a fixture running collection against a simulated bare clone),
not a third spot repair.

### A3 — archived-tool importability — 2 files, not 1

`tools/archive/banner_variance_cells.py` computed repo root as
`Path(__file__).resolve().parent.parent`. That was correct in `tools/`; after
the audit moved it into `tools/archive/` it lands on `tools/` and the module
is unimportable.

The bounded sweep found the **same defect in `render_card_gallery.py`**,
archived in the same commit, with an extra hop: its second `sys.path.insert`
pointed at the script's own directory to reach `art_fetch`, which stayed in
`tools/`. Both fixed to `parents[2]`; the gallery's second insert now points
at `ROOT / "tools"`. Both verified to import.

This is instance 2 of the *archiving* class (distinct from A2's
"reports the machine" class); at instance 3 it should become a lint that
imports every module under `tools/archive/`.

### A4 — orphan comment fragment

`tier0/constants.py` carried a dangling trailing-comment continuation
(`# fraction, otherwise remove a card`) on its own line under
`REST_PREFIGHT_HEAL_THRESHOLD`, left behind when its owning constant was
deleted. Deleted. (The audit cites it at `:563`; R67/R71 have since moved it
to `:579`.)

### Exit gate — MET

`git clone --depth 1` of the working branch, no art, no `.venv` in the tree:

```
871 passed, 21 skipped in 77.35s
```

Same tree on the art-present development machine: `892 passed`. The 21-test
delta is exactly the artifact-gated set, which is the guarded class behaving
as designed.
