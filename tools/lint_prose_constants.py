#!/usr/bin/env python3
"""Prose lint: player-facing strings that HAND-TYPE a named balance constant.

WHY THIS EXISTS. `lint_constant_parity` compares constants to constants: the
mod's `public const` against the tier0 value it mirrors. It structurally
cannot read prose, so the number a player is actually SHOWN is outside every
gate the repo owns. `EB-86` found the shape of the hazard in the shipped
source: `SalonMemberPower.Localization` printed the six salon numbers as
string literals while `Cards/SalonMemberTips.cs` interpolated
`SalonConstants.*` for the same copy. Both halves passed every check. A
repricing moves the constant, the interpolated half follows, and the literal
half quietly keeps telling the player a retired number -- a build that is
green, tests that pass, and a tooltip that lies.

WHAT IT CHECKS. A numeral that appears in a displayed string, is not
interpolated, and equals a named `const` in the mod whose NAME is about the
same thing the surrounding words are about.

THE MATCHING RULE, and why it is shaped this way. Value equality alone is
useless: `2` is a cost, a duration, a stack count and a multiplier all at
once, so a bare value join produced ~74 hits on this codebase of which a
handful were real. The discriminator is NAME AFFINITY -- a hit is reported
only when a word near the numeral shares a stem with a word in the constant's
name. "applies Pyro for 2 turns" reaches `ReactionConstants.AuraDurationTurns`
through `turns`; "deal 3 damage" does not reach `SparkPower.Threshold` at all.
Concretely:

  * SCOPE is `klee-mod/KleeCode/**/*.cs`, minus `Diagnostics/` -- those
    strings are telemetry rows and parity-vector log lines, read by this repo
    and never by a player, and their numerals are mostly `{0}`-style format
    placeholders.
  * SCOPE ALSO COVERS THE PACKAGED LOC TABLES (`EB-160`). The game merges
    `res://klee/localization/<lang>/<table>.json` OVER the dll's rows, so the
    copy a player actually reads is the JSON, and until this row the lint
    could not see it at all. Two sources reach the pack: the tracked tables
    under `klee-mod/pck-src/**/localization/**/*.json`, and the tables
    `tools/build_pck.ps1` still writes from a here-string at pack time. Both
    are read here; a numeral in a VALUE is a numeral a player is shown.
    `gen_keyword_loc.py` derives `card_keywords.json` from the C# and
    `--check` gates its staleness, so that table's rows can no longer drift on
    their own -- but the gate for a HAND-TYPED table (today `ancients.json`,
    tomorrow whatever the next dressing writes) is this one.
  * THE CORPUS IS THE C# ALONE, and that is a separate question from scope.
    `RARE_FRACTION` decides when ONE shared word is enough and is measured
    over the denominator; the JSON tables are a DERIVED or a packaged copy of
    the same prose, so counting them would let a table double a word's
    frequency and quietly un-suppress findings elsewhere -- the exact skew the
    `Teyvat` exclusion below is about. Scanned, not counted.
  * A DISPLAYED STRING is a string literal with at least three alphabetic
    words, no path characters, and no `KLEEMOD-` loc-key prefix. Comments are
    lexed out, so a doc comment quoting an old number is not a finding (it is
    prose about code, not prose shown to anyone).
  * A NUMERAL inside braces is skipped: `{0}`, `{Slots}` and the holes of an
    interpolated `$"..."` are resolved by the localizer or the compiler, and
    the hole text is not literal at all.
  * AFFINITY: the constant's name is split on CamelCase, lowercased, stripped
    of structural words (`per`, `max`, `of`, `to`, `up`, `and`), and words
    shorter than four letters are dropped. A window of +/-60 characters
    around the numeral is split the same way. A pair matches when one word is
    a prefix of the other and the shared prefix is at least four letters --
    so `turns`/`turn`, `vulnerable`/`vuln` and `shatters`/`shatter` all join,
    while `per`/`per` cannot, because `per` is not a word this lint counts.
  * STRENGTH, the second tuning pass. One shared word is enough only when
    that word is RARE IN THE MOD'S OWN PROSE -- present in at most
    `RARE_FRACTION` of the displayed strings. `damage` (71 of 636 strings),
    `turn` (41) and `encore` (18) are the vocabulary every card face uses, so
    a lone `damage` join says nothing; `splash` (5), `vuln` (4) and `weak`
    (1) name one mechanic each, so a lone join there is a real signal. Two or
    more shared words are always enough, however common each is -- that is
    what carries `AuraDurationTurns` against "applies Pyro for 2 turns". The
    corpus is measured on every run, so the threshold tracks the codebase
    instead of freezing a 2026 word list.

WHAT THIS BUYS AND WHAT IT DOES NOT. The rule is tuned for PRECISION, not
completeness: it is a gate that must stay green forever on a growing
codebase, and a gate that cries wolf gets suppressed. It will miss a literal
whose prose shares no vocabulary with its constant's name ("Maximum 3" does
not reach `SalonConstants.MemberSlots`). That is the accepted cost; the
alternative is 74 lines of noise and a lint nobody reads.

ALLOWLIST. `ALLOWED` below carries the curated residue -- a numeral that
genuinely coincides with a constant it has nothing to do with. Every entry
names the file, the constant, the numeral and the REASON, and a stale entry
(one whose site no longer exists) is itself a finding, so the list cannot
quietly outlive what it excuses.

Run: python tools/lint_prose_constants.py
Exit 1 with findings on stdout. `--list-constants` dumps the constants the
lint can see, for triaging a new finding.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools import lint_constant_parity as cp  # noqa: E402
# `EB-791`: the blind page's stripper, so this lint and the generator that
# writes the titles agree about what a rich-text tag is.
from understudy.qa_packet import strip_markup  # noqa: E402

CS_ROOT = REPO / "klee-mod" / "KleeCode"

# `EB-160`. The two other places a player-facing string reaches the pack: the
# tracked overlay, copied in as-is, and the packer's own here-strings.
#
# RESOLVED FROM `REPO` AT CALL TIME, not bound at import: the lint's own tests
# point `REPO` at a synthetic tree, and a path frozen here would send them at
# the shipped pack while every other root was redirected.
def pck_src() -> Path:
    return REPO / "klee-mod" / "pck-src"


def pck_script() -> Path:
    return REPO / "tools" / "build_pck.ps1"

# A loc table that is GENERATED from an interpolated source is out of scope,
# and it is the one exclusion here that is not a judgement call: this lint's
# whole demand is "interpolate the constant", and a derived file cannot --
# it IS the resolved output, and editing it is an edit the generator throws
# away. `tools/gen_keyword_loc.py` derives this table from `KleeMod.cs`'s
# `keywordFallback`, whose numerals are interpolated (`EB-89`) and whose rows
# this lint already reads at the source; `--check` is the staleness gate that
# stops the copy drifting. Scanning the output would report every one of those
# rows as a hand-typed literal, which is the definition of crying wolf.
#
# THE HAND-TYPED TABLES ARE THE POINT (`EB-160`) and none of them is here: the
# packer's own here-strings, and any table a future dressing commits by hand.
DERIVED_LOC_TABLES = frozenset({
    "klee-mod/pck-src/klee/localization/eng/card_keywords.json",
})

# Telemetry and parity-vector text: written for this repo's own logs, never
# rendered to a player, and full of `{0}` format placeholders.
#
# `Teyvat` for a different reason, and the stronger one: NOTHING UNDER IT
# CARRIES ONE OF THIS MOD'S BALANCE CONSTANTS. A mirror's numbers are the base
# game's, copied clause for clause off the 0.111.0 decompile -- Room Full of
# Cheese's 14, Brain Leech's 5 -- and interpolating a Klee-side constant into
# one would be a MECHANICAL CHANGE to a base event, which is the single thing
# this surface exists to prevent. The generated rows are curated FACE prose
# about those same base-game numbers, which is the same argument once
# removed. So a match here is a coincidence by construction, and an ALLOWED
# entry per dressed row would be a list that churns on every face edit and
# says nothing.
#
# AND IT SKEWS THE CORPUS, which is the reason it is an exclusion and not an
# allowlist. `RARE_FRACTION` decides when ONE shared word is enough, and it
# is measured over the displayed strings this lint can see. Act 1's thirty-
# three dressed events are thirty-three SCENE PARAGRAPHS of Genshin prose --
# by far the longest displayed strings in the mod and none of them about a
# card -- so letting them into the denominator moved words like "block" and
# "damage" across that line and un-suppressed fifty-seven findings in
# `Cards/Prototype/Generated` that have nothing to do with this arm. A gate
# whose verdict on a Klee card moves when a Mondstadt event is dressed is
# measuring the wrong corpus.
EXCLUDED_DIRS = ("Diagnostics", "Teyvat")

BACKSLASH = chr(92)

# Structural words: they carry no subject matter, so they must not be able to
# join a numeral to a constant. `per` alone accounted for a third of the
# false joins in the pre-tuning sweep (`ChargePerExhaust` reaching "1 more
# damage per").
STOPWORDS = frozenset({
    "per", "max", "min", "the", "and", "for", "of", "to", "up", "at",
    "constants", "value", "amount", "count", "base", "default",
})

MIN_WORD = 4          # letters; below this a "shared stem" is a coincidence
CONTEXT_CHARS = 60    # window each side of the numeral

# A single shared word must appear in no more than this fraction of the mod's
# displayed strings. 0.02 is ~13 of the 636 strings shipped today: it admits
# `fanfare` (11) and `burst` (5), and rejects `damage` (71), `turn` (41) and
# `encore` (18). Raising it re-admits the generic vocabulary and the lint
# starts crying wolf; lowering it drops `fanfare` and the Spotlight class of
# finding with it.
RARE_FRACTION = 0.02

# THE TWO CARD-FACE STAPLES, common by fiat and not by measurement. `block`
# and `damage` are the base game's two numbered nouns, printed on most cards;
# `damage` has always cleared RARE_FRACTION, and `block` sat within a string
# or two of it (26 of 1,332 displayed strings when the Klee pool expansion and
# Furina's Stage batch two landed together, 2026-09-23), so its verdict on
# every "Gain N Block" face flipped whenever the corpus grew elsewhere -- the
# EXCLUDED_DIRS finding one word over. A lone shared word on either is never
# enough to tie a numeral to a constant.
ALWAYS_COMMON = frozenset({"block", "damage"})

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
NUM_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
CAMEL_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z]*|[a-z]+|\d+")
PATHISH_RE = re.compile(r"res://|[/\\]|\.png|\.tres|\.ogg")


# --------------------------------------------------------------------------
# ALLOWED: curated coincidences. (relative path, Class.Member, numeral) ->
# reason. An entry that no longer matches a live site is reported, so this
# list stays as short as the code makes it.
# --------------------------------------------------------------------------
ALLOWED: dict[tuple[str, str, str], str] = {
    ("klee-mod/KleeCode/KleeMod.cs", "SalonConstants.TickEncoreCost", "1"):
        "The Confiscated keyword says 'A 1-cost Status card that does "
        "nothing.' -- that 1 is the Status card's ENERGY cost, not the "
        "Salon's Encore tick price. `cost` joins them and nothing else does. "
        "Repricing the salon tick must not touch this string.",
    # DROPPED by `EB-345` (R249), and by the lint reporting it stale, which is
    # the whole point of it reporting stale entries. The entry excused True
    # Spark Knight's "for your Attacks to cost 0 (minimum 1)": the shipped
    # text pass took the parenthesis out (rule 14) and the floor now reads
    # "never fewer than 1", which puts four words between `cost` and the
    # numeral and leaves no affinity to excuse.
    # 2026-09-02, the text-conventions pass. Both joins are the bare word the
    # base game uses for a card type: the page un-golded `Attack` on the
    # prototype faces (card types are plain words, `RAGE_POWER`), and the
    # lint's affinity now sees it.
    ("klee-mod/KleeCode/Cards/Prototype/Generated/ProtoMcMikaStarfrostSwirl.cs",
     "SalonConstants.TickEncoreCost", "1"):
        "Starfrost Swirl reads 'Your next Attack costs 1 less.' The 1 is an "
        "Energy discount on a card, not the Salon's Encore tick price, and "
        "`cost` is the only word joining them.",
    ("klee-mod/KleeCode/Cards/Prototype/Generated/ProtoMiSaraTenguStormcall.cs",
     "CompanionOverhaulLaw.LightfallPerAttack", "5"):
        "Tengu Stormcall reads 'Next turn, your Attacks deal 5 additional "
        "damage.' The 5 is Stormcall's own bonus (`StormcallBonus`, which the "
        "POWER face interpolates); the row prints the sheet's literal, as "
        "every authored face does, and `attack` is the only word joining it "
        "to Eula's per-Attack 5.",
    # DROPPED 2026-09-02, and by the excuse's own last sentence. It said "the
    # card face is the row's `description:`; move the number there" -- and the
    # `EB-283` counted/flag split did exactly that: `weak` is a COUNTED power,
    # so Sea-Salt Prayer's printed 1 became the `{PowerAmount:diff()}` token
    # its upgrade moves and the bare numeral left the string. The coincidence
    # cannot arise any more, and the lint reported the entry as stale, which is
    # the whole point of it reporting stale entries.
    # DROPPED by `EB-258`. The entry excused Deep Breath's "Spend 3 Encore"
    # against `KurageMemoryLaw.CostPerEnergy`, and the ONLY thing that ever
    # joined them was the bare word `Energy` sitting in the face's other
    # clause. Golding the resources broke that join at the source: the face
    # now reads "[gold]Energy[/gold]", the coincidence does not arise, and the
    # lint reported the excuse as no longer matching -- which is the whole
    # point of it reporting stale entries.
}


@dataclass(frozen=True)
class Literal:
    text: str
    line: int


def scan_strings(text: str) -> list[Literal]:
    """Every string literal in a C# source, with comments lexed out.

    Interpolation holes and verbatim doubled quotes are handled because both
    change what the literal's TEXT is: a hole is code, not text, and its
    contents must not be read as prose. Holes become NUL so that a numeral
    cannot be assembled across one.
    """
    out: list[Literal] = []
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            line += text.count("\n", i, j)
            i = j
            continue
        if c == "'":                      # char literal: '"' would derail us
            j = i + 1
            if j < n and text[j] == BACKSLASH:
                j += 1
            i = j + 2
            continue
        verbatim = c == "@" and i + 1 < n and text[i + 1] == '"'
        interp = c == "$" and i + 1 < n and text[i + 1] == '"'
        if not (verbatim or interp or c == '"'):
            i += 1
            continue
        start_line = line
        j = i + (2 if (verbatim or interp) else 1)
        buf: list[str] = []
        while j < n:
            ch = text[j]
            if verbatim:
                if ch == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        buf.append('"')
                        j += 2
                        continue
                    break
                if ch == "\n":
                    line += 1
                buf.append(ch)
                j += 1
                continue
            if ch == BACKSLASH:           # escape: one opaque character
                buf.append("\x00")
                j += 2
                continue
            if interp and ch == "{":
                if j + 1 < n and text[j + 1] == "{":
                    buf.append("{")
                    j += 2
                    continue
                depth = 1
                j += 1
                while j < n and depth:
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                    j += 1
                buf.append("\x00")
                continue
            if ch == '"' or ch == "\n":
                break
            buf.append(ch)
            j += 1
        out.append(Literal("".join(buf), start_line))
        i = j + 1
    return out


def is_displayed(text: str) -> bool:
    """Prose a player could read, as opposed to a key, a path or an id."""
    if PATHISH_RE.search(text) or "KLEEMOD-" in text:
        return False
    return len(WORD_RE.findall(text)) >= 3


def name_words(identifier: str) -> set[str]:
    """A constant's own vocabulary: CamelCase split, minus structural words."""
    words = {w.lower() for w in CAMEL_RE.findall(identifier)}
    return {w for w in words if len(w) >= MIN_WORD and w not in STOPWORDS}


