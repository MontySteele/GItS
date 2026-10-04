"""VARKA, THE OATH REWORK -- the sim engine's pins (`tier0/engine/varka_oath.py`).

Rules: `review/active/varka-paper-kit-2026-09-28.md` (every pick ruled
2026-09-29); rows: the `proto_vk_` block of `docs/prototype-surface.yaml`. His
rules have no switch (collapsed 2026-10-01: he ships nowhere else); the `varka`
fixture turns on the element port's ruled switch (`C.SWIRL_PAYS`) and
restores it.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy, Player


def _reset():
    loader.reset_arm_caches()


@pytest.fixture
def varka():
    saved = C.SWIRL_PAYS
    C.SWIRL_PAYS = True
    _reset()
    try:
        yield
    finally:
        C.SWIRL_PAYS = saved
        _reset()


def _enemy(hp=100, name="e", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left = aura, 2
    return e


def _state(n=1, element="pyro", fang=True, fang_upgraded=False, **kw):
    enemies = kw.pop("enemies", None) or [_enemy(name=f"e{i}")
                                          for i in range(n)]
    p = V.build_player(element, fang=fang, fang_upgraded=fang_upgraded)
    p.draw_pile = []
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _led(st):
    return V.ledger(st.player)


def _play(st, card):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _vk(name):
    return "proto_vk_" + name


def _hand_ids(st):
    return [c.id for c in st.player.hand]


# ---------------------------------------------------------------------------
# 0. No switch: always on, and dead for anyone who is not Varka.
# ---------------------------------------------------------------------------

def _ironclad_log(seed):
    from tier0.pilot.policy import make_pilot
    player = loader.build_player("ref_ironclad", "starter")
    enemies = loader.build_encounter("punisher")
    pilot = make_pilot(loader.pilot_weights("generic"))
    return combat.run_fight(player, enemies, pilot, seed=seed).log


def test_his_rules_have_no_switch():
    """Collapsed 2026-10-01 (legacy cleanup stage 2): he ships nowhere
    else, so the module carries no switch to turn off."""
    assert not hasattr(V, "VARKA_OATH")


def test_a_non_varka_fight_never_reaches_his_rules():
    """Every hook is dead for a player who is not Varka: no ledger, no
    Oath event, and the same seed writes the same log."""
    _reset()
    log = _ironclad_log(7)
    assert not any(str(e.get("event", "")).startswith("varka") for e in log)
    assert log == _ironclad_log(7)


def test_his_rows_always_resolve_and_his_verbs_refuse_anyone_else():
    _reset()
    assert loader.get_card(_vk("gale_mantle")).id == _vk("gale_mantle")
    st = CombatState(player=Player(hp=80, max_hp=80, character_id="klee"),
                     enemies=[_enemy()], rng=random.Random(0))
    assert V.ledger(st.player) is None
    card = _drill()
    with pytest.raises(NotImplementedError):
        effects.OPS["varka"](st, card.effects[1], card)
    assert V.predicate(st, "has_current_element") is False
    assert effects._runtime_count(st, "current_oath") == 0


# ---------------------------------------------------------------------------
# 1. The rows: ruled numbers and upgrades.
# ---------------------------------------------------------------------------

def _fx(cid, op, **match):
    card = loader.get_card(cid)
    return next(fx for fx in card.effects if fx["op"] == op
                and all(fx.get(k) == v for k, v in match.items()))


def test_the_ruled_rows_and_their_upgrades(varka):
    lisa = _fx(_vk("lisa_violet_arc"), "block")["amount_formula"]
    assert (lisa["base"], lisa["per"]) == (6, 3)    # Electro Knights pass
    lisa_up = _fx(_vk("lisa_violet_arc") + "+", "block")["amount_formula"]
    assert (lisa_up["base"], lisa_up["per"]) == (7, 4)
    for suffix, want in (("", 6), ("+", 8)):
        cid = _vk("amber_baron_bunny") + suffix
        assert _fx(cid, "block")["amount"] == want
        assert _fx(cid, "apply_power")["amount"] == want
    assert _fx(_vk("windborne_resolve"), "apply_power")["amount"] == 5
    assert _fx(_vk("windborne_resolve") + "+", "apply_power")["amount"] == 7
    assert _fx(_vk("dawn_winds_march"), "apply_power")["amount"] == 3
    nw = loader.get_card(_vk("northwind_avatar"))
    assert nw.cost == 2
    assert _fx(nw.id, "damage")["amount"] == 10
    hit = _fx(nw.id, "varka")
    assert (hit["kind"], hit["base"], hit["per"]) == ("avatar_hit", 10, 2)
    up = loader.get_card(_vk("northwind_avatar") + "+")
    assert _fx(up.id, "damage")["amount"] == 14
    assert _fx(up.id, "varka")["base"] == 14
    asc = loader.get_card(_vk("four_winds_ascension") + "+")
    assert _fx(asc.id, "damage")["amount"] == 13
    assert _fx(asc.id, "varka")["per"] == 4
    assert loader.get_card(_vk("grand_masters_order") + "+").retain is True
    assert _fx(_vk("knights_roll_call") + "+", "add_knight")["choose"] is True
    assert V.SWIRL_ELECTRO_DAMAGE_ALL == 3


def test_every_row_resolves_and_every_upgrade_applies(varka):
    rows = [c for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX)]
    assert len(rows) == 84          # 47, and 84 since the expansion
    for c in rows:
        loader.get_card(c.id)
        if c.no_upgrade:
            assert not upgrades.has_upgrade(c.id), c.id
        else:
            assert upgrades.has_upgrade(c.id), c.id
            loader.get_card(c.id + "+")


def test_a_bad_varka_op_is_refused_at_load():
    with pytest.raises(ValueError):
        V.validate_op("x", {"op": "varka", "kind": "absorb"})
    with pytest.raises(ValueError):
        V.validate_op("x", {"op": "varka", "kind": "avatar_hit", "base": 1})
    V.validate_op("x", {"op": "varka", "kind": "avatar_hit",
                        "base": 1, "per": 2})


def test_the_starter_and_the_helper(varka):
    p = V.build_player("hydro")
    ids = sorted(c.id for c in p.draw_pile)
    assert ids == sorted(["strike"] * 4 + ["defend"] * 4
                         + [_vk("windbound_execution"),
                            _vk("barbara_melody_loop")])
    assert (p.hp, p.max_hp, p.character_id) == (80, 80, "varka")
    assert V.FANG in p.relic_hooks
    rolled = {V.build_player(rng=random.Random(s)).draw_pile[-1].id
              for s in range(40)}
    assert rolled == set(V.STARTER_KNIGHT_IDS.values())


# ---------------------------------------------------------------------------
# 2. Oath credit, per card play.
# ---------------------------------------------------------------------------

def test_a_knight_sets_the_current_element_before_its_effects(varka):
    st = _state(fang=False)
    _play(st, _vk("amber_fiery_rain"))
    led = _led(st)
    assert led.current == "pyro"
    assert led.oath == {"pyro": 1, "hydro": 0, "electro": 0, "cryo": 0}
    assert st.player.block == 5                         # the rebalance's Amber
    assert st.enemies[0].aura == "pyro"


def test_a_multi_target_applier_credits_one(varka):
    st = _state(n=3, fang=False)
    _play(st, _vk("barbara_show_begin"))
    assert all(e.aura == "hydro" for e in st.enemies)
    assert _led(st).oath["hydro"] == 1


def test_apply_and_swirl_are_separate_keys_in_one_scope(varka):
    st = _state(fang=False)
    V.open_scope(st)
    V.credit(st, "apply", "pyro")
    V.credit(st, "apply", "pyro")
    V.credit(st, "swirl", "pyro")
    V.credit(st, "swirl", "pyro")
    V.close_scope(st)
    assert _led(st).oath["pyro"] == 2


def test_a_spread_credits_nothing(varka):
    """Windbound Execution Swirls A's Pyro, consuming it; the spread's copies
    on B and C credit nothing (2026-10-03: no spent auras)."""
    st = _state(enemies=[_enemy(name="a", aura="pyro"), _enemy(name="b"),
                         _enemy(name="c")], fang=False)
    _play(st, _vk("windbound_execution"))
    assert _led(st).oath == {"pyro": 1, "hydro": 0, "electro": 0, "cryo": 0}
    a, b, c = st.enemies
    assert a.aura is None and b.aura == "pyro" and c.aura == "pyro"
    assert _led(st).swirls_made == 1


def test_northwind_credits_both_keys_and_ascension_only_the_swirl(varka):
    # Northwind: 10 Anemo Swirls the Pyro (+1 swirl-Pyro, flat 2, Pyro
    # payout 3), then 10 + 2 x 2 Pyro, which credits apply-Pyro.
    st = _state(enemies=[_enemy(aura="pyro")], fang=False)
    led = _led(st)
    led.current, led.oath["pyro"] = "pyro", 1
    _play(st, _vk("northwind_avatar"))
    assert led.oath["pyro"] == 3
    assert st.enemies[0].hp == 100 - (10 + 2 + 3 + 14)
    # Ascension: 10 Anemo Swirls (+1), then 3 x 2 Pyro that credits nothing.
    st = _state(enemies=[_enemy(aura="pyro")], fang=False)
    led = _led(st)
    led.current, led.oath["pyro"] = "pyro", 1
    _play(st, _vk("four_winds_ascension"))
    assert led.oath["pyro"] == 2
    assert st.enemies[0].hp == 100 - (10 + 2 + 3 + 6)


def test_ascension_with_no_current_element_deals_its_anemo_only(varka):
    st = _state(fang=False)
    _play(st, _vk("four_winds_ascension"))
    assert st.enemies[0].hp == 90
    assert _led(st).oath == dict.fromkeys(V.ELEMENTS, 0)


# ---------------------------------------------------------------------------
# 2b. The open Oath ([USER], 2026-09-30): any card of his that applies Pyro,
#     Hydro, Cryo or Electro sets his current element and gains 1 Oath of it.
# ---------------------------------------------------------------------------

def _skill(*effects):
    """A non-Knight Skill of his carrying `effects` (the rebalance retired
    the rows these pins used to borrow: Favonius Drill and Wind Wall)."""
    import copy
    card = copy.deepcopy(loader.get_card(_vk("knightly_guard")))
    card.effects = [dict(fx) for fx in effects]
    return card


def _drill():
    """Favonius Drill's old row: Block 6, apply the current element."""
    return _skill({"op": "block", "amount": 6},
                  {"op": "varka", "kind": "apply_current_element",
                   "target": "enemy"})


