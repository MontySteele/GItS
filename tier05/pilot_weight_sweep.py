"""W4 -- the pilot-policy weight sweep harness, and the sweep DESIGN.

    PYTHONPATH=. python3 -m tier05.pilot_weight_sweep                  # plan only, runs NOTHING
    PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage coverage
    PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage screen
    PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage search --axes <the live axes the coverage stage named>
    PYTHONPATH=. python3 -m tier05.pilot_weight_sweep --execute --stage confirm --point-json P.json

Run them in that order, inside 2A's window: coverage says which axes are worth
paying for, the screen says which of those move anything, the search looks for
a combination, and confirm re-runs the one candidate on a held-out seed.

`--execute` is mandatory to run anything. The bare command prints the design
below, the DISCOVERED weight scope, the grid, the per-stage n and the measured
cost estimate, and exits without touching a cell -- because the ruled scope of
W4 is "design now; first run inside 2A's window", and a harness whose default
verb is `run` would make that fence a matter of remembering.

This module documents itself, `understudy/soak.py`'s pattern, for the same
reason: the design and the code that implements it drift the moment they live
in two files, and a sweep design that no longer describes the sweep is worse
than none.


WHAT THIS IS FOR, IN ONE SENTENCE
---------------------------------
The `EB-118` pilot pair -- bomb placement and exhaust selection, merged inert
behind `policy.PILOT_POLICIES_ENABLED = False` -- ships with HAND-PICKED
weights that were never swept, and this harness is how 2A's integration window
finds out whether any other weight vector is measurably better before the flip
is stamped.

THE PAIR'S WEIGHTS ARE NOT THIS FILE'S TO CHANGE. Nothing here writes to
`tier0/pilot/policy.py`. The harness reports; adopting a point is a separate,
stamped edit (`C.PILOT_WEIGHTS_VERSION` moves with any weight change, exactly
as it moves with the flip), and most of the grid's outcomes are [USER]'s call
rather than the integration's -- see THE TASTE / TUNING LINE below.


THIS IS ENGINEERING TUNING, NOT A REGISTERED EXPERIMENT
-------------------------------------------------------
A sweep is not pre-registered and not blind-graded: there is no prediction to
grade, and `EXPERIMENTS.md`'s registration law does not reach it. What DOES
reach it is the discipline underneath that law, and three rules carry over
verbatim:

  R68 (stamp law)   Every row this harness prints carries its cell's
                    `RT/D/P/C` stamp. A weight sweep taken across a `D` bump
                    is two sweeps, and an unstamped row cannot say which.

  R67/R33 (dead     A swept weight nothing READ produces a flat table that is
  knob law)         indistinguishable from "the weight does not matter". The
                    gate below refuses the point rather than printing the
                    table. It may not be satisfied by adding a read.

  look-first        The report is printed in GRID ORDER, never sorted by
                    winrate, and the adoption verdict is computed by the rule
                    stated below BEFORE any row is read -- not by picking the
                    best-looking row afterwards. Picking the grid maximum of a
                    noisy sweep is the forking-paths defect with extra steps,
                    and at the n this harness can afford most points will not
                    separate at all. THE EXPECTED OUTCOME IS A NULL: "no point
                    dominates, the hand-picked vector stands." That is written
                    here, before the first run, so a null cannot later be
                    reframed as the instrument having failed.


THE SCOPE IS DISCOVERED, NEVER DECLARED
---------------------------------------
`EB-118` Phase 2 has more than one build in flight against this same weights
file: 2C adds a mode-valuation chooser with weights of its own, filed in
`tier0/pilot/policy.py` for the same C#-parity reason the pair's are. A
hard-coded weight list in this file would silently stop covering the file it
claims to sweep the moment that lands.

So `discover_scope()` derives the whole thing from source, in four steps:

  (1) THE GATES themselves, from `tier0/engine/effects.py`. A gate is any
      function that late-imports the pilot module and returns it behind one
      boolean module attribute -- `return policy if policy.<FLAG> else None`.
      There is MORE THAN ONE, and that is deliberate rather than accidental:
      R191 gave 2C's mode chooser its own `MODE_CHOOSER_ENABLED` instead of a
      second reader of the pair's flag, so that flipping the pair does not
      silently activate mode valuation inside 2A's window. Hard-coding the
      pair's gate name here is exactly how this harness would have gone on
      sweeping eleven weights while 2C's landed beside them, unswept and
      unreported.

      ONE GATE PER SWEEP. The plan names every gate it found and points at
      `--gate <function>` for the others; forcing two switches at once would
      run two activation windows through one measurement.

  (2) ENTRY POINTS for that gate. Every call site of the form
      `pol = <gate>()` ... `pol.<name>(...)` names one function the switch
      gates. For the 2A pair that finds `bomb_placement_target` and
      `exhaust_victim`.

  (3) THE GATED CLOSURE, inside `tier0/pilot/policy.py`: the transitive set of
      module functions those entry points reach, and every module-level
      numeric constant loaded anywhere in it. `C.<KNOB>` reads are attribute
      loads on `constants` and are deliberately NOT collected -- those are
      `tier05.sweeps`' territory and go through its own gate.

  (4) THE PAIR-OWN / SHARED SPLIT. A constant in the closure that is ALSO
      referenced from outside it -- another policy function, or any other
      non-test module -- is SHARED. `PILOT_COMPANION_COPY_VALUE` is the live
      example: `exhaust_future_value` reaches it through `_tempo_value`, and
      so does the main scorer `_score`, so moving it moves draft scoring too.
      Shared constants are REPORTED and are NOT swept: D4 allows one variable
      per measurement window, and 2A's window already holds the flip.

A weight that arrives with no designed range -- 2C's will -- is printed under
UNRANGED and is NOT swept. This file will not invent a range for a term whose
comment it has not read; giving it one is that window's own act.


WHICH WEIGHTS (the grid), AND WHY THE NUMERAIRE IS PINNED
---------------------------------------------------------
`bomb_placement_score` is a sum of terms, each LINEAR in exactly one weight,
with coefficients that do not depend on any weight. Multiplying every bomb
VALUE weight by a positive k therefore multiplies every candidate's score by
k and leaves the argmax -- and the `(score, -hp, -index)` tie-break -- exactly
where it was. The bomb vector has one redundant degree of freedom, and a grid
that sweeps all eight axes spends most of its compute re-measuring the same
decisions under different labels.

`BOMB_LANDED_DAMAGE_VALUE` is therefore PINNED at its shipped 1.0 and used as
the numeraire: it is already documented as the unit ("a point of bomb damage
that will actually land is worth 1"), so every other bomb weight reads as
"how many points of landed damage is this worth" and the grid sweeps ratios.
`test_pilot_weight_sweep` proves the invariance rather than asserting it.
`BOMB_CONCENTRATION_STACK_CAP` is an integer COUNT cap, not a value, and does
not scale -- it stays in the grid.

The exhaust chooser has no such symmetry: `exhaust_future_value` measures its
three weights against base terms priced in `tier0/constants.py`, so all three
are free. Note also that with the shipped identity-blind payout hook the
payout term is a constant 0.0 for every candidate and cannot change a ranking;
it contributes no swept degree of freedom and no weight.

    weight                            shipped   swept range
    --------------------------------------------------------------------
    BOMB_LANDED_DAMAGE_VALUE            1.0      PINNED (numeraire)
    BOMB_LETHAL_WASTE_WEIGHT            1.0      0.0  0.5  1.0  1.5  2.0
    BOMB_CONCENTRATION_VALUE            2.0      0.0  1.0  2.0  4.0  6.0
    BOMB_CONCENTRATION_STACK_CAP        3        1    2    3    5
    BOMB_SUPPRESSION_VALUE              1.0      0.0  0.5  1.0  1.5
    BOMB_READER_LETHAL_POP_VALUE        4.0      0.0  2.0  4.0  8.0
    BOMB_EARLY_POP_PENALTY              3.0      0.0  1.5  3.0  6.0
    BOMB_MOVE_READER_AIM_VALUE          1.0      0.0  1.0  2.0
    EXHAUST_COST_EFFICIENCY_WEIGHT      0.5      0.0  0.25 0.5  1.0
    EXHAUST_SELF_EXHAUST_DISCOUNT       0.5      0.25 0.5  0.75 1.0
    EXHAUST_JUNK_BONUS                  6.0      NOT SWEEPABLE -- see below

Every range brackets the shipped value on both sides and includes the value
that TURNS THE TERM OFF, so each axis answers "is this term earning its place"
before it answers "is it sized right". `EXHAUST_SELF_EXHAUST_DISCOUNT` tops
out at 1.0 because that is the whole discount removed; above it the term would
stop being a discount.

`EXHAUST_JUNK_BONUS` IS EXPECTED TO REGISTER ZERO READS AND IS EXPECTED TO BE
REFUSED BY THE GATE. Post-`C11` Kokomi's rotation law drops Statuses and
Curses from the unfiltered chosen-Exhaust pool before the chooser ever sees
them, and she is the only shipped carrier of a chosen `exhaust_from`; the one
reachable caller left is `real_ironclad`'s True Grit+, which needs the
gitignored `game_ref/` tree and is absent on a fresh clone. This is written
down in ADVANCE so that the refusal reads as the gate working rather than as a
harness defect -- and the correct response to it is to leave the weight alone,
not to invent a read for it (R33).


WHAT THE COVERAGE PROBE ALREADY SAYS (instrument verification, NOT a result)
---------------------------------------------------------------------------
Read counts taken at n = 300, seed 11, `RT12/D15/P7/C11`, while proving the
harness works. These are read COUNTS, not outcomes: no winrate was compared,
no point was ranked, and nothing here is a tuning finding.

    cell               weight                          reads   share
    ------------------------------------------------------------------
    bomb-primary       BOMB_LANDED_DAMAGE_VALUE         9968   100%
                       BOMB_LETHAL_WASTE_WEIGHT         9968   100%
                       BOMB_SUPPRESSION_VALUE           3829    38%
                       BOMB_CONCENTRATION_STACK_CAP     2714    27%
                       BOMB_CONCENTRATION_VALUE         2521    25%
                       BOMB_EARLY_POP_PENALTY            207     2%
                       BOMB_READER_LETHAL_POP_VALUE       27   0.3%
                       BOMB_MOVE_READER_AIM_VALUE          4   0.04%
    exhaust-primary    EXHAUST_COST_EFFICIENCY_WEIGHT   9219   100%
                       EXHAUST_SELF_EXHAUST_DISCOUNT     384     4%
                       EXHAUST_JUNK_BONUS                  0     0%

Two things follow, and both are design, not accident:

  * `EXHAUST_JUNK_BONUS` reads ZERO, exactly as predicted above. It is
    structurally unreachable in these cells and is refused, not swept.

  * `BOMB_MOVE_READER_AIM_VALUE` (0.04%) and `BOMB_READER_LETHAL_POP_VALUE`
    (0.3%) are alive but UNDERPOWERED. `move_bombs` is on exactly one Klee
    row, and the term only fires when that card is in hand at the moment a
    concentration bomb is placed. Four decisions in ten thousand cannot move
    a winrate at any n this harness can afford, so a nonzero gate would pass
    them and the sweep would still learn nothing.

Hence `POWER_FLOOR`: the coverage stage prints each axis's share of its cell's
decisions and labels it DEAD / thin / live. THIN AXES ARE SCREENED (it is
cheap) BUT MUST NOT ENTER THE SEARCH STAGE -- pass the live axes explicitly
with `--axes`. This is advisory and stays advisory: "was it read" is a fact
and gets a gate; "could it possibly show" is a power judgement and gets a
printed label.


WHICH CELLS
-----------
Five, all derived from the ratified cell (`cells.CANONICAL`: seed 11, hunter,
`assigned`, realistic, all acts) so the only declared deltas are the character
and the plan:

    bomb-primary        klee/demolition   the concentration form's home. Four
                                          Klee rows carry `place_bomb` with
                                          `target: enemy`; nothing else in any
                                          shipped sheet does.
    bomb-secondary      klee/spark        the same weights OFF the arm they
                                          would be tuned on. A vector that
                                          helps demolition and hurts spark is
                                          not an improvement, it is a trade.
    exhaust-primary     kokomi/priest     the casket engine, where deliberate
                                          exhausts are the loop.
    exhaust-secondary   kokomi/assist     the arm with the worst realized
                                          payoff reach of the nine; a chooser
                                          change lands differently on a deck
                                          that is starving.
    null-control        furina/salon      no Furina row carries either op, so
                                          EVERY point must return a BYTE-
                                          IDENTICAL result digest here. A
                                          moving null cell means the harness
                                          is leaking, and the sweep is void.

The null control is not decoration. It is the only row in the report that can
distinguish "these weights did something" from "something else in this process
did something".

`CELL_SPECS` IS THE 2A PAIR'S CARRIER MAP, not a general one. Another gate has
other carriers -- 2C's mode chooser rides `deep_breath`, which is Furina's, so
the arm that is this sweep's null control would be that sweep's primary and a
Klee arm would be its control. Reusing the pattern in 2C's window means
re-deriving the carriers, not inheriting these five rows.


N PER POINT, AND WHAT IT CAN SEE
--------------------------------
    stage      n/point/cell   what it is for
    ------------------------------------------------------------------
    coverage   40             read counts only. Which weights are alive in
                              which cell, and the per-cell wall clock the
                              cost estimate is built from. No winrate is
                              reported at this n and none may be quoted.
    screen     300            ONE-AT-A-TIME: each free weight moved alone
                              across its range, all others at shipped. Finds
                              which axes the outcome is sensitive to at all.
                              A screen row NEVER adopts anything.
    search     600            the ratified n. Random search over only the
                              axes the screen separated, sampled from the
                              same value sets, seeded and therefore
                              reproducible.
    confirm    2000, SEED 12  the held-out re-run. A point may not be called
                              adoptable on the seed it was found on.

At n = 600 and a winrate near 5% the Wilson half-width is about 1.8pp, so a
point has to move the winrate by roughly its own size to separate. That is the
honest resolution of this instrument and it is why the screen exists: spending
600 runs on an axis nothing reads, or that moves nothing, is the same waste
R67 was written about.

MEASURED COST, from the coverage stage on this tree: about 0.035 s per run,
serial. That puts the screen at ~48k runs (~28 serial minutes), the search at
~147k (~86), and a confirm pair at ~20k (~12) -- all of it divided by the
worker count, so the whole design fits comfortably inside one window. The
coverage stage recomputes these from its own clock and prints them, because a
cost table that was true on somebody else's machine is not a cost table.


THE DECISION RULE
-----------------
Computed per candidate point P against the shipped baseline B, over the four
measurement cells (the null control is a validity check, not a term):

  P is DOMINATING  -- iff on NO cell is P's winrate Wilson-95 interval wholly
                      BELOW B's, on NO cell is any act's cleared-rate interval
                      wholly below B's, and on AT LEAST ONE cell P's winrate
                      interval is wholly ABOVE B's.
  P is DOMINATED   -- iff the mirror image holds with the roles swapped.
  P is INSEPARABLE -- every interval overlaps everywhere. The commonest
                      verdict, and a real one.
  P is a TRADE     -- P separates above on one cell and below on another.

Only a DOMINATING point that also reproduces as DOMINATING at the confirm
stage on seed 12 may be adopted, and adopting it is still a
`PILOT_WEIGHTS_VERSION` bump in its own edit with the sweep row cited.


THE TASTE / TUNING LINE
-----------------------
The integration may adopt, on its own authority, ONLY this:

  * a DOMINATING point that reproduces at confirm on the held-out seed. It is
    better everywhere it is different and worse nowhere; there is no
    preference to express, so there is nothing for [USER] to rule on.
  * dropping a DOMINATED point. Discarding something strictly worse is not a
    choice either.

EVERYTHING ELSE GOES TO [USER] VIA `QUEUE.md`. Specifically:

  * A TRADE. "Klee's demolition arm gains what Kokomi's assist arm loses" is a
    question about which character should be flying better, and that is
    design, not tuning.
  * Any pick among INSEPARABLE points. Choosing the prettiest row of a table
    whose intervals all overlap is taste wearing a number's clothes -- and the
    hand-picked vector is itself an inseparable point, so the honest default
    is to keep it and change nothing.
  * Any move to a SHARED weight (step (3) above). It leaves the pair's window
    and moves draft scoring, which is a second variable in a window that
    already has one.
  * Turning a term OFF -- any adopted 0.0. Deleting a term the packet argued
    for is a design reversal even when the number supports it, and the term's
    written rationale has to be withdrawn rather than quietly outvoted.
  * Anything that moves `BOMB_CONCENTRATION_STACK_CAP`. The cap is the term
    the pair's own comment calls a judgement about marginal noise versus
    lethal-waste risk; a sweep can say what it costs but not whether that
    judgement was the intended one.

Where the rule and a reading disagree, the rule wins; where this docstring and
the packet disagree, the packet
(`review/active/eb118-richness-phase0-2026-08-23.md`) wins.


WHAT THE SANDBOX GUARANTEES
---------------------------
`sandbox()` forces `PILOT_POLICIES_ENABLED` ON and arms the weights IN THIS
PROCESS only, and restores every name it touched -- values AND types -- on the
way out of any exception. The live switch is never written to disk and the
shipped default is never flipped; `test_pilot_weight_sweep` holds the proof
from both sides (the switch reads False after a sandbox that raised, and a
cell run with the sandbox NOT forcing is byte-identical across two wildly
different weight vectors).

Weights are armed as `float`/`int` SUBCLASSES that count their own arithmetic,
which is how the dead-weight gate sees a real read on the real read path
without `tier0/pilot/policy.py` being taught to report anything (R33). The
subclass returns ordinary floats from every operation, so nothing propagates
into the engine and no number changes.

PARALLELISM IS AT THE POINT LEVEL, NEVER INSIDE A CELL. `model.run_many(jobs>1)`
spreads a batch over worker PROCESSES that re-import `tier0.pilot.policy` and
would therefore run the SHIPPED weights while the parent believed it was
sweeping -- the exact silent-null R67 exists to prevent. Every cell this
harness runs is pinned to `jobs=1` and the pool is one worker per (point,
cell) task instead, each worker arming its own sandbox before it runs.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import random
import sys
import time
from collections.abc import Iterator, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tier05 import stats, sweeps

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_SOURCE = REPO_ROOT / "tier0" / "pilot" / "policy.py"
EFFECTS_SOURCE = REPO_ROOT / "tier0" / "engine" / "effects.py"

#: The 2A pair's switch -- the gate this harness plans against unless told
#: otherwise. Named, not hard-coded as THE gate: `discover_gates` finds every
#: switch in the engine and each gets its own sweep in its own window.
DEFAULT_SWITCH = "PILOT_POLICIES_ENABLED"

#: Where a constant referenced outside the gated closure makes it SHARED.
#: Tests are excluded: a test naming a weight is not a second consumer of it.
_SHARED_SCAN_ROOTS = ("tier0", "tier05")


class DeadWeightError(sweeps.DeadKnobError):
    """A swept pilot weight was never read while its cell ran.

    Subclasses `tier05.sweeps.DeadKnobError` deliberately: this is the same
    law (R67, and R33 underneath it) applied to the weights that live in
    `tier0/pilot/policy.py` instead of in `tier0/constants.py`. `sweeps.sweep`
    cannot arm these -- `constants._arm_knob` only knows its own module -- but
    the failure it refuses to print is identical.
    """


# ---------------------------------------------------------------------------
#  Read counting, without teaching policy.py to report anything (R33)
# ---------------------------------------------------------------------------

#: name -> number of real arithmetic/comparison uses since the last reset.
READS: dict[str, int] = {}


def reset_reads() -> None:
    READS.clear()


def _counted(cls):
    """Build a numeric subclass that tallies its own uses into READS.

    Counting arithmetic rather than attribute access is what makes this work
    at all: `policy.py` reads its own weights as bare module globals, and a
    PEP-562 module `__getattr__` -- the mechanism `tier0/constants.py` uses --
    is never consulted for a same-module global load.

    Every operation returns whatever the base type returns, so an armed weight
    is numerically indistinguishable from the plain one and nothing counted
    escapes into the engine.
    """
    ops = ("add", "radd", "sub", "rsub", "mul", "rmul", "truediv", "rtruediv",
           "floordiv", "rfloordiv", "mod", "rmod", "pow", "rpow",
           "lt", "le", "gt", "ge")
    ns: dict[str, Any] = {}

    def make(name):
        base = getattr(cls, f"__{name}__")

        def op(self, other):
            READS[self._w4_name] = READS.get(self._w4_name, 0) + 1
            return base(self, other)
        return op

    for name in ops:
        ns[f"__{name}__"] = make(name)

    def _neg(self):
        READS[self._w4_name] = READS.get(self._w4_name, 0) + 1
        return -cls(self)
    ns["__neg__"] = _neg

    def _new(subcls, value, name):
        # No __slots__: `int` is a variable-length type and refuses a
        # non-empty one, so the instance dict is what carries the label.
        self = cls.__new__(subcls, value)
        self._w4_name = name
        return self
    ns["__new__"] = _new
    return type(f"_Counted{cls.__name__.capitalize()}", (cls,), ns)


_CountedFloat = _counted(float)
_CountedInt = _counted(int)


def _arm_value(name: str, value):
    """Wrap `value` so its uses are counted. Bools are never weights."""
    if isinstance(value, bool):
        raise TypeError(f"{name} is a bool, not a weight")
    if isinstance(value, int):
        return _CountedInt(value, name)
    return _CountedFloat(float(value), name)


# ---------------------------------------------------------------------------
#  Discovery
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Gate:
    """One switch in the engine, and the function that reads it.

    `EB-118` ships more than one on purpose: R191 gave the 2C mode chooser its
    OWN activation window rather than a second reader of the pair's flag,
    because sharing one flag would activate mode valuation inside 2A's window
    and leave 2C's `POLICY_VERSION` bump with nothing to attribute. This
    harness honours that -- ONE gate per sweep, and it forces only that gate's
    switch.
    """

    function: str
    switch: str


@dataclass(frozen=True)
class WeightScope:
    """What this harness may sweep, derived from source at call time."""

    entry_points: tuple[str, ...]
    #: constant -> shipped value, reachable ONLY through the gated closure.
    pair_own: dict[str, float]
    #: constant -> shipped value, in the closure but read elsewhere too.
    shared: dict[str, float]
    #: the gate this scope is about, and every other gate found beside it.
    gate: Gate = Gate(function="_pilot_policies", switch=DEFAULT_SWITCH)
    gates: tuple[Gate, ...] = ()

    @property
    def defaults(self) -> dict[str, float]:
        return dict(self.pair_own)

    def describe(self) -> str:
        lines = [f"gate: {self.gate.function}() -> {self.gate.switch}"]
        others = [g for g in self.gates if g != self.gate]
        if others:
            lines.append("other gates found (each its OWN window, its own "
                         "sweep -- never both in one):")
            lines += [f"    --gate {g.function}   ({g.switch})"
                      for g in others]
        lines += [f"gated entry points ({len(self.entry_points)}): "
                  + ", ".join(self.entry_points),
                  f"pair-own weights ({len(self.pair_own)}), SWEEPABLE:"]
        for k, v in sorted(self.pair_own.items()):
            pin = "  [PINNED numeraire]" if k in PINNED else ""
            lines.append(f"    {k:<34} {v!r}{pin}")
        lines.append(f"shared weights ({len(self.shared)}), REPORTED ONLY "
                     f"-- moving one leaves this gate's window (D4):")
        for k, v in sorted(self.shared.items()):
            lines.append(f"    {k:<34} {v!r}")
        return "\n".join(lines)


def _read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _calls(node: ast.AST, name: str) -> bool:
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        fn = sub.func
        if isinstance(fn, ast.Name) and fn.id == name:
            return True
        if isinstance(fn, ast.Attribute) and fn.attr == name:
            return True
    return False


def discover_gates(src: str) -> tuple[Gate, ...]:
    """Every `... -> policy if policy.<FLAG> else None` gate in the engine.

    Structural, not by name: a gate is a function that late-imports the pilot
    module and returns it behind one boolean module attribute. Both shipped
    gates have exactly that shape, and a hard-coded gate name is how this
    harness would have gone on sweeping the 2A pair while 2C's chooser landed
    beside it, unswept and unreported.
    """
    tree = ast.parse(src)
    out: list[Gate] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(isinstance(n, ast.ImportFrom)
                   and any(a.name == "policy" for a in n.names)
                   for n in ast.walk(fn)):
            continue
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Return)
                    and isinstance(node.value, ast.IfExp)):
                continue
            body, test = node.value.body, node.value.test
            if not (isinstance(body, ast.Name) and body.id == "policy"):
                continue
            if (isinstance(test, ast.Attribute)
                    and isinstance(test.value, ast.Name)
                    and test.value.id == "policy"):
                out.append(Gate(function=fn.name, switch=test.attr))
    return tuple(sorted(set(out), key=lambda g: g.function))


def entry_points_from_source(src: str,
                             gate: str = "_pilot_policies") -> tuple[str, ...]:
    """Names the switch gates, read off the engine's own call sites.

    The shape it looks for is the one both call sites use and the one any
    later policy is expected to use: bind the result of the gate function to a
    local, then call methods on it. Kept source-in / names-out so a test can
    feed it a synthetic third call site instead of editing the engine.
    """
    tree = ast.parse(src)
    found: set[str] = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        holders: set[str] = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and _calls(node.value, gate):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        holders.add(target.id)
        if not holders:
            continue
        for node in ast.walk(fn):
            if (isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id in holders
                    and isinstance(node.ctx, ast.Load)):
                found.add(node.attr)
    return tuple(sorted(found))


def _numeric_globals(tree: ast.Module) -> dict[str, float]:
    out: dict[str, float] = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        if not name.isupper():
            continue
        value = node.value
        if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
                and isinstance(value.operand, ast.Constant)):
            inner = value.operand.value
            if isinstance(inner, (int, float)) and not isinstance(inner, bool):
                out[name] = -inner
            continue
        if isinstance(value, ast.Constant):
            inner = value.value
            if isinstance(inner, (int, float)) and not isinstance(inner, bool):
                out[name] = inner
    return out


def _functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _closure(funcs: Mapping[str, ast.AST],
             entries: Sequence[str]) -> set[str]:
    """Every function reachable from `entries`, by CALL or by REFERENCE.

    A bare Name load counts, not only an `ast.Call`, and that is the same
    REACHABILITY question `discover_scope`'s docstring already frames rather
    than a widening for its own sake: a function handed around as a VALUE runs
    just as surely as one invoked in place, so the weights it loads are inside
    the gate's surface.

    IT WAS FOUND BY A HOLE RATHER THAN BY DESIGN (W3 -- EB-118 Phase 3, R211,
    2026-08-25). `policy.exhaust_victim` picks its payout hook with
    `payout = payout or formula_aware_payout` and then calls it through the
    local name, so a call-only walk never reached `formula_aware_payout` and
    `EXHAUST_FORMULA_PAYOUT_WEIGHT` -- a live pilot weight that decides which
    card a chosen Exhaust spends -- was invisible to this sweep. A weight the
    sweep cannot see cannot be swept and cannot be cited, which is exactly the
    dead-knob condition R67 exists to refuse.
    BLAST RADIUS MEASURED BEFORE THE CHANGE AND AFTER, on both gates: the
    exhaust gate's pair-own set gains that ONE name and nothing else moves.
    It arrives UNRANGED, which is this file's designed behaviour for a weight
    discovered later -- it is reported in the plan and not swept, because the
    harness does not invent a range for a term whose comment it has not read.
    """
    seen: set[str] = set()
    stack = [e for e in entries if e in funcs]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        for node in ast.walk(funcs[name]):
            if (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                    and node.id in funcs):
                stack.append(node.id)
    return seen


def _names_loaded(funcs: Mapping[str, ast.AST], where: Sequence[str],
                  universe: Mapping[str, float]) -> set[str]:
    out: set[str] = set()
    for name in where:
        for node in ast.walk(funcs[name]):
            if (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                    and node.id in universe):
                out.add(node.id)
    return out


def _referenced_elsewhere(universe: Mapping[str, float]) -> set[str]:
    """Constants any OTHER non-test module names, by load or by attribute.

    AST rather than a text scan on purpose: `tier05/draft.py` discusses two of
    these weights in prose, and a comment is not a consumer.
    """
    out: set[str] = set()
    here = Path(__file__).resolve()
    for root in _SHARED_SCAN_ROOTS:
        for path in (REPO_ROOT / root).rglob("*.py"):
            parts = path.relative_to(REPO_ROOT).parts
            if "tests" in parts:
                continue
            if path.resolve() in (POLICY_SOURCE.resolve(), here):
                continue
            try:
                tree = ast.parse(_read_source(path))
            except SyntaxError:                     # pragma: no cover
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in universe:
                    out.add(node.attr)
                elif (isinstance(node, ast.Name) and node.id in universe
                      and isinstance(node.ctx, ast.Load)):
                    out.add(node.id)
    return out


def discover_scope(gate: Gate | str | None = None) -> WeightScope:
    """The sweepable surface of ONE gate, derived from source.

    Never a hard-coded list, and never two gates at once: sweeping the pair's
    weights and 2C's mode weights in one grid would put two activation windows
    in one measurement, which is the thing R191 split them to avoid.

    "Shared" is a REACHABILITY question, not a which-function-mentions-it one.
    `_tempo_value` loads `PILOT_COMPANION_COPY_VALUE` and sits inside the
    gated closure, but the main scorer `_score` reaches `_tempo_value` too --
    so the constant is shared, and only a closure taken from every non-gated
    function sees that.
    """
    effects_src = _read_source(EFFECTS_SOURCE)
    gates = discover_gates(effects_src)
    if isinstance(gate, str):
        matches = [g for g in gates if gate in (g.function, g.switch)]
        if not matches:
            raise KeyError(f"no gate {gate!r}; found "
                           f"{', '.join(g.function for g in gates) or 'none'}")
        gate = matches[0]
    elif gate is None:
        gate = next((g for g in gates if g.switch == DEFAULT_SWITCH),
                    gates[0] if gates else
                    Gate("_pilot_policies", DEFAULT_SWITCH))
    entries = entry_points_from_source(effects_src, gate.function)
    tree = ast.parse(_read_source(POLICY_SOURCE))
    universe = _numeric_globals(tree)
    funcs = _functions(tree)
    gated = _closure(funcs, entries)
    ungated_roots = [n for n in funcs if n not in gated]
    reachable_otherwise = _closure(funcs, ungated_roots)
    in_closure = _names_loaded(funcs, sorted(gated), universe)
    outside = _names_loaded(funcs, sorted(reachable_otherwise), universe)
    outside |= _referenced_elsewhere(universe)
    # The gate's own flag is not a weight, whichever gate this is.
    switches = {g.switch for g in gates} | {gate.switch}
    pair_own = {k: universe[k]
                for k in sorted(in_closure - outside - switches)}
    shared = {k: universe[k] for k in sorted((in_closure & outside)
                                             - switches)}
    return WeightScope(entry_points=entries, pair_own=pair_own, shared=shared,
                       gate=gate, gates=gates)


# ---------------------------------------------------------------------------
#  The grid
# ---------------------------------------------------------------------------

#: Held at its shipped value. `bomb_placement_score` is homogeneous of degree
#: one in the bomb VALUE weights, so the vector is scale-invariant and one
#: axis has to be the unit or the grid re-measures itself.
PINNED = ("BOMB_LANDED_DAMAGE_VALUE",)

#: The designed ranges. A weight discovered later with no row here is reported
#: as UNRANGED in the plan and is not swept -- the harness will not invent a
#: range for a term whose comment it has not read.
RANGES: dict[str, tuple[float, ...]] = {
    "BOMB_LETHAL_WASTE_WEIGHT": (0.0, 0.5, 1.0, 1.5, 2.0),
    "BOMB_CONCENTRATION_VALUE": (0.0, 1.0, 2.0, 4.0, 6.0),
    "BOMB_CONCENTRATION_STACK_CAP": (1, 2, 3, 5),
    "BOMB_SUPPRESSION_VALUE": (0.0, 0.5, 1.0, 1.5),
    "BOMB_READER_LETHAL_POP_VALUE": (0.0, 2.0, 4.0, 8.0),
    "BOMB_EARLY_POP_PENALTY": (0.0, 1.5, 3.0, 6.0),
    "BOMB_MOVE_READER_AIM_VALUE": (0.0, 1.0, 2.0),
    "EXHAUST_COST_EFFICIENCY_WEIGHT": (0.0, 0.25, 0.5, 1.0),
    "EXHAUST_SELF_EXHAUST_DISCOUNT": (0.25, 0.5, 0.75, 1.0),
    "EXHAUST_JUNK_BONUS": (0.0, 3.0, 6.0, 12.0),
}

#: cell name -> (character, archetype, role). `measure` cells carry the
#: verdict; the `control` cell must not move at all.
CELL_SPECS: dict[str, tuple[str, str, str]] = {
    "bomb-primary": ("klee", "demolition", "measure"),
    "bomb-secondary": ("klee", "spark", "measure"),
    "exhaust-primary": ("kokomi", "priest", "measure"),
    "exhaust-secondary": ("kokomi", "assist", "measure"),
    "null-control": ("furina", "salon", "control"),
}

#: stage -> (n per point per cell, seed). `confirm` is the held-out seed.
STAGE_N: dict[str, tuple[int, int]] = {
    "coverage": (40, 11),
    "screen": (300, 11),
    "search": (600, 11),
    "confirm": (2000, 12),
}

SEARCH_POINTS = 48


def registered_cells(names: Sequence[str] | None = None,
                     *, runs: int, seed: int) -> dict:
    """The registered cells, built lazily off `cells.CANONICAL`.

    Lazy because constructing a `Cell` validates its plan through
    `runner.resolve_plan`, and this module must stay importable (and cheap)
    for the plan-only path and for a worker process.

    `jobs=1` is not a default here, it is a REQUIREMENT -- see the parallelism
    note in the module docstring.
    """
    from tier05 import cells as cells_mod
    wanted = list(names) if names else list(CELL_SPECS)
    out = {}
    for name in wanted:
        if name not in CELL_SPECS:
            raise KeyError(f"unknown cell {name!r}; registered: "
                           f"{', '.join(CELL_SPECS)}")
        character, archetype, _role = CELL_SPECS[name]
        out[name] = cells_mod.CANONICAL.but(
            name=f"w4-{name}", character=character, archetype=archetype,
            runs=runs, seed=seed, jobs=1)
    return out


def screen_points(scope: WeightScope) -> list[dict[str, float]]:
    """One-at-a-time: the baseline, then each free axis moved alone.

    Ordered, never shuffled: the report prints in grid order and the reader
    has to be able to find a row by counting.
    """
    base = scope.defaults
    points = [dict(base)]
    for name in sorted(base):
        if name in PINNED or name not in RANGES:
            continue
        for value in RANGES[name]:
            if value == base[name]:
                continue
            point = dict(base)
            point[name] = value
            points.append(point)
    return points


def search_points(scope: WeightScope, axes: Sequence[str], *,
                  count: int = SEARCH_POINTS,
                  seed: int = 20260824) -> list[dict[str, float]]:
    """Random search over `axes` only, from the same declared value sets.

    Seeded and de-duplicated, so a search is reproducible from its seed and no
    point is paid for twice. The baseline is always point zero.
    """
    base = scope.defaults
    live = [a for a in axes if a in RANGES and a not in PINNED]
    rng = random.Random(seed)
    points = [dict(base)]
    seen = {tuple(sorted(base.items()))}
    attempts = 0
    while len(points) < count + 1 and attempts < count * 200:
        attempts += 1
        point = dict(base)
        for axis in live:
            point[axis] = rng.choice(RANGES[axis])
        key = tuple(sorted(point.items()))
        if key in seen:
            continue
        seen.add(key)
        points.append(point)
    return points


# ---------------------------------------------------------------------------
#  The sandbox
# ---------------------------------------------------------------------------

@dataclass
class SandboxState:
    """What a sandbox did, so a caller never has to assume it."""

    #: True when the harness had to force the switch on (the shipped state).
    forced: bool
    armed: tuple[str, ...] = ()
    reads: dict[str, int] = field(default_factory=dict)


@contextmanager
def sandbox(values: Mapping[str, float] | None = None, *, force: bool = True,
            switch: str = DEFAULT_SWITCH) -> Iterator[SandboxState]:
    """Hold ONE gate ON at `values`, in THIS process, and put it back.

    Exactly one switch is forced -- the one named. Forcing every gate at once
    would run two activation windows through one measurement, which is what
    R191 split the mode chooser out of the pair's flag to prevent.

    Restoration runs out of any exception, and restores the ORIGINAL objects
    rather than equal copies -- a counted subclass left behind in a live
    module would keep tallying into a later sweep's numbers and would be
    invisible at every call site.

    `force=False` arms the weights but leaves the switch exactly as it was.
    That is the byte-identity arm: with the switch off the engine never
    reaches a weight, so two very different vectors must produce the same run.
    """
    from tier0.pilot import policy

    values = dict(values or {})
    missing = [n for n in values if not hasattr(policy, n)]
    if missing:
        raise AttributeError(
            f"no such pilot weight(s): {', '.join(sorted(missing))}. A typo'd "
            f"weight would sweep nothing at all and print a clean null, which "
            f"is the defect this harness exists to refuse (R67).")
    if not hasattr(policy, switch):
        raise AttributeError(f"no such switch: {switch!r}")
    was_on = getattr(policy, switch)
    originals = {name: getattr(policy, name) for name in values}
    reset_reads()
    state = SandboxState(forced=bool(force and not was_on),
                         armed=tuple(sorted(values)))
    try:
        for name, value in values.items():
            setattr(policy, name, _arm_value(name, value))
        if force:
            setattr(policy, switch, True)
        yield state
    finally:
        for name, original in originals.items():
            setattr(policy, name, original)
        setattr(policy, switch, was_on)
        # Every armed name, INCLUDING the ones that recorded nothing: a
        # weight missing from the report and a weight reading zero are the
        # same fact, and only one of them is legible.
        state.reads = {name: READS.get(name, 0) for name in values}
        reset_reads()


# ---------------------------------------------------------------------------
#  Measurement
# ---------------------------------------------------------------------------

def result_digest(results: Sequence[Any]) -> str:
    """A stable fingerprint of a cell's outcome, for identity proofs.

    Deliberately more than the winrate: two weight vectors can reach the same
    winrate through different runs, and the null control's claim is that the
    RUNS are identical, not that the summary is.
    """
    h = hashlib.sha256()
    for r in results:
        h.update(repr((r.seed, bool(r.won), r.death_node, tuple(r.hp_by_node),
                       tuple(r.deck_ids), r.acts_completed)).encode("utf-8"))
    return h.hexdigest()[:16]


def summarize(results: Sequence[Any]) -> dict:
    """Winrate and the per-act funnel, each with its Wilson-95 interval."""
    from tier05 import run_metrics

    n = len(results)
    wins = sum(1 for r in results if r.won)
    lo, hi = stats.wilson95(wins, n)
    acts = []
    for row in run_metrics.act_funnel(list(results)):
        a_lo, a_hi = stats.wilson95(row["cleared"], n)
        acts.append({"act": row["act"], "cleared_rate": row["cleared_rate"],
                     "lo": a_lo, "hi": a_hi})
    return {"n": n, "win": wins / n if n else 0.0, "win_lo": lo, "win_hi": hi,
            "acts": acts, "digest": result_digest(results)}


def evaluate(cell, values: Mapping[str, float], *, force: bool = True,
             switch: str = DEFAULT_SWITCH) -> dict:
    """Run one cell at one weight point and reduce it to a report row.

    No gate here on purpose. The R67 question is asked once per POINT, by
    `gate_point` -- see its docstring for why a per-cell answer would be the
    wrong one.
    """
    started = time.perf_counter()
    with sandbox(values, force=force, switch=switch) as sb:
        results = cell.run()
    row = summarize(results)
    row.update({"stamp": cell.stamp(), "cell": cell.name,
                "values": dict(values), "reads": dict(sb.reads),
                "forced": sb.forced, "seconds": time.perf_counter() - started})
    return row


def gate_point(group: Sequence[Mapping], baseline: Mapping[str, float]) -> None:
    """R67, asked once per weight point across all its measurement cells.

    NOT per cell, and the difference matters: a bomb weight is structurally
    unread in a Kokomi cell and an exhaust weight is structurally unread in a
    Klee one, so a per-cell gate would refuse every point in the grid. What
    the sweep actually needs to know is whether the axis it MOVED was read
    ANYWHERE while the point ran. An axis that was not is the flat-table
    defect, and the point is refused rather than printed.

    Only the moved axes are gated. A baseline point moves nothing and is
    always admissible -- it is the comparator, not a claim about a weight.
    """
    measure = {f"w4-{n}" for n, (_c, _a, role) in CELL_SPECS.items()
               if role == "measure"}
    rows = [r for r in group if r.get("cell") in measure and "reads" in r]
    if not rows:
        return
    moved = sorted({k for r in rows for k, v in r["values"].items()
                    if v != baseline.get(k, v)})
    dead = [k for k in moved
            if sum(r["reads"].get(k, 0) for r in rows) == 0]
    if dead:
        raise DeadWeightError(
            f"swept {', '.join(dead)} and no measurement cell read "
            f"{'them' if len(dead) > 1 else 'it'} even once. Every row of "
            f"this axis would be identical to the baseline, and identical "
            f"rows here mean instrument error, NOT 'the weight does not "
            f"matter'. Sweep it in a cell that reaches it, or leave it alone "
            f"(R67); do not add a read to satisfy this gate (R33).")


#: Below this share of a cell's decisions, an axis cannot separate at any n
#: this harness can afford. Advisory, and deliberately NOT a second gate: the
#: R67 gate answers "was it read at all", which is a fact; this answers "could
#: a difference show", which is a judgement about power and is printed as one.
POWER_FLOOR = 0.01


def read_shares(row: Mapping) -> dict[str, float]:
    """Each armed weight's reads as a share of the busiest weight's.

    The busiest weight is the one read once per candidate evaluation -- the
    numeraire, for bombs -- so the share reads as "what fraction of this
    cell's decisions could this term have touched at all". An axis read four
    times in ten thousand evaluations passes the R67 gate honestly and still
    cannot move a winrate, and a sweep that spends 600 runs on it has bought
    nothing.
    """
    reads = row.get("reads") or {}
    busiest = max(reads.values(), default=0)
    if not busiest:
        return {k: 0.0 for k in reads}
    return {k: v / busiest for k, v in reads.items()}


def power_label(share: float) -> str:
    if share == 0:
        return "DEAD"
    return "thin" if share < POWER_FLOOR else "live"


def _task(payload: tuple) -> dict:
    """One (point, cell) evaluation, in whatever process owns it.

    Module-level and argument-only so it survives a spawned worker, which is
    the platform this repo builds on. The worker arms its OWN sandbox -- the
    parent's is not inherited under spawn, and assuming it was is exactly the
    silent null the docstring warns about.
    """
    cell_name, values, runs, seed, force, switch = payload
    cell = registered_cells([cell_name], runs=runs, seed=seed)[cell_name]
    return evaluate(cell, values, force=force, switch=switch)


def run_stage(stage: str, points: Sequence[Mapping[str, float]],
              cell_names: Sequence[str] | None = None, *,
              jobs: int = 0, gate: bool = True,
              baseline: Mapping[str, float] | None = None,
              switch: str = DEFAULT_SWITCH, progress=None) -> list[dict]:
    """Evaluate every point on every registered cell.

    Parallel over TASKS, never inside a cell (see the module docstring). One
    worker per (point, cell); each arms its own sandbox.

    The gate fires on the FIRST offending point rather than after the grid,
    `sweeps.sweep`'s rule and for its reason: a dead-axis sweep is compute
    with nothing at the end of it.
    """
    runs, seed = STAGE_N[stage]
    names = list(cell_names) if cell_names else list(CELL_SPECS)
    base = dict(baseline if baseline is not None else (points[0] if points else {}))
    payloads = [(name, dict(point), runs, seed, True, switch)
                for point in points for name in names]
    workers = (os.cpu_count() or 1) if jobs == 0 else jobs
    workers = max(1, min(workers, len(payloads) or 1))
    rows: list[dict] = []

    def take(row):
        rows.append(row)
        if progress:
            progress(len(rows), len(payloads))
        if gate and len(rows) % len(names) == 0:
            try:
                gate_point(rows[-len(names):], base)
            except DeadWeightError as exc:
                exc.rows = rows         # the caller still gets what it paid for
                raise

    if workers == 1:
        for payload in payloads:
            take(_task(payload))
        return rows
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(_task, payloads):
            take(row)
    return rows


# ---------------------------------------------------------------------------
#  The verdict
# ---------------------------------------------------------------------------

def _below(a: Mapping, b: Mapping) -> bool:
    """a's winrate interval lies wholly below b's."""
    return a["win_hi"] < b["win_lo"]


def _act_below(a: Mapping, b: Mapping) -> bool:
    for x, y in zip(a["acts"], b["acts"]):
        if x["hi"] < y["lo"]:
            return True
    return False


def classify(baseline: Mapping[str, Mapping],
             candidate: Mapping[str, Mapping]) -> str:
    """DOMINATING / DOMINATED / TRADE / INSEPARABLE, per the decision rule.

    Both arguments map a MEASURE cell name to its summary row. The control
    cell is not a term in the verdict -- it is checked separately, and a
    control that moved voids the whole sweep rather than changing a verdict.
    """
    shared = [c for c in candidate if c in baseline]
    if not shared:
        raise ValueError("no shared measurement cells to compare")
    up = any(_below(baseline[c], candidate[c]) for c in shared)
    down = any(_below(candidate[c], baseline[c]) for c in shared)
    act_down = any(_act_below(candidate[c], baseline[c]) for c in shared)
    act_up = any(_act_below(baseline[c], candidate[c]) for c in shared)
    if up and not (down or act_down):
        return "DOMINATING"
    if down and not (up or act_up):
        return "DOMINATED"
    if up or down or act_up or act_down:
        return "TRADE"
    return "INSEPARABLE"


ADOPTABLE = {"DOMINATING", "DOMINATED"}


def verdict_route(verdict: str) -> str:
    """Where a verdict goes. The taste / tuning line, as one function."""
    if verdict == "DOMINATING":
        return ("integration may adopt as TUNING -- after it reproduces at "
                "the confirm stage on the held-out seed, and with its own "
                "PILOT_WEIGHTS_VERSION bump")
    if verdict == "DOMINATED":
        return "integration may DISCARD; no [USER] act needed"
    if verdict == "TRADE":
        return "TASTE -> [USER] via QUEUE.md: this is one arm paid for by another"
    return ("TASTE -> [USER] via QUEUE.md, and the honest default is CHANGE "
            "NOTHING: the shipped vector is itself an inseparable point")


def taste_flags(point: Mapping[str, float],
                scope: WeightScope) -> list[str]:
    """Reasons a point is [USER]'s call whatever its verdict says."""
    base = scope.defaults
    out = []
    for name, value in sorted(point.items()):
        if name in scope.shared and value != base.get(name):
            out.append(f"{name} is SHARED -- moving it leaves 2A's window (D4)")
        if value == 0 and base.get(name) not in (0, 0.0):
            out.append(f"{name} -> 0 turns the term OFF: a design reversal, "
                       f"not a retune")
        if name == "BOMB_CONCENTRATION_STACK_CAP" and value != base.get(name):
            out.append("BOMB_CONCENTRATION_STACK_CAP is the pair's own "
                       "judgement call about marginal noise vs lethal waste")
    return out


