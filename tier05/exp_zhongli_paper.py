"""Zhongli paper sim (EXPLORATION, not a registered cell).

Answers the seven questions of the main session's Zhongli sim spec against
`review/active/zhongli-paper-kit-2026-09-28.md`, with the element port's two
switches ON (`C.SWIRL_PAYS`, `C.CRYSTALLIZE_KEEPS_AURA`) and the arm
`tier0.engine.zhongli_tab` installed for this process only.

    PYTHONPATH=. python -m tier05.exp_zhongli_paper --fights 300 --runs 400

Two surfaces:

* THE BATTERY -- tier 0's frozen encounters (swarm, attrition, burst_check,
  tank_boss, punisher, gauntlet), Zhongli's starter and three sample decks
  under each Mora policy, beside Klee, Kokomi, Furina and REF_IRONCLAD
  starters on the same encounters and seeds (tier 0 runs the SHIPPED kits;
  their arm flags stay off).
* WHOLE RUNS -- the tier 0.5 map, encounters, gold income, treasure and rest
  heal, with Zhongli's own reward screen, shop and settlement (below). The
  comparators' runs are `model.run_many`'s own, bare loadout.

WHAT THE ZHONGLI RUN LAYER IS (the smallest thing that answers 1-4), and
where it differs from the comparators' run layer:
  * gold: `C.GOLD_START` 99, `C.GOLD_INCOME` (N 10, E 25, B 100), treasure
    `C.TREASURE_GOLD` 40 -- the repo's own numbers.
  * settlement: after the fight's gold income, the Tab is paid from gold;
    a shortfall becomes one Unpaid Invoice (an Unplayable status in the deck)
    for the exact amount; Invoices count against the credit limit.
  * shop: pay every Invoice it can afford (oldest first), then one removal
    (Strike, then Defend) at `SHOP_REMOVAL_PRICE` rising by the step, then
    buy the best of three pool cards at `SHOP_CARD_PRICE` if its priority is
    at least 6.
  * reward screen: three offers from the 16-card sample pool at
    `C.RARITY_ODDS` (a non-final boss forces Rare), picked by one static
    priority list; the `never` policy skips Mora-only cards.
  * rest: heal below the repo's thresholds, else remove a Strike. NO UPGRADES
    (none are written), NO EVENTS (an Event room does nothing), no relics,
    no potions, no companions. The comparators have upgrades and events, so
    run-level win rates across characters are context, not a verdict.
"""

from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

POLICIES = ("always", "threshold", "never")
PAY_MODES = ("gold_first", "tab_first")
COMPARATORS = ("ref_ironclad", "klee", "kokomi", "furina")

DECKS = {
    "starter": [],
    # On the Tab (default): Mora cards as extra Energy.
    "tab": ["zl_rain_of_stone", "zl_rain_of_stone", "zl_earthly_tremor",
            "zl_liquidity", "zl_bulk_purchase", "zl_jade_screen",
            "zl_dominance", "zl_gold_tongued", "zl_settle_accounts",
            "zl_lithic_ledger"],
    # Contracts (the ceiling).
    "contracts": ["zl_contract_of_stone", "zl_contract_of_stone",
                  "zl_contract_of_earth", "zl_contract_of_earth",
                  "zl_contract_of_jade", "zl_pillar_of_contracts",
                  "zl_jade_screen", "zl_rain_of_stone", "zl_earthly_tremor",
                  "zl_settle_accounts"],
    # The Rock.
    "rock": ["zl_jade_shield", "zl_jade_shield", "zl_stone_stele",
             "zl_planet_befall", "zl_jade_screen", "zl_jade_screen",
             "zl_earthly_tremor", "zl_rain_of_stone", "zl_contract_of_stone",
             "zl_dominance"],
}

PRIORITY = {
    "zl_stone_stele": 9, "zl_planet_befall": 9, "zl_jade_shield": 7,
    "zl_contract_of_stone": 7, "zl_earthly_tremor": 7, "zl_rain_of_stone": 6,
    "zl_jade_screen": 6, "zl_pillar_of_contracts": 5,
    "zl_contract_of_earth": 5, "zl_dominance": 5, "zl_gold_tongued": 5,
    "zl_liquidity": 5, "zl_contract_of_jade": 4, "zl_settle_accounts": 4,
    "zl_lithic_ledger": 3, "zl_bulk_purchase": 3,
}
MORA_ONLY_OR_MORA_READERS = {"zl_liquidity", "zl_contract_of_jade",
                             "zl_gold_tongued", "zl_bulk_purchase",
                             "zl_settle_accounts", "zl_lithic_ledger"}
