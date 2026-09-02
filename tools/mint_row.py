#!/usr/bin/env python3
"""Mint one register row: the id, the pipe syntax, the 600-char gate, the lints.

THE RITUAL THIS REPLACES. Minting a BACKLOG row was five manual steps -- read
the ceiling out of `lint_register_ids.py`, take the next number, hand-write
`| `EB-n` | **Scope:** ... |`, eyeball it against the 600-character shape
limit, edit the lint's two constants, then run two lints and hope. Four of
those steps are mechanical and one of them (the constants) no longer exists:
since 2026-09-02 the id ceiling is DERIVED, so a mint edits its register and
nothing else (`docs/current/operations/register-ids.md`).

WHAT IT REFUSES TO DO FOR YOU. It does not write the row's words. `--scope`,
`--next-action`, `--gate` and `--acceptance` are required and are printed
verbatim: BACKLOG's own contract is that a row is those four things, and a
tool that defaulted any of them would mint rows that pass the shape lint and
say nothing. `--gate none` is the legitimate spelling of "nothing is holding
this", and it has to be typed.

THE ID. Derived: `max(every id both registers define, every RETIRED number)`
plus one. Two branches minting in parallel therefore take the SAME number and
neither notices -- by design, because that collision now surfaces as the id
lint's `DUPLICATE` finding on the merged tree instead of as a merge conflict in
a shared constant. The number is PRINTED so it lands in the branch's own diff
and commit message. `--id` overrides, for a packet that reserved a number.

    python tools/mint_row.py BACKLOG tools --scope "..." --next-action "..." \
        --gate none --acceptance "..." --provenance "R240"        # dry run
    python tools/mint_row.py BACKLOG tools ... --write            # and insert
    python tools/mint_row.py QUEUE 5 --decision "**CHOOSE** between (1) ..." \
        --status "OPEN -- gated on the round" --provenance "..." --oneline

Exit 0 when the row is inside its register's limits and (with `--write`) both
register lints pass; 1 otherwise.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import register_io                                        # noqa: E402

REPO = Path(__file__).resolve().parent.parent

#: The two shape ceilings, read off `lint_register_shape.py` rather than
#: copied: a minting tool that believed a different limit from the gate would
#: mint rows the gate refuses, which is the whole failure this replaces.
LINTS = ("tools/lint_register_shape.py", "tools/lint_register_ids.py")


def _shape_limits() -> dict[str, int]:
    import importlib.util
    path = REPO / "tools" / "lint_register_shape.py"
    spec = importlib.util.spec_from_file_location("lint_register_shape", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {"BACKLOG": mod.BACKLOG_MAX, "QUEUE": mod.QUEUE_MAX}


def backlog_row(cid: str, scope: str, next_action: str, gate: str,
                acceptance: str, provenance: str, status: str = "") -> str:
    """BACKLOG's declared four fields, in the order the register states them."""
    opener = f"**{status.strip()}** " if status.strip() else ""
    return (f"| `{cid}` | {opener}**Scope:** {scope} **Next action:** "
            f"{next_action} **Gate:** {gate} **Acceptance:** {acceptance} "
            f"| {provenance} |")


def queue_row(cid: str, decision: str, status: str, provenance: str) -> str:
    """QUEUE's three: the ask (with its pick list), the gated status, the source."""
    return f"| `{cid}` | {decision} | {status} | {provenance} |"


def build(args) -> tuple[str, str]:
    """`(id, row text)` for the arguments given."""
    if args.id:
        cid = args.id
    else:
        series, number = register_io.next_free(args.register)
        cid = f"{series}-{number}" if series == "EB" else f"{series}{number}"
    if args.register == "BACKLOG":
        missing = [n for n, v in (("--scope", args.scope),
                                  ("--next-action", args.next_action),
                                  ("--gate", args.gate),
                                  ("--acceptance", args.acceptance))
                   if not v]
        if missing:
            raise SystemExit(f"BACKLOG rows carry four fields; missing "
                             f"{', '.join(missing)}. The register's own "
                             f"contract, and `lint_register_shape` gates it.")
        row = backlog_row(cid, args.scope, args.next_action, args.gate,
                          args.acceptance, args.provenance or "-", args.status)
    else:
        if not args.decision or not args.status:
            raise SystemExit("QUEUE rows carry an ask with a numbered pick "
                             "list (--decision) and a gated status "
                             "(--status), per R136 and lint_register_shape.")
        row = queue_row(cid, args.decision, args.status, args.provenance or "-")
    return cid, row


def run_lints() -> list[tuple[str, int, str]]:
    """`[(lint, exit code, last line)]` for the two register gates."""
    out = []
    for rel in LINTS:
        res = subprocess.run([sys.executable, str(REPO / rel)],
                             capture_output=True, text=True, cwd=str(REPO))
        tail = [l for l in (res.stdout or "").strip().split("\n") if l.strip()]
        out.append((rel, res.returncode, tail[-1] if tail else ""))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("register", choices=sorted(register_io.REGISTERS))
    ap.add_argument("section",
                    help="the section heading to insert under; a unique "
                         "prefix is enough (`tools`, `tier0.5`, `5`)")
    ap.add_argument("--id", default="",
                    help="force this id instead of the derived next free one")
    ap.add_argument("--status", default="",
                    help="BACKLOG: an opener such as `OPEN 2026-09-02.`")
    ap.add_argument("--scope", default="")
    ap.add_argument("--next-action", default="")
    ap.add_argument("--gate", default="")
    ap.add_argument("--acceptance", default="")
    ap.add_argument("--decision", default="",
                    help="QUEUE: the ask, with its numbered pick list")
    ap.add_argument("--provenance", default="")
    ap.add_argument("--write", action="store_true",
                    help="insert the row at the top of the section's table "
                         "and run both register lints")
    ap.add_argument("--oneline", action="store_true",
                    help="one line: the id, the length, the verdict")
    args = ap.parse_args(argv)

    cid, row = build(args)
    limit = _shape_limits()[args.register]
    length = len(row)
    fits = length <= limit

    if not args.write:
        if args.oneline:
            print(f"mint_row: {cid} {length}/{limit} chars "
                  f"{'ok' if fits else 'TOO LONG'} (dry run, nothing written)")
        else:
            print(row)
            print()
            print(f"id:     {cid} ({'forced' if args.id else 'derived'})")
            print(f"length: {length} chars against the {limit} gate -- "
                  f"{'ok' if fits else 'TOO LONG, shorten it'}")
            print(f"target: {args.register} section {args.section!r}")
            print("dry run; add --write to insert it")
        return 0 if fits else 1

    if not fits:
        print(f"REFUSED: {length} chars against the {limit} gate. Shorten the "
              f"row rather than landing one the shape lint will fail.")
        return 1
    line = register_io.insert_row(args.register, args.section, row)
    results = run_lints()
    ok = all(code == 0 for _, code, _ in results)
    if args.oneline:
        print(f"mint_row: {cid} written to "
              f"{register_io.REGISTERS[args.register]}:{line} "
              f"({length}/{limit} chars); lints "
              f"{'green' if ok else 'RED'}")
        return 0 if ok else 1
    print(f"minted {cid}")
    print(f"  {register_io.REGISTERS[args.register]}:{line}  "
          f"({length}/{limit} chars)")
    for rel, code, tail in results:
        print(f"  [{'ok  ' if code == 0 else 'FAIL'}] {rel}: {tail}")
    if not ok:
        print("\nThe row is written and a gate is red -- fix or revert it "
              "before committing.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
