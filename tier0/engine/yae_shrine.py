"""YAE MIKO, THE SHRINE AND THE PUBLISHING HOUSE -- the sim's rules twin.

Design: `review/active/yae-proposal-2026-10-12.md` (ruled 2026-10-12) and the
card paper `review/active/yae-card-paper-2026-10-13.md`, whose sec.2 is the
list of readings this module takes, ruled 2026-10-13. Rows: the `proto_ym_`
rows of `docs/prototype-surface.yaml`. C# twin:
`klee-mod/KleeCode/Powers/Prototype/YaeShrine.cs` (`YaeLaw` mirrors the
numbers below, `tools/lint_constant_parity.py`).

NO SWITCH, as Varka: she ships nowhere else, so every hook this module adds to
the shared engine is a dead branch for any player who is not Yae (`live`).
Her numbers live here rather than in `constants.py` so they move neither the
constant census nor the world stamp.

THE RULES AS MODELLED (review r3, ruled 2026-10-14,
`review/active/yae-review-r3-2026-10-14.md`, both picks (a) as amended):
  * SAKURA: up to `sakura_cap` (`SAKURA_CAP`, plus 2 per Sakura
    Channeling) on a per-fight ledger (`YaeLedger.sakura`), each with a KIND,
    a LEVEL and a TIMER (actions left). A plant creates one at the Level the
    card prints (`PLANT_LEVEL`, Grafted Branch its own), +1 per Fox's
    Mooncall, with 3 actions left, and does not level the others.
  * KINDS (review r3, sec.1): set when planted. Sakura (Thunder, the
    default) strikes one enemy for 2 + Level; a Foxfire Sakura hits ALL
    enemies for 1 + Level; a Kitsune Sakura (the decoy) gives her 2 + Level
    Block. Every planter plants a plain Sakura unless its card names a kind
    (`as:` on the `plant` op: Foxfire Sweep, Shrine Maiden's Guard).
  * A SAKURA ACTS (`act`) at the end of her turn (oldest first), once more
    when it withers (Last Bloom), and on Tenko. A damage action is Electro,
    unpowered (a pet's hit: no Strength, no Weak; Vulnerable and Block
    apply), source "card"; the Lure aims a Thunder strike.
  * FULL SHRINE (amended after GPT's review): a plant into a full shrine
    makes the OLDEST act first. Same kind as the new one: the oldest
    refreshes to at least 3 and gains a Level, and none is added. A
    different kind: the oldest withers and the new Sakura takes its place
    (as the newest) at its printed Level. Under `SCALING == "count"` (pick 1
    (b) of the card paper, kept as a knob) a full plant replaces the oldest.
  * TENKO (review r3): one plain rule again, "Every Sakura acts now.
    Refresh them to at least 3 turns." The typed Tenko is gone.
  * EDIT AND THE MASTERPIECE (review r3, sec.2, pick 2 (a)): every card has
    two layers. The PERMANENT STACK (`ym_stack`) holds every Published
    Annotation for the run; ONE TEMPORARY SLOT (`ym_temp`) holds a combat
    Edit, which a later Edit replaces and which never touches the stack.
    An Edit may target a Published card (it fills the temporary slot).
    Publishing moves the temporary layer onto the stack, once. Stacked
    Annotations add up: Red Ink +3 each, Footnote draws 1 each, Fox Fire
    hits once each, Sakura Seal plants one each, Royalties 1 Energy each;
    Deadline Extension is Retain. REPRINT: on the card's first play each
    combat it replays once per Reprint layer, then those go inert for the
    combat; a new temporary Reprint arms one fresh replay; a copy is a new
    card, its Reprints armed (`reprint_replays`). "Annotated" is any card
    carrying a layer (`is_annotated`).
  * PUBLISH: The Seven Glamours moves a card's temporary layer onto its
    stack. The sim's fights are single combats; the run harness
    (`tools/yae_expansion_sim`) carries each deck slot's stack into the
    next fight, and Meditations of a Yako Publishes after an elite or boss
    fight: it reads the DRAFTS that fight left (`YaeLedger.drafts`, slot ->
    the temporary layer) and adds the picked one to that slot's stack
    (`publish_choices`, `publish_after_fight`). A Published card may be
    offered again: stacks grow.
  * SIGNATURE CARDS (review r3, sec.3): Second Printing (an Annotated card
    from the Discard Pile to hand, upgraded it costs 0 this turn), Author's
    Copy (a copy of an Annotated card in hand, never an Author's Copy, keeps
    its layers: LAW, no energy-positive copy loop), Serial Novel (at the
    start of her turn, a random Annotated card from the Discard Pile to
    hand, per stack).
  * FALLEN PETALS (review r3, sec.4): an active Skill. "Your oldest Sakura
    withers (it acts once, its Last Bloom). If one did, gain 1 Energy [and
    draw 1 card]."
  * POWERS (self, by name): Sakura Grove (at her turn start, after Yakan
    Offering, each Sakura gains n Levels), Edict of Cleansing (+n on a
    damage action at an enemy that is Weak or wears Pyro, Hydro or Cryo;
    damage kinds only), Serialization (Block per Annotated card played,
    unpowered), Fox's Mooncall (plant n Levels higher), Yakan Offering
    (plant at the start of her turn, after the draw), Sakura Channeling
    ("You can have 2 more Sakura"), Editor-in-Chief (after an Annotated
    card's play, the highest-Level Sakura acts), Serial Novel (above).
  * SAKURA ANNOTATIONS: a Sakura may carry one of Red Ink (its action is 3
    bigger: damage, each enemy's damage, or Block), Fox Fire (4 Electro to a
    random enemy whenever it acts) or Deadline Extension (its timer never
    ticks), written by "Edit your newest / oldest / every Sakura"
    (`edit_sakura`). A new one replaces the old; it lasts the Sakura's life.
  * RED INK ON A PLANTING CARD: Red Ink on a card that plants passes to
    every Sakura that play plants (`inherits`), once (+3) however many Red
    Ink layers the card has; a full-shrine plant that only levels plants
    nothing. THE DEAD-EDIT FILTER: an Edit, Reborn as Guuji Yae and the
    after-elite Publish offer skip a card the Annotation would do nothing on
    (`affects`). C# twin: `YaeAnnotationReach`.

READINGS TAKEN WHERE THE PAPER LEAVES ROOM (each in the builder's report):
  * Tier 0 seats one player, so every Sakura is hers.
  * `damage_per_sakura` and `damage_per_annotated` are ONE powered hit of
    the card (Strength counts, flat Attack riders ride it) carrying Electro.
  * Reborn as Guuji Yae's one Annotation is the pilot's (`reborn_choice`),
    else the row's printed default (Sakura Seal).
  * Review r3 (the builder's readings, 2026-10-14): Editor-in-Chief's
    "a Sakura strikes" is the highest-Level Sakura acting as its kind;
    Kitsune Pounce's "a Sakura strikes it" is the highest-Level DAMAGE
    Sakura (Thunder or Foxfire), aimed at it. A full-shrine replacement
    puts the new Sakura in the newest place. Fallen Petals and a
    different-kind full-shrine plant wither the oldest even under Deadline
    Extension (an active wither, not a timer). A Sakura inherits Red Ink
    once (+3), however many Red Ink layers its planting card carries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

CHARACTER = "yae"
HP = 72
ELEMENT = "electro"
CADENCE = "catalyst"


# --- the shrine (C# twin: `YaeLaw`, Powers/Prototype/YaeShrine.cs) ---
SAKURA_CAP = 3
SAKURA_TURNS = 3            # actions a Sakura has when planted or refreshed
SAKURA_BASE = 2             # a Sakura (Thunder) strikes for this + Level
FOXFIRE_BASE = 1            # a Foxfire Sakura hits ALL for this + Level
KITSUNE_BASE = 2            # a Kitsune Sakura gives this + Level Block
PLANT_LEVEL = 1             # +1 per Fox's Mooncall; Levels have no cap
#: Pick 1 (b): the proposal's placeholder, a strike by the COUNT standing.
COUNT_TABLE = {1: 3, 2: 4, 3: 5}   # the same ceiling as (a), paired
COUNT_TENKO_BONUS = 1       # (b): each Tenko adds 1 to every later strike
#: "level" (pick 1 (a), the default) or "count" (pick 1 (b)).
SCALING = "level"

# --- the Sakura kinds (review r3, sec.1; C# `YaeSakuraKind`) ---
THUNDER, FOXFIRE, KITSUNE = "thunder", "foxfire", "kitsune"
SAKURA_KINDS = (THUNDER, FOXFIRE, KITSUNE)
#: The kinds that deal damage (Edict of Cleansing, the Lure, Kitsune Pounce).
DAMAGE_KINDS = (THUNDER, FOXFIRE)
#: Each kind's printed name.
KIND_NAME = {THUNDER: "Sakura", FOXFIRE: "Foxfire Sakura",
             KITSUNE: "Kitsune Sakura"}

# --- the Annotations ---
RED_INK, FOOTNOTE, DEADLINE, FOX_FIRE, SAKURA_SEAL, ROYALTIES, REPRINT = (
    "red_ink", "footnote", "deadline", "fox_fire", "sakura_seal",
    "royalties", "reprint")
ANNOTATIONS = (RED_INK, FOOTNOTE, DEADLINE, FOX_FIRE, SAKURA_SEAL, ROYALTIES,
               REPRINT)
ROYALTIES_ENERGY = 1
RED_INK_AMOUNT = 3
FOX_FIRE_DAMAGE = 4
#: What a Publish is worth to the default pilot, best first.
PUBLISH_ORDER = (REPRINT, SAKURA_SEAL, ROYALTIES, FOOTNOTE, RED_INK, FOX_FIRE,
                 DEADLINE)

# --- the powers her rows apply (`apply_power`, target self) ---
SAKURA_GROVE = "ym_sakura_grove"
EDICT = "ym_edict_of_cleansing"
SERIALIZATION = "ym_serialization"
MOONCALL = "ym_foxs_mooncall"
YAKAN_OFFERING = "ym_yakan_offering"
CHANNELING = "ym_sakura_channeling"
EDITOR_IN_CHIEF = "ym_editor_in_chief"
SERIAL_NOVEL = "ym_serial_novel"
#: Auras an Electro strike reacts with (Edict of Cleansing's read).
REACTING_AURAS = ("pyro", "hydro", "cryo")

# --- the relic, as the sim spells a starting relic (`Player.relic_hooks`) ---
MEDITATIONS = "meditations_of_a_yako"
MEDITATIONS_UPGRADED = "meditations_of_a_yako+"
#: Annotations one after-elite Publish may keep (C# `PublishCount`):
#: Enlightened Blessing, the Orobas upgrade, keeps up to two.
PUBLISH_COUNT = {MEDITATIONS: 1, MEDITATIONS_UPGRADED: 2}
#: The rooms whose win offers it (C# `YaeEditing.OffersPublish`).
PUBLISH_ROOMS = ("elite", "boss")

#: The Annotations a Sakura can carry (`edit_sakura`).
SAKURA_ANNOTATIONS = (RED_INK, FOX_FIRE, DEADLINE)
SAKURA_EDIT_ENDS = ("newest", "oldest", "every")

ID_PREFIX = "proto_ym_"
#: Author's Copy never copies an Author's Copy (review r3: LAW, "copy
#: effects never make an energy-positive loop").
AUTHORS_COPY_ID = "proto_ym_authors_copy"
STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "proto_ym_yakan_evocation", "proto_ym_proofread",
)

#: The `yae` op's kinds and the numeric fields each one prints.
KIND_FIELDS = {
    "plant": ("amount",),
    "tenko": (),
    "extend": ("amount",),
    "level_up": ("amount",),
    "edit": ("amount",),
    "edit_all": (),
    "publish": (),
    "lure": (),
    "damage_per_sakura": ("base", "per"),
    "block_per_sakura": ("base", "per"),
    "damage_per_annotated": ("base", "per"),
    "block_per_annotated": ("base", "per"),
    "annotated_strike": ("base", "amount"),
    "fox_fire": (),
    # The design axes (ruled 2026-10-14).
    "edit_sakura": ("amount",),
    "plant_level": ("amount",),
    "strike_if_weak": (),
    # Review r3 (ruled 2026-10-14).
    "fallen_petals": (),
    "second_printing": (),
    "authors_copy": (),
}
KINDS = frozenset(KIND_FIELDS)
KIND_TARGETS = {
    "lure": "enemy", "damage_per_sakura": "enemy",
    "damage_per_annotated": "enemy", "annotated_strike": "enemy",
    "strike_if_weak": "enemy",
}
#: Kinds that take an `annotation:` name.
ANNOTATION_KINDS = frozenset({"edit", "edit_all", "edit_sakura"})
#: Kinds whose `as:` names the kind of Sakura they plant (review r3);
#: absent, a plain Sakura.
PLANT_AS_KINDS = frozenset({"plant", "plant_level"})
#: Kinds that read their upgrade at play time (`yae_upgraded`, C#
#: `IsUpgraded`): Fallen Petals' draw, Second Printing's free card.
UPGRADED_KINDS = frozenset({"fallen_petals", "second_printing"})
OP_FIELDS = frozenset({"op", "kind", "amount", "base", "per", "target",
                       "annotation", "as", "which", "upgraded", "seal",
                       "keeps"})


@dataclass
class Sakura:
    level: int
    turns_left: int
    seq: int                      # planting order, the ledger's clock
    annotation: Optional[str] = None   # Red Ink, Fox Fire or Deadline
    kind: str = THUNDER           # review r3: Thunder, Foxfire or Kitsune
    planted_level: Optional[int] = None   # the Level it was planted at
    #: Yae review r4, item 4: a Deadline Extension Edit that "keeps its Red
    #: Ink" leaves the +3 on a Sakura whose one Annotation slot is now
    #: Deadline Extension.
    red_ink_kept: bool = False


@dataclass
class YaeLedger:
    """Per-fight state, hung on the Player (`Player.yae_ledger`)."""
    sakura: list = field(default_factory=list)
    seq: int = 0
    shrine_bonus: int = 0         # SCALING == "count": +1 per Tenko
    lure: object = None           # this turn's aimed enemy, or None
    strikes: int = 0              # actions this combat
    strike_damage: int = 0        # printed damage, this combat
    edits: int = 0
    #: Reprint (review r3): the cards (by `id`) already played this fight,
    #: so their stacked Reprints are inert for the rest of it.
    reprinted: set = field(default_factory=set)
    #: slot -> the temporary layer the fight left on that deck card (the
    #: evidence the after-elite Publish reads).
    drafts: dict = field(default_factory=dict)
    # --- the pilot's choices (None: the default reading) ---
    edit_choice: object = None    # (state, card, annotation) -> card | None
    reborn_choice: Optional[str] = None
    #: (state, candidates) -> card | None, for Second Printing and Author's
    #: Copy.
    recall_choice: object = None


# --------------------------------------------------------------------------
#  Who is Yae
# --------------------------------------------------------------------------

def live(player) -> bool:
    return getattr(player, "character_id", "") == CHARACTER


def ledger(player) -> Optional[YaeLedger]:
    if not live(player):
        return None
    led = getattr(player, "yae_ledger", None)
    if led is None:
        led = YaeLedger()
        player.yae_ledger = led
    return led


def open_combat(player) -> None:
    """`combat.run_fight`: a fresh shrine per fight."""
    if live(player):
        player.yae_ledger = YaeLedger()


def _power(player, name: str) -> int:
    return int(player.powers.get(name, 0))


def _block(state, amount: int, reason: str) -> None:
    """Unpowered Block (no Dexterity, no Frail), the Powers' door."""
    if amount <= 0:
        return
    state.player.block += amount
    state.emit("block", amount=amount)
    state.emit("yae_block", amount=amount, reason=reason)


