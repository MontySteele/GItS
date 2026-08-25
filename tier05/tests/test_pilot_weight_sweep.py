"""W4: the weight-sweep harness, and the three claims it has to earn.

The claims, in the order the file makes them:

  DETERMINISM       the same weight point twice is the same set of runs, and
                    a search grid is reproducible from its seed.
  SANDBOX ISOLATION the harness forces the pair ON in its own process and puts
                    everything back -- the switch, the weights, and their
                    TYPES -- out of an exception as well as a clean exit.
  SWITCH-OFF        with the switch off, two wildly different weight vectors
  BYTE-IDENTITY     produce byte-identical runs. This file holds the proof at
                    the run level rather than at the call site
                    (`test_eb118_switch_off` holds the call-site half).

Every claim carries its POSITIVE CONTROL. "Nothing moved" is only evidence
when the same harness can be shown moving something under the same conditions
-- otherwise a harness that did nothing at all would pass every test here.

WHAT THE PHASE-2A FLIP DID TO THIS FILE (2026-08-24, `POLICY_VERSION` 8,
`PILOT_WEIGHTS_VERSION` 3). `policy.PILOT_POLICIES_ENABLED` shipped False when
these tests were written, so two kinds of line here were reading the shipped
default and calling it something else:

  * `assert policy.PILOT_POLICIES_ENABLED is False` after a sandbox was never
    a claim about the value False -- it is the RESTORATION claim, that the
    sandbox puts back whatever it found. It is asserted against
    `SHIPPED_SWITCH` below, captured at import before any sandbox has run,
    which is what it always meant and survives the next flip too.
  * the byte-identity arm's `force=False` used to leave the switch off because
    off was where it shipped. It now leaves it ON, so those tests hold the
    switch off explicitly. THE CLAIM IS UNCHANGED AND IS NOT RETIRED BY THE
    FLIP: it is what proves a weight reaches the engine only through the gate,
    and the pre-policy path is still live code behind that gate.

Cells run at 6 runs. That is far too small to say anything about a winrate and
is not asked to: every assertion below is about IDENTITY (a digest) or about
arithmetic, never about an outcome.
"""

from __future__ import annotations

import pytest

from tier0.engine.state import Bomb, Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state
from tier05 import pilot_weight_sweep as w4

PLACE_5 = {"op": "place_bomb", "amount": 1, "target": "enemy",
           "bomb_damage": 5}

#: The switch as the tree SHIPS it, read once at import and before any sandbox
#: has run. Every restoration assertion below compares against this rather than
#: against a literal: the sandbox's promise is "whatever I found, I put back",
#: and a literal turns that promise into a statement about the value of the day
#: -- which went stale the moment Phase 2A flipped it True.
SHIPPED_SWITCH = policy.PILOT_POLICIES_ENABLED


@pytest.fixture(scope="module")
def scope():
    return w4.discover_scope()


@pytest.fixture
def switch_off(monkeypatch):
    """Hold the pre-policy path down for a test's own duration.

    Before Phase 2A this was the shipped state and the byte-identity tests got
    it for free from `force=False`. Naming it is what keeps those tests about
    the gate instead of about the default.
    """
    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", False)


@pytest.fixture
def wild(scope):
    """A weight vector as far from the shipped one as the ranges reach."""
    point = dict(scope.defaults)
    point.update({
        "BOMB_LETHAL_WASTE_WEIGHT": 0.0,
        "BOMB_CONCENTRATION_VALUE": 6.0,
        "BOMB_CONCENTRATION_STACK_CAP": 1,
        "BOMB_SUPPRESSION_VALUE": 0.0,
        "BOMB_READER_LETHAL_POP_VALUE": 0.0,
        "BOMB_EARLY_POP_PENALTY": 6.0,
        "BOMB_MOVE_READER_AIM_VALUE": 2.0,
        "EXHAUST_COST_EFFICIENCY_WEIGHT": 0.0,
        "EXHAUST_SELF_EXHAUST_DISCOUNT": 1.0,
        # W3 (R211): the formula-aware payout's weight joins the gate's
        # surface, so a vector that ignored it would no longer be "as far
        # from the shipped one as the ranges reach". 0.0 is the DEGENERATE
        # case rather than an invented range end -- at zero the hook pays
        # nothing and the chooser is identity-blind again, which is the
        # property its own tests pin.
        "EXHAUST_FORMULA_PAYOUT_WEIGHT": 0.0,
    })
    return point


def _cell(name, runs=6, seed=11):
    return w4.registered_cells([name], runs=runs, seed=seed)[name]


# ---------------------------------------------------------------------------
#  Discovery -- the scope is read off source, never declared here
# ---------------------------------------------------------------------------

