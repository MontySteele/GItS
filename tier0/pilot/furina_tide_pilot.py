"""The research slice's pilots -- INSTRUMENTS, not balance verdicts.

`review/active/furina-research-proposal-2026-10-05.md` sec.10. One greedy pass
per card, the shape of `furina_v2_pilot`: every playable card gets a value in
damage-equivalent points divided by its Energy (a 0-cost card counts as half),
and the best is played while its value is above `PLAY_FLOOR`. A single-card
lethal is played first. The same value model makes the in-card choices (Drain
or not, Spend or not) for the JUDGED pilot.

THE VALUE MODEL:
- Damage is worth its number, capped at what the target has left (+Block);
  AoE sums over living enemies.
- Block is worth its number up to this turn's NEED (posted incoming, less
  Block held), and `EXCESS_BLOCK` per point past it.
- A Fanfare is worth `fanfare_value`: 0.7 x the best per-point rate of the
  outlets in this deck (0.3 with none); `FANFARE` is the flat stand-in the
  guest and Power estimates use.
- An HP point is worth `hp_value`: `HP_BASE` at full HP, rising linearly to
  `HP_LOW` at the half-line (an HP point near the line is worth more because
  it is the last room before Drain closes, and it is real HP).
- A Drain of N is charged: N x hp_value x the share of it the Singer cannot
  repay before the fight ends (estimated from the enemies' HP and this deck's
  damage rate), plus `DRAIN_RISK` per point when the incoming hit is not
  covered, minus N x FANFARE.
- A Restore of N is worth min(N, drained) x (hp_value + FANFARE), plus the
  Restore readers.

THREE PILOTS for the in-card choice: `judged` (the model above), `always`
(Drain and Spend whenever legal) and `never` (never Drain; Spend as judged).
The card choice itself is the same model for all three, so the comparison
isolates the Drain decision.
"""

from __future__ import annotations

from typing import Optional

from tier0.engine import furina_tide as T
from tier0.engine.combat import card_cost, card_playable
from tier0.pilot.policy import _incoming_damage

FANFARE = 1.2
DRAW = 2.0
EXCESS_BLOCK = 0.15
PLAY_FLOOR = 0.5
HP_BASE = 0.8
HP_LOW = 2.0
DRAIN_RISK = 0.35
DECK_DAMAGE_PER_TURN = 14.0   # the slice deck's rough damage rate
SEAT_TURNS = 2.5
EXPECTED_TURNS = 6


def _f(state) -> T.Ftd:
    return state.player.ftd


def hp_value(state) -> float:
    p = state.player
    half = T.half_line(p)
    if p.max_hp <= half:
        return HP_LOW
    frac = max(0.0, min(1.0, (p.hp - half) / (p.max_hp - half)))
    return HP_LOW + (HP_BASE - HP_LOW) * frac


def need(state) -> float:
    return max(0.0, _incoming_damage(state) - state.player.block)


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


def _aoe(state, amount: float) -> float:
    return sum(min(amount, e.hp + e.block) for e in state.living_enemies)


def turns_left(state) -> float:
    total = sum(e.hp + e.block for e in state.living_enemies)
    return max(1.0, total / DECK_DAMAGE_PER_TURN)


def unrepaid_share(state, n: int) -> float:
    """The share of a new Drain of N the Singer will not repay before the
    fight ends, given what is already drained."""
    f = _f(state)
    capacity = f.singer * turns_left(state)
    before = max(0.0, f.drained - capacity)
    after = max(0.0, f.drained + n - capacity)
    return (after - before) / n if n else 0.0


def _drain_triggers(state, n: int) -> float:
    f = _f(state)
    v = 0.0
    if f.powers["salon_encore"]:
        v += _aoe(state, T.SALON_ENCORE_DAMAGE * f.powers["salon_encore"])
    if "wriothesley" in f.stage:
        v += n * 0.9
    return v


def _gain_value(state, n: int) -> float:
    f = _f(state)
    mult = 1 + f.powers["revelry"]
    v = fanfare_value(state) * n * mult
    if f.powers["critics_darling"]:
        v += 0.9 * n * mult
    return v


def drain_cost(state, n: int) -> float:
    """What Draining N costs now, net of the Fanfare and triggers it buys."""
    hpv = hp_value(state)
    share = unrepaid_share(state, n)
    exposed = 1.0 if need(state) > 0 else 0.3
    cost = n * hpv * share + DRAIN_RISK * n * exposed
    return cost - _gain_value(state, n) - _drain_triggers(state, n)


def restore_value(state, n: int) -> float:
    f = _f(state)
    amount = min(n, f.drained)
    if amount <= 0:
        return 0.0
    v = amount * hp_value(state) + _gain_value(state, amount)
    if f.powers["endless_waltz"]:
        v += 0.9 * amount
    if "sigewinne" in f.stage:
        v += _block_value(amount, need(state))
    if "clorinde" in f.stage:
        v += 0.9 * T.CLORINDE_PER_RESTORE * amount
    if "charlotte" in f.stage and not f.charlotte_drew:
        v += DRAW
    return v