def prose_words(text: str) -> set[str]:
    words = {w.lower().strip("'-") for w in WORD_RE.findall(text)}
    return {w for w in words if len(w) >= MIN_WORD and w not in STOPWORDS}


def affinity(const_key: str, context: str) -> set[str]:
    """The words that join this numeral to this constant, if any.

    A prefix join rather than equality, because English inflects what C#
    does not: `AuraDurationTurns` vs "for 2 turns", `SuperconductVuln` vs
    "gains 2 Vulnerable", `ShatterDamage` vs "Shatters for 6 damage".
    """
    shared: set[str] = set()
    left = name_words(const_key.split(".", 1)[-1])
    right = prose_words(context)
    for a in left:
        for b in right:
            common = min(len(a), len(b))
            if common >= MIN_WORD and (a.startswith(b) or b.startswith(a)):
                shared.add(a)
    return shared


def brace_spans(text: str) -> list[tuple[int, int]]:
    """`{...}` regions -- format placeholders and DynamicVar tokens."""
    spans, depth, start = [], 0, 0
    for idx, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0:
                spans.append((start, idx + 1))
    return spans


def sources() -> list[Path]:
    return [p for p in sorted(CS_ROOT.rglob("*.cs"))
            if not any(part in EXCLUDED_DIRS for part in p.parts)]


