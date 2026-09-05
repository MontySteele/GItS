"""The elemental-reaction census over the blind-seat records.

WHY THIS EXISTS
---------------
The sweep packet (not yet on `main` when this was written -- retrieved with
`git show 95b2882a:review/active/elements-reaction-sweep-2026-09-05.md`,
CLAUDE.md sec. History retrieval) asks for exactly this in its §4 item 2:
"A script over the seat records: which reaction fired, what triggered it (a
kit card, a companion, a Mine, a Plan, a performance), on what turn, and
whether the record names it as a decision. This turns the counts in §2 into
a table." It is paper-stage evidence for the sweep, not a rule change and
not a grade: nothing here binds anything or moves a number.

WHAT IT READS
-------------
Every markdown file directly inside a `review/qa/` directory whose name
starts with `klee-round-`, `kokomi-round-`, `furina-reframe-round-` or
`control-ironclad-` -- the blind-seat records the four Prototype rounds
produced. Non-markdown siblings (`*.stderr.txt`, `*.stdout.txt`, json) and
any file whose name contains "prompt" are skipped on sight.

WHAT A "MENTION" IS
--------------------
One regex match of a reaction's name (or a verb form of it -- "vaporized",
"melted", "swirled", ...) anywhere in a record's prose, INCLUDING inside a
quoted card or keyword-box text. That is deliberate and it is the census's
sharpest limit, restated in the record's closing paragraph: a reaction named
in a rule quote counts exactly the same as one the record says fired. This
is a keyword census, not a reading.

Four collisions are excluded by name because they are common enough to
swamp a reaction that shares nothing but a word with them: the relic
`Frozen Egg`, the relic `Burning Blood`, the card `Burning Pact`, and
Bennett's power `Passion Overload`. Nothing else is hand-filtered --
`Freminet -- Shattering Pressure` and the base-game card `Shatter` both slip
through, on purpose, as an example the record names.

TRIGGER AND READING CLASSIFICATION
-----------------------------------
Both are literal, priority-ordered keyword matches over the sentence the
mention falls in (see `sentence_bounds` for how a "sentence" is cut out of
the markdown prose -- a period/question/exclamation before whitespace, or a
real blank-line paragraph break). The trigger order is fixed in
`TRIGGER_CHECKS`;
the reading order is decision-words first, then found-afterwards words,
else "unmarked" -- a mention with neither signal is common and is reported
as its own count rather than forced into one bucket.

USAGE
-----
    python tools/reaction_census.py            # write the record
    python tools/reaction_census.py --check     # verify it, write nothing
"""
from __future__ import annotations

import argparse
import bisect
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"
OUT = REPO / "review" / "records" / "reaction-census-2026-09-05.md"

DIR_PREFIXES = [
    ("klee-round-", "Klee"),
    ("kokomi-round-", "Kokomi"),
    ("furina-reframe-round-", "Furina"),
    ("control-ironclad-", "Control-Ironclad"),
]

SKIP_NAME = re.compile(r"prompt", re.I)
ROUND_RE = re.compile(r"^([0-9]+[a-z]?)(?:-|$)")
FIGHT_HEADING = re.compile(r"^#{1,6}\s*(.+?)\s*$", re.M)


@dataclass(frozen=True)
class ReactionSpec:
    name: str
    pattern: "re.Pattern[str]"
    exclude_after: tuple[str, ...] = ()
    exclude_before: tuple[str, ...] = ()


# Order fixed here is the order every table in the record prints them in.
REACTIONS: list[ReactionSpec] = [
    ReactionSpec("Vaporize", re.compile(r"\bvaporiz\w*", re.I)),
    ReactionSpec("Melt", re.compile(r"\bmelt\w*", re.I)),
    ReactionSpec("Overload", re.compile(r"\boverload\w*", re.I),
                 exclude_before=("passion ",)),
    ReactionSpec("Superconduct", re.compile(r"\bsuperconduct\w*", re.I)),
    ReactionSpec("Electro-Charged", re.compile(r"\belectro-charged\w*", re.I)),
    # Frozen / Freeze / Shatter are one reaction (LAW.md, one Hydro+Cryo row).
    ReactionSpec("Frozen", re.compile(r"\b(?:frozen|freeze[sd]?|shatters?)",
                                       re.I),
                 exclude_after=(" egg",)),
    ReactionSpec("Swirl", re.compile(r"\bswirl\w*", re.I)),
    ReactionSpec("Crystallize", re.compile(r"\bcrystalliz\w*", re.I)),
    # Dendro is not in the game (the sweep packet §3): case-sensitive and
    # excluding the two relic/card collisions, so a genuine hit would mean
    # the word is being used as the reaction, not as an ordinary verb.
    ReactionSpec("Burning", re.compile(r"\bBurning\b"),
                 exclude_after=(" blood", " pact")),
]

