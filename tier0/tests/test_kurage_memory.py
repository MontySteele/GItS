"""The Kurage's memory, VERSION 3: the QUARANTINED rule prototype behind
`C.KURAGE_MEMORY` (review/active/kokomi-kurage-memory-2026-08-29.md sec.11).

TWO KINDS OF TEST LIVE HERE and they are not the same claim.

The first is the GOLDEN, and it is the acceptance condition on the flag
itself: with `KURAGE_MEMORY` False not one byte of shipped behaviour
changes, so the shipped pulse is still `KURAGE_PULSE_BASE + Charge x
KURAGE_PULSE_PER_CHARGE` (4 + 3 x Charge), the summon still counts down,
a Companion's Exhaust still pays its Charge, and nothing ever enters a
queue. That test is the reason the rest of the file is allowed to exist.

The second is the RULE, tested with the flag monkeypatched on, and v3 has
two of them. They are filed in two sections BECAUSE THEY ARE INDEPENDENT
([USER], 2026-08-29: "Those should be independent mechanics") -- Rule 1
fires at a Muster and reads nothing about Companions or Exhaust; Rule 2
fires at the exhaust funnel and reads nothing about Musters. One test sits
between the sections and pins the consequence: a single Muster whose
recruit prints Exhaust yields TWO memories, in order.

NO NUMBER TAKEN OFF THIS ARM IS QUOTABLE ANYWHERE (R213 B / R215 B). The
assertions below are about what the engine DOES, never about whether any
of it is any good.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, refpowers
from tier0.engine.state import Card, CombatState, KurageMemory
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None

# The two starter Companions the whole file leans on, and why each:
#   gorou_inuzaka_charge -- cost 0, ATTACK, prints Exhaust. The card [USER]
#     named ("0-cost cards can autoplay for free (e.g. Gorou in the starter
#     deck)"), and the only one that is free to replay.
#   sayu_daruma_gift -- cost 1, SKILL, does NOT print Exhaust. The card that
#     has to be burned by hand to be remembered.
EXHAUST_COMPANION = "gorou_inuzaka_charge"
PLAIN_COMPANION = "sayu_daruma_gift"


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


def companion(cid=PLAIN_COMPANION):
    return loader.get_card(cid)


def junk(rarity="status"):
    """A Status/Curse. Built rather than loaded so the test states the one
    property it is about -- `rarity` -- instead of depending on a sheet row
    that a later pass may retire."""
    return Card(id="junk_ally", name="junk", cost=1, type="skill",
                rarity=rarity, tags=["companion"])


def x_companion():
    return Card(id="x_cost_ally", name="X ally", cost="X", type="attack",
                rarity="rare", role_c="applier", exhaust=True,
                effects=[{"op": "damage", "amount": 3, "target": "enemy"}])


def queued(price, card_id=EXHAUST_COMPANION, **kw):
    return KurageMemory(card_id=card_id, cost=price // 3, price=price, **kw)


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


def test_flag_off_nothing_is_ever_remembered():
    """Every v3 door, with the flag off: a played-and-Exhausted Companion and
    a Muster both leave the queue empty and the Charge funnel exactly where
    it shipped."""
    st = kokomi_state()
    play(st, companion(EXHAUST_COMPANION))             # plays AND exhausts
    st.player.hand.append(loader.get_card("waters_edge"))
    effects._op_conscript(st, {"op": "conscript", "amount": 1},
                          loader.get_card("conscription_notice"))
    assert st.kurage_queue == []
    assert st.kurage_last_card_type == ""
    assert st.player.charge == C.CHARGE_PER_EXHAUST    # the shipped funnel


# --------------------------------------------------------------------------
# RULE 1 -- MUSTER. The card SACRIFICED enters, on its original face.
# [USER]: "We would be adding the card that was sacrificed for the Muster,
# not the new card - so the original face."
# --------------------------------------------------------------------------

def muster(st, victim_id="waters_edge"):
    st.player.hand.append(loader.get_card(victim_id))
    effects._op_conscript(st, {"op": "conscript", "amount": 1},
                          loader.get_card("conscription_notice"))
    return st.player.hand[-1]                          # the recruit


def test_the_muster_remembers_the_card_it_sacrificed(memory):
    st = kokomi_state()
    printed = loader.get_card("waters_edge").cost
    recruit = muster(st)
    assert [m.card_id for m in st.kurage_queue] == ["waters_edge"]
    entry = st.kurage_queue[0]
    assert entry.rule == "muster"
    assert entry.cost == printed
    assert entry.price == printed * C.KURAGE_MEMORY_COST_PER_ENERGY
    assert recruit.id != "waters_edge"                 # it really transformed


def test_the_mustered_card_stores_no_target_because_it_was_never_played(memory):
    st = kokomi_state()
    muster(st)
    assert st.kurage_queue[0].target is None


def test_the_recruit_does_not_enter_at_the_transformation(memory):
    """RULE 1 remembers the sacrifice and NOTHING else. The recruit's own
    entry is Rule 2's business and happens later, when it Exhausts."""
    st = kokomi_state()
    recruit = muster(st)
    assert [m.card_id for m in st.kurage_queue] == ["waters_edge"]
    assert recruit.kurage_remembered is False


