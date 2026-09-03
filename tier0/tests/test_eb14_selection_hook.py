"""EB-14 — the mod-side hook into the selection screens.

The backlog row, verbatim:

    `selectors` is bot-feed only -- a mod-side hook into the selection screens
    is the open item

Two halves are testable from here and one is not.

WHAT IS NOT: nothing in this repo can execute C#, and the hook only means
anything inside a running game. The owed live smoke is named in the commit and
in `understudy/README.md`; these tests do not pretend to replace it. What they
do replace is the class of regression that a live smoke would only catch
months later -- a patch quietly gaining the power to ANSWER a screen, the row
shape drifting away from the bot feed's, or the sweep result being lost so the
next session rebuilds infrastructure the game already provides.

THE FIRST HALF IS SOURCE FACTS, the same instrument `test_track_b_curves.py`
and `test_eb18_fight_stream.py` use across the same language boundary.

THE SECOND HALF IS EXECUTABLE AND IS THE REAL CLAIM: the row the mod writes is
the row the bot feed writes, so the readers that already exist consume it
without knowing which feed produced it. Those readers are Python
(`understudy/replay.py`, `understudy/trace_replay.py`), so a mod-shaped record
can be fed to them here and the claim is checked rather than asserted.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from understudy import replay, trace_replay

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "SelectionTelemetry.cs"
TELEMETRY = REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "PlayTelemetry.cs"
# The soak is read through `conftest.seam_source("soak")`: `EB-180` split it
# into a facade and seven seams, and both claims below live in a seam now.


def _hook() -> str:
    return HOOK.read_text(encoding="utf-8")


def _telemetry() -> str:
    return TELEMETRY.read_text(encoding="utf-8")


# ------------------------------------------------- the sweep, kept on file --
#
# LAW requires the sweep BEFORE infrastructure is built, and the precedent is
# expensive: "the game exposes no first-party combat-end hook" stood in this
# repo's prose until somebody looked and found `Hook.AfterCombatEnd` /
# `Hook.AfterCombatVictory`, both first-party, both already delivered to a
# listener this mod had subscribed. A sweep whose RESULT is not written down
# gets re-run or, worse, re-guessed.

def test_the_sweep_result_is_recorded_in_the_file_that_acts_on_it():
    """Every surface the sweep examined is named where the next session will
    look: the hook itself. A result kept only in a commit message is a result
    nobody reading the code will find."""
    src = _hook()
    for surface in ("AbstractModel", "BaseLib.Hooks", "MultiPileCardSelect",
                    "ICardSelector", "CardSelectCmd.LogChoice"):
        assert surface in src, f"the sweep no longer names {surface}"
    assert "no first-party observation hook exists" in src


def test_the_sweep_names_the_build_it_was_taken_against():
    """A sweep is a statement about one build, and a later build could add the
    hook this file concluded does not exist -- so the file must name EVERY
    build it has been read against, not just the newest. `v0.111.0` is the
    pinned one (STATE.md, "Mod build environment") since R218; `v0.107.1` is
    the build the original sweep ran on and is kept, not overwritten."""
    src = _hook()
    assert "v0.107.1" in src
    assert "BaseLib 3.3.7.0" in src
    assert "v0.111.0" in src
    assert "3.4.5.0" in src


# ------------------------------------------- the measurement moves nothing --

def test_the_hook_never_installs_a_card_selector():
    """`CardSelectCmd.PushSelector` / `UseSelector` is the one first-party API
    that LOOKS like the answer and is the opposite of it: a pushed
    `ICardSelector` BYPASSES the selection UI and picks for the player. An
    instrument that installs one is not observing a choice, it is making it --
    the worst failure available to a measurement, and silent, because the
    telemetry would look perfectly healthy.

    Scoped to the whole mod, not to this file: the hazard is the API, not the
    filename."""
    for path in (REPO / "klee-mod" / "KleeCode").rglob("*.cs"):
        src = path.read_text(encoding="utf-8")
        # The doc comment in the hook explains why it must not be used, so the
        # ban is on the CALL, not on the word.
        assert "CardSelectCmd.PushSelector(" not in src, path
        assert "CardSelectCmd.UseSelector(" not in src, path


def test_the_patches_only_read():
    """Prefix reads, Postfix watches. A transpiler, a `__result` assignment or
    a `SetResult` here would put a measurement inside the decision path of a
    deterministic lockstep game."""
    src = _hook()
    assert "Transpiler" not in src
    assert "__result =" not in src
    assert "__runOriginal" not in src
    # the CALL, not the word: the doc comment explains why completing a
    # screen's task from here would be a measurement making the choice.
    assert ".SetResult(" not in src
    assert ".TrySetResult(" not in src


def test_every_entry_point_is_wrapped():
    """`PlayTelemetry`'s rule 2, inherited: an exception from a Harmony prefix
    lands in the game's own call path, and one from a task continuation is an
    unobserved fault. Every method that the game can reach catches."""
    src = _hook()
    entry_points = re.findall(r"internal static \w[\w<>?, ]* (\w+)\(", src)
    assert set(entry_points) >= {"Offer", "Answer", "OfferFromHand"}
    assert src.count("catch (Exception") >= len(entry_points)


def test_the_continuation_runs_on_the_completing_thread():
    """Reading `CardModel.Title` off a thread-pool thread in a lockstep co-op
    game is a race the default continuation scheduling would introduce for
    free. The screen sets its result from the UI, so running inline keeps the
    read on the game's own thread."""
    assert "TaskContinuationOptions.ExecuteSynchronously" in _hook()


