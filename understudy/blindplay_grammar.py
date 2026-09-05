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
from understudy.blindplay_board import (_bundle_cards, _combat, _event_option,
                                        _event_options, _map_nodes,
                                        _map_options, _proceed_option,
                                        _relic_options, _rest_options,
                                        _reward_items, _screen_cards)
from understudy.blindplay_faces import (_card_face, _card_title,
                                        _enemy_handles, _enemy_names,
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
         "upgrade", "remove", "use potion", "drop potion", "confirm",
         "proceed")


@dataclass
class Command:
    verb: str
    names: list[str] = field(default_factory=list)
    raw: str = ""
    # `EB-341`: `choose 2`, the row's PLACE in the list the page printed.
    # 0 means the tester named a thing instead, which is every other command.
    ordinal: int = 0

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
    # `EB-371`. Two words, like `use potion`, and read before the bare-first-
    # word rule for the same reason: `drop` alone is not a verb here, and a
    # tester who types `drop "Fire Potion"` is told so by the VERBS list.
    elif head.startswith("drop potion") or head.startswith("drop the potion"):
        verb = "drop potion"
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
    # `EB-341`. THE ORDINAL, AND WHY THE GRAMMAR NEEDED A SECOND HANDLE.
    #
    # The Future of Potions printed two options titled, character for
    # character, `Insert Common Potion` -- one losing a Flex Potion, one losing
    # a Dexterity Potion -- and a grammar that addresses options by title has
    # no way to say which. The r7b act-2b seat sent the title, was "accepted
    # with an empty refusal", and inferred which one had been taken from the
    # rarity of the reward pool afterwards.
    #
    # So a printed row may also be named by its PLACE, which is the one handle
    # every screen has and no screen can print twice. Quoted names still win
    # wherever the tester gave one; a bare number is only ever read as an
    # ordinal, because no screen names a row `2`.
    ordinal = 0
    if verb == "choose" and not names:
        m = re.fullmatch(r"choose\s+#?(\d+)", head)
        if m is None:
            raise BlindPlayError("`choose` needs a name in quotes, or the "
                                 "number of a row on the screen (`choose 2`)")
        ordinal = int(m.group(1))
        if ordinal < 1:
            raise BlindPlayError("the rows on a screen are counted from 1")
    # `EB-371`: the same second handle on the belt, and the row asks for it by
    # name (`drop potion <n>`). A potion is the one list on this page a screen
    # can print twice over -- two Fire Potions in two slots -- so the ordinal
    # is not a convenience here either.
    if verb == "drop potion" and not names:
        m = re.fullmatch(r"drop (?:the )?potion\s+#?(\d+)", head)
        if m is None:
            raise BlindPlayError(
                "`drop potion` needs a name in quotes, or the number of a "
                "potion on your belt (`drop potion 2`)")
        ordinal = int(m.group(1))
        if ordinal < 1:
            raise BlindPlayError("the potions on your belt are counted from 1")
    return Command(verb=verb, names=names, raw=raw, ordinal=ordinal)


# ------------------------------------------------------------- resolution --

@dataclass
class Resolution:
    """What a command means against the state it was typed at.

    `post` is the wire body and is the ONLY place an id lives; `printed` is the
    same decision in the names the screen used, and is what may be echoed back
    to the tester.

    `forms` is `EB-319`: the command(s) that WOULD have resolved, in the
    tester's own grammar. It is not part of `as_dict` -- `act` folds it into
    the refusal sentence, so every reader of a refusal gets the way out
    without having to know a second key exists.
    """
    ok: bool
    verb: str = ""
    post: dict[str, Any] | None = None
    printed: dict[str, Any] = field(default_factory=dict)
    refusal: str = ""
    forms: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "verb": self.verb, "post": self.post,
                "printed": self.printed, "refusal": self.refusal}


def _refuse(why: str, *forms: str) -> Resolution:
    """A refusal, and the form(s) that resolve where this one did not.

    `EB-319`. `play "Rapid Fire" on "Seapunk"` came back *Rapid Fire is
    random-target and takes no target* -- true, complete about the mistake and
    silent about the repair. The seat was mid-chain, the turn ended, and an
    Attack Potion's 12 free damage went with it: "the message had the
    information and withheld it" (round-7 act-1 seat, Fight 5). The ambiguity
    refusal had listed the numbered names that would work since `EB-177`, so
    the page was already keeping the promise on one refusal in twenty.

    Every refusal keeps it now. A site that knows the exact command names it
    here; a site that does not falls back in `act` to the screen's own
    "What you can say" list, which is the same list the page prints and is
    therefore never a form the tester has not already been offered.
    """
    return Resolution(ok=False, refusal=why, forms=forms)


