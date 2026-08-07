#!/usr/bin/env python3
"""L7: the `# a -> b` arithmetic on an upgrade row must still be true.

THE INCIDENT (SYS-11a/b, S1 parity sweep). An upgrades sheet row is two
claims wearing one line:

    surging_shoal:  {damage: +2}          # 4->6

the DELTA (machine-read, applied by tier0/content/upgrades.py) and the
ARITHMETIC (prose, read by humans, applied by nobody). When a card is
repriced, the delta usually does not move -- it is the BASE that moves --
so the delta stays correct and the arithmetic silently stops being. The
sweep found six of them on `kokomi-upgrades.yaml` alone, and
`surging_shoal`'s had been wrong through two successive repricings, "in
the file whose whole job is to say what a card becomes" (its own note, now
in the sheet).

That is the worst shape a stale comment can take: it is not vague, it is
ARITHMETIC. A reader checks it, the numbers add up, and they conclude the
row is verified -- when what they verified is that the old base and the old
result still differ by the delta.

WHY A SCAN RATHER THAN A CURATED CLAIM LIST. `test_pulse_multiplier_claims`
argues the other way for prose ("a regex cannot tell a record from a claim;
an author can"), and it is right about prose. It is not right about this
file. Upgrade rows are UNIFORM: one id, one delta mapping, and a comment
whose `a -> b` is by convention about THIS row's card. So the check is
mechanical, and both halves of it are anchored in data the lint reads
rather than in a table someone has to maintain -- which matters, because a
registry of 200 upgrade rows is a second copy of the sheet and would go
stale in exactly the way the sheet did.

Historical records DO occur here, and they are the norm on this file rather
than the exception: a repricing that moves a base is usually NARRATED in the
row it moved ("was 7->9", "base errata'd 8->6", "the base went 18->40"), so
the live arithmetic and its own history sit on one line. The marker is
therefore the house `(lint-ok: ...)` one, NARROWED: it names the pair it
exempts.

    surging_shoal: {damage: +2}   # R77: 6->8 all (was 7->9; lint-ok: 7->9)

`6->8` is still recomputed; only `7->9` is excused. A marker with no pair in
it exempts the whole line, which is the older convention and still honoured,
but naming the pair is what stops an exemption written for a history note
from quietly covering the live number beside it. Both directions, as usual:
a marker naming a pair that is no longer on the line is itself a finding.

TWO CHECKS PER PAIR, and they catch different things:

  ARITHMETIC  `b - a` must equal one of the row's delta values (or their
              sum, for the "4+4 -> 6+6" two-key shape). Catches a delta
              that was edited and a comment that was not.

  BASE        `a` must be a number the CARD actually prints -- any integer
              in its row, or a sum of two printed amounts (the "13->16 over
              the bar" shape, where 13 is base 7 plus a 6 in a branch).
              Catches the repricing class, where `b - a` still equals the
              delta and both numbers describe a card that no longer exists.

Neither alone is enough: SYS-11a's rows all passed the arithmetic check.

Plus SYS-11b, one line of the same family: a comment claiming a CAP is
preserved ("proc cap 3 unchanged") when the card row carries no such cap
field. The uncap-all ruling of 2026-07-24 dropped five stack ceilings and
left five comments still promising them.

Run:  python tools/lint_upgrade_comment_arithmetic.py [sheet ...]
Exit 0 clean; exit 1 with one finding per line.
"""

from __future__ import annotations

import re
import sys
from itertools import combinations
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.effect_walk import iter_effects, printed_floor  # noqa: E402

DOCS = REPO / "docs"

UPGRADE_SHEETS = ("klee-upgrades.yaml", "furina-upgrades.yaml",
                  "kokomi-upgrades.yaml", "ref-ironclad-upgrades.yaml")

# Where the BASE cards live. The ref-ironclad rows are modelled analogues in
# tier0, not docs sheets, so both trees are indexed -- an upgrade sheet whose
# cards the lint cannot find would otherwise report a clean run on rows it
# never checked.
CARD_SOURCES = (
    tuple(sorted(DOCS.glob("*-cards.yaml")))
    + tuple(sorted(DOCS.glob("*-companions.yaml")))
    + tuple(sorted((REPO / "tier0" / "content" / "cards").glob("*.yaml")))
)

