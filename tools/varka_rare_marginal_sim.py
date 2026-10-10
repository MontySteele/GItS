#!/usr/bin/env python3
"""VARKA RARE MARGINAL VALUE -- one card added to a drafted Varka deck, paired
against a filler (Prototype-stage exploration, not a Balance measurement).

    .venv/Scripts/python.exe -m tools.varka_rare_marginal_sim --seeds 200 --seed 11 --jobs 14 --json out.json
    .venv/Scripts/python.exe -m tools.varka_rare_marginal_sim --report out.json

Built for the Converging Winds rework question (2026-10-10). Nothing on disk
moves: the two rework options are SIM-ONLY variant cards, built here from the
shipped row and resolved by a process-local wrap of `varka_oath.on_swirl`:

  * cw_a  -- cost 1 Power, "Your Swirls deal 4 [6] additional damage to ALL
    enemies." Read as the Swirl's own flat damage made bigger: after the
    shared Swirl (spread + flat 2, `reactions._react`) every living enemy
    takes N more through `reactions._splash`, the door the flat 2 uses
    (element-less, ignores Block, Durin's scaling not applied).
  * cw_b  -- cost 1 Power, "Whenever you Swirl, gain 1 more Oath of the
    element Swirled." Read as +1 Oath of the swirled element on EVERY Swirl
    (one `varka_oath.gain` event, so Dawn Wind's March and Oath Unto Death
    see it), on top of the once-per-play Swirl credit.
  * demon_form -- a reference Rare Power (Ironclad's Demon Form, cost 3,
    "At the start of your turn, gain 2 Strength"), on the engine's existing
    `demon_form` power hook.

DECKS: per seed, the starter (one of four starter Knights, seed % 4) plus the
nine drafts of `tools.varka_expansion_sim`'s gauntlet (`_wo`'s drafting),
by the `default` drafter and by the Swirl-forced `gale` drafter. ARMS: the
deck plus nothing, plus a base Strike (the filler), plus each Rare of his
pool, plus the variants. Every arm meets the same fights (same encounter
spawn and combat seed). The play pilot is `varka_expansion_sim.make_pilot`
(stock pilot, his Powers first when affordable; the variants keep the
`proto_vk_` prefix so they get that treatment, as does the reference).

FIGHTS: full HP (80). SINGLE: act-1 elites byrdonis, bygone_effigy, act-1
bosses vantom, lagavulin_matriarch, act-2 boss knowledge_demon. MULTI: act-1
inklets (3), slime_group (2), phantasmal_gardener (4); act-2
exoskeleton_trio (3), decimillipede (3), kaiser_crab (2).
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import statistics as st
from collections import defaultdict

from tools import varka_expansion_sim as X

SINGLE = [(0, "byrdonis"), (0, "bygone_effigy"), (0, "vantom"),
          (0, "lagavulin_matriarch"), (1, "knowledge_demon")]
MULTI = [(0, "inklets"), (0, "slime_group"), (0, "phantasmal_gardener"),
         (1, "exoskeleton_trio"), (1, "decimillipede"), (1, "kaiser_crab")]
DECK_SOURCES = ("default", "gale")

CW_A = "vk_cw_variant_a"
CW_B = "vk_cw_variant_b"

_PATCHED = False


def patch():
    """`X.enable()` plus the variant powers' Swirl hook (process-local)."""
    global _PATCHED
    X.enable()
    if _PATCHED:
        return
    from tier0.engine import reactions, varka_oath as V
    orig = V.on_swirl

    def on_swirl(state, enemy, aura):
        p = state.player
        if V.ledger(p) is not None:
            bonus = int(p.powers.get(CW_A, 0))
            if bonus:
                hit = list(state.living_enemies)
                for other in hit:
                    reactions._splash(state, other, bonus)
                state.emit("cw_a_bonus", amount=bonus, enemies=len(hit))
        orig(state, enemy, aura)
        extra = int(p.powers.get(CW_B, 0))
        if extra and aura in V.ELEMENTS and V.ledger(p) is not None:
            V.gain(state, aura, extra, "cw_b")

    V.on_swirl = on_swirl
    _PATCHED = True


def _variant(base_id, new_id, name, cost, power, amount):
    from tier0.content import loader
    c = loader.get_card(base_id)
    c.id = new_id
    c.name = name
    c.cost = cost
    c.effects = [{"op": "apply_power", "power": power, "amount": amount,
                  "target": "self"}]
    return c


def make_card(arm):
    """A fresh Card for an arm, or None for the empty arm."""
    from tier0.content import loader
    cw = "proto_vk_converging_winds"
    if arm == "none":
        return None
    if arm == "strike":
        return loader.get_card("strike")
    if arm == "cw_a":
        return _variant(cw, "proto_vk_cw_a", "CW (a)", 1, CW_A, 4)
    if arm == "cw_a+":
        return _variant(cw, "proto_vk_cw_a_up", "CW (a)+", 1, CW_A, 6)
    if arm == "cw_b":
        return _variant(cw, "proto_vk_cw_b", "CW (b)", 1, CW_B, 1)
    if arm == "demon_form":
        return _variant(cw, "proto_vk_ref_demon_form", "Demon Form", 3,
                        "demon_form", 2)
    return loader.get_card(arm)


