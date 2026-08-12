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
    two-arm run to ask this class of question once. The counter answers a
    narrower one on every fight anybody plays: how many bombs of a payload
    landed on a body an EARLIER bomb of that same payload had already killed.
    The corpse test is read per bomb and before that bomb's damage, so the
    bomb that lands the kill counts as landing on a live enemy and only the
    bombs behind it count as corpse detonations -- a single-bomb killing blow
    is invisible to this counter and records 0. `understudy/README.md:253`
    fences the read the same way: `> 0` is a fact; `== 0` is not proof of
    absence.
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
        "intent": "", "run_id": "SEEDONE", "run_instance": "20260807-2200#0",
        "fight_index": 0,
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
    assert {k[0] for k in grouped} == {"A", "B"}
    a = grouped[("A", "20260807-2200#0")]
    assert [f["fight_index"] for f in a] == [0, 1]


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


# ------------------------------------------------------- the replayed seed --
#
# The defect the live smoke of EB-18 found: `PlayTelemetry` restarted
# `fight_index` when the run ID CHANGED, on the reasoning that two runs in a
# session have different seeds. Replaying a seed is a first-class arm
# (P1.5 / R104), so that reasoning is false in ordinary use -- seed 8B97LMCL2F
# played twice in one session gave one `run_id` whose fights ran 0,1,2,6,7,8,
# with no floor gap for a reader to see, and this reader folded the two runs
# into one.

def test_two_runs_of_one_seed_are_two_runs(tmp_path):
    """Same `run_id`, different `run_instance`: two groups, and each numbers
    its own fights from zero."""
    _log(tmp_path,
         _fight(run_instance="S#0", fight_index=0, character="Klee"),
         _fight(run_instance="S#0", fight_index=1, character="Klee"),
         _fight(run_instance="S#1", fight_index=0, character="Furina"),
         _fight(run_instance="S#1", fight_index=1, character="Furina"))
    fights = analyze.load_fights(tmp_path)
    grouped = analyze.fights_by_run(fights)
    assert set(grouped) == {("SEEDONE", "S#0"), ("SEEDONE", "S#1")}
    assert analyze.summarize_fights(fights)["runs"] == 2


def test_the_replayed_seed_joins_one_group_per_history_entry():
    """The join is COUNTED, not broadcast (2026-08-08 fix). The instance token
    splits the FIGHT side only, and the history side cannot be split to match
    -- so two groups against ONE history entry is one match and one surplus.

    Before the fix this reported runs_with_fights=2 / fights_unmatched=0, i.e.
    two finished runs where the history knew one: the second group is the
    replay still IN PROGRESS, which is precisely what this stream exists to
    show. It now surfaces as `ambiguous_replays`."""
    runs = [{"seed": "SEEDONE"}]
    fights = [_fight(run_instance="S#0"), _fight(run_instance="S#1")]
    join = analyze.join_fights_to_runs(runs, fights)
    assert join["runs_with_fights"] == 1
    assert join["fights_matched"] == 1
    assert join["fights_unmatched"] == 1
    assert join["ambiguous_replays"] == 1


def test_both_halves_of_a_replayed_seed_match_when_history_holds_both():
    """The other side of the cardinality rule: two history entries for the
    seed, two fight groups, nothing ambiguous."""
    runs = [{"seed": "SEEDONE"}, {"seed": "SEEDONE"}]
    fights = [_fight(run_instance="S#0"), _fight(run_instance="S#1")]
    join = analyze.join_fights_to_runs(runs, fights)
    assert join["runs_with_fights"] == 2
    assert join["fights_matched"] == 2
    assert join["fights_unmatched"] == 0
    assert join["ambiguous_replays"] == 0


def test_records_without_the_token_group_exactly_as_they_used_to(tmp_path):
    """Backward compatibility, stated as a test: a pre-fix record has no
    `run_instance`, so a replayed seed among them is ONE group -- ambiguous,
    which is what it always was, and never a crash."""
    old = _fight()
    del old["run_instance"]
    other = _fight(fight_index=1)
    del other["run_instance"]
    _log(tmp_path, old, other)
    fights = analyze.load_fights(tmp_path)
    assert set(analyze.fights_by_run(fights)) == {("SEEDONE", "")}
    s = analyze.summarize_fights(fights)
    assert s["runs"] == 1
    assert s["unlinked"] == 0
    assert s["seed_only"] == 2


def test_the_report_names_the_ambiguity_instead_of_hiding_it(capsys):
    old = _fight()
    del old["run_instance"]
    analyze.print_fight_report(analyze.summarize_fights([old]))
    out = capsys.readouterr().out
    assert "predate `run_instance`" in out
    assert "read as one run" in out


def test_a_run_carrying_the_token_prints_no_ambiguity_note(capsys):
    analyze.print_fight_report(analyze.summarize_fights([_fight()]))
    assert "predate `run_instance`" not in capsys.readouterr().out


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
    for key in ("run_id", "run_instance", "fight_index", "encounter",
                "detonations", "corpse_detonations"):
        assert key in keys, f"the human feed stopped writing {key}"


def test_the_new_run_signal_is_the_run_object_and_not_the_seed():
    """`RunManager.State` is assigned once per run (`SetUpNew*` throws if it is
    already set) and nulled in `CleanUp`, so a second embark is necessarily a
    different `RunState` instance. Comparing the SEED instead is the defect
    this test exists to keep out: it reads a replayed seed as one run."""
    src = CS_TELEMETRY.read_text(encoding="utf-8")
    assert "ReferenceEquals(seen, run)" in src
    assert "WeakReference<RunState>" in src
    # the old signal, by its shape: fight numbering keyed off a cached run id
    assert "_runId" not in src


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