ONE_COPY = {"zl_stone_stele", "zl_gold_tongued", "zl_lithic_ledger",
            "zl_pillar_of_contracts", "zl_planet_befall"}


# ----------------------------------------------------------------------
# setup
# ----------------------------------------------------------------------
def _setup(pay_mode: str = "gold_first", partner: bool = False):
    from tier0 import constants as C
    from tier0.engine import zhongli_tab as Z
    C.SWIRL_PAYS = True
    C.CRYSTALLIZE_KEEPS_AURA = True
    Z.install()
    Z.PAY_MODE = pay_mode
    Z.PARTNER_AURA_PER_TURN = partner
    return Z


def _stall_pilot(Z, base, extra_turns: int):
    """Q4's staller: with ONE enemy left, play no Attack for up to
    `extra_turns` turns (the Stele still ticks) -- the 'keep it alive to
    borrow more' line the paper's rule 2 is meant to make unprofitable."""
    def pilot(state):
        living = state.living_enemies
        zl = Z.ledger(state)
        if len(living) == 1:
            if not hasattr(zl, "stall_from"):
                zl.stall_from = state.turn
            if state.turn < zl.stall_from + extra_turns:
                hand = state.player.hand
                hidden = [c for c in hand if c.type == "attack"]
                for c in hidden:
                    hand.remove(c)
                try:
                    return base(state)
                finally:
                    hand.extend(hidden)
        return base(state)
    return pilot


# ----------------------------------------------------------------------
# THE BATTERY
# ----------------------------------------------------------------------
def zhongli_battery(deck: str, policy: str, fights: int, seed: int,
                    gold: int = 99, pay_mode: str = "gold_first",
                    partner: bool = False, stall: int = 0) -> list[dict]:
    Z = _setup(pay_mode, partner)
    from tier0.content import loader
    from tier0.engine.combat import run_fight
    from tier0.harness import metrics
    rows = []
    ids = Z.STARTER + DECKS[deck]
    for enc in loader.encounter_ids():
        for i in range(fights):
            hp = Z.HP
            stage_rows = []
            for stage in loader.encounter_stages(enc):
                p = Z.build_player(ids, hp, Z.HP, gold, 0, 0)
                pilot = Z.make_pilot(policy)
                if stall:
                    pilot = _stall_pilot(Z, pilot, stall)
                st = run_fight(p, loader.build_encounter(stage), pilot,
                               seed=seed + i)
                zl = Z.close_fight(st)
                fs = metrics.extract(st, hp)
                crys = _count_crystallize(st)
                stage_rows.append(_fight_row(Z, st, zl, fs, enc, stage, crys))
                hp = st.player.hp
                if hp <= 0 or st.living_enemies:
                    break
            rows.extend(stage_rows)
    return rows


def _count_crystallize(st) -> int:
    return sum(1 for ev in st.log if ev["event"] == "reaction"
               and ev.get("reaction") == "crystallize")


def _fight_row(Z, st, zl, fs, enc, stage, crys) -> dict:
    won = bool(st.player.alive) and not st.living_enemies
    return {
        "enc": enc, "stage": stage, "won": won, "turns": st.turn,
        "hp_lost": fs.hp_start - max(0, fs.hp_end),
        "dmg": fs.total_damage_dealt,
        "mora_gold": zl.mora_paid_gold, "tab": zl.tab,
        "tab_peak": zl.tab_peak, "settle_paid": zl.settle_paid,
        "net_gold": (zl.gold - zl.gold_start) - zl.tab,
        "energy_mora": zl.energy_from_mora,
        "mora_spent": zl.mora_paid_gold + zl.mora_on_tab,
        "stele_dmg": zl.stele_damage, "crys": crys,
        "refused": zl.refused_at_limit,
        "extra_credit_used": zl.extra_credit_used,
        "contracts": [(c["card"], c["kept"], c["credit_used_after"])
                      for c in zl.contracts],
        "mora_plays": dict(zl.mora_plays),
        "ledger_block": zl.ledger_block,
    }


def comparator_battery(character: str, fights: int, seed: int) -> list[dict]:
    _setup()             # the same element switches as Zhongli's world
    from tier0.harness import runner
    from tier0.content import loader
    rows = []
    for enc in loader.encounter_ids():
        for fs in runner.run_battery(character, "starter", enc, "generic",
                                     fights, seed):
            rows.append({"enc": enc, "won": fs.won, "turns": fs.turns,
                         "dmg": fs.total_damage_dealt})
    return rows


