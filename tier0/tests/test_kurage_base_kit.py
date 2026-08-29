"""THE KURAGE BASE KIT, VERSION 4: the jellyfish is always on, and one
Muster card takes Bake-Kurage's seat in the starter deck.

[USER], 2026-08-29, verbatim and the whole spec:

    "I think that we will want to make Bake-Kurage part of the base kit
    (always on) rather than a separate card. So yes, we could add one Muster
    card to the base deck to teach the pattern."

It answers sec.11.8: at the starter floor the v3 rule fired exactly once per
fight, on the one free card, and the bank was never spent and never blocked --
so the interesting half of the design (bank toward a card you cannot yet
afford; be blocked when you over-bank) was DRAFTED and never PRINTED. A Muster
in the opening deck prints RULE 1 in fight 1: the card sacrificed to it enters
the memory at three times its cost, which is a price the starter can fail to
pay.

EVERYTHING HERE IS QUARANTINED behind `C.KURAGE_MEMORY` (and, for the
jellyfish and the starter swap, `C.KURAGE_ALWAYS_ON` beneath it). The GOLDEN
tests at the top are the acceptance condition on the flag: with the flag off
the starter is the printed one and no jellyfish exists that a card did not
summon.

NO NUMBER TAKEN OFF THIS ARM IS QUOTABLE ANYWHERE (R213 B / R215 B). Every
assertion below is about what the engine DOES.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import CombatState, KurageMemory
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy

DROP = "bake_kurage"
ADD = "to_the_front"


@pytest.fixture
def base_kit(monkeypatch):
    """The flag ON, and the base kit with it. Every test that takes this
    fixture is testing the prototype; every test that does not is testing
    the shipped engine."""
    monkeypatch.setattr(C, "KURAGE_MEMORY", True)
    monkeypatch.setattr(C, "KURAGE_ALWAYS_ON", True)


@pytest.fixture
def v3_arm(monkeypatch):
    """The memory rule WITHOUT the base kit -- the v3 arm, kept reachable by
    one constant so a revert is a flip and not a re-authoring."""
    monkeypatch.setattr(C, "KURAGE_MEMORY", True)
    monkeypatch.setattr(C, "KURAGE_ALWAYS_ON", False)


def kokomi_state(enemies=None, seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def fight(seed=1, hp=(120, 60)):
    p = loader.build_player("kokomi")
    return combat.run_fight(p, [make_enemy(hp=h) for h in hp],
                            make_pilot(loader.pilot_weights("commander")),
                            seed=seed)


# --------------------------------------------------------------------------
# THE GOLDEN: flag off is today, exactly
# --------------------------------------------------------------------------

def test_the_base_kit_constant_is_only_read_under_the_master_flag():
    """`KURAGE_ALWAYS_ON` ships True. That is harmless and deliberate: it is
    read only where `KURAGE_MEMORY` has already been checked, and
    `KURAGE_MEMORY` is the quarantine."""
    assert C.KURAGE_MEMORY is False
    assert C.KURAGE_ALWAYS_ON is True


def test_flag_off_the_printed_starter_is_untouched():
    ids = loader.starting_deck("kokomi")
    assert DROP in ids and ADD not in ids
    assert len(ids) == 12
    assert [c.id for c in loader.build_player("kokomi").draw_pile] == ids


def test_flag_off_no_jellyfish_exists_that_no_card_summoned():
    st = fight()
    assert not [e for e in st.log if e["event"] == "kurage_base_kit"]


def test_flag_off_the_summon_still_counts_down():
    """The v0.4 jellyfish, unmoved: summoned for KURAGE_DURATION turns, one
    turn spent per pulse."""
    st = kokomi_state()
    effects._op_summon_kurage(st, {"op": "summon_kurage"},
                              loader.get_card(DROP))
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION
    st.kurage_last_card_type = "skill"
    effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION - 1


# --------------------------------------------------------------------------
# A -- THE ALWAYS-ON JELLYFISH
# --------------------------------------------------------------------------

def test_the_jellyfish_is_on_the_field_from_the_start_of_combat(base_kit):
    st = fight()
    installed = [e for e in st.log if e["event"] == "kurage_base_kit"]
    assert len(installed) == 1 and installed[0]["persistent"] is True
    # And it was there BEFORE the first turn opened.
    assert st.log.index(installed[0]) < min(
        i for i, e in enumerate(st.log) if e["event"] == "turn_open")


def test_it_is_hers_alone(base_kit):
    """The base kit is Kokomi's. A Companion-playing Klee must not acquire a
    jellyfish because a constant is on."""
    p = loader.build_player("klee")
    st = combat.run_fight(p, [make_enemy(hp=60)],
                          make_pilot(loader.pilot_weights("demolition")),
                          seed=1)
    assert not [e for e in st.log if e["event"] == "kurage_base_kit"]
    assert not p.powers.get("kurage_summon", 0)


def test_the_pulse_fires_on_turn_one_with_nothing_summoned(base_kit):
    st = fight()
    assert [e for e in st.log if e["event"] == "kurage_pulse"]
    assert not [e for e in st.log if e["event"] == "summon_kurage"]


def test_the_jellyfish_never_expires(base_kit):
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.kurage_last_card_type = "skill"
    for _ in range(20):
        effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == 1


def test_the_pulse_fires_every_turn_end(base_kit):
    st = fight()
    turns = len([e for e in st.log if e["event"] == "turn_open"])
    pulses = len([e for e in st.log if e["event"] == "kurage_pulse"])
    # One pulse per player turn end; the last turn may end in a kill before
    # the turn-end triggers run, so the pulse count is turns or turns-1.
    assert turns - 1 <= pulses <= turns


def test_with_always_on_off_the_v3_arm_is_whole(v3_arm):
    """The revert is one constant: no install at combat start, and the
    jellyfish is back to something a card must summon."""
    st = fight()
    assert not [e for e in st.log if e["event"] == "kurage_base_kit"]
    st2 = kokomi_state()
    effects._op_summon_kurage(st2, {"op": "summon_kurage"},
                              loader.get_card(DROP))
    assert st2.player.powers["kurage_summon"] == 1
    st2.kurage_last_card_type = "skill"
    effects.player_turn_end_triggers(st2)
    assert st2.player.powers["kurage_summon"] == 1      # v3: no decrement


# --------------------------------------------------------------------------
# B -- THE STARTER DECK
# --------------------------------------------------------------------------

def test_the_starter_swaps_the_summon_for_a_muster(base_kit):
    ids = loader.starting_deck("kokomi")
    assert DROP not in ids
    assert ids.count(ADD) == 1
    assert len(ids) == 12                      # the count does not move


def test_the_battery_and_the_run_read_the_same_starter(base_kit):
    """One seam, `loader._starter_ids`, so tier 0's `build_player` and tier
    0.5's `starting_deck` cannot disagree about what she opens with."""
    assert [c.id for c in loader.build_player("kokomi").draw_pile] \
        == loader.starting_deck("kokomi")


