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

import pytest

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
    "spark_knight",         # V8b R276's Spark Knight, a Power's element-less hit
    "plan",                 # V9  Kokomi planned hit
    # V11, the Tamakushi Casket's strike (`source="casket"`), was retired by
    # the Casket pass (2026-09-28): the relic counts Plans now.
    "salon",                # V12 Salon performance
    "salon_final_bow",      # V13 Salon bow / Evoke
    # V14/V15, the Stage's act and Bow (`furina_stage/act`, `/bow`, `/line`),
    # left with v2 (the Salon's Tab, 2026-10-05): the arm's guests and Powers
    # hit through `furina_tide`'s one door below.
    # The Furina re-founding sim slice (`furina_v2`, sim only): a performer's
    # act or Bow, and Clorinde's while-on-stage line. Kit verbs, not card hits.
    "furina_v2/act",
    "furina_v2/clorinde_line",
    # The Furina research slice (`furina_tide`, sim only): a guest's act or
    # line, Salon's Encore, Endless Waltz and Critics' Darling. Kit verbs.
    "furina_tide/line",
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


def test_the_player_side_funnel_is_still_the_players_alone():
    """MATRIX T5/T6. `refpowers.on_damage_received` is the PLAYER's funnel and
    stays that way: it reads `state.player.powers` and returns early for any
    other target, so the enemy side could not be bolted onto it and was not.
    The enemy's own funnel is `enemy_on_damage_received`, asserted below."""
    src = (ENGINE / "combat.py").read_text(encoding="utf-8")
    calls = re.findall(r"refpowers\.on_damage_received\(\s*state,\s*(\w[\w.]*)",
                       src)
    assert calls == ["state.player"], calls


def test_the_enemy_side_damage_received_funnel_exists_and_has_one_door():
    """MATRIX T5, DISAGREEMENT D5 — REPAIRED, and pinned the way the absence
    used to be: by counting doors.

    This test used to assert that tier0 had NO enemy-side
    `AfterDamageReceived` at all, which was the whole of D5 and D6. It now
    asserts the funnel exists and that exactly ONE site drives it —
    `effects.deal_damage_to_enemy`, the door the atlas's sec.2 names. The
    count is the pin: the game broadcasts the hook from `CreatureCmd.Damage`,
    which `refpowers.unpowered_damage` and the direct-HP paths also mirror,
    and wiring any of those is a second decision with its own cells rather
    than a copy of this one."""
    engine = "".join(path.read_text(encoding="utf-8")
                     for path in sorted(ENGINE.glob("*.py")))
    calls = re.findall(r"\.enemy_on_damage_received\(", engine)
    assert len(calls) == 1, calls
    assert "_refpowers.enemy_on_damage_received(" in (
        ENGINE / "effects.py").read_text(encoding="utf-8")


def test_the_enemy_side_before_damage_funnel_exists_and_has_one_door():
    """MATRIX T6, DISAGREEMENT D6 — REPAIRED, and a SECOND door because the
    game has a second hook. `ThornsPower` is the assembly's only
    `BeforeDamageReceived` override and it fires above Block and above the HP
    loss, so it cannot share the after-hook's entry point: a fully blocked hit
    and a killing blow are both thorned and neither reaches the other funnel.
    One driver, the same door as D5's."""
    engine = "".join(path.read_text(encoding="utf-8")
                     for path in sorted(ENGINE.glob("*.py")))
    assert len(re.findall(r"\.enemy_retaliates_before_the_hit\(", engine)) == 1


@pytest.mark.parametrize("power,amount", [("thorns", 5), ("flame_barrier", 4),
                                          ("curl_up", 14)])
def test_no_kit_verb_wakes_an_enemys_retaliation(power, amount):
    """MATRIX T6, the column as it must stay. All three readers ask
    `IsPoweredAttack()`, which every kit verb fails by construction —
    `ElementalHit.Deal` passes `ValueProp.Unpowered` with `dealer: null`. The
    end-to-end half is `test_eb495_d6_an_enemy_can_retaliate.py`; this is the
    whole-population sweep beside the other three behavioural pins above."""
    for source in KIT_SOURCES:
        state, enemy = _fresh()
        enemy.powers[power] = amount
        state.card_in_flight = "pin_card"
        hp = state.player.hp
        effects.deal_damage_to_enemy(state, enemy, 5, source=source)
        fired = (state.player.hp != hp) or enemy.curl_up_card is not None
        assert fired is (source in effects.CARD_DAMAGE_SOURCES), (power, source)


