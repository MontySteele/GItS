"""The Mondstadt companion overhaul's SECOND WAVE -- the thirteen rows whose
printed text needed an engine hook, and the hooks themselves.

The first pass (`test_companion_overhaul.py`) built twenty-one of the approved
workshop's thirty-four Universals and left thirteen out, each because its text
wanted something neither engine had. This file is the other thirteen. The
source is the same: `companion-workshop-mondstadt-2026-09-01.md` sec.3, a Paper
artefact on the companion-workshop branch and not in this tree.

THE FIRST SECTION IS STILL THE ONE THAT MATTERS. `C.COMPANION_OVERHAUL` ships
OFF, and every hook this branch adds sits on a shared path -- an enemy's attack,
a Block absorption, a reaction, a card's cost, the element an Attack applies.
So "flag off changes nothing" is not a property of the arm any more, it is a
property of five files that every shipped run walks, and it is pinned here
rather than intended.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, reactions
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

REPO = Path(__file__).resolve().parents[2]

#: The thirteen, in the workshop's sec.3 order. Read off the constant so the
#: two cannot drift, and sliced rather than listed so a fourteenth row added to
#: the tuple lands here too.
SECOND_WAVE = C.MONDSTADT_OVERHAUL_POOL_IDS[-13:]


def _caches_clear():
    loader._card_prototype.cache_clear()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared going in and out."""
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    _caches_clear()


def _play(state, card_id):
    effects.resolve_card(state, loader.get_card(card_id))


def _attack(cost=1, element="pyro", applies=True, amount=6):
    """A plain Attack card to swing the riders at."""
    return Card(id="probe", name="Probe", cost=cost, type="attack",
                element=element,
                effects=[{"op": "damage", "amount": amount, "target": "enemy",
                          "applies_element": applies}])


# ---------------------------------------------------------------------------
# THE FLAG IS OFF, AND THAT IS THE ACCEPTANCE CONDITION
# ---------------------------------------------------------------------------

def test_every_new_hook_is_a_no_op_with_the_flag_off():
    """Asserted against a state that CARRIES the arm's powers, because a hook
    that ran while the flag was off would be a silent second rule set on every
    shipped run -- and unlike the first pass's two turn blocks, these five sit
    on paths a shipped run walks every single turn."""
    st = make_state()
    st.player.powers.update({
        "mc_icy_paws": 6, "mc_sacramental_shower": 1, "mc_baron_bunny": 1,
        "mc_passion_overload": 4, "mc_lightning_fang": 2, "mc_swirl_charge": 6,
        "mc_favonian_favor": 3, "mc_sturm_und_drang": 6,
        "mc_binary_white": 1, "mc_binary_dark": 8, "mc_starfrost_discount": 1,
    })
    st.player.block = 10
    enemy = st.enemies[0]
    enemy.powers.update({"mc_melody_loop": 3, "mc_lightfall_sword": 2})
    before = (dict(st.player.powers), st.player.block, st.player.hp,
              dict(enemy.powers), enemy.hp, enemy.aura)

    assert effects.companion_overhaul_card_start(st, _attack()) == ""
    assert effects.companion_overhaul_before_enemy_hit(st, enemy, 12) == 12
    effects.companion_overhaul_block_absorbed(st, enemy, 5, 10)
    effects.companion_overhaul_reaction(st, enemy, "swirl", "hydro")
    assert effects.companion_overhaul_reaction_mult(st) == 1.0

    assert (dict(st.player.powers), st.player.block, st.player.hp,
            dict(enemy.powers), enemy.hp, enemy.aura) == before


def test_the_cost_discount_is_not_read_with_the_flag_off():
    st = make_state()
    st.player.powers["mc_starfrost_discount"] = 1
    assert combat.card_cost(st, _attack(cost=2)) == 2


def test_the_element_override_is_not_read_with_the_flag_off():
    """`_element_for` is the cadence dial every damage effect in the engine
    passes through, so this is the one that would be felt everywhere."""
    st = make_state()
    st.player.powers["mc_lightning_fang"] = 2
    st.mc_attack_element_override = ""
    card = _attack(element="pyro")
    assert effects._element_for(st, card.effects[0], card) == "pyro"


