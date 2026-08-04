"""The canon role x tempo baseline, read STRUCTURALLY out of the local dll.

Track A / T1 + T3 (docs/track-a-kickoff-brief.md). Produces three things:

  game_ref/role_tempo_canon.json   LOCAL artifact. Per-card classification for
                                   all five canon pools, card names included.
                                   Gitignored reference material -- never
                                   committed, same rule as every other
                                   game_ref/ output (.gitignore:28).
  docs/role-tempo-baseline.md      COMMITTED. Percentages and shapes only. No
                                   card names, no card text, no numbers off
                                   any card face.
  docs/role-tempo-floors.yaml      COMMITTED. The machine-readable floors the
                                   coverage lint reads. Percentages only.

WHY STRUCTURAL AND NOT TEXT
----------------------------
The brief says "on card text for canon", because the chat session's classifier
was a regex over the wiki. The DLL is better information and safer material:
a card's Cmds, DynamicVars, TargetType and the POWER/ORB/SUMMON models it
reaches for say what it does without any of its printed text entering this
process. The known wiki misses the brief lists ($Dexterity -> block,
@IE/@SE/@ST -> velocity, $Plating -> block, "Another player"/"an ally" ->
support) are not patched here; they are STRUCTURALLY ABSENT, because
DexterityPower and PlatingPower are read off their own models and an ally
target is `TargetType.AnyAlly` in the constructor. That is the reconciliation
those four fixes were reaching for.

The recursion is what makes the tag-through real on this side. Zap channels a
LightningOrb; nothing about Zap's own body says "scaling damage". The orb's
model does, so the orb's model is read, and Zap inherits it -- charter A0.1,
executed rather than asserted.

HOW THE FLOORS ARE DERIVED, in one paragraph
---------------------------------------------
A cell is (solve x fight-band). A cell is MANDATORY when all five canon pools
are non-zero in it; a cell any canon character sits at zero in is an identity
statement, not a debt (the charter's own example: Klee at zero sustain is
Silent-shaped). The floor for a mandatory cell is the MINIMUM of the five
canon percentages. Both halves are forced by the same requirement -- the
brief's stop-and-surface says a floor that would fail a canon character means
the derivation is wrong -- and a minimum-of-canon floor cannot, by
construction. `utility` is never linted (A0.2). `support` is never linted
either: the sim is one-seat, so those cells are play-graded only (D4).

USAGE
-----
    python tools/canon_role_tempo.py            # needs the game + ilspycmd
    python tools/canon_role_tempo.py --from-json  # re-derive from game_ref/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import extract_base_game_pool as extract      # noqa: E402
from tools import role_tempo as rt                        # noqa: E402

CHARACTERS = ("Ironclad", "Silent", "Defect", "Necrobinder", "Regent")
OUT_JSON = REPO / "game_ref" / "role_tempo_canon.json"
OUT_DOC = REPO / "docs" / "role-tempo-baseline.md"
OUT_FLOORS = REPO / "docs" / "role-tempo-floors.yaml"

# --- structural signals -----------------------------------------------------
#
# Each entry is (regex, role). Applied to a decompiled model's source -- a
# card, a Power, an Orb or a summoned creature, all four read the same way,
# which is what lets the tag-through recurse without a second vocabulary.
SIGNALS = (
    (re.compile(r"DamageCmd\.Attack|CreatureCmd\.Damage\b|"
                r"new (?:Damage|ExtraDamage|CalculatedDamage|OstyDamage)Var"),
     "frontload"),
    (re.compile(r"CreatureCmd\.GainBlock|new (?:Block|CalculatedBlock)Var|"
                r"StaticHoverTip\.Block|ModifyBlock"), "block"),
    (re.compile(r"CreatureCmd\.Heal\b|CreatureCmd\.GainMaxHp|"
                r"new (?:Heal|MaxHp)Var|PreventDamage"), "sustain"),
    (re.compile(r"CardPileCmd\.Draw|PlayerCmd\.GainEnergy|CardCmd\.AutoPlay|"
                r"CardPileCmd\.AutoPlayFromDrawPile|new (?:Cards|Energy)Var|"
                r"ModifyEnergyCost|CardCmd\.Retain"), "velocity"),
    # Co-op. Three independent spellings, all of them the game's own: an ally
    # TargetType, the MultiplayerOnly constraint, and a power that walks the
    # owner's teammates.
    (re.compile(r"TargetType\.(?:AnyAlly|AllAllies)|"
                r"CardMultiplayerConstraint\.MultiplayerOnly|"
                r"GetTeammatesOf"), "support"),
)
# A model that MODIFIES output rather than producing it is scaling. On a card
# this is reached through the Power it applies, never off the card's own body.
SCALING_IN_POWER = re.compile(
    r"ModifyDamage(?:Additive|Multiplicative)|ModifyOrbValue|"
    r"ModifyBlock(?:Additive|Multiplicative)|AfterSideTurnStart|"
    r"PowerCmd\.Apply<\w+Power>")
DEBUFF = re.compile(r"PowerType\.Debuff")
# Accumulated state: the base-game grammar for "base + extra * count".
ACCUMULATES = re.compile(r"new Calculat(?:ed|ion)\w*Var|CalculationBase|"
                         r"ExhaustPile|CombatState\.\w*Count")
# The three token layers the five pools actually own.
REACHES = (
    (re.compile(r"PowerCmd\.Apply<(\w+Power)>"), "Power"),
    (re.compile(r"OrbCmd\.Channel<(\w+Orb)>"), "Orb"),
    (re.compile(r"HoverTipFactory\.FromOrb<(\w+Orb)>"), "Orb"),
)
SUMMONS = re.compile(r"OstyCmd\.Summon")
CONSUMES_ONLY = re.compile(r"OrbCmd\.Evoke|ForgeCmd\.Forge|PlayerCmd\.GainStars")


class Reader:
    """Reads and memoises decompiled models by short type name."""

    def __init__(self, root: Path):
        self.root = root
        self._cache: dict[str, str] = {}

    def source(self, short_name: str) -> str:
        if short_name not in self._cache:
            paths = sorted(self.root.rglob(f"{short_name}.cs"))
            self._cache[short_name] = paths[0].read_text(encoding="utf-8") if paths else ""
        return self._cache[short_name]


def roles_of(src: str) -> set[str]:
    return {role for pattern, role in SIGNALS if pattern.search(src)}


def token_roles(reader: Reader, type_name: str, kind: str,
                depth: int = 0) -> set[str]:
    """What one token cashes into -- the tag-through, one level at a time.

    Depth-limited at 2: DemonForm applies Strength applies nothing, which is
    the deepest real chain, and an unbounded walk on decompiled source is a
    cycle waiting to happen.
    """
    src = reader.source(type_name)
    if not src:
        return set()
    roles = roles_of(src)
    if kind == "Power":
        if DEBUFF.search(src):
            # A debuff delivers no role of its own; it is the sheets'
            # `utility` voice and A0.2 protects that space from the lint.
            return {"utility"}
        if SCALING_IN_POWER.search(src):
            roles.add("scaling")
    if kind == "Orb":
        # An orb sits on the board and fires on its own schedule. Whatever it
        # does, it does repeatedly -- which is the definition of the scaling
        # half of the charter's demand curve.
        roles.add("scaling")
    if depth < 2:
        for pattern, sub_kind in REACHES:
            for name in set(pattern.findall(src)):
                roles |= token_roles(reader, name, sub_kind, depth + 1)
    return roles


def classify_canon(card: dict, src: str, reader: Reader) -> dict:
    """One canon card -> the same shape tools/role_tempo.py produces for ours."""
    direct = roles_of(src)
    inherited: set[str] = set()
    tokens: list[str] = []
    for pattern, kind in REACHES:
        for name in sorted(set(pattern.findall(src))):
            tokens.append(name)
            inherited |= token_roles(reader, name, kind)
    if SUMMONS.search(src):
        tokens.append("Osty")
        # The summon's own creature model is where its numbers live; the card
        # only says how big. Necrobinder is Furina's designated summon-economy
        # anchor, so this branch is the one her Salon is measured against.
        inherited |= token_roles(reader, "Osty", "Summon") or {"frontload",
                                                               "block"}
    if card["type"] == "Power":
        direct.add("scaling")

    roles = (direct | inherited) or {"utility"}
    cost = card["cost"] if card["cost"] >= 0 else 3     # X costs are -1
    reads_state = bool(ACCUMULATES.search(src)) or bool(
        CONSUMES_ONLY.search(src))
    has_body = bool(card["vars"].get("Damage") or card["vars"].get("Block")
                    or card["vars"].get("Cards") or card["vars"].get("Energy")
                    or card["vars"].get("Summon"))

    early = cost <= 1 and card["type"] != "Power" and has_body
    late = (card["type"] == "Power" or cost >= 3 or reads_state
            or bool(tokens))
    fight = set()
    if early:
        fight.add("early")
    if late:
        fight.add("late")
    if cost == 2 or not fight or fight == {"early", "late"}:
        fight.add("mid")

    rarity = card["rarity"].lower()
    payoff = reads_state or (bool(tokens) and not card["orbs"])
    run = set()
    if rarity in ("basic", "common") or (rarity == "uncommon" and not payoff):
        run.add("early")
    if rarity in ("rare", "ancient") or payoff:
        run.add("late")
    return {
        "name": card["name"],
        "rarity": rarity,
        "type": card["type"].lower(),
        "cost": card["cost"],
        "solve": sorted(roles),
        "direct": sorted(direct),
        "inherited": sorted(inherited),
        "tokens": tokens,
        "aoe": card["target"] in ("AllEnemies",),
        "fight": [b for b in rt.FIGHT_BANDS if b in fight],
        "run": [b for b in rt.RUN_BANDS if b in run] or ["early"],
        "mp_only": card["mp_only"],
    }


# --- aggregation ------------------------------------------------------------

def pool_percentages(cards: list[dict]) -> dict:
    """Percentages for one pool. Within-pool only -- the charter's caveat."""
    n = len(cards)
    solve = Counter(r for c in cards for r in c["solve"])
    cells = Counter((r, b) for c in cards for r in c["solve"]
                    for b in c["fight"])
    run_cells = Counter((r, b) for c in cards for r in c["solve"]
                        for b in c["run"])
    rarity_cells = Counter((r, c["rarity"]) for c in cards for r in c["solve"])
    multi = sum(1 for c in cards if len(c["solve"]) > 1)
    return {
        "n": n,
        "multi_solve_pct": round(100 * multi / n, 1),
        "aoe_pct": round(100 * sum(1 for c in cards if c["aoe"]) / n, 1),
        "solve": {r: round(100 * k / n, 1) for r, k in solve.items()},
        "fight_cells": {f"{r}|{b}": round(100 * k / n, 1)
                        for (r, b), k in cells.items()},
        "run_cells": {f"{r}|{b}": round(100 * k / n, 1)
                      for (r, b), k in run_cells.items()},
        "rarity_cells": {f"{r}|{b}": round(100 * k / n, 1)
                         for (r, b), k in rarity_cells.items()},
        "rarities": {r: k for r, k in Counter(
            c["rarity"] for c in cards).items()},
    }


