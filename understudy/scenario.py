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
      - set_block: {who: first, amount: 0}
      - set_power: {who: player, name: SPARK_POWER, amount: 2}
      - play:   {card: "Take It From the Top", target: first}
      - expect: {enemy_hp_block_delta: {who: first, amount: -10}}

ONE SELECTOR VOCABULARY, AND EVERY VERB THAT ADDRESSES A CREATURE READS IT.
`who` and `target` accept an entity id (`JAW_WORM_0`), a display name, or one
of `ENEMY_SYMBOLS` (`first`, `lowest_hp`, `highest_hp`) -- and the board-setup
verbs resolve it against the latest GET before posting, exactly as `play` does,
because the bridge only knows entity ids. That was NOT true on the first live
run (EB-146): `set_block: {who: first}` posted the literal string `first` and
the bridge answered *No living creature named 'first'*. Every step record now
carries both the selector as written and the id it resolved to, so a log read
back later can tell which creature was actually written.

`set_resource` and `set_energy` take NO `who`. The bridge writes both to the
player's own combat state and ignores the field, so naming a creature there
would set the player's number under an enemy's name; the parser refuses it
rather than letting it read as an enemy write that silently was not one.

`ASSUMPTIONS` IS PART OF THE FORMAT AND IS PRINTED WITH THE RESULT. An exact
expected number usually depends on something the scenario did not set -- the
enemy's Block, a Vulnerable stack, which enemy the encounter rolled. A file
that states its assumptions is a file whose failure can be read; one that does
not is a file whose failure means "something, somewhere".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from understudy import adapter, bridge, naming

SCENARIO_DIR = Path(__file__).resolve().parent / "scenarios"
# Gitignored, like `logs/soak/` and for the same reason: a reading taken on a
# hand-set board is disqualified by construction, and a disqualified reading
# committed to the repo is one a later reader can mistake for evidence.
LOG_DIR = Path(__file__).resolve().parent / "logs" / "scenario"

# The screens a scenario acts on itself. Combat is where it starts; the two
# selection screens are where a card's own effect can take it mid-step.
COMBAT_SCREENS = ("monster", "elite", "boss")
SELECT_SCREENS = ("hand_select", "card_select")

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
    # EB-150. A choose-one card's modes are faces on that same screen, and the
    # generator prints the sheet's `label` into both the option class's title
    # and its description -- so a mode is named here exactly as
    # docs/furina-cards.yaml:707 spells it, and a label edit on the sheet is an
    # edit here too. That coupling is deliberate: these are the only names in
    # this table that can go stale from a SHEET edit rather than a code one.
    "Gain 1 Energy and 2 Encore":
        "mode 0 of deep_breath on the choose-a-card screen "
        "(Cards/Furina/Generated/DeepBreath.cs, DeepBreathModeA)",
    "Spend 3 Encore: draw 3":
        "mode 1 of the same card (DeepBreathModeB)",
}

# Every verb a step may name. Kept as data so the parser can refuse an unknown
# key with the list, rather than skipping it -- a mistyped step that is silently
# ignored is a scenario that passes without running.
ACTION_STEPS = ("play", "select", "confirm", "end_turn")
SETUP_STEPS = ("give", "set_resource", "set_energy", "set_hp", "set_block",
               "set_power", "clear_hand")
OTHER_STEPS = ("expect", "read", "mark", "wait")
STEP_VERBS = ACTION_STEPS + SETUP_STEPS + OTHER_STEPS

# The setup verbs that address a CREATURE, and so take the `play` target's
# selector vocabulary; and the two that address the player and take no `who` at
# all. Kept as data beside the verb list because both facts are enforced -- the
# first by resolution before the POST, the second by a parse-time refusal.
CREATURE_SETUP_STEPS = ("set_hp", "set_block", "set_power")
PLAYER_ONLY_SETUP_STEPS = ("set_resource", "set_energy", "clear_hand")

# The setup verbs that take no `amount` either. `clear_hand` is the only one --
# it is the one verb here that moves CARDS rather than a number, and a file
# that wrote an amount on it would be asking for something the endpoint has no
# way to honour.
AMOUNTLESS_SETUP_STEPS = ("clear_hand",)

