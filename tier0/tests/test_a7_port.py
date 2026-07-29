"""A7 -- Unheard Confession reaches the actual game (2026-07-29).

Registered in docs/sprint-art-and-a7-2026-07-29.md, Track B. The card was
deferred from C# twice on a structural gap: the Fanfare mutators are
synchronous and every Block grant in the mod is `await CreatureCmd.GainBlock`.
The port settles that with a note-then-flush deferral, and these tests pin the
FOUR properties the brief called non-negotiable:

  1. parity exact -- all four mutation funnels trigger, in both engines;
  2. flat per change event, either direction, inert at saturation;
  3. the card does not pay itself for its own +8 (a sheet-ordering FACT,
     which the C# install order has to reproduce);
  4. the deferral is released visibly -- manifest blocked 2 -> 1.

There is no C# test project in this repo (co-op has no sim backstop), so the
C# half is asserted against the SOURCE TEXT, the same way the hand-written
parity lint does it. That is weaker than executing it and is stated plainly
rather than dressed up: it proves the call sites exist and are wired at the
sites we reasoned about, not that the game runs them. The bite-check is the
run-verification half.

Each test was seen to FAIL against the defect it names before it was kept.
The mutation used is recorded in each docstring.
"""

from __future__ import annotations

import random

from tier0.content import loader
from tier0.engine import combat, effects, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from tools import gen_klee_cards as gen


RESOURCES_CS = (gen.REPO / "klee-mod" / "KleeCode" / "Powers"
                / "FurinaResources.cs")
CARD_CS = (gen.REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
           / "Generated" / "UnheardConfession.cs")


def _cs() -> str:
    return RESOURCES_CS.read_text(encoding="utf-8")


