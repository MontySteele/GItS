"""`EB-581`: a row one arm of a kit retires is not grantable and not offered
under the arm that retires it, and no two prototype rows print one title.

WHAT THE SEAT SAW (Kokomi r21, assembled lane, (c) 1 and (c) 2). The
coordinator granted `proto_kurages_oath_memory` -- the `KURAGE_MEMORY` base
kit's Power, "whenever the Bake-Kurage plays a card from its memory, gain N
Block" -- into a `KOKOMI_OVERHAUL` run. That arm has no jellyfish memory for
the rule to fire on, so the card was INERT; and it prints the same title as
`proto_kk_kurages_oath`, the arm's own starter Skill, so nothing on the seat's
screen said which card it was holding. Two rounds went on it.

THE ROWS ARE NOT DELETED. They are the base kit behind `C.KURAGE_MEMORY` and
that arm is untouched. What is stated here is only that two arms of ONE KIT do
not stack -- which both overhauls already say at the offer door by replacing
the starter and the pool WHOLE, and which nothing said at the `--arm` grant
door, the one the coordinator used.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from understudy import embark

REPO = Path(__file__).resolve().parents[2]
MEMORY_ROW = "proto_kurages_oath_memory"
DEV = ("0.2.9999+proto", "manifest")


def test_the_memory_row_is_declared_superseded_by_the_overhaul():
    assert C.PROTOTYPE_ARM_SUPERSEDED[MEMORY_ROW] == "KOKOMI_OVERHAUL"
    assert MEMORY_ROW == C.KURAGE_MEMORY_POOL_ADD


def test_the_map_is_derived_from_the_arms_own_substitutions():
    """NOT A SECOND LIST. A superseded arm's rows ARE the rows it substitutes
    in, so a row added to an arm cannot be missed here."""
    for _, add in C.SPARK_ALT_STARTER_SUBS:
        assert C.PROTOTYPE_ARM_SUPERSEDED[add] == "KLEE_OVERHAUL"
    for add in C.SPARK_ALT_POOL_SUBS.values():
        assert C.PROTOTYPE_ARM_SUPERSEDED[add] == "KLEE_OVERHAUL"


def test_the_grant_door_refuses_it(monkeypatch):
    """THE ROW'S ACCEPTANCE, half one -- the door the coordinator used."""
    with pytest.raises(embark.EmbarkError) as err:
        embark.check_arms([MEMORY_ROW], DEV)

    assert MEMORY_ROW in str(err.value)
    assert "KOKOMI_OVERHAUL" in str(err.value)


def test_the_arms_own_row_is_still_grantable():
    """The control that makes the refusal a RULE and not a closed door: the
    card the coordinator meant to grant goes through."""
    assert embark.check_arms(["proto_kk_kurages_oath"], DEV) == DEV


def test_the_offer_door_does_not_substitute_it_under_the_overhaul(monkeypatch):
    """THE ROW'S ACCEPTANCE, half two. With `KURAGE_MEMORY` alone the shipped
    Oath leaves the pool and the memory row takes its slot; with the overhaul
    on as well the pool is `KOKOMI_OVERHAUL_POOL_IDS` whole and the
    substitution is not made at all."""
    spec = {"id": "kokomi"}
    monkeypatch.setattr(C, "KURAGE_MEMORY", True)

    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", False)
    assert loader._pool_substitutions(spec) == {
        C.KURAGE_MEMORY_POOL_DROP: MEMORY_ROW}

    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    assert loader._pool_substitutions(spec) == {}


def test_the_declared_map_still_names_the_row_as_a_substitution():
    """`declared_pool_substitutions` is FLAG-BLIND by contract -- it answers
    "what id is a pool substitution at all", a schema question -- so the
    branch above must not have taken the row out of the schema."""
    assert (loader.declared_pool_substitutions()[C.KURAGE_MEMORY_POOL_DROP]
            == MEMORY_ROW)


def test_the_title_lint_is_green_and_saw_the_rows():
    """THE ROW'S ACCEPTANCE, half three. A gate that scanned nothing prints
    the same clean line as one that scanned everything (the SS3.1/SS3.7 dead-gate
    class), so the count is asserted as well as the exit code."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_prototype_titles.py")],
        capture_output=True, text=True)

    assert res.returncode == 0, res.stdout + res.stderr
    assert "prototype titles unique" in res.stdout
    # THE COUNT, READ AS A NUMBER (`EB-724`). This was a substring test for
    # "0 title(s)", which is a substring of a healthy "200 title(s)" too -- so
    # the gate meant to catch a dead scan went red the first time the prototype
    # surface reached a round hundred. The claim was always "the lint saw
    # rows", and it is asserted as that now.
    seen = re.search(r"unique: (\d+) title", res.stdout)
    assert seen is not None, res.stdout
    assert int(seen.group(1)) > 0, res.stdout
    # And the pair `EB-581` was filed on is the exemption doing work, not an
    # empty branch.
    assert "pair(s) exempt" in res.stdout
    assert " 0 pair(s) exempt" not in res.stdout


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