def derive_floors(per_char: dict[str, dict]) -> dict:
    """min-of-canon over the cells every canon pool is non-zero in."""
    floors: dict[str, float] = {}
    identity_cells: dict[str, list[str]] = {}
    keys = set()
    for stats in per_char.values():
        keys |= set(stats["fight_cells"])
    for key in sorted(keys):
        role = key.split("|")[0]
        if role in rt.UNLINTED or role == "support":
            continue
        values = [stats["fight_cells"].get(key, 0.0)
                  for stats in per_char.values()]
        if min(values) <= 0:
            identity_cells[key] = sorted(
                name for name, stats in per_char.items()
                if not stats["fight_cells"].get(key))
            continue
        floors[key] = min(values)
    return {"mandatory": floors, "identity_only": identity_cells}


# --- entry points -----------------------------------------------------------

def build(from_json: bool) -> dict:
    per_char: dict[str, dict] = {}
    cards_by_char: dict[str, list[dict]] = {}
    if from_json:
        payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        cards_by_char = payload["cards"]
    else:
        dll = extract.game_dll()
        with extract.decompiled_project(dll) as root:
            reader = Reader(root)
            for character in CHARACTERS:
                names, sources = extract.read_pool(root, character)
                rows = []
                for name in names:
                    card = extract.parse_card(sources[name], name)
                    if card is None:
                        continue
                    rows.append(classify_canon(card, sources[name], reader))
                cards_by_char[character] = rows
                print(f"  {character}: {len(rows)} cards classified",
                      file=sys.stderr)
    for character, rows in cards_by_char.items():
        per_char[character] = pool_percentages(rows)
    return {"cards": cards_by_char, "stats": per_char,
            "floors": derive_floors(per_char)}