#: The eight weights `bomb_placement_score` reads. In scope until `C18`, out
#: of it since -- named here so the change is assertable in both directions
#: rather than merely absent.
BOMB_WEIGHTS = ("BOMB_LANDED_DAMAGE_VALUE", "BOMB_LETHAL_WASTE_WEIGHT",
                "BOMB_CONCENTRATION_VALUE", "BOMB_CONCENTRATION_STACK_CAP",
                "BOMB_SUPPRESSION_VALUE", "BOMB_READER_LETHAL_POP_VALUE",
                "BOMB_EARLY_POP_PENALTY", "BOMB_MOVE_READER_AIM_VALUE")


def test_the_entry_points_are_the_engines_own_call_sites(scope):
    """ONE entry point since `C18`, and the harness found that by itself.

    `EB-136` / R210 bound every `target: enemy` op of a card to a single aim
    taken at card-play construction, and `place_bomb` is one of the emitter's
    `AIMING_OPS` -- so `_op_place_bomb` stopped asking `bomb_placement_target`
    where the bomb goes and reads the play's bound target like every other
    aimed row. The chooser is still in `policy.py`, unedited; the ENGINE no
    longer calls it, which is exactly what "derived from source, never a
    hard-coded list" exists to notice.
    """
    assert scope.entry_points == ("exhaust_victim",)
    assert scope.gate.switch == "PILOT_POLICIES_ENABLED"


def test_gates_are_found_structurally_not_by_name():
    """`EB-118` ships more than one switch on purpose: R191 gave the 2C mode
    chooser its own so that flipping the 2A pair does not silently activate
    mode valuation inside 2A's window. A harness that hard-coded the pair's
    gate name would go on sweeping eleven weights while 2C's landed beside
    them, unswept and unreported."""
    synthetic = (
        "def _pilot_policies():\n"
        "    from tier0.pilot import policy\n"
        "    return policy if policy.PILOT_POLICIES_ENABLED else None\n"
        "\n"
        "def _mode_chooser():\n"
        "    from tier0.pilot import policy\n"
        "    return policy if policy.MODE_CHOOSER_ENABLED else None\n"
        "\n"
        "def _not_a_gate(state):\n"
        "    return state if state.turn else None\n")
    gates = w4.discover_gates(synthetic)
    assert gates == (w4.Gate("_mode_chooser", "MODE_CHOOSER_ENABLED"),
                     w4.Gate("_pilot_policies", "PILOT_POLICIES_ENABLED"))


def test_the_live_engine_gate_is_discovered_from_the_live_engine():
    gates = w4.discover_gates(
        w4.EFFECTS_SOURCE.read_text(encoding="utf-8"))
    assert w4.Gate("_pilot_policies", "PILOT_POLICIES_ENABLED") in gates


def test_a_sweep_is_one_gate_and_an_unknown_gate_is_refused():
    with pytest.raises(KeyError):
        w4.discover_scope("_no_such_gate")


def test_a_switch_is_never_mistaken_for_a_weight(scope):
    assert "PILOT_POLICIES_ENABLED" not in scope.pair_own
    assert "PILOT_POLICIES_ENABLED" not in scope.shared


def test_a_third_gated_chooser_is_discovered_without_editing_this_harness():
    """2C adds a mode-valuation chooser behind the SAME switch, in another
    worktree. A hard-coded entry list here would silently stop covering the
    file this harness claims to sweep; source discovery does not.
    """
    synthetic = (
        "def _op_choose_mode(state, fx, card):\n"
        "    pol = _pilot_policies()\n"
        "    if pol is not None:\n"
        "        return pol.mode_choice(state, fx, card)\n"
        "    return 0\n")
    assert w4.entry_points_from_source(synthetic) == ("mode_choice",)


def test_the_pair_weights_are_pair_own(scope):
    for name in ("EXHAUST_COST_EFFICIENCY_WEIGHT", "EXHAUST_JUNK_BONUS",
                 "EXHAUST_SELF_EXHAUST_DISCOUNT"):
        assert name in scope.pair_own, name
        assert getattr(policy, name) == scope.pair_own[name]


def test_the_bomb_weights_left_the_sweep_when_the_engine_stopped_reading_them(
        scope):
    """R33's dead-knob law, applied to the harness rather than to a result.

    `EB-136` / R210 (`C18`) bound `place_bomb target: enemy` to the play's one
    aim, so no engine path reaches `bomb_placement_score` any more. A sweep
    that kept sweeping these eight would report a null on every cell and
    would be unable to show the swept constant was READ even once -- which is
    the exact failure R33's exercise counter exists to catch. They are out of
    `pair_own` and out of `shared`; the constants themselves stand untouched
    in `policy.py`, waiting on the destination-scoring question `EB-136`
    severed.
    """
    for name in BOMB_WEIGHTS:
        assert name not in scope.pair_own, name
        assert name not in scope.shared, name
        assert hasattr(policy, name), name


