"""EB-71 (R174): the Sly grammar unification moves NO number.

Two near-identical mechanics wore the word "sly" -- Kokomi's authored effect
list (`Card.sly`) and the base-game auto-play keyword (`Card.sly_keyword`,
plus Hand Trick's one-turn `Card.sly_this_turn` twin). R174 ruled them into
one: the standard effect-list grammar, with the keyword carried as the
reserved `sly_autoplay` rider inside the same `sly` list.

WHY THIS FILE EXISTS. The ruling is a GRAMMAR change and the sprint it landed
in is stamp-free (no RT/D/P/C bump), so it may not move a drafted or a combat
value -- not by a point, not by an event, not by an ordering. Every expected
value below was CAPTURED FROM THE PRE-UNIFICATION TREE (the old grammar,
before any of this landed) and pasted in unedited; the scenarios then drive
the same situations through the new grammar. A number that moves fails here
rather than six weeks later inside somebody's run report.

The behaviour pins for each mechanic still live where they always did
(test_si_effects.py A4 block, test_si_pass6.py Hand Trick block,
test_si_powers.py Master Planner, test_kokomi.py Assist lane). This file is
narrower and blunter: same inputs, same outputs, across the rename.
"""

import pytest

from tier0.content import loader
from tier0.engine import combat, effects, refpowers
from tier0.engine.state import (SLY_AUTOPLAY, SLY_AUTOPLAY_OP,
                                SLY_AUTOPLAY_THIS_TURN, Card,
                                sly_autoplays, sly_autoplays_permanently,
                                sly_granted_this_turn, sly_riders)
from tier0.tests.conftest import make_enemy, make_state
from tier05 import draft
from tier05.draft import _static_power


def card(cid="c", type="skill", cost=0, fx=None, keyword=False, **kw):
    c = Card(id=cid, name=cid, cost=cost, type=type,
             effects=fx if fx is not None else [], **kw)
    if keyword:
        c.sly = list(c.sly) + [dict(SLY_AUTOPLAY)]
    return c


def _discard_one(state):
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": 1, "select": "chosen"}]))


def _events(state):
    return [e["event"] for e in state.log]


# --- the marker is not an op, and is worth nothing to anybody --------------

def test_the_autoplay_rider_is_not_an_engine_op():
    """It is a marker the discard trigger reads, never a verb `_resolve_
    effects` dispatches. Registering it in OPS would put an unpriceable entry
    in front of tools/lint_op_parity.py, and pricing it is a DRAFTER_VERSION
    change -- i.e. [USER]'s call, not this refactor's."""
    assert SLY_AUTOPLAY_OP not in effects.OPS
    assert SLY_AUTOPLAY_OP not in draft.STATIC_OP_PRICING


def test_the_autoplay_rider_adds_exactly_zero_drafted_value():
    """PRE-UNIFICATION VALUE: the keyword lived on a boolean the drafter
    never read, so a Sly card and its vanilla twin priced identically. That
    stays true, or the unification moved a drafted number."""
    plain = card("kw", type="skill", cost=1,
                 fx=[{"op": "block", "amount": 5}])
    keyword = card("kw", type="skill", cost=1, keyword=True,
                   fx=[{"op": "block", "amount": 5}])
    assert _static_power(plain) == _static_power(keyword) == 5.0
    # And the marker does not suppress an authored rider sharing the field.
    rider = card("kw", type="skill", cost=1,
                 sly=[{"op": "block", "amount": 4}],
                 fx=[{"op": "block", "amount": 5}])
    both = card("kw", type="skill", cost=1, keyword=True,
                sly=[{"op": "block", "amount": 4}],
                fx=[{"op": "block", "amount": 5}])
    assert _static_power(rider) == _static_power(both) == 7.0


# Every committed card that carries a Sly rider, priced on the
# PRE-UNIFICATION tree. These eight are Kokomi's Assist lane; nothing
# committed carries the base-game keyword (it only ever arrives through the
# extractor, into the gitignored reference pool).
PRE_UNIFICATION_SLY_PRICES = {
    "driftglass": 10.5,
    "drifting_lantern": 6.0,
    "driftwood_charm": 3.5,
    "quiet_harbor": 5.0,
    "salt_line": 5.25,
    "tidal_lure": 5.0,
    "undertow": 5.0,
    "whispered_word": 2.5,
}


def test_no_committed_sly_card_changed_its_drafted_price():
    index = loader._card_index()
    priced = {cid: round(_static_power(c), 10)
              for cid, c in index.items() if c.sly}
    assert priced == PRE_UNIFICATION_SLY_PRICES
    # And the marker is nowhere in the committed world, so nothing else in
    # the pool could have moved through this field either.
    assert not [cid for cid, c in index.items() if sly_autoplays(c)]


