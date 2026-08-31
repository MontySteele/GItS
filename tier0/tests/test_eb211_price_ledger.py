"""EB-211: the `costs` category stops passing on silence.

R223's battery marks a seat 4 of 6 on `costs`, and until this commit
`qualify.score_costs` ran one check -- `misreads.free_card_misreads`, over the
reader's prose -- and returned PASS whenever it found nothing. A form that
never mentioned a price therefore passed the category, so the mark was
satisfiable by SILENCE and the category could only ever fail a POSITIVE
misread (`review/active/klee-sparks-2026-08-29.md` section 13.8, claim 3).

The fix is a per-play PRICE LEDGER on the form -- bank before, price paid,
bank after -- scored against the costs and the bank the PACKET prints. The
board these tests read is `klee-sparks-r1-t04`, a SEALED packet from a closed
round: Energy 3, Spark 3, and a hand printing Cost 2 / 1 / 2 / 1. Nothing is
written into it (R101b); it is opened read-only, as the battery opens it.

THE FORM SCHEMA CHANGE IS PROSPECTIVE. `price_ledger` is nullable, so every
sealed form, every replay and every hand-written form loads exactly as before;
only `qualify.score_costs` requires it, and there it is required absolutely.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import misreads, qualify, seat, staged_turn

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "review" / "qa"
TURN = "klee-sparks-r1-t04"
TURN_DIR = QA / TURN

# The board, read off the sealed packet rather than restated here.
PACKET = (TURN_DIR / "packet.md").read_text(encoding="utf-8")


def _form(line, ledger):
    """A form that would SURVIVE every falsifier, varying only the ledger."""
    return {
        "turn_id": TURN,
        "grader": {"id": "x", "kind": "llm", "model": "x",
                   "designed_these_cards": False},
        "chosen_line": [{"card": c} for c in line],
        "q1_what_did_you_play": "the line above",
        "q2_other_line_considered": "the other one",
        "q3_what_it_gave_up": "some Block",
        "q4_different_intent": "yes",
        "q4_changed": True,
        "price_ledger": ledger,
    }


def _entry(card, e_before, price, e_after, s_before=3, s_price=0, s_after=3):
    return {"card": card, "energy_before": e_before, "energy_price": price,
            "energy_after": e_after, "spark_before": s_before,
            "spark_price": s_price, "spark_after": s_after}


# Kaboom! (Cost 1) then Duck and Cover (Cost 1), out of a printed Energy 3.
GOOD_LINE = ["Kaboom!", "Duck and Cover"]
GOOD_LEDGER = [_entry("Kaboom!", 3, 1, 2),
               _entry("Duck and Cover", 2, 1, 1)]


# ------------------------------------------------------ the board is real --

def test_the_packet_prints_the_numbers_these_tests_assume():
    """Read the board rather than assert a remembered one: if the sealed
    packet ever changed, every case below would be testing fiction."""
    assert misreads.printed_banks(PACKET)["energy"] == 3
    assert misreads.printed_banks(PACKET)["spark"] == 3
    assert misreads.printed_costs(PACKET)["Kaboom!"] == 1
    assert misreads.printed_costs(PACKET)["Jumpy Dumpty"] == 2


# ------------------------------------------------ THE LOCK: silence FAILS --

def test_a_form_silent_on_every_price_fails_costs():
    """THE ACCEPTANCE, word for word. This exact form -- four honest prose
    answers, a playable line, no mention of a price anywhere -- PASSED the
    category before this commit."""
    ok, why = qualify.score_costs(_form(GOOD_LINE, None), TURN_DIR)
    assert not ok
    assert "silent on every price" in why and "EB-211" in why


def test_an_empty_ledger_is_the_same_silence():
    ok, why = qualify.score_costs(_form(GOOD_LINE, []), TURN_DIR)
    assert not ok and "silent on every price" in why


def test_a_ledger_that_prices_the_board_passes():
    """The other direction, because a check that refuses everything is not a
    check: this is what a reader who read the costs looks like."""
    ok, why = qualify.score_costs(_form(GOOD_LINE, GOOD_LEDGER), TURN_DIR)
    assert ok, why
    assert "against the printed costs" in why


# ------------------------------------------------- what the ledger catches --

def test_a_price_the_packet_contradicts_fails_naming_both_numbers():
    bad = [_entry("Kaboom!", 3, 0, 3), _entry("Duck and Cover", 3, 1, 2)]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok
    assert "the ledger pays 0, the packet prints Cost: 1" in why


def test_a_bank_that_does_not_start_where_the_packet_prints_it_fails():
    bad = [_entry("Kaboom!", 5, 1, 4), _entry("Duck and Cover", 4, 1, 3)]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok and "the bank enters at 5" in why


def test_a_broken_chain_fails_even_where_every_entry_is_self_consistent():
    """Each row's own arithmetic is right and the bank still teleports. This
    is the reading a card ledger exists to catch."""
    bad = [_entry("Kaboom!", 3, 1, 2), _entry("Duck and Cover", 3, 1, 2)]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok and "where the board left it at 2" in why


def test_arithmetic_that_does_not_subtract_fails():
    bad = [_entry("Kaboom!", 3, 1, 3), _entry("Duck and Cover", 3, 1, 2)]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok and "3 - 1 is 2" in why


def test_a_ledger_shorter_than_the_line_fails():
    ok, why = qualify.score_costs(_form(GOOD_LINE, GOOD_LEDGER[:1]), TURN_DIR)
    assert not ok and "for a line of 2 play(s)" in why


def test_a_ledger_out_of_the_lines_order_fails():
    ok, why = qualify.score_costs(
        _form(GOOD_LINE, list(reversed(GOOD_LEDGER))), TURN_DIR)
    assert not ok and "in the line's own order" in why


def test_prose_that_calls_a_priced_card_free_still_fails_first():
    """The first half is untouched and is still checked BEFORE the ledger: a
    perfect ledger does not buy back a misread in the reader's own words."""
    form = _form(GOOD_LINE, GOOD_LEDGER)
    form["q1_what_did_you_play"] = "Kaboom! is free, so I led with it"
    ok, why = qualify.score_costs(form, TURN_DIR)
    assert not ok and "prints Cost: 1" in why


