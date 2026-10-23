"""THE RELEASE FIXES (2026-10-14): Furina's faces, no rule changes.

1. A face that says "below half" prints the threshold in combat, "below half
   (39 HP)", through the base game's `{InCombat:...|}` seam
   (`gen_klee_cards.half_hp_face_lines`, C# `HalfHpFace`).
2. Every "Spend up to X" has no chooser; the Spend tip says it pays all it
   can (", all you can" left the faces in the Furina text audit, 2026-10-23).

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


def test_no_spend_up_to_repeats_the_tip():
    rows = _rows()
    ups = [rid for rid, row in rows.items()
           if "[gold]Spend[/gold] up to" in (row.get("description") or "")]
    # furina-next paper 2 (2026-10-16): Bravura spends up to a cap (Bring
    # the House Down did until the upgrade census, 2026-10-23); Extended Run
    # names the clause and spends nothing.
    assert sorted(ups) == ["proto_fs_bis", "proto_fs_bravura",
                           "proto_fs_crashing_waves", "proto_fs_hold_the_stage",
                           "proto_fs_the_full_house", "proto_fs_tidal_flourish"]
    for rid in ups:
        if rid == "proto_fs_bis":
            continue
        # Furina text audit (2026-10-23), pick 2: the Spend tip carries it.
        assert "all you can" not in rows[rid]["description"], rid
