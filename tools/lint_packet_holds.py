#!/usr/bin/env python3
"""EB-228: a packet may not HOLD live work on a pick no register carries.

WHY THIS EXISTS. Kokomi slice 2's section 9 ended with a sentence that stopped
real work:

    **Staging the round-2 boards and whole-fight play of the two advanced arms
    are HELD on this pick.**

The pick it named was `PICK 2` -- a heading inside the packet, and nowhere
else. It reached no `QUEUE.md` row, so `STATE.md` reported no prototype-slice
row open, a round-2 run was scheduled on 2026-08-30 off that clean-looking
register, and the run stopped at the door. The packet was RIGHT; the registers
could not see it. Nothing in the repo joins the two, and that join is this
file. The packet left HEAD with the slice, and is read at
`git show a1df7d6:review/active/kokomi-slice-2-2026-08-29.md`.

WHAT IS CHECKED. Every `review/active/*.md`, paragraph by paragraph. A
paragraph that makes a HOLD CLAIM -- work asserted to be waiting on a decision
-- must name an id that a register actually carries. Otherwise the paragraph is
a finding, reported with its file, line and first line.

THE HOLD VOCABULARY, AND WHY IT IS A PHRASE AND NOT A WORD LIST. The obvious
implementation -- grep the packets for `held`, `blocked`, `pending`, `waits` --
was written first and measured: 53 matching lines across the nine live packets,
of which zero were holds on a pick. `every deck holds from turn one`, `the
starter every deck holds`, `SAME_NATION_REWARD_SHARE HOLDS AT 0.5`, `both rows
read pending`, `Superconduct, Overloaded and Frozen`, a run table's `Stopped
by` column. A gate with that false-positive rate is a gate somebody deletes,
so the predicate is the whole PHRASE the hazard is made of:

    <hold verb> <preposition> ... <decision noun>

with at most 60 characters of one sentence between the preposition and the
noun. `HELD on this pick` matches. `holds from turn one` does not -- no
preposition of the right kind and no decision noun. `blocked on EB-188` does
not -- no decision noun, and it is a hold on an ENGINEERING row, which is
registered and visible by construction.

Both halves are drawn from real packet text rather than guessed. The verbs and
their prepositions are every spelling found in `review/active/`,
`review/ruled/` and the historical packet; the decision nouns are the words
those packets use for the thing a hold waits on.

WHAT DISCHARGES A HOLD CLAIM. The paragraph names, as a whole word:

  * an id whose `QUEUE.md` row is OPEN -- the register of [USER]'s A/B/C
    picks, and the one `STATE.md` reads to answer *is a pick open?*; or
  * an id defined by a `BACKLOG.md` row. A hold on an engineering row is
    minted, registered and visible -- `EB-228`'s complaint is a hold that
    reaches NO register, not a hold that reaches the other one. Closed items
    leave HEAD (CLAUDE.md sec.Norms), so presence in the file is the liveness
    test BACKLOG offers; it has no status column.

A `PICK 2` heading, a `P5a` packet section or a bare `this pick` discharges
nothing. That is the entire point of the row.

An `EXPERIMENTS.md` registration id is deliberately NOT a discharge. A
registration names a MEASUREMENT, not the decision the measurement feeds, and
`KOKOMI-SLICE1-WF` -- the one such hold in the tree, at
`review/active/companion-cards-2026-08-30.md` sec.4.3 -- has been RUN AND
GRADED since 2026-08-30 while the sentence holding work on it still stands. It
costs nothing today: that sentence is spelled *is pending `X`*, with no
preposition and no decision noun, so the phrase predicate never reaches it.

THE EXCLUSIONS, each with the text that justified it.

  1. **Fenced code blocks** (``` and ~~~). A pasted command, a seat transcript
     or a sample register row is not this packet's claim about its own work.
  2. **Table rows** (a line opening `|`). `kokomi-overhaul-round-2` has a run
     table with a `Stopped by` column: the cell says why a seat's session
     ended, and every row of it would otherwise read as a hold.
  3. **Block quotes** (a line opening `>`). A quoted register preamble or a
     quoted seat verdict is someone else's words, and a published record is
     struck rather than rewritten (R101b) -- a lint that demanded an id inside
     one would be asking for the record to be edited.
  4. **Headings** (a line opening `#`). A title names a section; the claim, if
     there is one, is in the paragraph under it.
  5. **The `Status:` first line.** `lint_review_status.py` owns that line's
     shape, and it carries the packet's own pointer rather than a hold.

Markdown emphasis and backticks are stripped before matching, so `**HELD** on
this pick` and `blocked on `EB-188`` read the same as their plain forms, and
the whitespace is collapsed so a hold phrase split across a wrapped line still
matches.

    python tools/lint_packet_holds.py
    python tools/lint_packet_holds.py --paths <file.md> [...]   # off-tree file
    python tools/lint_packet_holds.py --self-test

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# EB-93. This tool ECHOES packet prose -- a finding prints the paragraph's
# first line, and these packets carry em dashes and card titles with a music
# note. On a cp1252 console that raises `UnicodeEncodeError` and takes the
# exit code with it, so a red gate would read as a crash.
from understudy.report import console_safe          # noqa: E402

ACTIVE = "review/active"
QUEUE = "docs/current/QUEUE.md"
BACKLOG = "docs/current/BACKLOG.md"


# --- the hold vocabulary ---------------------------------------------------
# Every spelling found in a packet, in a FINITE or PARTICIPLE form only. The
# bare infinitives -- `hold`, `block`, `wait`, `freeze`, `pause` -- are
# deliberately absent: a hold CLAIM is an assertion about state (*is HELD*,
# *are blocked*, *waits on*), never an infinitive, and `Block` and `Hold` are
# game keywords that appear capitalised in every combat sentence these packets
# write. Keeping `block` cost one false positive on the historical packet
# itself: *5 Block against 12 Block ... telegraphing 4 answers*.
HOLD_VERBS = (
    "held", "holds",
    "blocked", "blocks",
    "waits", "waiting",
    "awaits", "awaiting",
    "frozen", "freezes",
    "paused", "pauses",
    "stalled", "stalls",
    "gated", "gates",
    "deferred", "defers",
    "stopped", "stops",
)

# The prepositions that turn one of those verbs into a hold ON something.
# `on hold` is spelled as its own verb form below, because the preposition
# comes first there. `against` is NOT here -- *5 Block against 12 Block* is
# the only sense this repo uses it in.
PREPOSITIONS = ("on", "upon", "behind", "until", "pending", "for")

# What a hold waits FOR when the hold is a pick. `rule` is deliberately absent
# -- this repo says "the Charge rule", "a rule in the brief's rule list" and
# "LAW rule" constantly, and a game rule is not a decision. `ruling` is kept:
# it only ever means a settled [USER] answer.
DECISION_NOUNS = (
    "pick", "picks", "sub-pick", "sub-picks",
    "decision", "decisions",
    "ruling", "rulings",
    "countersign", "countersignature", "countersigning",
    "verdict", "verdicts",
    "sign-off", "signoff", "approval",
    "answer", "answers",
    "choice", "choices",
    "veto", "taste", "judgement", "judgment",
    "slate",
)

_VERBS = "|".join(sorted(HOLD_VERBS, key=len, reverse=True))
_PREPS = "|".join(PREPOSITIONS)
_NOUNS = "|".join(sorted(DECISION_NOUNS, key=len, reverse=True))

# <hold verb> <preposition> ...<=60 chars, one sentence... <decision noun>
#
# The window forbids sentence-ending punctuation, so a hold verb in one
# sentence cannot reach a decision noun in the next one. 60 characters is
# about ten words -- room for "on this pick", "on the P5a countersign", "on
# [USER]'s answer to the second question", and not room to wander.
HOLD_PHRASE = re.compile(
    rf"\b(?:{_VERBS})\b\s+(?:{_PREPS})\b[^.;:!?]{{0,60}}?\b(?:{_NOUNS})\b"
    rf"|\bon hold\b[^.;:!?]{{0,60}}?\b(?:{_NOUNS})\b"
    rf"|\b(?:awaits|awaiting)\b[^.;:!?]{{0,60}}?\b(?:{_NOUNS})\b",
    re.IGNORECASE,
)

# An id as the registers spell it, for the whole-word scan below.
ID_WORD = re.compile(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])")

# A register table row: `| `EB-71` | ... |`. The id is the first cell, and a
# cell may carry several joined by ` / ` (QUEUE's `S4-G12 / CC-G1 / CC-G2`).
ROW = re.compile(r"^\|(?P<cells>.+)\|\s*$")
BACKTICKED = re.compile(r"`([^`]+)`")
ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9.]+)*$")


def _rows(text: str) -> list[list[str]]:
    """Every markdown table BODY row in `text`, as its stripped cells.

    A table's header and its `|---|---|` separator are both dropped, by
    keeping only what follows a separator inside each run of table lines.
    Dropping the header is not cosmetic: `BACKLOG.md`'s header cell is the
    literal word `ID`, which satisfies the id pattern, and a paragraph
    containing the word `ID` would then discharge its own hold.
    """
    out: list[list[str]] = []
    block: list[list[str] | None] = []          # None marks a separator

    def flush() -> None:
        if not block:
            return
        last = max((i for i, r in enumerate(block) if r is None), default=None)
        rows = block if last is None else block[last + 1:]
        out.extend(r for r in rows if r is not None)
        block.clear()

    for line in text.splitlines():
        match = ROW.match(line.strip())
        if not match:
            flush()
            continue
        cells = [c.strip() for c in match.group("cells").split("|")]
        block.append(None if all(set(c) <= set("-: ") for c in cells)
                     else cells)
    flush()
    return out


def _ids_in_cell(cell: str) -> list[str]:
    """The ids a first column defines. `` `A` / `B` `` is two, not one."""
    parts = BACKTICKED.findall(cell) or [cell]
    return [p.strip() for p in parts if ID.match(p.strip())]


def queue_open_ids(text: str) -> set[str]:
    """Ids whose `QUEUE.md` row is OPEN.

    OPEN is read off the row's Status cell, and the test is the cell's FIRST
    word rather than a substring: the live `S4-G6` row reads
    `OPEN -- mechanism ANSWERED (R231), the band still owed`, so a search for
    a closed-marker word anywhere in the cell would close a row that is open.
    The register's own preamble says status is OPEN unless a row says
    otherwise; every row in HEAD says so explicitly, and a row that names no
    status is not counted -- `lint_register_shape.py` rule 5 owns that defect.
    """
    open_ids: set[str] = set()
    for cells in _rows(text):
        ids = _ids_in_cell(cells[0]) if cells else []
        if not ids:
            continue
        status = ""
        for cell in cells[1:]:
            first = cell.split()[0].strip("*_`") if cell.split() else ""
            if first.upper() in ("OPEN", "CLOSED", "RULED", "ANSWERED",
                                 "DONE", "WITHDRAWN", "SUPERSEDED"):
                status = first.upper()
                break
        if status == "OPEN":
            open_ids.update(ids)
    return open_ids


def backlog_ids(text: str) -> set[str]:
    """Every id a `BACKLOG.md` row defines.

    No status filter: the register has no status column, and closed items
    leave HEAD (CLAUDE.md sec.Norms), so a row's presence is what liveness
    this file offers.
    """
    out: set[str] = set()
    for cells in _rows(text):
        if cells:
            out.update(_ids_in_cell(cells[0]))
    return out


# --- paragraph extraction --------------------------------------------------
FENCE = re.compile(r"^\s*(```|~~~)")
EMPHASIS = re.compile(r"[*_`]")


def paragraphs(text: str) -> list[tuple[int, list[str]]]:
    """`(1-based line of the first line, lines)` for every prose paragraph.

    Exclusions 1-5 from the module docstring are applied here: fenced code is
    skipped whole, and a line opening `|`, `>` or `#` is dropped, as is the
    file's `Status:` first line. A paragraph made only of dropped lines
    disappears, which is how a table stops being a paragraph.
    """
    lines = text.splitlines()
    out: list[tuple[int, list[str]]] = []
    current: list[str] = []
    start = 0
    in_fence = False
    for index, raw in enumerate(lines, start=1):
        if FENCE.match(raw):
            in_fence = not in_fence
            raw = ""
        elif in_fence:
            raw = ""
        stripped = raw.strip()
        if index == 1 and stripped.startswith("Status:"):
            stripped = ""
        if stripped.startswith(("|", ">", "#")):
            stripped = ""
        if not stripped:
            if current:
                out.append((start, current))
                current = []
            continue
        if not current:
            start = index
        current.append(stripped)
    if current:
        out.append((start, current))
    return out


def normalised(lines: list[str]) -> str:
    """One line, emphasis and backticks gone, whitespace collapsed.

    Both halves matter. The hold phrase is regularly split across a wrapped
    line (`are\\nHELD on this pick`), and the emphasis markers sit inside it
    (`**HELD** on this pick`); neither is a difference the reader sees.
    """
    return re.sub(r"\s+", " ", EMPHASIS.sub("", " ".join(lines))).strip()


def hold_claims(paragraph: str) -> list[str]:
    """The hold phrases in one normalised paragraph."""
    return [m.group(0) for m in HOLD_PHRASE.finditer(paragraph)]


def names_id(paragraph: str, known: set[str]) -> list[str]:
    """Which of `known` the paragraph names, as whole words."""
    return sorted(i for i in known
                  if re.search(ID_WORD.pattern % re.escape(i), paragraph))


def findings(files: list[tuple[str, str]], known: set[str]) -> list[str]:
    """One finding per hold-claim paragraph that names no known id."""
    out: list[str] = []
    for name, text in files:
        for line_no, lines in paragraphs(text):
            flat = normalised(lines)
            claims = hold_claims(flat)
            if not claims:
                continue
            if names_id(flat, known):
                continue
            first = lines[0]
            out.append(
                f"{name}:{line_no}: holds work on a pick no register carries "
                f"-- {claims[0]!r}\n"
                f"    {first[:100]}\n"
                f"    Mint the pick as an OPEN QUEUE.md row (or name the "
                f"BACKLOG row it waits on) and cite the id in this paragraph.")
    return out


def active_files() -> list[tuple[str, str]]:
    root = REPO / ACTIVE
    return [(f"{ACTIVE}/{p.name}", p.read_text(encoding="utf-8"))
            for p in sorted(root.glob("*.md"))]


def known_ids() -> set[str]:
    queue = (REPO / QUEUE).read_text(encoding="utf-8")
    backlog = (REPO / BACKLOG).read_text(encoding="utf-8")
    return queue_open_ids(queue) | backlog_ids(backlog)


# --- self-test -------------------------------------------------------------
# The historical shape, verbatim from `a1df7d6`, and the near-misses that must
# NOT fire. Each near-miss is a real sentence from `review/active/` on
# 2026-09-02 -- the false positives the word-list version produced.
CAUGHT = (
    "**Staging the round-2 boards and whole-fight play of the two advanced "
    "arms are\nHELD on this pick.** Options 1-4 retire arms 1-4 as authored.",
    "The round-2 staging waits on the pick below.",
    "Everything downstream is on hold until the countersign.",
)

CLEAN = (
    "is worth anything: the starter, which every deck holds from turn one.",
    "**P7 -- the home-nation weight. `SAME_NATION_REWARD_SHARE` HOLDS AT "
    "0.5.** The constant is not defended on principle.",
    "**Nothing is staged.** No seed is pinned and both rows read `pending`.",
    "and pays reactions too, since Superconduct, Overloaded and Frozen on a",
    "repair (sec.2.6) on the other. Neither waits on the other.",
    "It is **blocked on `EB-188`**, not skipped: prototype rows are "
    "quarantined out of every pool.",
    "**Gated on the Burst fold:** the sheet changes, and P3's three rewrites.",
    "**Pair 3 needed twelve rolls.** Its question is 5 Block against 12 "
    "Block for a bank of six, and a body telegraphing 4 answers it.",
)


def self_test() -> list[str]:
    bad: list[str] = []
    known = {"EB-188", "M69"}

    for source in CAUGHT:
        if not findings([("fixture.md", source)], known):
            bad.append(f"self-test: a hold claim was accepted -- {source[:60]!r}")

    for source in CLEAN:
        hit = findings([("fixture.md", source)], known)
        if hit:
            bad.append(f"self-test: a non-hold fired -- {source[:60]!r}: {hit}")

    # The discharge, both ways round.
    held = CAUGHT[0].replace("this pick", "the `M69` pick")
    if findings([("fixture.md", held)], known):
        bad.append("self-test: naming an OPEN QUEUE id did not discharge")
    if not findings([("fixture.md", held)], {"EB-188"}):
        bad.append("self-test: naming a CLOSED id discharged")

    # Exclusions 1-4.
    fenced = "```\n" + CAUGHT[0] + "\n```\n"
    if findings([("fixture.md", fenced)], known):
        bad.append("self-test: exclusion 1 (fenced code) did not hold")
    table = "| Seat | Stopped by |\n|---|---|\n| Opus | held on the pick |\n"
    if findings([("fixture.md", table)], known):
        bad.append("self-test: exclusion 2 (table row) did not hold")
    quote = "> " + CAUGHT[0].replace("\n", "\n> ") + "\n"
    if findings([("fixture.md", quote)], known):
        bad.append("self-test: exclusion 3 (block quote) did not hold")
    heading = "## Work HELD on this pick\n"
    if findings([("fixture.md", heading)], known):
        bad.append("self-test: exclusion 4 (heading) did not hold")

    # The two register readers, on the shapes they actually meet.
    queue = ("| ID | Decision needed | Status | Provenance |\n"
             "|---|---|---|---|\n"
             "| `M69` | **Ask:** rule on X9 | OPEN -- the graded read is in "
             "| R188 |\n"
             "| `S4-G12` / `CC-G1` | **Ask:** approve | OPEN -- ready | x |\n"
             "| `M14` | **Ask:** amend | CLOSED (R231) | x |\n")
    got = queue_open_ids(queue)
    if got != {"M69", "S4-G12", "CC-G1"}:
        bad.append(f"self-test: queue_open_ids read {sorted(got)}")
    table = ("| ID | Item | Provenance |\n|---|---|---|\n"
             "| `EB-228` | **Scope:** x | 2026-08-30 |\n")
    got = backlog_ids(table)
    if got != {"EB-228"}:
        bad.append(f"self-test: backlog_ids read {sorted(got)} -- the header "
                   f"cell `ID` is an id-shaped word and must be dropped")

    return bad


def main(argv: list[str]) -> int:
    console_safe()
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        cases = len(CAUGHT) + len(CLEAN) + 8
        print(f"self-test: {cases} case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    known = known_ids()
    if "--paths" in argv:
        paths = [Path(a) for a in argv[argv.index("--paths") + 1:]]
        files = [(p.as_posix(), p.read_text(encoding="utf-8")) for p in paths]
    else:
        files = active_files()

    if not files:
        print(f"VACUOUS: no packets were read. {ACTIVE}/ is empty or moved; "
              f"this lint is reporting nothing, not health.")
        return 1
    if not known:
        print(f"VACUOUS: no ids were read out of {QUEUE} or {BACKLOG}. The "
              f"row shape moved; every hold claim would fail for the wrong "
              f"reason.")
        return 1

    bad = findings(files, known)
    for line in bad:
        print(line)

    # Disclosed on every run, green or red. A tree whose packets hold nothing
    # is legitimately clean, and a predicate that has stopped matching looks
    # exactly the same from outside -- so the count is printed rather than
    # inferred, the way the patch-scope lint prints its exemptions.
    total = claims = 0
    for _, text in files:
        for _, lines in paragraphs(text):
            total += 1
            claims += len(hold_claims(normalised(lines)))
    print(f"scope: {len(files)} packet(s), {total} paragraph(s), "
          f"{claims} hold claim(s); {len(known)} registered id(s) can "
          f"discharge one")
    if bad:
        print(f"\n{len(bad)} finding(s). EB-228: a hold that reaches no "
              f"register is a run scheduled against a clean-looking STATE.md.")
        return 1
    if not claims:
        print("packet-holds OK: no packet holds work on anything today")
        return 0
    print("packet-holds OK: every held paragraph names a register row")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
