"""KOKOMI EXPANSION, BATCH ONE (2026-09-29): 22 rows, four decks.

Paper `review/active/kokomi-expansion-2026-09-29.md`, every pick ruled at its
default ([USER]: "The defaults work here"). The sim half; the C# twin is
`KleeTests/Prototype/KokomiExpansionTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).

The readings the build took where the paper is loose, pinned below:
  * "the Energy paid for the Plans waiting" is the sum of what was actually
    paid (after reductions) for each Plan in the queue;
  * "the only Plan carried out" is no OTHER entry in the same drain (Dusk is
    its own drain; the same entry carried out twice is one Plan);
  * a "debuff" is a distinct debuff power; an aura is a Buff and not one;
  * At Water's Edge answers any reaction, whoever caused it;
  * "fully Blocked" is a hit Block absorbed whole, once per hit;
  * Watatsumi's Grace is the base game's Sturdy Clamp shape;
  * All Streams refunds nothing, and its gift is taken by the next card
    written on the Bake-Kurage this turn;
  * Kurage Swarm reads the cost paid when the Plan is written.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects, kokomi_plan, powers, reactions
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, kokomi_state, overhaul, plan_card)

NEW = C.KOKOMI_EXPANSION_BATCH_ONE_IDS
QUIET = [{"kind": "block", "amount": 5}]


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _casket(**kw):
    st = kokomi_state(**kw)
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    return st


def _write(st, cid, energy=10):
    """Play a card onto the Bake-Kurage through the real play path, so the
    Energy it paid is the one `combat.play_card` recorded."""
    card = _row(cid) if isinstance(cid, str) else cid
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


def _library(st, n=10):
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_lib{i}")
                           for i in range(n)]


# --- the batch -----------------------------------------------------------------

def test_the_batch_is_twelve_uncommon_and_ten_rare_last_in_the_pool(overhaul):
    rarities = [_row(cid).rarity for cid in NEW]
    # Pool completion (2026-10-01, paper sec.6) moved Coral Crash to Common.
    assert rarities.count("uncommon") == 11
    assert rarities.count("common") == 1
    assert rarities.count("rare") == 10
    # The payoff pass (2026-10-01) appended two rows after the batch, and
    # pool completion eight more.
    assert C.KOKOMI_OVERHAUL_POOL_IDS[-32:-10] == NEW
    assert "proto_kk_the_clouds_like_waves" not in C.KOKOMI_OVERHAUL_POOL_IDS
    assert "proto_kk_the_clouds_like_waves" not in {
        c.id for c in loader.prototype_cards()}
    assert not hasattr(kokomi_plan, "CLOUDS_LIKE_WAVES")
    assert not hasattr(kokomi_plan, "note_debuff_applied")


def test_every_new_row_loads_and_smiths(overhaul):
    for cid in NEW:
        up = _up(cid)
        assert up.id.startswith(cid), cid


def test_masterstroke_is_a_retained_plan_only_attack(overhaul):
    card = _row("proto_kk_masterstroke")
    assert card.type == "attack" and card.cost == 3 and card.retain
    assert card.effects == []
    assert card.plan == [{"op": "damage", "amount": 30,
                          "target": "front_enemy"}]
    assert _up("proto_kk_masterstroke").plan[0]["amount"] == 40


# --- the Big Plan: Energy paid ---------------------------------------------------

def test_the_queue_remembers_the_energy_paid(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=200, intents=QUIET)])
    _write(st, "proto_kk_surging_shoal")          # 2 paid
    _write(st, "proto_kk_nip")                    # 0 paid
    assert [e.paid for e in st.kk_plan_queue] == [2, 0]
    assert kokomi_plan.plan_energy_waiting(st) == 2


def test_weight_of_the_plan_reads_the_energy_paid_not_the_count(overhaul):
    enemy = make_enemy(hp=200, intents=QUIET)
    st = kokomi_state(enemies=[enemy])
    for _ in range(3):
        _write(st, "proto_kk_nip")                 # three feeders, 0 each
    before = enemy.hp
    _write(st, "proto_kk_weight_of_the_plan")
    assert before - enemy.hp == 5                  # feeders never scale it
    _write(st, "proto_kk_surging_shoal")           # 2 paid
    before = enemy.hp
    _write(st, "proto_kk_weight_of_the_plan")
    assert before - enemy.hp == 5 + 3 * 2


def test_a_reduced_cost_is_what_was_paid(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=200, intents=QUIET)])
    st.player.powers[kokomi_plan.FIRST_CARD_FREE] = 1
    _write(st, "proto_kk_surging_shoal")
    assert st.kk_plan_queue[0].paid == 0


def test_lull_pays_only_when_it_is_the_only_plan_of_the_morning(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule(st, _row("proto_kk_lull"))
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 2

    st = kokomi_state()
    kokomi_plan.schedule(st, _row("proto_kk_lull"))
    kokomi_plan.schedule(st, plan_card([{"op": "block", "amount": 1}]))
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 0


def test_the_same_plan_twice_is_still_alone(overhaul):
    st = kokomi_state()
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    kokomi_plan.schedule(st, _row("proto_kk_lull"))
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 4                   # carried out twice, alone


def test_a_dusk_plan_does_not_count_against_the_morning(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule(st, _row("proto_kk_lull"))
    kokomi_plan.schedule(st, _row("proto_kk_breakwater"))     # Dusk
    kokomi_plan.resolve_dusk(st)
    st.player.energy = 0
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 2


def test_undertide_lance_doubles_alone(overhaul):
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_undertide_lance"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 24

    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_undertide_lance"))
    kokomi_plan.schedule(st, plan_card([{"op": "block", "amount": 1}]))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 12


def test_measured_breath_draws_only_on_an_empty_queue(overhaul):
    st = kokomi_state()
    _library(st)
    _write(st, "proto_kk_measured_breath")
    assert st.player.block == 6 and len(st.player.hand) == 2

    st = kokomi_state(enemies=[make_enemy(hp=200, intents=QUIET)])
    _library(st)
    _write(st, "proto_kk_nip")
    _write(st, "proto_kk_measured_breath")
    assert st.player.block == 6 and len(st.player.hand) == 0


def test_grand_design_adds_one_per_energy_paid(overhaul):
    """Main session, 2026-09-29: "the Casket gains 1 more for each Energy
    paid for it"."""
    st = _casket(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.powers[kokomi_plan.GRAND_DESIGN] = 1
    _write(st, "proto_kk_surging_shoal")           # 2 paid
    _write(st, "proto_kk_nip")                     # 0 paid
    kokomi_plan.resolve_all(st)
    assert st.kk_casket == (1 + 2) + 1
    # Power cost sweep, 2026-09-30: cost stays 1, the upgrade is Innate.
    assert _up("proto_kk_grand_design").cost == 1
    assert _up("proto_kk_grand_design").innate


def test_the_long_game_pays_on_exactly_one_waiting(overhaul):
    st = kokomi_state()
    st.player.powers[kokomi_plan.LONG_GAME] = 1
    st.player.energy = 3
    kokomi_plan.long_game(st, 1)
    assert st.player.energy == 4
    kokomi_plan.long_game(st, 2)
    kokomi_plan.long_game(st, 0)
    assert st.player.energy == 4


def test_all_streams_cancels_without_refund_and_multiplies_the_next_plan(overhaul):
    """Main session, 2026-10-01: "Cancel all your Plans and take their cards
    back." No Energy comes back."""
    enemy = make_enemy(hp=300, intents=QUIET)
    st = kokomi_state(enemies=[enemy])
    _write(st, "proto_kk_nip")                     # 0 paid
    _write(st, "proto_kk_surging_shoal", energy=2)  # 2 paid
    _write(st, "proto_kk_all_streams_flow_to_the_sea", energy=1)
    assert st.kk_plan_queue == []
    assert st.player.energy == 0                   # nothing is refunded
    assert st.kk_next_plan_extra == 2
    _write(st, "proto_kk_surging_shoal", energy=2)
    assert st.kk_plan_queue[0].extra == 2
    assert st.kk_next_plan_extra is None
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 300 - 3 * 22                # once, plus once per cancel
    assert _row("proto_kk_all_streams_flow_to_the_sea").cost == 1
    assert _up("proto_kk_all_streams_flow_to_the_sea").cost == 0


def test_the_all_streams_gift_dies_with_the_turn(overhaul):
    st = kokomi_state()
    kokomi_plan.all_streams(st)
    assert st.kk_next_plan_extra == 0
    kokomi_plan.roll_turn(st)
    assert st.kk_next_plan_extra is None


# --- Tide Control ---------------------------------------------------------------

def test_drowning_pressure_counts_distinct_debuffs_not_auras(overhaul):
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 3, applier=st.player)
    powers.apply_power(st, enemy, "vulnerable", 1, applier=st.player)
    enemy.aura = "pyro"
    enemy.aura_turns_left = 2
    st.player.energy = 1
    before = enemy.hp
    _write(st, "proto_kk_drowning_pressure", energy=1)
    # 4 per debuff, two debuffs; Vulnerable multiplies (x1.5) and the Hydro
    # on Pyro vaporizes -- read against the plain 8 by ratio, not by value.
    assert kokomi_plan.debuff_count(enemy) == 2
    assert before - enemy.hp > 8


