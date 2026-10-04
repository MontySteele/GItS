"""THE FURINA RE-FOUNDING SIM SLICE (`tier0/engine/furina_v2.py`): the rules.

`review/active/furina-refounding-2026-10-03.md` sec.1 as amended by sec.8,
sec.2's cast and sec.9's rows. One pin per rule; the readings the paper left
open are `furina_v2.READINGS`. The slice is a separate arm: today's Furina
(`furina_stage`) is not touched, which the last tests pin. NOTHING MEASURED
HERE IS QUOTABLE.
"""

from __future__ import annotations

import random

import pytest

from tier0.engine import combat, furina_stage
from tier0.engine import furina_v2 as V
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.harness import furina_v2_probe as H


class Fixed:
    """A decider that always names one seat (or Spend / no Spend)."""

    def __init__(self, cue=0, spend=True, front=None):
        self.cue, self.spend, self.front = cue, spend, front

    def cue_target(self, state):
        return self.cue

    def curtain_spend(self, state, card, plain, big, price):
        return self.spend

    def front_target(self, state):
        return self.front


def _state(stage=(), fanfare=0, enemies=1, hp=500, deck=0, decider=None):
    p = V.build_player([])
    p.hp = p.max_hp = 200
    p.fv2.stage = list(stage)
    p.fv2.fanfare = fanfare
    p.fv2.opened = True
    p.fv2.decider = decider or Fixed()
    p.draw_pile = [Card(id=f"filler{i}", name="f", cost=0, type="skill")
                   for i in range(deck)]
    st = CombatState(player=p,
                     enemies=[Enemy(hp=hp, max_hp=hp, name=f"paper{i}",
                                    intents=[{"kind": "block", "amount": 0}])
                              for i in range(enemies)],
                     rng=random.Random(0))
    st.turn = 1
    return st


def _play(st, cid, energy=10):
    card = V.make_card(cid)
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


def _dealt(st):
    return sum(e.max_hp - e.hp for e in st.enemies)


# ---------------------------------------------------------------------------
# Rule 1: three seats, Usher opens, acts front to back.
# ---------------------------------------------------------------------------

def test_salon_solitaire_opens_with_usher_once():
    st = _state()
    st.player.fv2.opened = False
    V.turn_start(st)
    assert st.player.fv2.stage == ["usher"]
    st.player.fv2.stage = ["crabaletta"]
    V.turn_start(st)
    assert st.player.fv2.stage == ["crabaletta"]


def test_acts_run_front_to_back_so_seat_order_funds_a_star():
    # Charlotte in front of Neuvillette funds him the same turn ...
    st = _state(["charlotte", "neuvillette"], fanfare=1)
    V.end_of_turn_acts(st)
    assert st.player.fv2.ledger["star_acts"]["neuvillette"] == 1
    assert st.player.fv2.fanfare == 0
    # ... and behind him she does not.
    st = _state(["neuvillette", "charlotte"], fanfare=1)
    V.end_of_turn_acts(st)
    assert st.player.fv2.ledger["star_skips"]["neuvillette"] == 1
    assert st.player.fv2.fanfare == 2


def test_the_trio_acts():
    st = _state(["usher", "chevalmarin", "crabaletta"], enemies=2)
    V.end_of_turn_acts(st)
    assert st.player.block == V.ACT_USHER_BLOCK
    assert _dealt(st) == 2 * V.ACT_CHEVALMARIN_DAMAGE + V.ACT_CRABALETTA_DAMAGE


# ---------------------------------------------------------------------------
# Rule 5: one number; a star pays, a payment is not a Spend; short skips.
# ---------------------------------------------------------------------------

def test_a_star_payment_is_not_a_spend():
    st = _state(["clorinde", "navia"], fanfare=3)
    V.end_of_turn_acts(st)
    f = st.player.fv2
    assert f.ledger["paid"] == 1
    assert f.ledger["spent"] == 0 and f.spent_this_turn == 0
    assert f.ledger["clorinde_procs"] == 0          # her line did not fire
    assert f.ledger["acts"]["navia"] == 1
    assert _dealt(st) == V.ACT_CLORINDE_DAMAGE      # Navia read 0 spent


def test_a_short_star_skips_stays_and_spends_nothing():
    st = _state(["neuvillette"], fanfare=1)
    V.end_of_turn_acts(st)
    f = st.player.fv2
    assert f.fanfare == 1 and f.stage == ["neuvillette"]
    assert f.ledger["star_skips"]["neuvillette"] == 1
    assert f.ledger["paid"] == 0 and _dealt(st) == 0


