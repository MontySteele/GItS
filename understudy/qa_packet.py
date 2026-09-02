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
    """
    text = _text(raw)
    if not text:
        return ""
    out: list[str] = []
    for part in (p.strip() for p in text.split(",")):
        if not part:
            continue
        if not _ENUM_TOKEN.match(part):
            out.append(part)                 # the wire's own sentence, kept
            continue
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


def cost_note(card: dict[str, Any]) -> str:
    """The one sentence a discounted card carries. `""` when it is not one."""
    if not _discounted(card):
        return ""
    return (f"The cost printed on this card is {card['printed_cost']}; it is "
            f"showing {_text(card['cost'])} here.")


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


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


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
          costs: dict[str, int] | None = None) -> list[dict[str, Any]]:
    costs = costs or {}
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
            "upgraded": bool(entry.get("is_upgraded")),
            "playable": entry.get("can_play") is not False,
            # The game's own printed refusal, not ours.
            "unplayable_reason": _text(entry.get("unplayable_reason")),
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
            "hand": _hand(state, loc, costs),
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
    lines = [head, "", f"- Cost: {c['cost'] or '-'}", f"- {c['text'] or '(no printed text)'}"]
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