def test_salt_in_the_wound_draws_only_off_weak(overhaul):
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    _library(st)
    _write(st, "proto_kk_salt_in_the_wound")
    assert enemy.powers.get("vulnerable") == 1 and len(st.player.hand) == 0
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    _write(st, _up("proto_kk_salt_in_the_wound"))
    assert len(st.player.hand) == 2


def test_undercurrent_snare_plans_vulnerable_on_all(overhaul):
    a, b = make_enemy(hp=100, name="a"), make_enemy(hp=100, name="b")
    st = kokomi_state(enemies=[a, b])
    kokomi_plan.schedule(st, _row("proto_kk_undercurrent_snare"))
    kokomi_plan.resolve_all(st)
    assert a.powers.get("vulnerable") == 1 and b.powers.get("vulnerable") == 1


def test_tidal_resonance_draws_per_enemy_already_elemented(overhaul):
    a, b, c = (make_enemy(hp=100, name=n) for n in "abc")
    st = kokomi_state(enemies=[a, b, c])
    a.aura, a.aura_turns_left = "hydro", 2
    b.aura, b.aura_turns_left = "pyro", 2
    _library(st)
    _write(st, "proto_kk_tidal_resonance")
    assert len(st.player.hand) == 2
    assert c.aura == "hydro"


