#!/usr/bin/env python3
"""Resolve every R-number to one line, so a citation stops costing a grep.

WHY THIS EXISTS. 114-odd distinct R-ids are cited ~600 times across
`docs/current/`, and **not one of them is defined in HEAD**. The ledgers that
defined them were deleted on 2026-08-06 (`762e94d`, "retire the
ledger/citation regime"); the rulings issued since live only in commit
messages. So the only way to answer "what did R184 say?" was to read 210 KB of
registers and then `git log`. That is a per-reader cost paid over and over,
and it is exactly the cost an index removes: this file is generated ONCE per
change and read ON DEMAND.

WHAT A ROW CLAIMS, AND WHAT IT DOES NOT. A row is a POINTER, not the ruling.
The one-sentence cell is a handle for recognising the right ruling; the hash
is the RETRIEVAL POINT where the ruling's own words live. Nothing here
supersedes, amends, or restates law -- `docs/current/LAW.md` is still the only
place law is stated, and a row that disagrees with LAW is a stale row, not a
new rule.

WHERE A DEFINITION COMES FROM, in the order tried:

  1. **The generated current-law digest** inside the retired
     `tier0/DECISIONS.md` -- one dated line per ruling for R39..R121. This is
     the best source in existence and it covers two thirds of the namespace.
  2. **A `## R<n>` ledger heading** (`tier0/DECISIONS-archive-R39-R99.md`,
     `tier0/DECISIONS.md`, `klee-mod/DECISIONS.md`).
  3. **A bold ledger definition** -- `**R16 - card-mediated boosting**`,
     `**R34 executed (...):**`. The pre-R39 range was never headed (the ledger
     says so itself: "R1-R38 were never headed entries and remain not
     mechanically resolvable"), so this arm is best-effort by construction.
  4. **The earliest commit that RECORDS the id** -- subject first, then a body
     paragraph headed by the id, then a body line naming it next to
     RULED / ruling / countersign / [USER]. This is the only source for R122+.

Anything still unresolved gets a row saying so, pointing at the tag. An id
that is neither cited under `docs/current/` nor resolvable is omitted, and
counted in the footer -- the index tracks the namespace in use, not the
namespace in principle.

THE BARE-LETTER CAVEAT. `R7` in `LAW.md` is a KleeSelfCheck lint rule; `R1`
in `BACKLOG.md` is a red-pen reply number; `R2.1` in the atlas is a drafter
term. Three namespaces spell their ids the same way (`atlas/klee-mod-runtime.md`
documents the collision). This tool resolves the RULING namespace and marks
the rest unresolved rather than guessing -- a wrong definition is worse than
an honest "look at the tag".

SHALLOW CLONES. CI checks out depth-1 with no tags, so neither the ledgers nor
the commit bodies exist there. Every git read degrades to "no history" instead
of raising, the rows become unresolved rows, and the output is still a valid
file. `tools/lint_rulings_index.py` knows to skip its staleness half in that
case -- see its docstring.

Usage:
    python -m tools.gen_rulings_index            # write docs/current/RULINGS.md
    python -m tools.gen_rulings_index --stdout   # print it, write nothing
    python -m tools.gen_rulings_index --out P    # write elsewhere (the lint)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.lint_r_numbers import R_CEILING           # noqa: E402
from understudy.report import console_safe           # noqa: E402

DOCS = REPO / "docs/current"
OUT = DOCS / "RULINGS.md"

# CLAUDE.md's history-retrieval recipe names this tag, and the three ledger
# blobs at the tag are byte-identical to the ones `762e94d` deleted -- so the
# tag is the retrieval point a reader can actually fetch on a shallow clone,
# and the deleting commit's parent is only the fallback.
TAG = "pre-simplification-2026-08-06"
LEDGER_REVS = (TAG, "762e94d^")
LEDGER_PATHS = (
    "tier0/DECISIONS.md",                 # digest (R39-R121) + pre-R39 prose
    "tier0/DECISIONS-archive-R39-R99.md",
    "klee-mod/DECISIONS.md",
)
UNRESOLVED = f"unresolved: pre-ledger, see tag {TAG}"

# Fixed, not `--short`: `core.abbrev=auto` picks a length from the object
# count, so an abbreviation that varies by clone would make this file's
# staleness check fire on a fresh checkout that changed nothing.
ABBREV = 7
MAXLEN = 160
DASH = "—"          # em dash, as the registers spell it
NONE = "—"          # the empty cell


# --- git, degrading rather than raising -------------------------------------

def run(*args: str) -> tuple[int, str]:
    """`git <args>` -> (exit code, stdout). 127 when git itself is absent."""
    try:
        proc = subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="replace")
    except OSError:
        return 127, ""
    return proc.returncode, proc.stdout


# --- what the docs actually cite --------------------------------------------

R_TOKEN = re.compile(r"\bR(\d+)\b")


def pages() -> list[Path]:
    """Every page `lint_r_numbers` scans, minus the file we generate."""
    if not DOCS.is_dir():
        return []
    return sorted(p for p in DOCS.rglob("*.md") if p != OUT)


def cited_ids() -> set[int]:
    out: set[int] = set()
    for page in pages():
        text = page.read_text(encoding="utf-8")
        out.update(int(m) for m in R_TOKEN.findall(text))
    return {n for n in out if 1 <= n <= R_CEILING}


# --- entries -----------------------------------------------------------------

# Rank order IS the source preference; lower wins.
RANKS = {"digest": 0, "heading": 1, "bold": 2, "commit": 3}


@dataclass(frozen=True)
class Entry:
    date: str
    text: str
    rev: str
    kind: str

    @property
    def rank(self) -> int:
        return RANKS[self.kind]


def better(a: Entry | None, b: Entry) -> Entry:
    return b if a is None or b.rank < a.rank else a


# --- text hygiene ------------------------------------------------------------

LIST_LEAD = re.compile(r"^\s*(?:\d+\.|[-*+]|>)\s+")
LEAD_IDS = re.compile(r"^(?:R\d+\s*[/+&,–—-]\s*)*R\d+\s*"
                      r"(?:[:.–—+/-]\s*)?")
SENT_END = re.compile(r"(?<=[.;?!])\s")


def flatten(text: str) -> str:
    """A wrapped markdown blob -> one line, emphasis dropped."""
    return " ".join(text.split()).replace("**", "").replace("~~", "").strip()


def cell(text: str) -> str:
    """Last step only: a literal pipe would end the table column early."""
    return text.replace("|", r"\|")


def clip(text: str, limit: int = MAXLEN) -> str:
    """<= `limit` chars, cut at a sentence end when one is close enough."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cuts = [m.start() for m in SENT_END.finditer(text) if m.start() < limit]
    if cuts and cuts[-1] >= 40:
        return text[:cuts[-1]].strip()
    head = text[:limit - 1].rsplit(" ", 1)[0]
    return (head or text[:limit - 1]).rstrip(" ,;:") + "…"