# How many settles `clear_hand` will wait for an emptying hand. A hand holds at
# most `CardPile.MaxCardsInHand` = 10, each moving on its own queued command,
# and the runner's settle is 0.7 s -- so this is a ceiling with room in it
# rather than a tuned number, and it is a REFUSAL bound: reaching it fails the
# step by name.
CLEAR_HAND_SETTLES = 12

# The ceiling on one `wait` step. A turn boundary is the only thing in a
# scenario that takes longer than the runner's own settle -- the enemy side
# acts, the block clears, the hand is dealt and (for the Kokomi arm) the Plan
# queue drains, each with its own visuals -- and 30 s is a bound with room in
# it rather than a tuned number. A file that needs more than this is a file
# that is waiting for something a scenario should be asserting instead.
MAX_WAIT_SECONDS = 30.0


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
    # EB-147 (R213 B). This file names cards on the QUARANTINED prototype
    # surface, which is EMPTY in the committed tree by design -- accepted and
    # rejected slices leave it, so the healthy state has no rows. The pack's
    # card-name lint therefore cannot resolve those names against a sheet, and
    # this flag is how it is TOLD so, rather than the lint being loosened for
    # every file. The lint still checks what is checkable with no surface:
    # every granted id on a prototype scenario carries the prototype prefix,
    # so a typo naming a shipped card is still caught.
    prototype: bool = False

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
    if verb == "wait" and isinstance(raw, (int, float)):
        return {"seconds": float(raw)}
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
        prototype=bool(blob.get("prototype", False)),
    )


def _validate(i: int, verb: str, body: dict[str, Any]) -> None:
    def need(*keys: str) -> None:
        for k in keys:
            if body.get(k) in (None, ""):
                raise ScenarioError(f"step {i} ('{verb}'): needs '{k}'")

    if verb in ("give", "play"):
        need("card")
    elif verb in ("set_resource", "set_power"):
        # `name` is the resource id for one and the power id (or printed title)
        # for the other; one key, because to a scenario author both read as
        # "the thing being set" and a second spelling buys nothing.
        need("name")
        if "amount" not in body:
            raise ScenarioError(f"step {i} ('{verb}'): needs 'amount'")
    elif verb in ("set_energy", "set_hp", "set_block"):
        if "amount" not in body:
            raise ScenarioError(f"step {i} ('{verb}'): needs 'amount'")
    elif verb == "select":
        if not body.get("cards"):
            raise ScenarioError(f"step {i} ('select'): needs 'cards'")
    elif verb == "wait":
        # A BOUNDED WAIT, refused at parse time rather than clamped at run
        # time. A scenario is attended and the game is somebody's live process:
        # a file that asked for a minute of silence would be a file that looks
        # hung, and a silently clamped number is a file whose text stops being
        # what ran.
        try:
            seconds = float(body.get("seconds", 1.0))
        except (TypeError, ValueError):
            raise ScenarioError(
                f"step {i} ('wait'): 'seconds' must be a number, got "
                f"{body.get('seconds')!r}")
        if not 0 < seconds <= MAX_WAIT_SECONDS:
            raise ScenarioError(
                f"step {i} ('wait'): 'seconds' must be in (0, "
                f"{MAX_WAIT_SECONDS}], got {seconds}")
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
    if verb in PLAYER_ONLY_SETUP_STEPS and body.get("who"):
        # Refused rather than ignored. The bridge writes both of these to the
        # player's own combat state whatever `who` says, so a file that named an
        # enemy would read as an enemy write and be a player write -- the
        # silent-wrong-target shape `find_enemy` exists to prevent one verb over.
        raise ScenarioError(
            f"step {i} ('{verb}'): takes no 'who' -- the bridge writes it to "
            f"the PLAYER's combat state and ignores the field, so naming "
            f"{body['who']!r} here would set the player's number under that "
            f"creature's name")
    if verb in AMOUNTLESS_SETUP_STEPS and "amount" in body:
        # Checked AFTER the `who` rule, so a file that wrote both is told
        # about the target first -- naming the wrong creature is the worse of
        # the two mistakes and the one `find_enemy` exists to catch.
        raise ScenarioError(
            f"step {i} ('{verb}'): takes no 'amount' -- it moves the whole "
            f"hand and the endpoint has no partial form, so a number here "
            f"would read as a count and change nothing")


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


