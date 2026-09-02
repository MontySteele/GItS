#!/usr/bin/env python3
"""Player-facing TEXT against `docs/current/text-conventions.md`.

WHAT IT GUARDS. Every string the two PROTOTYPE arms and the companion arm
print in the game -- card faces, mode faces, the arm keyword tips, the power
badges, the two relics and the one selection prompt -- against the length
ceilings measured on the base game's own loc tables and the spellings the
conventions page fixes. The owner's ask, 2026-09-02: never print "a Yu-Gi-Oh
card's worth of text", and spell one word one way within a character and
between them.

WHAT IT READS. The EMITTED C# (`Cards/Prototype/Generated/*.cs`), not the
sheet: the face a player reads is the row's `description:` plus what the
codegen adds (`Play on the Bake-Kurage.`, the upgrade add-clause) minus what
it strips (`Exhaust.`), and `gen_prototype_cards.py --check` already holds
the two in step. Hand-written strings are read out of their `Localization`
tuples: a concatenation of literals is joined, an interpolated law constant
counts as one numeral, a `{hole}` as one numeral, a `[tag]` as nothing --
the same rendering `text-conventions.md` measured the base game with.

SCOPE, and why the older Sparks arm is outside it. Rows `proto_ko_*`,
`proto_kk_*`, `proto_mc_*`, `proto_mi_*` are the arms being played; the
`proto_spark_*` rows and their power are the retired-in-place Sparks arm
(`M48`), which carries no `description:` and prints the shipped grammar.
The shipped sheets are `--shipped`: a REPORT, never a gate, because their
rewrite is [USER]'s (`review/active/text-conventions-shipped-2026-09-02.md`).

THE EXCEPTION LIST is curated, with a reason per entry, and it has rot
semantics: an entry whose string is now UNDER its ceiling fails, so the list
can only shrink.

    python tools/lint_text_conventions.py               # the gate
    python tools/lint_text_conventions.py --self-test   # seen to FAIL on a fixture
    python tools/lint_text_conventions.py --shipped     # report the shipped sheets
    python tools/lint_text_conventions.py --census      # every string, its length

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import glob
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MOD = REPO / "klee-mod" / "KleeCode"

# --- the ceilings, from text-conventions.md ("Ceilings, measured") --------
CEILING = {
    "card": 120,          # RIGHT_HAND_HAND 117, the longest static base face
    "mode": 120,          # a mode face is a card face
    "tip": 135,           # CHANNELING 134, the longest base mechanic tip
    "power": 125,         # AGGRESSION_POWER 123
    "relic": 120,         # PAELS_TOOTH's static part, 118
    "prompt": 85,         # the longest base selectionScreenPrompt, 84
}
ADD_CLAUSE_CEILING = 20   # the longest base {IfUpgraded:show:...} clause, 18
MAX_SENTENCES = 4         # the base's longest card is four sentences

IN_SCOPE = re.compile(r"^proto_(ko|kk|mc|mi)_")

# --- the exceptions: id -> reason. Rot semantics, see the module doc. ----
EXCEPTIONS = {
    "proto_mc_durin_binary_form": (
        "a two-mode Power must print both modes on the reward screen, where "
        "the choose-a-card screen's mode faces are not yet visible; the base "
        "game has no static modal card to measure against"),
    "ProtoBombPower.description": (
        "the Bomb badge's static face carries rules 1, 2 and 6 in one "
        "paragraph because a canonical copy has no live pile to quote; the "
        "in-combat smart faces without a Mine meet the ceiling"),
    "ProtoBombPower.smartDescriptionMines": (
        "a live total, a live count, a Mine count and rule 6, which fires on "
        "the enemy's turn when no card is in front of the player (EB-260)"),
    "ProtoBombPower.smartDescriptionMinesWeak": (
        "the Mine face plus the one term a player cannot see in the total "
        "(EB-287)"),
    "TamakushiCasket.description": (
        "a two-rule starting relic plus the shared 59-character "
        "Companion-slot sentence every starting relic in this mod appends; "
        "its own two rules are under the ceiling on their own"),
}

# --- the spellings ----------------------------------------------------------
#: (name, regex over the RENDERED text, what the page says instead)
SPELLINGS: list[tuple[str, re.Pattern[str], str]] = [
    ("target-word", re.compile(r"\btarget enemy\b"),
     "a single-target hit names no target; the same enemy again is 'the enemy'"),
    ("every-enemy", re.compile(r"\bevery enemy\b"), "'ALL enemies'"),
    ("all-lowercase", re.compile(r"\ball enemies\b"), "'ALL enemies', capitals and all"),
    ("jellyfish", re.compile(r"\bjellyfish\b", re.I), "the pet is named: 'the Bake-Kurage'"),
    ("goes-off", re.compile(r"\b(detonat\w*|explode\w*|pops?)\b"),
     "a Bomb 'goes off'; the verb is 'Set off'"),
    ("lasts-more", re.compile(r"\bLasts \d+ more turn"), "'Lasts for {Amount} turns.'"),
    ("dash", re.compile(r"(\s--\s|--|—|–)"), "no dashes of any kind"),
    ("draw-cards", re.compile(r"\b[Dd]raw \d+(?=[.,;]|\s+(?:and|at|if)\b)"),
     "'Draw N cards.' with the noun"),
    ("more-damage", re.compile(r"\b\d+ more(?= damage| Block)"),
     "'N additional damage'"),
    ("reaction-lowercase", re.compile(r"\breactions?\b"),
     "'[gold]Elemental Reaction[/gold]', the shipped spelling"),
    ("otherwise-comma", re.compile(r"\bOtherwise [a-z]"), "'Otherwise, ...'"),
    ("parenthesis", re.compile(r"[()]"), "no parentheses"),
]
#: Regexes over the RAW text (markup matters).
RAW_SPELLINGS: list[tuple[str, re.Pattern[str], str]] = [
    ("gold-cardtype", re.compile(r"\[gold\]Attacks?\[/gold\]|\[gold\]Skills?\[/gold\]|\[gold\]Powers?\[/gold\]"),
     "card types are plain words: 'Attack', 'Skill', 'Power'"),
    ("bare-keyword", re.compile(r"(?<!\[gold\])\b(Block|Weak|Vulnerable|Strength|Dexterity)\b(?![^\[]*\[/gold\])"),
     "keywords are Capitalised and [gold]"),
    ("printed-exhaust", re.compile(r"(^|\.\s)Exhaust\.(\s|$)"),
     "Exhaust is the keyword rail, never a sentence"),
]
#: Card faces only: a Plan line never names the front enemy (the rule is the
#: word's), and the one row allowed to is the power whose trigger is not a Plan.
FRONT_ENEMY = re.compile(r"\bfront enemy\b")
FRONT_ENEMY_ALLOWED = {"proto_kk_the_generals_banner", "GeneralsBannerPower.description",
                       "PlanKey"}

TAG = re.compile(r"\[/?[a-z_]+\]")
LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')


@dataclass(frozen=True)
class Row:
    surface: str
    ident: str
    raw: str
    where: str


def render(s: str) -> str:
    """Tags gone, every hole one numeral, the base game's measuring rule."""
    s = s.replace("\\n", " ").replace("\n", " ")
    s = TAG.sub("", s)
    s = re.sub(r"\{[^{}]*energyIcons[^{}]*\}", "E", s)
    s = re.sub(r"\{[A-Za-z]+:plural:([^|}]*)\|([^}]*)\}", r"\2", s)
    s = re.sub(r"\{[A-Za-z_]+:show:([^|}]*)\|[^}]*\}", "", s)
    s = re.sub(r"\{[^{}]*\}", "6", s)
    return re.sub(r"\s+", " ", s).strip()


