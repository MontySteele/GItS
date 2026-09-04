"""Furina reframe, SLICE 1 -- the five ruled sentences, both sides of the flag.

The design is `review/ruled/furina-reframe-2026-08-29.md` (R220 A; `F`-picks
answered by R224) plus `review/ruled/furina-spotlight-options-2026-08-30.md`
§5 (R228 option 1). The engine is `tier0/engine/furina_reframe.py`, and every
flag in it ships OFF.

THE SHAPE OF THIS FILE, AND WHY IT IS THIS SHAPE. Every behavioural test comes
in a pair: the same board, once with the leg's flag on and once with it off.
The OFF half is not padding -- it is the only assertion that can catch a leg
leaking into the shipped engine, which is the single failure a quarantined
slice can inflict on a game that is being played tonight. `test_every_flag_
ships_off` is first for the same reason, and it is the test that fails if
somebody flips a default instead of a fixture.

WHAT IS NOT TESTED HERE, because it is not built: the `F1` (2) fourth member,
the `F9` cap carriers, the `F11`/`F12` drain cards, the `F16` starter delta,
the `F13`/`F14`/`F15` display work, the named-Companion half of R228's
selector, and the C# leg. The packet's §11 carries each with its reason.

The asymmetry the packet's slate slot 6 flags -- a full-stage deploy Evokes for
free while a dedicated Evoke pays Encore and leaves the stage smaller -- is
MEASURED, not asserted, in `test_furina_reframe_slot6.py`.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, furina_reframe, resources
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

FR = furina_reframe


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _card(**kw):
    d = dict(id="furina_reframe_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


def _companion(**kw):
    """A Companion is `role_c` or the `companion` tag (state.Card.is_companion)."""
    d = dict(id="reframe_test_companion", name="guest", cost=1, type="skill",
             character="furina", role_c="applier")
    d.update(kw)
    return Card(**d)


def _staged(members, encore=9, fanfare=0, seed=0):
    st = furina_state(seed=seed)
    p = st.player
    p.salon = list(members)
    p.powers["salon_member"] = len(p.salon)
    p.encore = encore
    p.fanfare = fanfare
    return st


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


@pytest.fixture
def manual(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_MANUAL", True)


@pytest.fixture
def evoke(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_EVOKE", True)


@pytest.fixture
def meter(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_METER", True)


@pytest.fixture
def one_mode(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_SPOTLIGHT", True)


# ======================================================================
# 0. THE QUARANTINE. Read this section before any other.
# ======================================================================

def test_every_flag_ships_off():
    """The whole slice is dark on a shipped tree, and one test says so."""
    assert FR.FURINA_REFRAME is False
    assert FR.FURINA_REFRAME_MANUAL is False
    assert FR.FURINA_REFRAME_EVOKE is False
    assert FR.FURINA_REFRAME_METER is False
    assert FR.FURINA_REFRAME_SPOTLIGHT is False
    # R251's leg (`EB-365`) joins the roll call rather than taking a quarantine
    # test of its own: the acceptance condition is one sentence about the whole
    # module, and it is asserted in one place.
    assert FR.FURINA_REFRAME_BURST is False


def test_the_master_flag_gates_every_leg(monkeypatch):
    """A leg flag alone does nothing: the master is AND-ed into all five, so
    one flip returns the shipped engine no matter what else is set."""
    for leg in ("FURINA_REFRAME_MANUAL", "FURINA_REFRAME_EVOKE",
                "FURINA_REFRAME_METER", "FURINA_REFRAME_SPOTLIGHT",
                "FURINA_REFRAME_BURST"):
        monkeypatch.setattr(FR, leg, True)
    p = furina_state().player

    assert not FR.manual_active(p)
    assert not FR.evoke_active(p)
    assert not FR.meter_active(p)
    assert not FR.spotlight_active(p)
    assert not FR.burst_retired(p)


def test_the_reframe_is_scoped_to_furina(monkeypatch):
    """One character's redesign. A roster-wide branch would be a different and
    much larger change than the one that was countersigned."""
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_MANUAL", True)

    assert FR.manual_active(loader.build_player("furina"))
    assert not FR.manual_active(loader.build_player("klee"))
    assert not FR.manual_active(loader.build_player("kokomi"))


# ======================================================================
# 1. MANUAL -- members do not auto-play (the single biggest change)
# ======================================================================

def test_the_turn_start_upkeep_runs_with_the_flag_off():
    st = _staged(["crabaletta"], encore=9)
    enemy_hp = st.enemies[0].hp

    effects.player_turn_start_triggers(st)

    assert len(_events(st, "salon_tick")) == 1
    assert st.enemies[0].hp < enemy_hp
    assert _events(st, "salon_upkeep_suppressed") == []


def test_manual_suppresses_the_turn_start_upkeep(manual):
    """There is no end-of-turn Salon path, so suppressing this one call
    removes the automatic engine entirely (§2.2)."""
    st = _staged(["crabaletta", "usher"], encore=9)
    enemy_hp = st.enemies[0].hp

    effects.player_turn_start_triggers(st)

    assert _events(st, "salon_tick") == []
    assert st.enemies[0].hp == enemy_hp
    assert st.player.encore == 9                 # no upkeep to pay
    assert st.player.block == 0                  # the usher did not act


def test_the_suppression_is_loud_rather_than_silent(manual):
    """An instrument that counted upkeeps has to be able to tell an empty
    stage from a stage whose upkeep no longer exists (D4, and R177's fuel
    finding was measured on the row this replaces)."""
    st = _staged(["crabaletta"], encore=9)

    effects.player_turn_start_triggers(st)

    assert len(_events(st, "salon_upkeep_suppressed")) == 1
    assert _events(st, "salon_upkeep_suppressed")[0]["members"] == 1


def test_an_empty_stage_says_nothing_at_turn_start(manual):
    st = _staged([], encore=9)

    effects.player_turn_start_triggers(st)

    assert _events(st, "salon_upkeep_suppressed") == []


# ======================================================================
# 2. The Companion trigger -- §4.3, F3 (1) and F4 (1)
# ======================================================================

def test_a_companion_play_does_not_touch_the_stage_with_the_flag_off():
    st = _staged(["usher", "crabaletta"], encore=9)

    combat._finish_play(st, _companion())

    assert st.player.salon == ["usher", "crabaletta"]
    assert st.player.block == 0
    assert _events(st, "salon_trigger") == []


def test_a_companion_play_performs_the_front_member_then_rotates(manual):
    st = _staged(["usher", "crabaletta"], encore=9)
    printed = C.SALON_MEMBERS["usher"]["tick"]["block"]

    combat._finish_play(st, _companion())

    assert st.player.block == printed            # the usher performed
    assert st.player.salon == ["crabaletta", "usher"]      # then rotated
    assert st.player.encore == 9 - C.SALON_TICK_ENCORE_COST
    assert len(_events(st, "salon_trigger")) == 1


def test_the_trigger_walks_the_company_over_several_companion_plays(manual):
    """`F4` (1): once per Companion CARD played, unbounded per turn -- the
    bound is your hand. Three plays walk a three-member stage exactly once
    round, which is the whole reason the trigger rotates."""
    st = _staged(["usher", "crabaletta", "chevalmarin"], encore=9)

    for _ in range(3):
        combat._finish_play(st, _companion())

    assert st.player.salon == ["usher", "crabaletta", "chevalmarin"]
    assert [ev["member"] for ev in _events(st, "salon_trigger")] == [
        "usher", "crabaletta", "chevalmarin"]


def test_a_companion_play_with_an_empty_salon_does_nothing_extra(manual):
    """RULED (§1.1a item 2), and visible under D4 -- with its OWN event name,
    because a display must be able to tell "your Companion found an empty
    stage" from a card the player chose to play into one."""
    st = _staged([], encore=9)

    combat._finish_play(st, _companion())

    assert st.player.encore == 9
    assert st.player.block == 0
    assert len(_events(st, "salon_trigger_whiffed")) == 1
    assert _events(st, "salon_perform_whiffed") == []


