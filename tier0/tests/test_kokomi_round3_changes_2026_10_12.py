"""Kokomi round-3 changes (2026-10-12), the sim side.

From the Fable round-2 review and the round record
`review/records/kokomi-round-2-2026-10-12.md`; provenance note "Kokomi
round-3 changes, 2026-10-12". The C# twins are
`klee-mod/KleeTests/Prototype/KokomiRound3ChangesTests.cs` (the Plan face's
Vulnerable fold and Coordinated Tide's results line are C#-only: the sim
prints no face and no page). NOTHING MEASURED HERE IS QUOTABLE (R215 B):
shape assertions about an engine.
"""

from tier0.content import loader, upgrades
from tier0.engine import combat, kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)
from tier0.tests.test_arm_keyword_tips import proto


def _rows():
    return {r["id"]: r for r in proto._rows()}


def _attacking(st):
    """Every enemy intends an attack, so the pilot plays a card face-up."""
    for e in st.enemies:
        e.intents = [{"kind": "attack", "amount": 5}]


def _play(st, c):
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


# --- Tide Wall: the largest intent ------------------------------------------

def test_tide_wall_reads_the_biggest_intent_not_the_front_one():
    """The Queen's shape: the front body intends nothing and the one behind
    it attacks. The Plan used to read 0."""
    st = kokomi_state(n_enemies=2)
    write(st, card("proto_kk_tide_wall"))
    st.enemies[1].intents = [{"kind": "attack", "amount": 9, "times": 2}]
    assert kokomi_plan.intent_damage(st, st.enemies[0]) == 0
    assert kokomi_plan.max_intent_damage(st) == 18
    st.player.block = 0
    carry_out(st)
    assert st.player.block == 6 + 18
    # Reworded in the Kokomi review (2026-10-13) and the Kokomi upgrade
    # pass (2026-10-19, finish round item 3).
    assert _rows()["proto_kk_tide_wall"]["description"].endswith(
        "plus the biggest attack an enemy intends when this is carried out.")


def test_no_enemies_intend_nothing():
    st = kokomi_state()
    st.enemies.clear()
    assert kokomi_plan.max_intent_damage(st) == 0


# --- Treatise: the face ------------------------------------------------------

def test_treatise_face_says_writing_does_not_count():
    # The card text pass (2026-10-12): "plan" is her one verb. The Kokomi
    # review (2026-10-13): the face names the two kinds of card that count.
    assert _rows()["proto_kk_treatise"]["description"] == (
        "The first time each turn you play a [gold]Plan[/gold] card or a "
        "[gold]Companion[/gold] without planning it, draw 1 card.")


# --- Kelp Wall: the now-line -------------------------------------------------

def test_kelp_wall_now_line_blocks_and_draws():
    row = loader.get_card("proto_kk_kelp_wall")
    # Numbers pass (kokomi-review-r5-2026-10-14): 5 -> 7 [9].
    assert row.effects[0] == {"op": "block", "amount": 7}
    assert row.effects[1] == {"op": "draw", "amount": 1}
    up = upgrades.apply_upgrade(loader.get_card("proto_kk_kelp_wall"))
    assert up.effects[0]["amount"] == 9
    # The pool overhaul (2026-10-13): the Plan is a Counter line; the Kokomi
    # upgrade pass (2026-10-19) adds +4 on the upgraded card.
    assert up.plan == [{"op": "damage_blocked_since", "amount": 4,
                        "target": "front_enemy"}]
    st = kokomi_state()
    _attacking(st)
    st.player.draw_pile = [card("proto_kk_evening_watch")]
    st.player.block = 0
    _play(st, card("proto_kk_kelp_wall"))
    assert st.player.block == 7
    assert [c.id for c in st.player.hand] == ["proto_kk_evening_watch"]


# --- Watchful Shoal: the jellyfish's Accuracy --------------------------------

