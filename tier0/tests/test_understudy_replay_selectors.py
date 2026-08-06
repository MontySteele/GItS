"""Probe B2/B3 -- `understudy/replay.py`'s selector consumption, pinned.

The S7 replay let tier0's OWN Spotlight heuristic
(`effects._op_spotlight_designate`) stand in for the answer a real run gave,
because before P1.5 that answer was not on the wire. It is now
(`fight.selectors`), and `--use-selectors` reads it instead.

That extension is RECONSTRUCTION, and these tests pin the three things that
makes it rather than a rule:

  * it reads the RECORDED answer, matched on the offer list as well as the
    chosen name;
  * it pushes that answer through the diagnostic switch tier0 already carries
    (`effects.SPOTLIGHT_FORCE`) and RESTORES it, so a raise inside a replayed
    turn cannot leak a forced designation into the next fight;
  * it is OFF by default, so the committed S7 artefact stays reproducible from
    a corpus that has no selectors in it.

WHAT A GREEN BAR HERE DOES NOT SAY. Nothing about whether tier0 is faithful.
The probe answers are measurements taken against the real game and they live
in `docs/archive/probe-a-block-offset.md` and `docs/archive/probe-b-fanfare-residual.md`.
"""

from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.engine import effects

from understudy import replay


SPOTLIGHT_PAIR = ["Center Stage", "Guest Cast"]


def _fight(selectors, **kw):
    fight = {
        "enemies": [{"name": "probe", "max_hp": 50}],
        "max_hp": 60,
        "hp_trajectory": [[1, 60, 0], [2, 60, 0]],
        "meters_by_turn": [[1, 0, 0, 3, 0], [2, 4, 0, 3, 0]],
        "enemy_pool_by_turn": [[1, 50], [2, 50]],
        "block_at_turn_end": [[1, 0]],
        "selectors": selectors,
        "cards_played": [],
    }
    fight.update(kw)
    return fight


# ------------------------------------------------------ the answer read ----

def test_selector_choice_maps_the_two_answers():
    fight = _fight([[1, "choose", 0, "Center Stage", SPOTLIGHT_PAIR],
                    [2, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]])
    assert replay._selector_choice(fight, 1) == "self"
    assert replay._selector_choice(fight, 2) == "companion"
    assert replay._selector_choice(fight, 3) is None


def test_selector_choice_ignores_a_screen_that_did_not_offer_the_pair():
    """"Center Stage" chosen from a list that did not also contain "Guest
    Cast" is a different screen wearing a familiar word."""
    fight = _fight([[1, "choose", 0, "Center Stage", ["Center Stage", "Encore"]]])
    assert replay._selector_choice(fight, 1) is None


def test_selector_choice_takes_the_last_answer_in_a_round():
    fight = _fight([[1, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR],
                    [1, "choose", 0, "Center Stage", SPOTLIGHT_PAIR]])
    assert replay._selector_choice(fight, 1) == "self"


def test_spotlight_target_is_the_character_or_the_guest_cast_key():
    assert replay._spotlight_target("self", "furina") == "furina"
    assert replay._spotlight_target("companion", "furina") == C.SPOTLIGHT_GUEST_CAST
    assert replay._spotlight_target(None, "furina") is None


# ---------------------------------------------------- the forced switch ----

def _spec(selectors, plays):
    return {
        "fight_id": "test#f1",
        "log": "test",
        "fight": _fight(selectors),
        "turns": [{"round": 1, "hand_at_open": [], "hp_at_open": 60,
                   "plays": [{"card": c, "card_id": None, "upgraded": False,
                              "target_id": None, "target_name": None,
                              "target_hp": None, "status": "ok", "i": i}
                             for i, c in enumerate(plays)]}],
    }


def test_force_is_restored_after_a_turn():
    before = effects.SPOTLIGHT_FORCE
    spec = _spec([[1, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]], ["Stage Presence"])
    replay.l2_rows(spec, replay.Names(), "furina", collections.Counter(),
                   use_selectors=True)
    assert effects.SPOTLIGHT_FORCE == before


def test_force_is_restored_even_when_a_play_raises(monkeypatch):
    """The `finally` is the point: a forced designation that leaked would
    silently re-score every later fight in the same process."""
    before = effects.SPOTLIGHT_FORCE

    def boom(*a, **kw):
        raise RuntimeError("probe")

    monkeypatch.setattr(replay.combat, "play_card", boom)
    spec = _spec([[1, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]], ["Stage Presence"])
    replay.l2_rows(spec, replay.Names(), "furina", collections.Counter(),
                   use_selectors=True)
    assert effects.SPOTLIGHT_FORCE == before


