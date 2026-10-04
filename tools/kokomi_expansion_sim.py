#!/usr/bin/env python3
"""KOKOMI EXPANSION, BATCH ONE -- the paper's sec.5 sim (exploration, not
quotable, R215 B).

    .venv/Scripts/python.exe -m tools.kokomi_expansion_sim --seeds 400 --seed 7 --jobs 14

Answers sec.5 of `review/active/kokomi-expansion-2026-09-29.md` on the BUILT
rows (the tier0 engine with `C.KOKOMI_OVERHAUL` on for THIS PROCESS ONLY;
nothing on disk moves). Modelled on the Varka Oath report
(`tools/varka_oath_report.py` / `tools/varka_oath_r4.py`, PR #768).

RUN -- a stylised act 1 on the tier-0.5 act-1 pools (`tier05/acts.py`):
floors N N N N E R N N E R B, then a card reward (elite odds), a rest and a
stylised act-2 boss drawn from the act-2 boss pool. A card reward of three
after every non-boss fight (rarity C/U/R 60/37/3 after a normal fight, 50/40/10
after an elite or the act-1 boss), rests heal 30% of max HP. The Tamakushi
Casket (her starting relic) and nothing else: no potions, gold, shops,
upgrades or events. Encounters, HP rolls and offers are drawn from
pilot-independent streams, so every pilot meets the same fights and offers
(paired).

GAUNTLET -- because the stock play pilot rarely survives the first act-1
elite (the starter loses Bygone Effigy and the Gardener at full HP in this
engine), every pilot's nine picks are also drafted off the same offer stream
as if every fight were won, and that deck fights every act-1 elite, act-1
boss and act-2 boss once per seed at full HP. It reads deck strength apart
from attrition.

PILOTS (drafters) -- one play pilot, five drafting rules:
  * baseline: the repo's default drafter (`tier05.draft.score_offer`,
    archetype "generic", skip under `C.DRAFT_SKIP_THRESHOLD`) over the whole
    current pool. It prices the seven new Powers and Shoal Call at 0, so the
    harness gives those eight the median default score of the other new cards
    (read once against the starter), so their pick rates mean something.
  * the four focused drafters (paper sec.3 grouping, plus the existing parts
    sec.1 names for each deck): a new card of the deck 10 (cap 2; a Power or
    a Rare cap 1), an existing card of the deck 7 (cap 2), anything else (or
    past its cap) the baseline's own score and skip line -- so every pilot
    fills its deck the same way and differs only in what it reaches for.
    The existing parts:
      - Plan volume: Bubble Ward, Nip, Jellyfish Drift, Current Read, Brine
        Sting, Feint, Sango Isshin, Tideturn, Change of Plans, Second
        Thoughts, Driftglass, Depths' Judgment, What the Tokoyo Took, What
        the Tokoyo Returns, Shell Guard. (Pearl Diver and Moon Signal left
        with the status batch, 2026-10-01.)
      - Big Plan: Opening Gambit, Second Wave, Surging Shoal, Ambush,
        Nereid's Ascension.
      - Tide Control: War Council, Vanguard, Brine Sting, Feint, Ambush,
        Opening Gambit, Undertow, Riptide.
      - Dusk Guard: Coral Bulwark, Shell Guard, Tide Wall, Breakwater, Shell
        of Sanctuary, Read the Field, The Moon a Ship, Bubble Ward.

THE PLAY PILOT is the repo's `priest` pilot (the feed pass's) with a harness
wrapper, an INSTRUMENT SURFACE and not a design claim:
  * Open the Casket when it holds 6, or from turn 6 when it holds any (the
    feed pass's wrapper);
  * her Powers are played first when affordable;
  * Brace for the Tide when an enemy intends to attack (All Streams Flow to
    the Sea and its rule left with the status batch, 2026-10-01);
  * a DUSK Plan is written when an enemy intends to attack (the stock rule
    writes a Plan only when none does, which is backwards for Dusk -- applied
    to every pilot, Breakwater and Shell of Sanctuary included);
  * the new clauses are valued as their nearest stock op (energy, damage,
    Block; the `kokomi` kinds as draws) so the stock scorer can see them.
"""

from __future__ import annotations

import argparse
import os
import random
import statistics as st
import sys
from collections import defaultdict

