"""P2, leg one: capture the HARD STATES, and nothing else yet.

WHAT R94 SETTLED, AND WHAT IT DELIBERATELY DID NOT

[USER] amended Phase 2's default on the evidence (R94, `Ruling 2` of the
understudy countersign package, 2026-08-04). The pre-registered fallback was
"sample draft picks only"; the Phase-0 run measured that draft is where the
cheap policy and the LLM ALREADY AGREE MOST (60%) and that sequencing carries
all the disagreement (28% on independent turn-openers), so sampling draft
would spend the budget where it helps least.

    **Amended default: hard-state turn sampling.** The LLM tier engages at
    turn-openings in flagged hard states -- cheap triggers computable from
    the wire, e.g. incoming above a set fraction of HP, more than one enemy
    alive, or lethal within reach. One state read plans the whole turn (the
    117-of-167 finding: planned steps are nearly free). Draft sampling is
    dropped from the default and remains available as an option. **The
    trigger thresholds are P2 design work, not set here.**

That last sentence is why this file exists in the shape it does. The ruling
names the SHAPE of a trigger and explicitly leaves the NUMBERS open. So:

  * the sampling leg is built, and it CAPTURES ONLY -- no model is called
    from the game loop, by anyone, ever, on this leg. A soak that phones an
    API mid-run is a soak whose wall-clock and whose failure modes are not
    the ones R98 validated;
  * the thresholds below are a PLACEHOLDER, marked as such in this file and
    stamped into every record they produce, so no capture can later be
    mistaken for one taken under a ratified definition;
  * they are deliberately CONSERVATIVE -- each one is set where a human would
    not argue that the state is hard -- because the failure a placeholder can
    actually cause is a corpus of states nobody agrees were hard, and an
    over-tight trigger that under-samples is recoverable by re-running while
    an over-loose one quietly poisons the corpus;
  * the proposal that would replace them is written up for [USER] rather
    than settled here (`review/active/p2-hard-state-thresholds-2026-08-13.md`).

THE FLAG. Off unless a soak passes `--p2-capture`. Capture costs one extra
`policy_v0` evaluation per sampled turn opening and a JSON write; the baseline
arm R98 validated is the arm without it, and it stays that way.

GUARDRAIL-7 IS UNCHANGED BY EVERY LINE OF THIS. A capture is a record of what
a bot saw and what two heuristics wanted. It is not evidence about balance,
difficulty, fun or legibility, and a count of hard states is a count of states
that tripped THESE thresholds -- not a measurement of how hard the game is.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from understudy import adapter, policy_v0, policy_v1

LOG_DIR = Path(__file__).resolve().parent / "logs" / "p2"

# ---------------------------------------------------------------------------
# PLACEHOLDER THRESHOLDS -- NOT RATIFIED. R94 left these to P2 design work and
# they have not been through [USER]. Every record carries `definition` below
# so a corpus can be filtered by the definition that produced it.
# ---------------------------------------------------------------------------

DEFINITION = "placeholder-conservative-2026-08-13"

#: Incoming damage on the enemies' next turn, as a fraction of CURRENT HP.
#: 0.35 rather than R94's unstated number: a turn that can cost a third of
#: what you have left is one nobody would call routine, and the Klee soak's
#: own floors sit at 8-18 incoming against 62 max, so this fires on the
#: fights that actually threaten rather than on every second turn.
HARD_INCOMING_FRACTION = 0.35

#: More than one enemy alive is R94's second named trigger. Kept at its
#: literal reading (two or more) because it is the one trigger the ruling
#: states without a free parameter.
HARD_MIN_ENEMIES = 2

#: "Lethal within reach": some single enemy's remaining HP is at or below
#: this multiple of the best single attack the hand can throw. 1.0 would be
#: "can kill it with one card"; 1.5 admits the two-card line, which is where
#: the sequencing disagreement the ruling is aimed at actually lives.
HARD_LETHAL_REACH = 1.5

#: Player HP at or below this fraction of max. NOT one of R94's three named
#: triggers -- it is added here because a low-HP turn opening is the state
#: whose mistakes end runs, and it is flagged separately in every record so
#: it can be dropped without touching the other three.
HARD_LOW_HP_FRACTION = 0.30

#: "Deal 9 damage", "Deal 5 damage to ALL enemies" -- the number
#: immediately before the word `damage`.
_CARD_DAMAGE_RE = re.compile(r"(\d+)\s+damage", re.IGNORECASE)

COMBAT_STATES = ("monster", "elite", "boss")


def _enemies(state: dict[str, Any]) -> list[dict]:
    b = state.get("battle") or {}
    out = []
    for e in (b.get("enemies") or state.get("enemies") or []):
        if not isinstance(e, dict):
            continue
        if int(e.get("hp") or 0) > 0:
            out.append(e)
    return out


def _incoming(enemies: list[dict]) -> int:
    """Declared incoming for the enemies' next turn.

    Parsed by `understudy.adapter._intent`, NOT by a reader written here. The
    number is not a numeric field on the wire at all -- it is in the intent's
    printed LABEL ("7", "7 x 3") -- and the adapter's docstring calls getting
    that wrong "the single most consequential thing this adapter can get
    wrong". A trigger with its own second parser would be a second chance to
    get it wrong, disagreeing silently with the policy it is sampling.
    """
    total = 0
    for e in enemies:
        for beat in adapter._intent(e.get("intents") or e.get("intent")):
            if beat.get("kind") == "attack":
                total += int(beat.get("amount") or 0) * int(beat.get("times") or 1)
    return total


def _best_attack(state: dict[str, Any]) -> int:
    """The largest single attack number printed on a card in hand, or 0.

    Read off the DESCRIPTION, because that is where the wire puts it (there
    is no `damage` field on a card row, the same way there is none on an
    intent). Deliberately crude: this is a TRIGGER, not a valuation, and
    reaching into the sim's damage model here would make it a second scorer
    that could disagree with the one the policy actually uses.
    """
    best = 0
    for c in ((state.get("player") or {}).get("hand") or []):
        if not isinstance(c, dict) or str(c.get("type")) != "Attack":
            continue
        for m in _CARD_DAMAGE_RE.finditer(str(c.get("description") or "")):
            best = max(best, int(m.group(1)))
    return best


def triggers(state: dict[str, Any]) -> dict[str, Any]:
    """Which placeholder triggers this state trips, and the numbers behind."""
    p = state.get("player") or {}
    hp = int(p.get("hp") or 0)
    max_hp = max(1, int(p.get("max_hp") or 1))
    enemies = _enemies(state)
    incoming = _incoming(enemies)
    best = _best_attack(state)
    weakest = min((int(e.get("hp") or 0) for e in enemies), default=0)

    fired = {
        "incoming_over_hp_fraction": bool(hp) and incoming >= HARD_INCOMING_FRACTION * hp,
        "multiple_enemies": len(enemies) >= HARD_MIN_ENEMIES,
        "lethal_within_reach": bool(best) and bool(weakest)
                               and weakest <= HARD_LETHAL_REACH * best,
        "low_hp": hp <= HARD_LOW_HP_FRACTION * max_hp,
    }
    return {"fired": [k for k, v in fired.items() if v],
            "all": fired,
            "numbers": {"hp": hp, "max_hp": max_hp, "incoming": incoming,
                        "enemies_alive": len(enemies),
                        "best_attack_in_hand": best,
                        "weakest_enemy_hp": weakest}}


def is_hard(state: dict[str, Any]) -> bool:
    return bool(triggers(state)["fired"])


class Sampler:
    """One soak's worth of captures. Owned by the driver, one per run.

    Fires at TURN OPENINGS only, which is R94's word: the first decision of a
    combat round. One state read plans the whole turn, so sampling every card
    play would buy near-duplicate states at full price.
    """

    def __init__(self, stamp: str, run_index: int, enabled: bool = False):
        self.enabled = enabled
        self.stamp = stamp
        self.run_index = run_index
        self.path = LOG_DIR / f"p2-{stamp}-run{run_index:03d}.jsonl"
        self.seen_turns: set = set()
        self.n_openings = 0
        self.n_captured = 0

    def _key(self, state: dict[str, Any]) -> tuple:
        run = state.get("run") or {}
        b = state.get("battle") or {}
        return (run.get("act"), run.get("floor"), b.get("round"))

    def maybe_capture(self, state: dict[str, Any], memo: policy_v1.Memo,
                      decision: Any = None, seed: str | None = None) -> None:
        """Capture this state if it is a fresh turn opening AND hard."""
        if not self.enabled:
            return
        if str(state.get("state_type")) not in COMBAT_STATES:
            return
        key = self._key(state)
        if key[2] is None or key in self.seen_turns:
            return
        self.seen_turns.add(key)
        self.n_openings += 1
        trig = triggers(state)
        if not trig["fired"]:
            return

        # policy_v0 is the FROZEN counterfactual and stays frozen: it is
        # evaluated here, never edited, because the comparison the LLM tier
        # will eventually be graded against is three-way (v0, v1, model) and
        # the two heuristic legs have to be recorded at the same state.
        try:
            v0 = policy_v0.counterfactual(state)
            v0_row = {"label": v0.label, "action": v0.action,
                      "category": v0.category, "available": v0.available,
                      "rationale": v0.rationale}
        except Exception as e:                                # noqa: BLE001
            v0_row = {"error": f"{type(e).__name__}: {e}"}

        d = decision if decision is not None else policy_v1.decide(state, memo)
        v1_row = {"label": d.label, "action": d.action, "category": d.category,
                  "available": d.available, "revision": d.revision,
                  "rationale": d.rationale}

        rec = {
            "record": "p2_hard_state",
            "leg": "capture_only",
            "definition": DEFINITION,
            "definition_status": "PLACEHOLDER -- not ratified; R94 left the "
                                 "trigger thresholds to P2 design work",
            "thresholds": {
                "HARD_INCOMING_FRACTION": HARD_INCOMING_FRACTION,
                "HARD_MIN_ENEMIES": HARD_MIN_ENEMIES,
                "HARD_LETHAL_REACH": HARD_LETHAL_REACH,
                "HARD_LOW_HP_FRACTION": HARD_LOW_HP_FRACTION},
            "guardrail": "Guardrail-7: a capture records what a bot saw and "
                         "what two heuristics wanted. It is not evidence "
                         "about balance, difficulty, fun or legibility.",
            "stamp": self.stamp, "run": self.run_index, "seed": seed,
            "act": key[0], "floor": key[1], "round": key[2],
            "triggers": trig,
            "policy_v0": v0_row,
            "policy_v1": v1_row,
            # The whole wire state, because the point of the corpus is that a
            # model can be shown exactly what the bot was shown. Trimming it
            # now would make the corpus a function of today's guess about
            # what matters.
            "state": state,
            "ts": time.time(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.n_captured += 1

    def summary(self) -> dict:
        return {"enabled": self.enabled, "definition": DEFINITION,
                "turn_openings_seen": self.n_openings,
                "hard_states_captured": self.n_captured,
                "path": str(self.path) if self.n_captured else None}


__all__ = ["Sampler", "triggers", "is_hard", "DEFINITION", "LOG_DIR"]
