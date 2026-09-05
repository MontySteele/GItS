"""The Mondstadt companion overhaul arm -- the flag, and both sides of it.

The source is the approved workshop `companion-workshop-mondstadt-2026-09-01.md`
(a Paper artefact on the companion-workshop branch, not in this tree): sec.1 the
bar and the authoring rules, sec.3 the per-character rewrites, sec.5 the counts.
[USER] approved it 2026-09-01 at all six default picks.

THE FIRST SECTION IS THE ONE THAT MATTERS. `C.COMPANION_OVERHAUL` ships OFF, and
with it off every companion offer any measurement was ever taken on is still the
same offer. That is an ACCEPTANCE CONDITION, not an intention, so it is pinned
here rather than trusted -- the same shape `test_klee_overhaul.py` uses for its
own arm.

WHAT THE SIM DOES HERE, unlike the Klee overhaul beside it. That arm is C# FIRST
and its ops REFUSE to resolve in tier0. This one is built in BOTH engines,
because it needed no new op at all: every row is written in the grammar the
sheets already speak, and the nine new POWERS ride two hooks the engine already
runs (`player_turn_start_triggers` and `player_turn_end_triggers`). A rule that
costs no new primitive is cheaper to mirror than to quarantine.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

REPO = Path(__file__).resolve().parents[2]

#: The seventeen rows the workshop retires from the offerable pool. Read off
#: the shipped sheet rather than listed, so the day an eighteenth Mondstadt row
#: ships this test asks about it too.
SHIPPED_MONDSTADT = tuple(sorted(
    c.id for c in loader._card_index().values()
    if c.is_companion and c.nation == "mondstadt"))


def _caches_clear():
    """Every memo whose answer depends on the flag, on both sides.

    `_card_prototype` resolves a `proto_` id only while some arm is on, and
    the three `rewards` caches all read the roster seam. A test that flipped
    the flag without clearing these would read an answer cached from before
    the flip -- which is the failure mode `test_klee_overhaul`'s fixture
    documents, met here at four call sites instead of two.
    """
    loader._card_prototype.cache_clear()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared going in and out."""
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    _caches_clear()


def _pool_ids(pool):
    return {c.id for cards in pool.values() for c in cards}


# ---------------------------------------------------------------------------
# THE FLAG IS OFF, AND THAT IS THE ACCEPTANCE CONDITION
# ---------------------------------------------------------------------------

def test_the_flag_ships_off():
    assert C.COMPANION_OVERHAUL is False


def test_flag_off_the_seam_returns_none():
    """No replacement, so `_companion_roster` is the shipped index filtered
    exactly as `companion_pool` always filtered it."""
    assert loader.companion_roster_replacement() is None


def test_flag_off_every_shipped_mondstadt_row_is_still_offerable():
    offerable = _pool_ids(rewards.companion_pool())
    # prune_witch_hunt is personal_pool, but `companion_pool` tiers every
    # companion and lets the per-character filter run at the offer site, so
    # all seventeen are in the pool with the flag off.
    assert set(SHIPPED_MONDSTADT) <= offerable


def test_flag_off_no_prototype_row_can_be_offered():
    offerable = _pool_ids(rewards.companion_pool())
    assert not [i for i in offerable if i.startswith("proto_")]


def test_flag_off_the_turn_hooks_are_no_ops():
    """The two functions the arm adds to the turn structure return before
    touching anything. Asserted against a state that CARRIES the arm's powers,
    because a hook that ran while the flag was off would be a silent second
    rule set on every shipped run."""
    st = make_state()
    st.player.powers.update({"mc_signature_mix": 2, "mc_revelation": 1,
                             "mc_oz": 1, "mc_glacial_waltz": 3})
    before = (dict(st.player.powers), st.player.block,
              [e.hp for e in st.enemies])
    effects.companion_overhaul_turn_start(st)
    effects.companion_overhaul_turn_end(st)
    assert (dict(st.player.powers), st.player.block,
            [e.hp for e in st.enemies]) == before