def loc_json_sources() -> list[Path]:
    """The TRACKED loc tables that reach the pack (`EB-160`).

    `klee-mod/pck-src` is the overlay: every file under it is copied into the
    pack as-is, so a `localization/<lang>/<table>.json` here is a table the
    game merges over the dll's rows and therefore the copy a player reads.
    """
    root = pck_src()
    if not root.exists():
        return []
    return [p for p in sorted(root.rglob("*.json"))
            if "localization" in p.parts
            and p.relative_to(REPO).as_posix() not in DERIVED_LOC_TABLES]


def loc_json_strings(path: Path) -> list[Literal]:
    """Every VALUE in a loc table, with the line it sits on.

    Keys are skipped: a key is `KLEEMOD-BOMB.title`, an identifier, and
    `is_displayed` would refuse it anyway. Values are read with the line
    number found by searching the raw text, because `json.loads` throws line
    numbers away and a finding that cannot be located is a finding nobody
    fixes. A table that will not parse is NOT silently skipped -- see
    `main`.
    """
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    out: list[Literal] = []
    rows = json.loads(raw)
    if not isinstance(rows, dict):
        return out
    for key, value in rows.items():
        if not isinstance(value, str):
            continue
        at = next((i for i, line in enumerate(lines, 1)
                   if f'"{key}"' in line), 1)
        out.append(Literal(value, at))
    return out