def test_a_non_companion_play_never_triggers_the_stage(manual):
    """The trigger is the Companion half of the kit. Furina's own cards Evoke;
    they do not also trigger for free."""
    st = _staged(["usher"], encore=9)

    combat._finish_play(st, _card(id="not_a_companion"))

    assert st.player.block == 0
    assert st.player.salon == ["usher"]
    assert _events(st, "salon_trigger") == []


def test_a_doubled_companion_performs_once_and_says_so(manual):
    """`EB-420`. Duet plays the next Companion card an extra time; the trigger
    is gated on `replay_index == 0`, so the extra play performs nobody -- and
    that gate is LAW:145's per-Companion-play bound rather than an accident of
    the call site ("a per-play bound a replay can double is not a bound",
    `KleeCompanionSpark`).

    THE RULE WAS ALREADY THIS AND LEFT NO TRACE. The round-5 seat played Duet
    into Freminet, counted three Companion plays' worth of triggers, got two,
    and found no line on any screen naming the second play. So the replay is
    emitted under its own name, the way the whiff is."""
    st = _staged(["usher", "crabaletta"], encore=9)
    st.replay_next_companion = 1

    combat._finish_play(st, _companion())

    # One play, two resolutions, ONE performance -- and the stage turned once.
    assert len(_events(st, "salon_trigger")) == 1
    assert st.player.salon == ["crabaletta", "usher"]
    # ...and the resolution that performed nobody has a line of its own.
    assert len(_events(st, "salon_replay_no_trigger")) == 1


