"""Kokomi kickoff roster v0.1: engine-level tests for Charge, Flawless
Strategy, Conscript, Sly, the prevention ward, and the Ceremonial Garment
state (docs/kokomi-kickoff-v1.md; these lock the SYSTEMS — statline work
waits on the ruling asks; every constant is PROPOSED).
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.state import Card, CombatState
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None


def kokomi_state(enemies=None, seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def kokomi_card(**kw):
    d = dict(id="kokomi_test", name="t", cost=0, type="skill",
             character="kokomi")
    d.update(kw)
    return Card(**d)


# --- character spec ---

def test_build_kokomi_skeleton():
    p = loader.build_player("kokomi")
    assert p.character_id == "kokomi" and p.element == "hydro"
    assert p.cadence == "catalyst"
    assert p.burst_max == 10 and p.charge == 0   # v0.3 fast-cycle meter
    assert "tamakushi_casket" in p.relic_hooks
    assert [k.id for k in p.kit_cards] == ["ceremonial_garment"]
    assert loader.character_nation("kokomi") == "inazuma"
    assert p.fanfare_cap == 0                # no Furina resources


def test_garment_kit_amount_matches_constant():
    """The sheet's printed state duration and the constant must agree —
    the kit/sheet cross-check pattern (drift guard)."""
    kit = loader.get_card("ceremonial_garment")
    (state_fx,) = [fx for fx in kit.effects
                   if fx.get("power") == "ceremonial_garment"]
    assert state_fx["amount"] == C.CEREMONIAL_GARMENT_TURNS


def test_catalyst_cadence_applies_hydro_on_attacks():
    st = kokomi_state()
    effects.resolve_card(st, kokomi_card(
        type="attack", effects=[{"op": "damage", "amount": 4}]))
    assert st.enemies[0].aura == "hydro"


# --- Charge accrual (the ONE exhaust funnel) ---

def test_exhaust_funnel_gains_charge_and_burst():
    st = kokomi_state()
    p = st.player
    refpowers.exhaust_card(st, kokomi_card())
    assert p.charge == C.CHARGE_PER_EXHAUST
    assert p.burst_energy == C.KOKOMI_BURST_PER_EXHAUST
    assert any(ev["event"] == "gain_charge" and ev["source"] == "exhaust"
               for ev in st.log)


def test_played_exhaust_card_feeds_charge():
    """A played Exhaust card routes through result_pile -> exhaust_card:
    the universal rule needs no per-card text."""
    st = kokomi_state()
    card = kokomi_card(effects=[{"op": "block", "amount": 1}], exhaust=True)
    st.player.hand.append(card)
    st.player.energy = 3
    combat.play_card(st, card)
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_mid_card_exhausts_feed_charge_via_sweep():
    """exhaust_from appends directly; the after_card_played sweep fires
    the funnel per victim — Charge must arrive exactly once each."""
    st = kokomi_state()
    st.player.hand = [kokomi_card(id="fodder_a"), kokomi_card(id="fodder_b")]
    burner = kokomi_card(
        id="burner", effects=[{"op": "exhaust_from", "amount": 2}])
    st.player.hand.append(burner)
    st.player.energy = 3
    combat.play_card(st, burner)
    assert st.player.charge == 2 * C.CHARGE_PER_EXHAUST


def test_no_charge_without_casket():
    """Universal accrual is gated on the relic hook: every other
    character's exhausts are a dead branch (anchor safety)."""
    p = loader.build_player("ref_ironclad")
    st = CombatState(player=p, enemies=[make_enemy(hp=50)],
                     rng=random.Random(0))
    refpowers.exhaust_card(st, kokomi_card())
    assert p.charge == 0


def test_gain_charge_op_is_additive_premium():
    st = kokomi_state()
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "gain_charge", "amount": 4}]))
    assert st.player.charge == 4


# --- Flawless Strategy (Strength -> Charge) ---

def test_strength_converts_to_charge():
    st = kokomi_state()
    powers.apply_power(st, st.player, "strength", 2)
    assert st.player.powers.get("strength", 0) == 0
    assert st.player.charge == 2
    assert any(ev["event"] == "strength_converted" for ev in st.log)


def test_negative_strength_still_applies():
    """Mangle-class Strength LOSS is not a gain and must land normally."""
    st = kokomi_state()
    powers.apply_power(st, st.player, "strength", -3)
    assert st.player.powers.get("strength", 0) == -3
    assert st.player.charge == 0


