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

from understudy import authorship, bridge, qa_packet, report, seat

# `EB-214` item 7 (`M55`, re-scoped by R224). The pile view's own header, as
# `KurageMemoryText.ChargeSource` renders it on screen. THE RATE IS SPELLED
# RATHER THAN IMPORTED, deliberately: this module may not reach `tier0` at all
# (`test_blindplay_cannot_reach_a_sheet_or_a_policy` is the structural
# no-leak pin), so the number is held in step from the OTHER side --
# `test_the_pile_views_charge_source_header_reaches_the_blind_page` reads
# `C.CHARGE_PER_EXHAUST` and fails the moment this sentence falls behind a
# retune, the same way `lint_constant_parity` holds the C# copy.
CHARGE_SOURCE_LINE = "Gain 1 Charge when a card of yours Exhausts"

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

# `EB-264`, the second half, and it is the same tag one step further on. The
# file NAME is namespaced by the art set it was drawn for, so a Klee run's
# Energy Potion read `Gain [ironclad energy icon][ironclad energy icon]` --
# a token naming a character who is not in the run, for an icon that is the
# same pip on every character's screen. The blind tester filed it as an
# unlocalised placeholder and could not tell what it was granting.
#
# So a sprite tag whose file name CONTAINS one of these subjects is rendered
# as that subject and nothing else: `[Energy]`, twice, which is what the
# screen draws and lets a reader count them. It is a REGISTER, like
# `HAZARD_EVENTS` -- one row per inline icon the game actually draws in place
# of a word, and a tag naming none of them keeps the old rendering (its own
# words, spaced) rather than being guessed at.
_ICON_SUBJECTS = {"energy": "Energy"}


def _icon_name(stem: str) -> str:
    words = [w for w in stem.split("_") if w]
    for w in words:
        subject = _ICON_SUBJECTS.get(w.lower())
        if subject:
            return subject
    return " ".join(words)


def _despritify(blob: Any) -> Any:
    """Rewrite every sprite tag in a finished structure. Values only."""
    if isinstance(blob, str):
        return _SPRITE_TAG.sub(
            lambda m: "[" + _icon_name(m.group(1)) + "]", blob)
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


