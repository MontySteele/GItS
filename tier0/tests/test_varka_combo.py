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
from tier0.engine.state import Card, CombatState, Enemy


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


def _burn():
    return Card(id="burn", name="Burn", cost=0, type="status",
                rarity="status", effects=[])


def _pool():
    # His co-op five (2026-10-13) sit outside the pool count.
    coop_only = loader.multiplayer_ids()
    return {c.id: c for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX) and c.rarity != "basic"
            and c.id not in coop_only}


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
    # The rarity sweep (2026-10-19): three Powers down, two Skills up.
    assert by == {"common": 20, "uncommon": 36, "rare": 22}
    assert not {_vk(x) for x in CUT} & set(pool)
    assert {x: pool[_vk(x)].rarity for x in ADDED} == ADDED
    for x in CUT:
        with pytest.raises(KeyError):
            loader.get_card(_vk(x))
    assert not hasattr(V, "OATH_OF_THE_KNIGHTS")


def test_the_new_rows_and_their_upgrades(varka):
    stoke = loader.get_card(_vk("stoke_the_flames"))
    # Varka payoff fix (2026-10-08): Stoke costs 0, was 1.
    assert (stoke.cost, stoke.type) == (0, "skill")
    cleave = loader.get_card(_vk("ember_cleave"))
    assert (cleave.cost, cleave.type) == (1, "attack")
    pyre = loader.get_card(_vk("pyre_oath"))
    assert (pyre.cost, pyre.type, pyre.innate) == (1, "power", False)
    # The Pyro pass (2026-10-11): the upgrade is 3 Strength, not Innate.
    assert loader.get_card(_vk("pyre_oath") + "+").innate is False
    shatter = loader.get_card(_vk("shatter"))
    assert (shatter.cost, shatter.type) == (1, "attack")
    freeze = loader.get_card(_vk("deep_freeze"))
    # Retain dropped 2026-10-13 ([USER]: "I think we should drop Retain").
    assert (freeze.cost, freeze.type, freeze.retain) == (1, "skill", False)
    assert loader.get_card(_vk("deep_freeze") + "+").cost == 0


# ---------------------------------------------------------------------------
# 2. Pyro burns.
# ---------------------------------------------------------------------------

def test_stoke_the_flames_gains_2_pyro_and_powers_the_next_pyro_attack(varka):
    # Pyro paper 2 (2026-10-12): "Gain 2 [3] Pyro Oath. Your next Pyro Attack
    # this turn deals 5 [7] additional damage." The Exhaust rider is gone.
    st = _state(element="hydro")
    st.player.hand = [_burn()]
    _play(st, _vk("stoke_the_flames"))
    assert st.player.exhaust_pile == []
    assert _led(st).oath["pyro"] == 2
    assert st.player.powers[V.NEXT_PYRO_ATTACK] == 5
    assert "next_attack_up" not in st.player.powers
    # The 2026-10-05 seat round: "Pyro becomes your current element."
    assert _led(st).current == "pyro"
    _play(st, _vk("stoke_the_flames") + "+")
    assert _led(st).oath["pyro"] == 2 + 3
    assert st.player.powers[V.NEXT_PYRO_ATTACK] == 5 + 7
    assert not hasattr(V, "EXHAUST_RIDER_OATH")
    assert "exhaust_for_pyro_oath" not in V.KINDS


def test_stokes_bonus_rides_the_next_pyro_attack_and_is_spent(varka):
    st = _state(element="hydro")
    _play(st, _vk("stoke_the_flames"))
    _play(st, _vk("ember_cleave"))
    assert st.enemies[0].hp == 100 - (9 + 5)
    assert V.NEXT_PYRO_ATTACK not in st.player.powers
    # Spent: the next Pyro Attack takes nothing from it (Ember Cleave's own
    # Strength 2 still counts).
    _play(st, _vk("ember_cleave"))
    assert st.enemies[0].hp == 100 - (9 + 5) - (9 + 2)