# ------------------------------------------------------------ the Spark half --

def test_the_spark_bank_must_be_stated_where_the_packet_prints_one():
    bad = [dict(GOOD_LEDGER[0], spark_before=None, spark_price=None,
                spark_after=None), GOOD_LEDGER[1]]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok and "the packet prints a Spark bank" in why


def test_a_spark_bank_that_does_not_chain_fails():
    bad = [_entry("Kaboom!", 3, 1, 2, 3, 0, 3),
           _entry("Duck and Cover", 2, 1, 1, 1, 0, 1)]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok and "Spark enters at 1" in why


def test_a_negative_spark_bank_fails():
    bad = [_entry("Kaboom!", 3, 1, 2, 3, 4, -1), GOOD_LEDGER[1]]
    ok, why = qualify.score_costs(_form(GOOD_LINE, bad), TURN_DIR)
    assert not ok and "does not go negative" in why


def test_a_board_with_no_spark_line_wants_the_spark_half_null():
    """`kokomi-slice2-t02` prints no Spark bank. A reader inventing one has
    read a meter the page does not show."""
    kok = QA / "kokomi-slice2-t02"
    packet = (kok / "packet.md").read_text(encoding="utf-8")
    assert "spark" not in misreads.printed_banks(packet)
    line = ["Sounding Line", "Coral Guard"]
    null = [_entry("Sounding Line", 2, 1, 1, None, None, None),
            _entry("Coral Guard", 1, 1, 0, None, None, None)]
    ok, why = qualify.score_costs(_form(line, null), kok)
    assert ok, why
    ok, why = qualify.score_costs(_form(line, [
        _entry("Sounding Line", 2, 1, 1), _entry("Coral Guard", 1, 1, 0)]), kok)
    assert not ok and "prints no Spark bank" in why


# ----------------------------------------------- the refund escape, EB-238 --

SYNTHETIC = """# Staged turn `synthetic`

## You

- HP 40/60
- Block 0
- Energy 3

## Your hand

### Pounding Surprise

- Cost: 1
- Deal 6 damage. Gain 1 Energy.
- (card text read from: bridge)

### Duck and Cover

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)
"""


def test_a_card_whose_printed_body_gives_energy_back_may_end_above_the_sum(
        tmp_path):
    """`misreads.py`'s rule: a false FAIL is worse than a missed one. A card
    that PRINTS a refund is not a reader's arithmetic error (`EB-238`'s
    Pounding Surprise class), and the relaxation is keyed to the printed body
    rather than to a card id.

    No sealed board prints an Energy refund, so the board is written here --
    and it prints *Gain 5 Block* beside it, because "gain" alone is most
    Skills in the game and relaxing on that word would be the check not
    existing.
    """
    (tmp_path / "packet.md").write_text(SYNTHETIC, encoding="utf-8")
    ok, why = qualify.score_costs(
        _form(["Pounding Surprise"],
              [_entry("Pounding Surprise", 3, 1, 3, None, None, None)]),
        tmp_path)
    assert ok, why
    # ... but never BELOW the subtraction: a refund cannot explain spending
    # more than the price.
    ok, why = qualify.score_costs(
        _form(["Pounding Surprise"],
              [_entry("Pounding Surprise", 3, 1, 1, None, None, None)]),
        tmp_path)
    assert not ok and "3 - 1 is 2" in why
    # And the Block-gaining card next to it gets no relaxation at all.
    ok, why = qualify.score_costs(
        _form(["Duck and Cover"],
              [_entry("Duck and Cover", 3, 1, 3, None, None, None)]),
        tmp_path)
    assert not ok and "3 - 1 is 2" in why


# ------------------------------------------------------ the schema is safe --

def test_the_schema_declares_the_ledger_nullable_and_required():
    schema = seat.form_schema()
    field = schema["properties"]["price_ledger"]
    assert field["type"] == ["array", "null"]
    assert "price_ledger" in schema["required"]
    assert schema["additionalProperties"] is False
    entry = field["items"]
    assert entry["additionalProperties"] is False
    assert set(entry["required"]) == set(entry["properties"])
    assert entry["properties"]["spark_before"]["type"] == ["integer", "null"]


