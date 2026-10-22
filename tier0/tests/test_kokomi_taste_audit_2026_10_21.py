"""THE KOKOMI TASTE AUDIT (2026-10-21), the sim side.

The ruling is review/active/kokomi-taste-audit-2026-10-21.md, "Ruled
2026-10-21: all five (a)" ([USER]: "That's a lot of card changes, but we can
do that and rerun the balance suite to see how it feels." and "Agreed on all
5 defaults."). Ten cards change; the C# twins are pinned in
`klee-mod/KleeTests/Prototype/KokomiTasteAuditTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import inspect

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects, kokomi_plan
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    IDLE, caches, card, carry_out, kokomi_state, write)

ATTACK = [{"kind": "attack", "amount": 6}]


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _casket(st):
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]


def _face_up(st, c):
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


def _queue(st):
    return [e.card_id for e in st.kk_plan_queue]


# --- 1. Shoal Call ------------------------------------------------------------

def test_shoal_call_plans_three_stings_and_the_casket_pays_for_each():
    """"Plan 3 [4] Stings." Each goes into the Plans queue as a Sting she
    Planned would, and the Tamakushi Casket pays 2 Block for each, as it does
    for one she Planned herself."""
    st = kokomi_state()
    _casket(st)
    _face_up(st, card("proto_kk_shoal_call"))
    assert _queue(st) == [kokomi_plan.STING_ID] * 3
    assert all(c.id != kokomi_plan.STING_ID for c in st.player.hand)
    assert st.player.block == 3 * C.KOKOMI_OVERHAUL_CASKET_BLOCK

    planned = kokomi_state()
    _casket(planned)
    write(planned, card(kokomi_plan.STING_ID))
    assert planned.player.block == C.KOKOMI_OVERHAUL_CASKET_BLOCK

    up = kokomi_state()
    _face_up(up, _up("proto_kk_shoal_call"))
    assert _queue(up) == [kokomi_plan.STING_ID] * 4


def test_a_planned_sting_is_carried_out_on_its_plan_line():
    st = kokomi_state(n_enemies=2)
    _face_up(st, card("proto_kk_shoal_call"))
    hp = [e.hp for e in st.enemies]
    carry_out(st)
    # Three Sting Plans, 3 to ALL each.
    assert [h - e.hp for h, e in zip(hp, st.enemies)] == [9, 9]
    assert st.kk_plan_queue == []


# --- 2. Kurage Bloom ----------------------------------------------------------

def test_kurage_bloom_plans_a_sting_at_the_end_of_her_turn():
    st = kokomi_state()
    _casket(st)
    st.player.powers[kokomi_plan.KURAGE_BLOOM] = 1
    kokomi_plan.turn_start_generators(st)
    assert st.player.hand == [] and st.kk_plan_queue == []
    kokomi_plan.turn_end(st)
    assert _queue(st) == [kokomi_plan.STING_ID]
    assert st.player.hand == []
    assert st.player.block == C.KOKOMI_OVERHAUL_CASKET_BLOCK
    row = loader.get_card("proto_kk_kurage_bloom")
    assert (row.cost, row.type, row.rarity) == (1, "power", "uncommon")
    assert _up("proto_kk_kurage_bloom").innate


def test_her_turn_end_runs_ahead_of_the_shipped_triggers():
    """`ProtoBakeKuragePower.BeforeSideTurnEnd` is a power tenant, which runs
    ahead of the model-driven `TurnEndSequencer`; the sim keeps that order."""
    src = inspect.getsource(combat)
    assert (src.index("kokomi_plan.turn_end(state)")
            < src.index("effects.player_turn_end_triggers(state)"))


# --- 3. Resolve of Watatsumi --------------------------------------------------

def test_resolve_of_watatsumi_adds_to_each_hit_and_each_block_of_a_plan():
    st = kokomi_state()
    st.player.powers[kokomi_plan.RESOLVE_OF_WATATSUMI] = 2
    probe = Card(id="proto_kk_probe", name="probe", cost=0, type="skill",
                 effects=[], plan=[{"op": "block", "amount": 5},
                                   {"op": "damage", "amount": 4,
                                    "target": "front_enemy", "times": 2}])
    write(st, probe)
    write(st, card(kokomi_plan.STING_ID))
    hp = st.enemies[0].hp
    carry_out(st)
    # The probe: 5 + 2 Block; two hits of 4 + 2. The Sting: 3 + 2.
    assert st.player.block == 7
    assert hp - st.enemies[0].hp == 2 * 6 + 5


def test_resolve_of_watatsumi_row():
    row = loader.get_card("proto_kk_resolve_of_watatsumi")
    assert (row.cost, row.type, row.rarity) == (1, "power", "uncommon")
    assert row.effects == [{"op": "apply_power",
                            "power": kokomi_plan.RESOLVE_OF_WATATSUMI,
                            "amount": 2, "target": "self"}]
    assert _up("proto_kk_resolve_of_watatsumi").effects[0]["amount"] == 3


# --- 4. Coral Crash -----------------------------------------------------------

def test_coral_crash_plan_hits_each_enemy_that_intends_to_attack_at_carry_out():
    st = kokomi_state(n_enemies=2)
    write(st, card("proto_kk_coral_crash"))
    attacker, idle = st.enemies
    attacker.intents = list(ATTACK)          # the intent read at carry-out
    hp = [e.hp for e in st.enemies]
    carry_out(st)
    assert hp[0] - attacker.hp == 8
    assert hp[1] == idle.hp


# --- 5. Watatsumi's Grace -----------------------------------------------------

def test_watatsumis_grace_gains_block_for_each_plan_waiting():
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 3
    kokomi_plan.turn_end(st)
    assert st.player.block == 0
    write(st, card(kokomi_plan.STING_ID))
    write(st, card(kokomi_plan.WARD_ID))
    write(st, card("proto_kk_coral_crash"))
    kokomi_plan.turn_end(st)
    # Kokomi defence pass (2026-10-22): "Stings and Wards don't count."
    assert len(st.kk_plan_queue) == 3
    assert st.player.block == 1 * 3
    # It keeps nothing at the clear (was the Sturdy Clamp shape).
    assert effects.block_clear_keeps(st) is None
    assert _up("proto_kk_watatsumis_grace").effects[0]["amount"] == 4


def test_grace_does_not_count_kurage_blooms_sting():
    """Kokomi defence pass (2026-10-22): Bloom's Sting is a Sting."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 3
    st.player.powers[kokomi_plan.KURAGE_BLOOM] = 1
    kokomi_plan.turn_end(st)
    assert len(st.kk_plan_queue) == 1
    assert st.player.block == 0


