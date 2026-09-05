"""EB-149: the BLIND packet — printed truth of one staged board, nothing else.

This module is the half of the QA funnel that must be provably free of design
context, so it is a module of its own rather than a function inside
`staged_turn.py`. Three facts follow from that separation and all three are
tested (`tier0/tests/test_staged_turn.py`):

  * IT IMPORTS NOTHING FROM `tier0`. Not the sheet loaders, not the engine,
    not the pilot. An AST walk over this file's imports pins it
    (`test_the_packet_builder_cannot_reach_a_sheet`). A packet builder that
    could open `docs/kokomi-cards.yaml` would be one refactor away from
    printing a `role:` into the thing whose whole value is that it has none.
  * IT COPIES FIELD BY FIELD FROM AN ALLOWLIST. Nothing is spread, merged or
    `dict(**wire)`-ed. Every value in a packet was written by a line naming
    exactly which printed quantity it is. That is what "by construction"
    means here: the leak cannot happen by omission, only by somebody adding a
    line that says the wrong thing.
  * IT SCRUBS ITS OWN OUTPUT AND RAISES. `FORBIDDEN` is a belt to that brace.
    Every string VALUE in the finished packet is matched against the design
    vocabulary; a hit is `PacketLeak`, not a warning, and the packet is not
    written. Keys are exempt on purpose -- a key is this module's own word
    (`enemies`, `intent`), never content taken off the wire.

WHAT THE AGENT IS ALLOWED TO SEE, AND WHY THAT LIST IS SHORT (R213 step 2)
--------------------------------------------------------------------------
"card texts, staged hand, intents only". Concretely: the card faces as the
GAME prints them, the player's HP / Block / energy / named resources, each
enemy's display name, HP, Block and telegraphed intent, and the printed name
and hover text of every power on the board. Not: internal ids, sheet comments,
roles, archetypes, tempo bands, solve tags, ruling numbers, register ids, the
character's design identity, or anything about how the board was staged.

The absence of ids is a design constraint and not tidiness. The agent's answer
is a list of PRINTED TITLES; `staged_turn.execute` translates those back to the
hand indices the bridge wants. An agent that never sees an id cannot be
answering about a card it recognises from a sheet.

WHERE THE CARD TEXT COMES FROM, AND THE PACKET SAYS WHICH
---------------------------------------------------------
Preferred and used in practice: the LIVE bridge GET's own `description` on
each hand entry, which is the string the game has already rendered with its
dynamic vars resolved -- the face a player is looking at. `text_source` on
each card says `bridge`.

Fallback, only when the wire carries no description: the generated C#
`Localization` block in `klee-mod/KleeCode/Cards/**/Generated/*.cs`. That text
is the TEMPLATE -- `{CalculatedDamage:diff()}` and friends are unresolved --
so a card that falls back is marked `generated-cs (unresolved dynamic vars)`
and the packet header says so in as many words. A packet that quietly printed
a template as if it were a face would be a packet whose answer to question one
is about a card that does not exist.

GUARDRAIL-7 IS UNCHANGED. A staged board is a board somebody set by hand.
Nothing derived from this packet is comparable to any run, and nothing here or
downstream of it is a claim about look, legibility, readability or fun.
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

# The disqualification that rides on the packet, the JSON, the verdict and
# every ledger row. Same reasoning as `bridge.GRANT_GUARDRAIL` and
# `frames.GUARDRAIL`: a caveat that lives outside the record is lost the
# moment two records are concatenated.
PACKET_GUARDRAIL = (
    "staged board: this hand and this board were set by hand through a "
    "dev door, so nothing measured here is comparable to any run, and "
    "nothing here is a claim about whether the turn is fun")

# The vocabulary a blind packet may not contain. Matched against string VALUES
# only (see the module docstring). Each entry is (rule-name, compiled regex).
#
# The snake_case rule is the one that earns its keep: it is how an internal
# card id (`pearl_barrage`, `all_streams_flow`) reads, and no printed face in
# this mod contains one -- the faces are Title Case prose. It is deliberately
# blunt.
FORBIDDEN: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("register-id", re.compile(r"\b(EB|S4-G|W)\-?\d+\b")),
    ("ruling-id", re.compile(r"\bR\d{1,3}\b")),
    ("milestone-id", re.compile(r"\bM\d{1,3}\b")),
    ("sheet-field-role", re.compile(r"\brole\s*:", re.I)),
    ("sheet-field-archetypes", re.compile(r"\barchetypes?\b", re.I)),
    ("sheet-field-tempo-band", re.compile(r"\btempo_band\b", re.I)),
    ("sheet-field-solve", re.compile(r"\bsolve\s*:", re.I)),
    ("mod-id-prefix", re.compile(r"KLEEMOD[-_]", re.I)),
    ("internal-snake-case-id", re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")),
)

# `klee-mod/KleeCode/Cards/<Character>/Generated/<Class>.cs`. Only read on the
# fallback path; see the module docstring.
_GENERATED_GLOB = "KleeCode/Cards/*/Generated/*.cs"
_LOC_RE = re.compile(r'\(\s*"(title|description)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\)')

# EB-186. THE COST PRINTED ON THE CARD, WHICH THE GAME STOPS SHOWING.
#
# Klee's Spark power rides `Hook.ModifyEnergyCostInCombat`, and the game
# consults that hook for BOTH display and payment -- so at a full bank every
# Attack the player holds is drawn at 0 (the draw pile too), while the rule
# frees exactly one of them. Round 1 of the Klee slice put twelve blind
# readers in front of that page: every one of them read "all my Attacks are
# free", and TEN of the twelve lines they wrote were refused live with
# `EnergyCostTooHigh`. A page whose costs are unpayable is not a picture of
# the turn.
#
# So the page carries the card's PRINTED cost beside the rendered one wherever
# the two differ. That number is read from the SHIPPED FACE in `klee-mod`
# -- the same C# this module already reads for the fallback card text, and
# the same `cost=` the generator wrote there out of the sheet -- and NOT from
# a tier0 loader, because this module may not reach a sheet (see the module
# docstring and `test_the_packet_builder_cannot_reach_a_sheet`). Two comment
# shapes carry it, the generated header's `Sheet entry: id=... cost=2` and the
# hand-written cards' `Sheet: cost 1, damage 7`, so one regex reads both and
# the pin in `tier0/tests` cross-checks every id it finds against the sheet
# the generator emitted from.
#
# DISCLOSED, BECAUSE IT IS A DEPARTURE. A player at the machine cannot see
# `1` on a discounted Kaboom!; the page shows it anyway, because the
# alternative -- proven twice over in round 1 -- is a page that reads as an
# offer the board will refuse.
#
# `EB-267`: KEYED BY CARD ID, NOT BY PRINTED TITLE, and that is the whole row.
# The prototype surface deliberately ships a re-priced twin of a shipped card
# under the SAME printed name -- `Flame Dance` is `flame_dance` at cost 2 and
# `proto_ko_flame_dance` at cost 1 -- so a title-keyed map answered the proto
# card with the shipped card's number and the page told a blind reader its
# cost was wrong when nothing was. The key is the wire's own `Id.Entry` with
# the mod prefix off (`KLEEMOD-PROTO_KO_FLAME_DANCE` -> `PROTO_KO_FLAME_DANCE`),
# which BaseLib derives from the C# CLASS NAME (`DuckAndCover` ->
# `DUCK_AND_COVER`, `KleeMod.cs:81`) -- so the class name in the file the cost
# comment sits in IS the key, for a generated card and a hand-written one
# alike, and the prototype rows are already in this glob rather than needing a
# sheet this module may not open.
_CARD_SOURCE_GLOB = "KleeCode/Cards/**/*.cs"
_SHEET_COST_RE = re.compile(r"[Ss]heet[^\n]*?\bcost[=:]?\s*(\d+)")

# `EB-282`. THE OTHER HALF OF A SPARK-PRICED CARD'S COST, WHICH THE `cost=`
# COMMENT ABOVE STRUCTURALLY CANNOT CARRY.
#
# A Spark-priced row prints `cost: 0` on the sheet and charges its Sparks
# through `spend_spark`, so the number the regex above finds is 0 -- true, and
# not the price. In the game the cost slot shows the SPARK BADGE for those
# rows, which is why the row asks for the body sentence ("Spend 1 Spark.") to
# come off the face: it is text overhead restating the badge. On this page
# there was no badge and no number, so dropping the sentence would have taken
# the price off the page entirely and the seats would have been reading a card
# whose cost they could not see.
#
# So the price is read the same way, off the same faces, out of the ONE place
# the generator writes it: `ISparkPricedCard.PrintedSparkPrice`, which the
# card's own playability gate reads back through `SparkCost.PriceOf` (the
# generated comment beside it says why it is declared once). Same key as the
# energy index -- the class name, which is what BaseLib derives `Id.Entry`
# from -- so a proto row and its same-named shipped twin cannot be confused.
#
# `EB-491`. TWO SHAPES SINCE FIREWORKS SHOW, whose upgrade CUTS the price:
# the flat literal, and `(IsUpgraded ? <up> : <base>)`. The index is keyed on
# the CLASS and so cannot know which copy a seat is holding, exactly as the
# energy index cannot -- so it reads the BASE branch, which is the number an
# unupgraded card charges and the one every other figure on this page states.
_SPARK_PRICE_RE = re.compile(
    r"PrintedSparkPrice\s*=>\s*(?:\(IsUpgraded\s*\?\s*\d+\s*:\s*)?"
    r"(\d+)\s*\)?\s*;")
_CLASS_RE = re.compile(
    r"^\s*(?:public|internal)\s+(?:sealed\s+|abstract\s+|static\s+|partial\s+)*"
    r"class\s+([A-Za-z_][A-Za-z0-9_]*)", re.M)
_MOD_ID_PREFIXES = ("KLEEMOD_",)

# The one power whose cost hook this note exists for, matched on the PRINTED
# name the wire carries (`Spark`), never on a power id.
_SPARK_TITLE = "spark"
# `... Playing one consumes 3 Sparks.` -- read off the power's OWN printed
# hover text, so the arithmetic below is the arithmetic a player can do from
# the words in front of them. No constant is imported for it: a threshold this
# module hard-coded would be a number the page asserts rather than reads.
_CONSUMES_RE = re.compile(r"consume(?:s)?\s+(\d+)", re.I)


class PacketLeak(RuntimeError):
    """A finished packet carried design vocabulary. It is not written."""


# ------------------------------------------------------------- scrubbing ---

def _strings(blob: Any) -> list[str]:
    """Every string VALUE in a nested structure. Keys are not values."""
    out: list[str] = []
    if isinstance(blob, str):
        out.append(blob)
    elif isinstance(blob, dict):
        for v in blob.values():
            out.extend(_strings(v))
    elif isinstance(blob, (list, tuple)):
        for v in blob:
            out.extend(_strings(v))
    return out


def leaks(blob: Any, allow: frozenset[str] | set[str] = frozenset()
          ) -> list[tuple[str, str, str]]:
    """`(rule, matched-text, the-string-it-was-in)` for every leak found.

    `allow` (EB-167) exempts EXACT matched tokens from the snake_case rule and
    from that rule ALONE. It exists because a design-blind render of ANY screen
    has to be able to say which screen it refused to drive, and the wire's own
    name for a screen -- `rest_site`, `card_select`, or an unknown one this
    repo has never seen -- reads as an internal id to a rule that is
    deliberately blunt. A screen name is the game's public API vocabulary, not
    design vocabulary: it names no card, no role and no ruling. The caller
    passes the ONE token it is about to print and nothing else, so the
    exemption is auditable at the call site rather than sitting in a growing
    constant here. Every other rule -- register ids, ruling numbers, sheet
    fields, the mod prefix -- is never exempt.

    Matched with `finditer` rather than `search`: a string holding an exempt
    token AND a real id must still report the id, and a first-match-only scan
    would stop at the exempt one.
    """
    found: list[tuple[str, str, str]] = []
    for s in _strings(blob):
        for rule, pattern in FORBIDDEN:
            for m in pattern.finditer(s):
                if rule == "internal-snake-case-id" and m.group(0) in allow:
                    continue
                found.append((rule, m.group(0), s))
                break
    return found


def assert_blind(blob: Any, allow: frozenset[str] | set[str] = frozenset()
                 ) -> None:
    bad = leaks(blob, allow)
    if bad:
        detail = "; ".join(f"{rule}: {hit!r} in {ctx[:120]!r}"
                           for rule, hit, ctx in bad[:5])
        raise PacketLeak(
            f"{len(bad)} design-vocabulary leak(s) in the packet: {detail}")


# --------------------------------------------------- the generated-C# path --

def localization_index(repo: Path) -> dict[str, str]:
    """`{printed title: printed description template}` from generated C#.

    The FALLBACK source only. Dynamic vars are left exactly as the generator
    wrote them, unresolved, because resolving them here would mean computing a
    number the game is the authority on -- and this module is not allowed to
    know enough to do that.
    """
    index: dict[str, str] = {}
    root = repo / "klee-mod"
    if not root.is_dir():
        return index
    for path in sorted(root.glob(_GENERATED_GLOB)):
        try:
            src = path.read_text(encoding="utf-8")
        except OSError:
            continue
        # PAIRED SEQUENTIALLY, not by carving out the `Localization => new()
        # { ... }` block. A description like
        # `Deal {CalculatedDamage:diff()} damage` contains a closing brace, so
        # a brace-matched block ends in the middle of the very string this
        # index exists to read -- which is how the first version of this
        # function silently returned every title with an empty description.
        # A file may hold several classes (a modal card's option bodies), and
        # each title claims the description that follows it.
        title = ""
        for m in _LOC_RE.finditer(src):
            if m.group(1) == "title":
                title = m.group(2)
            elif title:
                index.setdefault(title, m.group(2))
                title = ""
    return index


# `EB-246`. THE GAME'S RICH-TEXT MARKUP, AND THE ONE PLACE IT IS SPELLED.
#
# A printed name or body can carry the game's own inline markup --
# `Spend 6 [gold]Charge[/gold]: gain 12 Block` is a real *Choose one* option
# name -- and `scenario.card_key` has folded those tags out since Kokomi slice
# 2 so a replay can answer a modal in the vocabulary a blind grader was shown.
# The BLIND RENDER did not, so one choice had two printed names -- the staged
# packet's and the blind page's -- and the `KLEESPARK-W5` tester had to type
# `[gold]` tags to name a choice they were looking at.
#
# It lives HERE because this module is the leaf both sides may import:
# `blindplay` is forbidden `scenario` by the structural no-leak pin
# (`test_blindplay_cannot_reach_a_sheet_or_a_policy`), and a second copy of a
# regex is a second copy that drifts.
#
# DELIBERATELY NARROW, TWICE OVER, and both narrowings are the safety argument.
#
# 1. The shape: a bracketed run of lowercase word characters with an optional
#    `=value`, and nothing else. `[silent_energy_icon.png]` carries a dot and is
#    NOT matched -- that tag names an icon the player is looking at and
#    `blindplay._despritify` renders it as `[Energy]`, which has a capital and
#    is not matched either.
#
# 2. IT MUST BE CLOSED. An opening tag comes out only where the same string
#    also carries its `[/tag]`, and that is not tidiness -- it is what keeps
#    this from laundering an internal id past the leak guard. `[pearl_barrage]`
#    is a bracketed lowercase token and it is a CARD ID; a blunt "strip every
#    bracketed word" fold would have deleted it silently and handed a blind
#    tester the sentence it was hiding in with the evidence removed. Unpaired,
#    it survives, `qa_packet.leaks` still sees it, and the screen still refuses.
#
# Only the TAGS come out; the words between them are part of the name and stay.
RICH_TEXT_TAG = re.compile(r"\[/?([a-z0-9_]+)(?:=[^\]]*)?\]")
_RICH_TEXT_CLOSE = re.compile(r"\[/([a-z0-9_]+)\]")


def strip_markup(value: Any) -> str:
    """`value` with the game's CLOSED rich-text tags removed, nothing else."""
    text = str(value or "")
    closed = {m.group(1) for m in _RICH_TEXT_CLOSE.finditer(text)}
    return RICH_TEXT_TAG.sub(
        lambda m: "" if m.group(1) in closed else m.group(0), text)


