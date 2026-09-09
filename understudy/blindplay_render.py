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
from understudy.blindplay_board import (PHASE_FLIP_LINE, _pulse_phrase,
                                        enchant_moves_line, stage_seat_name)
from understudy.blindplay_notes import (_AURA_NAME_RE, ATTACK_BUFF_NOTE,
                                        AURA_NOTE, BOMB_FORECAST_NOTE,
                                        BOMB_REACTION_CLAUSE,
                                        REACTION_ELEMENTS,
                                        SALON_ARRIVAL_NOTE,
                                        AUTO_TURN_NOTE,
                                        BUFF_INTENT_CLAUSE,
                                        CLONE_NOTE, EMPTY_SHELVES_NOTE,
                                        INTENT_NUMBER_DISAGREES,
                                        INTENT_SOURCE_NOTE,
                                        ONE_USE_DISCOUNT_NOTE,
                                        ONE_USE_RIDER_NOTE,
                                        PER_HIT_NOTE,
                                        LAST_SALON_NOTE,
                                        MAP_FLOOR_LINE,
                                        CARD_REWARD_ALTERNATIVE_NOTE,
                                        CARRY_OUT_BOARD_NOTE,
                                        CHOOSER_CONFIRM_NOTE,
                                        DEFEND_INTENT_CLAUSE,
                                        ENEMY_HANDLE_NOTE,
                                        ENEMY_REPLACED_LINE,
                                        EVENT_NO_DECLINE_NOTE,
                                        FRONT_ENEMY_NOTE,
                                        HAND_REPEAT_NOTE,
                                        LAST_MORNING_NOTE,
                                        LAST_SALON_NOTE,
                                        METER_CAPPED_NOTE,
                                        METER_DEFINED_NOTE, METER_NOTE,
                                        METER_RULES,
                                        MULTI_INTENT_LABEL,
                                        MULTI_INTENT_NOTE,
                                        NO_REACTION_THIS_TURN,
                                        PENDING_PICK_NOTE, PICKED_MARK,
                                        REACTIONS_HEADING, REACTION_ROW,
                                        REACTION_ROW_NO_SOURCE,
                                        PLAN_AIM_NOTE,
                                        PLAN_BLOCK_NOTE,
                                        PLAN_CASKET_AURA_CLAUSE,
                                        PLAN_COUNT_CAPPED_NOTE,
                                        PLAN_COUNT_NOTE,
                                        PLAN_WRITTEN_NUMBER_NOTE,
                                        PLAN_HYDRO_NOTE,
                                        POWER_NOTE, SELECTION_NOTE,
                                        SPARK_OPENING_RULE,
                                        SPOTLIGHT_WINDOW_NOTE,
                                        TRANSFORM_NOTE, TRANSFORM_UNREADABLE)
from understudy.blindplay_observe import observation
from understudy.blindplay_read import _fold
from understudy.blindplay_shape import (BlindPlayError, CHARGE_SOURCE_LINE,
                                        FIGHT_OVERLAYS, KURAGE_COST_PER_ENERGY)


# ----------------------------------------------------------------- render --

def _render_card(c: dict[str, Any], bullet: str = "-",
                 mark: str = "") -> list[str]:
    """One card face. `mark` is a state the SCREEN is in about this row and
    not a fact about the card, so it goes at the END of the head, after the
    cost and the type -- the shape `EB-294` gave a picked bundle."""
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
    if bits:
        head += f" — {', '.join(bits)}"
    if mark:
        head += f" — {mark}"
    out = [head, f"    {c['text'] or '(no printed text)'}"]
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
    if c.get("upgraded_face"):
        out.append(f"    Upgraded: {c['upgraded_face']}")
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
        # `EB-271`: and the clause that stops the vague one being vague, on
        # its own line under it, because it is this page's sentence and not
        # the game's.
        if c.get("unplayable_note"):
            out.append(f"    {c['unplayable_note']}")
    return out


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


