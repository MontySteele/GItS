"""`EB-495` D3 — the Stage's acts and bows are Unpowered in BOTH engines.

`FurinaStage.Perform` passes `powered: false` twice (one per damage act; since
draft 3, 2026-09-25, the Bow is the act once more and shares them) — the same refusal the Salon's
`PerformMember` makes at `SalonPowers.cs:981`, and the same one the sim's own
Salon twin already made at `effects.salon_member_act`. The sim's three Stage
call sites passed no `powered=` at all, so the signature's `True` applied and
Furina's Strength and Weak scaled a performance in tier0 and not in the game.

THE BRIEF IS WITH THE GAME, so the sim was the one-sided defect and this is
the model catching up, not a rule moving. `review/active/furina-stage-brief-
2026-09-08.md` sec.3 rule 10 calls an act "a flat act that does not read its
bar" and ends "scaling on Fanfare lives in payoff cards (§5.2), never in the
performer"; the sentence the Stage inherited from the Salon is "a performance
is not an Attack and not a hit" (`EB-588`).

THE PIN IS PRINTED-EQUALS-DEALT. Strength up, Weak on, and the number that
lands is still the constant on the row. Weak is pinned beside Strength because
`powered` drops both in one place (`powers.modify_damage_dealt`), so a repair
that reached only one of them would pass a Strength-only test.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B): these are shape
assertions about an engine, not numbers about a game.
"""

from __future__ import annotations

import random

import pytest

from tier0.engine import furina_stage
from tier0.engine.state import CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _state(enemy_hp=99, **powers):
    player = Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina")
    player.powers.update(powers)
    enemy = Enemy(hp=enemy_hp, max_hp=enemy_hp, name="paper",
                  intents=[{"kind": "block", "amount": 0}])
    st = CombatState(player=player, enemies=[enemy], rng=random.Random(0))
    st.turn = 1
    return st


@pytest.mark.parametrize("modifier", [{}, {"strength": 5}, {"weak": 2},
                                      {"strength": 5, "weak": 2}])
def test_crabalettas_act_deals_its_printed_number(arm, modifier):
    st = _state(**modifier)
    st.player.stage = [["crabaletta", 4]]
    FS.perform(st, "crabaletta")
    assert st.enemies[0].hp == 99 - FS.ACT_CRABALETTA_DAMAGE


@pytest.mark.parametrize("modifier", [{}, {"strength": 5}, {"weak": 2},
                                      {"strength": 5, "weak": 2}])
def test_chevalmarins_act_deals_its_printed_number(arm, modifier):
    st = _state(**modifier)
    st.player.stage = [["chevalmarin", 4]]
    FS.perform(st, "chevalmarin")
    assert st.enemies[0].hp == 99 - FS.ACT_CHEVALMARIN_DAMAGE


@pytest.mark.parametrize("modifier", [{}, {"strength": 5}, {"weak": 2},
                                      {"strength": 5, "weak": 2}])
def test_crabalettas_bow_deals_its_printed_number(arm, modifier):
    """Reached the way a player reaches it: a Spend that empties the bar
    earns the curtain call (rule 9), which since draft 3 (2026-09-25) is the
    act once more -- the same unpowered hit."""
    st = _state(**modifier)
    st.player.stage = [["crabaletta", 1]]
    FS.spend(st, 1)
    assert st.player.stage == []
    assert st.enemies[0].hp == 99 - FS.ACT_CRABALETTA_DAMAGE


def test_furinas_own_card_still_takes_her_strength(arm):
    """The control, and the reason this is a parity repair rather than a
    blanket: `powered=False` is a fact about the PERFORMER, not about Furina.
    Her own damage is unchanged."""
    from tier0.engine import effects
    st = _state(strength=5)
    effects.deal_damage_to_enemy(st, st.enemies[0], 6, source="attack")
    assert st.enemies[0].hp == 99 - (6 + 5)
