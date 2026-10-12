"""THE KOKOMI RE-FOUNDING (2026-10-12), the sim side.

The direction is `review/active/kokomi-design-pass-2026-10-11.md` (all five
picks (a)); the cards are `review/active/kokomi-card-paper-2026-10-12.md`.
The Casket's count, Open the Casket and Dusk are retired; Ethereal is the base
game's keyword; Stings and Wards are her generated jellyfish; any Companion
card can be written as a Plan and is carried out next turn at its printed
rate after the Bake-Kurage applies Hydro to its target.

The C# twins are pinned structurally in
`klee-mod/KleeTests/KokomiRefoundingTests.cs`; these are the behaviours.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import copy

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, kokomi_plan
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards


IDLE = [{"kind": "block", "amount": 5}]        # intends no attack


@pytest.fixture(autouse=True)
def caches():
    def clear():
        from tier0.content import upgrades
        loader.reset_arm_caches()
        rewards.character_pool.cache_clear()
        for fn in (upgrades._upgrade_index,
                   upgrades._prototype_upgrade_index):
            getattr(fn, "cache_clear", lambda: None)()
    clear()
    yield
    clear()


def kokomi_state(n_enemies=1, hp=80):
    enemies = [make_enemy(hp=200, name=f"e{i}", intents=list(IDLE))
               for i in range(n_enemies)]
    st = make_state(enemies=enemies, hp=hp)
    st.player.character_id = "kokomi"
    st.player.element = "hydro"
    st.player.cadence = "catalyst"
    st.in_player_turn = True
    st.player.energy = 10
    return st


def card(cid):
    return copy.deepcopy(loader.get_card(cid))


def write(st, c):
    """Play `c` from her hand onto the Bake-Kurage. No enemy intends to
    attack, so the pilot's aim (`plan_aimed_at_pet`) writes it."""
    st.player.hand.append(c)
    assert kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


def reactions(st):
    return [e["reaction"] for e in st.log if e["event"] == "reaction"]


# --- Ethereal ---------------------------------------------------------------

def test_a_written_ethereal_card_is_not_exhausted_at_the_end_of_the_turn():
    """Base Ethereal exhausts only what is still IN HAND at the end of the
    turn (the decompiled `DoTurnEnd`). A written card left her hand when she
    wrote it, so it goes where a played card goes, and the one she held burns.
    """
    st = kokomi_state()
    written = card("proto_kk_riptide_guard")
    held = card("proto_kk_tidal_surge")
    assert written.is_ethereal and held.is_ethereal
    st.player.draw_pile = [written, held]
    plays = []

    def pilot(state):
        if not plays and written in state.player.hand:
            plays.append(written)
            return written
        return None

    combat._player_turn(st, pilot)
    assert len(st.kk_plan_queue) == 1
    assert not any(c is written for c in st.player.exhaust_pile)
    assert any(c is written for c in st.player.discard_pile)
    assert any(c is held for c in st.player.exhaust_pile)


# --- Stings and Wards -------------------------------------------------------

@pytest.mark.parametrize("cid", [kokomi_plan.STING_ID, kokomi_plan.WARD_ID])
def test_a_jellyfish_card_is_ethereal_costs_1_and_exhausts(cid):
    c = loader.get_card(cid)
    assert c.cost == 1 and c.is_ethereal and c.exhaust
    assert c.rarity == "token" and c.plan


def test_jellyfish_drift_adds_one_sting():
    st = kokomi_state()
    drift = card("proto_kk_jellyfish_drift")
    st.player.hand.append(drift)
    st.enemies[0].intents = [{"kind": "attack", "amount": 5}]
    combat.play_card(st, drift)
    stings = [c for c in st.player.hand if c.id == kokomi_plan.STING_ID]
    assert len(stings) == 1


# --- Companions as Plans ----------------------------------------------------

def carry_out(st):
    st.player.energy = 10
    kokomi_plan.resolve_all(st)


def test_shinobu_thundergrust_written_reacts_electro_charged():
    st = kokomi_state()
    write(st, card("proto_mi_shinobu_thundergrust"))
    assert len(st.kk_plan_queue) == 1
    hp = st.enemies[0].hp
    carry_out(st)
    assert "electrocharged" in reactions(st)
    assert st.enemies[0].hp < hp


def test_a_geo_companion_written_crystallizes():
    """The task named Gorou's Inuzaka; Inuzaka prints its own Plan line since
    the re-founding (Block 11), so the Geo Companion without one is Itto's."""
    st = kokomi_state()
    write(st, card("proto_mi_itto_superlative_superstrength"))
    carry_out(st)
    assert "crystallize" in reactions(st)


def test_gorou_inuzaka_written_carries_out_its_own_plan_line():
    st = kokomi_state()
    write(st, card("proto_mi_gorou_inuzaka"))
    st.player.block = 0
    carry_out(st)
    assert st.player.block == 11
    assert reactions(st) == []


def test_a_block_only_companion_written_leaves_just_the_hydro():
    st = kokomi_state()
    write(st, card("proto_mi_shinobu_grass_ring"))
    st.player.block = 0
    carry_out(st)
    assert st.enemies[0].aura == "hydro"
    assert reactions(st) == []
    assert st.player.block >= 4


def test_the_hydro_lands_before_the_companion_plays():
    st = kokomi_state()
    write(st, card("proto_mi_shinobu_thundergrust"))
    carry_out(st)
    events = [e["event"] for e in st.log]
    assert events.index("plan_companion") < events.index("reaction")


