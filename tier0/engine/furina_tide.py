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
   price on others). THE DRAIN LINE RULE (ruled 2026-10-09): the line is
   the HP she started this combat with, minus 1/4 of the Max HP she started
   it with, rounded down (`SHIPPED_LINE`, the default variant's; the `std`
   family of variants measures a share of Max HP, the `entry` family a
   share of entry HP), and a Drain is never refused for it: it may go past
   it. It cannot be paid if
   it would take her to 0 HP (`DRAIN_FLOOR`). HP lost to a Drain is DRAINED,
   in two parts: above the line (`drained_above`) and past it
   (`drained_past`). A fixed-price card whose Drain cannot be paid cannot be
   played (`playable`), Hemokinesis's shape.
2. REPAY N. Regain up to N of your drained HP, the past-line part first.
   Repay never returns HP an enemy took (the invariant: HP + drained <= Max
   HP, and Repay <= drained). THE REPAY FLOOR (ruled 2026-10-09): "Repay N.
   Gain X for any HP it could not Repay." -- `repay_floor` pays Block or
   Vigor for the leftover, N minus the HP returned; the damage cards add it
   to their damage (`repay_left_this_play`).
3. FANFARE. One number on Furina, no cap, no fade. She gains 1 for every HP
   she loses (to a Drain, to an enemy, to anything) and for every HP she
   Repays. Spend N on cards pays it; a spend-all is one Spend.
4. SALON SOLITAIRE (starting relic). At the end of your turn, Repay 2.
   (Shipped Repay 1 since the 2026-10-09 playtest trim; the variants
   below measured 2.)
