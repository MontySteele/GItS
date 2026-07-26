"""Furina sprint 1: engine-level tests for Spotlight, Encore, Fanfare and
skill-grade cadence (furina-kickoff-v0.1.md; card sheet not yet begun --
these lock the SYSTEMS, statline work comes with the sheet pass).
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, powers, resources
from tier0.engine.state import Card, CombatState, Enemy
from tier0.harness import metrics
from tier0.harness.axes import raw_axes
from tier0.pilot import policy
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def furina_card(**kw):
    """A fabricated Furina personal card (her sheet doesn't exist yet)."""
    d = dict(id="furina_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


# --- character spec / cadence ---

def test_build_furina_skeleton():
    p = loader.build_player("furina")
    assert p.character_id == "furina" and p.element == "hydro"
    assert p.cadence == "skill"
    assert p.fanfare_cap == int(C.FANFARE_CAP_FRACTION * p.max_hp) > 0
    assert "ethereal_spotlight" in p.relic_hooks
    assert loader.character_nation("furina") == "fontaine"


def test_skill_cadence_applies_element_on_skills_not_attacks():
    st = furina_state()
    e = st.enemies[0]
    effects.resolve_card(st, furina_card(
        type="attack", effects=[{"op": "damage", "amount": 4}]))
    assert e.aura is None                    # attacks never auto-apply
    effects.resolve_card(st, furina_card(
        effects=[{"op": "damage", "amount": 4}]))
    assert e.aura == "hydro"                 # skills do (Skill-grade)


def test_skill_cadence_never_touches_companion_cards():
    st = furina_state()
    # Lynette's AoE rider is explicitly applies_element: false; the plain
    # Backstroke's untagged hit must not pick up hydro from her cadence.
    effects.resolve_card(st, loader.get_card("freminet_pressurized_floe"))
    assert st.enemies[0].aura is None


# --- Encore ---

def test_encore_absorbs_after_block_before_hp():
    st = furina_state()
    p = st.player
    p.block, p.encore = 3, 10
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    assert p.hp == p.max_hp                  # 3 blocked, 5 absorbed
    assert p.encore == 5
    hits = [ev for ev in st.log if ev["event"] == "player_hit"]
    assert hits[0]["blocked"] == 3 and hits[0]["amount"] == 0
    absorbed = [ev for ev in st.log if ev["event"] == "encore_absorb"]
    assert absorbed[0]["amount"] == 5


def test_ten_block_then_one_encore_absorbs_an_eleven_damage_hit():
    st = furina_state()
    p = st.player
    p.block, p.encore = 10, 5
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 11}]
    combat._enemy_turn(st, e)
    assert p.block == 0
    assert p.encore == 4
    assert p.hp == p.max_hp


def test_encore_accounting_credits_a4_never_a3():
    """Kickoff §2 harness note, Tier 0 BINDING: without this rule she
    grows a phantom third elite axis."""
    st = furina_state()
    p = st.player
    p.block, p.encore = 3, 10
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    stats = metrics.extract(st, hp_start=p.max_hp)
    assert stats.encore_absorbed == 5
    assert stats.damage_blocked == 3         # encore NOT folded into block
    raw = raw_axes({"x": [stats]})
    assert raw["A4_sustain"] == 5.0          # healing 0 + encore 5


def test_gain_and_overdraw():
    st = furina_state()
    p = st.player
    effects.resolve_card(st, furina_card(
        effects=[{"op": "gain_encore", "amount": 4}]))
    assert p.encore == 4
    assert p.fanfare == 4 * C.FANFARE_PER_ENCORE_GAINED
    # Overdraw: greed is legal and priced (true HP, which is Fanfare flux).
    effects.resolve_card(st, furina_card(
        effects=[{"op": "spend_encore", "amount": 10}]))
    assert p.encore == 0
    assert p.hp == p.max_hp - 6
    assert p.fanfare == (4 * C.FANFARE_PER_ENCORE_GAINED
                         + 4 * C.FANFARE_PER_ENCORE_SPENT
                         + 6 * C.FANFARE_PER_HP_LOST)


