"""Focused readout for the Center Stage / Guest Cast + Fanfare-spend pass.

Usage:
    python -m tier05.exp_furina_modes suite
    python -m tier05.exp_furina_modes fanfare
    python -m tier05.exp_furina_modes fanfare-core
    python -m tier05.exp_furina_modes fanfare-cards
    python -m tier05.exp_furina_modes fanfare-pilot
    python -m tier05.exp_furina_modes fanfare-spend
    python -m tier05.exp_furina_modes fanfare-followup
    python -m tier05.exp_furina_modes fanfare-draftcards
    python -m tier05.exp_furina_modes fanfare-targets
    python -m tier05.exp_furina_modes fanfare-individual
    python -m tier05.exp_furina_modes draft
    python -m tier05.exp_furina_modes battery
    python -m tier05.exp_furina_modes starter
    python -m tier05.exp_furina_modes nudge
"""

from __future__ import annotations

import collections
import copy
import statistics
import sys

from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.pilot.policy import make_pilot
from tier05 import draft, model

SEED = 11
RUNS = 1500
FIGHTS = 500
ABLATION_FIGHTS = 300
STARTER_RUNS = 1000
CARD_SWEEP_RUNS = 300
ENCOUNTERS = ("punisher", "swarm", "attrition", "tank_boss")


def _generates_guest(card) -> bool:
    return any(fx.get("op") == "generate_guest_star" for fx in card.effects)


def _access(card) -> bool:
    return card.is_companion or _generates_guest(card)


def _machinery(card) -> bool:
    return ("spotlight" in card.archetypes
            and card.role in ("enabler", "payoff")
            and not _access(card))


def draft_readout() -> None:
    results = model.run_many(
        "furina", "spotlight", "spotlight", draft.assigned_policy,
        RUNS, SEED, grant_relics=True, grant_potions=True)
    early_picks = collections.Counter()
    companion_depth = collections.Counter()
    access_runs = machinery_runs = 0
    for result in results:
        picks = [loader.get_card(d["picked"]) for d in result.decisions
                 if d["node"] < 4 and d["picked"]]
        early_picks.update(c.id for c in picks)
        companion_depth[sum(c.is_companion for c in picks)] += 1
        access_runs += any(_access(c) for c in picks)
        machinery_runs += any(_machinery(c) for c in picks)
    online = sum(r.time_to_online is not None and r.time_to_online <= 3
                 for r in results)
    print(f"SPOTLIGHT DRAFT ({RUNS} realistic runs, seed {SEED})")
    print("  companion picks before first elite: "
          + "  ".join(f"{n}={companion_depth[n] / RUNS:.1%}"
                       for n in sorted(companion_depth)))
    print(f"  any extra cast access: {access_runs / RUNS:.1%}")
    print(f"  any machinery: {machinery_runs / RUNS:.1%}")
    print(f"  full core online before first elite: {online / RUNS:.1%}")
    print("  leading early picks: "
          + ", ".join(f"{cid} {n / RUNS:.1%}"
                      for cid, n in early_picks.most_common(12)))


def suite_readout() -> None:
    print(f"FURINA REALISTIC SUITE ({RUNS} runs/plan, seed {SEED})")
    for archetype in ("salon", "spotlight", "fanfare"):
        results = model.run_many(
            "furina", archetype, archetype, draft.assigned_policy,
            RUNS, SEED, grant_relics=True, grant_potions=True)
        wins = sum(r.won for r in results)
        first_elite = sum(r.death_node is None or r.death_node > 4
                          for r in results)
        second_elite = sum(r.death_node is None or r.death_node > 8
                           for r in results)
        online = sum(r.time_to_online is not None and r.time_to_online <= 3
                     for r in results)
        print(f"  {archetype:<10} Act {wins / RUNS:>5.1%}  "
              f"E1 {first_elite / RUNS:>5.1%}  "
              f"E2 {second_elite / RUNS:>5.1%}  "
              f"core@E1 {online / RUNS:>5.1%}")