# ---------------------------------------------------------------------------
#  Reporting
# ---------------------------------------------------------------------------

def _pct(x: float) -> str:
    return f"{100 * x:5.1f}%"


def format_rows(rows: Sequence[Mapping], scope: WeightScope) -> str:
    """The report, in GRID ORDER. Never sorted by outcome (look-first)."""
    base = scope.defaults
    out = []
    for row in rows:
        if "dead" in row:
            out.append(f"  {row['cell']:<18} REFUSED  {row['dead']}")
            continue
        delta = {k: v for k, v in row["values"].items() if v != base.get(k)}
        label = ("baseline" if not delta
                 else ", ".join(f"{k}={v}" for k, v in sorted(delta.items())))
        acts = " ".join(_pct(a["cleared_rate"]) for a in row["acts"])
        out.append(f"  {row['cell']:<18} win {_pct(row['win'])} "
                   f"[{_pct(row['win_lo'])},{_pct(row['win_hi'])}]  "
                   f"acts {acts}  {row['digest']}  {label}")
    return "\n".join(out)


def _by_point(rows: Sequence[Mapping]) -> list[tuple[tuple, dict]]:
    """Group rows by weight point, preserving grid order."""
    order: list[tuple] = []
    grouped: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(sorted(row["values"].items()))
        if key not in grouped:
            grouped[key] = {}
            order.append(key)
        grouped[key][row["cell"]] = row
    return [(k, grouped[k]) for k in order]


