"""YAE REVIEW R1 (Claude, 2026-10-14, no pick;
`review/active/yae-design-axes-2026-10-14.md`, the dated note):

  1. A "Rite: X" card says in combat what the shrine would do under X,
     summed over the Sakura standing ("Rite: Warding (your Sakura: 5
     Block)"); nothing with no Sakura. The Rite badge and the seat page say
     the same for the current Rite.
  2. Every Tenko card says "Tenko (no Sakura)" while none stands; none is
     gated (the coordinator dropped Kitsune Rite's gate, 2026-10-14).
  3. Sakura Seal costs 0; its upgrade (the cost cut before) is Footnote's,
     Edit 2 cards.
  4. Kitsune Rite: "Tenko. Draw 1 card." (upgrade as before, 1 [0]).

The sim half. The C# half is
`klee-mod/KleeTests/Prototype/YaeReviewR1Tests.cs`; the generated faces are
read here too, so the two engines' words are one table.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402

CODE = REPO / "klee-mod" / "KleeCode"
GENERATED = CODE / "Cards" / "Prototype" / "Generated"
SHRINE_CS = CODE / "Powers" / "Prototype" / "YaeShrine.cs"


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
        loader.reset_arm_caches()


def _state(n=1):
    enemies = [Enemy(hp=100, max_hp=100, name=f"e{i}",
                     intents=[{"kind": "block", "amount": 0}])
               for i in range(n)]
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(5)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _play(st, card):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _ym(name):
    return "proto_ym_" + name


def _face(card_id: str) -> str:
    text = (GENERATED / f"{gen.pascal(card_id)}.cs").read_text(encoding="utf-8")
    return re.search(r'\("description", "(.*)"\)', text).group(1)


# ---------------------------------------------------------------------------
# 1. The Rite clause
# ---------------------------------------------------------------------------

def test_no_sakura_no_rite_clause():
    st = _state()
    for rite in Y.RITES:
        assert Y.rite_total(st, rite) == 0
        assert Y.rite_line(st, rite) == ""


def test_the_rite_clause_sums_the_sakura_standing_under_that_rite():
    st = _state()
    for _ in range(3):
        _play(st, _ym("yakan_evocation"))        # Levels 3, 2, 1
    assert Y.rite_line(st, Y.THUNDER) == " (your Sakura: 12 damage)"
    assert Y.rite_line(st, Y.WARDING) == " (your Sakura: 12 Block)"
    assert Y.rite_line(st, Y.WILDFIRE) == " (your Sakura: 6 to ALL)"
    assert Y.rite_line(st, Y.OFFERING) == " (your Sakura: draw 3)"


def test_the_clause_reads_levels_and_red_ink_as_the_strike_does():
    st = _state()
    _play(st, _ym("yakan_evocation"))            # Level 1
    Y.level_up(st, 3)                            # Level 4: no cap
    Y.edit_sakura(st, "every", 1, Y.RED_INK)
    assert Y.rite_total(st, Y.THUNDER) == 2 + 4 + Y.RED_INK_AMOUNT
    assert Y.rite_total(st, Y.WILDFIRE) == 4 + Y.RED_INK_AMOUNT
    assert Y.rite_total(st, Y.OFFERING) == 1     # Red Ink skips Offering


def test_the_clause_is_what_the_strikes_then_do():
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("yakan_evocation"))
    promised = Y.rite_total(st, Y.WARDING)
    _play(st, _ym("shrine_maidens_guard"))       # 6 Block, Rite: Warding
    block = st.player.block
    Y.turn_end(st)
    assert st.player.block - block == promised


def test_the_words_are_one_table_in_both_engines():
    cs = SHRINE_CS.read_text(encoding="utf-8")
    for rite, cs_name in gen.YAE_RITES.items():
        words = Y.RITE_FACE[rite].replace("{n}", "{n}")
        if rite == Y.THUNDER:
            assert '_ => $"' + words + '"' in cs, words
        else:
            assert f'YaeRite.{cs_name} => $"{words}"' in cs, words
    assert f'NoSakura = "{Y.NO_SAKURA}"' in cs
    assert '" (your Sakura: {' in cs and Y.RITE_LINE.startswith(" (your Sakura: ")


@pytest.mark.parametrize("card_id,rite", [
    (_ym("thunder_rite"), "Thunder"),
    (_ym("shrine_maidens_guard"), "Warding"),
    (_ym("foxfire_sweep"), "Wildfire"),
    (_ym("kitsune_guile"), "Wildfire"),
    (_ym("manuscript_pile"), "Offering"),
])
def test_every_rite_card_carries_the_clause_after_the_rites_name(card_id, rite):
    face = _face(card_id)
    assert f"[gold]Rite[/gold]: {rite}{{InCombat:{{YaeRite}}|}}" in face
    text = (GENERATED / f"{gen.pascal(card_id)}.cs").read_text(encoding="utf-8")
    assert (f'description.Add("YaeRite", YaeShrineFace.RiteLine(this, '
            f'YaeRite.{rite}));') in text


def test_the_seat_page_prints_the_sum_on_the_rite_line():
    from understudy import blindplay_render as R
    shrine = {"sakura": [{"slot": 1, "level": 2, "strike": 4, "turns": 2,
                          "annotation": None},
                         {"slot": 2, "level": 1, "strike": 3, "turns": 3,
                          "annotation": None}],
              "lure": None, "annotated": 0, "rite": "Warding"}
    lines = R._render_shrine(shrine)
    assert lines[1] == ("- Rite: Warding. Each strike gives you its number "
                        "in Block. Your Sakura now: 7 Block.")
    empty = dict(shrine, sakura=[], rite="Offering")
    assert R._render_shrine(empty)[1] == (
        "- Rite: Offering. Each strike draws you its number of cards next "
        "turn.")
    for rite, words in R.SHRINE_RITE_AMOUNTS.items():
        assert words == Y.RITE_FACE[rite.lower()]


# ---------------------------------------------------------------------------
# 2. Tenko with no Sakura
# ---------------------------------------------------------------------------

def test_kitsune_rite_is_playable_with_no_sakura_and_still_draws():
    st = _state()
    card = loader.get_card(_ym("kitsune_rite"))
    assert card.playable_if is None
    st.player.hand.append(card)
    st.player.energy = 3
    assert combat.card_playable(st, card)
    hand = len(st.player.hand)
    combat.play_card(st, card)
    assert len(st.player.hand) == hand            # -1 played, +1 drawn
    assert not any(r["event"] == "yae_sakura_strike" for r in st.log)


@pytest.mark.parametrize("card_id", [_ym("kitsune_rite"),
                                     _ym("thunder_rite"),
                                     _ym("mikage_thunder"),
                                     _ym("tenko_kenshin")])
def test_every_tenko_card_says_no_sakura(card_id):
    face = _face(card_id)
    assert "[gold]Tenko[/gold]{InCombat:{YaeTenko}|}" in face
    text = (GENERATED / f"{gen.pascal(card_id)}.cs").read_text(encoding="utf-8")
    assert 'description.Add("YaeTenko", YaeShrineFace.TenkoLine(this));' in text
    assert "IsPlayable" not in text


def test_the_gate_predicate_is_gone():
    assert "sakura_standing" not in gen.PREDICATES_CS
    assert "sakura_standing" not in Path(effects.__file__).read_text(
        encoding="utf-8")


def test_the_tenko_clause_reads_the_shrine():
    st = _state()
    assert Y.tenko_line(st) == Y.NO_SAKURA == " (no Sakura)"
    _play(st, _ym("yakan_evocation"))
    assert Y.tenko_line(st) == ""


# ---------------------------------------------------------------------------
# 3. Sakura Seal, 0 Energy
# ---------------------------------------------------------------------------

def test_sakura_seal_costs_0_and_its_upgrade_edits_two():
    base = loader.get_card(_ym("sakura_seal"))
    plus = loader.get_card(_ym("sakura_seal") + "+")
    assert base.cost == 0 and plus.cost == 0
    assert base.effects[0]["amount"] == 1 and plus.effects[0]["amount"] == 2
    st = _state()
    a, b = loader.get_card("strike"), loader.get_card("defend")
    st.player.hand += [a, b]
    _play(st, plus)
    assert a.ym_annotation == Y.SAKURA_SEAL == b.ym_annotation


# ---------------------------------------------------------------------------
# 4. Kitsune Rite, Tenko and a card
# ---------------------------------------------------------------------------

def test_kitsune_rite_tenkos_then_draws_one():
    st = _state()
    _play(st, _ym("yakan_evocation"))
    hand = len(st.player.hand)
    _play(st, _ym("kitsune_rite"))
    assert any(r["event"] == "yae_tenko" for r in st.log)
    assert len(st.player.hand) == hand + 1
    plus = loader.get_card(_ym("kitsune_rite") + "+")
    assert plus.cost == 0 and loader.get_card(_ym("kitsune_rite")).cost == 1
    assert plus.exhaust
