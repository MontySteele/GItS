"""Per-encounter in-scale audit, with ACT-APPROPRIATE decks.

    python -m tools.encounter_audit 300

Answers one question per encounter: could the decks that actually get here
beat this fight if they arrived healthy? Full HP removes attrition, and using
the REAL decks of runs that reached that act removes progression. What is left
is the encounter itself.

USE THIS, not tools/roster_scale_gap.py, to ask whether a roster is
over-tuned. roster_scale_gap runs ONE fixed deck against everything, which
conflates "this fight is out of scale" with "this is an act-1 deck fighting
act-3 content" -- an error this project made on 2026-07-24 and corrected the
same day. The fixed-deck view is still the right tool for comparing a roster
against the frozen tier 0 battery, which is what it says on the tin.

What the corrected view found: the rosters are NOT uniformly over-tuned. The
median encounter is 99-100% winnable in every act, and the difficulty is
concentrated in a handful of bosses. Runs die to the HP LEDGER across a
mostly-free roster, not to fight difficulty -- so a global difficulty
multiplier would make an already-free roster freer in order to fix three
encounters. See docs/tier05-perf-and-ironclad-act3-notes.md 1.3.
"""
import random
import statistics
import sys
import warnings

warnings.simplefilter("ignore")

from tier0.content import loader                       # noqa: E402
from tier0.engine.combat import run_fight              # noqa: E402
from tier0.pilot.policy import make_pilot              # noqa: E402
from tier05 import acts, draft, model                  # noqa: E402
from tier05 import relics as relic_pool                # noqa: E402

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 400
SEED = 11
REPLAYS = 6
CHARS = [("ref_ironclad", "generic"), ("klee", "demolition"),
         ("furina", "salon")]


def decks_entering_act(res, act):
    """Deck + relics as they stood when the run entered `act` (0-based).

    RunResult only carries the FINAL deck, so approximate with runs that died
    in that act or later: their final deck is what they were carrying through
    it. Runs that got further carry a slightly bigger deck, which biases this
    UPWARD -- i.e. toward the fights looking easier than they are.
    """
    tpl = len(res[0].node_kinds) // res[0].n_acts
    out = []
    for r in res:
        entered = r.death_node is None or r.death_node >= act * tpl
        if entered and r.acts_completed >= act:
            out.append((r.deck_ids, r.relics))
    return out


def main():
    pilot_cache = {}
    print(f"# {RUNS} runs/char, seed {SEED}, realistic. Every encounter "
          f"replayed at FULL HP\n# against the real decks of runs that "
          f"reached that act. {REPLAYS} replays x deck.\n")
    for char, plan in CHARS:
        res = model.run_many(char, plan, plan, draft.POLICIES["assigned"],
                             RUNS, SEED, grant_relics=True, grant_potions=True,
                             jobs=4)
        pilot = pilot_cache.setdefault(plan, make_pilot(
            loader.pilot_weights(plan)))
        print(f"=== {char} ===")
        for act in range(acts.n_acts()):
            decks = decks_entering_act(res, act)
            if len(decks) < 10:
                print(f"  act {act + 1}: only {len(decks)} decks reached it, "
                      f"skipping")
                continue
            pools = acts.pools(act)
            specs = ([("easy", s) for s in pools["easy"]]
                     + [("hard", s) for s in pools["hard"]]
                     + [("elite", s) for s in pools["elite"]]
                     + [("boss", s) for s in acts.boss_pool(act)])
            rows = []
            for tier, spec in specs:
                rng = random.Random(SEED)
                wins = n = 0
                for deck_ids, rids in decks:
                    held = (relic_pool.HeldRelics.hold(list(rids), char)
                            if rids else None)
                    fx = held.combat_effects_for("E", False) if held else None
                    for _ in range(REPLAYS):
                        p = loader.build_player_from_ids(
                            char, list(deck_ids), relic_effects=fx)
                        st = run_fight(p, acts.spawn(spec, rng), pilot,
                                       seed=rng.randrange(2 ** 31))
                        wins += bool(st.player.alive and not st.living_enemies)
                        n += 1
                rows.append((wins / n, tier, spec["id"]))
            rows.sort()
            med = statistics.median(w for w, _, _ in rows)
            print(f"  -- act {act + 1} ({len(decks)} decks, median encounter "
                  f"{med:.0%}) --")
            for w, tier, sid in rows:
                mark = ("  <<< OUT OF SCALE" if w < 0.35 else
                        "  <<< free" if w > 0.98 else "")
                print(f"     {w:6.1%}  {tier:<6} {sid}{mark}")
        print()


if __name__ == "__main__":
    main()
