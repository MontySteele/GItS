"""Census the base game's COLORLESS card pool from the local sts2.dll.

WHY THIS EXISTS
---------------
`docs/current/research/companion-value-vs-colorless-study.md` had to build its
base-colorless reference band out of **Slay the Spire 1** wiki material,
because no StS2 colorless data existed anywhere in this repo. Its own §2 says
so in a warning box. Every companion pricing argument since has rested on that
borrowed band. The companion slate (R234, pick P8) ruled the real thing owed
before any Universal Companion Uncommon or Rare is added or repriced.

`tools/extract_base_game_pool.py` cannot answer it: that tool is built around
CHARACTER pools (`<Character>CardPool`, an `archetype_package`, a Tier 0 sheet)
and its translator exists to decide what our DSL can hold. This one asks a
narrower question -- what IS the colorless pool, by the numbers -- and so it
reads the ctor line, the keyword list and the effect vocabulary of every member
of `ColorlessCardPool` and prints a census. It emits no card sheet and makes no
playability judgement.

IP / REPO RULE (same as its sibling, .gitignore)
------------------------------------------------
This FILE contains no game data and is safe to commit. Its OUTPUT is game data.
The default is stdout for a human to read into a research note; `--json PATH`
is offered for `game_ref/` (gitignored) and nowhere else. The decompiled tree
is a TemporaryDirectory unless `GITS_ILSPY_TREE` says otherwise -- the same
opt-in knob, honoured by the shared helper this imports.

USAGE
-----
    python -m tools.colorless_census
    python -m tools.colorless_census --json game_ref/colorless.json
    python -m tools.colorless_census --cards           # per-card table
    python -m tools.colorless_census --compare         # vs character pools

THE COMPARISON, AND ITS ONE HONEST LIMIT
----------------------------------------
`--compare` runs the same census over the five character pools so "colorless is
priced above character cards at the same rarity" stops being folklore and
becomes a number. What it can honestly produce is a BODY MAGNITUDE: the mean
printed damage and block of the cards that print any, per rarity.

That read is only as good as its coverage, so coverage is reported beside it. A
large part of the colorless pool is 0-cost utility whose value is not a damage
number at all, and no arithmetic over `DamageVar` will ever see it. The census
states the covered share explicitly rather than averaging over a silent
denominator -- an omission that would bias exactly the comparison this exists
to make.

Requires ilspycmd and a local install, exactly as its sibling does; the game
path is read from `klee-mod/local.props` through the same helper, so there
remains exactly one place a machine path is configured.

WHAT IT DOES NOT DO
-------------------
It does not read card TEXT. Descriptions live in the localisation blob inside
`SlayTheSpire2.pck`, not in the assembly, and a census of costs and rarities
does not need them. Effect shape is read STRUCTURALLY from the decompiled body
-- the `*Cmd.Method(` vocabulary -- never from a name table, so this file stays
free of base-game content the way its sibling does.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from tools.extract_base_game_pool import (
    CARD_NS,
    CMD,
    CTOR,
    GENERIC_CMD,
    KEYWORD,
    MP_ONLY,
    POOL_NS,
    POWER,
    VAR,
    _read_decompiled_type,
    decompiled_project,
    game_dll,
)

POOL_TYPE = f"{POOL_NS}ColorlessCardPool"
# `ModelDb.Card<Alchemize>(),` -- one pool member per line.
MEMBER = re.compile(r"ModelDb\.Card<(\w+)>\(\)")
# `return new CardModel[65]` -- the pool's own declared size, checked against
# the number of members actually parsed so a decompiler quirk cannot silently
# shorten the census.
DECLARED = re.compile(r"new CardModel\[(\d+)\]")
# `public static ... Cards => ` in an epoch, listing the cards it gates.
EPOCH_MEMBER = re.compile(r"ModelDb\.Card<(\w+)>")


def pool_members(root: Path) -> tuple[list[str], int]:
    """Every card type named by ColorlessCardPool.GenerateAllCards."""
    src = _read_decompiled_type(root, POOL_TYPE)
    members = MEMBER.findall(src)
    declared = DECLARED.search(src)
    size = int(declared.group(1)) if declared else -1
    if size >= 0 and size != len(members):
        sys.exit(f"pool declares {size} cards but {len(members)} were parsed")
    if not members:
        sys.exit("no cards found in ColorlessCardPool -- check the shape")
    return members, size


def read_card(root: Path, name: str) -> dict:
    """Cost, type, rarity, keywords and effect vocabulary for one card."""
    src = _read_decompiled_type(root, f"{CARD_NS}{name}")
    ctor = CTOR.search(src)
    if not ctor:
        sys.exit(f"{name}: no CardModel ctor matched -- the shape changed")
    cost, card_type, rarity = ctor.groups()
    cmds = sorted({f"{a}.{b}" for a, b in CMD.findall(src)}
                  | {f"{a}.{b}" for a, b in GENERIC_CMD.findall(src)})
    return {
        "name": name,
        "cost": int(cost),
        "type": card_type,
        "rarity": rarity,
        "keywords": sorted(set(KEYWORD.findall(src))),
        "vars": {k: v for k, v in VAR.findall(src)},
        "powers": sorted(set(POWER.findall(src))),
        "cmds": cmds,
        "multiplayer_only": bool(MP_ONLY.search(src)),
    }


def epoch_gates(root: Path) -> dict[str, list[str]]:
    """Which unlock epoch gates which colorless card, when one does.

    The pool filters itself through five `Colorless<N>Epoch` types, so a fresh
    save does not see all 65. Which cards those epochs name is part of the
    acquisition answer, not a footnote.
    """
    gates: dict[str, list[str]] = {}
    for n in range(1, 6):
        short = f"Colorless{n}Epoch"
        matches = sorted(root.rglob(f"{short}.cs"))
        if not matches:
            continue
        src = matches[0].read_text(encoding="utf-8")
        gates[short] = sorted(set(EPOCH_MEMBER.findall(src)))
    return gates


def census(cards: list[dict]) -> dict:
    """The aggregate reads the research note cites."""
    by_rarity = Counter(c["rarity"] for c in cards)
    by_cost = Counter(c["cost"] for c in cards)
    by_type = Counter(c["type"] for c in cards)
    exhaust = [c["name"] for c in cards if "Exhaust" in c["keywords"]]
    cost_by_rarity: dict[str, Counter] = {}
    for c in cards:
        cost_by_rarity.setdefault(c["rarity"], Counter())[c["cost"]] += 1
    return {
        "pool_size": len(cards),
        "by_rarity": dict(sorted(by_rarity.items())),
        "by_cost": dict(sorted(by_cost.items())),
        "by_type": dict(sorted(by_type.items())),
        "cost_by_rarity": {r: dict(sorted(c.items()))
                           for r, c in sorted(cost_by_rarity.items())},
        "exhaust_count": len(exhaust),
        "exhaust_share": round(len(exhaust) / len(cards), 4) if cards else 0.0,
        "exhaust_cards": sorted(exhaust),
        "keyword_counts": dict(sorted(Counter(
            k for c in cards for k in c["keywords"]).items())),
        "multiplayer_only": sorted(c["name"] for c in cards
                                   if c["multiplayer_only"]),
    }


CHARACTERS = ("Ironclad", "Silent", "Defect", "Regent", "Necrobinder")


def named_pool(root: Path, pool: str) -> list[str]:
    """Members of any `<Name>CardPool`, by the same shape as the colorless one.

    Character pools are read with the SAME regex deliberately. If MegaCrit ever
    changes how a pool lists itself, the comparison must break loudly on both
    sides rather than quietly compare a full pool against a partial one.
    """
    src = _read_decompiled_type(root, f"{POOL_NS}{pool}CardPool")
    members = MEMBER.findall(src)
    if not members:
        sys.exit(f"no cards found in {pool}CardPool -- check the shape")
    return members


def _mag(card: dict, kind: str) -> float | None:
    """The printed Damage/Block magnitude of a card, or None if it prints none.

    `vars` is keyed by the Var class prefix the extractor's VAR regex captured
    (`Damage`, `Block`, `Magic`, ...). A card with no such var is not a zero --
    it is a card whose value this metric cannot see, and it must stay out of
    the mean rather than drag it down.
    """
    raw = card["vars"].get(kind)
    return float(raw) if raw is not None else None


def magnitude_bands(cards: list[dict]) -> dict:
    """Mean printed damage and block per rarity, WITH coverage."""
    out: dict[str, dict] = {}
    for rarity in sorted({c["rarity"] for c in cards}):
        rows = [c for c in cards if c["rarity"] == rarity]
        band: dict[str, object] = {"n": len(rows)}
        for kind in ("Damage", "Block"):
            vals = [(_mag(c, kind), c["cost"]) for c in rows]
            vals = [(v, k) for v, k in vals if v is not None]
            band[kind.lower()] = {
                "n_printing": len(vals),
                "coverage": round(len(vals) / len(rows), 3) if rows else 0.0,
                "mean": round(sum(v for v, _ in vals) / len(vals), 2)
                        if vals else None,
                # Per-energy is only defined above 0 cost; a 0-cost body has
                # no rate, and dividing by zero-or-one to keep the column full
                # would invent the very premium we are trying to measure.
                "mean_per_energy": round(
                    sum(v / k for v, k in vals if k > 0)
                    / max(1, len([1 for _, k in vals if k > 0])), 2)
                    if any(k > 0 for _, k in vals) else None,
                "n_zero_cost_excluded": len([1 for _, k in vals if k == 0]),
            }
        out[rarity] = band
    return out


def compare(root: Path, colorless: list[dict]) -> dict:
    """The colorless census beside the five character pools."""
    out = {"Colorless": {
        "pool_size": len(colorless),
        "by_rarity": dict(sorted(Counter(
            c["rarity"] for c in colorless).items())),
        "exhaust_share": round(sum("Exhaust" in c["keywords"]
                                   for c in colorless) / len(colorless), 3),
        "mean_cost": round(sum(c["cost"] for c in colorless)
                           / len(colorless), 2),
        "bands": magnitude_bands(colorless),
    }}
    for who in CHARACTERS:
        cards = [read_card(root, n) for n in named_pool(root, who)]
        out[who] = {
            "pool_size": len(cards),
            "by_rarity": dict(sorted(Counter(
                c["rarity"] for c in cards).items())),
            "exhaust_share": round(sum("Exhaust" in c["keywords"]
                                       for c in cards) / len(cards), 3),
            "mean_cost": round(sum(c["cost"] for c in cards) / len(cards), 2),
            "bands": magnitude_bands(cards),
        }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default=None,
                    help="write the full census to PATH (game_ref/ only -- "
                         "the output is game data)")
    ap.add_argument("--cards", action="store_true",
                    help="also print the per-card table")
    ap.add_argument("--compare", action="store_true",
                    help="also census the five character pools for the "
                         "same-rarity comparison")
    args = ap.parse_args(argv)

    comparison = None
    with decompiled_project(game_dll()) as root:
        members, declared = pool_members(root)
        cards = [read_card(root, name) for name in members]
        gates = epoch_gates(root)
        if args.compare:
            comparison = compare(root, cards)

    agg = census(cards)
    agg["declared_array_size"] = declared
    agg["epoch_gated"] = {k: len(v) for k, v in gates.items()}

    if args.cards:
        print(f"{'card':<22}{'cost':>5}  {'type':<7}{'rarity':<10}keywords")
        for c in sorted(cards, key=lambda c: (c["rarity"], c["cost"],
                                              c["name"])):
            print(f"{c['name']:<22}{c['cost']:>5}  {c['type']:<7}"
                  f"{c['rarity']:<10}{','.join(c['keywords'])}")
        print()
    print(json.dumps(agg, indent=2))
    if comparison is not None:
        print(json.dumps({"comparison": comparison}, indent=2))

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload: dict = {"census": agg, "cards": cards, "epochs": gates}
        if comparison is not None:
            payload["comparison"] = comparison
        out.write_text(json.dumps(payload, indent=2) + "\n",
                       encoding="utf-8")
        print(f"wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
