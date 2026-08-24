"""EB-118 Phase 2B: Big Badda Boom, the first DRAFTABLE Ethereal carrier.

`test_ethereal_base_field.py` proves the machinery on synthetic probes -- the
field, the shared predicate, the end-of-turn sweep, the remove-on-upgrade
delta. Everything there is true of a card nobody can be dealt. This file is
the other half: the ruled card, on the shipping sheet, through both engines.

THE BODY IS THE ONE [USER] RULED ON 2026-08-24 (option A of a reviewed slate),
which replaced the direction this file first pinned. The old body was 16@2 plus
Ethereal and an upgrade that only refunded the tax -- a pure price with nothing
to decide on either face. The ruled body keeps the price and gives the card
something to be about: `If it kills, deal 8 to a random OTHER enemy.` The
upgrade is unchanged (`remove: ethereal`, numbers unmoved), so the base-to-
upgraded delta is STILL exactly the keyword and R193's armed repricing trigger
still reads a one-variable card.

Four legs, because a keyword that only half-crosses the wall is the exact
divergence the codegen whitelist exists to stop (a card that vanishes in the
sim and lingers in the game is a different card):

  1. tier0 runtime -- the shipped row burns unplayed, the upgraded row does
     not, in a real fight loop rather than a direct call to the flush.
  1b. the RIDER at runtime -- kill / no-kill / no-survivor, on the real row.
  2. codegen -- the generator emits `CardKeyword.Ethereal` on the base and
     `RemoveKeyword(CardKeyword.Ethereal)` on the upgrade, emits the rider,
     and emits no number bump beside any of it.
  3. the SHIPPED artifact -- the committed generated file says the same. CI's
     `gen_roster_cards.py --check` proves the file matches the generator;
     this proves the generator was pointed at the right card.

The drafter leg is not here: it is a tier-0.5 price and lives in
`tier05/tests/test_ethereal_draft_valuation.py`, where the 0.6 share R193
ratified provisionally is exercised by this same card -- and where the rider's
static UNDER-CREDIT is pinned as the honest number it is.
"""

from __future__ import annotations

from pathlib import Path

from tier0.content import loader
from tier0.engine import combat
from tier0.tests.conftest import make_enemy, make_state
from tools import gen_klee_cards as gen

CARD = "big_badda_boom"
GENERATED = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
             / "Cards" / "Generated" / "BigBaddaBoom.cs")

SPLASH = 8


def _sheet_row() -> dict:
    row = next((c for c in gen._sheet_cards(gen.KLEE_PROFILE.sheet)
                if c["id"] == CARD), None)
    assert row is not None, f"{CARD} left docs/klee-cards.yaml"
    return row


def _unplayed_turn(card_id: str):
    """One fight, nothing playable, nothing to draw: the only thing that can
    move the card is the end-of-turn flush. Klee's own build_player, because
    the point is that the keyword works for the character who ships it."""
    p = loader.build_player("klee")
    p.draw_pile = []
    p.discard_pile = []
    p.hand = [loader.get_card(card_id)]
    p.energy = 0                      # the card costs 2; it cannot be played
    return combat.run_fight(
        p, [make_enemy(hp=1, intents=[{"kind": "block", "amount": 0}])],
        lambda s: None, seed=0)


def _play(*hps, card_id: str = CARD, seed: int = 0):
    """Play the real sheet row into a board of the given HP totals.

    tier0's single-target aim is the LOWEST-HP living enemy (`_pick_targets`),
    so the first argument is always the body the printed 16 lands on -- which
    is what lets a kill and a non-kill be written as one number.
    """
    st = make_state(
        enemies=[make_enemy(hp=h, name=f"e{i}") for i, h in enumerate(hps)],
        seed=seed)
    card = loader.get_card(card_id)
    st.player.energy = 5
    st.player.hand.append(card)
    combat.play_card(st, card)
    return st


# --- 1. tier0 runtime ------------------------------------------------------

def test_the_base_card_burns_in_hand():
    st = _unplayed_turn(CARD)
    assert any(c.id == CARD for c in st.player.exhaust_pile)
    assert not any(c.id == CARD for c in st.player.discard_pile)