def test_fanfare_has_no_fade_and_no_cap():
    st = _state(["usher"], fanfare=40)
    V.end_of_turn_acts(st)
    V.turn_open(st)
    assert st.player.fv2.fanfare == 40


# ---------------------------------------------------------------------------
# Rule 3: the Bow -- a free act, then 1 Fanfare after it.
# ---------------------------------------------------------------------------

def test_a_bow_is_a_free_act_then_one_fanfare():
    st = _state(["neuvillette", "clorinde", "charlotte"], fanfare=0)
    assert V.summon(st, "sigewinne") == "evict"      # guest onto three guests
    f = st.player.fv2
    assert f.stage == ["clorinde", "charlotte", "sigewinne"]
    assert _dealt(st) == V.ACT_NEUVILLETTE_DAMAGE    # unpaid: the Bow is free
    assert f.ledger["paid"] == 0 and f.fanfare == V.BOW_FANFARE
    order = [e["event"] for e in st.log if e["event"] in ("fv2_act",
                                                          "fv2_gain")]
    assert order == ["fv2_act", "fv2_gain"]


def test_a_second_copy_of_a_guest_bows_it_and_returns_it():
    st = _state(["clorinde", "usher"])
    assert V.summon(st, "clorinde") == "repeat"
    f = st.player.fv2
    assert f.stage == ["clorinde", "usher"]
    assert f.ledger["bows"]["clorinde"] == 1 and f.fanfare == 1
    assert _dealt(st) == V.ACT_CLORINDE_DAMAGE


# ---------------------------------------------------------------------------
# Rule 4: overflow. Salon summons never evict guests.
# ---------------------------------------------------------------------------

def test_a_full_stage_bows_the_front_most_salon_member():
    st = _state(["neuvillette", "usher", "chevalmarin"])
    assert V.summon(st, "crabaletta") == "evict"
    assert st.player.fv2.stage == ["neuvillette", "chevalmarin", "crabaletta"]
    assert st.player.fv2.ledger["bows"] == {"usher": 1}


def test_a_guest_summon_onto_a_mixed_stage_also_bows_a_salon_member():
    st = _state(["navia", "usher", "clorinde"])
    V.summon(st, "charlotte")
    assert st.player.fv2.stage == ["navia", "clorinde", "charlotte"]


@pytest.mark.parametrize("stage", [
    ["usher", "neuvillette", "clorinde"], ["neuvillette", "usher", "clorinde"],
    ["neuvillette", "clorinde", "usher"], ["navia", "charlotte", "sigewinne"],
    ["chevalmarin", "usher", "navia"]])
@pytest.mark.parametrize("member", V.SALON)
def test_overflow_never_evicts_a_guest_for_a_salon_summon(stage, member):
    st = _state(stage)
    guests = [m for m in stage if m in V.GUESTS]
    V.summon(st, member)
    after = st.player.fv2.stage
    assert all(g in after for g in guests)
    assert sum(st.player.fv2.ledger["bows"][g] for g in guests) == 0


def test_the_walk_on_is_one_act_and_one_fanfare_without_a_seat():
    st = _state(["neuvillette", "clorinde", "charlotte"])
    assert V.summon(st, "usher") == "walk_on"
    f = st.player.fv2
    assert f.stage == ["neuvillette", "clorinde", "charlotte"]
    assert f.ledger["acts"]["usher"] == 1           # one act, not act + Bow
    assert st.player.block == V.ACT_USHER_BLOCK
    assert f.fanfare == 1 and f.ledger["walk_ons"] == 1


def test_a_guest_summon_onto_three_guests_bows_the_front_guest():
    st = _state(["navia", "clorinde", "charlotte"])
    V.summon(st, "neuvillette")
    assert st.player.fv2.stage == ["clorinde", "charlotte", "neuvillette"]
    assert st.player.fv2.ledger["bows"] == {"navia": 1}


def test_lyney_is_not_in_the_slice():
    st = _state()
    for absent in ("lyney", "lynette", "chevreuse", "wriothesley"):
        with pytest.raises(ValueError, match="not in the re-founding"):
            V.summon(st, absent)
        assert not any(s.member == absent for s in V.CARDS.values())


# ---------------------------------------------------------------------------
# The flow counts: hold through the end of the turn, reset at its start.
# ---------------------------------------------------------------------------

