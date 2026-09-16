"""`EB-447`, `EB-350`, `EB-374`: three non-combat screens that were printing
less than the game holds.

`EB-447`. THE MASTER DECK. Every deck list this page printed outside a fight
was RECONSTRUCTED from the union of four combat piles, and every guard that
reconstruction has was bought with a defect: `Dazed x 5` listed on the map, a
played Power dropped from the same list, a generated Companion written in
because one fight's union happened to be bigger (`EB-528`). The bridge sends
`Player.Deck` -- the master list the game's own Deck screen draws -- on every
screen now.

`EB-350`. THE GRID. The shop's Card Removal grid printed exactly 25 rows
against a 38-card deck and again against a 29-card one (Kokomi r4d), because
`NCardGrid` is virtualised and the bridge was walking the holders that fit. The
bridge sends the grid's own list, and the removal screen gets the Smith's "not
on this list" model.

`EB-374`. THE OTHER BUTTON. Pael's Wing adds a SACRIFICE option to a card
reward and the bridge sent a boolean (Klee r9). It sends each button's printed
words now, and `sacrifice` is the verb that presses the one that is not a plain
skip.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

import pytest

from understudy import (blindplay, blindplay_board, blindplay_faces,
                        blindplay_grammar)

from tier0.tests.test_understudy_blindplay import (card_reward_state,
                                                   card_select_state,
                                                   combat_state, map_state)


@pytest.fixture(autouse=True)
def _clean_deck_store():
    """The deck memory is on disk and per lane. A test that inherited the
    previous one's deck would be asserting about a run it did not build."""
    blindplay_faces.forget_deck()
    yield
    blindplay_faces.forget_deck()


def _pile_entry(name: str) -> dict:
    return {"name": name, "cost": "1", "description": "Gain 5 Block."}


# --------------------------------------------------------------- `EB-447` ---

def test_the_red_one_the_map_prints_the_runs_own_deck():
    """Seen to FAIL: no screen outside a fight printed a deck at all, and the
    map is the screen every room is entered from."""
    state = copy.deepcopy(map_state())
    state["player"]["character"] = "Klee"
    state["player"]["master_deck"] = [_pile_entry("Jumpy Dumpty"),
                                      _pile_entry("Ka-pow!"),
                                      _pile_entry("Ka-pow!")]
    page = blindplay.observe(state)
    assert "## Your deck" in page
    assert "- **Jumpy Dumpty**" in page
    assert "- **Ka-pow!** × 2" in page


def test_the_master_deck_comes_with_no_fight_old_caveat():
    """The caveat is not a decoration: it told the reader the list was as of
    the last fight. Beside a list that is not, it is simply wrong."""
    state = copy.deepcopy(map_state())
    state["player"]["character"] = "Klee"
    state["player"]["master_deck"] = [_pile_entry("Jumpy Dumpty")]
    page = blindplay.observe(state)
    assert "This is the run's own deck list" in page
    assert "as it stood in the last fight" not in page


def test_the_master_deck_beats_the_pile_union_on_a_combat_screen():
    """Both are on the state inside a fight, and the reconstruction is the one
    that can be wrong: a Power leaves all four piles the moment it resolves."""
    state = copy.deepcopy(combat_state())
    state["player"]["master_deck"] = [_pile_entry("Catalytic Converter")]
    blindplay.observe(state)
    held = blindplay_faces.remembered_deck(state)
    assert [c["title"] for c in held["cards"]] == ["Catalytic Converter"]


def test_a_feed_with_no_master_deck_is_what_it_was():
    """ABSENT IS ABSENT. The union memory answers exactly as it always has,
    and the map still says the list is a fight old."""
    blindplay.observe(combat_state())
    state = copy.deepcopy(map_state())
    state["player"]["character"] = blindplay_faces.remembered_deck(
        combat_state()).get("character", "")
    page = blindplay.observe(state)
    assert "This is the run's own deck list" not in page


def test_the_upgrade_mark_is_read_the_same_way_on_both_reads():
    """`EB-609`'s rule, and the reason one function serves both: the entry's
    flag OR the `+` the game prints on the title."""
    rows = [blindplay_faces._deck_card({"name": "Strike+"}),
            blindplay_faces._deck_card({"name": "Strike",
                                        "is_upgraded": True}),
            blindplay_faces._deck_card({"name": "Strike"})]
    assert [r["upgraded"] for r in rows] == [True, True, False]


# --------------------------------------------------------------- `EB-350` ---

def test_the_red_one_the_removal_screen_names_what_it_will_not_remove():
    """Seen to FAIL: the grid listed 25 rows against a 38-card deck and said
    nothing about the rest, and a seat routed into an Elite planning on it."""
    state = copy.deepcopy(map_state())
    state["player"]["character"] = "Kokomi"
    state["player"]["master_deck"] = [_pile_entry("Coral Guard"),
                                      _pile_entry("Send the Runner"),
                                      _pile_entry("Sango Pearl")]
    blindplay.observe(state)          # remember the run's own deck

    removal = copy.deepcopy(card_select_state())
    removal["player"] = {"character": "Kokomi"}
    page = blindplay.observe(removal)

    assert "## Not on this list, and why" in page
    assert ("- **Sango Pearl** — the game is not offering it for removal on "
            "this screen") in page


