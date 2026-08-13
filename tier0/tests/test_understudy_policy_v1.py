"""R93's seven revisions, made executable.

Every test below is a Phase-0 observation turned into a red-if-regressed
assertion. The boards are the boards the report describes -- the floor-7
39-incoming-against-4-Block case is not invented, it is the row that got
revision #2 approved.

Why these run offline: policy_v1 is a pure function of a wire-state dict plus
its Memo. The bridge is not involved, no game is launched, and a synthetic
state is a legitimate fixture precisely because the adapter's job is to make
one indistinguishable from a real one.
"""

import pytest

from tier0 import constants as C
from understudy import naming, policy_v1
from tier05 import route as t5route


def _combat_state(hand, enemies, hp=39, potions=(), rnd=1, floor=7):
    return {
        "state_type": "monster",
        "run": {"act": 1, "floor": floor},
        "battle": {"round": rnd, "enemies": list(enemies)},
        "player": {
            "hp": hp, "max_hp": 71, "block": 0, "energy": 3, "gold": 0,
            "status": [], "potions": list(potions), "hand": list(hand),
            "draw_pile": [], "discard_pile": [], "exhaust_pile": [],
        },
    }


def _enemy(eid, name, hp, label, max_hp=None, aura=None):
    return {"entity_id": eid, "name": name, "hp": hp,
            "max_hp": max_hp or hp, "block": 0,
            "intents": [{"type": "Attack", "label": label}],
            "status": ([{"name": aura}] if aura else [])}


ETHEREAL = {"id": "KLEEMOD-ETHEREAL_SPOTLIGHT", "name": "Ethereal Spotlight",
            "cost": 0, "type": "Skill", "target_type": "Self", "can_play": True,
            "keywords": [{"name": "Ethereal", "description": "Vanishes."}],
            "description": "Choose Center Stage or Guest Cast."}
DEFEND = {"id": "BASE-DEFEND", "name": "Defend", "cost": 1, "type": "Skill",
          "target_type": "Self", "can_play": True,
          "description": "Gain 4 Block."}
BIG_SWING = {"id": "BASE-SWING", "name": "Big Swing", "cost": 2,
             "type": "Attack", "target_type": "Enemy", "can_play": True,
             "description": "Deal 25 damage."}


# ------------------------------------------------- #1 free expiring first ---

def test_free_expiring_card_is_played_before_anything_is_scored():
    """The single largest contributor to Phase-0's 34-of-47 turn-opener gap.

    The board is deliberately one where the block-panic rung WOULD fire, which
    is exactly the situation policy_v0 opened with a blocker in.
    """
    state = _combat_state([ETHEREAL, DEFEND, BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 25, "39")])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.1"
    assert d.action == {"action": "play_card", "card_index": 0}
    assert d.notes["names"]["card_name"] == "Ethereal Spotlight"


def test_a_non_expiring_zero_cost_card_gets_no_privilege():
    free_but_permanent = dict(ETHEREAL, keywords=[], description="Gain 1 Block.")
    state = _combat_state([free_but_permanent, BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 60, "5")])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision != "v1.1", "revision #1 is about EXPIRY, not about cost 0"


def test_the_free_card_arm_cannot_spin():
    """A play that does not remove the card is the one loop shape #1 has.

    The state never changes between calls here -- which is precisely what a
    rejected play looks like -- and the arm must stop offering it.
    """
    state = _combat_state([ETHEREAL, BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 60, "5")])
    memo = policy_v1.Memo()
    first = policy_v1.decide(state, memo)
    second = policy_v1.decide(state, memo)
    assert first.revision == "v1.1"
    assert second.revision != "v1.1"


# ------------------------------------ #2 block-panic gate and the kill line --

def test_the_panic_rung_still_fires_when_the_block_can_actually_matter():
    big_block = dict(DEFEND, name="Real Block", description="Gain 18 Block.")
    state = _combat_state([big_block, BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 60, "20")], hp=30)
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.2-panic"
    assert d.notes["gate"]["panic_condition"] is True
    assert d.notes["names"]["card_name"] == "Real Block"