def summarise(text: str) -> str:
    """Drop the list marker and the id run the entry opens with, then clip."""
    body = LEAD_IDS.sub("", LIST_LEAD.sub("", flatten(text)))
    return cell(clip(flatten(body)))


# --- the ledgers -------------------------------------------------------------

DIGEST = re.compile(
    r"^-\s+\*\*R(\d+)\*\*\s*(?:\((\d{4}-\d{2}-\d{2})\))?\s*"
    r"(?:—|--)\s*(.+)$")
STATUS_TAIL = re.compile(r"\s*(?:—|--)\s*`[A-Z][A-Z0-9:_-]*`\s*$")

HEADING = re.compile(r"^##\s+R(\d+)\s*(?:—|--|:)\s*(.+?)\s*$")
DATE_TAIL = re.compile(r"\s*\((\d{4}-\d{2}-\d{2})[^)]*\)\s*$")

BOLD = re.compile(r"^(?:\s*(?:\d+\.|[-*+])\s+)?\*\*R(\d+)\b(?P<rest>.*)$")
JOIN = re.compile(r"^\s*([/+&,]|–|—|--|-)\s*R?(\d+)")
BREAK = re.compile(r"^(?:#{1,6}\s|\s*(?:\d+\.|[-*+])\s+\*\*R\d+\b|\s*$)")


def leading_ids(first: int, rest: str) -> list[int]:
    """`R9` + `'/R12-R15:**'` -> [9, 12, 13, 14, 15]."""
    ids = [first]
    while True:
        m = JOIN.match(rest)
        if not m:
            return ids
        joiner, num = m.group(1), int(m.group(2))
        if joiner in ("–", "—", "--", "-"):
            lo = ids[-1]
            if lo < num <= lo + 40:
                ids.extend(range(lo + 1, num + 1))
            else:
                return ids
        else:
            ids.append(num)
        rest = rest[m.end():]