def _wind_wall():
    """Wind Wall's old row: Block 7, 3 more with a current element."""
    return _skill({"op": "block", "amount": 7},
                  {"op": "conditional", "if": "has_current_element",
                   "then": [{"op": "block", "amount": 3}]})


def _applier(*elements, target="enemy"):
    """A non-Knight card of his that applies `elements` in order."""
    import copy
    card = copy.deepcopy(loader.get_card(_vk("favonius_cut")))
    card.cost = 0
    card.effects = [{"op": "apply_aura", "element": el, "target": target}
                    for el in elements]
    return card


def test_a_non_knight_elemental_card_sets_the_element_and_credits(varka):
    st = _state(n=3, fang=False)
    p = st.player
    p.powers[V.DAWN_WINDS_MARCH] = 3
    p.powers[V.BOREAS_UNBOUND] = 1
    p.energy = 5
    _play(st, _applier("hydro", target="all_enemies"))
    led = _led(st)
    assert led.current == "hydro"
    assert led.oath == {"pyro": 0, "hydro": 1, "electro": 0, "cryo": 0}
    assert p.block == 3                                  # the March paid
    assert p.energy == 10 + 1                            # Unbound paid


def test_the_last_element_a_card_applies_wins(varka):
    st = _state(fang=False)
    _play(st, _applier("pyro", "cryo"))
    led = _led(st)
    assert led.current == "cryo"
    assert led.oath["pyro"] == 1 and led.oath["cryo"] == 1


