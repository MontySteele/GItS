"""Bridge JSON -> tier0 engine objects, so the REAL pilot can be asked.

Why an adapter and not a re-implementation
------------------------------------------
The brief says "port the tier0.5 pilot heuristics to the bridge protocol". The
cheapest reading of that is to retype the scoring formulas against the wire
schema. Retyping ~600 lines of `tier0/pilot/policy.py` would guarantee the
outcome M2 pre-registers as the thing to rule out first: an agreement rate
that is low because the PORT is wrong rather than because the POLICY is dumb.

So policy_v0 does not retype anything. It reconstructs enough tier0 state from
the wire to call `tier0.pilot.policy.make_pilot`, `tier05.draft.assigned_policy`,
`tier05.route` and `tier05.model.rest_action` -- the actual code the sim runs.
Nothing in tier0/ or tier05/ is modified, imported-and-monkeypatched, or read
for anything but its public entry points. That is the whole seam.

The price is this module: a translation layer whose fidelity is a fact about
the measurement, so it is enumerated rather than assumed.

WHAT CROSSES THE WIRE FAITHFULLY
  - Card identity. GItS ids are `KLEEMOD-<SHEET_ID>`; the sheet is the sim's
    source of truth, so a hand of GItS cards resolves to the exact `Card`
    objects tier0 scores, effects and all.
  - HP, block, energy, gold, potions, deck contents, map topology, enemy
    HP/block, intent kind and amount.

WHAT IS APPROXIMATED, AND HOW IT BIASES THE COUNTERFACTUAL
  - Base-game cards (rewards, colorless, statuses) have no sheet row. They get
    a text-derived stub: damage/block numbers scraped from the rules text,
    everything else empty. The pilot will systematically UNDERVALUE them,
    because a stub has no scaling, reaction or tempo terms. Every such card is
    flagged `approximate` in the decision log; the divergence report must not
    read "policy skipped the base-game rare" as judgment.
  - Player powers. Only the statuses tier0 names are carried (strength,
    dexterity, weak, vulnerable, frail, artifact, plus Furina's encore /
    fanfare / salon counters when the bridge exposes them). Anything else is
    dropped, so buff-sensitive scoring is conservative.
  - Enemy auras. The reaction term needs an aura per enemy; the base game has
    no aura concept and GItS applies its own. Read when the bridge reports it
    in enemy status, absent otherwise -- which zeroes `_reaction_value`.
  - Intent ramps and multi-phase bosses. The wire gives the CURRENT intent
    only, so `ramp` and `ramp_per_use` are structurally invisible. Incoming
    damage is therefore this-turn-accurate and future-turn-blind, which is
    what the pilot uses it for anyway.

WHAT IS NOT CARRIED AT ALL
  - Relic hooks, draw/discard pile ORDER, exhaust pile contents, orbs, and any
    in-combat overlay state. The pilot reads none of these except through
    relics, which the sim models by hook name and the bridge reports by prose.
"""

from __future__ import annotations

import copy
import random
import re
from typing import Any

from tier0.engine.state import Card, CombatState, Enemy, Player

from tier0.content import loader
from tier0.engine import combat

MOD_PREFIX = "KLEEMOD-"

# Bridge status name -> tier0 power key. Deliberately short: an unmapped
# status is dropped loudly (see `unmapped_statuses`) rather than guessed at.
STATUS_MAP = {
    "strength": "strength",
    "dexterity": "dexterity",
    "weak": "weak",
    "vulnerable": "vulnerable",
    "frail": "frail",
    "artifact": "artifact",
    "regen": "regen",
    "plating": "plating",
    "encore": "encore",
    "fanfare": "fanfare",
    "salon": "salon",
    # The strict Rare Power's own stack (the Klee Sparks arm, PICK 5). Named by
    # its TITLE, because that is what the bridge puts on the wire, and mapped to
    # the sim's power key so `combat.spark_price` sees the same rule the live
    # board is running. Without the row it would land in `unmapped_statuses` --
    # reported, never guessed -- and every Attack in hand would price at 0 on the
    # observed board while the game charged 3.
    "true_spark_knight": "spark_attack_cost",
}

