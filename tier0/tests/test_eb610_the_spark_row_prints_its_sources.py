"""`EB-610`: the Spark row says where this turn's Sparks came from.

THE FIND (Klee r23 lane 2, fight 5, turn 4). "A Spark appeared with no Bomb on
the field": the bank went 2 to 3 across Kaeya and Rapid Fire on a BARE board.
The only sentence naming a Spark source anywhere on that screen is the relic's
-- "whenever a Bomb goes off" -- so the meter contradicted the one rule the
reader had been given, and no line on the page could settle it. The Spark row
says what the word MEANS (`METER_RULES`) and, on round one, where the OPENING
bank came from (`EB-560`); neither can say what this turn did.

THE FEED HAD THE FACT AND THE PAGE COULD NOT REACH IT. `MeterLedger` has kept
per-play gains BY SOURCE since `EB-216`/R225, and `gits/GitsMeterLedger.cs`
publishes them on a SEPARATE ROUTE precisely so the engine's own vocabulary --
`relic:pounding_surprise/detonation` -- never lands on a grading surface
(R101b). So the bridge now also publishes the narrow read the page needs, and
nothing wider: the GAINS of the SPARK meter on the CURRENT turn, each with the
card its row opened on. `blindplay_board.spark_sources` turns the event word
into the printed one before any page sees it.

WHAT THIS FILE PINS is that translation and the line it produces: two sources
in one turn are both named, a Companion play is named by the CARD the player
played and not by the rule that paid, a repeated source folds into one entry
with its total, an unknown event still gets named rather than dropped, and the
three states of the feed (absent, empty, populated) do what the rest of this
page's sections do.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy

from understudy import blindplay, blindplay_board

from tier0.tests.test_understudy_blindplay import combat_state


def _sparked(*rows: dict, bank: int = 3) -> dict:
    """A Klee combat whose wire carries `player.spark_sources`, with a Spark
    meter on the board for the line to hang under."""
    state = copy.deepcopy(combat_state())
    state["character"] = "klee"
    state["player"]["spark_sources"] = list(rows)
    state["player"].setdefault("resources", {})["KLEEMOD_SPARK"] = bank
    return state


def _gain(source: str, amount: int, card: str = "") -> dict:
    return {"source": source, "amount": amount, "card": card}


def _spark_line(page: str) -> str:
    return next((l for l in page.splitlines() if l.strip().startswith(
        "- This turn:")), "")


def test_the_red_one_a_turn_with_two_spark_sources_names_both():
    """The r23 beat, as the ledger records it: a relic's detonation refund and
    a Companion play, on a turn whose board carried no Bomb the reader could
    see. Seen to FAIL: the page printed the bank and nothing else."""
    page = blindplay.observe(_sparked(
        _gain("relic:pounding_surprise/detonation", 1),
        _gain("companion:personal/play", 1, card="Kaeya — Frostgnaw")))
    line = _spark_line(page)
    assert line, "the Spark row printed no source line"
    assert "+1 a detonation" in line
    assert "+1 Kaeya — Frostgnaw" in line
    # In the order they resolved, which is the order they happened.
    assert line.index("detonation") < line.index("Kaeya")


def test_a_play_is_named_by_the_card_the_player_played():
    """The engine's word for that gain is `companion:personal/play`, which is
    true and is not what the player did."""
    page = blindplay.observe(_sparked(
        _gain("companion:personal/play", 1, card="Kaeya — Frostgnaw")))
    assert "+1 Kaeya — Frostgnaw" in _spark_line(page)
    assert "personal" not in page, (
        "the engine's vocabulary must not reach the page")


def test_a_gain_with_no_card_is_named_by_its_event():
    """The case the seat could not explain at all: a Spark with nothing played
    and no Bomb on the board."""
    page = blindplay.observe(_sparked(
        _gain("power:spark_per_turn/turn_start", 1)))
    assert "+1 the start of your turn" in _spark_line(page)


def test_one_source_paying_twice_folds_into_one_entry():
    rows = blindplay_board.spark_sources({"spark_sources": [
        _gain("relic:pounding_surprise/detonation", 1),
        _gain("relic:explosive_frags/detonation", 1)]})
    assert rows == [{"name": "a detonation", "amount": 2}], (
        "two detonations are one source paying twice, and the relic they rode "
        "is not a distinction the page makes")


def test_an_unknown_event_is_still_named():
    """A source this map has never seen is a source the page still names --
    readable, never invented, and never silent."""
    rows = blindplay_board.spark_sources({"spark_sources": [
        _gain("rule:some_new_thing", 2)]})
    assert rows == [{"name": "some new thing", "amount": 2}]


def test_a_spend_is_not_a_source():
    """The row asks where Sparks CAME FROM. The bridge sends positive entries
    only and the reader drops the rest, so both halves refuse a price."""
    assert blindplay_board.spark_sources(
        {"spark_sources": [_gain("rule:threshold_consume", -3)]}) == []


def test_a_turn_with_no_gain_prints_no_line():
    """A reader asking "where did that come from" is only ever asking about a
    number that moved."""
    page = blindplay.observe(_sparked())
    assert not _spark_line(page)
    assert "This turn:" not in page


def test_a_build_with_no_ledger_is_byte_identical_to_what_it_was():
    """The wire's third state: absent is not empty. A build with no klee mod
    to ask sends no key and the page is the page it always was."""
    assert blindplay_board.spark_sources({}) is None
    state = copy.deepcopy(combat_state())
    assert "This turn:" not in blindplay.observe(state)


def test_the_line_hangs_under_the_spark_row_and_nothing_else():
    page = blindplay.observe(_sparked(
        _gain("relic:pounding_surprise/detonation", 1)))
    lines = page.splitlines()
    idx = next(i for i, l in enumerate(lines) if l.strip().startswith(
        "- This turn:"))
    assert lines[idx - 1].startswith("- Spark:"), (
        "the source line belongs to the row whose number it explains")
    assert lines[idx].startswith("    - "), "and hangs under it, indented"