@pytest.mark.parametrize("element", ["anemo", "geo"])
def test_an_anemo_or_geo_card_neither_credits_nor_switches(
        varka, element):
    st = _state(fang=False)                             # no aura to react
    _led(st).current, _led(st).oath["pyro"] = "pyro", 1
    before = dict(_led(st).oath)
    _play(st, _applier(element))
    assert _led(st).current == "pyro"
    assert _led(st).oath == before


def test_a_swirl_spread_does_not_switch(varka):
    """Windbound Execution Swirls A's Pyro while Hydro is current: the
    Swirl credits Pyro, its spread lands on B and C, and Hydro stays."""
    st = _state(enemies=[_enemy(name="a", aura="pyro"), _enemy(name="b"),
                         _enemy(name="c")], fang=False)
    _led(st).current = "hydro"
    _play(st, _vk("windbound_execution"))
    assert _led(st).current == "hydro"
    assert _led(st).oath["pyro"] == 1


def test_baron_bunnys_burst_does_not_switch(varka):
    st = _state(n=2, fang=False)
    _led(st).current = "cryo"
    st.player.powers[V.BARON_BUNNY] = 3
    V.turn_start(st)
    assert _led(st).current == "cryo"
    assert _led(st).oath["pyro"] == 1                    # it still credits


