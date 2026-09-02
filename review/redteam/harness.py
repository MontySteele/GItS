#!/usr/bin/env python3
"""S13 replay harness: execute candidate exploit lines through tier0, verbatim.

READ-ONLY with respect to the repo. A line is a JSON object:

{
  "line_id": "unique_string",
  "character": "klee" | "furina" | "kokomi" | ...,
  "deck": ["card_id", ...],                # full deck list, duplicates allowed
  "upgraded": ["card_id", ...],            # optional: ALL copies of these ids upgraded
  "relics": ["relic_id", ...],             # optional: tier05 relic pool ids
  "potions": ["potion_id", ...],           # optional
  "encounter_id": "...",                   # from tier0 content encounters
  "seed": 0,
  "script": [                              # index = turn-1; plays in order
    ["card_a", "card_b"],
    [{"repeat": ["card_c", "card_d"], "times": 40}],
    "auto:N"                               # OR: let a greedy filler play any playable
  ],                                       #     card up to N plays this turn
  "script_default": "pass" | "auto:N",     # turns beyond script length (default pass)
  "claim": {
    "kind": "infinite",                    # engine degeneracy event must fire
    OR "kind": "stall",                    # nobody can finish: the engine's
                                           # no-progress detector fired, OR
                                           # the fight hit MAX_TURNS -- with
                                           # both sides still alive (EB-256)
    OR "kind": "metric", "metric": "...", "op": ">=", "value": N, "turn": T(optional)
  }
}

metric names: damage_dealt_total, hp_left, turns, won, block_gained_total,
  cards_played_in_turn (needs "turn"), damage_in_turn (needs "turn"),
  energy_spent_in_turn (needs "turn"), damage_dealt_by_turn (cumulative, needs "turn")

VERDICT: verified = (script executed with zero misses OR the only shortfall is an
engine degeneracy break) AND claim holds. Misses (scripted card absent from hand /
not playable) are recorded verbatim for diagnostics.
"""
import json, random, sys, traceback

sys.path.insert(0, "/home/user/GItS")

from tier0 import constants as C
from tier0.content import loader
from tier0.content import upgrades as upg
from tier0.engine import combat as combat_mod
from tier0.engine.combat import run_fight, card_playable
from tier0.harness import metrics as metrics_mod


def _resolve_relics(ids, character):
    if not ids:
        return None
    from tier05 import relics as t5relics
    combat_eff, _run_eff = t5relics.split_effects(list(ids), character)
    return combat_eff


def _expand_turn(spec):
    """Turn spec -> ('list', [ids]) or ('auto', N) or ('pass', 0)."""
    if spec is None:
        return ("pass", 0)
    if isinstance(spec, str):
        if spec.startswith("auto:"):
            return ("auto", int(spec.split(":", 1)[1]))
        if spec == "pass":
            return ("pass", 0)
        return ("list", [spec])
    out = []
    for item in spec:
        if isinstance(item, dict) and "repeat" in item:
            out.extend(list(item["repeat"]) * int(item.get("times", 1)))
        else:
            out.append(item)
    return ("list", out)


class ScriptPilot:
    def __init__(self, line):
        self.script = line.get("script", [])
        self.default = line.get("script_default", "pass")
        self.misses = []          # {"turn": t, "card": id, "reason": ...}
        self.plays = []           # {"turn": t, "card": id}
        self._turn_seen = None
        self._queue = None
        self._mode = None
        self._auto_left = 0

    def _load_turn(self, state):
        t = state.turn
        spec = self.script[t - 1] if t - 1 < len(self.script) else self.default
        mode, payload = _expand_turn(spec)
        self._mode = mode
        if mode == "list":
            self._queue = list(payload)
        elif mode == "auto":
            self._auto_left = payload
        self._turn_seen = t

    def __call__(self, state):
        if self._turn_seen != state.turn:
            self._load_turn(state)
        hand = state.player.hand
        if self._mode == "pass":
            return None
        if self._mode == "auto":
            if self._auto_left <= 0:
                return None
            for c in hand:
                if card_playable(state, c):
                    self._auto_left -= 1
                    self.plays.append({"turn": state.turn, "card": c.id})
                    return c
            return None
        # list mode: strict order
        while self._queue:
            want = self._queue.pop(0)
            cand = [c for c in hand if c.id == want]
            if not cand:
                self.misses.append({"turn": state.turn, "card": want,
                                    "reason": "not_in_hand"})
                continue
            playable = [c for c in cand if card_playable(state, c)]
            if not playable:
                self.misses.append({"turn": state.turn, "card": want,
                                    "reason": "not_playable"})
                continue
            self.plays.append({"turn": state.turn, "card": want})
            return playable[0]
        return None