def _playable_left(state, card=None) -> bool:
    """Is there another card in hand that an extra Energy would play?"""
    p = state.player
    return any(c is not card and card_cost(state, c) > 0
               and card_cost(state, c) <= p.energy + 1
               for c in p.hand)


def _outlet_rate(spec) -> float:
    """Damage-equivalent points per Fanfare one outlet pays."""
    k, n = spec.kind, spec.n
    if k == "block_spend_hit":
        return n[2] / n[1]
    if k in ("spend_aoe", "spend_hit"):
        return (n[2] - n[0]) / n[1]
    if k == "spend_draw":
        return (n[2] - n[0] + DRAW * n[3]) / n[1]
    if k == "spend_energy":
        return 6.0 / n[1]
    if k in ("block_spend_all", "bravura"):
        return float(n[1])
    if k == "rejoice":
        return float(n[0]) * 1.3
    return 0.0


def fanfare_value(state) -> float:
    """A held Fanfare is worth a share of what this deck's best outlet
    pays for it (cached per fight). With no outlet it is worth 0.3."""
    f = _f(state)
    cached = getattr(f, "_fanfare_value", None)
    if cached is not None:
        return cached
    p = state.player
    cards = p.hand + p.draw_pile + p.discard_pile
    rates = [_outlet_rate(T.spec_of(c)) for c in cards if T.spec_of(c)]
    best = max(rates, default=0.0)
    v = 0.3 if best <= 0 else 0.7 * best
    f._fanfare_value = v
    return v


def spend_cost(state, n: int) -> float:
    return fanfare_value(state) * n


# ----------------------------------------------------------------------
# The in-card choices.
# ----------------------------------------------------------------------
class Judged:
    def drain(self, state, card, spec) -> bool:
        plain, price, big = spec.n
        if spec.kind == "drain_block":
            gain = (_block_value(big, need(state))
                    - _block_value(plain, need(state)))
        elif spec.kind == "drain_aoe":
            gain = _aoe(state, big) - _aoe(state, plain)
        else:
            left = _target_left(state)
            if big >= left > plain:
                return True               # the Drain kills, the plain not
            gain = _single(state, big) - _single(state, plain)
        return gain - drain_cost(state, price) > 0

    def spend(self, state, card, spec) -> bool:
        price = spec.n[1]
        if spec.kind == "block_spend_hit":
            gain = _single(state, spec.n[2])
        elif spec.kind == "spend_aoe":
            gain = _aoe(state, spec.n[2]) - _aoe(state, spec.n[0])
        elif spec.kind == "spend_hit":
            gain = _single(state, spec.n[2]) - _single(state, spec.n[0])
        elif spec.kind == "spend_energy":
            gain = 6.0 if _playable_left(state) else 0.0
        else:
            gain = (_single(state, spec.n[2]) - _single(state, spec.n[0])
                    + DRAW * spec.n[3])
        return gain - spend_cost(state, price) > 0


    def spend_all_ok(self, state, rate: int) -> bool:
        pts = _f(state).fanfare
        return _single(state, rate * pts) - spend_cost(state, pts) > 0

    def spend_all(self, state, card, spec) -> bool:
        return self.spend_all_ok(state, spec.n[1])


class Always(Judged):
    def drain(self, state, card, spec) -> bool:
        return True

    def spend(self, state, card, spec) -> bool:
        return True


class Never(Judged):
    def drain(self, state, card, spec) -> bool:
        return False


DECIDERS = {"judged": Judged(), "always": Always(), "never": Never()}
DEFAULT_DECIDER = DECIDERS["judged"]


# ----------------------------------------------------------------------
# Card values (the card choice; same for every decider).
# ----------------------------------------------------------------------
def _base_value(card) -> tuple[float, float]:
    dmg = blk = 0.0
    for fx in card.effects:
        if fx.get("op") == "damage":
            dmg += float(fx.get("amount", 0)) * fx.get("times", 1)
        elif fx.get("op") == "block":
            blk += float(fx.get("amount", 0))
    return dmg, blk


def _guest_value(state, member: str) -> float:
    f = _f(state)
    n = max(1, len(state.living_enemies))
    if member == "charlotte":
        per = 0.6 * (hp_value(state) + FANFARE) * T.CHARLOTTE_ACT_RESTORE + 1.0
    elif member == "sigewinne":
        per = 0.6 * (hp_value(state) + FANFARE) * T.SIGEWINNE_ACT_RESTORE + 2.0
    elif member == "wriothesley":
        per = T.WRIOTHESLEY_ACT + 2.5
    elif member == "clorinde":
        per = T.CLORINDE_ACT + 4.0
    elif member == "neuvillette":
        per = T.NEUVILLETTE_ACT * n + 2.0
    elif member == "navia":
        per = 6.0
    else:
        per = 0.0
    if member in f.stage:
        return per                         # the repeat: one more act
    return per * SEAT_TURNS