def test_enemy_strength_untouched():
    st = kokomi_state()
    e = st.enemies[0]
    powers.apply_power(st, e, "strength", 2)
    assert e.powers.get("strength", 0) == 2


def test_sara_stormcall_is_the_conversion_exerciser():
    """The one deliberate Strength card in the Inazuma pool: Charge in
    Kokomi's hands, real Strength for anyone else."""
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("sara_tengu_stormcall"))
    assert st.player.charge == 2
    assert st.player.powers.get("strength", 0) == 0


# --- Conscript ---

def test_conscript_transforms_worst_card_into_recruit():
    st = kokomi_state()
    st.player.hand = [kokomi_card(id="chaff", type="skill",
                                  effects=[{"op": "block", "amount": 1}])]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 1}]))
    (recruit,) = st.player.hand
    assert recruit.is_companion and recruit.nation == "inazuma"
    assert recruit.conscripted and recruit.exhaust
    base = loader.get_card(recruit.id)
    if isinstance(base.cost, int):
        assert recruit.cost == max(0, base.cost + C.CONSCRIPT_COST_DELTA)


def test_conscript_never_eats_kit_or_companions():
    st = kokomi_state()
    kit = st.player.kit_cards[0]
    recruit_already = loader.get_card("gorou_war_banner")
    st.player.hand = [kit, recruit_already]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 1}]))
    assert any(ev["event"] == "conscript_whiffed" for ev in st.log)
    assert st.player.hand == [kit, recruit_already]


def test_conscript_create_mode_adds_to_hand():
    st = kokomi_state()
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 2, "mode": "create"}]))
    assert len(st.player.hand) == 2
    assert all(c.conscripted and c.exhaust for c in st.player.hand)
    assert st.cards_created_this_turn == 2


def test_conscripted_companion_is_self_sourced_for_provenance():
    """Ask §6.7 (PROPOSED): a conscripted recruit's control is Kokomi's
    own, a drafted companion's is not."""
    st = kokomi_state()
    drafted = loader.get_card("sayu_yoohoo_windwheel")
    effects.resolve_card(st, drafted)
    assert st.current_card_companion is True
    conscripted = loader.get_card("sayu_yoohoo_windwheel")
    conscripted.conscripted = True
    effects.resolve_card(st, conscripted)
    assert st.current_card_companion is False


def test_companion_pool_is_inazuma_draftables_only():
    pool = loader.companion_pool("inazuma")
    assert pool and all(c.nation == "inazuma" and c.is_companion
                        and not c.guest_star for c in pool)
    assert any(c.rarity == "rare" for c in pool)     # the Itto jackpot


# --- Sly ---

def test_sly_fires_on_card_effect_discard_only():
    st = kokomi_state()
    lantern = loader.get_card("drifting_lantern")
    st.player.hand = [lantern]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "discard", "amount": 1}]))
    assert st.player.block == 4                  # the sly line paid
    assert any(ev["event"] == "sly" for ev in st.log)


def test_sly_silent_on_end_of_turn_hand_flush():
    st = kokomi_state()
    st.player.hand = [loader.get_card("drifting_lantern")]
    pilot = NULL_PILOT
    combat._player_turn(st, pilot)
    assert not any(ev["event"] == "sly" for ev in st.log)


# --- prevention ward (kickoff §2.4) ---

def _ward_state():
    st = kokomi_state()
    st.player.powers["prevent_exhaust_ward"] = 6
    st.player.draw_pile = [kokomi_card(id=f"fuel_{i}") for i in range(5)]
    return st


def test_ward_prevents_first_unblocked_hit_and_exhausts_fuel():
    st = _ward_state()
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    assert st.player.hp == st.player.max_hp - 2      # 6 of 8 prevented
    assert len(st.player.exhaust_pile) == 1
    assert st.player.charge == C.CHARGE_PER_EXHAUST  # the proc IS fuel
    assert any(ev["event"] == "prevent_exhaust" and ev["amount"] == 6
               for ev in st.log)


def test_ward_procs_once_per_round():
    st = _ward_state()
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8, "times": 2}]
    combat._enemy_turn(st, e)
    # First hit: 6 prevented, 2 lands. Second hit: latch spent, 8 lands.
    assert st.player.hp == st.player.max_hp - 10
    assert len(st.player.exhaust_pile) == 1