def _number_names(names: list[str]) -> list[str]:
    """Printed names with the repeats numbered, in printed order.

    `EB-177`, FOUND LIVE. Two cards printing one title that differ by anything
    but upgrade state were BOTH unplayable: the bare title is ambiguous,
    `(upgraded)` says nothing here is, `(not upgraded)` narrows to both again,
    and run B6 died against the refusal limit holding two *Water's Edge*, one
    of them enchanted. Two enemies sharing a printed name had the same hole.

    The fix is the one the map already uses for a fork offering two `Monster`
    nodes (`_map_options`, `(path N)`): give each repeat a number, in the order
    the screen prints them, so every face on the screen has a name of its own.
    A title that appears ONCE is left exactly as the game printed it -- the
    number is a disambiguator, not decoration, and a hand of eight distinct
    cards must read the way it always did.

    Folded, not compared raw, so the numbering agrees with the matcher: two
    faces the grammar cannot tell apart are the two the render must number.
    `EB-173`'s surviving `+` keeps `Coral Guard` and `Coral Guard+` two
    different names, so an upgraded pair is still separated by `(upgraded)`
    and never reaches this.

    Called on BOTH sides of the line -- once by the observation that prints the
    names and once by the resolver that reads them back -- from the same
    printed-name sequence, which is what keeps the page and the grammar in
    step. Give it a different sequence on the two sides and they diverge; see
    `_resolve_enemy`, which numbers over EVERY enemy and only then drops the
    dead ones, because the render prints the dead ones too.
    """
    counts: dict[str, int] = {}
    for n in names:
        counts[_fold(n)] = counts.get(_fold(n), 0) + 1
    seen: dict[str, int] = {}
    out: list[str] = []
    for n in names:
        k = _fold(n)
        if counts[k] > 1 and k:
            seen[k] = seen.get(k, 0) + 1
            out.append(f"{n} ({seen[k]})")
        else:
            out.append(n)
    return out


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

      A COMBAT SCREEN WITH NO `battle` BLOCK AT ALL (`EB-178`) -- the
        killing blow has landed, the game has torn the combat down, and the
        rewards screen has not gone up yet. Read live across a victory: at
        +0 ms the wire answers `state_type: "monster"` with NO `battle` key,
        a `player` block stripped of its hand, energy and meters, and
        `run.floor` ALREADY advanced to the next floor; by +250 ms it answers
        `rewards`. Rendered as a screen it is `# Battle -- round 0` with an
        empty hand and no enemies, which both of run B6's fight records read
        as a NEW FIGHT starting. Riding it out is all it needs: the frame is
        gone in a quarter-second, and nothing here posts on the tester's
        behalf to make it go.

    `is_play_phase` is checked for an explicit `False` and never for
    falsiness: a build whose battle block does not carry the key must not
    have every combat screen read as a transition. The `EB-178` shape is
    checked on the block's ABSENCE rather than on any key inside it, for the
    same reason from the other side -- a live fight always has a battle
    block, and a build that stops sending one is a wire this tool should
    wait on and then report blocked, never draw a round 0 from.
    """
    if state.get("state_type") is None:
        return "the wire answered with no `state_type` key"
    if str(state.get("state_type")) == "unknown":
        return "the wire could not name this screen"
    if _combat_torn_down(state):
        return "the fight is over and the next screen is not up yet"
    if _chest_opening(state):
        return "the chest is still opening"
    if (str(state.get("state_type")) in COMBAT_SCREENS
            and _blob(state, "battle").get("is_play_phase") is False):
        return "the game has not handed the turn back to the player yet"
    return ""


def _combat_torn_down(state: dict[str, Any]) -> bool:
    """`EB-178`: a combat screen whose `battle` block the game has removed."""
    return (str(state.get("state_type")) in COMBAT_SCREENS
            and not isinstance(state.get("battle"), dict))


def _chest_opening(state: dict[str, Any]) -> bool:
    """`EB-263`: a treasure room the bridge caught mid-open.

    `BuildTreasureState` answers a BARE `{message}` twice -- once while the
    room is still loading and once for the frame in which it force-clicks the
    chest itself -- and writes `relics` only after the relic collection is
    visible (`McpMod.StateBuilder.cs:2384-2427`). So the opening frame carries
    no relics, no `can_proceed` and nothing to choose.

    CAPTURED LIVE, 2026-09-02: `{"treasure": {"message": "Opening chest..."}}`
    and no other key, which is byte for byte what the r3 Opus seat was handed
    -- "The screen printed `# An open chest` with a blank body, and advertised
    `choose \"<relic>\"` with no relics listed ... I never saw whether the
    chest contained anything or whether I received it." Riding it out is what
    it needs: the fixture is beside this file's tests, and the frame is gone in
    under a second.

    Checked on the ABSENCE of `relics` rather than on the message's words: the
    message is loc-free English written by the bridge and a wording pass would
    move it, and a chest that has BOTH a message and a relic list has a screen
    to draw.
    """
    if str(state.get("state_type")) != "treasure":
        return False
    blob = _blob(state, "treasure")
    return bool(_text(blob.get("message"))) and "relics" not in blob


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


def _relics(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in (_player(state).get("relics") or [])
            if isinstance(r, dict)]


def relic_faces(state: dict[str, Any]) -> list[dict[str, str]]:
    """The run's relics as PRINTED name and one-line effect. `EB-238`.

    THE DEFECT THIS CLOSES. Until now the page showed a relic on the reward
    and relic-select screens -- the moment it is OFFERED -- and never again.
    So a blind reader played every combat of a run without the one part of
    the board that is on screen for the whole of it, and `KLEESPARK-BT1`
    §22.4 is what that cost: Klee's starter *Pounding Surprise* pays +1 Spark
    per Bomb detonated, the priced mode under test placed three Bombs, and
    the mode REFUNDED ITS OWN PRICE inside the turn in front of eight readers
    none of whom could see why. A registration cannot control a relic the
    page does not print.

    IT PRINTS WHAT THE GAME PRINTS AND NOTHING ELSE (R217's quarantine): the
    relic's own title and its own hover description, off the wire, exactly as
    the HUD shows them on a mouse-over. No id, no rarity, no pool, no sim
    hook name -- and the `counter` the wire carries only when the relic draws
    one on its own icon.
    """
    out: list[dict[str, str]] = []
    for r in _relics(state):
        name = _text(r.get("name")) or _label(r.get("id"))
        if not name:
            continue
        row = {"name": name, "text": _text(r.get("description"))}
        counter = r.get("counter")
        if counter is not None:
            row["counter"] = _text(counter)
        out.append(row)
    return out


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
        # `EB-186`, and the same number for the same reason as on the staged
        # page: at a full Spark bank the game draws EVERY Attack at 0 while
        # the rule frees one, so a page that prints only what the game draws
        # is a page offering plays the board will refuse. Read from the
        # shipped face in `klee-mod`; `None` where that face gives no number,
        # and an absent number prints nothing.
        # `EB-267`: KEYED BY ID. A prototype row may print a shipped card's
        # name at a different price -- `Flame Dance` is 2 shipped and 1 on the
        # proto surface -- and a title-keyed lookup told a blind reader the
        # cost on the card in front of them was wrong when nothing was. The id
        # is read here, on the tool side, and only the number crosses.
        "printed_cost": qa_packet.printed_cost_index().get(
            qa_packet.card_key(entry.get("id"))),
        # `EB-286`. THE SPARK HALF OF THE PRICE. `cost` above is the ENERGY
        # cost and it is 0 on every Spark-priced card, so a hand line built
        # from it alone printed `Bang Bang!` at `cost 0` while the board
        # refused it -- the r3 Opus seat called a card that "prints cost 0"
        # and "sat unplayable in my hand across two entire fights" a trap,
        # and half of that was this render. Same index and same id key the
        # staged page uses (`printed_spark`, `EB-282`), so the two pages
        # cannot say different things about one price; the WIRE's own
        # `spark_price` is the fallback, because a hand entry carries it live
        # (`BuildCardState`, the GItS local edit) and a reward or shop row
        # never does. `None` where neither answers, and an absent price
        # prints nothing.
        "printed_spark": (
            qa_packet.printed_spark_index().get(
                qa_packet.card_key(entry.get("id")))
            or (_int(entry.get("spark_price"))
                if entry.get("spark_price") is not None else None)),
        "kind": _text(entry.get("type")),
        "upgraded": bool(entry.get("is_upgraded") or entry.get("upgraded")),
        "keywords": kws,
        "playable": entry.get("can_play") is not False,
        "unplayable_reason": _text(entry.get("unplayable_reason_text")
                                   or entry.get("unplayable_reason")),
    }


# `EB-262`, AND IT IS THE WHOLE ROW. A SHOP ITEM CARRIES ITS NAME UNDER ITS
# CATEGORY'S OWN KEY. `BuildShopState` (`McpMod.StateBuilder.cs:1636`) emits
# one flat row per shelf item -- `category`, `price`, `is_stocked`,
# `can_afford` -- and then merges the thing's face in under a PREFIXED
# spelling: `card_name` / `card_description`, `relic_name` /
# `relic_description`, `potion_name` / `potion_description`. None of those is
# `name`, so every item on both of the run's shops rendered as `(unnamed)` and
# `buy` answered *"nothing here is called '(unnamed)'"* at a tester holding
# 164 gold. The event screen has the same shape for an option that hands over
# a relic (`optData["relic_name"]`, `:1553`).
#
# So the readers below are ORDERED lists rather than one key, and the first
# that answers wins -- the plain spelling first, so nothing that already
# worked changes.
_OPTION_NAME_KEYS = ("name", "title", "label", "display_name",
                     "card_name", "relic_name", "potion_name")
_OPTION_TEXT_KEYS = ("description", "body", "text",
                     "card_description", "relic_description",
                     "potion_description")
# Read only when the entry printed no name of its own: the shop's card-removal
# shelf carries no model and therefore no title, and `Card Removal` is
# `qa_packet.label`'s rendering of the wire's own word for it, not a label
# invented here.
_OPTION_KIND_KEYS = ("type", "kind", "room_type", "category")


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
    for key in _OPTION_NAME_KEYS:
        if _text(entry.get(key)):
            name = _text(entry.get(key))
            break
    if not name:
        for key in _OPTION_KIND_KEYS:
            if entry.get(key):
                name = _label(entry.get(key))
                break
    text = ""
    for key in _OPTION_TEXT_KEYS:
        if _text(entry.get(key)):
            text = _text(entry.get(key))
            break
    enabled = True
    for key in ("is_enabled", "enabled"):
        if entry.get(key) is False:
            enabled = False
    # `is_stocked: false` is a shelf whose item has already been bought. The
    # game greys it; the page says so rather than offering a purchase the
    # bridge will refuse.
    if entry.get("is_stocked") is False:
        enabled = False
    if entry.get("is_locked"):
        enabled = False
    # `EB-262`. A SHOP CARD SHELF CARRIES THE CARD'S ENERGY COST, and it is
    # under the same prefixed spelling its name is: `card_cost`
    # (`BuildShopState`, `McpMod.StateBuilder.cs:1686`). Nothing here read it,
    # so the r3 Opus seat bought The Big One for 73 gold and "only discovered
    # it costs 3 energy -- a whole turn -- when I next saw it on a
    # card-selection screen".
    #
    # The SPARK half cannot come off the shelf: `spark_price` is emitted on a
    # HAND card only (`BuildCardState`), so a shelf is read through the same
    # id-keyed index the hand and the reward rows use. `card_id` is the only
    # key that names a card here, which is also what keeps this lookup off a
    # rest option or a map node -- those carry no `card_id` and get nothing.
    card_id = entry.get("card_id")
    energy = ""
    for key in ("card_cost", "energy_cost"):
        if _text(entry.get(key)):
            energy = _text(entry.get(key))
            break
    spark = (qa_packet.printed_spark_index().get(qa_packet.card_key(card_id))
             if card_id is not None else None)
    cost = qa_packet.cost_label({"cost": energy, "printed_spark": spark})
    # `EB-262`, the other half, AND IT IS NOT OURS TO FIX. A card shelf's
    # name, text and cost all live behind `entry.CreationResult?.Card`, and
    # `MerchantCardEntry.IsStocked` IS `CreationResult != null` -- so the
    # moment a card is bought the game clears the only field the shelf's face
    # was ever read from, and the bridge emits a row with a price and nothing
    # else. The page used to fall back to the shelf's category and print
    # `**Card** - 73 gold`, which reads as a card called "Card". It says what
    # is true instead.
    empty_shelf = (entry.get("category") == "card"
                   and entry.get("is_stocked") is False
                   and not _text(entry.get("card_name")))
    note = ""
    if empty_shelf:
        name = "(this shelf is empty)"
        note = ("Bought, or never stocked. The game clears a shelf's card the "
                "moment it is sold, and the name, the text and the cost all "
                "live on that card, so nothing on the feed can say which one "
                "it was.")
    return {
        "name": name,
        "text": text,
        "enabled": enabled,
        "cost": cost if cost != "-" else "",
        "note": note,
        "price": _int(entry.get("price", entry.get("cost")), 0)
        if entry.get("price") is not None or entry.get("cost") is not None
        else None,
    }


def _number_faces(faces: list[dict[str, Any]], field: str
                  ) -> list[dict[str, Any]]:
    """`_number_names` over one field of a list of already-built faces."""
    for face, name in zip(faces, _number_names([f[field] for f in faces])):
        face[field] = name
    return faces


def _powers(blob: dict[str, Any]) -> list[dict[str, Any]]:
    """`qa_packet._powers` plus the `type` the wire has always carried.

    `EB-179`. A status row on the wire is exactly `id`, `name`, `amount`,
    `type`, `description`, `keywords` -- no duration and no expiry anywhere.
    `type` is the one of those the page was dropping, and it is the game's
    own word for whether a thing on the board is helping or hurting, so it
    goes back on the line. The filter below MIRRORS `qa_packet._powers`'s
    skip rule (a row with no printed name is not a power the page shows), so
    the two lists stay index-aligned; they are one function's worth of logic
    living either side of a module boundary, and a change to one is a change
    to both.
    """
    out = qa_packet._powers(blob)
    kinds = [_text(row.get("type"))
             for row in (blob.get("status") or [])
             if isinstance(row, dict)
             and (_text(row.get("title")) or _label(row.get("name")))]
    for power, kind in zip(out, kinds):
        power["kind"] = kind
    return out


def _intent(blob: Any) -> dict[str, str]:
    return qa_packet._intent(blob)


# ------------------------------------------------------------ observations --

def _combat(state: dict[str, Any]) -> dict[str, Any]:
    p = _player(state)
    resources = p.get("resources")
    battle = _blob(state, "battle")
    combat = {
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
            # `EB-238`. ON THE COMBAT PAGE, not only where a relic is offered.
            # The HUD carries the relic row through every screen of the run;
            # the page did not, and `KLEESPARK-BT1` paid for it.
            "relics": relic_faces(state),
        },
        "round": _int(battle.get("round")),
        "hand": _number_faces([_card_face(c) for c in _hand(state)], "title"),
        # `EB-179`: whether the hand holds two cards printing one name, which
        # is the ONE place the missing enchantment field bites a reader.
        "hand_repeats": len({_fold(_text(c.get("name")))
                             for c in _hand(state)}) < len(_hand(state)),
        "piles": {"draw": _int(p.get("draw_pile_count")),
                  "discard": _int(p.get("discard_pile_count")),
                  "exhaust": _int(p.get("exhaust_pile_count"))},
        "enemies": _number_faces(
            [{"name": _text(e.get("name")),
              "hp": _int(e.get("hp")),
              "max_hp": _int(e.get("max_hp", e.get("hp"))),
              "block": _int(e.get("block")),
              "intent": _intent(e.get("intents") or e.get("intent")),
              "powers": _powers(e)} for e in _enemies(state)], "name"),
    }
    # `EB-186`: the once-per-screen Spark line, built from the printed powers
    # and the printed hand this screen already carries. Empty -- and so
    # printed nowhere -- on every screen where no card is being shown cheaper
    # than the cost on its face.
    combat["spark_note"] = qa_packet.spark_note(combat["you"]["powers"],
                                                combat["hand"])
    memory = kurage_memory(p)
    if memory is not None:
        combat["memory"] = memory
    plans = kokomi_plans(p)
    if plans is not None:
        combat["plans"] = plans
    return combat


def kokomi_plans(player: dict[str, Any]) -> dict[str, Any] | None:
    """The pending Plans as the observed board sees them (`EB-216`).

    THE ABSENT / EMPTY SPLIT IS THE SAME ONE `kurage_memory` MAKES, and for the
    same reason: an ABSENT key is "no Plan rule in this build", an EMPTY map is
    "the rule is here and this seat is not playing it", and a POPULATED map is
    her queue. `None` here keeps the section off the page in both of the first
    two cases -- a Klee at this table must not be shown an empty jellyfish.

    Emitted by `vendor/STS2_MCP/gits/GitsKokomiPlan.cs`, which lifts it by
    reflection from `KleeMod.Powers.KokomiPlan.Snapshot`. Every field name below
    is that method's, and the two together are the contract:

      pet / pet_name / pet_entity_id -- the Bake-Kurage, and the id a play aims
        at. `pet_entity_id` is null on a board with no jellyfish, which is a
        state rule 1 says cannot happen and this reader does not assume.
      pending -- how many Plans are waiting.
      twice -- Nereid's Ascension is up, so every Plan below happens TWICE. It
        is the one thing that makes the count stop being the number of things
        that will happen, which is why it is a field and not an inference.
      also_now -- The Moon Overlooks the Waters is out, so a Plan written this
        turn also happens immediately.
      queue -- ordered, front first: the card's name and how many clauses its
        Plan line carries.
    """
    raw = player.get("kokomi_plans")
    if not isinstance(raw, dict) or not raw:
        return None
    queue = [{"name": _text(row.get("name")),
              "clauses": _int(row.get("clauses"))}
             for row in (raw.get("queue") or []) if isinstance(row, dict)]
    pet_id = raw.get("pet_entity_id")
    return {
        "pet": bool(raw.get("pet")),
        "pet_name": _text(raw.get("pet_name")) or "Bake-Kurage",
        "pet_entity_id": None if pet_id is None else _text(pet_id),
        "pending": _int(raw.get("pending")),
        "twice": bool(raw.get("twice")),
        "also_now": bool(raw.get("also_now")),
        "queue": queue,
    }


def _pulse_phrase(memory: dict[str, Any]) -> str:
    """What the jellyfish will do at the end of THIS turn, in words.

    The pulse is keyed to the type of the last card she played, so it is a
    forecast the player can still change -- which is the whole reason it has to
    be on the page before the turn ends (D4).
    """
    amount, unit = memory["pulse_amount"], memory["pulse_unit"]
    if unit == "none":
        return "do nothing, because you have played no card this turn"
    if unit == "damage":
        return f"deal {amount} Hydro damage"
    if unit == "block":
        return f"give you {amount} Block"
    if unit == "charge":
        return f"give you {amount} Charge"
    return "apply Hydro"


def kurage_memory(player: dict[str, Any]) -> dict[str, Any] | None:
    """The Kurage's memory as the observed board sees it (`EB-181`).

    THE WIRE KEY IS ABSENT ON A BUILD WITHOUT THE RULE, and that absence is
    load-bearing: the rule is quarantined behind the mod's prototype compile
    switch, so a release build has no memory and must not be described as
    having an empty one. `None` here keeps `memory` off the observed board
    entirely; an empty QUEUE with a bank is a real state and IS reported.

    AN EMPTY MAP IS AN ABSENT MEMORY TOO (`EB-207`), and this is the second
    half of the same contract rather than a new rule. The bridge header spells
    three states, not two: an ABSENT key is "no memory rule in this build", an
    EMPTY MAP is "the rule is here and this player is not Kokomi" -- which is
    exactly what `KurageMemory.Snapshot` returns off a seat that fails
    `IsLive` -- and a POPULATED map is a memory. This reader only ever split
    the first from the rest, so on a KLEE run every combat page grew a
    "The Bake-Kurage's memory" heading built entirely out of `_int`/`_text`
    defaults: Charge 0, an empty queue, and a pulse of `none` rendered as
    "you have played no card this turn". The blind tester on the Klee
    whole-fight run reported that sentence as the most confusing thing on the
    screen, and it was describing a jellyfish Klee does not have.

    A Kokomi seat's memory is never empty as a MAP -- `Snapshot` writes twelve
    keys before it writes the queue -- so refusing `{}` cannot suppress a real
    one. The queue being empty is a different fact and still reaches the page.

    Emitted by `vendor/STS2_MCP/gits/GitsKurageMemory.cs`, which lifts it by
    reflection from `KleeMod.Powers.KurageMemory.Snapshot`. Every field name
    below is that method's, and the two together are the contract:

      bank / front_price / blocked / fires_next / empty / summon -- the meter,
        and the target it now has. `front_price` is null on an empty queue,
        which is the honest reading of "no ceiling" rather than a zero.
      base_kit -- the jellyfish was INSTALLED at fight start rather than
        summoned by a card, so it is on the field before turn 1 and there is
        no state in which it is absent.
      pulse_kind / pulse_amount / pulse_unit -- what the jellyfish will do at
        the end of THIS turn, so a seat can forecast its own turn end.
        `pulse_unit` can read `charge`, because the Power branch pays in Charge
        rather than in damage or Block.
      reading -- the ONE-LINE reading, verbatim. Kept on the wire because the
        rule still computes it, but the PAGE no longer prints it: sec.14
        replaced the strip with an element whose facts stand one per line.
      run_out_index -- sec.14.4's running subtraction over the queue: the index
        of the first entry the bank cannot reach, and -1 when it covers the
        whole queue. It is the pile view's own colouring, on the wire so the
        page and the screen cannot drift about where the Charge stops.
      queue -- ordered, front first: name, cost, price, target ("random" when
        the memory stored none), blocked, affordable, ephemeral, rule.

    THE WIRE'S PER-ROW `state` IS DELIBERATELY NOT CARRIED. `Snapshot` sends one
    -- "payable" / "runs_out" / "held", the pile view's own colouring -- and it
    is an INTERNAL SNAKE-CASE ID, which `qa_packet.assert_blind` refuses on the
    observed board and is right to: a blind tester must never be handed a
    developer's vocabulary. `run_out_index` says the same thing as a number,
    and the page turns it into a sentence.
    """
    raw = player.get("kurage_memory")
    if not isinstance(raw, dict) or not raw:
        return None
    queue = []
    for row in (raw.get("queue") or []):
        if not isinstance(row, dict):
            continue
        queue.append({
            "name": _text(row.get("name")),
            "cost": _int(row.get("cost")),
            "price": _int(row.get("price")),
            # A memory that stored no target aims randomly, and the board says
            # so in the word the strip uses rather than leaving a null for a
            # reader to interpret.
            "target": _text(row.get("target")) or "random",
            "blocked": bool(row.get("blocked")),
            "affordable": bool(row.get("affordable")),
            "ephemeral": bool(row.get("ephemeral")),
            "rule": _text(row.get("rule")),
        })
    front_price = raw.get("front_price")
    return {
        "bank": _int(raw.get("bank")),
        "front_price": None if front_price is None else _int(front_price),
        "blocked": bool(raw.get("blocked")),
        "fires_next": bool(raw.get("fires_next")),
        "empty": bool(raw.get("empty")),
        "summon": bool(raw.get("summon")),
        # The install as a FIGHT-START FACT, so a blind run can see the
        # jellyfish before turn 1 rather than inferring it from the first
        # pulse. `summon` says it is on the field; this says nobody summoned
        # it -- it is base kit, and there is no state where it is absent.
        "base_kit": bool(raw.get("base_kit")),
        "pulse_kind": _text(raw.get("pulse_kind")) or "none",
        "pulse_amount": _int(raw.get("pulse_amount")),
        "pulse_unit": _text(raw.get("pulse_unit")) or "none",
        "reading": _text(raw.get("reading")),
        # -1 rather than None on a wire that never sent the field: "the bank
        # covers everything queued" is the safe reading, and an empty queue
        # says the same thing.
        "run_out_index": _int(raw.get("run_out_index", -1)),
        "queue": queue,
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


def _preview_cards(state: dict[str, Any], st: str) -> list[dict[str, Any]]:
    """The card(s) a selection screen is SHOWING AS PICKED, if it shows any.

    `EB-263`. The only selection state the wire carries: `preview_cards`, and
    only while `preview_showing` is true. A screen without a preview container
    -- the deck enchant picker is one -- sends nothing at all, and that is
    what `SELECTION_NOTE` is for.
    """
    return [c for c in _listing(state, f"{st}.preview_cards")
            if isinstance(c, dict)]


def _rest_options(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "rest_site.options", "options")


def _event_options(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "event.options", "options")


def _proceed_option(state: dict[str, Any]) -> int:
    """The list position of the event option that IS *Proceed*, or `-1`.

    `EB-259`. Two readings, in this order, and no third: the wire's own
    `is_proceed` flag, which `BuildEventState` sets off the button's model
    (`McpMod.StateBuilder.cs:1490`), and failing that an option the screen
    PRINTS as *Proceed*. Ambiguity is not resolved -- two proceed-ish options
    answer `-1` and the tester is asked to name one, because picking between
    two buttons is the decision this tool exists not to make.
    """
    options = _event_options(state)
    flagged = [i for i, o in enumerate(options)
               if isinstance(o, dict) and o.get("is_proceed")]
    if len(flagged) != 1:
        named = [i for i, o in enumerate(options)
                 if _fold(_named_option(o)["name"]) == "proceed"]
        flagged = named
    if len(flagged) != 1:
        return -1
    return flagged[0] if _named_option(options[flagged[0]])["enabled"] else -1


def _reward_items(state: dict[str, Any]) -> list[Any]:
    return _listing(state, "rewards.items", "rewards")


def _relic_options(state: dict[str, Any]) -> list[Any]:
    """The relics a chest or a relic-select screen is offering.

    `EB-263`. THE CHEST'S RELICS ARE UNDER THE SCREEN'S OWN BLOB, and this
    read had only the top-level spellings. `BuildTreasureState`
    (`McpMod.StateBuilder.cs:2362`) writes `treasure.relics` and
    `BuildRelicSelectState` (`:2230`) writes `relic_select.relics`, each row
    carrying `name`, `description` and its own `index`. Reading `state["relics"]`
    found neither, so an opened chest rendered as `# An open chest` with
    nothing under it while still advertising `choose "<relic>"`: the tester
    could only `proceed` and never learned whether a relic had been taken.
    The screen blobs go FIRST because they are what the wire actually sends;
    the two bare spellings stay behind them so a state saved before this is
    still readable.
    """
    return _listing(state, "treasure.relics", "relic_select.relics",
                    "relics", "options")


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
    elif st in COMBAT_SCREENS and _combat_torn_down(state):
        # `EB-178`, belt and braces. `settle` rides this out in well under a
        # second, but a wire that got STUCK here must be reported as stuck --
        # the one thing it must never do is render `Battle -- round 0` with an
        # empty hand, which is the fight-that-never-was run B6 recorded twice.
        obs["screen"] = "combat"
        obs["blocked"] = ("the fight is over and the game has not put up the "
                          "next screen; nothing here can be played")
    elif st in COMBAT_SCREENS:
        obs["screen"] = "combat"
        obs["combat"] = _combat(state)
        obs["commands"] = ['play "<card title>" [on "<enemy>"]',
                           'use potion "<potion>" [on "<enemy>"]',
                           "end turn"]
        # `EB-216`, the Kokomi draft-6 half. The jellyfish is a TARGET, and
        # naming it is how a Plan is written -- so the grammar has to say so
        # on the screen where it can be used, and only there. A board with no
        # pet never sees this line.
        plans = obs["combat"].get("plans")
        if plans and plans.get("pet"):
            obs["commands"].insert(
                1, f'play "<card title>" on "{plans["pet_name"]}"'
                   "   (writes its Plan instead of playing it now)")
    elif st == "map":
        obs["screen"] = "map"
        obs["nodes"] = _map_options(state)
        obs["commands"] = ['go "<node>"']
    elif st == "card_reward":
        blob = _blob(state, "card_reward")
        obs["screen"] = "card_reward"
        obs["prompt"] = _text(blob.get("prompt")) or "Add a card to your deck."
        obs["offers"] = _number_faces(
            [_card_face(c) for c in _screen_cards(state)], "title")
        obs["can_skip"] = blob.get("can_skip") is not False
        obs["commands"] = ['choose "<card title>"', "skip"]
    elif st in SELECT_SCREENS:
        blob = _blob(state, st)
        obs["screen"] = "card_select"
        obs["prompt"] = _text(blob.get("prompt")) or "Choose a card."
        obs["offers"] = _number_faces(
            [_card_face(c) for c in _screen_cards(state)], "title")
        # `EB-263`. WHAT THE SCREEN SAYS IS PICKED, where it says anything.
        # `BuildCardSelectState` puts the chosen card(s) in `preview_cards`
        # while a preview container is open (`McpMod.StateBuilder.cs:2021`),
        # and that is the ONLY selection state on the wire -- no grid row
        # carries a selected flag. The upgrade and transform screens open a
        # preview and therefore have one; the enchant picker does not, which
        # is `SELECTION_NOTE` below.
        obs["selected"] = _number_faces(
            [_card_face(c) for c in _preview_cards(state, st)], "title")
        obs["can_confirm"] = bool(blob.get("can_confirm"))
        obs["can_skip"] = bool(blob.get("can_skip") or blob.get("can_cancel"))
        # `EB-259`. THE PAGE MAY NOT OFFER WHAT THE STATE WILL REFUSE. This
        # screen said *Confirm is not available* in its body and listed
        # `confirm` under "What you can say" three lines later; the tester
        # typed it, the screen had already advanced on its own, and the
        # command came back *"there is nothing waiting to be confirmed"*. The
        # wire answers the question outright (`can_confirm` /
        # `can_cancel`, `McpMod.StateBuilder.cs:2065`), so the grammar offered
        # is the grammar the wire says will work -- and `_confirm` / `_skip`
        # still refuse on their own, because a screen can move between the
        # render and the command.
        obs["commands"] = ['choose "<card title>"']
        if obs["can_confirm"]:
            obs["commands"].append("confirm")
        if obs["can_skip"]:
            obs["commands"].append("skip")
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
        # `EB-263`. THE VERBS WERE A CONSTANT. A SPENT rest site sends an
        # empty `options` list -- the room drops them once one is taken -- and
        # this screen still printed `choose "<option>"`, `rest`, `upgrade` and
        # `remove` over nothing at all: "Four verbs and nothing to choose"
        # (r3 Opus seat). Each verb is now offered only when an ENABLED option
        # answers to it, by the same keyword match `_rest_keyword` resolves
        # with, so the grammar on the page is the grammar the screen will
        # take. `proceed` is always last and always there: it is the one
        # button a rest site has whatever else it has.
        obs["commands"] = []
        live = [o for o in obs["options"] if o["enabled"]]
        if live:
            obs["commands"].append('choose "<option>"')
        for verb, words in (("rest", ("rest", "sleep", "heal")),
                            ("upgrade", ("upgrade", "smith", "forge")),
                            ("remove", ("remove", "purge", "toss"))):
            if any(any(w in _fold(o["name"]) for w in words) for o in live):
                obs["commands"].append(verb)
        # A FRESH rest site sends `can_proceed: false` -- the room will not let
        # you leave until its one choice is taken -- and a SPENT one sends
        # `true` with an empty option list. Captured live, both of them
        # (`review/qa/blindplay/eb263-live-shapes/`). The fallback is the
        # safety rail: a screen this tool can say nothing at all about is worse
        # than a verb that might be refused.
        if _blob(state, "rest_site").get("can_proceed") is not False                 or not obs["commands"]:
            obs["commands"].append("proceed")
    elif st == "event":
        ev = _blob(state, "event")
        obs["screen"] = "event"
        obs["title"] = _text(ev.get("event_name"))
        obs["text"] = _text(ev.get("body") or ev.get("text")
                            or ev.get("description"))
        obs["in_dialogue"] = bool(ev.get("in_dialogue"))
        obs["options"] = [_named_option(o) for o in _event_options(state)]
        # `EB-259`, the other half. An event room has NO proceed button --
        # `ExecuteProceed` walks rewards, rest, both merchants and the
        # treasure room and stops (`McpMod.Actions.cs:600-663`) -- so a bare
        # `proceed` here posted an action the game answered *"No proceed
        # button available or enabled"*, and a run lost two actions to it. The
        # verb is still offered, because an event whose only button reads
        # *Proceed* is exactly where a player would type it; `_proceed`
        # resolves it to THAT PRINTED OPTION instead of the proceed action.
        obs["commands"] = ['choose "<option>"']
        if obs["in_dialogue"] or _proceed_option(state) >= 0:
            obs["commands"].append("proceed")
    elif st == "rewards":
        obs["screen"] = "rewards"
        obs["items"] = [_named_option(r) for r in _reward_items(state)]
        obs["commands"] = ['choose "<reward>"', "proceed"]
    elif st in ("treasure", "relic_select"):
        obs["screen"] = st
        obs["items"] = [_named_option(r) for r in _relic_options(state)]
        # `EB-263`, the chest half. `BuildTreasureState` writes `relics` ONLY
        # while the relic collection is on screen, and writes a `message`
        # instead while the chest is still opening or the room is still
        # loading (`McpMod.StateBuilder.cs:2381-2399`). The page had a reader
        # for neither case, so an empty chest rendered as `# An open chest`
        # with a blank body while still advertising `choose "<relic>"`: "I
        # never saw whether the chest contained anything or whether I received
        # it" (r3 Opus seat). The message is the feed's own sentence, printed
        # verbatim, and the verb is offered only when there is something to
        # aim it at.
        obs["message"] = _text(_blob(state, st).get("message"))
        obs["commands"] = []
        if any(i["enabled"] for i in obs["items"]):
            obs["commands"].append('choose "<relic>"')
        obs["commands"].append("skip" if st == "relic_select" else "proceed")
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
    # `EB-286`: the COST SLOT as the game paints it, energy and Spark
    # together, through the one formatter the staged page already uses.
    # `qa_packet.cost_label` answers `-` when the wire sent no cost at all,
    # which is the case this line has always printed nothing for.
    price = qa_packet.cost_label(c)
    bits = [b for b in (f"cost {price}" if price != "-" else "",
                        c["kind"].lower() if c["kind"] else "") if b]
    if bits:
        head += f" — {', '.join(bits)}"
    out = [head, f"    {c['text'] or '(no printed text)'}"]
    note = qa_packet.cost_note(c)
    if note:
        out.append(f"    {note}")
    for k in c["keywords"]:
        out.append(f"    *{k['name']}* — {k['text']}" if k["text"]
                   else f"    *{k['name']}*")
    if not c["playable"]:
        # `EB-264`. The wire's reason is an ENUM NAME
        # (`McpMod.StateBuilder.cs:1324`), and `CANNOT BE PLAYED:
        # BlockedByCardLogic` told a blind tester nothing at all. The
        # translation lives in `qa_packet` so the staged page and this one
        # cannot say different things about one refusal; a reason the wire
        # spells as a sentence still comes through in the game's own words.
        out.append("    CANNOT BE PLAYED: "
                   + (qa_packet.unplayable_reason(c["unplayable_reason"])
                      or "the game gives no reason"))
    return out


# `EB-179`. THREE LEGIBILITY GAPS RUN B6 REPORTED, AND WHAT THE WIRE ACTUALLY
# CARRIES FOR EACH. Read off the live bridge on 2026-08-29 and confirmed
# against the vendored builder, so these lines state a fact about the feed and
# not a guess:
#
#   POWERS -- a status row is `id`, `name`, `amount` (the game's own
#     `DisplayAmount`), `type`, `description` (the game's own resolved
#     `SmartDescription`) and `keywords`. There is NO duration or expiry
#     field. Where the game states a duration it is inside the printed text
#     (`Vulnerable 3`: "...for 3 turns"); where it does not, nothing else
#     says it either (`Thorns 3`: "When hit by an attack, deal 3 damage
#     back."), which is the Toadpole's Thorns that came and went unexplained.
#     So: print the `type` the page was dropping, and say the rest out loud.
#
#   METERS -- the resource snapshot reflects each registered resource's `Id`
#     and `Amount` and nothing else. There is no maximum and no spend rule on
#     the wire, so a meter cannot print one.
#
#   ENCHANTMENTS -- the card builder emits `id`, `name`, `type`, `cost`,
#     `star_cost`, `description`, `rarity`, `is_upgraded` and `keywords`. No
#     enchantment field exists, and run B6's live evidence says an enchant
#     reaches none of the fields that do. Filed as a bridge gap rather than
#     patched here. The note is printed only where it bites -- a hand holding
#     two cards that print one name, where the reader can SEE two faces and
#     the page cannot tell them apart.
#
# Each line says what is missing and whose it is to carry. None of them
# invents a number, and none names a register id -- the page is scrubbed.
POWER_NOTE = ("*A power's number is what the game's data feed reports for it. "
              "The feed carries no duration and no expiry, so unless a "
              "power's own text says when it ends, this page cannot say "
              "either.*")
METER_NOTE = ("the game's data feed carries this meter's amount only: no "
              "maximum, and no rule for how it is spent")
# `EB-263`. THE ENCHANT PICKER MARKS NOTHING, and the r3 Opus seat found out
# the hard way: after `choose "Flame Dance"` "the whole list reprinted
# byte-identically; the only change anywhere on the screen was the footer
# going from `Confirm is not available.` to `Confirm is available.`". The
# reason is on the bridge and not here -- `BuildCardSelectState` reads every
# grid card through `BuildCardInfo`, which has no selected flag, and the
# enchant screen opens no preview container for `preview_cards` to hold. So
# the page says which signal it HAS rather than implying it has none.
SELECTION_NOTE = ("*This screen's data feed carries no per-card selection "
                  "state, so nothing in the list above can be marked as the "
                  "one you picked. The `Confirm is` line below is the only "
                  "thing that moves when a pick lands.*")

HAND_REPEAT_NOTE = ("*Two cards here print the same name. The game's data "
                    "feed does not report a card's enchantment, so if one of "
                    "them is enchanted, this page cannot show which.*")


def _render_power(power: dict[str, Any], indent: str) -> str:
    """One power: printed name, the amount, buff or debuff, the printed text."""
    line = f"{indent}{power['name']} {power['stacks']}"
    kind = str(power.get("kind") or "").strip().lower()
    if kind:
        line += f" ({kind})"
    if power["text"]:
        line += f" — {power['text']}"
    return line


def _render_options(items: list[dict[str, Any]], bullet: str = "-") -> list[str]:
    out = []
    for o in items:
        line = f"{bullet} **{o['name'] or '(unnamed)'}**"
        # `EB-262`: the card's own cost first, then the gold, because they are
        # two different prices and a row that printed only the gold is what
        # bought a 3-energy card blind.
        bits = [b for b in (f"cost {o['cost']}" if o.get("cost") else "",
                            f"{o['price']} gold"
                            if o.get("price") is not None else "") if b]
        if bits:
            line += " — " + ", ".join(bits)
        if not o.get("enabled", True):
            line += " (not available)"
        out.append(line)
        if o.get("text"):
            out.append(f"    {o['text']}")
        if o.get("note"):
            out.append(f"    *{o['note']}*")
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
            out.append(f"- {name}: {amount} — {METER_NOTE}")
        for pw in you["powers"]:
            out.append(_render_power(pw, "- "))
        out.append(f"- Piles: {c['piles']['draw']} in the draw pile, "
                   f"{c['piles']['discard']} discarded, "
                   f"{c['piles']['exhaust']} exhausted")
        # `EB-238`. IN THE HEADER, with HP and Energy, because that is where
        # the game keeps it: the relic row sits along the top of every screen
        # of a run, and a reader who is shown it only when one is OFFERED has
        # been shown the shop and not the board.
        if you["relics"]:
            out += ["", "## Your relics", ""] + [
                f"- **{r['name']}**"
                + (f" ({r['counter']})" if r.get("counter") else "")
                + (f" — {r['text']}" if r["text"] else "")
                for r in you["relics"]]
        if c.get("plans"):
            # `EB-216`, the Kokomi draft-6 half, and the page's contract is
            # `EB-198`'s lesson restated: ONE FACT PER LINE. The strip that
            # preceded this put a bank, a price and a state into one sentence
            # with three grammars and both readings of it were true; what
            # replaced it says the jellyfish is there, then what is waiting on
            # it, then in what order.
            #
            # THE ORDER IS THE ELEMENT'S. The HUD draws the pending Plans face
            # up, front at the top, so the page numbers them the same way -- a
            # blind reader is given what a sighted player sees and nothing
            # else.
            pl = c["plans"]
            out += ["", f"## The {pl['pet_name']}", ""]
            if pl["pet"]:
                out.append(f"- The {pl['pet_name']} is on the field for the "
                           "whole fight. Enemies cannot touch it. Play a card "
                           "on it to write its **Plan** line instead of "
                           "playing the card now.")
            if not pl["queue"]:
                out.append("- Nothing is planned. The morning is empty.")
            else:
                out.append(
                    f"- Planned, and carried out at the start of your next "
                    f"turn in this order ({pl['pending']}):")
                for i, e in enumerate(pl["queue"], 1):
                    out.append(f"  {i}. **{e['name']}**")
                if pl["twice"]:
                    out.append("- The jellyfish carries out EVERY Plan twice "
                               "while Nereid's Ascension lasts.")
            if pl["also_now"]:
                out.append("- Plans also happen NOW as you write them.")
        if c.get("memory"):
            # `EB-181`, rewritten for the memory CARD that replaced the strip
            # (review/ruled/kokomi-kurage-memory-2026-08-29.md §14). The page
            # mirrors THE ELEMENT'S facts, in the element's own order, because
            # a blind reader must be given what a sighted player sees and
            # nothing else:
            #
            #   1. the Charge count -- the big number under the card;
            #   2. the FRONT card, its price, and whether it fires next turn --
            #      the blue/red ring, which is one comparison and no forecast;
            #   3. the queue, in order, as the pile view shows it on a click,
            #      with the run-out called out.
            #
            # `EB-198` is why the first two are separate lines. The strip put
            # the bank, the price and the state into one sentence with three
            # grammars ("Charge 1 / 0"), and the tester read a free front as a
            # fraction over zero and an empty memory as a contradiction of the
            # Charge it had just been shown. Both frames were TRUE. One fact
            # per line is the repair.
            m = c["memory"]
            out += ["", "## The Bake-Kurage's memory", ""]
            if m["base_kit"]:
                out.append("- The Bake-Kurage is on the field for the whole "
                           "fight. Nothing summons it and nothing removes it.")
            out.append(f"- Charge: {m['bank']}")
            if m["queue"]:
                front = m["queue"][0]
                price = ("costs nothing" if not front["price"]
                         else f"costs {front['price']} Charge")
                if m["blocked"]:
                    state = ("you cannot pay it, so NOTHING in the memory "
                             "fires next turn")
                else:
                    state = "it fires at the start of your next turn"
                out.append(f"- Next to fire: **{front['name']}** — {price} — "
                           f"{state}.")
                # `EB-214` item 7 (`M55`, re-scoped by R224): the pile
                # view's own header line. The page's contract above is the
                # element's facts in the element's order, and item 3 is "the
                # queue, as the pile view shows it on a click" -- the header
                # is part of that view, and a reader who cannot click gets it
                # here or nowhere. The screen's sentence VERBATIM, with the
                # rate off the same constant `KurageMemoryText.ChargeSource`
                # interpolates (`lint_constant_parity` pins the pair equal),
                # so the two surfaces cannot drift on a retune.
                out.append(
                    f"- Opening the memory shows “{CHARGE_SOURCE_LINE}”, "
                    "and then the whole memory, front first:")
                for i, e in enumerate(m["queue"], 1):
                    price = "free" if not e["price"] else f"{e['price']} Charge"
                    out.append(f"  {i}. **{e['name']}** — {price} — "
                               f"aims at {e['target']}")
                # §14.4's running subtraction, the pile view's own colouring:
                # blue while the bank still reaches, red from the shortfall AND
                # every entry behind it. -1 means the bank covers the queue.
                run_out = m.get("run_out_index", -1)
                if run_out is None or run_out < 0:
                    out.append("- Your Charge covers every memory queued, if "
                               "you spend none of it elsewhere.")
                else:
                    out.append(f"- Charge runs out at #{run_out + 1} "
                               f"(**{m['queue'][run_out]['name']}**): that one "
                               f"and everything behind it are held until the "
                               f"bank catches up.")
            else:
                out.append("- The memory is empty. Nothing is queued and "
                           "nothing fires next turn.")
            out.append(f"- At the end of this turn the jellyfish will "
                       f"{_pulse_phrase(m)}.")
        if you["potions"]:
            out += ["", "## Potions", ""]
            for p in you["potions"]:
                out.append(f"- **{p['title']}** — {p['text']}" if p["text"]
                           else f"- **{p['title']}**")
        out += ["", "## Your hand", ""]
        if c.get("spark_note"):
            out += [c["spark_note"], ""]
        for card in c["hand"]:
            out += _render_card(card)
        if not c["hand"]:
            out.append("- (your hand is empty)")
        if c.get("hand_repeats"):
            out += ["", HAND_REPEAT_NOTE]
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
                out.append(_render_power(pw, "    "))
        if you["powers"] or any(e["powers"] for e in c["enemies"]):
            out += ["", POWER_NOTE]
    elif obs["screen"] == "map":
        out += ["# The map", "",
                "Where you can go next:", ""] + _render_options(obs["nodes"])
    elif obs["screen"] in ("card_reward", "card_select"):
        out += [f"# {obs['prompt']}", ""]
        for card in obs["offers"]:
            out += _render_card(card)
        if obs["screen"] == "card_select":
            if obs.get("selected"):
                out += ["", "## What you have picked", ""]
                for card in obs["selected"]:
                    out += _render_card(card)
            elif obs["can_confirm"]:
                out += ["", SELECTION_NOTE]
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
            + (_render_options(obs["options"]) if obs["options"]
               else ["- (this rest site has nothing left to offer; "
                     "its choice has already been taken)"])
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
        out += [titles[obs["screen"]], ""]
        if obs.get("message"):
            out += [obs["message"], ""]
        out += (_render_options(obs["items"]) if obs["items"]
                else ["- (nothing here to take)"])
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


# -------------------------------------------------------- the wire snapshot -

# `EB-216` / `M56` (R224 A). THE OBJECTIVE SIDE OF A BLIND RUN.
#
# Two of the six thresholds a blind run is graded on need a fact the record
# did not carry. `P2` counts a tester's call against THAT TURN'S
# `blocked` / `fires_next` pair; `P6` asks whether an aim call was correct.
# `record.md` holds words -- the tester's own sentences -- and words cannot be
# counted against a board nobody wrote down. The grades already published
# STAND (R101b, R224 A); this is the channel the NEXT run has.
#
# THREE RULES, and each of them is why a field is shaped the way it is.
#
# 1. IT IS MACHINE-WRITTEN FROM THE WIRE, NOT FROM THE TESTER'S PAGE. The page
#    is a scrubbed, printed-faces-only render whose whole purpose is to hide
#    ids; a grader reading it back is reading a rendering of the board and not
#    the board. Every value below is lifted straight off the state the driver
#    already held when it posted, ids and all.
#
# 2. IT IS NEVER SHOWN TO THE TESTER. R101b: the tester's page is the grading
#    surface and this is the erratum reader's. It goes into the session record
#    and the gitignored log; nothing in `observation()` / `render()` consults
#    it, and no snapshot text is ever fed back as feedback.
#
# 3. IT INVENTS NO FIELD. Every key is one the API already serves --
#    `battle.round`, `player.energy`, `player.resources` (BaseLib's registered
#    meters, which is Charge / Encore / Fanfare / Burst), `player.status` (a
#    POWER-shaped meter, which is where Sparks ride), the hand's own `cost`
#    and `spark_price` / `spark_affordable`, `player.kurage_memory` (the queue
#    strip, `gits/GitsKurageMemory.cs`), and the enemies' `intents`. A build
#    without the prototype rule serves no `kurage_memory` and the key is
#    absent here too, which is the same three-state contract the bridge
#    header spells and `kurage_memory()` above honours.
#
# ALL METERS, INCLUDING THE ZEROES, unlike the observed board -- which prints
# only non-zero ones so a tester is not taught about a meter this screen does
# not show. A grader counting "the bank was empty when the call was made"
# needs the zero written down.


def _snapshot_hand(state: dict[str, Any]) -> list[dict[str, Any]]:
    """The hand as the wire has it: id, printed prices, playability."""
    out = []
    for c in _hand(state):
        row = {
            "id": _text(c.get("id")),
            "name": _text(c.get("name")),
            "kind": _text(c.get("type")),
            "energy_cost": _text(c.get("cost")),
            "upgraded": bool(c.get("is_upgraded") or c.get("upgraded")),
            "target_type": _text(c.get("target_type")),
            "can_play": c.get("can_play") is not False,
        }
        # OMITTED WHERE THE WIRE OMITS THEM, which is the bridge's own
        # contract: an absent pair means "this card charges no Sparks", and
        # writing 0 here would make a priced card and a free one look alike
        # to a grader counting affordable sinks.
        if c.get("spark_price") is not None:
            row["spark_price"] = _int(c.get("spark_price"))
            row["spark_affordable"] = bool(c.get("spark_affordable"))
        out.append(row)
    return out


def _snapshot_meters(state: dict[str, Any]) -> dict[str, Any]:
    """Every meter the character has, from the two places the API keeps them.

    `resources` is BaseLib's registered custom-resource registry (Charge,
    Encore, Fanfare, Burst and their riders). `powers` is the creature's own
    power list, which is where the Spark bank lives -- `spark` is a
    `PowerModel`, not a registered resource, and a snapshot that read only one
    of the two would silently lose whichever meter the character in front of
    it actually uses.
    """
    p = _player(state)
    resources = p.get("resources")
    powers = {}
    for row in (p.get("status") or []):
        if isinstance(row, dict) and _text(row.get("id")):
            powers[_text(row.get("id"))] = _int(row.get("amount"))
    return {
        "resources": ({_text(k): _int(v) for k, v in resources.items()}
                      if isinstance(resources, dict) else {}),
        "powers": powers,
    }


def wire_snapshot(state: dict[str, Any], *, index: int, verb: str,
                  command: str = "") -> dict[str, Any]:
    """One turn of the board, off the wire, for the grader and nobody else.

    Taken from the state the seat ACTED ON -- pre-post, the board the decision
    was made against -- because every threshold this exists for asks whether a
    call matched the board the caller could see.
    """
    p = _player(state)
    battle = _blob(state, "battle")
    enemies = _enemies(state)
    snap: dict[str, Any] = {
        "index": index,
        "verb": verb,
        "command": command,
        "state_type": _text(state.get("state_type")),
        "turn": _int(battle.get("round")),
        "battle_turn": _int(battle.get("turn")),
        "energy": _int(p.get("energy")),
        "max_energy": _int(p.get("max_energy")),
        "hp": _int(p.get("hp")),
        "max_hp": _int(p.get("max_hp")),
        "block": _int(p.get("block")),
        "meters": _snapshot_meters(state),
        "hand": _snapshot_hand(state),
        "piles": {"draw": _int(p.get("draw_pile_count")),
                  "discard": _int(p.get("discard_pile_count")),
                  "exhaust": _int(p.get("exhaust_pile_count"))},
        "enemy_count": len(enemies),
        "enemies": [{
            "entity_id": _entity_id(e),
            "name": _text(e.get("name")),
            "hp": _int(e.get("hp")),
            "max_hp": _int(e.get("max_hp", e.get("hp"))),
            "block": _int(e.get("block")),
            "intents": [{"type": _text(i.get("type")),
                         "label": _text(i.get("label")),
                         "title": _text(i.get("title"))}
                        for i in (e.get("intents") or [])
                        if isinstance(i, dict)],
        } for e in enemies],
    }
    # THE QUEUE STRIP, VERBATIM AND UNSCRUBBED. `kurage_memory()` above is the
    # PAGE's reading and deliberately drops the per-row `state` id; a grader is
    # entitled to the developer's vocabulary the page must not print, so the
    # raw map goes here. An absent key stays absent: no memory rule in this
    # build (`PROTOTYPE_CARDS` undefined) is a different fact from an empty
    # memory, and both differ from a populated one.
    memory = p.get("kurage_memory")
    if isinstance(memory, dict):
        snap["kurage_memory"] = memory
    return snap


# The two verbs a snapshot is taken on: every play, and every end of turn.
SNAPSHOT_VERBS = ("play", "end turn")


def ledger_rows(wire: Any, after_index: int = 0) -> tuple[list[dict[str, Any]],
                                                          str]:
    """The meter-ledger rows minted since `after_index`, and a note.

    `EB-216` / R225's clause. The mod keeps one ledger of every meter mutation
    routed through its own gain/spend chokepoints, each named by the ENGINE
    EVENT that made it. This is the read; `understudy.bridge.meter_ledger` is
    the route.

    THE NOTE IS RETURNED RATHER THAN RAISED, and the distinction it carries is
    the one the bridge is careful about: `unavailable` means this build has no
    klee mod to ask, and is a different fact from a ledger that exists and is
    empty. A wire that cannot answer at all is `error: ...` -- a snapshot with
    no ledger is still a snapshot, and a run must never die because an
    instrument did.
    """
    read = getattr(wire, "meter_ledger", None)
    if read is None:
        return [], "no ledger route on this wire"
    try:
        blob = read()
    except bridge.BridgeError as exc:
        return [], f"error: {exc}"
    if not isinstance(blob, dict):
        return [], "error: the ledger route did not answer with an object"
    if not blob.get("available"):
        return [], "unavailable: this build has no meter ledger"
    all_rows = [r for r in (blob.get("rows") or []) if isinstance(r, dict)]
    # THE LEDGER RESTARTS ITS NUMBERING AT EVERY COMBAT, because a row carried
    # between fights would let a grader attribute a spend to the wrong one. A
    # watermark the ledger has fallen behind therefore means "new fight", not
    # "nothing new" -- filtering on it blindly would drop a whole fight.
    highest = max((_int(r.get("index")) for r in all_rows), default=0)
    if highest < after_index:
        return all_rows, ""
    return [r for r in all_rows if _int(r.get("index")) > after_index], ""


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
           face: Callable[[dict[str, Any]], str] | None = None,
           number: bool = False) -> tuple[int, str]:
    """`(index, refusal)` for `name` among `entries`, by PRINTED name only.

    Exact fold first, unique substring second. Two entries whose printed FACE
    is identical are interchangeable and the first is taken -- refusing there
    would make a second copy of a card unplayable, which is not an ambiguity a
    player experiences. Two entries that print the same title with different
    faces (a base and an upgraded copy) ARE ambiguous, and the refusal says how
    to disambiguate rather than guessing.

    `number` (`EB-177`) matches against `_number_names`'s output instead of the
    bare printed names, which is what the RENDER prints on the same screen: a
    repeated title carries `(1)`, `(2)` in printed order and a unique one is
    untouched, so the bare title stays valid wherever it is unique and the
    numbered form is the handle wherever it is not. Callers turn it on exactly
    where the observation numbers the same list; a caller that does not number
    its page must not number its grammar.

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
    printed = [key(e) for e in entries]
    if number:
        printed = _number_names(printed)
    name, want_upgraded = _split_qualifier(name)
    want = _fold(name)
    if not want:
        return -1, "no name given"
    exact = [i for i, p in enumerate(printed) if _fold(p) == want]
    loose = [i for i, p in enumerate(printed) if want in _fold(p)]
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
                        + ", ".join(sorted({printed[i] for i in hits})))
        hits = narrowed
    if not hits:
        offered = ", ".join(sorted({p for p in printed if p}))
        return -1, (f"nothing here is called {name!r}. "
                    f"What is on the screen: {offered or '(nothing)'}")
    if len(hits) > 1:
        # Identical FACES first, and before the numbering: two copies of one
        # card are interchangeable, refusing there would make the second copy
        # unplayable, and that is not an ambiguity a player experiences. The
        # numbered names are still on the page for anyone who wants to be
        # explicit -- they are a handle, not an obligation.
        if face is not None and len({face(entries[i]) for i in hits}) == 1:
            return hits[0], ""
        # `EB-177`: otherwise the refusal ADVERTISES the names that would have
        # worked. With `number` on, two copies of one title print as `... (1)`
        # and `... (2)`, so a bare ambiguous title lands here and the way out
        # is already on the screen -- name it back rather than describe it.
        choices = sorted({printed[i] for i in hits})
        # The upgrade qualifier is advertised only where it would actually
        # narrow -- EB-173's rule that advice a tester cannot act on costs a
        # turn of the refusal budget to discover. Where BOTH handles work
        # (`EB-177`: two copies of one printed title, one of them upgraded)
        # both are offered, because the numbered name is the one the page in
        # front of them already prints.
        qualifier = ""
        if len({_is_upgraded(entries[i]) for i in hits}) > 1:
            qualifier = ('; or add "(upgraded)" / "(not upgraded)" to pick '
                         "one")
        if len(choices) > 1:
            return -1, (f"{name!r} matches more than one thing on this "
                        f"screen; name one exactly: {', '.join(choices)}"
                        + qualifier)
        if face is not None:
            # One printed name over different faces, and this caller does not
            # number: the upgrade qualifier is the only handle there is.
            return -1, (f"{name!r} matches more than one different thing on "
                        f"this screen; name it exactly, or add "
                        f"\"(upgraded)\" / \"(not upgraded)\" to pick one")
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


