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
`proto_kk_*`, `proto_mc_*`, `proto_mi_*`, `proto_fr_*` are the arms being
played or being built (the Furina reframe joined on 2026-09-02); the
`proto_spark_*` rows and their power are the retired-in-place Sparks arm
(`M48`), which carries no `description:` and prints the shipped grammar.

THE SHIPPED SHEETS are `--shipped`, a REPORT rather than a gate. `R249` (`EB-345`)
ruled the pass on them and it is applied: the Furina sheet, the companion
rows, the shared keyword tips, the shipped powers and the shipped relics all
read against the same rules now, and the report is clean but for the
exceptions below. The Klee and Kokomi CARD rows are the one part left alone
(pick 1(b)) -- the overhauls being played replace them, so a rewrite of their
faces is work the overhaul deletes -- and they are skipped by id, off their
two sheets.

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

IN_SCOPE = re.compile(r"^proto_(ko|kk|mc|mi|fr)_")

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
    # `TamakushiCasket.description` left this list with `EB-346`: the shared
    # Companion-slot sentence is gone from every relic, and the Casket's own
    # two rules were always under the ceiling.
}

#: THE BOMB BADGE'S GRID (`EB-343`, R248). The badge is the one surface in the
#: mod that prints LIVE ARITHMETIC, and R248 requires it to name every one of
#: the target's modifiers folded into the total it shows -- a Vulnerable folded
#: in silently is the defect the row was raised on. Naming them costs
#: characters, and the Mine axis multiplies whatever the modifier axis costs.
#:
#: THE PLAIN FACE IS NOT HERE and that is the point: `smartDescription`, the
#: face a player reads on an unmodified enemy with no Mine in the pile, is 111
#: of 125 and stays gated. Every entry below is that face plus a clause it is
#: required to carry. Written as the grid rather than fifteen typed keys so it
#: cannot fall out of step with `ProtoBombPower.Localization`, which builds its
#: rows from the same two axes; the rot check still runs per key.
_BOMB_FACE_REASON = (
    "the Bomb badge is the arm's one live-arithmetic surface, and R248 "
    "requires it to name every modifier folded into the number it prints "
    "(EB-343); the Mine axis is EB-260's, rule 6 firing on the enemy's turn "
    "when no card is in front of the player. The unmodified face with no Mine "
    "is under the ceiling and is not excepted")
EXCEPTIONS.update({
    "ProtoBombPower.smartDescription" + mines + vulnerable + cap:
        _BOMB_FACE_REASON
    for mines in ("", "Mines")
    for vulnerable in ("", "Vulnerable")
    for cap in ("", "HardToKill", "Intangible", "Capped")
    if (mines or vulnerable or cap)
})

# --- the shipped exceptions: id -> reason. Same rot semantics. -----------
SHIPPED_EXCEPTIONS = {
    "BombPower.description": (
        "R249 pick 3(a): the shipped Bomb badge is the surface that states "
        "all three of its rules in full -- when it goes off, what makes it "
        "go off early, and the once-per-combat 25% cut -- because the "
        "keyword tip beside it is a primer and drops the last clause's "
        "scope; the prototype badge carries the same exception for the same "
        "reason"),
    "BombPower.smartDescription": (
        "R249 pick 3(a): the shipped Bomb badge keeps its three rules -- a "
        "live total, a live Bomb count and the 25%-off first attack -- the "
        "way the prototype's Mine faces do; the static description without "
        "the live count meets the ceiling"),
}

#: R249 pick 2(a). The shipped Bomb and the overhaul's Bomb are two rules,
#: and two words is honest: the shipped kit keeps "detonates" until the
#: overhaul replaces it, so the SHIPPED read does not carry the `goes-off`
#: spelling. The prototype gate still carries it, which is what keeps the arm
#: on one word -- and the day the overhaul lands, this set empties.
SHIPPED_SKIP_SPELLINGS = {"goes-off"}

