"""NAHIDA, THE SEEDS OF SKANDHA -- a PAPER kit made runnable. SIM ONLY,
EXPLORATORY, switched off.

Source of truth: `review/active/nahida-paper-kit-2026-09-28.md` (sec.2-sec.6)
and the sim spec the main session wrote for it (2026-09-29). Card numbers are
the paper's PLACEHOLDERS and are not tuned here. Nothing in this module is a
sheet row, nothing reaches the C#, and nothing measured with it is a balance
number (R215 B): the question it answers is "do we understand the mechanical
output of what we're trying to build".

THE SWITCH is `NAHIDA_PAPER` (default False), thrown only by `enable()`, which
also turns on the Dendro module (`dendro.DENDRO_ENGINE`), registers this
module's five ops in `effects.OPS` and adds Purification's trigger to
`reactions.REACTION_LISTENERS`; `disable()` takes all of it back. With the
switch off every entry point below returns at once and the ops are not
registered, so the shipped engine is byte-identical
(`tier0/tests/test_nahida_paper_sim.py` pins a whole-log digest).

THE RULES (paper sec.3, sec.5, sec.6):

  * SEED: a counter on an enemy, at most `SEED_CAP` (3) on one enemy.
  * PURIFICATION: every seeded enemy takes `PURIFY_PER_SEED` (2) Dendro per
    Seed on it. A Dendro HIT (paper pick 1 default): it paints and can react.
    It fires (1) from a card that says Purify; (2) on the FIRST reaction on a
    seeded enemy each turn, whoever causes it -- a card, a companion, a Core
    bursting on its timer. The trigger resets at the start of the player
    turn; a Core bursting at the end of the turn uses that turn's trigger if
    it is unspent. Sages' Mandate makes it twice a turn.
  * AKASHA TERMINAL (starting relic): the first Seed you place each fight
    places a second Seed on another enemy of your choice.
  * CATALYST CADENCE: every one of her Attacks paints Dendro (the shipped
    cadence dial does this for any on-sheet Attack; base Strikes stay
    element-less, R244).

THE AIM IS THE PILOT'S. Where a Seed goes is the decision the paper is built
on, so the pilot (`tier0/pilot/nahida.py`) names the enemy a card should bind
(`aim_card`) and `effects.bind_card_aim` takes it (`take_aim`). Akasha's
"enemy of your choice" asks the same pilot (`Field.chooser`).

OPEN READINGS the paper leaves (each flagged at its site and in the report):
Purification's damage takes no Strength (it is not her swing) but does take
the target's Vulnerable; a reaction-triggered Purification resolves once the
card that caused it has finished (a deferred queue, so nothing recurses
inside a hit); Scattered Seeds reads "has no Seed" once, when it is played;
Akasha's second Seed does nothing when there is no other enemy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tier0.engine.state import Card

#: THE SWITCH. Thrown by `enable()` only.
NAHIDA_PAPER = False

CHARACTER = "nahida"
#: OPEN READING: the paper says "fragile" and gives no number. Klee's 62, the
#: roster's most fragile body, is the stand-in.
HP = 62
SEED_CAP = 3
PURIFY_PER_SEED = 2
ROOTED_MIND_BLOCK = 2
RELIC_HOOK = "akasha_terminal"

#: The damage-event `source` values Purification emits.
SOURCE_PURIFY_CARD = "purify_card"
SOURCE_PURIFY_REACTION = "purify_reaction"


@dataclass
class Field:
    """Nahida's per-combat state. A side table on the CombatState (kept off
    `Player`/`Enemy`, which the mod mirrors), so the module stays separable."""
    seeds: dict = field(default_factory=dict)        # id(enemy) -> count
    powers: dict = field(default_factory=dict)       # foresight, rooted_mind,
    #                                                  shrine, mandate
    triggers_used: int = 0
    pending: int = 0
    akasha_used: bool = False
    in_purification: str = ""                       # instrument: recursion
    next_aim: dict = field(default_factory=dict)     # id(card) -> Enemy
    chooser: object = None                           # the pilot


def _field(state) -> Field:
    f = state.__dict__.get("_nahida")
    if f is None:
        f = Field()
        state.__dict__["_nahida"] = f
    return f


def field_of(state) -> Field:
    return _field(state)


def seeds(state, enemy) -> int:
    f = state.__dict__.get("_nahida")
    return f.seeds.get(id(enemy), 0) if f else 0


def total_seeds(state) -> int:
    return sum(seeds(state, e) for e in state.living_enemies)


def power(state, name: str) -> int:
    f = state.__dict__.get("_nahida")
    return f.powers.get(name, 0) if f else 0


def trigger_cap(state) -> int:
    return 2 if power(state, "mandate") else 1


def trigger_open(state) -> bool:
    return _field(state).triggers_used < trigger_cap(state)


# ---------------------------------------------------------------------------
# the switch
# ---------------------------------------------------------------------------

def enable() -> None:
    global NAHIDA_PAPER
    from tier0.engine import dendro, effects, reactions
    NAHIDA_PAPER = True
    dendro.DENDRO_ENGINE = True
    effects.OPS.update(_OPS)
    if on_reaction not in reactions.REACTION_LISTENERS:
        reactions.REACTION_LISTENERS.append(on_reaction)


def disable() -> None:
    global NAHIDA_PAPER
    from tier0.engine import dendro, effects, reactions
    NAHIDA_PAPER = False
    dendro.DENDRO_ENGINE = False
    for op in _OPS:
        effects.OPS.pop(op, None)
    while on_reaction in reactions.REACTION_LISTENERS:
        reactions.REACTION_LISTENERS.remove(on_reaction)


# ---------------------------------------------------------------------------
# Seeds
# ---------------------------------------------------------------------------

def add_seed(state, enemy, n: int = 1) -> int:
    """Place up to `n` Seeds on `enemy` (capped); Akasha rides the first."""
    f = _field(state)
    placed = 0
    for _ in range(n):
        if not enemy.alive or f.seeds.get(id(enemy), 0) >= SEED_CAP:
            break
        f.seeds[id(enemy)] = f.seeds.get(id(enemy), 0) + 1
        placed += 1
        state.emit("seed_placed", target=enemy.name,
                   seeds=f.seeds[id(enemy)])
        if (not f.akasha_used
                and RELIC_HOOK in state.player.relic_hooks):
            f.akasha_used = True
            other = (f.chooser.second_seed_target(state, exclude=enemy)
                     if f.chooser is not None else None)
            # OPEN READING: with no other enemy (a lone boss) the relic's
            # second Seed has nowhere to go and does nothing.
            if other is not None and f.seeds.get(id(other), 0) < SEED_CAP:
                f.seeds[id(other)] = f.seeds.get(id(other), 0) + 1
                state.emit("seed_placed", target=other.name,
                           seeds=f.seeds[id(other)], akasha=True)
    return placed


# ---------------------------------------------------------------------------
# Purification
# ---------------------------------------------------------------------------

def purify(state, source: str) -> None:
    """Every seeded enemy takes 2 Dendro per Seed on it (Shrine of Maya +1).

    OPEN READING: a Dendro hit that takes the TARGET's modifiers (Vulnerable,
    Block) but not the dealer's Strength -- Purification is not her swing.
    """
    from tier0.engine import effects
    f = _field(state)
    per = PURIFY_PER_SEED + f.powers.get("shrine", 0)
    targets = [(e, f.seeds.get(id(e), 0)) for e in state.living_enemies
               if f.seeds.get(id(e), 0) > 0]
    state.emit("purification", source=source, enemies=len(targets),
               seeds=sum(s for _, s in targets))
    rooted = f.powers.get("rooted_mind", 0)
    if rooted:
        amt = ROOTED_MIND_BLOCK * rooted
        state.player.block += amt
        state.emit("block", amount=amt, source="rooted_mind")
    dmg_source = (SOURCE_PURIFY_CARD if source == "card"
                  else SOURCE_PURIFY_REACTION)
    f.in_purification = source
    try:
        for e, s in targets:
            effects.deal_damage_to_enemy(state, e, per * s, element="dendro",
                                         source=dmg_source, powered=False)
    finally:
        f.in_purification = ""


def on_reaction(state, enemy, name: str) -> None:
    """A listener on the one reaction event: the first reaction on a SEEDED
    enemy each turn (twice with Sages' Mandate) queues a Purification."""
    if not NAHIDA_PAPER:
        return
    f = _field(state)
    if f.seeds.get(id(enemy), 0) <= 0:
        return
    if f.triggers_used >= trigger_cap(state):
        return
    f.triggers_used += 1
    f.pending += 1
    # `from_purification` is the recursion instrument: "" when a card, a
    # companion or a Core caused the reaction; "card" or "reaction" when a
    # Purification's own hit did (and which kind of Purification it was).
    state.emit("purify_trigger", reaction=name, target=enemy.name,
               n=f.triggers_used, from_purification=f.in_purification)


def flush(state) -> None:
    """Resolve every queued reaction-triggered Purification. Called by
    combat after each card and at the end of the turn. A Purification's own
    reactions can queue another only while the turn's cap allows."""
    if not NAHIDA_PAPER:
        return
    f = _field(state)
    while f.pending > 0 and state.living_enemies and state.player.alive:
        f.pending -= 1
        purify(state, "reaction")
    f.pending = 0


def turn_start(state) -> None:
    if not NAHIDA_PAPER:
        return
    f = _field(state)
    f.triggers_used = 0
    # Seeds on the dead are gone with them.
    live = {id(e) for e in state.living_enemies}
    for k in [k for k in f.seeds if k not in live]:
        del f.seeds[k]
    # INSTRUMENT ONLY: the board as the turn opens (saturation census).
    counts = [f.seeds.get(id(e), 0) for e in state.living_enemies]
    state.emit("seed_board", total=sum(counts), living=len(counts),
               capped=bool(counts) and all(c >= SEED_CAP for c in counts))


def foresight(state, enemy, dmg: int) -> int:
    """Foresight (Power): a seeded enemy's attacks deal 1 less per Seed."""
    n = power(state, "foresight")
    s = seeds(state, enemy)
    if not (n and s and dmg > 0):
        return dmg
    cut = min(dmg, n * s)
    state.emit("foresight_prevented", target=enemy.name, amount=cut)
    return dmg - cut


def take_aim(state, card) -> Optional[object]:
    f = state.__dict__.get("_nahida")
    if not f:
        return None
    aim = f.next_aim.pop(id(card), None)
    return aim if (aim is not None and aim.alive) else None


def aim_card(state, card, enemy) -> None:
    """The pilot's mouse pick for the next play of `card`."""
    if enemy is not None:
        _field(state).next_aim[id(card)] = enemy


# ---------------------------------------------------------------------------
# ops (registered only while the switch is on)
# ---------------------------------------------------------------------------

def _op_seed(state, fx: dict, card) -> None:
    n = fx.get("amount", 1)
    tgt = fx.get("target", "enemy")
    if tgt == "enemy":
        aim = state.card_aim if state.card_aim_bound else None
        if aim is None and state.living_enemies:
            aim = min(state.living_enemies, key=lambda e: e.hp)
        if aim is not None:
            add_seed(state, aim, n)
    elif tgt == "all_unseeded":
        # "Has no Seed" is read ONCE, as the card resolves: an enemy Akasha
        # seeds mid-resolution still takes the card's own Seed.
        snapshot = [e for e in state.living_enemies if seeds(state, e) == 0]
        for e in snapshot:
            add_seed(state, e, n)
    elif tgt == "all_seeded":
        for e in [e for e in state.living_enemies if seeds(state, e) > 0]:
            add_seed(state, e, n)
    else:
        raise ValueError(f"nahida_seed: unknown target {tgt!r}")


def _op_purify(state, fx: dict, card) -> None:
    for _ in range(fx.get("times", 1)):
        if not state.living_enemies:
            break
        purify(state, "card")


def _op_sprout(state, fx: dict, card) -> None:
    from tier0.engine import effects
    aim = state.card_aim if state.card_aim_bound else None
    amount = fx["seeded"] if (aim is not None and seeds(state, aim)) \
        else fx["amount"]
    effects.OPS["damage"](state, {"op": "damage", "amount": amount,
                                  "target": "enemy"}, card)


def _op_perception(state, fx: dict, card) -> None:
    from tier0.engine import effects
    amount = fx["amount"] + (fx["bonus"] if total_seeds(state) else 0)
    effects.OPS["block"](state, {"op": "block", "amount": amount}, card)


def _op_power(state, fx: dict, card) -> None:
    f = _field(state)
    f.powers[fx["power"]] = f.powers.get(fx["power"], 0) + fx.get("amount", 1)
    state.emit("nahida_power", power=fx["power"],
               stacks=f.powers[fx["power"]])


_OPS = {
    "nahida_seed": _op_seed,
    "nahida_purify": _op_purify,
    "nahida_sprout": _op_sprout,
    "nahida_perception": _op_perception,
    "nahida_power": _op_power,
}


# ---------------------------------------------------------------------------
# the cards (spec sheet, placeholders; `nh_` ids never enter any card index)
# ---------------------------------------------------------------------------

def _dmg(n, target="enemy", times=1):
    fx = {"op": "damage", "amount": n, "target": target}
    if times != 1:
        fx["times"] = times
    return fx


#: id -> (name, cost, type, rarity, effects, exhaust, kind). `kind` is the
#: report's card class for the autopilot census: S seeds, P purifies,
#: A other attack, B block, W power.
CARD_SPECS: dict[str, tuple] = {
    "nh_all_schemes": ("All Schemes to Know", 1, "attack", "basic",
                       [_dmg(3), {"op": "nahida_seed", "amount": 1}],
                       False, "S"),
    "nh_tri_karma": ("Tri-Karma Purification", 1, "skill", "basic",
                     [{"op": "nahida_purify", "times": 1}], False, "P"),
    "nh_karmic_bond": ("Karmic Bond", 1, "attack", "common",
                       [_dmg(6), {"op": "nahida_seed", "amount": 1}],
                       False, "S"),
    "nh_scattered_seeds": ("Scattered Seeds", 1, "attack", "common",
                           [_dmg(3, "all_enemies"),
                            {"op": "nahida_seed", "amount": 1,
                             "target": "all_unseeded"}], False, "S"),
    "nh_deep_roots": ("Deep Roots", 1, "skill", "common",
                      [{"op": "nahida_seed", "amount": 2},
                       {"op": "block", "amount": 4}], False, "S"),
    "nh_withering_bloom": ("Withering Bloom", 1, "attack", "common",
                           [_dmg(4, times=2)], False, "A"),
    "nh_perception": ("Perception", 1, "skill", "common",
                      [{"op": "nahida_perception", "amount": 6, "bonus": 3}],
                      False, "B"),
    "nh_seed_of_wisdom": ("Seed of Wisdom", 0, "skill", "common",
                          [{"op": "nahida_seed", "amount": 1}], True, "S"),
    "nh_sprout": ("Sprout", 1, "attack", "common",
                  [{"op": "nahida_sprout", "amount": 5, "seeded": 8}],
                  False, "A"),
    "nh_illusory_heart": ("Illusory Heart", 1, "skill", "uncommon",
                          [{"op": "nahida_purify", "times": 1},
                           {"op": "draw", "amount": 1}], False, "P"),
    "nh_harvest": ("Harvest", 2, "skill", "uncommon",
                   [{"op": "nahida_purify", "times": 2}], False, "P"),
    "nh_foresight": ("Foresight", 1, "power", "uncommon",
                     [{"op": "nahida_power", "power": "foresight"}],
                     False, "W"),
    "nh_rooted_mind": ("Rooted Mind", 1, "power", "uncommon",
                       [{"op": "nahida_power", "power": "rooted_mind"}],
                       False, "W"),
    "nh_grasp_of_wisdom": ("Grasp of Wisdom", 2, "attack", "uncommon",
                           [_dmg(12), {"op": "nahida_seed", "amount": 1,
                                       "target": "all_seeded"}], False, "S"),
    "nh_shrine_of_maya": ("Shrine of Maya", 2, "power", "rare",
                          [{"op": "nahida_power", "power": "shrine"}],
                          False, "W"),
    "nh_sages_mandate": ("Sages' Mandate", 2, "power", "rare",
                         [{"op": "nahida_power", "power": "mandate"}],
                         False, "W"),
}

STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "nh_all_schemes", "nh_tri_karma",
)


def card(card_id: str) -> Card:
    """A fresh card: `nh_` ids from the spec table, anything else through the
    loader (the base Strike and Defend, the companions)."""
    if card_id in CARD_SPECS:
        name, cost, ctype, rarity, fx, exhaust, _ = CARD_SPECS[card_id]
        import copy
        return Card(id=card_id, name=name, cost=cost, type=ctype,
                    rarity=rarity, effects=copy.deepcopy(fx),
                    exhaust=exhaust, character=CHARACTER)
    from tier0.content import loader
    return loader.get_card(card_id)


def kind(c: Card) -> str:
    """The autopilot census's card class (see CARD_SPECS)."""
    if c.id in CARD_SPECS:
        return CARD_SPECS[c.id][6]
    if c.is_companion:
        return "C"
    if c.type == "attack":
        return "A"
    return "B"


def build_player(card_ids, relic: bool = True):
    from tier0.engine.state import Player
    return Player(hp=HP, max_hp=HP,
                  draw_pile=[card(cid) for cid in card_ids],
                  element="dendro", cadence="catalyst",
                  relic_hooks=[RELIC_HOOK] if relic else [],
                  character_id=CHARACTER)
