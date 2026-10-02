"""`EB-581`: no two prototype rows print one title.

WHAT THE SEAT SAW (Kokomi r21, assembled lane, (c) 1 and (c) 2). The
coordinator granted `proto_kurages_oath_memory` -- a retired arm's Power --
into a Kokomi run, where it printed the same title as `proto_kk_kurages_oath`,
the kit's own starter Skill, so nothing on the seat's screen said which card
it was holding. The retired arm and its rows left at legacy cleanup stage 6;
what stands is the title rule and the grant door's acceptance of a live row.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from understudy import embark

REPO = Path(__file__).resolve().parents[2]
DEV = ("0.2.9999+proto", "manifest")


def test_the_retired_memory_row_is_gone_and_the_kits_row_is_grantable():
    from tier0.content import loader                  # noqa: PLC0415
    rows = {c.id for c in loader.prototype_cards()}
    assert "proto_kurages_oath_memory" not in rows
    assert embark.check_arms(["proto_kk_kurages_oath"], DEV) == DEV


def test_the_title_lint_is_green_and_saw_the_rows():
    """THE ROW'S ACCEPTANCE, half three. A gate that scanned nothing prints
    the same clean line as one that scanned everything (the SS3.1/SS3.7 dead-gate
    class), so the count is asserted as well as the exit code."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_prototype_titles.py")],
        capture_output=True, text=True)

    assert res.returncode == 0, res.stdout + res.stderr
    assert "prototype titles unique" in res.stdout
    # THE COUNT, READ AS A NUMBER (`EB-732`). This was a substring test for
    # "0 title(s)", which is a substring of a healthy "200 title(s)" too -- so
    # the gate meant to catch a dead scan went red the first time the prototype
    # surface reached a round hundred. The claim was always "the lint saw
    # rows", and it is asserted as that now.
    seen = re.search(r"unique: (\d+) title", res.stdout)
    assert seen is not None, res.stdout
    assert int(seen.group(1)) > 0, res.stdout


def test_the_title_lint_bites_on_two_live_rows(tmp_path, monkeypatch):
    """The negative test, and it is the state the surface was in before the
    grant door closed: two rows printing one title with neither declared
    superseded."""
    import tools.lint_prototype_titles as lint          # noqa: PLC0415

    surface = tmp_path / "prototype-surface.yaml"
    surface.write_text(
        "\n".join([
            '- {id: proto_one, name: "One Name", cost: 1, type: skill,',
            '   rarity: common}',
            '- {id: proto_two, name: "One Name (proto)", cost: 1,',
            '   type: skill, rarity: common}',
            "",
        ]), encoding="utf-8")
    monkeypatch.setattr(lint, "SURFACE", surface)

    assert lint.main() == 1


def test_the_shadow_suffix_is_not_a_second_title(tmp_path, monkeypatch):
    """WHY `lint_unique_names` COULD NOT SEE IT. The suffix is a SHEET device:
    `display_name` strips it in both engines, so the two rows above are one
    name on a card face and comparing `name:` finds nothing."""
    from tier0.content.loader import display_name       # noqa: PLC0415

    assert display_name("One Name (proto)") == display_name("One Name")