DECISION_RE = re.compile(
    r"\bchose\b|\binstead\b|\brejected\b|\bordered\b|\bwhich hit\b|"
    r"\bpreview\b|\bplanned\b|\bheld\b", re.I)
FOUND_RE = re.compile(
    r"\bfound\b|\barithmetic\b|\bsubtract\w*\b|\bunexplained\b|"
    r"\d+\s+where\s+\d+|\bnever named\b|\bdid(?:n.t| not) show\b|"
    r"\bno line\b", re.I)

MINE_RE = re.compile(r"(?<!of )(?<!is )(?<!not )(?<!was )\bmines?\b", re.I)
BOMB_RE = re.compile(r"\bbombs?\b", re.I)
COMPANION_RE = re.compile(r"\bcompanion\w*\b", re.I)
PLAN_RE = re.compile(r"\bplan\b|\bcarry-out\b|\bcarry out\b", re.I)
PERFORMANCE_RE = re.compile(r"\bperformance\w*\b|\bevoke\w*\b", re.I)
RELIC_RE = re.compile(r"\brelics?\b", re.I)
POTION_RE = re.compile(r"\bpotions?\b", re.I)
KIT_CARD_RE = re.compile(r"\bplay(?:s|ed|ing)?\b|\bcard\b", re.I)

TRIGGER_CHECKS: list[tuple[str, "re.Pattern[str]"]] = [
    ("companion card", COMPANION_RE),
    ("Mine", MINE_RE),
    ("Bomb explosion", BOMB_RE),
    ("Plan / carry-out", PLAN_RE),
    ("performance / Evoke", PERFORMANCE_RE),
    ("relic", RELIC_RE),
    ("potion", POTION_RE),
]

# The companion-acquisition keyword pass (a rough signal, not a reading --
# the closing paragraph says so again where the table prints).
ACQUIRE_RE = re.compile(r"\boffer\w*\b|\breward\w*\b|\bshop\w*\b|\btook\b|"
                         r"\bpassed\b", re.I)

BUILD_RE = re.compile(r"\*\*Build[s]?:?\*\*:?\s*(.+)", re.I)

# A "sentence" boundary is either terminal punctuation before whitespace/end
# (checked on the flattened text), or a markdown paragraph break -- a REAL
# blank line, i.e. two or more newlines in the original text with only
# whitespace between them. That second check must run on the ORIGINAL text,
# not the flattened one: this repo's prose wraps a list item across several
# lines with a hanging indent (a single newline, then 2-4 leading spaces),
# and once flattened that indentation reads as "2+ whitespace" exactly like
# a paragraph break would. Requiring two literal newlines is what tells a
# genuine blank line apart from an indented word-wrap -- get it wrong and
# every wrapped line becomes its own "sentence". Headings sit between two
# real blank lines already, so they never bleed into the paragraph beside
# them.
TERMINAL_RE = re.compile(r"[.!?](?=\s|$)")
PARA_BREAK_RE = re.compile(r"\n[ \t]*\n[ \t]*")


def flatten(text: str) -> str:
    """Newlines -> single spaces, 1:1, so offsets stay valid against `text`."""
    return text.replace("\n", " ")


def sentence_bounds(text: str, flat: str) -> list[int]:
    points = {m.end() for m in TERMINAL_RE.finditer(flat)}
    points |= {m.end() for m in PARA_BREAK_RE.finditer(text)}
    return [0] + sorted(points) + [len(flat)]


def sentence_span(flat: str, bounds: list[int], start: int, end: int
                   ) -> tuple[int, int]:
    i = bisect.bisect_right(bounds, start) - 1
    lo = bounds[i] if i >= 0 else 0
    j = bisect.bisect_right(bounds, end)
    hi = bounds[j] if j < len(bounds) else len(flat)
    return lo, hi


