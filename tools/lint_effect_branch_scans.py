#!/usr/bin/env python3
"""L4: nothing may read a card's `effects` as a flat list by accident.

A card row's `effects` is a tree -- `conditional` hangs `then:` and `else:`
lists off itself -- so a hand-rolled `for eff in card["effects"]` loop
silently answers its question about the TOP LEVEL only. Three unrelated
tools had done exactly that (S1 parity sweep, finding L4; the incident
record reads at
`git show pre-simplification-2026-08-06:review/parity-sweep/triage-memo.md`),
and fixing the call sites would not have closed the class -- the fourth
author writes the fourth flat loop. So this gate has two halves, and they
fail in opposite directions on purpose.

SOURCE half -- no scanner iterates the field raw
------------------------------------------------
Every `for ... in <row>["effects"]` / `<row>.get("effects")` in `tools/`
must either go through `tools/effect_walk.py` or be REGISTERED in
`TOP_LEVEL_ONLY` with the reason it is deliberately flat. A deliberate flat
read is legitimate -- gated value is not unconditional value, and
`lint_strict_domination` would call a conditional card dominant without
that distinction -- but it has to be a decision on the record, not a loop
that looks like every other loop.

Both directions: a registered site that no longer iterates the field raw is
ALSO a finding, so an entry cannot outlive the code it was excusing and
become cover for the next flat loop in the same function.

`gen_klee_cards.py` is excluded, in `EXEMPT_MODULES`, with its reason: it is
an emitter, its forty reads are positional (`card["effects"].index(eff)`,
one statement emitted per effect), and whether a given one should recurse is
a codegen question per call site rather than a scan to deepen. Its
whole-card questions ("does this card carry Bomb rules") go through
`effect_walk` anyway, via its own `_effects_everywhere`.

DATA half -- no card hides printed rules in a branch unnoticed
--------------------------------------------------------------
The source half can only guard the tools this repo has. The other side of
the same defect is a CARD that puts a rules-bearing op (one that makes a
card carry keyword text or a structural marker) somewhere a flat scanner
cannot see it. Those cards are enumerated in `BRANCH_ONLY_KNOWN`, one entry
per card, each naming what it hides and what was done about it.

A card that starts hiding such an op fails here; an entry whose card stopped
hiding it fails too.

Run:  python tools/lint_effect_branch_scans.py
Exit 0 clean; exit 1 with one finding per line.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.effect_walk import iter_effects, iter_effects_top  # noqa: E402

TOOLS = REPO / "tools"
DOCS = REPO / "docs"

# The sheets whose rows this lint reads. Card sheets only: an upgrades sheet
# carries deltas, not effects.
SHEETS = ("klee-cards.yaml", "furina-cards.yaml", "kokomi-cards.yaml",
          "mondstadt-companions.yaml", "fontaine-companions.yaml",
          "inazuma-companions.yaml")

EXEMPT_MODULES = {
    "gen_klee_cards.py": (
        "EMITTER, not a scanner. Its ~40 reads of the field are positional --"
        " one C# statement emitted per effect, indices taken with"
        " `card['effects'].index(eff)` -- so 'recurse' is a per-call-site"
        " codegen decision (what would a branch statement even be emitted"
        " INTO?) rather than a scan to deepen. The reads that ask a"
        " WHOLE-CARD question route through its `_effects_everywhere`, which"
        " is `effect_walk.iter_effects` -- `includes_bomb_rules` was the last"
        " one that did not (the L4 incident). The remaining branch-blind"
        " read is `aura_elements`/`preview_element_cs`, still announced by"
        " `apply_aura`/`swirl` in RULES_BEARING_OPS if a card ever hides"
        " one."),
    "effect_walk.py": (
        "the shared walk itself; `iter_effects_top` is the flat read by"
        " definition."),
    "lint_effect_branch_scans.py": "this gate.",
}

# {"module.py::function": why it is deliberately top-level-only}
#
# One line each, and the line has to say what would go WRONG if the site
# recursed -- "it doesn't need to" is not a reason, it is a shrug.
TOP_LEVEL_ONLY: dict[str, str] = {
    "extract_base_game_pool.py::_row_delta_key": (
        "`top_damage`/`top_block` ask whether the DLL's DynamicVar belongs to"
        " the card's PRINTED body, which is a top-level question by"
        " construction -- and the extractor refuses any card whose OnPlay"
        " branches on runtime state (_Untranslatable 'behaviour branches on"
        " runtime state'), so a translated row cannot contain a conditional"
        " at all."),
    "lint_constant_parity.py::_ancient_hook": (
        "reads an ANCIENT RELIC's effect list, not a card row. The relic DSL"
        " has no `conditional` op -- a relic hook is a flat list of effects"
        " by grammar -- so there is no tree here to walk."),
    "lint_strict_domination.py::effect_maps": (
        "gated value is not unconditional value. Folding a `then:` branch"
        " into the benefit map would let a card that MIGHT deal 20 dominate"
        " one that always deals 18, which inverts the whole comparison. The"
        " conditional is kept as one opaque key so the branch still"
        " distinguishes two cards without being credited to either."),
}

# Ops that make a card carry PRINTED RULES -- keyword text, a tooltip, or a
# structural marker some tool has to emit. Each name is here because a flat
# scan in this repo reads it; the comment says which one.
RULES_BEARING_OPS: dict[str, str] = {
    # The five Bomb ops LEFT this table when the L4 incident was fixed: their
    # only two flat readers -- `gen_klee_cards.emit`'s `includes_bomb_rules`
    # and `lint_handwritten_parity`'s `exp_bomb_tips` -- both walk the whole
    # tree now, so a branch-nested Bomb op is no longer a miss to announce.
    # (The emitter's `target_type` loop still reads `place_bomb`/`detonate`/
    # `move_bombs` positionally, but that loop asks "which effect aims this
    # card FIRST" -- an ordering question about the printed body, not a
    # rules-text scan, and it is covered by the EXEMPT_MODULES entry.)
    # gen_klee_cards.emit `aura_elements` / `preview_element_cs`. Both flat.
    "apply_aura": "element keyword + reaction preview",
    "swirl": "element keyword + reaction preview",
    # lint_generated_structure MECHANICS rows (now branch-aware; listed so a
    # branch-nested one is still announced rather than merely tolerated).
    "raise_fanfare_cap": "Fanfare keyword marker",
    "gain_fanfare_floor": "Fanfare keyword marker",
    "crash_fanfare": "Fanfare price marker",
    # Every power tooltip is keyed off the applied power's name.
    "apply_power": "power tooltip",
}

# {card id: (branch-only rules-bearing ops, what was done about it)}
#
# EMPTY IS THE HEALTHY STATE, not a disabled gate: the DATA half below still
# reads every row of every sheet, and the first card to hide a rules-bearing
# op in a branch fails until someone proves the readers see it. The one entry
# this dict ever held was `sparkly_explosion` -- THE L4 INCIDENT ITSELF, whose
# kill-conditional `then:` places 2 Bombs at 6 while the shipped card said
# `includesBombRules: false` -- retired when the generator and the parity gate
# both learned to walk the tree and the C# was regenerated.
BRANCH_ONLY_KNOWN: dict[str, tuple[tuple[str, ...], str]] = {}


# ---------------------------------------------------------------------------
# SOURCE half
# ---------------------------------------------------------------------------

def _is_effects_field_read(node: ast.AST) -> bool:
    """`x["effects"]` or `x.get("effects", ...)` -- the field, off a row.

    Deliberately NOT "any name called effects": passing the field to a
    recursive walker is the correct pattern, and a local already holding a
    walked list is not a raw read. The rule is about ITERATING the field.
    """
    if isinstance(node, ast.Subscript):
        key = node.slice
        return isinstance(key, ast.Constant) and key.value == "effects"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == "get" and node.func.value is not None:
            args = node.args
            return bool(args) and isinstance(args[0], ast.Constant) \
                and args[0].value == "effects"
    if isinstance(node, ast.BoolOp):
        return any(_is_effects_field_read(v) for v in node.values)
    return False


def raw_scan_sites() -> dict[str, list[int]]:
    """{"module.py::function": [line, ...]} for every raw iteration."""
    sites: dict[str, list[int]] = {}
    for path in sorted(TOOLS.glob("*.py")):
        if path.name in EXEMPT_MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        funcs = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        def owner(lineno: int) -> str:
            best = None
            for f in funcs:
                if f.lineno <= lineno <= (f.end_lineno or f.lineno):
                    if best is None or f.lineno > best.lineno:
                        best = f
            return best.name if best else "<module>"

        for node in ast.walk(tree):
            it = node.iter if isinstance(node, (ast.For, ast.comprehension)) \
                else None
            if it is not None and _is_effects_field_read(it):
                sites.setdefault(f"{path.name}::{owner(it.lineno)}",
                                 []).append(it.lineno)
    return sites


def source_findings() -> tuple[list[str], int]:
    sites = raw_scan_sites()
    findings = []
    for key, lines in sorted(sites.items()):
        if key not in TOP_LEVEL_ONLY:
            findings.append(
                f"FLAT EFFECT SCAN {key} (line(s) {lines}): iterates the"
                " `effects` field directly, so a `conditional`'s then/else"
                " contents are invisible to it. Walk it with"
                " tools/effect_walk.iter_effects, or register the site in"
                " TOP_LEVEL_ONLY with the reason recursing would be wrong.")
    for key in sorted(TOP_LEVEL_ONLY):
        if key not in sites:
            findings.append(
                f"STALE TOP_LEVEL_ONLY ENTRY {key}: no raw `effects`"
                " iteration there any more. Delete the entry -- left in"
                " place it silently excuses the next flat loop written in"
                " that function.")
    return findings, len(sites)


# ---------------------------------------------------------------------------
# DATA half
# ---------------------------------------------------------------------------

def _rows(path: Path) -> list[dict]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if isinstance(loaded, dict):
        loaded = loaded.get("cards", [])
    return [r for r in loaded if isinstance(r, dict) and r.get("effects")]


def branch_only_ops(row: dict) -> set[str]:
    """Ops that appear ONLY inside a conditional branch on this card."""
    top = {fx.get("op") for fx in iter_effects_top(row.get("effects"))}
    every = {fx.get("op") for fx in iter_effects(row.get("effects"))}
    return {op for op in every - top if op}


def data_findings() -> tuple[list[str], dict[str, int]]:
    findings: list[str] = []
    census = {"rows": 0, "branched": 0, "rules_bearing": 0}
    seen: set[str] = set()
    for name in SHEETS:
        for row in _rows(DOCS / name):
            census["rows"] += 1
            hidden = branch_only_ops(row)
            if not hidden:
                continue
            census["branched"] += 1
            risky = tuple(sorted(hidden & set(RULES_BEARING_OPS)))
            if not risky:
                continue
            census["rules_bearing"] += 1
            card_id = row["id"]
            seen.add(card_id)
            known = BRANCH_ONLY_KNOWN.get(card_id)
            if known is None:
                findings.append(
                    f"BRANCH-HIDDEN RULES {name}: {card_id} hides"
                    f" {list(risky)} inside a conditional branch"
                    f" ({', '.join(RULES_BEARING_OPS[op] for op in risky)})."
                    " Every flat scanner keyed on those ops will report this"
                    " card as not having them. Prove the readers are"
                    " branch-aware, then register the card in"
                    " BRANCH_ONLY_KNOWN with what you checked.")
            elif known[0] != risky:
                findings.append(
                    f"BRANCH_ONLY_KNOWN {card_id} is registered for"
                    f" {list(known[0])} but now hides {list(risky)} --"
                    " re-check the readers and update the entry.")
    for card_id in sorted(set(BRANCH_ONLY_KNOWN) - seen):
        findings.append(
            f"STALE BRANCH_ONLY_KNOWN ENTRY {card_id}: the card no longer"
            " hides a rules-bearing op in a branch. Delete the entry.")
    return findings, census


def main() -> int:
    src, site_count = source_findings()
    data, census = data_findings()
    findings = src + data
    for f in findings:
        print(f)
    # A verdict with its denominator, per the house rule: a gate that cannot
    # say how much it looked at is the confident half of a partial check.
    print(f"scope: {site_count} registered flat scan site(s) across"
          f" {len(list(TOOLS.glob('*.py'))) - len(EXEMPT_MODULES)} tools"
          f" module(s) ({', '.join(sorted(EXEMPT_MODULES))} exempt);"
          f" {census['rows']} card row(s) read, {census['branched']} with an"
          f" op that appears ONLY in a branch, {census['rules_bearing']} of"
          " those carrying a rules-bearing op")
    print(f"{'CLEAN' if not findings else f'{len(findings)} finding(s)'}:"
          " effect-branch scans")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
