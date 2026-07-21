"""Burning Blood at the RUN layer (run-model rework §2/§8).

combat.py stays emit-only (tier0 frozen; anchor lock untouched). The heal
that carries HP across fights is applied in model.py after each won fight
for characters whose relic_hooks contain "heal_after_won_fight".

HARD RULE 7 lock: the assertion FAILS against the pre-rework model (the
relic was silently inert -- hp_by_node recorded raw post-combat HP with no
heal). The control (klee, no relic) pins that the heal fires ONLY on the
relic character.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import CombatState
from tier05 import model

HIT = 15


def _fake_fight(player, enemies, pilot, seed):
    """Win every fight, taking a fixed HP hit -- isolates the run-layer
    heal from combat noise."""
    player.hp = max(1, player.hp - HIT)
    for e in enemies:
        e.hp = 0
    return CombatState(player=player, enemies=enemies,
                       rng=random.Random(seed))


def _skip(rng, deck, offers, archetype):
    return None


def test_burning_blood_heals_after_won_fight(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _fake_fight)
    r = model.run_one("ref_ironclad", "demolition", "demolition", _skip, 1)
    max_hp = loader._character_index()["ref_ironclad"]["hp"]
    # Node 0 (first normal): took HIT, then Burning Blood heals +6.
    assert r.hp_by_node[0] == max_hp - HIT + C.BURNING_BLOOD_HEAL


def test_no_relic_no_run_layer_heal(monkeypatch):
    monkeypatch.setattr(model, "run_fight", _fake_fight)
    r = model.run_one("klee", "demolition", "demolition", _skip, 1)
    max_hp = loader._character_index()["klee"]["hp"]
    assert r.hp_by_node[0] == max_hp - HIT      # klee has no relic hook


def test_burning_blood_capped_at_max_hp(monkeypatch):
    # A 1-HP hit leaves room for only part of the +6 before the cap.
    def barely_hit(player, enemies, pilot, seed):
        player.hp = max(1, player.hp - 3)
        for e in enemies:
            e.hp = 0
        return CombatState(player=player, enemies=enemies,
                           rng=random.Random(seed))
    monkeypatch.setattr(model, "run_fight", barely_hit)
    r = model.run_one("ref_ironclad", "demolition", "demolition", _skip, 1)
    max_hp = loader._character_index()["ref_ironclad"]["hp"]
    # -3 then +6 would be max_hp+3; the cap holds it at max_hp.
    assert r.hp_by_node[0] == max_hp