def test_a_sly_rider_is_vocabulary_checked_at_load_and_the_marker_is_not():
    """Riders are printed effects, so they now meet the same load-time op
    check `effects:` always did -- and the auto-play marker, which is not an
    op, must pass through it rather than take the reference pool down."""
    keyword = card("kw", keyword=True, fx=[{"op": "block", "amount": 1}])
    loader._validate_effect_vocabulary("kw", sly_riders(keyword))    # no raise
    with pytest.raises(ValueError, match="unknown op"):
        loader._validate_effect_vocabulary("typo", [{"op": "blok"}])


# --- the printed keyword, unchanged ---------------------------------------

def test_printed_keyword_autoplay_is_event_for_event_what_it_was():
    """PRE-UNIFICATION LOG, pasted verbatim."""
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    state.player.energy = 3
    sly = card("sly", type="attack", cost=2, keyword=True,
               fx=[{"op": "damage", "amount": 7, "target": "enemy"}])
    state.player.hand = [sly]
    _discard_one(state)
    assert _events(state) == ["discard", "sly_autoplay", "play", "damage"]
    assert state.enemies[0].hp == 53
    assert state.player.energy == 3          # the play is free
    assert state.cards_played_this_turn == 1
    assert [c.id for c in state.player.discard_pile] == ["sly"]


def test_the_batch_still_discards_whole_before_any_card_plays():
    """The ordering the unification most easily could have broken: authored
    riders resolve INSIDE the discard loop, the auto-play batch AFTER it."""
    state = make_state()
    seen = []
    a = card("a", keyword=True, fx=[{"op": "block", "amount": 1}])
    b = card("b", keyword=True, fx=[{"op": "block", "amount": 1}])
    state.player.hand = [a, b]
    original = effects.OPS["block"]

    def spy(st, fx, c):
        seen.append(sorted(x.id for x in st.player.discard_pile))
        return original(st, fx, c)

    effects.OPS["block"] = spy
    try:
        effects.resolve_card(state, card("discarder", fx=[
            {"op": "discard", "amount": 2, "select": "chosen"}]))
    finally:
        effects.OPS["block"] = original
    assert seen == [["b"], ["a"]]
    assert _events(state) == ["discard", "discard", "sly_autoplay", "play",
                              "block", "sly_autoplay", "play", "block"]
    assert state.player.block == 2


def test_an_authored_rider_still_resolves_inline_and_plays_nothing():
    state = make_state()
    assist = card("assist", sly=[{"op": "block", "amount": 4}],
                  fx=[{"op": "block", "amount": 99}])
    state.player.hand = [assist]
    _discard_one(state)
    assert _events(state) == ["discard", "sly", "block"]
    assert state.player.block == 4
    assert state.cards_played_this_turn == 0


def test_a_marker_only_card_emits_no_authored_sly_event():
    """`sly` announces an AUTHORED list resolving. The keyword's own event is
    `sly_autoplay`, and moving the keyword onto the same field must not start
    emitting the other one -- metrics and graders read these names."""
    state = make_state()
    sly = card("sly", keyword=True, fx=[{"op": "block", "amount": 3}])
    state.player.hand = [sly]
    _discard_one(state)
    assert "sly" not in _events(state)
    assert sly_riders(sly) == []


def test_the_hand_flush_is_still_not_a_sly_trigger():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    sly = card("sly", keyword=True, fx=[{"op": "block", "amount": 5}])
    state.player.hand = [sly]
    combat._player_turn(state, lambda s: None)
    assert sly in state.player.discard_pile
    assert state.player.block == 0
    assert state.cards_played_this_turn == 0


# --- the sly_this_turn fold ------------------------------------------------

def test_hand_tricks_grant_cashes_exactly_as_the_boolean_did():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    victim = card("victim", type="skill", cost=1,
                  fx=[{"op": "block", "amount": 3}])
    attack = card("attack", type="attack", cost=1,
                  fx=[{"op": "damage", "amount": 4, "target": "enemy"}])
    state.player.hand = [victim, attack]
    effects.resolve_card(state, card("hand_trick", fx=[
        {"op": "grant_sly_this_turn", "card_type": "skill"}]))
    assert victim.sly == [SLY_AUTOPLAY_THIS_TURN]
    assert sly_granted_this_turn(victim)
    assert not sly_autoplays_permanently(victim)
    _discard_one(state)
    assert _events(state) == ["granted_sly", "discard", "sly_autoplay",
                              "play", "block"]
    assert state.player.block == 3
    assert [c.id for c in state.player.hand] == ["attack"]


def test_the_grant_expires_at_the_turn_boundary_and_takes_nothing_with_it():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    victim = card("victim", type="skill", cost=1,
                  sly=[{"op": "block", "amount": 2}],
                  fx=[{"op": "block", "amount": 3}])
    state.player.hand = [victim]
    effects.resolve_card(state, card("hand_trick", fx=[
        {"op": "grant_sly_this_turn", "card_type": "skill"}]))
    refpowers.reset_turn_counters(state)
    # The grant is gone; the AUTHORED rider it was sitting beside is not.
    assert not sly_autoplays(victim)
    assert sly_riders(victim) == [{"op": "block", "amount": 2}]
    _discard_one(state)
    assert _events(state) == ["granted_sly", "discard", "sly", "block"]
    assert state.player.block == 2          # the list, not a free play