def _with_forms(res: Resolution, obs: dict[str, Any]) -> Resolution:
    """Fold `EB-319`'s way out into the refusal sentence.

    The screen's `commands` are the fallback and not a second-best one: they
    are the grammar the render prints under *What you can say*, so a refusal
    that ends in them can never send a tester somewhere the page did not. A
    screen that is not being driven has none, and then the refusal stands
    alone -- there is no form that resolves, and inventing one would be worse
    than the silence this row closes.
    """
    if res.ok:
        return res
    forms = list(res.forms) or [str(c) for c in obs.get("commands") or []]
    if not forms:
        return res
    lead = ("The form that resolves: " if len(forms) == 1
            else "Forms that resolve here: ")
    why = res.refusal.rstrip()
    if why and not why.endswith((".", "!", "?", ":")):
        why += "."
    res.refusal = f"{why} {lead}{'; '.join(forms)}".strip()
    return res


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
           number: bool = False, ordinal: int = 0,
           advice: str = "") -> tuple[int, str]:
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
    # `EB-341`: the ordinal FIRST, because it is the handle a tester reaches
    # for exactly when the printed names cannot separate two rows. It is the
    # place in the same list the render printed, counted from 1, and a number
    # off the end is refused with the count rather than clamped.
    if ordinal:
        if 1 <= ordinal <= len(printed):
            return ordinal - 1, ""
        return -1, (f"there is no row {ordinal} on this screen; it has "
                    f"{len(printed)}"
                    + (": " + ", ".join(f"{i}. {p}"
                                        for i, p in enumerate(printed, 1) if p)
                       if printed else ""))
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
        # `EB-341`. ONE PRINTED NAME, TWO ROWS, DIFFERENT BODIES -- and the
        # old answer was to TAKE THE FIRST, silently: `choices` has collapsed
        # to one name by here, the upgrade qualifier means nothing on an event
        # option, and with `face` unset the walk fell through to `hits[0]` at
        # the bottom of this function. That is what handed a seat `Insert
        # Common Potion` and never said which. A caller with an ordinal to
        # advertise refuses instead, and says how to be exact. It sits BELOW
        # the branch above on purpose: where the printed names still differ,
        # naming one of them back is better advice than a number.
        if advice:
            return -1, (f"{name!r} names more than one row on this screen and "
                        f"they do different things. {advice}")
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


def _prints_all_enemies(entry: dict[str, Any]) -> bool:
    """Does this card's PRINTED face say `ALL enemies`? (`EB-527`.)

    THE WORD IS THE BASE GAME'S OWN AND IT IS SPELLED ONE WAY: 47 uses, 0
    lowercase (`docs/current/text-conventions.md` rule 4), so the test is the
    literal rather than a pattern. It is asked ONLY to explain a refusal --
    the target type is read off the WIRE and decides everything, exactly as
    `EB-499` decided the other direction -- so a face that says something this
    misses simply gets the sentence it always got.
    """
    return "ALL enemies" in _text(_card_face(entry).get("text"))


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

# `EB-319`. The spellings that take NO enemy of the tester's choosing: the
# game aims these itself, or aims them at nobody. `Rapid Fire` -- "Deal 3
# damage to a random enemy 4 times" -- is `AllEnemies` here, which is why
# `play "Rapid Fire" on "Fossil Stalker"` used to be POSTED and then refused
# by the bridge's own `IsValidTarget` (`McpMod.Actions.cs:205-210`), a round
# trip whose answer named the card, named the enemy and named no way to play
# it. The set is CLOSED and holds the game's own enum names only: a custom
# single-target type renders as a bare number on the wire (`EB-216`), matches
# nothing here, and keeps the fall-through that lets a Plan card be aimed.
UNAIMED_TARGETS = frozenset({"none", "allenemies"}) | SELF_TARGETS


