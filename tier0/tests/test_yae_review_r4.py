"""Yae review r4, items 1 to 8 (build 0.2.5561 round). Sim half; the C# half
is `klee-mod/KleeTests/Prototype/YaeReviewR4Tests.cs`."""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy
from understudy import blindplay


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _state():
    enemies = [Enemy(hp=100, max_hp=100, name="e0",
                     intents=[{"kind": "block", "amount": 0}])]
    p = Y.build_player()
    p.draw_pile = []
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card):
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _row(card_id):
    import yaml
    from pathlib import Path
    sheet = Path(__file__).resolve().parents[2] / "docs" / "prototype-surface.yaml"
    rows = yaml.safe_load(sheet.read_text(encoding="utf-8"))
    rows = rows["cards"] if isinstance(rows, dict) else rows
    return next(r for r in rows if r["id"] == card_id)


def _block(card):
    return next(e["amount"] for e in card.effects if e["op"] == "block")


def _events(st, name):
    return [e for e in st.log if e.get("event") == name]


# 2. Red Ink on a planting card into a full shrine ---------------------------

def test_refreshed_sakura_gets_the_planting_cards_red_ink():
    st = _state()
    for _ in range(Y.SAKURA_CAP):
        Y.plant(st, 1)
    oldest = Y.ledger(st.player).sakura[0]
    assert oldest.annotation is None
    Y.plant(st, 1, annotation=Y.RED_INK)          # same kind: refresh
    assert len(Y.ledger(st.player).sakura) == Y.SAKURA_CAP
    assert oldest.annotation == Y.RED_INK
    assert oldest.level == 2


def test_a_plant_with_no_red_ink_leaves_a_refreshed_annotation_alone():
    st = _state()
    for _ in range(Y.SAKURA_CAP):
        Y.plant(st, 1)
    oldest = Y.ledger(st.player).sakura[0]
    oldest.annotation = Y.FOX_FIRE
    Y.plant(st, 1)
    assert oldest.annotation == Y.FOX_FIRE


# 3, 4. Deadline and Evergreen Charm -----------------------------------------

def test_deadline_is_8_and_11_upgraded():
    assert _block(_card("deadline")) == 8
    assert _block(loader.get_card("proto_ym_deadline+")) == 11
    assert "Gain 8 " in _row("proto_ym_deadline")["description"]


def test_evergreen_charm_is_7_and_10_and_keeps_red_ink():
    c = _card("evergreen_charm")
    assert _block(c) == 7
    assert "It keeps its Red Ink." in _row("proto_ym_evergreen_charm")["description"]
    assert _block(loader.get_card("proto_ym_evergreen_charm+")) == 10
    st = _state()
    Y.plant(st, 1)
    s = Y.ledger(st.player).sakura[0]
    s.annotation = Y.RED_INK
    plain = Y.act_size(st, s)
    _play(st, c)
    assert s.annotation == Y.DEADLINE and s.red_ink_kept
    assert Y.act_size(st, s) == plain                # the +3 stays
    # An Edit that does not keep it drops it.
    Y.edit_sakura(st, "oldest", 1, Y.FOX_FIRE)
    assert not s.red_ink_kept


def test_evergreen_charm_on_a_sakura_without_red_ink_keeps_nothing():
    st = _state()
    Y.plant(st, 1)
    s = Y.ledger(st.player).sakura[0]
    _play(st, _card("evergreen_charm"))
    assert s.annotation == Y.DEADLINE and not s.red_ink_kept


# 5. The Seven Glamours ------------------------------------------------------

# 2026-10-15 ([USER]: "it looks obviously OP - I thought it was Publishing one
# card per fight, not the whole hand"): a 2-cost Attack, 12 [16], Exhaust,
# that Publishes ONE Annotated card in hand, and only on a kill (Hand of
# Greed's Fatal check: a Minion's death does not count).