def test_a_written_companions_carry_out_plays_a_copy_that_exhausts():
    st = kokomi_state()
    original = card("proto_mi_shinobu_thundergrust")
    write(st, original)
    assert any(c is original for c in st.player.discard_pile)
    carry_out(st)
    assert any(c.id == original.id for c in st.player.exhaust_pile)
    assert sum(c.id == original.id for c in st.player.discard_pile) == 1


def test_the_carry_out_is_not_a_second_play_of_the_card_in_the_tally():
    st = kokomi_state()
    write(st, card("proto_mi_shinobu_thundergrust"))
    carry_out(st)
    plays = [e for e in st.log if e["event"] == "play"]
    assert len(plays) == 2
    assert [bool(e.get("plan_carry")) for e in plays] == [False, True]


# --- the relic --------------------------------------------------------------

def test_the_casket_gains_3_block_while_a_plan_is_waiting():
    st = kokomi_state()
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    st.player.block = 0
    kokomi_plan.casket_block(st)
    assert st.player.block == 0                 # nothing waiting
    write(st, card("proto_kk_riptide_guard"))
    st.player.block = 0
    kokomi_plan.casket_block(st)
    assert st.player.block == C.KOKOMI_OVERHAUL_CASKET_BLOCK == 3


# --- the new cards ----------------------------------------------------------

def test_grand_design_writes_up_to_3_writable_cards_for_free():
    st = kokomi_state()
    gd = card("proto_kk_grand_design")
    writable = [card("proto_kk_riptide_guard"), card("proto_kk_tidal_surge"),
                card("proto_mi_shinobu_thundergrust"),
                card("proto_kk_undertide_lance")]
    plain = card("proto_kk_evening_watch")
    st.player.hand.extend(writable + [plain])
    st.player.energy = 1
    st.player.hand.append(gd)
    st.enemies[0].intents = [{"kind": "attack", "amount": 5}]
    combat.play_card(st, gd)
    assert st.player.energy == 0                 # Grand Design's own 1
    assert len(st.kk_plan_queue) == 3
    assert any(c is plain for c in st.player.hand)


def test_dawn_tide_soaks_every_enemy_after_the_morning_plans():
    st = kokomi_state(n_enemies=3)
    st.player.powers[kokomi_plan.DAWN_TIDE] = 1
    kokomi_plan.resolve_all(st)
    kokomi_plan.dawn_tide(st)
    assert [e.aura for e in st.enemies] == ["hydro"] * 3


def test_kurage_bloom_and_sangonomiyas_orders_add_cards_at_turn_start():
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_BLOOM] = 1
    st.player.powers[kokomi_plan.SANGONOMIYAS_ORDERS] = 1
    kokomi_plan.turn_start_generators(st)
    ids = [c.id for c in st.player.hand]
    assert ids.count(kokomi_plan.STING_ID) == 1
    companions = [c for c in st.player.hand if c.is_companion]
    assert len(companions) == 1
    assert companions[0].rarity == "common" and companions[0].is_ethereal


def test_the_generators_offer_common_inazuma_and_the_generals_rare():
    st = kokomi_state()
    commons = kokomi_plan.generated_companions(st, "common")
    rares = kokomi_plan.generated_companions(st, "rare")
    assert commons and rares
    assert all(c.nation == "inazuma" for c in commons + rares)
    assert not any(c.id.startswith("proto_mi_gorou_") for c in commons + rares)
    kokomi_plan.call_the_generals(st)
    (got,) = st.player.hand
    assert got.rarity == "rare" and got.is_ethereal and got.exhaust


def test_watatsumi_resistance_hands_a_sting_for_a_written_companion():
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATATSUMI_RESISTANCE] = 1
    write(st, card("proto_mi_shinobu_thundergrust"))
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID]


def test_grand_strategist_answers_a_reaction_a_plan_caused():
    st = kokomi_state(n_enemies=2)
    st.player.powers[kokomi_plan.GRAND_STRATEGIST] = 5
    write(st, card("proto_mi_shinobu_thundergrust"))
    back = st.enemies[1].hp
    carry_out(st)
    assert "electrocharged" in reactions(st)
    assert st.enemies[1].hp <= back - 5


def test_watchful_shoal_pays_block_for_a_written_ethereal_card():
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    st.player.block = 0
    write(st, card("proto_kk_riptide_guard"))
    assert st.player.block == 3


def test_endless_shoal_copies_a_carried_out_sting():
    st = kokomi_state()
    st.player.powers[kokomi_plan.ENDLESS_SHOAL] = 1
    write(st, card(kokomi_plan.STING_ID))
    st.player.hand.clear()
    carry_out(st)
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID]


def test_war_banners_plan_line_is_strength_for_one_turn():
    st = kokomi_state()
    write(st, card("proto_mi_gorou_war_banner"))
    before = st.player.powers.get("strength", 0)
    carry_out(st)
    assert st.player.powers.get("strength", 0) == before + 3


def test_juugas_plan_line_is_6_block_at_the_end_of_3_turns():
    st = kokomi_state()
    write(st, card("proto_mi_gorou_juuga"))
    carry_out(st)
    assert st.player.powers.get("mi_juuga_guard") == 3
    assert not st.player.powers.get("mi_juuga")
    for left in (2, 1, 0):
        st.player.block = 0
        effects.player_turn_end_triggers(st)
        assert st.player.block == C.MI_JUUGA_GUARD_BLOCK == 6
        assert st.player.powers.get("mi_juuga_guard", 0) == left
