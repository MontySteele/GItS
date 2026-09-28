"""The CI shard split can make a shard slower, never make a test not run.

`tools/ci_shards.py` splits `tier0/tests` + `tier05/tests` by file for the
four-runner `pytest` matrix in `.github/workflows/repo.yml`. The full
node-level proof (`--verify`: the shards' collections are disjoint and their
union is the full collection) runs in the `lints` job, because it needs five
`pytest --collect-only` passes. These are its cheap halves: the partition
itself, its fail-safe cases, and the workflow agreeing with itself about N.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools import ci_shards

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "repo.yml"


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8])
def test_the_shards_are_disjoint_and_their_union_is_every_test_file(n):
    files = ci_shards.discover()
    assert len(files) > 300, "discovery found too little -- pin is stale"
    shards = ci_shards.partition(files, ci_shards.load_durations(), n)
    assert len(shards) == n
    flat = [f for s in shards for f in s]
    assert len(flat) == len(set(flat)), "a file is in two shards"
    assert sorted(flat) == files


def test_discovery_finds_this_file_and_both_roots():
    files = ci_shards.discover()
    assert "tier0/tests/test_ci_shards.py" in files
    assert any(f.startswith("tier05/tests/") for f in files)
    assert not [f for f in files if not Path(f).name.startswith("test_")
                and not f.endswith("_test.py")]


def test_an_untimed_file_still_lands_in_a_shard_and_a_stale_entry_is_ignored():
    files = ["a/test_known.py", "a/test_new.py", "a/test_other.py"]
    durations = {"a/test_known.py": 10.0, "a/test_other.py": 1.0,
                 "a/test_deleted.py": 999.0}
    shards = ci_shards.partition(files, durations, 2)
    assert sorted(f for s in shards for f in s) == sorted(files)


def test_the_split_is_deterministic_and_heaviest_first():
    durations = ci_shards.load_durations()
    files = ci_shards.discover()
    a = ci_shards.partition(files, durations, 4)
    assert a == ci_shards.partition(list(reversed(files)), durations, 4)
    for shard in a:
        weights = [durations.get(f, 0.0) for f in shard if f in durations]
        assert weights == sorted(weights, reverse=True)


def test_an_empty_shard_is_refused_rather_than_run(monkeypatch):
    """`pytest` with no path collects the whole repository, not nothing."""
    monkeypatch.setattr(ci_shards, "discover", lambda: ["a/test_only.py"])
    assert ci_shards.shard_files(1, 2) == ["a/test_only.py"]
    with pytest.raises(SystemExit):
        ci_shards.shard_files(2, 2)
    with pytest.raises(SystemExit):
        ci_shards.shard_files(3, 2)


def test_the_workflow_agrees_with_itself_about_the_shard_count():
    text = WORKFLOW.read_text(encoding="utf-8")
    matrix = re.search(r"^\s+shard: \[([0-9, ]+)\]\s*$", text, re.M)
    assert matrix, "the pytest matrix is gone"
    listed = [int(x) for x in matrix.group(1).split(",")]
    n = len(listed)
    assert listed == list(range(1, n + 1))
    ofs = {int(x) for x in re.findall(r"ci_shards\.py[^\n]*--of (\d+)", text)}
    assert ofs == {n}, ofs
    assert "--verify" in text, "the lints job's shard audit is gone"
    assert f"name: pytest (${{{{ matrix.shard }}}}/{n})" in text
