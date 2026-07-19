"""Combat state: player, enemies, piles. No rules logic here — just data
and the pile-manipulation primitives that everything else builds on.

Determinism contract: ALL randomness flows through CombatState.rng
(a random.Random seeded by the harness). Nothing may import the global
`random` module functions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Optional

from tier0 import constants as C


@dataclass
class Card:
    id: str
    name: str
    cost: Any                     # int or "X"
    type: str                     # attack | skill | power
    rarity: str = "common"        # basic | common | uncommon | rare
    element: str = "none"
    effects: list[dict] = field(default_factory=list)
    exhaust: bool = False
    solve: list[str] = field(default_factory=list)
    archetypes: list[str] = field(default_factory=list)
    role: str = "glue"
    tags: list[str] = field(default_factory=list)
    companion: Optional[dict] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Card":
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"card {d.get('id')!r}: unknown fields {sorted(unknown)}")
        return cls(**d)


@dataclass
class Bomb:
    """Delayed damage charge on an enemy (Klee signature, spec §4.2)."""
    damage: int
    element: str = "pyro"


@dataclass
class Fighter:
    hp: int
    max_hp: int
    block: int = 0
    powers: dict[str, int] = field(default_factory=dict)   # name -> stacks

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class Player(Fighter):
    energy: int = 0
    sparks: int = 0
    draw_pile: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)
    exhaust_pile: list[Card] = field(default_factory=list)
    relic_hooks: list[str] = field(default_factory=list)   # e.g. ["spark_on_detonation"]


@dataclass
class Enemy(Fighter):
    name: str = "enemy"
    intents: list[dict] = field(default_factory=list)      # rotating script
    intent_index: int = 0
    aura: Optional[str] = None
    aura_turns_left: int = 0
    bombs: list[Bomb] = field(default_factory=list)
    is_boss: bool = False
    sleep_turns: int = 0        # skips its turn while > 0 (BURST CHECK)
    frozen: bool = False        # skips next intent

    def current_intent(self) -> dict:
        return self.intents[self.intent_index % len(self.intents)]

    def advance_intent(self) -> None:
        self.intent_index += 1


@dataclass
class CombatState:
    player: Player
    enemies: list[Enemy]
    rng: random.Random
    turn: int = 0
    cards_played_this_turn: int = 0
    log: list[dict] = field(default_factory=list)          # event stream for metrics

    def emit(self, event: str, **data: Any) -> None:
        self.log.append({"turn": self.turn, "event": event, **data})

    @property
    def living_enemies(self) -> list[Enemy]:
        return [e for e in self.enemies if e.alive]

    @property
    def over(self) -> bool:
        return not self.player.alive or not self.living_enemies

    # --- pile primitives ---

    def shuffle_discard_into_draw(self) -> None:
        self.rng.shuffle(self.player.discard_pile)
        self.player.draw_pile = self.player.discard_pile + self.player.draw_pile
        self.player.discard_pile = []

    def draw(self, n: int) -> None:
        p = self.player
        for _ in range(n):
            if not p.draw_pile:
                if not p.discard_pile:
                    return
                self.shuffle_discard_into_draw()
            if len(p.hand) >= C.MAX_HAND_SIZE:
                return
            card = p.draw_pile.pop(0)
            p.hand.append(card)
            self.emit("draw", card=card.id)