def excluded(text: str, start: int, end: int, spec: ReactionSpec) -> bool:
    if spec.exclude_after:
        following = text[end:end + 12].lower()
        if any(following.startswith(e) for e in spec.exclude_after):
            return True
    if spec.exclude_before:
        preceding = text[max(0, start - 12):start].lower()
        if any(preceding.endswith(e) for e in spec.exclude_before):
            return True
    return False


def classify_dir(name: str) -> tuple[str, str] | None:
    for prefix, kit in DIR_PREFIXES:
        if name.startswith(prefix):
            if prefix == "control-ironclad-":
                return kit, "-"
            m = ROUND_RE.match(name[len(prefix):])
            return kit, (m.group(1) if m else "-")
    return None


def fight_sections(text: str) -> list[tuple[int, str]]:
    """[(offset, label)] for every heading; label is "Fight N[...]" or
    "outside a fight". Any heading that is not a Fight heading resets to
    "outside a fight" -- a retrospective section after the last numbered
    fight (e.g. "## The kit, after 5 fights") is not that fight's content.
    """
    out: list[tuple[int, str]] = [(0, "outside a fight")]
    for m in FIGHT_HEADING.finditer(text):
        heading = m.group(1).strip("* ")
        fm = re.match(r"(Fight\s+\d+[A-Za-z]*(?:\s*\([^)]*\))?)", heading)
        out.append((m.start(), fm.group(1) if fm else "outside a fight"))
    return out


def section_at(sections: list[tuple[int, str]], pos: int) -> str:
    offsets = [o for o, _ in sections]
    i = bisect.bisect_right(offsets, pos) - 1
    return sections[max(i, 0)][1]


def build_of(text: str) -> str:
    identity_end = text.find("## Fight")
    block = text if identity_end == -1 else text[:identity_end]
    m = BUILD_RE.search(block)
    return m.group(1).strip(" *") if m else ""


def trigger_of(sentence: str) -> str:
    for label, pat in TRIGGER_CHECKS:
        if pat.search(sentence):
            return label
    if KIT_CARD_RE.search(sentence):
        return "kit card"
    return "unknown"


def reading_of(sentence: str) -> str:
    if DECISION_RE.search(sentence):
        return "decision"
    if FOUND_RE.search(sentence):
        return "found-afterwards"
    return "unmarked"


@dataclass
class Mention:
    kit: str
    round: str
    file: str
    fight: str
    reaction: str
    trigger: str
    reading: str
    sentence: str
    build: str


@dataclass
class RecordInfo:
    kit: str
    round: str
    file: str
    companion_acquire_lines: int


INPUTS_RE = re.compile(r"^<!-- census-inputs: (.*) -->$", re.M)


def inputs_footer(records: list[tuple[str, str, str, Path]]) -> str:
    """One HTML comment naming every file the census read, repo-relative,
    so `--check` can re-read exactly those and no newer ones."""
    rel = [r[3].relative_to(REPO).as_posix() for r in records]
    return "<!-- census-inputs: " + ";".join(rel) + " -->\n"


def listed_inputs(text: str) -> list[str] | None:
    """The paths a committed census names in its footer, or None when the
    record predates the footer."""
    m = INPUTS_RE.search(text)
    if not m:
        return None
    return [x for x in m.group(1).split(";") if x]


def tree_paths(rev: str) -> set[str]:
    """Every path under review/qa in a git tree, repo-relative posix."""
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", rev, "review/qa"],
        cwd=REPO, capture_output=True, text=True, check=True).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def discover_records(only: set[str] | None = None
                     ) -> list[tuple[str, str, str, Path]]:
    """[(kit, round, dir_name, file_path)], sorted, every file this reads.
    With `only`, a set of repo-relative posix paths, files outside it are
    skipped."""
    out: list[tuple[str, str, str, Path]] = []
    if not QA_DIR.is_dir():
        return out
    for d in sorted(QA_DIR.iterdir()):
        if not d.is_dir():
            continue
        classified = classify_dir(d.name)
        if classified is None:
            continue
        kit, round_label = classified
        for f in sorted(d.glob("*.md")):
            if SKIP_NAME.search(f.name):
                continue
            if only is not None and f.relative_to(REPO).as_posix() not in only:
                continue
            out.append((kit, round_label, d.name, f))
    return out