def test_a_weight_the_main_scorer_also_reaches_is_shared_not_swept(scope):
    """`exhaust_future_value` reaches `PILOT_COMPANION_COPY_VALUE` through
    `_tempo_value` -- and so does `_score`. Moving it would move draft scoring
    as well as the chooser, which is a second variable in 2A's window (D4)."""
    assert "PILOT_COMPANION_COPY_VALUE" in scope.shared
    assert "PILOT_COMPANION_COPY_VALUE" not in scope.pair_own
    assert "PILOT_COMPANION_COPY_VALUE" not in w4.screen_points(scope)[1]


def test_furinas_stoker_weights_are_out_of_scope_entirely(scope):
    """The stoker is a different pilot surface, not behind this switch."""
    for name in ("STOKE_DEPLOY_OPEN", "STOKE_FUEL_HUNGRY",
                 "STOKE_RUNWAY_TURNS", "ENRAGE_TAX_TURNS"):
        assert name not in scope.pair_own
        assert name not in scope.shared


def test_an_unranged_weight_is_named_in_the_plan_and_not_swept():
    """The 2C overlap, handled without red-lighting anyone else's suite.

    A weight that arrives in the gated closure with no designed range is
    REPORTED as UNRANGED, not silently ignored and not swept at a range this
    file invented for a comment it has not read.
    """
    scope = w4.WeightScope(entry_points=("x",),
                           pair_own={"MODE_OVERDRAW_PENALTY": 1.0},
                           shared={})
    plan = w4.format_plan(scope)
    assert "UNRANGED" in plan
    assert "MODE_OVERDRAW_PENALTY" in plan
    assert w4.screen_points(scope) == [{"MODE_OVERDRAW_PENALTY": 1.0}]


# ---------------------------------------------------------------------------
#  Sandbox isolation
# ---------------------------------------------------------------------------

def test_importing_the_harness_arms_nothing():
    """Importing the harness neither flips the switch nor arms a weight: the
    switch reads exactly as the tree ships it, and the weight is a plain
    float rather than one of the counting subclasses."""
    assert policy.PILOT_POLICIES_ENABLED is SHIPPED_SWITCH
    assert type(policy.BOMB_LANDED_DAMAGE_VALUE) is float


def test_the_switch_and_the_weights_come_back_after_an_exception(scope):
    before = {k: getattr(policy, k) for k in scope.defaults}
    with pytest.raises(RuntimeError):
        with w4.sandbox({"BOMB_CONCENTRATION_VALUE": 99.0}):
            assert policy.PILOT_POLICIES_ENABLED is True
            assert policy.BOMB_CONCENTRATION_VALUE == 99.0
            raise RuntimeError("mid-cell")
    assert policy.PILOT_POLICIES_ENABLED is SHIPPED_SWITCH
    for name, value in before.items():
        restored = getattr(policy, name)
        assert restored == value
        # TYPE as well as value: a counted subclass left behind in a live
        # module would keep tallying into the next sweep's numbers, and would
        # be invisible at every call site.
        assert type(restored) in (int, float), name


def test_the_switch_comes_back_OFF_when_that_is_what_it_found(switch_off,
                                                             scope):
    """The restoration claim in the direction that can actually regress.

    Until Phase 2A this was the same test as the one above, because off was
    the shipped state. Now that the tree ships ON, a sandbox that simply left
    the switch alone would pass that one -- so the off side is asserted on its
    own, held down explicitly.
    """
    with pytest.raises(RuntimeError):
        with w4.sandbox({"BOMB_CONCENTRATION_VALUE": 99.0}):
            assert policy.PILOT_POLICIES_ENABLED is True
            raise RuntimeError("mid-cell")
    assert policy.PILOT_POLICIES_ENABLED is False


def test_a_typod_weight_is_refused_rather_than_swept_as_nothing():
    with pytest.raises(AttributeError) as excinfo:
        with w4.sandbox({"BOMB_LANDED_DAMGE_VALUE": 1.0}):
            pass                                    # pragma: no cover
    assert "R67" in str(excinfo.value)
    assert policy.PILOT_POLICIES_ENABLED is SHIPPED_SWITCH


def test_the_sandbox_reports_whether_it_had_to_force_the_switch(monkeypatch):
    """`forced` answers "did I have to turn it on", which is a fact about the
    switch the sandbox FOUND -- so since Phase 2A shipped it ON, the shipped
    tree's answer is False. Both sides are asserted rather than the one that
    happens to be shipping, which is the whole reason the field exists: a
    caller must never have to assume what state it inherited."""
    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", False)
    with w4.sandbox({}) as state:
        assert state.forced is True
    with w4.sandbox({}, force=False) as state:
        assert state.forced is False

    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", True)
    with w4.sandbox({}) as state:
        assert state.forced is False        # already on: nothing to force
    with w4.sandbox({}, force=False) as state:
        assert state.forced is False


