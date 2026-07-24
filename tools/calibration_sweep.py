"""Grid-search C.ACT_DIFFICULTY_SCALE against the roster.

The dial ships INERT at 1.0 (see the constant); picking its number is a
ruling, and this is the instrument that ruling reads. It sweeps the per-act
multiplier over every character at once, because the question is not only
"what does the anchor win" but "do the characters separate" -- at the 2-4%
floor the world had before this pass, they did not.

    python -m tools.calibration_sweep 300

Base world = shipped state PLUS a guaranteed Ancient energy boon per act
boundary (the missing boss-relic tier, sized at +1.5 to +4pp in the arms and
itself part of the same open ruling; see
docs/tier05-perf-and-ironclad-act3-notes.md 1.5.5). Drop --energy-boon to
sweep against the shipped boon pool instead.
"""
import sys
import warnings

warnings.simplefilter("ignore")

from tier0 import constants as C                              # noqa: E402
from tier05 import draft, model, run_metrics                  # noqa: E402
from tier05 import relics as relic_pool                       # noqa: E402

RUNS = int(next((a for a in sys.argv[1:] if a.isdigit()), 300))
ENERGY_BOON_ARM = "--no-energy-boon" not in sys.argv
SEED = 11
CHARS = [("ref_ironclad", "generic"), ("klee", "demolition"),
         ("furina", "salon"), ("kokomi", "priest")]
_real_build = model.build_node_encounter
_real_pick = relic_pool.ancient_pick
_real_offer = relic_pool.ancient_offer
ENERGY = "prismatic_gem"


def _pick(offer, character):
    return ENERGY if ENERGY in offer else _real_pick(offer, character)


def _offer(rng, held, character, k=3):
    ids = held.ids if hasattr(held, "ids") else (held or [])
    out = _real_offer(rng, held, character, k)
    if ENERGY not in ids and ENERGY not in out:
        out = [ENERGY] + list(out)[:k - 1]
    return out


if ENERGY_BOON_ARM:
    relic_pool.ancient_pick = _pick
    relic_pool.ancient_offer = _offer


def make_comp(per_act, tiers):
    def build(node_kind, rng, draw):
        enemies = _real_build(node_kind, rng, draw)
        mult = per_act.get(draw.act, 1.0)
        if mult == 1.0 or node_kind not in tiers:
            return enemies
        for e in enemies:
            e.hp = e.max_hp = max(1, round(e.hp * mult))
            for ph in e.phases:
                ph["hp"] = max(1, round(int(ph["hp"]) * mult))
                for it in ph["intents"]:
                    if it.get("kind") == "attack":
                        it["amount"] = max(1, round(it["amount"] * mult))
            for it in e.intents:
                if it.get("kind") == "attack":
                    it["amount"] = max(1, round(it["amount"] * mult))
        return enemies
    return build


def row(label, per_act, tiers):
    model.build_node_encounter = make_comp(per_act, tiers)
    out = []
    for char, plan in CHARS:
        res = model.run_many(char, plan, plan, draft.POLICIES["assigned"],
                             RUNS, SEED, grant_relics=True, grant_potions=True,
                             jobs=4)
        s = run_metrics.summarize_runs(res)
        f = {x["act"]: x["cleared_rate"] for x in s["act_funnel"]}
        out.append((char, s["winrate"], f.get(1, 0), f.get(2, 0)))
    model.build_node_encounter = _real_build
    cells = "  ".join(f"{c.split('_')[-1][:4]}:{w:5.1%}" for c, w, _, _ in out)
    anchor = out[0]
    print(f"  {label:<34} {cells}   | anchor funnel "
          f"a1 {anchor[2]:.0%} a2 {anchor[3]:.0%}")


def main():
    print(f"# {RUNS} runs/char, seed {SEED}, realistic, 3 acts")
    print(f"# base world = shipped"
          f"{' + guaranteed Ancient energy boon per act' if ENERGY_BOON_ARM else ''}"
          f"\n# current stamped default: "
          f"{[dict(e) for e in C.ACT_DIFFICULTY_SCALE]}\n")
    print("  === no compensator ===")
    row("1.00 / 1.00 / 1.00", {}, ("E", "B"))
    print("\n  === elites + bosses only ===")
    for a2, a3 in ((0.90, 0.80), (0.85, 0.75), (0.80, 0.70), (0.75, 0.65)):
        row(f"1.00 / {a2:.2f} / {a3:.2f}  (E,B)", {1: a2, 2: a3}, ("E", "B"))
    print("\n  === every fight in acts 2-3 ===")
    for a2, a3 in ((0.90, 0.80), (0.85, 0.75), (0.80, 0.70), (0.75, 0.65)):
        row(f"1.00 / {a2:.2f} / {a3:.2f}  (N,E,B)", {1: a2, 2: a3},
            ("N", "E", "B"))
    print("\n  === act 1 softened too (all fights, all acts) ===")
    for a1, a2, a3 in ((0.95, 0.85, 0.75), (0.90, 0.80, 0.70),
                       (0.85, 0.75, 0.65)):
        row(f"{a1:.2f} / {a2:.2f} / {a3:.2f}  (N,E,B)",
            {0: a1, 1: a2, 2: a3}, ("N", "E", "B"))


if __name__ == "__main__":
    main()