def paragraph(lines: list[str], start: int) -> str:
    """The definition's own paragraph: its line plus the wrapped remainder."""
    out = [lines[start]]
    for line in lines[start + 1:]:
        if BREAK.match(line):
            break
        out.append(line)
    return " ".join(out)


ANY_HEADING = re.compile(r"^#{1,6}\s")
ANY_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def parse_ledger(text: str, rev: str, into: dict[int, Entry]) -> None:
    lines = text.splitlines()
    # The pre-R39 range was never headed, so a bold definition carries no date
    # of its own -- it inherits the dated SECTION heading it sits under
    # ("## Furina pass-1 rulings executed (2026-07-20, ...)"), which is the
    # date the ledger itself would have given it.
    section_date = ""
    for i, line in enumerate(lines):
        if ANY_HEADING.match(line):
            d = ANY_DATE.search(line)
            if d:
                section_date = d.group(1)

        m = DIGEST.match(line)
        if m:
            body = STATUS_TAIL.sub("", m.group(3))
            entry = Entry(m.group(2) or "", summarise(body), rev, "digest")
            n = int(m.group(1))
            into[n] = better(into.get(n), entry)
            continue

        m = HEADING.match(line)
        if m:
            title = m.group(2)
            date = ""
            d = DATE_TAIL.search(title)
            if d:
                date, title = d.group(1), title[:d.start()]
            n = int(m.group(1))
            into[n] = better(into.get(n),
                             Entry(date, summarise(title), rev, "heading"))
            continue

        m = BOLD.match(line)
        if m:
            ids = leading_ids(int(m.group(1)), m.group("rest"))
            block = paragraph(lines, i)
            own = ANY_DATE.search(block)
            entry = Entry(own.group(1) if own else section_date,
                          summarise(block), rev, "bold")
            for n in ids:
                into[n] = better(into.get(n), entry)


def ledger_entries() -> tuple[dict[int, Entry], str | None]:
    """Read the retired ledgers once, from the first rev that has them."""
    for rev in LEDGER_REVS:
        code, short = run("rev-parse", f"--short={ABBREV}", f"{rev}^{{commit}}")
        if code != 0 or not short.strip():
            continue
        rev_short = short.strip()
        found: dict[int, Entry] = {}
        seen = False
        for path in LEDGER_PATHS:
            code, text = run("show", f"{rev}:{path}")
            if code != 0 or not text:
                continue
            seen = True
            parse_ledger(text, rev_short, found)
        if seen:
            return found, rev_short
    return {}, None


# --- the commits -------------------------------------------------------------

REC, FLD = "\x1e", "\x1f"
LOG_FORMAT = f"%x1e%H{FLD}%at{FLD}%ad{FLD}%s{FLD}%b"

RULING_WORD = re.compile(r"RULED|rulings?|ruled|countersigne?d?|\[USER\]",
                         re.IGNORECASE)
PARA_HEAD = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+|\*\*)?R(\d+)\b")
RANGE = re.compile(r"\bR(\d+)\s*[–—-]\s*R(\d+)\b")
SUBJ_LEAD = re.compile(r"^\s*\**R(\d+)\b")

# Selection tiers, best first. LEAD is the house convention for a ruling
# commit ("R208 and CONSTANTS_VERSION 17: ...", "R23: aura application pass"),
# so it outranks a subject that merely MENTIONS the number; a range
# (`R138-R174`) outranks nothing but the body, because it records the id
# without describing it.
LEAD, SUBJECT, SUBJRANGE, PARA, NEARBY = 0, 1, 2, 3, 4


@dataclass(frozen=True)
class Commit:
    full: str
    at: int
    date: str
    subject: str
    body: str

    @property
    def short(self) -> str:
        return self.full[:ABBREV]


