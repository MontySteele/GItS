"""YAML content loading: cards, characters, encounters, pilots.

Card files may hold one card or a list. Everything is validated minimally —
this is design tooling; a loud KeyError beats a validation framework.
"""

from __future__ import annotations

import copy
import warnings
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
DOCS_CARD_SHEETS = ("klee-cards.yaml", "furina-cards.yaml",
                    "mondstadt-companions.yaml", "fontaine-companions.yaml")

# The real base-game pool (tools/extract_base_game_pool.py ->
# tools/build_ironclad_sheet.py). game_ref/ is gitignored (.gitignore:28):
# decompiled material is REFERENCE ONLY, so this is a regenerable LOCAL
# artifact that is simply absent on a fresh clone.
#
# Absence is TOTAL and that is the design, not an accident: the cards live
# here AND so does the character yaml (char_*.yaml below). Committing a
# character whose starting_deck ids ship in a gitignored file would leave
# `build_player("real_ironclad")` a KeyError on every fresh clone -- a
# committed reference to a missing thing. Nothing in the repo names
# real_ironclad except inert guards (tier05.rewards.NO_COMPANION_CHARACTERS)
# and a skip-guarded test module.
GAME_REF_DIR = CONTENT_DIR.parents[1] / "game_ref"
EXTERNAL_CARD_SHEETS = {"ironclad_pool.yaml": "real_ironclad"}
EXTERNAL_CARD_LAYERS = {
    "ironclad_pool.yaml": (
        "ironclad_pool_pass4.yaml",
        "ironclad_pool_pass5.yaml",
        "ironclad_pool_pass6.yaml",
    ),
}

# The two hand-approximated reference characters own the cards/ sheets.
# Same sheet-name convention as DOCS_CARD_SHEETS: ownership is a property
# of the pool a card ships in, not a field repeated on every row.
#
# This tagging is what makes the rewards.character_pool ownership filter
# work. Before it, these rows had character=None and the filter only
# dropped cards belonging to SOMEONE ELSE -- so cards belonging to NOBODY
# were offered to everybody, and ~12% of Klee's reward screens were
# Ironclad/Silent stand-ins. tokens.yaml stays untagged on purpose:
# generated tokens are genuinely shared and are excluded from draft pools
# by rarity, not by ownership.
REF_CARD_SHEETS = {"ironclad_starter.yaml": "ref_ironclad",
                   "ironclad_package.yaml": "ref_ironclad",
                   "silent.yaml": "ref_silent"}