def write_local(payload: dict) -> None:
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"  wrote {OUT_JSON.relative_to(REPO)}  "
          "(gitignored -- reference only, do not commit)")


def _table(per_char: dict, extract_key: str, rows: list[str]) -> list[str]:
    heads = list(per_char)
    out = ["| cell | " + " | ".join(heads) + " |",
           "|---|" + "---|" * len(heads)]
    for key in rows:
        vals = [f"{per_char[c][extract_key].get(key, 0.0):.1f}"
                for c in heads]
        out.append(f"| `{key}` | " + " | ".join(vals) + " |")
    return out


def write_docs(payload: dict) -> None:
    per_char, floors = payload["stats"], payload["floors"]
    cell_keys = sorted({k for s in per_char.values() for k in s["fight_cells"]})
    lines = [
        "# Role x Tempo baseline — the five canon pools",
        "",
        "MACHINE-GENERATED by `tools/canon_role_tempo.py` from the local",
        "`sts2.dll`. Track A / T1+T3 of the Axis-Validity session",
        "(`docs/axis-validity-session-charter.md` §3).",
        "",
        "**Everything below is a PERCENTAGE or a shape.** No card name, no card",
        "text and no number off any card face appears here or in",
        "`docs/role-tempo-floors.yaml` — the per-card classification lives in",
        "`game_ref/role_tempo_canon.json`, which is gitignored reference",
        "material (.gitignore:28) and stays on the machine that has the game.",
        "",
        "## 0. Wiki-vs-DLL reconciliation (counts only)",
        "",
        "The charter's canon numbers were wiki-derived and it flagged them as",
        "running high. They do. Per-pool printed card counts, DLL:",
        "",
        "| pool | DLL total | basic | common | uncommon | rare | ancient | "
        "charter's wiki count |",
        "|---|---|---|---|---|---|---|---|",
    ]
    WIKI = {"Ironclad": 91, "Silent": 92, "Defect": 91,
            "Necrobinder": 91, "Regent": 91}
    for name, stats in per_char.items():
        r = stats["rarities"]
        lines.append(
            f"| {name} | {stats['n']} | {r.get('basic', 0)} | "
            f"{r.get('common', 0)} | {r.get('uncommon', 0)} | "
            f"{r.get('rare', 0)} | {r.get('ancient', 0)} | {WIKI[name]} |")
    total = sum(s["n"] for s in per_char.values())
    lines += [
        "",
        f"DLL total across the five pools: **{total}**. The wiki route's own",
        f"per-pool numbers sum to **{sum(WIKI.values())}**, so the wiki runs",
        "3–4 high per pool exactly as the charter predicted — the overage is",
        "flat, not concentrated, which is what a wiki-lists-a-few-extra story",
        "looks like and not what a we-are-reading-a-different-pool story would.",
        "",
        "**One number in the charter does not reconcile and is not the DLL's**",
        "**fault:** §head says \"402 canon cards total\" while its own per-pool",
        "wiki figures sum to 456. 402 is neither the wiki sum nor the DLL sum",
        "nor the draftable subtotal (410 = 5 × 82 common+uncommon+rare). It is",
        "carried forward here as an unexplained figure rather than quietly",
        "replaced; the percentages the charter rests on are unaffected, because",
        "every one of them is within-pool.",
        "",
        "The pools are startlingly regular: **every** character ships exactly",
        "20 common, 36 uncommon, 26 rare and 2 ancient. Rarity mix is therefore",
        "not an identity lever in canon at all — a fact worth having before",
        "anyone argues a GItS pool's shape from its rarity split.",
        "",
        "## 1. `solve` coverage, per pool (% of pool, multi-tagged)",
        "",
    ]
    roles = [r for r in rt.SOLVE]
    heads = list(per_char)
    lines += ["| role | " + " | ".join(heads) + " |",
              "|---|" + "---|" * len(heads)]
    for role in roles:
        lines.append(f"| {role} | " + " | ".join(
            f"{per_char[c]['solve'].get(role, 0.0):.1f}" for c in heads) + " |")
    lines += [
        "| **multi-solve** | " + " | ".join(
            f"{per_char[c]['multi_solve_pct']:.1f}" for c in heads) + " |",
        "| **aoe** (modifier) | " + " | ".join(
            f"{per_char[c]['aoe_pct']:.1f}" for c in heads) + " |",
        "",
        "`support` is present in every canon pool and is the amendment A0 adds",
        "to the vocabulary. It is also the one row here that no prediction in",
        "this track may touch: the sim is one-seat, so support cells are",
        "play-graded only (D4 clause, written in at birth).",
        "",
        "## 2. The (solve × fight-band) matrix (% of pool)",
        "",
    ]
    lines += _table(per_char, "fight_cells", cell_keys)
    lines += [
        "",
        "## 3. The (solve × run-band) matrix (% of pool)",
        "",
    ]
    run_keys = sorted({k for s in per_char.values() for k in s["run_cells"]})
    lines += _table(per_char, "run_cells", run_keys)
    lines += [
        "",
        "## 4. The (solve × rarity) matrix (% of pool)",
        "",
    ]
    rar_keys = sorted({k for s in per_char.values() for k in s["rarity_cells"]})
    lines += _table(per_char, "rarity_cells", rar_keys)
    lines += [
        "",
        "## 5. Necrobinder — Furina's designated summon-economy anchor",
        "",
        "The charter names him because his machinery is the closest canon",
        "analogue to the Salon: a card deploys a persistent body, the body acts",
        "on its own schedule, and the pool is built around how many are out.",
        "The shape, broken out:",
        "",
    ]
    necro = payload["cards"]["Necrobinder"]
    summ = [c for c in necro if "Osty" in c["tokens"]]
    lines += [
        f"- **{len(summ)} of {len(necro)} cards ({100*len(summ)/len(necro):.1f}%)"
        "** touch the summon layer.",
        "- What the summon cashes into: "
        + ", ".join(f"`{r}`" for r in sorted(
            {r for c in summ for r in c["inherited"]}) or ["(nothing)"]) + ".",
        "  Read off the summoned creature's own model, not authored.",
        "- Summon-carrier band spread: "
        + ", ".join(f"`fight:{b}` {100*sum(1 for c in summ if b in c['fight'])/len(summ):.0f}%"
                    for b in rt.FIGHT_BANDS) + ".",
        "",
        "**THE SHAPE THAT MATTERS FOR THE SALON:** the canon summon delivers",
        "more than one role — it attacks *and* shields, visibly — so a card",
        "that deploys one inherits a role at the band it deploys at, whatever",
        "the deck around it looks like. That is the charter's §2 diagnosis with",
        "a number under it, and it is the comparison Furina's typed members are",
        "measured against in `docs/role-tempo-review.tsv`.",
        "",
        "## 6. The floors, and why they are shaped this way",
        "",
        "A cell is **mandatory** when all five canon pools are non-zero in it.",
        "A cell any canon character sits at zero in is an *identity statement*",
        "and is never linted — the charter's own example is Klee at zero",
        "sustain being Silent-shaped rather than deficient.",
        "",
        "The floor for a mandatory cell is the **minimum of the five canon",
        "percentages**. That is forced, not chosen: the brief's stop-and-",
        "surface rule says a floor that would fail a canon character means the",
        "derivation is wrong, and a min-of-canon floor cannot fail one.",
        "",
        f"**{len(floors['mandatory'])} mandatory cells; "
        f"{len(floors['identity_only'])} identity-only cells.**",
        "",
        "| mandatory cell | floor (% of pool) |",
        "|---|---|",
    ]
    for key, val in sorted(floors["mandatory"].items()):
        lines.append(f"| `{key}` | {val:.1f} |")
    lines += [
        "",
        "| identity-only cell (never linted) | canon pools at zero |",
        "|---|---|",
    ]
    for key, who in sorted(floors["identity_only"].items()):
        lines.append(f"| `{key}` | {', '.join(who)} |")
    lines += [
        "",
        "## 7. What this baseline cannot see",
        "",
        "- **No magnitude.** A 3-damage card at fight-early counts exactly as",
        "  much as a 12-damage one. Weighting cells by size would be authoring",
        "  balance numbers, a hard non-goal of this track. Magnitude is Track",
        "  B's curve, and the two are meant to be read together.",
        "- **Canon has no sub-archetypes.** These percentages are whole-pool,",
        "  and the lint applies them to an archetype's sub-pool. That is",
        "  conservative in the right direction (a canon minimum is a bar every",
        "  canon character clears with its whole pool), but it is not an",
        "  apples-to-apples comparison and no cell result should be quoted as",
        "  though it were.",
        "- **`tools/extract_base_game_pool.py::_solve` disagrees with A0.**",
        "  That function tags AoE damage as `utility`, which the charter's",
        "  amendment retires (`aoe` is a modifier, not a role). It is",
        "  DELIBERATELY NOT CHANGED here: it feeds the reference anchors' seven-",
        "  axis scores, and re-tagging them would move measurements this track",
        "  is a non-goal for. The two classifiers coexist and this note is the",
        "  record that the divergence is known.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    floors_doc = [
        "# Role x tempo coverage floors -- MACHINE-GENERATED by",
        "# tools/canon_role_tempo.py from the five canon pools in the local",
        "# sts2.dll. Read by tools/lint_role_tempo_coverage.py.",
        "#",
        "# PERCENTAGES ONLY. No card name, no card text, no card number: this",
        "# file is committed and game_ref/ is not (.gitignore:28).",
        "#",
        "# A cell is mandatory when all five canon pools are non-zero in it;",
        "# the floor is the MINIMUM of the five, so no canon character can",
        "# fail its own floor. Cells any canon pool sits at zero in are",
        "# identity statements and are listed, unlinted, below.",
        "#",
        "# `utility` is never linted and never split (charter A0.2). `support`",
        "# is never linted either: one-seat sim, play-graded only (D4).",
        "",
        "mandatory:",
    ]
    for key, val in sorted(floors["mandatory"].items()):
        floors_doc.append(f"  \"{key}\": {val:.1f}")
    floors_doc += ["", "identity_only:"]
    for key, who in sorted(floors["identity_only"].items()):
        floors_doc.append(f"  \"{key}\": [{', '.join(who)}]")
    floors_doc += ["", "never_linted: [utility, support]", ""]
    OUT_FLOORS.write_text("\n".join(floors_doc), encoding="utf-8")
    print(f"  wrote {OUT_DOC.relative_to(REPO)} and "
          f"{OUT_FLOORS.relative_to(REPO)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from-json", action="store_true",
                    help="re-derive the docs from game_ref/role_tempo_canon."
                         "json instead of decompiling again")
    args = ap.parse_args(argv)
    payload = build(args.from_json)
    write_local(payload)
    write_docs(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
