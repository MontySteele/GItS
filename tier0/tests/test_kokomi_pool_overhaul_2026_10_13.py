"""THE KOKOMI POOL OVERHAUL (2026-10-13), the sim side.

Paper `review/active/kokomi-pool-overhaul-2026-10-13.md`, picks 1 (a) and
2 (a); [USER]: "On Kokomi, I'm good with default on 1 and 2." Eight rewrites
(sec.3), six cuts and six new cards (sec.4), and the readings the paper lists:

  * CHAIN -- "Plans carried out this turn" counts the Plan being carried out;
  * COUNTER -- "since you planned this" is per Plan, from the moment it is
    written until it is carried out: damage she blocked, whether an enemy
    attacked her, all the damage enemies dealt her (blocked or not);
  * INTENT -- read at landing, like Flank;
  * "triggers an Elemental Reaction" -- the card's or the Companion's own hit.

Provenance note "Kokomi pool overhaul, 2026-10-13". The C# twin is
`klee-mod/KleeTests/Prototype/KokomiPoolOverhaulTests.cs`. NOTHING MEASURED
HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import collections

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects, kokomi_plan
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, reactions, write)

ATTACK = [{"kind": "attack", "amount": 6}]

CUT = ("proto_kk_riptide_guard", "proto_kk_reserves",
       "proto_kk_brace_for_the_tide", "proto_kk_moons_reflection",
       "proto_kk_ceremonial_garment", "proto_kk_watatsumi_resistance")
# Jellyfish Current left with the Kokomi review r6 (2026-10-14, pick 2 (b));
# Kurage Vanguard holds its slot (`test_kokomi_review_r6_2026_10_14`).
NEW = ("proto_kk_turning_tide_chain", "proto_kk_brine_spray",
       "proto_kk_prepared_retreat",
       "proto_kk_battle_formation", "proto_kk_turnabout")


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _play(st, c):
    """Play `c` face-up: some enemy intends to attack, so the pilot does not
    write it."""
    for e in st.enemies:
        e.intents = list(ATTACK)
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


def _draw_plan(i):
    return Card(id=f"proto_kk_probe{i}", name=f"Probe {i}", cost=0,
                type="skill", effects=[],
                plan=[{"op": "draw", "amount": 1}])


# --- the pool -------------------------------------------------------------------

def test_each_new_card_takes_the_slot_of_the_cut_card_of_its_rarity():
    ids = list(C.KOKOMI_OVERHAUL_POOL_IDS)
    rows = {c.id for c in loader.prototype_cards()}
    for cid in CUT:
        assert cid not in ids and cid not in rows, cid
    for cid in NEW:
        assert cid in ids and cid in rows, cid
    assert len(ids) == 78
    rarity = collections.Counter(loader.get_card(cid).rarity for cid in ids)
    assert rarity == {"common": 20, "uncommon": 38, "rare": 20}
    # The re-founding's cut Turning Tide keeps its own id, cut.
    assert "proto_kk_turning_tide" not in rows


@pytest.mark.parametrize("cid,rarity,ctype,cost", [
    ("proto_kk_turning_tide_chain", "common", "attack", 1),
    ("proto_kk_brine_spray", "uncommon", "attack", 1),
    ("proto_kk_prepared_retreat", "uncommon", "skill", 1),
    ("proto_kk_battle_formation", "rare", "power", 1),
    ("proto_kk_turnabout", "rare", "skill", 2),
])
def test_the_six_new_cards(cid, rarity, ctype, cost):
    row = loader.get_card(cid)
    assert (row.rarity, row.type, row.cost) == (rarity, ctype, cost)
    assert _up(cid).id.startswith(cid)


def test_the_new_cards_numbers_and_upgrades():
    tide = loader.get_card("proto_kk_turning_tide_chain")
    # Numbers pass (kokomi-review-r5-2026-10-14): 9 [12] / Plan 5 [6];
    # Retreat 8 [11]; Brine Spray 8 [10].
    assert tide.effects == [{"op": "damage", "amount": 9, "target": "enemy"}]
    assert tide.plan == [{"op": "damage_per_plan_this_turn", "amount": 5,
                          "target": "all_enemies"}]
    up = _up("proto_kk_turning_tide_chain")
    assert (up.effects[0]["amount"], up.plan[0]["amount"]) == (12, 6)
    retreat = loader.get_card("proto_kk_prepared_retreat")
    assert retreat.effects == [{"op": "block", "amount": 8}]
    assert retreat.plan == [{"op": "energy_if_attacked_since", "amount": 1}]
    up = _up("proto_kk_prepared_retreat")
    assert (up.effects[0]["amount"], up.plan[0]["amount"]) == (11, 2)
    turnabout = loader.get_card("proto_kk_turnabout")
    assert turnabout.effects == [] and turnabout.exhaust
    assert turnabout.plan == [{"op": "damage_taken_since",
                               "target": "all_enemies"}]
    assert _up("proto_kk_turnabout").cost == 1   # the Prototype-stage rule
    spray = loader.get_card("proto_kk_brine_spray")
    assert spray.effects[0]["amount"] == 8
    assert _up("proto_kk_brine_spray").effects[0]["amount"] == 10
    assert _up("proto_kk_battle_formation").innate


def test_the_rewrites_numbers():
    # Numbers pass (kokomi-review-r5-2026-10-14): Snare Block 5 and Plan
    # 4 [5]; Brine Sting 10 [13] / Plan 10 [13].
    snare = loader.get_card("proto_kk_undercurrent_snare")
    assert snare.effects[0] == {"op": "block", "amount": 5}
    assert snare.plan == [{"op": "lose_strength_this_turn", "amount": 4,
                           "target": "enemies_intending_attack"}]
    assert _up("proto_kk_undercurrent_snare").plan[0]["amount"] == 5
    sting = loader.get_card("proto_kk_brine_sting")
    assert sting.plan == [{"op": "damage", "amount": 10,
                           "target": "enemies_attacked_since"}]
    assert _up("proto_kk_brine_sting").plan[0]["amount"] == 13
    # Coordinated Tide left with the Kokomi review r6 (pick 2 (b)), which
    # moved Grand Strategist to 6 [8].
    strat = loader.get_card("proto_kk_grand_strategist")
    assert (strat.effects[0]["amount"],
            _up("proto_kk_grand_strategist").effects[0]["amount"]) == (6, 8)


def test_the_new_clauses_are_plan_only():
    for op in ("damage_per_plan_this_turn", "damage_blocked_since",
               "damage_taken_since", "energy_if_attacked_since",
               "lose_strength_this_turn", "draw_pile_to_hand"):
        assert op in kokomi_plan.PLAN_ONLY_OPS, op
        assert op in kokomi_plan.PLAN_KINDS, op
    assert "enemies_attacked_since" in kokomi_plan.PLAN_AIMS


# --- CHAIN: Plans carried out this turn, itself included ---------------------------

def test_a_lone_chain_line_counts_itself():
    st = kokomi_state()
    write(st, card("proto_kk_feint"))
    hp = st.enemies[0].hp
    carry_out(st)
    assert hp - st.enemies[0].hp == 6           # 6 x 1
    assert st.kk_plans_carried_out_this_turn == 1


def test_a_chain_line_third_in_the_queue_counts_three():
    st = kokomi_state()
    for i in range(2):
        kokomi_plan.schedule(st, _draw_plan(i))
    write(st, card("proto_kk_feint"))
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    hp = st.enemies[0].hp
    carry_out(st)
    assert hp - st.enemies[0].hp == 6 * 3


def test_turning_tide_hits_all_per_plan_and_the_turn_roll_clears():
    st = kokomi_state(n_enemies=2)
    kokomi_plan.schedule(st, _draw_plan(0))
    write(st, card("proto_kk_turning_tide_chain"))
    st.player.draw_pile = [card("proto_kk_coral_bulwark")]
    before = [e.hp for e in st.enemies]
    carry_out(st)
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [10, 10]
    kokomi_plan.roll_turn(st)
    assert st.kk_plans_carried_out_this_turn == 0


def test_change_of_plans_carry_out_counts_too():
    st = kokomi_state()
    write(st, card("proto_kk_feint"))
    kokomi_plan.resolve_front(st)
    assert st.kk_plans_carried_out_this_turn == 1


# --- COUNTER: since you planned this, per Plan ----------------------------------------

def test_kelp_wall_deals_what_she_blocked_since_its_own_writing():
    st = kokomi_state()
    e = st.enemies[0]
    kokomi_plan.note_enemy_hit(st, e, blocked=4, incoming=6)   # before
    write(st, card("proto_kk_kelp_wall"))
    kokomi_plan.note_enemy_hit(st, e, blocked=5, incoming=9)
    write(st, card("proto_kk_kelp_wall"))
    kokomi_plan.note_enemy_hit(st, e, blocked=3, incoming=3)
    hp = e.hp
    carry_out(st)
    # The first window saw 5 + 3, the second 3 alone; neither saw the 4.
    assert hp - e.hp == (5 + 3) + 3


def test_kelp_wall_counts_a_real_enemy_attack_into_block():
    st = kokomi_state()
    e = st.enemies[0]
    write(st, card("proto_kk_kelp_wall"))
    e.intents = [{"kind": "attack", "amount": 7}]
    st.in_player_turn = False
    st.player.block = 5
    combat._enemy_turn(st, e)
    assert st.kk_damage_blocked_total == 5
    assert st.kk_damage_taken_total == 7
    assert st.kk_attackers == [id(e)]
    st.in_player_turn = True
    hp = e.hp
    carry_out(st)
    assert hp - e.hp == 5


def test_brine_sting_hits_each_enemy_that_attacked_since():
    st = kokomi_state(n_enemies=3)
    a, b, c = st.enemies
    kokomi_plan.note_enemy_hit(st, c, blocked=0, incoming=4)   # before
    write(st, card("proto_kk_brine_sting"))
    kokomi_plan.note_enemy_hit(st, a, blocked=2, incoming=2)   # all blocked
    kokomi_plan.note_enemy_hit(st, a, blocked=0, incoming=3)   # twice: once
    before = [x.hp for x in st.enemies]
    carry_out(st)
    assert [p - x.hp for p, x in zip(before, st.enemies)] == [10, 0, 0]


def test_prepared_retreat_pays_energy_only_if_attacked():
    st = kokomi_state()
    write(st, card("proto_kk_prepared_retreat"))
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 0
    write(st, card("proto_kk_prepared_retreat"))
    kokomi_plan.note_enemy_hit(st, st.enemies[0], blocked=6, incoming=6)
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 1


def test_turnabout_deals_all_damage_taken_blocked_or_not_to_all():
    st = kokomi_state(n_enemies=2)
    write(st, card("proto_kk_turnabout"))
    kokomi_plan.note_enemy_hit(st, st.enemies[0], blocked=6, incoming=10)
    kokomi_plan.note_enemy_hit(st, st.enemies[1], blocked=0, incoming=4)
    before = [x.hp for x in st.enemies]
    carry_out(st)
    assert [p - x.hp for p, x in zip(before, st.enemies)] == [14, 14]


def test_the_counter_totals_are_hers_alone():
    st = kokomi_state()
    st.player.character_id = "klee"
    kokomi_plan.note_enemy_hit(st, st.enemies[0], blocked=5, incoming=5)
    assert st.kk_damage_taken_total == 0 and st.kk_attackers == []


# --- INTENT: Undercurrent Snare ------------------------------------------------------

def test_undercurrent_snare_takes_strength_this_turn_from_attackers_at_landing():
    st = kokomi_state(n_enemies=2)
    a, b = st.enemies
    write(st, card("proto_kk_undercurrent_snare"))
    a.intents = list(ATTACK)          # the intents when it LANDS are read
    carry_out(st)
    assert a.powers.get("temp_strength_down") == 4
    assert b.powers.get("temp_strength_down") is None


# --- Read the Field ------------------------------------------------------------------

def test_read_the_field_puts_a_draw_pile_card_into_the_hand():
    st = kokomi_state()
    write(st, card("proto_kk_read_the_field"))
    st.player.draw_pile = [card("proto_kk_coral_bulwark"),
                           card("proto_kk_masterstroke")]
    st.player.hand = []
    carry_out(st)
    assert len(st.player.hand) == 1
    assert len(st.player.draw_pile) == 1


# --- Battle Formation ---------------------------------------------------------------

def test_battle_formation_fires_once_when_the_second_plan_finishes():
    """Numbers pass (kokomi-review-r5-2026-10-14): 3 -> 2 Plans, draw 2 -> 1."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    for i in range(4):
        kokomi_plan.schedule(st, _draw_plan(i))
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(10)]
    carry_out(st)
    paid = [e for e in st.log if e["event"] == "plan_battle_formation"]
    assert len(paid) == 1
    assert paid[0]["energy"] == 1 and paid[0]["cards"] == 1
    events = [e["event"] for e in st.log]
    carried = [i for i, ev in enumerate(events) if ev == "plan_carried_out"]
    at = events.index("plan_battle_formation")
    assert carried[1] < at < carried[2]


