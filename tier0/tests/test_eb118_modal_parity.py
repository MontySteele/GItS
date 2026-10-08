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
METER_CS = ROOT / "klee-mod" / "KleeCode" / "Powers" / "MeterCost.cs"


#: Furina's shipped `courtroom_drama` row, spelled inline: the modal probes
#: below were built on it, and the sheet that held it left at legacy cleanup
#: stage 6. Only its frame matters -- the effects are always replaced.
_PROBE_BASE = {
    "id": "courtroom_drama", "name": "Courtroom Drama", "register": "archon",
    "cost": 1, "type": "power", "rarity": "uncommon", "solve": ["utility"],
    "tempo_band": {"fight": ["late"], "run": ["early"]},
    "archetypes": ["generic"], "role": "glue",
    "effects": [{"op": "apply_power", "power": "cross_examination",
                 "amount": 1, "target": "self"}]}


def modal_card(*modes, **overrides):
    """Furina's Courtroom Drama frame with its effects replaced by one
    `choose_one`."""
    base = _PROBE_BASE
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
    # EB-182: this pair PRICES mode 2, so the body asks the selection that
    # offers the affordable modes only. It is the same screen -- the C# pin
    # `ModalChoicePinTests` is what says so structurally.
    assert ("ModalChoice.SelectAffordableMode(choiceContext, Owner, "
            "modeOptions, ModePrices)") in src
    # Round three (Furina, the Stage): `(Owner, this)`. The option face carries
    # the parent's vars now, so it has to carry the parent's upgrade state too.
    assert "ModalChoice.CreateMatchingOption<ModalProbeModeA>(Owner, this)" in src
    assert "ModalChoice.CreateMatchingOption<ModalProbeModeB>(Owner, this)" in src
    assert "if (modeIndex == 0)" in src
    # One class per mode, in the card's own file, off the shared base.
    assert "public sealed class ModalProbeModeA : ModalOptionCard" in src
    assert "public sealed class ModalProbeModeB : ModalOptionCard" in src


def test_an_unpriced_modal_emits_the_body_it_always_emitted():
    """EB-182's regression, at the codegen seam. No mode of this pair opens
    with a spend, so nothing is priced, no `ModePrices` table is declared, no
    `IsPlayable` gate appears, and the selection call is the one that shipped
    before per-option playability existed."""
    src = gen.emit(modal_card(ENCORE, HIT), gen.FURINA_PROFILE)
    assert "ModalChoice.SelectMode(choiceContext, Owner, modeOptions)" in src
    assert "ModePrices" not in src
    assert "IsPlayable" not in src


def test_a_priced_mode_declares_its_price_and_gates_the_card():
    """EB-182, the C# leg of the rule. The price is DATA -- one declaration,
    read by the screen filter and by the card-level gate -- and the bank read
    is the one the paying call gates on, so the price offered and the price
    charged cannot drift.

    EB-220 dropped the emitted bank LAMBDA: a `ModePrice` now names its meter
    and `MeterCost.BankOf` holds one read per meter, the same one the badge
    consults."""
    src = gen.emit(modal_card(ENCORE, DRAW), gen.FURINA_PROFILE)
    assert "internal static readonly ModePrice?[] ModePrices" in src
    assert "new ModePrice(Meter.Encore, 2)" in src
    assert ("protected override bool IsPlayable =>\n"
            "        ModalChoice.AnyAffordable(Owner, ModePrices);") in src
    # Mode 1 prices nothing and says so in the same table, by position.
    assert src.split("ModePrices =")[1].lstrip().startswith("{\n        null,")