def test_a_doubled_non_companion_says_nothing(manual):
    """The event is the Companion half of the kit, exactly as the trigger is:
    a replayed card of hers was never going to perform anybody."""
    st = _staged(["usher"], encore=9)
    st.replay_next_companion = 1

    combat._finish_play(st, _card(id="not_a_companion"))

    assert _events(st, "salon_replay_no_trigger") == []


def test_a_doubled_companion_says_nothing_with_the_flag_off():
    """The OFF half: with no reframe there is no Companion trigger to miss, so
    there is nothing for the line to be about."""
    st = _staged(["usher"], encore=9)
    st.replay_next_companion = 1

    combat._finish_play(st, _companion())

    assert _events(st, "salon_replay_no_trigger") == []


def test_the_trigger_performs_through_the_one_shared_act(manual):
    """The same hard requirement EB-118 pinned for the card verbs: no second
    Salon-resolution implementation. If the hook grew its own copy of the act,
    the stub below would not be reached from it."""
    seen = []
    original = effects.salon_member_act

    def spy(state, member):
        seen.append(member)
        return original(state, member)

    st = _staged(["usher"], encore=9)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(effects, "salon_member_act", spy)
        combat._finish_play(st, _companion())

    assert seen == ["usher"]


# ======================================================================
# 3. Deploy tempo -- §4.2, both halves RULED
# ======================================================================

def _deploy(member="usher", amount=1):
    return _card(effects=[{"op": "apply_power", "power": "salon_member",
                           "amount": amount, "member": member}])


def test_a_deploy_does_not_perform_with_the_flag_off():
    st = _staged([], encore=9)

    effects.resolve_card(st, _deploy("usher"))

    assert st.player.salon == ["usher"]
    assert st.player.block == 0                  # no performance
    assert _events(st, "salon_tick") == []


def test_a_deploy_performs_the_member_it_deploys(manual):
    """§4.2: the card pays on the turn it is played. The member that performs
    is the one that ENTERED -- the card's promise is about the member it
    names, not about whoever happens to be at the front."""
    st = _staged(["crabaletta"], encore=9)
    printed = C.SALON_MEMBERS["usher"]["tick"]["block"]
    enemy_hp = st.enemies[0].hp

    effects.resolve_card(st, _deploy("usher"))

    assert st.player.salon == ["crabaletta", "usher"]
    assert st.player.block == printed
    assert st.enemies[0].hp == enemy_hp          # crabaletta did NOT act
    assert [ev["member"] for ev in _events(st, "salon_tick")] == ["usher"]


