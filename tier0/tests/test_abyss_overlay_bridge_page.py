"""The Spiral Abyss Blessing screen on the seat bridge (2026-10-12).

The owner asked for the Abyss pick as its own screen before the Ancient's
("All of these options are tiny text on the Ancient screen"). The klee mod now
draws it as a full-screen overlay over the Ancient's room
(`klee-mod/KleeCode/Abyss/AbyssOverlay.cs`) and holds the Ancient's greeting
until it closes. The bridge reads that overlay as its own page and a `choose`
clicks its card (`vendor/STS2_MCP/gits/GitsAbyssOverlay.cs`,
`gits/GitsAbyssPage.cs`; the JSON round trip is pinned in
`klee-mod/KleeTests/AbyssOverlayTests.cs`).

Here: the event state the bridge now sends while the screen is up, read
through the seat's page and grammar; and SOURCE assertions on the bridge's
two edits and on the names the mod and the bridge share (the bridge has no C#
harness of its own). Shape assertions about a bridge: nothing measured here
is quotable.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from understudy import blindplay
from understudy.blindplay_grammar import act

REPO = Path(__file__).resolve().parents[2]
BRIDGE = REPO / "vendor" / "STS2_MCP"
ABYSS = REPO / "klee-mod" / "KleeCode" / "Abyss"

WHISPER = ("The Abyss whispers, urging you deeper. Take one Blessing. "
           "The enemies take one Shadow, at random, from the Blessings you "
           "pass.")

#: Co-op Abyss run, 2026-10-14: the Shadow beside a Blessing read as the one
#: that comes with it, three acts running.
PASS_LINE = "If you pass this, the enemies may take its Shadow:"

CARDS = [
    ("The Ley Line",
     "Each enemy turn, every enemy without an aura takes this act's element. "
     "An enemy wearing an aura deals 1 less damage.",
     "Abyss Mage Shield",
     "Elites enter combat with a shield of this act's element, 8 hits deep, "
     "that stops all damage."),
    ("Moonlit Rest", "Heal 4 HP at the end of each combat.",
     "Sheer Cold", "If you end your turn with no Block, lose 3 HP."),
    ("First Strike", "Your first Attack each combat is played twice.",
     "Riptide", "Whenever an enemy attack deals you unblocked damage, that "
     "enemy gains 1 Strength."),
]


def _screen_state(resolved: bool = False) -> dict:
    """What `BuildEventState` sends with the Blessing screen up: the Ancient's
    room, with `GitsAbyssPage.Apply` laid over it."""
    options = [] if resolved else [
        {"index": i, "title": b,
         "description": f"{bt}\n{PASS_LINE} {s} — {st}",
         "is_locked": False, "is_proceed": False, "was_chosen": False,
         "keywords": []}
        for i, (b, bt, s, st) in enumerate(CARDS)]
    return {"state_type": "event",
            "run": {"act": 1, "floor": 1, "ascension": 0,
                    "modifiers": ["KLEEMOD-SPIRAL_ABYSS"]},
            "player": {"character": "Klee", "hp": 70, "max_hp": 70,
                       "gold": 99, "relics": [], "potions": [], "status": []},
            "event": {"event_id": "NEOW", "event_name": "The Spiral Abyss",
                      "is_ancient": True, "in_dialogue": False,
                      "body": WHISPER, "options": options,
                      "abyss_screen": {
                          "subtitle": "The Spiral Abyss · Act 1",
                          "resolved": resolved,
                          "chosen": "Moonlit Rest" if resolved else None,
                          "result": None, "blessings_taken": [],
                          "shadows_in_force": []}}}


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def test_the_screen_reads_as_its_own_page():
    page = blindplay.observe(_screen_state())
    assert "The Spiral Abyss" in page
    assert WHISPER in page
    for blessing, text, shadow, shadow_text in CARDS:
        assert blessing in page
        assert text in page
        assert f"{PASS_LINE} {shadow}" in page
        assert shadow_text in page
    # Not the Ancient's: no dialogue to advance and nothing of Neow's.
    assert "Neow" not in page


def test_choose_names_a_blessing_and_clicks_its_card():
    res = act(_screen_state(), 'choose "Moonlit Rest"')
    assert res["ok"], res
    assert res["post"] == {"action": "choose_event_option", "index": 1}


def test_bridge_state_ends_with_the_screen():
    builder = (BRIDGE / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    start = builder.index("BuildEventState(EventRoom eventRoom, RunState runState)")
    end = builder.index("\n    private static ", start)
    body = builder[start:end]
    apply_at = body.index("GitsApplyAbyssScreen(state, uiRoom);")
    assert body.index('state["options"] = options;') < apply_at
    assert apply_at < body.index("return state;")
    assert "GItS LOCAL EDIT (the Spiral Abyss Blessing screen" in body


def test_choose_clicks_the_card_before_anything_else():
    actions = (BRIDGE / "McpMod.Actions.cs").read_text(encoding="utf-8")
    start = actions.index("object?> ExecuteChooseEventOption(")
    end = actions.index("\n    private static ", start)
    body = actions[start:end]
    abyss = body.index("GitsChooseAbyssCard(uiRoom, index)")
    assert abyss < body.index("gitsDialogueHitbox")
    assert abyss < body.index("FindAll<NEventOptionButton>(uiRoom)")
    overlay = (BRIDGE / "gits" / "GitsAbyssOverlay.cs").read_text(encoding="utf-8")
    assert "as NClickableControl" in overlay
    assert "card.ForceClick();" in overlay
    assert "GitsAbyssPage.IsOpen(json)" in overlay


def test_the_mod_and_the_bridge_name_the_same_nodes():
    page = (BRIDGE / "gits" / "GitsAbyssPage.cs").read_text(encoding="utf-8")
    view = (ABYSS / "AbyssOverlayView.cs").read_text(encoding="utf-8")
    glue = (ABYSS / "AbyssOverlay.cs").read_text(encoding="utf-8")
    root = re.search(r'RootName = "([^"]+)"', page).group(1)
    assert f'RootName = "{root}"' in view
    meta = re.search(r'MetaKey = "([^"]+)"', page).group(1)
    assert f'PageMeta = "{meta}"' in glue
    assert '$"AbyssCard{index}"' in page
    assert '$"AbyssCard{index}"' in view
    # The card's clickable is the game's, so ForceClick is a click.
    assert "new NClickableControl()" in glue
    assert "OptionButtonClicked(options[index], index)" in glue


def test_the_render_rig_prints_the_models_words():
    rig = (REPO / "tools" / "abyss_overlay_rig" / "godot" / "RigMain.cs").read_text(encoding="utf-8")
    model = (ABYSS / "AbyssOverlayModel.cs").read_text(encoding="utf-8")

    def whisper(text: str) -> str:
        m = re.search(r'Whisper =\s*"([^"]+)"\s*\+\s*"([^"]+)";', text)
        return m.group(1) + m.group(2)

    assert whisper(rig) == whisper(model) == WHISPER
    # The band label (owner, 2026-10-12: "IF PASSED" renamed "SHADOW").
    assert 'ShadowBandLabel = "Shadow"' in rig
    assert 'ShadowBandLabel = "Shadow"' in model
    for path in re.findall(r'"(abyss/(?:relics|powers)/[a-z_]+\.png)"', model):
        assert f'"{path}"' in rig


def test_the_page_says_which_shadow_the_enemies_took():
    """Co-op Abyss run, 2026-10-14: "the page does not say which Shadow
    lands on the enemies". The resolved screen, and the Ancient's page after
    it (`event.abyss_result`, off the room), print the result line."""
    line = "The party chose Overflow. The enemies took Fatui Skirmishers."
    state = _screen_state(resolved=True)
    state["event"]["abyss_screen"]["result"] = line
    assert f"The Spiral Abyss: {line}" in blindplay.observe(state)

    after = _screen_state()
    after["event"].update({"event_name": "Neow", "body": "Neow speaks.",
                           "abyss_result": line})
    del after["event"]["abyss_screen"]
    page = blindplay.observe(after)
    assert f"The Spiral Abyss: {line}" in page

    plain = _screen_state()
    del plain["event"]["abyss_screen"]
    assert "The Spiral Abyss:" not in blindplay.observe(plain)
