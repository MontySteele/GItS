"""`tier1/analyze.py` can see the whole roster. (E3, audit sec.5.)

The soak instrument predates the roster: `CHARACTER.KLEE` was a module
constant and the accessor was literally named `klee_player`. A soak box
running the shipped mod produces runs for three characters, and this tool
discarded two thirds of them at the door and reported the remainder as "the
soak" — a number that looked like a measurement and was a filter.

Synthetic run records throughout. The real ones live under `%APPDATA%` on
whichever machine ran the soak, which is exactly the kind of input a test must
not depend on (Track A).
"""

from __future__ import annotations

import pytest

from tier1 import analyze


def _run(*characters, deck=None, seed="X"):
    """A run-history record with one seat per named character."""
    return {
        "seed": seed,
        "players": [{"character": c, "deck": list(deck or [])}
                    for c in characters],
        "map_point_history": [],
    }


def test_the_roster_map_covers_every_shipped_character():
    """A fourth character must be ADDED here, not silently missing.

    The curated-map discipline: the game's ids and this repo's names are
    genuinely different vocabularies, so the mapping cannot be derived -- and
    an unmapped character is precisely the failure being fixed.
    """
    assert set(analyze.ROSTER.values()) == {"klee", "furina", "kokomi"}
    for game_id in analyze.ROSTER:
        assert game_id.startswith("CHARACTER.")


def test_a_furina_run_is_no_longer_invisible():
    """The defect, directly. This record used to be dropped by load_runs."""
    run = _run("CHARACTER.FURINA")
    seat = analyze.roster_player(run)
    assert seat["character"] == "CHARACTER.FURINA"


def test_a_coop_lobby_reports_both_seats():
    """`roster_player` returns one seat; `roster_seats` returns all of them.

    A Klee/Kokomi lobby is ONE run and TWO roster seats, and counting it as
    one player is how a co-op soak under-reports the character that happened
    to sit second.
    """
    run = _run("CHARACTER.KLEE", "CHARACTER.KOKOMI")
    assert len(analyze.roster_seats(run)) == 2
    assert analyze.roster_player(run)["character"] == "CHARACTER.KLEE"
    assert analyze.roster_player(run, "CHARACTER.KOKOMI")["character"] \
        == "CHARACTER.KOKOMI"


def test_non_roster_seats_are_ignored():
    """A base-game character in a co-op lobby is not ours to analyse."""
    run = _run("CHARACTER.IRONCLAD", "CHARACTER.KOKOMI")
    assert len(analyze.roster_seats(run)) == 1
    assert analyze.roster_player(run)["character"] == "CHARACTER.KOKOMI"


def test_a_run_with_no_roster_seat_raises_rather_than_guessing():
    """`next()` with no default. An unfiltered base-game run reaching this
    accessor is a caller bug, and a silent fallback would attribute somebody
    else's deck to us."""
    with pytest.raises(StopIteration):
        analyze.roster_player(_run("CHARACTER.IRONCLAD"))


def test_load_runs_defaults_to_the_whole_roster_not_to_klee(tmp_path):
    """The default was Klee by CONSTRUCTION rather than by choice."""
    import json
    history = tmp_path / "history"
    history.mkdir()
    for i, char in enumerate(("CHARACTER.KLEE", "CHARACTER.FURINA",
                              "CHARACTER.KOKOMI", "CHARACTER.IRONCLAD")):
        (history / f"{i}.run").write_text(json.dumps(_run(char)),
                                          encoding="utf-8")

    everyone = analyze.load_runs([history], character=None)
    assert len(everyone) == 3, "the non-roster run must still be excluded"

    just_furina = analyze.load_runs([history], "CHARACTER.FURINA")
    assert len(just_furina) == 1


def test_the_card_prefix_stays_mod_wide():
    """`CARD.KLEEMOD-` is BaseLib's MOD id prefix, not a character's.

    Every card this mod ships carries it whoever owns the card, so splitting
    it per character would invent a distinction the game does not have.
    """
    assert analyze.CARD_PREFIX == "CARD.KLEEMOD-"
    assert analyze.card_id({"id": "CARD.KLEEMOD-ARIA_OF_RECOMPENSE"}) \
        == "aria_of_recompense"
    # Furina's cards go through the same prefix, which is the point.
    assert analyze.card_id({"id": "CARD.KLEEMOD-HIGH_TIDE"}) == "high_tide"


def test_an_unprefixed_card_id_passes_through_untouched():
    """Base-game cards in a modded deck keep their own id."""
    assert analyze.card_id({"id": "CARD.STRIKE"}) == "CARD.STRIKE"
