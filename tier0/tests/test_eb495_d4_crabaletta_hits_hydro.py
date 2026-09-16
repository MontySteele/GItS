"""`EB-495` D4 — Crabaletta's act and bow are Hydro in BOTH engines.

`FurinaStage.cs:461` (the act) and `:542` (the bow) both pass
`Elements.Element.Hydro` into `ElementalHit.Deal`. The sim's two Crabaletta
legs passed no `element=`, so the default `None` applied: the hit set no aura
and consumed none, and every reaction off a Crabaletta hit existed in the game
and nowhere in tier0.

THE BRIEF IS SILENT, so the game is the answer and this is a one-sided sim
defect. `review/active/furina-stage-brief-2026-09-08.md` names Chevalmarin's
Hydro twice in as many words — rule 10 "deals 2 to every enemy and applies
Hydro", rule 9 "Chevalmarin: Hydro on every enemy" — and says only "Crabaletta
deals 5 to a random enemy" and "Crabaletta: deal 8 to a random enemy". It
never says Crabaletta's hit is elementless; it simply does not raise the
question, so there is no rule for the C# to contradict. Recorded here because
the reading is the load-bearing part: if the brief is later written to say a
Crabaletta hit carries no element, this is the file that has to change and the
C# with it, and that is a rule change rather than a parity repair.

THE REACTION, CORRECTED. `EB-495`'s row text says a Crabaletta hit into an
Electro aura applies Superconduct's Vulnerable. It does not, in either
engine: Superconduct is Electro + Cryo (`reactions.py`, and
`ReactionEffects.cs` with it), and Hydro into Electro is ELECTRO-CHARGED,
whose rider is a DoT. The observable is the same one either way — a reaction
that fired in the game and not in the sim — and the DoT is what is pinned.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B): these are shape
assertions about an engine, not numbers about a game.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.engine import furina_stage
from tier0.engine.state import CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _state(aura=None, enemy_hp=99):
    player = Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina")
    enemy = Enemy(hp=enemy_hp, max_hp=enemy_hp, name="paper",
                  intents=[{"kind": "block", "amount": 0}])
    enemy.aura = aura
    st = CombatState(player=player, enemies=[enemy], rng=random.Random(0))
    st.turn = 1
    return st


def test_crabalettas_act_leaves_a_hydro_aura(arm):
    st = _state()
    st.player.stage = [["crabaletta", 4]]
    FS.perform(st, "crabaletta")
    assert st.enemies[0].aura == "hydro"


def test_crabalettas_bow_leaves_a_hydro_aura(arm):
    st = _state()
    st.player.stage = [["crabaletta", 1]]
    FS.spend(st, 1)
    assert st.player.stage == []
    assert st.enemies[0].aura == "hydro"


def test_a_crabaletta_act_into_an_electro_aura_reacts(arm):
    """The cell the repair is actually about. Electro standing, Hydro landing:
    Electro-Charged fires, its DoT lands, and the aura is consumed."""
    st = _state(aura="electro")
    st.player.stage = [["crabaletta", 4]]
    FS.perform(st, "crabaletta")
    enemy = st.enemies[0]
    assert enemy.powers.get("dot", 0) == C.ELECTROCHARGED_DOT
    assert enemy.aura is None
    assert [e for e in st.log
            if e["event"] == "reaction"
            and e.get("reaction") == "electrocharged"]


def test_a_crabaletta_bow_into_an_electro_aura_reacts(arm):
    st = _state(aura="electro")
    st.player.stage = [["crabaletta", 1]]
    FS.spend(st, 1)
    assert st.enemies[0].powers.get("dot", 0) == C.ELECTROCHARGED_DOT


def test_the_aura_lands_even_when_block_eats_the_hit(arm):
    """The element is the HIT's, not the damage's, in both engines:
    `ElementalHit.Deal` resolves the reaction before the number reaches the
    body, and `deal_damage_to_enemy` applies the aura ahead of Block for the
    same reason. So a fully blocked Crabaletta act still leaves Hydro."""
    st = _state()
    st.enemies[0].block = 50
    st.player.stage = [["crabaletta", 4]]
    FS.perform(st, "crabaletta")
    assert st.enemies[0].aura == "hydro"
    assert st.enemies[0].hp == 99
