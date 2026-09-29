"""The Nahida paper sim's pilot -- an INSTRUMENT, not an optimiser.

Exploratory and switched off with `nahida_seeds.NAHIDA_PAPER`; nothing else
imports it. It follows the generic pilot's shape (`policy.make_pilot`: a
lethal check, a panic-block rule, then the best-scoring card) so its numbers
sit next to the other kits' generic-pilot numbers, and it adds only what the
new verbs need. Every heuristic is stated here so the report can name it:

  1. LETHAL: a card whose estimated damage covers every enemy's HP and Block
     is played at once.
  2. PANIC BLOCK: incoming >= 40% of HP (`C.BLOCK_PANIC_THRESHOLD`, the
     generic pilot's) and not yet blocked -> the biggest blocker.
  3. SCORE = damage now + 1.2 x the Block that prevents incoming damage
     (the generic pilot's weights) + SEED VALUE + REACTION VALUE + POWER
     VALUE + 2 per card drawn - 0.1 x cost. The best score above zero plays.
     * SEED VALUE: each Seed a card places is worth 2 per Seed x (the Purify
       cards still playable this turn + `FUTURE_PURIFIES` = 1.5), halved on
       an enemy at 10 HP or less, zero past the cap. Akasha's free Seed
       counts on the first placement.
     * PURIFY: its damage now, per seeded enemy, capped at the enemy's HP.
     * REACTION VALUE: a hit that will react on its aim pays the reaction's
       own rough size (Bloom's Core 6, Burning 6, Quicken 3, Burgeon 6 per
       enemy, Hyperbloom 12, an amplifier half the hit) and, if the aim is
       seeded and the turn's trigger is open, the Purification it fires.
     * POWER VALUE: 10 on turn 1, falling by 1 a turn (floor 0), the
       generic pilot's "setup decays late-fight" idea.
  4. THE AIM (the decision under test):
     * a card that Seeds its target aims by the PLACEMENT POLICY:
         spread   -- the enemy with the fewest Seeds (ties: most HP);
         deep     -- stack on the biggest threat: the enemy with the most
                     Seeds under the cap (ties: most HP), so it starts on the
                     biggest body and stays there until the cap;
         attacker -- stack on the enemy whose intent hits hardest this turn
                     (ties: most Seeds, then most HP).
       Akasha's second Seed goes to the policy's pick among the others.
     * an elemental hit (her Attacks paint Dendro; a companion paints its
       own element) aims where it REACTS on a seeded enemy while the trigger
       is open, else where it pops a Core, else a companion paints an
       unmarked seeded enemy (priming the next Dendro hit), else lowest HP.
     * Sprout aims at the lowest-HP seeded enemy; everything else keeps the
       engine's lowest-HP aim.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import dendro, nahida_seeds as ns, powers
from tier0.engine.combat import card_cost, card_playable
from tier0.pilot import policy as generic

POLICIES = ("spread", "deep", "attacker")
FUTURE_PURIFIES = 1.5
BLOCK_W = 1.2
COST_W = 0.1
DRAW_VALUE = 2.0
POWER_VALUE_T1 = 10.0

_REACTS = {
    # (hit element, standing aura) -> reaction, Dendro's pairs and the
    # shipped ones a Tri-Karma deck meets.
    ("dendro", "hydro"): "bloom", ("hydro", "dendro"): "bloom",
    ("dendro", "electro"): "quicken", ("electro", "dendro"): "quicken",
    ("dendro", "pyro"): "burning", ("pyro", "dendro"): "burning",
    ("pyro", "hydro"): "vaporize", ("hydro", "pyro"): "vaporize",
    ("pyro", "electro"): "overload", ("electro", "pyro"): "overload",
    ("hydro", "electro"): "electrocharged",
    ("electro", "hydro"): "electrocharged",
}
_REACTION_SIZE = {"bloom": 6.0, "burning": 6.0, "quicken": 3.0,
                  "overload": 6.0, "electrocharged": 4.0}


def enemy_incoming(state, e) -> float:
    """What this enemy's intent deals this turn, Foresight included."""
    if not e.alive or e.sleep_turns > 0:
        return 0.0
    intent = e.current_intent()
    if intent["kind"] != "attack":
        return 0.0
    per_hit = powers.modify_damage_dealt(e, e.ramped_amount(intent, state.turn))
    if e.frozen:
        per_hit *= C.FROZEN_DAMAGE_MULT
    per_hit = int(powers.modify_damage_taken(state.player, per_hit))
    per_hit = max(0, per_hit - ns.power(state, "foresight") * ns.seeds(state, e))
    return float(per_hit * e.ramped_times(intent))


def incoming(state) -> float:
    return sum(enemy_incoming(state, e) for e in state.living_enemies)