# The loc tables `tools/build_pck.ps1` still writes at pack time, as
# `[IO.File]::WriteAllText((Join-Path $locDir 'ancients.json'), @'...'@)`.
# These never exist as a file in the repo -- they are a here-string inside the
# packer -- which is exactly why they were outside every gate the repo owns
# (`EB-160`). `$locDir` is the localization directory the script builds once,
# so matching on that variable is matching on "a loc table", not on a filename
# that could be renamed out from under this pattern.
PCK_LOC_HERESTRING = re.compile(
    r"WriteAllText\(\(Join-Path\s+\$locDir\s+'(?P<name>[^']+)'\)\s*,\s*@'"
    r"(?P<body>.*?)^'@\)",
    re.S | re.M)


def pck_loc_strings() -> tuple[list[tuple[str, int, str]], list[str]]:
    """(rows, complaints) for every loc table the packer types by hand.

    A row is `(rel path, line, value)`. A COMPLAINT is a table under
    `$locDir` that will not parse as JSON: nothing else is written there, the
    game would merge a broken table as nothing at all, and a lint that shrugged
    at it would be reading past exactly the file it was widened to reach.
    """
    script = pck_script()
    if not script.exists():
        return [], [f"{script.name} is missing -- the packer moved, and a "
                    f"lint that passes because it read nothing is not a gate."]
    raw = script.read_text(encoding="utf-8")
    out: list[tuple[str, int, str]] = []
    complaints: list[str] = []
    if not PCK_LOC_HERESTRING.search(raw):
        complaints.append(
            f"{script.relative_to(REPO).as_posix()}: no loc table is "
            f"written from a here-string any more. If the packer stopped "
            f"typing tables by hand that is the row's goal reached -- drop "
            f"this reader; if the shape changed, point the pattern at it. A "
            f"gate that reads nothing is not a gate.")
    for match in PCK_LOC_HERESTRING.finditer(raw):
        base = raw.count("\n", 0, match.start("body")) + 1
        name = match.group("name")
        rel = f"{script.relative_to(REPO).as_posix()} ({name})"
        body = match.group("body")
        try:
            rows = json.loads(body)
        except json.JSONDecodeError as exc:
            complaints.append(f"{rel}:{base}: this loc table does not parse "
                              f"as JSON ({exc.msg}), so the game merges "
                              f"nothing from it.")
            continue
        if not isinstance(rows, dict):
            continue
        lines = body.splitlines()
        for key, value in rows.items():
            if not isinstance(value, str):
                continue
            at = base + next((i for i, line in enumerate(lines)
                              if f'"{key}"' in line), 0)
            out.append((rel, at, value))
    return out, complaints