#: R249 pick 1(b). The shipped Klee and Kokomi CARD rows do not take the
#: text pass: the overhauls being played replace them, so a rewrite of their
#: faces is work the overhaul deletes. Read off the two sheets by id, so a
#: row that leaves one loses the exemption with it -- and so the exemption
#: names rows rather than a directory, which also holds the companion cards.
EXEMPT_SHEETS = ("klee-cards.yaml", "kokomi-cards.yaml")
SHEET_ID = re.compile(r"^\s*-\s*\{id:\s*([a-z0-9_]+)", re.M)


def pick_branch(expr: str, branch: str) -> str:
    """A `#if`/`#else` pair holds TWO faces; keep the one that is compiled.

    `PROTOTYPE_CARDS` and `KLEE_OVERHAUL` guard the arm's face; the `#else`
    side, or nothing at all where there is none, is what a release build
    prints. Reading both as one string measures a paragraph no build ever
    shows.

    Line-scanned rather than matched, for `gen_keyword_loc.strip_prototype`'s
    reasons and one more: a regex for this shape backtracks quadratically
    inside each arm, and these strings run to kilobytes.
    """
    if "#if" not in expr:
        return expr
    out: list[str] = []
    mode: str | None = None
    for line in expr.splitlines(True):
        stripped = line.lstrip()
        if stripped.startswith("#if"):
            mode = "arm"
        elif stripped.startswith("#else") and mode:
            mode = "ship"
        elif stripped.startswith("#endif") and mode:
            mode = None
        elif mode is None or (mode == "arm") == (branch == "proto"):
            out.append(line)
    return "".join(out)


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
    # NON-GREEDY TO THE CALL'S OWN `);`, and not "any character except a
    # semicolon". The older pattern could not cross a semicolon INSIDE a
    # literal, so a tip whose prose used one was not matched at all and
    # never reached its ceiling: `MineKey` sat outside this census in both
    # of its wordings until `EB-343` went looking. A missing row is silent
    # here, exactly like the missing hover tip `EB-272` was filed on, so
    # the pattern now stops at the statement rather than at a character
    # the prose is allowed to contain.
    for name, body in re.findall(
            r"With\(inherited, (\w+Key),\s*(.*?)\);", src, re.S):
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


def loc_rows(paths: list[Path], surface: str, branch: str) -> list[Row]:
    rows: list[Row] = []
    for path in paths:
        src = read(path)
        src = re.sub(r"^\s*///.*$", "", src, flags=re.M)
        src = re.sub(r"^\s*//.*$", "", src, flags=re.M)
        where = str(path.relative_to(REPO))
        consts = _consts(src)
        # `[^;)\n]` and `\n` are disjoint on purpose. Written as `[^;)]|...|\n`
        # the two branches BOTH matched a newline, so every line inside a
        # localization body doubled the paths the lazy quantifier had to
        # retry, and a 50-line body (KurageSummonPower's two faces) took
        # longer than the rest of the lint put together. Same language, one
        # way to match each character.
        for key, expr in re.findall(
                r'\("(description|smartDescription\w*)",'
                r'\s*((?:[^;)\n]|\n|\)(?!,\n))*?)\),\n', src):
            if "Face(" in expr:
                continue
            classes = re.findall(r"class (\w+)", src[:src.find(expr)])
            cls = classes[-1] if classes else path.stem
            expr = pick_branch(expr, branch)
            text = csharp_text(expr)
            if "MineClause" in expr:
                text += consts.get("MineClause", "")
            rows.append(Row(surface, f"{cls}.{key}", text, where))
        if path.name == "ProtoBombPower.cs":
            # `EB-343` widened the second axis. The badge's face used to be two
            # by two -- a Mine in the pile, and Klee's Weak in the total -- and
            # R248 took Klee out of a Bomb entirely and made every one of the
            # TARGET's terms say its own name, so the grid is now the Mine axis
            # by Vulnerable by the four cap spellings. Rebuilt from the same
            # constants `ProtoBombPower.Face` composes, because this lint reads
            # SOURCE and cannot run `LocManager`.
            caps = (("", ""),
                    ("HardToKill", consts["HardToKillClause"]),
                    ("Intangible", consts["IntangibleClause"]),
                    ("Capped", consts["UnnamedCapClause"]))
            for mines in (False, True):
                for vulnerable in (False, True):
                    for cap_key, cap_text in caps:
                        clause = consts["VulnerableClause"] if vulnerable else ""
                        if cap_text:
                            clause += ("," + cap_text) if vulnerable else cap_text
                        face = ("[gold]Set off[/gold] here deals "
                                + consts["PyroTotal"] + clause + "."
                                + (consts["BombsWithMines"] if mines
                                   else consts["Bombs"])
                                + consts["GrowthSentence"]
                                + (consts["MineClause"] if mines
                                   else consts["NoSelfSentence"]))
                        rows.append(Row(
                            "power",
                            "ProtoBombPower.smartDescription"
                            + ("Mines" if mines else "")
                            + ("Vulnerable" if vulnerable else "")
                            + cap_key,
                            face, where))
    return rows


