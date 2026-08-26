#!/usr/bin/env python3
"""Every `<id> + upgrades.SUFFIX` site declares how it survives an ENCHANTED id.

WHY THIS EXISTS (EB-109). Appending the upgrade suffix to an id string is the
repo's one upgrade path, and it was written when an id was `x` or `x+` and
nothing else. `RUNTEMPLATE` 10 put a second decoration on the same string: an
enchantment rides a deck-list id as `x@sharp-2`, and the upgrade suffix goes
INSIDE the decoration (`x@sharp-2+`), which is the one spelling
`enchantments.split` round-trips. So `id + SUFFIX` is now a lookup whose
correctness depends on what the id already carries:

    x                -> x+                 fine
    x@sharp-2        -> x@sharp-2+         fine, and keeps the enchantment
    x+               -> x++                KeyError (no such base id)
    x@sharp-2+       -> x@sharp-2++        ValueError: int('2+')

The last row is the one that killed a run. `refpowers._upgraded` used the
`x++` MISS as its already-upgraded detector; the enchanted spelling throws
before the index is consulted, and every Ironclad run that enchanted an
upgraded attack crashed instead of scoring.

THE SEAM IS STRUCTURALLY INVISIBLE, which is why this is a lint and not four
audited call sites. An enchanted card was UNREACHABLE until `RUNTEMPLATE` 10:
every one of these sites was written correct, stayed correct through years of
review, and became wrong without being edited. Nothing about reading one of
them tells you which of the four rows above can reach it -- that answer lives
in the CALL CHAIN, three or four frames up, in whether the id came off a sheet
or off a run deck. The house pattern for a defect a reader cannot see is a
curated list plus a lint that refuses to let the list go stale (`STATE`'s
"structurally invisible defects"), and that is what this is: the reachability
answer is recorded ONCE, beside the site, and a NEW append site that nobody
has answered for fails the run.

WHAT A ROW CLAIMS, and what is checked mechanically:

  reach   "sheet"  -- the left operand cannot be an enchanted id, because it
                      is an id read off a card sheet, an effect dict, a roster
                      constant or a generation pool. Marks are attached only
                      by `enchantments.decorate`, and only onto a RUN DECK
                      list, so a sheet id never carries one.
          "deck"   -- the left operand CAN be an enchanted id: it comes from a
                      run's `deck_ids` or from a live `Card` instance built
                      from one (`loader._card_prototype` sets `card.id` to the
                      decorated id, mark and all).

  guard   how the site survives the two throwing rows above. Each kind is
          verified in the AST, not taken on trust:

          "has_upgrade"  the enclosing function calls `upgrades.has_upgrade`,
                         which splits the mark off and refuses an id that
                         already ends in SUFFIX -- so both throwing rows are
                         filtered out before the append.
          "split"        the enclosing function calls `enchantments.split`,
                         i.e. it normalises the id itself rather than trusting
                         the string.
          "degrade"      the append sits inside a `try` whose handler names
                         ValueError, so a throw becomes a logged
                         UNIMPLEMENTED and the base card, never a dead run.
          "guard_in:<f>" the filtering happens in a named sibling function
                         that this one calls, and `<f>` itself uses
                         has_upgrade.
          "not_an_id"    the left operand is not an id at all (a display
                         name), so no decoration can ride it.

A site whose key is absent from SITES is a finding. A SITES row that matches
no site is a finding too -- a stale row is a claim about code that no longer
exists, which is worse than no row.

THE KEY IS DELIBERATELY LINE-FREE: `<path>::<function>::<expression>`, with a
count for the functions that hold more than one. Line numbers drift on every
edit above them, and a registry keyed on drifting numbers is a registry people
learn to re-baseline without reading.

Run: python tools/lint_upgrade_suffix_appends.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The packages whose code RUNS a simulation. `tools/` and every `tests/` tree
# are out: a tool builds ids for a gallery or a fixture and never resolves one
# against a live run deck, and a test that wants a bad id wants it on purpose.
PACKAGES = ("tier0", "tier05")


def _site(path: str, func: str, expr: str, reach: str, guard: str,
          evidence: str, count: int = 1) -> tuple[tuple[str, str, str], dict]:
    return (path, func, expr), {
        "reach": reach, "guard": guard, "evidence": evidence, "count": count}


SITES: dict[tuple[str, str, str], dict] = dict((
    # -- tier0/content ----------------------------------------------------
    _site("tier0/content/upgrades.py", "apply_upgrade", "base_id + SUFFIX",
          "deck", "split",
          "THE site that handles the decorated spelling, and the reason the "
          "others can be simple. `base_id` is `enchantments.split(card.id)[0]` "
          "-- mark already stripped, upgrade suffix retained -- and the mark "
          "is re-attached afterwards through `enchantments.decorate`, which "
          "is the one spelling `split` round-trips. Rebuilding it by hand "
          "here is how the two decorations drift apart."),
    _site("tier0/content/upgrades.py", "apply_upgrade", "card.name + SUFFIX",
          "sheet", "not_an_id",
          "A DISPLAY NAME, not an id: `Strike` becomes `Strike+`. Enchantment "
          "marks ride ids only; the enchanted card's name is decorated "
          "separately by `_card_prototype` as `Name (Sharp)`."),

    # -- tier0/engine -----------------------------------------------------
    _site("tier0/engine/effects.py", "_generate", "pick.id + upgrades.SUFFIX",
          "sheet", "has_upgrade",
          "Stoke+. `pick` is a deepcopy of `state.rng.choice(pool)` where "
          "pool is `_generation_pool` -> `get_pool(character_id)` / "
          "`cards_in_pool`: card-sheet prototypes, whose ids are "
          "`_card_index()` keys and carry no mark. A generation pool is never "
          "a run deck, so the deck-only decoration cannot arrive here. The "
          "`has_upgrade(pick.id)` guard covers the already-upgraded row too."),
    _site("tier0/engine/effects.py", "_op_add_card", "cid + upgrades.SUFFIX",
          "sheet", "degrade",
          "HiddenDaggers+ / StormOfSteel+ (`created_upgraded`). `cid` is "
          "either `fx['card_id'] or fx['card']` -- a literal id PRINTED on "
          "the card's own effect dict -- or a member of "
          "`loader.cards_in_pool(fx['pool'])` (Secret Stash). Both are sheet "
          "ids read off committed YAML; a deck-list id never reaches this op, "
          "so no mark can arrive. The existing try/except is the belt."),
    _site("tier0/engine/effects.py", "_op_autoplay_from_exhaust",
          "victim.id + upgrades.SUFFIX",
          "deck", "degrade",
          "KnifeTrap+ (`autoplay_upgrade_first`). THE ONE REACHABLE SITE OF "
          "THE THREE: `victims` are live instances taken from "
          "`p.exhaust_pile`, i.e. real deck cards, and `_card_prototype` sets "
          "`card.id` to the decorated id -- so an enchanted card that has "
          "been exhausted arrives here with its mark on. Measured, not "
          "assumed: `x@sharp-2` + SUFFIX resolves to `x@sharp-2+` and KEEPS "
          "the rider (the correct outcome), and `x@sharp-2+` + SUFFIX raises "
          "the `int('2+')` ValueError, which this site's existing "
          "`except (KeyError, ValueError)` catches -- it emits UNIMPLEMENTED "
          "and plays the victim as it stands, which is what an "
          "already-upgraded card should do and is exactly what the "
          "undecorated `x++` KeyError already did. It does not crash and "
          "there is no behaviour to change."),
    _site("tier0/engine/refpowers.py", "_upgraded", "card.id + upgrades.SUFFIX",
          "deck", "split",
          "Aggression's discard-pile recall, and one of the two sites the "
          "RT11 re-baseline FIXED: it detected already-upgraded by the `x++` "
          "index miss, which the enchanted spelling throws before ever "
          "reaching. It now pre-splits and returns early, so the decorated "
          "and undecorated shapes are covered by one check."),

    # -- tier05 run layer -------------------------------------------------
    _site("tier05/events.py", "resolve", "ancient + upgrades.SUFFIX",
          "sheet", "not_an_id",
          "Dusty Tome. `ancient` is `roster.ANCIENTS[st.character]`, a "
          "constant sheet id being granted to the deck for the FIRST time -- "
          "it is not yet a deck-list entry, so nothing has decorated it and "
          "the Ancient sheet ships every one of them with a `+` row."),
    _site("tier05/events.py", "resolve", "c.id + upgrades.SUFFIX",
          "deck", "has_upgrade",
          "Two sites in one function -- the targeted upgrade (`opt['upgrade']`, "
          "over `st.deck_ids`) and the upgraded card-reward screen "
          "(`opt['upgraded']`, over rolled offers). Both filter their "
          "candidates through `upgrades.has_upgrade(c.id)` first, which "
          "splits the mark off and refuses an id already ending in SUFFIX.",
          2),
    _site("tier05/events.py", "resolve", "st.deck_ids[i] + upgrades.SUFFIX",
          "deck", "has_upgrade",
          "`upgrade_random`. The candidate indices are built by the "
          "comprehension immediately above it, filtered on "
          "`upgrades.has_upgrade(cid)` over the run's own deck ids -- the "
          "enchant-aware predicate, applied to the decorated string."),
    _site("tier05/model.py", "resolve_rest", "target + upgrades.SUFFIX",
          "deck", "guard_in:rest_action",
          "Rest-site smithing (M7). `target` is the second half of "
          "`rest_action`'s return, and `rest_action` only ever names a card "
          "it drew from `upgrades.has_upgrade(c.id)`-filtered candidates. The "
          "policy and its application are deliberately separate functions -- "
          "the policy is what the drafter tests -- so the guard is checked "
          "where it lives rather than duplicated here."),
    _site("tier05/relics.py", "_pickup_upgrade",
          "deck_ids[idx] + upgrades.SUFFIX",
          "deck", "has_upgrade",
          "Whetstone / War Paint. Candidate indices are collected in the loop "
          "above under `if not upgrades.has_upgrade(cid): continue`, so an "
          "already-upgraded or unupgradable id is never an index here."),
    _site("tier05/relics.py", "_fishing_upgrade",
          "deck_ids[idx] + upgrades.SUFFIX",
          "deck", "has_upgrade",
          "Fishing rewards. Same shape as `_pickup_upgrade`: the candidate "
          "comprehension is `upgrades.has_upgrade(cid)` over the run deck."),

    # -- tier05 experiment scripts ----------------------------------------
    _site("tier05/exp_eb17p_forced_copy.py", "_family",
          "cid + upgrades.SUFFIX",
          "sheet", "not_an_id",
          "The forced-copy family for one SWEPT card id -- a module-level "
          "constant naming a sheet row, built before any run exists. It is "
          "used as a MEMBERSHIP TEST against a run's deck ids, never resolved "
          "through the loader, so a mark it does not carry cannot break it."),
    _site("tier05/exp_eb17p_forced_copy.py", "compliance",
          "cid + upgrades.SUFFIX",
          "sheet", "not_an_id",
          "The end-of-run census: `sum(cid + SUFFIX in t.deck_ids ...)`. Same "
          "constant, same membership test, no loader lookup. An enchanted "
          "copy of a swept card would not be counted as upgraded here, which "
          "is a KNOWN limit of the census rather than a crash -- and the "
          "sweep's arms force plain ids, so no run can produce one."),
))


def _is_suffix(node: ast.AST) -> bool:
    return ((isinstance(node, ast.Attribute) and node.attr == "SUFFIX")
            or (isinstance(node, ast.Name) and node.id == "SUFFIX"))


def _scan(path: Path) -> list[dict]:
    """Every `<x> + SUFFIX` in one file, with the context a claim needs."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def ancestors(node: ast.AST):
        while node in parents:
            node = parents[node]
            yield node

    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
                and _is_suffix(node.right)):
            continue
        func = next((a for a in ancestors(node)
                     if isinstance(a, (ast.FunctionDef, ast.AsyncFunctionDef))),
                    None)
        tries = [a for a in ancestors(node) if isinstance(a, ast.Try)]
        out.append({
            "path": path.relative_to(REPO).as_posix(),
            "func": func.name if func else "<module>",
            "expr": ast.unparse(node),
            "line": node.lineno,
            "calls": _calls(func) if func else set(),
            "module_funcs": {n.name: _calls(n) for n in ast.walk(tree)
                             if isinstance(n, ast.FunctionDef)},
            "catches_value_error": any(_catches(t) for t in tries),
        })
    return out