def test_favonius_drill_counts_under_the_open_oath(varka):
    st = _state(fang=False)
    _led(st).current = "electro"
    _play(st, _drill())
    _play(st, _drill())
    assert _led(st).oath["electro"] == 2


def test_the_open_oath_switch_off_is_the_old_rule(varka, monkeypatch):
    monkeypatch.setattr(V, "OPEN_OATH", False)
    st = _state(fang=False)
    _play(st, _applier("hydro"))
    assert _led(st).current is None
    assert _led(st).oath["hydro"] == 1


# ---------------------------------------------------------------------------
# 3. The Swirl payout of each current element.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("current", ["pyro", "hydro", "cryo", "electro",
                                     None])
def test_each_swirl_payout(varka, current):
    st = _state(enemies=[_enemy(name="a", aura="cryo"), _enemy(name="b")],
                fang=False)
    _led(st).current = current
    _play(st, _vk("jean_dandelion_breeze"))
    a, b = st.enemies
    assert _led(st).oath["cryo"] == 1                   # the Swirl's credit
    extra_a = {"pyro": 3, "electro": 3}.get(current, 0)
    extra_b = {"electro": 3}.get(current, 0)
    assert a.hp == 100 - 2 - extra_a
    assert b.hp == 100 - 2 - extra_b
    assert st.player.block == 7 + (3 if current == "hydro" else 0)
    assert a.powers.get("vulnerable", 0) == (1 if current == "cryo" else 0)


def test_the_pyro_payout_is_unpowered_and_meets_vulnerable(varka):
    st = _state(enemies=[_enemy(aura="cryo")], fang=False)
    _led(st).current = "pyro"
    st.player.powers["strength"] = 5
    st.enemies[0].powers["vulnerable"] = 2
    V.on_swirl(st, st.enemies[0], "cryo")
    assert st.enemies[0].hp == 100 - int(3 * 1.5)


# ---------------------------------------------------------------------------
# 4. Powers.
# ---------------------------------------------------------------------------

def test_windborne_resolve_pays_on_every_change(varka):
    # Varka defence (2026-10-01): Cycle of Seasons' Block twin.
    st = _state(fang=False)
    st.player.powers[V.WINDBORNE_RESOLVE] = 5
    _play(st, _vk("amber_fiery_rain"))                  # None -> Pyro
    assert st.player.block == 5 + 5
    _play(st, _vk("amber_fiery_rain"))                  # already current
    assert st.player.block == 5 + 5 + 5
    _play(st, _applier("hydro"))                        # the open Oath
    assert st.player.block == 5 + 5 + 5 + 5


def test_boreas_unbound_pays_on_every_change(varka):
    st = _state(fang=False)
    st.player.powers[V.BOREAS_UNBOUND] = 1
    energy = []
    for cid in ("amber_fiery_rain", "amber_fiery_rain", "kaeya_glacial_waltz"):
        st.player.energy = 10
        _play(st, _vk(cid))
        energy.append(st.player.energy)
    assert energy == [10 - 1 + 1, 10 - 1, 10 - 1 + 1]
    st.player.energy = 10
    _led(st).oath["hydro"] = 5
    _play(st, _vk("change_of_guard"))                   # counts as a change
    assert _led(st).current == "hydro"
    assert st.player.energy == 10 - 0 + 1