def test_the_sandbox_forces_exactly_the_switch_it_was_given(monkeypatch):
    """One gate per sweep. Forcing every switch found would run two
    activation windows through one measurement, which is the arrangement
    R191 split the mode chooser out of the pair's flag to prevent."""
    monkeypatch.setattr(policy, "OTHER_SWITCH_PROBE", False, raising=False)
    with w4.sandbox({}, switch="OTHER_SWITCH_PROBE"):
        assert policy.OTHER_SWITCH_PROBE is True
        # Untouched, whatever it happens to be: forcing the named switch must
        # not reach the pair's.
        assert policy.PILOT_POLICIES_ENABLED is SHIPPED_SWITCH
    assert policy.OTHER_SWITCH_PROBE is False
    with pytest.raises(AttributeError):
        with w4.sandbox({}, switch="NO_SUCH_SWITCH"):
            pass                                    # pragma: no cover


def test_counted_weights_are_numerically_invisible():
    armed = w4._arm_value("BOMB_CONCENTRATION_VALUE", 2.0)
    assert armed == 2.0
    assert type(3.0 * armed) is float
    assert type(armed * 3) is float
    assert type(-armed) is float
    assert w4._arm_value("BOMB_CONCENTRATION_STACK_CAP", 3) == 3
    assert min(5, w4._arm_value("BOMB_CONCENTRATION_STACK_CAP", 3)) == 3


def test_reads_are_counted_on_the_real_read_path():
    """No `policy.py` edit and no self-report: the count comes off genuine
    arithmetic inside `bomb_placement_score` (R33's exercise-counter law).

    Armed from an EXPLICIT mapping rather than from `scope.defaults` since
    `C18`: the engine no longer reaches these eight (R210 bound `place_bomb`),
    so they are out of the discovered scope. The claim this test makes is
    about the COUNTER, not about the sweep's membership -- it has to keep
    holding on a function the harness can still be pointed at by hand, or the
    exercise counter has no proof it counts real arithmetic at all.
    """
    low, high = make_enemy(hp=3, name="low"), make_enemy(hp=60, name="high")
    state = make_state([low, high])
    armed = {name: getattr(policy, name) for name in BOMB_WEIGHTS}
    with w4.sandbox(armed) as sb:
        policy.bomb_placement_score(state, PLACE_5, high)
    assert sb.reads["BOMB_LANDED_DAMAGE_VALUE"] > 0
    assert sb.reads["BOMB_LETHAL_WASTE_WEIGHT"] > 0
    # A board with no existing pile never reaches the concentration term.
    assert sb.reads["BOMB_CONCENTRATION_VALUE"] == 0


# ---------------------------------------------------------------------------
#  Switch-off byte-identity, with its positive control
# ---------------------------------------------------------------------------

@pytest.mark.battery
@pytest.mark.parametrize("cell_name", ["bomb-primary", "exhaust-primary"])
def test_switch_off_is_byte_identical_across_two_wild_vectors(
        switch_off, scope, wild, cell_name):
    """The gate claim, at the RUN level.

    With the switch off the engine never reaches a weight, so the whole grid
    collapses to one set of runs. Before Phase 2A this was the inertness
    property that let the pair sit in HEAD without re-baselining anything;
    after the flip it is the same fact doing a different job -- proof that a
    weight reaches the engine ONLY through the gate, which is what the
    sandbox's `force=False` arm relies on and what makes a moving null control
    diagnostic rather than mysterious.
    """
    cell = _cell(cell_name)
    a = w4.evaluate(cell, scope.defaults, force=False)["digest"]
    b = w4.evaluate(cell, wild, force=False)["digest"]
    assert a == b


