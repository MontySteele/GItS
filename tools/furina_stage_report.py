#!/usr/bin/env python3
"""FURINA'S STAGE -- the arm's reports, on the re-founded rules.

    .venv/Scripts/python.exe -m tools.furina_stage_report
    .venv/Scripts/python.exe -m tools.furina_stage_report --fights 400 --seed 11

WHAT THIS IS. One run of fixed decks through `tier0.engine.furina_stage`
(`review/active/furina-refounding-2026-10-03.md`, sec.1 as sec.8 amends it,
sec.10's sheet), printing per deck, from the fight's own ledger
(`state.stage_ledger`, booked at each writer):

  1. THE FANFARE ECONOMY: gained, by door (cards, Bows, Charlotte, Powers);
     spent by a card's Spend; paid by each performer for its acts; and the
     line `start + gained - spent - paid = end`, checked per fight.
  2. THE STARS: acts paid for, and acts skipped for want of Fanfare.
  3. CUES: how many, on whom, and Cues on an empty stage.
  4. BOWS: by performer, the walk-ons, the guest repeats and A Five-Century
     Act's returns.
  5. TURNS BY CAST SIZE (0 to 4 performers at turn close).
  6. Per fight: damage dealt, damage that reached Furina, turns; winrate.

WHY A REPORT TOOL AND NOT A TEST. A measurement grid is not a gate. Nothing
here asserts anything and nothing here is a balance claim: no number measured
on a prototype is quotable, so what this prints is a shape for a seat round
to read against, not a table for a packet to cite.

THE DECKS are built by id off the sheet's rows, each the arm's starter plus a
handful of cards that lean on one family, so every rule is exercised at least
once. A smoke, not balance evidence.
"""

from __future__ import annotations

import argparse
import collections
import sys

from tier0.engine import furina_stage

#: The arm's own starter, read off `furina_stage.STARTER_IDS` so the report
#: cannot drift from what a run is dealt.
BASICS = [c for c in furina_stage.STARTER_IDS
          if not c.startswith("proto_fs_")]
STARTER_KIT = [c for c in furina_stage.STARTER_IDS
               if c.startswith("proto_fs_")]

#: The Salon trio and Rehearsal: summons, Cues and Dress Rehearsal.
SALON = STARTER_KIT + [
    "proto_fs_leading_lady", "proto_fs_surintendante_chevalmarin",
    "proto_fs_mademoiselle_crabaletta", "proto_fs_salon_debut",
    "proto_fs_interposition", "proto_fs_plot_twist",
    "proto_fs_counterclaim",
]
#: Spend small with Clorinde on stage.
SPEND_SMALL = STARTER_KIT + [
    "proto_fs_guest_star_clorinde", "proto_fs_warm_reception",
    "proto_fs_cheered_on", "proto_fs_quick_cue", "proto_fs_spirited_aria",
    "proto_fs_tidal_flourish", "proto_fs_pneuma_refrain",
]
#: Bank, then cash out: Bravura and the flow finisher.
FINALE = STARTER_KIT + [
    "proto_fs_warm_reception", "proto_fs_hold_your_places",
    "proto_fs_singer_of_many_waters", "proto_fs_bravura",
    "proto_fs_bring_the_house_down", "proto_fs_guest_star_navia",
]
#: The stars, funded by Charlotte.
STARS = STARTER_KIT + [
    "proto_fs_guest_star_neuvillette", "proto_fs_guest_star_charlotte",
    "proto_fs_guest_star_escoffier", "proto_fs_salon_debut",
    "proto_fs_stage_whisper", "proto_fs_warm_reception",
]
#: The supports: Lynette, Chevreuse, Sigewinne, Wriothesley.
SUPPORTS = STARTER_KIT + [
    "proto_fs_guest_star_lynette", "proto_fs_guest_star_chevreuse",
    "proto_fs_guest_star_sigewinne", "proto_fs_guest_star_wriothesley",
    "proto_fs_bis", "proto_fs_step_forward",
]
#: Bows: Gala Premiere, Grand Finale, Final Bow, Intermission, Da Capo,
#: Thunderous Applause and A Five-Century Act.
BOWS = STARTER_KIT + [
    "proto_fs_gala_premiere", "proto_fs_grand_finale", "proto_fs_final_bow",
    "proto_fs_intermission", "proto_fs_da_capo",
    "proto_fs_thunderous_applause", "proto_fs_five_century_act",
]
#: Directing: Lyney, Revolving Stage, Tutti!, Oratrice's Verdict, Endless
#: Waltz.
DIRECTING = STARTER_KIT + [
    "proto_fs_guest_star_lyney", "proto_fs_revolving_stage",
    "proto_fs_tutti", "proto_fs_oratrices_verdict",
    "proto_fs_endless_waltz", "proto_fs_mademoiselle_crabaletta",
]
#: Hydro and reactions.
HYDRO = STARTER_KIT + [
    "proto_fs_bubble_aria", "proto_fs_groundswell",
    "proto_fs_tide_of_applause", "proto_fs_grand_deluge",
    "proto_fs_regina_of_all_waters", "proto_fs_guest_star_neuvillette",
]
#: The Powers that bend the rules: Full House, Sold Out, Star Billing, Star
#: Turn, Premiere Season, Critics' Darling, Arkhe Alignment, Season Tickets.
POWERS = STARTER_KIT + [
    "proto_fs_full_house", "proto_fs_sold_out", "proto_fs_star_billing",
    "proto_fs_star_turn", "proto_fs_double_casting",
    "proto_fs_critics_darling", "proto_fs_arkhe_alignment",
    "proto_fs_season_tickets", "proto_fs_guest_star_clorinde",
]
#: No one on stage.
SOLO = STARTER_KIT + [
    "proto_fs_final_bow", "proto_fs_solo_verse", "proto_fs_soliloquy",
    "proto_fs_one_woman_show", "proto_fs_aria_for_one",
    "proto_fs_the_last_act", "proto_fs_between_acts",
]

