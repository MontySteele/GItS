"""EB-136 / R210 (`C18`): a card's `target: enemy` ops resolve against ONE
creature, and C#'s dead-target rule is reproduced op by op.

WHAT THE RULING SAID, all three halves ([USER] 2026-08-25, "full parity"):

  Q1(b)  EVERY `target: enemy` op binds, not just the three the row's old
         next-action named. That is 28 live cards and it reaches
         `ref_ironclad`'s starter `bash` -- the scoring anchor's own deck --
         plus `ref_silent` and both `real_*` pools.
  Q2     The same binding INSIDE one op: a multi-hit row holds its aim across
         hits and the hits after it dies FIZZLE, with no re-pick.
  Q3     Exact parity on dead targets, WHICH IS NOT UNIFORM. Aimed damage
         fizzles; aimed powers land on the corpse.

WHERE EACH VERDICT COMES FROM. Nothing here is argued from taste; every pin
below traces to a decompiled fact recorded in
`review/active/eb136-blast-radius-2026-08-25.md`:

  * `AttackCommand.Execute` refilters its one-element `GetPossibleTargets()`
    by `IsAlive` on EVERY hit and breaks on empty, and `CombatState
    .IsLiveCombat()` returns literally `true` -- so the break is
    unconditional. `CreatureCmd.Damage`'s `if (originalTarget2.IsDead)
    continue;` sits behind it. (sec.3.1 -> damage fizzles, and Q2.)
  * `PowerCmd.Apply` guards on `CanReceivePowers`, whose first-party doc
    comment says dead creatures can still have powers applied to them --
    `IsHittable`, three lines above it, DOES test `IsDead`. (sec.3.2 ->
    powers land on the corpse.)
  * `CardPlay.Target` is `init`-only and `CardCmd.AutoPlay` rolls it once
    from `HittableEnemies` before resolution. (sec.3.3 -> the binding moment
    is card-play construction, and `force_random_targeting` rolls once per
    card.)
  * The mod-authored ops reach the same corpse-accepting door:
    `BombPower.Place` and `BombPower.MoveAllTo` are `PowerCmd.Apply`, and
    `ElementalHit.ApplyOnly` -> `AuraCmd.Apply` is `PowerCmd.Apply<XAuraPower>`.
    `BombPower.DetonateOn` reads `target.Powers.OfType<BombPower>()` with no
    aliveness test at all and the mod counts the corpse case explicitly
    (`RecordDetonation(..., onCorpse: ...)`). (sec.3.4.)

BOARDS ARE BUILT SO THAT THE OLD BEHAVIOUR AND THE NEW ONE DISAGREE. Damage
to the lowest-HP enemy keeps that enemy lowest, so without a kill the per-op
re-pick was a no-op (audit sec.2.4) -- every board here therefore either kills
the aim mid-card or puts an aura/pile somewhere the aim is not. A test that
passed under both engines would be pinning nothing.
"""

from __future__ import annotations

from tier0.engine import effects
from tier0.engine.combat import _settle_phases
from tier0.engine.state import Bomb, Card
from tier0.tests.conftest import make_enemy, make_state


def _enemy(hp, name, bombs=(), aura=None):
    e = make_enemy(hp=hp, name=name)
    e.bombs = [Bomb(damage=d, element="pyro", turn_placed=0) for d in bombs]
    if aura:
        e.aura, e.aura_turns_left = aura, 3
    return e


def _card(cid, effs, ctype="attack", **kw) -> Card:
    return Card(id=cid, name=cid, cost=1, type=ctype, effects=effs, **kw)


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 1 -- the gather-and-detonate card, three ops, one enemy
# ---------------------------------------------------------------------------

