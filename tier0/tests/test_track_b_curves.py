"""Track B's curve generator, and the schema contract between its two feeds.

What can be wrong here in a way that costs a ruling is not the arithmetic --
it is the LABELLING. A curve that loses its feed becomes a balance claim the
moment somebody quotes it (Guardrail 7), and an empty cell that gets filled by
a plausible-looking neighbour becomes evidence about an act nobody has played.
Both are tested; so is the one structural thing no reader can check by eye --
that the C# writer and the Python writer still emit the same keys.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import track_b_curves as tb          # noqa: E402
from understudy import soak                     # noqa: E402


def _fight(**over):
    base = {
        "record": "fight", "feed": "bot", "source": "soak", "seats": 1,
        "act": 1, "floor": 3, "kind": "monster", "turns": 3,
        "outcome": "won", "hp_lost": 5,
        "enemies": [{"name": "Toadpole", "max_hp": 30}],
        "incoming_by_turn": [[1, 8, 1], [2, 12, 2], [3, 0, 0]],
        "enemy_pool_by_turn": [[1, 30], [2, 18], [3, 6]],
        "meters_by_turn": [[1, 0, 1, 3, 2], [2, 10, 3, 3, 1],
                           [3, 12, 3, 3, 0]],
        "block_at_turn_end": [[1, 5], [2, 9], [3, 0]],
        "cards_played": [[1, "Salon Début"], [2, "An Invitation"]],
        "damage_by_source": {"Salon Début": 12.0},
    }
    base.update(over)
    return tb._fight(base)


# ------------------------------------------------------------- labelling ---

def test_a_record_without_a_feed_is_a_bot_record_and_says_so():
    """The soak logs that predate the label are still readable, and they are
    read as what they are rather than as unlabelled."""
    f = tb._fight({"record": "fight", "act": 1, "kind": "monster"})
    assert f.feed == "bot"
    assert f.source == "soak"


def test_every_curve_section_carries_its_feed_and_the_guardrail():
    doc = tb.render([_fight(), _fight(feed="human", source="mod", seats=2,
                                      act=3)])
    assert "Guardrail 7" in doc
    assert "R14" in doc, "B2 must name the rule that keeps it diagnostic"
    assert "feed `bot`" in doc and "feed `human`" in doc
    # The two feeds are never merged into one row.
    for line in doc.splitlines():
        assert not (line.startswith("| bot") and "human" in line)


def test_an_act_with_no_data_stays_empty_and_is_named():
    """The one failure this whole file exists to prevent: an act 2 column
    filled in from act 1 because the shape looked plausible."""
    doc = tb.render([_fight(act=1)])
    assert "| bot | 2 | -- | -- | -- | -- |" in doc
    assert "has nothing in act 2" in doc
    assert "feed `bot` — act 2" not in doc


# ------------------------------------------------------ declared intent ----

def test_an_undeclared_fight_reads_as_undeclared_and_is_never_inferred():
    """R99/4a. A record with no `intent` key is a run nobody declared anything
    for. Nothing looks at `cards_played` and guesses -- an inferred intent
    would make the cut a classification, and the whole point of the cut is
    that a person said so."""
    assert _fight().intent == ""
    assert _fight(intent="Fanfare ").intent == "fanfare"


def test_two_writers_in_one_feed_are_named_rather_than_summed_silently():
    """When a soak drives the game both writers record every fight and both
    are honestly `bot`. A reader that only groups by feed reports a fight count
    that is a fact about how many instruments were running."""
    fights = [_fight(), _fight(source="mod")]
    doc = tb.render(fights)
    assert "Two writers are present" in doc
    assert len(tb.cut_by_source(fights, "soak")) == 1
    assert len(tb.cut_by_source(fights, None)) == 2


def test_one_writer_alone_gets_no_warning():
    assert "Two writers are present" not in tb.render([_fight(), _fight()])


def test_the_cut_keeps_only_what_was_declared():
    fights = [_fight(intent="fanfare"), _fight(intent="salon"), _fight()]
    assert len(tb.cut_by_intent(fights, "fanfare")) == 1
    assert len(tb.cut_by_intent(fights, None)) == 3


def test_the_baseline_cut_survives_a_committed_arm_writing_beside_it():
    """`--intent none` is the only way to regenerate an uncommitted curve once
    a committed soak has written into the same directory. Without it the
    baseline document becomes "whatever was in the folder that day"."""
    fights = [_fight(intent="fanfare"), _fight(), _fight()]
    assert len(tb.cut_by_intent(fights, "none")) == 2


def test_a_cut_document_says_it_is_cut_and_says_what_a_declaration_is():
    """A cut curve that reads like an uncut one is a number waiting to be
    quoted against the wrong denominator."""
    doc = tb.render([_fight(intent="fanfare")], intent="fanfare")
    assert "CUT BY DECLARED INTENT" in doc
    assert "declaration" in doc
    assert "| bot | fanfare | 1 |" in doc


def test_an_uncut_document_still_shows_what_was_declared():
    doc = tb.render([_fight(intent="fanfare"), _fight()])
    assert "CUT BY DECLARED INTENT" not in doc
    assert "| bot | (none) | 1 |" in doc


# ------------------------------------------------------------- arithmetic ---

def test_damage_per_turn_is_the_pools_own_drop():
    """Not the attributed sum: the pool cannot under-count what resolved off a
    play, and `damage_by_source` demonstrably does."""
    assert tb.pool_drops(_fight()) == {1: 12.0, 2: 12.0}


def test_demand_reads_the_telegraph_and_the_observed_clear_pace():
    rows = tb.demand_rows([_fight()])
    turn2 = [r for r in rows if r["turn"] == 2][0]
    assert turn2["incoming"] == 12
    assert turn2["attackers"] == 2
    assert turn2["required_output"] == 10.0          # 30 hp over 3 turns


def test_block_is_read_at_the_end_of_the_turn():
    rows = tb.output_rows([_fight()], {})
    assert [r["block"] for r in sorted(rows, key=lambda r: r["turn"])] == \
        [5.0, 9.0, 0.0]


def test_the_archetype_tie_break_is_declared_and_upgrades_resolve():
    table = {"Grand Salon": ("salon", "fanfare"), "Grand Salon+": ("salon",
                                                                   "fanfare")}
    assert tb.archetype_of("Grand Salon", table) == "salon"
    assert tb.archetype_of("Grand Salon+", table) == "salon"
    assert tb.archetype_of("Strike", table) == "generic"


def test_salon_fill_time_reports_the_turn_and_the_fraction():
    fill = tb.salon_fill([_fight()])["bot"]
    assert fill["first_full"] == [2]                 # cap 3 reached on turn 2
    assert fill["turns"] == 3 and fill["turns_full"] == 2
    assert fill["never_full"] == 0


def test_a_fight_with_no_meter_sample_is_counted_nowhere():
    """A pre-telemetry soak has no meters, and a missing sample is not a zero.
    Inferring one would put "the Salon never filled" into a table describing
    logs that could not have said so."""
    assert tb.salon_fill([_fight(meters_by_turn=[])]) == {}


# --------------------------------------------------- the schema contract ---
#
# The bot feed is written in Python and the human feed in C#. Nothing in either
# language can see the other, so the ONE thing that keeps Track B able to read
# both -- an identical key set -- is invisible to every other check in this
# repo. That is the shape the house turns into a lint.

CS = REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "PlayTelemetry.cs"

# Recorded rather than derived: each asymmetry is a decision, and a test that
# silently tolerated a new one would be no test at all.
BOT_ONLY = {"potions_used"}          # no first-party potion hook exists yet
#
# `selectors` LEFT THIS SET on 2026-08-12 (EB-14). It was bot-only from P1.5
# because the soak records a selector answer it POSTED itself, while the mod
# saw a card leave a pile rather than an offer being taken from a list. The
# mod-side hook into the selection screens now exists
# (`KleeCode/Diagnostics/SelectionTelemetry.cs`), so a selector cut is no
# longer a bot-feed cut. The human feed's four declared LIMITS on the channel
# -- local seat only, in-fight only, no bundle rows, no row for an empty answer
# -- are limits on what the column CONTAINS, not asymmetries of the key set,
# and they live in `understudy/README.md` where a reader of the column will
# find them.
MOD_ONLY = {"character", "ts",       # the seat's character; the wall clock
#                                      (the soak stamps `ts` in `emit`)
            "reactions_by_turn",     # a counter only the C# side can see: the
#                                      wire does not narrate reactions at all
            # EB-18. Per-fight identity and the bomb counters, MOD FEED ONLY,
            # all of them ADDED (no rename, no repurpose -- an addition is
            # free).
            #
            #   run_id, run_instance, fight_index, encounter -- the mod reads
            #     the live run state (`RunState.Rng.StringSeed`,
            #     `CombatRoom.Encounter`, and the `RunState` object's own
            #     identity, which is what tells a REPLAYED seed's second run
            #     from its first). The soak drives the game from outside and
            #     its adapter narrates a fight, not the run object around it;
            #     giving the bot feed these means new wire surface, which is a
            #     piece of work and not this one.
            #   detonations, corpse_detonations -- read straight off
            #     `BombPower`'s per-combat, per-player counters. There is no
            #     wire equivalent at all: a corpse detonation is a fact about
            #     the ORDER of two internal hooks, which no external observer
            #     can see. Probe (e) needed a scripted two-arm run to infer it
            #     once, which is the measurement this counter replaces.
            #
            # SURFACED, not smuggled: any Track B cut on these is a HUMAN-FEED
            # cut until a wire route for them lands.
            "run_id", "run_instance", "fight_index", "encounter",
            "detonations", "corpse_detonations"}


def _csharp_keys() -> set[str]:
    import re
    src = CS.read_text(encoding="utf-8")
    body = src.split("public string ToJson()", 1)[-1]
    keys = set(re.findall(r'Str\(sb,\s*"([a-z_]+)"', body))
    keys |= set(re.findall(r'Pairs\(sb,\s*"([a-z_]+)"', body))
    keys |= set(re.findall(r'sb\.Append\(",?\\"([a-z_]+)\\":', body))
    # `name` only ever appears nested inside `enemies`; `max_hp` appears BOTH
    # there and at the top level, so it stays.
    return keys - {"name"}


def _python_keys() -> set[str]:
    return set(soak.FightTelemetry(act=1, floor=1, kind="monster")
               .as_record().keys())


def test_the_two_feeds_write_the_same_fight_record():
    py, cs = _python_keys(), _csharp_keys()
    assert py - cs == BOT_ONLY, f"keys the mod stopped writing: {py - cs}"
    assert cs - py == MOD_ONLY, f"keys the soak stopped writing: {cs - py}"


def test_the_schema_version_is_stamped_by_both_writers():
    assert soak.SCHEMA_VERSION == "1"
    assert f'SchemaVersion = "{soak.SCHEMA_VERSION}"' in \
        CS.read_text(encoding="utf-8")


def test_both_writers_carry_the_declared_intent():
    """R99/4a rides the schema as an ADDITION, which is free -- but only if
    both writers add it. One writer's key is a column the other feed can never
    fill, and a cut that silently drops a whole feed is worse than no cut."""
    assert "intent" in _python_keys()
    assert "intent" in _csharp_keys()


def test_the_human_feeds_intent_is_declared_and_never_inferred():
    """The C# side reads a file and an environment variable. If it ever grows
    a deck-shaped heuristic, this is the test that says so."""
    src = CS.read_text(encoding="utf-8")
    assert 'IntentFile = "intent.txt"' in src
    assert 'IntentEnvVar = "GITS_TELEMETRY_INTENT"' in src


def test_the_combat_end_seam_is_a_first_party_hook_not_a_harmony_patch():
    """R100/5. `Hook.AfterCombatEnd` and `Hook.AfterCombatVictory` walk the
    same `IterateHookListeners` that already delivers `BeforeCombatStart`, so
    the outcome label costs two overrides. A Harmony patch appearing here
    later is a new patch surface on the combat lifecycle of a lockstep co-op
    game, and it should have to argue for itself."""
    src = CS.read_text(encoding="utf-8")
    assert "public override Task AfterCombatEnd(CombatRoom room)" in src
    assert "public override Task AfterCombatVictory(CombatRoom room)" in src
    assert "HarmonyPatch" not in src


def test_the_human_feed_never_writes_into_the_mod_directory():
    """`deploy.ps1` deletes and re-copies `mods/klee` -- a log written beside
    the dll is destroyed by the next deploy, which is exactly when the newest
    data exists."""
    src = CS.read_text(encoding="utf-8")
    assert 'GlobalizePath("user://")' in src
    assert "Assembly.GetExecutingAssembly().Location" not in src


def test_the_hook_is_registered_on_the_single_subscription_chain():
    """validate.ps1 S6c allows exactly one SubscribeForCombatStateHooks call;
    a listener that is not on that chain receives nothing, in silence."""
    entry = (REPO / "klee-mod" / "KleeCode" / "KleeMod.cs").read_text(
        encoding="utf-8")
    assert entry.count("ModHelper.SubscribeForCombatStateHooks(") == 1
    assert "Diagnostics.PlayTelemetryHooks.Subscribe(combatState)" in entry


def test_the_telemetry_hook_declares_no_balance_constant():
    """A measurement file that grows a tunable `const` becomes a constant the
    parity lint has to mirror. Everything here is a name or a schema string."""
    import re
    src = CS.read_text(encoding="utf-8")
    numeric = re.findall(
        r"^\s*(?:public|internal|private)\s+const\s+"
        r"(?:int|float|double|decimal)\s+(\w+)", src, re.M)
    assert numeric == [], f"telemetry declared balance-shaped constants: {numeric}"


def test_a_torn_last_line_does_not_lose_the_file(tmp_path):
    """A killed game leaves half a line. The rest of the session still counts."""
    p = tmp_path / "play-x.jsonl"
    good = json.dumps({"record": "fight", "feed": "human", "source": "mod",
                       "act": 2, "kind": "elite", "turns": 1})
    p.write_text(good + "\n" + good[:20], encoding="utf-8")
    fights = tb.load([tmp_path])
    assert len(fights) == 1 and fights[0].act == 2