def test_a_dead_field_lookup_records_nothing_rather_than_an_empty_offer():
    """The offered list is on no public surface, so it is read reflectively.
    If that lookup ever dies, "chosen from a list of zero" is a false
    statement about the game; recording nothing is a true one about the
    instrument."""
    src = _hook()
    assert 'AccessTools.Field(declaring, "_cards")' in src
    assert "selector rows are recorded for that screen" in src
    # the miss is reported once and names the type, not swallowed
    assert "Warned.Add(declaring)" in src


# ------------------------------------------------- the three named surfaces --

def test_the_three_selection_surfaces_are_patched():
    """`card_select` is three screens wearing one name (understudy atlas §5),
    and hand selection is a fourth surface that opens no screen at all. The
    six grid screens share one inherited `CardsSelected()`, so they cost one
    patch between them.

    ONE PATCH IS NOT ONE OFFER READER, and asserting the first used to imply
    the second here. `NCombatPileCardSelectScreen` assigns
    `_cards = Array.Empty<CardModel>()` once and never writes it again -- its
    offer lives in `_pile` + `_filter` -- so the inherited `_cards` read
    succeeded, returned empty, and every combat-pile selection wrote no row at
    all while the boot report said ARMED (round-2 correctness audit, 2026-08-13;
    18 `FromCombatPile` call sites incl. Liquid Memories, three Ancients and
    ten base cards). The patch count stays 3; the per-type resolver is pinned
    below."""
    src = _hook()
    for target in ("NCardGridSelectionScreen", "NChooseACardSelectionScreen",
                   "NPlayerHand"):
        assert f"[HarmonyPatch(typeof({target})" in src, target
    assert src.count("[HarmonyPatch(") == 3


def test_the_combat_pile_offer_is_read_from_the_pile_not_from_cards():
    """The combat pile's `_cards` is permanently empty, so a `_cards` read
    there is a silent no-op. The resolver must branch on the concrete type and
    recompute `_pile.Cards.Where(_filter)` the way `UpdatePileContents` does."""
    src = _hook()
    assert "screen is NCombatPileCardSelectScreen" in src
    assert 'AccessTools.Field(t, "_pile")' in src
    assert 'AccessTools.Field(t, "_filter")' in src
    assert "pile.Cards.Where(filter)" in src


def test_the_screen_label_is_the_concrete_type_and_not_a_re_spelling():
    """The mod can tell the three screens apart and the bridge cannot. Writing
    the bridge's `card_select` here would throw away the one thing this
    vantage has that the bot feed's does not."""
    src = _hook()
    assert "GetType().Name.ToLowerInvariant()" in src
    assert '"card_select"' not in src


def test_the_writer_stays_in_play_telemetry():
    """One writer, one file, one schema. The patch file hands rows over; it
    never opens the log itself, so `feed` and `source` cannot diverge between
    two writers describing the same session."""
    src = _hook()
    assert "PlayTelemetry.SelectorAnswered(" in src
    assert "File.AppendAllText" not in src
    assert "SelectorAnswered" in _telemetry()