@pytest.mark.battery
@pytest.mark.parametrize("cell_name,runs", [("exhaust-primary", 14)])
def test_the_positive_control_the_previous_test_needs(switch_off, scope, wild,
                                                      cell_name, runs):
    """Without this, a harness that ran nothing would pass the test above.

    Forcing the switch ON moves the cell, and moving the weights under it
    moves the cell again.

    THE BOMB CELL LEFT THIS CONTROL AT `C18` (`EB-136` / R210) and its
    inertness is pinned in its own right below, which is the honest place for
    it: the gate's Klee half no longer HAS a decision to move, because
    `_op_place_bomb` reads the play's bound aim instead of asking
    `bomb_placement_target`. Leaving `bomb-primary` parametrized here would
    have turned a positive control into a standing red light for a behaviour
    change the ruling asked for; deleting the row without replacing it would
    have lost the fact. Both halves of the byte-identity claim above still run
    on both cells -- on the bomb cell it now holds trivially, which is exactly
    what the new pin says out loud.

    THE EXHAUST CELL NEEDS TEN RUNS, NOT SIX, SINCE R208 / W2b (2026-08-25),
    and the reason is content rather than harness. This control has no power
    unless the sampled runs actually CONTAIN a chosen-exhaust decision the
    wild vector flips. W2b re-bodied `depths_judgment` off its exhaust-pile
    slope and revised `undertow`, which moves what a kokomi/priest deck
    drafts and therefore how often it reaches that decision; at six runs the
    wild vector stopped changing the digest. Six -> ten restores the control
    and the gate claim it backstops is unchanged. This is a POWER number for
    a control, not a threshold anything is measured against -- swept cells
    run at `STAGE_N`, which is 40 to 2000.

    TEN -> FOURTEEN SINCE W3 (EB-118 Phase 3, R211, 2026-08-25), for the SAME
    reason and by the same kind of measurement. W3 re-bodied all three of the
    Kokomi rows this cell drafts around -- `pearl_barrage` off its
    exhaust-pile slope onto a selection-cost one, `shell_of_sanctuary` into a
    cost-1 retriever, `the_tide_remembers` into a wide selection-cost attack
    -- which moves what a kokomi/priest deck drafts and therefore how often
    the sampled runs reach a chosen-exhaust decision the wild vector flips.
    Measured on the real harness at 10/12/14/16/20/24/30 runs: the wild vector
    does not move the digest at 10 or 12 and does move it at 14 and at every
    count above. Ten -> fourteen restores the control; the gate claim it
    backstops is unchanged.

    THE WILD VECTOR ALSO GREW ONE ENTRY IN THE SAME WINDOW, and that is not
    one fix wearing two hats: `EXHAUST_FORMULA_PAYOUT_WEIGHT` joined the
    gate's DISCOVERED surface (see `_closure`), so a vector leaving it at its
    shipped value was no longer "as far from the shipped one as the ranges
    reach". Adding it did NOT on its own restore the control -- the run count
    did -- and both changes are kept because both were separately wrong.
    """
    cell = _cell(cell_name, runs=runs)
    off = w4.evaluate(cell, scope.defaults, force=False)["digest"]
    on = w4.evaluate(cell, scope.defaults)["digest"]
    on_wild = w4.evaluate(cell, wild)["digest"]
    assert on != off
    assert on_wild != on


@pytest.mark.battery
def test_the_shipped_switch_is_the_on_side_of_that_pair(scope):
    """Which side of the pair above the tree actually ships, asserted where
    the harness can see it: `force=False` is the OFF comparator only while
    someone holds the switch down, and since Phase 2A nobody does by default.

    READ ON THE EXHAUST CELL SINCE `C18`. It used to read on `bomb-primary`,
    which since `EB-136` / R210 carries no gated decision at all and would
    therefore agree with itself whichever side shipped -- a claim about the
    default that a cell with nothing behind the gate cannot make.
    """
    assert policy.PILOT_POLICIES_ENABLED is True
    cell = _cell("exhaust-primary", runs=10)
    assert (w4.evaluate(cell, scope.defaults, force=False)["digest"]
            == w4.evaluate(cell, scope.defaults)["digest"])


@pytest.mark.battery
@pytest.mark.parametrize("cell_name", ["bomb-primary", "bomb-secondary"])
def test_the_bomb_cells_carry_no_gated_decision_since_the_binding(
        switch_off, scope, wild, cell_name):
    """`C18` (`EB-136` / R210) emptied the 2A pair's KLEE half, and this is
    where that is written down rather than inferred from a deleted row.

    `_op_place_bomb` used to ask `bomb_placement_target` where each bomb went;
    it now reads the play's ONE bound aim, because `place_bomb` is one of the
    emitter's `AIMING_OPS` and the mod puts every bomb of a placement on
    `cardPlay.Target`. So on a Klee cell the gate has nothing behind it: the
    switch may be off, forced on, or forced on at a wild vector, and all three
    are one digest. That is the same shape as the Furina null control below --
    which is the point. `CELL_SPECS` still calls these rows `measure`; they
    are only carriers again if the destination-scoring question `EB-136`
    severed is answered by putting a chooser back at BIND time.
    """
    cell = _cell(cell_name)
    digests = {
        w4.evaluate(cell, scope.defaults, force=False)["digest"],
        w4.evaluate(cell, scope.defaults)["digest"],
        w4.evaluate(cell, wild)["digest"],
    }
    assert len(digests) == 1