def test_gather_detonate_and_swing_all_land_on_the_same_enemy():
    """THE ROW'S FIRST ACCEPTANCE PIN, on `sparkly_explosion`'s ruled body.

    A board where the lowest-HP body and the fattest body differ, and where
    the gather-then-detonate sequence KILLS the aim before the damage line
    resolves. The mod puts all three on `cardPlay.Target`:

        BombPower.MoveAllTo(..., cardPlay.Target, HittableEnemies, ...)
        BombPower.DetonateOn(cardPlay.Target, 3)
        DamageCmd.Attack(14).Targeting(cardPlay.Target)

    Before `C18` the sim resolved that as up to three different enemies: the
    gather aimed at the 6 HP body, the detonation killed it, and the 14 then
    walked to the fat one -- scattering exactly what the card is built to
    concentrate. Now the 14 fizzles into the corpse's empty target list and
    the fat enemy is untouched.
    """
    low, fat = _enemy(6, "low"), _enemy(90, "fat", bombs=(5,))
    state = make_state([low, fat])

    effects.resolve_card(state, _card("sparkly_explosion", [
        {"op": "move_bombs", "target": "enemy"},
        {"op": "detonate", "target": "enemy", "bonus": 3},
        {"op": "damage", "amount": 14, "target": "enemy"},
    ]))

    assert not low.alive                      # the detonation killed the aim
    assert low.bombs == []                    # gathered here, then spent here
    assert fat.bombs == []                    # its pile was moved off it
    assert fat.hp == 90                       # and the 14 did NOT walk over


def test_without_a_kill_the_three_ops_are_still_one_enemy():
    """The same card on a board it does not kill, so the pin is about the
    BINDING and not about the fizzle. The gather has to bring the fat body's
    pile to the aim, and the swing has to land on the same aim -- not on
    whoever is lowest-HP after 8 points of bomb went into the 40 HP body."""
    aim, fat = _enemy(40, "aim"), _enemy(90, "fat", bombs=(5,))
    state = make_state([aim, fat])

    effects.resolve_card(state, _card("sparkly_explosion", [
        {"op": "move_bombs", "target": "enemy"},
        {"op": "detonate", "target": "enemy", "bonus": 3},
        {"op": "damage", "amount": 14, "target": "enemy"},
    ]))

    assert fat.hp == 90 and fat.bombs == []
    assert aim.hp == 40 - (5 + 3) - 14


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 2 -- `times` binds in the same pass
# ---------------------------------------------------------------------------

def test_a_multi_hit_row_stops_hitting_when_its_aim_dies():
    """THE ROW'S SECOND ACCEPTANCE PIN (R210 Q2), on
    `matinee_performance`'s shape: `damage 5` then `damage 2 times: N`.

    `AttackCommand.Execute` re-checks the SAME `_singleTarget` on every hit
    and breaks when it is dead. tier0's `_op_damage` used to call
    `_pick_targets` per hit, so the 2s spread across the survivors -- three
    hits into three different bodies where the mod deals one and stops.
    """
    low, fat = _enemy(5, "low"), _enemy(90, "fat")
    state = make_state([low, fat])

    effects.resolve_card(state, _card("matinee_performance", [
        {"op": "damage", "amount": 5, "target": "enemy"},
        {"op": "damage", "amount": 2, "target": "enemy", "times": 4},
    ]))

    assert not low.alive
    assert fat.hp == 90        # all four 2s fizzled; none walked to the fat


def test_the_multi_hit_row_that_does_not_kill_puts_every_hit_on_one_body():
    """The positive control the test above needs: the same row on a board
    where nothing dies still delivers all four hits, and delivers them to the
    bound aim rather than to whoever is lowest-HP after each one."""
    aim, other = _enemy(40, "aim"), _enemy(41, "other")
    state = make_state([aim, other])

    effects.resolve_card(state, _card("skewer", [
        {"op": "damage", "amount": 2, "target": "enemy", "times": 4},
    ]))

    assert aim.hp == 32 and other.hp == 41


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 3 -- the corpse-power pin
# ---------------------------------------------------------------------------

