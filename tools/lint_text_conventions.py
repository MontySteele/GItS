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
`proto_kk_*`, `proto_mc_*`, `proto_mi_*`, `proto_fs_*` are the arms being
played or being built; the
`proto_spark_*` rows and their power are the retired-in-place Sparks arm
(`M48`), which carries no `description:` and prints the shipped grammar.

THE SHIPPED SHEETS are `--shipped`, a REPORT rather than a gate. `R249` (`EB-345`)
ruled the pass on them and it is applied: the Furina sheet, the companion
rows, the shared keyword tips, the shipped powers and the shipped relics all
read against the same rules now. The report was clean but for the exceptions
below until `EB-777`, which found eight shipped power faces the old matcher
had never read at all (a semicolon in their prose); all eight are over the
power ceiling and they are reported, not rewritten -- this is a tooling row
and shipped prose belongs to a text pass.
The Klee and Kokomi CARD rows are the one part left alone
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
import tempfile
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

IN_SCOPE = re.compile(r"^proto_(ko|kk|mc|mi|fr|fs)_")

# --- the exceptions: id -> reason. Rot semantics, see the module doc. ----
EXCEPTIONS = {
    "proto_mc_durin_binary_form": (
        "a two-mode Power must print both modes on the reward screen, where "
        "the choose-a-card screen's mode faces are not yet visible; the base "
        "game has no static modal card to measure against"),
    "ProtoBakeKuragePower.descriptionCapped": (
        "`EB-653` (Kokomi r24). The cap lane's face, and it exists only under "
        "`GITS_KOKOMI_PLAN_CAP` -- a default build prints the row above it, "
        "at 66 of 125 since the 2026-09-25 text pass, and the capped face is "
        "139. Under the lane rule the jellyfish carried out two of "
        "four written Plans four mornings running and NO SURFACE SAID SO, so "
        "the seat read the rule as a wall for three of the four occurrences "
        "and then reverse-engineered it off the badge. A rule that binds and "
        "prints nowhere is not a rule a round can read, and the two short "
        "sentences in front of it are what the jellyfish IS (untargetable, "
        "holding the Plans until the next turn)"),
    "PendingPlansPower.descriptionCapped": (
        "`EB-777`. The cap lane's Plan badge, and it is on this list because "
        "the lint could not SEE it until now: the badge's own prose carries a "
        "semicolon (`in order next turn; a Dusk Plan at this turn's end`) and "
        "the old matcher's character class excluded one, so both of this "
        "power's faces were skipped whole and neither ever met a ceiling. "
        "`EB-680` recorded that the capped face 'came back under the ceiling' "
        "on the Dusk trim -- a conclusion drawn from a row nothing measured, "
        "and it was wrong: the face is 188 of 125. It is carried rather than "
        "rewritten for `ProtoBakeKuragePower.descriptionCapped`'s reason, "
        "word for word -- it prints only under `GITS_KOKOMI_PLAN_CAP`, a "
        "default build shows the row above it, and a rule that binds and "
        "prints nowhere is not a rule a round can read. The 2026-09-25 Kokomi "
        "text pass took the default face to 61 of 125 and the capped one to "
        "134; what is left over is the cap's own sentence"),
    # `TamakushiCasket.description` left this list with `EB-346`: the shared
    # Companion-slot sentence is gone from every relic, and the Casket's own
    # two rules were always under the ceiling.
}

#: THE BOMB BADGE'S GRID, rebuilt by the text pass of 2026-09-25 to at most
#: three short sentences: what a Set off pays, the pile, and the rider. Every
#: face fits the power ceiling EXCEPT ten that carry the rider sentence (126
#: to 164 rendered; the plain and Melt rider rows fit at 112 and 122),
#: and those are excepted by name here -- ONE reason for all of them, and only
#: the rows over 125 are listed (rot semantics would fail the rest).
_BOMB_RIDER_REASON = (
    "the Bomb badge's rider sentence (`EB-573`: a merge keeps Jumpy Dumpty's "
    "Mine-on-ALL and no other surface says so) rides a face that already "
    "names the total, the Sparks and the pile; the text pass of 2026-09-25 "
    "kept it as a third sentence and took this one exception for it")
