"""YAML content loading: cards, characters, encounters, pilots.

Card files may hold one card or a list. Everything is validated minimally —
this is design tooling; a loud KeyError beats a validation framework.
"""

from __future__ import annotations

import copy
from functools import lru_cache
from pathlib import Path

import yaml

from tier0 import constants as C
from tier0.content import upgrades
from tier0.engine.state import Card, Enemy, Player

CONTENT_DIR = Path(__file__).parent
# Design sheets in docs/ are the single source of truth for real card
# pools — the sim reads them directly so design and sim never drift.
DOCS_DIR = CONTENT_DIR.parents[1] / "docs"
DOCS_CARD_SHEETS = ("klee-cards.yaml", "mondstadt-companions.yaml")


def _load_yaml_dir(sub: str) -> list[dict]:
    docs = []
    for path in sorted((CONTENT_DIR / sub).glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        docs.extend(data if isinstance(data, list) else [data])
    return docs


def _is_reaction_fuel(card: Card) -> bool:
    """Does this companion feed or amplify the reaction system?

    DERIVED, not written per-row in the sheet, and that is the design decision
    rather than an implementation shortcut. Companions carried NO archetype tag
    at all, while tier05's adaptive scorer handed them a bonus scaled by
    reaction's share -- a share they could never raise, because untagged cards
    are invisible to `archetype_shares`. Reaction could not bootstrap through
    its own enablers.

    Deriving from effects keeps the tag from drifting away from what the card
    does. The rule is: a companion is reaction fuel iff it applies an element,
    places an aura, swirls (swirl IS a reaction), amplifies reactions, keys
    off existing auras (`consumes_aura` -- Albedo's Crystallize engine reads
    them, a reaction payoff), or summons something that applies an element
    (`summon_element` -- Oz).

    The last two fields exist because of this function (M7 ruling R4): both
    cards read as reaction cards to a human, but the only evidence was a
    prose `note`, and inferring intent from prose is exactly the drift this
    avoids. The sheet now says it structurally, so the tag can be honest.
    (The engine's oz_summon tick hardcodes electro; test_m6 pins the sheet
    field to that literal so the two cannot drift apart silently.)
    """
    for fx in card.effects:
        if fx.get("applies_element"):
            return True
        if fx.get("op") in ("apply_aura", "swirl"):
            return True
        if fx.get("consumes_aura") or fx.get("summon_element"):
            return True
        if (fx.get("op") == "apply_power"
                and fx.get("power") in C.AMP_PAYOFF_POWERS):
            return True
    return False


@lru_cache(maxsize=1)
def _card_index() -> dict[str, Card]:
    raw = _load_yaml_dir("cards")
    for sheet in DOCS_CARD_SHEETS:
        path = DOCS_DIR / sheet
        if path.exists():
            docs = yaml.safe_load(path.read_text())
            # Nation comes from the sheet name ("mondstadt-companions.yaml"),
            # not a per-card field: it is a property of the pool a card ships
            # in, and repeating it on every row is just drift waiting to
            # happen. This is what makes the v1.8 banner roll per-nation
            # without touching the sheets when Liyue lands.
            if sheet.endswith("-companions.yaml"):
                nation = sheet.split("-", 1)[0]
                for d in docs:
                    d.setdefault("nation", nation)
            raw.extend(docs)
    cards = [Card.from_dict(d) for d in raw]
    for c in cards:
        if c.role_c and "companion" not in c.tags:   # sheet marks via role_c
            c.tags.append("companion")
        if c.is_companion and _is_reaction_fuel(c):
            if "reaction" not in c.archetypes:
                c.archetypes.append("reaction")
    index = {c.id: c for c in cards}
    if len(index) != len(cards):
        seen: set[str] = set()
        dupes = {c.id for c in cards if c.id in seen or seen.add(c.id)}
        raise ValueError(f"duplicate card ids: {sorted(dupes)}")
    return index


def cards_in_pool(pool: str) -> list[Card]:
    """Named draft pools for add_card (e.g. Secret Stash's
    'demolition_commons')."""
    archetype, _, rarity = pool.rpartition("_")
    rarity = rarity.rstrip("s")                      # commons -> common
    cards = [c for c in _card_index().values()
             if rarity == c.rarity and archetype in c.archetypes
             and not c.kit_card]              # kit is never draftable (v1.9)
    if not cards:
        raise ValueError(f"empty card pool {pool!r}")
    return cards


def get_card(card_id: str) -> Card:
    """`<id>+` returns the upgraded form (M7) -- deck lists stay strings."""
    if card_id.endswith(upgrades.SUFFIX):
        base = copy.deepcopy(_card_index()[card_id[:-len(upgrades.SUFFIX)]])
        return upgrades.apply_upgrade(base)
    return copy.deepcopy(_card_index()[card_id])


@lru_cache(maxsize=1)
def _character_index() -> dict[str, dict]:
    return {d["id"]: d for d in _load_yaml_dir("characters")}


def _kit_cards(spec: dict) -> list[Card]:
    """v1.9: the character's kit Bursts, attached to the Player rather than
    shuffled into any deck. The character yaml names them (`kit:`) and the
    card sheet marks them (`kit_card: true`); requiring both to agree is the
    cross-check -- a card in a kit list that the sheet does not mark would
    silently dodge the pool exclusion, so it is a loud error instead."""
    kit = []
    for cid in spec.get("kit", []):
        card = get_card(cid)
        if not card.kit_card:
            raise ValueError(
                f"{spec['id']}: kit lists {cid!r} but the sheet does not "
                f"mark it kit_card")
        kit.append(card)
    return kit


def build_player(character_id: str, deck: str = "starter") -> Player:
    """deck: 'starter' or the name of a package list in the character yaml
    (e.g. 'archetype_package') appended to the starter deck."""
    spec = _character_index()[character_id]
    card_ids = list(spec["starting_deck"])
    if deck != "starter":
        card_ids += spec["packages"][deck]
    return Player(hp=spec["hp"], max_hp=spec["hp"],
                  draw_pile=[get_card(cid) for cid in card_ids],
                  element=spec.get("element", "none"),
                  cadence=spec.get("cadence", "skill"),
                  burst_max=spec.get("burst_max", 0),
                  relic_hooks=list(spec.get("relic_hooks", [])),
                  kit_cards=_kit_cards(spec))


def build_player_from_ids(character_id: str, card_ids: list[str]) -> Player:
    """Tier 0.5: build a player around an arbitrary (drafted) deck list."""
    spec = _character_index()[character_id]
    return Player(hp=spec["hp"], max_hp=spec["hp"],
                  draw_pile=[get_card(cid) for cid in card_ids],
                  element=spec.get("element", "none"),
                  cadence=spec.get("cadence", "skill"),
                  burst_max=spec.get("burst_max", 0),
                  relic_hooks=list(spec.get("relic_hooks", [])),
                  kit_cards=_kit_cards(spec))


def starting_deck(character_id: str) -> list[str]:
    return list(_character_index()[character_id]["starting_deck"])


def character_packages(character_id: str) -> dict[str, list[str]]:
    return {k: list(v) for k, v in
            _character_index()[character_id].get("packages", {}).items()}


@lru_cache(maxsize=1)
def _encounter_index() -> dict[str, dict]:
    return {d["id"]: d for d in _load_yaml_dir("encounters")}


def encounter_ids() -> list[str]:
    return sorted(_encounter_index())


def encounter_stages(encounter_id: str) -> list[str]:
    """A plain encounter is one stage; a 'sequence' encounter (GAUNTLET)
    lists stage encounter ids fought back-to-back with HP carryover."""
    spec = _encounter_index()[encounter_id]
    return list(spec.get("sequence", [encounter_id]))


def build_encounter(encounter_id: str) -> list[Enemy]:
    spec = _encounter_index()[encounter_id]
    if "sequence" in spec:
        raise ValueError(f"{encounter_id} is a sequence; use encounter_stages()")
    enemies = []
    for e in spec["enemies"]:
        for _ in range(e.get("count", 1)):
            enemies.append(Enemy(
                hp=e["hp"], max_hp=e["hp"], name=e["name"],
                intents=copy.deepcopy(e["intents"]),
                is_boss=e.get("is_boss", False),
                sleep_turns=e.get("sleep_turns", 0)))
    return enemies


@lru_cache(maxsize=1)
def _pilot_index() -> dict[str, dict]:
    return {d["id"]: d for d in _load_yaml_dir("pilots")}


def pilot_weights(pilot_id: str) -> dict:
    return _pilot_index()[pilot_id]["weights"]


def character_constraints(character_id: str) -> list[str]:
    """Identity constraints like "A1_frontload>A2_scaling" — hard on
    starter and the archetype-deck median, a warning on package decks
    (round-3 restructure)."""
    return list(_character_index()[character_id].get("constraints", []))


def archetype_decks(character_id: str) -> dict[str, str]:
    """deck -> pilot mapping for the median identity evaluation."""
    return dict(_character_index()[character_id].get("archetype_decks", {}))


def deck_bands(character_id: str) -> dict[str, dict[str, float]]:
    """Per-axis, per-deck score ceilings, e.g. A2_scaling caps."""
    return dict(_character_index()[character_id].get("deck_bands", {}))


def winrate_bands(character_id: str) -> dict[str, dict[str, tuple]]:
    """Ratified per-encounter winrate bands: enc -> deck -> (lo, hi).
    hi may be None (floor only). Checked at >=WINRATE_BAND_MIN_FIGHTS."""
    raw = _character_index()[character_id].get("winrate_bands", {})
    return {enc: {deck: (band[0], band[1]) for deck, band in per_deck.items()}
            for enc, per_deck in raw.items()}