ARMS = (("natural", None), ("salon", SALON), ("spend small", SPEND_SMALL),
        ("finale", FINALE), ("stars", STARS), ("supports", SUPPORTS),
        ("bows", BOWS), ("directing", DIRECTING), ("hydro", HYDRO),
        ("powers", POWERS), ("solo", SOLO))


def _run(deck, encounter, fights, seed):
    """One arm's fights, returning the final states."""
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot.policy import make_pilot

    pilot = make_pilot(loader.pilot_weights("salon"))
    states = []
    for i in range(fights):
        if deck is None:
            player = loader.build_player("furina")
        else:
            player = loader.build_player_from_ids("furina", BASICS + deck)
        states.append(combat.run_fight(
            player, loader.build_encounter(encounter), pilot, seed=seed + i))
    return states


def _ledger(st) -> dict:
    return st.stage_ledger or furina_stage.ledger(st)


def _dealt(st) -> int:
    """What the enemies lost this fight: each body's max HP less what it
    kept (a kill counts its whole bar, overkill nothing)."""
    return sum(e.max_hp - max(0, e.hp) for e in st.enemies)


def _turns(st) -> int:
    return sum(1 for row in st.log if row.get("event") == "stage_census")


def economy(states, out=sys.stdout, per_fight=False) -> dict:
    """Report 1, the Fanfare economy, for one arm."""
    n = len(states) or 1
    gained = collections.Counter()
    paid = collections.Counter()
    spent = spends = unbalanced = 0
    for st in states:
        led = _ledger(st)
        gained.update(led["gained"])
        paid.update(led["paid"])
        spent += led["spent"]
        spends += led["spends"]
        if furina_stage.ledger_expected_end(led) != furina_stage.fanfare(
                st.player):
            unbalanced += 1

    def line(name, total):
        print(f"     {name:<30} {total / n:7.2f}  {total:7d}", file=out)

    print("1. Fanfare economy (per fight mean / summed over the fights):",
          file=out)
    line("gained, all doors", sum(gained.values()))
    for source in furina_stage.GAIN_SOURCES:
        line(f"  {source}", gained[source])
    line("spent by a card's Spend", spent)
    line("  Spends", spends)
    line("paid by performers", sum(paid.values()))
    for member, total in sorted(paid.items()):
        line(f"  {member}", total)
    print(f"     start + gained - spent - paid = end: "
          f"{'holds in every fight' if not unbalanced else f'FAILS in {unbalanced} fight(s)'}",
          file=out)
    if per_fight:
        print("     fight  gained  spent   paid    end", file=out)
        for i, st in enumerate(states):
            led = _ledger(st)
            print(f"     {i:5d} {sum(led['gained'].values()):7d} "
                  f"{led['spent']:6d} {sum(led['paid'].values()):6d} "
                  f"{furina_stage.fanfare(st.player):6d}", file=out)
    return {"gained": sum(gained.values()), "spent": spent,
            "paid": sum(paid.values()), "unbalanced": unbalanced}