def test_an_aimed_debuff_whose_target_died_attaches_to_the_corpse():
    """THE ROW'S THIRD ACCEPTANCE PIN (R210 Q3), on `bash`'s shape -- and
    `bash` is in `ref_ironclad`'s STARTER, so this is the scoring anchor's
    own deck.

    `PowerCmd.Apply` accepts a corpse. Before `C18` the Vulnerable walked to
    the living bystander, which is a live debuff the sim was handing the
    player and the mod was not; the repair REMOVES that, and the audit says
    so in as many words (sec.4/C3 -- "a real strength loss for the anchor
    deck, not a rounding difference").
    """
    low, bystander = _enemy(6, "low"), _enemy(90, "bystander")
    state = make_state([low, bystander])

    effects.resolve_card(state, _card("bash", [
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "apply_power", "power": "vulnerable", "amount": 2,
         "target": "enemy"},
    ]))

    assert not low.alive
    assert low.powers.get("vulnerable") == 2          # on the corpse
    assert "vulnerable" not in bystander.powers       # NOT on the bystander


def test_every_stack_of_a_times_debuff_lands_on_the_corpse():
    """No death-break on the power side, unlike `_op_damage`: `PowerCmd
    .Apply` has no aliveness test to fail, so a `times` loop keeps applying.
    The kill happens on the row before, so all three stacks meet a corpse."""
    low, bystander = _enemy(4, "low"), _enemy(90, "bystander")
    state = make_state([low, bystander])

    effects.resolve_card(state, _card("poisoned_stab_like", [
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "apply_power", "power": "weak", "amount": 1,
         "target": "enemy", "times": 3},
    ]))

    assert not low.alive
    assert low.powers.get("weak") == 3
    assert bystander.powers == {}


# ---------------------------------------------------------------------------
#  The dead-target rule, op by op
# ---------------------------------------------------------------------------

def test_the_damage_funnel_refuses_a_corpse():
    """`CreatureCmd.Damage`'s `if (originalTarget2.IsDead) continue;`, at the
    funnel rather than only at the target picker -- so nothing downstream of a
    dead target runs either: no reaction, no aura consumption, no on-hit
    rider. The board is built with an aura precisely so a leak would show."""
    dead = _enemy(10, "dead", aura="hydro")
    dead.hp = 0
    state = make_state([dead])

    dealt = effects.deal_damage_to_enemy(state, dead, 20, element="pyro",
                                         source="attack")

    assert dealt == 0
    assert dead.hp == 0            # not driven further negative
    assert dead.aura == "hydro"    # the reaction pipeline never ran


def test_a_bomb_pile_stops_hitting_the_body_its_first_charge_killed():
    """The funnel guard fixes a case that PREDATES the binding, and it is
    pinned so the fix is not mistaken for a side effect: two charges on one
    enemy where the first is lethal. `BombPower.Detonate` loops its charges
    through `ElementalHit.Deal`, which lands on `CreatureCmd.Damage` and is
    skipped for a corpse. BOTH charges are still popped and still counted --
    the pile is spent either way, which is the mod's corpse-detonation shape
    -- so the pin is on the DAMAGE events, not on the detonation count."""
    e = _enemy(4, "e", bombs=(5, 5))
    state = make_state([e])

    effects.detonate_bombs(state, e)

    assert not e.alive
    assert e.hp == -1              # the first charge only
    pops = [r for r in state.log if r["event"] == "bomb_detonation"]
    hits = [r for r in state.log
            if r["event"] == "damage" and r.get("source") == "bomb"]
    assert len(pops) == 2 and len(hits) == 1


def test_place_bomb_arms_a_corpse():
    """`BombPower.Place` is `PowerCmd.Apply<BombPower>`. The bomb is inert as
    damage -- a corpse takes none -- but it EXISTS, which is what makes the
    `move_bombs` reading below a real question rather than a hypothetical."""
    low, other = _enemy(6, "low"), _enemy(90, "other")
    state = make_state([low, other])

    effects.resolve_card(state, _card("fish_flavored_bait", [
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "place_bomb", "amount": 1, "target": "enemy",
         "bomb_damage": 6},
    ]))

    assert not low.alive
    assert len(low.bombs) == 1
    assert other.bombs == []


