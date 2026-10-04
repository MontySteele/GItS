"""The research slice's pilots -- INSTRUMENTS, not balance verdicts.

`review/active/furina-research-proposal-2026-10-05.md` sec.10 and sec.16. One
greedy pass per card, the shape of `furina_v2_pilot`: every playable card gets
a value in damage-equivalent points divided by its Energy (a 0-cost card
counts as half), and the best is played while its value is above
`PLAY_FLOOR`. A single-card lethal is played first. The same value model
makes the in-card choices (Drain or not, Spend or not) for the JUDGED pilot,
and the play-or-hold choice on a fixed-price card.

THE VALUE MODEL:
- Damage is worth its number, capped at what the target has left (+Block);
  AoE sums over living enemies.
- Block is worth its number up to this turn's NEED (posted incoming, less
  Block held), and `EXCESS_BLOCK` per point past it.
- A Fanfare is worth `fanfare_value`: 0.7 x the best per-point rate of the
  outlets in this deck (0.3 with none); `FANFARE` is the flat stand-in the
  guest and Power estimates use. A Spend is charged that, less what
  Thunderous Applause pays for it.
- An HP point is worth `hp_value`: `HP_BASE` at full HP, rising linearly to
  `HP_LOW` at the half-line.
- A Drain of N, under the OLD rule (`no_curtain_call`): N x hp_value x the
  share of it the Singer cannot repay before the fight ends (estimated from
  the enemies' HP and this deck's damage rate), plus `DRAIN_RISK` per point
  when the incoming hit is not covered, minus the Fanfare and readers it
  buys.
- A Drain of N under the CURTAIN CALL (sec.16, the default): nothing is
  permanent, since every drained HP returns at the end. It is charged only
  `temp_hp_value` per point: `DRAIN_RISK` when a hit is coming (0.3 of it
  when covered) plus `ROOM_SHARE` of the near-the-line premium
  (hp_value - HP_BASE). ON A KILLING PLAY (`ends_fight`) it is charged
  nothing: no hit lands and the curtain returns the HP.
- A Repay of N is worth min(N, drained) x the same HP value (permanent under
  the old rule, temporary under the curtain call), plus its Fanfare and the
  Repay readers. Under `repay_no_fanfare` the Fanfare term is dropped.
- Under `singer_rests`, the FIRST Drain of a turn also forfeits this turn's
  Singer Repay (`forfeit_cost`); off the switch it is zero.

RISING APPLAUSE ALWAYS SPENDS ALL (sec.15 point 7): its value includes the
spend, good or bad, and the only choice is whether to play it now. Only the
`legacy` variant lets the decider decline (`spend_all`).

THREE PILOTS for the in-card choice: `judged` (the model above), `always`
(Drain and Spend whenever legal; a fixed Drain card is valued without its
cost) and `never` (never Drains: a fixed Drain card is never played; Spend
as judged). The card choice itself is the same model for all three.

THE STALL QUESTION (sec.15 point 3): this pilot cannot express delaying a
kill. It has no plan across turns: damage is valued capped at the target's
HP with no penalty for killing, a single-card lethal is always played first,
and the Singer's future Repays never enter a card's value. It cannot choose
to keep a beaten enemy alive, so the sim cannot measure the incentive.
"""

from __future__ import annotations

from tier0.engine import furina_tide as T
from tier0.engine.combat import card_cost, card_playable
from tier0.pilot.policy import _incoming_damage

FANFARE = 1.2
DRAW = 2.0
NEXT_ENERGY = 5.0             # an Energy next turn, in damage points
EXCESS_BLOCK = 0.15
PLAY_FLOOR = 0.5
HP_BASE = 0.8
HP_LOW = 2.0
DRAIN_RISK = 0.35
ROOM_SHARE = 0.5              # curtain call: the near-the-line premium kept
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


def _exposed(state) -> float:
    return 1.0 if need(state) > 0 else 0.3


def temp_hp_value(state) -> float:
    """Curtain call: one HP point that returns at the fight's end is worth
    only the risk of being low when hit and nearer the line."""
    return (DRAIN_RISK * _exposed(state)
            + ROOM_SHARE * max(0.0, hp_value(state) - HP_BASE))


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


