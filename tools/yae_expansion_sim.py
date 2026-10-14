#!/usr/bin/env python3
"""YAE MIKO, CARD STAGE BATCH ONE -- the paper's smoke harness (Prototype
stage exploration; nothing here is a balance claim).

    .venv/Scripts/python.exe -m tools.yae_expansion_sim --seeds 200 --seed 7 --jobs 8 --json out.json
    .venv/Scripts/python.exe -m tools.yae_expansion_sim --report out.json
    .venv/Scripts/python.exe -m tools.yae_expansion_sim --scaling count ...   # pick 1 (b)
    .venv/Scripts/python.exe -m tools.yae_expansion_sim --starter --seeds 300   # the starter alone

Reads her surface rows (`docs/prototype-surface.yaml`, `proto_ym_`) and
the rules twin (`tier0/engine/yae_shrine.py`). Three readings, all smoke:

  STARTER -- the ten-card starter and Meditations of a Yako against every
  act-1 normal encounter at full HP: damage a turn, turns to kill, HP lost.

  RUN -- the stylised act the Varka sims used (`tools/varka_expansion_sim`):
  the tier-0.5 act-1 pools, floors N N N N E R N N E R B, then a rest and
  an act-2 boss. A card reward of three after every non-boss-2 fight
  (C/U/R 60/37/3 after a normal fight, 50/40/10 after an elite or the boss).
  A rest heals 30% OR Publishes (the relic): the pilot Publishes when HP is
  at least half and a Sakura Seal or Footnote draft waits, else rests.
  Encounters, HP rolls and offers come from pilot-independent streams.

  SCALING -- per turn of every run fight: Sakura standing, their Levels,
  the strikes' damage. This is the paper's "how do the Sakura scale over a
  fight" reading, on the drafted decks the pilots build.

DRAFTERS -- the default (`tier05.draft.score_offer` on a view of each row with
its `yae` ops swapped for stock ops at a nominal board, `_draft_view`) and
three forced decks (paper sec.5): shrine, publishing, mischief. A forced
drafter scores a card of its deck 10 (Powers and Rares cap 1, else 2), a
support card 7 (cap 2), the rest the default's score.

THE PLAY PILOT is the stock `generic` pilot with Powers played first when
affordable (the Varka harness's rule) and one INSTRUMENT SURFACE: the `yae`
op, which the stock scorer cannot see, is valued as its nearest stock op
(`_translate`) so it plays it. Nothing in the engine's resolution moves.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
import traceback
from collections import Counter, defaultdict

TEMPLATE = ["N", "N", "N", "N", "E", "R", "N", "N", "E", "R", "B"]
RARITY = {"N": (60, 37, 3), "E": (50, 40, 10), "B": (50, 40, 10)}
P = "proto_ym_"
MAX_HP = 72

SHRINE = ["twin_sakura", "thunder_rite", "shrine_offering",
          "shrine_maidens_guard", "sakura_grove", "kitsune_rite",
          "thunderbolt_tithe", "rooted_shrine", "tenko_kenshin",
          "foxs_mooncall", "yakan_offering", "sakura_channeling"]
PUBLISHING = ["kitsune_flash", "deadline", "fox_fire_draft", "bestseller",
              "print_run", "footnote", "sakura_seal", "serialization",
              "manuscript_pile", "the_seven_glamours",
              "reborn_as_guuji_yae", "editor_in_chief"]
MISCHIEF = ["sly_strike", "fox_trick", "kitsune_guile", "foxfire_lure",
            "mischievous_teasing", "manuscript_pile"]


def _deck(core, support=()):
    return {"core": [P + c for c in core], "support": [P + c for c in support]}


DECKS = {
    "shrine": _deck(SHRINE, ["sakura_seal", "foxfire_lure", "edict_of_cleansing"]),
    "publishing": _deck(PUBLISHING, ["twin_sakura", "shrine_offering"]),
    "mischief": _deck(MISCHIEF, ["kitsune_flash", "sly_strike",
                                 "thunder_rite", "shrine_offering"]),
}
PILOTS = ("default",) + tuple(DECKS)


# --- the process switch and the scorer surface --------------------------------

_ENABLED = False
SCALING = "level"
#: `--knob name=value,...`: numbers only, for a paired reading of one rule
#: or one starter number. Module constants of `yae_shrine`, and two starter
#: riders patched onto the staged rows in this process only.
KNOBS = {"base": "SAKURA_BASE", "turns": "SAKURA_TURNS",
         "plant_level": "PLANT_LEVEL",
         "proofread_block": None, "yakan_block": None}


def parse_knobs(text):
    out = {}
    for part in (text or "").split(","):
        if not part.strip():
            continue
        k, v = part.split("=")
        if k.strip() not in KNOBS:
            raise SystemExit(f"unknown knob {k!r}; knobs: {sorted(KNOBS)}")
        out[k.strip()] = int(v)
    return out


def enable(scaling=None, knobs=None):
    global _ENABLED
    from tier0.engine import yae_shrine as Y
    from tier0.content import loader
    if scaling is not None:
        Y.SCALING = scaling
    for k, v in (knobs or {}).items():
        if KNOBS[k]:
            setattr(Y, KNOBS[k], v)
    if knobs and (knobs.get("proofread_block") or knobs.get("yakan_block")):
        loader.reset_arm_caches()
        idx = loader._prototype_index()
        if knobs.get("proofread_block"):
            row = idx[P + "proofread"]
            row.effects = [{"op": "block", "amount": knobs["proofread_block"]}
                           ] + [fx for fx in row.effects
                                if fx.get("op") != "block"]
        if knobs.get("yakan_block"):
            row = idx[P + "yakan_evocation"]
            row.effects = [fx for fx in row.effects
                           if fx.get("op") != "block"] + [
                {"op": "block", "amount": knobs["yakan_block"]}]
        loader._card_prototype.cache_clear()
    if _ENABLED:
        return
    loader.reset_arm_caches()
    from tier0.pilot import policy
    orig = policy._active_effects

    def active(state, effect_list, card=None):
        for fx in orig(state, effect_list, card):
            yield from _translate(state, fx, card)

    policy._active_effects = active
    _ENABLED = True


def _translate(state, fx, card=None):
    """A `yae` clause as its nearest stock op, for the stock scorer only."""
    if fx.get("op") != "yae":
        yield fx
        return
    from tier0.engine import yae_shrine as Y
    led = Y.ledger(state.player)
    if led is None:
        return
    kind = fx.get("kind")
    n_sak = len(led.sakura)
    base, per, amt = fx.get("base", 0), fx.get("per", 0), fx.get("amount", 0)
    if kind == "plant":
        # A plant is three strikes to come (more when it levels the shrine);
        # priced as a hit at a random enemy so a plant competes with a Strike.
        value = 0
        standing = n_sak
        for _ in range(amt):
            value += 2 * min(standing, Y.SAKURA_CAP) + (
                6 if standing < Y.SAKURA_CAP else 0)
            standing += 1
        yield {"op": "damage", "amount": value, "target": "random_enemy"}
    elif kind == "tenko":
        if n_sak:
            now = sum(Y.strike_damage(state, s, None) for s in led.sakura)
            kept = sum(2 for s in led.sakura if s.turns_left <= 1)
            yield {"op": "damage", "amount": now + kept,
                   "target": "random_enemy"}
    elif kind == "extend":
        if n_sak:
            yield {"op": "block", "amount": 2 * n_sak * amt}
    elif kind == "level_up":
        if n_sak:
            yield {"op": "damage", "amount": 2 * n_sak * amt,
                   "target": "random_enemy"}
    elif kind == "edit":
        value = {Y.RED_INK: 3, Y.FOOTNOTE: 3, Y.DEADLINE: 1, Y.FOX_FIRE: 4,
                 Y.SAKURA_SEAL: 6}[fx["annotation"]]
        others = len([c for c in state.player.hand if c is not card])
        if others:
            yield {"op": "damage", "amount": value * min(amt, others),
                   "target": "random_enemy"}
    elif kind == "edit_all":
        others = len([c for c in state.player.hand if c is not card])
        if others:
            yield {"op": "damage", "amount": 4 * others,
                   "target": "random_enemy"}
    elif kind == "publish":
        if any(Y.is_annotated(c) for c in state.player.hand if c is not card):
            yield {"op": "damage", "amount": 3, "target": "random_enemy"}
    elif kind == "lure":
        if n_sak:
            yield {"op": "damage", "amount": 2, "target": "enemy"}
    elif kind == "damage_per_sakura":
        yield {"op": "damage", "amount": base + per * n_sak, "target": "enemy"}
    elif kind == "block_per_sakura":
        yield {"op": "block", "amount": base + per * n_sak}
    elif kind == "damage_per_annotated":
        yield {"op": "damage", "amount": base + per * Y.annotated_in_hand(state),
               "target": "enemy"}
    elif kind == "block_per_annotated":
        yield {"op": "block", "amount": base + per * Y.annotated_in_hand(state)}
    elif kind == "annotated_strike":
        more = amt if (card is not None and Y.is_annotated(card)) else 0
        yield {"op": "damage", "amount": base + more, "target": "enemy"}
    elif kind == "fox_fire":
        yield {"op": "damage", "amount": Y.FOX_FIRE_DAMAGE,
               "target": "random_enemy"}


def make_pilot():
    """The stock `generic` pilot, Powers first when affordable."""
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot.policy import make_pilot as stock
    base = stock(loader.pilot_weights("generic"))

    def pilot(state):
        p = state.player
        powers = [c for c in p.hand if c.type == "power"
                  and c.id.startswith(P)
                  and combat.card_playable(state, c)
                  and combat.card_cost(state, c) <= p.energy]
        if powers:
            return max(powers, key=lambda c: combat.card_cost(state, c))
        return base(state)

    return pilot


# --- pool and drafting -----------------------------------------------------------

def pool():
    from tier0.content import loader
    out = {"common": [], "uncommon": [], "rare": []}
    for c in loader._prototype_index().values():
        if c.id.startswith(P) and c.rarity in out:
            out[c.rarity].append(c.id)
    return out


def _offer(rng, kind, pl):
    w = RARITY[kind]
    out = []
    while len(out) < 3:
        r = rng.choices(("common", "uncommon", "rare"), weights=w)[0]
        c = rng.choice(pl[r])
        if c not in out:
            out.append(c)
    return out


#: The `yae` kinds as stock ops FOR THE DRAFTER ONLY, at a nominal board
#: (two Sakura standing, two Annotated cards in hand).
def _draft_ops(fx):
    kind = fx.get("kind")
    base, per, amt = fx.get("base", 0), fx.get("per", 0), fx.get("amount", 0)
    if kind == "plant":
        return [{"op": "damage", "amount": 6 * amt, "target": "random_enemy"}]
    if kind == "tenko":
        return [{"op": "damage", "amount": 7, "target": "random_enemy"}]
    if kind == "extend":
        return [{"op": "block", "amount": 3 * amt}]
    if kind == "level_up":
        return [{"op": "damage", "amount": 4 * amt, "target": "random_enemy"}]
    if kind == "edit":
        return [{"op": "damage", "amount": 3 * amt, "target": "random_enemy"}]
    if kind == "edit_all":
        return [{"op": "damage", "amount": 8, "target": "random_enemy"}]
    if kind == "publish":
        return [{"op": "damage", "amount": 3, "target": "random_enemy"}]
    if kind == "lure":
        return [{"op": "damage", "amount": 2, "target": "enemy"}]
    if kind == "damage_per_sakura":
        return [{"op": "damage", "amount": base + 2 * per, "target": "enemy"}]
    if kind == "block_per_sakura":
        return [{"op": "block", "amount": base + 2 * per}]
    if kind == "damage_per_annotated":
        return [{"op": "damage", "amount": base + 2 * per, "target": "enemy"}]
    if kind == "block_per_annotated":
        return [{"op": "block", "amount": base + 2 * per}]
    if kind == "annotated_strike":
        return [{"op": "damage", "amount": base + amt // 2, "target": "enemy"}]
    # The design axes (2026-10-14), at the same nominal board.
    if kind == "rite":
        return [{"op": "block", "amount": 3}]
    if kind == "edit_sakura":
        return [{"op": "damage", "amount": 3 * min(amt, 2), "target": "random_enemy"}]
    if kind == "plant_level":
        return [{"op": "damage", "amount": 6 + 2 * amt, "target": "random_enemy"}]
    if kind == "strike_if_weak":
        return [{"op": "damage", "amount": 2, "target": "enemy"}]
    return None


def _draft_view(card):
    if not any(fx.get("op") == "yae" for fx in card.effects):
        return card
    import copy
    view = copy.copy(card)
    effects = []
    for fx in card.effects:
        ops = _draft_ops(fx) if fx.get("op") == "yae" else None
        effects.extend(ops if ops else [fx])
    view.effects = effects
    return view


_NOMINAL: dict = {}


def _nominal():
    """Rows the default scores under the skip line against the starter get
    the median of the rest (the Varka harness's fix), once per process."""
    if not _NOMINAL:
        from tier0 import constants as C
        from tier0.content import loader
        from tier0.engine import yae_shrine as Y
        from tier05 import draft
        starter = [loader.get_card(c) for c in Y.starter_ids()]
        ids = [c for r in pool().values() for c in r]
        sc = {c: draft.score_offer(_draft_view(loader.get_card(c)), starter,
                                   "generic") for c in ids}
        priced = sorted(v for v in sc.values()
                        if v >= C.DRAFT_SKIP_THRESHOLD)
        med = st.median(priced) if priced else 1.0
        _NOMINAL["x"] = (med, frozenset(
            c for c, v in sc.items() if v < C.DRAFT_SKIP_THRESHOLD))
    return _NOMINAL["x"]


def _default(card, deck_cards):
    from tier05 import draft
    med, low = _nominal()
    if card.id in low:
        return med
    return draft.score_offer(_draft_view(card), deck_cards, "generic")


def _score(card, deck, deck_cards, pilot):
    from tier0 import constants as C
    floor = C.DRAFT_SKIP_THRESHOLD
    if pilot == "default":
        return _default(card, deck_cards), floor
    d = DECKS[pilot]
    if card.id in d["core"]:
        cap = 1 if (card.type == "power" or card.rarity == "rare") else 2
        if deck.count(card.id) < cap:
            return 10.0, floor
    elif card.id in d["support"]:
        if deck.count(card.id) < 2:
            return 7.0, floor
    return _default(card, deck_cards), floor


def _draft(offer, deck, pilot):
    from tier0.content import loader
    from tier0.engine import yae_shrine as Y
    deck_cards = [loader.get_card(c) for c in Y.starter_ids() + deck]
    best, best_s, floor = None, float("-inf"), 0.0
    for cid in offer:
        s, floor = _score(loader.get_card(cid), deck, deck_cards, pilot)
        if s > best_s:
            best, best_s = cid, s
    return best if best_s >= floor else None


# --- one fight, one run ----------------------------------------------------------

def fight(deck, enemies, seed, hp, published=None):
    from tier0.engine import combat, yae_shrine as Y
    for i, e in enumerate(enemies):
        e.name = f"{e.name}#{i}"
    player = Y.build_player(extra=tuple(deck), published=published)
    player.hp = min(hp, player.max_hp)
    start = player.hp
    try:
        s = combat.run_fight(player, enemies, make_pilot(), seed=seed)
    except Exception as exc:                      # noqa: BLE001 -- reported
        return {"won": False, "turns": 0, "hp_lost": start, "hp_end": 0,
                "plays": {}, "stall": False,
                "error": f"{type(exc).__name__}: {exc}",
                "trace": traceback.format_exc(limit=6), "drafts": {},
                "published": {}, "turn_rows": [], "strikes": 0,
                "strike_damage": 0, "edits": 0, "block": 0, "dmg": 0}
    plays = Counter(r["card"] for r in s.log if r.get("event") == "play")
    led = s.player.yae_ledger
    won = bool(s.player.alive) and not s.living_enemies
    block, dmg = _log_reads(s.log)
    pub = {}
    for pile in (s.player.hand, s.player.draw_pile, s.player.discard_pile,
                 s.player.exhaust_pile):
        for c in pile:
            if getattr(c, "ym_published", False) and getattr(
                    c, "ym_annotation", None) and c.ym_slot is not None:
                pub[c.ym_slot] = c.ym_annotation
    return {"won": won, "turns": s.turn,
            "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp), "plays": dict(plays),
            "stall": s.player.alive and bool(s.living_enemies),
            "error": None, "block": block, "dmg": dmg,
            "strikes": led.strikes, "strike_damage": led.strike_damage,
            "edits": led.edits, "drafts": dict(led.drafts),
            "published": pub, "turn_rows": _turn_rows(s.log),
            "enemies": len(enemies)}


def _log_reads(log):
    block = 0
    dmg = 0.0
    for r in log:
        ev = r.get("event")
        if ev == "block":
            block += r.get("amount", 0)
        elif ev == "damage" and r.get("target") != "player":
            dmg += float(r.get("amount", 0)) + float(r.get("blocked", 0) or 0)
    return block, dmg


def _turn_rows(log):
    """Per turn: (Sakura standing after the plants, mean Level, strike
    damage this turn, all damage this turn)."""
    rows = defaultdict(lambda: {"count": 0, "levels": [], "strike": 0,
                                "dmg": 0.0})
    for r in log:
        t = r.get("turn", 0)
        ev = r.get("event")
        if ev in ("yae_plant", "yae_level"):
            rows[t]["count"] = len(r["levels"])
            rows[t]["levels"] = list(r["levels"])
        elif ev == "yae_sakura_strike":
            rows[t]["strike"] += r["amount"]
        elif ev == "damage" and r.get("target") != "player":
            rows[t]["dmg"] += float(r.get("amount", 0)) + float(
                r.get("blocked", 0) or 0)
    out = []
    count, levels = 0, []
    for t in range(1, max(rows) + 1 if rows else 1):
        row = rows.get(t)
        if row and row["levels"]:
            count, levels = row["count"], row["levels"]
        out.append((t, count, st.mean(levels) if levels else 0.0,
                    row["strike"] if row else 0, row["dmg"] if row else 0.0))
    return out


def _publish_at_rest(hp, max_hp, drafts, published):
    """Meditations of a Yako at a rest: Publish a waiting Sakura Seal or
    Footnote draft when HP is at least half, else rest."""
    from tier0.engine import yae_shrine as Y
    good = {s: a for s, a in drafts.items()
            if a in (Y.SAKURA_SEAL, Y.FOOTNOTE) and published.get(s) != a}
    if hp * 2 >= max_hp and good:
        slot = min(good, key=lambda s: Y.PUBLISH_ORDER.index(good[s]))
        published[slot] = good[slot]
        return hp, ("publish", slot, good[slot])
    return min(max_hp, hp + int(0.3 * max_hp)), ("rest", None, None)


def run(seed, pilot):
    from tier05 import acts
    enc_rng = random.Random(seed)
    draw = acts.ActDraw(enc_rng, act=0)
    offer_rng = random.Random(seed + 10 ** 6)
    pl = pool()
    deck: list = []
    hp = MAX_HP
    published: dict = {}
    drafts: dict = {}
    fights, offers, rests = [], [], []
    act1 = False
    for floor, kind in enumerate(TEMPLATE + ["B2"]):
        if kind == "R":
            hp, choice = _publish_at_rest(hp, MAX_HP, drafts, published)
            rests.append(choice)
            continue
        if kind == "B2":
            hp = min(MAX_HP, hp + int(0.3 * MAX_HP))
            spec = enc_rng.choice(acts.boss_pool(1))
        else:
            spec = draw.encounter_for(kind, enc_rng)
        enemies = acts.spawn(spec, enc_rng)
        r = fight(deck, enemies, seed * 100 + floor, hp, published)
        r.update(kind=kind, enc=spec["id"])
        fights.append(r)
        hp = r["hp_end"]
        drafts.update(r["drafts"])
        published.update(r["published"])
        if not r["won"]:
            break
        if kind == "B":
            act1 = True
        if kind in RARITY:
            offer = _offer(offer_rng, kind, pl)
            pick = _draft(offer, deck, pilot)
            offers.append((offer, pick))
            if pick:
                deck.append(pick)
    won = fights[-1]["kind"] == "B2" and fights[-1]["won"]
    return {"seed": seed, "pilot": pilot, "act1": act1, "won": won,
            "fights": fights, "offers": offers, "rests": rests,
            "published": published}


def starter_battery(seed):
    """The starter alone against every act-1 easy and hard encounter."""
    from tier05 import acts
    out = []
    for i, spec in enumerate(acts.pools(0)["easy"] + acts.pools(0)["hard"]):
        erng = random.Random(seed * 1000 + i)
        r = fight([], acts.spawn(spec, erng), seed * 1000 + i, MAX_HP)
        r.update(kind="N", enc=spec["id"])
        out.append(r)
    return {"seed": seed, "pilot": "starter", "fights": out}


def _slim(r):
    for f in r["fights"]:
        f.pop("drafts", None)
    return r


def _w(args):
    seed, pilot, scaling, knobs = args
    enable(scaling, knobs)
    return _slim(run(seed, pilot))


def _ws(args):
    seed, scaling, knobs = args
    enable(scaling, knobs)
    return _slim(starter_battery(seed))


def pmap(fn, jobs, argl, scaling, knobs=None):
    if jobs <= 1:
        enable(scaling, knobs)
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs, initializer=enable,
                                      initargs=(scaling, knobs)) as p:
        return p.map(fn, argl, chunksize=4)