def test_move_bombs_gathers_onto_a_corpse_but_never_gathers_from_one():
    """The asymmetry the emitted call spells out:

        BombPower.MoveAllTo(choiceContext, cardPlay.Target,
                            CombatState!.HittableEnemies, bonus, ...)

    The DESTINATION is `cardPlay.Target` and reaches the pile through
    `PowerCmd.Apply`, which accepts a corpse. The SOURCES are
    `HittableEnemies`, and `IsHittable` opens with `if (IsDead) return
    false;` -- so a dead body's own pile is never swept up. `living_enemies`
    is the sim's spelling of that list.
    """
    corpse, living = _enemy(10, "corpse", bombs=(4,)), _enemy(90, "living",
                                                              bombs=(5,))
    corpse.hp = 0
    state = make_state([corpse, living])
    state.card_aim, state.card_aim_bound = corpse, True
    try:
        effects._op_move_bombs(state, {"op": "move_bombs", "target": "enemy",
                                       "bonus": 1}, _card("probe", []))
    finally:
        state.card_aim, state.card_aim_bound = None, False

    assert living.bombs == []                     # swept off the living body
    assert [b.damage for b in corpse.bombs] == [4, 6]   # its own, plus 5 + 1


def test_detonating_a_corpse_spends_the_charges_for_nothing():
    """`BombPower.DetonateOn` has NO aliveness test -- it reads
    `target.Powers.OfType<BombPower>()` and pops. The mod knows this case
    happens and counts it (`RecordDetonation(..., onCorpse: target is
    { IsDead: true })`, the EB-18 instrument that reports and never grades).
    So the charges are consumed, the detonation is counted, and the damage
    behind them dies at the funnel."""
    corpse = _enemy(10, "corpse", bombs=(7, 7))
    corpse.hp = 0
    state = make_state([corpse])
    before = state.detonations_total
    state.card_aim, state.card_aim_bound = corpse, True
    try:
        effects._op_detonate(state, {"op": "detonate", "target": "enemy"},
                             _card("probe", []))
    finally:
        state.card_aim, state.card_aim_bound = None, False

    assert corpse.bombs == []
    assert state.detonations_total == before + 2
    assert corpse.hp == 0


def test_an_aimed_aura_lands_on_the_corpse_and_is_closed_at_the_settle():
    """`ElementalHit.ApplyOnly` -> `AuraCmd.Apply` ->
    `PowerCmd.Apply<XAuraPower>`: the corpse-accepting door again. The sim's
    own `close_dead_auras` clears it at the next settle, which is bookkeeping
    (EB-58's uptime rule) rather than a divergence -- the aura was applied,
    and then the body stopped counting as uptime."""
    low, other = _enemy(6, "low"), _enemy(90, "other")
    state = make_state([low, other])

    effects.resolve_card(state, _card("aimed_aura_probe", [
        {"op": "damage", "amount": 8, "target": "enemy",
         "applies_element": False},
        {"op": "apply_aura", "target": "enemy", "element": "hydro"},
    ]))

    assert not low.alive
    assert low.aura == "hydro"
    assert other.aura is None

    _settle_phases(state)
    assert low.aura is None


# ---------------------------------------------------------------------------
#  The bind itself
# ---------------------------------------------------------------------------

