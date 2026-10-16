"""THE RELEASE FIXES (2026-10-14): Furina's faces, no rule changes.

1. A face that says "below half" prints the threshold in combat, "below half
   (39 HP)", through the base game's `{InCombat:...|}` seam
   (`gen_klee_cards.half_hp_face_lines`, C# `HalfHpFace`).
2. Every "Spend up to X" says it spends all it can, with no chooser.

The C# twin is `klee-mod/KleeTests/Prototype/ReleaseFixesKkVkFsTests.cs`.
"""
from __future__ import annotations

from tier0.tests.test_arm_keyword_tips import PROTOTYPE_DIR, gen, proto


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in proto._rows()}


def test_every_below_half_face_carries_its_number():
    rows = _rows()
    for rid in ("proto_fs_understudys_debut", "proto_fs_crowd_favorite"):
        desc, args = gen.half_hp_face_lines(rows[rid], rows[rid]["description"])
        assert "below half{InCombat:{HalfHp}|}" in desc, rid
        assert args == [("HalfHp", "HalfHpFace.Line(this)")], rid
    # "below half HP" keeps "HP" out of combat only.
    row = rows["proto_mc_noelle_breastplate"]
    desc, _ = gen.half_hp_face_lines(row, row["description"])
    assert "below half{InCombat:{HalfHp}| HP}" in desc
    # Derived from the face: every row that prints the words, and no other.
    for rid, row in rows.items():
        _, args = gen.half_hp_face_lines(row, row.get("description") or "")
        assert bool(args) == ("below half" in (row.get("description") or "")), rid


def test_generated_faces_print_the_number():
    src = (PROTOTYPE_DIR / "ProtoFsUnderstudysDebut.cs").read_text(
        encoding="utf-8")
    assert "below half{InCombat:{HalfHp}|}" in src
    assert 'description.Add("HalfHp", HalfHpFace.Line(this));' in src


def test_every_spend_up_to_spends_all_it_can():
    rows = _rows()
    ups = [rid for rid, row in rows.items()
           if "[gold]Spend[/gold] up to" in (row.get("description") or "")]
    assert sorted(ups) == ["proto_fs_crashing_waves", "proto_fs_hold_the_stage",
                           "proto_fs_the_full_house", "proto_fs_tidal_flourish"]
    for rid in ups:
        assert ", all you can:" in rows[rid]["description"], rid