def card_key(raw: Any) -> str:
    """The wire's card id as `printed_cost_index` keys it (`EB-267`).

    `KLEEMOD-PROTO_KO_FLAME_DANCE` -> `PROTO_KO_FLAME_DANCE`. The mod prefix
    comes off because a plain `CardModel` stub ships without one
    (`KleeMod.cs:98`) and the two spellings name the same face; nothing else
    is folded, so two ids that differ still key differently. This is a key on
    the TOOL side and never reaches a page -- `_hand` reads it off the wire
    entry and copies only the number it found.
    """
    s = str(raw or "").strip().upper().replace("-", "_")
    for prefix in _MOD_ID_PREFIXES:
        if s.startswith(prefix):
            return s[len(prefix):]
    return s


def _class_key(src: str) -> str:
    """The first class declared in a C# file, as its `ModelId.Entry` spelling.

    `ProtoKoFlameDance` -> `PROTO_KO_FLAME_DANCE`. BaseLib derives the entry
    from the class name and the generator derives the class name from the
    sheet id, so this agrees with the `id=` the generated header prints for
    all 336 generated faces -- which is what
    `test_the_printed_cost_index_is_keyed_by_id` checks, rather than trusting
    it.
    """
    m = _CLASS_RE.search(src)
    if m is None:
        return ""
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", m.group(1))
    return re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name).upper()