# ---------------------------------------------------------------------------
# THE FLAG IS ON: WHAT MOVES
# ---------------------------------------------------------------------------

def test_flag_on_the_shipped_mondstadt_rows_leave_the_pool(overhaul):
    offerable = _pool_ids(rewards.companion_pool())
    assert not (set(SHIPPED_MONDSTADT) & offerable)


def test_flag_on_every_overhaul_row_is_offerable(overhaul):
    offerable = _pool_ids(rewards.companion_pool())
    assert set(C.MONDSTADT_OVERHAUL_POOL_IDS) <= offerable


def test_flag_on_fontaine_is_untouched(overhaul):
    """Each workshop is a NATION document (both say so in their own sec.6), and
    Fontaine has none yet. A nation-scoped replacement that quietly moved an
    unwritten nation's rows would be the defect this asserts against.

    IT USED TO SAY "inazuma and fontaine", and the Inazuma half moved out on
    2026-09-02 when the Inazuma workshop was approved and built -- so this test
    is now the last nation the arm leaves alone. `C.COMPANION_OVERHAUL_NATIONS`
    is the one list that decides, and the assertion below is its complement."""
    assert "fontaine" not in C.COMPANION_OVERHAUL_NATIONS
    before = {c.id for c in loader._card_index().values()
              if c.is_companion and c.nation == "fontaine"}
    after = {c.id for c in rewards._companion_roster()
             if c.nation == "fontaine"}
    assert before == after


def test_every_overhaul_id_resolves_to_a_mondstadt_companion(overhaul):
    for cid in C.MONDSTADT_OVERHAUL_POOL_IDS:
        card = loader.peek_card(cid)
        assert card.is_companion, cid
        assert card.nation == C.COMPANION_OVERHAUL_NATION, cid
        assert card.personal_pool is None, cid
        assert card.rarity in C.RARITY_ODDS, cid


def test_the_pool_ids_and_the_sheet_agree(overhaul):
    """`C.MONDSTADT_OVERHAUL_POOL_IDS` is the arm's list and the sheet is
    where the rows live; a row on one and not the other is a row that either
    cannot be offered or does not exist.

    THREE LISTS SINCE R236, and the split is what a `proto_mc_` row can be. The
    Mondstadt workshop's sec.3 rewrites the nation's UNIVERSALS, its sec.4 gives
    Klee four PERSONALS (`personal_pool`, filtered at every offer site), and its
    sec.3 stand-ins are handed to Klee IN PLACE of a Universal and are a member
    of no pool -- on the sheet and deliberately on neither pool list, subtracted
    by `C.COMPANION_STANDIN_IDS` rather than by their `replaces:` key, so a
    stand-in that fell off that list fails here instead of quietly joining the
    offerable pool. A row on none of the three is still the defect this asks
    about."""
    on_sheet = {c.id for c in loader.prototype_cards()
                if c.id.startswith("proto_mc_")}
    assert set(C.COMPANION_STANDIN_IDS) <= on_sheet
    assert on_sheet - set(C.COMPANION_STANDIN_IDS) == (
        set(C.MONDSTADT_OVERHAUL_POOL_IDS) | set(C.COVEN_PERSONAL_POOL_IDS))
    assert not (set(C.MONDSTADT_OVERHAUL_POOL_IDS)
                & set(C.COVEN_PERSONAL_POOL_IDS))
    assert not (set(C.COMPANION_STANDIN_IDS)
                & (set(C.MONDSTADT_OVERHAUL_POOL_IDS)
                   | set(C.COVEN_PERSONAL_POOL_IDS)))


def test_the_banner_roster_moves_with_the_pool(overhaul):
    """R64's whole point: the Featured Banner and the reward slot must read
    ONE roster. A banner still built from the shipped index would feature
    five-stars the slot cannot hand out."""
    featured = {c.id for c in rewards.five_star_roster("mondstadt")}
    assert featured
    assert all(i.startswith("proto_mc_") for i in featured)
    offerable = _pool_ids(rewards.companion_pool())
    assert featured <= offerable


