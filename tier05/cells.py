"""The canonical cell object (R68, 2026-07-26).

The ratified cell -- "600 runs, seed 11, hunter, RT7 / DRAFTER 10 / POLICY 2
/ C3" -- was a sentence in a sprint doc and existed in no code object. Twelve
experiment scripts hand-rolled their own seeds (11 / 20260720 / 20260724 /
20260725 / 2000), three carried byte-identical argument parsers wrapped
around drifted `_arm()` copies, several resolved plan->pilot themselves
instead of asking `runner.resolve_plan`, and `print_run_report` printed no
version stamps at all. Every one of those is a way for two numbers to look
comparable while coming from different worlds.

`CANONICAL` is that sentence, as an object.

The version fields are NOT stored. They are read from the live stamps at
construction, so a Cell always describes the world it is about to run in --
when the R66 epoch landing bumps POLICY_VERSION to 3, the canonical cell
follows on its own and nothing has to remember to edit a literal here. The
one thing a Cell must never do is claim a world it is not in; that is the
mislabelling the ghost check was written to catch and then committed itself
one bump after it was written.

Usage:

    from tier05 import cells

    cell = cells.CANONICAL                       # the ratified cell
    cell = cells.CANONICAL.but(runs=200)         # a declared delta
    cell = cells.CANONICAL.but(character="klee", archetype="demolition")

    results = cell.run()
    print(cell.stamp())

`but()` is `dataclasses.replace` with plan validation: a Cell cannot be
built naming an archetype its character does not have, because
`resolve_plan` is the only path to a pilot (R68) and it fails loudly.
"""

from __future__ import annotations

import dataclasses
import statistics
from dataclasses import dataclass, field
from typing import Any

from tier0 import constants as C
from tier05 import draft, model


def _resolve_plan(character: str, archetype: str) -> tuple[str, str]:
    """runner.resolve_plan, imported at call time.

    R68 made runner.resolve_plan the single source of truth for plan->pilot,
    so this module has to reach back for it. Importing at call time rather
    than module scope keeps the module-level dependency one-way (cells ->
    runner); runner returns the favour by importing cells inside main().
    """
    from tier05 import runner
    return runner.resolve_plan(character, archetype)


