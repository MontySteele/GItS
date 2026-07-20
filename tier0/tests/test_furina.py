"""Furina sprint 1: engine-level tests for Spotlight, Encore, Fanfare and
skill-grade cadence (furina-kickoff-v0.1.md; card sheet not yet begun --
these lock the SYSTEMS, statline work comes with the sheet pass).
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, powers
from tier0.engine.state import Card, CombatState
from tier0.harness import metrics
from tier0.harness.axes import raw_axes
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def furina_card(**kw):
    """A fabricated Furina personal card (her sheet doesn't exist yet)."""
    d = dict(id="furina_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


# --- character spec / cadence ---

def test_build_furina_skeleton():
    p = loader.build_player("furina")
    assert p.character_id == "furina" and p.element == "hydro"
    assert p.cadence == "skill"
    assert p.fanfare_cap == int(C.FANFARE_CAP_FRACTION * p.max_hp) > 0
    assert "ethereal_spotlight" in p.relic_hooks
    assert loader.character_nation("furina") == "fontaine"


def test_skill_cadence_applies_element_on_skills_not_attacks():
    st = furina_state()
    e = st.enemies[0]
    effects.resolve_card(st, furina_card(
        type="attack", effects=[{"op": "damage", "amount": 4}]))
    assert e.aura is None                    # attacks never auto-apply
    effects.resolve_card(st, furina_card(
        effects=[{"op": "damage", "amount": 4}]))
    assert e.aura == "hydro"                 # skills do (Skill-grade)


def test_skill_cadence_never_touches_companion_cards():
    st = furina_state()
    # Lynette's AoE rider is explicitly applies_element: false; the plain
    # 8-dmg Backstroke hit must not pick up hydro from her cadence either.
    effects.resolve_card(st, loader.get_card("freminet_pressurized_floe"))
    assert st.enemies[0].aura is None


# --- Encore ---

def test_encore_absorbs_after_block_before_hp():
    st = furina_state()
    p = st.player
    p.block, p.encore = 3, 10
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    assert p.hp == p.max_hp                  # 3 blocked, 5 absorbed
    assert p.encore == 5
    hits = [ev for ev in st.log if ev["event"] == "player_hit"]
    assert hits[0]["blocked"] == 3 and hits[0]["amount"] == 0
    absorbed = [ev for ev in st.log if ev["event"] == "encore_absorb"]
    assert absorbed[0]["amount"] == 5


def test_encore_accounting_credits_a4_never_a3():
    """Kickoff §2 harness note, Tier 0 BINDING: without this rule she
    grows a phantom third elite axis."""
    st = furina_state()
    p = st.player
    p.block, p.encore = 3, 10
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    stats = metrics.extract(st, hp_start=p.max_hp)
    assert stats.encore_absorbed == 5
    assert stats.damage_blocked == 3         # encore NOT folded into block
    raw = raw_axes({"x": [stats]})
    assert raw["A4_sustain"] == 5.0          # healing 0 + encore 5


def test_gain_and_overdraw():
    st = furina_state()
    p = st.player
    effects.resolve_card(st, furina_card(
        effects=[{"op": "gain_encore", "amount": 4}]))
    assert p.encore == 4
    assert p.fanfare == 4 * C.FANFARE_PER_ENCORE_GAINED
    # Overdraw: greed is legal and priced (true HP, which is Fanfare flux).
    effects.resolve_card(st, furina_card(
        effects=[{"op": "spend_encore", "amount": 10}]))
    assert p.encore == 0
    assert p.hp == p.max_hp - 6
    assert p.fanfare == (4 * C.FANFARE_PER_ENCORE_GAINED
                         + 4 * C.FANFARE_PER_ENCORE_SPENT
                         + 6 * C.FANFARE_PER_HP_LOST)


def test_encore_cost_is_a_gate_not_an_overdraw():
    st = furina_state()
    p = st.player
    card = furina_card(encore_cost=3)
    p.hand.append(card)
    p.energy = 3
    assert not combat.card_playable(st, card)
    p.encore = 3
    assert combat.card_playable(st, card)
    combat.play_card(st, card)
    assert p.encore == 0 and p.hp == p.max_hp


def test_encore_resets_per_combat():
    p = loader.build_player("furina")
    p.encore, p.fanfare = 50, 20
    st = combat.run_fight(p, [make_enemy(hp=1)],
                          NULL_PILOT, seed=1)
    assert not any(ev["event"] == "encore_absorb" for ev in st.log)


# --- Fanfare ---

def test_fanfare_caps_and_is_activity_only():
    st = furina_state()
    p = st.player
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 45}]
    combat._enemy_turn(st, e)                # 45 true HP lost
    assert p.fanfare == p.fanfare_cap        # capped at %maxHP (30)
    # No passive accrual: empty turns generate nothing.
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    before = p.fanfare
    combat._player_turn(st, NULL_PILOT)
    combat._player_turn(st, NULL_PILOT)
    assert p.fanfare == before


def test_fanfare_inert_without_the_resource():
    st = furina_state()
    st.player.fanfare_cap = 0                # e.g. Klee
    st.enemies[0].intents = [{"kind": "attack", "amount": 10}]
    combat._enemy_turn(st, st.enemies[0])
    assert st.player.fanfare == 0
    assert not any(ev["event"] == "gain_fanfare" for ev in st.log)


# --- Spotlight ---