# ---------------------------------------------------------------------------
# HEXEREI: ONE WORD, NO EFFECT
# ---------------------------------------------------------------------------

#: The rows the workshop's sec.3 marks Hexerei, across all thirty-four.
HEXEREI_ROWS = {
    "proto_mc_albedo_solar_isotoma",
    "proto_mc_fischl_nightrider",
    "proto_mc_fischl_oz",
    "proto_mc_sucrose_gust",
    "proto_mc_sucrose_astable",
    "proto_mc_sucrose_catalyst_conversion",
    "proto_mc_nicole_revelation",
    "proto_mc_mona_stellaris_phantasm",
    "proto_mc_venti_grand_ode",
    # The second wave's four, off the same sec.3 lines: Durin, Razor twice,
    # and Varka are all tagged characters in the workshop's own list.
    "proto_mc_durin_binary_form",
    "proto_mc_razor_claw_and_thunder",
    "proto_mc_razor_lightning_fang",
    "proto_mc_varka_sturm_und_drang",
    # The coven Personal off the same sec.3 line as the shipped Prune row it
    # supersedes: Prune is a tagged character in the workshop's own list.
    "proto_mc_prune_hexhunter_chime",
    # THE FAMILY STAND-INS (R236 sec.3), each tagged like the Universal it is
    # handed out in place of -- which is what lets Nicole's own stand-in pay
    # for the other three.
    "proto_mc_albedo_tectonic_tide",
    "proto_mc_fischl_sinful_hex",
    "proto_mc_nicole_ladder_of_ascent",
    "proto_mc_sucrose_mollis_favonius",
}


def test_the_hexerei_mark_is_on_exactly_the_rows_the_workshop_names():
    marked = {c.id for c in loader.prototype_cards()
              if c.id.startswith("proto_mc_") and c.hexerei}
    assert marked == HEXEREI_ROWS


#: THE FILES ALLOWED TO NAME THE FAMILY MARK, and the list is the whole point.
#:
#: Pick 2's words were "It does nothing by itself", and this test was the gate
#: that kept it so: the field's own declaration, and nothing else. R236 sec.3
#: MOVED IT, which is exactly what the gate was built to force -- Nicole's
#: family stand-in, "whenever you play a Hexerei card", is the Klee reader pick
#: 2 said would carry the payoff. So the mark is mechanical now and the gate is
#: a list of ONE reader rather than of none. A second reader is still a
#: deliberate change: adding a file here means somebody answered "does this
#: row's FAMILY really decide a rule?" out loud, in a diff.
HEXEREI_READERS = [
    "tier0/engine/companion_hexerei.py",     # Nicole's Ladder of Divine Ascent
    "tier0/engine/state.py",                 # the field's own declaration
]


def test_only_the_declared_readers_name_the_hexerei_mark():
    readers = []
    for path in sorted((REPO / "tier0").rglob("*.py")):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for hit in re.finditer(r"\.hexerei\b|\bhexerei\s*[:=]", text):
            line = text[:hit.start()].count("\n") + 1
            readers.append(f"{path.relative_to(REPO).as_posix()}:{line}")
    assert sorted({r.split(":")[0] for r in readers}) == HEXEREI_READERS, \
        readers


# ---------------------------------------------------------------------------
# THE NEW PREDICATES
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hp,max_hp,expect", [
    (39, 80, True),      # below half
    (40, 80, False),     # AT the bar reads False -- strictly below
    (41, 80, False),
])
def test_hp_pct_below(hp, max_hp, expect):
    st = make_state(hp=max_hp)
    st.player.hp = hp
    assert effects._predicate(st, "hp_pct_below_50") is expect