def test_the_swap_survives_the_randomized_starter_roll(base_kit):
    """The support slot's roll and the base-kit swap touch different cards
    and must compose."""
    for seed in range(8):
        ids = loader.starting_deck("kokomi", rng=random.Random(seed))
        assert DROP not in ids and ids.count(ADD) == 1 and len(ids) == 12


def test_no_other_character_starter_moves(base_kit):
    for cid in ("klee", "furina"):
        assert loader.starting_deck(cid) == \
            loader._character_index()[cid]["starting_deck"]


def test_the_sheets_did_not_move(base_kit):
    """The swap is CODE. The printed sheet still prints Bake-Kurage, which is
    what makes the flag a targeted revert."""
    spec = loader._character_index()["kokomi"]
    assert DROP in spec["starting_deck"] and ADD not in spec["starting_deck"]


def test_the_muster_in_the_starter_enrols_the_sacrifice_at_three_times_cost(
        base_kit):
    """THE WHOLE POINT OF B. Playing the starter's Muster in fight 1 puts the
    card it ate into the memory, priced at 3x -- so the bank, the afford and
    the block are printed rather than drafted."""
    st = kokomi_state()
    card = next(c for c in st.player.draw_pile if c.id == ADD)
    st.player.draw_pile.remove(card)
    st.player.hand.append(loader.get_card("waters_edge"))
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert [m.card_id for m in st.kurage_queue] == ["waters_edge"]
    entry = st.kurage_queue[0]
    assert entry.rule == "muster"
    # THE NUMBER IS [USER]'S RULE, so it is written out rather than
    # re-derived from the constant it is testing: "cards cost Charge equal
    # to 3x their Cost". Water's Edge is a 1, so the price is a 3.
    assert (entry.cost, entry.price) == (1, 3)
    assert entry.price == entry.cost * C.KURAGE_MEMORY_COST_PER_ENERGY


