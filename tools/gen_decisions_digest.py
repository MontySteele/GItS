"""Generate the current-law digest block in `tier0/DECISIONS.md`.

Track R-D (Clear the Stage, R119 full-AUTHORIZE), plan of record
`review/stage-clear/refactor-plan.md` §R-D. The ledger is split into volumes
(R39–R99 in `tier0/DECISIONS-archive-R39-R99.md`, R100+ live, R73–R80 in
`klee-mod/DECISIONS.md`), so no single file shows a reader the whole ruling
sequence. This tool renders one — one line per ruling: number, date where the
heading records one, a one-line title drawn MECHANICALLY from the ruling's own
heading/entry line, and the sidecar status.

THE GENERATOR CARRIES NO JUDGMENT
---------------------------------
Statuses come from `tier0/decisions-status.tsv`, and that sidecar has NOT had
its [USER] red-pen pass yet (queue: `docs/registry/user-queue.md` §4). So
almost every row is UNREVIEWED, and the digest says so per row rather than
pretending a current-law determination exists. The few non-UNREVIEWED rows are
mechanically derived from explicit strikes/banners in the ledger text; their
evidence is in the sidecar. When the red-pen pass lands, the sidecar gains real
statuses and this digest becomes the current-law surface with zero code change.

Titles are mechanical: for the tier0 volumes, the `## R<n> -- title (date)`
heading line; for `klee-mod/DECISIONS.md`, the `**R<n>. ...**` entry line of
the Neap Tide block (first line only — a wrapped entry line truncates, which is
honest for a digest). Nothing is paraphrased.

THE OUTPUT IS NEVER HAND-EDITED
-------------------------------
The block between the BEGIN/END markers in `tier0/DECISIONS.md` is owned by
this tool, same regime as `known-identifiers.tsv`. `--check` runs in CI
(`.github/workflows/repo.yml`, `lints` job): it regenerates and byte-diffs, so
a hand edit or a stale block fails the build.

Usage:
    python tools/gen_decisions_digest.py --write    # rewrite the block in place
    python tools/gen_decisions_digest.py --check    # CI: fail if stale
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIVE = REPO / "tier0" / "DECISIONS.md"
KLEE = REPO / "klee-mod" / "DECISIONS.md"
SIDECAR = REPO / "tier0" / "decisions-status.tsv"

BEGIN = ("<!-- BEGIN GENERATED current-law digest -- "
         "tools/gen_decisions_digest.py -- DO NOT HAND-EDIT -->")
END = ("<!-- END GENERATED current-law digest -->")

# tier0 volumes: `## R<n> ...` opens an entry. Only the heading line is read.
_T0_HEADING = re.compile(r"^##\s+R(\d+)\b(.*)$")
# klee-mod: the Neap Tide bold-entry idiom, `**R73. ...` — `R73b` is a
# sub-entry of R73 and is skipped (the sequence is integers).
_KLEE_ENTRY = re.compile(r"^\*\*R(\d+)(?![0-9b])(.*)$")
_DATE = re.compile(r"\((\d{4}-\d{2}-\d{2})\)\s*$")


def _tier0_volumes() -> list[Path]:
    """Every tier0 DECISIONS volume present, live file included. Glob, not a
    hardcoded pair, so the tool works both before and after a split lands."""
    return sorted((REPO / "tier0").glob("DECISIONS*.md"))


def _clean_title(raw: str) -> str:
    title = raw.strip()
    title = re.sub(r"^(--|—|-)\s*", "", title)
    m = _DATE.search(title)
    date = m.group(1) if m else ""
    if m:
        title = title[: m.start()].rstrip()
    return date, title


def _harvest() -> dict[int, tuple[str, str, str]]:
    """number -> (date, title, volume-relpath). First declaration wins; the
    duplicate-number lint (tools/lint_ledger_numbers.py) guarantees there is
    only one."""
    out: dict[int, tuple[str, str, str]] = {}
    for vol in _tier0_volumes():
        rel = vol.relative_to(REPO).as_posix()
        for line in vol.read_text(encoding="utf-8").splitlines():
            m = _T0_HEADING.match(line)
            if not m:
                continue
            date, title = _clean_title(m.group(2))
            out.setdefault(int(m.group(1)), (date, title, rel))
    if KLEE.exists():
        rel = KLEE.relative_to(REPO).as_posix()
        for line in KLEE.read_text(encoding="utf-8").splitlines():
            m = _KLEE_ENTRY.match(line)
            if not m:
                continue
            rest = m.group(2)
            bold_end = rest.find("**")
            bold = rest[:bold_end] if bold_end >= 0 else rest
            after = rest[bold_end + 2:] if bold_end >= 0 else ""
            # `**R74.**` carries its text after the bold; `**R73. title**`
            # inside it. Strip the number/qualifier prefix up to the first dot.
            title = re.sub(r"^[^.]*\.\s*", "", bold).strip()
            if not title:
                title = after.strip()
            out.setdefault(int(m.group(1)), ("", title, rel))
    # R1-R38 are OUT OF SCOPE by design: they were never written as headed
    # entries, resolving them is the open queue s.4 back-index question, and
    # this tool must not invent the index. (klee-mod carries bold `**R24.`-
    # style lines for a few of them; whether those ARE the entries is exactly
    # the judgment the queue row owns.)
    return {n: v for n, v in out.items() if n >= 39}


def _sidecar() -> dict[int, str]:
    rows: dict[int, str] = {}
    for line in SIDECAR.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        m = re.fullmatch(r"R(\d+)", parts[0])
        if not m:
            raise SystemExit(f"sidecar: unparseable ruling column: {parts[0]!r}")
        n = int(m.group(1))
        if n in rows:
            raise SystemExit(f"sidecar: duplicate row for R{n}")
        rows[n] = parts[1].strip() if len(parts) > 1 else ""
    return rows


def render() -> str:
    rulings = _harvest()
    statuses = _sidecar()

    missing = sorted(n for n in statuses if n not in rulings)
    extra = sorted(n for n in rulings if n not in statuses)
    problems = []
    if missing:
        problems.append(
            "sidecar rows with no ledger entry in any volume: "
            + ", ".join(f"R{n}" for n in missing))
    if extra:
        problems.append(
            "ledger entries with no sidecar row: "
            + ", ".join(f"R{n}" for n in extra))
    if problems:
        raise SystemExit("gen_decisions_digest: " + "; ".join(problems))

    unreviewed = sum(1 for s in statuses.values() if s == "UNREVIEWED")
    derived = len(statuses) - unreviewed

    lines = [
        BEGIN,
        "",
        f"**{len(statuses)} rulings across the volumes — "
        f"{derived} status-derived mechanically from explicit "
        f"strikes/banners, {unreviewed} UNREVIEWED.** UNREVIEWED means the "
        "sidecar's [USER] red-pen pass (queue: "
        "`docs/registry/user-queue.md` §4) has not read that row; it is not "
        "a judgment that the ruling is or is not current law. Statuses and "
        "evidence: `tier0/decisions-status.tsv`. Volume resolution: "
        "`docs/registry/identifiers.md` §3.",
        "",
    ]
    for n in sorted(statuses):
        date, title, vol = rulings[n]
        status = statuses[n]
        date_part = f" ({date})" if date else ""
        lines.append(f"- **R{n}**{date_part} — {title} — `{status}`")
    lines += ["", END]
    return "\n".join(lines)


def _splice(text: str, block: str) -> str:
    b, e = text.find(BEGIN), text.find(END)
    if b < 0 or e < 0:
        raise SystemExit(
            f"gen_decisions_digest: {LIVE.relative_to(REPO).as_posix()} has "
            "no digest markers; the split commit plants them once")
    return text[:b] + block + text[e + len(END):]


def main() -> int:
    ap = argparse.ArgumentParser(description="current-law digest generator")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()

    block = render()
    text = LIVE.read_text(encoding="utf-8")
    fresh = _splice(text, block)

    if args.write:
        if fresh != text:
            LIVE.write_text(fresh, encoding="utf-8", newline="\n")
            print("digest block rewritten")
        else:
            print("digest block already current")
        return 0

    if fresh != text:
        print("gen_decisions_digest --check: STALE — the digest block in "
              "tier0/DECISIONS.md does not match a fresh render.\n"
              "Run: python tools/gen_decisions_digest.py --write\n"
              "(The block is generated; hand edits are overwritten, "
              "by design.)")
        return 1
    print("gen_decisions_digest --check: OK (digest block is current)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
