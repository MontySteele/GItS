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


def leaks(blob: Any) -> list[tuple[str, str, str]]:
    """`(rule, matched-text, the-string-it-was-in)` for every leak found."""
    found: list[tuple[str, str, str]] = []
    for s in _strings(blob):
        for rule, pattern in FORBIDDEN:
            m = pattern.search(s)
            if m:
                found.append((rule, m.group(0), s))
    return found


def assert_blind(blob: Any) -> None:
    bad = leaks(blob)
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


def _hand(state: dict[str, Any], loc: dict[str, str]) -> list[dict[str, Any]]:
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
          disclosures: list[str] | None = None) -> dict[str, Any]:
    """One blind packet from one live wire state. Raises on any leak.

    `turn_id` is the only caller-supplied string that reaches the packet, and
    it is scrubbed with everything else -- so a turn file named `eb149-foo`
    is refused here rather than teaching the agent a register id.
    """
    loc = localization_index(repo) if repo is not None else {}
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
            },
            "hand": _hand(state, loc),
            "enemies": _enemies(state),
        },
        "disclosures": list(disclosures or []),
    }
    assert_blind(packet)
    return packet


# ---------------------------------------------------------------- markdown --

def _render_card(c: dict[str, Any]) -> list[str]:
    head = f"### {c['title']}"
    if c["upgraded"]:
        head += " (upgraded)"
    lines = [head, "", f"- Cost: {c['cost'] or '-'}", f"- {c['text'] or '(no printed text)'}"]
    if not c["playable"]:
        lines.append(f"- Cannot be played right now: "
                     f"{c['unplayable_reason'] or 'the game gives no reason'}")
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
    out += ["", "## Your hand", ""]
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