def test_killing_the_body_beats_buying_four_block_against_thirty_nine():
    """Phase-0, floor 7. 39 incoming, a 4-Block card, a 25 HP enemy that
    exactly 25 damage in hand kills. policy_v0 asked for the 4 Block on five
    consecutive comparisons."""
    state = _combat_state(
        [DEFEND, BIG_SWING],
        [_enemy("JAW_0", "Jaxfruit", 25, "15"),
         _enemy("FLY_1", "Flyconid", 48, "8 x 3")])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.2-kill"
    assert d.action["card_index"] == 1
    assert d.action["target"] == "JAW_0", "the kill line aims at the body it kills"
    gate = d.notes["gate"]
    assert gate["kill_removes"] == 15
    assert gate["prevented"] == 4.0


def test_a_block_that_cannot_dent_the_incoming_falls_through_to_scoring():
    """Same board with no kill available: the panic is gated, and the decision
    goes to the sim's own scorer rather than to a token 4 Block."""
    state = _combat_state(
        [DEFEND, BIG_SWING],
        [_enemy("JAW_0", "Jaxfruit", 40, "15"),
         _enemy("FLY_1", "Flyconid", 48, "8 x 3")])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.2"
    assert d.notes["gate"]["outcome"] == "gated_to_scoring"
    assert d.notes["gate"]["panic_condition"] is True


def test_the_gate_bar_is_a_bot_dial_and_not_a_balance_constant():
    """If this ever moves into tier0/constants.py it is a sim change wearing a
    harness's clothes."""
    assert not hasattr(C, "BLOCK_MATTERS_FRACTION")
    assert 0.0 < policy_v1.BLOCK_MATTERS_FRACTION <= 1.0


# --------------------------------------------------- #3 map, two plies -------

def _map_state(options, hp=60, floor=6):
    return {"state_type": "map", "run": {"act": 1, "floor": floor},
            "player": {"hp": hp, "max_hp": 71, "gold": 100,
                       "deck": [{"id": "KLEEMOD-STAGE_PRESENCE"}]},
            "map": {"next_options": options}}


def test_the_map_arm_takes_the_node_whose_successor_is_better():
    """Two identical Monster nodes; one leads to an Elite. policy_v0 saw a tie
    and broke it on index, which is two of Phase-0's three path differences."""
    state = _map_state([
        {"index": 0, "type": "Monster", "leads_to": [{"type": "Monster"}]},
        {"index": 1, "type": "Monster", "leads_to": [{"type": "Elite"}]}])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.3"
    assert d.action == {"action": "choose_map_node", "index": 1}
    assert d.notes["plies"] == 2


def test_the_lookahead_is_undiscounted_because_route_plan_is():
    """`tier05.route._plan` sums room values along a path with no discount
    factor. Inventing one here would make this a different policy rather than
    a shallower one, so the sum is asserted arithmetically."""
    state = _map_state([
        {"index": 0, "type": "Elite", "leads_to": [{"type": "Monster"}]},
        {"index": 1, "type": "Monster", "leads_to": [{"type": "Elite"}]}])
    d = policy_v1.decide(state, policy_v1.Memo())
    # elite 10 + normal 2 == normal 2 + elite 10; the tie breaks on index.
    assert d.action["index"] == 0


def test_a_node_with_no_lookahead_still_scores():
    state = _map_state([{"index": 0, "type": "Monster"}])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.action == {"action": "choose_map_node", "index": 0}
    assert d.notes["leads_to"] == []


# ------------------------------------------------- #4 the potion arm --------

def test_the_potion_arm_delegates_to_the_sims_own_ladder():
    state = _combat_state(
        [BIG_SWING], [_enemy("JAW_0", "Jaxfruit", 60, "35")], hp=30,
        potions=[{"id": "block_potion", "name": "Block Potion"}])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.4"
    assert d.action == {"action": "use_potion", "slot": 0}
    assert d.notes["names"]["potion_name"] == "Block Potion"


def test_the_potion_arm_fires_once_per_round_not_once_per_play():
    """`try_use_potions` sits at turn start in the sim. Without the memo it
    would be re-offered before every card in the turn."""
    state = _combat_state(
        [BIG_SWING], [_enemy("JAW_0", "Jaxfruit", 60, "35")], hp=30,
        potions=[{"id": "block_potion", "name": "Block Potion"}])
    memo = policy_v1.Memo()
    assert policy_v1.decide(state, memo).revision == "v1.4"
    assert policy_v1.decide(state, memo).revision != "v1.4"


