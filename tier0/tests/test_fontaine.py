"""Fontaine companion set v0.1 (Furina sprint 1, kickoff doc §10).

Sheet-structure locks: the ratified roster and the Cryo application
budget are enforced here so a later card edit answers to the kickoff's
convergence levers, not to a review. Plus the three DSL additions the
sheet flagged inline (reaction_triggered_this_turn, block_next_turn) and the
Guest Star reward exclusions. The Fontaine sanity check (2026-10-12,
review/ruled/fontaine-companions-2026-10-12.md, ruled) retired shatter_bonus
and moved Navia onto reactions.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state

FONTAINE_4STARS = ("chevreuse", "lynette", "charlotte", "freminet")


def _fontaine_cards():
    """The Fontaine set: the shipped sheet's rows, ported as they are to the
    prototype surface as `proto_mf_` (legacy cleanup pick 4)."""
    return [c for c in loader.prototype_cards()
            if c.id.startswith("proto_mf_")]


def _char(c):
    """The character a ported row belongs to, off its id: the surface files
    every companion row under its owner, so the cameo is read off the name
    (`proto_mf_<character>_...`)."""
    rest = c.id[len("proto_mf_"):]
    return rest.split("_", 1)[0]


# --- sheet structure ---

FONTAINE_5STARS = ("navia", "clorinde", "neuvillette", "arlecchino",
                   # The Fontaine pool rework (2026-10-19): five added.
                   "wriothesley", "lyney", "sigewinne", "escoffier", "emilie")


def test_fontaine_sheet_loads_ratified_roster():
    """The Fontaine pool rework (2026-10-19,
    review/active/fontaine-companions-2026-10-19.md): 30 cards, 8 / 13 / 9.
    The four 4-stars keep three cards each; each of the nine 5-stars has one
    Uncommon and one Rare."""
    cards = _fontaine_cards()
    shared = [c for c in cards if not c.guest_star]
    assert len(shared) == 30
    bench = [c for c in shared if c.star == 4]
    fives = [c for c in shared if c.star == 5]

    assert len(bench) == 12
    assert {_char(c) for c in bench} == set(FONTAINE_4STARS)
    for char in FONTAINE_4STARS:
        assert sum(1 for c in bench if _char(c) == char) == 3

    assert {_char(c) for c in fives} == set(FONTAINE_5STARS)
    for char in FONTAINE_5STARS:
        mine = sorted(c.rarity for c in fives if _char(c) == char)
        assert mine == ["rare", "uncommon"], (char, mine)

    by_rarity = {r: sum(1 for c in shared if c.rarity == r)
                 for r in ("common", "uncommon", "rare")}
    assert by_rarity == {"common": 8, "uncommon": 13, "rare": 9}


def test_cryo_application_budget():
    """Convergence lever 1, as the Fontaine pool rework (2026-10-19) left it:
    five Cryo cards, down from six. Freezing Point (Charlotte), Pers and
    Backstroke (Freminet) and Gracious Rebuke (Wriothesley) deal Cryo from the
    card; Chilling Penalty deals it from its Power. First-Person Shutter and
    Shattering Pressure lost theirs. The sheet must not quietly grow another."""
    budget = {"charlotte": 1, "freminet": 2, "wriothesley": 1}
    for char in budget:
        appliers = []
        for c in _fontaine_cards():
            if _char(c) != char:
                continue
            for fx in c.effects:
                if ((fx.get("applies_element") and c.element == "cryo")
                        or (fx.get("op") == "apply_aura"
                            and fx.get("element") == "cryo")):
                    appliers.append(c.id)
                    break
        assert len(appliers) == budget[char], (char, appliers)
    powered = [c.id for c in _fontaine_cards()
               if any(fx.get("power") == "mf_chilling_penalty"
                      for fx in c.effects)]
    assert powered == ["proto_mf_wriothesley_chilling_penalty"]


def test_healing_law_holds_on_fontaine_sheet():
    # R8 conjunctive law, by construction: the set contains no heal op at
    # all (sub-Rare sustain routes through Block -- Charlotte/droplets
    # conversions). The global sweep in test_errata also covers this; the
    # sheet-local assertion documents the by-construction claim.
    for c in _fontaine_cards():
        assert not any(fx.get("op") == "heal" for fx in c.effects), c.id


# --- Guest Star scoping ---

def test_guest_star_never_in_shared_rewards():
    from tier05 import rewards
    assert all(not c.guest_star
               for cs in rewards.companion_pool().values() for c in cs)
    # The offerable Fontaine five-stars are exactly the shared Rares, and no
    # guest id is among them. Since legacy cleanup stage 4 (pick 4) they are
    # the PORTED rows, `proto_mf_<shipped id>`, the shipped bodies as they are.
    roster = [c for cs in rewards.companion_pool().values() for c in cs
              if c.nation == "fontaine" and c.star == 5]
    # Eighteen since the Fontaine pool rework (2026-10-19): nine 5-stars,
    # an Uncommon and a Rare each.
    assert {c.id for c in roster} == {
        cid for cid in C.FONTAINE_OVERHAUL_POOL_IDS
        if loader.get_card(cid).star == 5}
    assert len(roster) == 18
    assert all(not c.guest_star and c.personal_pool is None for c in roster)


def test_personal_pool_not_offered_cross_character():
    """Probed on a REAL character. This used the invented id
    "furina_probe" until 2026-07-21; once card ownership became required
    (rewards.character_pool) that id had an empty pool, so the assertions
    below passed vacuously against zero offers."""
    from tier05 import rewards
    rng = random.Random(7)
    offered = {c.id for _ in range(300)
               for c in rewards.roll_rewards(rng, "furina")}
    assert offered, "empty offer set would make this test vacuous"
    assert "prune_witch_hunt" not in offered
    # Checked on the guest_star FLAG, not an id prefix. The prefix form
    # ("guest_") silently false-positives on Furina's own uncommon
    # "The Guest List" (guest_list) -- it only ever passed because the
    # probe character had no Furina cards to offer in the first place.
    assert not any(loader.get_card(cid).guest_star for cid in offered)
    # The leak this file was written to catch, stated directly: a reward
    # screen only ever offers cards the character owns (companions aside,
    # which are a shared pool by design).
    assert all(loader.get_card(cid).character == "furina"
               for cid in offered
               if not loader.get_card(cid).is_companion)


def test_unowned_character_pool_fails_loudly():
    """The rare->uncommon->common fallback used to run off the end and
    raise a bare KeyError from a dict literal. An empty pool is a config
    error and must say so."""
    from tier05 import rewards
    with pytest.raises(ValueError, match="no draftable cards"):
        rewards.roll_rewards(random.Random(1), "furina_probe")


# --- DSL: reaction_triggered_this_turn (Chevreuse) ---

def test_vanguards_valor_is_a_flat_six_for_this_turn():
    """The Fontaine pool rework (2026-10-19): "Your next Attack this turn
    deals 6 [9] additional damage." The reaction rider left, and the bonus
    ends with the turn (`NextAttackUpPower.AfterSideTurnEnd`)."""
    st = make_state(enemies=[make_enemy(hp=200)])
    card = loader.get_card("proto_mf_chevreuse_vanguards_valor")
    st.reactions_this_turn = 1
    effects.resolve_card(st, card)
    assert st.player.powers.get("next_attack_up", 0) == 6
    effects.player_turn_end_triggers(st)
    assert "next_attack_up" not in st.player.powers


def test_vanguards_valor_draws_nothing():
    """Ruled 2026-10-12: "I don't like to have cycling at Common", so the
    power-up came without the draw."""
    card = loader.get_card("proto_mf_chevreuse_vanguards_valor")
    assert card.rarity == "common"
    assert not any(fx.get("op") == "draw" for fx in card.effects)


def test_bogglecat_box_blocks_and_draws():
    """The Fontaine pool rework (2026-10-19): Backflip, 5 [8] Block, draw 2."""
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.draw_pile = [Card(id=f"filler{i}", name="f", cost=1, type="skill")
                           for i in range(5)]
    effects.resolve_card(st, loader.get_card("proto_mf_lynette_box_trick"))
    assert st.player.block == 5
    assert len(st.player.hand) == 2


def test_reactions_this_turn_resets_at_turn_start():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.reactions_this_turn = 3
    combat._player_turn(st, lambda s: None)
    assert st.reactions_this_turn == 0


# --- Charlotte, First-Person Shutter ---

def test_shutter_blocks_and_applies_weak():
    """The Fontaine pool rework (2026-10-19): "Gain 6 [9] Block. Apply 1
    Weak." The Cryo and next turn's Block left; it lays no aura."""
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, loader.get_card("proto_mf_charlotte_enduring_frosthelm"))
    assert st.player.block == 6
    assert st.enemies[0].aura is None
    assert st.enemies[0].powers.get("weak", 0) == 1
    assert "block_next_turn" not in st.player.powers


