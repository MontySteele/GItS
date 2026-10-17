"""Yae flat-value pass, 2026-10-17 (review/active/yae-flat-value-2026-10-17.md
sec.3, ruled 2026-10-17: [USER], "This all looks good" and "let's run just the
Commons for now and then see where we're at"). Sim half; the C# half is
`klee-mod/KleeTests/Prototype/YaeFlatValueTests.cs`.

Pinned: the eight attacks' new numbers, and Thunder Petal's "It strikes this
enemy." / Foxfire Sweep's "It strikes now." (`strike_planted`): the planted
Sakura acts once at its Level, on the card's target (a Foxfire on ALL), using
none of its turns and not as a Tenko; into a full shrine, the Sakura the plant
refreshed is the one that strikes.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _enemy(name="e0", hp=100):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=[{"kind": "block", "amount": 0}])


def _state(n_enemies=1, seed=0):
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(10)]
    st = CombatState(player=p,
                     enemies=[_enemy(f"e{i}") for i in range(n_enemies)],
                     rng=random.Random(seed))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card, target=None):
    if isinstance(card, str):
        card = _card(card)
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    if target is None:
        combat.play_card(st, card)
        return card
    orig = effects.bind_card_aim
    effects.bind_card_aim = lambda state, c: target
    try:
        combat.play_card(st, card)
    finally:
        effects.bind_card_aim = orig
    return card


def _led(st):
    return Y.ledger(st.player)


def _hp(st):
    return [e.hp for e in st.enemies]


def _events(st, name):
    return [r for r in st.log if r["event"] == name]


# --- the numbers -------------------------------------------------------------

@pytest.mark.parametrize("name, base, upgraded", [
    ("sly_strike", 8, 10),
    ("margin_note", 7, 10),
    ("sesshou_fang", 8, 10),            # no Sakura at Level 3: the base hit
    ("thunder_rite", 13, 17),           # an empty shrine: the Tenko does nothing
    ("publishers_deadline", 14, 18),
    ("galley_proof", 14, 18),
])
def test_the_flat_value_numbers(name, base, upgraded):
    for card, dmg in ((name, base), (name + "+", upgraded)):
        st = _state()
        _play(st, card)
        assert _hp(st) == [100 - dmg], card


def test_sly_strike_upgrade_applies_2_weak():
    st = _state()
    _play(st, "sly_strike")
    assert st.enemies[0].powers.get("weak") == 1
    st = _state()
    _play(st, "sly_strike+")
    assert st.enemies[0].powers.get("weak") == 2


def test_sesshou_fang_bonus_stays_6_upgraded_8():
    st = _state()
    Y.plant(st, 1, level=3)
    _play(st, "sesshou_fang")
    assert _hp(st) == [100 - 8 - 6]
    st = _state()
    Y.plant(st, 1, level=3)
    _play(st, "sesshou_fang+")
    assert _hp(st) == [100 - 10 - 8]


def test_proofread_is_unchanged():
    # Yakan Evocation's "It strikes now." is the draft pass's (2026-10-17,
    # round 9 pick 1 (a)): `test_yae_draft_pass.py`.
    st = _state()
    _play(st, "proofread")
    assert _hp(st) == [100] and not _led(st).sakura
    assert not _events(st, "yae_sakura_strike")


# --- "It strikes this enemy." / "It strikes now." ----------------------------

def test_thunder_petal_its_sakura_strikes_this_enemy():
    st = _state(n_enemies=3)
    _play(st, "thunder_petal", target=st.enemies[2])
    led = _led(st)
    assert len(led.sakura) == 1 and led.sakura[0].level == 1
    strikes = _events(st, "yae_sakura_strike")
    assert len(strikes) == 1 and strikes[0]["target"] == "e2"
    assert _hp(st) == [100, 100, 100 - 5 - (2 + 1)]


def test_thunder_petal_upgraded_is_8_and_the_strike():
    st = _state()
    _play(st, "thunder_petal+")
    assert _hp(st) == [100 - 8 - (2 + 1)]


def test_foxfire_sweep_its_foxfire_sakura_hits_all_now():
    st = _state(n_enemies=3)
    _play(st, "foxfire_sweep", target=st.enemies[0])
    assert _led(st).sakura[0].kind == Y.FOXFIRE
    assert _events(st, "yae_sakura_strike")[0]["target"] == "ALL"
    assert _hp(st) == [100 - 4 - (1 + 1)] * 3
    st = _state(n_enemies=2)
    _play(st, "foxfire_sweep+")
    assert _hp(st) == [100 - 6 - (1 + 1)] * 2


def test_the_strike_uses_none_of_its_turns():
    st = _state()
    _play(st, "thunder_petal")
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS
    st = _state()
    _play(st, "foxfire_sweep")
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS


def test_the_strike_is_not_a_tenko(monkeypatch):
    st = _state()
    Y.plant(st, 1)
    older = _led(st).sakura[0]
    older.turns_left = 1
    called = []
    monkeypatch.setattr(Y, "tenko", lambda state: called.append(True))
    _play(st, "thunder_petal")
    assert not called and not _events(st, "yae_tenko")
    assert older.turns_left == 1                  # no refresh
    assert len(_events(st, "yae_sakura_strike")) == 1   # only the new one


def test_into_a_full_shrine_the_refreshed_sakura_strikes():
    st = _state()
    Y.plant(st, 3)
    led = _led(st)
    oldest = led.sakura[0]
    _play(st, "thunder_petal")
    assert len(led.sakura) == 3 and led.last_planted is oldest
    assert oldest.level == 2
    # 5, the full shrine's act of the oldest at Level 1 (3), then the
    # refreshed Sakura's strike at Level 2 (4).
    assert _hp(st) == [100 - 5 - 3 - 4]


def test_into_a_full_shrine_of_another_kind_the_new_sakura_strikes():
    st = _state(n_enemies=2)
    Y.plant(st, 3)
    _play(st, "foxfire_sweep")
    led = _led(st)
    assert led.last_planted is led.sakura[-1]
    assert led.sakura[-1].kind == Y.FOXFIRE
    strikes = _events(st, "yae_sakura_strike")
    assert strikes[-1]["kind"] == Y.FOXFIRE and strikes[-1]["target"] == "ALL"
    # 4 to ALL; the replaced oldest's act (3, one enemy); the Foxfire's 2 to ALL.
    assert sorted(_hp(st)) == [100 - 4 - 3 - 2, 100 - 4 - 2]
