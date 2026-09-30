"""The Varka Oath rework's pilot: an INSTRUMENT, not an optimiser.

Two element policies; everything else is shared, so a gap between them is
the element decision.

  * "focused" (`home` = the starting Knight's element): plays only Knights
    of `home`, so the current element never changes. Off-element Knights are
    dead cards to it.
  * "juggling": each time it chooses a Knight it plays the one whose element
    the board NEEDS, ranked afresh before every card, whatever Oath it has
    banked:
      - Hydro when unblocked incoming damage is at least 10 (Swirls pay
        Block, Barbara paints everyone);
      - Electro when three or more enemies stand (Swirls pay 2 to ALL);
      - Cryo when one enemy stands with 60 HP or more (Vulnerable);
      - otherwise it KEEPS the current element (no need, no switch).
    A Knight whose element is neither needed nor current is held (before
    the first Knight, any Knight will do). A need it holds no Knight for
    falls to the next in the order.

Shared rules, asked afresh before every card:
  0. LETHAL on the last enemy (Ascension estimated at 6 + 3 x Oath).
  1. POWERS (Oath of the Knights, Sworn Brotherhood, Stormward Stance,
     Boreas Unbound, Converging Winds). Tailwind Stride next when 2+ Energy
     remain.
  2. DANGER: unblocked incoming >= a quarter of HP -> best block first.
  3. MOVERS: Rally to the Banner when Oath outside the current element >= 3;
     Four Winds' Accord when it would raise the current element's Oath.
  4. PAINT: a Knight the policy allows (Grand Master's Order first if in
     hand). Aim: an enemy that is clean or already wears that element (both
     gain Oath), lowest HP among those that survive the hit.
     Favonius Drill counts as a paint when a current element is set.
  5. SWIRL: an Anemo Attack on an enemy wearing a FRESH aura (Windbound when
     two or more enemies are fresh, Gale Sweep likewise; else best damage per
     Energy). Wall of Gales when two or more auras are fresh and Block is
     needed.
  6. ASCENSION once a current element is set (it cycles, so it is never
     held back): aimed at a fresh aura if one stands (its Anemo hit Swirls
     first), else at an enemy wearing the current element, else lowest HP.
  7. BLOCK up to incoming (best Block per Energy: Eye of the Storm at 2 per
     Oath, Wind Wall, Favonius Drill, Defend, Wall of Gales). (Headwind,
     cut from the pool, is still played if a test hands it over.)
  8. ATTACK (best damage per Energy); 9. anything left that helps.
"""

from __future__ import annotations

from tier0.engine import varka_oath as O
from tier0.engine import varka_paper as V
from tier0.engine.combat import card_playable, card_cost

POLICIES = ("focused", "juggling")


def _incoming(state) -> float:
    from tier0.pilot.policy import _incoming_damage
    return _incoming_damage(state)


def _per_enemy_incoming(state):
    from tier0.engine.varka_paper_pilot import _incoming_from
    return {id(e): _incoming_from(state, e) for e in state.living_enemies}


def _fresh(e) -> bool:
    return bool(e.aura) and not e.aura_spent


def _base(card) -> str:
    return card.id[len("varka_"):] if card.id.startswith("varka_") else card.id