# `id: {delta}` at column 0, with whatever trailing comment.
ENTRY = re.compile(r"^([a-z_][a-z0-9_]*):\s*(\{.*\})\s*(?:#(.*))?$")
# A column-0 comment is a section header or a note about the FILE; an
# indented one continues the row above it. Same rule lint_sheet_comments.py
# uses on the card sheets, and for the same reason.
CONTINUATION = re.compile(r"^\s+#(.*)$")

ARROW = re.compile(r"(?<![\w.])(\d+)\s*(?:->|-->|→)\s*(\d+)(?![\w.])")
# `(lint-ok: 7->9 -- reason)`. The group is everything the author wrote after
# the colon, which is where the exempted pair(s) and the reason both live.
LINT_OK = re.compile(r"lint-ok:?([^)\n]*)")
CAP_CLAIM = re.compile(
    r"\bcap\s+(\d+)\s+(?:unchanged|stays|holds|preserved)"
    r"|\bcap\s+(?:unchanged|stays|holds|preserved)\s+at\s+(\d+)",
    re.IGNORECASE)
# Fields on a card row that ARE a cap. Curated: a lint that guessed "any key
# containing 'cap'" would read `fanfare_cap` -- an upgrade KEY, not a ceiling.
CAP_FIELDS = ("max_stacks", "splash_procs_per_turn", "cap", "max")


def card_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for path in CARD_SOURCES:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if isinstance(loaded, dict):
            loaded = loaded.get("cards", [])
        for row in loaded:
            if isinstance(row, dict) and "id" in row:
                index.setdefault(row["id"], row)
    return index


def allowed_bases(row: dict) -> set[int]:
    """Every number this card PRINTS, plus pairwise sums of its amounts.

    Whole-row digits rather than a per-delta-key lookup on purpose: the
    comments legitimately quote slopes out of formula strings
    (`2_per_companion_played_this_turn` -> "+2 -> +3 Block per Companion"),
    costs, bomb damage and power amounts, and a key-to-field map would have
    to be re-derived every time the DSL grows a field. The strictness this
    lint needs comes from the ARITHMETIC check; this half only has to be
    able to say "that number is not on this card at all", which is exactly
    the repricing class.

    The pairwise sums cover the sheets' "so 13->16 over the bar" idiom,
    where the quoted base is the printed line plus a conditional's branch.
    """
    text = yaml.safe_dump(row, allow_unicode=True, sort_keys=True)
    bases = {int(n) for n in re.findall(r"\d+", text)}
    amounts = [n for n in
               (printed_floor(fx) for fx in iter_effects(row.get("effects")))
               if isinstance(n, int)]
    bases.update(a + b for a, b in combinations(amounts, 2))
    return bases


def allowed_deltas(delta: dict) -> set[int]:
    values = [v for v in delta.values()
              if isinstance(v, int) and not isinstance(v, bool)]
    out = set(values)
    if len(values) > 1:
        out.add(sum(values))
    return out


def exemptions(text: str) -> tuple[str, set[tuple[int, int]], bool]:
    """(text with the markers removed, pairs excused, whole-line exempt?).

    The markers are stripped before the line is scanned so a marker's own
    `7->9` is not then read as a claim needing checking.
    """
    marks = list(LINT_OK.finditer(text))
    if not marks:
        return text, set(), False
    excused: set[tuple[int, int]] = set()
    for m in marks:
        excused |= {(int(a), int(b)) for a, b in ARROW.findall(m.group(1))}
    stripped = LINT_OK.sub(" ", text)
    return stripped, excused, not excused


def entries(path: Path) -> list[tuple[str, dict, list[tuple[int, str]]]]:
    """[(card id, delta mapping, [(lineno, comment text), ...])]."""
    out: list[tuple[str, dict, list[tuple[int, str]]]] = []
    current: tuple[str, dict, list] | None = None
    for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1):
        m = ENTRY.match(line)
        if m:
            card_id, raw, comment = m.group(1), m.group(2), m.group(3)
            delta = yaml.safe_load(raw)
            current = (card_id, delta if isinstance(delta, dict) else {}, [])
            if comment:
                current[2].append((lineno, comment))
            out.append(current)
            continue
        cont = CONTINUATION.match(line)
        if cont and current is not None:
            current[2].append((lineno, cont.group(1)))
            continue
        if not line.strip():
            continue
        # A column-0 comment, or any other line, ends the row's block.
        current = None
    return out


