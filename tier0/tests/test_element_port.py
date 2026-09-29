"""THE ELEMENT PORT, PHASE ONE: fresh and spent auras, Swirl pays, Crystallize
keeps the aura (`review/ruled/element-home-review-2026-09-28.md` §3, §4, §6).

[USER], ruling §6: "That makes sense." On Geo: "making sure that Geo doesn't
just become a source of infinity block if we don't consume the aura, while
also making sure it's useful whether you trigger it incidentally ... but not
broken if it's your primary element." On Swirl: "it now requires three
elements to effectively function".

Two switches, one per change (§6 pick 4.4), each pinned on AND off here by
flipping it. The C# twin of every rule below is
`klee-mod/KleeTests/ElementPortTests.cs`.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.engine import effects, reactions
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def both_on(monkeypatch):
    monkeypatch.setattr(C, "SWIRL_PAYS", True)
    monkeypatch.setattr(C, "CRYSTALLIZE_KEEPS_AURA", True)


@pytest.fixture
def swirl_only(monkeypatch):
    monkeypatch.setattr(C, "SWIRL_PAYS", True)
    monkeypatch.setattr(C, "CRYSTALLIZE_KEEPS_AURA", False)


@pytest.fixture
def crystallize_only(monkeypatch):
    monkeypatch.setattr(C, "SWIRL_PAYS", False)
    monkeypatch.setattr(C, "CRYSTALLIZE_KEEPS_AURA", True)


def hit(state, enemy, element, dmg=10):
    return reactions.resolve_hit(state, enemy, element, dmg)


def three(hp=30):
    return make_state(enemies=[make_enemy(hp=hp, name="a"),
                               make_enemy(hp=hp, name="b"),
                               make_enemy(hp=hp, name="c")])


def reactions_logged(state):
    return [ev for ev in state.log if ev.get("event") == "reaction"]


# --- the sim's defaults -----------------------------------------------------

def test_the_sim_defaults_are_off_and_the_flat_two_is_two():
    # The arm convention (`operations/prototype.md`): the calibration world
    # is the shipped one. The mod turns both on; `lint_constant_parity`
    # compares the 2 by value.
    assert C.SWIRL_PAYS is False
    assert C.CRYSTALLIZE_KEEPS_AURA is False
    assert C.SWIRL_DAMAGE == 2


# --- Swirl (§4 A) -----------------------------------------------------------

@pytest.mark.usefixtures("both_on")
def test_swirl_on_a_fresh_aura_spreads_keeps_and_deals_two_to_all():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    a.aura_turns_left = 1                     # spending leaves duration alone
    out = hit(st, a, "anemo", 5)
    assert out == 5                           # Swirl amplifies nothing
    # Kept on the struck enemy, now spent, its clock untouched.
    assert a.aura == "pyro" and a.aura_spent and a.aura_turns_left == 1
    # Spread to the two that lacked it, SPENT, at full duration.
    for e in (b, c):
        assert e.aura == "pyro" and e.aura_spent
        assert e.aura_turns_left == C.AURA_DURATION_TURNS
    # The flat 2 to every enemy, the struck one included.
    assert [e.hp for e in (a, b, c)] == [30 - C.SWIRL_DAMAGE] * 3
    # Exactly one reaction: the 2 is element-less and reacts with nothing.
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]
    splash = [ev for ev in st.log if ev.get("event") == "damage"
              and ev.get("source") == "reaction_splash"]
    assert len(splash) == 3


@pytest.mark.usefixtures("both_on")
def test_the_two_ignores_block_like_overloads_splash():
    st = three()
    a, b, _ = st.enemies
    b.block = 10
    hit(st, a, "hydro", 0)
    hit(st, a, "anemo", 0)
    assert b.hp == 30 - C.SWIRL_DAMAGE and b.block == 10


@pytest.mark.usefixtures("both_on")
def test_the_spread_skips_an_enemy_already_wearing_the_element():
    # "every enemy that LACKS it": a body already wearing the aura keeps its
    # own, fresh and with its own clock.
    st = three()
    a, b, _ = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, b, "pyro", 0)
    b.aura_turns_left = 1
    hit(st, a, "anemo", 0)
    assert b.aura == "pyro" and not b.aura_spent and b.aura_turns_left == 1


@pytest.mark.usefixtures("both_on")
def test_the_spread_replaces_another_aura_and_does_not_react_there():
    # Today's reach, kept: a different aura is replaced. The copy reacting
    # where it lands is the deferred candidate (§4 A, "Later").
    st = three()
    a, b, _ = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, b, "electro", 0)
    hit(st, a, "anemo", 0)
    assert b.aura == "pyro" and b.aura_spent
    assert "weak" not in b.powers                         # no Overload on b
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]


@pytest.mark.usefixtures("both_on")
def test_spread_copies_are_spent_so_they_cannot_be_swirled_again():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "cryo", 0)
    hit(st, a, "anemo", 0)
    hp = [e.hp for e in st.enemies]
    assert hit(st, b, "anemo", 7) == 7
    assert [e.hp for e in st.enemies] == hp               # no second 2
    assert b.aura == "cryo" and b.aura_spent
    assert len(reactions_logged(st)) == 1
    assert [ev["event"] for ev in st.log][-1] == "trigger_spent"


@pytest.mark.usefixtures("both_on")
def test_a_second_anemo_hit_on_the_same_spent_aura_does_nothing():
    st = three()
    a = st.enemies[0]
    hit(st, a, "pyro", 0)
    hit(st, a, "anemo", 0)
    snapshot = [(e.hp, e.aura, e.aura_spent, e.aura_turns_left)
                for e in st.enemies]
    hit(st, a, "anemo", 0)
    assert [(e.hp, e.aura, e.aura_spent, e.aura_turns_left)
            for e in st.enemies] == snapshot
    assert len(reactions_logged(st)) == 1


# --- Crystallize (§4 B) -----------------------------------------------------

@pytest.mark.usefixtures("both_on")
def test_geo_on_a_fresh_aura_gives_four_block_and_keeps_it_spent():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "electro", 0)
    e.aura_turns_left = 1
    hit(st, e, "geo", 5)
    assert st.player.block == C.CRYSTALLIZE_BLOCK
    assert e.aura == "electro" and e.aura_spent and e.aura_turns_left == 1


@pytest.mark.usefixtures("both_on")
def test_geo_on_a_spent_aura_gives_nothing():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "electro", 0)
    hit(st, e, "geo", 0)
    hit(st, e, "geo", 0)
    assert st.player.block == C.CRYSTALLIZE_BLOCK
    assert len(reactions_logged(st)) == 1


@pytest.mark.usefixtures("both_on")
def test_swirl_then_crystallize_on_the_same_aura_crystallize_gets_nothing():
    # §7.1: one budget, shared across the room.
    st = three()
    a, b, _ = st.enemies
    hit(st, a, "hydro", 0)
    hit(st, a, "anemo", 0)
    hit(st, a, "geo", 0)
    hit(st, b, "geo", 0)                                  # a spread copy
    assert st.player.block == 0
    assert [ev["reaction"] for ev in reactions_logged(st)] == ["swirl"]


# --- the shared rule (§3) ---------------------------------------------------

@pytest.mark.usefixtures("both_on")
def test_a_same_element_hit_refreshes_and_re_enables_a_trigger():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "pyro", 0)
    hit(st, e, "geo", 0)
    e.aura_turns_left = 1
    hit(st, e, "pyro", 0)
    assert not e.aura_spent and e.aura_turns_left == C.AURA_DURATION_TURNS
    hit(st, e, "geo", 0)
    assert st.player.block == 2 * C.CRYSTALLIZE_BLOCK


@pytest.mark.usefixtures("both_on")
def test_pyro_onto_a_spent_hydro_aura_still_vaporizes():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "hydro", 0)
    hit(st, e, "anemo", 0)
    assert e.aura_spent
    assert hit(st, e, "pyro", 10) == 10 * C.VAPORIZE_MULT
    assert e.aura is None and not e.aura_spent            # iron rule: consumed


@pytest.mark.usefixtures("both_on")
def test_the_aura_still_expires_on_its_own_clock_when_spent():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "cryo", 0)
    hit(st, e, "geo", 0)
    reactions.tick_auras(st)
    assert e.aura == "cryo"
    reactions.tick_auras(st)
    assert e.aura is None


@pytest.mark.usefixtures("both_on")
def test_a_new_aura_after_expiry_arrives_fresh():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "cryo", 0)
    hit(st, e, "geo", 0)
    reactions.tick_auras(st)
    reactions.tick_auras(st)
    hit(st, e, "cryo", 0)
    assert not e.aura_spent


# --- repeated hits cannot loop ----------------------------------------------

@pytest.mark.usefixtures("both_on")
def test_a_multi_hit_anemo_card_swirls_once():
    st = three(hp=60)
    a = st.enemies[0]
    hit(st, a, "pyro", 0)
    for _ in range(4):
        effects.deal_damage_to_enemy(st, a, 3, element="anemo",
                                     source="attack")
    assert len(reactions_logged(st)) == 1


@pytest.mark.usefixtures("both_on")
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


@pytest.mark.usefixtures("both_on")
def test_a_swirl_over_every_enemy_swirls_once(monkeypatch):
    # Venti's Wind's Grand Ode Swirls every enemy at the end of the turn. On
    # the consume rule that was a Swirl per body; now the first spreads spent
    # copies and the rest pay nothing.
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    st = three()
    hit(st, st.enemies[0], "pyro", 0)
    st.player.powers["mc_grand_ode"] = 1
    effects.companion_overhaul_turn_end(st)
    assert len(reactions_logged(st)) == 1
    assert all(e.aura == "pyro" and e.aura_spent for e in st.enemies)


# --- each switch alone (§6 pick 4.4) ----------------------------------------

@pytest.mark.usefixtures("swirl_only")
def test_swirl_alone_leaves_crystallize_consuming_even_a_spent_aura():
    st = make_state()
    e = st.enemies[0]
    hit(st, e, "pyro", 0)
    hit(st, e, "anemo", 0)
    assert e.aura_spent
    hit(st, e, "geo", 0)                    # today's Crystallize: eats it
    assert st.player.block == C.CRYSTALLIZE_BLOCK and e.aura is None


@pytest.mark.usefixtures("crystallize_only")
def test_crystallize_alone_leaves_swirl_consuming_and_spreading_fresh():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, a, "geo", 0)
    assert a.aura_spent and st.player.block == C.CRYSTALLIZE_BLOCK
    hit(st, a, "anemo", 0)                  # today's Swirl, on a spent aura
    assert all(e.aura == "pyro" and not e.aura_spent for e in (a, b, c))
    assert all(e.hp == 30 for e in (a, b, c))              # no flat 2


@pytest.mark.usefixtures("consume_triggers")
def test_both_off_is_todays_consume_and_react():
    st = three()
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, a, "anemo", 0)
    assert all(e.aura == "pyro" and not e.aura_spent for e in (a, b, c))
    assert all(e.aura_turns_left == C.AURA_DURATION_TURNS for e in (a, b, c))
    assert all(e.hp == 30 for e in (a, b, c))
    hit(st, b, "anemo", 0)                  # the copy Swirls again
    assert len(reactions_logged(st)) == 2
    hit(st, c, "geo", 0)
    assert c.aura is None and st.player.block == C.CRYSTALLIZE_BLOCK
    assert not any(ev["event"] == "trigger_spent" for ev in st.log)


# --- the forecast and the event ----------------------------------------------

@pytest.mark.usefixtures("both_on")
def test_trigger_pays_answers_the_preview_question():
    st = make_state()
    e = st.enemies[0]
    assert reactions.trigger_pays(e, "anemo")             # no aura: no claim
    hit(st, e, "hydro", 0)
    assert reactions.trigger_pays(e, "geo")
    hit(st, e, "geo", 0)
    assert not reactions.trigger_pays(e, "geo")
    assert not reactions.trigger_pays(e, "anemo")
    assert reactions.trigger_pays(e, "pyro")              # still Vaporizes


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


# --- the words (§7.1) --------------------------------------------------------

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


def test_the_spent_previews_say_why_a_trigger_pays_nothing():
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    mod = (repo / "klee-mod" / "KleeCode" / "KleeMod.cs").read_text(
        encoding="utf-8")
    for key in ("SWIRL_SPENT_PREVIEW", "CRYSTALLIZE_SPENT_PREVIEW"):
        assert f'"KLEEMOD-{key}.title"' in mod
        assert f'"KLEEMOD-{key}.description"' in mod
    assert "This aura is spent, so [gold]Anemo[/gold] does nothing to it." in mod
    assert "This aura is spent, so [gold]Geo[/gold] does nothing to it." in mod
    aura = (repo / "klee-mod" / "KleeCode" / "Powers" / "AuraPower.cs"
            ).read_text(encoding="utf-8")
    assert "smartDescriptionSpent" in aura and "Spent: " in aura