def test_encore_cost_is_a_gate_not_an_overdraw():
    st = furina_state()
    p = st.player
    card = furina_card(encore_cost=3)
    p.hand.append(card)
    p.energy = 3
    assert not combat.card_playable(st, card)
    p.encore = 3
    assert combat.card_playable(st, card)
    combat.play_card(st, card)
    assert p.encore == 0 and p.hp == p.max_hp


def test_encore_resets_per_combat():
    p = loader.build_player("furina")
    p.encore, p.fanfare = 50, 20
    st = combat.run_fight(p, [make_enemy(hp=1)],
                          NULL_PILOT, seed=1)
    assert not any(ev["event"] == "encore_absorb" for ev in st.log)


# --- Fanfare ---

def test_fanfare_caps_and_is_activity_only():
    st = furina_state()
    p = st.player
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 45}]
    combat._enemy_turn(st, e)                # 45 true HP lost
    assert p.fanfare == p.fanfare_cap        # capped at %maxHP (30)
    # No passive ACCRUAL: empty turns never ADD. They now subtract, which is
    # the whole point of the rework -- so this asserts the direction of
    # travel, not stasis.
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    before = p.fanfare
    combat._player_turn(st, NULL_PILOT)
    combat._player_turn(st, NULL_PILOT)
    assert p.fanfare < before


def test_fanfare_decays_each_turn_but_never_below_the_floor():
    """F-A1/F-A2, on whichever decay shape is armed. The meter fades from
    turn 2 and rests on what was built."""
    st = furina_state()
    p = st.player
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    p.fanfare = 20

    combat._player_turn(st, NULL_PILOT)      # turn 1: no decay
    assert p.fanfare == 20, "decay must not tax the opening turn"

    combat._player_turn(st, NULL_PILOT)
    assert p.fanfare < 20, "the meter must fade from turn 2"

    p.fanfare_floor = 12
    p.fanfare = 20
    for _ in range(20):
        combat._player_turn(st, NULL_PILOT)
    assert p.fanfare == 12, "decay must clamp at the floor, not at zero"
    assert any(ev["event"] == "fanfare_decay" and ev["at_floor"]
               for ev in st.log)


def test_the_flat_decay_shape_no_longer_exists():
    """R67 (2026-07-26): proportional is the ONLY decay shape.

    This test used to be `test_flat_decay_still_works_when_the_fraction_is
    _disarmed`, and it passed by disarming the fraction to reach a branch
    the ruled world could never reach. So the suite pinned a code path
    production could not execute, while exp_furina_decay swept that same
    path and reported five identical rows as a null result. The pin is now
    the inverse: the knob is gone, and the shipped shape is measured.

    Note what this test deliberately does NOT do: disarm the fraction and
    check the result. FANFARE_DECAY_FRACTION is a RATE, not a switch --
    there is no "off" any more, and adding an `if fraction <= 0: return 0`
    guard to give it one would recreate exactly the unreachable branch R67
    just deleted, since the ruled world holds the fraction at 0.20 forever.
    So the test measures the world that exists.
    """
    assert not hasattr(C, "FANFARE_DECAY_PER_TURN")

    st = furina_state()
    p = st.player
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    p.fanfare = 20
    combat._player_turn(st, NULL_PILOT)      # turn 1 exempt
    assert p.fanfare == 20
    combat._player_turn(st, NULL_PILOT)
    assert p.fanfare == 20 - round(20 * C.FANFARE_DECAY_FRACTION)


def test_proportional_decay_takes_its_cut_and_still_clamps_at_the_floor():
    """The alternative decay shape, armed by FANFARE_DECAY_FRACTION."""
    st = furina_state()
    p = st.player
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    p.fanfare = 40
    original = C.FANFARE_DECAY_FRACTION
    try:
        C.FANFARE_DECAY_FRACTION = 0.25
        combat._player_turn(st, NULL_PILOT)      # turn 1: exempt
        assert p.fanfare == 40
        combat._player_turn(st, NULL_PILOT)
        assert p.fanfare == 30                   # 25% of 40
        combat._player_turn(st, NULL_PILOT)
        assert p.fanfare == 22                   # 25% of 30, rounded

        # Never stalls: a meter too small to round down still moves.
        p.fanfare, p.fanfare_floor = 2, 0
        combat._player_turn(st, NULL_PILOT)
        assert p.fanfare == 1

        # And the floor still wins.
        p.fanfare, p.fanfare_floor = 12, 12
        combat._player_turn(st, NULL_PILOT)
        assert p.fanfare == 12
    finally:
        C.FANFARE_DECAY_FRACTION = original