def test_at_waters_edge_answers_any_reaction(overhaul):
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    st.player.powers[kokomi_plan.AT_WATERS_EDGE] = 1
    enemy.aura, enemy.aura_turns_left = "pyro", 2
    reactions.resolve_hit(st, enemy, "hydro", 0, "probe")
    assert enemy.powers.get("weak") == 1
    assert enemy.powers.get("vulnerable") == 1


def test_ceremonial_garment_adds_per_debuff_on_an_attack_only(overhaul):
    enemy = make_enemy(hp=300)
    st = kokomi_state(enemies=[enemy])
    card = _row("proto_kk_massed_volley")         # 3 x3, an Attack
    assert kokomi_plan.garment_bonus(st, card, enemy) == 0
    st.player.powers[kokomi_plan.CEREMONIAL_GARMENT] = 1
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    powers.apply_power(st, enemy, "poison", 2, applier=st.player)
    assert kokomi_plan.garment_bonus(st, card, enemy) == 2
    assert kokomi_plan.garment_bonus(
        st, _row("proto_kk_coral_bulwark"), enemy) == 0


def test_suffocating_deep_doubles_weak_and_vulnerable(overhaul):
    enemy = make_enemy(hp=300)
    st = kokomi_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 2, applier=st.player)
    powers.apply_power(st, enemy, "vulnerable", 3, applier=st.player)
    _write(st, "proto_kk_suffocating_deep")
    assert enemy.powers.get("weak") == 4
    assert enemy.powers.get("vulnerable") == 6