def add_clauses(raw: str) -> list[str]:
    return [render(m) for m in re.findall(r"\{IfUpgraded:show:([^|}]*)\|", raw)]


def sentences(rendered: str) -> int:
    return len(re.findall(r"[.!?](?:\s|$)", rendered))


def csharp_text(expr: str) -> str:
    """Join a C# concat expression's literals; a bare identifier or an
    interpolation hole is one numeral, which is how the page measured."""
    expr = re.sub(r"^\s*//.*$", "", expr, flags=re.M)
    out: list[str] = []
    pos = 0
    for m in LIT.finditer(expr):
        between = expr[pos:m.start()]
        if out and re.search(r"[A-Za-z_][A-Za-z0-9_.]*\s*\+\s*$", between):
            out.append("6")
        lit = m.group(1).replace('\\"', '"')
        if expr[m.start() - 1: m.start()] == "$":
            lit = re.sub(r"\{[^{}]*\}", "6", lit)
        out.append(lit)
        pos = m.end()
    if re.search(r"^\s*\+\s*[A-Za-z_][A-Za-z0-9_.]*", expr[pos:]):
        out.append("6")
    return "".join(out)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- the surfaces --------------------------------------------------------------

def card_rows(gen_dir: Path, scope: re.Pattern[str] | None) -> list[Row]:
    rows: list[Row] = []
    for path in sorted(gen_dir.glob("*.cs")):
        src = read(path)
        cls = path.stem
        ident = re.sub(r"(?<!^)(?=[A-Z])", "_", cls).lower()
        if scope is not None and not scope.match(ident):
            continue
        faces = re.findall(r'\("description", "((?:[^"\\]|\\.)*)"\)', src)
        for i, face in enumerate(faces):
            rows.append(Row("card" if i == 0 else "mode",
                            ident if i == 0 else f"{ident}#mode{i}",
                            face, str(path.relative_to(REPO))))
    return rows


