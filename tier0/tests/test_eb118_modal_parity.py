"""EB-118 sec.5.4: the modal surface across the two engines.

Three questions this file answers and the modal behaviour file does not:
what the GENERATOR emits for a modal row, what it REFUSES, and whether the
C# mirror of the shape constants and the emit row still matches tier0's.

The C# leg's own pins live in klee-mod/KleeTests/ModalChoicePinTests.cs; this
file is the half that reads BOTH sources, because a constant mirrored in two
languages drifts in whichever one the other's tests cannot see.
"""

import copy
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import gen_klee_cards as gen                                   # noqa: E402
from tier0.engine import effects                               # noqa: E402

MODAL_CS = ROOT / "klee-mod" / "KleeCode" / "Cards" / "ModalChoice.cs"


def modal_card(*modes, **overrides):
    """A real Furina row with its effects replaced by one `choose_one`."""
    base = next(c for c in gen._sheet_cards(gen.FURINA_PROFILE.sheet)
                if c["id"] == "courtroom_drama")
    card = copy.deepcopy(base)
    for key in ("tags", "sly", "exhaust", "innate", "retain"):
        card.pop(key, None)
    card.update(id="modal_probe", name="Modal Probe", cost=1, type="skill",
                effects=[{"op": "choose_one", "modes": list(modes)}])
    card.update(overrides)
    return card


ENCORE = {"label": "Gain 2 Encore",
          "effects": [{"op": "gain_encore", "amount": 2}]}
DRAW = {"label": "Spend 2 Encore: draw 2",
        "effects": [{"op": "spend_encore", "amount": 2},
                    {"op": "draw", "amount": 2}]}
HIT = {"label": "Deal 7 damage",
       "effects": [{"op": "damage", "amount": 7, "target": "enemy"}]}


# --- what the generator emits ----------------------------------------------

def test_a_modal_row_generates_rather_than_blocking():
    assert gen.blocked_reason(modal_card(ENCORE, DRAW),
                              gen.FURINA_PROFILE) is None


def test_the_body_routes_through_the_games_own_choice_surface():
    src = gen.emit(modal_card(ENCORE, DRAW), gen.FURINA_PROFILE)
    assert "ModalChoice.SelectMode(choiceContext, Owner, modeOptions)" in src
    assert "ModalChoice.CreateOption<ModalProbeModeA>(Owner)" in src
    assert "ModalChoice.CreateOption<ModalProbeModeB>(Owner)" in src
    assert "if (modeIndex == 0)" in src
    # One class per mode, in the card's own file, off the shared base.
    assert "public sealed class ModalProbeModeA : ModalOptionCard" in src
    assert "public sealed class ModalProbeModeB : ModalOptionCard" in src


def test_the_taken_mode_is_recorded_in_the_generated_body():
    src = gen.emit(modal_card(ENCORE, DRAW), gen.FURINA_PROFILE)
    assert "ModalChoice.RecordChoice(this, modeIndex," in src


def test_the_face_is_ordinary_card_text_no_new_keyword():
    """Rails: a modal card prints a sentence, not a keyword."""
    desc = gen.build_description(modal_card(ENCORE, DRAW))
    assert desc == "Choose one: Gain 2 Encore | Spend 2 Encore: draw 2."
    assert "[gold]" not in desc
    src = gen.emit(modal_card(ENCORE, DRAW), gen.FURINA_PROFILE)
    assert "KleeKeywords" not in src


def test_a_mode_body_spend_emits_the_real_overdraw_call():
    """EB-119, the C# leg of the modal-spend repair.

    The contract's own second mode is `{op: spend_encore, amount: 2}`, and
    this fixture used to substitute `{op: gain_encore, amount: -2}` because
    the generator could not emit a spend inside a mode body. The substitution
    is a DIVERGENCE, not a paraphrase: `FurinaResources.GainEncore` opens
    `if (amount <= 0) return;`, so the mod would have done nothing while the
    sim drained the meter. What must be emitted is the same call a printed
    top-level spend makes -- `SpendEncoreOrHp`, the overdraw primitive, not
    the no-overdraw `SpendEncore`.
    """
    src = gen.emit(modal_card(ENCORE, DRAW), gen.FURINA_PROFILE)
    assert ("await FurinaResources.SpendEncoreOrHp(choiceContext, "
            "Owner.Creature, 2, this);") in src
    assert "GainEncore(Owner.Creature, -2)" not in src