# ----------------------------------------------------------------------
# WHOLE RUNS
# ----------------------------------------------------------------------
def _roll_offers(rng, n: int, forced: str | None, Z):
    from tier0 import constants as C
    by_r = defaultdict(list)
    for cid in Z.POOL:
        by_r[Z.DEFS[cid].rarity].append(cid)
    out = []
    for _ in range(n):
        if forced:
            r = forced
        else:
            x, acc, r = rng.random(), 0.0, "common"
            for rr, p in C.RARITY_ODDS.items():
                acc += p
                if x < acc:
                    r = rr
                    break
        cands = [c for c in by_r[r] if c not in out] or \
            [c for c in Z.POOL if c not in out]
        out.append(rng.choice(cands))
    return out


def _prio(cid: str, deck_ids: list[str], policy: str) -> int:
    if policy == "never" and cid in MORA_ONLY_OR_MORA_READERS:
        return 0
    n = deck_ids.count(cid)
    if (cid in ONE_COPY and n >= 1) or n >= 2:
        return 0
    if cid == "zl_pillar_of_contracts":
        contracts = sum(1 for c in deck_ids if c.startswith("zl_contract"))
        return 5 if contracts >= 2 else 1
    return PRIORITY[cid]


def run_zhongli(seed: int, policy: str, pay_mode: str = "gold_first",
                n_acts: int | None = None) -> dict:
    Z = _setup(pay_mode)
    from tier0 import constants as C
    from tier0.engine.combat import run_fight
    from tier0.harness import metrics as t0_metrics
    from tier05 import acts, maps, model, route

    class ZCtx(model._RunCtx):
        pass

    rng = random.Random(seed)
    res = model.RunResult(seed=seed, won=False, death_node=None,
                          hp_by_node=[], deck_ids=list(Z.STARTER),
                          node_kinds=[], n_acts=n_acts or acts.n_acts(),
                          route="hunter")
    ctx = ZCtx(character="zhongli", archetype="tab", policy=None, rng=rng,
               policy_rng=random.Random(seed + 6 * 10 ** 9),
               pilot=Z.make_pilot(policy), banner=frozenset(),
               route_policy=route.POLICIES["hunter"], res=res,
               deck_ids=res.deck_ids, hp=Z.HP, max_hp=Z.HP,
               gold=C.GOLD_START, n=n_acts or acts.n_acts(), seed_ids=set())
    invoices: dict[str, int] = {}
    fights: list[dict] = []
    shops: list[dict] = []
    income_by_act = Counter()
    inv_seq = [0]

    def resolve_fight(i, kind):
        enemies = model.build_node_encounter(kind, ctx.rng, ctx.act_draw)
        for e in enemies:
            e.zl_elite = kind == "E"
        player = Z.build_player(ctx.deck_ids, ctx.hp, ctx.max_hp, ctx.gold,
                                ctx.act_i, sum(invoices.values()))
        hp_start = ctx.hp
        state = run_fight(player, enemies, ctx.pilot,
                          seed=ctx.rng.randrange(2 ** 31))
        zl = Z.close_fight(state)
        fs = t0_metrics.extract(state, hp_start)
        ctx.res.fight_stats.append(fs)
        ctx.fights += 1
        ctx.hp = state.player.hp
        ctx.max_hp = state.player.max_hp
        won = state.player.alive and not state.living_enemies
        row = _fight_row(Z, state, zl, fs, kind, kind, _count_crystallize(state))
        row.update(act=ctx.act_i, kind=kind, gold_before=zl.gold_start,
                   invoice=0, income=0)
        ctx.gold = zl.gold
        if won:
            inc = C.GOLD_INCOME.get(kind, 0)
            ctx.gold += inc
            income_by_act[ctx.act_i] += inc
            row["income"] = inc
            pay = min(ctx.gold, zl.tab)
            ctx.gold -= pay
            short = zl.tab - pay
            if short > 0:
                inv_seq[0] += 1
                iid = f"{Z.INVOICE_ID}#{inv_seq[0]}"
                invoices[iid] = short
                ctx.deck_ids.append(iid)
                row["invoice"] = short
        fights.append(row)
        ctx.res.gold = ctx.gold
        ctx.res.hp_by_node.append(max(0, ctx.hp))
        if not won:
            if state.stalled:
                ctx.res.stall_node = i
            ctx.exit_dead(i)
            return True
        final_act = ctx.act_i == ctx.n - 1
        if kind == "B":
            ctx.res.acts_completed += 1
        if kind != "B" or not final_act:
            forced = "rare" if kind == "B" else None
            offers = _roll_offers(ctx.rng, 3, forced, Z)
            best = max(offers, key=lambda c: _prio(c, ctx.deck_ids, policy))
            if _prio(best, ctx.deck_ids, policy) >= 3:
                ctx.deck_ids.append(best)
        if kind == "B" and not final_act:
            ctx.hp = ctx.max_hp
        return False

    def resolve_shop():
        visit = {"act": ctx.act_i, "gold_in": ctx.gold, "invoices_paid": 0,
                 "invoice_gold": 0, "removal": 0, "card": 0,
                 "invoices_open_after": 0}
        for iid in sorted(invoices, key=lambda k: int(k.split("#")[1])):
            amt = invoices[iid]
            if ctx.gold >= amt:
                ctx.gold -= amt
                del invoices[iid]
                ctx.deck_ids.remove(iid)
                visit["invoices_paid"] += 1
                visit["invoice_gold"] += amt
        price = C.SHOP_REMOVAL_PRICE + C.SHOP_REMOVAL_PRICE_STEP * ctx.removal_uses
        target = next((c for c in ("strike", "defend")
                       if c in ctx.deck_ids), None)
        if target and ctx.gold >= price:
            ctx.gold -= price
            ctx.deck_ids.remove(target)
            ctx.removal_uses += 1
            visit["removal"] = price
        offers = _roll_offers(ctx.rng, C.SHOP_CARD_OFFERS, None, Z)
        best = max(offers, key=lambda c: _prio(c, ctx.deck_ids, policy))
        if _prio(best, ctx.deck_ids, policy) >= 6 and \
                ctx.gold >= C.SHOP_CARD_PRICE:
            ctx.gold -= C.SHOP_CARD_PRICE
            ctx.deck_ids.append(best)
            visit["card"] = C.SHOP_CARD_PRICE
        visit["invoices_open_after"] = len(invoices)
        shops.append(visit)
        ctx.res.gold = ctx.gold
        ctx.res.hp_by_node.append(ctx.hp)

    def resolve_rest(i, room):
        nxt = ctx.act_map.successors(room)
        pre = bool(nxt) and all(r.kind in ("E", "B") for r in nxt)
        heal = (ctx.hp < C.REST_SMITH_DANGER * ctx.max_hp
                or (pre and ctx.hp < C.REST_PREFIGHT_HEAL_THRESHOLD * ctx.max_hp)
                or ctx.hp < C.REST_HEAL_THRESHOLD * ctx.max_hp
                or "strike" not in ctx.deck_ids)
        if heal:
            ctx.hp = min(ctx.max_hp,
                         ctx.hp + int(C.REST_HEAL_FRACTION * ctx.max_hp))
        else:
            ctx.deck_ids.remove("strike")
        ctx.res.hp_by_node.append(ctx.hp)

    for act_i in range(ctx.n):
        if not ctx.begin_act(act_i):
            continue
        room = ctx.pick(ctx.act_map.rooms_on(0))
        dead = False
        while True:
            i = len(res.node_kinds)
            kind = room.kind
            if kind == maps.UNKNOWN:
                kind = maps.resolve_unknown(ctx.rng, ctx.unknown_weights)
            res.node_kinds.append(kind)
            ctx.elites_taken += kind == "E"
            ctx.rests_taken += kind == "R"
            if kind == "T":
                ctx.gold += C.TREASURE_GOLD
                income_by_act[act_i] += C.TREASURE_GOLD
                res.hp_by_node.append(ctx.hp)
            elif kind == "$":
                resolve_shop()
            elif kind == "R":
                resolve_rest(i, room)
            elif kind == "event":
                res.hp_by_node.append(ctx.hp)     # events not modelled
            else:
                if resolve_fight(i, kind):
                    dead = True
                    break
            ctx.mark_hindsight()
            succ = ctx.act_map.successors(room)
            if not succ:
                break
            room = ctx.pick(succ)
        if dead:
            break
    else:
        ctx.finish()
    return {"seed": seed, "policy": policy, "pay_mode": pay_mode,
            "won": res.won, "floors": len(res.node_kinds),
            "acts_completed": res.acts_completed, "fights": fights,
            "shops": shops, "income_by_act": dict(income_by_act),
            "gold_end": ctx.gold, "deck": list(ctx.deck_ids),
            "invoices_open": dict(invoices)}