def test_create_mode_conscription_sacrifices_nothing_and_remembers_nothing(
        memory):
    st = kokomi_state()
    effects._op_conscript(st, {"op": "conscript", "amount": 1,
                               "mode": "create"},
                          loader.get_card("conscription_notice"))
    assert st.kurage_queue == []


def test_a_remembered_non_companion_replays_free_once_and_vanishes(memory):
    """v3 lets the memory hold one of HER OWN cards, because that is what a
    Muster usually eats. It replays by exactly the same rules."""
    st = kokomi_state()
    muster(st)
    st.player.powers["kurage_summon"] = 1
    st.player.charge = 99
    piles = (len(st.player.discard_pile), len(st.player.exhaust_pile))
    assert effects.kurage_fire(st) is True
    assert st.kurage_queue == []
    assert (len(st.player.discard_pile),
            len(st.player.exhaust_pile)) == piles      # removed from combat
    assert [e for e in st.log if e["event"] == "play"
            and e["card"] == "waters_edge"]


# --------------------------------------------------------------------------
# RULE 2 -- EXHAUST. "When a Companion not originating from Memory
# Exhausts, remember it."
# --------------------------------------------------------------------------

def test_a_played_companion_without_exhaust_does_not_enter(memory):
    """THE RULE v3 REPLACED. Under v2 the play WAS the entry; under v3 it is
    not -- "thus you cannot just spam Raiden over and over"."""
    st = kokomi_state()
    play(st, companion(PLAIN_COMPANION))
    assert st.kurage_queue == []


def test_an_exhaust_companion_enters_once_carrying_its_target(memory):
    weak, strong = make_enemy(hp=90, name="weak"), make_enemy(hp=200,
                                                              name="strong")
    st = kokomi_state(enemies=[weak, strong])
    play(st, companion(EXHAUST_COMPANION))             # an ATTACK: it binds
    assert [m.card_id for m in st.kurage_queue] == [EXHAUST_COMPANION]
    entry = st.kurage_queue[0]
    assert entry.rule == "exhaust"
    assert entry.target is weak                        # the body it hit
    assert entry.ephemeral is False                    # it printed Exhaust


def test_a_hand_exhausted_plain_companion_enters_ephemeral_with_no_target(
        memory):
    st = kokomi_state()
    card = companion(PLAIN_COMPANION)
    refpowers.exhaust_card(st, card)                   # burned by hand
    assert [m.card_id for m in st.kurage_queue] == [PLAIN_COMPANION]
    assert st.kurage_queue[0].ephemeral is True
    assert st.kurage_queue[0].target is None


def test_a_companion_instance_enrols_at_most_once(memory):
    """The general once-only guard, and the only one v3 keeps."""
    st = kokomi_state()
    card = companion(EXHAUST_COMPANION)
    refpowers.exhaust_card(st, card)
    refpowers.exhaust_card(st, card)                   # somehow burned again
    assert len(st.kurage_queue) == 1
    assert [e for e in st.log if e["event"] == "kurage_memory_refused"
            and e["reason"] == "already"]


def test_one_of_her_own_cards_exhausting_does_not_enter(memory):
    """Rule 2 is about COMPANIONS. Her own cards reach the memory only by
    Rule 1, i.e. by being sacrificed to a Muster."""
    st = kokomi_state()
    refpowers.exhaust_card(st, loader.get_card("waters_edge"))
    assert st.kurage_queue == []
    assert st.player.charge == C.CHARGE_PER_EXHAUST    # it still pays fuel


@pytest.mark.parametrize("rarity", ["status", "curse"])
def test_junk_never_enters_and_never_pays(memory, rarity):
    st = kokomi_state()
    refpowers.exhaust_card(st, junk(rarity=rarity))
    assert st.kurage_queue == []
    assert st.player.charge == 0


