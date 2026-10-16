"""RED INK ON A PLANTING CARD, AND THE DEAD-EDIT FILTER (ruled 2026-10-14,
`review/active/yae-design-axes-2026-10-14.md`, the dated note). [USER]:
"Hmm, let's do both. Make the Sakura work, but also try to block dead edits
when we can."

  1. Red Ink on a card that plants a Sakura passes to every Sakura that
     play plants, and the card's own damage and Block still take the +3
     (widened 2026-10-14 after a GPT design review: Twin Sakura+ gains
     Block and once lost the Sakura bonus); a full-shrine plant that only
     levels plants nothing, so nothing inherits; no other Annotation passes.
  2. An Edit, Reborn as Guuji Yae and the after-elite Publish offer skip a
     card the Annotation would do nothing on: only Red Ink can be dead.

The sim half. The C# half is
`klee-mod/KleeTests/Prototype/YaeRedInkSakuraTests.cs`.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
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


def _ym(name):
    return "proto_ym_" + name


def _card(name):
    return loader.get_card(_ym(name))


def _red_ink_edit():
    """A bare "Edit a card in your hand: Red Ink" (Proofread's face until
    2026-10-14, when it became Reprint): the Red Ink Edit with nothing else
    on the card, so a test reads Red Ink alone."""
    card = loader.get_card(_ym("proofread"))
    card.effects = [{"op": "yae", "kind": "edit", "annotation": Y.RED_INK,
                     "amount": 1}]
    return card


def _play(st, card):
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _sakura(st):
    return Y.ledger(st.player).sakura


# ---------------------------------------------------------------------------
# 1. Inheritance
# ---------------------------------------------------------------------------

def test_red_ink_yakan_evocation_plants_a_red_ink_sakura():
    st = _state()
    evo = _card("yakan_evocation")
    Y.annotate(st, evo, Y.RED_INK)
    _play(st, evo)
    (s,) = _sakura(st)
    assert s.annotations == [Y.RED_INK]
    assert Y.act_size(st, s) == Y.SAKURA_BASE + s.level + Y.RED_INK_AMOUNT


def test_twin_sakura_gives_red_ink_to_both():
    st = _state()
    twin = _card("twin_sakura")
    Y.annotate(st, twin, Y.RED_INK)
    _play(st, twin)
    assert [s.annotations for s in _sakura(st)] == [[Y.RED_INK], [Y.RED_INK]]


def test_a_plant_at_a_level_passes_red_ink_too():
    # Guardian of Narukami (Grafted Branch's role until the dedupe cut it,
    # 2026-10-16).
    st = _state()
    guard = _card("guardian_of_narukami")
    Y.annotate(st, guard, Y.RED_INK)
    _play(st, guard)
    assert [s.annotations for s in _sakura(st)] == [[Y.RED_INK]]


def test_a_full_shrine_plant_that_only_levels_gives_the_oldest_the_red_ink():
    # Yae review r4, item 2 (was: inherits nothing).
    st = _state()
    Y.plant(st, 3)
    evo = _card("yakan_evocation")
    Y.annotate(st, evo, Y.RED_INK)
    _play(st, evo)
    assert len(_sakura(st)) == 3
    assert _sakura(st)[0].annotations == [Y.RED_INK]
    assert all(s.annotations == [] for s in _sakura(st)[1:])


def test_fox_fire_on_a_planting_card_does_not_inherit():
    st = _state()
    evo = _card("yakan_evocation")
    Y.annotate(st, evo, Y.FOX_FIRE)
    _play(st, evo)
    assert [s.annotations for s in _sakura(st)] == [[]]


def test_a_planting_card_that_gives_block_gets_both():
    """Twin Sakura+ gains 4 Block: Red Ink rides the Block AND both Sakura
    inherit it (2026-10-14)."""
    twin = loader.get_card(_ym("twin_sakura") + "+")
    assert Y.plants_sakura(twin) and Y.gives_block(twin)
    assert Y.inherits(twin) is False             # not annotated yet
    st = _state()
    Y.annotate(st, twin, Y.RED_INK)
    assert Y.inherits(twin)
    _play(st, twin)
    assert st.player.block == 4 + Y.RED_INK_AMOUNT
    assert [s.annotations for s in _sakura(st)] == [[Y.RED_INK], [Y.RED_INK]]


def test_a_published_red_ink_planting_card_plants_red_ink_every_play():
    st = _state()
    evo = _card("yakan_evocation")
    Y.annotate(None, evo, Y.RED_INK, "published")
    evo.ym_published = True
    _play(st, evo)
    st.player.discard_pile = [c for c in st.player.discard_pile
                              if c is not evo]
    _play(st, evo)
    assert [s.annotations for s in _sakura(st)] == [[Y.RED_INK], [Y.RED_INK]]


# ---------------------------------------------------------------------------
# 2. The dead-edit filter
# ---------------------------------------------------------------------------

def test_red_ink_skips_a_pure_utility_card_footnote_takes_it():
    lure = _card("foxfire_lure")
    assert not Y.affects(lure, Y.RED_INK)
    for name in (Y.FOOTNOTE, Y.DEADLINE, Y.FOX_FIRE, Y.SAKURA_SEAL,
                 Y.ROYALTIES, Y.REPRINT):
        assert Y.affects(lure, name)
    for cid in ("strike", "defend", _ym("yakan_evocation"),
                _ym("twin_sakura"), _ym("guardian_of_narukami")):
        assert Y.affects(loader.get_card(cid), Y.RED_INK), cid


def test_a_red_ink_edit_with_only_a_utility_card_in_hand_does_nothing():
    st = _state()
    lure = _card("foxfire_lure")
    st.player.hand.append(lure)
    _play(st, _red_ink_edit())
    assert not Y.is_annotated(lure)
    assert Y.ledger(st.player).edits == 0


def test_footnote_reaches_the_utility_card():
    st = _state()
    lure = _card("foxfire_lure")
    st.player.hand.append(lure)
    _play(st, _card("footnote"))
    assert Y.temp(lure) == Y.FOOTNOTE


def test_red_ink_goes_to_a_planting_card_over_a_utility_card():
    st = _state()
    lure, evo = _card("foxfire_lure"), _card("yakan_evocation")
    st.player.hand += [lure, evo]
    _play(st, _red_ink_edit())
    assert Y.temp(evo) == Y.RED_INK and not Y.is_annotated(lure)


def test_a_pilot_choice_of_a_dead_card_edits_nothing():
    st = _state()
    lure = _card("foxfire_lure")
    st.player.hand.append(lure)
    Y.ledger(st.player).edit_choice = lambda state, editor, ann: lure
    _play(st, _red_ink_edit())
    assert not Y.is_annotated(lure)


def test_reborn_respects_the_filter():
    st = _state()
    Y.ledger(st.player).reborn_choice = Y.RED_INK
    lure, strike = _card("foxfire_lure"), loader.get_card("strike")
    st.player.hand += [lure, strike]
    _play(st, _card("reborn_as_guuji_yae"))
    assert Y.temp(strike) == Y.RED_INK
    assert not Y.is_annotated(lure)
    assert Y.ledger(st.player).edits == 1


def test_the_publish_offer_respects_the_filter():
    cards = {0: _card("foxfire_lure"), 1: loader.get_card("strike"),
             2: _card("foxfire_lure")}
    drafts = {0: Y.RED_INK, 1: Y.RED_INK, 2: Y.FOOTNOTE}
    assert Y.publish_choices(drafts, {}, cards) == [1, 2]
    assert Y.publish_choices(drafts, {}) == [0, 1, 2]      # no cards: unfiltered
    out = Y.publish_after_fight("elite", {0: Y.RED_INK}, {}, cards=cards)
    assert out == []


# ---------------------------------------------------------------------------
# 3. The engines agree on which cards plant, and the tip says it
# ---------------------------------------------------------------------------

def test_the_planting_marker_is_the_sims_planting_set():
    """The C# marker (codegen) and the sim's `plants_sakura` name the same
    rows: Yakan Evocation, Twin Sakura, (review r3) the two kind planters,
    Foxfire Sweep and Shrine Maiden's Guard, and the pool to 78's five left
    after the dedupe (2026-10-16)."""
    marked, planting = set(), set()
    for path in GENERATED.glob("ProtoYm*.cs"):
        text = path.read_text(encoding="utf-8")
        cid = re.search(r"Sheet entry: id=(\S+)", text).group(1)
        if "ISakuraPlanterCard" in text.split("{", 1)[0]:
            marked.add(cid)
        if Y.plants_sakura(loader.get_card(cid)):
            planting.add(cid)
    assert marked == planting == {_ym("yakan_evocation"), _ym("twin_sakura"),
                                  _ym("foxfire_sweep"),
                                  _ym("shrine_maidens_guard"),
                                  _ym("thunder_petal"), _ym("genre_shift"),
                                  _ym("replanting"), _ym("narukami_bloom"),
                                  _ym("guardian_of_narukami")}


def test_a_yae_kinds_own_block_counts_for_red_ink_in_both_engines():
    """Red Ink rides a `yae` kind's own Block, so the filter keeps it. The
    refill (2026-10-16): Hide Behind the Shrine's "gain 5 more" is one, the
    only row carrying the C# `IYaeBlockCard` marker. Sakura Canopy's Block
    is on the calculated rail (a `CalculatedBlockVar`), which the game's own
    GainsBlock answers."""
    hide = _card("hide_behind_the_shrine")
    assert Y.gives_block(hide) and Y.affects(hide, Y.RED_INK)
    marked = set()
    for path in GENERATED.glob("ProtoYm*.cs"):
        text = path.read_text(encoding="utf-8")
        if "IYaeBlockCard" in text.split("{", 1)[0]:
            marked.add(re.search(r"Sheet entry: id=(\S+)", text).group(1))
    assert marked == {_ym("hide_behind_the_shrine")}
    src = (GENERATED / "ProtoYmSakuraCanopy.cs").read_text(encoding="utf-8")
    assert "CalculatedBlockVar(" in src


def test_the_red_ink_rule_says_where_it_goes():
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "YaeAnnotations.cs").read_text(encoding="utf-8")
    assert ('"If it plants, its [gold]Sakura[/gold] get it too."'
            in src)
