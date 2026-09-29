"""Zhongli, THE TAB -- an EXPLORATION sim of a Paper-stage kit.

`review/active/zhongli-paper-kit-2026-09-28.md` is the design (Paper stage,
not a brief; every number is a placeholder). This module answers "do we
understand the mechanical output of what we are trying to build", so it is an
INSTRUMENT, not a Prototype: nothing here is on a sheet, nothing is in any
loader index, pool, stamp or digest, and NOTHING IN THIS MODULE IS ON.

WHAT IT MODELS (paper sec.3, sec.4, sec.6; the main session's sim spec):
  * Wangsheng Account: the Tab, credit limit 40 / 80 / 120 by act.
  * Mora-priced cards: paid from gold first; when gold is short the WHOLE
    price goes on the Tab (``PAY_MODE = "gold_first"``, the paper's "when you
    cannot pay"). ``PAY_MODE = "tab_first"`` is the policy switch the spec
    allows ("or policy chooses not to"). At the limit, a Mora price cannot be
    paid and the card (or its Mora mode) cannot be played.
  * No gold ever enters during combat. Settlement is the RUN layer's
    (``tier05/exp_zhongli_paper.py``): after the rewards the Tab is paid from
    gold, the rest becomes one Unpaid Invoice for the exact amount.
  * Invoices count against the credit limit (``Player.zl_invoices``).
  * Contracts: pay now, a Term, Kept -> +20 credit this fight, Broken ->
    Statuses shuffled into the draw pile; each card instance pays out once
    per fight (its FIRST play sets the term; later plays are the plain body).
  * The Stele: 3 Geo to ALL enemies at the end of each of your turns.

WHY IT IS A FLAG AND TWO HOOKS. `combat._player_turn` calls `turn_start` and
`end_of_turn` behind ``ZHONGLI_PAPER``; with it False both return before
reading anything and the engine is byte-identical. The card bodies are one op,
``zl``, registered into `effects.OPS` only by `install()`, which the
experiment calls -- so no shipped vocabulary, lint or codegen sees it.

WHAT IT DELIBERATELY DOES NOT DO: upgrades, relics other than the Account,
events, co-op, C#. Card numbers are the spec's and are not tuned.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Optional

# ----------------------------------------------------------------------
# THE FLAG. OFF. The experiment turns it on for its own process only.
# ----------------------------------------------------------------------
ZHONGLI_PAPER = False

CHARACTER = "zhongli"
HP = 80                       # NOT IN THE PAPER. Placeholder (Ironclad's 80).
CREDIT_LIMIT_BY_ACT = (40, 80, 120)   # paper sec.3, placeholder
KEPT_CREDIT = 20              # paper sec.4: "Kept: +20 credit this fight"
ENERGY_PER_MORA = 1 / 20      # spec: 1 Energy ~ 20 Mora (the exchange peg)
STELE_DAMAGE = 3              # paper sec.4
BULK_DISCOUNT = 5
GOLD_TONGUED_DISCOUNT = 10
LEDGER_BLOCK = 3
PILLAR_BLOCK_PER_CONTRACT = 3

#: "gold_first" (the paper's reading) or "tab_first" (policy option).
PAY_MODE = "gold_first"

#: Co-op stand-in for question 6 ONLY: at the start of each of Zhongli's turns
#: a partner paints Hydro on one enemy (a fresh aura). Off for every solo read.
PARTNER_AURA_PER_TURN = False


# ----------------------------------------------------------------------
# THE CARDS (spec "Cards"; placeholders, not tuned).
# `mora` is the price of the Mora mode; `mora_only` means the card has no
# other mode (the Mora price is its cost line alongside any Energy cost).
# `alt_energy` is the Energy cost of the Mora mode when it differs.
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ZDef:
    id: str
    name: str
    cost: int
    type: str
    rarity: str
    mora: int = 0
    mora_only: bool = False
    alt_energy: Optional[int] = None    # Energy cost of the Mora mode
    contract: bool = False
    exhaust: bool = False


DEFS: dict[str, ZDef] = {d.id: d for d in (
    ZDef("zl_dominus_lapidis", "Dominus Lapidis", 1, "skill", "basic"),
    ZDef("zl_price_for_everything", "A Price for Everything", 0, "skill",
         "basic", mora=15, mora_only=True),
    ZDef("zl_rain_of_stone", "Rain of Stone", 1, "attack", "common",
         mora=20, alt_energy=0),
    ZDef("zl_jade_screen", "Jade Screen", 1, "skill", "common", mora=10),
    ZDef("zl_earthly_tremor", "Earthly Tremor", 1, "attack", "common",
         mora=20),
    ZDef("zl_dominance", "Dominance", 1, "attack", "common"),
    ZDef("zl_liquidity", "Liquidity", 0, "skill", "common", mora=30,
         mora_only=True, exhaust=True),
    ZDef("zl_bulk_purchase", "Bulk Purchase", 1, "skill", "common"),
    ZDef("zl_contract_of_stone", "Contract of Stone", 1, "skill", "common",
         contract=True),
    ZDef("zl_contract_of_earth", "Contract of Earth", 1, "attack", "common",
         contract=True),
    ZDef("zl_jade_shield", "Jade Shield", 2, "skill", "uncommon"),
    ZDef("zl_stone_stele", "Stone Stele", 1, "power", "uncommon"),
    ZDef("zl_settle_accounts", "Settle Accounts", 1, "skill", "uncommon"),
    ZDef("zl_lithic_ledger", "Lithic Ledger", 1, "power", "uncommon"),
    ZDef("zl_contract_of_jade", "Contract of Jade", 1, "skill", "uncommon",
         mora=20, mora_only=True, contract=True),
    ZDef("zl_pillar_of_contracts", "Pillar of Contracts", 2, "power", "rare"),
    ZDef("zl_planet_befall", "Planet Befall", 2, "attack", "rare",
         exhaust=True),
    ZDef("zl_gold_tongued", "Gold-Tongued", 1, "power", "rare"),
)}

STARTER = (["strike"] * 4 + ["defend"] * 4
           + ["zl_dominus_lapidis", "zl_price_for_everything"])
POOL = tuple(d.id for d in DEFS.values() if d.rarity != "basic")
INVOICE_ID = "zl_invoice"


def make_card(card_id: str):
    """A fresh Card instance. Base Strike/Defend come from the loader (the
    base game's numbers); Zhongli's rows are built here and never indexed."""
    from tier0.engine.state import Card
    if card_id in DEFS:
        d = DEFS[card_id]
        return Card(id=d.id, name=d.name, cost=d.cost, type=d.type,
                    rarity=d.rarity, element="geo",
                    effects=[{"op": "zl"}], exhaust=d.exhaust,
                    character=CHARACTER)
    if card_id.startswith(INVOICE_ID):
        # Unpaid Invoice: Unplayable (type status is the engine's unplayable
        # clog), circulates like a Wound. Its amount lives in the run layer.
        return Card(id=card_id, name="Unpaid Invoice", cost=0, type="status",
                    rarity="curse", character=CHARACTER)
    from tier0.content import loader
    return loader.get_card(card_id)


def build_player(deck_ids: list[str], hp: int, max_hp: int, gold: int,
                 act: int, invoices: int):
    from tier0.engine.state import Player
    p = Player(hp=hp, max_hp=max_hp,
               draw_pile=[make_card(cid) for cid in deck_ids],
               element="geo", cadence="catalyst", character_id=CHARACTER)
    p.zl_gold = gold
    p.zl_act = act
    p.zl_invoices = invoices
    return p


# ----------------------------------------------------------------------
# PER-FIGHT LEDGER (lives on the CombatState; a new fight is a new state).
# ----------------------------------------------------------------------
@dataclass
class Ledger:
    gold_start: int = 0
    gold: int = 0
    tab: int = 0
    act: int = 0
    invoices: int = 0
    kept_credit: int = 0
    bulk: int = 0
    gold_tongued: int = 0
    lithic: int = 0
    steles: list = field(default_factory=list)   # remaining ticks; -1 = forever
    petrify_used: bool = False
    # telemetry
    mora_paid_gold: int = 0
    mora_on_tab: int = 0
    tab_peak: int = 0
    extra_credit_used: bool = False
    mora_plays: dict = field(default_factory=dict)
    energy_from_mora: float = 0.0       # energy gained/saved by Mora modes
    refused_at_limit: int = 0
    stele_damage: int = 0
    ledger_block: int = 0
    settle_paid: int = 0
    contracts: list = field(default_factory=list)   # [card_id, verdict, credit_used_after]
    pending: list = field(default_factory=list)     # open terms
    jade_energy_next: int = 0
    paid_out: set = field(default_factory=set)      # id(card) that paid out


def ledger(state) -> Ledger:
    zl = getattr(state, "zl", None)
    if zl is None:
        p = state.player
        g = getattr(p, "zl_gold", 0)
        zl = Ledger(gold_start=g, gold=g, act=getattr(p, "zl_act", 0),
                    invoices=getattr(p, "zl_invoices", 0))
        state.zl = zl
    return zl


def is_zhongli(state) -> bool:
    return ZHONGLI_PAPER and state.player.character_id == CHARACTER


def credit_limit(zl: Ledger) -> int:
    return (CREDIT_LIMIT_BY_ACT[min(zl.act, 2)] + zl.kept_credit
            - zl.invoices)


def base_limit(zl: Ledger) -> int:
    return CREDIT_LIMIT_BY_ACT[min(zl.act, 2)] - zl.invoices


def mora_price(zl: Ledger, d: ZDef) -> int:
    return max(0, d.mora - BULK_DISCOUNT * zl.bulk
               - GOLD_TONGUED_DISCOUNT * zl.gold_tongued)


def can_pay(zl: Ledger, price: int) -> bool:
    if price <= 0:
        return True
    room = credit_limit(zl) - zl.tab
    if PAY_MODE == "tab_first":
        return room >= price or zl.gold >= price
    return zl.gold >= price or room >= price


def modes(card) -> list[str]:
    d = DEFS.get(card.id)
    if d is None:
        return ["energy"]
    if d.mora_only:
        return ["mora"]
    if d.mora:
        return ["energy", "mora"]
    return ["energy"]


def energy_cost(card, mode: str) -> int:
    d = DEFS.get(card.id)
    if d is not None and mode == "mora" and d.alt_energy is not None:
        return d.alt_energy
    return card.cost if isinstance(card.cost, int) else 0


def playable(state, card, mode: str) -> bool:
    if card.type == "status" or card.type == "curse":
        return False
    zl = ledger(state)
    if card.id == "zl_planet_befall" and zl.petrify_used:
        return False
    if energy_cost(card, mode) > state.player.energy:
        return False
    d = DEFS.get(card.id)
    if d is not None and mode == "mora":
        return can_pay(zl, mora_price(zl, d))
    return True


def _pay(state, zl: Ledger, card, price: int) -> None:
    zl.mora_plays[card.id] = zl.mora_plays.get(card.id, 0) + 1
    if price <= 0:
        return
    room = credit_limit(zl) - zl.tab
    use_tab = ((PAY_MODE == "tab_first" and room >= price)
               or (PAY_MODE != "tab_first" and zl.gold < price))
    if use_tab:
        if room < price:
            raise AssertionError("Mora price over the credit limit")
        zl.tab += price
        zl.mora_on_tab += price
        zl.tab_peak = max(zl.tab_peak, zl.tab)
        if zl.tab > base_limit(zl):
            zl.extra_credit_used = True
        if zl.lithic:
            _block(state, card, LEDGER_BLOCK * zl.lithic)
            zl.ledger_block += LEDGER_BLOCK * zl.lithic
        state.emit("zl_tab", card=card.id, price=price, tab=zl.tab)
    else:
        zl.gold -= price
        zl.mora_paid_gold += price
        state.emit("zl_gold", card=card.id, price=price, gold=zl.gold)


# ----------------------------------------------------------------------
# THE ONE OP. Everything a Zhongli row does is resolved here, off the
# card id and the mode the pilot stamped on the instance.
# ----------------------------------------------------------------------
def _block(state, card, amount: int) -> None:
    from tier0.engine import effects
    effects.OPS["block"](state, {"op": "block", "amount": amount}, card)


def _damage(state, card, amount: int, target: str = "enemy",
            geo: bool = True) -> None:
    from tier0.engine import effects
    fx = {"op": "damage", "amount": amount, "target": target,
          "applies_element": geo}
    effects.OPS["damage"](state, fx, card)


def _add_status(state, status_id: str, n: int) -> None:
    from tier0.engine import statuses
    for _ in range(n):
        c = statuses.make_status(status_id)
        pile = state.player.draw_pile
        pile.insert(state.rng.randrange(len(pile) + 1), c)


def _contracts_in_deck(state) -> int:
    p = state.player
    return sum(1 for pile in (p.draw_pile, p.hand, p.discard_pile,
                              p.exhaust_pile)
               for c in pile if c.id in DEFS and DEFS[c.id].contract)


def _open_term(state, zl: Ledger, card, kind: str, **kw) -> None:
    if id(card) in zl.paid_out:
        return                        # each Contract card pays out once/fight
    zl.paid_out.add(id(card))
    zl.pending.append({"card": card.id, "kind": kind, "turn": state.turn,
                       **kw})


def _op_zl(state, fx: dict, card) -> None:
    zl = ledger(state)
    p = state.player
    mode = getattr(card, "zl_mode", "energy")
    card.zl_mode = "energy"
    card.free_this_turn = False           # the pilot's per-play Energy override
    tgt = getattr(card, "zl_target", None)
    card.zl_target = None
    if tgt is not None and tgt.alive and state.card_aim_bound:
        state.card_aim = tgt
    d = DEFS[card.id]
    mora = mode == "mora"
    if mora:
        _pay(state, zl, card, mora_price(zl, d))
    cid = card.id
    if cid == "zl_dominus_lapidis":
        _block(state, card, 5)
        zl.steles.append(2)
    elif cid == "zl_price_for_everything":
        state.draw(2)
        p.energy += 1
        zl.energy_from_mora += 1
    elif cid == "zl_rain_of_stone":
        _damage(state, card, 9)
        if mora:
            zl.energy_from_mora += 1          # the Energy it did not cost
    elif cid == "zl_jade_screen":
        _block(state, card, 13 if mora else 8)
    elif cid == "zl_earthly_tremor":
        _damage(state, card, 10 if mora else 5, "all_enemies")
    elif cid == "zl_dominance":
        big = zl.tab * 2 >= CREDIT_LIMIT_BY_ACT[min(zl.act, 2)]
        state.emit("zl_dominance", big=big)
        _damage(state, card, 11 if big else 7, geo=False)
    elif cid == "zl_liquidity":
        p.energy += 2
        zl.energy_from_mora += 2
    elif cid == "zl_bulk_purchase":
        state.draw(1)
        zl.bulk += 1
    elif cid == "zl_contract_of_stone":
        _block(state, card, 12)
        _open_term(state, zl, card, "no_unblocked", hp=p.hp)
    elif cid == "zl_contract_of_earth":
        dead = sum(1 for e in state.enemies if not e.alive)
        _damage(state, card, 9, geo=False)
        _open_term(state, zl, card, "kill_this_turn", dead=dead)
    elif cid == "zl_jade_shield":
        _block(state, card, 10)
        from tier0.engine import powers
        powers.apply_power(state, p, "blur", 1)
    elif cid == "zl_stone_stele":
        zl.steles.append(-1)
    elif cid == "zl_settle_accounts":
        pay = min(20, zl.tab, zl.gold)
        zl.tab -= pay
        zl.gold -= pay
        zl.settle_paid += pay
        state.draw(2)
    elif cid == "zl_lithic_ledger":
        zl.lithic += 1
    elif cid == "zl_contract_of_jade":
        zl.jade_energy_next += 2
        _open_term(state, zl, card, "no_attack_next_turn")
    elif cid == "zl_pillar_of_contracts":
        _block(state, card, PILLAR_BLOCK_PER_CONTRACT * _contracts_in_deck(state))
    elif cid == "zl_planet_befall":
        zl.petrify_used = True
        target = state.card_aim if state.card_aim_bound else None
        _damage(state, card, 20)
        if target is not None and target.alive:
            target.sleep_turns += 1           # skips its next action
            state.emit("zl_petrify", enemy=target.name)
    elif cid == "zl_gold_tongued":
        zl.gold_tongued += 1
    else:                                     # pragma: no cover
        raise ValueError(cid)


def install() -> None:
    """Turn the arm on for THIS PROCESS: the flag and the one op."""
    global ZHONGLI_PAPER
    from tier0.engine import effects
    ZHONGLI_PAPER = True
    effects.OPS["zl"] = _op_zl


# ----------------------------------------------------------------------
# THE TWO TURN HOOKS (called from combat._player_turn behind the flag).
# ----------------------------------------------------------------------
def _settle_term(state, zl: Ledger, term: dict, kept: bool) -> None:
    zl.pending.remove(term)
    rec = {"card": term["card"], "kept": kept, "turn": state.turn,
           "enemies": tuple(sorted({e.name for e in state.enemies})),
           "credit_used_after": False}
    zl.contracts.append(rec)
    state.emit("zl_contract", card=term["card"], kept=kept)
    if kept:
        zl.kept_credit += KEPT_CREDIT
        rec["_mark"] = zl.mora_on_tab
        rec["_limit_before"] = credit_limit(zl) - KEPT_CREDIT
    else:
        if term["card"] == "zl_contract_of_stone":
            _add_status(state, "wound", 2)
        elif term["card"] == "zl_contract_of_earth":
            _add_status(state, "dazed", 2)
        elif term["card"] == "zl_contract_of_jade":
            _add_status(state, "wound", 1)


def turn_start(state) -> None:
    if not is_zhongli(state):
        return
    zl = ledger(state)
    p = state.player
    if state.turn == 1:
        # Pillar of Contracts, the "at the start of each combat" half: read as
        # deck presence (a played Power does not survive a combat).
        n_pillar = sum(1 for c in p.draw_pile + p.hand
                       if c.id == "zl_pillar_of_contracts")
        if n_pillar:
            from tier0.engine.state import Card
            probe = Card(id="zl_pillar_start", name="Pillar", cost=0,
                         type="power", effects=[])
            amt = (PILLAR_BLOCK_PER_CONTRACT * _contracts_in_deck(state)
                   * n_pillar)
            if amt:
                _block(state, probe, amt)
    if zl.jade_energy_next:
        p.energy += zl.jade_energy_next
        zl.energy_from_mora += zl.jade_energy_next
        zl.jade_energy_next = 0
    for term in list(zl.pending):
        if term["kind"] == "no_unblocked" and term["turn"] < state.turn:
            _settle_term(state, zl, term, p.hp >= term["hp"])
    if PARTNER_AURA_PER_TURN:
        from tier0.engine import reactions
        cands = [e for e in state.living_enemies
                 if not e.aura or e.aura_spent]
        if cands:
            reactions.apply_aura(state, state.rng.choice(cands), "hydro",
                                 "partner")


def end_of_turn(state) -> None:
    if not is_zhongli(state):
        return
    zl = ledger(state)
    # Terms that close at the end of a turn.
    for term in list(zl.pending):
        if term["kind"] == "kill_this_turn":
            dead = sum(1 for e in state.enemies if not e.alive)
            _settle_term(state, zl, term, dead > term["dead"])
        elif (term["kind"] == "no_attack_next_turn"
              and state.turn == term["turn"] + 1):
            _settle_term(state, zl, term,
                         state.attacks_played_this_turn == 0)
    # The Steles.
    if zl.steles and state.living_enemies:
        from tier0.engine.state import Card
        stele = Card(id="zl_stele_tick", name="Stele", cost=0, type="power",
                     element="geo", effects=[], character=CHARACTER)
        n = len(zl.steles)
        before = sum(max(0, e.hp) for e in state.enemies)
        for _ in range(n):
            if not state.living_enemies:
                break
            _damage(state, stele, STELE_DAMAGE, "all_enemies")
        zl.stele_damage += before - sum(max(0, e.hp) for e in state.enemies) \
            - sum(min(0, e.hp) for e in state.enemies) * 0
        zl.steles = [t - 1 if t > 0 else t for t in zl.steles]
        zl.steles = [t for t in zl.steles if t != 0]


def close_fight(state) -> Ledger:
    """End-of-fight bookkeeping the run layer reads. A Term still open when
    the fight ends is recorded as unresolved (the fight ended first)."""
    zl = ledger(state)
    for term in list(zl.pending):
        zl.pending.remove(term)
        zl.contracts.append({"card": term["card"], "kept": None,
                             "turn": state.turn,
                             "enemies": tuple(sorted({e.name for e in
                                                      state.enemies})),
                             "credit_used_after": False})
    for rec in zl.contracts:
        if rec.get("kept") and "_mark" in rec:
            # Extra credit "mattered" if, after the keep, the Tab went past
            # the limit the fight had before that keep.
            rec["credit_used_after"] = zl.tab_peak > rec["_limit_before"] \
                and zl.mora_on_tab > rec["_mark"]
    return zl


# ----------------------------------------------------------------------
# THE PILOT. An instrument, not an optimiser. Greedy, one card at a time:
#   1. every (card, mode) that is affordable and that the MORA POLICY allows;
#   2. a value in HP-equivalents: damage to living enemies (capped at what
#      the target has left, +8 for a kill), Block up to the incoming damage
#      at 1.2 and past it at 0.2, draw 3 per card, Energy 4 per point,
#      Powers a flat value early in the fight;
#   3. play the best value per Energy (0-cost cards count as 0.5 Energy);
#      stop when nothing is worth more than 0.
# Mora policies (question 3):
#   always    -- use a Mora mode whenever one is payable.
#   never     -- never pay Mora; Mora-only cards are dead.
#   threshold -- Mora only when the fight is dangerous: an elite or a boss
#                on the board, or HP at or below THRESHOLD_HP of max.
# A Contract of Jade term turn penalises Attacks (breaking costs a Wound
# and the credit) unless the Attack kills.
# ----------------------------------------------------------------------
THRESHOLD_HP = 0.5


def mora_allowed(state, policy: str) -> bool:
    if policy == "always":
        return True
    if policy == "never":
        return False
    p = state.player
    if p.hp <= THRESHOLD_HP * p.max_hp:
        return True
    return any(e.is_boss or getattr(e, "zl_elite", False)
               for e in state.enemies)


def _incoming(state) -> float:
    from tier0.pilot import policy
    return policy._incoming_damage(state)


def _dmg_value(state, amount: float, target: str, tgt=None) -> float:
    living = state.living_enemies
    if not living:
        return 0.0
    str_bonus = state.player.powers.get("strength", 0)
    weak = state.player.powers.get("weak", 0)
    def one(e):
        a = amount + str_bonus
        if weak:
            a *= 0.75
        if e.powers.get("vulnerable", 0):
            a *= 1.5
        eff = max(0.0, a - e.block)
        v = min(eff, e.hp)
        if eff >= e.hp:
            v += 8
        return v
    if target == "all_enemies":
        return sum(one(e) for e in living)
    return one(tgt) if tgt is not None else one(min(living, key=lambda e: e.hp))


def _best_target(state):
    living = state.living_enemies
    return min(living, key=lambda e: e.hp) if living else None


def _value(state, card, mode: str) -> float:
    zl = ledger(state)
    p = state.player
    need = max(0.0, _incoming(state) - p.block)
    def blk(n: float) -> float:
        return 1.2 * min(n, need) + 0.2 * max(0.0, n - need)
    cid = card.id
    early = state.turn <= 3
    jade_turn = any(t["kind"] == "no_attack_next_turn"
                    and state.turn == t["turn"] + 1 for t in zl.pending)
    v = 0.0
    if cid == "strike":
        v = _dmg_value(state, 6, "enemy")
    elif cid == "defend":
        v = blk(5)
    elif cid == "zl_dominus_lapidis":
        v = blk(5) + 1.5 * STELE_DAMAGE * len(state.living_enemies)
    elif cid == "zl_price_for_everything":
        v = 2 * 3 + 4
    elif cid == "zl_rain_of_stone":
        v = _dmg_value(state, 9, "enemy")
    elif cid == "zl_jade_screen":
        v = blk(13 if mode == "mora" else 8)
    elif cid == "zl_earthly_tremor":
        v = _dmg_value(state, 10 if mode == "mora" else 5, "all_enemies")
    elif cid == "zl_dominance":
        big = zl.tab * 2 >= CREDIT_LIMIT_BY_ACT[min(zl.act, 2)]
        v = _dmg_value(state, 11 if big else 7, "enemy")
    elif cid == "zl_liquidity":
        rest = sum(energy_cost(c, "energy") for c in p.hand
                   if c is not card and c.type != "status")
        v = 8.0 if rest > p.energy else 0.0
    elif cid == "zl_bulk_purchase":
        v = 3 + 1.0 * sum(1 for c in p.draw_pile + p.discard_pile + p.hand
                          if c.id in DEFS and DEFS[c.id].mora)
    elif cid == "zl_contract_of_stone":
        v = blk(12) + (3 if 12 + p.block >= _incoming(state) else 0)
    elif cid == "zl_contract_of_earth":
        v = _dmg_value(state, 9, "enemy") + 2
    elif cid == "zl_jade_shield":
        v = blk(10) + 0.4 * 10
    elif cid == "zl_stone_stele":
        v = (12 + 3 * len(state.living_enemies)) if early else 6
    elif cid == "zl_settle_accounts":
        v = 2 * 3 + (2 if zl.tab and zl.gold else 0)
    elif cid == "zl_lithic_ledger":
        v = 8 if early else 3
    elif cid == "zl_contract_of_jade":
        v = 5.0 if not jade_turn else 0.0
    elif cid == "zl_pillar_of_contracts":
        v = blk(PILLAR_BLOCK_PER_CONTRACT * _contracts_in_deck(state)) + 2
    elif cid == "zl_planet_befall":
        tgt = max(state.living_enemies, key=lambda e: e.hp, default=None)
        prevented = 0.0
        if tgt is not None and tgt.sleep_turns == 0:
            it = tgt.current_intent()
            if it["kind"] == "attack":
                prevented = it["amount"] * it.get("times", 1)
        v = _dmg_value(state, 20, "enemy", tgt) + prevented
    elif cid == "zl_gold_tongued":
        v = 10 if early else 3
    if jade_turn and card.type == "attack":
        if _dmg_value(state, 1000, "enemy") and v < 8:
            v -= 6
    return v


def make_pilot(mora_policy: str = "always"):
    def pilot(state):
        p = state.player
        zl = ledger(state)
        allowed = mora_allowed(state, mora_policy)
        best = None
        for card in p.hand:
            if card.type in ("status", "curse"):
                continue
            for mode in modes(card):
                if mode == "mora" and not allowed:
                    continue
                if not playable(state, card, mode):
                    continue
                v = _value(state, card, mode)
                if v <= 0:
                    continue
                cost = energy_cost(card, mode)
                ratio = v / (cost if cost > 0 else 0.5)
                # A Mora mode is preferred to the same card's Energy mode
                # when the policy allows it (that is what "use Mora" means).
                key = (ratio + (0.01 if mode == "mora" else 0), v)
                if best is None or key > best[0]:
                    best = (key, card, mode)
        # Telemetry: a Mora card in hand the limit refused this decision.
        for card in p.hand:
            d = DEFS.get(card.id)
            if (d is not None and d.mora and allowed
                    and not can_pay(zl, mora_price(zl, d))):
                zl.refused_at_limit += 1
                break
        if best is None:
            return None
        _, card, mode = best
        card.zl_mode = mode
        if mode == "mora" and energy_cost(card, mode) != card.cost:
            card.free_this_turn = True      # the Mora mode's Energy cost is 0
        if card.id in ("zl_planet_befall",):
            card.zl_target = max(state.living_enemies, key=lambda e: e.hp)
        return card
    return pilot


def summary(zl: Ledger) -> dict:
    return {k: v for k, v in dataclasses.asdict(zl).items()
            if k not in ("pending", "paid_out")}