def arms():
    rares = list(X.pool()["rare"])
    return ["none", "strike", "cw_a", "cw_a+", "cw_b", "demon_form"] + rares


def draft_deck(seed, source, element):
    offer_rng = random.Random(seed + 10 ** 6)
    pl = X.pool()
    deck = []
    for kind in [k for k in X.TEMPLATE if k != "R"]:
        offer = X._offer(offer_rng, kind, pl)
        pick = X._draft(offer, deck, source, element)
        if pick:
            deck.append(pick)
    return deck


def _spec(act, enc_id):
    from tier05 import acts
    p = acts.pools(act)
    for e in p["easy"] + p["hard"] + p["elite"] + acts.boss_pool(act):
        if e["id"] == enc_id:
            return e
    raise KeyError(enc_id)


def one_fight(element, deck, card, act, enc_id, fseed):
    from tier0.engine import combat, varka_oath as V
    from tier05 import acts
    enemies = acts.spawn(_spec(act, enc_id), random.Random(fseed))
    player = V.build_player(element, extra=tuple(deck))
    if card is not None:
        player.draw_pile.append(card)
    total_hp = sum(e.hp for e in enemies)
    s = combat.run_fight(player, enemies, X.make_pilot(), seed=fseed)
    led = getattr(s.player, "varka_ledger", None)
    won = bool(s.player.alive) and not s.living_enemies
    left = sum(max(0, e.hp) for e in s.enemies)
    played_turn = None
    post_swirls = 0
    bonus_targets = 0
    for r in s.log:
        ev = r.get("event")
        if (played_turn is None and card is not None and ev == "play"
                and r.get("card") == card.id):
            played_turn = r.get("turn")
        elif ev == "varka_swirl" and played_turn is not None:
            post_swirls += 1
        elif ev == "cw_a_bonus":
            bonus_targets += r.get("enemies", 0)
    return {"won": won, "turns": s.turn,
            "hp_lost": 80 - max(0, s.player.hp),
            "dmg_frac": (total_hp - left) / total_hp if total_hp else 0.0,
            "swirls": led.swirls_made if led else 0,
            "oath": sum(led.oath.values()) if led else 0,
            "played_turn": played_turn,
            # Swirls made after the added card was played (what (a) and (b)
            # scale with), and for cw_a the enemies its bonus struck.
            "post_swirls": post_swirls, "bonus_targets": bonus_targets}


def work(args):
    """One (seed, deck source): every arm on every fight."""
    patch()
    seed, source = args
    element = X.ELEMENTS[seed % 4]
    deck = draft_deck(seed, source, element)
    out = []
    for cat, fights in (("single", SINGLE), ("multi", MULTI)):
        for i, (act, enc) in enumerate(fights):
            fseed = seed * 1000 + (0 if cat == "single" else 100) + i
            for arm in arms():
                r = one_fight(element, deck, make_card(arm), act, enc, fseed)
                r.update(seed=seed, source=source, cat=cat, enc=enc, arm=arm)
                out.append(r)
    return out


def pmap(fn, jobs, argl):
    if jobs <= 1:
        patch()
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs, initializer=patch) as p:
        return p.map(fn, argl, chunksize=2)


# --- report -----------------------------------------------------------------