def test_the_upgraded_card_does_not():
    """The red half, and the whole value of the upgrade: same card, same
    fight, upgraded -- it flushes to discard and comes back around."""
    st = _unplayed_turn(CARD + "+")
    assert not any(c.id.startswith(CARD) for c in st.player.exhaust_pile)
    assert any(c.id == CARD + "+" for c in st.player.discard_pile)


def test_the_ruled_body_is_what_both_faces_print():
    """[USER] 2026-08-24, option A. The BODY is 16 plus a kill rider; the
    UPGRADE is still the keyword removal and nothing else, so the base-to-
    upgraded delta stays exactly Ethereal. A number bump reintroduced beside
    the keyword -- or a rider that ships on only one face -- would make R193's
    armed repricing trigger read a card it was not armed on."""
    base = loader.get_card(CARD)
    up = loader.get_card(CARD + "+")
    assert base.effects == up.effects == [
        {"op": "damage", "amount": 16, "target": "enemy"},
        {"op": "conditional", "if": "killed_target",
         "then": [{"op": "damage", "amount": SPLASH,
                   "target": "random_enemy"}]},
    ]
    assert base.cost == up.cost == 2


# --- 1b. the ruled rider, at runtime ---------------------------------------

def test_a_kill_splashes_onto_a_survivor():
    st = _play(12, 60)
    dead, survivor = st.enemies
    assert not dead.alive
    assert survivor.hp == 60 - SPLASH


def test_a_non_kill_does_not_splash_at_all():
    """The rider is gated on the kill, not on the swing. 40 HP survives the
    16, so the second body must be untouched."""
    st = _play(40, 60)
    hit, other = st.enemies
    assert hit.alive and hit.hp == 40 - 16
    assert other.hp == 60


def test_the_splash_can_never_land_on_the_corpse():
    """The RULED word is "other", and the engine is what enforces it: the
    branch resolves after the kill, and `_pick_targets` rolls only over
    `state.living_enemies`, so the body that just died is not in the bag.

    Swept over seeds rather than asserted once, because the pick is random --
    a single seed would prove only that one roll missed the corpse. Every
    seed must put the full splash on a LIVING enemy and leave the corpse at
    exactly the HP the killing 16 left it at.
    """
    for seed in range(25):
        st = _play(12, 60, 60, 60, seed=seed)
        corpse, *survivors = st.enemies
        assert not corpse.alive
        assert corpse.hp == 12 - 16          # nothing hit it a second time
        splashed = [e for e in survivors if e.hp != 60]
        assert len(splashed) == 1, f"seed {seed}: {[e.hp for e in survivors]}"
        assert splashed[0].hp == 60 - SPLASH


def test_the_last_enemy_leaves_the_splash_nowhere_to_go():
    """PINNED, not ruled: with the killed body the only body, the rider
    resolves into NOTHING -- `_pick_targets` returns an empty list and the
    damage op has nobody to deal to. No error, no self-hit, no re-hit of the
    corpse.

    THE MOD SIDE IS ASSUMED, NOT PINNED HERE, and deliberately so: its splash
    delegates to `.TargetingRandomOpponents`, which no headless test can reach
    (EB-105's boundary -- there is no live CombatState). It is the same
    unguarded call TWELVE shipped cards already make, three of which
    (da_da_da, rapid_fire, jumpy_dumpty) hit the empty pool whenever an early
    hit kills the last body, so this card adds no exposure the roster does not
    already carry. The undocumented part -- why the delegated path is safe
    when the hand-rolled `Rng.NextItem` paths all guard -- is an engineering
    finding, not something this test can settle."""
    st = _play(12)
    only, = st.enemies
    assert not only.alive
    assert only.hp == 12 - 16
    assert st.over


def test_the_rider_fires_on_the_upgraded_face_too():
    """The upgrade buys off Ethereal and touches nothing else, so the
    upgraded card must splash identically."""
    st = _play(12, 60, card_id=CARD + "+")
    assert st.enemies[1].hp == 60 - SPLASH


