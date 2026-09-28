#!/usr/bin/env python3
"""Split the CI test suite into N shards by file, balanced by measured time.

WHY THIS EXISTS (2026-09-28). The `pytest` job in `.github/workflows/repo.yml`
ran the whole of `tier0/tests` + `tier05/tests` on one 4-vCPU runner and took
8.5 minutes of an 8.8-minute job. The repo is public, so runners cost nothing;
four runners at once each run a quarter. This tool decides which quarter.

THE UNIT IS A FILE, never a test. `-n auto --dist loadscope` inside each shard
keeps a module on one worker so a module-scoped battery fixture is computed
once; splitting a module across shards would compute it once per shard. So a
module lives whole in exactly one shard.

THE BALANCE. `.github/test-durations.json` holds each file's measured seconds
(setup + call + teardown, from a JUnit report). Files go heaviest first to the
shard whose estimated wall clock grows least, where a shard's wall clock is
estimated as the larger of (its total / the workers it has) and (its heaviest
single file) -- a file cannot be faster than itself on one worker. The
numbers only steer the balance; a stale or missing number can make a shard
slower, NEVER make a test not run.

FAIL SAFE, which is the point of the design:

  * The file list comes from the disk, not from the durations file. A test
    file nobody has timed yet gets the mean weight and lands in SOME shard; a
    durations entry for a deleted file is ignored.
  * `--verify` runs `pytest --collect-only` over the full suite and over each
    shard and refuses unless the shards' node ids are disjoint and their
    union is exactly the full collection. The `lints` job runs it on every
    change, so a test that no shard would run fails CI instead of vanishing.
  * An empty shard is refused, because `pytest` with no path argument would
    collect the whole repository rather than nothing.

    python tools/ci_shards.py --shard 1 --of 4     # that shard's files
    python tools/ci_shards.py --of 4 --show        # the plan, with estimates
    python tools/ci_shards.py --of 4 --verify      # the collection audit
    python tools/ci_shards.py --update-durations report.xml
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOTS = ("tier0/tests", "tier05/tests")
DURATIONS = REPO / ".github" / "test-durations.json"
# pytest's default `python_files`; pytest.ini sets none. `--verify` is what
# actually proves this matches what pytest collects.
PATTERNS = ("test_*.py", "*_test.py")
WORKERS = 4          # `-n auto` on GitHub's standard ubuntu runner


def discover(repo: Path = REPO) -> list[str]:
    """Every test file under ROOTS, as sorted repo-relative posix paths."""
    found: set[str] = set()
    for root in ROOTS:
        for pattern in PATTERNS:
            for path in (repo / root).rglob(pattern):
                if "__pycache__" not in path.parts:
                    found.add(path.relative_to(repo).as_posix())
    return sorted(found)


def load_durations(path: Path = DURATIONS) -> dict[str, float]:
    if not path.exists():
        return {}
    return {k: float(v) for k, v in
            json.loads(path.read_text(encoding="utf-8")).items()}


def _estimate(total: float, heaviest: float, workers: int) -> float:
    return max(total / workers, heaviest)


def partition(files: list[str], durations: dict[str, float], shards: int,
              workers: int = WORKERS) -> list[list[str]]:
    """`shards` disjoint lists whose union is exactly `files`. Deterministic."""
    if shards < 1:
        raise ValueError("need at least one shard")
    known = [durations[f] for f in files if f in durations]
    default = sum(known) / len(known) if known else 1.0
    weight = {f: durations.get(f, default) for f in files}
    order = sorted(files, key=lambda f: (-weight[f], f))
    bins: list[list[str]] = [[] for _ in range(shards)]
    total = [0.0] * shards
    heaviest = [0.0] * shards
    def after(i: int, w: float) -> tuple:
        # The slowest shard's estimate if `w` joins shard i; then, among
        # placements that leave that the same, the least-loaded shard.
        new = _estimate(total[i] + w, max(heaviest[i], w), workers)
        rest = [_estimate(total[j], heaviest[j], workers)
                for j in range(shards) if j != i]
        return (max([new, *rest]), total[i] + w, i)

    for f in order:
        w = weight[f]
        best = min(range(shards), key=lambda i: after(i, w))
        bins[best].append(f)
        total[best] += w
        heaviest[best] = max(heaviest[best], w)
    # Heaviest first WITHIN a shard too: pytest collects in argument order and
    # xdist's loadscope hands out modules in collection order, so the long
    # batteries start at once instead of after the short files ahead of them
    # in the alphabet.
    return [sorted(b, key=lambda f: (-weight[f], f)) for b in bins]


def shard_files(index: int, shards: int) -> list[str]:
    """Shard `index` (1-based) of `shards`. Refuses an empty shard."""
    if not 1 <= index <= shards:
        raise SystemExit(f"--shard must be 1..{shards}, got {index}")
    files = partition(discover(), load_durations(), shards)[index - 1]
    if not files:
        raise SystemExit(
            f"shard {index}/{shards} is empty; `pytest` with no path would "
            "collect the whole repository. Use fewer shards.")
    return files


def _collect(paths: list[str]) -> set[str]:
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", *paths],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise SystemExit(f"collection failed for {len(paths)} path(s):\n"
                         f"{res.stdout[-4000:]}\n{res.stderr[-4000:]}")
    return {line for line in res.stdout.splitlines() if "::" in line}


def verify(shards: int) -> int:
    """The collection audit: the shards' node ids partition the full suite."""
    full = _collect(list(ROOTS))
    seen: dict[str, int] = {}
    problems: list[str] = []
    for i, files in enumerate(partition(discover(), load_durations(), shards),
                              start=1):
        if not files:
            problems.append(f"shard {i} is empty")
            continue
        for node in _collect(files):
            if node in seen:
                problems.append(f"{node} is in shard {seen[node]} and {i}")
            seen[node] = i
    missing = sorted(full - set(seen))
    extra = sorted(set(seen) - full)
    problems += [f"no shard runs {n}" for n in missing[:50]]
    problems += [f"a shard runs {n}, the full suite does not" for n in extra[:50]]
    if problems:
        print(f"ci_shards --verify: REFUSED ({len(missing)} missing, "
              f"{len(extra)} extra)")
        print("\n".join(problems))
        return 1
    print(f"ci_shards --verify: {len(full)} test ids, {shards} shards, "
          "disjoint, union is the full collection")
    return 0


