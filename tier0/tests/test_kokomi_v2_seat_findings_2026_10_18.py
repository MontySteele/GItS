"""THE KOKOMI V2 SEAT FINDINGS (2026-10-18), the page half.

Three seats could not see a rule that was working. Tidal Riposte's stored
bonus "never visibly paid off"; Pincer's Plan "never fired visibly; I never
knew whether it triggered"; and a lane read "War Council" twice under "The
Bake-Kurage carried these out" with no word on why. The mod now files a
`play_bonus` and a `doubled_by` event on the Attack's own row
(`TidalRiposteChargePower`, `FirstAttackTwicePower`) and an `again` field on a
repeated carry-out (`KokomiPlan.AgainSources`); the page prints all three.
And the Plan tip says when a Plan reads the enemies. C# half:
`klee-mod/KleeTests/Prototype/KokomiV2SeatFindingsTests.cs`.
"""

from __future__ import annotations

from understudy import blindplay
from tier0.tests.test_varka_payoff_seat_page import _ev, _row
from tier0.tests.test_varka_seat_page import varka_state


def _page(row):
    state = varka_state()
    state["player"]["resolutions"] = [row, _row("Strike", hits=True)]
    page = blindplay.observe(state)
    section = page.split(f"- **{row['card']}**", 1)[1]
    return page, section.split("- **Strike**", 1)[0]


def test_riposte_prints_its_bonus_on_the_attack_that_spent_it():
    page, row = _page(_row("Kurage's Wake", hits=True, events=[
        _ev("play_bonus", 9301, card="Kurage's Wake",
            power="Tidal Riposte", amount=8)]))
    assert "  Tidal Riposte: each of its hits dealt 8 more damage." in row
    assert page.count("Tidal Riposte: each of its hits") == 1


def test_pincer_prints_on_the_attack_it_played_twice():
    _, row = _page(_row("Strike+", hits=True, events=[
        _ev("doubled_by", 9302, card="Strike+", power="Pincer")]))
    assert "  Pincer: this Attack was played twice." in row


def test_neither_receipt_reaches_the_since_last_page_list():
    page, _ = _page(_row("Kurage's Wake", hits=True, events=[
        _ev("play_bonus", 9303, card="Kurage's Wake",
            power="Tidal Riposte", amount=8),
        _ev("doubled_by", 9304, card="Kurage's Wake", power="Pincer")]))
    assert "play_bonus" not in page and "doubled_by" not in page


def test_a_repeated_carry_out_names_what_bought_it():
    from tier0.tests.test_understudy_blindplay import (morning_of,
                                                       plans_combat_state)
    blindplay.forget_fight()
    first = {"card": "War Council", "number": 2,
             "line": "Bake-Kurage: War Council, 2", "on_play": False,
             "moved": [], "kind": "energy", "asked": 2}
    second = dict(first, again="Nereid's Ascension")
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of(first, second))))
    assert page.count("Bake-Kurage: War Council, 2") == 2
    assert page.count("*(carried out again: Nereid's Ascension)*") == 1


def test_the_plan_tip_says_when_it_reads_the_enemies():
    tip = blindplay.ARM_KEYWORDS["Plan"]
    assert "read enemies then" in tip
    assert "Block lasts that turn" in tip
