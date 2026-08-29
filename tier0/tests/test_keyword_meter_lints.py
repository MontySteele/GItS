"""The meter-keyword lint runs green AND can see the faces it was written for.

A lint that has never seen the defect it guards is indistinguishable from one
that cannot see it -- and this defect is invisible by construction: a missing
hover tip renders as nothing at all. So this file does both halves for BOTH
meters. The RED fixtures are faces that print a meter's word and attach no
definition, which is exactly the shape run B6 hit live; the green half asserts
the shipped tree is clean with non-vacuous denominators (the real faces DO name
Charge and Burst, so a scrape that silently read nothing could not pass).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_keyword_meters.py"

FACE = """using System.Collections.Generic;

namespace KleeMod.Cards.Kokomi.Generated;

public sealed class ProbeFace : CustomCardModel
{{
    public override List<(string, string)>? Localization => new()
    {{
        ("title", "Probe Face"),
        ("description", "{description}"),
    }};
{tip}}}
"""

CHARGE_DESCRIPTION = "Gain 3 [gold]Charge[/gold]."
BURST_DESCRIPTION = "Gain 3 [gold]Burst Energy[/gold]."

CHARGE_TIP = ("""
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KokomiRiderTips.ForCharge(base.ExtraHoverTips, this);
""")

BURST_TIP = ("""
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KleeCardTooltips.ForBurst(base.ExtraHoverTips, this);
""")


def _module():
    spec = importlib.util.spec_from_file_location("lint_keyword_meters", TOOL)
    mod = importlib.util.module_from_spec(spec)
    # Registered before exec: the lint declares a `@dataclass` whose field
    # annotations are strings (`from __future__ import annotations`), and
    # dataclasses resolves those through sys.modules[cls.__module__]. A module
    # loaded by path alone is not there, and the decorator raises at import.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _tree(tmp_path: Path, tip: str, description: str = CHARGE_DESCRIPTION,
          inside_kokomi: bool = True) -> Path:
    root = tmp_path / "Cards"
    where = (root / "Kokomi" / "Generated" if inside_kokomi
             else root / "Generated")
    where.mkdir(parents=True)
    (where / "ProbeFace.cs").write_text(
        FACE.format(tip=tip, description=description), encoding="utf-8")
    return root


def test_a_kokomi_face_naming_charge_without_the_tip_fails(tmp_path):
    lint = _module()
    bad = lint.findings(_tree(tmp_path, ""), classes=set())
    assert len(bad) == 1, bad
    assert "ProbeFace" in bad[0]
    assert "KokomiRiderTips.ForCharge" in bad[0]


def test_the_same_face_passes_once_the_charge_tip_is_attached(tmp_path):
    lint = _module()
    assert lint.findings(_tree(tmp_path, CHARGE_TIP), classes=set()) == []


def test_a_face_outside_kokomis_reach_naming_charge_fails(tmp_path):
    """The other sign: the word names her meter, so nothing there defines it."""
    lint = _module()
    bad = lint.findings(_tree(tmp_path, "", inside_kokomi=False),
                        classes=set())
    assert len(bad) == 1, bad
    assert "outside Kokomi's reach" in bad[0]


def test_charged_is_not_the_meter(tmp_path):
    """`Electro-Charged` is a reaction, and must not drag in a Kokomi tip."""
    lint = _module()
    root = _tree(tmp_path, "", description="Applies Electro-Charged.",
                 inside_kokomi=False)
    assert lint.findings(root, classes=set()) == []


def test_any_face_naming_burst_without_the_tip_fails(tmp_path):
    """Burst has no reach: the roster-wide tip is owed on every face."""
    lint = _module()
    root = _tree(tmp_path, "", description=BURST_DESCRIPTION,
                 inside_kokomi=False)
    bad = lint.findings(root, classes=set())
    assert len(bad) == 1, bad
    assert "KleeCardTooltips.ForBurst" in bad[0]
    # And never the reach complaint -- all three characters own a Burst meter.
    assert "reach" not in bad[0]


def test_the_same_face_passes_once_the_burst_tip_is_attached(tmp_path):
    lint = _module()
    root = _tree(tmp_path, BURST_TIP, description=BURST_DESCRIPTION,
                 inside_kokomi=False)
    assert lint.findings(root, classes=set()) == []


def test_bursting_is_not_the_meter(tmp_path):
    """`Ring of Bursting Grenades` is a card name, not the meter."""
    lint = _module()
    root = _tree(tmp_path, "",
                 description="Copy Ring of Bursting Grenades.",
                 inside_kokomi=False)
    assert lint.findings(root, classes=set()) == []


def test_a_face_naming_both_meters_owes_both_tips(tmp_path):
    """Ceremonial Garment's real shape: one face, two words, two findings."""
    lint = _module()
    root = _tree(tmp_path, "",
                 description="Costs your full [gold]Burst Energy[/gold] "
                             "meter. Spend 4 [gold]Charge[/gold].")
    bad = lint.findings(root, classes=set())
    assert len(bad) == 2, bad
    assert any("ForCharge" in line for line in bad)
    assert any("ForBurst" in line for line in bad)


def test_the_shipped_tree_is_clean_and_the_denominators_are_real():
    lint = _module()
    assert lint.findings() == []
    counts: dict[str, int] = {}
    for path in lint.CARD_ROOT.rglob("*.cs"):
        descriptions = lint._descriptions(path.read_text(encoding="utf-8"))
        for meter in lint.METERS:
            if any(meter.prints(d) for d in descriptions):
                counts[meter.word] = counts.get(meter.word, 0) + 1
    assert counts.get("Charge", 0) >= 15, counts
    assert counts.get("Burst", 0) >= 30, counts


def test_the_lint_runs_green_from_the_command_line():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