def fanfare_readout() -> None:
    """Trace realistic Fanfare assembly and combat resource conversion."""
    captures = []
    original_extract = metrics.extract

    def capture(state, hp_start):
        stat = original_extract(state, hp_start)
        gain_events = [e for e in state.log if e["event"] == "gain_fanfare"]
        spend_events = [e for e in state.log
                        if e["event"] == "fanfare_spent"]
        captures.append({
            "won": stat.won,
            "gain": sum(e["amount"] for e in gain_events),
            "spent": sum(e["amount"] for e in spend_events),
            "peak": max((e["total"] for e in gain_events), default=0),
            "end": state.player.fanfare,
            "cap": state.player.fanfare_cap,
            "sources": collections.Counter(
                e["source"] for e in gain_events),
            "plays": collections.Counter(
                e["card"] for e in state.log if e["event"] == "play"),
            "modes": collections.Counter(
                e["mode"] for e in state.log
                if e["event"] == "spotlight_designated"),
        })
        return stat

    metrics.extract = capture
    try:
        results = model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        metrics.extract = original_extract

    early_picks = collections.Counter()
    all_picks = collections.Counter()
    early_depth = collections.Counter()
    for result in results:
        early = [loader.get_card(d["picked"]) for d in result.decisions
                 if d["node"] < 4 and d["picked"]]
        picked = [loader.get_card(d["picked"]) for d in result.decisions
                  if d["picked"]]
        early_picks.update(c.id for c in early)
        all_picks.update(c.id for c in picked)
        early_depth[sum(
            "fanfare" in c.archetypes and c.role in ("enabler", "payoff")
            for c in early)] += 1

    source_totals = sum((c["sources"] for c in captures),
                        collections.Counter())
    play_totals = sum((c["plays"] for c in captures), collections.Counter())
    mode_totals = sum((c["modes"] for c in captures), collections.Counter())
    fanfare_ids = {
        c.id for c in loader._card_index().values()
        if "fanfare" in c.archetypes
    }
    fanfare_plays = [(cid, n) for cid, n in play_totals.most_common()
                     if cid in fanfare_ids]
    deaths = collections.Counter(
        r.death_node for r in results if r.death_node is not None)
    online = sum(r.time_to_online is not None and r.time_to_online <= 3
                 for r in results)

    print(f"FANFARE TRACE ({RUNS} realistic runs, seed {SEED})")
    print(f"  Act clears: {sum(r.won for r in results) / RUNS:.1%}; "
          f"core online by E1: {online / RUNS:.1%}")
    print("  Fanfare core pieces drafted before E1: "
          + "  ".join(f"{n}={early_depth[n] / RUNS:.1%}"
                       for n in sorted(early_depth)))
    print("  leading early picks: "
          + ", ".join(f"{cid} {n / RUNS:.1%}"
                      for cid, n in early_picks.most_common(12)))
    print("  death nodes: "
          + ", ".join(f"{node}={n / RUNS:.1%}"
                      for node, n in sorted(deaths.items())))
    print(f"  reached fights: {len(captures)}; fight wins "
          f"{sum(c['won'] for c in captures) / len(captures):.1%}")
    print("  per reached fight: "
          f"Fanfare +{statistics.mean(c['gain'] for c in captures):.1f} "
          f"/-{statistics.mean(c['spent'] for c in captures):.1f}, "
          f"peak {statistics.mean(c['peak'] for c in captures):.1f}, "
          f"end {statistics.mean(c['end'] for c in captures):.1f}")
    print("  threshold reach: "
          + "  ".join(
              f"{n}={sum(c['peak'] >= n for c in captures) / len(captures):.1%}"
              for n in (10, 15, 20, 30)))
    print("  gain sources: "
          + ", ".join(f"{source} {n / len(captures):.1f}/fight"
                      for source, n in source_totals.most_common()))
    print("  Spotlight designations: "
          + ", ".join(f"{mode} {n / len(captures):.2f}/fight"
                      for mode, n in mode_totals.most_common()))
    print("  Fanfare card plays: "
          + ", ".join(f"{cid} {n / len(captures):.2f}/fight"
                      for cid, n in fanfare_plays[:16]))
    print("  leading all-run draft picks: "
          + ", ".join(f"{cid} {n / RUNS:.1%}"
                      for cid, n in all_picks.most_common(16)))