def ends_fight(state, amount: float, aoe: bool = False) -> bool:
    """Would this much card damage kill every enemy left?"""
    living = state.living_enemies
    if not living:
        return False
    if aoe:
        return all(e.hp + e.block <= amount for e in living)
    return len(living) == 1 and _target_left(state) <= amount


def turns_left(state) -> float:
    total = sum(e.hp + e.block for e in state.living_enemies)
    return max(1.0, total / DECK_DAMAGE_PER_TURN)


def singer_capacity(state) -> float:
    """HP the Singer can still repay this fight. Under `singer_rests` this
    turn's Repay is already gone once she has Drained this turn."""
    f = _f(state)
    capacity = f.singer * turns_left(state)
    if f.singer_rests and f.drained_this_turn:
        capacity = max(0.0, capacity - f.singer)
    return capacity


def unrepaid_share(state, n: int) -> float:
    """The share of a new Drain of N the Singer will not repay before the
    fight ends, given what is already drained. 0 under the curtain call."""
    f = _f(state)
    if f.curtain_call:
        return 0.0
    capacity = singer_capacity(state)
    before = max(0.0, f.drained - capacity)
    after = max(0.0, f.drained + n - capacity)
    return (after - before) / n if n else 0.0


def forfeit_cost(state, n: int) -> float:
    """`singer_rests` only: what the first Drain of a turn costs by silencing
    this turn's Singer. Zero otherwise."""
    f = _f(state)
    if not f.singer_rests or f.drained_this_turn or f.singer <= 0:
        return 0.0
    cap = singer_capacity(state)
    cap_after = max(0.0, cap - f.singer)
    owed = f.drained + n
    lost = min(owed, cap) - min(owed, cap_after)
    cost = lost * hp_value(state)
    if f.repay_fanfare:
        cost += _loop_gain_value(state, lost)
    return cost


def _drain_triggers(state, n: int) -> float:
    f = _f(state)
    v = 0.0
    if f.powers["salon_encore"]:
        v += _aoe(state, T.SALON_ENCORE_DAMAGE * f.powers["salon_encore"])
    if "wriothesley" in f.stage:
        v += n * 0.9
    return v


def _gain_value(state, n: float) -> float:
    return fanfare_value(state) * n


def _loop_gain_value(state, n: float) -> float:
    """N Fanfare from a Drain or a Repay, with the readers of those two
    (Universal Revelry, Critics' Darling)."""
    f = _f(state)
    v = fanfare_value(state) * n * (1 + f.powers["revelry"])
    if f.powers["critics_darling"]:
        v += 0.9 * n * f.powers["critics_darling"]
    return v


def drain_cost(state, n: int, kills: bool = False) -> float:
    """What Draining N costs now, net of the Fanfare and triggers it buys.
    `kills`: this play ends the fight."""
    f = _f(state)
    if f.curtain_call:
        cost = 0.0 if kills else n * temp_hp_value(state)
    else:
        hpv = hp_value(state)
        cost = (n * hpv * unrepaid_share(state, n)
                + DRAIN_RISK * n * (0.0 if kills else _exposed(state)))
    cost += forfeit_cost(state, n)
    return cost - _loop_gain_value(state, n) - _drain_triggers(state, n)


def repay_value(state, n: int) -> float:
    f = _f(state)
    amount = min(n, f.drained)
    if amount <= 0:
        return 0.0
    per_hp = temp_hp_value(state) if f.curtain_call else hp_value(state)
    v = amount * per_hp
    if f.repay_fanfare:
        v += _loop_gain_value(state, amount)
    elif f.powers["revelry"] or f.powers["critics_darling"]:
        v += _loop_gain_value(state, amount) - _gain_value(state, amount)
    if f.powers["endless_waltz"]:
        v += 0.9 * amount
    if "sigewinne" in f.stage:
        v += _block_value(amount, need(state))
    if "clorinde" in f.stage:
        v += 0.9 * T.CLORINDE_PER_REPAY * amount
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
    if k in ("spend_aoe",):
        return (n[2] - n[0]) / n[1]
    if k == "spend_fixed_hit":
        return n[1] / n[0]
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
    """A Spend of N: the Fanfare's worth, less Thunderous Applause's AoE."""
    f = _f(state)
    cost = fanfare_value(state) * n
    if f.powers["thunderous"] and n > 0:
        cost -= _aoe(state, T.THUNDEROUS_DAMAGE * f.powers["thunderous"])
    return cost


