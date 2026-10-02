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


def test_a_generated_conditional_reads_if_x_comma_y():
    """text-conventions rule 7: "If X, Y. Otherwise, Z." The codegen's
    `conditional` op printed a colon after the condition on every generated
    face that used it; no generated face may print one now."""
    colon = re.compile(r"\bIf [^.\"]*?\]?: [a-z]|Otherwise: ")
    offenders = []
    for gen_dir in (MOD / "Cards" / "Prototype" / "Generated",):
        for path in sorted(gen_dir.glob("*.cs")):
            for face in re.findall(r'\("description", (.*)\),\n',
                                   path.read_text(encoding="utf-8")):
                if colon.search(face):
                    offenders.append(path.stem)
    assert offenders == []
    stage_combat = (MOD / "Cards" / "Prototype" / "Generated"
                    / "ProtoFsWarmupAct.cs").read_text(encoding="utf-8")
    assert ("If an enemy intends to attack, gain {BranchBlock:diff()} "
            "[gold]Block[/gold].") in stage_combat
