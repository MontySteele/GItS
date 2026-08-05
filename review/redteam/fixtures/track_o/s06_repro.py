"""Track O / slice 6 reproducers. Run from the repo root:

    python review/redteam/fixtures/track_o/s06_repro.py

Nothing here modifies an instrument. Each block prints an observed-vs-expected
pair for one finding in review/redteam .../track-o/slice-06.md.
"""
from __future__ import annotations

import collections
import os

from tier0.engine import effects
from understudy import replay

HERE = os.path.dirname(os.path.abspath(__file__))


def s06_1_process_pool_drops_the_force():
    """S06-1: `tier05.model.run_many(jobs>1)` spawns workers that re-import
    tier0, so any module-level knob the caller set -- including the
    process-global `effects.SPOTLIGHT_FORCE` -- is silently the DEFAULT in
    the workers. run_many's docstring: "a wall-clock lever ONLY, never a
    fidelity tradeoff ... An N-job result list is element-for-element
    identical to the serial one"."""
    from tier05 import model, draft

    def go(jobs):
        rs = model.run_many("furina", "salon", "spotlight",
                            draft.POLICIES["assigned"], 8, 11, jobs=jobs)
        return [(r.death_node, sum(r.hp_by_node)) for r in rs]

    base = go(1)
    prev = effects.SPOTLIGHT_FORCE
    try:
        effects.SPOTLIGHT_FORCE = "companion"
        serial, parallel = go(1), go(2)
    finally:
        effects.SPOTLIGHT_FORCE = prev
    print("S06-1 unforced baseline      :", base)
    print("S06-1 forced, jobs=1 (serial):", serial)
    print("S06-1 forced, jobs=2 (pool)  :", parallel)
    print("S06-1 serial moved off baseline:", serial != base,
          "| parallel silently == unforced baseline:", parallel == base)


def s06_2_mixed_corpus_is_pooled_unmarked():
    """S06-2: a corpus mixing a P1.5 log (selectors present) with a pre-P1.5
    log (none) is replayed under TWO reconstruction regimes and written to
    ONE unmarked TSV."""
    rows = []
    for stem in ("s06-selectors", "s06-no-selectors"):
        for spec in replay.fight_specs(os.path.join(HERE, stem + ".jsonl")):
            rows += replay.l2_rows(spec, replay.Names(), "furina",
                                   collections.Counter(), True)
    block = [r for r in rows if r["field"] == "l2.block_at_turn_end"
             and r["turn"] == 1]
    print("S06-2 same combat, two regimes, same TSV:",
          [(r["fight_id"], r["sim_value"], r["engine_value"],
            r["suspected_reading_corruption"]) for r in block])
    print("S06-2 row columns:", replay.COLUMNS)


def s06_3_the_answer_has_no_position_in_the_turn():
    """S06-3: the selector answer is applied from the turn's FIRST card, and
    the interleave that says where it actually happened (the `card_select`
    decision row's `i`) is dropped by `fight_specs`. Two different recordings
    -> byte-identical replay output."""
    def out(stem):
        specs = replay.fight_specs(os.path.join(HERE, stem + ".jsonl"))
        names, tally, led = replay.Names(), collections.Counter(), []
        rows = []
        for s in specs:
            rows += replay.l2_rows(s, names, "furina", tally, True, led)
        for r in rows + led:
            r["fight_id"] = ""
        return rows, led

    a, la = out("s06-interleave-a")   # answered BEFORE the first play
    b, lb = out("s06-interleave-b")   # answered AFTER the last play
    print("S06-3 rows identical:", a == b, "| ledger identical:", la == lb)

    names = replay.Names()
    card = names.card("Lynette — Enigmatic Feint", played=True)

    def block(arm):
        p = replay._fresh_player("furina", 55, 60, 0, {},
                                 spotlight=replay._spotlight_target(arm, "furina"))
        st = replay.CombatState(player=p, enemies=[replay._enemy("probe", 180)],
                                rng=replay.random.Random(0), turn=2)
        p.hand, p.energy = [card], 99
        prev = effects.SPOTLIGHT_FORCE
        if arm:
            effects.SPOTLIGHT_FORCE = arm
        try:
            replay.combat.play_card(st, card)
        finally:
            effects.SPOTLIGHT_FORCE = prev
        return p.block
    print("S06-3 magnitude, one Companion card: "
          "replay(this turn's answer / no answer)=%d  "
          "standing designation=%d" % (block("self"), block("companion")))


def s06_4_unresolved_plays_still_score_the_sim():
    """S06-4: a turn in which `combat.play_card` raised for every card still
    emits a full divergence row charged to the sim, unflagged."""
    specs = replay.fight_specs(os.path.join(HERE, "s06-selectors.jsonl"))
    real = replay.combat.play_card

    def boom(state, card):
        if card.name.startswith("Lynette"):
            raise RuntimeError("unresolvable")
        return real(state, card)

    tally, rows = collections.Counter(), []
    replay.combat.play_card = boom
    try:
        for s in specs:
            rows += replay.l2_rows(s, replay.Names(), "furina", tally, True)
    finally:
        replay.combat.play_card = real
    print("S06-4 l2_play_errors:", tally["l2_play_errors"])
    for r in rows:
        if r["field"] == "l2.enemy_pool_drop":
            print("S06-4  sim=%s eng=%s flag=%s | %s"
                  % (r["sim_value"], r["engine_value"],
                     r["suspected_reading_corruption"], r["action_context"]))


if __name__ == "__main__":
    from s06_make_logs import build  # noqa: E402  (fixtures are data)
    build()
    s06_1_process_pool_drops_the_force()
    s06_2_mixed_corpus_is_pooled_unmarked()
    s06_3_the_answer_has_no_position_in_the_turn()
    s06_4_unresolved_plays_still_score_the_sim()