def test_a_potion_the_sim_does_not_know_is_recorded_not_guessed():
    state = _combat_state(
        [BIG_SWING], [_enemy("JAW_0", "Jaxfruit", 60, "35")], hp=30,
        potions=[{"id": "SOME_BASE_GAME_POTION", "name": "Mystery Brew"}])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision != "v1.4", "an unknown potion is not drunk on a guess"


def test_a_full_hp_player_is_not_made_to_drink():
    state = _combat_state(
        [BIG_SWING], [_enemy("JAW_0", "Jaxfruit", 60, "2")], hp=71,
        potions=[{"id": "block_potion", "name": "Block Potion"}])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision != "v1.4"


# ------------------------------------------- #5 next_fight into the rest ----

def _rest_state(hp=52):
    return {"state_type": "rest_site", "run": {"act": 1, "floor": 7},
            "player": {"hp": hp, "max_hp": 71,
                       "deck": [{"id": "KLEEMOD-STAGE_PRESENCE"},
                                {"id": "KLEEMOD-SOLOISTS_SOLICITATION"}]},
            "rest_site": {"options": [{"index": 0, "name": "Rest"},
                                      {"index": 1, "name": "Smith"}]}}


def test_an_elite_after_the_rest_changes_the_rest_answer():
    """Phase-0's one rest divergence: `next_fight` was hard-coded False
    "because we did not look, not because we know"."""
    with_elite = policy_v1.Memo()
    with_elite.next_node_kinds = [t5route.ELITE]
    without = policy_v1.Memo()
    without.next_node_kinds = [t5route.NORMAL]
    a = policy_v1.decide(_rest_state(), with_elite)
    b = policy_v1.decide(_rest_state(), without)
    assert a.notes["next_fight"] is True
    assert b.notes["next_fight"] is False
    assert a.label != b.label, "the flag has to actually move the answer"


def test_the_map_arm_feeds_the_rest_arm():
    """The wiring, not the rule: the memo is filled by revision #3 and read by
    revision #5, and nothing else connects them."""
    memo = policy_v1.Memo()
    policy_v1.decide(_map_state(
        [{"index": 0, "type": "Monster", "leads_to": [{"type": "Elite"}]}]),
        memo)
    assert memo.next_node_kinds == [t5route.ELITE]
    assert policy_v1.decide(_rest_state(), memo).notes["next_fight"] is True


# -------------------------------------- #6 the in-combat choice overlay -----

def _overlay(deck_ids, options=("Center Stage", "Guest Cast")):
    return {"state_type": "card_select", "run": {"act": 1, "floor": 3},
            "player": {"hp": 50, "max_hp": 71, "hand": [],
                       "draw_pile": [{"id": i} for i in deck_ids],
                       "discard_pile": [], "exhaust_pile": []},
            "card_select": {"screen_type": "choose", "cards": [
                {"id": f"KLEEMOD-{n.upper().replace(' ', '_')}_OPTION",
                 "name": n, "cost": 0} for n in options]}}


def test_a_companion_light_deck_takes_center_stage():
    state = _overlay(["KLEEMOD-STAGE_PRESENCE"] * 10)
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.6"
    assert d.notes["basis"] == "companion_density"
    assert d.notes["names"]["card_name"] == "Center Stage"


def test_a_companion_heavy_deck_takes_guest_cast():
    from tier0.content import loader
    companion = next(
        (c.id for c in loader._card_index().values()
         if (c.companion is not None or bool(c.nation))), None)
    if companion is None:
        pytest.skip("no companion row on any sheet to build the deck from")
    ids = [f"KLEEMOD-{companion.upper()}"] * 5 + ["KLEEMOD-STAGE_PRESENCE"] * 5
    d = policy_v1.decide(_overlay(ids), policy_v1.Memo())
    assert d.notes["companion_share"] >= policy_v1.COMPANION_SHARE_FOR_GUEST_CAST
    assert d.notes["names"]["card_name"] == "Guest Cast"


