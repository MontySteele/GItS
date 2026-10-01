"""VARKA, THE EXPANSION -- the sim engine's pins for the 37 cards and the
Knight pass (`review/active/varka-expansion-2026-10-01.md` sec.3, all four
picks ruled at the defaults 2026-10-01). Rules: `tier0/engine/varka_oath.py`;
rows: the `proto_vk_` block of `docs/prototype-surface.yaml`. The C# twin is
`klee-mod/KleeTests/Prototype/VarkaExpansionTests.cs`.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy


def _reset():
    loader.reset_arm_caches()


@pytest.fixture
def varka():
    saved = (C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA)
    C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = True, True
    _reset()
    try:
        yield
    finally:
        C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = saved
        _reset()


def _enemy(hp=100, name="e", aura=None, spent=False):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left, e.aura_spent = aura, 2, spent
    return e


def _state(n=1, element="pyro", **kw):
    enemies = kw.pop("enemies", None) or [_enemy(name=f"e{i}")
                                          for i in range(n)]
    p = V.build_player(element, fang=False)
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _led(st):
    return V.ledger(st.player)


def _vk(name):
    return "proto_vk_" + name


def _play(st, card, target=None):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    if target is not None:
        st.pilot_target = target
    combat.play_card(st, card)
    return card


def _rows():
    return [c for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX)]


# ---------------------------------------------------------------------------
# 1. The pool.
# ---------------------------------------------------------------------------

EXPANSION_IDS = (
    "pathfinders_mark", "cavalry_charge", "west_wind_shield",
    "knightly_strike", "amber_sharpshooter",
    "blazing_charge", "tidal_bulwark", "glacial_edict", "static_field",
    "barbara_wellspring_hymn", "lisa_pulsating_witch",
    "noelle_steadfast_maid", "vow_of_the_blade", "unwavering_banner",
    # Varka defence (2026-10-01): Gust Ward took Four Banners' place.
    "shifting_gale", "cycle_of_seasons", "gust_ward", "eye_wall",
    # Element identities (2026-10-01): Short Circuit and Retaliating Tide
    # took Pressure Front's and Unbroken Tide's places.
    "short_circuit", "crosscurrent", "assembly_at_the_cathedral",
    "dawn_patrol",
    "wildfire_oath", "retaliating_tide", "absolute_zero", "thundering_verdict",
    "oath_unto_death", "grand_masters_verdict", "wolfpack",
    "oathbound_aegis", "weathervane", "tempest_of_the_four_winds",
    "twin_gales", "downburst", "eye_of_stormterror",
    "charge_of_the_knights", "the_order_answers",
)


def test_the_pool_is_78_twenty_thirty_five_twenty_three(varka):
    pool = [c for c in _rows() if c.rarity != "basic"]
    assert len(pool) == 78
    by = {r: sum(1 for c in pool if c.rarity == r)
          for r in ("common", "uncommon", "rare")}
    assert by == {"common": 20, "uncommon": 35, "rare": 23}
    ids = {c.id for c in pool}
    assert len(EXPANSION_IDS) == 37
    assert {_vk(x) for x in EXPANSION_IDS} <= ids
    # Thirteen pool Knights, Noelle among them; the starter four are not.
    knights = V.pool_knight_ids()
    assert len(knights) == 13
    assert _vk("noelle_steadfast_maid") in knights
    assert not set(V.STARTER_KNIGHT_IDS.values()) & set(knights)


def test_the_paper_numbers_and_upgrades(varka):
    def fx(cid, op, i=0):
        return [f for f in loader.get_card(cid).effects if f["op"] == op][i]
    assert fx(_vk("barbara_show_begin"), "block")["amount"] == 5
    assert fx(_vk("barbara_show_begin") + "+", "block")["amount"] == 7
    assert fx(_vk("mika_starfrost_swirl"), "apply_power")["amount"] == 2
    assert fx(_vk("mika_starfrost_swirl") + "+", "apply_power")["amount"] == 3
    assert fx(_vk("razor_claw_and_thunder") + "+", "varka")["base"] == 6
    assert fx(_vk("glacial_edict") + "+", "varka")["amount"] == 3
    assert fx(_vk("pathfinders_mark") + "+", "varka")["upgraded"] is True
    assert loader.get_card(_vk("retaliating_tide") + "+").cost == 1
    assert loader.get_card(_vk("the_order_answers") + "+").cost == 1
    assert loader.get_card(_vk("wildfire_oath") + "+").innate is True
    assert loader.get_card(_vk("lisa_pulsating_witch") + "+").retain is True
    up = loader.get_card(_vk("amber_sharpshooter") + "+")
    assert fx(up.id, "damage")["amount"] == 11
    assert fx(up.id, "conditional")["then"][0]["amount"] == 11
    assert loader.get_card(_vk("grand_masters_verdict")).exhaust is True


# ---------------------------------------------------------------------------
# 2. Noelle: a Geo Knight.
# ---------------------------------------------------------------------------

def test_noelle_is_a_knight_that_keeps_the_element_and_gains_no_oath(varka):
    st = _state()
    led = _led(st)
    led.current, led.oath["cryo"] = "cryo", 2
    st.player.powers[V.WINDBORNE_RESOLVE] = 5
    _play(st, _vk("noelle_steadfast_maid"))
    assert led.current == "cryo"
    assert led.oath == {"pyro": 0, "hydro": 0, "electro": 0, "cryo": 2}
    assert led.knights_this_turn == 1 and led.knights_this_combat == 1
    assert st.player.block == 9                        # no change, no Resolve
    assert len(st.player.hand) == 1                    # drew 1
    assert V.predicate(st, "knight_played_this_turn")


# ---------------------------------------------------------------------------
# 3. The Knight pass.
# ---------------------------------------------------------------------------

def test_diluc_gains_energy_when_a_hit_reacts(varka):
    st = _state(enemies=[_enemy(aura="hydro")])
    _play(st, _vk("diluc_searing_onslaught"))
    assert st.player.energy == 10 - 2 + 1
    st = _state()
    _play(st, _vk("diluc_searing_onslaught"))
    assert st.player.energy == 10 - 2


def test_kaeya_applies_vulnerable_and_mika_weak(varka):
    st = _state()
    _play(st, _vk("kaeya_frostgnaw"))
    assert st.enemies[0].powers.get("vulnerable") == 1
    st = _state()
    _play(st, _vk("mika_starfrost_swirl"))
    e = st.enemies[0]
    assert e.aura == "cryo" and e.powers.get("weak") == 2
    assert st.player.block == 0


def test_razor_hits_all_and_more_on_electro(varka):
    st = _state(enemies=[_enemy(name="a", aura="electro"), _enemy(name="b")])
    _play(st, _vk("razor_claw_and_thunder"))
    a, b = st.enemies
    assert a.hp == 100 - 7 and b.hp == 100 - 4
    assert b.aura == "electro"
    assert _led(st).current == "electro"


def test_sharpshooter_shoots_again_only_on_pyro(varka):
    st = _state(enemies=[_enemy(aura="pyro")])
    _play(st, _vk("amber_sharpshooter"))
    assert st.enemies[0].hp == 100 - 16
    st = _state()
    _play(st, _vk("amber_sharpshooter"))
    assert st.enemies[0].hp == 100 - 8          # her own Pyro does not count
    assert st.enemies[0].aura == "pyro"


def test_wellspring_hymn_cleanses_and_witch_draws_per_enemy(varka):
    st = _state()
    p = st.player
    p.powers.update(weak=2, frail=1, vulnerable=3, strength=1)
    _play(st, _vk("barbara_wellspring_hymn"))
    assert not any(p.powers.get(k) for k in ("weak", "frail", "vulnerable"))
    assert p.powers["strength"] == 1
    assert st.enemies[0].aura == "hydro"
    st = _state(n=3)
    _play(st, _vk("lisa_pulsating_witch"))
    assert len(st.player.hand) == 3
    assert all(e.aura == "electro" for e in st.enemies)


# ---------------------------------------------------------------------------
# 4. Commons.
# ---------------------------------------------------------------------------

def test_pathfinders_mark(varka):
    st = _state(n=2)
    led = _led(st)
    _play(st, _vk("pathfinders_mark"))
    assert led.current in V.ELEMENTS                 # a random one, now his
    assert sum(1 for e in st.enemies if e.aura) == 1
    assert led.oath[led.current] == 1
    st = _state(n=3)
    _led(st).current = "hydro"
    _play(st, _vk("pathfinders_mark") + "+")
    assert all(e.aura == "hydro" for e in st.enemies)


def test_cavalry_charge_carries_the_current_element_or_anemo(varka):
    st = _state()
    _led(st).current = "cryo"
    _play(st, _vk("cavalry_charge"))
    assert st.enemies[0].aura == "cryo" and st.enemies[0].hp == 93
    st = _state(enemies=[_enemy(aura="pyro")])
    _play(st, _vk("cavalry_charge"))
    assert _led(st).swirls_made == 1                 # plain Anemo Swirled


def test_west_wind_shield_and_knightly_strike(varka):
    st = _state(enemies=[_enemy(aura="pyro"), _enemy(aura="hydro",
                                                     spent=True), _enemy()])
    _play(st, _vk("west_wind_shield"))
    assert st.player.block == 5 + 2 * 2
    st = _state()
    _play(st, _vk("knightly_strike"))
    assert st.enemies[0].hp == 93
    _play(st, _vk("noelle_steadfast_maid"))
    _play(st, _vk("knightly_strike"))
    assert st.enemies[0].hp == 93 - 11


# ---------------------------------------------------------------------------
# 5. The element payoffs read their own element's Oath.
# ---------------------------------------------------------------------------

def test_blazing_charge_reads_pyro_oath_by_name(varka):
    st = _state()
    led = _led(st)
    led.current, led.oath["pyro"], led.oath["cryo"] = "cryo", 3, 9
    _play(st, _vk("blazing_charge"))
    assert st.enemies[0].hp == 100 - (5 + 2 * 3)
    assert led.current == "pyro" and led.oath["pyro"] == 4


def test_tidal_bulwark_reads_hydro_after_its_own(varka):
    st = _state()
    _led(st).oath["hydro"] = 2
    _play(st, _vk("tidal_bulwark"))
    assert st.player.block == 4 + 2 * 3


def test_glacial_edict_stacks_every_four_cryo(varka):
    st = _state()
    _led(st).oath["cryo"] = 7                         # + its own = 8
    _play(st, _vk("glacial_edict"))
    e = st.enemies[0]
    assert e.powers["weak"] == 3 and e.powers["vulnerable"] == 3


def test_thundering_verdict_hits_all_x_times_reading_electro(varka):
    # Element identities: X cost; 6 + 1 per Electro Oath, read once.
    st = _state(n=2)
    _led(st).oath["electro"] = 2
    card = loader.get_card(_vk("thundering_verdict"))
    st.player.hand.append(card)
    st.player.energy = 2
    combat.play_card(st, card)
    assert st.player.energy == 0
    assert [e.hp for e in st.enemies] == [100 - 2 * 8] * 2
    assert _led(st).oath["electro"] == 3             # one credit per card


# ---------------------------------------------------------------------------
# 6. The Powers and the rule-benders.
# ---------------------------------------------------------------------------

def test_static_field_draws_once_a_turn(varka):
    st = _state()
    st.player.powers[V.STATIC_FIELD] = 2
    _play(st, _vk("razor_claw_and_thunder"))
    assert len(st.player.hand) == 2
    _play(st, _vk("razor_claw_and_thunder"))
    assert len(st.player.hand) == 2
    st.turn = 2
    V.turn_start(st)
    _play(st, _vk("lisa_violet_arc"))
    assert len(st.player.hand) == 4


def test_unwavering_banner_stops_the_open_oath_not_knights(varka):
    st = _state()
    led = _led(st)
    led.current = "cryo"
    st.player.powers[V.UNWAVERING_BANNER] = 1
    _play(st, _vk("blazing_charge"))
    assert led.current == "cryo" and led.oath["pyro"] == 1
    _play(st, _vk("lisa_violet_arc"))
    assert led.current == "electro"


def test_shifting_gale_and_cycle_of_seasons(varka):
    st = _state(n=2)
    _play(st, _vk("shifting_gale"))
    assert st.enemies[0].hp == 94
    st.player.powers[V.CYCLE_OF_SEASONS] = 4
    _play(st, _vk("mika_starfrost_swirl"))             # none -> Cryo
    assert [e.hp for e in st.enemies] == [90, 96]
    st.enemies[0].aura = None                          # no Swirl, no Vulnerable
    st.enemies[0].powers.clear()
    _play(st, _vk("shifting_gale"))
    assert st.enemies[0].hp == 90 - 12


def test_charge_of_the_knights(varka):
    st = _state()
    _play(st, _vk("noelle_steadfast_maid"))
    _play(st, _vk("noelle_steadfast_maid"))
    _play(st, _vk("charge_of_the_knights"))
    assert st.enemies[0].hp == 100 - 10


def test_eye_wall_crosscurrent_and_eye_of_stormterror(varka):
    st = _state(enemies=[_enemy(aura="pyro")])
    led = _led(st)
    led.current = "hydro"
    p = st.player
    p.powers[V.EYE_OF_STORMTERROR] = 1
    _play(st, _vk("eye_wall"))
    assert p.block == 6
    _play(st, _vk("crosscurrent"))
    # Hydro pays 3 Block, twice, plus Eye Wall's 3; the Eye draws 1.
    assert p.block == 6 + 3 * 2 + 3
    assert len(p.hand) == 1
    V.turn_start(st)
    assert V.EYE_WALL not in p.powers


def test_assembly(varka):
    st = _state(n=3)
    st.player.powers[V.ASSEMBLY] = 3
    before = sum(e.hp for e in st.enemies)
    _play(st, _vk("noelle_steadfast_maid"))
    assert before - sum(e.hp for e in st.enemies) == 3


def test_absolute_zero_widens_its_payout(varka):
    # (Wildfire Oath widened Pyro's payout until element identities re-aimed
    # it: tier0/tests/test_varka_element_identities.py.)
    st = _state(enemies=[_enemy(name="a", aura="hydro"), _enemy(name="b")])
    led = _led(st)
    led.current = "cryo"
    st.player.powers[V.ABSOLUTE_ZERO] = 1
    _play(st, _vk("jean_dandelion_breeze"))
    for e in st.enemies:
        assert e.powers.get("vulnerable") == 1 and e.powers.get("weak") == 1


def test_twin_gales_pays_the_swirled_element_too(varka):
    st = _state(enemies=[_enemy(aura="pyro")])
    led = _led(st)
    led.current = "hydro"
    st.player.powers[V.TWIN_GALES] = 1
    _play(st, _vk("jean_dandelion_breeze"))
    assert st.player.block == 7 + 3                   # Hydro paid
    assert st.enemies[0].hp == 100 - 2 - 3           # and Pyro paid


def test_oath_unto_death_and_grand_masters_verdict(varka):
    st = _state()
    led = _led(st)
    led.current, led.oath["pyro"] = "pyro", 3
    st.player.powers[V.OATH_UNTO_DEATH] = 1
    _play(st, _vk("grand_masters_verdict"))
    assert led.oath["pyro"] == 3 + 3 + 1              # doubled, one more
    V.gain(st, "cryo", 1)
    assert led.oath["cryo"] == 1                      # not the current one


def test_wolfpack_copies_ascension_into_discard(varka):
    st = _state()
    st.player.powers[V.WOLFPACK] = 1
    _play(st, _vk("four_winds_ascension") + "+")
    ids = [c.id for c in st.player.discard_pile]
    assert ids.count(V.ASCENSION_ID + "+") == 2       # itself and the copy


def test_oathbound_aegis_pays_half_the_total_uncapped(varka):
    # Varka defence (2026-10-01): half the total, rounded down, no cap; a
    # second copy pays it again.
    st = _state()
    led = _led(st)
    led.oath.update(pyro=20, cryo=21)
    st.player.powers[V.OATHBOUND_AEGIS] = 1
    V.turn_end(st)
    assert st.player.block == 20
    st.player.block = 0
    st.player.powers[V.OATHBOUND_AEGIS] = 2
    V.turn_end(st)
    assert st.player.block == 40


def test_weathervane(varka):
    st = _state()
    led = _led(st)
    st.player.powers[V.WEATHERVANE] = 1
    led.current = "pyro"
    led.oath.update(pyro=1, cryo=3)
    V.turn_start(st)
    assert led.current == "cryo"                      # default: the most
    led.weathervane_choice = "pyro"
    V.turn_start(st)
    assert led.current == "pyro"
    led.weathervane_choice = "keep"
    V.turn_start(st)
    assert led.current == "pyro"


def test_tempest_four_hits_last_wins(varka):
    st = _state()
    _play(st, _vk("tempest_of_the_four_winds"))
    led = _led(st)
    assert led.current == "electro"
    assert all(led.oath[el] == 1 for el in V.ELEMENTS)


def test_downburst_spreads_fresh_copies(varka):
    st = _state(enemies=[_enemy(name="a", aura="pyro"), _enemy(name="b")])
    _play(st, _vk("downburst"))
    b = st.enemies[1]
    assert b.aura == "pyro" and not b.aura_spent
    st = _state(enemies=[_enemy(name="a", aura="pyro"), _enemy(name="b")])
    _play(st, _vk("favonius_cut"))
    assert st.enemies[1].aura_spent


def test_the_order_answers_adds_a_knight_at_its_cost(varka):
    st = _state()
    st.player.powers[V.THE_ORDER_ANSWERS] = 1
    V.turn_start(st)
    assert len(st.player.hand) == 1
    knight = st.player.hand[0]
    assert knight.id in V.pool_knight_ids() and not knight.free_this_turn


def test_vow_dawn_patrol(varka):
    st = _state()
    _led(st).current = "hydro"
    _play(st, _vk("vow_of_the_blade"))
    assert _led(st).oath["hydro"] == 1 and len(st.player.hand) == 1
    _play(st, _vk("dawn_patrol"))
    assert st.player.energy == 10 + 1                  # 0 cost, +1
    assert st.player.exhaust_pile[-1].id == _vk("dawn_patrol")