def test_the_new_predicate_is_registered_both_ways():
    """`test_content_boundaries` compares the registry to `_predicate`'s own
    if-chain in both directions; this is the arm's own half of that -- the
    prefix exists and a card can actually be validated against it."""
    assert "nth_attack_this_turn_" in effects.PREDICATE_PREFIXES
    assert effects.is_known_predicate("nth_attack_this_turn_3")
    assert not effects.is_known_predicate("nth_attack_this_turn_")


# ---------------------------------------------------------------------------
# THE FLAG IS ON: THE THIRTEEN ROWS EXIST AND ARE OFFERABLE
# ---------------------------------------------------------------------------

def test_all_thirteen_are_in_the_replacement_pool(overhaul):
    assert len(C.MONDSTADT_OVERHAUL_POOL_IDS) == 34
    roster = {c.id for c in loader.companion_roster_replacement()}
    for cid in SECOND_WAVE:
        assert cid in roster, cid


def test_every_second_wave_row_resolves_without_raising(overhaul):
    for cid in SECOND_WAVE:
        st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
        st.enemies[1].aura = "hydro"
        st.player.block = 9
        st.player.draw_pile = [Card(id=f"f{i}", name="f", cost=1,
                                    type="skill") for i in range(5)]
        _play(st, cid)
        effects.companion_overhaul_turn_end(st)
        effects.companion_overhaul_turn_start(st)


# ---------------------------------------------------------------------------
# DIONA -- THE BLOCK-ABSORPTION TRIGGER
# ---------------------------------------------------------------------------

def test_icy_paws_marks_the_block_it_granted(overhaul):
    st = make_state()
    _play(st, "proto_mc_diona_icy_paws")
    assert st.player.block == 6
    assert st.player.powers["mc_icy_paws"] == 6


def test_icy_paws_bites_the_attacker_and_the_mark_is_eaten(overhaul):
    st = make_state()
    st.player.block = 6
    st.player.powers["mc_icy_paws"] = 6
    enemy = st.enemies[0]
    effects.companion_overhaul_block_absorbed(st, enemy, 4, 6)
    assert enemy.aura == "cryo"
    # Marked-first: 6 marked, 4 absorbed, 2 left.
    assert st.player.powers["mc_icy_paws"] == 2


def test_icy_paws_stops_biting_once_the_mark_is_gone(overhaul):
    st = make_state()
    st.player.block = 6
    st.player.powers["mc_icy_paws"] = 6
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 6, 6)
    assert "mc_icy_paws" not in st.player.powers
    st.enemies[0].aura = None
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 3, 3)
    assert st.enemies[0].aura is None


def test_icy_paws_does_not_bite_a_hit_no_block_absorbed(overhaul):
    st = make_state()
    st.player.powers["mc_icy_paws"] = 6
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 0, 0)
    assert st.enemies[0].aura is None


def test_the_mark_is_clamped_to_the_block_still_standing(overhaul):
    """Block is cleared at the top of the player's turn, before this runs. The
    clamp is what makes the mark die with it -- and it stays correct under
    Barricade, which suppresses the clear."""
    st = make_state()
    st.player.powers["mc_icy_paws"] = 6
    st.player.block = 0
    effects.companion_overhaul_turn_start(st)
    assert "mc_icy_paws" not in st.player.powers

    st.player.powers["mc_icy_paws"] = 6
    st.player.block = 2                      # Barricade kept two
    effects.companion_overhaul_turn_start(st)
    assert st.player.powers["mc_icy_paws"] == 2


# ---------------------------------------------------------------------------
# NOELLE -- DAMAGE EQUAL TO YOUR BLOCK
# ---------------------------------------------------------------------------

def test_sweeping_time_deals_your_block_to_every_enemy(overhaul):
    st = make_state(enemies=[make_enemy(hp=50, name="a"),
                             make_enemy(hp=50, name="b")])
    st.player.block = 11
    _play(st, "proto_mc_noelle_sweeping_time")
    assert [e.hp for e in st.enemies] == [39, 39]


