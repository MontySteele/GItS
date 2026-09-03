"""One screen, design-blind, field by field.

Cut out of `blindplay.py` by `EB-180`: `observation` and nothing else,
which is the whole no-leak guarantee in one function. It assembles the
faces and the board into the structure the render prints, and it hands
the result to `qa_packet.assert_blind` -- so a leak raises here rather
than reaching a tester. Re-exported from `blindplay.py`.
"""
from __future__ import annotations

from typing import Any

from understudy import qa_packet
from understudy.blindplay_board import (_bundle_cards, _combat,
                                        _event_options, _map_ahead, _map_boss,
                                        _map_options, _preview_cards,
                                        _proceed_option, _relic_options,
                                        _rest_options, _reward_items,
                                        _screen_cards, _selected_bundle)
from understudy.blindplay_faces import (_card_face, _dedupe_text, _hazard,
                                        _named_option, _number_faces,
                                        _reward_option, _shop_options)
from understudy.blindplay_notes import keyword_notes
from understudy.blindplay_read import (_blob, _combat_torn_down, _despritify,
                                       _fold, _int, _player, _screen, _text)
from understudy.blindplay_shape import (COMBAT_SCREENS, PLAY_GUARDRAIL,
                                        SELECT_SCREENS, UNDRIVEN_SCREENS)