def test_the_hp_loss_cap_runs_at_the_one_place_the_game_runs_it():
    """MATRIX T5, D5's other half. `HardenedShellPower` is the assembly's only
    `ModifyHpLostBeforeOstyLate` override, and the game applies that hook to
    `max(modifiedAmount - blocked, 0)` — after Block, before HP. Both sim
    reads sit in `deal_damage_to_enemy`: the real hit and the amp
    counterfactual, which has to see the same clamp or it credits the
    amplifier with damage the shell refused."""
    src = (ENGINE / "effects.py").read_text(encoding="utf-8")
    assert src.count("enemy_hardened_shell_cap(enemy,") == 2


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
    ('companion_hexerei.py', 2): ("'companion'", None, "'electro'"),
    ('companion_hexerei.py', 3): ("'companion'", None, 'element'),
    ('effects.py', 1): ("'bomb'", None, 'bomb.element'),
    ('effects.py', 2): ('source', None, 'element'),
    ('effects.py', 3): ("'salon_final_bow'", None, "'hydro'"),
    # The Kurage memory's pulse (a Hydro companion hit) left with the memory
    # rule at legacy cleanup stage 6, and the rows below it moved up one.
    ('effects.py', 4): ("'attack' if card.type == 'attack' else 'card'", None, "'hydro'"),
    # `EB-470` MOVED ONE ROW WITHOUT CHANGING ONE. Lisa's Lightning Rose volley
    # left the end-of-turn block for the start-of-turn tail, so its Electro
    # entry -- the thirteenth here -- is now the sixth and the seven between
    # rotate down one. The MULTISET is untouched: the same twenty-eight calls
    # with the same source / powered / element triple on every one, which is
    # what this census is about. Nothing here is a flag moving.
    # THE AoE TRIM (2026-10-03): Durin's Principle of Purity's start-of-turn
    # Pyro hit is the fifth (the Mondstadt block), so the rows below it moved
    # down one; Yoimiya's Aurous Blaze answers a Skill play now, the
    # twenty-eighth, in place of its old volley on a non-Attack hit.
    ('effects.py', 5): ("'companion'", None, "'pyro'"),
    ('effects.py', 6): ("'companion'", None, "'electro'"),
    ('effects.py', 7): ("'companion'", None, 'None'),
    ('effects.py', 8): ("'salon'", 'False', "'hydro'"),
    ('effects.py', 9): ("'burst'", None, "'pyro'"),
    ('effects.py', 10): ("'companion'", None, "'electro'"),
    ('effects.py', 11): ("'companion'", None, "'hydro'"),
    ('effects.py', 12): ("'companion'", None, 'None'),
    ('effects.py', 13): ("'companion'", None, "'cryo'"),
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
    # (`furina_stage.py`'s two doors left with v2, the Salon's Tab,
    # 2026-10-05: the arm runs on `furina_tide`'s rules and its one door.)
    # THE FURINA RE-FOUNDING SIM SLICE (`furina_v2`, sim only): Clorinde's
    # line ("whenever you Spend, deal 4 Electro") and the one act door every
    # performer's damage act and Bow uses. Unpowered, as the Stage's acts are;
    # each carries its performer's element (None for the trio).
    ('furina_v2.py', 1): ("'furina_v2/clorinde_line'", 'False', "'electro'"),
    ('furina_v2.py', 2): ("'furina_v2/act'", 'False', 'element'),
    # THE FURINA RESEARCH SLICE (`furina_tide`, sim only): the one unpowered
    # door every guest act and line, and every HP-loop Power, uses.
    ('furina_tide.py', 1): ("'furina_tide/line'", 'False', 'element'),
    ('klee_overhaul.py', 1): ('EXPLOSION_SOURCE', 'False', 'element'),
    # Sparks 'n' Splash, since 2026-09-25 on a Bomb's own terms (the
    # explosion's unpowered door), at the start of the turn.
    ('klee_overhaul.py', 2): ('ECHO_SOURCE', 'False', "'pyro'"),
    # R276's Spark Knight: a Power's hit per Spark gained (not an Attack,
    # Klee's own terms), under its own source. NO ELEMENT since
    # 2026-09-23, so it cannot spend an aura a companion laid down.
    ('klee_overhaul.py', 3): ("'spark_knight'", None, 'None'),
    # Damage Report's hit per status drawn left at the AoE trim (2026-10-03):
    # it gains Block now.
    ('kokomi_plan.py', 1): ("'plan'", 'False', "'hydro'"),
    # POOL COMPLETION (2026-10-01): Sea's Reproach's answer to a Weak or a
    # Vulnerable, dealt as Tidal Riposte's is.
    ('kokomi_plan.py', 2): ("'plan'", 'False', "'hydro'"),
    # Expansion batch one: Tidal Riposte's answer, dealt as a planned hit is.
    ('kokomi_plan.py', 3): ("'plan'", 'False', "'hydro'"),
    # VARKA, THE OATH REWORK (`varka_oath`, no switch). The expansion's
    # (2026-10-01) Cycle of Seasons and Assembly at the Cathedral: a Power's
    # damage, element-less and unpowered.
    ('varka_oath.py', 1): ("'card'", 'False', 'None'),
    ('varka_oath.py', 2): ("'card'", 'False', 'None'),
    # Wildfire Oath (2026-10-03): Pyro's Absolute Zero, a Power's damage per
    # Pyro he applies, element-less and unpowered.
    ('varka_oath.py', 3): ("'card'", 'False', 'None'),
    # The Pyro payout (the one enemy; Wildfire Oath's ALL left with element
    # identities, 2026-10-01) and the Electro payout: element-less,
    # unpowered, his card's (`ElementalHit.DealUnelemented(powered: false)`).
    ('varka_oath.py', 4): ("'card'", 'False', 'None'),
    ('varka_oath.py', 5): ("'card'", 'False', 'None'),
    # The rebalance paper's Absolute Zero (sim only, behind
    # `varka_oath.REBALANCE`): a Power's damage per Weak or Vulnerable he
    # applies, element-less and unpowered.
    ('varka_oath.py', 6): ("'card'", 'False', 'None'),
    # Baron Bunny's next-turn burst: Pyro to ALL, unpowered.
    ('varka_oath.py', 7): ("'card'", 'False', "'pyro'"),
    # Element identities (2026-10-01): Retaliating Tide, a Power's damage at
    # his turn's end, element-less and unpowered.
    ('varka_oath.py', 8): ("'card'", 'False', 'None'),
    # Four Winds' Ascension's and Northwind Avatar's elemental follow-up: a
    # powered hit of the card, carrying his current element.
    ('varka_oath.py', 9): ('source', None, 'led.current'),
    # The expansion's element hits (Cavalry Charge, Blazing Charge,
    # Thundering Verdict, Razor, Tempest): a powered hit of the card,
    # carrying the element the card names.
    ('varka_oath.py', 10): ('source', None, 'element'),
    # Storm Surge's "each enemy it Swirls takes 5 more": element-less, powered.
    ('varka_oath.py', 11): ("'attack' if card.type == 'attack' else 'card'",
                           None, 'None'),
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
    "V12 Salon performance":
        ("Powers/SalonPowers.cs", "ElementalHit.Deal", "powered: false"),
    # The Salon's Tab (2026-10-05): a guest's act and a Power's hit, the
    # board's one door, unpowered either way.
    "V14 Stage guest act":
        ("Powers/Prototype/FurinaStage.cs", "ElementalHit.DealUnelemented",
         "powered: false"),
}


