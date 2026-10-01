"""THE FURINA RULES PASS (2026-10-01): the sim's pins.

`review/active/furina-rules-pass-2026-10-01.md`, all picks ruled. Sec.2's
four rule changes (rule 8 back-then-forward, rule 5's played-only summon,
rule 4 cut, Wriothesley "always your front performer") and sec.3's ported
rows. Palais Ledger, Center of Attention and The Curtain Never Falls are
game-side only and pinned in C# alone; the C# twin is
`klee-mod/KleeTests/Prototype/FurinaRulesPassTests.cs`. Readings: the
provenance note, "Furina rules pass, 2026-10-01". NOTHING MEASURED HERE IS
QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader, upgrades
from tier0.engine import combat, effects, furina_stage
from tier0.engine.state import Card, CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _proto(cid):
    return next(c for c in loader.prototype_cards() if c.id == cid)


def _state(stage=(), hp=500, deck=0):
    st = CombatState(player=Player(hp=200, max_hp=200, fanfare_cap=99,
                                   character_id="furina"),
                     enemies=[Enemy(hp=hp, max_hp=hp, name="paper",
                                    intents=[{"kind": "block",
                                              "amount": 0}])],
                     rng=random.Random(0))
    st.turn = 2
    st.player.stage = [list(pair) for pair in stage]
    st.player.draw_pile = [Card(id=f"filler{i}", name="f", cost=0,
                                type="skill") for i in range(deck)]
    return st


def _play(st, card, energy=10):
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)


# ---------------------------------------------------------------------------
# Sec.2, rule 8: back first, then forward.
# ---------------------------------------------------------------------------

def test_a_spend_the_back_cannot_cover_is_paid_forward_and_bows_back_first(arm):
    st = _state([["usher", 4], ["chevalmarin", 2], ["crabaletta", 1]])
    assert FS.can_pay(st.player, 7)
    assert not FS.can_pay(st.player, 8)
    assert FS.spend(st, 5) == 5
    assert st.player.stage == [["usher", 2]]
    bows = [e["member"] for e in st.log if e["event"] == "stage_bow"]
    assert bows == ["crabaletta", "chevalmarin"]


def test_a_spend_the_back_covers_touches_nobody_else(arm):
    st = _state([["usher", 4], ["crabaletta", 6]])
    assert FS.spend(st, 3) == 3
    assert st.player.stage == [["usher", 4], ["crabaletta", 3]]


# ---------------------------------------------------------------------------
# Sec.2, rule 5: only what you play summons.
# ---------------------------------------------------------------------------

def test_a_played_card_that_gives_fanfare_summons_on_an_empty_stage(arm):
    st = _state()
    effects.resolve_card(st, _proto("proto_fs_warm_reception"))
    assert len(st.player.stage) == 1 and st.player.stage[0][1] == 3


@pytest.mark.parametrize("source", [FS.GAIN_BOW, FS.GAIN_POWER])
def test_a_triggered_gain_does_nothing_on_an_empty_stage(arm, source):
    st = _state()
    assert FS.raise_fanfare(st, 3, source=source) == 0
    assert st.player.stage == []


def test_each_performer_has_nobody_to_land_on(arm):
    """Grand Deluge's "each performer gains 2" on an empty stage."""
    st = _state()
    assert FS.raise_fanfare(st, 2, FS.SEAT_ALL) == 0
    assert st.player.stage == []


def test_a_reaction_trigger_does_nothing_on_an_empty_stage(arm):
    st = _state()
    st.player.powers[FS.TIDE_OF_APPLAUSE] = 2
    FS.note_reaction(st)
    assert st.player.stage == []
    st.player.stage = [["usher", 1]]
    FS.note_reaction(st)
    assert st.player.stage == [["usher", 3]]


# ---------------------------------------------------------------------------
# Sec.2, rule 4 cut.
# ---------------------------------------------------------------------------

def test_the_front_regains_nothing_at_turn_start(arm):
    st = _state([["usher", 3]])
    for turn in (2, 3, 4):
        st.turn = turn
        FS.turn_start_regen(st)
    assert st.player.stage == [["usher", 3]]


# ---------------------------------------------------------------------------
# Sec.2, Wriothesley: always your front performer.
# ---------------------------------------------------------------------------