def test_battle_formation_waits_for_two():
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    for i in range(1):
        kokomi_plan.schedule(st, _draw_plan(i))
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    carry_out(st)
    assert not [e for e in st.log if e["event"] == "plan_battle_formation"]


# --- REACTIONS: the card's or the Companion's own hit ------------------------------

def _stings(st):
    return sum(1 for c in st.player.hand
               if c.id.rstrip("+") == kokomi_plan.STING_ID)


def test_jellyfish_current_pays_for_a_stings_own_reaction():
    st = kokomi_state()
    st.player.powers[kokomi_plan.JELLYFISH_CURRENT] = 1
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    _play(st, card(kokomi_plan.STING_ID))
    assert "electrocharged" in reactions(st)
    assert _stings(st) == 1
    # The aura is gone: the next Sting refreshes Hydro and reacts with
    # nothing, so the loop ends (each reaction consumes the aura).
    _play(st, st.player.hand.pop())
    assert _stings(st) == 0


def test_jellyfish_current_ignores_another_cards_reaction():
    st = kokomi_state()
    st.player.powers[kokomi_plan.JELLYFISH_CURRENT] = 1
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    _play(st, card("proto_kk_jellyfish_drift"))      # adds one Sting itself
    assert "electrocharged" in reactions(st)
    assert _stings(st) == 1