# --- Freminet (the Fontaine sanity check, 2026-10-12) ---

def test_shattering_pressure_is_an_unelemented_retain_attack():
    """The Fontaine pool rework (2026-10-19): "Retain. Deal 8 [10] damage.
    Each time you Retain this, it deals 5 additional damage this combat." No
    element. The growth is pinned in `test_fontaine_companion_rework.py`."""
    st = make_state(enemies=[make_enemy(hp=300)])
    card = loader.get_card("proto_mf_freminet_shattering_pressure")
    assert card.type == "attack" and card.rarity == "uncommon" and card.cost == 1
    assert card.retain and card.retain_grow == 5 and card.element in (None, "none")
    effects.resolve_card(st, card)
    e = st.enemies[0]
    assert 300 - e.hp == 8
    assert e.aura is None


def test_backstroke_deals_cryo():
    """The Fontaine pool rework (2026-10-19): 12 [16] Cryo and 6 [8] Block."""
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, loader.get_card("proto_mf_freminet_pressurized_floe"))
    assert st.enemies[0].aura == "cryo"
    assert st.enemies[0].hp == 188
    assert st.player.block == 6


def test_shatter_bonus_is_retired():
    assert not any(fx.get("power") == "shatter_bonus"
                   for c in _fontaine_cards() for fx in c.effects)