@dataclass(frozen=True)
class Cell:
    """One reproducible measurement configuration.

    Frozen: a cell that mutates mid-experiment is a cell whose stamp lies
    about half its own rows. Derive variants with `but()`.
    """

    name: str
    character: str = "furina"
    archetype: str = "salon"
    runs: int = 600
    seed: int = 11
    route: str = "hunter"
    policy: str = "assigned"
    # The realistic power budget: relics granted and potions dropping/
    # bought/used. The ratified cell runs realistic -- a bare run is a
    # different world, not a cheaper sample of the same one.
    realistic: bool = True
    n_acts: int | None = None
    jobs: int = 0

    def __post_init__(self) -> None:
        # Fails loudly on an archetype the character does not have. This is
        # the single source of truth for plan->pilot (R68): scripts used to
        # pass `archetype` as its own pilot id directly, which worked right
        # up until a plan's pilot differed from its name.
        _resolve_plan(self.character, self.archetype)
        if self.policy not in draft.POLICIES:
            raise ValueError(
                f"unknown policy {self.policy!r}; choose one of "
                f"{', '.join(sorted(draft.POLICIES))}")

    # -- identity ---------------------------------------------------------

    @property
    def pilot(self) -> str:
        """The combat pilot for this cell's plan, via runner.resolve_plan."""
        return _resolve_plan(self.character, self.archetype)[1]

    @property
    def versions(self) -> dict[str, int]:
        """The LIVE world stamps, read at call time and never stored."""
        return {
            "RT": C.RUNTEMPLATE_VERSION,
            "D": C.DRAFTER_VERSION,
            "P": draft.POLICY_VERSION,
            "C": C.CONSTANTS_VERSION,
        }

    def stamp(self) -> str:
        """The mandatory report line (R68).

        A report without one of these is not citable in a sprint doc or a
        ruling. That is the whole point: the numbers this repo argues over
        are only comparable to each other when they name the world they came
        from, and for most of this project's life they did not.
        """
        v = self.versions
        return (f"cell={self.name} seed={self.seed} runs={self.runs} "
                f"RT{v['RT']}/D{v['D']}/P{v['P']}/C{v['C']}")

    def describe(self, subject: str | None = None,
                 varying: tuple[str, ...] = ()) -> str:
        """The human line that goes under the stamp.

        `subject` replaces the character/plan prefix for scripts that sweep
        several arms off one base cell. `varying` names any other field the
        script sweeps, and prints it as "(swept)" instead of the base cell's
        value. Both exist for the same reason: a multi-arm report that heads
        its table with whichever character or policy the base cell happened
        to hold is a header contradicting its own rows, which is worse than
        no header at all.
        """
        loadout = "relics + potions" if self.realistic else "bare"
        acts = "all registered acts" if self.n_acts is None \
            else f"{self.n_acts} act(s)"
        head = subject or f"{self.character}/{self.archetype} " \
                          f"(pilot {self.pilot})"
        def _f(name, shown):
            return "(swept)" if name in varying else shown
        return (f"{head}, route {_f('route', self.route)}, "
                f"policy {_f('policy', self.policy)}, "
                f"{_f('realistic', loadout)}, {_f('n_acts', acts)}")

    # -- derivation -------------------------------------------------------

    def but(self, **deltas: Any) -> Cell:
        """A declared delta from this cell.

        Named `but` rather than `replace` because that is how the deltas
        read at the call site -- `CANONICAL.but(runs=200)` says "the
        ratified cell, but shorter", which is exactly the claim a reader
        needs to check. An undeclared copy with three fields edited says
        nothing.
        """
        unknown = set(deltas) - {f.name for f in dataclasses.fields(self)}
        if unknown:
            raise TypeError(f"Cell has no field(s): {', '.join(sorted(unknown))}")
        if "name" not in deltas:
            # A derived cell that kept the canonical name would stamp its
            # rows as the ratified cell. Force the divergence into the name.
            delta_desc = ",".join(f"{k}={deltas[k]}" for k in sorted(deltas))
            deltas = dict(deltas, name=f"{self.name}[{delta_desc}]")
        return dataclasses.replace(self, **deltas)

    # -- execution --------------------------------------------------------

    def run(self) -> list:
        """Run the cell. Returns model.run_many's results, untouched."""
        return model.run_many(
            self.character, self.archetype, self.pilot,
            draft.POLICIES[self.policy], self.runs, self.seed,
            grant_relics=self.realistic, grant_potions=self.realistic,
            n_acts=self.n_acts, jobs=self.jobs, route_name=self.route)

    def arm(self) -> dict:
        """Run the cell and reduce it to the standard summary row.

        THE consolidated `_arm()`. Three copies of this existed
        (exp_roster_anchors, exp_furina_ghostcheck, exp_free_draft_cell) and
        they had drifted: each computed a slightly different set of fields
        off the same results, so a row from one was not quite a row from
        another even at identical settings.

        `fights` is here because under RUNTEMPLATE 6+ it is a VARIABLE, not
        a template constant: a route decides how many fights a run takes and
        a deck that dies early gets fewer. Any per-combat rate quoted off an
        arm has to be rescaled against this rather than against a fixed
        number that no longer exists.
        """
        results = self.run()
        decks = [list(r.deck_ids) for r in results]
        n = len(results)
        return {
            "results": results,
            "decks": decks,
            "win": sum(r.won for r in results) / n,
            # acts_completed counts boss wins, so >= 1 IS the act-1 clear.
            "act1": sum(r.acts_completed >= 1 for r in results) / n,
            "acts": statistics.mean(r.acts_completed for r in results),
            "decksize": statistics.mean(len(d) for d in decks),
            "fights": statistics.mean(len(r.fight_stats) for r in results),
        }


# The ratified cell (R68). 600 runs, seed 11, hunter, realistic loadout, at
# whatever RT/D/P/C the tree currently stamps.
CANONICAL = Cell(name="canonical")


#: Flags the shared experiment parser understands, and the Cell field each
#: one overrides. Deliberately small: an experiment script's job is to run
#: ONE declared configuration, so anything beyond "shorter", "elsewhere" and
#: "faster" belongs in the script's own Cell literal where a reader can see
#: it, not on a command line where it vanishes from the record.
_OVERRIDE_FLAGS = {
    "--runs": ("runs", int),
    "--seed": ("seed", int),
    "--route": ("route", str),
    "--jobs": ("jobs", int),
}


def parse_overrides(argv: list[str], base: Cell) -> tuple[Cell, list[str]]:
    """Apply `--runs/--seed/--route/--jobs` from argv to `base`.

    Returns the derived cell and the surviving arguments. This replaces
    three byte-identical hand-rolled parsers that had been copied between
    experiment scripts (audit §2.6) -- byte-identical at the time they were
    copied, which is exactly how the `_arm()` bodies they wrapped came to
    drift without anyone noticing they had.

    Overrides go through `Cell.but()`, so an overridden cell renames itself
    and its stamp stops claiming to be the cell it was derived from.
    """
    args = list(argv)
    deltas: dict[str, Any] = {}
    for flag, (fieldname, cast) in _OVERRIDE_FLAGS.items():
        if flag in args:
            i = args.index(flag)
            if i + 1 >= len(args):
                raise SystemExit(f"{flag} needs a value")
            deltas[fieldname] = cast(args[i + 1])
            del args[i:i + 2]
    return (base.but(**deltas) if deltas else base), args


def print_header(cell: Cell, title: str, subject: str | None = None,
                 varying: tuple[str, ...] = ()) -> None:
    """The standard experiment banner: title, stamp, then the description.

    Stamp BEFORE the description, because the stamp is the part that has to
    survive being pasted into a doc on its own.
    """
    print("=" * 78)
    print(title)
    print(f"  {cell.stamp()}")
    print(f"  {cell.describe(subject, varying)}")
    print("=" * 78)
