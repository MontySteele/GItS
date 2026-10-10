"""Two Furina rulings of 2026-10-10.

Regina of All Waters stops at the Drain line, like a guest's act ("I'm good
with stopping Regina's Drain at the line"): "At the start of your turn,
Drain 3, never past your line. If you do, gain 1 Strength."

Guest Star: Navia moves Rare -> Uncommon ("I lean more towards putting
Navia to Uncommon first"); the pool is 20 / 38 / 20.

C# twin: klee-mod/KleeTests/Prototype/FurinaReginaLineTests.cs.
"""
from __future__ import annotations

from pathlib import Path

from tier0.content import loader
from tier0.engine import furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(__file__).resolve().parents[2]


def _furina(hp: int) -> object:
    st = make_state(enemies=[make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.player.hp = 78
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)              # entered at 78: line 59
    st.player.hp = hp
    st.player.energy = 9
    return st


def test_regina_drains_only_the_room_above_the_line():
    st = _furina(61)
    p = st.player
    assert T.line_hp(p) == 59
    p.powers[FS.REGINA_OF_ALL_WATERS] = 2
    T.turn_start(st)
    assert p.hp == 59                           # 2 of room, not 3 or 6
    assert p.powers.get("strength", 0) == 1     # the second copy found none


def test_regina_at_the_line_drains_nothing():
    st = _furina(59)
    p = st.player
    p.powers[FS.REGINA_OF_ALL_WATERS] = 1
    T.turn_start(st)
    assert p.hp == 59
    assert p.powers.get("strength", 0) == 0


def test_regina_reads_as_ruled_and_navia_is_uncommon():
    rows = {c.id: c for c in loader.prototype_cards()}
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    assert ("Drain[/gold] 3, never past your line. If you do, gain 1"
            in sheet)
    assert rows["proto_fs_guest_star_navia"].rarity == "uncommon"
    assert T.CARDS["ftd_navia"].rarity == "uncommon"