def test_ward_cannot_pay_from_an_empty_deck():
    st = _ward_state()
    st.player.draw_pile = []
    st.player.discard_pile = []
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    assert st.player.hp == st.player.max_hp - 8      # defenseless
    assert not st.player.exhaust_pile


def test_ward_latch_resets_each_player_turn():
    st = _ward_state()
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    combat._player_turn(st, NULL_PILOT)
    combat._enemy_turn(st, e)
    assert len(st.player.exhaust_pile) >= 2          # proc'd again


# --- Ceremonial Garment (Shape B) ---

def test_garment_state_reads_charge_on_attacks():
    st = kokomi_state()
    p = st.player
    p.powers["ceremonial_garment"] = 2
    p.charge = 8
    e = st.enemies[0]
    hp0 = e.hp
    effects.resolve_card(st, kokomi_card(
        type="attack", effects=[{"op": "damage", "amount": 4}]))
    bonus = 8 // C.GARMENT_CHARGE_DIVISOR
    assert hp0 - e.hp == 4 + bonus


def test_garment_state_decays_per_turn():
    st = kokomi_state()
    st.player.powers["ceremonial_garment"] = 2
    powers.on_turn_end(st, st.player)
    assert st.player.powers["ceremonial_garment"] == 1


def test_charge_is_read_never_spent():
    st = kokomi_state()
    st.player.charge = 10
    effects.resolve_card(st, loader.get_card("nereids_ascension"))
    assert st.player.charge == 10                    # read, not consumed


def test_nereids_ascension_reads_charge():
    st = kokomi_state()
    e = st.enemies[0]
    st.player.charge = 10
    hp0 = e.hp
    effects.resolve_card(st, loader.get_card("nereids_ascension"))
    assert hp0 - e.hp == 12 + 10 // 2      # v0.3 base 12


def test_riptide_strike_is_the_on_curve_reader():
    """v0.3 charge-curve pass: the sub-Rare read exists and scales."""
    st = kokomi_state()
    e = st.enemies[0]
    st.player.charge = 10
    hp0 = e.hp
    effects.resolve_card(st, loader.get_card("riptide_strike"))
    assert hp0 - e.hp == 5 + 10 // 2
    assert st.player.charge == 10          # read, never spent


# --- integration: batteries run clean ---

def test_priest_deck_runs_and_accrues_charge():
    p = loader.build_player("kokomi", "priest_weighted")
    pilot = make_pilot(loader.pilot_weights("priest"))
    st = combat.run_fight(p, [make_enemy(hp=120)], pilot, seed=7)
    assert any(ev["event"] == "fight_end" for ev in st.log)
    assert p.charge > 0                              # the engine turned


def test_commander_deck_conscripts_in_play():
    p = loader.build_player("kokomi", "commander_weighted")
    pilot = make_pilot(loader.pilot_weights("commander"))
    conscripted = 0
    for seed in range(6):
        p = loader.build_player("kokomi", "commander_weighted")
        st = combat.run_fight(p, [make_enemy(hp=120)], pilot, seed=seed)
        conscripted += sum(1 for ev in st.log if ev["event"] == "conscript")
    assert conscripted > 0


# --- v0.2 sheet pass laws (R51/R52, 2026-07-24): catch -> lint culture ---