def extract(records: list[tuple[str, str, str, Path]]
            ) -> tuple[list[Mention], list[RecordInfo]]:
    mentions: list[Mention] = []
    infos: list[RecordInfo] = []
    for kit, round_label, dir_name, path in records:
        text = path.read_text(encoding="utf-8")
        flat = flatten(text)
        bounds = sentence_bounds(text, flat)
        sections = fight_sections(text)
        build = build_of(text)
        acquire_lines = 0
        for line in text.splitlines():
            if COMPANION_RE.search(line) and ACQUIRE_RE.search(line):
                acquire_lines += 1
        infos.append(RecordInfo(kit, round_label, path.name, acquire_lines))
        for spec in REACTIONS:
            for m in spec.pattern.finditer(text):
                if excluded(text, m.start(), m.end(), spec):
                    continue
                lo, hi = sentence_span(flat, bounds, m.start(), m.end())
                sentence = flat[lo:hi].strip()
                mentions.append(Mention(
                    kit=kit, round=round_label, file=path.name,
                    fight=section_at(sections, m.start()),
                    reaction=spec.name,
                    trigger=trigger_of(sentence),
                    reading=reading_of(sentence),
                    sentence=sentence,
                    build=build,
                ))
    return mentions, infos


def truncate(s: str, n: int = 160) -> str:
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    return s[:n - 1].rstrip() + "…"


def md_escape(s: str) -> str:
    return s.replace("|", "\\|")


KIT_ORDER = ["Klee", "Kokomi", "Furina", "Control-Ironclad"]


