"""`yaml.safe_load`, memoised on the exact text. Same data, parsed once.

WHY (2026-09-28, the CI speed pass). PyYAML's pure-Python parser was about
45% of the whole test suite's time: 387 s of 863 s summed over the workers,
measured by wrapping `yaml.safe_load` for one full run. Almost all of it was
the same few sheets parsed again and again -- `prototype_cards` alone parsed
36 distinct texts 485 times, because `reset_caches` and the tests' fixture
sheets make the per-function `lru_cache`s start cold over and over.

WHAT IT PROMISES, and why each half holds:

  * THE SAME DATA. The key is the text itself, not a path or an mtime, so a
    changed file is a different key and a stale answer is impossible by
    construction. A miss calls `yaml.safe_load` -- the same pure-Python
    `SafeLoader` as before, not libyaml's `CSafeLoader` -- so a parse error
    raises exactly the exception it always raised, and nothing is stored.
  * NO SHARED STATE. The parsed object is never handed out: every call,
    hit or miss, returns `copy.deepcopy` of it, so a caller that mutates what
    it got (`_card_index` does `setdefault` on every row) mutates its own copy,
    exactly as it did with a fresh parse. `deepcopy` keeps anchors/aliases
    aliased the way the parser left them. A deep copy of the largest sheet
    (`prototype-surface.yaml`, 142 KB) costs about 1 ms against a 150 ms parse.

Non-text input (a stream) is passed straight through, unmemoised.

ONE OF TWO COPIES, on purpose: `understudy/yaml_memo.py` is the other.
`understudy/authorship.py` and `understudy/resource_order.py` are imported by
the blind seat, and a blind-seat module may not import anything under `tier0`
(the no-leak pin in `tier0/tests/test_understudy_blindplay.py`), while
nothing in `tier0` imports `understudy`. `tier0/tests/test_yaml_memo.py`
holds the two copies to the same source.
"""

from __future__ import annotations

import copy
from collections import OrderedDict
from typing import Any

import yaml

#: Distinct texts kept. The repo's sheets number a few hundred; a test that
#: writes fixture sheets to tmp_path adds one entry per fixture and ages out.
MAX_ENTRIES = 512

_MEMO: "OrderedDict[str, Any]" = OrderedDict()


def safe_load(text: Any) -> Any:
    """`yaml.safe_load(text)`, parsed once per distinct text; a fresh copy
    every call."""
    if not isinstance(text, str):
        return yaml.safe_load(text)
    try:
        master = _MEMO[text]
    except KeyError:
        master = yaml.safe_load(text)      # raises as before; nothing stored
        _MEMO[text] = master
        if len(_MEMO) > MAX_ENTRIES:
            _MEMO.popitem(last=False)
    else:
        _MEMO.move_to_end(text)
    return copy.deepcopy(master)


def clear() -> None:
    """Forget every parsed text (tests only; nothing needs it for freshness)."""
    _MEMO.clear()
