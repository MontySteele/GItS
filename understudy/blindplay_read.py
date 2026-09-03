"""Small reads: printed text, folded names, and the blobs behind them.

Cut out of `blindplay.py` by `EB-180`. The scrubber's small reads --
`_text`, `_fold`, `_number_names`, `_despritify` -- and `transient` /
`settle`, which decide whether the wire is showing a SCREEN or a frame
on the way to one. Re-exported from `blindplay.py`, so
`blindplay.transient(state)` still resolves.
"""
from __future__ import annotations

import re
import time
from typing import Any

from understudy import bridge, qa_packet

from understudy.blindplay_shape import (COMBAT_SCREENS, SETTLE_DELAY_S,
                                        SETTLE_TRIES)


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
    """One printed string, with the game's markup folded out (`EB-246`).

    THE DEFECT, IN ONE SENTENCE: a *Choose one* option is named
    `Spend 6 [gold]Charge[/gold]: gain 12 Block` on the wire, the staged packet
    folds those tags out through `scenario.card_key` and this page did not, so
    the same choice had two printed names and a `KLEESPARK-W5` tester had to
    type `[gold]` to name the thing they were reading. The fold is
    `qa_packet.strip_markup` -- the SAME object `scenario` uses, not a copy --
    and it is applied HERE, at the one door every printed value on this page
    comes through, for the reason `_despritify` gives one screen over: a rule
    applied in one reader is a rule the next reader somebody adds will miss.
    """
    return qa_packet._text(qa_packet.strip_markup(value))


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

    `EB-246`: the markup goes FIRST, so a tester who echoes a name back with
    the tags still in it (which is what the W5 tester had to type) folds to the
    same key as the bare name this page now prints. Without it the tag WORDS
    survived the punctuation fold -- `[gold]Charge[/gold]` folded to
    `gold charge gold` -- and the two spellings were two different names.
    """
    s = qa_packet.strip_markup(text).casefold()
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