def test_policy_v0_declined_this_screen_and_that_is_the_regression():
    """The point of revision #6 stated as a test: the counterfactual arm
    returns nothing here, which is honest for a measurement and useless for a
    driver."""
    from understudy import policy_v0
    assert policy_v0.counterfactual(
        _overlay(["KLEEMOD-STAGE_PRESENCE"])).available is False
    assert policy_v1.decide(
        _overlay(["KLEEMOD-STAGE_PRESENCE"]), policy_v1.Memo()).available is True


def test_a_deck_management_overlay_still_goes_to_the_sims_smith_order():
    """Revision #6 must not swallow the upgrade/remove screens policy_v0
    already answers by delegation."""
    state = _overlay(["KLEEMOD-STAGE_PRESENCE"])
    state["card_select"]["screen_type"] = "upgrade"
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v0"


# --------------------------------------------- #7 the names, the blocker ----

def test_every_emitted_action_carries_resolved_names():
    """The P1 blocker. `{"action": "play_card", "card_index": 2}` is a complete
    instruction and a useless dataset row."""
    boards = [
        _combat_state([ETHEREAL, BIG_SWING],
                      [_enemy("JAW_0", "Jaxfruit", 60, "5")]),
        _map_state([{"index": 0, "type": "Monster"}]),
        _rest_state(),
        _overlay(["KLEEMOD-STAGE_PRESENCE"]),
    ]
    for state in boards:
        d = policy_v1.decide(state, policy_v1.Memo())
        if d.action is None:
            continue
        names = d.notes.get("names")
        assert names, f"no names on a {state['state_type']} action"
        assert names["verb"] == d.action["action"]
        assert names["state_type"] == state["state_type"]


def test_a_play_names_the_card_and_the_enemy():
    state = _combat_state([BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 60, "5"),
                           _enemy("FLY_1", "Flyconid", 20, "5")])
    d = policy_v1.decide(state, policy_v1.Memo())
    names = d.notes["names"]
    assert names["card_name"] == "Big Swing"
    assert names["target_name"] == "Flyconid"
    assert names["target_hp"] == 20


def test_naming_never_raises_and_says_so_when_it_fails():
    out = naming.describe({"player": None}, {"action": "play_card",
                                             "card_index": 99})
    assert isinstance(out, dict)


def test_the_hand_is_logged_by_name_as_the_divergence_denominator():
    state = _combat_state([ETHEREAL, DEFEND],
                          [_enemy("JAW_0", "Jaxfruit", 60, "5")])
    assert naming.hand_names(state) == ["Ethereal Spotlight", "Defend"]


# ----------------------------------------------------- shape and scope ------

def test_policy_v1_never_ends_a_run_by_raising():
    """The run is the expensive half. Every arm is wrapped, and a garbage
    state must produce a Decision rather than a traceback."""
    for junk in ({}, {"state_type": "monster"}, {"state_type": "map"},
                 {"state_type": "rest_site"}, {"state_type": "card_select"},
                 {"state_type": "banana", "player": {"hand": "not a list"}}):
        d = policy_v1.decide(junk, policy_v1.Memo())
        assert isinstance(d, policy_v1.Decision)


def test_the_same_state_gives_the_same_answer():
    """Determinism: every arm sorts, none rolls. Two runs disagreeing has to be
    a fact about the runs."""
    state = _combat_state([DEFEND, BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 25, "15"),
                           _enemy("FLY_1", "Flyconid", 48, "8 x 3")])
    a = policy_v1.decide(state, policy_v1.Memo())
    b = policy_v1.decide(state, policy_v1.Memo())
    assert a.action == b.action and a.revision == b.revision


def test_policy_v0_is_frozen_by_this_sprint():
    """policy_v0 is one arm of a published measurement. policy_v1 must be a
    NEW module rather than an edit, and the counterfactual arm's own answers
    must be unchanged."""
    from understudy import policy_v0
    state = _combat_state([ETHEREAL, DEFEND, BIG_SWING],
                          [_enemy("JAW_0", "Jaxfruit", 25, "39")])
    cf = policy_v0.counterfactual(state)
    assert cf.category == "sequencing"
    # The Phase-0 behaviour, still exactly as measured: a 0-cost expiring card
    # has NO privileged status in the counterfactual arm's ladder. That is the
    # divergence revision #1 exists to close, and policy_v0 must keep showing
    # it or the measurement it belongs to stops being reproducible.
    assert cf.action["card_index"] != 0


