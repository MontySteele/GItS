"""The Varka paper arm's pilot: an INSTRUMENT, not an optimiser.

A fixed priority list, asked afresh before every card (the engine's pilot
contract: `(state) -> Card | None`). Heuristics, in order:

  0. LETHAL: against the last enemy, the cheapest Attack whose estimate kills.
  1. POWERS first (Converging Winds, Stormward Stance, Sturm und Drang).
  2. ASCENSION when the Winds held reach `threshold` (the switch Q2 asks for:
     2 = fire early, 3 = wait; 4 = hoard), or when its estimate kills its
     target outright (the "or fight end" clause).
  3. DANGER: if the unblocked incoming damage is at least a quarter of HP,
     block before the engine.
  4. ABSORB: an enemy wears a FRESH aura. Prefer an aura whose Wind is not
     held. If the Fang is unused this turn, spend the cheapest plain Attack on
     it (never an Absorb card or Ascension, which the Fang makes redundant);
     else an Absorb card.
  5. PAINT: a Knight (or Muster) whose Wind is not held, Grand Master's Order
     first when one is in hand. Aim (`aim` switch): "smart" paints a CLEAN
     enemy (no aura), else one already wearing that element, else the lowest
     HP; "naive" leaves the engine's default aim (lowest HP). Muster picks
     the first element not held, in the order Pyro, Hydro, Electro, Cryo.
     In GALE mode a Knight paints even when its Wind is held (Swirls, not
     Winds, are the plan there), aimed the same way.
  6. BLOCK up to the unblocked incoming damage.
  7. ATTACK: best estimated damage per Energy (Gale Sweep only with a fresh
     aura on the board; Ascension held back under rule 2).
  8. Anything left that helps: Knights as damage, Lisa's draw, Defends.
"""

from __future__ import annotations

from tier0.engine import varka_paper as V
from tier0.engine.combat import card_playable, card_cost


def _incoming(state) -> float:
    from tier0.pilot.policy import _incoming_damage
    return _incoming_damage(state)


def _fresh(e) -> bool:
    return bool(e.aura) and not e.aura_spent


def _is(card, name) -> bool:
    return card.id == f"varka_{name}"


def _est_attack(state, vs, card) -> float:
    """Printed damage plus the arm's flat riders; for ranking only."""
    bonus = V.attack_bonus(state, card) if card.type == "attack" else 0
    bonus += state.player.powers.get("strength", 0)
    if _is(card, "four_winds_ascension"):
        return V.ASCENSION_BASE + V.ASCENSION_PER_WIND * len(vs.winds) + bonus
    total = 0.0
    for fx in card.effects:
        if fx.get("op") == "damage":
            total += (fx["amount"] + bonus) * fx.get("times", 1)
        elif fx.get("op") == "varka" and fx["kind"] == "gale_sweep":
            n = sum(1 for e in state.living_enemies if _fresh(e))
            total += (fx["amount"] + bonus + 2) * n
        elif fx.get("op") == "varka" and fx["kind"] == "knight":
            for inner in fx["inner"]:
                if inner.get("op") == "damage":
                    total += inner["amount"]
    return total


def _block_of(state, vs, card) -> int:
    n = 0
    for fx in card.effects:
        if fx.get("op") == "block":
            n += fx["amount"]
        elif fx.get("op") == "varka" and fx["kind"] == "wind_wall":
            n += fx["amount"] + (fx["bonus"] if vs.winds else 0)
        elif fx.get("op") == "varka" and fx["kind"] == "knight":
            n += sum(i.get("amount", 0) for i in fx["inner"]
                     if i.get("op") == "block")
    return n


def _knight_element(card):
    for fx in card.effects:
        if fx.get("op") == "varka" and fx["kind"] == "knight":
            return fx["element"]
    return None


