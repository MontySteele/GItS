"""Furina, THE SALON'S TAB -- a research sim slice, a separate arm (sim only).

The design is `review/active/furina-research-proposal-2026-10-05.md`: the
research pass's proposal. It is a PAPER that nobody has ruled. This arm exists
so the paper's kill questions can be asked of numbers rather than argued; it
is an instrument, not a balance verdict, and no number it prints is quotable
as a sheet number (`EXPERIMENTS.md`: a prototype row's number is not
quotable).

HOW IT IS SWITCHED ON. Per player: a `Player` built by `build_player` carries
`player.ftd` (an `Ftd` record) and `character_id = "furina_tide"`. Every hook
the engine calls is a no-op for any other player, so today's Furina arms and
every other kit are untouched: no sheet row, no pool, no loader door, no
codegen sees this arm.

THE RULES (paper sec.2):

1. DRAIN N. A choice on some of her cards: lose N HP for the bigger effect.
   It cannot be chosen if it would take her below the line: half the HP she
   started this combat with (the default variant, `entry`; the `std` family
   of variants measures half of Max HP, Genshin's rule). HP lost to a Drain
   is DRAINED: the engine keeps the count.
2. RESTORE N. Regain up to N of your drained HP. Restore never returns HP an
   enemy took (the invariant: HP + drained <= Max HP, and Restore <= drained).
3. FANFARE. One number on Furina, no cap, no fade. She gains 1 for every HP
   she loses (to a Drain, to an enemy, to anything) and for every HP she
   Restores. Spend N on cards pays it. Readers count this turn's flow.
4. SALON SOLITAIRE (starting relic). At the end of your turn, Restore 2.
5. GUEST STARS. Three seats; a guest acts at the end of her turn; a guest
   onto a full stage makes the oldest guest leave, acting once more as it
   goes; a second copy of a guest on stage makes it act and stay.

Unrepaid drained HP is simply lost when the fight ends (there is no refund);
that is the design's cost, and `fight_record` reports it.

PROBE-ONLY ROWS. The `ftd_rising_applause_6` / `_all2` alternatives (rarity
"probe", never offered) and The Crowd Gasps (an Uncommon Power the paper
replaced with Lynette's line; it is in the draft pool the slice was read
on). VARIANTS switch the Singer's Restore, whether enemy hits print
Fanfare, and the line.

THE K3 SWITCHES (`VARIANT_SWITCHES`; all off by default, so `entry` is the
paper's rules). A Drain the Singer fully repays costs no HP and prints
Fanfare twice (on the loss and on the Restore); these variants price it:
- `singer_rests`: Salon Solitaire Restores only at the end of a turn in
  which no Drain happened (`Ftd.singer_rests`). Any Drain counts, Neuvillette's
  act included, since it is a real Drain; his act comes before the Singer.
- `restore_no_fanfare`: Restore prints no Fanfare (`Ftd.restore_fanfare`
  False). HP loss from any cause still prints it.
- `both`: the two together.
- `singer1`: the Singer Restores 1 (the paper's named lever), for comparison.
All four keep the `entry` line.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field

CHARACTER = "furina_tide"
TAG = "ftd"
HP = 78                      # furina.yaml's hp; the slice does not move it
ELEMENT = "hydro"
CADENCE = "skill"

SEATS = 3
SINGER_RESTORE = 2           # Salon Solitaire: end of turn, Restore 2

GUESTS = ("charlotte", "wriothesley", "sigewinne", "clorinde",
          "neuvillette", "navia")
GUEST_ELEMENTS = {"wriothesley": "cryo", "clorinde": "electro",
                  "neuvillette": "hydro", "navia": "geo"}

# Guest numbers (paper sec.7).
CHARLOTTE_ACT_RESTORE = 2
SIGEWINNE_ACT_RESTORE = 3
WRIOTHESLEY_ACT = 4
CLORINDE_ACT = 6
CLORINDE_PER_RESTORE = 2     # "deal twice that much Electro"
NEUVILLETTE_DRAIN = 4
NEUVILLETTE_ACT = 8          # to ALL, when he drains
NEUVILLETTE_ACT_DRY = 3      # to ALL, when he cannot
NEUVILLETTE_HYDRO_BONUS = 2
NAVIA_PER_SPENT = 2
SALON_ENCORE_DAMAGE = 3      # Power: whenever you Drain, 3 to ALL


def _new_ledger() -> dict:
    return {
        "gained": 0, "gained_by": collections.Counter(),
        "spent": 0, "spends": 0,
        "drained": 0, "drains": 0, "drain_offers": 0, "card_drains": 0,
        "drain_blocked_by_line": 0,
        "restored": 0, "restore_wasted": 0, "singer_skipped": 0,
        "spend_offers": 0,
        "guest_acts": collections.Counter(), "bows": 0,
        "started_at_or_below_half": False,
        "fanfare_end": 0, "unrepaid_end": 0,
        "damage_by_turn": collections.Counter(),
    }


@dataclass
class Ftd:
    fanfare: int = 0
    drained: int = 0                 # HP lost to Drains and not yet Restored
    gained_this_turn: int = 0
    spent_this_turn: int = 0
    restored_this_turn: int = 0
    charlotte_drew: bool = False
    stage: list = field(default_factory=list)
    powers: collections.Counter = field(default_factory=collections.Counter)
    singer: int = SINGER_RESTORE
    hit_fanfare: bool = True         # variant: do enemy hits print Fanfare?
    line: float = 0.5                # variant: the Drain line, share of Max HP
    entry_hp: int = 0                # HP at the start of this combat
    line_from_entry: bool = False    # variant: the line is half of entry HP
    singer_rests: bool = False       # variant: no Singer on a turn she Drained
    restore_fanfare: bool = True     # variant: does Restore print Fanfare?
    drained_this_turn: bool = False
    decider: object = None
    ledger: dict = field(default_factory=_new_ledger)


def live(player) -> bool:
    return isinstance(getattr(player, "ftd", None), Ftd)


def _f(state) -> Ftd:
    return state.player.ftd


def _decider(state):
    d = _f(state).decider
    if d is None:
        from tier0.pilot import furina_tide_pilot      # late: avoids a cycle
        return furina_tide_pilot.DEFAULT_DECIDER
    return d


# ----------------------------------------------------------------------
# The cards (paper sec.7, the slice's rows).
# kind and numbers; the resolver below is keyed by kind.
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Spec:
    name: str
    cost: int
    type: str                  # attack | skill | power
    rarity: str
    kind: str
    n: tuple = ()
    member: str = ""


CARDS: dict[str, Spec] = {
    # --- Starter ---
    # Curtain Rise: Deal 7. Drain 3: deal 14 instead.
    "ftd_curtain_rise": Spec("Curtain Rise", 1, "attack", "basic",
                             "drain_hit", (7, 3, 14)),
    # Rising Applause: Gain 5 Block. Spend all your Fanfare: also deal that
    # much damage. (The proposal's starter card; the probe alternatives are
    # below.)
    "ftd_rising_applause": Spec("Rising Applause", 1, "skill", "basic",
                                "block_spend_all", (5, 1)),
    # Probe alternatives for the starter's Spend card: a fixed Spend 6 for
    # 12, and spend-all at 2 per point.
    "ftd_rising_applause_6": Spec("Rising Applause (Spend 6)", 1, "skill",
                                  "probe", "block_spend_hit", (5, 6, 12)),
    "ftd_rising_applause_all2": Spec("Rising Applause (spend-all, 2)", 1,
                                     "skill", "probe", "block_spend_all",
                                     (5, 2)),
    # --- Common, Ousia ---
    # Mademoiselle Crabaletta (2): Deal 12. Drain 5: deal 26 instead.
    "ftd_crabaletta": Spec("Mademoiselle Crabaletta", 2, "attack", "common",
                           "drain_hit", (12, 5, 26)),
    # Surintendante Chevalmarin (1): Deal 4 to ALL, apply Hydro.
    # Drain 3: deal 8 to ALL instead.
    "ftd_chevalmarin": Spec("Surintendante Chevalmarin", 1, "attack",
                            "common", "drain_aoe", (4, 3, 8)),
    # Gentilhomme Usher (1): Gain 7 Block. Drain 3: gain 14 instead.
    "ftd_usher": Spec("Gentilhomme Usher", 1, "skill", "common",
                      "drain_block", (7, 3, 14)),
    # Soloist's Solicitation (0): Deal 4. Drain 2: deal 9 instead.
    "ftd_solicitation": Spec("Soloist's Solicitation", 0, "attack", "common",
                             "drain_hit", (4, 2, 9)),
    # --- Common, Spend ---
    # Tidal Flourish (1): Deal 5 to ALL. Spend 6: deal 12 to ALL and Hydro.
    "ftd_tidal_flourish": Spec("Tidal Flourish", 1, "attack", "common",
                               "spend_aoe", (5, 6, 12)),
    # Spirited Aria (1): Deal 8. Spend 5: deal 13 and draw 2 instead.
    "ftd_spirited_aria": Spec("Spirited Aria", 1, "attack", "common",
                              "spend_draw", (8, 5, 13, 2)),
    # Quick Flourish (0): Deal 3. Spend 4: deal 11 and apply Hydro instead.
    "ftd_quick_flourish": Spec("Quick Flourish", 0, "attack", "common",
                               "spend_hit", (3, 4, 11)),
    # Interval Bell (0): Draw 1 card. Spend 4: also gain 1 Energy.
    "ftd_interval_bell": Spec("Interval Bell", 0, "skill", "common",
                              "spend_energy", (1, 4, 1)),
    # Standing Ovation (1): Spend all your Fanfare. Deal that much damage to
    # ALL enemies.
    "ftd_standing_ovation": Spec("Standing Ovation", 1, "attack", "common",
                                 "rejoice", (1,)),
    # --- Common, Pneuma ---
    # Surging Waters (1, Attack): Deal 6. Restore 3.
    "ftd_surging_waters": Spec("Surging Waters", 1, "attack", "common",
                               "hit_restore", (6, 3)),
    # Hymn of Many Waters (1): Gain 8 Block. Restore 3.
    "ftd_hymn": Spec("Hymn of Many Waters", 1, "skill", "common",
                     "block_restore", (8, 3)),
    # --- Common, guest ---
    "ftd_charlotte": Spec("Guest Star: Charlotte", 1, "skill", "common",
                          "guest", (), "charlotte"),
    # --- Uncommon ---
    # Ousia Surge (1): Deal 4, plus 1 per Fanfare you gained this turn.
    "ftd_ousia_surge": Spec("Ousia Surge", 1, "attack", "uncommon",
                            "ousia", (4, 1)),
    # Pneuma Refrain (1): Restore 5. Gain 6 Block.
    "ftd_pneuma_refrain": Spec("Pneuma Refrain", 1, "skill", "uncommon",
                               "block_restore", (6, 5)),
    # Bravura (1): Spend all your Fanfare. Deal 6, plus 2 per point.
    "ftd_bravura": Spec("Bravura", 1, "attack", "uncommon", "bravura",
                        (6, 2)),
    # Salon's Encore (Power, 1): Whenever you Drain, deal 3 to ALL enemies.
    "ftd_salon_encore": Spec("Salon's Encore", 1, "power", "uncommon",
                             "power", (1,), "salon_encore"),
    # Endless Waltz (Power, 1): Whenever you Restore, deal that much damage
    # to a random enemy.
    "ftd_endless_waltz": Spec("Endless Waltz", 1, "power", "uncommon",
                              "power", (1,), "endless_waltz"),
    # The Crowd Gasps (Power, 1): Whenever an enemy makes you lose HP, gain
    # that much Fanfare.
    "ftd_crowd_gasps": Spec("The Crowd Gasps", 1, "power", "uncommon",
                            "power", (1,), "crowd_gasps"),
    "ftd_wriothesley": Spec("Guest Star: Wriothesley", 1, "skill",
                            "uncommon", "guest", (), "wriothesley"),
    "ftd_sigewinne": Spec("Guest Star: Sigewinne", 1, "skill", "uncommon",
                          "guest", (), "sigewinne"),
    # --- Rare ---
    # Let the People Rejoice (2): Spend all your Fanfare. Deal 2 to ALL per
    # point.
    "ftd_rejoice": Spec("Let the People Rejoice", 2, "attack", "rare",
                        "rejoice", (2,)),
    # Universal Revelry (Power, 2): Whenever you gain Fanfare, gain that much
    # again.
    "ftd_revelry": Spec("Universal Revelry", 2, "power", "rare", "power",
                        (1,), "revelry"),
    # Critics' Darling (Power, 1): Whenever you gain Fanfare, deal that much
    # damage to a random enemy.
    "ftd_critics_darling": Spec("Critics' Darling", 1, "power", "rare",
                                "power", (1,), "critics_darling"),
    "ftd_clorinde": Spec("Guest Star: Clorinde", 1, "skill", "rare",
                         "guest", (), "clorinde"),
    "ftd_neuvillette": Spec("Guest Star: Neuvillette", 2, "skill", "rare",
                            "guest", (), "neuvillette"),
    "ftd_navia": Spec("Guest Star: Navia", 1, "skill", "rare", "guest", (),
                      "navia"),
}

STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "ftd_curtain_rise", "ftd_rising_applause",
)

DRAIN_KINDS = ("drain_hit", "drain_aoe", "drain_block")
SPEND_KINDS = ("block_spend_hit", "spend_aoe", "spend_draw", "spend_hit",
               "spend_energy")


def spec_of(card) -> Spec | None:
    return CARDS.get(getattr(card, "id", ""))


def make_card(card_id: str):
    from tier0.content import loader
    from tier0.engine.state import Card
    if card_id not in CARDS:
        if card_id in ("strike", "defend"):
            return loader.get_card(card_id)
        raise KeyError(f"{card_id!r} is not a research-slice row")
    spec = CARDS[card_id]
    return Card(id=card_id, name=spec.name, cost=spec.cost, type=spec.type,
                rarity=spec.rarity, effects=[], tags=[TAG],
                character=CHARACTER)


#: Design variants the probe can switch per run: (singer, hit_fanfare).
VARIANTS = {"std": (2, True, 0.5), "nohit": (2, False, 0.5),
            "s3": (3, True, 0.5), "nohit_s3": (3, False, 0.5),
            "s1": (1, True, 0.5), "nohit_s1": (1, False, 0.5),
            "nohit_l33": (2, False, 1 / 3), "nohit_l40": (2, False, 0.4),
            "entry": (2, True, 0.5), "entry_nohit": (2, False, 0.5),
            "entry_s1": (1, True, 0.5)}


#: The K3 variants: the `entry` rules plus engine switches (Ftd fields).
VARIANT_SWITCHES = {
    "singer_rests": (2, {"singer_rests": True}),
    "restore_no_fanfare": (2, {"restore_fanfare": False}),
    "both": (2, {"singer_rests": True, "restore_fanfare": False}),
    "singer1": (1, {}),
}
for _name, (_singer, _sw) in VARIANT_SWITCHES.items():
    VARIANTS[_name] = (_singer, True, 0.5)

DEFAULT_VARIANT = "entry"      # the proposal's rules: the line from entry HP


def build_player(card_ids, hp: int | None = None, max_hp: int = HP,
                 singer: int = SINGER_RESTORE,
                 variant: str = DEFAULT_VARIANT):
    from tier0.engine.state import Player
    p = Player(hp=max_hp if hp is None else hp, max_hp=max_hp,
               draw_pile=[make_card(cid) for cid in card_ids],
               element=ELEMENT, cadence=CADENCE, character_id=CHARACTER)
    singer, hit, line = VARIANTS[variant]
    switches = VARIANT_SWITCHES.get(variant, (0, {}))[1]
    p.ftd = Ftd(singer=singer, hit_fanfare=hit, line=line, entry_hp=p.hp,
                line_from_entry=(variant.startswith("entry")
                                 or variant in VARIANT_SWITCHES),
                **switches)
    p.ftd.ledger["started_at_or_below_half"] = p.hp <= max_hp / 2
    return p


# ----------------------------------------------------------------------
# The loop: Drain, Restore, Fanfare.
# ----------------------------------------------------------------------
def half_line(player) -> float:
    f = getattr(player, "ftd", None)
    if f is not None and f.line_from_entry:
        return f.entry_hp * f.line
    return player.max_hp * (f.line if f is not None else 0.5)


def can_drain(state, n: int) -> bool:
    p = state.player
    return n > 0 and p.hp - n >= half_line(p)


def gain(state, amount: int, source: str) -> None:
    """Fanfare in. Universal Revelry doubles it; Critics' Darling turns the
    gain into damage (the doubled amount)."""
    if amount <= 0 or not live(state.player):
        return
    f = _f(state)
    amount += amount * f.powers["revelry"]
    f.fanfare += amount
    f.gained_this_turn += amount
    f.ledger["gained"] += amount
    f.ledger["gained_by"][source] += amount
    state.emit("ftd_gain", amount=amount, source=source, fanfare=f.fanfare)
    if f.powers["critics_darling"] and state.living_enemies:
        enemy = state.rng.choice(state.living_enemies)
        _hit(state, enemy, amount * f.powers["critics_darling"], None)


def spend(state, amount: int) -> bool:
    f = _f(state)
    if amount <= 0 or f.fanfare < amount:
        return False
    f.fanfare -= amount
    f.spent_this_turn += amount
    f.ledger["spent"] += amount
    f.ledger["spends"] += 1
    state.emit("ftd_spend", amount=amount, fanfare=f.fanfare)
    return True


def drain(state, n: int) -> bool:
    """Rule 1. Lose N HP (not below half), mark it drained, gain N Fanfare,
    then the Drain readers (Salon's Encore, Wriothesley)."""
    p = state.player
    f = _f(state)
    if not can_drain(state, n):
        return False
    p.hp -= n
    f.drained += n
    f.drained_this_turn = True
    f.ledger["drained"] += n
    f.ledger["drains"] += 1
    state.hp_lost_this_turn += n
    state.emit("ftd_drain", amount=n, hp=p.hp, drained=f.drained)
    gain(state, n, "drain")
    living = list(state.living_enemies)
    if f.powers["salon_encore"]:
        for enemy in living:
            _hit(state, enemy, SALON_ENCORE_DAMAGE * f.powers["salon_encore"],
                 None)
    if "wriothesley" in f.stage and state.living_enemies:
        _hit(state, state.rng.choice(state.living_enemies), n, "cryo")
    return True


def restore(state, n: int) -> int:
    """Rule 2. Regain up to N drained HP; gain that much Fanfare; then the
    Restore readers. Returns HP restored."""
    p = state.player
    f = _f(state)
    f.drained = min(f.drained, max(0, p.max_hp - p.hp))
    amount = min(n, f.drained)
    f.ledger["restore_wasted"] += n - amount
    if amount <= 0:
        return 0
    p.hp += amount
    f.drained -= amount
    f.restored_this_turn += amount
    f.ledger["restored"] += amount
    state.emit("ftd_restore", amount=amount, hp=p.hp, drained=f.drained)
    if f.restore_fanfare:
        gain(state, amount, "restore")
    if f.powers["endless_waltz"] and state.living_enemies:
        _hit(state, state.rng.choice(state.living_enemies),
             amount * f.powers["endless_waltz"], None)
    if "sigewinne" in f.stage:
        p.block += amount
    if "clorinde" in f.stage and state.living_enemies:
        _hit(state, state.rng.choice(state.living_enemies),
             CLORINDE_PER_RESTORE * amount, "electro")
    if "charlotte" in f.stage and not f.charlotte_drew and not state.over:
        f.charlotte_drew = True
        state.draw(1)
    return amount


def on_hp_loss(state, n: int) -> None:
    """Hook from `resources.note_player_hp_loss`: true HP loss from any
    source but a Drain (enemy hits, statuses) prints Fanfare 1:1."""
    if n <= 0 or not live(state.player):
        return
    f = _f(state)
    if f.hit_fanfare or f.powers["crowd_gasps"]:
        gain(state, n, "hit")


# ----------------------------------------------------------------------
# Damage helpers.
# ----------------------------------------------------------------------
def _hydro_bonus(state, element) -> int:
    if element == "hydro" and "neuvillette" in _f(state).stage:
        return NEUVILLETTE_HYDRO_BONUS
    return 0


def _hit(state, enemy, amount: int, element) -> None:
    from tier0.engine import effects
    amount += _hydro_bonus(state, element)
    before = enemy.hp
    effects.deal_damage_to_enemy(state, enemy, amount, element=element,
                                 powered=False, source="furina_tide/line")
    _f(state).ledger["damage_by_turn"][state.turn] += max(0, before
                                                          - enemy.hp)


def _card_damage(state, card, amount: int, *, all_enemies: bool = False,
                 hydro: bool = False) -> None:
    from tier0.engine import effects
    f = _f(state)
    fx = {"op": "damage", "amount": amount,
          "target": "all_enemies" if all_enemies else "enemy"}
    if hydro:
        fx["applies_element"] = True
        fx["amount"] = amount + _hydro_bonus(state, "hydro")
    before = sum(e.hp for e in state.enemies)
    effects.OPS["damage"](state, fx, card)
    f.ledger["damage_by_turn"][state.turn] += max(
        0, before - sum(e.hp for e in state.enemies))


def _card_block(state, card, amount: int) -> None:
    from tier0.engine import effects
    effects.OPS["block"](state, {"op": "block", "amount": amount}, card)


# ----------------------------------------------------------------------
# Guests.
# ----------------------------------------------------------------------
def act(state, member: str) -> None:
    p = state.player
    f = _f(state)
    if state.over or not p.alive:
        return
    f.ledger["guest_acts"][member] += 1
    living = list(state.living_enemies)
    if member == "charlotte":
        restore(state, CHARLOTTE_ACT_RESTORE)
    elif member == "sigewinne":
        restore(state, SIGEWINNE_ACT_RESTORE)
    elif member == "wriothesley":
        if living:
            _hit(state, state.rng.choice(living), WRIOTHESLEY_ACT, "cryo")
    elif member == "clorinde":
        if living:
            _hit(state, state.rng.choice(living), CLORINDE_ACT, "electro")
    elif member == "neuvillette":
        if drain(state, NEUVILLETTE_DRAIN):
            dmg = NEUVILLETTE_ACT
        else:
            dmg = NEUVILLETTE_ACT_DRY
        for enemy in list(state.living_enemies):
            _hit(state, enemy, dmg, "hydro")
    elif member == "navia":
        base = NAVIA_PER_SPENT * f.spent_this_turn
        if base > 0 and living:
            _hit(state, state.rng.choice(living), base, "geo")
    state.emit("ftd_act", member=member)


def summon(state, member: str) -> str:
    f = _f(state)
    if member in f.stage:
        f.ledger["bows"] += 1
        act(state, member)
        return "repeat"
    if len(f.stage) >= SEATS:
        leaver = f.stage.pop(0)
        f.ledger["bows"] += 1
        act(state, leaver)
    f.stage.append(member)
    return "seated"


# ----------------------------------------------------------------------
# Engine hooks. Each is a no-op for any player without `ftd`.
# ----------------------------------------------------------------------
def turn_open(state) -> None:
    if not live(state.player):
        return
    f = _f(state)
    f.gained_this_turn = 0
    f.spent_this_turn = 0
    f.restored_this_turn = 0
    f.drained_this_turn = False
    f.charlotte_drew = False


def end_of_turn(state) -> None:
    """Guests act in seat order, then Salon Solitaire's Singer Restores
    (under `singer_rests`, only if no Drain happened this turn)."""
    if not live(state.player):
        return
    f = _f(state)
    for member in list(f.stage):
        if state.over or not state.player.alive or not state.living_enemies:
            break
        act(state, member)
    if f.singer_rests and f.drained_this_turn:
        f.ledger["singer_skipped"] += 1
        return
    if not state.over and state.player.alive:
        restore(state, f.singer)


def resolve_card(state, card) -> None:
    if not live(state.player):
        return
    spec = spec_of(card)
    if spec is None:
        return
    f = _f(state)
    n = spec.n
    k = spec.kind
    d = _decider(state)
    if k in DRAIN_KINDS:
        plain, price, big = n
        offered = True
        f.ledger["drain_offers"] += 1
        if not can_drain(state, price):
            f.ledger["drain_blocked_by_line"] += 1
            offered = False
        take = offered and d.drain(state, card, spec)
        if take:
            drain(state, price)
            f.ledger["card_drains"] += 1
        amount = big if take else plain
        if k == "drain_hit":
            _card_damage(state, card, amount)
        elif k == "drain_aoe":
            _card_damage(state, card, amount, all_enemies=True, hydro=True)
        else:
            _card_block(state, card, amount)
    elif k in SPEND_KINDS:
        f.ledger["spend_offers"] += 1
        price = n[1]
        take = f.fanfare >= price and d.spend(state, card, spec)
        if take:
            spend(state, price)
        if k == "block_spend_hit":
            _card_block(state, card, n[0])
            if take:
                _card_damage(state, card, n[2])
        elif k == "spend_aoe":
            _card_damage(state, card, n[2] if take else n[0],
                         all_enemies=True, hydro=take)
        elif k == "spend_draw":
            _card_damage(state, card, n[2] if take else n[0])
            if take:
                state.draw(n[3])
        elif k == "spend_hit":
            _card_damage(state, card, n[2] if take else n[0], hydro=take)
        elif k == "spend_energy":
            state.draw(n[0])
            if take:
                state.player.energy += n[2]
    elif k == "block_spend_all":
        _card_block(state, card, n[0])
        held = f.fanfare
        if held > 0 and d.spend_all(state, card, spec):
            spend(state, held)
            _card_damage(state, card, n[1] * held)
    elif k == "hit_restore":
        _card_damage(state, card, n[0])
        restore(state, n[1])
    elif k == "block_restore":
        _card_block(state, card, n[0])
        restore(state, n[1])
    elif k == "ousia":
        _card_damage(state, card, n[0] + n[1] * f.gained_this_turn)
    elif k == "bravura":
        held = f.fanfare
        if held > 0:
            spend(state, held)
        _card_damage(state, card, n[0] + n[1] * held)
    elif k == "rejoice":
        held = f.fanfare
        if held > 0:
            spend(state, held)
            _card_damage(state, card, n[0] * held, all_enemies=True)
    elif k == "power":
        f.powers[spec.member] += n[0]
    elif k == "guest":
        summon(state, spec.member)
    else:                                    # pragma: no cover
        raise ValueError(f"unknown kind {k!r}")


def close_ledger(state) -> None:
    f = _f(state)
    f.ledger["fanfare_end"] = f.fanfare
    f.ledger["unrepaid_end"] = f.drained


READINGS: tuple[str, ...] = (
    "The half-line: a Drain N is legal when HP - N >= Max HP / 2.",
    "A Drain's HP loss is not routed through `note_player_hp_loss` (so no "
    "other arm's hook sees it); it prints its Fanfare directly.",
    "Enemy hits (and any other true HP loss) print Fanfare through the "
    "`note_player_hp_loss` hook, 1 per HP.",
    "Salon Solitaire's Restore comes after the guests act, at the end of her "
    "turn, before enemies act.",
    "Critics' Darling deals the (Revelry-doubled) gain to a random enemy, "
    "unpowered. Endless Waltz deals the HP Restored, unpowered.",
    "Guest acts and lines are unpowered (Strength and Weak do not touch "
    "them).",
    "Neuvillette's act Drains 4 if legal (a real Drain: Fanfare, Salon's "
    "Encore and Wriothesley all see it), else deals the dry 3.",
    "Card damage aims at the engine's bound aim (the lowest-HP enemy).",
)
