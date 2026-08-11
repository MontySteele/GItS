"""Two record-retention invariants, machine-checked (R177/R178, 2026-08-11).

Born from the 2026-08-11 process audit: every earlier safeguard policed files
and rows, none policed lifecycle, so closed material stayed in HEAD by simply
never being asked to leave. These checks make the exit rule fail loudly:

1. **Packet lifecycle.** Every file under `review/active/` opens with a
   metadata block carrying `lifecycle:`, `owner:` and `exit_when:`.
   `lifecycle` must read `active`, and every id named in `owner:` must
   resolve to a row currently open in QUEUE.md or BACKLOG.md. The moment a
   packet's owning row closes, this lint goes red until the packet leaves
   HEAD in that same commit — the enforcement half of "exit is part of
   close" (R178). Metadata is checked, not prose: an active packet may
   legitimately *mention* historical evidence (words like HISTORICAL or
   GRADED are not findings).

2. **Dead current-paths.** A `docs/current/...` or `review/active/...` path
   cited anywhere in the doc tree claims to be in HEAD and must exist there.
   Lines that retrieve history explicitly (`git show`, the
   pre-simplification tag) are exempt — that syntax is the declared way to
   cite a path that left HEAD. Historical namespaces (`docs/archive/…`,
   `dockets/…`, ledger identifiers) and the local-only working dirs under
   `review/<other>/` (run checkpoints, captures) are out of scope by
   construction: they never claimed HEAD-ness.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

ACTIVE_DIR = "review/active"
REGISTERS = ("docs/current/QUEUE.md", "docs/current/BACKLOG.md")
META_KEYS = ("lifecycle", "owner", "exit_when")
META_WINDOW = 10          # the block must sit in the first N lines
HISTORY_MARKS = ("git show", "pre-simplification-2026-08-06")
PATH_RE = re.compile(r"(?:docs/current|review/active)/[A-Za-z0-9_.\-/]+")


def pages(root: Path | None = None):
    root = root or REPO
    for sub in ("docs", "review"):
        base = root / sub
        if base.is_dir():
            yield from sorted(base.rglob("*.md"))
    for name in ("CLAUDE.md", "AGENTS.md"):
        p = root / name
        if p.is_file():
            yield p


def open_row_cells(root: Path | None = None) -> list[str]:
    """First table cell of every register row, backticks stripped."""
    root = root or REPO
    cells: list[str] = []
    for rel in REGISTERS:
        f = root / rel
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("| ") and not set(line) <= {"|", "-", " "}:
                first = line.split("|")[1].strip().replace("`", "")
                if first and first.lower() != "id":
                    cells.append(first)
    return cells


def _meta(text: str) -> dict[str, str]:
    got: dict[str, str] = {}
    for line in text.splitlines()[:META_WINDOW]:
        m = re.match(r"^([a-z_]+):\s*(.+)$", line.strip())
        if m and m.group(1) in META_KEYS:
            got[m.group(1)] = m.group(2).strip()
    return got


def packet_findings(root: Path | None = None) -> list[str]:
    root = root or REPO
    active = root / ACTIVE_DIR
    if not active.is_dir():
        return []
    cells = open_row_cells(root)
    bad: list[str] = []
    for f in sorted(active.iterdir()):
        if not f.is_file():
            continue
        rel = f.relative_to(root).as_posix()
        meta = _meta(f.read_text(encoding="utf-8", errors="replace"))
        missing = [k for k in META_KEYS if k not in meta]
        if missing:
            bad.append(f"{rel}: no {'/'.join(missing)} in the first "
                       f"{META_WINDOW} lines — every active packet declares "
                       "its lifecycle block (R178)")
            continue
        if meta["lifecycle"] != "active":
            bad.append(f"{rel}: lifecycle reads {meta['lifecycle']!r} — "
                       "a packet that is not active does not live under "
                       f"{ACTIVE_DIR}/ (R178: it leaves HEAD with the commit "
                       "that closed it)")
        for owner in [o.strip() for o in meta["owner"].split(",")]:
            if not any(owner in cell for cell in cells):
                bad.append(f"{rel}: owner {owner!r} matches no open QUEUE/"
                           "BACKLOG row — the owning row closed, so the "
                           "packet exits in the same commit (R178), or the "
                           "owner id is wrong")
    return bad


def path_findings(root: Path | None = None) -> list[str]:
    root = root or REPO
    bad: list[str] = []
    for f in pages(root):
        rel = f.relative_to(root).as_posix()
        for n, line in enumerate(
                f.read_text(encoding="utf-8", errors="replace").splitlines(),
                1):
            if any(mark in line for mark in HISTORY_MARKS):
                continue
            for m in PATH_RE.finditer(line):
                cited = m.group(0).rstrip(".,;:)")
                if not (root / cited).exists():
                    bad.append(f"{rel}:{n}: cites {cited}, which is not in "
                               "HEAD — retrieve-by-commit syntax (git show) "
                               "is the way to cite a path that left")
    return bad


def findings(root: Path | None = None) -> list[str]:
    return packet_findings(root) + path_findings(root)


def main() -> int:
    bad = findings()
    if bad:
        print(f"docs-lifecycle FINDINGS ({len(bad)}):")
        for b in bad:
            print(f"  - {b}")
        return 1
    n_packets = len(list((REPO / ACTIVE_DIR).iterdir()))
    print(f"docs-lifecycle OK: {n_packets} active packets all owned by open "
          "rows; no dead docs/current or review path cited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