def report(rows, out=print):
    by = defaultdict(list)
    for r in rows:
        by[(r["cat"], r["arm"])].append(r)
        by[(r["cat"] + ":" + r["source"], r["arm"])].append(r)
    key = {(r["seed"], r["source"], r["cat"], r["enc"]): None for r in rows}
    del key

    def idx(cat, arm):
        return {(r["seed"], r["source"], r["enc"]): r for r in by[(cat, arm)]}

    def paired(cat, arm, base="strike"):
        a, b = idx(cat, arm), idx(cat, base)
        ks = [k for k in a if k in b]
        dw = [a[k]["won"] - b[k]["won"] for k in ks]
        dh = [a[k]["hp_lost"] - b[k]["hp_lost"] for k in ks]
        dd = [a[k]["dmg_frac"] - b[k]["dmg_frac"] for k in ks]
        dt = [a[k]["turns"] - b[k]["turns"] for k in ks]

        def se(x):
            return st.pstdev(x) / len(x) ** 0.5 if len(x) > 1 else 0.0
        return (len(ks), st.mean(dw), se(dw), st.mean(dh), se(dh),
                st.mean(dd), st.mean(dt))

    cats = ["single", "multi"] + [f"{c}:{s}" for c in ("single", "multi")
                                  for s in DECK_SOURCES]
    arm_list = []
    for r in rows:
        if r["arm"] not in arm_list:
            arm_list.append(r["arm"])
    for cat in cats:
        out(f"\n### {cat} -- vs deck + Strike (paired; d = arm - strike)\n")
        out("| arm | n | win% | d win pp (+-se) | d HP lost (+-se) "
            "| d dmg% (losses incl.) | d turns | played% | swirls/fight |")
        out("|---|---|---|---|---|---|---|---|---|")
        res = []
        for arm in arm_list:
            rs = by[(cat, arm)]
            if not rs:
                continue
            n, dw, sw, dh, sh, dd, dt = paired(cat, arm)
            win = st.mean(r["won"] for r in rs)
            pl = (st.mean(r["played_turn"] is not None for r in rs)
                  if arm not in ("none",) else float("nan"))
            sw_ = st.mean(r["swirls"] for r in rs)
            res.append((dw, dh, arm, n, win, sw, sh, dd, dt, pl, sw_))
        res.sort(key=lambda t: (-t[0], t[1]))
        for dw, dh, arm, n, win, sw, sh, dd, dt, pl, sw_ in res:
            out(f"| {arm.replace('proto_vk_', '')} | {n} | {100*win:.1f} | "
                f"{100*dw:+.1f} (+-{100*sw:.1f}) | {dh:+.2f} (+-{sh:.2f}) | "
                f"{100*dd:+.1f} | {dt:+.2f} | {100*pl:.0f} | {sw_:.2f} |")
    # Conditional splits: fights the filler deck wins (HP lost, both won)
    # and fights it loses (share of enemy HP removed).
    out("\n### Conditional splits vs deck + Strike\n")
    out("| arm | single: d HP lost when both won | single: d dmg% when "
        "strike lost | multi: d HP lost when both won | multi: d dmg% when "
        "strike lost | post-play Swirls single / multi |")
    out("|---|---|---|---|---|---|")
    for arm in arm_list:
        cells = []
        for cat in ("single", "multi"):
            a, b = idx(cat, arm), idx(cat, "strike")
            ks = [k for k in a if k in b]
            bw = [a[k]["hp_lost"] - b[k]["hp_lost"] for k in ks
                  if a[k]["won"] and b[k]["won"]]
            bl = [a[k]["dmg_frac"] - b[k]["dmg_frac"] for k in ks
                  if not b[k]["won"]]
            cells += [f"{st.mean(bw):+.2f}" if bw else "-",
                      f"{100*st.mean(bl):+.1f}" if bl else "-"]
        ps = [st.mean(r.get("post_swirls", 0) for r in by[(c, arm)])
              for c in ("single", "multi")]
        out(f"| {arm.replace('proto_vk_', '')} | " + " | ".join(cells)
            + f" | {ps[0]:.2f} / {ps[1]:.2f} |")
    for arm in ("cw_a", "cw_a+"):
        for cat in ("single", "multi"):
            rs = by[(cat, arm)]
            if rs:
                n = 4 if arm == "cw_a" else 6
                out(f"\n{arm} {cat}: bonus damage dealt per fight (gross, "
                    f"before overkill) = "
                    f"{n*st.mean(r.get('bonus_targets', 0) for r in rs):.1f}")
    # Swirl distribution on the filler arm
    out("\n### Swirls per fight, deck + Strike arm\n")
    out("| cohort | mean | median | p25 | p75 | share with 0 |")
    out("|---|---|---|---|---|---|")
    for cat in cats:
        xs = sorted(r["swirls"] for r in by[(cat, "strike")])
        if not xs:
            continue
        q = st.quantiles(xs, n=4)
        out(f"| {cat} | {st.mean(xs):.2f} | {st.median(xs):.0f} | {q[0]:.0f} "
            f"| {q[2]:.0f} | {100*sum(x == 0 for x in xs)/len(xs):.0f}% |")
    out("\n### Swirls per encounter (deck + Strike), and win% strike/cw_a/cw_b\n")
    out("| encounter | swirls | win% strike | win% cw_a | win% cw_b "
        "| win% cw current |")
    out("|---|---|---|---|---|---|")
    encs = []
    for r in rows:
        if r["enc"] not in encs:
            encs.append(r["enc"])
    be = defaultdict(list)
    for r in rows:
        be[(r["enc"], r["arm"])].append(r)
    for e in encs:
        s = be[(e, "strike")]
        out(f"| {e} | {st.mean(r['swirls'] for r in s):.2f} | "
            + " | ".join(f"{100*st.mean(r['won'] for r in be[(e, a)]):.1f}"
                         for a in ("strike", "cw_a", "cw_b",
                                   "proto_vk_converging_winds")) + " |")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--json")
    ap.add_argument("--report")
    a = ap.parse_args(argv)
    if a.report:
        with open(a.report, encoding="utf-8") as f:
            report(json.load(f))
        return
    argl = [(a.seed + i, src) for i in range(a.seeds) for src in DECK_SOURCES]
    rows = [r for chunk in pmap(work, a.jobs, argl) for r in chunk]
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    report(rows)


if __name__ == "__main__":
    main()
