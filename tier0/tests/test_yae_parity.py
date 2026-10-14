"""YAE MIKO: the sim twin and the C# agree (built 2026-10-13).

Varka's parity is three seams, and hers are the same three:

  1. THE NUMBERS. `YaeLaw` mirrors `tier0/engine/yae_shrine.py` by value
     (`tools/lint_constant_parity.py`, run here too so a drift fails this
     file by name).
  2. THE GRAMMAR. The `yae` op's kinds, the numeric fields each prints, the
     kinds that aim, and the five Annotation names are one table in each
     engine (`yae_shrine.KIND_FIELDS` and `gen_klee_cards.YAE_KIND_FIELDS`);
     every kind names a `YaeCards` method the C# defines, every Annotation a
     `YaeAnnotation` member.
  3. THE ROWS. Every `proto_ym_` row's generated class carries its printed
     numbers as `Ym*` vars, its upgrade as the same deltas the sim applies,
     and the starter and pool the C# roster lists are the sim's.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402

from tier0.content import loader                # noqa: E402
from tier0.engine import yae_shrine as Y        # noqa: E402

CODE = REPO / "klee-mod" / "KleeCode"
SHRINE_CS = CODE / "Powers" / "Prototype" / "YaeShrine.cs"
ANNOTATIONS_CS = CODE / "Powers" / "Prototype" / "YaeAnnotations.cs"
ROSTER_CS = CODE / "Powers" / "Prototype" / "YaeRoster.cs"
LAW_CS = CODE / "Powers" / "Prototype" / "YaePrototype.cs"
GENERATED = CODE / "Cards" / "Prototype" / "Generated"


def _rows() -> list:
    return [c for c in loader.prototype_cards() if c.id.startswith(Y.ID_PREFIX)]


def test_the_law_numbers_mirror_the_sim():
    text = LAW_CS.read_text(encoding="utf-8")
    law = dict(re.findall(r"public const int (\w+) = (\d+);", text))
    assert {k: int(v) for k, v in law.items()} == {
        "SakuraCap": Y.SAKURA_CAP, "SakuraTurns": Y.SAKURA_TURNS,
        "SakuraBase": Y.SAKURA_BASE, "PlantLevel": Y.PLANT_LEVEL,
        "RedInkAmount": Y.RED_INK_AMOUNT, "FoxFireDamage": Y.FOX_FIRE_DAMAGE,
        "OfferingPerStrike": Y.OFFERING_DRAW,
        "RoyaltiesPayout": Y.ROYALTIES_ENERGY,
    }


def test_the_constant_parity_lint_holds():
    out = subprocess.run([sys.executable, str(REPO / "tools"
                                              / "lint_constant_parity.py")],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "YaeLaw" not in out.stdout


def test_the_op_grammar_is_one_table_in_each_engine():
    assert gen.YAE_KIND_FIELDS == Y.KIND_FIELDS
    assert set(gen.YAE_KINDS) == set(Y.KINDS)
    assert gen.YAE_AIMED_KINDS == {k for k, t in Y.KIND_TARGETS.items()
                                   if t == "enemy"}
    assert gen.YAE_ANNOTATION_KINDS == set(Y.ANNOTATION_KINDS)
    assert set(gen.YAE_ANNOTATIONS) == set(Y.ANNOTATIONS)
    # Shrine r2 (2026-10-14): the typed Tenko kinds; the design axes: the
    # Sakura readings, the ends.
    assert set(gen.YAE_TENKO_KINDS) == set(Y.TENKO_NAME)
    assert set(Y.TENKO_NAME) == set(Y.TENKO_KINDS) - {Y.THUNDER}
    assert gen.YAE_SAKURA_ANNOTATIONS == set(Y.SAKURA_ANNOTATIONS)
    assert set(gen.YAE_SAKURA_ENDS) == set(Y.SAKURA_EDIT_ENDS)


def test_every_kind_is_a_yaecards_method_and_every_annotation_a_member():
    shrine = SHRINE_CS.read_text(encoding="utf-8")
    for method in gen.YAE_KINDS.values():
        assert re.search(rf"public static (?:async )?Task {method}\(", shrine), method
    members = ANNOTATIONS_CS.read_text(encoding="utf-8")
    for member in gen.YAE_ANNOTATIONS.values():
        assert re.search(rf"\b{member} = \d+,", members), member
    for member in list(gen.YAE_TENKO_KINDS.values()) + list(gen.YAE_SAKURA_ENDS.values()):
        assert re.search(rf"\b{member} = \d+,", shrine), member


def test_every_power_her_rows_apply_is_a_class():
    text = (CODE / "Powers" / "Prototype" / "YaePowers.cs").read_text(
        encoding="utf-8")
    for name in (Y.SAKURA_GROVE, Y.EDICT, Y.SERIALIZATION, Y.MOONCALL,
                 Y.YAKAN_OFFERING, Y.CHANNELING, Y.EDITOR_IN_CHIEF,
                 Y.FALLEN_PETALS, Y.FALLEN_PETALS_PLUS):
        cls = gen.APPLY_POWERS[name][0]
        assert f"class {cls} " in text, cls


def _class_file(card_id: str) -> str:
    return (GENERATED / f"{gen.pascal(card_id)}.cs").read_text(encoding="utf-8")


@pytest.mark.parametrize("card", _rows(), ids=lambda c: c.id)
def test_each_row_carries_its_numbers_and_upgrade_into_the_class(card):
    text = _class_file(card.id)
    for fx in card.effects:
        if fx.get("op") != "yae":
            continue
        for field in Y.KIND_FIELDS[fx["kind"]]:
            var = gen.YAE_VAR_FIELDS[field]
            if f'"{var}"' not in text:
                # No var: the reader's default is the row's number.
                assert fx[field] == gen.YAE_FIELD_DEFAULTS[field], (var, fx)
                continue
            assert f'new DynamicVar("{var}", {fx[field]}m)' in text, (var, fx)
    up = loader.get_card(card.id + "+")
    for base, plus in zip(card.effects, up.effects):
        if base.get("op") != "yae":
            continue
        for field in Y.KIND_FIELDS[base["kind"]]:
            delta = plus[field] - base[field]
            var = gen.YAE_VAR_FIELDS[field]
            if delta:
                assert (f'DynamicVars["{var}"].UpgradeValueBy({delta}m);'
                        in text), (card.id, var, delta)


def test_the_roster_lists_the_sims_starter_and_the_forty():
    text = ROSTER_CS.read_text(encoding="utf-8")
    pool = re.search(r"Pool\(\) => new CardModel\[\]\s*\{(.*?)\n\s*\};",
                     text, re.S).group(1)
    listed = [gen.pascal(c.id) for c in _rows() if c.rarity != "basic"]
    named = re.findall(r"ModelDb\.Card<(\w+)>", pool)
    assert named == listed
    assert len(named) == 40
    starter = re.search(r"StartingDeck\(\) => new CardModel\[\]\s*\{(.*?)\n\s*\};",
                        text, re.S).group(1)
    own = [n for n in re.findall(r"ModelDb\.Card<(\w+)>", starter)
           if n.startswith("ProtoYm")]
    assert own == [gen.pascal(i) for i in Y.STARTER_IDS if i.startswith("proto_")]


def test_her_companion_is_hidden_from_her_in_both_engines():
    assert Y.hidden_from("proto_mi_yae_sesshou_sakura", "yae")
    assert not Y.hidden_from("proto_mi_yae_sesshou_sakura", "klee")
    pool = (CODE / "CompanionPool.cs").read_text(encoding="utf-8")
    assert "ProtoMiYaeSesshouSakura" in pool
