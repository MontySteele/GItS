"""EB-31: the sim half of Touch of Orobas, for Kokomi and Furina.

Extends two files rather than replacing either. test_starter_relic_upgrades.py
owns the C#-side invariants (every starter overrides the BaseLib hook, the
upgraded form is Ancient rarity and pooled) plus the EB-31 membership gate
(every upgraded form has an owner-gated tier05 row). test_relics_combat_start.py
owns the with/without deltas for the combat_start_* family, which is where
Klee's variant lives.

Neither could host these, and the reason is the whole point of the pass: Klee's
upgrade ADDS an effect at combat start, and these two do not. They CHANGE A
RULE the kit already runs -- the exhaust funnel's accrual rate, and the
Spotlight's mode exclusivity -- so they have no combat-start delta to assert
and are read where the rule runs instead.

CONVENTIONS KEPT FROM BOTH. Every assertion is a with/without PAIR against an
otherwise identical player, which is the seen-to-fail guard: an inert hook (the
engine dropping the effect) collapses the delta to zero and the test fails. And
the relic_effect dicts are inlined verbatim from tier05/content/relics.yaml so
this tier0 test stays layer-pure -- no tier05 import, the boundary runs the
other way.

BOTH DIRECTIONS, per the task's own framing: the upgraded form's effects, AND
the replacement semantics (what the upgrade takes away, and what it must not
touch). The second half is where these relics have historically gone wrong --
`PearlOfInsightRelic` shipped as a no-op with a lying tooltip, and
`CurtainNeverFalls` shipped unmodelled entirely.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, refpowers, relics, resources
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

# --- the two rows, inlined verbatim from tier05/content/relics.yaml ---------

PEARL_OF_INSIGHT = [
    # STAGED 2 -> 4 (EB-74 B-alone): this fixture is a THIRD copy of the two
    # numbers, beside tier05/content/relics.yaml and the C# literal, so the
    # base-rate change moves it too.
    {"hook": "charge_per_exhaust", "amount": 4},
    {"hook": "burst_per_exhaust", "amount": 4},
]
CURTAIN_NEVER_FALLS = [{"hook": "spotlight_both_modes"}]


def kokomi_state(relic_effects=None, seed=0):
    p = loader.build_player("kokomi")
    p.relic_effects = list(relic_effects or [])
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def kokomi_card(**kw):
    d = dict(id="kokomi_test", name="t", cost=0, type="skill",
             character="kokomi")
    d.update(kw)
    return Card(**d)


def furina_state(relic_effects=None, seed=0):
    p = loader.build_player("furina")
    p.relic_effects = list(relic_effects or [])
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def furina_card(**kw):
    d = dict(id="furina_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


def companion_card(**kw):
    """A Companion card as the sheets actually write one.

    Two details are load-bearing and both were got wrong first time. A
    Companion is `role_c` (or the `companion` tag), NOT the `companion` field,
    which holds a spec dict. And `character` is the COMPANION's own id --
    `clorinde`, never `furina` -- which is precisely what keeps Center Stage
    (`card.character == p.character_id`) off Companions in the base engine and
    what the upgrade must not disturb.
    """
    d = dict(id="companion_test", name="guest", cost=0, type="skill",
             character="clorinde", role_c="applier")
    d.update(kw)
    return Card(**d)


# ===========================================================================
# Kokomi: Pearl of Insight -- the doubled per-exhaust rate.
# ===========================================================================

def test_pearl_of_insight_doubles_the_exhaust_rate():
    """The effect, as a with/without delta on the ONE exhaust funnel."""
    st = kokomi_state(PEARL_OF_INSIGHT)
    refpowers.exhaust_card(st, kokomi_card())
    assert st.player.charge == 4          # STAGED: was 2
    assert st.player.burst_energy == 4

    st_no = kokomi_state()
    refpowers.exhaust_card(st_no, kokomi_card())
    assert st_no.player.charge == C.CHARGE_PER_EXHAUST == 2   # STAGED: was 1
    assert st_no.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST == 2


def test_the_doubled_rate_is_exactly_twice_the_base_rate():
    """Pinned as a RATIO, not as two literals.

    C# declares `ChargePerExhaust = KokomiConstants.ChargePerExhaust * 2` and
    the compiler enforces that link; nothing enforced it sim-side, where the
    row carries resolved numbers. Asserting the ratio is what keeps a retune
    of the base constant from silently un-doubling the upgrade -- the sim row
    would still say 2 while the base said 2.
    """
    charge = next(fx["amount"] for fx in PEARL_OF_INSIGHT
                  if fx["hook"] == "charge_per_exhaust")
    burst = next(fx["amount"] for fx in PEARL_OF_INSIGHT
                 if fx["hook"] == "burst_per_exhaust")
    assert charge == 2 * C.CHARGE_PER_EXHAUST
    assert burst == 2 * C.KOKOMI_BURST_PER_EXHAUST


def test_the_rate_REPLACES_the_base_rather_than_adding_to_it():
    """The replacement semantics, and they are not cosmetic.

    C# `ExhaustCharge` is a ternary -- it picks the relic's value or the base
    value, never their sum. Additive would give (STAGED) 2+4=6 Charge per
    exhaust,
    which is a 3x upgrade wearing a 2x tooltip. Same class of defect as the
    original bug (panel and funnel disagreeing), inverted.
    """
    st = kokomi_state(PEARL_OF_INSIGHT)
    refpowers.exhaust_card(st, kokomi_card())
    assert st.player.charge == 4, "additive would read 6"   # STAGED: was 2/3
    assert st.player.burst_energy == 4, "additive would read 6"


def test_the_upgrade_rides_the_funnel_and_not_one_exhaust_site():
    """Mid-card exhausts, not just played ones.

    The accrual law is structural -- "whenever one of your cards is Exhausted"
    passes through a single funnel, which is why the sim reads the rate there
    rather than at each site. A rate wired at the played-exhaust site only
    would pass the test above and silently pay base at every other door.
    """
    st = kokomi_state(PEARL_OF_INSIGHT)
    st.player.hand = [kokomi_card(id="fodder_a"), kokomi_card(id="fodder_b")]
    burner = kokomi_card(
        id="burner", effects=[{"op": "exhaust_from", "amount": 2}])
    st.player.hand.append(burner)
    st.player.energy = 3
    combat.play_card(st, burner)
    assert st.player.charge == 8          # 2 victims x the doubled rate
    #                                       (STAGED: was 4)


def test_the_mustered_exhaust_bucket_survives_the_upgrade():
    """C5's separate reporting bucket is accrual BOOKKEEPING, not a rate.

    P8 is a claim about conscript income specifically, so a mustered
    recruit's rotation has to stay distinguishable in the log. The upgrade
    changes how much each exhaust pays and must not change which bucket it
    pays into.
    """
    st = kokomi_state(PEARL_OF_INSIGHT)
    card = kokomi_card(id="recruit")
    card.conscripted = True
    refpowers.exhaust_card(st, card)
    assert any(ev["event"] == "gain_charge"
               and ev["source"] == "exhaust_muster"
               and ev["amount"] == 4       # STAGED: was 2
               for ev in st.log)


def test_the_upgrade_is_inert_without_the_charge_engine():
    """The gate, on the starter's own hook rather than on a character id.

    Each variant is its own owner-gated row, so a Kokomi row should never
    reach anyone else. This is the belt as well as the braces -- and it is
    asserted at the funnel, which is already inside the `tamakushi_casket`
    branch: a player with no Charge engine never reaches the rate at all.
    """
    p = loader.build_player("ref_ironclad")
    p.relic_effects = list(PEARL_OF_INSIGHT)
    st = CombatState(player=p, enemies=[make_enemy(hp=50)],
                     rng=random.Random(0))
    refpowers.exhaust_card(st, kokomi_card())
    assert p.charge == 0 and p.burst_energy == 0


def test_exhaust_accrual_returns_the_base_rates_untouched_by_default():
    """The reader itself, at the layer boundary the whole module rests on.

    Every public function in engine/relics.py opens on `if not
    player.relic_effects`, so the frozen battery is a dead branch. A reader
    that returned anything but its arguments there would move the battery.
    """
    p = loader.build_player("kokomi")
    assert p.relic_effects == []
    assert relics.exhaust_accrual(p, 1, 2) == (1, 2)
    assert relics.exhaust_accrual(p, 7, 9) == (7, 9)


# ===========================================================================
# Furina: The Curtain Never Falls -- both Spotlight modes, permanently.
# ===========================================================================

def test_both_modes_light_her_cards_and_companions_at_once():
    """The effect. Base Furina has to choose; upgraded Furina does not."""
    st = furina_state(CURTAIN_NEVER_FALLS)
    assert effects.is_spotlighted(st, furina_card())
    assert effects.is_spotlighted(st, companion_card())
    assert st.player.spotlight is None, (
        "the upgrade must not need a designation -- that is the point")

    st_no = furina_state()
    assert not effects.is_spotlighted(st_no, furina_card())
    assert not effects.is_spotlighted(st_no, companion_card())


def test_base_furina_still_gets_exactly_one_mode():
    """Non-vacuity: the pair above only means something while the base rule
    is still exclusive."""
    st = furina_state()
    st.player.spotlight = "furina"
    assert effects.is_spotlighted(st, furina_card())
    assert not effects.is_spotlighted(st, companion_card())

    st.player.spotlight = C.SPOTLIGHT_GUEST_CAST
    assert not effects.is_spotlighted(st, furina_card())
    assert effects.is_spotlighted(st, companion_card())


def test_the_upgrade_removes_the_exclusivity_not_the_targeting():
    """R2 reading 1 ([USER], ruled during implementation), both halves.

    This is the assertion the ruling is actually about. "Both modes at once"
    read naively means every lit card gets everything, which would hand her
    own cards the Guest Cast multiplier -- a numeric buff to her entire
    personal pool that nobody ruled and the C# explicitly gates against.
    """
    st = furina_state(CURTAIN_NEVER_FALLS)
    # Guest Cast's half reaches Companions only.
    assert effects.is_outward_spotlighted(st, companion_card())
    assert not effects.is_outward_spotlighted(st, furina_card())
    assert effects.spotlight_mult(st, companion_card()) == C.SPOTLIGHT_BASE_MULT
    assert effects.spotlight_mult(st, furina_card()) == 1.0
    # Center Stage's half reaches her own cards only.
    assert effects.center_stage_active(st, furina_card())
    assert not effects.center_stage_active(st, companion_card())


def test_her_companions_still_mint_no_fanfare_when_upgraded():
    """The targeting half, asserted through the real play path.

    Guest Cast's "their plays generate no Fanfare" clause has to survive the
    upgrade, and combat.play_card is the only place that clause is enforced.
    Asserted as a pair so a Fanfare gate that had simply become always-true
    fails here rather than looking correct.
    """
    st = furina_state(CURTAIN_NEVER_FALLS)
    st.player.energy = 3
    own = furina_card(effects=[{"op": "block", "amount": 1}])
    st.player.hand.append(own)
    combat.play_card(st, own)
    minted = st.player.fanfare
    assert minted == C.FANFARE_PER_SPOTLIGHT_CARD > 0

    guest = companion_card(effects=[{"op": "block", "amount": 1}])
    st.player.hand.append(guest)
    combat.play_card(st, guest)
    assert st.player.fanfare == minted, (
        "a Companion play minted Fanfare under the upgrade; Guest Cast's "
        "no-Fanfare clause survives R2, which drops the exclusivity and not "
        "the targeting")


def test_selector_payoff_conditions_are_always_on_when_upgraded():
    """R2's third half: the upgrade is the SELECTOR-PAYOFF ENABLER.

    Not a convenience. With the selector card gone there is no designation
    event left to move, so without this every card keying off
    `spotlight_moved_this_turn` (curtain_cue, directors_cut) becomes dead
    text the moment the relic is taken -- the upgrade would silently subtract
    from her pool while appearing to add to it.
    """
    st = furina_state(CURTAIN_NEVER_FALLS)
    assert st.spotlight_moved_this_turn is False, "nothing has moved"
    assert effects._predicate(st, "spotlight_moved_this_turn")

    st_no = furina_state()
    assert not effects._predicate(st_no, "spotlight_moved_this_turn")


def test_the_selector_stops_arriving_when_upgraded():
    """The replacement semantics, and the cost the ruling accepted.

    C# `CurtainNeverFalls` deliberately does NOT override AfterPlayerTurnStart
    the way the base relic does. Funnel Contract §3 is intact -- the
    designation funnel is not removed, moved or renamed, and a drafted
    `spotlight_designate` card still routes through it. An upgraded Furina
    simply never FIRES it again.
    """
    st = furina_state(CURTAIN_NEVER_FALLS)
    effects.player_turn_start_triggers(st)
    assert not any(c.id == "ethereal_spotlight" for c in st.player.hand)
    assert not any(ev["event"] == "selector_granted" for ev in st.log)

    st_no = furina_state()
    effects.player_turn_start_triggers(st_no)
    assert any(c.id == "ethereal_spotlight" for c in st_no.player.hand)


def test_the_designation_funnel_still_works_when_upgraded():
    """Funnel Contract §3, asserted rather than asserted-about.

    "Never fires it again" is a statement about the selector, not about the
    funnel. A drafted designate card must still designate -- the op is not
    removed, it is merely without consequence, and an engine that had ripped
    the funnel out would pass every other test in this section.
    """
    st = furina_state(CURTAIN_NEVER_FALLS)
    st.player.hand.append(companion_card())
    effects.resolve_card(st, furina_card(
        id="selector", effects=[{"op": "spotlight_designate"}]))
    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST
    # ...and designating changed nothing, because both halves were already on.
    assert effects.is_spotlighted(st, furina_card())
    assert effects.center_stage_active(st, furina_card())


def test_the_upgrade_is_inert_without_the_spotlight_economy():
    """Gated on `ethereal_spotlight` for the same reason `combat_start_spark`
    is gated on `spark_on_detonation`: the starter's own hook is the honest
    test for "this player runs the Spotlight economy", and the upgrade keeps
    that hook rather than removing it.
    """
    p = loader.build_player("kokomi")
    p.relic_effects = list(CURTAIN_NEVER_FALLS)
    st = CombatState(player=p, enemies=[make_enemy(hp=50)],
                     rng=random.Random(0))
    assert not relics.spotlight_both_modes(p)
    assert not effects.is_spotlighted(st, companion_card())


def test_both_modes_is_false_on_a_battery_player():
    """The layer boundary, stated as an assertion.

    Battery players carry no relic_effects, so this reader is a dead branch
    there -- which is what keeps the frozen 3.0 battery from feeling any of
    this.
    """
    p = loader.build_player("ref_ironclad")
    assert p.relic_effects == []
    assert not relics.spotlight_both_modes(p)


# ===========================================================================
# The hook vocabulary itself.
# ===========================================================================

def test_the_three_new_hooks_are_combat_scoped_and_never_alarm():
    """A hook in neither vocabulary is a loud UNIMPLEMENTED (house rule).

    All three are rule changes read outside apply_combat_start, so it would
    be easy to add the reader and forget the vocabulary -- and the failure
    mode is noise on every fight, not silence.
    """
    for hook in ("charge_per_exhaust", "burst_per_exhaust",
                 "spotlight_both_modes"):
        assert hook in relics.COMBAT_HOOKS

    st = kokomi_state(PEARL_OF_INSIGHT + CURTAIN_NEVER_FALLS)
    st.turn = 1
    relics.reset_combat(st)
    relics.apply_combat_start(st)
    assert not [ev for ev in st.log if ev["event"] == "UNIMPLEMENTED"]


def test_the_rule_change_hooks_grant_nothing_at_combat_start():
    """They are READS, not writes. A rule change that also fired as an effect
    at combat start would pay twice on turn 1."""
    st = kokomi_state(PEARL_OF_INSIGHT)
    st.turn = 1
    relics.reset_combat(st)
    relics.apply_combat_start(st)
    assert st.player.charge == 0 and st.player.burst_energy == 0
