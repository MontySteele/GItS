"""The observation as the page the tester is handed. Same content.

Cut out of `blindplay.py` by `EB-180`: `render`, the notes it prints
beside a screen, the arm-keyword register and `observe` (the two
composed). Re-exported from `blindplay.py`, so `blindplay.render(obs)`
and `blindplay.observe(state)` still resolve.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from understudy import qa_packet
from understudy.blindplay_board import PHASE_FLIP_LINE, enchant_moves_line
from understudy.blindplay_notes import (_AURA_NAME_RE, ATTACK_BUFF_NOTE,
                                        AURA_NOTE, BOMB_FORECAST_NOTE,
                                        BOMB_REACTION_CLAUSE,
                                        REACTION_ELEMENTS,
                                        AUTO_TURN_NOTE,
                                        BUFF_INTENT_CLAUSE,
                                        CLONE_NOTE, EMPTY_SHELVES_NOTE,
                                        INTENT_NUMBER_DISAGREES,
                                        INTENT_SOURCE_NOTE,
                                        INTENT_SOURCE_NOTE_BREAKDOWN,
                                        ONE_USE_DISCOUNT_NOTE,
                                        ONE_USE_RIDER_NOTE,
                                        PER_HIT_NOTE,
                                        MAP_FLOOR_LINE, MAP_RUN_LINE,
                                        CARD_REWARD_ALTERNATIVE_NOTE,
                                        CARRY_OUT_BOARD_NOTE,
                                        CHOOSER_CONFIRM_NOTE,
                                        TWO_LINE_WAITING_ROW,
                                        CHOOSER_ONE_CHOICE_NOTE,
                                        CHOOSER_MAYBE_CLOSES_NOTE,
                                        CLOSES_NOTE_HEAD,
                                        ONE_PRESS_CHOOSER_KIND,
                                        chooser_note,
                                        DEFEND_INTENT_CLAUSE,
                                        ENEMY_HANDLE_NOTE,
                                        ENEMY_REPLACED_LINE, ENEMY_REVIVED_LINE,
                                        ENEMY_SIZE_NOTE,
                                        EVENT_NO_DECLINE_NOTE,
                                        TREASURE_PROCEED_NOTE,
                                        FRONT_ENEMY_NOTE,
                                        HAND_REPEAT_NOTE,
                                        LAST_MORNING_NOTE,
                                        METER_CAPPED_NOTE,
                                        METER_DEFINED_NOTE, METER_NOTE,
                                        METER_RULES,
                                        MULTI_INTENT_LABEL,
                                        MULTI_INTENT_NOTE,
                                        NO_REACTION_THIS_TURN,
                                        PENDING_PICK_NOTE, PICKED_MARK,
                                        REACTIONS_HEADING,
                                        RESOLUTIONS_HEADING,
                                        RESOLUTION_ROW,
                                        RESOLUTION_HIT_ROW,
                                        RESOLUTION_HIT_BLOCKED,
                                        RESOLUTION_HIT_ALL_BLOCKED,
                                        RESOLUTION_HIT_ON_YOU,
                                        RESOLUTION_HIT_SOURCE,
                                        RESOLUTION_HIT_THORNS, THORNS_POWER,
                                        RESOLUTION_HIT_SELF,
                                        RESOLUTION_NO_HITS,
                                        RESOLUTION_NO_HITS_STAGE,
                                        RESOLUTION_SUMMONED,
                                        RESOLUTION_OATH, RESOLUTION_FANG,
                                        RESOLUTION_FANG_DEFAULT,
                                        RESOLUTION_NO_AURA,
                                        RESOLUTION_HIT_KILLED,
                                        RESOLUTION_KILLED,
                                        RESOLUTION_AUTO_CLAUSE,
                                        RESOLUTION_CARRIED_CLAUSE,
                                        RESOLUTION_OVERFLOW_CLAUSE,
                                        RESOLUTION_AUTO_TURN_NOTE,
                                        NO_RESOLUTIONS_THIS_TURN,
                                        INTENT_FOLD_CLAUSE,
                                        INTENT_FOLD_NOTHING,
                                        INTENT_TOTAL_CLAUSE,
                                        INTENT_TARGET_SIDE,
                                        INTENT_TARGET_NOTE,
                                        INTENT_ICON_NUMBER,
                                        REWARD_ALTERNATIVES_HEADING,
                                        REWARD_ALTERNATIVE_ROW,
                                        REWARD_ALTERNATIVE_UNNAMED,
                                        GRID_INCOMPLETE_NOTE,
                                        DECK_IS_THE_RUNS_OWN,
                                        REACTION_CARRIED_CLAUSE,
                                        REACTION_FROZEN_THAWED_CLAUSE,
                                        REACTION_CARRIED_ONLY, REACTION_ROW,
                                        REACTION_ROW_NO_SOURCE,
                                        RELIC_ANSWER_ROW,
                                        RELIC_ANSWER_ROW_NO_TARGET,
                                        RELIC_ANSWER_GAIN_ROW,
                                        RELIC_ANSWERS_HEADING,
                                        CARD_OFFER_AFTER_SKIP_NOTE,
                                        PLAN_AIM_NOTE,
                                        PLAN_BLOCK_NOTE,
                                        PLAN_CASKET_AURA_CLAUSE,
                                        PLAN_COUNT_CAPPED_NOTE,
                                        PLAN_COUNT_NOTE,
                                        PLAN_WRITTEN_NUMBER_NOTE,
                                        PLAN_HYDRO_NOTE,
                                        PLAN_PAST_LETHAL_BLOCK,
                                        PLAN_PAST_LETHAL_CLAUSE,
                                        POWER_NOTE, SELECTION_NOTE,
                                        SPARK_OPENING_RULE, spark_opening_rule,
                                        SPARK_SOURCES_LINE,
                                        TRANSFORM_NOTE, TRANSFORM_UNREADABLE,
                                        BEHIND_CLAUSE, MAP_PATHS_HEAD,
                                        NOTHING_BEHIND_CLAUSE, ORB_ORDER_NOTE,
                                        POTION_BARRED_NOTE,
                                        RESOLUTION_APPLIED,
                                        RESOLUTION_REMOVED,
                                        STOLEN_CARD_CLAUSE,
                                        TURN_ORDER_DUSK, TURN_ORDER_NOTE,
                                        TURN_ORDER_ORB,
                                        TURN_ORDER_PERFORMER,
                                        TURN_ORDER_POWER,
                                        UNBLOCKED_RAISER_CLAUSE,
                                        UNBLOCKED_RAISE_CLAUSE)
from understudy.blindplay_coop import banner as coop_banner
from understudy.blindplay_coop import render_lines as coop_lines
from understudy.blindplay_observe import observation
from understudy.blindplay_read import _fold, _text
from understudy.blindplay_shape import (BlindPlayError, FIGHT_OVERLAYS,
                                        opening_spark)


# ----------------------------------------------------------------- render --

#: Varka round 3 (2026-10-10): a Knight's hand row names its element. The
#: game prints the keyword "Knight." at the head of the rules box
#: (`KleeKeywords.Knight`, `AutoKeywordPosition.Before`).
_KNIGHT_HEAD = re.compile(r"^Knight\.")
KNIGHT_TAG = "Knight, {element}."
#: And while a relic forbids drawing on your turn (Fiddle: "You may not draw
#: cards during your turn"), a face that prints "Draw N" says so.
_NO_DRAW_RELIC = re.compile(r"\bmay not draw cards during your turn\b", re.I)
_DRAW_N = re.compile(r"\bdraw \d+\b", re.I)
NO_DRAW_CLAUSE = " (no draw: {relic})"


def _knight_tagged(c: dict[str, Any]) -> str:
    """The face's text, its leading "Knight." carrying the printed element."""
    text = str(c.get("text") or "")
    element = c.get("printed_element") or c.get("element")
    if element and _KNIGHT_HEAD.match(text):
        return KNIGHT_TAG.format(element=element) + text[len("Knight."):]
    return text


def _no_draw_relic(you: dict[str, Any]) -> str:
    """The held relic that forbids drawing on your turn, by name, or ""."""
    for relic in you.get("relics") or []:
        if _NO_DRAW_RELIC.search(str(relic.get("text") or "")):
            return str(relic.get("name") or "")
    return ""


def _no_draw_clause(c: dict[str, Any], relic: str) -> str:
    """`(no draw: Fiddle)` on a face that prints "Draw N"."""
    if relic and _DRAW_N.search(str(c.get("text") or "")):
        return NO_DRAW_CLAUSE.format(relic=relic)
    return ""


def _render_card(c: dict[str, Any], bullet: str = "-",
                 mark: str = "", raiser: dict[str, Any] | None = None,
                 no_draw: str = "") -> list[str]:
    """One card face. `mark` is a state the SCREEN is in about this row and
    not a fact about the card, so it goes at the END of the head, after the
    cost and the type -- the shape `EB-294` gave a picked bundle.

    `raiser` is `EB-752`'s held relic, or None: a rule that raises UNBLOCKED
    damage, which no damage face can fold and which therefore rides beside the
    number instead of inside it."""
    head = f"{bullet} **{c['title']}**"
    if c["upgraded"]:
        head += " (upgraded)"
    # The element INDICATOR's twin on this page: the card now carries a gem
    # rather than a sentence, and a gem does not cross a text wire. Beside the
    # title, in brackets, because that is where the card carries it -- next to
    # the type plaque, at a glance, before the rules. The keyword's own row
    # further down still carries the aura duration and the reaction rule; this
    # line is the glance, not the explanation.
    if c.get("element"):
        head += f" [{c['element']}]"
    # `EB-181`: the enchantment beside the title, where the game paints it and
    # where `(upgraded)` already sits -- the two facts a copy of a card can
    # differ by, on one line, so two copies of one title are told apart at a
    # glance instead of by a paragraph explaining that they cannot be.
    ench = c.get("enchantment")
    if ench:
        head += (f" ({ench['name']} {ench['amount']})" if ench.get("amount")
                 else f" ({ench['name']})")
    # `EB-286`: the COST SLOT as the game paints it, energy and Spark
    # together, through the one formatter the staged page already uses.
    # `qa_packet.cost_label` answers `-` when the wire sent no cost at all,
    # which is the case this line has always printed nothing for.
    price = qa_packet.cost_label(c)
    bits = [b for b in (f"cost {price}" if price != "-" else "",
                        c["kind"].lower() if c["kind"] else "") if b]
    # 2026-09-25 (opus-furina-l2b, (c) 2): a MODE row on a chooser prints no
    # cost and no type. "Deal 7 damage -- cost 0, skill" was the option card's
    # placeholder: the play's cost was paid when the card was played, and its
    # type is the card's, printed in the hand one screen earlier.
    if c.get("mode_face"):
        bits = []
    if bits:
        head += f" — {', '.join(bits)}"
    if mark:
        head += f" — {mark}"
    # `EB-752`: the held relic's term BESIDE the number, never inside it. The
    # face's sentence is the game's and is printed unchanged; the clause is
    # this page's and is appended after it, the way `_rider_clause` puts a
    # named source beside a carry-out's figure.
    out = [head, f"    {_knight_tagged(c) or '(no printed text)'}"
                 + _unblocked_raise_clause(c, raiser)
                 + _no_draw_clause(c, no_draw)]
    # 2026-09-28 (the Spend pass): a Spend mode the board cannot pay, under
    # the face that prints it. The game plays such a card's plain mode without
    # asking, so this line is the only place the refused mode shows.
    for line in c.get("spend_unavailable") or []:
        out.append(f"    {line}")
    # `EB-483`: on the Smith's grid, the face this card would print UPGRADED,
    # under the one it prints now. Absent on every other screen, and absent
    # here for a row this page cannot render without guessing -- see
    # `qa_packet.upgraded_face` for both bounds.
    # `EB-529`: and where it cannot be rendered, the REASON, because "no
    # `Upgraded:` line" and "no upgrade" are the same silence to a reader
    # deciding what to spend a Smith on.
    # `EB-667`: AND ONLY ONE UPGRADE LINE. Alice's Introduction Magic printed
    # both `Upgraded: not shown -- its upgrade changes nothing this face
    # prints.` and `Upgraded, and gains Retain.` on the Klee r24 lane-1 Smith,
    # which is one screen contradicting itself: the keyword line IS what the
    # upgrade does, so the note above it is false rather than merely silent.
    # The note is the "this page cannot tell you what it does" line, and a row
    # whose schema upgrade is a keyword has already told the reader.
    # `EB-700`: the face this card is WRITTEN with, above the upgrade line and
    # below the one the board is printing, because it is about the sentence
    # directly above it. Absent wherever the two agree, which is every card on
    # a board with nothing folding into it.
    if c.get("written_face"):
        out.append(f"    Written: {c['written_face']}")
        out.append("    (the line above this one is what the board is "
                   "printing now; this is the card's own written face, off "
                   "its sheet -- the difference is the board's.)")
    if c.get("upgraded_face"):
        # The upgraded copy's cost slot, in the head line's own words, where
        # the upgrade moves a Spark price ("cost 2 Sparks" above, "cost 1
        # Spark" here) -- the one change such an upgrade makes.
        cost = (f"cost {c['upgraded_cost']} — "
                if c.get("upgraded_cost") else "")
        out.append(f"    Upgraded: {cost}{c['upgraded_face']}")
    elif c.get("upgraded_note") and not c.get("upgraded_keywords"):
        out.append(f"    Upgraded: not shown -- {c['upgraded_note']}.")
    # `EB-551`: THE KEYWORD DELTAS, BESIDE THE NUMBER DELTAS. "Aria+ showed
    # only the number change and not Innate, the most load-bearing keyword in
    # the deck, chosen without being shown" (Furina r13 lane 1). Its own line
    # rather than a tail on the face's, because it is true whether or not the
    # face rendered -- a row this page cannot number still adds its keyword,
    # and that is often the whole of what a Smith pick turns on.
    if c.get("upgraded_keywords"):
        out.append("    Upgraded, and gains "
                   + ", ".join(c["upgraded_keywords"]) + ".")
    note = qa_packet.cost_note(c)
    if note:
        out.append(f"    {note}")
    # SEAT PAGE 3 (2026-10-05): a Guest Star's guest, under the face, as two
    # plain lines off its own hover tip (`ArmKeywordTips.For<Guest>`, the
    # badge's words). The face says only "Summon Lyney."; the tip was a gloss
    # the brief page cut once the lane had seen it, and seats passed four
    # guests they could not read.
    guest = _guest_tip(c)
    if guest is not None:
        out += _guest_lines(guest["text"])
    for k in c["keywords"]:
        if k is guest:
            continue
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
                   + (qa_packet.unplayable_reason(
                       c["unplayable_reason"], c.get("stars_have"),
                       c.get("star_cost"))
                      or "the game gives no reason"))
        # `EB-271`: and the clause that stops the vague one being vague, on
        # its own line under it, because it is this page's sentence and not
        # the game's.
        if c.get("unplayable_note"):
            out.append(f"    {c['unplayable_note']}")
    return out


#: A Guest Star card's title names its guest.
_GUEST_STAR_TITLE = re.compile(r"^Guest Star: (?P<who>\w+)")
#: The tip's two halves: the guest's standing line, then its act.
_GUEST_ACT_SPLIT = re.compile(r"\s*\bAct: ")


def _guest_tip(c: dict[str, Any]) -> dict[str, str] | None:
    """The keyword row that is this Guest Star's guest, or None."""
    hit = _GUEST_STAR_TITLE.match(str(c.get("title") or ""))
    if not hit:
        return None
    for k in c.get("keywords") or []:
        if k.get("name") == hit.group("who") and k.get("text"):
            return k
    return None


def _guest_lines(text: str) -> list[str]:
    """`Line: ...` and `Act: ...`, the tip's own two sentences."""
    parts = _GUEST_ACT_SPLIT.split(text.strip(), maxsplit=1)
    if len(parts) == 2 and parts[1]:
        out = [f"    Act: {parts[1].strip()}"]
        if parts[0].strip():
            out.insert(0, f"    Line: {parts[0].strip()}")
        return out
    return [f"    Guest: {text.strip()}"]


def _render_moved(said: dict[str, Any]) -> list[str]:
    """What the board did under one carried-out Plan (`EB-329`).

    ONE ENEMY PER LINE, the page's own `EB-198` contract: a morning against
    four Gardeners is four facts and joining them into a sentence is how the
    strip that preceded this section came to be unreadable. The verb is
    "lost", not "took damage", because the number is an HP DIFFERENCE and a
    Plan can move a bar through something that is not a hit.

    A Plan that moved no HP says so where the mod measured it, and says
    nothing where the mod could not -- `board_read` is the split, and it is
    what keeps this honest against a bridge older than the field.
    """
    if not said["board_read"]:
        return []
    if not said["moved"]:
        return ["    - no enemy lost HP"]
    return [f"    - {_moved_line(m)}" for m in said["moved"]]


def _moved_line(m: dict[str, Any]) -> str:
    """One body's share of one Plan, HP and Block (`EB-329`, `EB-440`).

    THE SILENCE THE r12 SEAT READ AS SUCCESS. `Kurage's Oath+` carried out into
    a Defend intent, HP went 35 to 35, the aura landed, and the receipt was
    "no enemy lost HP" -- true, and indistinguishable on the page from a Plan
    that did nothing at all. The Block the beat ate is now the line's own
    clause, so a morning spent on a shield reads as one.

    ABSENT IS NOT ZERO, `board_read`'s discipline one level down: a bridge that
    predates the measurement sends no `absorbed` key and prints exactly the
    line it always printed.
    """
    absorbed = m.get("absorbed") or 0
    if not m["amount"] and absorbed:
        return (f"{m['target']} lost no HP -- {absorbed} absorbed by Block"
                + (", and died" if m["dead"] else ""))
    line = f"{m['target']} lost {m['amount']} HP"
    if absorbed:
        line += f", and {absorbed} more absorbed by Block"
    return line + (", and died" if m["dead"] else "")


def _render_carry_out(pl: dict[str, Any]) -> list[str]:
    """The morning, and then the Plans that fired as they were written.

    `EB-329`. TWO HEADINGS, BECAUSE THEY ARE TWO MOMENTS. The r4c seat was
    told on one screen both that the jellyfish "carried these out at the start
    of this turn" and that the Plan in question was still planned; the first
    was simply not true of a resolution that happened mid-turn. Change of
    Plans is that door -- its own face says "carries out your front Plan NOW"
    -- so it is filed under a heading that says WHEN. It is the only such door
    since The Moon Overlooks the Waters was withdrawn (`EB-570`), and the
    heading is kept because the door is.
    """
    out: list[str] = []
    # `EB-654`. WHAT A SUMMON DID, FIRST, BECAUSE IT HAPPENED FIRST: a
    # Companion summon fires at the END of the player's turn, so its hit
    # landed before the enemy acted and before this turn's morning -- and it
    # landed after the last page the seat read, which is the whole reason
    # "Yae Miko's Sakura took 10 HP off an enemy" arrived on the next screen
    # as an unexplained change in a bar. Its own heading, because the
    # Bake-Kurage did not do it: the source names itself on the line.
    if pl.get("summon_hits"):
        out.append("- These fired at the end of your last turn, before the "
                   "enemies acted:")
        out += _carry_out_rows(pl["summon_hits"])
    # `EB-680`. A DUSK PLAN DID NOT HAPPEN THIS MORNING, so it is not filed
    # under the morning's heading.
    #
    # R265's Dusk lines are carried out at the END of the turn they are written
    # on, before the enemies act -- so by the time a seat reads this list they
    # are one turn and one enemy phase old, and the heading said "at the start
    # of this turn". Kokomi r27 lane 2: one Dusk Plan's timing printed three
    # ways at once, the card saying the end of this turn, the badge and the
    # queue saying the start of the next, and this heading saying the start of
    # THIS one. Two of the three are fixed at their source; this is the third.
    #
    # READ OFF THE MOD'S OWN MARK, which is `KokomiPlan.Entry.Title`'s "Dusk: "
    # prefix -- the same string the strip draws and the same one `Announce`
    # passes through as the carry-out's `card`. No new wire field, and a build
    # that predates the prefix files every row under the morning exactly as it
    # did.
    dusk = [row for row in pl["carried_out"] if _is_dusk(row)]
    morning = [row for row in pl["carried_out"] if not _is_dusk(row)]
    if dusk:
        out.append(f"- The {pl['pet_name']} carried these out at the END of "
                   "your last turn, before the enemies acted:")
        out += _carry_out_rows(dusk)
    if morning:
        out.append(f"- The {pl['pet_name']} carried these out at the "
                   "start of this turn, front first:")
        out += _carry_out_rows(morning)
    if pl["fired_now"]:
        out.append(f"- The {pl['pet_name']} carried these out THIS TURN, the "
                   "moment each was written, and not at the start of the "
                   "turn:")
        out += _carry_out_rows(pl["fired_now"])
    return out


#: `EB-680`. The mark `KokomiPlan.Entry.Title` puts on a Dusk entry, which is
#: the only place the wire says which timing an entry has. Case-sensitive and
#: anchored, because it is a prefix the mod writes and not a word a card face
#: might happen to use.
_DUSK_MARK = "Dusk: "


def _is_dusk(row: dict[str, Any]) -> bool:
    """Is this queued or carried-out Plan a DUSK entry? (`EB-680`)"""
    return str(row.get("card") or row.get("name") or "").startswith(_DUSK_MARK)


