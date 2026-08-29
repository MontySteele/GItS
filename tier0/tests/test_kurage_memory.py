"""The Kurage's memory: the QUARANTINED rule prototype behind
`C.KURAGE_MEMORY` (review/active/kokomi-kurage-memory-2026-08-29.md).

TWO KINDS OF TEST LIVE HERE and they are not the same claim.

The first is the GOLDEN, and it is the acceptance condition on the flag
itself: with `KURAGE_MEMORY` False not one byte of shipped behaviour
changes, so the shipped pulse is still `KURAGE_PULSE_BASE + Charge x
KURAGE_PULSE_PER_CHARGE` (4 + 3 x Charge), the summon still counts down,
a Companion's Exhaust still pays its Charge, and nothing ever enters a
queue. That test is the reason the rest of the file is allowed to exist.

The second is the RULE, tested with the flag monkeypatched on. These are
red-first tests of things that are RULES rather than numbers -- above all
the two recursion rules, which the proposal owed and did not state, and
which the doctrine seat named as the hole its whole D2 pass depended on.

NO NUMBER TAKEN OFF THIS ARM IS QUOTABLE ANYWHERE (R213 B / R215 B). The
assertions below are about what the engine DOES, never about whether any
of it is any good.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, refpowers
from tier0.engine.state import Card, CombatState
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None


def kokomi_state(enemies=None, seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


@pytest.fixture
def memory(monkeypatch):
    """The flag ON. Every test that uses this fixture is testing the
    prototype; every test that does not is testing the shipped engine."""
    monkeypatch.setattr(C, "KURAGE_MEMORY", True)


def play(st, card, energy=9):
    """A MANUAL play, through the real cost path, so `_finish_play` is
    entered the way a player enters it."""
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)


def companion(cid="sayu_daruma_gift"):
    return loader.get_card(cid)


# --------------------------------------------------------------------------
# THE GOLDEN: flag off is today, exactly
# --------------------------------------------------------------------------

def test_flag_is_off_by_default():
    """If this ever fails, everything else in the repo is measured against
    a rule [USER] has not taken."""
    assert C.KURAGE_MEMORY is False


def test_flag_off_the_pulse_is_still_base_plus_three_per_charge():
    """The golden. 4 + 3 x Charge, the summon decrements, the bank is read
    and never spent -- the shipped numbers, asserted through the constants
    so a retune moves the test with the engine and a RULE change does not."""
    st = kokomi_state()
    e = st.enemies[0]
    st.player.charge = 7
    st.player.powers["kurage_summon"] = C.KURAGE_DURATION
    hp0 = e.hp
    effects.player_turn_end_triggers(st)
    assert hp0 - e.hp == C.KURAGE_PULSE_BASE + 7 * C.KURAGE_PULSE_PER_CHARGE
    assert st.player.charge == 7                       # read, never spent
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION - 1
    assert st.kurage_queue == []                       # no memory exists


def test_flag_off_a_companion_play_banks_nothing_and_pays_its_charge():
    """The two halves the flag changes, pinned in their shipped form: a
    played Companion enters no queue, and its Exhaust still pays Charge
    (R216 D's Muster subsidy, as shipped)."""
    st = kokomi_state()
    card = companion()
    card.exhaust = True
    card.conscripted = True
    play(st, card)
    assert st.kurage_queue == []
    assert st.kurage_last_card_type == ""
    assert st.player.charge == C.CHARGE_PER_EXHAUST


# --------------------------------------------------------------------------
# THE QUEUE
# --------------------------------------------------------------------------

def test_played_companions_enter_the_memory_in_play_order(memory):
    st = kokomi_state()
    play(st, companion("sayu_daruma_gift"))
    play(st, companion("gorou_inuzaka_charge"))
    assert st.kurage_queue == ["sayu_daruma_gift", "gorou_inuzaka_charge"]


def test_her_own_non_companion_cards_never_enter_the_memory(memory):
    st = kokomi_state()
    play(st, loader.get_card("waters_edge"))
    play(st, loader.get_card("coral_guard"))
    assert st.kurage_queue == []


def test_a_mustered_companion_is_remembered_as_a_copy_though_it_exhausts(memory):
    """The reason the memory is a COPY and not the card: a Mustered
    Companion's own rules send it to the Exhaust pile, and the memory has
    to survive that."""
    st = kokomi_state()
    card = companion()
    card.exhaust = True
    card.conscripted = True          # the Muster stamp `_op_conscript` sets
    play(st, card)
    assert card in st.player.exhaust_pile
    assert st.kurage_queue == ["sayu_daruma_gift"]
    # and the remembered face re-materialises as a real, playable card
    assert loader.get_card(st.kurage_queue[0]).is_companion


def test_the_memory_carries_upgrade_state(memory):
    """"The face you played it with" -- an id carries `+`, so the copy
    does too."""
    st = kokomi_state()
    card = companion()
    card.id = "sayu_daruma_gift+"
    play(st, card)
    assert st.kurage_queue == ["sayu_daruma_gift+"]


def test_the_memory_is_per_fight_and_a_new_fight_starts_empty(memory):
    p = loader.build_player("kokomi")
    st = combat.run_fight(p, [make_enemy(hp=40)],
                          make_pilot(loader.pilot_weights("commander")),
                          seed=3)
    st2 = combat.run_fight(p, [make_enemy(hp=40)],
                           make_pilot(loader.pilot_weights("commander")),
                           seed=4)
    assert st2.kurage_queue == [] or st2.kurage_queue is not st.kurage_queue


# --------------------------------------------------------------------------
# THE FUEL (PICK A)
# --------------------------------------------------------------------------

def test_her_own_cards_exhaust_still_pays_one_charge(memory):
    st = kokomi_state()
    card = loader.get_card("coral_guard")
    refpowers.exhaust_card(st, card, caused_by_ethereal=False)
    assert st.player.charge == C.CHARGE_PER_EXHAUST


@pytest.mark.parametrize("conscripted", [True, False])
def test_a_companion_exhaust_pays_no_charge_mustered_or_drafted(
        memory, conscripted):
    """PICK A's one clause, and the half that breaks
    'block with Companions until the jellyfish is lethal'."""
    st = kokomi_state()
    card = companion()
    card.conscripted = conscripted
    refpowers.exhaust_card(st, card, caused_by_ethereal=False)
    assert st.player.charge == 0


def test_a_status_still_pays_nothing(memory):
    """Unchanged by the flag: the 2026-08-23 ruling that a Status or a
    Curse is never one of her cards."""
    st = kokomi_state()
    junk = Card(id="dazed", name="Dazed", cost=0, type="status",
                rarity="status")
    assert junk.is_junk               # the shared rotation-law predicate
    refpowers.exhaust_card(st, junk, caused_by_ethereal=False)
    assert st.player.charge == 0


def test_play_or_exhaust_mode_pays_on_the_play_too(memory, monkeypatch):
    """PICK A2, implemented so the arm can be swept and recommended by
    nobody."""
    monkeypatch.setattr(C, "KURAGE_FUEL_MODE", "play_or_exhaust")
    st = kokomi_state()
    play(st, loader.get_card("coral_guard"))
    assert st.player.charge == C.CHARGE_PER_EXHAUST
    st2 = kokomi_state()
    play(st2, companion())               # a Companion still pays nothing
    assert st2.player.charge == 0


# --------------------------------------------------------------------------
# THE FIRE (PICK B, PICK D) AND THE RECURSION RULE
# --------------------------------------------------------------------------

def armed(seed=0, enemies=None):
    """A jellyfish on the field, a memory with one Companion in it, and
    exactly the threshold banked."""
    st = kokomi_state(enemies=enemies, seed=seed)
    st.player.powers["kurage_summon"] = 1
    st.player.charge = C.KURAGE_THRESHOLD
    st.kurage_queue.append("sayu_daruma_gift")
    return st


def test_the_fire_pays_exactly_the_threshold_and_plays_one_card(memory):
    st = armed()
    assert effects.kurage_fire(st) is True
    assert st.player.charge == 0
    assert st.kurage_queue == []
    plays = [e for e in st.log if e["event"] == "play"]
    assert [e["card"] for e in plays] == ["sayu_daruma_gift"]
    assert plays[0]["free"] is True and plays[0]["cost"] == 0


def test_the_surplus_stays_banked_and_only_one_card_fires_per_turn(memory):
    st = armed()
    st.player.charge = C.KURAGE_THRESHOLD * 3
    st.kurage_queue.append("gorou_inuzaka_charge")
    assert effects.kurage_fire(st) is True
    assert effects.kurage_fire(st) is False        # the latch, not the bank
    assert st.player.charge == C.KURAGE_THRESHOLD * 2
    assert st.kurage_queue == ["gorou_inuzaka_charge"]


def test_a_replayed_companion_does_not_re_enter_the_memory(memory):
    """RECURSION RULE 1, and the reason an uncapped queue is self-bounding
    at all. The card fired IS a Companion, so without the exclusion this
    queue would come back at length 1 forever."""
    st = armed()
    effects.kurage_fire(st)
    assert st.kurage_queue == []


def test_below_the_threshold_nothing_fires(memory):
    st = armed()
    st.player.charge = C.KURAGE_THRESHOLD - 1
    assert effects.kurage_fire(st) is False
    assert st.player.charge == C.KURAGE_THRESHOLD - 1
    assert st.kurage_queue == ["sayu_daruma_gift"]


def test_an_empty_memory_holds_the_bank_and_pays_nothing(memory):
    """PICK D1. The punishment is tempo, never deletion -- the queue is
    checked BEFORE the spend."""
    st = armed()
    st.kurage_queue.clear()
    st.player.charge = C.KURAGE_THRESHOLD * 2
    assert effects.kurage_fire(st) is False
    assert st.player.charge == C.KURAGE_THRESHOLD * 2
    assert any(e["event"] == "kurage_memory_empty" for e in st.log)


def test_no_jellyfish_no_fire_though_the_memory_still_fills(memory):
    st = kokomi_state()
    st.player.charge = C.KURAGE_THRESHOLD
    play(st, companion())
    assert st.kurage_queue == ["sayu_daruma_gift"]     # the memory fills
    assert effects.kurage_fire(st) is False            # nothing acts on it
    assert st.player.charge == C.KURAGE_THRESHOLD


def test_the_fire_happens_at_turn_start_before_the_player_acts(memory):
    """PICK B1, through the real turn loop: the free card must be on the
    board in the state the player is planning in."""
    st = armed()
    st.player.hand.clear()
    combat._player_turn(st, NULL_PILOT)
    fired = [e for e in st.log if e["event"] == "kurage_memory_fire"]
    assert len(fired) == 1
    played = [i for i, e in enumerate(st.log) if e["event"] == "play"]
    ends = [i for i, e in enumerate(st.log) if e["event"] == "turn_close"]
    assert played and ends and played[0] < ends[0]
    assert st.player.charge == 0


def test_turn_end_timing_is_implemented(memory, monkeypatch):
    """PICK B2. Not recommended; implemented so the pair can be swept."""
    monkeypatch.setattr(C, "KURAGE_FIRE_TIMING", "turn_end")
    st = armed()
    st.player.hand.clear()
    combat._player_turn(st, NULL_PILOT)
    fired = [i for i, e in enumerate(st.log)
             if e["event"] == "kurage_memory_fire"]
    assert len(fired) == 1
    # and it did NOT fire at turn start under this setting
    opens = [i for i, e in enumerate(st.log) if e["event"] == "turn_open"]
    closes = [i for i, e in enumerate(st.log) if e["event"] == "turn_close"]
    assert opens[0] < fired[0] and fired[0] > closes[0] - 40


# --------------------------------------------------------------------------
# THE PULSE
# --------------------------------------------------------------------------

def pulse_state(memory_on=True):
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    return st


def test_the_pulse_keys_off_an_attack(memory):
    st = pulse_state()
    e = st.enemies[0]
    st.player.charge = 40                 # the bank must not be read at all
    play(st, loader.get_card("waters_edge"))
    hp_before = e.hp
    effects.player_turn_end_triggers(st)
    assert hp_before - e.hp == C.KURAGE_PULSE_BASE
    assert st.player.charge == 40
    assert st.player.powers["kurage_summon"] == 1      # persistent


def test_the_pulse_keys_off_a_skill(memory):
    st = pulse_state()
    play(st, loader.get_card("coral_guard"))
    block_before = st.player.block
    effects.player_turn_end_triggers(st)
    assert st.player.block - block_before == C.KURAGE_MEMORY_PULSE_BLOCK


def test_the_power_pulse_applies_hydro_and_no_number(memory):
    st = pulse_state()
    e = st.enemies[0]
    st.player.charge = 12
    play(st, Card(id="kokomi_power", name="p", cost=0, type="power",
                  character="kokomi", effects=[]))
    hp_before, block_before = e.hp, st.player.block
    effects.player_turn_end_triggers(st)
    assert e.aura == "hydro"
    assert e.hp == hp_before and st.player.block == block_before


def test_no_card_played_means_no_pulse(memory):
    st = pulse_state()
    e = st.enemies[0]
    hp_before, block_before = e.hp, st.player.block
    effects.player_turn_end_triggers(st)
    assert e.hp == hp_before and st.player.block == block_before
    (ev,) = [x for x in st.log if x["event"] == "kurage_pulse"]
    assert ev["kind"] == "none"


def test_the_pulse_ignores_the_jellyfishs_own_auto_play(memory):
    """RECURSION RULE 2, and the seat's second finding: an auto-played
    card must not determine or overwrite the pulse. She played an Attack;
    the jellyfish then replays a Skill; the pulse is still the Attack's."""
    st = armed()
    e = st.enemies[0]
    play(st, loader.get_card("waters_edge"))
    assert st.kurage_last_card_type == "attack"
    effects.kurage_fire(st)                     # sayu_daruma_gift is a skill
    assert st.kurage_last_card_type == "attack"
    hp_before = e.hp
    effects.player_turn_end_triggers(st)
    assert hp_before - e.hp == C.KURAGE_PULSE_BASE


def test_the_summon_is_persistent_under_the_flag(memory):
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("bake_kurage"))
    assert st.player.powers["kurage_summon"] == 1
    for _ in range(4):
        effects.player_turn_end_triggers(st)
        assert st.player.powers["kurage_summon"] == 1