def tip_rows() -> list[Row]:
    path = MOD / "Cards" / "Prototype" / "ArmKeywordTips.cs"
    src = re.sub(r"^\s*//.*$", "", read(path), flags=re.M)
    where = str(path.relative_to(REPO))
    rows: list[Row] = []
    for name, body in re.findall(r"With\(inherited, (\w+Key),\s*((?:[^;]|\n)*?)\);", src):
        if "SparkBody()" in body:
            continue
        rows.append(Row("tip", name, csharp_text(body), where))
    concat = r'("[^"]*"(?:\s*\+\s*"[^"]*")*)'
    word = csharp_text(re.search(r"const string word =\s*" + concat + ";", src).group(1))
    shared = csharp_text(re.search(r"const string shared =\s*" + concat + ";", src).group(1))
    arm = re.search(r'return word \+ "Start each combat with "((?:[^;])*);', src)
    rows.append(Row("tip", "SparkKey", word + "Start each combat with "
                    + csharp_text(arm.group(1)) + shared, where))
    rows.append(Row("tip", "SparkKey.sparks-arm", word + shared, where))
    return rows


def _consts(src: str) -> dict[str, str]:
    return {n: csharp_text(e) for n, e in
            re.findall(r"const string (\w+) =\s*((?:[^;])*);", src)}


def loc_rows(paths: list[Path], surface: str, slot_sentence: str) -> list[Row]:
    rows: list[Row] = []
    for path in paths:
        src = read(path)
        src = re.sub(r"^\s*///.*$", "", src, flags=re.M)
        src = re.sub(r"^\s*//.*$", "", src, flags=re.M)
        where = str(path.relative_to(REPO))
        consts = _consts(src)
        for key, expr in re.findall(
                r'\("(description|smartDescription\w*)",\s*((?:[^;)]|\)(?!,\n)|\n)*?)\),\n', src):
            if "Face(" in expr:
                continue
            classes = re.findall(r"class (\w+)", src[:src.find(expr)])
            cls = classes[-1] if classes else path.stem
            if "#if KLEE_OVERHAUL" in expr:
                expr = expr.split("#else")[0]
            text = csharp_text(expr)
            if "RewardSlotDescription" in expr:
                text += slot_sentence
            if "MineClause" in expr:
                text += consts.get("MineClause", "")
            rows.append(Row(surface, f"{cls}.{key}", text, where))
        if path.name == "ProtoBombPower.cs":
            for mines in (False, True):
                for weak in (False, True):
                    face = ("[gold]Set off[/gold] here deals "
                            + (consts["WeakTotal"] if weak else consts["PlainTotal"])
                            + (consts["BombsWithMines"] if mines else consts["Bombs"])
                            + consts["GrowthSentence"]
                            + (consts["MineClause"] if mines else consts["NoSelfSentence"]))
                    rows.append(Row("power", "ProtoBombPower.smartDescription"
                                    + ("Mines" if mines else "") + ("Weak" if weak else ""),
                                    face, where))
    return rows


def prompt_rows() -> list[Row]:
    path = MOD / "Powers" / "Prototype" / "KokomiPlan.cs"
    m = re.search(r"ReflectionPromptText =\s*((?:[^;])*);", read(path))
    return [Row("prompt", "KokomiPlan.ReflectionPromptText", csharp_text(m.group(1)),
                str(path.relative_to(REPO)))]


def slot_sentence() -> str:
    m = re.search(r'RewardSlotDescription =\s*"([^"]*)"', read(MOD / "CompanionSlot.cs"))
    return m.group(1) if m else ""


