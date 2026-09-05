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
from understudy.blindplay_board import _pulse_phrase
from understudy.blindplay_notes import (AURA_NOTE,
                                        CARD_REWARD_ALTERNATIVE_NOTE,
                                        CARRY_OUT_BOARD_NOTE,
                                        DEFEND_INTENT_CLAUSE,
                                        ENEMY_HANDLE_NOTE,
                                        HAND_REPEAT_NOTE,
                                        LAST_MORNING_NOTE,
                                        METER_CAPPED_NOTE,
                                        METER_DEFINED_NOTE, METER_NOTE,
                                        METER_RULES,
                                        MULTI_INTENT_LABEL,
                                        MULTI_INTENT_NOTE,
                                        PENDING_PICK_NOTE, PICKED_MARK,
                                        PLAN_AIM_NOTE,
                                        PLAN_HYDRO_NOTE,
                                        POWER_NOTE, SELECTION_NOTE,
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
    if c.get("upgraded_face"):
        out.append(f"    Upgraded: {c['upgraded_face']}")
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

    `EB-329`. TWO HEADINGS, BECAUSE THEY ARE TWO MOMENTS. The r4c seat played
    War Council with The Moon Overlooks the Waters out and was told on one
    screen both that the jellyfish "carried these out at the start of this
    turn" and that War Council was still planned; the first was simply not
    true of that resolution. Change of Plans is the same door -- its own face
    says "carries out your front Plan NOW" -- so both are filed together,
    under a sentence that says WHEN.
    """
    out: list[str] = []
    if pl["carried_out"]:
        out.append(f"- The {pl['pet_name']} carried these out at the "
                   "start of this turn, front first:")
        out += _carry_out_rows(pl["carried_out"])
    if pl["fired_now"]:
        out.append(f"- The {pl['pet_name']} carried these out THIS TURN, the "
                   "moment each was written, and not this morning:")
        out += _carry_out_rows(pl["fired_now"])
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

    ABSENT IS NOT EMPTY, this section's standing rule: a bridge with no
    `riders` key sends none, and the row reads exactly as it always did.
    """
    riders = said.get("riders") or []
    if not riders:
        return ""
    named = ", ".join(f"{r['source']} {r['amount']}" for r in riders)
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


def _board_note_wanted(pl: dict[str, Any]) -> bool:
    """Is a board reading on this screen at all? (`EB-329`)

    The note explains the two numbers under a Plan, so it is printed where
    both are and nowhere else -- a bridge older than the measurement prints
    the lines it always printed and no footnote about numbers it does not
    carry. It goes at the END of the section rather than under the last Plan,
    where the indent made it read as a fact about that one card.
    """
    return any(said["board_read"]
               for said in pl["carried_out"] + pl["fired_now"])


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


def _render_power(power: dict[str, Any], indent: str) -> str:
    """One power: printed name, the amount, buff or debuff, the printed text.

    `EB-467`: where the amount is an allowance counting down against a cap the
    power's own sentence states, the two numbers print in ONE clause -- "12 of
    20 left this turn" -- instead of standing apart and contradicting.
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
        line += f" — {power['text']}"
    return line


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
    if _fold(kind) == "defend":
        bits.append(DEFEND_INTENT_CLAUSE)
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
            if top:
                out.append(f"- {name}: {amount}/{top} — "
                           f"{rule or METER_CAPPED_NOTE}")
            else:
                out.append(f"- {name}: {amount} — {rule or METER_NOTE}")
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
                # `EB-442`: WHERE a Plan lands, then `EB-378`'s whose hit
                # it is -- both under the pet's own line, because both are
                # facts about the jellyfish's carry-out rather than about any
                # one Plan in the queue below. The aim rule leads: a reader
                # asking what a Plan will do asks which body first.
                out.append(PLAN_AIM_NOTE)
                out.append(PLAN_HYDRO_NOTE)
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
            # `EB-329`: which of the two numbers under a Plan is which, once,
            # at the foot of the section rather than under the last card.
            if _board_note_wanted(pl):
                out += ["", CARRY_OUT_BOARD_NOTE]
        if c.get("salon") and (c["salon"]["performed"]
                               or c["salon"]["replayed"]):
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
        out += ["", "## The other side", ""]
        for e in c["enemies"]:
            # `EB-496`: the letter in brackets after the name, where the card
            # face already carries its element -- the handle at a glance,
            # before the numbers.
            line = f"- **{e['name']}**"
            if e.get("handle"):
                line += f" [{e['handle']}]"
            line += f" — HP {e['hp']}/{e['max_hp']}"
            if e["block"]:
                line += f", Block {e['block']}"
            out.append(line)
            out += _render_intents(e["intents"])
            for pw in e["powers"]:
                out.append(_render_power(pw, "    "))
        # `EB-496`: and the rule about both handles, under the list they are
        # handles for. The hand's own note is about cards and says the
        # opposite, which is what sent a seat's Melt into the wrong body.
        if c["enemies"]:
            out += ["", ENEMY_HANDLE_NOTE]
        # `EB-461`: ONCE PER SCREEN, and only where a telegraph has parts. The
        # note is about a claim the enemy block just made, so it sits with the
        # block's other two notes rather than under the line that made it.
        if any(len(e["intents"]) > 1 for e in c["enemies"]):
            out += ["", MULTI_INTENT_NOTE]
        if you["powers"] or any(e["powers"] for e in c["enemies"]):
            out += ["", POWER_NOTE]
        if any(p.get("kind") == "aura"
               for p in you["powers"] + [x for e in c["enemies"]
                                         for x in e["powers"]]):
            out += ["", AURA_NOTE]
    elif obs["screen"] == "map":
        out += ["# The map", "",
                "Where you can go next:", ""] + _render_options(obs["nodes"])
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
        # `EB-341`: said on the screen where the claim is made, and only where
        # a potion is actually on offer -- a run with a free slot reads
        # exactly as it always did.
        if obs.get("potion_offered") and obs.get("potion_slots") \
                and obs["potions_held"] >= obs["potion_slots"]:
            out += ["", f"*Your potion slots are full: "
                        f"{obs['potions_held']} of {obs['potion_slots']}. A "
                        f"potion claimed now has nowhere to go, and the game "
                        f"says nothing when one is dropped -- so this page "
                        f"will not claim it until a slot is free.*"]
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
        out += [f"- **{k['name']}** — {k['text']}" for k in obs["keywords"]]

    out += ["", "## What you can say", ""]
    out += [f"- `{c}`" for c in obs["commands"]]
    out += ["", obs["guardrail"], ""]
    text = "\n".join(out).rstrip() + "\n"
    qa_packet.assert_blind(text, allow={st})
    return text


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