def test_a_written_stings_plan_line_reaction_is_the_stings():
    st = kokomi_state()
    st.player.powers[kokomi_plan.JELLYFISH_CURRENT] = 1
    write(st, card(kokomi_plan.STING_ID))
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    carry_out(st)
    assert "electrocharged" in reactions(st)
    assert _stings(st) == 1


def test_jellyfish_currents_loop_is_bounded_on_a_thin_deck():
    """The thin-deck loop rule's known set: a Sting reacts once per aura, and
    the Sting it makes finds the aura gone."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.JELLYFISH_CURRENT] = 3
    st.enemies[0].hp = st.enemies[0].max_hp = 999
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    _play(st, card(kokomi_plan.STING_ID))
    for _ in range(10):
        if not st.player.hand:
            break
        _play(st, st.player.hand.pop())
    assert reactions(st).count("electrocharged") == 1


def test_coordinated_tide_pays_for_a_companions_own_reaction():
    st = kokomi_state()
    st.player.powers[kokomi_plan.COORDINATED_TIDE] = 1
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "hydro", 2
    _play(st, card("proto_mi_shinobu_thundergrust"))
    assert "electrocharged" in reactions(st)
    assert _stings(st) == 1


def test_coordinated_tide_pays_for_a_written_companion_reacting_with_the_hydro():
    """Rule 8: a written Companion reacts with the Bake-Kurage's Hydro, so
    it makes Stings."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.COORDINATED_TIDE] = 1
    write(st, card("proto_mi_shinobu_thundergrust"))
    carry_out(st)
    assert "electrocharged" in reactions(st)
    assert _stings(st) == 1