def test_proportional_20_percent_is_the_ruled_shape():
    """[USER] ruling 2026-07-24, reversing the plan's flat direction on
    measurement: proportional beats flat at BOTH tails, because a flat
    subtraction is one number for every meter level."""
    assert C.FANFARE_DECAY_FRACTION == 0.20


def test_a_floor_grant_raises_floor_cap_and_current_together():
    """F-A2/F-A3. Raising the cap alongside the floor is load-bearing: a
    grant that pushed current toward an unmoved ceiling would re-pin the
    meter, which is the failure the gradient depends on avoiding."""
    st = furina_state()
    p = st.player
    cap0, cur0 = p.fanfare_cap, p.fanfare
    resources.gain_fanfare_floor(st, 15, "test")

    assert p.fanfare_floor == 15
    assert p.fanfare_cap == cap0 + 15
    assert p.fanfare == cur0 + 15
    assert p.fanfare < p.fanfare_cap, "a grant must not seat the meter at cap"


def test_floors_are_static_value_not_accrual():
    """The no-passive-accrual law (kickoff §4) is intact, not amended: a
    floor does not grow with time, so stalling still earns nothing."""
    st = furina_state()
    p = st.player
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    resources.gain_fanfare_floor(st, 10, "test")
    floor0, cap0 = p.fanfare_floor, p.fanfare_cap
    for _ in range(8):
        combat._player_turn(st, NULL_PILOT)
    assert (p.fanfare_floor, p.fanfare_cap) == (floor0, cap0)


def test_playing_a_power_grants_a_constellation_floor_by_rarity():
    """F-A3. The grant is a rule of the engine, not a line on the card."""
    st = furina_state()
    p = st.player
    p.energy = 3
    power = loader.get_card("rapturous_applause")      # uncommon
    assert power.type == "power" and power.rarity == "uncommon"
    p.hand.append(power)
    combat.play_card(st, power)
    assert p.fanfare_floor == C.FANFARE_FLOOR_PER_POWER

    rare = loader.get_card("the_sea_is_my_stage")      # rare
    assert rare.type == "power" and rare.rarity == "rare"
    p.hand.append(rare)
    p.energy = 3
    combat.play_card(st, rare)
    # Its own printed grant (15) AND the rare Power rule (8) both land.
    assert p.fanfare_floor == (C.FANFARE_FLOOR_PER_POWER
                               + C.FANFARE_FLOOR_PER_POWER_RARE + 15)


def test_floors_and_cap_do_not_leak_across_fights_in_a_run():
    """`player` is ONE object reused every fight; a leak here would inflate
    the ceiling all run long and quietly invalidate every act-3 number."""
    st = furina_state()
    p = st.player
    base_cap = p.fanfare_cap
    resources.gain_fanfare_floor(st, 12, "test")
    assert p.fanfare_cap == base_cap + 12

    combat.run_fight(p, [Enemy(hp=1, max_hp=1, name="dummy",
                               intents=[{"kind": "attack", "amount": 0}])],
                     NULL_PILOT, seed=1)
    assert p.fanfare_floor == 0
    assert p.fanfare_cap == base_cap


def test_fanfare_inert_without_the_resource():
    st = furina_state()
    st.player.fanfare_cap = 0                # e.g. Klee
    st.enemies[0].intents = [{"kind": "attack", "amount": 10}]
    combat._enemy_turn(st, st.enemies[0])
    assert st.player.fanfare == 0
    assert not any(ev["event"] == "gain_fanfare" for ev in st.log)


