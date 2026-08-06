"""Probe (e) (R118 / Q11) — corpse detonation, measured on a fixed script.

**A MEASUREMENT, NOT A POLICY.** This module drives the real game through a
script written down in advance so that the readings it produces have no policy
in them. It exercises no design authority, changes no mod behaviour, and
concludes nothing: the registration is
`docs/probe-e-corpse-detonation-registration-draft.md` (COUNTERSIGNED
2026-08-06) and the answer lands in the probe report, not here.

The pre-registered question it exists to answer, verbatim:

    "Does a killing blow on a bombed enemy early-detonate that enemy's bombs?"

THE SCRIPT, AND WHY IT IS THIS
------------------------------
Klee, first fight of a fresh run, chosen seed. Every action is one of three
verbs and the conditions that pick between them are arithmetic on wire
readings, so no turn contains a choice:

  kill arm (--arm kill):
    1. whittle  -- while the chosen target's (hp + block) > KABOOM_DAMAGE and
                   it carries no bombs: play Kaboom! at it.
    2. bomb     -- once (hp + block) <= KABOOM_DAMAGE: play Pop! at it (a
                   SKILL -- placing a bomb is not a hit and detonates
                   nothing). If Pop! is not in hand, end the turn and wait.
    3. blow     -- the target is bombed and killable in one hit: play Kaboom!
                   at it. That is the killing blow the question is about.

  control arm (--arm control):
    1. bomb     -- play Pop! at the target while (hp + block) > KABOOM_DAMAGE
                   (no whittling: the control wants the blow NON-lethal).
    2. blow     -- play Kaboom! at it. The enemy survives; per §4.2 an Attack
                   hit on a bombed enemy is the schedule on which bombs
                   resolve early, so this arm must show the detonation the
                   kill arm is being asked about. Without it, "the bombs did
                   not resolve" is not distinguishable from "the bombs were
                   never applied".

The two halves of the question are separable in the log: the bomb application
and the blow are distinct scripted actions with a reading between them
(`about` = before_play / after-state on the next decision point).

THE TWO TELLS (read on every reading, decided by neither)
---------------------------------------------------------
  * relic tell  -- Pounding Surprise is Klee's STARTER relic
                   (tier0/content/characters/klee.yaml `spark_on_detonation`),
                   so the first fight of a fresh run holds it by construction.
                   Its spark lands as the player's "Spark" power on the wire:
                   a Spark delta across the blow means the detonation hook
                   fired.
  * damage tell -- the target's and every other creature's hp/block plus the
                   player's hp, all recorded per reading; the blow is
                   bracketed by the readings on either side of it.

TARGET DISCIPLINE (confounder 2: single-target only)
----------------------------------------------------
The target is the lowest-HP living enemy at the first combat decision, pinned
by wire id for the rest of the fight. Kaboom! and Pop! are both single-target
by their printed sheets; the script plays NOTHING else -- no Jumpy Dumpty
(random targets), no Duck and Cover, no potions. In the kill arm the blow is
only thrown while a SECOND living enemy exists, because a fight that ends on
the blow takes the player's status strip (and with it the Spark tell) off the
wire before the after-reading exists. If the fight cannot satisfy that, the
script ends turns and the probe reports the state unreachable (layer 4)
rather than improvising.

Usage
-----

    python -m understudy.probe_corpse --arm kill    --seed PROBEE
    python -m understudy.probe_corpse --arm control --seed PROBEE
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from understudy import adapter, policy_v1, soak
from understudy.policy_v1 import Decision

KABOOM = "kaboom!"
POP = "pop!"
# Kaboom!'s printed damage (docs/klee-cards.yaml `kaboom`, amount: 7). Used
# only to SIZE the blow; the readings never consult the sheet.
KABOOM_DAMAGE = 7
CHARACTER = "KLEEMOD-KLEE"


def _hand(state: dict) -> list[dict]:
    return list((state.get("player") or {}).get("hand") or [])


def _playable(entry: dict) -> bool:
    return entry.get("can_play") is not False


class ScriptedPolicy:
    """`policy_v1` with combat overridden by the fixed script above."""

    POLICY_VERSION = "probe_e/" + policy_v1.POLICY_VERSION
    BLOCK_MATTERS_FRACTION = policy_v1.BLOCK_MATTERS_FRACTION
    COMPANION_SHARE_FOR_GUEST_CAST = policy_v1.COMPANION_SHARE_FOR_GUEST_CAST
    Memo = policy_v1.Memo

    def __init__(self, arm: str, readings: list[dict], out: Any,
                 turns: int) -> None:
        self.arm = arm
        self.readings = readings
        self.out = out
        self.turns = turns          # same stop the B2 script needed
        self.target_id: str | None = None
        self.blow_done = False

    # -- the reading ------------------------------------------------------
    def _read(self, state: dict, about: str, extra: dict | None = None) -> None:
        p = state.get("player") or {}
        b = state.get("battle") or {}
        row = {
            "ts": time.time(),
            "state_type": state.get("state_type"),
            "round": b.get("round"),
            "turn_owner": b.get("turn"),
            "hp": p.get("hp"),
            "block": int(p.get("block", 0) or 0),
            "energy": p.get("energy"),
            "about": about,
            "relics": [r.get("name") if isinstance(r, dict) else r
                       for r in (p.get("relics") or [])],
            "status": [(s.get("name"), s.get("amount", s.get("stacks")))
                       for s in (p.get("status") or []) if isinstance(s, dict)],
            "resources": p.get("resources"),
            "enemies": [{"id": adapter.enemy_id(e), "name": e.get("name"),
                         "hp": e.get("hp"), "block": e.get("block", 0),
                         "status": [(s.get("name"), s.get("amount", s.get("stacks")))
                                    for s in (e.get("status") or [])
                                    if isinstance(s, dict)]}
                        for e in adapter.enemy_blobs(state)],
            "target_id": self.target_id,
            **(extra or {}),
        }
        self.readings.append(row)
        if self.out is not None:
            self.out.write(json.dumps(row, ensure_ascii=False) + "\n")
            self.out.flush()

    # -- the script -------------------------------------------------------
    def decide(self, state: dict, memo: Any, commit: str | None = None) -> Decision:
        st = str(state.get("state_type"))
        if st in soak.COMBAT:
            return self._combat(state, memo, commit)
        return policy_v1.decide(state, memo, commit=commit)

    def _target(self, state: dict) -> dict | None:
        living = [e for e in adapter.enemy_blobs(state)
                  if int(e.get("hp", 0) or 0) > 0]
        if self.target_id is None:
            if not living:
                return None
            pick = min(living, key=lambda e: (int(e.get("hp", 0)),
                                              adapter.enemy_id(e)))
            self.target_id = adapter.enemy_id(pick)
            return pick
        for e in living:
            if adapter.enemy_id(e) == self.target_id:
                return e
        return None

    @staticmethod
    def _bombed(enemy: dict) -> bool:
        for s in enemy.get("status") or []:
            if isinstance(s, dict) and "bomb" in str(s.get("name") or "").lower():
                return True
        return False

    def _find(self, state: dict, name: str) -> int | None:
        for i, c in enumerate(_hand(state)):
            if (str(c.get("name") or "").strip().lower() == name
                    and _playable(c)):
                return i
        return None

    def _combat(self, state: dict, memo: Any, commit: str | None) -> Decision:
        rnd = int((state.get("battle") or {}).get("round") or 0)
        if self.blow_done or rnd > self.turns:
            # The blow (or the round bound) has been reached: every reading
            # that matters is on disk. Read once more so the after-state is
            # recorded, then hand combat back so the fight can actually end.
            self._read(state, "after_blow" if self.blow_done else "round_bound")
            return policy_v1.decide(state, memo, commit=commit)
        t = self._target(state)
        if t is None:
            self._read(state, "target_lost")
            return policy_v1.decide(state, memo, commit=commit)
        ehp = int(t.get("hp", 0) or 0) + int(t.get("block", 0) or 0)
        bombed = self._bombed(t)
        living = [e for e in adapter.enemy_blobs(state)
                  if int(e.get("hp", 0) or 0) > 0]
        kaboom = self._find(state, KABOOM)
        pop = self._find(state, POP)

        if self.arm == "kill":
            if bombed and ehp <= KABOOM_DAMAGE and kaboom is not None:
                if len(living) < 2:
                    # the fight would end on the blow and take the Spark
                    # tell off the wire with it -- declared unreachable, not
                    # improvised around (registration layer 4).
                    self._read(state, "blow_withheld_last_enemy")
                    return self._end(state)
                self._read(state, "before_blow", extra={"card": KABOOM,
                                                        "ehp": ehp})
                self.blow_done = True
                return self._play(state, kaboom, KABOOM,
                                  "the killing blow on the bombed target")
            if (not bombed and ehp <= KABOOM_DAMAGE and pop is not None
                    and kaboom is not None):
                # The bomb is only placed when the blow can follow it THIS
                # turn (Kaboom! in hand, energy for it). The first live run
                # proved why: a bomb left overnight on a 1-HP target
                # detonated on the normal start-of-turn schedule and killed
                # it before any blow existed to measure.
                self._read(state, "before_bomb", extra={"card": POP,
                                                        "ehp": ehp})
                return self._play(state, pop, POP,
                                  "place the bomb (skill; not a hit)")
            if not bombed and ehp > KABOOM_DAMAGE and kaboom is not None:
                self._read(state, "before_whittle", extra={"card": KABOOM,
                                                           "ehp": ehp})
                return self._play(state, kaboom, KABOOM,
                                  "whittle toward one-hit range")
            self._read(state, "before_end_turn", extra={"ehp": ehp,
                                                        "bombed": bombed})
            return self._end(state)

        # control arm: bomb at full strength, then a non-lethal blow.
        if bombed and ehp > KABOOM_DAMAGE and kaboom is not None:
            self._read(state, "before_blow", extra={"card": KABOOM,
                                                    "ehp": ehp})
            self.blow_done = True
            return self._play(state, kaboom, KABOOM,
                              "the NON-lethal blow on the bombed target")
        if not bombed and ehp > KABOOM_DAMAGE and pop is not None:
            self._read(state, "before_bomb", extra={"card": POP, "ehp": ehp})
            return self._play(state, pop, POP,
                              "place the bomb (skill; not a hit)")
        self._read(state, "before_end_turn", extra={"ehp": ehp,
                                                    "bombed": bombed})
        return self._end(state)

    def _play(self, state: dict, index: int, name: str, why: str) -> Decision:
        action = policy_v1._play(state, index, target_id=self.target_id)
        return Decision(
            available=True, category="probe", revision="probe_e",
            action=action, label=f"FIXED SCRIPT: play {name}",
            rationale=why, notes={"probe": "e", "arm": self.arm,
                                  "card": name, "target": self.target_id})

    def _end(self, state: dict) -> Decision:
        return Decision(
            available=True, category="probe", revision="probe_e",
            action={"action": "end_turn"}, label="FIXED SCRIPT: end turn",
            rationale="no scripted verb available this reading",
            notes={"probe": "e", "arm": self.arm})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="probe (e) — corpse detonation")
    ap.add_argument("--arm", choices=("kill", "control"), required=True)
    ap.add_argument("--seed", default=None, help="chosen run seed (P1.5)")
    ap.add_argument("--max-fights", type=int, default=1)
    ap.add_argument("--turns", type=int, default=12,
                    help="scripted rounds before combat is handed back to "
                         "policy_v1 so the fight can actually end")
    ap.add_argument("--no-setup", action="store_true")
    ap.add_argument("--out", default="", help="probe reading JSONL")
    args = ap.parse_args(argv)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    readings: list[dict] = []
    out = args.out or str(soak.LOG_DIR / f"probe-e-{args.arm}-{stamp}.jsonl")
    soak.LOG_DIR.mkdir(parents=True, exist_ok=True)

    session = soak.Session(stamp, do_setup=not args.no_setup, intent="")
    real = soak.policy_v1
    summary: dict[str, Any] = {}
    with open(out, "w", encoding="utf-8") as fh:
        scripted = ScriptedPolicy(args.arm, readings, fh, args.turns)
        soak.policy_v1 = scripted        # the ONLY seam; restored in `finally`
        try:
            session.setup()
            driver = soak.RunDriver(session, 1, stamp,
                                    character=CHARACTER,
                                    max_fights=args.max_fights,
                                    chosen_seed=args.seed)
            summary = driver.run()
        finally:
            soak.policy_v1 = real
            session.teardown()

    print(json.dumps({"arm": args.arm, "stamp": stamp,
                      "turns_scripted": args.turns,
                      "readings": len(readings), "out": out,
                      "run": summary}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