5. GUEST STARS (the pool to 75's rule, `review/active/furina-pool-growth-
   2026-10-09.md` sec.3, ruled 2026-10-09). Three seats (four with Ensemble
   Cast). A Guest Star exhausts when played and has no effect on summon; a
   guest has a line while on stage and acts at the end of her turn, oldest
   first, then each Showstopper Spends 5 and they act again, then Salon
   Solitaire Repays. A guest onto a full stage makes the oldest leave (no
   act); a guest that leaves (evicted, or sent off by Final Bow) sends its
   card from the exhaust pile to the discard pile. A second copy of a guest
   on stage moves it to the newest seat, with no act. An upgraded Guest Star
   raises its guest's line or act.
6. THE CURTAIN CALL (sec.16, the default variant `curtain_call`). When a
   combat ends, the HP drained above the line returns (`close_ledger`); the
   HP drained past it stays lost unless A Five-Century Act is in play. Under
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
slice's 24, the pool-40 paper's ten (sec.3) and the pool-75 paper's 41
(sec.5), 75 in all.

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
SINGER_REPAY = 1             # Salon Solitaire: end of turn, Repay 1 (2026-10-09 playtest trim, was 2;
                             # the research VARIANTS below keep the 2 they measured)

GUESTS = ("charlotte", "wriothesley", "lynette", "clorinde",
          "sigewinne", "neuvillette", "lyney", "chevreuse",
          # The pool to 75 (2026-10-09): Neuvillette joins the pool, and
          # three more.
          "freminet", "navia", "escoffier")
GUEST_ELEMENTS = {"wriothesley": "cryo", "clorinde": "electro",
                  "lynette": "anemo", "neuvillette": "hydro",
                  "lyney": "pyro", "freminet": "cryo", "navia": "geo",
                  "escoffier": "cryo"}

# Guest numbers (paper sec.16; Sigewinne and Neuvillette from sec.7/15).
CHARLOTTE_ACT_REPAY = 2
SIGEWINNE_ACT_REPAY = 2      # the pool-40 paper: "Repay 2." (was 3)
WRIOTHESLEY_ACT = 4
LYNETTE_ACT = 3              # Anemo to an enemy with an aura
CLORINDE_ACT = 6
CLORINDE_PER_REPAY = 2       # "deal twice that much Electro"
NEUVILLETTE_HYDRO_BONUS = 2  # line: "Your Hydro damage deals 2 more." [3]
SALON_ENCORE_DAMAGE = 3      # Power: whenever you Drain, 3 to ALL
THUNDEROUS_DAMAGE = 3        # Power: whenever you Spend, 3 to ALL
# The pool to 39 (review/active/furina-pool-40-2026-10-05.md sec.3).
LYNEY_LINE_DROP = 10         # line: "Your Drain line is 10 HP lower."
LYNEY_ACT_DRAIN = 2          # act: "Drain 2, never past your line. Deal 8
                             # Pyro damage to ALL enemies."
LYNEY_ACT = 8
CHEVREUSE_ACT = 4            # act: "Deal 4 damage to a random enemy."
CHEVREUSE_LINE_VULNERABLE = 1  # line: each Spend, 1 Vulnerable (random)
DRAIN_FLOOR = 1              # a Drain cannot take her to 0 HP (2026-10-09)
LINE_MAX_HP_DIVISOR = 4      # the Drain line: entry HP minus Max HP // 4
                             # (2026-10-09; FurinaStageLaw.LineMaxHpDivisor)
#: The default variant's line marker: entry HP minus a quarter of entry Max
#: HP. Every other variant's line is a float share.
SHIPPED_LINE = "entry_minus_quarter_max"
FOUNTAIN_TURNS = 3           # Fountain of Lucine: the next 3 turns
# The pool to 75 (review/active/furina-pool-growth-2026-10-09.md, ruled
# 2026-10-09). Sec.3: a guest's upgrade raises its line or its act.
CHARLOTTE_ACT_REPAY_UPGRADED = 4
SIGEWINNE_ACT_REPAY_UPGRADED = 4
WRIOTHESLEY_ACT_UPGRADED = 7
LYNEY_ACT_UPGRADED = 11
LYNETTE_ACT_UPGRADED = 6
CHEVREUSE_LINE_WEAK_UPGRADED = 1   # upgraded line: also 1 Weak
CLORINDE_ACT_UPGRADED = 9
# The Spend paper (review/active/furina-spend-paper-2026-10-10.md pick 2,
# built at its default 2026-10-10): Freminet's act is "Gain 3 Block. Spend
# half your Fanfare (rounded down): gain that much more Block." [6]; his 5 [8]
# Cryo hit left with it. Navia's act Spends half and deals that much as Geo.
FREMINET_ACT_BLOCK = 3             # act: gain 3 Block [6], then the half
FREMINET_ACT_BLOCK_UPGRADED = 6
GUEST_SPEND_DIVISOR = 2            # Navia's and Freminet's acts: half the bank
SPEND_UP_TO_EVERY = 4              # "Draw 1 / hit once more for every 4"
NAVIA_LINE_DISCOUNT = 2            # line: first Spend each turn 2 less [3]
NAVIA_LINE_DISCOUNT_UPGRADED = 3
NEUVILLETTE_HYDRO_BONUS_UPGRADED = 3
ESCOFFIER_ACT = 4                  # act: 4 Cryo to ALL [6]
ESCOFFIER_ACT_UPGRADED = 6
ESCOFFIER_LINE_REPAY = 1           # line: whenever a guest acts, Repay 1
ENSEMBLE_SEATS = 4                 # Ensemble Cast: 4 guest seats
SHOWSTOPPER_SPEND = 5              # Showstopper: end of turn, Spend 5
NEAR_LINE = 5                      # "within 5 HP of your Drain line"
HYMN_THRESHOLD = 4                 # Hymn of Renewal: a Repay of 4 or more HP
PRIMA_DONNA_FANFARE = 10           # Prima Donna: 10 or more Fanfare
REGINA_DRAIN = 3                   # Regina of All Waters: Drain 3
STAR_TURN_FANFARE_PER = 6          # Star Turn: 1 less per 6 Fanfare


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
        # The pool to 75: guest lines that fired (their own log line,
        # sec.3), duplicate moves and leaves.
        "lines": collections.Counter(), "moves": 0, "leaves": 0,
    }


@dataclass
class Ftd:
    fanfare: int = 0
    # HP lost to Drains and not yet Repaid, in two parts (the Drain line
    # rule, 2026-10-09): taken at or above the line, and past it. `drained`
    # is their sum.
    drained_above: int = 0
    drained_past: int = 0
    # Neuvillette's act (2026-10-09): HP she lost since her last turn ended,
    # to Drains and to anything else (the C# `HpLostSinceLastTurn`).
    hp_lost_window: int = 0
    gained_this_turn: int = 0
    spent_this_turn: int = 0
    repaid_this_turn: int = 0
    drained_hp_this_turn: int = 0    # HP drained this turn (the page reads it)
    charlotte_drew: bool = False
    lynette_fired: bool = False
    ousia_drew: bool = False         # Ousia Surge: drawn this turn
    fountains: list = field(default_factory=list)   # [amount, turns left]
    fountain_seen: int = 0           # the arm power's total already scheduled
    energy_next: int = 0             # Salon's Tab: Energy next turn
    stage: list = field(default_factory=list)
    # The pool to 75 (sec.3): which guests on stage were brought or moved by
    # an upgraded Guest Star, and the Guest Star cards each holds (each
    # returns to the discard pile when its guest leaves).
    stage_up: set = field(default_factory=set)
    stage_cards: dict = field(default_factory=dict)
    spends_this_turn: int = 0        # Navia's line and Crescendo
    drains_this_combat: int = 0      # Undercurrent's count
    repays_this_turn: int = 0        # Rising Tide's count
    repaid_this_play: int = 0        # Grand Absolution's "that much"
    repay_left_this_play: int = 0    # the Repay floor's damage
    repay_next: int = 0              # Gentle Current: Repay next turn
    powers: collections.Counter = field(default_factory=collections.Counter)
    singer: int = SINGER_REPAY
    hit_fanfare: bool = True         # variant: do enemy hits print Fanfare?
    line: float | str = 0.5          # variant: the Drain line, share of Max
                                     # HP, or SHIPPED_LINE
    entry_hp: int = 0                # HP at the start of this combat
    entry_max_hp: int = 0            # Max HP at the start of this combat
    line_from_entry: bool = False    # variant: the line is half of entry HP
    singer_rests: bool = False       # variant: no Singer on a turn she Drained
    repay_fanfare: bool = True       # variant: does Repay print Fanfare?
    curtain_call: bool = False       # variant: drained HP returns at the end
    rising_optional: bool = False    # legacy: the pilot may skip the spend
    drained_this_turn: bool = False
    decider: object = None
    ledger: dict = field(default_factory=_new_ledger)

    @property
    def drained(self) -> int:
        """HP lost to Drains and not yet Repaid: both parts."""
        return self.drained_above + self.drained_past

    @drained.setter
    def drained(self, value: int) -> None:
        """A pin's or a probe's board: N drained HP, all above the line."""
        self.drained_above = max(0, int(value))
        self.drained_past = 0


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
    # Mademoiselle Crabaletta (2): Drain 5. Deal 20 damage. (Was 24; the
    # pool-75 round's card numbers, ruled 2026-10-09.)
    "ftd_crabaletta": Spec("Mademoiselle Crabaletta", 2, "attack", "common",
                           "drain_fixed_hit", (5, 20)),
    # Soloist's Solicitation (0): Drain 2. Deal 6 damage. (Was 8, the same
    # ruling.)
    "ftd_solicitation": Spec("Soloist's Solicitation", 0, "attack", "common",
                             "drain_fixed_hit", (2, 6)),
    # Surintendante Chevalmarin (1): Deal 4 Hydro damage to ALL enemies.
    # Drain 3: deal 8 instead.
    "ftd_chevalmarin": Spec("Surintendante Chevalmarin", 1, "attack",
                            "common", "drain_aoe", (4, 3, 8)),
    # Gentilhomme Usher (1): Gain 6 Block. Drain 3: gain 11 instead. (The
    # 2026-10-09 playtest trim, was 7 / 13; mirrored here with the pool to
    # 75 so the sim and the sheet agree.)
    "ftd_usher": Spec("Gentilhomme Usher", 1, "skill", "common",
                      "drain_block", (6, 3, 11)),
    # Salon's Tab (1): Draw 2 cards. Drain 4: also gain 2 Energy next turn.
    # (2026-10-05: was 0-cost Draw 1 / +1; the 0-cost Tab made Guest+ and
    # Tab+ an infinite.)
    "ftd_salons_tab": Spec("Salon's Tab", 1, "skill", "uncommon",
                           "drain_tab", (2, 4, 2)),
    # --- Repay (4) ---
    # Surging Waters (1, Attack): Repay 3. Deal 6 damage, plus 1 for any HP
    # it could not Repay. (The Repay floor, 2026-10-09.)
    "ftd_surging_waters": Spec("Surging Waters", 1, "attack", "common",
                               "hit_repay", (6, 3)),
    # Hymn of Many Waters (1): Gain 8 Block. Repay 3. Gain 1 Block for any
    # HP it could not Repay.
    "ftd_hymn": Spec("Hymn of Many Waters", 1, "skill", "common",
                     "block_repay", (8, 3)),
    # Pneuma Refrain (1): Repay 5. Draw 2 cards.
    "ftd_pneuma_refrain": Spec("Pneuma Refrain", 1, "skill", "uncommon",
                               "repay_draw", (5, 2)),
    # Singer of Many Waters (1): Repay all your drained HP. Exhaust.
    "ftd_singer": Spec("Singer of Many Waters", 1, "skill", "rare",
                       "repay_all", (), exhaust=True),
    # --- Fanfare outlets (6) ---
    # Tidal Flourish (1): Deal 5 Hydro damage to ALL enemies. Spend up to
    # 10: deal 1 more for each. (The Spend paper, 2026-10-10; Uncommon since
    # the 2026-10-09 trim.)
    "ftd_tidal_flourish": Spec("Tidal Flourish", 1, "attack", "uncommon",
                               "upto_aoe", (5, 10)),
    # Spirited Aria (1): Deal 8 damage. Spend up to 8: deal 1 more for each.
    # Draw 1 for every 4 spent. (The Spend paper.)
    "ftd_spirited_aria": Spec("Spirited Aria", 1, "attack", "common",
                              "upto_hit_draw", (8, 8)),
    # Quick Flourish (0): Spend 4. Deal 11 Hydro damage.
    "ftd_quick_flourish": Spec("Quick Flourish", 0, "attack", "common",
                               "spend_fixed_hit", (4, 11)),
    # Standing Ovation (1): Spend all your Fanfare. Deal that much damage to
    # ALL enemies. Uncommon since the pool-75 round (ruled 2026-10-09).
    "ftd_standing_ovation": Spec("Standing Ovation", 1, "attack", "uncommon",
                                 "rejoice", (1,)),
    # Interval Bell (0): v2 text after #900: Draw 1 card. Spend 3: draw 1
    # card and gain 1 Energy instead.
    # Uncommon since the 2026-10-09 trim.
    "ftd_interval_bell": Spec("Interval Bell", 0, "skill", "uncommon",
                              "spend_energy", (1, 3, 1)),
    # Bravura (1): Spend all your Fanfare. Deal 6, plus 2 per point.
    "ftd_bravura": Spec("Bravura", 1, "attack", "uncommon", "bravura",
                        (6, 2)),
    # --- Powers (2, Uncommon; Endless Waltz was cut 2026-10-09) ---
    # Salon's Encore (1): Whenever you Drain, deal 3 damage to ALL enemies.
    "ftd_salon_encore": Spec("Salon's Encore", 1, "power", "uncommon",
                             "power", (1,), "salon_encore"),
    # Thunderous Applause (1): Whenever you Spend, deal 3 damage to ALL
    # enemies.
    "ftd_thunderous": Spec("Thunderous Applause", 1, "power", "uncommon",
                           "power", (1,), "thunderous"),
    # --- Guests (4, cost 1). The pool to 75 (sec.3): every Guest Star
    # exhausts; its card returns when its guest leaves. ---
    "ftd_charlotte": Spec("Guest Star: Charlotte", 1, "skill", "common",
                          "guest", (), "charlotte", exhaust=True),
    "ftd_wriothesley": Spec("Guest Star: Wriothesley", 1, "skill",
                            "uncommon", "guest", (), "wriothesley",
                            exhaust=True),
    "ftd_lynette": Spec("Guest Star: Lynette", 1, "skill", "uncommon",
                        "guest", (), "lynette", exhaust=True),
    "ftd_clorinde": Spec("Guest Star: Clorinde", 1, "skill", "rare",
                         "guest", (), "clorinde", exhaust=True),
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
    # Drain 2, never past your line. Deal 8 Pyro damage to ALL enemies.
    "ftd_lyney": Spec("Guest Star: Lyney", 1, "skill", "uncommon", "guest",
                      (), "lyney", exhaust=True),
    # A Five-Century Act (Power, 2): HP you Drain past your line also
    # returns when combat ends. (2026-10-09; was "You can Drain down to 1
    # HP".)
    "ftd_five_century": Spec("A Five-Century Act", 2, "power", "rare",
                             "power", (1,), "five_century"),
    # Fountain of Lucine (1): At the start of your next 3 turns, Repay 3.
    "ftd_fountain": Spec("Fountain of Lucine", 1, "skill", "uncommon",
                         "fountain", (3,)),
    # Hold the Stage (1): Gain 6 Block. Spend up to 12: gain 1 more for
    # each. (The Spend paper.)
    "ftd_hold_the_stage": Spec("Hold the Stage", 1, "skill", "uncommon",
                               "upto_block", (6, 12)),
    # Guest Star: Chevreuse (1). Line: whenever you Spend, apply 1
    # Vulnerable to a random enemy. Act: deal 4 damage to a random enemy.
    "ftd_chevreuse": Spec("Guest Star: Chevreuse", 1, "skill", "uncommon",
                          "guest", (), "chevreuse", exhaust=True),
    # Bis! (Power, 1): Whenever you Spend all your Fanfare, keep half of it.
    "ftd_bis": Spec("Bis!", 1, "power", "rare", "power", (1,), "bis"),
    # Critics' Darling (Power, 2, Rare): Whenever you Drain or Repay, deal
    # that much damage to a random enemy.
    "ftd_critics_darling": Spec("Critics' Darling", 2, "power", "rare",
                                "power", (1,), "critics_darling"),
    # Sigewinne (Uncommon). Line: whenever you Repay, gain that much Block.
    # Act: Repay 2.
    "ftd_sigewinne": Spec("Guest Star: Sigewinne", 1, "skill", "uncommon",
                          "guest", (), "sigewinne", exhaust=True),
    # --- THE POOL TO 75 (review/active/furina-pool-growth-2026-10-09.md
    # sec.5, ruled 2026-10-09): the 41, as the sheet prints them, base
    # numbers (the probe drafts no upgrades). ---
    # Guests and stage (11).
    "ftd_casting_call": Spec("Casting Call", 1, "skill", "uncommon",
                             "tutor_guest", ()),
    "ftd_encore": Spec("Encore!", 0, "skill", "common", "encore", (4, 1)),
    "ftd_tutti": Spec("Tutti!", 1, "skill", "uncommon", "tutti", ()),
    "ftd_final_bow": Spec("Final Bow", 1, "skill", "uncommon", "final_bow",
                          (2,)),
    "ftd_grand_entrance": Spec("Grand Entrance", 1, "power", "uncommon",
                               "power", (4,), "grand_entrance"),
    "ftd_freminet": Spec("Guest Star: Freminet", 1, "skill", "uncommon",
                         "guest", (), "freminet", exhaust=True),
    "ftd_showstopper": Spec("Showstopper", 2, "power", "rare", "power",
                            (1,), "showstopper"),
    "ftd_ensemble_cast": Spec("Ensemble Cast", 2, "power", "rare", "power",
                              (1,), "ensemble_cast"),
    "ftd_navia": Spec("Guest Star: Navia", 1, "skill", "rare", "guest", (),
                      "navia", exhaust=True),
    "ftd_escoffier": Spec("Guest Star: Escoffier", 1, "skill", "rare",
                          "guest", (), "escoffier", exhaust=True),
    # The Crowd (9).
    # Crashing Waves (1): Deal 4 Hydro damage twice. Spend up to 12: hit
    # once more for every 4. (The Spend paper.)
    "ftd_crashing_waves": Spec("Crashing Waves", 1, "attack", "common",
                               "upto_volley", (4, 2, 12)),
    "ftd_bubble_aria": Spec("Bubble Aria", 1, "skill", "common",
                            "spend_block_draw", (6, 3, 2)),
    # Commanding Gaze: the plain mode applies 2 Vulnerable (ruled
    # 2026-10-09, was 1).
    "ftd_commanding_gaze": Spec("Commanding Gaze", 1, "skill", "common",
                                "spend_debuff", (2, 4, 2, 2)),
    "ftd_star_turn": Spec("Star Turn", 2, "attack", "uncommon", "star_turn",
                          (15,), exhaust=True),
    # Sold Out and Overdraft give their Energy next turn (the 2026-10-09
    # build's loop ruling, Interval Bell's fix).
    "ftd_sold_out": Spec("Sold Out", 1, "skill", "uncommon", "sold_out",
                         (6, 1, 2)),
    "ftd_crescendo": Spec("Crescendo", 1, "power", "uncommon", "power",
                          (1,), "crescendo"),
    "ftd_prima_donna": Spec("Prima Donna", 2, "power", "rare", "power",
                            (1,), "prima_donna"),
    "ftd_standing_room_only": Spec("Standing Room Only", 2, "power", "rare",
                                   "power", (1,), "standing_room_only"),
    "ftd_bring_the_house_down": Spec("Bring the House Down", 2, "attack",
                                     "rare", "house_down", (1,)),
    # Ousia, Drain (10).
    "ftd_undercurrent": Spec("Undercurrent", 1, "attack", "common",
                             "undercurrent", (2, 5, 1)),
    "ftd_overdraft": Spec("Overdraft", 0, "skill", "common",
                          "drain_energy_next", (4, 1)),
    "ftd_ousia_pledge": Spec("Ousia Pledge", 1, "skill", "common",
                             "drain_draw", (3, 2)),
    "ftd_against_the_tide": Spec("Against the Tide", 1, "attack",
                                 "uncommon", "near_line_hit", (8, 14)),
    "ftd_pay_the_tab": Spec("Pay the Tab", 1, "skill", "uncommon",
                            "drain_draw", (6, 3)),
    "ftd_riptide_lunge": Spec("Riptide Lunge", 1, "attack", "uncommon",
                              "riptide", (3, 10, 6)),
    "ftd_high_stakes": Spec("High Stakes", 1, "power", "uncommon", "power",
                            (4,), "high_stakes"),
    "ftd_regina": Spec("Regina of All Waters", 2, "power", "rare", "power",
                       (1,), "regina"),
    "ftd_the_deluge": Spec("The Deluge", 2, "attack", "rare", "deluge",
                           (8, 24), exhaust=True),
    "ftd_all_in": Spec("All In", 0, "skill", "rare", "drain_energy", (8, 2),
                       exhaust=True),
    # Pneuma, Repay (10).
    # Soothing Waters: Repay 2. Draw 1 card. No Repay floor (ruled
    # 2026-10-09): a 0-cost draw-1 card paying out on an empty Repay looped
    # forever, and the draw already carries it, as with Pneuma Refrain.
    "ftd_soothing_waters": Spec("Soothing Waters", 0, "skill", "uncommon",
                                "repay_draw", (2, 1)),
    "ftd_gentle_current": Spec("Gentle Current", 1, "skill", "common",
                               "block_repay_next", (5, 4)),
    "ftd_clean_slate": Spec("Clean Slate", 1, "attack", "common",
                            "clean_slate", (7, 3, 1)),
    "ftd_hydro_lance": Spec("Hydro Lance", 2, "attack", "common",
                            "hydro_hit_repay", (14, 4)),
    "ftd_cleansing_torrent": Spec("Cleansing Torrent", 2, "attack",
                                  "uncommon", "hydro_aoe_repay", (10, 4)),
    "ftd_balance_the_books": Spec("Balance the Books", 1, "skill",
                                  "uncommon", "balance_books", (4,)),
    "ftd_rising_tide": Spec("Rising Tide", 1, "attack", "uncommon",
                            "rising_tide", (6, 3)),
    "ftd_pneuma_tides": Spec("Pneuma Tides", 1, "power", "uncommon",
                             "power", (2,), "pneuma_tides"),
    "ftd_hymn_of_renewal": Spec("Hymn of Renewal", 2, "power", "rare",
                                "power", (1,), "hymn_of_renewal"),
    "ftd_grand_absolution": Spec("Grand Absolution", 2, "attack", "rare",
                                 "grand_absolution", (), exhaust=True),
    # The bridge (1).
    "ftd_ebb_and_flow": Spec("Ebb and Flow", 1, "skill", "uncommon",
                             "ebb_flow", (4, 2)),
    # --- THE BLOCK GAP (review/records/furina-drain-line-round-2026-10-09.md
    # pick 2, ruled 2026-10-09): four Block cards, base numbers. ---
    # Velvet Curtain (1): Gain 7 Block. Gain 2 Fanfare.
    "ftd_velvet_curtain": Spec("Velvet Curtain", 1, "skill", "common",
                               "block_fanfare", (7, 2)),
    # Private Box (1): Gain 5 Block, plus 3 for each guest on stage.
    "ftd_private_box": Spec("Private Box", 1, "skill", "uncommon",
                            "guest_block", (5, 3)),
    # The Masquerade (Power, 1): Whenever you Drain, gain that much Block.
    "ftd_masquerade": Spec("The Masquerade", 1, "power", "uncommon",
                           "power", (1,), "masquerade"),
    # The Show Must Go On (2): Gain Block equal to your Fanfare (no Spend).
    "ftd_show_must_go_on": Spec("The Show Must Go On", 2, "skill", "rare",
                                "fanfare_block", ()),
    # --- Beyond the slice: rows a probe deck needs (never drafted) ---
    # The Crowd Gasps (Power, 1): Whenever an enemy makes you lose HP, gain
    # that much Fanfare (the `tragedy` deck; matters only without hits).
    "ftd_crowd_gasps": Spec("The Crowd Gasps", 1, "power", "uncommon",
                            "power", (1,), "crowd_gasps", in_slice=False),
    # Neuvillette (sec.15 point 4; drafted since the pool to 75). Line:
    # Hydro damage deals 2 more. Act: deal Hydro damage to ALL enemies equal
    # to the HP you lost since your last turn, Drained or taken (2026-10-09:
    # was the HP drained this turn; cost 1, was 2). He Drains nothing.
    "ftd_neuvillette": Spec("Guest Star: Neuvillette", 1, "skill", "rare",
                            "guest", (), "neuvillette", exhaust=True),
}

STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "ftd_curtain_rise", "ftd_rising_applause",
)

#: Modal Drain cards (the plain mode is a real line): the K3 take rate.
DRAIN_KINDS = ("drain_hit", "drain_aoe", "drain_block", "drain_tab")
#: Fixed-price Drain cards: unplayable when the Drain cannot be paid. Every
#: one's `n[0]` is its Drain price.
FIXED_DRAIN_KINDS = ("drain_fixed_hit", "drain_fixed_aoe",
                     # The pool to 75.
                     "undercurrent", "drain_energy", "drain_energy_next",
                     "drain_draw", "riptide",
                     "deluge", "ebb_flow")
SPEND_KINDS = ("block_spend_hit", "spend_energy",
               # The pool to 75: each one's `n` prints its price at `[1]`
               # except the volley's and the debuff's (`spend_price`).
               "spend_block_draw", "spend_debuff")
#: "Spend up to X" cards (the Spend paper, 2026-10-10): no choice, the Spend
#: is made on play. Each one's cap is `upto_cap`.
UPTO_KINDS = ("upto_aoe", "upto_hit_draw", "upto_block", "upto_volley")


def upto_cap(spec) -> int:
    """An up-to card's X (the volley prints it at `[2]`, the rest at `[1]`)."""
    return int(spec.n[2] if spec.kind == "upto_volley" else spec.n[1])
#: Fixed-price Spend cards; every one's `n[0]` is its Spend price.
FIXED_SPEND_KINDS = ("spend_fixed_hit", "encore", "sold_out")


def spend_price(spec) -> int:
    """A Spend-mode card's price (most print it at `n[1]`)."""
    return int(spec.n[1])


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
    card = Card(id=card_id, name=spec.name, cost=spec.cost, type=spec.type,
                rarity=spec.rarity, effects=[], tags=[TAG],
                character=CHARACTER, exhaust=spec.exhaust,
                retain=spec.kind == "tutti")
    if spec.kind == "star_turn":
        card.cost_reduction_per_fanfare = STAR_TURN_FANFARE_PER
    return card


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
# The default variant is the shipped rules: the Drain line rule's line,
# entry HP minus 1/4 of Max HP (ruled 2026-10-09). The other research
# variants keep the half line they measured.
VARIANTS["curtain_call"] = (2, True, SHIPPED_LINE)

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
                entry_max_hp=p.max_hp,
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


def shipped_line(entry_hp: int, entry_max_hp: int) -> int:
    """The shipped Drain line (2026-10-09; `FurinaStageLaw.LineOf`): the
    HP she started the combat with, minus 1/4 of the Max HP she started it
    with, rounded down; never below 0. 50/80 -> 30, 80/80 -> 60."""
    return max(0, max(0, int(entry_hp))
               - max(0, int(entry_max_hp)) // LINE_MAX_HP_DIVISOR)


def half_line(player) -> float:
    """The Drain line (the name is the half line's; since 2026-10-09 it is
    her entry HP minus 1/4 of her entry Max HP under the default variant).
    Lyney on stage lowers it by 10, never below 1. A Five-Century Act no
    longer moves it."""
    f = getattr(player, "ftd", None)
    if f is not None and f.line == SHIPPED_LINE:
        line = float(shipped_line(f.entry_hp, f.entry_max_hp))
    elif f is not None and f.line_from_entry:
        line = f.entry_hp * f.line
    else:
        line = player.max_hp * (f.line if f is not None else 0.5)
    if f is None:
        return line
    if "lyney" in f.stage:
        return max(float(DRAIN_FLOOR), line - LYNEY_LINE_DROP)
    return line


def line_hp(player) -> int:
    """The line as the C# prints it: the float line rounded up
    (`FurinaStageLaw.LineOf`), the lowest HP still above it."""
    import math
    return math.ceil(half_line(player))


def can_drain(state, n: int) -> bool:
    """Rule 1 (2026-10-09): a Drain is never refused for the line, only
    when it would take her to 0 HP or below."""
    p = state.player
    return n > 0 and p.hp - n >= DRAIN_FLOOR


def guest_drain_room(state, n: int) -> int:
    """A guest act's Drain of `n`, stopped at the line (the drain-line round,
    2026-10-09; the C# `FurinaStageLedger.GuestDrainRoom`): the part that
    fits without going past the line, 0 at or below it."""
    p = state.player
    return max(0, min(n, p.hp - line_hp(p)))


def past_line(state, n: int) -> bool:
    """Would a Drain of `n` go past the line?"""
    p = state.player
    return n > 0 and p.hp - n < half_line(p)


def near_line(player) -> bool:
    """Against the Tide and High Stakes: within 5 HP of the Drain line, or
    at or below it (a Drain may go past it since 2026-10-09). The C# line is
    the float line rounded up (`FurinaStageLaw.LineOf`)."""
    return player.hp - line_hp(player) <= NEAR_LINE


def capacity(state) -> int:
    """Rule 5: three seats, four with Ensemble Cast."""
    return (ENSEMBLE_SEATS if _player_power(state.player, "ensemble_cast")
            else SEATS)


def act_amount(member: str, upgraded: bool = False) -> int:
    """A guest's act number as its seat holds it (the C#
    `StageDirector.ActAmount`). Navia and Neuvillette read the turn."""
    table = {
        "charlotte": (CHARLOTTE_ACT_REPAY, CHARLOTTE_ACT_REPAY_UPGRADED),
        "sigewinne": (SIGEWINNE_ACT_REPAY, SIGEWINNE_ACT_REPAY_UPGRADED),
        "wriothesley": (WRIOTHESLEY_ACT, WRIOTHESLEY_ACT_UPGRADED),
        "lynette": (LYNETTE_ACT, LYNETTE_ACT_UPGRADED),
        "clorinde": (CLORINDE_ACT, CLORINDE_ACT_UPGRADED),
        "lyney": (LYNEY_ACT, LYNEY_ACT_UPGRADED),
        "chevreuse": (CHEVREUSE_ACT, CHEVREUSE_ACT),
        "freminet": (FREMINET_ACT_BLOCK, FREMINET_ACT_BLOCK_UPGRADED),
        "escoffier": (ESCOFFIER_ACT, ESCOFFIER_ACT_UPGRADED),
    }
    pair = table.get(member)
    if pair is None:
        return 0
    return pair[1] if upgraded else pair[0]


def navia_discount(f: Ftd) -> int:
    """Navia's line: the next Spend's discount -- 2 (3 upgraded) while she is
    on stage and no Spend has been made this turn."""
    if f.spends_this_turn > 0 or "navia" not in f.stage:
        return 0
    return (NAVIA_LINE_DISCOUNT_UPGRADED if "navia" in f.stage_up
            else NAVIA_LINE_DISCOUNT)


def price_of(f: Ftd, price: int) -> int:
    """What a Spend of `price` takes now (Navia's line)."""
    return max(0, int(price) - navia_discount(f))


def _line(state, member: str, amount: int) -> None:
    """A guest's LINE fired: its own log line (sec.3), never an act."""
    f = _f(state)
    f.ledger["lines"][member] += 1
    state.emit("ftd_line", member=member, amount=amount)


def _strength(state, n: int) -> None:
    if n <= 0 or not state.player.alive:
        return
    from tier0.engine import powers as _powers
    _powers.apply_power(state, state.player, "strength", n)


def playable(state, card) -> bool:
    """A fixed price must be payable: a fixed Drain above 0 HP, a fixed
    Spend from the bank. Every other row (and any non-slice card) is True."""
    spec = spec_of(card)
    if spec is None or not live(state.player):
        return True
    if spec.kind in FIXED_DRAIN_KINDS:
        return can_drain(state, spec.n[0])
    if spec.kind in FIXED_SPEND_KINDS:
        f = _f(state)
        return f.fanfare >= price_of(f, spec.n[0])
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
    if amount <= 0:
        return False
    pay = price_of(f, amount)
    if f.fanfare < pay:
        return False
    discount = amount - pay
    f.fanfare -= pay
    f.spent_this_turn += pay
    f.spends_this_turn += 1
    f.ledger["spent"] += pay
    f.ledger["spends"] += 1
    state.emit("ftd_spend", amount=pay, fanfare=f.fanfare)
    if discount:
        _line(state, "navia", discount)
    _after_spend(state)
    return True


def _after_spend(state) -> None:
    """The Spend readers: Thunderous Applause, Chevreuse's line (upgraded:
    also 1 Weak) and Crescendo (the first Spend each turn)."""
    f = _f(state)
    thunder = (THUNDEROUS_DAMAGE * f.powers["thunderous"]
               + _arm_power(state, "thunderous"))
    if thunder:
        for enemy in list(state.living_enemies):
            _hit(state, enemy, thunder, None)
    if "chevreuse" in f.stage and state.living_enemies:
        from tier0.engine import powers as _powers
        _line(state, "chevreuse", CHEVREUSE_LINE_VULNERABLE)
        _powers.apply_power(state, state.rng.choice(state.living_enemies),
                            "vulnerable", CHEVREUSE_LINE_VULNERABLE)
        if "chevreuse" in f.stage_up and state.living_enemies:
            _powers.apply_power(state,
                                state.rng.choice(state.living_enemies),
                                "weak", CHEVREUSE_LINE_WEAK_UPGRADED)
    crescendo = _player_power(state.player, "crescendo")
    if crescendo and f.spends_this_turn == 1 and not state.over:
        state.draw(crescendo)


def up_to_of(f: Ftd, cap: int) -> int:
    """What a "Spend up to `cap`" counts now: the cap, or all she holds plus
    Navia's free points if that is less (the C# `UpToOf`)."""
    cap = int(cap)
    return 0 if cap <= 0 else min(cap, f.fanfare + navia_discount(f))


def spend_up_to(state, cap: int) -> int:
    """"Spend up to X" (the Spend paper, 2026-10-10, pick 1): spends X, or all
    she holds if that is less, and never fails. A Spend only when at least 1
    counts (Thunderous Applause, Chevreuse, Crescendo); not a spend-all, so
    Bis! and Standing Room Only ignore it. Navia's line makes the first 2 [3]
    points of the first Spend each turn free: they count, and are not taken.
    Returns what counts as spent."""
    f = _f(state)
    counted = up_to_of(f, cap)
    if counted <= 0:
        return 0
    free = min(counted, navia_discount(f))
    pay = counted - free
    f.fanfare -= pay
    f.spent_this_turn += pay
    f.spends_this_turn += 1
    f.ledger["spent"] += pay
    f.ledger["spends"] += 1
    state.emit("ftd_spend", amount=pay, fanfare=f.fanfare)
    if free:
        _line(state, "navia", free)
    _after_spend(state)
    return counted


def spend_half(state) -> int:
    """A guest's act's half-Spend (Navia, Freminet; the Spend paper's pick
    2): "Spend half your Fanfare (rounded down)", of what is left when it
    acts. Returns what counts as spent."""
    return spend_up_to(state, _f(state).fanfare // GUEST_SPEND_DIVISOR)


def spend_all(state) -> int:
    """"Spend all your Fanfare": one Spend of everything held (nothing held
    is no Spend). Navia's first Spend each turn keeps 2 (3 upgraded); Bis!
    keeps half, rounded down; the card reads the whole bank. Standing Room
    Only answers a spend-all of at least 1. Returns what the card reads."""
    f = _f(state)
    held = f.fanfare
    if held <= 0:
        return 0
    keep = min(held, navia_discount(f))
    pay = held - keep
    f.fanfare -= pay
    f.spent_this_turn += pay
    f.spends_this_turn += 1
    f.ledger["spent"] += pay
    f.ledger["spends"] += 1
    state.emit("ftd_spend", amount=pay, fanfare=f.fanfare)
    if keep:
        _line(state, "navia", keep)
    _after_spend(state)
    if _player_power(state.player, "bis"):
        kept = held // 2
        f.fanfare += kept
        f.ledger["bis_kept"] += kept
    _strength(state, _player_power(state.player, "standing_room_only"))
    return held


def drain(state, n: int) -> bool:
    """Rule 1. Lose N HP (never to 0 HP), mark it drained -- the part that
    stays at or above the line, and the part past it (2026-10-09) -- gain N
    Fanfare, then the Drain readers."""
    p = state.player
    f = _f(state)
    if not can_drain(state, n):
        return False
    above = max(0, min(n, p.hp - line_hp(p)))
    p.hp -= n
    f.drained_above += above
    f.drained_past += n - above
    f.hp_lost_window += n
    f.drained_this_turn = True
    f.drained_hp_this_turn += n
    f.drains_this_combat += 1
    f.ledger["drained"] += n
    f.ledger["drained_past"] = f.ledger.get("drained_past", 0) + (n - above)
    f.ledger["drains"] += 1
    state.hp_lost_this_turn += n
    state.emit("ftd_drain", amount=n, hp=p.hp, drained=f.drained)
    gain(state, n, "drain")
    _loop_readers(state, n)
    # The Masquerade (the block gap, 2026-10-09): the HP actually drained as
    # Block, per copy; a Power's Block, unpowered (the C# `StageDirector`).
    # A guest act's Drain arrives here already stopped at the line.
    masquerade = _player_power(p, "masquerade")
    if masquerade and not state.over:
        p.block += n * masquerade
    encore = (SALON_ENCORE_DAMAGE * f.powers["salon_encore"]
              + _arm_power(state, "salon_encore"))
    if encore:
        for enemy in list(state.living_enemies):
            _hit(state, enemy, encore, None)
    if "wriothesley" in f.stage and state.living_enemies:
        _line(state, "wriothesley", n)
        _hit(state, state.rng.choice(state.living_enemies), n, "cryo")
    if "freminet" in f.stage:
        _line(state, "freminet", n)
        p.block += n
    surge = _player_power(p, "ousia_surge")
    if surge and not f.ousia_drew and not state.over:
        f.ousia_drew = True
        state.draw(surge)
    return True


def _clamp_drained(p, f: Ftd) -> None:
    """HP + drained never exceeds Max HP; the clamp takes the past-line
    part first, the order a Repay returns it in (the C# `RepayRoom`)."""
    over = f.drained - max(0, p.max_hp - p.hp)
    if over > 0:
        past = min(over, f.drained_past)
        f.drained_past -= past
        f.drained_above = max(0, f.drained_above - (over - past))


def repay(state, n: int) -> int:
    """Rule 2. Regain up to N drained HP, the past-line part first
    (2026-10-09); gain that much Fanfare; then the Repay readers. Returns HP
    repaid."""
    p = state.player
    f = _f(state)
    _clamp_drained(p, f)
    amount = min(n, f.drained)
    f.ledger["repay_wasted"] += n - amount
    if amount <= 0:
        return 0
    p.hp += amount
    past = min(amount, f.drained_past)
    f.drained_past -= past
    f.drained_above = max(0, f.drained_above - (amount - past))
    f.repaid_this_turn += amount
    f.repays_this_turn += 1
    f.repaid_this_play += amount
    f.ledger["repaid"] += amount
    state.emit("ftd_repay", amount=amount, hp=p.hp, drained=f.drained)
    if f.repay_fanfare:
        gain(state, amount, "repay")
    _loop_readers(state, amount)
    if "clorinde" in f.stage and state.living_enemies:
        _line(state, "clorinde", CLORINDE_PER_REPAY * amount)
        _hit(state, state.rng.choice(state.living_enemies),
             CLORINDE_PER_REPAY * amount, "electro")
    if "charlotte" in f.stage and not f.charlotte_drew and not state.over:
        f.charlotte_drew = True
        _line(state, "charlotte", 1)
        state.draw(1)
    if "sigewinne" in f.stage:
        _line(state, "sigewinne", amount)
        p.block += amount
    hymn = _player_power(p, "hymn_of_renewal")
    if hymn and amount >= HYMN_THRESHOLD and not state.over:
        # Hymn of Renewal counts the HP this Repay actually returned.
        _strength(state, hymn)
    return amount


def repay_floor(state, n: int, floor: str) -> int:
    """THE REPAY FLOOR (ruled 2026-10-09): "Repay N. Gain X for any HP it
    could not Repay." The Repay resolves first; the leftover, N minus the HP
    it returned, is paid as Block (`block`, unpowered, as Sigewinne's line
    pays) or Vigor (`vigor`: the sim's `next_attack_up`, the base game's
    "your next Attack deals N more"). The C# `StageDirector.RepayFloor`.
    Returns HP repaid."""
    if n <= 0:
        return 0
    back = repay(state, n)
    left = n - back
    p = state.player
    if left <= 0 or state.over or not p.alive:
        return back
    if floor == "block":
        p.block += left
    elif floor == "vigor":
        from tier0.engine import powers as _powers
        _powers.apply_power(state, p, "next_attack_up", left)
    f = _f(state)
    f.ledger["floor_paid"] = f.ledger.get("floor_paid", 0) + left
    return back


def card_repay(state, n: int, floor: str = "none") -> int:
    """A card's Repay N: with its floor, and the leftover recorded for the
    play (`repay_left_this_play`, the damage cards' floor). Returns HP
    repaid."""
    back = repay_floor(state, n, floor)
    if live(state.player):
        _f(state).repay_left_this_play += max(0, n - back)
    return back


def on_hp_loss(state, n: int) -> None:
    """Hook from `resources.note_player_hp_loss`: true HP loss from any
    source but a Drain (enemy hits, statuses) prints Fanfare 1:1 and counts
    for Neuvillette's act. Lynette's line pays it again the first time each
    turn."""
    if n <= 0 or not live(state.player):
        return
    f = _f(state)
    f.hp_lost_window += n
    if f.hit_fanfare or f.powers["crowd_gasps"]:
        gain(state, n, "hit")
    if "lynette" in f.stage and not f.lynette_fired:
        f.lynette_fired = True
        _line(state, "lynette", n)
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
def hydro_bonus(state) -> int:
    """Neuvillette's line: "Your Hydro damage deals 2 more." [3] Read by
    `effects.deal_damage_to_enemy`'s additive phase for every Hydro hit she
    deals (a card's, a guest's, his own act's), the C#
    `FurinaStage.HydroBonus`."""
    f = getattr(state.player, "ftd", None)
    if not isinstance(f, Ftd) or "neuvillette" not in f.stage:
        return 0
    return (NEUVILLETTE_HYDRO_BONUS_UPGRADED if "neuvillette" in f.stage_up
            else NEUVILLETTE_HYDRO_BONUS)


def _hit(state, enemy, amount: int, element) -> None:
    from tier0.engine import effects
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
    """One guest's act (the C# `StageDirector.Act`): at the end of her turn
    or bought by a card. Escoffier's line answers every act, his own
    included."""
    p = state.player
    f = _f(state)
    if state.over or not p.alive:
        return
    f.ledger["guest_acts"][member] += 1
    living = list(state.living_enemies)
    n = act_amount(member, member in f.stage_up)
    if member in ("charlotte", "sigewinne"):
        # "Repay 2. Gain 1 Block for any HP it could not Repay." (The Repay
        # floor, 2026-10-09.)
        repay_floor(state, n, "block")
    elif member == "wriothesley":
        if living:
            _hit(state, state.rng.choice(living), n, "cryo")
    elif member == "lynette":
        aura = [e for e in living if getattr(e, "aura", None)]
        if aura:
            _hit(state, state.rng.choice(aura), n, "anemo")
    elif member == "clorinde":
        if living:
            _hit(state, state.rng.choice(living), n, "electro")
    elif member == "neuvillette":
        # The HP she lost since her last turn, Drained or taken (2026-10-09).
        dmg = f.hp_lost_window
        if dmg > 0:
            for enemy in living:
                _hit(state, enemy, dmg, "hydro")
    elif member == "lyney":
        # "Drain 2, never past your line. Deal 8 Pyro damage to ALL
        # enemies." A guest's Drain stops at the line (the drain-line round,
        # 2026-10-09): it drains only the room above it, 0 with none, and
        # the damage lands either way.
        room = guest_drain_room(state, LYNEY_ACT_DRAIN)
        if room > 0:
            drain(state, room)
        if not state.over and p.alive:
            for enemy in list(state.living_enemies):
                _hit(state, enemy, n, "pyro")
    elif member == "chevreuse":
        if living:
            _hit(state, state.rng.choice(living), n, None)
    elif member == "freminet":
        # "Gain 3 Block. Spend half your Fanfare (rounded down): gain that
        # much more Block." [6] (the Spend paper, 2026-10-10, pick 2).
        p.block += n
        if p.alive and not state.over:
            more = spend_half(state)
            if more > 0 and p.alive and not state.over:
                p.block += more
    elif member == "navia":
        # "Spend half your Fanfare (rounded down). Deal that much Geo damage
        # to a random enemy." (the Spend paper, pick 2). Nothing spent,
        # nothing dealt.
        dmg = spend_half(state)
        living = state.living_enemies
        if dmg > 0 and living and not state.over:
            _hit(state, state.rng.choice(living), dmg, "geo")
    elif member == "escoffier":
        for enemy in living:
            _hit(state, enemy, n, "cryo")
    state.emit("ftd_act", member=member)
    if "escoffier" in f.stage and not state.over and p.alive:
        _line(state, "escoffier", ESCOFFIER_LINE_REPAY)
        repay(state, ESCOFFIER_LINE_REPAY)


def summon(state, member: str, upgraded: bool = False, card=None) -> str:
    """A Guest Star (sec.3): no effect on summon. A guest already on stage
    moves to the newest seat, with no act; otherwise it takes the back seat,
    and on a full stage the oldest guest leaves first (no act) and its cards
    go to the discard pile. `card` is the Guest Star played: its seat holds
    it until the guest leaves."""
    f = _f(state)
    if member in f.stage:
        f.stage.remove(member)
        f.stage.append(member)
        if upgraded:
            f.stage_up.add(member)
        if card is not None:
            f.stage_cards.setdefault(member, []).append(card)
        f.ledger["moves"] += 1
        state.emit("ftd_move", member=member)
        return "repeat"
    result = "seated"
    if len(f.stage) >= capacity(state):
        leave(state, 0, "evicted")
        result = "evict"
    f.stage.append(member)
    if upgraded:
        f.stage_up.add(member)
    else:
        f.stage_up.discard(member)
    f.stage_cards[member] = [card] if card is not None else []
    return result


def leave(state, index: int, reason: str = "") -> str | None:
    """The guest in seat `index` leaves the stage: its Guest Star cards go
    from the exhaust pile to the discard pile (sec.3)."""
    f = _f(state)
    if index < 0 or index >= len(f.stage):
        return None
    member = f.stage.pop(index)
    f.stage_up.discard(member)
    p = state.player
    for card in f.stage_cards.pop(member, []):
        for i, held in enumerate(p.exhaust_pile):
            if held is card:
                del p.exhaust_pile[i]
                p.discard_pile.append(card)
                break
    f.ledger["leaves"] += 1
    f.ledger["bows"] += 1
    state.emit("ftd_leave", member=member, reason=reason)
    return member


def act_all(state) -> int:
    """Each guest acts once, oldest first, over a snapshot of the stage
    (end of turn, Tutti!, Bring the House Down, Showstopper)."""
    f = _f(state)
    acts = 0
    for member in list(f.stage):
        if (state.over or not state.player.alive
                or not state.living_enemies):
            break
        if member in f.stage:
            act(state, member)
            acts += 1
    return acts


def act_oldest(state) -> bool:
    """Encore!: "Your oldest guest acts." """
    f = _f(state)
    if not f.stage or state.over:
        return False
    act(state, f.stage[0])
    return True


def final_bow(state, index: int, times: int) -> bool:
    """Final Bow: the chosen guest acts `times` times, then leaves and its
    card returns to the discard pile."""
    f = _f(state)
    if index < 0 or index >= len(f.stage):
        return False
    member = f.stage[index]
    for _ in range(times):
        if state.over or not state.player.alive or member not in f.stage:
            break
        act(state, member)
    if member in f.stage:
        leave(state, f.stage.index(member), "final_bow")
    return True


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
    f.spends_this_turn = 0
    f.repays_this_turn = 0
    f.repaid_this_play = 0
    f.repay_left_this_play = 0


def turn_start(state) -> None:
    """After her draw: Fountain of Lucine's Repays. What the arm's power
    took in since the last turn start is scheduled for three turns (the C#
    `FurinaStage.FountainRepays` reads its power the same way); then each
    schedule Repays its amount, one Repay per schedule."""
    if not live(state.player):
        return
    f = _f(state)
    p = state.player
    # The pool to 75's turn-start Powers, in the C# `FurinaStage.TurnStart`
    # order: Regina of All Waters first (so the Repays after it have room),
    # then Fountain of Lucine, Gentle Current, Pneuma Tides, and Prima Donna
    # last (so it reads the Fanfare they printed).
    for _ in range(_player_power(p, "regina")):
        if state.over or not p.alive or not can_drain(state, REGINA_DRAIN):
            break
        if drain(state, REGINA_DRAIN):
            _strength(state, 1)
    applied = _arm_fountain(state)
    if applied > f.fountain_seen:
        f.fountains.append([applied - f.fountain_seen, FOUNTAIN_TURNS])
        f.fountain_seen = applied
    due = [amount for amount, _turns in f.fountains]
    for item in f.fountains:
        item[1] -= 1
    f.fountains = [item for item in f.fountains if item[1] > 0]
    # The Repay floor (2026-10-09): Fountain of Lucine's and Gentle
    # Current's pay Block, Pneuma Tides' Vigor.
    for amount in due:
        if state.over or not state.player.alive:
            break
        f.ledger["fountain_repaid"] += repay_floor(state, amount, "block")
    if f.repay_next and not state.over and p.alive:
        owed, f.repay_next = f.repay_next, 0
        repay_floor(state, owed, "block")
    tides = _player_power(p, "pneuma_tides")
    if tides and not state.over and p.alive:
        repay_floor(state, tides, "vigor")
    donna = _player_power(p, "prima_donna")
    if donna and f.fanfare >= PRIMA_DONNA_FANFARE and p.alive:
        p.energy += donna


def _arm_fountain(state) -> int:
    from tier0.engine import furina_stage           # late: avoids a cycle
    powers = getattr(state.player, "powers", None) or {}
    return int(powers.get(furina_stage.FOUNTAIN_OF_LUCINE, 0) or 0)


def end_of_turn(state) -> None:
    """Guests act in seat order (oldest first); then each Showstopper Spends
    5 and the guests act again; then Salon Solitaire's Singer Repays (under
    `singer_rests`, only if no Drain happened this turn)."""
    if not live(state.player):
        return
    f = _f(state)
    act_all(state)
    for _ in range(_player_power(state.player, "showstopper")):
        if (state.over or not state.player.alive or not f.stage
                or f.fanfare < price_of(f, SHOWSTOPPER_SPEND)):
            break
        if not spend(state, SHOWSTOPPER_SPEND):
            break
        f.ledger["showstopper_rounds"] = (
            f.ledger.get("showstopper_rounds", 0) + 1)
        act_all(state)
    if f.singer_rests and f.drained_this_turn:
        f.ledger["singer_skipped"] += 1
    elif not state.over and state.player.alive:
        repay(state, f.singer)
    # Neuvillette's window (2026-10-09): what she loses from here on -- the
    # enemies' turn first -- counts for his next act.
    f.hp_lost_window = 0


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
    elif k == "drain_fixed_hit":
        # Only the plain row: the pool-75 fixed Drains (also in
        # FIXED_DRAIN_KINDS) each resolve in their own branch below.
        price, dmg = n
        if drain(state, price):         # `playable` gated it; belt and braces
            f.ledger["fixed_drains"] += 1
            _card_damage(state, card, dmg)
    elif k in SPEND_KINDS:
        f.ledger["spend_offers"] += 1
        price = spend_price(spec)
        take = (f.fanfare >= price_of(f, price)
                and d.spend(state, card, spec))
        if take:
            spend(state, price)
        if k == "block_spend_hit":
            _card_block(state, card, n[0])
            if take:
                _card_damage(state, card, n[2])
        elif k == "spend_energy":
            state.draw(n[0])
            if take:
                state.player.energy += n[2]
        elif k == "spend_block_draw":
            _card_block(state, card, n[0])
            if take:
                state.draw(n[2])
        elif k == "spend_debuff":
            _debuff_target(state, "vulnerable", n[2] if take else n[0])
            if take:
                _debuff_target(state, "weak", n[3])
    elif k in UPTO_KINDS:
        # "Spend up to X" (the Spend paper, 2026-10-10): no choice; 1 more
        # per point spent, and "for every 4" in fours.
        spent = spend_up_to(state, upto_cap(spec))
        if k == "upto_aoe":
            _card_damage(state, card, n[0] + spent, all_enemies=True,
                         hydro=True)
        elif k == "upto_hit_draw":
            _card_damage(state, card, n[0] + spent)
            if spent // SPEND_UP_TO_EVERY:
                state.draw(spent // SPEND_UP_TO_EVERY)
        elif k == "upto_block":
            _card_block(state, card, n[0] + spent)
        else:                                       # upto_volley
            for _ in range(n[1] + spent // SPEND_UP_TO_EVERY):
                _card_damage(state, card, n[0], hydro=True)
    elif k == "spend_fixed_hit":
        price, dmg = n
        if spend(state, price):
            _card_damage(state, card, dmg, hydro=True)
    elif k == "encore":
        if spend(state, n[0]):
            act_oldest(state)
            state.draw(n[1])
    elif k == "sold_out":
        if spend(state, n[0]):
            state.draw(n[2])
            f.energy_next += n[1]
    elif k == "block_spend_all":
        _card_block(state, card, n[0])
        held = f.fanfare
        if held > 0 and (not f.rising_optional
                         or d.spend_all(state, card, spec)):
            spend_all(state)
            _card_damage(state, card, n[1] * held)
    elif k == "hit_repay":
        # The Repay floor (2026-10-09): Repay first, then the damage plus
        # what it could not return.
        back = repay(state, n[1])
        _card_damage(state, card, n[0] + (n[1] - back))
    elif k == "block_repay":
        _card_block(state, card, n[0])
        repay_floor(state, n[1], "block")
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
        summon(state, spec.member, card=card)
        entrance = _player_power(state.player, "grand_entrance")
        if entrance:
            repay_floor(state, entrance, "block")
    # --- The pool to 75 ---
    elif k == "tutor_guest":
        tutor_guest(state)
    elif k == "tutti":
        act_all(state)
    elif k == "final_bow":
        if f.stage:
            final_bow(state, _decider_bow(state), n[0])
    elif k == "star_turn":
        _card_damage(state, card, n[0])
    elif k == "house_down":
        held = spend_all(state)
        _card_damage(state, card, n[0] * held)
        act_all(state)
    elif k == "undercurrent":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            _card_damage(state, card, n[1] + n[2] * f.drains_this_combat)
    elif k == "drain_energy":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            state.player.energy += n[1]
    elif k == "drain_energy_next":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            f.energy_next += n[1]
    elif k == "drain_draw":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            state.draw(n[1])
    elif k == "near_line_hit":
        _card_damage(state, card,
                     n[1] if near_line(state.player) else n[0])
    elif k == "riptide":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            target = _bound_target(state)
            _card_damage(state, card, n[1])
            if target is not None and not target.alive:
                repay(state, n[2])
    elif k == "deluge":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            _card_damage(state, card, n[1], all_enemies=True)
    elif k == "block_repay_next":
        _card_block(state, card, n[0])
        f.repay_next += n[1]
    elif k == "clean_slate":
        _card_damage(state, card, n[0])
        repay(state, n[1])
        if f.drained <= 0:
            state.draw(n[2])
    elif k == "hydro_hit_repay":
        back = repay(state, n[1])
        _card_damage(state, card, n[0] + (n[1] - back), hydro=True)
    elif k == "hydro_aoe_repay":
        back = repay(state, n[1])
        _card_damage(state, card, n[0] + (n[1] - back), all_enemies=True,
                     hydro=True)
    elif k == "balance_books":
        dmg = f.drained // 2
        if dmg > 0:
            _card_damage(state, card, dmg, all_enemies=True)
        repay(state, n[0])
    elif k == "rising_tide":
        _card_damage(state, card, n[0] + n[1] * f.repays_this_turn)
    elif k == "grand_absolution":
        back = repay(state, f.drained)
        if back > 0:
            _card_damage(state, card, back, all_enemies=True)
    elif k == "ebb_flow":
        if drain(state, n[0]):
            f.ledger["fixed_drains"] += 1
            repay(state, n[1])
    # --- The block gap (2026-10-09) ---
    elif k == "block_fanfare":
        _card_block(state, card, n[0])
        gain(state, n[1], "card")
    elif k == "guest_block":
        _card_block(state, card, n[0] + n[1] * len(f.stage))
    elif k == "fanfare_block":
        if f.fanfare > 0:
            _card_block(state, card, f.fanfare)
    else:                                    # pragma: no cover
        raise ValueError(f"unknown kind {k!r}")


def _bound_target(state):
    """The enemy a single-target card hits (the engine's bound aim: the
    lowest-HP living enemy, `READINGS`)."""
    living = state.living_enemies
    return min(living, key=lambda e: e.hp) if living else None


def _debuff_target(state, power: str, amount: int) -> None:
    from tier0.engine import powers as _powers
    target = _bound_target(state)
    if target is not None and amount > 0:
        _powers.apply_power(state, target, power, amount)


def _decider_bow(state) -> int:
    """Final Bow's choice: the decider's `final_bow` hook when it has one,
    else the guest whose act is biggest (the oldest on a tie)."""
    d = _decider(state)
    pick = getattr(d, "final_bow", None)
    if pick is not None:
        return int(pick(state))
    return default_bow(state)


def default_bow(state) -> int:
    """The sim's default Final Bow pick: the guest whose act number is
    biggest, the oldest on a tie."""
    f = _f(state)
    best, best_n = 0, -1
    for i, member in enumerate(f.stage):
        n = act_amount(member, member in f.stage_up)
        if member == "navia":
            n = f.fanfare // GUEST_SPEND_DIVISOR
        elif member == "freminet":
            n += f.fanfare // GUEST_SPEND_DIVISOR
        elif member == "neuvillette":
            n = f.hp_lost_window
        if n > best_n:
            best, best_n = i, n
    return best


def tutor_guest(state) -> bool:
    """Casting Call: a Guest Star from the draw pile into the hand. The sim
    takes the first one a guest not already on stage (a tutor, the paper's
    reading), else the first."""
    p = state.player
    f = _f(state)
    guests = [c for c in p.draw_pile if is_guest_card(c)]
    if not guests:
        return False
    fresh = [c for c in guests if guest_member(c) not in f.stage]
    pick = (fresh or guests)[0]
    for i, held in enumerate(p.draw_pile):
        if held is pick:
            del p.draw_pile[i]
            break
    p.hand.append(pick)
    return True


def guest_member(card) -> str | None:
    """The guest a Guest Star card summons, or None: a slice row's member,
    or a sheet row's `stage_guest` op."""
    spec = spec_of(card)
    if spec is not None:
        return spec.member if spec.kind == "guest" else None
    for fx in getattr(card, "effects", None) or []:
        if fx.get("op") == "stage_guest":
            return fx.get("member")
    return None


def is_guest_card(card) -> bool:
    return guest_member(card) is not None


def close_ledger(state) -> None:
    """The fight is over: record what the curtain found (and, under the
    curtain call, if she lived) return the HP drained above the line -- and
    past it too, with A Five-Century Act (the Drain line rule, 2026-10-09).
    The past-line part is lost."""
    p = state.player
    f = _f(state)
    f.ledger["unrepaid_end"] = f.drained
    f.ledger["lost_past_line"] = f.drained_past
    f.ledger["fanfare_end"] = f.fanfare
    if f.curtain_call and p.alive and f.drained > 0:
        owed = f.drained_above
        if _player_power(p, "five_century"):
            owed += f.drained_past
            f.ledger["lost_past_line"] = 0
        back = min(owed, max(0, p.max_hp - p.hp))
        p.hp += back
        f.ledger["curtain_repaid"] += back
    f.drained_above = 0
    f.drained_past = 0


READINGS: tuple[str, ...] = (
    "The line (2026-10-09): the HP she started the combat with, minus 1/4 "
    "of the Max HP she started it with, rounded down (`SHIPPED_LINE`). A "
    "Drain N is legal when HP - N >= 1; the "
    "part of it below the line (the line rounded up, as the C# prints it) "
    "is `drained_past`.",
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
    "copy.",
    "Lyney's act never Drains past the line: it drains only the room "
    "above it (0 with none) and deals its damage either way. His line lowers the line by 10 while he is on "
    "stage, never below 1 HP. A Five-Century Act does not move the line: it "
    "returns the past-line part at the curtain call.",
    "Bis! keeps half a spend-all, rounded down; a second copy adds nothing. "
    "Fountain of Lucine's Repays come after her draw, one per play.",
    "Guest acts and lines are unpowered (Strength and Weak do not touch "
    "them).",
    "Neuvillette's act deals the HP she lost since her last turn ended "
    "(Drained or taken, gross of Repays) to ALL as Hydro; it Drains "
    "nothing.",
    "The Repay floor's Vigor is the sim's `next_attack_up` (the next Attack "
    "card deals that much more, then it is spent); its Block is unpowered, "
    "as Sigewinne's line pays it.",
    "The curtain call returns the HP drained above the line in "
    "`close_ledger`, after the fight's record is taken; the probe calls it "
    "on every fight.",
    "Card damage aims at the engine's bound aim (the lowest-HP enemy).",
)