@pytest.mark.parametrize("hp,max_hp,expect", [
    (57, 80, True),      # above 70%
    (56, 80, False),     # AT the bar reads False -- strictly above
    (10, 80, False),
])
def test_hp_pct_above(hp, max_hp, expect):
    st = make_state(hp=max_hp)
    st.player.hp = hp
    assert effects._predicate(st, "hp_pct_above_70") is expect


def test_both_hp_predicates_are_registered_for_the_loader():
    assert effects.is_known_predicate("hp_pct_below_50")
    assert effects.is_known_predicate("hp_pct_above_70")
    # The argument must be an integer, like every other parametric bar.
    assert not effects.is_known_predicate("hp_pct_below_half")


# ---------------------------------------------------------------------------
# THE NINE POWERS
# ---------------------------------------------------------------------------

def test_signature_mix_pays_block_then_ticks(overhaul):
    st = make_state()
    st.player.powers["mc_signature_mix"] = 2
    effects.companion_overhaul_turn_start(st)
    assert st.player.block == C.MC_SIGNATURE_MIX_BLOCK
    assert st.player.powers["mc_signature_mix"] == 1
    st.player.block = 0
    effects.companion_overhaul_turn_start(st)
    assert st.player.block == C.MC_SIGNATURE_MIX_BLOCK
    assert "mc_signature_mix" not in st.player.powers
    st.player.block = 0
    effects.companion_overhaul_turn_start(st)
    assert st.player.block == 0


def test_revelation_pays_strength_only_after_a_turn_that_held_block(overhaul):
    st = make_state()
    st.player.powers["mc_revelation"] = 1
    # Turn one: nobody has held a line yet, so Block only.
    effects.companion_overhaul_turn_start(st)
    assert st.player.block == C.MC_REVELATION_BLOCK
    assert st.player.powers.get("strength", 0) == 0
    # The turn ends with Block standing, so the latch arms.
    effects.companion_overhaul_turn_end(st)
    assert st.player.mc_held_block_at_turn_end is True
    st.player.block = 0
    effects.companion_overhaul_turn_start(st)
    assert st.player.powers["strength"] == C.MC_REVELATION_STRENGTH


def test_revelation_pays_no_strength_after_a_turn_that_spent_its_block(
        overhaul):
    st = make_state()
    st.player.powers["mc_revelation"] = 1
    st.player.block = 0
    effects.companion_overhaul_turn_end(st)
    assert st.player.mc_held_block_at_turn_end is False
    effects.companion_overhaul_turn_start(st)
    assert st.player.powers.get("strength", 0) == 0


def test_the_omen_fires_at_the_next_turn_start_and_leaves(overhaul):
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.player.powers["mc_omen"] = 1
    effects.companion_overhaul_turn_start(st)
    assert all(e.powers.get("vulnerable", 0) == C.MC_OMEN_VULNERABLE
               for e in st.enemies)
    assert "mc_omen" not in st.player.powers


def test_the_omen_is_popped_whole_rather_than_ticked(overhaul):
    """Two copies pay two Vulnerable NEXT turn, not one Vulnerable on each of
    two turns: the promise is kept once however many copies were played."""
    st = make_state()
    st.player.powers["mc_omen"] = 2
    effects.companion_overhaul_turn_start(st)
    assert st.enemies[0].powers["vulnerable"] == 2 * C.MC_OMEN_VULNERABLE
    assert "mc_omen" not in st.player.powers


def test_glacial_waltz_hits_and_ticks(overhaul):
    st = make_state()
    st.player.powers["mc_glacial_waltz"] = 3
    effects.companion_overhaul_turn_end(st)
    assert st.enemies[0].hp < 50
    assert st.enemies[0].aura == "cryo"
    assert st.player.powers["mc_glacial_waltz"] == 2


def test_oz_is_permanent_and_pays_once_per_copy(overhaul):
    st = make_state()
    st.player.powers["mc_oz"] = 2
    effects.companion_overhaul_turn_end(st)
    # Two volleys of MC_OZ_DMG each. The second one lands into an Electro
    # aura the first applied, so it REFRESHES rather than reacting -- damage
    # is what this asserts, not the aura lifecycle.
    assert st.enemies[0].hp == 50 - 2 * C.MC_OZ_DMG
    assert st.player.powers["mc_oz"] == 2, "no turn limit (workshop sec.1)"