# EB-185. THE STATUSES THE SIM HOLDS AS A NAMED PLAYER FIELD, NOT AS A POWER.
#
# Sparks ride the wire as a POWER (`SPARK_POWER`, printed `Spark`, a Buff with
# a counter) because that is how the live game holds them, while tier0 keeps
# them on `Player.sparks` -- a field, apart from the powers dict, because the
# threshold rule reads it directly. Neither table above could carry the
# crossing: `STATUS_MAP` lands in `powers` and `WIRE_RESOURCES` reads the
# `resources` blob, which has no Spark row in it at all.
#
# The cost of the gap was the whole of a round: every observed reading of a
# Klee board in slice 1 scored a bank of ZERO, so three of the six boards
# collapsed to four playable lines and `closeness --observed` was reading a
# turn nobody was handed. Explicit table for `WIRE_RESOURCES`' reason -- an
# unmapped status is still REPORTED, so a meter the falsifier could not see
# never passes for one it read.
STATUS_FIELDS = {"spark": "sparks"}

_DMG_RE = re.compile(r"[Dd]eal\s+(\d+)\s+damage")
_INTENT_RE = re.compile(r"^(\d+)(?:\s*[x\u00d7]\s*(\d+))?$")
_INTENT_DESC_RE = re.compile(r"[Aa]ttack for (\d+)")
_BLK_RE = re.compile(r"[Gg]ain\s+(\d+)\s+[Bb]lock")


def sheet_id(bridge_id: str) -> str:
    """`KLEEMOD-ARIA_OF_RECOMPENSE` -> `aria_of_recompense`."""
    core = bridge_id[len(MOD_PREFIX):] if bridge_id.startswith(MOD_PREFIX) else bridge_id
    return core.lower()


def resolve_card(entry: dict[str, Any],
                 prototype_index: dict[str, Card] | None = None
                 ) -> tuple[Card, bool]:
    """A wire card as the sim would see it. Returns (card, approximate).

    `prototype_index` is the DEV ROUTE (R213 B), passed only when the caller
    declared it. A quarantined row is absent from `loader._card_index()` by
    construction, so without it a live prototype card falls through to the
    text approximation below and the falsifier refuses the reading as
    approximate -- the wrong answer to give about a card the sim holds an
    EXACT row for. The index is built by the caller, once, rather than by
    re-reading the surface per card.
    """
    bid = str(entry.get("id") or "")
    if bid.startswith(MOD_PREFIX):
        sid = sheet_id(bid)
        if prototype_index:
            hit = prototype_index.get(sid)
            if hit is not None:
                # Fresh per hand slot: two slots naming one row must not be
                # the same object, or a line that plays one consumes both.
                return copy.deepcopy(hit), False
        try:
            return loader.peek_card(sid), False
        except (KeyError, ValueError):
            pass
    return _text_card(entry), True


def _text_card(entry: dict[str, Any]) -> Card:
    desc = str(entry.get("description") or "")
    effects: list[dict] = []
    m = _DMG_RE.search(desc)
    if m:
        effects.append({"op": "damage", "amount": int(m.group(1))})
    m = _BLK_RE.search(desc)
    if m:
        effects.append({"op": "block", "amount": int(m.group(1))})
    cost = entry.get("cost")
    if not isinstance(cost, int):
        cost = 1
    return Card(
        id=str(entry.get("id") or "unknown"),
        name=str(entry.get("name") or entry.get("id") or "unknown"),
        cost=cost,
        type=str(entry.get("type") or "skill").lower(),
        rarity=str(entry.get("rarity") or "common").lower(),
        effects=effects,
        archetypes=["generic"],
        role="glue",
    )


def _statuses(blob: Any) -> tuple[dict[str, int], dict[str, int], list[str]]:
    """`(powers, player fields, unmapped)` -- see `STATUS_FIELDS` for why the
    middle one exists and is not folded into the first."""
    powers: dict[str, int] = {}
    fields: dict[str, int] = {}
    unmapped: list[str] = []
    for st in blob or []:
        if not isinstance(st, dict):
            continue
        raw = str(st.get("name") or "").strip().lower().replace(" ", "_")
        amount = st.get("amount")
        if amount is None:
            amount = st.get("stacks", 1)
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            amount = 1
        key = STATUS_MAP.get(raw)
        field = STATUS_FIELDS.get(raw)
        if key:
            powers[key] = amount
        elif field:
            fields[field] = amount
        else:
            unmapped.append(raw)
    return powers, fields, unmapped