# --- Dusk Guard ---------------------------------------------------------------------

def test_coral_crash_deals_her_block(overhaul):
    enemy = make_enemy(hp=300)
    st = kokomi_state(enemies=[enemy])
    st.player.block = 17
    before = enemy.hp
    _write(st, "proto_kk_coral_crash")
    assert before - enemy.hp == 17


def test_evening_watch_blocks_per_enemy_intending_to_attack(overhaul):
    a = make_enemy(hp=100, name="a")
    b = make_enemy(hp=100, name="b")
    c = make_enemy(hp=100, name="c", intents=QUIET)
    st = kokomi_state(enemies=[a, b, c])
    kokomi_plan.schedule(st, _row("proto_kk_evening_watch"))
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 10


def test_brace_for_the_tide_doubles_block_at_dusk(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule(st, _row("proto_kk_brace_for_the_tide"))
    st.player.block = 13
    kokomi_plan.resolve_dusk(st)
    assert st.player.block == 26
    assert _row("proto_kk_brace_for_the_tide").exhaust


def test_watatsumis_grace_keeps_up_to_the_cap(overhaul):
    st = kokomi_state()
    assert kokomi_plan.grace_keeps(st) is None
    st.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 10
    st.player.block = 25
    assert kokomi_plan.grace_keeps(st) == 10
    st.player.block = 6
    assert kokomi_plan.grace_keeps(st) == 6


def test_grace_through_a_real_turn_boundary(overhaul):
    """The whole fight loop: Block above the cap is lost at the clear."""
    seen = []

    def pilot(state):
        if state.turn == 1:
            state.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 10
            state.player.block = 40
        elif state.turn == 2 and not seen:
            seen.append(state.player.block)
        return None

    enemy = make_enemy(hp=500, intents=QUIET)
    player = kokomi_state().player
    player.hp = player.max_hp = 80
    combat.run_fight(player, [enemy], pilot, seed=1)
    assert seen and seen[0] == 10


def test_tidal_riposte_answers_a_fully_blocked_hit_once(overhaul):
    enemy = make_enemy(hp=100)
    st = kokomi_state(enemies=[enemy])
    st.player.powers[kokomi_plan.TIDAL_RIPOSTE] = 5
    kokomi_plan.tidal_riposte(st, enemy, blocked=6, unblocked=0)
    assert enemy.hp == 95
    kokomi_plan.tidal_riposte(st, enemy, blocked=3, unblocked=2)
    kokomi_plan.tidal_riposte(st, enemy, blocked=0, unblocked=0)
    assert enemy.hp == 95


# --- Plan volume ------------------------------------------------------------------------

def test_shoal_call_adds_two_nips_upgraded_when_it_is(overhaul):
    st = kokomi_state()
    _write(st, "proto_kk_shoal_call")
    assert [c.id for c in st.player.hand] == ["proto_kk_nip", "proto_kk_nip"]
    st = kokomi_state()
    _write(st, _up("proto_kk_shoal_call"))
    assert all(c.id == "proto_kk_nip" + upgrades.SUFFIX
               for c in st.player.hand)
    assert len(st.player.hand) == 2


def test_kurage_swarm_counts_zero_cost_writes(overhaul):
    st = _casket(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.powers[kokomi_plan.KURAGE_SWARM] = 1
    _write(st, "proto_kk_nip")
    _write(st, "proto_kk_bubble_ward")
    _write(st, "proto_kk_surging_shoal")
    assert st.kk_casket == 2
