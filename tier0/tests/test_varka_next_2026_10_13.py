"""`varka-next` (Varka round 5, review/records/varka-round-5-2026-10-13.md,
"What to change" 3 and 4; staging paper review/active/varka-next-2026-10-13.md):

  * Eula: Icetide Vortex is an Attack, same cost and numbers, so the sim
    counts it where it counts Attacks (Lisa: Infinite Circuit's Block);
  * Twin Gales pays a matched element twice (the payout tests are in
    test_varka_expansion.py).
"""
from __future__ import annotations

from tier0.content import loader
from tier0.tests.test_varka_expansion import (_enemy, _led, _play, _state,
                                              _vk, varka)  # noqa: F401


def test_icetide_vortex_is_an_attack_with_its_old_numbers(varka):
    eula = loader.get_card(_vk("eula_icetide_vortex"))
    assert eula.type == "attack"
    assert eula.cost == 1
    up = loader.get_card(_vk("eula_icetide_vortex") + "+")
    assert (up.type, up.cost) == ("attack", 1)
    dmg = [f for f in eula.effects if f["op"] == "damage"]
    up_dmg = [f for f in up.effects if f["op"] == "damage"]
    assert (dmg[0]["amount"], up_dmg[0]["amount"]) == (8, 11)


def test_icetide_vortex_counts_as_an_attack_played(varka):
    st = _state(enemies=[_enemy(name="a")])
    _play(st, _vk("eula_icetide_vortex"))
    block = st.player.block
    _play(st, _vk("lisa_violet_arc"))
    # Infinite Circuit: 6, plus 3 for each Attack played this turn.
    assert st.player.block - block == 6 + 3