def test_flow_counts_persist_through_end_of_turn_acts_and_reset_at_turn_start():
    st = _state(["navia"], fanfare=5)
    _play(st, "fv2_curtain_rise")                    # Spend 3
    f = st.player.fv2
    assert f.spent_this_turn == 3
    before = _dealt(st)
    V.end_of_turn_acts(st)
    assert _dealt(st) - before == V.NAVIA_PER_SPENT * 3
    assert f.spent_this_turn == 3
    V.turn_open(st)
    assert f.spent_this_turn == 0 and f.gained_this_turn == 0


def test_gained_this_turn_counts_bows_and_charlotte_until_turn_start():
    st = _state(["charlotte"])
    _play(st, "fv2_rising_applause")
    V.end_of_turn_acts(st)
    assert st.player.fv2.gained_this_turn == 3 + V.CHARLOTTE_GAIN
    V.turn_open(st)
    assert st.player.fv2.gained_this_turn == 0


def test_ousia_reads_gained_and_pneuma_reads_spent_not_paid():
    st = _state(["clorinde"], fanfare=4)
    V.cue(st, 0)                                     # pays 1: not spent
    _play(st, "fv2_pneuma_refrain")
    assert st.player.block == 4
    _play(st, "fv2_rising_applause")
    hp0 = st.enemies[0].hp
    _play(st, "fv2_ousia_surge")
    assert hp0 - st.enemies[0].hp == 4 + 2 * 3


# ---------------------------------------------------------------------------
# Spend on cards, and Clorinde's line.
# ---------------------------------------------------------------------------

def test_curtain_rise_spends_three_for_seventeen_and_clorinde_answers():
    st = _state(["clorinde"], fanfare=3)
    _play(st, "fv2_curtain_rise")
    f = st.player.fv2
    assert f.fanfare == 0 and f.ledger["spent"] == 3
    assert f.ledger["clorinde_procs"] == 1
    assert _dealt(st) == 17 + V.CLORINDE_SPEND_DAMAGE


def test_curtain_rise_short_deals_seven():
    st = _state([], fanfare=2)
    _play(st, "fv2_curtain_rise")
    assert _dealt(st) == 7 and st.player.fv2.fanfare == 2


def test_bravura_spends_all_and_zero_is_no_spend():
    st = _state(["clorinde"], fanfare=0)
    _play(st, "fv2_bravura")
    assert _dealt(st) == 4 and st.player.fv2.ledger["spends"] == 0
    st = _state([], fanfare=5)
    _play(st, "fv2_bravura")
    assert _dealt(st) == 4 + 2 * 5 and st.player.fv2.fanfare == 0


# ---------------------------------------------------------------------------
# Rule 6: Rehearsal scales damage and Block acts, never Fanfare or draw.
# ---------------------------------------------------------------------------

def test_rehearsal_scales_damage_and_block_acts_only():
    st = _state(["usher", "crabaletta", "charlotte"], deck=5)
    _play(st, "fv2_dress_rehearsal")
    assert st.player.fv2.rehearsal == 1
    V.end_of_turn_acts(st)
    assert st.player.block == V.ACT_USHER_BLOCK + 1
    assert _dealt(st) == V.ACT_CRABALETTA_DAMAGE + 1
    assert st.player.fv2.fanfare == V.CHARLOTTE_GAIN     # not scaled
    hand = len(st.player.hand)
    V.turn_start(st)
    assert len(st.player.hand) == hand + V.CHARLOTTE_DRAW  # not scaled


def test_rehearsal_does_not_scale_clorindes_line():
    st = _state(["clorinde"], fanfare=3)
    st.player.fv2.rehearsal = 2
    V.spend(st, 3)
    assert _dealt(st) == V.CLORINDE_SPEND_DAMAGE


# ---------------------------------------------------------------------------
# Rule 7: Cue -- the chosen performer acts now; a star pays.
# ---------------------------------------------------------------------------

def test_a_cue_acts_the_chosen_performer_and_a_star_pays():
    st = _state(["usher", "clorinde"], fanfare=1,
                decider=Fixed(cue=1))
    _play(st, "fv2_stage_whisper")
    f = st.player.fv2
    assert f.ledger["cues_on"] == {"clorinde": 1}
    assert f.ledger["paid"] == 1 and _dealt(st) == V.ACT_CLORINDE_DAMAGE


def test_a_short_star_cued_skips_and_the_card_still_blocks():
    st = _state(["neuvillette"], fanfare=0, decider=Fixed(cue=0))
    _play(st, "fv2_places_everyone")
    assert st.player.block == 5
    assert st.player.fv2.ledger["star_skips"]["neuvillette"] == 1
    assert _dealt(st) == 0


