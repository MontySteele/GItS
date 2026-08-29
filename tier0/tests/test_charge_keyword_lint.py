"""The Charge-keyword lint runs green AND can see the face it was written for.

A lint that has never seen the defect it guards is indistinguishable from one
that cannot see it -- and this defect is invisible by construction: a missing
hover tip renders as nothing at all. So this file does both halves. The RED
fixture is a Kokomi face that prints the word and attaches no definition,
which is exactly the shape run B6 hit live; the green half asserts the shipped
tree is clean with a non-vacuous denominator (the real faces DO name Charge,
so a scrape that silently read nothing could not pass).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_charge_keyword.py"

FACE = """using System.Collections.Generic;

namespace KleeMod.Cards.Kokomi.Generated;

public sealed class ProbeFace : CustomCardModel
{{
    public override List<(string, string)>? Localization => new()
    {{
        ("title", "Probe Face"),
        ("description", "Gain 3 [gold]Charge[/gold]."),
    }};
{tip}}}
"""

TIP = ("""
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KokomiRiderTips.ForCharge(base.ExtraHoverTips, this);
""")


def _module():
    spec = importlib.util.spec_from_file_location("lint_charge_keyword", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tree(tmp_path: Path, tip: str) -> Path:
    root = tmp_path / "Cards"
    (root / "Kokomi" / "Generated").mkdir(parents=True)
    (root / "Kokomi" / "Generated" / "ProbeFace.cs").write_text(
        FACE.format(tip=tip), encoding="utf-8")
    return root


def test_a_kokomi_face_naming_charge_without_the_tip_fails(tmp_path):
    lint = _module()
    bad = lint.findings(_tree(tmp_path, ""), classes=set())
    assert len(bad) == 1, bad
    assert "ProbeFace" in bad[0]
    assert "KokomiRiderTips.ForCharge" in bad[0]


def test_the_same_face_passes_once_the_tip_is_attached(tmp_path):
    lint = _module()
    assert lint.findings(_tree(tmp_path, TIP), classes=set()) == []


def test_a_face_outside_kokomis_reach_naming_charge_fails(tmp_path):
    """The other sign: the word names her meter, so nothing there defines it."""
    lint = _module()
    root = tmp_path / "Cards"
    (root / "Generated").mkdir(parents=True)
    (root / "Generated" / "StrangerFace.cs").write_text(
        FACE.format(tip=""), encoding="utf-8")
    bad = lint.findings(root, classes=set())
    assert len(bad) == 1, bad
    assert "outside Kokomi's reach" in bad[0]


def test_charged_is_not_the_meter(tmp_path):
    """`Electro-Charged` is a reaction, and must not drag in a Kokomi tip."""
    lint = _module()
    root = tmp_path / "Cards"
    (root / "Generated").mkdir(parents=True)
    (root / "Generated" / "ReactionFace.cs").write_text(
        FACE.format(tip="").replace(
            "Gain 3 [gold]Charge[/gold].", "Applies Electro-Charged."),
        encoding="utf-8")
    assert lint.findings(root, classes=set()) == []


def test_the_shipped_tree_is_clean_and_the_denominator_is_real():
    lint = _module()
    assert lint.findings() == []
    named = [p for p in (lint.CARD_ROOT).rglob("*.cs")
             if any(lint.prints_charge_word(d)
                    for d in lint._descriptions(
                        p.read_text(encoding="utf-8")))]
    assert len(named) >= 15, named


def test_the_lint_runs_green_from_the_command_line():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
