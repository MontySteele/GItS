"""EB-144 — the pilot's conditional literacy, and the Salon verbs.

Two blindnesses, one row. `policy._active_effects`'s predicate chain ended in
a bare `else: continue`, which yields NEITHER branch — so a predicate nobody
had taught it made the pilot price the whole conditional at zero, silently.
And `salon_rotate` / `salon_perform` appeared nowhere in `tier0/pilot/`, so
`change_the_bill` scored as its Block 3 and nothing else.

The lint at the bottom is the point of the file: the failure mode here is
SILENCE, so a future sheet row printing a predicate nobody triaged has to
fail a test rather than quietly lose its branch. Every printed predicate must
land in `policy.SCORABLE_PREDICATES` or `policy.BLIND_PREDICATES` — the
second being a claim that a mid-resolution fact was decided against, not
forgotten.

WHAT THE LINT CAN SEE IS A PROPERTY OF THE CHECKOUT, and the census tests
below name the layer they count because of it. A fresh clone and CI load the
roster plus the two committed `ref_*` approximations; a checkout holding the
gitignored `game_ref/` also loads the base-game `real_ironclad` /
`real_silent` pools, which print three predicates the roster never does — so
for a while the same suite answered differently in two places, green in CI
and red on the deploy machine. The exact-list censuses below are therefore
ROSTER censuses; the reference pools get their own curated census, and that
one SKIPS where the pools are absent, discharged instead by
`klee-mod/build/validate.ps1`'s S7 gate — the one place the suite runs with
`game_ref/` present.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _ops(state, card):
    return [fx["op"] for fx in policy._active_effects(state, card.effects,
                                                      card)]


def _stage(state, *members):
    p = state.player
    p.salon.extend(members)
    p.powers["salon_member"] = len(p.salon)


# --- (1) the two predicates the standing read named ------------------------

def test_hold_the_line_scores_the_conditional_block_against_an_attacker():
    """72.6% measured fire rate, credited at zero until now."""
    # The retired Hold the Line's shape (legacy cleanup stage 6).
    card = Card(id="hold_the_line", name="Hold the Line", cost=1,
                type="skill", effects=[
                    {"op": "spend_spark", "amount": 2},
                    {"op": "block", "amount": 5},
                    {"op": "conditional", "if": "enemy_intends_attack",
                     "then": [{"op": "block", "amount": 6}]}])

    attacking = make_state(enemies=[make_enemy(hp=60, intents=[
        {"kind": "attack", "amount": 12}])])
    assert policy._raw_block(attacking, card) == 11        # 5 + 6

    blocking = make_state(enemies=[make_enemy(hp=60, intents=[
        {"kind": "block", "amount": 9}])])
    assert policy._raw_block(blocking, card) == 5


def test_the_predicate_read_is_the_engine_s_own():
    """Delegation, not a second copy: the pilot's branch choice and the
    engine's `_predicate` cannot disagree, because they are one call."""
    st = make_state(enemies=[make_enemy(hp=60, intents=[
        {"kind": "attack", "amount": 5}])])
    st.player.charge = 10
    _stage(st, "usher")
    for name in ("enemy_intends_attack", "has_salon_members",
                 "spotlight_moved_this_turn", "charge_at_least_10"):
        gated = [{"op": "conditional", "if": name,
                  "then": [{"op": "damage", "amount": 7}]}]
        seen = bool(list(policy._active_effects(st, gated)))
        assert seen is effects._predicate(st, name), name


# --- (2) the rest of the audit --------------------------------------------

