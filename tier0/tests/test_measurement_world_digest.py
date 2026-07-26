"""game_ref/ participates in the measurement-world provenance digest.

WHY: on 2026-07-22/23 a measurement world diverged between two machines whose
world lines matched, because the provenance digest hashed only
``git diff --binary`` over tracked files -- gitignored game_ref/ content was
invisible to it. Both measurement tools now print a ``game_ref=`` digest over
every ``*.yaml`` in game_ref/; these tests pin that two machines with
different game_ref content produce different digests and that absence hashes
distinctly.
"""

from __future__ import annotations

import pytest

from tier0.content import local_reference
from tools import klee_survival_sprint, real_battery_calibration

DIGESTS = pytest.mark.parametrize(
    "game_ref_digest",
    [real_battery_calibration._game_ref_digest,
     klee_survival_sprint._game_ref_digest],
    ids=["real_battery_calibration", "klee_survival_sprint"],
)


@pytest.fixture(autouse=True)
def _isolated_game_ref(tmp_path, monkeypatch):
    """Point the loader's game_ref selection at a temp dir, auto mode."""
    monkeypatch.delenv(local_reference.REFERENCE_MODE_ENV, raising=False)
    monkeypatch.setattr(
        local_reference, "DEFAULT_GAME_REF_DIR", tmp_path / "game_ref")
    return tmp_path / "game_ref"


@DIGESTS
def test_absent_directory_is_labeled_not_hashed(game_ref_digest):
    assert game_ref_digest() == "absent"


@DIGESTS
def test_content_difference_changes_digest(
        game_ref_digest, _isolated_game_ref):
    ref = _isolated_game_ref
    ref.mkdir()
    (ref / "ironclad_pool.yaml").write_text("hp: 80\n")
    machine_a = game_ref_digest()

    (ref / "ironclad_pool.yaml").write_text("hp: 82\n")
    machine_b = game_ref_digest()

    assert machine_a != machine_b
    assert machine_a not in {"absent", "committed-only"}
    assert len(machine_a) == 12


@DIGESTS
def test_file_set_difference_changes_digest(
        game_ref_digest, _isolated_game_ref):
    ref = _isolated_game_ref
    ref.mkdir()
    (ref / "ironclad_pool.yaml").write_text("hp: 80\n")
    base = game_ref_digest()

    (ref / "ironclad_pool_pass4.yaml").write_text("hp: 80\n")
    layered = game_ref_digest()

    assert base != layered


@DIGESTS
def test_empty_directory_differs_from_absent(
        game_ref_digest, _isolated_game_ref):
    _isolated_game_ref.mkdir()
    empty = game_ref_digest()
    assert empty != "absent"
    assert len(empty) == 12


@DIGESTS
def test_committed_only_mode_is_labeled(
        game_ref_digest, _isolated_game_ref, monkeypatch):
    ref = _isolated_game_ref
    ref.mkdir()
    (ref / "ironclad_pool.yaml").write_text("hp: 80\n")
    monkeypatch.setenv(
        local_reference.REFERENCE_MODE_ENV, local_reference.COMMITTED_ONLY)
    assert game_ref_digest() == "committed-only"
