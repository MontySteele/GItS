"""EB-249: what the distinctness instrument reads, both halves.

(a) THE INPUT. Every companion nation has to be measured: the instrument once
read Mondstadt's sheet and nothing else, and an absent pool reads as coverage.
Since legacy cleanup stage 6 (2026-10-01) the house pools are cut from the
prototype surface (`cdr.surface_pools`), the shipped sheets being deleted.

(b) THE TAXONOMY. The metric measures the DRAFTABLE UNIVERSAL pool. Personal
rows (a `personal_pool` field: Varka's Knights, Klee's coven, the stand-ins)
and `guest_star` rows (the Fontaine cameos) are not in that pool, and counting
them would put cards no player can draft inside a ratio about drafting.
"""

from tools import card_distinctness_report as cdr


def _pools():
    return dict(cdr.surface_pools())


def test_every_companion_nation_is_measured_and_named():
    """(a)."""
    names = {r["pool"] for r in cdr.build_reports()}
    assert {"mondstadt-companions", "fontaine-companions",
            "inazuma-companions"} <= names


def test_personal_rows_are_not_in_the_universal_pool():
    """(b), Mondstadt's half: the nation's rows carry Personals (stand-ins,
    Knights, the coven); the universal pool is the companion roster's 34."""
    rows = _pools()["mondstadt-companions"]
    assert any(r.get("personal_pool") for r in rows)
    # 35 since Durin split in two (AoE trim, 2026-10-03).
    assert len(cdr.universal_rows(rows)) == 35


def test_guest_stars_are_not_in_the_universal_pool():
    """(b), Fontaine's half: three of nineteen rows are generated cameos."""
    rows = _pools()["fontaine-companions"]
    assert len(rows) == 19
    assert len(cdr.universal_rows(rows)) == 16


def test_the_kit_pools_are_the_pinned_78_and_untouched_by_the_filter():
    """The control. No kit row carries either field, so the filter takes
    nothing off -- and each pool is the 78 `PoolCountTests` pins."""
    pools = _pools()
    for ch in ("klee", "kokomi", "furina"):
        assert len(pools[ch]) == 78, ch
        assert len(cdr.universal_rows(pools[ch])) == 78, ch


def test_no_companion_pool_breaches_the_gate():
    breaches, _ = cdr.gate_breaches(cdr.build_reports())
    assert not [b for b in breaches if b[0].endswith("-companions")]