def test_this_cost_zero_asks_what_this_card_would_cost_now():
    """The engine reads `state.current_card_cost`, which at score time is the
    LAST resolved card's leftovers. The pilot reads the cost the card would
    actually be played at — the number `play_card` assigns to that field one
    line before the branch resolves."""
    # The retired Tail of Flame's shape (legacy cleanup stage 6).
    card = Card(id="tail_of_flame", name="Tail of Flame", cost=1,
                type="attack", effects=[
                    {"op": "damage", "amount": 5, "target": "enemy"},
                    {"op": "conditional", "if": "this_cost_zero",
                     "then": [{"op": "damage", "amount": 4,
                               "target": "enemy"}]}])

    paid = make_state(enemies=[make_enemy(hp=60)])
    paid.current_card_cost = 0            # stale leftovers: must NOT be read
    assert policy._expected_damage(paid, card) == 5.0

    # A card that costs 0 now pays the branch, whatever the leftovers say.
    free = make_state(enemies=[make_enemy(hp=60)])
    card.cost_delta_this_turn = -1
    free.current_card_cost = 3            # stale leftovers, the other way
    assert policy.card_cost(free, card) == 0
    assert policy._expected_damage(free, card) == 9.0


def test_mid_resolution_predicates_stay_blind_on_purpose():
    """The repair must not widen past what is knowable at score time."""
    st = make_state(enemies=[make_enemy(hp=60)])
    for name in sorted(policy.BLIND_PREDICATES):
        gated = [{"op": "conditional", "if": name,
                  "then": [{"op": "damage", "amount": 99}],
                  "else": [{"op": "block", "amount": 99}]}]
        assert list(policy._active_effects(st, gated, None)) == [], name


# --- (3) the lint ----------------------------------------------------------

def _printed_predicates(effect_list):
    for fx in effect_list:
        if fx.get("op") == "conditional":
            yield fx["if"]
            yield from _printed_predicates(fx.get("then", []))
            yield from _printed_predicates(fx.get("else", []))
        elif fx.get("op") == "choose_one":
            for mode in fx.get(effects.MODES_KEY, []):
                yield from _printed_predicates(mode.get("effects", []))


# The base-game pools behind the gitignored `game_ref/`. Derived from the
# loader rather than retyped, so the two cannot disagree about which
# characters are the reference layer.
REFERENCE_POOLS = frozenset(loader.EXTERNAL_CARD_SHEETS.values())


def _is_reference(card):
    return card.character in REFERENCE_POOLS


def _is_roster(card):
    """The committed surface: the playable roster and both `ref_*` anchors —
    everything a fresh clone and CI can load."""
    return not _is_reference(card)


def _reference_layer_is_loaded():
    """Did this checkout's loader actually pull the `real_*` pools in?

    Asked of the LOADER, never of the filesystem. The question the lint cares
    about is not whether a directory exists but whether those cards are in
    the index it walks, and only the loader answers that.
    """
    return any(_is_reference(card) for card in loader._card_index().values())


def _every_printed_predicate(keep=lambda card: True):
    """Every `if:` on every loadable card, upgraded faces included.

    `keep` selects the layer being censused — `_is_roster` for the committed
    sheets, `_is_reference` for the `game_ref/` pools, the default for both.
    """
    found = {}
    for card_id, card in loader._card_index().items():
        if not keep(card):
            continue
        faces = [card]
        if upgrades.has_upgrade(card_id):
            faces.append(upgrades.apply_upgrade(loader.get_card(card_id)))
        for face in faces:
            for name in _printed_predicates(face.effects):
                found.setdefault(name, set()).add(card_id)
    return found


def test_every_printed_predicate_is_triaged():
    """THE LINT. A sheet row may not print a predicate the pilot has never
    been shown: either it is scorable, or it is declared blind with a reason.
    A new `if:` that is neither loses its whole branch at score time, which is
    exactly the ten-row hole this row was filed for.

    Every loadable card, both layers: this assertion is the one thing that
    must hold in EVERY checkout, so it is deliberately not scoped. Where
    `game_ref/` is present it also covers the `real_*` pools, and the curated
    census below says exactly which names that is allowed to be."""
    untriaged = {
        name: sorted(users)
        for name, users in _every_printed_predicate().items()
        if not (policy.predicate_is_scorable(name)
                or policy.predicate_is_declared_blind(name))
    }
    assert not untriaged, (
        "predicate(s) the pilot cannot score and has not declared blind — "
        "add to policy.SCORABLE_PREDICATES (with a live read) or to "
        f"policy.BLIND_PREDICATES (with the reason): {untriaged}")