def test_the_mode_body_spend_is_the_top_level_spends_own_call():
    """Structural, not textual: the statement a mode body emits for a spend
    is the statement build_body emits for the same printed effect. One
    pathway, so an overdraw or Fanfare rule can only be changed in one place.
    """
    spend = {"op": "spend_encore", "amount": 2}
    printed = modal_card(ENCORE, DRAW)
    printed["effects"] = [spend]
    top = [ln.strip() for ln in gen.build_body(printed, gen.FURINA_PROFILE)
           if "SpendEncoreOrHp" in ln]
    assert len(top) == 1
    assert top[0] in gen.emit(modal_card(ENCORE, DRAW), gen.FURINA_PROFILE)


def test_a_modal_card_is_aimed_by_its_modes():
    """TargetType is declared before a mode is picked, so an enemy-facing
    mode still has to make the card aimable."""
    src = gen.emit(modal_card(ENCORE, HIT), gen.FURINA_PROFILE)
    assert "TargetType.AnyEnemy" in src


# --- what the generator refuses --------------------------------------------

@pytest.mark.parametrize("modes,expected", [
    ([ENCORE], "at least 2 modes"),
    ([ENCORE, DRAW, ENCORE, DRAW], "at most 3"),
    ([{"label": "", "effects": [{"op": "draw", "amount": 1}]}, DRAW],
     "non-empty label"),
    ([{"label": "a", "effects": []}, DRAW], "non-empty effects list"),
    ([{"label": "a", "effect": [{"op": "draw", "amount": 1}]}, DRAW],
     "mode field(s)"),
    ([{"label": "a", "effects": [{"op": "summon_kurage", "amount": 1}]}, DRAW],
     "inside a mode body"),
    ([{"label": "a", "effects": [{"op": "draw", "amount": "all"}]}, DRAW],
     "must be a literal int"),
])
def test_an_inexpressible_modal_blocks_with_a_reason(modes, expected):
    reason = gen.blocked_reason(modal_card(*modes), gen.FURINA_PROFILE)
    assert reason and expected in reason


@pytest.mark.parametrize("amount", [0, -2])
def test_the_substitution_trick_cannot_be_generated(amount):
    """EB-119. The generator half of the block. `gain_encore: -2` is inert in
    C# and live in the sim, so it may not reach a mode body (or a conditional
    branch) at all -- the sim's loader refuses it on every sheet, and this is
    the same bar on the emit side."""
    mode = {"label": "nope",
            "effects": [{"op": "gain_encore", "amount": amount}]}
    reason = gen.blocked_reason(modal_card(mode, HIT), gen.FURINA_PROFILE)
    assert reason and "must be a positive literal int" in reason


def test_modes_that_would_aim_differently_block():
    away = {"label": "Hit them all",
            "effects": [{"op": "damage", "amount": 3, "target": "all_enemies"}]}
    reason = gen.blocked_reason(modal_card(HIT, away), gen.FURINA_PROFILE)
    assert reason and "disagree on TargetType" in reason


def test_two_modals_on_one_card_block():
    card = modal_card(ENCORE, DRAW)
    card["effects"] = card["effects"] + copy.deepcopy(card["effects"])
    reason = gen.blocked_reason(card, gen.FURINA_PROFILE)
    assert reason and "mode selection collision" in reason


# --- the C# mirror ---------------------------------------------------------

def test_the_generator_mirrors_the_engines_shape_constants():
    assert gen.MODAL_FIELDS == set(effects.MODAL_FIELDS)
    assert gen.MODE_FIELDS == set(effects.MODE_FIELDS)


