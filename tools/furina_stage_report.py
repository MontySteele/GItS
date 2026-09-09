#!/usr/bin/env python3
"""The FURINA STAGE's reports (`EB-724`; the brief's sec.13, in order).

    .venv/Scripts/python.exe -m tools.furina_stage_report
    .venv/Scripts/python.exe -m tools.furina_stage_report --fights 400 --seed 11

WHAT THIS IS. `review/active/furina-stage-brief-2026-09-08.md` sec.13 lists
five things the sim has to report under the arm, and this prints all five from
ONE run so a round packet can quote them together instead of assembling them:

  1. Spend fires, split by the lead's bar AT THE MOMENT OF SPEND (1-2, 3-5,
     6 and up) and by whether the target died.
  2. Performers lost by a hit, by a bow, and by rotation.
  3. Turns with one, two and three performers on stage.
  4. Fanfare absorbed on the lead against what would have reached Furina --
     the Refill-as-prevention price the LAW clause R269 added asks for.
  5. A granted PRESERVE deck against a granted EXPEND deck, on the same seeds.

WHY A REPORT TOOL AND NOT A TEST. `tools/klee_survival_sprint.py`'s shape and
its reason: a measurement grid is not a gate. Nothing here asserts anything and
nothing here is a balance claim -- under R215 B no number measured on a
prototype is quotable, so what this prints is a shape for a seat round to read
against, not a table for a packet to cite as a result.

HOW IT TURNS THE ARM ON. `furina_stage.FURINA_STAGE` is a MODULE constant, set
here for the process and nowhere else. That is the same door
`tier0/tests/test_furina_stage.py` opens with `monkeypatch`, and it is why the
flag lives in the arm module rather than in `constants.py`: a run of this tool
moves neither the constant census nor the world stamp.

THE TWO GRANTED DECKS are sec.9's -- "Round one runs the natural starter and
the two granted decks, Preserve and Expend, on the same seed" -- built by ID
off the batch-one rows, because a drafted deck cannot be asked to hold a
particular shape. Preserve is readers, Refills, Scene Change and the Rare;
Expend is Understudy, the three named summons and the Spend attacks.
"""

from __future__ import annotations

import argparse
import collections
import random
import sys

from tier0.engine import furina_stage


# --- sec.9's two granted decks ---------------------------------------------
#
# TEN CARDS EACH BESIDE THE SEVEN BASICS, so the two differ in what they hold
# and not in how many cards they hold. Both keep the three kit starters, which
# is what makes them the same character playing two ways rather than two
# characters.

BASICS = (["soloists_solicitation"] * 3 + ["stage_presence"] * 3
          + ["regal_bearing"])

STARTER_KIT = ["proto_fs_salon_debut", "proto_fs_curtain_rise",
               "proto_fs_standing_ovation"]

#: PRESERVE: grow the lead behind Block, Refill the reserve, cash big with the
#: readers and the Rare (brief sec.4).
PRESERVE = STARTER_KIT + [
    "proto_fs_standing_ovation", "proto_fs_warm_reception",
    "proto_fs_warm_reception", "proto_fs_scene_change",
    "proto_fs_ousia_surge", "proto_fs_pneuma_refrain",
    "proto_fs_interposition", "proto_fs_let_the_people_rejoice",
]

#: EXPEND: field performers cheaply, spend them at 1 for full riders and bows,
#: replace them. Pays in cards and Energy, not in Fanfare (brief sec.4).
EXPEND = STARTER_KIT + [
    "proto_fs_understudy", "proto_fs_understudy",
    "proto_fs_gentilhomme_usher", "proto_fs_surintendante_chevalmarin",
    "proto_fs_mademoiselle_crabaletta", "proto_fs_curtain_rise",
    "proto_fs_tidal_flourish", "proto_fs_grand_entrance",
    "proto_fs_final_bow",
]

ARMS = (("natural", None), ("preserve", PRESERVE), ("expend", EXPEND))

#: The buckets sec.13 names, in its own order.
BARS = ((1, 2, "1-2"), (3, 5, "3-5"), (6, 10 ** 9, "6+"))


def _bucket(bar: int) -> str:
    for low, high, label in BARS:
        if low <= bar <= high:
            return label
    return "0"          # a Spend into an empty stage: the rider did not fire


def _run(deck, encounter, fights, seed):
    """One arm's fights, returning the event logs. Late imports: turning the
    flag on before `combat` binds its module-level readers is the whole reason
    `main` sets it first."""
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot.policy import make_pilot

    pilot = make_pilot(loader.pilot_weights("salon"))
    logs = []
    for i in range(fights):
        if deck is None:
            player = loader.build_player("furina")
        else:
            player = loader.build_player_from_ids("furina", BASICS + deck)
        state = combat.run_fight(player, loader.build_encounter(encounter),
                                 pilot, seed=seed + i)
        logs.append(state)
    return logs


def _rows(states, event):
    for st in states:
        for row in st.log:
            if row.get("event") == event:
                yield st, row