def numeric_constants() -> dict[float, list[str]]:
    """Named numeric constants of the mod, keyed by value.

    `lint_constant_parity.collect()` is reused deliberately: the two lints
    then agree by construction on what "a named balance constant" is, and a
    constant that becomes invisible to one becomes invisible to both rather
    than to one silently.
    """
    by_value: dict[float, list[str]] = {}
    for key, (raw, _path) in cp.collect().items():
        value = cp.parse_number(raw)
        if value is None:
            continue
        by_value.setdefault(value, []).append(key)
    return by_value


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    const: str
    numeral: str
    shared: tuple[str, ...]
    context: str

    @property
    def allow_key(self) -> tuple[str, str, str]:
        return (self.path, self.const, self.numeral)

    def __str__(self) -> str:
        return (f"{self.path}:{self.line}: displayed string hand-types "
                f"{self.numeral}, which is {self.const}'s value "
                f"(shared: {', '.join(self.shared)}). Interpolate the "
                f"constant, or add an ALLOWED entry saying why the match is "
                f"a coincidence.\n    ...{self.context}...")


def displayed_corpus() -> list[tuple[str, int, str]]:
    """(relative path, line, text) for every displayed string in scope.

    `EB-791`: A STRING THAT IS ANOTHER STRING WITH THE TAGS OFF IS NOT A
    SECOND PIECE OF PROSE. A modal card's mode face carries its sentence
    twice -- as the option card's TITLE, which the game draws as plain text,
    and as its DESCRIPTION, which the game renders. The tags therefore come
    off one and stay on the other, and this lint's join is word ADJACENCY:
    `[gold]Energy[/gold]` next to a numeral is not a join and `Energy` next to
    the same numeral is, which is the reason three of the entries in `ALLOWED`
    above record themselves as dropped ("golding the resources broke that join
    at the source"). Un-golding the title re-created every one of those
    coincidences, on a copy of a sentence the lint is already reading one line
    below with its tags intact.

    So the copy does not vote and is not reported. Matched EXACTLY -- the
    title must be some other literal in the same file with `strip_markup`
    applied and nothing else -- so a title that says anything of its own is
    scanned as normal, and so is one whose description carries an
    interpolation hole the title spells out as a number.
    """
    out = []
    for path in sources():
        rel = path.relative_to(REPO).as_posix()
        lits = scan_strings(path.read_text(encoding="utf-8"))
        # Off EVERY literal and not only the displayed ones: a closing tag
        # reads as a path to `is_displayed`, so the tagged original is not in
        # the corpus at all -- which is exactly why golding a resource drops a
        # face out of this lint's reach.
        untagged = {strip_markup(lit.text) for lit in lits
                    if strip_markup(lit.text) != lit.text}
        for lit in lits:
            if lit.text in untagged or not is_displayed(lit.text):
                continue
            out.append((rel, lit.line, lit.text))
    return out