# ------------------------------- the card_select screens, learned live ------
#
# `card_select` is three screens wearing one name, and the first validation
# soak stalled on the difference. Both rows below are that stall, made red.


def _grid(prompt, screen_type="select", can_confirm=False, preview=False):
    return {"state_type": "card_select", "run": {"act": 1, "floor": 5},
            "player": {"hp": 42, "max_hp": 71, "hand": [],
                       "draw_pile": [{"id": "KLEEMOD-SALON_DEBUT"},
                                     {"id": "KLEEMOD-STAGE_PRESENCE"}],
                       "discard_pile": [], "exhaust_pile": []},
            "card_select": {"screen_type": screen_type, "prompt": prompt,
                            "can_confirm": can_confirm,
                            "preview_showing": preview,
                            "cards": [
                                {"id": "KLEEMOD-SALON_DEBUT",
                                 "name": "Salon Debut", "cost": 1, "index": 0},
                                {"id": "KLEEMOD-STAGE_PRESENCE",
                                 "name": "Stage Presence", "cost": 1,
                                 "index": 1}]}}


def test_a_registered_selection_is_confirmed_not_toggled_again():
    """The live stall: `select_card` TOGGLES on a grid screen, so re-issuing it
    deselects. Twelve of those in a row is what the watchdog saw."""
    d = policy_v1.decide(_grid("Choose a card to Remove.", can_confirm=True,
                               preview=True), policy_v1.Memo())
    assert d.action == {"action": "confirm_selection"}
    assert d.notes["basis"] == "grid_confirm"


def test_the_screen_kind_is_read_off_the_prompt_when_the_type_says_nothing():
    """The shop's removal service reports `screen_type: "select"` and
    `prompt: "Choose a card to Remove."`. Keying on the type alone sent it to
    the generic fallback, which scores with `score_offer` and would therefore
    have removed the deck's BEST card."""
    assert policy_v1._screen_kind(
        {"screen_type": "select", "prompt": "Choose a card to Remove."}) == "remove"
    assert policy_v1._screen_kind(
        {"screen_type": "select", "prompt": "Choose a card to Upgrade."}) == "upgrade"
    assert policy_v1._screen_kind(
        {"screen_type": "choose", "prompt": "Choose one."}) == ""


def test_a_prompt_derived_remove_screen_reaches_the_sims_ladder():
    d = policy_v1.decide(_grid("Choose a card to Remove."), policy_v1.Memo())
    assert d.notes.get("screen_kind_from") == "prompt" or \
        d.notes.get("screen_kind") == "remove"


def test_a_committed_remove_screen_is_answered_and_never_cancelled():
    """The fourth validation soak's loop. `rest_action`'s on-plan-upgrade rung
    outranks its thin rung, so on a remove screen the sim's ladder routinely
    wants to upgrade and policy_v0 declines. At a rest site cancelling costs
    nothing; at a shop's removal service the gold is already spent, and the run
    bounced shop -> card_select -> shop until the watchdog stopped it."""
    d = policy_v1.decide(_grid("Choose a card to Remove."), policy_v1.Memo())
    assert d.available, "a paid-for screen must never be answered with a shrug"
    assert d.action["action"] == "select_card"
    if d.notes.get("basis"):
        assert d.notes["basis"] == "score_offer_inverse"
        scores = d.notes["scores"]
        chosen = d.notes["names"]["card_name"]
        assert scores[chosen] == min(scores.values()), \
            "a remove screen takes the card the drafter would least want"


def test_the_shop_arm_does_not_buy_an_untyped_item():
    """It bought the card-REMOVAL service, which arrives with no `type`, and
    then could not follow through. Buying a service the bot cannot complete is
    not a judgment call it is entitled to make."""
    state = {"state_type": "shop", "run": {"act": 1, "floor": 3},
             "player": {"hp": 50, "max_hp": 71, "gold": 400,
                        "deck": [{"id": "KLEEMOD-STAGE_PRESENCE"}]},
             "items": [{"name": "Card Removal", "price": 75},
                       {"name": "Aria of Recompense", "type": "card",
                        "id": "KLEEMOD-ARIA_OF_RECOMPENSE", "price": 50}]}
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.notes["untyped_items_skipped"] == ["Card Removal"]
    if d.action.get("action") == "shop_purchase":
        assert d.notes["names"]["item_name"] != "Card Removal"