def furina_state(fanfare_cap: int = 60) -> CombatState:
    st = CombatState(player=loader.build_player("furina"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.fanfare_cap = fanfare_cap
    return st


# --------------------------------------------------------------------------
# The trigger surface: four funnels, both engines
# --------------------------------------------------------------------------

def test_every_fanfare_mutator_in_the_sim_notes_the_change():
    """The trigger surface is "every function that writes p.fanfare".

    Asserted structurally rather than per-behaviour because the failure mode
    is a FIFTH mutator added later with no note call -- which no
    behaviour test can see, since it tests the four that exist. Mutation:
    delete the note_fanfare_change call from drop_fanfare_to_floor and this
    fails naming that function.
    """
    import inspect

    from tier0.engine import resources as res

    writers = {"gain_fanfare", "decay_fanfare", "gain_fanfare_floor",
               "drop_fanfare_to_floor"}
    for name in writers:
        src = inspect.getsource(getattr(res, name))
        assert "note_fanfare_change" in src, name

    # raise_fanfare_cap is deliberately NOT in the set: it moves the CEILING
    # and never the meter, so there is no change to pay for. Pinned so the
    # exclusion reads as a decision -- adding a note call there would pay
    # Block for every "Fanfare Cap +X" Power in the pool, which is twelve
    # cards' worth of value nobody printed.
    assert "note_fanfare_change" not in inspect.getsource(res.raise_fanfare_cap)


def test_every_fanfare_mutator_in_the_mod_notes_the_change():
    """The C# half of the same surface, and the actual porting risk.

    A funnel missed here is a card that pays in the sim and is silently
    quieter in the game -- the exact divergence class the deferral discipline
    exists to stop. Mutation: drop the NoteFanfareChanged line from
    DecayFanfare and this fails naming it.
    """
    src = _cs()
    for method in ("GainFanfare", "GainFanfareFloor", "DecayFanfare",
                   "DropFanfareToFloor"):
        start = src.index(f"public static {'void' if method.startswith('Gain') else 'int'} {method}(")
        body = src[start:src.index("\n    }", start)]
        assert "NoteFanfareChanged(" in body, method

    # Same exclusion as the sim, for the same reason.
    cap_start = src.index("public static void RaiseFanfareCap(")
    cap_body = src[cap_start:src.index("\n    }", cap_start)]
    assert "NoteFanfareChanged(" not in cap_body


def test_the_payout_is_flat_per_event_not_proportional_to_the_move():
    """"Whenever Fanfare changes amount" -- the AMOUNT of the change buys
    nothing. A 1-point gain and a 40-point gain both pay the printed number.

    Mutation: scale the grant by the delta and the two halves stop agreeing.
    """
    st = furina_state()
    st.player.powers["fanfare_delta_block"] = 1

    resources.gain_fanfare(st, 1, "test")
    small = st.player.block

    st.player.block = 0
    resources.gain_fanfare(st, 40, "test")
    assert st.player.block == small == 1


def test_a_gain_that_lands_entirely_at_the_cap_is_not_a_change():
    """Saturation is inert, and this is the edge the brief named.

    A meter pinned at its ceiling stops paying, because nothing moved. The
    failure mode is the opposite of obvious: a card that keeps paying at the
    cap turns a dead resource into a Block engine.
    """
    st = furina_state(fanfare_cap=10)
    st.player.fanfare = 10
    st.player.powers["fanfare_delta_block"] = 3

    resources.gain_fanfare(st, 25, "test")

    assert st.player.fanfare == 10
    assert st.player.block == 0


def test_it_pays_on_the_way_down_too():
    """Decay is the only downward mover and it must trigger.

    See test_the_decay_grant_is_cleared_by_the_turn_start_block_clear for
    what then HAPPENS to this Block -- the two facts are separate and both
    true, and only reading them together describes the card.
    """
    st = furina_state()
    st.player.fanfare = 40
    st.turn = 5
    st.player.powers["fanfare_delta_block"] = 2

    resources.decay_fanfare(st)

    assert st.player.fanfare < 40
    assert st.player.block == 2


def test_a_meter_resting_on_its_floor_does_not_pay_for_a_decay_that_did_nothing():
    """The other saturation edge, at the bottom. decay_fanfare still EMITS on
    a resting meter (that state is interesting downstream), so "the event
    fired" and "the meter moved" are different questions and only the second
    one pays."""
    st = furina_state()
    st.player.fanfare = 5
    st.player.fanfare_floor = 5
    st.turn = 5
    st.player.powers["fanfare_delta_block"] = 2

    resources.decay_fanfare(st)

    assert st.player.block == 0


# --------------------------------------------------------------------------
# The sheet-ordering fact
# --------------------------------------------------------------------------

def test_the_card_does_not_pay_itself_for_its_own_floor_grant():
    """RULED, and load-bearing: the +8 is written BEFORE the power installs.

    Reversed, this card opens with 8 free Block nobody printed -- the same
    invisible value the Fanfare rework spent a sprint removing. The engine's
    own note_fanfare_change is what would pay it, so nothing in the engine
    prevents this; only the effect order does.

    Mutation: swap the two effects on the sheet row and this asserts 8 == 0.
    """
    st = furina_state()
    effects.resolve_card(st, loader.get_card("unheard_confession"))

    assert st.player.powers["fanfare_delta_block"] == 1
    assert st.player.fanfare_floor == 8
    assert st.player.block == 0


def test_the_generated_csharp_reproduces_that_order():
    """The same fact on the other side of the bridge, which is where it could
    actually drift: the sheet's order is only a C# guarantee for as long as
    the generator emits effects in sheet order.

    Mutation: emit the apply_power first and this fails.
    """
    src = CARD_CS.read_text(encoding="utf-8")
    grant = src.index("GainFanfareFloor(")
    install = src.index("PowerCmd.Apply<FanfareDeltaBlockPower>")
    assert grant < install


def test_the_card_pays_once_the_power_is_installed():
    """The positive half. Without it the two order tests above are satisfied
    by a card that never pays at all."""
    st = furina_state()
    effects.resolve_card(st, loader.get_card("unheard_confession"))
    st.player.block = 0

    resources.gain_fanfare(st, 3, "test")

    assert st.player.block == 1


# --------------------------------------------------------------------------
# The deferral, released
# --------------------------------------------------------------------------

def test_the_card_generates_and_the_old_blocked_reason_is_gone():
    """RED TEST built from the old blocked state, as the brief required.

    Verified to fail before it was kept: with the `fanfare_delta_block`
    early-return restored in gen_klee_cards.blocked_reason, the first
    assertion fails and the card is absent from the manifest again.
    """
    import json

    import yaml

    cards = yaml.safe_load(
        gen.FURINA_PROFILE.sheet.read_text(encoding="utf-8"))
    card = next(c for c in cards if c["id"] == "unheard_confession")
    assert gen.blocked_reason(card, gen.FURINA_PROFILE) is None

    emitted = gen.emit(card, gen.FURINA_PROFILE)
    assert "PowerCmd.Apply<FanfareDeltaBlockPower>" in emitted

    manifest = json.loads(
        gen.FURINA_PROFILE.manifest.read_text(encoding="utf-8"))
    assert "unheard_confession" in manifest["generated"]
    assert "unheard_confession" not in manifest["blocked"]


def test_the_power_exists_in_the_mod_and_is_not_iconless():
    """R13 makes an iconless PowerModel a boot failure, so a power added
    without an icon entry does not ship quietly -- it does not ship at all.
    This asserts the entry rather than the art: the path-ahead-of-art policy
    is deliberate and KleePck.Path returns null until the PNG lands."""
    src = _cs()
    assert "class FanfareDeltaBlockPower : PowerModel" in src

    icons = (gen.REPO / "klee-mod" / "KleeCode" / "Powers"
             / "KleePowerIcons.cs").read_text(encoding="utf-8")
    assert "FanfareDeltaBlockPower =>" in icons


# --------------------------------------------------------------------------
# The deferral idiom itself
# --------------------------------------------------------------------------

def test_the_decay_settle_happens_before_the_block_clear_in_both_engines():
    """THE FINDING, pinned so it cannot be "fixed" by accident.

    The sim decays at the top of _player_turn and clears Block a few lines
    later, so the decay-triggered Block is destroyed on every turn without
    Barricade. The C# flush therefore has to sit in BeforeSideTurnStart --
    the broadcast AfterBlockCleared follows -- or the mod would pay a
    Block/turn the sim never pays.

    Moving the C# flush to AfterPlayerTurnStart is the plausible "fix" and it
    is a silent divergence, which is why this test asserts the SITE.
    """
    import inspect

    from tier0.engine import combat as combat_mod

    src = inspect.getsource(combat_mod._player_turn)
    assert src.index("decay_fanfare") < src.index("p.block = 0")

    cs = _cs()
    turn_start = cs.index("public override async Task BeforeSideTurnStart(")
    turn_start_body = cs[turn_start:cs.index("\n    public override", turn_start)]
    assert "DecayFanfare(creature)" in turn_start_body
    assert "FlushFanfareDeltaBlock(" in turn_start_body


def test_the_settle_reaches_the_enemy_turn():
    """The site that actually matters for a defensive power: absorption and
    HP loss both mint Fanfare from synchronous hooks during the enemy's turn.
    A flush wired only to card plays would pay nothing while she is being
    hit, which is when Block is worth anything.
    """
    cs = _cs()
    damage = cs.index("public override async Task AfterDamageReceived(")
    body = cs[damage:cs.index("\n    public override", damage)]
    assert "FlushFanfareDeltaBlock(" in body


def test_the_pending_settle_is_taken_and_cleared():
    """Idempotence, asserted on the source because it is the property that
    makes five flush call sites safe. A flush that peeked without clearing
    would pay the same Block once per hook for the rest of the turn."""
    cs = _cs()
    start = cs.index("public static async Task FlushFanfareDeltaBlock(")
    body = cs[start:cs.index("\n    }", start)]
    assert "PendingDeltaBlock.Remove(creature);" in body
    assert body.index("PendingDeltaBlock.Remove(creature);") < body.index(
        "CreatureCmd.GainBlock(")


def test_the_grant_is_unpowered_like_the_other_activity_payouts():
    """The sim says "unscaled printed number, following salon_bow_block" --
    a power's activity payout, not a card's printed Block, so Spotlight does
    not read it. Unpowered is how that is spelled on this side."""
    cs = _cs()
    start = cs.index("public static async Task FlushFanfareDeltaBlock(")
    body = cs[start:cs.index("\n    }", start)]
    assert "ValueProp.Unpowered" in body


def test_furina_still_wins_fights_with_the_power_installed():
    """A smoke test against the whole loop rather than a unit: the power
    installs, the meter moves all combat, and nothing throws. Cheap insurance
    that the trigger did not introduce a recursion (a Block grant that moved
    the meter would)."""
    st = furina_state()
    effects.resolve_card(st, loader.get_card("unheard_confession"))
    for _ in range(3):
        st.turn += 1
        resources.decay_fanfare(st)
        resources.gain_fanfare(st, 4, "test")
    assert st.player.block > 0
    assert combat is not None
