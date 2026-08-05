"""R99/4b — the archetype-committed draft arm, and the pin that keeps it honest.

The arm's whole claim on being usable is one sentence: **the flag is the only
delta from baseline**. If that is false, then every baseline soak number taken
after it landed is quietly a number about a different policy, R98's validation
stops meaning what it says, and nobody finds out until two soaks disagree for a
reason nobody can name.

So the pin comes first in this file, and it is not a spot check: every state
shape the driver can hand `decide` is replayed through `commit=None` and
compared against the same call without the argument, decision for decision.

The rest tests the arm itself — that it takes the declared archetype when it is
on offer, that it falls through to the sim's own plan when it is not, and that
a word nobody declared is refused rather than silently run as baseline under a
committed label.
"""

import pytest

from understudy import committed, policy_v1

# Real sheet ids: `adapter.resolve_card` resolves a `KLEEMOD-` id through
# `loader.peek_card`, so these carry their sheet archetypes rather than the
# `["generic"]` a text-approximated card gets. That matters here — a fixture
# whose archetypes were invented would test the fixture.
FANFARE = {"id": "KLEEMOD-ARIA_OF_RECOMPENSE", "name": "Aria of Recompense",
           "cost": 1, "type": "Skill", "rarity": "basic"}
SALON = {"id": "KLEEMOD-CASTING_CALL", "name": "Casting Call",
         "cost": 1, "type": "Power", "rarity": "common"}
PLAIN = {"id": "BASE-BASH", "name": "Bash", "cost": 2, "type": "Attack",
         "rarity": "common", "description": "Deal 8 damage."}


def _reward(cards):
    return {"state_type": "card_reward",
            "run": {"act": 1, "floor": 4},
            "player": {"hp": 60, "max_hp": 71, "gold": 99, "hand": [],
                       "draw_pile": [], "discard_pile": [], "exhaust_pile": []},
            "card_reward": {"cards": list(cards)}}


# ------------------------------------------------------------- the sheets ---

def test_membership_comes_off_the_design_sheet_and_upgrades_resolve():
    table = committed.archetype_table()
    assert "fanfare" in table["Aria of Recompense"]
    assert table["Aria of Recompense+"] == table["Aria of Recompense"]


def test_a_card_with_no_sheet_row_belongs_to_no_archetype():
    """Every base-game and colorless card. This is correct rather than a gap:
    those are exactly the cards a committed deck is trying not to be made of.
    """
    class _C:
        name = "Strike"
    assert not committed.is_committed(_C(), "fanfare")


def test_an_undeclarable_word_is_refused_rather_than_run_as_baseline():
    """A mislabelled arm is worse than a refused one: the label is what the
    whole measurement gets read by."""
    assert committed.normalise(None) is None
    assert committed.normalise("  ") is None
    assert committed.normalise("Fanfare") == "fanfare"
    with pytest.raises(ValueError):
        committed.normalise("goodstuff")


def test_generic_is_not_declarable():
    """Committing to no archetype is what baseline already is, and a second
    spelling of baseline is a second thing to keep comparable."""
    assert "generic" not in committed.COMMITTABLE


# ------------------------------------------------------------- THE PIN ------

def _states():
    """One of every shape `RunDriver._drive` can hand to `decide`."""
    combat = {
        "state_type": "monster",
        "run": {"act": 1, "floor": 7},
        "battle": {"round": 1, "enemies": [
            {"entity_id": "e1", "name": "Toadpole", "hp": 20, "max_hp": 20,
             "block": 0, "intents": [{"type": "Attack", "label": "9"}],
             "status": []}]},
        "player": {"hp": 39, "max_hp": 71, "block": 0, "energy": 3, "gold": 0,
                   "status": [], "potions": [],
                   "hand": [dict(PLAIN, can_play=True, target_type="Enemy")],
                   "draw_pile": [], "discard_pile": [], "exhaust_pile": []},
    }
    rest = {"state_type": "rest_site", "run": {"act": 1, "floor": 8},
            "player": {"hp": 40, "max_hp": 71, "gold": 0, "hand": [],
                       "draw_pile": [], "discard_pile": [], "exhaust_pile": []},
            "options": [{"name": "Rest"}, {"name": "Smith"}]}
    mapping = {"state_type": "map", "run": {"act": 1, "floor": 5},
               "player": {"hp": 50, "max_hp": 71, "gold": 0, "hand": [],
                          "draw_pile": [], "discard_pile": [],
                          "exhaust_pile": []},
               "map": {"next_options": [
                   {"kind": "monster", "leads_to": ["rest"]},
                   {"kind": "elite", "leads_to": ["shop"]}]}}
    shop = {"state_type": "shop", "run": {"act": 1, "floor": 9},
            "player": {"hp": 50, "max_hp": 71, "gold": 200, "hand": [],
                       "draw_pile": [], "discard_pile": [], "exhaust_pile": []},
            "items": [dict(PLAIN, type="card", price=50)]}
    return [
        _reward([FANFARE, SALON, PLAIN]),
        _reward([PLAIN]),
        _reward([]),
        combat, rest, mapping, shop,
        {"state_type": "event", "run": {"act": 1, "floor": 2}},
        {"state_type": "unknown", "run": {"act": 1, "floor": 0}},
    ]


