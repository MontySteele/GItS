"""THE KOKOMI RE-FOUNDING (2026-10-12), the sim side.

The direction is `review/ruled/kokomi-design-pass-2026-10-11.md` (all five
picks (a)); the cards are `review/ruled/kokomi-card-paper-2026-10-12.md`.
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
    written = card("proto_kk_steady_tide")
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
def test_a_jellyfish_card_is_ethereal_costs_0_and_exhausts(cid):
    """Cost 0 since the jellyfish build (2026-10-12); still a Plan line."""
    c = loader.get_card(cid)
    assert c.cost == 0 and c.is_ethereal and c.exhaust
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


def test_a_companion_with_no_plan_line_cannot_be_planned():
    """Kokomi review r9 pick 1 (a), 2026-10-15; [USER]: "let's get rid of
    Companions as Plans unless we make a card that specifically has a Plan
    line." Shinobu prints none: the jellyfish refuses it, so it plays at the
    enemy as printed and nothing is queued."""
    st = kokomi_state()
    c = card("proto_mi_shinobu_thundergrust")
    assert c.is_companion and not c.plan
    assert not kokomi_plan.can_be_written(c)
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    hp = st.enemies[0].hp
    combat.play_card(st, c)
    assert st.kk_plan_queue == []
    assert st.enemies[0].hp < hp
    assert not any(e["event"] == "plan_written" for e in st.log)


def test_gorou_inuzaka_written_carries_out_its_own_plan_line():
    st = kokomi_state()
    write(st, card("proto_mi_gorou_inuzaka"))
    st.player.block = 0
    carry_out(st)
    assert st.player.block == 11
    assert reactions(st) == []


# --- the relic --------------------------------------------------------------

def _casket(st):
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    st.player.block = 0


@pytest.mark.parametrize("cid", [
    "proto_kk_steady_tide",              # a Plan card
    "proto_mi_shinobu_thundergrust",     # a Companion with no Plan line
    "proto_mi_gorou_inuzaka",            # both: pays once
    kokomi_plan.STING_ID,
    kokomi_plan.WARD_ID,
])
def test_the_casket_pays_1_for_a_plan_card_or_companion_played(cid):
    """Ward and Casket (2026-10-18, [USER]: "if we allow for Sting and Ward
    to count, is that a real problem? ... (possibly bringing it down to 1 per
    card played)"): "Whenever you play a Plan card or a Companion, gain 1
    Block." Played face-up."""
    st = kokomi_state()
    st.enemies[0].intents = [{"kind": "attack", "amount": 5}]
    _casket(st)
    c = card(cid)
    st.player.hand.append(c)
    combat.play_card(st, c)
    gained = sum(e["amount"] for e in st.log if e["event"] == "casket_block")
    assert gained == C.KOKOMI_OVERHAUL_CASKET_BLOCK == 1


@pytest.mark.parametrize("cid", ["proto_kk_steady_tide", kokomi_plan.WARD_ID])
def test_the_casket_pays_for_a_card_planned_and_not_for_its_carry_out(cid):
    st = kokomi_state()
    _casket(st)
    write(st, card(cid))
    assert st.player.block == 1
    st.player.block = 0
    st.log.clear()
    carry_out(st)
    assert not any(e["event"] == "casket_block" for e in st.log)


@pytest.mark.parametrize("cid", ["strike", "defend"])
def test_the_casket_pays_nothing_for_a_strike_or_defend(cid):
    st = kokomi_state()
    st.enemies[0].intents = [{"kind": "attack", "amount": 5}]
    _casket(st)
    c = card(cid)
    st.player.hand.append(c)
    combat.play_card(st, c)
    assert not any(e["event"] == "casket_block" for e in st.log)


def test_the_casket_left_the_start_of_the_turn():
    """The start-of-turn Block (2026-10-12) is gone: the twin pays per play,
    from `effects.resolve_card`."""
    import inspect
    assert "kokomi_plan.casket_block(state" not in inspect.getsource(
        combat._player_turn)
    assert "kokomi_plan.casket_block(state, card)" in inspect.getsource(
        effects.resolve_card)


# --- the new cards ----------------------------------------------------------

def test_grand_design_writes_up_to_3_writable_cards_for_free():
    st = kokomi_state()
    gd = card("proto_kk_grand_design")
    writable = [card("proto_kk_steady_tide"), card("proto_kk_tidal_surge"),
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
    """A Companion that prints a Plan line (Gorou's) is the only one written
    since Kokomi review r9 pick 1 (a)."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATATSUMI_RESISTANCE] = 1
    write(st, card("proto_mi_gorou_inuzaka"))
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID]


def test_grand_strategist_answers_a_reaction_a_plan_caused():
    st = kokomi_state(n_enemies=2)
    st.player.powers[kokomi_plan.GRAND_STRATEGIST] = 5
    for enemy in st.enemies:
        enemy.aura = "electro"
    write(st, card("proto_kk_kurages_oath"))
    back = st.enemies[1].hp
    carry_out(st)
    assert "electrocharged" in reactions(st)
    assert st.enemies[1].hp <= back - 5


def test_watchful_shoal_pays_nothing_for_writing_an_ethereal_card():
    """Kokomi round-3 changes (2026-10-12): Watchful Shoal is the jellyfish's
    Accuracy now (`test_kokomi_round3_changes_2026_10_12`); writing pays
    nothing."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    st.player.block = 0
    write(st, card("proto_kk_steady_tide"))
    assert st.player.block == 0


def test_endless_shoal_adds_a_sting_for_any_carried_out_plan():
    """The jellyfish build (2026-10-12): "Whenever the Bake-Kurage carries
    out a Plan, add a Sting to your hand." Any Plan, not only a Sting."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.ENDLESS_SHOAL] = 1
    write(st, card("proto_kk_brine_sting"))
    st.player.hand.clear()
    carry_out(st)
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID]


def test_war_banners_plan_line_is_permanent_strength():
    """The Kokomi level pass (2026-10-12): "Plan: Gain 1 [2] Strength", for
    good -- no temporary Strength left to take back."""
    st = kokomi_state()
    write(st, card("proto_mi_gorou_war_banner"))
    before = st.player.powers.get("strength", 0)
    carry_out(st)
    assert st.player.powers.get("strength", 0) == before + 1
    assert not st.player.powers.get("temp_strength")


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


def test_the_jellyfish_are_the_only_0_cost_plan_rows():
    """Card paper rule 2 ("No card with a Plan line costs 0") was LIFTED by
    the jellyfish ruling (2026-10-12, [USER]: "I'm actually totally fine with
    0-cost plans"); the rule that stands is that no Plan happens within her
    own turn. Today only the two jellyfish tokens are 0-cost Plan rows, so a
    new one is a deliberate change of this pin, not an accident. Crystal
    Collapse+ keeps cost 1 and gains Retain (2026-10-12)."""
    from pathlib import Path

    import yaml
    from tier0.content import upgrades

    sheet = Path(__file__).resolve().parents[2] / "docs" / "prototype-surface.yaml"
    rows = yaml.safe_load(sheet.read_text(encoding="utf-8"))
    plan_rows = [r for r in rows if r.get("plan")]
    assert "proto_mi_gorou_crystal_collapse" in {r["id"] for r in plan_rows}
    for row in plan_rows:
        delta = row.get("upgrade") or ({} if row.get("no_upgrade") else
                                       upgrades.prototype_default_delta(
                                           row["id"], row.get("cost"),
                                           row.get("effects", []),
                                           bool(row.get("exhaust")),
                                           row["plan"]))
        if row["id"] in (kokomi_plan.STING_ID, kokomi_plan.WARD_ID):
            assert row["cost"] == 0 and "cost" not in delta, row["id"]
            continue
        assert row["cost"] >= 1, row["id"]
        assert row["cost"] + delta.get("cost", 0) >= 1, row["id"]
    up = upgrades.apply_upgrade(card("proto_mi_gorou_crystal_collapse"))
    assert up.cost == 1 and up.retain