def observation(state: dict[str, Any]) -> dict[str, Any]:
    """One screen, design-blind, field by field. Raises `PacketLeak` on a leak.

    Returns a structure with a `blocked` string that is empty when the screen
    can be played and carries the reason when it cannot. Callers must check it:
    a blocked screen has no `commands`, and the driver stops rather than
    inventing one.
    """
    st = _screen(state)
    obs: dict[str, Any] = {
        "state_type": st,
        "guardrail": PLAY_GUARDRAIL,
        "blocked": "",
        "screen": "",
        "commands": [],
    }
    hazard = _hazard(state)

    if hazard is not None:
        obs["screen"] = "hazard"
        obs["blocked"] = hazard[1]
    elif st in UNDRIVEN_SCREENS:
        obs["screen"] = "undriven"
        obs["blocked"] = UNDRIVEN_SCREENS[st]
    elif st in COMBAT_SCREENS and _combat_torn_down(state):
        # `EB-178`, belt and braces. `settle` rides this out in well under a
        # second, but a wire that got STUCK here must be reported as stuck --
        # the one thing it must never do is render `Battle -- round 0` with an
        # empty hand, which is the fight-that-never-was run B6 recorded twice.
        obs["screen"] = "combat"
        obs["blocked"] = ("the fight is over and the game has not put up the "
                          "next screen; nothing here can be played")
    elif st in COMBAT_SCREENS:
        obs["screen"] = "combat"
        obs["combat"] = _combat(state)
        obs["commands"] = ['play "<card title>" [on "<enemy>"]',
                           'use potion "<potion>" [on "<enemy>"]',
                           "end turn"]
        # `EB-216`, the Kokomi draft-6 half. The jellyfish is a TARGET, and
        # naming it is how a Plan is written -- so the grammar has to say so
        # on the screen where it can be used, and only there. A board with no
        # pet never sees this line.
        plans = obs["combat"].get("plans")
        if plans and plans.get("pet"):
            obs["commands"].insert(
                1, f'play "<card title>" on "{plans["pet_name"]}"'
                   "   (writes its Plan instead of playing it now)")
    elif st == "map":
        obs["screen"] = "map"
        obs["nodes"] = _map_options(state)
        # `EB-298`: the floors ahead and the boss, both already on the feed.
        obs["ahead"] = _map_ahead(state)
        obs["boss"] = _map_boss(state)
        obs["commands"] = ['go "<node>"']
    elif st == "card_reward":
        blob = _blob(state, "card_reward")
        obs["screen"] = "card_reward"
        obs["prompt"] = _text(blob.get("prompt")) or "Add a card to your deck."
        obs["offers"] = _number_faces(
            [_card_face(c) for c in _screen_cards(state)], "title")
        obs["can_skip"] = blob.get("can_skip") is not False
        obs["commands"] = ['choose "<card title>"', "skip"]
    elif st in SELECT_SCREENS:
        blob = _blob(state, st)
        obs["screen"] = "card_select"
        obs["prompt"] = _text(blob.get("prompt")) or "Choose a card."
        obs["offers"] = _number_faces(
            [_card_face(c) for c in _screen_cards(state)], "title")
        # `EB-263`. WHAT THE SCREEN SAYS IS PICKED. Two channels now, and the
        # older one first: `BuildCardSelectState` puts the chosen card(s) in
        # `preview_cards` while a preview container is open, which the upgrade
        # and transform screens open and -- since this row's bridge half --
        # the enchant picker does too, under its own two container names.
        #
        # The second channel is the GRID's own selection, `selected` per card,
        # read off `NCardGrid._highlightedCards`: the one list all five
        # selection screens write through, so a pick is legible the moment it
        # lands and not only once a preview opens over it. `selection_known`
        # is whether the bridge could ask at all; where it could not, the page
        # says so (`SELECTION_NOTE`) rather than printing "nothing is picked".
        #
        # `EB-314`. A PREVIEW IS NOT ALWAYS A RESULT, and on the transform
        # screen it is half a snapshot and half a slot machine. The screen is
        # named on the wire (`screen_type`) and whether its preview is up
        # (`preview_showing`), and both are needed below: what the preview
        # holds means different things on a transform screen than on the
        # other four, and a pick that is already made may not be re-taken.
        obs["select_kind"] = _text(blob.get("screen_type"))
        obs["preview_showing"] = bool(blob.get("preview_showing"))
        picked = [_card_face(c) for c in _preview_cards(state, st)]
        # How many results the transform screen has NOT chosen yet, and
        # whether its preview came through in a shape this page can read at
        # all. Zero and False on every other screen, whose preview is the
        # decided thing it looks like.
        obs["undecided"] = 0
        obs["preview_unnamed"] = False
        if obs["select_kind"] == "transform" and picked:
            half, odd = divmod(len(picked), 2)
            if odd or not half:
                picked, obs["preview_unnamed"] = [], True
            else:
                picked, obs["undecided"] = picked[:half], half
        obs["selected"] = _number_faces(picked, "title")
        obs["selection_known"] = bool(blob.get("selection_known"))
        if not obs["selected"] and obs["selection_known"] \
                and not obs["preview_unnamed"]:
            obs["selected"] = [c for c in obs["offers"] if c.get("selected")]
        obs["can_confirm"] = bool(blob.get("can_confirm"))
        obs["can_skip"] = bool(blob.get("can_skip") or blob.get("can_cancel"))
        # `EB-259`. THE PAGE MAY NOT OFFER WHAT THE STATE WILL REFUSE. This
        # screen said *Confirm is not available* in its body and listed
        # `confirm` under "What you can say" three lines later; the tester
        # typed it, the screen had already advanced on its own, and the
        # command came back *"there is nothing waiting to be confirmed"*. The
        # wire answers the question outright (`can_confirm` /
        # `can_cancel`, `McpMod.StateBuilder.cs:2065`), so the grammar offered
        # is the grammar the wire says will work -- and `_confirm` / `_skip`
        # still refuse on their own, because a screen can move between the
        # render and the command.
        #
        # `EB-314`'s half of the same rule: ONCE THE PREVIEW IS UP THE PICK IS
        # MADE, and naming another card is not a way to change it -- see
        # `_choose`. The verb is not offered where it does not work.
        obs["commands"] = ([] if obs["preview_showing"]
                           else ['choose "<card title>"'])
        if obs["can_confirm"]:
            obs["commands"].append("confirm")
        if obs["can_skip"]:
            obs["commands"].append("skip")
    elif st == "bundle_select":
        # `EB-173`: A BUNDLE HAS NO NAME, and asking for one printed
        # `- **(unnamed)**` twice, on a screen whose only verb is
        # `choose "<bundle>"`. Nothing on it could be named, `confirm` before a
        # selection is an error the game just repeats, and a live session sat
        # there answering `confirm` until its action budget ran out. The wire
        # gives each bundle an index and a LIST OF CARDS; the cards have
        # printed titles, so the bundle is named by what is in it -- which is
        # also how a player at the screen would say it out loud. No id and no
        # invented label: every word below is one the game printed.
        blob = _blob(state, "bundle_select")
        obs["screen"] = "bundle_select"
        obs["prompt"] = _text(blob.get("prompt")) or "Choose a bundle."
        bundles = _screen_cards(state)
        obs["offers"] = [{"cards": [_card_face(c) for c in _bundle_cards(b)]}
                         for b in bundles]
        # `EB-294`. THE SCREEN NEVER SAID WHICH BUNDLE WAS ARMED. `choose`
        # answered `ok Selecting bundle 0` and the re-render was the same page
        # with no mark on either offer: "I had to send `confirm` on faith that
        # the right one was armed" (r2 Opus seat). The wire does answer --
        # `BuildBundleSelectState` fills `preview_cards` from the preview
        # container the moment a bundle is picked -- so the pick is found by
        # matching those printed titles against each bundle's own, and the
        # render marks it. `can_confirm` is the CONFIRM BUTTON's own state
        # where the wire sends it, with `preview_showing` behind it for a
        # state saved before that key was read.
        obs["selected"] = _selected_bundle(bundles, _preview_cards(
            state, "bundle_select"))
        obs["can_confirm"] = bool(blob.get("can_confirm")
                                  if blob.get("can_confirm") is not None
                                  else blob.get("preview_showing"))
        obs["preview_showing"] = bool(blob.get("preview_showing"))
        obs["commands"] = ['choose "<any card title in the bundle you want>"',
                           "confirm"]
    elif st in ("shop", "fake_merchant"):
        obs["screen"] = "shop"
        obs["gold"] = _int(_player(state).get("gold"))
        obs["items"] = _shop_options(state)
        obs["commands"] = ['buy "<item>"', "proceed"]
    elif st == "rest_site":
        obs["screen"] = "rest_site"
        obs["options"] = [_named_option(o) for o in _rest_options(state)]
        obs["hp"] = _int(_player(state).get("hp"))
        obs["max_hp"] = _int(_player(state).get("max_hp"))
        # `EB-263`. THE VERBS WERE A CONSTANT. A SPENT rest site sends an
        # empty `options` list -- the room drops them once one is taken -- and
        # this screen still printed `choose "<option>"`, `rest`, `upgrade` and
        # `remove` over nothing at all: "Four verbs and nothing to choose"
        # (r3 Opus seat). Each verb is now offered only when an ENABLED option
        # answers to it, by the same keyword match `_rest_keyword` resolves
        # with, so the grammar on the page is the grammar the screen will
        # take. `proceed` is always last and always there: it is the one
        # button a rest site has whatever else it has.
        obs["commands"] = []
        live = [o for o in obs["options"] if o["enabled"]]
        if live:
            obs["commands"].append('choose "<option>"')
        for verb, words in (("rest", ("rest", "sleep", "heal")),
                            ("upgrade", ("upgrade", "smith", "forge")),
                            ("remove", ("remove", "purge", "toss"))):
            if any(any(w in _fold(o["name"]) for w in words) for o in live):
                obs["commands"].append(verb)
        # A FRESH rest site sends `can_proceed: false` -- the room will not let
        # you leave until its one choice is taken -- and a SPENT one sends
        # `true` with an empty option list. Captured live, both of them
        # (`review/qa/blindplay/eb263-live-shapes/`). The fallback is the
        # safety rail: a screen this tool can say nothing at all about is worse
        # than a verb that might be refused.
        if _blob(state, "rest_site").get("can_proceed") is not False                 or not obs["commands"]:
            obs["commands"].append("proceed")
    elif st == "event":
        ev = _blob(state, "event")
        obs["screen"] = "event"
        obs["title"] = _text(ev.get("event_name"))
        obs["text"] = _text(ev.get("body") or ev.get("text")
                            or ev.get("description"))
        obs["in_dialogue"] = bool(ev.get("in_dialogue"))
        obs["options"] = [_named_option(o) for o in _event_options(state)]
        # `EB-259`, the other half. An event room has NO proceed button --
        # `ExecuteProceed` walks rewards, rest, both merchants and the
        # treasure room and stops (`McpMod.Actions.cs:600-663`) -- so a bare
        # `proceed` here posted an action the game answered *"No proceed
        # button available or enabled"*, and a run lost two actions to it. The
        # verb is still offered, because an event whose only button reads
        # *Proceed* is exactly where a player would type it; `_proceed`
        # resolves it to THAT PRINTED OPTION instead of the proceed action.
        obs["commands"] = ['choose "<option>"']
        if obs["in_dialogue"] or _proceed_option(state) >= 0:
            obs["commands"].append("proceed")
    elif st == "rewards":
        obs["screen"] = "rewards"
        # `EB-290`: named by what each row hands over, and the repeats
        # numbered the way every other list on this page is numbered. Two
        # rewards that print one name -- the run that met `12 Gold` and
        # `40 Gold (stolen back)` -- were both called `Gold`, the documented
        # `Gold (1)` was refused, and the tester could only take them one at a
        # time by naming the pair and trusting which one came first.
        obs["items"] = _number_faces(
            [_dedupe_text(_reward_option(r)) for r in _reward_items(state)],
            "name")
        # `EB-294`. THE VERB WAS A CONSTANT HERE TOO. Once both rewards were
        # taken the page printed `- (nothing here to take)` and still offered
        # `choose "<reward>"` under "What you can say", which is the same
        # defect `EB-263` closed one screen over on a spent rest site.
        obs["commands"] = []
        if any(i["enabled"] for i in obs["items"]):
            obs["commands"].append('choose "<reward>"')
        obs["commands"].append("proceed")
    elif st in ("treasure", "relic_select"):
        obs["screen"] = st
        obs["items"] = [_named_option(r) for r in _relic_options(state)]
        # `EB-263`, the chest half. `BuildTreasureState` writes `relics` ONLY
        # while the relic collection is on screen, and writes a `message`
        # instead while the chest is still opening or the room is still
        # loading (`McpMod.StateBuilder.cs:2381-2399`). The page had a reader
        # for neither case, so an empty chest rendered as `# An open chest`
        # with a blank body while still advertising `choose "<relic>"`: "I
        # never saw whether the chest contained anything or whether I received
        # it" (r3 Opus seat). The message is the feed's own sentence, printed
        # verbatim, and the verb is offered only when there is something to
        # aim it at.
        obs["message"] = _text(_blob(state, st).get("message"))
        obs["commands"] = []
        if any(i["enabled"] for i in obs["items"]):
            obs["commands"].append('choose "<relic>"')
        obs["commands"].append("skip" if st == "relic_select" else "proceed")
    elif st == "game_over":
        blob = _blob(state, "game_over")
        obs["screen"] = "game_over"
        obs["result"] = _text(blob.get("result") or blob.get("outcome"))
        obs["floor"] = _int(_blob(state, "run").get("floor"))
        obs["blocked"] = "the run is over; there is nothing left to play"
    elif st == "menu":
        obs["screen"] = "menu"
        obs["blocked"] = ("this is a menu, not a play screen. Start the run "
                          "before handing the seat the controls.")
    else:
        obs["screen"] = "unknown"
        obs["blocked"] = "this tool has never seen this screen"

    # Sprite tags are rewritten HERE, at the boundary, rather than in each of
    # the dozen readers that could carry one: the wire prints them in card
    # faces, relic faces, keyword bodies, event options and intent labels
    # alike, and a rule applied in one reader is a rule that will be missing
    # from the next one somebody adds.
    obs = _despritify(obs)

    # `EB-272`: computed over the FINISHED structure, at the same boundary and
    # for the same reason the sprite tags are rewritten there -- every screen
    # gets the rule, and a reader added tomorrow gets it for free. After the
    # sprite pass, so a word inside a rewritten icon tag is read as it prints.
    obs["keywords"] = keyword_notes(obs)

    # The wire's own screen name is the ONE token exempted from the snake_case
    # rule, and only because a refusal has to be able to name what it refused.
    #
    # `EB-176`, FOUND LIVE. BOTH names are exempt, because there are two and
    # they are not always the same string: `st` is what the WIRE called the
    # screen, `obs["screen"]` is what this tool calls it, and the branches
    # above deliberately fold several wire names onto one tool name --
    # `hand_select` renders as `card_select`. Exempting only `st` meant a live
    # `hand_select` wrote the un-exempt token `card_select` into its own
    # observation and the blindness assertion killed the session on a screen
    # that had leaked nothing. Both are screen vocabulary: neither names a
    # card, a role or a ruling, which is the test the exemption exists for.
    qa_packet.assert_blind(obs, allow={st, obs["screen"]})
    return obs