TEMPLATE = ["N", "N", "N", "N", "E", "R", "N", "N", "E", "R", "B"]
RARITY = {"N": (60, 37, 3), "E": (50, 40, 10), "B": (50, 40, 10)}
PILOTS = ("volume", "big_plan", "tide", "dusk", "baseline")
FOCUSED = ("volume", "big_plan", "tide", "dusk")

NEW = {
    "big_plan": ["weight_of_the_plan", "lull", "undertide_lance",
                 "measured_breath", "grand_design", "the_long_game",
                 "masterstroke"],
    "tide": ["drowning_pressure", "salt_in_the_wound", "undercurrent_snare",
             "tidal_resonance", "at_waters_edge", "ceremonial_garment",
             "suffocating_deep"],
    "dusk": ["coral_crash", "evening_watch", "brace_for_the_tide",
             "watatsumis_grace", "tidal_riposte"],
    "volume": ["shoal_call", "kurage_swarm", "kurage_canopy", "coral_tithe"],
}
OLD = {
    "volume": ["bubble_ward", "nip", "jellyfish_drift", "current_read",
               "brine_sting", "feint", "sango_isshin", "tideturn",
               "change_of_plans", "driftglass", "depths_judgment",
               "what_the_tokoyo_took", "what_the_tokoyo_returns",
               "shell_guard"],
    "big_plan": ["opening_gambit", "second_wave", "surging_shoal", "ambush",
                 "nereids_ascension"],
    "tide": ["war_council", "vanguard", "brine_sting", "feint", "ambush",
             "opening_gambit", "undertow", "riptide"],
    "dusk": ["coral_bulwark", "shell_guard", "tide_wall", "breakwater",
             "shell_of_sanctuary", "read_the_field", "the_moon_a_ship",
             "bubble_ward"],
}
P = "proto_kk_"
NEW_IDS = [P + c for deck in ("big_plan", "tide", "dusk", "volume")
           for c in NEW[deck]]
#: The new rows the default drafter prices at 0 (the seven Powers and Shoal
#: Call): the harness gives them the median of the others (`_nominal`).
NOMINAL_IDS = frozenset(P + c for c in (
    "grand_design", "the_long_game", "at_waters_edge", "ceremonial_garment",
    "watatsumis_grace", "tidal_riposte", "kurage_swarm", "shoal_call"))


# --- the process switch and the harness surfaces ------------------------------

_ENABLED = False


def enable():
    """The arm on, for this process only, plus the three pilot surfaces."""
    global _ENABLED
    if _ENABLED:
        return
    from tier0.content import loader, upgrades
    for fn in (upgrades._upgrade_index,):
        try:
            fn.cache_clear()
        except AttributeError:
            pass
    for name in dir(loader):
        fn = getattr(loader, name)
        if hasattr(fn, "cache_clear"):
            fn.cache_clear()
    from tier0.engine import kokomi_plan
    from tier0.pilot import policy

    orig_aim = kokomi_plan.plan_aimed_at_pet

    def aim(state, card):
        if (getattr(card, "plan_dusk", False) and card.plan
                and kokomi_plan.live(state)
                and not state.force_random_targeting
                and not state.kurage_autoplaying):
            if not card.effects:
                return True
            return any(kokomi_plan._intends_to_attack(e)
                       for e in state.living_enemies)
        return orig_aim(state, card)

    kokomi_plan.plan_aimed_at_pet = aim

    orig_active = policy._active_effects

    def active(state, effect_list, card=None):
        for fx in orig_active(state, effect_list, card):
            yield _translate(state, fx)

    policy._active_effects = active
    _ENABLED = True