def test_the_bake_kurages_own_hydro_is_not_the_companions_reaction():
    """A Companion written into an Electro aura: the pet's Hydro reacts first
    (hers, not the Companion's) and the Companion's Electro then lands on a
    bare body."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.COORDINATED_TIDE] = 1
    write(st, card("proto_mi_shinobu_thundergrust"))
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    carry_out(st)
    assert reactions(st) == ["electrocharged"]
    assert _stings(st) == 0


def test_coordinated_tide_ignores_her_own_cards():
    st = kokomi_state()
    st.player.powers[kokomi_plan.COORDINATED_TIDE] = 1
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    _play(st, card("proto_kk_undertow"))
    assert "electrocharged" in reactions(st)
    assert _stings(st) == 0


def test_grand_strategist_answers_any_reaction_she_triggers():
    st = kokomi_state(n_enemies=2)
    st.player.powers[kokomi_plan.GRAND_STRATEGIST] = 4
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
    back = st.enemies[1].hp
    _play(st, card(kokomi_plan.STING_ID))             # a card, not a Plan
    assert "electrocharged" in reactions(st)
    assert back - st.enemies[1].hp == 4


def test_all_streams_counts_the_reactions_she_triggered_this_combat():
    st = kokomi_state()
    st.enemies[0].hp = st.enemies[0].max_hp = 500
    for _ in range(2):
        st.enemies[0].aura, st.enemies[0].aura_turns_left = "electro", 2
        _play(st, card(kokomi_plan.STING_ID))
    assert st.kk_reactions_this_combat == 2
    kokomi_plan.roll_turn(st)
    st.enemies[0].aura = None
    hp = st.enemies[0].hp
    _play(st, card("proto_kk_all_streams_flow"))
    assert hp - st.enemies[0].hp == 10 + 5 * 2


def test_brine_spray_adds_two_stings_only_when_its_hit_reacts():
    st = kokomi_state()
    _play(st, card("proto_kk_brine_spray"))
    assert _stings(st) == 0
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "cryo", 2
    _play(st, card("proto_kk_brine_spray"))
    assert len(reactions(st)) == 1
    assert _stings(st) == 2


def test_no_card_is_credited_after_a_play_ends():
    st = kokomi_state()
    _play(st, card(kokomi_plan.STING_ID))
    assert st.kk_hit_card is None