def test_no_card_spends_fanfare():
    """F-A4, the sprint's defining law. Reading the meter must never move it.

    Asserted on the reader that used to be the archetype's flagship spender,
    so a re-introduced spend line fails here rather than in a winrate cell
    three passes later."""
    st = furina_state()
    p = st.player
    card = loader.get_card("crescendo")
    p.hand.append(card)
    p.energy = 3
    p.fanfare = 30

    assert combat.card_playable(st, card), "no Fanfare playability gate"
    hp0 = st.enemies[0].hp
    combat.play_card(st, card)

    assert st.enemies[0].hp == hp0 - 23        # 8 + floor(30 / 2), unchanged
    assert p.fanfare == 30, "the read must not consume the pool"
    assert not [ev for ev in st.log if ev["event"] == "fanfare_spent"]


def test_the_spend_grammar_is_rejected_by_name_not_silently_ignored():
    """F-A4's loud loader. A dead field on a live card is a card whose
    author believes it still does something."""
    with pytest.raises(ValueError) as err:
        Card.from_dict({"id": "ghost", "name": "Ghost", "cost": 1,
                        "type": "attack", "fanfare_cost": 5})
    msg = str(err.value)
    assert "fanfare_cost" in msg and "RETIRED" in msg
    assert "gain_fanfare_floor" in msg, "the error must name the way forward"


def test_reads_behave_under_floors_and_decay():
    """F-A6. Neither read grammar needed changing -- this VERIFIES that,
    which is the whole of the item. Both must see the live pool: a floor
    keeps a read online through a lull, and decay walks it back down.
    """
    st = furina_state()
    p = st.player
    crescendo = loader.get_card("crescendo")          # 8 + 1_per_2_fanfare
    entrance = loader.get_card("dramatic_entrance")   # if fanfare_at_least_5

    p.fanfare = 0
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 0
    assert not effects._predicate(st, "fanfare_at_least_5")

    # A floor holds both reads online with no activity at all...
    resources.gain_fanfare_floor(st, 12, "test")
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 6
    assert effects._predicate(st, "fanfare_at_least_5")

    # ...and decay cannot take them below it.
    p.hand, p.draw_pile, p.discard_pile = [], [], []
    for _ in range(6):
        combat._player_turn(st, NULL_PILOT)
    assert p.fanfare == 12
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 6

    # Above the floor, decay is visible in the read itself. Expressed
    # against the proportional shape, which R67 made the only one -- the
    # old form subtracted the flat FANFARE_DECAY_PER_TURN (5) and agreed
    # with the real answer only by the accident that 25//2 and 24//2 are
    # both 12.
    p.fanfare = 30
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 15
    combat._player_turn(st, NULL_PILOT)
    assert effects._bonus_formula(st, "1_per_2_fanfare") == \
        (30 - round(30 * C.FANFARE_DECAY_FRACTION)) // 2
    assert crescendo and entrance                      # ids exist on the sheet


def test_every_read_is_instrumented_at_the_moment_it_reads():
    """The gate-(2) instrument. Sampled at READ time, not turn start: the
    pool refills mid-turn and spills, so a turn-start sample can look
    healthy while every read still lands on a pinned meter."""
    st = furina_state()
    p = st.player
    p.fanfare = p.fanfare_cap
    st.log.clear()

    effects._bonus_formula(st, "1_per_2_fanfare")
    effects._predicate(st, "fanfare_at_least_5")
    reads = [ev for ev in st.log if ev["event"] == "fanfare_read"]
    assert {ev["kind"] for ev in reads} == {"bonus_formula", "threshold"}
    assert all(ev["at_cap"] for ev in reads)

    # At-cap alone cannot see the floor-stacking failure: a grant raises the
    # cap alongside the floor, so a meter pinned on its FLOOR never reads
    # at-cap. Both pins are recorded for exactly this reason.
    st2 = furina_state()
    resources.gain_fanfare_floor(st2, 10, "test")
    st2.log.clear()
    effects._bonus_formula(st2, "1_per_2_fanfare")
    ev = next(e for e in st2.log if e["event"] == "fanfare_read")
    assert ev["at_floor"] and not ev["at_cap"]