def _numbered_titles(entries: list[dict[str, Any]]) -> list[str]:
    """The printed titles of a card list, numbered as the render numbers them."""
    return _number_names([_card_title(e) for e in entries])


def _card_face_key(entry: dict[str, Any]) -> str:
    c = _card_face(entry)
    return f"{c['title']}|{c['cost']}|{c['upgraded']}|{c['text']}"


def _resolve_enemy(state: dict[str, Any], name: str) -> tuple[str, str]:
    """`(entity id, refusal)` for an enemy named the way the screen names it."""
    enemies = _enemies(state)
    # `EB-177`: numbered over EVERY enemy, then narrowed to the living ones.
    # The render prints a corpse (HP 0) as a line of its own, so numbering the
    # survivors alone would rename `Slug (2)` to `Slug` the moment the first
    # slug died -- the page and the grammar would disagree about which one the
    # tester is looking at, which is the whole defect this closes.
    names = _number_names([_text(e.get("name")) for e in enemies])
    living = [i for i, e in enumerate(enemies) if _int(e.get("hp")) > 0]
    if not name:
        if len(living) == 1:
            return _entity_id(enemies[living[0]]), ""
        return "", ("there is more than one enemy, so say which: "
                    f"{', '.join(names[i] for i in living)}")
    idx, why = _match([{"n": names[i]} for i in living], name,
                      key=lambda e: e["n"])
    if idx < 0:
        return "", why
    return _entity_id(enemies[living[idx]]), ""