def _aims_at_an_enemy(entry: dict[str, Any]) -> bool:
    """Does this hand card need an enemy of the tester's choosing? `EB-402`.

    THE DEFECT, in one line: `play "Slack Water"` with no `on` clause was
    answered `ok` and did nothing -- no damage, no Weak -- on the Kokomi
    round-10 seat, while an `AllEnemies` card played bare resolved.

    WHY. Six of the arm's cards are `KokomiTargets.PetOrEnemy`, a CUSTOM target
    type minted at `ModelDb.Init`, so `card.TargetType.ToString()` renders a
    bare NUMBER on the wire (`EB-216`) and matches nothing in `AIMED_TARGETS`.
    The bridge's `ExecutePlayCard` only demands a target for
    `TargetType.AnyEnemy` (`McpMod.Actions.cs:152`), so the play was posted
    with a NULL target, reached `PlayCardAction(card, null)`, and the card's
    own `ArgumentNullException.ThrowIfNull(cardPlay.Target)` ended it inside
    the action queue -- after the wire had already answered `ok`.

    AND WHY THE NUMBER ALONE IS NOT ENOUGH. The other two custom spellings
    render as bare numbers too, and for BOTH of them a bare play is correct:
    `PetOrSelf` (ten cards, e.g. Tide Wall) falls through to its now-line on
    the player, and `PetOnly` (two) schedules its Plan with no target read. So
    the question is asked of the CARD rather than of the spelling, through the
    bridge's `can_target_enemy` (`EB-402`, the twin of `EB-216`'s
    `can_target_pet`): both are `CardModel.IsValidTarget`, which is the game's
    own gate and is prefixed by BaseLib for every custom type.

    An ABSENT `can_target_enemy` is a build that predates the field, and it
    reads as the behaviour that build has: the named spellings decide and a
    custom one falls through, exactly as before.
    """
    aim = str(entry.get("target_type") or "").lower()
    if aim in AIMED_TARGETS:
        return True
    if not aim or aim in UNAIMED_TARGETS:
        return False
    return entry.get("can_target_enemy") is True


def _potion_aims_at_an_enemy(entry: dict[str, Any]) -> bool:
    """Does this potion need an enemy of the tester's choosing? `EB-452`.

    THE DEFECT, in one line: on the Kokomi round-13 boss, turn 5,
    `use potion "Weak Potion"` with no `on` clause was accepted, the potion
    was spent, no Weak landed on any of the three bodies, no intent moved,
    and no refusal was printed anywhere.

    WHY IT WAS ACCEPTED. This function's card twin (`_aims_at_an_enemy`)
    falls THROUGH to "aims itself" on a spelling it does not know, because
    the arm mints custom card target types that legitimately play bare -- a
    Plan on the pet, a now-line on the player. A POTION has neither form:
    `ExecuteUsePotion`'s switch resolves `AnyEnemy` from the tester's own
    `target`, resolves the three self spellings to the player whatever is
    sent, and answers every other spelling with `default: target = null`
    (`McpMod.Actions.cs:286-306`) -- then enqueues the use anyway. So a
    spelling this page does not know is the one case where the game spends
    the potion on nobody and says `ok`, which is exactly what the seat saw.

    So the fall-through is the OTHER WAY here, and it is the conservative
    direction: only a potion the game itself aims -- `AllEnemies`, `None`,
    the three self spellings -- is used bare, and everything else is asked
    for an enemy. A potion refused for want of a target costs one refusal
    with the working forms in it; a potion drunk into the void costs the
    potion. An ABSENT `target_type` is a feed that has not said, and reads as
    unaimed, the same way the card twin reads it.
    """
    aim = str(entry.get("target_type") or "").strip().lower()
    if aim in AIMED_TARGETS:
        return True
    return bool(aim) and aim not in UNAIMED_TARGETS


def _fight_round(state: dict[str, Any]) -> int:
    """The battle round of this board (`EB-541`).

    The grammar reads the same memory the render does, so it has to ask the
    same fight-boundary question with the same fact -- a grammar that reset the
    letters the render had just minted would put the two back out of step,
    which is what `_resolve_enemy`'s own note is about.
    """
    return _int(_blob(state, "battle").get("round"))


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
    names = _enemy_names(enemies, _fight_round(state))
    # `EB-496`: the letter the page prints beside each body, which is the same
    # memory the numbers come out of. Read here so the grammar and the render
    # cannot mean different bodies by `B`.
    handles = _enemy_handles(enemies)
    living = [i for i, e in enumerate(enemies) if _int(e.get("hp")) > 0]
    if not name:
        if len(living) == 1:
            return _entity_id(enemies[living[0]]), ""
        return "", ("there is more than one enemy, so say which: "
                    f"{', '.join(names[i] for i in living)}")
    # THE LETTER IS AN EXACT MATCH AND NOTHING ELSE. `_match` takes a unique
    # SUBSTRING, and a bare `A` is a substring of half the names on any board;
    # a handle is one token that either is or is not the body's own.
    want = _fold(name)
    for i in living:
        if handles[i] and _fold(handles[i]) == want:
            return _entity_id(enemies[i]), ""
    idx, why = _match([{"n": names[i]} for i in living], name,
                      key=lambda e: e["n"])
    if idx < 0:
        return "", why
    return _entity_id(enemies[living[idx]]), ""