def _intent(blob: Any) -> list[dict]:
    """The current intent as a one-entry tier0 intent script.

    The wire carries `intents` as a LIST of typed hints -- `{"type":
    "DebuffStrong", "title": "Strategic", "description": ...}` for a debuff,
    with numeric fields only on the damaging ones. A non-damaging intent
    becomes a zero-block beat: the pilot reads intents solely through
    `_incoming_damage`, and an intent that deals none contributes none.
    """
    if isinstance(blob, list):
        blob = blob[0] if blob else None
    if not isinstance(blob, dict):
        return [{"kind": "block", "amount": 0}]
    if str(blob.get("type", "")).lower() != "attack":
        return [{"kind": "block", "amount": 0}]

    # The number is in `label`, as the UI string the game prints under the
    # icon: "7", or "7 x 3" for a multi-hit. There is no numeric field at all.
    # Missing this reads every attack as zero incoming damage, which silently
    # disables the pilot's block-panic rung -- the single most consequential
    # thing this adapter can get wrong.
    label = str(blob.get("label") or "").strip()
    m = _INTENT_RE.match(label)
    if not m:
        m = _INTENT_DESC_RE.search(str(blob.get("description") or ""))
    if not m:
        return [{"kind": "block", "amount": 0}]
    dmg = int(m.group(1))
    times = 1
    if m.lastindex and m.lastindex >= 2 and m.group(2):
        times = int(m.group(2))
    return [{"kind": "attack", "amount": dmg, "times": times}]


def _enemy_aura(entry: dict[str, Any]) -> str | None:
    for st in entry.get("status") or []:
        if not isinstance(st, dict):
            continue
        name = str(st.get("name") or "").strip().lower()
        # The wire says "Cryo Aura", not "cryo". Matching the element word
        # rather than the whole label is what makes the pilot's reaction term
        # non-zero at all.
        for element in ("pyro", "hydro", "electro", "cryo",
                        "anemo", "geo", "dendro"):
            if name.startswith(element):
                return element
    return None


def build_combat_state(state: dict[str, Any], *, prototype: bool = False
                       ) -> tuple[CombatState, dict[str, Any]]:
    """Reconstruct a tier0 CombatState. Returns (state, provenance notes).

    `prototype` opens the quarantined surface to the resolver for THIS call
    only (R213 B); see `resolve_card`.
    """
    p = state.get("player") or {}
    proto_index = ({c.id: c for c in loader.prototype_cards()}
                   if prototype else None)
    powers, fields, unmapped = _statuses(p.get("status"))

    hand_entries = list(p.get("hand") or [])
    hand: list[Card] = []
    approx: list[str] = []
    # THE SPARK PRICE, AS THE LIVE GAME REPORTED IT (the Klee Sparks arm).
    # `cost` on the wire is the ENERGY cost and is 0 for every Spark-priced
    # card, so without these two keys an observed board shows a hand of free
    # cards; and `can_play` folds every refusal into one boolean, so it cannot
    # tell a short bank from a missing target. Kept in wire order, paired with
    # the resolved card, so the cross-check below can name the card that
    # disagrees.
    wire_prices: list[tuple[str, int, bool]] = []
    for e in hand_entries:
        card, is_approx = resolve_card(e, proto_index)
        hand.append(card)
        if is_approx:
            approx.append(card.name)
        if e.get("spark_price") is not None:
            wire_prices.append((card.id,
                                int(e["spark_price"]),
                                bool(e.get("spark_affordable", True))))

    player = Player(
        hp=int(p.get("hp", 0)),
        max_hp=int(p.get("max_hp", 1)),
        block=int(p.get("block", 0)),
        powers=powers,
        energy=int(p.get("energy", 0)),
        hand=hand,
        character_id="furina" if "FURINA" in str(state.get("player", {}).get("character", "")).upper()
        else str(p.get("character", "")).lower(),
        potions=[str(x.get("name", "")) for x in (p.get("potions") or []) if isinstance(x, dict)],
        node_kind={"monster": "normal", "elite": "elite", "boss": "boss"}.get(
            str(state.get("state_type")), ""),
    )

    enemies: list[Enemy] = []
    for e in enemy_blobs(state):
        epowers, _, _ = _statuses(e.get("status"))
        # DOUBLE-COUNTING GUARD. The intent label the wire prints is the
        # FINAL number the player will take -- the game has already folded in
        # the attacker's Strength and any Weak on it. tier0's
        # `_incoming_damage` folds them in again from `powers`, so carrying
        # them across turned a Jaxfruit with Strength 4 telegraphing 10 into
        # a 45-damage panic and would have made the pilot block through every
        # turn it should have been attacking. Powers that modify what an enemy
        # DEALS are dropped; powers that modify what it RECEIVES are kept.
        # The guard has to be total, not selective. tier0's damage pipeline
        # reads several enemy powers on the way out (Vulnerable among them),
        # and every one of those readings is a second application of something
        # the label already contains. The pilot consults enemy powers for
        # nothing else -- `_expected_damage` only looks at them through
        # `bonus_per_target_power`, which no GItS starter uses -- so the whole
        # dict is dropped and the aura, which lives in its own field, carries
        # the only enemy state the scoring actually needs.
        epowers = {}
        enemies.append(Enemy(
            hp=int(e.get("hp", 0)),
            max_hp=int(e.get("max_hp", e.get("hp", 1)) or 1),
            block=int(e.get("block", 0)),
            powers=epowers,
            name=str(e.get("name") or e.get("entity_id") or "enemy"),
            intents=_intent(e.get("intents") or e.get("intent")),
            aura=_enemy_aura(e),
            is_boss=str(state.get("state_type")) == "boss",
        ))

    # EB-185. The named-field statuses, written after construction and REFUSED
    # rather than guessed when the sim has no such field -- a `setattr` onto a
    # Player that does not carry the attribute would put the bank somewhere
    # nothing reads and report success.
    for field_name, amount in fields.items():
        if not hasattr(player, field_name):
            raise AttributeError(
                f"the wire carries a status mapped to Player.{field_name}, "
                f"which the sim's Player does not have")
        setattr(player, field_name, int(amount))

    cs = CombatState(
        player=player,
        enemies=enemies,
        rng=random.Random(0),      # never consumed: scoring is pure
        turn=int((state.get("battle") or {}).get("round", 1) or 1),
    )
    # THE CROSS-CHECK, and it is the whole reason the wire keys are worth
    # carrying. `SparkCost.PriceOf` (the number the badge draws and the gate
    # charges) and `combat.spark_price` (the number the sim charges) are two
    # implementations of one rule in two languages; a divergence between them is
    # a defect in one of them, and it is invisible unless something asks. A
    # disagreement is REPORTED, never repaired here -- the same posture
    # `unmapped_statuses` takes, and for the same reason: a reading the
    # falsifier could not verify must not pass for one it did.
    disagreements: list[str] = []
    for card_id, wire_price, _ in wire_prices:
        for card in cs.player.hand:
            if card.id != card_id:
                continue
            sim_price = combat.spark_price(cs, card)
            if sim_price != wire_price:
                disagreements.append(
                    f"{card_id}: wire {wire_price}, sim {sim_price}")
            break

    notes = {
        "approximate_cards": approx,
        "player_fields": dict(sorted(fields.items())),
        "unmapped_statuses": sorted(set(unmapped)),
        "enemy_count": len(enemies),
        "auras_seen": sorted({e.aura for e in enemies if e.aura}),
        "spark_prices": {cid: price for cid, price, _ in wire_prices},
        "spark_unaffordable": sorted(
            cid for cid, _, ok in wire_prices if not ok),
        "spark_price_disagreements": sorted(set(disagreements)),
    }
    return cs, notes