def update_durations(reports: list[Path]) -> None:
    """Rewrite DURATIONS from JUnit report(s): seconds per test file."""
    per_file: dict[str, float] = {}
    for report in reports:
        for case in ET.parse(report).iter("testcase"):
            cls = case.get("classname") or ""
            parts = cls.split(".")
            # tier0.tests.test_x[.Class] -> tier0/tests/test_x.py
            for n in range(len(parts), 0, -1):
                rel = "/".join(parts[:n]) + ".py"
                if (REPO / rel).is_file():
                    per_file[rel] = per_file.get(rel, 0.0) + float(
                        case.get("time") or 0.0)
                    break
    DURATIONS.write_text(
        json.dumps({k: round(v, 2) for k, v in sorted(per_file.items())},
                   indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(per_file)} files to {DURATIONS.relative_to(REPO)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--of", type=int, default=4, help="number of shards")
    ap.add_argument("--shard", type=int, help="print this shard's files")
    ap.add_argument("--show", action="store_true", help="print the plan")
    ap.add_argument("--verify", action="store_true",
                    help="prove the shards partition the full collection")
    ap.add_argument("--update-durations", nargs="+", type=Path,
                    metavar="JUNIT_XML")
    args = ap.parse_args(argv)
    if args.update_durations:
        update_durations(args.update_durations)
        return 0
    if args.verify:
        return verify(args.of)
    if args.show:
        durations = load_durations()
        files = discover()
        known = [durations[f] for f in files if f in durations]
        default = sum(known) / len(known) if known else 1.0
        for i, b in enumerate(partition(files, durations, args.of), start=1):
            ws = [durations.get(f, default) for f in b]
            print(f"shard {i}: {len(b)} files, {sum(ws):.0f} s summed, "
                  f"heaviest {max(ws):.0f} s, estimate "
                  f"{_estimate(sum(ws), max(ws), WORKERS):.0f} s")
        return 0
    if args.shard is None:
        ap.error("give --shard N, --show, --verify or --update-durations")
    # "\n" even on Windows: a `\r` left on a path by `$(...)` names a file
    # that does not exist.
    sys.stdout.reconfigure(newline="\n")
    print("\n".join(shard_files(args.shard, args.of)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