# --------------------------------------------------------------------------
#  The shrine
# --------------------------------------------------------------------------

def sakura_count(player) -> int:
    led = ledger(player)
    return 0 if led is None else len(led.sakura)


def sakura_cap(player) -> int:
    """How many Sakura may stand: 3, plus Sakura Channeling's amount (2 per
    copy). The full-shrine rule fires at this. C# twin:
    `YaeShrine.MaxSakura`."""
    return SAKURA_CAP + _power(player, CHANNELING)


def kind_base(kind: str) -> int:
    """What a kind's action adds to its Level: Thunder 2, Foxfire 1,
    Kitsune 2 (read at call time, so a knob moves it). C#
    `YaeShrineLedger.KindBase`."""
    return {THUNDER: SAKURA_BASE, FOXFIRE: FOXFIRE_BASE,
            KITSUNE: KITSUNE_BASE}[kind]


def _plant_level(player) -> int:
    """1, plus 1 for each Fox's Mooncall ("planted 1 Level higher")."""
    return PLANT_LEVEL + _power(player, MOONCALL)


def plant(state, n: int = 1, reason: str = "plant",
          level: Optional[int] = None,
          annotation: Optional[str] = None,
          kind: str = THUNDER) -> None:
    """Plant `n` Sakura of `kind`, one at a time, each at the card's Level
    (`level`, Grafted Branch; else `PLANT_LEVEL`) plus Fox's Mooncall's
    bonus. FULL SHRINE (review r3, amended): the OLDEST acts first; if it is
    the same kind it refreshes (to at least 3) and gains 1 Level and none is
    added; if not, it withers and the new Sakura takes its place, as the
    newest, at its printed Level. `annotation`: what each NEW Sakura
    inherits from the planting card (Red Ink, `inherited`)."""
    if kind not in SAKURA_KINDS:
        raise ValueError(f"unknown Sakura kind {kind!r}")
    led = ledger(state.player)
    if led is None:
        return
    cap = sakura_cap(state.player)
    for _ in range(n):
        if len(led.sakura) >= cap and led.sakura:
            oldest = led.sakura[0]
            if SCALING == "level":
                act(state, oldest, "full_shrine")
                if oldest.kind == kind:
                    oldest.turns_left = max(oldest.turns_left, SAKURA_TURNS)
                    oldest.level += 1
                    # Yae review r4, item 2: the planting card's Red Ink
                    # goes to the refreshed Sakura, as to a new one.
                    if annotation in SAKURA_ANNOTATIONS:
                        oldest.annotation = annotation
                        oldest.red_ink_kept = False
                    state.emit("yae_level", reason=reason,
                               levels=[s.level for s in led.sakura])
                    continue
                # A different kind: the oldest withers, the new one takes
                # its place (changing the mix costs an established Sakura).
                if oldest in led.sakura:
                    led.sakura.remove(oldest)
                state.emit("yae_wither", count=1, standing=len(led.sakura),
                           reason="replaced")
            else:
                led.sakura.pop(0)                   # (b): the oldest goes
        led.seq += 1
        start = _plant_level(state.player)
        if level is not None:
            start = max(start, level + start - PLANT_LEVEL)   # Mooncall too
        led.sakura.append(Sakura(
            level=start, turns_left=SAKURA_TURNS, seq=led.seq,
            annotation=(annotation if annotation in SAKURA_ANNOTATIONS
                        else None),
            kind=kind, planted_level=start))
        state.emit("yae_plant", reason=reason, count=len(led.sakura),
                   kind=kind, levels=[s.level for s in led.sakura])