def test_dawn_winds_march_pays_on_a_gain_of_the_current_element(varka):
    st = _state(fang=False)
    st.player.powers[V.DAWN_WINDS_MARCH] = 3
    _play(st, _vk("amber_fiery_rain"))                  # current set first
    assert st.player.block == 5 + 3
    V.gain(st, "hydro", 1)                              # not current
    assert st.player.block == 8
    V.gain(st, "pyro", 2)                               # one gain event
    assert st.player.block == 11


def test_the_turn_start_order_bunny_sworn_oath_of_the_knights(varka):
    st = _state(n=3, fang=False)
    p, led = st.player, _led(st)
    led.current = "hydro"
    p.powers[V.BARON_BUNNY] = 6 + 8                     # two Bunnies stack
    p.powers[V.SWORN_BROTHERHOOD] = 1
    p.powers[V.OATH_OF_THE_KNIGHTS] = 1
    led.oath["hydro"] = 2
    V.turn_start(st)
    assert all(e.hp == 100 - 14 and e.aura == "pyro" for e in st.enemies)
    assert V.BARON_BUNNY not in p.powers
    assert led.current == "hydro"                       # Bunny sets nothing
    # one burst, one scope: +1 Pyro; then Sworn +1 each.
    assert led.oath == {"pyro": 2, "hydro": 3, "electro": 1, "cryo": 1}
    assert p.block == 3                                 # hydro Oath after Sworn


def test_baron_bunny_through_the_turn(varka):
    st = _state(n=2, fang=False)
    _play(st, _vk("amber_baron_bunny"))
    assert st.player.block == 6
    assert st.player.powers[V.BARON_BUNNY] == 6
    assert all(e.hp == 100 for e in st.enemies)
    V.turn_start(st)
    assert all(e.hp == 94 for e in st.enemies)


def test_stormward_stance(varka):
    st = _state(fang=False)
    st.player.powers[V.STORMWARD] = 3
    led = _led(st)
    led.current, led.oath["pyro"] = "pyro", 3
    _play(st, _vk("favonius_cut"))
    assert st.enemies[0].hp == 100 - 14                 # 3 Oath: below bar
    led.oath["pyro"] = 4
    _play(st, _vk("favonius_cut"))
    assert st.enemies[0].hp == 100 - 14 - 17
    hp = st.enemies[0].hp
    _play(st, _vk("oathsworn_strike"))                  # element-less
    assert st.enemies[0].hp == hp - (6 + 4)
    hp = st.enemies[0].hp
    _play(st, "strike")                                 # the base Strike
    assert st.enemies[0].hp == hp - 6


def test_converging_winds(varka):
    """The Swirl's spread becomes the flat 2 carrying the element, landing
    on each other enemy; a spread reaction credits nothing."""
    st = _state(enemies=[_enemy(name="a", aura="pyro"),
                         _enemy(name="b", aura="hydro"),
                         _enemy(name="c")], fang=False)
    st.player.powers[V.CONVERGING_WINDS] = 1
    _play(st, _vk("jean_dandelion_breeze"))
    a, b, c = st.enemies
    assert a.hp == 98
    assert b.hp < 98 and b.aura is None                 # Vaporize on b
    assert c.hp == 98 and c.aura == "pyro"
    assert _led(st).oath == {"pyro": 1, "hydro": 0, "electro": 0, "cryo": 0}


def test_grand_masters_order_plays_the_next_knight_twice(varka):
    st = _state(fang=False)
    _play(st, _vk("grand_masters_order"))
    _play(st, _vk("barbara_melody_loop"))
    # two Knight plays, 6 each (the rebalance's Barbara)
    assert st.player.block == 6 + 6
    assert _led(st).knights_this_turn == 2
    assert V.GRAND_MASTERS_ORDER not in st.player.powers
    _play(st, _vk("barbara_melody_loop"))               # spent: once
    assert _led(st).knights_this_turn == 3


def test_gale_sweep_hits_each_aura_once(varka):
    # 2026-10-03: no spent auras, so the sweep takes every aura'd body (a, b
    # and d), each shielded from the earlier Swirls' spread until its hit.
    st = _state(enemies=[_enemy(name="a", aura="pyro"),
                         _enemy(name="b", aura="cryo"),
                         _enemy(name="c"),
                         _enemy(name="d", aura="hydro")],
                fang=False)
    _play(st, _vk("gale_sweep"))
    a, b, c, d = st.enemies
    # a, b and d Swirled (3 + three Swirls' flat 2s); c took only the 2s.
    assert (a.hp, b.hp, c.hp, d.hp) == (91, 91, 94, 91)
    assert _led(st).oath == {"pyro": 1, "hydro": 1, "electro": 0, "cryo": 1}


