"""EB-142: targeted scenarios against the REAL game. ATTENDED ONLY.

    python -m understudy.scenario run understudy/scenarios/<file>.yaml \
        --why "one line"

WHAT THIS IS FOR, AND WHY IT IS NOT A SOAK
------------------------------------------
The soak asks "does a thousand runs of policy_v1 produce a defect". This asks a
different question, one sentence long and answerable in one fight:

    put card X in hand (upgraded or not), set up the board, play it at enemy Y,
    and assert Z.

That question has had no instrument. `tier0` can assert the arithmetic, and
`lint_constant_parity` can assert that a C# constant equals a sheet number, but
neither of them can assert that the SHIPPED C# card, resolved by the real game
against a real enemy with a real Block value, produced the damage the sheet
prints. The two halves that were missing are now doors:
`gits/GitsGiveCard.cs` (EB-52) puts a chosen card in hand, and
`gits/GitsDebugState.cs` (EB-142) sets the board around it.

THE THREE RULES THIS FILE LIVES UNDER, AND NONE OF THEM MOVED
-------------------------------------------------------------
**Guardrail-7 is unchanged.** Nothing here is balance evidence. A scenario
asserts a NUMBER the sheet already claims -- 10 damage, 5 Block, 9 to every
enemy, Sparks 2 -- and a failed assert is a DEFECT, never a design finding. It
cannot produce a winrate and it must never be quoted as one; its board was set
by hand, so it is not comparable to any soak, any run, or any other scenario.

**No fun, ever.** A JSON-state agent cannot see the screen. This file may
assert HP, Block, power stacks, resource amounts, prompt strings, playability
and unplayable reasons, and printed card text. It may not emit a claim about
look, legibility, readability or feel, and neither may anything reading its
log. `frames.GUARDRAIL` says the same thing about pictures and is unchanged.

**Attended only, and structurally so.** Every scenario grants a card and writes
a board, which is exactly what the soak's claim -- that its runs are runs the
game generated -- forbids. This module therefore sits on `harness.py`'s side of
the line, beside `give-card` and `frame`, and `soak.py` does not import it.
`tier0/tests/test_understudy_scenario.py` pins that absence the same way
`test_understudy_give_card.py` pins the grant verb's.

`bridge.GRANT_GUARDRAIL` rides on EVERY row of the JSONL, not once at the top:
a caveat that lives outside the record is a caveat lost the moment two records
are concatenated, which is GitsGiveCard's own reasoning applied to this log.

HOW A SCENARIO REACHES A FIGHT
------------------------------
It does not reimplement the embark. `soak.run_scripted` -- the setup / swap /
teardown dance `probe_block.py` and `probe_corpse.py` each carried a copy of,
factored out for this file's sake -- builds a `Session`, runs ONE `RunDriver`,
and restores the seam in a `finally`. The driver does the main menu, the
character select, the character read-back (EB-117), the seed read-back (R95)
and the route to the first fight; this module's `ScenarioPolicy` delegates
every one of those screens to `policy_v1` untouched and wakes up only when a
combat screen appears.

THE SCENARIO POSTS ITS OWN ACTIONS, AND THAT IS DELIBERATE
----------------------------------------------------------
`probe_block` and `probe_corpse` return one `Decision` per call and let the
driver post it. This file cannot: `soak._mechanical_action` claims `hand_select`
BEFORE `policy_v1.decide` is ever asked, and answers it by selecting card 0 and
confirming. That is the right default for an unattended soak and fatal for a
scenario whose whole question is *which* card gets chosen -- `the_tide_remembers`
scales off the COST of the card you exhaust. So when the first combat screen
arrives, the runner executes the entire scenario inline, posting each action
itself and settling between them, and only then hands combat back to
`policy_v1` so the fight can end and the run can stop.

The cost is stated rather than hidden: the driver's watchdog and its per-action
telemetry do not see the scenario's own posts. This is the attended loop -- a
person or an agent is watching it -- and the scenario writes its own JSONL with
a row per step. Nothing about an unattended run changed.

NAMES ARE RESOLVED AT THE MOMENT OF THE POST, NEVER BEFORE
----------------------------------------------------------
R93 revision #7's rule, and this file is the place it is easiest to get wrong:
a scenario is written as a list of card NAMES, and `card_index: 2` is a
different card one frame later. Every `play` and `select` re-reads the state and
resolves the name against the hand it is about to act on. A name that is not
there is a failed step with the hand printed, never a silent index.

THE FILE FORMAT
---------------
YAML, under `understudy/scenarios/`. `steps` is a list of single-key mappings;
`expect` steps assert against the state bracketed by the last action.

    name: eb142-example
    character: KLEEMOD-FURINA
    turns: 8
    assumptions: ["..."]          # every number that depends on the board
    steps:
      - give:   {card: KLEEMOD-TAKE_IT_FROM_THE_TOP, pile: hand}
      - set_block: {who: JAW_WORM_0, amount: 0}
      - play:   {card: "Take It From the Top", target: JAW_WORM_0}
      - expect: {enemy_hp_block_delta: {who: JAW_WORM_0, amount: -10}}

`ASSUMPTIONS` IS PART OF THE FORMAT AND IS PRINTED WITH THE RESULT. An exact
expected number usually depends on something the scenario did not set -- the
enemy's Block, a Vulnerable stack, which enemy the encounter rolled. A file
that states its assumptions is a file whose failure can be read; one that does
not is a file whose failure means "something, somewhere".
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from understudy import adapter, bridge, naming

SCENARIO_DIR = Path(__file__).resolve().parent / "scenarios"
LOG_DIR = Path(__file__).resolve().parent / "logs"

# The screens a scenario acts on itself. Combat is where it starts; the two
# selection screens are where a card's own effect can take it mid-step.
COMBAT_SCREENS = ("monster", "elite", "boss")
SELECT_SCREENS = ("hand_select", "card_select")

# Every verb a step may name. Kept as data so the parser can refuse an unknown
# key with the list, rather than skipping it -- a mistyped step that is silently
# ignored is a scenario that passes without running.
# Cards a scenario may name that are on NO sheet, each with the reason it is
# reachable in a fight. `tier0/tests/test_understudy_scenario.py` checks every
# other name against `docs/*-cards.yaml`, and without this list that lint would
# have to be switched off -- at which point a typo in a card name stops being
# caught at all. Adding a row here is a claim that the card exists in the mod
# and is reachable without a draft; the test asserts the C# class exists.
TOKEN_CARDS = {
    "KLEEMOD-ETHEREAL_SPOTLIGHT":
        "Furina's starter relic adds one to hand at the start of every turn "
        "(Relics/EtherealSpotlightRelic.cs)",
    "Ethereal Spotlight": "the printed title of the above",
    "Center Stage":
        "an option on the Ethereal Spotlight's choose-a-card screen "
        "(Cards/Furina/SpotlightCards.cs, CenterStageOption)",
    "Guest Cast":
        "the other option on that screen, offered only when the player owns a "
        "Companion card (GuestCastOption)",
}

ACTION_STEPS = ("play", "select", "confirm", "end_turn")
SETUP_STEPS = ("give", "set_resource", "set_energy", "set_hp", "set_block")
OTHER_STEPS = ("expect", "read", "mark")
STEP_VERBS = ACTION_STEPS + SETUP_STEPS + OTHER_STEPS


class ScenarioError(RuntimeError):
    """A scenario file that cannot be run: a bad key, a missing field."""


class ExpectFailed(RuntimeError):
    """An assertion that did not hold. Carries the check and both readings."""

    def __init__(self, check: str, detail: str, before: dict, after: dict):
        super().__init__(f"{check}: {detail}")
        self.check = check
        self.detail = detail
        self.before = before
        self.after = after


# --------------------------------------------------------------- parsing ---

@dataclass
class Scenario:
    name: str
    character: str
    steps: list[tuple[str, Any]]
    path: Path | None = None
    seed: str | None = None
    turns: int = 12
    notes: str = ""
    assumptions: list[str] = field(default_factory=list)

    def cards_named(self) -> list[str]:
        """Every card this file names, for the lint that checks they exist.

        Read off the parsed steps rather than the raw text, so a card named in
        a comment is not asserted to exist and a card named in a step cannot be
        missed.
        """
        out: list[str] = []
        for verb, body in self.steps:
            if verb in ("give", "play"):
                out.append(str(body.get("card") or ""))
            elif verb == "select":
                out.extend(str(c) for c in (body.get("cards") or []))
            elif verb == "expect":
                for spec in body.values():
                    if isinstance(spec, dict) and spec.get("card"):
                        out.append(str(spec["card"]))
        return [c for c in out if c]


def _as_body(verb: str, raw: Any) -> dict[str, Any]:
    """One step's body, normalised to a dict.

    Three shorthands are accepted because they read better in a file and are
    unambiguous: `end_turn:` with nothing after it, `set_energy: 3`, and
    `select: [A, B]`. Everything else must be a mapping -- guessing at a shape
    is how a step means something the author did not write.
    """
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    if verb in ("set_energy",) and isinstance(raw, int):
        return {"amount": raw}
    if verb == "select" and isinstance(raw, list):
        return {"cards": list(raw)}
    if verb == "select" and isinstance(raw, str):
        return {"cards": [raw]}
    if verb == "read" and isinstance(raw, str):
        return {"label": raw}
    raise ScenarioError(f"step '{verb}': expected a mapping, got {type(raw).__name__}")


def parse(blob: dict[str, Any], path: Path | None = None) -> Scenario:
    if not isinstance(blob, dict):
        raise ScenarioError("a scenario file is a mapping at the top level")
    for required in ("name", "character", "steps"):
        if not blob.get(required):
            raise ScenarioError(f"missing '{required}'")
    raw_steps = blob["steps"]
    if not isinstance(raw_steps, list):
        raise ScenarioError("'steps' must be a list")

    steps: list[tuple[str, Any]] = []
    for i, entry in enumerate(raw_steps):
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ScenarioError(
                f"step {i}: each step is a single-key mapping, e.g. "
                f"`- play: {{card: X}}`; got {entry!r}")
        verb, raw = next(iter(entry.items()))
        if verb not in STEP_VERBS:
            raise ScenarioError(
                f"step {i}: unknown verb '{verb}'. One of: "
                + ", ".join(STEP_VERBS))
        body = _as_body(verb, raw)
        _validate(i, verb, body)
        steps.append((verb, body))

    if not any(v == "expect" for v, _ in steps):
        # A scenario with no assertion is a scenario that cannot fail, which
        # is worse than no scenario: it reads like coverage and is not.
        raise ScenarioError("a scenario with no `expect` step asserts nothing")

    return Scenario(
        name=str(blob["name"]),
        character=str(blob["character"]),
        steps=steps,
        path=path,
        seed=blob.get("seed") or None,
        turns=int(blob.get("turns", 12)),
        notes=str(blob.get("notes") or ""),
        assumptions=[str(a) for a in (blob.get("assumptions") or [])],
    )


def _validate(i: int, verb: str, body: dict[str, Any]) -> None:
    def need(*keys: str) -> None:
        for k in keys:
            if body.get(k) in (None, ""):
                raise ScenarioError(f"step {i} ('{verb}'): needs '{k}'")

    if verb in ("give", "play"):
        need("card")
    elif verb == "set_resource":
        need("name")
        if "amount" not in body:
            raise ScenarioError(f"step {i} ('set_resource'): needs 'amount'")
    elif verb in ("set_energy", "set_hp", "set_block"):
        if "amount" not in body:
            raise ScenarioError(f"step {i} ('{verb}'): needs 'amount'")
    elif verb == "select":
        if not body.get("cards"):
            raise ScenarioError(f"step {i} ('select'): needs 'cards'")
    elif verb == "expect":
        if not body:
            raise ScenarioError(f"step {i} ('expect'): asserts nothing")
        for check in body:
            if check not in CHECKS:
                raise ScenarioError(
                    f"step {i} ('expect'): unknown check '{check}'. One of: "
                    + ", ".join(sorted(CHECKS)))
    if verb == "give":
        pile = str(body.get("pile") or "hand")
        if pile not in bridge.GRANT_PILES:
            raise ScenarioError(
                f"step {i} ('give'): pile must be one of "
                f"{bridge.GRANT_PILES}, not {pile!r}")


def load(path: str | Path) -> Scenario:
    p = Path(path)
    blob = yaml.safe_load(p.read_text(encoding="utf-8"))
    return parse(blob, path=p)


def all_scenarios(directory: Path | None = None) -> list[Path]:
    d = directory or SCENARIO_DIR
    return sorted(d.glob("*.yaml")) if d.is_dir() else []


# ------------------------------------------------------- wire helpers ------

def _hand(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in ((state.get("player") or {}).get("hand") or [])
            if isinstance(c, dict)]


def _select_blob(state: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """The active selection screen and its blob, or `("", {})`.

    `card_select` and `hand_select` are two different screens with two
    different verbs (`select_card` / `combat_select_card`,
    `confirm_selection` / `combat_confirm_selection`), and the atlas's warning
    that "card_select is three screens wearing one name" is why the screen is
    read off `state_type` rather than guessed from what is on it.
    """
    st = str(state.get("state_type") or "")
    if st in SELECT_SCREENS and isinstance(state.get(st), dict):
        return st, state[st]
    return "", {}


def card_key(text: str) -> str:
    """One comparable key for a card named by id, loc key, or printed title.

    `KLEEMOD-TAKE_IT_FROM_THE_TOP`, `take_it_from_the_top` and
    `Take It From the Top` are the three spellings that appear across the
    sheets, the wire and a scenario file, and a scenario author should not have
    to know which one this frame is using. Case, the BaseLib prefix and the
    difference between `-`, `_` and a space all fold away; nothing else does.
    """
    key = str(text or "").strip().casefold()
    if key.startswith("kleemod-"):
        key = key[len("kleemod-"):]
    for ch in ("-", "_", "'", "!", ",", "."):
        key = key.replace(ch, " ")
    return " ".join(key.split())


def find_card(entries: list[dict[str, Any]], name: str) -> int | None:
    """`name`'s LIST POSITION among `entries`, or None. Id first, title second.

    List position, not the entry's own `index` field, and that is the repo's
    settled convention rather than a shortcut: `naming._at` indexes the hand
    list by `card_index`, and `policy_v1._choice_overlay` indexes a selector by
    list position too (`probe_block` states it in as many words). The two agree
    on every screen seen so far; where they ever disagree, the wire array the
    GET just returned is the thing the POST is indexing into.
    """
    want = card_key(name)
    for i, c in enumerate(entries):
        if card_key(str(c.get("id") or "")) == want:
            return i
    for i, c in enumerate(entries):
        if card_key(str(c.get("name") or "")) == want:
            return i
    return None


# Symbolic targets, and why a scenario file needs them at all: the encounter is
# GENERATED. `GitsSeed` can pin which run the generators make, but no scenario
# in this pack asserts anything about WHICH monster it hit, so writing
# `JAW_WORM_0` into a file would make it fail on every seed but one for a reason
# that is not the scenario's subject. `first` is the wire's own enemy order.
ENEMY_SYMBOLS = ("first", "lowest_hp", "highest_hp")


def find_enemy(state: dict[str, Any], who: str) -> dict[str, Any] | None:
    """The enemy `who` names: an entity id, a display name, or a symbol.

    Living enemies only. A symbol resolved against a state where the intended
    creature has died is a symbol pointing at a different creature, which is
    why every check resolves its symbol against the BEFORE state and then
    follows the concrete entity id (see `_enemy_pair`).
    """
    want = str(who or "").strip().casefold()
    living = [e for e in adapter.enemy_blobs(state)
              if int(e.get("hp", 0) or 0) > 0]
    if want == "first":
        return living[0] if living else None
    if want == "lowest_hp":
        return min(living, key=lambda e: (int(e.get("hp", 0) or 0),
                                          adapter.enemy_id(e))) if living else None
    if want == "highest_hp":
        return max(living, key=lambda e: (int(e.get("hp", 0) or 0),
                                          adapter.enemy_id(e))) if living else None
    for e in adapter.enemy_blobs(state):
        if adapter.enemy_id(e).casefold() == want:
            return e
        if str(e.get("name") or "").strip().casefold() == want:
            return e
    return None


def _enemy_pair(who: str, before: dict[str, Any], after: dict[str, Any]
                ) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str]:
    """`(before-blob, after-blob, concrete id)` for one enemy across a bracket.

    The identity is fixed on the BEFORE state and followed by entity id, so a
    symbolic target cannot silently become a different creature between the two
    readings -- which is exactly what would happen to `lowest_hp` after a hit.
    """
    b = find_enemy(before, who)
    if b is None:
        return None, None, str(who)
    eid = adapter.enemy_id(b)
    return b, find_enemy(after, eid), eid


def _powers(blob: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for s in blob.get("status") or []:
        if isinstance(s, dict) and s.get("name"):
            amt = s.get("amount", s.get("stacks"))
            out[str(s["name"]).strip().casefold()] = int(amt or 0)
    return out


def _who_blob(state: dict[str, Any], who: str) -> dict[str, Any] | None:
    if str(who or "player").strip().casefold() == "player":
        return state.get("player") or {}
    return find_enemy(state, who)


def digest(state: dict[str, Any]) -> dict[str, Any]:
    """The slice of a state a scenario can assert on, small enough to print.

    Not `soak._trim_state`: that one is sized for a defect record and keeps the
    map and the run. This one keeps exactly what a check reads, so a failure
    diff is the same vocabulary as the assertion that failed.
    """
    p = state.get("player") or {}
    return {
        "state_type": state.get("state_type"),
        "round": (state.get("battle") or {}).get("round"),
        "turn": (state.get("battle") or {}).get("turn"),
        "player": {"hp": p.get("hp"), "block": p.get("block", 0),
                   "energy": p.get("energy"),
                   "status": _powers(p),
                   "resources": p.get("resources")},
        "hand": [{"name": c.get("name"), "id": c.get("id"),
                  "cost": c.get("cost"), "can_play": c.get("can_play"),
                  "unplayable_reason": c.get("unplayable_reason"),
                  "is_upgraded": c.get("is_upgraded")}
                 for c in _hand(state)],
        "enemies": [{"id": adapter.enemy_id(e), "name": e.get("name"),
                     "hp": e.get("hp"), "block": e.get("block", 0),
                     "status": _powers(e)}
                    for e in adapter.enemy_blobs(state)],
        "prompt": _select_blob(state)[1].get("prompt"),
    }


# ------------------------------------------------------------- checks ------
#
# Each check is `(spec, before, after) -> str | None`; the string is the reason
# it failed. They read the WIRE and nothing else -- never a sheet, never tier0.
# A check that consulted `docs/klee-cards.yaml` for the number it is asserting
# would have the sheet on both sides of its own comparison, which is the
# `probe_block` rule ("Block cards are recognised from the WIRE's own printed
# description") applied to assertions.


def _hp(blob: dict[str, Any] | None) -> int:
    return int((blob or {}).get("hp", 0) or 0)


def _blk(blob: dict[str, Any] | None) -> int:
    return int((blob or {}).get("block", 0) or 0)


def _check_enemy_hp_delta(spec, before, after):
    b, a, eid = _enemy_pair(str(spec["who"]), before, after)
    if b is None:
        return f"no enemy {spec['who']!r} in the before-state"
    got = _hp(a) - _hp(b)
    want = int(spec["amount"])
    if got != want:
        return f"{eid} HP moved {got:+d}, expected {want:+d} ({_hp(b)} -> {_hp(a)})"
    return None


def _check_enemy_hp_block_delta(spec, before, after):
    """The bracket to use when the enemy's Block is not something the scenario
    set. Damage eats Block first, so HP alone under-reports by whatever Block
    was standing; (hp + block) is the quantity the hit actually moved."""
    b, a, eid = _enemy_pair(str(spec["who"]), before, after)
    if b is None:
        return f"no enemy {spec['who']!r} in the before-state"
    got = (_hp(a) + _blk(a)) - (_hp(b) + _blk(b))
    want = int(spec["amount"])
    if got != want:
        return (f"{eid} HP+Block moved {got:+d}, expected {want:+d} "
                f"({_hp(b)}+{_blk(b)} -> {_hp(a)}+{_blk(a)})")
    return None


def _check_each_enemy_hp_block_delta(spec, before, after):
    """Every enemy ALIVE IN THE BEFORE-STATE moved by the same amount.

    The denominator is the before-state on purpose: an enemy the hit killed is
    gone from `battle.enemies` in the after-state, and a check that iterated
    the after-state would quietly stop asserting about the one that died --
    which, on a splash card, is the interesting one.
    """
    want = int(spec["amount"])
    living = [e for e in adapter.enemy_blobs(before) if _hp(e) > 0]
    if len(living) < int(spec.get("at_least", 1)):
        return (f"needed at least {spec.get('at_least', 1)} living enemies, "
                f"the fight has {len(living)}")
    bad = []
    for b in living:
        eid = adapter.enemy_id(b)
        a = find_enemy(after, eid)
        got = ((_hp(a) + _blk(a)) if a is not None else 0) - (_hp(b) + _blk(b))
        if a is None and _hp(b) + _blk(b) <= -want:
            continue        # died to it: it took at least what was asserted
        if got != want:
            bad.append(f"{eid} moved {got:+d}")
    if bad:
        return f"expected every enemy {want:+d}; " + ", ".join(bad)
    return None


def _check_player_block(spec, before, after):
    got = _blk(after.get("player"))
    want = int(spec if isinstance(spec, int) else spec["amount"])
    return None if got == want else f"player Block is {got}, expected {want}"


def _check_player_hp_delta(spec, before, after):
    got = _hp(after.get("player")) - _hp(before.get("player"))
    want = int(spec if isinstance(spec, int) else spec["amount"])
    return None if got == want else f"player HP moved {got:+d}, expected {want:+d}"


def _check_power(spec, before, after):
    blob = _who_blob(after, str(spec.get("who") or "player"))
    if blob is None:
        return f"no creature {spec.get('who')!r}"
    name = str(spec["name"]).strip().casefold()
    powers = _powers(blob)
    if name not in powers:
        return (f"{spec.get('who', 'player')} has no {spec['name']!r}; "
                f"powers: {sorted(powers)}")
    if "stacks" in spec and powers[name] != int(spec["stacks"]):
        return (f"{spec['name']} is {powers[name]}, expected "
                f"{int(spec['stacks'])}")
    return None


def _check_no_power(spec, before, after):
    blob = _who_blob(after, str(spec.get("who") or "player"))
    if blob is None:
        return f"no creature {spec.get('who')!r}"
    name = str(spec["name"]).strip().casefold()
    powers = _powers(blob)
    return None if name not in powers else \
        f"{spec['name']} is still present at {powers[name]}"


def _check_resource(spec, before, after):
    res = (after.get("player") or {}).get("resources")
    if not isinstance(res, dict):
        # The ABSENCE of the key means "this bridge predates P1.5"; an empty
        # map means "nothing registered". GitsResources.cs draws that
        # distinction deliberately and a check that blurred it would report a
        # missing instrument as a wrong number.
        return ("player.resources is not on the wire -- the bridge predates "
                "P1.5 (gits/GitsResources.cs)")
    name = str(spec["name"])
    if name not in res:
        return f"no registered resource {name!r}; have: {sorted(res)}"
    got, want = int(res[name] or 0), int(spec["amount"])
    return None if got == want else f"{name} is {got}, expected {want}"


def _check_prompt(spec, before, after):
    got = _select_blob(after)[1].get("prompt")
    want = str(spec if isinstance(spec, str) else spec["text"])
    return None if str(got or "") == want else \
        f"prompt is {got!r}, expected {want!r}"


def _check_prompt_contains(spec, before, after):
    got = str(_select_blob(after)[1].get("prompt") or "")
    want = str(spec if isinstance(spec, str) else spec["text"])
    return None if want.casefold() in got.casefold() else \
        f"prompt {got!r} does not contain {want!r}"


def _check_state_type(spec, before, after):
    got = str(after.get("state_type") or "")
    want = str(spec if isinstance(spec, str) else spec["value"])
    return None if got == want else f"state_type is {got!r}, expected {want!r}"


def _hand_entry(state, card):
    idx = find_card(_hand(state), str(card))
    if idx is None:
        return None
    entries = _hand(state)
    return entries[idx] if 0 <= idx < len(entries) else None


def _check_can_play(spec, before, after):
    entry = _hand_entry(after, spec["card"])
    if entry is None:
        return (f"{spec['card']!r} is not in hand; hand: "
                f"{[c.get('name') for c in _hand(after)]}")
    got = entry.get("can_play") is not False
    want = bool(spec["value"])
    if got != want:
        return (f"{spec['card']} can_play is {got}, expected {want} "
                f"(unplayable_reason: {entry.get('unplayable_reason')!r})")
    return None


def _check_unplayable_reason(spec, before, after):
    entry = _hand_entry(after, spec["card"])
    if entry is None:
        return f"{spec['card']!r} is not in hand"
    got = entry.get("unplayable_reason")
    want = spec["value"]
    if want is None:
        return None if got is None else f"unplayable_reason is {got!r}, expected null"
    return None if str(got) == str(want) else \
        f"unplayable_reason is {got!r}, expected {want!r}"


def _check_description_contains(spec, before, after):
    entry = _hand_entry(after, spec["card"])
    if entry is None:
        return f"{spec['card']!r} is not in hand"
    got = " ".join(str(entry.get("description") or "").split())
    want = str(spec["text"])
    return None if want.casefold() in got.casefold() else \
        f"description {got!r} does not contain {want!r}"


CHECKS: dict[str, Callable[..., str | None]] = {
    "enemy_hp_delta": _check_enemy_hp_delta,
    "enemy_hp_block_delta": _check_enemy_hp_block_delta,
    "each_enemy_hp_block_delta": _check_each_enemy_hp_block_delta,
    "player_block": _check_player_block,
    "player_hp_delta": _check_player_hp_delta,
    "power": _check_power,
    "no_power": _check_no_power,
    "resource": _check_resource,
    "prompt": _check_prompt,
    "prompt_contains": _check_prompt_contains,
    "state_type": _check_state_type,
    "can_play": _check_can_play,
    "unplayable_reason": _check_unplayable_reason,
    "description_contains": _check_description_contains,
}


# -------------------------------------------------------------- runner -----

class Runner:
    """Executes one scenario's steps against a wire, writing a row per step.

    `wire` is `understudy.bridge` in production and a fake in the tests. It is
    an argument rather than an import so the parser, the step machinery and
    every check can be exercised with no game running -- which is the only way
    any of it gets tested at all, since the game is a live process on somebody's
    Windows box.
    """

    def __init__(self, scenario: Scenario, why: str, wire: Any = bridge,
                 out: Any = None, sleep: Callable[[float], None] = time.sleep,
                 settle: float = 0.7):
        if not str(why).strip():
            raise ScenarioError(
                "a scenario needs a --why: it grants cards and writes a board, "
                "and a run nobody can account for later is worse than no run")
        self.scenario = scenario
        self.why = str(why).strip()
        self.wire = wire
        self.out = out
        self.sleep = sleep
        self.settle_s = settle
        self.rows: list[dict[str, Any]] = []
        self.failures: list[dict[str, Any]] = []
        self.state: dict[str, Any] = {}
        # The delta baseline. Reset by every ACTION step, so an `expect` reads
        # the bracket around the single action before it -- the same bracket
        # `probe_block` takes its readings on ("consecutive readings bracket
        # exactly one card").
        self.before: dict[str, Any] = {}
        self.i = 0

    # -- log ---------------------------------------------------------------
    def emit(self, row: dict[str, Any]) -> None:
        row.setdefault("ts", time.time())
        row["i"] = self.i
        row["scenario"] = self.scenario.name
        row["why"] = self.why
        # ON EVERY ROW. See the module docstring: one row of a concatenated log
        # has to carry its own disqualification.
        row["guardrail"] = bridge.GRANT_GUARDRAIL
        self.i += 1
        self.rows.append(row)
        if self.out is not None:
            self.out.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            self.out.flush()

    # -- wire --------------------------------------------------------------
    def read(self) -> dict[str, Any]:
        self.state = self.wire.get_state()
        return self.state

    def _settle(self) -> dict[str, Any]:
        self.sleep(self.settle_s)
        return self.read()

    def _post(self, action: dict[str, Any], label: str) -> dict[str, Any]:
        """POST one action, with its NAMES resolved at this state (R93 #7)."""
        names = naming.describe(self.state, action)
        result = self.wire.post(**action)
        row = {"step": label, "action": action, "names": names,
               "status": result.get("status"),
               "message": result.get("message") or result.get("error")}
        self.before = self.state
        self._settle()
        row["after"] = digest(self.state)
        self.emit(row)
        if str(result.get("status")) == "error" or result.get("error"):
            raise ExpectFailed(
                label, f"the bridge refused it: "
                       f"{result.get('message') or result.get('error')}",
                self.before, self.state)
        return result

    # -- steps -------------------------------------------------------------
    def run(self) -> bool:
        """Every step in order. Returns True if nothing failed.

        FAIL-FAST, and the reason is not tidiness: a scenario's setup steps are
        preconditions for its assertions, so an expect that fails after a
        failed grant is not a second finding, it is the same one wearing a
        different number.
        """
        self.read()
        self.before = self.state
        for verb, body in self.scenario.steps:
            try:
                self._step(verb, body)
            except ExpectFailed as e:
                self.failures.append({"step": verb, "check": e.check,
                                      "detail": e.detail,
                                      "before": digest(e.before),
                                      "after": digest(e.after)})
                self.emit({"step": verb, "expect_failed": e.check,
                           "detail": e.detail,
                           "before": digest(e.before),
                           "after": digest(e.after)})
                return False
        return True

    def _step(self, verb: str, body: dict[str, Any]) -> None:
        handler = getattr(self, f"_do_{verb}")
        handler(body)

    # setup verbs ----------------------------------------------------------
    def _do_give(self, body: dict[str, Any]) -> None:
        card = str(body["card"])
        pile = str(body.get("pile") or "hand")
        report = self.wire.give_card(card, count=int(body.get("count", 1)),
                                     upgraded=bool(body.get("upgraded", False)),
                                     pile=pile)
        self.emit({"step": "give", "request": {"card": card, "pile": pile,
                                               "count": int(body.get("count", 1)),
                                               "upgraded": bool(body.get("upgraded", False))},
                   "result": report})
        if str(report.get("status")) != "ok":
            raise ExpectFailed("give", f"{card}: {report.get('message')}",
                               self.state, self.state)
        self._settle()

    def _debug(self, op: str, label: str, **kw: Any) -> None:
        report = self.wire.debug_state(op, self.why, **kw)
        self.emit({"step": label, "request": dict(kw, op=op), "result": report})
        if str(report.get("status")) != "ok":
            raise ExpectFailed(label, str(report.get("message")
                                          or report.get("error")),
                               self.state, self.state)
        # `set_hp` and `set_energy` answer `queued: true`: they go through async
        # commands that run visuals. Settling here rather than trusting the
        # answer is what stops the next assertion from racing the write.
        if report.get("queued"):
            self._settle()
        else:
            self.read()

    def _do_set_resource(self, body):
        self._debug("set_resource", "set_resource",
                    amount=int(body["amount"]), resource=str(body["name"]))

    def _do_set_energy(self, body):
        self._debug("set_energy", "set_energy", amount=int(body["amount"]))

    def _do_set_hp(self, body):
        self._debug("set_hp", "set_hp", amount=int(body["amount"]),
                    who=str(body.get("who") or "player"))

    def _do_set_block(self, body):
        self._debug("set_block", "set_block", amount=int(body["amount"]),
                    who=str(body.get("who") or "player"))

    # action verbs ---------------------------------------------------------
    def _do_play(self, body: dict[str, Any]) -> None:
        self.read()
        name = str(body["card"])
        index = find_card(_hand(self.state), name)
        if index is None:
            raise ExpectFailed(
                "play", f"{name!r} is not in hand; hand: "
                        f"{[c.get('name') for c in _hand(self.state)]}",
                self.state, self.state)
        entry = _hand(self.state)[index]
        action: dict[str, Any] = {"action": "play_card", "card_index": index}
        target = body.get("target")
        if target:
            enemy = find_enemy(self.state, str(target))
            if enemy is None:
                raise ExpectFailed(
                    "play", f"no enemy {target!r}; the fight has "
                            f"{[adapter.enemy_id(e) for e in adapter.enemy_blobs(self.state)]}",
                    self.state, self.state)
            action["target"] = adapter.enemy_id(enemy)
        self._post(action, f"play {entry.get('name') or name}")

    def _do_select(self, body: dict[str, Any]) -> None:
        for card in body["cards"]:
            self.read()
            screen, blob = _select_blob(self.state)
            if not screen:
                raise ExpectFailed(
                    "select", f"no selection screen is up (state_type is "
                              f"{self.state.get('state_type')!r})",
                    self.state, self.state)
            entries = [c for c in (blob.get("cards") or []) if isinstance(c, dict)] \
                or _hand(self.state)
            index = find_card(entries, str(card))
            if index is None:
                raise ExpectFailed(
                    "select", f"{card!r} is not offered; offered: "
                              f"{[c.get('name') for c in entries]}",
                    self.state, self.state)
            if screen == "hand_select":
                action = {"action": "combat_select_card", "card_index": index}
            else:
                action = {"action": "select_card", "index": index}
            self._post(action, f"select {card}")

    def _do_confirm(self, body: dict[str, Any]) -> None:
        self.read()
        screen, _ = _select_blob(self.state)
        if screen == "hand_select":
            action = {"action": "combat_confirm_selection"}
        elif screen == "card_select":
            action = {"action": "confirm_selection"}
        else:
            # NOT A FAILURE, AND THE ROW SAYS WHY. A `card_select` of the
            # "choose" type takes the pick immediately -- raw-full.md:728, "for
            # 'choose' type: picking is immediate (no confirm needed)" -- and a
            # one-of-one hand selection can close on the select too. A scenario
            # that wrote `confirm` after either would fail on a screen that did
            # exactly what it was asked. The step is recorded as skipped rather
            # than passed, so a scenario that never opened a screen at all is
            # still visible in the log; the assertions after it are what
            # actually catch that.
            self.emit({"step": "confirm", "skipped":
                       f"no selection screen is up (state_type is "
                       f"{self.state.get('state_type')!r}); the screen took "
                       f"the pick without a confirm"})
            return
        self._post(action, "confirm")

    def _do_end_turn(self, body: dict[str, Any]) -> None:
        self.read()
        self._post({"action": "end_turn"}, "end_turn")

    # bookkeeping verbs ----------------------------------------------------
    def _do_read(self, body: dict[str, Any]) -> None:
        self.read()
        self.emit({"step": "read", "label": str(body.get("label") or ""),
                   "after": digest(self.state)})

    def _do_mark(self, body: dict[str, Any]) -> None:
        """Move the delta baseline to now, for a bracket wider than one action."""
        self.read()
        self.before = self.state
        self.emit({"step": "mark", "at": digest(self.state)})

    def _do_expect(self, body: dict[str, Any]) -> None:
        self.read()
        results = {}
        for check, spec in body.items():
            why = CHECKS[check](spec, self.before, self.state)
            results[check] = why or "ok"
            if why:
                self.emit({"step": "expect", "check": check, "spec": spec,
                           "ok": False, "detail": why})
                raise ExpectFailed(check, why, self.before, self.state)
        self.emit({"step": "expect", "checks": results, "ok": True,
                   "after": digest(self.state)})


# ------------------------------------------------------ the soak seam ------

class ScenarioPolicy:
    """`policy_v1` with the first combat screen replaced by one scenario.

    Everything outside that one screen is delegated untouched, for
    `probe_block`'s reason: the claim is about one card in one fight, and
    re-deciding the map or the draft would put a second policy into a check
    that is supposed to have none.
    """

    def __init__(self, runner: Runner, turns: int = 12):
        from understudy import policy_v1
        self._policy = policy_v1
        self.POLICY_VERSION = "scenario/" + policy_v1.POLICY_VERSION
        self.BLOCK_MATTERS_FRACTION = policy_v1.BLOCK_MATTERS_FRACTION
        self.COMPANION_SHARE_FOR_GUEST_CAST = \
            policy_v1.COMPANION_SHARE_FOR_GUEST_CAST
        self.Memo = policy_v1.Memo
        self.runner = runner
        self.turns = turns
        self.done = False
        self.ok: bool | None = None

    def decide(self, state: dict[str, Any], memo: Any,
               commit: str | None = None):
        st = str(state.get("state_type") or "")
        if not self.done and st in COMBAT_SCREENS:
            self.done = True
            # THE WHOLE SCENARIO RUNS HERE, posting its own actions -- see the
            # module docstring. `soak._mechanical_action` owns `hand_select`
            # before `decide` is ever asked, so a scenario that returned one
            # Decision per call could not choose which card it exhausts.
            self.ok = self.runner.run()
            state = self.runner.state or state
        # Combat is handed back so the fight can END; the run stops on the
        # driver's own `max_fights` bound. Every reading the scenario took is
        # already on disk by now, exactly as the probes arrange it.
        return self._policy.decide(state, memo, commit=commit)


# ---------------------------------------------------------------- main -----

def _print_failure(runner: Runner) -> None:
    for f in runner.failures:
        print(f"\nFAILED {f['step']} / {f['check']}: {f['detail']}",
              file=sys.stderr)
        print("--- before ---", file=sys.stderr)
        print(json.dumps(f["before"], indent=1, default=str), file=sys.stderr)
        print("--- after ----", file=sys.stderr)
        print(json.dumps(f["after"], indent=1, default=str), file=sys.stderr)


def cmd_check(args) -> int:
    """Parse without a game. The lint half of this module, and the thing to
    run before walking to the machine the game is on."""
    paths = [Path(args.file)] if args.file else all_scenarios()
    bad = 0
    for p in paths:
        try:
            s = load(p)
            print(f"OK   {p.name}: {len(s.steps)} steps, "
                  f"{sum(1 for v, _ in s.steps if v == 'expect')} expects, "
                  f"{len(s.assumptions)} assumption(s)")
        except (ScenarioError, yaml.YAMLError) as e:
            bad += 1
            print(f"BAD  {p.name}: {e}", file=sys.stderr)
    return 1 if bad else 0


def cmd_run(args) -> int:
    from understudy import soak

    scenario = load(args.file)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else \
        LOG_DIR / f"scenario-{scenario.name}-{stamp}.jsonl"

    print(f"scenario: {scenario.name}  ({scenario.character})")
    if scenario.notes:
        print(scenario.notes.strip())
    for a in scenario.assumptions:
        print(f"  ASSUMES: {a}")
    print(f"GUARDRAIL: {bridge.GRANT_GUARDRAIL}")

    summary: dict[str, Any] = {}
    with out_path.open("w", encoding="utf-8") as fh:
        runner = Runner(scenario, args.why, out=fh)
        runner.emit({"step": "scenario_begin", "character": scenario.character,
                     "file": str(scenario.path), "seed": scenario.seed,
                     "assumptions": scenario.assumptions})
        policy = ScenarioPolicy(runner, turns=scenario.turns)
        summary = soak.run_scripted(policy, stamp,
                                    character=scenario.character,
                                    max_fights=1,
                                    chosen_seed=scenario.seed,
                                    do_setup=not args.no_setup)
        runner.emit({"step": "scenario_end", "ok": policy.ok,
                     "failures": len(runner.failures), "run": summary})

    print(f"\nlog: {out_path}")
    if policy.ok is None:
        print("NOT RUN: no combat screen was ever reached", file=sys.stderr)
        return 2
    if not policy.ok:
        _print_failure(runner)
        return 1
    print(f"PASS: {sum(1 for v, _ in scenario.steps if v == 'expect')} "
          f"expect step(s) held")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="drive one scenario against the real game")
    r.add_argument("file")
    r.add_argument("--why", default="",
                   help="one line, logged on every row. REQUIRED: a scenario "
                        "grants cards and writes a board")
    r.add_argument("--out", default="")
    r.add_argument("--no-setup", action="store_true",
                   help="attach to a game that is already up")
    r.set_defaults(func=cmd_run)

    c = sub.add_parser("check", help="parse only; no game involved")
    c.add_argument("file", nargs="?", default="")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except (ScenarioError, yaml.YAMLError) as e:
        print(f"scenario error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
