"""THE ELEMENT PORT: Swirl pays (`review/ruled/element-home-review-2026-09-28.md`
§4 A, ruled §6), AS AMENDED 2026-10-03: there is no spent aura, and every
reaction consumes the aura it acts on, Swirl and Crystallize included, as in
Genshin.

[USER], 2026-10-03: "Should we get rid of the concept of elements being
'spent' after a swirl? It seems to generate confusion." then "agreed ...
please proceed". The consequence accepted with it: a Swirl that hits ALL
enemies pays once per enemy whose aura is still there when its Anemo hit
lands, because the copies a Swirl spreads are fresh.

`C.SWIRL_PAYS` is pinned on AND off here by flipping it. The C# twin of every
rule below is `klee-mod/KleeTests/ElementPortTests.cs`.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.engine import effects, reactions
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def swirl_pays(monkeypatch):
    monkeypatch.setattr(C, "SWIRL_PAYS", True)


def hit(state, enemy, element, dmg=10):
    return reactions.resolve_hit(state, enemy, element, dmg)


def three(hp=30):
    return make_state(enemies=[make_enemy(hp=hp, name="a"),
                               make_enemy(hp=hp, name="b"),
                               make_enemy(hp=hp, name="c")])


def reactions_logged(state):
    return [ev for ev in state.log if ev.get("event") == "reaction"]


# --- the sim's defaults -----------------------------------------------------

def test_the_sim_default_is_off_and_the_flat_two_is_two():
    # The arm convention (`operations/prototype.md`). The mod turns it on;
    # `lint_constant_parity` compares the 2 by value.
    assert C.SWIRL_PAYS is False
    assert C.SWIRL_DAMAGE == 2
    assert not hasattr(C, "CRYSTALLIZE_KEEPS_AURA")


def test_there_is_no_spent_state():
    e = make_enemy()
    assert not hasattr(e, "aura_spent")
    assert not hasattr(reactions, "trigger_keeps_aura")
    assert not hasattr(reactions, "trigger_pays")


# --- Swirl (§4 A) -----------------------------------------------------------

@pytest.mark.usefixtures("swirl_pays")
def test_swirl_consumes_spreads_fresh_copies_and_deals_two_to_all():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    out = hit(st, a, "anemo", 5)
    assert out == 5                           # Swirl amplifies nothing
    # Consumed on the struck enemy, like every reaction.
    assert a.aura is None and a.aura_turns_left == 0
    # Spread to the others, ordinary auras at full duration.
    for e in (b, c):
        assert e.aura == "pyro"
        assert e.aura_turns_left == C.AURA_DURATION_TURNS
    # The flat 2 to every enemy, the struck one included.
    assert [e.hp for e in (a, b, c)] == [30 - C.SWIRL_DAMAGE] * 3
    # Exactly one reaction: the 2 is element-less and reacts with nothing.
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]
    splash = [ev for ev in st.log if ev.get("event") == "damage"
              and ev.get("source") == "reaction_splash"]
    assert len(splash) == 3


@pytest.mark.usefixtures("swirl_pays")
def test_the_two_ignores_block_like_overloads_splash():
    st = three()
    a, b, _ = st.enemies
    b.block = 10
    hit(st, a, "hydro", 0)
    hit(st, a, "anemo", 0)
    assert b.hp == 30 - C.SWIRL_DAMAGE and b.block == 10


@pytest.mark.usefixtures("swirl_pays")
def test_the_spread_refreshes_an_aura_of_the_same_element():
    # Amended 2026-10-01 ([USER]): "reapplying the same element as a refresh
    # mechanic feels fine". A body already wearing it goes back to full
    # duration; nothing reacts there.
    st = three()
    a, b, _ = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, b, "pyro", 0)
    b.aura_turns_left = 1
    hit(st, a, "anemo", 0)
    assert b.aura == "pyro"
    assert b.aura_turns_left == C.AURA_DURATION_TURNS
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]


@pytest.mark.usefixtures("swirl_pays")
def test_the_spread_replaces_another_aura_and_does_not_react_there():
    # Today's reach, kept: a different aura is replaced, and the copy does
    # not react where it lands (no new spread reactions).
    st = three()
    a, b, _ = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, b, "electro", 0)
    hit(st, a, "anemo", 0)
    assert b.aura == "pyro"
    assert "weak" not in b.powers                         # no Overload on b
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]


@pytest.mark.usefixtures("swirl_pays")
def test_a_spread_copy_is_fresh_and_a_later_anemo_hit_swirls_it():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "cryo", 0)
    hit(st, a, "anemo", 0)
    assert hit(st, b, "anemo", 7) == 7
    assert b.aura is None                                 # consumed
    assert a.aura == "cryo" and c.aura == "cryo"          # b's spread
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"] * 2
    assert [e.hp for e in st.enemies] == [30 - 2 * C.SWIRL_DAMAGE] * 3


@pytest.mark.usefixtures("swirl_pays")
def test_a_second_anemo_hit_on_the_same_body_finds_no_aura():
    st = three()
    a = st.enemies[0]
    hit(st, a, "pyro", 0)
    hit(st, a, "anemo", 0)
    snapshot = [(e.hp, e.aura, e.aura_turns_left) for e in st.enemies]
    hit(st, a, "anemo", 0)
    assert [(e.hp, e.aura, e.aura_turns_left)
            for e in st.enemies] == snapshot
    assert len(reactions_logged(st)) == 1


@pytest.mark.usefixtures("swirl_pays")
def test_a_swirl_all_over_three_enemies_and_one_pyro_aura_pays_three_times():
    # The consequence [USER] accepted: an Anemo hit on ALL enemies, landing
    # in enemy order, meets a's Pyro (spreads to b and c), then b's fresh
    # copy (spreads to a and c), then c's (spreads to a and b).
    st = three(hp=60)
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    for e in list(st.living_enemies):
        effects.deal_damage_to_enemy(st, e, 0, element="anemo",
                                     source="attack")
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"] * 3
    assert [e.hp for e in (a, b, c)] == [60 - 3 * C.SWIRL_DAMAGE] * 3
    assert (a.aura, b.aura, c.aura) == ("pyro", "pyro", None)


@pytest.mark.usefixtures("swirl_pays")
def test_nothing_recurses_a_copy_is_an_application_with_no_trigger():
    # A Swirl's spread puts copies up with `apply_aura` and never calls
    # `resolve_hit`, so one Anemo hit makes exactly one Swirl however many
    # bodies carry a different aura.
    st = make_state(enemies=[make_enemy(hp=40, name=n) for n in "abcd"])
    a, b, c, d = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, b, "hydro", 0)
    hit(st, c, "electro", 0)
    calls = []
    real = reactions.resolve_hit

    def spy(*args, **kwargs):
        calls.append(args[2])
        return real(*args, **kwargs)

    reactions.resolve_hit = spy
    try:
        spy(st, a, "anemo", 0)
    finally:
        reactions.resolve_hit = real
    assert calls == ["anemo"]
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]
    assert (b.aura, c.aura, d.aura) == ("pyro", "pyro", "pyro")


# --- Crystallize ------------------------------------------------------------

@pytest.mark.parametrize("swirl", [False, True])
def test_geo_gives_four_block_and_consumes_the_aura(monkeypatch, swirl):
    monkeypatch.setattr(C, "SWIRL_PAYS", swirl)
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "electro", 0)
    hit(st, e, "geo", 5)
    assert st.player.block == C.CRYSTALLIZE_BLOCK
    assert e.aura is None and e.aura_turns_left == 0
    hit(st, e, "geo", 0)                                  # nothing left
    assert st.player.block == C.CRYSTALLIZE_BLOCK
    assert len(reactions_logged(st)) == 1


@pytest.mark.usefixtures("swirl_pays")
def test_swirl_then_crystallize_on_a_spread_copy_pays_both():
    st = three()
    a, b, _ = st.enemies
    hit(st, a, "hydro", 0)
    hit(st, a, "anemo", 0)
    hit(st, a, "geo", 0)                                  # a: consumed
    assert st.player.block == 0
    hit(st, b, "geo", 0)                                  # b's fresh copy
    assert st.player.block == C.CRYSTALLIZE_BLOCK and b.aura is None
    assert [ev["reaction"] for ev in reactions_logged(st)] == [
        "swirl", "crystallize"]


# --- the shared rule --------------------------------------------------------

@pytest.mark.usefixtures("swirl_pays")
def test_pyro_onto_hydro_still_vaporizes_and_consumes():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "hydro", 0)
    assert hit(st, e, "pyro", 10) == 10 * C.VAPORIZE_MULT
    assert e.aura is None                                 # iron rule


# --- repeated hits cannot loop ----------------------------------------------

@pytest.mark.usefixtures("swirl_pays")
def test_a_multi_hit_anemo_card_on_one_body_swirls_once():
    st = three(hp=60)
    a = st.enemies[0]
    hit(st, a, "pyro", 0)
    for _ in range(4):
        effects.deal_damage_to_enemy(st, a, 3, element="anemo",
                                     source="attack")
    assert len(reactions_logged(st)) == 1


@pytest.mark.usefixtures("swirl_pays")
def test_a_geo_performer_acting_twice_crystallizes_once():
    # Navia's act is a Geo hit through the ordinary pipeline
    # (`furina_stage`, powered=False); acting twice is two of them.
    st = make_state(enemies=[make_enemy(hp=60)])
    e = st.enemies[0]
    hit(st, e, "hydro", 0)
    for _ in range(2):
        effects.deal_damage_to_enemy(st, e, 4, element="geo",
                                     powered=False, source="salon")
    assert st.player.block == C.CRYSTALLIZE_BLOCK


@pytest.mark.usefixtures("swirl_pays")
def test_a_swirl_over_every_enemy_pays_per_standing_aura():
    # Venti's Wind's Grand Ode Swirls every enemy at the end of the turn.
    # With fresh copies, each body still wearing the aura when its turn in
    # the sweep comes Swirls (2026-10-03): three bodies, three Swirls.
    st = three()
    hit(st, st.enemies[0], "pyro", 0)
    st.player.powers["mc_grand_ode"] = 1
    effects.companion_overhaul_turn_end(st)
    assert len(reactions_logged(st)) == 3


# --- the switch off ---------------------------------------------------------

@pytest.mark.usefixtures("consume_triggers")
def test_swirl_pays_off_copies_onto_every_enemy_with_no_flat_two():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, a, "anemo", 0)
    assert all(e.aura == "pyro" for e in (a, b, c))
    assert all(e.aura_turns_left == C.AURA_DURATION_TURNS for e in (a, b, c))
    assert all(e.hp == 30 for e in (a, b, c))
    hit(st, b, "anemo", 0)                  # the copy Swirls again
    assert len(reactions_logged(st)) == 2
    hit(st, c, "geo", 0)
    assert c.aura is None and st.player.block == C.CRYSTALLIZE_BLOCK


# --- the event ---------------------------------------------------------------

def test_the_reaction_event_names_its_source_kind():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "hydro", 0)
    hit(st, e, "pyro", 0)
    assert reactions_logged(st)[-1]["source_kind"] == "automatic"
    st.card_aim_bound = True
    hit(st, e, "hydro", 0)
    hit(st, e, "pyro", 0)
    assert reactions_logged(st)[-1]["source_kind"] == "card"
    st.current_card_companion = True
    hit(st, e, "hydro", 0)
    hit(st, e, "pyro", 0)
    assert reactions_logged(st)[-1]["source_kind"] == "companion"


# --- the words ---------------------------------------------------------------

def test_the_flat_two_is_one_number_on_every_surface():
    import re
    from pathlib import Path
    from understudy import blindplay_shape
    repo = Path(__file__).resolve().parents[2]
    mod = repo / "klee-mod" / "KleeCode"
    table = (mod / "Elements" / "ReactionTable.cs").read_text(encoding="utf-8")
    assert re.search(rf"SwirlDamage\s*=\s*{C.SWIRL_DAMAGE}\b", table)
    assert blindplay_shape.SWIRL_DAMAGE == C.SWIRL_DAMAGE
    # Interpolated, never typed: a retune cannot leave a tip quoting 2.
    for path in (mod / "KleeMod.cs",
                 mod / "Cards" / "Prototype" / "ArmKeywordTips.cs"):
        assert "ReactionConstants.SwirlDamage" in path.read_text(
            encoding="utf-8"), path.name


def test_no_surface_still_speaks_of_a_spent_aura():
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    mod = repo / "klee-mod" / "KleeCode"
    text = (mod / "KleeMod.cs").read_text(encoding="utf-8")
    assert "SPENT_PREVIEW" not in text
    assert "meets an aura: remove it, deal" in text
    aura = (mod / "Powers" / "AuraPower.cs").read_text(encoding="utf-8")
    assert "smartDescriptionSpent" not in aura and "Spent: " not in aura
    tips = (mod / "Cards" / "Prototype" / "ArmKeywordTips.cs").read_text(
        encoding="utf-8")
    assert "copy it, spent" not in tips