# --- 5-star Rares (R64, 2026-07-25): the four new powers ---

def _play(st, card_id):
    """play_card goes through the real hand/energy path -- the companion hook
    being tested lives there, not in resolve_card."""
    return _play_card(st, loader.get_card(card_id))


def _play_card(st, card):
    st.player.hand.append(card)
    st.player.energy = 9
    combat.play_card(st, card)
    return card


def _probe_attack(amount, *, times=1, element=None):
    """A plain non-Companion Attack, printed `amount` (x `times`)."""
    fx = {"op": "damage", "amount": amount, "target": "enemy"}
    if times > 1:
        fx["times"] = times
    if element:
        fx["applies_element"] = True
    return Card(id="probe_attack", name="Probe", cost=1, type="attack",
                element=element, effects=[fx])


def test_cannon_fire_support_hits_all_enemies_each_turn():
    """The Fontaine pool rework (2026-10-19): "At the start of your turn,
    deal 5 [7] Geo damage to ALL enemies." Nothing on play; on an aura each
    hit is a Crystallize."""
    st = make_state(enemies=[make_enemy(hp=200), make_enemy(hp=200)])
    _play(st, "proto_mf_navia_cannon_fire_support")
    assert st.player.powers["cannon_fire_support"] == 5
    assert all(e.hp == 200 for e in st.enemies)
    st.enemies[0].aura = "hydro"
    st.enemies[0].aura_turns_left = C.AURA_DURATION_TURNS
    effects.player_turn_start_triggers(st)
    assert st.enemies[1].hp == 195
    assert st.enemies[0].hp < 200
    assert st.enemies[0].aura is None                  # Crystallized


def test_cannon_fire_support_no_longer_pays_block_on_a_reaction():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.powers["cannon_fire_support"] = 5
    st.enemies[0].aura = "hydro"
    st.enemies[0].aura_turns_left = C.AURA_DURATION_TURNS
    _play_card(st, _probe_attack(4, element="pyro"))     # Vaporize
    assert st.player.block == 0


def test_night_vigil_pays_only_against_an_aura_and_only_on_attacks():
    """Clorinde reads the board before she moves. Same hook and same ordering
    as Albedo's solar_isotoma -- read BEFORE the hit consumes the aura."""
    st = make_state(enemies=[make_enemy(hp=300)])
    e = st.enemies[0]
    st.player.powers["night_vigil"] = 3

    # No aura: the rider is worth nothing.
    before = e.hp
    effects.resolve_card(st, _probe_attack(6, element="cryo"))   # 6, cryo
    assert before - e.hp == 6
    assert e.aura == "cryo"

    # Aura up: the SAME card now pays the rider, and it is collected even
    # though this hit reacts the aura away.
    before = e.hp
    effects.resolve_card(st, loader.get_card("proto_mf_chevreuse_interdiction_fire"))
    melt = C.MELT_MULT                    # pyro onto cryo
    assert before - e.hp == int((7 + 3) * melt)


def test_night_vigil_does_not_pay_bombs_or_summons():
    """'Your Attacks' means card Attacks. A bomb tick is not one."""
    st = make_state(enemies=[make_enemy(hp=300)])
    e = st.enemies[0]
    st.player.powers["night_vigil"] = 5
    e.aura = "hydro"
    before = e.hp
    effects.deal_damage_to_enemy(st, e, 10, element=None, source="bomb")
    assert before - e.hp == 10


# A plain Hydro applier (Block, then Hydro on the enemy).
HYDRO_APPLIER = "proto_mc_barbara_show_begin"