@lru_cache(maxsize=4)
def _printed_cost_index_cached(repo: Path) -> tuple[tuple[str, int], ...]:
    index: dict[str, int] = {}
    root = repo / "klee-mod"
    if not root.is_dir():
        return ()
    for path in sorted(root.glob(_CARD_SOURCE_GLOB)):
        try:
            src = path.read_text(encoding="utf-8")
        except OSError:
            continue
        cost = _SHEET_COST_RE.search(src)
        if cost is None:
            continue
        # The FIRST class in the file. A modal card's file holds several and
        # only the outer one carries the sheet comment, so the first class is
        # the one that comment is about -- the same rule the title-keyed
        # version used, moved onto the key that is actually unique.
        key = _class_key(src)
        if key:
            index.setdefault(key, int(cost.group(1)))
    return tuple(sorted(index.items()))


def printed_cost_index(repo: Path | None = None) -> dict[str, int]:
    """`{card id: the cost printed on the shipped face}` (EB-186, EB-267).

    Keyed by `card_key`'s spelling of the wire's own card id, NOT by printed
    title: a prototype row may share a shipped card's name and carry a
    different price, and a title-keyed map answered the wrong one.

    A card the index has no row for gets NO note -- an absent number is
    silence, never a guess.
    """
    root = repo if repo is not None else Path(__file__).resolve().parents[1]
    return dict(_printed_cost_index_cached(root))


@lru_cache(maxsize=4)
def _printed_spark_index_cached(repo: Path) -> tuple[tuple[str, int], ...]:
    index: dict[str, int] = {}
    root = repo / "klee-mod"
    if not root.is_dir():
        return ()
    for path in sorted(root.glob(_CARD_SOURCE_GLOB)):
        try:
            src = path.read_text(encoding="utf-8")
        except OSError:
            continue
        price = _SPARK_PRICE_RE.search(src)
        if price is None:
            continue
        key = _class_key(src)
        if key:
            index.setdefault(key, int(price.group(1)))
    return tuple(sorted(index.items()))


def printed_spark_index(repo: Path | None = None) -> dict[str, int]:
    """`{card id: the Spark price printed on the face}` (`EB-282`).

    Same glob, same key and same silence rule as `printed_cost_index`: a card
    the index has no row for gets nothing, never a zero and never a guess.
    """
    root = repo if repo is not None else Path(__file__).resolve().parents[1]
    return dict(_printed_spark_index_cached(root))


