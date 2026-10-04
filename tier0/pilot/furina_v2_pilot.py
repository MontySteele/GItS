"""The Furina re-founding slice's pilot -- an INSTRUMENT, not a balance verdict.

`review/active/furina-refounding-2026-10-03.md` sec.9. One greedy pass per
card: every playable card gets a value in damage-equivalent points, divided by
its Energy cost (a 0-cost card counts as half a point of Energy), and the best
card is played while its value is above `PLAY_FLOOR`. A single-card lethal is
played first. The same value model makes the choices INSIDE a card (the
`Decider`): which performer a Cue names, whether Curtain Rise Spends, which
performer Step Forward moves.

THE VALUE MODEL, all in one place so a reader can argue with it:

- Damage is worth its number, capped at what the target has left (+Block).
- Block is worth its number up to this turn's NEED (posted incoming damage,
  less Block held, less the Block the end-of-turn acts will add), and
  `EXCESS_BLOCK` per point past it.
- A Fanfare held is worth `FANFARE` points. Gaining is +, Spending is -.
- A star's end-of-turn price is RESERVED: a Spend that would leave a star on
  stage short is charged that star's act.
- A draw is worth `DRAW` points while there is a card to draw.
- A performer on stage is worth its steady act value per turn, for
  `SEAT_TURNS` turns; a summon that Bows someone adds that Bow and loses the
  leaver's seat value; a walk-on is worth its Bow (free act + 1 Fanfare).
- A Cue is worth the best performer's act right now (a short star: 0).
- Powers: Dress Rehearsal is worth Rehearsal x expected acts left; Thunderous
  Applause is worth one draw per expected Bow left.
- Readers wait: Ousia Surge is held while a playable card would still raise
  this turn's gain, Pneuma Refrain while a playable card would still Spend.
"""

from __future__ import annotations

from typing import Optional

from tier0.engine import furina_v2 as V
from tier0.engine.combat import card_cost, card_playable
from tier0.pilot.policy import _incoming_damage

FANFARE = 1.5          # a Fanfare held, in damage points
DRAW = 2.0             # one card drawn
EXCESS_BLOCK = 0.15    # a Block point past this turn's need
SEAT_TURNS = 2.5       # how long a seated performer is expected to act
STEADY_BLOCK = 0.6     # a performer's Block, valued on an average turn
PLAY_FLOOR = 0.5       # a card worth less than this is not played
EXPECTED_TURNS = 6     # a fight's expected length, for the Powers' value


# ----------------------------------------------------------------------
# Readers of the board.
# ----------------------------------------------------------------------
def _f(state) -> V.Fv2:
    return state.player.fv2


def eot_block(state) -> int:
    """The Block the end-of-turn acts will add (Usher, Sigewinne)."""
    f = _f(state)
    r = f.rehearsal
    total = 0
    for m in f.stage:
        if m == "usher":
            total += V.ACT_USHER_BLOCK + r
        elif m == "sigewinne":
            losses = int(state.player_damage_events) - f.sigewinne_mark
            total += (V.ACT_SIGEWINNE_BLOCK
                      + V.SIGEWINNE_PER_HP_LOSS * max(0, losses) + r)
    return total


def need(state) -> float:
    p = state.player
    return max(0.0, _incoming_damage(state) - p.block - eot_block(state))


def reserve(state) -> int:
    """The Fanfare the stars on stage will pay at the end of this turn."""
    return sum(V.STAR_PRICE[m] for m in _f(state).stage if m in V.STARS)


def _block_value(b: float, need_now: float) -> float:
    return min(b, need_now) + EXCESS_BLOCK * max(0.0, b - need_now)


def _target_left(state) -> float:
    living = state.living_enemies
    if not living:
        return 0.0
    e = min(living, key=lambda x: x.hp)
    return float(e.hp + e.block)


def _single(state, amount: float) -> float:
    return min(amount, _target_left(state))


def act_value(state, member: str, *, free: bool = False,
              need_now: Optional[float] = None, steady: bool = False,
              fanfare: Optional[int] = None) -> float:
    """What one act of `member` is worth now (or, `steady`, on a typical
    turn). A star that cannot pay is worth 0 (it skips)."""
    f = _f(state)
    r = f.rehearsal
    held = f.fanfare if fanfare is None else fanfare
    n = max(1, len(state.living_enemies))
    if need_now is None:
        need_now = need(state)
    price = 0 if free else V.STAR_PRICE.get(member, 0)
    if member in V.STARS and not free and held < price:
        return 0.0
    cost = price * FANFARE
    if member == "usher":
        b = V.ACT_USHER_BLOCK + r
        return STEADY_BLOCK * b if steady else _block_value(b, need_now)
    if member == "chevalmarin":
        return (V.ACT_CHEVALMARIN_DAMAGE + r) * n
    if member == "crabaletta":
        return V.ACT_CRABALETTA_DAMAGE + r
    if member == "neuvillette":
        return (V.ACT_NEUVILLETTE_DAMAGE + r) * n - cost
    if member == "clorinde":
        return V.ACT_CLORINDE_DAMAGE + r - cost
    if member == "escoffier":
        return sum(act_value(state, m, need_now=need_now, steady=steady)
                   for m in f.stage if m in V.SALON) - cost
    if member == "navia":
        spent = f.spent_this_turn
        return float(V.NAVIA_PER_SPENT * spent + r) if spent > 0 else (
            2.0 if steady else 0.0)
    if member == "charlotte":
        return FANFARE * V.CHARLOTTE_GAIN
    if member == "sigewinne":
        losses = int(state.player_damage_events) - f.sigewinne_mark
        b = (V.ACT_SIGEWINNE_BLOCK + V.SIGEWINNE_PER_HP_LOSS * max(0, losses)
             + r)
        return STEADY_BLOCK * b if steady else _block_value(b, need_now)
    return 0.0


