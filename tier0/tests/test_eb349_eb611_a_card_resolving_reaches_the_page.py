"""`EB-349` / `EB-611`: a card resolving reaches the page, in hit order.

THE STANDING FACT this closes is printed on the page itself, in
`understudy/blindplay_notes.AUTO_TURN_NOTE`: "What it played, what it aimed at
and what each card did are not on this page's data feed -- THERE IS NO RECORD
OF A CARD RESOLVING ON THE WIRE AT ALL." Every screen the bridge sends is an
after-state.

`EB-349` (Kokomi r4d act 3, 1): a relic that plays a turn FOR the player --
Vakuu -- took six openings, five from an empty hand, and nothing said a turn
had happened.

`EB-611` (Klee r23 lane 2 (c) 3): a multi-hit random `Set off` prints only the
after-state, so a seat could confirm WHICH bodies were hit and never the order.
"Rapid Fire on a hallway prints four ordered lines" is the row's acceptance and
it is the first test below.

WHAT THIS FILE PINS is the page half on a feed shaped as the mod sends one, and
the three states the whole feed keeps: absent is a build with no ledger, empty
is a turn nothing resolved -- which PRINTS here, unlike the relic-answer
section -- and populated is the cards in order.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

from understudy import blindplay, blindplay_board

from tier0.tests.test_understudy_blindplay import combat_state


def _hit(target="Damp Cultist", amount=6, blocked=0, combat_id="") -> dict:
    return {"target": target, "amount": amount, "blocked": blocked,
            "combat_id": combat_id}


def _resolved(card="Rapid Fire", hits=(), auto=False, carried=False,
              overflowed=False) -> dict:
    return {"card_id": card.lower().replace(" ", "_"), "card": card,
            "auto_played": auto, "carried": carried,
            "overflowed": overflowed, "hits": list(hits)}


def _state(*rows: dict) -> dict:
    state = copy.deepcopy(combat_state())
    state["player"]["resolutions"] = list(rows)
    return state


def test_the_red_one_rapid_fire_on_a_hallway_prints_four_ordered_lines():
    """`EB-611`'s acceptance, in its own words. The seat could confirm which
    bodies a random multi-hit struck and never in what order."""
    page = blindplay.observe(_state(_resolved(hits=[
        _hit("Damp Cultist"), _hit("Toadpole"), _hit("Damp Cultist"),
        _hit("Toadpole")])))
    assert "## What you played this turn, and what it did" in page
    assert "- **Rapid Fire**" in page
    lines = [ln.strip() for ln in page.splitlines() if ln.strip()[:2] in
             ("1.", "2.", "3.", "4.")]
    assert lines == ["1. **Damp Cultist** -- 6",
                     "2. **Toadpole** -- 6",
                     "3. **Damp Cultist** -- 6",
                     "4. **Toadpole** -- 6"]


def test_two_hits_on_one_body_are_two_lines():
    """`EB-518`'s rule one card over: three entries reading the same number
    divide among three bodies more than one way, and the beat that does not add
    up is the one that struck the same body twice."""
    page = blindplay.observe(_state(_resolved(hits=[_hit(), _hit()])))
    assert page.count("**Damp Cultist** -- 6") == 2


def test_a_hit_that_landed_on_block_is_still_a_place_in_the_order():
    """Dropping it would print three lines for a four-hit card, which is the
    `EB-611` defect wearing a different hat."""
    page = blindplay.observe(_state(_resolved(hits=[
        _hit(amount=0, blocked=6), _hit(amount=6)])))
    assert "1. **Damp Cultist** -- all 6 onto Block" in page
    assert "2. **Damp Cultist** -- 6" in page


def test_a_partly_blocked_hit_prints_both_numbers():
    page = blindplay.observe(_state(_resolved(hits=[
        _hit(amount=2, blocked=4)])))
    assert "1. **Damp Cultist** -- 2 (and 4 onto Block)" in page


def test_the_red_one_an_auto_played_turn_is_on_the_page_at_last():
    """`EB-349`'s acceptance: a seat reconciles an auto-played turn. Vakuu
    played six openings, five from an empty hand, and the page could only say
    that a gap existed."""
    page = blindplay.observe(_state(
        _resolved("Strike", hits=[_hit(amount=6)], auto=True),
        _resolved("Defend", auto=True)))
    assert "- **Strike** *(the game played this one, not you)*" in page
    assert "The rows above are the turn the game took for you" in page


def test_a_turn_the_reader_played_carries_no_auto_note():
    page = blindplay.observe(_state(_resolved("Strike", hits=[_hit()])))
    assert "the game played this one" not in page
    assert "the turn the game took for you" not in page


def test_a_card_that_landed_nothing_countable_says_so():
    """A Power, a draw card, a Block card. The row exists because the card
    resolved; the absence of hits under it is the honest report."""
    page = blindplay.observe(_state(_resolved("Coral Guard")))
    assert "- **Coral Guard**" in page
    assert "Nothing this page can count landed off it." in page


def test_a_row_from_the_unwatched_window_says_so():
    """`EB-710`'s clause, on this ledger and in its words: a card that resolved
    after the player ended their turn is printed rather than dropped."""
    page = blindplay.observe(_state(_resolved("Strike", hits=[_hit()],
                                              carried=True)))
    line = next(ln for ln in page.splitlines()
                if ln.startswith("- **Strike**"))
    assert line.endswith("*(since you ended your last turn)*")


def test_an_overflowing_row_says_so_rather_than_truncating_silently():
    page = blindplay.observe(_state(_resolved(hits=[_hit()],
                                              overflowed=True)))
    assert "more hits landed than this page will list" in page


def test_a_turn_nothing_resolved_prints_its_own_line():
    """The empty list PRINTS here where the relic-answer section's does not:
    on a turn the game played for you it files no rows of yours, and the empty
    line beside the auto-played rows is half of what tells a reader the empty
    hand is the price of a relic."""
    page = blindplay.observe(_state())
    assert "## What you played this turn, and what it did" in page
    assert "Nothing has resolved on your turn yet" in page


def test_a_build_with_no_ledger_is_byte_identical_to_what_it_was():
    assert blindplay_board.resolutions({}) is None
    page = blindplay.observe(combat_state())
    assert "## What you played this turn, and what it did" not in page


def test_the_body_is_named_the_way_the_enemy_list_names_it():
    """`EB-329` / `EB-427`: the page owns the names. A receipt naming a body
    one way while the list four lines down names it another is the mix the r11
    seat read as the numbering having shifted."""
    state = _state(_resolved(hits=[_hit(target="a stale title")]))
    standing = blindplay_board._enemies(state)
    assert standing, "the recorded fixture has enemies to name against"
    state["player"]["resolutions"][0]["hits"][0]["combat_id"] = str(
        standing[0]["combat_id"])

    page = blindplay.observe(state)

    assert "a stale title" not in page
    assert f"**{standing[0]['name']}**" in page


def test_the_reader_carries_the_keys_the_mod_sends():
    rows = blindplay_board.resolutions(
        {"resolutions": [_resolved(hits=[_hit()])]})
    assert rows and sorted(rows[0]) == sorted(
        ["card", "auto_played", "carried", "overflowed", "hits",
         "summoned"])
    assert sorted(rows[0]["hits"][0]) == sorted(
        ["target", "amount", "blocked", "combat_id", "killed"])


def test_the_internal_id_never_crosses_onto_the_page():
    """The mod sends `card_id` beside the title and it is a snake-case
    internal name. `qa_packet.assert_blind` refuses one onto a blind page and
    is right to -- the reader is looking at `Rapid Fire`, not `rapid_fire` --
    so the reader drops it, and a row the mod could not title is not a row."""
    rows = blindplay_board.resolutions(
        {"resolutions": [_resolved(hits=[_hit()])]})
    assert "card_id" not in rows[0]
    assert blindplay_board.resolutions(
        {"resolutions": [{"card": "", "card_id": "rapid_fire",
                          "hits": []}]}) == []


# ------------------------------------------------ a killing hit is a kill ---
#
# THE FIND (2026-09-24, three seats). "Strike -- Nothing this page can count
# landed off it", under the Strike that had just killed Toadpole (2), and the
# same under a Strike+ that took a 3-HP Gardener off the board. The base game
# skips `AfterDamageReceived` for a creature the hit killed, so the ledger fed
# by that hook filed nothing. A build whose ledger hears `AfterDeath` files the
# kill in hit order (`killed`); a build without it has the kill read off the
# board, across exactly one new row.


def _two_body_state(*rows: dict, toadpole: bool = True,
                    round_: int = 2) -> dict:
    """The recorded board plus a 6-HP Toadpole (combat id 2) beside Nibbit."""
    state = _state(*rows)
    state["battle"]["round"] = round_
    enemies = state["battle"]["enemies"]
    if toadpole:
        body = copy.deepcopy(enemies[0])
        body.update({"name": "Toadpole", "combat_id": 2, "hp": 6,
                     "max_hp": 21, "entity_id": "TOADPOLE"})
        enemies.append(body)
    return state


def test_a_kill_the_ledger_filed_prints_as_a_kill_in_hit_order():
    page = blindplay.observe(_state(_resolved("Kurage's Oath", hits=[
        _hit("Nibbit", 7), dict(_hit("Toadpole", 0), killed=True),
        _hit("Nibbit", 7)])))
    assert ("  2. **Toadpole** -- killed (the feed carries no number for a "
            "killing hit)") in page
    assert "1. **Nibbit** -- 7" in page and "3. **Nibbit** -- 7" in page
    assert "Nothing this page can count landed off it." not in page


def test_a_lone_filed_kill_is_not_nothing():
    page = blindplay.observe(_state(_resolved("Strike", hits=[
        dict(_hit("Toadpole", 0), killed=True)])))
    assert "1. **Toadpole** -- killed" in page
    assert "Nothing this page can count" not in page


def test_the_red_one_a_strike_that_emptied_its_target_says_it_killed_it():
    """Seen to FAIL on the 2026-09-24 transcripts: the recorded ledger filed no
    hit for the kill and the page printed "Nothing this page can count landed
    off it". The body stood on the screen before the Strike and is gone from
    the one after, with one row filed between."""
    blindplay.observe(_two_body_state())
    page = blindplay.observe(_two_body_state(_resolved("Strike"),
                                             toadpole=False))
    assert ("  Killed **Toadpole**: standing on the screen before this card, "
            "gone after it.") in page
    assert "Nothing this page can count landed off it." not in page

    # And it stays under that row for the rest of the turn, while a Block
    # card played after it still says it landed nothing.
    page = blindplay.observe(_two_body_state(
        _resolved("Strike"), _resolved("Defend"), toadpole=False))
    lines = page.splitlines()
    at = lines.index("- **Strike**")
    assert lines[at + 1].startswith("  Killed **Toadpole**")
    assert lines[at + 2] == "- **Defend**"
    assert lines[at + 3] == "  Nothing this page can count landed off it."


def test_an_all_enemies_card_lists_the_body_it_killed():
    blindplay.observe(_two_body_state())
    page = blindplay.observe(_two_body_state(
        _resolved("Kurage's Oath", hits=[_hit("Nibbit", 7, combat_id="1")]),
        toadpole=False))
    assert "1. **Nibbit** -- 7" in page
    assert "  Killed **Toadpole**: standing on the screen before" in page


def test_a_kill_the_ledger_filed_is_not_said_twice():
    blindplay.observe(_two_body_state())
    page = blindplay.observe(_two_body_state(
        _resolved("Strike", hits=[dict(_hit("Toadpole", 0, combat_id="2"),
                                       killed=True)]),
        toadpole=False))
    assert "1. **Toadpole** -- killed" in page
    assert "Killed **Toadpole**" not in page


def test_no_card_is_named_for_a_death_it_cannot_be_tied_to():
    """Two rows at once, or a new round, and the page no longer knows which
    card it was -- so it names none."""
    blindplay.observe(_two_body_state())
    page = blindplay.observe(_two_body_state(
        _resolved("Strike"), _resolved("Defend"), toadpole=False))
    assert "Killed **Toadpole**" not in page

    blindplay.observe(_two_body_state(round_=2))
    page = blindplay.observe(_two_body_state(_resolved("Strike"),
                                             toadpole=False, round_=3))
    assert "Killed **Toadpole**" not in page
