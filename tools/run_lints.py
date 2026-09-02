#!/usr/bin/env python3
"""Run the repo's lint battery CONCURRENTLY and report every result.

The battery is fifteen CI invocations plus five that only ever run locally,
and until now the only way to run it was to paste twenty lines from
`docs/current/operations/lints.md` / `.github/workflows/repo.yml` one at a
time. Pasted serially
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
#   ci      -- the PRE-PUSH gate. The `lints` job in
#              .github/workflows/repo.yml invokes the original sixteen
#              directly; the Correction-D rows added 2026-08-26 (the four
#              register/stamp shape lints and the hook self-tests) are gated
#              HERE and by `tools/hooks/push_gate.py`, which runs exactly
#              `--lane ci`. Putting them in repo.yml is [USER]'s edit, not this
#              branch's -- so this lane is a SUPERSET of that job today, and
#              the divergence is written down rather than assumed away.
#   local   -- operations/lints.md "Local-only (not in CI)"; a runner has no art and
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


# Order is the CI file's order, then operations/lints.md's local list, then the
# suite-gated remainder. Concurrency makes the order cosmetic; it is kept
# readable so this table can be diffed against repo.yml by eye.
REGISTRY: tuple[Lint, ...] = (
    _ci("handwritten-parity",   "tools/lint_handwritten_parity.py"),
    _ci("constant-parity",      "tools/lint_constant_parity.py"),
    # EB-89. Beside constant-parity in the CI file for the same reason it is
    # beside it here: the same hazard class, the half that reads PROSE
    # instead of constants.
    _ci("prose-constants",      "tools/lint_prose_constants.py"),
    # EB-152, and the third row of the same family: constant-parity joins a C#
    # number to a sheet number, prose-constants joins a written number to the
    # constant, and this joins a number the ENGINE PAYS to what the card's face
    # says about it. The playtest that found it ("Klee's cards that give Burst
    # energy are labelled, but Kokomi's are not") is the argument for a gate
    # rather than a test: only a player could see the gap.
    _ci("burst-legibility",     "tools/lint_burst_legibility.py"),
    # EB-164, the fourth row of that family and the one a BLIND READER found.
    # Burst-legibility guards a number that is paid and never printed; this
    # guards a number that is printed and then claimed AGAIN, so the reader
    # adds it twice. Round 2 of the Kokomi slice lost seven verdicts to it.
    _ci("face-scaling",         "tools/lint_face_scaling.py"),
    # EB-169, and the fifth row of that family read from the other end: the
    # four above ask whether a face is honest, this asks whether a face the
    # repo has ALREADY recorded as dishonest can still reach a blind grader.
    _ci("face-defects",         "tools/lint_face_defects.py"),
    # The sixth row of the same family, and the quietest failure of the lot:
    # the others guard a number that is wrong, this guards a WORD that is
    # unexplained. Run B6 said it out loud ("granting Charge and Burst was not
    # explained in its displayed rules text"), and a missing hover tip renders
    # as nothing at all -- no seam, no exception -- so nothing but a join can
    # see it. One row per meter inside that file -- Charge and Burst, and the
    # next meter is a row there rather than a seventh lint here.
    _ci("keyword-meters",       "tools/lint_keyword_meters.py"),
    # EB-153. The same family read one surface over: those six ask whether a
    # card's WORDS are honest, this asks whether a power has a BADGE at all.
    # Its question is answered at boot by KleeSelfCheck R13 and nowhere the
    # repo can see, which is how seven powers kept the base-game placeholder
    # for months with every gate green -- and its second shape (the aura path
    # built by string concatenation) has no case for anyone to forget.
    _ci("power-icons",          "tools/lint_power_icons.py"),
    # 2026-08-30: three marker lines shipped to main inside BACKLOG.md when a
    # fold fixed a DUPLICATE-row finding without reading its context. Markers
    # are invisible to every register lint, so they get their own gate.
    _ci("conflict-markers",     "tools/lint_conflict_markers.py"),
    _ci("op-parity",            "tools/lint_op_parity.py"),
    _ci("sly-grammar",          "tools/lint_sly_grammar.py"),
    _ci("codegen-staleness",    "tools/gen_roster_cards.py", "--check"),
    # EB-147 (R213 B). The prototype surface is quarantined from every
    # MEASUREMENT tool and from the release build -- it is NOT quarantined
    # from correctness. Its emitted C# is committed, so it can go stale
    # exactly like the roster's, and a stale prototype roster is what sends a
    # slice to the funnel carrying a card that is not the card the sheet
    # says. Cheap on an empty surface, and it needs no game_ref.
    _ci("prototype-codegen",    "tools/gen_prototype_cards.py", "--check"),
    # EB-190, beside the codegen gate for the reason burst-legibility sits
    # beside constant-parity: same file, the other hazard. The codegen gate
    # asks whether the surface still says what the C# says; this asks whether
    # the surface records WHO WROTE each row, and whether any committed grade
    # under review/qa/ was produced by a family that contributed to the row it
    # graded. Carries a curated debt set -- the four Klee slice 1 records this
    # row was opened for -- so it is green today and bites on the next one.
    _ci("prototype-authorship", "tools/lint_prototype_authorship.py"),
    # EB-225 (R225 item 6, M66 pick 2), the third row on the same surface for
    # the third hazard: the codegen gate asks whether the surface still matches
    # the C#, authorship asks who wrote it, and this asks whether the C# is SAFE
    # TO RUN under the single PROTOTYPE_CARDS switch M66 kept. Every Harmony
    # patch in the three quarantined directories must be character-scoped (one
    # flag compiles two arms, so an unscoped patch acts on the other arm's seat
    # -- EB-194, EB-221) and seat-guarded (`LocalContext.GetMe` THROWS on a
    # seatless combat: d217b4f, two whole blind sessions). Exemptions are
    # `// lint: no-seat` markers and are printed on every run, green or red.
    _ci("prototype-patch-scope", "tools/lint_prototype_patch_scope.py"),
    _ci("pool-membership",      "tools/lint_pool_membership.py"),
    _ci("ancient-coverage",     "tools/lint_ancient_coverage.py"),
    # EB-255, beside pool-membership's family because it asks the other
    # question about the same two lists: that one asks whether every card is
    # IN a pool, this asks whether the STARTER and the draftable pool are the
    # disjoint, rarity-separated sets `tier05.draft.archetype_shares` says
    # they are. [USER]'s solo playtest found it from the far end -- a starter
    # card read back as a card the drafter chose. Carries a curated debt set
    # (thirteen rows, one of them the live contamination) so it is green today
    # and bites on the fourteenth; the flagged arms are walked too, because
    # the second contaminator is one flag away.
    _ci("starter-pool-overlap", "tools/lint_starter_pool_overlap.py"),
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

    # --- Correction D (2026-08-26): the governance rules that were prose ---
    # Each ships GREEN by carrying a curated DEBT set of the rows failing
    # today, the structurally-invisible-defects pattern: the gate binds from
    # this commit forward while the existing rows are a work list. A DEBT
    # entry that has since become clean FAILS, so the sets can only shrink.
    _ci("register-shape",       "tools/lint_register_shape.py"),
    _ci("stamp-rows",           "tools/lint_stamp_rows.py"),
    _ci("sheet-stamp",          "tools/lint_sheet_stamp.py"),
    _ci("experiments-active",   "tools/lint_experiments_active.py"),
    # The review tree's three directories, and the paths that cite them.
    _ci("review-status",        "tools/lint_review_status.py"),
    # EB-228, and the other half of review-status's question: that one asks
    # whether a packet SAYS what it is, this asks whether a packet that HOLDS
    # live work on a pick ever reached a register. Kokomi slice 2 sec.9 PICK 2
    # held round-2 staging and minted no QUEUE row, so STATE.md read clean and
    # a round-2 run was scheduled and stopped at the door on 2026-08-30.
    _ci("packet-holds",         "tools/lint_packet_holds.py"),
    # The hooks under tools/hooks/ are the only code here that no test imports
    # and no lint reads -- they run out of process, on stdin JSON. A refusal
    # that quietly stopped refusing looks exactly like a session that never
    # tried the forbidden thing, so their self-tests are gated like anything
    # else, in the lane push_gate.py itself runs.
    _ci("hook-self-tests",      "tools/hooks/selftest_all.py"),

    _local("text-encoding",       "tools/lint_text_encoding.py"),
    _local("generated-structure", "tools/lint_generated_structure.py"),
    _local("art-lint",            "tools/art_lint.py"),
    _local("card-distinctness",   "tools/card_distinctness_report.py", "--gate"),
    _local("game-ref-backup",     "tools/lint_game_ref_backup.py"),
    _local("game-assemblies-backup", "tools/lint_game_assemblies_backup.py"),

    _suite("companion-shop-coverage",  "tools/lint_companion_shop_coverage.py"),
    _suite("effect-branch-scans",      "tools/lint_effect_branch_scans.py"),
    _suite("enchant-parity",           "tools/lint_enchant_parity.py"),
    _suite("furina-registers",         "tools/lint_furina_registers.py"),
    _suite("kokomi-decksize",          "tools/lint_kokomi_decksize.py"),
    _suite("recall-exhaust",           "tools/lint_recall_exhaust.py"),
    _suite("register-isolation",       "tools/lint_register_isolation.py"),
    _suite("sheet-comments",           "tools/lint_sheet_comments.py"),
    # The other half of the sheet-comment pair (2026-09-01): `sheet-comments`
    # checks that the prose on a sheet is TRUE, this one checks that there is
    # not too much of it for an agent to open the sheet cheaply.
    _suite("sheet-comment-blocks",     "tools/lint_sheet_comment_blocks.py"),
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
