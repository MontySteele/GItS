"""G-A5(a), sequencing half: the scripted Fanfare trajectory the live build
has to reproduce.

The arithmetic half of parity is machine-checked on both sides -- see
tier0/tests/test_furina_fanfare_parity.py and
klee-mod/KleeCode/Diagnostics/FurinaParityVectors.cs. What no automated check
on either side can reach is ORDER: that decay lands at the true top of the
player turn, before the block clear and before Salon upkeep; that a card's
"Fanfare +X" grant lands in its own printed effect order; that a doubled card
grants once per resolution. There is no C# test project, so the only
executable copy of the C# layer is the game itself.

So this prints the sim's answer, turn by turn, for a fully deterministic
scripted fight. G-A5(b)'s live capture plays the same cards in the same order
and the two are diffed by eye -- or by grepping the game log for the same
fields, which is why the format is terse and stable rather than pretty.

WHAT TO WATCH, in the order the failures are likely:

  1. `decay` on turn 1. There must be none. The sim skips decay while
     turn < 2 so the opening hand plays against what the player built, not
     against an immediate tax. The C# guard is TurnNumber <= 1.
  2. `decay` arriving AFTER a turn-start generator. If the number decays a
     meter that already includes this turn's Salon tick or draw income, the
     hook is too late -- decay must eat inventory, not income.
  3. A "Fanfare +X" card granting its floor out of its printed effect order.
     Watch a card that also reads Fanfare: the read must see whatever the
     order in front of it says, and the two sides must agree on which.
  4. Any `spend` line at all. Fanfare is read-only; there is no spend.

Usage: python -m tier05.exp_furina_parity_trace
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine.state import CombatState, Enemy, Player

SEED = 11                     # the sprint's registered seed

# A fixed script rather than a pilot policy: parity needs the same plays in the
# same order on both sides, and a policy would re-decide when the C# build's
# numbers differ -- which is precisely the case under test. Cards are named by
# id and played in this order, skipping any the hand does not hold that turn.
#
# Chosen to exercise every branch of the ported behaviour in as few turns as
# possible: the "Fanfare Cap +X" keyword (ceiling only), the "Fanfare +X"
# keyword on a rare Power (floor, cap and current together), an Encore SPEND
# (generation -- the one source that stays deterministic once the enemy is
# forbidden to hit, see the punching bag below), a threshold reader, and at
# least two turns of pure decay so the fade is visible in isolation.
SCRIPT: list[list[str]] = [
    ["an_invitation"],              # T1: generate. No decay this turn.
    ["lasting_impression"],         # T2: first decay, THEN Encore +4 and
                                    #     "Fanfare Cap +5" -- ceiling only
    ["breathless"],                 # T3: decay, THEN spend 4 Encore -> the
                                    #     meter has something to fade
    ["the_sea_is_my_stage"],        # T4: a RARE POWER -- "Fanfare +15"
    [],                             # T5: pure decay, now clamped by the floor
    [],                             # T6: still on the floor: fade must stop
]

# A small fixed deck rather than Furina's starter. The starter holds neither
# keyword, and shuffling ten cards makes "was it in hand" a property of the
# seed rather than of the design under test. Six cards against a five-card
# draw means everything is reachable by turn 2.
DECK: list[str] = [
    "an_invitation", "lasting_impression", "the_sea_is_my_stage",
    "breathless", "stage_presence", "soloists_solicitation",
]


def _scripted_pilot(script: list[list[str]]):
    """Play the named cards, in order, from whatever the hand actually holds.

    A card named for a turn but absent from the hand is SKIPPED and reported,
    rather than being conjured. Conjuring it would make the trace reproducible
    and wrong -- the live build draws the same deck with the same seed, so a
    card missing here is a card missing there, and the divergence is
    information.
    """
    missed: list[tuple[int, str]] = []

    def pilot(state: CombatState):
        turn = state.turn
        wanted = script[turn - 1] if 1 <= turn <= len(script) else []
        played = state.cards_played_this_turn
        if played >= len(wanted):
            return None
        target = wanted[played]
        for card in state.player.hand:
            if card.id.rstrip("+") == target:
                return card
        missed.append((turn, target))
        return None

    pilot.missed = missed          # type: ignore[attr-defined]
    return pilot


def _fanfare_events(log: list) -> list[dict]:
    kinds = {"gain_fanfare", "fanfare_decay", "fanfare_floor_granted",
             "fanfare_cap_raised", "fanfare_read", "play"}
    return [e for e in log if e.get("event") in kinds]


def main() -> int:
    player: Player = loader.build_player("furina")
    player.draw_pile = [loader.peek_card(cid) for cid in DECK]
    max_hp, cap = player.max_hp, player.fanfare_cap

    # A punching bag: enough HP to survive the whole script, and an intent that
    # never touches the player. Both matter. A fight that ends early truncates
    # the trajectory, and HP loss MINTS Fanfare -- an enemy that hits would add
    # a term the live capture would have to reproduce exactly, turning a
    # sequencing check into a damage-roll check.
    def dummy() -> Enemy:
        return Enemy(hp=9999, max_hp=9999, name="parity_dummy",
                     intents=[{"kind": "block", "amount": 0}])

    pilot = _scripted_pilot(SCRIPT)

    print("=" * 78)
    print(f"FURINA FANFARE PARITY TRACE — seed {SEED}, "
          f"decay {C.FANFARE_DECAY_FRACTION:.0%}, "
          f"absorbed +{C.FANFARE_PER_ENCORE_ABSORBED} / spent "
          f"+{C.FANFARE_PER_ENCORE_SPENT} / HP lost "
          f"+{C.FANFARE_PER_HP_LOST}")
    print(f"  cap = {C.FANFARE_CAP_FRACTION:.0%} of {max_hp} maxHP = {cap} "
          f"(a safety rail under decay, not a dial -- F-A5)")
    # The deck below cannot be forced in-game, so G-A5(b) is a QUALITATIVE
    # capture, not a diff: the four shapes printed here are what to look for.
    print("  Live capture (G-A5b) checks these four shapes, not exact numbers:")
    print("    1. turn 1 shows NO decay line;  2. the meter falls every later "
          "turn it is above its floor;")
    print("    3. a \"Fanfare +X\" card raises the floor and the fall then "
          "STOPS on it;")
    print("    4. no card ever spends Fanfare.")
    print("=" * 78)

    state = combat.run_fight(player, [dummy()], pilot, SEED)

    print(f"\n  {'turn':>4}  {'event':<22} {'amt':>4} {'fanfare':>8} "
          f"{'floor':>6} {'cap':>5}   note")
    # Only the scripted turns. The dummy never dies, so the fight runs to the
    # turn cap; every turn past the script is an empty meter resting on its
    # floor, which is true, correct, and says nothing.
    horizon = len(SCRIPT)
    for e in (x for x in _fanfare_events(state.log) if x["turn"] <= horizon):
        kind = e["event"]
        if kind == "play":
            print(f"  {e['turn']:>4}  {'play ' + e['card']:<22} "
                  f"{'':>4} {'':>8} {'':>6} {'':>5}")
            continue
        amount = e.get("amount", "")
        note = ""
        if kind == "gain_fanfare":
            note = f"source={e.get('source', '')}"
            if e.get("wasted"):
                note += f" WASTED={e['wasted']} (at cap)"
        elif kind == "fanfare_decay":
            note = "resting on floor" if e.get("at_floor") else ""
        elif kind in ("fanfare_floor_granted", "fanfare_cap_raised"):
            note = f"source={e.get('source', '')}"
        elif kind == "fanfare_read":
            note = f"kind={e.get('kind', '')}"
            if e.get("at_cap"):
                note += " AT-CAP"
            if e.get("at_floor"):
                note += " AT-FLOOR"
        print(f"  {e['turn']:>4}  {kind:<22} {amount:>4} "
              f"{e.get('total', ''):>8} {e.get('floor', ''):>6} "
              f"{e.get('cap', ''):>5}   {note}")

    decays = [e for e in state.log if e["event"] == "fanfare_decay"]
    grants = [e for e in state.log if e["event"] == "fanfare_floor_granted"]
    print(f"\n  {len(decays)} decay ticks, {len(grants)} floor grants, "
          f"final fanfare {player.fanfare} on floor {player.fanfare_floor}")

    # The assertions the trace exists to make, stated rather than left for a
    # reader to notice. Each is a live-build failure mode, not a sim one.
    if any(e["turn"] < 2 for e in decays):
        print("  !! decay fired before turn 2 -- the opening-hand rule broke")
    if not decays:
        print("  !! NO decay at all -- this is the 'fanfare still capped' bug")
    for turn, card_id in pilot.missed:            # type: ignore[attr-defined]
        print(f"  .. turn {turn}: '{card_id}' was not in hand, skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