def test_watchful_shoal_numbers_and_face():
    row = loader.get_card("proto_kk_watchful_shoal")
    up = upgrades.apply_upgrade(loader.get_card("proto_kk_watchful_shoal"))
    assert (row.effects[0]["amount"], up.effects[0]["amount"]) == (4, 6)   # Kokomi review r6 item 3
    assert _rows()["proto_kk_watchful_shoal"]["description"] == (
        "Your [gold]Stings[/gold] deal {PowerAmount:diff()} additional "
        "damage.")   # its Ward half left with the Ward's Block, 2026-10-18


def test_a_played_sting_deals_3_more():
    st = kokomi_state()
    _attacking(st)
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    st.enemies[0].powers["vulnerable"] = 0
    hp = st.enemies[0].hp
    _play(st, card(kokomi_plan.STING_ID))
    # The Sting's 4 since the jellyfish build (2026-10-12).
    assert hp - st.enemies[0].hp == 4 + 3


def test_an_upgraded_sting_counts_and_brine_sting_does_not():
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    sting = upgrades.apply_upgrade(loader.get_card(kokomi_plan.STING_ID))
    assert kokomi_plan.watchful_shoal_bonus(
        st, sting, kokomi_plan.STING_ID) == 3
    assert kokomi_plan.watchful_shoal_bonus(
        st, card("proto_kk_brine_sting"), kokomi_plan.STING_ID) == 0


def test_a_written_sting_carries_the_bonus_to_every_enemy():
    st = kokomi_state(n_enemies=2)
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    write(st, card(kokomi_plan.STING_ID))
    (entry,) = st.kk_plan_queue
    assert entry.clauses[0]["amount"] == 3 + 3
    before = [e.hp for e in st.enemies]
    carry_out(st)
    lost = [b - e.hp for b, e in zip(before, st.enemies)]
    assert all(x >= 6 for x in lost), lost


def test_a_played_ward_gains_no_block_from_the_shoal():
    """Ward and Casket (2026-10-18): a Ward draws, and Watchful Shoal no
    longer touches it."""
    st = kokomi_state()
    _attacking(st)
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    st.player.block = 0
    _play(st, card(kokomi_plan.WARD_ID))
    assert st.player.block == 0
    assert kokomi_plan.watchful_shoal_bonus(
        st, card(kokomi_plan.WARD_ID), kokomi_plan.STING_ID) == 0


def test_other_cards_get_nothing():
    st = kokomi_state()
    _attacking(st)
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    st.player.block = 0
    _play(st, card("proto_kk_coral_bulwark"))
    assert st.player.block == 8


def test_a_flipped_ward_carries_out_its_now_line_and_gains_no_block():
    st = kokomi_state()
    st.player.powers[kokomi_plan.WATCHFUL_SHOAL] = 3
    write(st, card(kokomi_plan.WARD_ID))
    assert kokomi_plan.flip(st, 0)
    st.player.block = 0
    carry_out(st)
    assert st.player.block == 0


# --- Coordinated Tide: before the plan bus -----------------------------------

def test_coordinated_tide_lands_before_the_plan_bus():
    """The pool overhaul (2026-10-13): Coordinated Tide no longer hits on a
    carry-out (it adds a Sting when a Companion's own hit reacts), so a
    written Plan carried out pays it nothing; the plan bus still pays (on a
    Plan that is not a Sting or Ward since the Kokomi card paper v2)."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.COORDINATED_TIDE] = 1
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 3
    write(st, card("proto_kk_brine_sting"))
    carry_out(st)
    events = [e["event"] for e in st.log]
    assert "plan_coordinated_tide" not in events
    assert "plan_kurage_canopy" in events


def test_the_page_prints_the_tide_rider_the_bridge_now_sends():
    """`KokomiPlan.ResolveEntry` names Coordinated Tide as a rider on the
    carry-out row; the blind page prints riders after the Plan's line."""
    from understudy import blindplay_render
    said = {"riders": [{"source": "Coordinated Tide", "amount": 6,
                        "target": "Queen", "combat_id": "2"}]}
    assert blindplay_render._rider_clause(said) == (
        " Inside the same beat: Coordinated Tide 6 on Queen.")