def _render_performance(row: dict[str, Any]) -> str:
    """One Salon member's act (`EB-405`): who, on whom, for how much, and what
    the body is wearing afterwards.

    THREE FACTS AND NOT FOUR. The `paid` half is on the line because it is the
    difference between the printed number and three-quarters of it
    (`SalonConstants.DryDamageMultiplier`), and a reader watching a member act
    small with an empty buffer is owed the reason. The aura clause is printed
    only for a member that AIMED: the Usher gains Block and touches nobody, so
    a sentence about what it left on a body would be about no body.
    """
    line = f"- **{row['member']}**"
    if row["target"]:
        line += (f" hit {row['target']} for {row['amount']}"
                 + (f" {row['element']}" if row["element"] else ""))
        line += (f", and it is wearing a {row['aura']} aura" if row["aura"]
                 else ", and left no aura on it")
    else:
        line += f" gave you {row['amount']} Block"
    if not row["paid"]:
        line += " (dry: it could not pay its Encore, so it acted at "
        line += "three-quarters)"
    return line + "."


def _render_evoke(row: dict[str, Any]) -> str:
    """One Evoke (`EB-564`): who bowed, what the bow did, and what it minted.

    THE DEFECT, in the r14 lane-1 seat's words: "The Salon log printed the two
    performances and never printed the Evoke. I only knew it had happened by
    reading the auras." It fired twice in one elite -- the kit's biggest single
    beat -- and the whole evidence was Encore jumping by three and every body
    coming out wearing Hydro.

    IT IS ITS OWN SENTENCE AND NOT A PERFORMANCE LINE. A bow does things a
    performance never does: Chevalmarin's touches EVERY enemy and names no
    body, and every Evoke leaves the member. So the line says the member left,
    then what the bow did, then what it paid -- and the clauses that do not
    apply to this member are simply absent, `_render_performance`'s own rule
    about the Usher and the aura.
    """
    line = f"- **{row['member']}** took its final bow — an EVOKE, so it left "
    line += "the stage"
    did: list[str] = []
    if row["aura_all"]:
        did.append("left Hydro on every enemy")
    if row["target"]:
        did.append(f"hit {row['target']} for {row['damage']} Hydro")
    if row["block"]:
        did.append(f"gave you {row['block']} Block")
    if row["encore"]:
        did.append(f"granted {row['encore']} Encore")
    if row["fanfare"]:
        # THE FOCUS MULTIPLIER IS ON THE LINE because it is the whole
        # difference between an Evoke and a performance the reader can see
        # from the numbers -- the Fanfare is larger BECAUSE the bow cost a
        # member, and the Focus term counted `focus_mult` times.
        mult = (f", its Focus counting {row['focus_mult']} times"
                if row["focus_mult"] > 1 else "")
        did.append(f"minted {row['fanfare']} Fanfare{mult}")
    if did:
        line += ". It " + ", ".join(did[:-1] + [f"and {did[-1]}"]
                                    if len(did) > 1 else did)
    return line + "."


#: A per-turn ALLOWANCE stated in a power's own sentence (`EB-467`). The
#: shipped shape is Hardened Shell's "cannot lose more than 20 HP each turn";
#: the alternatives are the same sentence's other spellings of "each turn",
#: which is the only clause that makes the number a per-turn budget rather
#: than a total.
_PER_TURN_CAP = re.compile(
    r"more than (\d+)\s+\S+ (?:each|per|every|a|in a single|in one) turn",
    re.IGNORECASE)