def prototype_rows() -> list[Row]:
    slot = slot_sentence()
    return (card_rows(MOD / "Cards" / "Prototype" / "Generated", IN_SCOPE)
            + tip_rows()
            + loc_rows(sorted((MOD / "Powers" / "Prototype").glob("*.cs")), "power", slot)
            + loc_rows([MOD / "Relics" / "PoundingSurprise.cs",
                        MOD / "Relics" / "TamakushiCasket.cs"], "relic", slot)
            + prompt_rows())


def shipped_rows() -> list[Row]:
    slot = slot_sentence()
    rows: list[Row] = []
    for gen in (MOD / "Cards" / "Generated", MOD / "Cards" / "Kokomi" / "Generated",
                MOD / "Cards" / "Furina" / "Generated"):
        rows += card_rows(gen, None)
    powers = [p for p in sorted((MOD / "Powers").glob("*.cs"))]
    rows += loc_rows(powers, "power", slot)
    relics = [p for p in sorted((MOD / "Relics").glob("*.cs"))
              if p.name not in ("PoundingSurprise.cs", "TamakushiCasket.cs")]
    rows += loc_rows(relics, "relic", slot)
    # The keyword fallback table in KleeMod.cs: the Applies-X and reaction tips.
    kleemod = read(MOD / "KleeMod.cs")
    for key, expr in re.findall(r'\["(KLEEMOD-[A-Z_]+)\.description"\]\s*=\s*((?:[^;]|\n)*?),\n', kleemod):
        rows.append(Row("tip", key, csharp_text(expr), "klee-mod/KleeCode/KleeMod.cs"))
    return rows


# --- the checks ----------------------------------------------------------------

def findings_for(rows: list[Row], exceptions: dict[str, str], gate: bool = True) -> list[str]:
    out: list[str] = []
    seen_over: set[str] = set()
    for row in rows:
        text = render(row.raw)
        n = len(text)
        ceiling = CEILING[row.surface]
        tag = f"{row.where} [{row.ident}]"
        if n > ceiling:
            seen_over.add(row.ident)
            if row.ident not in exceptions:
                out.append(f"{tag}: {n} > {ceiling} ({row.surface} ceiling): {text}")
        if sentences(text) > MAX_SENTENCES:
            out.append(f"{tag}: {sentences(text)} sentences (max {MAX_SENTENCES}): {text}")
        for clause in add_clauses(row.raw):
            if len(clause) > ADD_CLAUSE_CEILING:
                out.append(f"{tag}: upgrade clause {len(clause)} > {ADD_CLAUSE_CEILING}: {clause}")
        for name, rx, instead in SPELLINGS:
            if rx.search(text):
                out.append(f"{tag}: {name}: {instead}: {text}")
        holes_blanked = re.sub(r"\{[^{}]*\}", "6", row.raw)
        for name, rx, instead in RAW_SPELLINGS:
            if rx.search(holes_blanked):
                out.append(f"{tag}: {name}: {instead}: {row.raw}")
        if (row.surface in ("card", "mode") or row.surface == "tip"
                or row.surface == "power") \
                and FRONT_ENEMY.search(text) and row.ident not in FRONT_ENEMY_ALLOWED:
            out.append(f"{tag}: front-enemy: a Plan line names no target; "
                       f"the tip carries the rule: {text}")
    if gate:
        known = {r.ident for r in rows}
        for ident, reason in exceptions.items():
            if ident not in known:
                out.append(f"EXCEPTION ROT: {ident!r} names no string on the tree")
            elif ident not in seen_over:
                out.append(f"EXCEPTION ROT: {ident!r} is under its ceiling now; "
                           f"drop it from EXCEPTIONS ({reason[:40]}...)")
    return out


# --- the self-test: seen to FAIL on a fixture -------------------------------------

