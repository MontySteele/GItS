"""The board behind the screen: combat, the pet, the meters, the map.

Cut out of `blindplay.py` by `EB-180`. Where `blindplay_faces` reads
one printed thing, this reads the ARRANGEMENT of them -- the combat
block, Kokomi's pending Plans, the Kurage's memory, the reachable map
and what each screen is offering. Re-exported from `blindplay.py`, so
`blindplay.kokomi_plans(player)` still resolves.
"""
from __future__ import annotations

from typing import Any

from understudy import qa_packet
from understudy.blindplay_faces import (_card_face, _card_title, _enemy_names,
                                        _hook_note, _intents, _meter_max,
                                        _named_option, _number_faces, _powers,
                                        relic_faces, remember_deck,
                                        remembered_deck, remembered_enemy_name)
from understudy.blindplay_read import (_blob, _enemies, _fold, _hand, _int,
                                       _label, _listing, _player, _potions,
                                       _screen, _text)
from understudy.blindplay_shape import SELECT_SCREENS


# `EB-342`. The three things a card can be missing from the Smith's grid for,
# in the order they are checked, each in the page's own plain words. The
# register that answers the second is `qa_packet.no_upgrade_index`, and only
# its ID SET crosses -- its rows' prose names ruling numbers.
# `EB-386`. THE MOD'S OWN BOOKKEEPING, KEPT OFF THE BOARD.
#
# The round-two seat: "The three meters `Spotlight Mode`, `Spotlight Moved` and
# `Spotlight Plays` appeared and disappeared in the status list all run and I
# never worked out what any of them meant." Nor could it: the wire reports
# every resource the mod REGISTERED, and these three are internal state, not a
# currency anybody holds, spends or plans around.
#
# WHY HIDDEN AND NOT DEFINED, which was the row's choice. Each of the three
# already has a surface that states its rule in words:
#
#   `Spotlight Mode` is an enum ordinal, and the two BUFFS it selects between
#     -- Center Stage and Guest Cast -- are named rows in the status list with
#     their own text and, since `EB-386`, their own duration. A number that
#     duplicates a named buff, in a spelling only the source can read, is a
#     second surface for one fact and the worse of the two. The mod-side half
#     of the row makes that buff follow the mode, so the named surface cannot
#     go missing while the number stays.
#   `Spotlight Moved` and `Spotlight Plays` are per-turn counters that back
#     card CONDITIONS, and every card that reads one prints its own condition
#     on its face. The counter is the implementation of a sentence the reader
#     already has.
#   `Spotlight Spend Boost` (`EB-422`) is the FOURTH of the same kind, found
#     the same way: "a row reading `Spotlight Spend Boost: 30` sat in the
#     status bar all fight with no gloss and no card naming it" (Furina round
#     5, run 1, fight 4). It is this turn's accumulator, and its only writer
#     is `SpotlightSystem.OnEncoreSpent`, which adds the amount of
#     `OvationSpendBoostPower` to it on each Encore spend and zeroes it at
#     turn end. That power is a NAMED status row -- "Standing Ovation --
#     Spotlighted Companions are 10% stronger on turns you spend Encore" --
#     printed by the card the player played, so the rule is already on the
#     page in its own words; 30 is three spends' worth of one 10, which is a
#     running total the sentence does not promise and the feed cannot
#     explain. The seat read the two side by side and reported exactly that:
#     "Standing Ovation says 10%; the meter said 30."
#
# So defining them would put four glossary rows on the page to explain four
# rows that should not be on the page. Keyed by the WIRE id rather than the
# printed name, because that is what the mod declares and what a rename here
# would silently stop matching.
INTERNAL_METERS = frozenset({
    "KLEEMOD_SPOTLIGHT_MODE",
    "KLEEMOD_SPOTLIGHT_MOVED",
    "KLEEMOD_SPOTLIGHT_PLAYS",
    "KLEEMOD_SPOTLIGHT_SPEND_BOOST",
})