def test_a_deploy_onto_a_full_stage_evokes_the_front_member(manual):
    """[USER]'s "overcrowding the stage still forces out an Evoke" -- which
    §2.2 shows is the SHIPPED displacement bow under a new name. What the flag
    adds is that the bow is an Evoke."""
    st = _staged(["usher", "crabaletta", "chevalmarin"], encore=9)
    bow_block = C.SALON_MEMBERS["usher"]["bow"]["block"]

    effects.resolve_card(st, _deploy("crabaletta"))

    assert st.player.salon == ["crabaletta", "chevalmarin", "crabaletta"]
    assert len(_events(st, "salon_final_bow")) == 1
    assert len(_events(st, "salon_evoke")) == 1
    assert st.player.block >= bow_block          # the usher's bow, then the
                                                 # replacement's performance


def test_the_displacement_bow_is_not_an_evoke_with_the_flag_off():
    st = _staged(["usher", "crabaletta", "chevalmarin"], encore=9)

    effects.resolve_card(st, _deploy("crabaletta"))

    assert len(_events(st, "salon_final_bow")) == 1
    assert _events(st, "salon_evoke") == []


def test_the_full_stage_deploy_evokes_the_front_and_cannot_be_aimed(
        manual, evoke, monkeypatch):
    """THE LOCK on the other half of the slot-6 ruling. Overflow deployment
    keeps evoking the FRONT automatically -- that is the reward for filling
    the stage, and the aim is what Encore buys on the dedicated card instead.

    Two assertions, because one of them alone could pass by luck. First: the
    deploy's own `member:` names who ENTERS, and the member who LEAVES is the
    front regardless of it -- here the card names the very member sitting at
    the back, and the usher still takes the bow. Second, and structurally:
    the chooser is booby-trapped for the length of this deploy, so a future
    edit that routed the overflow bow through it fails HERE rather than
    quietly erasing the asymmetry the ruling created on purpose.
    """
    st = _staged(["usher", "crabaletta", "chevalmarin"], encore=9)

    def _never(*a, **kw):
        raise AssertionError("the overflow Evoke must not consult the aim")

    monkeypatch.setattr(FR, "evoke_target_index", _never)

    effects.resolve_card(st, _deploy("chevalmarin"))

    assert _events(st, "salon_final_bow")[0]["member"] == "usher"
    assert _events(st, "salon_evoke")[0]["member"] == "usher"
    assert st.player.salon == ["crabaletta", "chevalmarin", "chevalmarin"]


# ======================================================================
# 4. EVOKE -- §4.4, F5 (player's choice, front by default), F6 (1), F7 (1)
# ======================================================================

def _evoke_card(encore_cost=0, member=None):
    """`member=None` prints no aim, which under the slot-6 ruling IS the front
    member -- so every test written before the ruling still means what it
    meant. `member="..."` is the aimed Evoke the ruling added."""
    fx = {"op": "salon_bow"}
    if member is not None:
        fx["member"] = member
    return _card(id="reframe_test_evoke", encore_cost=encore_cost,
                 effects=[fx])


def test_the_bow_is_the_shipped_bow_with_the_flag_off():
    """`F6`'s multiplier is the only thing the flag adds to the verb, so with
    it off the number is the printed base plus ONE Focus term."""
    st = _staged(["usher"], encore=9, fanfare=3 * C.SALON_FOCUS_PER)
    printed = C.SALON_MEMBERS["usher"]["bow"]["block"]

    effects.resolve_card(st, _evoke_card())

    assert st.player.block == printed + 3
    assert _events(st, "salon_evoke") == []


def test_an_evoke_applies_the_focus_term_n_times(evoke):
    """`F6` (1): a multiplier on the SAME Focus term -- one divisor, one
    number on screen, "x N" on the face. It lands on the Focus term alone and
    never on the printed base."""
    st = _staged(["usher"], encore=9, fanfare=3 * C.SALON_FOCUS_PER)
    printed = C.SALON_MEMBERS["usher"]["bow"]["block"]

    effects.resolve_card(st, _evoke_card())

    assert st.player.block == printed + 3 * FR.EVOKE_FOCUS_MULT
    assert _events(st, "salon_evoke")[0]["focus_mult"] == FR.EVOKE_FOCUS_MULT


