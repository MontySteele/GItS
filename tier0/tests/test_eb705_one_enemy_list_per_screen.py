"""`EB-705`: the enemy list prints once, and a page that doubles it is refused.

THE FIND (Kokomi r31 lane 1, fights 3 and 5; Klee r27 lane 2 before it). The
enemy block printed TWICE on multi-enemy screens, footnotes included, AFTER
`EB-694`'s identical-record dedupe -- so the two copies were not equal field
for field, and the second one reached the page as three more creatures with
three more letters. "The duplicate is above the record level."

TWO HALVES, AND THEY CLOSE DIFFERENT DOORS.

`_enemies` drops a repeat on the `(entity_id, combat_id)` pair alone wherever
the feed sent a combat id: the game mints one per creature per fight, so two
records carrying the same one are the same body however they differ. Without a
combat id the older exact test stands, because `(entity_id, None)` is a pair
two Twig Slimes share and dropping on it would collapse them.

`assert_one_page` covers the enemy list: two identical body rows in one enemy
block are one body printed twice and can be nothing else, because
`_enemy_names` gives every body on a board a printed name of its own. That is
the backstop for a SECOND APPEND -- a caller that concatenates two reads, or a
branch that grows a second `out +=` tomorrow -- which no dedupe on the feed can
see.
"""

from __future__ import annotations

import pytest

from understudy import blindplay


@pytest.fixture(autouse=True)
def _fresh_fight():
    """`EB-428`: the fight's enemy ordinals are process state, so every test
    here starts on a fresh fight."""
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()
from understudy.blindplay_read import _enemies
from understudy.blindplay_render import assert_one_page
from understudy.blindplay_shape import BlindPlayError


def _body(entity: str, cid: int | None, name: str, hp: int, **extra) -> dict:
    row = {"entity_id": entity, "combat_id": cid, "name": name, "hp": hp,
           "max_hp": hp, "block": 0,
           "intents": [{"type": "Attack", "damage": 5}], "status": []}
    row.update(extra)
    return row


THREE = [_body("SLUG", 1, "Slug", 10),
         _body("SLUG", 2, "Slug", 10),
         _body("FUNGI", 3, "Fungi", 14)]


def _combat(enemies: list[dict]) -> dict:
    return {"state_type": "monster",
            "player": {"character": "kokomi", "hp": 60, "max_hp": 80,
                       "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                       "potions": [], "relics": [], "status": [],
                       "draw_pile_count": 5, "discard_pile_count": 0,
                       "exhaust_pile_count": 0},
            "battle": {"round": 2, "enemies": enemies}}


def _bodies(page: str) -> list[str]:
    block = page.split("## The other side", 1)[1].split("## ", 1)[0]
    return [l for l in block.splitlines() if l.startswith("- **")]


# ---------------------------------------------------------------------------
# THE THREE-BODY REPRO
# ---------------------------------------------------------------------------

def test_a_board_sent_twice_with_one_field_moved_prints_one_list():
    """The r31 shape: the same three bodies again, not equal field for field.
    Before this row the page printed six creatures and six letters."""
    doubled = THREE + [dict(b, index=i) for i, b in enumerate(THREE)]
    page = blindplay.observe(_combat(doubled))
    assert len(_bodies(page)) == 3
    assert "Slug (3)" not in page


def test_the_three_bodies_keep_their_own_names_and_letters():
    page = blindplay.observe(_combat(THREE + list(THREE)))
    rows = _bodies(page)
    assert "Slug (1)" in rows[0] and "[A]" in rows[0]
    assert "Slug (2)" in rows[1] and "[B]" in rows[1]
    assert "Fungi" in rows[2] and "[C]" in rows[2]


def test_two_real_bodies_sharing_an_entity_id_are_never_collapsed():
    """`_enemy_names`' `#n` tie-break exists to survive exactly this, and the
    dedupe may not take its job: two Slugs, two combat ids, two rows."""
    assert len(_enemies(_combat(THREE))) == 3


def test_a_feed_with_no_combat_id_keeps_the_old_exact_test():
    """`(entity_id, None)` is a pair two identical bodies share, so a repeat
    is dropped there only where the records match field for field."""
    twins = [_body("SLUG", None, "Slug", 10),
             _body("SLUG", None, "Slug", 9)]
    assert len(_enemies(_combat(twins))) == 2
    same = [_body("SLUG", None, "Slug", 10), _body("SLUG", None, "Slug", 10)]
    assert len(_enemies(_combat(same))) == 1


# ---------------------------------------------------------------------------
# AND THE BACKSTOP
# ---------------------------------------------------------------------------

DOUBLED_PAGE = """# Battle — round 2

## The other side

- **Slug (1)** [A] — HP 10/10
    Intent: Attack
- **Slug (1)** [A] — HP 10/10
    Intent: Attack

## What you can say
"""


def test_assert_one_page_refuses_a_doubled_enemy_list():
    with pytest.raises(BlindPlayError) as caught:
        assert_one_page(DOUBLED_PAGE)
    assert "enemy list twice" in str(caught.value)


def test_assert_one_page_leaves_a_board_of_distinct_bodies_alone():
    assert_one_page(DOUBLED_PAGE.replace("**Slug (1)** [A] — HP 10/10\n    "
                                         "Intent: Attack\n- ", "", 1)
                    .replace("**Slug (1)** [A]", "**Slug (2)** [B]", 1))
    assert_one_page(blindplay.observe(_combat(THREE)))


def test_the_check_does_not_reach_outside_the_enemy_block():
    """Two cards printing one name is `EB-179`'s case and not this one: the
    hand is another section and the check stops at the next heading."""
    page = """# Battle — round 2

## Your hand

- **Strike** — Deal 6 damage.
- **Strike** — Deal 6 damage.

## The other side

- **Slug (1)** [A] — HP 10/10

## What you can say
"""
    assert_one_page(page)