ALREADY_UPGRADED = "already upgraded; an upgraded copy cannot be upgraded again"
NO_UPGRADE_DEFINED = "this build defines no upgrade for it"
UNEXPLAINED_OMISSION = ("on the screen's list nowhere, and nothing on the feed "
                        "says why")


def upgrade_deck_floor(state: dict[str, Any]) -> int:
    """The floor the deck behind `_omitted_from_upgrade` was read on. `0` if none."""
    return _int((remembered_deck(state) or {}).get("floor"))


def _omitted_from_upgrade(state: dict[str, Any]) -> list[dict[str, str]]:
    """Deck cards the upgrade grid does not offer, each with its reason.

    `EB-342`. The r7b act-3 Smith listed 25 cards against a deck of 35 or 36
    and explained none of the fifteen it left out.

    THE DECK COMES FROM THE LAST FIGHT, because it comes from nowhere else:
    `BuildPlayerState` sends the four piles and a selection screen is not a
    combat (`blindplay_faces.remember_deck`). So this is as stale as that
    fight, the render says so beside it, and a card drafted since is simply
    absent from both sides of the subtraction -- which is a card this page
    never claims anything about, rather than one it names wrongly.

    MATCHED ON THE PRINTED FACE, `(folded title, upgraded)`, one grid card
    consumed per deck card: three `Strike` in the deck and three on the grid
    leave nothing over, and three in the deck against two on the grid leave
    exactly one. The id is used for the REASON and never for the match, since
    a remembered pile entry and a grid entry are the same card model and the
    title is what the reader is looking at.
    """
    held = remembered_deck(state)
    if not held:
        return []
    deck = held["cards"]
    grid: list[tuple[str, bool]] = []
    for entry in _screen_cards(state):
        if isinstance(entry, dict):
            grid.append((_fold(_text(entry.get("name"))),
                         bool(entry.get("is_upgraded")
                              or entry.get("upgraded"))))
    debt = qa_packet.no_upgrade_index()
    out: list[dict[str, str]] = []
    for card in deck:
        face = (_fold(card["title"]), bool(card["upgraded"]))
        if face in grid:
            grid.remove(face)
            continue
        if card["upgraded"]:
            reason = ALREADY_UPGRADED
        elif card["key"] in debt:
            reason = NO_UPGRADE_DEFINED
        else:
            reason = UNEXPLAINED_OMISSION
        out.append({"title": card["title"], "reason": reason})
    return out


def _potion_slots(state: dict[str, Any]) -> int:
    """How many potion slots this run has (`EB-341`). `0` where none is sent.

    `BuildPlayerState` sends `max_potion_slots` beside the potion list, and
    the list holds only the FILLED slots -- a null slot is skipped. So the two
    numbers together are "2 of 3", and neither on its own is. A feed that
    sends no maximum answers 0, and every caller treats that as "this page
    cannot say", never as "no slots".
    """
    return _int(_player(state).get("max_potion_slots"), 0)


