"""One fight's numbers, accumulated from state deltas.

Cut out of `soak.py` by `EB-180`. `FightTelemetry`, `_telegraphed`, `_meters`
and `_enemy_pool` are that file's, moved whole and re-exported from it, so
`soak._meters(state)` and `soak.FightTelemetry(...)` still resolve.

Nothing here touches the wire, the game directory or a dial a test swaps --
it reads a state dict and returns numbers -- so it needs no call-time read of
`soak`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from understudy.soak_shape import SCHEMA_VERSION

# ------------------------------------------------------------ telemetry ----
#
# THE SCHEMA IS DOCUMENTED IN `understudy/README.md` AND IS A SHARED SURFACE
# TO BE: Track B wants the same per-fight numbers out of the sim. Renaming a
# key here is a cross-session change once Track B reads it.

@dataclass
class FightTelemetry:
    """One fight's numbers, accumulated from state deltas.

    ATTRIBUTION RULE, stated because it is an approximation and a reader who
    does not know that would over-read the damage table:

      * damage BY SOURCE is the total enemy (hp + block) drop observed across
        the state read immediately after an action, attributed to the card or
        potion that action named. Anything that resolves later in the same
        frame batch lands on the play that triggered it, which is usually what
        you want (a summon's hit is the summon card's) and is occasionally
        wrong (a bomb detonating on a later play).
      * damage TAKEN is the player hp drop observed across a ROUND boundary,
        attributed to the enemy turn as a whole rather than per enemy -- the
        wire does not narrate which enemy landed which hit.
      * INCOMING per turn is the sum of the telegraphed attack intents read at
        the start of the player's turn, before any block.

    All three are floors on truth, not estimates of it: they under-attribute
    rather than invent.
    """
    act: int
    floor: int
    kind: str
    # R99/4a. The DECLARED deck intent for the run this fight belongs to: the
    # committed archetype on the bot feed, whatever the person wrote in
    # `intent.txt` on the human feed, `""` when nobody declared anything. It is
    # a declaration, never an inference -- nothing reads the deck and guesses.
    intent: str = ""
    enemies: list = field(default_factory=list)
    hp_start: int = 0
    max_hp: int = 0
    turns: int = 0
    hp_trajectory: list = field(default_factory=list)     # [(round, hp, block)]
    incoming_by_turn: list = field(default_factory=list)  # [(round, dmg, n_atk)]
    # TRACK B ADDITIONS (2026-08-04). Keys only ADDED -- nothing renamed, which
    # is what the shared-schema rule in understudy/README.md costs and permits.
    enemy_pool_by_turn: list = field(default_factory=list)  # [(round, pool)]
    meters_by_turn: list = field(default_factory=list)  # [(rnd, fanfare, salon,
    #                                                     salon_cap, encore)]
    block_at_turn_end: list = field(default_factory=list)   # [(round, block)]
    cards_played: list = field(default_factory=list)      # [(round, name)]
    # P1.5 ADDITION (2026-08-05), spec item 3. Every SELECTOR screen resolved
    # inside this fight: [round, screen_type, index, chosen name, offered names].
    #
    # WHY THE OFFERED LIST IS IN THE ROW. A choice is not reconstructible from
    # what was taken alone -- "Center Stage" means one thing against
    # [Center Stage, Guest Cast] and nothing at all against a list that did not
    # contain Guest Cast. This is the same denominator rule `hand` already
    # applies to a card play, for the same reason.
    #
    # `-1` in the index slot is a selector resolved without one (a confirm, a
    # skip); the verb is legible from `screen_type` plus the empty chosen name.
    selectors: list = field(default_factory=list)
    potions_used: list = field(default_factory=list)
    damage_by_source: dict = field(default_factory=dict)
    damage_taken: int = 0
    hp_end: int = 0
    outcome: str = "unknown"

    def as_record(self) -> dict:
        return {
            "record": "fight", "schema": SCHEMA_VERSION,
            # THE FEED LABEL IS PART OF THE RECORD, not part of the filename.
            # Guardrail 7 says every Track B curve is labelled with its feed;
            # a label that lives in a path is a label that is lost the first
            # time somebody concatenates two files.
            "feed": "bot", "source": "soak", "intent": self.intent,
            "seats": 1, "seat_index": 0,
            "act": self.act, "floor": self.floor,
            "kind": self.kind, "enemies": self.enemies,
            "hp_start": self.hp_start, "hp_end": self.hp_end,
            "max_hp": self.max_hp, "hp_lost": self.hp_start - self.hp_end,
            "turns": self.turns, "outcome": self.outcome,
            "hp_trajectory": self.hp_trajectory,
            "incoming_by_turn": self.incoming_by_turn,
            "enemy_pool_by_turn": self.enemy_pool_by_turn,
            "meters_by_turn": self.meters_by_turn,
            "block_at_turn_end": self.block_at_turn_end,
            "cards_played": self.cards_played,
            "n_cards_played": len(self.cards_played),
            "selectors": self.selectors,
            "potions_used": self.potions_used,
            "damage_by_source": {k: round(v, 1)
                                 for k, v in sorted(self.damage_by_source.items())},
            "damage_dealt": round(sum(self.damage_by_source.values()), 1),
            "damage_taken": self.damage_taken,
        }


_INTENT_LABEL = re.compile(r"^(\d+)(?:\s*[x×]\s*(\d+))?$")


def _telegraphed(state: dict[str, Any]) -> tuple[int, int]:
    """(total telegraphed damage, number of attacking enemies) this turn."""
    from understudy import adapter
    total = attackers = 0
    for e in adapter.enemy_blobs(state):
        if int(e.get("hp", 0)) <= 0:
            continue
        blob = e.get("intents") or e.get("intent")
        if isinstance(blob, list):
            blob = blob[0] if blob else None
        if not isinstance(blob, dict):
            continue
        if str(blob.get("type", "")).lower() != "attack":
            continue
        m = _INTENT_LABEL.match(str(blob.get("label") or "").strip())
        if not m:
            continue
        dmg = int(m.group(1)) * (int(m.group(2)) if m.lastindex and m.lastindex >= 2
                                 and m.group(2) else 1)
        total += dmg
        attackers += 1
    return total, attackers


_METER_IDS = {
    "FANFARE_METER_POWER": 0,
    "SALON_MEMBER_POWER": 1,
}

# UNSEEN, NOT EMPTY. -1 is what this file records for a meter the wire did not
# carry on the read it was taken from. A zero would be a measurement claiming
# the meter was empty in fights where it demonstrably was not.
#
# ENCORE WAS UNSEEN ON EVERY BOT FIGHT UNTIL P1.5, and the sentence that used
# to stand here -- "Encore is not on the wire and cannot be" -- was right about
# the wire and wrong about "cannot". `EncoreMeterPower` was retired as a
# display in animation sprint 2 (E1), so Encore left `creature.Powers`, which
# is the only place the bridge's state builder looked. The P1.5 fork adds
# `player.resources` (`vendor/STS2_MCP/gits/GitsResources.cs`), a read of
# BaseLib's own custom-resource registry, and Encore is in it by construction.
#
# -1 SURVIVES AS THE ANSWER FOR AN OLD BRIDGE. A run driven against a
# pre-P1.5 bridge has no `resources` key at all, and its logs must keep saying
# "unseen" rather than start saying "0".
METER_UNSEEN = -1
ENCORE_UNSEEN = METER_UNSEEN   # the P1-era name, kept for readers of old logs

# Wire ids of the custom RESOURCES, which are the canonical values -- the badge
# powers below are a display of them. Both are read: the resource when the
# bridge carries it, the badge as the fallback for an older one.
_ENCORE_RESOURCE_ID = "KLEEMOD_ENCORE"
_FANFARE_RESOURCE_ID = "KLEEMOD_FANFARE"

# The live cap is the printed base plus Casting Call's raises, and
# `SalonCapUpPower` is an ordinary PowerModel -- so the raise HAS been on the
# wire all along, in the status strip, next to the meter whose cap it moves.
# The P1 note said the cap "is not on the wire at all"; that was true of the
# CAP and false of its only addend.
_SALON_CAP_UP_ID = "SALON_CAP_UP_POWER"


def _meters(state: dict[str, Any]) -> list[int]:
    """[fanfare, salon, salon_cap, encore] for one turn opening.

    Read by ID rather than by title everywhere: a display name is loc data and
    moves with a wording pass, an id is the thing itself. A number this file
    cannot see is recorded as unseen, not guessed.
    """
    player = state.get("player") or {}
    out = [0, 0, SALON_PRINTED_CAP, METER_UNSEEN]

    for st in (player.get("status") or []):
        if not isinstance(st, dict):
            continue
        wire_id = str(st.get("id") or "").strip().upper()
        try:
            amount = int(st.get("amount"))
        except (TypeError, ValueError):
            continue
        slot = _METER_IDS.get(wire_id)
        if slot is not None:
            out[slot] = amount
        elif wire_id == _SALON_CAP_UP_ID:
            out[2] = SALON_PRINTED_CAP + amount

    # P1.5: the resource map, when the bridge carries one. It is authoritative
    # over the badge for Fanfare -- the badge is synced from the resource at
    # known hook sites, and the resource is the value those sites are syncing.
    resources = player.get("resources")
    if isinstance(resources, dict):
        for key, slot in ((_FANFARE_RESOURCE_ID, 0), (_ENCORE_RESOURCE_ID, 3)):
            if key in resources:
                try:
                    out[slot] = int(resources[key])
                except (TypeError, ValueError):
                    pass
        # A live combat with a resources map but no Encore in it is not an
        # unseen meter -- it is a player who has no Encore. Only the ABSENCE of
        # the map leaves the column unseen.
        if out[3] == METER_UNSEEN and _ENCORE_RESOURCE_ID not in resources:
            out[3] = 0
    return out


# The PRINTED salon cap (SalonConstants.MemberSlots). Not a balance constant
# here -- it is the label on a telemetry column, and the C# side owns the
# number. A run that raises the live cap is legible from its card plays.
SALON_PRINTED_CAP = 3


def _enemy_pool(state: dict[str, Any]) -> int:
    from understudy import adapter
    return sum(max(0, int(e.get("hp", 0))) + max(0, int(e.get("block", 0)))
               for e in adapter.enemy_blobs(state))