def commits() -> list[Commit]:
    """`HEAD` plus every TAG. Deliberately not `--all`, and not HEAD alone.

    `--all` reads every ref the CLONE happens to hold -- other agents'
    worktree branches, stale remotes, a colleague's WIP -- so two checkouts of
    the same commit would generate two different files and the staleness gate
    would fire on a difference nobody made.

    HEAD alone is too little: the six earliest ruling commits (`R8`, the
    conjunctive healing law LAW.md still cites, among them) are reachable only
    from the `wip-safety-net` tag, because that history was never merged
    forward. Tags are the repo's own retrieval mechanism (CLAUDE.md's
    history-retrieval section) and a full clone fetches all of them, so
    `HEAD --tags` is both stable across clones and complete.
    """
    code, out = run("log", "HEAD", "--tags", "--date=short",
                    f"--format={LOG_FORMAT}")
    if code != 0:
        return []
    found: list[Commit] = []
    for rec in out.split(REC):
        if not rec.strip():
            continue
        parts = rec.split(FLD)
        if len(parts) < 5:
            continue
        full, at, date, subject, body = parts[0], parts[1], parts[2], parts[3], parts[4]
        try:
            stamp = int(at)
        except ValueError:
            continue
        found.append(Commit(full.strip(), stamp, date.strip(), subject, body))
    return found


def subject_ids(subject: str) -> dict[int, int]:
    """id -> tier, for what a subject records: leading, named, or in a range."""
    tiers: dict[int, int] = {}
    for lo, hi in ((int(a), int(b)) for a, b in RANGE.findall(subject)):
        if lo < hi <= lo + 60:
            for n in range(lo, hi + 1):
                tiers[n] = SUBJRANGE
    for m in R_TOKEN.findall(subject):
        tiers[int(m)] = SUBJECT
    lead = SUBJ_LEAD.match(subject)
    if lead:
        tiers[int(lead.group(1))] = LEAD
    return tiers


def body_paragraphs(body: str) -> dict[int, str]:
    """id -> the body paragraph HEADED by it (the sitting-commit shape)."""
    out: dict[int, str] = {}
    for block in re.split(r"\n\s*\n", body):
        block = block.strip("\n")
        if not block.strip():
            continue
        m = PARA_HEAD.match(block)
        if m:
            out.setdefault(int(m.group(1)), block)
    return out


def nearby_ids(body: str) -> set[int]:
    """Ids sitting on a line that also says RULED / ruling / countersign."""
    out: set[int] = set()
    for line in body.splitlines():
        if RULING_WORD.search(line):
            out.update(int(m) for m in R_TOKEN.findall(line))
    return out


def commit_entries(log: list[Commit]) -> dict[int, Entry]:
    """Earliest recording commit per id -- subjects preferred, then bodies."""
    best: dict[int, tuple[int, int, str, Commit, str]] = {}
    for c in log:
        paras = body_paragraphs(c.body)
        tiers: dict[int, int] = {n: NEARBY for n in nearby_ids(c.body)}
        tiers.update({n: PARA for n in paras})
        tiers.update(subject_ids(c.subject))
        for n, tier in tiers.items():
            if not 1 <= n <= R_CEILING:
                continue
            key = (tier, c.at, c.full)
            if n not in best or key < best[n][:3]:
                best[n] = (tier, c.at, c.full, c, paras.get(n, ""))

    out: dict[int, Entry] = {}
    for n, (_tier, _at, _full, c, para) in best.items():
        # A body paragraph HEADED by the id is the sitting-commit shape --
        # "R138 S4-G5/B-G1. No special Fanfare axis exists ..." -- and says
        # more about that one ruling than a subject covering thirty-seven.
        if para:
            text = para
        elif n in subject_ids(c.subject):
            text = c.subject
        else:
            text = next((s for s in re.split(r"(?<=[.;?!])\s", c.body)
                         if re.search(rf"\bR{n}\b", s)), c.subject)
        out[n] = Entry(c.date, summarise(text), c.short, "commit")
    return out


# --- rendering ---------------------------------------------------------------

HEADER = """# Rulings index

**On-demand.** CLAUDE.md's read order does not load this file; open it when a
ruling is cited by number and you need to know which ruling it is.
**Generated -- do not hand-edit.** Regenerate with
`python -m tools.gen_rulings_index`; `tools/lint_rulings_index.py` gates it.
A row is a POINTER, never the ruling: the last column is the RETRIEVAL POINT
(`git show <hash>`, or `git show <hash>:<ledger path>`) where the words live.
"""


def compress(numbers: list[int]) -> str:
    """[1, 2, 3, 9] -> 'R1-R3, R9'."""
    if not numbers:
        return "none"
    runs: list[tuple[int, int]] = []
    for n in sorted(numbers):
        if runs and n == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], n)
        else:
            runs.append((n, n))
    return ", ".join(f"R{a}" if a == b else f"R{a}-R{b}" for a, b in runs)