class VarkaOathPilot:
    def __init__(self, policy: str = "focused", home: str = "pyro"):
        assert policy in POLICIES, policy
        self.policy = policy
        self.home = home

    # -- estimates --------------------------------------------------------
    def _asc_est(self, state, vs):
        return (O.ASC_BASE + O.ASC_PER_OATH * O.current_oath(vs)
                + state.player.powers.get("strength", 0))

    def _dmg_est(self, state, vs, card) -> float:
        b = _base(card)
        if b == "four_winds_ascension":
            return self._asc_est(state, vs)
        bonus = (O.attack_bonus(state, vs, card) if card.type == "attack"
                 else 0) + state.player.powers.get("strength", 0)
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
                        total += inner["amount"] * inner.get("times", 1)
            elif fx.get("op") == "varka_oath":
                k, n = fx["kind"], O.current_oath(vs)
                fr = sum(1 for e in state.living_enemies if _fresh(e))
                if k == "oathsworn":
                    total += fx["base"] + n + bonus
                elif k == "azure":
                    total += fx["per"] * n
                elif k == "northwind":
                    total += fx["anemo"] + fx["elem"] + fx["per"] * n + bonus
                elif k == "storm_surge":
                    total += ((fx["amount"] + bonus)
                              * len(state.living_enemies)
                              + (fx["more"] + 2) * fr)
        return total

    def _block_est(self, state, vs, card) -> int:
        b = _base(card)
        if b in ("eye_of_the_storm", "eye_of_the_storm_x"):
            return 2 * O.current_oath(vs)
        if b == "knightly_guard":
            return 8
        if b == "jean":
            return 7
        if b == "tailwind_guard":
            return 3 * sum(1 for v in vs.oath.values() if v > 0)
        if b == "change_of_guard":
            return O.current_oath(vs)
        if b == "wind_wall":
            return 7 + (3 if vs.current else 0)
        if b == "favonius_drill":
            return 6
        if b == "wall_of_gales":
            return 16
        n = 0
        for fx in card.effects:
            if fx.get("op") == "block":
                n += fx["amount"]
        return n

    # -- element choice ---------------------------------------------------
    def _need_order(self, state, vs, playable, cost):
        if self.policy == "focused":
            return [self.home]
        p = state.player
        inc = _per_enemy_incoming(state)
        attackers = [v for v in inc.values() if v > 0]
        unblocked = max(0.0, sum(attackers) - p.block)
        order = []
        living = state.living_enemies
        if unblocked >= 10:
            order.append("hydro")
        if len(living) >= 3:
            order.append("electro")
        if len(living) == 1 and living[0].hp >= 60:
            order.append("cryo")
        if vs.current and vs.current not in order:
            order.append(vs.current)
        if vs.current is None:
            # no element yet: any Knight will do, Pyro first
            for el in ("pyro", "hydro", "cryo", "electro"):
                if el not in order:
                    order.append(el)
        # An element that is neither needed nor current is not played:
        # juggling switches for a reason, never for a spare Knight.
        return order

    def _allowed_knights(self, state, vs, playable, cost):
        knights = [(c, O.knight_element(c)) for c in playable
                   if O.knight_element(c) in O.ELEMENTS]
        if not knights:
            return []
        order = self._need_order(state, vs, playable, cost)
        rank = {el: i for i, el in enumerate(order)}
        ok = [(c, el) for c, el in knights if el in rank]
        ok.sort(key=lambda t: (rank[t[1]], -self._dmg_est(state, vs, t[0])))
        return ok

    def _paint_target(self, state, element, hit):
        living = state.living_enemies
        good = [e for e in living if e.aura is None or e.aura == element]
        for pool in ([e for e in good if e.hp + e.block > hit], good):
            if pool:
                return min(pool, key=lambda e: e.hp)
        return min(living, key=lambda e: e.hp)

    def _play(self, vs, card, aim=None):
        if _base(card) == "change_of_guard" and vs.cog_choice is None:
            vs.cog_choice = vs.current       # as a Block card: stay put
        vs.playing = card
        vs.aim = aim
        return card

    # -- the policy ---------------------------------------------------------
    def __call__(self, state):
        p = state.player
        vs = p.varka
        vs.playing = None
        vs.aim = None
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
        fresh = [e for e in living if _fresh(e)]
        by = {}
        for c in playable:
            by.setdefault(_base(c), []).append(c)

        def has(name):
            return by.get(name, [None])[0]

        # 0. lethal on the last enemy
        if len(living) == 1:
            e = living[0]
            killers = [c for c in attacks
                       if self._dmg_est(state, vs, c) >= e.hp + e.block
                       and not (_base(c) == "gale_sweep" and not _fresh(e))]
            if killers:
                return self._play(vs, min(killers, key=lambda c: cost[id(c)]),
                                  e)

        # 1. powers, then Tailwind
        for c in playable:
            if c.type == "power":
                return self._play(vs, c)
        c = has("tailwind_stride")
        if c is not None and energy - cost[id(c)] >= 1:
            return self._play(vs, c)

        # 2. danger
        if need >= 0.25 * max(1, p.hp):
            c = self._best_block(state, vs, playable, cost)
            if c is not None:
                return self._play(vs, c, self._drill_aim(state, vs))

        # 3. movers
        if vs.current:
            cur = O.current_oath(vs)
            total = sum(vs.oath.values())
            c = has("rally_to_the_banner")
            if c is not None and total - cur >= 3:
                return self._play(vs, c)
            c = has("four_winds_accord")
            if c is not None and total // 4 + 1 > cur:
                return self._play(vs, c)
        # R4 Change of Guard, the juggler's switch without a Knight: to the
        # element the board needs, when banked Oath is there and no Knight of
        # it is in hand.
        c = has("change_of_guard")
        if c is not None and self.policy == "juggling" and vs.current:
            top = self._need_order(state, vs, playable, cost)[0]
            held = any(O.knight_element(k) == top for k in playable)
            if top != vs.current and vs.oath.get(top, 0) > 0 and not held:
                vs.cog_choice = top
                return self._play(vs, c)

        # 4. paint
        knights = self._allowed_knights(state, vs, playable, cost)
        if knights:
            gmo = has("grand_masters_order")
            if gmo is not None:
                return self._play(vs, gmo)
            c, el = knights[0]
            tgt = self._paint_target(state, el, self._dmg_est(state, vs, c))
            if vs.gmo_pending:
                vs.aim2 = tgt
            return self._play(vs, c, tgt)
        c = has("favonius_drill")
        if c is not None and vs.current:
            return self._play(vs, c, self._drill_aim(state, vs))

        # 5. swirl
        if fresh:
            c = has("jean")
            if c is not None:
                return self._play(vs, c, min(fresh, key=lambda e: e.hp))
            if len(fresh) >= 2:
                for name in ("windbound_execution", "gale_sweep",
                             "storm_surge"):
                    c = has(name)
                    if c is not None:
                        return self._play(vs, c)
                c = has("wall_of_gales")
                if c is not None and need > 0:
                    return self._play(vs, c)
            sw = [c for c in attacks if c.element == V.ELEMENT
                  and _base(c) != "four_winds_ascension"]
            if sw:
                c = max(sw, key=lambda c: self._dmg_est(state, vs, c)
                        / max(1, cost[id(c)]))
                return self._play(vs, c, min(fresh, key=lambda e: e.hp))

        # 5b. R4 Unfurled Banner: Ascension back from the discard pile
        c = has("unfurled_banner")
        if (c is not None and vs.current and O.current_oath(vs) >= 3
                and any(x.id == "varka_four_winds_ascension"
                        for x in p.discard_pile)):
            return self._play(vs, c)

        # 6. Ascension
        c = has("four_winds_ascension")
        if c is not None and vs.current:
            if fresh:
                tgt = min(fresh, key=lambda e: e.hp)
            else:
                wear = [e for e in living if e.aura == vs.current]
                tgt = min(wear or living, key=lambda e: e.hp)
            return self._play(vs, c, tgt)

        # 7. block
        if need > 0:
            inc = _per_enemy_incoming(state)
            c = has("headwind")
            if c is not None and max(inc.values() or [0]) >= 8:
                tgt = max(living, key=lambda e: inc[id(e)])
                if not tgt.powers.get("weak", 0):
                    return self._play(vs, c, tgt)
            c = self._best_block(state, vs, playable, cost)
            if c is not None:
                return self._play(vs, c, self._drill_aim(state, vs))

        # 8. attack
        cand = [c for c in attacks
                if not (_base(c) == "gale_sweep" and not fresh)
                and not (_base(c) == "four_winds_ascension"
                         and not vs.current)]
        if cand:
            c = max(cand, key=lambda c: self._dmg_est(state, vs, c)
                    / max(1, cost[id(c)]))
            return self._play(vs, c)
        c = has("four_winds_ascension")
        if c is not None:
            return self._play(vs, c)

        # 9. leftovers that help
        for name in ("headwind", "knights_roll_call"):
            c = has(name)
            if c is not None:
                return self._play(vs, c)
        c = self._best_block(state, vs, playable, cost)
        if c is not None:
            return self._play(vs, c, self._drill_aim(state, vs))
        return None

    def _drill_aim(self, state, vs):
        if not vs.current:
            return None
        living = state.living_enemies
        good = [e for e in living if e.aura is None or e.aura == vs.current]
        return min(good or living, key=lambda e: e.hp)

    def _best_block(self, state, vs, playable, cost):
        best, score = None, 0.0
        for c in playable:
            if c.type != "skill" or O.knight_element(c):
                continue
            b = self._block_est(state, vs, c)
            if b <= 0:
                continue
            s = b / max(1, cost[id(c)])
            if s > score:
                best, score = c, s
        return best