class VarkaPilot:
    def __init__(self, threshold: int = 3, aim: str = "smart",
                 gale: bool = False):
        self.threshold = threshold
        self.aim = aim
        self.gale = gale

    # -- helpers --------------------------------------------------------
    def _paint_target(self, state, element, hit=6):
        """Smart: a clean enemy that survives the Knight's hit (lowest HP of
        those), else any clean one, else one already wearing the element,
        else the lowest HP."""
        living = state.living_enemies
        if self.aim == "naive":
            return None                    # the engine's lowest-HP bind
        for pool in ([e for e in living if e.aura is None
                      and e.hp + e.block > hit],
                     [e for e in living if e.aura is None],
                     [e for e in living if e.aura == element]):
            if pool:
                return min(pool, key=lambda e: e.hp)
        return min(living, key=lambda e: e.hp)

    def _hand_row(self, state, vs):
        """Q5: the turn's opening hand, before any card is played."""
        p = state.player
        knight = any(c.id in V.KNIGHT_IDS for c in p.hand)
        fresh = any(_fresh(e) for e in state.living_enemies)
        vs.turn_rows.append({"turn": state.turn, "knight": knight,
                             "fresh": fresh,
                             "strike_turn": not knight and not fresh,
                             "winds": len(vs.winds)})

    def _play(self, vs, card, aim=None):
        vs.playing = card
        vs.aim = aim
        return card

    # -- the policy ------------------------------------------------------
    def __call__(self, state):
        p = state.player
        vs = p.varka
        vs.playing = None
        vs.aim = None
        if not vs.turn_rows or vs.turn_rows[-1]["turn"] != state.turn:
            self._hand_row(state, vs)
        living = state.living_enemies
        if not living:
            return None
        playable = [c for c in p.hand if card_playable(state, c)]
        if not playable:
            return None
        cost = {id(c): card_cost(state, c) for c in playable}
        attacks = [c for c in playable if c.type == "attack"]
        need = max(0.0, _incoming(state) - p.block)

        # 0. lethal on the last enemy
        if len(living) == 1:
            e = living[0]
            killers = [c for c in attacks
                       if _est_attack(state, vs, c) >= e.hp + e.block
                       and not (_is(c, "gale_sweep") and not _fresh(e))]
            if killers:
                return self._play(vs, min(killers,
                                          key=lambda c: cost[id(c)]), e)

        # 1. powers
        for c in playable:
            if c.type == "power":
                return self._play(vs, c)

        # 2. Ascension
        asc = [c for c in attacks if _is(c, "four_winds_ascension")]
        if asc:
            c = asc[0]
            est = _est_attack(state, vs, c)
            target = min(living, key=lambda e: e.hp)
            if (len(vs.winds) >= self.threshold
                    or est >= target.hp + target.block):
                return self._play(vs, c, target)

        # 3. danger: block first
        if need >= 0.25 * max(1, p.hp):
            c = self._best_block(state, vs, playable)
            if c is not None:
                return self._play(vs, c)

        # 4. absorb a fresh aura
        fresh = [e for e in living if _fresh(e)]
        if fresh:
            wanted = [e for e in fresh if e.aura not in vs.winds] or fresh
            tgt = min(wanted, key=lambda e: e.hp)
            fang_ready = vs.fang_turn != state.turn
            if fang_ready:
                plain = [c for c in attacks
                         if c.id not in V.ABSORB_IDS
                         and not _is(c, "four_winds_ascension")
                         and not (self.gale and _is(c, "gale_sweep"))]
                if plain:
                    return self._play(vs, min(
                        plain, key=lambda c: (cost[id(c)],
                                              -_est_attack(state, vs, c))),
                        tgt)
            if self.gale:
                sweep = [c for c in attacks if _is(c, "gale_sweep")]
                if sweep:
                    return self._play(vs, sweep[0])
            if not self.gale or not fang_ready:
                absorbers = [c for c in attacks if c.id in V.ABSORB_IDS]
                if absorbers and (tgt.aura not in vs.winds or self.gale):
                    return self._play(vs, min(absorbers,
                                              key=lambda c: cost[id(c)]), tgt)
            if self.gale:
                anemo = [c for c in attacks if c.element == V.ELEMENT
                         and not _is(c, "four_winds_ascension")]
                if anemo:
                    return self._play(vs, max(
                        anemo, key=lambda c: _est_attack(state, vs, c)), tgt)

        # 5. paint
        knights = [c for c in playable if c.id in V.KNIGHT_IDS]
        missing = [el for el in V.WIND_ELEMENTS if el not in vs.winds]
        paint = []
        for c in knights:
            el = _knight_element(c)
            if el == "choose":
                if missing or self.gale:
                    paint.append((c, missing[0] if missing else "pyro"))
            elif el not in vs.winds or self.gale:
                paint.append((c, el))
        if paint:
            gmo = [c for c in playable if _is(c, "grand_masters_order")]
            if gmo:
                return self._play(vs, gmo[0])
            # a named Knight before Muster, so Muster keeps its choice
            paint.sort(key=lambda t: _knight_element(t[0]) == "choose")
            c, el = paint[0]
            if _knight_element(c) == "choose":
                vs.muster_choice = el
            return self._play(vs, c, self._paint_target(
                state, el, _est_attack(state, vs, c)))

        # 6. block
        if need > 0:
            c = self._best_block(state, vs, playable)
            if c is not None:
                return self._play(vs, c)

        # 7. attack
        cand = [c for c in attacks
                if not _is(c, "four_winds_ascension")
                and not (_is(c, "gale_sweep") and not fresh)]
        if cand:
            c = max(cand, key=lambda c: _est_attack(state, vs, c)
                    / max(1, cost[id(c)]))
            return self._play(vs, c)

        # 8. leftovers
        for c in playable:
            if c.id in V.KNIGHT_IDS:
                return self._play(vs, c)
        for c in playable:
            if _block_of(state, vs, c) > 0:
                return self._play(vs, c)
        return None

    def _best_block(self, state, vs, playable):
        blockers = [c for c in playable if _block_of(state, vs, c) > 0
                    and c.id not in V.KNIGHT_IDS]
        if not blockers:
            return None
        return max(blockers, key=lambda c: _block_of(state, vs, c))


