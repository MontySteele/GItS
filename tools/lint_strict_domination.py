"""Strict-domination lint across card sheets (worknote 2026-07-20 item 2).

Rarity buys different or bigger-with-a-twist, never "the common plus
stuff": within one sheet, two cards at the same cost/type/gates where
one's effect set is a superset of the other's with every shared amount
>= (and at least one strict excess) leave the lesser card a dead pick.
Confirmed class: cant_catch_me over warm_glow (Klee, queued errata),
pit_orchestra over macaron_break (Furina, resolves pass 2).

Scope per the assigning worknote, narrowed by R26 (2026-07-20): the law
protects draft decisions between cards competing at similar weight —
an ADJACENT-RARITY phenomenon (common<->uncommon, uncommon<->rare).
Adjacent-rarity strict dominations are findings; two-step gaps (rare
over common) print as informational only — rares are the designated
power spike, and a rare obsoleting a common's slot is the rarity ladder
working. Basics are excluded entirely — starters are supposed to be
outclassed (Strike is strictly dominated by half the base game, by
design). Cards are only compared inside an identical (cost, type,
encore_cost, exhaust, tags) group, so a playability gate or Exhaust
rider makes a pair incomparable rather than falsely dominated; formula
amounts also mark a card incomparable.

Effects are split into benefits and COSTS (self-damage, discard,
spend_encore): domination needs benefits superset-with-all->= AND costs
subset-with-all-<=. Hot Hands (spark 3 + 2 self-damage) does NOT
dominate Spark Collection (spark 2) — the blood is the twist that
uncommon legitimately buys. This matters: without it the lint's first
run flagged three ratified bigger-with-a-twist shapes as dominations.

KNOWN pairs are dominations already ruled on and awaiting their
scheduled fix: printed as notes, exit stays 0. Remove an entry when its
errata lands — the lint then guards the fix.

Usage: python tools/lint_strict_domination.py docs/klee-cards.yaml [...]
Exit 0 clean; exit 1 with one finding per line.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

# Known dominations awaiting their scheduled fix. Remove when landed.
KNOWN = {
    # Queued errata (worknote item 1): cant_catch_me {block: -2}, lands
    # AFTER the R10 Crackle measurement window. Drop this entry then.
    frozenset({"cant_catch_me", "warm_glow"}),
    # Resolves at Furina pass 2 with the R16 re-costing. Drop then.
    frozenset({"pit_orchestra", "macaron_break"}),
}

# Lint-discovered dominations with NO ruling yet (DECISIONS 76). They do
# not fail the lint — the sheets belong to their sessions and edits need
# red-pen first — but they print as NEEDS RULING until dispositioned:
# move to KNOWN with a schedule, fix the rows, or rule them accepted.
# (sparkly_explosion/big_badda_boom was here; CLEARED by R26 — a
# rare-over-common two-step gap is informational, not a finding.)
PENDING_RULING = {
    # block 8 + exhaust-a-status vs block 7: the CCM shape exactly.
    frozenset({"dodge_roll", "hide_and_seek"}),
}

RARITY_ORDER = {"common": 0, "uncommon": 1, "rare": 2}


def is_cost(eff: dict) -> bool:
    """Detrimental effect: paying it is worse, not better."""
    op = eff.get("op")
    return (op in ("discard", "spend_encore")
            or (op == "damage" and eff.get("target") == "self"))


def effect_maps(card: dict) -> tuple[dict, dict] | None:
    """(benefits, costs) as signature -> total amount; None if incomparable."""
    good: dict = {}
    bad: dict = {}
    for eff in card.get("effects", []):
        m = bad if is_cost(eff) else good
        eff = dict(eff)
        amount = eff.pop("amount", 1)
        if not isinstance(amount, int):
            return None  # formula/complex amount
        key = tuple(sorted((k, str(v)) for k, v in eff.items()))
        m[key] = m.get(key, 0) + amount
    return good, bad


def dominates(a: dict, b: dict) -> bool:
    ea, eb = effect_maps(a), effect_maps(b)
    if ea is None or eb is None:
        return False
    ga, ca = ea
    gb, cb = eb
    # benefits: a carries everything b does, at >= amounts
    if not set(gb) <= set(ga) or any(ga[k] < gb[k] for k in gb):
        return False
    # costs: a pays no cost b doesn't, at <= amounts
    if not set(ca) <= set(cb) or any(ca[k] > cb[k] for k in ca):
        return False
    return (ga, ca) != (gb, cb)


def comparison_group(card: dict) -> tuple:
    return (card.get("cost"), card.get("type"), card.get("encore_cost"),
            card.get("exhaust"), tuple(sorted(card.get("tags", []))))


def lint_sheet(path: Path) -> tuple[list[str], list[str]]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    cards = [c for c in rows
             if isinstance(c, dict) and c.get("effects")
             and c.get("rarity") not in (None, "basic")]
    findings: list[str] = []
    notes: list[str] = []
    for a in cards:
        for b in cards:
            if a is b or a["rarity"] == b["rarity"]:
                continue
            if comparison_group(a) != comparison_group(b):
                continue
            if dominates(a, b):
                pair = frozenset({a["id"], b["id"]})
                msg = (f"{path.name}: {a['id']} ({a['rarity']}) strictly "
                       f"dominates {b['id']} ({b['rarity']}) at cost "
                       f"{a.get('cost')}")
                ra = RARITY_ORDER.get(a["rarity"])
                rb = RARITY_ORDER.get(b["rarity"])
                adjacent = (ra is not None and rb is not None
                            and abs(ra - rb) == 1)
                if pair in KNOWN:
                    notes.append(f"known (allowlisted): {msg}")
                elif not adjacent:
                    notes.append(f"informational (non-adjacent rarities, "
                                 f"R26): {msg}")
                elif pair in PENDING_RULING:
                    notes.append(f"NEEDS RULING (pending, DECISIONS 76): "
                                 f"{msg}")
                else:
                    findings.append(msg)
    return findings, notes


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or [REPO / "docs" / "klee-cards.yaml",
                                        REPO / "docs" / "furina-cards.yaml"]
    findings: list[str] = []
    for p in paths:
        found, notes = lint_sheet(p)
        findings.extend(found)
        for n in notes:
            print(n)
    for f in findings:
        print(f)
    print(f"{'CLEAN' if not findings else f'{len(findings)} finding(s)'}: "
          f"{', '.join(p.name for p in paths)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
