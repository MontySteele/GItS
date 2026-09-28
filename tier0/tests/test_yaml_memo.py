"""The YAML memo returns exactly what `yaml.safe_load` returns, every time.

`tier0/content/yaml_memo.py` (and its copy `understudy/yaml_memo.py`) exist
for speed only -- the 2026-09-28 CI speed pass. These pins are what lets a
reader believe "speed only": the data is the same, byte for byte, on every
committed sheet; a caller that mutates its answer cannot reach the next
caller's; a bad document raises what it always raised; and the two copies
cannot drift apart.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest
import yaml

from tier0.content import yaml_memo
from understudy import yaml_memo as understudy_yaml_memo

REPO = Path(__file__).resolve().parents[2]
ROOTS = ("docs", "tier0", "tier05", "understudy", "tools", "review")


def _committed_yaml() -> list[Path]:
    out: list[Path] = []
    for root in ROOTS:
        for pattern in ("*.yaml", "*.yml"):
            out.extend(p for p in (REPO / root).rglob(pattern)
                       if "__pycache__" not in p.parts)
    return sorted(set(out))


def test_every_committed_sheet_loads_to_the_same_data():
    """`repr` is the strict comparison on purpose: it tells `True` from `1`,
    `1.0` from `1`, a date from a string, and key order within a mapping --
    all things `==` alone would forgive."""
    paths = _committed_yaml()
    assert len(paths) >= 100, f"only {len(paths)} sheets found -- pin is stale"
    yaml_memo.clear()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        want = repr(yaml.safe_load(text))
        assert repr(yaml_memo.safe_load(text)) == want, path     # a miss
        assert repr(yaml_memo.safe_load(text)) == want, path     # a hit


def test_a_caller_that_mutates_its_answer_cannot_reach_the_next_caller():
    text = ("- id: a\n  tags: [x]\n  effects: [{op: deal, n: 3}]\n"
            "- &shared {k: 1}\n- *shared\n")
    yaml_memo.clear()
    first = yaml_memo.safe_load(text)
    first[0]["tags"].append("MUTATED")
    first[0]["effects"][0]["n"] = 99
    first[1]["k"] = 2
    first.append("extra")
    second = yaml_memo.safe_load(text)
    assert second == yaml.safe_load(text)
    assert second is not first
    # An alias stays an alias, as the parser leaves it.
    assert second[1] is second[2]


def test_a_bad_document_raises_what_it_always_raised_and_is_not_kept():
    bad = "a: [1, 2\nb: 3\n"
    with pytest.raises(yaml.YAMLError) as plain:
        yaml.safe_load(bad)
    yaml_memo.clear()
    for _ in range(2):
        with pytest.raises(type(plain.value)) as memo:
            yaml_memo.safe_load(bad)
        assert str(memo.value) == str(plain.value)
    assert bad not in yaml_memo._MEMO


def test_a_stream_is_passed_straight_through():
    path = _committed_yaml()[0]
    with path.open(encoding="utf-8") as fh:
        got = yaml_memo.safe_load(fh)
    assert repr(got) == repr(yaml.safe_load(path.read_text(encoding="utf-8")))


def test_the_memo_is_bounded():
    yaml_memo.clear()
    for i in range(yaml_memo.MAX_ENTRIES + 10):
        yaml_memo.safe_load(f"n: {i}\n")
    assert len(yaml_memo._MEMO) == yaml_memo.MAX_ENTRIES
    yaml_memo.clear()


def test_the_two_copies_are_the_same_code():
    """Two copies because a blind-seat module may not import `tier0` (see the
    module docstring); held identical here so they cannot drift."""
    for name in ("safe_load", "clear"):
        assert (inspect.getsource(getattr(yaml_memo, name))
                == inspect.getsource(getattr(understudy_yaml_memo, name)))
    assert yaml_memo.MAX_ENTRIES == understudy_yaml_memo.MAX_ENTRIES