def test_an_unaimed_evoke_expends_the_front_member(evoke):
    """`F5` as the slot-6 ruling revised it: the card may aim, and the FRONT is
    what it takes when it names nobody. This is the same end of the same queue
    the trigger performs, the shipped bow takes and a full-stage deploy
    displaces -- so the default keeps "one order, one lesson" for every card
    that does not pay to break it."""
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _evoke_card())

    assert st.player.salon == ["crabaletta"]
    assert st.player.powers["salon_member"] == 1


def test_the_front_sentinel_is_the_same_thing_written_out(evoke):
    """`member: front` and no `member:` at all are one rule, not two: the
    sentinel exists so a row can say what it means instead of relying on a
    reader knowing what an absent key implies."""
    for aim in (None, FR.EVOKE_TARGET_FRONT):
        st = _staged(["usher", "crabaletta"], encore=9)

        effects.resolve_card(st, _evoke_card(member=aim))

        assert st.player.salon == ["crabaletta"], aim


def test_an_aimed_evoke_takes_the_member_the_card_names(evoke):
    """THE RULING: a dedicated Evoke chooses which member it removes. Each of
    the three is named in turn off the same board, so what is pinned is the
    aim itself and not one member's luck of the queue order."""
    stage = ["usher", "crabaletta", "chevalmarin"]
    for aimed in stage:
        st = _staged(stage, encore=9)

        effects.resolve_card(st, _evoke_card(member=aimed))

        assert aimed not in st.player.salon, aimed
        assert st.player.salon == [m for m in stage if m != aimed], aimed
        assert st.player.powers["salon_member"] == 2, aimed
        assert _events(st, "salon_final_bow")[0]["member"] == aimed, aimed
        assert _events(st, "salon_evoke")[0]["member"] == aimed, aimed


def test_the_aim_is_ignored_with_the_evoke_leg_off():
    """The byte-identical guard, in this file's standing shape. A row carrying
    an aim on a release build is the shipped bow: front member, one Focus
    term, no `salon_evoke` event. The choice is a thing the leg GIVES."""
    stage = ["usher", "crabaletta", "chevalmarin"]
    st = _staged(stage, encore=9, fanfare=3 * C.SALON_FOCUS_PER)
    printed = C.SALON_MEMBERS["usher"]["bow"]["block"]

    effects.resolve_card(st, _evoke_card(member="chevalmarin"))

    assert st.player.salon == ["crabaletta", "chevalmarin"]
    assert st.player.block == printed + 3
    assert _events(st, "salon_evoke") == []


def test_an_aim_at_an_absent_member_takes_the_front_and_says_so(evoke):
    """An aimed card that cannot find its member is an UNAIMED Evoke, never a
    wasted one -- and under D4 the miss is emitted, because the aim leaves no
    trace in the state afterwards for a display to read."""
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _evoke_card(member="chevalmarin"))

    assert st.player.salon == ["crabaletta"]
    assert [ev["member"] for ev in _events(st, "salon_evoke_target_absent")
            ] == ["chevalmarin"]


def test_the_absent_aim_is_not_emitted_when_the_member_is_there(evoke):
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _evoke_card(member="crabaletta"))

    assert _events(st, "salon_evoke_target_absent") == []


def test_an_unknown_member_name_is_refused(evoke):
    """The deploy verb raises on an unknown member and so does this one: a
    typo that quietly degraded into "the front member" is the one failure an
    aimed Evoke could hide for a whole sprint."""
    st = _staged(["usher"], encore=9)

    with pytest.raises(ValueError):
        effects.resolve_card(st, _evoke_card(member="paimon"))


def test_a_repeated_aimed_evoke_takes_the_named_member_then_the_front(evoke):
    """`amount: 2` with an aim resolves the aim FIRST and then behaves like an
    unaimed Evoke, because there is only one of each member on a stage. Pinned
    so the second bow's target is a stated rule rather than an accident of the
    loop."""
    st = _staged(["usher", "crabaletta", "chevalmarin"], encore=9)
    card = _card(id="reframe_test_evoke_x2",
                 effects=[{"op": "salon_bow", "amount": 2,
                           "member": "chevalmarin"}])

    effects.resolve_card(st, card)

    assert st.player.salon == ["crabaletta"]
    assert [ev["member"] for ev in _events(st, "salon_evoke")] == [
        "chevalmarin", "usher"]