def _fanfare_core_arm(rule: str):
    original_complete = draft.core_complete
    original_progress = draft._core_progress

    def pieces(deck):
        return [c for c in deck if "fanfare" in c.archetypes
                and c.role in ("enabler", "payoff")]

    def complete(deck, archetype):
        if archetype != "fanfare":
            return original_complete(deck, archetype)
        if rule == "generic4":
            return len(pieces(deck)) >= 4
        if rule == "two-piece":
            return len(pieces(deck)) >= 2
        if rule == "one-payoff":
            return any(c.role == "payoff" for c in pieces(deck))
        if rule == "native-online":
            return True
        raise ValueError(rule)

    def progress(deck, archetype):
        if archetype != "fanfare":
            return original_progress(deck, archetype)
        if rule == "generic4":
            return min(1.0, len(pieces(deck)) / 4)
        if rule == "two-piece":
            return min(1.0, len(pieces(deck)) / 2)
        if rule == "one-payoff":
            return float(any(c.role == "payoff" for c in pieces(deck)))
        if rule == "native-online":
            return 1.0
        raise ValueError(rule)

    draft.core_complete = complete
    draft._core_progress = progress
    try:
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        draft.core_complete = original_complete
        draft._core_progress = original_progress


def fanfare_core_readout() -> None:
    print(f"FANFARE CORE SWEEP ({STARTER_RUNS} realistic runs/arm, "
          "same seeds)")
    for label, rule in (
            ("generic four-piece", "generic4"),
            ("Aria + any one piece", "two-piece"),
            ("first payoff completes", "one-payoff"),
            ("native resource online", "native-online")):
        _starter_result(label, _fanfare_core_arm(rule))


def _fanfare_seeded_arm(card_id: str | None):
    spec = loader._character_index()["furina"]
    original = list(spec["starting_deck"])
    try:
        if card_id is not None:
            spec["starting_deck"] = original + [card_id]
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            CARD_SWEEP_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        spec["starting_deck"] = original


def _run_rates(results) -> tuple[float, float, float]:
    n = len(results)
    return (
        sum(r.won for r in results) / n,
        sum(r.death_node is None or r.death_node > 4 for r in results) / n,
        sum(r.death_node is None or r.death_node > 8 for r in results) / n,
    )


def fanfare_cards_readout() -> None:
    baseline = _run_rates(_fanfare_seeded_arm(None))
    candidates = [
        c for c in loader._card_index().values()
        if "fanfare" in c.archetypes
        and c.rarity in ("common", "uncommon", "rare")
        and not c.kit_card
    ]
    rows = []
    for card in sorted(candidates, key=lambda c: (c.rarity, c.id)):
        rates = _run_rates(_fanfare_seeded_arm(card.id))
        rows.append((rates[0] - baseline[0], rates[1] - baseline[1],
                     card.rarity, card.id, rates))
    print(f"FANFARE SINGLE-CARD SEED SWEEP ({CARD_SWEEP_RUNS} realistic "
          "runs/arm; one extra card, same seeds)")
    print(f"  baseline Act {baseline[0]:.1%}  E1 {baseline[1]:.1%}  "
          f"E2 {baseline[2]:.1%}")
    for act_delta, e1_delta, rarity, cid, rates in sorted(
            rows, reverse=True):
        print(f"  {cid:<25} {rarity:<8} "
              f"Act {rates[0]:>5.1%} ({act_delta * 100:+5.1f}pt)  "
              f"E1 {rates[1]:>5.1%} ({e1_delta * 100:+5.1f}pt)  "
              f"E2 {rates[2]:>5.1%}")


def _fanfare_pilot_arm(overrides: dict[str, float]):
    weights = loader._pilot_index()["fanfare"]["weights"]
    original = dict(weights)
    try:
        weights.update(overrides)
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        weights.clear()
        weights.update(original)