def act_size(state, s: Sakura) -> int:
    """One action's size, before Edict: Thunder 2 + Level damage, Foxfire
    1 + Level to each enemy, Kitsune 2 + Level Block; a Red Ink Sakura's 3
    adds to any kind (review r3)."""
    led = ledger(state.player)
    if SCALING == "level":
        size = kind_base(s.kind) + s.level
    else:
        size = (COUNT_TABLE[min(SAKURA_CAP, len(led.sakura))]
                + led.shrine_bonus + kind_base(s.kind) - SAKURA_BASE)
    if s.annotation == RED_INK or s.red_ink_kept:
        size += RED_INK_AMOUNT
    return size


#: THE LIVE TENKO CLAUSE (C# twin `YaeShrineFace`). In combat a Tenko card
#: says what its Tenko would do now, summed by kind over the Sakura
#: standing: "Tenko (8 damage, 4 to each enemy, 5 Block)"; with none
#: standing "Tenko (no Sakura)". Before Edict and Fox Fire.
TENKO_FACE = {THUNDER: "{n} damage", FOXFIRE: "{n} to each enemy",
              KITSUNE: "{n} Block"}
NO_SAKURA = " (no Sakura)"


def tenko_totals(state) -> dict:
    """Each kind's summed action size over the Sakura standing."""
    led = ledger(state.player)
    out = {k: 0 for k in SAKURA_KINDS}
    for s in (led.sakura if led else ()):
        out[s.kind] += act_size(state, s)
    return out


