"""Citation-graph extractor for the shared inventory pass (P-A / R-A, wave 8).

Producer of `review/stage-clear/citation-graph.tsv`. Mechanical only: no
judgment, no doc edits. See `citation-graph-notes.md` for extraction rules and
known blind spots.

Scope (citing side): docs/, review/, tools/, tier0/tests/, tier05/tests/,
understudy/, tier0/DECISIONS.md, klee-mod/DECISIONS.md.
Scope (cited side): any path-shaped or filename-shaped reference into docs/ or
review/.

Run from repo root:  python review/stage-clear/extract_citations.py
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "review" / "stage-clear" / "citation-graph.tsv"

CITING_DIRS = ["docs", "review", "tools", "tier0/tests", "tier05/tests", "understudy"]
# The ledger is volumized (R-D, 2026-08-06): the archive volume is an
# append-only frozen record exactly like the live file, so it cites as LEDGER.
CITING_FILES = ["tier0/DECISIONS.md", "tier0/DECISIONS-archive-R39-R99.md",
                "klee-mod/DECISIONS.md"]
CITING_EXT = {".md", ".py", ".yaml", ".yml", ".txt", ".tsv", ".json", ".toml", ".cfg", ".ini"}

# Rule 1: explicit path-shaped references into docs/ or review/.
PATH_RE = re.compile(r"(?<![A-Za-z0-9_/.-])(?:docs|review)/[A-Za-z0-9_./\-]+\.(?:md|yaml|yml|tsv|json|txt|png|html)")
# Rule 2: wiki-style links.
WIKI_RE = re.compile(r"\[\[([^\]|#]+)")
# Rule 3: bare-filename mentions of a doc/review markdown or yaml file, e.g.
# `backlog-2026-07-29.md` cited without its directory.
BARE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.\-]*\.(?:md|yaml|yml|tsv|json|txt)")

TRAILING_JUNK = ".,;:)]}\"'`"


def norm(p: str) -> str:
    return p.strip().lstrip("(<`\"'").rstrip(TRAILING_JUNK)


def build_basename_index() -> tuple[dict[str, str], set[str]]:
    """basename -> unique repo-relative path for files under docs/ and review/.

    Ambiguous basenames (>1 owner) are excluded and returned separately so the
    notes file can record the blind spot.
    """
    seen: dict[str, list[str]] = collections.defaultdict(list)
    for root in ("docs", "review"):
        base = REPO / root
        if not base.is_dir():
            continue
        for f in base.rglob("*"):
            if f.is_file():
                seen[f.name].append(f.relative_to(REPO).as_posix())
    unique = {name: paths[0] for name, paths in seen.items() if len(paths) == 1}
    ambiguous = {name for name, paths in seen.items() if len(paths) > 1}
    return unique, ambiguous


def citing_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for d in CITING_DIRS:
        base = REPO / d
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*")):
            if f.is_file() and f.suffix.lower() in CITING_EXT:
                # do not let this pass's own outputs cite themselves into the graph
                if "stage-clear" in f.parts:
                    continue
                out.append(f)
    for f in CITING_FILES:
        p = REPO / f
        if p.is_file():
            out.append(p)
    return out


STATUS_RE = re.compile(r"Lifecycle:\s*\*{0,2}(LIVING|REFERENCE|ARCHIVED)")


def doc_status(rel: str) -> str:
    """Lifecycle status of a repo-relative path, best effort.

    Reads the file's own header banner where present; falls back to location
    (docs/archive/ => ARCHIVED) and to CODE for the code-side citers.
    """
    if rel in ("tier0/DECISIONS.md", "tier0/DECISIONS-archive-R39-R99.md",
               "klee-mod/DECISIONS.md"):
        return "LEDGER"
    if rel.startswith(("tools/", "tier0/", "tier05/", "understudy/")):
        return "CODE"
    p = REPO / rel
    if rel.startswith("docs/archive/"):
        return "ARCHIVED"
    if rel.startswith("review/"):
        return "REVIEW"
    if p.suffix.lower() in (".md", ".yaml", ".yml") and p.is_file():
        head = p.read_text(encoding="utf-8", errors="replace")[:2000]
        m = STATUS_RE.search(head)
        if m:
            return m.group(1)
        m2 = re.search(r"^#\s*(?:Lifecycle|Status):\s*(LIVING|REFERENCE|ARCHIVED)", head, re.M | re.I)
        if m2:
            return m2.group(1).upper()
    return "UNBANNERED"


def main() -> int:
    basename_to_path, ambiguous = build_basename_index()
    edges: set[tuple[str, str, str]] = set()  # (citer, cited, rule)
    for f in citing_files():
        rel = f.relative_to(REPO).as_posix()
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits: dict[str, str] = {}
        for m in PATH_RE.finditer(text):
            hits[norm(m.group(0))] = "path"
        for m in WIKI_RE.finditer(text):
            name = norm(m.group(1))
            if name in basename_to_path:
                hits.setdefault(basename_to_path[name], "wiki")
        path_basenames = {p.rsplit("/", 1)[-1] for p in hits}
        for m in BARE_RE.finditer(text):
            name = norm(m.group(0))
            if name in path_basenames:
                continue  # already captured with its directory
            if name in basename_to_path:
                target = basename_to_path[name]
                if target != rel:
                    hits.setdefault(target, "bare")
        for cited, rule in hits.items():
            if cited == rel:
                continue
            edges.add((rel, cited, rule))

    # ---- write graph ----
    status_cache: dict[str, str] = {}

    def st(rel: str) -> str:
        if rel not in status_cache:
            status_cache[rel] = doc_status(rel)
        return status_cache[rel]

    lines = ["citer\tciter_status\tcited\trule\tcited_exists"]
    for citer, cited, rule in sorted(edges):
        exists = "yes" if (REPO / cited).exists() else "NO"
        lines.append(f"{citer}\t{st(citer)}\t{cited}\t{rule}\t{exists}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- write per-file in-degree for every file in docs/ and review/ ----
    by_target: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for citer, cited, _ in edges:
        by_target[cited][st(citer)] += 1
    deg_lines = ["file\tstatus\tin_degree_total\tcode\tledger\tliving\treference\tarchived\treview\tother"]
    all_targets: set[str] = set(by_target)
    for root in ("docs", "review"):
        for f in (REPO / root).rglob("*"):
            if f.is_file() and "stage-clear" not in f.parts:
                all_targets.add(f.relative_to(REPO).as_posix())
    for t in sorted(all_targets):
        c = by_target.get(t, collections.Counter())
        other = sum(c.values()) - sum(
            c.get(k, 0) for k in ("CODE", "LEDGER", "LIVING", "REFERENCE", "ARCHIVED", "REVIEW")
        )
        deg_lines.append(
            f"{t}\t{st(t) if (REPO / t).exists() else 'MISSING'}\t{sum(c.values())}"
            f"\t{c.get('CODE', 0)}\t{c.get('LEDGER', 0)}\t{c.get('LIVING', 0)}\t{c.get('REFERENCE', 0)}"
            f"\t{c.get('ARCHIVED', 0)}\t{c.get('REVIEW', 0)}\t{other}"
        )
    (REPO / "review" / "stage-clear" / "citation-indegree.tsv").write_text(
        "\n".join(deg_lines) + "\n", encoding="utf-8"
    )

    # ---- console summary ----
    indeg = collections.Counter(cited for _, cited, _ in edges)
    dead = sorted({cited for _, cited, _ in edges if not (REPO / cited).exists()})
    print(f"edges: {len(edges)}")
    print(f"citing files scanned: {len(citing_files())}")
    print(f"distinct cited targets: {len(indeg)}")
    print(f"ambiguous basenames excluded from bare-name matching: {len(ambiguous)}")
    print(f"dead citations (cited path does not exist): {len(dead)}")
    for d in dead:
        who = sorted(c for c, t, _ in edges if t == d)[:4]
        print(f"  DEAD {d}  <- {', '.join(who)}")
    # reconcile with tier0/tests/test_doc_citation_targets.py's view
    doc_path_re = re.compile(r"docs/[A-Za-z0-9_./-]+\.(?:md|yaml|tsv|json|txt)")
    pinned: set[str] = set()
    for p in sorted((REPO / "tools").rglob("*.py")):
        for m in doc_path_re.finditer(p.read_text(encoding="utf-8", errors="replace")):
            pinned.add(m.group(0))
    mine = {t for c, t, r in edges if c.startswith("tools/") and c.endswith(".py") and t.startswith("docs/") and r == "path"}
    # strip trailing-junk normalization differences by comparing normalized sets
    missing = {p for p in pinned if norm(p) not in {norm(t) for t in mine}}
    print(f"pin-test targets (tools/ -> docs/): {len(pinned)}; in graph: {len(pinned) - len(missing)}; missing: {sorted(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
