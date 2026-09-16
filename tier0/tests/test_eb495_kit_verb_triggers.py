"""`EB-495`: the kit-verb / base-game-trigger matrix, PINNED AS IT IS TODAY.

The matrix itself, its reasoning and its seven disagreements live in
`docs/current/atlas/kit-verbs-vs-base-triggers.md`. This file is the half that
fails when a cell moves. It pins the CURRENT answer, not the desired one.

FOUR OF THE CELLS IT PINNED WERE RECORDED DEFECTS -- D1, D2, D3 and D4 in the
atlas, every one of them the sim disagreeing with the game one-sidedly -- and
all four were repaired on 2026-09-16, sim side only. The pins below moved with
them, which is exactly the visible diff this file exists to force: a repair
lands here or it does not land. D5, D6 and D7 remain, D5 and D6 pinned as
absences.

THREE KINDS OF PIN, all labelled where they are used.

  * BEHAVIOURAL, on the real sim. The four sim triggers that read
    "is this an Attack" -- Skittish, Envenom, the shipped Bomb's
    detonate-on-hit, and Shatter -- are called through
    `effects.deal_damage_to_enemy` once per `source` literal and the answer
    asserted. This is the sim column of the matrix, measured rather than read.

  * STRUCTURAL, on the sim's own source. Which `source=` and `powered=` each
    kit verb's ONE call site passes is the whole of its row, and an AST walk
    over `tier0/engine/*.py` is the only way to assert it without standing up
    every arm's fixture. The table below is the matrix's sim column as
    literals.

  * STRUCTURAL, on the mod's C# source. The same question one engine over. The
    mod DLL only executes inside the game, so -- exactly as
    `test_noncard_parity_vectors.py` argues -- what is available is to read the
    call sites. The C# CALL GRAPH half (that `ElementalHit.Deal` reaches
    `CreatureCmd.Damage` and never an `AttackCommand`) is pinned against the
    real assemblies in `klee-mod/KleeTests/KitVerbBaseTriggerPinTests.cs`;
    neither half is load-bearing alone.

WHY A `source` CENSUS AND NOT A LIST OF VERBS. A verb is added by writing one
more `deal_damage_to_enemy(...)` call, and the failure mode this file exists
for is the one Furina's Stage already hit: a new call site that simply OMITS
`powered=` or `element=` and silently takes the default. A census asserts the
whole population, so a new call site fails until somebody decides its cell.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tier0.engine import effects
from tier0.engine.state import Bomb
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "tier0" / "engine"
MOD = REPO / "klee-mod" / "KleeCode"


# ==========================================================================
# BEHAVIOURAL -- the sim's four "is this an Attack" readers
# ==========================================================================

#: Every `source` literal a kit verb mints, and the one the base path mints.
#: Kept as a tuple rather than derived, because "the population is these and
#: no others" is itself the claim `test_the_source_census_is_complete` makes.
KIT_SOURCES = (
    "attack",               # V1  an Attack card's own damage
    "card",                 # V2  a Skill's or Power's damage
    "bomb",                 # V4  shipped Bomb detonation
    "set_off",              # V5  Klee-overhaul explosion, and V6 a Mine
    "bomb_echo",            # V8  Sparks 'n' Splash echo
    "plan",                 # V9  Kokomi planned hit
    "casket",               # V11 Tamakushi Casket strike
    "salon",                # V12 Salon performance
    "salon_final_bow",      # V13 Salon bow / Evoke
    "furina_stage/act",     # V14 Stage act
    "furina_stage/bow",     # V15 Stage bow
    "companion",            # V17 companion / summon pulse
    "burst",                # V17 Sparks 'n' Splash volley
)


def _fresh(**enemy_kwargs):
    enemy = make_enemy(hp=200)
    for key, value in enemy_kwargs.items():
        setattr(enemy, key, value)
    return make_state(enemies=[enemy]), enemy


def test_skittish_answers_any_card_sourced_damage_and_nothing_else():
    """MATRIX T3, the sim column. `SkittishPower` is the only enemy-side
    on-hit power tier0 models at all (atlas sec.2).

    DISAGREEMENT D1, REPAIRED. The gate is now
    `source in effects.CARD_DAMAGE_SOURCES`, the sim's spelling of the game's
    `DamageProps.HasFlag(ValueProp.Move) && ModelSource is CardModel`
    (`SkittishPower.cs:58`): a Skill's damage (`source="card"`) wakes it in
    both engines, and every kit verb still does not, because
    `ElementalHit.Deal` hands the game no `ModelSource` at all. The end-to-end
    half is `test_eb495_d1_skittish_wakes_on_a_skill.py`.
    """
    for source in KIT_SOURCES:
        state, enemy = _fresh(skittish=3)
        effects.deal_damage_to_enemy(state, enemy, 5, source=source)
        assert enemy.skittish_fired is (
            source in effects.CARD_DAMAGE_SOURCES), source


def test_envenom_answers_any_powered_card_hit_and_nothing_else():
    """MATRIX T4, the sim column, and DISAGREEMENT D2, REPAIRED -- the same
    shape as D1 one power over. `EnvenomPower.AfterDamageGiven` asks
    `props.IsPoweredAttack()` (`EnvenomPower.cs:22`), which is `Move` and not
    `Unpowered` and says nothing about `CardType.Attack`, so a Skill's damage
    poisons in the game; `refpowers.envenom_on_hit` returned early on
    `source != "attack"`. It now asks the same two things the game does, and
    `test_eb495_d2_envenom_takes_a_powered_attack.py` is the end-to-end half.
    """
    for source in KIT_SOURCES:
        state, enemy = _fresh()
        state.player.powers["envenom"] = 1
        effects.deal_damage_to_enemy(state, enemy, 5, source=source)
        poisoned = enemy.powers.get("poison", 0) > 0
        assert poisoned is (source in effects.CARD_DAMAGE_SOURCES), source


def test_the_shipped_bomb_detonates_on_an_attack_hit_and_on_nothing_else():
    """MATRIX T5-adjacent, the mod's own reader rather than a base-game one,
    and the one cell where the two engines AGREE about Attack-ness through
    different machinery: `BombPower.AfterDamageReceived` asks for
    `IsPoweredAttack()` AND `cardSource is { Type: CardType.Attack }`
    (`BombPower.cs:643-644`); the sim asks `source == "attack"`."""
    for source in KIT_SOURCES:
        state, enemy = _fresh()
        enemy.bombs.append(Bomb(damage=6))
        before = state.detonations_total
        effects.deal_damage_to_enemy(state, enemy, 5, source=source)
        fired = state.detonations_total > before
        assert fired is (source == "attack"), source


def test_shatter_answers_an_attack_hit_and_nothing_else():
    """The same agreement one power over: `FrozenPower.AfterDamageReceived`
    gates on `CardType.Attack` (`FrozenPower.cs:118`) and the sim on
    `source == "attack"` (`effects.py:1034`)."""
    for source in KIT_SOURCES:
        state, enemy = _fresh(frozen=2)
        effects.deal_damage_to_enemy(state, enemy, 5, source=source)
        shattered = enemy.frozen == 0
        assert shattered is (source == "attack"), source


def test_the_sim_has_no_enemy_side_damage_received_funnel():
    """MATRIX T5/T6, DISAGREEMENTS D5 and D6, pinned as an ABSENCE.

    `refpowers.on_damage_received` reads `state.player`'s powers and is called
    from one site for damage the player received, so no verb can ever wake an
    enemy's Thorns, FlameBarrier, HardenedShell or EmotionChip. Asserting the
    absence is what makes ADDING the funnel a deliberate act: this test fails
    the day somebody gives an enemy Thorns, which is the moment the matrix's
    whole T6 column has to be re-answered.
    """
    src = (ENGINE / "combat.py").read_text(encoding="utf-8")
    calls = re.findall(r"refpowers\.on_damage_received\(\s*state,\s*(\w[\w.]*)",
                       src)
    assert calls == ["state.player"], calls


# ==========================================================================
# STRUCTURAL -- the sim's call-site census
# ==========================================================================

#: `(file, ordinal) -> (source, powered, element)` for EVERY
#: `deal_damage_to_enemy` call in `tier0/engine`, in file order, as the
#: expressions are written. The key is the call's ORDINAL within its file,
#: not its line number: a line number moves under every unrelated edit
#: (main went red on the merge of #549 for exactly that), an ordinal moves
#: only when a call is added, removed or reordered. `None` means the keyword
#: is absent and the signature's default applies (`powered=True`,
#: `element=None`) -- which is exactly the state D3 and D4 are about, so the
#: absence is spelled rather than folded away.
SIM_CALL_SITES = {
    ('companion_hexerei.py', 1): ("'companion'", None, 'None'),
    ('companion_hexerei.py', 2): ("'companion'", None, 'None'),
    ('companion_hexerei.py', 3): ("'companion'", None, "'electro'"),
    ('companion_hexerei.py', 4): ("'companion'", None, 'element'),
    ('effects.py', 1): ("'bomb'", None, 'bomb.element'),
    ('effects.py', 2): ('source', None, 'element'),
    ('effects.py', 3): ("'salon_final_bow'", None, "'hydro'"),
    ('effects.py', 4): ("'companion'", None, "'hydro'"),
    ('effects.py', 5): ("'attack' if card.type == 'attack' else 'card'", None, "'hydro'"),
    ('effects.py', 6): ("'companion'", None, 'None'),
    ('effects.py', 7): ("'salon'", 'False', "'hydro'"),
    ('effects.py', 8): ("'burst'", None, "'pyro'"),
    ('effects.py', 9): ("'companion'", None, "'electro'"),
    ('effects.py', 10): ("'companion'", None, "'hydro'"),
    ('effects.py', 11): ("'companion'", None, 'None'),
    ('effects.py', 12): ("'companion'", None, "'cryo'"),
    ('effects.py', 13): ("'companion'", None, "'electro'"),
    ('effects.py', 14): ("'companion'", None, "'electro'"),
    ('effects.py', 15): ("'companion'", None, 'None'),
    ('effects.py', 16): ("'companion'", None, 'None'),
    ('effects.py', 17): ("'companion'", None, "'geo'"),
    ('effects.py', 18): ("'companion'", None, 'None'),
    ('effects.py', 19): ("'companion'", None, "'electro'"),
    ('effects.py', 20): ("'companion'", None, "'electro'"),
    ('effects.py', 21): ("'companion'", None, "'cryo'"),
    ('effects.py', 22): ("'companion'", None, "'cryo'"),
    ('effects.py', 23): ("'companion'", None, "'hydro'"),
    ('effects.py', 24): ("'companion'", None, "'geo'"),
    ('effects.py', 25): ("'companion'", None, "'hydro'"),
    ('effects.py', 26): ("'companion'", None, "'pyro'"),
    ('effects.py', 27): ("'companion'", None, "'pyro'"),
    ('effects.py', 28): ("'companion'", None, "'pyro'"),
    ('furina_stage.py', 1): ("'furina_stage/bow'", 'False', "'hydro'"),
    ('furina_stage.py', 2): ("'furina_stage/act'", 'False', "'hydro'"),
    ('furina_stage.py', 3): ("'furina_stage/act'", 'False', "'hydro'"),
    ('klee_overhaul.py', 1): ('EXPLOSION_SOURCE', 'False', 'element'),
    ('klee_overhaul.py', 2): ('ECHO_SOURCE', None, "'pyro'"),
    ('kokomi_plan.py', 1): ("'plan'", 'False', "'hydro'"),
    ('kokomi_plan.py', 2): ("'casket'", 'False', "'hydro'"),
}


def _sim_call_sites():
    found = {}
    for path in sorted(ENGINE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else getattr(func, "id", None))
            if name != "deal_damage_to_enemy":
                continue
            kw = {k.arg: ast.unparse(k.value) for k in node.keywords}
            found[(path.name, node.lineno)] = (kw.get("source"),
                                               kw.get("powered"),
                                               kw.get("element"))
    # Re-key by ordinal within the file (line order), see SIM_CALL_SITES.
    ordinal = {}
    keyed = {}
    for (name, _line), flags in sorted(found.items()):
        ordinal[name] = ordinal.get(name, 0) + 1
        keyed[(name, ordinal[name])] = flags
    return keyed


def test_the_source_census_is_complete():
    """Every damage call site in the engine, with the two flags that decide
    its row. A new verb, or an old one whose flags moved, lands here first."""
    assert _sim_call_sites() == SIM_CALL_SITES


def test_every_call_site_names_its_source():
    """No verb may take the `source="card"` default. `"card"` means "a
    non-Attack card's damage" in the matrix, and a verb that silently inherits
    it would read as one."""
    for where, (source, _powered, _element) in _sim_call_sites().items():
        assert source is not None, where


def test_the_sources_the_census_mints_are_the_ones_the_matrix_lists():
    """The literal `source` strings, reconciled with `KIT_SOURCES` above, so
    the behavioural half above cannot silently stop covering a verb."""
    literal = set()
    for source, _p, _e in _sim_call_sites().values():
        for token in re.findall(r"'([^']+)'", source or ""):
            literal.add(token)
    # `EXPLOSION_SOURCE` / `ECHO_SOURCE` are constants, resolved here.
    from tier0.engine import klee_overhaul
    literal.add(klee_overhaul.EXPLOSION_SOURCE)
    literal.add(klee_overhaul.ECHO_SOURCE)
    assert literal == set(KIT_SOURCES)


# ==========================================================================
# STRUCTURAL -- the mod's call-site census (the C# column)
# ==========================================================================

#: `file -> (line of the ElementalHit door, door name, powered argument)` for
#: each of the SHARED VERB HELPERS the matrix names. Companion pulses are not
#: enumerated: `test_no_companion_pulse_takes_the_powered_door` asserts the
#: whole population instead.
CS_VERB_DOORS = {
    # verb, file, the helper that owns it
    "V4 bomb detonation (shipped)":
        ("Powers/BombPower.cs", "ElementalHit.Deal", None),
    "V5 bomb explosion / Set off":
        ("Powers/Prototype/ProtoBombPower.cs",
         "ElementalHit.DealWithoutDealerMods", None),
    "V9 planned hit":
        ("Powers/Prototype/KokomiPlan.cs", "ElementalHit.Deal", "powered: false"),
    "V11 Casket strike":
        ("Relics/TamakushiCasket.cs", "ElementalHit.Deal", None),
    "V12 Salon performance":
        ("Powers/SalonPowers.cs", "ElementalHit.Deal", "powered: false"),
    "V14/V15 Stage act and bow":
        ("Powers/Prototype/FurinaStage.cs", "ElementalHit.Deal",
         "powered: false"),
}


def _cs(rel: str) -> str:
    return (MOD / rel).read_text(encoding="utf-8")


def test_every_named_verb_reaches_its_documented_elemental_door():
    """MATRIX sec.4, the C# column. The door is the cell: `ElementalHit.Deal`
    means `ValueProp.Unpowered` with `dealer: null`, which is the whole of
    "this verb is damage-only to every base-game trigger"."""
    for verb, (rel, door, _powered) in CS_VERB_DOORS.items():
        assert door in _cs(rel), verb


def test_the_three_verbs_that_refuse_the_dealers_terms_still_refuse_them():
    """`EB-343` (R248), `EB-334` (R246) and `EB-588`, pinned as call-site
    text. The Klee arm spells its refusal as a named method instead, which
    `KleeTests` pins structurally; these three spell it as an argument, which
    only a source read can see."""
    for verb, (rel, _door, powered) in CS_VERB_DOORS.items():
        if powered is None:
            continue
        assert powered in _cs(rel), verb


def test_the_stage_refuses_the_dealers_terms_in_both_engines():
    """DISAGREEMENT D3, REPAIRED, and still pinned from both sides in one
    place so a later move on either side has to come here and decide.

    `FurinaStage.Perform` and `.Bow` pass `powered: false` three times; the
    sim's `furina_stage.perform` and `._bow` now pass `powered=False` at the
    same three places, so Furina's Strength and Weak scale a performance in
    neither engine. The behavioural half is
    `test_eb495_d3_a_performance_carries_no_strength.py`."""
    assert _cs("Powers/Prototype/FurinaStage.cs").count("powered: false") == 3

    stage = [flags for (name, _i), flags in sorted(_sim_call_sites().items())
             if name == "furina_stage.py"]
    assert len(stage) == 3, stage
    assert [powered for _s, powered, _e in stage] == ["False"] * 3


def test_crabaletta_carries_hydro_in_both_engines():
    """DISAGREEMENT D4, REPAIRED, the same shape as D3 one argument over. The
    C# act and bow both name `Elements.Element.Hydro`, and the sim's two
    Crabaletta legs now do too, so a Crabaletta hit sets an aura and consumes
    one in both engines. The behavioural half is
    `test_eb495_d4_crabaletta_hits_hydro.py`."""
    cs = _cs("Powers/Prototype/FurinaStage.cs")
    assert cs.count("Elements.Element.Hydro") == 4   # 2 acts, 2 bows

    sites = _sim_call_sites()
    stage = [flags for (name, _i), flags in sorted(sites.items())
             if name == "furina_stage.py"]
    assert len(stage) == 3, stage
    assert [element for _s, _p, element in stage] == ["'hydro'"] * 3


def test_the_one_door_is_unpowered_with_no_dealer_and_no_card_source():
    """THE SINGLE LINE THAT DECIDES 20 OF THE MATRIX'S 24 ROWS
    (`ElementalHit.cs:120`). `Unpowered` kills T3, T4, T6 and T7; `dealer:
    null` kills T4 and T6 a second time; `cardSource: null` kills T8's
    `UnsettlingLamp` leg (disagreement D7)."""
    src = _cs("Powers/ElementalHit.cs")
    body = src[src.index("public static async Task<int> Deal("):]
    body = body[:body.index("public static Task<int> DealWithoutDealerMods")]

    assert "ValueProp.Unpowered" in body
    assert "dealer: null, cardSource: null, cardPlay: null" in body
    # The negative half, and it is the load-bearing one: an AttackCommand here
    # would hand every kit verb `Hook.BeforeAttack` and re-answer T3 and T7.
    assert "DamageCmd" not in body
    assert "AttackCommand" not in body


def test_only_the_set_off_cards_own_hit_is_an_attack():
    """MATRIX V7. `DamageCmd.Attack` appears outside `Cards/` exactly once, in
    `ProtoBombPower.DealCardDamage` -- the printed number a Set-off card owes
    after its explosions, which IS an Attack and takes every T2/T3/T4 trigger.
    A second non-card site would be a new Attack-shaped verb and a new row."""
    sites = []
    for path in sorted(MOD.rglob("*.cs")):
        if "/Cards/" in path.as_posix() or "\\Cards\\" in str(path):
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"await\s+DamageCmd\.Attack\(", line):
                sites.append((path.relative_to(MOD).as_posix(), lineno))
    # The path and the count are the pin; the line number is not (it moved
    # 1315 -> 1386 under an unrelated edit and turned main red on #549).
    assert [path for path, _line in sites] == [
        "Powers/Prototype/ProtoBombPower.cs"]


def test_no_kit_verb_hands_the_game_a_card_source_for_its_debuff():
    """MATRIX T8 / DISAGREEMENT D7. A verb's debuff carries `cardSource: null`
    -- the Plan's, the reaction's and the detonation's alike -- which is what
    keeps `UnsettlingLamp` off it. Pinned so that handing one a cardSource is
    a deliberate re-answer of the T8 column rather than a copy-paste."""
    for rel, needle in (
            ("Powers/Prototype/KokomiPlan.cs",
             "applier: kokomi,\n                cardSource: null"),
            ("Powers/DemolitionPowers.cs",
             "applier: Owner, cardSource: null"),
    ):
        assert needle in _cs(rel), rel


def test_the_mod_ships_no_potion_so_potion_damage_is_not_a_kit_verb():
    """The matrix's one deliberate omission, asserted rather than assumed: all
    three characters return the base game's pool, so there is no kit potion
    verb for any trigger to see."""
    for rel in ("Klee.cs", "Furina.cs", "Kokomi.cs"):
        assert "PotionPool<SilentPotionPool>()" in _cs(rel), rel


# ==========================================================================
# The atlas doc and this file are one deliverable
# ==========================================================================

ATLAS = REPO / "docs" / "current" / "atlas" / "kit-verbs-vs-base-triggers.md"


def test_the_matrix_doc_exists_and_is_indexed():
    assert ATLAS.exists()
    index = (ATLAS.parent / "README.md").read_text(encoding="utf-8")
    assert "kit-verbs-vs-base-triggers.md" in index


def test_the_matrix_doc_answers_every_cell():
    """No cell may read "unknown" -- `EB-495`'s acceptance line. The table is
    24 verb rows by 8 trigger columns; this counts the rows and refuses the
    word."""
    text = ATLAS.read_text(encoding="utf-8")

    # The MATRIX rows, not sec.4's call-site table: sec.4 spells `| V1 | ...`
    # with the id in its own cell, the matrix spells `| V1 Attack-card ...`.
    rows = [ln for ln in text.splitlines()
            if re.match(r"^\| V\d+ [^|]", ln)]
    assert len(rows) == 24, len(rows)
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")][1:]
        assert len(cells) == 8, row
        for cell in cells:
            assert cell, row
            assert "unknown" not in cell.lower(), row
            assert "?" not in cell, row


def test_every_disagreement_has_a_number_and_a_section():
    text = ATLAS.read_text(encoding="utf-8")
    for n in range(1, 8):
        assert f"### D{n} " in text, n
