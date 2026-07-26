"""Shared tier 0.5 test fixtures.

`scripted_map` is the successor to the old `monkeypatch.setattr(model,
"node_template", ...)` idiom. Since §11 a run walks a generated map instead of
a fixed spine, so a test that wants to ask a one-node question ("does the
treasure node grant a relic") injects the node sequence it means rather than
patching a template that no longer exists.
"""

from __future__ import annotations

import pytest

from tier05 import maps, model


@pytest.fixture
def scripted_map(monkeypatch):
    """Force every act of a run to walk exactly these node kinds.

        scripted_map("NNEB")        # one act, four nodes, in that order

    Returns the patch function so a test can re-script mid-test.
    """
    def apply(kinds):
        monkeypatch.setattr(
            model, "build_act_map",
            lambda rng, act, _k=list(kinds): maps.linear(_k, act))
        return list(kinds)
    return apply
