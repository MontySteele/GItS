"""Furina, the Stage: her Hydro attack modes deal Hydro damage (the seat round
of 2026-09-26, act 2 lane 2).

THE FIND. Quick Cue's Spend mode ("deal 8 and apply Hydro") hit an enemy
wearing Pyro: Vaporize was listed, the damage landed at face value. The row
resolved `damage` and then `apply_aura`, so the reaction fired on the
application, after the hit, and multiplied nothing -- and Courtroom Drama
("Your first Elemental Reaction each turn applies 1 Vulnerable and 1 Weak to
its target before the hit lands") landed after the hit too.

THE RULING. Every Furina prototype row whose face says "deal N ... and apply
Hydro" to the same target makes that damage a Hydro hit (`applies_element:
true`, the mechanism Klee's rows use). Bubble Aria's FIRST hit carries it
(`element_hits: 1`). The mod's pins are
`klee-mod/KleeTests/Prototype/FurinaHydroHitsTests.cs`.
"""

import copy
import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, furina_stage as FS
from tier0.engine.state import CombatState, Enemy, Player
from tools.effect_walk import iter_effects  # noqa: E402


@pytest.fixture
def arm(monkeypatch):
    yield


def _state(stage=("usher",), fanfare=5, enemies=None, cross_examination=0):
    # `element: hydro` is the character sheet's (docs' furina character
    # yaml); the loader hands it to every real Furina.
    player = Player(hp=200, max_hp=200, fanfare_cap=99,
                    character_id="furina", element="hydro")
    st = CombatState(player=player, enemies=enemies or [_enemy()],
                     rng=random.Random(0))
    st.turn = 2
    st.player.stage = list(stage)
    st.player.stage_fanfare = fanfare       # enough for any Spend mode here
    if cross_examination:
        st.player.powers["cross_examination"] = cross_examination
    return st


