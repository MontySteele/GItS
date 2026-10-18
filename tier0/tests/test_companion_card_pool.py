"""The shared companions' own pool (legacy review pick 4).

[USER], 2026-10-18 ("Agreed on all 6 legacy picks"): "Shared companions move
to their own pool with a neutral frame, out of Klee's." The mod's
`CompanionCardPool` holds them; the codegen routes a row there by what it IS
(`loader.is_shared_companion_row`), never by its `character:` field, which
every Universal still carries as `klee`.

These pin the three things that must agree: the rows the codegen routes, the
companion offer roster (sim `C.*_OVERHAUL_POOL_IDS`, C#
`CompanionOverhaulRoster`), and the generated pool membership.
"""

import json
import re
from pathlib import Path

from tier0 import constants as C
from tier0.content import loader, yaml_memo
from tools.gen_klee_cards import pascal

REPO = Path(__file__).resolve().parents[2]
CODE = REPO / "klee-mod" / "KleeCode"
GENERATED = CODE / "Cards" / "Prototype" / "Generated"
SHEET = REPO / "docs" / "prototype-surface.yaml"


def _rows() -> list[dict]:
    return [r for r in yaml_memo.safe_load(SHEET.read_text(encoding="utf-8"))
            if isinstance(r, dict) and "id" in r]


def _roster_arm(key: str) -> set[str]:
    src = (GENERATED / "PrototypeRoster.cs").read_text(encoding="utf-8")
    body = src.split(f"private static List<CardModel> Build{pascal(key)}()")[1]
    body = body.split("};")[0]
    return set(re.findall(r"ModelDb\.Card<(\w+)>", body))


def _offer_roster_ids() -> set[str]:
    return set(C.MONDSTADT_OVERHAUL_POOL_IDS + C.INAZUMA_OVERHAUL_POOL_IDS
               + C.FONTAINE_OVERHAUL_POOL_IDS)


def test_the_shared_rows_are_the_offer_roster():
    """Every row the codegen calls shared is on the companion offer roster,
    and every roster card is a shared row: a Universal cannot be framed as a
    companion and offered as nothing, or offered and framed as Klee's."""
    shared = {r["id"] for r in _rows() if loader.is_shared_companion_row(r)}
    assert shared, "the predicate matched nothing"
    assert shared == _offer_roster_ids()


def test_kit_own_and_personal_companions_stay_in_their_kit():
    rows = {r["id"]: r for r in _rows()}
    for cid in C.KIT_OWN_COMPANION_IDS:
        assert "star" in rows[cid], cid
        assert not loader.is_shared_companion_row(rows[cid]), cid
    knights = [r for r in rows.values() if r.get("personal_pool")]
    assert knights, "no Personal rows found -- the fixture moved"
    assert not any(loader.is_shared_companion_row(r) for r in knights)


def _manifest() -> dict:
    return json.loads((GENERATED / "manifest.json").read_text(
        encoding="utf-8"))


def _cards_and_faces(ids) -> set[str]:
    """The classes a set of rows puts in a pool: each row's own, plus its
    choose-one MODE FACES, which ride with it (EB-150) and so wear its frame."""
    faces = _manifest()["mode_faces"]
    out = set()
    for cid in ids:
        out.add(pascal(cid))
        out.update(faces.get(cid, []))
    return out


def test_the_generated_pools_split_companions_out_of_klees():
    companion = _roster_arm("companion")
    klee = _roster_arm("klee")
    assert companion == _cards_and_faces(_offer_roster_ids())
    assert not companion & klee
    # Klee's own three are still hers.
    assert {pascal(cid) for cid in C.KLEE_OWN_COMPANION_IDS} <= klee
    manifest = _manifest()
    assert set(manifest["companion_pool"]) == _offer_roster_ids()
    # The EMITTING owner does not move: art path and text stay Klee's profile.
    assert all(manifest["owners"][cid] == "klee"
               for cid in manifest["companion_pool"])


def test_the_csharp_offer_roster_lists_exactly_the_pool():
    """`CompanionOverhaulRoster` (the offer) lists by type; the pool is
    generated. Both must name the same classes."""
    src = (CODE / "Powers" / "Prototype" / "CompanionOverhaulRoster.cs"
           ).read_text(encoding="utf-8")
    listed = set(re.findall(r"ModelDb\.Card<(\w+)>", src))
    assert _cards_and_faces(_offer_roster_ids()) == _roster_arm("companion")
    assert listed == {pascal(cid) for cid in _offer_roster_ids()}


def test_the_pool_wears_the_colorless_look():
    body = (CODE / "CompanionCardPool.cs").read_text(encoding="utf-8")
    assert 'EnergyColorName => "colorless";' in body
    assert 'CardFrameMaterialPath => "card_frame_colorless";' in body
    assert 'PrototypeCards.For("companion")' in body
    assert "CompanionPool.All" in body
