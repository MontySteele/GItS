"""Sheet comment/number consistency lint (Furina sheet red-pen, flag 1).

Catches the tuning-round drift class: a prose comment quoting a number
("Eight points of deferred HP") that no longer matches the row's actual
effects (amount: 6). Deliberately heuristic — it extracts number tokens
(digits AND spelled-out words) from each card's trailing comments and
checks membership against an allowed set built from the row itself:

  - every digit on the card's own row lines (cost, amounts, encore_cost,
    max_stacks, threshold predicates, formulas);
  - pairwise sums of the row's `amount:` values ("an honest 5 that
    becomes 12" phrasing on conditional kickers);
  - fanfare-cap arithmetic for `N_per_M_fanfare` formulas ("at cap:
    8+7" phrasing): base cap, uncapped cap, and each cap // divisor;
  - a small global set: maxHP 60, meter 70, the caps, and the salon
    economy constants (tick damage / upkeep / burst), which comments
    legitimately cite on member cards;
  - 0, 1, 2 are always allowed ("turn one", "two conventions" — prose
    this small is noise, not drift).

Skipped tokens: section/version/ruling refs (§3.2, v1.9, R8, A6,
DECISIONS 64, Guardrail 6), ranges and dates (4-5, 2026-07-20),
percentages, and "5-star". A comment line containing `lint-ok` is
exempt entirely (for prose whose numbers are deliberately external).

Usage: python tools/lint_sheet_comments.py docs/furina-cards.yaml [...]
Exit 0 clean; exit 1 with one finding per line.
"""

from __future__ import annotations

import re
import sys
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tier0 import constants as C  # noqa: E402

WORDS = {w: n for n, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen "
    "twenty".split())}

CARD_START = re.compile(r"^- \{id: (\w+)")
# Card comments are INDENTED; a column-0 comment is a section header and
# ends the current card's block.
COMMENT = re.compile(r"^\s+#")
HEADER = re.compile(r"^#")
# Refs that are never card numbers; stripped before token extraction.
SKIP = re.compile(
    r"§[\d.]+\w?|v[\d.]+|(?<![A-Za-z])[AR]\d+|DECISIONS \d+|"
    r"Guardrail \d+|flag \d+|\d+-star|\d+%|\d+[-–]\d+")
NUM = re.compile(r"(?<![\w.])(\d+)")


def card_numbers(row_lines: list[str], max_hp: int) -> set[int]:
    text = " ".join(row_lines)
    allowed = {int(n) for n in re.findall(r"\d+", text)}
    amounts = [int(n) for n in re.findall(r"amount: (\d+)", text)]
    allowed.update(a + b for a, b in combinations(amounts, 2))
    cap = int(max_hp * C.FANFARE_CAP_FRACTION)
    caps = [cap] + [cap + int(n) for n in
                    re.findall(r"raise_fanfare_cap, amount: (\d+)", text)]
    allowed.update(caps)
    for div in re.findall(r"_per_(\d+)_fanfare", text):
        allowed.update(c // int(div) for c in caps)
        allowed.update(a + cap // int(div) for a in amounts)
    return allowed


def lint_sheet(path: Path) -> list[str]:
    max_hp = 60  # Furina; per-sheet if a third character ever needs it
    globals_ok = {0, 1, 2, max_hp, 70, int(max_hp * C.FANFARE_CAP_FRACTION),
                  C.SALON_TICK_ENCORE_COST, C.SALON_TICK_BURST,
                  C.SALON_FOCUS_PER}
    # Salon v2: every member tick/bow number is quotable in comments, plus
    # its dry three-quarters form (the v1 SALON_MEMBER_DMG family's heir).
    for spec in C.SALON_MEMBERS.values():
        for half in ("tick", "bow"):
            for v in spec[half].values():
                if isinstance(v, int):
                    globals_ok.add(v)
                    globals_ok.add(int(v * C.SALON_DRY_DAMAGE_MULT))
    findings: list[str] = []
    card_id, row_lines, comments = None, [], []

    def flush():
        if card_id is None:
            return
        allowed = card_numbers(row_lines, max_hp) | globals_ok
        for lineno, line in comments:
            if "lint-ok" in line:
                continue
            stripped = SKIP.sub(" ", line)
            cited = {int(n) for n in NUM.findall(stripped)}
            cited |= {WORDS[w] for w in
                      re.findall(r"[A-Za-z]+", stripped.lower())
                      if w in WORDS}
            for n in sorted(cited - allowed):
                findings.append(
                    f"{path.name}:{lineno}: {card_id}: comment cites {n}, "
                    f"row has {sorted(allowed & set(range(100)))}")

    for lineno, line in enumerate(path.read_text(encoding="utf-8")
                                  .splitlines(), 1):
        m = CARD_START.match(line)
        if m:
            flush()
            card_id, row_lines, comments = m.group(1), [line], []
        elif HEADER.match(line):
            flush()
            card_id, row_lines, comments = None, [], []
        elif card_id and COMMENT.match(line):
            comments.append((lineno, line))
        elif card_id:
            row_lines.append(line)
    flush()
    return findings


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or [REPO / "docs" / "furina-cards.yaml"]
    findings = [f for p in paths for f in lint_sheet(p)]
    for f in findings:
        print(f)
    print(f"{'CLEAN' if not findings else f'{len(findings)} finding(s)'}: "
          f"{', '.join(p.name for p in paths)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