def _metric(name, turn, state, stats, pilot):
    log = state.log
    if name == "damage_dealt_total":
        return stats.total_damage_dealt
    if name == "hp_left":
        return max(0, state.player.hp)
    if name == "turns":
        return state.turn
    if name == "won":
        return int(bool(state.player.alive) and not state.living_enemies)
    if name == "block_gained_total":
        return stats.total_block_gained
    if name == "cards_played_in_turn":
        return sum(1 for p in pilot.plays if p["turn"] == turn)
    if name == "damage_in_turn":
        return stats.damage_by_turn.get(turn, 0)
    if name == "damage_dealt_by_turn":
        return sum(v for t, v in stats.damage_by_turn.items() if t <= turn)
    if name == "energy_spent_in_turn":
        spent = 0
        for ev in log:
            if ev.get("event") == "play" and ev.get("turn") == turn:
                spent += ev.get("cost", 0) or 0
        return spent
    raise ValueError(f"unknown metric {name}")


_OPS = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b,
        "<=": lambda a, b: a <= b, "<": lambda a, b: a < b,
        "==": lambda a, b: a == b}


def run_line(line):
    lid = line.get("line_id", "?")
    try:
        loader.reset_caches()
        char = line["character"]
        deck_ids = list(line["deck"])
        player = loader.build_player_from_ids(
            char, deck_ids,
            relic_effects=_resolve_relics(line.get("relics"), char),
            potions=list(line.get("potions") or []),
        )
        upgraded = set(line.get("upgraded") or [])
        if upgraded:
            player.draw_pile = [
                upg.apply_upgrade(c) if c.id in upgraded else c
                for c in player.draw_pile]
        enemies = loader.build_encounter(line["encounter_id"])
        hp_start = player.hp
        pilot = ScriptPilot(line)
        state = run_fight(player, enemies, pilot, seed=int(line.get("seed", 0)))
        stats = metrics_mod.extract(state, hp_start)
        degen = [ev for ev in state.log if ev.get("event") == "degeneracy"]
        claim = line["claim"]
        kind = claim["kind"]
        observed = {}
        if kind == "infinite":
            holds = bool(degen)
            observed = {"degeneracy_events": degen,
                        "max_plays_in_a_turn": max(
                            [sum(1 for p in pilot.plays if p["turn"] == t)
                             for t in range(1, state.turn + 1)] or [0])}
        elif kind == "stall":
            # EB-256: a stall is "the fight ended with nobody able to finish
            # it", and there are now TWO ways out of one -- the turn cap, and
            # the engine's own no-progress detector, which ends a frozen fight
            # around round 11 instead of letting it grind to 30. The claim
            # asked for the cap because the cap was the only exit that
            # existed; asking for either keeps the ledger's meaning exactly
            # and stops a detected stall from reading as "the exploit is
            # fixed". `stall_softlock_3` is the line that moved.
            holds = ((bool(getattr(state, "stalled", False))
                      or state.turn >= C.MAX_TURNS)
                     and bool(state.player.alive) and bool(state.living_enemies))
            observed = {"turns": state.turn, "player_alive": bool(state.player.alive),
                        "enemies_alive": len(state.living_enemies),
                        "detected_stall": bool(getattr(state, "stalled", False))}
        elif kind == "metric":
            val = _metric(claim["metric"], claim.get("turn"), state, stats, pilot)
            holds = _OPS[claim["op"]](val, claim["value"])
            observed = {claim["metric"]: val}
        else:
            raise ValueError(f"unknown claim kind {kind}")
        executed = not pilot.misses
        # An engine degeneracy break is a successful execution for infinite claims
        # (the engine cut the loop; the script beyond the cut is not a miss).
        return {"line_id": lid, "ok": True,
                "executed": executed, "misses": pilot.misses,
                "plays_made": len(pilot.plays),
                "claim_holds": bool(holds),
                "verified": bool(executed and holds),
                "observed": observed,
                "degeneracy_events": degen,
                "fight": {"won": bool(stats.won), "turns": state.turn,
                          "hp_left": max(0, state.player.hp),
                          "damage_dealt_total": stats.total_damage_dealt}}
    except Exception:
        return {"line_id": lid, "ok": False, "verified": False,
                "error": traceback.format_exc(limit=4)}


def main():
    src = sys.argv[1]
    with open(src) as f:
        data = json.load(f)
    lines = data if isinstance(data, list) else [data]
    out = [run_line(l) for l in lines]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    text = json.dumps(out, indent=1, default=str)
    if dst:
        with open(dst, "w") as f:
            f.write(text)
        vc = sum(1 for r in out if r.get("verified"))
        ec = sum(1 for r in out if not r.get("ok"))
        print(f"{len(out)} lines: {vc} verified, {ec} errored -> {dst}")
    else:
        print(text)


if __name__ == "__main__":
    main()