def _cs(rel: str) -> str:
    return (MOD / rel).read_text(encoding="utf-8")


def test_the_stage_refuses_the_dealers_terms_in_both_engines():
    """DISAGREEMENT D3, REPAIRED, and still pinned from both sides in one
    place so a later move on either side has to come here and decide.

    THE SALON'S TAB (2026-10-05). A guest's act and a Power's hit go through
    `GameStageBoard.One`, whose two ElementalHit calls both pass
    `powered: false`, so Furina's Strength and Weak scale a performance in
    neither engine: the sim arm hits through `furina_tide._hit`, the one
    unpowered door. Her Drain goes through the same board as an unblockable,
    unpowered HP loss on herself, not through ElementalHit."""
    cs = _cs("Powers/Prototype/FurinaStage.cs")
    doors = (cs.count("ElementalHit.Deal(")
             + cs.count("ElementalHit.DealUnelemented("))
    assert doors == 2
    assert cs.count("powered: false") == doors
    assert not (MOD / "Powers/Prototype/FurinaStageGuests.cs").exists()

    sites = _sim_call_sites()
    assert not [k for k in sites if k[0] == "furina_stage.py"]
    tide = [flags for (name, _i), flags in sorted(sites.items())
            if name == "furina_tide.py"]
    assert tide == [("'furina_tide/line'", "False", "element")]