def test_a_named_spotlight_overlay_is_still_the_spotlight_arm():
    """The prompt reader must not swallow the screen revision #6 owns."""
    state = _overlay(["KLEEMOD-STAGE_PRESENCE"])
    state["card_select"]["prompt"] = "Choose one."
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.revision == "v1.6"
    assert d.notes["basis"] == "companion_density"


def test_an_enchant_screen_confirms_on_the_second_visit():
    """`NDeckEnchantSelectScreen` reports `can_confirm: true` with
    `preview_showing: false`, so the preview flag alone is not evidence that a
    selection landed. Without the memo the driver re-toggled the same card
    until the cycle watchdog stopped the run."""
    state = _grid("Choose a card to Enchant.",
                  screen_type="NDeckEnchantSelectScreen", can_confirm=True)
    memo = policy_v1.Memo()
    first = policy_v1.decide(state, memo)
    assert first.action["action"] == "select_card"
    second = policy_v1.decide(state, memo)
    assert second.action == {"action": "confirm_selection"}
    assert second.notes["registered_by"] == "prior_selection"


def test_the_confirm_is_not_offered_before_anything_is_selected():
    """A screen that reports can_confirm on arrival must not be confirmed
    blind -- that would pick whatever the game had highlighted."""
    state = _grid("Choose a card to Enchant.",
                  screen_type="NDeckEnchantSelectScreen", can_confirm=True)
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.action["action"] == "select_card"


def test_a_multi_select_screen_picks_a_different_card_each_visit():
    """"Choose 2 Common Cards to Add to Your Deck" (`simple_select`) keeps
    `can_confirm` false until the quota is met. An arm that re-picks its single
    best option toggles the same card on and off forever, which is what the
    sixth validation soak did until the cycle watchdog stopped it."""
    state = {"state_type": "card_select", "run": {"act": 1, "floor": 6},
             "player": {"hp": 49, "max_hp": 71, "hand": [],
                        "draw_pile": [{"id": "KLEEMOD-STAGE_PRESENCE"}],
                        "discard_pile": [], "exhaust_pile": []},
             "card_select": {"screen_type": "simple_select",
                             "prompt": "Choose 2 Common Cards to Add to Your Deck.",
                             "can_confirm": False, "preview_showing": False,
                             "cards": [
                                 {"id": "KLEEMOD-ARIA_OF_RECOMPENSE",
                                  "name": "Aria of Recompense", "cost": 1},
                                 {"id": "KLEEMOD-STAGE_PRESENCE",
                                  "name": "Stage Presence", "cost": 1},
                                 {"id": "KLEEMOD-SALON_DEBUT",
                                  "name": "Salon Debut", "cost": 1}]}}
    memo = policy_v1.Memo()
    picks = []
    for _ in range(3):
        d = policy_v1.decide(state, memo)
        assert d.action["action"] == "select_card"
        picks.append(d.action["index"])
    assert len(set(picks)) == 3, f"the same index was re-toggled: {picks}"


def test_a_screen_whose_options_are_exhausted_stops_rather_than_spinning():
    """If every option has been toggled and the wire still will not confirm,
    the arm declines and the driver's forced-default path takes over -- which
    is counted and reported, unlike a silent loop."""
    state = {"state_type": "card_select", "run": {"act": 1, "floor": 6},
             "player": {"hp": 49, "max_hp": 71, "hand": [],
                        "draw_pile": [{"id": "KLEEMOD-STAGE_PRESENCE"}],
                        "discard_pile": [], "exhaust_pile": []},
             "card_select": {"screen_type": "simple_select",
                             "prompt": "Choose 2 Common Cards.",
                             "can_confirm": False, "preview_showing": False,
                             "cards": [{"id": "KLEEMOD-STAGE_PRESENCE",
                                        "name": "Stage Presence", "cost": 1}]}}
    memo = policy_v1.Memo()
    assert policy_v1.decide(state, memo).available is True
    assert policy_v1.decide(state, memo).available is False


