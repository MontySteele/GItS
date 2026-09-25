"""THE CO-OP SET in a one-seat engine (review/records/coop-set-2026-09-25.md).

Nine multiplayer-only cards, three per overhaul arm, speak about ANOTHER
player: "Choose another player", "each other player", "whenever another player
plays an Attack". Tier 0 seats ONE player (`CombatState.player`), so every one
of those clauses has nobody to land on, and this module is where that is said
once rather than at nine call sites.

WHAT THE SIM DOES WITH THEM, and why it is honest rather than a gap:

  * It never DEALS them. They are `multiplayer: true` rows, outside each arm's
    pool list (`C.KLEE_OVERHAUL_POOL_IDS` and its twins); their mirrors
    (`C.*_MULTIPLAYER_IDS`) exist for `tools/lint_arm_pool_parity.py` and are
    read by no pool, draft, reward or run template -- the base game's own
    `CardPoolModel.GetUnlockedCards` drops them from a one-player run the same
    way.
  * It still LOADS them, through the same vocabulary check every row passes,
    so a typo in one is a load error here as it is a build error in C#.
  * If one is resolved anyway (a test, a hand-built state), a clause aimed at
    another player does NOTHING and says so (`coop_no_other_player`) -- the
    base game refuses an ally-aimed play outright with nobody else alive
    (`UnplayableReason.NoLivingAllies`), and a power that watches the other
    players never hears from one. What a card does for its OWN player is
    resolved normally: Pass the Match still draws, Coordinated Strike still
    hits, and the three Powers are applied (and never fire).

The co-op rules themselves are C#-only and are tested there
(`klee-mod/KleeTests/Prototype/CoopSetTests.cs`).
"""

from __future__ import annotations

from tier0.engine.state import Card, CombatState

#: The `target:` spelling for "another player" (`TargetType.AnyAlly`).
ALLY = "ally"

#: Plan clauses about another player. Plan-only: a Plan is written on the
#: Bake-Kurage, so neither has a now-line spelling.
ALLY_DRAW = "ally_draw"
OTHERS_ATTACK_DAMAGE_THIS_TURN = "others_attack_damage_this_turn"
PLAN_OPS = frozenset((ALLY_DRAW, OTHERS_ATTACK_DAMAGE_THIS_TURN))


def other_players(state: CombatState) -> list:
    """"Each other player". Tier 0 seats one, so there are none."""
    return []


def no_other_player(state: CombatState, op: str,
                    card: Card | None = None) -> None:
    """A clause aimed at another player, in a fight that has no other player:
    nothing happens, and the log says why."""
    state.emit("coop_no_other_player", op=op,
               card=card.id if card is not None else None)