def test_lightning_rose_applies_its_vulnerable_after_the_hit(overhaul):
    st = make_state()
    st.player.powers["mc_lightning_rose"] = 3
    effects.companion_overhaul_turn_end(st)
    enemy = st.enemies[0]
    # The hit is unamplified: a Vulnerable applied first would have made it
    # 1.5x, which is the reading the printed sentence does not support.
    assert enemy.hp == 50 - C.MC_LIGHTNING_ROSE_DMG
    assert enemy.powers["vulnerable"] == C.MC_LIGHTNING_ROSE_VULN
    assert st.player.powers["mc_lightning_rose"] == 2


def test_grand_ode_swirls_every_enemy_and_ticks(overhaul):
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.enemies[0].aura = "pyro"
    st.enemies[1].aura = "hydro"
    st.player.powers["mc_grand_ode"] = 2
    effects.companion_overhaul_turn_end(st)
    # This engine's Swirl SPREADS the aura it touched across the board (and
    # Anemo itself never sticks), which is exactly what the `swirl` op does --
    # the power calls the same `reactions.resolve_hit`, so the two cannot mean
    # different things. Board order decides what the second enemy ends up
    # holding, and asserting it here is what would catch the power growing a
    # private Swirl of its own.
    assert [e.aura for e in st.enemies] == ["pyro", "pyro"]
    assert st.player.powers["mc_grand_ode"] == 1


def test_dandelion_breeze_pays_its_block_even_with_no_aura_on_the_board(
        overhaul):
    st = make_state()
    st.player.powers["mc_dandelion_breeze"] = 1
    effects.companion_overhaul_turn_end(st)
    assert st.player.block == C.MC_DANDELION_BREEZE_BLOCK


def test_dandelion_breeze_swirls_the_aura_bearer(overhaul):
    """It picks the aura-bearer and Swirls THERE -- the clean enemy catches
    the spread, which is what a Swirl is in this engine."""
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.enemies[1].aura = "cryo"
    st.player.powers["mc_dandelion_breeze"] = 1
    effects.companion_overhaul_turn_end(st)
    assert [e.aura for e in st.enemies] == ["cryo", "cryo"]
    assert st.player.block == C.MC_DANDELION_BREEZE_BLOCK


def test_the_isotoma_pays_nothing_without_an_aura(overhaul):
    """Both halves are inside the condition -- "if any enemy has an aura, deal
    8 damage to that enemy AND gain 4 Block" is one guarded sentence, unlike
    Jean's, whose clauses are joined by a bare "and"."""
    st = make_state()
    st.player.powers["mc_isotoma_bloom"] = 1
    effects.companion_overhaul_turn_end(st)
    assert st.player.block == 0
    assert st.enemies[0].hp == 50


def test_the_isotoma_hits_the_aura_bearer_and_pays_block(overhaul):
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.enemies[1].aura = "hydro"
    st.player.powers["mc_isotoma_bloom"] = 1
    effects.companion_overhaul_turn_end(st)
    assert st.enemies[0].hp == 50
    assert st.enemies[1].hp == 50 - C.MC_ISOTOMA_DMG
    # No element on the damage, so the aura it found is still standing.
    assert st.enemies[1].aura == "hydro"
    assert st.player.block == C.MC_ISOTOMA_BLOCK