def common_words(corpus: list[tuple[str, int, str]]) -> set[str]:
    """Words too common in the mod's own prose to carry a lone match.

    Measured rather than listed: the vocabulary a card face reaches for is a
    property of the shipped copy, and it moves as characters ship.
    """
    counts: dict[str, int] = {}
    for _rel, _line, text in corpus:
        for w in prose_words(text):
            counts[w] = counts.get(w, 0) + 1
    cap = max(1, RARE_FRACTION * len(corpus))
    return {w for w, c in counts.items() if c > cap} | ALWAYS_COMMON


def loc_corpus() -> tuple[list[tuple[str, int, str]], list[str]]:
    """Every displayed string in a loc table that reaches the pack (`EB-160`).

    SCANNED, NOT COUNTED: these rows are returned for findings and are NOT
    part of `common_words`' denominator -- see the module docstring's CORPUS
    paragraph for why letting a derived copy of the prose vote would move the
    threshold under everything else.
    """
    out: list[tuple[str, int, str]] = []
    complaints: list[str] = []
    for path in loc_json_sources():
        rel = path.relative_to(REPO).as_posix()
        try:
            rows = loc_json_strings(path)
        except json.JSONDecodeError as exc:
            complaints.append(f"{rel}: this loc table does not parse as JSON "
                              f"({exc.msg}), so the game merges nothing from "
                              f"it.")
            continue
        out += [(rel, lit.line, lit.text) for lit in rows
                if is_displayed(lit.text)]

    packed, packer_complaints = pck_loc_strings()
    out += [row for row in packed if is_displayed(row[2])]
    complaints += packer_complaints

    # A DERIVED entry that names nothing is itself a finding, `ALLOWED`'s own
    # rule one list over: the exclusion list may not quietly outlive the
    # generator that earned it.
    for rel in sorted(DERIVED_LOC_TABLES):
        if not (REPO / rel).exists():
            complaints.append(
                f"DERIVED_LOC_TABLES names {rel}, which does not exist. Drop "
                f"the entry, or point it at the table the generator writes "
                f"now.")
    return out, complaints


