"""BACKLOG: "Furina: a Spend card silently plays its plain side when her
Fanfare cannot pay the Spend." A `choose_one` whose mode is headed by a
`stage_spend` is not offered that mode when the bank is short, so the plain
mode played with no word said. The face now says "(Not enough Fanfare)" in
hand, as a Drain mode says "(Not enough HP)". Behaviour unchanged. C# twin:
`FurinaWaveTests.A_spend_mode_says_when_fanfare_is_short`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

from pathlib import Path

from tier0.tests.test_arm_keyword_tips import PROTOTYPE_DIR, gen, proto

REPO = Path(__file__).resolve().parents[2]
POWERS = REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
SPEND_MODES = {"ProtoFsBubbleAria.cs": "3",
               "ProtoFsCommandingGaze.cs": "4"}


def test_only_spend_mode_rows_carry_the_line():
    carrying = {row["id"] for row in proto._rows()
                if gen.stage_spend_short_call(row) is not None}
    assert carrying == {"proto_fs_bubble_aria", "proto_fs_commanding_gaze"}


def test_the_generated_faces_carry_the_token_and_the_gate_s_price():
    for name, price in SPEND_MODES.items():
        src = (PROTOTYPE_DIR / name).read_text(encoding="utf-8")
        assert "{InCombat:{StageSpendShort}|}" in src, name
        assert ('description.Add("StageSpendShort", '
                f"FurinaStageFacePreview.SpendShort(this, {price}));") in src
    face = (POWERS / "FurinaStageBowPreview.cs").read_text(encoding="utf-8")
    # The localization census (2026-10-23, step 2): the words are a keyed
    # row, read through `CodeText`.
    assert ('"KLEEMOD-FACE_STAGE_SPEND_SHORT.description", '
            r'"\n(Not enough Fanfare)"') in face