def _translate(state, fx):
    """The new clauses as their nearest stock op, for the stock scorer only."""
    from tier0 import constants as C
    from tier0.engine import kokomi_plan
    op = fx.get("op")
    if op == "energy_if_alone":
        return {"op": "energy", "amount": fx.get("amount", 0)}
    if op == "damage_if_alone":
        return {**fx, "op": "damage"}
    if op == "block_per_attacking_enemy":
        n = sum(1 for e in state.living_enemies
                if kokomi_plan._intends_to_attack(e))
        return {"op": "block", "amount": fx.get("amount", 0) * n}
    if op == "double_block":
        return {"op": "block",
                "amount": (state.player.block + 5) * C.PLAN_DELAY_DISCOUNT}
    if op == "kokomi":
        kind = fx.get("kind")
        amt = fx.get("amount", 0)
        if kind == "draw_if_no_plan":
            return {"op": "draw", "amount": 0 if state.kk_plan_queue else amt}
        if kind == "draw_if_target_weak":
            weak = any(e.powers.get("weak", 0) > 0
                       for e in state.living_enemies)
            return {"op": "draw", "amount": amt if weak else 0}
        if kind == "resonance":
            had = sum(1 for e in state.living_enemies if e.aura)
            return {"op": "draw", "amount": amt * had}
        if kind == "shoal_call":
            return {"op": "draw", "amount": amt}
        return {"op": "draw", "amount": 0}
    return fx


def make_pilot():
    from tier0.content import loader
    from tier0.engine import combat, kokomi_plan
    from tier0.pilot.policy import make_pilot as stock
    base = stock(loader.pilot_weights("priest"))

    def pilot(state):
        p = state.player
        hand = [c for c in p.hand if combat.card_playable(state, c)]
        if not hand:
            return None
        tok = next((c for c in hand if c.id == kokomi_plan.OPEN_THE_CASKET),
                   None)
        if tok is not None and (state.kk_casket >= _open_at()
                                or (state.turn >= 6 and state.kk_casket > 0)):
            return tok
        powers = [c for c in hand if c.type == "power"
                  and c.id.startswith(P)
                  and combat.card_cost(state, c) <= p.energy]
        if powers:
            return max(powers, key=lambda c: combat.card_cost(state, c))
        attacking = any(kokomi_plan._intends_to_attack(e)
                        for e in state.living_enemies)
        for c in hand:
            cost = combat.card_cost(state, c)
            if cost > p.energy:
                continue
            if c.id == P + "brace_for_the_tide" and attacking \
                    and not any(e.card_id == c.id
                                for e in state.kk_plan_queue):
                return c
        return base(state)

    return pilot


# --- drafting ------------------------------------------------------------------

def _offer(rng, kind, pool):
    w = RARITY[kind]
    out = []
    while len(out) < 3:
        r = rng.choices(("common", "uncommon", "rare"), weights=w)[0]
        c = rng.choice(pool[r])
        if c not in out:
            out.append(c)
    return out


_NOMINAL: dict = {}