def test_a_sealed_form_with_no_ledger_still_loads_unchanged(tmp_path):
    """R101b. Every form written before this field existed is a published
    record, and `staged_turn` must read it exactly as it always did."""
    sealed = sorted(TURN_DIR.glob("form-*.json"))
    assert sealed, "the sealed round should carry at least one form"
    for path in sealed:
        blob = json.loads(path.read_text(encoding="utf-8"))
        assert "price_ledger" not in blob
        assert staged_turn.load_form(path) == blob


def test_the_grader_prompt_asks_for_the_ledger():
    """A field the schema requires and the prompt never mentions is how
    `KLEESPARK-BT2` refused all six of its forms (`EB-239`). Both doors, or
    neither."""
    for doc in ("qa_grader_prompt.md", "qa_form.md"):
        text = (REPO / "understudy" / doc).read_text(encoding="utf-8")
        assert "price_ledger" in text, doc


# ================================ R232: the re-picked `costs` six, pinned ===
#
# R232 (2026-08-30) took the re-pick section 26 owed. The battery file states
# the new rule in prose; this is the same rule as an executable predicate, so
# a later addition made "by taste" is caught by CI rather than by a reader.


def _asks_the_ledgers_question(packet: str) -> tuple[bool, str]:
    """R232's picking rule, (a) and (b), against one printed packet."""
    bank = misreads.printed_banks(packet).get("energy")
    if bank is None:
        return False, "the packet prints no Energy bank, so no chain is scored"
    priced = sorted({c for c in misreads.printed_costs(packet).values() if c})
    if len(priced) < 2:
        return False, (f"the hand prints one non-zero cost ({priced}) -- every "
                       f"line over it moves the bank by the same number")
    if priced[0] + priced[1] > bank:
        return False, (f"the two cheapest different prices are {priced[0]} and "
                       f"{priced[1]}, and the bank is {bank}: no line pays "
                       f"both, so the chain never takes two different steps")
    return True, f"bank {bank} pays {priced[0]} then {priced[1]}"


_COSTS_ITEMS = [i for i in qualify.load_battery() if i.category == "costs"]


@pytest.mark.parametrize("item", _COSTS_ITEMS, ids=lambda i: i.turn_id)
def test_every_costs_board_asks_the_ledgers_question(item):
    """R232's rule (a) and (b): a printed Energy bank, and two DIFFERENT
    non-zero prices jointly payable out of it, so the chain has to take two
    different steps and a reflex subtractor cannot land right by habit."""
    packet = (QA / item.turn_id / "packet.md").read_text(encoding="utf-8")
    ok, why = _asks_the_ledgers_question(packet)
    assert ok, f"{item.turn_id}: {why}"


def test_the_costs_six_carry_both_spark_shapes():
    """R232's rule (c). The Spark half of an entry is scored where the packet
    prints a Spark bank and required NULL where it does not, so the six have
    to contain both or one of those two failures is untestable."""
    with_spark, without = [], []
    for item in _COSTS_ITEMS:
        packet = (QA / item.turn_id / "packet.md").read_text(encoding="utf-8")
        target = (with_spark if "spark" in misreads.printed_banks(packet)
                  else without)
        target.append(item.turn_id)
    assert len(with_spark) >= 2, with_spark
    assert len(without) >= 2, without


@pytest.mark.parametrize("turn_id, why", [
    ("kokomi-slice2-t02", "an Energy bank of 2 against 1, 1, 1 and 2"),
    ("kokomi-slice2-t06", "an Energy bank of 2 against 1, 1, 1 and 2"),
    ("klee-slice1-r3-t03", "no non-zero cost but 1"),
    ("klee-slice1-r3-t04", "no non-zero cost but 1"),
])
def test_the_boards_r232_dropped_really_do_fail_the_new_rule(turn_id, why):
    """SEEN TO FAIL. A picking rule nothing fails is not a rule, and these are
    the four boards the re-pick actually moved out: each is a real sealed
    packet, and each is refused for the reason the battery file gives."""
    packet = (QA / turn_id / "packet.md").read_text(encoding="utf-8")
    ok, _ = _asks_the_ledgers_question(packet)
    assert not ok, f"{turn_id} was dropped for {why} and now passes"


@pytest.mark.parametrize("item", qualify.load_regression(),
                         ids=lambda i: i.id)
def test_the_regression_set_stays_scorable_on_the_half_it_was_picked_for(item):
    """R232 kept the old six as a labelled `free-claim-regression` set. Kept
    means still usable: each prints a bank and prices at least two cards, so
    `free_card_misreads` -- the first half of `score_costs`, still shipped --
    still has something to be wrong about on every one of them."""
    packet = (QA / item.turn_id / "packet.md").read_text(encoding="utf-8")
    assert "energy" in misreads.printed_banks(packet)
    assert sum(1 for c in misreads.printed_costs(packet).values() if c) >= 2
