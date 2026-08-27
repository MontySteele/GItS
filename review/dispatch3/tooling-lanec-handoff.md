# Lane C handoff — visual QA gates

Surplus-dispatch-3, tooling rail, lane C (charter section 5, charter label
`EB-151` — that is the charter's own name for the lane, not a minted BACKLOG
id).

**Branch:** `dispatch3-laneC-visual-qa`, worktree `../GItS-laneC`, cut from
`main` at `223a4ff`.
**Nothing merged, nothing deployed, no PR opened.** The game was never
launched and no file in the primary checkout, in `docs/current/`, in a sheet,
in a constants file, or in any build script was touched.

---

## 1. What this is, in one paragraph

Five independent checks that read the *leftovers* of a pck build — a captured
build log, the committed scene sources, the pck contract, the staged package,
a directory of capture PNGs — and report what is broken. None of them needs
the game, the MegaDot editor, a deployed mod, or a live capture, so all five
run on a clean clone and in CI. They do not replace `validate.ps1`'s S-gates
and do not edit them; they ask questions those gates structurally cannot ask,
because those gates are PowerShell, run only on the deploy path, and several
of them need the game install.

| gate | the question | inputs |
|---|---|---|
| `export-log` | did the headless import **or export** log an error? | a captured build log |
| `scene-deps` | does every reference inside a `.tscn`/`.tres` resolve? | `klee-mod/pck-src` (+ optional resource universe, + C# source) |
| `fallback` | did a character silently ship another character's art? | a build log + a declared policy |
| `contract` | does the package match its contract, and did every committed scene reach the pack? | a staged package dir and/or a contract file |
| `contact-sheet` | build a review sheet that is byte-reproducible | a directory of PNGs |

---

## 2. Exact commands

Everything below runs from the worktree root.

```
# the five gates
python -m tools.visual_qa scene-deps
python -m tools.visual_qa export-log <build.log>
python -m tools.visual_qa fallback <build.log> --policy <policy.yaml>
python -m tools.visual_qa contract --package <staged-package-dir>
python -m tools.visual_qa contact-sheet <png-dir> --out <sheet.png>
python -m tools.visual_qa all --log <build.log> --package <dir>

# --strict promotes warnings to failures; --verbose prints what a gate did NOT check
python -m tools.visual_qa --verbose --strict scene-deps

# the tests
python -m pytest tier0/tests/test_visual_qa_*.py -q          # 63 passed
python tools/run_lints.py --lane ci                          # 22 lint(s) passed
```

To capture a build log for the first two gates — **this is [USER]'s command to
run, not the gate's**; nothing in this lane launches a build:

```powershell
tools\build_pck.ps1 *>&1 | Tee-Object -FilePath build.log
```

### Interpreter note

This worktree has no `.venv`, and the primary checkout's `.venv` is read-only
to this lane, so everything above was run with the machine's own Python 3.14 at
`C:\Users\Monty\AppData\Local\Python\bin\python.exe` (pytest 9.1.1, Pillow
12.3.0 — the same versions the primary venv reports). On a normal machine
`python` off `PATH` or the repo venv is the right interpreter.

---

## 3. Test results

| suite | result |
|---|---|
| `pytest tier0/tests/test_visual_qa_*.py -q` | **63 passed** |
| `python tools/run_lints.py --lane ci` | **22 lint(s) passed** |
| `python tools/run_lints.py --lane local` | 4 passed, `card-distinctness` **exit 2** — pre-existing and environmental: it prints *"no game_ref/ pools found — run tools/extract_base_game_pool.py locally for official anchors"*. `game_ref/` is gitignored local reference data and this worktree has none. Nothing to do with this branch. |
| `pytest tier0/tests tier05/tests -q -m "not battery"` | **3758 passed, 46 skipped, 12 xfailed, 1 failed → then fixed → green.** The one failure was `test_encoding_gate::test_no_new_undeclared_encodings`, caused by two of my own lines; see finding **F5** and the fix. |

**A test-harness trap worth knowing about, because it will bite the next agent
too.** Run through a shell with no valid stdin handle, *every* repo test that
shells out (`test_vendor_pin`, `test_rulings_index`, `test_sheet_lints`, ~74
tests in total) fails with `OSError: [WinError 6] The handle is invalid` inside
`subprocess.Popen`. It is not a repo red — the same tests pass when run from a
normal console. My own CLI test pins `stdin=subprocess.DEVNULL` so it is immune;
the repo's existing subprocess tests do not.

---

## 4. Findings

Each carries a file:line. "Reported, not fixed" means the file belongs to
someone else (a shared build script) and this lane wrote a note instead.

### F1 — the export stage's log is never read for errors *(reported, not fixed)*

`tools/build_pck.ps1:771-778`. The import log is swept for `ERROR`:

```
$importErrors = $importLog | Select-String 'ERROR'
if ($importErrors) { ... throw "MegaDot import reported errors." }
```

The export log gets `$LASTEXITCODE` and nothing else. An export that logs a
missing dependency and still exits 0 goes through clean, and the resulting pack
is short a resource with every gate green. The `export-log` gate attributes
findings to a stage and covers both; the fixture
`tools/visual_qa/fixtures/build_dirty.log` carries one export-stage error
specifically to pin that.

### F2 — the ERROR sweep both over- and under-matches *(reported, not fixed)*

Same site. `Select-String 'ERROR'` in PowerShell is **case-insensitive and
unanchored**, so a resource path containing the letters "error" fails the whole
build. In the other direction, Godot reports several real load failures with no
`ERROR:` prefix at all — `Unrecognized dependency:`, `Failed loading resource`,
`Cannot open file` — and those are invisible to both the grep and the exit
code. The gate matches Godot's prefixes case-**sensitively** and anchored,
carries the un-prefixed failures as their own rule, and pulls in the engine's
`at:` continuation line for context.

### F3 — fallbacks and skipped copy blocks are printed, and gated by nothing *(mechanism built; the policy is [USER]'s)*

`tools/build_pck.ps1:128` (`SKIPPED: …`), `:230` and `:264`
(`Furina fallback: … <- Klee`). The script's own comment at `:196-201` records
what that costs: a `-Exclude` bug dropped **both** Furina and Kokomi back onto
Klee's art, the build went green, and it was *"caught only because the fallback
lines are printed"*. The `fallback` gate turns those lines into a ledger that
fails in **both** directions — an undeclared fallback is a finding, and a
declared fallback the build did not produce is a finding too (the standing
allowlist shape: `validate.ps1` S12's `$pckDeferred`,
`tier0/tests/test_pck_reference_gate.py`). Which of today's real fallbacks are
*intended* is an art-plan call and is left open — see question **Q1**.

### F4 — no rule anywhere opens a scene *(gate built)*

`validate.ps1` S6c (`klee-mod/build/validate.ps1:505-536`) checks that a
C#-referenced `.tscn`/`.tres` is authored somewhere and appears in the
contract. S12 (`:935-1012`) checks that a C#-referenced pck path is packed.
Neither one reads the scene's contents. So a `Sprite2D` pointing at a texture
nobody exports, an `AnimationTree` travelling to a state the `AnimationPlayer`
does not have, or an animation track on a node that was renamed, is invisible
until the game runs — and the AnimationTree case fails **silently at runtime**
(`AnimationNodeStateMachinePlayback.Travel` to a missing state is a no-op), so
"until the game runs" can mean "until somebody notices the character never
plays a hurt animation".

`scene-deps` covers: undeclared/unused `ExtResource`/`SubResource` ids, non-
`res://` paths, `type="Script"` resources (forbidden by
`klee-mod/pck-src/README.md`), animation names an `AnimationNodeAnimation`
plays but no library declares, state-machine transitions touching unknown
states, animation tracks whose `NodePath` matches no node, an `AnimationTree`
whose `anim_player` points at something that is not an `AnimationPlayer`, and —
when a resource universe is supplied — `ext_resource` paths that are not in the
pack. It also cross-checks the six `Play`/`Queue` animation names in C#
(including the interpolated `$"slot{i + 1}_pop"` and `$"fire{index + 1}"` forms,
matched as patterns rather than skipped).

The four required creature states are **read from the source of truth, not
retyped**: a test asserts `scene_deps.CREATURE_STATES` equals the keys of
`CreatureAnimationRouter.TriggerToState`
(`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:45-54`).

### F5 — `lint_text_encoding.py` cannot see `Path.open("rb")` *(reported, worked around locally, not fixed)*

`tools/lint_text_encoding.py:60-70`. `_is_binary_open` reads the mode from
keyword `mode=` or **positional argument index 1**, which is the builtin
`open(path, "rb")` shape. The bound-method shape `path.open("rb")` puts the
mode at index **0**, so it is not recognised as binary and is counted as an
undeclared *text* read. My two chunked-hash / magic-byte reads were flagged by
`test_encoding_gate` for exactly this reason. I rewrote both to the builtin
form with a comment rather than edit a lint this lane does not own. There are
no other `Path.open("rb")` calls in the repo today, so this is latent, not
live — hygiene class, [USER]'s or an integrator's call whether to widen
`_is_binary_open`.

### F6 — two committed scenes have a stale `load_steps` *(advisory, non-blocking)*

| scene | declares | file actually has |
|---|---|---|
| `klee-mod/pck-src/furina/model/combat.tscn` | `load_steps=26` | 4 ext + 20 sub → 25 |
| `klee-mod/pck-src/furina/ui/salon_stage.tscn` | `load_steps=11` | 0 ext + 8 sub → 9 |

In Godot 4 this value feeds the loader's progress counter, not correctness, so
the gate reports it as a **WARNING**, never an error. What it means is that
both files were hand-edited after the editor last wrote them, which is exactly
what `pck-src/README.md` says the directory is for. The other six scenes agree
to the digit. No action proposed; it is here so nobody rediscovers it as a
mystery.

### F7 — NON-FINDINGS (things that are clean, said out loud)

* All eight committed scenes carry **zero** error-severity scene findings.
* All six C# `Play`/`Queue` animation names resolve against a scene that
  declares them.
* Both combat scenes carry the full `idle`/`attack`/`hurt`/`death` state set.
* Every committed `.tscn` has a matching resource row in the fixture contract.
* Every `ext_resource` path in `pck-src` resolves against the fixture contract's
  resource universe (11 textures, all present).

---

## 5. Files added

Nothing was modified. Every path below is new.

```
tools/visual_qa/__init__.py            package doc: what the five gates are
tools/visual_qa/findings.py            Finding/Report, severity, "checked" counts
tools/visual_qa/godot_scene.py         a small .tscn/.tres reader
tools/visual_qa/scene_deps.py          gate 2
tools/visual_qa/export_log.py          gate 1
tools/visual_qa/fallback.py            gate 3
tools/visual_qa/contract.py            gate 4
tools/visual_qa/contact_sheet.py       gate 5
tools/visual_qa/ledger_adapter.py      the lane B seam
tools/visual_qa/__main__.py            the CLI
tools/visual_qa/README.md              how to run it
tools/visual_qa/fixtures/              build logs, contract, policies, scenes, capture generator
tier0/tests/test_visual_qa_export_log.py
tier0/tests/test_visual_qa_scene_deps.py
tier0/tests/test_visual_qa_fallback.py
tier0/tests/test_visual_qa_contract.py
tier0/tests/test_visual_qa_contact_sheet.py
tier0/tests/test_visual_qa_ledger_seam.py
tier0/tests/test_visual_qa_cli.py
review/dispatch3/tooling-lanec-handoff.md   (this file)
```

The CLI is `python -m tools.visual_qa`, **not** `tools/lint_visual_qa.py`. That
is deliberate: `run_lints.py`'s `registry-coverage` check globs
`tools/lint_*.py` and fails on anything unregistered, so a `lint_`-named tool
would have forced an edit to `tools/run_lints.py` — a shared file lane B is
likely to need at the same time. See section 8.

---

## 6. The contact sheet's determinism claim

Exactly this, and nothing wider:

> the same set of input PNGs, in any listing order, on the same machine,
> produces a byte-identical sheet and a byte-identical manifest.

How it is achieved: cells are laid out in sorted POSIX-path order, so a
directory walk's order cannot reach the output; the PNG is encoded in-module
(IHDR + one IDAT + IEND, **no ancillary chunks at all** — asserted by a test
that walks the chunk list), so no timestamp, filename, gamma or library version
is embedded; the resampler is named explicitly rather than left to a Pillow
default that has moved between majors.

The manifest records `rgba_sha256` (the hash of the *uncompressed* canvas)
alongside `png_sha256`, so two machines with different zlib builds can still
prove they composed the same image. The compressed-byte claim is a
same-machine claim and is labelled as one in the module.

**No live captures were taken** — [USER] is playtesting on `0.2-1155` and the
charter forbids launching the game. The tool is proven on five generated
fixture PNGs of deliberately varied size, aspect and transparency. Nothing
about the *capture* half is proven; that is debt, listed below.

---

## 7. The lane B seam

Lane B (`EB-148`, art/provenance ledger) is being built concurrently in its own
worktree. I did not read or edit any of it.

Lane C consumes exactly **five fields** — `asset_id`, `packed_path`,
`fallback_from`, `rights_tier`, `review_state` — through exactly **one
function**, `tools/visual_qa/ledger_adapter.py::row_from_mapping`, which maps
incoming column spellings through an `ALIASES` table. A minimal fixture of the
row shape is at `tools/visual_qa/fixtures/ledger_rows.sample.json`, written
with a deliberate *mix* of key spellings so the aliasing is exercised rather
than assumed.

**Aligning at merge = editing `ALIASES`.** Nothing else in the package knows a
ledger exists, and a test asserts that (`test_lane_c_does_not_import_lane_b_code`).
A mapping that carries none of the aliases for `packed_path` yields `None` and
the gate reports it — never guessed.

Two joins are already implemented against that shape and will start paying the
day a real export exists: a ledger row whose `packed_path` is not in the pck
contract, and an observed build fallback that no ledger row records (the half a
policy file cannot answer: *does the bookkeeping know?*).

---

## 8. Patch notes — shared files this lane did NOT edit

Both are one-owner files. The rows are written out so an integrator can apply
them without re-deriving anything.

**(a) `tools/run_lints.py`** — one registry row, `ci` lane, so `scene-deps`
runs on every push. It is the only gate whose inputs are all committed:

```python
_ci("visual-qa-scenes",     "tools/visual_qa/cli_scene_deps.py"),
```

…except there is no such script, because the CLI is a package entry point. The
minimal change is either a two-line shim at `tools/lint_visual_qa_scenes.py`
that calls `tools.visual_qa.__main__.main(["scene-deps"])`, or teaching
`Lint.command()` to accept `-m`. **Recommendation is PROPOSED and the choice is
the integrator's**, since it touches a shared file's shape. Note that the gate
is already covered by pytest (`tier0/tests/test_visual_qa_scene_deps.py`
asserts the live tree is clean), so it is gated today — the registry row would
add a second, faster signal, not a first one.

**(b) `klee-mod/build/validate.ps1`** — three proposed rules, none written:

| proposed | what it would do | why it is not in this branch |
|---|---|---|
| S17 | pipe the MegaDot import **and export** logs through `python -m tools.visual_qa export-log` | fixes F1/F2, but changes what can block a deploy — [USER]'s call (Q2) |
| S18 | run `contract --package $StageDir` beside S2 | overlaps S2's sha256 deliberately; adds package-shape and scene-source coverage |
| S19 | run `fallback` against a real policy file | blocked on Q1 — there is no policy yet |

---

## 9. Known debt

1. **No live capture run.** The contact-sheet tool is proven on fixtures only;
   the capture half (getting real frames out of the running game) does not
   exist in this lane and was out of scope tonight.
2. **The fallback policy is a sample, not a policy.**
   `tools/visual_qa/fixtures/fallback_policy.sample.yaml` matches the *fixture*
   log. A real one has to be written by whoever owns the art plan.
3. **`scene-deps` needs a resource universe to check texture existence.** The
   live contract is gitignored (`*.pck.contract.txt`), so on a clean machine
   the gate checks shape only and says so (a NOTE, visible under `--verbose`).
   The committed fixture contract is a hand-kept list of the eleven textures
   the scenes reference today; a scene that gains a twelfth will fail
   `test_live_scenes_resolve_against_the_fixture_contract_universe` until the
   fixture is updated. That is intended, and it is also a maintenance cost.
4. **The C# animation-name association is a heuristic.** A `.cs` file that
   names one or more `.tscn` paths is checked against those scenes; one that
   names none is checked against every scene. It cannot produce a false error
   unless a name exists in no scene at all, which is the defect — but it can
   miss a name that exists in the *wrong* scene.
5. **Animation track NodePaths are resolved as if the AnimationPlayer's
   `root_node` were the scene root.** True for all eight scenes today (every
   player is a direct child of the root); a scene that parents its player
   deeper would need the real rule.
6. **State-machine `transitions` are parsed positionally.** Correct for the
   shape Godot writes; a hand-authored malformed array would be read
   optimistically.
7. **`Path.open("rb")` blind spot in `lint_text_encoding.py`** (F5) is reported,
   not fixed.
8. **`load_steps` drift** in two scenes (F6) is reported, not fixed.

---

## 10. Merge risks

1. **Lane B's real column names.** Expected and contained: edit `ALIASES` in
   `ledger_adapter.py`. If lane B's row shape needs a *sixth* field for a QA
   gate to do its job, that is a conversation, not a rename.
2. **`tools/run_lints.py`.** Deliberately untouched. If lane B adds a
   `tools/lint_*.py`, lane B will have to edit it and there is no conflict with
   this branch. If both lanes' patch notes get applied at once, they touch the
   same tuple.
3. **`tier0/tests/` filenames.** All six new files are `test_visual_qa_*.py`;
   no collision with anything on `main` at `223a4ff`.
4. **`tools/visual_qa/` is a new package directory** — no path either lane
   already owned.
5. **The two advisory WARNINGs (F6) mean `--strict scene-deps` exits 1 today.**
   Anyone wiring the gate into a pipeline should either not pass `--strict` or
   land the `load_steps` correction first.
6. **The fixture contract is coupled to `pck-src`.** Adding a scene or a
   texture reference to `pck-src` without updating
   `tools/visual_qa/fixtures/sample.contract.txt` turns two tests red. Loud by
   design; still a coupling a reviewer should know about.

---

## 11. Questions for [USER] — numbered, pick-lists, nothing assumed

**Q1 — the fallback policy.** The `fallback` gate needs a file saying which
cross-character art fills are *intended*. Nobody but you can say that. Which
shape do you want?

1. One curated policy file with a reason and an expected-until note per row,
   living beside the build scripts, and a deploy rule that fails on anything
   undeclared.
2. Same file, but the gate runs as a report only (never blocks a deploy) until
   the art plan settles.
3. No policy file: drive the gate off lane B's ledger instead, using
   `fallback_from` as the declaration (the code for this already exists —
   `ledger_adapter.check_fallbacks`).
4. Leave the gate uninvoked for now; revisit when the art batches land.

**Q2 — should any of these block a deploy?** Section 8 lists three proposed
`validate.ps1` rules. Promoting a check to a deploy gate is the same class of
decision as `-RunCsharpTests` (S16), which is deliberately opt-in today.

1. All three as blocking rules.
2. Export-log only (F1/F2 are real defects in the current build path).
3. All three, but as warnings that print and never throw.
4. None yet — keep them as commands somebody runs on purpose.

**Q3 — the load_steps drift (F6).** Two Furina scenes disagree with their own
resource counts. Cosmetic in Godot 4.

1. Correct both numbers now (a two-character edit each, hygiene class).
2. Leave them and keep the warning.
3. Drop the rule entirely — it only detects hand-editing, which `pck-src`
   exists to permit.

**Q4 — `lint_text_encoding.py`'s blind spot (F5).** `Path.open("rb")` reads as
an undeclared text read.

1. Widen `_is_binary_open` to check positional index 0 as well when the call is
   a bound `.open`.
2. Leave it — there are no such calls in the repo and the failure direction is
   safe (it over-reports, never under-reports).

**Q5 — captures.** The contact-sheet assembler is proven on fixtures. Getting
real frames requires driving the game, which tonight's charter forbids.

1. Next session, wire the sheet to the existing understudy/bot capture path.
2. Keep it fixture-only until there is a specific review that needs a sheet.
3. Something else you have in mind for how captures should be taken.

---

## 12. What this does NOT establish

It does not establish that the current pck is correct: no build was run, no
pack was opened, and no live contract was read. It does not establish that the
art is right, that any fallback is acceptable, or that any scene is *visually*
correct — every check here is structural. It does not establish anything about
capture quality, since no capture was taken. It rules nothing: no mapping, no
taste, no rights, no spend, no scope, no ship call, and no BACKLOG/QUEUE id was
minted.
