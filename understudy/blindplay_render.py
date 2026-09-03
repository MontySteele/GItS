"""The observation as the page the tester is handed. Same content.

Cut out of `blindplay.py` by `EB-180`: `render`, the notes it prints
beside a screen, the arm-keyword register and `observe` (the two
composed). Re-exported from `blindplay.py`, so `blindplay.render(obs)`
and `blindplay.observe(state)` still resolve.
"""
from __future__ import annotations

import hashlib
from typing import Any

from understudy import qa_packet

from understudy.blindplay_board import _pulse_phrase
from understudy.blindplay_notes import (AURA_NOTE, HAND_REPEAT_NOTE,
                                        METER_CAPPED_NOTE, METER_NOTE,
                                        POWER_NOTE, SELECTION_NOTE,
                                        TRANSFORM_NOTE, TRANSFORM_UNREADABLE)
from understudy.blindplay_observe import observation
from understudy.blindplay_read import _fold
from understudy.blindplay_shape import (BlindPlayError, CHARGE_SOURCE_LINE,
                                        FIGHT_OVERLAYS, KURAGE_COST_PER_ENERGY)


# ----------------------------------------------------------------- render --

def _render_card(c: dict[str, Any], bullet: str = "-") -> list[str]:
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
        # `EB-271`: and the clause that stops the vague one being vague, on
        # its own line under it, because it is this page's sentence and not
        # the game's.
        if c.get("unplayable_note"):
            out.append(f"    {c['unplayable_note']}")
    return out

def _render_power(power: dict[str, Any], indent: str) -> str:
    """One power: printed name, the amount, buff or debuff, the printed text."""
    line = f"{indent}{power['name']} {power['stacks']}"
    kind = str(power.get("kind") or "").strip().lower()
    if kind:
        line += f" ({kind})"
    if power["text"]:
        line += f" — {power['text']}"
    return line


def _render_intent(intent: dict[str, str]) -> str:
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
    """
    head = intent.get("kind") or intent.get("type") or ""
    kind = intent.get("type") or ""
    if head and kind and _fold(head) != _fold(kind):
        head = f"{head} ({kind})"
    bits = [head, (f"the number on its icon is {intent['label']}"
                   if intent.get("label") else ""), intent.get("text") or ""]
    return " — ".join(b for b in bits if b) or "(no intent shown)"


def _render_options(items: list[dict[str, Any]], bullet: str = "-") -> list[str]:
    out = []
    for o in items:
        line = f"{bullet} **{o['name'] or '(unnamed)'}**"
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
            # `EB-181`: with a ceiling the row reads like the HP and Energy
            # rows above it and the note narrows to the half still true; with
            # none it is exactly the row it always was.
            top = you.get("meter_max", {}).get(name)
            if top:
                out.append(f"- {name}: {amount}/{top} — {METER_CAPPED_NOTE}")
            else:
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
            # `EB-317`. WHAT ALREADY HAPPENED, BEFORE WHAT IS STILL WAITING,
            # because that is the order the turn had: the morning's Plans were
            # carried out at the top of this turn and the queue below is what
            # the player has written since. Each line is the mod's own string
            # -- the words the speech bubble put over the jellyfish's head --
            # printed verbatim, which is the whole point of the field. The
            # meter ledger is NOT here and must not be (`R101b`): this is what
            # a sighted player saw, not an instrument's rows.
            if pl["carried_out"]:
                out.append(f"- The {pl['pet_name']} carried these out at the "
                           "start of this turn, front first:")
                for said in pl["carried_out"]:
                    out.append(f"  - {said['line']}")
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
            out.append(f"    Intent: {_render_intent(e['intent'])}")
            for pw in e["powers"]:
                out.append(_render_power(pw, "    "))
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
    elif obs["screen"] in ("card_reward", "card_select"):
        out += [f"# {obs['prompt']}", ""]
        for card in obs["offers"]:
            out += _render_card(card)
        if obs["screen"] == "card_select":
            if obs.get("selected"):
                out += ["", "## What you have picked", ""]
                for card in obs["selected"]:
                    out += _render_card(card)
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
            out += ["", f"Confirm is {'available' if obs['can_confirm'] else 'not available'}."]
        # `EB-314`: over an open preview `skip` does not leave the screen --
        # it cancels the pick and puts the grid back (`ExecuteCancelSelection`
        # presses the preview's own Cancel), so the page says which one it is.
        if obs.get("can_skip") and obs.get("preview_showing"):
            out += ["", "You may say `skip` to undo this pick and choose "
                        "again; it does not leave the screen."]
        elif obs.get("can_skip"):
            out += ["", "You may skip this."]
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
    else:                                                # pragma: no cover
        raise BlindPlayError(f"no renderer for screen {obs['screen']!r}")

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
