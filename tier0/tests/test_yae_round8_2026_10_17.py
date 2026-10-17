"""Yae round 8 (2026-10-17): Fox's Bargain reads Weak before its hit.

Lane 5: the Energy refund "did not trigger on a killing blow" -- the
conditional ran after the damage, when a dead target no longer carries Weak.
"""
from pathlib import Path

import yaml


def test_foxs_bargain_reads_weak_before_the_hit():
    rows = yaml.safe_load(Path("docs/prototype-surface.yaml").read_text(encoding="utf-8"))
    row = next(r for r in rows if r["id"] == "proto_ym_foxs_bargain")
    ops = [e["op"] for e in row["effects"]]
    assert ops == ["conditional", "damage"]
    assert row["effects"][0]["if"] == "target_has_power_weak"