def test_the_declaration_names_only_real_predicates():
    """The other direction: a typo in either collection would silently
    triage nothing.

    Asked through `is_known_predicate` rather than against `PREDICATE_NAMES`
    alone, because a declaration may name one PARAMETERISED predicate
    (`self_has_power_tracking`) without adopting its whole family — the
    engine's own recogniser is the one that answers for both forms, and it
    still rejects a bare prefix or a non-integer bar."""
    for name in policy.SCORABLE_PREDICATES | policy.BLIND_PREDICATES:
        assert effects.is_known_predicate(name), name
    for prefix in (policy.SCORABLE_PREDICATE_PREFIXES
                   + policy.BLIND_PREDICATE_PREFIXES):
        assert prefix in effects.PREDICATE_PREFIXES, prefix
    assert not (policy.SCORABLE_PREDICATES & policy.BLIND_PREDICATES)


def _prototype_predicates():
    """Every `if:` any prototype row prints, by row id.

    The surface's own faces AND their `plan:` lines, because a planned clause
    is scored through the same `_active_effects` walk the now-line is
    (`policy._plan_discounted`) and a predicate inside one falls into exactly
    the same hole.
    """
    found = {}
    for card in loader.prototype_cards():
        for source in (card.effects, getattr(card, "plan", None) or []):
            for name in _printed_predicates(source):
                found.setdefault(name, set()).add(card.id)
    return found


def test_the_prototype_surface_prints_no_untaught_predicate():
    """THE LINT `EB-712` ASKED FOR. Every predicate a prototype row prints is
    either scorable or declared blind with a reason -- the same claim the
    shipped sheets have had to make since `EB-144`, now asked of the layer the
    shipped census cannot reach.

    Deliberately NOT a curated list: the surface turns over every slice, so a
    census of today's names would be a test about the staging file's contents
    rather than about the pilot's literacy. The claim is the property.
    """
    untriaged = {
        name: sorted(users)
        for name, users in _prototype_predicates().items()
        if not (policy.predicate_is_scorable(name)
                or policy.predicate_is_declared_blind(name))
    }
    assert not untriaged, (
        "prototype row(s) print a predicate the pilot cannot score and has "
        "not declared blind -- it prices the WHOLE conditional at zero and no "
        "round measured on that row means anything. Add to "
        "policy.SCORABLE_PREDICATES / _ENGINE_LIVE_PREDICATES (with a live "
        f"read) or to policy.BLIND_PREDICATES (with the reason): {untriaged}")


def test_the_surface_is_actually_being_censused():
    """The lint's own guard. An empty surface, a loader that stopped returning
    prototype rows, or a walk that stopped descending would make the assertion
    above pass by finding nothing -- which is the failure mode this whole file
    exists to refuse."""
    assert loader.prototype_cards(), "no prototype rows loaded at all"
    printed = _prototype_predicates()
    assert printed, "no prototype row prints a conditional -- suspicious"
    # Feint printed `plan_carried_out_this_turn` until the Casket pass
    # (2026-09-28) re-keyed it onto the count; Press the Advantage prints
    # `plan_held`, the arm's conditional today.
    assert "plan_held" in printed, sorted(printed)


def test_press_the_advantages_waiting_branch_is_scored_and_not_priced_at_zero():
    """`EB-712`'s rule on the arm's conditional row, both ways round. Press the
    Advantage prints 7 and 11 (the cleanup pass, 2026-09-29) and the difference
    IS the card; untaught, the pilot would read the 11 as nothing. (Feint was the named row until the
    Casket pass, 2026-09-28, took it off the yes/no.)

    Seen to FAIL before the predicate was taught: both states scored 0.0,
    because a `continue` on an unknown predicate yields NEITHER branch.
    """
    card = next(c for c in loader.prototype_cards()
                if c.id == "proto_kk_press_the_advantage")

    quiet = make_state(enemies=[make_enemy(hp=60)])
    quiet.kk_plan_queue = []
    assert policy._expected_damage(quiet, card) == 7.0

    waiting = make_state(enemies=[make_enemy(hp=60)])
    waiting.kk_plan_queue = [object()]
    assert policy._expected_damage(waiting, card) == 11.0