# ----------------------------------------------------------------------
# The in-card choices.
# ----------------------------------------------------------------------
class Judged:
    def drain(self, state, card, spec) -> bool:
        plain, price, big = spec.n
        kills = False
        if spec.kind == "drain_block":
            gain = (_block_value(big, need(state))
                    - _block_value(plain, need(state)))
        elif spec.kind == "drain_aoe":
            gain = _aoe(state, big) - _aoe(state, plain)
            kills = ends_fight(state, big, aoe=True)
        elif spec.kind == "drain_tab":
            gain = NEXT_ENERGY
        else:
            left = _target_left(state)
            if big >= left > plain:
                return True               # the Drain kills, the plain not
            gain = _single(state, big) - _single(state, plain)
            kills = ends_fight(state, big)
        return gain - drain_cost(state, price, kills) > 0

    def fixed_drain_value(self, state, spec) -> float | None:
        """A fixed Drain card's play value; None means never play it."""
        price, dmg = spec.n
        return (_single(state, dmg)
                - drain_cost(state, price, ends_fight(state, dmg)))

    def spend(self, state, card, spec) -> bool:
        price = spec.n[1]
        if spec.kind == "block_spend_hit":
            gain = _single(state, spec.n[2])
        elif spec.kind == "spend_aoe":
            gain = _aoe(state, spec.n[2]) - _aoe(state, spec.n[0])
        elif spec.kind == "spend_energy":
            gain = 6.0 if _playable_left(state) else 0.0
        else:
            gain = (_single(state, spec.n[2]) - _single(state, spec.n[0])
                    + DRAW * spec.n[3])
        return gain - spend_cost(state, price) > 0

    def spend_all(self, state, card, spec) -> bool:
        """`legacy` only: may Rising Applause skip its spend?"""
        pts = _f(state).fanfare
        return _single(state, spec.n[1] * pts) - spend_cost(state, pts) > 0


class Always(Judged):
    def drain(self, state, card, spec) -> bool:
        return True

    def fixed_drain_value(self, state, spec) -> float | None:
        return _single(state, spec.n[1])

    def spend(self, state, card, spec) -> bool:
        return True


class Never(Judged):
    def drain(self, state, card, spec) -> bool:
        return False

    def fixed_drain_value(self, state, spec) -> float | None:
        return None


DECIDERS = {"judged": Judged(), "always": Always(), "never": Never()}
DEFAULT_DECIDER = DECIDERS["judged"]