def test_step_forward_moves_the_chosen_performer():
    st = _state(["neuvillette", "charlotte"], decider=Fixed(front=1))
    _play(st, "fv2_step_forward")
    assert st.player.fv2.stage == ["charlotte", "neuvillette"]
    assert st.player.block == 3


# ---------------------------------------------------------------------------
# The guests' lines and acts (sec.2 / sec.8).
# ---------------------------------------------------------------------------

def test_escoffier_makes_only_the_first_salon_summon_card_free():
    st = _state(["escoffier"])
    first = V.make_card("fv2_take_the_stage")
    second = V.make_card("fv2_gentilhomme_usher")
    assert combat.card_cost(st, first) == 0
    _play(st, "fv2_take_the_stage", energy=0)
    assert combat.card_cost(st, second) == 1
    V.turn_open(st)
    assert combat.card_cost(st, second) == 0
    # a non-summon card is never free, and without her nothing is
    assert combat.card_cost(st, V.make_card("fv2_encore")) == 1
    assert combat.card_cost(_state([]), second) == 1


def test_escoffiers_act_pays_two_and_the_salon_acts():
    st = _state(["usher", "escoffier", "crabaletta"], fanfare=2)
    V.cue(st, 1)
    assert st.player.fv2.ledger["paid"] == 2
    assert st.player.block == V.ACT_USHER_BLOCK
    assert _dealt(st) == V.ACT_CRABALETTA_DAMAGE


def test_neuvillette_adds_three_to_a_hydro_card_only():
    st = _state(["neuvillette"])
    _play(st, "fv2_mademoiselle_crabaletta")       # a damaging Skill: Hydro
    assert _dealt(st) == 4 + V.NEUVILLETTE_HYDRO_BONUS
    st = _state(["neuvillette"])
    _play(st, "fv2_encore")                          # an Attack: no element
    assert _dealt(st) == 7


def test_charlotte_draws_one_more_at_the_start_of_the_turn():
    st = _state(["charlotte"], deck=3)
    V.turn_start(st)
    assert len(st.player.hand) == 1


def test_sigewinne_blocks_three_plus_two_per_hp_loss():
    st = _state(["sigewinne"])
    V.summon(st, "usher")
    st.player_damage_events += 2
    V.end_of_turn_acts(st)
    assert st.player.block == (V.ACT_SIGEWINNE_BLOCK + 2 * 2
                               + V.ACT_USHER_BLOCK)
    st.player.block = 0
    V.end_of_turn_acts(st)
    assert st.player.block == V.ACT_SIGEWINNE_BLOCK + V.ACT_USHER_BLOCK


def test_thunderous_applause_draws_on_every_bow_and_walk_on():
    st = _state(["navia", "clorinde", "charlotte"], deck=5)
    _play(st, "fv2_thunderous_applause")
    hand = len(st.player.hand)
    V.summon(st, "usher")                            # a walk-on is a Bow
    assert len(st.player.hand) == hand + 1


def test_guest_cards_give_the_papers_fanfare():
    for cid, gain in (("fv2_guest_star_neuvillette", 4),
                      ("fv2_guest_star_clorinde", 2),
                      ("fv2_guest_star_escoffier", 3),
                      ("fv2_guest_star_navia", 2),
                      ("fv2_guest_star_charlotte", 0),
                      ("fv2_guest_star_sigewinne", 0)):
        st = _state([])
        _play(st, cid)
        assert st.player.fv2.fanfare == gain, cid
        assert st.player.fv2.stage == [V.CARDS[cid].member]


# ---------------------------------------------------------------------------
# A separate arm: today's Furina is untouched.
# ---------------------------------------------------------------------------

def test_the_slice_hooks_are_inert_for_todays_furina():
    p = Player(hp=78, max_hp=78, character_id="furina")
    st = CombatState(player=p, enemies=[Enemy(hp=10, max_hp=10, name="x",
                                              intents=[{"kind": "block",
                                                        "amount": 0}])],
                     rng=random.Random(0))
    assert not V.live(p)
    V.turn_open(st)
    V.turn_start(st)
    V.end_of_turn_acts(st)
    assert not hasattr(p, "fv2") and not st.log
    slice_player = V.build_player(list(V.STARTER_IDS))
    assert not furina_stage.active(slice_player)


def test_every_probe_deck_is_slice_rows_and_runs():
    for name in H.PROBES:
        for cid in H.deck(name):
            V.make_card(cid)
        r = H.run_one(name, 7)
        assert r["fights"], name
