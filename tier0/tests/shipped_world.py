"""THE SHIPPED WORLD, NAMED: the four kit arms off for one test.

Since legacy cleanup stage 3 (2026-10-01,
`review/active/legacy-cleanup-2026-10-01.md`, pick 5) the sim's defaults are
the current kits: `KLEE_OVERHAUL`, `KOKOMI_OVERHAUL`, `COMPANION_OVERHAUL` and
`furina_stage.FURINA_STAGE` are on. A test that pins the OLD shipped kits says
so with this fixture, so it keeps saying one true thing whichever way the
defaults point -- the `consume_triggers` arrangement, for the arms.

Imported into both conftests (`tier0/tests`, `tier05/tests`). A whole module
takes it with `pytestmark = pytest.mark.usefixtures("shipped_world")`; a test
that then wants an arm on still gets it, because `usefixtures` runs before the
test's own fixtures and body. It goes with the shipped kits (stage 5).

Every memoized view that moves with an arm is dropped going in and coming out,
so a cache warmed in the shipped world never reaches the next test.
"""

from __future__ import annotations

import pytest

_CONSTANT_ARMS = ("KLEE_OVERHAUL", "KOKOMI_OVERHAUL", "COMPANION_OVERHAUL")


def _read_defaults() -> dict[str, bool]:
    from tier0 import constants as C
    from tier0.engine import furina_stage
    out = {flag: getattr(C, flag) for flag in _CONSTANT_ARMS}
    out["FURINA_STAGE"] = furina_stage.FURINA_STAGE
    return out


#: Each kit arm's value AS SHIPPED IN THE MODULE, read when the conftests
#: import this file (before any test can flip one). The "the arm ships on"
#: pins read this, because inside `shipped_world` the live attribute is False.
DEFAULTS = _read_defaults()

#: THE CALIBRATION IS RETIRED (legacy cleanup pick 5, ruled 2026-10-01):
#: "tier0 calibration is retired until a kit reaches Balance, then
#: re-measured on the current kits." The frozen bands and scorecards were
#: measured on the shipped kits; they skip, they are not re-banded.
RETIRED_CALIBRATION = pytest.mark.skip(
    reason="calibration retired until a kit reaches Balance, 2026-10-01 "
           "(review/active/legacy-cleanup-2026-10-01.md, pick 5)")


def drop_arm_caches() -> None:
    """Every memoized view whose answer moves with an arm flag, both engines."""
    from tier0.content import loader
    from tier0.engine import companion_standins
    loader.reset_arm_caches()
    getattr(companion_standins._replacements, "cache_clear", lambda: None)()
    try:
        from tier05 import rewards
    except ImportError:  # pragma: no cover - tier05 always ships beside tier0
        return
    for name in ("character_pool", "companion_pool", "_companion_roster",
                 "designed_nations", "five_star_roster"):
        fn = getattr(rewards, name, None)
        getattr(fn, "cache_clear", lambda: None)()


@pytest.fixture
def shipped_world(monkeypatch):
    """The shipped kits: every kit arm off, caches dropped both ways."""
    from tier0 import constants as C
    from tier0.engine import furina_stage
    for flag in _CONSTANT_ARMS:
        monkeypatch.setattr(C, flag, False)
    monkeypatch.setattr(furina_stage, "FURINA_STAGE", False)
    drop_arm_caches()
    yield
    monkeypatch.undo()
    drop_arm_caches()