def test_an_x_cost_companion_is_ineligible(memory):
    st = kokomi_state()
    refpowers.exhaust_card(st, x_companion())
    assert st.kurage_queue == []
    assert [e for e in st.log if e["event"] == "kurage_memory_refused"
            and e["reason"] == "x_cost"]


# --------------------------------------------------------------------------
# THE TWO RULES ARE INDEPENDENT
# [USER]: "No, if the Muster prints a card that Exhausts, then it gets added
# as well." / "Those should be independent mechanics."
# --------------------------------------------------------------------------

def test_one_muster_then_playing_the_recruit_yields_two_memories_in_order(
        memory):
    st = kokomi_state()
    recruit = muster(st)
    assert len(st.kurage_queue) == 1                   # Rule 1 fired alone
    play(st, recruit)                                  # Muster gave it Exhaust
    assert [m.card_id for m in st.kurage_queue] == ["waters_edge", recruit.id]
    assert [m.rule for m in st.kurage_queue] == ["muster", "exhaust"]


# --------------------------------------------------------------------------
# THE PRICE: 3 x the remembered face's cost
# --------------------------------------------------------------------------

def test_the_price_is_three_times_the_face_cost(memory):
    st = kokomi_state()
    card = companion(PLAIN_COMPANION)                  # cost 1
    refpowers.exhaust_card(st, card)
    assert st.kurage_queue[0].price == (
        card.cost * C.KURAGE_MEMORY_COST_PER_ENERGY)


def test_a_permanent_face_change_moves_the_price(memory):
    """The id carries upgrade state and the instance carries the upgraded
    cost, so a permanent cost change changes the price."""
    st = kokomi_state()
    base = companion(PLAIN_COMPANION).cost
    card = companion(PLAIN_COMPANION)
    card.cost += 1
    refpowers.exhaust_card(st, card)
    assert st.kurage_queue[0].price == (
        (base + 1) * C.KURAGE_MEMORY_COST_PER_ENERGY)


def test_a_temporary_discount_is_ignored(memory):
    """The advisor's rule statement: "including permanent upgrade changes,
    ignoring temporary combat discounts". The price is read off the card and
    never off `combat.card_cost`, which is what makes that true."""
    st = kokomi_state()
    card = companion(PLAIN_COMPANION)
    card.cost_delta_this_turn = -1
    card.cost_delta_this_combat = -1
    assert combat.card_cost(st, card) == 0             # free to PLAY
    refpowers.exhaust_card(st, card)
    assert st.kurage_queue[0].price == (
        card.cost * C.KURAGE_MEMORY_COST_PER_ENERGY)   # and not 0


def test_musters_minus_one_counts_on_the_recruits_own_entry(memory):
    """The recruit IS the card that Exhausted, so its Mustered face is the
    face the price reads -- KURAGE_MEMORY_COST_BASIS "remembered_face", and
    v3 has no other basis."""
    st = kokomi_state()
    recruit = muster(st)
    printed = loader.get_card(recruit.id).cost
    assert recruit.cost == max(0, printed + C.CONSCRIPT_COST_DELTA)
    play(st, recruit)
    entry = st.kurage_queue[-1]
    assert entry.cost == recruit.cost
    assert entry.price == recruit.cost * C.KURAGE_MEMORY_COST_PER_ENERGY


def test_a_zero_cost_memory_fires_for_free(memory):
    """[USER]: "0-cost cards can autoplay for free (e.g. Gorou in the starter
    deck)"."""
    st = kokomi_state()
    play(st, companion(EXHAUST_COMPANION))             # cost 0, Exhaust
    assert st.kurage_queue[0].price == 0
    st.player.powers["kurage_summon"] = 1
    st.player.charge = 0
    assert effects.kurage_fire(st) is True
    assert st.player.charge == 0


# --------------------------------------------------------------------------
# THE FIRE, THE BLOCK, AND THE ONE PLAY PER TURN
# --------------------------------------------------------------------------

def armed(entries=(), charge=99, enemies=None, seed=0):
    st = kokomi_state(enemies=enemies, seed=seed)
    st.player.powers["kurage_summon"] = 1
    st.player.charge = charge
    st.kurage_queue.extend(entries)
    return st


def test_the_fire_pays_the_fronts_own_price_and_plays_one_card(memory):
    st = armed([queued(3, PLAIN_COMPANION)], charge=10)
    assert effects.kurage_fire(st) is True
    assert st.player.charge == 7
    assert st.kurage_queue == []
    assert st.cards_played_this_turn == 1


