#!/usr/bin/env python3
"""EB-118: the six constraints on exhaust-pile retrieval, swept.

WHY THIS EXISTS. `recall_to_draw` gained a SOURCE (`from: exhaust`), not a
parallel op family, and the packet's §6.4 puts all six constraints on the
op and the loader rather than on card-author discipline. Four of them are
runtime pool filters and cannot be got wrong by a sheet
(`effects.recall_exhaust_pool` is the only pool); two are card SHAPE --
Uncommon-or-Rare, and the retrieval card Exhausts -- and shape is exactly
what a future sheet row can get wrong. `loader._validate_recall_shape`
refuses such a row at load and `gen_klee_cards.blocked_reason` refuses to
generate it; this sweeps the committed sheets so the finding arrives at
lint time instead of at the first run that happens to draft the card.

It also runs the ENGINE CLOSURE check the packet asks for -- against the
complete effect graph, not one card. The hazard the exclusions exist for is
a CYCLE: a retriever that can pull a retriever (itself included) turns the
exhaust pile from a one-way rotation into a loop, and the tier0 closure
detector (`combat._player_turn`, cards created vs consumed) only ever sees
one turn of one fight. So the pool filter is run over every card in the
loader index, with a synthetic retriever standing in for the card no sheet
ships yet, and the pool is asserted to exclude every retriever, every kit
card, every Status and every Curse. The denominator is printed: a sweep
that compared nothing must not read like a clean one
(`lint_strict_domination`'s rule).

The last section pins the C# leg structurally, the way
`lint_constant_parity` pins the mirrored constants: the mod's own predicate
must name all three exclusions and place the card on TOP of the DRAW pile.
Both engines, one law.

Run: python tools/lint_recall_exhaust.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tier0.content import loader                        # noqa: E402
from tier0.engine import effects                        # noqa: E402
from tier0.engine.state import Card, CombatState, Player  # noqa: E402
from tools import effect_walk                           # noqa: E402

# Every sheet a card row can live on -- personal pools, companion pools and
# the token/ancient side sheets. The loader reads a subset of these; the
# codegen reads a different subset; a shape law that only checked one of the
# two would be the scope defect G1 found (see tier0/tests/test_sheet_lints).
SHEETS = tuple(sorted((REPO / "docs").glob("*-cards.yaml"))) + tuple(
    sorted((REPO / "docs").glob("*-companions.yaml")))

ALLOWED_RARITIES = ("uncommon", "rare")


def _rows(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if isinstance(data, dict):
        data = data.get("cards", data.get("companions", []))
    return [r for r in (data or []) if isinstance(r, dict)]


def _retrieval_rows(row: dict) -> list[dict]:
    """The row's exhaust-retrieval effect lines, branches included."""
    return [fx for fx in effect_walk.iter_effects(row)
            if fx.get("op") == "recall_to_draw"
            and fx.get("from") == effects.RECALL_EXHAUST_SOURCE]


def _sheet_shapes() -> tuple[list[str], int, int]:
    """Constraints 1 and 2 over every committed row."""
    out: list[str] = []
    rows = retrievers = 0
    for sheet in SHEETS:
        rel = sheet.relative_to(REPO).as_posix()
        for row in _rows(sheet):
            rows += 1
            if not _retrieval_rows(row):
                continue
            retrievers += 1
            cid = row.get("id", "<unnamed>")
            if row.get("rarity") not in ALLOWED_RARITIES:
                out.append(
                    f"RARITY: {rel} row {cid!r} retrieves from the exhaust "
                    f"pile at rarity {row.get('rarity')!r}. EB-118 §6.4 "
                    f"constraint 1 is Uncommon or Rare -- a Common retriever "
                    f"is the version of this capability the packet refuses.")
            if not row.get("exhaust"):
                out.append(
                    f"NOT SELF-EXHAUSTING: {rel} row {cid!r} retrieves from "
                    f"the exhaust pile without `exhaust: true`. EB-118 §6.4 "
                    f"constraint 2: the retrieval card is half the price, and "
                    f"a repeatable retriever is a different card.")
            for fx in _retrieval_rows(row):
                if fx.get("position", "top") != "top":
                    out.append(
                        f"PLACEMENT: {rel} row {cid!r} asks for position "
                        f"{fx.get('position')!r}. Constraint 4 is top of the "
                        f"draw pile, and there is no other destination -- "
                        f"never the hand.")
    return out, rows, retrievers


