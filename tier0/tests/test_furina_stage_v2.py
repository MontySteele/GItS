"""FURINA'S STAGE on the re-founded rules (`tier0/engine/furina_stage.py`).

`review/active/furina-refounding-2026-10-03.md`: sec.1's rules as sec.8
amends them, sec.2's cast, sec.10's sheet (`docs/prototype-surface.yaml`'s
`proto_fs_*` rows). One pin per rule edge, mirroring the sim slice's
(`test_furina_v2_slice.py`) against Furina's own arm, then the rows, guests
and Powers the slice did not have. NOTHING MEASURED HERE IS QUOTABLE.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects
from tier0.engine import furina_stage as FS
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.pilot import policy


class Fixed:
    """A decider that always names one seat (or a fixed choice)."""

    def __init__(self, cue=0, front=None, bow=0, arkhe="ousia", spend=True):
        self.cue, self.front, self.bow = cue, front, bow
        self.arkhe, self.spend = arkhe, spend

    def cue_target(self, state):
        return self.cue

    def front_target(self, state):
        return self.front

    def final_bow_target(self, state):
        return self.bow

    def arkhe_choice(self, state):
        return self.arkhe

    def spend_mode(self, state, modes):
        spend = next(i for i, m in enumerate(modes)
                     if FS.spend_mode_amount(m) is not None)
        keep = next(i for i in range(len(modes)) if i != spend)
        if self.spend and FS.can_pay(state.player,
                                     FS.spend_mode_amount(modes[spend])):
            return spend
        return keep


def _enemy(hp=500, name="paper", intents=None):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=intents or [{"kind": "block", "amount": 0}])


def _state(stage=(), fanfare=0, enemies=1, hp=500, deck=0, decider=None,
           turn=1):
    p = Player(hp=200, max_hp=200, character_id="furina", element="hydro",
               cadence="skill")
    p.stage = list(stage)
    p.stage_fanfare = fanfare
    p.stage_decider = decider or Fixed()
    p.draw_pile = [Card(id=f"filler{i}", name="f", cost=0, type="skill")
                   for i in range(deck)]
    st = CombatState(player=p,
                     enemies=[_enemy(hp, f"paper{i}") for i in range(enemies)],
                     rng=random.Random(0))
    st.turn = turn
    return st


def _play(st, cid, energy=10):
    card = loader.get_card(cid)
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


def _dealt(st):
    return sum(e.max_hp - e.hp for e in st.enemies)


def _led(st):
    return FS.ledger(st)


# ---------------------------------------------------------------------------
# The numbers: the brief's names and values (the C# mirrors them by name).
# ---------------------------------------------------------------------------

def test_the_cast_numbers_are_the_sheets():
    assert (FS.SEATS, FS.SOLD_OUT_SEATS, FS.CASTING_AGENT_OFFER,
            FS.BOW_FANFARE) == (3, 4, 3, 1)
    assert (FS.ACT_USHER_BLOCK, FS.ACT_CHEVALMARIN_DAMAGE,
            FS.ACT_CRABALETTA_DAMAGE) == (4, 2, 5)
    assert (FS.ACT_NEUVILLETTE_PRICE, FS.ACT_NEUVILLETTE_DAMAGE,
            FS.NEUVILLETTE_HYDRO_BONUS) == (2, 7, 2)
    assert (FS.ACT_CLORINDE_PRICE, FS.ACT_CLORINDE_DAMAGE,
            FS.CLORINDE_SPEND_DAMAGE) == (1, 6, 4)
    assert (FS.ACT_LYNEY_PRICE, FS.TRICK_DAMAGE, FS.ACT_ESCOFFIER_PRICE,
            FS.NAVIA_PER_SPENT) == (1, 4, 2, 2)
    assert (FS.ACT_CHARLOTTE_GAIN, FS.CHARLOTTE_DRAW, FS.ACT_LYNETTE_DAMAGE,
            FS.ACT_CHEVREUSE_PRICE, FS.ACT_CHEVREUSE_ENERGY) == (1, 1, 3, 2, 1)
    assert (FS.ACT_SIGEWINNE_BLOCK, FS.SIGEWINNE_PER_HP_LOSS,
            FS.ACT_WRIOTHESLEY_DAMAGE, FS.WRIOTHESLEY_PER_BLOCKED,
            FS.PNEUMA_FANFARE) == (3, 2, 4, 1, 2)
    assert FS.STAR_PRICE == {"neuvillette": 2, "clorinde": 1, "lyney": 1,
                             "escoffier": 2, "navia": 0}


@pytest.mark.parametrize("retired", [
    "OPENING_FANFARE", "SUMMON_FANFARE", "LEAD_REGEN", "REFILL_AMOUNT",
    "FADE_DIVISOR", "ACT_CLORINDE_TAX", "ACT_WRIOTHESLEY_BASE",
    "ACT_WRIOTHESLEY_RATE", "ACT_WRIOTHESLEY_BLOCKED_RATE",
    "ACT_SIGEWINNE_HEAL_FLOOR", "ACT_CHARLOTTE_GIFT", "ACT_LYNEY_DAMAGE",
    "ACT_ESCOFFIER_GIFT", "ACT_ESCOFFIER_DAMAGE", "PNEUMA_LEAD_REGAIN",
    "FRONT_HOLDER", "absorb", "fade", "settle_hit", "lead", "back"])
def test_the_retired_machinery_is_gone(retired):
    assert not hasattr(FS, retired)


@pytest.mark.parametrize("op", [
    "stage_scene_change", "stage_perform_lead", "stage_spend_back_all",
    "stage_reverse", "stage_whisper", "stage_intermission",
    "stage_spend_front_all"])
def test_the_retired_ops_are_gone(op):
    assert op not in effects.OPS


def test_the_retired_counts_and_predicates_are_gone():
    for token in ("stage_lead_fanfare", "stage_back_fanfare"):
        assert token not in effects.RUNTIME_COUNT_NAMES
    assert "stage_front_hit" not in effects.PREDICATE_NAMES
    for token in ("stage_spent", "fanfare_gained", "fanfare_spent",
                  "stage_count", "stage_bows"):
        assert token in effects.RUNTIME_COUNT_NAMES


# ---------------------------------------------------------------------------
# Rule 1: three seats, Usher opens, acts front to back.
# ---------------------------------------------------------------------------

def test_salon_solitaire_opens_with_usher_once():
    st = _state()
    FS.turn_start(st)
    assert st.player.stage == ["usher"]
    st.player.stage = ["crabaletta"]
    FS.turn_start(st)
    assert st.player.stage == ["crabaletta"]
    st = _state(turn=2)
    FS.turn_start(st)
    assert st.player.stage == []
    assert st.player.stage_fanfare == 0


def test_a_real_fight_opens_with_usher_and_no_fanfare():
    p = loader.build_player("furina")
    st = CombatState(player=p, enemies=[_enemy()], rng=random.Random(0))
    st.turn = 1
    FS.turn_start(st)
    assert p.stage == ["usher"] and p.stage_fanfare == 0


def test_acts_run_front_to_back_so_seat_order_funds_a_star():
    st = _state(["charlotte", "neuvillette"], fanfare=1)
    FS.end_of_turn_acts(st)
    assert _led(st)["star_acts"]["neuvillette"] == 1
    assert st.player.stage_fanfare == 0
    st = _state(["neuvillette", "charlotte"], fanfare=1)
    FS.end_of_turn_acts(st)
    assert _led(st)["star_skips"]["neuvillette"] == 1
    assert st.player.stage_fanfare == 2


def test_the_trio_acts():
    st = _state(["usher", "chevalmarin", "crabaletta"], enemies=2)
    FS.end_of_turn_acts(st)
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert _dealt(st) == 2 * FS.ACT_CHEVALMARIN_DAMAGE + FS.ACT_CRABALETTA_DAMAGE


def test_no_trio_act_carries_an_element():
    st = _state(["chevalmarin", "crabaletta"])
    FS.end_of_turn_acts(st)
    assert st.enemies[0].aura is None
    assert not [e for e in st.log if e["event"] == "reaction"]


def test_performers_take_no_hits_and_her_block_meets_the_attack():
    st = _state(["usher"], fanfare=5,
                enemies=1)
    st.enemies[0].intents = [{"kind": "attack", "amount": 10}]
    hp = st.player.hp
    combat._enemy_turn(st, st.enemies[0])
    assert st.player.hp == hp - 10
    assert st.player.stage == ["usher"] and st.player.stage_fanfare == 5


def test_a_performance_carries_no_strength():
    st = _state(["crabaletta"])
    st.player.powers["strength"] = 5
    FS.end_of_turn_acts(st)
    assert _dealt(st) == FS.ACT_CRABALETTA_DAMAGE


# ---------------------------------------------------------------------------
# Rule 5: one number; a star pays, a payment is not a Spend; short skips.
# ---------------------------------------------------------------------------

def test_a_star_payment_is_not_a_spend():
    st = _state(["clorinde", "navia"], fanfare=3)
    FS.end_of_turn_acts(st)
    led = _led(st)
    assert led["paid"] == {"clorinde": 1}
    assert led["spent"] == 0 and st.player.stage_spent_this_turn == 0
    assert led["clorinde_procs"] == 0
    assert led["acts"]["navia"] == 1
    assert _dealt(st) == FS.ACT_CLORINDE_DAMAGE      # Navia read 0 spent


def test_a_short_star_skips_stays_and_spends_nothing():
    st = _state(["neuvillette"], fanfare=1)
    FS.end_of_turn_acts(st)
    assert st.player.stage_fanfare == 1 and st.player.stage == ["neuvillette"]
    assert _led(st)["star_skips"]["neuvillette"] == 1
    assert _led(st)["paid"] == {} and _dealt(st) == 0


def test_fanfare_has_no_fade_and_no_cap():
    st = _state(["usher"], fanfare=40)
    FS.end_of_turn_acts(st)
    FS.turn_open(st)
    st.turn = 2
    FS.turn_start(st)
    assert st.player.stage_fanfare == 40


def test_the_ledger_balances():
    st = _state(["clorinde", "charlotte"], fanfare=5)
    _play(st, "proto_fs_curtain_rise")
    _play(st, "proto_fs_standing_ovation")
    FS.end_of_turn_acts(st)
    led = _led(st)
    assert FS.ledger_expected_end(led) == st.player.stage_fanfare


# ---------------------------------------------------------------------------
# Rule 3: the Bow -- a free act, then 1 Fanfare after it.
# ---------------------------------------------------------------------------

def test_a_bow_is_a_free_act_then_one_fanfare():
    st = _state(["neuvillette", "clorinde", "charlotte"], fanfare=0)
    assert FS.summon(st, "sigewinne") == "evict"
    assert st.player.stage == ["clorinde", "charlotte", "sigewinne"]
    # Unpaid (the Bow is free), and no +2: she left before her Bow act.
    assert _dealt(st) == FS.ACT_NEUVILLETTE_DAMAGE
    assert _led(st)["paid"] == {} and st.player.stage_fanfare == FS.BOW_FANFARE
    order = [e["event"] for e in st.log
             if e["event"] in ("stage_act", "stage_gain")]
    assert order == ["stage_act", "stage_gain"]


def test_a_second_copy_of_a_guest_bows_it_and_it_keeps_its_seat():
    st = _state(["clorinde", "usher"])
    _play(st, "proto_fs_guest_star_clorinde")
    assert st.player.stage == ["clorinde", "usher"]
    assert _led(st)["bows"]["clorinde"] == 1
    assert st.player.stage_fanfare == FS.BOW_FANFARE + 2   # the card's 2 too
    assert _dealt(st) == FS.ACT_CLORINDE_DAMAGE


def test_bows_count_for_da_capo():
    st = _state(["usher", "crabaletta"])
    FS.curtain_call(st)
    assert st.player.stage_bows == 2
    hp = st.enemies[0].hp
    _play(st, "proto_fs_da_capo")
    assert hp - st.enemies[0].hp == 5 + 2 * 2


# ---------------------------------------------------------------------------
# Rule 4: overflow. Salon summons never evict guests.
# ---------------------------------------------------------------------------

def test_a_full_stage_bows_the_front_most_salon_member():
    st = _state(["neuvillette", "usher", "chevalmarin"])
    assert FS.summon(st, "crabaletta") == "evict"
    assert st.player.stage == ["neuvillette", "chevalmarin", "crabaletta"]
    assert dict(_led(st)["bows"]) == {"usher": 1}


def test_a_guest_summon_onto_a_mixed_stage_also_bows_a_salon_member():
    st = _state(["navia", "usher", "clorinde"])
    FS.summon(st, "charlotte")
    assert st.player.stage == ["navia", "clorinde", "charlotte"]


@pytest.mark.parametrize("stage", [
    ["usher", "neuvillette", "clorinde"], ["neuvillette", "usher", "clorinde"],
    ["neuvillette", "clorinde", "usher"], ["navia", "charlotte", "sigewinne"],
    ["chevalmarin", "usher", "navia"]])
@pytest.mark.parametrize("member", FS.SALON)
def test_overflow_never_evicts_a_guest_for_a_salon_summon(stage, member):
    st = _state(stage)
    guests = [m for m in stage if m in FS.GUESTS]
    FS.summon(st, member)
    assert all(g in st.player.stage for g in guests)
    assert sum(_led(st)["bows"][g] for g in guests) == 0


def test_the_walk_on_is_one_act_and_one_fanfare_without_a_seat():
    st = _state(["neuvillette", "clorinde", "charlotte"])
    assert FS.summon(st, "usher") == "walk_on"
    assert st.player.stage == ["neuvillette", "clorinde", "charlotte"]
    assert _led(st)["acts"]["usher"] == 1
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert st.player.stage_fanfare == 1 and _led(st)["walk_ons"] == 1


def test_a_guest_summon_onto_three_guests_bows_the_front_guest():
    st = _state(["navia", "clorinde", "charlotte"])
    FS.summon(st, "neuvillette")
    assert st.player.stage == ["clorinde", "charlotte", "neuvillette"]
    assert dict(_led(st)["bows"]) == {"navia": 1}


def test_sold_out_opens_a_fourth_seat():
    st = _state(["usher", "chevalmarin", "crabaletta"])
    st.player.powers[FS.SOLD_OUT] = 1
    assert FS.capacity(st.player) == 4
    assert FS.summon(st, "clorinde") == "seated"
    assert len(st.player.stage) == 4
    assert FS.summon(st, "usher") == "evict"


def test_an_unknown_performer_is_a_loud_error():
    with pytest.raises(ValueError):
        FS.summon(_state(), "furina")


# ---------------------------------------------------------------------------
# The flow counts: hold through the end of the turn, reset at its start.
# ---------------------------------------------------------------------------

def test_flow_counts_persist_through_end_of_turn_acts_and_reset_at_turn_start():
    st = _state(["navia"], fanfare=5)
    _play(st, "proto_fs_curtain_rise")                     # Spend 3
    assert st.player.stage_spent_this_turn == 3
    before = _dealt(st)
    FS.end_of_turn_acts(st)
    assert _dealt(st) - before == FS.NAVIA_PER_SPENT * 3
    assert st.player.stage_spent_this_turn == 3
    FS.turn_open(st)
    assert st.player.stage_spent_this_turn == 0
    assert st.player.stage_gained_this_turn == 0


def test_gained_this_turn_counts_bows_and_charlotte_until_turn_start():
    st = _state(["charlotte"])
    _play(st, "proto_fs_standing_ovation")                 # Gain 3
    FS.end_of_turn_acts(st)
    assert st.player.stage_gained_this_turn == 3 + FS.ACT_CHARLOTTE_GAIN
    FS.turn_open(st)
    assert st.player.stage_gained_this_turn == 0


def test_ousia_surge_reads_gained_and_pneuma_refrain_reads_spent_not_paid():
    st = _state(["clorinde"], fanfare=4)
    FS.cue(st, index=0)                                    # pays 1: not spent
    _play(st, "proto_fs_pneuma_refrain")
    assert st.player.block == 4
    _play(st, "proto_fs_standing_ovation")
    hp0 = st.enemies[0].hp
    _play(st, "proto_fs_ousia_surge")
    assert hp0 - st.enemies[0].hp == 4 + 2 * 3


def test_bring_the_house_down_reads_the_fanfare_spent_this_turn():
    st = _state([], fanfare=5, enemies=2)
    _play(st, "proto_fs_curtain_rise")                     # Spend 3 (17)
    before = _dealt(st)
    _play(st, "proto_fs_bring_the_house_down")
    assert _dealt(st) - before == 2 * 3 * 3


# ---------------------------------------------------------------------------
# Spend on cards, and Clorinde's line.
# ---------------------------------------------------------------------------

def test_curtain_rise_spends_three_for_seventeen_and_clorinde_answers():
    st = _state(["clorinde"], fanfare=3)
    _play(st, "proto_fs_curtain_rise")
    assert st.player.stage_fanfare == 0 and _led(st)["spent"] == 3
    assert _led(st)["clorinde_procs"] == 1
    assert _dealt(st) == 17 + FS.CLORINDE_SPEND_DAMAGE


def test_curtain_rise_short_deals_seven_and_the_mode_is_not_offered():
    st = _state([], fanfare=2)
    card = loader.get_card("proto_fs_curtain_rise")
    modes = card.effects[0]["modes"]
    assert not FS.mode_offered(st.player, modes[1])
    assert FS.mode_refusal(st.player, modes[1])
    _play(st, "proto_fs_curtain_rise")
    assert _dealt(st) == 7 and st.player.stage_fanfare == 2


def test_bravura_spends_all_and_zero_is_no_spend():
    st = _state(["clorinde"], fanfare=0)
    _play(st, "proto_fs_bravura")
    assert _dealt(st) == 6 and _led(st)["spends"] == 0
    assert _led(st)["clorinde_procs"] == 0
    st = _state([], fanfare=5)
    _play(st, "proto_fs_bravura")
    assert _dealt(st) == 6 + 3 * 5 and st.player.stage_fanfare == 0


def test_the_pilot_takes_a_spend_mode_when_it_can_pay():
    d = policy.FURINA_STAGE_DECIDER
    modes = loader.get_card("proto_fs_curtain_rise").effects[0]["modes"]
    assert d.spend_mode(_state([], fanfare=3), modes) == 1
    assert d.spend_mode(_state([], fanfare=2), modes) == 0
    toast = loader.get_card("proto_fs_raise_a_toast").effects[0]["modes"]
    assert d.spend_mode(_state([], fanfare=9), toast) == 0


def test_raise_a_toast_draws_either_way_and_share_the_spotlight_needs_an_ally():
    st = _state([], fanfare=9, deck=3, decider=Fixed(spend=True))
    _play(st, "proto_fs_raise_a_toast")
    assert len(st.player.hand) == 1 and st.player.stage_fanfare == 5
    st = _state([], fanfare=4)
    _play(st, "proto_fs_share_the_spotlight")
    assert st.player.stage_fanfare == 4
    assert any(e["event"] == "coop_no_other_player" for e in st.log)


# ---------------------------------------------------------------------------
# Rule 6: Rehearsal scales damage and Block acts, never Fanfare or draw.
# ---------------------------------------------------------------------------

def test_rehearsal_scales_damage_and_block_acts_only():
    st = _state(["usher", "crabaletta", "charlotte"], deck=5)
    _play(st, "proto_fs_counterclaim")                     # Dress Rehearsal
    assert FS.rehearsal(st.player) == 1
    FS.end_of_turn_acts(st)
    assert st.player.block == FS.ACT_USHER_BLOCK + 1
    assert _dealt(st) == FS.ACT_CRABALETTA_DAMAGE + 1
    assert st.player.stage_fanfare == FS.ACT_CHARLOTTE_GAIN
    hand = len(st.player.hand)
    st.turn = 2
    FS.turn_start(st)
    assert len(st.player.hand) == hand + FS.CHARLOTTE_DRAW


def test_rehearsal_does_not_scale_clorindes_line():
    st = _state(["clorinde"], fanfare=3)
    st.player.powers[FS.REHEARSAL] = 2
    FS.spend(st, 3)
    assert _dealt(st) == FS.CLORINDE_SPEND_DAMAGE


def test_premiere_season_gains_rehearsal_at_each_turn_start():
    st = _state([], turn=2)
    _play(st, "proto_fs_double_casting")
    assert FS.rehearsal(st.player) == 0
    FS.turn_start(st)
    FS.turn_start(st)
    assert FS.rehearsal(st.player) == 2


# ---------------------------------------------------------------------------
# Rule 7: Cue -- the chosen performer acts now; a star pays.
# ---------------------------------------------------------------------------

def test_a_cue_acts_the_chosen_performer_and_a_star_pays():
    st = _state(["usher", "clorinde"], fanfare=1, decider=Fixed(cue=1))
    _play(st, "proto_fs_stage_whisper")
    assert dict(_led(st)["cues_on"]) == {"clorinde": 1}
    assert _led(st)["paid"] == {"clorinde": 1}
    assert _dealt(st) == FS.ACT_CLORINDE_DAMAGE


def test_a_short_star_cued_skips_and_the_card_still_blocks():
    st = _state(["neuvillette"], fanfare=0, decider=Fixed(cue=0))
    _play(st, "proto_fs_interposition")                    # Places, Everyone!
    assert st.player.block == 5
    assert _led(st)["star_skips"]["neuvillette"] == 1
    assert _dealt(st) == 0


def test_a_cue_on_an_empty_stage_does_only_the_plain_part():
    st = _state([])
    _play(st, "proto_fs_plot_twist")                       # Encore!
    assert _dealt(st) == 7 and _led(st)["cue_whiffs"] == 1


def test_bis_cues_one_performer_twice_and_a_star_pays_each_time():
    st = _state(["usher", "clorinde"], fanfare=2, decider=Fixed(cue=1))
    _play(st, "proto_fs_bis")
    assert _led(st)["paid"] == {"clorinde": 2}
    assert _dealt(st) == 2 * FS.ACT_CLORINDE_DAMAGE
    assert st.player.block == 0


def test_step_forward_moves_the_chosen_performer():
    st = _state(["neuvillette", "charlotte"], decider=Fixed(front=1))
    _play(st, "proto_fs_step_forward")
    assert st.player.stage == ["charlotte", "neuvillette"]
    assert st.player.block == 3
    st = _state([])
    _play(st, "proto_fs_step_forward")
    assert st.player.block == 3


def test_the_pilots_cue_names_the_best_act_it_can_pay_for():
    d = policy.FURINA_STAGE_DECIDER
    st = _state(["usher", "neuvillette"], fanfare=0, enemies=3)
    assert d.cue_target(st) == 0                   # he cannot pay
    st = _state(["usher", "neuvillette"], fanfare=2, enemies=3)
    assert d.cue_target(st) == 1
    st = _state(["usher", "charlotte", "neuvillette"])
    assert d.front_target(st) == 1
    assert d.final_bow_target(_state(["navia", "crabaletta"])) == 1


# ---------------------------------------------------------------------------
# The guests' lines and acts (sec.2 / sec.8 / sec.10).
# ---------------------------------------------------------------------------

def test_escoffier_makes_only_the_first_salon_summon_card_free():
    st = _state(["escoffier"])
    first = loader.get_card("proto_fs_salon_debut")        # Take the Stage
    second = loader.get_card("proto_fs_leading_lady")      # Gentilhomme Usher
    assert combat.card_cost(st, first) == 0
    _play(st, "proto_fs_salon_debut", energy=0)
    assert combat.card_cost(st, second) == 1
    FS.turn_open(st)
    assert combat.card_cost(st, second) == 0
    # A conditional summon is not a Salon summon card; without her, nothing.
    assert combat.card_cost(st, loader.get_card(
        "proto_fs_improvised_number")) == 1
    assert combat.card_cost(_state([]), second) == 1


def test_escoffiers_act_pays_two_and_the_salon_acts():
    st = _state(["usher", "escoffier", "crabaletta"], fanfare=2)
    FS.cue(st, index=1)
    assert _led(st)["paid"] == {"escoffier": 2}
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert _dealt(st) == FS.ACT_CRABALETTA_DAMAGE


def test_lyney_makes_the_first_cue_card_free_and_his_act_makes_a_trick():
    st = _state(["lyney"], fanfare=1)
    whisper = loader.get_card("proto_fs_stage_whisper")
    assert combat.card_cost(st, whisper) == 0
    assert combat.card_cost(st, loader.get_card("proto_fs_bis")) == 0
    FS.end_of_turn_acts(st)
    assert _led(st)["paid"] == {"lyney": 1}
    [trick] = [c for c in st.player.hand if c.id == FS.TRICK_ID]
    assert (trick.cost, trick.retain, trick.exhaust) == (0, True, True)
    st.player.hand.remove(trick)
    st.player.hand.append(trick)
    combat.play_card(st, trick)
    assert _dealt(st) == FS.TRICK_DAMAGE
    assert st.enemies[0].aura == "pyro"
    st = _state(["lyney"], fanfare=1)
    _play(st, "proto_fs_plot_twist", energy=0)
    assert combat.card_cost(st, whisper) == 1


def test_lynettes_line_moves_the_first_cued_performer_to_the_front():
    st = _state(["lynette", "usher", "crabaletta"], decider=Fixed(cue=2))
    FS.cue(st)
    assert st.player.stage == ["crabaletta", "lynette", "usher"]
    FS.cue(st, index=2)
    assert st.player.stage == ["crabaletta", "lynette", "usher"]


def test_lynettes_act_finds_an_aura():
    st = _state(["lynette"], enemies=2)
    st.enemies[1].aura = "pyro"
    FS.end_of_turn_acts(st)
    assert st.enemies[0].hp == st.enemies[0].max_hp
    assert st.enemies[1].hp < st.enemies[1].max_hp


def test_neuvillettes_line_adds_two_to_hydro_cards_and_hydro_acts():
    st = _state(["neuvillette"])
    _play(st, "proto_fs_mademoiselle_crabaletta")   # a damaging Skill: Hydro
    assert _dealt(st) == 4 + FS.NEUVILLETTE_HYDRO_BONUS
    st = _state(["neuvillette"], fanfare=2, enemies=2)
    FS.end_of_turn_acts(st)
    assert _dealt(st) == 2 * (FS.ACT_NEUVILLETTE_DAMAGE
                              + FS.NEUVILLETTE_HYDRO_BONUS)


def test_neuvillettes_line_leaves_other_damage_alone():
    st = _state(["neuvillette"])
    _play(st, "proto_fs_plot_twist")                     # an Attack
    assert _dealt(st) == 7
    st = _state(["neuvillette", "clorinde"], fanfare=1)
    FS.cue(st, index=1)
    assert _dealt(st) == FS.ACT_CLORINDE_DAMAGE
    st = _state(["crabaletta"])
    _play(st, "proto_fs_mademoiselle_crabaletta")
    assert _dealt(st) == 4


def test_chevreuse_acts_once_a_turn_and_her_energy_comes_next_turn():
    st = _state(["chevreuse"], fanfare=4)
    FS.end_of_turn_acts(st)
    FS.cue(st, index=0)                                  # already acted
    assert _led(st)["paid"] == {"chevreuse": 2}
    st.player.energy = 0
    FS.turn_open(st)
    st.turn = 2
    FS.turn_start(st)
    assert st.player.energy == FS.ACT_CHEVREUSE_ENERGY


def test_chevreuse_short_does_not_use_her_act_and_her_bow_is_free():
    st = _state(["chevreuse"], fanfare=1)
    FS.end_of_turn_acts(st)
    assert not st.player.stage_chevreuse_acted
    assert st.player.stage_energy_next == 0
    st.player.stage_fanfare = 0
    FS.final_bow(st, 0)
    assert st.player.stage_energy_next == FS.ACT_CHEVREUSE_ENERGY
    assert _led(st)["paid"] == {}


def test_navia_reads_the_fanfare_spent_this_turn_and_zero_is_no_hit():
    st = _state(["navia"])
    FS.end_of_turn_acts(st)
    assert _dealt(st) == 0
    st.player.powers[FS.REHEARSAL] = 3
    FS.end_of_turn_acts(st)
    assert _dealt(st) == 0


def test_charlotte_draws_one_more_at_the_start_of_the_turn():
    st = _state(["charlotte"], deck=3, turn=2)
    FS.turn_start(st)
    assert len(st.player.hand) == 1


def test_sigewinne_blocks_three_plus_two_per_hp_loss():
    st = _state(["sigewinne"])
    FS.summon(st, "usher")
    st.player_damage_events += 2
    FS.end_of_turn_acts(st)
    assert st.player.block == (FS.ACT_SIGEWINNE_BLOCK + 2 * 2
                               + FS.ACT_USHER_BLOCK)
    st.player.block = 0
    FS.end_of_turn_acts(st)
    assert st.player.block == FS.ACT_SIGEWINNE_BLOCK + FS.ACT_USHER_BLOCK


def test_sigewinne_counts_from_her_seating():
    st = _state([])
    st.player_damage_events = 5
    FS.summon(st, "sigewinne")
    FS.end_of_turn_acts(st)
    assert st.player.block == FS.ACT_SIGEWINNE_BLOCK


def test_wriothesley_reads_what_her_block_stopped_since_his_act():
    st = _state([])
    FS.note_blocked(st, 7)                       # before he arrives: nothing
    FS.summon(st, "wriothesley")
    FS.note_blocked(st, 6)
    FS.end_of_turn_acts(st)
    assert _dealt(st) == FS.ACT_WRIOTHESLEY_DAMAGE + 6
    FS.end_of_turn_acts(st)
    assert _dealt(st) == 2 * FS.ACT_WRIOTHESLEY_DAMAGE + 6


def test_the_enemy_hit_loop_feeds_wriothesley():
    st = _state(["wriothesley"])
    st.player.block = 10
    st.enemies[0].intents = [{"kind": "attack", "amount": 6}]
    combat._enemy_turn(st, st.enemies[0])
    assert st.player.stage_wriothesley_blocked == 6


@pytest.mark.parametrize("cid,gain", [
    ("proto_fs_guest_star_neuvillette", 4), ("proto_fs_guest_star_clorinde", 2),
    ("proto_fs_guest_star_escoffier", 3), ("proto_fs_guest_star_navia", 2),
    ("proto_fs_guest_star_lyney", 2), ("proto_fs_guest_star_charlotte", 0),
    ("proto_fs_guest_star_sigewinne", 0), ("proto_fs_guest_star_lynette", 0),
    ("proto_fs_guest_star_chevreuse", 0),
    ("proto_fs_guest_star_wriothesley", 0)])
def test_guest_cards_summon_and_give_their_fanfare(cid, gain):
    st = _state([])
    _play(st, cid)
    assert st.player.stage_fanfare == gain
    assert st.player.stage == [cid[len("proto_fs_guest_star_"):]]


def test_an_upgraded_clorinde_gives_four():
    st = _state([])
    _play(st, "proto_fs_guest_star_clorinde" + upgrades.SUFFIX)
    assert st.player.stage_fanfare == 4


# ---------------------------------------------------------------------------
# Bows that leave, and the Bows that do not.
# ---------------------------------------------------------------------------

def test_final_bow_sends_the_chosen_performer_off_with_its_bow():
    st = _state(["navia", "crabaletta"], decider=Fixed(bow=1))
    _play(st, "proto_fs_final_bow")
    assert st.player.stage == ["navia"]
    assert st.player.block == 8
    assert _dealt(st) == FS.ACT_CRABALETTA_DAMAGE
    assert st.player.stage_fanfare == FS.BOW_FANFARE


def test_final_bow_on_an_empty_stage_only_blocks():
    st = _state([])
    _play(st, "proto_fs_final_bow")
    assert st.player.block == 8 and st.player.stage_fanfare == 0


def test_intermission_draws_after_the_bow():
    st = _state(["usher"], deck=5)
    _play(st, "proto_fs_intermission")
    assert st.player.stage == [] and len(st.player.hand) == 2


def test_a_five_century_act_returns_the_first_leaver_at_the_back():
    st = _state(["usher", "crabaletta"], decider=Fixed(bow=0))
    st.player.powers[FS.FIVE_CENTURY_ACT] = 1
    FS.final_bow(st)
    assert st.player.stage == ["crabaletta", "usher"]
    FS.final_bow(st, 0)                          # once a turn
    assert st.player.stage == ["usher"]
    # The returner acts at the end of the turn with everyone.
    FS.end_of_turn_acts(st)
    assert st.player.block == 2 * FS.ACT_USHER_BLOCK


def test_a_five_century_act_never_returns_an_evicted_performer():
    st = _state(["usher", "chevalmarin", "crabaletta"])
    st.player.powers[FS.FIVE_CENTURY_ACT] = 1
    FS.summon(st, "usher")
    assert st.player.stage == ["chevalmarin", "crabaletta", "usher"]
    assert _led(st)["returns"] == 0


def test_grand_finale_bows_everyone_who_keeps_their_seat():
    st = _state(["usher", "clorinde"], fanfare=0)
    _play(st, "proto_fs_grand_finale")
    assert st.player.stage == ["usher", "clorinde"]
    assert st.player.stage_fanfare == 2 * FS.BOW_FANFARE
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert _dealt(st) == FS.ACT_CLORINDE_DAMAGE          # free


def test_let_the_people_rejoice_spends_all_then_bows_and_keeps_the_cast():
    st = _state(["usher", "crabaletta"], fanfare=5, enemies=2)
    _play(st, "proto_fs_let_the_people_rejoice")
    assert _led(st)["spent"] == 5
    assert st.player.stage == ["usher", "crabaletta"]
    assert st.player.stage_fanfare == 2 * FS.BOW_FANFARE
    assert _dealt(st) == 2 * 2 * 5 + FS.ACT_CRABALETTA_DAMAGE


def test_thunderous_applause_draws_on_every_bow_and_walk_on():
    st = _state(["navia", "clorinde", "charlotte"], deck=5)
    _play(st, "proto_fs_thunderous_applause")
    hand = len(st.player.hand)
    FS.summon(st, "usher")                               # a walk-on is a Bow
    assert len(st.player.hand) == hand + 1
    FS.curtain_call(st)
    assert len(st.player.hand) == hand + 4


def test_gala_premiere_on_a_full_stage_bows_the_salon_for_fanfare():
    st = _state(["usher", "chevalmarin", "crabaletta"])
    _play(st, "proto_fs_gala_premiere")
    assert st.player.stage == ["usher", "chevalmarin", "crabaletta"]
    assert st.player.stage_fanfare == 3 * FS.BOW_FANFARE
    st = _state([])
    _play(st, "proto_fs_gala_premiere")
    assert st.player.stage == ["usher", "chevalmarin", "crabaletta"]


# ---------------------------------------------------------------------------
# The other verbs.
# ---------------------------------------------------------------------------

def test_tutti_acts_everyone_and_endless_waltz_only_the_guests():
    st = _state(["usher", "crabaletta"])
    _play(st, "proto_fs_tutti")
    assert st.player.block == FS.ACT_USHER_BLOCK
    assert _dealt(st) == FS.ACT_CRABALETTA_DAMAGE
    st = _state(["crabaletta", "clorinde"], fanfare=1)
    _play(st, "proto_fs_endless_waltz")
    assert _dealt(st) == 18 + FS.ACT_CLORINDE_DAMAGE


def test_oratrices_verdict_redirects_the_performers_random_picks():
    st = _state(["crabaletta", "clorinde"], fanfare=4, enemies=3)
    _play(st, "proto_fs_oratrices_verdict")
    target = st.player.stage_verdict
    assert target is not None
    FS.end_of_turn_acts(st)
    FS.spend(st, 1)                                      # Clorinde's line
    hit = [e for e in st.enemies if e.hp < e.max_hp]
    assert hit == [target]
    FS.turn_open(st)
    assert st.player.stage_verdict is None


def test_ousia_multiplies_damage_acts_with_rehearsal_and_neuvillette_after():
    st = _state(["crabaletta", "neuvillette", "usher"], fanfare=2,
                decider=Fixed(arkhe="ousia"))
    st.player.powers[FS.REHEARSAL] = 1
    _play(st, "proto_fs_dual_nature")
    FS.end_of_turn_acts(st)
    assert _dealt(st) == ((FS.ACT_CRABALETTA_DAMAGE + 1) * 2
                          + (FS.ACT_NEUVILLETTE_DAMAGE + 1) * 2
                          + FS.NEUVILLETTE_HYDRO_BONUS)
    assert st.player.block == FS.ACT_USHER_BLOCK + 1     # Block is not doubled


def test_pneuma_gains_two_fanfare_and_arkhe_copies_add():
    st = _state([], decider=Fixed(arkhe="pneuma"))
    _play(st, "proto_fs_dual_nature")
    assert st.player.stage_fanfare == FS.PNEUMA_FANFARE
    st = _state(["crabaletta"], turn=2, decider=Fixed(arkhe="ousia"))
    st.player.powers[FS.ARKHE_ALIGNMENT] = 2
    FS.turn_start(st)
    assert st.player.stage_act_damage_mult == 3
    st = _state([], turn=2, decider=Fixed(arkhe="pneuma"))
    st.player.powers[FS.ARKHE_ALIGNMENT] = 2
    FS.turn_start(st)
    assert st.player.stage_fanfare == 2 * FS.PNEUMA_FANFARE


def test_critics_darling_answers_every_change_payments_included():
    st = _state(["clorinde"], fanfare=0)
    st.player.powers[FS.CRITICS_DARLING] = 1
    FS.gain(st, 3)
    assert _dealt(st) == 3
    FS.spend(st, 2)
    assert _dealt(st) == 3 + 2 + FS.CLORINDE_SPEND_DAMAGE
    FS.end_of_turn_acts(st)                              # pays 1
    assert _dealt(st) == 3 + 2 + FS.CLORINDE_SPEND_DAMAGE + 1 \
        + FS.ACT_CLORINDE_DAMAGE


def test_tide_of_applause_gains_on_a_reaction():
    st = _state([])
    st.player.powers[FS.TIDE_OF_APPLAUSE] = 2
    st.enemies[0].aura = "pyro"
    _play(st, "proto_fs_bubble_aria")
    assert st.player.stage_fanfare == 2


def test_season_tickets_and_revolving_stage_at_turn_start():
    st = _state(["crabaletta"], turn=2)
    st.player.powers[FS.SEASON_TICKETS] = 2
    st.player.powers[FS.REVOLVING_STAGE] = 1
    FS.turn_start(st)
    assert st.player.stage_fanfare == 2
    assert _dealt(st) == FS.ACT_CRABALETTA_DAMAGE
    assert _led(st)["cues_on"]["crabaletta"] == 1


def test_star_billing_and_star_turn_after_the_arrival():
    st = _state(["clorinde"], deck=5)
    st.player.powers[FS.STAR_BILLING] = 2
    st.player.powers[FS.STAR_TURN] = 1
    _play(st, "proto_fs_guest_star_neuvillette")         # Gain 4, pays 2
    assert len(st.player.hand) == 2
    assert _led(st)["paid"] == {"neuvillette": 2}
    _play(st, "proto_fs_guest_star_clorinde")            # a repeat: Bow, then
    assert _led(st)["bows"]["clorinde"] == 1             # it acts again
    assert _led(st)["star_acts"]["clorinde"] == 1


def test_full_house_doubles_the_acts_on_a_full_stage_only():
    st = _state(["usher", "usher", "usher"])
    st.player.powers[FS.FULL_HOUSE] = 1
    FS.end_of_turn_acts(st)
    assert st.player.block == 6 * FS.ACT_USHER_BLOCK
    st = _state(["usher", "usher"])
    st.player.powers[FS.FULL_HOUSE] = 1
    FS.end_of_turn_acts(st)
    assert st.player.block == 2 * FS.ACT_USHER_BLOCK


def test_casting_agent_offers_three_different_guest_cards():
    st = _state([])
    got = FS.casting_agent(st)
    assert got.id in FS.GUEST_STAR_CARD_IDS and got.free_this_turn
    [row] = [e for e in st.log if e["event"] == "stage_casting_agent"]
    assert len(set(row["offered"])) == FS.CASTING_AGENT_OFFER
    up = FS.casting_agent(st, upgraded=True)
    assert up.id.endswith(upgrades.SUFFIX)


def test_the_last_act_costs_one_less_per_empty_seat():
    card = loader.get_card(FS.LAST_ACT_ID)
    assert combat.card_cost(_state([]), card) == 0
    assert combat.card_cost(_state(["usher", "usher"]), card) == 2
    st = _state(["usher"])
    st.player.powers[FS.SOLD_OUT] = 1
    assert combat.card_cost(st, card) == 0


def test_the_no_one_on_stage_family():
    st = _state([], deck=5, turn=2)
    st.player.powers[FS.ONE_WOMAN_SHOW] = 1
    st.player.energy = 0
    FS.turn_start(st)
    assert st.player.energy == 1 and len(st.player.hand) == 2
    st = _state([])
    st.player.powers[FS.SOLILOQUY] = 3
    _play(st, "proto_fs_solo_verse")
    assert _dealt(st) == 12 + 3
    st = _state(["usher"])
    _play(st, "proto_fs_solo_verse")
    assert _dealt(st) == 6
    st = _state([])
    _play(st, "proto_fs_improvised_number")
    assert len(st.player.stage) == 1 and st.player.stage[0] in FS.SALON
    st = _state(["usher"])
    _play(st, "proto_fs_improvised_number")
    assert st.player.stage == ["usher"]


def test_ensemble_piece_counts_the_performers():
    st = _state(["usher", "clorinde"])
    _play(st, "proto_fs_ensemble_piece")
    assert _dealt(st) == 2 * 5


def test_take_the_stage_summons_a_salon_member_and_draws():
    st = _state([], deck=2)
    _play(st, "proto_fs_salon_debut")
    assert len(st.player.stage) == 1 and st.player.stage[0] in FS.SALON
    assert len(st.player.hand) == 1 and st.player.stage_fanfare == 0


def test_the_fanfare_cards():
    for cid, gain in (("proto_fs_standing_ovation", 3),
                      ("proto_fs_warm_reception", 3),
                      ("proto_fs_hold_your_places", 2),
                      ("proto_fs_cheered_on", 2),
                      ("proto_fs_singer_of_many_waters", 6)):
        st = _state([], deck=3)
        _play(st, cid)
        assert st.player.stage_fanfare == gain, cid
    st = _state([])
    st.cards_played_this_turn = 0
    _play(st, "proto_fs_opening_number")
    assert st.player.stage_fanfare == 2
    _play(st, "proto_fs_opening_number")
    assert st.player.stage_fanfare == 2
    st = _state([])
    st.enemies[0].aura = "pyro"
    _play(st, "proto_fs_groundswell")
    assert st.player.stage_fanfare == 3


# ---------------------------------------------------------------------------
# The starter and the pool (sec.10).
# ---------------------------------------------------------------------------

def test_the_starter_is_four_strikes_four_defends_and_the_kit_pair():
    assert loader._starter_ids({"id": "furina"}) == list(FS.STARTER_IDS)
    assert FS.STARTER_IDS[:8] == ("strike",) * 4 + ("defend",) * 4
    assert FS.STARTER_IDS[8:] == ("proto_fs_curtain_rise",
                                  "proto_fs_standing_ovation")


def test_the_pool_is_78_at_24_33_21():
    pool = loader.pool_replacement("furina")
    assert len(pool) == len(set(pool)) == 78
    rarity = [loader.get_card(c).rarity for c in pool]
    assert (rarity.count("common"), rarity.count("uncommon"),
            rarity.count("rare")) == (24, 33, 21)


def test_the_two_rarity_moves_are_additions_and_their_old_rows_drops():
    assert {"proto_fs_leading_lady", "proto_fs_double_casting"} <= set(
        FS.POOL_ADDS)
    assert {"guest_list", "matinee_performance"} <= set(FS.POOL_DROPS)
    assert not ({"guest_list", "matinee_performance"} & set(FS.POOL_SUBS))
    assert loader.get_card("proto_fs_leading_lady").rarity == "common"
    lady = loader.get_card("proto_fs_double_casting")
    assert (lady.rarity, lady.type) == ("rare", "power")
    assert not set(FS.POOL_SUBS) & set(FS.POOL_DROPS)


@pytest.mark.parametrize("cid,name", [
    ("proto_fs_plot_twist", "Encore!"),
    ("proto_fs_interposition", "Places, Everyone!"),
    ("proto_fs_counterclaim", "Dress Rehearsal"),
    ("proto_fs_leading_lady", "Gentilhomme Usher"),
    ("proto_fs_double_casting", "Premiere Season"),
    ("proto_fs_quick_cue", "Quick Flourish")])
def test_the_renames_keep_their_ids(cid, name):
    assert loader.get_card(cid).name == name


def test_every_stage_row_is_named_by_one_of_the_maps():
    import yaml
    rows = yaml.safe_load((loader.DOCS_DIR / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    on_sheet = {r["id"]: r.get("replaces") for r in rows
                if str(r["id"]).startswith("proto_fs_")
                and not r.get("multiplayer")}
    named = {**FS.POOL_SUBS, **FS.STARTER_SUBS, **FS.PROMOTED_STARTERS}
    assert set(named.values()) | set(FS.POOL_ADDS) == set(on_sheet)
    assert {p: s for s, p in named.items()} == {
        k: v for k, v in on_sheet.items() if k not in FS.POOL_ADDS}
    assert all(on_sheet[k] is None for k in FS.POOL_ADDS)
    tier = [r["id"] for r in rows if str(r["id"]).startswith("proto_fs_")
            and r.get("multiplayer")]
    assert tier == list(C.FURINA_STAGE_MULTIPLAYER_IDS)


def test_every_furina_row_resolves_on_a_full_stage():
    """Every pool row, the starter pair and the co-op rows, played onto a
    stage holding a star, a support and a Salon member, with Fanfare to
    spend: nothing raises and the ledger balances."""
    ids = (loader.pool_replacement("furina") + list(FS.STARTER_IDS[8:])
           + list(C.FURINA_STAGE_MULTIPLAYER_IDS))
    for cid in ids:
        st = _state(["clorinde", "charlotte", "usher"], fanfare=6, enemies=2,
                    deck=4, decider=policy.FURINA_STAGE_DECIDER)
        st.enemies[0].aura = "pyro"
        _play(st, cid)
        FS.end_of_turn_acts(st)
        assert FS.ledger_expected_end(_led(st)) == st.player.stage_fanfare, cid


def test_a_drafted_furina_fights_on_the_new_rules():
    from tier0.pilot.policy import make_pilot
    pilot = make_pilot(loader.pilot_weights("salon"))
    pool = loader.pool_replacement("furina")
    for seed in range(6):
        rng = random.Random(seed)
        picks = rng.sample(pool, 10)
        p = loader.build_player_from_ids("furina",
                                         list(FS.STARTER_IDS) + picks)
        st = combat.run_fight(p, loader.build_encounter("attrition"), pilot,
                              seed=seed)
        assert FS.ledger_expected_end(st.stage_ledger) == p.stage_fanfare
        assert any(e["event"] == "stage_open" for e in st.log)


# ---------------------------------------------------------------------------
# A separate arm: nobody else grows a stage, and the slice is untouched.
# ---------------------------------------------------------------------------

def test_the_stage_hooks_are_inert_for_anyone_else():
    for who in ("kokomi", "furina_v2"):
        p = Player(hp=78, max_hp=78, character_id=who)
        st = CombatState(player=p, enemies=[_enemy()], rng=random.Random(0))
        st.turn = 1
        FS.turn_open(st)
        FS.turn_start(st)
        FS.end_of_turn_acts(st)
        FS.note_turn_census(st)
        assert p.stage == [] and not st.log
        assert FS.gain(st, 3) == 0 and p.stage_fanfare == 0
        assert FS.hydro_bonus(st) == 0


def test_the_readings_are_written_down():
    assert FS.READINGS and all(isinstance(r, str) for r in FS.READINGS)