def test_the_index_is_found_by_reference_and_not_by_name():
    """Two Strikes in a draw pile are two different cards. Matching the chosen
    card against the offered list by printed title points the row at whichever
    one sorted first, which is a wrong answer that reads as a right one."""
    assert "ReferenceEquals(offered[i], card)" in _telemetry()


def test_the_row_rides_the_open_fight_record():
    """Scoped exactly like the bot feed: `soak.py` records a selector only
    when `self.fight is not None`, because a selector outside a fight belongs
    to no fight. The mod's equivalent is the open record lookup."""
    src = _telemetry()
    assert "Open.TryGetValue(owner, out var record)" in src
    assert "record.Selectors.Add(" in src
    assert "record.Turns" in src            # the round is the fight's counter


# --------------------------------------------- the two feeds stay separate --

def test_a_soak_driven_game_labels_its_mod_written_rows_bot():
    """THE DEFECT NOT TO REPEAT. The mod writes a record for every fight it
    sees, labelled `human` unless told otherwise -- so a soak launched from a
    shell that did not export the variable wrote bot-driven play into the one
    feed whose whole value is that a person produced it. The selector rows
    ride the same record, so they inherit the same label and the same fix:
    the soak sets the variable for the child it launches.

    Now that BOTH writers see the same selections, the label is what keeps one
    soak from looking like a soak plus a playtest."""
    # The FAMILY `EB-180` split the soak into: the launch moved to
    # `soak_session.py` and the selector row to `soak_driver.py`.
    from tier0.tests.conftest import seam_source
    soak = seam_source("soak")
    assert 'env["GITS_TELEMETRY_FEED"] = "bot"' in soak
    telemetry = _telemetry()
    assert 'FeedEnvVar = "GITS_TELEMETRY_FEED"' in telemetry
    # `human` is the reading when nobody said anything, which is the only
    # default that is true by default.
    assert 'IsNullOrWhiteSpace(declared) ? "human"' in telemetry


def test_the_two_writers_are_distinguishable_within_one_feed():
    """A soak-driven session now has two instruments describing the same
    choices: the soak (`source: soak`) and the mod (`source: mod`). Both are
    `feed: bot`, so `source` is what stops a reader double-counting."""
    from tier0.tests.conftest import seam_source
    assert '"source": "soak"' in seam_source("soak")
    assert 'Str(sb, "source", "mod")' in _telemetry()


# ------------------------------- the row shape, checked instead of asserted --
#
# The C# writer is hand-rolled so its key names are greppable text; the ROW is
# hand-rolled for the same reason, and this is where the shape stops being a
# claim. `_mod_row` below is what `PlayTelemetry.ToJson` emits for one
# selector, reconstructed by reading the emitter -- and then handed to the
# readers that were written against the bot feed.

SPOTLIGHT_OFFER = ["Center Stage", "Guest Cast"]


def _mod_row(round_: int, index: int) -> list:
    """One row in the order the C# emitter writes it."""
    return [round_, "nchooseacardselectionscreen", index,
            SPOTLIGHT_OFFER[index], list(SPOTLIGHT_OFFER)]


def test_the_emitter_writes_the_five_columns_in_the_bot_feeds_order():
    """Round, screen, index, chosen, offered -- read off the emitter itself so
    a reordering here is a failing test rather than a silently unreadable
    column."""
    body = _telemetry().split('sb.Append(",\\"selectors\\":[");', 1)
    assert len(body) == 2, "the selectors block moved or was renamed"
    block = body[1].split("sb.Append(',');\n            }", 1)[0]
    assert block.index("row.Round") < block.index("row.Screen")
    assert block.index("row.Screen") < block.index("row.Index")
    assert block.index("row.Index") < block.index("row.Chosen")
    assert block.index("row.Chosen") < block.index("row.Offered")


