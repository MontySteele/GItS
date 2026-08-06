"""The Fanfare compensation pass (2026-07-28) — reader density and R7.

Registered in docs/archive/sprint-fanfare-compensation-2026-07-28.md. The parent
sprint (docs/archive/sprint-fanfare-rework-2026-07-28.md) cut single-leg Fanfare in
and left two out-of-band numbers; this pass exists to move them, and these
tests pin the mechanics it shipped rather than the numbers, which are all
PROPOSED.

Each test here was seen to FAIL against the defect it names before it was
kept -- the house rule. The mutation used is recorded in each docstring.
"""
from __future__ import annotations

import random
import subprocess
import sys

import yaml

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from tier05 import draft


REPO = loader.DOCS_DIR.parent


# --------------------------------------------------------------------------
# Track 1 -- every Power prints a Fanfare keyword (R7)
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


def test_every_power_prints_exactly_one_fanfare_keyword():
    """Track 1, the ruling itself: no Power grants nothing any more.

    The rework left twelve Powers granting nothing at all, which was invisible
    in a different way than the pre-rework silent grant: the value was gone,
    but "which Powers grant" had become a curated list nobody could read off a
    card. The ruling reverses it, and the shape of the ruling -- ALL of them --
    is what lets this be an assertion instead of a list.
    """
    powers = [c for c in _sheet() if c.get("type") == "power"]
    assert len(powers) == 17
    for card in powers:
        kws = _keywords(card)
        assert len(kws) == 1, f"{card['id']} prints {kws}"


def test_the_full_grant_stayed_rare_and_the_cap_took_everything_else():
    """R6 survives Track 1 unamended, which is the point of the two keywords.

    "Fanfare Cap +X" going everywhere would be a reason to worry the pair had
    collapsed into one keyword. It has not: the full grant is still three rare
    Powers, and every other Power prints the cheap half.
    """
    grants = {c["id"] for c in _sheet()
              if "gain_fanfare_floor" in _keywords(c)}
    assert grants == {"unheard_confession", "the_sea_is_my_stage",
                      "rapturous_applause"}
    for cid in grants:
        card = next(c for c in _sheet() if c["id"] == cid)
        assert card["type"] == "power" and card["rarity"] == "rare"


def test_r7_fails_on_a_power_that_grants_nothing(tmp_path, capsys):
    """RED TEST for R7. Mutation: strip the keyword off one Power.

    Verified to fail before it was kept -- with `raise_fanfare_cap` removed
    from `casting_call` the lint exits 1 and names R7. Without this the ruling
    would be a convention held by twelve hand-edited rows, which is precisely
    the shape the rework's own short list had and the shape that lost.
    """
    import tools.lint_furina_registers as lint

    cards = _sheet()
    victim = next(c for c in cards if c["id"] == "casting_call")
    victim["effects"] = [fx for fx in victim["effects"]
                         if fx.get("op") != "raise_fanfare_cap"]
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
    assert "R7 casting_call" in out


def test_r2_no_longer_drags_the_cap_keyword_into_the_archon_voice():
    """The lint half of Track 1, and the reason it had to move.

    R2 sends Fanfare READS to the archon register. `raise_fanfare_cap` was in
    that set for exactly one day, while the cap keyword sat on a short list
    R2 itself selected. Under the ruling every Power prints it, so leaving it
    in R2 would have forced twelve salon and private Powers to rename into a
    voice they do not speak, to satisfy a rule that had stopped choosing
    anything. These three rows are the proof it released.
    """
    for cid in ("casting_call", "grand_salon", "quick_change"):
        card = next(c for c in _sheet() if c["id"] == cid)
        assert "raise_fanfare_cap" in _keywords(card)
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


def test_the_starter_reads_the_meter_now():
    """Track 2.4, the act-1 lever, and the one number in the sprint that
    cannot be aimed at a single archetype: this card is in every Furina deck.
    """
    assert "aria_of_recompense" in loader.starting_deck("furina")
    st = _furina_state(fanfare=16)
    play(st, "aria_of_recompense")
    assert st.player.encore == 5
    assert st.player.block == 4


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

def test_the_starter_reader_does_not_close_the_drafts_reader_limb():
    """A free card cannot be evidence that a DRAFT assembled a plan.

    Found by an existing test going red rather than by design: once the
    starter read the meter, `core_complete(starter + [one floor source])`
    returned True for the fanfare plan, so the reader limb was satisfied at
    run start for every deck forever -- and it feeds score_offer's core-advance
    bonus, so the drafter would have been told a third of the plan was free.
    Mutation: drop the `rarity != basic` filter in `draft._drafted_readers`
    and this test fails on the first assertion.
    """
    starter = [loader.get_card(cid) for cid in loader.starting_deck("furina")]
    assert any(draft._reads_fanfare(c) for c in starter)
    assert draft._drafted_readers(starter) == 0

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