# `EB-342`. THE CARDS THIS BUILD DEFINES NO UPGRADE FOR.
#
# `tools/gen_prototype_cards.UPGRADE_DEBT` is the register of them, and since
# `EB-315` emptied the overhaul half it is the Spark arm's alone -- which is
# exactly where the r7b act-3 seat's two silently-omitted cards live
# (`proto_powder_charge_spark`, `proto_shinobu_sanctifying_ring_*`).
#
# ONLY THE IDS CROSS. Each row's VALUE is register prose that names ruling and
# row numbers, which is precisely what may not reach a blind page; the page
# writes its own plain sentence and reads nothing from here but the key set.
# Parsed with a regex rather than imported for `printed_cost_index`'s reason
# one function up: the module that owns it reaches a sheet loader, and this
# index is read from a page that may not.
_UPGRADE_DEBT_BLOCK = re.compile(
    r"^UPGRADE_DEBT[^{]*\{(.*?)^\}", re.M | re.S)
_UPGRADE_DEBT_KEY = re.compile(r'^\s*"([a-z0-9_]+)"\s*:', re.M)


@lru_cache(maxsize=4)
def _no_upgrade_index_cached(repo: Path) -> tuple[str, ...]:
    src = repo / "tools" / "gen_prototype_cards.py"
    try:
        text = src.read_text(encoding="utf-8")
    except OSError:
        return ()
    block = _UPGRADE_DEBT_BLOCK.search(text)
    if block is None:
        return ()
    return tuple(sorted(card_key(k)
                        for k in _UPGRADE_DEBT_KEY.findall(block.group(1))))


def no_upgrade_index(repo: Path | None = None) -> frozenset[str]:
    """`{card id}` for every row this build defines no upgrade for (`EB-342`).

    Keyed the way `printed_cost_index` is -- `card_key`'s spelling of the
    wire's own id -- so a face on a screen looks up by the same handle. An
    empty set on a checkout with no `tools/` tree is silence, never a guess.
    """
    root = repo if repo is not None else Path(__file__).resolve().parents[1]
    return frozenset(_no_upgrade_index_cached(root))


# `EB-483`. THE FACE A CARD WOULD PRINT IF IT WERE UPGRADED.
#
# THE FIND (Kokomi r16 (c) 6). "The upgrade screen shows the current face,
# never the upgraded one. Thirteen cards, no previews. I upgraded Deep Current
# on a guess and found out it was 6 to 9 two fights later."
#
# THE UPGRADED FACE IS NOT ON THE WIRE. `BuildCardSelectState` serialises each
# grid card through `BuildCardInfo`, which prints `GetDescriptionForPile` --
# the card as it stands. The bridge CAN build the other one
# (`SafeGetCardUpgradePreviewDescription`, which clones and calls
# `UpgradeInternal`) but only the wiki endpoint asks it to, and adding a clone
# per card per poll to the singleplayer builder is not a change to make from
# this side of the line while `EB-489` is open.
#
# SO IT IS DERIVED, from the two things the CODEGEN already writes down: the
# description TEMPLATE in `Localization` and the delta in `OnUpgrade`. The
# template says where each number sits and what it is called; the delta says
# which name moves and by how much. Everything between the holes is literal
# text and is carried through untouched, so the upgraded face is the card's
# own sentence with its own numbers moved -- not a summary of the delta.
#
# THE MATCH IS AGAINST THE WIRE'S OWN PRINTED FACE, never against the
# template's base values, which is what makes the arithmetic the board's: the
# template is turned into a pattern, the pattern reads the numbers the screen
# is actually showing, and the delta is added to those. A face this module
# cannot match gets NO upgraded line -- an absent face is silence, and the one
# thing this page may never print is a guess.
#
# THE UPGRADE SCREEN ONLY, and that is a correctness bound rather than taste.
# A `Calculated*` hole is `base + extra * multiplier`, so on a board where the
# multiplier is live (Guest Cast, a Charge bank) a delta on `CalculationBase`
# moves the printed number by MORE than the delta. A Smith is out of combat,
# every multiplier is at rest, and the two are equal.
_LOC_DESCRIPTION_RE = re.compile(
    r'\("description",\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+)\)')
_CSHARP_LITERAL_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
_UPGRADE_DELTA_RE = re.compile(
    r"DynamicVars(?:\.([A-Za-z_][A-Za-z0-9_]*)|\[\"([A-Za-z_][A-Za-z0-9_]*)\"\])"
    r"\.UpgradeValueBy\((-?\d+(?:\.\d+)?)m\)")
#: One `{Name}` / `{Name:diff()}` / `{Name:plural:a|b}` hole. Deliberately
#: refuses a nested brace: `{IfUpgraded:show:{Encore:diff()} ...|}` is a hole
#: whose two arms are two different sentences, and a template carrying one is
#: skipped whole rather than half-rendered.
_HOLE_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([^{}]*))?\}")


def _loc_description(src: str) -> str:
    """The `("description", ...)` row of the FIRST `Localization` in a file."""
    m = _LOC_DESCRIPTION_RE.search(src)
    if m is None:
        return ""
    return "".join(_CSHARP_LITERAL_RE.findall(m.group(1))).replace('\\"', '"')


def _upgrade_deltas(src: str) -> dict[str, int]:
    """`{var name: delta}` off every `UpgradeValueBy` in a card's source."""
    out: dict[str, int] = {}
    for dotted, indexed, amount in _UPGRADE_DELTA_RE.findall(src):
        try:
            out[dotted or indexed] = int(float(amount))
        except ValueError:
            continue
    return out


def _hole_deltas(template: str, deltas: dict[str, int]) -> dict[str, int]:
    """The deltas re-keyed onto the HOLE names the template actually prints.

    A delta usually lands on the var it is named for. `CalculationBase` is the
    exception and the common one: it is the input to a `Calculated*` var, so
    the face prints `{CalculatedDamage:diff()}` while `OnUpgrade` moves
    `CalculationBase`. Resolved only where the template holds exactly ONE
    `Calculated*` hole -- two would be a card computing both numbers off one
    base, which the generator refuses to emit for that very reason.
    """
    holes = [m.group(1) for m in _HOLE_RE.finditer(template)]
    out: dict[str, int] = {}
    for name, delta in deltas.items():
        if name in holes:
            out[name] = delta
            continue
        if name == "CalculationBase":
            calculated = [h for h in holes if h.startswith("Calculated")]
            if len(set(calculated)) == 1:
                out[calculated[0]] = delta
                continue
        return {}          # a delta with nowhere to land: render nothing
    return out


def _plural_arm(spec: str, value: int) -> str:
    """SmartFormat's `plural:singular|plural`, resolved for `value`."""
    arms = spec.split("|")
    return arms[0] if value == 1 else arms[-1]