def _load_yaml_dir(sub: str, owners: dict[str, str] | None = None
                   ) -> list[dict]:
    docs = []
    for path in sorted((CONTENT_DIR / sub).glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        rows = data if isinstance(data, list) else [data]
        owner = (owners or {}).get(path.name)
        if owner:
            for d in rows:
                # DRAFTABLE RARITIES ONLY. Basics/tokens/statuses stay
                # deliberately ownerless: rewards.character_pool already
                # excludes them by rarity, so tagging buys nothing there --
                # while `character` is ALSO Furina's Spotlight key
                # (combat.py:92, effects.py:127/459/578). Engine test states
                # use strike/defend as filler, and tagging those would make
                # them valid Spotlight targets, changing a shared path for a
                # draft-layer fix. test_fontaine.test_character_field_
                # derivation locks that invariant.
                if d.get("rarity") in C.RARITY_ODDS:
                    d.setdefault("character", owner)
        docs.extend(rows)
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


def _external_cards() -> list[dict]:
    """Rows from the gitignored game_ref/ reference sheets, if present.

    Deliberately NOT the docs/ path's post-processing: no nation inference
    (a base-game pool has no Teyvat nation), and `character` is FORCED
    rather than `setdefault`-ed. That force is load-bearing, not cosmetic:
    rewards.character_pool drops cards tagged with another character
    (rewards.py:48), so without it every Klee reward screen could offer a
    Bash -- and every Ironclad screen a Jumpy Dumpty.
    """
    raw: list[dict] = []
    for sheet, char in EXTERNAL_CARD_SHEETS.items():
        path = GAME_REF_DIR / sheet
        if not path.exists():
            continue          # fresh clone: the reference simply is not here
        docs = yaml.safe_load(path.read_text()) or []
        for d in docs:
            d["character"] = char
        pool_ids = {d["id"] for d in docs}
        for layer_name in EXTERNAL_CARD_LAYERS.get(sheet, ()):
            layer_path = GAME_REF_DIR / layer_name
            if not layer_path.exists():
                raise ValueError(
                    f"{sheet}: missing required local layer {layer_name}; "
                    "rebuild/restore game_ref before loading real_ironclad")
            layer = yaml.safe_load(layer_path.read_text()) or []
            layer_ids = {d["id"] for d in layer}
            stale = sorted(layer_ids - pool_ids)
            if stale:
                raise ValueError(
                    f"{sheet}: stale merged pool is missing {layer_name} "
                    f"cards {stale}; run build_ironclad_sheet.py")
        # A partial external upgrade population biases both combat (Armaments,
        # Aggression) and run decisions (smithing versus removal). Treat the
        # external reference as one atomic artifact: either every row resolves
        # through the shared `<id>+` path, or real_ironclad does not load.
        missing_upgrades = sorted(
            d["id"] for d in docs if not upgrades.has_upgrade(d["id"])
        )
        if missing_upgrades:
            raise ValueError(
                f"{sheet}: incomplete external upgrade coverage for "
                f"{missing_upgrades}; rebuild game_ref with "
                "extract_base_game_pool.py --emit-sheet before loading "
                "real_ironclad")
        raw.extend(docs)
    return raw


@lru_cache(maxsize=1)
def _card_index() -> dict[str, Card]:
    raw = _load_yaml_dir("cards", REF_CARD_SHEETS)
    for sheet in DOCS_CARD_SHEETS:
        path = DOCS_DIR / sheet
        if path.exists():
            docs = yaml.safe_load(path.read_text())
            # R20 (2026-07-20): *-upgrades.yaml sheets are the ONE upgrade
            # convention. Inline `upgrade:` fields are IGNORED by Tier 0,
            # and silently ignoring them risks an inline-only upgrade that
            # never applies -- so the tolerance is loud, not silent.
            # UserWarning on purpose: DeprecationWarning is filtered out
            # of non-__main__ code by default, which would be silence.
            inline = [d["id"] for d in docs if "upgrade" in d]
            if inline:
                warnings.warn(
                    f"{sheet}: DEPRECATED inline `upgrade:` fields on "
                    f"{inline} (R20, 2026-07-20). Upgrades live in the "
                    "*-upgrades.yaml sheets; these fields are IGNORED "
                    "and must be reverted to the upgrade sheet.")
            # Nation comes from the sheet name ("mondstadt-companions.yaml"),
            # not a per-card field: it is a property of the pool a card ships
            # in, and repeating it on every row is just drift waiting to
            # happen. This is what makes the v1.8 banner roll per-nation
            # without touching the sheets when Liyue lands.
            if sheet.endswith("-companions.yaml"):
                nation = sheet.split("-", 1)[0]
                for d in docs:
                    d.setdefault("nation", nation)
                    # character derives from the id prefix ("fischl_oz" ->
                    # fischl): same drift argument as nation-from-filename.
                    # Explicit field wins (Guest Star rows name their cameo
                    # because their ids are prefixed "guest_").
                    d.setdefault("character", d["id"].split("_", 1)[0])
            elif sheet.endswith("-cards.yaml"):
                # Personal sheets: every row belongs to the character in the
                # filename. This is what makes self-Spotlight legible.
                char = sheet[:-len("-cards.yaml")]
                for d in docs:
                    d.setdefault("character", char)
            raw.extend(docs)
    raw.extend(_external_cards())
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


def guest_star_generation_pool(rarity: str) -> list[Card]:
    """Guest Star generation pool (kickoff §9, guardrails c+d): shared
    companions plus the purpose-built Guest Star set, at EXACTLY the
    generator's rarity. Playable characters' personal cards are absent by
    construction (neither companions nor guest_star rows); 5-star shared
    Rares are unreachable from sub-Rare generators because their rarity
    is 'rare' (the equal-rarity clause is the banner's bodyguard)."""
    pool = [c for c in _card_index().values()
            if (c.is_companion or c.guest_star)
            and c.rarity == rarity and not c.kit_card]
    if not pool:
        raise ValueError(f"empty guest-star pool at rarity {rarity!r}")
    return sorted(pool, key=lambda c: c.id)


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
    index = {d["id"]: d for d in _load_yaml_dir("characters")}
    # Reference characters live beside their (gitignored) card sheet -- see
    # GAME_REF_DIR. glob() on a missing directory yields nothing, so no
    # exists() guard is needed; the `char_` prefix keeps this from ever
    # picking up ironclad.json's siblings.
    for path in sorted(GAME_REF_DIR.glob("char_*.yaml")):
        d = yaml.safe_load(path.read_text())
        index[d["id"]] = d
    return index


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
    hooks = list(spec.get("relic_hooks", []))
    if deck != "starter":
        card_ids += spec["packages"][deck]
        # R8: probe-only relic hooks (harness instrumentation, e.g. the
        # sustain_probe's exempt heal trickle). Never on 'starter', never
        # in Tier 0.5 runs (build_player_from_ids does not read this).
        hooks += spec.get("package_relic_hooks", {}).get(deck, [])
    return Player(hp=spec["hp"], max_hp=spec["hp"],
                  draw_pile=[get_card(cid) for cid in card_ids],
                  element=spec.get("element", "none"),
                  cadence=spec.get("cadence", "skill"),
                  burst_max=spec.get("burst_max", 0),
                  relic_hooks=hooks,
                  kit_cards=_kit_cards(spec),
                  character_id=spec["id"],
                  fanfare_cap=(int(C.FANFARE_CAP_FRACTION * spec["hp"])
                               if spec.get("fanfare") else 0))


def build_player_from_ids(character_id: str, card_ids: list[str],
                          relic_effects: list[dict] | None = None,
                          potions: list[str] | None = None,
                          potion_slots: int = C.POTION_SLOTS,
                          node_kind: str = "") -> Player:
    """Tier 0.5: build a player around an arbitrary (drafted) deck list.

    ``relic_effects`` is the combat-side relic engine's seam (engine/relics.py):
    a list of dicts keyed by ``hook``. It defaults to None -> [] so the battery
    path (build_player, which never passes it) stays byte-identical and every
    relic code path remains a dead branch there. The run layer (tier05/model)
    computes the effective per-fight list and passes it in.

    ``potions`` is the combat-side potion engine's seam (engine/potions.py): a
    list of held potion-id strings, likewise defaulting to None -> [] so the
    battery stays byte-identical and every potion code path is a dead branch.
    ``potion_slots`` (Potion Belt raises it) and ``node_kind`` (elite/boss
    context for the offensive use-policy) are inert on the battery."""
    spec = _character_index()[character_id]
    return Player(hp=spec["hp"], max_hp=spec["hp"],
                  draw_pile=[get_card(cid) for cid in card_ids],
                  element=spec.get("element", "none"),
                  cadence=spec.get("cadence", "skill"),
                  burst_max=spec.get("burst_max", 0),
                  relic_hooks=list(spec.get("relic_hooks", [])),
                  relic_effects=list(relic_effects or []),
                  potions=list(potions or []),
                  potion_slots=potion_slots,
                  node_kind=node_kind,
                  kit_cards=_kit_cards(spec),
                  character_id=spec["id"],
                  fanfare_cap=(int(C.FANFARE_CAP_FRACTION * spec["hp"])
                               if spec.get("fanfare") else 0))


def starting_deck(character_id: str, rng=None) -> list[str]:
    """Return the printed starter, optionally resolving its run-start rolls.

    Tier 0's frozen starter scorecards call this without an RNG and retain the
    canonical basic deck. Tier 0.5 passes a dedicated per-run stream so Klee's
    Mondstadt Companion pair is deterministic without perturbing encounters,
    rewards, or any previously calibrated run randomness.
    """
    spec = _character_index()[character_id]
    deck = list(spec["starting_deck"])
    if rng is None:
        return deck
    for slot in spec.get("randomized_starter", {}).values():
        replaced = slot["replace"]
        if replaced not in deck:
            raise ValueError(
                f"{character_id}: randomized starter cannot replace "
                f"missing card {replaced!r}")
        choices = list(slot["choices"])
        if not choices:
            raise ValueError(
                f"{character_id}: randomized starter has no choices")
        deck[deck.index(replaced)] = rng.choice(choices)
    return deck


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


def character_nation(character_id: str) -> str | None:
    """Home nation for reward weighting (§4.1). None for the refs, which
    never reach the companion slot anyway."""
    return _character_index().get(character_id, {}).get("nation")


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