def test_two_grants_in_one_turn_still_pick_two_different_cards():
    state = make_state()
    x = card("x", type="skill", cost=1, fx=[{"op": "block", "amount": 3}])
    y = card("y", type="skill", cost=1, fx=[{"op": "block", "amount": 2}])
    state.player.hand = [x, y]
    for _ in range(2):
        effects.resolve_card(state, card("ht", fx=[
            {"op": "grant_sly_this_turn", "card_type": "skill"}]))
    assert sly_granted_this_turn(x) and sly_granted_this_turn(y)


def test_a_printed_keyword_skill_is_still_a_legal_grant_target():
    """The pre-unification filter was `!card.IsSlyThisTurn`, which a PRINTED
    keyword never set -- so Hand Trick could land on an already-Sly Skill and
    the second copy went elsewhere. Widening that filter to "is this card Sly
    at all" would move which card the pilot picks, so it is not done."""
    state = make_state()
    printed = card("printed", type="skill", cost=1, keyword=True,
                   fx=[{"op": "block", "amount": 9}])
    state.player.hand = [printed]
    effects.resolve_card(state, card("hand_trick", fx=[
        {"op": "grant_sly_this_turn", "card_type": "skill"}]))
    assert [e["event"] for e in state.log] == ["granted_sly"]
    # One card, and it auto-plays exactly once whatever it is carrying.
    _discard_one(state)
    assert _events(state)[-4:] == ["discard", "sly_autoplay", "play", "block"]
    assert state.player.block == 9


# --- Master Planner speaks the unified form -------------------------------

def test_master_planner_marks_the_skill_permanently():
    state = make_state()
    state.player.powers["master_planner"] = 1
    skill = card("skill", type="skill", cost=0,
                 fx=[{"op": "block", "amount": 2}])
    combat.resolve_free_play(state, skill)
    assert skill.sly == [SLY_AUTOPLAY]
    assert sly_autoplays_permanently(skill)
    refpowers.reset_turn_counters(state)
    assert sly_autoplays(skill)             # a turn sweep must not clear it
    assert [e["event"] for e in state.log] == ["play", "block",
                                               "master_planner"]


def test_master_planner_leaves_attacks_alone_and_marks_once():
    state = make_state()
    state.enemies = [make_enemy(hp=60)]
    state.player.powers["master_planner"] = 1
    attack = card("atk", type="attack", cost=0,
                  fx=[{"op": "damage", "amount": 3, "target": "enemy"}])
    combat.resolve_free_play(state, attack)
    assert attack.sly == []
    skill = card("skill", type="skill", cost=0,
                 fx=[{"op": "block", "amount": 2}])
    combat.resolve_free_play(state, skill)
    combat.resolve_free_play(state, skill)
    assert skill.sly == [SLY_AUTOPLAY]      # a switch, not a counter
    assert sum(e["event"] == "master_planner" for e in state.log) == 1


def test_master_planner_upgrades_a_one_turn_grant_to_permanent():
    """Pre-unification this fell out of the two fields: the power checked
    `sly_keyword`, which Hand Trick's grant never set, so playing a
    Hand-Tricked Skill under Master Planner made the Sly permanent. Folding
    both onto one field must not swallow that upgrade."""
    state = make_state()
    state.player.powers["master_planner"] = 1
    skill = card("skill", type="skill", cost=0,
                 fx=[{"op": "block", "amount": 2}])
    state.player.hand = [skill]
    effects.resolve_card(state, card("hand_trick", fx=[
        {"op": "grant_sly_this_turn", "card_type": "skill"}]))
    combat.resolve_free_play(state, skill)
    refpowers.reset_turn_counters(state)
    assert sly_autoplays(skill)
    assert sly_autoplays_permanently(skill)


def test_a_granted_rider_never_leaks_back_into_the_printed_row():
    """Grants rebind the list instead of appending to it, so a grant landing
    on a card that still shares the loader's row cannot mark the row."""
    printed = [{"op": "block", "amount": 4}]
    a = Card(id="a", name="a", cost=1, type="skill", sly=printed)
    b = Card(id="b", name="b", cost=1, type="skill", sly=printed)
    state = make_state()
    state.player.hand = [a, b]
    effects.resolve_card(state, card("hand_trick", fx=[
        {"op": "grant_sly_this_turn", "card_type": "skill"}]))
    granted = [c for c in (a, b) if sly_autoplays(c)]
    assert len(granted) == 1
    assert printed == [{"op": "block", "amount": 4}]
    other = [c for c in (a, b) if c not in granted][0]
    assert other.sly == printed