def test_an_unaffordable_front_blocks_the_queue_and_the_bank_holds(memory):
    """[USER]: "Sticking a card you can't afford into Memory blocks Memory
    until it's played"."""
    behind = queued(0, EXHAUST_COMPANION)
    st = armed([queued(9, PLAIN_COMPANION), behind], charge=5)
    assert effects.kurage_fire(st) is False
    assert st.player.charge == 5                       # nothing spent
    assert len(st.kurage_queue) == 2                   # nothing behind fired
    assert st.kurage_queue[1] is behind
    assert [e for e in st.log if e["event"] == "kurage_memory_blocked"]


def test_one_play_per_turn_with_twenty_queued_and_a_hundred_charge(memory):
    """[USER]: "If you stack infinite Charge, then you still get only one
    play per turn."""
    st = armed([queued(0) for _ in range(20)], charge=100)
    assert effects.kurage_fire(st) is True
    assert effects.kurage_fire(st) is False
    assert len(st.kurage_queue) == 19


def test_the_fire_happens_at_turn_start_before_the_player_acts(memory):
    st = armed([queued(0)], charge=10)
    combat._player_turn(st, NULL_PILOT)
    order = [e["event"] for e in st.log
             if e["event"] in ("kurage_memory_fire", "kurage_pulse")]
    assert order and order[0] == "kurage_memory_fire"
    assert st.kurage_queue == []


def test_turn_end_timing_is_implemented(memory, monkeypatch):
    monkeypatch.setattr(C, "KURAGE_FIRE_TIMING", "turn_end")
    st = armed([queued(0)], charge=10)
    combat._player_turn(st, NULL_PILOT)
    assert st.kurage_queue == []


def test_a_memory_play_never_re_enters_pays_no_charge_and_is_not_the_pulse_key(
        memory):
    """The three things the rule statement forbids a copy, in one test
    because they are one clause: "a Memory-originated play never creates
    another Memory; its removal does not count as an Exhaust for Charge; ...
    it must not program Kurage's Attack/Skill/Power pulse"."""
    st = armed([queued(0, EXHAUST_COMPANION)], charge=4)
    assert effects.kurage_fire(st) is True
    assert st.kurage_queue == []                       # no re-entry
    assert st.player.charge == 4                       # price 0, no Exhaust pay
    assert st.kurage_last_card_type == ""              # not the pulse key


def test_the_copy_is_removed_from_combat_and_reaches_no_pile(memory):
    st = armed([queued(0, EXHAUST_COMPANION), queued(3, PLAIN_COMPANION)],
               charge=9)
    before = (len(st.player.discard_pile), len(st.player.exhaust_pile),
              len(st.player.hand), len(st.player.draw_pile))
    effects.kurage_fire(st)
    st.kurage_fired_this_turn = False
    effects.kurage_fire(st)
    assert (len(st.player.discard_pile), len(st.player.exhaust_pile),
            len(st.player.hand), len(st.player.draw_pile)) == before
    assert len([e for e in st.log
                if e["event"] == "kurage_memory_removed"]) == 2


def test_the_copys_removal_is_not_an_exhaust_event_at_all(memory):
    """"its removal does not count as an Exhaust for Charge". Stronger than
    the Charge assertion above and deliberately so: the copy must not reach
    the exhaust funnel AT ALL, because everything else hanging off that funnel
    -- the Burst wage, the rotation latch, `exhausts_this_turn`, a relic's
    damage_per_exhaust -- would otherwise pay out for a card that was never
    burned. `kurage_fire` clears the copy's own `exhaust` flag to make that
    true at the pile rule rather than by five special cases."""
    st = armed([queued(0, EXHAUST_COMPANION)], charge=4)
    st.player.burst_max = 10
    burst, exhausts = st.player.burst_energy, st.exhausts_this_turn
    assert effects.kurage_fire(st) is True
    assert st.exhausts_this_turn == exhausts
    assert st.player.burst_energy == burst
    assert not [e for e in st.log if e["event"] == "exhaust"]


def test_a_memory_play_still_triggers_when_you_play_a_companion(memory):
    """The copy is a real card play through `resolve_free_play`, so ordinary
    Companion payoffs see it. Navia's is the cheapest witness."""
    st = armed([queued(0, EXHAUST_COMPANION)], charge=0)
    st.player.powers["cannon_fire_support"] = 4
    st.player.block = 0
    effects.kurage_fire(st)
    assert st.player.block >= 4
    assert st.companion_plays_this_turn == 1