def fanfare_pilot_readout() -> None:
    print(f"FANFARE PILOT SWEEP ({STARTER_RUNS} realistic runs/arm, "
          "same seeds)")
    for label, overrides in (
            ("current", {}),
            ("tempo 0.6 / sustain 1.0",
             {"tempo": 0.6, "sustain": 1.0}),
            ("damage 1.4",
             {"damage": 1.4}),
            ("converter",
             {"damage": 1.4, "tempo": 0.7, "sustain": 0.9}),
            ("aggressive",
             {"damage": 1.6, "tempo": 0.4, "sustain": 0.6})):
        _starter_result(label, _fanfare_pilot_arm(overrides))


FANFARE_SPENDERS = (
    "crescendo",
    "florid_cadenza",
    "flood_of_emotion",
    "universal_revelry",
    "high_tide",
)


def _fanfare_spend_arm(energy_delta: int = 0,
                       fanfare_delta: int = 0):
    cards = loader._card_index()
    original = {
        cid: (cards[cid].cost, cards[cid].fanfare_cost)
        for cid in FANFARE_SPENDERS
    }
    try:
        for cid in FANFARE_SPENDERS:
            card = cards[cid]
            card.cost = max(0, card.cost + energy_delta)
            card.fanfare_cost = max(0, card.fanfare_cost + fanfare_delta)
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        for cid, (cost, fanfare_cost) in original.items():
            cards[cid].cost = cost
            cards[cid].fanfare_cost = fanfare_cost


def fanfare_spend_readout() -> None:
    print(f"FANFARE SPENDER TAX SWEEP ({STARTER_RUNS} realistic runs/arm, "
          "same seeds)")
    for label, energy_delta, fanfare_delta in (
            ("current", 0, 0),
            ("spenders cost 1 less Energy", -1, 0),
            ("spenders cost 5 less Fanfare", 0, -5),
            ("both discounts", -1, -5)):
        _starter_result(
            label, _fanfare_spend_arm(energy_delta, fanfare_delta))


def _fanfare_followup_arm(bottom_repairs: bool,
                           common_efficiency: bool,
                           deep: bool = False):
    cards = loader._card_index()
    touched = (
        "florid_cadenza",
        "showstopper",
        "suffering_for_art",
        "hearts_swelling",
        "thunderous_ovation",
        "crowd_work",
        "audience_participation",
        "tempo_change",
        "ebb_and_flow",
        "thunderous_ovation",
    )
    original = {
        cid: (
            cards[cid].cost,
            cards[cid].fanfare_cost,
            cards[cid].encore_cost,
            copy.deepcopy(cards[cid].effects),
        )
        for cid in touched
    }
    try:
        if bottom_repairs:
            cards["florid_cadenza"].fanfare_cost = 5
            showstopper = cards["showstopper"]
            showstopper.effects[0]["amount"] = 7
            showstopper.effects[1]["if"] = "fanfare_at_least_15"
            showstopper.effects[1]["then"][0]["amount"] = 8
            cards["suffering_for_art"].effects[0]["amount"] = 1
            cards["hearts_swelling"].cost = 1
        if common_efficiency:
            cards["crowd_work"].effects.append({"op": "energy", "amount": 1})
            cards["audience_participation"].effects[0]["amount"] = 3
            cards["tempo_change"].encore_cost = 1
            cards["ebb_and_flow"].effects.append({"op": "energy", "amount": 1})
            cards["thunderous_ovation"].effects[0]["amount"] = 4
        if deep:
            return {
                encounter: _fight_cell(
                    "fanfare_weighted", "fanfare", encounter)
                for encounter in ENCOUNTERS
            }
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        for cid, (cost, fanfare_cost, encore_cost, card_effects) in (
                original.items()):
            cards[cid].cost = cost
            cards[cid].fanfare_cost = fanfare_cost
            cards[cid].encore_cost = encore_cost
            cards[cid].effects = card_effects


def fanfare_followup_readout() -> None:
    print(f"FANFARE FOLLOW-UP GROUPS ({STARTER_RUNS} realistic runs/arm, "
          "same seeds)")
    for label, bottom, common in (
            ("current first dose", False, False),
            ("bottom-card repairs", True, False),
            ("common efficiency", False, True),
            ("combined", True, True)):
        _starter_result(
            label, _fanfare_followup_arm(bottom, common))


