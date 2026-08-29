"""THE AFFORDABILITY RUN, and the fixture that stops the two engines drifting.

Spec: `review/active/kokomi-kurage-memory-2026-08-29.md` §14.4. The rule is the
running subtraction the memory CARD's pile view paints: front first, blue while
the bank still reaches, red at the entry it cannot reach, and red for every
entry behind that one — [USER]'s "also red", which is true because
`kurage_fire` holds on an unaffordable front and pays nothing.

WHY IT NEEDED A FIXTURE AT ALL. Every other number the memory display shows
comes from the same expression the RESOLUTION uses, which is why the strip's
numbers never drifted. This is the first display fact with no resolution-side
expression to borrow: nothing in the engine ever asks "how far down the queue
does the bank reach", because the engine only ever fires one memory. So it is
one pure function per engine —

    tier0/engine/effects.py            kurage_affordability
    klee-mod/.../KurageMemory.cs       KurageMemory.Affordability

— and a table BOTH suites read, rather than two loops that happen to agree
today. This module derives the table from the sim and pins it to disk;
`klee-mod/KleeTests/Prototype/KurageMemoryPinTests.cs` runs the C# arithmetic
against the same file. Neither half is the parity claim alone; the composition
is.

Regenerate with `python -m tier0.tests.test_kurage_affordability` after a
DELIBERATE rule change, never to make a red test green.
"""

from __future__ import annotations

import json
from pathlib import Path

from tier0.engine import effects

_VECTORS = (Path(__file__).resolve().parents[2]
            / "docs" / "kurage-affordability-vectors.json")

#: (bank, prices) -> the cases the rule has to get right. Each is a real shape
#: rather than an arbitrary tuple:
_CASES: list[tuple[int, list[int]]] = [
    # The direction's own worked example (§14.3's mock): a bank of 4 over
    # 3/free/3/free. The first three fit — the free one costs nothing and does
    # not move the bank — and the second 3 does not, so it and the free card
    # behind it are held. A FREE CARD CAN BE HELD, and that is the case a naive
    # per-card `bank >= price` test gets wrong.
    (4, [3, 0, 3, 0]),
    # A dry bank. The front runs out immediately and the free card behind it is
    # held rather than fired: nothing past the shortfall fires.
    (0, [3, 0]),
    # A free front on a bank of 1: the old "Charge 1 / 0" frame `EB-198` was
    # filed on. It is PAYABLE, because free is free, and the 3 behind it is
    # where the run stops.
    (1, [0, 3]),
    # An empty memory. No entries, no shortfall, and the run-out index is -1
    # rather than 0 — an empty queue is not a blocked one.
    (0, []),
    # The bank covers the whole queue exactly. The boundary is `<=`: a price
    # equal to what is left is PAYABLE, not a shortfall.
    (6, [3, 3]),
    # One short of that. Same queue, one less Charge.
    (5, [3, 3]),
    # A long queue with a big bank: everything blue, run-out -1.
    (30, [3, 6, 9, 3]),
]


def _derive() -> list[dict]:
    return [
        {
            "bank": bank,
            "prices": prices,
            "states": effects.kurage_affordability(prices, bank),
            "run_out_index": effects.kurage_run_out_index(prices, bank),
        }
        for bank, prices in _CASES
    ]


# --------------------------------------------------------------- the rule --

def test_the_directions_worked_example():
    """§14.3's mock, and the shape the C# pin asserts too."""
    assert effects.kurage_affordability([3, 0, 3, 0], 4) == [
        "payable", "payable", "runs_out", "held"]
    assert effects.kurage_run_out_index([3, 0, 3, 0], 4) == 2


def test_a_dry_bank_holds_the_free_card_behind_the_shortfall():
    assert effects.kurage_affordability([3, 0], 0) == ["runs_out", "held"]
    assert effects.kurage_run_out_index([3, 0], 0) == 0


def test_a_free_front_is_payable_and_the_run_stops_behind_it():
    """`EB-198`'s frame: free is free, and it is not a block."""
    assert effects.kurage_affordability([0, 3], 1) == ["payable", "runs_out"]
    assert effects.kurage_run_out_index([0, 3], 1) == 1


def test_an_empty_memory_has_no_shortfall():
    assert effects.kurage_affordability([], 0) == []
    assert effects.kurage_run_out_index([], 0) == -1


def test_an_exact_bank_pays():
    """The boundary is `<=`. A price equal to what remains is payable, which is
    the same boundary `kurage_fire` uses (`p.charge < entry.price` blocks)."""
    assert effects.kurage_affordability([3, 3], 6) == ["payable", "payable"]
    assert effects.kurage_run_out_index([3, 3], 6) == -1
    assert effects.kurage_affordability([3, 3], 5) == ["payable", "runs_out"]


def test_nothing_is_ever_payable_behind_a_shortfall():
    """The property, stated once rather than case by case: `held` never
    follows anything but `runs_out` or `held`, and there is at most one
    `runs_out`. This is the whole of "also red"."""
    for bank in range(0, 12):
        for prices in ([], [0], [3], [3, 0, 3, 0], [0, 0, 9], [1, 2, 3, 4]):
            states = effects.kurage_affordability(prices, bank)
            assert states.count("runs_out") <= 1
            seen_short = False
            for state in states:
                if seen_short:
                    assert state == "held"
                if state == "runs_out":
                    seen_short = True


def test_the_run_never_spends_more_than_the_bank():
    """The other property: the prices marked payable sum to at most the bank.
    A display that promised a card the bank cannot reach would be exactly the
    lie the shipped gauge's own comment forbids."""
    for bank in range(0, 20):
        prices = [3, 0, 4, 1, 9, 2]
        states = effects.kurage_affordability(prices, bank)
        spent = sum(p for p, s in zip(prices, states) if s == "payable")
        assert spent <= bank


# ------------------------------------------------------------ the fixture --

def test_the_fixture_on_disk_is_the_sims_answer():
    """The file the C# suite reads is the sim's table, not a hand-typed one."""
    assert _VECTORS.exists(), (
        f"missing fixture: {_VECTORS}. Regenerate with "
        "`python -m tier0.tests.test_kurage_affordability`.")
    on_disk = json.loads(_VECTORS.read_text(encoding="utf-8"))
    assert on_disk == _derive()


def test_the_fixture_covers_every_state():
    """A parity table that never exercises `held` would pass with the C# twin
    stopping at the shortfall, which is the one thing [USER] ruled against."""
    states = {s for row in _derive() for s in row["states"]}
    assert states == {"payable", "runs_out", "held"}


if __name__ == "__main__":
    _VECTORS.write_text(json.dumps(_derive(), indent=2) + "\n",
                        encoding="utf-8")
    print(f"wrote {_VECTORS}")
