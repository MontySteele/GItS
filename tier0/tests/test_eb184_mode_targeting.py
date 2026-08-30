"""EB-184: A TARGET DEMANDED OF A MODE THAT ATTACKS NOTHING.

Kokomi slice 1 round 4, `t02`. The seat took the *Gain 3 Block* half of
`proto_thoma_crimson_ooyoroi_either` and wrote no target, correctly from the
printed face. The bridge refused -- *"Card requires a target. Provide 'target'
with an entity_id."* -- because the card is typed as an Attack and declares
`TargetType.AnyEnemy`. The line never resolved and the round's pair read
RETURNED the arm on that alone, calling it "an implementation repair, not a
board redesign".

THE CARD TYPE IS THE WRONG WITNESS, AND THE CARD'S TargetType IS NOT A BUG.
The game aims a card BEFORE its mode is chosen: `TargetType` is a property of
the CardModel, the choose-a-card screen opens inside `OnPlay`, and the 0.111.0
decompile has no mid-play enemy picker. So an Attack-typed modal MUST declare
`AnyEnemy` for the sake of the mode that aims. What has to change is who is
ASKED: the chosen MODE, not the card.

THE FIX SPANS BOTH ENGINES, and this file is the seam that reads all of it:

* **the sim** already asks the mode -- `effects._op_choose_one` resolves the
  chosen body and every `target:` in it is that effect's own. The pins below
  are a REGRESSION FENCE around behaviour that was already right, so a future
  card-type shortcut cannot be introduced quietly.
* **codegen** now emits the per-mode answer onto the card
  (`gen_klee_cards.mode_aims` -> `IModalCard.ModeAimsAtChosenEnemy`), because
  the card's own `TargetType` cannot carry it.
* **the bridge** reads those two members by name
  (`vendor/STS2_MCP/gits/GitsModalTargeting.cs`) and derives the refusal from
  the mode the play NAMED, falling back to the card only when no mode was
  named.
* **the harness** names it: `staged_turn.execute_steps` puts the form's
  `choose` on the play step and `scenario._do_play` posts it as `mode`.

Both directions are pinned. A targetless mode must play with no target; an
AIMING mode must still be refused without one.
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import gen_klee_cards as gen                                    # noqa: E402
from tier0.engine import effects                                # noqa: E402
from tier0.engine.state import Card                             # noqa: E402
from tier0.pilot import policy                                  # noqa: E402
from understudy import scenario, staged_turn                    # noqa: E402

MODAL_CS = ROOT / "klee-mod" / "KleeCode" / "Cards" / "ModalChoice.cs"
BRIDGE_CS = ROOT / "vendor" / "STS2_MCP" / "gits" / "GitsModalTargeting.cs"
ACTIONS_CS = ROOT / "vendor" / "STS2_MCP" / "McpMod.Actions.cs"
THOMA_CS = (ROOT / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "Generated" / "ProtoThomaCrimsonOoyoroiEither.cs")

HIT = {"label": "Deal 8 damage",
       "effects": [{"op": "damage", "amount": 8, "target": "enemy"}]}
BLOCK = {"label": "Gain 3 Block",
         "effects": [{"op": "block", "amount": 3}]}
SWEEP = {"label": "Deal 3 damage to ALL enemies",
         "effects": [{"op": "damage", "amount": 3, "target": "all_enemies"}]}


def modal_row(*modes, **overrides):
    """A real Furina row with its effects replaced by one `choose_one`."""
    import copy
    base = next(c for c in gen._sheet_cards(gen.FURINA_PROFILE.sheet)
                if c["id"] == "courtroom_drama")
    card = copy.deepcopy(base)
    for key in ("tags", "sly", "exhaust", "innate", "retain"):
        card.pop(key, None)
    card.update(id="modal_probe", name="Modal Probe", cost=1, type="attack",
                effects=[{"op": "choose_one", "modes": [dict(m)
                                                        for m in modes]}])
    card.update(overrides)
    return card


# --- the sheet reading: which modes aim ------------------------------------

def test_the_aiming_answer_is_per_mode_and_in_sheet_order():
    assert gen.mode_aims(modal_row(HIT, BLOCK)) == [
        ("Deal 8 damage", True), ("Gain 3 Block", False)]


def test_a_mode_that_hits_everything_aims_at_nobody():
    """`all_enemies` resolves itself; only `enemy` asks the player to pick."""
    assert [a for _, a in gen.mode_aims(modal_row(SWEEP, BLOCK))] == [False,
                                                                     False]


def test_a_mode_aims_from_INSIDE_a_branch_too():
    """The same walk the card-level TargetType scan uses (EB-142's lesson):
    an aiming op dereferences the target wherever in the body it sits."""
    buried = {"label": "Maybe hit",
              "effects": [{"op": "conditional", "predicate": "spotlight_moved_this_turn",
                           "then": [{"op": "damage", "amount": 4,
                                     "target": "enemy"}]}]}
    assert [a for _, a in gen.mode_aims(modal_row(buried, BLOCK))] == [True,
                                                                      False]


def test_a_card_with_no_modes_answers_nothing_rather_than_an_empty_list():
    """None, not `[]`, so codegen emits nothing at all for every row the rule
    does not reach and that regen stays a byte comparison."""
    row = modal_row(HIT, BLOCK)
    row["effects"] = [{"op": "damage", "amount": 8, "target": "enemy"}]
    assert gen.mode_aims(row) is None


# --- what the generator puts on the card -----------------------------------

def test_a_modal_card_declares_the_per_mode_answer_and_the_interface():
    src = gen.emit(modal_row(HIT, BLOCK), gen.FURINA_PROFILE)
    assert "IModalCard" in src.split("\n{")[0]
    assert 'new[] { "Deal 8 damage", "Gain 3 Block" }' in src
    assert "public IReadOnlyList<bool> ModeAimsAtChosenEnemy =>" in src
    assert "new[] { true, false }" in src


def test_the_declared_TargetType_still_follows_the_aiming_mode():
    """The card's own aim is unchanged and must be: the game fixes it before
    the mode is chosen. This is the half EB-184 must NOT 'repair'."""
    src = gen.emit(modal_row(HIT, BLOCK), gen.FURINA_PROFILE)
    assert "TargetType.AnyEnemy" in src


def test_a_non_modal_card_declares_neither_row():
    row = modal_row(HIT, BLOCK)
    row["effects"] = [{"op": "damage", "amount": 8, "target": "enemy"}]
    src = gen.emit(row, gen.FURINA_PROFILE)
    assert "ModeAimsAtChosenEnemy" not in src and "IModalCard" not in src


def test_the_card_that_returned_the_arm_carries_the_repair():
    """`proto_thoma_crimson_ooyoroi_either`, the round-4 `t02` card itself:
    mode 1 aims, mode 2 (the Block the seat took) does not."""
    src = THOMA_CS.read_text(encoding="utf-8")
    assert "IModalCard" in src
    assert "new[] { true, false }" in src
    assert 'new[] { "Deal 8 damage, applying its element",' in src


# --- the two C# sources agree on the member names --------------------------

def test_the_interface_declares_exactly_what_the_bridge_reads_by_name():
    """A WIRE CONTRACT across two assemblies that never reference each other:
    the bridge reflects on these members by name, so a rename in either source
    silently restores the defect."""
    iface = MODAL_CS.read_text(encoding="utf-8")
    bridge = BRIDGE_CS.read_text(encoding="utf-8")
    assert "public interface IModalCard" in iface
    assert "IReadOnlyList<string> ModeLabels { get; }" in iface
    assert "IReadOnlyList<bool> ModeAimsAtChosenEnemy { get; }" in iface
    assert 'LabelsMember = "ModeLabels"' in bridge
    assert 'AimsMember = "ModeAimsAtChosenEnemy"' in bridge


def test_the_emitted_members_are_the_ones_the_interface_names():
    src = gen.emit(modal_row(HIT, BLOCK), gen.FURINA_PROFILE)
    for member in re.findall(r"IReadOnlyList<\w+> (\w+) \{ get; \}",
                             MODAL_CS.read_text(encoding="utf-8")):
        assert f"{member} =>" in src


# --- the bridge's refusal, read at the source ------------------------------

def _play_card_source() -> str:
    src = ACTIONS_CS.read_text(encoding="utf-8")
    start = src.index("private static Dictionary<string, object?> ExecutePlayCard")
    end = src.index("private static Dictionary<string, object?> ExecuteEndTurn")
    return src[start:end]


def test_the_bridge_asks_the_named_mode_and_not_only_the_card_type():
    body = _play_card_source()
    assert 'data.TryGetValue("mode"' in body
    assert "GitsModalTargeting.Modes(card)" in body
    assert "modes![modeIndex].Aims" in body


def test_the_bridge_still_refuses_an_aiming_mode_with_no_target():
    """The half that must NOT be weakened: the refusal survives, and it is
    reached from the per-mode answer rather than from the card type."""
    body = _play_card_source()
    refusal = body.index("Card requires a target")
    aims = body.index("bool aims = ")
    assert aims < refusal, "the refusal must be gated on the mode's answer"
    assert "else if (aims)" in body


def test_a_targetless_mode_is_played_at_the_aim_the_game_needs_anyway():
    """The game aims before the mode is chosen, so the play still carries an
    aim -- one the chosen mode discards, and which the response reports."""
    body = _play_card_source()
    assert "combatState.Enemies.FirstOrDefault(c => c.IsAlive)" in body
    assert "inert" in body


# --- the harness names the mode on the play --------------------------------

def _turn():
    return staged_turn.load(ROOT / "understudy" / "turns"
                            / "kokomi-first-turn-example.yaml")


def _form(line):
    return {"turn_id": "t", "packet_sha256": "", "chosen_line": line,
            "grader": {"id": "opus-5", "kind": "llm", "model": "claude-opus-5",
                       "designed_these_cards": False}}


def test_the_play_step_carries_the_chosen_mode():
    steps = staged_turn.execute_steps(
        _turn(), _form([{"card": "Pearl Barrage", "choose": "Gain 3 Block"}]))
    play = next(b for v, b in steps if v == "play")
    assert play == {"card": "Pearl Barrage", "mode": "Gain 3 Block"}


def test_a_play_that_names_no_mode_carries_no_mode_key():
    steps = staged_turn.execute_steps(
        _turn(), _form([{"card": "Pearl Barrage", "target": "Jaw Worm"}]))
    play = next(b for v, b in steps if v == "play")
    assert "mode" not in play


def test_the_mode_and_the_screen_answer_come_from_ONE_form_key():
    """`choose` is read twice -- once onto the play, once onto the screen the
    play opens -- and never written twice."""
    steps = staged_turn.execute_steps(
        _turn(), _form([{"card": "Pearl Barrage", "choose": "Gain 3 Block"}]))
    play = next(b for v, b in steps if v == "play")
    modal = next(b for v, b in steps if v == "answer_modal")
    assert play["mode"] == modal["choose"] == "Gain 3 Block"


# --- and the runner posts it ------------------------------------------------

class _Wire:
    def __init__(self, states):
        self.states = list(states)
        self.posts: list[dict] = []

    def get_state(self):
        return self.states[0] if len(self.states) == 1 else self.states.pop(0)

    def post(self, **action):
        self.posts.append(action)
        return {"status": "ok", "message": "ok"}

    def give_card(self, card_id, count=1, upgraded=False, pile="deck"):
        return {"status": "ok", "message": "queued"}

    def debug_state(self, op, why, amount=0, who="player", resource="",
                    power=""):
        return {"status": "ok", "message": "set", "queued": False}


def _board():
    return {
        "state_type": "monster",
        "battle": {"round": 1, "turn": "player",
                   "enemies": [{"entity_id": "JAW_WORM_0", "name": "Jaw Worm",
                                "hp": 40, "max_hp": 44, "block": 0,
                                "status": []}]},
        "player": {"hp": 70, "max_hp": 70, "block": 0, "energy": 3,
                   "status": [], "resources": {},
                   "hand": [{"id": "KLEEMOD-KABOOM", "name": "Kaboom!",
                             "cost": "1", "can_play": True,
                             "unplayable_reason": None,
                             "description": "Choose one.",
                             "is_upgraded": False,
                             "target_type": "AnyEnemy"}]},
    }


def _run(play_body):
    s = scenario.parse({"name": "t", "character": "KLEEMOD-KLEE",
                        "steps": [{"play": play_body},
                                  {"expect": {"player_block": 0}}]})
    wire = _Wire([_board()])
    runner = scenario.Runner(s, "a test", wire=wire, out=io.StringIO(),
                             sleep=lambda _s: None)
    runner.run()
    return wire.posts


def test_the_runner_posts_the_mode_beside_the_card():
    posts = _run({"card": "Kaboom!", "mode": "Gain 3 Block"})
    assert posts[0] == {"action": "play_card", "card_index": 0,
                        "mode": "Gain 3 Block"}


def test_a_step_with_no_mode_posts_exactly_what_it_always_did():
    posts = _run({"card": "Kaboom!"})
    assert posts[0] == {"action": "play_card", "card_index": 0}


# --- the sim's half: a regression fence around behaviour already right ------

@pytest.fixture
def fixed_index(monkeypatch):
    monkeypatch.setattr(policy, "MODE_CHOOSER_ENABLED", False)


def _card(**kw):
    base = dict(id="t", name="t", cost=1, type="attack")
    base.update(kw)
    return Card(**base)


def test_the_sim_resolves_an_attacks_block_mode_without_aiming(state,
                                                              fixed_index):
    """Mode A is the Block. The card is TYPED an attack and nothing in the
    resolution asks it for a target -- which is the whole of EB-184's claim,
    stated in the engine that already held it."""
    card = _card(effects=[{"op": "choose_one", "modes": [BLOCK, HIT]}])
    hp = state.enemies[0].hp
    effects.resolve_card(state, card)
    assert state.player.block == 3
    assert state.enemies[0].hp == hp


def test_the_sim_still_aims_the_attacking_mode(state, fixed_index):
    """The other direction, and it must not be weakened: the mode that aims
    lands on the enemy."""
    card = _card(effects=[{"op": "choose_one", "modes": [HIT, BLOCK]}])
    hp = state.enemies[0].hp
    effects.resolve_card(state, card)
    assert state.enemies[0].hp == hp - 8
    assert state.player.block == 0