def _front_body(enemies: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The body a single-target Plan lands on, off the rows this page prints.

    `EB-773`. `PLAN_AIM_NOTE` is the rule and `blindplay_board.mark_front` is
    where it is already applied -- the leftmost living non-Minion, falling
    back to the leftmost living body where every one of them is a Minion. That
    reader sets `front` only where two or more are alive, because with one
    body there is no choice to get wrong; here a lone living body IS the
    answer, so the mark is asked first and the list second. Reading the
    PRINTED rows rather than the wire keeps this and the warning's own
    `target` naming the same body a reader can see.
    """
    alive = [e for e in enemies if isinstance(e.get("hp"), int)
             and e["hp"] > 0 and not e.get("phase_flip")]
    if not alive:
        return None
    return next((e for e in alive if e.get("front")), alive[0])


def _past_lethal_clauses(pl: dict[str, Any],
                         enemies: list[dict[str, Any]]) -> dict[int, str]:
    """`EB-773`: which queued Plans are written past the front body's life.

    THE RUNNING SUBTRACTION, over the queue in the order the jellyfish takes
    it. An entry earns the clause when the damage queued AHEAD of it already
    covers the front body's HP behind its Block -- which is the board the
    `EB-714` seat wrote a second 8 into, and the one nothing on this screen
    said anything about.

    ONLY `aim == "front"` COUNTS, on both sides of the comparison. A Plan whose
    face says ALL hits every living body and cannot be over-killed past the
    front one; a Plan Converging Tide has stamped is aimed by `CombatId` at a
    body this page cannot resolve, and says nothing rather than guessing; an
    entry with no damage clause adds nothing to the total and never earns the
    clause. A feed older than the fields sends `aim == ""` for everything and
    this returns an empty map -- the queue prints exactly as it always did.

    NEREID'S ASCENSION IS COUNTED, because `twice` is a fact about the next
    morning and not a forecast: the Rare carries out the FIRST entry twice, so
    its damage is doubled in the running total before the second entry is
    weighed. Nothing else in the queue changes.

    THE FIRST ENTRY NEVER EARNS IT -- nothing is queued ahead of it -- which is
    also why this is a warning about a QUEUE and not about a card.
    """
    body = _front_body(enemies)
    if body is None:
        return {}
    queue = pl.get("queue") or []
    out: dict[int, str] = {}
    ahead = 0
    for index, entry in enumerate(queue):
        if entry.get("aim") != "front":
            continue
        if ahead > 0 and body["hp"] <= max(0, ahead - (body.get("block") or 0)):
            block = (PLAN_PAST_LETHAL_BLOCK.format(block=body["block"])
                     if body.get("block") else "")
            out[index] = PLAN_PAST_LETHAL_CLAUSE.format(
                target=f"**{body['name']}**", hp=body["hp"], block=block,
                queued=ahead)
        damage = entry.get("damage") or 0
        ahead += damage * 2 if index == 0 and pl.get("twice") else damage
    return out


def _carry_out_rows(rows: list[dict[str, Any]]) -> list[str]:
    """One heading's worth of Plans, in the order the jellyfish took them.

    `EB-453` PUT THE UNRUN PLANS IN THE SAME LIST. A kill inside the first
    Plan of a morning unwinds the drain, so the rest never happen -- and the
    r13 seat, who had written two, was shown one and nothing about the other.
    They ride the same list because they were in the same queue and the ORDER
    is the fact: what the jellyfish did, and then where it stopped.
    """
    out: list[str] = []
    for said in rows:
        if said["unfinished"]:
            out.append(f"  - {said['card']} — still planned when the fight "
                       "ended, so it never happened.")
            continue
        out.append(
            f"  - {said['line']}{_kind_clause(said)}{_rider_clause(said)}")
        out += _render_moved(said)
    return out


def _rider_clause(said: dict[str, Any]) -> str:
    """What ELSE landed inside this Plan's beat, by name (`EB-453`).

    THE TWO NUMBERS THAT WOULD NOT ADD UP. The line's own figure is what the
    Plan's first clause produced and the lines under it are what the BOARD
    lost, measured across the whole beat -- so `War Council, 7 (the 7 is
    damage)` sat above `lost 9 HP` and the missing 2 was the Tamakushi Casket
    answering the Weak that same Plan had just applied. The page could not name
    it, because a subtraction has no sources; the mod names it at the line that
    deals it (`KokomiPlan.NoteRider`) and this prints the name.

    AND ON WHICH BODY (`EB-518`). Naming the source was not enough to make the
    beat add up, because a beat can strike ONE body twice: the r18 seat read
    "Tamakushi Casket 2, Tamakushi Casket 2, Tamakushi Casket 2" over bodies
    that had lost 1, 9 and 7, divided the three entries evenly, made every body
    5 + 2, and concluded a FOURTH strike had gone unlisted. It had not -- two
    of the three landed on the same body, because the Plan's own Hydro hit
    froze it before the hit landed and the relic answered the Frozen as well as
    the Weak. With the body named, each `lost N HP` line under this one is the
    Plan's own number plus its own riders, and the subtraction the seat had to
    do by hand is on the page.

    ABSENT IS NOT EMPTY, this section's standing rule, and it is why the target
    is a suffix rather than part of the format: a bridge with no `riders` key
    sends none and the row reads as it always did, and one that sends riders
    without the `EB-518` fields prints the source and the number alone.
    """
    riders = said.get("riders") or []
    if not riders:
        return ""
    named = ", ".join(f"{r['source']} {r['amount']}"
                      + (f" on {r['target']}" if r.get("target") else "")
                      for r in riders)
    return f" Inside the same beat: {named}."


def _kind_clause(said: dict[str, Any]) -> str:
    """What the figure on a carry-out line IS (`EB-426`).

    `Bake-Kurage: Cleansing Wave, 7` put a bare 7 in the slot every other line
    uses for damage and then said "no enemy lost HP". The 7 was BLOCK, cut from
    the clause's 10 by Frail, and the r11 seat derived both halves off the
    board. Neither is in the mod's sentence -- it is one string with one figure
    -- so the kind and the amount the clause asked for ride beside it and the
    page says them.

    THE MOD'S SENTENCE IS UNTOUCHED. It is printed as sent, and this is a
    clause AFTER it: one composer for the on-screen words, which is the whole
    argument for the `line` field, and the page adding what the wire now
    carries.

    EVERY KIND AND NOT ONLY BLOCK. "A bare number in the slot every other line
    uses for damage" is a complaint about a slot with no label, and labelling
    one kind would leave the slot exactly as ambiguous for the next reader --
    `Exposed Flank, 2` is two stacks of Vulnerable.

    THE ASKED-FOR HALF IS PRINTED ONLY WHERE IT DIFFERS, and it is not always
    smaller: a hit into Vulnerable lands above what its clause asked for. Which
    power moved it is not on the wire (`CreatureCmd.GainBlock` reports a landed
    amount and no attribution), so the page states the two numbers and leaves
    the screen's own status rows to name what sits between them.
    """
    if said["number"] is None or not said["kind"]:
        return ""
    clause = f" — the {said['number']} is {said['kind']}"
    if said["asked"] is not None and said["asked"] != said["number"]:
        clause += f"; the clause asked for {said['asked']}"
    return clause + "."


#: `EB-653`. The cap's own sentence, as `KokomiPlan.CapSentenceFormat` spells
#: it. Matched on the SENTENCE rather than on a power's name -- the discipline
#: `_PLAYS_YOUR_TURN` and `PLAN_CASKET_AURA_CLAUSE` already keep here -- so a
#: build that moves the clause onto another badge keeps the page honest, and a
#: build with no cap declared matches nothing and prints the note it always
#: printed.
_PLAN_CAP_SENTENCE = re.compile(
    r"carries out at most (\d+) at the start of your turn", re.I)


def _plan_count_note(you: dict[str, Any]) -> str:
    """The count rule the BUILD supports, read off the wire (`EB-653`).

    THE OLD NOTE ASSERTED A RULE THE LANE HAD TURNED OFF. "The number on the
    Plan badge is how many are written, NOT A LIMIT" was written under
    `EB-563`, when nothing in `KokomiPlan.cs` capped the queue; `EB-643` (R265)
    added `GITS_KOKOMI_PLAN_CAP`, and the r24 lane ran with it at 2. Four
    mornings carried out two of four written Plans while this page said there
    was no limit -- so the seat had a screen and a board that could not both be
    right, and read the rule as a wall.

    THE WIRE IS THE AUTHORITY, and it already carries the answer: the mod
    appends the cap's sentence to `ProtoBakeKuragePower`'s description when a
    cap is declared, and a power's description reaches the page as
    `powers[].text`. So this reads the sentence and prints the matching note;
    the number in the note is the mod's number and is never derived here.
    """
    for power in you.get("powers") or []:
        found = _PLAN_CAP_SENTENCE.search(str(power.get("text") or ""))
        if found:
            return PLAN_COUNT_CAPPED_NOTE.format(n=found.group(1))
    return PLAN_COUNT_NOTE


def _board_note_wanted(pl: dict[str, Any]) -> bool:
    """Is a board reading on this screen at all? (`EB-329`)

    The note explains the two numbers under a Plan, so it is printed where
    both are and nowhere else -- a bridge older than the measurement prints
    the lines it always printed and no footnote about numbers it does not
    carry. It goes at the END of the section rather than under the last Plan,
    where the indent made it read as a fact about that one card.
    """
    return any(said["board_read"]
               for said in pl["carried_out"] + pl["fired_now"]
               + (pl.get("summon_hits") or []))


#: A per-turn ALLOWANCE stated in a power's own sentence (`EB-467`). The
#: shipped shape is Hardened Shell's "cannot lose more than 20 HP each turn";
#: the alternatives are the same sentence's other spellings of "each turn",
#: which is the only clause that makes the number a per-turn budget rather
#: than a total.
_PER_TURN_CAP = re.compile(
    r"more than (\d+)\s+\S+ (?:each|per|every|a|in a single|in one) turn",
    re.IGNORECASE)

#: THE ALLOWANCE THAT COUNTS UP (the Klee full run on lane 1, 2026-09-26).
#: Sloth prints "You cannot play more than 3 cards each turn", and its badge is
#: `SlothPower.DisplayAmount`, which is `_cardsPlayedThisTurn` (decompiled) --
#: the cards already PLAYED, starting at 0. Hardened Shell's number is what is
#: LEFT. Both sentences match `_PER_TURN_CAP`, so the page printed "Sloth 3 of
#: 3 left this turn" after the third card, backwards. The verb is the tell: a
#: cap on what you PLAY is counted as you play.
_PLAYED_CAP = re.compile(r"\bplay more than \d+", re.IGNORECASE)


def _turn_allowance(power: dict[str, Any]) -> tuple[int, str] | None:
    """The cap a power's number is COUNTING DOWN AGAINST, or None. `EB-467`.

    THE DEFECT. "Hardened Shell 12 — Skulking Colony cannot lose more than 20
    HP each turn" is two numbers of two different kinds on one line, and every
    seat that met it read them as a contradiction: the r3 Klee seat watched the
    badge go 20 -> 0 -> 5 and worked out from its OWN damage that the number is
    what is LEFT this turn, "nothing on screen says so"; the Kokomi r15 seat
    filed the same line again (`(c)` 3).

    THE TEST IS THE POWER'S OWN SENTENCE, and it has to be, because the wire
    sends a power as `name`, `amount`, `type` and `description` and carries no
    maximum for one (`EB-181`'s finding, one rule over). So the cap is read out
    of the description the game itself printed, and only where that sentence
    states a PER-TURN allowance the amount fits inside. A power whose number
    has climbed past the sentence's number is not counting down against it --
    that is a different power wearing a similar sentence -- and gets the line
    it always had.

    RETURNS THE CAP AND WHICH WAY THE NUMBER RUNS: `"left"` for an allowance
    that counts down (Hardened Shell), `"played"` for one that counts the cards
    already played (Sloth, `_PLAYED_CAP`).
    """
    text = str(power.get("text") or "")
    found = _PER_TURN_CAP.search(text)
    if not found:
        return None
    cap = int(found.group(1))
    stacks = power.get("stacks")
    if not isinstance(stacks, int) or isinstance(stacks, bool):
        return None
    if not 0 <= stacks <= cap:
        return None
    return cap, ("played" if _PLAYED_CAP.search(text) else "left")


# `EB-525`. THE STEP THE SENTENCE DOES NOT SAY IT LEAVES OUT.
#
# THE FIND (Furina r12 lane 1, the elite). The Bygone Effigy wears "Slow N --
# Whenever you play a card, this enemy receives 10% more damage from Attacks
# this turn", and the seat played three cheap cards and then two attacks: "I
# predicted 27 damage and got 25. By the arithmetic, Soloist's+ resolved at
# Slow 30 (not 40) and Chevreuse at 40 (not 50) -- i.e. a card's own Slow
# increment does not apply to itself. The printed text does not say that."
#
# THE STACK ARRIVES AFTER THE CARD RESOLVES, which is the game's own trigger
# order and is invisible in a sentence written in the present tense: "whenever
# you play a card" is true of the card in your hand, and the number it hits
# with is the one that was on the board before it. Every Slow turn the seat's
# arithmetic was off by one step, and it read the difference as its own error
# twice before deriving the rule.
#
# A CLAUSE ON THE PAGE AND NOT A NEW SENTENCE, `_turn_allowance`'s shape one
# power over (`EB-467`): the wire sends a power as `name`, `amount`, `type` and
# `description`, so what the page can add is a clause about the sentence the
# game printed -- and it is added only where that sentence is the one the rule
# is about, so a future power wearing a similar name gets the line it always
# had.
_SLOW_TRIGGER = "whenever you play a card"
_SLOW_CLAUSE = " It counts the cards played BEFORE this one."


def _slow_clause(power: dict[str, Any]) -> str:
    """`EB-525`: the step Slow's own sentence leaves out, or ''."""
    if str(power.get("name") or "").strip().casefold() != "slow":
        return ""
    text = str(power.get("text") or "")
    return _SLOW_CLAUSE if _SLOW_TRIGGER in text.casefold() else ""


#: `EB-722`. A PLACER POWER, whose number is the SIZE of the charge it plants
#: and not how many stacks of it stand. Klee's arm has two -- `Witches' Circle`
#: and `Chained Reactions` -- and both print the same shape of sentence, so the
#: test is that sentence and never their names: a third placer worded the same
#: way gets the same label and a renamed one does not go silent, which is the
#: discipline `_turn_allowance` and `_PLAN_CAP_SENTENCE` already keep here.
_PLACED_CHARGE = re.compile(r"place a (Bomb|Mine)\s+(\d+)\b", re.IGNORECASE)


def _placed_charge(power: dict[str, Any]) -> str:
    """What this power's number IS, where it is a charge size. `EB-722`.

    THE DEFECT (Klee r25 lane 2, (c) 4). Every other numbered buff on that
    strip prints its own stack count, and `Witches' Circle 3 (buff)` and
    `Chained Reactions 3` name the SIZE each one places -- so a seat reading
    the strip cannot tell which kind of number it is looking at.

    THE ROW'S OWN DEFAULT WAS "print the number the face means", and that is
    what this does: the number stays and takes the noun the sentence beside it
    uses, `Witches' Circle: Bomb 3`. Dropping it was the fallback and is not
    needed -- the size is the one fact about this power a reader plans on.

    MATCHED ONLY WHERE THE TWO AGREE. A power whose stack count and whose
    printed size have come apart is not a placer wearing this shape -- it is a
    power that stacks AND places -- and it gets the line it always had.
    """
    found = _PLACED_CHARGE.search(str(power.get("text") or ""))
    if not found:
        return ""
    stacks = power.get("stacks")
    if not isinstance(stacks, int) or isinstance(stacks, bool):
        return ""
    return found.group(1).title() if int(found.group(2)) == stacks else ""


#: `EB-721`. The amplifying reaction a power's own sentence says is folded into
#: the number it prints. `ProtoBombPower`'s face writes it as a clause on the
#: total -- " with Vaporize", " with Melt" -- in the same place and the same
#: shape as `after Vulnerable` and `capped by Hard To Kill`, so the pattern is
#: that clause and not the badge's name.
_FOLDED_REACTION = re.compile(
    r"\bdeals? [^.]*?\bwith (Vaporize|Melt)\b", re.IGNORECASE)


def _folded_reaction(power: dict[str, Any]) -> str:
    """The header's label where a reaction is inside its number. `EB-721`.

    THE DEFECT (Klee r25 lane 2, (c) 2). "`Bomb 18 ... sizes, oldest first:
    12` is one 12-size Bomb standing against a Hydro aura for a Vaporize. Both
    numbers are honest; they are adjacent and disagree." `EB-559` folded the
    pending amplifier into the printed total, and until `EB-721` no surface
    named it -- so the header and the raw list beside it could not be
    reconciled without knowing a rule neither of them stated.

    THE ROW'S PICK WAS THE LABEL, not folding the multiplier into both numbers:
    the sizes list is the QUEUE, and multiplying every entry by a bonus only
    the leading charge collects would make three of four figures false to buy
    one agreement.

    OFF THE SENTENCE AND NEVER OFF THE NAME, `_turn_allowance`'s discipline, so
    a second badge that folds an amplifier in gets the same label the day its
    face says so.
    """
    found = _FOLDED_REACTION.search(str(power.get("text") or ""))
    return f", with {found.group(1).title()}" if found else ""


def _bomb_header(power: dict[str, Any]) -> str:
    """A Bomb badge's header where its number is not the size of the pile.

    THE FIND (the Klee later-act seats, 2026-09-26: act-2 lanes 1 and 4, act-3
    lane 2, and the lane-2 full run). "`Bomb 19` ... `Bombs here, oldest
    first: 13` -- the headline includes Vulnerable, and nothing on the line
    says so"; the same under Hard To Kill (`Bomb 9` over a 15) and on a Mine
    pile. The badge's number is `ProtoBombPower.DisplayAmount`, what a Set off
    DEALS into this body (`EB-270`); the list beside it is the SIZES. `EB-721`
    labelled one term folded into it (the reaction) and left the target's
    Vulnerable and cap unnamed.

    THE LABEL, NOT A NEW NUMBER. Both figures are the game's and both stay:
    the header says the badge's figure is what a Set off deals and names the
    pile's size beside it. Only where the two differ -- a pile whose number IS
    its size reads exactly as it always did.

    `''` where the sentence carries no forecast or no sizes, which is every
    power that is not a Bomb pile.
    """
    text = str(power.get("text") or "")
    stacks = power.get("stacks")
    if not isinstance(stacks, int) or isinstance(stacks, bool):
        return ""
    sizes = _BOMB_SIZES.search(text)
    if not _BOMB_FORECAST.search(text) or not sizes:
        return ""
    charges = _bomb_charge_sizes(sizes.group(1))
    if not charges or sum(charges) == stacks:
        return ""
    reaction = _FOLDED_REACTION.search(text)
    folded = f" with {reaction.group(1).title()}" if reaction else ""
    return f"{power['name']}: deals {stacks}{folded} (sizes {sum(charges)})"


def _spark_sources_line(combat: dict[str, Any]) -> str:
    """`EB-610`'s sub-line, in one place because two rows now print it.

    Spark reaches the page in two shapes -- a METER row on a build that sends
    `combat["meters"]`, and a POWER row (`Spark 3 (buff)`) on a build that
    does not -- and the sentence saying where this turn's Sparks came from is
    the same sentence under either. Assembling it twice is how the power
    shape came to print nothing at all.
    """
    return SPARK_SOURCES_LINE.format(
        sources=", ".join(f"+{s['amount']} {s['name']}"
                          for s in combat["spark_sources"]))


#: 2026-09-26 (control seat, Ironclad): "the hand printed 'Deal 3 damage
#: twice'; it folded my own Shrink in but not the target's Vulnerable, and the
#: hits landed 5 and 5." A card's face is worked out with no target
#: (`SafeGetCardDescription`), so no power on an enemy is in it, and the wire
#: carries no per-target figure. Said on the enemy's Vulnerable line.
PREVIEW_LEAVES_OUT_CLAUSE = (" The damage printed on your cards does not "
                             "count this; it is added when a hit lands here.")


def _preview_leaves_out(power: dict[str, Any],
                        hand: list[dict[str, Any]]) -> str:
    """The clause on an enemy's Vulnerable row, while a hand is shown."""
    if not hand or _fold(power.get("name")) != "vulnerable":
        return ""
    return PREVIEW_LEAVES_OUT_CLAUSE


#: 2026-09-26 (control seat, Silent): "Tea of Discourtesy kept saying 'next
#: combat' after it had fired." Beside the name, where the game greys it out.
RELIC_USED_UP = " (used up: it has done its job and does nothing more)"


#: The Furina full-run round (2026-10-10): the game sometimes lists one
#: power twice on a creature ("Weak 1" twice, "Crab Rage" twice). The page
#: prints it once and says so.
POWER_LISTED_TWICE_CLAUSE = " (the game lists this twice)"


def _once(powers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The powers with a second row of the same name and amount folded
    into the first, which carries `listed_twice`."""
    out: list[dict[str, Any]] = []
    seen: dict[tuple[Any, Any], dict[str, Any]] = {}
    for pw in powers:
        key = (pw.get("name"), pw.get("stacks"))
        if key in seen:
            seen[key]["listed_twice"] = True
            continue
        row = dict(pw)
        seen[key] = row
        out.append(row)
    return out


def _render_power(power: dict[str, Any], indent: str) -> str:
    """One power: printed name, the amount, buff or debuff, the printed text.

    `EB-467`: where the amount is an allowance counting down against a cap the
    power's own sentence states, the two numbers print in ONE clause -- "12 of
    20 left this turn" -- instead of standing apart and contradicting.

    `EB-525`: and where the sentence describes a stack that arrives after the
    card that adds it has already resolved, the page says which cards the
    number counts.

    `EB-722`: and where the number is the SIZE of a charge the power plants
    rather than a count of itself, the noun rides beside it.

    `EB-721`: and where the number has an amplifying reaction folded into it
    that the raw figures beside it do not, the header says which.

    2026-09-26: and where a Bomb badge's number is what a Set off deals rather
    than the pile's size, the header says so and names the size
    (`_bomb_header`); a per-turn cap that counts cards PLAYED says "played".
    """
    cap = _turn_allowance(power)
    placed = _placed_charge(power)
    bomb = _bomb_header(power)
    if cap is not None:
        line = f"{indent}{power['name']} {power['stacks']} of {cap[0]} " \
               f"{cap[1]} this turn"
    elif bomb:
        line = f"{indent}{bomb}"
    elif placed:
        line = f"{indent}{power['name']}: {placed} {power['stacks']}"
    elif power.get("numbered") is False:
        # A `Single` power: the game draws no number on its icon (2026-09-25).
        line = f"{indent}{power['name']}"
    else:
        line = f"{indent}{power['name']} {power['stacks']}{_folded_reaction(power)}"
    kind = str(power.get("kind") or "").strip().lower()
    if kind:
        line += f" ({kind})"
    if power["text"]:
        line += (f" — {power['text']}{_slow_clause(power)}"
                 f"{_every_n_cards_clause(power)}")
    # 2026-09-26 (control seats): what the power holds and never prints.
    if power.get("stolen_card"):
        line += STOLEN_CARD_CLAUSE.format(card=power["stolen_card"])
    if "behind" in power:
        line += (BEHIND_CLAUSE.format(names=_and_list(
                     [f"**{n}**" for n in power["behind"]]))
                 if power["behind"] else NOTHING_BEHIND_CLAUSE)
    if power.get("listed_twice"):
        line += POWER_LISTED_TWICE_CLAUSE
    return line


#: 2026-09-26 (the Furina full run on lane 1, Aeonglass): "Withering
#: Presence: 'Every 6 cards you play, add a Wither'. On T1 I held back to 5
#: cards to dodge it. The counter carries across turns ... nothing on screen
#: says so." The badge is `WitheringPresencePower.DisplayAmount`, its
#: `CardsLeft` var (decompiled): the cards left before the next one, which
#: only a card play moves. Read off the power's own sentence, never its name.
_EVERY_N_CARDS = re.compile(r"\bevery (\d+) cards you play\b", re.IGNORECASE)
_EVERY_N_CARDS_CLAUSE = (" The number is the cards left before the next one, "
                         "and it carries over from turn to turn.")


def _every_n_cards_clause(power: dict[str, Any]) -> str:
    """The count an "every N cards you play" power keeps, or ''."""
    text = str(power.get("text") or "")
    found = _EVERY_N_CARDS.search(text)
    stacks = power.get("stacks")
    if (not found or not isinstance(stacks, int) or isinstance(stacks, bool)
            or not 0 < stacks <= int(found.group(1))):
        return ""
    return _EVERY_N_CARDS_CLAUSE


# `EB-349`. The three sentences the page reads a rule out of, each the printed
# words of a thing already on the screen: a relic that takes a turn, a status
# that adds damage to every hit, and a power that pays for one card. Matched on
# the sentence and never on a name, so a second relic, debuff or power worded
# the same way gets the same line and a renamed one does not go silent.
_PLAYS_YOUR_TURN = re.compile(r"plays your (?:\w+ )?turn for you", re.I)
_PER_HIT_DAMAGE = re.compile(r"additional damage from attacks", re.I)
# `EB-408`. The flat term on the PLAYER's own Attacks, which is a different
# sentence from the debuff above and belongs to a different note: Fantastic
# Voyage prints "Your Attacks deal 5 additional damage this turn." The figure
# between the two halves is the game's own hole and reaches this list with its
# `[blue]` markup still on it (`qa_packet._powers` copies the description as
# sent), so the pattern steps over whatever sits between them rather than
# spelling a number it would then have to un-tag.
_ATTACK_DAMAGE_BUFF = re.compile(
    r"your attacks deal[^.]*additional damage", re.I)
_MULTI_HIT_LABEL = re.compile(r"^\s*(\d+)\s*[x×]\s*(\d+)\s*$")
_ONE_USE_DISCOUNT = re.compile(r"the next (\w+) you play costs", re.I)
# `EB-669`. The same sentence with any other consequence -- Battle Plan's "the
# next Attack you play face-up this turn deals 4 additional damage". Asked
# SECOND, so a price keeps the note written for a price.
# 2026-09-26 (control seat, Necrobinder): and Vigor's "Your next Attack
# deals 8 additional damage" (Akabeko), which every Attack in hand previews.
_ONE_USE_RIDER = re.compile(
    r"the next (\w+) you play\b|\byour next (\w+) deals\b", re.I)
#: 2026-09-26 (control seat, Necrobinder): Pen Nib's "Every 10th Attack you
#: play deals double damage", a relic's one-card rider.
_EVERY_NTH_PLAY = re.compile(
    r"\bevery (\d+)(?:st|nd|rd|th) (\w+) you play[^.]*", re.I)
# `EB-433`. A relic that answers a debuff with an elemental hit, which is what
# makes the panel's "leaves no aura" clause false for a debuff Plan. The
# Tamakushi Casket's own sentence, with the element left open: the clause is
# about a hit that carries one, and the Plan is Hydro either way.
#
# `EB-348` REWROTE THAT SENTENCE ("Each debuff you apply lands a real 6 Hydro
# hit on that enemy"), so the pattern follows it. Both spellings are matched
# rather than only the current one: the gate is on a relic a RUN is holding,
# the old wording is what a save from before the rewrite carries, and a clause
# that silently stopped printing is exactly the defect `EB-433` was filed on.
_DEBUFF_ANSWERING_HIT = re.compile(
    r"(?:whenever|each) (?:you apply a debuff|debuff you apply)[^.]*"
    r"(?:damage|hit)", re.I)

# `EB-752`. A RELIC THAT RAISES UNBLOCKED DAMAGE -- The Boot's sentence with
# its two numbers left open. Matched on the SENTENCE and never on a name,
# `_PLAYS_YOUR_TURN`'s discipline: a second relic worded the same way gets the
# same clause and a renamed one does not go silent.
#
# TWO PATTERNS BECAUSE THERE ARE TWO ANSWERS. The first is the rule's whole
# shape ("deal 4 or less unblocked attack damage ... increase it to 5"), which
# hands the page an arithmetic it can actually do; the second is the bare
# topic, so a relic that raises unblocked damage in some other wording is
# still NAMED beside the number rather than vanishing from the page.
_UNBLOCKED_RAISE = re.compile(
    r"\b(\d+)\s*or less unblocked attack damage[^.]*?increase it to\s*(\d+)",
    re.I)
_UNBLOCKED_TOPIC = re.compile(r"unblocked attack damage", re.I)
#: The printed damage on a face, which is the number the clause is about.
_DEAL_DAMAGE = re.compile(r"\bdeal\s+(\d+)\b", re.I)


def _unblocked_raiser(you: dict[str, Any]) -> dict[str, Any] | None:
    """`EB-752`: the held relic whose rule no damage face can carry.

    THE FIND (Klee r27, lanes 2 and cook). "Ka-pow! printed Deal 4 while The
    Boot made it 5", and on a Weak turn the printed numbers under-counted in
    the direction that makes a seat UNDER-play. The first reading was that the
    face's calculator was wrong; `EB-328` settled that it is not. The Boot is
    a `ModifyHpLostAfterOstyLate` hook -- it runs after the target's Block has
    been taken out of the hit -- and a card in hand has no target, no Block
    and therefore no honest way to fold it. So the number stays the game's and
    the modifier is printed BESIDE it.

    `low` / `high` ARE THE RELIC'S OWN NUMBERS where its sentence spells them,
    and None where it does not. The page does no arithmetic it cannot source
    off the feed: with them it says how much this face gains, without them it
    names the relic and says the rule is not in the number.
    """
    for relic in you.get("relics") or []:
        text = str(relic.get("text") or "")
        if not _UNBLOCKED_TOPIC.search(text):
            continue
        found = _UNBLOCKED_RAISE.search(text)
        return {"name": relic["name"],
                "low": int(found.group(1)) if found else None,
                "high": int(found.group(2)) if found else None}
    return None


def _unblocked_raise_clause(c: dict[str, Any],
                            raiser: dict[str, Any] | None) -> str:
    """`EB-752`: what that relic adds to THIS face, beside its number.

    BOTH HALVES ON THIS SCREEN, `_attack_buff_note`'s rule: the relic is held
    and this card is an Attack printing a damage figure. A Skill, a Power and
    an Attack that prints no number raise no question and get no clause.

    "ON AN UNBLOCKED HIT" IS THE WHOLE CONDITION and it is said every time,
    because it is the half a seat cannot see: the hit that lands into Block
    gets nothing, and a page that printed a flat `+1` would be wrong on every
    such hit. Where the relic's sentence gives its numbers, a face already
    above the threshold gains nothing and says nothing.
    """
    if not raiser:
        return ""
    if str(c.get("kind") or "").strip().casefold() != "attack":
        return ""
    found = _DEAL_DAMAGE.search(str(c.get("text") or ""))
    if not found:
        return ""
    name = f"**{raiser['name']}**"
    if raiser["low"] is None:
        return UNBLOCKED_RAISER_CLAUSE.format(relic=name)
    printed = int(found.group(1))
    if printed > raiser["low"] or raiser["high"] <= printed:
        return ""
    return UNBLOCKED_RAISE_CLAUSE.format(n=raiser["high"] - printed,
                                         relic=name)


def _auto_turn_note(you: dict[str, Any], round_: Any) -> list[str]:
    """`EB-349`: the turn a relic played, named on the turn it played it.

    Round one only, which is the turn the relic's own sentence is about, and
    off the relic row this page already prints. The ledger itself is the
    bridge's -- there is no record of a card resolving anywhere on the feed.
    """
    if round_ != 1:
        return []
    for relic in you.get("relics") or []:
        if _PLAYS_YOUR_TURN.search(str(relic.get("text") or "")):
            return ["", AUTO_TURN_NOTE.format(relic=f"**{relic['name']}**")]
    return []


def _per_hit_note(you: dict[str, Any],
                  enemies: list[dict[str, Any]]) -> list[str]:
    """`EB-349`: a per-hit modifier netted against a multi-hit icon.

    Fires only where both halves are on this screen -- a status of the
    player's whose printed rule is per-hit damage from Attacks, and an icon
    figure of the shape `AxB` -- and prints both readings of that icon. The
    first such pair on the board carries the note; it is one rule about the
    board and not a line per enemy.
    """
    hit = next((p for p in you.get("powers") or []
                if _PER_HIT_DAMAGE.search(str(p.get("text") or ""))
                and isinstance(p.get("stacks"), int)), None)
    if not hit:
        return []
    for enemy in enemies:
        for intent in enemy.get("intents") or []:
            found = _MULTI_HIT_LABEL.match(str(intent.get("label") or ""))
            if not found:
                continue
            each, hits = int(found.group(1)), int(found.group(2))
            return ["", PER_HIT_NOTE.format(
                name=hit["name"], n=hit["stacks"],
                label=str(intent["label"]).strip(), hits=hits,
                low=each * hits, high=(each + hit["stacks"]) * hits)]
    return []


# `EB-605`. The two number groups on a Bomb badge, each matched on the badge's
# own words rather than on the power's name: the headline forecast names the
# element it would deal, and the list of charge sizes is its own clause.
_BOMB_FORECAST = re.compile(
    r"set off here deals[^.]*?(Pyro|Hydro|Electro|Cryo)", re.I)
#
# `EB-755` WIDENED THE SIZES CLAUSE TWICE OVER, and the first widening is a
# defect this row found rather than one it set out to fix: the live face reads
# `Bomb sizes here, OLDEST FIRST: ...` (`ProtoBombPower.Bombs`, since `EB-432`
# put the order on the badge) and this pattern demanded the colon immediately
# after `here`, so on the real badge it matched NOTHING and the note it gates
# has been silent in the game while its fixture -- which spelled the clause
# without the qualifier -- went on passing. The qualifier is now skipped
# wherever it appears.
#
# AND THE CAPTURE ADMITS THE ORDINALS. The list is `1st 12 / 2nd 8` from this
# row on, so the class can no longer be digits and slashes; it runs to the
# clause's own comma instead, which is what kept `including {Mines} Mines` and
# `growing each turn` out of the numbers before and still does.
#
# AND THE TEXT PASS OF 2026-09-25 RENAMED THE CLAUSE, the `EB-755` drift once
# more: `ProtoBombPower.Bombs` now reads `Bombs here, oldest first: ...`, so
# the pattern demanding `bomb sizes here` matched nothing on the live badge and
# the note below went silent while its fixtures -- still spelling the old
# clause -- passed. Four seats on 2026-09-26 then read `Bomb 19` over a `13`
# with nothing between them. Both spellings are matched -- the new one only
# with its `oldest first` qualifier, because a still older face printed
# `Bombs here: {Count}`, a COUNT of charges and not their sizes.
_BOMB_SIZES = re.compile(
    r"(?:bomb sizes here[^:.]*|bombs here, oldest first):\s*([^,.]+)", re.I)

# One charge per `/`-separated item, and the size is the LAST number in it:
# `1st 12` is the twelfth-size charge in first position, not a charge of 1 and
# a charge of 12 (`EB-755`).


def _bomb_charge_sizes(clause: str) -> list[int]:
    """The charge sizes in a Bomb badge's sizes clause, in set-off order."""
    out: list[int] = []
    for item in clause.split("/"):
        found = _NUMBER.findall(item)
        if found:
            out.append(int(found[-1]))
    return out



def _bomb_forecast_note(power: dict[str, Any],
                        others: list[dict[str, Any]],
                        indent: str) -> list[str]:
    """`EB-605`: which of a Bomb badge's two number groups is which.

    ONLY WHERE THEY DISAGREE, which is the row's own acceptance: a lone Bomb 6
    prints 6 everywhere on its line and has nothing to explain. The page claims
    neither figure and computes neither -- both are the game's, printed
    unchanged -- it says what each one is, and where the body is wearing an
    aura the pile's element reacts with, it names the reaction the seat had to
    infer from a Spark counter.
    """
    text = str(power.get("text") or "")
    forecast, sizes = _BOMB_FORECAST.search(text), _BOMB_SIZES.search(text)
    if not forecast or not sizes or not isinstance(power.get("stacks"), int):
        return []
    charges = _bomb_charge_sizes(sizes.group(1))
    total = sum(charges)
    if not charges or total == power["stacks"]:
        return []
    element = forecast.group(1).capitalize()
    line = BOMB_FORECAST_NOTE.format(n=power["stacks"], total=total)
    aura = next((_AURA_NAME_RE.match(str(row.get("name") or "").strip())
                 for row in others
                 if str(row.get("kind") or "").strip().lower() == "aura"
                 and _AURA_NAME_RE.match(str(row.get("name") or "").strip())),
                None)
    if aura:
        pair = frozenset({element, aura.group(1)})
        named = next((word for word, elements in REACTION_ELEMENTS.items()
                      if elements == pair), "")
        if named:
            line = line.rstrip("*") + BOMB_REACTION_CLAUSE.format(
                aura=aura.group(1), element=element, reaction=named) + "*"
    return [indent + line]


def _casket_aura_clause(you: dict[str, Any]) -> str:
    """`EB-433`: the exception a held relic makes to the panel's aura rule.

    THE CLAUSE IS FALSE WITHOUT IT AND FALSE WITHOUT THE RELIC, which is why it
    is gated and not printed flat: "A Plan that blocks, draws or applies a
    debuff leaves no aura" is true of the PLAN and was wrong about the board,
    because the Tamakushi Casket answers the debuff with a Hydro hit of its own
    and that hit lays the aura. A run that is not holding it reads the short
    rule, which is then true.

    Matched on the relic's own sentence rather than its name, `_PLAYS_YOUR_TURN`'s
    discipline: a second relic that answers a debuff with an elemental hit says
    the same thing, and a renamed one does not go silent. `""` where no relic
    on the feed says it, which is every board the clause would be noise on.
    """
    for relic in you.get("relics") or []:
        if _DEBUFF_ANSWERING_HIT.search(str(relic.get("text") or "")):
            return PLAN_CASKET_AURA_CLAUSE.format(
                relic=f"**{relic['name']}**")
    return ""


#: The Tamakushi Casket's own clause, "... adds 1 to the Casket." Matched on
#: the relic's words, `_casket_aura_clause`'s discipline, not on its name.
_CASKET_COUNT_TEXT = re.compile(r"\bto the Casket\b", re.IGNORECASE)


def _casket_count_line(you: dict[str, Any]) -> list[str]:
    """`- Casket: N`, the count on the Tamakushi Casket's icon (2026-09-28).

    The count is the relic's `counter` off the wire (`ShowCounter` /
    `DisplayAmount`, `TamakushiCasket.cs`), the number the game draws on the
    icon. Printed beside the Bake-Kurage because that is where a reader
    deciding when to open the Casket is looking. `[]` with no such relic or
    no counter on it (out of combat the icon draws none).
    """
    for relic in you.get("relics") or []:
        counter = str(relic.get("counter") or "").strip()
        if counter and _CASKET_COUNT_TEXT.search(str(relic.get("text") or "")):
            return [f"- Casket: {counter}"]
    return []


def _one_use_discount_note(you: dict[str, Any]) -> list[str]:
    """A rider the game folds into every row and pays out once.

    `EB-349` filed the PRICE half (Mika: "the next Skill you play costs 0")
    and `EB-669` the other one (Battle Plan: "the next Attack you play ...
    deals 4 additional damage"). One sentence shape, two consequences -- a
    price goes back up on the rest of the hand, a rider is simply not on them
    -- so the price is asked first and keeps its own words, and every other
    one-use rider takes the general note.

    ONE LINE FOR THE HAND, never a line per card, which is `_attack_buff_note`'s
    rule beside it: the fact is about the power and the hand is where it is
    being misread.
    """
    for power in you.get("powers") or []:
        text = str(power.get("text") or "")
        found = _ONE_USE_DISCOUNT.search(text)
        if found:
            return ["", ONE_USE_DISCOUNT_NOTE.format(
                power=f"**{power['name']}**", kind=found.group(1))]
        found = _ONE_USE_RIDER.search(text)
        if found:
            return ["", ONE_USE_RIDER_NOTE.format(
                power=f"**{power['name']}**",
                kind=found.group(1) or found.group(2),
                words=found.group(0)[:1].lower() + found.group(0)[1:])]
    # 2026-09-26 (control seat, Necrobinder): Pen Nib at 9 doubled the number
    # on every Attack in hand, and only the next one played gets it
    # (`PenNib.ModifyDamageMultiplicative` doubles any Attack not yet played
    # while `AttacksPlayed == 9`). A relic whose counter is one short of its
    # own "every Nth" gets the same ONE-card note.
    for relic in you.get("relics") or []:
        found = _EVERY_NTH_PLAY.search(str(relic.get("text") or ""))
        counter = str(relic.get("counter") or "").strip()
        if (found and counter.isdigit()
                and int(counter) == int(found.group(1)) - 1):
            return ["", ONE_USE_RIDER_NOTE.format(
                power=f"**{relic['name']}**", kind=found.group(2),
                words=found.group(0)[:1].lower() + found.group(0)[1:])]
    return []


_NUMBER = re.compile(r"\d+")


#: 2026-10-04 (Klee lane 2, 2026-10-02): Tuning Fork printed "(7)" and nothing
#: said 7 of what. A relic counter that counts toward a threshold prints it.
#: The relic's own sentence names the threshold where it can ("Every time you
#: play 10 Skills", "Every 10th Attack", "Every 3 turns"); the table is for a
#: relic whose sentence a feed sends without it, keyed by printed title.
_RELIC_THRESHOLD_TEXT = re.compile(
    r"\bevery (?:time you \w+ )?(\d+)(?:st|nd|rd|th)?\b", re.I)
RELIC_THRESHOLDS = {"Tuning Fork": 10}


def _relic_counter(relic: dict[str, Any]) -> str:
    """A relic's counter as its icon's number, with "of N" where the relic
    counts toward N and the counter is a plain count below it."""
    counter = str(relic.get("counter") or "").strip()
    if not counter.isdigit():
        return counter
    found = _RELIC_THRESHOLD_TEXT.search(str(relic.get("text") or ""))
    threshold = (int(found.group(1)) if found
                 else RELIC_THRESHOLDS.get(str(relic.get("name") or "")))
    if threshold and int(counter) < threshold:
        return f"{counter} of {threshold}"
    return counter


def _attack_buff_note(you: dict[str, Any],
                      hand: list[dict[str, Any]]) -> list[str]:
    """`EB-408`: a flat Attack buff beside the faces it may or may not be in.

    BOTH HALVES ON THIS SCREEN, `_per_hit_note`'s rule: a status of the
    player's whose printed sentence says its number is additional damage on
    Attacks, and an Attack in hand printing a number of its own. The first such
    status carries the note; it is one rule about the hand and not a line per
    card. A hand with no Attack in it, or one whose Attacks print no figure,
    raises no question and gets no line.
    """
    buff = next((p for p in you.get("powers") or []
                 if _ATTACK_DAMAGE_BUFF.search(str(p.get("text") or ""))
                 and isinstance(p.get("stacks"), int)), None)
    if not buff:
        return []
    if not any(str(card.get("kind") or "").strip().casefold() == "attack"
               and _NUMBER.search(str(card.get("text") or ""))
               for card in hand):
        return []
    return ["", ATTACK_BUFF_NOTE.format(name=f"**{buff['name']}**",
                                        n=buff["stacks"])]


def _numbers_disagree(intent: dict[str, Any]) -> bool:
    """`EB-607`: does the hover sentence's number contradict the icon's?

    Only where BOTH fields carry a number and they share none: `6x3` beside
    "Attack 3 times" agrees on the 3 and says nothing, and a sentence with no
    number at all -- which is most of them -- is not a disagreement. The page
    reports the pair; it does not pick between them or do arithmetic to
    reconcile them, because it has no third field to check either against.
    """
    on_icon = set(_NUMBER.findall(str(intent.get("label") or "")))
    in_words = set(_NUMBER.findall(str(intent.get("text") or "")))
    return bool(on_icon and in_words and not (on_icon & in_words))


#: Seat page 5 (2026-10-05): the game's generic hover sentences. Each says
#: only the kind and the icon's number, which the line already carries, so
#: one of these whose every number is on the icon is not printed. Anything
#: else the game writes (`gain 8 Block`, `add 4 Burn to your hand`, `apply
#: Afflictions`) is kept, and so is any sentence whose number is not the
#: icon's (`EB-607`'s disagreement).
_GENERIC_HOVER = re.compile(
    r"^This enemy intends to (?:"
    r"Attack(?: for \d+(?: damage)?)?(?: \d+ times)?"
    r"|attack"
    r"|use a Buff|buff itself"
    r"|apply a Debuff(?: to you)?"
    r"|give you \d+ Status cards?"
    r"|Block on its turn"
    r")\.?$")


def _hover_adds_nothing(intent: dict[str, Any]) -> bool:
    """Seat page 5: is the hover sentence the game's generic template with
    no number the icon does not already show?"""
    text = str(intent.get("text") or "").strip()
    if not _GENERIC_HOVER.match(text):
        return False
    in_words = set(_NUMBER.findall(text))
    on_icon = set(_NUMBER.findall(str(intent.get("label") or "")))
    return in_words <= on_icon


def _intent_target_note(enemies: list[dict[str, Any]],
                        coop: bool = False) -> list[str]:
    """Seat page 5 (2026-10-05): `EB-323`'s missing target, said once under
    the enemy list on every page where more than one body could be meant --
    two or more enemies, or co-op -- instead of on every intent line. Not a
    once-per-lane gloss: seats cut pages with `sed`, and once-only text is
    what a slice loses."""
    if len(enemies) < 2 and not coop:
        return []
    if not any(i.get("target_side") or _fold(i.get("type")) == "buff"
               for e in enemies for i in e.get("intents") or []):
        return []
    return ["", INTENT_TARGET_NOTE]


def _intent_source_note(enemies: list[dict[str, Any]]) -> list[str]:
    """`EB-607`: where an icon number comes from, said where Strength is up.

    Printed only on a board that raises the question -- an enemy wearing
    Strength and telegraphing an Attack -- because on every other board the
    provenance of a number nobody is checking against a modifier is furniture.
    Keyed on the power's printed name, which is the row this page prints and
    the word the reader is reading it against.

    `EB-779`: AND THE CLOSING SENTENCE IS CHOSEN OFF THIS BOARD. The clause
    saying the feed carries no base, no modifier list and no breakdown was
    true when it was written and `EB-607`'s bridge half made it false, so on
    the very page that printed *"the game folded Strength into that: it is 12
    on the move and 15 after"* the footnote denied all three. It is now
    conditional on the breakdown having actually arrived on an intent of this
    board -- a bridge older than `EB-607` sends none and reads as before.
    """
    for enemy in enemies:
        if not any(_fold(p.get("name")) == "strength"
                   for p in enemy.get("powers") or []):
            continue
        intents = enemy.get("intents") or []
        if any(_fold(i.get("type")) == "attack" or i.get("label")
               for i in intents):
            if any(_breakdown_clauses(i.get("breakdown") or {})
                   for i in intents):
                return ["", INTENT_SOURCE_NOTE_BREAKDOWN]
            return ["", INTENT_SOURCE_NOTE]
    return []


# `EB-706`. THE INTENT NUMBER FOLDED WEAK ON SOME SCREENS AND NOT OTHERS.
#
# THE FIND. "r31 lane 1 read 11 and took 8, then read 6 under Weak 2 and took
# 6; r27 lane 2 saw 7 re-print to 5. The number a seat plans Block against
# cannot be trusted."
#
# AND THE "SOMETIMES" IS IN THE GAME'S OWN GETTER, which the row asked for.
# `AttackIntent.GetSingleDamage` (decompiled from `sts2.dll`, v0.111.0) is:
#
#     decimal num = DamageCalc();
#     Player me = LocalContext.GetMe(owner.CombatState);
#     if (me != null)
#         num = Hook.ModifyDamage(..., ModifyDamageHookType.All, ...);
#     return Math.Max(0, (int)num);
#
# So the label folds EVERY modifier -- the enemy's Weak, the player's
# Vulnerable, Strength -- on a frame where the local player resolves, and
# returns the RAW move damage on a frame where `LocalContext.GetMe` answers
# null. The bridge asks for the label on whatever frame the poll lands on
# (`McpMod.StateBuilder.cs:1606`), so both answers reach this page under one
# field name and nothing on the wire says which one arrived. The seat's two
# reads are that pair exactly: 11 raw is 8 through Weak (11 x 0.75, truncated),
# and 7 raw is 5.
#
# THE PAGE DOES NO ARITHMETIC ON THE GAME'S NUMBER AND CLAIMS NEITHER. It
# prints the multiplier the board is standing in and BOTH landings, which is
# `PER_HIT_NOTE`'s shape one field over and for the same reason: two readings
# are both live, both have been seen, and a page that picks one is guessing on
# the seat's behalf.
#
# BUT ONLY WHERE THE WIRE CANNOT SAY WHICH, and since `EB-607`'s bridge half
# it usually can. The intent's `breakdown` is `GetSingleDamage` call for call
# -- the same `Hook.ModifyDamage(..., ModifyDamageHookType.All, ...)` under
# the same `LocalContext.GetMe` guard -- so where it arrived, the figure is
# the folded one and its `modifiers` list names Weak and Vulnerable when they
# were counted. Every Weak line three seats read on 2026-09-24 sat under a
# breakdown saying so ("the game folded **Weak** into that: it is 6 on the
# move and 4 after") and then offered 3 as a second landing; the seats took
# the headline each time, and the second landing was Weak counted twice. So a
# part carrying a breakdown prints one number, the game's, and no fold line;
# the two-landing line is left for a part that arrived without one (a bridge
# older than `EB-607`, or the frame where `GetMe` answered null).
#
# THE MULTIPLIERS ARE THE GAME'S OWN CONSTANTS. `WeakPower.CanonicalVars` is
# `DamageDecrease 0.75`, `VulnerablePower.CanonicalVars` is `DamageIncrease
# 1.5`, and both truncate to an int at the end (`(int)num`). Both can be moved
# by a relic or a power -- Paper Krane and Debilitate on Weak, Paper Phrog and
# Cruelty on Vulnerable -- and the note says so rather than pretending the
# constant is the whole rule.
INTENT_FOLD_NOTE = (
    "*An intent's figure is the game's own `GetIntentLabel`, and that getter "
    "folds the board's multipliers in only on a frame where it can resolve the "
    "local player; on any other frame it returns the move's raw damage. Where "
    "the game also sends how it arrived at the figure, the line says what it "
    "folded and that figure is the one to read. A part marked `Folded "
    "through` arrived without that, so nothing on the feed says which of the "
    "two it is, and the line prints both landings and this page picks "
    "neither. The multipliers used are the game's own constants (Weak x0.75, "
    "Vulnerable x1.5, truncated); a relic or power that moves either -- Paper "
    "Krane, Debilitate, Paper Phrog, Cruelty -- is not in this arithmetic.*")

_WEAK_MULTIPLIER = 0.75
_VULNERABLE_MULTIPLIER = 1.5


def _stacks_of(blob: dict[str, Any], word: str) -> int:
    """How many stacks of a named power this body is wearing, or 0."""
    for power in blob.get("powers") or []:
        if _fold(power.get("name")) == word and isinstance(
                power.get("stacks"), int):
            return int(power["stacks"])
    return 0


def _intent_fold_lines(enemy: dict[str, Any],
                       you: dict[str, Any]) -> list[str]:
    """`EB-706`: both landings of a telegraph, where a multiplier stands.

    Empty on every board where neither Weak nor Vulnerable is up, which is
    most of them, and empty for a part whose label is not a plain number or a
    plain `NxM` -- the two shapes this page can take apart without guessing.

    AND EMPTY FOR A PART THAT CARRIES THE GAME'S BREAKDOWN. That block is the
    game's own fold of every modifier on the board, so its figure already
    counts the Weak and the Vulnerable this line would fold a second time; the
    breakdown clause on the intent line says what was folded, and one number
    is the whole answer (2026-09-24, three seats).
    """
    weak = _stacks_of(enemy, "weak")
    vulnerable = _stacks_of(you, "vulnerable")
    if not weak and not vulnerable:
        return []
    multiplier = ((_WEAK_MULTIPLIER if weak else 1.0)
                  * (_VULNERABLE_MULTIPLIER if vulnerable else 1.0))
    wearing = [w for w in (
        f"the **Weak {weak}** on this body" if weak else "",
        f"the **Vulnerable {vulnerable}** on you" if vulnerable else "") if w]
    out: list[str] = []
    for intent in enemy.get("intents") or []:
        if _fold(intent.get("type")) != "attack":
            continue
        if (intent.get("breakdown") or {}).get("repeats"):
            continue
        label = str(intent.get("label") or "").strip()
        multi = _MULTI_HIT_LABEL.match(label)
        if multi:
            each, hits = int(multi.group(1)), int(multi.group(2))
        elif label.isdigit():
            each, hits = int(label), 1
        else:
            continue
        folded = max(0, int(each * multiplier))
        if folded == each:
            continue
        shown = f"{each} each" if hits > 1 else str(each)
        lands = (f"{folded} each, {folded * hits} in all" if hits > 1
                 else str(folded))
        already = f"{each * hits} in all" if hits > 1 else str(each)
        out.append(f"      Folded through {' and '.join(wearing)}, {shown} "
                   f"lands as {lands}. If the figure above already counts "
                   f"{'them' if len(wearing) > 1 else 'it'}, it lands as "
                   f"{already}.")
    return out


def _hit_on_you_source(hit: dict[str, Any],
                       enemies: list[dict[str, Any]]) -> str:
    """Who dealt a hit that landed on you while a card resolved: the dealer
    the mod filed, named with its Thorns where the board shows it holding
    Thorns; with no dealer on the wire, the one enemy on the board holding
    Thorns; else nothing (2026-10-04, Klee w20 round). A hit the mod marks
    `self` (no dealer but you: a Drain) is your own HP cost, never a Thorns
    guess (the Furina pool-75 round, 2026-10-09)."""
    if hit.get("self"):
        return RESOLUTION_HIT_SELF
    def thorny(enemy: dict[str, Any]) -> bool:
        return any(_fold(str(p.get("name") or "")) == _fold(THORNS_POWER)
                   for p in enemy.get("powers") or [])
    source = str(hit.get("source") or "").strip()
    if source:
        # A board name may carry its number (`Slug (2)`); the mod's is bare.
        named = [e for e in enemies
                 if _fold(re.sub(r"\s*\(\d+\)$", "", str(e.get("name") or "")))
                 == _fold(source)]
        template = (RESOLUTION_HIT_THORNS if any(thorny(e) for e in named)
                    else RESOLUTION_HIT_SOURCE)
        return template.format(source=source)
    holders = [e for e in enemies if thorny(e)]
    if len(holders) == 1 and holders[0].get("name"):
        return RESOLUTION_HIT_THORNS.format(source=holders[0]["name"])
    return ""


def _resolution_lines(rows: list[dict[str, Any]],
                      stage: bool = False,
                      enemies: list[dict[str, Any]] | None = None
                      ) -> list[str]:
    """`EB-349` / `EB-611`. The turn's resolutions, with their hits numbered.

    ONE ROW PER CARD, ONE NUMBERED LINE PER HIT. The numbering is the point:
    `EB-611`'s seat could confirm which bodies a random multi-hit struck and
    never the order, and "Rapid Fire on a hallway prints four ordered lines" is
    the row's acceptance in as many words.

    A HIT THAT LANDED ENTIRELY ON BLOCK STILL PRINTS, and says so. It is a
    place in the order, and dropping it would print three lines for a four-hit
    card -- the same defect wearing a different hat.

    THE AUTO-PLAYED TURN IS THE ONE THIS SECTION WAS OPENED FOR. Where the game
    played every row, the note under them says what the board below is: the
    turn the reader never saw, which the page has had to describe as a gap
    since `AUTO_TURN_NOTE` was written.
    """
    if not rows:
        return [NO_RESOLUTIONS_THIS_TURN]
    out: list[str] = []
    for row in rows:
        clauses = ""
        if row.get("auto_played"):
            clauses += RESOLUTION_AUTO_CLAUSE
        if row.get("carried"):
            clauses += RESOLUTION_CARRIED_CLAUSE
        if row.get("overflowed"):
            clauses += RESOLUTION_OVERFLOW_CLAUSE
        out.append(RESOLUTION_ROW.format(card=row["card"], clauses=clauses))
        # 2026-09-25 evening: the performer a random summon rolled.
        if row.get("summoned"):
            out.append(RESOLUTION_SUMMONED.format(names=_and_list(
                [f"**{name}**" for name in row["summoned"]])))
        # The rebalance round (2026-10-03): Varka's Oath gains, sourced,
        # printed after the hits and powers that made them.
        oath_lines = [RESOLUTION_OATH.format(
            n=gain["amount"], element=gain["element"],
            source=f" ({gain['source']})" if gain["source"] else "")
            for gain in row.get("oath") or []]
        if oath_lines and row.get("fang_ascension"):
            oath_lines.append(RESOLUTION_FANG.format(
                relic=row.get("fang_relic") or RESOLUTION_FANG_DEFAULT))
        killed = row.get("killed") or []
        applied = row.get("applied") or []
        if not row["hits"] and not killed and not applied and oath_lines:
            out += oath_lines
            continue
        if not row["hits"] and not killed and not applied:
            # 2026-09-25 (opus-furina-l2b): on a board with a stage, a card
            # that hit nothing may still have moved a bar, and the stage log
            # above now files every Raise -- so the line points there rather
            # than saying nothing countable happened.
            # The Varka payoff round (2026-10-10): a Swirl with no aura to
            # Swirl says so (Sucrose on a bare board).
            if row.get("swirl_no_aura") and not row.get("swirl_on_aura"):
                out.append(RESOLUTION_NO_AURA)
            else:
                out.append(RESOLUTION_NO_HITS_STAGE if stage
                           else RESOLUTION_NO_HITS)
            continue
        for n, hit in enumerate(row["hits"], start=1):
            target = hit["target"] or "an enemy"
            # A body that died inside the play: the game hands the killing hit
            # to no damage hook, so the ledger files the death with no number.
            if hit.get("killed"):
                out.append(RESOLUTION_HIT_KILLED.format(n=n, target=target))
                continue
            if hit.get("on_player"):
                line = RESOLUTION_HIT_ON_YOU.format(
                    n=n, target=target, amount=hit["amount"],
                    source=_hit_on_you_source(hit, enemies or []))
                if hit["blocked"] > 0:
                    line += RESOLUTION_HIT_BLOCKED.format(blocked=hit["blocked"])
                out.append(line)
                continue
            if hit["amount"] <= 0 and hit["blocked"] > 0:
                out.append(RESOLUTION_HIT_ALL_BLOCKED.format(
                    n=n, target=target, blocked=hit["blocked"]))
                continue
            line = RESOLUTION_HIT_ROW.format(n=n, target=target,
                                             amount=hit["amount"])
            if hit["blocked"] > 0:
                line += RESOLUTION_HIT_BLOCKED.format(blocked=hit["blocked"])
            out.append(line)
        # 2026-09-26 (the Silent control seat): the powers it put on enemies.
        for a in applied:
            out.append((RESOLUTION_APPLIED if a["amount"] > 0
                        else RESOLUTION_REMOVED).format(
                power=a["power"], n=abs(a["amount"]),
                target=a["target"] or "an enemy"))
        out += oath_lines
        # And a kill the ledger did not file, read off the board: after the
        # numbered hits, because no place in their order is known.
        if killed:
            out.append(RESOLUTION_KILLED.format(
                targets=_and_list([f"**{k}**" for k in killed])))
    if all(row.get("auto_played") for row in rows):
        out += ["", RESOLUTION_AUTO_TURN_NOTE]
    return out


def _render_intents(intents: list[dict[str, Any]]) -> list[str]:
    """Every component of one telegraph, one line each (`EB-342`).

    A move with one component reads exactly as it always did -- `Intent:` and
    the line. A move with several prints each component under its own
    `and also:` continuation, because the seat that read `Attack for 8` and
    then opened the next round with four `Burn`s in hand was reading the FIRST
    of two rows the wire sent, and there is no shape of one line that can hold
    two telegraphs without inventing a grammar for joining them.

    `EB-461`: and where there IS more than one, every number on them is marked
    as ONE PART of the move rather than as the move. The feed sends no marker
    saying which parts of a chosen move resolve -- see `MULTI_INTENT_NOTE`,
    which the board prints once under the enemy block. Neither the label nor
    the note claims how often such a part lands: the first wording did, and
    the r15 seats stopped blocking against telegraphs that landed in full.
    """
    rows = list(intents) or [{}]
    part = len(rows) > 1
    out = [f"    Intent: {_render_intent(rows[0], part)}"]
    out += [f"      and also: {_render_intent(row, part)}" for row in rows[1:]]
    return out


def _render_intent(intent: dict[str, Any], part: bool = False) -> str:
    """One telegraph, with every field saying what it is (`EB-299`).

    The line used to be `kind`, `label` and `text` joined by commas, so a
    debuff turn read `Strategic, 2, This enemy intends to apply a Debuff to
    you` and the r2 Codex seat reported that "the Strategic intent's number
    was understandable only from its accompanying sentence". That is three
    different grammars in one comma list, which is `EB-198`'s lesson: the
    number is the one the game DRAWS ON THE ICON and the feed gives it no
    unit, so the page says that is what it is instead of setting it beside a
    word it does not modify. The wire's `type` -- the mechanical kind, which
    the page dropped the way it dropped a power's (`EB-179`) -- goes back on
    beside the hover tip's heading where the two differ.

    `EB-474`: a `Defend` part says that it ADDS BLOCK. The feed sends that
    part with an empty `label` and, on every capture in `review/qa`, no
    description at all -- so the line read `Defensive (Defend)` and nothing on
    it connected the part to the `Block N` on the body's own line one row up.
    The Furina r9 seat played `Deal 6` into a 5-HP body that lived at 4 and
    could not account for it, having read the HP line as the whole target.
    """
    head = intent.get("kind") or intent.get("type") or ""
    kind = intent.get("type") or ""
    if head and kind and _fold(head) != _fold(kind):
        head = f"{head} ({kind})"
    # Seat page 5 (2026-10-05): "icon shows 8" for "the number on its icon
    # is 8", and the game's generic hover sentence only where it adds
    # something (`_hover_adds_nothing`).
    number = (INTENT_ICON_NUMBER.format(label=intent["label"])
              + (MULTI_INTENT_LABEL if part else "")
              if intent.get("label") else "")
    text = "" if _hover_adds_nothing(intent) else intent.get("text") or ""
    bits = [head, number, text]
    # `EB-607`: the two numbers on this line are two fields of the feed --
    # `GetIntentLabel`'s icon figure and `GetHoverTip`'s sentence -- and the
    # page printed both and said nothing about the pair.
    if _numbers_disagree(intent):
        bits.append(INTENT_NUMBER_DISAGREES)
    # `EB-607`, the second half: WHERE THAT NUMBER CAME FROM. The bridge sends
    # the game's own base, the figure its hook phases arrived at, and the
    # models it folded in -- so the line no longer has to leave `12 before and
    # after Strength 3` unexplained. Nothing here is recomputed; the fold line
    # prints only where something WAS folded, and the total only on a
    # multi-hit, because a clause under every intent is noise.
    bits += _breakdown_clauses(intent.get("breakdown") or {})
    # Seat page 3 (2026-10-05): what a debuff move does, read off the base
    # game by the move's id (`blindplay_moves`). "Strategic (Debuff)" alone
    # did not say Weak from Frail from a stolen card.
    if intent.get("effect"):
        bits.append(INTENT_EFFECT_CLAUSE.format(effect=intent["effect"]))
    if _fold(kind) == "defend":
        bits.append(DEFEND_INTENT_CLAUSE)
    # `EB-323`: and a part says whose side it is on. `Empower (Buff)` was a
    # heading, a bracketed kind and nothing else on a board of three bodies.
    # The WIRE answers this now, off the game's own `IntentType`, for every
    # kind that settles it; the older buff-only clause is what a feed that
    # sends nothing still gets, so a bridge predating the row is unmoved.
    side = _text(intent.get("target_side"))
    if side:
        bits.append(INTENT_TARGET_SIDE.format(side=side))
    elif _fold(kind) == "buff":
        bits.append(BUFF_INTENT_CLAUSE)
    return " — ".join(b for b in bits if b) or "(no intent shown)"


def _breakdown_clauses(breakdown: dict[str, Any]) -> list[str]:
    """`EB-607`. What the bridge read off `Hook.ModifyDamage`, in two clauses.

    The FOLD clause answers the r23 question directly -- `12 on the move and 15
    after`, naming what did it -- and the NOTHING-FOLDED form answers the other
    half of the same find, Fossil Stalker's 12 that did not move under
    Strength 3. Both print only on an attack part, because that is the only
    part the game hands a breakdown for.

    THE TOTAL is a multi-hit's own line, and it is the game's arithmetic and
    not this page's: the bridge sends the product beside its factors, and this
    prints all three so the reader can check it.
    """
    if not breakdown or not breakdown.get("repeats"):
        return []
    out: list[str] = []
    mods = breakdown.get("modifiers") or []
    if mods:
        out.append(INTENT_FOLD_CLAUSE.format(
            modifiers=_and_list([f"**{m}**" for m in mods]),
            base=breakdown["base"], folded=breakdown["folded"]))
    elif breakdown["base"] == breakdown["folded"]:
        out.append(INTENT_FOLD_NOTHING.format(base=breakdown["base"]))
    if breakdown["repeats"] > 1:
        out.append(INTENT_TOTAL_CLAUSE.format(
            folded=breakdown["folded"], repeats=breakdown["repeats"],
            total=breakdown["total"]))
    return out


def _and_list(items: list[str]) -> str:
    """`a`, `a and b`, `a, b and c`. The page's own joining, spelled once."""
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " and " + items[-1]


#: `EB-701`. The trigger the turn-order note answers, matched on the SENTENCE
#: and never on a name -- the rule this page is under for every note it reads
#: off a printed face. "at the end of your turn", "at the end of the turn",
#: "at end of turn": the game writes all three and they are one moment.
_END_OF_TURN = re.compile(r"\bend of (?:your |the |this )?turn\b", re.I)


def _end_of_turn_on_board(c: dict[str, Any]) -> bool:
    """Does anything on this combat screen fire at the end of your turn?

    THE POWERS FIRST, because that is the row `EB-701`'s gate names, and both
    sides of the board: an enemy's own end-of-turn trigger resolves in the same
    step and a reader planning a kill needs the order either way.

    AND THE TWO KIT BLOCKS, which carry the two effects the seat named. A Dusk
    entry is a Plan whose carry-out moved to the end of THIS turn, and the
    stage's performers act at the end of your turn by rule -- neither is a
    power and neither would be found by reading the power rows alone.
    """
    powers = list(c["you"]["powers"])
    for e in c["enemies"]:
        powers += e["powers"]
    if any(_END_OF_TURN.search(p.get("text") or "") for p in powers):
        return True
    if _orb_end_of_turn(c):
        return True
    if c.get("stage") is not None:
        return True
    plans = c.get("plans") or {}
    return any(_is_dusk(e) for e in (plans.get("queue") or []))


def _orb_lines(orbs: dict[str, Any] | None) -> list[str]:
    """The orbs in slot order, oldest first, and which one evokes next.

    2026-09-26 (control seat, Defect): no orb was printed anywhere, and the
    seat misread "your rightmost Orb" twice. The oldest orb is the rightmost
    one (`OrbCmd.EvokeNext` takes `Orbs.First()`), so the page says so.
    """
    if not orbs:
        return []
    rows = orbs["list"]
    out = [f"- Orbs: {len(rows)} of {orbs['slots']} slots filled"
           + (", oldest first:" if rows else ".")]
    for n, o in enumerate(rows, start=1):
        # The orb's own sentence carries both figures, Focus folded in;
        # the bare numbers stand in only where the wire sent no sentence.
        out.append(f"  {n}. **{o['name']}** — " + (
            o["text"] or f"passive {o['passive']}, evoke {o['evoke']}"))
    if rows:
        out.append(ORB_ORDER_NOTE)
    return out


def _ally_lines(pets: list[dict[str, Any]]) -> list[str]:
    """Each pet no kit block prints (Osty), with HP, Block and powers."""
    out = []
    for pet in pets:
        out.append(f"- Your ally **{pet['name']}**: HP {pet['hp']}/"
                   f"{pet['max_hp']}"
                   + (f", Block {pet['block']}" if pet["block"] else ""))
        out += [_render_power(pw, "    - ") for pw in _once(pet["powers"])]
    return out


def _orb_end_of_turn(c: dict[str, Any]) -> bool:
    """Does an orb on this board fire at the end of your turn?"""
    orbs = c["you"].get("orbs") or {}
    return any(_END_OF_TURN.search(o.get("text") or "")
               for o in orbs.get("list") or [])


def _turn_order_note(c: dict[str, Any]) -> str:
    """`TURN_ORDER_NOTE` with only this board's examples (2026-09-26).

    A kit's word is named only where that kit's block is on the board: the
    Ironclad control seat read "a performer's act, a Dusk Plan" on its own
    board and met two words it could not look up.
    """
    examples = [TURN_ORDER_POWER]
    if _orb_end_of_turn(c):
        examples.append(TURN_ORDER_ORB)
    if c.get("stage") is not None:
        examples.append(TURN_ORDER_PERFORMER)
    if c.get("plans"):
        examples.append(TURN_ORDER_DUSK)
    return TURN_ORDER_NOTE.format(examples=", ".join(examples))


#: `EB-708`. The size the game draws into a printed name -- `Twig Slime (M)`,
#: `Leaf Slime (S)`. Case-sensitive and anchored on the brackets, so it fires
#: on a size and not on a parenthetical the mod writes into a title.
_SIZE_LETTER = re.compile(r"\((?:S|M|L)\)")


def _colliding(items: list[dict[str, Any]]) -> bool:
    """Do two of these options print the same name? (`EB-341`)

    The Future of Potions printed three options, two of them
    character-for-character identical (`Insert Common Potion`, losing a
    different potion each), and the only grammar was `choose "<option>"`. The
    r7b act-2b seat sent the title, it was "accepted with an empty refusal",
    and no screen ever said which of the two it took: "If the roll had gone the
    other way I would have lost a potion I meant to keep and been told
    nothing."
    """
    names = [_fold(o.get("name")) for o in items if _fold(o.get("name"))]
    return len(set(names)) < len(names)


def _render_options(items: list[dict[str, Any]], bullet: str = "-") -> list[str]:
    # `EB-341`: the ordinal in front of the title, and ONLY where two titles
    # collide -- a number on every row of every screen would be furniture, and
    # `choose <number>` works whether or not the number is printed. The
    # ordinal is the row's place in this list, which is the number the grammar
    # resolves, so the page and the resolver cannot mean different things by 2.
    ordinals = _colliding(items)
    out = []
    for i, o in enumerate(items, 1):
        line = f"{bullet} "
        if ordinals:
            line += f"{i}. "
        line += f"**{o['name'] or '(unnamed)'}**"
        # `EB-262`: the card's own cost first, then the gold, because they are
        # two different prices and a row that printed only the gold is what
        # bought a 3-energy card blind.
        bits = [b for b in (f"cost {o['cost']}" if o.get("cost") else "",
                            o.get("kind") or "",
                            f"{o['price']} gold"
                            if o.get("price") is not None else "") if b]
        if bits:
            line += " — " + ", ".join(bits)
        if not o.get("enabled", True):
            # `EB-262`: `sold` where the page can prove the shelf was bought
            # -- it printed the card itself before the purchase -- and the
            # unchanged `not available` everywhere else, which covers a shelf
            # that was never stocked and a row priced out of reach.
            line += f" ({o.get('unavailable') or 'not available'})"
        # `EB-448`: the mark the event screen never had. `was_chosen` is on
        # the feed and says this row is the one this room has already
        # resolved, which is what makes the outcome below readable as an
        # outcome rather than as an offer.
        if o.get("taken"):
            line += " — TAKEN"
        out.append(line)
        if o.get("text"):
            out.append(f"    {o['text']}")
        # `EB-448`: what this row NAMES, each in the game's own words. An
        # option that hands over a card or a relic carries its face on the
        # feed and the page dropped it, so a granted `Byrdonis Egg` was a
        # sentence and never a card.
        for named in o.get("names") or []:
            row = f"    · **{named['name']}**"
            # The guest seat round (2026-09-25): a named CARD's cost, in the
            # words a reward row prints it (`cost 2`), where the feed sent one.
            if named.get("cost"):
                row += f" — cost {named['cost']}"
            if named.get("text"):
                row += f" — {named['text']}"
            out.append(row)
        if o.get("note"):
            out.append(f"    *{o['note']}*")
    return out


#: `EB-735`. The window the stage log covers, said once at the head of the
#: section. The clear is at her turn END, so what a seat opening a turn reads
#: here is the end-of-turn acts it could not watch, then the enemies' turn,
#: then what it has played since.
STAGE_LOG_HEADING = ("- Since you ended your last turn, in order (the "
                     "end-of-turn acts, the enemies' turn, then what you have "
                     "played this turn):")

# THE STAGE, RE-FOUNDED (2026-10-04, review/active/furina-refounding-2026-10-03.md
# sec.1 as amended by sec.8). Performers have no bars and take no hits;
# Fanfare is ONE number on Furina, with no fade and no cap; a star pays its
# price for each act or skips it; a Bow is a free act, then 1 Fanfare. The
# block prints her Fanfare with this turn's flow, Rehearsal, the seats front
# to back (guests marked, stars' prices), each performer's act in its badge's
# words, the mod's forecast of the end of the turn, and the log in plain
# words. No markup in any literal (`EB-246`): the page's own words are
# written folded.

#: The header line: her Fanfare and this turn's flow.
STAGE_FANFARE_LINE = ("- Fanfare {fanfare} (this turn: {gained} gained, "
                      "{spent} spent on Spend, {paid} paid by stars)")
#: THE SALON'S TAB (2026-10-05): the HP loan's two numbers, the "Drained N"
#: counter's reading. The Drain line rule (2026-10-09): a Drain may go past
#: the line, and what it drains past it does not return.
STAGE_DRAIN_LINE = ("- Drained {drained} HP{past}. Drained HP above your "
                    "line returns after combat. Drain line {line} HP{why}: "
                    "HP you Drain past it is lost unless you Repay it.")
#: THE "LOST FOR GOOD" COUNTER (the quarter-line round, 2026-10-10, "What to
#: change" 1): the part drained past the line, after the drained count, only
#: when there is any. Seats learned that cost only by losing the HP.
STAGE_DRAIN_PAST = " ({past} past your line: lost unless you Repay)"
#: THE SPEND ROUND (2026-10-10, "A Five-Century Act becomes visible"): with
#: the power up the past-line part returns after combat, so the counter drops
#: "lost unless you Repay" and the line says the return covers it.
STAGE_DRAIN_LINE_RETURNS = ("- Drained {drained} HP{past}. Drained HP "
                            "returns after combat, past your line too. "
                            "Drain line {line} HP{why}.")
STAGE_DRAIN_PAST_RETURNS = " ({past} past your line)"
#: THE SPEND ROUND 2 (2026-10-10, change 4): a line of 0 explains itself. A
#: seat read "Drain line 0" as "every Drain is permanent", which is
#: backwards: at 0 every Drain stays above the line and returns. The words
#: are `FurinaStageLaw.LineZeroReturns`.
STAGE_DRAIN_LINE_ZERO = ("- Drained {drained} HP. Drain line 0 HP{why}: all "
                         "your Drain returns after combat.")
#: Seat page 3: where the line comes from ("the HP you started this fight
#: with, minus 1/4 of your Max HP", 2026-10-09); seats connected it to their
#: entry HP only late.
STAGE_DRAIN_WHY = " ({why})"
STAGE_REHEARSAL_CLAUSE = " · Rehearsal {n}"
STAGE_EMPTY_LINE = "- The stage is empty."
STAGE_SEATS_LINE = "- Seats, front to back ({used} of {capacity}): {seats}."
STAGE_GUEST_MARK = " (Guest Star, pays {price} per act)"
STAGE_GUEST_FREE_MARK = " (Guest Star)"
STAGE_ACT_LINE = "- **{who}** — {act}"

#: The forecast (`FurinaStage.Forecast`), one line per seat, front to back.
STAGE_FORECAST_HEADING = "- At the end of your turn, front to back:"
#: A star that cannot pay (or Chevreuse, who acts once a turn) skips.
STAGE_FORECAST_SKIPS = "  - **{who}**: skips its act (it costs {price} Fanfare)"
STAGE_FORECAST_SKIPS_FREE = "  - **{who}**: skips its act"
STAGE_FORECAST_ROW = "  - **{who}**: {what}{price}{times}"
STAGE_FORECAST_PRICE = ", pays {price} Fanfare"
STAGE_FORECAST_TWICE = ", twice"
STAGE_FORECAST_TIMES = ", {n} times"
STAGE_FORECAST_AFTER = "- After the acts: Fanfare {fanfare}."
#: What one act of each kind does, as the forecast names it.
STAGE_KIND_WORDS = {
    "block": "{n} Block",
    "damage": "{n}{element} damage to {target}",
    "energy": "{n} Energy next turn",
    "fanfare": "{n} Fanfare",
    # The Salon's Tab (2026-10-05): Charlotte's and Sigewinne's act.
    "repay": "Repay {n}",
    "card": "adds a Trick to your hand",
    "ensemble": "your Salon members act",
}

#: The log, one line per beat. `{who}` is the performer's short name.
STAGE_LOG_ARRIVE = "  - **{who}** joined the stage{src}."
STAGE_LOG_ACT = "  - **{who}**{where} acted{effect}."
STAGE_LOG_ACT_FREE = "  - **{who}**{where} acted for free{effect}."
#: 2026-09-26 (lane 1): a seat's repeat (Full House) says so.
STAGE_LOG_ACT_AGAIN = "  - **{who}** acted again{effect}."
#: Where twins stand, each act names its seat (front = seat 1).
STAGE_LOG_SEAT = " (seat {n})"
STAGE_LOG_SKIP = "  - **{who}** skipped its act: {why}."
STAGE_LOG_SKIP_PLAIN = "  - **{who}** skipped its act."
STAGE_LOG_PAY = "  - **{who}** paid {n} Fanfare: {before} → {after}."
STAGE_LOG_BOW_STAYS = "  - **{who}** took a Bow and stays on stage."
STAGE_LOG_BOW_LEAVES = "  - **{who}** took a Bow."
STAGE_LOG_LEAVE = "  - **{who}** left the stage: {why}."
STAGE_LOG_WALKON = ("  - **{who}** walked on: every seat holds a Guest Star, "
                    "so it took its Bow without a seat.")
STAGE_LOG_CUE = "  - You Cued **{who}**."
STAGE_LOG_MOVE = "  - **{who}** moved to the front."
#: THE POOL TO 75 (2026-10-09, sec.3): a second copy of a guest on stage moves
#: it to the newest seat, with no act; and a guest's line has a log line of
#: its own, so it is not read as an act.
STAGE_LOG_REPEAT = ("  - **{who}** moved to the newest seat (a second copy; "
                    "no act).")
STAGE_LOG_LINE = "  - **{who}**'s line ({n})."
STAGE_LOG_GAIN = "  - You gained {n} Fanfare{src}: {before} → {after}."
STAGE_LOG_SPEND = "  - You spent {n} Fanfare: {before} → {after}."
STAGE_LOG_DRAIN = "  - You drained {n} HP."
STAGE_LOG_REPAY = "  - You repaid {n} HP."
#: The drain-line round (2026-10-09): a Power's hit (Critics' Darling, Salon's
#: Encore, Thunderous Applause) has a log line, so a seat can see it.
STAGE_LOG_HIT = "  - **{src}** dealt {n} damage to {to}."
STAGE_LOG_HIT_REACH = {"all": "ALL enemies", "random": "a random enemy"}
STAGE_SOURCE_CLAUSE = " from {src}"
#: What an act did, by kind, with the beat's measured figure.
STAGE_LOG_EFFECTS = {
    "block": ": Furina gains {n} Block",
    "damage": ": {n} damage{to}",
    "energy": ": {n} Energy next turn",
    "fanfare": ": you gain {n} Fanfare",
    "repay": ": you Repay {n}",
}
#: Which kind each guest's act is, where it is not damage: the mod's own
#: table (`FurinaStage.CueOf`). SEAT PAGE 3 (2026-10-05): this still held the
#: v2 Stage's kinds, so Chevreuse's act (4 damage to a random enemy) logged
#: as "4 Energy next turn", Lyney's as a Trick and the two Repays as Block
#: and Fanfare.
STAGE_MEMBER_KINDS = {
    "charlotte": "repay", "sigewinne": "repay",
    # The v2 Stage's retired performers, for its recorded logs. (Escoffier
    # came back with the pool to 75 as a damage act, 4 Cryo to ALL.)
    "usher": "block",
}
#: The damage acts' reach, where the act names no one body (Lyney now; the
#: v2 Stage's two for its recorded logs).
STAGE_ALL_MEMBERS = frozenset({"lyney", "chevalmarin", "neuvillette",
                               "escoffier"})


def _frozen_clause(row: dict[str, Any], obs: dict[str, Any],
                   combat: dict[str, Any]) -> str:
    """What a Frozen receipt needs beside it (2026-09-26), or `""`.

    A carried row whose body stands on this board without Frozen has worn
    off (`REACTION_FROZEN_THAWED_CLAUSE`). Not on a boss that is not a Minion:
    a boss is never Frozen (the Frozen row's `FROZEN_BOSS_CLAUSE`), so there is
    nothing to wear off. A body this board cannot find gets no clause:
    silence, never a guess."""
    if row.get("reaction") != "Frozen":
        return ""
    target = str(row.get("target") or "").strip().casefold()
    bodies = [e for e in (combat.get("enemies") or [])
              if str(e.get("name") or "").strip().casefold() == target]
    if not bodies:
        return ""

    def wears(body: dict[str, Any], name: str) -> bool:
        return any(str(p.get("name") or "").strip().casefold() == name
                   for p in (body.get("powers") or [])
                   if isinstance(p, dict))

    if obs.get("state_type") == "boss" and not any(
            wears(b, "minion") for b in bodies):
        return ""
    if row.get("carried") and not any(wears(b, "frozen") for b in bodies):
        return REACTION_FROZEN_THAWED_CLAUSE
    return ""


#: 2026-09-26 (wave-3 Furina lane 4). THE CHOOSER THAT OPENS OVER THE BOARD.
#: Arkhe Alignment asks "Ousia or Pneuma" at the start of every turn, after
#: the draw (`AfterPlayerTurnStart` follows the hand draw, 0.111.0
#: `CombatManager.SetupPlayerTurn`) -- but the page printed only the two
#: options, so the seat chose blind every turn and guessed wrong twice. The
#: bridge now sends the fight under a chooser that opened mid-fight
#: (`McpMod.StateBuilder.cs`, the overlay branch), and the page prints it here,
#: short: what a choice about this turn is made against.
BOARD_BEHIND_HEADING = "## The fight behind this chooser"


def _stars_line(you: dict[str, Any]) -> list[str]:
    """The Regent's star total, beside energy (2026-09-26, control seat).

    Printed wherever the wire sends `stars`, which is wherever the game's own
    counter shows. Star Next Turn keeps its own row among the powers below.
    """
    if you.get("stars") is None:
        return []
    return [f"- Stars {you['stars']}"]


def _status_clause(counts: Any) -> str:
    """` (5 Dazed)` for a pile holding Status cards, `""` otherwise."""
    if not counts:
        return ""
    return " (" + ", ".join(f"{n} {name}" for name, n in counts) + ")"


def _render_board_behind(c: dict[str, Any]) -> list[str]:
    """The fight under a mid-fight chooser: you, your hand, the stage and each
    enemy's HP and intent."""
    you = c["you"]
    out = ["", BOARD_BEHIND_HEADING, "",
           f"- HP {you['hp']}/{you['max_hp']} · Block {you['block']} · "
           f"Energy {you['energy']}/{you['max_energy']}"
           + (f" · Stars {you['stars']}" if you.get("stars") is not None
              else "")]
    hand = [card["title"] for card in c.get("hand") or []]
    out.append("- Your hand: " + (", ".join(hand) if hand
                                  else "(your hand is empty)"))
    if c.get("stage") is not None:
        out += _render_stage(c["stage"], you)
    for e in c.get("enemies") or []:
        line = f"- **{e['name']}**"
        if e.get("phase_flip"):
            line += f" — {PHASE_FLIP_LINE}"
        else:
            line += f" — HP {e['hp']}/{e['max_hp']}"
        if e["block"]:
            line += f", Block {e['block']}"
        out.append(line)
        out += _render_intents(e["intents"])
    out += _intent_target_note(c.get("enemies") or [])
    return out


#: The Varka payoff round (2026-10-10): Four Winds' Ascension's once-per-
#: combat rule, under the card in the hand, in the base game's words for a
#: relic that adds a card. Printed while Boreas's Fang (or Wolf's Gravestone)
#: is held; Darv's Tome hands the same card with no such rule.
ASCENSION_TITLE = "Four Winds' Ascension"
ASCENSION_ONCE_NOTE = ("    - Added by {relic} the first time each combat you "
                       "gain Oath.")
ASCENSION_RELICS = ("Boreas's Fang", "Wolf's Gravestone")


#: The Varka forced-Amber round (2026-10-10): Wildfire Oath's payout, under
#: each card in the hand that applies Pyro, while the power is up. Its per-
#: application damage is the Pyro Oath per stack (`WildfireOathPower.
#: DamageFor`); it fires on every Pyro application of his, never on a Swirl's
#: spread, so an Anemo card does not get the line.
WILDFIRE_TITLE = "Wildfire Oath"
WILDFIRE_NOTE = "    - Wildfire: +{n} a hit."


def _wildfire_hit(you: dict[str, Any], oath: dict[str, Any] | None)         -> int | None:
    """Wildfire Oath's damage per Pyro application now, or None with the
    power down (or no Oath block to read his Pyro Oath off)."""
    if not oath:
        return None
    for power in you.get("powers") or []:
        if _fold(power.get("name")) == _fold(WILDFIRE_TITLE):
            stacks = power.get("stacks")
            stacks = stacks if isinstance(stacks, int) and stacks > 0 else 1
            return max(0, stacks * int(oath["counts"].get("Pyro") or 0))
    return None


def _applies_pyro(card: dict[str, Any]) -> bool:
    """Does this face apply Pyro: its element indicator (which follows an
    override row) or any of its `Applies Pyro` rows."""
    if card.get("element") == "Pyro":
        return True
    if any(k.get("name") == "Element overridden"
           for k in card.get("keywords") or []):
        return False
    return any(k.get("name") == "Applies Pyro"
               for k in card.get("keywords") or [])


def _ascension_relic(you: dict[str, Any]) -> str:
    """The relic that adds Four Winds' Ascension, as held, or `""`."""
    for relic in you.get("relics") or []:
        name = relic.get("name") if isinstance(relic, dict) else None
        if name and _fold(name) in {_fold(r) for r in ASCENSION_RELICS}:
            return str(name)
    return ""


#: VARKA (the Oath rework). The block's heading and its lines, in the words
#: his tips use (`ArmKeywordTips.ForOath` / `ForCurrentElement`). The payout
#: sentences are the wire badge's own (`VarkaLaw` numbers).
OATH_HEADING = "## Your Oath"
OATH_ELEMENT_LINE = "- Current element: {element}."
OATH_NO_ELEMENT_LINE = ("- Current element: none. Set by the last Pyro, "
                        "Hydro, Cryo or Electro you applied.")
OATH_COUNTS_LINE = "- Oath: {counts}."
OATH_PAYOUT_LINE = "- {payout}"
OATH_NO_PAYOUT_LINE = ("- Your Swirls pay nothing until you apply Pyro, "
                       "Hydro, Cryo or Electro.")
AURA_LINE = "{element}: an Anemo hit Swirls it."
AURA_NONE = "no aura."


def _render_oath(oath: dict[str, Any]) -> list[str]:
    """His block: current element, the four Oath counts, what a Swirl pays,
    and each enemy's aura, one fact a line."""
    element = oath["element"]
    out = [OATH_ELEMENT_LINE.format(element=element) if element
           else OATH_NO_ELEMENT_LINE]
    out.append(OATH_COUNTS_LINE.format(counts=", ".join(
        f"{el} {oath['counts'][el]}" for el in oath["counts"])))
    out.append(OATH_PAYOUT_LINE.format(payout=oath["payout"]) if oath["payout"]
               else OATH_NO_PAYOUT_LINE)
    for row in oath["auras"]:
        if row["element"] is None:
            clause = AURA_NONE
        else:
            clause = AURA_LINE.format(element=row["element"])
        out.append(f"- **{row['name']}**: {clause}")
    return out


def _render_stage(stage: dict[str, Any], you: dict[str, Any]) -> list[str]:
    """The stage (`EB-735`; the re-founding, 2026-10-04).

    Her Fanfare first, with this turn's flow and Rehearsal; then her Block and
    what it will be after the acts, and her HP; then the seats front to back,
    guests marked with their price; each performer's act in its badge's own
    words; and the mod's forecast of the end of the turn.
    """
    seats = stage["seats"]
    head = STAGE_FANFARE_LINE.format(
        fanfare=stage["fanfare"], gained=stage["gained"],
        spent=stage["spent"], paid=stage["paid"])
    if stage.get("rehearsal"):
        head += STAGE_REHEARSAL_CLAUSE.format(n=stage["rehearsal"])
    out = [head]
    # `EB-743`: her Block now, and after the acts where they give any.
    block = [f"Block {you['block']}"]
    forecast = stage.get("forecast")
    after = (forecast["block"] if forecast is not None
             else stage.get("act_block"))
    if after:
        block.append(f"after the acts: Block {you['block'] + after}")
    block.append(f"Furina {you['hp']}/{you['max_hp']}")
    out.append("- " + " · ".join(block))
    if stage.get("line") is not None:
        why = stage.get("line_why") or ""
        past = stage.get("drained_past") or 0
        returns = bool(stage.get("past_returns"))
        line_words = STAGE_DRAIN_LINE_RETURNS if returns else STAGE_DRAIN_LINE
        if stage["line"] <= 0:
            line_words = STAGE_DRAIN_LINE_ZERO
        past_words = STAGE_DRAIN_PAST_RETURNS if returns else STAGE_DRAIN_PAST
        out.append(line_words.format(
            drained=stage.get("drained", 0), line=stage["line"],
            past=past_words.format(past=past) if past > 0 else "",
            why=STAGE_DRAIN_WHY.format(why=why) if why else ""))
    if not seats:
        out.append(STAGE_EMPTY_LINE)
        return out
    names = []
    for row in seats:
        name = f"**{row['name']}**"
        if row.get("guest"):
            name += (STAGE_GUEST_MARK.format(price=row["price"])
                     if row.get("price") else STAGE_GUEST_FREE_MARK)
        names.append(name)
    out.append(STAGE_SEATS_LINE.format(
        used=len(seats), capacity=stage.get("capacity") or len(seats),
        seats=", ".join(names)))
    # 2026-09-28 (Furina seat): what each performer's act does, in its
    # badge's words. Twins print once.
    said: set[str] = set()
    for row in seats:
        if row.get("act") and row["name"] not in said:
            said.add(row["name"])
            out.append(STAGE_ACT_LINE.format(who=row["name"], act=row["act"]))
    out += _render_stage_forecast(forecast)
    return out


def _render_stage_forecast(forecast: dict[str, Any] | None) -> list[str]:
    """The mod's forecast of the end of this turn, one line per seat front to
    back: what the act does, a star's price, how many times it lands, or that
    it skips for want of Fanfare; then her Fanfare and the Block after the
    acts. Nothing on a build that sends none, or on an empty stage."""
    if not forecast or not forecast.get("acts"):
        return []
    out = [STAGE_FORECAST_HEADING]
    for act in forecast["acts"]:
        if act["skips"]:
            out.append((STAGE_FORECAST_SKIPS if act["price"]
                        else STAGE_FORECAST_SKIPS_FREE).format(
                who=act["name"], price=act["price"]))
            continue
        what = STAGE_KIND_WORDS.get(act["kind"], "{n}").format(
            n=act["amount"],
            element=f" {act['element']}" if act["element"] else "",
            target=act["target"] or "a random enemy")
        times = act.get("times") or 1
        out.append(STAGE_FORECAST_ROW.format(
            who=act["name"], what=what,
            price=(STAGE_FORECAST_PRICE.format(price=act["price"])
                   if act["price"] else ""),
            times=(STAGE_FORECAST_TIMES.format(n=times) if times > 2
                   else STAGE_FORECAST_TWICE if times == 2 else "")))
    out.append(STAGE_FORECAST_AFTER.format(fanfare=forecast["fanfare_after"]))
    return out


#: The damage acts whose number is the HP she lost since her last turn
#: (`FurinaStageDirector.ActBody`, Neuvillette).
STAGE_HP_LOST_MEMBERS = frozenset({"neuvillette"})
STAGE_NO_DAMAGE_HP_LOST = ": no damage (you lost no HP since your last turn)"


#: The element a guest's act deals, for the log (the act beat carries the
#: amount and not the element; `FurinaStageDirector.Act`).
STAGE_MEMBER_ELEMENTS = {
    "neuvillette": "Hydro", "clorinde": "Electro", "navia": "Geo",
    "lynette": "Anemo", "wriothesley": "Cryo", "lyney": "Pyro",
    # The pool to 75 (2026-10-09).
    "freminet": "Cryo", "escoffier": "Cryo",
}


def _stage_act_effect(row: dict[str, Any]) -> str:
    """What one act did, with the beat's figure."""
    member = row["member"]
    kind = STAGE_MEMBER_KINDS.get(member, "damage")
    n = row["moved"]
    if kind == "card":
        return ": adds a Trick to your hand"
    if kind == "ensemble":
        return ": your Salon members act"
    if kind == "damage":
        if n <= 0:
            # The Furina full-run round (2026-10-10): his act reads the HP
            # she lost since her last turn, so a 0 says why.
            return (STAGE_NO_DAMAGE_HP_LOST if member in STAGE_HP_LOST_MEMBERS
                    else ": no damage")
        element = STAGE_MEMBER_ELEMENTS.get(member, "")
        to = (" to ALL enemies" if member in STAGE_ALL_MEMBERS
              else f" to {row['target']}" if row.get("target")
              else " to an enemy with an aura" if member == "lynette"
              else " to a random enemy")
        return f": {n}{' ' + element if element else ''} damage{to}"
    return STAGE_LOG_EFFECTS[kind].format(n=n)


def _render_stage_log(stage: dict[str, Any]) -> list[str]:
    """One line per beat, in order, in plain words."""
    out: list[str] = []
    free: str | None = None
    # 2026-09-26 (lane 1): two acts of one kind in a row read as one, so a
    # seat's repeat says "again" and twins name their seats.
    seats = stage.get("seats") or []
    twins = {r["name"] for r in seats
             if sum(1 for o in seats if o["name"] == r["name"]) > 1}
    last_key: int | None = None
    for row in stage["log"]:
        event, who = row["event"], row["name"]
        src = (STAGE_SOURCE_CLAUSE.format(src=row["source"])
               if row.get("source") else "")
        if event != "act":
            free = None
            last_key = None
        if event == "arrive":
            out.append(STAGE_LOG_ARRIVE.format(who=who, src=src))
        elif event == "act":
            key = row.get("key")
            effect = _stage_act_effect(row)
            if key is not None and key == last_key and free is None:
                out.append(STAGE_LOG_ACT_AGAIN.format(who=who, effect=effect))
                continue
            last_key = key
            where = (STAGE_LOG_SEAT.format(n=row["seat"] + 1)
                     if who in twins and row.get("seat", -1) >= 0 else "")
            template = (STAGE_LOG_ACT_FREE if free == row["member"]
                        else STAGE_LOG_ACT)
            out.append(template.format(who=who, where=where, effect=effect))
        elif event == "skip":
            out.append(STAGE_LOG_SKIP.format(who=who, why=row["why"])
                       if row.get("why")
                       else STAGE_LOG_SKIP_PLAIN.format(who=who))
        elif event == "pay":
            out.append(STAGE_LOG_PAY.format(
                who=who, n=row["moved"], before=row["fanfare"] + row["moved"],
                after=row["fanfare"]))
        elif event == "bow":
            out.append(STAGE_LOG_BOW_STAYS.format(who=who)
                       if row.get("why") == "stays"
                       else STAGE_LOG_BOW_LEAVES.format(who=who))
            free = row["member"]
        elif event == "leave":
            out.append(STAGE_LOG_LEAVE.format(who=who, why=row["why"]))
        elif event == "walkon":
            out.append(STAGE_LOG_WALKON.format(who=who))
        elif event == "cue":
            out.append(STAGE_LOG_CUE.format(who=who))
        elif event == "move":
            out.append(STAGE_LOG_MOVE.format(who=who))
        elif event == "repeat":
            out.append(STAGE_LOG_REPEAT.format(who=who))
        elif event == "line":
            out.append(STAGE_LOG_LINE.format(who=who, n=row["moved"]))
        elif event == "gain":
            out.append(STAGE_LOG_GAIN.format(
                n=row["moved"], src=src, before=row["fanfare"] - row["moved"],
                after=row["fanfare"]))
        elif event == "spend":
            out.append(STAGE_LOG_SPEND.format(
                n=row["moved"], before=row["fanfare"] + row["moved"],
                after=row["fanfare"]))
        elif event == "drain":
            out.append(STAGE_LOG_DRAIN.format(n=row["moved"]))
        elif event == "repay":
            out.append(STAGE_LOG_REPAY.format(n=row["moved"]))
        elif event == "hit" and row.get("source"):
            out.append(STAGE_LOG_HIT.format(
                src=row["source"], n=row["moved"],
                to=STAGE_LOG_HIT_REACH.get(row.get("why"), "a random enemy")))
    return out


#: `EB-676`. WHY THE TWO NUMBERS CAN DISAGREE, said once and claiming nothing
#: about which is right. There is one HP field on the wire -- `BuildPlayerState`
#: writes `creature.CurrentHp` on every screen -- so a victory screen reading
#: 25/80 and the next screen reading 16/80 are ONE field at two moments, not a
#: player block and a save disagreeing. The earlier of the two can be read
#: before the fight's own end-of-turn effects have landed in it, which is
#: exactly the 9 HP of Constrict the r26 seat planned its map around.
HP_SETTLE_NOTE = (
    "*This page reads one HP figure off the game's data feed and prints it "
    "unchanged; it has no second source and does no arithmetic on it. A figure "
    "read the instant a fight ends can be read before that fight's own "
    "end-of-turn effects have landed in it, so a drop that appears on the next "
    "screen may be the previous screen's number settling rather than anything "
    "this screen did.*")

#: `EB-715`. The act break is a room this page never had. Nothing here claims a
#: cause: every number in the block is the feed's, before and after.
ACT_CHANGE_NOTE = (
    "*The game moves the run between acts on a screen this tool is not shown: "
    "a boss reward, a rest and the act's own transition all resolve before the "
    "next page is drawn. The numbers above are this page's own previous read "
    "and its read now -- nothing here says which step did what.*")


def _render_run_change(change: dict[str, Any]) -> list[str]:
    """`EB-676` / `EB-715`: what moved since the previous screen, or nothing.

    ONE BLOCK, TWO ROWS. An act change prints the whole ledger -- act, HP, gold
    and deck -- because that is `EB-715`'s ask and because an act break moves
    all four at once. Anything else prints the HP line alone, and only where
    the ROOM changed: HP moving between round one and round two of a fight is
    the fight, and the combat page has already printed the blow that did it.

    2026-09-26: and gold, the deck's own cards and a belt potion the game
    used by itself, wherever they moved (`_deck_move_lines`).
    """
    if not change:
        return []
    out: list[str] = []
    if change.get("act"):
        was, now = change["act"]
        out += ["", "## Between the last screen and this one, the act changed",
                "", f"- Act {was} → Act {now}"]
        if change.get("hp"):
            out.append(f"- HP {change['hp'][0]} → {change['hp'][1]}"
                       + (f" (of {change['max_hp']})" if change.get("max_hp")
                          else ""))
        if change.get("gold"):
            out.append(f"- Gold {change['gold'][0]} → {change['gold'][1]}")
        if change.get("deck"):
            out.append(f"- Cards in the deck {change['deck'][0]} → "
                       f"{change['deck'][1]}")
        out += _deck_move_lines(change)
        out += ["", ACT_CHANGE_NOTE]
        return out
    rows: list[str] = []
    if change.get("hp") and change.get("room_changed"):
        was, now = change["hp"]
        moved = ("down" if now < was else "up") + f" {abs(now - was)}"
        rows.append(f"- HP {was} → {now}"
                    + (f" (of {change['max_hp']})" if change.get("max_hp")
                       else "")
                    + f", {moved}")
    # 2026-09-26 (control seat, Defect): "Treasure chest gold was never
    # itemized (55 -> 101)." Gold is said wherever it moved.
    if change.get("gold"):
        was, now = change["gold"]
        rows.append(f"- Gold {was} → {now}, "
                    + ("down" if now < was else "up") + f" {abs(now - was)}")
    rows += _deck_move_lines(change)
    if not rows:
        return out
    out += ["", "## Since the screen before this one", ""] + rows
    if change.get("hp") and change.get("room_changed"):
        # `EB-676`, THE BRIDGE HALF. The note above says a figure read the
        # instant a fight ends may not have settled yet. The bridge now ANSWERS
        # that question -- `player.hp_settled`, true only when no action is
        # executing and no dead combat is still standing in its own teardown
        # (`gits/GitsSettledHp.cs`) -- so where both of the two reads this
        # block subtracts say settled, the move is a real move and the hedge
        # comes off. `run_change` folds the pair into one boolean and answers
        # false where the bridge is older than the field, so the page in front
        # of an unpatched bridge reads exactly as it did.
        if not change.get("hp_settled"):
            out += ["", HP_SETTLE_NOTE]
    return out


def _deck_move_lines(change: dict[str, Any]) -> list[str]:
    """2026-09-26 (control seats, all four): a transform, an event's random
    upgrade or downgrade, and a curse reached the deck with nothing said.
    The run's own deck, read before and after, names what moved."""
    out = [f"- In your deck, **{was}** became **{now}**."
           for was, now in change.get("deck_became") or []]
    out += [f"- Joined your deck: **{title}**" + (f" — {text}" if text else "")
            for title, text in change.get("deck_gained") or []]
    if change.get("deck_lost"):
        out.append("- Left your deck: " + ", ".join(
            f"**{title}**" for title in change["deck_lost"]))
    # And Fairy in a Bottle firing (control seat, Defect): nothing said it had.
    out += [f"- **{name}** left your belt. You never use it yourself: the "
            f"game uses it when its text comes true." for name in
            change.get("potions_fired") or []]
    return out


#: 2026-09-28 (Kokomi seat): the bridge's `game_over.result`, said in words.
_RUN_RESULT = {"victory": ". You WON the run.",
               "defeat": ". You LOST the run."}


# ------------------------------------------- 2026-10-05: the seat-page pass -
#
# Three additions to the combat page, each a fact a sighted player has and
# the page did not, none of them a recommendation:
#
# - the ENEMY BRIEFING (`blindplay_enemies`): what each kind of enemy here
#   does, base-game facts, on round 1. Each row is a gloss, so the brief page
#   keeps it the first time a lane is shown it and cuts it after;
# - the INCOMING line: the attack telegraphs summed against your Block, with
#   the parts the page cannot count named as unknown. No lethal, no plan;
# - the SINCE-LAST-PAGE line: what the ledger filed that no other line shows
#   (a card drawn by an effect, a debuff Artifact negated, an enemy power that
#   fired, a stolen card given back), only what is new since the lane's last
#   page (`events_after`, set by the printing door), omitted when empty.

#: What a debuff move does, beside its telegraph (`blindplay_moves`).
INTENT_EFFECT_CLAUSE = "the move: {effect}"
#: The heading over the enemy briefing.
BRIEFING_HEADING = "## What these enemies do (base game)"
#: The incoming-attacks line. A sum of the telegraphs, never a plan.
INCOMING_LINE = ("- Incoming this turn: {total} (your Block {block}): you "
                 "would take {take}.")
#: SEAT PAGE 4 (2026-10-05): the HP that leaves, beside the take. The effort
#: test's seats at every effort level read "you would take 12" and took it
#: without weighing their HP (review/records/sonnet-effort-test-2026-10-05.md).
INCOMING_LEAVES = " You would be at {after}/{max_hp} HP."
INCOMING_UNKNOWN = ("- Incoming this turn: {total} plus an unknown amount "
                    "from {who} (your Block {block}).")
INCOMING_NONE = "- Incoming this turn: no attack is shown."
#: SEAT PAGE 6: no attack, but the end of the turn hurts (Burn, Constrict).
INCOMING_NO_ATTACK_TAKE = ("- Incoming this turn: no attack is shown "
                           "(your Block {block}): you would take {take}.")
#: SEAT PAGE 4: beside the rest site's HP, how much healing can land.
REST_ROOM = " (healing stops at max HP: at most {room} more)"
#: The since-last-page line, and how many phrases it names before it counts.
EVENTS_HEAD = "- Since last page: "
EVENTS_CAP = 8
#: SEAT PAGE 3 (2026-10-05). An attack that Shattered Frozen: the after-state
#: shows only "no Frozen", and a seat read the enemy's next full hit as
#: Frozen's cut failing (`FrozenPower.AfterDamageReceived`).
EVENT_SHATTERED = "{card} Shattered {target}: Frozen removed"
#: The curtain call, on the first page after the fight (Furina's drained HP
#: comes back when combat ends; seats could not tell it had).
EVENT_HP_RETURNED = "Drained {n} HP returned (the fight ended)"
#: THE SPEND ROUND (2026-10-10): the curtain call also names what did NOT
#: come back, the HP drained past the line and not Repaid; and under A
#: Five-Century Act, how much of the return was past the line.
EVENT_HP_RETURNED_LOST = ("Drained {n} HP returned; {lost} past your line "
                          "lost (the fight ended)")
EVENT_HP_RETURNED_PAST = "Drained {n} HP returned, {past} of it past your line"
#: The Varka payoff round (2026-10-10). Wolfpack firing: the copy goes into
#: the draw pile, where no other line of the page shows it arrive.
EVENT_WOLFPACK = ("Wolfpack shuffled {n} of Four Winds' Ascension into your "
                  "draw pile (it Exhausts when played)")
#: And under Twin Gales, what each Swirl paid ("Numbers held"; a line, not a
#: rule): `{paid}` is the mod's own words, `VarkaOath.TwinGalesPaid`.
EVENT_SWIRL_PAID = "Twin Gales: the Swirl of {element} on {target} paid {paid}"
#: SEAT PAGE 3: enemy powers whose firing is NOT news. Each fires on every
#: card or hit, or every turn, and what it did is already on the page (a
#: Strength, a Block, a damage figure): "Slippery fired x2" on a single hit
#: confused a seat. Matched on the power's printed name. A one-off trigger
#: (Crab Rage, Reattach, Hard To Kill's cap) is not here and still prints.
PASSIVE_ENEMY_POWERS = frozenset({
    "slow", "slippery", "thorns", "plating", "ritual", "territorial",
    "enrage", "personal hive", "skittish", "paper cuts", "flutter",
})


def _briefing_lines(enemies: list[dict[str, Any]],
                    shown: set[str] | frozenset[str] = frozenset()
                    ) -> list[str]:
    """One gloss per KIND of enemy on the board that the table knows, named
    as the enemy list names its first body (the `(n)` off). A kind in
    `shown` (its `brief_key`) was briefed earlier in this fight."""
    rows: list[str] = []
    seen: set[str] = set()
    for e in enemies:
        text = e.get("briefing") or ""
        if not text or text in seen or e.get("brief_key") in shown:
            continue
        seen.add(text)
        name = re.sub(r"\s*\(\d+\)$", "", str(e.get("name") or "")).strip()
        rows.append(f"*{name or 'This enemy'}* — {text}")
    return ["", BRIEFING_HEADING, ""] + rows if rows else []


def _attack_part_total(intent: dict[str, Any], weak: int,
                       vulnerable: int) -> int | None:
    """What one attack part adds up to, or `None` where the page cannot say.

    The game's own breakdown first: it folds Strength, Weak and Vulnerable.
    Without one, the icon's `N` or `NxM` -- and `None` where Weak or
    Vulnerable stands, because that label may or may not count them
    (`INTENT_FOLD_NOTE`)."""
    breakdown = intent.get("breakdown") or {}
    if breakdown.get("repeats"):
        total = breakdown.get("total")
        if isinstance(total, int):
            return total
        return int(breakdown.get("folded") or 0) * int(breakdown["repeats"])
    label = str(intent.get("label") or "").strip()
    multi = _MULTI_HIT_LABEL.match(label)
    if multi:
        value = int(multi.group(1)) * int(multi.group(2))
    elif label.isdigit():
        value = int(label)
    else:
        return None
    if weak or vulnerable:
        return None
    return value


#: SEAT PAGE 6 (2026-10-05): what stands between the telegraphs and your HP
#: and lands before the enemies act. Base-game Sonnet seats read "you would
#: be at 0" and lived (Osty, Beating Remnant, Frost), or the reverse (Burn,
#: Disintegration). The order is the game's (`CombatManager.DoTurnEnd`):
#: end-of-turn Block first (Orichalcum, Plating, then the orbs), then the
#: cards in hand, then the end-of-turn powers, then the enemies. Block lasts
#: until YOUR next turn starts, so all of it meets all of the damage.
INCOMING_FOLDS = " ({folds})"
INCOMING_NOT_COUNTED = " Not counted: {names}."
FOLD_BLOCK = "{who} {verb} {n} Block first"
FOLD_SELF_HIT = "{who} {verb} you for {n} first"
FOLD_SELF_HP = "{who} {verb} {n} HP"
FOLD_OSTY = "{name} absorbs up to {hp}"
FOLD_CAP = "{name} caps the turn's HP loss at {cap}"
#: A hand card that hurts at the end of the turn, by its own sentence
#: (Burn, Decay, Toxic, Infection, Wither: Block takes it; Bad Luck, Beckon:
#: it is HP lost). Regret's number is the hand size, so it is named.
_IN_HAND_EOT = re.compile(r"end of (?:your |the )?turn,? if this is in your "
                          r"hand", re.I)
_TAKE_DAMAGE = re.compile(r"\btake (\d+) damage", re.I)
_LOSE_HP = re.compile(r"\blose (\d+) HP", re.I)
#: Player debuffs that hit at the end of the turn, by printed name. Block
#: takes the first set (`ConstrictPower`, `DisintegrationPower`,
#: `MagicBombPower`); the second is HP lost (`DemisePower`, Unblockable).
EOT_HIT_POWERS = ("constrict", "constricted", "disintegration", "magic bomb")
EOT_HP_POWERS = ("demise",)
#: Player powers that gain Block at the end of the turn, by printed name: the
#: stack count is the Block (`PlatingPower`).
EOT_BLOCK_POWERS = ("plating", "plated armor", "metallicize")
#: Varka round 3 (2026-10-10): any other power of yours whose hover text
#: gains Block at the end of your turn. A plain "gain N Block" in that
#: sentence is folded; a conditional or computed one ("if", "equal to") is
#: named under "Not counted", the way relics are.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_PLAIN_GAIN_BLOCK = re.compile(r"\bgain (\d+) Block\b", re.I)
_ANY_GAIN_BLOCK = re.compile(r"\bgain\b[^.]*\bBlock\b", re.I)
_CONDITIONAL_BLOCK = re.compile(
    r"\b(?:if|unless|otherwise|equal to|for each|per|up to|instead)\b", re.I)


def _power_eot_block(text: str) -> int | None:
    """The plain Block a power's text gains at the end of your turn: N, or
    0 where it gains none then, or None where it gains some the page cannot
    count."""
    found = 0
    for sentence in _SENTENCE_SPLIT.split(text):
        if not _END_OF_TURN.search(sentence) \
                or not _ANY_GAIN_BLOCK.search(sentence):
            continue
        plain = _PLAIN_GAIN_BLOCK.search(sentence)
        if plain is None or _CONDITIONAL_BLOCK.search(sentence):
            return None
        found += int(plain.group(1))
    return found


#: Player powers that change what a hit costs, which this line does not
#: model: named, never counted.
HIT_RULE_POWERS = ("intangible", "buffer")
#: A relic's sentence for end-of-turn Block with no Block up (Orichalcum).
_NO_BLOCK_RELIC = re.compile(
    r"end (?:of )?your turn without (?:any )?Block, gain (\d+) Block", re.I)
#: And Block per card in hand (Cloak Clasp).
_PER_CARD_RELIC = re.compile(
    r"end of your turn, gain (\d+) Block for each card in your hand", re.I)
#: Beating Remnant: "You cannot lose more than 20 HP in a single turn."
_HP_LOSS_CAP = re.compile(r"lose more than (\d+) HP", re.I)
#: SEAT PAGE 7 (2026-10-05): Kokomi's waiting Dusk Plans, which the
#: Bake-Kurage carries out at the end of this turn, before the enemies act
#: (`ProtoBakeKuragePower.BeforeSideTurnEnd`). Counted only off the entry's
#: own Plan text on the wire (`plan_line`, numbers filled); an entry with no
#: text, or whose Block the page cannot count (Double your Block), is named.
DUSK_FOLD_NAME = "{name} (Dusk Plan)"
_DUSK_FLAT_BLOCK = re.compile(r"^Gain (\d+) Block\.?$", re.I)
#: Breakwater: the count is the queue left once the Dusk entries are out.
_DUSK_PER_PLAN = re.compile(
    r"^Gain (\d+) Block, and (\d+) more for each Plan waiting\.?$", re.I)
#: Evening Watch: the living enemies with an attack shown.
_DUSK_PER_ATTACKER = re.compile(
    r"^Gain (\d+) Block for each enemy intending to attack\.?$", re.I)


def _plain_name(title: Any) -> str:
    """A hand face's printed title without the page's `(n)` or the `+`."""
    name = re.sub(r"\s*\(\d+\)$", "", str(title or "")).strip()
    return name.rstrip("+").strip()


def _named_sum(parts: list[tuple[str, int]]) -> tuple[str, int, bool]:
    """`(who, n, plural)` for one clause: `Frost x2 and Plating`, 8."""
    counts: dict[str, int] = {}
    for name, _n in parts:
        counts[name] = counts.get(name, 0) + 1
    who = _and_list([f"{k} x{v}" if v > 1 else k for k, v in counts.items()])
    return who, sum(n for _name, n in parts), len(parts) > 1


def _dusk_block_number(text: str, morning: int, attackers: int) -> int | None:
    """One Dusk entry's Block off its Plan text, 0 where it gives no Block,
    `None` where the page cannot count it."""
    text = re.sub(r"^.*\bplan:\s*", "", text.strip(), flags=re.I | re.S)
    if not text:
        return None
    found = _DUSK_FLAT_BLOCK.match(text)
    if found:
        return int(found.group(1))
    found = _DUSK_PER_PLAN.match(text)
    if found:
        return int(found.group(1)) + int(found.group(2)) * morning
    found = _DUSK_PER_ATTACKER.match(text)
    if found:
        return int(found.group(1)) * attackers
    return None if re.search(r"\bBlock\b", text, re.I) else 0


def _dusk_facts(plans: dict[str, Any] | None,
                enemies: list[dict[str, Any]]
                ) -> tuple[list[tuple[str, int]], list[str]]:
    """The waiting Dusk Plans' Block: `(counted, named)`. Nereid's Ascension
    carries the first Dusk entry out twice (`KokomiPlan.Drain`)."""
    queue = (plans or {}).get("queue") or []
    morning = sum(1 for e in queue if not _is_dusk(e))
    attackers = sum(1 for e in enemies
                    if not e.get("phase_flip")
                    and not (isinstance(e.get("hp"), int) and e["hp"] <= 0)
                    and any(_fold(i.get("type")) == "attack"
                            for i in e.get("intents") or []))
    counted: list[tuple[str, int]] = []
    named: list[str] = []
    first = True
    for entry in queue:
        if not _is_dusk(entry):
            continue
        name = DUSK_FOLD_NAME.format(
            name=str(entry.get("name") or "")[len(_DUSK_MARK):])
        n = _dusk_block_number(str(entry.get("plan_line") or ""), morning,
                               attackers)
        times = 2 if first and (plans or {}).get("twice") else 1
        first = False
        if n is None:
            if name not in named:
                named.append(name)
        elif n > 0:
            counted += [(name, n)] * times
    return counted, named


def _turn_end_facts(you: dict[str, Any], hand: list[dict[str, Any]],
                    pets: list[dict[str, Any]],
                    dusk: tuple[list[tuple[str, int]], list[str]] = ([], [])
                    ) -> dict[str, Any]:
    """What lands between the end of your turn and the enemies' hits, off the
    wire's own numbers, as if the turn ended now; what the page cannot count
    goes in `unknown`, by name. SEAT PAGE 7: `dusk` is `_dusk_facts`'s."""
    block_parts: list[tuple[str, int]] = list(dusk[0])
    hit_parts: list[tuple[str, int]] = []
    hp_parts: list[tuple[str, int]] = []
    unknown: list[str] = list(dusk[1])
    block_now = int(you.get("block") or 0)
    cap = None
    for relic in you.get("relics") or []:
        name, text = str(relic.get("name") or ""), str(relic.get("text") or "")
        found = _HP_LOSS_CAP.search(text)
        if found:
            cap = (name, int(found.group(1)))
            continue
        found = _NO_BLOCK_RELIC.search(text)
        if found:
            if block_now == 0 and dusk[0]:
                # Whether the Dusk Block lands before this relic looks is
                # not on the page: named, never counted.
                unknown.append(name)
            elif block_now == 0:
                block_parts.append((name, int(found.group(1))))
            continue
        found = _PER_CARD_RELIC.search(text)
        if found:
            if hand:
                block_parts.append((name, int(found.group(1)) * len(hand)))
            continue
        # Any other relic that gives Block at the end of the turn (Ripple
        # Basin: only if no Attack was played, which the wire does not say).
        if _END_OF_TURN.search(text) and re.search(r"\bgain \d+ Block", text,
                                                    re.I):
            unknown.append(name)
    for power in you.get("powers") or []:
        key, stacks = _fold(power.get("name")), power.get("stacks")
        name = str(power.get("name") or "")
        if key in HIT_RULE_POWERS:
            unknown.append(name)
            continue
        if key not in EOT_BLOCK_POWERS + EOT_HIT_POWERS + EOT_HP_POWERS:
            # Its hover text says the number it gains, the stacks in it.
            gained = _power_eot_block(str(power.get("text") or ""))
            if gained is None:
                unknown.append(name)
            elif gained:
                block_parts.append((name, gained))
            continue
        if not isinstance(stacks, int) or stacks <= 0:
            continue
        if key in EOT_BLOCK_POWERS:
            block_parts.append((name, stacks))
        elif key in EOT_HIT_POWERS:
            hit_parts.append((name, stacks))
        elif key in EOT_HP_POWERS:
            hp_parts.append((name, stacks))
    for orb in (you.get("orbs") or {}).get("list") or []:
        if _fold(orb.get("name")) in ("frost", "frost orb") and orb.get(
                "passive"):
            block_parts.append(("Frost", int(orb["passive"])))
    for card in hand:
        name = _plain_name(card.get("title"))
        text = str(card.get("text") or "")
        # Regret: HP lost per card in hand at the end, whatever the hand
        # holds then; named, never counted.
        if _fold(name) == "regret" or (_IN_HAND_EOT.search(text)
                                       and re.search(r"\bfor each\b", text,
                                                     re.I)):
            if name not in unknown:
                unknown.append(name)
            continue
        if not _IN_HAND_EOT.search(text):
            continue
        damage, hp = _TAKE_DAMAGE.search(text), _LOSE_HP.search(text)
        if damage:
            hit_parts.append((name, int(damage.group(1))))
        elif hp:
            hp_parts.append((name, int(hp.group(1))))
        elif name not in unknown:
            unknown.append(name)
    osty = next((pet for pet in pets if pet.get("absorbs")
                 and int(pet.get("hp") or 0) > 0), None)
    return {"block": block_parts, "hit": hit_parts, "hp": hp_parts,
            "osty": osty, "cap": cap, "unknown": unknown}


def _fold_clauses(facts: dict[str, Any], absorbs: bool) -> list[str]:
    """The few words for each fact folded into the take."""
    out = []
    for key, template, one, many in (("block", FOLD_BLOCK, "adds", "add"),
                                     ("hit", FOLD_SELF_HIT, "hits", "hit"),
                                     ("hp", FOLD_SELF_HP, "costs", "cost")):
        if facts[key]:
            who, n, plural = _named_sum(facts[key])
            out.append(template.format(who=who, n=n,
                                       verb=many if plural else one))
    if absorbs and facts["osty"]:
        out.append(FOLD_OSTY.format(name=facts["osty"]["name"],
                                    hp=facts["osty"]["hp"]))
    return out


def _with_folds(line: str, clauses: list[str]) -> str:
    """`line` with its closing full stop moved after the folded facts."""
    return line[:-1] + INCOMING_FOLDS.format(folds="; ".join(clauses)) + "."


def _incoming_line(enemies: list[dict[str, Any]], you: dict[str, Any],
                   hand: list[dict[str, Any]] | None = None,
                   pets: list[dict[str, Any]] | None = None,
                   plans: dict[str, Any] | None = None) -> str:
    """`- Incoming this turn: N (your Block B): you would take T.`

    The sum of every attack part shown; a part it cannot count is named as
    unknown. SEAT PAGE 6: and what lands before the hits or stands between
    them and your HP, folded in where the wire gives the number and said in
    a few words (`_turn_end_facts`); what it cannot count is named. No plan."""
    total, unknown, any_attack = 0, [], False
    vulnerable = _stacks_of(you, "vulnerable")
    for e in enemies:
        if e.get("phase_flip") or (isinstance(e.get("hp"), int)
                                   and e["hp"] <= 0):
            continue
        weak = _stacks_of(e, "weak")
        for intent in e.get("intents") or []:
            if _fold(intent.get("type")) != "attack":
                continue
            any_attack = True
            part = _attack_part_total(intent, weak, vulnerable)
            if part is None:
                name = str(e.get("name") or "an enemy")
                if name not in unknown:
                    unknown.append(name)
            else:
                total += part
    facts = _turn_end_facts(you, hand or [], pets or [],
                            _dusk_facts(plans, enemies))
    not_counted = (INCOMING_NOT_COUNTED.format(
        names=_and_list(facts["unknown"])) if facts["unknown"] else "")
    if not any_attack and not (facts["hit"] or facts["hp"]):
        return INCOMING_NONE + not_counted
    block = int(you.get("block") or 0)
    if unknown:
        clauses = _fold_clauses(facts, absorbs=True)
        if facts["cap"]:
            clauses.append(FOLD_CAP.format(name=facts["cap"][0],
                                           cap=facts["cap"][1]))
        line = INCOMING_UNKNOWN.format(total=total, who=_and_list(unknown),
                                       block=block)
        if clauses:
            line = _with_folds(line, clauses)
        return line + not_counted
    # The game's order: end-of-turn Block, then the self-hits (Block takes
    # them), then the HP-loss ones, then the attacks. Osty takes the
    # unblocked attack damage up to his HP (`DieForYouPower`) and only the
    # rest reaches you; a cap relic stops the turn's loss at its number.
    held = block + sum(n for _name, n in facts["block"])
    self_hit = sum(n for _name, n in facts["hit"])
    lost = max(0, self_hit - held) + sum(n for _name, n in facts["hp"])
    held = max(0, held - self_hit)
    unblocked = max(0, total - held)
    absorbs = bool(facts["osty"]) and unblocked > 0
    if absorbs:
        unblocked = max(0, unblocked - int(facts["osty"]["hp"]))
    take = lost + unblocked
    clauses = _fold_clauses(facts, absorbs)
    if facts["cap"] and take > facts["cap"][1]:
        take = facts["cap"][1]
        clauses.append(FOLD_CAP.format(name=facts["cap"][0],
                                       cap=facts["cap"][1]))
    if any_attack:
        line = INCOMING_LINE.format(total=total, block=block, take=take)
    else:
        line = INCOMING_NO_ATTACK_TAKE.format(block=block, take=take)
    if clauses:
        line = _with_folds(line, clauses)
    if take and isinstance(you.get("hp"), int) and you.get("max_hp"):
        line += INCOMING_LEAVES.format(after=max(0, you["hp"] - take),
                                       max_hp=you["max_hp"])
    return line + not_counted


#: SEAT PAGE 3: the end-of-turn acts' Block, beside the incoming line on a
#: stage board. Sigewinne's line gives Block for every Repay, and an act or
#: the Singer may Repay at the end of the turn, before the enemies act.
INCOMING_STAGE_BLOCK = (" Your guests' end-of-turn acts come first and may "
                        "add Block (Sigewinne).")
INCOMING_STAGE_BLOCK_FIXED = (" Your guests' end-of-turn acts come first and "
                              "add {n} Block.")


def _stage_block_clause(stage: dict[str, Any] | None) -> str:
    """What the stage may add to her Block before the enemies act, or `""`.
    The forecast's own figure where it sends one; else Sigewinne on stage is
    named, because her line turns a Repay into Block and the page cannot
    count a Repay's size before it lands."""
    if not stage:
        return ""
    forecast = stage.get("forecast") or {}
    after = forecast.get("block") or stage.get("act_block") or 0
    if after:
        return INCOMING_STAGE_BLOCK_FIXED.format(n=after)
    if any(row.get("member") == "sigewinne"
           for row in stage.get("seats") or []):
        return INCOMING_STAGE_BLOCK
    return ""


def _event_phrases(kind: str, evs: list[dict[str, Any]]) -> list[str]:
    """The phrases for one kind of event, repeats counted."""
    counted: dict[tuple, int] = {}
    for ev in evs:
        key = (ev["card"], ev["target"], ev["power"], ev["source"],
               bool(ev.get("on_player")))
        counted[key] = counted.get(key, 0) + 1
    out: list[str] = []
    if kind == "drawn":
        by_source: dict[str, list[str]] = {}
        for (card, _t, _p, source, _o), n in counted.items():
            by_source.setdefault(source, []).append(
                card + (f" x{n}" if n > 1 else ""))
        for source, cards in by_source.items():
            out.append(f"drew {_and_list(cards)}"
                       + (f" ({source})" if source else ""))
        return out
    if kind == "curtain":
        total = sum(int(ev.get("amount") or 0) for ev in evs)
        lost = sum(int(ev.get("lost") or 0) for ev in evs)
        past = sum(int(ev.get("past") or 0) for ev in evs)
        if lost > 0:
            return [EVENT_HP_RETURNED_LOST.format(n=total, lost=lost)]
        if total <= 0:
            return []
        if past > 0:
            return [EVENT_HP_RETURNED_PAST.format(n=total, past=past)]
        return [EVENT_HP_RETURNED.format(n=total)]
    if kind == "wolfpack":
        total = sum(int(ev.get("amount") or 0) for ev in evs)
        if total <= 0:
            return []
        return [EVENT_WOLFPACK.format(
            n="a copy" if total == 1 else f"{total} copies")]
    for (card, target, power, _s, on_player), n in counted.items():
        times = f" x{n}" if n > 1 else ""
        if kind == "negated":
            out.append((f"your Artifact negated {power}" if on_player
                        else f"Artifact negated {power} on {target}") + times)
        elif kind == "triggered":
            if power.strip().casefold() in PASSIVE_ENEMY_POWERS:
                continue
            out.append(f"{target}'s {power} fired{times}")
        elif kind == "returned":
            out.append(f"{card} came back to your deck from {target}")
        elif kind == "shattered":
            out.append(EVENT_SHATTERED.format(card=card or "an attack",
                                              target=target) + times)
        elif kind == "paid":
            out.append(EVENT_SWIRL_PAID.format(
                element=card or "an aura", target=target or "an enemy",
                paid=power) + times)
    return out


def _events_lines(events: list[dict[str, Any]], after: int) -> list[str]:
    """`- Since last page: ...`, or nothing. The events with `seq` past
    `after`, grouped by kind in the order each kind first happened, capped."""
    fresh = [ev for ev in events if int(ev.get("seq") or 0) > after]
    kinds: list[str] = []
    for ev in fresh:
        if ev["kind"] not in kinds:
            kinds.append(ev["kind"])
    phrases: list[str] = []
    for kind in kinds:
        phrases += _event_phrases(kind, [e for e in fresh
                                         if e["kind"] == kind])
    if not phrases:
        return []
    if len(phrases) > EVENTS_CAP:
        phrases = phrases[:EVENTS_CAP] + [
            f"and {len(phrases) - EVENTS_CAP} more"]
    return [EVENTS_HEAD + "; ".join(phrases) + "."]


def newest_event(obs: dict[str, Any]) -> int:
    """The highest event `seq` on a combat observation, else 0. The printing
    door records it so the next page prints only what came after."""
    combat = obs.get("combat") or {}
    rows = combat.get("events") or obs.get("events") or []
    return max((int(ev.get("seq") or 0) for ev in rows), default=0)

def render(obs: dict[str, Any]) -> str:
    """The observation as the page the tester is handed. Same content."""
    st = obs["state_type"]
    if obs["blocked"]:
        body = [f"TOOL-BLOCKED: {st}", "", obs["blocked"]]
        if obs["screen"] == "game_over":
            result = obs["result"]
            body += ["", f"The run ended on floor {obs['floor']}"
                         + _RUN_RESULT.get(result.lower(),
                                           f": {result}" if result else ".")]
            if obs.get("summary"):
                body += ["", "What the run ended with:", ""] + obs["summary"]
        # CO-OP: the other player's side of the same ending. Absent on every
        # singleplayer page.
        if obs.get("coop"):
            body += coop_lines(obs["coop"])
        # `EB-396`: and where the blocked screen has a way OUT, the page ends
        # on the command that takes it. A blocked page that printed no verb
        # was the whole defect -- the seat had nothing to type and the run
        # stopped on a screen rather than on a board.
        if obs.get("commands"):
            body += ["", "What you can say here:", ""] \
                + [f"- `{c}`" for c in obs["commands"]]
        text = "\n".join(body) + "\n"
        qa_packet.assert_blind(text, allow={st})
        return text

    # CO-OP: what the run is waiting on, first, where a reader looks first.
    # Nothing on a singleplayer page, which has no `coop` key.
    out: list[str] = coop_banner(obs.get("coop"))
    # SEAT PAGE 3: what happened since the last page where no fight is up to
    # print it (the curtain call, on the reward screen). Printed only through
    # a printing door, which sets `events_after`.
    if obs["screen"] != "combat" and "events_after" in obs:
        said = _events_lines(obs.get("events") or [], obs["events_after"])
        out += said + ([""] if said else [])
    if obs["screen"] == "combat":
        c = obs["combat"]
        you = c["you"]
        out += [f"# Battle — round {c['round']}", "",
                f"- HP {you['hp']}/{you['max_hp']}",
                f"- Block {you['block']}",
                f"- Energy {you['energy']}/{you['max_energy']}"]
        out += _stars_line(you)
        defined = {row["name"] for row in (obs.get("keywords") or [])}
        spark_named = False
        for name, amount in sorted(you["meters"].items()):
            # `EB-181`: with a ceiling the row reads like the HP and Energy
            # rows above it and the note narrows to the half still true; with
            # none it is exactly the row it always was.
            top = you.get("meter_max", {}).get(name)
            # `EB-382`: where the MOD declares a spend rule the feed cannot
            # carry, the row prints the rule instead of the sentence saying
            # there is none. The ceiling half is unchanged either way, because
            # a maximum and a spend rule are two different facts and this table
            # answers only the second.
            rule = METER_RULES.get(name)
            # `EB-407`: and where the GLOSSARY defines the same word on this
            # screen, the meter line points at it instead of printing a second
            # copy. One definition per screen is `keyword_notes`' own rule and
            # the meters block was the one place two sources could both fire.
            if name in defined:
                rule = METER_DEFINED_NOTE
            # `EB-560`. THE OPENING RULE, ONCE, ON THE FIRST SCREEN OF A
            # FIGHT. "Where Spark comes from is not on the combat screen. I
            # opened fight 1 with 1 and could not tell whether that was a
            # starting bank, a relic, or something a card had done" (Klee r20
            # lane 2, (c) 3).
            #
            # ROUND ONE ONLY, which is what makes it the OPENING rule: on round
            # 4 the bank is the sum of everything since, and a page still
            # saying "you started with 1" would answer a question nobody is
            # asking. A `METER_RULES` row would print on every round and is the
            # wrong home for the same reason.
            #
            # IT OVERRIDES THE GLOSSARY POINTER RATHER THAN DEFERRING TO IT,
            # and `EB-407` is not breached: the page's own `Spark` row says
            # what the word means ("cards cost Sparks instead of Energy") and
            # not where this bank came from, because that row is printed on
            # every arm and the opening grant is Klee's. Two facts, one screen,
            # neither a second copy of the other.
            #
            # KLEE'S ARM AND NOT THE BOARD, `_zero_meters`' own question one
            # block up: the meter is registered for every seat at the table.
            if (name == "Spark" and c["round"] == 1
                    and _fold(obs.get("character") or "") == "klee"):
                rule = spark_opening_rule(opening_spark(obs))
            # `EB-568`: the floor is a CLAUSE on this row, not a row. The
            # r14 lane-2 seat met `Fanfare Floor 8` and `Fanfare Cap Bonus 8`
            # as two unexplained meters beside a Fanfare that had sat at 8 for
            # three fights, and had no route from either number to the card
            # that bought them. The cap bonus needs no clause: it is already
            # inside the `/{top}` this row prints, which is the honest place
            # for a number whose whole meaning is how much of the maximum was
            # bought.
            floor = (you.get("fanfare_parts") or {}).get("floor")
            bound = (f", and it cannot fall below {floor}"
                     if name == "Fanfare" and floor else "")
            if top:
                out.append(f"- {name}: {amount}/{top}{bound} — "
                           f"{rule or METER_CAPPED_NOTE}")
            else:
                out.append(f"- {name}: {amount}{bound} — "
                           f"{rule or METER_NOTE}")
            # `EB-610`. AND WHERE THIS TURN'S SPARKS CAME FROM, under the row
            # they moved. Klee r23 lane 2 watched the bank go 2 to 3 across
            # Kaeya and Rapid Fire on a BARE BOARD, while the only sentence
            # naming a Spark source anywhere on the screen is the relic's
            # "whenever a Bomb goes off" -- so the meter contradicted the one
            # rule the reader had, and nothing could settle it.
            #
            # A SUB-LINE AND NOT A CLAUSE ON THE ROW, `ENEMY_REPLACED_LINE`'s
            # shape: the row above says what the meter IS, which is true on
            # every turn, and this says what it DID this turn, which is a
            # different fact with a different lifetime. Printed only where
            # there is something to say -- a turn with no gain prints nothing,
            # because a reader asking "where did that come from" is only ever
            # asking about a number that moved.
            if name == "Spark" and c.get("spark_sources"):
                out.append("    - " + _spark_sources_line(c))
                spark_named = True
        for pw in _once(you["powers"]):
            out.append(_render_power(pw, "- "))
            # `EB-610`, THE OTHER SHAPE SPARK ARRIVES IN. The clause above is
            # emitted inside the METERS loop, and the live look of 2026-09-16
            # read a build whose wire carried Spark POWER-shaped -- a
            # `Spark 3 (buff)` status row with `combat["meters"]` empty -- so
            # the sources rode the wire, folded correctly, and were printed
            # nowhere. The fact belongs beside the number it explains,
            # whichever row that number is on; `spark_named` keeps it to ONE
            # copy on a build that sends both shapes.
            if (not spark_named and c.get("spark_sources")
                    and _fold(pw.get("name")) == "spark"):
                out.append("    - " + _spark_sources_line(c))
                spark_named = True
        status = c.get("pile_status") or {}
        out.append(f"- Piles: {c['piles']['draw']} in the draw pile"
                   f"{_status_clause(status.get('draw'))}, "
                   f"{c['piles']['discard']} discarded"
                   f"{_status_clause(status.get('discard'))}, "
                   f"{c['piles']['exhaust']} exhausted")
        out += _orb_lines(you.get("orbs"))
        out += _ally_lines(c.get("pets") or [])
        # 2026-10-05: what happened since the last page that no other line
        # shows. Omitted when there is nothing.
        out += _events_lines(c.get("events") or [],
                             int(c.get("events_after") or 0))
        # `EB-238`. IN THE HEADER, with HP and Energy, because that is where
        # the game keeps it: the relic row sits along the top of every screen
        # of a run, and a reader who is shown it only when one is OFFERED has
        # been shown the shop and not the board.
        if you["relics"]:
            out += ["", "## Your relics", ""] + [
                f"- **{r['name']}**"
                + (f" ({_relic_counter(r)})" if r.get("counter") else "")
                + (RELIC_USED_UP if r.get("used_up") else "")
                + (f" — {r['text']}" if r["text"] else "")
                for r in you["relics"]]
            # `EB-349`: and where one of them has already taken this turn, the
            # line saying so -- under the relic row, because it is that
            # relic's sentence being applied to the board above.
            out += _auto_turn_note(you, c["round"])
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
            # 2026-09-28 (Kokomi seat): the Casket's count, where the Plans
            # that fill it are read. It was only the relic row's "(N)", and a
            # seat timing Open the Casket read the Plan block and never saw it.
            out += _casket_count_line(you)
            if pl["pet"]:
                out.append(f"- The {pl['pet_name']} is on the field for the "
                           "whole fight. Enemies cannot touch it. Play a card "
                           "on it to write its **Plan** line instead of "
                           "playing the card now.")
                # `EB-442`: WHERE a Plan lands, then `EB-378`'s whose hit
                # it is -- both under the pet's own line, because both are
                # facts about the jellyfish's carry-out rather than about any
                # one Plan in the queue below. The aim rule leads: a reader
                # asking what a Plan will do asks which body first.
                out.append(PLAN_AIM_NOTE)
                # `EB-433`: and the exception the starter relic makes to it,
                # appended to the sentence it is an exception to.
                out.append(PLAN_HYDRO_NOTE + _casket_aura_clause(you))
                # `EB-411`: and what the hit meets when it gets there -- the
                # enemy's own Block, which YOUR turn start does not clear and
                # which no play of yours can strip before the morning.
                out.append(PLAN_BLOCK_NOTE)
                # `EB-653`: the count rule this BUILD is under. Under a
                # declared cap the wire's own sentence replaces "not a
                # limit", which the cap makes false.
                out.append(_plan_count_note(you))
                # `EB-647`: and that the numbers in that queue are FIXED --
                # written with her terms folded in, and untouched by anything
                # that lands on her afterwards.
                out.append(PLAN_WRITTEN_NUMBER_NOTE)
                # `EB-578`. AND WHEN THE HAND HOLDS NONE, one line saying so.
                # The form under *What you can say* is gone on such a turn
                # (`blindplay_observe`), and a form that disappears with no
                # sentence in its place reads as a page that forgot it -- so
                # the absence is stated where the jellyfish is described. The
                # flag is only ever set on a build whose bridge answers
                # `can_target_pet`, so an older feed prints neither this line
                # nor a missing form.
                if pl.get("plannable") is False:
                    out.append("- No Plan card in hand: the jellyfish waits.")
            # `EB-317`. WHAT ALREADY HAPPENED, BEFORE WHAT IS STILL WAITING,
            # because that is the order the turn had: the morning's Plans were
            # carried out at the top of this turn and the queue below is what
            # the player has written since. Each line is the mod's own string
            # -- the words the speech bubble put over the jellyfish's head --
            # printed verbatim, which is the whole point of the field. The
            # meter ledger is NOT here and must not be (`R101b`): this is what
            # a sighted player saw, not an instrument's rows.
            #
            # `EB-329` splits the block in THREE, in the order the turn had
            # them: what the morning did, what fired mid-turn as it was
            # written, and what is still waiting. And each Plan now carries
            # what the BOARD did under it, which is the row's own headline --
            # the line's own figure is its first clause's and a reader who
            # took it for the damage got `Exposed Flank, 2` for a beat that
            # moved 3.
            out += _render_carry_out(pl)
            if not pl["queue"]:
                out.append("- Nothing is planned. Nothing will be carried "
                           "out at the start of your next turn.")
            else:
                # `EB-680`: the queue is ONE queue and two of its entries
                # land at different moments, so the line that says WHEN says
                # it per entry rather than once for all of them. The Dusk
                # clause rides the entry's own row, where a reader deciding
                # whether to write another one is looking.
                out.append(
                    f"- Planned, and carried out at the start of your next "
                    f"turn in this order ({pl['pending']}):")
                # `EB-773`: and which of them is written at a body the Plans
                # ahead of it will already have killed.
                past_lethal = _past_lethal_clauses(pl, c.get("enemies") or [])
                for i, e in enumerate(pl["queue"], 1):
                    out.append(f"  {i}. **{e['name']}**"
                               + (" — Dusk: this one is carried out at the "
                                  "END of this turn instead, before the "
                                  "enemies act" if _is_dusk(e) else "")
                               + past_lethal.get(i - 1, ""))
                    # A PLAN STAYS OPEN (2026-10-01), pick 5 (a): both
                    # lines while it waits, the one it will be carried out
                    # as first, and the verb that flips it.
                    if e.get("two_line") and (e.get("now_line")
                                              or e.get("plan_line")):
                        now = e.get("line") == "now"
                        out.append("     - " + TWO_LINE_WAITING_ROW.format(
                            line="now-line" if now else "Plan line",
                            this=e["now_line"] if now else e["plan_line"],
                            other_name="Plan line" if now else "Now-line",
                            other=e["plan_line"] if now else e["now_line"],
                            n=i))
                if pl["twice"]:
                    # 2026-09-28 (Kokomi seat): with a Dusk Plan in the
                    # list above, "your FIRST Plan" read as entry 1. The Rare
                    # doubles the first entry of EACH drain
                    # (`KokomiPlan.Drain`): the morning's and the Dusk's.
                    out.append("- Nereid's Ascension: the jellyfish carries "
                               "out your FIRST Plan twice at the start of "
                               "your turn, and your first Dusk Plan twice "
                               "at the end of it.")
            # `EB-329`: which of the two numbers under a Plan is which, once,
            # at the foot of the section rather than under the last card.
            if _board_note_wanted(pl):
                out += ["", CARRY_OUT_BOARD_NOTE]
        # `EB-735`. THE STAGE, ABOVE EVERYTHING IT DECIDES. Three round-one
        # seats played some 550 actions without ever knowing who was on stage
        # or what a bar held, because the page had no renderer for her
        # performers; the block below is that renderer, and it goes here --
        # under the header and above the hand -- because her Fanfare (the
        # re-founding, 2026-10-04: one number on Furina) is the price of half
        # the cards in the hand underneath.
        if c.get("stage") is not None:
            out += ["", "## Your stage", ""]
            out += _render_stage(c["stage"], you)
            if c["stage"]["log"]:
                out.append(STAGE_LOG_HEADING)
                out += _render_stage_log(c["stage"])
        # `EB-506`. WHO IS AT THE FRONT, printed as a LIST IN ORDER with the
        # front marked, and refreshed off the live company on every screen.
        #
        # "I could never tell who the front member was ... after doing exactly
        # that in fight 3 the line still named the Usher. With two members up I
        # was guessing which one my next Companion card would fire" (Furina r11
        # lane 1, (c) 4). The stage buff's face is a smart description keyed on
        # the front member, so it is a registered row redrawn when the game
        # feels like it; the company is a live list and its head IS the answer.
        #
        # ITS OWN SECTION, above what the stage DID this turn, because the
        # order is a fact about the board now and the performances are a
        # receipt for what has already happened -- and because the section
        # below prints only on a turn something acted, while the question "who
        # is in front" is asked on every turn including the quiet ones.
        # `EB-681`. WHAT REACTED THIS TURN, under the board that reacted and
        # above the hand -- a receipt for the beat just watched, filed where
        # the other receipts on this page are (the carry-out block, the
        # Salon's). Present and empty prints its own line, because "no line"
        # and "no reaction" were the same page to the r27 lane-1 seat.
        #
        # `EB-710`. AND THE ROWS FROM THE WINDOW NOBODY WAS SHOWN. A reaction
        # off an end-of-turn tenant, or off the enemy side, used to be cleared
        # before any page could print it -- this heading said "Nothing reacted
        # this turn" through six Electro-Charged. The mod carries those rows
        # one turn (`ReactionLog.MarkTurnStart`); they print here, marked with
        # their own window, and where they are ALL the page has, the empty
        # line is replaced by one that says both facts rather than the false
        # one.
        if c.get("reactions") is not None:
            out += ["", REACTIONS_HEADING, ""]
            rows = c["reactions"]
            if rows and all(row.get("carried") for row in rows):
                out.append(REACTION_CARRIED_ONLY)
            for row in rows:
                line = (REACTION_ROW if row["source"]
                        else REACTION_ROW_NO_SOURCE).format(**row)
                if row.get("detail"):
                    line += " " + row["detail"]
                if row.get("carried"):
                    line = line.rstrip(".") + "." + REACTION_CARRIED_CLAUSE
                line += _frozen_clause(row, obs, c)
                out.append(line)
            if not rows:
                out.append(NO_REACTION_THIS_TURN)
        # `EB-695`. AND WHAT A RELIC ANSWERED WITH, beside the reactions and
        # for the same reason: it is a thing that LANDED inside a beat whose
        # own number does not account for it. Inside a Plan carry-out the
        # rider clause names the Casket's 2; played from hand it was named
        # nowhere, and the r30 seat subtracted it from HP by hand every time.
        # Printed only where something answered -- see `RELIC_ANSWERS_HEADING`
        # for why this section has no empty line where the one above it does.
        if c.get("relic_answers"):
            out += ["", RELIC_ANSWERS_HEADING, ""]
            for row in c["relic_answers"]:
                line = (RELIC_ANSWER_GAIN_ROW if row.get("unit")
                        else RELIC_ANSWER_ROW if row["target"]
                        else RELIC_ANSWER_ROW_NO_TARGET).format(**row)
                if row.get("carried"):
                    line = line.rstrip(".") + "." + REACTION_CARRIED_CLAUSE
                out.append(line)
        # `EB-349` / `EB-611`. WHAT RESOLVED THIS TURN, beside the two receipts
        # above and for their reason: this page prints after-states, and the
        # beat that produced one was on no feed at all. A card's hits are
        # NUMBERED under it, because the order is the whole of `EB-611` -- a
        # seat could confirm which bodies a random multi-hit struck and never
        # in what order -- and the empty line prints, unlike the relic-answer
        # section, because on a turn the game played for you the empty list IS
        # the finding.
        if c.get("resolutions") is not None:
            out += ["", RESOLUTIONS_HEADING, ""]
            out += _resolution_lines(c["resolutions"],
                                     stage=c.get("stage") is not None,
                                     enemies=c.get("enemies") or [])
        if you["potions"]:
            out += ["", "## Potions", ""]
            # `EB-341`: how many slots there are, beside how many are used.
            # A tester who cannot see the denominator cannot know that the
            # next potion offered has nowhere to go.
            if you.get("potion_slots"):
                out += [f"- {len(you['potions'])} of "
                        f"{you['potion_slots']} slots are full.", ""]
            # 2026-10-01 (a Varka seat): `use potion 1` drank the first
            # potion when the seat meant another; the belt printed no
            # numbers. Each row carries the number `use potion <n>` takes.
            for n, p in enumerate(you["potions"], start=1):
                out.append(f"- {n}. **{p['title']}** — {p['text']}"
                           if p["text"] else f"- {n}. **{p['title']}**")
        # VARKA (the Oath rework): his current element, his four Oath counts,
        # what a Swirl pays now and every enemy's aura, directly above the
        # hand whose Swirl choices they decide. The Varka payoff round
        # (2026-10-10) moved it here from under the stage, where it sat after
        # the powers, the receipts and the potions, far from the hand.
        if c.get("oath") is not None:
            out += ["", OATH_HEADING, ""] + _render_oath(c["oath"])
        out += ["", "## Your hand", ""]
        if c.get("spark_note"):
            out += [c["spark_note"], ""]
        # `EB-752`: read once for the hand and handed to each face, because it
        # is a fact about what you are HOLDING and not about any one card.
        raiser = _unblocked_raiser(you)
        no_draw = _no_draw_relic(you)
        fang = _ascension_relic(you)
        wildfire = _wildfire_hit(you, c.get("oath"))
        for card in c["hand"]:
            out += _render_card(card, raiser=raiser, no_draw=no_draw)
            if wildfire is not None and _applies_pyro(card):
                out.append(WILDFIRE_NOTE.format(n=wildfire))
            # The Varka payoff round (2026-10-10): where Four Winds'
            # Ascension came from, and that it comes once a combat (a seat
            # tried to play a second one that never came).
            if fang and _fold(card.get("title")).rstrip("+") == _fold(
                    ASCENSION_TITLE):
                out.append(ASCENSION_ONCE_NOTE.format(relic=fang))
        if not c["hand"]:
            out.append("- (your hand is empty)")
        if c.get("hand_repeats"):
            out += ["", HAND_REPEAT_NOTE]
        # `EB-349`: the one-use discount, under the hand it is priced onto.
        if c["hand"]:
            out += _one_use_discount_note(you)
        # `EB-408`: and where a flat Attack buff is up, where the damage
        # figure on each of those faces came from -- one field of the feed,
        # printed unchanged, which may or may not already count the buff.
        out += _attack_buff_note(you, c["hand"])
        out += ["", _OTHER_SIDE, ""]
        for e in c["enemies"]:
            # `EB-496`: the letter in brackets after the name, where the card
            # face already carries its element -- the handle at a glance,
            # before the numbers.
            line = f"- **{e['name']}**"
            if e.get("handle"):
                line += f" [{e['handle']}]"
            # `EB-671`: and the mark, before the numbers, because the question
            # it answers ("where does a Plan land?") is asked about the body
            # and not about its HP. `mark_front` holds the rule.
            if e.get("front"):
                line += " — FRONT"
            if e.get("phase_flip"):
                # `EB-332`: the sentinel is not printed, the event is.
                line += f" — {PHASE_FLIP_LINE}"
            else:
                line += f" — HP {e['hp']}/{e['max_hp']}"
            if e["block"]:
                line += f", Block {e['block']}"
            out.append(line)
            # `EB-672`: and where this body took a dead one's place, the line
            # saying whose -- under that body, because that is where a reader
            # aiming by letter meets the question.
            if e.get("replaced"):
                out.append(ENEMY_REPLACED_LINE.format(was=e["replaced"]))
            elif e.get("revived"):
                out.append(ENEMY_REVIVED_LINE.format(
                    handle=e.get("handle") or e["name"]))
            out += _render_intents(e["intents"])
            # `EB-706`: and where a multiplier stands that the game's own label
            # sometimes folds and sometimes does not, both numbers -- under the
            # telegraph they are about, because a seat plans Block against THIS
            # body's figure.
            out += _intent_fold_lines(e, you)
            for pw in _once(e["powers"]):
                out.append(_render_power(pw, "    ")
                           + _preview_leaves_out(pw, c["hand"]))
                # `EB-605`: and where a Bomb badge's headline and its list of
                # charge sizes are two different numbers, which is which.
                out += _bomb_forecast_note(pw, e["powers"], "    ")
        # 2026-10-05: the attacks shown, summed against your Block. A sum of
        # the telegraphs and nothing more; no plan is computed.
        # SEAT PAGE 3: on Furina's stage too. Her guests are pets, and an
        # enemy's move is handed the player creatures only, so every attack
        # shown is at her (`FurinaStagePets`: "enemies cannot target it by
        # construction"); what the end-of-turn acts may add is said, not
        # counted. NOT IN CO-OP: a telegraph carries no target, and either
        # player may take it.
        if c["enemies"] and not obs.get("coop"):
            out += ["", _incoming_line(c["enemies"], you, c["hand"],
                                       c.get("pets"), c.get("plans"))
                    + _stage_block_clause(c.get("stage"))]
        # `EB-496`: and the rule about both handles, under the list they are
        # handles for. The hand's own note is about cards and says the
        # opposite, which is what sent a seat's Melt into the wrong body.
        if c["enemies"]:
            out += ["", ENEMY_HANDLE_NOTE]
        # Seat page 5 (2026-10-05): `EB-323`'s missing target, on every page
        # where more than one body could be meant.
        out += _intent_target_note(c["enemies"], bool(obs.get("coop")))
        # `EB-708`: and where one of those names carries a SIZE letter, the
        # legend for it -- beside the handle note, because both are about a
        # bracketed thing the list above just printed, and because the seat
        # that lost a Plan on it read the two brackets as one convention.
        if any(_SIZE_LETTER.search(e["name"] or "") for e in c["enemies"]):
            out += ["", ENEMY_SIZE_NOTE]
        # `EB-671`: and what the mark on one of those lines means, beside the
        # note about the handles on all of them.
        if any(e.get("front") for e in c["enemies"]):
            out += ["", FRONT_ENEMY_NOTE]
        # `EB-461`: ONCE PER SCREEN, and only where a telegraph has parts. The
        # note is about a claim the enemy block just made, so it sits with the
        # block's other two notes rather than under the line that made it.
        if any(len(e["intents"]) > 1 for e in c["enemies"]):
            out += ["", MULTI_INTENT_NOTE]
        # `EB-349`: and where a per-hit modifier meets a multi-hit icon, the
        # arithmetic both ways -- beside the note above, because both are
        # about a claim the enemy block has just made.
        out += _per_hit_note(you, c["enemies"])
        # `EB-607`: and where an enemy is wearing Strength, where the number
        # on its icon came from -- one field, printed unchanged.
        out += _intent_source_note(c["enemies"])
        # `EB-706`: and WHY the figure above can be either number, once per
        # screen, beside the provenance note that answers the same question
        # about Strength.
        if any(_intent_fold_lines(e, you) for e in c["enemies"]):
            out += ["", INTENT_FOLD_NOTE]
        if you["powers"] or any(e["powers"] for e in c["enemies"]):
            out += ["", POWER_NOTE]
        # `EB-701`: and where something on this board fires at the END of your
        # turn, when that is -- beside the note above, because both are
        # sentences about the powers the screen has just printed, and once per
        # screen however many of them carry the trigger.
        if _end_of_turn_on_board(c):
            out += ["", _turn_order_note(c)]
        if any(p.get("kind") == "aura"
               for p in you["powers"] + [x for e in c["enemies"]
                                         for x in e["powers"]]):
            out += ["", AURA_NOTE]
        # 2026-10-05: what each kind of enemy here does. SEAT PAGE 3: once
        # PER FIGHT, on the first page a printing door shows of it, whatever
        # the round (`briefed`, the fight's memory of the kinds already
        # briefed, set by `blindplay.screen_page`); with no door, on round 1.
        # The brief page never trims it (`blindplay_brief.KEPT_SECTIONS`).
        if c.get("briefed") is not None:
            out += _briefing_lines(c["enemies"], c["briefed"])
        elif c["round"] == 1:
            out += _briefing_lines(c["enemies"])
    elif obs["screen"] == "map":
        out += ["# The map", ""]
        # `EB-323`: the floor first, because it is the frame the rest of this
        # screen is read in -- the lookahead below counts floors and the
        # run-over page counts floors, and nothing in between ever said which
        # one you were standing on.
        if obs.get("floor"):
            out += [MAP_FLOOR_LINE.format(
                here=obs["floor"],
                act=f" of act {obs['act']}" if obs.get("act") else "",
                next=obs["floor"] + 1), ""]
        if obs.get("seed") or obs.get("ascension") is not None:
            out += [MAP_RUN_LINE.format(
                seed=obs.get("seed") or "not known to this page",
                ascension=(obs["ascension"] if obs.get("ascension") is not None
                           else "not known to this page")), ""]
        if obs.get("hp") is not None:
            out += [f"- HP {obs['hp']}/{obs['max_hp']}", ""]
        out += ["Where you can go next:", ""] + _render_options(obs["nodes"])
        # 2026-09-26: every route, where the feed carries the links. It
        # replaces the all-rooms list below, which cannot show a dead end.
        if obs.get("paths"):
            out += ["", MAP_PATHS_HEAD, ""]
            out += [f"- {f['floors_ahead']} floor"
                    f"{'' if f['floors_ahead'] == 1 else 's'} ahead: "
                    + "; ".join(f"{r['letter']} {r['kind']}"
                                + (f" (to {', '.join(r['to'])})"
                                   if r["to"] else "")
                                for r in f["rooms"])
                    for f in obs["paths"]]
        # `EB-298`: the rest of the act, which was on the feed all along.
        elif obs.get("ahead"):
            out += ["", "The floors ahead of you, nearest first — every room "
                        "on each, in the order they are drawn:", ""]
            out += [f"- {f['floors_ahead']} floor"
                    f"{'' if f['floors_ahead'] == 1 else 's'} ahead: "
                    + ", ".join(f["kinds"]) for f in obs["ahead"]]
        if obs.get("boss"):
            out += ["", f"At the top of this act: **{obs['boss']}**"]
        # `EB-447`: what you are routing WITH. The gold is this screen's own
        # feed; the deck is the lane's store and carries its staleness with
        # it, in the same words the Smith's omission list uses.
        if obs.get("gold") is not None:
            out += ["", f"You have {obs['gold']} gold."]
        if obs.get("deck"):
            out += ["", "## Your deck", ""]
            out += [f"- **{c['title']}**"
                    + (f" × {c['count']}" if c["count"] > 1 else "")
                    for c in obs["deck"]]
            # `EB-447`: and WHICH of the two lists this is. Where the
            # bridge sends `player.master_deck` the list above is the run's
            # own deck, read on this screen, and the fight-old caveat that
            # stood here would be simply wrong. Where it does not, the caveat
            # is exactly as it was.
            if obs.get("deck_is_master"):
                out += ["", DECK_IS_THE_RUNS_OWN]
            else:
                floor = obs.get("deck_floor")
                out += ["", "*This page has no deck on this screen's data "
                            "feed: the list above is your deck as it stood in "
                            "the last fight"
                        + (f" (floor {floor})" if floor else "")
                        + ". Anything you have picked up since is not in it.*"]
        else:
            out += ["", "*This page cannot say what is in your deck yet: the "
                        "deck is on a fight's data feed and no fight of this "
                        "run has been read.*"]
    elif obs["screen"] in ("card_reward", "card_select"):
        out += [f"# {obs['prompt']}", ""]
        for card in obs["offers"]:
            out += _render_card(card)
        if obs["screen"] == "card_select":
            if obs.get("selected"):
                # `EB-329`: the note FIRST, because the misread it prevents is
                # a count, and a reader who has already counted sixteen rows
                # will not go back for a footnote.
                out += ["", "## What you have picked", "",
                        PENDING_PICK_NOTE, ""]
                for card in obs["selected"]:
                    out += _render_card(card, mark=PICKED_MARK)
                # `EB-355` / `EB-393`: the number the enchant moves, on the
                # picked card, before the irreversible confirm.
                if obs.get("enchant"):
                    out += [""] + [enchant_moves_line(obs["enchant"],
                                                      c["title"],
                                                      c.get("text") or "")
                                   for c in obs["selected"]]
                # `EB-314`: on a transform screen the cards above are the ones
                # going IN, and what comes out is still unrolled.
                if obs.get("undecided"):
                    out += ["", TRANSFORM_NOTE]
            elif obs.get("preview_unnamed"):
                out += ["", TRANSFORM_UNREADABLE]
            elif obs.get("selection_known"):
                # `EB-263`: asked, and the answer is nothing. That is a fact
                # about the board, not a hole in the feed, and it is worth one
                # line because the screen looks identical either way.
                out += ["", "Nothing on this screen is picked yet."]
            elif obs["can_confirm"]:
                out += ["", SELECTION_NOTE]
            # `EB-342`: WHAT THE SMITH IS NOT OFFERING, and why. The grid holds
            # the cards the game will upgrade; the deck is not on this screen's
            # feed at all, so the subtraction is against the deck this page
            # printed for itself in the last fight -- and it says so, because a
            # card drafted since that fight is in neither half of it.
            if obs.get("clone_marked"):
                out += ["", CLONE_NOTE]
            if obs.get("omitted"):
                out += ["", "## Not on this list, and why", ""]
                out += [f"- **{o['title']}** — {o['reason']}"
                        for o in obs["omitted"]]
                # `EB-447`: and which deck the subtraction was against.
                if obs.get("deck_is_master"):
                    out += ["", "*The subtraction above is against the run's "
                                "own deck list, off this screen's own data "
                                "feed, minus the cards the screen is "
                                "offering.*"]
                else:
                    floor = obs.get("deck_floor")
                    out += ["", "*This page has no deck on this screen's data "
                               "feed: the list above is your deck as it stood "
                               "in the last fight"
                            + (f" (floor {floor})" if floor else "")
                            + ", minus the cards the screen is offering. "
                              "Anything you have picked up since is in "
                              "neither list.*"]
            # `EB-674`: what the verb after `choose` is, before the refusal
            # that would otherwise teach it. Above the button's own state,
            # because the sentence is about the screen and the line below is
            # about this instant.
            #
            # `EB-779`: and it is the sentence TRUE OF THIS SCREEN. One
            # `choose` closes the mode chooser and resolves the mode (proofs-9
            # lane 1 sec.9), so the two-command sentence was false on it and
            # the `confirm` it told a seat to say cost a refusal every time.
            note = chooser_note(obs.get("select_kind"),
                                obs.get("closes_on_last_pick"),
                                obs.get("picks_needed"))
            out += ["", note]
            # And the button's own state, on the screens that HAVE one. The
            # mode chooser has none -- `BuildChooseCardState` hardwires
            # `can_confirm: false` -- so "Confirm is not available" there reads
            # as a button a reader is waiting for rather than one that is not
            # on the screen at all, which is the misread the note just closed.
            # 2026-09-26: and the closes-on-its-last-pick chooser prints the
            # line only where a confirm is really live (a pick of "up to").
            if note is not CHOOSER_ONE_CHOICE_NOTE \
                    and not (note.startswith(CLOSES_NOTE_HEAD)
                             and not obs["can_confirm"]):
                out += ["", f"Confirm is {'available' if obs['can_confirm'] else 'not available'}."]
            # 2026-09-26 (wave-3 Furina lane 4): the fight behind a chooser
            # that opened mid-fight, where the bridge sends it.
            if obs.get("board"):
                out += _render_board_behind(obs["board"])
        # `EB-314`: over an open preview `skip` does not leave the screen --
        # it cancels the pick and puts the grid back (`ExecuteCancelSelection`
        # presses the preview's own Cancel), so the page says which one it is.
        if obs.get("can_skip") and obs.get("preview_showing"):
            out += ["", "You may say `skip` to undo this pick and choose "
                        "again; it does not leave the screen."]
        elif obs.get("can_skip"):
            out += ["", "You may skip this."]
        # `EB-350`: and where the page could not read the whole grid off the
        # feed, that the list above is a viewport and not the grid. Printed
        # under the list it is about; silent on a bridge that answered.
        if obs.get("grid_incomplete"):
            out += ["", GRID_INCOMPLETE_NOTE]
        # `EB-374`: the alternative buttons, BY NAME. The bridge sends each
        # button's own printed words now, so the screen's other option is a
        # named row with the verb that presses it rather than a caveat about a
        # control the feed would not describe.
        if obs.get("alternatives"):
            out += ["", REWARD_ALTERNATIVES_HEADING, ""]
            for alt in obs["alternatives"]:
                if alt["name"] and alt["verb"]:
                    out.append(REWARD_ALTERNATIVE_ROW.format(
                        name=alt["name"], verb=alt["verb"]))
                elif alt["name"]:
                    # A third button, which no run has produced yet: named,
                    # and honest that this page has no verb aimed at it.
                    out.append(f"- **{alt['name']}** — this page has no verb "
                               "for this one.")
                else:
                    out.append(REWARD_ALTERNATIVE_UNNAMED)
        # `EB-374`: and where a held relic has rewritten what that alternative
        # IS and the words did NOT reach the feed, the caveat goes with it.
        # Printed under the skip line because it is about the skip, on a run
        # holding one of those relics, and only while the page cannot name the
        # button for itself -- a caveat beside the answer is worse than none.
        if obs.get("alternative_relics") and not obs.get("alternatives"):
            out += ["", CARD_REWARD_ALTERNATIVE_NOTE.format(
                relics=" and ".join(f"**{r}**"
                                    for r in obs["alternative_relics"]))]
    elif obs["screen"] == "bundle_select":
        out += [f"# {obs['prompt']}", ""]
        for i, offer in enumerate(obs["offers"]):
            titles = ", ".join(c["title"] for c in offer["cards"]
                               if c["title"])
            head = f"## A bundle of: {titles or '(nothing printed)'}"
            # `EB-294`: the mark the screen never had.
            if i == obs.get("selected", -1):
                head += " — PICKED"
            out += [head, ""]
            for card in offer["cards"]:
                out += _render_card(card)
            out.append("")
        if obs.get("selected", -1) < 0 and obs.get("preview_showing"):
            out += ["*A bundle has been picked and this page cannot say "
                    "which: the screen shows the picked cards rather than "
                    "marking the bundle, and the cards it is showing match "
                    "no single bundle above.*", ""]
        elif obs.get("selected", -1) < 0:
            out += ["*Nothing is picked yet.*", ""]
        # `EB-704`: and the SHAPE of the screen, which this chooser owed as
        # much as the card grid did. A bundle is picked with `choose` and taken
        # with `confirm` -- the verb is in this screen's own command list -- and
        # `EB-674`'s sentence was printed on one of the two paths.
        #
        # THE NOTE AND NOT THE BUTTON'S STATE. The card grid prints `Confirm
        # is ...` beside it because that screen's command list is gated on
        # `can_confirm`; this one offers the verb on every render, so a line
        # saying the button is not available would contradict the grammar three
        # lines below it.
        out += ["", CHOOSER_CONFIRM_NOTE]
    elif obs["screen"] == "shop":
        out += ["# The shop", "", f"You have {obs['gold']} gold.", ""]
        if obs["items"]:
            out += ["On the shelves:", ""] + _render_options(obs["items"])
        else:
            # `EB-360`: the wire returned NO shelves. The r5 seat met a shop
            # with 400 gold in hand and "zero items on every shelf, two
            # observes running", and the page printed an empty shop as if that
            # were the shop. It cannot tell a sold-out shop from a feed that
            # sent nothing, so it says exactly that.
            out += [EMPTY_SHELVES_NOTE]
    elif obs["screen"] == "rest_site":
        # SEAT PAGE 4: the game's Heal figure is not capped by max HP (a seat
        # at 62/80 read "Heal 24" and healed 18), so the room is printed.
        room = (obs["max_hp"] - obs["hp"]
                if isinstance(obs.get("hp"), int)
                and isinstance(obs.get("max_hp"), int) else 0)
        out += ["# A place to rest", "",
                f"HP {obs['hp']}/{obs['max_hp']}"
                + (REST_ROOM.format(room=room) if room > 0 else "")
                + (f", {obs['gold']} gold" if obs.get("gold") is not None
                   else ""), ""] \
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
        # `EB-393`: the decline half. Under the rows, because it is a fact
        # about the list and not about any one of them.
        if obs.get("must_choose"):
            out += ["", EVENT_NO_DECLINE_NOTE]
    elif obs["screen"] in ("rewards", "treasure", "relic_select"):
        titles = {"rewards": "# What the fight left behind",
                  "treasure": "# An open chest",
                  "relic_select": "# Choose one"}
        out += [titles[obs["screen"]], ""]
        # `EB-350`: the gold, on the screens where a route or a purchase is
        # weighed against it, not only on the map and in the shop.
        if obs.get("gold") is not None:
            out += [f"You have {obs['gold']} gold.", ""]
        if obs.get("message"):
            out += [obs["message"], ""]
        out += (_render_options(obs["items"]) if obs["items"]
                else ["- (nothing here to take)"])
        # `EB-702`: WHERE THE CARD OFFER'S SKIP IS, on the screen a seat typed
        # `skip` at and was told there was nothing here to skip. The row above
        # is the offer; its own page is where the skip lives, and that page is
        # opened with `choose`. Printed only where a card row is actually on
        # offer, so a gold-and-potion screen reads exactly as it always did.
        if obs.get("card_offers"):
            out += ["", "*" + " and ".join(f"**{n}**"
                                           for n in obs["card_offers"])
                    + (" is a card OFFER" if len(obs["card_offers"]) == 1
                       else " are card OFFERS")
                    + " rather than the offer's own page: `choose` it to open "
                      "the card screen, and the skip -- *You may skip this* -- "
                      "is on THAT screen. `skip` typed here has no card reward "
                      "open to skip, and `proceed` leaves the whole reward "
                      "screen.*",
                    # 2026-10-01 (seat round): the row is still here after a
                    # skip. The game keeps a skipped offer on the reward
                    # screen (its skip closes only the card screen), so the
                    # page says so rather than reading as a failed skip.
                    "", CARD_OFFER_AFTER_SKIP_NOTE]
        # 2026-09-29 (Varka Oath round, lane 2 act 1): a seat read the
        # chest's relic, typed `proceed` and never had it -- the run save
        # holds no relic for that floor. `proceed` leaves a chest's relic
        # behind, as the game's own button does, so the page says so where a
        # relic is actually waiting.
        if obs["screen"] == "treasure" and any(
                i["enabled"] for i in obs["items"]):
            out += ["", TREASURE_PROCEED_NOTE]
        if obs.get("potion_barred"):
            out += ["", POTION_BARRED_NOTE.format(relic=obs["potion_barred"])]
        # `EB-341`: said on the screen where the claim is made, and only where
        # a potion is actually on offer -- a run with a free slot reads
        # exactly as it always did.
        elif obs.get("potion_offered") and obs.get("potion_slots") \
                and obs["potions_held"] >= obs["potion_slots"]:
            # `EB-356`: and the way out, on the same line. The bridge drinks
            # a non-combat potion here (`ExecuteUsePotion` refuses only the
            # CombatOnly ones), so the verb is offered under "What you can
            # say" and named where the seat is told the belt is full.
            out += ["", f"*Your potion slots are full: "
                        f"{obs['potions_held']} of {obs['potion_slots']}. A "
                        f"potion claimed now has nowhere to go, and the game "
                        f"says nothing when one is dropped -- so this page "
                        f"will not claim it until a slot is free. Drink one "
                        f"first (`use potion`) if the game allows it here, or "
                        f"drop one (`drop potion`).*"]
        # `EB-329`: the receipt for a morning that ended the fight, on the
        # screen the fight ended into. Nothing is claimed about WHY the fight
        # ended -- the note says the fight is over and that this is the last
        # thing the jellyfish did in it, both of which the record supports.
        if obs.get("last_morning"):
            lm = obs["last_morning"]
            out += ["", f"## The {lm['pet_name']}'s last carry-out", "",
                    LAST_MORNING_NOTE, ""] + _render_carry_out(lm)
            if _board_note_wanted(lm):
                out += ["", CARRY_OUT_BOARD_NOTE]
    else:                                                # pragma: no cover
        raise BlindPlayError(f"no renderer for screen {obs['screen']!r}")

    # `EB-676` / `EB-715`: what the run did between the previous screen this
    # page drew and this one. Directly under the screen's own body, above the
    # relics and the belt, because it is the thing a seat about to choose a
    # route or plan a block has to know and the one thing no screen printed.
    out += _render_run_change(obs.get("run_change") or {})

    # CO-OP: the other player's HP, Block, turn and pets, and any vote in
    # progress, under the screen's own body. Singleplayer pages carry no
    # `coop` key and print nothing here.
    if obs.get("coop"):
        out += coop_lines(obs["coop"])

    # `EB-473`: the relic row, on a screen that is not a fight, in the
    # combat header's own words and under its own heading. A relic claimed at
    # the reward of the LAST fight of a run had no later combat page to print
    # it on, and the Klee r15 run-2 seat finished holding one it could not
    # describe. Above the belt, because that is the order the combat page
    # already has -- relics, then potions.
    if obs.get("held_relics"):
        out += ["", "## Your relics", ""] + [
            f"- **{r['name']}**"
            + (f" ({_relic_counter(r)})" if r.get("counter") else "")
            + (RELIC_USED_UP if r.get("used_up") else "")
            + (f" — {r['text']}" if r["text"] else "")
            for r in obs["held_relics"]]

    # `EB-371`: the belt, on a screen that is not a fight. A combat page has
    # printed it under the same heading since `EB-341`; every other screen was
    # offering `drop potion` over a list the reader could not see. Above the
    # glossary and below the screen's own body, which is where the combat page
    # already puts it.
    if obs.get("belt"):
        out += ["", "## Potions", ""]
        if obs.get("belt_slots"):
            out += [f"- {len(obs['belt'])} of {obs['belt_slots']} slots are "
                    f"full.", ""]
        for p in obs["belt"]:
            out.append(f"- **{p['title']}** — {p['text']}" if p["text"]
                       else f"- **{p['title']}**")

    # `EB-272`: one definition per arm keyword the screen printed, once, below
    # the board and above the grammar -- where a reader who has just met the
    # word looks next, and where it does not push the board off the top.
    if obs.get("keywords"):
        out += ["", "## Words on this screen", ""]
        # `EB-504`: a row whose rule belongs to a character this run is not
        # playing prints its NAME and stops. The word is on the screen and the
        # page will not pretend it has no entry; what it has is no rule here.
        out += [f"- **{k['name']}** — {k['text']}" if k["text"]
                else f"- **{k['name']}**" for k in obs["keywords"]]

    out += ["", "## What you can say", ""]
    out += [f"- `{c}`" for c in obs["commands"]]
    out += ["", obs["guardrail"], ""]
    text = "\n".join(out).rstrip() + "\n"
    assert_one_page(text)
    assert_chooser_note(obs, text)
    qa_packet.assert_blind(text, allow={st})
    return text


def assert_chooser_note(obs: dict[str, Any], text: str) -> None:
    """No chooser without `EB-674`'s sentence (`EB-704`).

    A screen that offers `confirm` is a screen where a pick is TWO commands and
    the chooser stays up between them, which is the shape `EB-674` found a seat
    learning from a refusal. The note was printed on the card grid and not on
    the bundle picker, and the acceptance the row asks for is not "these two
    branches" but "no chooser without it" -- so the pin is here, at the one
    place the page is finished, and it reads the GRAMMAR rather than the branch:
    whatever screen starts offering the verb tomorrow owes the sentence too.

    `EB-779` ADDS THE OTHER DIRECTION, which is the half proofs-9 lane 1 found
    live: the one-press chooser must NEVER be told to say `confirm`. One
    `choose` closes that screen, so the word is a refusal a seat spends eight
    times a run, and the assertion reads the page's own text rather than the
    branch that wrote it.
    """
    if "confirm" in (obs.get("commands") or []) \
            and CHOOSER_CONFIRM_NOTE not in text \
            and CHOOSER_MAYBE_CLOSES_NOTE not in text \
\
            and CLOSES_NOTE_HEAD not in text:
        raise BlindPlayError(
            "this page offers `confirm` and does not say that a pick here is "
            "two commands, so a reader would learn it from a refusal: "
            + str(obs.get("screen")))
    if str(obs.get("select_kind") or "").strip().lower() \
            == ONE_PRESS_CHOOSER_KIND:
        if CHOOSER_ONE_CHOICE_NOTE not in text:
            raise BlindPlayError(
                "this is the one-press chooser and the page does not say that "
                "one `choose` closes it: " + str(obs.get("screen")))
        if "`confirm`" in text:
            raise BlindPlayError(
                "this page tells a reader to say `confirm` on the chooser "
                "that has no confirm button (`EB-779`): "
                + str(obs.get("screen")))


#: A section heading, which on this page is the only line that opens with a
#: hash. `EB-510`.
_HEADING = re.compile(r"^#{1,2} .+$", re.MULTILINE)


def assert_one_page(text: str) -> None:
    """One section per heading, and one heading per section (`EB-510`).

    WHAT THE SEAT SAW (Furina r11 lane 2, (c) 8): "several observe screens
    printed `## Your hand` and `## The other side` twice, with card bodies
    duplicated line-for-line. It never changed what I could do, but it made
    two screens genuinely hard to read."

    AND THE RENDER ABOVE CANNOT PRODUCE IT. Every heading is appended at
    exactly one `out +=` on one branch, the branches are mutually exclusive,
    and the two headings a combat page shares with the trailing non-combat
    block (`## Your relics`, `## Potions`) are gated on `screen != "combat"`
    -- so a page built by this function has each of its headings once, which
    is what the check below asserts. A doubled page therefore came from
    something that emitted this text TWICE: a caller that printed the page and
    then appended a second read of it.

    So the pin is here, at the one place the page is finished, and it is the
    shape rather than the cause: whatever doubles a section -- a branch that
    grows a second `out +=` tomorrow, or a caller that concatenates two reads
    through `render` -- stops being a screen a seat has to read twice and
    becomes a refusal naming the heading. It raises `BlindPlayError`, the same
    class every other structural refusal on this page raises, so a driver that
    already handles one handles this.
    """
    seen: dict[str, int] = {}
    for heading in _HEADING.findall(text):
        seen[heading] = seen.get(heading, 0) + 1
    twice = sorted(h for h, n in seen.items() if n > 1)
    if twice:
        raise BlindPlayError(
            "this page printed a section twice, so a reader would read the "
            "same board as two boards: " + ", ".join(repr(h) for h in twice))
    _assert_one_enemy_list(text)


#: `EB-705`. The enemy block, and the body rows inside it. A body row is the
#: one bullet in that section that opens with a bold name; its intents, powers
#: and the replaced-body line are all indented under it.
_OTHER_SIDE = "## The other side"
_BODY_ROW = re.compile(r"^- \*\*.+", re.MULTILINE)


def _assert_one_enemy_list(text: str) -> None:
    """One body per board, and one board per screen (`EB-705`).

    THE FIND. The enemy list printed TWICE on multi-enemy screens, footnotes
    included, after `EB-694`'s dedupe -- so the copies were not equal field for
    field and the second one arrived as three more creatures. `EB-694`'s own
    reasoning is why the check belongs here: the render appends this block at
    exactly one place, so a doubled list is either a feed that repeated itself
    or a caller that appended the section twice, and neither is a screen a seat
    should have to read.

    IT NEEDS NO IDS BECAUSE THE PAGE ALREADY MINTED THEM. `_enemy_names` gives
    every body on a board a printed name of its own -- `Slug (1)`, `Slug (2)` --
    and `_enemy_handles` a letter, so two identical body rows in one enemy
    block are one body printed twice and can be nothing else.
    """
    if _OTHER_SIDE not in text:
        return
    block = text.split(_OTHER_SIDE, 1)[1]
    cut = _HEADING.search(block)
    if cut:
        block = block[:cut.start()]
    seen: dict[str, int] = {}
    for row in _BODY_ROW.findall(block):
        seen[row] = seen.get(row, 0) + 1
    twice = sorted(r for r, n in seen.items() if n > 1)
    if twice:
        raise BlindPlayError(
            "this page printed the enemy list twice, so a reader would count "
            "the board as two boards: " + ", ".join(repr(r) for r in twice))


def observe(state: dict[str, Any]) -> str:
    """A design-blind Markdown render of any screen the wire can return."""
    return render(observation(state))


def still_in_fight(obs: dict[str, Any], was_in_fight: bool) -> bool:
    """Whether the run is inside a fight on THIS screen (`EB-245`).

    A combat screen IS a fight. An overlay a fight can wear inherits the answer
    from the screen before it, because the feed does not say which side of a
    fight boundary an overlay is on. Everything else is not a fight, which is
    where a fight record is owed.
    """
    if obs["screen"] == "combat":
        return True
    if obs["state_type"] in FIGHT_OVERLAYS:
        return was_in_fight
    return False


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