def _calls(node: ast.AST) -> set[str]:
    return {ast.unparse(n.func) for n in ast.walk(node)
            if isinstance(n, ast.Call)}


def _catches(node: ast.Try) -> bool:
    for handler in node.handlers:
        named = handler.type
        parts = (named.elts if isinstance(named, ast.Tuple)
                 else [named] if named is not None else [])
        if any(ast.unparse(p) == "ValueError" for p in parts):
            return True
    return False


def _guard_ok(row: dict, found: dict) -> str | None:
    """None if the declared guard is really there; else why not."""
    guard = row["guard"]
    calls = found["calls"]
    if guard == "has_upgrade":
        if not calls & {"upgrades.has_upgrade", "has_upgrade"}:
            return ("declares guard 'has_upgrade' but its enclosing function "
                    "calls no has_upgrade")
    elif guard == "split":
        if not calls & {"enchantments.split", "split"}:
            return ("declares guard 'split' but its enclosing function calls "
                    "no enchantments.split")
    elif guard == "degrade":
        if not found["catches_value_error"]:
            return ("declares guard 'degrade' but the append is not inside a "
                    "try whose handler names ValueError -- the enchanted "
                    "already-upgraded id raises exactly that")
    elif guard.startswith("guard_in:"):
        sibling = guard.split(":", 1)[1]
        if sibling not in calls:
            return (f"declares guard 'guard_in:{sibling}' but its enclosing "
                    f"function does not call {sibling}")
        sib_calls = found["module_funcs"].get(sibling)
        if sib_calls is None:
            return f"names guard function {sibling!r}, which this module lacks"
        if not sib_calls & {"upgrades.has_upgrade", "has_upgrade"}:
            return (f"names guard function {sibling!r}, which itself calls no "
                    f"has_upgrade")
    elif guard != "not_an_id":
        return f"unknown guard kind {guard!r}"
    return None