def prose_findings() -> list[Finding]:
    by_value = numeric_constants()
    corpus = displayed_corpus()
    common = common_words(corpus)
    loc_rows, _complaints = loc_corpus()
    findings: list[Finding] = []
    seen: set[tuple[str, int, str, str]] = set()
    for rel, line, text in corpus + loc_rows:
        skip = brace_spans(text)
        for m in NUM_RE.finditer(text):
            if any(a <= m.start() < b for a, b in skip):
                continue
            value = float(m.group(1))
            if value not in by_value:
                continue
            lo = max(0, m.start() - CONTEXT_CHARS)
            context = text[lo:m.end() + CONTEXT_CHARS]
            for key in sorted(by_value[value]):
                shared = affinity(key, context)
                # One shared word carries the match only when it is a word
                # this codebase's prose does NOT reach for constantly.
                if len(shared) < 2 and not (shared - common):
                    continue
                dedupe = (rel, line, key, m.group(1))
                if dedupe in seen:
                    continue
                seen.add(dedupe)
                findings.append(Finding(
                    rel, line, key, m.group(1), tuple(sorted(shared)),
                    context.replace("\x00", "*").strip()))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list-constants", action="store_true",
                    help="print the constants the lint can see, then exit")
    args = ap.parse_args(argv)

    if args.list_constants:
        for value, keys in sorted(numeric_constants().items()):
            print(f"{value:>12g}  {', '.join(sorted(keys))}")
        return 0

    files = sources()
    if not files:
        print("FINDING: no C# sources found under klee-mod/KleeCode -- the "
              "layout changed, and a lint that passes because it read "
              "nothing is not a gate.")
        return 1

    tables = loc_json_sources()
    findings = prose_findings()
    packaged, complaints = loc_corpus()
    live = {f.allow_key for f in findings}
    reported = [f for f in findings if f.allow_key not in ALLOWED]
    stale = sorted(set(ALLOWED) - live)

    for f in reported:
        print(f"FINDING: {f}")
    for key in stale:
        print(f"FINDING: ALLOWED excuses {key}, which no longer matches any "
              f"displayed string. Drop the entry.")
    for complaint in complaints:
        print(f"FINDING: {complaint}")

    if reported or stale or complaints:
        return 1
    print(f"prose constants: OK ({len(files)} source(s), "
          f"{len(tables)} hand-written loc table(s) plus {len(packaged)} "
          f"packaged loc row(s), "
          f"{sum(len(v) for v in numeric_constants().values())} named "
          f"constants, {len(ALLOWED)} allowed coincidence(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