def test_the_starter_muster_can_bank_a_price_the_starter_cannot_yet_pay(
        base_kit):
    """sec.11.8's missing half, now reachable at the floor: a front priced
    above the bank BLOCKS, and the bank holds."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1       # as combat start installs it
    st.player.hand.append(loader.get_card("waters_edge"))
    effects._op_conscript(st, {"op": "conscript", "amount": 1},
                          loader.get_card(ADD))
    st.player.charge = 1                       # under the price of 3
    assert effects.kurage_fire(st) is False
    assert len(st.kurage_queue) == 1
    assert st.player.charge == 1               # unspent, not lost
    assert [e for e in st.log if e["event"] == "kurage_memory_blocked"]


# --------------------------------------------------------------------------
# C -- WHAT `summon_kurage` MEANS WHEN THE JELLYFISH IS PERMANENT.
# Each test below pins the LEAST-INVASIVE DEFAULT this build chose, and each
# default is a numbered pick returning to [USER] in sec.12.
# --------------------------------------------------------------------------

def test_c1_the_summon_op_is_an_idempotent_no_op(base_kit):
    """Pick 1. `bake_kurage`'s first leg sets a bit that is already set; its
    second leg (gain_charge 1) still pays."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    before = st.player.charge
    play = loader.get_card(DROP)
    st.player.energy = 3
    st.player.hand.append(play)
    combat.play_card(st, play)
    assert st.player.powers["kurage_summon"] == 1
    assert st.player.charge == before + 1
    assert [e for e in st.log
            if e["event"] == "summon_kurage" and e.get("base_kit")]


def test_c2_the_kurage_turns_upgrade_is_inert(base_kit):
    """Pick 2. An upgraded Bake-Kurage is mechanically identical to a base
    one, exactly as it already was under v3."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    effects._op_summon_kurage(st, {"op": "summon_kurage", "amount": 2},
                              loader.get_card(DROP + "+"))
    assert st.player.powers["kurage_summon"] == 1


def test_c3_the_casket_refresh_pays_nothing(base_kit):
    """Pick 3. Refreshing a jellyfish that never expires is a max(1, 1)."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    effects.OPS["apply_power"](st, {"op": "apply_power",
                                    "power": "ceremonial_garment",
                                    "amount": 1, "target": "self"},
                               loader.get_card("waters_edge"))
    assert st.player.powers["kurage_summon"] == 1


def test_c4_the_oaths_ward_is_ruled_and_no_longer_rides_the_pulse(base_kit):
    """Pick 4 is RULED ([USER], 2026-08-29) and the default this test used to
    pin is gone: the pulse no longer carries the ward at all, however many
    stacks are standing. The ward's own section below has the rest."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.powers["kurage_ward"] = 5
    st.kurage_last_card_type = "skill"
    paid = []
    for _ in range(3):
        st.player.block = 0
        effects.player_turn_end_triggers(st)
        paid.append(st.player.block)
    assert paid == [C.KURAGE_MEMORY_PULSE_BLOCK] * 3


def test_c5_the_fires_summon_gate_can_no_longer_fail_in_a_real_fight(
        base_kit):
    """Pick 5. `KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON` is retired-under-flag:
    both settings read the same while the jellyfish cannot be absent."""
    st = kokomi_state()
    assert st.player.powers.get("kurage_summon", 0) == 0   # a bare state
    st = fight()
    assert st.player.powers.get("kurage_summon", 0) == 1   # a real fight


# --------------------------------------------------------------------------
# KURAGE'S OATH, RE-KEYED TO THE MEMORY PLAY (sec.12.4 pick 4, RULED).
#
# [USER], 2026-08-29: "Let's rewrite it to '3 block per memory played,
# upgrade to 5' as a placeholder and see if it needs adjusting later."
#
# The numbers are a PLACEHOLDER in [USER]'s own word and nothing here is a
# balance claim; the tests below are about WHEN the ward pays and about the
# face carrying the ruled figures, never about whether they are right.
# --------------------------------------------------------------------------

def armed(entries, charge=0, ward=0):
    """A state with the base kit installed, a memory queue, and optionally
    the Oath standing."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.charge = charge
    if ward:
        st.player.powers["kurage_ward"] = ward
    st.kurage_queue.extend(entries)
    return st