def self_test() -> list[str]:
    bad: list[str] = []
    fixture = [
        Row("card", "fx_long", "Deal 6 damage to ALL enemies, then choose one for the fight. "
            "White: enemies take 50% more damage from reactions. Dark: your Pyro Attacks that "
            "react deal 8 more damage. Then draw 2 cards. Gain 3 Block.", "fixture"),
        Row("card", "fx_target", "Deal 6 damage to target enemy.", "fixture"),
        Row("card", "fx_every", "Deal 5 damage to every enemy.", "fixture"),
        Row("card", "fx_jelly", "The jellyfish carries out your front Plan now.", "fixture"),
        Row("card", "fx_draw", "Draw 1. [gold]Plan[/gold]: Draw 3.", "fixture"),
        Row("card", "fx_bare", "Gain 4 Block. Apply 1 Weak.", "fixture"),
        Row("card", "fx_gold_type", "Your next [gold]Attack[/gold] costs 1 less.", "fixture"),
        Row("card", "fx_plan_front", "[gold]Plan[/gold]: the front enemy gains 1 [gold]Weak[/gold].", "fixture"),
        Row("power", "fx_lasts", "Gain [blue]4[/blue] [gold]Block[/gold]. Lasts {Amount} more turn{Amount:plural:|s}.", "fixture"),
        Row("power", "fx_dash", "Draw {Amount} cards -- unless you play an Attack.", "fixture"),
        Row("card", "fx_upgrade", "Deal 6 damage.{IfUpgraded:show: Then draw 2 cards and gain 3 Block.|}", "fixture"),
        Row("tip", "fx_tip", "A " + "very " * 30 + "long tip.", "fixture"),
    ]
    expected = {"fx_long": ("> 120", "sentences", "reaction-lowercase", "more-damage"),
                "fx_target": ("target-word",), "fx_every": ("every-enemy",),
                "fx_jelly": ("jellyfish",), "fx_draw": ("draw-cards",),
                "fx_bare": ("bare-keyword",), "fx_gold_type": ("gold-cardtype",),
                "fx_plan_front": ("front-enemy",), "fx_lasts": ("lasts-more",),
                "fx_dash": ("dash",), "fx_upgrade": ("upgrade clause",),
                "fx_tip": ("> 135",)}
    found = findings_for(fixture, {}, gate=False)
    for ident, needles in expected.items():
        mine = [f for f in found if f"[{ident}]" in f]
        for needle in needles:
            if not any(needle in f for f in mine):
                bad.append(f"self-test: {ident} did not raise {needle!r}")
    clean = [
        Row("card", "ok_a", "Deal {Damage:diff()} damage. Apply 1 [gold]Weak[/gold].", "fixture"),
        Row("card", "ok_b", "Play on the [gold]Bake-Kurage[/gold]. [gold]Plan[/gold]: Deal 5 damage to ALL enemies.", "fixture"),
        Row("power", "ok_c", "At the end of your turn, deal [blue]6[/blue] [gold]Cryo[/gold] damage to a random enemy. Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}.", "fixture"),
        Row("card", "ok_d", "Gain 4 [gold]Block[/gold]. Next turn, draw 2 cards if you play no Attacks this turn.", "fixture"),
    ]
    for f in findings_for(clean, {}, gate=False):
        bad.append(f"self-test: clean fixture raised {f}")
    # rot: an exception naming a clean string fails
    rot = findings_for([clean[0]], {"ok_a": "no reason"}, gate=True)
    if not any("EXCEPTION ROT" in f for f in rot):
        bad.append("self-test: a stale exception did not fail")
    return bad


def census(rows: list[Row]) -> None:
    for row in sorted(rows, key=lambda r: (r.surface, -len(render(r.raw)))):
        text = render(row.raw)
        flag = "OVER" if len(text) > CEILING[row.surface] else "    "
        print(f"{flag} {row.surface:6s} {len(text):4d} {row.ident:44s} {text}")


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: 12 bad + 4 clean case(s), {len(bad)} failure(s)")
        return 1 if bad else 0
    if "--shipped" in argv:
        rows = shipped_rows()
        found = findings_for(rows, {}, gate=False)
        for line in found:
            print(line)
        over = [r for r in rows if len(render(r.raw)) > CEILING[r.surface]]
        print(f"shipped report: {len(rows)} strings, {len(over)} over ceiling, "
              f"{len(found)} finding(s) -- a report, not a gate")
        return 0
    rows = prototype_rows()
    if "--census" in argv:
        census(rows)
        return 0
    found = findings_for(rows, EXCEPTIONS)
    for line in found:
        print(line)
    exceptions = [f"  {k}: {v}" for k, v in EXCEPTIONS.items()]
    print("text-conventions: exceptions carried (each over its ceiling for the reason given):")
    print("\n".join(exceptions))
    if found:
        print(f"{len(found)} finding(s). The rules: docs/current/text-conventions.md")
        return 1
    print(f"text-conventions: {len(rows)} prototype-arm strings meet the ceilings and spellings")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