def enemy_blobs(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Enemies live under `battle`, not at the top level.

    Cost one combat's worth of confusion to learn, so it is a named function
    with a docstring rather than a `.get` chain repeated in three places.
    """
    battle = state.get("battle")
    if isinstance(battle, dict) and isinstance(battle.get("enemies"), list):
        return [e for e in battle["enemies"] if isinstance(e, dict)]
    return [e for e in (state.get("enemies") or []) if isinstance(e, dict)]


def enemy_id(e: dict[str, Any]) -> str:
    return str(e.get("entity_id") or e.get("id") or "")


def entity_ids(state: dict[str, Any]) -> list[str]:
    return [enemy_id(e) for e in enemy_blobs(state) if enemy_id(e)]


def deck_cards(state: dict[str, Any]) -> list[Card]:
    """Every card the run currently owns, as tier0 Cards.

    In combat the deck is split across piles; out of combat the bridge reports
    `player.deck`. Both shapes are handled because the draft policy is asked
    at card_reward (out of combat) and at shops (also out of combat), but the
    counterfactual is worth computing anywhere.
    """
    p = state.get("player") or {}
    entries: list[dict] = []
    if isinstance(p.get("deck"), list):
        entries = [e for e in p["deck"] if isinstance(e, dict)]
    else:
        for pile in ("hand", "draw_pile", "discard_pile", "exhaust_pile"):
            entries += [e for e in (p.get(pile) or []) if isinstance(e, dict)]
    if entries:
        out = []
        for e in entries:
            card, _ = resolve_card(e)
            out.append(card)
        return out

    # Out of combat the wire carries no deck at all. Fall back to the last
    # snapshot the deck watcher took during a fight -- see deckwatch.py for
    # what that costs in staleness.
    from understudy import deckwatch
    out = []
    for cid in deckwatch.current():
        card, _ = resolve_card({"id": cid})
        out.append(card)
    return out