def test_the_end_of_turn_order_is_the_one_the_mod_walks(overhaul):
    """The C# twin (`CompanionOverhaulTurnEnd`) walks the power types in one
    fixed sequence. This asserts the sim's source declares the same one --
    several of them put an element on the board and three draw from the rng,
    so a divergence here is a divergence in which reactions fire and in every
    later roll of the fight.

    THE SECOND WAVE ADDED FOUR AND ONLY ONE OF THEM JOINS THE WALK. Eula's
    Lightfall Sword deals damage and is hosted on an enemy, so its position
    matters and it is driven by the listener like the six; the other three are
    a tick and two removals, which cannot change an outcome by running in a
    different order, so they keep their own `AfterSideTurnEnd` broadcast in the
    mod exactly as the shipped `AttackUpThisTurnPower` does."""
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def companion_overhaul_turn_end(")[1]
    body = body.split("\ndef ")[0]
    order = [m for m in re.findall(r'"(mc_[a-z_]+)"', body)]
    seen = list(dict.fromkeys(order))
    assert seen == ["mc_glacial_waltz", "mc_oz", "mc_lightning_rose",
                    "mc_grand_ode", "mc_dandelion_breeze",
                    "mc_isotoma_bloom",
                    "mc_lightfall_sword", "mc_favonian_favor",
                    "mc_passion_overload", "mc_lightning_fang"], seen

    cs = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "CompanionOverhaulPowers.cs").read_text(encoding="utf-8")
    walk = cs.split("public override async Task AfterSideTurnEnd(")[1]
    cs_order = re.findall(r"OfType<(\w+Power)>", walk)
    assert cs_order == ["GlacialWaltzPower", "MondstadtOzPower",
                        "LightningRosePower", "GrandOdePower",
                        "DandelionBreezePower", "SolarIsotomaBloomPower",
                        "LightfallSwordPower",
                        # THE INAZUMA ARM'S BLOCK, appended before the latch --
                        # its own file's sim twin is
                        # `effects.inazuma_overhaul_turn_end`, pinned by
                        # `test_inazuma_companion_overhaul.py`, and this
                        # assertion is where the two walks are held level.
                        "JuugaPower", "MujiMujiDarumaPower",
                        "SanctifyingRingPower", "SesshouSakuraPower",
                        "SoumetsuPower", "KyoukaPower", "TamotoPower",
                        "CrimsonOoyoroiPower", "WarBannerPower",
                        "AurousBlazePower",
                        # KLEE'S COVEN (R236), last before the latch. Its sim
                        # twin is `companion_coven.turn_end`, called from the
                        # tail of `player_turn_end_triggers` for the same
                        # reason: the throw draws from the rng.
                        "YueguiPower",
                        "RevelationPower"], cs_order


# ---------------------------------------------------------------------------
# THE CARDS THEMSELVES, PLAYED
# ---------------------------------------------------------------------------

def _play(state, card_id):
    effects.resolve_card(state, loader.get_card(card_id))


def test_breastplate_pays_its_bonus_only_below_half(overhaul):
    st = make_state(hp=80)
    _play(st, "proto_mc_noelle_breastplate")
    assert st.player.block == 6
    st = make_state(hp=80)
    st.player.hp = 20
    _play(st, "proto_mc_noelle_breastplate")
    assert st.player.block == 10


def test_fantastic_voyage_takes_the_other_arm_when_hurt(overhaul):
    st = make_state(hp=80)
    _play(st, "proto_mc_bennett_fantastic_voyage")
    assert st.player.powers["strength"] == 3
    assert st.player.block == 0
    st = make_state(hp=80)
    st.player.hp = 20
    _play(st, "proto_mc_bennett_fantastic_voyage")
    assert st.player.powers.get("strength", 0) == 0
    assert st.player.block == 10


def test_ravaging_confession_reads_the_aura_she_found(overhaul):
    """"If the enemy has an aura, apply 1 Vulnerable" is a SNAPSHOT taken at
    card start (`state.target_had_aura`), not a live read after the hit.

    That is the reading the engine already had and the C# was made to match:
    Rosaria is an Attack that APPLIES Cryo, so a live read would always find
    the aura she just left and the branch would fire on every play. "From
    behind", in the workshop's word -- she is rewarded for hitting an enemy
    somebody else already lit up."""
    clean = make_state()
    _play(clean, "proto_mc_rosaria_ravaging_confession")
    assert clean.enemies[0].powers.get("vulnerable", 0) == 0

    lit = make_state()
    lit.enemies[0].aura = "hydro"
    _play(lit, "proto_mc_rosaria_ravaging_confession")
    assert lit.enemies[0].powers["vulnerable"] == 1


