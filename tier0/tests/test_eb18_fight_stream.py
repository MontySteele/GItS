"""EB-18: per-fight JSON-lines telemetry, and the reader that joins it.

The backlog row, verbatim:

    The mod's per-fight telemetry (C2) was never built -- JSON-lines per
    fight; `tier1/analyze.py` reads per-**run** granularity. Answers the
    corpse-detonation count for free.

Half of that was already true by the time the row was reached: `PlayTelemetry`
writes one JSON-lines record per seat per fight (Track B's human feed). What
was missing is what makes a per-fight record ATTRIBUTABLE and what the row
says it buys --

  * `run_id` / `fight_index` / `encounter` -- a fight record with no run
    linkage is an island; the run's string seed is the same token the game's
    own run history writes as `seed`, so the join costs nothing to either side.
  * `detonations` / `corpse_detonations` -- probe (e) (R118 / Q11) scripted a
    two-arm run to ask, once, whether a killing blow detonates the bombs on the
    body it just made. A counter answers it on every fight anybody plays.
  * a reader on the tier1 side that reads BOTH granularities, and that a
    machine with no fight logs -- or with logs written before any of this --
    analyses exactly as it did before.

Same fence as every other telemetry item: everything here REPORTS and nothing
GRADES. No card, relic or formula reads the new counters; The Big One still
reads `DetonationsThisCombat`, whose value this change does not move.
"""

from __future__ import annotations

import json
from pathlib import Path

from tier1 import analyze

REPO = Path(__file__).resolve().parents[2]
CS_TELEMETRY = REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "PlayTelemetry.cs"
CS_BOMB = REPO / "klee-mod" / "KleeCode" / "Powers" / "BombPower.cs"


# ------------------------------------------------------------- fixtures ---

def _fight(**over) -> dict:
    """One record in the shape `PlayTelemetry.ToJson` writes it."""
    base = {
        "record": "fight", "schema": "1", "feed": "human", "source": "mod",
        "intent": "", "run_id": "SEEDONE", "fight_index": 0,
        "encounter": "ENCOUNTER.TOADPOLES", "seats": 1, "seat_index": 0,
        "character": "Klee", "act": 1, "floor": 1, "kind": "monster",
        "enemies": [{"name": "Toadpole", "max_hp": 30}],
        "hp_start": 70, "hp_end": 64, "max_hp": 70, "hp_lost": 6, "turns": 3,
        "outcome": "won", "cards_played": [[1, "Kaboom!"]],
        "n_cards_played": 1, "damage_by_source": {"Kaboom!": 12},
        "damage_dealt": 12, "damage_taken": 6,
        "detonations": 2, "corpse_detonations": 0, "ts": 1000.0,
    }
    base.update(over)
    return base


def _log(tmp_path: Path, *records: dict, name: str = "play-1.jsonl") -> Path:
    path = tmp_path / name
    path.write_text("".join(json.dumps(r) + "\n" for r in records),
                    encoding="utf-8")
    return path


# ------------------------------------------------------------- the reader --

def test_the_reader_reads_a_fight_per_line(tmp_path):
    _log(tmp_path, _fight(), _fight(fight_index=1, floor=2))
    fights = analyze.load_fights(tmp_path)
    assert [f["fight_index"] for f in fights] == [0, 1]


def test_a_truncated_last_line_costs_one_fight_and_not_the_file(tmp_path):
    """The crash JSON-lines exists to survive: the process died mid-append."""
    path = _log(tmp_path, _fight(), _fight(fight_index=1))
    text = path.read_text(encoding="utf-8")
    path.write_text(text + '{"record": "fight", "run_id": "SEE',
                    encoding="utf-8")
    assert len(analyze.load_fights(tmp_path)) == 2


def test_a_record_that_is_not_a_fight_is_skipped_not_an_error(tmp_path):
    _log(tmp_path, {"record": "session", "note": "hello"}, _fight())
    assert len(analyze.load_fights(tmp_path)) == 1


def test_no_log_directory_is_an_empty_read_and_never_a_crash(tmp_path):
    assert analyze.load_fights(tmp_path / "nothing-here") == []
    assert analyze.summarize_fights([]) == {}


def test_an_empty_summary_prints_nothing(capsys):
    analyze.print_fight_report({})
    assert capsys.readouterr().out == ""


# ------------------------------------------------------------ attribution --

def test_fights_group_by_run_and_sort_by_fight_index(tmp_path):
    _log(tmp_path,
         _fight(run_id="A", fight_index=1),
         _fight(run_id="A", fight_index=0),
         _fight(run_id="B", fight_index=0))
    grouped = analyze.fights_by_run(analyze.load_fights(tmp_path))
    assert set(grouped) == {"A", "B"}
    assert [f["fight_index"] for f in grouped["A"]] == [0, 1]


def test_records_with_no_run_id_are_unlinked_rather_than_one_big_run(tmp_path):
    """Every record written before EB-18 lacks the key. Reading them as a
    shared run would invent a run that never existed."""
    _log(tmp_path, _fight(), {"record": "fight", "act": 1, "outcome": "won"})
    s = analyze.summarize_fights(analyze.load_fights(tmp_path))
    assert s["fights"] == 2
    assert s["runs"] == 1
    assert s["unlinked"] == 1