def _pet_target(state: dict[str, Any], name: str) -> str | None:
    """`EB-216`. The jellyfish's entity id when the tester named IT, else None.

    NAMED, NEVER DEFAULTED, and that is the whole decision: "now or at dawn" is
    the choice the slice exists to test (its sec.1), so a card that could go
    either way and was aimed at nothing is played NOW. Only the tester's own
    word sends it to the jellyfish.
    """
    plans = _combat(state).get("plans") if state else None
    if not plans or not plans.get("pet_entity_id") or not name:
        return None
    idx, _ = _match([{"n": plans["pet_name"]}], name, key=lambda e: e["n"])
    return plans["pet_entity_id"] if idx == 0 else None


def _play(state: dict[str, Any], cmd: Command) -> Resolution:
    hand = _hand(state)
    titles = _numbered_titles(hand)
    idx, why = _match(hand, cmd.name, key=_card_title, face=_card_face_key,
                      number=True)
    if idx < 0:
        return _refuse(why)
    entry = hand[idx]
    if entry.get("can_play") is False:
        # `EB-264`: the same translation the page uses, so a refusal and the
        # card's own line cannot disagree about why.
        reason = qa_packet.unplayable_reason(
            entry.get("unplayable_reason_text") or entry.get("unplayable_reason"))
        return _refuse(f"{titles[idx]!r} cannot be played right now"
                       + (f": {reason}" if reason else ""))
    post: dict[str, Any] = {"action": "play_card", "card_index": idx}
    printed = {"card": titles[idx]}
    # `EB-216`. THE JELLYFISH FIRST, because it is the one target that is not
    # an enemy and the refusal a tester would otherwise get ("there is more
    # than one enemy, so say which") would be about the wrong board.
    pet = _pet_target(state, cmd.target)
    if pet is not None:
        post["target"] = pet
        printed["target"] = (_combat(state)["plans"]["pet_name"])
        return Resolution(True, "play", post, printed)
    needs_target = str(entry.get("target_type") or "").lower() in (
        "anyenemy", "enemy", "singleenemy", "targetenemy")
    if cmd.target or needs_target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            return _refuse(why)
        post["target"] = eid
        printed["target"] = next(
            (n for e, n in zip(_enemies(state), _number_names(
                [_text(x.get("name")) for x in _enemies(state)]))
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
                          face=_card_face_key, number=True)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_card_reward", "card_index": idx},
                          {"card": _numbered_titles(entries)[idx]})
    if st in SELECT_SCREENS:
        entries = _screen_cards(state)
        idx, why = _match(entries, cmd.name, key=_card_title,
                          face=_card_face_key, number=True)
        if idx < 0:
            return _refuse(why)
        verb = "select_card" if st == "card_select" else "combat_select_card"
        key = "index" if st == "card_select" else "card_index"
        return Resolution(True, "choose", {"action": verb, key: idx},
                          {"card": _numbered_titles(entries)[idx]})
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
    if not options[idx]["enabled"]:
        # `EB-262`: a shelf the wire marks `is_stocked: false` has already been
        # bought. The page prints it as not available; the grammar agrees.
        return _refuse(f"{options[idx]['name']!r} is on the shelf but not "
                       f"available to buy")
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
    if st == "event":
        # `EB-259`. AN EVENT ROOM HAS NO PROCEED BUTTON. `ExecuteProceed`
        # never looks at one (`McpMod.Actions.cs:600-663`), so the bare verb
        # used to post an action the event refused outright and the tester
        # lost the action. Where the screen prints a *Proceed* option, that is
        # what the word means here, and it is posted as the choice it is.
        entries = _event_options(state)
        idx = _proceed_option(state)
        if idx < 0:
            offered = ", ".join(o["name"]
                                for o in (_named_option(x) for x in entries)
                                if o["name"])
            return _refuse("this event has no Proceed to take; choose one of "
                           f"its options: {offered or '(nothing printed)'}")
        option = _named_option(entries[idx])
        posted = entries[idx].get("index") if isinstance(entries[idx],
                                                         dict) else None
        return Resolution(True, "proceed",
                          {"action": "choose_event_option",
                           "index": posted if isinstance(posted, int) else idx},
                          {"option": option["name"]})
    if st in ("rewards", "treasure", "shop", "fake_merchant", "rest_site"):
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
# the same model does not satisfy it" is the ruling's own wording. A driver
# that a person points at a model name needs that refusal in code.
#
# EB-190 MOVED THE RULE, IT DID NOT COPY IT. `understudy/authorship.py` now
# owns the family table and the check, because `seat.py` needs the SAME
# refusal asked the other way round -- not "who is running" but "what does the
# row record about who wrote it" -- and two doors answering one question is
# how a governance rule ends up enforced in one place and remembered in the
# other. `authorship` imports nothing but yaml and reads exactly two keys off
# the prototype surface (`id`, `authored_by`), so the no-sheet pin on this
# module is unchanged. The names below stay bound here: this is where every
# caller and every test already reaches for them.
AUTHOR_FAMILY = authorship.AUTHOR_FAMILY
MODEL_FAMILIES = authorship.MODEL_FAMILIES
model_family = authorship.model_family


