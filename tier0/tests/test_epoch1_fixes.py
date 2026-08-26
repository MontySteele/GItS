"""EPOCH 1 (2026-07-26): the four number-moving fixes, pinned.

R66 (archetype registry) plus audit s1.4, s1.7 and s2.4. All four were
landed as one commit group with one archive event and one re-baseline,
because each moves measured numbers and separate landings would have needed
separate baselines.

Every defect here was SILENT. None crashed, none failed a test, and each one
produced numbers that looked exactly like correct numbers -- which is why
they need pins rather than a note in a doc.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, reactions
from tier0.engine.state import Bomb, CombatState
from tier0.tests.conftest import make_enemy
from tier05 import draft, run_metrics


# --- R66: the archetype registry -------------------------------------------

def test_kokomis_archetypes_are_the_sheets():
    """The ratified sheet is canonical. ("garment", "ward", "conscript")
    matched zero cards, predated the v0.2 sheet pass, and its conscript term
    had already been retired by the lore pass."""
    assert draft.ROSTER_ARCHETYPES["kokomi"] == ("priest", "commander",
                                                 "assist")


def test_every_registered_archetype_exists_on_a_real_card():
    """The general form of R66's defect, for the whole roster.

    A registry naming tags no card carries is not a small error: it makes
    the drafter's synergy term structurally unreachable, so it scores pure
    static power and reports the result as evidence about drafting. This
    would have caught Kokomi's tuple the day it drifted.
    """
    by_character: dict[str, set[str]] = {}
    for card in loader._card_index().values():
        owner = getattr(card, "character", None)
        if owner:
            by_character.setdefault(owner, set()).update(card.archetypes or ())
    for character, family in draft.ROSTER_ARCHETYPES.items():
        tagged = by_character.get(character, set())
        for archetype in family:
            assert archetype in tagged, (
                f"{character}: registry names {archetype!r}, which exists on "
                f"no card in her pool. Tagged: {sorted(tagged)}")


def test_klee_and_furina_tuples_did_not_move():
    """R66 explicitly does not move their numbers."""
    assert draft.ROSTER_ARCHETYPES["klee"] == ("demolition", "spark",
                                               "reaction")
    assert draft.ROSTER_ARCHETYPES["furina"] == ("salon", "spotlight",
                                                 "fanfare")


def test_the_policy_stamp_bumped():
    # 3 was R66's bump; 4 is R124 (EB-31p); 5 is EB-24p (the pilot reads
    # reaction_triggered_this_turn); 6 is EB-29t (Enrage skill tax +
    # Intangible per-hit cap, the promoted Test Subject reads); 7 is R176
    # (the pilot values copy_companion_in_hand / replay_next_companion --
    # EB-17p's 40,396 draws / 0 plays was pilot scoring, not an unreachable
    # in-hand condition; every Klee tier0.5 number moves with it); 8 is
    # EB-118 Phase 2A (`PILOT_POLICIES_ENABLED` flips True -- Klee's bomb
    # placement and Kokomi's chosen exhaust become decisions instead of
    # heuristics, and `C.PILOT_WEIGHTS_VERSION` moves 2 -> 3 in the same
    # edit because the pair's eleven weights are read for the first time);
    # 9 is EB-118 Phase 2C, the SECOND and last of Phase 2's two activation
    # windows (`MODE_CHOOSER_ENABLED` flips True -- a `choose_one` stops
    # resolving a fixed index and asks the pilot, and
    # `C.PILOT_WEIGHTS_VERSION` moves 3 -> 4 in the same edit for the same
    # reason). Two flags, two windows, two bumps: R191.
    # 10 is EB-118 Phase-3 Window 3 (R211) and it is NOT a flip -- no switch
    # was staged for it. `policy.exhaust_victim`'s DEFAULT payout hook becomes
    # `formula_aware_payout`, so a card whose damage scales with what you
    # exhausted finally pulls on which card the pilot picks, and
    # `C.PILOT_WEIGHTS_VERSION` moves 4 -> 5 in the same edit for the weight
    # that arrives with it. What re-baselines is narrower than the stamp
    # suggests and is asserted rather than argued: the hook pays zero for any
    # card printing no selection formula, so every other chosen-Exhaust
    # carrier's pick is provably unchanged (test_eb118_policies).
    # 11 is the SCORER-LITERACY window (2026-08-26) -- ONE window under R207
    # carrying four items, none of which is a flip and none of which moves a
    # printed number or a drafter dial: EB-143 (the Spark hold-versus-spend
    # term, and the ONE new weight, so `C.PILOT_WEIGHTS_VERSION` moves 5 -> 6
    # in the same edit), EB-144 (five predicates over ten sheet rows read live
    # at score time, plus both Salon verbs valued off the resolver's own
    # `salon_tick_amount`), EB-145 (the score forecasts its own chosen-exhaust
    # selection, so Tide of Names and Pearl Barrage stop being priced at their
    # base) and EB-129 (Book of Five Rings chunk credit at event valuation).
    # Archive scope is roster combat + tier-0.5 only: both anchors are
    # provably unmoved (test_eb144_predicate_literacy). ONE re-baseline is
    # owed at this cell and has NOT been taken at the bump.
    assert draft.POLICY_VERSION == 11


def test_the_starvation_alarm_keys_on_the_cohorts_own_archetypes():
    """R66's ab.py half: a latent bug for EVERY non-Klee character.

    The alarm read draft.ARCHETYPES -- Klee's three. A Furina cohort can
    never populate any of them, so all three scored 0.0 and the alarm fired
    on every run. P1 predicts these go to exactly zero for Kokomi.
    """
    for character in ("furina", "kokomi"):
        deck = [c for c in loader._card_index().values()
                if getattr(c, "character", None) == character]
        family = draft.archetypes_for(deck)
        assert family == draft.ROSTER_ARCHETYPES[character]
        assert family != draft.ARCHETYPES, (
            f"{character} must not be graded against Klee's archetypes")


# --- audit s1.4: the Tamakushi refresh --------------------------------------

def _kokomi_state() -> CombatState:
    return CombatState(player=loader.build_player("kokomi"),
                       enemies=[make_enemy(hp=100)], rng=random.Random(0))


def test_the_garment_refresh_never_shortens_an_upgraded_summon():
    """audit s1.4: the refresh hard-set KURAGE_DURATION.

    Playing the Garment after an UPGRADED summon (kurage_turns +1, so 2
    turns) took the jellyfish back to 1 and deleted the turn the upgrade had
    paid for. R56/R57's "restoring a longer duration is safe" was true of
    the design and false of the wiring.
    """
    st = _kokomi_state()
    st.player.powers["kurage_summon"] = C.KURAGE_DURATION + 1   # upgraded

    effects._op_apply_power(
        st, {"op": "apply_power", "power": "ceremonial_garment",
             "amount": 1, "target": "self"}, None)

    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION + 1, (
        "the refresh must top the timer up, never cut it down")
    refreshed = [e for e in st.log if e["event"] == "kurage_refreshed"]
    assert refreshed and refreshed[-1]["turns"] == C.KURAGE_DURATION + 1, (
        "the emitted turn count must agree with the power it just set")


def test_the_garment_refresh_still_restores_a_decayed_summon():
    """The behaviour the link exists for, unchanged: the E-into-Q loop."""
    st = _kokomi_state()
    st.player.powers["kurage_summon"] = 1

    effects._op_apply_power(
        st, {"op": "apply_power", "power": "ceremonial_garment",
             "amount": 1, "target": "self"}, None)

    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION


def test_the_garment_does_not_conjure_a_kurage_from_nothing():
    """The guard the fix must not remove: the Burst refreshes, it does not
    summon."""
    st = _kokomi_state()
    st.player.powers.pop("kurage_summon", None)

    effects._op_apply_power(
        st, {"op": "apply_power", "power": "ceremonial_garment",
             "amount": 1, "target": "self"}, None)

    assert not st.player.powers.get("kurage_summon", 0)


# --- audit s1.7: overkill in the splash paths -------------------------------

def _swarm_state(hp: int = 3, n: int = 3) -> CombatState:
    return CombatState(
        player=loader.build_player("klee"),
        enemies=[make_enemy(hp=hp, name=f"add{i}") for i in range(n)],
        rng=random.Random(0))


def test_reaction_splash_does_not_credit_overkill():
    """audit s1.7: A6 is a ratified elite axis summed from these emitted
    amounts, and it over-read hardest for exactly the reaction archetypes it
    grades."""
    st = _swarm_state(hp=3, n=1)
    enemy = st.enemies[0]

    reactions._splash(st, enemy, 8)

    dmg = [e for e in st.log if e["event"] == "damage"][-1]
    assert dmg["amount"] == 3, "8 into a 3 HP add is 3 damage dealt, not 8"
    assert enemy.hp == -5, "the HP hit itself is unclamped; only the count is"


def test_detonation_splash_does_not_credit_overkill():
    """The same defect on the wider path: detonation splash hits EVERY
    living enemy, so it over-read hardest against boards of small adds."""
    st = _swarm_state(hp=2, n=3)
    st.player.powers["detonation_splash"] = 9      # Blazing Delight
    target = st.enemies[0]
    target.bombs = [Bomb(damage=1, element=None)]

    effects.detonate_bombs(st, target)

    splash = [e for e in st.log if e["event"] == "damage"
              and e.get("source") == "detonation_splash"]
    assert splash, "the splash path must actually have run"
    for ev in splash:
        assert ev["amount"] <= 2, (
            f"9 splash credited {ev['amount']} against a 2 HP add")


def test_shatter_reports_one_answer_not_two():
    """audit s1.7 (the smaller half): the emitted amount was clamped and the
    RETURNED total was not, so one function gave two different answers for
    the same hit depending which you read."""
    st = _swarm_state(hp=2, n=1)
    enemy = st.enemies[0]
    enemy.frozen = True
    enemy.hp = 40                       # survives the hit; shatter overkills
    enemy.max_hp = 40

    # Land an attack that leaves less HP than the Shatter will deal.
    enemy.hp = 1 + C.SHATTER_DAMAGE
    returned = effects.deal_damage_to_enemy(st, enemy, 1, source="attack")

    emitted = sum(e["amount"] for e in st.log if e["event"] == "damage")
    assert returned == emitted, (
        f"returned {returned} but emitted {emitted}; the docstring promises "
        f"'damage actually dealt to HP' and both must mean that")


def test_a_normal_hit_still_counts_in_full():
    """Positive control: the clamp must bite only on overkill."""
    st = _swarm_state(hp=50, n=1)
    reactions._splash(st, st.enemies[0], 8)
    dmg = [e for e in st.log if e["event"] == "damage"][-1]
    assert dmg["amount"] == 8


# --- audit s2.4: survival_profile's axis -------------------------------------

class _FakeRun:
    def __init__(self, node_kinds, hp_by_node, n_acts=1):
        self.node_kinds = node_kinds
        self.hp_by_node = hp_by_node
        self.n_acts = n_acts


def test_survival_profile_does_not_size_its_axis_off_the_first_run():
    """audit s2.4: it read results[0].node_kinds and treated one run's room
    layout as the cohort's axis.

    Under RUNTEMPLATE 6+ paths differ per run, so the scalars cross-sampled
    HP from floors that were different room types run to run. The module's
    own docstring already forbids this for the HP bands.

    The pin: reordering the cohort must not change the answer. Under the old
    code it did, because results[0] decided everything.
    """
    floors = C.MAP_FLOORS
    fighter = _FakeRun(["N"] * floors, [10] * floors)
    rester = _FakeRun(["R"] * floors, [50] * floors)

    a = run_metrics.survival_profile([fighter, rester], max_hp=100)
    b = run_metrics.survival_profile([rester, fighter], max_hp=100)

    assert a == b, "the profile must not depend on which run came first"


def test_non_fight_floors_are_not_read_as_survival_samples():
    """A rest stop's HP entry is a carried-over value. Counting it as a
    fight sample is the defect in miniature."""
    floors = C.MAP_FLOORS
    # One run fights every floor at 10 HP; one rests every floor at 90.
    kinds_fight = ["N"] * floors
    kinds_rest = ["R"] * floors
    runs = [_FakeRun(kinds_fight, [10] * floors),
            _FakeRun(kinds_rest, [90] * floors)]

    out = run_metrics.survival_profile(runs, max_hp=100)

    # Only the fighting run contributes, so the median is its 10%.
    assert out["median_hp_pct_by_fight"], out
    assert all(abs(p - 0.10) < 1e-9 for p in out["median_hp_pct_by_fight"]), \
        out["median_hp_pct_by_fight"]


def test_a_short_dead_run_does_not_truncate_the_axis():
    """results[0] being a dead run used to shrink the axis to its length."""
    floors = C.MAP_FLOORS
    dead_early = _FakeRun(["N"], [5])                 # died on floor 0
    full = _FakeRun(["N"] * floors, [60] * floors)

    out = run_metrics.survival_profile([dead_early, full], max_hp=100)

    assert len(out["median_hp_pct_by_fight"]) == floors, (
        "the axis is FLOORS, not the shortest run's walked path")


def test_dead_runs_still_contribute_zero_rather_than_vanishing():
    """The anti-survivorship rule the fix must preserve: otherwise later
    medians are conditional on survival and an early death makes the
    reported act-health curve look healthier."""
    floors = C.MAP_FLOORS
    runs = [_FakeRun(["N"], [0])] * 3 + [_FakeRun(["N"] * floors,
                                                  [80] * floors)]

    out = run_metrics.survival_profile(runs, max_hp=100)

    # Three of four runs are dead past floor 0, so the median there is 0.
    assert out["median_hp_pct_by_fight"][-1] == 0.0, \
        out["median_hp_pct_by_fight"]
