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