# --------------------------------------------------------------------------
# TARGETING (PICK E)
# --------------------------------------------------------------------------

def test_the_replay_follows_the_enemy_her_last_attack_hit(memory):
    weak, strong = make_enemy(hp=30, name="weak"), make_enemy(hp=200,
                                                              name="strong")
    st = armed(enemies=[weak, strong])
    play(st, loader.get_card("waters_edge"))     # binds the lowest-HP aim
    assert st.kurage_last_attack_target is weak
    assert effects.kurage_target(st) is weak


def test_with_that_enemy_dead_the_replay_takes_the_highest_hp(memory):
    weak, strong = make_enemy(hp=30, name="weak"), make_enemy(hp=200,
                                                              name="strong")
    st = armed(enemies=[weak, strong])
    st.kurage_last_attack_target = weak
    weak.hp = 0                       # `alive` is derived, not assignable
    assert effects.kurage_target(st) is strong


def test_with_no_attack_yet_the_replay_takes_the_highest_hp(memory):
    weak, strong = make_enemy(hp=30, name="weak"), make_enemy(hp=200,
                                                              name="strong")
    st = armed(enemies=[weak, strong])
    assert st.kurage_last_attack_target is None
    assert effects.kurage_target(st) is strong


def test_the_random_target_rule_is_implemented(memory, monkeypatch):
    """PICK E2: no override, and the shipped forced-random free-play roll
    stands."""
    monkeypatch.setattr(C, "KURAGE_TARGET_RULE", "random")
    st = armed(enemies=[make_enemy(hp=30), make_enemy(hp=200)])
    assert effects.kurage_target(st) is None
    assert effects.kurage_fire(st) is True       # and it still resolves


