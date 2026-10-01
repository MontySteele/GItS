"""VARKA, ELEMENT IDENTITIES -- the sim engine's pins for the ruled paper
`review/active/varka-element-identities-2026-10-01.md` (picks 1 to 5 at the
defaults, 2026-10-01; Violet Storm raised to 8 [11] and an Attack): Electro's
discard-and-spend cards, Thundering Verdict at X, Retaliating Tide, Wildfire
Oath's one big hit, the element-switch warnings' codegen half, and the faces
the Varka round read wrong. Rules: `tier0/engine/varka_oath.py`; rows: the
`proto_vk_` block of `docs/prototype-surface.yaml`. The C# twin is
`klee-mod/KleeTests/Prototype/VarkaElementIdentitiesTests.cs`.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def varka():
    saved = (C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA)
    C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = True, True
    loader.reset_arm_caches()
    try:
        yield
    finally:
        C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = saved
        loader.reset_arm_caches()


def _enemy(hp=100, name="e", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left, e.aura_spent = aura, 2, False
    return e


def _state(n=1, element="pyro", enemies=None):
    enemies = enemies or [_enemy(name=f"e{i}") for i in range(n)]
    p = V.build_player(element, fang=False)
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _vk(name):
    return "proto_vk_" + name


def _play(st, card, energy=10):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = energy
    combat.play_card(st, card)
    return card


def _fx(cid, op, i=0):
    return [f for f in loader.get_card(cid).effects if f["op"] == op][i]


# ---------------------------------------------------------------------------
# 1. The pool: 78, each new card in its old card's place.
# ---------------------------------------------------------------------------

NEW = ("charged_lunge", "short_circuit", "chain_lightning", "violet_storm",
       "retaliating_tide")
GONE = ("updraft", "pressure_front", "unfurled_banner", "four_winds_accord",
        "unbroken_tide")


def test_the_pool_stays_78_with_the_five_swaps(varka):
    pool = {c.id: c for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX) and c.rarity != "basic"}
    assert len(pool) == 78
    by = {r: sum(1 for c in pool.values() if c.rarity == r)
          for r in ("common", "uncommon", "rare")}
    assert by == {"common": 20, "uncommon": 35, "rare": 23}
    assert {_vk(x) for x in NEW} <= set(pool)
    assert not {_vk(x) for x in GONE} & set(pool)
    rarity = {x: pool[_vk(x)].rarity for x in NEW}
    assert rarity == {"charged_lunge": "common", "short_circuit": "uncommon",
                      "chain_lightning": "uncommon", "violet_storm": "rare",
                      "retaliating_tide": "rare"}


def test_the_paper_numbers(varka):
    assert _fx(_vk("charged_lunge"), "varka")["base"] == 6
    assert _fx(_vk("charged_lunge") + "+", "varka")["base"] == 9
    assert _fx(_vk("short_circuit"), "discard")["amount"] == 3
    assert _fx(_vk("short_circuit") + "+", "discard")["amount"] == 2
    assert _fx(_vk("short_circuit"), "energy")["amount"] == 2
    assert loader.get_card(_vk("short_circuit")).cost == 0
    assert loader.get_card(_vk("chain_lightning")).cost == 2
    assert _fx(_vk("chain_lightning") + "+", "varka")["base"] == 11
    verdict = loader.get_card(_vk("thundering_verdict"))
    assert verdict.cost == "X" and verdict.rarity == "rare"
    assert (_fx(verdict.id, "varka")["base"], _fx(verdict.id, "varka")["per"]) \
        == (6, 1)
    assert _fx(verdict.id + "+", "varka")["base"] == 8
    storm = loader.get_card(_vk("violet_storm"))
    assert (storm.type, storm.cost, storm.rarity) == ("attack", 1, "rare")
    assert _fx(storm.id, "varka")["base"] == 8
    assert _fx(storm.id + "+", "varka")["base"] == 11
    tide = loader.get_card(_vk("retaliating_tide"))
    assert (tide.type, tide.cost) == ("power", 2)
    assert loader.get_card(tide.id + "+").cost == 1
    # Sec.2: Dawn Patrol exhausts (the expansion already printed it).
    assert loader.get_card(_vk("dawn_patrol")).exhaust is True


# ---------------------------------------------------------------------------
# 2. Electro.
# ---------------------------------------------------------------------------

def test_charged_lunge_hits_electro_and_draws(varka):
    st = _state()
    _play(st, _vk("charged_lunge"))
    e = st.enemies[0]
    assert e.hp == 100 - 6 and e.aura == "electro"
    assert len(st.player.hand) == 1
    assert V.ledger(st.player).current == "electro"     # the open Oath


def test_short_circuit_discards_three_for_two_energy_and_electro(varka):
    st = _state()
    st.player.hand = [loader.get_card("strike") for _ in range(4)]
    card = loader.get_card(_vk("short_circuit"))
    st.player.hand.append(card)
    st.player.energy = 1
    combat.play_card(st, card)
    assert st.player.energy == 3                         # 0 cost, +2
    assert len(st.player.hand) == 1                      # 4 - 3 discarded
    assert st.discards_this_turn == 3
    assert st.enemies[0].aura == "electro"


def test_chain_lightning_costs_one_less_per_discard(varka):
    st = _state(n=2)
    chain = loader.get_card(_vk("chain_lightning"))
    assert combat.card_cost(st, chain) == 2
    st.discards_this_turn = 1
    assert combat.card_cost(st, chain) == 1
    st.discards_this_turn = 5
    assert combat.card_cost(st, chain) == 0
    st.discards_this_turn = 0
    _play(st, chain)
    assert [e.hp for e in st.enemies] == [100 - 8] * 2
    assert all(e.aura == "electro" for e in st.enemies)


def test_chain_lightning_after_short_circuit_is_free(varka):
    st = _state()
    st.player.hand = [loader.get_card("strike") for _ in range(3)]
    chain = loader.get_card(_vk("chain_lightning"))
    st.player.hand.append(chain)
    circuit = loader.get_card(_vk("short_circuit"))
    st.player.hand.append(circuit)
    st.player.energy = 0
    combat.play_card(st, circuit)
    # The pilot's discard pick may take Chain Lightning itself; a copy left
    # in hand costs 2 - 3 discards = 0.
    if chain in st.player.hand:
        assert combat.card_cost(st, chain) == 0
    assert st.player.energy == 2


def test_violet_storm_discards_the_hand_and_hits_per_card(varka):
    st = _state(n=2)
    st.player.hand = [loader.get_card("strike") for _ in range(3)]
    _play(st, _vk("violet_storm"))
    assert st.player.hand == []
    assert st.discards_this_turn == 3
    assert sum(100 - e.hp for e in st.enemies) == 3 * 8
    assert V.ledger(st.player).oath["electro"] == 1     # one credit per card


def test_violet_storm_with_an_empty_hand_hits_nothing(varka):
    st = _state()
    _play(st, _vk("violet_storm"))
    assert st.enemies[0].hp == 100


def test_thundering_verdict_spends_x(varka):
    st = _state(n=2)
    card = loader.get_card(_vk("thundering_verdict"))
    st.player.hand.append(card)
    st.player.energy = 3
    combat.play_card(st, card)
    assert st.player.energy == 0
    # 6 + 1 x Electro Oath (0 before the hits), three times, to ALL.
    assert [e.hp for e in st.enemies] == [100 - 18] * 2
    st = _state()
    card = loader.get_card(_vk("thundering_verdict"))
    st.player.hand.append(card)
    st.player.energy = 0
    combat.play_card(st, card)
    assert st.enemies[0].hp == 100


# ---------------------------------------------------------------------------
# 3. Hydro: Retaliating Tide.
# ---------------------------------------------------------------------------

def test_retaliating_tide_deals_block_up_to_hydro_oath(varka):
    st = _state(n=1)
    led = V.ledger(st.player)
    st.player.powers[V.RETALIATING_TIDE] = 1
    led.oath["hydro"] = 5
    st.player.block = 12
    V.turn_end(st)
    assert st.enemies[0].hp == 100 - 5
    st = _state(n=1)
    led = V.ledger(st.player)
    st.player.powers[V.RETALIATING_TIDE] = 1
    led.oath["hydro"] = 9
    st.player.block = 4
    V.turn_end(st)
    assert st.enemies[0].hp == 100 - 4


def test_retaliating_tide_reads_the_aegis_block(varka):
    st = _state(n=1)
    led = V.ledger(st.player)
    st.player.powers[V.RETALIATING_TIDE] = 1
    st.player.powers[V.OATHBOUND_AEGIS] = 15
    led.oath["hydro"] = 6
    st.player.block = 0
    V.turn_end(st)
    assert st.player.block == 6                         # the Aegis's
    assert st.enemies[0].hp == 100 - 6                  # then the Tide


def test_unbroken_tide_left_the_engine():
    assert not hasattr(V, "keeps_block")
    assert not hasattr(V, "UNBROKEN_TIDE")


# ---------------------------------------------------------------------------
# 4. Pyro: Wildfire Oath's one big hit.
# ---------------------------------------------------------------------------

def test_wildfire_adds_pyro_oath_to_the_first_attacks_first_hit(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current, led.oath["pyro"] = "pyro", 7
    st.player.powers[V.WILDFIRE_OATH] = 1
    _play(st, _vk("squall"))                             # 4 twice
    assert st.enemies[0].hp == 100 - (4 + 7) - 4
    hp = st.enemies[0].hp
    _play(st, _vk("squall"))                             # the turn's second
    assert st.enemies[0].hp == hp - 8
    st.turn = 2
    hp = st.enemies[0].hp
    _play(st, _vk("squall"))                             # a new turn
    assert st.enemies[0].hp == hp - (4 + 7) - 4


def test_wildfire_needs_pyro_current_and_a_first_attack(varka):
    st = _state()
    led = V.ledger(st.player)
    led.current, led.oath["pyro"] = "hydro", 7
    st.player.powers[V.WILDFIRE_OATH] = 1
    _play(st, _vk("squall"))
    assert st.enemies[0].hp == 100 - 8
    led.current = "pyro"
    _play(st, _vk("squall"))                             # not the first
    assert st.enemies[0].hp == 100 - 16
    # Skills do not spend it; stacks multiply it.
    st = _state()
    led = V.ledger(st.player)
    led.current, led.oath["pyro"] = "pyro", 3
    st.player.powers[V.WILDFIRE_OATH] = 2
    _play(st, _vk("wind_wall"))
    _play(st, _vk("favonius_cut"))
    assert st.enemies[0].hp == 100 - 14 - 6


def test_wildfire_no_longer_widens_the_swirl(varka):
    st = _state(n=2, enemies=[_enemy(name="a", aura="hydro"),
                              _enemy(name="b", aura="hydro")])
    led = V.ledger(st.player)
    led.current, led.oath["pyro"] = "pyro", 4
    st.player.powers[V.WILDFIRE_OATH] = 1
    _play(st, _vk("jean_dandelion_breeze"))              # a Skill
    # The flat 2 to both, then Pyro's 3 to the one Swirled.
    assert sorted(e.hp for e in st.enemies) == [100 - 2 - 3, 100 - 2]


# ---------------------------------------------------------------------------
# 5. The faces: the codegen's half of sec.7 and the round's misreads.
# ---------------------------------------------------------------------------

def _rows():
    from tier0.content import yaml_memo
    raw = yaml_memo.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
    return {r["id"]: r for r in raw}


def test_the_switch_element_each_row_declares():
    import tools.gen_klee_cards as gen
    profile = gen.PROTOTYPE_OWNERS["varka"]
    rows = _rows()
    want = {
        "blazing_charge": "pyro", "charged_lunge": "electro",
        "short_circuit": "electro", "chain_lightning": "electro",
        "violet_storm": "electro", "thundering_verdict": "electro",
        "tempest_of_the_four_winds": "electro",     # Electro, last, wins
        "tidal_bulwark": "hydro", "glacial_edict": "cryo",
        "amber_baron_bunny": "pyro", "lisa_pulsating_witch": "electro",
        "kaeya_frostgnaw": "cryo",
        "favonius_drill": None, "cavalry_charge": None,
        "pathfinders_mark": None, "noelle_steadfast_maid": None,
        "squall": None, "northwind_avatar": None,
    }
    got = {k: gen.varka_switch_element(rows[_vk(k)], profile) for k in want}
    assert got == want


def test_element_kinds_are_tagged_with_their_element_not_anemo():
    import tools.gen_klee_cards as gen
    profile = gen.PROTOTYPE_OWNERS["varka"]
    rows = _rows()
    for name, tags in (("cavalry_charge", []), ("blazing_charge", ["pyro"]),
                       ("charged_lunge", ["electro"]),
                       ("violet_storm", ["electro"]),
                       ("thundering_verdict", ["electro"]),
                       ("tempest_of_the_four_winds",
                        ["pyro", "hydro", "cryo", "electro"])):
        row = rows[_vk(name)]
        assert gen.varka_kind_owns_element(row), name
        assert not profile.damage_applies_element(row), name
        assert gen.declares_no_element(row, profile), name
        assert gen.element_tag_elements_for(row, profile, False) == tags, name
    avatar = rows[_vk("northwind_avatar")]
    assert not gen.varka_kind_owns_element(avatar)
    assert profile.damage_applies_element(avatar)


def test_the_generated_faces():
    gen_dir = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
    cavalry = (gen_dir / "ProtoVkCavalryCharge.cs").read_text(encoding="utf-8")
    assert "AppliesAnemo" not in cavalry
    assert "public Element Element => Element.None;" in cavalry
    blazing = (gen_dir / "ProtoVkBlazingCharge.cs").read_text(encoding="utf-8")
    assert "KleeKeywords.AppliesPyro" in blazing
    assert "ArmKeywordTips.ForElementSwitch(" in blazing
    assert "Element.Pyro)" in blazing
    chain = (gen_dir / "ProtoVkChainLightning.cs").read_text(encoding="utf-8")
    assert "TryModifyEnergyCostInCombat" in chain
    assert "KokomiResources.DiscardsThisTurn(this)" in chain
    verdict = (gen_dir / "ProtoVkThunderingVerdict.cs").read_text(
        encoding="utf-8")
    assert "HasEnergyCostX => true" in verdict


def test_the_swirl_tips_say_what_passes_block():
    tips = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    assert '" unblockable damage to ALL enemies' in tips
    from understudy import blindplay_notes as notes
    assert "unblockable damage to ALL enemies" in notes.ARM_KEYWORDS["Swirl"]
    # The truth the words state: the flat 2 is Unblockable. The current
    # element's payout is ordinary (Unpowered) damage, which Block stops, and
    # like base-game damage says nothing (only the exception is marked).
    pays = (REPO / "klee-mod" / "KleeCode" / "Powers"
            / "ReactionEffects.cs").read_text(encoding="utf-8")
    assert re.search(r"damage,\s*ValueProp\.Unblockable \| ValueProp\.Unpowered",
                     pays)
    hit = (REPO / "klee-mod" / "KleeCode" / "Powers"
           / "ElementalHit.cs").read_text(encoding="utf-8")
    unelemented = hit[hit.index("Task<int> DealUnelemented("):]
    assert "ValueProp.Unpowered," in unelemented[:600]
    assert "Unblockable" not in unelemented[:600]


def test_the_sim_harness_names_only_live_rows(varka):
    from tools import varka_expansion_sim as S
    pool = {c.id for c in loader.prototype_cards()
            if c.id.startswith(V.ID_PREFIX)}
    named = (S.FOCUS + S.GALE + S.SWITCH + S.MUSTER + S.ALL_KNIGHTS
             + [c for cs in S.PAYOFFS.values() for c in cs])
    assert {S.P + c for c in named} <= pool
    assert {"charged_lunge", "short_circuit", "chain_lightning",
            "violet_storm", "thundering_verdict"} <= set(S.PAYOFFS["electro"])
    assert "retaliating_tide" in S.PAYOFFS["hydro"]