def control_is_still(rows: Sequence[Mapping]) -> tuple[bool, set[str]]:
    """Every point must produce ONE digest on the control cell.

    A moving control means a weight reached a character that carries neither
    op, which can only be a leak in this harness. The sweep is void, not
    merely suspect.
    """
    digests = {row["digest"] for row in rows
               if row.get("cell", "").endswith("null-control")
               and "digest" in row}
    return (len(digests) <= 1), digests


def format_verdicts(rows: Sequence[Mapping], scope: WeightScope) -> str:
    base = scope.defaults
    grouped = _by_point(rows)
    if not grouped:
        return "  (no rows)"
    measure = {n for n, (_c, _a, role) in CELL_SPECS.items()
               if role == "measure"}
    baseline_key = tuple(sorted(base.items()))
    baseline = dict(grouped[0][1])
    if grouped[0][0] != baseline_key:
        return "  (grid does not start at the shipped baseline; no verdicts)"
    b_cells = {k: v for k, v in baseline.items()
               if k.replace("w4-", "") in measure and "dead" not in v}
    out = []
    for key, cells_at_point in grouped[1:]:
        point = dict(key)
        c_cells = {k: v for k, v in cells_at_point.items()
                   if k.replace("w4-", "") in measure and "dead" not in v}
        if not c_cells:
            continue
        verdict = classify(b_cells, c_cells)
        delta = ", ".join(f"{k}={v}" for k, v in sorted(point.items())
                          if v != base.get(k)) or "baseline"
        out.append(f"  {verdict:<12} {delta}")
        out.append(f"               -> {verdict_route(verdict)}")
        for flag in taste_flags(point, scope):
            out.append(f"               !! TASTE: {flag}")
    return "\n".join(out) if out else "  (no comparable points)"


