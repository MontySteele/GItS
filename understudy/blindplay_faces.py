"""One card, one option, one enemy, as the game prints it.

Cut out of `blindplay.py` by `EB-180`: the field-by-field readers that
turn a wire blob into a printed FACE -- a card, a shop shelf, a relic,
a power, a telegraph, an enemy's numbered name. Re-exported from
`blindplay.py`, so `blindplay._card_face(entry)` and
`blindplay.forget_fight()` still resolve.

TWO MODULE-LEVEL MEMORIES LIVE HERE, and they live here because their
readers do: the shop's shelves (`_SHELF_MEMORY`) and the fight's enemy
ordinals (`_FIGHT_MEMORY`). `forget_shelves` and `forget_fight` are
their resets and are beside them.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import field
from pathlib import Path
from typing import Any

from understudy import qa_packet
from understudy.blindplay_read import (_blob, _entity_id, _fold, _int, _label,
                                       _listing, _number_names, _relics,
                                       _screen, _text)
from understudy.blindplay_shape import HAZARD_EVENT_TITLES, HAZARD_EVENTS


def relic_faces(state: dict[str, Any]) -> list[dict[str, str]]:
    """The run's relics as PRINTED name and one-line effect. `EB-238`.

    THE DEFECT THIS CLOSES. Until now the page showed a relic on the reward
    and relic-select screens -- the moment it is OFFERED -- and never again.
    So a blind reader played every combat of a run without the one part of
    the board that is on screen for the whole of it, and `KLEESPARK-BT1`
    §22.4 is what that cost: Klee's starter *Pounding Surprise* pays +1 Spark
    per Bomb detonated, the priced mode under test placed three Bombs, and
    the mode REFUNDED ITS OWN PRICE inside the turn in front of eight readers
    none of whom could see why. A registration cannot control a relic the
    page does not print.

    IT PRINTS WHAT THE GAME PRINTS AND NOTHING ELSE (R217's quarantine): the
    relic's own title and its own hover description, off the wire, exactly as
    the HUD shows them on a mouse-over. No id, no rarity, no pool, no sim
    hook name -- and the `counter` the wire carries only when the relic draws
    one on its own icon.
    """
    out: list[dict[str, str]] = []
    for r in _relics(state):
        name = _text(r.get("name")) or _label(r.get("id"))
        if not name:
            continue
        row = {"name": name, "text": _text(r.get("description"))}
        counter = r.get("counter")
        if counter is not None:
            row["counter"] = _text(counter)
        out.append(row)
    return out


def _hazard(state: dict[str, Any]) -> tuple[str, str] | None:
    """`(id, why)` when this event is on the hazard register, else `None`.

    Matched on the wire id first and the display title second -- the same
    read-by-id-then-by-name shape `soak._hazard_event` uses, and for the same
    reason: a title is loc data that a wording pass moves, and a screen this
    tool must not drive is worth catching twice.
    """
    if _screen(state) != "event":
        return None
    ev = _blob(state, "event")
    ident = str(ev.get("event_id") or "").strip().upper()
    if ident in HAZARD_EVENTS:
        return ident, HAZARD_EVENTS[ident]
    by_title = HAZARD_EVENT_TITLES.get(_text(ev.get("event_name")).lower())
    if by_title:
        return by_title, HAZARD_EVENTS.get(by_title, "on the hazard register")
    return None


# ------------------------------------------------------- printed fragments --

# THE ELEMENT, AS A TAG ([USER], 2026-09-01, after playing Klee: "instead of
# saying 'applies pyro' - maybe make it a card indicator as well to remove text
# overhead? That would be a universal shift").
#
# The game now says it with a picture: `KleeKeywords.Applies*` moved to
# `AutoKeywordPosition.None`, so `Applies Pyro` left the rules box and
# `Vfx/ElementBadge.cs` paints the aura's own icon beside the type plaque
# instead. A picture does not cross this wire. The seat reading this page would
# have lost the element from the card LINE and kept it only in the keyword
# block below -- so the tag puts it back where the indicator is, at a glance,
# beside the title.
#
# READ OFF THE KEYWORD, which is the same declaration the badge reads. The wire
# sends a card's keywords resolved (`CardModel.HoverTips` walks `Keywords`, and
# that walk is untouched by the position flip), so `Applies Pyro` is still on
# every elemental face as a keyword row and this is the surface that survives.
# No bridge change, and it reads correctly against a build from either side of
# the flip.
#
# ANCHORED AND ONE WORD WIDE: `Applies Electro-Charged`, a Kokomi companion's
# printed reaction, is not an element and must not become one.
#
# `EB-454` PUT ANEMO AND GEO IN THE MAP. They leave no aura, so they get no gem
# and had no `Applies` keyword either -- and the r13 seat read `Jean -- Gale
# Blade` as untyped "until a Reaction preview named Anemo mid-fight", on a page
# where every other element prints beside the title. The gem is still four
# (`ElementBadge.IconPathFor` answers null for both); the WORD is six, because
# the word is what a reader pairs against an aura.
_ELEMENT_KEYWORD = re.compile(
    r"^Applies (Pyro|Hydro|Electro|Cryo|Anemo|Geo)$")


def _element(keywords: list[dict[str, str]]) -> str:
    """The element this face applies or triggers with (`Pyro`), or `""`.

    First match wins, in the order the game listed them -- the badge's own rule
    (`ElementBadge.ElementOf` takes the card's own element, which is the first
    keyword codegen emits) for the handful of companion rows that apply a
    second aura on top of their own.
    """
    for k in keywords:
        m = _ELEMENT_KEYWORD.match(k["name"])
        if m:
            return m.group(1)
    return ""


def _card_face(entry: dict[str, Any]) -> dict[str, Any]:
    """One card as the game prints it. Field by field, never spread.

    `keywords` is included because the live wire resolves a keyword's text with
    the board's numbers in it (`+1 damage per 2 Charge you hold. You hold 8
    Charge: ...`), which is part of the face a player is reading. `id`,
    `target_type` and `index` are read on the TOOL side and never copied here.
    """
    kws = []
    for k in entry.get("keywords") or []:
        if isinstance(k, dict) and _text(k.get("name")):
            kws.append({"name": _text(k.get("name")),
                        "text": _text(k.get("description"))})
    return {
        "title": _text(entry.get("name")),
        "text": _text(entry.get("description")),
        "cost": _text(entry.get("cost")),
        # `EB-186`, and the same number for the same reason as on the staged
        # page: at a full Spark bank the game draws EVERY Attack at 0 while
        # the rule frees one, so a page that prints only what the game draws
        # is a page offering plays the board will refuse. Read from the
        # shipped face in `klee-mod`; `None` where that face gives no number,
        # and an absent number prints nothing.
        # `EB-267`: KEYED BY ID. A prototype row may print a shipped card's
        # name at a different price -- `Flame Dance` is 2 shipped and 1 on the
        # proto surface -- and a title-keyed lookup told a blind reader the
        # cost on the card in front of them was wrong when nothing was. The id
        # is read here, on the tool side, and only the number crosses.
        "printed_cost": qa_packet.printed_cost_index().get(
            qa_packet.card_key(entry.get("id"))),
        # `EB-286`. THE SPARK HALF OF THE PRICE. `cost` above is the ENERGY
        # cost and it is 0 on every Spark-priced card, so a hand line built
        # from it alone printed `Bang Bang!` at `cost 0` while the board
        # refused it -- the r3 Opus seat called a card that "prints cost 0"
        # and "sat unplayable in my hand across two entire fights" a trap,
        # and half of that was this render. Same index and same id key the
        # staged page uses (`printed_spark`, `EB-282`), so the two pages
        # cannot say different things about one price; the WIRE's own
        # `spark_price` is the fallback, because a hand entry carries it live
        # (`BuildCardState`, the GItS local edit) and a reward or shop row
        # never does. `None` where neither answers, and an absent price
        # prints nothing.
        "printed_spark": (
            qa_packet.printed_spark_index().get(
                qa_packet.card_key(entry.get("id")))
            or (_int(entry.get("spark_price"))
                if entry.get("spark_price") is not None else None)),
        "kind": _text(entry.get("type")),
        "upgraded": bool(entry.get("is_upgraded") or entry.get("upgraded")),
        "keywords": kws,
        # The card's element indicator, as a word. `""` on every face that
        # applies none, which is every base-game card and every skill of ours
        # that only blocks or draws.
        "element": _element(kws),
        "playable": entry.get("can_play") is not False,
        "unplayable_reason": _text(entry.get("unplayable_reason_text")
                                   or entry.get("unplayable_reason")),
        # `EB-271`: filled in by `_combat`, where the board this refusal is
        # about is in hand. Empty on every face built off a screen that has no
        # board -- a reward, a shop shelf -- and empty on every card that is
        # not refusing.
        "unplayable_note": "",
        # `EB-181`. THE FIELD THAT DID NOT EXIST. Run B6 held a Sharp *Water's
        # Edge* and reached none of the fields that exist, because a card face
        # on this wire carried `is_upgraded` and nothing at all about an
        # enchantment. The bridge now emits `enchantment` from the game's own
        # `CardModel.Enchantment` and emits it ONLY when there is one
        # (`McpMod.StateBuilder.cs`, `GitsEnchantmentInfo`), so an absent key
        # is the positive statement "not enchanted" -- and on a bridge too old
        # to carry it, no face on the page claims one either way.
        "enchantment": _enchantment(entry.get("enchantment")),
        # `EB-263`: whether THIS screen says the card is picked. `None` on
        # every screen and every bridge that does not answer, which is a third
        # state and not a `False`.
        "selected": (bool(entry["selected"])
                     if entry.get("selected") is not None else None),
    }


def _enchantment(blob: Any) -> dict[str, Any] | None:
    """The card's enchantment as a printed row, or `None` (`EB-181`).

    The bridge sends `{id, name, description, amount, shows_amount}`; `id` is
    an internal token and does not cross. `shows_amount` is the GAME's own
    `ShowAmount`, so a stacking enchantment prints its number and a
    one-and-done one does not -- which is not this page's call to make.

    The DESCRIPTION is carried here but not printed twice: `CardModel.HoverTips`
    already appends the enchantment's own tips, so the rule reaches the page as
    a keyword row under the card and what was missing was only the NAME beside
    the title.
    """
    if not isinstance(blob, dict):
        return None
    name = _text(blob.get("name")) or _label(blob.get("id"))
    if not name:
        return None
    row: dict[str, Any] = {"name": name,
                           "text": _text(blob.get("description"))}
    if blob.get("shows_amount") and _int(blob.get("amount")):
        row["amount"] = _int(blob.get("amount"))
    return row


# `EB-262`, AND IT IS THE WHOLE ROW. A SHOP ITEM CARRIES ITS NAME UNDER ITS
# CATEGORY'S OWN KEY. `BuildShopState` (`McpMod.StateBuilder.cs:1636`) emits
# one flat row per shelf item -- `category`, `price`, `is_stocked`,
# `can_afford` -- and then merges the thing's face in under a PREFIXED
# spelling: `card_name` / `card_description`, `relic_name` /
# `relic_description`, `potion_name` / `potion_description`. None of those is
# `name`, so every item on both of the run's shops rendered as `(unnamed)` and
# `buy` answered *"nothing here is called '(unnamed)'"* at a tester holding
# 164 gold. The event screen has the same shape for an option that hands over
# a relic (`optData["relic_name"]`, `:1553`).
#
# So the readers below are ORDERED lists rather than one key, and the first
# that answers wins -- the plain spelling first, so nothing that already
# worked changes.
_OPTION_NAME_KEYS = ("name", "title", "label", "display_name",
                     "card_name", "relic_name", "potion_name")
_OPTION_TEXT_KEYS = ("description", "body", "text",
                     "card_description", "relic_description",
                     "potion_description")
# Read only when the entry printed no name of its own: the shop's card-removal
# shelf carries no model and therefore no title, and `Card Removal` is
# `qa_packet.label`'s rendering of the wire's own word for it, not a label
# invented here.
_OPTION_KIND_KEYS = ("type", "kind", "room_type", "category")

# What a card shelf reads as once the game has cleared its card, and the key
# `_shop_options` looks a remembered face up by. See `EB-262` below.
EMPTY_SHELF = "(this shelf is empty)"


# `EB-341`. THE SHELF SAID WHAT IT WAS ONLY ONCE IT COULD NOT BE BOUGHT.
#
# `Fysh Oil` printed as `**Fysh Oil** -- 74 gold / Gain 1 Strength and 1
# Dexterity`, in the identical format used by `Vambrace`, `Stone Calendar` and
# `Royal Stamp` one line above -- a bare name, a price and an effect. The r7b
# act-3 seat bought it as a permanent Strength relic, which in that deck is the
# best 74 gold in the act. It is a potion, and the ONLY disclosure was the
# sold-out line: `**Potion** -- 74 gold (not available)`. "The screen is
# scrupulous about what it cannot tell you and careless about what it can."
#
# `category` is on every shelf row (`BuildShopState`: `card`, `relic`,
# `potion`, `card_removal`) and is the one field that separates them. It goes
# where the card TYPE already went, in front of it, because a card shelf wants
# both -- `card (skill)` -- and a relic or potion shelf has only the one. The
# category is dropped where it merely repeats the shelf's own printed name, so
# the removal shelf does not read `Card Removal -- card removal`.
def _shelf_kind(entry: dict[str, Any], name: str) -> str:
    """`card (skill)` / `relic` / `potion`, or the card type alone. `EB-341`."""
    kind = _text(entry.get("card_type")).lower()
    category = _text(entry.get("category")).replace("_", " ").lower().strip()
    if not category or _fold(name) == _fold(category):
        return kind
    return f"{category} ({kind})" if kind else category


def _named_option(entry: Any) -> dict[str, Any]:
    """One printed option -- a rest choice, a reward, a relic, a menu button.

    A wire option is sometimes a bare string and sometimes a dict under one of
    half a dozen key spellings; every one of them is a PRINTED label, so all of
    them are read and the first that answers wins. A label that arrives
    id-shaped goes through `qa_packet.label`, which strips the mod prefix and
    title-cases the rest -- a rendering, not a lookup.
    """
    if not isinstance(entry, dict):
        return {"name": _label(entry), "text": "", "enabled": True}
    name = ""
    for key in _OPTION_NAME_KEYS:
        if _text(entry.get(key)):
            name = _text(entry.get(key))
            break
    if not name:
        for key in _OPTION_KIND_KEYS:
            if entry.get(key):
                name = _label(entry.get(key))
                break
    text = ""
    for key in _OPTION_TEXT_KEYS:
        if _text(entry.get(key)):
            text = _text(entry.get(key))
            break
    enabled = True
    for key in ("is_enabled", "enabled"):
        if entry.get(key) is False:
            enabled = False
    # `is_stocked: false` is a shelf whose item has already been bought. The
    # game greys it; the page says so rather than offering a purchase the
    # bridge will refuse.
    if entry.get("is_stocked") is False:
        enabled = False
    if entry.get("is_locked"):
        enabled = False
    # `EB-262`. A SHOP CARD SHELF CARRIES THE CARD'S ENERGY COST, and it is
    # under the same prefixed spelling its name is: `card_cost`
    # (`BuildShopState`, `McpMod.StateBuilder.cs:1686`). Nothing here read it,
    # so the r3 Opus seat bought The Big One for 73 gold and "only discovered
    # it costs 3 energy -- a whole turn -- when I next saw it on a
    # card-selection screen".
    #
    # The SPARK half cannot come off the shelf: `spark_price` is emitted on a
    # HAND card only (`BuildCardState`), so a shelf is read through the same
    # id-keyed index the hand and the reward rows use. `card_id` is the only
    # key that names a card here, which is also what keeps this lookup off a
    # rest option or a map node -- those carry no `card_id` and get nothing.
    card_id = entry.get("card_id")
    energy = ""
    for key in ("card_cost", "energy_cost"):
        if _text(entry.get(key)):
            energy = _text(entry.get(key))
            break
    spark = (qa_packet.printed_spark_index().get(qa_packet.card_key(card_id))
             if card_id is not None else None)
    cost = qa_packet.cost_label({"cost": energy, "printed_spark": spark})
    # `EB-262`, the other half, AND IT IS NOT OURS TO FIX. A card shelf's
    # name, text and cost all live behind `entry.CreationResult?.Card`, and
    # `MerchantCardEntry.IsStocked` IS `CreationResult != null` -- so the
    # moment a card is bought the game clears the only field the shelf's face
    # was ever read from, and the bridge emits a row with a price and nothing
    # else. The page used to fall back to the shelf's category and print
    # `**Card** - 73 gold`, which reads as a card called "Card". It says what
    # is true instead.
    empty_shelf = (entry.get("category") == "card"
                   and entry.get("is_stocked") is False
                   and not _text(entry.get("card_name")))
    note = ""
    if empty_shelf:
        name = EMPTY_SHELF
        note = ("Bought, or never stocked. The game clears a shelf's card the "
                "moment it is sold, and the name, the text and the cost all "
                "live on that card, so nothing on the feed can say which one "
                "it was.")
    return {
        "name": name,
        "text": text,
        "enabled": enabled,
        "cost": cost if cost != "-" else "",
        # `EB-268`: the shelf's card TYPE, which the wire sends beside its
        # cost under the same prefixed spelling (`card_type`,
        # `BuildShopState`) and which a HAND line has always printed. The r1
        # Opus seat bought two cards "without knowing what they cost to
        # play"; a shelf reads the way a hand line does now.
        # `EB-341`: with the shelf's CATEGORY in front of it.
        "kind": _shelf_kind(entry, name),
        "note": note,
        # What the row says INSTEAD of a price when it cannot be taken. Empty
        # means the default, `(not available)`; `_shop_options` sets `sold`
        # on a shelf it can prove was bought.
        "unavailable": "",
        "price": _int(entry.get("price", entry.get("cost")), 0)
        if entry.get("price") is not None or entry.get("cost") is not None
        else None,
    }


# `EB-290`. A REWARD ROW IS NAMED BY ITS `description` AND BY NOTHING ELSE.
# `BuildRewardsState` (`McpMod.StateBuilder.cs:1932`) emits `index`, `type`
# and `description` for every reward and a printed NAME for exactly one kind
# of them, the potion. So a relic reward reaches this page as
# `{"type": "relic", "description": "Golden Pearl"}`, `_named_option`'s
# kind fallback printed it `**Relic**` with the relic's own name below as body
# text, and `choose "Golden Pearl"` was refused *"nothing here is called
# 'Golden Pearl'. What is on the screen: Relic"* -- at a tester reading the
# words Golden Pearl off the screen in front of them. `Reward.Description` IS
# the reward's printed face ("Golden Pearl", "12 Gold", "40 Gold (stolen
# back)"), so it is the NAME here; the type word survives only where the row
# prints nothing else, which is where it is all there is.
def _reward_option(entry: Any) -> dict[str, Any]:
    """One reward row, named by the thing it hands over (`EB-290`)."""
    option = _named_option(entry)
    if not isinstance(entry, dict):
        return option
    if any(_text(entry.get(k)) for k in _OPTION_NAME_KEYS):
        return option                        # a potion: it printed its name
    described = _text(entry.get("description"))
    if described and "\n" not in described:
        option["name"] = described
        option["text"] = ""                  # it is the heading now
    return option


def _dedupe_text(option: dict[str, Any]) -> dict[str, Any]:
    """Drop a body line that only repeats the heading above it.

    A potion reward carries its title under BOTH `potion_name` and the
    reward's own `description`, so the row printed the name and then printed
    it again as its own text.
    """
    if _fold(option.get("text")) == _fold(option.get("name")):
        option["text"] = ""
    return option


# `EB-262`, THE HALF THAT IS OURS AFTER ALL. The lost name is the GAME's --
# `MerchantCardEntry.IsStocked` IS `CreationResult != null`, so a purchase
# clears the only field the shelf's face was read from and the bridge can only
# emit what is left. But this page has SEEN that shelf: it rendered the same
# shop, from the same wire, before the purchase. So the shelf is remembered
# between renders and a bought row prints the name it had, marked `sold`,
# instead of `(this shelf is empty)`.
#
# THE SHOP'S IDENTITY IS ITS OWN FINGERPRINT and not a screen counter: the
# `(index, category, price)` of every shelf, which is exactly the part a
# purchase does NOT change (proven on the two live captures, which differ in
# `is_stocked`, `card_name` and `card_cost` and in nothing else). A different
# shop fingerprints differently and the memory is dropped, so nothing can
# carry a name from one shop to another, and a session that arrives at a shop
# already sold out has no memory to draw on and says so as it did before.
_SHELF_MEMORY: dict[str, Any] = {"shop": (), "shelves": {}}


def forget_shelves() -> None:
    """Drop the remembered shop shelves. The operator's reset, and the tests'."""
    _SHELF_MEMORY["shop"] = ()
    _SHELF_MEMORY["shelves"] = {}


def _shop_fingerprint(items: list[dict[str, Any]]) -> tuple[Any, ...]:
    return tuple((_int(i.get("index"), -1), _text(i.get("category")),
                  _int(i.get("price"), -1)) for i in items)


def _shop_options(state: dict[str, Any]) -> list[dict[str, Any]]:
    """The shelves, with a bought one wearing the face it had (`EB-262`)."""
    items = _shop_items(state)
    fingerprint = _shop_fingerprint(items)
    if _SHELF_MEMORY["shop"] != fingerprint:
        forget_shelves()
        _SHELF_MEMORY["shop"] = fingerprint
    shelves: dict[int, dict[str, str]] = _SHELF_MEMORY["shelves"]

    options = [_named_option(i) for i in items]
    for entry, option in zip(items, options):
        index = _int(entry.get("index"), -1)
        if option["name"] != EMPTY_SHELF:
            if option["name"]:
                shelves[index] = {"name": option["name"],
                                  "text": option["text"],
                                  "cost": option["cost"],
                                  "kind": option["kind"]}
            continue
        seen = shelves.get(index)
        if seen is None:
            continue
        option["name"] = seen["name"]
        option["text"] = seen["text"]
        option["cost"] = seen["cost"]
        option["kind"] = seen["kind"]
        option["unavailable"] = "sold"
        option["note"] = ("Sold. The game clears a shelf's card the moment it "
                          "is bought, so this name, this text and this cost "
                          "are what this page printed for the same shelf "
                          "before the purchase -- not what the feed says now.")
    return options


# `EB-342`. THE SMITH OMITS CARDS AND SAYS NOTHING.
#
# The r7b act-3 seat's upgrade screen listed 25 cards against a deck of 35 or
# 36. Eight of the missing were already upgraded, "which is obviously right";
# the rest -- `Powder Charge`, `Shinobu -- Sanctifying Ring (proto)` -- were
# neither upgraded nor listed, and no line explained the absence. "On a screen
# that is otherwise the most scrupulous in the bridge, a silent omission is
# conspicuous."
#
# THE DECK IS NOT ON THE WIRE OUTSIDE COMBAT. `BuildPlayerState` sends the four
# PILES, and a selection screen is not a combat, so nothing on the upgrade
# screen's own feed can name a card that is not in its grid --
# `deckwatch.py`'s opening paragraph is the same finding from the policy side.
# What this page HAS is the same thing it has for a sold shop shelf: it printed
# the board itself, one screen earlier. So the deck is remembered off the last
# COMBAT the page rendered -- hand plus draw plus discard plus exhaust, which
# inside a fight IS the deck -- and the upgrade screen subtracts its grid from
# it. The staleness is real and the page says it out loud rather than papering
# over it: a card drafted since that fight is not in the memory.
#
# ROUND 1 IS THE AUTHORITATIVE READ, for `deckwatch.record`'s reason: at round
# one every card is in hand or draw, so the union is exactly the deck and it is
# the only reading that can observe a REMOVAL. A later round can lose cards to
# an exhaust-and-clear or to a torn-down pile, so it is taken only when it is
# BIGGER than what is already held -- without that, the union read at a victory
# screen replaces the real deck with three cards.
_DECK_PILES = ("hand", "draw_pile", "discard_pile", "exhaust_pile")

# ON DISK, and that is not a convenience -- it is what makes the row's answer
# reachable at all. A blind seat drives this tool as `python -m
# understudy.blindplay observe` and `... act "<command>"`, one PROCESS PER
# CALL, so an in-memory note taken during a fight is gone before the Smith's
# screen is rendered. `deckwatch.py` keeps its own snapshot in this same
# directory for the same reason and under the same staleness caveat; this is
# a second store rather than a read of that one because that one keeps IDS for
# a draft policy and this needs the PRINTED FACE.
#
# PER LANE. Two seats play beside each other on `GITS_LANE=1` and `=2`, and one
# lane's deck answering the other's Smith screen would be worse than no answer.
# The variable is read raw and scrubbed to a filename rather than resolved
# through `instances`, which this module does not import.
_DECK_STORE_DIR = Path(__file__).resolve().parent / "logs"
_DECK_MEMORY: dict[str, Any] = {}


def _deck_store() -> Path:
    lane = re.sub(r"[^A-Za-z0-9]", "", os.environ.get("GITS_LANE", "")) or "0"
    return _DECK_STORE_DIR / f"_blindplay-deck-lane{lane}.json"


def _held_deck() -> dict[str, Any]:
    """Whatever is in the store, as a row. `{}` when there is nothing to read.

    The in-process copy is a cache over it and never an alternative to it: a
    session that renders every screen in one process and a seat that spawns a
    process per call have to see the same deck.
    """
    store = _deck_store()
    try:
        held = json.loads(store.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        held = _DECK_MEMORY
    return held if isinstance(held, dict) and held.get("cards") else {}


def forget_deck() -> None:
    """Drop the remembered deck. The operator's reset, and the tests'."""
    _DECK_MEMORY.clear()
    store = _deck_store()
    try:
        store.unlink()
    except OSError:
        pass


def remember_deck(state: dict[str, Any]) -> None:
    """Snapshot the deck from a COMBAT state's four piles (`EB-342`).

    ROUND 1 IS THE AUTHORITATIVE READ, for `deckwatch.record`'s reason: at
    round one every card is in hand or draw, so the union is exactly the deck
    and it is the only reading that can observe a REMOVAL. A later round can
    lose cards to an exhaust-and-clear or to a pile the game has already torn
    down, and the union read at a victory screen would replace a 13-card deck
    with 3. A board belonging to a DIFFERENT character is a different run and
    simply replaces what is held.

    `EB-528`. AND ROUND ONE IS THE *ONLY* READ NOW. The clause this replaces
    took a later round's union whenever it was BIGGER than what is held, and a
    later round's union can grow for a reason that is not a deck at all: a
    Companion generated mid-combat (`An Invitation`, `Guest List`) is added to
    the HAND and to no permanent list -- `GuestStarGenerator.Generate` goes
    through `CardPileCmd.AddGeneratedCardToCombat`, and the mod is right --
    so the union grew by one and the generated card was written into the deck
    this page remembers. Furina r12 met it twice: "Lynette -- Bogglecat Box
    appeared in my end-of-act deck list ... Bennett, Barbara, Gorou and
    Freminet, which arrived by the same route, did not" (lane 1), and
    "Shinobu, generated mid-fight by An Invitation, appeared in my deck list
    at the Smith" (lane 2). The tell is in the seat's own control: only the
    generated cards whose fight happened to make the union bigger got in.

    NOTHING IS LOST BY DROPPING IT. A card the run really did gain -- a
    reward, an event, a Status -- is in hand or draw at the NEXT fight's round
    one, which is the read this function already called the authoritative one.
    What the page gives up is freshness INSIDE one combat, and it already
    labels the deck it prints with the floor that read was taken on.
    """
    player = _blob(state, "player")
    if not any(isinstance(player.get(p), list) for p in _DECK_PILES):
        return
    cards: list[dict[str, Any]] = []
    for pile in _DECK_PILES:
        for entry in player.get(pile) or []:
            if isinstance(entry, dict) and _text(entry.get("name")):
                cards.append({"title": _text(entry.get("name")),
                              "key": qa_packet.card_key(entry.get("id")),
                              "upgraded": bool(entry.get("is_upgraded")
                                               or entry.get("upgraded"))})
    if not cards:
        return
    held = _held_deck()
    same_run = _fold(held.get("character")) == _fold(player.get("character"))
    if same_run and _int(_blob(state, "battle").get("round")) != 1:
        return
    row = {"cards": cards,
           "character": _text(player.get("character")),
           "act": _int(_blob(state, "run").get("act")),
           "floor": _int(_blob(state, "run").get("floor"))}
    _DECK_MEMORY.clear()
    _DECK_MEMORY.update(row)
    try:
        _DECK_STORE_DIR.mkdir(parents=True, exist_ok=True)
        _deck_store().write_text(json.dumps(row), encoding="utf-8")
    except OSError:
        pass                       # a read-only tree still gets the in-process copy


def remembered_deck(state: dict[str, Any]) -> dict[str, Any]:
    """The deck this page last read, IF it is about the run on `state`.

    Two guards, and both of them refuse rather than guess. The CHARACTER has
    to match the board in hand -- a deck remembered from another run, or from
    the other lane's game, is not this player's. And the FLOOR may not have
    gone backwards: a run only ever climbs, so a screen below the floor the
    deck was read on belongs to a run that started since.

    Returns `{}` where nothing applies, which is what a fresh session, a
    changed character and a first fight all look like -- and the caller prints
    nothing at all rather than an empty list of omissions.
    """
    held = _held_deck()
    if not held:
        return {}
    if _fold(held.get("character")) != _fold(_blob(state, "player")
                                             .get("character")):
        return {}
    floor, here = _int(held.get("floor")), _int(_blob(state, "run").get("floor"))
    if floor and here and here < floor:
        return {}
    return {"cards": [dict(c) for c in held["cards"]], "floor": floor}


def _number_faces(faces: list[dict[str, Any]], field: str
                  ) -> list[dict[str, Any]]:
    """`_number_names` over one field of a list of already-built faces."""
    for face, name in zip(faces, _number_names([f[field] for f in faces])):
        face[field] = name
    return faces


# `EB-271`, THE OTHER HALF, AND THIS ONE MISTARGETS IN SILENCE.
#
# `_number_names` numbers a repeat by its PLACE IN THE LIST IT IS GIVEN, and
# the enemy list is not the same list from one screen to the next: the feed
# drops a body once its death finishes (the kokomi r1 pair reported "enemies
# are renumbered when one dies"). With TWO enemies of a name that is only the
# stale-number problem the other half of this row closes -- the survivor
# prints bare and the number the tester last saw still finds it, because one
# copy remains. With THREE it is worse than a refusal: kill `Slug (1)` and the
# two survivors reprint as `Slug (1)` and `Slug (2)`, so `attack "Slug (2)"`
# now names the creature the page called `Slug (3)` one screen earlier and the
# command SUCCEEDS against the wrong body. Nothing on the page says so.
#
# So the number is assigned once and KEPT FOR THE FIGHT. The identity it is
# kept against is `combat_id`, the game's own per-creature id
# (`BuildEnemyState`, `McpMod.StateBuilder.cs:1444`) -- NOT `entity_id`, which
# the same builder derives by counting names as it walks the live list
# (`jaw_worm_0`, `jaw_worm_1`) and which therefore renumbers with everything
# else.
#
# THE FIGHT'S IDENTITY IS ITS ROSTER, on the `_SHELF_MEMORY` pattern above and
# for the same reason: this module is handed one snapshot at a time and is
# told nothing about boundaries. A `combat_id` counts from 1 inside each
# combat, so the ids alone would carry numbering from one fight into the next.
# The roster remembers `(fold, max_hp)` beside each id, and the memory is
# dropped whenever the board in hand shares NO remembered creature, or claims
# a remembered id for a DIFFERENT creature. A board that is a subset of the
# roster is the same fight with bodies gone; a board that adds an id beside
# remembered ones is a summon, and the newcomer takes the next free number.
#
# `EB-427` ADDED `names`, AND IT IS THE HALF EVERY RECEIPT NEEDED. The
# numbering above already held across a death -- the kokomi r11 seat's three
# Inklets keep 1, 2 and 3 through the one the morning killed -- but every line
# that names a body the board no longer carries fell back to the mod's bare
# title, so one morning printed `Inklet`, `Inklet (1)` and `Inklet (2)` for
# three bodies and the seat read that as the numbers having shifted under it.
# The fight remembers each id's PRINTED name, so a body that has left the board
# is still called what it was called while it stood.
#
# `EB-428` ADDED `elements`, and it rides here because it decays on the same
# boundary. The reaction glossary prints a row only where the screen can supply
# both of its elements, and a screen is one turn: a Cryo card played on turn 1
# is not in the hand on turn 2, and a glossary that dropped Melt for it would
# be `EB-340`'s own defect back again -- "whether I was allowed to see it
# depended on my draw". So an element this FIGHT has been shown to reach stays
# reachable for the fight. It is the nearest honest reading of the row's "the
# deck faces": the deck memory (`remember_deck`) keeps titles alone and cannot
# answer what a card applies.
#
# `EB-496`. AND IT WAS PROCESS STATE, WHICH IS WHY THE SEATS STILL SAW IT
# RENUMBER. Everything above is true of ONE PROCESS, and a seat does not have
# one: the brief hands it `GITS_LANE=1 python -m understudy.blindplay observe`
# and `... act "<command>"`, so every screen of a round is rendered by a fresh
# interpreter with an empty dict. Each render therefore numbered the board it
# was handed from 1 -- kill `Gardener (1)` and the next `observe` calls the
# survivors `(1)`, `(2)`, `(3)` -- which is precisely the defect `EB-271` and
# `EB-427` closed for the in-process `Session` driver and never closed for the
# seats. The Klee r17 lane-1 seat aimed a 14-damage Melt at the body one row
# down and only found out by reading max-HP off the next screen.
#
# SO THE MEMORY IS ON DISK, `_DECK_MEMORY`'s shape one memory over and in the
# same directory, per lane, for the same reason: a session that renders every
# screen in one process and a seat that spawns a process per call have to see
# the same numbers. Sets are stored as sorted lists because JSON has no set;
# the in-process dict is the working copy and the file is the truth.
_FIGHT_STORE_DIR = Path(__file__).resolve().parent / "logs"
_FIGHT_MEMORY: dict[str, Any] = {"roster": {}, "ordinals": {},
                                 "numbered": set(), "names": {},
                                 "handles": {}, "elements": set()}
#: Whether this process has read the lane's store yet. The load is lazy and
#: happens once: a fresh `observe` pays one file read, and a long-lived
#: `Session` pays it on its first fight and never again.
_FIGHT_LOADED = [False]


def _fight_store() -> Path:
    lane = re.sub(r"[^A-Za-z0-9]", "", os.environ.get("GITS_LANE", "")) or "0"
    return _FIGHT_STORE_DIR / f"_blindplay-fight-lane{lane}.json"


def _load_fight() -> None:
    """Fill the in-process memory from the lane's store, once (`EB-496`)."""
    if _FIGHT_LOADED[0]:
        return
    _FIGHT_LOADED[0] = True
    try:
        held = json.loads(_fight_store().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(held, dict):
        return
    # A tuple survives a JSON round trip as a list, and `roster` compares its
    # values against `(fold, max_hp)` tuples -- so the shape is restored here
    # rather than left for `_enemy_names` to trip over.
    roster = held.get("roster")
    if isinstance(roster, dict):
        _FIGHT_MEMORY["roster"] = {
            k: (str(v[0]), int(v[1])) for k, v in roster.items()
            if isinstance(v, (list, tuple)) and len(v) == 2}
    for key in ("ordinals", "names", "handles"):
        value = held.get(key)
        if isinstance(value, dict):
            _FIGHT_MEMORY[key] = dict(value)
    for key in ("numbered", "elements"):
        value = held.get(key)
        if isinstance(value, list):
            _FIGHT_MEMORY[key] = {str(v) for v in value}


def _save_fight() -> None:
    """Write the memory back to the lane's store. A read-only tree keeps the
    in-process copy and loses nothing else (`remember_deck`'s own bargain)."""
    row = {"roster": {k: list(v) for k, v in _FIGHT_MEMORY["roster"].items()},
           "ordinals": dict(_FIGHT_MEMORY["ordinals"]),
           "names": dict(_FIGHT_MEMORY["names"]),
           "handles": dict(_FIGHT_MEMORY["handles"]),
           "numbered": sorted(_FIGHT_MEMORY["numbered"]),
           "elements": sorted(_FIGHT_MEMORY["elements"])}
    try:
        _FIGHT_STORE_DIR.mkdir(parents=True, exist_ok=True)
        _fight_store().write_text(json.dumps(row), encoding="utf-8")
    except OSError:
        pass


def forget_fight() -> None:
    """Drop the remembered enemy numbers. The operator's reset, and the tests'."""
    _FIGHT_MEMORY["roster"] = {}
    _FIGHT_MEMORY["ordinals"] = {}
    _FIGHT_MEMORY["numbered"] = set()
    _FIGHT_MEMORY["names"] = {}
    _FIGHT_MEMORY["handles"] = {}
    _FIGHT_MEMORY["elements"] = set()
    _FIGHT_LOADED[0] = True
    try:
        _fight_store().unlink()
    except OSError:
        pass


def remember_elements(found: set[str]) -> set[str]:
    """Every element this fight has been shown to reach (`EB-428`).

    UNION AND NEVER SUBTRACT, for the reason in `_FIGHT_MEMORY`'s header: the
    question a reaction row answers is whether the DECK can build the pair, and
    a card that is in the discard this turn is in the hand two turns from now.
    Dropped with the rest of the fight's memory, so a Cryo drafted for one run
    is not still colouring the glossary of the next.

    `EB-496` PUT IT ON DISK, and that is what closes `EB-428`'s reward half:
    the reward screen is a different PROCESS from the fight it followed, so the
    elements the deck had just shown were gone by the time the offer was read
    and every reaction card was priced against its own element alone. The Klee
    r17 lane-1 seat passed Dahlia (Hydro) twice holding Pyro and Electro and
    was told, on both screens, that no reaction was reachable.
    """
    _load_fight()
    before = set(_FIGHT_MEMORY["elements"])
    _FIGHT_MEMORY["elements"] |= set(found)
    if _FIGHT_MEMORY["elements"] != before:
        _save_fight()
    return set(_FIGHT_MEMORY["elements"])


def remembered_enemy_name(combat_id: Any, title: str) -> str:
    """What this fight has been calling the body with that combat id (`EB-427`).

    THE CALLER'S OWN TITLE STAYS THE FALLBACK, for the two cases it was always
    right for: an id this fight never saw, and a wire that carries no id at
    all. What changes is the case in between -- a body that WAS on the board
    and is not any more, which is exactly the body a carry-out or a performance
    is most likely to be about, because a Plan that killed something is a Plan
    a reader wants to read.

    THE EXPRESSION IS `_enemy_names`' OWN, deliberately: a name is numbered
    here on the same two conditions it is numbered there, so a body cannot be
    called one thing in the enemy list and another in the receipt above it.
    """
    _load_fight()
    key = f"c{combat_id}"
    name = _FIGHT_MEMORY["names"].get(key)
    if not name:
        return title
    if _fold(name) in _FIGHT_MEMORY["numbered"] and key in _FIGHT_MEMORY["ordinals"]:
        return f"{name} ({_FIGHT_MEMORY['ordinals'][key]})"
    return name


# `EB-496`, THE SECOND HANDLE ON THE OTHER SIDE OF THE BOARD.
#
# A number is a name's copy count, and it is only a handle where a name
# repeats: a board of one Gardener and one Sewer Clam prints neither. What the
# seat asked for is a handle that is the same word on every screen of the
# fight whatever dies, for every body, so a card can be aimed without reading
# the list again -- and the letters are that. Assigned in the order the fight
# first saw each body, kept beside the ordinal in the same memory, and dropped
# with it.
#
# LETTERS AND NOT SLOTS. A slot is a place on the board and the board closes
# up; a letter is minted once and never reused, which is the whole property
# the number lacked. `E27` and up is the honest overflow rather than `AA`: no
# encounter in the game fields twenty-seven bodies, and a reader meeting one
# is better served by something that cannot be mistaken for a name.
def _handle_for(nth: int) -> str:
    return chr(ord("A") + nth) if nth < 26 else f"E{nth + 1}"


def _enemy_key(entry: dict[str, Any]) -> str:
    """The creature's identity for the fight.

    `combat_id` where the wire carries it, and `entity_id` only as the
    fallback for a feed that does not -- a fallback that is worth having
    because it is still right while nothing has died, and wrong in exactly the
    way this whole function exists to fix once something has.
    """
    cid = entry.get("combat_id")
    return f"c{cid}" if cid is not None else f"e{_entity_id(entry)}"


def _enemy_names(enemies: list[dict[str, Any]]) -> list[str]:
    """The printed enemy names, numbered ONCE and kept for the fight.

    Same output as `_number_names` on the opening board of any fight, which is
    the point: nothing about a first screen changes. What changes is every
    screen after a death.

    A name that has ever repeated in this fight stays numbered even when one
    body is left, because the number is the handle the tester has been using
    and taking it away is the stale-number refusal this row's first half had
    to paper over. A name that has never repeated is left exactly as the game
    printed it.
    """
    if not enemies:
        return []
    _load_fight()
    names = [_text(e.get("name")) for e in enemies]
    # An id the feed repeats on ONE board cannot identify a creature, and
    # collapsing two bodies onto one key would print one number twice -- the
    # silent-mistarget failure this function exists to remove, arriving by the
    # other door. `CombatId` is unique per creature so the game cannot produce
    # it; the slot breaks the tie anyway, and those enemies simply keep the
    # old positional behaviour rather than a wrong one.
    keys, seen_key = [], {}
    for entry in enemies:
        key = _enemy_key(entry)
        nth = seen_key.get(key, 0)
        seen_key[key] = nth + 1
        keys.append(key if nth == 0 else f"{key}#{nth}")
    ident = [(_fold(n), _int(e.get("max_hp", e.get("hp"))))
             for n, e in zip(names, enemies)]

    roster: dict[str, tuple[str, int]] = _FIGHT_MEMORY["roster"]
    shared = any(roster.get(k) == i for k, i in zip(keys, ident))
    clash = any(k in roster and roster[k] != i for k, i in zip(keys, ident))
    if clash or not shared:
        forget_fight()
    roster = _FIGHT_MEMORY["roster"]
    ordinals: dict[str, int] = _FIGHT_MEMORY["ordinals"]
    numbered: set[str] = _FIGHT_MEMORY["numbered"]

    handles: dict[str, str] = _FIGHT_MEMORY["handles"]
    fresh = False
    for key, name, (fold, hp) in zip(keys, names, ident):
        if key in roster or not fold:
            continue
        fresh = True
        roster[key] = (fold, hp)
        # `EB-427`: the printed name beside the ordinal, so a line about a body
        # that has since left the board can be given the same handle.
        _FIGHT_MEMORY["names"][key] = name
        # `EB-496`: and the letter, minted in first-seen order and never
        # reused, so a summon takes the next free one rather than a dead
        # body's.
        handles[key] = _handle_for(len(handles))
        seen = sum(1 for f, _ in roster.values() if f == fold)
        ordinals[key] = seen
        if seen > 1:
            numbered.add(fold)
    if fresh:
        _save_fight()
    return [f"{n} ({ordinals[k]})" if _fold(n) in numbered and k in ordinals
            else n for k, n in zip(keys, names)]


def _enemy_handles(enemies: list[dict[str, Any]]) -> list[str]:
    """The per-fight letter of each body on this board, in its order (`EB-496`).

    Read out of the memory `_enemy_names` fills, and only out of it: a body
    this fight has never numbered has no letter, and the page prints none
    rather than counting the list it happens to be holding -- which is the
    counting this row exists to stop.
    """
    handles: dict[str, str] = _FIGHT_MEMORY["handles"]
    seen_key: dict[str, int] = {}
    out: list[str] = []
    for entry in enemies:
        key = _enemy_key(entry)
        nth = seen_key.get(key, 0)
        seen_key[key] = nth + 1
        out.append(handles.get(key if nth == 0 else f"{key}#{nth}", ""))
    return out


# `EB-271`, THE SECOND HANDLE. THE ONE REFUSAL ON THE SCREEN THAT NAMED
# NOTHING.
#
# The r2 Opus seat put it exactly: *"every other refusal on this screen names
# its reason (`you have no Spark; and this costs 1`, `no enemy is holding a
# Bomb`, `you do not have enough energy`). This one does not."* The one that
# does not is `BlockedByHook`, which the wire spells as that bare enum name
# and `qa_packet.UNPLAYABLE_REASONS` renders as *"something else on the board
# is stopping you right now"* -- true, and a sentence a tester cannot act on.
#
# `CardModel.CanPlay` reports the flag and has no slot for WHICH model
# refused, so the sentence cannot come off the wire and this page must not
# invent one. What it can do is stop being vague with facts it is already
# printing:
#
#   * an ARM GATE, and this is the one the row names. A Spark-priced card
#     refuses through `SparkAttackCostPower.ShouldPlay`, a hook, so a shortfall
#     that the mod's own `KleeUnplayableReason` did not reach the page for
#     still arrives as the bare enum -- while the price and the bank are BOTH
#     on this screen already (`printed_spark` on the face, `Spark` in the
#     powers). Two numbers the page prints, subtracted.
#   * otherwise the honest half: a hook is something ALREADY ON THE BOARD, and
#     the statuses on the player are the board's own list. Naming them is not
#     a guess at which one refused -- the note says the feed does not name it
#     -- it is telling a reader where to look, which is what the seat was
#     asking for.
#
# `BlockedByCardLogic` is deliberately NOT here: the card's own rule is its
# printed text, two lines above on the same page.
_BARE_HOOK = "blockedbyhook"
_SPARK_POWER = "spark"


def _hook_note(card: dict[str, Any],
               powers: list[dict[str, Any]]) -> str:
    """The extra clause for a refusal the feed would not explain. `""` mostly."""
    if card["playable"] or _fold(card["unplayable_reason"]) != _BARE_HOOK:
        return ""
    price = card.get("printed_spark")
    bank = next((_int(p.get("stacks")) for p in powers
                 if _fold(p.get("name")) == _SPARK_POWER), None)
    if isinstance(price, int) and price > 0 and bank is not None \
            and bank < price:
        return (f"This card is priced at {price} Spark and your bank is "
                f"{bank}.")
    on_you = ", ".join(
        f"{p['name']} {p['stacks']}" if p.get("stacks") else p["name"]
        for p in powers if p.get("name"))
    if not on_you:
        return ""
    return ("The feed does not say which thing is stopping it. A hook is "
            f"something already on the board, and what is on YOU right now "
            f"is: {on_you}.")


def _meter_max(player: dict[str, Any]) -> dict[str, int]:
    """`{printed meter name: its maximum}` for every meter that declares one.

    `EB-181`. `player.resources` is `{id: amount}` and carries no ceiling, so
    every meter row on this page has had to say so. The bridge's
    `resource_info` is the fuller row per id -- `amount`, `max`, `resets_to`
    -- with `max` filled only where the RESOURCE ITSELF declares one, since a
    ceiling is the mod's fact and never BaseLib's
    (`vendor/STS2_MCP/gits/GitsResources.cs`).

    A meter that answers `null` is left OUT of this map rather than entered as
    0: a zero would print `Charge: 8/0`, and "this meter declares no maximum"
    is the thing the row still has to be able to say.
    """
    info = player.get("resource_info")
    if not isinstance(info, dict):
        return {}
    out: dict[str, int] = {}
    for key, row in info.items():
        if not isinstance(row, dict):
            continue
        top = row.get("max")
        if isinstance(top, bool) or not isinstance(top, int) or top <= 0:
            continue
        out[_label(key)] = top
    return out


def _powers(blob: dict[str, Any]) -> list[dict[str, Any]]:
    """`qa_packet._powers` plus the `type` the wire has always carried.

    `EB-179`. A status row on the wire is exactly `id`, `name`, `amount`,
    `type`, `description`, `keywords` -- no duration and no expiry anywhere.
    `type` is the one of those the page was dropping, and it is the game's
    own word for whether a thing on the board is helping or hurting, so it
    goes back on the line. The filter below MIRRORS `qa_packet._powers`'s
    skip rule (a row with no printed name is not a power the page shows), so
    the two lists stay index-aligned; they are one function's worth of logic
    living either side of a module boundary, and a change to one is a change
    to both.
    """
    out = qa_packet._powers(blob)
    rows = [row for row in (blob.get("status") or [])
            if isinstance(row, dict)
            and (_text(row.get("title")) or _label(row.get("name")))]
    for power, row in zip(out, rows):
        kind = _text(row.get("type"))
        power["kind"] = "aura" if _is_aura(power["name"]) else kind
        # `EB-340`: the tips the wire hangs on the status row, carried through
        # so the glossary can define a word an enemy's buff line announced.
        # `Galvanic 6 -- Powers are afflicted with Galvanized` reached a blind
        # seat with `Galvanized` defined nowhere, on the turn whose whole
        # decision was whether to play a Power. Same shape as a card face's
        # `keywords`, read the same way, and absent where the feed sends none.
        power["keywords"] = [
            {"name": _text(k.get("name")), "text": _text(k.get("description"))}
            for k in (row.get("keywords") or [])
            if isinstance(k, dict) and _text(k.get("name"))]
    return out


def _is_aura(name: str) -> bool:
    """Is this printed power an elemental AURA? (`EB-294`)

    THE WIRE SAYS `Buff` AND IT IS NOT LYING, WHICH IS THE WHOLE TRAP.
    `AuraPower.Type` is `PowerType.Buff` on purpose and the reason is written
    at the property: elemental application has to COEXIST with Artifact
    ([USER] 2026-08-23), and `ArtifactPower` negates on
    `GetTypeForAmount(amount) == PowerType.Debuff`, so a positive counter that
    must not be eaten has to declare itself a buff. That is a rule about
    Artifact, not a statement to a reader -- and the page printed it as one:
    `Hydro Aura 2 (buff)` sat in the same block as `Vulnerable 1 (debuff)`,
    and the r2 Opus seat read the aura it had just applied as something
    helping the enemy.

    Read off the PRINTED TITLE, which is the only handle this side of the line
    has: `AuraPower.Localization` writes `("title", $"{Element} Aura")` for
    every element, so every aura on the board prints a name ending in the word
    Aura and nothing else does. An id would be the sturdier key, and an id may
    not reach this module at all.
    """
    words = _fold(name).split()
    return bool(words) and words[-1] == "aura"


def _intent(blob: Any) -> dict[str, str]:
    """`qa_packet._intent` plus the wire's own `type` (`EB-299`).

    A telegraph on the wire is `type` (`Attack`, `Debuff`, ...), `label` (the
    number the game draws ON the icon), `title` (the hover tip's heading --
    `Aggressive`, `Strategic`) and `description` (its sentence). The page
    printed title, label and description comma-joined and dropped `type`
    entirely, which is `EB-179`'s power defect one field over.
    """
    out = qa_packet._intent(blob)
    row = blob[0] if isinstance(blob, list) and blob else blob
    out["type"] = _text(row.get("type")) if isinstance(row, dict) else ""
    return out


# `EB-342`. A TELEGRAPH IS A LIST AND THE PAGE PRINTED ITS FIRST ROW.
#
# `BuildEnemyState` walks `moveState.Intents` and sends `intents` as a LIST --
# one entry per component of the move -- and `qa_packet._intent` takes
# `blob[0]` and drops the rest, which is right for the staged packet's one-line
# telegraph and wrong for a page a tester plans a turn on. The r7b act-3 seat
# read `Aggressive (Attack) -- the number on its icon is 8 -- This enemy
# intends to Attack for 8 damage`, and the round that followed opened with FOUR
# `Burn`s in hand, 8 more HP a turn, at 18/56, in the fight that ended the run.
# The bridge already has the vocabulary for the second half -- seat 3 was shown
# `Strategic (StatusCard)` on another enemy -- so the components existed and
# the page was printing one of them.
#
# Every component, in the order the move declares them. A single-component move
# renders exactly as it always did: one row, one line, unchanged.
def _intents(blob: Any) -> list[dict[str, str]]:
    """Every component of one telegraph, in the move's own order (`EB-342`)."""
    rows = blob if isinstance(blob, list) else [blob]
    out = [_intent(row) for row in rows if isinstance(row, dict)]
    return out or [_intent(None)]


def _shop_items(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in _listing(state, "items", "shop.items")
            if isinstance(i, dict)]

def _card_title(entry: dict[str, Any]) -> str:
    return _text(entry.get("name"))