def test_the_aim_is_taken_before_the_first_op_not_at_the_first_aimed_op():
    """`CardCmd.AutoPlay` fills `cardPlay.Target` BEFORE `OnPlayWrapper` is
    entered, so the aim is picked pre-AoE (audit sec.3.3) -- "not lazily at
    the first aimed op", in the audit's words.

    The board makes eager and lazy binding give different answers: the AoE
    KILLS the pre-AoE lowest-HP body, so a lazily-bound aim would find only
    the survivor and put the debuff on it. Eagerly bound, the debuff goes to
    the corpse the card started out aiming at.
    """
    a, b = _enemy(8, "a"), _enemy(90, "b")
    state = make_state([a, b])

    effects.resolve_card(state, _card("aoe_then_aim", [
        {"op": "damage", "amount": 10, "target": "all_enemies"},
        {"op": "apply_power", "power": "vulnerable", "amount": 1,
         "target": "enemy"},
    ]))

    assert not a.alive and b.hp == 80
    assert a.powers.get("vulnerable") == 1
    assert "vulnerable" not in b.powers


def test_an_aoe_that_reorders_the_board_does_not_move_the_aim():
    """The reorder case the test above cannot make: an `all_enemies` row with
    a per-target rider that hits the two bodies unequally, so the lowest-HP
    reading FLIPS mid-card. The bound aim is the pre-AoE one."""
    a, b = _enemy(30, "a"), _enemy(34, "b", aura="cryo")
    state = make_state([a, b])

    effects.resolve_card(state, _card("reordering_aoe", [
        {"op": "damage", "amount": 6, "target": "all_enemies",
         "bonus_vs_aura": 12, "applies_element": False},
        {"op": "apply_power", "power": "weak", "amount": 1,
         "target": "enemy"},
    ]))

    assert a.hp == 24 and b.hp == 16          # `b` is now the lowest
    assert a.powers.get("weak") == 1          # but the aim was bound to `a`
    assert "weak" not in b.powers


def test_the_bind_is_cleared_between_plays():
    """`card_aim_bound` is what keeps the pilot's between-play estimates off
    the last card's corpse: `_default_target` has to read live state when no
    `CardPlay` is in flight."""
    low, fat = _enemy(6, "low"), _enemy(90, "fat")
    state = make_state([low, fat])

    effects.resolve_card(state, _card("bash", [
        {"op": "damage", "amount": 8, "target": "enemy"},
    ]))

    assert state.card_aim is None and state.card_aim_bound is False
    assert effects._default_target(state) is fat


def test_a_free_play_does_not_steal_the_outer_cards_aim():
    """A free play constructs a SECOND `CardPlay` inside the first, with its
    own target, and `resolve_card`'s `finally` clears the pair on the way
    out. `combat._FREE_PLAY_CONTEXT` saves and restores them, or the outer
    card would finish its remaining aimed ops unbound -- silently back on the
    per-op lowest-HP pick this row exists to kill."""
    from tier0.engine import combat

    low, fat = _enemy(6, "low"), _enemy(90, "fat")
    state = make_state([low, fat])
    inner = _card("inner", [{"op": "damage", "amount": 3,
                             "target": "random_enemy"}])

    def _outer_probe(st, fx, card):
        assert st.card_aim_bound and st.card_aim is low
        combat.resolve_free_play(st, inner)
        assert st.card_aim_bound and st.card_aim is low

    effects.OPS["_eb136_probe"] = _outer_probe
    try:
        effects.resolve_card(state, _card("outer", [
            {"op": "_eb136_probe"},
            {"op": "apply_power", "power": "vulnerable", "amount": 1,
             "target": "enemy"},
        ]))
    finally:
        del effects.OPS["_eb136_probe"]

    assert low.powers.get("vulnerable") == 1
    assert "vulnerable" not in fat.powers


