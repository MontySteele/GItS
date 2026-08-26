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
"""

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects
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

def test_take_it_from_the_top_scores_its_damage_arm_once_the_bar_is_met():
    """W3's spotlight payoff. Before EB-144 the whole conditional vanished
    and the card scored as Block 5 on both faces and in both states."""
    card = loader.get_card("take_it_from_the_top")

    quiet = make_state(enemies=[make_enemy(hp=60)])
    quiet.spotlight_moved_this_turn = False
    assert _ops(quiet, card) == ["block"]
    assert policy._expected_damage(quiet, card) == 0.0

    moved = make_state(enemies=[make_enemy(hp=60)])
    moved.spotlight_moved_this_turn = True
    assert _ops(moved, card) == ["block", "damage"]
    assert policy._expected_damage(moved, card) == 10.0


def test_hold_the_line_scores_the_conditional_block_against_an_attacker():
    """72.6% measured fire rate, credited at zero until now."""
    card = loader.get_card("hold_the_line")

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

def test_has_salon_members_reads_the_live_stage():
    """Three Furina rows older than W3 sat in the same hole."""
    card = loader.get_card("waters_embrace")
    empty = make_state(enemies=[make_enemy(hp=60)])
    assert policy._raw_block(empty, card) == 9

    staged = make_state(enemies=[make_enemy(hp=60)])
    _stage(staged, "crabaletta")
    assert policy._raw_block(staged, card) == 14           # 9 + 5


def test_charge_threshold_reads_the_live_bank():
    card = loader.get_card("read_the_current")
    lean = make_state(enemies=[make_enemy(hp=60)])
    lean.player.charge = 9
    assert policy._expected_damage(lean, card) == 7.0

    banked = make_state(enemies=[make_enemy(hp=60)])
    banked.player.charge = 10
    assert policy._expected_damage(banked, card) == 13.0


def test_this_cost_zero_asks_what_this_card_would_cost_now():
    """The engine reads `state.current_card_cost`, which at score time is the
    LAST resolved card's leftovers. The pilot reads the cost the card would
    actually be played at — the number `play_card` assigns to that field one
    line before the branch resolves."""
    card = loader.get_card("tail_of_flame")

    paid = make_state(enemies=[make_enemy(hp=60)])
    paid.current_card_cost = 0            # stale leftovers: must NOT be read
    assert policy._expected_damage(paid, card) == 5.0

    # Klee's own channel: a full Spark bank frees the attack, which is the
    # exact state `tail_of_flame` is printed to pay off.
    free = make_state(enemies=[make_enemy(hp=60)])
    free.player.sparks = combat.spark_threshold(free)
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


def _every_printed_predicate():
    """Every `if:` on every loadable card, upgraded faces included."""
    found = {}
    for card_id, card in loader._card_index().items():
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
    exactly the ten-row hole this row was filed for."""
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
    triage nothing."""
    for name in policy.SCORABLE_PREDICATES | policy.BLIND_PREDICATES:
        assert name in effects.PREDICATE_NAMES, name
    for prefix in (policy.SCORABLE_PREDICATE_PREFIXES
                   + policy.BLIND_PREDICATE_PREFIXES):
        assert prefix in effects.PREDICATE_PREFIXES, prefix
    assert not (policy.SCORABLE_PREDICATES & policy.BLIND_PREDICATES)


def test_the_two_collections_cover_todays_sheet_exactly():
    """A census, so the row's before/after list is checkable rather than
    asserted. Eighteen names across the three sheets and the companions.

    `target_has_aura` is C20's (R189 C2, `elemental_ecstasy`) and joins as a
    SCORABLE name; `target_has_nonpyro_aura` stays on the list because
    `sizzle` still prints it -- the redesign moved one row, not the family.
    """
    printed = set(_every_printed_predicate())
    assert sorted(n for n in printed if policy.predicate_is_scorable(n)) == [
        "charge_at_least_10",
        "encore_at_least_5",
        "encore_at_least_8",
        "enemy_intends_attack",
        "exhaust_pile_at_least_3",
        "exhaust_pile_at_least_8",
        "fanfare_at_least_12",
        "fanfare_at_least_15",
        "fanfare_at_least_20",
        "has_salon_members",
        "has_spark",
        "reaction_triggered_this_turn",
        "spotlight_moved_this_turn",
        "target_has_aura",
        "target_has_nonpyro_aura",
        "this_cost_zero",
    ]
    assert sorted(n for n in printed
                  if policy.predicate_is_declared_blind(n)) == [
        "killed_target",
        "reaction_triggered_by_this",
    ]


def test_the_anchors_print_no_conditional_at_all():
    """The archive-scope claim, asserted rather than argued: this row moves
    the ROSTER's combat numbers and cannot move `ref_ironclad`'s or
    `ref_silent`'s, because neither anchor pool prints an `if:` for the pilot
    to have been blind to. (`real_*` needs `game_ref/` and is out of reach of
    a test that must pass on a fresh clone.)"""
    owners = {cid for users in _every_printed_predicate().values()
              for cid in users}
    for pool in ("ref_ironclad", "ref_silent"):
        anchor = {c.id for c in loader._card_index().values()
                  if c.character == pool}
        assert anchor, pool
        assert not (anchor & owners), (pool, sorted(anchor & owners))


# --- (4) the Salon verbs ---------------------------------------------------

def test_change_the_bill_is_no_longer_just_block_three():
    """The whole card. With Crabaletta at the front of a rotated stage the
    perform lands on the SECOND member — which is what the rotate buys."""
    st = make_state(enemies=[make_enemy(hp=60)])
    _stage(st, "usher", "crabaletta")
    st.player.encore = 5
    card = loader.get_card("change_the_bill")

    # rotate first: usher goes to the back, so crabaletta performs (6 damage).
    assert policy._expected_damage(st, card) == 6.0
    assert policy._raw_block(st, card) == 3.0              # printed Block only


def test_the_usher_s_tick_lands_in_block_not_damage():
    st = make_state(enemies=[make_enemy(hp=60)])
    _stage(st, "crabaletta", "usher")           # rotate -> usher performs
    st.player.encore = 5
    card = loader.get_card("change_the_bill")

    assert policy._expected_damage(st, card) == 0.0
    assert policy._raw_block(st, card) == 6.0              # 3 printed + 3 tick


def test_the_perform_pays_its_encore_upkeep():
    """A tick that can pay costs a point; the scorer charges it at the same
    price `_sustain_value` credits a point at."""
    fed = make_state(enemies=[make_enemy(hp=60)])
    _stage(fed, "usher", "crabaletta")
    fed.player.encore = 3
    card = loader.get_card("change_the_bill")
    assert policy._sustain_value(fed, card) == pytest.approx(
        -C.SALON_TICK_ENCORE_COST * C.PILOT_ENCORE_VALUE)

    dry = make_state(enemies=[make_enemy(hp=60)])
    _stage(dry, "usher", "crabaletta")
    dry.player.encore = 0
    assert policy._sustain_value(dry, card) == 0.0
    # ...and the dry tick pays three-quarters, the engine's own reduction.
    assert policy._expected_damage(dry, card) == float(
        int(6 * C.SALON_DRY_DAMAGE_MULT))


def test_an_empty_stage_pays_nothing_and_the_card_still_scores():
    """`_op_salon_perform` whiffs on an empty stage; so does the forecast."""
    st = make_state(enemies=[make_enemy(hp=60)])
    card = loader.get_card("change_the_bill")
    assert policy._salon_verb_yield(st, card) == (0.0, 0.0, 0.0)
    assert policy._raw_block(st, card) == 3.0


def test_the_forecast_agrees_with_the_resolver_it_forecasts():
    """The anti-drift pin. The pilot's tick number IS `salon_tick_amount` —
    the only difference the `note=False` kwarg may make is the census row."""
    for member in sorted(C.SALON_MEMBERS):
        for fanfare in (0, 25):
            for encore in (0, 4):
                st = make_state(enemies=[make_enemy(hp=90)])
                _stage(st, member)
                st.player.encore = encore
                st.player.fanfare_cap = 30
                st.player.fanfare = fanfare
                paid = encore >= C.SALON_TICK_ENCORE_COST
                quiet = effects.salon_tick_amount(st, member, paid,
                                                  note=False)
                loud = effects.salon_tick_amount(st, member, paid)
                assert quiet == loud, (member, fanfare, encore)


def test_the_forecast_files_no_fanfare_census_row():
    """A forecast is not a read: scoring a hand must not inflate the C2
    escrow's `fanfare_read` census."""
    st = make_state(enemies=[make_enemy(hp=60)])
    _stage(st, "crabaletta")
    st.player.fanfare_cap = 30
    st.player.fanfare = 20
    st.player.encore = 3
    before = len([ev for ev in st.log if ev["event"] == "fanfare_read"])
    policy._salon_verb_yield(st, loader.get_card("change_the_bill"))
    after = len([ev for ev in st.log if ev["event"] == "fanfare_read"])
    assert after == before