def test_guest_cast_empowers_companion_block_and_center_stage_does_not():
    """The measured C1 mechanism, on the sim side only: the SAME Companion
    card resolves to a different Block under the two recorded answers. The
    engine's half of this comparison is the probe, not the test."""
    names = replay.Names()
    card = names.card("Lynette — Enigmatic Feint", played=True)
    assert card is not None, "the probe's index card must resolve"

    def block_under(arm):
        player = replay._fresh_player(
            "furina", 60, 60, 0, {},
            spotlight=replay._spotlight_target(arm, "furina"))
        state = replay.CombatState(player=player,
                                   enemies=[replay._enemy("probe", 50)],
                                   rng=replay.random.Random(0), turn=1)
        effects.resolve_card(state, card)
        return state.player.block

    assert block_under("companion") > block_under("self")


# ----------------------------------------------------------- the ledger ----

# ------------------------------------- the standing designation (item 1) ----
#
# Errata Batch 2 item 1 / R113 clause C-a. Probe (b) Ledger 2 measured the
# term this section pins: 26 of 27 plays agree exactly with the engine, and
# the single mismatch is the fight's FIRST Ethereal Spotlight -- engine +0,
# tier0 +2, because the reconstruction seeded the turn with the answer the
# turn itself gave, so the play that SET the designation was already covered
# by it. +2 Fanfare per combat, once, in tier0's favour
# (`docs/archive/probe-b-fanfare-residual.md`).

def test_standing_choice_is_the_latest_earlier_round_s_answer():
    fight = _fight([[1, "choose", 0, "Center Stage", SPOTLIGHT_PAIR],
                    [3, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]])
    assert replay._standing_choice(fight, 1) is None      # nothing before it
    assert replay._standing_choice(fight, 2) == "self"
    assert replay._standing_choice(fight, 3) == "self"    # round 3's own
    assert replay._standing_choice(fight, 4) == "companion"  # answer excluded


def test_the_fight_s_first_spotlight_is_not_credited_for_setting_itself():
    """Probe (b) Ledger 2's one mismatch, pinned on the sim side.

    The engine scores a play against the designation standing when the play
    RESOLVES, and the first Ethereal Spotlight of a combat has none. The
    round's recorded answer still arrives -- through `SPOTLIGHT_FORCE`, when
    the designating card resolves -- so the SAME turn's later Furina card is
    income exactly as the engine credits it. Two plays, one credit.
    """
    spec = _spec([[1, "choose", 0, "Center Stage", SPOTLIGHT_PAIR]],
                 ["Ethereal Spotlight", "Stage Presence"])
    ledger: list[dict] = []
    replay.l2_rows(spec, replay.Names(), "furina", collections.Counter(),
                   use_selectors=True, ledger=ledger)
    assert ledger[0]["sim_income"] == C.FANFARE_PER_SPOTLIGHT_CARD


def test_the_engine_itself_already_scores_against_the_standing_designation():
    """The other half of the same law, and the reason item 1 moves no run
    number: `combat.play_card` credits BEFORE the card resolves, and
    `run_fight` opens every combat undesignated -- so tier0's own first
    Spotlight was never credited. Only the reconstruction's seed was."""
    from tier0.content import loader
    player = replay._fresh_player("furina", 60, 60, 0, {})
    assert player.spotlight is None
    state = replay.CombatState(player=player,
                               enemies=[replay._enemy("probe", 50)],
                               rng=replay.random.Random(0), turn=1)
    card = loader.get_card("ethereal_spotlight")
    player.hand.append(card)
    player.energy = 3
    replay.combat.play_card(state, card)
    assert player.spotlight == "furina"      # the designation is now standing
    assert player.fanfare == 0               # the setting play is not covered