def _cost_line(stage: str, points: int, cells: int,
               seconds_per_run: float | None) -> str:
    runs, seed = STAGE_N[stage]
    total = points * cells * runs
    if seconds_per_run is None:
        cost = "run --stage coverage for a measured estimate"
    else:
        secs = total * seconds_per_run
        cost = f"~{secs / 60:.1f} min at {seconds_per_run * 1000:.1f} ms/run"
    return (f"  {stage:<9} n={runs:<5} seed={seed:<3} points={points:<4} "
            f"cells={cells}  {total:>8} runs  {cost}")


def format_plan(scope: WeightScope,
                seconds_per_run: float | None = None) -> str:
    screen = screen_points(scope)
    # WHAT AN UNRANGED NAME MEANS: discovered, live, and deliberately NOT
    # swept -- this harness does not invent a range for a term whose comment it
    # has not read. The one standing entry is `EXHAUST_FORMULA_PAYOUT_WEIGHT`
    # (W3 / R211), and its range is DEFERRED until the pilot valuation repairs
    # land, ruled [USER] 2026-08-25. Do not fill it in from this plan alone: a
    # weight swept while the scorer around it is under repair measures the
    # repair rather than the weight.
    unranged = [k for k in scope.pair_own
                if k not in RANGES and k not in PINNED]
    lines = [
        "W4 -- pilot-policy weight sweep, PLAN ONLY. Nothing was run.",
        "",
        scope.describe(),
    ]
    if unranged:
        lines += ["", "UNRANGED (discovered, no designed range -- NOT swept; "
                      "give it a RANGES row or leave it alone):"]
        lines += [f"    {name}" for name in sorted(unranged)]
    lines += ["", "cells:"]
    for name, (character, archetype, role) in CELL_SPECS.items():
        lines.append(f"    {name:<18} {character + '/' + archetype:<20} {role}")
    lines += ["", "stages:"]
    lines.append(_cost_line("coverage", 1, len(CELL_SPECS), seconds_per_run))
    lines.append(_cost_line("screen", len(screen), len(CELL_SPECS),
                            seconds_per_run))
    lines.append(_cost_line("search", SEARCH_POINTS + 1, len(CELL_SPECS),
                            seconds_per_run))
    lines.append(_cost_line("confirm", 2, len(CELL_SPECS), seconds_per_run))
    lines += ["", "decision rule: DOMINATING / DOMINATED are the integration's;",
              "               TRADE and INSEPARABLE are TASTE and go to [USER].",
              "               See this module's docstring for the full rule.",
              "", "no weight was changed, no live switch was flipped, and no",
              "cell was run. Add --execute --stage <name> inside 2A's window."]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