def findings() -> list[str]:
    out: list[str] = []
    found: dict[tuple[str, str, str], list[dict]] = {}
    for pkg in PACKAGES:
        for path in sorted((REPO / pkg).rglob("*.py")):
            if "tests" in path.relative_to(REPO).parts:
                continue
            for hit in _scan(path):
                found.setdefault((hit["path"], hit["func"], hit["expr"]),
                                 []).append(hit)

    for key in sorted(found):
        hits = found[key]
        row = SITES.get(key)
        if row is None:
            out.append(
                f"UNDECLARED APPEND SITE {key[0]}:{hits[0]['line']} "
                f"({key[1]}, `{key[2]}`): a new `+ SUFFIX` site with no "
                f"reachability answer. Add a row to "
                f"tools/lint_upgrade_suffix_appends.SITES saying whether the "
                f"left operand can be a DECK id (which may carry an "
                f"enchantment mark) or only a SHEET id, and how the site "
                f"survives `x+`/`x@sharp-2+` -- EB-109.")
            continue
        if len(hits) != row["count"]:
            out.append(
                f"COUNT DRIFT at {key[0]} ({key[1]}, `{key[2]}`): the row "
                f"claims {row['count']} site(s), the file has {len(hits)} "
                f"(lines {', '.join(str(h['line']) for h in hits)}). A row "
                f"that answers for fewer sites than exist leaves the new one "
                f"unanswered while looking covered.")
        if row["reach"] not in ("sheet", "deck"):
            out.append(f"{key}: unknown reach {row['reach']!r}")
        if len(row["evidence"].split()) < 15:
            out.append(
                f"THIN EVIDENCE at {key[0]} ({key[1]}): a reachability answer "
                f"is a claim about a CALL CHAIN and has to name it. The whole "
                f"failure mode here is a site that reads correct locally.")
        why = _guard_ok(row, hits[0])
        if why:
            out.append(f"GUARD GONE at {key[0]}:{hits[0]['line']} "
                       f"({key[1]}, `{key[2]}`): {why}.")

    for key in sorted(set(SITES) - set(found)):
        out.append(
            f"STALE ROW {key[0]} ({key[1]}, `{key[2]}`): SITES answers for an "
            f"append site that no longer exists. Delete the row -- a stale "
            f"answer is a claim about code nobody can read.")
    if not found:
        out.append(
            "NOTHING SCANNED: no `+ SUFFIX` site found in "
            f"{'/'.join(PACKAGES)}. The lint would pass vacuously.")
    return out


def main() -> int:
    bad = findings()
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    deck = sum(r["count"] for r in SITES.values() if r["reach"] == "deck")
    total = sum(r["count"] for r in SITES.values())
    print(f"upgrade-suffix appends OK: {total} site(s) across "
          f"{len(PACKAGES)} package(s), {deck} of them reachable with an "
          f"enchanted deck id, every one declaring how it survives one")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
