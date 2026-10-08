"""The research slice's probes (proposal sec.10), act one plus a boss gauntlet.

    .venv/Scripts/python.exe -m tier0.harness.furina_tide_probe --runs 1000 --jobs 0
    .venv/Scripts/python.exe -m tier0.harness.furina_tide_probe --runs 1000 --jobs 0 --curtain

`--curtain` is sec.16's read: the curtain call (the default rule) against
`no_curtain_call` and the `legacy` baseline, with `ref:ironclad`.

`--picks` is the pool-40 paper's read (sec.5 item 3): over the same draft
seeds, how often each card was offered and how often the draft took it when
it was, so a dominant or a dead card shows.

WHAT A RUN IS. The retired `furina_v2_probe` spine: a FIXED deck (no
draft, no relic but Salon Solitaire, no potions, no upgrades) walks act one's
`C.RUN_NODE_TEMPLATE` against the act's own pools; HP carries; a rest heals
30%; the run is an act-one WIN when the boss falls. The `draft` probe drafts
ten cards from 3-card offers (60/30/10) by the pilot's own value model.

GAUNTLET (`--gauntlet`). One deck fights the act-2 boss and then the act-3
boss, each at full HP, from the tier05 boss pools: a read of late-game
scaling only (the decks are hand-built, so compare probes with each other,
never with a shipped number).

A job is `probe/pilot` (pilot: judged | always | never). The reference runs
the same seeds: `ref:ironclad` is the reference Ironclad starter. (`ref:v2`,
the Furina v2 sim slice's starter, left with that slice on 2026-10-08; tag
`furina-v2-sim-slice-2026-10-08` keeps it.)

This is an instrument for the proposal's kill questions, not a balance
number: no world stamp, no band, nothing here is quotable as a sheet value.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor

from tier0 import constants as C
from tier0.engine import furina_tide as T
from tier0.engine.combat import run_fight
from tier0.pilot import furina_tide_pilot

STARTER = list(T.STARTER_IDS)

PROBES: dict[str, tuple[str, list[str]]] = {
    "base": ("starter only", []),
    "base_6": ("starter with Rising Applause as a fixed Spend 6: deal 12",
               []),
    "base_all2": ("starter with the spend-all Rising Applause at 2 per "
                  "point", []),
    "ousia": ("Ousia: Crabaletta, Chevalmarin x2, Solicitation, Usher, "
              "Tidal Flourish, Bravura, Salon's Encore",
              ["ftd_crabaletta", "ftd_chevalmarin", "ftd_chevalmarin",
               "ftd_solicitation", "ftd_usher", "ftd_tidal_flourish",
               "ftd_bravura", "ftd_salon_encore"]),
    "pneuma": ("Pneuma: Hymn x2, Surging Waters x2, Pneuma Refrain, "
               "Endless Waltz, Curtain Rise, Usher",
               ["ftd_hymn", "ftd_hymn", "ftd_surging_waters",
                "ftd_surging_waters", "ftd_pneuma_refrain",
                "ftd_endless_waltz", "ftd_curtain_rise", "ftd_usher"]),
    "guests": ("Guests: Charlotte, Wriothesley, Sigewinne, Clorinde, "
               "Chevalmarin, Surging Waters, Usher, Crabaletta",
               ["ftd_charlotte", "ftd_wriothesley", "ftd_sigewinne",
                "ftd_clorinde", "ftd_chevalmarin", "ftd_surging_waters",
                "ftd_usher", "ftd_crabaletta"]),
    "tragedy": ("Ousia finale with The Crowd Gasps in place of Salon's "
                "Encore",
                ["ftd_crabaletta", "ftd_chevalmarin", "ftd_chevalmarin",
                 "ftd_revelry", "ftd_rejoice", "ftd_tidal_flourish",
                 "ftd_bravura", "ftd_crowd_gasps"]),
    "loop": ("the HP loop: Revelry, Critics' Darling, Endless Waltz, Salon's "
             "Encore, Pneuma Refrain, Hymn, Crabaletta, Chevalmarin",
             ["ftd_revelry", "ftd_critics_darling", "ftd_endless_waltz",
              "ftd_salon_encore", "ftd_pneuma_refrain", "ftd_hymn",
              "ftd_crabaletta", "ftd_chevalmarin"]),
    "balanced": ("a balanced draft: Crabaletta, Chevalmarin, Usher, Hymn, "
                 "Surging Waters, Standing Ovation, Bravura, Tidal Flourish",
                 ["ftd_crabaletta", "ftd_chevalmarin", "ftd_usher",
                  "ftd_hymn", "ftd_surging_waters", "ftd_standing_ovation",
                  "ftd_bravura", "ftd_tidal_flourish"]),
    "finale": ("Ousia finale: the Ousia deck with Universal Revelry and Let "
               "the People Rejoice in place of Solicitation and Usher",
               ["ftd_crabaletta", "ftd_chevalmarin", "ftd_chevalmarin",
                "ftd_revelry", "ftd_rejoice", "ftd_tidal_flourish",
                "ftd_bravura", "ftd_salon_encore"]),
}

DRAFT = "draft"
DRAFT_PICKS = 10
DRAFT_OFFER = 3
RARITY_WEIGHTS = (("common", 60), ("uncommon", 30), ("rare", 10))
DRAFT_POOL: dict[str, list[str]] = {
    r: sorted(cid for cid, sp in T.CARDS.items()
              if sp.rarity == r and sp.in_slice)
    for r, _w in RARITY_WEIGHTS}

FIGHT_KINDS = ("N", "E", "B")


def deck(probe: str) -> list[str]:
    if probe in ("base_6", "base_all2"):
        alt = ("ftd_rising_applause_6" if probe == "base_6"
               else "ftd_rising_applause_all2")
        return [c if c != "ftd_rising_applause" else alt for c in STARTER]
    return STARTER + list(PROBES[probe][1])


def _draft_ref_state(picks: list[str]):
    from tier0.engine.state import CombatState, Enemy
    p = T.build_player(STARTER + picks)
    p.energy = 3
    p.ftd.fanfare = 8          # a mid-fight bank, so Spend modes are priced
    p.ftd.drained = 4
    p.hp = T.HP - 4
    enemy = Enemy(hp=40, max_hp=40, name="draft_ref",
                  intents=[{"kind": "attack", "amount": 10}])
    st = CombatState(player=p, enemies=[enemy], rng=random.Random(0))
    st.turn = 1
    return st


def draft_deck(seed: int, log: list | None = None) -> list[str]:
    """Ten picks from 3-card offers. `log`, when given, receives one
    `(offer, pick)` per pick."""
    from tier0.engine.combat import card_cost
    rng = random.Random(f"furina_tide-draft-{seed}")
    rarities = [r for r, _w in RARITY_WEIGHTS]
    weights = [w for _r, w in RARITY_WEIGHTS]
    picks: list[str] = []
    dec = furina_tide_pilot.DECIDERS["judged"]
    for _ in range(DRAFT_PICKS):
        offer: list[str] = []
        while len(offer) < DRAFT_OFFER:
            r = rng.choices(rarities, weights)[0]
            cid = rng.choice(DRAFT_POOL[r])
            if cid not in offer:
                offer.append(cid)
        st = _draft_ref_state(picks)
        hand = [T.make_card(c) for c in offer]
        st.player.hand = list(hand)
        best, best_key = offer[0], None
        for i, (cid, card) in enumerate(zip(offer, hand)):
            v = furina_tide_pilot.value(st, card, hand, dec)
            key = (v / max(0.5, card_cost(st, card)), v, -i)
            if best_key is None or key > best_key:
                best, best_key = cid, key
        picks.append(best)
        if log is not None:
            log.append((list(offer), best))
    return STARTER + picks


def pick_rates(runs: int, seed: int = 1) -> dict[str, dict]:
    """Per card: offered (in how many offers), picked, and the pick rate
    when offered, over `runs` draft seeds."""
    offered: collections.Counter = collections.Counter()
    picked: collections.Counter = collections.Counter()
    for s in range(seed, seed + runs):
        log: list = []
        draft_deck(s, log)
        for offer, pick in log:
            offered.update(set(offer))
            picked[pick] += 1
    return {cid: {"rarity": T.CARDS[cid].rarity, "offered": offered[cid],
                  "picked": picked[cid],
                  "rate": picked[cid] / offered[cid] if offered[cid] else 0.0}
            for cid in sorted(offered, key=lambda c: (T.CARDS[c].rarity, c))}


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
    T.close_ledger(state)
    L = state.player.ftd.ledger
    return {
        "kind": kind,
        "won": state.player.alive and not state.living_enemies,
        "turns": state.turn,
        "hp": state.player.hp,      # after the curtain call, when it is on
        "gained": L["gained"], "gained_by": dict(L["gained_by"]),
        "spent": L["spent"], "spends": L["spends"],
        "spend_offers": L["spend_offers"],
        "drained": L["drained"], "drains": L["drains"],
        "card_drains": L["card_drains"],
        "fixed_drains": L["fixed_drains"],
        "curtain_repaid": L["curtain_repaid"],
        "drain_offers": L["drain_offers"],
        "drain_blocked": L["drain_blocked_by_line"],
        "repaid": L["repaid"], "repay_wasted": L["repay_wasted"],
        "singer_skipped": L["singer_skipped"],
        "fanfare_end": L["fanfare_end"], "unrepaid_end": L["unrepaid_end"],
        "start_low": L["started_at_or_below_half"],
        "damage_by_turn": dict(L["damage_by_turn"]),
        "max_cards": max(_plays_per_turn(state) or [0]),
    }


def run_one(probe: str, seed: int, pilot: str = "judged",
            variant: str = T.DEFAULT_VARIANT) -> dict:
    from tier05 import acts
    cards = draft_deck(seed) if probe == DRAFT else deck(probe)
    play = furina_tide_pilot.PILOTS[pilot]
    rng = random.Random(seed)
    draw = acts.ActDraw(rng, 0)
    hp = max_hp = T.HP
    fights: list[dict] = []
    won = False
    for kind in C.RUN_NODE_TEMPLATE:
        if kind == "R":
            hp = min(max_hp, hp + int(C.REST_HEAL_FRACTION * max_hp))
            continue
        if kind not in FIGHT_KINDS:
            continue
        enemies = acts.spawn(draw.encounter_for(kind, rng), rng)
        player = T.build_player(cards, hp=hp, max_hp=max_hp,
                                variant=variant)
        state = run_fight(player, enemies, play,
                          seed=rng.randrange(2 ** 31))
        fights.append(fight_record(state, kind))
        hp = state.player.hp
        if not fights[-1]["won"]:
            break
        if kind == "B":
            won = True
    out = {"seed": seed, "won": won, "fights": fights, "hp_end": hp}
    if probe == DRAFT:
        out["deck"] = cards
    return out


def run_gauntlet(probe: str, seed: int, pilot: str = "judged",
                 variant: str = T.DEFAULT_VARIANT) -> dict:
    """Act-2 boss then act-3 boss, each at full HP."""
    from tier05 import acts
    cards = deck(probe)
    play = furina_tide_pilot.PILOTS[pilot]
    rng = random.Random(f"gauntlet-{seed}")
    out = {"seed": seed, "fights": []}
    for act in (1, 2):
        draw = acts.ActDraw(rng, act)
        enemies = acts.spawn(draw.encounter_for("B", rng), rng)
        player = T.build_player(cards, variant=variant)
        state = run_fight(player, enemies, play,
                          seed=rng.randrange(2 ** 31))
        rec = fight_record(state, f"B{act + 1}")
        out["fights"].append(rec)
    return out


def run_reference(which: str, seed: int) -> dict:
    """The reference Ironclad starter over act one, on the same seeds, under
    the generic pilot (ported from the retired `furina_v2_probe`)."""
    if which != "ironclad":
        raise ValueError(f"unknown reference {which!r}: only ref:ironclad")
    from tier0.content import loader
    from tier0.pilot.policy import make_pilot
    from tier05 import acts
    character = "ref_ironclad"
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
        rec = {"kind": kind, "won": state.player.alive
               and not state.living_enemies,
               "turns": state.turn, "hp": state.player.hp}
        fights.append(rec)
        hp = state.player.hp
        if not rec["won"]:
            break
        if kind == "B":
            won = True
    return {"seed": seed, "won": won, "fights": fights, "hp_end": hp}


def _one(job: str, seed: int) -> dict:
    if job.startswith("ref:"):
        return run_reference(job[4:], seed)
    gaunt = job.startswith("gauntlet:")
    head, _, pilot = (job[9:] if gaunt else job).partition("/")
    probe, _, variant = head.partition("@")
    fn = run_gauntlet if gaunt else run_one
    return fn(probe, seed, pilot or "judged", variant or T.DEFAULT_VARIANT)


def _chunk(args) -> list[dict]:
    job, lo, hi = args
    return [_one(job, s) for s in range(lo, hi)]


def run_job(job: str, runs: int, seed: int, jobs: int) -> list[dict]:
    if jobs <= 1:
        return [_one(job, s) for s in range(seed, seed + runs)]
    step = max(1, runs // (jobs * 4))
    parts = [(job, lo, min(seed + runs, lo + step))
             for lo in range(seed, seed + runs, step)]
    out: list[dict] = []
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for part in ex.map(_chunk, parts):
            out.extend(part)
    return out


def summarize(results: list[dict]) -> dict:
    fights = [f for r in results for f in r["fights"]]
    n = len(results)
    s: dict = {"runs": n}
    if "won" in results[0]:
        s["act1_win"] = sum(r["won"] for r in results) / n
    bosses = [f for f in fights if f["kind"] == "B"]
    s["boss_reached"] = len(bosses) / n if n else 0
    s["fights_won"] = sum(sum(1 for f in r["fights"] if f["won"])
                          for r in results) / n
    s["elite1_won"] = sum(1 for r in results
                          if sum(1 for f in r["fights"]
                                 if f["kind"] == "E" and f["won"]) >= 1) / n
    if bosses:
        s["boss_turns"] = sum(f["turns"] for f in bosses) / len(bosses)
    if "hp_end" in results[0]:
        # HP at the end of act one: the mean over the runs that cleared it
        # (after the boss and, under the curtain call, its return), and
        # over every run with a death counted as 0.
        winners = [r["hp_end"] for r in results if r.get("won")]
        s["hp_end_act1_winners"] = (sum(winners) / len(winners)
                                    if winners else 0.0)
        s["hp_end_all"] = sum(max(0, r["hp_end"]) for r in results) / n
    if fights and "hp" in fights[0]:
        # No starter clears the spine, so the act's HP read for a starter is
        # the mean HP left after a won fight.
        won_f = [f["hp"] for f in fights if f["won"]]
        s["hp_after_won_fight"] = sum(won_f) / len(won_f) if won_f else 0.0
    if not fights or "drain_offers" not in fights[0]:
        return s
    tot = collections.Counter()
    for f in fights:
        for k in ("gained", "spent", "spends", "spend_offers", "drained",
                  "drains", "drain_offers", "drain_blocked", "repaid",
                  "fanfare_end", "unrepaid_end", "turns", "singer_skipped",
                  "card_drains", "fixed_drains", "curtain_repaid"):
            tot[k] += f[k]
        for src, v in f["gained_by"].items():
            tot["g_" + src] += v
    nf = len(fights)
    legal = tot["drain_offers"] - tot["drain_blocked"]
    s.update({
        "fights": nf,
        # card Drains over legal card offers (Neuvillette's act Drains are
        # in `drains` but are never offered, so they stay out of the rate)
        "drain_take_rate": tot["card_drains"] / legal if legal else 0.0,
        "drain_blocked_rate": (tot["drain_blocked"] / tot["drain_offers"]
                               if tot["drain_offers"] else 0.0),
        "gained_per_turn": tot["gained"] / max(1, tot["turns"]),
        "spent_per_turn": tot["spent"] / max(1, tot["turns"]),
        "spent_share": tot["spent"] / max(1, tot["gained"]),
        "fanfare_end_per_fight": tot["fanfare_end"] / nf,
        "drained_per_fight": tot["drained"] / nf,
        "repaid_per_fight": tot["repaid"] / nf,
        "unrepaid_per_fight": tot["unrepaid_end"] / nf,
        "curtain_repaid_per_fight": tot["curtain_repaid"] / nf,
        "fixed_drains_per_fight": tot["fixed_drains"] / nf,
        "singer_skipped_per_fight": tot["singer_skipped"] / nf,
        "gain_split": {k[2:]: round(v / max(1, tot["gained"]), 2)
                       for k, v in tot.items() if k.startswith("g_")},
        "start_low_rate": sum(1 for f in fights if f["start_low"]) / nf,
    })
    low = [f for f in fights if f["start_low"]]
    high = [f for f in fights if not f["start_low"]]
    for label, group in (("low", low), ("high", high)):
        offers = sum(f["drain_offers"] for f in group)
        s[f"won_{label}"] = (sum(f["won"] for f in group) / len(group)
                             if group else 0.0)
        s[f"blocked_{label}"] = (sum(f["drain_blocked"] for f in group)
                                 / offers if offers else 0.0)
    dbt = collections.defaultdict(list)
    for f in bosses:
        for t, d in f.get("damage_by_turn", {}).items():
            dbt[int(t)].append(d)
    s["boss_kit_damage_by_turn"] = {
        t: round(sum(v) / len(bosses), 1) for t, v in sorted(dbt.items())
        if t <= 8}
    return s


def summarize_gauntlet(results: list[dict]) -> dict:
    out = {}
    for idx, label in ((0, "act2_boss"), (1, "act3_boss")):
        fs = [r["fights"][idx] for r in results]
        out[label + "_win"] = sum(f["won"] for f in fs) / len(fs)
        out[label + "_turns"] = sum(f["turns"] for f in fs) / len(fs)
        out[label + "_gained_per_turn"] = (sum(f["gained"] for f in fs)
                                           / max(1, sum(f["turns"]
                                                        for f in fs)))
    return out


DEFAULT_JOBS = (
    "ref:ironclad",
    "base/judged", "base/always", "base/never",
    "ousia/judged", "ousia/always", "ousia/never",
    "pneuma/judged", "pneuma/always", "pneuma/never",
    "guests/judged", "finale/judged",
    "draft/judged", "draft/always", "draft/never",
)
#: The K3 comparison (`--k3`): the baseline rules and each K3 switch
#: (`furina_tide.K3_SWITCHES`), on the same seeds, under the old rule.
K3_VARIANTS = ("entry",) + tuple(T.K3_SWITCHES)
K3_JOBS = tuple(
    job for v in K3_VARIANTS for job in (
        f"base@{v}/judged",
        f"draft@{v}/judged", f"draft@{v}/always", f"draft@{v}/never",
        f"balanced@{v}/judged", f"balanced@{v}/always",
        f"balanced@{v}/never",
        f"gauntlet:finale@{v}/judged"))

#: The sec.16 comparison (`--curtain`): the curtain call against the old
#: end-of-fight rule (both with the always-spend Rising Applause), and the
#: old baseline (`legacy`: no curtain call, Rising Applause skippable), on
#: the same seeds, with the Ironclad reference for scale.
CURTAIN_VARIANTS = ("curtain_call", "no_curtain_call", "legacy")
CURTAIN_JOBS = ("ref:ironclad",) + tuple(
    job for v in CURTAIN_VARIANTS for job in (
        f"base@{v}/judged", f"base@{v}/never",
        f"draft@{v}/judged", f"draft@{v}/always", f"draft@{v}/never",
        f"balanced@{v}/judged", f"balanced@{v}/always",
        f"balanced@{v}/never",
        f"gauntlet:finale@{v}/judged"))

GAUNTLET_JOBS = (
    "gauntlet:ousia/judged", "gauntlet:pneuma/judged",
    "gauntlet:guests/judged", "gauntlet:finale/judged",
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=500)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--job", action="append")
    ap.add_argument("--gauntlet", action="store_true")
    ap.add_argument("--k3", action="store_true",
                    help="run K3_JOBS: the K3 switches against the baseline")
    ap.add_argument("--curtain", action="store_true",
                    help="run CURTAIN_JOBS: sec.16's curtain-call read")
    ap.add_argument("--picks", action="store_true",
                    help="print each card's draft pick rate when offered")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    if args.picks:
        rates = pick_rates(args.runs, args.seed)
        for cid, r in rates.items():
            print(f"{cid:24s} {r['rarity']:9s} offered {r['offered']:6d} "
                  f"picked {r['picked']:6d} rate {r['rate']:.1%}")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(rates, fh, indent=1)
        return 0
    if args.jobs == 0:
        import os
        args.jobs = os.cpu_count() or 1
    jobs = args.job or (CURTAIN_JOBS if args.curtain else
                        K3_JOBS if args.k3 else
                        GAUNTLET_JOBS if args.gauntlet else DEFAULT_JOBS)
    table = {}
    for job in jobs:
        res = run_job(job, args.runs, args.seed, args.jobs)
        table[job] = (summarize_gauntlet(res)
                      if "gauntlet:" in job else summarize(res))
        print(job, json.dumps(table[job]), flush=True)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(table, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