def _living_enemy_names(state: dict[str, Any]) -> list[str]:
    """The printed names of the living enemies, numbered as the render numbers
    them (`EB-402`, and the numbering is `_resolve_enemy`'s own)."""
    enemies = _enemies(state)
    names = _enemy_names(enemies, _fight_round(state))
    return [names[i] for i, e in enumerate(enemies) if _int(e.get("hp")) > 0]


# `EB-519`: A LETTER IS A BODY ON THE OTHER SIDE, AND NEVER THE PET.
#
# THE DEFECT (Kokomi r18, both lanes). `EB-496` minted the per-fight letter and
# `_resolve_enemy` matches it EXACTLY, for the reason written there: a bare `A`
# is a unique SUBSTRING of half the names on any board. The pet's own lookup
# was left on `_match` and so kept the substring rule -- and the jellyfish is
# called `Bake-Kurage`, which folds to `bakekurage` and therefore CONTAINS
# `a`, `b`, `e`, `g`, `k`, `r` and `u`. Seven of the first letters a fight
# hands out are the pet, and the pet block sits ABOVE the enemy block, so
# `on "A"` was refused as a Plan the card could not carry ("cannot be planned
# on Bake-Kurage") and `on "B"` was silently ACCEPTED as one -- writing a Plan
# the seat never asked for out of a card it had aimed at the second body.
#
# THE SHAPE OF THE HANDLE IS THE TEST, not the board's current letters: one
# letter, or `E27` and up, is `_handle_for`'s whole output and is not a name
# anything in this game prints. Declining it here sends it one block down to
# `_resolve_enemy`, which either resolves it exactly or refuses it with the
# living bodies listed -- both of which are about the right side of the board.
# The pet KEEPS ITS NAME: `Bake-Kurage`, and every unique substring of it that
# is not a bare handle, still reach the jellyfish exactly as before.
_ENEMY_HANDLE = re.compile(r"^(?:[a-z]|e[0-9]+)$")


def _is_enemy_handle(name: str) -> bool:
    """Is this word one of `EB-496`'s per-fight letters rather than a name?"""
    return bool(_ENEMY_HANDLE.match(_fold(name)))