def test_the_join_is_on_the_run_seed_the_history_already_writes():
    runs = [{"seed": "SEEDONE"}, {"seed": "OTHER"}]
    fights = [_fight(), _fight(fight_index=1), _fight(run_id="INFLIGHT")]
    join = analyze.join_fights_to_runs(runs, fights)
    assert join["runs_with_fights"] == 1
    assert join["fights_matched"] == 2
    # A run still in progress writes no history entry; that is a count, not a
    # warning, and it is exactly the case per-fight telemetry makes visible.
    assert join["fights_unmatched"] == 1


def test_a_coop_fight_is_two_rows_that_share_a_run_and_a_fight_index():
    fights = [_fight(seats=2, seat_index=0, character="Klee"),
              _fight(seats=2, seat_index=1, character="Furina")]
    s = analyze.summarize_fights(fights)
    assert s["coop_fights"] == 2
    assert s["runs"] == 1
    assert s["characters"]["Furina"] == 1


# ------------------------------------------------- the corpse-detonation ---

def test_the_corpse_detonation_count_totals_and_counts_its_fights():
    fights = [_fight(detonations=3, corpse_detonations=2),
              _fight(detonations=1, corpse_detonations=0),
              _fight(detonations=4, corpse_detonations=1)]
    s = analyze.summarize_fights(fights)
    assert s["detonations"] == 8
    assert s["corpse_detonations"] == 3
    assert s["fights_with_corpse"] == 2
    assert s["detonation_fights"] == 3


def test_a_log_that_predates_the_counter_is_absent_not_zero():
    """The denominator is fights that CARRY the key. Counting a pre-EB-18
    record as a zero would turn a fact about the log format into a reading
    about the game."""
    old = _fight()
    del old["detonations"]
    del old["corpse_detonations"]
    s = analyze.summarize_fights([old, _fight(corpse_detonations=1)])
    assert s["fights"] == 2
    assert s["detonation_fights"] == 1
    assert s["corpse_detonations"] == 1


def test_the_report_prints_the_count_and_refuses_to_read_zero_as_absence(capsys):
    analyze.print_fight_report(
        analyze.summarize_fights([_fight(corpse_detonations=0)]))
    out = capsys.readouterr().out
    assert "corpse detonations   0" in out
    assert "not proof of absence" in out


def test_the_report_names_the_feed_because_labelling_is_load_bearing(capsys):
    analyze.print_fight_report(analyze.summarize_fights([_fight()]))
    out = capsys.readouterr().out
    assert "human/mod" in out
    assert "ENCOUNTER.TOADPOLES" in out


# ------------------------------------------------------ the writing side ---
#
# Nothing in this repo can execute the C# writer, so these are source facts --
# the same instrument `test_track_b_curves.py` uses across the same boundary.

def _csharp_keys() -> set[str]:
    """The keys `PlayTelemetry.ToJson` emits, read the way
    `test_track_b_curves.py` reads them (the writer is hand-rolled precisely so
    the key names are greppable text rather than reflected field names)."""
    import re
    body = CS_TELEMETRY.read_text(encoding="utf-8") \
        .split("public string ToJson()", 1)[-1]
    keys = set(re.findall(r'Str\(sb,\s*"([a-z_]+)"', body))
    keys |= set(re.findall(r'Pairs\(sb,\s*"([a-z_]+)"', body))
    keys |= set(re.findall(r'sb\.Append\(",?\\"([a-z_]+)\\":', body))
    return keys


def test_the_mod_writes_the_join_key_and_the_counters():
    keys = _csharp_keys()
    for key in ("run_id", "fight_index", "encounter",
                "detonations", "corpse_detonations"):
        assert key in keys, f"the human feed stopped writing {key}"


def test_the_run_id_is_the_games_own_seed_and_not_an_invented_id():
    """A minted id would be unjoinable against the run history, which is the
    only thing the key is for."""
    assert "StringSeed" in CS_TELEMETRY.read_text(encoding="utf-8")


def test_the_corpse_test_is_read_per_bomb_before_that_bombs_damage():
    """The bomb that lands the kill detonated on a LIVE enemy; only the bombs
    behind it in the same payload are corpse detonations. A single test taken
    before the payload would mislabel the first one."""
    src = CS_BOMB.read_text(encoding="utf-8")
    assert "onCorpse: target is { IsDead: true }" in src


def test_the_corpse_counter_is_per_player_like_the_total_it_rides_beside():
    """EPOCH 2 / D2: a team-wide count inflates a co-op seat's reading. The
    corpse counter is keyed the same way the detonation total is, and cleared
    with it, or the two would disagree in co-op."""
    src = CS_BOMB.read_text(encoding="utf-8")
    assert "Dictionary<Player, int> _corpseDetonationsByPlayer" in src
    assert "_corpseDetonationsByPlayer.Clear();" in src


def test_the_counter_is_read_by_telemetry_and_by_nothing_else():
    """REPORTS, never GRADES. If a card or relic ever reads it, this fails."""
    readers = [p for p in (REPO / "klee-mod" / "KleeCode").rglob("*.cs")
               if "CorpseDetonationsThisCombat" in p.read_text(encoding="utf-8")]
    assert {p.name for p in readers} == {"BombPower.cs", "PlayTelemetry.cs"}


def test_the_big_ones_input_is_untouched_by_the_new_counter():
    """`DetonationsThisCombat` still counts every detonation, corpse ones
    included -- the new counter is a second reading of the same events, not a
    filter on the old one."""
    src = CS_BOMB.read_text(encoding="utf-8")
    body = src.split("private static void RecordDetonation", 1)[-1]
    total = body.index("_detonationsByPlayer[player] =")
    corpse = body.index("if (!onCorpse) return;")
    assert total < corpse, "the total must increment before the corpse gate"