def test_forced_random_targeting_rolls_once_per_card_not_once_per_op():
    """`CardCmd.AutoPlay` rolls `Rng.CombatTargets.NextItem(HittableEnemies)`
    ONCE, before resolution, and only `if (card2.TargetType ==
    TargetType.AnyEnemy)`. tier0 rolled inside `_pick_targets`, i.e. once per
    aimed op, so a three-op free play took three independent draws.

    Four aimed rows on a four-enemy board, none of them lethal: under a
    per-op roll they scatter across the board (the whole point of Havoc's
    variance profile); under the card-level roll every one lands on one body.
    """
    board = [_enemy(60, f"e{i}") for i in range(4)]
    state = make_state(board, seed=3)
    state.force_random_targeting = True

    effects.resolve_card(state, _card("havoc_like", [
        {"op": "damage", "amount": 3, "target": "enemy"},
        {"op": "damage", "amount": 3, "target": "enemy"},
        {"op": "damage", "amount": 3, "target": "enemy"},
        {"op": "damage", "amount": 3, "target": "enemy"},
    ]))

    hit = [e for e in board if e.hp != 60]
    assert len(hit) == 1
    assert hit[0].hp == 48


def test_a_card_that_aims_at_nothing_does_not_consume_a_targeting_roll():
    """The `if (card2.TargetType == TargetType.AnyEnemy)` half of that same
    autoplay branch. A free-played Skill that only draws must not eat a draw
    from `Rng.CombatTargets`, or every free play after it in the chain lands
    somewhere the mod would not have put it.

    Asserted on the RNG stream rather than on an outcome: the state of the
    generator has to be byte-identical across a play that aims at nothing.
    """
    state = make_state([_enemy(60, "a"), _enemy(60, "b")], seed=5)
    state.force_random_targeting = True
    before = state.rng.getstate()

    effects.resolve_card(state, _card("blockish", [{"op": "block",
                                                    "amount": 5}],
                                      ctype="skill"))

    assert state.rng.getstate() == before


# ---------------------------------------------------------------------------
#  The dead-enemy power state (audit sec.4/C3), and the phased-boss seam
# ---------------------------------------------------------------------------

def test_a_power_banked_on_a_phase_down_body_does_not_survive_the_revive():
    """`combat._settle_phases` revives an enemy at `hp <= 0` with phases
    remaining into a FRESH BODY -- and it already rebuilds `powers` from
    scratch, keeping only Strength and Enrage (the two the real boss keeps
    across knockdowns, test-subject dossier :240).

    That seam is what the audit flagged as unexamined at C3: between the
    killing hit and the settle, a phased boss reads as dead, so a bound aim
    CAN bank a debuff on it. The existing revive is the answer -- the debuff
    goes with the old bar -- and this pins it rather than leaving it to be
    rediscovered as a leak.
    """
    boss = _enemy(6, "boss")
    boss.phases = [{"hp": 40, "intents": [{"kind": "attack", "amount": 9}]}]
    boss.counts_for_fatal = False
    state = make_state([boss])

    effects.resolve_card(state, _card("bash", [
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "apply_power", "power": "vulnerable", "amount": 2,
         "target": "enemy"},
    ]))
    assert boss.powers.get("vulnerable") == 2      # banked on the old bar

    _settle_phases(state)
    assert boss.hp == 40
    assert "vulnerable" not in boss.powers


def test_a_bomb_banked_on_a_phase_down_body_dies_with_the_bar_too():
    """The same seam for the pile, and the reconciliation the row asked for:
    `combat._settle_phases` clears `e.bombs` at the REVIVE. That line is not
    a death rule and does not contradict the mod's corpse-Bomb semantics --
    C# never removes a `BombPower` for dying, and neither does tier0 (see
    `test_a_bomb_survives_an_ordinary_death` below). What it models is a new
    body: fresh bar, fresh moveset, nothing carried but Strength and Enrage.
    """
    boss = _enemy(6, "boss")
    boss.phases = [{"hp": 40, "intents": [{"kind": "attack", "amount": 9}]}]
    boss.counts_for_fatal = False
    state = make_state([boss])

    effects.resolve_card(state, _card("fish_flavored_bait", [
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "place_bomb", "amount": 1, "target": "enemy",
         "bomb_damage": 6},
    ]))
    assert len(boss.bombs) == 1

    _settle_phases(state)
    assert boss.bombs == []


