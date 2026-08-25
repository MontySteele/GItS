"""EB-118 Phase 1 -- the acceptance pins for the cleanup batch.

Phase 1 is the coordinated card-body/C#-parity batch that HOLDS card ids,
rarities, roles and archetypes (packet §3). What it moves is bodies, and
several of its results are stated as facts about a POOL rather than about
one card. Those are pinned here, over the whole sheet, so a later row
cannot reintroduce a retired shape one card at a time.

Per-card behaviour lives in the pin-card files beside this one. What is
here is the batch's own contract.
"""

import sys
from pathlib import Path

import yaml

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tier05 import draft                                          # noqa: E402
from tools import effect_walk                                     # noqa: E402



def _sheet(name):
    with open(REPO / "docs" / f"{name}-cards.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _row(name, cid):
    return next(c for c in _sheet(name) if c["id"] == cid)


def _play(state, card_id, energy=5):
    card = loader.get_card(card_id)
    state.player.energy = energy
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


def _every_effect(card):
    return list(effect_walk.iter_effects(card.get("effects", [])))


# --- §4.3: two direct faces gain a readable second price --------------------

def test_blast_radius_charges_a_chosen_discard():
    """The face was flat AoE with nothing to decide. The price is a CHOSEN
    discard -- a random one would be variance rather than a decision, and
    decisions are the packet's whole subject. Base damage is untouched:
    §4.3 says add the second price first and reprice in its own window."""
    enemies = [make_enemy(hp=40), make_enemy(hp=40)]
    state = make_state(enemies=enemies)
    state.player.hand.append(loader.get_card("strike"))
    state.player.hand.append(loader.get_card("defend"))

    _play(state, "blast_radius")

    assert [e.hp for e in enemies] == [31, 31]
    discards = _events(state, "discard")
    assert len(discards) == 1 and discards[0]["chosen"] is True
    assert len(state.player.discard_pile) >= 1


def test_no_holding_back_pays_both_of_its_prices():
    """Two prices, both existing grammar: the card Exhausts, and it adds one
    `confiscated` -- Klee's already-shipped status-price vocabulary, not an
    inline Burn injector -- to the discard pile."""
    enemies = [make_enemy(hp=40), make_enemy(hp=40)]
    state = make_state(enemies=enemies)

    card = _play(state, "no_holding_back")

    assert [e.hp for e in enemies] == [26, 26]
    assert [c.id for c in state.player.exhaust_pile] == ["no_holding_back"]
    assert card not in state.player.hand
    assert [c.id for c in state.player.discard_pile] == ["confiscated"]


def test_both_face_prices_survive_the_upgrade():
    """§4.3 keeps the ruled damage upgrade for the structural pass and says
    BOTH prices remain. An upgrade that quietly bought off a price would be
    the second ruling this batch is not allowed to make."""
    base, up = loader.get_card("blast_radius"), loader.get_card("blast_radius+")
    assert up.effects[0]["amount"] == base.effects[0]["amount"] + 3
    assert up.effects[-1] == {"op": "discard", "amount": 1, "select": "chosen"}

    nhb, nhb_up = (loader.get_card("no_holding_back"),
                   loader.get_card("no_holding_back+"))
    assert nhb_up.effects[0]["amount"] == nhb.effects[0]["amount"] + 4
    assert nhb_up.exhaust is True
    assert nhb_up.effects[-1]["card"] == "confiscated"


# --- §4.4: Explosives Workshop becomes a connective install -----------------

def _workshop_state():
    state = make_state(enemies=[make_enemy(hp=200)])
    _play(state, "explosives_workshop")
    return state


def test_the_workshop_pays_on_the_first_discard_of_the_turn_and_once():
    """One window over two event families. A turn that discards twice pays
    once; the second event is not a second trigger."""
    state = _workshop_state()
    state.player.hand.append(loader.get_card("strike"))
    state.player.hand.append(loader.get_card("defend"))
    assert state.player.powers.get("bomb_damage_up", 0) == 0

    effects.resolve_card(state, loader.get_card("kaboom"))   # no discard
    assert state.player.powers.get("bomb_damage_up", 0) == 0

    effects.resolve_card(state, _discarder())
    assert state.player.powers["bomb_damage_up"] == 1

    effects.resolve_card(state, _discarder())
    assert state.player.powers["bomb_damage_up"] == 1
    assert len(_events(state, "workshop_trigger")) == 1


def _discarder():
    """A minimal one-op card: discard 1, chosen. Built rather than borrowed
    so the pin does not move when a real card's body does."""
    from tier0.engine.state import Card
    return Card(id="probe_discard", name="Probe", cost=0, type="skill",
                rarity="common",
                effects=[{"op": "discard", "amount": 1, "select": "chosen"}])


def test_an_exhaust_is_the_same_trigger_as_a_discard():
    """"Discard OR Exhaust" is ONE window: a turn that Exhausts and then
    discards pays once, not twice. The latch is the bound the A1/A2 rail
    asks for -- a discard-heavy turn cannot turn the card into an engine."""
    state = _workshop_state()
    for _ in range(3):
        state.player.hand.append(loader.get_card("strike"))

    _play(state, "da_da_da")          # an Exhaust, no discard
    assert state.player.powers["bomb_damage_up"] == 1

    effects.resolve_card(state, _discarder())
    assert state.player.powers["bomb_damage_up"] == 1
    assert len(_events(state, "workshop_trigger")) == 1


def test_a_bomb_armed_before_the_trigger_detonates_at_the_new_number():
    """The reason the trigger pays into `bomb_damage_up` rather than a
    second bomb-damage stat. A Bomb armed three turns ago and one armed
    after the trigger detonate for the same amount; anything else is a trap
    the player cannot see."""
    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy])
    _play(state, "explosives_workshop")
    _play(state, "pop")                                  # a 5-damage Bomb
    state.player.hand.append(loader.get_card("strike"))
    effects.resolve_card(state, _discarder())            # the turn's trigger

    effects.detonate_bombs(state, enemy)

    assert [ev["damage"] for ev in _events(state, "bomb_detonation")] == [6]


