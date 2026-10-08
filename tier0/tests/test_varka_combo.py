"""VARKA, THE COMBO PASS -- the sim's pins.

Paper: `review/active/varka-combo-pass-2026-10-04.md` (RULED 2026-10-04, all
four picks, Baron Bunny amended). Rows: the `proto_vk_` block of
`docs/prototype-surface.yaml`; rules: `tier0/engine/varka_oath.py`; C# twins:
`klee-mod/KleeTests/Prototype/VarkaComboTests.cs`.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy


@pytest.fixture
def varka():
    loader.reset_arm_caches()
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _vk(name):
    return "proto_vk_" + name


def _enemy(hp=100, name="e", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left = aura, 2
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


def _play(st, card):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _led(st):
    return V.ledger(st.player)


def _pool():
    return {c.id: c for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX) and c.rarity != "basic"}


CUT = ("gale_mantle", "west_wind_shield", "knightly_guard", "tailwind_guard",
       "oath_of_the_knights")
ADDED = {"stoke_the_flames": "common", "ember_cleave": "common",
         "shatter": "common", "pyre_oath": "uncommon",
         "deep_freeze": "uncommon"}


# ---------------------------------------------------------------------------
# 1. The pool: 78 at 20 / 35 / 23, five out and five in.
# ---------------------------------------------------------------------------

def test_the_pool_stays_78_five_out_five_in(varka):
    pool = _pool()
    assert len(pool) == 78
    by = {r: sum(1 for c in pool.values() if c.rarity == r)
          for r in ("common", "uncommon", "rare")}
    assert by == {"common": 20, "uncommon": 35, "rare": 23}
    assert not {_vk(x) for x in CUT} & set(pool)
    assert {x: pool[_vk(x)].rarity for x in ADDED} == ADDED
    for x in CUT:
        with pytest.raises(KeyError):
            loader.get_card(_vk(x))
    assert not hasattr(V, "OATH_OF_THE_KNIGHTS")


def test_the_new_rows_and_their_upgrades(varka):
    stoke = loader.get_card(_vk("stoke_the_flames"))
    assert (stoke.cost, stoke.type) == (1, "skill")
    cleave = loader.get_card(_vk("ember_cleave"))
    assert (cleave.cost, cleave.type) == (1, "attack")
    pyre = loader.get_card(_vk("pyre_oath"))
    assert (pyre.cost, pyre.type, pyre.innate) == (1, "power", False)
    assert loader.get_card(_vk("pyre_oath") + "+").innate is True
    shatter = loader.get_card(_vk("shatter"))
    assert (shatter.cost, shatter.type) == (1, "attack")
    freeze = loader.get_card(_vk("deep_freeze"))
    assert (freeze.cost, freeze.type, freeze.retain) == (1, "skill", True)
    assert loader.get_card(_vk("deep_freeze") + "+").cost == 0


# ---------------------------------------------------------------------------
# 2. Pyro burns.
# ---------------------------------------------------------------------------

def test_stoke_the_flames_exhausts_a_chosen_card_and_gains_2_pyro(varka):
    st = _state(element="hydro")
    st.player.hand = [loader.get_card("defend")]
    _play(st, _vk("stoke_the_flames"))
    assert [c.id for c in st.player.exhaust_pile] == ["defend"]
    assert _led(st).oath["pyro"] == 2
    # The 2026-10-05 seat round: "Pyro becomes your current element."
    assert _led(st).current == "pyro"
    st.player.hand = [loader.get_card("defend")]
    _play(st, _vk("stoke_the_flames") + "+")
    assert _led(st).oath["pyro"] == 2 + 3


def test_stoke_the_flames_switches_after_its_gain(varka):
    # Gain first, then the switch: the gain is not yet the current
    # element's, so Dawn Wind's March does not pay for it.
    st = _state(element="hydro")
    led = _led(st)
    led.current = "electro"
    st.player.powers[V.DAWN_WINDS_MARCH] = 4
    _play(st, _vk("stoke_the_flames"))
    assert led.current == "pyro" and led.oath["pyro"] == 2
    assert st.player.block == 0


def test_the_banner_holds_stoke_the_flames(varka):
    st = _state(element="hydro")
    p, led = st.player, _led(st)
    led.current = "electro"
    p.powers[V.UNWAVERING_BANNER] = 1
    _play(st, _vk("stoke_the_flames"))
    assert led.current == "electro"
    assert led.oath["pyro"] == 2 and led.oath["electro"] == 1


def test_ember_cleave_hits_9_pyro_then_exhausts(varka):
    st = _state()
    st.player.hand = [loader.get_card("defend")]
    _play(st, _vk("ember_cleave"))
    e = st.enemies[0]
    assert e.hp == 91 and e.aura == "pyro"
    assert [c.id for c in st.player.exhaust_pile] == ["defend"]
    assert _led(st).oath["pyro"] == 1               # its own application
    st = _state()
    _play(st, _vk("ember_cleave") + "+")
    assert st.enemies[0].hp == 88


def test_pyre_oath_gains_1_pyro_per_exhausted_card(varka):
    st = _state(element="hydro")
    _play(st, _vk("pyre_oath"))
    assert st.player.powers[V.PYRE_OATH] == 1
    st.player.hand = [loader.get_card("defend")]
    _play(st, _vk("stoke_the_flames"))
    assert _led(st).oath["pyro"] == 2 + 1
    # A card that exhausts itself is an Exhaust too.
    _play(st, _vk("dawn_patrol"))
    assert _led(st).oath["pyro"] == 4


# ---------------------------------------------------------------------------
# 3. Cryo shatters.
# ---------------------------------------------------------------------------

def test_shatter_reads_stacks_of_weak_and_vulnerable(varka):
    st = _state()
    _play(st, _vk("shatter"))
    assert st.enemies[0].hp == 95 and st.enemies[0].aura == "cryo"
    st = _state()
    e = st.enemies[0]
    e.powers["weak"] = 1
    e.powers["vulnerable"] = 2
    assert V.weak_and_vulnerable(e) == 3
    _play(st, _vk("shatter"))
    # 5 + 2 x 3 = 11, and Vulnerable folds it (x1.5, rounded down).
    assert e.hp == 100 - int(11 * 1.5)
    st = _state()
    st.enemies[0].powers["weak"] = 1
    _play(st, _vk("shatter") + "+")
    assert st.enemies[0].hp == 100 - (7 + 3)


def test_deep_freeze_applies_cryo_and_doubles_weak_and_vulnerable(varka):
    st = _state()
    e = st.enemies[0]
    e.powers["weak"] = 2
    e.powers["vulnerable"] = 1
    _play(st, _vk("deep_freeze"))
    assert e.aura == "cryo"
    assert (e.powers["weak"], e.powers["vulnerable"]) == (4, 2)
    assert _led(st).current == "cryo"               # the open Oath
    st = _state()
    _play(st, _vk("deep_freeze"))                   # nothing to double
    assert "weak" not in st.enemies[0].powers


# ---------------------------------------------------------------------------
# 4. Unwavering Banner, reworded.
# ---------------------------------------------------------------------------

def test_the_banner_holds_and_pays_1_oath_of_the_current_element(varka):
    st = _state()
    p, led = st.player, _led(st)
    led.current = "pyro"
    p.powers[V.UNWAVERING_BANNER] = 1
    _play(st, _vk("deep_freeze"))                   # Cryo would switch
    assert led.current == "pyro"
    assert led.oath == {"pyro": 1, "hydro": 0, "electro": 0, "cryo": 1}
    # Once per play: Tempest would switch three times.
    _play(st, _vk("tempest_of_the_four_winds"))
    assert led.current == "pyro"
    assert led.oath["pyro"] == 1 + 1 + 1            # its own Pyro + the Banner
    # An on-element card is not a change: nothing.
    before = led.oath["pyro"]
    _play(st, _vk("ember_cleave"))
    assert led.oath["pyro"] == before + 1           # its application only
    # A Knight still changes it.
    _play(st, _vk("kaeya_frostgnaw"))
    assert led.current == "cryo"


def test_the_banner_with_no_current_element_pays_nothing(varka):
    st = _state()
    st.player.powers[V.UNWAVERING_BANNER] = 1
    _play(st, _vk("deep_freeze"))
    assert _led(st).current is None
    assert _led(st).oath["cryo"] == 1               # the application only


def test_the_banner_holds_change_of_guard_and_weathervane(varka):
    st = _state()
    p, led = st.player, _led(st)
    p.powers[V.UNWAVERING_BANNER] = 1
    led.current = "pyro"
    led.oath.update(pyro=2, hydro=5)
    _play(st, _vk("change_of_guard"))
    assert led.current == "pyro" and led.oath["pyro"] == 3
    p.powers[V.WEATHERVANE] = 1
    led.weathervane_choice = "hydro"
    V.turn_start(st)
    assert led.current == "pyro" and led.oath["pyro"] == 3


# ---------------------------------------------------------------------------
# 5. Section 1 and 2's fixes.
# ---------------------------------------------------------------------------

def test_baron_bunny_hits_one_random_enemy(varka):
    st = _state(n=3)
    _play(st, _vk("amber_baron_bunny"))
    assert st.player.block == 6
    V.turn_start(st)
    assert sorted(e.hp for e in st.enemies) == [94, 100, 100]
    up = loader.get_card(_vk("amber_baron_bunny") + "+")
    assert [f["amount"] for f in up.effects] == [8, 8]


def test_charge_of_the_knights_costs_1_and_pays_5_then_7(varka):
    card = loader.get_card(_vk("charge_of_the_knights"))
    f = card.effects[0]["amount_formula"]
    assert (card.cost, f["per"]) == (1, 5)
    up = loader.get_card(_vk("charge_of_the_knights") + "+")
    assert (up.cost, up.effects[0]["amount_formula"]["per"]) == (1, 7)


def test_kaeya_and_razor_are_attacks(varka):
    for name in ("kaeya_frostgnaw", "razor_claw_and_thunder"):
        card = loader.get_card(_vk(name))
        assert card.type == "attack", name
        assert V.is_knight(card), name


def test_lions_fang_upgrade_is_a_cost_cut(varka):
    card = loader.get_card("proto_mc_jean_lions_fang")
    up = loader.get_card("proto_mc_jean_lions_fang+")
    assert (card.cost, up.cost) == (2, 1)
    assert up.effects[0]["amount"] == card.effects[0]["amount"] == 8


def test_four_winds_ascension_upgrade_is_a_cost_cut(varka):
    card = loader.get_card(_vk("four_winds_ascension"))
    up = loader.get_card(_vk("four_winds_ascension") + "+")
    assert (card.cost, up.cost) == (2, 1)
    assert up.effects == card.effects


def test_the_counts_the_cuts_left_stay_grammar(varka):
    st = _state()
    _led(st).oath.update(pyro=3, hydro=4, electro=2)
    assert effects._runtime_count(st, "half_total_oath") == 4
    assert effects._runtime_count(st, "oath_elements") == 3