def fanfare_draftcards_readout() -> None:
    results = model.run_many(
        "furina", "fanfare", "fanfare", draft.assigned_policy,
        RUNS, SEED, grant_relics=True, grant_potions=True)
    offered = collections.Counter()
    picked = collections.Counter()
    early_offered = collections.Counter()
    early_picked = collections.Counter()
    early_pick_wins = collections.Counter()
    early_pass_wins = collections.Counter()
    early_passes = collections.Counter()
    competitors: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)

    for result in results:
        for decision in result.decisions:
            fanfare_offers = [
                card for card in decision["offers"]
                if "fanfare" in card.archetypes
            ]
            for card in fanfare_offers:
                offered[card.id] += 1
                if decision["picked"] == card.id:
                    picked[card.id] += 1
                if decision["node"] < 4:
                    early_offered[card.id] += 1
                    if decision["picked"] == card.id:
                        early_picked[card.id] += 1
                        early_pick_wins[card.id] += result.won
                    else:
                        early_passes[card.id] += 1
                        early_pass_wins[card.id] += result.won
                        competitors[card.id][
                            decision["picked"] or "<skip>"] += 1

    print(f"FANFARE OFFER/PICK TRACE ({RUNS} realistic runs, seed {SEED})")
    print("  Sorted by early pick rate; Act rates compare runs where the same "
          "card was offered and taken/passed (directional, not randomized).")
    rows = []
    for cid, n_early in early_offered.items():
        card = loader.get_card(cid)
        n_pick = early_picked[cid]
        n_pass = early_passes[cid]
        rows.append((
            n_pick / n_early,
            cid,
            card.rarity,
            n_early,
            n_pick,
            early_pick_wins[cid] / n_pick if n_pick else 0.0,
            early_pass_wins[cid] / n_pass if n_pass else 0.0,
            competitors[cid].most_common(1)[0]
            if competitors[cid] else ("-", 0),
            picked[cid] / offered[cid],
        ))
    for (early_rate, cid, rarity, n_early, n_pick, pick_wr, pass_wr,
         competitor, all_rate) in sorted(rows):
        print(
            f"  {cid:<25} {rarity:<8} early {n_pick:>3}/{n_early:<3} "
            f"{early_rate:>5.1%}  all {all_rate:>5.1%}  "
            f"Act take/pass {pick_wr:>5.1%}/{pass_wr:>5.1%}  "
            f"pass→{competitor[0]} {competitor[1]}")


def _fanfare_target_arm(thunder_block: int = 3,
                         sea_cost: int = 2,
                         sea_encore: int = 0):
    cards = loader._card_index()
    thunder = cards["thunderous_ovation"]
    sea = cards["the_sea_is_my_stage"]
    original = (
        copy.deepcopy(thunder.effects),
        sea.cost,
        copy.deepcopy(sea.effects),
    )
    try:
        thunder.effects[0]["amount"] = thunder_block
        sea.cost = sea_cost
        if sea_encore:
            sea.effects.append({"op": "gain_encore", "amount": sea_encore})
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        thunder.effects = original[0]
        sea.cost = original[1]
        sea.effects = original[2]


def fanfare_targets_readout() -> None:
    print(f"FANFARE TARGETED FLOOR BRACKET ({STARTER_RUNS} realistic "
          "runs/arm, same seeds)")
    for label, thunder, sea_cost, sea_encore in (
            ("current", 3, 2, 0),
            ("Thunderous base Block 5", 5, 2, 0),
            ("Sea gains 6 Encore", 3, 2, 6),
            ("Sea cost 1 + 6 Encore", 3, 1, 6),
            ("Thunderous + Sea cost 1/Encore 6", 5, 1, 6)):
        _starter_result(
            label, _fanfare_target_arm(thunder, sea_cost, sea_encore))