@pytest.mark.battery
def test_the_null_control_cell_never_moves(switch_off, scope, wild):
    """Furina carries neither op. Every point must land on one digest here,
    with the switch off OR forced on -- a moving control can only be a leak
    in this harness, and voids the sweep rather than shading a verdict."""
    cell = _cell("null-control")
    digests = {
        w4.evaluate(cell, scope.defaults, force=False)["digest"],
        w4.evaluate(cell, scope.defaults)["digest"],
        w4.evaluate(cell, wild)["digest"],
    }
    assert len(digests) == 1


# ---------------------------------------------------------------------------
#  Determinism
# ---------------------------------------------------------------------------

def test_the_same_point_twice_is_the_same_runs(scope):
    cell = _cell("bomb-primary")
    first = w4.evaluate(cell, scope.defaults)
    second = w4.evaluate(cell, scope.defaults)
    assert first["digest"] == second["digest"]
    assert first["win"] == second["win"]
    assert first["acts"] == second["acts"]


def test_cells_are_pinned_to_one_job(scope):
    """`run_many(jobs>1)` spreads a batch over worker processes that re-import
    `tier0.pilot.policy`, which would run the SHIPPED weights while the parent
    believed it was sweeping. The parallelism lives one level up instead."""
    for cell in w4.registered_cells(runs=6, seed=11).values():
        assert cell.jobs == 1


def test_a_search_grid_is_reproducible_from_its_seed(scope):
    axes = ["BOMB_LETHAL_WASTE_WEIGHT", "BOMB_CONCENTRATION_VALUE"]
    a = w4.search_points(scope, axes, count=12, seed=7)
    b = w4.search_points(scope, axes, count=12, seed=7)
    c = w4.search_points(scope, axes, count=12, seed=8)
    assert a == b
    assert a != c
    assert a[0] == scope.defaults          # point zero is always the baseline
    assert len({tuple(sorted(p.items())) for p in a}) == len(a)


def test_the_screen_moves_exactly_one_axis_per_point(scope):
    points = w4.screen_points(scope)
    assert points[0] == scope.defaults
    for point in points[1:]:
        moved = [k for k, v in point.items() if v != scope.defaults[k]]
        assert len(moved) == 1
        assert moved[0] not in w4.PINNED
        assert point[moved[0]] in w4.RANGES[moved[0]]


def test_the_numeraire_is_never_swept(scope):
    """A `PINNED` axis is held at its shipped value wherever it is in scope.

    Stated over `PINNED` rather than over the one name in it since `C18`: the
    bomb numeraire left the discovered scope with the rest of its vector when
    R210 bound `place_bomb`, and a test that named it directly would have gone
    green-by-absence on a grid that had stopped containing it. The property is
    also exercised on a scope that DOES hold it, below, so this arm cannot
    pass vacuously.
    """
    for point in w4.screen_points(scope):
        for name in w4.PINNED:
            if name in point:
                assert point[name] == scope.defaults[name]

    pinned = {name: getattr(policy, name) for name in w4.PINNED}
    held = w4.WeightScope(entry_points=("x",),
                          pair_own=dict(pinned,
                                        BOMB_LETHAL_WASTE_WEIGHT=1.0),
                          shared={})
    points = w4.screen_points(held)
    assert len(points) > 1, "the control grid has to actually sweep something"
    for point in points:
        for name, value in pinned.items():
            assert point[name] == value


def test_the_bomb_vector_is_scale_invariant_which_is_why_it_is_pinned(scope):
    """`bomb_placement_score` is a sum of terms each linear in one weight, so
    scaling every VALUE weight by k > 0 scales every candidate's score by k
    and leaves the argmax where it was. One axis therefore has to be the unit
    or the grid spends its compute re-measuring the same decisions.

    The integer stack CAP is a count, not a value, and is held fixed.
    """
    scaled = {k: (v if k == "BOMB_CONCENTRATION_STACK_CAP" else v * 2.0)
              for k, v in scope.defaults.items() if k.startswith("BOMB_")}
    for hp_a, hp_b, bombs in ((30, 31, ()), (8, 40, (5,)), (60, 12, (5, 5))):
        a = make_enemy(hp=hp_a, name="a")
        b = make_enemy(hp=hp_b, name="b")
        b.bombs = [Bomb(damage=d, element="pyro", turn_placed=0)
                   for d in bombs]
        state = make_state([a, b])
        state.player.hand = [Card(id="det", name="det", cost=1, type="skill",
                                  effects=[{"op": "detonate",
                                            "target": "enemy"}])]
        with w4.sandbox(scope.defaults):
            plain = policy.bomb_placement_target(state, PLACE_5).name
        with w4.sandbox({**scope.defaults, **scaled}):
            doubled = policy.bomb_placement_target(state, PLACE_5).name
        assert plain == doubled, (hp_a, hp_b, bombs)


# ---------------------------------------------------------------------------
#  The R67 gate, at the level the question is actually asked
# ---------------------------------------------------------------------------