def test_the_removal_screen_says_which_deck_the_subtraction_was_against():
    state = copy.deepcopy(map_state())
    state["player"]["character"] = "Kokomi"
    state["player"]["master_deck"] = [_pile_entry("Sango Pearl")]
    blindplay.observe(state)

    removal = copy.deepcopy(card_select_state())
    removal["player"] = {"character": "Kokomi", "master_deck": [
        _pile_entry("Sango Pearl")]}
    page = blindplay.observe(removal)
    assert "the run's own deck list" in page


def test_a_screen_that_is_not_a_removal_screen_gets_no_such_list():
    """Matched on the printed PROMPT, never on the screen name: the game
    spells a dozen different asks `select`."""
    assert blindplay_board.is_removal_screen(
        {"prompt": "Choose a card to Remove."})
    assert not blindplay_board.is_removal_screen(
        {"prompt": "Choose a card to add to your hand."})


def test_a_bridge_that_could_not_read_the_grid_says_so():
    """`grid_complete: false` is the bridge admitting it is back on the
    viewport walk. "These are all the cards" and "these are the cards that fit"
    are different claims, and the second under the first's heading is the r4d
    defect."""
    state = copy.deepcopy(card_select_state())
    state["card_select"]["grid_complete"] = False
    page = blindplay.observe(state)
    assert "could not read the whole grid" in page


def test_a_bridge_that_read_the_grid_prints_no_such_caveat():
    state = copy.deepcopy(card_select_state())
    state["card_select"]["grid_complete"] = True
    assert "could not read the whole grid" not in blindplay.observe(state)
    # And a bridge that sends neither key is unmoved.
    assert "could not read the whole grid" not in blindplay.observe(
        card_select_state())


# --------------------------------------------------------------- `EB-374` ---

def _reward_with(*alternatives: dict) -> dict:
    state = copy.deepcopy(card_reward_state())
    state["card_reward"]["alternatives"] = list(alternatives)
    return state


def test_the_red_one_the_sacrifice_button_is_named_at_last():
    """Seen to FAIL: two card rewards printed `choose` and `skip` and the seat
    holding Pael's Wing never saw the control its whole rule is about."""
    page = blindplay.observe(_reward_with(
        {"index": 0, "name": "Skip"},
        {"index": 1, "name": "Sacrifice"}))
    assert "## Instead of choosing a card" in page
    assert "- **Skip** -- say `skip`" in page
    assert "- **Sacrifice** -- say `sacrifice`" in page


def test_the_verb_presses_the_button_that_is_not_the_plain_skip():
    post = blindplay.act(_reward_with({"index": 0, "name": "Skip"},
                                      {"index": 1, "name": "Sacrifice"}),
                         "sacrifice")["post"]
    assert post == {"action": "skip_card_reward", "alternative_index": 1}


def test_skip_still_presses_index_zero_and_posts_what_it_always_posted():
    """`skip` is what every policy and soak caller sends, and a verb that
    quietly started pressing a different button would be the worse defect."""
    post = blindplay.act(_reward_with({"index": 0, "name": "Skip"},
                                      {"index": 1, "name": "Sacrifice"}),
                         "skip")["post"]
    assert post == {"action": "skip_card_reward"}


def test_sacrifice_refuses_where_there_is_only_a_plain_skip():
    out = blindplay.act(_reward_with({"index": 0, "name": "Skip"}),
                        "sacrifice")
    assert not out["ok"]
    assert "no alternative but the plain skip" in out["refusal"]


def test_sacrifice_refuses_where_there_is_no_alternative_at_all():
    out = blindplay.act(_reward_with(), "sacrifice")
    assert not out["ok"]
    assert "no alternative to choosing" in out["refusal"]


def test_sacrifice_refuses_off_the_card_reward_screen():
    out = blindplay.act(map_state(), "sacrifice")
    assert not out["ok"]


def test_a_button_whose_words_the_feed_could_not_read_keeps_its_row():
    """The count has to keep matching what the verbs can press, and "there is
    a control here and the feed will not say what it does" is the caveat this
    page has printed all along."""
    page = blindplay.observe(_reward_with({"index": 0, "name": None}))
    assert "does not say what it is" in page


def test_the_relic_caveat_comes_off_where_the_words_arrive():
    """A caveat beside the answer is worse than no caveat: it sends the reader
    hunting for words that are four lines above it."""
    state = _reward_with({"index": 0, "name": "Skip"},
                         {"index": 1, "name": "Sacrifice"})
    state["player"] = {"relics": [
        {"id": "PAELS_WING", "name": "Pael's Wing",
         "description": "Whenever you skip a card reward, sacrifice it."}]}
    page = blindplay.observe(state)
    assert "- **Sacrifice** -- say `sacrifice`" in page
    assert "cannot tell you whether that is a plain skip" not in page


def test_the_reader_assigns_the_verbs_the_way_the_bridge_indexes_them():
    rows = blindplay_board.reward_alternatives(
        {"alternatives": [{"index": 0, "name": "Skip"},
                          {"index": 1, "name": "Sacrifice"}]})
    assert [r["verb"] for r in rows] == ["skip", "sacrifice"]
    assert blindplay_board.reward_alternatives({}) == []


def test_the_verb_is_in_the_grammars_own_table():
    assert "sacrifice" in blindplay_grammar.VERBS
