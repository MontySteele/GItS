"""One line of player language, resolved against the screen it was typed at.

Cut out of `blindplay.py` by `EB-180`: `parse_command`, the printed-name
match, the eleven verbs and `act`. Re-exported from `blindplay.py`, so
`blindplay.act(state, command)` and `blindplay.parse_command(text)`
still resolve.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from understudy import qa_packet
from understudy.blindplay_board import (_bundle_cards, _combat,
                                        _event_options, _map_nodes,
                                        _map_options, _proceed_option,
                                        _relic_options, _rest_options,
                                        _reward_items, _screen_cards)
from understudy.blindplay_faces import (_card_face, _card_title, _enemy_names,
                                        _named_option, _reward_option,
                                        _shop_items, _shop_options)
from understudy.blindplay_notes import PREVIEW_LOCKED
from understudy.blindplay_observe import observation
from understudy.blindplay_read import (_blob, _enemies, _entity_id, _fold,
                                       _hand, _int, _number_names, _player,
                                       _potions, _screen, _text)
from understudy.blindplay_shape import (BlindPlayError, COMBAT_SCREENS,
                                        SELECT_SCREENS)



_QUOTED = re.compile(r'"([^"]*)"|“([^”]*)”')

VERBS = ("play", "end turn", "choose", "skip", "go", "buy", "rest",
         "upgrade", "remove", "use potion", "confirm", "proceed")


@dataclass
class Command:
    verb: str
    names: list[str] = field(default_factory=list)
    raw: str = ""

    @property
    def name(self) -> str:
        return self.names[0] if self.names else ""

    @property
    def target(self) -> str:
        return self.names[1] if len(self.names) > 1 else ""


def parse_command(text: str) -> Command:
    """One line of player language, or `BlindPlayError`.

    Quotes are the grammar's only structure and they are required around every
    name: a screen prints titles with `on`, `and` and `choose` inside them, and
    a parser that split on words would resolve half a card. Curly quotes are
    read too -- a model that types them is not making a different request.
    """
    raw = " ".join(str(text or "").split())
    if not raw:
        raise BlindPlayError("empty command")
    names = [(a or b) for a, b in _QUOTED.findall(raw)]
    head = _QUOTED.sub("", raw).strip().casefold()
    head = " ".join(head.split())
    head = head.rstrip(".")
    if head.startswith("use potion") or head.startswith("use the potion"):
        verb = "use potion"
    elif head.startswith("end turn"):
        verb = "end turn"
    else:
        verb = head.split(" ")[0] if head else ""
    if verb not in VERBS:
        raise BlindPlayError(
            f"{raw!r} is not a command. The ones that exist are: "
            + ", ".join(VERBS))
    if verb in ("play", "go", "buy") and not names:
        raise BlindPlayError(f"`{verb}` needs a name in quotes")
    if verb == "choose" and not names:
        raise BlindPlayError("`choose` needs a name in quotes")
    return Command(verb=verb, names=names, raw=raw)


# ------------------------------------------------------------- resolution --

@dataclass
class Resolution:
    """What a command means against the state it was typed at.

    `post` is the wire body and is the ONLY place an id lives; `printed` is the
    same decision in the names the screen used, and is what may be echoed back
    to the tester.
    """
    ok: bool
    verb: str = ""
    post: dict[str, Any] | None = None
    printed: dict[str, Any] = field(default_factory=dict)
    refusal: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "verb": self.verb, "post": self.post,
                "printed": self.printed, "refusal": self.refusal}


def _refuse(why: str) -> Resolution:
    return Resolution(ok=False, refusal=why)


# `EB-173`: the qualifier the refusal advertises, and the resolver now honours.
# Accepted on either side of the title so a tester who echoes the screen back
# ("Coral Guard+ (upgraded)") is understood, and negatable so the BASE copy is
# reachable too -- a disambiguator that can only ever pick one of the two
# leaves the other unplayable, which is the defect this exists to close.
_QUALIFIER = re.compile(r"\s*\((not\s+)?upgraded\)\s*", re.I)


def _split_qualifier(name: str) -> tuple[str, bool | None]:
    """`(title without the qualifier, wanted upgrade state or None)`."""
    m = _QUALIFIER.search(name)
    if not m:
        return name, None
    return (name[:m.start()] + name[m.end():]).strip(), not m.group(1)


def _is_upgraded(entry: dict[str, Any]) -> bool:
    return bool(entry.get("is_upgraded") or entry.get("upgraded"))


# `EB-271`: a trailing `(2)` on a name the tester typed. `_number_names` only
# ever appends this shape, so stripping it back off is exact rather than a
# guess at what a bracketed number might have meant.
_STALE_NUMBER = re.compile(r"\s*\((\d+)\)\s*$")


def _match(entries: list[dict[str, Any]], name: str, *,
           key: Callable[[dict[str, Any]], str],
           face: Callable[[dict[str, Any]], str] | None = None,
           number: bool = False) -> tuple[int, str]:
    """`(index, refusal)` for `name` among `entries`, by PRINTED name only.

    Exact fold first, unique substring second. Two entries whose printed FACE
    is identical are interchangeable and the first is taken -- refusing there
    would make a second copy of a card unplayable, which is not an ambiguity a
    player experiences. Two entries that print the same title with different
    faces (a base and an upgraded copy) ARE ambiguous, and the refusal says how
    to disambiguate rather than guessing.

    `number` (`EB-177`) matches against `_number_names`'s output instead of the
    bare printed names, which is what the RENDER prints on the same screen: a
    repeated title carries `(1)`, `(2)` in printed order and a unique one is
    untouched, so the bare title stays valid wherever it is unique and the
    numbered form is the handle wherever it is not. Callers turn it on exactly
    where the observation numbers the same list; a caller that does not number
    its page must not number its grammar.

    `EB-173`, FOUND LIVE AND FIXED HERE. `_fold` strips punctuation, which is
    right for apostrophes and dashes and WRONG for the `+` the game itself
    appends to an upgraded title: `Coral Guard` and `Coral Guard+` folded to
    the same key, so with both in hand every naming of either was ambiguous --
    and the refusal's advice, `"(upgraded)"`, was documented in the grammar and
    implemented nowhere, so the escape hatch answered "nothing here is called
    that". NEITHER copy could be played. A blind session hit it on its fifth
    combat round and died against the refusal limit. Two halves to the fix:
    the qualifier is now PARSED and filters the hits (with `(not upgraded)`
    for the other side), and `+` survives the fold as a distinguishing mark,
    so the two titles are simply different names and the common case never
    reaches the ambiguity arm at all.
    """
    printed = [key(e) for e in entries]
    if number:
        printed = _number_names(printed)
    name, want_upgraded = _split_qualifier(name)
    want = _fold(name)
    if not want:
        return -1, "no name given"
    exact = [i for i, p in enumerate(printed) if _fold(p) == want]
    loose = [i for i, p in enumerate(printed) if want in _fold(p)]
    if not (exact or loose):
        # `EB-271`, FOUND LIVE. A NUMBER IS A PLACE IN A LIST, AND THE LIST
        # MOVES. `_number_names` numbers a title only while it repeats, so the
        # moment one of two `Duck and Cover` copies is played the survivor is
        # printed bare and `play "Duck and Cover (1)"` -- the name the page was
        # printing one screen earlier, and the name the tester had just typed
        # once -- answered "nothing here is called that". `HAND_REPEAT_NOTE`
        # tells a reader the number is re-counted per screen; that is true and
        # it is not a reason to refuse a name that can only mean one thing.
        #
        # So a stale number is ACCEPTED WHEN ONE COPY REMAINS, and only then:
        # the suffix comes off and the bare name has to resolve to EXACTLY ONE
        # entry. With two copies still on the screen `(3)` is genuinely
        # ambiguous and falls through to the refusal below, which advertises
        # the numbered names that would have worked.
        bare = _STALE_NUMBER.sub("", name).strip()
        if bare and bare != name:
            want_bare = _fold(bare)
            again = ([i for i, p in enumerate(printed)
                      if _fold(p) == want_bare]
                     or [i for i, p in enumerate(printed)
                         if want_bare and want_bare in _fold(p)])
            if len(again) == 1:
                name, want, exact = bare, want_bare, again
    hits = exact or loose
    if want_upgraded is not None:
        def _wanted(idx: list[int]) -> list[int]:
            return [i for i in idx if _is_upgraded(entries[i]) == want_upgraded]
        # Widen to the substring pass when the qualifier empties the exact
        # one: `Coral Guard (upgraded)` names the `+` copy exactly, and its
        # title is not the string the tester typed.
        narrowed = _wanted(exact) or _wanted(loose)
        if not narrowed and hits:
            state = "upgraded" if want_upgraded else "un-upgraded"
            return -1, (f"nothing here called {name!r} is {state}. "
                        f"What is on the screen: "
                        + ", ".join(sorted({printed[i] for i in hits})))
        hits = narrowed
    if not hits:
        offered = ", ".join(sorted({p for p in printed if p}))
        return -1, (f"nothing here is called {name!r}. "
                    f"What is on the screen: {offered or '(nothing)'}")
    if len(hits) > 1:
        # Identical FACES first, and before the numbering: two copies of one
        # card are interchangeable, refusing there would make the second copy
        # unplayable, and that is not an ambiguity a player experiences. The
        # numbered names are still on the page for anyone who wants to be
        # explicit -- they are a handle, not an obligation.
        if face is not None and len({face(entries[i]) for i in hits}) == 1:
            return hits[0], ""
        # `EB-177`: otherwise the refusal ADVERTISES the names that would have
        # worked. With `number` on, two copies of one title print as `... (1)`
        # and `... (2)`, so a bare ambiguous title lands here and the way out
        # is already on the screen -- name it back rather than describe it.
        choices = sorted({printed[i] for i in hits})
        # The upgrade qualifier is advertised only where it would actually
        # narrow -- EB-173's rule that advice a tester cannot act on costs a
        # turn of the refusal budget to discover. Where BOTH handles work
        # (`EB-177`: two copies of one printed title, one of them upgraded)
        # both are offered, because the numbered name is the one the page in
        # front of them already prints.
        qualifier = ""
        if len({_is_upgraded(entries[i]) for i in hits}) > 1:
            qualifier = ('; or add "(upgraded)" / "(not upgraded)" to pick '
                         "one")
        if len(choices) > 1:
            return -1, (f"{name!r} matches more than one thing on this "
                        f"screen; name one exactly: {', '.join(choices)}"
                        + qualifier)
        if face is not None:
            # One printed name over different faces, and this caller does not
            # number: the upgrade qualifier is the only handle there is.
            return -1, (f"{name!r} matches more than one different thing on "
                        f"this screen; name it exactly, or add "
                        f"\"(upgraded)\" / \"(not upgraded)\" to pick one")
    return hits[0], ""


def _match_bundle(entries: list[dict[str, Any]], name: str
                  ) -> tuple[int, str]:
    """`(index, refusal)` for the bundle holding a card printed `name`.

    `EB-173`. Exact title first, unique substring second -- `_match`'s order,
    on a set of names per entry instead of one. A title that appears in TWO
    bundles is refused rather than guessed at: which bundle the tester meant is
    exactly the question, and the other cards are how they would say it.
    """
    name, _ = _split_qualifier(name)
    want = _fold(name)
    if not want:
        return -1, "no name given"
    titles = [[_card_title(c) for c in _bundle_cards(b)] for b in entries]
    hits = [i for i, ts in enumerate(titles)
            if any(_fold(t) == want for t in ts)]
    if not hits:
        hits = [i for i, ts in enumerate(titles)
                if any(want in _fold(t) for t in ts)]
    if not hits:
        offered = "; ".join(f"[{', '.join(t for t in ts if t)}]"
                            for ts in titles)
        return -1, (f"no bundle here holds anything called {name!r}. "
                    f"What is on the screen: {offered or '(nothing)'}")
    if len(hits) > 1:
        return -1, (f"{name!r} is in more than one bundle; name a card that "
                    f"is only in the one you want")
    return hits[0], ""

def _numbered_titles(entries: list[dict[str, Any]]) -> list[str]:
    """The printed titles of a card list, numbered as the render numbers them."""
    return _number_names([_card_title(e) for e in entries])


def _card_face_key(entry: dict[str, Any]) -> str:
    c = _card_face(entry)
    return f"{c['title']}|{c['cost']}|{c['upgraded']}|{c['text']}"


# The wire's `target_type` spellings, split by what the BRIDGE does with each.
#
# `EB-269`. `ExecuteUsePotion` (`vendor/STS2_MCP/McpMod.Actions.cs:287-306`) is
# the authority and it is a `switch` on `potion.TargetType`: `AnyEnemy` REFUSES
# a post with no `target`, while `Self` / `AnyAlly` / `AnyPlayer` resolve the
# target to the player's own creature and anything else resolves it to nothing.
# So an aimed potion has to be aimed before it is posted and a self-aimed one
# must not carry a target at all -- and a card follows the same table, which is
# why `_play` reads the aimed set from here rather than spelling its own copy.
AIMED_TARGETS = frozenset({"anyenemy", "enemy", "singleenemy", "targetenemy"})
SELF_TARGETS = frozenset({"self", "anyally", "anyplayer"})


def _resolve_enemy(state: dict[str, Any], name: str) -> tuple[str, str]:
    """`(entity id, refusal)` for an enemy named the way the screen names it."""
    enemies = _enemies(state)
    # `EB-177`: numbered over EVERY enemy, then narrowed to the living ones.
    # The render prints a corpse (HP 0) as a line of its own, so numbering the
    # survivors alone would rename `Slug (2)` to `Slug` the moment the first
    # slug died -- the page and the grammar would disagree about which one the
    # tester is looking at, which is the whole defect this closes.
    # `EB-271`: and through the fight's memory, so the same is true of the
    # corpse the feed stops sending. Both sides read the same function off the
    # same list, which is what keeps the page and the grammar in step.
    names = _enemy_names(enemies)
    living = [i for i, e in enumerate(enemies) if _int(e.get("hp")) > 0]
    if not name:
        if len(living) == 1:
            return _entity_id(enemies[living[0]]), ""
        return "", ("there is more than one enemy, so say which: "
                    f"{', '.join(names[i] for i in living)}")
    idx, why = _match([{"n": names[i]} for i in living], name,
                      key=lambda e: e["n"])
    if idx < 0:
        return "", why
    return _entity_id(enemies[living[idx]]), ""


def _pet_target(state: dict[str, Any], name: str) -> str | None:
    """`EB-216`. The jellyfish's entity id when the tester named IT, else None.

    NAMED, NEVER DEFAULTED, and that is the whole decision: "now or at dawn" is
    the choice the slice exists to test (its sec.1), so a card that could go
    either way and was aimed at nothing is played NOW. Only the tester's own
    word sends it to the jellyfish.
    """
    plans = _combat(state).get("plans") if state else None
    if not plans or not plans.get("pet_entity_id") or not name:
        return None
    idx, _ = _match([{"n": plans["pet_name"]}], name, key=lambda e: e["n"])
    return plans["pet_entity_id"] if idx == 0 else None


def _play(state: dict[str, Any], cmd: Command) -> Resolution:
    hand = _hand(state)
    titles = _numbered_titles(hand)
    idx, why = _match(hand, cmd.name, key=_card_title, face=_card_face_key,
                      number=True)
    if idx < 0:
        return _refuse(why)
    entry = hand[idx]
    if entry.get("can_play") is False:
        # `EB-264`: the same translation the page uses, so a refusal and the
        # card's own line cannot disagree about why.
        reason = qa_packet.unplayable_reason(
            entry.get("unplayable_reason_text") or entry.get("unplayable_reason"))
        return _refuse(f"{titles[idx]!r} cannot be played right now"
                       + (f": {reason}" if reason else ""))
    post: dict[str, Any] = {"action": "play_card", "card_index": idx}
    printed = {"card": titles[idx]}
    # `EB-216`. THE JELLYFISH FIRST, because it is the one target that is not
    # an enemy and the refusal a tester would otherwise get ("there is more
    # than one enemy, so say which") would be about the wrong board.
    pet = _pet_target(state, cmd.target)
    if pet is not None:
        post["target"] = pet
        printed["target"] = (_combat(state)["plans"]["pet_name"])
        return Resolution(True, "play", post, printed)
    needs_target = str(entry.get("target_type") or "").lower() in AIMED_TARGETS
    if cmd.target or needs_target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            return _refuse(why)
        post["target"] = eid
        printed["target"] = next(
            (n for e, n in zip(_enemies(state),
                               _enemy_names(_enemies(state)))
             if _entity_id(e) == eid), "")
    return Resolution(True, "play", post, printed)


def _use_potion(state: dict[str, Any], cmd: Command) -> Resolution:
    """`use potion "<title>" [on "<enemy>"]`, resolved against the belt.

    `EB-269`, AND THE DEFECT WAS THE SLOT NUMBER. `BuildPlayerState` walks
    `player.PotionSlots` and SKIPS the empty ones while numbering every slot it
    walks past (`McpMod.StateBuilder.cs:1274-1292`), so each row carries its own
    `slot` and the list position stops agreeing with it the moment a potion is
    spent out of an earlier slot. This function posted the LIST POSITION. On the
    r2 Opus run that is exactly what happened: the Energy Potion in slot 0 was
    drunk, the Dexterity Potion in slot 1 became the only row and therefore list
    index 0, and every `use potion "Dexterity Potion"` for the rest of the run
    posted `slot: 0` -- an empty slot -- and was answered `No potion in slot 0`.
    Three attempts, three failures, on two screens, with a full Skill Potion as
    the seat's last out on the turn it died. The slot is the wire's own number
    now, and the list position is only the fallback for a feed that sends none.

    THE TARGET IS THE POTION'S OWN, and the table is `ExecuteUsePotion`'s. An
    `AnyEnemy` potion is refused by the bridge with no `target`, so it is aimed
    HERE where the refusal can name the enemies instead of coming back as a
    bare word; a `Self` / `AnyAlly` / `AnyPlayer` potion is resolved to the
    player by the bridge whatever is sent, so nothing is sent -- and a tester
    who aimed one anyway is told it went on them rather than being refused for
    a mistake with no consequence.
    """
    potions = _potions(state)
    if not potions:
        return _refuse("you are not carrying any potions")
    idx, why = _match(potions, cmd.name, key=lambda p: _text(p.get("name")))
    if idx < 0:
        return _refuse(why)
    entry = potions[idx]
    slot = entry.get("slot")
    post: dict[str, Any] = {"action": "use_potion",
                            "slot": slot if isinstance(slot, int) else idx}
    printed = {"potion": _text(entry.get("name"))}
    aim = str(entry.get("target_type") or "").strip().lower()
    if aim in SELF_TARGETS:
        printed["target"] = "yourself"
        return Resolution(True, "use potion", post, printed)
    if aim in AIMED_TARGETS or cmd.target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            return _refuse(why)
        post["target"] = eid
        printed["target"] = next(
            (n for e, n in zip(_enemies(state),
                               _enemy_names(_enemies(state)))
             if _entity_id(e) == eid), cmd.target)
    return Resolution(True, "use potion", post, printed)


def _choose(state: dict[str, Any], cmd: Command) -> Resolution:
    """`choose` on whichever screen is up. One verb, six wire actions.

    The screen decides the action, never the shape of the name: the tester says
    the printed thing they want, and this function knows that a card reward
    wants `select_card_reward` while a rest site wants `choose_rest_option`.
    """
    st = _screen(state)
    if st == "card_reward":
        entries = _screen_cards(state)
        idx, why = _match(entries, cmd.name, key=_card_title,
                          face=_card_face_key, number=True)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_card_reward", "card_index": idx},
                          {"card": _numbered_titles(entries)[idx]})
    if st in SELECT_SCREENS:
        # `EB-314`. THE PICK IS ALREADY TAKEN. See `PREVIEW_LOCKED`: the five
        # grid screens keep their selection while the preview is up, only the
        # mouse block stops a second click reaching it, and `select_card`
        # does not go through the mouse. The way out is `skip`, which presses
        # the preview's own Cancel and clears the selection with it.
        if _blob(state, st).get("preview_showing"):
            return _refuse(PREVIEW_LOCKED)
        entries = _screen_cards(state)
        idx, why = _match(entries, cmd.name, key=_card_title,
                          face=_card_face_key, number=True)
        if idx < 0:
            return _refuse(why)
        verb = "select_card" if st == "card_select" else "combat_select_card"
        key = "index" if st == "card_select" else "card_index"
        return Resolution(True, "choose", {"action": verb, key: idx},
                          {"card": _numbered_titles(entries)[idx]})
    if st == "bundle_select":
        # `EB-173`: match on the printed title of any card IN a bundle, the
        # only name this screen has. `_match` is deliberately not reused: its
        # `key` is one string per entry, and a bundle is a set of names.
        entries = _screen_cards(state)
        idx, why = _match_bundle(entries, cmd.name)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_bundle", "index": idx},
                          {"bundle": _named_option(entries[idx])["name"]})
    if st == "event":
        return _index_choice(state, cmd, _event_options(state),
                             "choose_event_option")
    if st == "rest_site":
        return _index_choice(state, cmd, _rest_options(state),
                             "choose_rest_option")
    if st == "rewards":
        # `EB-290`: the same namer and the same numbering the render uses --
        # a page and a grammar that number differently are two screens.
        return _index_choice(state, cmd, _reward_items(state), "claim_reward",
                             namer=_reward_option, number=True)
    if st == "treasure":
        return _index_choice(state, cmd, _relic_options(state),
                             "claim_treasure_relic")
    if st == "relic_select":
        return _index_choice(state, cmd, _relic_options(state), "select_relic")
    return _refuse("there is nothing to choose on this screen")


def _index_choice(state: dict[str, Any], cmd: Command, entries: list[Any],
                  action: str, *,
                  namer: Callable[[Any], dict[str, Any]] = _named_option,
                  number: bool = False) -> Resolution:
    """A `choose` that posts an index into a list of PRINTED options.

    The index posted is the option's own `index` field where the wire supplies
    one and its LIST POSITION otherwise -- event options carry an explicit
    index and the walker in `soak` reads it, while a rest site is indexed by
    position. Resolved here, at the moment of posting, for `naming.py:14-17`'s
    reason.

    `namer` and `number` (`EB-290`) exist so that a screen whose RENDER names
    its rows differently resolves them the same way. They are passed by the
    caller that renders that screen and by no other: a caller whose page does
    not number must not number its grammar (`_match`'s own rule).
    """
    options = [namer(o) for o in entries]
    names = [o["name"] for o in options]
    if number:
        names = _number_names(names)
    idx, why = _match([{"n": n} for n in names], cmd.name,
                      key=lambda e: e["n"])
    if idx < 0:
        return _refuse(why)
    if not options[idx]["enabled"]:
        return _refuse(f"{names[idx]!r} is on the screen but not "
                       f"available to take")
    raw = entries[idx]
    posted = raw.get("index") if isinstance(raw, dict) else None
    return Resolution(True, "choose",
                      {"action": action,
                       "index": posted if isinstance(posted, int) else idx},
                      {"option": names[idx]})


def _go(state: dict[str, Any], cmd: Command) -> Resolution:
    if not _map_nodes(state):
        return _refuse("the map is not asking for a move right now")
    options = _map_options(state)
    idx, why = _match([{"n": o["name"]} for o in options], cmd.name,
                      key=lambda e: e["n"])
    if idx < 0:
        return _refuse(why)
    return Resolution(True, "go", {"action": "choose_map_node", "index": idx},
                      {"node": options[idx]["name"]})


def _buy(state: dict[str, Any], cmd: Command) -> Resolution:
    items = _shop_items(state)
    if not items:
        return _refuse("there is nothing on the shelves")
    # `EB-262`: the SAME reader the page uses, remembered shelves and all --
    # a grammar that could not name a row the page printed would be a second
    # screen. `_shop_options` only ever adds a name it printed itself.
    options = _shop_options(state)
    idx, why = _match([{"n": o["name"]} for o in options], cmd.name,
                      key=lambda e: e["n"])
    if idx < 0:
        return _refuse(why)
    if not options[idx]["enabled"]:
        # `EB-262`: a shelf the wire marks `is_stocked: false` has already been
        # bought. The page prints it as not available; the grammar agrees.
        return _refuse(f"{options[idx]['name']!r} is on the shelf but not "
                       f"available to buy")
    price = options[idx]["price"]
    gold = _int(_player(state).get("gold"))
    if price is not None and price > gold:
        return _refuse(f"{options[idx]['name']!r} costs {price} gold and you "
                       f"have {gold}")
    return Resolution(True, "buy", {"action": "shop_purchase", "index": idx},
                      {"item": options[idx]["name"], "price": price})


def _rest_keyword(state: dict[str, Any], cmd: Command,
                  keywords: tuple[str, ...]) -> Resolution:
    """`rest` / `upgrade` / `remove` at a rest site, by the printed option.

    On a CARD screen the same two words mean "pick this card", and that is
    handled by falling through to `_choose` -- the screen decides, exactly as
    it does for `choose`.
    """
    options = [_named_option(o) for o in _rest_options(state)]
    if not options:
        return _refuse("this rest site is not offering anything")
    for i, o in enumerate(options):
        folded = _fold(o["name"])
        if any(k in folded for k in keywords):
            if not o["enabled"]:
                return _refuse(f"{o['name']!r} is not available")
            raw = _rest_options(state)[i]
            posted = raw.get("index") if isinstance(raw, dict) else None
            return Resolution(
                True, cmd.verb,
                {"action": "choose_rest_option",
                 "index": posted if isinstance(posted, int) else i},
                {"option": o["name"]})
    return _refuse(f"nothing here offers to {cmd.verb}. What is offered: "
                   + ", ".join(o["name"] for o in options))


def _not_in_battle(obs: dict[str, Any]) -> str:
    """Why a combat verb cannot be taken on THIS screen (`EB-290`).

    THE FLAT REFUSAL WAS FACTUALLY WRONG. `use potion "Touch of Insanity"`
    opened *"Choose a card to make free."*, which is a combat overlay the wire
    names `hand_select` and this page renders as a card chooser; the next
    `play "Big Badda Boom" on "Sewer Clam"` came back *"you are not in a
    battle"* at a tester who was in one, round one, with the Sewer Clam on the
    screen. The r4 Opus seat filed it as a wrong answer, which is what it was:
    the true reason is that a chooser is open and wants an answer first, and
    the way out is the grammar the page is already offering three lines above.
    An overlay this page renders as a chooser therefore names itself, quotes
    its own prompt and lists its own verbs; every other screen keeps the old
    sentence, because there it is true.
    """
    if obs["screen"] not in ("card_select", "bundle_select", "card_reward"):
        return "you are not in a battle"
    prompt = str(obs.get("prompt") or "").strip()
    verbs = ", ".join(f"`{c}`" for c in obs["commands"])
    return ("a card chooser is open and has to be answered first"
            + (f' — "{prompt}"' if prompt else "")
            + (f". What you can say here: {verbs}" if verbs else ""))


def act(state: dict[str, Any], command: str) -> dict[str, Any]:
    """Resolve one player-language command against the CURRENT state.

    Returns the `Resolution` as a dict. It does NOT post -- the caller posts,
    so that the state a command was resolved against and the state it is sent
    to are provably the same frame.
    """
    try:
        cmd = parse_command(command)
    except BlindPlayError as exc:
        return _refuse(str(exc)).as_dict()

    st = _screen(state)
    obs = observation(state)
    if obs["blocked"]:
        return _refuse(f"this screen is not being driven: {obs['blocked']}"
                       ).as_dict()

    if cmd.verb == "play":
        res = (_play(state, cmd) if st in COMBAT_SCREENS
               else _refuse(_not_in_battle(obs)))
    elif cmd.verb == "use potion":
        res = _use_potion(state, cmd)
    elif cmd.verb == "end turn":
        res = (Resolution(True, "end turn", {"action": "end_turn"}, {})
               if st in COMBAT_SCREENS else _refuse(_not_in_battle(obs)))
    elif cmd.verb == "choose":
        res = _choose(state, cmd)
    elif cmd.verb == "go":
        res = _go(state, cmd) if st == "map" else _refuse("the map is not up")
    elif cmd.verb == "buy":
        res = (_buy(state, cmd) if st in ("shop", "fake_merchant")
               else _refuse("you are not in a shop"))
    elif cmd.verb == "rest":
        res = (_rest_keyword(state, cmd, ("rest", "sleep", "heal"))
               if st == "rest_site" else _refuse("there is nowhere to rest"))
    elif cmd.verb in ("upgrade", "remove"):
        if st == "rest_site":
            words = (("upgrade", "smith", "forge") if cmd.verb == "upgrade"
                     else ("remove", "purge", "toss"))
            res = _rest_keyword(state, cmd, words)
        elif st in SELECT_SCREENS and cmd.name:
            res = _choose(state, cmd)
        else:
            res = _refuse(f"nothing here can {cmd.verb} a card")
    elif cmd.verb == "confirm":
        res = _confirm(state)
    elif cmd.verb == "skip":
        res = _skip(state)
    elif cmd.verb == "proceed":
        res = _proceed(state)
    else:                                                # pragma: no cover
        res = _refuse(f"{cmd.verb!r} is not wired to anything")
    res.verb = res.verb or cmd.verb
    return res.as_dict()


def _confirm(state: dict[str, Any]) -> Resolution:
    st = _screen(state)
    verbs = {"card_select": "confirm_selection",
             "hand_select": "combat_confirm_selection",
             "bundle_select": "confirm_bundle_selection"}
    if st not in verbs:
        return _refuse("there is nothing waiting to be confirmed")
    return Resolution(True, "confirm", {"action": verbs[st]}, {})


def _skip(state: dict[str, Any]) -> Resolution:
    st = _screen(state)
    if st == "card_reward":
        blob = _blob(state, "card_reward")
        if blob.get("can_skip") is False:
            return _refuse("this card reward cannot be skipped")
        return Resolution(True, "skip", {"action": "skip_card_reward"}, {})
    if st == "relic_select":
        return Resolution(True, "skip", {"action": "skip_relic_selection"}, {})
    if st in SELECT_SCREENS:
        blob = _blob(state, st)
        if not (blob.get("can_skip") or blob.get("can_cancel")):
            return _refuse("this screen will not let you leave without "
                           "choosing")
        verb = ("cancel_selection" if st == "card_select"
                else "combat_confirm_selection")
        return Resolution(True, "skip", {"action": verb}, {})
    return _refuse("there is nothing here to skip")


def _proceed(state: dict[str, Any]) -> Resolution:
    st = _screen(state)
    if st == "event" and _blob(state, "event").get("in_dialogue"):
        return Resolution(True, "proceed", {"action": "advance_dialogue"}, {})
    if st == "event":
        # `EB-259`. AN EVENT ROOM HAS NO PROCEED BUTTON. `ExecuteProceed`
        # never looks at one (`McpMod.Actions.cs:600-663`), so the bare verb
        # used to post an action the event refused outright and the tester
        # lost the action. Where the screen prints a *Proceed* option, that is
        # what the word means here, and it is posted as the choice it is.
        entries = _event_options(state)
        idx = _proceed_option(state)
        if idx < 0:
            offered = ", ".join(o["name"]
                                for o in (_named_option(x) for x in entries)
                                if o["name"])
            return _refuse("this event has no Proceed to take; choose one of "
                           f"its options: {offered or '(nothing printed)'}")
        option = _named_option(entries[idx])
        posted = entries[idx].get("index") if isinstance(entries[idx],
                                                         dict) else None
        return Resolution(True, "proceed",
                          {"action": "choose_event_option",
                           "index": posted if isinstance(posted, int) else idx},
                          {"option": option["name"]})
    if st in ("rewards", "treasure", "shop", "fake_merchant", "rest_site"):
        return Resolution(True, "proceed", {"action": "proceed"}, {})
    return _refuse("there is nothing to leave from this screen")