def test_a_guest_act_carries_its_element_in_both_engines():
    """THE GUEST CAST's half of draft 3's ruling (a guest on Furina's stage
    carries its element), on the four guests the Salon's Tab keeps
    (2026-10-05): Wriothesley Cryo, Lynette Anemo, Clorinde Electro, and
    Charlotte's act is a Repay, no hit. The board's one door sends
    `Element.None` element-less and a guest's element through
    `ElementalHit.Deal`."""
    director = _cs("Powers/Prototype/FurinaStageDirector.cs")
    for member, nxt, element in (
            ("Wriothesley", "Lynette", "Element.Cryo"),
            ("Lynette", "Clorinde", "Element.Anemo")):
        arm = director[director.index(f"case StagePerformer.{member}:"):
                       director.index(f"case StagePerformer.{nxt}:")]
        assert element in arm, member
    clorinde = director[director.index("case StagePerformer.Clorinde:"):]
    assert "Element.Electro" in clorinde[:300]
    charlotte = director[director.index("case StagePerformer.Charlotte:"):
                         director.index("case StagePerformer.Wriothesley:")]
    assert "Repay(FurinaStageLaw.CharlotteActRepay)" in charlotte
    cs = _cs("Powers/Prototype/FurinaStage.cs")
    one = cs[cs.index("private Task<int> One("):cs.index("public async Task Draw(")]
    assert "element == Element.None" in one
    assert "ElementalHit.DealUnelemented(" in one
    assert "ElementalHit.Deal(" in one


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
    """MATRIX V7. `DamageCmd.Attack` outside `Cards/` is a SHORT, NAMED LIST,
    and each entry is a hit that IS an Attack and therefore takes every
    T2/T3/T4 trigger. Anything else appearing here is a new Attack-shaped verb
    and a new row.

    `ProtoBombPower.DealCardDamage` is the original: the printed number a
    Set-off card owes after its explosions.

    `EB-693` ADDED THE OTHER TWO, and it is a deliberate re-answer of this
    column rather than a copy-paste. `KokomiRules.QuarterMaxHp` and
    `QuarterMaxHpAll` are Sango Isshin's two now-line clauses, and the card's
    own type is `Attack`. They used to go out through `ElementalHit.Deal` --
    the unpowered door -- so the hit took her Strength (hand-rolled by
    `SimDamagePipeline.DealerMods`) and skipped every power that answers an
    attack: the r29 lane-1 seat watched it ignore an Effigy's Slow that Strike
    and Feint both took on the next turn. The D default is one damage kind,
    Attack, with all modifiers, so the two clauses take this door now.

    THE PLANNED HALF IS NOT HERE and must not be: a Plan's carry-out is the
    jellyfish's (`EB-334`, R246 pick 1) and stays an unpowered `ElementalHit`,
    which is what the `Plan` keyword prints."""
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
    # VARKA's Gale Sweep (prototype batch one): one hit per fresh-aura body,
    # each from the card itself -- an Anemo Attack's own hit, so it takes
    # every trigger an Attack takes (`VarkaRules.HitFreshAuras`). And the Oath
    # rework's second hit (Four Winds' Ascension, Northwind Avatar): the
    # card's own hit on its target carrying his current element
    # (`VarkaCards.CurrentElementHit`), an Attack's hit for the same reason.
    # The expansion (2026-10-01) adds `VarkaCards.ElementHit`, the same hit
    # carrying the element the card names (Blazing Charge, Thundering
    # Verdict, Razor, Tempest). The rebalance (2026-10-03) adds Kindled
    # Edge's "deal 7 more": the card's own second hit, with no element.
    assert [path for path, _line in sites] == [
        "Powers/Prototype/ProtoBakeKuragePower.cs",
        "Powers/Prototype/ProtoBakeKuragePower.cs",
        "Powers/Prototype/ProtoBombPower.cs",
        "Powers/Prototype/VarkaOath.cs",
        "Powers/Prototype/VarkaOath.cs",
        "Powers/Prototype/VarkaOath.cs",
        "Powers/Prototype/VarkaRules.cs"]


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
