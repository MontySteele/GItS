"""Yae's Edit and Sakura tips, cut (2026-10-14).

[USER]: "On Yae - the "Edit" tooltip seems unnecessarily long; no need to
show the text for every possible edit if the card can only apply one. We
could move the actual Edit's effect text into the selection screen, since
AFAIK we only ever apply one type of edit in a given screen."

[USER]: "I think the Sakura tooltip is overly verbose, and Sakura and Tenko
should be cut into separate tips."

The Edit tip is the general rule; each Annotation a face names is its own
tip (its Sakura reading on a card that Edits a Sakura); each hand screen an
Edit opens names its one Annotation in the prompt, and the seat page prints
that prompt. Tenko is its own tip.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from understudy import blindplay

from tier0.tests.test_refusal_changed_under_the_seat import (  # noqa: F401
    _hand_of, _observe, _sting, lane)

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
ANNOTATIONS = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
               / "YaeAnnotations.cs")


def _src(stem: str) -> str:
    return (GEN / f"{stem}.cs").read_text(encoding="utf-8")


def test_every_hand_edit_screen_applies_exactly_one_annotation():
    """The premise of the prompt: `YaeEditing.Edit` takes one Annotation and
    opens its screen with that Annotation's prompt; every card that opens
    one passes exactly one. Reborn as Guuji Yae (`EditAll`) chooses on its
    own screen and opens no hand screen; the Sakura Edits open none."""
    src = ANNOTATIONS.read_text(encoding="utf-8")
    edit = src[src.index("public static async Task Edit("):]
    edit = edit[:edit.index("\n    }\n")]
    assert "YaeAnnotation annotation," in edit
    assert "EditPromptKeyFor(annotation)" in edit
    assert "EditPromptKey)" not in edit
    callers = 0
    for path in GEN.glob("ProtoYm*.cs"):
        for call in re.findall(r"YaeCards\.Edit\((.*?)\);", path.read_text(
                encoding="utf-8")):
            callers += 1
            assert len(re.findall(r"YaeAnnotation\.\w+", call)) == 1, path
    assert callers >= 6


@pytest.mark.parametrize("stem, member, on_sakura", [
    ("ProtoYmProofread", "Reprint", "false"),
    ("ProtoYmMarginNote", "RedInk", "false"),
    ("ProtoYmFootnote", "Footnote", "false"),
    ("ProtoYmDeadline", "DeadlineExtension", "false"),
    ("ProtoYmSakuraSeal", "SakuraSeal", "false"),
    ("ProtoYmRoyalties", "Royalties", "false"),
    ("ProtoYmInkedBranches", "RedInk", "true"),
    ("ProtoYmFoxFireDraft", "FoxFire", "true"),
    ("ProtoYmEvergreenCharm", "DeadlineExtension", "true"),
])
def test_a_card_that_applies_one_annotation_carries_only_its_tip(
        stem, member, on_sakura):
    src = _src(stem)
    tips = re.findall(r"ForAnnotation\([^;]*?YaeAnnotation\.(\w+), (\w+)\)",
                      src)
    assert set(tips) == {(member, on_sakura)}
    assert "ArmKeywordTips.ForEdit(" in src


def test_reborn_keeps_its_own_chooser_and_carries_no_annotation_tip():
    assert "ForAnnotation" not in _src("ProtoYmRebornAsGuujiYae")


@pytest.mark.parametrize("stem, sakura", [
    ("ProtoYmKitsuneRite", False), ("ProtoYmTenkoKenshin", False),
    ("ProtoYmThunderRite", False), ("ProtoYmMikageThunder", True)])
def test_tenko_is_its_own_tip(stem, sakura):
    src = _src(stem)
    assert "ArmKeywordTips.ForTenko(" in src
    assert ("ArmKeywordTips.ForSakura(" in src) == sakura


def test_the_edit_prompt_shows_on_the_seat_page(lane, capsys):
    """The bridge posts the screen's prompt; the chooser page prints it as
    its heading."""
    prompt = ("Choose a card to Edit: Red Ink (it deals 3 more damage and "
              "gives 3 more Block).")
    defend = _sting(id="DEFEND", name="Defend", description="Gain 5 Block.",
                    cost="1", type="Skill", target_type="Self")
    state = _hand_of([])
    state["player"]["hand"] = [dict(defend, index=0)]
    state["state_type"] = "hand_select"
    state["hand_select"] = {"mode": "simple_select", "prompt": prompt,
                            "cards": [dict(defend, index=0)],
                            "can_confirm": False}
    screen, _posted = lane
    screen["now"] = state
    capsys.readouterr()
    assert blindplay.cmd_observe(_observe()) == 0
    assert f"# {prompt}" in capsys.readouterr().out


def test_the_seat_glossary_splits_the_rows():
    rows = blindplay.ARM_KEYWORDS
    assert "Red Ink" not in rows["Edit"] and "Tenko" not in rows["Sakura"]
    assert "Thunder" not in rows["Sakura"]
    # Review r3 (2026-10-14): Tenko is one plain rule again.
    assert rows["Tenko"] == ("Every Sakura acts now. Refresh them to at "
                             "least 3 turns.")
    assert "Rite" not in rows and "Rite" not in rows["Sakura"]
    assert rows["Red Ink"].startswith(
        "This card deals 3 more damage and gives 3 more Block. If it plants, "
        "its Sakura get it too.")
