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
  * Drowning Pressure and Ceremonial Garment count STACKS of Weak plus
    stacks of Vulnerable (the Kokomi card pass, 2026-10-11);
  * At Water's Edge answers her first Hydro damage each turn (the same pass);
  * "fully Blocked" is a hit Block absorbed whole, once per hit;
  * Watatsumi's Grace is the base game's Sturdy Clamp shape;
  * All Streams refunds nothing, and its gift is taken by the next card
    written on the Bake-Kurage this turn;
  * Kurage Swarm reads the cost paid when the Plan is written.

THE RE-FOUNDING (2026-10-12) cut Weight of the Plan, Lull, The Long Game,
Salt in the Wound, Tidal Resonance and Kurage Swarm, retired Dusk (Evening
Watch and Brace for the Tide are now-lines) and the Energy-paid record, made
Undertide Lance and Masterstroke flat Plans, and put Stings in Shoal Call;
Grand Design is a new card under the old name. The tests below are the
batch's survivors at their current numbers.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects, kokomi_plan, powers, reactions
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, kokomi_state, overhaul, plan_card, plan_line)

#: The batch's rows still in her pool after the re-founding (2026-10-12),
#: the jellyfish build (2026-10-12), which cut Measured Breath, and the pool
#: overhaul (2026-10-13), which cut Ceremonial Garment and Brace for the Tide.
NEW = (
    "proto_kk_undertide_lance",
    "proto_kk_grand_design", "proto_kk_masterstroke",
    "proto_kk_drowning_pressure", "proto_kk_undercurrent_snare",
    "proto_kk_at_waters_edge",
    "proto_kk_suffocating_deep", "proto_kk_coral_crash",
    "proto_kk_evening_watch",
    "proto_kk_watatsumis_grace", "proto_kk_tidal_riposte",
    "proto_kk_shoal_call",
)
CUT = ("proto_kk_weight_of_the_plan", "proto_kk_lull",
       "proto_kk_the_long_game", "proto_kk_salt_in_the_wound",
       "proto_kk_tidal_resonance", "proto_kk_kurage_swarm",
       "proto_kk_ceremonial_garment", "proto_kk_brace_for_the_tide")
QUIET = [{"kind": "block", "amount": 5}]


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


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

def test_the_batchs_survivors_are_in_the_pool_and_the_cuts_are_not(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert set(NEW) <= set(ids)
    rows = {c.id for c in loader.prototype_cards()}
    for cid in CUT + ("proto_kk_all_streams_flow_to_the_sea",
                      "proto_kk_measured_breath"):
        assert cid not in ids and cid not in rows
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
    """The re-founding (2026-10-12): a flat 42 [54], no Strength rider."""
    card = _row("proto_kk_masterstroke")
    assert card.type == "attack" and card.cost == 3 and card.retain
    assert card.effects == []
    assert card.plan == [{"op": "damage", "amount": 42,
                          "target": "front_enemy"}]
    assert _up("proto_kk_masterstroke").plan[0]["amount"] == 54


# --- the Big Plan ---------------------------------------------------

def test_undertide_lance_plans_a_flat_eighteen(overhaul):
    """The re-founding (2026-10-12): a flat 18 to the front enemy, alone or
    not (the "carried out alone" doubling is gone)."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_undertide_lance"))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 18

    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_undertide_lance"))
    kokomi_plan.schedule(st, plan_card([{"op": "block", "amount": 1}]))
    kokomi_plan.resolve_all(st)
    assert enemy.hp == 200 - 18


# --- Tide Control ---------------------------------------------------------------

def test_drowning_pressure_counts_weak_and_vulnerable_stacks(overhaul):
    """The Kokomi card pass (2026-10-11, pick 1): "Deal 3 [4] Hydro damage for
    each Weak and Vulnerable on the enemy" -- STACKS. 2 Weak + 2 Vulnerable
    is 4; the card's own 1 Weak and 1 Vulnerable (the Kokomi level pass,
    2026-10-12) make 6, so 18; the Vulnerable then multiplies the hit (x1.5)
    to 27. Poison is a debuff and not counted; an aura is not counted."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 2, applier=st.player)
    powers.apply_power(st, enemy, "vulnerable", 2, applier=st.player)
    powers.apply_power(st, enemy, "poison", 3, applier=st.player)
    assert kokomi_plan.weak_vuln_stacks(enemy) == 4
    card = _row("proto_kk_drowning_pressure")
    assert card.effects[:2] == [
        {"op": "apply_power", "power": "weak", "amount": 1, "target": "enemy"},
        {"op": "apply_power", "power": "vulnerable", "amount": 1,
         "target": "enemy"}]
    assert card.effects[2]["amount_formula"] == {
        "base": 0, "per": 3, "count": "weak_vuln_stacks_on_target"}
    assert effects._runtime_count(st, "weak_vuln_stacks_on_target") == 4
    before = enemy.hp
    _write(st, card, energy=1)
    assert before - enemy.hp == 27                 # 18, x1.5 Vulnerable
    assert _up("proto_kk_drowning_pressure").effects[2][
        "amount_formula"]["per"] == 4


def test_drowning_pressures_floor_is_its_own_debuffs(overhaul):
    """The Kokomi level pass (2026-10-12): on a clean enemy it applies 1 Weak
    and 1 Vulnerable first, so it deals 6, x1.5 Vulnerable = 9."""
    enemy = make_enemy(hp=200)
    st = kokomi_state(enemies=[enemy])
    _write(st, _row("proto_kk_drowning_pressure"), energy=1)
    assert 200 - enemy.hp == 9


