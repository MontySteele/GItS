"""Probe B2 (R103 probe (a)) — the +2 block offset, measured on a fixed script.

**A MEASUREMENT, NOT A POLICY.** This module drives the real game through a
script written down in advance so that the block reading it produces has no
policy in it. It exercises no design authority, changes no mod behaviour, and
concludes nothing: the answer is in `docs/archive/probe-a-block-offset.md`.

The pre-registered question it exists to answer:

    "Does the +2 block offset (C1 candidate) reproduce in a minimal fight
     with relics stripped and a fixed script?"

WHAT THE SCRIPT IS, AND WHY IT IS THIS
--------------------------------------
S7's C1 cluster is `l2.block_at_turn_end`, sim over engine by exactly 2 on
133/277 turns. Two things can produce that: the engine resolving a card's
Block 2 lower than tier0's arithmetic (a play-resolution difference), or the
two instruments reading the same number at different moments (a sampling
seam). The script separates them by reading `player.block` at EVERY decision
point, so a turn's total is never the only observation:

    turn open -> [read] play -> [read] play -> [read] end_turn

Consecutive readings bracket exactly one card, the same way S7's L1 bracket
uses `target_hp` for damage.

THE ARM, AND WHY THERE ARE TWO
------------------------------
Furina's starter relic grants an Ethereal Spotlight every turn; playing it
opens a Center Stage / Guest Cast selector, and that answer decides whether a
Companion card's printed Block is multiplied (`SpotlightSystem.PrintedBlock`
on the C# side, `effects._spotlight_scale` on tier0's). The script FIXES the
answer -- `--spotlight center` or `--spotlight guest` -- so the same Companion
card can be read under both, and the arm is a declared input rather than
something a policy chose.

"RELICS STRIPPED"
-----------------
The game offers no relic-less start. The probe runs the FIRST fight of a fresh
run instead, where the only relic is the character's starter, and records
`player.relics` on every reading so the relic state is KNOWN rather than
assumed. Whether that starter can touch Block is a fact the doc states from
the recording, not from memory.

Usage
-----

    python -m understudy.probe_block --spotlight center --seed TRACKB2A
    python -m understudy.probe_block --spotlight guest  --seed TRACKB2B
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from understudy import policy_v1, soak
from understudy.policy_v1 import Decision

# The selector this probe fixes, and the exact strings the bridge offers.
SPOTLIGHT_OFFERS = ("center stage", "guest cast")
ARM_CHOICE = {"center": "Center Stage", "guest": "Guest Cast"}

# The card the starter relic grants. Played first every turn because the
# selector answer has to be standing before any Companion card resolves.
SPOTLIGHT_CARD = "ethereal spotlight"


def _hand(state: dict) -> list[dict]:
    return list((state.get("player") or {}).get("hand") or [])


def _playable(entry: dict) -> bool:
    return entry.get("can_play") is not False


class ScriptedPolicy:
    """`policy_v1` with combat and the Spotlight selector overridden.

    Everything outside a fight is delegated untouched: the probe's claim is
    about a fight, and re-deciding the map or the draft would put a second
    policy into a measurement that is supposed to have none.
    """

    POLICY_VERSION = "probe_b2/" + policy_v1.POLICY_VERSION
    BLOCK_MATTERS_FRACTION = policy_v1.BLOCK_MATTERS_FRACTION
    COMPANION_SHARE_FOR_GUEST_CAST = policy_v1.COMPANION_SHARE_FOR_GUEST_CAST
    # `soak.RunDriver` reaches through the module for the memo type as well as
    # for `decide`. Delegated rather than reimplemented: the probe overrides
    # WHAT is chosen, never the bookkeeping the driver keeps around it.
    Memo = policy_v1.Memo

    def __init__(self, arm: str, readings: list[dict], out: Any,
                 turns: int) -> None:
        self.arm = arm
        self.readings = readings
        self.out = out
        # THE SCRIPT HAS TO STOP, AND THE FIRST ATTEMPT PROVED IT. A
        # Block-only script never kills anything and Furina never dies behind
        # the Block it is measuring: the first live run reached round 140 of
        # one floor-2 fight and was still going. After `turns` rounds the
        # probe hands combat back to `policy_v1` so the fight resolves and the
        # run ends; every reading it took before the hand-back is unaffected,
        # and the analysis reads only rounds <= `turns`.
        self.turns = turns

    # -- the reading ------------------------------------------------------
    def _read(self, state: dict, about: str, extra: dict | None = None) -> None:
        p = state.get("player") or {}
        b = state.get("battle") or {}
        row = {
            "ts": time.time(),
            "state_type": state.get("state_type"),
            "round": b.get("round"),
            "turn_owner": b.get("turn"),
            "block": int(p.get("block", 0) or 0),
            "hp": p.get("hp"),
            "energy": p.get("energy"),
            "about": about,
            "relics": [r.get("name") if isinstance(r, dict) else r
                       for r in (p.get("relics") or [])],
            "status": [(s.get("name"), s.get("amount", s.get("stacks")))
                       for s in (p.get("status") or []) if isinstance(s, dict)],
            # P1.5 item 2's reflection read of BaseLib's custom-resource
            # registry. Recorded beside the status strip rather than instead
            # of it: the badge and the resource are two readings of one meter
            # and the difference between them is itself a fact.
            "resources": p.get("resources"),
            # Read through the soak's own extractor so the probe and the fight
            # record cannot disagree about what "the meters" are.
            "meters": soak._meters(state) if state.get("state_type") in soak.COMBAT else None,
            "enemies": [{"name": e.get("name"), "hp": e.get("hp"),
                         "block": e.get("block", 0),
                         "status": [(s.get("name"), s.get("amount", s.get("stacks")))
                                    for s in (e.get("status") or [])
                                    if isinstance(s, dict)]}
                        for e in (state.get("enemies") or (state.get("battle") or {}).get("enemies") or [])],
            **(extra or {}),
        }
        self.readings.append(row)
        # WRITTEN AS IT IS TAKEN. A reading held in a list until the run ends
        # is a reading lost the moment the run does not, and a probe whose
        # output survives only the happy path is not an instrument.
        if self.out is not None:
            self.out.write(json.dumps(row, ensure_ascii=False) + "\n")
            self.out.flush()

    # -- the script -------------------------------------------------------
    def decide(self, state: dict, memo: Any, commit: str | None = None) -> Decision:
        st = str(state.get("state_type"))
        if st in soak.COMBAT:
            return self._combat(state, memo, commit)
        choice = self._spotlight_answer(state)
        if choice is not None:
            return choice
        return policy_v1.decide(state, memo, commit=commit)

    def _spotlight_answer(self, state: dict) -> Decision | None:
        # Read exactly where `policy_v1._choice_overlay` reads, and index the
        # same way it does (list position, not `card.index`) -- the probe must
        # differ from the policy in WHICH option it takes and in nothing else.
        blob = state.get("card_select") or {}
        entries = [e for e in (blob.get("cards") or []) if isinstance(e, dict)]
        offered = [str(e.get("name") or "").strip().lower() for e in entries]
        if not set(SPOTLIGHT_OFFERS).issubset(set(offered)):
            return None
        index = offered.index(ARM_CHOICE[self.arm].lower())
        self._read(state, "spotlight_selector",
                   extra={"chosen": ARM_CHOICE[self.arm], "offered": offered})
        return Decision(
            available=True, category="probe", revision="probe_b2",
            action={"action": "select_card", "index": index},
            label=f"FIXED SCRIPT: {ARM_CHOICE[self.arm]}",
            rationale="the probe's declared arm; no policy chose this",
            notes={"probe": "b2", "arm": self.arm})

    def _combat(self, state: dict, memo: Any, commit: str | None) -> Decision:
        rnd = int((state.get("battle") or {}).get("round") or 0)
        if rnd > self.turns:
            return policy_v1.decide(state, memo, commit=commit)
        hand = _hand(state)
        # 1. the granted Spotlight, so the arm is standing for the whole turn
        for i, c in enumerate(hand):
            if (str(c.get("name") or "").strip().lower() == SPOTLIGHT_CARD
                    and _playable(c)):
                self._read(state, "before_play", extra={"card": c.get("name")})
                return self._play(state, i, c, "the granted Spotlight, first")
        # 2. every card that prints Block, in hand order -- no scoring, no
        #    ladder, no preference. Block cards are recognised from the WIRE's
        #    own printed description, never from a sheet: a probe that read
        #    tier0 to decide what to play would have tier0 in both sides of
        #    its own comparison.
        for i, c in enumerate(hand):
            if _playable(c) and "block" in str(c.get("description") or "").lower():
                self._read(state, "before_play", extra={"card": c.get("name")})
                return self._play(state, i, c, "prints Block (wire text)")
        self._read(state, "before_end_turn")
        return Decision(
            available=True, category="probe", revision="probe_b2",
            action={"action": "end_turn"}, label="FIXED SCRIPT: end turn",
            rationale="no Block card left in hand", notes={"probe": "b2"})

    def _play(self, state: dict, index: int, entry: dict, why: str) -> Decision:
        action = policy_v1._play(state, index)
        return Decision(
            available=True, category="probe", revision="probe_b2",
            action=action, label=f"FIXED SCRIPT: play {entry.get('name')}",
            rationale=why, notes={"probe": "b2", "card": entry.get("name")})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="probe B2 — the +2 block offset")
    ap.add_argument("--spotlight", choices=sorted(ARM_CHOICE), required=True)
    ap.add_argument("--seed", default=None, help="chosen run seed (P1.5)")
    ap.add_argument("--max-fights", type=int, default=1)
    ap.add_argument("--turns", type=int, default=8,
                    help="scripted rounds before combat is handed back to "
                         "policy_v1 so the fight can actually end")
    ap.add_argument("--no-setup", action="store_true")
    ap.add_argument("--out", default="", help="probe reading JSONL")
    args = ap.parse_args(argv)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    readings: list[dict] = []
    out = args.out or str(soak.LOG_DIR / f"probe-b2-{args.spotlight}-{stamp}.jsonl")
    soak.LOG_DIR.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {}
    with open(out, "w", encoding="utf-8") as fh:
        scripted = ScriptedPolicy(args.spotlight, readings, fh, args.turns)
        # `soak.run_scripted` is the setup / policy-swap / teardown dance this
        # file and `probe_corpse.py` each carried a copy of (EB-142). The seam
        # and its `finally` restore are unchanged; only their address is.
        summary = soak.run_scripted(scripted, stamp,
                                    character=soak.DEFAULT_CHARACTER,
                                    max_fights=args.max_fights,
                                    chosen_seed=args.seed,
                                    do_setup=not args.no_setup)

    print(json.dumps({"arm": args.spotlight, "stamp": stamp,
                      "turns_scripted": args.turns,
                      "readings": len(readings), "out": out,
                      "run": summary}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