def _pet_target(state: dict[str, Any], name: str) -> str | None:
    """`EB-216`. The jellyfish's entity id when the tester named IT, else None.

    NAMED, NEVER DEFAULTED, and that is the whole decision: "now or at dawn" is
    the choice the slice exists to test (its sec.1), so a card that could go
    either way and was aimed at nothing is played NOW. Only the tester's own
    word sends it to the jellyfish.

    `EB-519`: and never by a LETTER, for the reason written above this function.
    """
    plans = _combat(state).get("plans") if state else None
    if not plans or not plans.get("pet_entity_id") or not name:
        return None
    if _is_enemy_handle(name):
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
    # `EB-319`, and it is refused HERE rather than by the game. The card aims
    # itself; naming an enemy is the tester's only mistake, and the command
    # that works is the same one without the `on` clause. Posting it would
    # spend the action and come back `Card 'Rapid Fire' cannot be played on
    # 'Fossil Stalker'`, which is what happened.
    aim = str(entry.get("target_type") or "").lower()
    if (cmd.target and aim in UNAIMED_TARGETS
            and not entry.get("can_target_pet")):
        return _refuse(
            f"{titles[idx]!r} "
            + ("is played on you, not on an enemy" if aim in SELF_TARGETS
               else "does its own aiming")
            + f', so it takes no `on "{cmd.target}"`',
            f'play "{titles[idx]}"')
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
        # `EB-480`. A CARD THAT CANNOT BE PLANNED IS REFUSED HERE, not posted.
        #
        # THE FIND (Kokomi r16 (c) 1). `play "Strike" on "Bake-Kurage"` came
        # back `ok` with an empty refusal, burned one of the run's 120 actions
        # and changed nothing -- energy, hand and discard as before, "Nothing
        # is planned." The post is accepted by the bridge, reaches
        # `PlayCardAction(card, pet)`, and the card's own now-line runs against
        # a target it does not read, which for a `Strike` is a no-op.
        #
        # `can_target_pet` IS THE FACT, and it is the game's own answer:
        # `CardModel.IsValidTarget` for the pet, asked per hand card by the
        # bridge (`McpMod.StateBuilder.BuildCardState`, `EB-216`). A `false`
        # here means the drag would not land, which is exactly what the tester
        # just tried to do in words.
        #
        # ONLY AN EXPLICIT `false` REFUSES, `_aims_at_an_enemy`'s rule for its
        # own twin: an ABSENT field is a bridge that predates it, and on such a
        # feed this reads as the behaviour that build has -- the play goes
        # through, exactly as before.
        #
        # THE REFUSAL LISTS THE PLAN CARDS IN HAND, which is `EB-402`'s repair
        # one clause over: the way out is in the refusal rather than a screen
        # away, and where the hand holds none the bare form is the only one
        # offered because it is the only one that works.
        if entry.get("can_target_pet") is False:
            pet_name = _text(_combat(state)["plans"].get("pet_name"))
            plannable = [t for e, t in zip(hand, titles)
                         if e.get("can_target_pet") is True]
            return _refuse(
                f"{titles[idx]!r} cannot be planned on {pet_name}, so aiming "
                "it there would spend the action and do nothing",
                *(f'play "{t}" on "{pet_name}"' for t in plannable),
                f'play "{titles[idx]}"')
        post["target"] = pet
        printed["target"] = (_combat(state)["plans"]["pet_name"])
        return Resolution(True, "play", post, printed)
    # `EB-499`. THE SAME REFUSAL AS `EB-319`, FOR THE CARDS WHOSE SPELLING IS A
    # NUMBER -- and it is HERE, under the pet, because by this line the tester
    # has not named the jellyfish and the only body left to mean is an enemy.
    #
    # THE DEFECT (Kokomi r17 lane 1, turn 1 of an 84-HP elite that gains
    # Strength every round). `play "Riptide" on "Byrdonis"` was POSTED, and the
    # bridge answered `Card 'Riptide' cannot be played on 'Byrdonis'` -- a
    # sentence that names the card, names the enemy and names no way to play
    # it. Riptide is "Deal 9 damage to ALL enemies"; the working form is the
    # bare `play "Riptide"`, and the seat did not find it for four rounds:
    # "that refusal is the largest single reason this run ended on floor 8".
    #
    # WHY `EB-319`'s GUARD MISSED IT. That guard reads the SPELLING, and the
    # arm's cards do not have one: a custom target type renders as a bare
    # NUMBER on the wire (`EB-216`), so `allenemies` never matched and the play
    # fell through to the post. The fact is on the feed all the same --
    # `can_target_enemy`, the game's own `IsValidTarget` asked per card
    # (`EB-402`) -- and an explicit `false` beside a named enemy is this
    # mistake exactly.
    #
    # ONLY AN EXPLICIT `false`, `EB-402`'s and `EB-480`'s shared rule: an
    # ABSENT field is a bridge that predates it and keeps the behaviour that
    # build has.
    if (cmd.target and aim not in AIMED_TARGETS
            and entry.get("can_target_enemy") is False):
        return _refuse(
            f'{titles[idx]!r} does its own aiming, so it takes no '
            f'`on "{cmd.target}"`',
            f'play "{titles[idx]}"')
    needs_target = _aims_at_an_enemy(entry)
    if cmd.target or needs_target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            # `EB-402`. A card that has to be aimed and was not is refused with
            # the `on` form listed back per living enemy, so the way out is in
            # the refusal rather than one screen away.
            #
            # `EB-527`. AND WHERE THE FACE SAYS OTHERWISE, THE REFUSAL SAYS SO.
            # Two faces printing "ALL enemies" took opposite forms on one
            # screen (Furina r12 lane 2): `Lynette -- Magic Trick` was refused
            # BARE with "there is more than one enemy, so say which", and the
            # very next turn `Chevreuse -- Ring of Bursting Grenades` was
            # refused WITH `on` -- "two cards, both printing ALL enemies, with
            # opposite targeting rules and nothing on either face to tell them
            # apart", which cost the seat an elite turn.
            #
            # THE WIRE IS RIGHT AND THE FACE IS INCOMPLETE. Magic Trick's Swirl
            # half needs a body, so the game aims the card at one; the ALL in
            # its damage clause is true of what the hit does and not of how it
            # is played. `EB-499` gave the other direction its own sentence
            # ("does its own aiming, so it takes no `on`"); this is that
            # sentence's twin, so both refusals name the form that works AND
            # say why the face did not predict it.
            if not cmd.target and _prints_all_enemies(entry):
                why = (f"{titles[idx]!r} prints \"ALL enemies\" and is still "
                       "aimed at one body, so say which: "
                       + ", ".join(_living_enemy_names(state)))
            return _refuse(why, *(f'play "{titles[idx]}" on "{n}"'
                                  for n in _living_enemy_names(state)))
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
    a mistake with no consequence. `EB-452` widened the first half from the
    `AnyEnemy` spelling to every spelling the game does not aim itself, for
    the reason in `_potion_aims_at_an_enemy`: on the others the bridge passes
    a null target, spends the potion and answers `ok`.
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
    if _potion_aims_at_an_enemy(entry) or cmd.target:
        eid, why = _resolve_enemy(state, cmd.target)
        if not eid:
            # `EB-452`, and it is `_play`'s own repair one verb over: a potion
            # that has to be aimed and was not is refused with the `on` form
            # listed back per living enemy, so the working command is in the
            # refusal rather than a screen away.
            return _refuse(why, *(f'use potion "{printed["potion"]}" on "{n}"'
                                  for n in _living_enemy_names(state)))
        post["target"] = eid
        printed["target"] = next(
            (n for e, n in zip(_enemies(state),
                               _enemy_names(_enemies(state)))
             if _entity_id(e) == eid), cmd.target)
    return Resolution(True, "use potion", post, printed)


