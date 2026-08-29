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
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools import lint_constant_parity as cp  # noqa: E402

CS_ROOT = REPO / "klee-mod" / "KleeCode"

# Telemetry and parity-vector text: written for this repo's own logs, never
# rendered to a player, and full of `{0}` format placeholders.
EXCLUDED_DIRS = ("Diagnostics",)

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
    ("klee-mod/KleeCode/Powers/SparkKitPowers.cs",
     "SalonConstants.TickEncoreCost", "1"):
        "True Spark Knight reads 'for your Attacks to cost 0 (minimum 1)'. "
        "The 1 is the floor on a card's energy cost -- a rule of the base "
        "game's cost arithmetic, with no constant behind it -- and again it "
        "is the word `cost` doing the joining.",
    ("klee-mod/KleeCode/Cards/Furina/Generated/DeepBreath.cs",
     "KurageMemoryLaw.CostPerEnergy", "3"):
        "Deep Breath is a FURINA card and reads 'Gain 1 Energy and 2 Encore | "
        "Spend 3 Encore: draw 3.' -- that 3 is an Encore price on Furina's "
        "meter. The Kurage's memory multiplier is Kokomi's, it is behind a "
        "quarantine flag, and the only thing joining them is the word "
        "`Energy` appearing in a different clause of the same face. Changing "
        "the memory's 3x must not touch this string, and vice versa.",
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
    """(relative path, line, text) for every displayed string in scope."""
    out = []
    for path in sources():
        rel = path.relative_to(REPO).as_posix()
        for lit in scan_strings(path.read_text(encoding="utf-8")):
            if is_displayed(lit.text):
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
    return {w for w, c in counts.items() if c > cap}


def prose_findings() -> list[Finding]:
    by_value = numeric_constants()
    corpus = displayed_corpus()
    common = common_words(corpus)
    findings: list[Finding] = []
    seen: set[tuple[str, int, str, str]] = set()
    for rel, line, text in corpus:
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

    findings = prose_findings()
    live = {f.allow_key for f in findings}
    reported = [f for f in findings if f.allow_key not in ALLOWED]
    stale = sorted(set(ALLOWED) - live)

    for f in reported:
        print(f"FINDING: {f}")
    for key in stale:
        print(f"FINDING: ALLOWED excuses {key}, which no longer matches any "
              f"displayed string. Drop the entry.")

    if reported or stale:
        return 1
    print(f"prose constants: OK ({len(files)} source(s), "
          f"{sum(len(v) for v in numeric_constants().values())} named "
          f"constants, {len(ALLOWED)} allowed coincidence(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