def render() -> tuple[str, dict[str, object]]:
    """The whole file, plus the stats the footer and the lint report."""
    ledger, ledger_rev = ledger_entries()
    log = commits()
    from_commits = commit_entries(log)

    resolved: dict[int, Entry] = {}
    for n in range(1, R_CEILING + 1):
        entry = ledger.get(n) or from_commits.get(n)
        if entry and entry.text:
            resolved[n] = entry

    cited = cited_ids()
    rows = sorted(cited | set(resolved))
    omitted = [n for n in range(1, R_CEILING + 1)
               if n not in cited and n not in resolved]

    counts = {"digest": 0, "heading": 0, "bold": 0, "commit": 0,
              "unresolved": 0}
    lines = [HEADER,
             "| ruling | date | what it settled | retrieval point |",
             "| --- | --- | --- | --- |"]
    for n in rows:
        entry = resolved.get(n)
        if entry is None:
            counts["unresolved"] += 1
            lines.append(f"| R{n} | {NONE} | {UNRESOLVED} | {NONE} |")
            continue
        counts[entry.kind] += 1
        date = entry.date or NONE
        lines.append(f"| R{n} | {date} | {entry.text} | `{entry.rev}` |")

    ledger_total = counts["digest"] + counts["heading"] + counts["bold"]
    lines += [
        "",
        f"{len(rows)} rows over the R1..R{R_CEILING} namespace "
        f"{DASH} {ledger_total} resolved from the retired ledgers "
        f"({counts['digest']} from the current-law digest, "
        f"{counts['heading']} from a ledger heading, "
        f"{counts['bold']} from a bold ledger definition), "
        f"{counts['commit']} from a commit message, "
        f"{counts['unresolved']} unresolved.",
        "",
        f"{len(omitted)} id(s) omitted {DASH} neither cited under "
        f"`docs/current/` nor resolvable from history: {compress(omitted)}.",
        "",
        (f"Ledger retrieval point: `{ledger_rev}` (tag `{TAG}`); ledger paths "
         "`tier0/DECISIONS.md`, `tier0/DECISIONS-archive-R39-R99.md`, "
         "`klee-mod/DECISIONS.md`."
         if ledger_rev else
         "Ledger retrieval point: UNAVAILABLE in the clone that generated "
         f"this file. `git fetch --depth=1 origin tag {TAG}`, then "
         "regenerate."),
        "",
        "An unresolved row is not always a missing ruling. Three namespaces "
        f"spell ids `R<n>` {DASH} rulings, `KleeSelfCheck` lint rules, and "
        "red-pen reply numbers (`atlas/klee-mod-runtime.md` documents the "
        "collision) — a cited `R7` may never have been a ruling at all.",
        "",
    ]
    text = "\n".join(lines)
    stats = {
        "rows": len(rows),
        "cited": len(cited),
        "ledger": ledger_total,
        "commit": counts["commit"],
        "unresolved": counts["unresolved"],
        "omitted": len(omitted),
        # The ledgers, not the commit count, decide whether this clone can
        # answer the question: a depth-1 CI checkout still has ONE commit, so
        # "any commits at all" would read as history and let the staleness
        # gate fire on an all-unresolved regeneration.
        "history": ledger_rev is not None,
        "ledger_rev": ledger_rev,
        "commits": len(log),
    }
    return text, stats


def main(argv: list[str]) -> int:
    console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT,
                    help="destination (default: docs/current/RULINGS.md)")
    ap.add_argument("--stdout", action="store_true",
                    help="print the file instead of writing it")
    args = ap.parse_args(argv)

    text, stats = render()
    if args.stdout:
        print(text, end="")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" explicitly: the lint compares BYTES, so a CRLF write on
    # Windows would fail the gate on every Linux run and back again.
    args.out.write_text(text, encoding="utf-8", newline="\n")
    where = args.out
    if where.is_relative_to(REPO):
        where = where.relative_to(REPO)
    print(f"rulings-index: wrote {where.as_posix()} "
          f"-- {stats['rows']} rows, {stats['ledger']} from the ledgers, "
          f"{stats['commit']} from commits, {stats['unresolved']} unresolved, "
          f"{stats['omitted']} omitted"
          + ("" if stats["history"] else "  [NO HISTORY IN THIS CLONE]"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
