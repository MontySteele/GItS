"""EB-203: A CARD THAT NEEDS AIMING, PLAYED AT NOBODY.

WHAT WENT WRONG. `KLEESPARK-R1` sealed eight lines and the bridge refused two
of them: a play named a card that takes a target and the form carried
`target: null`, so `staged_turn.execute_steps` emitted a `play` step with no
`target` body key and the game had nothing to aim at. Two of eight graded
lines were therefore UNTESTED -- not because the reading was wrong, but
because nothing between the form and the game ever asked whether the line
could be played at all.

Nothing was going to catch it. `staged_turn.load_form` requires only `card`;
`seat.form_schema` makes `target` REQUIRED AND NULLABLE on purpose -- a null
target is the honest answer for a card that needs none, and a schema that
forbade it would forbid Duck and Cover -- and the local seat enforces no
schema at all. So the check has to be a FALSIFIER, run against the board, and
it is: `target_missing`, refused before the grade like every other rule in
`staged_turn.FALSIFIERS`.

WHERE "NEEDS A TARGET" COMES FROM, AND WHY IT IS NOT THE PACKET
---------------------------------------------------------------
**The packet does not carry targeting.** `qa_packet._hand` emits a title, the
printed text, a cost, a printed cost, `upgraded`, `playable` and the game's
own `unplayable_reason` -- and no aiming field, because the wire's hand entry
has none to give. So the fact is DERIVED FROM THE CARD SHEET the packet was
built from, and this docstring is where that is recorded.

The sheets are `understudy/resource_order.SHEETS` -- the same seven files, read
the same way, so the two checks cannot come to disagree about what a card is.
The spec is the effect's own `target:` key, whose whole vocabulary across every
sheet is four words: `enemy`, `all_enemies`, `random_enemy`, `self`. Exactly
one of them is AIMED. `enemy` means the player picks; the other three resolve
themselves. So:

    a card needs a target  <=>  some effect that resolves names `target: enemy`

and that is deliberately about the EFFECT rather than the card's `type:`. A
Skill that places a Bomb on one enemy (Powder Pop, Pop!, Mine Toss's shipped
twin) is aimed and is not an Attack; an Attack that hits everything (Tinder
Toss) is not. Typing the rule off `type: attack` would have been wrong in both
directions.

THE MODE REFINEMENT, WHICH IS `EB-184` FROM THE OTHER SIDE. A *Choose one*
card has one aimed mode and one that is not -- and `EB-184` is exactly that
defect, a modal typed Attack demanding a target on its targetless Block mode.
So when the form records `choose:`, only that mode's effects are read
(`resource_order.selected_effects`, the same resolver the order flag uses). A
play with no recorded mode falls back to the whole row: refusing a line whose
mode nobody stated is the safe direction, because the alternative is sealing
another line the bridge will not play.

WHAT THIS MODULE DOES NOT DO. **It never repairs a form** -- `M63` is "refuse
only, never repair", and a tool that filled in the obvious target would be
choosing which enemy a reader meant. It does not say a null target is wrong:
`target: null` stays legal, and is the required answer, for every card that
aims at nothing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from understudy import resource_order

# The one aimed spec. The other three (`all_enemies`, `random_enemy`, `self`)
# resolve without the player, and a card built only from those takes no target.
AIMED = "enemy"

# Recorded in every summary this module produces, because "where did the tool
# learn that this card takes a target" is the first question a refused reader
# will ask and the answer is not on the page they were shown.
SOURCE = ("the card sheets (understudy/resource_order.SHEETS: the three "
          "character sheets, the three companion sheets and "
          "docs/prototype-surface.yaml), read through each effect's own "
          "`target:` key. The blind packet carries NO targeting field -- the "
          "wire's hand entry has none -- so the sheet is the derivation and "
          "this is the record of it")

RULE = ("a play that names a card whose effects aim at ONE enemy must carry "
        "that enemy's printed name in `target`; a card that aims at nobody "
        "must carry `target: null`")

_CARD_HEAD = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


# ------------------------------------------------------------ the sheet ----

def aims_at_one(effects: Any) -> bool:
    """Does anything in these effects resolve against ONE chosen enemy?"""
    for eff in resource_order._walk(effects):
        if str(eff.get("target") or "").strip().casefold() == AIMED:
            return True
    return False


def needs_target(row: Mapping[str, Any] | None, choose: Any = None) -> bool:
    """Does this sheet row, played this way, ask the player to aim?

    A row no sheet printed (`None`) answers `False`: a refusal raised because
    a title could not be found would name the harness rather than the reading,
    which is the same call `resource_order.unresolved` makes.
    """
    if row is None:
        return False
    return aims_at_one(resource_order.selected_effects(row, choose))


def takes_a_target(title: Any, *,
                   index: Mapping[str, Mapping[str, Any]] | None = None,
                   repo: Path | None = None) -> bool:
    """The one-title door, for a caller holding a printed name and nothing else."""
    cards = index if index is not None else resource_order.card_index(repo)
    return needs_target(cards.get(resource_order.normalise(title)))


# ------------------------------------------------------------ the packet ---

def packet_titles(turn_dir: Path) -> list[str]:
    """The printed titles of the hand the grader was shown, in printed order.

    `packet.json` first, because it is the structured half of the same page.
    `packet.md` is the fallback, and there a `###` heading is a card only when
    a `- Cost:` line follows it -- the enemies are `###` headings too.
    """
    blob = turn_dir / "packet.json"
    if blob.is_file():
        try:
            packet = json.loads(blob.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            packet = {}
        hand = ((packet.get("board") or {}).get("hand") or [])
        titles = [str(c.get("title") or "") for c in hand if isinstance(c, dict)]
        if titles:
            return [t for t in titles if t]
    md = turn_dir / "packet.md"
    if not md.is_file():
        return []
    text = md.read_text(encoding="utf-8")
    heads = list(_CARD_HEAD.finditer(text))
    out = []
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        if re.search(r"^-\s*Cost:", text[head.end():end], re.MULTILINE):
            out.append(head.group(1).strip())
    return out


def hand_cards_that_take_a_target(
        titles: Sequence[str], *,
        index: Mapping[str, Mapping[str, Any]] | None = None,
        repo: Path | None = None) -> list[str]:
    """Which of the hand's printed titles need aiming. The list a refusal prints.

    The whole hand is walked, not just the line, because the refusal has to be
    actionable by somebody who is looking at the page: "you played Powder Pop
    at nobody" is half the message and "these three cards take a target" is
    the other half.
    """
    cards = index if index is not None else resource_order.card_index(repo)
    seen: list[str] = []
    for title in titles:
        row = cards.get(resource_order.normalise(title))
        if needs_target(row) and title not in seen:
            seen.append(title)
    return seen


# ----------------------------------------------------------- the finding ---

def findings(chosen_line: Sequence[Mapping[str, Any]], *,
             index: Mapping[str, Mapping[str, Any]] | None = None,
             repo: Path | None = None) -> list[dict[str, Any]]:
    """One entry per play that had to aim and did not. Empty is the good case."""
    cards = index if index is not None else resource_order.card_index(repo)
    out: list[dict[str, Any]] = []
    for i, play in enumerate(chosen_line or []):
        title = str(play.get("card") or "")
        row = cards.get(resource_order.normalise(title))
        if not needs_target(row, play.get("choose")):
            continue
        if str(play.get("target") or "").strip():
            continue
        out.append({
            "position": i + 1,
            "card": title,
            "mode": str(play.get("choose") or ""),
            "why": (f"play {i + 1} names {title!r}, whose printed effects aim "
                    f"at ONE enemy, and carries no target. The bridge has "
                    f"nothing to aim at, so this line cannot be replayed -- "
                    f"it is sealed and UNTESTED, which is the state "
                    f"KLEESPARK-R1 ended two of its eight lines in"),
        })
    return out


def summary(chosen_line: Sequence[Mapping[str, Any]], *,
            hand: Sequence[str] = (),
            index: Mapping[str, Mapping[str, Any]] | None = None,
            repo: Path | None = None) -> dict[str, Any]:
    """The whole check as one blob, for a verdict to carry verbatim."""
    cards = index if index is not None else resource_order.card_index(repo)
    hits = findings(chosen_line, index=cards)
    return {
        "refused": bool(hits),
        "findings": hits,
        "hand_takes_a_target": hand_cards_that_take_a_target(hand, index=cards),
        "hand": [str(t) for t in hand],
        "rule": RULE,
        "derived_from": SOURCE,
        "repair": ("out of scope by M63: this refuses a form and never "
                   "repairs one"),
    }