def test_sweeping_time_is_dead_behind_no_block(overhaul):
    st = make_state(enemies=[make_enemy(hp=50, name="a")])
    st.player.block = 0
    _play(st, "proto_mc_noelle_sweeping_time")
    assert st.enemies[0].hp == 50


# ---------------------------------------------------------------------------
# BARBARA -- A POWER ON THE CHOSEN BODY
# ---------------------------------------------------------------------------

def test_melody_loop_lands_on_the_chosen_enemy(overhaul):
    st = make_state(enemies=[make_enemy(hp=10, name="a"),
                             make_enemy(hp=50, name="b")])
    _play(st, "proto_mc_barbara_melody_loop")
    assert st.player.block == 4
    aimed = [e for e in st.enemies if e.powers.get("mc_melody_loop")]
    assert len(aimed) == 1
    assert aimed[0].powers["mc_melody_loop"] == 3


def test_melody_loop_applies_hydro_to_its_host_and_ticks(overhaul):
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.enemies[1].powers["mc_melody_loop"] = 2
    effects.companion_overhaul_turn_start(st)
    assert st.enemies[1].aura == "hydro"
    assert st.enemies[0].aura is None
    assert st.enemies[1].powers["mc_melody_loop"] == 1
    effects.companion_overhaul_turn_start(st)
    assert "mc_melody_loop" not in st.enemies[1].powers


# ---------------------------------------------------------------------------
# BENNETT AND RAZOR -- THE NEXT-ATTACK ELEMENT OVERRIDE
# ---------------------------------------------------------------------------

def test_passion_overload_pays_four_and_makes_the_attack_pyro(overhaul):
    st = make_state(enemies=[make_enemy(hp=50)])
    _play(st, "proto_mc_bennett_passion_overload")
    assert st.player.powers["mc_passion_overload"] == 4
    effects.resolve_card(st, _attack(element="none", applies=False, amount=6))
    assert st.enemies[0].hp == 50 - 10           # 6 printed + 4
    assert st.enemies[0].aura == "pyro"          # a row that applied nothing
    assert "mc_passion_overload" not in st.player.powers


def test_passion_overload_expires_at_turn_end_unspent(overhaul):
    st = make_state()
    st.player.powers["mc_passion_overload"] = 4
    effects.companion_overhaul_turn_end(st)
    assert "mc_passion_overload" not in st.player.powers


def test_lightning_fang_pays_three_every_attack_for_two_turns(overhaul):
    st = make_state(enemies=[make_enemy(hp=50)])
    _play(st, "proto_mc_razor_lightning_fang")
    assert st.player.powers["mc_lightning_fang"] == 2
    effects.resolve_card(st, _attack(element="none", applies=False, amount=6))
    assert st.enemies[0].hp == 50 - 9
    assert st.enemies[0].aura == "electro"
    # Still up: it is a window, not a one-shot.
    assert st.player.powers["mc_lightning_fang"] == 2
    effects.companion_overhaul_turn_end(st)
    assert st.player.powers["mc_lightning_fang"] == 1
    effects.companion_overhaul_turn_end(st)
    assert "mc_lightning_fang" not in st.player.powers


def test_the_one_shot_rider_beats_the_blanket_one(overhaul):
    """The order is law and is written down in `companion_overhaul_card_start`;
    this is the pin. Both DAMAGE halves stack; only the ELEMENT is exclusive,
    because an Attack applies one element."""
    st = make_state(enemies=[make_enemy(hp=60)])
    st.player.powers["mc_lightning_fang"] = 2
    st.player.powers["mc_passion_overload"] = 4
    effects.resolve_card(st, _attack(element="none", applies=False, amount=6))
    assert st.enemies[0].hp == 60 - 13           # 6 + 4 + 3, all three stack
    assert st.enemies[0].aura == "pyro"          # the one-shot won


# ---------------------------------------------------------------------------
# DAHLIA AND AMBER -- THE PRE-ENEMY-ATTACK TRAPS
# ---------------------------------------------------------------------------