def check_independent(model: str, author: str = AUTHOR_FAMILY, *,
                      rows: Any = ()) -> None:
    """Refuse the author's own model family as tester. R217 C, EB-190.

    Thin: the rule is `authorship.check_independent`. This wrapper exists only
    to keep the failure spelled `BlindPlayError`, which is what the driver's
    own error handling and this module's tests catch.
    """
    try:
        authorship.check_independent(model, author, rows=rows)
    except authorship.IndependenceError as exc:
        raise BlindPlayError(str(exc)) from None


def command_schema(forecast_asks: int = 0) -> dict[str, Any]:
    """The reply shape for a play turn. Shape only -- never content.

    `EB-229`, the RUN-lane twin of `EB-239`. `KURAGEMEM002` graded `P1`, `P2`
    and `P4` UNREACHED not because the display failed but because THE QUESTION
    WAS NEVER ASKED: this schema was `command` and `thinking` and nothing
    else, so the tester says why it plays what it plays and is never asked
    what it EXPECTS. §13.5's *stated IN ADVANCE* rule was on the record with
    nothing enforcing it, and `KURAGEMEM001` met it by accident.

    A registration that wants a forecast switches it on and the field
    APPEARS; every other run gets this function's default and the schema it
    has always had, byte for byte. When it is on the field is DECLARED and
    required, `additionalProperties` stays `False`, and `forecast` is the
    FIRST property and the FIRST required key -- a reply is written top to
    bottom, so the pre-commitment is asked BEFORE the command rather than
    beside it.
    """
    if forecast_asks <= 0:
        return {"type": "object",
                "properties": {"command": {"type": "string"},
                               "thinking": {"type": "string"}},
                "required": ["command", "thinking"],
                "additionalProperties": False}
    return {"type": "object",
            "properties": {"forecast": {"type": "array",
                                        "items": {"type": "string"}},
                           "command": {"type": "string"},
                           "thinking": {"type": "string"}},
            "required": ["forecast", "command", "thinking"],
            "additionalProperties": False}