def test_a_screens_selection_state_does_not_survive_leaving_the_screen():
    """Furina's starter relic reopens the SAME "Choose a card." Spotlight
    screen every turn, with the same key. Toggles remembered from last turn
    made the arm believe every option was already taken, so it declined a
    screen the bridge will not let anyone cancel ("No skip option available -
    a card must be chosen") and the run bounced until the watchdog stopped it.
    """
    overlay = _overlay(["KLEEMOD-STAGE_PRESENCE"])
    overlay["card_select"]["prompt"] = "Choose a card."
    combat = _combat_state([BIG_SWING], [_enemy("A", "One", 40, "5")])
    memo = policy_v1.Memo()
    # Two visits with a combat turn in between, which is how the real run goes.
    policy_v1.decide(overlay, memo)
    policy_v1.decide(overlay, memo)
    policy_v1.decide(combat, memo)
    assert memo.selected_screens == {}, "the visit never ended"
    again = policy_v1.decide(overlay, memo)
    assert again.available, "the reopened screen was declined as exhausted"
    assert again.action["action"] == "select_card"


def test_a_card_the_game_marks_unplayable_is_never_chosen():
    """tier0's `card_playable` knows about energy and nothing else. A card the
    GAME has blocked -- a boss debuff, an unplayable status, a condition the
    sim does not model -- scored normally, was chosen, was rejected, and was
    chosen again. That loop ended a run on an Act 1 boss at 379 actions."""
    blocked = dict(BIG_SWING, name="Blocked Swing", can_play=False)
    state = _combat_state([blocked, DEFEND],
                          [_enemy("A", "One", 60, "5")])
    d = policy_v1.decide(state, policy_v1.Memo())
    assert d.notes["names"].get("card_name") != "Blocked Swing"


def test_a_play_the_bridge_rejected_is_not_offered_again_this_turn():
    """The backstop for when the wire says `can_play` and the game still says
    no. The driver records the rejection; the policy must honour it."""
    state = _combat_state([BIG_SWING, DEFEND],
                          [_enemy("A", "One", 60, "5")])
    memo = policy_v1.Memo()
    first = policy_v1.decide(state, memo)
    assert first.notes["names"]["card_name"] == "Big Swing"
    memo.rejected.add((memo.turn_key(state), "BASE-SWING"))
    second = policy_v1.decide(state, memo)
    assert second.notes["names"].get("card_name") != "Big Swing"


def test_the_rejection_veto_is_scoped_to_the_turn():
    """A boss debuff that lasts several turns costs one wasted action per turn
    to rediscover, which is cheap and self-correcting. Carrying the veto
    forever would silently shrink the deck."""
    state = _combat_state([BIG_SWING, DEFEND],
                          [_enemy("A", "One", 60, "5")], rnd=1)
    later = _combat_state([BIG_SWING, DEFEND],
                          [_enemy("A", "One", 60, "5")], rnd=2)
    memo = policy_v1.Memo()
    memo.rejected.add((memo.turn_key(state), "BASE-SWING"))
    assert policy_v1.decide(later, memo).notes["names"]["card_name"] == "Big Swing"


# ------------------- revisions #8-#10: the Act-2 reach pass (2026-08-13) ----
#
# Each of the three is a DEFECT fix -- an input the module declares it reads
# and was not reading -- so each test states the wrong answer it replaces.

def _reach_map_state(kinds, hp=62, max_hp=62, act=1, floor=3):
    """A map screen offering `kinds` (wire words: "Elite", "Monster", ...).
    Named apart from this file's older `_map_state` on purpose -- that one
    takes fully-formed option dicts and predates this pass."""
    return {"state_type": "map",
            "run": {"act": act, "floor": floor},
            "player": {"hp": hp, "max_hp": max_hp, "gold": 0,
                       "character": "Klee", "deck": []},
            "map": {"next_options": [{"index": i, "type": k, "leads_to": []}
                                     for i, k in enumerate(kinds)]}}


