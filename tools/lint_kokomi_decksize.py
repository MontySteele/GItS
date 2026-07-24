"""Kokomi deck-size grammar lint (kickoff v1 §1 law 4, user-authored).

THE LAW (Kokomi personal pool ONLY — not mod-wide, not companion pools):
Common cards may not increase deck size — they may only reduce it or
replace themselves (net card delta <= 0). Uncommon and Rare may create
cards, priced so a positive-sum engine needs Rare payoffs plus solved
draw/energy velocity.

Catch→lint culture: the law is machine-checkable, so it ships as a gate
(test_sheet_lints), not a convention. Basics are held to the Common bar
too (stricter than the law's letter; a basic that mints cards would be a
starter-guaranteed engine, which is the exact loop the law breaks).

Accounting:
  created  = add_card amounts + conscript(mode=create) amounts +
             generate_from_pool / generate_guest_star amounts
             (recursed through conditional then/else and sly lists)
  consumed = exhaust_from amounts ("all" counts as the whole hand, 10) +
             1 if the card itself Exhausts
  Conscript's default transform mode is delta ZERO (replace, never
  create). Draw/discard move cards, they don't mint or burn them.

Usage: python tools/lint_kokomi_decksize.py docs/kokomi-cards.yaml
Exit 0 clean; exit 1 with one finding per line.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

CREATE_OPS = {"add_card", "generate_from_pool", "generate_guest_star"}
CHECKED_RARITIES = {"basic", "common"}
ALL_SENTINEL = 10                    # MAX_HAND_SIZE: "all" burns the hand


def _walk(effects: list[dict]):
    for fx in effects or []:
        yield fx
        yield from _walk(fx.get("then", []))
        yield from _walk(fx.get("else", []))


def _amount(fx: dict) -> int:
    n = fx.get("amount", 1)
    if n == "all":
        return ALL_SENTINEL
    return n if isinstance(n, int) else 1     # formula amounts: floor at 1


def card_delta(row: dict) -> int:
    created = consumed = 0
    for fx in list(_walk(row.get("effects", []))) + list(
            _walk(row.get("sly", []))):
        op = fx.get("op")
        if op in CREATE_OPS:
            created += _amount(fx)
        elif op == "conscript" and fx.get("mode") == "create":
            created += _amount(fx)
        elif op == "exhaust_from":
            consumed += _amount(fx)
    if row.get("exhaust"):
        consumed += 1
    return created - consumed


def lint(paths: list[str]) -> list[str]:
    findings = []
    for path in paths:
        rows = yaml.safe_load(Path(path).read_text()) or []
        for row in rows:
            if row.get("rarity") not in CHECKED_RARITIES:
                continue
            delta = card_delta(row)
            if delta > 0:
                findings.append(
                    f"{Path(path).name}: {row['id']} ({row['rarity']}) nets "
                    f"card delta +{delta} — Commons may only reduce the deck "
                    f"or replace themselves (kickoff §1 law 4)")
    return findings


def main(argv: list[str]) -> int:
    paths = argv or ["docs/kokomi-cards.yaml"]
    findings = lint(paths)
    for f in findings:
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