def forecast_block(questions: list[str]) -> str:
    """The pre-commit questions, printed for a blind RUN's tester.

    The same position `qa_packet` gives the staged twin: BEFORE the board,
    because a forecast collected after the line is a rationalisation. An
    empty list prints nothing at all, which is what every unregistered run
    gets.
    """
    if not questions:
        return ""
    out = ["## Before you decide", "",
           "Answer these BEFORE you choose your command, and write the "
           "answers into your reply's `forecast` list in this order. They "
           "are predictions about what is about to happen, not questions "
           "about what you did:", ""]
    out += [f"{i}. {q}" for i, q in enumerate(questions, 1)]
    return "\n".join(out)


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
        # `EB-229`. The SCHEMA is half of what a turn asks for, so a test that
        # wants to know what the tester was asked has to be able to read it.
        self.schemas: list[dict[str, Any]] = []
        self.calls = 0

    def identity(self) -> dict[str, Any]:
        return {"model_requested": self.model, "model_observed": self.model,
                "codex_version": "(scripted)", "thread_id": "(scripted)"}

    def send(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self.sent.append(prompt)
        self.schemas.append(schema)
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

    def __init__(self, states: list[dict[str, Any]],
                 ledger: list[list[dict[str, Any]]] | None = None):
        self.states = list(states)
        self.posts: list[dict[str, Any]] = []
        self.i = 0
        # `EB-216`. The meter ledger the far side would be keeping: one list
        # per POST, cumulative, the way the mod's own is. `None` scripts a wire
        # with no ledger route at all, which is a release build.
        self.ledger = None if ledger is None else list(ledger)

    def get_state(self) -> dict[str, Any]:
        return self.states[min(self.i, len(self.states) - 1)]

    def post(self, action: str, **params: Any) -> dict[str, Any]:
        self.posts.append({"action": action, **params})
        self.i += 1
        return {"status": "ok", "message": ""}

    def health(self) -> dict[str, Any]:
        return {"mod_version": "0.0-scripted"}

    def meter_ledger(self) -> dict[str, Any]:
        if self.ledger is None:
            # What a release build answers: the route is there, the mod that
            # keeps a ledger is not.
            return {"status": "ok", "available": False, "rows": [], "count": 0}
        rows = self.ledger[min(max(self.i - 1, 0), len(self.ledger) - 1)]
        return {"status": "ok", "available": True, "rows": rows,
                "count": len(rows)}


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
                 forecast: list[str] | None = None,
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
        # `EB-229`. OPT-IN and EMPTY BY DEFAULT: a run that registers no
        # forecast prints no such block, is sent the schema it has always
        # been sent, and seals a record with no forecast key in it.
        self.forecast = [str(q).strip() for q in (forecast or [])
                         if str(q).strip()]
        # The questions are printed on the blind page, so they answer to the
        # same leak rule every other line of it does (`staged_turn` checks
        # its own the same way).
        bad = qa_packet.leaks(list(self.forecast))
        if bad:
            rule, hit, ctx = bad[0]
            raise BlindPlayError(
                f"forecast question leaks design vocabulary ({rule}: {hit!r} "
                f"in {ctx[:80]!r}): it is printed at the top of the blind "
                f"page -- ask it in the vocabulary the page prints")
        self.forecasts: list[dict[str, Any]] = []
        self.actions = 0
        self.refusals = 0
        # `EB-216`. One row per play and per end turn, machine-written off the
        # wire and never rendered to the seat.
        self.wire_rows: list[dict[str, Any]] = []
        # The highest meter-ledger row index already filed on a snapshot, so
        # each snapshot carries the rows THIS action minted and not the fight's
        # whole history over again.
        self._ledger_seen = 0
        self.fight_records: list[str] = []
        self.run_record = ""
        self.stopped = ""
        self.started = time.time()

    # -- the two things the seat is ever sent ------------------------------

    def _page(self, obs_md: str, feedback: str,
              forecast: list[str] | None = None) -> str:
        parts = []
        # `EB-229`. FIRST, and that position is the whole point -- the same
        # one `qa_packet` gives the staged twin. The tester reads top to
        # bottom, so a question printed under the board is a question asked
        # after the line has been chosen.
        block = forecast_block(list(forecast or []))
        if block:
            parts.append(block)
        parts.append(obs_md)
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

            # `EB-229`. A forecast is a PER-TURN pre-commitment, so it is
            # asked on the screens that have turns. A map walk, a shop or a
            # reward screen has no next turn to predict, and asking there
            # would collect a forecast about a board the tester is not on.
            asks = list(self.forecast) if obs["screen"] == "combat" else []
            body = self._page(page, feedback, asks)
            prompt = f"{self.prompt}\n\n---\n\n{body}\n" if first else body
            first = False
            try:
                reply = self.thread.send(prompt, command_schema(len(asks)))
            except SeatBudgetExhausted as exc:
                self.stopped = "budget:rate_limit"
                self.transcript.write(kind="seat_budget", detail=str(exc))
                break
            except BlindPlayError as exc:
                self.stopped = "seat_refused"
                self.transcript.write(kind="seat_error", detail=str(exc))
                break
            if asks:
                # RECORDED, NEVER GRADED HERE. The registration that switched
                # the channel on is what grades the answers against the wire;
                # this driver's whole job is that the answer EXISTS, is
                # attached to the page it was written on, and is countable.
                # A short answer is COUNTED SHORT rather than stopping the
                # run: the staged lane can refuse a form and re-read it, a
                # live run cannot un-spend the game time, and a slot whose
                # denominator is short is a fact its grader can see.
                answers = [str(a).strip()
                           for a in (reply.get("forecast") or [])]
                row = {"action": self.actions + 1,
                       "observation_sha256": page_sha,
                       "questions": list(asks),
                       "answers": answers,
                       "asked": len(asks),
                       "answered": len([a for a in answers if a])}
                row["short"] = row["answered"] < row["asked"]
                self.forecasts.append(row)
                self.transcript.write(kind="forecast", **row)

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
            # `EB-216`. The board the seat decided on, written down before the
            # POST moves it. Only `play` and `end turn`: a map walk or a shop
            # purchase has no turn, no bank and no intent to count against.
            snap = None
            if res["verb"] in SNAPSHOT_VERBS:
                snap = wire_snapshot(state, index=len(self.wire_rows) + 1,
                                     verb=res["verb"], command=command)
                self.wire_rows.append(snap)
                self.transcript.write(kind="wire", index=snap["index"],
                                      verb=snap["verb"], turn=snap["turn"])
            post = dict(res["post"] or {})
            action = post.pop("action")
            result = self.wire.post(action, **post)
            # `EB-216`, R225's clause. AFTER the POST, because the ledger row
            # this play minted does not exist until the play has resolved --
            # the board above is the decision, this is what the decision cost
            # and what it gave back. A gain that lands later (a turn-start kit
            # response after an `end turn`) is on the NEXT snapshot's rows,
            # which is where the engine actually put it.
            if snap is not None:
                rows, note = ledger_rows(self.wire, self._ledger_seen)
                snap["ledger"] = rows
                if note:
                    snap["ledger_note"] = note
                for row in rows:
                    self._ledger_seen = max(self._ledger_seen,
                                            _int(row.get("index")))
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
        # `EB-229`. The key is present only where the channel was switched
        # on, so an unregistered run's sealed record is what it has always
        # been -- the same discipline `wire` is written under.
        extra = {"forecast_questions": list(self.forecast),
                 "forecasts": list(self.forecasts)} if self.forecast else {}
        return {
            **extra,
            "session_id": self.session_id,
            "actions": self.actions,
            "termination": self.stopped or "unknown",
            "prompt_sha256": self.prompt_sha,
            "wire": list(self.wire_rows),
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


def granted_arms(seed: str, log_dir: Path | None = None) -> tuple[str, str]:
    """`(arms granted into this run's deck, where it was read)`. EB-188.

    A blind whole-fight run cannot DRAW a prototype row -- the surface is
    quarantined out of every pool -- so `understudy/embark.py --arm` grants it
    into the starting deck before the tester sees a screen. A record that did
    not name the grant would describe a deck the generators never produced as
    though they had, which is the claim `bridge.GRANT_GUARDRAIL` exists to
    refuse.

    MATCHED BY SEED, and that is the whole of the honesty here. The sidecar is
    written by whichever process opened the run, and this may be a different
    process on a different day; the seed is the run's identity (R95), so a
    sidecar whose seed is not this run's is a record of a DIFFERENT run and
    its arms are not reported. Read off disk like the two version reads above,
    and for the same reason -- this module may never import the operator side.

    Answers `("(none)", ...)` when nothing matches, which is a positive
    statement rather than a gap: the run met only what the pools offered.
    """
    d = log_dir or (Path(__file__).resolve().parent / "logs")
    none = ("(none)", "no `--arm` grant recorded against this run's seed")
    if not seed or not d.is_dir():
        return none
    for path in sorted(d.glob("embark-*.json"), reverse=True):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):                         # noqa: PERF203
            continue
        if not isinstance(blob, dict) or _text(blob.get("run_seed")) != seed:
            continue
        granted = blob.get("arms_granted") or []
        if not granted:
            return none
        named = ", ".join(_text(g.get("card_id")) for g in granted)
        return named, f"the embark sidecar `{path.name}`, matched by run seed"
    return none


def game_version(wire: Any = None) -> tuple[str, str]:
    """`(game build, where it was read)`. Never guessed.

    The other half of `EB-174`: a record has to name the GAME too, because a
    live number was never comparable across a game build (R95) and the pin
    moved under this tool once already (R218, v0.107.1 -> v0.111.0 mid-sitting).

    `release_info.json` in the install root is the game's own statement of its
    version, and it is the first of the four facts
    `operations/understudy-seats.md` names for
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


def turn_notes(log_dir: Path) -> list[tuple[str, str, str]]:
    """The tester's own per-turn sentence, off the gitignored turn pages.

    `(turn, command, thinking)` per answered turn. The blind prompt REQUIRES a
    `thinking` field on every answer and the schema enforces it, but until now
    nothing carried it into the committed record — so a record could not
    evidence a claim about what the tester said IN ADVANCE of a play, which is
    exactly what a legibility slate grades. Reads only; the material is the
    tester's own words, the same class the fight records already carry
    verbatim, and no observation text is copied out.
    """
    rows: list[tuple[str, str, str]] = []
    for reply in sorted(log_dir.glob("turn-*/reply.json")):
        try:
            data = json.loads(reply.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        rows.append((reply.parent.name, _text(data.get("command")),
                     _text(data.get("thinking"))))
    return rows


def notes_markdown(rows: list[tuple[str, str, str]]) -> str:
    """The per-turn channel as the committed record carries it."""
    out = ["## Turn by turn, in the tester's own words", "",
           "One line per answered turn: the command the tester gave and the "
           "sentence it gave for it, verbatim, off `turn-*/reply.json`. The "
           "same R217 G label rides on it as on the fight records — it is one "
           "model's account, not a measurement.", ""]
    if not rows:
        out += ["No answered turn carried a note."]
        return "\n".join(out) + "\n"
    out += ["| turn | command | the tester's sentence |", "|---|---|---|"]
    for turn, command, thinking in rows:
        note = thinking.replace("|", "\\|").replace("\n", " ").strip()
        cmd = command.replace("|", "\\|").strip()
        out.append(f"| `{turn}` | `{cmd}` | {note} |")
    return "\n".join(out) + "\n"


def read_snapshots(path: Path) -> list[dict[str, Any]]:
    """The wire snapshots of a finished session, from either half.

    `EB-216`. A grader is handed one of two directories and should not have to
    care which: the GITIGNORED log dir (`wire.jsonl`, which is what every
    committed `review/qa/blindplay/*/grade.py` is pointed at, beside the
    `turn-*/` pages they already read) or the COMMITTED record dir
    (`wire.json`, which is what survives the log being swept). A directory
    with neither answers with nothing rather than raising: a session sealed
    before this channel existed has no snapshots, and that is a fact about the
    session, not an error in the reader.
    """
    jsonl = path / "wire.jsonl"
    if jsonl.is_file():
        rows = []
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
    blob = path / "wire.json"
    if blob.is_file():
        data = json.loads(blob.read_text(encoding="utf-8"))
        return [r for r in (data.get("snapshots") or [])
                if isinstance(r, dict)]
    return []


def meter_plays(snapshots: list[dict[str, Any]],
                meter: str = "spark") -> list[dict[str, Any]]:
    """Every ledger row for one meter, flattened out of the snapshots.

    `EB-216` / R225's clause: the per-play `{card, before, price_paid, gains
    {source: n}, after}` a grader counts against. The snapshot a row rides on
    is carried through as `snapshot` and `turn`, because a play is only
    interesting beside the board it was made on.

    NOTHING PUBLISHED IS RE-GRADED THROUGH THIS (R101b, R224 A). It is the
    read the NEXT run's slate has; a record sealed before the channel existed
    has no rows and stays exactly as it was graded.

    `meter` is a parameter for the reason it is a field on the mod side:
    Charge and Encore are the same shape and will want the same counts.
    """
    out = []
    for snap in snapshots:
        for row in (snap.get("ledger") or []):
            if not isinstance(row, dict):
                continue
            if meter and _text(row.get("meter")) != meter:
                continue
            out.append({**row, "snapshot": _int(snap.get("index")),
                        "turn": _int(row.get("turn", snap.get("turn")))})
    return out


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
    for key in ("model_requested", "model_observed",
                # The LOCAL backend's four, and they are absent from a codex
                # run's identity entirely, so a codex record is byte-identical
                # to what this function has always written. `seat_family` is
                # the VENDOR family R217 C is read off, which the authorship
                # family (`local`) names a chair rather than answering;
                # `blindness` says out loud that this backend's claim is
                # structural where the codex seat's is transcript-proved.
                "backend", "seat_family", "endpoint",
                "server_version", "server_version_source",
                "schema_enforced", "blindness", "seat_status",
                "codex_version",
                "build_version", "build_version_source",
                "game_version", "game_version_source", "run_seed",
                "arms_granted", "arms_granted_source",
                "prompt_sha256", "actions", "termination",
                # `EB-229`. Present only where a registration switched the
                # forecast channel on, so nothing moves on a run that did not.
                "forecast_asked"):
        if key in identity:
            out.append(f"- **{key}**: {identity[key] or '(not read)'}")
    out += ["", f"- **guardrail**: {summary['guardrail']}", ""]
    # `EB-216`. The record NAMES the machine channel and does not inline it:
    # `wire.json` is a board, not prose, and a reader who wants a count wants
    # the file rather than a table of it. The count is here so a missing file
    # is visible from the record alone.
    if summary.get("wire") is not None:
        out += [f"- **wire snapshots**: {len(summary['wire'])} in "
                f"`wire.json` beside this file — one row per play and per "
                f"end turn, machine-written off the API and never shown to "
                f"the tester (`EB-216`, R101b)", ""]
    # `EB-229`. The forecasts are on the COMMITTED half, because they are the
    # thing a registration that asked for them has to count, and the
    # gitignored log is swept. Absent entirely on a run that asked for none.
    if summary.get("forecast_questions"):
        rows = summary.get("forecasts") or []
        short = len([r for r in rows if r.get("short")])
        out += ["## Forecasts, stated in advance", "",
                "One row per combat turn the tester was asked on, written "
                "BEFORE its command and never graded here (`EB-229`).", "",
                f"- **asked on**: {len(rows)} turns, "
                f"{short} of them answered short", ""]
        out += [f"{i}. {q}"
                for i, q in enumerate(summary["forecast_questions"], 1)]
        out += ["", "| action | " + " | ".join(
            f"answer {i}" for i in range(
                1, len(summary["forecast_questions"]) + 1)) + " |",
            "|---" * (len(summary["forecast_questions"]) + 1) + "|"]
        for r in rows:
            cells = list(r.get("answers") or [])
            cells += [""] * (len(summary["forecast_questions"]) - len(cells))
            out.append(f"| {r.get('action')} | " + " | ".join(
                str(c).replace("|", "\\|").replace("\n", " ")
                for c in cells) + " |")
        out.append("")
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
    # `EB-216`. BOTH SIDES GET IT, and for the reason the graders are written
    # the way they are: every `review/qa/blindplay/*/grade.py` takes the
    # GITIGNORED log dir as its argument and reads the run's own artefacts out
    # of it, while the committed half is what survives the log being swept. It
    # is the same rows either way.
    rows = summary.get("wire") or []
    (log_dir / "wire.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n"
                for r in rows), encoding="utf-8")
    (out / "wire.json").write_text(
        json.dumps({"session_id": summary["session_id"],
                    "snapshots": rows}, indent=1, default=str) + "\n",
        encoding="utf-8")
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


def build_thread(log_dir: Path, backend: str, model: str) -> Any:
    """The tester for one run: the Codex seat, or the local backend.

    ONE function so the two cannot drift on the things they share. Both are
    handed the same `log_dir`, both answer `identity()` / `send()` /
    `close()`, and `Session` -- which owns the prompt, the schema, the loop,
    the records and the budgets -- never learns which it got. The CODEX PATH
    IS UNCHANGED and is what an unflagged `session` still runs.

    `local_play` is imported HERE rather than at module scope so this module's
    import list stays what `test_blindplay_cannot_reach_a_sheet_or_a_policy`
    reads it as, and so an operator with no local endpoint configured never
    pays for the import.
    """
    if backend == "local":
        from understudy import local_play
        return local_play.thread(log_dir, model=model)
    # R217 C, asked before a process is started. The LOCAL path asks the same
    # question inside `LocalThread.__init__`, where the served model's own
    # name is finally known.
    resolved = model or seat.DEFAULT_MODEL
    check_independent(resolved)
    return CodexThread(log_dir, model=resolved)


def cmd_session(args) -> int:
    session_id = args.session_id or time.strftime("%Y%m%d-%H%M%S",
                                                  time.gmtime())
    log_dir = LOG_ROOT / session_id
    from understudy import local_play
    try:
        thread = build_thread(log_dir, args.backend, args.model)
    except BlindPlayError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except local_play.LocalPlayError as exc:
        print(f"local backend: {exc}", file=sys.stderr)
        return 2
    version, source = build_version()
    game, game_source = game_version()
    seed = bridge.current_seed() or ""
    budget = Budget(max_actions=args.max_actions,
                    max_wall_s=args.max_wall_s,
                    max_refusals=args.max_refusals,
                    max_stalls=args.max_stalls)
    try:
        session = Session(thread, wire=bridge, session_id=session_id,
                          budget=budget,
                          forecast=list(args.forecast or []))
        # The local backend keeps its per-screen reply row -- the scratchpad
        # it stripped, the token counts, the wall clock -- in the SESSION's
        # transcript rather than a second log, so a reader follows one file.
        # Attached rather than passed, because `Session` builds the transcript
        # and the thread is older than the session it is handed to.
        if hasattr(thread, "transcript"):
            thread.transcript = session.transcript
        summary = session.run()
    finally:
        thread.close()
    arms, arms_source = granted_arms(seed)
    identity = {**thread.identity(), "build_version": version,
                "build_version_source": source,
                "game_version": game, "game_version_source": game_source,
                "run_seed": seed,
                "arms_granted": arms, "arms_granted_source": arms_source,
                "prompt_sha256": summary["prompt_sha256"],
                "actions": summary["actions"],
                "termination": summary["termination"]}
    if summary.get("forecast_questions"):
        identity["forecast_asked"] = len(summary["forecast_questions"])
    path = seal(summary, identity, log_dir=session.dir)
    print(f"transcript: {summary['transcript']}")
    print(f"record:     {path}")
    print(f"actions:    {summary['actions']}   "
          f"stopped: {summary['termination']}")
    return 0


SECTIONS = ("## Turn by turn", "## Leak audit")


def _splice(record: Path, heading: str, block: str) -> None:
    """Replace one appended section of a sealed record, keeping the others.

    The record is the head the seal wrote plus appended sections in `SECTIONS`
    order. Each post-hoc writer replaces its own section and never truncates a
    sibling — the bug this exists to stop is a second writer silently dropping
    the first one's block.
    """
    text = record.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for name in SECTIONS:
        head, sep, tail = text.partition("\n" + name)
        if sep:
            blocks[name] = (sep.lstrip("\n") + tail).rstrip() + "\n"
            text = head
    blocks[heading] = block.rstrip() + "\n"
    # A block may itself have swallowed a later sibling on an older record.
    for name in SECTIONS:
        if name in blocks and name != heading:
            body, sep, _ = blocks[name].partition("\n## ")
            if sep:
                blocks[name] = body.rstrip() + "\n"
    out = text.rstrip()
    for name in SECTIONS:
        if name in blocks:
            out += "\n\n" + blocks[name].rstrip()
    record.write_text(out + "\n", encoding="utf-8")


def cmd_notes(args) -> int:
    """Carry the tester's per-turn sentences into the committed record.

    Separate from `session` for the reason `audit` is: it reads the gitignored
    turn pages of a run that has FINISHED and writes only the committed
    record, so a session sealed before this existed is still completable.
    """
    log_dir = LOG_ROOT / args.session_id
    if not log_dir.is_dir():
        raise BlindPlayError(f"no session log at {log_dir}")
    rows = turn_notes(log_dir)
    record = RECORD_ROOT / args.session_id / "record.md"
    if not record.is_file():
        raise BlindPlayError(f"no sealed record at {record}")
    _splice(record, "## Turn by turn", notes_markdown(rows))
    print(f"record: {record}")
    print(f"turns:  {len(rows)}")
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
        _splice(record, "## Leak audit", audit_markdown(audit))
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

    s = sub.add_parser("session", help="one blind thread plays the run")
    s.add_argument("--backend", choices=("codex", "local"), default="codex",
                   help="who plays. `codex` is the seat and the default and "
                        "is unchanged. `local` plays the same pages through "
                        "the OpenAI-compatible endpoint at "
                        "$GITS_LOCAL_MODEL_URL -- AN OPTION, not a seat: "
                        "the 2026-08-29 ADVANCE covered the staged "
                        "single-turn tester only and whole-run blind play by "
                        "a local model is a pick for [USER]")
    s.add_argument("--model", default="",
                   help=f"the codex model (default {seat.DEFAULT_MODEL}), or "
                        f"with --backend local the served model to ask for "
                        f"(default: whatever /v1/models reports)")
    s.add_argument("--session-id", default="")
    s.add_argument("--max-actions", type=int, default=60)
    s.add_argument("--max-wall-s", type=float, default=3600.0)
    s.add_argument("--max-refusals", type=int, default=3)
    s.add_argument("--max-stalls", type=int, default=6,
                   help="stop after this many identical screens running "
                        "(EB-173: a screen the tester cannot get off)")
    s.add_argument("--forecast", action="append", metavar="QUESTION",
                   help="EB-229: ask this question BEFORE the command on "
                        "every combat turn, and seal the answers with the "
                        "record. Repeatable, in the order the registration "
                        "numbers them. Omit it and the run is asked, sent "
                        "and sealed exactly as it always was.")
    s.set_defaults(func=cmd_session)

    u = sub.add_parser("audit", help="leak-audit a finished session's own "
                                     "observations and append the counts to "
                                     "its committed record")
    u.add_argument("session_id")
    u.set_defaults(func=cmd_audit)

    n = sub.add_parser("notes", help="carry a finished session's per-turn "
                                     "sentences into its committed record")
    n.add_argument("session_id")
    n.set_defaults(func=cmd_notes)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except BlindPlayError as exc:
        print(f"blind play error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