def test_the_plan_follows_the_character_on_the_wire():
    """Revision #8. Before this, a Klee run drafted, rested and priced every
    overlay under Furina's `salon` -- the module constant, hardcoded when the
    bot played Furina. `resolve_plan` is the sim's own source of truth."""
    klee = {"player": {"character": "Klee"}}
    furina = {"player": {"character": "Furina"}}
    kokomi = {"player": {"character": "Sangonomiya Kokomi"}}
    assert policy_v1._plan_for(klee) == ("klee", "demolition")
    # The Furina arm is unchanged BY CONSTRUCTION, which is what makes this
    # fix safe to ship: her assigned plan is the string that was hardcoded.
    assert policy_v1._plan_for(furina) == ("furina", policy_v1.ARCHETYPE)
    assert policy_v1._plan_for(kokomi)[1] == "priest"


def test_an_unnamed_character_falls_back_to_the_old_constant():
    """A menu state names nobody. The fallback is what every caller used
    unconditionally before the revision, so an unrecognised run behaves as it
    did rather than in some third way."""
    assert policy_v1._plan_for({}) == (policy_v1.CHARACTER,
                                       policy_v1.ARCHETYPE)
    assert policy_v1._plan_for({"player": {"character": "Nobody"}}) == (
        policy_v1.CHARACTER, policy_v1.ARCHETYPE)


def test_the_plan_is_not_frozen_by_a_state_that_names_nobody():
    """The cache must not latch the fallback off a menu frame and keep it for
    the whole run -- that would reintroduce the bug it fixes."""
    memo = policy_v1.Memo()
    assert policy_v1._plan({"player": {}}, memo) == policy_v1.ARCHETYPE
    assert memo.plan is None
    assert policy_v1._plan({"player": {"character": "Klee"}},
                           memo) == "demolition"
    assert memo.plan == "demolition"


def test_the_elite_bar_rises_with_the_elites_this_act():
    """Revision #9. All 48 path decisions of the 20260813-002613 soak printed
    `elite bar 0.55`, including after two elites had been taken, because
    `state["elites_taken"]` is a key the wire has never carried."""
    memo = policy_v1.Memo()
    first = policy_v1._map(_reach_map_state(["Elite", "Monster"]), memo)
    assert "elite bar 0.55" in first.rationale
    assert memo.elites_taken == 1
    second = policy_v1._map(_reach_map_state(["Elite", "Monster"], hp=40), memo)
    assert "elite bar 0.70" in second.rationale
    # 40/62 = 0.65 is under the risen bar, so the elite is now repellent.
    assert second.notes["elite_ok"] is False
    assert second.label.endswith("(N)")


def test_the_elite_count_is_act_local():
    """`tier05.route` declares both counts act-local; the reset is not
    optional bookkeeping, it is what the dial means."""
    memo = policy_v1.Memo()
    policy_v1._map(_reach_map_state(["Elite"]), memo)
    assert memo.elites_taken == 1
    policy_v1._map(_reach_map_state(["Monster"], act=2), memo)
    assert memo.elites_taken == 0 and memo.act_counted == 2


def _spent_rest(can_proceed=True):
    return {"state_type": "rest_site",
            "run": {"act": 1, "floor": 7},
            "player": {"hp": 45, "max_hp": 62, "character": "Klee",
                       "deck": []},
            "rest_site": {"can_proceed": can_proceed, "options": []}}


def test_a_spent_rest_site_is_a_decision_not_a_forced_default():
    """Revision #10. Choosing Rest re-serves the screen with `options: []`;
    9 of the 11 "forced defaults" in the 20260813-002613 soak were this, with
    the HP row jumping +18 immediately before each one."""
    d = policy_v1.decide(_spent_rest(), policy_v1.Memo())
    assert d.available and d.action == {"action": "proceed"}
    assert d.notes["screen_spent"] is True
    assert d.revision == "v1.10"


def test_a_spent_rest_site_that_refuses_its_exit_still_declines():
    """EB-13's own bounce, which is why the revision is gated on
    `can_proceed`: posting a refused `proceed` is a loop with a rationale
    attached, and `_last_resort` is the seat for answering that screen."""
    d = policy_v1.decide(_spent_rest(can_proceed=False), policy_v1.Memo())
    assert not d.available