def _closure() -> tuple[list[str], int]:
    """ENGINE CLOSURE, over the complete effect graph.

    Every card the loader indexes is put in one exhaust pile together with a
    synthetic retriever (no sheet ships one yet, and a sweep that ran only
    over shipped rows would be vacuous by construction), and the op's own
    pool filter is asked what it can see. The exclusions are the closure
    argument: nothing that retrieves -- including the retrieving card itself
    -- may be retrievable, or the pile stops being a one-way rotation.
    """
    out: list[str] = []
    index = loader._card_index()
    retriever = Card.from_dict({
        "id": "__closure_probe_retriever", "name": "Closure Probe",
        "cost": 1, "type": "skill", "rarity": "rare", "exhaust": True,
        "effects": [{"op": "recall_to_draw", "from": "exhaust"}],
    })
    state = CombatState(player=Player(hp=1, max_hp=1), enemies=[],
                        rng=random.Random(0))
    state.player.exhaust_pile = list(index.values()) + [retriever]

    pool = effects.recall_exhaust_pool(state, retriever)
    ids = {c.id for c in pool}
    for c in state.player.exhaust_pile:
        eligible = c.id in ids
        if effects.retrieves_from_exhaust(c) and eligible:
            out.append(
                f"CLOSURE: {c.id!r} retrieves from the exhaust pile and is "
                f"itself retrievable. The cycle exclusion (constraint 3) is "
                f"not holding.")
        if c.is_junk and eligible:
            out.append(
                f"JUNK: {c.id!r} is a {c.rarity} and is retrievable "
                f"(constraint 6 / the C11 rotation law).")
        if c.kit_card and eligible:
            out.append(
                f"KIT: {c.id!r} is a kit card and is retrievable. The Burst "
                f"never enters a pile as loot (the v1.9 invariant).")
    if retriever.id in ids:
        out.append(
            "SELF: the retrieving card can retrieve itself. Constraint 3 "
            "covers the card's own instance, which by the time the pool is "
            "read has Exhausted into the pile it is reading.")
    if not pool:
        out.append(
            "VACUOUS: the closure sweep found NO eligible card in an exhaust "
            "pile holding the whole card index. The filter is excluding "
            "everything, which is not what the exclusions say.")
    return out, len(state.player.exhaust_pile)


# The three clauses the mod's predicate must name, and the placement it must
# use. Structural, in `lint_constant_parity`'s shape: a live CombatState is
# outside the headless C# boundary (klee-mod/KleeTests/README.md), so the
# pin is on the source of the one function both engines route through.
CS_FILE = "klee-mod/KleeCode/Powers/RecallFromExhaust.cs"
CS_REQUIRED = {
    "KitGrant.NotKitCard": "the kit exemption (v1.9)",
    "KokomiResources.IsJunk": "constraint 6, the C11 junk predicate",
    "IExhaustRetriever": "constraint 3, the retriever exclusion",
    "CardPilePosition.Top": "constraint 4, top of the pile",
    "PileType.Draw": "constraint 4, the DRAW pile and never the hand",
    "CardKeyword.Exhaust": "constraint 5, the gained keyword",
}


def _cs_parity() -> list[str]:
    out: list[str] = []
    path = REPO / CS_FILE
    if not path.exists():
        return [f"MISSING C# LEG: {CS_FILE} does not exist. The exhaust "
                f"source is sim-only, which is the divergence shape the "
                f"parity discipline exists to prevent."]
    text = path.read_text(encoding="utf-8")
    for needle, why in sorted(CS_REQUIRED.items()):
        if needle not in text:
            out.append(
                f"C# LEG: {CS_FILE} never names {needle!r} -- {why}. The "
                f"sim's twin is effects.recall_exhaust_pool / "
                f"_op_recall_to_draw.")
    if "PileType.Hand" in text:
        out.append(
            f"C# LEG: {CS_FILE} names PileType.Hand. Constraint 4 is "
            f"top-of-draw, and the hand is the destination the packet "
            f"explicitly refuses.")
    return out


def findings() -> tuple[list[str], int, int, int]:
    shape, rows, retrievers = _sheet_shapes()
    closure, swept = _closure()
    return shape + closure + _cs_parity(), rows, retrievers, swept


def main() -> int:
    bad, rows, retrievers, swept = findings()
    for line in bad:
        print(line)
    print(f"scope: {rows} sheet row(s) in {len(SHEETS)} sheet(s), "
          f"{retrievers} of them retrieving from the exhaust pile; "
          f"ENGINE CLOSURE swept {swept} card(s) (the whole loader index "
          f"plus a synthetic retriever).")
    if bad:
        print(f"\n{len(bad)} finding(s). EB-118 §6.4: six constraints, "
              f"enforced by the op, the loader and the generator -- never by "
              f"card-author discipline.")
        return 1
    print("recall/exhaust OK: shape law clean on both sheets and C# leg, "
          "and no retriever, kit card or junk card is reachable from the "
          "exhaust pool.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