def _row(cell, values, reads):
    return {"cell": cell, "values": values, "reads": reads}


def test_the_gate_refuses_an_axis_no_measurement_cell_read():
    base = {"EXHAUST_JUNK_BONUS": 6.0}
    group = [_row("w4-exhaust-primary", {"EXHAUST_JUNK_BONUS": 12.0},
                  {"EXHAUST_JUNK_BONUS": 0}),
             _row("w4-exhaust-secondary", {"EXHAUST_JUNK_BONUS": 12.0},
                  {"EXHAUST_JUNK_BONUS": 0})]
    with pytest.raises(w4.DeadWeightError) as excinfo:
        w4.gate_point(group, base)
    message = str(excinfo.value)
    assert "instrument error" in message
    assert "R33" in message                 # do not fix this by adding a read


def test_the_gate_passes_an_axis_some_cell_did_read():
    """Positive control. A gate that refused everything would look identical
    to a working one from the negative test alone."""
    base = {"BOMB_LETHAL_WASTE_WEIGHT": 1.0}
    group = [_row("w4-bomb-primary", {"BOMB_LETHAL_WASTE_WEIGHT": 2.0},
                  {"BOMB_LETHAL_WASTE_WEIGHT": 9968}),
             _row("w4-exhaust-primary", {"BOMB_LETHAL_WASTE_WEIGHT": 2.0},
                  {"BOMB_LETHAL_WASTE_WEIGHT": 0})]
    w4.gate_point(group, base)              # a bomb axis is dead in a Kokomi
                                            # cell BY CONSTRUCTION, not by fault


def test_the_gate_says_nothing_about_the_baseline_point():
    base = {"BOMB_LETHAL_WASTE_WEIGHT": 1.0}
    group = [_row("w4-bomb-primary", dict(base),
                  {"BOMB_LETHAL_WASTE_WEIGHT": 0})]
    w4.gate_point(group, base)


def test_the_control_cell_is_not_a_term_in_the_gate():
    base = {"BOMB_LETHAL_WASTE_WEIGHT": 1.0}
    group = [_row("w4-null-control", {"BOMB_LETHAL_WASTE_WEIGHT": 2.0},
                  {"BOMB_LETHAL_WASTE_WEIGHT": 0})]
    w4.gate_point(group, base)


def test_the_gate_fires_end_to_end_on_the_first_offending_point(
        scope, monkeypatch):
    """The whole loop, on real cells: `EXHAUST_JUNK_BONUS` is unreachable
    behind Kokomi's rotation law, so the sweep is refused rather than printing
    a table of rows identical to the baseline for a reason that has nothing to
    do with the weight.

    Refusal lands on the point that earned it, not after the grid --
    `sweeps.sweep`'s rule, for its reason: there is nothing to learn from
    finishing a dead-axis sweep.
    """
    monkeypatch.setitem(w4.STAGE_N, "coverage", (4, 11))
    cells = ["exhaust-primary", "exhaust-secondary"]
    junk = {**scope.defaults, "EXHAUST_JUNK_BONUS": 12.0}
    junk2 = {**scope.defaults, "EXHAUST_JUNK_BONUS": 0.0}
    with pytest.raises(w4.DeadWeightError) as excinfo:
        w4.run_stage("coverage", [scope.defaults, junk, junk2], cells,
                     jobs=1, baseline=scope.defaults)
    assert "EXHAUST_JUNK_BONUS" in str(excinfo.value)
    assert len(excinfo.value.rows) == 2 * len(cells), "point three must not run"


def test_a_live_axis_survives_the_same_end_to_end_loop(scope, monkeypatch):
    """Positive control for the test above."""
    monkeypatch.setitem(w4.STAGE_N, "coverage", (4, 11))
    moved = {**scope.defaults, "EXHAUST_COST_EFFICIENCY_WEIGHT": 1.0}
    rows = w4.run_stage("coverage", [scope.defaults, moved],
                        ["exhaust-primary"], jobs=1, baseline=scope.defaults)
    assert len(rows) == 2
    assert all(r["reads"]["EXHAUST_COST_EFFICIENCY_WEIGHT"] > 0 for r in rows)


def test_the_power_floor_separates_dead_from_thin_from_live():
    row = {"reads": {"BUSY": 10000, "THIN": 4, "DEAD": 0}}
    shares = w4.read_shares(row)
    assert w4.power_label(shares["BUSY"]) == "live"
    assert w4.power_label(shares["THIN"]) == "thin"
    assert w4.power_label(shares["DEAD"]) == "DEAD"


def test_a_moving_control_cell_is_detected():
    moved = [{"cell": "w4-null-control", "digest": "aaaa"},
             {"cell": "w4-null-control", "digest": "bbbb"}]
    still = [{"cell": "w4-null-control", "digest": "aaaa"},
             {"cell": "w4-null-control", "digest": "aaaa"}]
    assert w4.control_is_still(moved)[0] is False
    assert w4.control_is_still(still)[0] is True