# --- 2. codegen ------------------------------------------------------------

def test_the_generator_emits_the_keyword_and_its_removal():
    cs = gen.emit(_sheet_row(), gen.KLEE_PROFILE)
    assert "CardKeyword.Ethereal" in cs
    assert "RemoveKeyword(CardKeyword.Ethereal);" in cs
    # The keyword renders through the game's auto-keyword pipeline (the A9
    # rail), so the description must NOT also say the word.
    assert "Ethereal." not in cs
    # And the upgrade is the keyword removal ALONE.
    assert "UpgradeValueBy" not in cs


def test_the_generator_emits_the_ruled_rider():
    """The C# half of the ruled body. The guard is the same `enemiesAtStart`
    snapshot sparkly_explosion ships for the same predicate, and the splash
    aims through the game's own random-opponent helper -- whose population is
    `HittableEnemies`, the live accessor. That is what makes "other" true in
    the mod for the same reason it is true in the sim."""
    cs = gen.emit(_sheet_row(), gen.KLEE_PROFILE)
    assert "var enemiesAtStart = CombatState!.HittableEnemies.ToList();" in cs
    assert "if (enemiesAtStart.Any(e => e.IsDead))" in cs
    assert f"DamageCmd.Attack({SPLASH}m)" in cs
    assert ".TargetingRandomOpponents(CombatState!)" in cs


def test_the_card_text_reads_the_ruled_sentence():
    """"OTHER" IS PRINTED, and it is derived rather than hand-written: the
    branch's own predicate is a kill, so the corpse is out of the bag the pick
    rolls over and the face is entitled to the stronger word
    (`gen.KILL_PREDICATES`). Outside a kill branch the same op still prints
    the plain "a random enemy", which is why this pin names the whole
    sentence rather than the adjective."""
    cs = gen.emit(_sheet_row(), gen.KLEE_PROFILE)
    assert ('("description", "Deal {Damage:diff()} damage. If it kills: '
            'deal 8 damage to a random other enemy."),') in cs


def test_the_other_is_derived_from_the_predicate_not_pinned_to_the_card():
    """The red half of the wording rule. `gen._branch_text` prints the stronger
    word ONLY where it is true -- the THEN arm of a kill predicate, where the
    hit body is already out of the pool. The identical damage op in a branch
    gated on anything else, or in the ELSE arm of the kill branch (nothing
    died), must keep the plain word. Without this, "other" is one careless
    edit away from becoming the global phrasing and lying on every
    random-target card Klee ships."""
    row = _sheet_row()
    branch = row["effects"][1]["then"]

    after_kill = gen._branch_text(row, branch, in_then=True,
                                  predicate="killed_target")
    assert after_kill == "deal 8 damage to a random other enemy."

    for kwargs in ({"in_then": True, "predicate": "has_spark"},
                   {"in_then": False, "predicate": "killed_target"},
                   {"in_then": True, "predicate": ""}):
        txt = gen._branch_text(row, branch, **kwargs)
        assert txt == "deal 8 damage to a random enemy.", kwargs


def test_the_card_is_not_blocked():
    """`ethereal` is on the codegen field whitelist. Without that entry the
    first card ruled Ethereal from print blocks with "card field(s)
    ['ethereal'] not understood" -- which is the whitelist working, but it
    would mean this card ships in the sim and not in the mod."""
    assert gen.blocked_reason(_sheet_row(), gen.KLEE_PROFILE) is None


# --- 3. the shipped artifact ----------------------------------------------

def test_the_committed_generated_card_carries_it():
    cs = GENERATED.read_text(encoding="utf-8")
    assert "CardKeyword.Ethereal" in cs
    assert "RemoveKeyword(CardKeyword.Ethereal);" in cs
    assert "UpgradeValueBy" not in cs
    # The ruled rider reached the SHIPPED file, not just the generator.
    assert "if (enemiesAtStart.Any(e => e.IsDead))" in cs
    assert f"DamageCmd.Attack({SPLASH}m)" in cs
    assert ".TargetingRandomOpponents(CombatState!)" in cs
    assert "to a random other enemy." in cs