def _drop_potion(state: dict[str, Any], cmd: Command) -> Resolution:
    """`drop potion "<title>"` or `drop potion <n>`, off the belt. `EB-371`.

    THE ROW, IN ONE SENTENCE: at three of three a potion reward is refused
    ("a potion claimed now has nowhere to go", `_full_slots`) and until this
    verb existed there was nothing a seat outside a fight could do about it.
    The r9 act-1 seat lost both of Tiny Mailbox's rest-site potions that way.

    THE SLOT IS THE WIRE'S OWN NUMBER, `_use_potion`'s hard-won lesson
    (`EB-269`): `BuildPlayerState` skips empty slots while numbering the ones
    it walks past, so the list position stops agreeing with the slot the
    moment a potion is spent out of an earlier one, and `ExecuteDiscardPotion`
    refuses an empty slot by number. The list position is the fallback for a
    feed that sends none, exactly as it is one function up.

    NO SCREEN TEST HERE. `ExecuteDiscardPotion` (`McpMod.Actions.cs:325`)
    wants a run in progress and a potion in the slot -- no combat, no play
    phase, no usability check -- so the only question this page can honestly
    ask is whether the screen is being driven at all, and `act` has already
    asked it.
    """
    potions = _potions(state)
    if not potions:
        return _refuse("you are not carrying any potions")
    if cmd.ordinal:
        if cmd.ordinal > len(potions):
            return _refuse(
                f"you are carrying {len(potions)} potion(s), so there is no "
                f"number {cmd.ordinal} on your belt")
        idx = cmd.ordinal - 1
    else:
        idx, why = _match(potions, cmd.name,
                          key=lambda p: _text(p.get("name")))
        if idx < 0:
            return _refuse(why)
    entry = potions[idx]
    slot = entry.get("slot")
    post = {"action": "discard_potion",
            "slot": slot if isinstance(slot, int) else idx}
    return Resolution(True, "drop potion", post,
                      {"potion": _text(entry.get("name"))})


