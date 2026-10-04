"""The Furina re-founding sim slice's probes (paper sec.9), act one.

    .venv/Scripts/python.exe -m tier0.harness.furina_v2_probe --runs 1000 --jobs 0
    .venv/Scripts/python.exe -m tier0.harness.furina_v2_probe --probe 6a --runs 200

WHAT A RUN IS. A FIXED probe deck (no draft, no relic but Salon Solitaire, no
potions, no upgrades) walks act one's spine `C.RUN_NODE_TEMPLATE`
(`NNNRETN$ERB`: four monster fights, two elites, the boss) against the act's
own encounter pools (`tier05.acts`): the first three N from the easy pool,
the fourth from the hard pool, elites and the boss drawn the act's way. HP
carries; a rest heals 30% of max HP (`C.REST_HEAL_FRACTION`); treasure and
shop do nothing. A run is an act-one WIN when the boss falls.

Run i is a pure function of `seed + i`, so `--jobs` is a wall-clock lever
only. This is an instrument for the slice's questions (sec.5.1), not a
balance number: no world stamp, no band.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor

from tier0 import constants as C
from tier0.engine import furina_v2 as V
from tier0.engine.combat import run_fight
from tier0.pilot import furina_v2_pilot

STARTER = list(V.STARTER_IDS)

#: Sec.9's probe decks, each the starter plus the cards named. The paper names
#: what each probe compares; the packages are the smallest decks that ask it.
PROBES: dict[str, tuple[str, list[str]]] = {
    "base": ("starter only (Strike x4, Defend x4, Curtain Rise, Rising "
             "Applause; Usher from Salon Solitaire)", []),
    # 1. Mixed cast (Usher, Chevalmarin and one guest) against three guests
    #    with walk-ons. Same guest (Neuvillette) and the same two Salon
    #    summon cards in both; 1b trades the two extra Chevalmarin/Usher
    #    seats for two more guests, so its Salon summons walk on.
    "1a": ("mixed cast: Usher, Chevalmarin, Neuvillette",
           ["fv2_guest_star_neuvillette", "fv2_surintendante_chevalmarin",
            "fv2_surintendante_chevalmarin", "fv2_gentilhomme_usher",
            "fv2_gentilhomme_usher"]),
    "1b": ("three guests (Neuvillette, Clorinde, Charlotte), Salon summons "
           "walk on",
           ["fv2_guest_star_neuvillette", "fv2_guest_star_clorinde",
            "fv2_guest_star_charlotte", "fv2_gentilhomme_usher",
            "fv2_gentilhomme_usher"]),
    # 2. Clorinde Spend-small against a Bravura finale.
    "2a": ("Clorinde Spend-small (Curtain Rise x2 more, Rising Applause x2 "
           "more)",
           ["fv2_guest_star_clorinde", "fv2_curtain_rise", "fv2_curtain_rise",
            "fv2_rising_applause", "fv2_rising_applause"]),
    "2b": ("Bravura finale (Bravura x3, Rising Applause x2 more)",
           ["fv2_bravura", "fv2_bravura", "fv2_bravura",
            "fv2_rising_applause", "fv2_rising_applause"]),
    # 3. Charlotte against a third Salon member in the same (third) seat.
    "3a": ("Usher, Chevalmarin, then Charlotte",
           ["fv2_surintendante_chevalmarin", "fv2_guest_star_charlotte"]),
    "3b": ("Usher, Chevalmarin, then Crabaletta",
           ["fv2_surintendante_chevalmarin", "fv2_mademoiselle_crabaletta"]),
    # 4. "Places, Everyone!" against a plain 1-cost 8 Block.
    "4a": ("Places, Everyone! x2 (+ Chevalmarin, Crabaletta to Cue)",
           ["fv2_places_everyone", "fv2_places_everyone",
            "fv2_surintendante_chevalmarin", "fv2_mademoiselle_crabaletta"]),
    "4b": ("plain 8 Block x2 (+ Chevalmarin, Crabaletta)",
           ["fv2_probe_plain_block", "fv2_probe_plain_block",
            "fv2_surintendante_chevalmarin", "fv2_mademoiselle_crabaletta"]),
    # 5. A draft that finds no Dress Rehearsal: the same eight-card draft,
    #    5b with the Dress Rehearsal replaced by a Defend.
    "5a": ("eight-card draft with Dress Rehearsal",
           ["fv2_surintendante_chevalmarin", "fv2_mademoiselle_crabaletta",
            "fv2_gentilhomme_usher", "fv2_encore", "fv2_places_everyone",
            "fv2_ousia_surge", "fv2_pneuma_refrain", "fv2_dress_rehearsal"]),
    "5b": ("the same draft, no Rehearsal (a Defend in its place)",
           ["fv2_surintendante_chevalmarin", "fv2_mademoiselle_crabaletta",
            "fv2_gentilhomme_usher", "fv2_encore", "fv2_places_everyone",
            "fv2_ousia_surge", "fv2_pneuma_refrain", "defend"]),
    # 6. Escoffier with Take the Stage and Thunderous Applause; 6b doubles
    #    the engine to look for the loop.
    "6a": ("Escoffier, Thunderous Applause, Take the Stage x3",
           ["fv2_guest_star_escoffier", "fv2_thunderous_applause",
            "fv2_take_the_stage", "fv2_take_the_stage",
            "fv2_take_the_stage"]),
    "6b": ("Escoffier, Thunderous Applause x2, Take the Stage x5 (stress)",
           ["fv2_guest_star_escoffier", "fv2_thunderous_applause",
            "fv2_thunderous_applause", "fv2_take_the_stage",
            "fv2_take_the_stage", "fv2_take_the_stage",
            "fv2_take_the_stage", "fv2_take_the_stage"]),
}

FIGHT_KINDS = ("N", "E", "B")
OVER = 12          # sec.9: "flag any turn over 12"


def deck(probe: str) -> list[str]:
    return STARTER + list(PROBES[probe][1])


def _plays_per_turn(state) -> list[int]:
    out: list[int] = []
    for e in state.log:
        ev = e.get("event")
        if ev == "turn_open":
            out.append(0)
        elif ev == "play" and out:
            out[-1] += 1
    return out


def fight_record(state, kind: str) -> dict:
    f = state.player.fv2
    L = f.ledger
    plays = _plays_per_turn(state)
    return {
        "kind": kind,
        "won": state.player.alive and not state.living_enemies,
        "turns": state.turn,
        "gained": L["gained"], "gained_by": dict(L["gained_by"]),
        "spent": L["spent"], "spends": L["spends"], "paid": L["paid"],
        "star_acts": dict(L["star_acts"]),
        "star_skips": dict(L["star_skips"]),
        "cues": L["cues"], "cues_on": dict(L["cues_on"]),
        "cue_whiffs": L["cue_whiffs"],
        "walk_ons": L["walk_ons"], "bows": sum(L["bows"].values()),
        "guest_repeats": L["guest_repeats"],
        "clorinde_procs": L["clorinde_procs"],
        "escoffier_free_summons": L["escoffier_free_summons"],
        "thunderous_draws": L["thunderous_draws"],
        "max_cards": max(plays) if plays else 0,
        "turns_over_12": sum(1 for n in plays if n > OVER),
        "card_cap_hits": sum(1 for e in state.log
                             if e.get("event") == "degeneracy"),
    }


def run_one(probe: str, seed: int) -> dict:
    from tier05 import acts
    rng = random.Random(seed)
    draw = acts.ActDraw(rng, 0)
    hp = max_hp = V.HP
    fights: list[dict] = []
    won = False
    for kind in C.RUN_NODE_TEMPLATE:
        if kind == "R":
            hp = min(max_hp, hp + int(C.REST_HEAL_FRACTION * max_hp))
            continue
        if kind not in FIGHT_KINDS:
            continue
        enemies = acts.spawn(draw.encounter_for(kind, rng), rng)
        player = V.build_player(deck(probe), hp=hp, max_hp=max_hp)
        state = run_fight(player, enemies, furina_v2_pilot.pilot,
                          seed=rng.randrange(2 ** 31))
        fights.append(fight_record(state, kind))
        hp = state.player.hp
        if not fights[-1]["won"]:
            break
        if kind == "B":
            won = True
    return {"seed": seed, "won": won, "fights": fights, "hp_end": hp}


#: YARDSTICKS, not probes: other starters walked down the same spine with
#: the generic pilot, so an act-one win rate has something to stand beside.
REFERENCES = {
    "ref:ref_ironclad": "the reference Ironclad starter, generic pilot",
    "ref:furina": "today's Furina (the Stage) starter, generic pilot",
}


def run_reference(character: str, seed: int) -> dict:
    from tier0.content import loader
    from tier0.pilot.policy import make_pilot
    from tier05 import acts
    pilot = make_pilot(loader.pilot_weights("generic"))
    rng = random.Random(seed)
    draw = acts.ActDraw(rng, 0)
    hp = max_hp = loader._character_index()[character]["hp"]
    fights: list[dict] = []
    won = False
    for kind in C.RUN_NODE_TEMPLATE:
        if kind == "R":
            hp = min(max_hp, hp + int(C.REST_HEAL_FRACTION * max_hp))
            continue
        if kind not in FIGHT_KINDS:
            continue
        enemies = acts.spawn(draw.encounter_for(kind, rng), rng)
        player = loader.build_player(character, "starter")
        player.hp, player.max_hp = hp, max_hp
        state = run_fight(player, enemies, pilot,
                          seed=rng.randrange(2 ** 31))
        plays = _plays_per_turn(state)
        rec = {"kind": kind, "turns": state.turn,
               "won": state.player.alive and not state.living_enemies,
               "max_cards": max(plays) if plays else 0,
               "turns_over_12": sum(1 for n in plays if n > OVER),
               "card_cap_hits": 0}
        for key in ("gained", "spent", "spends", "paid", "cues", "walk_ons",
                    "bows", "clorinde_procs", "escoffier_free_summons"):
            rec[key] = 0
        for key in ("star_skips", "star_acts", "cues_on"):
            rec[key] = {}
        fights.append(rec)
        hp = state.player.hp
        if not rec["won"]:
            break
        if kind == "B":
            won = True
    return {"seed": seed, "won": won, "fights": fights, "hp_end": hp}


def _one(probe: str, seed: int) -> dict:
    if probe.startswith("ref:"):
        return run_reference(probe[4:], seed)
    return run_one(probe, seed)


def _chunk(args) -> list[dict]:
    probe, lo, hi = args
    return [_one(probe, s) for s in range(lo, hi)]


def run_probe(probe: str, runs: int, seed: int, jobs: int = 1) -> list[dict]:
    if jobs == 1:
        return [_one(probe, seed + i) for i in range(runs)]
    import os
    workers = os.cpu_count() if jobs <= 0 else jobs
    step = max(1, runs // (workers * 4))
    chunks = [(probe, seed + lo, seed + min(runs, lo + step))
              for lo in range(0, runs, step)]
    out: list[dict] = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for part in ex.map(_chunk, chunks):
            out.extend(part)
    return out


def summarize(results: list[dict]) -> dict:
    n = len(results)
    fights = [f for r in results for f in r["fights"]]
    nf = max(1, len(fights))

    def mean(key):
        return sum(f[key] for f in fights) / nf

    skips = collections.Counter()
    star_acts = collections.Counter()
    cues_on = collections.Counter()
    for f in fights:
        skips.update(f["star_skips"])
        star_acts.update(f["star_acts"])
        cues_on.update(f["cues_on"])
    return {
        "runs": n,
        "act1_win": sum(r["won"] for r in results) / max(1, n),
        "fights": len(fights),
        "fight_win": sum(f["won"] for f in fights) / nf,
        "turns": mean("turns"),
        "gained": mean("gained"), "spent": mean("spent"),
        "paid": mean("paid"), "spends": mean("spends"),
        "star_skips": sum(skips.values()) / nf,
        "star_skips_by": dict(skips), "star_acts_by": dict(star_acts),
        "cues": mean("cues"), "cues_on": dict(cues_on),
        "walk_ons": mean("walk_ons"), "bows": mean("bows"),
        "clorinde_procs": mean("clorinde_procs"),
        "escoffier_free_summons": mean("escoffier_free_summons"),
        "max_cards": max((f["max_cards"] for f in fights), default=0),
        "mean_max_cards": mean("max_cards"),
        "turns_over_12": sum(f["turns_over_12"] for f in fights),
        "card_cap_hits": sum(f["card_cap_hits"] for f in fights),
    }


def _fmt_counter(c: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items(),
                                                     key=lambda kv: -kv[1]))


def print_table(rows: dict, out=sys.stdout) -> None:
    out.write("probe | act-1 win | fights | gained | spent | paid | "
              "star skips | cues | walk-ons | bows | max cards | turns >12\n")
    for name, s in rows.items():
        out.write(f"{name} | {s['act1_win']:.1%} | {s['fights']} | "
                  f"{s['gained']:.2f} | {s['spent']:.2f} | {s['paid']:.2f} | "
                  f"{s['star_skips']:.2f} | {s['cues']:.2f} | "
                  f"{s['walk_ons']:.2f} | {s['bows']:.2f} | "
                  f"{s['max_cards']} | {s['turns_over_12']}\n")
    out.write("\nper fight means; star skips, cues and walk-ons are per fight;"
              " max cards is the most cards played in any one turn\n")
    for name, s in rows.items():
        label = PROBES[name][0] if name in PROBES else REFERENCES[name]
        out.write(f"\n{name}: {label}\n")
        if s["cues_on"]:
            out.write(f"  cues on: {_fmt_counter(s['cues_on'])}\n")
        if s["star_acts_by"] or s["star_skips_by"]:
            out.write(f"  star acts paid: {_fmt_counter(s['star_acts_by'])};"
                      f" skipped: {_fmt_counter(s['star_skips_by']) or '0'}\n")
        if s["clorinde_procs"]:
            out.write(f"  Clorinde line procs/fight: "
                      f"{s['clorinde_procs']:.2f}\n")
        if s["escoffier_free_summons"]:
            out.write(f"  Escoffier free summons/fight: "
                      f"{s['escoffier_free_summons']:.2f}\n")
        out.write(f"  mean turns/fight {s['turns']:.2f}; fight win "
                  f"{s['fight_win']:.1%}; mean per-fight max cards "
                  f"{s['mean_max_cards']:.2f}; card-cap hits "
                  f"{s['card_cap_hits']}\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probe", action="append",
                    help="probe id (repeatable); default every probe")
    ap.add_argument("--runs", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1,
                    help="worker processes; 0 = one per CPU")
    ap.add_argument("--json", default=None, help="write the summaries here")
    ap.add_argument("--reference", action="store_true",
                    help="also walk the yardstick starters (REFERENCES)")
    args = ap.parse_args(argv)
    probes = args.probe or list(PROBES)
    if args.reference:
        probes += list(REFERENCES)
    rows = {}
    for name in probes:
        rows[name] = summarize(run_probe(name, args.runs, args.seed,
                                         args.jobs))
    sys.stdout.write(f"Furina re-founding sim slice, act one; runs {args.runs}"
                     f" per probe; seed {args.seed}\n\n")
    print_table(rows)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
