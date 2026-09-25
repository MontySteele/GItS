"""THE CO-OP SET in the one-seat sim (review/records/coop-set-2026-09-25.md).

Nine multiplayer-only cards, three per overhaul arm. Tier 0 seats ONE player
(`tier0/engine/coop.py`), so the co-op rules themselves are tested in C#
(`klee-mod/KleeTests/Prototype/CoopSetTests.cs`). What is pinned here is the
sim's half of the contract:

  * the rows LOAD through the same checks every row takes, and the
    multiplayer rules are enforced at load exactly as the emitter enforces
    them;
  * no sim pool DEALS one -- they sit outside every pool list, the way the
    base game's `GetUnlockedCards` keeps them out of a one-player run;
  * resolved anyway, what a card does for its own player happens and what it
    does for another player lands on no one.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from pathlib import Path

import pytest
import yaml

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import coop, effects, kokomi_plan
from tier0.tests.conftest import make_state
from tools import gen_klee_cards as gen
from tier05 import rewards

TIERS = (C.KLEE_OVERHAUL_MULTIPLAYER_IDS + C.FURINA_STAGE_MULTIPLAYER_IDS
         + C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS)


def _row(cid):
    return next(c for c in loader.prototype_cards() if c.id == cid)


@pytest.fixture
def arms(monkeypatch):
    """All three overhaul arms on, with the flag-keyed caches cleared."""
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    from tier0.engine import furina_stage
    monkeypatch.setattr(furina_stage, "FURINA_STAGE", True)
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


# ---- the rows ---------------------------------------------------------------

def test_the_nine_load_and_are_the_three_tiers():
    assert len(TIERS) == 9
    assert loader.multiplayer_ids() == frozenset(TIERS)
    ids = {c.id for c in loader.prototype_cards()}
    assert set(TIERS) <= ids


def test_two_uncommons_and_one_rare_per_character():
    for tier in (C.KLEE_OVERHAUL_MULTIPLAYER_IDS,
                 C.FURINA_STAGE_MULTIPLAYER_IDS,
                 C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS):
        assert sorted(_row(cid).rarity for cid in tier) == [
            "rare", "uncommon", "uncommon"]


def test_the_multiplayer_tier_is_outside_every_pool_count():
    for pool in (C.KLEE_OVERHAUL_POOL_IDS, C.KOKOMI_OVERHAUL_POOL_IDS):
        assert not set(pool) & set(TIERS)
    # The counts R276 ruled do not move.
    assert len(C.KLEE_OVERHAUL_POOL_IDS) == 78
    assert len(C.KOKOMI_OVERHAUL_POOL_IDS) == 39


def test_no_sim_pool_deals_one(arms):
    """The single-player guard, sim side: the one door every offer surface
    reads (`rewards.character_pool`) holds none of them under any arm."""
    for character in ("klee", "furina", "kokomi"):
        pool = rewards.character_pool(character)
        offered = {c.id for cards in pool.values() for c in cards} \
            if isinstance(pool, dict) else {getattr(c, "id", c) for c in pool}
        assert not offered & set(TIERS), character


# ---- the load-time rules (the emitter's twins) -------------------------------

def _sheet(tmp_path, row):
    path = tmp_path / "surface.yaml"
    path.write_text(yaml.safe_dump([row]), encoding="utf-8")
    return path


BASE = {"id": "proto_ko_probe", "name": "Probe", "character": "klee",
        "authored_by": ["claude"], "cost": 1, "type": "skill",
        "rarity": "uncommon"}


def _card(row):
    """The row as the emitter sees it: provenance off."""
    return {k: v for k, v in row.items() if k != "authored_by"}


def test_an_ally_aimed_row_must_be_multiplayer(tmp_path):
    row = dict(BASE, effects=[{"op": "block", "amount": 6, "target": "ally"}])
    with pytest.raises(ValueError, match="another player"):
        loader.prototype_cards(_sheet(tmp_path, row))
    assert "must be `multiplayer: true`" in gen.blocked_reason(
        _card(row), gen.KLEE_PROFILE)
    ok = dict(row, multiplayer=True)
    assert [c.id for c in loader.prototype_cards(_sheet(tmp_path, ok))] == [
        "proto_ko_probe"]


def test_multiplayer_is_a_ruling_and_an_arms(tmp_path):
    fx = [{"op": "draw", "amount": 1}]
    with pytest.raises(ValueError, match="must be true"):
        loader.prototype_cards(_sheet(tmp_path, dict(
            BASE, effects=fx, multiplayer=False)))
    outside = dict(BASE, id="proto_mc_probe", effects=fx, multiplayer=True)
    with pytest.raises(ValueError, match="outside the three overhaul arms"):
        loader.prototype_cards(_sheet(tmp_path, outside))
    assert "only an overhaul arm" in gen.card_level_reason(_card(outside))


def test_only_the_co_op_verbs_may_aim_at_another_player():
    row = dict(BASE, multiplayer=True,
               effects=[{"op": "draw", "amount": 1, "target": "ally"}])
    assert "cannot aim at another player" in gen.blocked_reason(
        _card(row), gen.KLEE_PROFILE)


# ---- resolved in a one-seat fight -------------------------------------------

def _klee():
    st = make_state()
    st.player.character_id = "klee"
    st.in_player_turn = True
    _stock(st)
    return st


def _stock(st):
    """Something to draw, so a draw that happens is seen."""
    st.player.draw_pile = [loader.get_card("strike") for _ in range(5)]


def test_pass_the_match_still_draws_and_places_nothing(arms):
    st = _klee()
    before = len(st.player.hand)
    effects.resolve_card(st, _row("proto_ko_pass_the_match"))
    assert len(st.player.hand) == before + 1
    assert not st.player.powers.get("ko_pass_the_match")
    assert any(e["event"] == "coop_no_other_player" for e in st.log)


def test_hide_here_gives_klee_nothing(arms):
    st = _klee()
    effects.resolve_card(st, _row("proto_ko_hide_here"))
    assert st.player.block == 0
    assert any(e["event"] == "coop_no_other_player"
               and e["op"] == "block_largest_bomb" for e in st.log)


def test_joint_orders_now_line_and_plan_land_on_no_one(arms):
    st = make_state()
    st.player.character_id = "kokomi"
    st.in_player_turn = True
    effects.resolve_card(st, _row("proto_kk_joint_orders"))
    assert st.player.block == 0
    card = _row("proto_kk_joint_orders")
    _stock(st)
    kokomi_plan.schedule(st, card)
    hand = len(st.player.hand)
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == hand
    assert any(e["event"] == "coop_no_other_player"
               and e["op"] == coop.ALLY_DRAW for e in st.log)


def test_coordinated_strike_hits_and_its_plan_lands_on_no_one(arms):
    st = make_state()
    st.player.character_id = "kokomi"
    st.player.element = "hydro"
    st.player.cadence = "catalyst"
    st.in_player_turn = True
    hp = st.enemies[0].hp
    effects.resolve_card(st, _row("proto_kk_coordinated_strike"))
    assert st.enemies[0].hp == hp - 6
    kokomi_plan.schedule(st, _row("proto_kk_coordinated_strike"))
    kokomi_plan.resolve_all(st)
    assert not st.player.powers.get("attack_up_this_turn")
    assert any(e["event"] == "coop_no_other_player"
               and e["op"] == coop.OTHERS_ATTACK_DAMAGE_THIS_TURN
               for e in st.log)


def test_share_the_spotlight_moves_no_bar(arms):
    from tier0.engine import furina_stage as FS
    st = make_state()
    st.player.character_id = "furina"
    st.in_player_turn = True
    FS.open_combat(st)
    stage = [list(s) for s in FS.stage(st.player)]
    effects.resolve_card(st, _row("proto_fs_share_the_spotlight"))
    assert [list(s) for s in FS.stage(st.player)] == stage
    assert st.player.block == 0


def test_the_three_powers_apply_and_never_fire(arms):
    """Each sits on its owner and watches OTHER players; a one-seat fight
    never gives one anything to hear."""
    for cid, power in (("proto_ko_knights_of_favonius", "ko_knights_of_favonius"),
                       ("proto_fs_people_of_fontaine", "fs_people_of_fontaine"),
                       ("proto_kk_sangonomiyas_counsel", "kk_sangonomiyas_counsel")):
        st = make_state()
        effects.resolve_card(st, _row(cid))
        assert st.player.powers.get(power), cid


def test_every_op_the_nine_print_is_registered():
    for cid in TIERS:
        row = _row(cid)
        for fx in list(row.effects) + list(row.plan or []):
            assert fx["op"] in effects.OPS, (cid, fx["op"])


def test_the_sheet_marks_all_nine_and_nothing_else():
    raw = yaml.safe_load(
        (Path(loader.PROTOTYPE_SHEET)).read_text(encoding="utf-8"))
    marked = [d["id"] for d in raw if d.get("multiplayer")]
    assert marked == list(TIERS)