def test_a_bomb_survives_an_ordinary_death():
    """THE DEAD-BOMB PIN. An ordinary death removes nothing: no tier0 site
    clears `bombs` for dying (the only `e.bombs = []` in `combat.py` is the
    phase revive above), and no C# site removes `BombPower` for dying either.
    So a corpse holds its pile, `move_bombs` can gather onto it and
    `detonate` can pop it -- which is what makes the corpse-detonation
    counter in the mod a real instrument rather than dead code."""
    e = _enemy(4, "e", bombs=(6,))
    state = make_state([e, _enemy(90, "other")])

    effects.resolve_card(state, _card("strike", [
        {"op": "damage", "amount": 9, "target": "enemy"},
    ]))

    assert not e.alive
    assert [b.damage for b in e.bombs] == [6]


def test_a_corpses_powers_never_tick_and_never_act():
    """The other half of C3's "consequences are unexamined": every duration
    tick, every intent and every turn hook in the engine walks
    `living_enemies`, so a debuff banked on a corpse is inert rather than
    quietly ticking down or being counted as control. Pinned structurally --
    a card banks Weak on a corpse, a full player turn is run over it, and the
    stack is exactly where it was."""
    from tier0.engine import combat

    low, other = _enemy(6, "low"), _enemy(90, "other")
    state = make_state([low, other])

    effects.resolve_card(state, _card("bash", [
        {"op": "damage", "amount": 8, "target": "enemy"},
        {"op": "apply_power", "power": "weak", "amount": 2,
         "target": "enemy"},
    ]))
    assert low.powers.get("weak") == 2

    combat._settle_phases(state)
    state.turn += 1
    for e in state.living_enemies:
        assert e is other
    assert low.powers.get("weak") == 2


# ---------------------------------------------------------------------------
#  What R210 left open, and where R211 answered it
# ---------------------------------------------------------------------------

def test_swirl_aim_question_is_answered_at_the_bind():
    """THE FLIP. This was a strict xfail for the life of `C18` -- the one
    question R210 declined to guess at -- and R211 (`EB-139`, `C20`) answered
    it: for manually-modelled play, if ANY living enemy carries an aura at
    card-play construction the WHOLE CARD binds to the lowest-HP AURA-BEARING
    enemy. The re-take inside `_op_swirl` is gone; the aura-awareness moved to
    `bind_card_aim`, where the card's damage cannot disagree with its Swirl.

    `sayu_yoohoo_windwheel`: `damage 4 target: enemy` + `swirl target: enemy`,
    the one in-scope card that carries a second aimed op. Board: the aura sits
    on the FAT body, so under the old re-take the two ops landed on different
    creatures.

    Both observables are asserted, because either alone would pass under a
    half-adoption. The damage went to the aura-bearer, not to the lowest-HP
    body; and the swirl reacted, so `_react` spread that Pyro back over every
    living body -- which is why the auraless `low` ends the play Pyro'd rather
    than clean. The wider acceptance set lives in
    `tier0/tests/test_eb139_swirl_aura_bind.py`.
    """
    low, fat = _enemy(30, "low"), _enemy(90, "fat", aura="pyro")
    state = make_state([low, fat])

    effects.resolve_card(state, _card("sayu_yoohoo_windwheel", [
        {"op": "damage", "amount": 4, "target": "enemy",
         "applies_element": False},
        {"op": "swirl", "target": "enemy"},
    ]))

    # The whole card went to the aura-bearer: the damage is on `fat`, and
    # `low` -- lowest HP, and what C18 would have aimed at -- is untouched by
    # it.
    assert fat.hp == 86, "the damage did not follow the Swirl onto the aura"
    assert low.hp == 30, "the damage stayed on the lowest-HP body"
    # And the Swirl found an aura to spread, which is the whole point of
    # aiming there.
    assert low.aura == "pyro", "the Swirl found no aura and did nothing"
