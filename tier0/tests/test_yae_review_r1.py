"""YAE REVIEW R1 (Claude, 2026-10-14, no pick;
`review/active/yae-design-axes-2026-10-14.md`, the dated note):

  1. (Shrine r2, 2026-10-14, replaced the Rite clause.) A Tenko card says
     in combat what its Tenko would do, summed over the Sakura standing:
     "Tenko (12 damage)", "Tenko (Warding: 5 Block)".
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
# 1. The Tenko clause (shrine r2 replaced review r1's Rite clause)
# ---------------------------------------------------------------------------

def test_no_sakura_says_so():
    st = _state()
    assert Y.tenko_totals(st) == {k: 0 for k in Y.SAKURA_KINDS}
    assert Y.tenko_line(st) == " (no Sakura)"


def test_the_tenko_clause_sums_the_sakura_standing_by_kind():
    # Review r3: one plain Tenko; the clause sums each kind's action.
    st = _state()
    for _ in range(3):
        _play(st, _ym("yakan_evocation"))        # Levels 1, 1, 1
    assert Y.tenko_line(st) == " (9 damage)"
    Y.ledger(st.player).sakura[1].kind = Y.FOXFIRE
    Y.ledger(st.player).sakura[2].kind = Y.KITSUNE
    assert Y.tenko_line(st) == " (3 damage, 2 to each enemy, 3 Block)"


def test_the_clause_reads_levels_and_red_ink_as_the_action_does():
    st = _state()
    _play(st, _ym("yakan_evocation"))            # Level 1
    Y.level_up(st, 3)                            # Level 4: no cap
    Y.edit_sakura(st, "every", 1, Y.RED_INK)
    assert Y.tenko_totals(st)[Y.THUNDER] == 2 + 4 + Y.RED_INK_AMOUNT


def test_the_clause_is_what_the_tenko_then_does():
    st = _state()
    _play(st, _ym("shrine_maidens_guard"))       # 6 Block, a Kitsune Sakura
    st.player.block = 0
    promised = Y.tenko_totals(st)[Y.KITSUNE]
    _play(st, _ym("kitsune_guile"))              # Tenko
    assert st.player.block == promised == 2 + 1


def test_the_words_are_one_table_in_both_engines():
    cs = SHRINE_CS.read_text(encoding="utf-8")
    for kind in Y.SAKURA_KINDS:
        words = Y.TENKO_FACE[kind]
        if kind == Y.THUNDER:
            assert '_ => $"' + words + '"' in cs, words
        else:
            name = gen.YAE_SAKURA_KINDS[kind]
            assert f'YaeSakuraKind.{name} => $"{words}"' in cs, words
    assert f'NoSakura = "{Y.NO_SAKURA}"' in cs
    assert "YaeTenkoKind" not in cs


@pytest.mark.parametrize("card_id", [
    _ym("shrine_maidens_guard"), _ym("foxfire_sweep"), _ym("kitsune_guile"),
    _ym("manuscript_pile"),
])
def test_no_card_prints_a_typed_tenko(card_id):
    face = _face(card_id)
    assert "(Warding" not in face and "(Wildfire" not in face
    assert "(Offering" not in face and "Rite" not in face
    text = (GENERATED / f"{gen.pascal(card_id)}.cs").read_text(encoding="utf-8")
    assert "YaeTenkoKind" not in text


def test_the_seat_page_has_no_rite_line():
    from understudy import blindplay_render as R
    shrine = {"sakura": [{"slot": 1, "level": 2, "strike": 4, "turns": 2,
                          "annotation": None}],
              "lure": None, "annotated": 0}
    lines = R._render_shrine(shrine)
    assert not any("Rite" in line for line in lines)
    assert not hasattr(R, "SHRINE_RITE_LINE")


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
    assert Y.tenko_line(st) == " (3 damage)"


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
    assert Y.temp(a) == Y.SAKURA_SEAL == Y.temp(b)


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