def tenko_words(totals: dict) -> str:
    """The clause for each kind's sum, in kind order, zeros left out; with
    nothing standing the "no Sakura" words. PURE."""
    parts = [TENKO_FACE[k].format(n=totals.get(k, 0)) for k in SAKURA_KINDS
             if totals.get(k, 0) > 0]
    return f" ({', '.join(parts)})" if parts else NO_SAKURA


def tenko_line(state) -> str:
    """A Tenko card's live clause; "" off a Yae."""
    if ledger(state.player) is None:
        return ""
    return tenko_words(tenko_totals(state))


def edict_applies(target) -> bool:
    """Edict of Cleansing's read: the enemy is Weak, or wears an aura an
    Electro strike reacts with."""
    return target is not None and (
        target.aura in REACTING_AURAS
        or int(target.powers.get("weak", 0)) > 0)


def strike_damage(state, s: Sakura, target) -> int:
    """A damage action's damage at `target` (Edict included); 0 for a
    Kitsune."""
    if s.kind not in DAMAGE_KINDS:
        return 0
    dmg = act_size(state, s)
    if edict_applies(target):
        dmg += _power(state.player, EDICT)
    return dmg


def _aim(state, aim=None):
    if aim is not None and aim.alive:
        return aim
    led = ledger(state.player)
    if led.lure is not None and led.lure.alive:
        return led.lure
    living = list(state.living_enemies)
    return state.rng.choice(living) if living else None


