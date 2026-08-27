"""CLI for the visual QA gates.

    python -m tools.visual_qa scene-deps
    python -m tools.visual_qa export-log build.log
    python -m tools.visual_qa fallback build.log --policy art-fallbacks.yaml
    python -m tools.visual_qa contract --package klee-mod/dist/stage
    python -m tools.visual_qa contact-sheet art/captures --out sheet.png
    python -m tools.visual_qa all --log build.log --package ...

Exit code is 1 when any gate reports an ERROR (or, with `--strict`, a
WARNING), else 0 -- the same contract every lint in `tools/` already has, so
this can be wired into `tools/run_lints.py` and `klee-mod/build/validate.ps1`
without either of them learning anything new. Neither wiring is done by this
lane: both files are shared and single-owner, and the proposed rows are in
`review/dispatch3/tooling-lanec-handoff.md`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):                             # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.visual_qa import contact_sheet, contract, export_log, fallback, scene_deps
from tools.visual_qa.findings import Report

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PCK_SRC = ROOT / "klee-mod" / "pck-src"
DEFAULT_CSHARP = ROOT / "klee-mod" / "KleeCode"


def _universe(args: argparse.Namespace) -> set[str] | None:
    """The set of resources a scene may reference, or None if unknown."""
    if args.contract:
        parsed = contract.parse(
            Path(args.contract).read_text(encoding="utf-8", errors="replace")
        )
        return parsed.resource_set
    if args.resource_dir:
        base = Path(args.resource_dir)
        return {
            p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()
        }
    return None


def _emit(reports: list[Report], args: argparse.Namespace) -> int:
    failed = False
    for report in reports:
        print(report.render(verbose=args.verbose))
        failed = failed or report.failed(strict=args.strict)
    total = sum(len(r.findings) for r in reports)
    print(
        f"\nvisual_qa: {len(reports)} gate(s), {total} finding(s) -- "
        + ("FAIL" if failed else "OK")
    )
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.visual_qa",
        description=__doc__.splitlines()[0],
    )
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as failures")
    parser.add_argument("--verbose", action="store_true",
                        help="also print NOTE findings (what a gate did not check)")
    sub = parser.add_subparsers(dest="gate", required=True)

    p = sub.add_parser("export-log", help="read a MegaDot build log for errors")
    p.add_argument("log", type=Path)
    p.add_argument("--allow-incomplete", action="store_true",
                   help="do not require the build's completion line")

    p = sub.add_parser("scene-deps", help="check .tscn/.tres references")
    p.add_argument("--pck-src", type=Path, default=DEFAULT_PCK_SRC)
    p.add_argument("--contract", help="pck contract, used as the resource universe")
    p.add_argument("--resource-dir", help="directory used as the resource universe")
    p.add_argument("--csharp", type=Path, default=DEFAULT_CSHARP,
                   help="C# source root for the animation-name cross-check")
    p.add_argument("--no-csharp", action="store_true")

    p = sub.add_parser("fallback", help="check cross-character fallbacks and skips")
    p.add_argument("log", type=Path)
    p.add_argument("--policy", type=Path, default=None)
    p.add_argument("--allow-partial-log", action="store_true")

    p = sub.add_parser("contract", help="check the contract and staged package")
    p.add_argument("--contract", type=Path, default=None)
    p.add_argument("--package", type=Path, default=None)
    p.add_argument("--pck-src", type=Path, default=DEFAULT_PCK_SRC)
    p.add_argument("--pck", type=Path, default=None)
    p.add_argument("--expect-version", default=contract.DEFAULT_VERSION)

    p = sub.add_parser("contact-sheet", help="assemble a deterministic sheet")
    p.add_argument("input_dir", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--columns", type=int, default=contact_sheet.DEFAULT_COLUMNS)
    p.add_argument("--cell", type=int, default=contact_sheet.DEFAULT_CELL)
    p.add_argument("--padding", type=int, default=contact_sheet.DEFAULT_PADDING)

    p = sub.add_parser("all", help="every gate whose inputs were supplied")
    p.add_argument("--log", type=Path, default=None)
    p.add_argument("--policy", type=Path, default=None)
    p.add_argument("--package", type=Path, default=None)
    p.add_argument("--contract", type=Path, default=None)
    p.add_argument("--pck-src", type=Path, default=DEFAULT_PCK_SRC)
    p.add_argument("--resource-dir", default=None)
    p.add_argument("--csharp", type=Path, default=DEFAULT_CSHARP)

    args = parser.parse_args(argv)
    reports: list[Report] = []

    if args.gate == "export-log":
        reports.append(export_log.run(args.log, ROOT,
                                      require_completion=not args.allow_incomplete))
    elif args.gate == "scene-deps":
        reports.append(scene_deps.run(
            args.pck_src, ROOT,
            universe=_universe(args),
            csharp_source=None if args.no_csharp else args.csharp,
        ))
    elif args.gate == "fallback":
        reports.append(fallback.run(
            args.log, args.policy, ROOT,
            require_build_markers=not args.allow_partial_log,
        ))
    elif args.gate == "contract":
        reports.append(contract.run(
            args.contract, ROOT,
            package_dir=args.package,
            pck_src=args.pck_src,
            pck_path=args.pck,
            expected_version=args.expect_version,
        ))
    elif args.gate == "contact-sheet":
        reports.append(contact_sheet.run(
            args.input_dir, args.out, ROOT,
            columns=args.columns, cell=args.cell, padding=args.padding,
        ))
    elif args.gate == "all":
        if args.log:
            reports.append(export_log.run(args.log, ROOT))
            reports.append(fallback.run(args.log, args.policy, ROOT))
        if args.package or args.contract:
            reports.append(contract.run(
                args.contract, ROOT,
                package_dir=args.package, pck_src=args.pck_src,
            ))
        universe = None
        if args.contract and Path(args.contract).is_file():
            universe = contract.parse(
                Path(args.contract).read_text(encoding="utf-8", errors="replace")
            ).resource_set
        elif args.resource_dir:
            base = Path(args.resource_dir)
            universe = {
                p.relative_to(base).as_posix()
                for p in base.rglob("*") if p.is_file()
            }
        reports.append(scene_deps.run(
            args.pck_src, ROOT, universe=universe, csharp_source=args.csharp,
        ))

    return _emit(reports, args)


if __name__ == "__main__":                                # pragma: no cover
    raise SystemExit(main())