def test_ancient_sea_authority_extends_applied_and_refreshed_auras():
    st = make_state(enemies=[make_enemy(hp=200)])
    e = st.enemies[0]
    effects.resolve_card(st, loader.get_card(HYDRO_APPLIER))
    assert e.aura_turns_left == C.AURA_DURATION_TURNS

    st2 = make_state(enemies=[make_enemy(hp=200)])
    e2 = st2.enemies[0]
    effects.resolve_card(
        st2, loader.get_card("proto_mf_neuvillette_ancient_sea_authority"))
    effects.resolve_card(st2, loader.get_card(HYDRO_APPLIER))
    assert e2.aura_turns_left == C.AURA_DURATION_TURNS + 1
    # Refresh must agree with application -- the reason aura_duration() is a
    # function rather than the constant read at three call sites.
    e2.aura_turns_left = 1
    effects.resolve_card(st2, loader.get_card(HYDRO_APPLIER))
    assert e2.aura_turns_left == C.AURA_DURATION_TURNS + 1


def test_ancient_sea_authority_hits_for_hydro_each_turn_start():
    """2026-10-11 Companion pass: "At the start of your turn, deal 5 Hydro
    damage to a random enemy." (it applied Hydro only before). Nothing on
    play; the hit lands at the turn start, lays the Hydro, and the Hydro
    lasts the extra turn."""
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(
        st, loader.get_card("proto_mf_neuvillette_ancient_sea_authority"))
    assert all(e.aura is None for e in st.enemies)
    assert st.enemies[0].hp == 200
    effects.player_turn_start_triggers(st)
    e = st.enemies[0]
    assert e.hp == 200 - C.ANCIENT_SEA_DMG == 195
    assert e.aura == "hydro"
    assert e.aura_turns_left == C.AURA_DURATION_TURNS + 1


def test_masque_ratchets_strength_every_turn():
    st = make_state(enemies=[make_enemy(hp=300)])
    effects.resolve_card(st, loader.get_card("proto_mf_arlecchino_masque_red_death"))
    assert st.player.powers.get("strength", 0) == 0    # nothing on play
    effects.player_turn_start_triggers(st)
    assert st.player.powers["strength"] == 1
    effects.player_turn_start_triggers(st)
    assert st.player.powers["strength"] == 2           # a ratchet, not a flat


def test_masque_loses_1_hp_every_turn_start_before_the_strength():
    """2026-10-11 Companion pass: "At the start of your turn, lose 1 HP and
    gain 1 Strength." Unblockable, flat per turn, and not scaled by the
    stack (the upgrade's 2 Strength still costs 1 HP)."""
    st = make_state(hp=50, enemies=[make_enemy(hp=300)])
    effects.resolve_card(st, loader.get_card("proto_mf_arlecchino_masque_red_death"))
    assert st.player.hp == 50                          # nothing on play
    st.player.block = 10
    effects.player_turn_start_triggers(st)
    assert st.player.hp == 50 - C.MASQUE_HP_LOSS == 49
    assert st.player.block == 10                       # Block does not pay it
    assert st.player.powers["strength"] == 1
    effects.player_turn_start_triggers(st)
    assert st.player.hp == 48

    st = make_state(hp=50, enemies=[make_enemy(hp=300)])
    st.player.powers["masque_red_death"] = 2           # the upgraded stack
    effects.player_turn_start_triggers(st)
    assert st.player.hp == 49
    assert st.player.powers["strength"] == 2


def test_masque_bond_of_life_is_gone():
    """The Bond of Life Block clause left in the 2026-10-11 pass: Block
    standing at the end of the turn is no longer eaten."""
    st = make_state(enemies=[make_enemy(hp=300)])
    effects.resolve_card(st, loader.get_card("proto_mf_arlecchino_masque_red_death"))
    st.player.block = 12
    effects.player_turn_end_triggers(st)
    assert st.player.block == 12
    assert not [ev for ev in st.log if ev["event"] == "bond_of_life"]
    assert not hasattr(C, "MASQUE_BOND_BLOCK")


@pytest.mark.parametrize("stacks", (0, 1, 2))
def test_masque_pays_no_flat_damage_rider_on_attacks(stacks):
    """EB-98: the ORIGINAL "+N damage on your Attacks" half was deleted on
    2026-07-25 and replaced by the Strength ratchet plus the Bond, but the
    rider stayed in _op_damage and was paid on top of the Strength. An Attack
    now deals its PRINTED number whatever the masque stack count, until a turn
    start has converted stacks into real Strength. MasqueRedDeathPower carries
    no damage modifier either, so this is the C#-parity reading as well.

    Read BEFORE any turn start (Strength still 0) so the rider, if it came
    back, would be the only term able to move the number.
    """
    st = make_state(enemies=[make_enemy(hp=300)])
    st.player.powers["masque_red_death"] = stacks
    assert st.player.powers.get("strength", 0) == 0

    hp = st.enemies[0].hp
    _play_card(st, _probe_attack(16))              # printed 16, single hit
    assert hp - st.enemies[0].hp == 16

    hp = st.enemies[0].hp
    _play_card(st, _probe_attack(5, times=3))      # printed 5 x 3
    assert hp - st.enemies[0].hp == 15