def memory_entry(price=0, card_id="gorou_inuzaka_charge"):
    return KurageMemory(card_id=card_id, cost=price // 3, price=price)


def test_the_ward_pays_on_the_automatic_memory_play(base_kit):
    st = armed([memory_entry()], ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is True
    assert st.player.block == 3
    paid = [e for e in st.log if e["event"] == "kurage_ward_paid"]
    assert len(paid) == 1 and paid[0]["amount"] == 3
    assert paid[0]["manual"] is False


def test_the_ward_pays_on_a_stir_play_too(base_kit):
    """The acceleration keyword fires the front outside the automatic
    rhythm, and a memory play is a memory play."""
    st = armed([memory_entry()], ward=3)
    st.player.block = 0
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("waters_edge"))
    assert st.player.block == 3
    paid = [e for e in st.log if e["event"] == "kurage_ward_paid"]
    assert len(paid) == 1 and paid[0]["manual"] is True


def test_the_ward_does_not_pay_on_the_pulse_under_the_flag(base_kit):
    """THE HALF THAT MOVED. Under the base kit the pulse fires every turn
    end; if the ward still rode it, the Oath would pay per turn for free."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.powers["kurage_ward"] = 3
    st.kurage_last_card_type = "skill"
    st.player.block = 0
    effects.player_turn_end_triggers(st)
    assert st.player.block == C.KURAGE_MEMORY_PULSE_BLOCK
    assert not [e for e in st.log if e["event"] == "kurage_ward_paid"]


def test_a_blocked_memory_pays_no_ward(base_kit):
    """The ward is per memory PLAYED. A front she cannot afford is not a
    play, so it pays nothing -- which is the whole reason the trigger moved
    off a pulse that cannot be blocked out of."""
    st = armed([memory_entry(price=9)], charge=1, ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is False
    assert st.player.block == 0
    assert not [e for e in st.log if e["event"] == "kurage_ward_paid"]


def test_an_empty_memory_pays_no_ward(base_kit):
    st = armed([], ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is False
    assert st.player.block == 0


def test_the_ward_is_paid_once_per_play_not_once_per_turn(base_kit):
    """Two fires in one turn (the automatic one plus a Stir) pay twice."""
    st = armed([memory_entry(), memory_entry()], ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is True
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("waters_edge"))
    assert st.player.block == 6
    assert len([e for e in st.log if e["event"] == "kurage_ward_paid"]) == 2


def test_the_amount_is_the_cards_and_never_a_constant(base_kit):
    """3 base, 5 upgraded -- and both come off whatever stacks the card
    applied, so there is no code-side override that could disagree with the
    printed face."""
    for stacks in (3, 5):
        st = armed([memory_entry()], ward=stacks)
        st.player.block = 0
        assert effects.kurage_fire(st) is True
        assert st.player.block == stacks


def test_the_surface_row_prints_the_ruled_placeholder(base_kit):
    """The FACE half of the ruling: the staged row carries [USER]'s 3, on
    the quarantined surface, with the shipped row untouched."""
    rows = {c.id: c for c in loader.prototype_cards()}
    row = rows["proto_kurages_oath_memory"]
    assert row.name == "Kurage's Oath"
    assert (row.cost, row.type, row.rarity) == (1, "power", "common")
    assert row.effects == [{"op": "apply_power", "power": "kurage_ward",
                            "amount": 3, "target": "self"}]


def test_the_shipped_oath_row_did_not_move():
    """No flag, no fixture: the printed sheet is untouched by all of this."""
    shipped = loader.get_card("kurages_oath")
    assert shipped.effects == [{"op": "apply_power", "power": "kurage_ward",
                                "amount": 5, "target": "self"}]
    assert loader.get_card("kurages_oath+").effects[0]["amount"] == 7


def test_flag_off_the_ward_still_rides_the_pulse():
    """THE HARD REQUIREMENT. With the flag off the shipped Oath is exactly
    what it has always been: its ward is paid by the jellyfish's pulse, on
    top of KURAGE_PULSE_BLOCK, and no memory play exists to pay it."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.powers["kurage_ward"] = 5
    st.player.block = 0
    effects.player_turn_end_triggers(st)
    assert st.player.block == C.KURAGE_PULSE_BLOCK + 5
    assert not [e for e in st.log if e["event"] == "kurage_ward_paid"]


# --------------------------------------------------------------------------
# THE SMOKE: five whole starter-deck fights, no numbers claimed
# --------------------------------------------------------------------------

def test_five_starter_fights_run_to_completion_under_the_base_kit(base_kit):
    """NO NUMBER IS ASSERTED and none may be quoted. sec.12 reports the
    SHAPE this same run produced; the pilot does not value the memory, so
    this exercises the rule and never the decision."""
    for seed in (1, 2, 3, 4, 5):
        st = fight(seed=seed)
        assert st.over or not st.living_enemies or not st.player.alive
        assert not [e for e in st.log if e["event"] == "UNIMPLEMENTED"]