def report(states, label, out=sys.stdout):
    """The five reports, in sec.13's order, for one arm."""
    print(f"\n=== {label} ({len(states)} fights) ===", file=out)

    # 1. Spend fires, by the bar at the moment of Spend and by whether the
    #    target died. "Whether the target died" is read as the fight ending on
    #    this play's turn -- the sim has no per-Spend target, because a Spend
    #    is a payment and the card's own damage op is what aims.
    # "WHETHER THE TARGET DIED" IS READ AS THE FIGHT'S LAST TURN, and the
    # substitution is disclosed rather than hidden: a Spend is a PAYMENT and
    # the card's own damage op is what aims, so the sim has no per-Spend
    # target to ask about. What sec.13's split is for is the difference
    # between cashing out and wagering (sec.4's "Spend for lethal is clean,
    # Spend speculatively is the wager"), and the turn the fight ended on is
    # the fact that answers it. A fight the player LOST has no such turn, so
    # its spends all count as wagers.
    spends = collections.Counter()
    lethal = collections.Counter()
    for st, row in _rows(states, "stage_spend"):
        bucket = _bucket(row["bar_at_spend"])
        spends[bucket] += 1
        last = max((r.get("turn", 0) for r in st.log
                    if r.get("event") == "stage_spend"), default=0)
        if not st.living_enemies and st.player.alive and row["turn"] == last:
            lethal[bucket] += 1
    total = sum(spends.values())
    print(f"1. Spend fires: {total}", file=out)
    for _low, _high, label_ in BARS:
        n = spends[label_]
        share = f"{100 * n / total:.0f}%" if total else "--"
        print(f"     bar {label_:>4}: {n:5d}  ({share})   "
              f"lethal turn: {lethal[label_]}", file=out)

    # 2. Performers lost, by cause.
    lost = collections.Counter(row["reason"]
                               for _st, row in _rows(states, "stage_leave"))
    rotated = sum(1 for _st, _r in _rows(states, "stage_rotate_out"))
    print("2. Performers lost:", file=out)
    print(f"     by a hit:      {lost['hit']}", file=out)
    print(f"     by a bow:      {lost['spend'] + lost['spend_all'] + lost['final_bow']}",
          file=out)
    print(f"     by rotation:   {rotated}", file=out)

    # 3. Turns with one, two and three performers.
    census = collections.Counter(row["performers"]
                                 for _st, row in _rows(states, "stage_census"))
    turns = sum(census.values())
    print(f"3. Turns by cast size ({turns} turns sampled):", file=out)
    for n in range(furina_stage.SEATS + 1):
        share = f"{100 * census[n] / turns:.0f}%" if turns else "--"
        print(f"     {n} performer(s): {census[n]:5d}  ({share})", file=out)

    # 4. The Refill-as-prevention price: what the lead ate, against what
    #    reached her anyway.
    absorbed = sum(row["amount"] for _st, row in _rows(states, "stage_absorb"))
    to_her = sum(row["amount"] for _st, row in _rows(states, "player_hit"))
    print(f"4. Fanfare absorbed on the lead: {absorbed}", file=out)
    print(f"     HP that reached Furina anyway: {to_her}", file=out)
    denom = absorbed + to_her
    if denom:
        print(f"     the cast took {100 * absorbed / denom:.0f}% of what got "
              f"through her Block", file=out)

    # 5. is the comparison across arms; `main` prints it once at the foot.
    won = sum(1 for st in states if not st.living_enemies and st.player.alive)
    print(f"   winrate: {100 * won / len(states):.1f}%  "
          f"(HP left, mean: "
          f"{sum(max(0, st.player.hp) for st in states) / len(states):.1f})",
          file=out)
    return {"label": label, "fights": len(states), "won": won,
            "spends": total, "absorbed": absorbed}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fights", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--encounter", default="attrition")
    args = ap.parse_args(argv)

    from understudy.report import console_safe
    console_safe()

    # THE ARM, ON, for this process and nothing else. Set BEFORE any engine
    # import that binds a reader, which is why every import below this line is
    # inside a function.
    furina_stage.FURINA_STAGE = True

    print(f"FURINA, THE STAGE -- sec.13 reports\n"
          f"arm: FURINA_STAGE on; fights per arm: {args.fights}; "
          f"seed: {args.seed}; encounter: {args.encounter}")
    print("NOT QUOTABLE (R215 B): a shape for a seat round to read against, "
          "never a measured result.")

    summary = []
    for label, deck in ARMS:
        states = _run(deck, args.encounter, args.fights, args.seed)
        summary.append(report(states, label))

    # 5. The two granted decks, on the same seeds.
    print("\n=== 5. Preserve against Expend, same seeds ===")
    for row in summary:
        print(f"  {row['label']:<9} wins {row['won']:4d}/{row['fights']}   "
              f"Spend fires {row['spends']:5d}   "
              f"Fanfare absorbed {row['absorbed']:6d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