# ==========================================================================
#  REVISION TWO (paper sec.9): Absorb is optional and is not a Swirl
# ==========================================================================

ABSORB_POLICIES = ("absorb", "swirl", "smart")


def _incoming_from(state, e) -> float:
    """`policy._incoming_damage` for one enemy."""
    from tier0 import constants as C
    from tier0.engine import powers
    if e.sleep_turns > 0 or not e.alive:
        return 0.0
    intent = e.current_intent()
    if intent["kind"] != "attack":
        return 0.0
    per_hit = powers.modify_damage_dealt(e, e.ramped_amount(intent,
                                                             state.turn))
    if e.frozen:
        per_hit *= C.FROZEN_DAMAGE_MULT
    per_hit = powers.modify_damage_taken(state.player, per_hit)
    return int(per_hit) * intent.get("times", 1)


def _asc_est(state, vs) -> float:
    per = (V.ASCENSION_B_PER_WIND if vs.asc_version == "B"
           else V.ASCENSION_PER_WIND)
    return (V.ASCENSION_BASE + per * len(vs.winds)
            + state.player.powers.get("strength", 0))


class VarkaPilot2:
    """Revision two's pilot: an INSTRUMENT with a switchable Absorb policy.

    The three policies differ ONLY in whether a fresh aura whose Wind is not
    held gets Absorbed (rule 4) and in what a Knight paints for (rule 5);
    every other rule is shared, so a gap between them is the Absorb decision.
      * "absorb" (a): Absorb whenever a new Wind is on the board.
      * "swirl"  (b): never Absorb (the Fang is always declined; an Absorb
        card is aimed away from fresh auras it would take).
      * "smart"  (c): Absorb when the Wind is new AND (a Knight is still in
        hand with the Energy to follow it this turn, OR fewer than 2 Winds are
        held -- "early"); otherwise Swirl.
    Shared rules, asked afresh before every card:
      0. LETHAL on the last enemy (Fang declined: a Swirl pays more).
      1. POWERS.
      2. ASCENSION: Winds held >= `threshold`; else the PREVENT-LETHAL clause
         (the unblocked incoming is at least current HP, and killing one
         enemy brings it below); else the KILL clause (its estimate kills the
         lowest-HP enemy). Each fire records its reason.
      3. DANGER: unblocked incoming >= a quarter of HP -> block first.
      4. ABSORB (policy-gated), via the Fang on the cheapest non-Anemo plain
         Attack when the Fang is ready, else an Absorb card.
      5. PAINT BEFORE SWIRL (the sec.9.4 rule of thumb, all policies): a
         Knight with a reason to paint -- a new Wind with an Absorb to follow
         (policies a/c), or a Swirl card in hand -- is played before any
         Swirl, if the Energy covers both. Target: a clean enemy that
         survives the hit, else one already wearing the element.
      6. SWIRL: an Anemo Attack on a fresh aura (Gale Sweep first when two or
         more are fresh; Windbound only on a held Wind's aura). Fang declined.
      7. BLOCK up to incoming; 8. ATTACK (best damage per Energy); 9. rest.
    """

    def __init__(self, policy: str = "smart", threshold: int = 3):
        assert policy in ABSORB_POLICIES, policy
        self.policy = policy
        self.threshold = threshold

    # -- helpers ---------------------------------------------------------
    def _play(self, vs, card, aim=None, fang=False, reason=None):
        vs.playing = card
        vs.aim = aim
        vs.fang_want = fang
        vs.asc_reason = reason
        return card

    def _paint_target(self, state, element, hit, exclude=()):
        living = [e for e in state.living_enemies if e not in exclude]
        if not living:
            living = state.living_enemies
        for pool in ([e for e in living if e.aura is None
                      and e.hp + e.block > hit],
                     [e for e in living if e.aura is None],
                     [e for e in living if e.aura == element]):
            if pool:
                return min(pool, key=lambda e: e.hp)
        return min(living, key=lambda e: e.hp)

    def _wants_absorb(self, vs, playable, cost, energy):
        if self.policy == "swirl" or vs.no_gain:
            return False
        if self.policy == "absorb":
            return True
        # smart: a Knight to follow this turn, or early (< 2 Winds)
        knights = [c for c in playable if c.id in V.KNIGHT_IDS]
        follow = any(energy - 1 >= cost[id(c)] for c in knights)
        return follow or len(vs.winds) < 2

    # -- the policy ------------------------------------------------------
    def __call__(self, state):
        p = state.player
        vs = p.varka
        vs.playing = None
        vs.aim = None
        vs.fang_want = False
        vs.asc_reason = None
        if not vs.turn_rows or vs.turn_rows[-1]["turn"] != state.turn:
            knight = any(c.id in V.KNIGHT_IDS for c in p.hand)
            fresh0 = any(_fresh(e) for e in state.living_enemies)
            vs.turn_rows.append({"turn": state.turn, "knight": knight,
                                 "fresh": fresh0,
                                 "strike_turn": not knight and not fresh0,
                                 "winds": len(vs.winds)})
        living = state.living_enemies
        if not living:
            return None
        playable = [c for c in p.hand if card_playable(state, c)]
        if not playable:
            return None
        cost = {id(c): card_cost(state, c) for c in playable}
        energy = p.energy
        attacks = [c for c in playable if c.type == "attack"]
        need = max(0.0, _incoming(state) - p.block)
        fresh = [e for e in living if _fresh(e) and e.aura in V.WIND_ELEMENTS]

        def is_asc(c):
            return _is(c, "four_winds_ascension")

        # 0. lethal on the last enemy
        if len(living) == 1:
            e = living[0]
            killers = []
            for c in attacks:
                est = (_asc_est(state, vs) if is_asc(c)
                       else _est_attack(state, vs, c))
                if _is(c, "gale_sweep") and not _fresh(e):
                    continue
                if est >= e.hp + e.block:
                    killers.append(c)
            if killers:
                c = min(killers, key=lambda c: cost[id(c)])
                return self._play(vs, c, e,
                                  reason="kill" if is_asc(c) else None)

        # 1. powers
        for c in playable:
            if c.type == "power":
                return self._play(vs, c)

        # 2. Ascension
        asc = [c for c in attacks if is_asc(c)]
        if asc:
            c = asc[0]
            est = _asc_est(state, vs)
            if len(vs.winds) >= self.threshold:
                tgt = max(living, key=lambda e: e.hp)
                return self._play(vs, c, tgt, reason="threshold")
            if need >= p.hp:
                saves = [e for e in living if est >= e.hp + e.block
                         and need - _incoming_from(state, e) < p.hp]
                if saves:
                    return self._play(vs, c, max(
                        saves, key=lambda e: _incoming_from(state, e)),
                        reason="prevent_lethal")
            tgt = min(living, key=lambda e: e.hp)
            if est >= tgt.hp + tgt.block:
                return self._play(vs, c, tgt, reason="kill")

        # 3. danger: block first
        if need >= 0.25 * max(1, p.hp):
            c = self._best_block(state, vs, playable)
            if c is not None:
                return self._play(vs, c)

        # 4. absorb (policy-gated)
        new = ([e for e in fresh if e.aura not in vs.winds]
               if not vs.no_gain else [])
        if new and self._wants_absorb(vs, playable, cost, energy):
            tgt = min(new, key=lambda e: e.hp)
            if vs.fang_turn != state.turn:
                plain = [c for c in attacks
                         if c.id not in V.ABSORB_IDS and not is_asc(c)
                         and not _is(c, "gale_sweep")]
                if plain:
                    c = min(plain, key=lambda c: (c.element == V.ELEMENT,
                                                  cost[id(c)],
                                                  -_est_attack(state, vs, c)))
                    return self._play(vs, c, tgt, fang=True)
            absorbers = [c for c in attacks if c.id in V.ABSORB_IDS]
            if absorbers:
                return self._play(vs, min(absorbers,
                                          key=lambda c: cost[id(c)]), tgt)

        # 5. paint before swirl
        knights = [c for c in playable if c.id in V.KNIGHT_IDS]
        missing = ([el for el in V.WIND_ELEMENTS if el not in vs.winds]
                   if not vs.no_gain else [])
        absorb_means = bool(self.policy != "swirl" and missing and (
            (vs.fang_turn != state.turn and any(
                c.id not in V.ABSORB_IDS and not is_asc(c)
                and not _is(c, "gale_sweep") for c in attacks))
            or any(c.id in V.ABSORB_IDS for c in attacks)))
        swirl_cards = [c for c in attacks if not is_asc(c) and (
            _is(c, "gale_sweep") or (c.element == V.ELEMENT
                                     and c.id not in V.ABSORB_IDS))]
        paint = []
        for c in knights:
            el = _knight_element(c)
            rest = energy - cost[id(c)]
            follow_swirl = any(cost[id(s)] <= rest for s in swirl_cards)
            follow_absorb = absorb_means and rest >= 1
            if el == "choose":
                if missing and follow_absorb:
                    paint.append((c, missing[0], 0))
                elif follow_swirl:
                    paint.append((c, (missing or ["pyro"])[0], 1))
            elif el in missing and follow_absorb:
                paint.append((c, el, 0))
            elif follow_swirl:
                paint.append((c, el, 1))
        if paint:
            gmo = [c for c in playable if _is(c, "grand_masters_order")]
            if gmo:
                return self._play(vs, gmo[0])
            # new-Wind paints first, a named Knight before Muster
            paint.sort(key=lambda t: (t[2],
                                      _knight_element(t[0]) == "choose"))
            c, el, _ = paint[0]
            hit = _est_attack(state, vs, c)
            tgt = self._paint_target(state, el, hit)
            if vs.gmo_pending:
                if _knight_element(c) == "choose":
                    rest_missing = [m for m in missing if m != el]
                    vs.muster_choice2 = (rest_missing[0] if rest_missing
                                         else el)
                vs.aim2 = self._paint_target(state, el, hit, exclude=(tgt,))
            if _knight_element(c) == "choose":
                vs.muster_choice = el
            return self._play(vs, c, tgt)

        # 6. swirl
        sw = []
        for c in attacks:
            if is_asc(c):
                continue
            if _is(c, "gale_sweep"):
                if fresh:
                    sw.append((c, None))
                continue
            if c.element != V.ELEMENT:
                continue
            targets = fresh
            if c.id in V.ABSORB_IDS:
                targets = ([e for e in fresh if e.aura in vs.winds]
                           if V.ABSORB_HELD_SWIRLS and not vs.no_gain else [])
            if targets:
                sw.append((c, min(targets, key=lambda e: e.hp)))
        if sw:
            sweep = [t for t in sw if _is(t[0], "gale_sweep")]
            if sweep and len(fresh) >= 2:
                return self._play(vs, sweep[0][0])
            c, tgt = max(sw, key=lambda t: _est_attack(state, vs, t[0])
                         / max(1, cost[id(t[0])]))
            return self._play(vs, c, tgt)

        # 7. block
        if need > 0:
            c = self._best_block(state, vs, playable)
            if c is not None:
                return self._play(vs, c)

        # 8. attack
        cand = [c for c in attacks if not is_asc(c)
                and not (_is(c, "gale_sweep") and not fresh)]
        if cand:
            c = max(cand, key=lambda c: _est_attack(state, vs, c)
                    / max(1, cost[id(c)]))
            aim = None
            if c.id in V.ABSORB_IDS and (self.policy == "swirl"
                                         or vs.no_gain):
                # an Absorb card is not aimed at a fresh aura it would take
                safe = [e for e in living if not _fresh(e)]
                aim = min(safe or living, key=lambda e: e.hp)
            return self._play(vs, c, aim)

        # 9. leftovers
        for c in playable:
            if c.id in V.KNIGHT_IDS:
                el = _knight_element(c)
                if el == "choose":
                    vs.muster_choice = (missing or ["pyro"])[0]
                    el = vs.muster_choice
                return self._play(vs, c, self._paint_target(
                    state, el, _est_attack(state, vs, c)))
        for c in playable:
            if _block_of(state, vs, c) > 0:
                return self._play(vs, c)
        return None

    def _best_block(self, state, vs, playable):
        blockers = [c for c in playable if _block_of(state, vs, c) > 0
                    and c.id not in V.KNIGHT_IDS]
        if not blockers:
            return None
        return max(blockers, key=lambda c: _block_of(state, vs, c))