@lru_cache(maxsize=4)
def _upgraded_face_index_cached(
        repo: Path) -> tuple[tuple[str, tuple[str, tuple[tuple[str, int], ...]]], ...]:
    index: dict[str, tuple[str, tuple[tuple[str, int], ...]]] = {}
    root = repo / "klee-mod"
    if not root.is_dir():
        return ()
    for path in sorted(root.glob(_CARD_SOURCE_GLOB)):
        try:
            src = path.read_text(encoding="utf-8")
        except OSError:
            continue
        key = _class_key(src)
        if not key or key in index:
            continue
        template = strip_markup(_loc_description(src))
        if not template or "{IfUpgraded" in template:
            continue
        holes = _hole_deltas(template, _upgrade_deltas(src))
        if holes:
            index[key] = (template, tuple(sorted(holes.items())))
    return tuple(sorted(index.items()))


def upgraded_face(card_id: Any, printed: str,
                  repo: Path | None = None) -> str:
    """The face this card would print upgraded, or `""` where it cannot say.

    `printed` is the wire's own current description, markup already stripped by
    the bridge. See the block comment above for the whole argument, including
    why this is the UPGRADE SCREEN's answer and not the hand's.
    """
    root = repo if repo is not None else Path(__file__).resolve().parents[1]
    row = dict(_upgraded_face_index_cached(root)).get(card_key(card_id))
    if row is None:
        return ""
    template, holes = row
    deltas = dict(holes)

    # The template as a PATTERN over the printed face: literal text escaped,
    # every hole a group. A numeric hole reads the number the screen is
    # showing; a plural hole reads whichever arm it printed.
    pattern, pieces, at = [], [], 0
    for m in _HOLE_RE.finditer(template):
        pattern.append(re.escape(template[at:m.start()]))
        pieces.append(("literal", template[at:m.start()], ""))
        spec = m.group(2) or ""
        if spec.startswith("plural:"):
            arms = [re.escape(a) for a in spec[len("plural:"):].split("|")]
            pattern.append("(?:" + "|".join(arms) + ")")
        else:
            pattern.append(r"(-?\d+)")
        pieces.append(("hole", m.group(1), spec))
        at = m.end()
    pattern.append(re.escape(template[at:]))
    pieces.append(("literal", template[at:], ""))

    # SEARCHED, NOT FULL-MATCHED, and the surrounding text is kept verbatim:
    # the game APPENDS its auto-keyword sentences to a card's body ("Applies
    # Pyro.", "Retain."), so the template is the middle of the printed face
    # rather than the whole of it. A template whose literal text this build
    # has since reworded simply does not match, and the row prints nothing.
    face = strip_markup(printed).strip()
    hit = re.search("".join(pattern), face)
    if hit is None:
        return ""

    values: dict[str, int] = {}
    out: list[str] = []
    group = 0
    for kind, name, spec in pieces:
        if kind == "literal":
            out.append(name)
            continue
        if spec.startswith("plural:"):
            # Resolved off the number this same face prints, so a 1 -> 2 that
            # moves the word moves it here too.
            out.append(_plural_arm(spec[len("plural:"):], values.get(name, 2)))
            continue
        group += 1
        value = int(hit.group(group)) + deltas.get(name, 0)
        values[name] = value
        out.append(str(value))
    return face[:hit.start()] + "".join(out) + face[hit.end():]


# `EB-264`. THE WIRE'S UNPLAYABLE REASON IS AN ENUM NAME, AND A PLAYER CANNOT
# READ IT. `unplayable_reason` on a hand entry is `UnplayableReason.ToString()`
# (`McpMod.StateBuilder.cs:1324`), so the page printed
# `CANNOT BE PLAYED: BlockedByCardLogic` at a blind tester, who reported it as
# the least readable thing on the screen and could not tell it from
# `EnergyCostTooHigh`, which at least guesses. These are the plain sentences,
# keyed on the enum name folded to lower case.
#
# THE MAP IS NOT THE ONLY PATH, DELIBERATELY. A reason the wire spells as a
# SENTENCE -- anything carrying a space -- is kept verbatim, because the mod
# side is growing reasons of its own ("you have no Spark") and a page that
# mapped those would be overwriting the game's own words with ours. An enum
# name this map has never seen is rendered as its own words rather than
# dropped: a tester who reports `blocked by hook` has reported something a
# reader of this file can act on, and silence there would hide the next enum
# the same way this row's three were hidden.
UNPLAYABLE_REASONS: dict[str, str] = {
    "energycosttoohigh": "you do not have enough energy",
    "notenoughenergy": "you do not have enough energy",
    "starcosttoohigh": "you do not have enough Stars",
    "blockedbycardlogic": "this card's own rule is stopping you right now",
    "blockedbyhook": "something else on the board is stopping you right now",
    "unplayable": "this card cannot be played at all",
    "none": "",
}
_ENUM_TOKEN = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")