def _combat(state: dict[str, Any]) -> dict[str, Any]:
    p = _player(state)
    resources = p.get("resources")
    battle = _blob(state, "battle")
    # `EB-342`: the four piles ARE the deck while a fight is up, and the
    # Smith's screen two rooms later has no deck on its own feed. Remembered
    # here, on the one screen that carries it, and read back there.
    remember_deck(state)
    combat = {
        "you": {
            "hp": _int(p.get("hp")), "max_hp": _int(p.get("max_hp")),
            "block": _int(p.get("block")), "energy": _int(p.get("energy")),
            "max_energy": _int(p.get("max_energy")),
            # NON-ZERO ONLY, for `qa_packet.build`'s reason: the wire reports
            # every meter the mod REGISTERED, so a board with no Spotlight on
            # it would otherwise print "Spotlight Mode: 0" and teach the tester
            # something this screen does not show.
            # `EB-386`: and NOT the mod's own bookkeeping. See
            # `INTERNAL_METERS`.
            "meters": ({_label(k): _int(v) for k, v in resources.items()
                        if _int(v) and k not in INTERNAL_METERS}
                       if isinstance(resources, dict) else {}),
            # `EB-181`: the CEILING beside the amount, per meter, where the
            # meter declares one. `{printed name: max}`, and a meter that
            # declares none is simply absent from this map -- so the row for
            # it keeps saying, honestly, that the feed reports no maximum.
            "meter_max": _meter_max(p),
            "powers": _powers(p),
            "potions": [{"title": _text(x.get("name")),
                         "text": _text(x.get("description"))}
                        for x in _potions(state)],
            # `EB-341`: how many slots there are, which the wire has always
            # carried (`max_potion_slots`, `BuildPlayerState`) and the page
            # never printed. A tester who cannot see three-of-three cannot
            # know a fourth potion has nowhere to go.
            "potion_slots": _potion_slots(state),
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
        # `EB-271`: numbered through the fight's memory, not by place in the
        # list the feed happens to be sending this screen.
        "enemies": [{"name": name,
                     "hp": _int(e.get("hp")),
                     "max_hp": _int(e.get("max_hp", e.get("hp"))),
                     "block": _int(e.get("block")),
                     # `EB-342`: EVERY component of the telegraph, not the
                     # first. A move that attacks and also puts four Burns in
                     # hand is two intents on the wire and was one line here.
                     "intents": _intents(e.get("intents") or e.get("intent")),
                     "powers": _powers(e)}
                    for e, name in zip(_enemies(state),
                                       _enemy_names(_enemies(state)))],
    }
    # `EB-271`: the refusal that named nothing, given the board it is about.
    for face in combat["hand"]:
        face["unplayable_note"] = _hook_note(face, combat["you"]["powers"])
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
        # `EB-329`: the mod names a moved enemy by its combat id, and THE
        # PAGE OWNS THE NAMES -- `_enemy_names` numbers repeats and keeps the
        # numbers for the fight, so `Toadpole (2)` has to mean the same body
        # in the Bake-Kurage's receipt as in the enemy list four lines down.
        name_moved_rows(plans, _enemies(state), combat["enemies"])
        combat["plans"] = plans
    salon = furina_salon(p)
    if salon is not None:
        # `EB-405`, and it is `EB-329`'s rule one arm over: the mod names the
        # body it hit by combat id and THE PAGE OWNS THE NAMES, so `Slug (2)`
        # in a performance line means the same body as `Slug (2)` in the enemy
        # list under it.
        name_performances(salon, _enemies(state), combat["enemies"])
        combat["salon"] = salon
    return combat


def furina_salon(player: dict[str, Any]) -> dict[str, Any] | None:
    """This turn's Salon performances, as the observed board sees them.

    `EB-405`. THE DEFECT, in the seat's own words: "Crabaletta chose its own
    enemy and left a Hydro aura on a body the seat had not picked" (Furina
    round 4, run 1, (c) 4), in a kit whose readable decision is which element
    lands on which aura. Nothing about that reached the page, because nothing
    about it reached the wire: the only Salon row on a screen was the counter
    power's static rulebook sentence, which carries the company COUNT and
    cannot carry a body.

    THE ABSENT / EMPTY SPLIT IS `kokomi_plans`', and for the same reason: an
    ABSENT key is "no reframe in this build", an EMPTY map is "the rule is here
    and this seat is not playing it", and a populated map is her stage. `None`
    here keeps the section off the page in both of the first two cases.

    Emitted by `vendor/STS2_MCP/gits/GitsFurinaSalon.cs`, which lifts it by
    reflection from `KleeMod.Powers.FurinaReframeLedger.Snapshot`. Every field
    below is that method's, and the two together are the contract:

      performed -- this turn's acts, in the order they happened. `member` is
        the stage name the faces use; `target` and `combat_id` are the body the
        member PICKED, both null for the Usher, who blocks and aims at nobody;
        `element` is what the member supplied and `aura` is what the body is
        wearing AFTERWARDS, which are not the same fact -- a hit into a
        different aura consumes it into a reaction and leaves the body bare;
        `amount` is the number it dealt or blocked and `paid` is whether it
        could afford its Encore, which is the difference between the printed
        number and three-quarters of it.

      replayed -- `EB-420`. This turn's Companion cards that were played an
        EXTRA time, by printed title, one entry per extra play. The extra play
        makes nobody perform -- the trigger is once per Companion card played,
        LAW:145's bound -- so these are the plays that are missing from
        `performed`, and a reader given only that list would count the stage's
        acts and reach the wrong rule. The round-5 seat did exactly that: "two
        Crabaletta lines ... for three Companion-card plays' worth of
        triggers", and "no line anywhere on the screen said Duet".
    """
    raw = player.get("furina_salon")
    if not isinstance(raw, dict) or not raw:
        return None
    performed = [
        {"member": _text(row.get("member")),
         "target": _text(row.get("target")),
         "combat_id": _text(row.get("combat_id")),
         "element": _text(row.get("element")),
         "aura": _text(row.get("aura")),
         "amount": _int(row.get("amount")),
         "paid": bool(row.get("paid"))}
        for row in (raw.get("performed") or []) if isinstance(row, dict)]
    replayed = [name for name in
                (_text(entry) for entry in (raw.get("replayed") or []))
                if name]
    return {"performed": performed, "replayed": replayed}


def name_performances(salon: dict[str, Any], wire: list[dict[str, Any]],
                      printed: list[dict[str, Any]]) -> None:
    """Resolve each performance's combat id to the name this page uses.

    `EB-405`, and it is `name_moved_rows` verbatim: THE ID IS THE HANDLE AND
    THE NAME IS THE FALLBACK. A body still on the board gets the page's own
    numbered name; one the performance KILLED is off the next board entirely
    and keeps the title the mod recorded, which is why the mod sends a title
    at all.

    `EB-424`, AND IT IS `EB-427` ONE ARM OVER. The mod's title is the game's
    printed name and carries no copy number, so the r5 seat read
    *"Crabaletta hit Corpse Slug (2)"* on turn 1 and *"Crabaletta hit Corpse
    Slug"* on turn 2 -- "in a two-of-a-kind fight I could not tell which body
    it hit" -- for the one reason that the second body was no longer on the
    board. The fight's own memory names it, so a performance on a duplicate
    always says which copy.
    """
    by_id = {_text(raw.get("combat_id")): face["name"]
             for raw, face in zip(wire, printed)
             if _text(raw.get("combat_id"))}
    for row in salon["performed"]:
        if not row["combat_id"]:
            continue
        row["target"] = (by_id.get(row["combat_id"])
                         or remembered_enemy_name(row["combat_id"],
                                                  row["target"]))


def name_moved_rows(plans: dict[str, Any], wire: list[dict[str, Any]],
                    printed: list[dict[str, Any]]) -> None:
    """Resolve each moved row's combat id to the name this page uses.

    `EB-329`. THE ID IS THE HANDLE AND THE NAME IS THE FALLBACK, the split
    `KokomiPlan.MovedOn` documents from the other side. A body still on the
    board gets the page's own numbered name; one that DIED to the Plan is off
    the next board entirely and keeps the title the mod recorded, which is
    the whole reason the mod sends a title at all.

    `EB-427` PUT THE FIGHT'S MEMORY BETWEEN THE TWO. The mod's title carries no
    copy number, so a morning against three Inklets that killed one printed
    `Inklet`, `Inklet (1)` and `Inklet (2)` -- three bodies, two handles and one
    bare word -- and the r11 seat read the mix as the numbering having shifted.
    `remembered_enemy_name` hands back the name this page used while that body
    stood, so the receipt and the enemy list under it never disagree.
    """
    by_id = {_text(raw.get("combat_id")): face["name"]
             for raw, face in zip(wire, printed)
             if _text(raw.get("combat_id"))}
    for row in plans["carried_out"] + plans["fired_now"]:
        for moved in row["moved"]:
            moved["target"] = (by_id.get(moved["combat_id"])
                               or remembered_enemy_name(moved["combat_id"],
                                                        moved["target"]))


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
      carried_out -- `EB-317`: what the jellyfish has already done THIS TURN,
        in the order it did it. Each row carries `card`, the `number` its
        clause produced (null when it produced none) and `line`, THE STRING THE
        SPEECH BUBBLE SAID over the pet's head. The page prints `line`
        verbatim: the mod builds the sentence once (`Vfx.KurageBeat.Line`) so a
        seat's page and a sighted player's screen cannot come to disagree about
        the words. `_carry_out_line` recomposes it only when an older build
        sends the parts without the sentence.

        `EB-329` adds two per row. `moved` is WHAT THE BOARD DID -- each
        enemy's HP loss across the whole Plan, measured by the mod rather than
        read off a clause, so the Casket's answering strikes and a reaction's
        damage are inside it. `on_play` is which door the Plan came through,
        and it splits this list in two here: `carried_out` keeps the MORNING
        and `fired_now` takes Change of Plans and The Moon Overlooks the
        Waters, because "at the start of this turn" is a false sentence about
        a Plan that fired as it was written.
    """
    raw = player.get("kokomi_plans")
    if not isinstance(raw, dict) or not raw:
        return None
    queue = [{"name": _text(row.get("name")),
              "clauses": _int(row.get("clauses"))}
             for row in (raw.get("queue") or []) if isinstance(row, dict)]
    pet_id = raw.get("pet_entity_id")
    pet_name = _text(raw.get("pet_name")) or "Bake-Kurage"
    said = [_carried_out_row(row, pet_name)
            for row in (raw.get("carried_out") or [])
            if isinstance(row, dict)]
    return {
        "pet": bool(raw.get("pet")),
        "pet_name": pet_name,
        "pet_entity_id": None if pet_id is None else _text(pet_id),
        "pending": _int(raw.get("pending")),
        "twice": bool(raw.get("twice")),
        "also_now": bool(raw.get("also_now")),
        "queue": queue,
        "carried_out": [row for row in said if not row["on_play"]],
        "fired_now": [row for row in said if row["on_play"]],
    }


def _carried_out_row(row: dict[str, Any], pet_name: str) -> dict[str, Any]:
    """One carried-out Plan, as the screen said it (`EB-317`).

    THE MOD'S SENTENCE WINS. `line` is what the bubble carried, so it is
    printed as sent and never reassembled from `card` and `number` when it is
    there. The fallback exists for one case and is written for it: a build
    whose wire predates the field, where printing nothing would be worse than
    printing the same format the mod uses.

    `board_read` IS THE THIRD STATE, and `EB-329` needs it because the other
    two are not enough: "every enemy came through untouched" and "this bridge
    predates the measurement" are different facts, and a page that printed
    "nothing moved" for the second would be inventing a board. An ABSENT
    `moved` key answers False and the row prints exactly what it printed
    before this change; a present-and-empty one answers True and the row can
    say the Plan moved no HP, which for a Draw or a Block Plan is the honest
    and useful receipt.
    """
    number = row.get("number")
    number = None if number is None else _int(number)
    card = _text(row.get("card"))
    line = _text(row.get("line"))
    if not line:
        line = (f"{pet_name}: {card}" if number is None
                else f"{pet_name}: {card}, {number}")
    # `EB-426`: WHAT THE NUMBER IS, and what its clause asked for. Both are
    # `KokomiPlan.NumberKind` / `AskedFor`'s, and both are ABSENT on a bridge
    # older than the field -- which prints exactly the line it always printed,
    # `board_read`'s discipline again.
    asked = row.get("asked")
    raw_moved = row.get("moved")
    return {"card": card, "number": number, "line": line,
            "kind": _text(row.get("kind")),
            "asked": None if asked is None else _int(asked),
            "on_play": bool(row.get("on_play")),
            "board_read": isinstance(raw_moved, list),
            # `EB-440`: A ROW IS A BODY THIS PLAN MOVED SOMETHING ON, and
            # Block is something. The filter existed to drop the mod's
            # zero-delta rows, and a beat that spent itself entirely on a
            # Defend intent produces exactly such a row with the Block beside
            # it -- which is the receipt the r12 seat did not get.
            "moved": [_moved_row(m) for m in (raw_moved or [])
                      if isinstance(m, dict)
                      and (_int(m.get("amount")) > 0
                           or _int(m.get("absorbed")) > 0)]}


def last_morning(state: dict[str, Any]) -> dict[str, Any] | None:
    """The last carry-out of a fight that is already over (`EB-329`).

    THE SAME SNAPSHOT, READ ON A SCREEN WITH NO COMBAT BEHIND IT. Everything
    else in `kokomi_plans` is about a live board -- the pending queue, the
    pet, Nereid's window -- and none of it means anything here, so this
    returns the carry-out lines alone. The queue in particular is deliberately
    dropped: a fight that ended mid-turn can leave Plans pending, and "carried
    out at the start of your next turn" is a promise about a fight that no
    longer exists.

    `None` where there is nothing to say, which covers a build with no Plan
    rule, a seat that is not Kokomi, a bridge that predates the out-of-combat
    emission, and a fight whose last turn carried nothing out.
    """
    plans = kokomi_plans(_player(state))
    if plans is None:
        return None
    said = plans["carried_out"] + plans["fired_now"]
    if not said:
        return None
    return {"pet_name": plans["pet_name"], "carried_out": plans["carried_out"],
            "fired_now": plans["fired_now"]}


def _moved_row(row: dict[str, Any]) -> dict[str, Any]:
    """One enemy's share of one Plan (`EB-329`), off `KokomiPlan.MovedRow`.

    `target` is the mod's own read of the creature's title and is REPLACED by
    `name_moved_rows` wherever the body is still on the board, so a reader is
    handed the numbered name this page has been using all fight. Where the
    game would not answer either, the row says so in words rather than
    printing a bare number against nothing.

    `EB-440` ADDED `absorbed`, AND THE ABSENT / ZERO SPLIT IS THE ONE
    `board_read` MAKES ONE LEVEL UP. A bridge older than the measurement sends
    no key at all and this page must not print a Block figure for it; a bridge
    that sends 0 measured the Block and found none. So an absent key answers
    `None` and a present one answers its number.
    """
    absorbed = row.get("absorbed")
    return {"target": _text(row.get("target")) or "an enemy",
            "combat_id": _text(row.get("combat_id")),
            "amount": _int(row.get("amount")),
            "dead": bool(row.get("dead")),
            "absorbed": None if absorbed is None else _int(absorbed)}


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
    raw = _map_nodes(state)
    nodes = [_named_option(n) for n in raw]
    for i, (entry, o) in enumerate(zip(raw, nodes), 1):
        o["name"] = f"{o['name'] or 'Path'} (path {i})"
        # `EB-298`: the wire's OWN one-level lookahead, which nothing read.
        # `BuildMapState` puts each travelable point's children on the option
        # as `leads_to`, room type and all, so the page can say what a fork
        # opens onto instead of leaving the tester to pick blind.
        leads = [_label((c or {}).get("type"))
                 for c in (entry.get("leads_to") or [])
                 if isinstance(c, dict)]
        if leads:
            o["text"] = "leads on to: " + ", ".join(leads)
    return nodes


def _map_ahead(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Every floor between here and the boss, nearest first (`EB-298`).

    THE WHOLE MAP IS ON THE WIRE AND THE PAGE PRINTED TWO NODES OF IT.
    `BuildMapState` sends `nodes` -- every point of the act with its `col`,
    its `row`, its room `type` and its `children` -- plus `current_position`,
    `visited`, and a `boss` block carrying the boss's own printed name. The
    render read `next_options` and nothing else, so the r2 Opus seat had "no
    floors ahead and no elite/shop/campfire distinction, so route choice is a
    coin flip", and took an `Unknown` that turned out to be an event.

    A row is a floor, and the direction of travel is read rather than
    assumed: the next options sit one step from where you are, so their row
    against the current row says which way the numbers run. With no current
    position on the feed the nearest next option is the datum and travel is
    taken to run away from it in the same direction, which is the only
    reading a single row supports.

    THIS IS WHAT A SIGHTED PLAYER SEES, and no more: the rooms on each floor,
    in the order they are drawn left to right. It is not a route -- the
    `children` edges that would make one are on the feed too, and printing a
    reachability graph as prose is a page nobody can read. The floors and the
    one-level `leads_to` on each option are what the seat asked for.
    """
    nodes = [n for n in _listing(state, "map.nodes", "nodes")
             if isinstance(n, dict)]
    if not nodes:
        return []
    options = [n for n in _map_nodes(state) if isinstance(n, dict)]
    here = _blob(state, "map").get("current_position")
    here_row = (_int(here.get("row"), -1) if isinstance(here, dict) else -1)
    option_rows = sorted({_int(o.get("row"), -1) for o in options
                          if o.get("row") is not None})
    if not option_rows:
        return []
    step = 1 if here_row < 0 or option_rows[0] > here_row else -1
    if here_row < 0:
        here_row = option_rows[0] - step

    floors: dict[int, list[tuple[int, str]]] = {}
    for node in nodes:
        row, col = _int(node.get("row"), -1), _int(node.get("col"), -1)
        if row < 0 or (row - here_row) * step <= 0:
            continue
        kind = _label(node.get("type"))
        if kind:
            floors.setdefault(row, []).append((col, kind))
    # A floor is named by its DISTANCE and never by the wire's `row`. The row
    # is a grid coordinate: nothing on the feed says it is the floor number
    # the game prints, and a page that guessed would be teaching the tester a
    # coordinate -- which is the one thing `_map_options` exists not to do.
    return [{"floors_ahead": (row - here_row) * step,
             "kinds": [k for _, k in sorted(floors[row])]}
            for row in sorted(floors, key=lambda r: (r - here_row) * step)]


def _map_boss(state: dict[str, Any]) -> str:
    """The boss at the top of this act, by its PRINTED name (`EB-298`).

    `AddBossIdentity` writes both an `id` and a `name` and only the second one
    is a thing the game prints, so only the second one is read. A `bosses`
    list with a second entry means the act has two and both are named.
    """
    blob = _blob(state, "map")
    bosses = [b for b in (blob.get("bosses") or [blob.get("boss")])
              if isinstance(b, dict)]
    return ", ".join(n for n in (_text(b.get("name")) for b in bosses) if n)


def _bundle_cards(bundle: Any) -> list[dict[str, Any]]:
    """The cards inside one bundle entry, in the order the wire lists them."""
    if not isinstance(bundle, dict):
        return []
    return [c for c in (bundle.get("cards") or []) if isinstance(c, dict)]


def _selected_bundle(bundles: list[dict[str, Any]],
                     preview: list[dict[str, Any]]) -> int:
    """Which bundle the preview is showing, or `-1` (`EB-294`).

    The preview holds CARDS, not a bundle index, so the pick is the bundle
    whose printed titles are the preview's -- as a multiset, because a bundle
    may hold two copies of one card. Two bundles that print the same titles
    are not told apart and answer `-1`: the render then says a pick has
    landed and that the page cannot say which, which is the same honesty the
    enchant picker gets and for the same reason.
    """
    want = sorted(_fold(_card_title(c)) for c in preview)
    if not want:
        return -1
    hits = [i for i, b in enumerate(bundles)
            if sorted(_fold(_card_title(c)) for c in _bundle_cards(b)) == want]
    return hits[0] if len(hits) == 1 else -1


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