# The game's rich-text markup, as it appears in a modal option's own name:
# `[gold]`, `[/gold]`, `[b]`, and any other single bracketed tag. Folded out
# by `card_key` -- see its docstring for the defect that made this necessary.
_RICH_TEXT_TAG = re.compile(r"\[/?[a-z0-9_]+(?:=[^\]]*)?\]")


def card_key(text: str) -> str:
    """One comparable key for a card named by id, loc key, or printed title.

    `KLEEMOD-TAKE_IT_FROM_THE_TOP`, `take_it_from_the_top` and
    `Take It From the Top` are the three spellings that appear across the
    sheets, the wire and a scenario file, and a scenario author should not have
    to know which one this frame is using. Case, the BaseLib prefix, the game's
    own RICH-TEXT TAGS and the difference between `-`, `_` and a space all fold
    away; nothing else does.

    WHY THE TAGS FOLD, and it is a defect this function was on the wrong side
    of. A "Choose one" modal names its options with the game's markup left in
    (`Spend 6 [gold]Charge[/gold]: gain 12 Block`), while the packet a grader
    reads is SCRUBBED of markup by `qa_packet` before the face is printed. So a
    replay answering the modal in the printed vocabulary -- which is the only
    vocabulary a blind grader has -- could not match its own option, and every
    priced modal line stopped `modal_unanswered`. Found live on Kokomi slice 2
    `t06`, on both graders, 2026-08-29. Only the TAGS are removed; the words
    between them are part of the name and stay.
    """
    key = str(text or "").strip().casefold()
    if key.startswith("kleemod-"):
        key = key[len("kleemod-"):]
    key = _RICH_TEXT_TAG.sub("", key)
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


def find_pet(state: dict[str, Any], who: str) -> str | None:
    """The Bake-Kurage's entity id when `who` names it, else `None`.

    `EB-292`. THE ONE TARGET THAT IS NOT AN ENEMY. The Kokomi arm's jellyfish
    is a PET: it is on the player's side, `find_enemy` cannot see it, and a
    Plan card's only legal target is that creature. The wire publishes it in
    the arm's own block (`player.kokomi_plans.pet_entity_id`, written by
    `KleeMod.Powers.KokomiPlan.Snapshot`) rather than in `battle.enemies`,
    which is the same place `blindplay._pet_target` reads it from -- one
    contract, two readers, so a seat and a scenario cannot aim differently.

    NAMED, NEVER DEFAULTED, for `blindplay._pet_target`'s reason: a card that
    could go either way and was aimed at nothing is played NOW.
    """
    plans = ((state.get("player") or {}).get("kokomi_plans")) or {}
    if not isinstance(plans, dict):
        return None
    pet_id = plans.get("pet_entity_id")
    if not pet_id:
        return None
    name = str(plans.get("pet_name") or "Bake-Kurage")
    return str(pet_id) if str(who or "").strip().casefold() == name.casefold() \
        else None


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