def test_nightrider_calls_oz_only_when_oz_is_out(overhaul):
    st = make_state()
    _play(st, "proto_mc_fischl_nightrider")
    plain = 50 - st.enemies[0].hp
    st = make_state()
    st.player.powers["mc_oz"] = 1
    _play(st, "proto_mc_fischl_nightrider")
    assert 50 - st.enemies[0].hp > plain


def test_every_overhaul_row_resolves_without_raising(overhaul):
    """The cheapest possible whole-sheet smoke: a row that cannot be played is
    a row a seat cannot grade. Two enemies, one of them aura'd, so the
    conditional and the targeting arms are both reachable."""
    for cid in C.MONDSTADT_OVERHAUL_POOL_IDS:
        st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
        st.enemies[1].aura = "hydro"
        st.player.draw_pile = [Card(id=f"f{i}", name="f", cost=1,
                                    type="skill") for i in range(5)]
        _play(st, cid)
        effects.companion_overhaul_turn_end(st)
        effects.companion_overhaul_turn_start(st)


# ---------------------------------------------------------------------------
# `EB-549` -- THE OTHER DOOR, and it went around the roster
# ---------------------------------------------------------------------------
#
# THE FIND (Furina r13 lane 1). "Two cards in this run share a name with a
# completely different card": the card-reward copy of `Kaeya -- Frostgnaw` read
# "Deal 8 damage. Gain 3 Block" and the copy An Invitation fetched into hand was
# a 6-damage, no-Block card under the same title. `Dahlia -- Sacramental Shower`
# was a cost-1 Attack in play and a cost-1 Skill at a reward. "From the seat
# they are simply two different cards with one name."
#
# THEY ARE THE ARM'S ROW AND THE SHIPPED ROW IT REWRITES. A prototype row that
# shadows a shipped one keeps its printed name, and the whole premise of that
# (`EB-322`) is that the arm substitutes the shipped row out, so ONE of the pair
# is reachable in a build. `companion_roster_replacement` makes that true at the
# offer door; the Guest Star generation pool read `_card_index` and went around
# it -- `EB-491`'s lesson one door over.


def test_the_generated_pool_offers_the_arms_row_and_not_the_shipped_one(
        overhaul):
    """The seat's own pair, at the door that fetched the wrong half."""
    ids = {c.id for c in loader.guest_star_generation_pool("common")}

    assert "proto_mc_kaeya_frostgnaw" in ids
    assert "kaeya_frostgnaw" not in ids
    assert "proto_mc_dahlia_sacramental_shower" in ids
    assert "dahlia_sacramental_shower" not in ids


def test_no_name_the_generated_pool_can_show_is_offerable_twice(overhaul):
    """The row's acceptance, stated over the whole pool rather than the two
    rows that were caught: a shadow and the row it shadows print one title, so
    a build in which BOTH are reachable is the defect whatever the pair."""
    for rarity in ("common", "uncommon"):
        names = [loader.display_name(c.name)
                 for c in loader.guest_star_generation_pool(rarity)]
        assert len(names) == len(set(names)), sorted(names)


def test_the_flag_off_pool_is_byte_for_byte_what_it_always_was():
    """The acceptance condition on the flag, and the half that makes the change
    narrow: with no replacement the companion half is the shipped index
    filtered exactly as it was, and the Guest Star half never moved at all."""
    _caches_clear()
    ids = {c.id for c in loader.guest_star_generation_pool("common")}
    assert "kaeya_frostgnaw" in ids
    assert "proto_mc_kaeya_frostgnaw" not in ids
    _caches_clear()