def test_the_prototype_predicate_read_is_the_engine_s_own(monkeypatch):
    """One rule, asked from both sides. The pilot delegates to
    `effects._predicate` rather than keeping a second copy, so the branch it
    scores and the branch that resolves cannot drift."""
    card = next(c for c in loader.prototype_cards()
                if c.id == "proto_kk_press_the_advantage")
    state = make_state(enemies=[make_enemy(hp=60)])
    state.kk_plan_queue = [object()]

    asked = []
    real = effects._predicate
    monkeypatch.setattr(effects, "_predicate",
                        lambda st, nm, *a, **k: (asked.append(nm),
                                                 real(st, nm, *a, **k))[1])
    list(policy._active_effects(state, card.effects, card))
    assert "plan_held" in asked


def test_the_reference_pools_print_only_the_three_blind_names():
    """The half of the lint the checkout can hide, made explicit.

    `real_ironclad` / `real_silent` load only where the gitignored
    `game_ref/` is, so this census ran nowhere until the S7 deploy gate went
    red on three untriaged names. It is a CURATED list, not a tolerance: the
    base-game pools are a regenerable local artifact, and a rebuild that
    printed a fourth predicate must fail here rather than be absorbed.

    Every name is declared BLIND (`policy.BLIND_PREDICATES` carries the
    reason for each). `self_has_power_tracking` is the interesting one -- it
    could be read live, and is deliberately not, because the collections are
    lint-only and blind moves no measured number while scorable would move
    the `real_silent` anchor."""
    if not _reference_layer_is_loaded():
        pytest.skip(
            "no game_ref/ in this checkout, so real_ironclad / real_silent "
            "are not in the card index and this census has nothing to "
            "count. The gate is discharged on the deploy machine by "
            "klee-mod/build/validate.ps1's S7 step, which runs this suite "
            "with game_ref/ present -- that is where "
            "test_the_reference_pools_print_only_the_three_blind_names "
            "actually reports.")

    printed = _every_printed_predicate(_is_reference)
    assert printed, "the reference pools loaded but printed no `if:` at all"

    untriaged = {
        name: sorted(users)
        for name, users in printed.items()
        if not (policy.predicate_is_scorable(name)
                or policy.predicate_is_declared_blind(name))
    }
    assert not untriaged, (
        "base-game predicate(s) the pilot cannot score and has not declared "
        "blind — add to policy.SCORABLE_PREDICATES (with a live read, which "
        "moves an anchor's numbers and wants a P window) or to "
        f"policy.BLIND_PREDICATES (with the reason): {untriaged}")

    assert sorted(n for n in printed
                  if policy.predicate_is_declared_blind(n)) == [
        "drew_skill_this_card",
        "killed_target_fatal",
        "self_has_power_tracking",
    ]


def test_the_anchors_print_no_conditional_at_all():
    """The archive-scope claim, asserted rather than argued: this row moves
    the ROSTER's combat numbers and cannot move `ref_ironclad`'s or
    `ref_silent`'s, because neither anchor pool prints an `if:` for the pilot
    to have been blind to. (`real_*` needs `game_ref/`, so the claim about
    THAT layer is the test above, which skips where the pools are absent and
    is discharged by validate.ps1's S7 gate instead.)"""
    owners = {cid for users in _every_printed_predicate().values()
              for cid in users}
    for pool in ("ref_ironclad", "ref_silent"):
        anchor = {c.id for c in loader._card_index().values()
                  if c.character == pool}
        assert anchor, pool
        assert not (anchor & owners), (pool, sorted(anchor & owners))


# --- (4) the Salon verbs ---------------------------------------------------
