"""The text pass of 2026-09-25: the pins the rewrite leans on.

The owner: "the existing text is often very verbose and unintuitive". The
specs are `review/records/text-pass-2026-09-25/`. Text only: no number or
behaviour moved, so what is pinned here is the one fact a shorter sentence
now takes for granted, and the one codegen spelling every generated face uses.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "klee-mod" / "KleeCode"


def _const(path: Path, name: str) -> int:
    src = path.read_text(encoding="utf-8")
    hit = re.search(rf"const int {name}\s*=\s*(\d+);", src)
    assert hit, (path.name, name)
    return int(hit.group(1))


def test_every_burst_meter_fills_at_one_rate_from_both_incomes():
    """The Burst tip prints ONE number: "Fills 5 from each Elemental Skill
    card and each Elemental Reaction." That sentence is true only while every
    meter's skill-card grant and reaction grant are the same number. If one
    ever moves, `KleeCardTooltips.BurstBody` has to name both rates again."""
    burst = MOD / "Powers" / "BurstResource.cs"
    furina = MOD / "Powers" / "FurinaResources.cs"
    kokomi = MOD / "Powers" / "KokomiResources.cs"
    shared = _const(burst, "PerSkillTag")
    assert _const(burst, "PerReaction") == shared                 # Klee
    assert _const(furina, "BurstPerSkillTag") == shared           # Furina
    assert _const(furina, "BurstPerReaction") == shared
    assert _const(kokomi, "BurstPerReaction") == shared           # Kokomi
    tip = (MOD / "Cards" / "KleeCardTooltips.cs").read_text(encoding="utf-8")
    assert '$"Fills {perSkillTag} from each [gold]Elemental Skill[/gold] card "' \
        in tip
    assert "{meter.Amount}/{meter.Max}." in tip


def test_a_generated_conditional_reads_if_x_comma_y():
    """text-conventions rule 7: "If X, Y. Otherwise, Z." The codegen's
    `conditional` op printed a colon after the condition on every generated
    face that used it; no generated face may print one now."""
    colon = re.compile(r"\bIf [^.\"]*?\]?: [a-z]|Otherwise: ")
    offenders = []
    for gen_dir in (MOD / "Cards" / "Generated",
                    MOD / "Cards" / "Furina" / "Generated",
                    MOD / "Cards" / "Kokomi" / "Generated"):
        for path in sorted(gen_dir.glob("*.cs")):
            for face in re.findall(r'\("description", (.*)\),\n',
                                   path.read_text(encoding="utf-8")):
                if colon.search(face):
                    offenders.append(path.stem)
    assert offenders == []
    stage_combat = (MOD / "Cards" / "Furina" / "Generated"
                    / "WarmupAct.cs").read_text(encoding="utf-8")
    assert "If an enemy intends to attack, gain 3 [gold]Block[/gold]." \
        in stage_combat