def _enemy(hp=200, name="paper", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    e.aura = aura
    return e


def _play(st, cid, mode=None, monkeypatch=None, upgraded=False):
    card = loader.get_card(cid)
    if upgraded:
        # The row's `damage: +N`, bound as `upgrades` binds it: the first
        # top-level damage op -- which is the ONE op, both hits included.
        card = copy.deepcopy(card)
        next(fx for fx in card.effects
             if fx.get("op") == "damage")["amount"] += card.upgrade["damage"]
    if mode is not None:
        monkeypatch.setattr(FS, "spend_mode_index", lambda state, modes: mode)
    effects.resolve_card(st, card)


VAPORIZED_11 = int(11 * C.VAPORIZE_MULT)


# ---------------------------------------------------------------------------
# THE FINDING: Vaporize off Quick Cue's Spend mode multiplies its 11 (8
# until the 2026-09-28 Spend pass, 14 from the 2026-09-29 fade pass until the
# 2026-10-01 rules pass).
# ---------------------------------------------------------------------------

def test_vaporize_off_quick_cues_spend_mode_multiplies_its_hit(
        arm, monkeypatch):
    st = _state(enemies=[_enemy(aura="pyro")])
    _play(st, "proto_fs_quick_cue", 1, monkeypatch)
    assert st.enemies[0].hp == 200 - VAPORIZED_11
    assert VAPORIZED_11 > 11
    assert st.enemies[0].aura is None           # consumed by the hit
    reactions = [e for e in st.log if e["event"] == "reaction"]
    assert [r["reaction"] for r in reactions] == ["vaporize"]


def test_quick_cues_plain_mode_is_still_a_plain_hit(arm, monkeypatch):
    st = _state(enemies=[_enemy(aura="pyro")])
    _play(st, "proto_fs_quick_cue", 0, monkeypatch)
    assert st.enemies[0].hp == 200 - 3
    assert st.enemies[0].aura == "pyro"


def test_courtroom_dramas_vulnerable_lands_on_the_reacting_hit(
        arm, monkeypatch):
    st = _state(enemies=[_enemy(aura="pyro")], cross_examination=1)
    st.reactions_this_turn = 0
    _play(st, "proto_fs_quick_cue", 1, monkeypatch)
    # 11 x Vaporize x the Vulnerable Courtroom Drama put on it before it landed.
    assert st.enemies[0].hp == 200 - int(
        11 * C.VAPORIZE_MULT * C.VULNERABLE_TAKEN_MULT)
    assert st.enemies[0].powers.get("vulnerable", 0) >= 1
    assert st.enemies[0].powers.get("weak", 0) >= 1


def test_tidal_flourishs_spend_mode_vaporizes_every_pyro_body(
        arm, monkeypatch):
    st = _state(enemies=[_enemy(aura="pyro"), _enemy(name="b", aura="pyro"),
                         _enemy(name="c")])
    _play(st, "proto_fs_tidal_flourish", 1, monkeypatch)
    vaporized = int(13 * C.VAPORIZE_MULT)          # 13 since the fade pass
    assert [e.hp for e in st.enemies] == [200 - vaporized, 200 - vaporized,
                                         200 - 13]
    assert [e.aura for e in st.enemies] == [None, None, "hydro"]


def test_bubble_arias_first_hit_carries_hydro_and_its_second_is_plain(arm):
    st = _state(enemies=[_enemy(aura="pyro")])
    _play(st, "proto_fs_bubble_aria")
    # The first 4 is Vaporized; the second meets a bare body and applies
    # nothing, so the Pyro it consumed is not replaced.
    assert st.enemies[0].hp == 200 - int(4 * C.VAPORIZE_MULT) - 4
    assert st.enemies[0].aura is None
    clean = _state()
    _play(clean, "proto_fs_bubble_aria")
    assert clean.enemies[0].hp == 200 - 8
    assert clean.enemies[0].aura == "hydro"
    # Upgraded, both hits move (the one var): 5 and 5.
    up = _state()
    _play(up, "proto_fs_bubble_aria", upgraded=True)
    assert up.enemies[0].hp == 200 - 10


def test_grand_deluges_hit_is_the_reaction_that_gains_fanfare(arm):
    st = _state(stage=("usher", "crabaletta"), fanfare=0,
                enemies=[_enemy(aura="pyro"), _enemy(name="b")])
    _play(st, "proto_fs_grand_deluge")
    # 12 to ALL since the 2026-09-29 audit pass (was 10).
    assert [e.hp for e in st.enemies] == [200 - int(12 * C.VAPORIZE_MULT),
                                         200 - 12]
    assert [e.aura for e in st.enemies] == [None, "hydro"]
    # The re-founded sheet (2026-10-04): "On an Elemental Reaction, gain 4
    # Fanfare" -- Furina's one number.
    assert st.player.stage_fanfare == 4


# ---------------------------------------------------------------------------
# THE SHEET: no Furina row applies Hydro after a hit on the same target.
# ---------------------------------------------------------------------------

def _effect_lists(effects_):
    """Every effect LIST in the tree: the top level, each branch, each mode."""
    yield effects_
    for fx in effects_ or []:
        for key in ("then", "else"):
            if fx.get(key):
                yield from _effect_lists(fx[key])
        for mode in fx.get("modes") or []:
            yield from _effect_lists(mode.get("effects"))


def _furina_proto_rows():
    import yaml
    rows = yaml.safe_load(
        (loader.DOCS_DIR / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    return [r for r in rows if str(r["id"]).startswith("proto_fs_")]


def test_no_furina_row_applies_hydro_after_a_hit_on_the_same_target():
    offenders = []
    for row in _furina_proto_rows():
        for effects_ in _effect_lists(row.get("effects")):
            hit = set()
            for fx in effects_ or []:
                if fx.get("op") == "damage":
                    hit.add(fx.get("target"))
                elif (fx.get("op") == "apply_aura"
                      and fx.get("target") in hit):
                    offenders.append(row["id"])
    assert offenders == []


def test_the_four_hydro_attacks_carry_it_on_the_hit():
    carried = {}
    for row in _furina_proto_rows():
        for fx in iter_effects(row.get("effects") or []):
            if fx.get("op") == "damage" and fx.get("applies_element"):
                carried[row["id"]] = fx.get("element_hits")
    assert carried == {"proto_fs_tidal_flourish": None,
                       "proto_fs_quick_cue": None,
                       "proto_fs_bubble_aria": 1,
                       "proto_fs_grand_deluge": None}