def _hit(state, target, size: int, reason: str, kind: str) -> None:
    """One damage action's hit: Electro, unpowered, Edict on top."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    dmg = size + (_power(state.player, EDICT) if edict_applies(target) else 0)
    if dmg <= 0:
        return
    led.strike_damage += dmg
    state.emit("yae_sakura_hit", reason=reason, kind=kind, amount=dmg,
               target=target.name)
    effects.deal_damage_to_enemy(state, target, dmg, element=ELEMENT,
                                 source="card", powered=False)


def fox_fire(state, source: str) -> None:
    """Fox Fire: 4 Electro to a random enemy, unpowered, not aimed."""
    from tier0.engine import effects                # late: cycle
    living = list(state.living_enemies)
    if not living:
        return
    target = state.rng.choice(living)
    state.emit("yae_fox_fire", card=source, target=target.name)
    effects.deal_damage_to_enemy(state, target, FOX_FIRE_DAMAGE,
                                 element=ELEMENT, source="card",
                                 powered=False)


def act(state, s: Sakura, reason: str, aim=None) -> None:
    """ONE SAKURA ACTS as its kind (review r3): a Sakura strikes one enemy
    (`aim`, else the Lure's, else random), a Foxfire Sakura hits ALL, a
    Kitsune Sakura gives her Block; then its own Fox Fire, once."""
    led = ledger(state.player)
    if not state.living_enemies:
        return
    size = act_size(state, s)
    led.strikes += 1
    if s.kind == THUNDER:
        target = _aim(state, aim)
        state.emit("yae_sakura_strike", reason=reason, level=s.level,
                   amount=size, kind=s.kind,
                   target=None if target is None else target.name)
        if target is not None:
            _hit(state, target, size, reason, s.kind)
    elif s.kind == FOXFIRE:
        state.emit("yae_sakura_strike", reason=reason, level=s.level,
                   amount=size, kind=s.kind, target="ALL")
        for e in list(state.living_enemies):
            _hit(state, e, size, reason, s.kind)
    else:
        state.emit("yae_sakura_strike", reason=reason, level=s.level,
                   amount=0, kind=s.kind, block=size, target=None)
        _block(state, size, "kitsune")
    if s.annotation == FOX_FIRE:
        fox_fire(state, "sakura")


#: The old name: every caller that "strikes" a Sakura now makes it act.
strike = act


def act_all(state, reason: str) -> None:
    led = ledger(state.player)
    for s in list(led.sakura):
        if not state.living_enemies:
            break
        act(state, s, reason)


def edit_sakura(state, which: str, n: int, annotation: str,
                keeps: Optional[str] = None) -> None:
    """"Edit your newest / oldest Sakura" (`n` from that end), "Edit every
    Sakura" (`which` every): the Annotation replaces any the Sakura
    carried."""
    if annotation not in SAKURA_ANNOTATIONS:
        raise ValueError(f"no Sakura reading for {annotation!r}")
    led = ledger(state.player)
    ordered = led.sakura if which == "oldest" else list(reversed(led.sakura))
    if which == "every":
        n = len(ordered)
    if not ordered:
        state.emit("yae_edit_nothing", what="sakura")
    for s in ordered[:n]:
        had_red = s.annotation == RED_INK or s.red_ink_kept
        s.annotation = annotation
        s.red_ink_kept = bool(keeps == RED_INK and had_red
                              and annotation != RED_INK)
        state.emit("yae_sakura_annotate", seq=s.seq, annotation=annotation)


def highest(led, kinds=SAKURA_KINDS):
    """The highest-Level Sakura of `kinds`, the oldest on a tie (Editor-in-
    Chief any kind; Kitsune Pounce a damage kind)."""
    cands = [s for s in led.sakura if s.kind in kinds]
    if not cands:
        return None
    return max(cands, key=lambda s: (s.level, -s.seq))


def tenko(state) -> None:
    """TENKO (review r3): "Every Sakura acts now. Refresh them to at least 3
    turns." Tenko with no Sakura does nothing."""
    led = ledger(state.player)
    if led is None or not led.sakura:
        return
    state.emit("yae_tenko", count=len(led.sakura))
    act_all(state, "tenko")
    for s in led.sakura:
        s.turns_left = max(s.turns_left, SAKURA_TURNS)
    if SCALING == "count":
        led.shrine_bonus += COUNT_TENKO_BONUS


def extend(state, n: int) -> None:
    led = ledger(state.player)
    for s in led.sakura:
        s.turns_left += n


def level_up(state, n: int) -> None:
    """"Each Sakura gains a Level" (n Levels), no cap."""
    led = ledger(state.player)
    for s in led.sakura:
        s.level += n


def grove(state, n: int) -> None:
    """Sakura Grove: "each Sakura gains a Level" (n Levels)."""
    led = ledger(state.player)
    if led.sakura:
        for s in led.sakura:
            s.level += n
        state.emit("yae_level", reason="sakura_grove",
                   levels=[s.level for s in led.sakura])


def wither_oldest(state, reason: str = "fallen_petals") -> bool:
    """Fallen Petals (review r3): the oldest Sakura acts once (its Last
    Bloom) and withers, Deadline Extension or not. Whether one did."""
    led = ledger(state.player)
    if led is None or not led.sakura:
        return False
    oldest = led.sakura[0]
    act(state, oldest, "bloom")
    if oldest in led.sakura:
        led.sakura.remove(oldest)
    state.emit("yae_wither", count=1, standing=len(led.sakura),
               reason=reason)
    return True


def turn_start(state) -> None:
    """`combat._player_turn`, post-draw: the Lure expires; Serial Novel
    brings back an Annotated card; Yakan Offering plants; then Sakura Grove
    levels every Sakura."""
    led = ledger(state.player)
    if led is None:
        return
    led.lure = None
    for _ in range(_power(state.player, SERIAL_NOVEL)):
        cands = [c for c in state.player.discard_pile if is_annotated(c)]
        if not cands or len(state.player.hand) >= _max_hand():
            break
        pick = state.rng.choice(cands)
        state.player.discard_pile.remove(pick)
        state.player.hand.append(pick)
        state.emit("yae_serial_novel", card=pick.id)
    for _ in range(_power(state.player, YAKAN_OFFERING)):
        plant(state, 1, "yakan_offering")
    levels = _power(state.player, SAKURA_GROVE)
    if levels:
        grove(state, levels)


def turn_end(state) -> None:
    """`combat`'s player turn end: every Sakura acts, then the timers tick.
    LAST BLOOM: each Sakura whose timer ran out, oldest first, acts once
    more, then withers."""
    led = ledger(state.player)
    if led is None:
        return
    act_all(state, "turn_end")
    for s in led.sakura:
        if s.annotation != DEADLINE:          # Deadline Extension: no wither
            s.turns_left -= 1
    withered = [s for s in led.sakura if s.turns_left <= 0]
    for s in withered:
        act(state, s, "bloom")                # still standing as it blooms
        led.sakura.remove(s)
        state.emit("yae_wither", count=1, standing=len(led.sakura))
    _record_drafts(state)


def _record_drafts(state) -> None:
    """The manuscript: every deck card's slot -> its temporary layer, read
    at the end of each turn so a fight that ends mid-turn still left it."""
    led = ledger(state.player)
    p = state.player
    for pile in (p.hand, p.draw_pile, p.discard_pile, p.exhaust_pile):
        for c in pile:
            slot = getattr(c, "ym_slot", None)
            t = temp(c)
            if slot is not None and t:
                led.drafts[slot] = t


def _max_hand() -> int:
    from tier0 import constants as C                # late: cycle
    return C.MAX_HAND_SIZE


# --------------------------------------------------------------------------
#  The publishing house: two layers per card (review r3, sec.2)
# --------------------------------------------------------------------------

def stack(card) -> list:
    """The permanent stack: every Published Annotation, oldest first."""
    return list(getattr(card, "ym_stack", None) or ())


def temp(card) -> Optional[str]:
    """The one temporary slot (this combat's Edit), or None."""
    return getattr(card, "ym_temp", None)


def layers(card) -> list:
    """Every layer, the stack first, then the temporary slot."""
    t = temp(card)
    return stack(card) + ([t] if t else [])


def count(card, name: str) -> int:
    """How many layers of `name` the card carries."""
    return layers(card).count(name)


def is_annotated(card) -> bool:
    """"Annotated": carrying any layer, a Published one included."""
    return bool(layers(card))


def is_published(card) -> bool:
    return bool(stack(card))


def annotated_in_hand(state) -> int:
    return sum(1 for c in state.player.hand if is_annotated(c))


def _apply_layers(card) -> None:
    """The card's riders from every layer, added up (review r3): Red Ink
    +3 each on damage and Block, Deadline Retain, and one play rider per
    Footnote, Fox Fire, Sakura Seal and Royalties layer, stack first."""
    if getattr(card, "ym_base_retain", None) is None:
        card.ym_base_retain = bool(card.retain)
    ls = layers(card)
    red = ls.count(RED_INK)
    card.enchant_damage = RED_INK_AMOUNT * red
    card.enchant_block = RED_INK_AMOUNT * red
    card.retain = card.ym_base_retain or DEADLINE in ls
    riders = []
    for name in ls:
        if name == FOOTNOTE:
            riders.append({"op": "draw", "amount": 1})
        elif name == FOX_FIRE:
            riders.append({"op": "yae", "kind": "fox_fire"})
        elif name == SAKURA_SEAL:
            riders.append({"op": "yae", "kind": "plant", "amount": 1,
                           "seal": True})
        elif name == ROYALTIES:
            riders.append({"op": "energy", "amount": ROYALTIES_ENERGY})
    card.enchant_effects = riders


def annotate(state, card, name: str, reason: str = "edit") -> None:
    """An Edit: `name` fills the card's ONE TEMPORARY SLOT, replacing what
    was there; the stack is never touched. A temporary Reprint arms one
    fresh replay."""
    if name not in ANNOTATIONS:
        raise ValueError(f"unknown Annotation {name!r}")
    card.ym_temp = name
    card.ym_armed = 1 if name == REPRINT else 0
    slot = getattr(card, "ym_slot", None)
    if state is not None and slot is not None:
        led = ledger(state.player)
        if led is not None:
            led.drafts[slot] = name
    _apply_layers(card)
    if state is not None:
        state.emit("yae_annotate", card=card.id, annotation=name,
                   reason=reason)


def publish_card(state, card) -> Optional[str]:
    """PUBLISH: the temporary layer moves onto the stack, once. Returns the
    Annotation Published, or None with an empty slot. A temporary Reprint
    that moves before the card's first play this combat is counted by the
    stack from then on, so its armed replay is dropped (never counted
    twice)."""
    t = temp(card)
    if not t:
        return None
    card.ym_stack = stack(card) + [t]
    card.ym_temp = None
    if t == REPRINT and state is not None:
        led = ledger(state.player)
        if led is not None and id(card) not in led.reprinted:
            card.ym_armed = 0
    _apply_layers(card)
    slot = getattr(card, "ym_slot", None)
    if state is not None:
        led = ledger(state.player)
        if led is not None and slot is not None:
            led.drafts.pop(slot, None)
        state.emit("yae_publish", card=card.id, annotation=t,
                   stack=list(card.ym_stack))
    return t


def publish_to(card, names) -> None:
    """A deck card enters the fight with this stack (the run harness's
    permanence, `build_player`)."""
    if isinstance(names, str):
        names = [names]
    card.ym_stack = stack(card) + list(names)
    _apply_layers(card)


#: The `yae` kinds whose play plants a Sakura (C# `ISakuraPlanterCard`,
#: `gen_klee_cards.YAE_PLANT_KINDS`).
PLANT_KINDS = frozenset({"plant", "plant_level"})


def _walk(effects):
    """Every effect, `conditional` branches and `choose_one` modes
    included."""
    for fx in effects or ():
        yield fx
        if fx.get("op") == "conditional":
            yield from _walk(fx.get("then"))
            yield from _walk(fx.get("else"))
        if fx.get("op") == "choose_one":
            for mode in fx.get("modes") or ():
                yield from _walk(mode.get("effects"))


def plants_sakura(card) -> bool:
    """Does the card's own play plant a Sakura?"""
    return any(fx.get("op") == "yae" and fx.get("kind") in PLANT_KINDS
               for fx in _walk(card.effects))


def deals_damage(card) -> bool:
    """An Attack, or any card with a damage op (the C# reads a damage var):
    widened past Sharp's Attack door so a Skill that hits stays editable."""
    return card.type == "attack" or any(
        fx.get("op") == "damage" for fx in _walk(card.effects))


#: The `yae` kinds that give the card's own Block (C# `IYaeBlockCard`).
BLOCK_KINDS = frozenset({"block_per_sakura", "block_per_annotated"})


def gives_block(card) -> bool:
    """Nimble's door (the game's `GainsBlock`), or a `yae` kind that gives
    the card's own Block (Print Run), which Red Ink rides too."""
    from tier0.content import enchantments          # late: cycle
    return enchantments._gains_block(card) or any(
        fx.get("op") == "yae" and fx.get("kind") in BLOCK_KINDS
        for fx in _walk(card.effects))


def playable(card) -> bool:
    """Can the card be played at all? A Status or Curse, or an Unplayable
    card, never is (C# `YaeAnnotationReach.Playable`)."""
    return not card.is_junk and "unplayable" not in (card.tags or ())


def affects(card, annotation: str) -> bool:
    """Would `annotation` do anything on `card`? Red Ink needs damage, Block
    or a plant; Reprint needs a playable card. C#
    `YaeAnnotationReach.Affects`."""
    if annotation == REPRINT:
        return playable(card)
    return (annotation != RED_INK or deals_damage(card) or gives_block(card)
            or plants_sakura(card))


def reprint_replays(state, card) -> int:
    """REPRINT, EXACTLY (review r3): a card's Reprints add up. On its first
    play each combat it replays once per Reprint on its stack, then those go
    inert for the combat; a temporary Reprint arms one fresh replay (spent
    on the next play). C# `YaeMasterpiece.EnchantPlayCount`."""
    led = ledger(state.player)
    if led is None:
        return 0
    n = 0
    if id(card) not in led.reprinted:
        n += stack(card).count(REPRINT)
        led.reprinted.add(id(card))
    n += int(getattr(card, "ym_armed", 0) or 0)
    card.ym_armed = 0
    if n:
        state.emit("yae_reprint", card=card.id, replays=n)
    return n


def reprint_used(state, card) -> bool:
    """The display's "Reprint: used": the card carries Reprint and has no
    replay left this combat."""
    led = ledger(state.player)
    if led is None or count(card, REPRINT) == 0:
        return False
    return id(card) in led.reprinted and not getattr(card, "ym_armed", 0)


def inherits(card) -> bool:
    """Does the card's Red Ink pass to the Sakura it plants? Red Ink on any
    layer of a card that plants; once, however many layers (review r3)."""
    return count(card, RED_INK) > 0 and plants_sakura(card)


def inherited(card) -> Optional[str]:
    return RED_INK if inherits(card) else None


def _editable(state, editor, annotation: Optional[str] = None) -> list:
    """The cards an Edit can reach; with `annotation`, only those it would
    do something on (the dead-edit filter)."""
    return [c for c in state.player.hand
            if c is not editor and not c.kit_card and not c.is_junk
            and (annotation is None or affects(c, annotation))]


def _edit_reaches(state, editor, annotation: str) -> list:
    """The cards an Edit (the chooser and Reborn as Guuji Yae) can reach:
    `_editable` with the dead-edit filter. A Published card is reachable
    (review r3, pick 2 (a)): the Edit fills its temporary slot. C# twin:
    `YaeEditing.EditReaches`."""
    return _editable(state, editor, annotation)


def _has_op(card, op: str) -> bool:
    return any(fx.get("op") == op for fx in card.effects)


def _edit_target(state, editor, annotation: str):
    """The default reading of "a card in your hand": Red Ink goes on the
    hardest-hitting Attack (most hits), else a Block card; Deadline on the
    dearest card; Reprint on the dearest card, an Attack first; the play
    riders on the cheapest card. A card with an empty temporary slot is
    preferred, so an Edit replaces one only when it must."""
    cands = _edit_reaches(state, editor, annotation)
    if not cands:
        return None
    fresh = [c for c in cands if not temp(c)] or cands

    def cost(c):
        return c.cost if isinstance(c.cost, int) else 1

    if annotation == RED_INK:
        hits = [c for c in fresh if _has_op(c, "damage")]
        if hits:
            return max(hits, key=lambda c: (
                max((int(fx.get("times", 1)) if isinstance(
                    fx.get("times", 1), int) else 1)
                    for fx in c.effects if fx.get("op") == "damage"),
                -cost(c)))
        blocks = [c for c in fresh if _has_op(c, "block")]
        return blocks[0] if blocks else fresh[0]
    if annotation == DEADLINE:
        return max(fresh, key=cost)
    if annotation == REPRINT:
        # The card most worth a second play: the dearest, an Attack first.
        return max(fresh, key=lambda c: (cost(c), c.type == "attack"))
    plain = [c for c in fresh if not c.exhaust] or fresh
    return min(plain, key=cost)


def edit(state, editor, annotation: str, n: int = 1) -> None:
    led = ledger(state.player)
    for _ in range(n):
        chooser = led.edit_choice or _edit_target
        target = chooser(state, editor, annotation)
        if target is None or target not in _edit_reaches(state, editor,
                                                     annotation):
            if not _edit_reaches(state, editor, annotation):
                # Yae review r4, item 8: it says so rather than doing nothing.
                state.emit("yae_edit_nothing", what="hand")
            return
        annotate(state, target, annotation)
        led.edits += 1


def edit_all(state, editor, default: str) -> None:
    """Reborn as Guuji Yae: one Annotation (the pilot's `reborn_choice`,
    else the row's) on every other card in hand."""
    led = ledger(state.player)
    name = led.reborn_choice or default
    cards = _edit_reaches(state, editor, name)
    if not cards:
        state.emit("yae_edit_nothing", what="hand")
    for c in cards:
        annotate(state, c, name, "reborn")
    if cards:
        led.edits += len(cards)


def publish(state, editor) -> None:
    """The Seven Glamours (Yae review r4, item 5): EVERY card in hand with a
    temporary layer is Published (the layer moves onto its stack). Was the
    best one only."""
    for c in [c for c in _editable(state, editor) if temp(c)]:
        publish_card(state, c)


def offers_publish(room: str, gives_rewards: bool = True,
                   final_boss: bool = False) -> bool:
    """Meditations of a Yako: "After an elite or boss fight, you may Publish
    an Annotation." Never a normal fight, and never the final boss (no
    reward screen follows it). C# `YaeEditing.OffersPublish`."""
    return gives_rewards and not final_boss and room in PUBLISH_ROOMS


def publish_choices(drafts: dict, published: Optional[dict] = None,
                    cards: Optional[dict] = None) -> list:
    """The offer: every deck slot the fight left with a temporary layer, in
    slot order. A Published slot is offered again (review r3: stacks grow),
    so `published` filters nothing. `cards` (slot -> card): a slot whose
    draft would do nothing on its card is not offered (the dead-edit
    filter). C# `YaeEditing.PublishChoices`."""
    return [slot for slot in sorted(drafts)
            if drafts[slot]
            and (cards is None or slot not in cards
                 or affects(cards[slot], drafts[slot]))]


def publish_after_fight(room: str, drafts: dict, published: dict,
                        relic: str = MEDITATIONS, pick=None,
                        final_boss: bool = False,
                        cards: Optional[dict] = None) -> list:
    """The after-elite Publish, run-level: `drafts` is the fight's
    (`YaeLedger.drafts`), `published` the run's {slot: [stack]}, grown in
    place. `pick(choices, drafts)` returns the slots to keep (empty is the
    skip); the default reading keeps the best by `PUBLISH_ORDER`. Returns
    [(slot, Annotation)] Published, empty when nothing is offered."""
    if relic not in PUBLISH_COUNT or not offers_publish(
            room, final_boss=final_boss):
        return []
    choices = publish_choices(drafts, published, cards)
    if not choices:
        return []
    if pick is None:
        picked = sorted(choices, key=lambda s: (
            PUBLISH_ORDER.index(drafts[s]), s))
    else:
        picked = [s for s in (pick(choices, drafts) or []) if s in choices]
    out = []
    for slot in picked[:PUBLISH_COUNT[relic]]:
        have = published.get(slot) or []
        if isinstance(have, str):
            have = [have]
        published[slot] = list(have) + [drafts[slot]]
        out.append((slot, drafts[slot]))
    return out


def after_play(state, card) -> None:
    """`effects.resolve_card`, after the card's own effects, for an
    Annotated card: Serialization ("whenever you play an Annotated card,
    gain 3 Block"), then Editor-in-Chief, "a Sakura strikes" (the
    highest-Level Sakura acts as its kind, the oldest on a tie)."""
    led = ledger(state.player)
    if led is None or not is_annotated(card):
        return
    _block(state, _power(state.player, SERIALIZATION), "serialization")
    if not led.sakura:
        return
    for _ in range(_power(state.player, EDITOR_IN_CHIEF)):
        if not state.living_enemies:
            return
        act(state, highest(led), "editor_in_chief")


# --------------------------------------------------------------------------
#  The signature cards (review r3, sec.3)
# --------------------------------------------------------------------------

def _recall_default(state, cands):
    """The default pick among Annotated cards: the most layers, then the
    dearest."""
    def cost(c):
        return c.cost if isinstance(c.cost, int) else 1
    return max(cands, key=lambda c: (len(layers(c)), cost(c)))


def second_printing(state, card, free: bool) -> None:
    """"Put an Annotated card from your Discard Pile into your hand. [It
    costs 0 this turn.]" Nothing Annotated there: nothing happens."""
    led = ledger(state.player)
    p = state.player
    cands = [c for c in p.discard_pile if is_annotated(c)]
    if not cands or len(p.hand) >= _max_hand():
        return
    pick = (led.recall_choice or _recall_default)(state, cands)
    if pick is None or pick not in cands:
        return
    p.discard_pile.remove(pick)
    p.hand.append(pick)
    if free:
        pick.free_this_turn = True
    state.emit("yae_second_printing", card=pick.id, free=free)


def copy_candidates(state, editor) -> list:
    """Author's Copy's targets: the Annotated cards in hand, never an
    Author's Copy (LAW: copy effects never make an energy-positive loop)."""
    return [c for c in state.player.hand
            if c is not editor and is_annotated(c)
            and not c.id.startswith(AUTHORS_COPY_ID)]


def make_copy(card):
    """A copy is a new card: every layer kept, no deck slot, its Reprints
    armed (a temporary Reprint arms one fresh replay; the stack's fire on
    its first play)."""
    import copy as _copy
    clone = _copy.deepcopy(card)
    clone.ym_slot = None
    clone.ym_armed = 1 if temp(clone) == REPRINT else 0
    return clone


def authors_copy(state, editor) -> None:
    """"Add a copy of an Annotated card in your hand (not an Author's Copy)
    to your hand. It keeps its Annotations." A full hand: the copy goes to
    the Discard Pile, as every made card does."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    cands = copy_candidates(state, editor)
    if not cands:
        return
    pick = (led.recall_choice or _recall_default)(state, cands)
    if pick is None or pick not in cands:
        return
    clone = make_copy(pick)
    effects._add_token(state, clone, "hand")
    state.emit("yae_authors_copy", card=pick.id)


#: Universals never offered to one character: "Yae Miko -- Sesshou Sakura"
#: stays in the Inazuma roster for the others and is hidden from Yae's own
#: offers (pick 5 (a), ruled 2026-10-13). C# twin:
#: `CompanionPool.IsHiddenFrom`.
HIDDEN_COMPANIONS = {"proto_mi_yae_sesshou_sakura": CHARACTER}


def hidden_from(card_id: str, character_id) -> bool:
    """Is this companion never offered to `character_id`?"""
    return HIDDEN_COMPANIONS.get(card_id) == character_id


# --------------------------------------------------------------------------
#  The op
# --------------------------------------------------------------------------

def _refuse(what: str) -> None:
    raise NotImplementedError(
        f"{what} is YAE's (tier0/engine/yae_shrine.py) and resolves only "
        "for a Yae seat; no shipped row prints it.")


def validate_op(card_id: str, fx: dict) -> None:
    """The loader's shape check for one `yae` op, AT LOAD."""
    kind = fx.get("kind")
    if kind not in KINDS:
        raise ValueError(f"card {card_id!r}: unknown yae kind {kind!r}")
    unknown = set(fx) - OP_FIELDS
    if unknown:
        raise ValueError(f"card {card_id!r}: yae {kind!r} has unknown "
                         f"fields {sorted(unknown)}")
    have = set(fx) & {"per", "base", "amount"}
    want = set(KIND_FIELDS[kind])
    if want != have:
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes the fields "
                         f"{sorted(want)}, got {sorted(have)}")
    for key in want:
        if not isinstance(fx[key], int) or fx[key] < 0:
            raise ValueError(f"card {card_id!r}: yae {kind!r} `{key}` must "
                             f"be a non-negative int, got {fx[key]!r}")
    if fx.get("target") != KIND_TARGETS.get(kind):
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes target "
                         f"{KIND_TARGETS.get(kind)!r}, got "
                         f"{fx.get('target')!r}")
    if (kind in ANNOTATION_KINDS) != ("annotation" in fx):
        raise ValueError(f"card {card_id!r}: yae {kind!r} "
                         f"{'needs' if kind in ANNOTATION_KINDS else 'takes no'}"
                         " `annotation:`")
    if "annotation" in fx and fx["annotation"] not in ANNOTATIONS:
        raise ValueError(f"card {card_id!r}: unknown Annotation "
                         f"{fx['annotation']!r}")
    if "as" in fx and kind not in PLANT_AS_KINDS:
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes no `as:` "
                         "(review r3: the typed Tenko is gone)")
    if "as" in fx and fx["as"] not in (FOXFIRE, KITSUNE):
        raise ValueError(f"card {card_id!r}: unknown Sakura kind "
                         f"{fx['as']!r}")
    if "upgraded" in fx and kind not in UPGRADED_KINDS:
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes no "
                         "`upgraded:`")
    if "seal" in fx:
        raise ValueError(f"card {card_id!r}: `seal:` is Sakura Seal's "
                         "rider, never a row's")
    if (kind == "edit_sakura") != ("which" in fx):
        raise ValueError(f"card {card_id!r}: yae {kind!r} "
                         f"{'needs' if kind == 'edit_sakura' else 'takes no'}"
                         " `which:`")
    if "which" in fx and fx["which"] not in SAKURA_EDIT_ENDS:
        raise ValueError(f"card {card_id!r}: `which:` is newest, oldest or "
                         "every, "
                         f"got {fx['which']!r}")
    if "keeps" in fx and (kind != "edit_sakura" or fx["keeps"] != RED_INK):
        raise ValueError(f"card {card_id!r}: `keeps:` is red_ink, on an "
                         "edit_sakura")
    if kind == "edit_sakura" and fx["annotation"] not in SAKURA_ANNOTATIONS:
        raise ValueError(f"card {card_id!r}: {fx['annotation']!r} has no "
                         "Sakura reading")