def test_an_empty_meter_makes_the_multiplier_worth_nothing(evoke):
    """The multiplier multiplies the Focus term, and the Focus term is zero
    below `SALON_FOCUS_PER` held. An Evoke on a cold meter is the printed
    number -- which is what makes the meter worth holding."""
    st = _staged(["usher"], encore=9, fanfare=0)

    effects.resolve_card(st, _evoke_card())

    assert st.player.block == C.SALON_MEMBERS["usher"]["bow"]["block"]


def test_the_focus_term_never_reaches_the_encore_refund_or_the_aura(evoke):
    """§3.1 amendment 4, countersigned PROSPECTIVE by R224: the Focus term
    scales performance numerics ONLY -- damage and Block -- and never Energy,
    Encore, Charge, Fanfare itself, card generation or aura stacks.

    Chevalmarin is the one live row the invariant touches, and this is the
    test that would fail if the multiplier were ever plumbed into `_salon_bow`
    generally instead of into `_salon_amount`. Her Evoke refunds exactly its
    printed Encore at any meter and at any multiplier.
    """
    printed = C.SALON_MEMBERS["chevalmarin"]["bow"]["encore"]
    for fanfare in (0, 3 * C.SALON_FOCUS_PER):
        st = _staged(["chevalmarin"], encore=9, fanfare=fanfare)
        before = st.player.encore

        effects.resolve_card(st, _evoke_card())

        assert st.player.encore - before == printed


def test_an_evoke_card_is_unplayable_below_its_printed_encore_price(evoke):
    """`F7` (1): the price is the card's shipped `encore_cost` -- a
    playability GATE and then a spend, both before the op resolves, so an
    Evoke that cannot be paid for is never half-resolved."""
    st = _staged(["usher"], encore=1)

    assert not combat.card_playable(st, _evoke_card(encore_cost=2))
    assert combat.card_playable(st, _evoke_card(encore_cost=1))


def test_playing_an_evoke_card_spends_the_encore_price(evoke):
    st = _staged(["usher"], encore=5)
    card = _evoke_card(encore_cost=2)
    st.player.hand.append(card)

    combat.play_card(st, card)          # calls `_finish_play` itself

    assert st.player.encore == 3
    assert st.player.salon == []


# ======================================================================
# 5. METER -- §4.1, performance mints and nothing else does
# ======================================================================

def test_a_performance_mints_the_trigger_amount(meter, manual):
    st = _staged(["usher"], encore=9, fanfare=0)

    combat._finish_play(st, _companion())

    assert st.player.fanfare == FR.FANFARE_PER_TRIGGER
    assert [ev["source"] for ev in _events(st, "gain_fanfare")] == [
        "salon_performance"]


def test_an_evoke_mints_the_larger_amount(meter, evoke):
    """The ordering is the ruled half of the pair: trigger < Evoke, because an
    Evoke costs a member."""
    st = _staged(["usher"], encore=9, fanfare=0)

    effects.resolve_card(st, _evoke_card())

    assert st.player.fanfare == FR.FANFARE_PER_EVOKE
    assert FR.FANFARE_PER_EVOKE > FR.FANFARE_PER_TRIGGER


def test_the_mint_is_bounded_per_companion_play(meter, manual):
    """LAW:145 (countersigned R224) permits a character engine to answer a
    Companion play and mint its resource only where the kit "bounds the amount
    generated per Companion play". One play, one performance, one bounded
    mint -- Klee's `KLEE_COMPANION_SPARK_MAX_PER_PLAY` is the same
    declaration."""
    st = _staged(["usher", "crabaletta"], encore=9, fanfare=0)

    combat._finish_play(st, _companion())

    assert st.player.fanfare <= FR.FANFARE_PER_COMPANION_TRIGGER_MAX