def _card_taken(entries: list[dict[str, Any]], idx: int) -> dict[str, Any]:
    """The card a `choose` took, printed (`EB-341`).

    The title the page numbered, plus the card's own body where it has one --
    so the line after a pick names the thing that was added rather than only
    its name, which is the half a seat was reading off a later screen.
    """
    printed: dict[str, Any] = {"card": _numbered_titles(entries)[idx]}
    body = _card_face(entries[idx])["text"]
    if body:
        printed["text"] = body
    return printed


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
                          face=_card_face_key, number=True,
                          ordinal=cmd.ordinal)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_card_reward", "card_index": idx},
                          _card_taken(entries, idx))
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
                          face=_card_face_key, number=True,
                          ordinal=cmd.ordinal)
        if idx < 0:
            return _refuse(why)
        verb = "select_card" if st == "card_select" else "combat_select_card"
        key = "index" if st == "card_select" else "card_index"
        return Resolution(True, "choose", {"action": verb, key: idx},
                          _card_taken(entries, idx))
    if st == "bundle_select":
        # `EB-173`: match on the printed title of any card IN a bundle, the
        # only name this screen has. `_match` is deliberately not reused: its
        # `key` is one string per entry, and a bundle is a set of names.
        entries = _screen_cards(state)
        if cmd.ordinal:
            # `EB-341`: a bundle has no name of its own (`EB-173`), so its
            # place on the screen is the second handle here too.
            idx, why = _match([{"n": ""} for _ in entries], "",
                              key=lambda e: e["n"], ordinal=cmd.ordinal)
        else:
            idx, why = _match_bundle(entries, cmd.name)
        if idx < 0:
            return _refuse(why)
        return Resolution(True, "choose",
                          {"action": "select_bundle", "index": idx},
                          {"bundle": _named_option(entries[idx])["name"]})
    if st == "event":
        # `EB-448`: the page's own namer, so the line after the command names
        # the card or relic the option hands over rather than only the
        # sentence promising one.
        return _index_choice(state, cmd, _event_options(state),
                             "choose_event_option", namer=_event_option)
    if st == "rest_site":
        return _index_choice(state, cmd, _rest_options(state),
                             "choose_rest_option")
    if st == "rewards":
        # `EB-290`: the same namer and the same numbering the render uses --
        # a page and a grammar that number differently are two screens.
        res = _index_choice(state, cmd, _reward_items(state), "claim_reward",
                            namer=_reward_option, number=True)
        return _full_slots(state, res) or res
    if st == "treasure":
        return _index_choice(state, cmd, _relic_options(state),
                             "claim_treasure_relic")
    if st == "relic_select":
        return _index_choice(state, cmd, _relic_options(state), "select_relic")
    return _refuse("there is nothing to choose on this screen")


def _full_slots(state: dict[str, Any], res: Resolution) -> Resolution | None:
    """Refuse a potion claim the run has no slot for. `None` otherwise.

    `EB-341`. THE POTION THAT VANISHED. The r7b act-3 seat claimed `Fire
    Potion` off a reward screen; the tool answered `ok Claiming reward: potion
    (Fire Potion)`; the next combat listed three potions and `Fire Potion` was
    not among them. Three slots, four potions, "and no line on either screen
    saying the claim had failed or that a slot was full".

    BOTH NUMBERS ARE ON THE FEED -- `potions` holds the FILLED slots and
    `max_potion_slots` the count of them (`BuildPlayerState`) -- so the page
    can say what the game is about to do instead of reporting `ok` for
    something that did not happen. Refused rather than warned: an accepted
    claim that drops the potion spends an action and teaches the tester a
    board that is not there, which is the same defect one screen further on.

    NARROW ON PURPOSE. It fires only on a reward the wire TYPES as a potion,
    only where the wire sends a slot count at all, and only when the held
    count has reached it. Every other claim resolves exactly as before.
    """
    if not res.ok or not isinstance(res.post, dict):
        return None
    index = res.post.get("index")
    items = _reward_items(state)
    row = next((r for r in items
                if isinstance(r, dict) and r.get("index") == index), None)
    if row is None and isinstance(index, int) and 0 <= index < len(items):
        row = items[index] if isinstance(items[index], dict) else None
    if row is None or _fold(row.get("type")) != "potion":
        return None
    slots = _int(_player(state).get("max_potion_slots"), 0)
    held = len(_potions(state))
    if not slots or held < slots:
        return None
    # `EB-371`: the refusal names the way out. It used to say "use one first"
    # on a screen where a combat-only potion cannot be used, which left a seat
    # at three of three with nothing to do but leave the reward behind.
    return _refuse(
        f"your potion slots are full: {held} of {slots}, and this reward is a "
        f"potion. Drop one first (`drop potion 1`, or by name), use one if "
        f"you are in a fight, or leave this on the screen -- claiming it now "
        f"is how a potion disappears with the game saying nothing.")