def allowed(state, card, decider) -> bool:
    """The engine's playability, the fixed-price gate, and the never-Drain
    pilot's refusal of a fixed Drain card."""
    if not T.playable(state, card):
        return False
    spec = T.spec_of(card)
    if spec is not None and spec.kind in T.FIXED_DRAIN_KINDS:
        return decider.fixed_drain_value(state, spec) is not None
    return True


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
    hp_per = temp_hp_value(state) if f.curtain_call else hp_value(state)
    per_repay = hp_per + (FANFARE if f.repay_fanfare else 0.0)
    if member == "charlotte":
        per = 0.6 * per_repay * T.CHARLOTTE_ACT_REPAY + 1.0
    elif member == "sigewinne":
        per = 0.6 * per_repay * T.SIGEWINNE_ACT_REPAY + 2.0
    elif member == "wriothesley":
        per = T.WRIOTHESLEY_ACT + 2.5
    elif member == "lynette":
        per = 0.5 * T.LYNETTE_ACT + 3.0 * FANFARE
    elif member == "clorinde":
        per = T.CLORINDE_ACT + 4.0
    elif member == "neuvillette":
        per = 3.0 * n + 2.0
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
    if k == "drain_fixed_hit":
        return float(n[1] if T.can_drain(state, n[0]) else 0)
    if k == "hit_repay":
        return float(n[0])
    if k == "bravura":
        return float(n[0] + n[1] * f.fanfare)
    if k == "block_spend_hit":
        return float(n[2] if f.fanfare >= n[1] else 0)
    if k == "block_spend_all":
        return float(n[1] * f.fanfare)
    if k == "spend_draw":
        return float(n[2] if f.fanfare >= n[1] else n[0])
    if k == "spend_fixed_hit":
        return float(n[1] if f.fanfare >= n[0] else 0)
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
    if k in T.DRAIN_KINDS:
        plain, price, big = n
        kills = False
        if k == "drain_block":
            pv = _block_value(plain, need_now)
            bv = _block_value(big, need_now)
        elif k == "drain_aoe":
            pv, bv = _aoe(state, plain), _aoe(state, big)
            kills = ends_fight(state, big, aoe=True)
        elif k == "drain_tab":
            draws = bool(state.player.draw_pile or state.player.discard_pile)
            pv = DRAW if draws else 0.0
            bv = pv + NEXT_ENERGY
        else:
            pv, bv = _single(state, plain), _single(state, big)
            kills = ends_fight(state, big)
        if T.can_drain(state, price) and decider.drain(state, card, spec):
            return bv - drain_cost(state, price, kills)
        return pv
    if k in T.FIXED_DRAIN_KINDS:
        if not T.playable(state, card):
            return 0.0
        v = decider.fixed_drain_value(state, spec)
        return 0.0 if v is None else v
    if k in T.SPEND_KINDS:
        price = n[1]
        if k == "block_spend_hit":
            pv = _block_value(n[0], need_now)
            bv = pv + _single(state, n[2])
        elif k == "spend_aoe":
            pv, bv = _aoe(state, n[0]), _aoe(state, n[2])
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
    if k in T.FIXED_SPEND_KINDS:
        if not T.playable(state, card):
            return 0.0
        return _single(state, n[1]) - spend_cost(state, n[0])
    if k == "block_spend_all":
        v = _block_value(n[0], need_now)
        pts = f.fanfare
        if pts and (not f.rising_optional
                    or decider.spend_all(state, card, spec)):
            v += _single(state, n[1] * pts) - spend_cost(state, pts)
        return v
    if k == "hit_repay":
        return _single(state, n[0]) + repay_value(state, n[1])
    if k == "block_repay":
        return _block_value(n[0], need_now) + repay_value(state, n[1])
    if k == "repay_draw":
        draws = bool(state.player.draw_pile or state.player.discard_pile)
        return repay_value(state, n[0]) + (DRAW * n[1] if draws else 0.0)
    if k == "repay_all":
        return repay_value(state, f.drained)
    if k == "bravura":
        pts = f.fanfare
        return _single(state, n[0] + n[1] * pts) - spend_cost(state, pts)
    if k == "rejoice":
        pts = f.fanfare
        if pts <= 0:
            return 0.0
        return _aoe(state, n[0] * pts) - spend_cost(state, pts)
    if k == "power":
        tl = max(1, EXPECTED_TURNS - state.turn)
        m = spec.member
        ne = max(1, len(state.living_enemies))
        if m == "salon_encore":
            return 0.8 * tl * ne * 2.0
        if m == "thunderous":
            return 0.8 * tl * ne * 1.5
        if m == "endless_waltz":
            return 0.8 * tl * 3.0
        if m == "revelry":
            return 0.8 * tl * 3.0 * FANFARE
        if m == "critics_darling":
            return 0.8 * tl * 3.0
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
        playable = [c for c in state.player.hand if card_playable(state, c)
                    and allowed(state, c, decider)]
        if not playable:
            return None
        lethal = _lethal(state, playable)
        if lethal is not None:
            return lethal
        ranked = _ranked(state, playable, decider)
        return ranked[0] if ranked else None
    return pilot


PILOTS = {name: make_pilot(name) for name in DECIDERS}
