"""Buckets 1 & 2: the crude crutches. If we just multiply the damage Klee
deals (or the block she puts up) by a flat factor, how big does the knob have
to go before she stops bleeding out? Sizes the problem; not a shipped fix.

Damage knob: scales BASE at effects.deal_damage_to_enemy -- the whole
player->enemy attack pipeline (direct hits, bomb detonations, spark/burst
hits, companion hits). Misses the few direct-HP riders (reaction hp, splash),
so it slightly UNDER-counts her damage; fine for a crude probe.

Block knob: scales the printed amount of the `block` op (OPS['block']) --
i.e. the block HER CARDS put up (duck_and_cover, hide_and_seek, ...). Does
NOT touch potion/relic block: that is loadout, not "the block she does".

Target line = real_ironclad at m=1.0 (the balanced reference): its winrate and
its net %HP-lost/fight are what a "reasonable" Klee should reach.
"""
from __future__ import annotations
import argparse, sys
from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier05 import draft, model

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# --- the knobs, read live by the wrappers -------------------------------
_DMG_MULT = 1.0
_BLK_MULT = 1.0

_orig_deal = effects.deal_damage_to_enemy
_orig_block = effects.OPS["block"]


def _deal(state, enemy, base, *a, **k):
    return _orig_deal(state, enemy, base * _DMG_MULT, *a, **k)


def _block(state, fx, card):
    if _BLK_MULT != 1.0 and "amount" in fx:
        fx = dict(fx)
        fx["amount"] = fx["amount"] * _BLK_MULT
    return _orig_block(state, fx, card)


effects.deal_damage_to_enemy = _deal
effects.OPS["block"] = _block


def measure(character, runs, seed):
    res = model.run_many(character, "generic", "generic",
                         draft.POLICIES["assigned"], runs, seed,
                         grant_relics=True, grant_potions=True)
    max_hp = loader._character_index()[character]["hp"]
    won = sum(1 for r in res if r.won)
    # per-fight HP lost (net of in-combat heals; Klee has no Burning Blood so
    # gross == net for her). survivorship note: a death caps the last fight's
    # loss, so this is a LOWER bound on true bleed -- winrate is the headline.
    losses, norm_losses = [], []
    for r in res:
        kinds = [k for k in r.node_kinds if k in "NEB"]
        for k, fs in zip(kinds, r.fight_stats):
            loss = fs.hp_start - fs.hp_end
            losses.append(loss)
            if k == "N":
                norm_losses.append(loss)
    m = lambda xs: sum(xs) / len(xs) if xs else 0.0
    return {"win": won / len(res), "n": len(res),
            "hp_pf": m(losses), "hp_pf_pct": m(losses) / max_hp,
            "norm_pf": m(norm_losses), "norm_pct": m(norm_losses) / max_hp,
            "maxhp": max_hp}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--knob", choices=["damage", "block"], default="damage")
    ap.add_argument("--mults", type=float, nargs="+",
                    default=[1.0, 1.15, 1.3, 1.5, 1.75, 2.0])
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    # Target line: the balanced reference, unpatched. real_ironclad lives in
    # the gitignored game_ref/ artifact (decompiled reference, intentionally
    # absent on fresh clones) -- so this ONE comparison anchor is not
    # reproducible without it. The Klee sweep below is fully self-contained
    # (her cards ship in docs/klee-cards.yaml), so we skip the target line
    # gracefully rather than crash the whole run.
    try:
        ref = measure("real_ironclad", args.runs, args.seed)
        print(f"\nTARGET LINE  real_ironclad @1.0x: win {ref['win']:.0%} | "
              f"HP/fight {ref['hp_pf']:.1f} ({ref['hp_pf_pct']:.1%} of "
              f"{ref['maxhp']}) | normals {ref['norm_pf']:.1f} "
              f"({ref['norm_pct']:.1%})")
    except KeyError:
        print("\nTARGET LINE  real_ironclad UNAVAILABLE: needs the local "
              "game_ref/ artifact (absent on fresh clones). Klee numbers "
              "below are self-contained; the 40% reference is the balanced "
              "target when game_ref/ is present.")

    print(f"\n=== KLEE, {args.knob.upper()} x knob ({args.runs} runs, seed "
          f"{args.seed}) ===")
    print(f"  {'mult':>5} {'win%':>6} {'HP/fight':>10} {'%maxhp':>8} "
          f"{'normals':>9} {'norm%':>7}")
    for mult in args.mults:
        if args.knob == "damage":
            globals()["_DMG_MULT"] = mult
        else:
            globals()["_BLK_MULT"] = mult
        d = measure("klee", args.runs, args.seed)
        globals()["_DMG_MULT"] = 1.0
        globals()["_BLK_MULT"] = 1.0
        print(f"  {mult:>5.2f} {d['win']:>5.0%} {d['hp_pf']:>10.1f} "
              f"{d['hp_pf_pct']:>7.1%} {d['norm_pf']:>9.1f} {d['norm_pct']:>6.1%}")