def test_the_flag_off_is_baseline_decision_for_decision():
    """THE PIN. `commit=None` must be the policy R98 validated — not similar
    to it, identical to it — or every baseline number taken after this landed
    is a number about a different policy."""
    for state in _states():
        base = policy_v1.decide(state, policy_v1.Memo()).as_log()
        flagged = policy_v1.decide(state, policy_v1.Memo(), commit=None).as_log()
        assert base == flagged, f"the flag moved baseline at {state['state_type']}"


def test_the_flag_changes_the_draft_and_nothing_but_the_draft():
    """The other half of the pin: with a commitment set, the ONLY category that
    may move is the draft. A commitment that leaked into the combat ladder or
    the map arm would make every divergence in a committed soak unreadable."""
    for state in _states():
        base = policy_v1.decide(state, policy_v1.Memo()).as_log()
        armed = policy_v1.decide(state, policy_v1.Memo(),
                                 commit="fanfare").as_log()
        if state["state_type"] == "card_reward":
            continue
        assert base == armed, f"the commitment leaked into {state['state_type']}"


# -------------------------------------------------------------- the arm -----

def test_the_committed_arm_takes_the_declared_archetype():
    d = policy_v1.decide(_reward([PLAIN, FANFARE]), policy_v1.Memo(),
                         commit="fanfare")
    assert d.action == {"action": "select_card_reward", "card_index": 1}
    assert d.revision == policy_v1.COMMIT_REVISION
    assert d.notes["commit"] == "fanfare"
    assert d.notes["committed_offers"] == ["Aria of Recompense"]


def test_the_two_commitments_take_different_cards_from_one_screen():
    """The same screen, two declarations, two decks. This is the arm's whole
    job: one variable per measurement window, and the variable is the word."""
    offers = _reward([FANFARE, SALON, PLAIN])
    fan = policy_v1.decide(offers, policy_v1.Memo(), commit="fanfare")
    sal = policy_v1.decide(offers, policy_v1.Memo(), commit="salon")
    assert fan.action["card_index"] == 0
    assert sal.action["card_index"] == 1


def test_without_the_archetype_on_offer_the_sims_own_plan_decides():
    """Rung 2, and it keeps the sim's right to skip. A committed arm that took
    junk rather than skip would be measuring junk."""
    d = policy_v1.decide(_reward([PLAIN]), policy_v1.Memo(), commit="fanfare")
    assert d.revision == policy_v1.COMMIT_REVISION + "-fallback"
    assert d.notes["committed_offers"] == []
    assert d.action["action"] in ("select_card_reward", "skip_card_reward")


def test_an_empty_screen_is_unavailable_rather_than_a_guess():
    d = policy_v1.decide(_reward([]), policy_v1.Memo(), commit="salon")
    assert not d.available


def test_the_committed_arm_still_names_what_it_posts():
    """Revision #7 is attached in `decide` for every arm, including this one:
    a soak log that cannot be categorised without reading prose is the thing
    the P1 blocker existed to prevent."""
    d = policy_v1.decide(_reward([PLAIN, FANFARE]), policy_v1.Memo(),
                         commit="fanfare")
    assert d.notes["names"]["card_name"] == "Aria of Recompense"


def test_the_arm_is_deterministic():
    """No policy roll is consumed by the commitment. Two identical states give
    the same answer, which is what makes a divergence between two runs a fact
    about the runs."""
    state = _reward([FANFARE, SALON, PLAIN])
    first = policy_v1.decide(state, policy_v1.Memo(), commit="fanfare").as_log()
    second = policy_v1.decide(state, policy_v1.Memo(), commit="fanfare").as_log()
    assert first == second