def test_a_priced_mode_face_carries_the_shipped_cost_badge():
    """EB-182, the arm this unblocks (Bag of Tricks), generalised by EB-220 to
    every meter. A priced mode's FACE declares `IMeterPricedCard`, which is what
    the shipped METER cost badge reads -- the price lands on the option a player
    is choosing between, in the look that already exists.

    The face declares no number of its own: it READS the card's `ModePrices`
    row, so the badge, the screen filter and the gate share one literal."""
    spend = {"label": "Spend 3 Sparks: deal 12",
             "effects": [{"op": "spend_spark", "amount": 3},
                         {"op": "damage", "amount": 12, "target": "enemy"}]}
    src = gen.emit(modal_card(HIT, spend), gen.FURINA_PROFILE)
    assert "new ModePrice(Meter.Sparks, 3)" in src
    assert ("public sealed class ModalProbeModeB : ModalOptionCard, "
            "IMeterPricedCard") in src
    assert ("public Meter PricedMeter =>\n"
            "        ModalProbe.ModePrices[1]!.Value.Meter;") in src
    assert ("public int PrintedMeterPrice =>\n"
            "        ModalProbe.ModePrices[1]!.Value.Amount;") in src
    # The unpriced mode's face is untouched -- no badge, no interface.
    assert "public sealed class ModalProbeModeA : ModalOptionCard\n" in src


def test_an_encore_priced_mode_face_is_badged_too():
    """EB-220, [USER] 2026-08-30: "Yes, I think Encore and Charge need badges."
    Before it, only a Spark-priced face carried one; an Encore- or Charge-priced
    mode printed its price in the label and nowhere else."""
    src = gen.emit(modal_card(HIT, DRAW), gen.FURINA_PROFILE)
    assert "new ModePrice(Meter.Encore, 2)" in src
    assert ("public sealed class ModalProbeModeB : ModalOptionCard, "
            "IMeterPricedCard") in src
    assert ("public Meter PricedMeter =>\n"
            "        ModalProbe.ModePrices[1]!.Value.Meter;") in src


def test_a_state_dependent_mode_price_is_refused_rather_than_emitted():
    """EB-182's red case, and the guard it LEANS ON rather than adds. The
    price reaches C# as a literal (`ModePrices`), so a formula at the head of
    a mode body would be a number the screen filter could not show before the
    choice -- a row the sim gates per option while the mod offers it whatever
    the bank holds. `_branch_op_reason` already refuses it; this is what makes
    that refusal load-bearing rather than incidental."""
    formula = {"label": "Spend Encore: draw 2",
               "effects": [{"op": "spend_encore",
                            "amount": {"count": "fanfare", "per": 1}},
                           {"op": "draw", "amount": 2}]}
    reason = gen.blocked_reason(modal_card(ENCORE, formula),
                                gen.FURINA_PROFILE)
    assert reason == "branch spend_encore amount must be a literal int"


def test_the_sim_and_the_generator_price_the_same_modes():
    """One rule, two engines: `effects.MODE_PRICE_OPS` names the ops that make
    a mode's cost line, and the generator's table is the same set. A meter
    added to one side and not the other is a mode gated in the sim and offered
    in the mod, which is the drift EB-182 exists to close.

    The generator still prices the shipped Encore and Charge meters, which
    left the sim on 2026-10-08 and print on no current row; those two are the
    only names it may carry that the sim does not (they go with the codegen's
    shipped leftovers, which ride Klee's promotion)."""
    retired = {"spend_encore", "spend_charge"}
    assert set(gen.MODE_PRICE_OPS) - retired == set(effects.MODE_PRICE_OPS)
    for op in effects.MODE_PRICE_OPS:
        # EB-220: the generator's value is now the C# `Meter` member, and the
        # member NAMES are the sim's printed meter names -- the strings both
        # engines put in a refusal line ("needs 3 Sparks, bank holds 2").
        assert effects.MODE_PRICE_OPS[op][1] == gen.MODE_PRICE_OPS[op]


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


def test_an_aimed_mode_beside_an_all_enemies_mode_aims_the_card():
    """AoE trim, 2026-10-03 (Durin: Binary Form). The one legal mixture: the
    card declares AnyEnemy and the all-enemies mode never reads the aim. (It
    was refused before; no other pair of mode TargetTypes is reachable, so the
    refusal stays only as a guard.)"""
    away = {"label": "Hit them all",
            "effects": [{"op": "damage", "amount": 3, "target": "all_enemies"}]}
    assert gen.blocked_reason(modal_card(HIT, away), gen.FURINA_PROFILE) is None


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