def render(mentions: list[Mention], infos: list[RecordInfo],
           records: list[tuple[str, str, str, Path]]) -> str:
    n_records = len(records)
    n_mentions = len(mentions)
    have_build = any(m.build for m in mentions)

    lines: list[str] = []
    lines.append("Status: RECORD")
    lines.append("")
    lines.append("# The elemental-reaction census: what the seat records "
                 "say fired, and how")
    lines.append("")
    lines.append(
        f"A keyword census, run 2026-09-05 by `tools/reaction_census.py` "
        f"over {n_records} blind-seat record files under `review/qa/` "
        f"(every `klee-round-*`, `kokomi-round-*`, `furina-reframe-round-*` "
        f"and `control-ironclad-*` directory), for the sweep packet's §4 "
        f"item 2 (`git show 95b2882a:review/active/"
        f"elements-reaction-sweep-2026-09-05.md`, not yet on `main` when "
        f"this ran). It found {n_mentions} mentions of the eight implemented "
        f"reactions (Dendro's Burning is listed and reads zero -- §3 of "
        f"that packet already says why). Every number below is produced by "
        f"re-running the script; nothing here is hand-counted or "
        f"hand-graded.")
    lines.append("")
    lines.append(
        "**This is a keyword count, not a reading.** A \"mention\" is one "
        "regex match of a reaction's name anywhere in a record's prose, "
        "including inside a quoted card or glossary text -- so a reaction "
        "named in a rule box counts exactly the same as one a fight says "
        "fired. \"Trigger\" and \"decision vs. found-afterwards\" are both "
        "literal, priority-ordered keyword matches over the sentence a "
        "mention falls in, not a judgement about what actually happened at "
        "the table. Where a sentence carries neither a decision-word nor a "
        "found-word, it is counted as **unmarked** rather than forced into "
        "either bucket -- and that bucket turns out to be the largest one, "
        "which is itself a finding.")
    lines.append("")

    # -- Per-reaction summary -------------------------------------------
    lines.append("## 1. Per reaction")
    lines.append("")
    lines.append("| Reaction | Mentions | Records | Decision | "
                 "Found-afterwards | Unmarked |")
    lines.append("|---|---|---|---|---|---|")
    per_reaction_records: dict[str, set[tuple[str, str, str]]] = \
        defaultdict(set)
    for m in mentions:
        per_reaction_records[m.reaction].add((m.kit, m.round, m.file))
    for spec in REACTIONS:
        rows = [m for m in mentions if m.reaction == spec.name]
        c = Counter(m.reading for m in rows)
        lines.append(
            f"| {spec.name} | {len(rows)} | "
            f"{len(per_reaction_records[spec.name])} | "
            f"{c['decision']} | {c['found-afterwards']} | {c['unmarked']} |")
    lines.append("")

    # -- Trigger breakdown, reaction x trigger ---------------------------
    trigger_labels = [label for label, _ in TRIGGER_CHECKS] + \
        ["kit card", "unknown"]
    lines.append("## 2. Trigger, by reaction")
    lines.append("")
    header = "| Reaction | " + " | ".join(trigger_labels) + " |"
    lines.append(header)
    lines.append("|" + "---|" * (len(trigger_labels) + 1))
    for spec in REACTIONS:
        rows = [m for m in mentions if m.reaction == spec.name]
        c = Counter(m.trigger for m in rows)
        cells = " | ".join(str(c[t]) for t in trigger_labels)
        lines.append(f"| {spec.name} | {cells} |")
    lines.append("")

    # -- Per-kit summary --------------------------------------------------
    lines.append("## 3. Per kit")
    lines.append("")
    lines.append(
        "\"Records\" here is every record read for that kit, whether or "
        "not it mentions a reaction -- Control-Ironclad's records are read "
        "in full and print zero because base Ironclad has no elements.")
    lines.append("")
    lines.append("| Kit | Records | Mentions | Decision | "
                 "Found-afterwards | Unmarked |")
    lines.append("|---|---|---|---|---|---|")
    records_per_kit = Counter(kit for kit, _, _, _ in records)
    for kit in KIT_ORDER:
        rows = [m for m in mentions if m.kit == kit]
        c = Counter(m.reading for m in rows)
        lines.append(
            f"| {kit} | {records_per_kit[kit]} | {len(rows)} | "
            f"{c['decision']} | {c['found-afterwards']} | {c['unmarked']} |")
    lines.append("")

    # -- Top 10 decision-read sentences -----------------------------------
    lines.append("## 4. Ten decision-read sentences, longest first")
    lines.append("")
    lines.append(
        "\"Most quoted\" is operationalised as: among mentions classified "
        "**decision**, the ten with the longest extracted sentence, ties "
        "broken by (kit, round, file, position in file). Longer is used as "
        "a proxy for \"most says about the choice\", not for importance.")
    lines.append("")
    decisions = [m for m in mentions if m.reading == "decision"]
    decisions_sorted = sorted(
        decisions,
        key=lambda m: (-len(m.sentence), m.kit, m.round, m.file))[:10]
    lines.append("| Record | File | Fight | Reaction | Sentence |")
    lines.append("|---|---|---|---|---|")
    for m in decisions_sorted:
        lines.append(
            f"| {m.kit} {m.round} | {m.file} | {m.fight} | {m.reaction} | "
            f"{md_escape(truncate(m.sentence))} |")
    lines.append("")

    # -- Companion acquisition signal --------------------------------------
    lines.append("## 5. Companion cards named as offered or taken")
    lines.append("")
    lines.append(
        "A line counts if it mentions \"companion\" and at least one of "
        "\"offer\", \"reward\", \"shop\", \"took\", \"passed\" -- a rough "
        "acquisition signal, **not a reading**: it counts lines, not "
        "companions, and says nothing about which companion or whether it "
        "was actually taken.")
    lines.append("")
    nonzero = [i for i in infos if i.companion_acquire_lines > 0]
    total_acquire = sum(i.companion_acquire_lines for i in infos)
    lines.append(
        f"{total_acquire} such lines across {len(nonzero)} of "
        f"{len(infos)} records. Records with at least one:")
    lines.append("")
    lines.append("| Record | File | Lines |")
    lines.append("|---|---|---|")
    for i in sorted(nonzero, key=lambda i: (i.kit, i.round, i.file)):
        lines.append(f"| {i.kit} {i.round} | {i.file} | "
                     f"{i.companion_acquire_lines} |")
    lines.append("")

    # -- Closing limits ------------------------------------------------
    lines.append("## 6. Limits")
    lines.append("")
    lines.append(
        "This is regex over prose, not a reading of any fight. A reaction "
        "named in a rule quote or a keyword-box excerpt counts the same as "
        "one a record says fired. Four proper-noun collisions are excluded "
        "by name because they would otherwise swamp an unrelated reaction "
        "(the relic `Frozen Egg`, the relic `Burning Blood`, the card "
        "`Burning Pact`, Bennett's power `Passion Overload`); nothing else "
        "is hand-filtered, so `Freminet -- Shattering Pressure` and the "
        "base-game card `Shatter` both sit inside the Frozen row on "
        "purpose. \"Sentence\" is cut out of markdown prose by terminal "
        "punctuation or a paragraph break, not a real parser, so an "
        "occasional row runs on past what a human would call one sentence. "
        "Trigger and reading are both literal keyword buckets, checked in "
        "a fixed priority order (see the script's `TRIGGER_CHECKS`, "
        "`DECISION_RE`, `FOUND_RE`); \"unmarked\" is not a reading of "
        "\"no decision happened\", only of \"neither signal phrase is "
        "here\". The companion-acquisition count in §5 is a line count, "
        "not a reading, and does not name which companion.")
    lines.append("")
    if not have_build:
        lines.append(
            "No record's Identity section in this run prints a `Build` "
            "field, so that column is left out of the table below rather "
            "than shipped empty; the script still looks for one "
            "(`BUILD_RE`) and will fill it in the day a record does.")
        lines.append("")

    # -- Full per-mention table --------------------------------------------
    lines.append("## 7. Every mention")
    lines.append("")
    lines.append(
        f"All {n_mentions} mentions, in file order within kit and round. "
        f"Re-run `python tools/reaction_census.py --check` to verify this "
        f"table against the records on disk.")
    lines.append("")
    lines.append("| Record | File | Fight | Reaction | Trigger | Reading | "
                 "Sentence |")
    lines.append("|---|---|---|---|---|---|---|")
    kit_index = {k: i for i, k in enumerate(KIT_ORDER)}

    def sort_key(m: Mention):
        return (kit_index.get(m.kit, len(KIT_ORDER)), m.round, m.file)

    for m in sorted(mentions, key=sort_key):
        lines.append(
            f"| {m.kit} {m.round} | {m.file} | {m.fight} | {m.reaction} | "
            f"{m.trigger} | {m.reading} | {md_escape(truncate(m.sentence))} |")
    lines.append("")

    return "\n".join(lines) + "\n" + inputs_footer(records)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="verify the committed record against the files it "
                         "names, write nothing")
    ap.add_argument("--pin", metavar="REV",
                    help="write over the record files present in this git "
                         "tree (a published census gains its inputs footer "
                         "without its numbers moving)")
    args = ap.parse_args(argv)

    only: set[str] | None = None
    if args.check and OUT.exists():
        listed = listed_inputs(OUT.read_text(encoding="utf-8"))
        if listed is not None:
            only = set(listed)
            missing = [x for x in listed if not (REPO / x).is_file()]
            if missing:
                print(f"reaction_census: {OUT.relative_to(REPO)} names "
                      f"{len(missing)} record file(s) no longer on disk: "
                      + ", ".join(missing[:5]))
                return 1
    elif args.pin:
        only = tree_paths(args.pin)

    records = discover_records(only)
    if not records:
        print("reaction_census: no matching records found under "
              f"{QA_DIR.relative_to(REPO)} -- check the directory patterns",
              file=sys.stderr)
        return 1
    mentions, infos = extract(records)
    text = render(mentions, infos, records)

    if args.check:
        if not OUT.exists():
            print(f"reaction_census: {OUT.relative_to(REPO)} is missing. "
                  f"Run: python tools/reaction_census.py")
            return 1
        current = OUT.read_text(encoding="utf-8")
        if current != text:
            print(f"reaction_census: {OUT.relative_to(REPO)} is STALE -- "
                  f"the seat records on disk no longer match the committed "
                  f"census. Run: python tools/reaction_census.py")
            return 1
        newer = len(discover_records()) - len(records)
        note = (f"; {newer} newer record file(s) under review/qa are not "
                f"counted -- re-run without --check to refresh"
                if newer else "")
        print(f"reaction_census: OK ({len(mentions)} mentions, "
              f"{len(records)} records{note})")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"reaction_census: wrote {OUT.relative_to(REPO)} "
          f"({len(mentions)} mentions, "
          f"{len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
