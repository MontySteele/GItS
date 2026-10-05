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

FURINA'S ARM RUNS ON THESE RULES (2026-10-05): `tier0.engine.furina_stage`
attaches an `Ftd` to the sheet's Furina at every combat's start (curtain call
on, the entry line) and its `stage_*` ops call the verbs below, so the
release Furina and this slice are one implementation. The slice's own
`Spec` rows and probe stay as the proposal's instrument.

THE RULES (paper sec.2, with sec.16's two changes: Restore is now REPAY, and
the curtain call is the default; sec.17's edit: Curtain Rise's Drain mode
deals 12; and `review/active/furina-pool-40-2026-10-05.md` sec.2: Universal
Revelry reads Drain and Repay again, never hits):

1. DRAIN N. Lose N HP for the bigger effect (a mode on some cards, a fixed
   price on others). It cannot be paid if it would take her below the line:
   half the HP she started this combat with (the `entry` line; the `std`
   family of variants measures half of Max HP, Genshin's rule). HP lost to
   a Drain is DRAINED: the engine keeps the count. A fixed-price card whose
   Drain cannot be paid cannot be played (`playable`), Hemokinesis's shape.
2. REPAY N. Regain up to N of your drained HP. Repay never returns HP an
   enemy took (the invariant: HP + drained <= Max HP, and Repay <= drained).
3. FANFARE. One number on Furina, no cap, no fade. She gains 1 for every HP
   she loses (to a Drain, to an enemy, to anything) and for every HP she
   Repays. Spend N on cards pays it; a spend-all is one Spend.
4. SALON SOLITAIRE (starting relic). At the end of your turn, Repay 2.
5. GUEST STARS. Three seats; a guest acts at the end of her turn; a guest
   onto a full stage makes the oldest guest leave, acting once more as it
   goes; a second copy of a guest on stage makes it act and stay.
6. THE CURTAIN CALL (sec.16, the default variant `curtain_call`). When a
   combat ends, all drained HP returns (`close_ledger`). Under
   `no_curtain_call` unrepaid drained HP is lost when the fight ends, the
   paper's old rule. Either way `fight_record` reports the unrepaid HP at
   the curtain (under the curtain call, the HP the curtain returned).

RISING APPLAUSE ALWAYS SPENDS ALL (sec.15 point 7): the face is the rule;
whether to play it now is the only choice. The `legacy` variant (the old
baseline: no curtain call, and the pilot may decline Rising Applause's
spend) is kept for reference only.

PROBE-ONLY ROWS (`in_slice` False, never drafted). The `ftd_rising_applause_6`
/ `_all2` alternatives (rarity "probe"), The Crowd Gasps and Neuvillette:
rows a probe deck uses, kept under sec.15/16's rules. The draft pool is the
slice's 24 and the pool-40 paper's ten (sec.3), 34 in all.

THE K3 SWITCHES (`K3_SWITCHES`, under the `entry` line and the old no-curtain
rule). A Drain the Singer fully repays costs no HP and prints Fanfare twice
(on the loss and on the Repay); these variants price it:
- `singer_rests`: Salon Solitaire Repays only at the end of a turn in
  which no Drain happened (`Ftd.singer_rests`).
- `repay_no_fanfare`: Repay prints no Fanfare (`Ftd.repay_fanfare`
  False). HP loss from any cause still prints it.
- `both`: the two together.
- `singer1`: the Singer Repays 1 (the paper's named lever), for comparison.
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
SINGER_REPAY = 2             # Salon Solitaire: end of turn, Repay 2

GUESTS = ("charlotte", "wriothesley", "lynette", "clorinde",
          "sigewinne", "neuvillette", "lyney", "chevreuse")
GUEST_ELEMENTS = {"wriothesley": "cryo", "clorinde": "electro",
                  "lynette": "anemo", "neuvillette": "hydro",
                  "lyney": "pyro"}

# Guest numbers (paper sec.16; Sigewinne and Neuvillette from sec.7/15).
CHARLOTTE_ACT_REPAY = 2
SIGEWINNE_ACT_REPAY = 2      # the pool-40 paper: "Repay 2." (was 3)
WRIOTHESLEY_ACT = 4
LYNETTE_ACT = 3              # Anemo to an enemy with an aura
CLORINDE_ACT = 6
CLORINDE_PER_REPAY = 2       # "deal twice that much Electro"
NEUVILLETTE_HYDRO_BONUS = 2
SALON_ENCORE_DAMAGE = 3      # Power: whenever you Drain, 3 to ALL
THUNDEROUS_DAMAGE = 3        # Power: whenever you Spend, 3 to ALL
# The pool to 39 (review/active/furina-pool-40-2026-10-05.md sec.3).
LYNEY_LINE_DROP = 10         # line: "Your Drain line is 10 HP lower."
LYNEY_ACT_DRAIN = 2          # act: "Drain 2: deal 8 Pyro damage to ALL."
LYNEY_ACT = 8
CHEVREUSE_ACT = 4            # act: "Deal 4 damage to a random enemy."
CHEVREUSE_LINE_VULNERABLE = 1  # line: each Spend, 1 Vulnerable (random)
FIVE_CENTURY_LINE = 1        # A Five-Century Act: Drain down to 1 HP
FOUNTAIN_TURNS = 3           # Fountain of Lucine: the next 3 turns


def _new_ledger() -> dict:
    return {
        "gained": 0, "gained_by": collections.Counter(),
        "spent": 0, "spends": 0,
        "drained": 0, "drains": 0, "drain_offers": 0, "card_drains": 0,
        "fixed_drains": 0,
        "drain_blocked_by_line": 0,
        "repaid": 0, "repay_wasted": 0, "singer_skipped": 0,
        "spend_offers": 0,
        "guest_acts": collections.Counter(), "bows": 0,
        "started_at_or_below_half": False,
        "fanfare_end": 0, "unrepaid_end": 0, "curtain_repaid": 0,
        "bis_kept": 0, "fountain_repaid": 0,
        "damage_by_turn": collections.Counter(),
    }


@dataclass
class Ftd:
    fanfare: int = 0
    drained: int = 0                 # HP lost to Drains and not yet Repaid
    gained_this_turn: int = 0
    spent_this_turn: int = 0
    repaid_this_turn: int = 0
    drained_hp_this_turn: int = 0    # Neuvillette's act reads it
    charlotte_drew: bool = False
    lynette_fired: bool = False
    ousia_drew: bool = False         # Ousia Surge: drawn this turn
    fountains: list = field(default_factory=list)   # [amount, turns left]
    fountain_seen: int = 0           # the arm power's total already scheduled
    energy_next: int = 0             # Salon's Tab: Energy next turn
    stage: list = field(default_factory=list)
    powers: collections.Counter = field(default_factory=collections.Counter)
    singer: int = SINGER_REPAY
    hit_fanfare: bool = True         # variant: do enemy hits print Fanfare?
    line: float = 0.5                # variant: the Drain line, share of Max HP
    entry_hp: int = 0                # HP at the start of this combat
    line_from_entry: bool = False    # variant: the line is half of entry HP
    singer_rests: bool = False       # variant: no Singer on a turn she Drained
    repay_fanfare: bool = True       # variant: does Repay print Fanfare?
    curtain_call: bool = False       # variant: drained HP returns at the end
    rising_optional: bool = False    # legacy: the pilot may skip the spend
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
# The cards (paper sec.16, the slice's rows; numbers are the instrument's).
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
    in_slice: bool = True      # False: a probe deck's row, never drafted
    exhaust: bool = False


CARDS: dict[str, Spec] = {
    # --- Starter ---
    # Curtain Rise: Deal 7. Drain 3: deal 12 instead. (sec.17: was 14.)
    "ftd_curtain_rise": Spec("Curtain Rise", 1, "attack", "basic",
                             "drain_hit", (7, 3, 12)),
    # Rising Applause: Gain 5 Block. Spend all your Fanfare and deal that
    # much damage. (Always spends: sec.15 point 7.)
    "ftd_rising_applause": Spec("Rising Applause", 1, "skill", "basic",
                                "block_spend_all", (5, 1)),
    # Probe alternatives for the starter's Spend card: a fixed Spend 6 for
    # 12, and spend-all at 2 per point.
    "ftd_rising_applause_6": Spec("Rising Applause (Spend 6)", 1, "skill",
                                  "probe", "block_spend_hit", (5, 6, 12),
                                  in_slice=False),
    "ftd_rising_applause_all2": Spec("Rising Applause (spend-all, 2)", 1,
                                     "skill", "probe", "block_spend_all",
                                     (5, 2), in_slice=False),
    # --- Drain (5) ---
    # Mademoiselle Crabaletta (2): Drain 5. Deal 24 damage.
    "ftd_crabaletta": Spec("Mademoiselle Crabaletta", 2, "attack", "common",
                           "drain_fixed_hit", (5, 24)),
    # Soloist's Solicitation (0): Drain 2. Deal 8 damage.
    "ftd_solicitation": Spec("Soloist's Solicitation", 0, "attack", "common",
                             "drain_fixed_hit", (2, 8)),
    # Surintendante Chevalmarin (1): Deal 4 Hydro damage to ALL enemies.
    # Drain 3: deal 8 instead.
    "ftd_chevalmarin": Spec("Surintendante Chevalmarin", 1, "attack",
                            "common", "drain_aoe", (4, 3, 8)),
    # Gentilhomme Usher (1): Gain 7 Block. Drain 3: gain 13 instead.
    "ftd_usher": Spec("Gentilhomme Usher", 1, "skill", "common",
                      "drain_block", (7, 3, 13)),
    # Salon's Tab (1): Draw 2 cards. Drain 4: also gain 2 Energy next turn.
    # (2026-10-05: was 0-cost Draw 1 / +1; the 0-cost Tab made Guest+ and
    # Tab+ an infinite.)
    "ftd_salons_tab": Spec("Salon's Tab", 1, "skill", "uncommon",
                           "drain_tab", (2, 4, 2)),
    # --- Repay (4) ---
    # Surging Waters (1, Attack): Deal 6 damage. Repay 3.
    "ftd_surging_waters": Spec("Surging Waters", 1, "attack", "common",
                               "hit_repay", (6, 3)),
    # Hymn of Many Waters (1): Gain 8 Block. Repay 3.
    "ftd_hymn": Spec("Hymn of Many Waters", 1, "skill", "common",
                     "block_repay", (8, 3)),
    # Pneuma Refrain (1): Repay 5. Draw 2 cards.
    "ftd_pneuma_refrain": Spec("Pneuma Refrain", 1, "skill", "uncommon",
                               "repay_draw", (5, 2)),
    # Singer of Many Waters (1): Repay all your drained HP. Exhaust.
    "ftd_singer": Spec("Singer of Many Waters", 1, "skill", "rare",
                       "repay_all", (), exhaust=True),
    # --- Fanfare outlets (6) ---
    # Tidal Flourish (1): Deal 5 to ALL. Spend 6: deal 12 Hydro to ALL
    # instead.
    "ftd_tidal_flourish": Spec("Tidal Flourish", 1, "attack", "common",
                               "spend_aoe", (5, 6, 12)),
    # Spirited Aria (1): Deal 8. Spend 5: deal 13 and draw 2 instead.
    "ftd_spirited_aria": Spec("Spirited Aria", 1, "attack", "common",
                              "spend_draw", (8, 5, 13, 2)),
    # Quick Flourish (0): Spend 4. Deal 11 Hydro damage.
    "ftd_quick_flourish": Spec("Quick Flourish", 0, "attack", "common",
                               "spend_fixed_hit", (4, 11)),
    # Standing Ovation (1): Spend all your Fanfare. Deal that much damage to
    # ALL enemies.
    "ftd_standing_ovation": Spec("Standing Ovation", 1, "attack", "common",
                                 "rejoice", (1,)),
    # Interval Bell (0): v2 text after #900: Draw 1 card. Spend 3: draw 1
    # card and gain 1 Energy instead.
    "ftd_interval_bell": Spec("Interval Bell", 0, "skill", "common",
                              "spend_energy", (1, 3, 1)),
    # Bravura (1): Spend all your Fanfare. Deal 6, plus 2 per point.
    "ftd_bravura": Spec("Bravura", 1, "attack", "uncommon", "bravura",
                        (6, 2)),
    # --- Powers (3, Uncommon) ---
    # Salon's Encore (1): Whenever you Drain, deal 3 damage to ALL enemies.
    "ftd_salon_encore": Spec("Salon's Encore", 1, "power", "uncommon",
                             "power", (1,), "salon_encore"),
    # Endless Waltz (1): Whenever you Repay, deal that much damage to a
    # random enemy.
    "ftd_endless_waltz": Spec("Endless Waltz", 1, "power", "uncommon",
                              "power", (1,), "endless_waltz"),
    # Thunderous Applause (1): Whenever you Spend, deal 3 damage to ALL
    # enemies.
    "ftd_thunderous": Spec("Thunderous Applause", 1, "power", "uncommon",
                           "power", (1,), "thunderous"),
    # --- Guests (4, cost 1) ---
    "ftd_charlotte": Spec("Guest Star: Charlotte", 1, "skill", "common",
                          "guest", (), "charlotte"),
    "ftd_wriothesley": Spec("Guest Star: Wriothesley", 1, "skill",
                            "uncommon", "guest", (), "wriothesley"),
    "ftd_lynette": Spec("Guest Star: Lynette", 1, "skill", "uncommon",
                        "guest", (), "lynette"),
    "ftd_clorinde": Spec("Guest Star: Clorinde", 1, "skill", "rare",
                         "guest", (), "clorinde"),
    # --- Rares (2 more) ---
    # Universal Revelry (Power, 2): "Whenever you Drain or Repay, gain that
    # much additional Fanfare." (The pool-40 paper, sec.2: hits no longer
    # count; a second copy adds again.)
    "ftd_revelry": Spec("Universal Revelry", 2, "power", "rare", "power",
                        (1,), "revelry"),
    # Let the People Rejoice (2): Spend all your Fanfare. Deal 2 to ALL per
    # point.
    "ftd_rejoice": Spec("Let the People Rejoice", 2, "attack", "rare",
                        "rejoice", (2,)),
    # --- The pool to 39 (review/active/furina-pool-40-2026-10-05.md
    # sec.3): seven Uncommons and three Rares. ---
    # Grand Deluge (2): Drain 6. Deal 16 Hydro damage to ALL enemies.
    "ftd_grand_deluge": Spec("Grand Deluge", 2, "attack", "uncommon",
                             "drain_fixed_aoe", (6, 16)),
    # Ousia Surge (Power, 1): The first time you Drain each turn, draw 1.
    "ftd_ousia_surge": Spec("Ousia Surge", 1, "power", "uncommon", "power",
                            (1,), "ousia_surge"),
    # Guest Star: Lyney (1). Line: your Drain line is 10 HP lower. Act:
    # Drain 2: deal 8 Pyro damage to ALL enemies (skipped below the line).
    "ftd_lyney": Spec("Guest Star: Lyney", 1, "skill", "uncommon", "guest",
                      (), "lyney"),
    # A Five-Century Act (Power, 2): You can Drain down to 1 HP.
    "ftd_five_century": Spec("A Five-Century Act", 2, "power", "rare",
                             "power", (1,), "five_century"),
    # Fountain of Lucine (1): At the start of your next 3 turns, Repay 3.
    "ftd_fountain": Spec("Fountain of Lucine", 1, "skill", "uncommon",
                         "fountain", (3,)),
    # Hold the Stage (1): Gain 6 Block. Spend 6: gain 16 instead.
    "ftd_hold_the_stage": Spec("Hold the Stage", 1, "skill", "uncommon",
                               "spend_block", (6, 6, 16)),
    # Guest Star: Chevreuse (1). Line: whenever you Spend, apply 1
    # Vulnerable to a random enemy. Act: deal 4 damage to a random enemy.
    "ftd_chevreuse": Spec("Guest Star: Chevreuse", 1, "skill", "uncommon",
                          "guest", (), "chevreuse"),
    # Bis! (Power, 1): Whenever you Spend all your Fanfare, keep half of it.
    "ftd_bis": Spec("Bis!", 1, "power", "rare", "power", (1,), "bis"),
    # Critics' Darling (Power, 2, Rare): Whenever you Drain or Repay, deal
    # that much damage to a random enemy.
    "ftd_critics_darling": Spec("Critics' Darling", 2, "power", "rare",
                                "power", (1,), "critics_darling"),
    # Sigewinne (Uncommon). Line: whenever you Repay, gain that much Block.
    # Act: Repay 2.
    "ftd_sigewinne": Spec("Guest Star: Sigewinne", 1, "skill", "uncommon",
                          "guest", (), "sigewinne"),
    # --- Beyond the slice: rows a probe deck needs (never drafted) ---
    # The Crowd Gasps (Power, 1): Whenever an enemy makes you lose HP, gain
    # that much Fanfare (the `tragedy` deck; matters only without hits).
    "ftd_crowd_gasps": Spec("The Crowd Gasps", 1, "power", "uncommon",
                            "power", (1,), "crowd_gasps", in_slice=False),
    # Neuvillette (sec.15 point 4). Line: Hydro damage deals 2 more. Act:
    # deal Hydro damage to ALL enemies equal to the HP you drained this
    # turn. He Drains nothing himself.
    "ftd_neuvillette": Spec("Guest Star: Neuvillette", 2, "skill", "rare",
                            "guest", (), "neuvillette", in_slice=False),
}

STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "ftd_curtain_rise", "ftd_rising_applause",
)

#: Modal Drain cards (the plain mode is a real line): the K3 take rate.
DRAIN_KINDS = ("drain_hit", "drain_aoe", "drain_block", "drain_tab")
#: Fixed-price Drain cards: unplayable when the Drain cannot be paid.
FIXED_DRAIN_KINDS = ("drain_fixed_hit", "drain_fixed_aoe")
SPEND_KINDS = ("block_spend_hit", "spend_aoe", "spend_draw", "spend_energy",
               "spend_block")
FIXED_SPEND_KINDS = ("spend_fixed_hit",)


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
                character=CHARACTER, exhaust=spec.exhaust)