def test_the_cs_emit_row_mirrors_the_tier0_event():
    """Same event name and same field names in both engines.

    The tier0 side is the literal in `effects._op_choose_one`; the C# side is
    ModalChoice.EventName / EventFields, read out of the source here so a
    rename on either side fails rather than quietly splitting the stream.
    """
    src = MODAL_CS.read_text(encoding="utf-8")
    name = re.search(r'EventName = "([a-z_]+)"', src)
    fields = re.search(r"EventFields = \{([^}]*)\}", src)
    assert name and fields
    assert name.group(1) == "mode_chosen"
    assert re.findall(r'"([a-z]+)"', fields.group(1)) == \
        ["card", "index", "label"]


def test_the_cs_side_reuses_the_base_game_choice_screen():
    """The reason this surface is not an invented prompt, pinned in prose AND
    in the call. The behavioural half is KleeTests' IL pin."""
    src = MODAL_CS.read_text(encoding="utf-8")
    assert "CardSelectCmd.FromChooseACardScreen(" in src
    assert "PlayerChoiceContext" in src


# --- the shipped prototype, as generated -----------------------------------

DEEP_BREATH_CS = (ROOT / "klee-mod" / "KleeCode" / "Cards" / "Furina"
                  / "Generated" / "DeepBreath.cs")


def _deep_breath_cs() -> str:
    return DEEP_BREATH_CS.read_text(encoding="utf-8")


def test_the_prototypes_committed_cs_carries_both_ruled_modes():
    """EB-118 2C, the C# face of `deep_breath`. Read off the COMMITTED file
    rather than a fresh emit, because what ships is the file: `--check` keeps
    the two in step, and this says what the file has to contain."""
    src = _deep_breath_cs()
    assert "ModalChoice.SelectMode(choiceContext, Owner, modeOptions)" in src
    assert "ModalChoice.CreateOption<DeepBreathModeA>(Owner)" in src
    assert "ModalChoice.CreateOption<DeepBreathModeB>(Owner)" in src
    assert "public sealed class DeepBreathModeA : ModalOptionCard" in src
    assert "public sealed class DeepBreathModeB : ModalOptionCard" in src


def test_the_prototypes_mode_1_is_the_body_it_shipped_with():
    """R194's whole reason for this pair: the card players know survives as
    one mode, and in C# that means the two statements the class emitted
    before the conversion, unchanged, under `if (modeIndex == 0)`."""
    mode_1 = _deep_breath_cs().split("if (modeIndex == 0)")[1].split("else")[0]
    assert "await PlayerCmd.GainEnergy(1, Owner);" in mode_1
    assert "FurinaResources.GainEncore(Owner.Creature, 2);" in mode_1


def test_the_prototypes_mode_2_overdraws_through_the_real_primitive():
    """EB-119's repair, on the shipped card rather than on a fixture: mode 2
    calls `SpendEncoreOrHp` -- a thin bank pays TRUE HP -- and not the
    no-overdraw `SpendEncore`, and not a negative `GainEncore`."""
    src = _deep_breath_cs()
    mode_2 = src.split("if (modeIndex == 0)")[1].split("else")[1]
    assert ("await FurinaResources.SpendEncoreOrHp(choiceContext, "
            "Owner.Creature, 2, this);") in mode_2
    assert "await CardPileCmd.Draw(choiceContext, 2m, Owner);" in mode_2
    assert "GainEncore(Owner.Creature, -2)" not in src


def test_the_prototypes_upgrade_is_the_ruled_cost_line():
    """R194 point 6, and contract point 5 in the same assertion: the upgrade
    moves the CARD's cost and no mode body, and the Exhaust keyword the card
    prints survives it."""
    src = _deep_breath_cs()
    assert "EnergyCost.UpgradeBy(-1);" in src
    assert "RemoveKeyword(CardKeyword.Exhaust)" not in src
    assert "CardKeyword.Exhaust" in src          # still printed on the base


def test_the_prototypes_face_prints_the_choice_as_ordinary_text():
    """Rails: "Choose one:" is a sentence, not a keyword. One face, two
    labels, no tooltip and nothing registered."""
    src = _deep_breath_cs()
    assert ('("description", "Choose one: Gain 1 Energy and 2 Encore | '
            'Spend 2 Encore: draw 2."),') in src
    assert "KleeKeywords" not in src