# `EB-341`: what an ambiguous option refusal tells the tester to do instead.
# One sentence, and it names the handle the page prints beside those very rows.
ORDINAL_ADVICE = ("Say `choose <number>` for the row you want, counting from "
                  "the top of the list on this screen; the numbers are "
                  "printed beside the titles wherever two of them collide.")


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

    `EB-341`: the TEXT rides beside the name into `_match`, so two rows that
    print one title and do different things are told apart rather than
    collapsed onto the first -- and `cmd.ordinal` is the way out the refusal
    then advertises.
    """
    options = [namer(o) for o in entries]
    names = [o["name"] for o in options]
    if number:
        names = _number_names(names)
    rows = [{"n": n, "t": o.get("text") or ""}
            for n, o in zip(names, options)]
    idx, why = _match(rows, cmd.name, key=lambda e: e["n"],
                      face=lambda e: f"{e['n']}|{e['t']}",
                      ordinal=cmd.ordinal, advice=ORDINAL_ADVICE)
    if idx < 0:
        return _refuse(why)
    if not options[idx]["enabled"]:
        return _refuse(f"{names[idx]!r} is on the screen but not "
                       f"available to take")
    raw = entries[idx]
    posted = raw.get("index") if isinstance(raw, dict) else None
    # `EB-341`: the row's own body rides along so the line after the command
    # can say what the screen said this option does. Present only where the
    # row HAS a body -- an absent key is the page saying nothing, which is
    # what a row with no printed text leaves it able to say.
    printed = {"option": names[idx]}
    if options[idx].get("text"):
        printed["text"] = options[idx]["text"]
    # `EB-448`: and the faces of whatever the row names, so the result line
    # says WHAT was given rather than only that something was. Present only
    # where the namer supplies them, which today is the event screen alone.
    if options[idx].get("names"):
        printed["names"] = options[idx]["names"]
    return Resolution(True, "choose",
                      {"action": action,
                       "index": posted if isinstance(posted, int) else idx},
                      printed)


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
                      _bought(options[idx], price))


def _bought(option: dict[str, Any], price: Any) -> dict[str, Any]:
    """The shelf a `buy` took, printed (`EB-341`).

    Name and gold as before, plus the two fields that answer "what did I just
    buy" -- the shelf's CATEGORY (`_shelf_kind`: `potion`, `relic`,
    `card (skill)`) and its body. `Fysh Oil` was bought as a relic because the
    row printed like the relics beside it; the answer line now says `potion`
    at the moment of purchase rather than on the sold-out shelf afterwards.
    """
    printed: dict[str, Any] = {"item": option["name"], "price": price}
    for key in ("kind", "text"):
        if option.get(key):
            printed[key] = option[key]
    return printed


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

    `EB-319`: the verbs are no longer listed HERE. Every refusal ends in the
    forms that resolve now (`_with_forms`), and this sentence listing them a
    second time is the same list twice.
    """
    if obs["screen"] not in ("card_select", "bundle_select", "card_reward"):
        return "you are not in a battle"
    prompt = str(obs.get("prompt") or "").strip()
    return ("a card chooser is open and has to be answered first"
            + (f' — "{prompt}"' if prompt else ""))


def act(state: dict[str, Any], command: str) -> dict[str, Any]:
    """Resolve one player-language command against the CURRENT state.

    Returns the `Resolution` as a dict. It does NOT post -- the caller posts,
    so that the state a command was resolved against and the state it is sent
    to are provably the same frame.

    `EB-319`: every refusal that leaves here ends in the form(s) that resolve.
    This is the ONE funnel -- each `_refuse` above may name its own exact
    command and most do not need to, because the screen's own grammar is the
    honest fallback and it is applied here rather than at forty call sites.
    """
    try:
        cmd = parse_command(command)
    except BlindPlayError as exc:
        # A command that did not parse was typed against SOME screen, and that
        # screen's own grammar is exactly what the typist needed. `observation`
        # raises on a leak here for the same reason it does one line below: a
        # leak must never reach a tester, typo or no typo.
        return _with_forms(_refuse(str(exc)), observation(state)).as_dict()

    st = _screen(state)
    obs = observation(state)
    if obs["blocked"]:
        # No forms, deliberately: a screen that is not being driven has no
        # command that resolves, and `_with_forms` leaves the sentence alone.
        return _with_forms(
            _refuse(f"this screen is not being driven: {obs['blocked']}"),
            obs).as_dict()

    if cmd.verb == "play":
        res = (_play(state, cmd) if st in COMBAT_SCREENS
               else _refuse(_not_in_battle(obs)))
    elif cmd.verb == "use potion":
        res = _use_potion(state, cmd)
    elif cmd.verb == "drop potion":
        # `EB-371`: no screen list, deliberately. The wire's own gate on
        # `discard_potion` is "a run is in progress", which is the question
        # `obs["blocked"]` above has already answered for this page.
        res = _drop_potion(state, cmd)
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
    return _with_forms(res, obs).as_dict()


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
