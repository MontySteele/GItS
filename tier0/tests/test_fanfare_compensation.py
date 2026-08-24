"""The Fanfare compensation pass (2026-07-28) — reader density and R7.

Registered in docs/archive/sprint-fanfare-compensation-2026-07-28.md. The parent
sprint (docs/archive/sprint-fanfare-rework-2026-07-28.md) cut single-leg Fanfare in
and left two out-of-band numbers; this pass exists to move them, and these
tests pin the mechanics it shipped rather than the numbers. Those numbers were
PROPOSED when this file was written and were RATIFIED at the R130 sitting
(2026-08-07) with exactly one exception: Track 2.4, the starter's reader
clause, was VETOED and reverted.

Each test here was seen to FAIL against the defect it names before it was
kept -- the house rule. The mutation used is recorded in each docstring.
"""
from __future__ import annotations

import random
import subprocess
import sys
from dataclasses import replace

import yaml

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from tier05 import draft


REPO = loader.DOCS_DIR.parent


# --------------------------------------------------------------------------
# Track 1 -- RETIRED as a universal rider (EB-118 sec.5.2, 2026-08-24).
# What survives is R6: the full grant is a rare-POWER payoff, three cards.
# --------------------------------------------------------------------------

def _sheet() -> list[dict]:
    return yaml.safe_load(
        (loader.DOCS_DIR / "furina-cards.yaml").read_text(encoding="utf-8"))


def _keywords(card: dict) -> list[str]:
    out = []
    stack = list(card.get("effects") or ())
    while stack:
        fx = stack.pop()
        if fx.get("op") in ("gain_fanfare_floor", "raise_fanfare_cap"):
            out.append(fx["op"])
        for branch in ("then", "else"):
            stack.extend(fx.get(branch) or ())
    return out


def test_no_power_carries_an_incidental_cap_rider():
    """The inverse of the rule this file was written to pin.

    Track 1 required every Power to print a Fanfare keyword, and thirteen of
    them printed "Fanfare Cap +X" because the rule said so rather than
    because the card was about headroom. EB-118 sec.5.2 removed them and
    retired R7, so the assertion flips: a Power prints the cap verb only if a
    future ruling gives one that job, and none has. The three rare payoffs
    keep the OTHER keyword, which is the next test.

    Verified to fail against the pre-removal sheet, where all seventeen
    Powers carried a keyword and thirteen of them carried this one.
    """
    powers = [c for c in _sheet() if c.get("type") == "power"]
    assert len(powers) == 17
    carriers = [c["id"] for c in powers
                if "raise_fanfare_cap" in _keywords(c)]
    assert carriers == []


def test_the_only_cap_carrier_left_is_the_one_its_upgrade_pins():
    """`lasting_impression` is the sixteenth card of sec.5.2's list and the
    one that did not land: its ruled upgrade delta is `fanfare_cap: +2`,
    which binds to this op, so removing the op makes `apply_upgrade` raise
    and the card needs a NEW ruled delta before it can lose the line. That is
    [USER]'s call, so the row is pinned here rather than left to drift -- if
    the delta is ever ruled and the op removed, this test is what says so.
    """
    carriers = [c["id"] for c in _sheet()
                if "raise_fanfare_cap" in _keywords(c)]
    assert carriers == ["lasting_impression"]


def test_the_full_grant_is_still_three_rare_powers():
    """R6 survives both Track 1 and its retirement, which is the point.

    The pair of keywords was always at risk of collapsing into one: first by
    "Fanfare Cap +X" going everywhere (Track 1), now by it going nowhere
    (EB-118 sec.5.2). Neither touched the full grant. It is still exactly
    three rare Powers, and it is still the only Fanfare keyword a card can
    earn by being a payoff.
    """
    grants = {c["id"] for c in _sheet()
              if "gain_fanfare_floor" in _keywords(c)}
    assert grants == {"unheard_confession", "the_sea_is_my_stage",
                      "rapturous_applause"}
    for cid in grants:
        card = next(c for c in _sheet() if c["id"] == cid)
        assert card["type"] == "power" and card["rarity"] == "rare"


def test_r6_still_fails_on_a_full_grant_outside_a_rare_power(tmp_path, capsys):
    """RED TEST for the rule that SURVIVED. Mutation: plant the full grant on
    a common Power.

    R7's own red test retired with R7 (EB-118 sec.5.2) -- a red test for a
    rule that no longer exists asserts nothing. R6 is the half that still
    binds, and it never had a mutation test of its own; it does now, because
    the pair of keywords is only meaningful while one of them is still gated.
    Verified to fail before it was kept: with the grant planted on
    `casting_call` the lint exits 1 and names R6.
    """
    import tools.lint_furina_registers as lint

    cards = _sheet()
    victim = next(c for c in cards if c["id"] == "casting_call")
    victim["effects"] = victim["effects"] + [
        {"op": "gain_fanfare_floor", "amount": 5}]
    broken = tmp_path / "furina-cards.yaml"
    broken.write_text(yaml.safe_dump(cards), encoding="utf-8")

    original, lint.SHEET = lint.SHEET, broken
    try:
        assert lint.main() == 1
    finally:
        lint.SHEET = original
    # And it must fail FOR THE RIGHT REASON. A lint that exits 1 because the
    # temp file tripped some other rule would look identical from here.
    out = capsys.readouterr().out
    assert "R6 casting_call" in out