def test_undercurrent_snare_plans_vulnerable_on_all(overhaul):
    """The pool overhaul (2026-10-13): the Plan line is an Intent read --
    each enemy that intends to attack when it lands loses 4 Strength this
    turn (Piercing Wail's `temp_strength_down`; 3 -> 4 in the numbers pass,
    kokomi-review-r5-2026-10-14); no Vulnerable any more."""
    a, b = make_enemy(hp=100, name="a"), make_enemy(hp=100, name="b",
                                                     intents=QUIET)
    st = kokomi_state(enemies=[a, b])
    kokomi_plan.schedule(st, _row("proto_kk_undercurrent_snare"))
    kokomi_plan.resolve_all(st)
    assert a.powers.get("temp_strength_down") == 4
    assert b.powers.get("temp_strength_down") is None
    assert a.powers.get("vulnerable") is None


def test_at_waters_edge_fires_once_per_turn_on_hydro_damage(overhaul):
    """The Kokomi card pass (2026-10-11): "The first time each turn you deal
    Hydro damage to an enemy, apply 1 Weak and 1 Vulnerable to it." Once a
    turn: the second Hydro hit pays nothing; a non-Hydro hit never claims it;
    the next turn pays again. A reaction no longer triggers it."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = kokomi_state(enemies=[a, b])
    st.player.powers[kokomi_plan.AT_WATERS_EDGE] = 1
    effects.deal_damage_to_enemy(st, a, 3, element=None)
    assert a.powers.get("weak") is None
    effects.deal_damage_to_enemy(st, a, 3, element="hydro")
    assert a.powers.get("weak") == 1 and a.powers.get("vulnerable") == 1
    effects.deal_damage_to_enemy(st, a, 3, element="hydro")
    effects.deal_damage_to_enemy(st, b, 3, element="hydro")
    assert a.powers.get("weak") == 1 and a.powers.get("vulnerable") == 1
    assert b.powers.get("weak") is None
    kokomi_plan.roll_turn(st)
    effects.deal_damage_to_enemy(st, b, 3, element="hydro")
    assert b.powers.get("weak") == 1 and b.powers.get("vulnerable") == 1
    # A reaction alone pays nothing now.
    kokomi_plan.roll_turn(st)
    c = make_enemy(hp=200, name="c")
    c.aura, c.aura_turns_left = "pyro", 2
    reactions.resolve_hit(st, c, "hydro", 0, "probe")
    assert c.powers.get("weak") is None


def test_ceremonial_garment_adds_per_weak_and_vulnerable_stack(overhaul):
    """The Kokomi card pass (2026-10-11): stacks of Weak plus stacks of
    Vulnerable, on an Attack only; Poison is not counted."""
    enemy = make_enemy(hp=300)
    st = kokomi_state(enemies=[enemy])
    card = _row("proto_kk_pincer")                # an Attack
    assert kokomi_plan.garment_bonus(st, card, enemy) == 0
    st.player.powers[kokomi_plan.CEREMONIAL_GARMENT] = 1
    powers.apply_power(st, enemy, "weak", 2, applier=st.player)
    powers.apply_power(st, enemy, "vulnerable", 1, applier=st.player)
    powers.apply_power(st, enemy, "poison", 2, applier=st.player)
    assert kokomi_plan.garment_bonus(st, card, enemy) == 3
    assert kokomi_plan.garment_bonus(
        st, _row("proto_kk_coral_bulwark"), enemy) == 0


def test_suffocating_deep_doubles_weak_and_vulnerable(overhaul):
    enemy = make_enemy(hp=300)
    st = kokomi_state(enemies=[enemy])
    powers.apply_power(st, enemy, "weak", 2, applier=st.player)
    powers.apply_power(st, enemy, "vulnerable", 3, applier=st.player)
    _write(st, "proto_kk_suffocating_deep")
    # The Rare pass (2026-10-04): 1 of each first, then the doubling.
    assert enemy.powers.get("weak") == 6
    assert enemy.powers.get("vulnerable") == 8


def test_suffocating_deep_never_doubles_nothing(overhaul):
    """The Rare pass (2026-10-04): on a clean enemy it leaves Weak 2 and
    Vulnerable 2, where it used to leave none."""
    enemies = [make_enemy(hp=300), make_enemy(hp=300)]
    st = kokomi_state(enemies=enemies)
    _write(st, "proto_kk_suffocating_deep")
    assert [(e.powers.get("weak"), e.powers.get("vulnerable"))
            for e in enemies] == [(2, 2), (2, 2)]


# --- Guard (Dusk retired 2026-10-12) ---------------------------------------------------------------------

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
    _library(st)
    _write(st, "proto_kk_evening_watch")
    # The re-founding (2026-10-12): 4 [6] each, counted when played, then a
    # draw.
    assert st.player.block == 4 * 2
    assert len(st.player.hand) == 1


def test_brace_for_the_tide_doubles_block_now(overhaul):
    """The re-founding (2026-10-12): the base game's Entrench. The card left
    with the pool overhaul (2026-10-13); its `double_block` kind stays
    registered with no row spelling it, and still doubles."""
    st = kokomi_state()
    st.player.block = 13
    kokomi_plan.kind(st, {"op": "kokomi", "kind": "double_block"}, None, None)
    assert st.player.block == 26


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

def test_shoal_call_is_blade_dance(overhaul):
    """The jellyfish build (2026-10-12): the base game's Blade Dance. Cost 1,
    Exhaust, "Add 3 [4] Stings to your hand." -- plain Stings on both faces;
    the upgrade adds a fourth. Common since the Kokomi review (2026-10-13),
    as Blade Dance is."""
    row = _row("proto_kk_shoal_call")
    assert row.cost == 1 and row.exhaust and row.rarity == "common"
    st = kokomi_state()
    _write(st, "proto_kk_shoal_call")
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID] * 3
    st = kokomi_state()
    _write(st, _up("proto_kk_shoal_call"))
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID] * 4