def test_the_shower_answers_the_attacker_before_its_hit(overhaul):
    st = make_state(enemies=[make_enemy(hp=50)])
    _play(st, "proto_mc_dahlia_sacramental_shower")
    assert st.player.powers["mc_sacramental_shower"] == 1
    dmg = effects.companion_overhaul_before_enemy_hit(st, st.enemies[0], 12)
    assert dmg == 12                              # the Shower reduces nothing
    assert st.enemies[0].hp == 50 - C.MC_SHOWER_DMG
    assert st.enemies[0].aura == "hydro"
    assert "mc_sacramental_shower" not in st.player.powers


def test_one_trap_answers_one_hit(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.player.powers["mc_sacramental_shower"] = 2
    effects.companion_overhaul_before_enemy_hit(st, st.enemies[0], 5)
    assert st.player.powers["mc_sacramental_shower"] == 1
    effects.companion_overhaul_before_enemy_hit(st, st.enemies[0], 5)
    assert "mc_sacramental_shower" not in st.player.powers
    effects.companion_overhaul_before_enemy_hit(st, st.enemies[0], 5)
    assert st.enemies[0].hp == 90 - 2 * C.MC_SHOWER_DMG


def test_baron_bunny_eats_three_and_answers_the_board(overhaul):
    st = make_state(enemies=[make_enemy(hp=50, name="a"),
                             make_enemy(hp=50, name="b")])
    _play(st, "proto_mc_amber_explosive_puppet")
    dmg = effects.companion_overhaul_before_enemy_hit(st, st.enemies[0], 12)
    assert dmg == 12 - C.MC_BARON_BUNNY_REDUCTION
    assert [e.hp for e in st.enemies] == [50 - C.MC_BARON_BUNNY_DMG,
                                          50 - C.MC_BARON_BUNNY_DMG]
    assert "mc_baron_bunny" not in st.player.powers


def test_the_reduction_floors_at_zero_rather_than_healing(overhaul):
    st = make_state()
    st.player.powers["mc_baron_bunny"] = 1
    assert effects.companion_overhaul_before_enemy_hit(st, st.enemies[0], 2) == 0


def test_the_traps_fire_inside_a_real_enemy_turn(overhaul):
    """End to end through `combat._enemy_turn`, because the two call sites are
    the whole point of the hook: the Shower has to land BEFORE the hit and the
    paws have to read the Block that hit actually ate."""
    st = make_state(enemies=[make_enemy(hp=50,
                                        intents=[{"kind": "attack",
                                                  "amount": 10}])])
    st.player.block = 6
    st.player.powers["mc_icy_paws"] = 6
    st.player.powers["mc_sacramental_shower"] = 1
    hp_before = st.player.hp
    combat._enemy_turn(st, st.enemies[0])
    assert st.enemies[0].hp == 50 - C.MC_SHOWER_DMG
    # Hydro from the Shower, then Cryo from the paws on the same body: the
    # second application reacts with the first (Frozen), so the aura is gone.
    assert st.enemies[0].aura is None
    assert st.enemies[0].frozen == 1
    assert st.player.block == 0
    assert st.player.hp == hp_before - 4      # 10 in, 6 blocked


def test_a_trap_that_kills_the_attacker_stops_its_hit(overhaul):
    st = make_state(enemies=[make_enemy(hp=5,
                                        intents=[{"kind": "attack",
                                                  "amount": 30}])])
    st.player.powers["mc_sacramental_shower"] = 1
    hp_before = st.player.hp
    combat._enemy_turn(st, st.enemies[0])
    assert not st.enemies[0].alive
    assert st.player.hp == hp_before


# ---------------------------------------------------------------------------
# DAHLIA AND VARKA -- THE REACTION EVENT
# ---------------------------------------------------------------------------

def test_favonian_favor_pays_per_reaction_and_expires(overhaul):
    st = make_state(enemies=[make_enemy(hp=50)])
    _play(st, "proto_mc_dahlia_favonian_favor")
    assert st.player.block == 7
    assert st.player.powers["mc_favonian_favor"] == 3
    st.enemies[0].aura = "hydro"
    effects.deal_damage_to_enemy(st, st.enemies[0], 5, element="pyro",
                                 source="attack")
    assert st.player.block == 10               # 7 + 3 for the Vaporize
    effects.companion_overhaul_turn_end(st)
    assert "mc_favonian_favor" not in st.player.powers


def test_sturm_und_drang_banks_the_swirled_element(overhaul):
    st = make_state(enemies=[make_enemy(hp=60, name="a"),
                             make_enemy(hp=60, name="b")])
    _play(st, "proto_mc_varka_sturm_und_drang")
    assert st.player.powers["mc_sturm_und_drang"] == 6
    st.enemies[0].aura = "cryo"
    reactions.resolve_hit(st, st.enemies[0], "anemo", 0, "swirl_op")
    assert st.player.powers["mc_swirl_charge"] == 6
    assert st.player.mc_swirl_element == "cryo"
    # The next Attack takes the damage AND the element, and spends the charge.
    effects.resolve_card(st, _attack(element="none", applies=False, amount=6))
    assert "mc_swirl_charge" not in st.player.powers
    assert st.player.mc_swirl_element == ""


def test_two_swirls_bank_twice_and_the_last_element_wins(overhaul):
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.player.powers["mc_sturm_und_drang"] = 6
    effects.companion_overhaul_reaction(st, st.enemies[0], "swirl", "cryo")
    effects.companion_overhaul_reaction(st, st.enemies[0], "swirl", "hydro")
    assert st.player.powers["mc_swirl_charge"] == 12
    assert st.player.mc_swirl_element == "hydro"


def test_a_non_swirl_reaction_banks_nothing(overhaul):
    st = make_state()
    st.player.powers["mc_sturm_und_drang"] = 6
    effects.companion_overhaul_reaction(st, st.enemies[0], "vaporize", "hydro")
    assert "mc_swirl_charge" not in st.player.powers


# ---------------------------------------------------------------------------
# DURIN -- THE TWO DAMAGE-PIPELINE MODIFIERS
# ---------------------------------------------------------------------------

def test_binary_form_offers_two_modes_and_hits_the_board(overhaul):
    st = make_state(enemies=[make_enemy(hp=50, name="a"),
                             make_enemy(hp=50, name="b")])
    _play(st, "proto_mc_durin_binary_form")
    assert [e.hp for e in st.enemies] == [40, 40]
    chosen = ("mc_binary_white" in st.player.powers,
              "mc_binary_dark" in st.player.powers)
    assert chosen.count(True) == 1, "exactly one form, for the fight"


def test_white_scales_the_reaction_and_not_the_hit(overhaul):
    """The multiplier is on the REACTION'S OWN contribution. A Vaporize turns
    10 into 20; White makes that 25, not 30."""
    st = make_state(enemies=[make_enemy(hp=90)])
    st.enemies[0].aura = "hydro"
    plain = reactions.resolve_hit(st, st.enemies[0], "pyro", 10)
    assert plain == 10 * C.VAPORIZE_MULT

    st.player.powers["mc_binary_white"] = 1
    st.enemies[0].aura = "hydro"
    amped = reactions.resolve_hit(st, st.enemies[0], "pyro", 10)
    assert amped == 10 + (plain - 10) * C.MC_BINARY_WHITE_REACTION_MULT


def test_white_scales_the_overload_splash(overhaul):
    st = make_state(enemies=[make_enemy(hp=90, name="a"),
                             make_enemy(hp=90, name="b")])
    st.enemies[0].aura = "electro"
    st.player.powers["mc_binary_white"] = 1
    reactions.resolve_hit(st, st.enemies[0], "pyro", 0)
    scaled = int(C.OVERLOAD_SPLASH * C.MC_BINARY_WHITE_REACTION_MULT)
    assert st.enemies[1].hp == 90 - scaled


def test_white_stacks_add_rather_than_compound(overhaul):
    st = make_state()
    st.player.powers["mc_binary_white"] = 2
    assert effects.companion_overhaul_reaction_mult(st) == pytest.approx(2.0)


def test_dark_pays_only_on_a_pyro_attack_that_reacts(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.player.powers["mc_binary_dark"] = 8

    # No aura: no reaction, no bonus.
    effects.deal_damage_to_enemy(st, st.enemies[0], 10, element="pyro",
                                 source="attack")
    assert st.enemies[0].hp == 80

    # Hydro aura: Vaporize, and the 8 is added BEFORE the amplifier -- the
    # additive phase, where the C# twin's ModifyDamageAdditive also puts it.
    st.enemies[0].aura = "hydro"
    st.enemies[0].hp = 90
    effects.deal_damage_to_enemy(st, st.enemies[0], 10, element="pyro",
                                 source="attack")
    assert st.enemies[0].hp == 90 - int((10 + 8) * C.VAPORIZE_MULT)


def test_dark_pays_nothing_on_an_off_element_attack(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.player.powers["mc_binary_dark"] = 8
    st.enemies[0].aura = "pyro"
    effects.deal_damage_to_enemy(st, st.enemies[0], 10, element="hydro",
                                 source="attack")
    assert st.enemies[0].hp == 90 - int(10 * C.VAPORIZE_MULT)


# ---------------------------------------------------------------------------
# RAZOR -- THE ATTACKS-PLAYED COUNTER
# ---------------------------------------------------------------------------

def test_claw_and_thunder_pays_on_the_third_attack_only(overhaul):
    for played_before, expect in ((0, 0), (1, 0), (2, 1), (3, 0)):
        st = make_state(enemies=[make_enemy(hp=90)])
        st.attacks_played_this_turn = played_before
        st.player.energy = 0
        _play(st, "proto_mc_razor_claw_and_thunder")
        assert st.player.energy == expect, played_before
        assert st.enemies[0].hp == 82
        assert st.enemies[0].aura == "electro"


def test_the_predicate_counts_the_card_asking(overhaul):
    st = make_state()
    st.attacks_played_this_turn = 2
    assert effects._predicate(st, "nth_attack_this_turn_3")
    assert not effects._predicate(st, "nth_attack_this_turn_2")


# ---------------------------------------------------------------------------
# EULA -- THE COUNTING DELAYED BLADE
# ---------------------------------------------------------------------------

def test_the_lightfall_sword_counts_two_turns_then_falls(overhaul):
    st = make_state(enemies=[make_enemy(hp=90, name="a"),
                             make_enemy(hp=90, name="b")])
    _play(st, "proto_mc_eula_glacial_illumination")
    host = [e for e in st.enemies if e.powers.get("mc_lightfall_sword")][0]
    assert host.powers["mc_lightfall_sword"] == 2

    effects.resolve_card(st, _attack(amount=0))
    effects.companion_overhaul_turn_end(st)
    assert host.powers["mc_lightfall_sword"] == 1
    assert host.mc_lightfall_tally == 1

    effects.resolve_card(st, _attack(amount=0))
    effects.resolve_card(st, _attack(amount=0))
    hp_before = host.hp
    effects.companion_overhaul_turn_end(st)
    assert "mc_lightfall_sword" not in host.powers
    assert host.hp == hp_before - (C.MC_LIGHTFALL_BASE
                                   + C.MC_LIGHTFALL_PER_ATTACK * 3)
    assert host.mc_lightfall_tally == 0


def test_the_blade_counts_no_skills(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.enemies[0].powers["mc_lightfall_sword"] = 2
    effects.companion_overhaul_card_start(
        st, Card(id="s", name="s", cost=1, type="skill"))
    assert st.enemies[0].mc_lightfall_tally == 0


# ---------------------------------------------------------------------------
# MIKA -- THE NEXT-ATTACK COST DISCOUNT
# ---------------------------------------------------------------------------

def test_starfrost_discounts_the_next_attack_and_nothing_else(overhaul):
    st = make_state(enemies=[make_enemy(hp=90, name="a"),
                             make_enemy(hp=90, name="b")])
    _play(st, "proto_mc_mika_starfrost_swirl")
    assert [e.hp for e in st.enemies] == [85, 85]
    assert st.player.powers["mc_starfrost_discount"] == 1

    # A Skill is unmoved; an Attack is a point cheaper.
    assert combat.card_cost(st, Card(id="s", name="s", cost=2,
                                     type="skill")) == 2
    assert combat.card_cost(st, _attack(cost=2)) == 1
    # Reading the price does not spend it -- `card_playable` asks constantly.
    assert combat.card_cost(st, _attack(cost=2)) == 1


def test_the_discount_is_spent_by_the_attack_that_takes_it(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.player.powers["mc_starfrost_discount"] = 1
    effects.resolve_card(st, _attack(cost=2))
    assert "mc_starfrost_discount" not in st.player.powers


def test_mika_does_not_discount_her_own_card(overhaul):
    """She IS an Attack that applies the rider, which is the case the shipped
    next-attack power never had to face."""
    st = make_state(enemies=[make_enemy(hp=90)])
    st.player.powers["mc_starfrost_discount"] = 1
    _play(st, "proto_mc_mika_starfrost_swirl")
    assert st.player.powers["mc_starfrost_discount"] == 1


# ---------------------------------------------------------------------------
# THE ORDER LAWS, AGAINST THE OTHER ENGINE'S SOURCE
# ---------------------------------------------------------------------------

def test_the_incoming_hit_order_is_the_one_the_mod_walks():
    """Three powers answer an enemy's hit; two of them put an element on the
    board and can kill the attacker, so the sequence decides which reactions
    fire. One listener per engine, one order, asserted against both sources --
    the shape `test_companion_overhaul.py` uses for the end-of-turn six."""
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def companion_overhaul_before_enemy_hit(")[1]
    body = body.split("\ndef ")[0]
    seen = list(dict.fromkeys(re.findall(r'"(mc_[a-z_]+)"', body)))
    assert seen == ["mc_sacramental_shower", "mc_baron_bunny"], seen

    cs = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "CompanionOverhaulHooks.cs").read_text(encoding="utf-8")
    walk = cs.split("public override async Task BeforeDamageReceived(")[1]
    walk = walk.split("\n    }")[0]         # the method body, not the file
    cs_order = re.findall(r"OfType<(\w+Power)>", walk)
    assert cs_order == ["SacramentalShowerPower", "BaronBunnyPower",
                        "IcyPawsPower"], cs_order


def test_the_element_override_order_is_the_one_the_mod_walks():
    """Last wins, and the sequence is blanket then one-shots. A divergence here
    is a divergence in which element an Attack applies, i.e. in which reaction
    fires -- the sharpest kind there is."""
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def companion_overhaul_card_start(")[1]
    body = body.split("\ndef ")[0]
    riders = [m for m in re.findall(r'"(mc_[a-z_]+)"', body)
              if m in ("mc_lightning_fang", "mc_passion_overload",
                       "mc_swirl_charge")]
    assert list(dict.fromkeys(riders)) == [
        "mc_lightning_fang", "mc_passion_overload", "mc_swirl_charge"]

    cs = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "CompanionOverhaulHooks.cs").read_text(encoding="utf-8")
    body = cs.split("Element ElementFor(")[1]
    body = body.split("\n}")[0]
    cs_order = re.findall(
        r"OfType<(LightningFangPower|PassionOverloadPower|SwirlChargePower)>",
        body)
    assert cs_order == ["LightningFangPower", "PassionOverloadPower",
                        "SwirlChargePower"], cs_order


def test_every_new_power_has_a_c_sharp_class_the_generator_knows():
    """The generator refuses a row naming a power with no `PowerModel` in its
    registry, which is what kept these thirteen off the surface in the first
    place. This asserts the other direction: every power the thirteen apply is
    in the registry AND has a class in the file the arm owns."""
    import tools.gen_klee_cards as gen
    cs = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "CompanionOverhaulHooks.cs").read_text(encoding="utf-8")
    for power in ("mc_icy_paws", "mc_melody_loop", "mc_passion_overload",
                  "mc_sacramental_shower", "mc_favonian_favor",
                  "mc_binary_white", "mc_binary_dark", "mc_lightning_fang",
                  "mc_sturm_und_drang", "mc_baron_bunny",
                  "mc_lightfall_sword", "mc_starfrost_discount"):
        cls = gen.APPLY_POWERS[power][0]
        assert f"class {cls}" in cs, (power, cls)