def _card_hit(state, card, amount: int) -> None:
    """One powered Electro hit of the card on the play's aim."""
    from tier0.engine import effects                # late: cycle
    targets = effects._pick_targets(state, "enemy")
    if not targets or amount <= 0:
        return
    if card.type == "attack":
        amount += state.current_attack_bonus + card.enchant_damage
    source = "attack" if card.type == "attack" else "card"
    effects.deal_damage_to_enemy(state, targets[0], amount, element=ELEMENT,
                                 source=source)


def _card_block(state, card, amount: int) -> None:
    from tier0.engine import effects                # late: cycle
    if amount > 0:
        effects._op_block(state, {"op": "block", "amount": amount}, card)


def op_yae(state, fx: dict, card) -> None:
    """`effects.OPS['yae']`."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    if led is None:
        _refuse(f"op 'yae' ({fx.get('kind')!r}) on {card.id!r}")
    kind = fx["kind"]
    if kind == "plant":
        # Sakura Seal's rider plants a plain Sakura and passes nothing on.
        plant(state, fx["amount"], "card",
              annotation=None if fx.get("seal") else inherited(card),
              kind=fx.get("as", THUNDER))
    elif kind == "tenko":
        tenko(state)
    elif kind == "extend":
        extend(state, fx["amount"])
    elif kind == "level_up":
        level_up(state, fx["amount"])
    elif kind == "edit":
        edit(state, card, fx["annotation"], fx["amount"])
    elif kind == "edit_all":
        edit_all(state, card, fx["annotation"])
    elif kind == "publish":
        publish(state, card)
    elif kind == "lure":
        targets = effects._pick_targets(state, "enemy")
        led.lure = targets[0] if targets else None
    elif kind == "damage_per_sakura":
        _card_hit(state, card, fx["base"] + fx["per"] * len(led.sakura))
    elif kind == "block_per_sakura":
        _card_block(state, card, fx["base"] + fx["per"] * len(led.sakura))
    elif kind == "damage_per_annotated":
        _card_hit(state, card,
                  fx["base"] + fx["per"] * annotated_in_hand(state))
    elif kind == "block_per_annotated":
        _card_block(state, card,
                    fx["base"] + fx["per"] * annotated_in_hand(state))
    elif kind == "annotated_strike":
        _card_hit(state, card,
                  fx["base"] + (fx["amount"] if is_annotated(card) else 0))
    elif kind == "fox_fire":
        fox_fire(state, card.id)
    elif kind == "edit_sakura":
        edit_sakura(state, fx["which"], fx["amount"], fx["annotation"],
                    fx.get("keeps"))
    elif kind == "plant_level":
        plant(state, 1, "card", level=fx["amount"],
              annotation=inherited(card), kind=fx.get("as", THUNDER))
    elif kind == "strike_if_weak":
        targets = effects._pick_targets(state, "enemy")
        target = targets[0] if targets else None
        if (target is not None and target.alive
                and int(target.powers.get("weak", 0)) > 0):
            s = highest(led, DAMAGE_KINDS)
            if s is not None:
                act(state, s, "pounce", aim=target)
    elif kind == "fallen_petals":
        if wither_oldest(state):
            state.player.energy += 1
            state.emit("energy", amount=1)
            if fx.get("upgraded"):
                state.draw(1)
    elif kind == "second_printing":
        second_printing(state, card, bool(fx.get("upgraded")))
    elif kind == "authors_copy":
        authors_copy(state, card)
    else:
        _refuse(f"yae kind {kind!r}")


# --------------------------------------------------------------------------
#  Building her
# --------------------------------------------------------------------------

def starter_ids() -> list[str]:
    return list(STARTER_IDS)


def build_player(extra: tuple = (), hp: Optional[int] = None,
                 relic: bool = True, relic_upgraded: bool = False,
                 published: Optional[dict] = None):
    """A fresh Yae combat Player (72 HP) holding the starter, `extra` card
    ids and Meditations of a Yako. `published` is {deck slot: stack} (a
    list of Annotations, or one name; slots index `starter_ids() + extra`):
    those cards enter the fight with that stack, the run harness's
    permanence. Every card carries its slot (`ym_slot`) so the fight can
    report the drafts it leaves."""
    from tier0.content import loader                # late: cycle
    from tier0.engine.state import Player
    ids = starter_ids() + list(extra)
    cards = []
    for i, cid in enumerate(ids):
        c = loader.get_card(cid)
        c.ym_slot = i
        cards.append(c)
    hp = HP if hp is None else hp
    player = Player(hp=hp, max_hp=max(hp, HP), draw_pile=cards,
                    element=ELEMENT, cadence=CADENCE,
                    character_id=CHARACTER)
    if relic or relic_upgraded:
        player.relic_hooks.append(
            MEDITATIONS_UPGRADED if relic_upgraded else MEDITATIONS)
    player.yae_ledger = YaeLedger()
    for slot, names in (published or {}).items():
        publish_to(cards[slot], names)
    return player