#: Design variants the probe can switch per run: (singer, hit_fanfare, line).
VARIANTS = {"std": (2, True, 0.5), "nohit": (2, False, 0.5),
            "s3": (3, True, 0.5), "nohit_s3": (3, False, 0.5),
            "s1": (1, True, 0.5), "nohit_s1": (1, False, 0.5),
            "nohit_l33": (2, False, 1 / 3), "nohit_l40": (2, False, 0.4),
            "entry": (2, True, 0.5), "entry_nohit": (2, False, 0.5),
            "entry_s1": (1, True, 0.5)}

#: The K3 variants: the `entry` rules (no curtain call) plus engine switches.
K3_SWITCHES = {
    "singer_rests": (2, {"singer_rests": True}),
    "repay_no_fanfare": (2, {"repay_fanfare": False}),
    "both": (2, {"singer_rests": True, "repay_fanfare": False}),
    "singer1": (1, {}),
}
#: The sec.16 rule variants, all on the `entry` line.
RULE_SWITCHES = {
    "curtain_call": (2, {"curtain_call": True}),     # sec.16: the default
    "no_curtain_call": (2, {}),                      # the old end-of-fight
    "legacy": (2, {"rising_optional": True}),        # the old baseline
}
VARIANT_SWITCHES = {**K3_SWITCHES, **RULE_SWITCHES}
for _name, (_singer, _sw) in VARIANT_SWITCHES.items():
    VARIANTS[_name] = (_singer, True, 0.5)