def _line_value(state, member: str) -> float:
    """A guest's while-on-stage line, per turn, roughly."""
    if member == "charlotte":
        return DRAW * V.CHARLOTTE_DRAW
    if member == "clorinde":
        return 0.5 * V.CLORINDE_SPEND_DAMAGE
    if member == "escoffier":
        return 1.5
    if member == "neuvillette":
        return 1.0
    return 0.0


def seat_value(state, member: str) -> float:
    steady = act_value(state, member, steady=True, fanfare=99)
    return (steady + _line_value(state, member)) * SEAT_TURNS


def bow_value(state, member: str) -> float:
    f = _f(state)
    return (act_value(state, member, free=True) + FANFARE * V.BOW_FANFARE
            + DRAW * f.thunderous)


def summon_value(state, member: str) -> float:
    f = _f(state)
    if member in V.GUESTS and member in f.stage:
        return bow_value(state, member)
    if len(f.stage) < V.SEATS:
        return seat_value(state, member)
    salon = [m for m in f.stage if m in V.SALON]
    if salon:
        leaver = salon[0]
        return (seat_value(state, member) + bow_value(state, leaver)
                - seat_value(state, leaver))
    if member in V.SALON:
        return bow_value(state, member)            # the walk-on
    leaver = f.stage[0]
    return (seat_value(state, member) + bow_value(state, leaver)
            - seat_value(state, leaver))


def best_cue(state) -> tuple[Optional[int], float]:
    f = _f(state)
    if not f.stage:
        return None, 0.0
    need_now = need(state)
    vals = [(act_value(state, m, need_now=need_now), -i, i)
            for i, m in enumerate(f.stage)]
    v, _neg, i = max(vals)
    return i, v


def _spend_cost(state, amount: int) -> float:
    """What Spending `amount` costs: the Fanfare's value, plus any star
    act this Spend would leave unpaid at the end of the turn; less
    Clorinde's line, which a Spend sets off."""
    f = _f(state)
    left = f.fanfare - amount
    cost = FANFARE * amount
    if left < reserve(state):
        budget = left
        for m in f.stage:
            if m in V.STARS:
                price = V.STAR_PRICE[m]
                if budget >= price:
                    budget -= price
                else:
                    cost += act_value(state, m, fanfare=99)
    if amount > 0 and "clorinde" in f.stage:
        cost -= V.CLORINDE_SPEND_DAMAGE
    return cost


# ----------------------------------------------------------------------
# The Decider: the choices a card asks for while it resolves.
# ----------------------------------------------------------------------
class Decider:
    def cue_target(self, state) -> Optional[int]:
        i, _v = best_cue(state)
        return i

    def curtain_spend(self, state, card, plain: int, big: int,
                      price: int) -> bool:
        left = _target_left(state)
        if big >= left > plain:
            return True                      # the Spend kills, the plain not
        return (_single(state, big) - _spend_cost(state, price)
                > _single(state, plain))

    def front_target(self, state) -> Optional[int]:
        """Step Forward: Charlotte to the front when a star stands before
        her (she then funds it the same turn); else nobody moves."""
        f = _f(state)
        if "charlotte" in f.stage:
            i = f.stage.index("charlotte")
            if any(m in V.STARS for m in f.stage[:i]):
                return i
        return None


DEFAULT_DECIDER = Decider()


# ----------------------------------------------------------------------
# Card values.
# ----------------------------------------------------------------------
def _gains_fanfare(state, card) -> bool:
    spec = V.spec_of(card)
    if spec is None:
        return False
    return spec.kind == "gain" or (spec.kind == "guest" and V.numbers(card)[0])


def _spends(state, card) -> bool:
    spec = V.spec_of(card)
    if spec is None:
        return False
    f = _f(state)
    if spec.kind == "bravura":
        return f.fanfare > 0
    if spec.kind == "curtain_rise":
        return f.fanfare >= V.numbers(card)[1]
    return False