def unplayable_reason(raw: Any) -> str:
    """The game's refusal in words a player can read (`EB-264`).

    A `[Flags]` enum prints as `A, B`, so each part is read on its own.

    `EB-290`, AND THE TRUNCATION WAS OURS. A reason the mod writes as a
    SENTENCE has its own commas -- `KleeUnplayableReason.For` says *"you have
    no Spark, and this costs 1"* -- and splitting that at the comma and
    rejoining the halves with `"; "` is what put *"you have no Spark; and this
    costs 1"* on a blind page. The r4 Opus seat read the tail as a truncated
    sentence and filed it, which is exactly what a semicolon before a
    conjunction reads as. So the flags split is taken ONLY where every part is
    an enum token; anything else is the game's own words and is kept whole,
    punctuation included. A mixed string (an enum name beside a sentence) is
    not a shape either side emits -- `_card_face` reads
    `unplayable_reason_text` OR `unplayable_reason`, never both -- and is kept
    whole for the same reason: it is safer to print one of the game's words
    unrewritten than to shred a sentence at a comma that belongs to it.
    """
    text = _text(raw)
    if not text:
        return ""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not all(_ENUM_TOKEN.match(p) for p in parts):
        return text
    out: list[str] = []
    for part in parts:
        known = UNPLAYABLE_REASONS.get(part.lower())
        if known is not None:
            if known:
                out.append(known)
            continue
        spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", part)
        out.append(re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", spaced).lower())
    return "; ".join(out)


def _discounted(card: dict[str, Any]) -> bool:
    """Is this card being SHOWN cheaper than the cost printed on it?"""
    shown, printed = _text(card.get("cost")), card.get("printed_cost")
    return (isinstance(printed, int) and shown.isdigit()
            and int(shown) < printed)


def cost_label(card: dict[str, Any]) -> str:
    """The COST SLOT for one card, as the game paints it (`EB-282`).

    The game's cost slot shows the Spark badge on a Spark-priced card, so the
    page says the price in the same place and in the same words the keyword
    already uses. A card with no Spark price reads exactly as it always did --
    the rendered energy cost, or `-` when the wire sent none.

    A row priced in BOTH prints both, in the order the badge stacks them. No
    row is priced that way today; the branch is here because a page that
    silently dropped half a price is the defect this whole function exists to
    repair.
    """
    shown = _text(card.get("cost")) or "-"
    price = card.get("printed_spark")
    if not isinstance(price, int) or price <= 0:
        return shown
    sparks = f"{price} Spark" if price == 1 else f"{price} Sparks"
    return sparks if shown in ("0", "-") else f"{shown} and {sparks}"


def _spark_price(card: dict[str, Any]) -> int:
    price = card.get("printed_spark")
    return price if isinstance(price, int) and price > 0 else 0


def spark_discount_note(card: dict[str, Any]) -> str:
    """`EB-339`. WHAT A COST-TO-ZERO EFFECT DOES NOT COVER.

    WHAT THE SEAT SAW (`klee round 7b, opus-act2.md`,
    section (c), last bullet). `Vexing Puzzlebox` prints "It's free to play
    this turn"; the card it handed over arrived as `Powder Charge -- cost 1
    Spark`, with none of the "the cost printed on this card is X; it is showing
    Y here" line the energy cards get. The seat wrote the rule out for
    themselves -- "free apparently means free of ENERGY" -- which is a rule a
    page should not make a player derive from a card that silently did not
    work.

    AND THE REASON IS STRUCTURAL, not a display slip. A Spark price is an
    EFFECT (`op: spend_spark` at the head of the row), not a cost, so
    `printed_cost` is 0 on every Spark-priced row in the pool
    (`proto_ko_powder_charge`, `proto_ko_dig_in`, and the rest). A cost-to-zero
    effect moves the ENERGY cost from 0 to 0, `_discounted` is correctly False,
    and there was nothing on the wire for either page to notice.

    SO IT IS SAID WHENEVER THE ENERGY SLOT READS ZERO, which is exactly when a
    relic, a potion or a power can claim the card is free -- and not only while
    a discount happens to be running, because nothing on the wire says one is.
    The sentence is true either way, so a page carrying it cannot mislead; the
    page withholding it already did.
    """
    price = _spark_price(card)
    if not price:
        return ""
    shown = _text(card.get("cost"))
    if shown not in ("", "-", "0"):
        return ""
    sparks = f"{price} Spark" if price == 1 else f"{price} Sparks"
    return (f"Its {sparks} is a price, not an Energy cost: an effect that "
            f"makes a card free to play, or cuts its cost to 0, covers Energy "
            f"only, and the {sparks} is still spent.")


def cost_note(card: dict[str, Any]) -> str:
    """The one sentence a discounted card carries, and `EB-339`'s beside it.

    `""` when the card is neither discounted nor Spark-priced. Where both
    apply they are ONE line in the order the price is read: what the Energy
    slot is doing, then what the Spark slot is not.

    `EB-342`. THE FIRST HALF DID DUTY FOR TWO DIFFERENT FACTS. On a single r7b
    fight-15 screen `The Big One+` read *"The cost printed on this card is 3;
    it is showing 2 here"* -- a PERMANENT Smith upgrade -- and `Flame Dance`
    read *"The cost printed on this card is 1; it is showing 0 here"* -- a
    one-turn `Vexing Puzzlebox` discount that evaporates at end of turn.
    Identical phrasing for a property of the CARD and a property of THIS TURN,
    with the `(upgraded)` tag the only distinguisher and sitting in the title
    rather than beside the cost line being explained.

    The number the discount is measured against is the cost on the SHIPPED
    FACE (`printed_cost_index`, read off the card's own C# sheet row), so an
    upgraded copy showing less than its base is showing the upgrade and an
    un-upgraded one showing less is showing something on the board. That is
    the whole distinction, and it is read off `upgraded`, which the wire
    carries per card -- nothing here guesses at a duration the feed does not
    send, so the board half says where to look rather than how long it lasts.
    """
    parts: list[str] = []
    if _discounted(card):
        opening = (f"The cost printed on this card is {card['printed_cost']}; "
                   f"it is showing {_text(card['cost'])} here")
        parts.append(
            f"{opening}, because this copy is upgraded — that is permanent."
            if card.get("upgraded") else
            f"{opening}. This copy is not upgraded, so the cut is this turn's "
            f"board and not the card: it is what this card costs now, not "
            f"what it costs.")
    spark = spark_discount_note(card)
    if spark:
        parts.append(spark)
    return " ".join(parts)
def spark_note(powers: list[dict[str, Any]],
               hand: list[dict[str, Any]]) -> str:
    """The once-per-page Spark line (EB-186). `""` when nothing is discounted.

    Every clause is either the power's own printed text, quoted, or division
    performed on two numbers that text and the page both show. Nothing here
    knows what a Spark is for.
    """
    spark = next((p for p in powers
                  if _text(p.get("name")).lower() == _SPARK_TITLE), None)
    if spark is None or _int(spark.get("stacks")) <= 0:
        return ""
    discounted = [c for c in hand if _discounted(c)]
    if not discounted:
        return ""
    bank = _int(spark.get("stacks"))
    rule = _text(spark.get("text"))
    n = len(discounted)
    out = [f'Spark, and the costs below. Spark\'s own text reads: "{rule}"',
           f"Your bank is {bank}.",
           f"{n} card{'s' if n != 1 else ''} in your hand "
           f"{'are' if n != 1 else 'is'} shown at a cost LOWER than the cost "
           f"printed on the card; each of them says so on its own line."]
    m = _CONSUMES_RE.search(rule)
    each = int(m.group(1)) if m else 0
    if each > 0:
        covered = bank // each
        out.append(f"Playing one of them at the shown cost consumes {each}, "
                   f"so a bank of {bank} covers {covered} of the "
                   f"{n}; anything after that costs what its card prints.")
    return " ".join(out)


# ------------------------------------------------------------- the packet ---

def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# `EB-370`. A base-game LocString with no entry for the key it was asked for
# does not raise -- it prints the key itself, and two different call
# conventions on the mod/bridge side give it two different shapes. Neither
# names anything a player would recognise, and both read as a leak because
# they carry an internal table name (`monsters`, `relics`) or a mod-prefixed
# id (`KLEEMOD-FURINA`) -- found live, Kokomi round 9
# (`review/qa/kokomi-round-9-2026-09-04`): a dead monster's name in the
# morning-log reprint of a carried-out Plan (a `.ToString()` on the
# unresolved LocString, `KleeMod.Powers.KokomiPlan.EnemyName`), and a
# base-game relic's OFFERED title at an Ancient node (a `.GetFormattedText()`
# that found no registered per-character title variant for a relic that is
# only ever BORROWED, never owned, by a modded character's pool). The second
# one BRICKED the run: the leak guard was RIGHT to refuse a mod id on a relic
# face, so the fix belongs here, upstream of the guard, not in the guard.
#
#   LocString table monsters entry SLUDGE_SPINNER.name   (`.ToString()`)
#   relics.SEA_GLASS.KLEEMOD-FURINA.title                 (`.GetFormattedText()`)
#
# Both are unpacked to the one thing inside them a player would recognise --
# the game object's own id, humanised exactly as `label()` humanises any
# other id-shaped wire string. A per-character owner segment
# (`KLEEMOD-FURINA`) is dropped rather than shown: it names which modded
# character's pool happened to read the shared object first, not the object,
# so dropping it IS "the fallback to the base entry, no character variant"
# this repo's norms ask for. A string that does not match either shape --
# which is every string this module has ever printed before this row -- is
# untouched.
_LOCSTRING_TOSTRING = re.compile(r"^LocString table \S+ entry (?P<rest>\S+)$")
_LOCSTRING_KEY = re.compile(r"^[a-z][a-z_]*\.(?P<rest>[A-Z][A-Za-z0-9_.\-]*)$")


def _delocify(text: str) -> str:
    """`text`, with an unresolved base-game LocString's raw key humanised.

    Never a raw key: a shape this does not recognise passes through
    unchanged, and a shape it does recognise but cannot find an entry
    segment in (no dot, or nothing left after the trailing field) also
    passes through unchanged -- neither is invented text.
    """
    m = _LOCSTRING_TOSTRING.match(text) or _LOCSTRING_KEY.match(text)
    if not m:
        return text
    segments = m.group("rest").split(".")
    field = segments[-1] if len(segments) > 1 else None
    body = segments[:-1] if field else segments
    entry = next((s for s in body if not s.upper().startswith("KLEEMOD")), None)
    entry = entry or (body[0] if body else None)
    return label(entry) if entry else text


def _text(value: Any) -> str:
    return _delocify(" ".join(str(value or "").split()))


def label(raw: Any) -> str:
    """An id-shaped wire string as a PRINTED label.

    The wire spells a registered resource `KLEEMOD_ENCORE` and a power's
    `name` is sometimes its id rather than its Title. Neither may reach a
    blind packet as written -- the mod prefix is a design fact and a
    snake_case token is an id. Stripping the prefix and title-casing the rest
    is a rendering, not a lookup: this module still knows nothing about what
    the thing IS. `_text` is used for anything the game already printed.
    """
    s = str(raw or "").strip()
    for prefix in ("KLEEMOD_", "KLEEMOD-", "kleemod_", "kleemod-"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    s = s.replace("_", " ").replace("-", " ")
    return " ".join(w.capitalize() if w.isupper() or w.islower() else w
                    for w in s.split())


def _powers(blob: dict[str, Any]) -> list[dict[str, Any]]:
    """Printed power name, stack count and hover text. No power ids."""
    out = []
    for s in blob.get("status") or []:
        if not isinstance(s, dict):
            continue
        name = _text(s.get("title")) or label(s.get("name"))
        if not name:
            continue
        out.append({"name": name,
                    "stacks": _int(s.get("amount", s.get("stacks")), 0),
                    "text": _text(s.get("description"))})
    return out


def _relics(player: dict[str, Any]) -> list[dict[str, str]]:
    """Printed relic name and hover text. No relic ids, no counters invented.

    `EB-238`. The wire's relic row is `id`, `name`, `description`, `counter`,
    `keywords`; two of those are printed on the HUD and the rest are not.
    """
    out = []
    for r in player.get("relics") or []:
        if not isinstance(r, dict):
            continue
        name = _text(r.get("name")) or label(r.get("id"))
        if not name:
            continue
        row = {"name": name, "text": _text(r.get("description"))}
        if r.get("counter") is not None:
            row["counter"] = _text(r.get("counter"))
        out.append(row)
    return out


def _intent(blob: Any) -> dict[str, str]:
    """The telegraph as the game draws it: its label and its hover text.

    Read as printed and NOT interpreted. `understudy.adapter._intent` parses
    the same field into a tier0 intent script for the pilot; that parse is the
    falsifier's business and has no place in the blind packet, where the agent
    is meant to read the same icon a player reads.
    """
    if isinstance(blob, list):
        blob = blob[0] if blob else None
    if not isinstance(blob, dict):
        return {"label": "", "text": "", "kind": ""}
    return {"label": _text(blob.get("label")),
            "text": _text(blob.get("description")),
            "kind": _text(blob.get("title") or blob.get("type"))}


def _hand(state: dict[str, Any], loc: dict[str, str],
          costs: dict[str, int] | None = None,
          sparks: dict[str, int] | None = None) -> list[dict[str, Any]]:
    costs = costs or {}
    sparks = sparks or {}
    cards = []
    for entry in (state.get("player") or {}).get("hand") or []:
        if not isinstance(entry, dict):
            continue
        title = _text(entry.get("name"))
        desc = _text(entry.get("description"))
        source = "bridge"
        if not desc:
            desc = _text(loc.get(title, ""))
            source = "generated-cs (unresolved dynamic vars)" if desc \
                else "unavailable"
        cards.append({
            "title": title,
            "text": desc,
            "text_source": source,
            "cost": _text(entry.get("cost")),
            # EB-186. `None` where the shipped face gives no number.
            # EB-267: BY ID. The id is read here, on the tool side, and never
            # copied into the packet -- only the integer it found is.
            "printed_cost": costs.get(card_key(entry.get("id"))),
            # `EB-282`. The Spark half of the same price, read the same way.
            # `None` on every card that prints no Spark price, which is every
            # card outside the Spark rows.
            "printed_spark": sparks.get(card_key(entry.get("id"))),
            "upgraded": bool(entry.get("is_upgraded")),
            "playable": entry.get("can_play") is not False,
            # The game's own printed refusal, not ours.
            "unplayable_reason": _text(entry.get("unplayable_reason_text")
                                       or entry.get("unplayable_reason")),
        })
    return cards


def _enemies(state: dict[str, Any]) -> list[dict[str, Any]]:
    battle = state.get("battle")
    blobs = (battle.get("enemies") if isinstance(battle, dict)
             and isinstance(battle.get("enemies"), list)
             else state.get("enemies")) or []
    out = []
    for e in blobs:
        if not isinstance(e, dict):
            continue
        out.append({"name": _text(e.get("name")),
                    "hp": _int(e.get("hp")),
                    "max_hp": _int(e.get("max_hp", e.get("hp"))),
                    "block": _int(e.get("block")),
                    "intent": _intent(e.get("intents") or e.get("intent")),
                    "powers": _powers(e)})
    return out


def build(state: dict[str, Any], turn_id: str, *, repo: Path | None = None,
          disclosures: list[str] | None = None,
          forecast: list[str] | None = None) -> dict[str, Any]:
    """One blind packet from one live wire state. Raises on any leak.

    `turn_id` is the only caller-supplied string that reaches the packet, and
    it is scrubbed with everything else -- so a turn file named `eb149-foo`
    is refused here rather than teaching the agent a register id.
    """
    loc = localization_index(repo) if repo is not None else {}
    costs = printed_cost_index(repo)
    sparks = printed_spark_index(repo)
    p = state.get("player") or {}
    resources = p.get("resources")
    packet = {
        "turn_id": turn_id,
        "guardrail": PACKET_GUARDRAIL,
        "board": {
            "you": {
                "hp": _int(p.get("hp")),
                "max_hp": _int(p.get("max_hp")),
                "block": _int(p.get("block")),
                "energy": _int(p.get("energy")),
                # NON-ZERO ONLY. The wire reports every meter the mod has
                # REGISTERED, so a Kokomi board answers with Furina's
                # Spotlight and Fanfare counters sitting at zero -- and a
                # grader reading "Spotlight Mode: 0" on a board with no
                # Spotlight on it has been told something about the game that
                # this board does not print. The HUD shows a meter when it
                # holds something; so does the packet.
                "resources": ({label(k): _int(v) for k, v in resources.items()
                               if _int(v)}
                              if isinstance(resources, dict) else {}),
                "powers": _powers(p),
                # `EB-238`. THE RUN'S RELICS, ON THE STAGED PAGE.
                #
                # `KLEESPARK-BT1` §22.4 is why. Klee's starter relic
                # *Pounding Surprise* pays +1 Spark for every Bomb that
                # detonates; the row under test placed three Bombs for a
                # price of 3 Sparks; and on the replay the bank read
                # 3 -> 0 -> 3 inside one turn. The mode REFUNDED ITS OWN
                # PRICE in front of eight blind readers, none of whom could
                # see the relic that did it -- because this page printed no
                # relic at all. A registration cannot control what its own
                # page does not show.
                #
                # PRINTED NAME AND PRINTED HOVER TEXT, off the wire, and
                # nothing else: no id, no rarity, no pool, no sim hook. That
                # is the same quarantine every other line here keeps -- what
                # the player sees at the machine, and not one word the game
                # does not put on the screen.
                "relics": _relics(p),
            },
            "hand": _hand(state, loc, costs, sparks),
            "enemies": _enemies(state),
        },
        "disclosures": list(disclosures or []),
        # `EB-236` item (d) / the staged twin of `EB-229`. THE QUESTIONS A
        # REGISTRATION ASKS BEFORE THE LINE. Empty on every board that
        # registers none, which is every board written before this key
        # existed. See `render` for why they are printed FIRST.
        "forecast": [str(q) for q in (forecast or [])],
    }
    packet["board"]["spark_note"] = spark_note(packet["board"]["you"]["powers"],
                                               packet["board"]["hand"])
    assert_blind(packet)
    return packet


# ---------------------------------------------------------------- markdown --

def _render_card(c: dict[str, Any]) -> list[str]:
    head = f"### {c['title']}"
    if c["upgraded"]:
        head += " (upgraded)"
    lines = [head, "", f"- Cost: {cost_label(c)}",
             f"- {c['text'] or '(no printed text)'}"]
    note = cost_note(c)
    if note:
        lines.insert(3, f"- {note}")
    if not c["playable"]:
        # `EB-264`: the enum name becomes a sentence here, at the one place it
        # is printed, so the packet JSON keeps the wire's own word for a
        # falsifier to read and the PAGE carries the words a player can.
        why = unplayable_reason(c["unplayable_reason"])
        lines.append(f"- Cannot be played right now: "
                     f"{why or 'the game gives no reason'}")
    lines.append(f"- (card text read from: {c['text_source']})")
    lines.append("")
    return lines


def render(packet: dict[str, Any]) -> str:
    """The packet as the page an agent is handed. Same content as the JSON."""
    b = packet["board"]
    you = b["you"]
    out: list[str] = [f"# Staged turn `{packet['turn_id']}`", "",
                      packet["guardrail"], "",
                      "You are looking at one turn of a card battle, exactly "
                      "as the game prints it. Everything you are allowed to "
                      "know is on this page.", "",
                      "## You", "",
                      f"- HP {you['hp']}/{you['max_hp']}",
                      f"- Block {you['block']}",
                      f"- Energy {you['energy']}"]
    for name, amount in sorted(you["resources"].items()):
        out.append(f"- {name}: {amount}")
    for pw in you["powers"]:
        out.append(f"- {pw['name']} {pw['stacks']}"
                   + (f" — {pw['text']}" if pw["text"] else ""))
    # `EB-238`. Between the header and the hand, which is where the HUD keeps
    # it: a relic is on screen for the whole of a run, and a page that shows
    # one only where it is OFFERED has shown the reader the shop, not the
    # board. Absent where the run carries none, like every other block here.
    for r in you.get("relics") or []:
        out.append(f"- Relic — {r['name']}"
                   + (f" ({r['counter']})" if r.get("counter") else "")
                   + (f": {r['text']}" if r["text"] else ""))
    if packet.get("forecast"):
        # BEFORE THE HAND, AND THAT POSITION IS THE WHOLE POINT.
        #
        # `EB-229` found `KURAGEMEM002`'s `P1`, `P2` and `P4` UNREACHED not
        # because the display failed but because THE QUESTION WAS NEVER
        # ASKED: a reply schema of `command` and `thinking` lets a tester say
        # why it plays what it plays and never what it EXPECTS, and the
        # staged form's four questions are all past-tense. A forecast
        # collected after the line is a rationalisation.
        #
        # So a registration that wants one asks it here, at the top of the
        # page, in printed vocabulary, and the form carries one answer per
        # question. It is OPT-IN: a board that registers no forecast prints
        # no such block and its form is graded exactly as before.
        out += ["", "## Before you decide", "",
                "Answer these BEFORE you choose a line, and write the answers "
                "into your form's `forecast` list in this order. They are "
                "predictions, not questions about what you did:", ""]
        out += [f"{i}. {q}" for i, q in enumerate(packet["forecast"], 1)]
    out += ["", "## Your hand", ""]
    if b.get("spark_note"):
        out += [b["spark_note"], ""]
    for c in b["hand"]:
        out += _render_card(c)
    out += ["## The other side", ""]
    for e in b["enemies"]:
        out.append(f"### {e['name']}")
        out.append("")
        out.append(f"- HP {e['hp']}/{e['max_hp']}"
                   + (f", Block {e['block']}" if e["block"] else ""))
        intent = e["intent"]
        telegraph = ", ".join(x for x in (intent["kind"], intent["label"],
                                          intent["text"]) if x)
        out.append(f"- Intent: {telegraph or '(the game shows no intent)'}")
        for pw in e["powers"]:
            out.append(f"- {pw['name']} {pw['stacks']}"
                       + (f" — {pw['text']}" if pw["text"] else ""))
        out.append("")
    if packet["disclosures"]:
        out += ["## Disclosures", ""]
        out += [f"- {d}" for d in packet["disclosures"]]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def dumps(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=1, ensure_ascii=False) + "\n"