def test_a_non_pyro_attack_leaves_stokes_bonus_standing(varka):
    st = _state(element="hydro")
    _play(st, _vk("stoke_the_flames"))
    _play(st, _vk("shatter"))                       # Icebreaker: Cryo, 5
    assert st.enemies[0].hp == 95
    assert st.player.powers[V.NEXT_PYRO_ATTACK] == 5
    st.enemies[0].aura = None                       # no Melt in the sum
    _play(st, _vk("ember_cleave"))
    assert st.enemies[0].hp == 95 - (9 + 5)
    assert V.NEXT_PYRO_ATTACK not in st.player.powers


def test_stokes_bonus_ends_with_the_turn(varka):
    st = _state(element="hydro")
    _play(st, _vk("stoke_the_flames"))
    V.turn_end(st)
    assert V.NEXT_PYRO_ATTACK not in st.player.powers


def test_stoke_the_flames_switches_before_its_gain(varka):
    # The Varka payoff round (2026-10-10): the switch first, then the gain,
    # so the gain is the current element's and Dawn Wind's March pays.
    st = _state(element="hydro")
    led = _led(st)
    led.current = "electro"
    st.player.powers[V.DAWN_WINDS_MARCH] = 4
    _play(st, _vk("stoke_the_flames"))
    assert led.current == "pyro" and led.oath["pyro"] == 2
    assert st.player.block == 4


def test_the_banner_holds_stoke_the_flames(varka):
    st = _state(element="hydro")
    p, led = st.player, _led(st)
    led.current = "electro"
    p.powers[V.UNWAVERING_BANNER] = 1
    _play(st, _vk("stoke_the_flames"))
    assert led.current == "electro"
    assert led.oath["pyro"] == 2 and led.oath["electro"] == 1


def test_ember_cleave_is_setup_strike_in_pyro(varka):
    # Pyro paper 2 (2026-10-12): "Deal 7 [9] Pyro damage. Gain 2 [3]
    # Strength this turn." No Oath gain, no Exhaust rider. The Varka review
    # (2026-10-12, pick 1 (a)): 9 [11].
    st = _state(element="hydro")
    st.player.hand = [_burn()]
    _play(st, _vk("ember_cleave"))
    e = st.enemies[0]
    assert e.hp == 91 and e.aura == "pyro"
    assert st.player.exhaust_pile == []
    assert _led(st).oath["pyro"] == 1               # its application's credit
    assert st.player.powers["temp_strength"] == 2
    assert st.player.powers["strength"] == 2
    st = _state(element="hydro")
    _play(st, _vk("ember_cleave") + "+")
    assert st.enemies[0].hp == 89
    assert st.player.powers["strength"] == 3


def test_ashen_oath_gains_2_strength_and_2_pyro_oath(varka):
    # The Pyro pass (2026-10-11): "Gain 2 [3] Strength. Gain 2 Pyro Oath."
    # Its gain switches nothing; the Exhaust-trigger power left with it.
    assert loader.get_card(_vk("pyre_oath")).name == "For Crepus"
    assert not hasattr(V, "PYRE_OATH")
    st = _state(element="hydro")
    led = _led(st)
    led.current = "electro"
    st.player.hand = [loader.get_card("defend")]
    _play(st, _vk("pyre_oath"))
    assert st.player.powers["strength"] == 2
    assert led.oath["pyro"] == 2 and led.current == "electro"
    assert [c.id for c in st.player.hand] == ["defend"]
    _play(st, _vk("pyre_oath") + "+")
    assert st.player.powers["strength"] == 2 + 3


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
    # Varka last pass (2026-10-12): its 1 Weak and 1 Vulnerable land
    # before the doubling, so 2 + 1 doubles to 6 and 1 + 1 to 4.
    assert (e.powers["weak"], e.powers["vulnerable"]) == (6, 4)
    assert _led(st).current == "cryo"               # the open Oath
    st = _state()
    _play(st, _vk("deep_freeze"))                   # a clean enemy ends on 2
    assert st.enemies[0].powers["weak"] == 2
    assert st.enemies[0].powers["vulnerable"] == 2


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
    # Its application only (Pyro paper 2, 2026-10-12: no Oath gain); no
    # Banner payment.
    assert led.oath["pyro"] == before + 1
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
    assert up.effects[0]["amount"] == card.effects[0]["amount"] == 6   # pool sweep


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
