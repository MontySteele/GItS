"""G-A5(a): the sim/C# Fanfare parity vectors, and the fixture that binds them.

There is no C# test project -- the mod DLL only executes inside the game -- so
"run both implementations and diff" is not available. What IS available is to
make the two implementations answer the same question sheet:

  1. This module derives the answers from the SIM, which is the design of
     record, and writes them to docs/furina-fanfare-parity-vectors.json.
  2. klee-mod/KleeCode/Diagnostics/FurinaParityVectors.cs carries the same
     table as C# literals, and KleeSelfCheck runs the C# arithmetic against it
     at boot, logging a SELFCHECK error for any row that disagrees.
  3. test_csharp_vectors_match_the_sim (below) parses that C# file and asserts
     its table is byte-for-byte the sim's. That is what stops the two copies
     drifting apart in the ordinary way -- somebody edits one side.

So the Python suite guarantees the two TABLES agree, and the in-game
self-check guarantees the C# CODE agrees with its table. The composition is
the parity claim, and neither half is load-bearing alone.

WHY VECTORS RATHER THAN A TRAJECTORY. The arithmetic is where divergence
actually hides: banker's-vs-half-up rounding, whether the >= 1 rule applies
before or after the floor clamp, and whether a floor grant raises the cap
before the current value is clamped against it. Each of those is a silent
one-line difference that a winrate would never surface. SEQUENCING -- decay at
the true top of the turn, the grant after resolution -- is not checkable from
here at all, and is what G-A5(b)'s live capture and
tier05/exp_furina_parity_trace.py exist for.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

from tier0 import constants as C
from tier0.engine import resources
from tier0.engine.state import CombatState, Player

_VECTORS = (Path(__file__).resolve().parents[2]
            / "docs" / "furina-fanfare-parity-vectors.json")
_CSHARP = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
           / "Diagnostics" / "FurinaParityVectors.cs")
_RESOURCES = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
              / "Powers" / "FurinaResources.cs")

# Chosen to hit every branch of the arithmetic rather than to look plausible:
#
#   (0, 0)    empty meter resting on an empty floor -- decay must be a no-op
#             and must NOT be driven negative by the >= 1 rule.
#   (3, 0)    3 * 0.20 = 0.6 -> rounds to 1. Ordinary small case.
#   (2, 0)    2 * 0.20 = 0.4 -> rounds to 0, so the >= 1 rule is what removes
#             anything at all. This is the "cannot stall" clause.
#   (1, 0)    the smallest meter that can still fall; lands exactly on 0.
#   (5, 0)    5 * 0.20 = 1.0 exactly. No rounding involved.
#   (10, 8)   the fall (2) would land exactly ON the floor.
#   (10, 9)   the fall (2) would UNDERSHOOT the floor -- the clamp binds.
#   (9, 9)    resting exactly on the floor -- no-op, and the >= 1 rule must
#             not fire. The bug this catches is a meter that grinds through
#             its own baseline one point per turn.
#   (12, 10)  12 * 0.20 = 2.4 -> 2. Clamp does not bind.
#   (45, 0)   45 * 0.20 = 9.0 exactly, at a realistic mid-fight level.
#   (13, 0)   13 * 0.20 = 2.6 -> 3. Rounds UP, unlike 12.
#   (25, 0)   25 * 0.20 = 5.0 exactly.
#   (30, 0)   30 * 0.20 = 6.0.
#   (7, 0)    7 * 0.20 = 1.4 -> 1.
#   (2, 2)    on the floor at a value where the fall would otherwise be 0.
#   (110, 0)  110 * 0.20 = 22.0, above any realistic cap -- pins the shape at
#             a magnitude where an int-vs-double slip would show.
#
# THE BANKER'S-ROUNDING ROW. (0.5-exact cases only arise at meter values that
# are multiples of 2.5, which integers cannot be, so no vector can force the
# half-to-even tie directly. That is itself worth knowing: the tie is
# unreachable for FANFARE_DECAY_FRACTION = 0.20, so the two languages' shared
# ToEven default is currently belt-and-braces rather than load-bearing. It
# stops being unreachable the moment the fraction changes -- 0.10 makes every
# odd multiple of 5 a tie -- which is why the C# side pins MidpointRounding
# explicitly instead of relying on the default surviving a constant change.)
_DECAY_CASES = [
    (0, 0), (1, 0), (2, 0), (3, 0), (5, 0), (7, 0), (12, 10), (13, 0),
    (10, 8), (10, 9), (9, 9), (2, 2), (25, 0), (30, 0), (45, 0), (110, 0),
]

#   (current, floor, cap, grant)
#
#   (0, 0, 40, 5)     first grant into a fresh combat.
#   (38, 0, 40, 5)    current + grant would EXCEED the old cap but not the new
#                     one. This is the row that fails if the cap is raised
#                     after the clamp instead of before -- the grant would be
#                     truncated to 40 rather than reaching 43.
#   (40, 0, 40, 8)    current sitting exactly ON the old cap.
#   (12, 5, 45, 8)    ordinary mid-fight rare-Power grant.
#   (0, 15, 55, 5)    a meter BELOW its own floor (reachable only through a
#                     cap rewind bug); the grant must still behave.
#   (20, 10, 50, 15)  the constellation card's own magnitude.
_GRANT_CASES = [
    (0, 0, 40, 5), (38, 0, 40, 5), (40, 0, 40, 8), (12, 5, 45, 8),
    (0, 15, 55, 5), (20, 10, 50, 15),
]


def _state(current: int, floor: int, cap: int) -> CombatState:
    player = Player(hp=60, max_hp=60)
    player.fanfare = current
    player.fanfare_floor = floor
    player.fanfare_cap = cap
    return CombatState(player=player, enemies=[], rng=random.Random(0))


def _derive() -> dict:
    decay = []
    for current, floor in _DECAY_CASES:
        # Cap is irrelevant to decay but must be non-zero: it is the "does
        # this character have Fanfare at all" gate, mirroring burst_max.
        state = _state(current, floor, max(cap := 1000, cap))
        state.turn = 2                      # decay applies from turn 2
        resources.decay_fanfare(state)
        decay.append({"before": current, "floor": floor,
                      "after": state.player.fanfare})

    grant = []
    for current, floor, cap, n in _GRANT_CASES:
        state = _state(current, floor, cap)
        resources.gain_fanfare_floor(state, n, "parity")
        p = state.player
        grant.append({"before": current, "floor": floor, "cap": cap,
                      "grant": n, "after": p.fanfare,
                      "after_floor": p.fanfare_floor,
                      "after_cap": p.fanfare_cap})
    return {
        "_comment": ("GENERATED by tier0/tests/test_furina_fanfare_parity.py "
                     "from the sim. Do not hand-edit; regenerate. The C# "
                     "mirror is klee-mod/KleeCode/Diagnostics/"
                     "FurinaParityVectors.cs and is checked against this."),
        "decay_fraction": C.FANFARE_DECAY_FRACTION,
        "floor_per_power": C.FANFARE_FLOOR_PER_POWER,
        "floor_per_power_rare": C.FANFARE_FLOOR_PER_POWER_RARE,
        "decay": decay,
        "floor_grant": grant,
    }


def test_vectors_file_matches_the_sim():
    """The checked-in fixture is what the sim actually does, today.

    Regenerate with:
        python -m tier0.tests.test_furina_fanfare_parity
    """
    derived = _derive()
    assert _VECTORS.exists(), f"missing fixture: {_VECTORS}"
    stored = json.loads(_VECTORS.read_text(encoding="utf-8"))
    assert stored == derived, (
        "parity vectors are stale -- regenerate with "
        "`python -m tier0.tests.test_furina_fanfare_parity`, then update the "
        "C# mirror in FurinaParityVectors.cs to match")


def test_decay_never_breaches_the_floor_or_goes_negative():
    """The two properties the vectors encode, asserted as properties too.

    A table can be regenerated into agreement with a bug. These cannot.
    """
    for current, floor in _DECAY_CASES:
        state = _state(current, floor, 1000)
        state.turn = 2
        resources.decay_fanfare(state)
        after = state.player.fanfare
        assert after >= 0, (current, floor, after)
        assert after >= min(floor, current), (current, floor, after)
        assert after <= current, (current, floor, after)
        # Above the floor, SOMETHING must come off -- the anti-stall rule.
        if current > floor:
            assert after < current, (current, floor, after)


def test_floor_grant_raises_cap_before_clamping_current():
    """The 38/40/+5 row, stated as the invariant it exists to protect."""
    state = _state(38, 0, 40)
    resources.gain_fanfare_floor(state, 5, "parity")
    p = state.player
    assert (p.fanfare, p.fanfare_floor, p.fanfare_cap) == (43, 5, 45), (
        "a floor grant must raise the cap BEFORE clamping the current value "
        "against it, or the grant is silently truncated at the old ceiling")


_ROW = re.compile(
    r"new\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")
_GROW = re.compile(
    r"new\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,"
    r"\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def test_csharp_vectors_match_the_sim():
    """The C# mirror carries the same table.

    A source-text check, deliberately: the C# cannot be executed from here, so
    the achievable guarantee is that the question sheet is identical on both
    sides. KleeSelfCheck does the other half in-game.
    """
    assert _CSHARP.exists(), f"missing C# mirror: {_CSHARP}"
    src = _CSHARP.read_text(encoding="utf-8")
    derived = _derive()

    decay_block = src.split("DecayVectors")[1].split("};")[0]
    got = [tuple(int(g) for g in m) for m in _ROW.findall(decay_block)]
    want = [(row["before"], row["floor"], row["after"])
            for row in derived["decay"]]
    assert got == want, f"C# decay vectors differ\n got={got}\nwant={want}"

    grant_block = src.split("FloorGrantVectors")[1].split("};")[0]
    ggot = [tuple(int(g) for g in m) for m in _GROW.findall(grant_block)]
    gwant = [(row["before"], row["floor"], row["cap"], row["grant"],
              row["after"], row["after_floor"], row["after_cap"])
             for row in derived["floor_grant"]]
    assert ggot == gwant, f"C# grant vectors differ\n got={ggot}\nwant={gwant}"

def test_csharp_constants_match_the_sim():
    """The three ported constants, read out of the C# source.

    This is the drift that would otherwise be invisible: the vectors above
    pin BEHAVIOUR at a given fraction, but a sim-side retune of the fraction
    itself would regenerate them happily on the Python side while the live
    build kept the old number. Balance divergence, silent, in the shipped
    artifact. So the C# literals are asserted directly.
    """
    source = _RESOURCES.read_text(encoding="utf-8")

    def literal(name: str) -> str:
        m = re.search(rf"{name}\s*=\s*([0-9.]+)\s*;", source)
        assert m, f"could not find constant {name} in {_RESOURCES.name}"
        return m.group(1)

    assert float(literal("FanfareDecayFraction")) == C.FANFARE_DECAY_FRACTION
    assert int(literal("FanfareFloorPerPower")) == C.FANFARE_FLOOR_PER_POWER
    assert (int(literal("FanfareFloorPerPowerRare"))
            == C.FANFARE_FLOOR_PER_POWER_RARE)


def test_fanfare_spend_path_stays_deleted():
    """F-A4 retired `fanfare_cost`. The C# payment path is gone, not dormant.

    Asserted as an absence because that is the only way to notice a
    reintroduction: a spend that came back would not fail any behavioural
    test, it would just quietly drain a meter every card on the sheet reads.
    """
    source = _RESOURCES.read_text(encoding="utf-8")
    assert "SpendFanfare" not in source, (
        "FurinaResources.SpendFanfare is back -- Fanfare is read-only "
        "(F-A4); reopen the ruling before re-adding a spend path")
    assert "CustomResources<FanfareResource>.Cost(" not in source, (
        "a Fanfare COST is being read again; the fanfare_cost grammar is "
        "retired and no sheet carries it")


if __name__ == "__main__":
    _VECTORS.write_text(
        json.dumps(_derive(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {_VECTORS}")