def _fanfare_individual_arm(repair: str, deep: bool = False):
    cards = loader._card_index()
    touched = (
        "florid_cadenza",
        "showstopper",
        "suffering_for_art",
        "hearts_swelling",
    )
    original = {
        cid: (
            cards[cid].cost,
            cards[cid].fanfare_cost,
            copy.deepcopy(cards[cid].effects),
        )
        for cid in touched
    }
    try:
        if repair == "florid":
            cards["florid_cadenza"].fanfare_cost = 5
        elif repair == "showstopper":
            showstopper = cards["showstopper"]
            showstopper.effects[0]["amount"] = 7
            showstopper.effects[1]["if"] = "fanfare_at_least_15"
            showstopper.effects[1]["then"][0]["amount"] = 8
        elif repair == "suffering":
            cards["suffering_for_art"].effects[0]["amount"] = 1
        elif repair == "suffering_thunder":
            cards["suffering_for_art"].effects[0]["amount"] = 1
            cards["thunderous_ovation"].effects[0]["amount"] = 5
        elif repair == "hearts":
            cards["hearts_swelling"].cost = 1
        elif repair != "current":
            raise ValueError(repair)
        if deep:
            return {
                encounter: _fight_cell(
                    "fanfare_weighted", "fanfare", encounter)
                for encounter in ("punisher", "tank_boss")
            }
        return model.run_many(
            "furina", "fanfare", "fanfare", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        for cid, (cost, fanfare_cost, card_effects) in original.items():
            cards[cid].cost = cost
            cards[cid].fanfare_cost = fanfare_cost
            cards[cid].effects = card_effects


def fanfare_individual_readout() -> None:
    print(f"FANFARE INDIVIDUAL REPAIRS ({STARTER_RUNS} realistic runs + "
          f"{FIGHTS} deep fights/cell, same seeds)")
    for label, repair in (
            ("current", "current"),
            ("Florid Spend 5", "florid"),
            ("Showstopper 7+8 at 15", "showstopper"),
            ("Suffering self-damage 1", "suffering"),
            ("Hearts Swelling cost 1", "hearts")):
        results = _fanfare_individual_arm(repair)
        rates = _run_rates(results)
        deep = _fanfare_individual_arm(repair, deep=True)
        print(
            f"  {label:<27} Act {rates[0]:>5.1%}  "
            f"E1 {rates[1]:>5.1%}  E2 {rates[2]:>5.1%}  "
            f"deep P {deep['punisher']['wr']:>5.1%} / "
            f"T {deep['tank_boss']['wr']:>5.1%}")


def _fight_cell(deck: str, pilot_id: str, encounter: str) -> dict:
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    package = loader.character_packages("furina").get(deck, [])
    rows = []
    for i in range(FIGHTS):
        player = loader.build_player_from_ids(
            "furina", loader.starting_deck("furina") + list(package))
        state = run_fight(player, loader.build_encounter(encounter), pilot,
                          seed=SEED + i)
        stat = metrics.extract(state, player.max_hp)
        gained = sum(e["amount"] for e in state.log
                     if e["event"] == "gain_fanfare")
        spent = sum(e["amount"] for e in state.log
                    if e["event"] == "fanfare_spent")
        max_fanfare = max((e["total"] for e in state.log
                           if e["event"] == "gain_fanfare"), default=0)
        modes = collections.Counter(
            e.get("mode") for e in state.log
            if e["event"] == "spotlight_designated")
        rows.append((stat, gained, spent, max_fanfare,
                     modes["center_stage"], modes["guest_cast"]))
    return {
        "wr": sum(r[0].won for r in rows) / FIGHTS,
        "dpt": statistics.mean(
            r[0].total_damage_dealt / max(1, r[0].turns) for r in rows),
        "turns": statistics.mean(r[0].turns for r in rows),
        "gain": statistics.mean(r[1] for r in rows),
        "spend": statistics.mean(r[2] for r in rows),
        "peak": statistics.mean(r[3] for r in rows),
        "center": statistics.mean(r[4] for r in rows),
        "guest": statistics.mean(r[5] for r in rows),
    }


def battery_readout() -> None:
    configs = (("salon_weighted", "salon"),
               ("spotlight_weighted", "spotlight"),
               ("spotlight_companions_only", "spotlight"),
               ("fanfare_weighted", "fanfare"),
               ("self_carry", "fanfare"))
    print(f"DEEP BATTERY ({FIGHTS} fights/cell, seed {SEED})")
    for deck, pilot_id in configs:
        print(f"  {deck}")
        for encounter in ENCOUNTERS:
            r = _fight_cell(deck, pilot_id, encounter)
            print(f"    {encounter:<10} WR {r['wr']:>5.1%}  "
                  f"DPT {r['dpt']:>5.1f}  turns {r['turns']:>4.1f}  "
                  f"Fanfare +{r['gain']:>4.1f}/-{r['spend']:>4.1f} "
                  f"peak {r['peak']:>4.1f}  "
                  f"modes C{r['center']:.1f}/G{r['guest']:.1f}")


def _ablation_cell(package: list[str], encounter: str) -> tuple[float, float]:
    pilot = make_pilot(loader.pilot_weights("spotlight"))
    wins = 0
    dpt = []
    for i in range(ABLATION_FIGHTS):
        player = loader.build_player_from_ids(
            "furina", loader.starting_deck("furina") + package)
        state = run_fight(player, loader.build_encounter(encounter), pilot,
                          seed=SEED + i)
        stat = metrics.extract(state, player.max_hp)
        wins += stat.won
        dpt.append(stat.total_damage_dealt / max(1, stat.turns))
    return wins / ABLATION_FIGHTS, statistics.mean(dpt)


def ablation_readout() -> None:
    """Replace each machinery slot with a plain Companion and remeasure ST."""
    base = list(loader.character_packages("furina")["spotlight_weighted"])
    candidates = []
    for cid in base:
        card = loader.get_card(cid)
        if cid not in candidates and "spotlight" in card.archetypes \
                and not card.is_companion:
            candidates.append(cid)
    encounters = ("punisher", "tank_boss")
    baseline = {e: _ablation_cell(base, e) for e in encounters}
    print(f"SPOTLIGHT SLOT ABLATION ({ABLATION_FIGHTS} fights/ST cell; "
          "replace one card with Chevreuse — Interdiction Fire)")
    print("  baseline " + "  ".join(
        f"{e} {baseline[e][0]:.1%}/{baseline[e][1]:.1f}DPT"
        for e in encounters))
    rows = []
    for cid in candidates:
        package = list(base)
        package[package.index(cid)] = "chevreuse_interdiction_fire"
        cells = {e: _ablation_cell(package, e) for e in encounters}
        wr_delta = statistics.mean(
            (cells[e][0] - baseline[e][0]) * 100 for e in encounters)
        dpt_delta = statistics.mean(
            cells[e][1] - baseline[e][1] for e in encounters)
        rows.append((wr_delta, dpt_delta, cid, cells))
    for wr_delta, dpt_delta, cid, cells in sorted(rows, reverse=True):
        detail = "  ".join(f"{e} {cells[e][0]:.1%}/{cells[e][1]:.1f}"
                            for e in encounters)
        print(f"  {cid:<24} mean {wr_delta:+5.1f}pt/{dpt_delta:+4.1f}DPT  "
              f"{detail}")


def _starter_arm(attack: str | None = None,
                 support: str | None = None,
                 randomized: bool = True):
    """Run the real role-locked starter, optionally fixing either roll."""
    spec = loader._character_index()["furina"]
    original = spec.get("randomized_starter")
    try:
        if not randomized:
            spec.pop("randomized_starter", None)
        else:
            resolved = {
                role: {
                    "replace": slot["replace"],
                    "choices": list(slot["choices"]),
                }
                for role, slot in original.items()
            }
            if attack is not None:
                resolved["attack"]["choices"] = [attack]
            if support is not None:
                resolved["support"]["choices"] = [support]
            spec["randomized_starter"] = resolved
        return model.run_many(
            "furina", "spotlight", "spotlight", draft.assigned_policy,
            STARTER_RUNS, SEED, grant_relics=True, grant_potions=True)
    finally:
        if original is None:
            spec.pop("randomized_starter", None)
        else:
            spec["randomized_starter"] = original


def _starter_result(label: str, results) -> None:
    wins = sum(r.won for r in results)
    first_elite = sum(r.death_node is None or r.death_node > 4
                      for r in results)
    second_elite = sum(r.death_node is None or r.death_node > 8
                       for r in results)
    online = sum(r.time_to_online is not None and r.time_to_online <= 3
                 for r in results)
    print(f"  {label:<35} Act {wins / STARTER_RUNS:>5.1%}  "
          f"E1 {first_elite / STARTER_RUNS:>5.1%}  "
          f"E2 {second_elite / STARTER_RUNS:>5.1%}  "
          f"core@E1 {online / STARTER_RUNS:>5.1%}")


def starter_readout() -> None:
    spec = loader._character_index()["furina"]["randomized_starter"]
    attacks = list(spec["attack"]["choices"])
    supports = list(spec["support"]["choices"])
    print(f"FURINA STARTER PAIRINGS ({STARTER_RUNS} realistic runs/arm, "
          "same seeds)")
    _starter_result("canonical basics", _starter_arm(randomized=False))
    _starter_result("randomized aggregate", _starter_arm())
    for attack in attacks:
        for support in supports:
            attack_name = loader.get_card(attack).name
            support_name = loader.get_card(support).name
            label = f"{attack_name} + {support_name}"
            results = _starter_arm(attack, support)
            _starter_result(label, results)


def _starter_nudge_arm(soloist_damage: int, stage_block: int):
    cards = loader._card_index()
    soloist_fx = cards["soloists_solicitation"].effects[0]
    stage_fx = cards["stage_presence"].effects[0]
    original = soloist_fx["amount"], stage_fx["amount"]
    try:
        soloist_fx["amount"] = soloist_damage
        stage_fx["amount"] = stage_block
        return _starter_arm()
    finally:
        soloist_fx["amount"], stage_fx["amount"] = original


def nudge_readout() -> None:
    """Bracket small personal-basic lifts after removing Box Trick's skew."""
    starter = loader._character_index()["furina"]["randomized_starter"]
    original_supports = starter["support"]["choices"]
    try:
        starter["support"]["choices"] = [
            "charlotte_enduring_frosthelm",
            "lynette_enigmatic_feint",
        ]
        print(f"FURINA BASE-KIT NUDGES ({STARTER_RUNS} realistic runs/arm, "
              "Charlotte/Enigmatic support slate)")
        for label, damage, block in (
                ("prior: Soloist 4 / Stage 5", 4, 5),
                ("Soloist 5 / Stage 5", 5, 5),
                ("shipping: Soloist 4 / Stage 6", 4, 6),
                ("Soloist 5 / Stage 6", 5, 6)):
            _starter_result(label, _starter_nudge_arm(damage, block))
    finally:
        starter["support"]["choices"] = original_supports


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("suite", "all"):
        suite_readout()
    if mode in ("fanfare", "all"):
        fanfare_readout()
    if mode in ("fanfare-core", "all"):
        fanfare_core_readout()
    if mode in ("fanfare-cards", "all"):
        fanfare_cards_readout()
    if mode in ("fanfare-pilot", "all"):
        fanfare_pilot_readout()
    if mode in ("fanfare-spend", "all"):
        fanfare_spend_readout()
    if mode in ("fanfare-followup", "all"):
        fanfare_followup_readout()
    if mode in ("fanfare-draftcards", "all"):
        fanfare_draftcards_readout()
    if mode in ("fanfare-targets", "all"):
        fanfare_targets_readout()
    if mode in ("fanfare-individual", "all"):
        fanfare_individual_readout()
    if mode in ("draft", "all"):
        draft_readout()
    if mode in ("battery", "all"):
        battery_readout()
    if mode in ("ablation", "all"):
        ablation_readout()
    if mode in ("starter", "all"):
        starter_readout()
    if mode in ("nudge", "all"):
        nudge_readout()
    if mode not in (
            "suite", "fanfare", "fanfare-core", "fanfare-cards",
            "fanfare-pilot", "fanfare-spend", "fanfare-followup",
            "fanfare-draftcards", "fanfare-targets", "fanfare-individual",
            "draft", "battery", "ablation", "starter", "nudge", "all"):
        raise SystemExit(
            "choose suite, fanfare, fanfare-core, fanfare-cards, "
            "fanfare-pilot, fanfare-spend, fanfare-followup, "
            "fanfare-draftcards, fanfare-targets, fanfare-individual, draft, "
            "battery, ablation, starter, nudge, or all")


if __name__ == "__main__":
    main()
