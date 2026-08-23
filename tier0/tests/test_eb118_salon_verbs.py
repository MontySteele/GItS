"""EB-118 §5.5 -- the Salon queue-manipulation verbs, staged.

Three verbs over the EXISTING typed FIFO queue, never a counter:

  salon_rotate    the leftmost member goes to the back. Identity preserved,
                  no tick, no Encore, no bow.
  salon_perform   the leftmost member acts NOW, at the standard price.
  leftmost_salon_member_<name> / `leftmost_salon_act`
                  the read half: which performer is next, and what their act
                  is currently worth.

THE LOAD-BEARING TEST is `test_perform_now_and_a_normal_tick_are_the_same_
function`, with the byte-for-byte pair beside it. The packet's hard
requirement is that no second Salon-resolution implementation exists -- so
these pin the SHARING, not merely the agreement. Two copies that happen to
agree today would pass an equality test and fail the requirement.

No shipped card prints either op; every state here is built by hand.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _card(**kw):
    d = dict(id="eb118_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


def _staged(members, encore=9, fanfare=0, seed=0):
    st = furina_state(seed=seed)
    p = st.player
    p.salon = list(members)
    p.powers["salon_member"] = len(p.salon)
    p.encore = encore
    p.fanfare = fanfare
    return st


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


# ======================================================================
# rotate -- a reorder and nothing else
# ======================================================================

def test_rotate_moves_the_leftmost_member_to_the_back():
    st = _staged(["crabaletta", "usher", "chevalmarin"])

    effects.resolve_card(st, _card(effects=[{"op": "salon_rotate"}]))

    assert st.player.salon == ["usher", "chevalmarin", "crabaletta"]


def test_rotate_preserves_member_identity_and_the_counter_mirror():
    """A rotation is a permutation: the same multiset of members, the same
    length, so powers['salon_member'] cannot move either."""
    st = _staged(["usher", "usher", "chevalmarin"])

    effects.resolve_card(st, _card(effects=[{"op": "salon_rotate"}]))

    assert sorted(st.player.salon) == ["chevalmarin", "usher", "usher"]
    assert st.player.powers["salon_member"] == 3


def test_rotate_performs_no_tick_drains_no_encore_and_takes_no_bow():
    """The whole contract of the verb, in one state read.

    Crabaletta is leftmost, so a stray tick would show as damage, a stray bow
    as 14 damage plus a pop, and either as an Encore drain. Stagehands is
    armed to catch a bow that fired without changing the queue length."""
    st = _staged(["crabaletta", "usher"], encore=5)
    p = st.player
    p.powers["salon_bow_block"] = 5
    p.powers["salon_bow_encore"] = 2
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _card(effects=[{"op": "salon_rotate"}]))

    assert p.salon == ["usher", "crabaletta"]
    assert p.encore == 5                       # no upkeep, no bow rider
    assert p.block == 0                        # no usher tick, no Stagehands
    assert p.burst_energy == 0                 # no particle
    assert st.enemies[0].hp == enemy_hp
    assert _events(st, "salon_tick") == []
    assert _events(st, "salon_final_bow") == []


def test_rotate_amount_rotates_that_many_times():
    st = _staged(["crabaletta", "usher", "chevalmarin"])

    effects.resolve_card(st, _card(
        effects=[{"op": "salon_rotate", "amount": 2}]))

    assert st.player.salon == ["chevalmarin", "crabaletta", "usher"]


def test_rotate_on_an_empty_stage_is_a_visible_no_op():
    """`conscript_whiffed`'s pattern. A rotate that found nothing leaves no
    trace in the state, so it has to leave one in the log."""
    st = _staged([])

    effects.resolve_card(st, _card(effects=[{"op": "salon_rotate"}]))

    assert st.player.salon == []
    assert len(_events(st, "salon_rotate_whiffed")) == 1
    assert _events(st, "salon_rotate") == []


# ======================================================================
# perform-now -- the SAME path, once
# ======================================================================

def test_perform_now_and_a_normal_tick_are_the_same_function():
    """THE hard requirement (packet §5.5): no duplicate Salon-resolution
    implementation. Both routes are made to fail together -- if either grew
    its own copy of the tick body, the stub below would not be reached from
    it and the assertion would fail."""
    seen = []
    original = effects.salon_member_act

    def spy(state, member):
        seen.append(member)
        return original(state, member)

    upkeep = _staged(["usher"])
    on_demand = _staged(["usher"])
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(effects, "salon_member_act", spy)
        effects.salon_tick(upkeep)
        effects.resolve_card(on_demand,
                             _card(effects=[{"op": "salon_perform"}]))

    assert seen == ["usher", "usher"]


@pytest.mark.parametrize("member", sorted(C.SALON_MEMBERS))
@pytest.mark.parametrize("encore", [9, 0])
def test_perform_now_matches_a_normal_tick_byte_for_byte(member, encore):
    """Same member, same meter, same seed: the on-demand act and the
    turn-start act must be indistinguishable in every observable -- enemy HP
    (the Focus-scaled damage and the dry three-quarters), Encore (the upkeep
    drain), Block, the burst particle, and the telemetry row itself.

    `encore=0` is the dry arm; `fanfare=25` puts the Focus term at +2 so a
    reader that dropped the scaling cannot pass by dealing the printed
    number."""
    upkeep = _staged([member], encore=encore, fanfare=25, seed=7)
    on_demand = _staged([member], encore=encore, fanfare=25, seed=7)

    effects.salon_tick(upkeep)
    effects.resolve_card(on_demand, _card(effects=[{"op": "salon_perform"}]))

    def observables(st):
        return (st.enemies[0].hp, st.player.encore, st.player.block,
                st.player.burst_energy, st.player.salon,
                _events(st, "salon_tick"))

    assert observables(on_demand) == observables(upkeep)


def test_perform_now_fires_exactly_once():
    """One act, not one per member and not one per slot."""
    st = _staged(["crabaletta", "crabaletta", "crabaletta"], encore=9)

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert len(_events(st, "salon_tick")) == 1
    assert st.player.encore == 9 - C.SALON_TICK_ENCORE_COST


def test_perform_now_drains_the_tick_encore_cost():
    st = _staged(["crabaletta"], encore=1)

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert st.player.encore == 1 - C.SALON_TICK_ENCORE_COST
    assert _events(st, "salon_tick")[0]["paid"] is True


def test_perform_now_goes_dry_on_an_empty_meter():
    """SALON_DRY_DAMAGE_MULT, inherited rather than restated: the act still
    happens, at three-quarters, and the meter cannot go below zero."""
    st = _staged(["crabaletta"], encore=0)
    printed = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert st.player.encore == 0
    assert _events(st, "salon_tick")[0]["paid"] is False
    assert enemy_hp - st.enemies[0].hp == int(printed
                                              * C.SALON_DRY_DAMAGE_MULT)


def test_perform_now_carries_the_fanfare_focus_term():
    st = _staged(["crabaletta"], encore=9, fanfare=2 * C.SALON_FOCUS_PER)
    printed = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert enemy_hp - st.enemies[0].hp == printed + 2


def test_perform_now_pays_the_burst_particle():
    st = _staged(["crabaletta"], encore=9)
    assert st.player.burst_max, "the fixture must have a burst meter"

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    # The tick's own particle AND the spend rider her particle economy pays
    # on the upkeep Encore (BURST_PER_ENCORE_SPENT) -- both inherited from the
    # shared path, which is why the on-demand act cannot pay a cheaper meter.
    assert st.player.burst_energy == (
        C.SALON_TICK_BURST
        + C.BURST_PER_ENCORE_SPENT * C.SALON_TICK_ENCORE_COST)


def test_perform_now_leaves_the_member_on_stage():
    """A performance is not a bow and not a rotation: the queue is untouched,
    so the same member is still leftmost afterwards."""
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert st.player.salon == ["usher", "crabaletta"]
    assert st.player.powers["salon_member"] == 2
    assert _events(st, "salon_final_bow") == []


def test_perform_now_amount_repeats_the_leftmost_member():
    """`amount: N` is N acts by whoever is leftmost -- pair it with
    `salon_rotate` to spread them. Two acts, two upkeep payments."""
    st = _staged(["crabaletta", "usher"], encore=9)
    printed = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _card(
        effects=[{"op": "salon_perform", "amount": 2}]))

    assert len(_events(st, "salon_tick")) == 2
    assert st.player.encore == 9 - 2 * C.SALON_TICK_ENCORE_COST
    assert enemy_hp - st.enemies[0].hp == 2 * printed
    assert st.player.block == 0                # the usher never acted


def test_perform_now_on_an_empty_stage_is_a_visible_no_op():
    st = _staged([], encore=5)

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert st.player.encore == 5
    assert _events(st, "salon_tick") == []
    assert len(_events(st, "salon_perform_whiffed")) == 1


def test_perform_now_stops_when_the_last_enemy_is_already_dead():
    """The upkeep loop's break condition, inherited: `salon_member_act`
    refuses on a cleared board, so a repeat cannot bill Encore for acts that
    have nothing to act against."""
    st = _staged(["crabaletta"], encore=9)
    st.enemies[0].hp = 0

    effects.resolve_card(st, _card(
        effects=[{"op": "salon_perform", "amount": 3}]))

    assert st.player.encore == 9
    assert _events(st, "salon_tick") == []


# ======================================================================
# the read half
# ======================================================================

def test_the_leftmost_predicate_names_the_next_performer():
    st = _staged(["chevalmarin", "crabaletta"])

    assert effects._predicate(st, "leftmost_salon_member_chevalmarin")
    assert not effects._predicate(st, "leftmost_salon_member_crabaletta")
    assert not effects._predicate(st, "leftmost_salon_member_usher")


def test_rotate_moves_the_answer_the_predicate_gives():
    """The two verbs are one mechanism: rotating is how a card body CHOOSES
    which performer the reads and the bow will find."""
    st = _staged(["chevalmarin", "crabaletta"])

    effects.resolve_card(st, _card(effects=[{"op": "salon_rotate"}]))

    assert effects._predicate(st, "leftmost_salon_member_crabaletta")
    assert not effects._predicate(st, "leftmost_salon_member_chevalmarin")


def test_the_leftmost_predicate_is_false_on_an_empty_stage():
    st = _staged([])
    for member in C.SALON_MEMBERS:
        assert not effects._predicate(st, f"leftmost_salon_member_{member}")


def test_the_leftmost_predicate_is_load_checked_against_the_member_table():
    """A misspelled member must fail at load, not silently never fire."""
    for member in C.SALON_MEMBERS:
        assert effects.is_known_predicate(f"leftmost_salon_member_{member}")
    assert not effects.is_known_predicate("leftmost_salon_member_navia")
    assert not effects.is_known_predicate("leftmost_salon_member_")


def test_the_leftmost_predicate_gates_a_card_branch():
    """The sheet-facing shape: a conditional keyed on WHO is next."""
    st = _staged(["usher", "crabaletta"], encore=9)
    body = _card(effects=[{
        "op": "conditional",
        "if": "leftmost_salon_member_usher",
        "then": [{"op": "gain_encore", "amount": 3}],
        "else": [{"op": "gain_encore", "amount": 1}],
    }])

    effects.resolve_card(st, body)

    assert st.player.encore == 12


def test_the_leftmost_act_read_is_the_value_the_member_would_deal():
    """The reward half: `leftmost_salon_act` and the act itself resolve
    through one expression, so a card that pays off the next performer cannot
    print a number the stage will not deliver."""
    st = _staged(["crabaletta"], encore=9, fanfare=2 * C.SALON_FOCUS_PER)
    read = effects._runtime_count(st, "leftmost_salon_act")
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _card(effects=[{"op": "salon_perform"}]))

    assert read == enemy_hp - st.enemies[0].hp


def test_the_leftmost_act_read_goes_dry_with_the_meter():
    st = _staged(["usher"], encore=0)
    printed = C.SALON_MEMBERS["usher"]["tick"]["block"]

    assert effects._runtime_count(st, "leftmost_salon_act") == int(
        printed * C.SALON_DRY_DAMAGE_MULT)


def test_the_leftmost_act_read_is_zero_on_an_empty_stage():
    st = _staged([])

    assert effects._runtime_count(st, "leftmost_salon_act") == 0


def test_the_leftmost_act_read_drives_a_damage_amount():
    """A card body using the read, end to end: the sheet-facing form is
    `amount: leftmost_salon_act` on any op that takes a runtime count."""
    st = _staged(["crabaletta"], encore=9)
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _card(effects=[{
        "op": "damage", "target": "enemy", "amount": "leftmost_salon_act"}]))

    assert enemy_hp - st.enemies[0].hp == (
        C.SALON_MEMBERS["crabaletta"]["tick"]["damage"])


# ======================================================================
# codegen -- the sheet syntax the verbs will be written in
# ======================================================================

def _hypothetical(effects):
    """A Furina row that prints the verb under test.

    No SHIPPED card may use these ops yet (EB-118 is staged infrastructure),
    so the codegen support is exercised against a row built here rather than
    against the sheet. The row is a copy of a real one so every field the
    generator reads is present and plausible.
    """
    import copy

    import yaml

    from tools import gen_klee_cards as gen

    sheet = yaml.safe_load(
        (gen.REPO / "docs" / "furina-cards.yaml").read_text(encoding="utf-8"))
    rows = sheet["cards"] if isinstance(sheet, dict) else sheet
    row = copy.deepcopy(next(r for r in rows if r["id"] == "salon_debut"))
    row["effects"] = effects
    return row


def test_codegen_emits_the_rotate_verb_as_one_synchronous_call():
    from tools import gen_klee_cards as gen

    body = gen.emit(_hypothetical([{"op": "salon_rotate"}]),
                    gen.FURINA_PROFILE)

    assert "SalonMemberPower.RotateLeftmost(Owner.Creature, 1);" in body
    assert "await SalonMemberPower.RotateLeftmost" not in body
    assert "BowLeftmost" not in body


def test_codegen_emits_perform_now_through_the_shared_entry_point():
    from tools import gen_klee_cards as gen

    body = gen.emit(_hypothetical([{"op": "salon_perform", "amount": 2}]),
                    gen.FURINA_PROFILE)

    assert ("await SalonMemberPower.PerformLeftmost("
            "choiceContext, Owner.Creature, 2);") in body


def test_codegen_writes_the_verbs_onto_the_card_face():
    from tools import gen_klee_cards as gen

    rotate = gen.build_description(_hypothetical([{"op": "salon_rotate"}]))
    perform = gen.build_description(_hypothetical([{"op": "salon_perform"}]))

    assert "moves to the back" in rotate
    assert "performs now" in perform


def test_codegen_maps_the_leftmost_predicate_onto_the_shared_member_enum():
    from tools import gen_klee_cards as gen

    for member in C.SALON_MEMBERS:
        cs = gen.predicate_cs(f"leftmost_salon_member_{member}")
        assert cs == ("SalonMemberPower.LeftmostMember(Owner.Creature) == "
                      f"{gen.SALON_MEMBER_CS[member]}")
        assert gen.predicate_text(f"leftmost_salon_member_{member}") == (
            f"If {gen.SALON_MEMBER_NAMES[member]} is next to perform")

    # `random` is not an identity, and an unknown member is not a predicate.
    assert gen.predicate_cs("leftmost_salon_member_random") is None
    assert gen.predicate_cs("leftmost_salon_member_navia") is None