@pytest.mark.parametrize("leg", ["hp_lost", "encore_spent",
                                 "encore_absorbed"])
def test_the_shipped_generation_legs_mint_nothing(meter, leg):
    """§4.1 retires all four legs, and with them the invariant "every point of
    damage past Block prints exactly 1 Fanfare"."""
    st = _staged(["usher"], encore=9, fanfare=0)

    if leg == "hp_lost":
        resources.note_player_hp_loss(st, 7)
    elif leg == "encore_spent":
        resources.spend_encore(st, 3, "test")
    else:
        resources.absorb_into_encore(st, 4, "test")

    assert st.player.fanfare == 0


@pytest.mark.parametrize("leg", ["hp_lost", "encore_spent",
                                 "encore_absorbed"])
def test_the_shipped_generation_legs_still_mint_with_the_flag_off(leg):
    st = _staged(["usher"], encore=9, fanfare=0)

    if leg == "hp_lost":
        resources.note_player_hp_loss(st, 7)
    elif leg == "encore_spent":
        resources.spend_encore(st, 3, "test")
    else:
        resources.absorb_into_encore(st, 4, "test")

    assert st.player.fanfare > 0


def test_the_meter_still_decays(meter, manual):
    """KEPT by §3, and it is the load-bearing half of the whole design: a
    number that only rises is what D2 calls not-a-decision, and the brake is
    what makes holding the meter a demand on the stage."""
    st = _staged(["usher"], encore=9, fanfare=30)
    st.turn = 4

    resources.decay_fanfare(st)

    assert st.player.fanfare == 30 - round(30 * C.FANFARE_DECAY_FRACTION)


# ======================================================================
# 6. SPOTLIGHT -- R228 option (1), ONE MODE, PRICED
# ======================================================================

def _designate():
    return _card(effects=[{"op": "spotlight_designate"}])


def test_the_shipped_selector_still_runs_a_heuristic_with_the_flag_off():
    st = _staged([], encore=9)

    effects.resolve_card(st, _designate())

    assert st.player.spotlight is not None
    assert st.player.encore == 9                 # the shipped selector is free


def test_the_selector_aims_guest_cast_and_pays_encore(one_mode):
    st = _staged([], encore=9)

    effects.resolve_card(st, _designate())

    assert st.player.spotlight == C.SPOTLIGHT_GUEST_CAST
    assert st.player.encore == 9 - FR.SPOTLIGHT_DESIGNATE_ENCORE_COST
    assert _events(st, "spotlight_designated")[0]["mode"] == "guest_cast"


def test_an_unaffordable_designation_is_a_no_op_and_not_a_discount(one_mode):
    """"Free when under-priced" is the failure R228 names in its own biggest
    risk. An unpaid aim leaves the Spotlight where it was and says so."""
    st = _staged([], encore=1)

    effects.resolve_card(st, _designate())

    assert st.player.spotlight is None
    assert st.player.encore == 1
    assert len(_events(st, "spotlight_designate_unpaid")) == 1


def test_re_aiming_at_the_same_target_bills_nothing(one_mode):
    st = _staged([], encore=9)
    st.player.spotlight = C.SPOTLIGHT_GUEST_CAST

    effects.resolve_card(st, _designate())

    assert st.player.encore == 9
    assert len(_events(st, "spotlight_designate_redundant")) == 1


def test_center_stage_retires_under_the_one_mode_flag(one_mode):
    st = _staged([], encore=9)
    st.player.spotlight = st.player.character_id

    assert not effects.center_stage_active(st, _card())


def test_guest_cast_still_multiplies_a_companion_by_the_shipped_number(
        one_mode):
    """KEPT by R228: Guest Cast and `SPOTLIGHT_BASE_MULT = 1.5` are exactly
    what they ship. The pick moved what the selector IS, not what it pays."""
    st = _staged([], encore=9)
    st.player.spotlight = C.SPOTLIGHT_GUEST_CAST

    assert effects.spotlight_mult(st, _companion()) == C.SPOTLIGHT_BASE_MULT
    assert effects.spotlight_mult(st, _card()) == 1.0
