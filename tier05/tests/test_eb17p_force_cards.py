"""The `force_cards` deck-injection seam (EB-17p prerequisites 2 and 3).

`force_cards` exists so two arms can run on the SAME seeds with one deck
holding an extra copy of a named card and the other not -- the register's
"two decks on the same seeds, one with a copy forced in, one without". The
registration (`review/active/eb17p-registration-draft-2026-08-08.md` §2.2,
§10) buys its pairing with two properties, and this file is where both are
pinned rather than assumed:

  1. `force_cards=None` is the world we already have. Element-for-element
     identical to the pre-seam batch, on the `grant_relics` / `grant_potions`
     / `slot_mode` precedent. Without this the CONTROL arm is not an anchor
     and nothing in the sweep's report is comparable to the roster table --
     it is stop condition S2, and S2 needs something that can fail.

  2. The injection happens at the END of run start, AFTER the run-start
     relic effects that draw from the main stream in a deck-size-dependent
     way (`relics.py:424-445`). So a forced run and its control enter floor 1
     having consumed exactly the same randomness: same map, same seeded/Neow
     relics, same gold, differing in one card. That is tested directly, by
     comparing the rng state itself, because "the injection is late enough"
     is the one claim the whole paired design rests on.

The forced copy is ASSIGNED, never enforced: a rest node can remove it and a
smith node rewrites its id in place, so the end-of-run read pools `X` with
`X+`. That is intent-to-treat by design (§2.3), not a gap in this file.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier05 import cells, draft, model

CHAR = "klee"
ARCH = "reaction"
PILOT = "reaction"
POLICY = draft.assigned_policy

# A card the sweep actually forces, and Klee's basic Attack -- the filler.
FORCED = "friendly_visit"
FILLER = "kaboom"

SEEDS = (1, 2, 3, 7, 11)


def _setup(seed, force_cards=None):
    """Run start ONLY, stopping before the first node.

    The seam's claim is about what run start consumes, so the test looks at
    run start rather than inferring it from a whole run's outcome.
    """
    return model._setup_run(CHAR, ARCH, PILOT, POLICY, seed, "standard",
                            None, True, True, 1, "hunter",
                            force_cards)


# ===========================================================================
# 1. force_cards=None is byte-for-byte the pre-seam world
# ===========================================================================

def test_force_cards_none_is_byte_for_byte_unchanged():
    """The S2 precondition. REAL combat, no stub: if the seam perturbs a run
    it does not perturb a metric, it perturbs the control arm."""
    for seed in SEEDS:
        default = model.run_one(CHAR, ARCH, PILOT, POLICY, seed,
                                grant_relics=True, grant_potions=True,
                                n_acts=1)
        for explicit in (None, []):
            other = model.run_one(CHAR, ARCH, PILOT, POLICY, seed,
                                  grant_relics=True, grant_potions=True,
                                  n_acts=1, force_cards=explicit)
            assert other.deck_ids == default.deck_ids, seed
            assert other.hp_by_node == default.hp_by_node, seed
            assert other.gold == default.gold, seed
            assert other.won == default.won, seed
            assert other.death_node == default.death_node, seed
            assert other.node_kinds == default.node_kinds, seed
            assert other.relics == default.relics, seed
            assert other.shop == default.shop, seed
            assert other.rests == default.rests, seed
            assert other.removal_uses == default.removal_uses, seed
            assert [d["picked"] for d in other.decisions] == \
                   [d["picked"] for d in default.decisions], seed


def test_force_cards_none_batch_is_element_for_element_identical():
    """The pin the registration names: a NONE BATCH, not just a none run.
    `run_many` threads the argument through `_run_range` and the process-pool
    chunk tuple, and a positional slip there would land the value in the
    wrong parameter without any single run looking wrong."""
    default = model.run_many(CHAR, ARCH, PILOT, POLICY, 8, 11,
                             grant_relics=True, grant_potions=True, n_acts=1)
    forced_none = model.run_many(CHAR, ARCH, PILOT, POLICY, 8, 11,
                                 grant_relics=True, grant_potions=True,
                                 n_acts=1, force_cards=None)
    assert len(forced_none) == len(default) == 8
    for a, b in zip(forced_none, default):
        assert a.seed == b.seed
        assert a.deck_ids == b.deck_ids
        assert a.hp_by_node == b.hp_by_node
        assert a.won == b.won
        assert a.node_kinds == b.node_kinds
        assert a.gold == b.gold


def test_a_canonical_cell_forces_nothing():
    """The ratified cell must not have quietly acquired a treatment."""
    assert cells.CANONICAL.force_cards is None
    assert "forced=" not in cells.CANONICAL.stamp()


# ===========================================================================
# 2. A forced id is in the deck at run start, and costs no randomness
# ===========================================================================

@pytest.mark.parametrize("cid", [FORCED, FILLER])
def test_forced_id_is_in_the_deck_at_run_start(cid):
    for seed in SEEDS:
        plain = _setup(seed)
        forced = _setup(seed, [cid])
        # Appended, and appended LAST: the control deck is a prefix of the
        # forced one, so the injection adds and never reorders or replaces.
        assert forced.deck_ids == list(plain.deck_ids) + [cid], seed
        # `res.deck_ids` is the SAME list object, which is what makes the
        # injection visible to every downstream deck read without a second
        # write. A copy here would leave RunResult reporting the control deck.
        assert forced.res.deck_ids is forced.deck_ids, seed
        assert cid in forced.res.deck_ids, seed


def test_run_start_rng_consumption_is_unchanged_by_injection():
    """THE pairing claim, tested at the source.

    If the injection sat before the run-start relic effects, `_pickup_upgrade`
    would shuffle a one-longer list of deck indices and every draw from the
    main stream after it would differ -- the two arms would face different
    maps from floor 1 and the pairing would be gone before the first node.
    Comparing the generator's own state is the direct read of that, and it
    fails on any future edit that moves the injection earlier.
    """
    for seed in SEEDS:
        plain = _setup(seed)
        for cid in (FORCED, FILLER):
            forced = _setup(seed, [cid])
            assert forced.rng.getstate() == plain.rng.getstate(), (seed, cid)
            # And the rest of run start agrees too: same body, same purse,
            # same relics. One card is the entire difference.
            assert forced.hp == plain.hp
            assert forced.max_hp == plain.max_hp
            assert forced.gold == plain.gold
            assert forced.seed_ids == plain.seed_ids
            assert ([] if forced.held is None else list(forced.held.ids)) == \
                   ([] if plain.held is None else list(plain.held.ids))


def test_two_forced_cards_both_land_in_order():
    ctx = _setup(11, [FORCED, FILLER])
    plain = _setup(11)
    assert ctx.deck_ids == list(plain.deck_ids) + [FORCED, FILLER]


def test_an_unknown_forced_id_fails_loudly_at_run_start():
    """A typo must not surface as a KeyError deep inside a worker process,
    halfway through a 2,400-run batch."""
    with pytest.raises(Exception):
        _setup(11, ["no_such_card_at_all"])


# ===========================================================================
# 3. The seam through Cell -- the object a registered experiment runs
# ===========================================================================

def test_a_forced_cell_stamps_its_treatment():
    """A forced arm must never print a line that reads like the control."""
    base = cells.CANONICAL.but(character=CHAR, archetype=ARCH, name="eb17p")
    treated = base.but(force_cards=(FORCED,), name="eb17p-forced")
    assert f"forced={FORCED}" in treated.stamp()
    assert "forced=" not in base.stamp()
    # Same world: forcing a card is a DECK change, so the RT/D/P/C the two
    # arms carry must be identical. If this ever fails, the sweep is a
    # two-world sweep and §9's S1 has fired.
    assert treated.versions == base.versions


def test_a_cell_forwards_its_force_cards_to_the_model(monkeypatch):
    """`Cell.run()` must hand the treatment to `run_many` as a LIST.

    Checked at the boundary rather than through a run's outcome, because a
    finished run cannot answer this question: the run layer removes copies at
    rest nodes and rewrites ids at smith nodes, so the treated arm's FINAL
    deck is not reliably longer than the control's -- which is intent-to-
    treat (§2.3) working as designed, not a leak. Run start is where the
    assignment is observable, and the two tests above pin it there.
    """
    seen = {}

    def _spy(*a, **kw):
        seen.update(kw)
        return []

    monkeypatch.setattr(model, "run_many", _spy)
    cells.CANONICAL.but(character=CHAR, archetype=ARCH, runs=2, n_acts=1,
                        name="t", force_cards=(FORCED, FILLER)).run()
    assert seen["force_cards"] == [FORCED, FILLER]

    seen.clear()
    cells.CANONICAL.but(character=CHAR, archetype=ARCH, runs=2, n_acts=1,
                        name="k").run()
    assert seen["force_cards"] is None


@pytest.mark.battery
def test_the_arms_stay_paired_by_seed():
    """Run i of either arm is a pure function of `seed + i`, which is what
    makes the pairing by INDEX legitimate (§4)."""
    treated = cells.CANONICAL.but(character=CHAR, archetype=ARCH, runs=3,
                                  n_acts=1, name="t", force_cards=(FILLER,))
    control = treated.but(force_cards=None, name="k")
    pairs = list(zip(treated.run(), control.run()))
    assert len(pairs) == 3
    for t, k in pairs:
        assert t.seed == k.seed


def test_forced_and_control_share_the_run_start_deck_prefix():
    """The end-to-end version of the rng pin: two Cells, same seeds, one
    card apart at the start."""
    treated = cells.CANONICAL.but(character=CHAR, archetype=ARCH, runs=3,
                                  n_acts=1, name="t", force_cards=(FILLER,))
    control = treated.but(force_cards=None, name="k")
    starts = []
    for cell in (control, treated):
        got = []
        for i in range(cell.runs):
            ctx = _setup(cell.seed + i,
                         list(cell.force_cards) if cell.force_cards else None)
            got.append(list(ctx.deck_ids))
        starts.append(got)
    for k_deck, t_deck in zip(*starts):
        assert t_deck == k_deck + [FILLER]


def test_the_filler_is_klees_own_basic_attack():
    """§5.1: the filler is a duplicate of the character's own starting
    Strike, so the filler arm measures DECK DILUTION and nothing else. If
    Klee's starter stops containing it, the negative control has quietly
    become a real card and the sweep's baseline is no longer a baseline."""
    starter = loader.starting_deck(CHAR, random.Random(11))
    assert FILLER in starter
    card = loader.peek_card(FILLER)
    assert card.rarity == "basic"
