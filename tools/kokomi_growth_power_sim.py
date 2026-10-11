#!/usr/bin/env python3
"""KOKOMI GROWTH POWERS -- marginal value of one Power added to a drafted
Kokomi deck, paired against a filler Strike (Prototype-stage exploration,
not a Balance measurement).

    .venv/Scripts/python.exe -m tools.kokomi_growth_power_sim --seeds 150 --seed 11 --jobs 14 --policy open3 --json out.json
    .venv/Scripts/python.exe -m tools.kokomi_growth_power_sim --report out.json

Built for `review/active/kokomi-growth-powers-2026-10-10.md` (2026-10-10),
modelled on `tools.varka_rare_marginal_sim` (#1042). Nothing on disk moves:
the proposed cards are SIM-ONLY variants built here from a shipped row and
resolved by process-local wraps:

  * rising_tide   -- Uncommon, cost 1 Power, "At the start of your turn, the
    Casket gains 1." (wrap of `refpowers.player_turn_start_late`, after the
    hand draw, through `kokomi_plan.gain_casket`).
  * rising_tide+  -- the same, Innate (the upgrade).
  * gd_keep_1     -- Grand Design bent, cost 2, "Open the Casket no longer
    empties the Casket." Open gives Strength = the full count.
  * gd_keep_2     -- the same, Open gives Strength = count // 2.
    (wrap of `kokomi_plan.open_casket`, which `effects._op_open_casket`
    reads off the module at call time.)
  * demon_form    -- stand-in reference, cost 3, "At the start of your turn,
    gain 2 Strength" (the engine's `demon_form` hook).
  * the shipped Powers: Grand Design (current), Nereid's Ascension, The Long
    Game, Treatise.

DECKS: per seed, the starter plus nine drafts (offer stream N N N N E N N E B,
rarity C/U/R 60/37/3 after a normal, 50/40/10 after an elite or boss, as
`tools.kokomi_expansion_sim`) from the current Kokomi pool, MINUS every tested
card (so no deck already holds one), by the tier-0.5 drafter
`tier05.draft.score_offer` under two archetypes ("priest", her default plan,
and "generic"), skip under `C.DRAFT_SKIP_THRESHOLD`. ARMS: deck + nothing,
deck + Strike (the filler), deck + each tested card. Every arm meets the same
fights (same spawn and combat seed).

PILOT: the stock `priest` pilot, with two harness rules applied to every arm:
the tested Powers (ids `proto_kk_*`) are played first when affordable, and the
Open the Casket token follows `--policy`:
  * stock -- no rule; the stock scorer decides (it prices `open_casket` 0).
  * open3 -- play it when the Casket holds 3 or more, at most once per turn
    (the stock scorer never sees the token). The default.
The token has Retain and no Exhaust, so a played token goes to the discard
pile and is opened again only once it is redrawn. `--token-stays` is an
INSTRUMENT, not a card text: the played token returns to hand on a later turn,
which reads the "open every turn" ceiling the paper's risk line assumes.

FIGHTS: full HP. HALLWAY = the single-enemy act-1/act-2 normals (nibbit,
mawler, fogmog, sewer_clam; tunneler, hunter_killer, louse_progenitor,
ovicopter, obscura). BOSS = vantom, lagavulin_matriarch, knowledge_demon and
kaiser_crab (two bodies; the long act-2 boss).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics as st
from collections import defaultdict

HALLWAY = [(0, "nibbit"), (0, "mawler"), (0, "fogmog"), (0, "sewer_clam"),
           (1, "tunneler"), (1, "hunter_killer"), (1, "louse_progenitor"),
           (1, "ovicopter"), (1, "obscura")]
BOSS = [(0, "vantom"), (0, "lagavulin_matriarch"), (1, "knowledge_demon"),
        (1, "kaiser_crab")]
DECK_SOURCES = ("priest", "generic")
TEMPLATE = ["N", "N", "N", "N", "E", "N", "N", "E", "B"]
RARITY = {"N": (60, 37, 3), "E": (50, 40, 10), "B": (50, 40, 10)}
P = "proto_kk_"

RISING = "kk_sim_rising_tide"
KEEP = "kk_sim_casket_keeps"          # amount = the divisor (1 or 2)

SHIPPED = ["proto_kk_grand_design", "proto_kk_nereids_ascension",
           "proto_kk_the_long_game", "proto_kk_treatise"]
ARMS = ["none", "strike", "rising_tide", "rising_tide+", "gd_keep_1",
        "gd_keep_2", "demon_form"] + SHIPPED
TESTED = frozenset(SHIPPED)

_PATCHED = False


def _token_stays() -> bool:
    return os.environ.get("KK_GROWTH_TOKEN_STAYS") == "1"


def patch():
    """Loader caches cleared, plus the two sim-only power hooks."""
    global _PATCHED
    if _PATCHED:
        return
    from tier0.engine import kokomi_plan as K, powers, refpowers
    orig_turn = refpowers.player_turn_start_late

    def turn_late(state):
        orig_turn(state)
        p = state.player
        n = int(p.powers.get(RISING, 0))
        if n and p.alive and not state.over:
            K.gain_casket(state, n)
            state.emit("rising_tide", amount=n)

    refpowers.player_turn_start_late = turn_late       # combat reads it
    orig_open = K.open_casket

    def open_casket(state):
        div = int(state.player.powers.get(KEEP, 0))
        if not div:
            return orig_open(state)
        if not K.live(state):
            return
        points = state.kk_casket                 # kept, not emptied
        state.emit("casket_opened", points=points)
        strength = points // div
        if strength > 0:
            powers.apply_power(state, state.player, "strength", strength)

    K.open_casket = open_casket
    _PATCHED = True


def _variant(new_id, name, cost, power, amount, innate=False):
    from tier0.content import loader
    c = loader.get_card("proto_kk_grand_design")
    c.id = new_id
    c.name = name
    c.cost = cost
    c.rarity = "rare"
    c.innate = innate
    c.effects = [{"op": "apply_power", "power": power, "amount": amount,
                  "target": "self"}]
    return c


def make_card(arm):
    from tier0.content import loader
    if arm == "none":
        return None
    if arm == "strike":
        return loader.get_card("strike")
    if arm == "rising_tide":
        return _variant(P + "sim_rising_tide", "Rising Tide", 1, RISING, 1)
    if arm == "rising_tide+":
        return _variant(P + "sim_rising_tide_up", "Rising Tide+", 1, RISING,
                        1, innate=True)
    if arm == "gd_keep_1":
        return _variant(P + "sim_gd_keep_1", "Grand Design (keep, 1/1)", 2,
                        KEEP, 1)
    if arm == "gd_keep_2":
        return _variant(P + "sim_gd_keep_2", "Grand Design (keep, 1/2)", 2,
                        KEEP, 2)
    if arm == "demon_form":
        return _variant(P + "sim_ref_demon_form", "Demon Form", 3,
                        "demon_form", 2)
    return loader.get_card(arm)


def make_pilot(policy):
    from tier0.content import loader
    from tier0.engine import combat, kokomi_plan as K
    from tier0.pilot.policy import make_pilot as stock
    base = stock(loader.pilot_weights("priest"))
    opened = {"turn": None}

    def pilot(state):
        p = state.player
        s = int(p.powers.get("strength", 0))
        if s > getattr(state, "_kk_sim_max_str", 0):
            state._kk_sim_max_str = s
        if _token_stays() and opened["turn"] != state.turn and not any(
                c.id.startswith(K.OPEN_THE_CASKET) for c in p.hand):
            # INSTRUMENT ONLY (--token-stays): a played token comes back to
            # hand from the discard pile on a later turn, so it can be opened
            # every turn -- the paper's "opening every turn" ceiling, not a
            # card text.
            for pile in (p.discard_pile, p.draw_pile):
                tok = next((c for c in pile
                            if c.id.startswith(K.OPEN_THE_CASKET)), None)
                if tok is not None:
                    if len(p.hand) < 10:
                        pile.remove(tok)
                        p.hand.append(tok)
                    break
        hand = [c for c in p.hand if combat.card_playable(state, c)]
        if not hand:
            return None
        if policy == "open3":
            tok = next((c for c in hand if c.id.startswith(K.OPEN_THE_CASKET)),
                       None)
            if (tok is not None and state.kk_casket >= 3
                    and opened["turn"] != state.turn):
                opened["turn"] = state.turn
                return tok
        pw = [c for c in hand if c.type == "power" and c.id.startswith(P)
              and (c.id in TESTED or c.id.startswith(P + "sim_"))
              and combat.card_cost(state, c) <= p.energy]
        if pw:
            return max(pw, key=lambda c: combat.card_cost(state, c))
        if policy == "open3":
            # the token is played by the rule above only: hide it from the
            # stock scorer for this decision
            whole = list(p.hand)
            p.hand[:] = [c for c in whole
                         if not c.id.startswith(K.OPEN_THE_CASKET)]
            try:
                return base(state)
            finally:
                p.hand[:] = whole
        return base(state)

    return pilot


# --- drafting -----------------------------------------------------------------

def _pool():
    from tier05 import rewards
    return {r: [c.id for c in cs if c.id not in TESTED]
            for r, cs in rewards.character_pool("kokomi").items()}


def _offer(rng, kind, pool):
    w = RARITY[kind]
    out = []
    while len(out) < 3:
        r = rng.choices(("common", "uncommon", "rare"), weights=w)[0]
        c = rng.choice(pool[r])
        if c not in out:
            out.append(c)
    return out


def draft_deck(seed, archetype):
    from tier0 import constants as C
    from tier0.content import loader
    from tier05 import draft
    rng = random.Random(seed + 10 ** 6)
    pool = _pool()
    deck = list(loader.starting_deck("kokomi"))
    for kind in TEMPLATE:
        offer = _offer(rng, kind, pool)
        cards = [loader.get_card(c) for c in deck]
        scored = [(draft.score_offer(loader.get_card(c), cards, archetype), c)
                  for c in offer]
        s, best = max(scored)
        if s >= C.DRAFT_SKIP_THRESHOLD:
            deck.append(best)
    return deck


# --- one fight -----------------------------------------------------------------

def _spec(act, enc_id):
    from tier05 import acts
    p = acts.pools(act)
    for e in p["easy"] + p["hard"] + p["elite"] + acts.boss_pool(act):
        if e["id"] == enc_id:
            return e
    raise KeyError(enc_id)


def one_fight(deck, card, act, enc_id, fseed, policy):
    from tier0.content import loader
    from tier0.engine import combat
    from tier05 import acts
    enemies = acts.spawn(_spec(act, enc_id), random.Random(fseed))
    player = loader.build_player_from_ids("kokomi", list(deck))
    if card is not None:
        player.draw_pile.append(card)
    total = sum(e.hp for e in enemies)
    s = combat.run_fight(player, enemies, make_pilot(policy), seed=fseed)
    won = bool(s.player.alive) and not s.living_enemies
    left = sum(max(0, e.hp) for e in s.enemies)
    played_turn = None
    opens = 0
    carried = 0
    open_pts = []
    for r in s.log:
        ev = r.get("event")
        if (played_turn is None and card is not None and ev == "play"
                and r.get("card") == card.id):
            played_turn = r.get("turn")
        elif ev == "casket_count" and r.get("why") == "carry_out":
            carried += 1
        elif ev == "casket_opened":
            opens += 1
            open_pts.append(int(r.get("points", 0)))
    max_str = max(getattr(s, "_kk_sim_max_str", 0),
                  int(s.player.powers.get("strength", 0)))
    return {"won": won, "turns": s.turn,
            "hp_lost": s.player.max_hp - max(0, s.player.hp),
            "dmg": total - left, "dmg_frac": (total - left) / total,
            "played_turn": played_turn, "opens": opens,
            "open_pts": open_pts, "max_str": max_str,
            "casket_end": int(s.kk_casket), "carried": carried}


def work(args):
    seed, source, policy, stays = args
    os.environ["KK_GROWTH_TOKEN_STAYS"] = "1" if stays else "0"
    patch()
    deck = draft_deck(seed, source)
    out = []
    for cat, fights in (("hallway", HALLWAY), ("boss", BOSS)):
        for i, (act, enc) in enumerate(fights):
            fseed = seed * 1000 + (0 if cat == "hallway" else 100) + i
            for arm in ARMS:
                r = one_fight(deck, make_card(arm), act, enc, fseed, policy)
                r.update(seed=seed, source=source, cat=cat, enc=enc, arm=arm,
                         deck_n=len(deck))
                out.append(r)
    return out


def pmap(fn, jobs, argl):
    if jobs <= 1:
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs, initializer=patch) as p:
        return p.map(fn, argl, chunksize=2)


# --- report --------------------------------------------------------------------

def _name(arm):
    return arm.replace(P, "")


def _q(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * (len(xs) - 1) + 0.5))] if xs else 0


def report(rows, out=print):
    by = defaultdict(list)
    for r in rows:
        by[(r["cat"], r["arm"])].append(r)
    arms = []
    for r in rows:
        if r["arm"] not in arms:
            arms.append(r["arm"])

    def idx(cat, arm):
        return {(r["seed"], r["source"], r["enc"]): r for r in by[(cat, arm)]}

    def se(x):
        return st.pstdev(x) / len(x) ** 0.5 if len(x) > 1 else 0.0

    for cat in ("hallway", "boss"):
        out(f"\n### {cat} -- vs deck + Strike (paired; d = arm - strike)\n")
        out("| arm | n | win% | d win pp (+-se) | d HP lost (+-se) | "
            "enemy HP removed (mean) | d HP removed | d turns | turns | "
            "played% | opens/fight |")
        out("|---|---|---|---|---|---|---|---|---|---|---|")
        b = idx(cat, "strike")
        res = []
        for arm in arms:
            a = idx(cat, arm)
            ks = [k for k in a if k in b]
            dw = [a[k]["won"] - b[k]["won"] for k in ks]
            dh = [a[k]["hp_lost"] - b[k]["hp_lost"] for k in ks]
            dd = [a[k]["dmg"] - b[k]["dmg"] for k in ks]
            dt = [a[k]["turns"] - b[k]["turns"] for k in ks]
            rs = by[(cat, arm)]
            pl = (100 * st.mean(r["played_turn"] is not None for r in rs)
                  if arm != "none" else float("nan"))
            res.append((st.mean(dw), arm, len(ks), st.mean(r["won"] for r in rs),
                        se(dw), st.mean(dh), se(dh),
                        st.mean(r["dmg"] for r in rs), st.mean(dd),
                        st.mean(dt), st.mean(r["turns"] for r in rs), pl,
                        st.mean(r["opens"] for r in rs)))
        res.sort(key=lambda t: -t[0])
        for (dw, arm, n, win, sw, dh, sh, dmg, dd, dt, tu, pl, op) in res:
            out(f"| {_name(arm)} | {n} | {100*win:.1f} | {100*dw:+.1f} "
                f"(+-{100*sw:.1f}) | {dh:+.2f} (+-{sh:.2f}) | {dmg:.1f} | "
                f"{dd:+.1f} | {dt:+.2f} | {tu:.2f} | {pl:.0f} | {op:.2f} |")

    out("\n### Max Strength reached per fight\n")
    out("| arm | hallway median | hallway p90 | hallway max | boss median | "
        "boss p90 | boss max | boss: fights with max >= 30 |")
    out("|---|---|---|---|---|---|---|---|")
    for arm in arms:
        h = [r["max_str"] for r in by[("hallway", arm)]]
        bb = [r["max_str"] for r in by[("boss", arm)]]
        out(f"| {_name(arm)} | {_q(h, .5)} | {_q(h, .9)} | {max(h)} | "
            f"{_q(bb, .5)} | {_q(bb, .9)} | {max(bb)} | "
            f"{100*sum(x >= 30 for x in bb)/len(bb):.1f}% |")

    out("\n### Max Strength, Grand Design variants, fights where the card "
        "was played\n")
    out("| arm | cohort | n | median | p90 | max |")
    out("|---|---|---|---|---|---|")
    for arm in ("gd_keep_1", "gd_keep_2", "demon_form",
                "proto_kk_grand_design", "strike"):
        for cat in ("hallway", "boss"):
            xs = [r["max_str"] for r in by[(cat, arm)]
                  if arm == "strike" or r["played_turn"] is not None]
            if xs:
                out(f"| {_name(arm)} | {cat} | {len(xs)} | {_q(xs, .5)} | "
                    f"{_q(xs, .9)} | {max(xs)} |")

    out("\n### Open the Casket: how the pilot plays it (deck + Strike)\n")
    out("| cohort | fights | share with 0 opens | share with 2+ opens | "
        "opens/fight | mean points per open | Casket left at end (mean) | "
        "Plans carried out per turn |")
    out("|---|---|---|---|---|---|---|---|")
    for cat in ("hallway", "boss"):
        for arm in ("strike", "rising_tide", "gd_keep_1", "gd_keep_2"):
            rs = by[(cat, arm)]
            pts = [x for r in rs for x in r["open_pts"]]
            out(f"| {cat} / {_name(arm)} | {len(rs)} | "
                f"{100*st.mean(r['opens'] == 0 for r in rs):.0f}% | "
                f"{100*st.mean(r['opens'] >= 2 for r in rs):.0f}% | "
                f"{st.mean(r['opens'] for r in rs):.2f} | "
                f"{st.mean(pts) if pts else 0:.2f} | "
                f"{st.mean(r['casket_end'] for r in rs):.2f} | "
                f"{sum(r['carried'] for r in rs) / sum(r['turns'] for r in rs):.2f} |")

    out("\n### Boss enemy HP removed by encounter (mean; spawned HP in "
        "brackets)\n")
    showd = ["strike", "rising_tide", "rising_tide+", "gd_keep_1",
             "gd_keep_2", "demon_form", "proto_kk_grand_design",
             "proto_kk_nereids_ascension", "proto_kk_the_long_game",
             "proto_kk_treatise"]
    bd = defaultdict(list)
    for r in rows:
        bd[(r["enc"], r["arm"])].append(r)
    out("| encounter | " + " | ".join(_name(a) for a in showd) + " |")
    out("|---|" + "---|" * len(showd))
    for _, enc in BOSS:
        rs = [r for r in bd[(enc, "strike")] if r["dmg_frac"]]
        tot = st.mean(r["dmg"] / r["dmg_frac"] for r in rs) if rs else 0
        out(f"| {enc} [{tot:.0f}] | " + " | ".join(
            f"{st.mean(r['dmg'] for r in bd[(enc, a)]):.1f}"
            for a in showd) + " |")

    out("\n### Boss win% by encounter\n")
    show = ["strike", "rising_tide", "rising_tide+", "gd_keep_1", "gd_keep_2",
            "demon_form", "proto_kk_grand_design",
            "proto_kk_nereids_ascension", "proto_kk_the_long_game",
            "proto_kk_treatise"]
    out("| encounter | turns (strike) | " + " | ".join(_name(a) for a in show)
        + " |")
    out("|---|---|" + "---|" * len(show))
    be = defaultdict(list)
    for r in rows:
        be[(r["enc"], r["arm"])].append(r)
    for _, enc in BOSS:
        out(f"| {enc} | {st.mean(r['turns'] for r in be[(enc, 'strike')]):.1f}"
            " | " + " | ".join(
                f"{100*st.mean(r['won'] for r in be[(enc, a)]):.1f}"
                for a in show) + " |")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=150)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--policy", choices=("stock", "open3"), default="open3")
    ap.add_argument("--token-stays", action="store_true",
                    help="instrument: a played Open the Casket returns to "
                    "hand on a later turn (the open-every-turn ceiling)")
    ap.add_argument("--json")
    ap.add_argument("--report")
    a = ap.parse_args(argv)
    if a.report:
        with open(a.report, encoding="utf-8") as f:
            report(json.load(f))
        return
    argl = [(a.seed + i, src, a.policy, a.token_stays)
            for i in range(a.seeds) for src in DECK_SOURCES]
    rows = [r for chunk in pmap(work, a.jobs, argl) for r in chunk]
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    report(rows)


if __name__ == "__main__":
    main()
