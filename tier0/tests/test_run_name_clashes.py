"""`tools/lint_run_name_clashes.py`: names one run can hold differ by more
than punctuation (2026-09-29, a Varka seat met "Kaeya: Frostgnaw" and
"Kaeya — Frostgnaw" in one deck)."""

from __future__ import annotations

from tools import lint_run_name_clashes as lint


def _row(cid, name, **kw):
    return {"id": cid, "name": name, **kw}


def test_the_repo_is_clean_and_the_allow_list_is_empty():
    assert lint.findings(lint.read_sheets()) == []
    assert lint.ALLOWED == frozenset()


def test_normalise_folds_the_punctuation_a_player_cannot_see():
    assert (lint.normalise("Kaeya: Frostgnaw")
            == lint.normalise("Kaeya — Frostgnaw")
            == lint.normalise("kaeya - frostgnaw (proto)")
            == lint.normalise("Kaeya –  Frostgnaw"))
    assert (lint.normalise("Barbara: Let the Show Begin")
            == lint.normalise("Barbara — Let the Show Begin♪"))


def test_a_personal_knight_against_a_companion_is_a_finding():
    sheets = {
        "prototype-surface.yaml": [
            _row("proto_mc_kaeya_frostgnaw", "Kaeya — Frostgnaw",
                 character="klee", nation="mondstadt"),
            _row("proto_vk_kaeya_frostgnaw", "Kaeya: Frostgnaw",
                 character="varka", nation="mondstadt",
                 personal_pool="varka")],
    }
    found = lint.findings(sheets)
    assert len(found) == 1 and "varka" in found[0]
    # Held open on the allow-list, it passes; the list is shrink-only.
    pair = ("proto_vk_kaeya_frostgnaw", "proto_mc_kaeya_frostgnaw")
    assert lint.findings(sheets, frozenset({pair})) == []
    sheets["prototype-surface.yaml"][1]["name"] = "Kaeya: Heart of the Abyss"
    stale = lint.findings(sheets, frozenset({pair}))
    assert len(stale) == 1 and "STALE" in stale[0]


def test_own_rows_are_not_compared_with_each_other():
    # A whole-kit swap prints a shipped title on purpose.
    sheets = {
        "prototype-surface.yaml": [
            _row("proto_ko_pop", "Pop!", character="klee"),
            _row("proto_ko_pop_twin", "Pop!", character="klee")],
    }
    assert lint.findings(sheets) == []