# ---------------------------------------------------------------------------
#  The decision rule and the taste / tuning line
# ---------------------------------------------------------------------------

def _summary(win, lo, hi):
    return {"win": win, "win_lo": lo, "win_hi": hi,
            "acts": [{"act": 1, "cleared_rate": 0.5, "lo": 0.4, "hi": 0.6}]}


def test_classify_reads_the_four_verdicts():
    base = {"a": _summary(0.05, 0.04, 0.06), "b": _summary(0.05, 0.04, 0.06)}
    up = {"a": _summary(0.12, 0.10, 0.14), "b": _summary(0.05, 0.04, 0.06)}
    down = {"a": _summary(0.01, 0.00, 0.02), "b": _summary(0.05, 0.04, 0.06)}
    trade = {"a": _summary(0.12, 0.10, 0.14), "b": _summary(0.01, 0.00, 0.02)}
    same = {"a": _summary(0.06, 0.04, 0.08), "b": _summary(0.05, 0.04, 0.06)}
    assert w4.classify(base, up) == "DOMINATING"
    assert w4.classify(base, down) == "DOMINATED"
    assert w4.classify(base, trade) == "TRADE"
    assert w4.classify(base, same) == "INSEPARABLE"


def test_an_act_funnel_regression_blocks_a_winrate_gain():
    """A point that wins more and clears act 1 measurably less is a TRADE, not
    an improvement -- the funnel is a term in the rule, not a decoration."""
    base = {"a": {"win": 0.05, "win_lo": 0.04, "win_hi": 0.06,
                  "acts": [{"act": 1, "cleared_rate": 0.70,
                            "lo": 0.68, "hi": 0.72}]}}
    cand = {"a": {"win": 0.12, "win_lo": 0.10, "win_hi": 0.14,
                  "acts": [{"act": 1, "cleared_rate": 0.50,
                            "lo": 0.48, "hi": 0.52}]}}
    assert w4.classify(base, cand) == "TRADE"


def test_only_dominating_and_dominated_belong_to_the_integration():
    assert w4.ADOPTABLE == {"DOMINATING", "DOMINATED"}
    for verdict in ("TRADE", "INSEPARABLE"):
        assert verdict not in w4.ADOPTABLE
        assert "[USER]" in w4.verdict_route(verdict)
    assert "[USER]" not in w4.verdict_route("DOMINATING")
    # ... and even a dominating point is not free.
    assert "PILOT_WEIGHTS_VERSION" in w4.verdict_route("DOMINATING")
    assert "confirm" in w4.verdict_route("DOMINATING")


def test_the_inseparable_default_is_to_change_nothing():
    assert "CHANGE NOTHING" in w4.verdict_route("INSEPARABLE")


def test_taste_flags_catch_the_three_named_cases(scope):
    off = w4.taste_flags({**scope.defaults, "BOMB_SUPPRESSION_VALUE": 0.0},
                         scope)
    assert any("turns the term OFF" in f for f in off)

    cap = w4.taste_flags(
        {**scope.defaults, "BOMB_CONCENTRATION_STACK_CAP": 5}, scope)
    assert any("STACK_CAP" in f for f in cap)

    shared = w4.taste_flags(
        {**scope.defaults, "PILOT_COMPANION_COPY_VALUE": 3.0}, scope)
    assert any("SHARED" in f for f in shared)

    assert w4.taste_flags(scope.defaults, scope) == []


# ---------------------------------------------------------------------------
#  The CLI's own fence
# ---------------------------------------------------------------------------

def test_the_bare_command_runs_nothing(capsys):
    assert w4.main([]) == 0
    out = capsys.readouterr().out
    assert "PLAN ONLY" in out
    assert "Nothing was run" in out
    assert policy.PILOT_POLICIES_ENABLED is SHIPPED_SWITCH


def test_execute_without_a_stage_is_refused(capsys):
    assert w4.main(["--execute"]) == 2


def test_the_plan_carries_the_decision_rule_and_the_taste_line(scope):
    plan = w4.format_plan(scope)
    assert "DOMINATING" in plan and "DOMINATED" in plan
    assert "TASTE" in plan and "[USER]" in plan


def test_every_report_row_carries_its_world_stamp(scope):
    """R68: a report without a stamp is not citable, and a weight sweep taken
    across a version bump is two sweeps that cannot say which is which."""
    row = w4.evaluate(_cell("bomb-primary"), scope.defaults)
    assert "RT" in row["stamp"] and "/D" in row["stamp"]
    assert "/P" in row["stamp"] and "/C" in row["stamp"]