def report(states, label, out=sys.stdout, per_fight=False) -> dict:
    """Every report, in order, for one arm."""
    print(f"\n=== {label} ({len(states)} fights) ===", file=out)
    eco = economy(states, out=out, per_fight=per_fight)

    star_acts = collections.Counter()
    skips = collections.Counter()
    cues_on = collections.Counter()
    bows = collections.Counter()
    cues = whiffs = walk_ons = repeats = returns = 0
    for st in states:
        led = _ledger(st)
        star_acts.update(led["star_acts"])
        skips.update(led["star_skips"])
        cues_on.update(led["cues_on"])
        bows.update(led["bows"])
        cues += led["cues"]
        whiffs += led["cue_whiffs"]
        walk_ons += led["walk_ons"]
        repeats += led["guest_repeats"]
        returns += led["returns"]

    print("2. Stars (and Chevreuse): acts paid / skipped for want of Fanfare:",
          file=out)
    seen = sorted(set(star_acts) | set(skips))
    if not seen:
        print("     no star took the stage", file=out)
    for member in seen:
        print(f"     {member:<12} paid {star_acts[member]:5d}   "
              f"skipped {skips[member]:5d}", file=out)

    print(f"3. Cues: {cues} (on an empty stage: {whiffs})", file=out)
    for member, k in cues_on.most_common():
        print(f"     on {member:<12} {k:5d}", file=out)

    print(f"4. Bows: {sum(bows.values())}  walk-ons {walk_ons}  "
          f"guest repeats {repeats}  Five-Century returns {returns}",
          file=out)
    for member, k in bows.most_common():
        print(f"     {member:<12} {k:5d}", file=out)

    census = collections.Counter(row["performers"] for st in states
                                 for row in st.log
                                 if row.get("event") == "stage_census")
    turns = sum(census.values())
    print(f"5. Turns by cast size ({turns} turns sampled):", file=out)
    for k in range(max([furina_stage.SEATS, *census]) + 1):
        share = f"{100 * census[k] / turns:.0f}%" if turns else "--"
        print(f"     {k} performer(s): {census[k]:5d}  ({share})", file=out)

    n = len(states) or 1
    to_her = [sum(row["amount"] for row in st.log
                  if row.get("event") == "player_hit") for st in states]
    dealt = [_dealt(st) for st in states]
    fight_turns = [_turns(st) for st in states]
    won = sum(1 for st in states if not st.living_enemies and st.player.alive)
    print(f"6. Per fight: damage dealt {sum(dealt) / n:.1f}, damage reaching "
          f"Furina {sum(to_her) / n:.1f}, turns {sum(fight_turns) / n:.1f}",
          file=out)
    print(f"   winrate: {100 * won / n:.1f}%  (HP left, mean: "
          f"{sum(max(0, st.player.hp) for st in states) / n:.1f})", file=out)
    return {"label": label, "fights": len(states), "won": won,
            "spent": eco["spent"], "paid": eco["paid"], "cues": cues,
            "skips": sum(skips.values()), "bows": sum(bows.values()),
            "dealt": sum(dealt) / n, "to_her": sum(to_her) / n,
            "unbalanced": eco["unbalanced"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fights", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--encounter", default="attrition")
    ap.add_argument("--per-fight", action="store_true",
                    help="report 1: one Fanfare-economy line per fight")
    args = ap.parse_args(argv)

    from understudy.report import console_safe
    console_safe()

    print(f"FURINA'S STAGE (re-founded) -- the arm's reports\n"
          f"fights per arm: {args.fights}; "
          f"seed: {args.seed}; encounter: {args.encounter}")
    print("NOT QUOTABLE: a shape for a seat round to read against, never a "
          "measured result.")

    summary = []
    for label, deck in ARMS:
        states = _run(deck, args.encounter, args.fights, args.seed)
        summary.append(report(states, label, per_fight=args.per_fight))

    print("\n=== Every deck, same seeds ===")
    for row in summary:
        print(f"  {row['label']:<14} wins {row['won']:4d}/{row['fights']}   "
              f"spent {row['spent']:6d}   paid {row['paid']:6d}   "
              f"cues {row['cues']:5d}   skips {row['skips']:5d}   "
              f"bows {row['bows']:5d}   dealt/fight {row['dealt']:6.1f}   "
              f"to Furina/fight {row['to_her']:5.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