def test_r2_still_does_not_reach_the_cap_verb():
    """The release survives the rule that caused it.

    R2 sends Fanfare READS to the archon register. `raise_fanfare_cap` was in
    that set for exactly one day, until Track 1 put the line on every Power
    and R2 stopped selecting anything by keeping it. EB-118 sec.5.2 removed
    the riders, so the original reason is spent -- and the release is NOT
    reversed, because whether a dedicated headroom card speaks in the archon
    voice is a naming call with no card to judge. These three rows are the
    proof: they are exactly the salon and private Powers that carried the
    line, they no longer carry it, and their registers did not move to pay
    for its removal.
    """
    for cid in ("casting_call", "grand_salon", "quick_change"):
        card = next(c for c in _sheet() if c["id"] == cid)
        assert "raise_fanfare_cap" not in _keywords(card)
        assert card["register"] in ("salon", "private")

    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_furina_registers.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


# --------------------------------------------------------------------------
# Track 2 -- the readers themselves
# --------------------------------------------------------------------------

def _furina_state(fanfare: int = 0, encore: int = 0):
    """A Furina in combat with the meter pre-set, cap open.

    The cap is opened explicitly because `fanfare_cap` gates every meter
    write; a state built with cap 0 silently swallows every gain and every
    assertion below would pass for the wrong reason.
    """
    st = CombatState(player=loader.build_player("furina"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.fanfare_cap = 30
    st.player.fanfare = fanfare
    st.player.encore = encore
    return st


def play(st: CombatState, card_id: str) -> None:
    card = loader.get_card(card_id)
    st.player.hand.append(card)
    st.player.energy = 3
    combat.play_card(st, card)


def test_the_three_new_commons_are_commons_on_the_low_slope():
    """Track 2.1's rate rule: commons read at 1_per_4, never the rares' 1_per_2.

    A common on the rare rate would make the rare's steeper number worthless,
    which is the rarity ladder inverted. Asserted rather than trusted because
    the rate is a string in a yaml row and nothing else checks it.
    """
    for cid in ("applause_line", "held_breath"):
        card = loader.get_card(cid)
        assert card.rarity == "common"
        formulas = [fx["bonus_formula"] for fx in card.effects
                    if "bonus_formula" in fx]
        assert formulas == ["1_per_4_fanfare"]

    # And the rares kept the steep rate they are paid for.
    for cid in ("crescendo", "high_tide", "thunderous_ovation"):
        card = loader.get_card(cid)
        assert any(fx.get("bonus_formula") == "1_per_2_fanfare"
                   for fx in card.effects)


def test_applause_line_scales_and_pays_its_base_at_an_empty_meter():
    """The damage rail at common. A reader that is dead on an empty meter is
    a rare's problem, not a common's -- so the base has to carry it."""
    st = _furina_state()
    before = st.enemies[0].hp
    play(st, "applause_line")
    assert before - st.enemies[0].hp == 3

    st = _furina_state(fanfare=12)
    before = st.enemies[0].hp
    play(st, "applause_line")
    assert before - st.enemies[0].hp == 3 + 3      # 12 // 4


def test_held_breath_is_the_archetypes_first_non_rare_fanfare_wall():
    st = _furina_state(fanfare=20)
    play(st, "held_breath")
    assert st.player.block == 4 + 5                # 20 // 4


def test_breathless_prints_the_meter_it_spends():
    """Track 2.3. The converter is the one new card that PAYS Fanfare rather
    than reading it, and that is the whole argument for a converter at common
    under single-leg: the spend is the generation."""
    st = _furina_state(encore=10)
    play(st, "breathless")
    assert st.player.encore == 6
    assert st.player.fanfare == 4 * C.FANFARE_PER_ENCORE_SPENT


def test_breathless_played_dry_costs_true_hp_and_still_prints():
    """The risk line. spend_encore is the OVERDRAW primitive, so a dry buffer
    is paid in HP -- which prints the same Fanfare by the other leg. The card
    is never dead and never free."""
    st = _furina_state(encore=0)
    hp = st.player.hp
    play(st, "breathless")
    assert st.player.hp == hp - 4
    assert st.player.fanfare == 4 * C.FANFARE_PER_HP_LOST


def test_suffering_for_art_closes_its_own_loop_on_one_face():
    """Track 2.2's flagship. The wound prints the meter and the third clause
    reads it, so this is the only card in the pool that both pays Fanfare and
    cashes it. The block is worth nothing on a cold meter, which is the price
    of a 0-cost common that the archetype plays every turn."""
    st = _furina_state()
    play(st, "suffering_for_art")
    assert st.player.fanfare == 1                  # the wound, and only it
    assert st.player.block == 0                    # 1 // 4

    st = _furina_state(fanfare=15)
    play(st, "suffering_for_art")
    assert st.player.block == 4                    # (15 + 1) // 4


def test_hearts_swelling_pays_on_the_turn_it_is_guaranteed_to_be_played():
    """The base 3 is the fix, not decoration.

    hearts_swelling is INNATE, so its guaranteed play is turn one into an
    empty meter. A pure scaling clause here would have been a printed reader
    with a near-zero fire rate on the one turn the card is promised to be in
    hand -- the D4 mistake the brief names. Mutation run: dropping the base to
    0 makes this assert 0 == 3 and fails.
    """
    card = loader.get_card("hearts_swelling")
    assert card.innate
    st = _furina_state()
    play(st, "hearts_swelling")
    assert st.player.encore == 7
    assert st.player.block == 3


def test_the_starter_does_not_read_the_meter():
    """Track 2.4 VETOED at the R130 sitting (2026-08-07).

    The starter was the sprint's act-1 lever and the one number that could not
    be aimed at a single archetype -- it is in every Furina deck, so it moved
    the salon and spotlight arms too. [USER] vetoed exactly that: the starter
    gets no payoff, Encore generation alone is fine for a starter. This is the
    veto pin -- a Fanfare of 16 (four ticks of the commons rate) buys aria
    nothing. The tier rule and the five other bodies stand; only this one
    reverted.
    """
    assert "aria_of_recompense" in loader.starting_deck("furina")
    st = _furina_state(fanfare=16)
    play(st, "aria_of_recompense")
    assert st.player.encore == 5
    assert st.player.block == 0


def test_every_new_reader_goes_through_the_clamp():
    """The negative floor is live (the Hyperbeam), so a reader that read the
    raw field would pay NEGATIVE block off a buried meter -- a defensive card
    that removes your Block. One chokepoint per engine, and these are the
    cards that just started using it."""
    st = _furina_state(fanfare=-20)
    st.player.fanfare_floor = -20
    assert resources.readable(st.player) == 0
    play(st, "held_breath")
    assert st.player.block == 4                    # base only, never less


# --------------------------------------------------------------------------
# The drafter consequence of putting a reader on a basic
# --------------------------------------------------------------------------

def test_a_basic_reader_could_not_close_the_drafts_reader_limb():
    """A free card cannot be evidence that a DRAFT assembled a plan.

    Found by an existing test going red rather than by design: while the
    starter read the meter (Track 2.4), `core_complete(starter + [one floor
    source])` returned True for the fanfare plan, so the reader limb was
    satisfied at run start for every deck forever -- and it feeds
    score_offer's core-advance bonus, so the drafter was being told a third
    of the plan was free.

    R130 (2026-08-07) vetoed that body, so NO basic reads the meter today and
    the starter can no longer supply the premise. The rule outlived the card
    and stays in `draft._drafted_readers`, so the pin is rebuilt around a
    basic-rarity reader constructed here rather than drawn from the sheet:
    the filter must hold for the next basic anyone proposes as a reader, and
    a pin that can only fire while one exists is a pin that quietly retires.
    Mutation: drop the `rarity != basic` filter and the second assertion goes
    1 == 0.
    """
    starter = [loader.get_card(cid) for cid in loader.starting_deck("furina")]
    assert not any(draft._reads_fanfare(c) for c in starter)   # R130 veto
    assert draft._drafted_readers(starter) == 0

    basic_reader = replace(loader.get_card("applause_line"), rarity="basic")
    assert draft._reads_fanfare(basic_reader)                  # it IS a reader
    assert draft._drafted_readers(starter + [basic_reader]) == 0

    drafted = starter + [loader.get_card("applause_line")]
    assert draft._drafted_readers(drafted) == 1


def test_the_generation_and_floor_limbs_are_untouched_by_the_exclusion():
    """The exclusion is surgical on purpose: only the reader limb is a COUNT,
    and only a count can be gamed by a free card. The other two limbs are
    totals over printed amounts, where the starter's contribution is a real
    quantity that scales with what the draft adds."""
    starter = [loader.get_card(cid) for cid in loader.starting_deck("furina")]
    assert draft._fanfare_generation_total(starter) > 0
    assert draft._fanfare_floor_total(starter) == 0
