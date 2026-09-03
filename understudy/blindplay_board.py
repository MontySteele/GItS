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
                                        _hook_note, _intent, _meter_max,
                                        _named_option, _number_faces, _powers,
                                        relic_faces)
from understudy.blindplay_read import (_blob, _enemies, _fold, _hand, _int,
                                       _label, _listing, _player, _potions,
                                       _screen, _text)
from understudy.blindplay_shape import SELECT_SCREENS


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
            # `EB-181`: the CEILING beside the amount, per meter, where the
            # meter declares one. `{printed name: max}`, and a meter that
            # declares none is simply absent from this map -- so the row for
            # it keeps saying, honestly, that the feed reports no maximum.
            "meter_max": _meter_max(p),
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
        # `EB-271`: numbered through the fight's memory, not by place in the
        # list the feed happens to be sending this screen.
        "enemies": [{"name": name,
                     "hp": _int(e.get("hp")),
                     "max_hp": _int(e.get("max_hp", e.get("hp"))),
                     "block": _int(e.get("block")),
                     "intent": _intent(e.get("intents") or e.get("intent")),
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
      carried_out -- `EB-317`: what the jellyfish has already done THIS TURN,
        in the order it did it. Each row carries `card`, the `number` its
        clause produced (null when it produced none) and `line`, THE STRING THE
        SPEECH BUBBLE SAID over the pet's head. The page prints `line`
        verbatim: the mod builds the sentence once (`Vfx.KurageBeat.Line`) so a
        seat's page and a sighted player's screen cannot come to disagree about
        the words. `_carry_out_line` recomposes it only when an older build
        sends the parts without the sentence.
    """
    raw = player.get("kokomi_plans")
    if not isinstance(raw, dict) or not raw:
        return None
    queue = [{"name": _text(row.get("name")),
              "clauses": _int(row.get("clauses"))}
             for row in (raw.get("queue") or []) if isinstance(row, dict)]
    pet_id = raw.get("pet_entity_id")
    pet_name = _text(raw.get("pet_name")) or "Bake-Kurage"
    carried_out = [_carried_out_row(row, pet_name)
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
        "carried_out": carried_out,
    }


def _carried_out_row(row: dict[str, Any], pet_name: str) -> dict[str, Any]:
    """One carried-out Plan, as the screen said it (`EB-317`).

    THE MOD'S SENTENCE WINS. `line` is what the bubble carried, so it is
    printed as sent and never reassembled from `card` and `number` when it is
    there. The fallback exists for one case and is written for it: a build
    whose wire predates the field, where printing nothing would be worse than
    printing the same format the mod uses.
    """
    number = row.get("number")
    number = None if number is None else _int(number)
    card = _text(row.get("card"))
    line = _text(row.get("line"))
    if not line:
        line = (f"{pet_name}: {card}" if number is None
                else f"{pet_name}: {card}, {number}")
    return {"card": card, "number": number, "line": line}


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