class _LogWindow:
    """Where in `godot.log` this scenario's own output starts.

    A CURSOR AND NOT THE WHOLE FILE, because `--no-setup` attaches to a game
    that has already been playing: a scenario must not fail on an engine error
    somebody else's fight produced, and it must not pass because the one it
    caused scrolled past. The cursor is set when the `Runner` is built, which
    is before its first step and after the launch either way.
    """

    def __init__(self) -> None:
        self.offset = 0

    def path(self) -> Path:
        """The log of the instance THIS THREAD is bound to.

        `bridge.current_instance()` is the lane binding the whole harness
        already resolves against (`EB-210`); an unbound thread is lane 0, whose
        tree is the machine's own `%APPDATA%` -- the same fallback
        `bridge.current_base` makes.

        BUILT BY HAND RATHER THAN THROUGH `instances.lane("lane0")`, and the
        reason is a red CI run: `lane()` resolves the GAME DIRECTORY, which
        `SystemExit`s when `klee-mod/local.props` is absent. A `Runner` is
        constructed by two dozen unit tests on a machine that has no game and
        needs no game, and a log path has no business asking where the game is
        installed -- only where its user tree is.
        """
        from understudy import instances
        inst = bridge.current_instance()
        root = getattr(inst, "appdata", None) if inst is not None else None
        if root is None:
            root = os.environ.get("APPDATA", "")
        return Path(root).joinpath(*instances.LOG_RELATIVE)

    def reset(self) -> None:
        try:
            self.offset = self.path().stat().st_size
        except (OSError, ValueError):
            self.offset = 0

    def tail(self) -> tuple[list[str], Path]:
        """Everything written since `reset`, and the whole file after a relaunch.

        THE TRUNCATION CASE IS THE NORMAL ONE, not an edge: the runner is built
        before `soak.run_scripted` launches the game, and the game REWRITES
        `godot.log` from zero on every launch. A cursor taken from the previous
        session's file is past the new file's end, and seeking there would read
        nothing and pass every check -- which is a silent instrument, the one
        failure mode this check must not have.
        """
        p = self.path()
        offset = self.offset
        try:
            if p.stat().st_size < offset:
                offset = 0
        except OSError:
            offset = 0
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            fh.seek(offset)
            return fh.read().splitlines(), p


LOG_WINDOW = _LogWindow()


def _check_log_lacks(spec, before, after):
    """No line matching `text` has reached `godot.log` since the run began.

    THE ONLY CHECK IN THIS FILE THAT DOES NOT READ THE WIRE, and it exists
    because `EB-292`'s defect is invisible to the wire: an `NCard` given a
    non-finite size still reports a legal board, and the first thing that goes
    wrong is a Godot error printed every frame until the card trail runs the
    process out of memory. The bridge answers normally right up to the moment
    it stops answering at all, so the state a scenario can assert on cannot see
    it and the log can.

    A MISSING LOG IS A FAILURE, not a pass: the instrument is the file, and a
    check that cannot find it has not looked.
    """
    want = str(spec if isinstance(spec, str) else spec["text"])
    try:
        lines, path = LOG_WINDOW.tail()
    except OSError as e:
        return f"no godot.log to read ({e}); the check could not be made"
    hits = [ln for ln in lines if want in ln]
    if not hits:
        return None
    return (f"{len(hits)} line(s) matching {want!r} in {path} since the run "
            f"began; first: {hits[0].strip()!r}")