def _nominal():
    """The median default-drafter score of the new cards it CAN price (every
    new row but the seven Powers and Shoal Call, which it prices at 0), read
    against the starter deck once per process (main session, 2026-09-29)."""
    if "v" not in _NOMINAL:
        from tier0.content import loader
        from tier05 import draft
        starter = [loader.get_card(c) for c in loader.starting_deck("kokomi")]
        vals = sorted(draft.score_offer(loader.get_card(c), starter, "generic")
                      for c in NEW_IDS if c not in NOMINAL_IDS)
        n = len(vals)
        _NOMINAL["v"] = (vals[n // 2] if n % 2
                         else (vals[n // 2 - 1] + vals[n // 2]) / 2)
    return _NOMINAL["v"]


def _baseline(card, deck_cards):
    from tier05 import draft
    if card.id in NOMINAL_IDS:
        return _nominal()
    return draft.score_offer(card, deck_cards, "generic")


def _score(card, deck_ids, deck_cards, pilot):
    from tier0 import constants as C
    short = card.id[len(P):] if card.id.startswith(P) else card.id
    if pilot == "baseline":
        return _baseline(card, deck_cards), C.DRAFT_SKIP_THRESHOLD
    floor = C.DRAFT_SKIP_THRESHOLD
    if short in NEW[pilot]:
        cap = 1 if (card.type == "power" or card.rarity == "rare") else 2
        s = 10.0
    elif short in OLD[pilot]:
        cap, s = 2, 7.0
    else:
        return _baseline(card, deck_cards), floor
    if deck_ids.count(card.id) >= cap:
        return _baseline(card, deck_cards), floor
    return s, floor


def _draft(offer_ids, deck, pilot):
    from tier0.content import loader
    deck_cards = [loader.get_card(c) for c in deck]
    best, best_s, floor = None, float("-inf"), 0.0
    for cid in offer_ids:
        s, floor = _score(loader.get_card(cid), deck, deck_cards, pilot)
        if s > best_s:
            best, best_s = cid, s
    return best if best_s >= floor else None


# --- one fight, one run ----------------------------------------------------------

def fight(deck, enemies, seed, hp):
    from tier0.content import loader
    from tier0.engine import combat
    player = loader.build_player_from_ids("kokomi", list(deck))
    player.hp = min(hp, player.max_hp)
    start = player.hp
    s = combat.run_fight(player, enemies, make_pilot(), seed=seed)
    plays = defaultdict(int)
    writes = defaultdict(int)
    close = []
    for r in s.log:
        ev = r.get("event")
        if ev == "play":
            plays[r["card"]] += 1
        elif ev == "plan_written":
            writes[r["card"]] += 1
        elif ev == "turn_close":
            close.append(int(r.get("block", 0)))
    return {"won": bool(s.player.alive) and not s.living_enemies,
            "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp), "plays": dict(plays),
            "writes": dict(writes), "close_block": close,
            "casket": s.kk_casket}


def run(seed, pilot, grant=()):
    from tier0.content import loader
    from tier05 import acts, rewards
    enc_rng = random.Random(seed)
    draw = acts.ActDraw(enc_rng, act=0)
    offer_rng = random.Random(seed + 10 ** 6)
    pool = {r: [c.id for c in cs]
            for r, cs in rewards.character_pool("kokomi").items()}
    deck = list(loader.starting_deck("kokomi")) + list(grant)
    hp = max_hp = 80
    fights, offers = [], []
    floors = TEMPLATE + ["B2"]
    act1 = False
    for floor, kind in enumerate(floors):
        if kind == "R":
            hp = min(max_hp, hp + int(0.3 * max_hp))
            continue
        if kind == "B2":
            hp = min(max_hp, hp + int(0.3 * max_hp))     # the rest between
            spec = enc_rng.choice(acts.boss_pool(1))
        else:
            spec = draw.encounter_for(kind, enc_rng)
        enemies = acts.spawn(spec, enc_rng)
        r = fight(deck, enemies, seed * 100 + floor, hp)
        r.update(kind=kind, enc=spec["id"], floor=floor, hp_in=hp,
                 n_enemies=len(enemies), deck=list(deck))
        fights.append(r)
        hp = r["hp_end"]
        if not r["won"]:
            break
        if kind == "B":
            act1 = True
        if kind in ("N", "E", "B"):
            offer = _offer(offer_rng, kind, pool)
            pick = _draft(offer, deck, pilot)
            offers.append((tuple(offer), pick))
            if pick:
                deck.append(pick)
    won = bool(fights) and fights[-1]["kind"] == "B2" and fights[-1]["won"]
    return {"seed": seed, "pilot": pilot, "grant": tuple(grant),
            "act1": act1, "won": won, "fights": fights, "offers": offers,
            "deck": deck}


def draft_only(seed, pilot, grant=()):
    """The same offers the run would see, drafted as if every fight were won:
    N N N N E N N E B, nine offers. The deck a pilot would carry to the act-2
    boss, independent of how far its run actually got."""
    from tier0.content import loader
    from tier05 import rewards
    offer_rng = random.Random(seed + 10 ** 6)
    pool = {r: [c.id for c in cs]
            for r, cs in rewards.character_pool("kokomi").items()}
    deck = list(loader.starting_deck("kokomi")) + list(grant)
    offers = []
    for kind in [k for k in TEMPLATE if k != "R"]:
        offer = _offer(offer_rng, kind, pool)
        pick = _draft(offer, deck, pilot)
        offers.append((tuple(offer), pick))
        if pick:
            deck.append(pick)
    return deck, offers


def gauntlet(seed, pilot, grant=()):
    """THE FULL-DECK GAUNTLET: the drafted deck of `draft_only` against every
    act-1 elite, every act-1 boss and every act-2 boss, each at full HP."""
    from tier05 import acts
    deck, offers = draft_only(seed, pilot, grant)
    specs = ([("E", e) for e in acts.pools(0)["elite"]]
             + [("B", e) for e in acts.boss_pool(0)]
             + [("B2", e) for e in acts.boss_pool(1)])
    fights = []
    for i, (kind, spec) in enumerate(specs):
        erng = random.Random(seed * 1000 + i)
        r = fight(deck, acts.spawn(spec, erng), seed * 1000 + i, 80)
        r.update(kind=kind, enc=spec["id"], deck=list(deck))
        fights.append(r)
    return {"seed": seed, "pilot": pilot, "grant": tuple(grant),
            "deck": deck, "offers": offers, "fights": fights}


def _w(args):
    enable()
    return run(*args)


def _wg(args):
    enable()
    return gauntlet(*args)


def pmap(fn, jobs, argl):
    if jobs <= 1:
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs) as pool:
        return pool.map(fn, argl, chunksize=4)


# --- stats ---------------------------------------------------------------------------

def m(xs, d=1):
    xs = list(xs)
    return f"{st.mean(xs):.{d}f}" if xs else "-"


def pct(k, n):
    return f"{100.0 * k / n:.1f}%" if n else "-"


def ci95(k, n):
    if not n:
        return 0.0
    p = k / n
    return 196.0 * (p * (1 - p) / n) ** 0.5


NAMES = {"volume": "Plan volume", "big_plan": "Big Plan",
         "tide": "Tide Control", "dusk": "Dusk Guard",
         "baseline": "baseline (default drafter)"}


def sec_won(out, by):
    out("\n## 1a. Act won per pilot (paired seeds)")
    out("act 1 = the stylised act 1 through its boss; run = act 1 plus the "
        "act-2 boss. 95% CI is the normal approximation.")
    out("\n| pilot | act 1 won | run won (act 1 + act-2 boss) | act-2 boss "
        "won when reached | floors fought (mean) | HP lost per fight |")
    out("|---|---|---|---|---|---|")
    res = {}
    for pl in PILOTS:
        rs = by[pl]
        n = len(rs)
        a1 = sum(r["act1"] for r in rs)
        w = sum(r["won"] for r in rs)
        reach = [r for r in rs if r["act1"]]
        res[pl] = (100 * a1 / n, 100 * w / n)
        out(f"| {NAMES[pl]} | {pct(a1, n)} ±{ci95(a1, n):.1f} | "
            f"{pct(w, n)} ±{ci95(w, n):.1f} | "
            f"{pct(sum(r['won'] for r in reach), len(reach))} | "
            f"{m((len(r['fights']) for r in rs), 2)} | "
            f"{m(f['hp_lost'] for r in rs for f in r['fights'])} |")
    v1, vr = res["volume"]
    behind1 = [NAMES[p] for p in FOCUSED if v1 - res[p][0] > 10]
    behindr = [NAMES[p] for p in FOCUSED if vr - res[p][1] > 10]
    out(f"\nMore than 10 points behind Plan volume -- act 1: "
        f"{', '.join(behind1) or 'none'}; run: "
        f"{', '.join(behindr) or 'none'}.")
    return res


def _gauntlet_cells(rs):
    cells = []
    for kind in ("E", "B", "B2"):
        fs = [f for r in rs for f in r["fights"] if f["kind"] == kind]
        k = sum(f["won"] for f in fs)
        cells.append((k, len(fs)))
    fs = [f for r in rs for f in r["fights"]]
    cells.append((sum(f["won"] for f in fs), len(fs)))
    return cells, fs


def sec_gauntlet(out, gb):
    out("\n## 1b. The full-deck gauntlet (drafted deck, full HP)")
    out("Each pilot drafts all nine offers of the same stream as if every "
        "fight were won, then fights every act-1 elite (3), act-1 boss (2) "
        "and act-2 boss (2) once per seed at 80 HP. Won = share of fights "
        "won.")
    out("\n| pilot | act-1 elites | act-1 bosses | act-2 bosses | all 7 | "
        "HP lost per fight | deck size |")
    out("|---|---|---|---|---|---|---|")
    res = {}
    for pl in PILOTS:
        cells, fs = _gauntlet_cells(gb[pl])
        res[pl] = (100 * cells[2][0] / cells[2][1],
                   100 * cells[3][0] / cells[3][1])
        out(f"| {NAMES[pl]} | "
            + " | ".join(f"{pct(k, n)} ±{ci95(k, n):.1f}" for k, n in cells)
            + f" | {m(f['hp_lost'] for f in fs)} | "
            f"{m(len(r['deck']) for r in gb[pl])} |")
    vb, va = res["volume"]
    out("\nMore than 10 points behind Plan volume -- act-2 bosses: "
        + (", ".join(NAMES[p] for p in FOCUSED if vb - res[p][0] > 10)
           or "none")
        + "; all 7: "
        + (", ".join(NAMES[p] for p in FOCUSED if va - res[p][1] > 10)
           or "none") + ".")
    return res


def sec_grand(out, by, gd, gdg):
    out("\n## 2. Big Plan against Plan volume with Grand Design held")
    out("Granted: both pilots start with Grand Design in the starter (the "
        "Tamakushi Casket is her relic in every cell). Drafted: the plain "
        "runs whose deck held Grand Design by the act-1 boss.")
    out("\n| cell | pilot | n | act 1 won | run won | Casket at "
        "the act-1 boss (mean) |")
    out("|---|---|---|---|---|---|")
    for label, src in (("granted", gd), ("drafted", by)):
        for pl in ("big_plan", "volume"):
            rs = src[pl]
            if label == "drafted":
                rs = [r for r in rs
                      if any(P + "grand_design" in f["deck"]
                             for f in r["fights"] if f["kind"] == "B")]
            n = len(rs)
            a1 = sum(r["act1"] for r in rs)
            w = sum(r["won"] for r in rs)
            cas = [f["casket"] for r in rs for f in r["fights"]
                   if f["kind"] == "B"]
            out(f"| {label} | {NAMES[pl]} | {n} | {pct(a1, n)} "
                f"±{ci95(a1, n):.1f} | {pct(w, n)} ±{ci95(w, n):.1f} | "
                f"{m(cas)} |")
    out("\nThe gauntlet with Grand Design granted (share of fights won; "
        "Casket at the end of the fight):")
    out("\n| pilot | act-1 elites | act-1 bosses | act-2 bosses | all 7 | "
        "Casket (mean) |")
    out("|---|---|---|---|---|---|")
    for pl in ("big_plan", "volume"):
        cells, fs = _gauntlet_cells(gdg[pl])
        out(f"| {NAMES[pl]} | "
            + " | ".join(f"{pct(k, n)} ±{ci95(k, n):.1f}" for k, n in cells)
            + f" | {m(f['casket'] for f in fs)} |")


def sec_dusk(out, by, gb, dg):
    g, c = P + "watatsumis_grace", P + "coral_crash"
    out("\n## 3. Dusk Guard: Grace and Coral Crash both held")
    out("Fights from the runs and the gauntlet together; the last two rows "
        "are the Dusk Guard pilot with Grace and Coral Crash GRANTED in its "
        "starter (natural drafts rarely hold both). Block carried = "
        "Block standing when she ends her turn (the "
        "`turn_close` event). A fight 'past turn 15' lasted more than 15 of "
        "her turns.")
    out("\n| pilot | fights | turns with > 30 Block carried | turns "
        "(mean / p90 / max) | share past turn 15 | won |")
    out("|---|---|---|---|---|---|")
    for pl in PILOTS:
        for both in (True, False):
            fs = [f for src in (by, gb) for r in src[pl]
                  for f in r["fights"]
                  if (g in f["deck"] and c in f["deck"]) == both]
            if not fs:
                continue
            label = f"{NAMES[pl]} ({'both held' if both else 'not both'})"
            out(_dusk_row(label, fs))
    for kind, src in (("run", dg["run"]), ("gauntlet", dg["gauntlet"])):
        fs = [f for r in src for f in r["fights"]]
        out(_dusk_row(f"Dusk Guard, both GRANTED ({kind} fights)", fs))


def _dusk_row(label, fs):
    turns = sorted(f["turns"] for f in fs)
    close = [b for f in fs for b in f["close_block"]]
    p90 = turns[int(0.9 * (len(turns) - 1))]
    return (f"| {label} | {len(fs)} | "
            f"{pct(sum(b > 30 for b in close), len(close))} | "
            f"{m(turns)} / {p90} / {turns[-1]} | "
            f"{pct(sum(t > 15 for t in turns), len(turns))} | "
            f"{pct(sum(f['won'] for f in fs), len(fs))} |")


def sec_cards(out, by, gb):
    out(f"\n## 4. The {len(NEW_IDS)} new cards still in the pool: pick and "
        "play rates")
    out("Offers from the gauntlet's full drafts (nine per seed per "
        "pilot). Fights from the runs and the gauntlet. "
        "Offered = times in a 3-card offer; taken = share of those offers "
        "that took it; plays per fight = plays (a write counts) in fights "
        "whose deck held it, per copy, all pilots pooled. Dead = held in "
        "20+ fights at under 0.3 plays per fight. Dominant = the baseline "
        "drafter takes it from 80%+ of its offers AND it is played 1.5+ "
        "times per fight held.")
    out("\n| card | rarity | baseline: offered / taken | own deck's "
        "drafter: taken | plays per fight held (fights) | flag |")
    out("|---|---|---|---|---|---|")
    from tier0.content import loader
    owner = {P + c: d for d, cs in NEW.items() for c in cs}
    flags = []
    for cid in NEW_IDS:
        cells = {}
        for pl in PILOTS:
            off = pk = 0
            for r in gb[pl]:
                for offer, pick in r["offers"]:
                    if cid in offer:
                        off += 1
                        pk += pick == cid
            cells[pl] = (off, pk)
        plays = held = 0
        for pl in PILOTS:
            for r in by[pl] + gb[pl]:
                for f in r["fights"]:
                    n = f["deck"].count(cid)
                    if n:
                        held += n
                        plays += f["plays"].get(cid, 0)
        ppf = plays / held if held else 0.0
        bo, bp = cells["baseline"]
        oo, op_ = cells[owner[cid]]
        flag = ""
        if held >= 20 and ppf < 0.3:
            flag = "DEAD"
        elif bo and bp / bo >= 0.8 and ppf >= 1.5:
            flag = "DOMINANT"
        if flag:
            flags.append(f"{loader.get_card(cid).name} ({flag})")
        out(f"| {loader.get_card(cid).name} | "
            f"{loader.get_card(cid).rarity} | {bo} / {pct(bp, bo)} | "
            f"{pct(op_, oo)} of {oo} | {ppf:.2f} ({held}) | {flag} |")
    out(f"\nFlagged: {', '.join(flags) or 'none'}.")


def _open_at() -> int:
    """The Casket count the pilot opens at. 6 is the feed pass's wrapper;
    `--open-at 3` is the early opening a player reported (2026-10-04). An
    environment variable, so the worker processes read the same number."""
    return int(os.environ.get("KK_SIM_OPEN_AT", "6"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=14)
    ap.add_argument("--open-at", type=int, default=6,
                    help="the Casket count the pilot opens at (default 6)")
    args = ap.parse_args(argv)
    os.environ["KK_SIM_OPEN_AT"] = str(args.open_at)
    enable()

    def out(s=""):
        print(s)
        sys.stdout.flush()

    out(f"# Kokomi expansion batch one, sec.5 sim -- `python -m "
        f"tools.kokomi_expansion_sim --seeds {args.seeds} --seed "
        f"{args.seed}`")
    seeds = [args.seed + i for i in range(args.seeds)]
    argl = [(s, pl) for pl in PILOTS for s in seeds]
    by = defaultdict(list)
    for r in pmap(_w, args.jobs, argl):
        by[r["pilot"]].append(r)
    gdl = [(s, pl, (P + "grand_design",)) for pl in ("big_plan", "volume")
           for s in seeds]
    gd = defaultdict(list)
    for r in pmap(_w, args.jobs, gdl):
        gd[r["pilot"]].append(r)
    gb = defaultdict(list)
    for r in pmap(_wg, args.jobs, argl):
        gb[r["pilot"]].append(r)
    gdg = defaultdict(list)
    for r in pmap(_wg, args.jobs, gdl):
        gdg[r["pilot"]].append(r)
    sec_won(out, by)
    sec_gauntlet(out, gb)
    sec_grand(out, by, gd, gdg)
    dgl = [(s, "dusk", (P + "watatsumis_grace", P + "coral_crash"))
           for s in seeds]
    dg = {"run": pmap(_w, args.jobs, dgl),
          "gauntlet": pmap(_wg, args.jobs, dgl)}
    sec_dusk(out, by, gb, dg)
    sec_cards(out, by, gb)


if __name__ == "__main__":
    main()
