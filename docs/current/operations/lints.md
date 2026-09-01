## Lints

CI's `lints` job invokes these directly (the softlock gates):

```sh
python3 tools/lint_handwritten_parity.py   tools/lint_constant_parity.py   tools/lint_op_parity.py
python3 tools/gen_roster_cards.py --check
python3 tools/lint_pool_membership.py       tools/lint_ancient_coverage.py
python3 tools/suggest_role_tempo_tags.py --check    tools/lint_role_tempo_coverage.py --gate
python3 tools/lint_roster_registry.py       tools/lint_upgrade_suffix_appends.py
python3 tools/lint_vendor_pin.py            tools/art_coverage.py
```

Correction D added five more to `run_lints`'s `ci` lane that `repo.yml` does
not yet name (`lint_register_shape.py`, `lint_stamp_rows.py`,
`lint_sheet_stamp.py`, `lint_experiments_active.py`,
`tools/hooks/selftest_all.py`) — see Mechanisms. `lint_sheet_stamp.py
--update` is the one that re-pins `SHEET_DIGEST` after a sheet edit, and it
belongs in the same commit as the edit.

`lint_prototype_patch_scope.py` (`EB-225`, R225 item 6) is in that same `ci`
lane and walks the three `Compile Remove` prototype directories: every Harmony
patch there must be character-scoped and seat-guarded (`LocalContext.GetMe`
THROWS on a seatless combat — `d217b4f`), and the only exemption is a
`// lint: no-seat: <reason>` marker, which the tool prints on every run.

Local-only (not in CI): `lint_text_encoding.py`, `lint_generated_structure.py`,
`art_lint.py`, `card_distinctness_report.py --gate`,
`lint_game_ref_backup.py`, `dump_claimed_sources.py`.
`tools/README.md` is the authoritative map of which tool is gated by what.

`tools/run_lints.py` runs the whole battery concurrently and prints one row per
tool with its exit code — see the parallel-suite section. It carries the
registry those two lists describe, and fails the run if a `tools/lint_*.py`
appears that no registry row names, so the list above cannot go stale in
silence.

Suite-gated (runs under `pytest`, not in the CI `lints` job):
`lint_recall_exhaust.py` (`EB-118`, merged **inert** 2026-08-23; gate
`tier0/tests/test_eb118_recall_exhaust.py`).

```sh
python3 tools/lint_recall_exhaust.py       # exit 1 with findings on stdout
```

Three sweeps in one tool — card shape, engine closure, a structural C# pin —
all enforcing `EB-118` §6.4's six constraints on `recall_to_draw` with
`from: exhaust`. Each leg, and why leg (a) is deliberately vacuous until a
committed sheet row ships `from: exhaust`, is in the tool's own docstring.

Encoding rule is repo-wide and structural: **every text read/write declares
`encoding=`** (an omitted encoding is cp1252 on Windows, UTF-8 on CI). The
content path carries zero encoding debt.

**The rule extends to `sys.stdout`** (EB-93, 2026-08-13). A console's encoding
is chosen by the terminal, not by the file that prints, so a tool that echoes
shipped content — card titles carry `♪` — raises `UnicodeEncodeError` on a
default Windows console and takes the process exit code with it. Any entry
point that prints content declares the console too:
`understudy.report.console_safe()` at the top of `main` (UTF-8, falling back to
`backslashreplace`, never raising).
