# tools/visual_qa — visual QA gates

Five independent checks over the artefacts a pck build leaves behind. None of
them needs the game, the MegaDot editor, a deployed mod, or a live capture: every
entry point takes explicit file paths, so all five run in CI and on a clean
clone.

Built on the surplus-dispatch-3 tooling rail, lane C (charter label `EB-151`).

| gate | asks | inputs |
|---|---|---|
| `export-log` | did the headless import **or export** log an error? | a captured build log |
| `scene-deps` | does every `.tscn` / `.tres` reference resolve? | `klee-mod/pck-src` (+ optional resource universe, + C# source) |
| `fallback` | did a character silently ship another character's art? | a captured build log + a policy file |
| `contract` | does the package match its contract, and did every committed scene reach the pack? | a staged package dir and/or a contract file |
| `contact-sheet` | assemble a review sheet that is byte-reproducible | a directory of PNGs |

## Running

```
python -m tools.visual_qa scene-deps
python -m tools.visual_qa export-log build.log
python -m tools.visual_qa fallback build.log --policy my-fallbacks.yaml
python -m tools.visual_qa contract --package klee-mod/dist/stage
python -m tools.visual_qa contact-sheet art/captures --out art/sheet.png
python -m tools.visual_qa all --log build.log --package klee-mod/dist/stage
```

Exit code is `1` when any gate reports an ERROR, `0` otherwise — the same
contract every lint in `tools/` has. `--strict` promotes WARNINGs to failures.
`--verbose` also prints NOTE findings, which are each gate saying what it
deliberately did **not** check.

Capturing a build log for the first two gates (the build itself is
[USER]-run — nothing here launches it):

```powershell
tools\build_pck.ps1 *>&1 | Tee-Object -FilePath build.log
```

## Severity

* **ERROR** — fails the gate.
* **WARNING** — printed; fails only under `--strict`.
* **NOTE** — never a failure. A stated known-limit, in the shape
  `validate.ps1` S12 uses for its own.

Every gate also reports `checked: …` counts on every run. A gate that says it
checked nothing did nothing, and that has to be visible without reading the
source — the failure mode `validate.ps1` S8 lived in for its entire life.

## What these gates do NOT do

* They do not replace or edit `klee-mod/build/validate.ps1`'s S-gates. Where
  they overlap (S1's stray-JSON rule, S2's contract sha256) the overlap is
  deliberate: the S-gate is PowerShell and deploy-only, this is Python and
  portable.
* They do not run MegaDot, launch the game, deploy, or read the game
  installation.
* They do not decide anything. `fallback` needs a policy saying which
  cross-character fills are intended; that policy is an art-plan call and this
  package ships only a **sample** (`fixtures/fallback_policy.sample.yaml`).

## Fixtures

`fixtures/` holds the synthetic inputs the tests run on: two build logs (clean
and dirty), a sample contract, two deliberately broken scenes, a sample
fallback policy, a sample art-ledger export, and a generator for capture PNGs.
No binary images are committed — `make_capture_fixtures.py` writes them
deterministically into a temp directory at test time.

## The lane B seam

`ledger_adapter.py` is the only place this package knows anything about the
art/provenance ledger lane B (`EB-148`) is building. It reads five fields —
`asset_id`, `packed_path`, `fallback_from`, `rights_tier`, `review_state` —
through one function, `row_from_mapping`, with an alias table for the column
spellings. Aligning at merge means editing `ALIASES`; nothing else in the
package touches a ledger.

## Tests

```
python -m pytest tier0/tests/test_visual_qa_*.py -q
```