DEFAULT_VARIANT = "curtain_call"   # sec.16: the entry line + curtain call


def build_player(card_ids, hp: int | None = None, max_hp: int = HP,
                 singer: int = SINGER_REPAY,
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
# The loop: Drain, Repay, Fanfare.
# ----------------------------------------------------------------------
def _player_power(player, key: str) -> int:
    """A pool-40 Power's copies on this player: the slice's own count and
    the arm's (`furina_stage`'s `fs_*` ids)."""
    f = getattr(player, "ftd", None)
    own = int(f.powers[key]) if f is not None else 0
    from tier0.engine import furina_stage           # late: avoids a cycle
    arm_id = furina_stage.ARM_POWER_IDS.get(key)
    powers = getattr(player, "powers", None) or {}
    return own + (int(powers.get(arm_id, 0) or 0) if arm_id else 0)


def half_line(player) -> float:
    """The Drain line. A Five-Century Act puts it at 1 HP; Lyney on stage
    lowers it by 10, never below 1."""
    f = getattr(player, "ftd", None)
    if f is not None and f.line_from_entry:
        line = f.entry_hp * f.line
    else:
        line = player.max_hp * (f.line if f is not None else 0.5)
    if f is None:
        return line
    if _player_power(player, "five_century"):
        return float(FIVE_CENTURY_LINE)
    if "lyney" in f.stage:
        return max(float(FIVE_CENTURY_LINE), line - LYNEY_LINE_DROP)
    return line


def can_drain(state, n: int) -> bool:
    p = state.player
    return n > 0 and p.hp - n >= half_line(p)


def playable(state, card) -> bool:
    """A fixed price must be payable: a fixed Drain above the line, a fixed
    Spend from the bank. Every other row (and any non-slice card) is True."""
    spec = spec_of(card)
    if spec is None or not live(state.player):
        return True
    if spec.kind in FIXED_DRAIN_KINDS:
        return can_drain(state, spec.n[0])
    if spec.kind in FIXED_SPEND_KINDS:
        return _f(state).fanfare >= spec.n[0]
    return True


def _arm_power(state, key: str) -> int:
    """A Power's stacks on Furina's ARM (`furina_stage`), whose sheet rows
    apply `fs_*` ids through `apply_power`; 0 for the slice's own players."""
    from tier0.engine import furina_stage           # late: avoids a cycle
    powers = getattr(state.player, "powers", None) or {}
    return int(powers.get(furina_stage.ARM_POWER_IDS[key], 0) or 0)


def revelry_copies(state) -> int:
    """Universal Revelry's copies, the slice's and the arm's."""
    return int(_f(state).powers["revelry"]) + _arm_power(state, "revelry")


def gain(state, amount: int, source: str) -> None:
    """Fanfare in. Universal Revelry no longer multiplies a gain (the pool-40
    paper, sec.2); it adds its own gain to a Drain or a Repay
    (`_loop_readers`)."""
    if amount <= 0 or not live(state.player):
        return
    f = _f(state)
    f.fanfare += amount
    f.gained_this_turn += amount
    f.ledger["gained"] += amount
    f.ledger["gained_by"][source] += amount
    state.emit("ftd_gain", amount=amount, source=source, fanfare=f.fanfare)


def _loop_readers(state, n: int) -> None:
    """The readers of a Drain or a Repay of N (never a hit), sec.15's
    texts: Universal Revelry gains N more Fanfare per copy, and Critics'
    Darling deals N per copy to a random enemy. Neither triggers itself."""
    copies = revelry_copies(state)
    if copies and n > 0:
        gain(state, n * copies, "revelry")
    critics = _player_power(state.player, "critics_darling")
    if critics and state.living_enemies:
        _hit(state, state.rng.choice(state.living_enemies), n * critics,
             None)


def spend(state, amount: int) -> bool:
    """One Spend (a spend-all is one). Thunderous Applause reads it."""
    f = _f(state)
    if amount <= 0 or f.fanfare < amount:
        return False
    f.fanfare -= amount
    f.spent_this_turn += amount
    f.ledger["spent"] += amount
    f.ledger["spends"] += 1
    state.emit("ftd_spend", amount=amount, fanfare=f.fanfare)
    thunder = (THUNDEROUS_DAMAGE * f.powers["thunderous"]
               + _arm_power(state, "thunderous"))
    if thunder:
        for enemy in list(state.living_enemies):
            _hit(state, enemy, thunder, None)
    if "chevreuse" in f.stage and state.living_enemies:
        from tier0.engine import powers as _powers
        _powers.apply_power(state, state.rng.choice(state.living_enemies),
                            "vulnerable", CHEVREUSE_LINE_VULNERABLE)
    return True


def spend_all(state) -> int:
    """"Spend all your Fanfare": one Spend of everything held (nothing held
    is no Spend). Bis! keeps half of it, rounded down; the spend and what
    it pays for are the whole bank. Returns what was spent."""
    f = _f(state)
    held = f.fanfare
    if held <= 0 or not spend(state, held):
        return 0
    if _player_power(state.player, "bis"):
        kept = held // 2
        f.fanfare += kept
        f.ledger["bis_kept"] += kept
    return held


def drain(state, n: int) -> bool:
    """Rule 1. Lose N HP (not below the line), mark it drained, gain N
    Fanfare, then the Drain readers."""
    p = state.player
    f = _f(state)
    if not can_drain(state, n):
        return False
    p.hp -= n
    f.drained += n
    f.drained_this_turn = True
    f.drained_hp_this_turn += n
    f.ledger["drained"] += n
    f.ledger["drains"] += 1
    state.hp_lost_this_turn += n
    state.emit("ftd_drain", amount=n, hp=p.hp, drained=f.drained)
    gain(state, n, "drain")
    _loop_readers(state, n)
    encore = (SALON_ENCORE_DAMAGE * f.powers["salon_encore"]
              + _arm_power(state, "salon_encore"))
    if encore:
        for enemy in list(state.living_enemies):
            _hit(state, enemy, encore, None)
    if "wriothesley" in f.stage and state.living_enemies:
        _hit(state, state.rng.choice(state.living_enemies), n, "cryo")
    surge = _player_power(p, "ousia_surge")
    if surge and not f.ousia_drew and not state.over:
        f.ousia_drew = True
        state.draw(surge)
    return True


def repay(state, n: int) -> int:
    """Rule 2. Regain up to N drained HP; gain that much Fanfare; then the
    Repay readers. Returns HP repaid."""
    p = state.player
    f = _f(state)
    f.drained = min(f.drained, max(0, p.max_hp - p.hp))
    amount = min(n, f.drained)
    f.ledger["repay_wasted"] += n - amount
    if amount <= 0:
        return 0
    p.hp += amount
    f.drained -= amount
    f.repaid_this_turn += amount
    f.ledger["repaid"] += amount
    state.emit("ftd_repay", amount=amount, hp=p.hp, drained=f.drained)
    if f.repay_fanfare:
        gain(state, amount, "repay")
    _loop_readers(state, amount)
    for _ in range(int(f.powers["endless_waltz"])
                   + _arm_power(state, "endless_waltz")):
        if not state.living_enemies:
            break
        _hit(state, state.rng.choice(state.living_enemies), amount, None)
    if "sigewinne" in f.stage:
        p.block += amount
    if "clorinde" in f.stage and state.living_enemies:
        _hit(state, state.rng.choice(state.living_enemies),
             CLORINDE_PER_REPAY * amount, "electro")
    if "charlotte" in f.stage and not f.charlotte_drew and not state.over:
        f.charlotte_drew = True
        state.draw(1)
    return amount


def on_hp_loss(state, n: int) -> None:
    """Hook from `resources.note_player_hp_loss`: true HP loss from any
    source but a Drain (enemy hits, statuses) prints Fanfare 1:1. Lynette's
    line pays it again the first time each turn."""
    if n <= 0 or not live(state.player):
        return
    f = _f(state)
    if f.hit_fanfare or f.powers["crowd_gasps"]:
        gain(state, n, "hit")
    if "lynette" in f.stage and not f.lynette_fired:
        f.lynette_fired = True
        gain(state, n, "lynette")


def energy_kept(state) -> int:
    """Hook after the turn's Energy refill: Salon's Tab's Energy arrives
    next turn (the Interval Bell fix, #900). 0 for anyone else."""
    if not live(state.player):
        return 0
    f = _f(state)
    out, f.energy_next = f.energy_next, 0
    return out


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
        repay(state, CHARLOTTE_ACT_REPAY)
    elif member == "sigewinne":
        repay(state, SIGEWINNE_ACT_REPAY)
    elif member == "wriothesley":
        if living:
            _hit(state, state.rng.choice(living), WRIOTHESLEY_ACT, "cryo")
    elif member == "lynette":
        aura = [e for e in living if getattr(e, "aura", None)]
        if aura:
            _hit(state, state.rng.choice(aura), LYNETTE_ACT, "anemo")
    elif member == "clorinde":
        if living:
            _hit(state, state.rng.choice(living), CLORINDE_ACT, "electro")
    elif member == "neuvillette":
        dmg = f.drained_hp_this_turn
        if dmg > 0:
            for enemy in living:
                _hit(state, enemy, dmg, "hydro")
    elif member == "lyney":
        # "Drain 2: deal 8 Pyro damage to ALL enemies." Below the line the
        # act skips: no Drain and no damage.
        if can_drain(state, LYNEY_ACT_DRAIN) and drain(state, LYNEY_ACT_DRAIN):
            for enemy in list(state.living_enemies):
                _hit(state, enemy, LYNEY_ACT, "pyro")
    elif member == "chevreuse":
        if living:
            _hit(state, state.rng.choice(living), CHEVREUSE_ACT, None)
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
    f.repaid_this_turn = 0
    f.drained_hp_this_turn = 0
    f.drained_this_turn = False
    f.charlotte_drew = False
    f.lynette_fired = False
    f.ousia_drew = False


def turn_start(state) -> None:
    """After her draw: Fountain of Lucine's Repays. What the arm's power
    took in since the last turn start is scheduled for three turns (the C#
    `FurinaStage.FountainRepays` reads its power the same way); then each
    schedule Repays its amount, one Repay per schedule."""
    if not live(state.player):
        return
    f = _f(state)
    applied = _arm_fountain(state)
    if applied > f.fountain_seen:
        f.fountains.append([applied - f.fountain_seen, FOUNTAIN_TURNS])
        f.fountain_seen = applied
    due = [amount for amount, _turns in f.fountains]
    for item in f.fountains:
        item[1] -= 1
    f.fountains = [item for item in f.fountains if item[1] > 0]
    for amount in due:
        if state.over or not state.player.alive:
            break
        f.ledger["fountain_repaid"] += repay(state, amount)


def _arm_fountain(state) -> int:
    from tier0.engine import furina_stage           # late: avoids a cycle
    powers = getattr(state.player, "powers", None) or {}
    return int(powers.get(furina_stage.FOUNTAIN_OF_LUCINE, 0) or 0)


def end_of_turn(state) -> None:
    """Guests act in seat order, then Salon Solitaire's Singer Repays
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
        repay(state, f.singer)


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
    if k == "drain_fixed_aoe":
        price, dmg = n
        if drain(state, price):
            f.ledger["fixed_drains"] += 1
            _card_damage(state, card, dmg, all_enemies=True, hydro=True)
        return
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
        if k == "drain_hit":
            _card_damage(state, card, big if take else plain)
        elif k == "drain_aoe":
            _card_damage(state, card, big if take else plain,
                         all_enemies=True, hydro=True)
        elif k == "drain_block":
            _card_block(state, card, big if take else plain)
        else:                                       # drain_tab
            state.draw(plain)
            if take:
                f.energy_next += big
    elif k in FIXED_DRAIN_KINDS:
        price, dmg = n
        if drain(state, price):         # `playable` gated it; belt and braces
            f.ledger["fixed_drains"] += 1
            _card_damage(state, card, dmg)
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
        elif k == "spend_energy":
            state.draw(n[0])
            if take:
                state.player.energy += n[2]
        elif k == "spend_block":
            _card_block(state, card, n[2] if take else n[0])
    elif k in FIXED_SPEND_KINDS:
        price, dmg = n
        if spend(state, price):
            _card_damage(state, card, dmg, hydro=True)
    elif k == "block_spend_all":
        _card_block(state, card, n[0])
        held = f.fanfare
        if held > 0 and (not f.rising_optional
                         or d.spend_all(state, card, spec)):
            spend_all(state)
            _card_damage(state, card, n[1] * held)
    elif k == "hit_repay":
        _card_damage(state, card, n[0])
        repay(state, n[1])
    elif k == "block_repay":
        _card_block(state, card, n[0])
        repay(state, n[1])
    elif k == "repay_draw":
        repay(state, n[0])
        state.draw(n[1])
    elif k == "repay_all":
        repay(state, f.drained)
    elif k == "bravura":
        held = spend_all(state)
        _card_damage(state, card, n[0] + n[1] * held)
    elif k == "rejoice":
        held = spend_all(state)
        if held > 0:
            _card_damage(state, card, n[0] * held, all_enemies=True)
    elif k == "fountain":
        f.fountains.append([n[0], FOUNTAIN_TURNS])
    elif k == "power":
        f.powers[spec.member] += n[0]
    elif k == "guest":
        summon(state, spec.member)
    else:                                    # pragma: no cover
        raise ValueError(f"unknown kind {k!r}")


def close_ledger(state) -> None:
    """The fight's end: record the bank and the unrepaid HP, then (under the
    curtain call, if she lived) return every drained HP."""
    f = _f(state)
    f.ledger["fanfare_end"] = f.fanfare
    f.ledger["unrepaid_end"] = f.drained
    p = state.player
    if f.curtain_call and p.alive and f.drained > 0:
        back = min(f.drained, max(0, p.max_hp - p.hp))
        p.hp += back
        f.ledger["curtain_repaid"] += back
        f.drained = 0


READINGS: tuple[str, ...] = (
    "The line: a Drain N is legal when HP - N >= half the HP she started "
    "the combat with (the `entry` line).",
    "A Drain's HP loss is not routed through `note_player_hp_loss` (so no "
    "other arm's hook sees it); it prints its Fanfare directly.",
    "Enemy hits (and any other true HP loss) print Fanfare through the "
    "`note_player_hp_loss` hook, 1 per HP; Lynette's line reads the same "
    "hook, so a status's HP loss counts as an enemy's.",
    "Salon Solitaire's Repay comes after the guests act, at the end of her "
    "turn, before enemies act.",
    "Universal Revelry adds the Drain or Repay amount again per copy (the "
    "pool-40 paper, sec.2); hits and Lynette's line are not read. Critics' "
    "Darling's damage reads the Drain or Repay amount, unpowered, per "
    "copy. Endless Waltz deals the HP Repaid, unpowered, once per copy.",
    "Lyney's act skips entirely below the line (no Drain, no damage); his "
    "line lowers the line by 10 while he is on stage, never below 1 HP. A "
    "Five-Century Act's line is 1 HP whatever else is true.",
    "Bis! keeps half a spend-all, rounded down; a second copy adds nothing. "
    "Fountain of Lucine's Repays come after her draw, one per play.",
    "Guest acts and lines are unpowered (Strength and Weak do not touch "
    "them).",
    "Neuvillette's act deals the HP drained this turn (gross of Repays) to "
    "ALL as Hydro; it Drains nothing.",
    "The curtain call returns drained HP in `close_ledger`, after the "
    "fight's record is taken; the probe calls it on every fight.",
    "Card damage aims at the engine's bound aim (the lowest-HP enemy).",
)