def _hit_element(state, card, fx) -> Optional[str]:
    if card.is_companion:
        return card.element if fx.get("applies_element") else None
    if card.character == ns.CHARACTER and card.type == "attack":
        return "dendro"
    return None


def _card_hit_element(state, card) -> Optional[str]:
    for fx in card.effects:
        if fx["op"] in ("damage", "nahida_sprout"):
            el = _hit_element(state, card, {**fx, "applies_element":
                                             fx.get("applies_element", True)})
            if el:
                return el
    return None


def _seeds_target(card) -> Optional[str]:
    for fx in card.effects:
        if fx["op"] == "nahida_seed":
            return fx.get("target", "enemy")
    return None


class NahidaPilot:
    def __init__(self, policy: str = "spread"):
        if policy not in POLICIES:
            raise ValueError(policy)
        self.policy = policy

    # --- placement ---------------------------------------------------------
    def seed_target(self, state, exclude=None):
        cands = [e for e in state.living_enemies
                 if e is not exclude and ns.seeds(state, e) < ns.SEED_CAP]
        if not cands:
            return None
        if self.policy == "spread":
            return min(cands, key=lambda e: (ns.seeds(state, e), -e.hp))
        if self.policy == "deep":
            return max(cands, key=lambda e: (ns.seeds(state, e), e.hp))
        return max(cands, key=lambda e: (enemy_incoming(state, e),
                                         ns.seeds(state, e), e.hp))

    def second_seed_target(self, state, exclude):
        cands = [e for e in state.living_enemies
                 if e is not exclude and ns.seeds(state, e) < ns.SEED_CAP]
        if not cands:
            return None
        if self.policy == "spread":
            return min(cands, key=lambda e: (ns.seeds(state, e), -e.hp))
        if self.policy == "deep":
            return max(cands, key=lambda e: e.hp)
        return max(cands, key=lambda e: (enemy_incoming(state, e), e.hp))

    # --- aim -----------------------------------------------------------------
    def aim(self, state, card):
        living = state.living_enemies
        if not living:
            return None
        if _seeds_target(card) == "enemy":
            t = self.seed_target(state)
            return t if t is not None else min(living, key=lambda e: e.hp)
        if any(fx["op"] == "nahida_sprout" for fx in card.effects):
            seeded = [e for e in living if ns.seeds(state, e)]
            return min(seeded or living, key=lambda e: e.hp)
        el = _card_hit_element(state, card)
        if el and any(fx["op"] in ("damage", "nahida_sprout")
                      and fx.get("target", "enemy") == "enemy"
                      for fx in card.effects):
            open_ = ns.trigger_open(state)
            best = None
            for e in living:
                r = _REACTS.get((el, e.aura)) if e.aura else None
                d = dendro.peek(state, e)
                pops = bool(d and d.cores and el in ("pyro", "electro"))
                key = (bool(r or pops) and ns.seeds(state, e) > 0 and open_,
                       bool(r or pops),
                       card.is_companion and e.aura is None
                       and ns.seeds(state, e) > 0,
                       -e.hp)
                if best is None or key > best[0]:
                    best = (key, e)
            return best[1]
        return None

    # --- valuation -----------------------------------------------------------
    def purify_value(self, state) -> float:
        per = ns.PURIFY_PER_SEED + ns.power(state, "shrine")
        return sum(min(e.hp + e.block, per * ns.seeds(state, e))
                   for e in state.living_enemies if ns.seeds(state, e))

    def _seed_value(self, state, target, n, purifies_left) -> float:
        per = ns.PURIFY_PER_SEED + ns.power(state, "shrine")
        if target is None:
            return 0.0
        room = ns.SEED_CAP - ns.seeds(state, target)
        placed = max(0, min(n, room))
        f = ns.field_of(state)
        if (placed and not f.akasha_used
                and ns.RELIC_HOOK in state.player.relic_hooks
                and len(state.living_enemies) > 1):
            placed += 1
        v = placed * per * (purifies_left + FUTURE_PURIFIES)
        return v * (0.5 if target.hp <= 10 else 1.0)

    def _reaction_value(self, state, card, aim, hit) -> float:
        el = _card_hit_element(state, card)
        if not el or aim is None:
            return 0.0
        r = _REACTS.get((el, aim.aura)) if aim.aura else None
        d = dendro.peek(state, aim)
        v = 0.0
        if d and d.cores and el == "pyro":
            r, v = r or "burgeon", v + dendro.CORE_BURST * len(state.living_enemies)
        elif d and d.cores and el == "electro":
            r, v = r or "hyperbloom", v + dendro.CORE_BURST * dendro.HYPERBLOOM_MULT
        if r:
            v += _REACTION_SIZE.get(r, 0.5 * hit)
            if ns.seeds(state, aim) and ns.trigger_open(state):
                v += self.purify_value(state)
        return v

    def score(self, state, card, aim, inc) -> tuple[float, float]:
        """(score, immediate damage) for playing `card` at `aim` now."""
        p = state.player
        cost = card_cost(state, card)
        hand_p = [c for c in p.hand if c is not card
                  and ns.kind(c) == "P" and card_playable(state, c)]
        purifies_left = (len(hand_p)
                         if p.energy - (cost if isinstance(cost, int) else 0) >= 1
                         else 0)
        dmg = raw_block = seedv = powerv = tempo = 0.0
        if card.character == ns.CHARACTER:
            for fx in card.effects:
                op = fx["op"]
                if op == "damage":
                    n = fx["amount"] * fx.get("times", 1)
                    if fx.get("target") == "all_enemies":
                        dmg += sum(min(e.hp + e.block, n)
                                   for e in state.living_enemies)
                    elif aim is not None:
                        dmg += min(aim.hp + aim.block, n)
                elif op == "nahida_sprout":
                    n = fx["seeded"] if (aim and ns.seeds(state, aim)) \
                        else fx["amount"]
                    dmg += min(aim.hp + aim.block, n) if aim else 0
                elif op == "nahida_seed":
                    tgt = fx.get("target", "enemy")
                    if tgt == "enemy":
                        seedv += self._seed_value(state, aim, fx["amount"],
                                                  purifies_left)
                    elif tgt == "all_unseeded":
                        for e in state.living_enemies:
                            if not ns.seeds(state, e):
                                seedv += self._seed_value(state, e, 1,
                                                          purifies_left)
                    else:
                        for e in state.living_enemies:
                            if ns.seeds(state, e):
                                seedv += self._seed_value(state, e, 1,
                                                          purifies_left)
                elif op == "nahida_purify":
                    dmg += self.purify_value(state) * fx.get("times", 1)
                    raw_block += (ns.ROOTED_MIND_BLOCK
                                  * ns.power(state, "rooted_mind")
                                  * fx.get("times", 1))
                elif op == "nahida_perception":
                    raw_block += fx["amount"] + (fx["bonus"]
                                                 if ns.total_seeds(state) else 0)
                elif op == "block":
                    raw_block += fx["amount"]
                elif op == "draw":
                    tempo += DRAW_VALUE * fx["amount"]
                elif op == "nahida_power":
                    powerv += max(0.0, POWER_VALUE_T1 - (state.turn - 1))
        else:
            dmg = generic._expected_damage(state, card)
            raw_block = generic._raw_block(state, card)
        blk = min(raw_block, max(0.0, inc - p.block))
        react = self._reaction_value(state, card, aim, dmg)
        total = (dmg + BLOCK_W * blk + seedv + react + powerv + tempo
                 - COST_W * (cost if isinstance(cost, int) else 0))
        return total, dmg

    # --- the pilot -----------------------------------------------------------
    def __call__(self, state):
        f = ns.field_of(state)
        f.chooser = self
        p = state.player
        playable = [c for c in p.hand if card_playable(state, c)]
        if not playable:
            return None
        inc = incoming(state)
        aims = [self.aim(state, c) for c in playable]
        scored = [self.score(state, c, a, inc) for c, a in zip(playable, aims)]
        remaining = sum(e.hp + e.block for e in state.living_enemies)
        for c, a, (_, d) in zip(playable, aims, scored):
            if d >= remaining:
                ns.aim_card(state, c, a)
                return c
        if (inc >= C.BLOCK_PANIC_THRESHOLD * max(1, p.hp) and p.block < inc):
            blockers = []
            for c, a in zip(playable, aims):
                rb = (generic._raw_block(state, c)
                      if c.character != ns.CHARACTER
                      else sum(fx.get("amount", 0) + fx.get("bonus", 0)
                               * (1 if ns.total_seeds(state) else 0)
                               for fx in c.effects
                               if fx["op"] in ("block", "nahida_perception")))
                if rb > 0:
                    blockers.append((rb, c, a))
            if blockers:
                _, c, a = max(blockers, key=lambda t: t[0])
                ns.aim_card(state, c, a)
                return c
        best_i = max(range(len(playable)), key=lambda i: (scored[i][0], -i))
        if scored[best_i][0] <= 0:
            return None
        if _seeds_target(playable[best_i]) == "enemy":
            # INSTRUMENT ONLY: would the three policies put this Seed on
            # different enemies? The census behind "is placement a decision".
            picks = {id(NahidaPilot(pol).seed_target(state))
                     for pol in POLICIES}
            state.emit("placement_probe", distinct=len(picks),
                       living=len(state.living_enemies))
        ns.aim_card(state, playable[best_i], aims[best_i])
        return playable[best_i]


def make_nahida_pilot(policy: str = "spread") -> NahidaPilot:
    return NahidaPilot(policy)
