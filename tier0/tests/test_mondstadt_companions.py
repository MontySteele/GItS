"""The Mondstadt companion review (2026-10-03), the sim side.

`review/active/mondstadt-companions-2026-10-03.md`, both picks ruled at their
defaults: Mona's Stellaris Phantasm applies its Vulnerable now for 1 Energy,
Noelle's Breastplate gains 8, Sucrose's Wind Spirit Creation Swirls ALL for 1,
and Amber's Fiery Rain hits for 3 per hit. C# twin:
`klee-mod/KleeTests/Prototype/MondstadtCompanionsTests.cs`.
"""

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.tests.conftest import make_enemy, make_state


def _board(n=2, hp=50):
    return make_state(enemies=[make_enemy(hp=hp, name=f"e{i}") for i in range(n)])


def test_stellaris_phantasm_applies_hydro_and_vulnerable_to_all_now():
    card = loader.get_card("proto_mc_mona_stellaris_phantasm")
    assert card.cost == 1 and card.exhaust is True
    st = _board()
    effects.resolve_card(st, card)
    assert [e.aura for e in st.enemies] == ["hydro", "hydro"]
    assert [e.powers.get("vulnerable", 0) for e in st.enemies] == [3, 3]
    assert "mc_omen" not in st.player.powers
    up = _board()
    effects.resolve_card(up, loader.get_card("proto_mc_mona_stellaris_phantasm+"))
    assert [e.powers.get("vulnerable", 0) for e in up.enemies] == [4, 4]


def test_the_omen_power_and_its_constant_are_gone():
    assert not hasattr(C, "MC_OMEN_VULNERABLE")


def test_breastplate_gains_eight_and_upgrades_to_eleven():
    card = loader.get_card("proto_mc_noelle_breastplate")
    assert card.cost == 1
    st = make_state(hp=80)
    effects.resolve_card(st, card)
    assert st.player.block == 8
    st = make_state(hp=80)
    effects.resolve_card(st, loader.get_card("proto_mc_noelle_breastplate+"))
    assert st.player.block == 11
    st = make_state(hp=80)
    st.player.hp = 20
    effects.resolve_card(st, loader.get_card("proto_mc_noelle_breastplate+"))
    assert st.player.block == 15


def test_wind_spirit_creation_costs_one_and_swirls_all_like_astable():
    gust = loader.get_card("proto_mc_sucrose_gust")
    assert gust.cost == 1 and gust.exhaust is False
    assert [fx for fx in gust.effects if fx["op"] == "swirl"] == [
        {"op": "swirl", "target": "all_enemies"}]
    # The same Swirl Astable Anemohypostasis does, on the same board.
    boards = []
    for cid in ("proto_mc_sucrose_gust", "proto_mc_sucrose_astable"):
        st = _board()
        st.enemies[0].aura = "pyro"
        st.enemies[1].aura = "hydro"
        effects.resolve_card(st, loader.get_card(cid))
        boards.append(([e.aura for e in st.enemies], [e.hp for e in st.enemies]))
    assert boards[0] == boards[1]
    draws = [fx["amount"] for fx in
             loader.get_card("proto_mc_sucrose_gust+").effects
             if fx["op"] == "draw"]
    assert draws == [2]


def test_fiery_rain_deals_three_per_hit_to_all_and_four_upgraded():
    st = _board(n=3)
    effects.resolve_card(st, loader.get_card("proto_mc_amber_fiery_rain"))
    assert [50 - e.hp for e in st.enemies] == [9, 9, 9]
    st = _board(n=3)
    effects.resolve_card(st, loader.get_card("proto_mc_amber_fiery_rain+"))
    assert [50 - e.hp for e in st.enemies] == [12, 12, 12]


# --- sec.4, the Klee-only companions (ruled 2026-10-03) ----------------------

CUT = ("proto_mc_barbara_front_row_seat", "proto_mc_diona_shaken_not_purred",
       "proto_mc_noelle_i_got_your_back", "proto_mc_kaeya_cold_blooded_strike",
       "proto_mc_sayu_silencers_secret", "proto_mc_yaoyao_yuegui_throwing_mode",
       "proto_ko_second_surprise", "proto_ko_solitary_confinement",
       "proto_ko_once_more")
SHARED = ("proto_mc_qiqi_herald_of_frost", "proto_mc_fischl_sinful_hex",
          "proto_mc_sucrose_mollis_favonius", "proto_mc_nicole_ladder_of_ascent")
KLEE_OWN = ("proto_mc_albedo_dust_of_purification", "proto_mc_jean_lions_fang",
            "proto_mc_prune_hexhunter_chime")


def test_the_cut_rows_are_gone_from_the_sheet_and_every_pool():
    on_sheet = {c.id for c in loader.prototype_cards()}
    for cid in CUT:
        assert cid not in on_sheet, cid
        assert cid not in C.KLEE_OVERHAUL_POOL_IDS, cid
        assert cid not in C.MONDSTADT_OVERHAUL_POOL_IDS, cid
    # Kept on [USER]'s word: "it's quite good!"
    assert "proto_ko_kitchen_alchemy" in C.KLEE_OVERHAUL_POOL_IDS


def test_four_rows_join_the_shared_pool_with_no_owner():
    for cid in SHARED:
        card = loader.peek_card(cid)
        assert card.personal_pool is None and card.replaces is None, cid
        assert cid in C.MONDSTADT_OVERHAUL_POOL_IDS, cid
    assert len(C.MONDSTADT_OVERHAUL_POOL_IDS) == 39


def test_three_rows_are_klees_own_draftable_companions():
    assert set(C.KLEE_OWN_COMPANION_IDS) == set(KLEE_OWN)
    for cid in KLEE_OWN:
        card = loader.peek_card(cid)
        assert card.is_companion, cid
        assert card.personal_pool is None and card.replaces is None, cid
        assert cid in C.KLEE_OVERHAUL_POOL_IDS, cid
        assert cid not in C.MONDSTADT_OVERHAUL_POOL_IDS, cid
    from collections import Counter
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    assert Counter(loader.peek_card(i).rarity for i in ids) == {
        "common": 24, "uncommon": 33, "rare": 21}
    assert C.COMPANION_STANDIN_IDS == () and C.COVEN_PERSONAL_POOL_IDS == ()