def test_the_upgrade_buys_a_bigger_step_not_a_second_trigger():
    """§4.4: the upgrade raises the per-trigger increment and does not add
    another trigger per turn."""
    state = make_state(enemies=[make_enemy(hp=200)])
    _play(state, "explosives_workshop+")
    for _ in range(3):
        state.player.hand.append(loader.get_card("strike"))

    effects.resolve_card(state, _discarder())
    assert state.player.powers["bomb_damage_up"] == 2

    effects.resolve_card(state, _discarder())
    assert state.player.powers["bomb_damage_up"] == 2


def test_the_workshop_keeps_every_field_the_drafter_reads():
    """§4.4's own claim, pinned instead of asserted in prose: the card stays
    a Power with the same metadata, so the drafter's valuation of it cannot
    have moved and the conversion does not need a `D` bump.

    The credit is ZERO and that is not an accident of this card --
    `STATIC_POWER_ENGINE_VALUE` is 0.0, the deliberate 'the drafter cannot
    see an engine's payout curve at offer time' convention. Both halves are
    asserted: if either the constant or this card's metadata moves, the
    no-bump argument stops holding and this test says so.
    """
    row = _row("klee", "explosives_workshop")
    assert (row["type"], row["rarity"], row["role"], row["cost"]) == (
        "power", "uncommon", "payoff", 1)
    assert row["archetypes"] == ["demolition"]

    assert draft.STATIC_POWER_ENGINE_VALUE == 0.0
    for cid in ("explosives_workshop", "explosives_workshop+"):
        assert draft._static_power(loader.get_card(cid)) == 0.0


# --- §4.6: the `skill_tag` contribution becomes visible ---------------------

MOD_CARDS = REPO / "klee-mod" / "KleeCode" / "Cards"


def _cs_source(cid):
    """The shipped C# for one Klee row -- generated or hand-written."""
    cls = "".join(part.title() for part in cid.split("_")).replace("Mk2", "Mk2")
    for path in (MOD_CARDS / "Generated", MOD_CARDS):
        for candidate in path.glob("*.cs"):
            text = candidate.read_text(encoding="utf-8")
            if f"class {cls} " in text or f"class {cls}(" in text \
                    or f"class {cls}\n" in text or f"class {cls}:" in text:
                return text
    return None


def test_every_skill_tag_face_prints_the_burst_it_pays():
    """The tag was worth BURST_PER_SKILL_TAG on play and no face said so --
    a real number on fifteen cards that the player could only learn by
    watching the meter. Every one of them now prints it, the hand-written
    `pop` included, which is the card this pin exists for: it does not come
    out of the generator and would have been the one that stayed silent."""
    from tier0 import constants as C

    tagged = [c["id"] for c in _sheet("klee")
              if "skill_tag" in (c.get("tags") or ())]
    assert len(tagged) == 15

    line = f"[gold]Burst[/gold] +{C.BURST_PER_SKILL_TAG}."
    for cid in tagged:
        source = _cs_source(cid)
        assert source is not None, cid
        assert line in source, cid


def test_the_burst_line_is_text_and_not_a_third_keyword():
    """Rail 1 of the packet's binding rails: Klee gets no third keyword out
    of this pass. A `CardKeyword` would give the line a badge, a tooltip and
    a place in the game's auto-keyword pipeline -- which is what a keyword
    IS. So the text is checked to exist and the keyword list is checked not
    to name it."""
    marker = "IEnumerable<CardKeyword> CanonicalKeywords"
    for cid in ("pop", "mine_toss", "all_my_treasures"):
        source = _cs_source(cid)
        assert "[gold]Burst[/gold] +5." in source, cid
        # The DECLARATION, not any prose that mentions it -- the whole point
        # of the pin is which list the word is in.
        assert marker in source, cid
        declaration = source.split(marker, 1)[1].split(";", 1)[0]
        assert "Burst" not in declaration, cid