def card_damage(state, card) -> float:
    spec = T.spec_of(card)
    if spec is None:
        return _base_value(card)[0]
    f = _f(state)
    n = spec.n
    k = spec.kind
    if k == "drain_hit":
        return float(n[2] if T.can_drain(state, n[1]) else n[0])
    if k == "hit_restore":
        return float(n[0])
    if k == "ousia":
        return float(n[0] + n[1] * f.gained_this_turn)
    if k == "bravura":
        return float(n[0] + n[1] * f.fanfare)
    if k == "block_spend_hit":
        return float(n[2] if f.fanfare >= n[1] else 0)
    if k == "block_spend_all":
        return float(n[1] * f.fanfare)
    if k in ("spend_draw", "spend_hit"):
        return float(n[2] if f.fanfare >= n[1] else n[0])
    return 0.0


def value(state, card, playable: list, decider) -> float:
    spec = T.spec_of(card)
    need_now = need(state)
    if spec is None:
        dmg, blk = _base_value(card)
        return _single(state, dmg) + _block_value(blk, need_now)
    f = _f(state)
    n = spec.n
    k = spec.kind
    others = [c for c in playable if c is not card]
    if k in T.DRAIN_KINDS:
        plain, price, big = n
        if k == "drain_block":
            pv = _block_value(plain, need_now)
            bv = _block_value(big, need_now)
        elif k == "drain_aoe":
            pv, bv = _aoe(state, plain), _aoe(state, big)
        else:
            pv, bv = _single(state, plain), _single(state, big)
        if T.can_drain(state, price) and decider.drain(state, card, spec):
            return bv - drain_cost(state, price)
        return pv
    if k in T.SPEND_KINDS:
        price = n[1]
        if k == "block_spend_hit":
            pv = _block_value(n[0], need_now)
            bv = pv + _single(state, n[2])
        elif k == "spend_aoe":
            pv, bv = _aoe(state, n[0]), _aoe(state, n[2])
        elif k == "spend_hit":
            pv, bv = _single(state, n[0]), _single(state, n[2])
        elif k == "spend_energy":
            draws = bool(state.player.draw_pile or state.player.discard_pile)
            pv = DRAW if draws else 0.0
            bv = pv + (6.0 if _playable_left(state, card) else 0.0)
        else:
            pv = _single(state, n[0])
            bv = _single(state, n[2]) + DRAW * n[3]
        if f.fanfare >= price and decider.spend(state, card, spec):
            return bv - spend_cost(state, price)
        return pv
    if k == "block_spend_all":
        v = _block_value(n[0], need_now)
        pts = f.fanfare
        if pts and decider.spend_all(state, card, spec):
            v += _single(state, n[1] * pts) - spend_cost(state, pts)
        return v
    if k == "hit_restore":
        return _single(state, n[0]) + restore_value(state, n[1])
    if k == "block_restore":
        return _block_value(n[0], need_now) + restore_value(state, n[1])
    if k == "ousia":
        v = _single(state, n[0] + n[1] * f.gained_this_turn)
        if any(T.spec_of(c) and T.spec_of(c).kind in T.DRAIN_KINDS
               for c in others) and state.player.energy >= card_cost(
                   state, card) + 1:
            v *= 0.4                      # a Drain is still to come
        return v
    if k == "bravura":
        pts = f.fanfare
        return _single(state, n[0] + n[1] * pts) - spend_cost(state, pts)
    if k == "rejoice":
        pts = f.fanfare
        if pts <= 0:
            return 0.0
        v = _aoe(state, n[0] * pts) - spend_cost(state, pts)
        return v
    if k == "power":
        tl = max(1, EXPECTED_TURNS - state.turn)
        m = spec.member
        if m == "salon_encore":
            return 0.8 * tl * max(1, len(state.living_enemies)) * 2.0
        if m == "endless_waltz":
            return 0.8 * tl * 3.0
        if m == "revelry":
            return 0.8 * tl * 5.0 * FANFARE
        if m == "critics_darling":
            return 0.8 * tl * 5.0
        if m == "crowd_gasps":
            return 0.8 * tl * 3.0 * FANFARE
    if k == "guest":
        return _guest_value(state, spec.member)
    return 0.0


def _ranked(state, playable: list, decider) -> list:
    keyed = []
    for i, c in enumerate(playable):
        v = value(state, c, playable, decider)
        if v < PLAY_FLOOR:
            continue
        keyed.append(((v / max(0.5, card_cost(state, c)), v, -i), c))
    keyed.sort(key=lambda kc: kc[0], reverse=True)
    return [c for _k, c in keyed]


def _lethal(state, playable: list):
    if len(state.living_enemies) != 1:
        return None
    left = sum(e.hp + e.block for e in state.living_enemies)
    for c in playable:
        if card_damage(state, c) >= left:
            return c
    return None


def make_pilot(name: str):
    decider = DECIDERS[name]

    def pilot(state):
        state.player.ftd.decider = decider
        playable = [c for c in state.player.hand if card_playable(state, c)]
        if not playable:
            return None
        lethal = _lethal(state, playable)
        if lethal is not None:
            return lethal
        ranked = _ranked(state, playable, decider)
        return ranked[0] if ranked else None
    return pilot


PILOTS = {name: make_pilot(name) for name in DECIDERS}