def _run_zhongli_chunk(args):
    lo, hi, seed, policy, pay_mode = args
    return [run_zhongli(seed + i, policy, pay_mode) for i in range(lo, hi)]


def zhongli_runs(policy: str, runs: int, seed: int, pay_mode: str,
                 jobs: int) -> list[dict]:
    import os
    workers = min(os.cpu_count() or 1, runs) if jobs == 0 else max(1, jobs)
    if workers <= 1:
        return _run_zhongli_chunk((0, runs, seed, policy, pay_mode))
    edges = [runs * k // workers for k in range(workers + 1)]
    chunks = [(lo, hi, seed, policy, pay_mode)
              for lo, hi in zip(edges, edges[1:]) if lo < hi]
    with ProcessPoolExecutor(max_workers=len(chunks)) as pool:
        return [r for block in pool.map(_run_zhongli_chunk, chunks)
                for r in block]


def _comparator_chunk(args):
    character, plan, pilot, seed, lo, hi = args
    _setup()             # the same element switches as Zhongli's world
    from tier05 import draft, model
    res = model._run_range(character, plan, pilot, draft.POLICIES["assigned"],
                           seed, lo, hi, "standard", None, False, False, None,
                           "hunter")
    return [{"won": r.won, "floors": len(r.node_kinds),
             "acts_completed": r.acts_completed} for r in res]


def comparator_runs(character: str, runs: int, seed: int, jobs: int):
    """`model.run_many`'s runs (bare loadout, assigned drafter, hunter route),
    chunked here only so every worker runs with the element switches ON."""
    import os
    from tier05.runner import resolve_plan
    plan, pilot = resolve_plan(character, None)
    workers = min(os.cpu_count() or 1, runs) if jobs == 0 else max(1, jobs)
    edges = [runs * k // workers for k in range(workers + 1)]
    chunks = [(character, plan, pilot, seed, lo, hi)
              for lo, hi in zip(edges, edges[1:]) if lo < hi]
    if len(chunks) <= 1:
        return _comparator_chunk(chunks[0])
    with ProcessPoolExecutor(max_workers=len(chunks)) as pool:
        return [r for block in pool.map(_comparator_chunk, chunks)
                for r in block]


# ----------------------------------------------------------------------
# statistics helpers
# ----------------------------------------------------------------------
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def ms(xs) -> str:
    xs = [x for x in xs if x is not None]
    if not xs:
        return "n=0"
    m = statistics.fmean(xs)
    sd = statistics.pstdev(xs) if len(xs) > 1 else 0.0
    return f"{m:.2f} (sd {sd:.2f}, n={len(xs)})"


def pct(xs) -> str:
    xs = sorted(xs)
    if not xs:
        return "-"
    q = lambda f: xs[min(len(xs) - 1, int(f * len(xs)))]
    return f"p10 {q(.1)} / p50 {q(.5)} / p90 {q(.9)}"


def spearman(xs, ys) -> float:
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    if len(xs) < 3:
        return float("nan")
    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx)
                    * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def main(argv=None) -> int:
    from tier05 import expcli
    expcli.help_if_asked(__doc__, argv)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--fights", type=int, default=200)
    ap.add_argument("--runs", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260929)
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--out", default=None,
                    help="write the raw result dict as JSON here")
    args = ap.parse_args(argv)
    import json
    t0 = time.perf_counter()
    out = {"battery": {}, "comparator_battery": {}, "runs": {},
           "comparator_runs": {}, "stall": {}, "partner": {}}
    for deck in DECKS:
        for pol in POLICIES:
            out["battery"][f"{deck}|{pol}|99|gold_first"] = zhongli_battery(
                deck, pol, args.fights, args.seed)
        out["battery"][f"{deck}|always|0|gold_first"] = zhongli_battery(
            deck, "always", args.fights, args.seed, gold=0)
        out["battery"][f"{deck}|always|99|tab_first"] = zhongli_battery(
            deck, "always", args.fights, args.seed, pay_mode="tab_first")
    for deck in DECKS:
        out["stall"][deck] = zhongli_battery(deck, "always", args.fights,
                                             args.seed, stall=5)
        out["partner"][deck] = zhongli_battery(deck, "always", args.fights,
                                               args.seed, partner=True)
    for ch in COMPARATORS:
        out["comparator_battery"][ch] = comparator_battery(ch, args.fights,
                                                           args.seed)
    print(f"battery done {time.perf_counter() - t0:.0f}s", file=sys.stderr)
    for pol in POLICIES:
        for pm in PAY_MODES:
            out["runs"][f"{pol}|{pm}"] = zhongli_runs(pol, args.runs,
                                                      args.seed, pm, args.jobs)
            print(f"runs {pol}|{pm} {time.perf_counter() - t0:.0f}s",
                  file=sys.stderr)
    for ch in COMPARATORS:
        out["comparator_runs"][ch] = comparator_runs(ch, args.runs,
                                                     args.seed, args.jobs)
        print(f"comparator {ch} {time.perf_counter() - t0:.0f}s",
              file=sys.stderr)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, default=str)
    print(f"done in {time.perf_counter() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
