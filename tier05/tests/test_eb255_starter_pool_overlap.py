"""EB-255: `_committed_share` reads a starter card back as a draft.

`tier05.draft.archetype_shares` excludes the starting deck from "what has been
drafted" by asking `c.rarity != "basic"`, and its docstring states the
invariant that makes that exclusion exact: *every starter card is basic and
basic never appears in the draftable pool*. Nothing checked it, and its first
half is false.

This file pins the FINDING, which is what the row asks for at this stage --
"red on both rows today" -- while `tools/lint_starter_pool_overlap.py` is the
gate that keeps it from growing. The FIX (exclude by starter membership) moves
`archetype_shares` for two characters, therefore `dominant_archetype`,
therefore the rest plan and the adaptive drafter, therefore every tier-0.5
number they produce: a `POLICY_VERSION` window with a re-baseline, gated on
the design call about which copies of a starter id a later draft should count.
So the cases below assert the contamination IS there, by name and by size, and
they will fail the day it is fixed -- which is the day this file is rewritten
in the same commit as the window.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, rewards

from tools import lint_starter_pool_overlap as lint


def test_an_invitation_is_a_starter_card_that_is_also_offerable():
    """The one live contaminator, stated in full: common (not basic), not a
    companion (so `companions=False` does not drop it), carrying a real
    archetype tag (so it lands in `tagged`), in Furina's starter AND in her
    reward pool."""
    card = loader.get_card("an_invitation")
    assert card.rarity == "common"
    assert card.is_companion is False
    assert card.archetypes == ["spotlight"]
    assert "an_invitation" in loader.starting_deck("furina")
    pool = {c.id for cs in rewards.character_pool("furina").values()
            for c in cs}
    assert "an_invitation" in pool


def test_to_the_front_is_the_same_shape_one_flag_away():
    """The second row the playtest named. It enters Kokomi's starter only
    under `C.KURAGE_MEMORY` (`loader._starter_ids`), which is why the lint
    walks the flagged arms rather than only the live tree."""
    card = loader.get_card("to_the_front")
    assert card.rarity == "common"
    assert card.is_companion is False
    assert card.archetypes == ["commander"]
    assert "to_the_front" not in loader.starting_deck("kokomi")   # flag off
    with lint._arm(KURAGE_MEMORY=True):
        assert "to_the_front" in loader.starting_deck("kokomi")
        pool = {c.id for cs in rewards.character_pool("kokomi").values()
                for c in cs}
        assert "to_the_front" in pool


def test_furinas_starter_alone_already_reads_as_a_committed_draft():
    """The defect itself, in the number it corrupts. An untouched Furina
    starting deck -- nothing drafted, no reward screen shown -- must score
    0.0 on every archetype, and it does not: it reports a full spotlight
    commitment off one dealt card."""
    deck = [loader.get_card(cid) for cid in loader.starting_deck("furina")]
    shares = draft.archetype_shares(deck, companions=False)
    assert shares["spotlight"] == 1.0, (
        "if this is 0.0 the fix has landed -- rewrite this file with the "
        "POLICY_VERSION window that landed it")
    assert draft.dominant_archetype(deck) == "spotlight"


def test_klee_is_the_control():
    """Klee's whole starter IS basic, so her undrafted deck reads as the spec
    says every undrafted deck should. The contamination is a property of two
    sheets, not of the function."""
    deck = [loader.get_card(cid) for cid in loader.starting_deck("klee")]
    assert draft.archetype_shares(deck, companions=False) == {
        a: 0.0 for a in draft.ARCHETYPES}
    assert draft.dominant_archetype(deck) == "goodstuff"


# --- the gate itself ----------------------------------------------------


def test_the_lint_is_green_and_its_debt_matches_the_tree():
    """The curated-debt contract, both directions: nothing unlisted, and
    nothing listed that has quietly become clean."""
    seen, basics_offered = lint.findings()
    known = {(a, c, i): claims for a, c, i, claims in lint.DEBT}
    assert basics_offered == []
    assert seen == known
    assert lint.main() == 0


def test_the_debt_names_both_rows_the_playtest_found():
    known = {(a, c, i): claims for a, c, i, claims in lint.DEBT}
    assert known[("shipped", "furina", "an_invitation")] == (1, 3)
    assert known[("kurage_memory", "kokomi", "to_the_front")] == (1, 3)


def test_the_second_claim_is_a_gate_with_no_debt():
    """*Basic never appears in the draftable pool* is true today, on every
    character, and carries no debt entry -- so it is a plain gate and a basic
    reaching a reward screen is a new defect rather than a known one."""
    for character_id in sorted(loader._character_index()):
        pool = {c.id for cs in rewards.character_pool(character_id).values()
                for c in cs}
        assert not [cid for cid in pool
                    if loader.get_card(cid).rarity == "basic"]


def test_the_lint_bites_on_a_fourteenth_row(monkeypatch):
    """Seen to FAIL: shrink the debt set by one and the gate must go red,
    naming the row it lost. A curated list nobody has watched go red is a
    list, not a gate."""
    monkeypatch.setattr(lint, "DEBT", lint.DEBT[1:])
    assert lint.main() == 1


def test_the_lint_bites_when_a_debt_row_is_fixed(monkeypatch):
    """The other direction, which is what keeps the set shrinking: a DEBT
    entry the tree no longer produces is also red."""
    monkeypatch.setattr(
        lint, "DEBT",
        lint.DEBT + (("shipped", "klee", "kaboom", (1,)),))
    assert lint.main() == 1


def test_the_lint_reads_the_starter_through_the_named_seam():
    """`loader.starter_replaced_whole` (PR #276) is the predicate for a
    whole-starter replacement, and this lint asks it rather than keeping a
    second copy -- an overhaul arm has no `randomized_starter` slot to roll,
    and re-deriving that here is how the two answers drift apart."""
    with lint._arm(KOKOMI_OVERHAUL=True):
        assert loader.starter_replaced_whole("kokomi") is True
        universe = lint._starter_universe("kokomi")
        assert universe == list(C.KOKOMI_OVERHAUL_STARTER_IDS)
    assert loader.starter_replaced_whole("kokomi") is False
    universe = lint._starter_universe("kokomi")
    # Flag off: the printed twelve PLUS the randomized slot's choices, which
    # are starter cards too -- a card the run is dealt and never drafts.
    assert set(loader.starting_deck("kokomi")) <= set(universe)
    assert "shinobu_grass_ring_bond" in universe