def test_an_empty_memory_holds_the_bank_and_pays_nothing(memory):
    st = armed([], charge=50)
    assert effects.kurage_fire(st) is False
    assert st.player.charge == 50
    assert [e for e in st.log if e["event"] == "kurage_memory_empty"]


def test_no_jellyfish_no_fire_though_the_memory_still_fills(memory):
    st = kokomi_state()
    play(st, companion(EXHAUST_COMPANION))
    assert len(st.kurage_queue) == 1
    st.player.charge = 99
    assert effects.kurage_fire(st) is False


# --------------------------------------------------------------------------
# THE TARGET: the same body, or a random eligible one
# --------------------------------------------------------------------------

def test_the_copy_plays_against_the_same_target(memory):
    """[USER]: "Cards must play against the same target the second time".
    The stored body is preferred even when it is no longer the body a fresh
    bind would pick -- which is the whole content of the promise."""
    weak, strong = make_enemy(hp=90, name="weak"), make_enemy(hp=200,
                                                             name="strong")
    st = kokomi_state(enemies=[weak, strong])
    play(st, companion(EXHAUST_COMPANION))             # binds to `weak`
    assert st.kurage_queue[0].target is weak
    weak.hp = 300                                      # now the HIGHEST hp
    st.player.powers["kurage_summon"] = 1
    st.player.charge = 9
    hp_weak, hp_strong = weak.hp, strong.hp
    effects.kurage_fire(st)
    assert weak.hp < hp_weak and strong.hp == hp_strong


def test_a_dead_target_falls_back_to_an_eligible_enemy(memory):
    """"unless that target no longer exists, in which case they play randomly
    against eligible targets"."""
    weak, strong = make_enemy(hp=90, name="weak"), make_enemy(hp=200,
                                                             name="strong")
    st = kokomi_state(enemies=[weak, strong])
    play(st, companion(EXHAUST_COMPANION))
    weak.hp = 0
    st.player.powers["kurage_summon"] = 1
    st.player.charge = 9
    hp_strong = strong.hp
    effects.kurage_fire(st)
    assert strong.hp < hp_strong


def test_a_memory_with_no_target_takes_the_fallback(memory):
    st = armed([queued(0, EXHAUST_COMPANION)], charge=0,
               enemies=[make_enemy(hp=120)])
    hp0 = st.enemies[0].hp
    assert effects.kurage_fire(st) is True
    assert st.enemies[0].hp < hp0


def test_the_most_hp_fallback_is_implemented(memory, monkeypatch):
    monkeypatch.setattr(C, "KURAGE_MEMORY_TARGET_FALLBACK", "most_hp")
    weak, strong = make_enemy(hp=30, name="weak"), make_enemy(hp=200,
                                                             name="strong")
    st = armed([queued(0, EXHAUST_COMPANION)], charge=0,
               enemies=[weak, strong])
    hp_weak, hp_strong = weak.hp, strong.hp
    effects.kurage_fire(st)
    assert strong.hp < hp_strong and weak.hp == hp_weak


# --------------------------------------------------------------------------
# THE FUEL: 1 Exhaust = 1 Charge, on her originals
# --------------------------------------------------------------------------

def test_her_own_cards_exhaust_pays_one_charge(memory):
    st = kokomi_state()
    refpowers.exhaust_card(st, loader.get_card("waters_edge"))
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_an_original_companions_exhaust_pays_too(memory):
    """v3 RETIRES v2's PICK A1: under v2 a Companion paid nothing."""
    st = kokomi_state()
    play(st, companion(EXHAUST_COMPANION))
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_a_mustered_companions_exhaust_pays_too(memory):
    st = kokomi_state()
    recruit = muster(st)
    before = st.player.charge
    play(st, recruit)
    assert st.player.charge == before + C.CHARGE_PER_EXHAUST


def test_play_or_exhaust_mode_is_still_implemented(memory, monkeypatch):
    """v2's PICK A2, kept sweepable. It pays on the PLAY of one of her own
    non-Companion cards, on top of the funnel."""
    monkeypatch.setattr(C, "KURAGE_FUEL_MODE", "play_or_exhaust")
    st = kokomi_state()
    play(st, loader.get_card("waters_edge"))
    assert st.player.charge >= C.CHARGE_PER_EXHAUST