def test_the_meter_arithmetic_did_not_move():
    """The other half of §4.6: the tag, its membership and its arithmetic
    are untouched, and only the reading changed. One play, one payment, at
    the constant the face now prints."""
    from tier0 import constants as C

    state = make_state(enemies=[make_enemy(hp=200)])
    state.player.burst_max = 100

    _play(state, "pop")

    income = [(ev["source"], ev["amount"])
              for ev in _events(state, "burst_income")]
    assert income == [("skill_tag", C.BURST_PER_SKILL_TAG)]


# --- §4.2: the Bomb-placement target cut ------------------------------------
#
# The packet's acceptance line is "Klee random Bomb placement is zero and
# explicit random damage remains". Both halves are one claim about the
# sheet, so both are asserted here rather than left to the twelve edited
# rows to imply.

CONCENTRATION = {"jumpy_dumpty", "ammo_scavenging", "chain_fuse",
                 "bomb_voyage", "sorry_jean", "bombs_away",
                 "controlled_demolition", "all_my_treasures",
                 # already concentrated before the cut
                 "pop", "fish_flavored_bait", "double_pop", "trip_wire"}
DISTRIBUTION = {"mine_toss", "jumpy_dumpty_mk2", "cluster_charge",
                "sparkly_explosion"}


def test_no_klee_card_places_a_bomb_at_a_random_target():
    """Zero, over the WHOLE effect tree -- `sparkly_explosion` places
    inside a kill-conditional's `then:`, so a top-level scan would have
    read clean while a random placement shipped."""
    offenders = [
        card["id"] for card in _sheet("klee")
        for eff in _every_effect(card)
        if eff.get("op") == "place_bomb"
        and eff.get("target") in ("random_enemy", "random_enemies")
    ]
    assert offenders == []


def test_every_bomb_row_is_one_of_the_two_ruled_shapes():
    """Concentration (`target: enemy`, amount kept) or distribution
    (`target: all_enemies`, amount 1). The amount rule is not decoration:
    the engine loops amount x targets, so `all_enemies` at amount 2 is two
    Bombs on EVERY enemy -- the exact substitution §4.2 forbids."""
    for card in _sheet("klee"):
        for eff in _every_effect(card):
            if eff.get("op") != "place_bomb":
                continue
            if eff["target"] == "enemy":
                assert card["id"] in CONCENTRATION, card["id"]
            elif eff["target"] == "all_enemies":
                assert card["id"] in DISTRIBUTION, card["id"]
                assert eff["amount"] == 1, card["id"]
            else:
                raise AssertionError(
                    f"{card['id']}: bomb target {eff['target']!r}")


def test_explicit_random_damage_survives_the_cut():
    """§4.1 preserves the rows whose `damage` op is deliberately random.
    Klee controls where she PREPARES explosions; she does not always control
    where the spray lands, and the cut was aimed at the first half only.

    THE LIST IS TEN, NOT THE NINE THIS PIN WAS WRITTEN WITH, and the tenth is
    not a survivor of the cut -- it arrived after it. `big_badda_boom`'s
    Option A body (Phase 2B, R201) added `{op: damage, target: random_enemy}`
    inside its kill conditional, and Phase 2B landed on `main` while this cut
    sat staged. So the set grows for a reason outside §4.1 entirely, which is
    exactly why it is spelled out here rather than quietly re-counted: the
    cut still removed random PLACEMENT and still left random DAMAGE alone.
    The tenth row is BACKLOG `EB-126`'s thirteenth
    `TargetingRandomOpponents` caller and adds no new exposure.
    """
    random_damage = {
        card["id"] for card in _sheet("klee")
        for eff in _every_effect(card)
        if eff.get("op") == "damage"
        and eff.get("target") in ("random_enemy", "random_enemies")
    }
    assert random_damage == {
        "crackle", "da_da_da", "gleeful_barrage", "jumpy_dumpty",
        "jumpy_dumpty_mk2", "kaboom_beetle_swarm", "pocket_fireworks",
        "rapid_fire", "study_of_explosions",
        "big_badda_boom"}


def test_a_concentration_row_stacks_its_whole_payload_on_one_enemy():
    """Bomb Voyage is three Bombs, and after the cut all three land on the
    same chosen enemy. Under the old random roll they scattered."""
    aimed = make_enemy(hp=20, name="aimed")
    other = make_enemy(hp=60, name="other")
    state = make_state(enemies=[aimed, other])

    _play(state, "bomb_voyage")

    assert [b.damage for b in aimed.bombs] == [5, 5, 5]
    assert other.bombs == []


def test_a_distribution_row_gives_every_enemy_exactly_one():
    """Mine Toss is the pure distribution row: one Bomb each, however wide
    the board, and never two on one enemy."""
    enemies = [make_enemy(hp=40, name=n) for n in ("a", "b", "c", "d")]
    state = make_state(enemies=enemies)

    _play(state, "mine_toss")

    assert [[b.damage for b in e.bombs] for e in enemies] == [[5]] * 4