#  CLI
# ---------------------------------------------------------------------------

def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tier05.pilot_weight_sweep",
        description="W4: the EB-118 pilot-pair weight sweep harness.")
    p.add_argument("--execute", action="store_true",
                   help="actually run cells; without it the plan is printed "
                        "and nothing runs")
    p.add_argument("--stage", choices=sorted(STAGE_N),
                   help="which stage to execute")
    p.add_argument("--cell", action="append", dest="cells",
                   help="restrict to a registered cell (repeatable)")
    p.add_argument("--gate",
                   help="which engine switch to sweep, by gate function or "
                        "switch name. Default is the 2A pair's. ONE gate per "
                        "sweep -- each has its own activation window (R191).")
    p.add_argument("--jobs", type=int, default=0,
                   help="worker processes over (point, cell) TASKS; "
                        "0 = one per CPU, 1 = serial")
    p.add_argument("--axes", default="",
                   help="comma-separated axes for --stage search; "
                        "default is every ranged pair-own axis")
    p.add_argument("--point-json",
                   help="a JSON weight point, for --stage confirm")
    p.add_argument("--json", dest="json_out",
                   help="write the raw rows to this path (a temp artifact, "
                        "never committed prose)")
    p.add_argument("--no-gate", action="store_true",
                   help="report unread weights instead of refusing them. "
                        "Diagnostics only -- a sweep run this way is not "
                        "citable (R67).")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    scope = discover_scope(args.gate)

    if not args.execute:
        print(format_plan(scope))
        return 0
    if not args.stage:
        print("--execute needs --stage", file=sys.stderr)
        return 2

    gate = not args.no_gate
    if args.stage == "coverage":
        points = [scope.defaults]
        gate = False        # coverage is how the dead weights are FOUND
    elif args.stage == "screen":
        points = screen_points(scope)
    elif args.stage == "search":
        axes = ([a.strip() for a in args.axes.split(",") if a.strip()]
                or [a for a in scope.pair_own
                    if a in RANGES and a not in PINNED])
        points = search_points(scope, axes)
    else:
        if not args.point_json:
            print("--stage confirm needs --point-json", file=sys.stderr)
            return 2
        point = json.loads(Path(args.point_json).read_text(encoding="utf-8"))
        points = [scope.defaults, {**scope.defaults, **point}]

    def progress(done, total):
        print(f"  ... {done}/{total}", file=sys.stderr)

    refusal = None
    try:
        rows = run_stage(args.stage, points, args.cells, jobs=args.jobs,
                         gate=gate, baseline=scope.defaults,
                         switch=scope.gate.switch, progress=progress)
    except DeadWeightError as exc:
        rows = getattr(exc, "rows", [])
        refusal = str(exc)
    stamped = next((r["stamp"] for r in rows if "stamp" in r), "UNSTAMPED")

    print("=" * 78)
    print(f"W4 weight sweep -- stage {args.stage}, "
          f"gate {scope.gate.function} ({scope.gate.switch})")
    print(f"  {stamped}")
    print(f"  engineering tuning, not a registered experiment; "
          f"rows in grid order")
    print("=" * 78)
    print(format_rows(rows, scope))

    still, digests = control_is_still(rows)
    print("")
    if not digests:
        # Saying "the control held" about a control that never ran is the
        # one failure mode a validity check must not have.
        print("  control cell: NOT RUN -- this sweep has no validity check")
    elif not still:
        print(f"  CONTROL MOVED ({len(digests)} digests on null-control). "
              f"This sweep is VOID: a weight reached a character carrying "
              f"neither op, which can only be a leak in this harness.")
    else:
        print("  control cell: one digest across every point (as required)")

    if args.stage in ("screen", "search", "confirm"):
        print("")
        print("verdicts (decision rule in the module docstring):")
        print(format_verdicts(rows, scope))

    if args.stage == "coverage":
        print("")
        print("weight reads per cell. DEAD = not read at all (the R67 gate "
              f"will refuse it); thin = under the {POWER_FLOOR:.0%} power "
              "floor, readable but not separable at any affordable n.")
        for row in rows:
            if "reads" not in row:
                continue
            shares = read_shares(row)
            print(f"  {row['cell']:<20} {row['seconds'] / row['n']:.4f} s/run")
            for name in sorted(row["reads"]):
                count = row["reads"][name]
                share = shares.get(name, 0.0)
                print(f"      {power_label(share):<5} {name:<32} "
                      f"{count:>7}  {share:6.2%}")
        timed = [r for r in rows if r.get("n")]
        if timed:
            per_run = sum(r["seconds"] for r in timed) / sum(
                r["n"] for r in timed)
            print("")
            print("measured cost of the remaining stages "
                  "(serial-equivalent; divide by workers):")
            print(format_plan(scope, per_run).split("stages:\n", 1)[-1]
                  .split("\n\ndecision rule")[0])

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(rows, indent=2, sort_keys=True, default=str),
            encoding="utf-8")
        print(f"\n  rows -> {args.json_out}")

    if refusal is not None:
        print("")
        print(f"  REFUSED (R67): {refusal}")
        return 1
    return 0


if __name__ == "__main__":       # pragma: no cover
    raise SystemExit(main())