def test_pilot_values_the_smooth_fanfare_reads():
    """F-B1 turned these two commons from binary gates into smooth reads,
    so the pilot must now see a value that MOVES with the meter rather than
    stepping once. A pilot blind to the rider would price the archetype's
    own payoffs at their printed number and play straight past them."""
    st = furina_state()
    entrance = loader.get_card("dramatic_entrance")   # 6 + 1 per 4 Fanfare
    ovation = loader.get_card("thunderous_ovation")   # 7 + 1 per 4 Fanfare

    st.player.fanfare = 0
    assert policy._expected_damage(st, entrance) == 6
    assert policy._raw_block(st, ovation) == 7

    st.player.fanfare = 4        # one step
    assert policy._expected_damage(st, entrance) == 7
    assert policy._raw_block(st, ovation) == 8

    st.player.fanfare = 20       # five steps -- no threshold cliff anywhere
    assert policy._expected_damage(st, entrance) == 11
    assert policy._raw_block(st, ovation) == 12


def test_the_common_fanfare_readers_are_live_from_turn_one():
    """F-A4 on the two commons that used to be the archetype's gates.

    They are now un-gated readers: playable at 0 Fanfare, better at 5, and
    the meter is untouched either way. (F-B1 replaces the binary threshold
    with a smooth per-N read; that is card DESIGN and lands there, not
    here -- this pins only that the gate and the payment are gone.)
    """
    for cid, get, low, high in (
            ("dramatic_entrance",
             lambda st: st.enemies[0].hp, None, None),
            ("thunderous_ovation",
             lambda st: st.player.block, None, None)):
        st = furina_state()
        p = st.player
        card = loader.get_card(cid)
        p.hand.append(card)
        p.energy = 1
        p.fanfare = 0
        assert combat.card_playable(st, card), f"{cid} must not be gated"

        p.fanfare = 5
        combat.play_card(st, card)
        assert p.fanfare == 5, f"{cid} must not spend the meter"
        assert not [ev for ev in st.log if ev["event"] == "fanfare_spent"]


# --- Spotlight ---

def _stock_deck(p, *card_ids):
    p.draw_pile.extend(loader.get_card(cid) for cid in card_ids)


def test_selector_v5_chooses_between_ready_guest_cast_and_center_stage():
    """Guest Cast is a hand-level tactical choice, not a depth check."""
    st = furina_state()
    _stock_deck(st.player, "chevreuse_interdiction_fire",
                "lynette_box_trick")
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == "furina"       # no Companion ready now
    st.player.hand.append(loader.get_card("lynette_box_trick"))
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST


def test_selector_v5_designates_guest_cast_for_a_generated_guest():
    st = furina_state()                       # one enemy: crowd rule bypassed
    effects.resolve_card(st, loader.get_card("an_invitation"))
    guest = st.player.hand[0]
    assert guest.generated_by_guest_star and guest.character
    effects.resolve_card(st, loader.get_card("ethereal_spotlight"))
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST


def test_spotlight_pilot_invites_then_designates_before_playing_guest():
    st = furina_state()
    st.player.hand = [loader.get_card("an_invitation"),
                      loader.get_card("ethereal_spotlight")]
    st.player.energy = 3
    pilot = make_pilot(loader.pilot_weights("spotlight"))
    invitation = pilot(st)
    assert invitation.id == "an_invitation"
    combat.play_card(st, invitation)
    assert any(c.generated_by_guest_star for c in st.player.hand)
    assert pilot(st).id == "ethereal_spotlight"


def test_guest_cast_persists_after_a_generated_guest_performs():
    st = furina_state()
    guest = Card(id="temporary_guest", name="Guest", cost=0, type="skill",
                 character="lynette", generated_by_guest_star=True)
    st.player.hand = [guest]
    st.player.spotlight = C.SPOTLIGHT_GUEST_CAST
    combat.play_card(st, guest)
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST
    assert not any(e["event"] == "spotlight_returned" for e in st.log)