# --- report ------------------------------------------------------------------------

def ci(k, n):
    if not n:
        return 0.0
    p = k / n
    return 196.0 * (p * (1 - p) / n) ** 0.5


def pc(k, n):
    return f"{100.0 * k / n:.1f} ±{ci(k, n):.1f}" if n else "-"


def _mean(xs):
    return st.mean(xs) if xs else 0.0


def report(data, out=print):
    out(f"# Yae card stage smoke -- scaling `{data['scaling']}`, knobs "
        f"{data.get('knobs') or '{}'}, pool "
        f"{data['pool_size']} ({data['pool_counts']}), {data['seeds']} seeds "
        f"from {data['seed']}. SMOKE CHECKS, NOT BALANCE CLAIMS.")
    if data.get("starter"):
        fs = [f for r in data["starter"] for f in r["fights"]]
        won = [f for f in fs if f["won"]]
        out("\n## The starter alone, act-1 normal encounters, full HP")
        out(f"- fights {len(fs)}, won {pc(len(won), len(fs))}, errors "
            f"{sum(1 for f in fs if f['error'])}")
        if won:
            out(f"- turns to kill {_mean([f['turns'] for f in won]):.1f}, "
                f"damage a turn {_mean([f['dmg'] / max(1, f['turns']) for f in won]):.1f}, "
                f"of it Sakura {_mean([f['strike_damage'] / max(1, f['turns']) for f in won]):.1f}, "
                f"HP lost {_mean([f['hp_lost'] for f in won]):.1f}, "
                f"Block a turn {_mean([f['block'] / max(1, f['turns']) for f in won]):.1f}")
    runs = data.get("runs") or []
    if not runs:
        return
    by = defaultdict(list)
    for r in runs:
        by[r["pilot"]].append(r)
    present = [p for p in PILOTS if by[p]]
    out("\n## The stylised run (paired seeds)")
    out("| pilot | n | act 1 | run | floors | dmg/turn | Sakura dmg/turn | "
        "strikes/fight | edits/fight | published/run | errors |")
    out("|---|---|---|---|---|---|---|---|---|---|---|")
    for pilot in present:
        rs = by[pilot]
        fs = [f for r in rs for f in r["fights"]]
        n = len(rs)
        out(f"| {pilot} | {n} | {pc(sum(r['act1'] for r in rs), n)} | "
            f"{pc(sum(r['won'] for r in rs), n)} | "
            f"{_mean([len(r['fights']) for r in rs]):.1f} | "
            f"{_mean([f['dmg'] / max(1, f['turns']) for f in fs]):.1f} | "
            f"{_mean([f['strike_damage'] / max(1, f['turns']) for f in fs]):.1f} | "
            f"{_mean([f['strikes'] for f in fs]):.1f} | "
            f"{_mean([f['edits'] for f in fs]):.1f} | "
            f"{_mean([len(r['published']) for r in rs]):.2f} | "
            f"{sum(1 for f in fs if f['error'])} |")
    out("\n## How the Sakura scale over a fight (every run fight, by turn)")
    out("| pilot | turn | fights | Sakura standing | mean Level | "
        "Sakura dmg | all dmg |")
    out("|---|---|---|---|---|---|---|")
    for pilot in present:
        rows = defaultdict(list)
        for r in by[pilot]:
            for f in r["fights"]:
                for t, count, lvl, strike, dmg in f["turn_rows"]:
                    rows[t].append((count, lvl, strike, dmg))
        for t in sorted(rows)[:8]:
            xs = rows[t]
            out(f"| {pilot} | {t} | {len(xs)} | "
                f"{_mean([x[0] for x in xs]):.2f} | "
                f"{_mean([x[1] for x in xs if x[0]]):.2f} | "
                f"{_mean([x[2] for x in xs]):.1f} | "
                f"{_mean([x[3] for x in xs]):.1f} |")
    out("\n## Plays per fight held (the deck's cards, default drafter)")
    held = Counter()
    plays = Counter()
    for r in by.get("default", []):
        picks = [p for _, p in r["offers"] if p]
        for i, f in enumerate(r["fights"]):
            deck = Counter(picks[:i])
            for cid, k in deck.items():
                held[cid] += k
            for cid, k in f["plays"].items():
                if cid.startswith(P):
                    plays[cid] += k
    out("| card | held (fight-copies) | plays per copy-fight |")
    out("|---|---|---|")
    for cid, h in sorted(held.items(), key=lambda kv: -kv[1]):
        out(f"| {cid[len(P):]} | {h} | {plays[cid] / h:.2f} |")
    out("\n## Drafts (default drafter): picks per card")
    picks = Counter(p for r in by.get("default", []) for _, p in r["offers"] if p)
    offered = Counter(c for r in by.get("default", []) for o, _ in r["offers"]
                      for c in o)
    out("| card | offered | taken | take rate |")
    out("|---|---|---|---|")
    for cid, o in sorted(offered.items(), key=lambda kv: -kv[1]):
        out(f"| {cid[len(P):]} | {o} | {picks[cid]} | {picks[cid] / o:.2f} |")
    rests = Counter(c[0] for r in runs for c in r["rests"])
    out(f"\nRest sites: {dict(rests)}; annotations published by slot: "
        f"{Counter(a for r in runs for a in r['published'].values())}")
    errs = [f for r in runs for f in r["fights"] if f["error"]]
    if errs:
        out(f"\nERRORS ({len(errs)}): {errs[0]['error']}\n{errs[0]['trace']}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--pilots", default=",".join(PILOTS))
    ap.add_argument("--scaling", default="level", choices=("level", "count"))
    ap.add_argument("--starter", action="store_true",
                    help="the starter battery only")
    ap.add_argument("--knob", default="", help="name=value,... (KNOBS)")
    ap.add_argument("--json", help="write the raw results here")
    ap.add_argument("--report", help="report a --json file instead of running")
    args = ap.parse_args(argv)
    if args.report:
        with open(args.report, encoding="utf-8") as fh:
            report(json.load(fh))
        return 0
    from understudy.report import console_safe
    console_safe()
    knobs = parse_knobs(args.knob)
    enable(args.scaling, knobs)
    pl = pool()
    data = {"seeds": args.seeds, "seed": args.seed, "scaling": args.scaling,
            "knobs": knobs,
            "pool_size": sum(len(v) for v in pl.values()),
            "pool_counts": {k: len(v) for k, v in pl.items()}}
    seeds = range(args.seed, args.seed + args.seeds)
    data["starter"] = pmap(_ws, args.jobs,
                           [(s, args.scaling, knobs) for s in seeds],
                           args.scaling, knobs)
    if not args.starter:
        pilots = args.pilots.split(",")
        data["runs"] = pmap(_w, args.jobs,
                            [(s, p, args.scaling, knobs) for p in pilots
                             for s in seeds], args.scaling, knobs)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
    report(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