# --------------------------------------------------------------------------
# THE PULSE
# --------------------------------------------------------------------------

def pulse_state():
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    return st


def test_the_pulse_keys_off_an_attack(memory):
    st = pulse_state()
    st.kurage_last_card_type = "attack"
    hp0 = st.enemies[0].hp
    effects.kurage_memory_pulse(st)
    assert hp0 - st.enemies[0].hp == C.KURAGE_PULSE_BASE


def test_the_pulse_keys_off_a_skill(memory):
    st = pulse_state()
    st.kurage_last_card_type = "skill"
    effects.kurage_memory_pulse(st)
    assert st.player.block == C.KURAGE_MEMORY_PULSE_BLOCK


def test_the_power_pulse_grants_charge(memory):
    """[USER], 2026-08-29: "Sacrificing a power seems like a bigger deal than
    sacrificing anything else." The amount is DERIVED: CHARGE_PER_EXHAUST."""
    st = pulse_state()
    st.kurage_last_card_type = "power"
    effects.kurage_memory_pulse(st)
    assert st.player.charge == C.CHARGE_PER_EXHAUST
    assert st.enemies[0].aura is None                  # not Hydro any more


def test_the_power_pulses_charge_can_pay_a_front(memory):
    st = armed([queued(3, PLAIN_COMPANION)], charge=2)
    st.kurage_last_card_type = "power"
    assert effects.kurage_fire(st) is False            # 2 < 3, blocked
    effects.kurage_memory_pulse(st)
    assert st.player.charge == 2 + C.CHARGE_PER_EXHAUST
    assert effects.kurage_fire(st) is True


def test_the_hydro_power_pulse_is_still_implemented(memory, monkeypatch):
    monkeypatch.setattr(C, "KURAGE_POWER_PULSE", "hydro")
    st = pulse_state()
    st.kurage_last_card_type = "power"
    effects.kurage_memory_pulse(st)
    assert st.enemies[0].aura == "hydro"
    assert st.player.charge == 0


def test_no_card_played_means_no_pulse(memory):
    st = pulse_state()
    hp0 = st.enemies[0].hp
    effects.kurage_memory_pulse(st)
    assert st.enemies[0].hp == hp0
    assert st.player.charge == 0


def test_the_summon_is_persistent_under_the_flag(memory):
    st = kokomi_state()
    effects._op_summon_kurage(st, {"op": "summon_kurage"},
                              loader.get_card("bake_kurage"))
    st.kurage_last_card_type = "skill"
    effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == 1      # never decrements


# --------------------------------------------------------------------------
# THE ACCELERATION KEYWORD'S HOOK (provisional name "Stir")
# --------------------------------------------------------------------------

def test_play_front_memory_fires_outside_the_automatic_rhythm(memory):
    """The op neither reads nor sets the per-turn latch, so a Skill printing
    it can add a play to a turn the jellyfish has already used."""
    st = armed([queued(0), queued(0)], charge=9)
    assert effects.kurage_fire(st) is True             # the automatic one
    assert st.kurage_fired_this_turn is True
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("bake_kurage"))
    assert st.kurage_queue == []                       # and the second fired


def test_play_front_memory_still_pays_the_price_and_respects_the_block(memory):
    st = armed([queued(9, PLAIN_COMPANION)], charge=5)
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("bake_kurage"))
    assert len(st.kurage_queue) == 1
    assert st.player.charge == 5


def test_play_front_memory_is_inert_with_the_flag_off():
    st = kokomi_state()
    st.kurage_queue.append(queued(0))
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("bake_kurage"))
    assert len(st.kurage_queue) == 1


# --------------------------------------------------------------------------
# THE SMOKE: five whole fights, no numbers claimed
# --------------------------------------------------------------------------

def test_five_fights_run_to_completion_under_the_flag(memory):
    """NO NUMBER IS ASSERTED and none may be quoted. The only claim is that
    the rule runs end to end without raising -- the pilot does not value the
    queue (policy.py says so), so this is not a measurement of the design and
    cannot become one. sec.11 reports the SHAPE the same run produced."""
    for seed in (1, 2, 3, 4, 5):
        p = loader.build_player("kokomi")
        st = combat.run_fight(p, [make_enemy(hp=120), make_enemy(hp=60)],
                              make_pilot(loader.pilot_weights("commander")),
                              seed=seed)
        assert st.over or not st.living_enemies or not st.player.alive
        assert not [e for e in st.log if e["event"] == "UNIMPLEMENTED"]