def prompt_rows() -> list[Row]:
    path = MOD / "Powers" / "Prototype" / "KokomiPlan.cs"
    m = re.search(r"ReflectionPromptText =\s*((?:[^;])*);", read(path))
    return [Row("prompt", "KokomiPlan.ReflectionPromptText", csharp_text(m.group(1)),
                str(path.relative_to(REPO)))]


def exempt_card_ids() -> set[str]:
    """The rows R249 pick 1(b) leaves alone, by id, off their own sheets."""
    out: set[str] = set()
    for name in EXEMPT_SHEETS:
        out |= set(SHEET_ID.findall(read(REPO / "docs" / name)))
    return out


def prototype_rows() -> list[Row]:
    return (card_rows(MOD / "Cards" / "Prototype" / "Generated", IN_SCOPE)
            + tip_rows()
            + loc_rows(sorted((MOD / "Powers" / "Prototype").glob("*.cs")), "power", "proto")
            + loc_rows([MOD / "Relics" / "PoundingSurprise.cs",
                        MOD / "Relics" / "TamakushiCasket.cs"], "relic", "proto")
            + prompt_rows())


def shipped_rows() -> list[Row]:
    rows: list[Row] = []
    for gen in (MOD / "Cards" / "Generated", MOD / "Cards" / "Kokomi" / "Generated",
                MOD / "Cards" / "Furina" / "Generated"):
        rows += card_rows(gen, None)
    powers = [p for p in sorted((MOD / "Powers").glob("*.cs"))]
    rows += loc_rows(powers, "power", "shipped")
    relics = [p for p in sorted((MOD / "Relics").glob("*.cs"))
              if p.name not in ("PoundingSurprise.cs", "TamakushiCasket.cs")]
    rows += loc_rows(relics, "relic", "shipped")
    # The keyword fallback table in KleeMod.cs: the Applies-X and reaction tips.
    kleemod = read(MOD / "KleeMod.cs")
    for key, expr in re.findall(r'\["(KLEEMOD-[A-Z_]+)\.description"\]\s*=\s*((?:[^;]|\n)*?),\n', kleemod):
        rows.append(Row("tip", key, csharp_text(expr), "klee-mod/KleeCode/KleeMod.cs"))
    return rows


# --- the checks ----------------------------------------------------------------

def findings_for(rows: list[Row], exceptions: dict[str, str], gate: bool = True,
                 skip_spellings: set[str] = frozenset()) -> list[str]:
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
            if name in skip_spellings:
                continue
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
        exempt = exempt_card_ids()
        scoped = [r for r in rows if r.ident.split("#")[0] not in exempt]
        found = findings_for(scoped, SHIPPED_EXCEPTIONS,
                             skip_spellings=SHIPPED_SKIP_SPELLINGS)
        for line in found:
            print(line)
        print("text-conventions (shipped): exceptions carried "
              "(each over its ceiling for the reason given):")
        print("\n".join(f"  {k}: {v}" for k, v in SHIPPED_EXCEPTIONS.items()))
        print(f"  spellings not read here: {sorted(SHIPPED_SKIP_SPELLINGS)} "
              "-- R249 pick 2(a), the shipped kit keeps 'detonates'")
        print(f"shipped report: {len(scoped)} strings read, "
              f"{len(rows) - len(scoped)} Klee/Kokomi card faces skipped "
              f"(R249 pick 1(b)), {len(found)} finding(s) "
              "-- a report, not a gate")
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