def test_wriothesley_on_a_full_stage_bows_the_front_and_takes_it(arm):
    st = _state([["usher", 2], ["chevalmarin", 3], ["crabaletta", 4]])
    FS.guest_star(st, "wriothesley", 5, front=True)
    assert st.player.stage == [["wriothesley", 7], ["chevalmarin", 3],
                               ["crabaletta", 4]]


def test_a_summon_around_him_bows_the_one_behind_him(arm):
    st = _state([["wriothesley", 5], ["usher", 2], ["crabaletta", 4]])
    FS.recast_front(st, "chevalmarin")
    assert st.player.stage[0] == ["wriothesley", 5]
    assert [m for m, _f in st.player.stage] == ["wriothesley", "crabaletta",
                                                "chevalmarin"]


# ---------------------------------------------------------------------------
# Sec.3, the ported rows.
# ---------------------------------------------------------------------------

def test_singer_of_many_waters_feeds_the_front(arm, monkeypatch):
    st = _state([["usher", 2], ["crabaletta", 1]])
    effects.resolve_card(st, _proto("proto_fs_singer_of_many_waters"))
    assert st.player.stage == [["usher", 8], ["crabaletta", 1]]
    # The delta index is cached at the flag's value, so it is handed the
    # row's own `upgrade:` block (`test_the_batch_two_upgrades_bind`'s way).
    import copy
    import yaml
    rows = yaml.safe_load((loader.DOCS_DIR / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    row = next(r for r in rows if r["id"] == "proto_fs_singer_of_many_waters")
    monkeypatch.setattr(upgrades, "_upgrade_index", lambda: {
        row["id"]: dict(row["upgrade"])})
    up = upgrades.apply_upgrade(
        copy.deepcopy(_proto("proto_fs_singer_of_many_waters")))
    assert up.effects[0]["amount"] == 9
    assert up.exhaust


def test_opening_number_feeds_the_back_only_as_the_turns_first_card(arm):
    st = _state([["usher", 2], ["crabaletta", 1]])
    _play(st, _proto("proto_fs_opening_number"))
    assert st.enemies[0].hp == 500 - 9
    assert st.player.stage[-1] == ["crabaletta", 3]
    _play(st, _proto("proto_fs_opening_number"))
    assert st.enemies[0].hp == 500 - 18
    assert st.player.stage[-1] == ["crabaletta", 3]


def test_leading_lady_reads_the_front(arm):
    st = _state([["usher", 7], ["crabaletta", 1]])
    effects.resolve_card(st, _proto("proto_fs_leading_lady"))
    assert st.enemies[0].hp == 500 - (6 + 7)


def test_endless_waltz_acts_only_the_performers_at_five_or_more(arm):
    st = _state([["usher", 5], ["crabaletta", 4], ["chevalmarin", 6]])
    effects.resolve_card(st, _proto("proto_fs_endless_waltz"))
    acted = [e["member"] for e in st.log if e["event"] == "stage_act"]
    assert acted == ["usher", "chevalmarin"]
    # 14 to ALL, then Chevalmarin's 2 to ALL; Usher's act is Block.
    assert st.enemies[0].hp == 500 - 14 - FS.ACT_CHEVALMARIN_DAMAGE
    assert st.player.block == FS.ACT_USHER_BLOCK


def test_the_twelve_are_offered_and_the_pool_stays_seventy_eight(arm):
    from tier05 import rewards
    ported = {
        "proto_fs_singer_of_many_waters", "proto_fs_opening_number",
        "proto_fs_leading_lady", "proto_fs_endless_waltz",
        "proto_fs_commanding_gaze", "proto_fs_undercurrent",
        "proto_fs_warmup_act", "proto_fs_courtroom_drama",
        "proto_fs_crashing_waves", "proto_fs_duet", "proto_fs_quick_change",
        "proto_fs_witness_stand"}
    assert ported <= set(FS.POOL_SUBS.values()) | set(FS.POOL_ADDS)
    rows = {r.id: r for r in loader.prototype_cards()}
    assert sorted(rows[c].rarity for c in ported).count("common") == 4
    assert sorted(rows[c].rarity for c in ported).count("rare") == 2
    rewards.character_pool.cache_clear()
    try:
        offered = {c.id for cs in rewards.character_pool("furina").values()
                   for c in cs}
    finally:
        rewards.character_pool.cache_clear()
    assert ported <= offered
    assert not offered & {"an_invitation", "guest_list",
                          "command_performance", "singer_of_many_waters",
                          "warmup_act"}