EXCEPTIONS.update({
    "ProtoBombPower.smartDescription" + sparks + mines + "Rider" + reaction:
        _BOMB_RIDER_REASON
    for sparks, mines, reaction in (
        ("Sparks", "Mines", ""), ("Sparks", "Mines", "Vaporize"),
        ("Sparks", "Mines", "Melt"), ("Sparks", "", "Vaporize"),
        ("Sparks", "", "Melt"), ("", "Mines", "Vaporize"),
        ("", "Mines", "Melt"), ("Sparks", "", ""), ("", "Mines", ""),
        ("", "", "Vaporize"))
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

#: A CARD TITLE QUOTED AS AN EXAMPLE, dash and all (2026-09-25). The Companion
#: tip's whole rule is the shape of a Companion's title -- "a character's name,
#: a dash, then its own" -- and its example is a real card, printed as the game
#: prints it. The title is struck out of the text before the spellings run, so
#: any OTHER dash in the tip still fails; and an entry whose title is no longer
#: in its string fails too (rot), so the list can only shrink.
QUOTED_TITLES = {"CompanionKey": "Amber — Explosive Puppet"}

TAG = re.compile(r"\[/?[a-z_]+\]")
LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')


@dataclass(frozen=True)
class Row:
    surface: str
    ident: str
    raw: str
    where: str


#: A `{InCombat:A|B}` block, whose `A` may hold one level of var holes.
IN_COMBAT = re.compile(r"\{InCombat:(?:[^{}|]|\{[^{}]*\})*\|([^{}]*)\}")


def render(s: str) -> str:
    """Tags gone, every hole one numeral, the base game's measuring rule."""
    s = s.replace("\\n", " ").replace("\n", " ")
    # `{InCombat:<live line>|<off-board>}` is the base game's own Body Slam
    # shape, and the ceilings are STATIC faces: the off-board branch is what
    # is measured. The Stage's readers print it, and the Furina text pass
    # (2026-09-25) brought their rows into scope.
    s = IN_COMBAT.sub(r"\1", s)
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
        # A Stage round-three defect: the readers' tip picks one of four
        # `const string` rules, so the call carries no literal at all and
        # reaches this census as an empty string. Parsed out by name below.
        if "ReaderKey" in name:
            continue
        rows.append(Row("tip", name, csharp_text(body), where))
    concat = r'("[^"]*"(?:\s*\+\s*"[^"]*")*)'
    word = csharp_text(re.search(r"const string word =\s*" + concat + ";", src).group(1))
    shared = csharp_text(re.search(r"const string shared =\s*" + concat + ";", src).group(1))
    arm = re.search(r'return word \+ "Start each combat with "((?:[^;])*);', src)
    rows.append(Row("tip", "SparkKey", word + "Start each combat with "
                    + csharp_text(arm.group(1)) + shared, where))
    rows.append(Row("tip", "SparkKey.sparks-arm", word + shared, where))
    # A Stage round-three defect. THE READER'S RULE, parsed by name because
    # the call carries no literal. Four rules until the text pass
    # (2026-09-25) deleted the three whose face now names the performer.
    for rule in ("ReaderSpendAllRule",):
        body = csharp_text(
            re.search(rf"const string {rule} =\s*" + concat + ";",
                      src).group(1))
        rows.append(Row("tip", f"ReaderKey.{rule}", body, where))
    return rows


def skip_literal(src: str, i: int) -> int:
    """Index of the character after the C# string literal that opens at `i`.

    `EB-777`. The one primitive this file was missing. Every matcher below used
    to reason about C# with a character class, and a character class cannot
    tell a `;` in PROSE from a `;` that ends a statement -- so a face that used
    one was skipped whole and never met its ceiling. Scanning the literal is
    the only way to know which is which, and it is eight lines.
    """
    i += 1                                   # past the opening quote
    n = len(src)
    while i < n:
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == '"':
            return i + 1
        i += 1
    return n


def _statement_end(src: str, start: int) -> int:
    """Index of the `;` that ends the statement beginning at `start`.

    Literal-aware, for `skip_literal`'s reason: `const string X = "a; b";` is
    one statement and its value contains a semicolon.
    """
    i = start
    n = len(src)
    while i < n:
        c = src[i]
        if c == '"':
            i = skip_literal(src, i)
            continue
        if c == "/" and src[i + 1:i + 2] == "/":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if c == ";":
            return i
        i += 1
    return n


_CONST_HEAD = re.compile(r"const string (\w+) =\s*")


def _consts(src: str) -> dict[str, str]:
    """`const string` declarations, read to the statement's own `;`.

    `EB-777` made this literal-aware. It used to run `[^;]*` to the first
    semicolon ANYWHERE, so a const whose prose carried one was truncated and
    every face that appends it was measured SHORT -- an under-measure rather
    than a skip, and just as silent.
    """
    out: dict[str, str] = {}
    for m in _CONST_HEAD.finditer(src):
        end = _statement_end(src, m.end())
        out[m.group(1)] = csharp_text(src[m.end():end])
    return out


#: `EB-540`. `NextAttackRiderPower.CardTypeClause`, read out of the one file
#: that declares it. Memoized because four faces in two files append it.
_RIDER_CLAUSE: list[str] = []


def _rider_card_type_clause() -> str:
    if not _RIDER_CLAUSE:
        src = read(MOD / "Powers" / "Prototype" / "CompanionOverhaulHooks.cs")
        _RIDER_CLAUSE.append(_consts(src).get("CardTypeClause", ""))
    return _RIDER_CLAUSE[0]


#: `EB-653`. `KokomiPlan.CapSentenceFormat`, read out of the one file that
#: declares it, for `_rider_card_type_clause`'s reason exactly: two faces
#: append it and a clause reaching this lint as a bare identifier is one
#: numeral, which is text no ceiling measures.
_CAP_SENTENCE: list[str] = []


def _plan_cap_sentence() -> str:
    """`KokomiPlan.CapSentenceFormat`, read to the statement's own `;`.

    This sentence contains a semicolon ("at most 2 at the start of your turn;
    the rest wait in order"), so it is the one clause in the tree that proved
    the trap: read to the first semicolon ANYWHERE it returns half a literal,
    the clause measures as nothing, and the capped face sits outside every
    ceiling -- the silence `EB-343` was filed on. `_consts` is literal-aware
    since `EB-777` and would answer this correctly too; the explicit read
    stays because the sentence is a *format* string this file composes rather
    than a clause it appends, and because a fixture that pins the trap is
    worth keeping pointed at the one string that sprang it.
    """
    if not _CAP_SENTENCE:
        src = read(MOD / "Powers" / "Prototype" / "KokomiPlan.cs")
        found = re.search(
            r"const string CapSentenceFormat =\s*"
            r'((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+);', src)
        _CAP_SENTENCE.append(csharp_text(found.group(1)) if found else "")
    return _CAP_SENTENCE[0]


#: `EB-777`. The start of a Localization row: `("description",` or
#: `("smartDescriptionWhatever",`. Where the body ENDS is not a regex's
#: question -- see `loc_bodies`.
LOC_MARKER = re.compile(r'\("(description|smartDescription\w*)",')


@dataclass(frozen=True)
class LocFace:
    key: str
    body: str
    start: int
    #: `row` measured here, `grid` rebuilt by the `ProtoBombPower` block
    #: below, `unparsed` -- a face nothing measures, which is a finding.
    status: str


def loc_bodies(src: str) -> list[LocFace]:
    """Every Localization row in `src`, body scanned rather than matched.

    `EB-777`, and it is `tip_rows`' trap one surface over. The old matcher ran
    `[^;)\\n]` to a `),\\n` terminator, so a body was allowed to contain
    anything EXCEPT a semicolon -- which meant a face whose prose used one
    matched nothing at all and was never measured against its ceiling. A
    missing row is silent here, exactly like the missing hover tip `EB-272`
    was filed on, and `ProtoBombPower.cs` carries a comment telling authors
    not to type a semicolon in player-facing prose because of it.

    Widening the character class is not the fix, because the class was doing
    two jobs: excluding `;` kept a body from running off the end of its own
    statement when the row had no `),\\n` after it. So the boundary is found
    the way C# finds it -- count parentheses, skip string literals and line
    comments, and stop at a `;` that is really a statement terminator.
    """
    out: list[LocFace] = []
    n = len(src)
    for m in LOC_MARKER.finditer(src):
        start = m.end()
        depth = 1                    # the `(` in front of the key is open
        i = start
        body: str | None = None
        while i < n:
            c = src[i]
            if c == '"':
                i = skip_literal(src, i)
                continue
            if c == "/" and src[i + 1:i + 2] == "/":
                while i < n and src[i] != "\n":
                    i += 1
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    body = src[start:i]
                    break
            elif c == ";" and depth == 1:
                break                # a statement ended inside the tuple
            i += 1
        if body is None:
            out.append(LocFace(m.group(1), "", start, "unparsed"))
        elif "Face(" in body:
            out.append(LocFace(m.group(1), body, start, "grid"))
        else:
            out.append(LocFace(m.group(1), body, start, "row"))
    return out


#: `EB-777`'s POSITIVE COUNT. One entry per Localization row the scanner met,
#: as `(file, key, status)`. A ceiling that is never reached fails nothing, so
#: the gate also has to answer "how many faces exist" -- `loc_audit_findings`
#: turns an `unparsed` marker into a failure and `main` prints the arithmetic.
#: Appended to by `loc_rows`, which is called once per surface set, so the
#: tally is reset at the top of `prototype_rows` / `shipped_rows`.
LOC_TALLY: list[tuple[str, str, str]] = []


def loc_audit_findings() -> list[str]:
    """A Localization row the scanner could not read is a face nobody measures."""
    return [f"{where} [{key}]: UNMEASURED -- a Localization row this lint "
            f"could not read to its own `)`. No ceiling was applied to it."
            for where, key, status in LOC_TALLY if status == "unparsed"]


def loc_counts() -> tuple[int, int, int]:
    """(markers seen, rows measured, rows rebuilt as the Bomb grid)."""
    return (len(LOC_TALLY),
            sum(1 for _w, _k, s in LOC_TALLY if s == "row"),
            sum(1 for _w, _k, s in LOC_TALLY if s == "grid"))


def loc_count_line() -> str:
    """The positive count. `EB-777`: a skip has to be VISIBLE, not merely absent."""
    seen, measured, grid = loc_counts()
    return (f"  localization rows scanned: {seen} = {measured} measured "
            f"+ {grid} composed by the Bomb grid "
            f"+ {seen - measured - grid} unmeasured")


def loc_rows(paths: list[Path], surface: str, branch: str) -> list[Row]:
    rows: list[Row] = []
    for path in paths:
        src = read(path)
        src = re.sub(r"^\s*///.*$", "", src, flags=re.M)
        src = re.sub(r"^\s*//.*$", "", src, flags=re.M)
        where = str(path.relative_to(REPO))
        consts = _consts(src)
        for face in loc_bodies(src):
            LOC_TALLY.append((where, face.key, face.status))
            if face.status != "row":
                continue
            key, expr = face.key, face.body
            classes = re.findall(r"class (\w+)", src[:face.start])
            cls = classes[-1] if classes else path.stem
            expr = pick_branch(expr, branch)
            text = csharp_text(expr)
            if "MineClause" in expr:
                text += consts.get("MineClause", "")
            # `EB-540`: the next-Attack riders' shared clause. It is declared
            # ONCE on `NextAttackRiderPower` -- the class whose own
            # `BeforeCardPlayed` is the rule -- and appended by four faces in
            # two files, so it is read from where it lives rather than from
            # each caller's own `consts`. A clause reaching this file as a bare
            # identifier is one numeral and therefore text no ceiling measures,
            # which is the silence `EB-343` was filed on.
            if "CardTypeClause" in expr:
                # `csharp_text` has already counted the trailing identifier as
                # ONE NUMERAL, which is right for a number and wrong for a
                # sentence, so the numeral it stood in for comes off before the
                # sentence goes on.
                text = text[:-1] if text.endswith("6") else text
                text += _rider_card_type_clause()
            # `EB-653`: the cap's clause, and it is TWO ROWS rather than one.
            # The sentence prints only where a lane declared
            # `GITS_KOKOMI_PLAN_CAP`, so the face a default build shows and the
            # face a cap lane shows are two faces, each measured on its own --
            # the arrangement the Spark tip already takes for a body decided
            # at runtime.
            if "CapSentence" in expr:
                text = text[:-1] if text.endswith("6") else text
                rows.append(Row(surface, f"{cls}.{key}", text, where))
                rows.append(Row(surface, f"{cls}.{key}Capped",
                                text + _plan_cap_sentence(), where))
                continue
            rows.append(Row(surface, f"{cls}.{key}", text, where))
        if path.name == "ProtoBombPower.cs":
            # THE LIVE GRID (text pass 2026-09-25), rebuilt from the same
            # constants `ProtoBombPower.Face` composes, because this lint reads
            # SOURCE and cannot run `LocManager`. Four axes: whether a Set off
            # here gives Sparks, whether a Mine is in the pile, whether a rider
            # is, and which amplifying reaction the leading charge will cause.
            reactions = (("", ""), ("Vaporize", consts["VaporizeClause"]),
                         ("Melt", consts["MeltClause"]))
            for sparks in (False, True):
                for mines in (False, True):
                    for rider in (False, True):
                        for r_key, r_text in reactions:
                            face = ("[gold]Set off[/gold] here deals "
                                    + consts["PyroTotal"] + r_text
                                    + (consts["SparksClause"] if sparks
                                       else "")
                                    + "." + consts["Bombs"]
                                    + (consts["MinesClause"] if mines
                                       else "")
                                    + "."
                                    + (consts["RiderSentence"] if rider
                                       else ""))
                            rows.append(Row(
                                "power",
                                "ProtoBombPower.smartDescription"
                                + ("Sparks" if sparks else "")
                                + ("Mines" if mines else "")
                                + ("Rider" if rider else "")
                                + r_key,
                                face, where))
    return rows


#: The SHIPPED power files the arm adds a face to. `EB-421` and `EB-420` put
#: the second and third here -- Guest Cast's mode buff and the replay buff Duet
#: applies -- and they are LISTED rather than globbed because "which shipped
#: power carries an arm face" is a fact worth naming in one place.
FURINA_ARM_FACE_FILES = ("FurinaResources.cs", "SpotlightSystem.cs",
                         "CompanionPowers.cs")


def furina_arm_rows() -> list[Row]:
    """`EB-385`. The arm's faces on SHIPPED powers, gated with the rest of the
    arm.

    Those files are SHIPPED, so `--shipped` reads all of them and the arm rows
    would otherwise be measured only by a report. What belongs to the prototype
    gate is the rows the ARM adds, which are the rows whose KEY says so --
    filtered by key rather than by file, so a second arm face in one of these
    files joins the gate the day it lands and no shipped row is counted twice.
    """
    rows = loc_rows([MOD / "Powers" / name for name in FURINA_ARM_FACE_FILES],
                    "power", "proto")
    return [r for r in rows if "Reframe" in r.ident]


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
    LOC_TALLY.clear()
    return (card_rows(MOD / "Cards" / "Prototype" / "Generated", IN_SCOPE)
            + tip_rows()
            + loc_rows(sorted((MOD / "Powers" / "Prototype").glob("*.cs")), "power", "proto")
            + loc_rows([MOD / "Relics" / "PoundingSurprise.cs",
                        MOD / "Relics" / "TamakushiCasket.cs"], "relic", "proto")
            + furina_arm_rows()
            + prompt_rows())


def shipped_rows() -> list[Row]:
    LOC_TALLY.clear()
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
        spelled = text
        quoted = QUOTED_TITLES.get(row.ident)
        if quoted is not None:
            if quoted not in text:
                out.append(f"QUOTED-TITLE ROT: {tag} no longer quotes "
                           f"{quoted!r}")
            spelled = text.replace(quoted, "the title")
        for name, rx, instead in SPELLINGS:
            if name in skip_spellings:
                continue
            if rx.search(spelled):
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

#: `EB-777`'s FIXTURE. A `Localization` body whose prose carries a SEMICOLON,
#: written the way the tree writes one. Under the old matcher this file
#: produced NO rows at all -- not a short row, not a wrong row, nothing -- and
#: `ProtoBombPower.cs` carries a comment telling authors never to type a
#: semicolon in player-facing prose because of it. The fixture is over the
#: power ceiling on purpose: "it is read" and "it is MEASURED" are two claims,
#: and a fixture that is comfortably short only proves the first.
SEMICOLON_FIXTURE = '''namespace Fixture;

public sealed class SemicolonFacePower : PowerModel, ILocalizationProvider
{
    private const string Tail = " it is spent; nothing refunds it.";

    public List<(string, string)>? Localization => new()
    {
        ("title", "Semicolon"),
        ("description",
            "At the start of your turn this pays [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]; whatever is left over is carried; and when "
          + "the turn after it ends, the whole pile goes off at once."
          + Tail),
    };
}
'''


def self_test() -> list[str]:
    bad: list[str] = []
    # `EB-777`, the SOURCE half of the self-test: every fixture below is a
    # `Row` handed straight to the checks, which tests the ceilings and says
    # nothing about whether a face reaches them. This one goes through the
    # parser.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "SemicolonFacePower.cs"
        path.write_text(SEMICOLON_FIXTURE, encoding="utf-8")
        faces = [f for f in loc_bodies(re.sub(r"^\s*//.*$", "",
                                              path.read_text(encoding="utf-8"),
                                              flags=re.M))
                 if f.status == "row"]
        if len(faces) != 1:
            bad.append(f"self-test: the semicolon face parsed as {len(faces)} "
                       "row(s), not 1")
        else:
            text = render(csharp_text(faces[0].body))
            if ";" not in text:
                bad.append("self-test: the semicolon face lost its semicolon")
            if len(text) <= CEILING["power"]:
                bad.append("self-test: the semicolon fixture is under the "
                           "power ceiling and proves nothing")
            probe = [Row("power", "fx_semicolon", csharp_text(faces[0].body),
                         "fixture")]
            if not any("> 125" in f for f in findings_for(probe, {}, gate=False)):
                bad.append("self-test: the semicolon face was not measured "
                           "against the power ceiling")
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
        print("self-test: 12 bad + 4 clean case(s) + the EB-777 semicolon "
              f"face, {len(bad)} failure(s)")
        return 1 if bad else 0
    if "--shipped" in argv:
        rows = shipped_rows()
        exempt = exempt_card_ids()
        scoped = [r for r in rows if r.ident.split("#")[0] not in exempt]
        found = loc_audit_findings() + findings_for(
            scoped, SHIPPED_EXCEPTIONS, skip_spellings=SHIPPED_SKIP_SPELLINGS)
        for line in found:
            print(line)
        print("text-conventions (shipped): exceptions carried "
              "(each over its ceiling for the reason given):")
        print("\n".join(f"  {k}: {v}" for k, v in SHIPPED_EXCEPTIONS.items()))
        print(f"  spellings not read here: {sorted(SHIPPED_SKIP_SPELLINGS)} "
              "-- R249 pick 2(a), the shipped kit keeps 'detonates'")
        print(loc_count_line())
        print(f"shipped report: {len(scoped)} strings read, "
              f"{len(rows) - len(scoped)} Klee/Kokomi card faces skipped "
              f"(R249 pick 1(b)), {len(found)} finding(s) "
              "-- a report, not a gate")
        return 0
    rows = prototype_rows()
    if "--census" in argv:
        census(rows)
        return 0
    found = loc_audit_findings() + findings_for(rows, EXCEPTIONS)
    for line in found:
        print(line)
    exceptions = [f"  {k}: {v}" for k, v in EXCEPTIONS.items()]
    print("text-conventions: exceptions carried (each over its ceiling for the reason given):")
    print("\n".join(exceptions))
    print(loc_count_line())
    if found:
        print(f"{len(found)} finding(s). The rules: docs/current/text-conventions.md")
        return 1
    print(f"text-conventions: {len(rows)} prototype-arm strings meet the ceilings and spellings")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