def test_an_auto_played_attack_lands_on_the_led_target(memory):
    weak, strong = make_enemy(hp=90, name="weak"), make_enemy(hp=200,
                                                              name="strong")
    st = kokomi_state(enemies=[weak, strong])
    st.player.powers["kurage_summon"] = 1
    st.player.charge = C.KURAGE_THRESHOLD
    st.kurage_queue.append("gorou_inuzaka_charge")     # a Companion ATTACK
    st.kurage_last_attack_target = strong
    hp_weak, hp_strong = weak.hp, strong.hp
    effects.kurage_fire(st)
    assert strong.hp < hp_strong and weak.hp == hp_weak


# --------------------------------------------------------------------------
# THE SMOKE: a whole fight, no numbers claimed
# --------------------------------------------------------------------------

def test_a_whole_fight_runs_to_completion_under_the_flag(memory):
    """NO NUMBER IS ASSERTED and none may be quoted. The only claim is
    that the rule runs end to end without raising -- the pilot does not
    value the queue (policy.py says so), so this is not a measurement of
    the design and cannot become one."""
    for seed in (1, 2, 3, 4, 5):
        p = loader.build_player("kokomi")
        st = combat.run_fight(p, [make_enemy(hp=120), make_enemy(hp=60)],
                              make_pilot(loader.pilot_weights("commander")),
                              seed=seed)
        assert st.over or not st.living_enemies or not st.player.alive
        assert not [e for e in st.log if e["event"] == "UNIMPLEMENTED"]