def _glamours_state(n=2):
    st = _state()
    st.enemies = [Enemy(hp=100, max_hp=100, name=f"e{i}",
                        intents=[{"kind": "block", "amount": 0}])
                  for i in range(n)]
    a, b, plain = _card("sly_strike"), _card("sly_strike"), _card("sly_strike")
    for x in (a, b, plain):
        st.player.hand.append(x)
    Y.annotate(st, a, Y.RED_INK)
    Y.annotate(st, b, Y.FOOTNOTE)
    return st, a, b, plain


def test_seven_glamours_row():
    c = _card("the_seven_glamours")
    assert (c.rarity, c.type, c.cost, c.exhaust) == ("rare", "attack", 2, True)
    up = loader.get_card("proto_ym_the_seven_glamours+")
    assert up.cost == 2
    assert next(e["amount"] for e in up.effects if e["op"] == "damage") == 16
    assert _row("proto_ym_the_seven_glamours")["description"] == (
        "Deal 12 [gold]Electro[/gold] damage. If this kills an enemy, "
        "[gold]Publish[/gold] an [gold]Annotated[/gold] card in your hand.")


def test_seven_glamours_kill_publishes_one_card():
    st, a, b, plain = _glamours_state()
    st.enemies[0].hp = 5
    _play(st, _card("the_seven_glamours"))
    assert not st.enemies[0].alive
    # One card: the sim's pick is the best by PUBLISH_ORDER (Footnote).
    assert Y.stack(b) == [Y.FOOTNOTE] and Y.temp(b) is None
    assert Y.stack(a) == [] and Y.temp(a) == Y.RED_INK
    assert Y.stack(plain) == []


def test_seven_glamours_without_a_kill_publishes_nothing():
    st, a, b, plain = _glamours_state()
    _play(st, _card("the_seven_glamours"))
    assert st.enemies[0].hp == 88
    assert Y.stack(a) == [] and Y.stack(b) == []
    assert Y.temp(a) == Y.RED_INK and Y.temp(b) == Y.FOOTNOTE


def test_seven_glamours_minion_kill_publishes_nothing():
    st, a, b, plain = _glamours_state()
    st.enemies[0].hp = 5
    st.enemies[0].counts_for_fatal = False       # a summoned Minion
    _play(st, _card("the_seven_glamours"))
    assert not st.enemies[0].alive
    assert Y.stack(a) == [] and Y.stack(b) == []


# 6. The Edit chooser (seat page) --------------------------------------------

def _hand_select(prompt, enchantment):
    card = {"index": 0, "name": "Strike", "id": "STRIKE_YAE",
            "description": "Deal 6 damage.", "type": "Attack", "cost": "1",
            "selected": False}
    if enchantment:
        card["enchantment"] = enchantment
    return card


def test_mark_edit_replaces_names_the_temporary_annotation():
    from understudy.blindplay_faces import mark_edit_replaces
    faces = [{"enchantment": {"name": "Annotated",
                              "text": "Published: Red Ink. This combat: Footnote."}},
             {"enchantment": {"name": "Annotated", "text": "Published: Red Ink."}},
             {"enchantment": None}, {}]
    mark_edit_replaces("Choose a card to Edit: Red Ink (x).", faces)
    assert faces[0]["replaces"] == "Footnote"
    assert "replaces" not in faces[1] and "replaces" not in faces[2]
    other = [{"enchantment": {"name": "Annotated",
                              "text": "This combat: Footnote."}}]
    mark_edit_replaces("Choose a card to Publish.", other)
    assert "replaces" not in other[0]


# 8. An Edit with nothing to Edit says so -------------------------------------

def test_margin_note_with_no_card_says_so():
    st = _state()
    c = _card("margin_note")
    st.player.hand[:] = []
    _play(st, c)
    assert any(e.get("what") == "hand" for e in _events(st, "yae_edit_nothing"))


