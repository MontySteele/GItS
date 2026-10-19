"""THE FONTAINE POOL REWORK (2026-10-19,
review/active/fontaine-companions-2026-10-19.md): 30 cards, 8 / 13 / 9.
Five kept, eleven rebuilt on their ids, fourteen new for nine 5-stars.

Each new or rebuilt row is resolved as printed, and each new Power is fired
at its own site. C# twin: `KleeTests/Prototype/FontaineCompanionReworkTests.cs`.
The sheet-structure locks (roster, Cryo budget, Navia, Valor, Shutter) are
`test_fontaine.py`'s.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, refpowers, resources
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards


def _card(cid):
    return loader.get_card(cid)


def _play(st, cid):
    """The real hand and energy path: the played card's own Exhaust and the
    exhaust funnel live there, not in resolve_card."""
    card = _card(cid)
    st.player.hand.append(card)
    st.player.energy = 9
    combat.play_card(st, card)
    return card


def _filler(n, rarity="common", type_="skill"):
    return [Card(id=f"filler{i}", name="f", cost=1, type=type_, rarity=rarity)
            for i in range(n)]


def _wound(i=0):
    return Card(id=f"status_wound_{i}", name="Wound", cost=-1, type="status",
                rarity="status")


def _wet(enemy, element="hydro"):
    enemy.aura = element
    enemy.aura_turns_left = C.AURA_DURATION_TURNS


# --- the pool -------------------------------------------------------------

@pytest.mark.parametrize("who", ["klee", "kokomi", "varka", "furina", "yae"])
def test_every_kit_that_drafts_companions_is_offered_the_thirty(who):
    """The pool is shared: each kit's companion slot reads the one roster,
    so all thirty rows reach every character."""
    offerable = {c.id for cs in rewards.companion_pool().values() for c in cs}
    assert set(C.FONTAINE_OVERHAUL_POOL_IDS) <= offerable
    assert len(C.FONTAINE_OVERHAUL_POOL_IDS) == 30
    for cid in C.FONTAINE_OVERHAUL_POOL_IDS:
        card = _card(cid)
        assert card.is_companion and card.nation == "fontaine"
        assert card.personal_pool is None


# --- the Commons ------------------------------------------------------------

def test_interdiction_fire_deals_pyro_and_applies_vulnerable():
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, _card("proto_mf_chevreuse_interdiction_fire"))
    e = st.enemies[0]
    assert e.hp == 193 and e.aura == "pyro"
    assert e.powers.get("vulnerable", 0) == 1


def test_enigmatic_feint_blocks_then_swirls():
    st = make_state(enemies=[make_enemy(hp=200)])
    _wet(st.enemies[0])
    effects.resolve_card(st, _card("proto_mf_lynette_enigmatic_feint"))
    assert st.player.block == 8
    assert st.enemies[0].aura is None              # Swirled


def test_freezing_point_and_pers():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.draw_pile = _filler(3)
    effects.resolve_card(st, _card("proto_mf_charlotte_freezing_point"))
    assert st.enemies[0].hp == 192 and len(st.player.hand) == 1
    pers = _card("proto_mf_freminet_pers_deploy")
    assert pers.cost == 0
    assert not any(fx.get("op") == "draw" for fx in pers.effects)
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, pers)
    assert st.enemies[0].hp == 196 and st.enemies[0].aura == "cryo"


# --- the Uncommons ----------------------------------------------------------

def test_astonishing_shift_swirls_hits_all_and_weakens_all():
    st = make_state(enemies=[make_enemy(hp=200), make_enemy(hp=200)])
    effects.resolve_card(st, _card("proto_mf_lynette_astonishing_shift"))
    assert all(e.hp <= 194 for e in st.enemies)
    assert all(e.powers.get("weak", 0) == 1 for e in st.enemies)


def test_shattering_pressure_grows_by_five_each_time_it_is_retained():
    st = make_state(enemies=[make_enemy(hp=500)])
    card = _card("proto_mf_freminet_shattering_pressure")
    st.player.hand.append(card)
    combat._player_turn(st, lambda s: None)
    assert any(c is card for c in st.player.hand)     # Retained
    combat._player_turn(st, lambda s: None)
    before = st.enemies[0].hp
    effects.resolve_card(st, card)
    assert before - st.enemies[0].hp == 8 + 5 + 5
    assert st.enemies[0].aura is None


def test_crystalshot_draws_only_when_its_own_hit_crystallizes():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.draw_pile = _filler(3)
    effects.resolve_card(st, _card("proto_mf_navia_ceremonial_crystalshot"))
    assert st.enemies[0].hp == 190
    assert st.player.hand == []                        # no aura, no draw

    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.draw_pile = _filler(3)
    _wet(st.enemies[0])
    effects.resolve_card(st, _card("proto_mf_navia_ceremonial_crystalshot"))
    assert st.enemies[0].aura is None                  # Crystallized
    assert len(st.player.hand) == 1


def test_an_earlier_crystallize_this_turn_does_not_draw():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.draw_pile = _filler(3)
    st.crystallize_this_card = 3                       # another card's
    effects.resolve_card(st, _card("proto_mf_navia_ceremonial_crystalshot"))
    assert st.player.hand == []


def test_hunters_vigil_draws_and_arms_the_electro_rider():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.draw_pile = _filler(4)
    effects.resolve_card(st, _card("proto_mf_clorinde_hunters_vigil"))
    assert len(st.player.hand) == 2
    assert st.player.powers.get("mi_next_electro", 0) == 1


def test_o_tears_hits_all_for_hydro():
    st = make_state(enemies=[make_enemy(hp=200), make_enemy(hp=200)])
    effects.resolve_card(st, _card("proto_mf_neuvillette_o_tears"))
    assert [e.hp for e in st.enemies] == [193, 193]
    assert all(e.aura == "hydro" for e in st.enemies)


def test_balemoon_rising_costs_two_hp():
    st = make_state(hp=50, enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, _card("proto_mf_arlecchino_balemoon_rising"))
    assert st.player.hp == 48
    assert st.enemies[0].hp == 188 and st.enemies[0].aura == "pyro"


def test_gracious_rebuke_takes_strength_for_good():
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, _card("proto_mf_wriothesley_gracious_rebuke"))
    e = st.enemies[0]
    assert e.hp == 193 and e.aura == "cryo"
    assert e.powers.get("strength", 0) == -1
    card = _card("proto_mf_wriothesley_gracious_rebuke")
    assert not card.exhaust
    loss = next(fx for fx in card.effects if fx["op"] == "lose_strength")
    assert not loss.get("this_turn")


def test_grin_malkin_hat_hits_for_pyro_on_every_exhaust():
    st = make_state(hp=60, enemies=[make_enemy(hp=200)])
    _play(st, "proto_mf_lyney_grin_malkin_hat")
    assert st.player.powers["mf_grin_malkin_hat"] == 4
    st.player.draw_pile = _filler(5)
    _play(st, "proto_mf_lyney_miracle_parade")         # Exhausts itself
    assert st.enemies[0].hp == 196
    assert st.enemies[0].aura == "pyro"
    refpowers.exhaust_card(st, _wound())               # a Status, too
    assert st.enemies[0].hp < 196


def test_rebound_hydrotherapy_blocks_and_wets_each_turn():
    st = make_state(enemies=[make_enemy(hp=200)])
    _play(st, "proto_mf_sigewinne_rebound_hydrotherapy")
    assert st.player.block == 0
    effects.player_turn_start_triggers(st)
    assert st.player.block == 3
    assert st.enemies[0].aura == "hydro"
    assert st.enemies[0].hp == 200                     # no damage


def test_low_temperature_cooking_draws_one_more_next_turn():
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, _card("proto_mf_escoffier_low_temperature_cooking"))
    assert st.player.block == 8
    assert st.player.powers.get("draw_cards_next_turn", 0) == 1
    assert refpowers.hand_draw_bonus(st.player) == 1


def test_lumidouce_legacy_may_exhaust_junk_even_under_kokomis_law():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.relic_hooks.append("tamakushi_casket")   # her rotation law
    wound = _wound()
    st.player.hand = [wound]
    st.player.draw_pile = _filler(4)
    effects.resolve_card(st, _card("proto_mf_emilie_lumidouce_legacy"))
    assert any(c is wound for c in st.player.exhaust_pile)
    assert len(st.player.hand) == 2


# --- the Rares --------------------------------------------------------------

def test_chilling_penalty_answers_any_hp_lost():
    st = make_state(hp=60, enemies=[make_enemy(hp=200)])
    _play(st, "proto_mf_wriothesley_chilling_penalty")
    assert st.player.powers["mf_chilling_penalty"] == 5
    _play(st, "proto_mf_arlecchino_balemoon_rising")   # its own price
    # 5 Cryo off the HP, then 12 Pyro melts it.
    assert st.enemies[0].hp == 200 - 5 - int(12 * C.MELT_MULT)
    before = st.enemies[0].hp
    resources.note_player_hp_loss(st, 0)               # nothing lost
    assert st.enemies[0].hp == before
    st.player.hp -= 3
    resources.note_player_hp_loss(st, 3)               # an enemy's hit
    assert st.enemies[0].hp == before - 5


def test_chilling_penalty_answers_each_of_furinas_drains():
    """GPT's review (2026-10-19): every Drain is an HP loss in the game
    (`StageBoard.LoseHp` is `CreatureCmd.Damage`), so each Drain hits once."""
    from tier0.engine import furina_stage as FS
    st = make_state(enemies=[make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.powers["mf_chilling_penalty"] = 5
    assert FS.drain(st, 4)
    assert FS.drain(st, 4)
    assert st.enemies[0].hp == 300 - 5 - 5


def test_miracle_parade_pays_four_hp_for_two_energy_and_two_cards():
    st = make_state(hp=50, enemies=[make_enemy(hp=200)])
    st.player.draw_pile = _filler(5)
    card = _play(st, "proto_mf_lyney_miracle_parade")
    assert st.player.hp == 46
    assert st.player.energy == 9 + 2
    assert len(st.player.hand) == 2
    assert any(c is card for c in st.player.exhaust_pile)


def test_syringing_blocks_four_for_each_enemy_hit_kills_and_blocks_included():
    st = make_state(enemies=[make_enemy(hp=200), make_enemy(hp=5),
                             make_enemy(hp=200)])
    st.enemies[2].block = 30
    effects.resolve_card(
        st, _card("proto_mf_sigewinne_super_saturated_syringing"))
    assert st.enemies[0].hp == 190
    assert not st.enemies[1].alive
    assert st.enemies[2].hp == 200                     # all into Block
    assert st.player.block == 4 * 3


def test_rehab_diet_blocks_and_mends_up_to_the_entry_hp():
    st = make_state(hp=60, enemies=[make_enemy(hp=200)])
    effects.companion_overhaul_entry_hp(st)            # walked in at 60
    st.player.hp = 50
    card = _card("proto_mf_escoffier_rehab_diet")
    assert card.exhaust and card.rarity == "rare"
    effects.resolve_card(st, card)
    assert st.player.block == 10
    assert st.player.hp == 56
    effects.resolve_card(st, card)
    assert st.player.hp == 60                          # the ceiling


def test_aromatic_explication_takes_the_hands_junk_first_for_an_energy():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.powers["mf_aromatic_explication"] = 1
    hand_wound, pile_wound = _wound(1), _wound(2)
    st.player.hand = [hand_wound] + _filler(2)
    st.player.draw_pile = [pile_wound]
    st.player.energy = 3
    effects.fontaine_turn_start_late(st)
    assert any(c is hand_wound for c in st.player.exhaust_pile)
    assert any(c is pile_wound for c in st.player.draw_pile)
    assert st.player.energy == 4
    effects.fontaine_turn_start_late(st)               # the Draw Pile's next
    assert any(c is pile_wound for c in st.player.exhaust_pile)
    assert st.player.energy == 5
    effects.fontaine_turn_start_late(st)               # nothing left
    assert st.player.energy == 5


def test_aromatic_explication_fires_after_the_draw():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.powers["mf_aromatic_explication"] = 1
    wound = _wound()
    st.player.draw_pile = [wound] + _filler(4)
    combat._player_turn(st, lambda s: None)
    assert any(c is wound for c in st.player.exhaust_pile)