# --- EB-150: the mode faces are POOL MEMBERS -------------------------------
#
# [USER], 2026-08-26: "Deep Breath's 'choose one' mechanic doesn't work -
# softlocks the game". The cause is not in any mode body. `CardModel.Pool`
# (decompile, MegaCrit.Sts2.Core.Models/CardModel.cs:297) does NOT return null
# for a card that belongs to no pool -- it falls through to
# `ModelDb.CardPool<MockCardPool>()`, whose `GenerateAllCards` calls
# `NeverEverCallThisOutsideOfTests_ClearOwner()` and throws
# `InvalidOperationException: You monster!`. The throw lands inside
# `NChooseACardSelectionScreen._Ready()` at the first `NCard.Create(card)`,
# which is before `_skipButton`/`_peekButton` are fetched, so the overlay's
# `AfterOverlayShown()` NREs on a null button, the awaited
# `TaskCompletionSource` never completes, and the turn is gone.
#
# THIS IS THE HALF THE LIVE SCENARIO CANNOT RUN ON EVERY COMMIT.
# `understudy/scenarios/deep-breath-modal-choice.yaml` is the live proof and
# it needs the game; this is the structural pin that a mode face emitted
# tomorrow is carried the same way, on a lane that runs in CI.

KLEE_CODE = ROOT / "klee-mod" / "KleeCode"

OPTION_CLASS_RE = re.compile(
    r"public sealed class (\w+)\s*:\s*ModalOptionCard")


def _modal_option_classes_in_tree() -> dict[str, Path]:
    """Every `: ModalOptionCard` class in the shipped C#, by class name."""
    found: dict[str, Path] = {}
    for path in KLEE_CODE.rglob("*.cs"):
        for name in OPTION_CLASS_RE.findall(path.read_text(encoding="utf-8")):
            found[name] = path
    return found


def test_every_mode_face_is_carried_by_a_generated_modal_options_roster():
    # `PrototypeRoster.cs` joins the glob because it is a mode-face carrier
    # too. The quarantined surface (R213 B) has no per-character
    # `<Char>ModalOptions` file -- its whole membership is one generated
    # class, a second file for the same list buying nothing on a surface whose
    # healthy state is empty -- so a modal PROTOTYPE row's faces are emitted
    # into `PrototypeRoster` beside the card that opens the screen. Without
    # this the faces would be genuinely pooled and this test would still call
    # them missing, which is the wrong direction for a soft-lock guard to be
    # wrong in. `tools/lint_pool_membership.py` already reads both files.
    carriers = sorted(KLEE_CODE.rglob("*ModalOptions.cs")) + sorted(
        KLEE_CODE.rglob("PrototypeRoster.cs"))
    rosters = "".join(p.read_text(encoding="utf-8") for p in carriers)
    missing = [name for name in _modal_option_classes_in_tree()
               if f"ModelDb.Card<{name}>()" not in rosters]
    assert not missing, (
        f"mode faces in no ModalOptions roster: {sorted(missing)}. A card in "
        "no pool takes CardModel.Pool through MockCardPool, which throws "
        "inside the choose-a-card screen's _Ready and soft-locks the turn "
        "(EB-150).")


def test_every_modal_options_roster_is_carried_by_a_card_pool():
    """A roster nothing reads is a list, not a membership. The off-pool list
    is what puts the faces into `CardPoolModel.AllCardIds`, which is the only
    thing `CardModel.Pool` looks at."""
    pools = "".join(p.read_text(encoding="utf-8")
                    for p in KLEE_CODE.rglob("*CardPool.cs"))
    rosters = sorted(p.stem for p in KLEE_CODE.rglob("*ModalOptions.cs"))
    assert rosters, "no ModalOptions roster is generated at all"
    orphans = [cls for cls in rosters if f"{cls}.All" not in pools]
    assert not orphans, (
        f"ModalOptions rosters no card pool carries: {orphans} (EB-150)")