def test_evergreen_charm_with_no_sakura_says_so():
    st = _state()
    _play(st, _card("evergreen_charm"))
    assert any(e.get("what") == "sakura" for e in _events(st, "yae_edit_nothing"))


# 7. Foxfire Lure --------------------------------------------------------------

def test_foxfire_lure_says_striking_sakura():
    assert "your striking [gold]Sakura[/gold] strike it" in         _row("proto_ym_foxfire_lure")["description"]


# Pick 1 (a), ruled 2026-10-15 ([USER]: "Otherwise I'm good with it."):
# Edits that Exhaust, and a multi-card Edit is one chooser of up to N
# DIFFERENT cards that the player may stop short of (GPT, relayed by
# [USER]). C# half: YaeReviewR4Tests' pick 1 facts.

def test_pick1_rows():
    seal, foot = _card("sakura_seal"), _card("footnote")
    inked, royal = _card("inked_branches"), _card("royalties")
    assert (seal.cost, seal.exhaust) == (0, True)
    assert (foot.cost, foot.exhaust) == (0, True)
    assert (inked.cost, inked.exhaust) == (0, True)
    assert (royal.cost, royal.exhaust) == (1, True)
    amount = lambda c: next(fx["amount"] for fx in c.effects
                            if fx.get("op") == "yae")
    assert (amount(seal), amount(_card("sakura_seal+"))) == (2, 3)
    assert (amount(foot), amount(_card("footnote+"))) == (2, 3)
    assert (amount(royal), amount(_card("royalties+"))) == (2, 2)
    assert _card("royalties+").cost == 0
    assert _card("inked_branches+").cost == 0
    for name, base, per in (("bestseller", (8, 10), (3, 4)),
                            ("print_run", (6, 8), (3, 4))):
        fx = lambda c: next(f for f in c.effects if f.get("op") == "yae")
        lo, hi = fx(_card(name)), fx(_card(name + "+"))
        assert (lo["base"], hi["base"]) == base
        assert (lo["per"], hi["per"]) == per


def _hand(st, *names):
    cards = [loader.get_card(n) for n in names]
    st.player.hand += cards
    return cards


def test_a_multi_edit_picks_distinct_cards():
    st = _state()
    a, b = _hand(st, "strike", "defend")
    _play(st, _card("footnote"))
    assert Y.temp(a) == Y.FOOTNOTE and Y.temp(b) == Y.FOOTNOTE
    assert Y.ledger(st.player).edits == 2


def test_a_multi_edit_never_edits_the_same_card_twice():
    st = _state()
    (a,) = _hand(st, "strike")
    _play(st, _card("footnote+"))           # up to 3, one card to reach
    assert Y.temp(a) == Y.FOOTNOTE
    assert Y.ledger(st.player).edits == 1


def test_a_pilot_that_names_the_same_card_again_stops():
    st = _state()
    a, b = _hand(st, "strike", "defend")
    Y.ledger(st.player).edit_choice = lambda state, editor, ann: a
    _play(st, _card("footnote"))
    assert Y.temp(a) == Y.FOOTNOTE and not Y.is_annotated(b)
    assert Y.ledger(st.player).edits == 1


def test_a_later_pick_stops_rather_than_overwrite():
    st = _state()
    a, b = _hand(st, "strike", "defend")
    Y.annotate(st, b, Y.RED_INK)
    _play(st, _card("sakura_seal"))
    # The first pick takes the fresh card; the second would overwrite Red
    # Ink, so it stops.
    assert Y.temp(a) == Y.SAKURA_SEAL and Y.temp(b) == Y.RED_INK


def test_inked_branches_upgraded_also_edits_a_hand_card():
    st = _state()
    Y.plant(st, 1)
    (a,) = _hand(st, "strike")
    _play(st, _card("inked_branches"))
    assert Y.ledger(st.player).sakura[0].annotation == Y.RED_INK
    assert not Y.is_annotated(a)
    _play(st, _card("inked_branches+"))
    assert Y.temp(a) == Y.RED_INK