def test_ovation_spend_boost_converts_spend_events_into_turn_boost():
    """R32.1 flip (pass 3): with Standing Ovation up, every Encore spend
    EVENT grants turn-scoped Spotlighted percentage points through the
    §2.2a pipe; the window closes at turn end (EXPIRING), and a
    dry-buffer spend is not an event."""
    st = furina_state()
    p = st.player
    p.powers["ovation_spend_boost"] = 10
    p.encore = 5
    resources.spend_encore(st, 2)
    assert p.powers.get("spotlight_mult_bonus_turn", 0) == 10
    resources.spend_encore(st, 3)
    assert p.powers["spotlight_mult_bonus_turn"] == 20
    powers.on_turn_end(st, p)
    assert "spotlight_mult_bonus_turn" not in p.powers
    resources.spend_encore(st, 2)                # buffer is dry: no event
    assert "spotlight_mult_bonus_turn" not in p.powers


def test_knob_exercise_counter_counts_companion_reads_only():
    """R33 lint-law (DECISIONS 87): dead-knob claims require an exercise
    counter. The tally increments exactly when SPOTLIGHT_BASE_MULT is
    read into a live computation -- the companion branch -- and never on
    the self branch. E1's null would have shown 0 reads per cell."""
    st = furina_state()
    p = st.player
    effects.reset_knob_reads()
    p.spotlight = "furina"
    effects.spotlight_mult(st, furina_card())
    assert effects.KNOB_READS.get("SPOTLIGHT_BASE_MULT", 0) == 0
    p.spotlight = "chevreuse"
    effects.spotlight_mult(st, loader.get_card("chevreuse_interdiction_fire"))
    assert effects.KNOB_READS["SPOTLIGHT_BASE_MULT"] == 1
    effects.reset_knob_reads()
    assert effects.KNOB_READS == {}


def test_spotlight_force_oracle_arms_bypass_selector_v5():
    """Diagnostic arms force either mode; companion has no self fallback."""
    st = furina_state()          # starter: 10 furina cards in draw pile
    p = st.player
    selector = loader.get_card("ethereal_spotlight")
    try:
        effects.SPOTLIGHT_FORCE = "companion"
        effects.resolve_card(st, selector)
        assert p.spotlight is None           # no companion cards: no aim
        _stock_deck(p, "chevreuse_interdiction_fire")
        effects.resolve_card(st, selector)
        assert p.spotlight == C.SPOTLIGHT_GUEST_CAST
        effects.SPOTLIGHT_FORCE = "self"
        effects.resolve_card(st, selector)
        assert p.spotlight == "furina"
    finally:
        effects.SPOTLIGHT_FORCE = None


def test_spotlight_empowers_damage_and_block_only():
    # R16 world: the empowerment is CARD-MEDIATED. The base mult is the
    # relic's residual passive (E1-swept); her cards grant the rest via
    # spotlight_mult_bonus. This test pins the card-granted path.
    st = furina_state()
    st.player.spotlight = "charlotte"
    st.player.powers["spotlight_mult_bonus"] = 50    # e.g. two top_billing
    e = st.enemies[0]
    mult = C.SPOTLIGHT_BASE_MULT + 0.5
    # Damage: Freezing Point prints 4 -> int(4 * mult).
    _stock_deck(st.player, "charlotte_freezing_point")   # draw target
    effects.resolve_card(st, loader.get_card("charlotte_freezing_point"))
    dmg = [ev for ev in st.log if ev["event"] == "damage"][0]
    assert dmg["base"] == int(4 * mult)
    # Block: Frosthelm prints 4 now + 4 next turn -> scaled both.
    effects.resolve_card(st, loader.get_card("charlotte_enduring_frosthelm"))
    assert st.player.block == int(4 * mult)
    assert st.player.powers["block_next_turn"] == int(4 * mult)
    # §2.2a extension: numbers only, never turn-economy or power stacks --
    # Snappy Silhouette's Vulnerable 2 and cantrip stay printed.
    effects.resolve_card(st, loader.get_card("charlotte_snappy_silhouette"))
    assert e.powers["vulnerable"] == 2