def test_the_bot_side_reader_resolves_a_mod_written_spotlight_answer():
    """`replay._selector_choice` is the consumer that made the offered list
    load-bearing: "Center Stage" chosen from a list that did not also contain
    "Guest Cast" is a different screen wearing a familiar word. A mod-written
    row answers it exactly as a soak-written one does."""
    fight = {"selectors": [_mod_row(2, 0)]}
    assert replay._selector_choice(fight, 2) == "self"
    fight = {"selectors": [_mod_row(2, 1)]}
    assert replay._selector_choice(fight, 2) == "companion"
    # and the round is honoured, not ignored
    assert replay._selector_choice(fight, 3) is None


def test_a_one_option_spotlight_row_is_declined_by_the_reader():
    """When no companion is in the deck the screen offers Center Stage alone.
    The mod records the offer it saw; the reader declines it, because a choice
    with one arm is not a designation the reconstruction can read."""
    lone = [1, "nchooseacardselectionscreen", 0, "Center Stage",
            ["Center Stage"]]
    assert replay._selector_choice({"selectors": [lone]}, 1) is None


def test_the_standing_designation_reads_a_mod_written_row():
    """R113 clause C-a: what was standing at a round's opening is the answer
    recorded on an EARLIER round. Cross-feed, this is the same arithmetic."""
    fight = {"selectors": [_mod_row(1, 1), _mod_row(3, 0)]}
    assert replay._standing_choice(fight, 2) == "companion"
    assert replay._standing_choice(fight, 4) == "self"
    assert replay._standing_choice(fight, 1) is None


def test_the_divergence_reader_traces_a_mod_written_record():
    """`trace_replay` compares two recordings key by key; `selectors` is one
    of its three trace keys. A mod-written record traces like any other."""
    fight = {"cards_played": [[1, "Kaboom!"]], "meters_by_turn": [[1, 0, 0, 0, 0]],
             "selectors": [_mod_row(1, 1)]}
    traced = trace_replay.trace(fight)
    assert traced["selectors"] == [_mod_row(1, 1)]
    assert "selectors" in trace_replay.TRACE_KEYS


def test_the_human_readable_reconstruction_prints_the_offer():
    """The offered list is printed, not just the answer -- the mod's row
    carries it, so the reconstruction is as legible cross-feed as within."""
    lines = trace_replay.selector_lines({"selectors": [_mod_row(2, 1)]})
    assert len(lines) == 1
    assert "Guest Cast" in lines[0]
    assert "*Guest Cast*" in lines[0]          # the chosen one is marked
    assert "Center Stage" in lines[0]
    assert "nchooseacardselectionscreen" in lines[0]


def test_a_multi_select_screen_writes_one_row_per_card_taken():
    """A grid that takes two cards is two rows sharing one offered list, which
    is what the bot feed produces too (one row per POST). The reader indexes
    each row independently."""
    offered = ["Strike", "Defend", "Bash"]
    rows = [[3, "nsimplecardselectscreen", 0, "Strike", offered],
            [3, "nsimplecardselectscreen", 2, "Bash", offered]]
    lines = trace_replay.selector_lines({"selectors": rows})
    assert len(lines) == 2
    assert "*Strike*" in lines[0] and "*Bash*" in lines[1]


def test_a_record_with_no_selectors_still_reads_as_absent_not_empty():
    """A pre-EB-14 human-feed record carries no `selectors` key at all, and
    `trace_replay` already refuses to read that as evidence of sameness. The
    new key does not change what an old record means."""
    absent = trace_replay.trace({"cards_played": [], "meters_by_turn": []})
    assert absent["selectors"] is trace_replay.NOT_RECORDED
    empty = trace_replay.trace({"cards_played": [], "meters_by_turn": [],
                                "selectors": []})
    assert empty["selectors"] == []


def test_the_row_survives_a_json_round_trip():
    """The emitter quotes by hand. A card title with a quote or a backslash in
    it must not be able to tear the line the reader parses.

    The load-bearing assertion is the second one — the C# escape arm actually
    existing. The first only fixes the row SHAPE a reader expects; a Python
    round-trip cannot say anything about a hand-rolled C# writer.
    """
    row = [1, "nsimplecardselectscreen", 0, 'He said "hi"', ['He said "hi"']]
    assert json.loads(json.dumps({"selectors": [row]}))["selectors"][0] == row
    assert 'case \'"\': sb.Append("\\\\\\"")' in _telemetry()