def _kokomi_sheet_rows():
    import yaml
    text = (loader.DOCS_DIR / "kokomi-cards.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


def _walk_printed(row):
    """Every printed effect: main list, conditional branches, sly riders."""
    stack = list(row.get("effects", [])) + list(row.get("sly", []))
    while stack:
        fx = stack.pop()
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                stack.extend(fx[branch])


def test_law2_no_heals_anywhere_in_her_pool():
    """R52 ask 1: NO heals, period — no amendment taken and none planned
    (Furina holds the mod's one). The v0.1 sango_prayer heal is gone; this
    gate keeps the ruling from being 'rediscovered' by a future card."""
    offenders = [row["id"] for row in _kokomi_sheet_rows()
                 if any(fx.get("op") == "heal" for fx in _walk_printed(row))]
    assert not offenders, f"R52 ask 1 violated by {offenders}"


def test_r51_debuffs_ride_exhaust_or_sly_pieces_only():
    """R51 texture (user, verbatim intent): Weak/Vulnerable are engine
    payoffs on exhaust/Sly pieces — never a spammable cheap AoE debuff at
    common (the excluded Furina commanding-gaze shape). Machine form:
    an enemy-target weak/vuln in the MAIN effects requires exhaust: true;
    a Sly rider is gated by the Sly mechanism itself; either way the card
    sits above common."""
    def enemy_debuffs(fx_list):
        return [fx for fx in fx_list
                if fx.get("op") == "apply_power"
                and fx.get("power") in ("weak", "vulnerable")
                and fx.get("target", "self") != "self"]

    offenders = []
    for row in _kokomi_sheet_rows():
        in_main = enemy_debuffs([fx for fx in _walk_printed(row)
                                 if fx not in row.get("sly", [])])
        in_sly = enemy_debuffs(row.get("sly", []))
        if not in_main and not in_sly:
            continue
        if row.get("rarity") in ("basic", "common"):
            offenders.append(f"{row['id']} (common-tier debuff)")
        if in_main and not row.get("exhaust"):
            offenders.append(f"{row['id']} (main-effect debuff, no Exhaust)")
    assert not offenders, f"R51 texture violated: {offenders}"


def test_sango_prayer_stills_the_spears():
    """R52 rework: Weak 2 to all + Block 5, zero HP restored."""
    st = kokomi_state(enemies=[make_enemy(hp=50), make_enemy(hp=50)])
    hp0 = st.player.hp
    effects.resolve_card(st, loader.get_card("sango_prayer"))
    assert all(e.powers.get("weak", 0) == 2 for e in st.enemies)
    assert st.player.block == 5
    assert st.player.hp == hp0                       # the healer heals no HP


def test_exposing_current_marks_and_burns():
    st = kokomi_state()
    e = st.enemies[0]
    hp0 = e.hp
    card = loader.get_card("exposing_current")
    assert card.exhaust                              # R51: exhaust piece
    effects.resolve_card(st, card)
    assert hp0 - e.hp == 8                           # v0.3 reprice
    assert e.powers.get("vulnerable", 0) == 2


def test_tidal_lure_sly_bell_is_a_debuff():
    st = kokomi_state()
    st.player.hand = [loader.get_card("tidal_lure")]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "discard", "amount": 1}]))
    assert st.enemies[0].powers.get("vulnerable", 0) == 1
    assert any(ev["event"] == "sly" for ev in st.log)


def test_raiden_is_a_rare_conscript_payoff():
    """R52 ask 9: the opposed apex exists, Rare only, in the pool."""
    pool = loader.companion_pool("inazuma")
    (raiden,) = [c for c in pool if c.id == "raiden_musou_no_hitotachi"]
    assert raiden.rarity == "rare" and raiden.star == 5


# --- v0.2 upgrade sheet (rest-smith dependency for the act sims) ---

def test_kokomi_upgrade_coverage_is_complete():
    """Every draftable Kokomi/Inazuma card has an expressible upgrade;
    the kit Burst deliberately has none (sparks_n_splash precedent)."""
    from tier0.content import upgrades
    import yaml
    for sheet in ("kokomi-cards.yaml", "inazuma-companions.yaml"):
        rows = yaml.safe_load(
            (loader.DOCS_DIR / sheet).read_text(encoding="utf-8"))
        for row in rows:
            if row.get("kit_card"):
                assert not upgrades.has_upgrade(row["id"])
            else:
                assert upgrades.has_upgrade(row["id"]), row["id"]


def test_kokomi_upgrades_respect_the_resource_curve():
    """Klee R1 precedent applied to her engine: no upgrade moves a
    gain_charge line or a conscript count. Checked by applying every
    upgrade and diffing the printed resource ops."""
    import yaml

    def resource_shape(card):
        return [(fx.get("op"), fx.get("amount"))
                for fx in card.effects
                if fx.get("op") in ("gain_charge", "conscript")]

    for sheet in ("kokomi-cards.yaml", "inazuma-companions.yaml"):
        rows = yaml.safe_load(
            (loader.DOCS_DIR / sheet).read_text(encoding="utf-8"))
        for row in rows:
            if row.get("kit_card"):
                continue
            base = loader.get_card(row["id"])
            upped = loader.get_card(row["id"] + "+")
            assert resource_shape(base) == resource_shape(upped), row["id"]


def test_vigil_upgrade_moves_the_cap_with_the_amount():
    """Single-application encoding: max_stacks == amount must ride along
    or the upgrade is silently swallowed (pass-2 fix lineage)."""
    upped = loader.get_card("vigil_of_the_deep+")
    (fx,) = [f for f in upped.effects
             if f.get("power") == "prevent_exhaust_ward"]
    assert fx["amount"] == 8 and fx["max_stacks"] == 8