def _turn_allowance(power: dict[str, Any]) -> int | None:
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
    """
    found = _PER_TURN_CAP.search(str(power.get("text") or ""))
    if not found:
        return None
    cap = int(found.group(1))
    stacks = power.get("stacks")
    if not isinstance(stacks, int) or isinstance(stacks, bool):
        return None
    return cap if 0 <= stacks <= cap else None


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


def _render_power(power: dict[str, Any], indent: str) -> str:
    """One power: printed name, the amount, buff or debuff, the printed text.

    `EB-467`: where the amount is an allowance counting down against a cap the
    power's own sentence states, the two numbers print in ONE clause -- "12 of
    20 left this turn" -- instead of standing apart and contradicting.

    `EB-525`: and where the sentence describes a stack that arrives after the
    card that adds it has already resolved, the page says which cards the
    number counts.
    """
    cap = _turn_allowance(power)
    if cap is None:
        line = f"{indent}{power['name']} {power['stacks']}"
    else:
        line = f"{indent}{power['name']} {power['stacks']} of {cap} left " \
               f"this turn"
    kind = str(power.get("kind") or "").strip().lower()
    if kind:
        line += f" ({kind})"
    if power["text"]:
        line += f" — {power['text']}{_slow_clause(power)}"
    return line


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
_ONE_USE_RIDER = re.compile(r"the next (\w+) you play\b", re.I)
# `EB-433`. A relic that answers a debuff with an elemental hit, which is what
# makes the panel's "leaves no aura" clause false for a debuff Plan. The
# Tamakushi Casket's own sentence, with the element left open: the clause is
# about a hit that carries one, and the Plan is Hydro either way.
_DEBUFF_ANSWERING_HIT = re.compile(
    r"whenever you apply a debuff[^.]*damage", re.I)


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
_BOMB_SIZES = re.compile(r"bomb sizes here:\s*([0-9/ ]+)", re.I)


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
    charges = [int(n) for n in _NUMBER.findall(sizes.group(1))]
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
                power=f"**{power['name']}**", kind=found.group(1))]
    return []


_NUMBER = re.compile(r"\d+")


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


def _numbers_disagree(intent: dict[str, str]) -> bool:
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


def _intent_source_note(enemies: list[dict[str, Any]]) -> list[str]:
    """`EB-607`: where an icon number comes from, said where Strength is up.

    Printed only on a board that raises the question -- an enemy wearing
    Strength and telegraphing an Attack -- because on every other board the
    provenance of a number nobody is checking against a modifier is furniture.
    Keyed on the power's printed name, which is the row this page prints and
    the word the reader is reading it against.
    """
    for enemy in enemies:
        if not any(_fold(p.get("name")) == "strength"
                   for p in enemy.get("powers") or []):
            continue
        if any(_fold(i.get("type")) == "attack" or i.get("label")
               for i in enemy.get("intents") or []):
            return ["", INTENT_SOURCE_NOTE]
    return []


def _render_intents(intents: list[dict[str, str]]) -> list[str]:
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


def _render_intent(intent: dict[str, str], part: bool = False) -> str:
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
    number = (f"the number on its icon is {intent['label']}"
              + (MULTI_INTENT_LABEL if part else "")
              if intent.get("label") else "")
    bits = [head, number, intent.get("text") or ""]
    # `EB-607`: the two numbers on this line are two fields of the feed --
    # `GetIntentLabel`'s icon figure and `GetHoverTip`'s sentence -- and the
    # page printed both and said nothing about the pair.
    if _numbers_disagree(intent):
        bits.append(INTENT_NUMBER_DISAGREES)
    if _fold(kind) == "defend":
        bits.append(DEFEND_INTENT_CLAUSE)
    # `EB-323`: and a `Buff` part says whose side it is on. `Empower (Buff)`
    # was a heading, a bracketed kind and nothing else on a board of three
    # bodies; the target itself is not on the wire and the clause says so.
    if _fold(kind) == "buff":
        bits.append(BUFF_INTENT_CLAUSE)
    return " — ".join(b for b in bits if b) or "(no intent shown)"


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
            if named.get("text"):
                row += f" — {named['text']}"
            out.append(row)
        if o.get("note"):
            out.append(f"    *{o['note']}*")
    return out


#: `EB-735`. The window the stage log covers, said once at the head of the
#: section rather than implied by its rows. The clear is at her turn END
#: (`FurinaStageHooks.BeforeSideTurnEnd`), so what a seat opening a turn reads
#: here is the sweep it could not watch and the enemy turn that followed it --
#: which is exactly the half of the fight the bars move most in.
STAGE_LOG_HEADING = ("- Since you ended your last turn, in order (the "
                     "end-of-turn acts, the enemies' turn, then what you have "
                     "played this turn):")

STAGE_EMPTY_LINE = ("- The stage is empty. A [gold]Spend[/gold] rider cannot "
                    "fire at all, so those cards play at their base number.")


def _render_stage(stage: dict[str, Any], you: dict[str, Any]) -> list[str]:
    """The stage, in DAMAGE ORDER, on one line, plus the reserve on the next.

    `EB-735`. Round one's first finding was that the page named no performer,
    no seat and no bar, and its second was that the three read as "one
    anonymous pool with three names". Both are answered by printing them, and
    printing them in the order the damage takes: brief sec.8's last failure
    mode asks for exactly this -- "the strip must show the lead's bar beside
    her Block, in the damage order".

    SO THE FIRST LINE IS THE DAMAGE ORDER AND NOTHING ELSE. Block, then the
    lead's bar, then her HP: the three numbers one attack meets, in the order
    it meets them, which is the one sentence rule 6 is. The reserve goes on its
    own line because nothing reaches it, and a seat that read the two as one
    line would be reading four bars where an attack sees two.
    """
    seats = stage["seats"]
    lead = seats[0] if seats else None
    head = [f"Block {you['block']}"]
    if lead is not None:
        head.append(f"lead: {lead['name']} {lead['fanfare']}")
    head.append(f"Furina {you['hp']}/{you['max_hp']}")
    out = ["- " + " · ".join(head)]
    # The seats nothing reaches, named the way rule 5 names them -- and with
    # `stage_seat_name` deciding, so a lone performer is never called a back
    # performer a Raise would then be sent to.
    reserve = [f"{stage_seat_name(i, len(seats))}: {row['name']} "
               f"{row['fanfare']}"
               for i, row in enumerate(seats) if i > 0]
    if reserve:
        out.append("- " + " · ".join(reserve))
    if not seats:
        out.append(STAGE_EMPTY_LINE)
    return out


def _stage_moved(row: dict[str, Any]) -> str:
    """What the board did under one beat, or nothing.

    THE MEASURED NUMBER, never the clause's (`EB-511`): the mod files what the
    enemies' HP actually fell by and what Block she actually gained, so an act
    into a Vulnerable reads the number the seat can check against the bodies
    four lines down. A beat that moved nothing -- Chevalmarin's bow, which only
    leaves an aura -- says nothing rather than saying 0.
    """
    return f" It moved {row['moved']}." if row["moved"] else ""


def _render_stage_log(stage: dict[str, Any]) -> list[str]:
    """One line per arrival, act, bow, departure and rotation."""
    out: list[str] = []
    standing = len(stage["seats"])
    for row in stage["log"]:
        who = f"**{row['name']}**"
        seat = row["seat"]
        # WHICH SEAT, where the beat happened in one. A departed performer is
        # in no seat and the line names none. The cast size is TODAY'S, floored
        # at the index the beat recorded: rule 5 makes "back" mean the
        # back-most OCCUPIED seat, so a lone performer must not be called a
        # middle one, and a beat from a fuller stage must not be told there
        # were fewer seats than it stood in.
        where = (f" the {stage_seat_name(seat, max(standing, seat + 1))} seat"
                 if seat >= 0 else "")
        if row["event"] == "arrive":
            out.append(f"  - {who} took{where} at {row['fanfare']} "
                       f"[gold]Fanfare[/gold].")
        elif row["event"] == "act":
            seat_clause = f" from{where}" if where else ""
            out.append(f"  - {who} performed{seat_clause}."
                       f"{_stage_moved(row)}")
        elif row["event"] == "bow":
            out.append(f"  - {who} took a [gold]Bow[/gold]."
                       f"{_stage_moved(row)}")
        elif row["event"] == "leave":
            out.append(f"  - {who} left the stage: {row['why']}.")
        elif row["event"] == "rotate":
            out.append(f"  - {who} moved from the front seat to the back, "
                       f"bar and all. Nobody left and nobody took a "
                       f"[gold]Bow[/gold].")
    return out


def render(obs: dict[str, Any]) -> str:
    """The observation as the page the tester is handed. Same content."""
    st = obs["state_type"]
    if obs["blocked"]:
        body = [f"TOOL-BLOCKED: {st}", "", obs["blocked"]]
        if obs["screen"] == "game_over":
            body += ["", f"The run ended on floor {obs['floor']}"
                         + (f": {obs['result']}" if obs["result"] else ".")]
            if obs.get("summary"):
                body += ["", "What the run ended with:", ""] + obs["summary"]
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
        defined = {row["name"] for row in (obs.get("keywords") or [])}
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
                rule = SPARK_OPENING_RULE
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
                for i, e in enumerate(pl["queue"], 1):
                    out.append(f"  {i}. **{e['name']}**"
                               + (" — Dusk: this one is carried out at the "
                                  "END of this turn instead, before the "
                                  "enemies act" if _is_dusk(e) else ""))
                if pl["twice"]:
                    out.append("- The jellyfish carries out your FIRST Plan "
                               "twice while Nereid's Ascension lasts.")
            # `EB-329`: which of the two numbers under a Plan is which, once,
            # at the foot of the section rather than under the last card.
            if _board_note_wanted(pl):
                out += ["", CARRY_OUT_BOARD_NOTE]
        # `EB-735`. THE STAGE, ABOVE EVERYTHING IT DECIDES. Three round-one
        # seats played some 550 actions without ever knowing who was on stage
        # or what a bar held, because the page had no renderer for her
        # performers; the block below is that renderer, and it goes here --
        # under the header and above the hand -- because rule 6 makes the
        # lead's bar part of the damage order the header's Block line opens,
        # and rule 8 makes the same bar the price of half the cards in the
        # hand underneath.
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
        if c.get("salon") and c["salon"].get("company"):
            company = c["salon"]["company"]
            out += ["", "## Your Salon", ""]
            for i, member in enumerate(company):
                out.append(f"- **{member}**"
                           + (" — FRONT: the next Companion card you play "
                              "performs this one, and then sends it to the "
                              "back" if i == 0 else ""))
            # `EB-585`. THE ARRIVAL THAT PERFORMED AND WAS NOT FILED. On the
            # fight's first screen an occupied stage was occupied by the
            # relic's arrival, and an arrival performs -- so an empty
            # performance list here is a receipt that did not reach the feed,
            # not a member that did nothing. Round one and an empty list are
            # the only board the sentence is true on.
            if c["round"] == 1 and not c["salon"]["performed"]:
                out += ["", SALON_ARRIVAL_NOTE]
        if c.get("salon") and (c["salon"]["performed"]
                               or c["salon"]["replayed"]
                               or c["salon"].get("evoked")):
            # `EB-405`. WHAT THE STAGE DID THIS TURN, one act per line --
            # `EB-198`'s contract, the same one the carry-out block is under.
            #
            # THE TARGET AND THE AURA ARE THE POINT. "Crabaletta chose its own
            # enemy and left a Hydro aura on a body the seat had not picked"
            # (Furina round 4, run 1, (c) 4) is a complaint about a decision
            # the reader could not see, in a kit whose readable decision is
            # which element lands on which aura. The member names its body, and
            # the line ends with what that body is WEARING -- read after the
            # hit, so a reaction that consumed the aura says "and left no
            # aura" rather than claiming Hydro that is not there.
            out += ["", "## What your Salon did this turn", ""]
            # `EB-582`. THE EVOKE LEADS, because that is the order the card
            # promises and the order the engines resolve. `EB-564` put the bow
            # LAST here on the reading that "an Evoke follows the acts above",
            # and the r15 lane-1 seat read the consequence off the page: the
            # Deploy word says "a full stage [gold]Evokes[/gold] the front
            # member first", the arriving member performs AFTER that bow, and
            # the page printed the two the other way round (`EB-582`, Furina
            # r15 lane 1 (c) 2).
            #
            # THE BOUNDARY, stated because the block cannot hide it: these are
            # two lists and not one stream, so the grouping orders them by
            # CLASS and cannot interleave. It is right for every turn whose
            # Evoke came from a deploy -- which is every Evoke that has a
            # performance beside it at all -- and the one turn it cannot order
            # is a Companion play followed by a full-stage deploy, where the
            # first performance belongs above the bow. Ordering that needs a
            # per-act sequence on the wire, which the ledger does not carry.
            out += [_render_evoke(row) for row in c["salon"].get("evoked", [])]
            out += [_render_performance(row) for row in c["salon"]["performed"]]
            # `EB-420`. THE PLAY BEHIND ONE OF THE ACTS ABOVE, named. The
            # round-5 seat counted "two Crabaletta lines ... for three
            # Companion-card plays' worth of triggers" and found "no line
            # anywhere on the screen said Duet" -- and a performance list
            # cannot say which of its acts came from a replay.
            #
            # `EB-464` FLIPPED THE SECOND HALF OF THE SENTENCE. The extra play
            # used to perform nobody; it performs now, so the acts above are no
            # longer one short of the plays and the line says what happened
            # instead of what did not.
            out += [f"- **{name}** was played an extra time, and the extra "
                    "play performed as well."
                    for name in c["salon"]["replayed"]]
        # `EB-681`. WHAT REACTED THIS TURN, under the board that reacted and
        # above the hand -- a receipt for the beat just watched, filed where
        # the other receipts on this page are (the carry-out block, the
        # Salon's). Present and empty prints its own line, because "no line"
        # and "no reaction" were the same page to the r27 lane-1 seat.
        if c.get("reactions") is not None:
            out += ["", REACTIONS_HEADING, ""]
            for row in c["reactions"]:
                out.append((REACTION_ROW if row["source"]
                            else REACTION_ROW_NO_SOURCE).format(**row))
            if not c["reactions"]:
                out.append(NO_REACTION_THIS_TURN)
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
                # `EB-248`: THE COST THE RULE MULTIPLIED, beside the price it
                # produced. The price is three times the EFFECTIVE face, so a
                # Muster recruit printing 2 enrols at 3 and the tester who read
                # both numbers had no route from one to the other -- the defect
                # was named unprompted, and it is legibility rather than
                # arithmetic. This is `KurageMemory.PriceText`'s sentence,
                # word for word, so the page and the pile view say the same
                # thing. A free memory carries no derivation: a zero price
                # means a zero cost, and "cost 0 x 3" would restate the answer
                # rather than explain it.
                for i, e in enumerate(m["queue"], 1):
                    price = ("free" if not e["price"] else
                             f"{e['price']} Charge, cost {e['cost']} x "
                             f"{KURAGE_COST_PER_ENERGY}")
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
            # `EB-341`: how many slots there are, beside how many are used.
            # A tester who cannot see the denominator cannot know that the
            # next potion offered has nowhere to go.
            if you.get("potion_slots"):
                out += [f"- {len(you['potions'])} of "
                        f"{you['potion_slots']} slots are full.", ""]
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
        # `EB-349`: the one-use discount, under the hand it is priced onto.
        if c["hand"]:
            out += _one_use_discount_note(you)
        # `EB-408`: and where a flat Attack buff is up, where the damage
        # figure on each of those faces came from -- one field of the feed,
        # printed unchanged, which may or may not already count the buff.
        out += _attack_buff_note(you, c["hand"])
        # `EB-567`. THE WINDOW, BEFORE THE REFUSAL RATHER THAN AFTER IT. Under
        # the arm the Spotlight's price is the opening Encore exactly, and
        # both r14 seats learned that from a refusal one action too late.
        #
        # `EB-600` TOOK THE TURN-ONE GATE OFF, because the rule it was built
        # on is false. The note used to print on round 1 only, on the reading
        # that "the window is already open or already shut" by round 2; Encore
        # is REFILLABLE, and both r16 lanes said so. Lane 1: "Aria and Hearts
        # Swelling grant Encore without performing, and I broke the rule on
        # turn 1 of the run." Lane 2 lit it after a performance in three
        # fights off Chevalmarin's grant of 3. A window that reopens has to be
        # stated on the turn it reopens on, so the note rides the CARD being
        # in hand and nothing else.
        #
        # GATED ON THE SALON BLOCK, which is the page's own test for "this
        # build plays the reframe": the block is sent only under
        # `FurinaReframe.ManualLiveFor`, and a release build's selector costs
        # no Encore and would make this sentence false.
        if (c.get("salon") is not None
                and any(card["title"] == "Ethereal Spotlight"
                        for card in c["hand"])):
            out += ["", SPOTLIGHT_WINDOW_NOTE]
        out += ["", "## The other side", ""]
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
            out += _render_intents(e["intents"])
            for pw in e["powers"]:
                out.append(_render_power(pw, "    "))
                # `EB-605`: and where a Bomb badge's headline and its list of
                # charge sizes are two different numbers, which is which.
                out += _bomb_forecast_note(pw, e["powers"], "    ")
        # `EB-496`: and the rule about both handles, under the list they are
        # handles for. The hand's own note is about cards and says the
        # opposite, which is what sent a seat's Melt into the wrong body.
        if c["enemies"]:
            out += ["", ENEMY_HANDLE_NOTE]
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
        if you["powers"] or any(e["powers"] for e in c["enemies"]):
            out += ["", POWER_NOTE]
        if any(p.get("kind") == "aura"
               for p in you["powers"] + [x for e in c["enemies"]
                                         for x in e["powers"]]):
            out += ["", AURA_NOTE]
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
        out += ["Where you can go next:", ""] + _render_options(obs["nodes"])
        # `EB-298`: the rest of the act, which was on the feed all along.
        if obs.get("ahead"):
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
            floor = obs.get("deck_floor")
            out += ["", "*This page has no deck on this screen's data feed: "
                        "the list above is your deck as it stood in the last "
                        "fight"
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
                floor = obs.get("deck_floor")
                out += ["", "*This page has no deck on this screen's data "
                           "feed: the list above is your deck as it stood in "
                           "the last fight"
                        + (f" (floor {floor})" if floor else "")
                        + ", minus the cards the screen is offering. Anything "
                          "you have picked up since is in neither list.*"]
            # `EB-674`: what the verb after `choose` is, before the refusal
            # that would otherwise teach it. Above the button's own state,
            # because the sentence is about the screen and the line below is
            # about this instant.
            out += ["", CHOOSER_CONFIRM_NOTE]
            out += ["", f"Confirm is {'available' if obs['can_confirm'] else 'not available'}."]
        # `EB-314`: over an open preview `skip` does not leave the screen --
        # it cancels the pick and puts the grid back (`ExecuteCancelSelection`
        # presses the preview's own Cancel), so the page says which one it is.
        if obs.get("can_skip") and obs.get("preview_showing"):
            out += ["", "You may say `skip` to undo this pick and choose "
                        "again; it does not leave the screen."]
        elif obs.get("can_skip"):
            out += ["", "You may skip this."]
        # `EB-374`: and where a held relic has rewritten what that alternative
        # IS, the caveat goes with it. Printed under the skip line because it
        # is about the skip, and only on a run holding one of those relics.
        if obs.get("alternative_relics"):
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
        out += ["# A place to rest", "",
                f"HP {obs['hp']}/{obs['max_hp']}"
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
        # `EB-341`: said on the screen where the claim is made, and only where
        # a potion is actually on offer -- a run with a free slot reads
        # exactly as it always did.
        if obs.get("potion_offered") and obs.get("potion_slots") \
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
        # `EB-604`: the Salon's half of the same receipt, in the combat page's
        # own order -- the Evoke leads (`EB-582`), then the performances, then
        # the extra plays. No body is renamed here, because a reward screen
        # has no enemy list to map a combat id onto; the mod's own title
        # stands, which is the trade the carry-out block above already makes.
        if obs.get("last_salon"):
            ls = obs["last_salon"]
            out += ["", "## What your Salon did in the fight's last beat", "",
                    LAST_SALON_NOTE, ""]
            out += [_render_evoke(row) for row in ls["evoked"]]
            out += [_render_performance(row) for row in ls["performed"]]
            out += [f"- **{name}** was played an extra time, and the extra "
                    "play performed as well." for name in ls["replayed"]]
    else:                                                # pragma: no cover
        raise BlindPlayError(f"no renderer for screen {obs['screen']!r}")

    # `EB-473`: the relic row, on a screen that is not a fight, in the
    # combat header's own words and under its own heading. A relic claimed at
    # the reward of the LAST fight of a run had no later combat page to print
    # it on, and the Klee r15 run-2 seat finished holding one it could not
    # describe. Above the belt, because that is the order the combat page
    # already has -- relics, then potions.
    if obs.get("held_relics"):
        out += ["", "## Your relics", ""] + [
            f"- **{r['name']}**"
            + (f" ({r['counter']})" if r.get("counter") else "")
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
    qa_packet.assert_blind(text, allow={st})
    return text


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