def test_ledger_row_decomposes_income_decay_and_the_hp_seam():
    spec = _spec([[1, "choose", 0, "Center Stage", SPOTLIGHT_PAIR]],
                 ["Ethereal Spotlight", "Stage Presence"])
    ledger: list[dict] = []
    replay.l2_rows(spec, replay.Names(), "furina", collections.Counter(),
                   use_selectors=True, ledger=ledger)
    assert len(ledger) == 1
    row = ledger[0]
    assert set(replay.LEDGER_COLUMNS) <= set(row)
    assert row["selector"] == "self"
    assert row["eng_open"] == 0 and row["eng_next_open"] == 4
    # Playing one of Furina's own cards under Center Stage is income, and the
    # ledger names the source rather than reporting a bare number.
    assert row["sim_income"] == C.FANFARE_PER_SPOTLIGHT_CARD
    assert "center_stage" in row["sim_income_by_source"]
    assert row["residual_raw"] == row["sim_after_turn"] - row["eng_next_open"]
    # hp_trajectory is flat in the fixture, so the between-turn HP channel
    # contributes nothing and `full` differs from `post_decay` by zero.
    assert row["hp_drop_to_next_open"] == 0
    assert row["sim_next_open_full"] == row["sim_next_open_post_decay"]


def test_selectors_are_off_by_default():
    """The committed S7 artefact must stay reproducible: a corpus with no
    selectors in it and a corpus read without `--use-selectors` are the same
    measurement, and neither consults `fight.selectors`."""
    spec = _spec([[1, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]], ["Stage Presence"])
    tally: "collections.Counter[str]" = collections.Counter()
    replay.l2_rows(spec, replay.Names(), "furina", tally)
    assert tally["l2_turns_with_selector"] == 0

    tally2: "collections.Counter[str]" = collections.Counter()
    replay.l2_rows(spec, replay.Names(), "furina", tally2, use_selectors=True)
    assert tally2["l2_turns_with_selector"] == 1


# -------------------------------------------- probe B2's scripted driver ----

def _scripted(arm):
    import io
    from understudy import probe_block
    return probe_block.ScriptedPolicy(arm, [], io.StringIO(), turns=8)


def test_probe_takes_the_declared_arm_not_the_policy_s():
    screen = {"state_type": "card_select",
              "card_select": {"cards": [{"name": "Center Stage"},
                                        {"name": "Guest Cast"}]}}
    assert _scripted("center").decide(screen, None).action["index"] == 0
    assert _scripted("guest").decide(screen, None).action["index"] == 1


def test_probe_plays_the_granted_spotlight_before_any_block_card():
    state = {"state_type": "monster", "battle": {"round": 1},
             "player": {"block": 0, "hp": 60, "hand": [
                 {"name": "Regal Bearing", "description": "Gain 3 Block.",
                  "target_type": "self"},
                 {"name": "Ethereal Spotlight", "description": "Designate.",
                  "target_type": "self"}]}}
    action = _scripted("center").decide(state, None).action
    assert action == {"action": "play_card", "card_index": 1}


def test_probe_ends_the_turn_when_no_block_card_is_left():
    state = {"state_type": "monster", "battle": {"round": 1},
             "player": {"block": 0, "hp": 60, "hand": [
                 {"name": "Some Attack", "description": "Deal 6 damage.",
                  "target_type": "enemy"}]}}
    assert _scripted("center").decide(state, None).action == {"action": "end_turn"}


def test_probe_writes_each_reading_as_it_is_taken():
    """A reading held in a list until the run ends is a reading lost the
    moment the run does not -- and the first live attempt did not end."""
    import io, json as _json
    from understudy import probe_block
    buf = io.StringIO()
    pol = probe_block.ScriptedPolicy("center", [], buf, turns=8)
    state = {"state_type": "monster", "battle": {"round": 1},
             "player": {"block": 4, "hp": 60, "hand": [
                 {"name": "Regal Bearing", "description": "Gain 3 Block.",
                  "target_type": "self"}]}}
    pol.decide(state, None)
    rows = [_json.loads(line) for line in buf.getvalue().splitlines() if line]
    assert len(rows) == 1 and rows[0]["block"] == 4 and rows[0]["card"] == "Regal Bearing"


def test_probe_hands_combat_back_after_the_scripted_turns(monkeypatch):
    """The bound exists because a Block-only script never kills anything: the
    first live run reached round 140 of one fight and was still going."""
    from understudy import probe_block
    sentinel = object()
    monkeypatch.setattr(probe_block.policy_v1, "decide",
                        lambda *a, **kw: sentinel)
    state = {"state_type": "monster", "battle": {"round": 9},
             "player": {"block": 0, "hp": 60, "hand": []}}
    assert _scripted("center").decide(state, None) is sentinel


def test_write_tsv_honours_a_column_set():
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "led.tsv")
        replay.write_tsv([{"fight_id": "a", "turn": 1}], path,
                         replay.LEDGER_COLUMNS)
        head = open(path, encoding="utf-8").readline().strip().split("\t")
    assert head == replay.LEDGER_COLUMNS
