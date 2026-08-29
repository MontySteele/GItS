"""EB-167/EB-168: DESIGN-BLIND PLAY of any screen, and the seat that plays it.

`qa_packet.py` renders ONE staged combat turn design-blind. This module is the
same guarantee widened to every screen the wire can return -- map, rewards,
shop, rest, event, the three selection overlays, game over -- plus a command
grammar in player language, plus the smallest driver that lets an independent
model actually play through it.

WHAT IS DIFFERENT FROM `harness state`, AND WHY THIS FILE EXISTS AT ALL
-----------------------------------------------------------------------
`understudy/harness.py` renders a screen with `policy_v0`'s recommendation
printed beside it. That is exactly right for the Phase-0 divergence loop and
exactly wrong here: a tester who is shown what the sim would do is not reading
the board, and R217 E minted this row saying so in as many words. So this
module is built on `qa_packet`'s scrubber and on the title-resolution
convention `staged_turn.execute` and `naming` follow, and NEVER on `harness`.
The AST pin in `tier0/tests/test_understudy_blindplay.py` keeps it that way:
no `harness`, no `policy_v0`, no `policy_v1`, and nothing from `tier0` /
`tier05` -- which also means no `soak`, no `scenario` and no `adapter`, each of
which reaches a sheet loader transitively.

THREE INVARIANTS, ALL TESTED
----------------------------
  * **EVERY OBSERVATION IS SCRUBBED.** `observation()` copies field by field
    from an allowlist, exactly as `qa_packet.build` does, and the finished
    structure AND the rendered Markdown both go through
    `qa_packet.assert_blind`. A leak raises `PacketLeak` and the observation is
    not returned, let alone shown. The one exemption is the wire's own screen
    name (`qa_packet.leaks(..., allow=...)`), passed one token at a time, and
    it exists only so a refusal can say WHICH screen it refused.
  * **AN UNKNOWN SCREEN IS `TOOL-BLOCKED`, NEVER A HEURISTIC.** A `state_type`
    this module does not know, an overlay, a minigame, or a registered hazard
    event renders as `TOOL-BLOCKED: <state_type>` and the driver STOPS. There
    is no "well, press the first button" path anywhere in this file --
    `soak._mechanical_action` has one because a soak's job is to keep moving,
    and a blind tester's job is the opposite.
  * **NOTHING BUT PRINTED FACES CROSSES THE LINE.** No card ids, no entity
    ids, no policy score, no EV, no design tag, no seed, no run comparison.
    Ids exist on this side of the line only long enough to build the POST:
    a title is resolved to a hand INDEX at the moment of posting, one frame
    later than which it would mean a different card (`naming.py:14-17`).

THE COMMAND GRAMMAR IS THE WHOLE INTERFACE
------------------------------------------
    play "<title>" [on "<enemy>"]      end turn        choose "<name>"
    skip            go "<node>"        buy "<item>"    rest
    upgrade ["<title>"]                remove ["<title>"]
    use potion "<title>" [on "<enemy>"]                confirm        proceed

Every name in it is a name the screen printed. The game prints an upgraded
card's own `+`, and the fold keeps it, so `Coral Guard` and `Coral Guard+` are
simply two names. A title matching two cards with DIFFERENT printed faces is
refused as ambiguous rather than guessed at, and BOTH sides are then reachable:
`"<title> (upgraded)"` and `"<title> (not upgraded)"` filter the hits, on
either side of the title, so echoing the screen back verbatim works (EB-173, a
live deadlock: neither copy was playable). A title matching two identical faces takes
the first, because two copies of one card are interchangeable and refusing
there would make a duplicate unplayable. A card the game says cannot be played,
or an item the run cannot afford, is refused WITH THE GAME'S OWN REASON where
the wire gives one.

THE SEAT, AND WHAT IS SEALED (R217 A/C/G)
-----------------------------------------
`session` runs ONE `codex exec` thread per run (`codex exec resume <id>` after
the first turn) so the tester keeps one context across the whole Act, which is
the difference between a run report and eleven disconnected turn reports. The
seat is the same one `seat.py` builds -- same sandbox, same three-source
transcript guard, same identity fill -- and the AUTHOR'S OWN MODEL FAMILY IS
REFUSED as tester: independence is by family, not by fresh context.

Sealed record: `understudy/logs/blindplay/<session>/` (gitignored) holds the
transcript and the model's records verbatim; `review/qa/blindplay/<session>/`
holds the identity block and those same records, committed, under the R217 G
label -- subjective feedback from an independent model playing the real game.
Useful for iteration; not human validation, not balance evidence, not
approval. It never enters an Understudy report, a win-rate table or a
measurement register.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from understudy import bridge, qa_packet, report, seat

REPO = Path(__file__).resolve().parents[1]
LOG_ROOT = Path(__file__).resolve().parent / "logs" / "blindplay"
RECORD_ROOT = REPO / "review" / "qa" / "blindplay"
PROMPT_PATH = Path(__file__).resolve().parent / "blindplay_prompt.md"

# The disclaimer that rides on every observation, the transcript and the sealed
# record -- same reasoning as `qa_packet.PACKET_GUARDRAIL`: a caveat that lives
# outside the record is lost the moment two records are concatenated.
PLAY_GUARDRAIL = (
    "you are playing the real game through a tool that shows you only what "
    "the screen prints; nothing recorded here is a measurement, a comparison "
    "with any other run, or a judgement of whether the game is fun or good "
    "that anyone will treat as approval")

COMBAT_SCREENS = frozenset({"monster", "elite", "boss"})
SELECT_SCREENS = frozenset({"card_select", "hand_select"})

# Screens that exist and are deliberately NOT driven. Each is TOOL-BLOCKED
# with its own reason rather than lumped in with the unknown ones, because
# "this module has no grammar for a minigame" and "the wire returned a screen
# nobody has ever seen" are different findings for whoever reads the log.
UNDRIVEN_SCREENS = {
    "crystal_sphere": "a minigame with a click-a-cell interface; the command "
                      "grammar has no shape for it",
    "overlay": "the wire's own catch-all for an overlay it does not model, "
               "which is one of the two shapes a soft-lock takes",
    "unknown": "the wire could not name this screen",
}

# How long the driver rides out a TRANSITION before calling it a screen.
# `unknown` -- and a state with no `state_type` key at all -- is what the wire
# answers for the moment between leaving one room and entering the next, which
# is not a screen and must not be reported as one. `soak._settle_transient`
# learned this on the same wire and these are its numbers.
SETTLE_TRIES = 60
SETTLE_DELAY_S = 0.5

# EB-1. A REGISTER, NOT A HEURISTIC, and a deliberate SECOND COPY of
# `soak.HAZARD_EVENTS`. Importing soak here would pull `policy_v1` and through
# it every tier0 sheet loader into the design-blind module, which is the one
# import this file may not have. `test_understudy_blindplay` asserts this map
# covers every id soak registers, so the two cannot drift apart silently: the
# day soak adds a hazard, the test here goes red.
HAZARD_EVENTS = {
    "PUNCH_OFF": "entering this room spins the game's main thread on an "
                 "unbounded error loop. It is refused, not played.",
}
HAZARD_EVENT_TITLES = {"punch off": "PUNCH_OFF"}


class BlindPlayError(RuntimeError):
    """A command, a screen or a seat this module refuses to work with."""


class SeatBudgetExhausted(BlindPlayError):
    """The SEAT's own budget ran out -- somebody else's rate limit, not ours.

    Kept apart from every other seat failure because the two mean opposite
    things to whoever reads the record. `seat_refused` says the transcript
    guard bit or the model would not answer, and that is a finding. A usage
    limit says the session was cut off mid-run by an account quota, which is
    not a finding about anything: the honest record is how far it got, under
    its own termination reason, with the partial records kept.
    """


# The markers a usage limit reads as on the seat's stderr. Deliberately three
# spellings and the HTTP status: the wording is a third party's and moves, and
# a session that misfiles a quota stop as a refusal is a session that reads as
# a finding about the game.
_RATE_LIMIT_MARKERS = ("rate limit", "rate_limit", "usage limit",
                       "usage_limit", "429", "quota", "too many requests")


def _is_rate_limited(stderr_text: str) -> bool:
    low = str(stderr_text or "").casefold()
    return any(m in low for m in _RATE_LIMIT_MARKERS)


# ------------------------------------------------------------ small reads --

# The base game prints inline SPRITE TAGS in its own loc data -- Booming
# Conch's face is "...draw 2 additional cards and gain
# [silent_energy_icon.png]", and the game draws an energy pip where that tag
# sits. To the deliberately blunt snake_case rule that reads as an internal id,
# so the FIRST live screen of the first acceptance run -- Neow's boon list --
# was refused outright and no run could start.
#
# It is not a leak: the tag names an ICON THE PLAYER IS LOOKING AT, no card, no
# role and no ruling. So it is rendered rather than exempted, which is also the
# more honest render: a tester shown `[silent_energy_icon.png]` is being shown
# a filename, and a tester shown `[silent energy icon]` is being shown what the
# screen shows. Deliberately narrow -- a bracketed bare token with an image
# extension, and nothing else. Anything that is genuinely an id still refuses.
_SPRITE_TAG = re.compile(r"\[([A-Za-z0-9_]+)\.(?:png|jpg|jpeg|svg|webp)\]",
                         re.I)


def _despritify(blob: Any) -> Any:
    """Rewrite every sprite tag in a finished structure. Values only."""
    if isinstance(blob, str):
        return _SPRITE_TAG.sub(
            lambda m: "[" + m.group(1).replace("_", " ") + "]", blob)
    if isinstance(blob, dict):
        return {k: _despritify(v) for k, v in blob.items()}
    if isinstance(blob, list):
        return [_despritify(v) for v in blob]
    return blob


def _text(value: Any) -> str:
    return qa_packet._text(value)


def _int(value: Any, default: int = 0) -> int:
    return qa_packet._int(value, default)


def _label(value: Any) -> str:
    return qa_packet.label(value)


def _fold(text: Any) -> str:
    """One comparable key for a printed name.

    Case, punctuation and whitespace fold away; nothing else does. Deliberately
    NOT `scenario.card_key`, which also folds the mod's id prefix -- an id may
    not reach this side of the line at all, so a grammar that quietly accepted
    one would be a grammar a tester could type an id into.

    `EB-173`: `+` SURVIVES, because it is not punctuation here -- it is the
    game's own printed mark for an upgraded card, and folding it away made
    `Coral Guard` and `Coral Guard+` one key, which made both unplayable
    whenever a hand held one of each.
    """
    s = str(text or "").casefold()
    s = s.replace("—", " ").replace("–", " ").replace("-", " ")
    s = re.sub(r"[^a-z0-9+ ]+", " ", s)
    return " ".join(s.split())


def _screen(state: dict[str, Any]) -> str:
    return str(state.get("state_type") or "unknown")


def transient(state: dict[str, Any]) -> str:
    """Why this state is a MOMENT rather than a screen, or `""`.

    Three shapes, all of them the wire caught mid-stride:

      NO `state_type` KEY, and `state_type: "unknown"` -- the frame between
        leaving one room and entering the next. `soak._settle_transient`
        learned both on this wire; the reasoning is in `Session._settle`.

      A COMBAT SCREEN WITH `battle.is_play_phase` FALSE (`EB-175`) -- the
        turn has been handed back to the game and not yet handed on to the
        player. `end_turn` is asynchronous: `ExecuteEndTurn` calls
        `PlayerCmd.EndTurn` and answers `ok Ending turn` at once, and a GET
        55 ms later reads the round UNCHANGED, the hand already discarded to
        zero, energy still full, and `is_play_phase` false. Rendered as a
        screen that is exactly what a blind tester saw four times in one
        session: a playable turn with an empty hand. Its second `end turn`
        then landed on the REAL next turn a quarter-second later and spent
        it, which is why the rounds it recorded went 1 -> 3 -> 5. Nothing
        here posts a second `end_turn` on the tester's behalf; the read
        waits for the turn the game is already handing over.

    `is_play_phase` is checked for an explicit `False` and never for
    falsiness: a build whose battle block does not carry the key must not
    have every combat screen read as a transition.
    """
    if state.get("state_type") is None:
        return "the wire answered with no `state_type` key"
    if str(state.get("state_type")) == "unknown":
        return "the wire could not name this screen"
    if (str(state.get("state_type")) in COMBAT_SCREENS
            and _blob(state, "battle").get("is_play_phase") is False):
        return "the game has not handed the turn back to the player yet"
    return ""


def settle(state: dict[str, Any], wire: Any = bridge,
           tries: int = SETTLE_TRIES,
           delay: float = SETTLE_DELAY_S) -> dict[str, Any]:
    """Poll while the state is a transition; hand back whatever is there.

    Bounded on purpose, and the bound does not raise: a wire that really is
    stuck is reported as blocked by the caller, which is a better record than
    a read that never returns.
    """
    for _ in range(tries):
        if not transient(state):
            return state
        time.sleep(delay)
        state = wire.get_state()
    return state


def _player(state: dict[str, Any]) -> dict[str, Any]:
    p = state.get("player")
    return p if isinstance(p, dict) else {}


def _enemies(state: dict[str, Any]) -> list[dict[str, Any]]:
    battle = state.get("battle")
    if isinstance(battle, dict) and isinstance(battle.get("enemies"), list):
        blobs = battle["enemies"]
    else:
        blobs = state.get("enemies") or []
    return [e for e in blobs if isinstance(e, dict)]


def _entity_id(e: dict[str, Any]) -> str:
    return str(e.get("entity_id") or e.get("id") or "")


def _hand(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in (_player(state).get("hand") or []) if isinstance(c, dict)]


def _potions(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in (_player(state).get("potions") or [])
            if isinstance(p, dict)]


def _blob(state: dict[str, Any], key: str) -> dict[str, Any]:
    b = state.get(key)
    return b if isinstance(b, dict) else {}


def _listing(state: dict[str, Any], *keys: str) -> list[Any]:
    """The first non-empty list among `state[k]` and `state[k]['<inner>']`."""
    for key in keys:
        if "." in key:
            outer, inner = key.split(".", 1)
            value = _blob(state, outer).get(inner)
        else:
            value = state.get(key)
        if isinstance(value, list) and value:
            return value
    return []


def _hazard(state: dict[str, Any]) -> tuple[str, str] | None:
    """`(id, why)` when this event is on the hazard register, else `None`.

    Matched on the wire id first and the display title second -- the same
    read-by-id-then-by-name shape `soak._hazard_event` uses, and for the same
    reason: a title is loc data that a wording pass moves, and a screen this
    tool must not drive is worth catching twice.
    """
    if _screen(state) != "event":
        return None
    ev = _blob(state, "event")
    ident = str(ev.get("event_id") or "").strip().upper()
    if ident in HAZARD_EVENTS:
        return ident, HAZARD_EVENTS[ident]
    by_title = HAZARD_EVENT_TITLES.get(_text(ev.get("event_name")).lower())
    if by_title:
        return by_title, HAZARD_EVENTS.get(by_title, "on the hazard register")
    return None


# ------------------------------------------------------- printed fragments --

def _card_face(entry: dict[str, Any]) -> dict[str, Any]:
    """One card as the game prints it. Field by field, never spread.

    `keywords` is included because the live wire resolves a keyword's text with
    the board's numbers in it (`+1 damage per 2 Charge you hold. You hold 8
    Charge: ...`), which is part of the face a player is reading. `id`,
    `target_type` and `index` are read on the TOOL side and never copied here.
    """
    kws = []
    for k in entry.get("keywords") or []:
        if isinstance(k, dict) and _text(k.get("name")):
            kws.append({"name": _text(k.get("name")),
                        "text": _text(k.get("description"))})
    return {
        "title": _text(entry.get("name")),
        "text": _text(entry.get("description")),
        "cost": _text(entry.get("cost")),
        "kind": _text(entry.get("type")),
        "upgraded": bool(entry.get("is_upgraded") or entry.get("upgraded")),
        "keywords": kws,
        "playable": entry.get("can_play") is not False,
        "unplayable_reason": _text(entry.get("unplayable_reason")),
    }


def _named_option(entry: Any) -> dict[str, Any]:
    """One printed option -- a rest choice, a reward, a relic, a menu button.

    A wire option is sometimes a bare string and sometimes a dict under one of
    half a dozen key spellings; every one of them is a PRINTED label, so all of
    them are read and the first that answers wins. A label that arrives
    id-shaped goes through `qa_packet.label`, which strips the mod prefix and
    title-cases the rest -- a rendering, not a lookup.
    """
    if not isinstance(entry, dict):
        return {"name": _label(entry), "text": "", "enabled": True}
    name = ""
    for key in ("name", "title", "label", "display_name"):
        if _text(entry.get(key)):
            name = _text(entry.get(key))
            break
    if not name:
        for key in ("type", "kind", "room_type"):
            if entry.get(key):
                name = _label(entry.get(key))
                break
    enabled = True
    for key in ("is_enabled", "enabled"):
        if entry.get(key) is False:
            enabled = False
    if entry.get("is_locked"):
        enabled = False
    return {
        "name": name,
        "text": _text(entry.get("description") or entry.get("body")
                      or entry.get("text")),
        "enabled": enabled,
        "price": _int(entry.get("price", entry.get("cost")), 0)
        if entry.get("price") is not None or entry.get("cost") is not None
        else None,
    }


def _powers(blob: dict[str, Any]) -> list[dict[str, Any]]:
    return qa_packet._powers(blob)


def _intent(blob: Any) -> dict[str, str]:
    return qa_packet._intent(blob)


# ------------------------------------------------------------ observations --

def _combat(state: dict[str, Any]) -> dict[str, Any]:
    p = _player(state)
    resources = p.get("resources")
    battle = _blob(state, "battle")
    return {
        "you": {
            "hp": _int(p.get("hp")), "max_hp": _int(p.get("max_hp")),
            "block": _int(p.get("block")), "energy": _int(p.get("energy")),
            "max_energy": _int(p.get("max_energy")),
            # NON-ZERO ONLY, for `qa_packet.build`'s reason: the wire reports
            # every meter the mod REGISTERED, so a board with no Spotlight on
            # it would otherwise print "Spotlight Mode: 0" and teach the tester
            # something this screen does not show.
            "meters": ({_label(k): _int(v) for k, v in resources.items()
                        if _int(v)} if isinstance(resources, dict) else {}),
            "powers": _powers(p),
            "potions": [{"title": _text(x.get("name")),
                         "text": _text(x.get("description"))}
                        for x in _potions(state)],
        },
        "round": _int(battle.get("round")),
        "hand": [_card_face(c) for c in _hand(state)],
        "piles": {"draw": _int(p.get("draw_pile_count")),
                  "discard": _int(p.get("discard_pile_count")),
                  "exhaust": _int(p.get("exhaust_pile_count"))},
        "enemies": [{"name": _text(e.get("name")),
                     "hp": _int(e.get("hp")),
                     "max_hp": _int(e.get("max_hp", e.get("hp"))),
                     "block": _int(e.get("block")),
                     "intent": _intent(e.get("intents") or e.get("intent")),
                     "powers": _powers(e)} for e in _enemies(state)],
    }


def _map_nodes(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "map.next_options", "next_options")


def _map_options(state: dict[str, Any]) -> list[dict[str, Any]]:
    """The reachable nodes, by PRINTED type, each with a path number.

    The number is not decoration. The wire names a node by its room type only,
    so a fork offering two fights offers two options both called `Monster` --
    and a grammar that resolves by printed name would either refuse the move or
    guess which fork. Numbering them by the order the wire lists them makes
    every option nameable without teaching the tester a coordinate, an id or
    anything about what is down either path.
    """
    nodes = [_named_option(n) for n in _map_nodes(state)]
    for i, o in enumerate(nodes, 1):
        o["name"] = f"{o['name'] or 'Path'} (path {i})"
    return nodes


def _bundle_cards(bundle: Any) -> list[dict[str, Any]]:
    """The cards inside one bundle entry, in the order the wire lists them."""
    if not isinstance(bundle, dict):
        return []
    return [c for c in (bundle.get("cards") or []) if isinstance(c, dict)]


def _screen_cards(state: dict[str, Any]) -> list[dict[str, Any]]:
    """The cards the CURRENT screen is offering, in POST index order."""
    st = _screen(state)
    if st == "card_reward":
        entries = _listing(state, "card_reward.cards", "cards")
    elif st in SELECT_SCREENS:
        entries = _listing(state, f"{st}.cards")
        if not entries and st == "hand_select":
            entries = _hand(state)
    elif st == "bundle_select":
        entries = _listing(state, "bundle_select.bundles",
                           "bundle_select.cards", "bundles")
    else:
        entries = []
    return [e for e in entries if isinstance(e, dict)]


def _shop_items(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in _listing(state, "items", "shop.items")
            if isinstance(i, dict)]


def _rest_options(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "rest_site.options", "options")


def _event_options(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "event.options", "options")


def _reward_items(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "rewards.items", "rewards")


def _relic_options(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "relics", "options")


def observation(state: dict[str, Any]) -> dict[str, Any]:
    """One screen, design-blind, field by field. Raises `PacketLeak` on a leak.

    Returns a structure with a `blocked` string that is empty when the screen
    can be played and carries the reason when it cannot. Callers must check it:
    a blocked screen has no `commands`, and the driver stops rather than
    inventing one.
    """
    st = _screen(state)
    obs: dict[str, Any] = {
        "state_type": st,
        "guardrail": PLAY_GUARDRAIL,
        "blocked": "",
        "screen": "",
        "commands": [],
    }
    hazard = _hazard(state)

    if hazard is not None:
        obs["screen"] = "hazard"
        obs["blocked"] = hazard[1]
    elif st in UNDRIVEN_SCREENS:
        obs["screen"] = "undriven"
        obs["blocked"] = UNDRIVEN_SCREENS[st]
    elif st in COMBAT_SCREENS:
        obs["screen"] = "combat"
        obs["combat"] = _combat(state)
        obs["commands"] = ['play "<card title>" [on "<enemy>"]',
                           'use potion "<potion>" [on "<enemy>"]',
                           "end turn"]
    elif st == "map":
        obs["screen"] = "map"
        obs["nodes"] = _map_options(state)
        obs["commands"] = ['go "<node>"']
    elif st == "card_reward":
        blob = _blob(state, "card_reward")
        obs["screen"] = "card_reward"
        obs["prompt"] = _text(blob.get("prompt")) or "Add a card to your deck."
        obs["offers"] = [_card_face(c) for c in _screen_cards(state)]
        obs["can_skip"] = blob.get("can_skip") is not False
        obs["commands"] = ['choose "<card title>"', "skip"]
    elif st in SELECT_SCREENS:
        blob = _blob(state, st)
        obs["screen"] = "card_select"
        obs["prompt"] = _text(blob.get("prompt")) or "Choose a card."
        obs["offers"] = [_card_face(c) for c in _screen_cards(state)]
        obs["can_confirm"] = bool(blob.get("can_confirm"))
        obs["can_skip"] = bool(blob.get("can_skip") or blob.get("can_cancel"))
        obs["commands"] = ['choose "<card title>"', "confirm", "skip"]
    elif st == "bundle_select":
        # `EB-173`: A BUNDLE HAS NO NAME, and asking for one printed
        # `- **(unnamed)**` twice, on a screen whose only verb is
        # `choose "<bundle>"`. Nothing on it could be named, `confirm` before a
        # selection is an error the game just repeats, and a live session sat
        # there answering `confirm` until its action budget ran out. The wire
        # gives each bundle an index and a LIST OF CARDS; the cards have
        # printed titles, so the bundle is named by what is in it -- which is
        # also how a player at the screen would say it out loud. No id and no
        # invented label: every word below is one the game printed.
        blob = _blob(state, "bundle_select")
        obs["screen"] = "bundle_select"
        obs["prompt"] = _text(blob.get("prompt")) or "Choose a bundle."
        obs["offers"] = [{"cards": [_card_face(c) for c in _bundle_cards(b)]}
                         for b in _screen_cards(state)]
        obs["can_confirm"] = bool(blob.get("preview_showing"))
        obs["commands"] = ['choose "<any card title in the bundle you want>"',
                           "confirm"]
    elif st in ("shop", "fake_merchant"):
        obs["screen"] = "shop"
        obs["gold"] = _int(_player(state).get("gold"))
        obs["items"] = [_named_option(i) for i in _shop_items(state)]
        obs["commands"] = ['buy "<item>"', "proceed"]
    elif st == "rest_site":
        obs["screen"] = "rest_site"
        obs["options"] = [_named_option(o) for o in _rest_options(state)]
        obs["hp"] = _int(_player(state).get("hp"))
        obs["max_hp"] = _int(_player(state).get("max_hp"))
        obs["commands"] = ['choose "<option>"', "rest", "upgrade", "remove",
                           "proceed"]
    elif st == "event":
        ev = _blob(state, "event")
        obs["screen"] = "event"
        obs["title"] = _text(ev.get("event_name"))
        obs["text"] = _text(ev.get("body") or ev.get("text")
                            or ev.get("description"))
        obs["in_dialogue"] = bool(ev.get("in_dialogue"))
        obs["options"] = [_named_option(o) for o in _event_options(state)]
        obs["commands"] = ['choose "<option>"', "proceed"]
    elif st == "rewards":
        obs["screen"] = "rewards"
        obs["items"] = [_named_option(r) for r in _reward_items(state)]
        obs["commands"] = ['choose "<reward>"', "proceed"]
    elif st in ("treasure", "relic_select"):
        obs["screen"] = st
        obs["items"] = [_named_option(r) for r in _relic_options(state)]
        obs["commands"] = ['choose "<relic>"'] + (
            ["skip"] if st == "relic_select" else ["proceed"])
    elif st == "game_over":
        blob = _blob(state, "game_over")
        obs["screen"] = "game_over"
        obs["result"] = _text(blob.get("result") or blob.get("outcome"))
        obs["floor"] = _int(_blob(state, "run").get("floor"))
        obs["blocked"] = "the run is over; there is nothing left to play"
    elif st == "menu":
        obs["screen"] = "menu"
        obs["blocked"] = ("this is a menu, not a play screen. Start the run "
                          "before handing the seat the controls.")
    else:
        obs["screen"] = "unknown"
        obs["blocked"] = "this tool has never seen this screen"

    # Sprite tags are rewritten HERE, at the boundary, rather than in each of
    # the dozen readers that could carry one: the wire prints them in card
    # faces, relic faces, keyword bodies, event options and intent labels
    # alike, and a rule applied in one reader is a rule that will be missing
    # from the next one somebody adds.
    obs = _despritify(obs)

    # The wire's own screen name is the ONE token exempted from the snake_case
    # rule, and only because a refusal has to be able to name what it refused.
    #
    # `EB-176`, FOUND LIVE. BOTH names are exempt, because there are two and
    # they are not always the same string: `st` is what the WIRE called the
    # screen, `obs["screen"]` is what this tool calls it, and the branches
    # above deliberately fold several wire names onto one tool name --
    # `hand_select` renders as `card_select`. Exempting only `st` meant a live
    # `hand_select` wrote the un-exempt token `card_select` into its own
    # observation and the blindness assertion killed the session on a screen
    # that had leaked nothing. Both are screen vocabulary: neither names a
    # card, a role or a ruling, which is the test the exemption exists for.
    qa_packet.assert_blind(obs, allow={st, obs["screen"]})
    return obs


# ----------------------------------------------------------------- render --

def _render_card(c: dict[str, Any], bullet: str = "-") -> list[str]:
    head = f"{bullet} **{c['title']}**"
    if c["upgraded"]:
        head += " (upgraded)"
    bits = [b for b in (f"cost {c['cost']}" if c["cost"] else "",
                        c["kind"].lower() if c["kind"] else "") if b]
    if bits:
        head += f" — {', '.join(bits)}"
    out = [head, f"    {c['text'] or '(no printed text)'}"]
    for k in c["keywords"]:
        out.append(f"    *{k['name']}* — {k['text']}" if k["text"]
                   else f"    *{k['name']}*")
    if not c["playable"]:
        out.append("    CANNOT BE PLAYED: "
                   + (c["unplayable_reason"] or "the game gives no reason"))
    return out


def _render_options(items: list[dict[str, Any]], bullet: str = "-") -> list[str]:
    out = []
    for o in items:
        line = f"{bullet} **{o['name'] or '(unnamed)'}**"
        if o.get("price") is not None:
            line += f" — {o['price']} gold"
        if not o.get("enabled", True):
            line += " (not available)"
        out.append(line)
        if o.get("text"):
            out.append(f"    {o['text']}")
    return out


def render(obs: dict[str, Any]) -> str:
    """The observation as the page the tester is handed. Same content."""
    st = obs["state_type"]
    if obs["blocked"]:
        body = [f"TOOL-BLOCKED: {st}", "", obs["blocked"]]
        if obs["screen"] == "game_over":
            body += ["", f"The run ended on floor {obs['floor']}"
                         + (f": {obs['result']}" if obs["result"] else ".")]
        text = "\n".join(body) + "\n"
        qa_packet.assert_blind(text, allow={st})
        return text

    out: list[str] = []
    if obs["screen"] == "combat":
        c = obs["combat"]
        you = c["you"]
        out += [f"# Battle — round {c['round']}", "",
                f"- HP {you['hp']}/{you['max_hp']}",
                f"- Block {you['block']}",
                f"- Energy {you['energy']}/{you['max_energy']}"]
        for name, amount in sorted(you["meters"].items()):
            out.append(f"- {name}: {amount}")
        for pw in you["powers"]:
            out.append(f"- {pw['name']} {pw['stacks']}"
                       + (f" — {pw['text']}" if pw["text"] else ""))
        out.append(f"- Piles: {c['piles']['draw']} in the draw pile, "
                   f"{c['piles']['discard']} discarded, "
                   f"{c['piles']['exhaust']} exhausted")
        if you["potions"]:
            out += ["", "## Potions", ""]
            for p in you["potions"]:
                out.append(f"- **{p['title']}** — {p['text']}" if p["text"]
                           else f"- **{p['title']}**")
        out += ["", "## Your hand", ""]
        for card in c["hand"]:
            out += _render_card(card)
        if not c["hand"]:
            out.append("- (your hand is empty)")
        out += ["", "## The other side", ""]
        for e in c["enemies"]:
            line = f"- **{e['name']}** — HP {e['hp']}/{e['max_hp']}"
            if e["block"]:
                line += f", Block {e['block']}"
            out.append(line)
            telegraph = ", ".join(x for x in (e["intent"]["kind"],
                                              e["intent"]["label"],
                                              e["intent"]["text"]) if x)
            out.append(f"    Intent: {telegraph or '(no intent shown)'}")
            for pw in e["powers"]:
                out.append(f"    {pw['name']} {pw['stacks']}"
                           + (f" — {pw['text']}" if pw["text"] else ""))
    elif obs["screen"] == "map":
        out += ["# The map", "",
                "Where you can go next:", ""] + _render_options(obs["nodes"])
    elif obs["screen"] in ("card_reward", "card_select"):
        out += [f"# {obs['prompt']}", ""]
        for card in obs["offers"]:
            out += _render_card(card)
        if obs["screen"] == "card_select":
            out += ["", f"Confirm is {'available' if obs['can_confirm'] else 'not available'}."]
        if obs.get("can_skip"):
            out += ["", "You may skip this."]
    elif obs["screen"] == "bundle_select":
        out += [f"# {obs['prompt']}", ""]
        for offer in obs["offers"]:
            titles = ", ".join(c["title"] for c in offer["cards"]
                               if c["title"])
            out += [f"## A bundle of: {titles or '(nothing printed)'}", ""]
            for card in offer["cards"]:
                out += _render_card(card)
            out.append("")
    elif obs["screen"] == "shop":
        out += ["# The shop", "", f"You have {obs['gold']} gold.", "",
                "On the shelves:", ""] + _render_options(obs["items"])
    elif obs["screen"] == "rest_site":
        out += ["# A place to rest", "",
                f"HP {obs['hp']}/{obs['max_hp']}", ""] \
            + _render_options(obs["options"])
    elif obs["screen"] == "event":
        out += [f"# {obs['title'] or 'Something happens'}", ""]
        if obs["text"]:
            out += [obs["text"], ""]
        if obs["in_dialogue"]:
            out += ["(the scene is still being told; say `proceed`)", ""]
        out += _render_options(obs["options"])
    elif obs["screen"] in ("rewards", "treasure", "relic_select"):
        titles = {"rewards": "# What the fight left behind",
                  "treasure": "# An open chest",
                  "relic_select": "# Choose one"}
        out += [titles[obs["screen"]], ""] + _render_options(obs["items"])
    else:                                                # pragma: no cover
        raise BlindPlayError(f"no renderer for screen {obs['screen']!r}")

    out += ["", "## What you can say", ""]
    out += [f"- `{c}`" for c in obs["commands"]]
    out += ["", obs["guardrail"], ""]
    text = "\n".join(out).rstrip() + "\n"
    qa_packet.assert_blind(text, allow={st})
    return text


def observe(state: dict[str, Any]) -> str:
    """A design-blind Markdown render of any screen the wire can return."""
    return render(observation(state))


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------- grammar ---

_QUOTED = re.compile(r'"([^"]*)"|“([^”]*)”')

VERBS = ("play", "end turn", "choose", "skip", "go", "buy", "rest",
         "upgrade", "remove", "use potion", "confirm", "proceed")


@dataclass
class Command:
    verb: str
    names: list[str] = field(default_factory=list)
    raw: str = ""

    @property
    def name(self) -> str:
        return self.names[0] if self.names else ""

    @property
    def target(self) -> str:
        return self.names[1] if len(self.names) > 1 else ""


def parse_command(text: str) -> Command:
    """One line of player language, or `BlindPlayError`.

    Quotes are the grammar's only structure and they are required around every
    name: a screen prints titles with `on`, `and` and `choose` inside them, and
    a parser that split on words would resolve half a card. Curly quotes are
    read too -- a model that types them is not making a different request.
    """
    raw = " ".join(str(text or "").split())
    if not raw:
        raise BlindPlayError("empty command")
    names = [(a or b) for a, b in _QUOTED.findall(raw)]
    head = _QUOTED.sub("", raw).strip().casefold()
    head = " ".join(head.split())
    head = head.rstrip(".")
    if head.startswith("use potion") or head.startswith("use the potion"):
        verb = "use potion"
    elif head.startswith("end turn"):
        verb = "end turn"
    else:
        verb = head.split(" ")[0] if head else ""
    if verb not in VERBS:
        raise BlindPlayError(
            f"{raw!r} is not a command. The ones that exist are: "
            + ", ".join(VERBS))
    if verb in ("play", "go", "buy") and not names:
        raise BlindPlayError(f"`{verb}` needs a name in quotes")
    if verb == "choose" and not names:
        raise BlindPlayError("`choose` needs a name in quotes")
    return Command(verb=verb, names=names, raw=raw)


# ------------------------------------------------------------- resolution --

@dataclass
class Resolution:
    """What a command means against the state it was typed at.

    `post` is the wire body and is the ONLY place an id lives; `printed` is the
    same decision in the names the screen used, and is what may be echoed back
    to the tester.
    """
    ok: bool
    verb: str = ""
    post: dict[str, Any] | None = None
    printed: dict[str, Any] = field(default_factory=dict)
    refusal: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "verb": self.verb, "post": self.post,
                "printed": self.printed, "refusal": self.refusal}


def _refuse(why: str) -> Resolution:
    return Resolution(ok=False, refusal=why)


# `EB-173`: the qualifier the refusal advertises, and the resolver now honours.
# Accepted on either side of the title so a tester who echoes the screen back
# ("Coral Guard+ (upgraded)") is understood, and negatable so the BASE copy is
# reachable too -- a disambiguator that can only ever pick one of the two
# leaves the other unplayable, which is the defect this exists to close.
_QUALIFIER = re.compile(r"\s*\((not\s+)?upgraded\)\s*", re.I)


def _split_qualifier(name: str) -> tuple[str, bool | None]:
    """`(title without the qualifier, wanted upgrade state or None)`."""
    m = _QUALIFIER.search(name)
    if not m:
        return name, None
    return (name[:m.start()] + name[m.end():]).strip(), not m.group(1)


def _is_upgraded(entry: dict[str, Any]) -> bool:
    return bool(entry.get("is_upgraded") or entry.get("upgraded"))


def _match(entries: list[dict[str, Any]], name: str, *,
           key: Callable[[dict[str, Any]], str],
           face: Callable[[dict[str, Any]], str] | None = None
           ) -> tuple[int, str]:
    """`(index, refusal)` for `name` among `entries`, by PRINTED name only.

    Exact fold first, unique substring second. Two entries whose printed FACE
    is identical are interchangeable and the first is taken -- refusing there
    would make a second copy of a card unplayable, which is not an ambiguity a
    player experiences. Two entries that print the same title with different
    faces (a base and an upgraded copy) ARE ambiguous, and the refusal says how
    to disambiguate rather than guessing.

    `EB-173`, FOUND LIVE AND FIXED HERE. `_fold` strips punctuation, which is
    right for apostrophes and dashes and WRONG for the `+` the game itself
    appends to an upgraded title: `Coral Guard` and `Coral Guard+` folded to
    the same key, so with both in hand every naming of either was ambiguous --
    and the refusal's advice, `"(upgraded)"`, was documented in the grammar and
    implemented nowhere, so the escape hatch answered "nothing here is called
    that". NEITHER copy could be played. A blind session hit it on its fifth
    combat round and died against the refusal limit. Two halves to the fix:
    the qualifier is now PARSED and filters the hits (with `(not upgraded)`
    for the other side), and `+` survives the fold as a distinguishing mark,
    so the two titles are simply different names and the common case never
    reaches the ambiguity arm at all.
    """
    name, want_upgraded = _split_qualifier(name)
    want = _fold(name)
    if not want:
        return -1, "no name given"
    exact = [i for i, e in enumerate(entries) if _fold(key(e)) == want]
    loose = [i for i, e in enumerate(entries) if want in _fold(key(e))]
    hits = exact or loose
    if want_upgraded is not None:
        def _wanted(idx: list[int]) -> list[int]:
            return [i for i in idx if _is_upgraded(entries[i]) == want_upgraded]
        # Widen to the substring pass when the qualifier empties the exact
        # one: `Coral Guard (upgraded)` names the `+` copy exactly, and its
        # title is not the string the tester typed.
        narrowed = _wanted(exact) or _wanted(loose)
        if not narrowed and hits:
            state = "upgraded" if want_upgraded else "un-upgraded"
            return -1, (f"nothing here called {name!r} is {state}. "
                        f"What is on the screen: "
                        + ", ".join(sorted({key(entries[i]) for i in hits})))
        hits = narrowed
    if not hits:
        offered = ", ".join(sorted({key(e) for e in entries if key(e)}))
        return -1, (f"nothing here is called {name!r}. "
                    f"What is on the screen: {offered or '(nothing)'}")
    if len(hits) > 1 and face is not None:
        faces = {face(entries[i]) for i in hits}
        if len(faces) > 1:
            return -1, (f"{name!r} matches more than one different thing on "
                        f"this screen; name it exactly, or add "
                        f"\"(upgraded)\" / \"(not upgraded)\" to pick one")
    elif len(hits) > 1:
        names = sorted({key(entries[i]) for i in hits})
        if len(names) > 1:
            return -1, (f"{name!r} matches {len(names)} different things "
                        f"({', '.join(names)}); name one exactly")
    return hits[0], ""


def _match_bundle(entries: list[dict[str, Any]], name: str
                  ) -> tuple[int, str]:
    """`(index, refusal)` for the bundle holding a card printed `name`.

    `EB-173`. Exact title first, unique substring second -- `_match`'s order,
    on a set of names per entry instead of one. A title that appears in TWO
    bundles is refused rather than guessed at: which bundle the tester meant is
    exactly the question, and the other cards are how they would say it.
    """
    name, _ = _split_qualifier(name)
    want = _fold(name)
    if not want:
        return -1, "no name given"
    titles = [[_card_title(c) for c in _bundle_cards(b)] for b in entries]
    hits = [i for i, ts in enumerate(titles)
            if any(_fold(t) == want for t in ts)]
    if not hits:
        hits = [i for i, ts in enumerate(titles)
                if any(want in _fold(t) for t in ts)]
    if not hits:
        offered = "; ".join(f"[{', '.join(t for t in ts if t)}]"
                            for ts in titles)
        return -1, (f"no bundle here holds anything called {name!r}. "
                    f"What is on the screen: {offered or '(nothing)'}")
    if len(hits) > 1:
        return -1, (f"{name!r} is in more than one bundle; name a card that "
                    f"is only in the one you want")
    return hits[0], ""


def _card_title(entry: dict[str, Any]) -> str:
    return _text(entry.get("name"))


def _card_face_key(entry: dict[str, Any]) -> str:
    c = _card_face(entry)
    return f"{c['title']}|{c['cost']}|{c['upgraded']}|{c['text']}"


def _resolve_enemy(state: dict[str, Any], name: str) -> tuple[str, str]:
    """`(entity id, refusal)` for an enemy named the way the screen names it."""
    living = [e for e in _enemies(state) if _int(e.get("hp")) > 0]
    if not name:
        if len(living) == 1:
            return _entity_id(living[0]), ""
        return "", ("there is more than one enemy, so say which: "
                    f"{', '.join(_text(e.get('name')) for e in living)}")
    idx, why = _match(living, name, key=lambda e: _text(e.get("name")))
    if idx < 0:
        return "", why
    return _entity_id(living[idx]), ""


def _play(state: dict[str, Any], cmd: Command) -> Resolution:
    hand = _hand(state)
    idx, why = _match(hand, cmd.name, key=_card_title, face=_card_face_key)
    if idx < 0:
        return _refuse(why)
    entry = hand[idx]
    if entry.get("can_play") is False:
        reason = _text(entry.get("unplayable_reason"))
        return _refuse(f"{_card_title(entry)!r} cannot be played right now"
                       + (f": {reason}" if reason else ""))
    post: dict[str, Any] = {"action": "play_card", "card_index": idx}
    printed = {"card": _card_title(entry)}
    needs_target = str(entry.get("target_type") or "").lower() in (
        "anyenemy", "enemy", "singleenemy", "targetenemy")
    if cmd.target or needs_target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            return _refuse(why)
        post["target"] = eid
        printed["target"] = next(
            (_text(e.get("name")) for e in _enemies(state)
             if _entity_id(e) == eid), "")
    return Resolution(True, "play", post, printed)


def _use_potion(state: dict[str, Any], cmd: Command) -> Resolution:
    potions = _potions(state)
    if not potions:
        return _refuse("you are not carrying any potions")
    idx, why = _match(potions, cmd.name, key=lambda p: _text(p.get("name")))
    if idx < 0:
        return _refuse(why)
    post: dict[str, Any] = {"action": "use_potion", "slot": idx}
    printed = {"potion": _text(potions[idx].get("name"))}
    if cmd.target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            return _refuse(why)
        post["target"] = eid
        printed["target"] = cmd.target
    return Resolution(True, "use potion", post, printed)


def _choose(state: dict[str, Any], cmd: Command) -> Resolution:
    """`choose` on whichever screen is up. One verb, six wire actions.

    The screen decides the action, never the shape of the name: the tester says
    the printed thing they want, and this function knows that a card reward
    wants `select_card_reward` while a rest site wants `choose_rest_option`.
    """
    st = _screen(state)
    if st == "card_reward":
        entries = _screen_cards(state)
        idx, why = _match(entries, cmd.name, key=_card_title,
                          face=_card_face_key)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_card_reward", "card_index": idx},
                          {"card": _card_title(entries[idx])})
    if st in SELECT_SCREENS:
        entries = _screen_cards(state)
        idx, why = _match(entries, cmd.name, key=_card_title,
                          face=_card_face_key)
        if idx < 0:
            return _refuse(why)
        verb = "select_card" if st == "card_select" else "combat_select_card"
        key = "index" if st == "card_select" else "card_index"
        return Resolution(True, "choose", {"action": verb, key: idx},
                          {"card": _card_title(entries[idx])})
    if st == "bundle_select":
        # `EB-173`: match on the printed title of any card IN a bundle, the
        # only name this screen has. `_match` is deliberately not reused: its
        # `key` is one string per entry, and a bundle is a set of names.
        entries = _screen_cards(state)
        idx, why = _match_bundle(entries, cmd.name)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_bundle", "index": idx},
                          {"bundle": _named_option(entries[idx])["name"]})
    if st == "event":
        return _index_choice(state, cmd, _event_options(state),
                             "choose_event_option")
    if st == "rest_site":
        return _index_choice(state, cmd, _rest_options(state),
                             "choose_rest_option")
    if st == "rewards":
        return _index_choice(state, cmd, _reward_items(state), "claim_reward")
    if st == "treasure":
        return _index_choice(state, cmd, _relic_options(state),
                             "claim_treasure_relic")
    if st == "relic_select":
        return _index_choice(state, cmd, _relic_options(state), "select_relic")
    return _refuse("there is nothing to choose on this screen")


def _index_choice(state: dict[str, Any], cmd: Command, entries: list[Any],
                  action: str) -> Resolution:
    """A `choose` that posts an index into a list of PRINTED options.

    The index posted is the option's own `index` field where the wire supplies
    one and its LIST POSITION otherwise -- event options carry an explicit
    index and the walker in `soak` reads it, while a rest site is indexed by
    position. Resolved here, at the moment of posting, for `naming.py:14-17`'s
    reason.
    """
    options = [_named_option(o) for o in entries]
    idx, why = _match([{"n": o["name"]} for o in options], cmd.name,
                      key=lambda e: e["n"])
    if idx < 0:
        return _refuse(why)
    if not options[idx]["enabled"]:
        return _refuse(f"{options[idx]['name']!r} is on the screen but not "
                       f"available to take")
    raw = entries[idx]
    posted = raw.get("index") if isinstance(raw, dict) else None
    return Resolution(True, "choose",
                      {"action": action,
                       "index": posted if isinstance(posted, int) else idx},
                      {"option": options[idx]["name"]})


def _go(state: dict[str, Any], cmd: Command) -> Resolution:
    if not _map_nodes(state):
        return _refuse("the map is not asking for a move right now")
    options = _map_options(state)
    idx, why = _match([{"n": o["name"]} for o in options], cmd.name,
                      key=lambda e: e["n"])
    if idx < 0:
        return _refuse(why)
    return Resolution(True, "go", {"action": "choose_map_node", "index": idx},
                      {"node": options[idx]["name"]})


def _buy(state: dict[str, Any], cmd: Command) -> Resolution:
    items = _shop_items(state)
    if not items:
        return _refuse("there is nothing on the shelves")
    options = [_named_option(i) for i in items]
    idx, why = _match([{"n": o["name"]} for o in options], cmd.name,
                      key=lambda e: e["n"])
    if idx < 0:
        return _refuse(why)
    price = options[idx]["price"]
    gold = _int(_player(state).get("gold"))
    if price is not None and price > gold:
        return _refuse(f"{options[idx]['name']!r} costs {price} gold and you "
                       f"have {gold}")
    return Resolution(True, "buy", {"action": "shop_purchase", "index": idx},
                      {"item": options[idx]["name"], "price": price})


def _rest_keyword(state: dict[str, Any], cmd: Command,
                  keywords: tuple[str, ...]) -> Resolution:
    """`rest` / `upgrade` / `remove` at a rest site, by the printed option.

    On a CARD screen the same two words mean "pick this card", and that is
    handled by falling through to `_choose` -- the screen decides, exactly as
    it does for `choose`.
    """
    options = [_named_option(o) for o in _rest_options(state)]
    if not options:
        return _refuse("this rest site is not offering anything")
    for i, o in enumerate(options):
        folded = _fold(o["name"])
        if any(k in folded for k in keywords):
            if not o["enabled"]:
                return _refuse(f"{o['name']!r} is not available")
            raw = _rest_options(state)[i]
            posted = raw.get("index") if isinstance(raw, dict) else None
            return Resolution(
                True, cmd.verb,
                {"action": "choose_rest_option",
                 "index": posted if isinstance(posted, int) else i},
                {"option": o["name"]})
    return _refuse(f"nothing here offers to {cmd.verb}. What is offered: "
                   + ", ".join(o["name"] for o in options))


def act(state: dict[str, Any], command: str) -> dict[str, Any]:
    """Resolve one player-language command against the CURRENT state.

    Returns the `Resolution` as a dict. It does NOT post -- the caller posts,
    so that the state a command was resolved against and the state it is sent
    to are provably the same frame.
    """
    try:
        cmd = parse_command(command)
    except BlindPlayError as exc:
        return _refuse(str(exc)).as_dict()

    st = _screen(state)
    obs_blocked = observation(state)["blocked"]
    if obs_blocked:
        return _refuse(f"this screen is not being driven: {obs_blocked}"
                       ).as_dict()

    if cmd.verb == "play":
        res = (_play(state, cmd) if st in COMBAT_SCREENS
               else _refuse("you are not in a battle"))
    elif cmd.verb == "use potion":
        res = _use_potion(state, cmd)
    elif cmd.verb == "end turn":
        res = (Resolution(True, "end turn", {"action": "end_turn"}, {})
               if st in COMBAT_SCREENS else _refuse("you are not in a battle"))
    elif cmd.verb == "choose":
        res = _choose(state, cmd)
    elif cmd.verb == "go":
        res = _go(state, cmd) if st == "map" else _refuse("the map is not up")
    elif cmd.verb == "buy":
        res = (_buy(state, cmd) if st in ("shop", "fake_merchant")
               else _refuse("you are not in a shop"))
    elif cmd.verb == "rest":
        res = (_rest_keyword(state, cmd, ("rest", "sleep", "heal"))
               if st == "rest_site" else _refuse("there is nowhere to rest"))
    elif cmd.verb in ("upgrade", "remove"):
        if st == "rest_site":
            words = (("upgrade", "smith", "forge") if cmd.verb == "upgrade"
                     else ("remove", "purge", "toss"))
            res = _rest_keyword(state, cmd, words)
        elif st in SELECT_SCREENS and cmd.name:
            res = _choose(state, cmd)
        else:
            res = _refuse(f"nothing here can {cmd.verb} a card")
    elif cmd.verb == "confirm":
        res = _confirm(state)
    elif cmd.verb == "skip":
        res = _skip(state)
    elif cmd.verb == "proceed":
        res = _proceed(state)
    else:                                                # pragma: no cover
        res = _refuse(f"{cmd.verb!r} is not wired to anything")
    res.verb = res.verb or cmd.verb
    return res.as_dict()


def _confirm(state: dict[str, Any]) -> Resolution:
    st = _screen(state)
    verbs = {"card_select": "confirm_selection",
             "hand_select": "combat_confirm_selection",
             "bundle_select": "confirm_bundle_selection"}
    if st not in verbs:
        return _refuse("there is nothing waiting to be confirmed")
    return Resolution(True, "confirm", {"action": verbs[st]}, {})


def _skip(state: dict[str, Any]) -> Resolution:
    st = _screen(state)
    if st == "card_reward":
        blob = _blob(state, "card_reward")
        if blob.get("can_skip") is False:
            return _refuse("this card reward cannot be skipped")
        return Resolution(True, "skip", {"action": "skip_card_reward"}, {})
    if st == "relic_select":
        return Resolution(True, "skip", {"action": "skip_relic_selection"}, {})
    if st in SELECT_SCREENS:
        blob = _blob(state, st)
        if not (blob.get("can_skip") or blob.get("can_cancel")):
            return _refuse("this screen will not let you leave without "
                           "choosing")
        verb = ("cancel_selection" if st == "card_select"
                else "combat_confirm_selection")
        return Resolution(True, "skip", {"action": verb}, {})
    return _refuse("there is nothing here to skip")


def _proceed(state: dict[str, Any]) -> Resolution:
    st = _screen(state)
    if st == "event" and _blob(state, "event").get("in_dialogue"):
        return Resolution(True, "proceed", {"action": "advance_dialogue"}, {})
    if st in ("rewards", "treasure", "shop", "fake_merchant", "rest_site",
              "event"):
        return Resolution(True, "proceed", {"action": "proceed"}, {})
    return _refuse("there is nothing to leave from this screen")


# ------------------------------------------------------------- transcript --

class Transcript:
    """One JSONL row per observation, command and post. Gitignored.

    It holds the observation SHA rather than the observation: the page itself
    is reproducible from the state and the file is meant to be read by a
    person checking what the seat was shown and what it said.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: list[dict[str, Any]] = []

    def write(self, **row: Any) -> dict[str, Any]:
        row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.rows.append(row)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        return row


# ------------------------------------------------------------- the tester --

# Independence is by model FAMILY (R217 C). The slice's author is Claude, so a
# Claude seat is refused however fresh its context is -- "a fresh context on
# the same model does not satisfy it" is the ruling's own wording. The check
# lives here rather than in `seat.py` because `seat.py`'s blind grader is one
# turn against a staged board, where the author never had a chance to be the
# grader; a driver that a person points at a model name needs the refusal in
# code.
AUTHOR_FAMILY = "claude"
MODEL_FAMILIES = {
    "claude": ("claude", "anthropic", "opus", "sonnet", "haiku", "fable"),
    "gpt": ("gpt", "openai", "o1", "o3", "codex"),
}


def model_family(model: str) -> str:
    low = str(model or "").casefold()
    for family, markers in MODEL_FAMILIES.items():
        if any(m in low for m in markers):
            return family
    return ""


def check_independent(model: str, author: str = AUTHOR_FAMILY) -> None:
    """Refuse the author's own model family as tester. R217 C."""
    family = model_family(model)
    if not family:
        raise BlindPlayError(
            f"cannot tell which model family {model!r} belongs to, and an "
            f"independence rule that cannot name the family is not a check")
    if family == author:
        raise BlindPlayError(
            f"{model!r} is in the {family!r} family, which authored this "
            f"slice. Independence is by model FAMILY, not by fresh context "
            f"(R217 C): the tester must be the Codex seat.")


def command_schema() -> dict[str, Any]:
    """The reply shape for a play turn. Shape only -- never content."""
    return {"type": "object",
            "properties": {"command": {"type": "string"},
                           "thinking": {"type": "string"}},
            "required": ["command", "thinking"],
            "additionalProperties": False}


def record_schema() -> dict[str, Any]:
    """The reply shape for a fight or run record. Shape only."""
    return {"type": "object",
            "properties": {"record": {"type": "string"}},
            "required": ["record"],
            "additionalProperties": False}


class ScriptedThread:
    """A tester made of a list. The whole loop runs without codex or a game."""

    def __init__(self, replies: list[dict[str, Any]], model: str = "gpt-test"):
        self.replies = list(replies)
        self.model = model
        self.sent: list[str] = []
        self.calls = 0

    def identity(self) -> dict[str, Any]:
        return {"model_requested": self.model, "model_observed": self.model,
                "codex_version": "(scripted)", "thread_id": "(scripted)"}

    def send(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self.sent.append(prompt)
        self.calls += 1
        if not self.replies:
            raise BlindPlayError("the scripted tester ran out of replies")
        return self.replies.pop(0)


class ScriptedWire:
    """A game made of a list of states. Shipped, not test-only.

    `get_state` returns the next scripted state on every POST and the current
    one otherwise, which is enough to walk a whole fight: the scenario author
    writes the frames the seat will see and the driver does not know the
    difference. Every POST is recorded so a test can assert the wire body the
    grammar produced.
    """

    def __init__(self, states: list[dict[str, Any]]):
        self.states = list(states)
        self.posts: list[dict[str, Any]] = []
        self.i = 0

    def get_state(self) -> dict[str, Any]:
        return self.states[min(self.i, len(self.states) - 1)]

    def post(self, action: str, **params: Any) -> dict[str, Any]:
        self.posts.append({"action": action, **params})
        self.i += 1
        return {"status": "ok", "message": ""}

    def health(self) -> dict[str, Any]:
        return {"mod_version": "0.0-scripted"}


class CodexThread:
    """ONE `codex exec` thread for a whole run (EB-168).

    `codex exec` for the first turn and `codex exec resume <thread id>` after
    it, which is the door `seat.py` deliberately did not walk through: a blind
    GRADER must not have seen the previous board, and a blind PLAYER must.
    Everything else is `seat.py`'s -- the same flags, the same empty scratch
    root outside the repo, and the same three-source transcript guard applied
    to EVERY reply, not just the first.
    """

    def __init__(self, session: Path, *, model: str = seat.DEFAULT_MODEL,
                 timeout: int = seat.TIMEOUT_S):
        check_independent(model)
        self.session = session
        self.model = model
        self.timeout = timeout
        self.codex = seat.codex_path()
        self.codex_version = seat._codex_version(self.codex)
        self.scratch = seat.scratch_root()
        if seat.is_inside_repo(self.scratch):
            raise BlindPlayError("the seat's scratch directory resolved "
                                 "inside the repo")
        self.thread_id = ""
        self.model_observed = ""
        self.turn = 0

    def identity(self) -> dict[str, Any]:
        return {"model_requested": self.model,
                "model_observed": self.model_observed,
                "codex_version": self.codex_version,
                "thread_id": self.thread_id}

    def close(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)

    def _argv(self, d: Path) -> list[str]:
        """`codex exec` for the first turn, `codex exec resume` after it.

        THE TWO SUBCOMMANDS DO NOT TAKE THE SAME FLAGS, and the first live
        acceptance run is what proved it: `codex exec resume` accepts neither
        `-C` nor `--sandbox` nor `--color` (codex-cli 0.150.1 answers
        `error: unexpected argument '-C' found` and exits 2), so a session
        built by pasting the first turn's argv after `resume` dies on its
        SECOND action every time -- one action in, no fight, no record.

        What each dropped flag is replaced by, rather than given up:
          `-C`        the process cwd, which is already `self.scratch`
          `--sandbox` `-c sandbox_mode=...`, the config key the flag sets
          `--color`   nothing; the stream is `--json` either way
        """
        common = ["--skip-git-repo-check", "--ignore-user-config",
                  "--ignore-rules", "--json",
                  "--output-schema", str(d / "schema.json"),
                  "-o", str(d / "reply.json"), "-m", self.model, "-"]
        if self.thread_id:
            return [self.codex, "exec", "resume", self.thread_id,
                    "-c", 'sandbox_mode="read-only"'] + common
        return [self.codex, "exec", "-C", str(self.scratch),
                "--sandbox", "read-only", "--color", "never"] + common

    def send(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self.turn += 1
        d = self.session / f"turn-{self.turn:03d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "prompt.md").write_text(prompt, encoding="utf-8")
        (d / "schema.json").write_text(json.dumps(schema, indent=1) + "\n",
                                       encoding="utf-8")
        argv = self._argv(d)
        (d / "argv.json").write_text(json.dumps(argv, indent=1) + "\n",
                                     encoding="utf-8")
        code, timed_out = seat._run(argv, stdin_text=prompt,
                                    stdout=d / "events.jsonl",
                                    stderr=d / "stderr.txt",
                                    cwd=self.scratch, timeout=self.timeout)
        if timed_out:
            raise BlindPlayError("the seat did not answer inside the timeout")
        events = seat.read_jsonl(d / "events.jsonl")
        self.thread_id = self.thread_id or seat.thread_id(events)
        source = seat.find_rollout(self.thread_id)
        rollout = None
        if source is not None:
            shutil.copyfile(source, d / "rollout.jsonl")
            rollout = seat.read_jsonl(d / "rollout.jsonl")
        stderr_text = (d / "stderr.txt").read_text(encoding="utf-8",
                                                   errors="replace")
        reason, offenders, _counts = seat.guard(events, rollout, stderr_text)
        if reason:
            raise BlindPlayError(
                f"seat refused ({reason}): "
                f"{seat.REFUSAL_REASONS.get(reason, reason)}"
                + (f" -- {', '.join(offenders)}" if offenders else ""))
        if code != 0:
            if _is_rate_limited(stderr_text):
                raise SeatBudgetExhausted(
                    f"codex exited {code} on a usage limit: "
                    f"{stderr_text.strip()[:300]}")
            raise BlindPlayError(
                f"codex exited {code}: {stderr_text.strip()[:300]}")
        self.model_observed = seat.rollout_model(rollout or [])
        try:
            reply = json.loads((d / "reply.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise BlindPlayError(f"the seat's reply did not parse: {exc}")
        if not isinstance(reply, dict):
            raise BlindPlayError("the seat's reply is not a JSON object")
        return reply


# --------------------------------------------------------------- the loop --

@dataclass
class Budget:
    """Three ways to stop, all of them declared before the run starts."""
    max_actions: int = 60
    max_wall_s: float = 3600.0
    max_refusals: int = 3
    # `EB-173`. The other three stop a session that is going WRONG; this one
    # stops a session that is going NOWHERE, which the first three cannot see.
    # A command the resolver accepts and the wire answers with an error resets
    # the refusal counter and spends an action, so a screen the tester cannot
    # get off loops until the action budget is gone -- observed live, 150+
    # identical `confirm`s at one bundle screen. Stall = the rendered page
    # unchanged, this many times running.
    max_stalls: int = 6


FIGHT_QUESTIONS = """That fight is over. In a short paragraph each, and in
plain language:

1. What line did you take, and why that one?
2. What other line did you seriously consider, and what would it have given up?
3. Would a different enemy intent, or a different draw, have changed your
   choice?
4. Which cards became automatic, and which became dead?
5. Did your plan change during the fight, and where?
6. Was anything on the screen confusing to read?"""

RUN_QUESTIONS = """The run is over. In a short paragraph each, and in plain
language:

1. How do you think this character works?
2. Which tension came up again and again?
3. Which cards defined the run?
4. Where did play start to feel repetitive?
5. What would you avoid drafting next time, and why?"""

RECORD_DISCLAIMER = (
    "None of this is a judgement of whether the game is fun or good that "
    "anyone will treat as approval. It is one model's account of one run, "
    "recorded for iteration.")


class Session:
    """One blind run: one screen at a time, one command at a time.

    `wire` is anything with `get_state()` and `post(action, **params)` --
    `understudy.bridge` in the live case and a scripted double in the tests, so
    the whole loop is exercised without the game or codex.
    """

    def __init__(self, thread: Any, *, wire: Any = bridge,
                 session_id: str = "", budget: Budget | None = None,
                 log_root: Path | None = None,
                 prompt_path: Path | None = None,
                 settle_tries: int = SETTLE_TRIES,
                 settle_delay_s: float = SETTLE_DELAY_S):
        self.thread = thread
        self.wire = wire
        self.settle_tries = settle_tries
        self.settle_delay_s = settle_delay_s
        self.budget = budget or Budget()
        self.session_id = session_id or time.strftime("%Y%m%d-%H%M%S",
                                                      time.gmtime())
        self.dir = (log_root or LOG_ROOT) / self.session_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.transcript = Transcript(self.dir / "transcript.jsonl")
        self.prompt_text = (prompt_path or PROMPT_PATH).read_text(
            encoding="utf-8")
        self.prompt = seat.template_body(self.prompt_text)
        self.prompt_sha = sha256(self.prompt)
        self.actions = 0
        self.refusals = 0
        self.fight_records: list[str] = []
        self.run_record = ""
        self.stopped = ""
        self.started = time.time()

    # -- the two things the seat is ever sent ------------------------------

    def _page(self, obs_md: str, feedback: str) -> str:
        parts = [obs_md]
        if feedback:
            parts.append(f"## What happened last time\n\n{feedback}")
        parts.append("Answer with ONE command from the grammar.")
        return "\n\n".join(parts)

    def _settle(self, state: dict[str, Any]) -> dict[str, Any]:
        """Ride out a MOMENT rather than reporting it as a screen.

        The first live acceptance run died here: the seat walked onto a Monster
        node, the very next read answered `state_type: "unknown"` because the
        room had not been entered yet, and the driver stopped the session
        TOOL-BLOCKED against a transition. `soak._settle_transient` had already
        learned this on the same wire, and the fix is the same shape -- poll,
        bounded, and hand back whatever is there when the bound runs out so a
        wire that really is stuck is still reported as blocked rather than
        waited on forever. A missing `state_type` key is the same moment one
        frame earlier and settles the same way.

        `EB-175` added the third shape -- a combat screen the game has not
        handed back yet -- to `transient()`, which is where all three now
        live so the CLI's own live reads ride out the same moments.
        """
        return settle(state, self.wire, self.settle_tries,
                      self.settle_delay_s)

    def _ask_record(self, questions: str) -> str:
        reply = self.thread.send(f"{questions}\n\n{RECORD_DISCLAIMER}\n",
                                 record_schema())
        text = str(reply.get("record") or "").strip()
        self.transcript.write(kind="record", chars=len(text))
        return text

    # -- the loop ----------------------------------------------------------

    def run(self) -> dict[str, Any]:
        feedback = ""
        first = True
        in_fight = False
        last_page_sha = ""
        stalls = 0
        while True:
            if self.actions >= self.budget.max_actions:
                self.stopped = "max_actions"
                break
            if time.time() - self.started > self.budget.max_wall_s:
                self.stopped = "max_wall"
                break

            state = self._settle(self.wire.get_state())
            try:
                obs = observation(state)
            except qa_packet.PacketLeak as exc:
                self.stopped = "observation_leak"
                self.transcript.write(kind="leak", detail=str(exc))
                break
            page = render(obs)
            page_sha = sha256(page)
            if page_sha == last_page_sha:
                stalls += 1
                if stalls >= self.budget.max_stalls:
                    self.stopped = "stalled"
                    self.transcript.write(kind="stall", page_sha256=page_sha,
                                          repeats=stalls)
                    break
            else:
                stalls = 0
            last_page_sha = page_sha
            self.transcript.write(kind="observation",
                                  state_type=obs["state_type"],
                                  screen=obs["screen"],
                                  blocked=obs["blocked"],
                                  observation_sha256=page_sha)

            was_in_fight, in_fight = in_fight, obs["screen"] == "combat"
            if was_in_fight and not in_fight and self.actions:
                # SAME REASONING AS THE RUN RECORD BELOW (b0de780): a seat that
                # cannot answer at a fight boundary must not take the fight
                # records already gathered down with it.
                try:
                    self.fight_records.append(
                        self._ask_record(FIGHT_QUESTIONS))
                except SeatBudgetExhausted as exc:
                    self.stopped = "budget:rate_limit"
                    self.transcript.write(kind="seat_budget", detail=str(exc),
                                          at="fight_record")
                    break
                except BlindPlayError as exc:
                    self.stopped = "seat_refused"
                    self.transcript.write(kind="seat_error", detail=str(exc),
                                          at="fight_record")
                    break

            if obs["blocked"]:
                self.stopped = ("run_over" if obs["screen"] == "game_over"
                                else "tool_blocked")
                break

            body = self._page(page, feedback)
            prompt = f"{self.prompt}\n\n---\n\n{body}\n" if first else body
            first = False
            try:
                reply = self.thread.send(prompt, command_schema())
            except SeatBudgetExhausted as exc:
                self.stopped = "budget:rate_limit"
                self.transcript.write(kind="seat_budget", detail=str(exc))
                break
            except BlindPlayError as exc:
                self.stopped = "seat_refused"
                self.transcript.write(kind="seat_error", detail=str(exc))
                break
            command = str(reply.get("command") or "").strip()
            if not command:
                self.stopped = "no_command"
                break

            res = act(state, command)
            self.transcript.write(kind="command", command=command,
                                  ok=res["ok"], verb=res["verb"],
                                  printed=res["printed"],
                                  post=res["post"], refusal=res["refusal"])
            if not res["ok"]:
                self.refusals += 1
                feedback = f"That did not work: {res['refusal']}"
                if self.refusals >= self.budget.max_refusals:
                    self.stopped = "refusal_limit"
                    break
                continue

            self.refusals = 0
            post = dict(res["post"] or {})
            action = post.pop("action")
            result = self.wire.post(action, **post)
            self.actions += 1
            feedback = _result_line(result)
            self.transcript.write(kind="result", action=action,
                                  summary=feedback)

        # ASKED EVEN ON A TRUNCATED RUN -- a session that hit its action budget
        # still has an account worth keeping -- but never at the cost of the
        # record already gathered: a seat that has just refused cannot answer,
        # and losing the fight records to that would be losing the session.
        if self.actions and not self.run_record:
            try:
                self.run_record = self._ask_record(RUN_QUESTIONS)
            except BlindPlayError as exc:
                self.transcript.write(kind="seat_error", detail=str(exc),
                                      at="run_record")
        return self.summary()

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "actions": self.actions,
            "termination": self.stopped or "unknown",
            "prompt_sha256": self.prompt_sha,
            "fight_records": list(self.fight_records),
            "run_record": self.run_record,
            "transcript": str(self.transcript.path),
            "guardrail": PLAY_GUARDRAIL,
            **self.thread.identity(),
        }


def _result_line(result: Any) -> str:
    """The wire's answer to a POST, in the tester's vocabulary.

    Only the game's own `message` and `status` cross back -- a full state dump
    would carry ids, and the next observation is where the board is read
    anyway. Scrubbed like everything else.
    """
    if not isinstance(result, dict):
        return ""
    text = " ".join(x for x in (_text(result.get("status")),
                                _text(result.get("message"))) if x)
    leaks = qa_packet.leaks(text)
    if leaks:
        return "(the game answered with something this tool will not repeat)"
    return text


# ----------------------------------------------------------- sealed record --

# `klee-mod/local.props` is the machine's one statement of where the game is,
# and this is a DELIBERATE SECOND COPY of the four lines `soak.game_dir()`
# reads it with -- for the same reason `HAZARD_EVENTS` is copied above:
# importing `soak` here would pull `policy_v1` and every tier0 sheet loader
# into the design-blind module. Nothing below reads anything but a version
# string, and a missing file is answered with a reason, never a guess.
LOCAL_PROPS = Path(__file__).resolve().parents[1] / "klee-mod" / "local.props"


def _game_dir() -> Path | None:
    try:
        text = LOCAL_PROPS.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"<GameDir>([^<]+)</GameDir>", text)
    return Path(m.group(1).strip()) if m and m.group(1).strip() else None


def _json_field(path: Path, key: str) -> str:
    try:
        # `deploy.ps1` writes the manifest through PowerShell, which stamps a
        # UTF-8 BOM; `utf-8-sig` reads it either way.
        blob = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return ""
    return _text(blob.get(key)) if isinstance(blob, dict) else ""


def build_version(wire: Any = None) -> tuple[str, str]:
    """`(mod build, where it was read)` for the DEPLOYED package. Never guessed.

    `EB-174`. This used to read the bridge's health payload, which carries the
    VENDORED bridge's own version (`v0.4.0`) and has never carried ours -- so
    every sealed record's identity block read `(not read)`, on a document
    whose whole purpose is provenance. The honest source is the package that
    is actually installed: `<GameDir>\\mods\\klee\\manifest.json`, whose
    producer is `klee-mod\\build\\deploy.ps1` and whose `version` is the
    string the deploy stamped (`MAJOR.AUTO`, R214, with `+proto` beside it
    where `deploy_proto.ps1` built it).

    Read off DISK rather than off the wire on purpose: the file is what a
    person would open to answer "which build was this", and a record that
    names a build nobody can find on the machine is not provenance. `wire` is
    accepted and ignored so the call site does not have to know that.
    """
    game = _game_dir()
    if game is None:
        return "", (f"no GameDir in {LOCAL_PROPS.name}, so the deployed "
                    f"package cannot be found")
    manifest = game / "mods" / "klee" / "manifest.json"
    version = _json_field(manifest, "version")
    if version:
        return version, "the deployed `mods\\klee\\manifest.json` `version`"
    return "", (f"no `version` in {manifest}" if manifest.is_file()
                else f"no deployed package at {manifest}")


def game_version(wire: Any = None) -> tuple[str, str]:
    """`(game build, where it was read)`. Never guessed.

    The other half of `EB-174`: a record has to name the GAME too, because a
    live number was never comparable across a game build (R95) and the pin
    moved under this tool once already (R218, v0.107.1 -> v0.111.0 mid-sitting).

    `release_info.json` in the install root is the game's own statement of its
    version, and it is the first of the four facts `OPERATIONS.md` names for
    confirming a pin. Cheaper and steadier than the two alternatives: reading
    `release=v...` out of `godot.log` means scanning a file that reaches
    gigabytes on a bad run, and Steam's `appmanifest` buildid names a build
    without naming a version.
    """
    game = _game_dir()
    if game is None:
        return "", (f"no GameDir in {LOCAL_PROPS.name}, so the install root "
                    f"cannot be found")
    info = game / "release_info.json"
    version = _json_field(info, "version")
    if version:
        return version, "the game's own `release_info.json` `version`"
    return "", (f"no `version` in {info}" if info.is_file()
                else f"no `release_info.json` at {info}")


# --------------------------------------------------------- the leak audit --

# The seed is added per-session; these are the standing extra rules, ON TOP of
# `qa_packet.FORBIDDEN`, which the render already enforces at write time.
#
# WHY AN AUDIT AT ALL WHEN THE RENDER ALREADY SCRUBS. Because "the scrubber
# ran" and "no observation carried a leak" are different claims, and only the
# second one is `EB-167`'s acceptance. The scrubber is a belt on the render
# path; this is a brace read back off what was ACTUALLY SHOWN to the tester --
# every `turn-*/prompt.md`, the exact bytes `codex exec` was handed. A scrubber
# that silently stopped running would still leave this audit able to say so.
#
# The four extra patterns are the SIM's vocabulary rather than the sheet's.
# `qa_packet` guards ids, rulings and sheet fields; a prompt that said "policy"
# or "EV" or "counterfactual" would be leaking the pilot's reasoning instead,
# which is the specific thing R217 E forbids by naming `harness state` as the
# endpoint this tool may never build on.
AUDIT_EXTRA: tuple[tuple[str, str], ...] = (
    ("pilot-vocabulary-policy", r"\bpolicy\b"),
    ("pilot-vocabulary-score", r"\bscores?\b|\bscoring\b"),
    ("pilot-vocabulary-ev", r"\bEV\b|\bexpected value\b"),
    ("pilot-vocabulary-counterfactual", r"\bcounterfactual\b"),
    ("pilot-vocabulary-pilot", r"\bpilot\b"),
)


def leak_audit(log_dir: Path, seed: str = "") -> dict[str, Any]:
    """Scan every observation actually shown to the tester. Never writes.

    Returns `{observations, rules: {rule: count}, offenders: [(file, rule,
    hit, context)], total}`. An empty `rules` map with a non-zero
    `observations` count is the finding this is for.

    `seed` is audited as its own rule: the run seed is not design vocabulary,
    but a tester who can see it can look the run up, and R95's whole point is
    that a number is only comparable inside a labelled world.
    """
    rules: list[tuple[str, re.Pattern[str]]] = [
        (rule, pattern) for rule, pattern in qa_packet.FORBIDDEN]
    rules += [(rule, re.compile(pat, re.I)) for rule, pat in AUDIT_EXTRA]
    if seed:
        rules.append(("run-seed", re.compile(re.escape(seed), re.I)))

    counts: dict[str, int] = {}
    offenders: list[tuple[str, str, str, str]] = []
    pages = sorted(log_dir.glob("turn-*/prompt.md"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for line in text.splitlines():
            for rule, pattern in rules:
                for m in pattern.finditer(line):
                    counts[rule] = counts.get(rule, 0) + 1
                    if len(offenders) < 40:
                        offenders.append((page.parent.name, rule, m.group(0),
                                          line.strip()[:160]))
    return {"observations": len(pages), "rules": counts,
            "offenders": offenders, "total": sum(counts.values())}


def audit_markdown(audit: dict[str, Any]) -> str:
    """The audit as the committed record carries it."""
    out = ["## Leak audit", "",
           f"Every observation the tester was actually shown — "
           f"`turn-*/prompt.md`, the exact bytes handed to `codex exec` — "
           f"scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary "
           f"rules and this run's seed.", "",
           f"- **observations scanned**: {audit['observations']}",
           f"- **total hits**: {audit['total']}"]
    if audit["rules"]:
        out += ["", "| rule | hits |", "|---|---|"]
        out += [f"| `{r}` | {n} |" for r, n in sorted(audit["rules"].items())]
        out += ["", "Offenders (first 40):", ""]
        out += [f"- `{d}` — `{r}` matched `{hit}` in: {ctx}"
                for d, r, hit, ctx in audit["offenders"]]
    else:
        out += ["", "No rule matched in any observation."]
    return "\n".join(out) + "\n"


def record_markdown(summary: dict[str, Any], identity: dict[str, Any]) -> str:
    """The COMMITTED half: identity, then the model's words verbatim."""
    out = [f"# Blind play session `{summary['session_id']}`", "",
           "**R217 G — subjective feedback from an independent model playing "
           "the real game. Useful for iteration; not human validation, not "
           "balance evidence, not approval. It never enters an Understudy "
           "report, a win-rate table or a measurement register.**", "",
           "## Identity", ""]
    for key in ("model_requested", "model_observed", "codex_version",
                "build_version", "build_version_source",
                "game_version", "game_version_source", "run_seed",
                "prompt_sha256", "actions", "termination"):
        if key in identity:
            out.append(f"- **{key}**: {identity[key] or '(not read)'}")
    out += ["", f"- **guardrail**: {summary['guardrail']}", ""]
    for i, text in enumerate(summary["fight_records"], 1):
        out += [f"## Fight {i}, in the tester's own words", "", text.rstrip(),
                ""]
    if summary["run_record"]:
        out += ["## The run, in the tester's own words", "",
                summary["run_record"].rstrip(), ""]
    return "\n".join(out).rstrip() + "\n"


def seal(summary: dict[str, Any], identity: dict[str, Any], *,
         log_dir: Path, record_root: Path | None = None) -> Path:
    """Write both halves. The gitignored one first, the committed one after."""
    (log_dir / "session.json").write_text(
        json.dumps({**summary, **identity}, indent=1, default=str) + "\n",
        encoding="utf-8")
    for i, text in enumerate(summary["fight_records"], 1):
        (log_dir / f"fight-{i:02d}.md").write_text(text, encoding="utf-8")
    if summary["run_record"]:
        (log_dir / "run.md").write_text(summary["run_record"],
                                        encoding="utf-8")
    out = (record_root or RECORD_ROOT) / summary["session_id"]
    out.mkdir(parents=True, exist_ok=True)
    path = out / "record.md"
    path.write_text(record_markdown(summary, identity), encoding="utf-8")
    return path


# -------------------------------------------------------------------- CLI --

def _load_state(args) -> dict[str, Any]:
    """The live state, or a saved one.

    A saved file is either a raw wire state or one of the envelopes this repo
    already writes around one (`review/qa/<turn>/observed.json` keeps it under
    `state`), so the recorded material is usable as a fixture without being
    unwrapped by hand first.

    A LIVE read settles first and a saved one never does (`EB-175`): the
    operator driving `observe` / `act` by hand reads the wire on exactly the
    frames the driver does, and a fixture is a frame somebody chose.
    """
    if not args.raw_file:
        return settle(bridge.get_state())
    blob = json.loads(Path(args.raw_file).read_text(encoding="utf-8"))
    inner = blob.get("state") if isinstance(blob, dict) else None
    if isinstance(inner, dict) and inner.get("state_type"):
        return inner
    return blob


def cmd_observe(args) -> int:
    state = _load_state(args)
    try:
        print(observe(state))
    except qa_packet.PacketLeak as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_act(args) -> int:
    state = _load_state(args)
    res = act(state, args.command)
    print(json.dumps(res, indent=1, default=str))
    if not res["ok"]:
        return 1
    if args.raw_file or args.dry_run:
        return 0
    post = dict(res["post"] or {})
    action = post.pop("action")
    result = bridge.post(action, **post)
    print(_result_line(result))
    return 0


def cmd_session(args) -> int:
    session_id = args.session_id or time.strftime("%Y%m%d-%H%M%S",
                                                  time.gmtime())
    log_dir = LOG_ROOT / session_id
    try:
        check_independent(args.model)
    except BlindPlayError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    version, source = build_version()
    game, game_source = game_version()
    seed = bridge.current_seed() or ""
    thread = CodexThread(log_dir, model=args.model)
    budget = Budget(max_actions=args.max_actions,
                    max_wall_s=args.max_wall_s,
                    max_refusals=args.max_refusals,
                    max_stalls=args.max_stalls)
    try:
        session = Session(thread, wire=bridge, session_id=session_id,
                          budget=budget)
        summary = session.run()
    finally:
        thread.close()
    identity = {**thread.identity(), "build_version": version,
                "build_version_source": source,
                "game_version": game, "game_version_source": game_source,
                "run_seed": seed,
                "prompt_sha256": summary["prompt_sha256"],
                "actions": summary["actions"],
                "termination": summary["termination"]}
    path = seal(summary, identity, log_dir=session.dir)
    print(f"transcript: {summary['transcript']}")
    print(f"record:     {path}")
    print(f"actions:    {summary['actions']}   "
          f"stopped: {summary['termination']}")
    return 0


def cmd_audit(args) -> int:
    """Read back what the tester was shown, and say so in the record.

    Separate from `session` on purpose: the audit is a claim about a run that
    has FINISHED, and a session that crashed mid-run should still be auditable
    without re-running it. It reads the gitignored turn pages and writes only
    the committed record.
    """
    log_dir = LOG_ROOT / args.session_id
    if not log_dir.is_dir():
        raise BlindPlayError(f"no session log at {log_dir}")
    session = log_dir / "session.json"
    seed = ""
    if session.is_file():
        seed = _text(json.loads(session.read_text(encoding="utf-8"))
                     .get("run_seed"))
    audit = leak_audit(log_dir, seed)

    record = RECORD_ROOT / args.session_id / "record.md"
    if record.is_file():
        text = record.read_text(encoding="utf-8")
        head = text.split("\n## Leak audit", 1)[0].rstrip()
        record.write_text(head + "\n\n" + audit_markdown(audit),
                          encoding="utf-8")
        print(f"record:  {record}")
    print(f"scanned: {audit['observations']} observation(s)")
    print(f"hits:    {audit['total']}")
    for rule, n in sorted(audit["rules"].items()):
        print(f"  {rule}: {n}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # EB-93: this entry point echoes shipped card titles, and two of them carry
    # a music note. A default Windows console is cp1252.
    report.console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("observe", help="render the current screen, blind")
    o.add_argument("--raw-file", default="",
                   help="a saved wire state instead of the live one")
    o.set_defaults(func=cmd_observe)

    a = sub.add_parser("act", help="resolve one player-language command")
    a.add_argument("command")
    a.add_argument("--raw-file", default="",
                   help="resolve against a saved state and post nothing")
    a.add_argument("--dry-run", action="store_true",
                   help="resolve against the live state and post nothing")
    a.set_defaults(func=cmd_act)

    s = sub.add_parser("session", help="one blind Codex thread plays the run")
    s.add_argument("--model", default=seat.DEFAULT_MODEL)
    s.add_argument("--session-id", default="")
    s.add_argument("--max-actions", type=int, default=60)
    s.add_argument("--max-wall-s", type=float, default=3600.0)
    s.add_argument("--max-refusals", type=int, default=3)
    s.add_argument("--max-stalls", type=int, default=6,
                   help="stop after this many identical screens running "
                        "(EB-173: a screen the tester cannot get off)")
    s.set_defaults(func=cmd_session)

    u = sub.add_parser("audit", help="leak-audit a finished session's own "
                                     "observations and append the counts to "
                                     "its committed record")
    u.add_argument("session_id")
    u.set_defaults(func=cmd_audit)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except BlindPlayError as exc:
        print(f"blind play error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