# --- 6. Sea's Reproach --------------------------------------------------------

def test_seas_reproach_weakens_each_attacker_and_the_upgrade_hits_it():
    attacker = make_enemy(hp=100, name="a", intents=list(ATTACK))
    idle = make_enemy(hp=100, name="b", intents=list(IDLE))
    st = kokomi_state()
    st.enemies = [attacker, idle]
    st.player.powers[kokomi_plan.SEAS_REPROACH] = 1
    kokomi_plan.seas_reproach(st)
    assert attacker.powers.get("weak") == 1 and attacker.hp == 100
    assert not idle.powers.get("weak") and idle.hp == 100
    st.player.powers[kokomi_plan.SEAS_REPROACH_PLUS] = 1
    kokomi_plan.seas_reproach(st)
    # Two copies: 2 Weak; the upgraded copy deals 5.
    assert attacker.powers.get("weak") == 3
    assert attacker.hp == 100 - C.KOKOMI_SEAS_REPROACH_DAMAGE
    assert idle.hp == 100


def test_seas_reproach_is_read_after_the_mornings_plans():
    src = inspect.getsource(combat)
    assert (src.index("kokomi_plan.resolve_all(state)")
            < src.index("kokomi_plan.seas_reproach(state)"))


# --- 7. Suffocating Deep (and 8. Undertow) --------------------------------------
# `test_kokomi_expansion.py` and `test_eb624_undertows_two_printed_numbers.py`
# hold the behaviour; the rows here.

def test_suffocating_deep_and_undertow_rows():
    deep = loader.get_card("proto_kk_suffocating_deep")
    assert (deep.cost, deep.rarity, deep.exhaust) == (2, "rare", True)
    assert deep.effects[1] == {"op": "kokomi", "kind": "weak_vuln_attackers",
                               "amount": 2}
    under = loader.get_card("proto_kk_undertow")
    assert under.effects == [{"op": "damage", "amount": 7, "target": "enemy",
                              "bonus_vs_attacker": 3}]


# --- 9. Flotsam Surge ---------------------------------------------------------

def test_flotsam_surges_plan_hits_all_and_plans_a_sting_for_the_next_morning():
    st = kokomi_state(n_enemies=2)
    _casket(st)
    write(st, card("proto_kk_flotsam_surge"))
    block = st.player.block                  # its own Plan's Casket payout
    hp = [e.hp for e in st.enemies]
    carry_out(st)
    assert [h - e.hp for h, e in zip(hp, st.enemies)] == [9, 9]
    # The Sting waits for the next morning, and the Casket paid for it.
    assert _queue(st) == [kokomi_plan.STING_ID]
    assert st.player.block - block == C.KOKOMI_OVERHAUL_CASKET_BLOCK
    assert st.player.discard_pile == [] or all(
        c.id != "status_dazed" for c in st.player.discard_pile)


# --- 10. Riptide Ruin ---------------------------------------------------------

def test_riptide_ruin_hits_once_more_per_plan_carried_out_not_stings():
    st = kokomi_state(n_enemies=2)
    write(st, card(kokomi_plan.STING_ID))
    write(st, card("proto_kk_coral_crash"))
    carry_out(st)
    assert st.kk_chain_plans_this_turn == 1   # the Sting does not count
    hp = [e.hp for e in st.enemies]
    _face_up(st, card("proto_kk_riptide_ruin"))
    assert [h - e.hp for h, e in zip(hp, st.enemies)] == [18, 18]
