#!/usr/bin/env python3
"""Run the repo's lint battery CONCURRENTLY and report every result.

The battery is fifteen CI invocations plus five that only ever run locally,
and until now the only way to run it was to paste twenty lines from
`OPERATIONS.md` / `.github/workflows/repo.yml` one at a time. Pasted serially
they cost the sum of their runtimes; run as separate processes they cost the
slowest one, because each is an independent short-lived Python process with no
shared state -- they read committed files and exit.

Three properties this wrapper has that a pasted list does not:

  * **It reports, it does not judge.** Every tool's exit code is printed the
    same way, including the ones known to be red today. `lint_role_tempo_coverage
    --gate` exits 1 on `main` (disclosed furina/spotlight tempo debt); it shows
    up here as `FAIL` like anything else. A wrapper that special-cases a known
    red is a wrapper you cannot trust when a second thing goes red.
  * **It cannot go stale silently.** `tools/lint_*.py` is globbed and compared
    against the registry below; a lint that is neither registered nor
    explicitly declared suite-gated fails the run under the name
    `registry-coverage`. The failure mode this prevents is a new gate that
    nobody runs because nobody edited the list.
  * **It declares the child console.** EB-93: a tool that echoes shipped card
    titles (`U+266A`) raises `UnicodeEncodeError` when its stdout is a pipe on
    a cp1252 host, and takes the exit code with it. The children are given
    `PYTHONIOENCODING=utf-8:backslashreplace` so a captured run and a terminal
    run agree.

Usage:

    python tools/run_lints.py               # the push gate: CI lane + local lane
    python tools/run_lints.py --all         # ... plus the suite-gated lints
    python tools/run_lints.py --serial      # one at a time (the comparison arm)
    python tools/run_lints.py --list        # print the registry, run nothing
    python tools/run_lints.py --only constant-parity,op-parity

Exit code is 1 if any tool failed (or if the registry is stale), else 0.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from understudy.report import console_safe          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Lanes:
#   ci      -- invoked by the `lints` job in .github/workflows/repo.yml
#   local   -- OPERATIONS.md "Local-only (not in CI)"; a runner has no art and
#              no game, so these answer questions CI structurally cannot ask
#   suite   -- already exercised by pytest (tools/README.md "Suite-gated");
#              excluded from the default run because `pytest` covers them, and
#              running them twice buys nothing. `--all` includes them.
#   library -- registered so the coverage check can see them, never RUN here:
#              they take arguments the suite supplies and have no standalone
#              CLI contract, so a bare invocation is a usage error rather than
#              a finding. `--all` does not include this lane; `--list` shows it.
LANES = ("ci", "local", "suite", "library")
RUNNABLE = ("ci", "local", "suite")


@dataclass(frozen=True)
class Lint:
    name: str
    lane: str
    args: tuple[str, ...]
    note: str = ""

    @property
    def script(self) -> str:
        return self.args[0]

    def command(self) -> list[str]:
        return [sys.executable, *self.args]


def _ci(name: str, *args: str) -> Lint:
    return Lint(name, "ci", args)


def _local(name: str, *args: str) -> Lint:
    return Lint(name, "local", args)


def _suite(name: str, *args: str) -> Lint:
    return Lint(name, "suite", args)


def _library(name: str, script: str, note: str) -> Lint:
    return Lint(name, "library", (script,), note)


# Order is the CI file's order, then OPERATIONS' local list, then the
# suite-gated remainder. Concurrency makes the order cosmetic; it is kept
# readable so this table can be diffed against repo.yml by eye.
REGISTRY: tuple[Lint, ...] = (
    _ci("handwritten-parity",   "tools/lint_handwritten_parity.py"),
    _ci("constant-parity",      "tools/lint_constant_parity.py"),
    # EB-89. Beside constant-parity in the CI file for the same reason it is
    # beside it here: the same hazard class, the half that reads PROSE
    # instead of constants.
    _ci("prose-constants",      "tools/lint_prose_constants.py"),
    _ci("op-parity",            "tools/lint_op_parity.py"),
    _ci("sly-grammar",          "tools/lint_sly_grammar.py"),
    _ci("codegen-staleness",    "tools/gen_roster_cards.py", "--check"),
    _ci("pool-membership",      "tools/lint_pool_membership.py"),
    _ci("ancient-coverage",     "tools/lint_ancient_coverage.py"),
    _ci("role-tempo-artifacts", "tools/suggest_role_tempo_tags.py", "--check"),
    _ci("role-tempo-coverage",  "tools/lint_role_tempo_coverage.py", "--gate"),
    _ci("roster-registry",      "tools/lint_roster_registry.py"),
    _ci("r-numbers",            "tools/lint_r_numbers.py"),
    # EB-127. Beside r-numbers deliberately: same question (an id namespace
    # with no gate), the other series.
    _ci("register-ids",         "tools/lint_register_ids.py"),
    # Governance correction C, 2026-08-26. Third of the R-namespace trio:
    # r-numbers says a citation is IN RANGE, this says the citation can be
    # RESOLVED -- every cited id has a row in docs/current/RULINGS.md. CI lane
    # because the half that bites there reads two files and no history; the
    # staleness half needs the retired ledgers, so on the depth-1 checkout it
    # skips itself and says so on stdout rather than failing blind.
    _ci("rulings-index",        "tools/lint_rulings_index.py"),
    # EB-109. Structural, over committed source, so it runs where the other
    # invisible-seam gates run: an enchanted id became reachable at
    # RUNTEMPLATE 10 and turned correct `+ SUFFIX` sites wrong without anyone
    # editing them.
    _ci("upgrade-suffix-appends", "tools/lint_upgrade_suffix_appends.py"),
    _ci("vendor-pin",           "tools/lint_vendor_pin.py"),
    _ci("art-coverage",         "tools/art_coverage.py"),

    _local("text-encoding",       "tools/lint_text_encoding.py"),
    _local("generated-structure", "tools/lint_generated_structure.py"),
    _local("art-lint",            "tools/art_lint.py"),
    _local("card-distinctness",   "tools/card_distinctness_report.py", "--gate"),
    _local("game-ref-backup",     "tools/lint_game_ref_backup.py"),

    _suite("companion-shop-coverage",  "tools/lint_companion_shop_coverage.py"),
    _suite("effect-branch-scans",      "tools/lint_effect_branch_scans.py"),
    _suite("enchant-parity",           "tools/lint_enchant_parity.py"),
    _suite("furina-registers",         "tools/lint_furina_registers.py"),
    _suite("kokomi-decksize",          "tools/lint_kokomi_decksize.py"),
    _suite("recall-exhaust",           "tools/lint_recall_exhaust.py"),
    _suite("register-isolation",       "tools/lint_register_isolation.py"),
    _suite("sheet-comments",           "tools/lint_sheet_comments.py"),
    _suite("strict-domination",        "tools/lint_strict_domination.py"),
    _suite("upgrade-comment-arith",    "tools/lint_upgrade_comment_arithmetic.py"),
    _suite("upgrade-coverage",         "tools/lint_upgrade_coverage.py"),

    _library("unique-names", "tools/lint_unique_names.py",
             "takes explicit sheet paths (`<sheet.yaml> [...]`); bare "
             "invocation exits 2 on usage, which is not a finding. The sheet "
             "list is the suite's -- tier0/tests/test_sheet_lints.py."),
)


@dataclass
class Result:
    lint: Lint
    code: int
    seconds: float
    output: str = field(default="", repr=False)

    @property
    def ok(self) -> bool:
        return self.code == 0


def registry_gaps() -> list[str]:
    """`tools/lint_*.py` files no registry row names.

    The glob is the source of truth for what EXISTS; the registry is the
    source of truth for what RUNS. This is the join, and a non-empty result is
    a failing row rather than a warning -- a lint nobody runs is not a lint.
    """
    registered = {lint.script for lint in REGISTRY}
    on_disk = {p.relative_to(ROOT).as_posix()
               for p in sorted((ROOT / "tools").glob("lint_*.py"))}
    return sorted(on_disk - registered)


def run_one(lint: Lint) -> Result:
    env = dict(os.environ)
    # EB-93, applied to the child: its stdout here is a PIPE, so without this
    # it decodes as the host codepage and a card title with a music note kills
    # the process. utf-8 with backslashreplace never raises.
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            lint.command(), cwd=ROOT, env=env,
            capture_output=True, text=True,
            encoding="utf-8", errors="backslashreplace")
        code, output = proc.returncode, proc.stdout + proc.stderr
    except OSError as exc:                       # missing script, bad exe
        code, output = 127, f"{type(exc).__name__}: {exc}"
    return Result(lint, code, time.perf_counter() - start, output)


def selected(args: argparse.Namespace) -> list[Lint]:
    lanes = set(RUNNABLE) if args.all else {"ci", "local"}
    if args.lane:
        lanes = set(args.lane)
    picks = [lint for lint in REGISTRY if lint.lane in lanes]
    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        unknown = wanted - {lint.name for lint in REGISTRY}
        if unknown:
            raise SystemExit(f"unknown lint name(s): {', '.join(sorted(unknown))}")
        picks = [lint for lint in REGISTRY if lint.name in wanted]
    return picks


def print_table(results: list[Result], wall: float, jobs: int) -> None:
    width = max((len(r.lint.name) for r in results), default=4)
    print()
    print("  " + "seconds".rjust(8) + "  " + "lane".ljust(7) + "  tool")
    for r in sorted(results, key=lambda r: -r.seconds):
        flag = "" if r.ok else f"   <- exit {r.code}"
        print(f"  {r.seconds:8.2f}  {r.lint.lane:<7}  "
              f"{r.lint.name.ljust(width)}{flag}")
    serial = sum(r.seconds for r in results)
    print()
    print(f"  serial sum   {serial:8.2f}s over {len(results)} tool(s)")
    print(f"  wall clock   {wall:8.2f}s at jobs={jobs}")
    if wall > 0:
        print(f"  speedup      {serial / wall:8.2f}x")


def main(argv: list[str]) -> int:
    console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true",
                    help="include the suite-gated lane (pytest already runs "
                         "it); never the library lane, which has no CLI")
    ap.add_argument("--lane", action="append", choices=LANES,
                    help="run exactly these lanes (repeatable)")
    ap.add_argument("--only", help="comma-separated registry names")
    ap.add_argument("--serial", action="store_true",
                    help="one at a time -- the comparison arm, not the gate")
    ap.add_argument("--jobs", type=int, default=0,
                    help="worker count (default: one per tool, capped at 16)")
    ap.add_argument("--list", action="store_true",
                    help="print the registry and exit")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress passing tools' captured output (default)")
    ap.add_argument("--verbose", action="store_true",
                    help="print every tool's captured output, pass or fail")
    args = ap.parse_args(argv)

    if args.list:
        for lane in LANES:
            rows = [lint for lint in REGISTRY if lint.lane == lane]
            print(f"{lane} ({len(rows)}):")
            for lint in rows:
                print(f"  {lint.name:<24} {' '.join(lint.args)}")
                if lint.note:
                    print(f"  {'':<24} -- {lint.note}")
        gaps = registry_gaps()
        print(f"\nunregistered tools/lint_*.py: {gaps or 'none'}")
        return 0

    picks = selected(args)
    jobs = 1 if args.serial else (args.jobs or min(len(picks), 16))
    print(f"run_lints: {len(picks)} tool(s), jobs={jobs}, root={ROOT}")

    results: list[Result] = []
    start = time.perf_counter()
    if jobs == 1:
        for lint in picks:
            r = run_one(lint)
            results.append(r)
            print(f"  [{'ok  ' if r.ok else 'FAIL'}] {r.lint.name} "
                  f"({r.seconds:.2f}s, exit {r.code})", flush=True)
    else:
        # as_completed, not map: map yields in SUBMISSION order, so one slow
        # tool would hold back every finished result behind it and the run
        # would look stalled while sixteen processes were already done.
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            for fut in as_completed([pool.submit(run_one, p) for p in picks]):
                r = fut.result()
                results.append(r)
                print(f"  [{'ok  ' if r.ok else 'FAIL'}] {r.lint.name} "
                      f"({r.seconds:.2f}s, exit {r.code})", flush=True)
    wall = time.perf_counter() - start

    for r in results:
        if r.output and (args.verbose or not r.ok):
            head = "OUTPUT" if r.ok else "FAILED"
            print(f"\n----- {head}: {r.lint.name} "
                  f"({' '.join(r.lint.args)}) exit {r.code} -----")
            print(r.output.rstrip())

    print_table(results, wall, jobs)

    gaps = registry_gaps()
    if gaps:
        print("\n  [FAIL] registry-coverage: tools/lint_*.py not in REGISTRY:")
        for g in gaps:
            print(f"           {g}")

    failed = [r.lint.name for r in results if not r.ok]
    print()
    if failed or gaps:
        print(f"FAILED: {', '.join(failed) or '(registry only)'}"
              + ("  +registry-coverage" if gaps else ""))
        return 1
    print(f"OK: {len(results)} lint(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
