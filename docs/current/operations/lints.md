## Lints

`tools/run_lints.py` is the one entry point. It runs the battery concurrently,
prints one row per tool with its exit code, and fails the run if a
`tools/lint_*.py` exists that no registry row names.

```sh
python tools/run_lints.py --lane ci      # the gate: CI and the pre-push hook run exactly this
python tools/run_lints.py                # ci + local lanes
python tools/run_lints.py --list         # every lint, by lane
python tools/run_lints.py --only op-parity,stamp-rows
```

Lanes (the registry in `run_lints.py` is the only list):

- **`ci`**: the gate. The `lints` job in `.github/workflows/repo.yml` runs
  `--lane ci` and nothing else, and so does `tools/hooks/pre_push_gate.py`.
  Every row must pass on a fresh shallow clone with no `game_ref/`, no art and
  no game. To add a lint to CI, add a `_ci(...)` row; there is no second list.
- **`local`**: needs art, `game_ref/` or the game (`text-encoding`,
  `generated-structure`, `art-lint`, `card-distinctness --gate`,
  `game-ref-backup`, `game-assemblies-backup`).
- **`suite`**: already run inside pytest; `--all` includes them.
- **`library`**: registered for the coverage check, never run bare.

`tools/README.md` maps which tool is gated by what.

Notes on individual lints:

- `lint_sheet_stamp.py --update` re-pins `SHEET_DIGEST` after a sheet edit, in
  the same commit as the edit. It guards Balance-stage measurement: a sheet
  edit must move a stamp.
- `lint_prototype_patch_scope.py` (`EB-225`) walks the three `Compile Remove`
  prototype directories: every Harmony patch there must be character-scoped and
  seat-guarded (`LocalContext.GetMe` THROWS on a seatless combat, `d217b4f`);
  the only exemption is a `// lint: no-seat: <reason>` marker, printed on
  every run.
- `lint_text_conventions.py` checks every prototype-arm face, keyword tip,
  power badge, relic and prompt against the ceilings measured on the base
  game's own loc tables and the spellings `docs/current/text-conventions.md`
  fixes, with a curated exception list. `--self-test`, `--shipped` (report the
  shipped sheets without gating), `--census`.
- `lint_recall_exhaust.py` (`EB-118`) is suite-gated through
  `tier0/tests/test_eb118_recall_exhaust.py`; its three sweeps and why leg (a)
  is vacuous are in its docstring.

A lint that ships green over existing debt carries a curated `DEBT` set: an
entry that has since become clean FAILS, so the set only shrinks.

Retired 2026-09-23 with the register and ruling machinery: `r-numbers`,
`rulings-index`, `register-ids`, `register-shape`, `experiments-active`,
`review-status`, `packet-holds`, and the tools `gen_rulings_index`,
`mint_row`, `row`, `register_io`. Retrieve any of them with
`git show 2b73880a:tools/<file>`.

**Encoding rule, repo-wide:** every text read/write declares `encoding=` (an
omitted encoding is cp1252 on Windows, UTF-8 on CI). The rule extends to
`sys.stdout` (EB-93): an entry point that prints shipped content (card titles
carry `♪`) calls `understudy.report.console_safe()` at the top of `main`.