# ---------------------------------------------------------------------------
# 5. Boreas's Fang.
# ---------------------------------------------------------------------------

def test_the_fang_adds_ascension_on_the_first_gain_once(varka):
    st = _state()
    _play(st, _vk("amber_fiery_rain"))
    assert _hand_ids(st) == [V.ASCENSION_ID]
    assert st.player.hand[0].free_this_turn is False     # the Fang's is not
    _play(st, _vk("kaeya_glacial_waltz"))
    assert _hand_ids(st).count(V.ASCENSION_ID) == 1
    V.open_combat(st.player)                            # the next fight
    assert _led(st).fang_fired is False


def test_the_upgraded_fang_adds_it_upgraded_and_a_full_hand_discards(varka):
    st = _state(fang_upgraded=True)
    V.gain(st, "cryo", 1)
    assert _hand_ids(st) == [V.ASCENSION_ID + "+"]
    # Wolf's Gravestone: "It costs 0 this turn", and only the first gain.
    assert st.player.hand[0].free_this_turn is True
    V.gain(st, "hydro", 1)
    assert _hand_ids(st) == [V.ASCENSION_ID + "+"]
    st = _state()
    st.player.hand = [loader.get_card("strike")
                      for _ in range(C.MAX_HAND_SIZE)]
    V.gain(st, "cryo", 1)
    assert [c.id for c in st.player.discard_pile] == [V.ASCENSION_ID]


def test_no_fang_no_ascension(varka):
    st = _state(fang=False)
    V.gain(st, "pyro", 1)
    assert st.player.hand == []


# ---------------------------------------------------------------------------
# 6. Every `varka` op kind.
# ---------------------------------------------------------------------------

def test_apply_current_element(varka):
    st = _state(fang=False)
    _play(st, _drill())
    assert st.enemies[0].aura is None and st.player.block == 6
    _led(st).current = "electro"
    _play(st, _drill())
    assert st.enemies[0].aura == "electro"
    assert _led(st).oath["electro"] == 1


def test_gain_current_oath_and_knight_played_this_turn(varka):
    st = _state(fang=False)
    _play(st, _vk("knightly_guard"))
    assert _led(st).oath == dict.fromkeys(V.ELEMENTS, 0)
    _play(st, _vk("amber_fiery_rain"))
    _play(st, _vk("knightly_guard"))
    assert _led(st).oath["pyro"] == 2
    V.turn_start(st)
    assert V.predicate(st, "knight_played_this_turn") is False


def test_swirled_take_more(varka):
    st = _state(enemies=[_enemy(name="a", aura="pyro"), _enemy(name="b")],
                fang=False)
    _play(st, _vk("storm_surge"))
    a, b = st.enemies
    # 5 Anemo to both. a Swirls (2 to both, a Pyro copy on b) and takes 5
    # more; then b's fresh copy Swirls too (2 to both, a copy back on a) and
    # b takes 5 more (2026-10-03: a Swirl ALL pays per standing aura).
    assert (a.hp, b.hp) == (100 - 5 - 2 - 5 - 2, 100 - 5 - 2 - 5 - 2)
    assert (a.aura, b.aura) == ("pyro", None)


def test_swirl_fresh_auras_shields_its_snapshot(varka):
    st = _state(enemies=[_enemy(name="a", aura="pyro"),
                         _enemy(name="b", aura="cryo")], fang=False)
    _play(st, _vk("wall_of_gales"))
    assert st.player.block == 16
    assert _led(st).swirls_made == 2
    assert _led(st).oath == {"pyro": 1, "hydro": 0, "electro": 0, "cryo": 1}


def test_oath_per_cryo_enemy(varka):
    st = _state(enemies=[_enemy(name="a"), _enemy(name="b", aura="cryo"),
                         _enemy(name="c", aura="hydro")], fang=False)
    _play(st, _vk("eula_icetide_vortex"))
    # a: Cryo applied (+1 apply), then 2 enemies wear Cryo: +2 in one event.
    assert _led(st).oath["cryo"] == 3