def _stock_deck(p, *card_ids):
    p.draw_pile.extend(loader.get_card(cid) for cid in card_ids)


def test_selector_designates_deepest_companion_character():
    st = furina_state()
    st.player.draw_pile.clear()      # isolate: her real starter is now 10
    _stock_deck(st.player, "chevreuse_interdiction_fire",
                "chevreuse_vanguards_valor", "lynette_box_trick")
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == "chevreuse"


def test_spotlight_empowers_damage_and_block_only():
    # R16 world: the empowerment is CARD-MEDIATED. The base mult is the
    # relic's residual passive (E1-swept); her cards grant the rest via
    # spotlight_mult_bonus. This test pins the card-granted path.
    st = furina_state()
    st.player.spotlight = "charlotte"
    st.player.powers["spotlight_mult_bonus"] = 50    # e.g. two top_billing
    e = st.enemies[0]
    mult = C.SPOTLIGHT_BASE_MULT + 0.5
    # Damage: Freezing Point prints 3 -> int(3 * mult).
    _stock_deck(st.player, "charlotte_freezing_point")   # draw target
    effects.resolve_card(st, loader.get_card("charlotte_freezing_point"))
    dmg = [ev for ev in st.log if ev["event"] == "damage"][0]
    assert dmg["base"] == int(3 * mult)
    # Block: Frosthelm prints 3 now + 3 next turn -> scaled both.
    effects.resolve_card(st, loader.get_card("charlotte_enduring_frosthelm"))
    assert st.player.block == int(3 * mult)
    assert st.player.powers["block_next_turn"] == int(3 * mult)
    # §2.2a extension: numbers only, never turn-economy or power stacks --
    # Snappy Silhouette's Vulnerable 2 and cantrip stay printed.
    effects.resolve_card(st, loader.get_card("charlotte_snappy_silhouette"))
    assert e.powers["vulnerable"] == 2


def test_unspotlighted_and_untagged_cards_unchanged():
    st = furina_state()
    st.player.spotlight = "charlotte"
    effects.resolve_card(st, loader.get_card("chevreuse_interdiction_fire"))
    dmg = [ev for ev in st.log if ev["event"] == "damage"][0]
    assert dmg["base"] == 5                  # not the designated character
    st2 = furina_state()
    st2.player.spotlight = "furina"
    effects.resolve_card(st2, loader.get_card("strike"))   # untagged
    dmg2 = [ev for ev in st2.log if ev["event"] == "damage"][0]
    assert dmg2["base"] == 6                 # strike prints 6, unscaled


def test_self_spotlight_reduced_rate():
    st = furina_state()
    st.player.spotlight = "furina"
    effects.resolve_card(st, furina_card(
        effects=[{"op": "damage", "amount": 4, "applies_element": False}]))
    dmg = [ev for ev in st.log if ev["event"] == "damage"][0]
    assert dmg["base"] == int(4 * C.SPOTLIGHT_SELF_MULT)   # 5, not 6


def test_ovation_fanfare_on_spotlighted_play():
    st = furina_state()
    p = st.player
    p.spotlight = "lynette"
    card = loader.get_card("lynette_box_trick")
    p.hand.append(card)
    p.energy = 3
    combat.play_card(st, card)
    assert st.spotlighted_cards_this_turn == 1
    assert p.fanfare == C.FANFARE_PER_SPOTLIGHT_CARD


def test_designation_moves_freely_and_duplicates_inert():
    st = furina_state()
    st.player.draw_pile.clear()      # isolate from the real starter's depth
    _stock_deck(st.player, "chevreuse_interdiction_fire",
                "chevreuse_vanguards_valor", "lynette_box_trick")
    sel = loader.get_card("ethereal_spotlight")
    effects.resolve_card(st, sel)
    assert st.player.spotlight == "chevreuse"
    events = sum(1 for ev in st.log if ev["event"] == "spotlight_designated")
    effects.resolve_card(st, sel)            # same aim: inert re-aim
    assert st.player.spotlight == "chevreuse"
    assert sum(1 for ev in st.log
               if ev["event"] == "spotlight_designated") == events
    # Deck composition shifts -> the selector re-aims at the new deepest.
    _stock_deck(st.player, "lynette_enigmatic_feint",
                "lynette_astonishing_shift")
    effects.resolve_card(st, sel)
    assert st.player.spotlight == "lynette"


def test_selector_delivered_each_turn_and_vanishes():
    st = furina_state()
    combat._player_turn(st, NULL_PILOT)
    assert not any(c.id == "ethereal_spotlight" for c in st.player.hand)
    assert any(c.id == "ethereal_spotlight" for c in st.player.exhaust_pile)
    assert not any(c.id == "ethereal_spotlight"
                   for c in st.player.discard_pile)   # never loot
    assert any(ev["event"] == "selector_granted" for ev in st.log)


def test_per_turn_cap_schematized_but_off():
    assert C.SPOTLIGHT_CARDS_PER_TURN_CAP is None    # kickoff §3.2: OFF;
    # arming it is a ruling, and this lock makes turning it on deliberate.


# --- DoT chip routes through Encore too ---

def test_dot_absorbed_by_encore():
    st = furina_state()
    p = st.player
    p.encore = 3
    powers.apply_power(st, p, "dot", 5)
    powers.on_turn_start(st, p)
    assert p.hp == p.max_hp - 2 and p.encore == 0
    assert sum(ev["amount"] for ev in st.log
               if ev["event"] == "encore_absorb") == 3