def lint_sheet(path: Path, cards: dict[str, dict]) -> tuple[list[str], dict]:
    findings: list[str] = []
    scope = {"rows": 0, "with_arrow": 0, "pairs": 0, "cap_claims": 0,
             "no_card": 0, "exempt_lines": 0, "exempt_pairs": 0}
    for card_id, delta, comments in entries(path):
        scope["rows"] += 1
        row = cards.get(card_id)
        if row is None:
            scope["no_card"] += 1
            findings.append(
                f"{path.name}: {card_id}: no card row with this id on any"
                " sheet -- the upgrade delta applies to nothing, and its"
                " arithmetic cannot be checked against anything.")
            continue
        bases = allowed_bases(row)
        deltas = allowed_deltas(delta)
        saw_arrow = False
        for lineno, raw_text in comments:
            text, excused, whole_line = exemptions(raw_text)
            if whole_line:
                scope["exempt_lines"] += 1
                continue
            pairs = [(int(a), int(b)) for a, b in ARROW.findall(text)]
            scope["exempt_pairs"] += len(excused)
            for stale in sorted(excused - set(pairs)):
                findings.append(
                    f"{path.name}:{lineno}: {card_id}: `lint-ok:"
                    f" {stale[0]}->{stale[1]}` excuses a pair that is not on"
                    " this line any more. Delete the marker -- an exemption"
                    " outliving its claim is cover for the next one.")
            for a_s, b_s in ARROW.findall(text):
                if (int(a_s), int(b_s)) in excused:
                    continue
                saw_arrow = True
                scope["pairs"] += 1
                a, b = int(a_s), int(b_s)
                if deltas and (b - a) not in deltas:
                    findings.append(
                        f"{path.name}:{lineno}: {card_id}: comment says"
                        f" {a}->{b} (a change of {b - a:+d}) but the row's"
                        f" delta is {delta} -- the arithmetic and the applied"
                        " delta disagree. Fix the comment, or excuse this"
                        f" pair with `(lint-ok: {a}->{b} -- <why this is a"
                        " historical record>)`.")
                elif a not in bases:
                    findings.append(
                        f"{path.name}:{lineno}: {card_id}: comment says"
                        f" {a}->{b}, but {a} is not a number the card prints"
                        f" (row has {sorted(n for n in bases if n < 100)}) --"
                        " the base moved and the annotation did not. Fix the"
                        f" comment, or excuse this pair with `(lint-ok:"
                        f" {a}->{b} -- <why>)`.")
            for hi, lo in CAP_CLAIM.findall(text):
                scope["cap_claims"] += 1
                claimed = int(hi or lo)
                caps = [v for fx in iter_effects(row.get("effects"))
                        for k, v in fx.items()
                        if k in CAP_FIELDS and isinstance(v, int)]
                if claimed not in caps:
                    findings.append(
                        f"{path.name}:{lineno}: {card_id}: comment promises a"
                        f" cap of {claimed} is preserved, but the card row"
                        f" carries no such ceiling (cap fields found:"
                        f" {caps or 'none'}). The uncap-all ruling"
                        " (2026-07-24) dropped stack ceilings and left the"
                        " comments promising them.")
        if saw_arrow:
            scope["with_arrow"] += 1
    return findings, scope


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or [DOCS / s for s in UPGRADE_SHEETS]
    cards = card_index()
    findings: list[str] = []
    for path in paths:
        sheet_findings, scope = lint_sheet(path, cards)
        findings += sheet_findings
        for f in sheet_findings:
            print(f)
        # The denominator, per the house rule: "CLEAN" with no scope is the
        # confident half of a partial check, and this lint's silence on a row
        # with no `a -> b` is silence, not approval.
        print(f"scope {path.name}: {scope['rows']} upgrade row(s),"
              f" {scope['with_arrow']} carrying `a -> b` arithmetic"
              f" ({scope['pairs']} pair(s) recomputed),"
              f" {scope['cap_claims']} cap claim(s),"
              f" {scope['exempt_pairs']} pair(s) + {scope['exempt_lines']}"
              f" whole line(s) excused by lint-ok,"
              f" {scope['no_card']} row(s) with no card")
    print(f"{'CLEAN' if not findings else f'{len(findings)} finding(s)'}: "
          f"{', '.join(p.name for p in paths)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
