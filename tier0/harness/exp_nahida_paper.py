"""The Nahida paper sim's experiment driver (exploratory, 2026-09-29).

Answers the seven questions of the main session's `spec-nahida.md` on the
tier-0 battery (six frozen encounters) plus two ad-hoc packs defined here
(never added to the frozen battery), against the other kits on the same
fights and seeds. Every cell turns the element port's two switches ON
(`C.SWIRL_PAYS`, `C.CRYSTALLIZE_KEEPS_AURA`, as the spec asks) and restores
them after; the Nahida cells throw `nahida_seeds.enable()` and the kit cells
throw each kit's own arm, one at a time.

    PYTHONPATH=. python -m tier0.harness.exp_nahida_paper --fights 400 --out nahida.json

NOTHING HERE IS A BALANCE NUMBER. The card numbers are the paper's
placeholders, the pilot is an instrument (`tier0/pilot/nahida.py`), and the
report says what the sim cannot tell.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import json
import math
import statistics
import sys
import time
from collections import Counter
from dataclasses import dataclass, field

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import furina_stage, nahida_seeds as ns
from tier0.engine.combat import run_fight
from tier0.engine.state import Enemy
from tier0.pilot.nahida import make_nahida_pilot
from tier0.pilot.policy import make_pilot

SEED = 42

# --- the fights ---------------------------------------------------------------

#: Two packs the frozen battery lacks: enemies whose jobs differ, so "spread",
#: "stack on the biggest" and "stack on the attacker" are different choices.
ADHOC = {
    "mixed_trio": [
        {"name": "attacker", "hp": 40,
         "intents": [{"kind": "attack", "amount": 12},
                     {"kind": "attack", "amount": 8}]},
        {"name": "buffer", "hp": 30,
         "intents": [{"kind": "buff", "power": "strength", "amount": 2},
                     {"kind": "block", "amount": 8}]},
        {"name": "brute", "hp": 70,
         "intents": [{"kind": "block", "amount": 10},
                     {"kind": "attack", "amount": 7}]},
    ],
    "boss_adds": [
        {"name": "boss", "hp": 160, "is_boss": True,
         "intents": [{"kind": "attack", "amount": 12},
                     {"kind": "attack", "amount": 4, "times": 3},
                     {"kind": "buff", "power": "strength", "amount": 2}]},
        {"name": "add", "hp": 22, "count": 2,
         "intents": [{"kind": "attack", "amount": 5}]},
    ],
}

SINGLE = ("burst_check", "punisher", "tank_boss")
PACKS = ("swarm", "attrition", "gauntlet", "mixed_trio", "boss_adds")
FIGHTS = SINGLE + PACKS


def _stages(enc: str) -> list[str]:
    return [enc] if enc in ADHOC else loader.encounter_stages(enc)


def _enemies(stage: str) -> list[Enemy]:
    if stage not in ADHOC:
        return loader.build_encounter(stage)
    out = []
    for e in ADHOC[stage]:
        for _ in range(e.get("count", 1)):
            out.append(Enemy(hp=e["hp"], max_hp=e["hp"], name=e["name"],
                             intents=copy.deepcopy(e["intents"]),
                             is_boss=e.get("is_boss", False)))
    return out


# --- the decks ----------------------------------------------------------------

STARTER = list(ns.STARTER_IDS)
SEEDBED = STARTER + ["nh_karmic_bond", "nh_scattered_seeds", "nh_deep_roots",
                     "nh_sprout", "nh_perception", "nh_seed_of_wisdom",
                     "nh_withering_bloom", "nh_illusory_heart", "nh_harvest",
                     "nh_grasp_of_wisdom"]
COMPANIONS = {"hydro": "dahlia_sacramental_shower",     # 1, Deal 6 Hydro
              "pyro": "chevreuse_interdiction_fire",     # 1, Deal 7 Pyro
              "electro": "fischl_nightrider"}            # 1, Deal 5 Electro
FORESIGHT = SEEDBED + ["nh_foresight"]
STORM = SEEDBED + ["nh_sages_mandate", "nh_shrine_of_maya"] \
    + [COMPANIONS["hydro"]] * 3


# --- the worlds ---------------------------------------------------------------

@contextlib.contextmanager
def element_port():
    held = (C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA)
    C.SWIRL_PAYS = C.CRYSTALLIZE_KEEPS_AURA = True
    try:
        yield
    finally:
        C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = held


@contextlib.contextmanager
def nahida_world():
    with element_port():
        ns.enable()
        try:
            yield
        finally:
            ns.disable()


@contextlib.contextmanager
def kit_world(kit: str):
    """`klee`/`kokomi`/`furina` with their prototype arm on (the release
    build's kits); `*_shipped` and the references with every arm off."""
    held = (C.KLEE_OVERHAUL, C.KOKOMI_OVERHAUL, furina_stage.FURINA_STAGE)
    with element_port():
        C.KLEE_OVERHAUL = kit == "klee"
        C.KOKOMI_OVERHAUL = kit == "kokomi"
        furina_stage.FURINA_STAGE = kit == "furina"
        loader.reset_arm_caches()
        try:
            yield
        finally:
            (C.KLEE_OVERHAUL, C.KOKOMI_OVERHAUL,
             furina_stage.FURINA_STAGE) = held
            loader.reset_arm_caches()


# --- one fight's record ---------------------------------------------------------

DIRECT = ("attack", "card")
REACTIVE = ("dendro_core", "dendro_burning", "reaction_splash", "shatter")


@dataclass
class Rec:
    won: bool
    turns: int
    hp_lost: int
    by_source: Counter = field(default_factory=Counter)
    turn_dmg: list = field(default_factory=list)
    turn_purify: list = field(default_factory=list)     # (card, reaction)
    turn_kinds: list = field(default_factory=list)      # "SAP..." per turn
    reactions: Counter = field(default_factory=Counter)
    prevented: int = 0
    recursive_triggers: int = 0          # queued by a Purify CARD's hit
    chained_triggers: int = 0            # queued by an automatic one's hit
    trigger_by: Counter = field(default_factory=Counter)
    board: list = field(default_factory=list)          # (seeds, capped)
    probes: list = field(default_factory=list)         # (distinct, living)

    @property
    def damage(self) -> int:
        return sum(self.by_source.values())


def _bucket(src: str) -> str:
    if src in DIRECT:
        return "direct"
    if src == ns.SOURCE_PURIFY_CARD:
        return "purify_card"
    if src == ns.SOURCE_PURIFY_REACTION:
        return "purify_reaction"
    if src in REACTIVE:
        return "reaction"
    return "other"


def extract(states, hp_start: int, kinds_of) -> Rec:
    """One record per ATTEMPT (a gauntlet is two combats, HP carried)."""
    last = states[-1]
    won = bool(last.player.alive) and not last.living_enemies
    rec = Rec(won=won, turns=sum(s.turn for s in states),
              hp_lost=hp_start - max(0, last.player.hp))
    offset = 0
    for st in states:
        n = st.turn
        tdmg = [0] * n
        tpur = [[0, 0] for _ in range(n)]
        tkind = [""] * n
        for ev in st.log:
            t = ev.get("turn", 0)
            if not 1 <= t <= n:
                continue
            k = ev["event"]
            if k == "damage":
                amt = ev.get("amount", 0)
                rec.by_source[_bucket(ev.get("source", ""))] += amt
                tdmg[t - 1] += amt
            elif k == "purification":
                tpur[t - 1][0 if ev["source"] == "card" else 1] += 1
            elif k == "play":
                c = _card_for(ev["card"])
                tkind[t - 1] += kinds_of(c) if c is not None else "?"
            elif k == "reaction":
                rec.reactions[ev["reaction"]] += 1
            elif k == "foresight_prevented":
                rec.prevented += ev["amount"]
            elif k == "seed_board":
                rec.board.append((ev["total"], ev["capped"]))
            elif k == "placement_probe":
                rec.probes.append((ev["distinct"], ev["living"]))
            elif k == "purify_trigger":
                rec.trigger_by[ev["reaction"]] += 1
                if ev.get("from_purification") == "card":
                    rec.recursive_triggers += 1
                elif ev.get("from_purification") == "reaction":
                    rec.chained_triggers += 1
        rec.turn_dmg += tdmg
        rec.turn_purify += [tuple(x) for x in tpur]
        rec.turn_kinds += tkind
        offset += n
    return rec


_CARD_CACHE: dict = {}


def _card_for(card_id: str):
    """A read-only card for a played id (kinds depend on the id alone)."""
    if card_id not in _CARD_CACHE:
        try:
            _CARD_CACHE[card_id] = (ns.card(card_id)
                                    if card_id in ns.CARD_SPECS
                                    else loader.peek_card(card_id))
        except Exception:                     # a token no index answers
            _CARD_CACHE[card_id] = None
    return _CARD_CACHE[card_id]


def _kinds_generic(c) -> str:
    if c.is_companion:
        return "C"
    return {"attack": "A", "power": "W"}.get(c.type, "B")


def run_nahida(deck, enc, policy="spread", n=400, seed=SEED,
               relic=True) -> list[Rec]:
    out = []
    for i in range(n):
        states, carry, hp0 = [], None, None
        for stage in _stages(enc):
            p = ns.build_player(deck, relic=relic)
            if carry is not None:
                p.hp = carry
            if hp0 is None:
                hp0 = p.hp
            st = run_fight(p, _enemies(stage), make_nahida_pilot(policy),
                           seed=seed + i)
            states.append(st)
            carry = st.player.hp
            if not st.player.alive:
                break
        out.append(extract(states, hp0, ns.kind))
    return out


def run_kit(character, deck, pilot_id, enc, n=400, seed=SEED) -> list[Rec]:
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    out = []
    for i in range(n):
        states, carry, hp0 = [], None, None
        for stage in _stages(enc):
            p = loader.build_player(character, deck)
            if carry is not None:
                p.hp = carry
            if hp0 is None:
                hp0 = p.hp
            st = run_fight(p, _enemies(stage), pilot, seed=seed + i)
            states.append(st)
            carry = st.player.hp
            if not st.player.alive:
                break
        out.append(extract(states, hp0, _kinds_generic))
    return out


# --- summaries --------------------------------------------------------------------

def _q(xs, p):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def summarize(recs: list[Rec]) -> dict:
    n = len(recs)
    wins = [r for r in recs if r.won]
    dpt = [r.damage / max(1, r.turns) for r in recs]
    ttk = [r.turns for r in wins]
    maxturn = [max(r.turn_dmg) if r.turn_dmg else 0 for r in recs]
    tot = Counter()
    for r in recs:
        tot.update(r.by_source)
    alld = sum(tot.values()) or 1
    burst = [max(r.turn_dmg) / r.damage for r in recs if r.damage]
    front = [sum(r.turn_dmg[:3]) / r.damage for r in recs if r.damage]
    cv = []
    for r in recs:
        if len(r.turn_dmg) >= 2 and r.damage:
            m = statistics.mean(r.turn_dmg)
            cv.append(statistics.pstdev(r.turn_dmg) / m if m else 0)
    return {
        "n": n,
        "win": len(wins) / n,
        "win_se": math.sqrt(max(1e-9, len(wins) / n * (1 - len(wins) / n) / n)),
        "dpt_mean": statistics.mean(dpt), "dpt_sd": statistics.pstdev(dpt),
        "ttk_med": _q(ttk, .5), "ttk_p10": _q(ttk, .1), "ttk_p90": _q(ttk, .9),
        "hp_lost_mean": statistics.mean(r.hp_lost for r in recs),
        "hp_lost_sd": statistics.pstdev([r.hp_lost for r in recs]),
        "maxturn_mean": statistics.mean(maxturn),
        "maxturn_max": max(maxturn),
        "share": {k: tot[k] / alld for k in
                  ("direct", "purify_card", "purify_reaction", "reaction",
                   "other")},
        "burst_share": statistics.mean(burst) if burst else 0,
        "front3_share": statistics.mean(front) if front else 0,
        "turn_cv": statistics.mean(cv) if cv else 0,
        "prevented_mean": statistics.mean(r.prevented for r in recs),
        "prevented_sd": statistics.pstdev([r.prevented for r in recs]),
    }


def curve(recs: list[Rec], turns: int = 10) -> list[float]:
    """Mean damage on turn t over fights still running at t."""
    out = []
    for t in range(turns):
        xs = [r.turn_dmg[t] for r in recs if len(r.turn_dmg) > t]
        out.append(statistics.mean(xs) if xs else float("nan"))
    return out


def purify_dist(recs: list[Rec]) -> dict:
    per_turn = Counter()
    per_turn_react = Counter()
    for r in recs:
        for c, x in r.turn_purify:
            per_turn[c + x] += 1
            per_turn_react[x] += 1
    return {"total": dict(sorted(per_turn.items())),
            "reaction": dict(sorted(per_turn_react.items())),
            "triggers_from_purify_card": sum(r.recursive_triggers
                                             for r in recs),
            "triggers_from_auto_purification": sum(r.chained_triggers
                                                   for r in recs),
            "turns": sum(len(r.turn_purify) for r in recs),
            "triggers_by": dict(sum((r.trigger_by for r in recs), Counter()))}


def placement(recs: list[Rec]) -> dict:
    """Is placement a decision? How often the three policies would put the
    Seed a card places on different enemies (multi-enemy boards only), and
    how fast the board saturates (every living enemy at the cap)."""
    multi = [d for r in recs for d, n in r.probes if n > 1]
    first_sat = []
    for r in recs:
        t = next((i + 1 for i, (_, cap) in enumerate(r.board) if cap), None)
        if t is not None:
            first_sat.append(t)
    sat_turns = sum(1 for r in recs for _, cap in r.board if cap)
    all_turns = sum(len(r.board) for r in recs)
    seeds_t = {t: statistics.mean([r.board[t - 1][0] for r in recs
                                   if len(r.board) >= t] or [0])
               for t in (2, 3, 4, 6)}
    return {"probes_multi": len(multi),
            "policies_disagree": (sum(1 for d in multi if d > 1)
                                  / max(1, len(multi))),
            "fights_saturating": len(first_sat) / max(1, len(recs)),
            "first_saturation_med": _q(first_sat, .5),
            "turns_saturated": sat_turns / max(1, all_turns),
            "seeds_on_board_at_turn": seeds_t}


def autopilot(recs: list[Rec]) -> dict:
    pats = Counter()
    seed_then_purify = only_sp = with_p = 0
    turns = 0
    for r in recs:
        for k in r.turn_kinds:
            if not k:
                continue
            turns += 1
            pats[k] += 1
            if "P" in k:
                with_p += 1
            i = k.find("S")
            if i >= 0 and "P" in k[i:]:
                seed_then_purify += 1
                if set(k) <= {"S", "P"}:
                    only_sp += 1
    h = -sum((v / turns) * math.log2(v / turns) for v in pats.values()) \
        if turns else 0
    return {"turns": turns, "distinct": len(pats), "entropy_bits": h,
            "seed_then_purify": seed_then_purify / max(1, turns),
            "only_seed_purify": only_sp / max(1, turns),
            "with_purify": with_p / max(1, turns),
            "top": pats.most_common(8)}


# --- the questions ---------------------------------------------------------------

def run_all(n: int, seed: int) -> dict:
    out: dict = {"n": n, "seed": seed, "fights": list(FIGHTS)}
    t0 = time.perf_counter()

    kits = {
        "klee_proto": ("klee", "klee", "starter", "generic"),
        "kokomi_proto": ("kokomi", "kokomi", "starter", "generic"),
        "furina_proto": ("furina", "furina", "starter", "generic"),
        "ironclad": ("ref_ironclad", "none", "starter", "generic"),
        "silent": ("ref_silent", "none", "starter", "generic"),
        "klee_demolition_pkg": ("klee", "none", "demolition_weighted",
                                "demolition"),
        "kokomi_priest_pkg": ("kokomi", "none", "priest_weighted", "priest"),
        "furina_salon_pkg": ("furina", "none", "salon_weighted", "salon"),
        "ironclad_pkg": ("ref_ironclad", "none", "archetype_package",
                         "generic"),
    }
    raw_kits = {}
    for name, (char, arm, deck, pilot) in kits.items():
        with kit_world(arm):
            raw_kits[name] = {enc: run_kit(char, deck, pilot, enc, n, seed)
                              for enc in FIGHTS}
        print(f"  {name} done ({time.perf_counter() - t0:.0f}s)",
              file=sys.stderr)

    raw = {}
    with nahida_world():
        for deck_name, deck in (("starter", STARTER), ("seedbed", SEEDBED)):
            for pol in ("spread", "deep", "attacker"):
                raw[(deck_name, pol)] = {enc: run_nahida(deck, enc, pol, n, seed)
                                         for enc in FIGHTS}
            print(f"  nahida {deck_name} done "
                  f"({time.perf_counter() - t0:.0f}s)", file=sys.stderr)
        raw[("seedbed_norelic", "spread")] = {
            enc: run_nahida(SEEDBED, enc, "spread", n, seed, relic=False)
            for enc in FIGHTS}
        for el, cid in COMPANIONS.items():
            for copies in (1, 3):
                raw[(f"tri_{el}_x{copies}", "spread")] = {
                    enc: run_nahida(SEEDBED + [cid] * copies, enc, "spread",
                                    n, seed) for enc in FIGHTS}
        for pol in ("spread", "attacker"):
            raw[("storm", pol)] = {enc: run_nahida(STORM, enc, pol, n, seed)
                                   for enc in FIGHTS}
            raw[("foresight", pol)] = {
                enc: run_nahida(FORESIGHT, enc, pol, n, seed)
                for enc in FIGHTS}
        # Mandate alone, and Storm without it, to isolate the recursion.
        raw[("storm_nomandate", "spread")] = {
            enc: run_nahida([c for c in STORM if c != "nh_sages_mandate"],
                            enc, "spread", n, seed) for enc in FIGHTS}
        print(f"  nahida variants done ({time.perf_counter() - t0:.0f}s)",
              file=sys.stderr)

    out["kits"] = {k: {e: summarize(v) for e, v in d.items()}
                   for k, d in raw_kits.items()}
    out["kit_curves"] = {k: curve(sum(d.values(), []))
                         for k, d in raw_kits.items()}
    out["nahida"] = {f"{d}|{p}": {e: summarize(v) for e, v in cells.items()}
                     for (d, p), cells in raw.items()}
    out["nahida_curves"] = {f"{d}|{p}": curve(sum(cells.values(), []))
                            for (d, p), cells in raw.items()}
    out["storm"] = {f"{d}|{p}": purify_dist(sum(cells.values(), []))
                    for (d, p), cells in raw.items()
                    if d.startswith(("storm", "tri_", "seedbed"))}
    out["storm_by_fight"] = {
        f"{d}|{p}|{e}": purify_dist(v)
        for (d, p), cells in raw.items() if d == "storm"
        for e, v in cells.items()}
    out["autopilot"] = {f"{d}|{p}": autopilot(sum(cells.values(), []))
                        for (d, p), cells in raw.items()}
    out["placement"] = {f"{d}|{p}|{e}": placement(v)
                        for (d, p), cells in raw.items()
                        if d in ("starter", "seedbed", "foresight")
                        for e, v in cells.items()}
    out["autopilot_kits"] = {k: autopilot(sum(d.values(), []))
                             for k, d in raw_kits.items()}
    out["seconds"] = time.perf_counter() - t0
    return out


# --- the worked Foresight turn (paper sec.5) --------------------------------------

def foresight_turn() -> dict:
    """Foresight in play, two unseeded enemies (a 14-damage attacker and a
    20-HP buffer), 2 Seeds to place and a Purify in hand. Both lines, played
    through the real engine: Seed, Seed, Purify, then the enemy turn."""
    from tier0.engine import combat
    from tier0.engine.state import CombatState
    import random
    results = {}
    with nahida_world():
        for line in ("both_on_attacker", "one_each"):
            p = ns.build_player([], relic=False)
            p.hp = p.max_hp = 62
            attacker = Enemy(hp=40, max_hp=40, name="attacker",
                             intents=[{"kind": "attack", "amount": 14}])
            buffer = Enemy(hp=20, max_hp=20, name="buffer",
                           intents=[{"kind": "buff", "power": "strength",
                                     "amount": 2}])
            st = CombatState(player=p, enemies=[attacker, buffer],
                             rng=random.Random(1))
            st.turn = 1
            st.in_player_turn = True
            f = ns.field_of(st)
            f.powers["foresight"] = 1
            seed_a = ns.card("nh_seed_of_wisdom")
            seed_b = ns.card("nh_seed_of_wisdom")
            purify = ns.card("nh_tri_karma")
            p.hand = [seed_a, seed_b, purify]
            p.energy = 3
            ns.aim_card(st, seed_a, attacker)
            combat.play_card(st, seed_a)
            ns.aim_card(st, seed_b, attacker if line == "both_on_attacker"
                        else buffer)
            combat.play_card(st, seed_b)
            combat.play_card(st, purify)
            ns.flush(st)
            hp_a, hp_b = attacker.hp, buffer.hp
            st.in_player_turn = False
            before = p.hp + p.block
            combat._enemy_turn(st, attacker)
            results[line] = {
                "attacker_seeds": ns.seeds(st, attacker),
                "buffer_seeds": ns.seeds(st, buffer),
                "purify_to_attacker": 40 - hp_a,
                "purify_to_buffer": 20 - hp_b,
                "attacker_hit_landed": before - (p.hp + p.block),
            }
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=400)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    res = run_all(a.fights, a.seed)
    res["foresight_turn"] = foresight_turn()
    text = json.dumps(res, indent=1, default=str)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