def test_unspotlighted_and_untagged_cards_unchanged():
    st = furina_state()
    st.player.spotlight = "charlotte"
    effects.resolve_card(st, loader.get_card("chevreuse_interdiction_fire"))
    dmg = [ev for ev in st.log if ev["event"] == "damage"][0]
    assert dmg["base"] == 7                  # not the designated character
    st2 = furina_state()
    st2.player.spotlight = "furina"
    effects.resolve_card(st2, loader.get_card("strike"))   # untagged
    dmg2 = [ev for ev in st2.log if ev["event"] == "damage"][0]
    assert dmg2["base"] == 6                 # strike prints 6, unscaled


def test_self_spotlight_has_no_numeric_multiplier():
    """Self aim is 1.0x, and it is 1.0x in CODE.

    The `assert C.SPOTLIGHT_SELF_MULT == 1.0` that used to open this test
    was struck by R67 with the constant: it read like a second check and
    was worth nothing, because spotlight_mult() hard-codes its self-aim
    early return and never consulted the constant. Had someone edited that
    knob to 1.5 the assert would have failed while behavior was unmoved --
    the test would have reported a change that could not happen. The
    behavioral assert below is the one that was ever load-bearing.
    """
    st = furina_state()
    st.player.spotlight = "furina"
    st.player.powers["spotlight_mult_bonus"] = 50
    st.player.powers["spotlight_flat_damage"] = 3
    effects.resolve_card(st, furina_card(
        effects=[{"op": "damage", "amount": 4, "applies_element": False}]))
    dmg = [ev for ev in st.log if ev["event"] == "damage"][0]
    assert dmg["base"] == 4


def test_only_center_stage_spotlighted_plays_generate_fanfare():
    st = furina_state()
    p = st.player
    p.spotlight = C.SPOTLIGHT_GUEST_CAST
    card = loader.get_card("lynette_box_trick")
    p.hand.append(card)
    p.energy = 3
    combat.play_card(st, card)
    assert st.spotlighted_cards_this_turn == 1
    assert p.fanfare == 0
    p.spotlight = "furina"
    own = furina_card()
    p.hand.append(own)
    combat.play_card(st, own)
    assert p.fanfare == C.FANFARE_PER_SPOTLIGHT_CARD


def test_designation_moves_freely_and_duplicates_inert():
    st = furina_state()
    st.player.hand.append(loader.get_card("chevreuse_interdiction_fire"))
    sel = loader.get_card("ethereal_spotlight")
    effects.resolve_card(st, sel)
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST
    events = sum(1 for ev in st.log if ev["event"] == "spotlight_designated")
    effects.resolve_card(st, sel)            # same aim: inert re-aim
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST
    assert sum(1 for ev in st.log
               if ev["event"] == "spotlight_designated") == events
    # Once no Companion is ready, the selector returns to Center Stage.
    st.player.hand.clear()
    effects.resolve_card(st, sel)
    assert st.player.spotlight == "furina"


def test_selector_delivered_each_turn_and_vanishes():
    st = furina_state()
    combat._player_turn(st, NULL_PILOT)
    assert not any(c.id == "ethereal_spotlight" for c in st.player.hand)
    assert any(c.id == "ethereal_spotlight" for c in st.player.exhaust_pile)
    assert not any(c.id == "ethereal_spotlight"
                   for c in st.player.discard_pile)   # never loot
    assert any(ev["event"] == "selector_granted" for ev in st.log)


def test_per_turn_cap_schematized_but_off():
    assert C.SPOTLIGHT_CARDS_PER_TURN_CAP is None    # kickoff §3.2: OFF;
    # arming it is a ruling, and this lock makes turning it on deliberate.


# --- DoT chip routes through Encore too ---

def test_dot_absorbed_by_encore():
    st = furina_state()
    p = st.player
    p.encore = 3
    powers.apply_power(st, p, "dot", 5)
    powers.on_turn_start(st, p)
    assert p.hp == p.max_hp - 2 and p.encore == 0
    assert sum(ev["amount"] for ev in st.log
               if ev["event"] == "encore_absorb") == 3