CHECKS: dict[str, Callable[..., str | None]] = {
    "log_lacks": _check_log_lacks,
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
        # Where this run's engine output starts. Set here rather than at the
        # first `log_lacks` step, so a file that asserts the log late still
        # sees everything its own steps produced.
        LOG_WINDOW.reset()

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

    def _resolve_who(self, label: str, who: str) -> str:
        """One creature selector, as the concrete entity id the bridge knows.

        The bridge addresses creatures by `"player"` and by the entity ids its
        last GET reported, and by nothing else; a scenario file is written in
        the same vocabulary a `play` target uses, which includes the symbols
        (`first`, `lowest_hp`, `highest_hp`) and a display name. Resolving here
        rather than in the file is what makes a scenario portable across seeds
        -- see `ENEMY_SYMBOLS` for why writing `JAW_WORM_0` into a file is a
        scenario that fails on every seed but one, for a reason that is not its
        subject.

        Resolved against a FRESH read, for `_do_play`'s reason: the board one
        frame ago is a different board, and `lowest_hp` in particular names a
        different creature after every hit.
        """
        raw = str(who or "player").strip()
        if raw.casefold() == "player":
            return "player"
        self.read()
        enemy = find_enemy(self.state, raw)
        if enemy is None:
            raise ExpectFailed(
                label, f"no creature {raw!r}; the fight has "
                       f"{[adapter.enemy_id(e) for e in adapter.enemy_blobs(self.state)]}"
                       f" (and 'player')",
                self.state, self.state)
        return adapter.enemy_id(enemy)

    def _debug(self, op: str, label: str, selector: str | None = None,
               **kw: Any) -> None:
        report = self.wire.debug_state(op, self.why, **kw)
        row: dict[str, Any] = {"step": label, "request": dict(kw, op=op),
                               "result": report}
        if selector is not None:
            # BOTH, on every board write that names a creature: the selector is
            # what the file said and the id is what the bridge was told, and a
            # log read back six months later has to be able to tell which
            # creature moved without re-deriving the symbol against a board it
            # no longer has.
            row["selector"] = selector
            row["resolved_who"] = kw.get("who")
        self.emit(row)
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
        selector = str(body.get("who") or "player")
        self._debug("set_hp", "set_hp", selector=selector,
                    amount=int(body["amount"]),
                    who=self._resolve_who("set_hp", selector))

    def _do_set_block(self, body):
        selector = str(body.get("who") or "player")
        self._debug("set_block", "set_block", selector=selector,
                    amount=int(body["amount"]),
                    who=self._resolve_who("set_block", selector))

    def _do_clear_hand(self, body):
        """EB-165. Empty the hand to the bottom of the draw pile.

        No `who` and no `amount`: the endpoint empties the LOCAL PLAYER's hand
        and there is no partial form. `_debug` settles on the queued answer,
        which matters more here than anywhere else in this class -- the very
        next step is normally a grant, and a grant that raced the clear would
        be granted into a hand that is about to be emptied.
        """
        self._debug("clear_hand", "clear_hand")
        # AND THEN WAIT FOR IT, which the other five ops do not need to do.
        # The clear queues ONE pile move per card and each runs its own pile
        # visuals, so a ten-card hand empties over rather more frames than the
        # single settle `_debug` takes -- and the next step is a grant, which
        # would land in a hand still being emptied. Bounded, and the emptiness
        # is asserted rather than assumed: a hand that never empties is a
        # failure here, where it names the clear, instead of a wrong hand in a
        # design-blind packet nobody can see is wrong.
        for _ in range(CLEAR_HAND_SETTLES):
            if not _hand(self.state):
                break
            self._settle()
        left = [c.get("name") for c in _hand(self.state)]
        self.emit({"step": "clear_hand_settled", "left_in_hand": left})
        if left:
            raise ExpectFailed(
                "clear_hand",
                f"the hand did not empty; still holding {left}",
                self.state, self.state)

    def _do_set_power(self, body):
        selector = str(body.get("who") or "player")
        self._debug("set_power", "set_power", selector=selector,
                    amount=int(body["amount"]), power=str(body["name"]),
                    who=self._resolve_who("set_power", selector))

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
            # THE JELLYFISH FIRST, `blindplay._play`'s order and for its
            # reason: it is the one target that is not an enemy, so asking
            # `find_enemy` first would refuse a legal Plan play with a message
            # about the wrong half of the board.
            pet = find_pet(self.state, str(target))
            if pet is not None:
                action["target"] = pet
            else:
                enemy = find_enemy(self.state, str(target))
                if enemy is None:
                    raise ExpectFailed(
                        "play", f"no enemy {target!r}; the fight has "
                                f"{[adapter.enemy_id(e) for e in adapter.enemy_blobs(self.state)]}",
                        self.state, self.state)
                action["target"] = adapter.enemy_id(enemy)
        # EB-184: the chosen MODE, when the step names one, so the bridge can
        # ask that mode whether the play aims rather than asking the card's
        # printed type. A `choose_one` card typed as an Attack declares
        # `AnyEnemy` for the sake of the mode that aims -- the game fixes the
        # aim before the mode is chosen -- so the type answers for the CARD and
        # not for the play, and the targetless mode was refused with "Card
        # requires a target". Passed through verbatim: the bridge owns the
        # match against the card's own printed mode labels.
        if body.get("mode"):
            action["mode"] = str(body["mode"])
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

    def _do_wait(self, body: dict[str, Any]) -> None:
        """Sleep, then read. The one step that buys time rather than state.

        The runner's settle is sized for a card play; a TURN BOUNDARY is not,
        and `end_turn` is the only action that crosses one. It does not move
        the delta baseline: a wait is not an action, so an `expect` after it
        still reads the bracket around the play or the end-turn before it.
        """
        seconds = float(body.get("seconds", 1.0))
        self.sleep(seconds)
        self.read()
        self.emit({"step": "wait", "seconds": seconds,
                   "after": digest(self.state)})

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