def _base_value(state, card) -> tuple[float, float]:
    """(damage, block) of a non-slice card (base Strike / Defend)."""
    dmg = blk = 0.0
    for fx in card.effects:
        if fx.get("op") == "damage":
            dmg += float(fx.get("amount", 0)) * fx.get("times", 1)
        elif fx.get("op") == "block":
            blk += float(fx.get("amount", 0))
    return dmg, blk


def card_damage(state, card) -> float:
    """The single-target damage a card would deal now (lethal check)."""
    spec = V.spec_of(card)
    if spec is None:
        return _base_value(state, card)[0]
    f = _f(state)
    n = V.numbers(card)
    k = spec.kind
    if k == "curtain_rise":
        return float(n[2] if f.fanfare >= n[1] else n[0])
    if k in ("damage_cue", "summon_damage"):
        return float(n[0])
    if k == "ousia":
        return float(n[0] + n[1] * f.gained_this_turn)
    if k == "bravura":
        return float(n[0] + n[1] * f.fanfare)
    return 0.0


def value(state, card, playable: list) -> float:
    spec = V.spec_of(card)
    need_now = need(state)
    if spec is None:
        dmg, blk = _base_value(state, card)
        return _single(state, dmg) + _block_value(blk, need_now)
    f = _f(state)
    n = V.numbers(card)
    k = spec.kind
    draws_left = bool(state.player.draw_pile or state.player.discard_pile)
    others = [c for c in playable if c is not card]
    if k == "curtain_rise":
        plain, price, big = n
        v = _single(state, plain)
        if f.fanfare >= price:
            v = max(v, _single(state, big) - _spend_cost(state, price))
        return v
    if k == "gain":
        return FANFARE * n[0] + _reader_bonus(state, others, gained=n[0])
    if k == "take_the_stage":
        sv = sum(summon_value(state, m) for m in V.SALON) / len(V.SALON)
        return sv + (DRAW * n[0] if draws_left else 0.0)
    if k == "summon_block":
        return summon_value(state, spec.member) + _block_value(n[0], need_now)
    if k == "hydro_summon":
        return summon_value(state, spec.member) + 1.0
    if k == "summon_damage":
        bonus = (V.NEUVILLETTE_HYDRO_BONUS if "neuvillette" in f.stage
                 else 0)
        return summon_value(state, spec.member) + _single(state, n[0] + bonus)
    if k == "damage_cue":
        return _single(state, n[0]) + best_cue(state)[1]
    if k == "block_cue":
        return _block_value(n[0], need_now) + best_cue(state)[1]
    if k == "cue_draw":
        return best_cue(state)[1] + (DRAW * n[0] if draws_left else 0.0)
    if k == "step_forward":
        move = 0.5 if DEFAULT_DECIDER.front_target(state) is not None else 0
        return _block_value(n[0], need_now) + move
    if k == "ousia":
        v = _single(state, n[0] + n[1] * f.gained_this_turn)
        if any(_gains_fanfare(state, c) for c in others) and (
                state.player.energy >= card_cost(state, card) + 1):
            v *= 0.3                          # a gain is still to come
        return v
    if k == "pneuma":
        v = _block_value(n[0] + n[1] * f.spent_this_turn, need_now)
        if any(_spends(state, c) for c in others) and (
                state.player.energy >= card_cost(state, card) + 1):
            v *= 0.3                          # a Spend is still to come
        return v
    if k == "bravura":
        pts = f.fanfare
        v = _single(state, n[0] + n[1] * pts) - (
            _spend_cost(state, pts) if pts else 0.0)
        return v
    if k == "thunderous":
        turns_left = max(1, EXPECTED_TURNS - state.turn)
        return DRAW * 0.6 * turns_left
    if k == "rehearsal":
        turns_left = max(1, EXPECTED_TURNS - state.turn)
        acts = max(1.5, len(f.stage) + 0.5)
        return n[0] * acts * turns_left * 0.8
    if k == "guest":
        return summon_value(state, spec.member) + FANFARE * n[0] + (
            _reader_bonus(state, others, gained=n[0]) if n[0] else 0.0)
    if k == "block":
        return _block_value(n[0], need_now)
    return 0.0


def _reader_bonus(state, others, *, gained: int) -> float:
    """A gain played before Ousia Surge raises it this turn."""
    bonus = 0.0
    for c in others:
        spec = V.spec_of(c)
        if spec is not None and spec.kind == "ousia":
            bonus = max(bonus, V.numbers(c)[1] * gained)
    return bonus


def pilot(state):
    playable = [c for c in state.player.hand if card_playable(state, c)]
    if not playable:
        return None
    left = sum(e.hp + e.block for e in state.living_enemies)
    if len(state.living_enemies) == 1:
        for c in playable:
            if card_damage(state, c) >= left:
                return c
    best, best_key = None, None
    for i, c in enumerate(playable):
        v = value(state, c, playable)
        if v < PLAY_FLOOR:
            continue
        key = (v / max(0.5, card_cost(state, c)), v, -i)
        if best_key is None or key > best_key:
            best, best_key = c, key
    return best