def test_change_of_guard(varka):
    # The open-Oath round (2026-10-01): cost 0, no Exhaust, no Block; it
    # draws 1 (2 upgraded), with no Oath too.
    st = _state(fang=False)
    card = loader.get_card(_vk("change_of_guard"))
    assert card.cost == 0 and not card.exhaust
    st.player.draw_pile = [loader.get_card(_vk("knightly_guard"))
                           for _ in range(6)]
    st.player.hand = []
    _play(st, card)                                     # no Oath: draws only
    assert _led(st).current is None and st.player.block == 0
    assert _hand_ids(st) == [_vk("knightly_guard")]
    assert card in st.player.discard_pile               # no Exhaust
    led = _led(st)
    led.oath.update(pyro=2, hydro=3, electro=3)
    _play(st, _vk("change_of_guard"))                   # most; tie P/H/E/C
    assert led.current == "hydro" and st.player.block == 0
    led.guard_choice = "pyro"
    _play(st, _vk("change_of_guard"))
    assert led.current == "pyro" and st.player.block == 0


def test_rally(varka):
    st = _state(fang=False)
    led = _led(st)
    led.oath.update(pyro=1, hydro=2, electro=3, cryo=4)
    _play(st, _vk("rally_to_the_banner"))              # no current: nothing
    assert led.oath == {"pyro": 1, "hydro": 2, "electro": 3, "cryo": 4}
    led.current = "hydro"
    _play(st, _vk("rally_to_the_banner"))
    assert led.oath == {"pyro": 0, "hydro": 10, "electro": 0, "cryo": 0}


def test_add_knight(varka):
    st = _state(fang=False)
    _play(st, _vk("knights_roll_call"))
    knight = st.player.hand[-1]
    assert knight.id in V.pool_knight_ids() and knight.free_this_turn
    assert len(V.pool_knight_ids()) == 13     # 9 + the expansion's 4
    _led(st).current = "cryo"
    _play(st, _vk("knights_roll_call") + "+")
    assert st.player.hand[-1].id == _vk("kaeya_frostgnaw")


# ---------------------------------------------------------------------------
# 7. The three counts and three predicates.
# ---------------------------------------------------------------------------

def test_the_counts(varka):
    st = _state(fang=False)
    led = _led(st)
    assert effects._runtime_count(st, "current_oath") == 0
    led.oath.update(pyro=2, cryo=1)
    assert effects._runtime_count(st, "current_oath") == 0
    led.current = "pyro"
    assert effects._runtime_count(st, "current_oath") == 2
    assert effects._runtime_count(st, "oath_elements") == 2
    _play(st, _vk("tailwind_guard"))
    assert st.player.block == 6
    _play(st, _vk("favonius_cut"))
    _play(st, _vk("favonius_cut"))
    block = st.player.block
    _play(st, _vk("lisa_violet_arc"))                   # 6 + 3 x 2 Attacks
    assert st.player.block == block + 12


def test_the_predicates(varka):
    st = _state(fang=False)
    _play(st, _wind_wall())
    assert st.player.block == 7
    _led(st).current = "pyro"
    _play(st, _wind_wall())
    assert st.player.block == 7 + 10
    block = st.player.block
    _play(st, _vk("crosswind"))                         # no aura: no Swirl
    assert st.player.block == block
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "hydro", 2
    _play(st, _vk("crosswind"))
    assert st.player.block == block + 5
    assert V.predicate(st, "swirled_by_this") is False  # outside a play


# ---------------------------------------------------------------------------
# 8. A whole fight, piloted.
# ---------------------------------------------------------------------------

def test_a_varka_fight_runs_to_the_end(varka):
    from tier0.pilot.policy import make_pilot
    player = V.build_player("electro", extra=(
        _vk("gale_sweep"), _vk("storm_surge"), _vk("frost_ward"),
        _vk("sworn_brotherhood"), _vk("amber_baron_bunny")))
    enemies = loader.build_encounter("punisher")
    pilot = make_pilot(loader.pilot_weights("generic"))
    st = combat.run_fight(player, enemies, pilot, seed=3)
    assert st.log[-1]["event"] == "fight_end"
    assert any(e["event"] == "varka_oath" for e in st.log)
