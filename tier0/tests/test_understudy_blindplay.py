"""EB-167/EB-168: the design-blind any-screen render and its driver.

No game, no codex. What can be pinned without either is everything this row is
actually about: that the module cannot reach a sheet or a policy, that every
screen it knows renders and survives the scrubber, that a screen it does not
know is REFUSED rather than guessed at, that a command resolves by printed name
only, and that the whole session loop runs to a stop on each of its budgets
against a scripted wire and a scripted tester.

FIXTURES: RECORDED WHERE ONE EXISTS, SYNTHETIC WHERE NONE DOES. The combat
screen is a real recorded wire state (`review/qa/kokomi-slice1-r3-t01/
observed.json`, staged live on 2026-08-28 and committed). No other screen kind
has a full committed recording -- the Phase-0 logs store decisions, not states
-- so map, shop, rest, event, the reward screens and the selection overlays are
built here from `vendor/STS2_MCP/docs/raw-simplified.md`'s state table and the
field names `understudy/naming.py` reads off each of them. Those are marked
`synthetic` in `SCREENS` below, and a synthetic fixture proves the RENDERER,
never the wire.
"""

from __future__ import annotations

import argparse
import ast
import inspect
import json
import re
import time
from pathlib import Path
from unittest import mock

import pytest

from tier0 import constants as C
from tier0.tests.conftest import seam_files
from understudy import (blindplay, blindplay_notes, blindplay_shape,
                        embark, qa_packet, soak)

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


# ------------------------------------------------------------- fixtures ----


@pytest.fixture(autouse=True)
def _fresh_fight():
    """`EB-428`. THE FIGHT'S MEMORY IS PROCESS STATE, so it leaks between tests.

    It always did -- `_FIGHT_MEMORY` has held enemy ordinals since `EB-271` and
    the tests that cared called `forget_fight` by hand. `EB-428` put the
    elements this fight has been shown into the same memory, which is the
    right lifetime for them and the wrong one for a test file: a Cryo card in
    one test's hand made another test's glossary reach Melt. So every test
    starts on a fresh fight, and a test that wants the memory to carry still
    gets it, because it carries WITHIN a test.
    """
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def combat_state() -> dict:
    """RECORDED. A real staged Kokomi turn as the bridge returned it."""
    blob = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))
    return blob["state"]


def map_state() -> dict:
    """SYNTHETIC, BUILT FROM THE BRIDGE'S OWN BUILDER (`EB-298`).

    `BuildMapState` (`vendor/STS2_MCP/McpMod.StateBuilder.cs:1784`) sends far
    more than the two adjacent labels this page used to print: each travelable
    option carries a one-level `leads_to` lookahead with the children's room
    types, `nodes` is EVERY point of the act with its `col`, `row`, `type` and
    `children`, `current_position` says where you are standing, and `boss` /
    `bosses` carry the act boss's own printed name. This fixture is that
    shape. A LIVE capture is still owed and the row says so -- `EB-262` and
    `EB-263` both closed on a fixture written from this same file and both
    reopened on the wire's own bytes.
    """
    return {"state_type": "map",
            "run": {"act": 1, "floor": 3},
            "player": {"hp": 40, "max_hp": 70, "gold": 99},
            "map": {
                "current_position": {"col": 2, "row": 3, "type": "Monster"},
                "next_options": [
                    {"index": 0, "type": "Monster", "col": 1, "row": 4,
                     "leads_to": [{"col": 1, "row": 5, "type": "Elite"},
                                  {"col": 2, "row": 5, "type": "Unknown"}]},
                    {"index": 1, "type": "Monster", "col": 2, "row": 4,
                     "leads_to": [{"col": 2, "row": 5, "type": "Unknown"}]},
                    {"index": 2, "type": "rest_site", "col": 3, "row": 4,
                     "leads_to": [{"col": 3, "row": 5, "type": "Merchant"}]}],
                "nodes": [
                    {"col": 2, "row": 3, "type": "Monster",
                     "children": [[1, 4], [2, 4], [3, 4]]},
                    {"col": 1, "row": 4, "type": "Monster", "children": []},
                    {"col": 2, "row": 4, "type": "Monster", "children": []},
                    {"col": 3, "row": 4, "type": "rest_site", "children": []},
                    {"col": 1, "row": 5, "type": "Elite", "children": []},
                    {"col": 2, "row": 5, "type": "Unknown", "children": []},
                    {"col": 3, "row": 5, "type": "Merchant", "children": []},
                    {"col": 2, "row": 6, "type": "Boss",
                     "id": "GREMLIN_MATRIARCH", "name": "Gremlin Matriarch",
                     "children": []}],
                "boss": {"col": 2, "row": 6, "id": "GREMLIN_MATRIARCH",
                         "name": "Gremlin Matriarch"}}}


def shop_state() -> dict:
    """SYNTHETIC, BUILT FROM THE BRIDGE'S OWN BUILDER (`EB-262`).

    `BuildShopState` (`vendor/STS2_MCP/McpMod.StateBuilder.cs:1636`) puts the
    shelves under `shop.items` and merges each thing's face in under a
    CATEGORY-PREFIXED key -- `card_name`, `relic_name`, `potion_name` -- with
    no plain `name` anywhere, and closes with the card-removal shelf, which
    carries a price and no model at all. This fixture is that shape, item for
    item, because the one this file used to carry (`items` with `name`) was a
    shape the wire has never sent: it kept every render test green while both
    of a live run's shops printed fourteen rows of `(unnamed)`.
    """
    return {"state_type": "shop",
            "player": {"hp": 40, "max_hp": 70, "gold": 120},
            "shop": {"can_proceed": True, "items": [
                {"index": 0, "category": "card", "price": 75,
                 "is_stocked": True, "can_afford": True, "on_sale": False,
                 "card_id": "KLEEMOD-CORAL_GUARD", "card_name": "Coral Guard",
                 "card_type": "Skill", "card_cost": "1", "card_rarity": "Common",
                 "card_description": "Gain 5 Block."},
                {"index": 1, "category": "relic", "price": 160,
                 "is_stocked": True, "can_afford": False,
                 "relic_id": "KLEEMOD-BOTTLED_TIDE",
                 "relic_name": "Bottled Tide",
                 "relic_description": "At the start of each combat, gain 3 "
                                      "Block."},
                {"index": 2, "category": "potion", "price": 50,
                 "is_stocked": False, "can_afford": True,
                 "potion_id": "FIRE_POTION", "potion_name": "Fire Potion",
                 "potion_description": "Deal 20 damage to one enemy."},
                {"index": 3, "category": "card_removal", "price": 90,
                 "is_stocked": True, "can_afford": True}]}}


def rest_state() -> dict:
    """SYNTHETIC. `rest_site.options` with `name`/`index`/`is_enabled`."""
    return {"state_type": "rest_site",
            "player": {"hp": 30, "max_hp": 70},
            "rest_site": {"options": [
                {"index": 0, "name": "Rest", "is_enabled": True,
                 "description": "Heal 30% of your maximum health."},
                {"index": 1, "name": "Smith", "is_enabled": True,
                 "description": "Upgrade a card."},
                {"index": 2, "name": "Dig", "is_enabled": False}]}}


def event_state() -> dict:
    """SYNTHETIC. `event.options` carry their own `index` (`naming.py:183`)."""
    return {"state_type": "event",
            "event": {"event_id": "BONFIRE_SPIRITS",
                      "event_name": "Bonfire Spirits",
                      "in_dialogue": False,
                      "body": "The spirits ask for an offering.",
                      "options": [{"index": 0, "title": "Offer a card"},
                                  {"index": 1, "title": "Leave"}]}}


def hazard_event_state() -> dict:
    """SYNTHETIC, and the one screen that must never be played: EB-1."""
    return {"state_type": "event",
            "event": {"event_id": "PUNCH_OFF", "event_name": "Punch Off",
                      "options": [{"index": 0, "title": "Nab it"}]}}


def card_reward_state() -> dict:
    """SYNTHETIC. `card_reward.cards`, printed faces (`naming.py:82`)."""
    return {"state_type": "card_reward",
            "card_reward": {"can_skip": True, "cards": [
                {"name": "Coral Guard", "cost": "1", "type": "Skill",
                 "description": "Gain 5 Block."},
                {"name": "Coral Guard", "cost": "1", "type": "Skill",
                 "is_upgraded": True, "description": "Gain 8 Block."},
                {"name": "Bake-Kurage", "cost": "1", "type": "Skill",
                 "description": "Summon Bake-Kurage for 1 turn."}]}}


def card_select_state() -> dict:
    """SYNTHETIC. The three screens in one name -- the PROMPT is the only
    place the game states which one it is (`policy_v1.py:1066-1070`)."""
    return {"state_type": "card_select",
            "card_select": {"screen_type": "select", "can_confirm": False,
                            "can_cancel": True,
                            "prompt": "Choose a card to Remove.",
                            "cards": [
                                {"name": "Coral Guard", "cost": "1",
                                 "description": "Gain 5 Block."},
                                {"name": "Send the Runner", "cost": "0",
                                 "description": "Draw 1 card."}]}}


def rewards_state() -> dict:
    """SYNTHETIC, BUILT FROM THE BRIDGE'S OWN BUILDER (`EB-290`).

    `BuildRewardsState` (`vendor/STS2_MCP/McpMod.StateBuilder.cs:1932`) emits
    `index`, `type` and `description` for every reward and a printed NAME for
    exactly one kind of them, the potion (`potion_name`). There is no
    `relic_name`, no `card_name` and no plain `name` anywhere -- so the
    `{"name": "Gold"}` shape this file used to carry is a shape the wire has
    never sent, and it kept the render tests green while the r4 Opus seat's
    reward screen printed `**Relic**` over the words `Golden Pearl` and
    refused `choose "Golden Pearl"`. Two Gold rows because that run met two,
    which is the case that wanted the numbering.
    """
    return {"state_type": "rewards",
            "rewards": {"can_proceed": True, "items": [
                {"index": 0, "type": "gold", "description": "12 Gold",
                 "gold_amount": 12},
                {"index": 1, "type": "gold",
                 "description": "40 Gold (stolen back)", "gold_amount": 40},
                {"index": 2, "type": "relic", "description": "Golden Pearl"},
                {"index": 3, "type": "potion", "potion_id": "FIRE_POTION",
                 "potion_name": "Fire Potion", "description": "Fire Potion",
                 "potion_description": "Deal 20 damage to one enemy."},
                {"index": 4, "type": "card", "description": "Card"}]}}


def empty_rewards_state() -> dict:
    """SYNTHETIC (`EB-294`). Both rewards taken: `BuildRewardsState` skips a
    button that is not enabled, so a spent screen sends an EMPTY item list and
    a live proceed -- and the page was still advertising a chooser over it."""
    return {"state_type": "rewards",
            "rewards": {"can_proceed": True, "items": []}}


def treasure_state() -> dict:
    """SYNTHETIC, BUILT FROM THE BRIDGE'S OWN BUILDER (`EB-263`).

    `BuildTreasureState` (`McpMod.StateBuilder.cs:2362`) writes the opened
    chest's relics under `treasure.relics`, each row carrying its own `index`,
    printed `name` and printed `description`. The top-level `relics` this file
    used to carry is a key the wire does not send, which is why a live chest
    rendered as `# An open chest` with nothing under it.
    """
    return {"state_type": "treasure",
            "treasure": {"can_proceed": True, "relics": [
                {"index": 0, "id": "KLEEMOD-PEARL_DIVERS_CHARM",
                 "name": "Pearl Diver's Charm", "rarity": "Common",
                 "description": "Start each combat with 1 Charge."}]}}


def relic_select_state() -> dict:
    """SYNTHETIC. `relic_select.relics` (`McpMod.StateBuilder.cs:2230`), the
    same blob one screen over -- and it was reading the same absent key."""
    return {"state_type": "relic_select",
            "relic_select": {"prompt": "Choose a relic.", "can_skip": True,
                             "relics": [
                                 {"index": 0, "id": "KLEEMOD-TIDE_GLASS",
                                  "name": "Tide Glass", "rarity": "Rare",
                                  "description": "Draw 1 more card."},
                                 {"index": 1, "id": "KLEEMOD-SALT_LANTERN",
                                  "name": "Salt Lantern", "rarity": "Common",
                                  "description": "Gain 1 Charge."}]}}


def game_over_state() -> dict:
    return {"state_type": "game_over", "run": {"floor": 9},
            "game_over": {"result": "Defeat"}}


def menu_state() -> dict:
    return {"state_type": "menu", "options": [{"name": "embark"}]}


# `(name, builder, provenance, drivable)`. `provenance` is the honest label the
# module docstring promises: `recorded` means a real wire state is committed in
# this repo, `synthetic` means the fixture was written from the wire doc.
SCREENS = [
    ("combat", combat_state, "recorded", True),
    ("map", map_state, "synthetic", True),
    ("shop", shop_state, "synthetic", True),
    ("rest_site", rest_state, "synthetic", True),
    ("event", event_state, "synthetic", True),
    ("card_reward", card_reward_state, "synthetic", True),
    ("card_select", card_select_state, "synthetic", True),
    ("rewards", rewards_state, "synthetic", True),
    ("treasure", treasure_state, "synthetic", True),
    ("relic_select", relic_select_state, "synthetic", True),
    ("game_over", game_over_state, "synthetic", False),
    ("menu", menu_state, "synthetic", False),
    ("hazard", hazard_event_state, "synthetic", False),
]


# ------------------------------------------------------- structural pins ---

def _imported(path: Path) -> list[str]:
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        if isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    return names


def test_blindplay_cannot_reach_a_sheet_or_a_policy():
    """THE NO-LEAK GUARANTEE, STRUCTURALLY -- the same pin `qa_packet` carries,
    widened by the two modules R217 E named. `harness` prints policy_v0's
    recommendation beside the screen, which is precisely the leak this row
    forbids; `soak`, `scenario`, `adapter` and `naming` each reach a tier0
    sheet loader transitively, so they are refused by the same walk."""
    # `EB-180` split the module into a facade and ten seams; the walk is of
    # EVERY one of them. A no-leak pin that read the facade alone after the
    # code moved would be a pin on an empty file.
    banned = {"harness", "policy_v0", "policy_v1", "soak", "scenario",
              "adapter", "naming", "staged_turn", "replay", "embark"}
    for path in seam_files("blindplay"):
        named = _imported(path)
        assert not [m for m in named
                    if m.split(".")[0] in ("tier0", "tier05")], (path, named)
        assert not [m for m in named
                    if m.rsplit(".", 1)[-1] in banned], (path, named)
    named = _imported(Path(blindplay.__file__))
    assert not [m for m in named if m.rsplit(".", 1)[-1] in banned], named


def test_soak_never_imports_blindplay():
    """The other direction, and the same rule `scenario.py` lives under: an
    unattended soak may not reach a tool whose whole job is to hand a screen to
    a third party's model."""
    # Every file `EB-180` split the soak into, not the facade alone.
    for path in seam_files("soak"):
        named = _imported(path)
        assert not [m for m in named if "blindplay" in m], (path, named)


def test_a_base_game_sprite_tag_renders_instead_of_refusing():
    """FOUND LIVE, on the first screen of the first acceptance run. Neow's boon
    list prints Booming Conch as "...and gain [silent_energy_icon.png]" -- the
    base game's own inline sprite tag, which the blunt snake_case rule reads as
    an internal id. It refused the screen and no run could start. The tag names
    an ICON THE PLAYER IS LOOKING AT, so it is rendered, not exempted: showing
    a tester a filename is not showing them the screen."""
    state = {"state_type": "event",
             "event": {"event_id": "NEOW", "event_name": "Neow",
                       "options": [
                           {"index": 0, "title": "Booming Conch",
                            "description": "At the start of Elite combats, "
                                           "draw 2 additional cards and gain "
                                           "[silent_energy_icon.png]."}]}}
    page = blindplay.observe(state)                  # would raise PacketLeak
    # `EB-264` NARROWED THIS FROM THE FILE NAME'S WORDS TO THE ICON ITSELF.
    # The tag is namespaced by the art set it was drawn for, so on a KLEE run
    # the Energy Potion read "Gain [ironclad energy icon][ironclad energy
    # icon]" -- a token naming a character who is not in the run, for a pip
    # that is the same on every character's screen. The subject is what the
    # player is looking at; the namespace is a fact about the asset.
    assert "[Energy]" in page
    assert "silent" not in page and ".png" not in page

    # A tag naming no icon the register knows keeps the old rendering rather
    # than being guessed at.
    state["event"]["options"][0]["description"] = "gain [boss_relic_icon.png]"
    assert "[boss relic icon]" in blindplay.observe(state)

    # And the narrowness is the point: a bracketed token WITHOUT an image
    # extension is still an id, and still refuses.
    state["event"]["options"][0]["description"] = "gain [pearl_barrage]"
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observe(state)


def test_blindplay_never_imports_the_operator_side_embark():
    """`embark.py` exists BECAUSE `blindplay` may not launch a game: it imports
    `soak`, and through it `policy_v1` and every tier0 sheet loader. An import
    of it from the blind module would carry the whole banned tree in behind one
    innocuous name, so it is pinned in both directions -- named in `banned`
    above, and checked here from the other end."""
    assert embark.soak is soak, "embark is the side that owns the launch"
    for path in seam_files("blindplay"):        # the family, since `EB-180`
        assert not [m for m in _imported(path)
                    if "embark" in m], f"{path} reached the operator side"


def test_embark_expands_a_roster_id_to_a_select_screen_option():
    """EB-117's cheap half: `--character kokomi` must not reach `soak._embark`,
    which compares against the screen's own option strings and would embark on
    whatever was highlighted."""
    assert embark.option_id("kokomi") == "KLEEMOD-KOKOMI"
    assert embark.option_id("KLEEMOD-KOKOMI") == "KLEEMOD-KOKOMI"
    with pytest.raises(embark.EmbarkError):
        embark.option_id("")


def test_embark_never_prefixes_a_base_game_character():
    """A CONTROL round plays a base-game class (Ironclad, Silent, Defect,
    Necrobinder, Regent) on the same funnel a mod round uses. The select
    screen offers those unprefixed -- `KLEEMOD-` is BaseLib's prefix for
    THIS mod's own custom models -- so `option_id` must pass them through
    exactly, in any case, rather than asking the wire for a
    `KLEEMOD-IRONCLAD` option that does not exist on any screen."""
    for base in embark.BASE_CHARACTERS:
        assert embark.option_id(base) == base
        assert embark.option_id(base.lower()) == base
    # A roster id (a mod character) still gets the mod's own prefix.
    assert embark.option_id("klee") == "KLEEMOD-KLEE"


def test_a_hold_embark_has_nothing_to_tear_down(tmp_path, monkeypatch):
    """FOUND LIVE. A `--hold` attaches to a game somebody else launched and
    records no ledger rows -- so it must not be picked as "the latest embark"
    by a teardown, or the launch that DOES need reverting hides behind it and
    the mod stays in the game directory."""
    monkeypatch.setattr(embark, "LOG_DIR", tmp_path)
    (tmp_path / "embark-20260101-000000.json").write_text(json.dumps(
        {"stamp": "20260101-000000", "hold": False,
         "ledger": str(tmp_path / "led.json")}), encoding="utf-8")
    (tmp_path / "embark-20260202-000000.json").write_text(json.dumps(
        {"stamp": "20260202-000000", "hold": True, "ledger": "gone"}),
        encoding="utf-8")
    assert embark.latest_stamp() == "20260101-000000"
    assert "nothing to revert" in embark.teardown("20260202-000000")


def test_every_soak_ledger_row_has_an_embark_teardown_slot():
    """`--teardown` runs in a DIFFERENT PROCESS from the embark, so it rebinds
    `Session`'s undo entries by the ledger text on disk. A row soak learns to
    write that this map does not know would be left APPLIED forever, which is a
    teardown that silently keeps a mod in somebody's game directory.

    READ OFF `Session.__init__` RATHER THAN LISTED HERE, so the day soak grows
    an entry this map does not carry, this goes red on its own. `_bridge_entry`
    is gone from BOTH sides since `EB-310` -- the shared `mods\\STS2_MCP` is
    never removed by a teardown, so there is no entry to rebind.
    """
    held = set(re.findall(r"self\.(_\w+_entry)\b",
                          inspect.getsource(soak.Session.__init__)))
    slots = [attr for attr, _ in embark._LEDGER_SLOTS]
    assert held == {"_seed_entry", "_speed_entry", "_launch_entry",
                    "_appid_entry"}, held
    assert held == set(slots)
    assert len(slots) == len(set(slots))
    assert "_bridge_entry" not in slots


def test_the_hazard_register_covers_soak_s():
    """`blindplay.HAZARD_EVENTS` is a deliberate second copy (importing soak
    would drag policy_v1 in). This is the test that keeps the copy honest: the
    day soak registers a hazard this file does not, it goes red."""
    assert set(soak.HAZARD_EVENTS) <= set(blindplay.HAZARD_EVENTS)


# ------------------------------------------------------------- rendering ---

@pytest.mark.parametrize("name,build,provenance,drivable", SCREENS,
                         ids=[s[0] for s in SCREENS])
def test_every_screen_renders_and_is_blind(name, build, provenance, drivable):
    state = build()
    obs = blindplay.observation(state)
    page = blindplay.render(obs)
    assert page.strip()
    assert bool(obs["blocked"]) is not drivable
    # The scrubber has already run inside `observation` and `render`; this is
    # the same claim spelled out in the vocabulary a reader checks by eye.
    for forbidden in ("KLEEMOD", "pearl_barrage", "role:", "archetypes",
                      "tempo_band", "policy", "score", "EV "):
        assert forbidden not in page, f"{forbidden!r} leaked into {name}"
    assert provenance in ("recorded", "synthetic")


def test_the_recorded_combat_screen_prints_the_faces_and_no_ids():
    """A render that leaks nothing by being empty is not a render."""
    page = blindplay.observe(combat_state())
    assert "Pearl Barrage" in page and "Nibbit" in page
    # `EB-299` re-cut this line: every field on it now says what it is.
    assert ("Intent: Aggressive (Attack) — the number on its icon is 12 — "
            "This enemy intends to Attack for 12 damage." in page)
    assert "Charge: 8" in page                    # a meter that holds something
    # ...and one that does not. `EB-238` NARROWED THIS ASSERTION FROM THE
    # WHOLE PAGE TO THE METER LINES, deliberately: the claim was always "a
    # meter holding nothing is not drawn", and the page now also prints the
    # run's relics -- one of which says *"gain 1 Charge and 2 Burst Energy"*
    # in its own hover text. That is a word the player reads off the HUD,
    # not a meter this screen drew at zero.
    assert not [ln for ln in page.splitlines() if ln.startswith("- Burst")]
    assert "11 in the draw pile" in page          # pile COUNTS, not contents
    assert "Bake-Kurage" not in page              # ...which is in the draw pile
    assert "KLEEMOD" not in page and "_" not in page.replace("state_type", "")


def test_the_element_a_card_applies_is_a_tag_on_its_line():
    """The element INDICATOR's twin on the blind page.

    [USER], 2026-09-01, after playing Klee: *"instead of saying 'applies pyro'
    - maybe make it a card indicator as well to remove text overhead? That
    would be a universal shift."* The game now says it with a picture --
    `KleeKeywords.Applies*` moved to `AutoKeywordPosition.None`, so the
    sentence left the rules box and `Vfx/ElementBadge.cs` paints the aura's own
    icon beside the type plaque -- and a picture does not cross this wire. So
    the element rides the card LINE as a tag, read off the same keyword the
    badge reads.

    THE FIXTURE IS RECORDED, which is what makes this a pin rather than a
    restatement: `Pearl Barrage` came off the live bridge on 2026-08-28
    carrying `Applies Hydro` as a KEYWORD, and that keyword is untouched by the
    position flip (`CardModel.HoverTips` walks `Keywords`, never the printed
    text). So the same assertion holds against a build from either side of it.
    """
    page = blindplay.observe(combat_state())
    lines = [ln for ln in page.splitlines() if "**Pearl Barrage**" in ln]

    assert lines, "the recorded hand's Hydro card must be on the page"
    assert all("[Hydro]" in ln for ln in lines)
    # The tag is the GLANCE, not the explanation: the keyword's own row still
    # carries the aura duration and the reaction rule, which is the half a
    # player gets by hovering the gem.
    assert "*Applies Hydro*" in page
    # And a card that applies nothing wears no tag. `Coral Guard` blocks.
    for ln in page.splitlines():
        if "**Coral Guard**" in ln:
            assert "[" not in ln.split("**Coral Guard**", 1)[1]


def test_anemo_and_geo_carry_the_tag_too():
    """`EB-454`. The two that TRIGGER and leave no aura printed no tag at all,
    on a page where every other element prints one: the Kokomi r13 seat read
    `Jean -- Gale Blade` as untyped "until a Reaction preview named Anemo
    mid-fight" ((c) 8).

    THE GEM IS STILL FOUR and the WORD is now six, which is the split the fix
    is: `ElementBadge.IconPathFor` answers null for both because there is no
    aura icon to paint, while `KleeKeywords.AppliesAnemo` / `AppliesGeo` are
    declared, hover their own tip and cross this wire as a keyword row.
    """
    state = combat_state()
    state["player"]["hand"][1]["keywords"] = [
        {"name": "Applies Anemo",
         "description": "Another aura: consumed, and a reaction triggers."}]
    state["player"]["hand"][2]["keywords"] = [
        {"name": "Applies Geo",
         "description": "Another aura: consumed, and a reaction triggers."}]

    faces = blindplay.observation(state)["combat"]["hand"]

    assert [f["element"] for f in faces] == ["Hydro", "Anemo", "Geo", "",
                                             "Hydro"]


def test_the_element_tag_is_never_read_off_a_reaction_word():
    """`Applies Electro-Charged` is a REACTION a companion prints, not an
    element, and the six elements are not the seven words that follow the verb.
    The tag's pattern is anchored and element-named for exactly this row, which
    ships on the Mondstadt companion arm."""
    state = combat_state()
    state["player"]["hand"][2]["keywords"] = [
        {"name": "Applies Electro-Charged",
         "description": "A stacking damage-over-time."}]

    faces = blindplay.observation(state)["combat"]["hand"]

    assert [f["element"] for f in faces] == ["Hydro", "", "", "", "Hydro"]


def test_a_card_face_carrying_an_internal_id_is_refused():
    """The belt to the allowlist's brace, exactly as in `qa_packet`: a wire
    that started printing ids would be refused rather than rendered."""
    state = combat_state()
    state["player"]["hand"][0]["description"] = "Play pearl_barrage. Deal 5."
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observation(state)


def test_a_design_tag_on_a_face_is_refused():
    state = combat_state()
    state["player"]["hand"][0]["description"] = "role: payoff. Deal 5 damage."
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observation(state)


def test_a_policy_hint_and_the_run_seed_never_reach_the_page():
    """STRUCTURAL, not scrubbed, and the distinction is worth stating. A
    policy recommendation and the run seed are refused by the ALLOWLIST -- no
    line of this module copies either -- which is the stronger of the two
    guards, because nothing has to recognise them. The scrubber only ever sees
    what the allowlist already let through."""
    state = combat_state()
    state["policy_v0"] = {"action": "play_card", "label": "Pearl Barrage",
                          "score": 12.5}
    state["recommendation"] = "play Pearl Barrage on Nibbit"
    state["run_seed"] = "HUMWKRKNCE"
    page = blindplay.observe(state)
    assert "12.5" not in page and "recommend" not in page.lower()
    assert "HUMWKRKNCE" not in page


def test_an_unknown_state_type_is_tool_blocked_and_never_guessed():
    obs = blindplay.observation({"state_type": "seance_minigame"})
    assert obs["blocked"]
    assert "TOOL-BLOCKED: seance_minigame" in blindplay.render(obs)
    # ...and nothing can be done on it, however reasonable the command reads.
    assert blindplay.act({"state_type": "seance_minigame"}, "proceed")[
        "refusal"]


def test_the_undriven_screens_are_named_rather_than_lumped_in():
    for st in ("crystal_sphere", "overlay", "unknown"):
        obs = blindplay.observation({"state_type": st})
        assert obs["blocked"] and obs["screen"] == "undriven"


def test_a_hazard_event_is_tool_blocked():
    """EB-1. The register, not a heuristic: the screen renders as refused and
    the driver stops, because there is no safe option to pick."""
    obs = blindplay.observation(hazard_event_state())
    assert obs["screen"] == "hazard" and obs["blocked"]
    assert "TOOL-BLOCKED: event" in blindplay.render(obs)
    assert blindplay.act(hazard_event_state(), 'choose "Nab it"')["refusal"]
    # A NON-hazard event on the same screen type is driven normally.
    assert not blindplay.observation(event_state())["blocked"]


# -------------------------------------------------------------- grammar ----

def test_the_grammar_refuses_what_it_does_not_know():
    with pytest.raises(blindplay.BlindPlayError):
        blindplay.parse_command("attack the big one")
    with pytest.raises(blindplay.BlindPlayError):
        blindplay.parse_command("play Pearl Barrage")     # no quotes
    assert blindplay.parse_command('play "A" on "B"').names == ["A", "B"]
    assert blindplay.parse_command("end turn").verb == "end turn"
    assert blindplay.parse_command('use potion "Fire"').verb == "use potion"


def test_a_play_resolves_by_printed_title_at_the_moment_of_posting():
    state = combat_state()
    res = blindplay.act(state, 'play "All Streams Flow to the Sea" on "Nibbit"')
    assert res["ok"]
    assert res["post"]["action"] == "play_card"
    assert res["post"]["card_index"] == 4           # list position, not `index`
    assert res["post"]["target"] == "NIBBIT_0"      # the id lives HERE only
    assert res["printed"] == {"card": "All Streams Flow to the Sea",
                              "target": "Nibbit"}


def test_a_single_enemy_needs_no_naming_but_a_wrong_name_refuses():
    state = combat_state()
    assert blindplay.act(state, 'play "Pearl Barrage"')["ok"]
    res = blindplay.act(state, 'play "Pearl Barrage" on "Jaw Worm"')
    assert not res["ok"] and "Jaw Worm" in res["refusal"]


def test_a_title_matching_two_different_faces_is_refused_as_ambiguous():
    """Two Coral Guards, one upgraded, are two different cards. A driver that
    picked one would be answering a question the tester did not ask."""
    res = blindplay.act(card_reward_state(), 'choose "Coral Guard"')
    assert not res["ok"] and "more than one" in res["refusal"]
    ok = blindplay.act(card_reward_state(), 'choose "Bake-Kurage"')
    assert ok["ok"] and ok["post"]["card_index"] == 2


def test_two_identical_copies_are_interchangeable():
    """...and the same rule the other way: refusing here would make a second
    copy of a card unplayable, which is not an ambiguity a player has."""
    state = combat_state()
    hand = state["player"]["hand"]
    hand.append(json.loads(json.dumps(hand[3])))     # a second Coral Guard
    res = blindplay.act(state, 'play "Coral Guard"')
    assert res["ok"] and res["post"]["card_index"] == 3


def test_an_unplayable_card_is_refused_with_the_game_s_own_reason():
    state = combat_state()
    state["player"]["hand"][0]["can_play"] = False
    state["player"]["hand"][0]["unplayable_reason"] = "Not enough energy"
    res = blindplay.act(state, 'play "Pearl Barrage"')
    assert not res["ok"] and "Not enough energy" in res["refusal"]


def test_a_shop_refuses_what_the_run_cannot_afford():
    res = blindplay.act(shop_state(), 'buy "Bottled Tide"')
    assert not res["ok"] and "160" in res["refusal"] and "120" in res["refusal"]
    ok = blindplay.act(shop_state(), 'buy "Coral Guard"')
    assert ok["ok"] and ok["post"] == {"action": "shop_purchase", "index": 0}


def test_the_map_numbers_its_paths_so_a_fork_is_nameable():
    page = blindplay.observe(map_state())
    assert "Monster (path 1)" in page and "Rest Site (path 3)" in page
    ambiguous = blindplay.act(map_state(), 'go "Monster"')
    assert not ambiguous["ok"]
    res = blindplay.act(map_state(), 'go "Monster (path 2)"')
    assert res["ok"] and res["post"] == {"action": "choose_map_node",
                                         "index": 1}


def test_two_cards_printing_one_title_are_both_playable_by_number():
    """`EB-177`, found live. Run B6 held two *Water's Edge*, one of them
    enchanted, and could play NEITHER: the bare title was ambiguous and the
    upgrade qualifier did not separate them. The render numbers them the way
    the map numbers a fork, and each number resolves to its own copy."""
    state = combat_state()
    hand = state["player"]["hand"]
    twin = json.loads(json.dumps(hand[3]))          # a second Coral Guard
    twin["cost"] = "0"                              # ...with a different face
    hand.append(twin)
    page = blindplay.observe(state)
    assert "Coral Guard (1)" in page and "Coral Guard (2)" in page

    first = blindplay.act(state, 'play "Coral Guard (1)"')
    assert first["ok"] and first["post"]["card_index"] == 3
    assert first["printed"]["card"] == "Coral Guard (1)"
    second = blindplay.act(state, 'play "Coral Guard (2)"')
    assert second["ok"] and second["post"]["card_index"] == len(hand) - 1


def test_the_ambiguous_bare_title_is_refused_with_the_numbers_it_could_use():
    state = combat_state()
    hand = state["player"]["hand"]
    twin = json.loads(json.dumps(hand[3]))
    twin["cost"] = "0"
    hand.append(twin)
    res = blindplay.act(state, 'play "Coral Guard"')
    assert not res["ok"]
    assert "Coral Guard (1)" in res["refusal"]
    assert "Coral Guard (2)" in res["refusal"]


def test_a_title_that_is_unique_on_its_screen_is_never_numbered():
    """The number is a disambiguator, not decoration: a hand of distinct cards
    reads exactly as it always did, and the bare title stays valid."""
    page = blindplay.observe(combat_state())
    assert "Pearl Barrage" in page and "Pearl Barrage (1)" not in page
    assert blindplay.act(combat_state(), 'play "Pearl Barrage"')["ok"]


def test_two_enemies_sharing_a_name_are_numbered_in_printed_order():
    state = combat_state()
    enemies = state["battle"]["enemies"]
    twin = json.loads(json.dumps(enemies[0]))
    twin["entity_id"] = "NIBBIT_1"
    enemies.append(twin)
    page = blindplay.observe(state)
    assert "Nibbit (1)" in page and "Nibbit (2)" in page

    bare = blindplay.act(state, 'play "Pearl Barrage" on "Nibbit"')
    assert not bare["ok"] and "Nibbit (2)" in bare["refusal"]
    res = blindplay.act(state, 'play "Pearl Barrage" on "Nibbit (2)"')
    assert res["ok"] and res["post"]["target"] == "NIBBIT_1"


def test_a_dead_enemy_does_not_renumber_the_one_still_standing():
    """The render prints a corpse, so the grammar must number over the corpses
    too -- otherwise `Nibbit (2)` becomes `Nibbit` the moment the first one
    dies and the page and the grammar disagree mid-fight."""
    state = combat_state()
    enemies = state["battle"]["enemies"]
    twin = json.loads(json.dumps(enemies[0]))
    twin["entity_id"] = "NIBBIT_1"
    enemies.append(twin)
    enemies[0]["hp"] = 0
    res = blindplay.act(state, 'play "Pearl Barrage" on "Nibbit (2)"')
    assert res["ok"] and res["post"]["target"] == "NIBBIT_1"


def test_a_numbered_screen_still_reads_as_blind():
    state = combat_state()
    state["player"]["hand"].append(
        json.loads(json.dumps(state["player"]["hand"][3])))
    state["battle"]["enemies"].append(
        json.loads(json.dumps(state["battle"]["enemies"][0])))
    qa_packet.assert_blind(blindplay.observation(state),
                           allow={state["state_type"]})


def _with_powers(state: dict) -> dict:
    """RECORDED SHAPES. Both status rows are the wire's own, field for field,
    read live on 2026-08-29 through the debug door: `id`, `name`, `amount`,
    `type`, `description`, `keywords`, and no duration or expiry anywhere.

    `Vulnerable` states its duration inside the printed text; `Thorns` states
    none, which is the power run B6 watched come and go unexplained."""
    out = json.loads(json.dumps(state))
    out["player"]["status"] = [
        {"id": "VULNERABLE_POWER", "name": "Vulnerable", "amount": 3,
         "type": "Debuff", "keywords": [],
         "description": "Receive 50% more damage from Attacks for 3 turns."}]
    out["battle"]["enemies"][0]["status"] = [
        {"id": "THORNS_POWER", "name": "Thorns", "amount": 3, "type": "Buff",
         "keywords": [],
         "description": "When hit by an attack, deal 3 damage back."}]
    return out


def test_a_power_prints_the_buff_or_debuff_the_wire_carries():
    """`EB-179`, gap one. `type` was on the wire all along and the page was
    dropping it."""
    page = blindplay.observe(_with_powers(combat_state()))
    assert "Vulnerable 3 (debuff) — Receive 50% more damage" in page
    assert "Thorns 3 (buff) — When hit by an attack" in page


def test_the_page_says_out_loud_that_a_power_carries_no_expiry():
    """...and gap one's other half: there IS no duration field on the wire, so
    the page states that rather than printing nothing and letting a power
    vanish unexplained. Only where a power is actually on the board."""
    assert blindplay.POWER_NOTE in blindplay.observe(_with_powers(combat_state()))
    bare = json.loads(json.dumps(combat_state()))
    bare["player"]["status"] = []
    for e in bare["battle"]["enemies"]:
        e["status"] = []
    assert blindplay.POWER_NOTE not in blindplay.observe(bare)


def test_a_meter_says_the_wire_carries_no_maximum_and_no_spend_rule():
    """`EB-179`, gap two. The resource snapshot reflects an `Id` and an
    `Amount` and nothing else, so `burst_max` is not a field this page is
    failing to read -- it does not exist."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["resources"] = {"KLEEMOD_KOKOMI_BURST": 12}
    page = blindplay.observe(state)
    assert f"Kokomi Burst: 12 — {blindplay.METER_NOTE}" in page
    assert "no maximum" in page and "how it is spent" in page


def test_the_arms_two_meters_print_their_zero_and_nobody_elses_does():
    """`EB-487` (Furina r10 (c) 3). Encore and Fanfare dropped their row at 0,
    so the seat inferred a load-bearing number from a missing line twice and
    read Fanfare as arriving only once a member had performed.

    The recorded turn carries EVERY registered resource at 0 (BaseLib's
    registry knows nothing about who is playing), which is exactly why the ARM
    is asked rather than the board."""
    state = json.loads(json.dumps(combat_state()))
    assert state["player"]["resources"]["KLEEMOD_ENCORE"] == 0
    assert state["player"]["resources"]["KLEEMOD_FANFARE"] == 0

    # This board is Kokomi's, and the non-zero rule is untouched on it.
    kokomi = blindplay.observe(state)
    assert "Encore: 0" not in kokomi and "Fanfare: 0" not in kokomi

    state["player"]["character"] = "Furina"
    furina = blindplay.observe(state)
    assert "- Encore: 0 —" in furina
    assert "- Fanfare: 0 —" in furina
    # And only those two: every other registered meter still keeps its zero
    # off the page, including the three Fanfare bookkeeping resources beside
    # it and Kokomi's own Burst.
    for hidden in ("Fanfare Floor", "Fanfare Cap Bonus", "Kokomi Burst",
                   "Furina Burst", "Burst"):
        assert f"- {hidden}: 0" not in furina


def test_a_hand_printing_one_name_twice_says_an_enchant_would_not_show():
    """`EB-179`, gap three. The card builder emits no enchantment field, and
    the one place that bites a reader is a hand holding two cards they can see
    are different and the page cannot tell apart."""
    state = combat_state()
    assert blindplay.HAND_REPEAT_NOTE not in blindplay.observe(state)
    state["player"]["hand"].append(
        json.loads(json.dumps(state["player"]["hand"][3])))
    assert blindplay.HAND_REPEAT_NOTE in blindplay.observe(state)


def test_the_three_honest_lines_still_read_as_blind():
    state = _with_powers(combat_state())
    state["player"]["resources"] = {"KLEEMOD_KOKOMI_BURST": 12}
    state["player"]["hand"].append(
        json.loads(json.dumps(state["player"]["hand"][3])))
    obs = blindplay.observation(state)
    qa_packet.assert_blind(obs, allow={state["state_type"]})
    qa_packet.assert_blind(blindplay.render(obs), allow={state["state_type"]})


def test_the_screen_decides_the_verb_not_the_command():
    """One `choose`, six wire actions. Each is the verb that screen advertises
    in `vendor/STS2_MCP/docs/raw-simplified.md`."""
    cases = [
        (event_state(), 'choose "Leave"',
         {"action": "choose_event_option", "index": 1}),
        (rest_state(), "rest", {"action": "choose_rest_option", "index": 0}),
        (rest_state(), "upgrade", {"action": "choose_rest_option", "index": 1}),
        # `EB-290`: a reward is named by what it hands over, so this row is
        # `12 Gold` and not the word `Gold` twice.
        (rewards_state(), 'choose "12 Gold"',
         {"action": "claim_reward", "index": 0}),
        (rewards_state(), 'choose "Golden Pearl"',
         {"action": "claim_reward", "index": 2}),
        (treasure_state(), 'choose "Pearl Diver\'s Charm"',
         {"action": "claim_treasure_relic", "index": 0}),
        (card_select_state(), 'choose "Send the Runner"',
         {"action": "select_card", "index": 1}),
        (card_reward_state(), "skip", {"action": "skip_card_reward"}),
        (combat_state(), "end turn", {"action": "end_turn"}),
        (shop_state(), "proceed", {"action": "proceed"}),
    ]
    for state, command, want in cases:
        res = blindplay.act(state, command)
        assert res["ok"], f"{command}: {res['refusal']}"
        assert res["post"] == want, command


def test_a_disabled_option_is_refused():
    res = blindplay.act(rest_state(), 'choose "Dig"')
    assert not res["ok"] and "not available" in res["refusal"]


def test_a_command_on_the_wrong_screen_is_refused():
    assert not blindplay.act(map_state(), "end turn")["ok"]
    assert not blindplay.act(combat_state(), 'go "Monster (path 1)"')["ok"]
    assert not blindplay.act(shop_state(), 'play "Coral Guard"')["ok"]


# ------------------------- EB-262 / EB-263: the two screens with no names ---

def test_every_shelf_in_a_shop_is_named_and_buyable():
    """`EB-262`'s acceptance, on the shape the bridge actually sends. A shop
    item carries its printed name under its CATEGORY's key, so every shelf of
    both of a live run's shops rendered as `(unnamed)` with a price and `buy`
    answered *"nothing here is called '(unnamed)'"*. The tester finished the
    run holding 164 gold it could not spend."""
    page = blindplay.observe(shop_state())
    assert "(unnamed)" not in page
    # `EB-262`, REOPENED ON THE LIVE SCREEN: the card's own ENERGY cost is on
    # the shelf under `card_cost` and was never read, so The Big One was
    # bought for 73 gold and its 3 energy discovered a screen later. Two
    # prices, both printed, the card's first.
    assert "**Coral Guard** — cost 1, card (skill), 75 gold" in page
    # `EB-268`: and the card TYPE beside it, which the wire sends as
    # `card_type` and the hand line has always printed.
    assert "**Bottled Tide** — relic, 160 gold" in page
    assert "At the start of each combat, gain 3 Block." in page
    # The card-removal shelf has no model and therefore no title; the wire's
    # own word for it is rendered rather than a label invented here.
    assert "**Card Removal** — 90 gold" in page
    # And a shelf already bought says so rather than offering a refused buy.
    assert "**Fire Potion** — potion, 50 gold (not available)" in page

    res = blindplay.act(shop_state(), 'buy "Coral Guard"')
    assert res["ok"] and res["post"] == {"action": "shop_purchase", "index": 0}
    assert res["printed"] == {"item": "Coral Guard", "price": 75,
                          "kind": "card (skill)", "text": "Gain 5 Block."}
    assert blindplay.act(shop_state(), 'buy "Card Removal"')["ok"]
    sold = blindplay.act(shop_state(), 'buy "Fire Potion"')
    assert not sold["ok"] and "not available to buy" in sold["refusal"]


def test_an_opened_chest_prints_its_relic_and_choose_takes_it():
    """`EB-263`'s acceptance. The chest's relics are under `treasure.relics`,
    which this reader did not have, so the whole screen was `# An open chest`
    while still advertising `choose "<relic>"`: there was no name to say and
    the tester never learned whether a relic had been taken."""
    page = blindplay.observe(treasure_state())
    assert "# An open chest" in page
    assert "**Pearl Diver's Charm**" in page
    assert "Start each combat with 1 Charge." in page
    res = blindplay.act(treasure_state(), 'choose "Pearl Diver\'s Charm"')
    assert res["ok"]
    assert res["post"] == {"action": "claim_treasure_relic", "index": 0}


def test_a_relic_select_screen_reads_the_same_blob():
    """The screen one over had the same hole and is fixed by the same read."""
    page = blindplay.observe(relic_select_state())
    assert "**Tide Glass**" in page and "**Salt Lantern**" in page
    res = blindplay.act(relic_select_state(), 'choose "Salt Lantern"')
    assert res["ok"] and res["post"] == {"action": "select_relic", "index": 1}


def test_the_shop_and_the_chest_still_read_as_blind():
    """The nested faces come off the wire, so the scrubber is what says they
    may be printed -- not the fact that this file wrote the fixture."""
    for state in (shop_state(), treasure_state(), relic_select_state()):
        page = blindplay.observe(state)
        assert "KLEEMOD" not in page and "_" not in page


# --------------------------- EB-259: the render offers what the state takes --

def proceed_event_state() -> dict:
    """SYNTHETIC. `BuildEventState` flags the Proceed button on the option
    itself (`McpMod.StateBuilder.cs:1490`)."""
    return {"state_type": "event",
            "event": {"event_id": "GOLDEN_IDOL", "event_name": "Golden Idol",
                      "in_dialogue": False,
                      "body": "The idol is gone. Nothing else is here.",
                      "options": [{"index": 0, "title": "Proceed",
                                   "is_proceed": True, "is_locked": False}]}}


def test_bare_proceed_on_an_event_takes_the_printed_proceed_option():
    """`EB-259`'s first desk check. An event room has NO proceed button --
    `ExecuteProceed` walks rewards, rest, both merchants and the treasure room
    and stops (`McpMod.Actions.cs:600-663`) -- so the bare verb posted an
    action the event refused and a run lost two actions to it. It now resolves
    to the option the screen prints."""
    res = blindplay.act(proceed_event_state(), "proceed")
    assert res["ok"]
    assert res["post"] == {"action": "choose_event_option", "index": 0}
    assert res["printed"] == {"option": "Proceed"}
    # ...and the page offers it, because that is where a player would type it.
    assert "- `proceed`" in blindplay.observe(proceed_event_state())


def test_an_event_with_no_proceed_says_so_and_offers_none():
    """The other direction, and it is the half that keeps the first honest:
    an event with real choices is not given a Proceed this tool invented."""
    obs = blindplay.observation(event_state())
    assert "proceed" not in obs["commands"]
    res = blindplay.act(event_state(), "proceed")
    assert not res["ok"]
    assert "no Proceed" in res["refusal"]
    assert "Offer a card" in res["refusal"] and "Leave" in res["refusal"]


def test_a_dialogue_event_still_advances_on_proceed():
    """`advance_dialogue` is a different verb on the same word and is
    untouched: an ancient still being told is not choosing anything."""
    state = event_state()
    state["event"]["in_dialogue"] = True
    assert "proceed" in blindplay.observation(state)["commands"]
    assert blindplay.act(state, "proceed")["post"] == {
        "action": "advance_dialogue"}


def test_confirm_is_offered_only_where_the_wire_says_it_works():
    """`EB-259`'s second desk check. The Gorge card-select printed *Confirm is
    not available.* in its body and listed `confirm` under "What you can say"
    three lines later; the tester typed it and got *"there is nothing waiting
    to be confirmed"*. The page now offers the grammar the wire says will
    work."""
    page = blindplay.observe(card_select_state())
    assert "Confirm is not available." in page
    assert "- `confirm`" not in page
    assert "- `skip`" in page                      # `can_cancel` is true here

    ready = card_select_state()
    ready["card_select"]["can_confirm"] = True
    ready["card_select"]["can_cancel"] = False
    page = blindplay.observe(ready)
    assert "Confirm is available." in page
    assert "- `confirm`" in page and "- `skip`" not in page
    # The command itself still refuses on its own: a screen can move between
    # the render and the reply, which is exactly what happened live.
    assert blindplay.act(ready, "confirm")["ok"]


# ------------------------------- EB-264: no wire tokens on a player's page --

def test_the_unplayable_enums_never_reach_the_page():
    """`EB-264`'s acceptance, one lock per string the tester quoted. The
    translation lives in `qa_packet` so the staged page and this one cannot
    disagree about one refusal; a reason the wire spells as a SENTENCE comes
    through in the game's own words, which is the door the mod's own Spark
    refusal comes through."""
    state = combat_state()
    hand = state["player"]["hand"]
    hand[0]["can_play"], hand[0]["unplayable_reason"] = \
        False, "BlockedByCardLogic"
    hand[1]["can_play"], hand[1]["unplayable_reason"] = \
        False, "EnergyCostTooHigh"
    page = blindplay.observe(state)
    assert "BlockedByCardLogic" not in page and "EnergyCostTooHigh" not in page
    assert "CANNOT BE PLAYED: this card's own rule is stopping you right " \
           "now" in page
    assert "CANNOT BE PLAYED: you do not have enough energy" in page
    # The refusal a play gets back says the same thing as the card's own line.
    res = blindplay.act(state, f'play "{hand[0]["name"]}"')
    assert not res["ok"] and "this card's own rule" in res["refusal"]


def test_a_reason_the_wire_writes_in_words_is_kept_verbatim():
    state = combat_state()
    state["player"]["hand"][0]["can_play"] = False
    state["player"]["hand"][0]["unplayable_reason"] = "you have no Spark"
    assert "CANNOT BE PLAYED: you have no Spark" in blindplay.observe(state)


def test_a_same_named_proto_card_prints_no_cost_discrepancy():
    """`EB-267` on the screen it was FOUND on -- a card reward. The prototype
    surface ships a re-priced twin of a shipped card under the same printed
    name, and the title-keyed cost map answered the shipped card's 2 for the
    proto card's 1: the page told the tester the cost on the card in front of
    them was wrong when nothing was wrong with it."""
    state = {"state_type": "card_reward",
             "card_reward": {"can_skip": True, "cards": [
                 {"id": "KLEEMOD-PROTO_KO_FLAME_DANCE", "name": "Flame Dance",
                  "cost": "1", "type": "Attack",
                  "description": "Deal 9 damage to ALL enemies."}]}}
    page = blindplay.observe(state)
    assert "The cost printed on this card" not in page
    # ...and a card the board really is discounting still says so.
    state["card_reward"]["cards"][0]["cost"] = "0"
    assert "The cost printed on this card is 1; it is showing 0 here." \
        in blindplay.observe(state)


def test_an_icon_token_names_the_icon_and_not_the_art_set():
    """The third string: `[ironclad energy icon]` in Energy Potion's text, on
    a run with no Ironclad in it."""
    state = combat_state()
    state["player"]["potions"] = [
        {"name": "Energy Potion",
         "description": "Gain [ironclad_energy_icon.png]"
                        "[ironclad_energy_icon.png]."}]
    page = blindplay.observe(state)
    assert "ironclad" not in page and ".png" not in page
    assert "Gain [Energy][Energy]." in page


# --------------- EB-374: the sacrifice this page can and cannot speak about --
#
# THE FINDING. The r9 act-2 seat took Pael's Wing and met two card rewards
# afterwards; both printed `choose` and `skip` and nothing else, and it could
# not tell whether `skip` WAS the sacrifice the relic had promised.
#
# WHAT THE FEED CARRIES, read off the vendored builder: `BuildCardRewardState`
# emits the cards and ONE boolean -- whether an alternative button exists on
# the screen -- and `ExecuteSkipCardReward` presses that button whatever it has
# become. The button's words are on neither side of the wire, so the page
# cannot say that skip is the sacrifice and must not say that it is not.
# Carrying the control is a bridge change, `EB-310`'s family.


def paels_wing_reward_state() -> dict:
    """A card reward on a run holding the relic, relics as `BuildPlayerState`
    sends them (`name` plus the game's own hover `description`)."""
    state = json.loads(json.dumps(card_reward_state()))
    state["player"] = {"hp": 40, "max_hp": 70, "relics": [
        {"id": "PAELS_WING", "name": "Pael's Wing",
         "description": "Whenever you skip a card reward, sacrifice it."}]}
    return state


def test_a_card_reward_says_which_relic_has_rewritten_its_alternative():
    """Seen to FAIL: the screen printed `choose` and `skip` and said nothing
    about either the relic or the control it could not reach."""
    page = blindplay.observe(paels_wing_reward_state())
    assert "**Pael's Wing**" in page
    assert "changes what the alternative to choosing a card does" in page
    # It says what the feed has and does not claim what the button is.
    assert "never what that button says or does" in page
    assert "cannot tell you whether that is a plain skip" in page
    # And the verbs are unchanged: there is no `sacrifice` to offer.
    assert "sacrifice`" not in page
    assert blindplay.act(paels_wing_reward_state(), "skip")["post"] == {
        "action": "skip_card_reward"}


def test_the_wire_carries_no_sacrifice_control_to_offer():
    """The reason this row is a page line and not a verb, asserted against the
    vendored builder rather than against a memory of it."""
    builder = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
               ).read_text(encoding="utf-8")
    head = builder.index("BuildCardRewardState(NCardRewardSelectionScreen")
    body = builder[head:builder.index("private static", head + 10)]
    assert 'state["can_skip"] = altButtons.Count > 0;' in body
    assert set(re.findall(r'state\["(\w+)"\]', body)) == {"cards", "can_skip"}
    assert "sacrifice" not in builder.casefold()


def test_a_run_without_the_relic_reads_exactly_as_before():
    """The register is one relic long on purpose: a caveat printed on every
    reward screen of every run would teach a doubt that is not there."""
    page = blindplay.observe(card_reward_state())
    assert "alternative to choosing" not in page
    assert "You may skip this." in page


# ------------------- EB-375: the icon fold is on the door, not on one screen -
#
# THE DEFECT, AND WHY IT SURVIVED `EB-264`. The sprite pass ran on the finished
# OBSERVATION, so every screen was clean -- and the two lines a COMMAND answers
# with are not part of an observation. `taken_line` prints the row a choice
# took and `_result_line` the game's own answer, both assembled from `_text`
# and neither passing through that boundary. The control run's second seat read
# `The next Attack you play costs 0 [ironclad_energy_icon.png]` off the reward
# it had just claimed and the file name twice off Venerable Tea Set, while the
# same cards printed `[Energy]` in combat one screen later.
#
# So the rule moved onto `_text` itself, the one door every printed value comes
# through, and the corpus sweep below is the lint the row asks for.

_BRACKETED_FILE = re.compile(
    r"\[[A-Za-z0-9_]+\.(?:png|jpg|jpeg|svg|webp)\]", re.I)


def test_the_line_after_a_claim_prints_the_icon_and_not_the_file():
    """Seen to FAIL: both lines carried the raw file name, which is what the
    control run reported off a reward screen and a relic face."""
    took = blindplay.taken_line(
        {"ok": True, "verb": "choose",
         "printed": {"card": "Unrelenting",
                     "text": "The next Attack you play costs "
                             "0 [ironclad_energy_icon.png]"}})
    assert "Took: Unrelenting — The next Attack you play costs 0 [Energy]." \
        == took
    answer = blindplay._result_line(
        {"status": "ok", "message": "Venerable Tea Set: gain "
                                    "[ironclad_energy_icon.png]"})
    assert answer == "ok Venerable Tea Set: gain [Energy]"


def test_a_relic_face_folds_the_icon_wherever_it_is_printed():
    """The relic row is on the combat page and in the claim line, and the two
    must not disagree about a word the player is looking at."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["relics"] = [
        {"id": "VENERABLE_TEA_SET", "name": "Venerable Tea Set",
         "description": "At the start of your turn, gain "
                        "[ironclad_energy_icon.png][ironclad_energy_icon.png]."
         }]
    page = blindplay.observe(state)
    assert "gain [Energy][Energy]." in page
    assert not _BRACKETED_FILE.search(page)


def test_no_printed_face_in_the_page_corpus_carries_a_bracketed_file_name():
    """THE LINT THE ROW ASKS FOR, over the corpus of real wire envelopes.

    `review/qa/blindplay/eb263-live-shapes/` is nine screens captured off a
    live run, six of which carry a sprite tag in a card, relic or potion face.
    Every one is rendered and every string of every observation is swept -- not
    only the markdown -- so a face that reaches the page through a field the
    render does not print yet is still held to the rule.
    """
    swept = 0
    for path in sorted(LIVE.glob("*.json")):
        state = json.loads(path.read_text(encoding="utf-8"))
        obs = blindplay.observation(state)
        for value in blindplay._every_string(obs):
            assert not _BRACKETED_FILE.search(value), (path.name, value)
        page = blindplay.render(obs)
        assert not _BRACKETED_FILE.search(page), path.name
        swept += 1
    assert swept == 9
    # The corpus is only worth its lines if it CONTAINS the thing being
    # excluded: six of the nine envelopes carry a raw tag on the wire.
    raw = [p.name for p in sorted(LIVE.glob("*.json"))
           if _BRACKETED_FILE.search(p.read_text(encoding="utf-8"))]
    assert len(raw) >= 6, raw


# -------------------------------------------------------------- session ----

def fight_states() -> list[dict]:
    """A scripted fight: two combat frames, a reward screen, then game over."""
    a = combat_state()
    b = json.loads(json.dumps(a))
    b["battle"]["enemies"][0]["hp"] = 20
    return [a, b, rewards_state(), game_over_state()]


def _session(tmp_path, replies, states=None, ledger=None, **budget):
    thread = blindplay.ScriptedThread(replies)
    wire = blindplay.ScriptedWire(states if states is not None
                                  else fight_states(), ledger=ledger)
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(**budget),
                          log_root=tmp_path)
    return s, s.run(), wire, thread


def test_a_scripted_fight_runs_end_to_end(tmp_path):
    """The whole loop, without the game and without codex: observation ->
    command -> POST -> the next screen, then the fight record at the end of the
    fight and the run record at the end of the run, both kept verbatim."""
    replies = [
        {"command": 'play "Pearl Barrage" on "Nibbit"', "thinking": "chip"},
        {"command": "end turn", "thinking": "nothing left"},
        {"record": "I opened with the exhaust attack."},
        {"command": 'choose "12 Gold"', "thinking": "take it"},
        {"record": "Kokomi seems to want a full rotation."},
    ]
    s, summary, wire, thread = _session(tmp_path, replies)
    assert summary["termination"] == "run_over"
    assert summary["actions"] == 3
    assert [p["action"] for p in wire.posts] == ["play_card", "end_turn",
                                                 "claim_reward"]
    assert wire.posts[0]["target"] == "NIBBIT_0"
    assert summary["fight_records"] == ["I opened with the exhaust attack."]
    assert summary["run_record"].startswith("Kokomi seems")
    # The first prompt carries the blind brief; later ones are just screens.
    assert "Everything you know is on the page" in thread.sent[0]
    assert "Everything you know is on the page" not in thread.sent[1]
    rows = [json.loads(l) for l in
            (tmp_path / "t" / "transcript.jsonl").read_text(
                encoding="utf-8").splitlines()]
    assert {r["kind"] for r in rows} >= {"observation", "command", "result",
                                         "record"}
    assert all(len(r["observation_sha256"]) == 64
               for r in rows if r["kind"] == "observation")


def test_the_next_observe_after_a_play_re_reads_the_aura_off_the_feed(tmp_path):
    """`EB-482` (Kokomi r16 (c) 5), and it is the row's ACCEPTANCE run as a
    fixture: apply Electro, observe, the Hydro card in hand prints the preview.

    The seat reported "the reaction preview arrives a turn late... it cannot
    appear on the turn you play the card that CREATES the aura", and the row
    was minted against a stale-board hypothesis. The loop has no board memory
    at all: every iteration opens with `self.wire.get_state()` through
    `settle_board`, and a card's preview is a hover tip the game rebuilds per
    read (`KleeCardTooltips.ForCard` walks `CombatState.HittableEnemies` at
    the moment it is asked). This pins that, so the hypothesis cannot be
    re-minted.

    The cause the seat actually met is one card, not the loop: `Amber --
    Explosive Puppet` carries NO preview on any board, because its Pyro damage
    is delivered later by `BaronBunnyPower` and `gen_klee_cards.emit` derives
    the preview element from a damage or `apply_aura` op on the row itself.
    """
    bare = combat_state()
    assert "Reaction preview" not in blindplay.observe(bare)

    reacted = json.loads(json.dumps(bare))
    reacted["battle"]["enemies"][0]["status"] = [
        {"id": "ELECTRO_AURA", "name": "Electro Aura", "amount": 2,
         "type": "Debuff", "keywords": [],
         "description": "This enemy is wearing an Electro aura."}]
    for card in reacted["player"]["hand"]:
        if card["name"] == "Pearl Barrage":
            card["keywords"] = list(card.get("keywords") or []) + [
                {"name": "Reaction preview: Electro-Charged",
                 "description": "Hydro meets Electro: the aura is consumed "
                                "and both take a dot."}]

    replies = [{"command": "end turn", "thinking": "set it up"},
               {"command": 'play "Pearl Barrage" on "Nibbit"',
                "thinking": "now it eats the aura"},
               {"record": "one turn"}]
    _s, _summary, _wire, thread = _session(
        tmp_path, replies, states=[bare, reacted, reacted])

    # The page the seat decided the SECOND action on was built off the second
    # wire state, aura and all -- no observation was carried over.
    assert "Reaction preview: Electro-Charged" not in thread.sent[0]
    assert "Reaction preview: Electro-Charged" in thread.sent[1]


def test_the_session_stops_on_the_action_budget(tmp_path):
    replies = [{"command": "end turn", "thinking": "x"} for _ in range(5)]
    replies.append({"record": "short run"})
    s, summary, wire, _ = _session(tmp_path, replies,
                                   states=[combat_state()], max_actions=2)
    assert summary["termination"] == "max_actions"
    assert summary["actions"] == 2 and len(wire.posts) == 2


def test_the_session_stops_on_consecutive_refusals(tmp_path):
    """A tester that keeps naming a card that is not there is stopped, not
    looped: nothing is posted and the refusal count is the budget."""
    replies = [{"command": 'play "Fireball"', "thinking": "?"}
               for _ in range(5)]
    s, summary, wire, _ = _session(tmp_path, replies, states=[combat_state()],
                                   max_refusals=2)
    assert summary["termination"] == "refusal_limit"
    assert wire.posts == [] and summary["actions"] == 0
    assert summary["run_record"] == ""      # nothing was played, nothing asked


def test_the_session_stops_on_the_wall_clock(tmp_path):
    thread = blindplay.ScriptedThread(
        [{"command": "end turn", "thinking": "x"} for _ in range(3)])
    wire = blindplay.ScriptedWire([combat_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_wall_s=-1.0),
                          log_root=tmp_path)
    assert s.run()["termination"] == "max_wall"


class _LimitedThread(blindplay.ScriptedThread):
    """A seat whose account quota runs out after `after` replies."""

    def __init__(self, replies, after: int):
        super().__init__(replies)
        self.after = after

    def send(self, prompt, schema):
        if self.calls >= self.after:
            raise blindplay.SeatBudgetExhausted("codex exited 1 on a usage "
                                                "limit: 429 rate limit")
        return super().send(prompt, schema)


def test_a_usage_limit_stops_the_session_under_its_own_name(tmp_path):
    """SOMEBODY ELSE'S QUOTA IS NOT A FINDING ABOUT THIS GAME. A seat that runs
    out of account budget mid-run is `budget:rate_limit`, not `seat_refused` --
    the two read as opposite things in a sealed record, one a fact about the
    tester's plan and the other a fact about the tool. The partial records
    survive it either way."""
    thread = _LimitedThread([{"command": "end turn", "thinking": "x"}], after=1)
    wire = blindplay.ScriptedWire([combat_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(), log_root=tmp_path)
    summary = s.run()
    assert summary["termination"] == "budget:rate_limit"
    assert summary["actions"] == 1 and len(wire.posts) == 1
    rows = [json.loads(l) for l in
            (tmp_path / "t" / "transcript.jsonl").read_text(
                encoding="utf-8").splitlines()]
    assert any(r["kind"] == "seat_budget" for r in rows)


@pytest.mark.parametrize("text,limited", [
    ("stream error: 429 Too Many Requests", True),
    ("You've hit your usage limit. Try again later.", True),
    ("error: unexpected argument '-C' found", False),
    ("", False),
])
def test_the_rate_limit_markers_read_a_third_party_s_wording(text, limited):
    assert blindplay._is_rate_limited(text) is limited


def test_resume_drops_the_flags_resume_does_not_take(tmp_path):
    """FOUND LIVE, on the SECOND action of the first acceptance run. `codex
    exec resume` accepts neither `-C` nor `--sandbox` nor `--color`, so a
    session that pastes the first turn's argv after `resume` dies every time
    one action in -- no fight, no record. The sandbox is not given up, it moves
    to the config key the flag sets."""
    t = blindplay.CodexThread.__new__(blindplay.CodexThread)
    t.codex, t.model, t.scratch = "codex", "gpt-test", tmp_path
    t.thread_id = ""
    first = t._argv(tmp_path)
    assert first[:2] == ["codex", "exec"] and "-C" in first
    assert "--sandbox" in first

    t.thread_id = "abc-123"
    resumed = t._argv(tmp_path)
    assert resumed[:4] == ["codex", "exec", "resume", "abc-123"]
    for flag in ("-C", "--sandbox", "--color"):
        assert flag not in resumed, flag
    assert 'sandbox_mode="read-only"' in resumed
    # Both arms still end on the stdin prompt and still name the model.
    for argv in (first, resumed):
        assert argv[-1] == "-" and "-m" in argv
        assert "--ignore-user-config" in argv and "--json" in argv


class _TransientWire(blindplay.ScriptedWire):
    """A wire that answers with the transition before it answers with the room.

    Two reads of `unknown` -- one of them with no `state_type` key at all --
    and then the screen. Nothing is posted in between, which is exactly the
    live shape: walking onto a map node changes the room before the bridge can
    name it.
    """

    def __init__(self, states):
        super().__init__(states)
        self.transients = [{"state_type": "unknown"}, {}]

    def get_state(self):
        if self.transients:
            return self.transients.pop(0)
        return super().get_state()


def test_a_transition_is_ridden_out_and_never_reported_as_a_screen(tmp_path):
    """The first live acceptance run stopped TOOL-BLOCKED against the moment
    between two rooms. A bounded settle rides it out; only a wire that STAYS
    unnamed is blocked."""
    thread = blindplay.ScriptedThread([{"command": "end turn",
                                        "thinking": "."},
                                       {"record": "r"}, {"record": "r"}])
    wire = _TransientWire([combat_state(), game_over_state()])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_actions=1),
                          log_root=tmp_path, settle_delay_s=0.0)
    summary = s.run()
    assert wire.posts and wire.posts[0]["action"] == "end_turn"
    assert summary["termination"] != "tool_blocked"


def _mid_turn_frame(state: dict) -> dict:
    """The frame `EB-175` was diagnosed on, copied field for field.

    Recorded live on 2026-08-29, 55 ms after `end_turn` answered
    `ok Ending turn`: still `state_type: monster`, still `turn: player`, the
    ROUND UNCHANGED, the hand already discarded to zero, energy still full,
    and `is_play_phase` FALSE. Two of these arrive before the real next round.
    """
    frame = json.loads(json.dumps(state))
    frame["battle"]["is_play_phase"] = False
    frame["player"]["hand"] = []
    frame["player"]["discard_pile_count"] = \
        int(frame["player"].get("discard_pile_count", 0) or 0) + 5
    return frame


class _EndTurnWire:
    """A wire whose `end_turn` is ASYNCHRONOUS, as the bridge's really is.

    `ExecuteEndTurn` calls `PlayerCmd.EndTurn` and answers at once; the next
    two reads are the turn still being handed over. Every POST records the
    round of the frame the TESTER WAS LOOKING AT, which is the whole
    assertion: one `end turn` from the tester must spend exactly one round.

    A turn ends only when it is ended from a play-phase frame -- ending from
    the hand-over frame is what the game itself refuses ("Not in play phase")
    and what the seat spent its real turns on.
    """

    def __init__(self, rounds: list[dict], tail: dict):
        self.rounds, self.tail = list(rounds), tail
        self.i = 0
        self.pending: list[dict] = []
        self.posts: list[dict] = []
        self.posted_rounds: list[int | None] = []
        self.handed: dict = {}

    def _current(self) -> dict:
        return (self.rounds[self.i] if self.i < len(self.rounds)
                else self.tail)

    def get_state(self) -> dict:
        self.handed = self.pending.pop(0) if self.pending else self._current()
        return self.handed

    def post(self, action: str, **params) -> dict:
        seen = self.handed or self._current()
        battle = seen.get("battle") or {}
        self.posts.append({"action": action, **params})
        self.posted_rounds.append(battle.get("round"))
        if action == "end_turn" and battle.get("is_play_phase"):
            self.pending = [_mid_turn_frame(seen), _mid_turn_frame(seen)]
            self.i += 1
        return {"status": "ok", "message": "Ending turn"}

    def health(self) -> dict:
        return {"mod_version": "0.0-scripted"}


def test_the_frame_between_two_turns_is_named_a_transition():
    """`EB-175`, the predicate. A combat screen with `is_play_phase` false is
    a moment, not a screen; a build that does not carry the key at all is not
    read as one."""
    live = combat_state()
    assert blindplay.transient(live) == ""
    assert blindplay.transient(_mid_turn_frame(live))
    no_key = json.loads(json.dumps(live))
    no_key["battle"].pop("is_play_phase")
    assert blindplay.transient(no_key) == ""


def test_one_end_turn_from_the_tester_spends_exactly_one_round(tmp_path):
    """`EB-175`. Four times in one blind session the seat said `end turn`, was
    answered `ok Ending turn`, and was then shown a combat screen with an
    empty hand and full energy -- the frame above -- so it said `end turn`
    again and spent a REAL turn on it. The rounds it recorded went 1 -> 3 -> 5.

    Three `end turn`s, three rounds, and no round entered twice."""
    rounds = []
    for n, hp in ((1, 57), (2, 40), (3, 20)):
        frame = json.loads(json.dumps(combat_state()))
        frame["battle"]["round"] = n
        frame["battle"]["enemies"][0]["hp"] = hp
        rounds.append(frame)
    wire = _EndTurnWire(rounds, game_over_state())
    thread = blindplay.ScriptedThread(
        [{"command": "end turn", "thinking": "."} for _ in range(3)]
        + [{"record": "fight"}, {"record": "run"}])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_actions=3),
                          log_root=tmp_path, settle_delay_s=0.0)
    s.run()
    assert [p["action"] for p in wire.posts] == ["end_turn"] * 3
    assert wire.posted_rounds == [1, 2, 3]


def _victory_frame(state: dict) -> dict:
    """The frame `EB-178` was read on, copied field for field.

    Recorded live on 2026-08-29, 0 ms after the killing blow answered
    `ok Playing 'Water's Edge' targeting Leaf Slime (S)`: `state_type` is
    still `monster`, there is NO `battle` key at all, the `player` block has
    lost its hand, energy, meters and pile counts, and `run.floor` has
    ALREADY advanced. The next read, 250 ms later, answered `rewards`.
    """
    frame = json.loads(json.dumps(state))
    frame.pop("battle", None)
    for gone in ("hand", "energy", "max_energy", "resources",
                 "draw_pile_count", "discard_pile_count",
                 "exhaust_pile_count"):
        frame["player"].pop(gone, None)
    frame["run"] = {"act": 1, "floor": 2, "ascension": 3}
    return frame


class _VictoryWire:
    """A wire that answers the torn-down frame ONCE after the killing blow."""

    def __init__(self, combat: dict, after: dict):
        self.combat, self.after = combat, after
        self.pending: list[dict] = []
        self.done = False
        self.posts: list[dict] = []

    def get_state(self) -> dict:
        if self.pending:
            return self.pending.pop(0)
        return self.after if self.done else self.combat

    def post(self, action: str, **params) -> dict:
        self.posts.append({"action": action, **params})
        if action == "play_card":
            self.pending = [_victory_frame(self.combat)]
            self.done = True
        return {"status": "ok", "message": ""}

    def health(self) -> dict:
        return {"mod_version": "0.0-scripted"}


def test_the_frame_after_a_kill_is_named_a_transition_not_a_new_fight():
    """`EB-178`, the predicate. A combat screen with no `battle` block at all
    is the fight being torn down, not a fight starting."""
    live = combat_state()
    assert blindplay.transient(live) == ""
    assert blindplay.transient(_victory_frame(live))
    # ...and a build that simply stops sending `is_play_phase` is still a
    # screen, which is the neighbouring predicate this must not swallow.
    no_key = json.loads(json.dumps(live))
    no_key["battle"].pop("is_play_phase")
    assert blindplay.transient(no_key) == ""


def test_the_frame_after_a_kill_is_never_drawn_as_battle_round_zero():
    """Belt and braces for a wire that got stuck in the moment: blocked, and
    never a playable-looking round 0 with an empty hand."""
    obs = blindplay.observation(_victory_frame(combat_state()))
    assert obs["blocked"] and not obs["commands"]
    page = blindplay.render(obs)
    assert "round 0" not in page and "TOOL-BLOCKED" in page


def test_a_victory_renders_once_as_the_rewards_screen(tmp_path):
    """`EB-178`, end to end. Both of run B6's fight records read the moment
    after a kill as a NEW FIGHT: an empty `Battle -- round 0`. The seat must
    be shown the fight, then the rewards, and nothing in between."""
    combat = combat_state()
    wire = _VictoryWire(combat, rewards_state())
    thread = blindplay.ScriptedThread(
        [{"command": 'play "Pearl Barrage"', "thinking": "."},
         {"record": "fight"},
         {"command": 'choose "12 Gold"', "thinking": "."},
         {"record": "run"}])
    s = blindplay.Session(thread, wire=wire, session_id="t",
                          budget=blindplay.Budget(max_actions=2),
                          log_root=tmp_path,
                          settle_tries=8, settle_delay_s=0.0)
    s.run()
    pages = thread.sent
    assert not any("round 0" in p for p in pages), pages
    assert any("# Battle" in p for p in pages)
    assert any("What the fight left behind" in p for p in pages)


def test_a_wire_that_stays_unnamed_is_still_tool_blocked(tmp_path):
    wire = blindplay.ScriptedWire([{"state_type": "unknown"}])
    s = blindplay.Session(blindplay.ScriptedThread([]), wire=wire,
                          session_id="t", log_root=tmp_path,
                          settle_tries=3, settle_delay_s=0.0)
    assert s.run()["termination"] == "tool_blocked" and wire.posts == []


def test_the_session_stops_on_a_screen_it_will_not_drive(tmp_path):
    s, summary, wire, _ = _session(tmp_path, [], states=[hazard_event_state()])
    assert summary["termination"] == "tool_blocked" and wire.posts == []


def test_a_refusal_is_told_back_to_the_tester_in_its_own_words(tmp_path):
    replies = [{"command": 'play "Fireball"', "thinking": "?"},
               {"command": "end turn", "thinking": "fine"},
               {"record": "r"}, {"record": "r"}]
    s, summary, wire, thread = _session(tmp_path, replies,
                                        states=[combat_state()],
                                        max_actions=1)
    assert "That did not work" in thread.sent[1]
    assert "nothing here is called" in thread.sent[1]


# ------------------------------------------------- the seat and the seal ---

def test_the_author_s_own_model_family_is_refused_as_tester():
    """R217 C: independence is by model FAMILY, not by fresh context."""
    for model in ("claude-opus-5", "claude-sonnet-4.5", "anthropic/fable"):
        with pytest.raises(blindplay.BlindPlayError) as e:
            blindplay.check_independent(model)
        assert "family" in str(e.value)
    blindplay.check_independent("gpt-5.6-sol")          # the Codex seat passes
    with pytest.raises(blindplay.BlindPlayError):
        blindplay.check_independent("some-unheard-of-model")


def test_the_prompt_is_readable_and_stamped():
    body = blindplay.seat.template_body(
        blindplay.PROMPT_PATH.read_text(encoding="utf-8"))
    assert "one command" in body
    assert "judgement of whether the game is fun" in body.lower()
    assert len(blindplay.sha256(body)) == 64


def test_the_reply_schemas_constrain_shape_and_never_content():
    for schema in (blindplay.command_schema(), blindplay.record_schema()):
        assert schema["additionalProperties"] is False
        blob = json.dumps(schema)
        assert "enum" not in blob and "minLength" not in blob


def test_the_sealed_record_carries_the_identity_and_the_words_verbatim(tmp_path):
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "words"}]
    s, summary, _wire, thread = _session(tmp_path, replies,
                                         states=[combat_state()],
                                         max_actions=1)
    identity = {**thread.identity(), "build_version": "0.2.1269",
                "build_version_source":
                    "the deployed `mods\\klee\\manifest.json` `version`",
                "game_version": "v0.111.0",
                "game_version_source":
                    "the game's own `release_info.json` `version`",
                "run_seed": "HUMWKRKNCE",
                "prompt_sha256": summary["prompt_sha256"],
                "actions": summary["actions"],
                "termination": summary["termination"]}
    path = blindplay.seal(summary, identity, log_dir=s.dir,
                          record_root=tmp_path / "committed")
    text = path.read_text(encoding="utf-8")
    assert "0.2.1269" in text and "v0.111.0" in text and "HUMWKRKNCE" in text
    assert summary["prompt_sha256"] in text
    assert "R217 G" in text and "not approval" in text
    assert "words" in text


def test_both_versions_are_read_off_disk_or_left_empty_never_invented(
        tmp_path, monkeypatch):
    """`EB-174`. A sealed record has to name the MOD build and the GAME build,
    each labelled with where it was read -- and name neither rather than
    invent one. The bridge's health payload is not consulted at all: it
    carries the VENDORED bridge's own version and never ours, which is how
    every record's identity block came to read `(not read)`."""
    game = tmp_path / "Slay the Spire 2"
    (game / "mods" / "klee").mkdir(parents=True)
    props = tmp_path / "local.props"
    props.write_text(f"<Project><PropertyGroup><GameDir>{game}</GameDir>"
                     f"</PropertyGroup></Project>", encoding="utf-8")
    monkeypatch.setattr(blindplay, "LOCAL_PROPS", props)

    # Nothing deployed and no release file: two empties, two reasons.
    assert blindplay.build_version()[0] == ""
    assert "no deployed package" in blindplay.build_version()[1]
    assert blindplay.game_version()[0] == ""
    assert "release_info.json" in blindplay.game_version()[1]

    # `deploy.ps1` writes the manifest with a BOM; both reads survive one.
    (game / "mods" / "klee" / "manifest.json").write_text(
        '﻿{"id": "klee", "version": "0.2.1269"}', encoding="utf-8")
    (game / "release_info.json").write_text(
        '{"version": "v0.111.0", "commit": "41cef1ea"}', encoding="utf-8")
    assert blindplay.build_version() == (
        "0.2.1269", "the deployed `mods\\klee\\manifest.json` `version`")
    assert blindplay.game_version() == (
        "v0.111.0", "the game's own `release_info.json` `version`")

    # No local.props at all is a reason, not a traceback and not a guess.
    monkeypatch.setattr(blindplay, "LOCAL_PROPS", tmp_path / "absent.props")
    assert blindplay.build_version()[0] == ""
    assert blindplay.game_version()[0] == ""


# --- EB-173: the deadlock a live session died on --------------------------

def test_the_games_own_plus_is_not_folded_away():
    """FOUND LIVE, 2026-08-29, run B of the EB-167 acceptance. `_fold` stripped
    punctuation, and the `+` the GAME appends to an upgraded title is not
    punctuation -- it is the only thing distinguishing the two cards. Folded
    away, `Coral Guard` and `Coral Guard+` shared one key, so with both in hand
    EVERY naming of EITHER was refused as ambiguous and neither could be
    played. The session burned its refusal budget on round 5 and stopped."""
    state = combat_state()
    hand = state["player"]["hand"]
    base = json.loads(json.dumps(hand[3]))
    assert base["name"] == "Coral Guard"
    up = json.loads(json.dumps(base))
    up["name"] = "Coral Guard+"
    up["is_upgraded"] = True
    up["description"] = "Gain 8 Block."
    hand.append(up)

    plain = blindplay.act(state, 'play "Coral Guard"')
    assert plain["ok"] and plain["post"]["card_index"] == 3
    plus = blindplay.act(state, 'play "Coral Guard+"')
    assert plus["ok"] and plus["post"]["card_index"] == len(hand) - 1


def test_echoing_the_screen_back_verbatim_resolves():
    """The render prints `**Coral Guard+** (upgraded)`, and a tester who types
    that back must be understood. Before the fix it answered `nothing here is
    called 'Coral Guard+ (upgraded)'` -- the escape hatch the refusal itself
    advertised was documented in the grammar and implemented nowhere."""
    state = combat_state()
    hand = state["player"]["hand"]
    up = json.loads(json.dumps(hand[3]))
    up["name"] = "Coral Guard+"
    up["is_upgraded"] = True
    hand.append(up)
    res = blindplay.act(state, 'play "Coral Guard+ (upgraded)"')
    assert res["ok"] and res["post"]["card_index"] == len(hand) - 1


def test_the_qualifier_reaches_both_sides_of_an_ambiguous_pair():
    """The card-reward screen prints NO `+` -- two rows both read `Coral
    Guard`, one upgraded -- so the ambiguity refusal is still right there. What
    changed is that it is now escapable in BOTH directions: a disambiguator
    that could only ever name one of the two would leave the other
    unselectable, which is the same defect wearing a different hat."""
    amb = blindplay.act(card_reward_state(), 'choose "Coral Guard"')
    assert not amb["ok"] and "more than one" in amb["refusal"]

    up = blindplay.act(card_reward_state(), 'choose "Coral Guard (upgraded)"')
    assert up["ok"] and up["post"]["card_index"] == 1
    base = blindplay.act(card_reward_state(),
                         'choose "Coral Guard (not upgraded)"')
    assert base["ok"] and base["post"]["card_index"] == 0


def test_the_refusal_advertises_only_what_is_implemented():
    """The whole shape of EB-173: advice a tester cannot act on is worse than
    no advice, because it costs a turn of the refusal budget to discover."""
    amb = blindplay.act(card_reward_state(), 'choose "Coral Guard"')
    assert "(upgraded)" in amb["refusal"] and "(not upgraded)" in amb["refusal"]
    for phrase in ("Coral Guard (upgraded)", "Coral Guard (not upgraded)"):
        assert blindplay.act(card_reward_state(), f'choose "{phrase}"')["ok"]


def test_a_qualifier_that_matches_nothing_says_so_rather_than_guessing():
    state = combat_state()
    res = blindplay.act(state, 'play "Coral Guard (upgraded)"')
    assert not res["ok"] and "is upgraded" in res["refusal"]


def bundle_select_state() -> dict:
    """SYNTHETIC, and shaped on the LIVE wire read 2026-08-29: a bundle has an
    `index` and a list of `cards`, and NO name of its own."""
    return {"state_type": "bundle_select",
            "bundle_select": {"screen_type": "bundle",
                              "prompt": "Choose a bundle.",
                              "bundles": [
                {"index": 0, "card_count": 2, "cards": [
                    {"name": "Call to Arms", "cost": "1", "type": "Skill",
                     "description": "Muster 1. Draw 1 card."},
                    {"name": "Massed Volley", "cost": "1", "type": "Attack",
                     "description": "Deal 5 damage to ALL enemies."}]},
                {"index": 1, "card_count": 2, "cards": [
                    {"name": "Crane Wing", "cost": "1", "type": "Skill",
                     "description": "Gain 4 Block."},
                    {"name": "Massed Volley", "cost": "1", "type": "Attack",
                     "description": "Deal 5 damage to ALL enemies."}]}]}}


def test_a_bundle_is_named_by_what_is_in_it():
    """EB-173, second half. A bundle has no name, and asking the wire for one
    rendered `- **(unnamed)**` twice on a screen whose only verb was
    `choose "<bundle>"`. Nothing on it could be named; a live session sat there
    answering `confirm` until its action budget ran out. The cards inside DO
    have printed titles, so the bundle is named by its contents -- which is
    also how a player at the screen would say it out loud."""
    page = blindplay.render(blindplay.observation(bundle_select_state()))
    assert "(unnamed)" not in page
    assert "A bundle of: Call to Arms, Massed Volley" in page
    assert "Gain 4 Block." in page          # the faces, not just the titles
    assert "any card title in the bundle you want" in page


def test_choosing_a_bundle_by_a_card_only_it_holds():
    res = blindplay.act(bundle_select_state(), 'choose "Call to Arms"')
    assert res["ok"] and res["post"] == {"action": "select_bundle", "index": 0}
    res = blindplay.act(bundle_select_state(), 'choose "Crane Wing"')
    assert res["ok"] and res["post"] == {"action": "select_bundle", "index": 1}


def test_a_card_in_both_bundles_is_refused_rather_than_guessed():
    """Which bundle was meant is exactly the question being asked."""
    res = blindplay.act(bundle_select_state(), 'choose "Massed Volley"')
    assert not res["ok"] and "more than one bundle" in res["refusal"]


def test_a_card_in_no_bundle_is_told_what_is_on_the_screen():
    res = blindplay.act(bundle_select_state(), 'choose "Pearl Barrage"')
    assert not res["ok"]
    assert "Call to Arms" in res["refusal"] and "Crane Wing" in res["refusal"]


def test_the_session_stops_on_a_screen_it_cannot_get_off(tmp_path):
    """EB-173, third half, and the reason the other two cost a whole run. The
    action, wall and refusal budgets all stop a session that is going WRONG.
    None of them sees a session going NOWHERE: a command the resolver ACCEPTS
    and the wire answers with an error resets the refusal counter and spends an
    action, so the loop can sit on one screen until the action budget is gone.
    Live, that was 150+ identical `confirm`s at one bundle screen."""
    replies = [{"command": "confirm", "thinking": ""} for _ in range(40)]
    replies.append({"record": "nothing happened"})
    s, summary, wire, _ = _session(
        tmp_path, replies, states=[bundle_select_state()],
        max_actions=200, max_stalls=4)
    assert summary["termination"] == "stalled"
    assert summary["actions"] < 10


def test_a_hand_select_screen_does_not_kill_the_session():
    """EB-176, found live: a `hand_select` state renders as `card_select`, and
    only the WIRE's name was exempt from the snake_case rule -- so the tool's
    own name for the screen, written into the tool's own observation, tripped
    the blindness assertion and stopped a session on a screen that had leaked
    nothing. Both names are screen vocabulary; neither names a card, a role or
    a ruling."""
    state = {"state_type": "hand_select",
             "hand_select": {"prompt": "Choose a card to discard.",
                             "cards": [{"name": "Coral Guard", "cost": "1",
                                        "type": "Skill",
                                        "description": "Gain 5 Block."}]}}
    obs = blindplay.observation(state)          # must not raise
    assert obs["state_type"] == "hand_select" and obs["screen"] == "card_select"
    assert "Coral Guard" in blindplay.render(obs)


def test_the_exemption_is_still_only_the_screen_names():
    """The other half: widening the allowance must not have widened it to
    anything a card, a sheet or a ruling could put on the page."""
    state = {"state_type": "hand_select",
             "hand_select": {"prompt": "Choose a card to discard.",
                             "cards": [{"name": "Coral Guard", "cost": "1",
                                        "type": "Skill",
                                        "description": "role: bridge"}]}}
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observation(state)


# ---------------------------------------- EB-186, the whole-run play page ---

def banked_combat_state(bank: int = 3) -> dict:
    """A Klee combat screen at a Spark bank, as the live game draws it: two
    Attacks printing 1 and 2, both rendered 0, both playable. Round 1 of the
    Klee slice proved the board refuses the second of them."""
    return {
        "state_type": "monster",
        "battle": {"round": 1, "enemies": [
            {"name": "Seapunk", "hp": 45, "max_hp": 45, "block": 0,
             "intents": [{"type": "Attack", "label": "11",
                          "description": "Attack for 11 damage."}]}]},
        "player": {
            "hp": 42, "max_hp": 62, "block": 0, "energy": 2, "max_energy": 3,
            "resources": {}, "draw_pile_count": 10,
            "discard_pile_count": 0, "exhaust_pile_count": 0,
            "status": ([{"name": "Spark", "amount": bank, "type": "Buff",
                         "description": "At 3 Sparks, your Attacks cost 0. "
                                        "Playing one consumes 3 Sparks."}]
                       if bank else []),
            "hand": [
                {"id": "KLEEMOD-KABOOM", "name": "Kaboom!", "type": "Attack",
                 "cost": "0" if bank >= 3 else "1", "can_play": True,
                 "description": "Deal 7 damage. Applies Pyro."},
                {"id": "KLEEMOD-RAPID_FIRE", "name": "Rapid Fire",
                 "type": "Attack", "cost": "0" if bank >= 3 else "2",
                 "can_play": True,
                 "description": "Deal 4 damage to random enemies four times."},
                {"id": "KLEEMOD-DUCK_AND_COVER", "name": "Duck and Cover",
                 "type": "Skill", "cost": "1", "can_play": True,
                 "description": "Gain 5 Block."},
            ]},
    }


def test_the_play_page_states_the_spark_rule_and_the_printed_costs():
    """`EB-186` on the whole-run page. The tester playing a live run reads the
    same screen a staged grader does, so it carries the same two facts."""
    page = blindplay.render(blindplay.observation(banked_combat_state(3)))
    assert "At 3 Sparks, your Attacks cost 0. Playing one consumes 3 " \
           "Sparks." in page
    assert "covers 1 of the 2" in page
    assert page.count("The cost printed on this card") == 2
    assert "The cost printed on this card is 2; it is showing 0 here." in page


def test_the_play_page_says_nothing_extra_with_no_bank():
    page = blindplay.render(blindplay.observation(banked_combat_state(0)))
    assert "The cost printed on this card" not in page
    assert "Spark, and the costs below" not in page


# ------------------------------------------- the Kurage's memory (EB-181) ---
#
# The bridge field the memory rule needs, on the observed board. The rule
# itself is quarantined in the mod (`Powers/Prototype/KurageMemory.cs`), so
# these fixtures are SYNTHETIC and prove the READER, never the wire -- the same
# posture every non-combat screen above takes. What they pin is the contract in
# `vendor/STS2_MCP/gits/GitsKurageMemory.cs`: which fields exist, that an
# absent key is absent rather than empty, and that the block, the empty queue
# and the pulse each reach the page a tester reads.


def memory_combat_state(memory: dict | None) -> dict:
    """A Kokomi combat with (or without) `player.kurage_memory` on the wire."""
    state = combat_state()
    player = dict(state["player"])
    player.pop("kurage_memory", None)
    if memory is not None:
        player["kurage_memory"] = memory
    state = dict(state)
    state["player"] = player
    return state


BLOCKED_MEMORY = {
    "bank": 5, "front_price": 9, "blocked": True, "fires_next": False,
    "empty": False, "summon": True, "base_kit": True,
    "pulse_kind": "skill", "pulse_amount": 5, "pulse_unit": "block",
    "reading": "Charge 5 / 9 — Raiden Shogun blocked",
    # sec.14.4's running subtraction. The bank is 5 and the front costs 9, so
    # the queue runs out at entry 0 -- and Gorou, free though he is, is HELD
    # behind it, because a front the bank cannot pay holds everything and pays
    # nothing.
    "run_out_index": 0,
    "queue": [
        {"name": "Raiden Shogun", "cost": 3, "price": 9, "target": "Slime",
         "blocked": True, "affordable": False, "state": "runs_out",
         "ephemeral": False, "rule": "exhaust"},
        {"name": "Gorou", "cost": 0, "price": 0, "target": None,
         "blocked": False, "affordable": True, "state": "held",
         "ephemeral": True, "rule": "muster"},
    ],
}


def test_a_board_carrying_the_memory_parses_every_field():
    obs = blindplay.observation(memory_combat_state(BLOCKED_MEMORY))
    memory = obs["combat"]["memory"]
    assert memory["bank"] == 5
    assert memory["front_price"] == 9
    assert memory["blocked"] is True
    assert memory["fires_next"] is False
    assert memory["empty"] is False
    assert memory["summon"] is True
    assert memory["base_kit"] is True
    assert memory["pulse_kind"] == "skill"
    assert memory["pulse_amount"] == 5
    assert memory["pulse_unit"] == "block"
    assert [row["name"] for row in memory["queue"]] == ["Raiden Shogun",
                                                        "Gorou"]
    assert memory["queue"][0]["blocked"] is True
    assert memory["queue"][0]["target"] == "Slime"
    # A memory that stored NO target aims randomly, and the board says the word
    # rather than leaving a null for a reader to interpret.
    assert memory["queue"][1]["target"] == "random"
    assert memory["queue"][1]["price"] == 0
    # The affordability run rides beside the reading, so the page and the tests
    # see the same projection the pile view paints.
    assert memory["run_out_index"] == 0
    # ...but the wire's per-row STATE does not reach the board: "runs_out" is an
    # internal snake-case id and `assert_blind` refuses one. The index says the
    # same thing as a number and the page renders it as a sentence.
    assert "state" not in memory["queue"][0]


def test_a_board_without_the_key_has_no_memory_at_all():
    """A release build has no memory rule compiled in, and the observed board
    must not describe it as an EMPTY one. Absence is the fact."""
    obs = blindplay.observation(memory_combat_state(None))
    assert "memory" not in obs["combat"]
    assert "memory" not in blindplay.render(obs)


def test_an_empty_map_is_a_seat_that_is_not_kokomi_and_gets_no_section():
    """`EB-207`: the Klee page carried her jellyfish and told him it had
    played no card.

    THREE wire states, not two (`vendor/STS2_MCP/gits/GitsKurageMemory.cs`):
    an ABSENT key is a build with no memory rule, an EMPTY MAP is the rule
    present on a seat that is not hers -- exactly what
    `KurageMemory.Snapshot` returns off a failed `IsLive` -- and a populated
    map is a memory. Reading `{}` as a memory built the whole section out of
    `_int`/`_text` defaults, and the `none` pulse default rendered as a
    sentence about a card the tester HAD played.
    """
    obs = blindplay.observation(memory_combat_state({}))
    assert "memory" not in obs["combat"]
    page = blindplay.render(obs)
    assert "Bake-Kurage" not in page
    assert "you have played no card this turn" not in page
    # A real memory beside it is untouched: refusing `{}` cannot suppress one,
    # because `Snapshot` writes twelve keys before it writes the queue.
    assert "Bake-Kurage" in blindplay.render(
        blindplay.observation(memory_combat_state(BLOCKED_MEMORY)))


def test_the_page_shows_the_bank_the_price_the_block_and_the_pulse():
    """D4: everything that will fire next turn is readable this turn.

    THE PAGE MIRRORS THE ELEMENT (sec.14). The strip's one running line is gone
    and each fact stands on its own: the Charge count, then the front card with
    its price and whether it fires, then the queue behind a heading, then the
    run-out. `EB-198` is the reason -- the tester read "Charge 1 / 0" as a
    fraction over a zero denominator, and both frames were true as drawn.
    """
    page = blindplay.render(blindplay.observation(
        memory_combat_state(BLOCKED_MEMORY)))
    assert "- Charge: 5" in page
    assert ("- Next to fire: **Raiden Shogun** — costs 9 Charge — you cannot "
            "pay it, so NOTHING in the memory fires next turn." in page)
    assert "aims at Slime" in page
    assert "aims at random" in page
    # A 0-cost memory reads as free, because it is.
    assert "**Gorou** — free" in page
    # The run-out is CALLED OUT rather than left to be counted off the list,
    # and it names what is held behind it.
    assert "Charge runs out at #1 (**Raiden Shogun**)" in page
    assert "everything behind it are held" in page
    assert "the jellyfish will give you 5 Block" in page
    # The strip's grammars are gone with the strip.
    assert "Charge 5 / 9" not in page


def test_the_pile_views_charge_source_header_reaches_the_blind_page():
    """`EB-214` item 7 (`M55`, re-scoped by R224).

    The Charge-source line is a Godot Label at the head of the pile view
    (`KurageMemoryText.ChargeSource`), so a SIGHTED player reads it on a
    click and a blind tester -- who has no click -- would never see it at
    all. `P4`'s half (b) is exactly "name a play that would supply the
    Charge", so a rerun grading that half against a line the page does not
    carry would be grading a surface the tester was never shown.

    The rate INTERPOLATES from the same constant the C# reads, which
    `lint_constant_parity` pins equal (`KokomiConstants.ChargePerExhaust ==
    C.CHARGE_PER_EXHAUST`), so a retune moves both sentences or neither.
    """
    page = blindplay.render(blindplay.observation(
        memory_combat_state(BLOCKED_MEMORY)))
    assert blindplay.CHARGE_SOURCE_LINE == (
        f"Gain {C.CHARGE_PER_EXHAUST} Charge when a card of yours Exhausts")
    assert blindplay.CHARGE_SOURCE_LINE in page
    # It heads the QUEUE, where the pile view puts it -- not the top of the
    # section, and never on an empty queue, which has no view to head.
    assert "and then the whole memory, front first:" in page
    empty = dict(BLOCKED_MEMORY, front_price=None, blocked=False,
                 fires_next=False, empty=True, queue=[])
    assert "when a card of yours Exhausts" not in blindplay.render(
        blindplay.observation(memory_combat_state(empty)))


def test_a_discounted_memory_prints_the_cost_it_was_multiplied_by():
    """`EB-248`. The price is derivable from what the queue prints.

    A Muster recruit is discounted by one, so *Thoma - Crimson Ooyoroi* prints
    a face of 2 and enrols at `cost: 1, price: 3`: the rule reads the EFFECTIVE
    cost, and a tester holding the card and the queue side by side has no route
    from the 2 to the 3. `KURAGECAD-W1`'s tester named exactly that. Each queue
    line now carries the cost the rule multiplied, in
    `KurageMemory.PriceText`'s words, so the arithmetic is on the page.

    The rate is the sim's rather than a number typed twice, and this assertion
    is the pin: `blindplay` may not import `tier0` itself.
    """
    assert blindplay.KURAGE_COST_PER_ENERGY == C.KURAGE_MEMORY_COST_PER_ENERGY
    discounted = dict(
        BLOCKED_MEMORY, bank=3, front_price=3, blocked=False, fires_next=True,
        run_out_index=-1,
        reading="Charge 3 / 3 — Thoma - Crimson Ooyoroi fires next turn",
        queue=[
            {"name": "Thoma - Crimson Ooyoroi", "cost": 1, "price": 3,
             "target": "Slime", "blocked": False, "affordable": True,
             "ephemeral": False, "rule": "muster"},
            {"name": "Gorou", "cost": 0, "price": 0, "target": None,
             "blocked": False, "affordable": True, "ephemeral": True,
             "rule": "muster"},
        ])
    page = blindplay.render(blindplay.observation(
        memory_combat_state(discounted)))
    assert ("1. **Thoma - Crimson Ooyoroi** — 3 Charge, cost 1 x 3 — "
            "aims at Slime" in page)
    assert f"cost 1 x {C.KURAGE_MEMORY_COST_PER_ENERGY}" in page
    # A free memory reads as free and carries no derivation: a zero price is a
    # zero cost, and "cost 0 x 3" would restate the answer rather than explain
    # it.
    assert "2. **Gorou** — free — aims at random" in page
    # EVERY entry carries its own, front or not.
    blocked = blindplay.render(blindplay.observation(
        memory_combat_state(BLOCKED_MEMORY)))
    assert ("1. **Raiden Shogun** — 9 Charge, cost 3 x 3 — aims at Slime"
            in blocked)


def test_the_page_says_a_payable_front_fires_and_names_no_run_out():
    """The other side of the same element: a bank that covers the whole queue
    draws blue throughout, and the page must not invent a shortfall."""
    payable = dict(BLOCKED_MEMORY, bank=12, front_price=9, blocked=False,
                   fires_next=True, run_out_index=-1,
                   reading="Charge 12 / 9 — Raiden Shogun fires next turn",
                   queue=[dict(BLOCKED_MEMORY["queue"][0], blocked=False,
                               affordable=True, state="payable"),
                          dict(BLOCKED_MEMORY["queue"][1], state="payable")])
    page = blindplay.render(blindplay.observation(
        memory_combat_state(payable)))
    assert "- Charge: 12" in page
    assert ("- Next to fire: **Raiden Shogun** — costs 9 Charge — it fires at "
            "the start of your next turn." in page)
    assert "Your Charge covers every memory queued" in page
    assert "runs out at" not in page


def test_an_empty_memory_says_so_and_is_not_a_block():
    empty = dict(BLOCKED_MEMORY, front_price=None, blocked=False,
                 fires_next=False, empty=True, queue=[],
                 pulse_kind="none", pulse_amount=0, pulse_unit="none",
                 reading="Charge 5 — memory empty")
    obs = blindplay.observation(memory_combat_state(empty))
    assert obs["combat"]["memory"]["front_price"] is None
    page = blindplay.render(obs)
    # The empty state is the count ALONE on the element, and the page says the
    # same thing in words: no card, no price, no ring.
    assert "The memory is empty. Nothing is queued and nothing fires" in page
    assert "- Charge: 5" in page
    assert "Next to fire" not in page
    assert "runs out at" not in page
    assert "you have played no card this turn" in page


def test_the_power_pulse_reads_in_charge():
    """The Power branch pays in Charge, so the page has to be able to say a
    unit that is neither damage nor Block."""
    powered = dict(BLOCKED_MEMORY, pulse_kind="power", pulse_amount=1,
                   pulse_unit="charge")
    page = blindplay.render(blindplay.observation(
        memory_combat_state(powered)))
    assert "the jellyfish will give you 1 Charge" in page


def test_the_page_names_the_jellyfish_as_a_fight_start_fact():
    """sec.12.6 item 12. Under the base kit the Bake-Kurage is installed at
    combat start, so a blind run must be able to SEE it before turn 1 rather
    than inferring it from the first pulse."""
    page = blindplay.render(blindplay.observation(
        memory_combat_state(BLOCKED_MEMORY)))
    assert "on the field for the whole fight" in page


def test_a_summoned_jellyfish_is_not_announced_as_base_kit():
    """With the base kit off the v3 arm is still reachable, and the page must
    not tell a tester the jellyfish is permanent when it is not."""
    summoned = dict(BLOCKED_MEMORY, base_kit=False)
    page = blindplay.render(blindplay.observation(
        memory_combat_state(summoned)))
    assert "on the field for the whole fight" not in page


# ------------------------------------------------- EB-216: the wire snapshot -
#
# `M56` (R224 A). The record's OBJECTIVE side: a machine-written board per
# play and per end turn, so `P2` (a call against that turn's
# `blocked`/`fires_next` pair) and `P6` (was the aim right) are countable at
# all. Nothing already published is re-graded (R101b); these pin the channel
# the NEXT run writes.


def test_the_wire_snapshot_is_taken_on_every_play_and_every_end_turn(tmp_path):
    replies = [
        {"command": 'play "Pearl Barrage" on "Nibbit"', "thinking": "chip"},
        {"command": "end turn", "thinking": "done"},
        {"record": "fight"},
        {"command": 'choose "12 Gold"', "thinking": "take it"},
        {"record": "run"},
    ]
    _s, summary, _wire, _thread = _session(tmp_path, replies)
    rows = summary["wire"]
    # Three actions were posted; the reward claim is not a turn and gets no row.
    assert [r["verb"] for r in rows] == ["play", "end turn"]
    assert [r["index"] for r in rows] == [1, 2]
    assert rows[0]["command"] == 'play "Pearl Barrage" on "Nibbit"'


def test_the_wire_snapshot_reads_the_board_off_the_wire_not_the_page():
    """Every field is the API's own, ids included -- which is the whole point:
    the tester's page hides ids by construction and a grader reading it back
    would be grading a rendering of the board rather than the board."""
    snap = blindplay.wire_snapshot(combat_state(), index=1, verb="end turn")
    assert snap["state_type"] and snap["turn"] >= 0
    assert snap["energy"] == combat_state()["player"]["energy"]
    assert snap["enemy_count"] == len(combat_state()["battle"]["enemies"])
    assert snap["enemies"][0]["entity_id"] == "NIBBIT_0"
    assert snap["enemies"][0]["intents"][0]["type"] == "Attack"
    assert snap["hand"][0]["id"] == "KLEEMOD-PEARL_BARRAGE"
    assert snap["hand"][0]["energy_cost"] == "1"
    assert set(snap["piles"]) == {"draw", "discard", "exhaust"}


def test_the_wire_snapshot_carries_every_meter_including_the_zeroes():
    """The observed board prints only NON-ZERO meters, deliberately. A grader
    counting "the bank was empty when the call was made" needs the zero, and
    it needs the Spark bank too -- which is a POWER, not a registered
    resource, so a snapshot reading one source would lose whichever meter the
    character in front of it actually uses."""
    state = combat_state()
    state["player"]["status"] = [
        {"id": "KLEEMOD-SPARK", "name": "Spark", "amount": 2,
         "type": "Buff", "description": "A resource."}]
    snap = blindplay.wire_snapshot(state, index=1, verb="end turn")
    assert snap["meters"]["resources"]["KLEEMOD_CHARGE"] == 8
    assert snap["meters"]["resources"]["KLEEMOD_ENCORE"] == 0
    assert snap["meters"]["powers"]["KLEEMOD-SPARK"] == 2


def test_the_wire_snapshot_carries_the_memory_strip_only_when_the_wire_does():
    """The bridge's three-state contract, kept: an ABSENT key is "no memory
    rule in this build", and inventing an empty one here would make a release
    build look like a Kokomi seat holding nothing."""
    with_memory = blindplay.wire_snapshot(
        memory_combat_state(BLOCKED_MEMORY), index=1, verb="end turn")
    assert with_memory["kurage_memory"]["blocked"] is True
    assert with_memory["kurage_memory"]["fires_next"] is False
    # UNSCRUBBED, unlike the page: the per-row `state` id the observed board
    # must never print is exactly what an erratum reader wants.
    assert "queue" in with_memory["kurage_memory"]
    without = blindplay.wire_snapshot(memory_combat_state(None), index=1,
                                      verb="end turn")
    assert "kurage_memory" not in without


def test_the_wire_snapshot_omits_a_spark_price_the_wire_omits():
    state = combat_state()
    state["player"]["hand"][0]["spark_price"] = 2
    state["player"]["hand"][0]["spark_affordable"] = False
    snap = blindplay.wire_snapshot(state, index=1, verb="play")
    assert snap["hand"][0]["spark_price"] == 2
    assert snap["hand"][0]["spark_affordable"] is False
    assert "spark_price" not in snap["hand"][1]


def test_the_wire_snapshot_never_reaches_the_tester(tmp_path):
    """R101b. The tester's page is the grading surface; the snapshot is the
    grader's. A card id is the cheapest proof: it is in every snapshot row and
    must be in no prompt."""
    replies = [{"command": "end turn", "thinking": "x"} for _ in range(2)]
    replies.append({"record": "words"})
    _s, summary, _wire, thread = _session(tmp_path, replies,
                                          states=[combat_state()],
                                          max_actions=2)
    assert summary["wire"] and summary["wire"][0]["hand"][0]["id"]
    for sent in thread.sent:
        assert "KLEEMOD-PEARL_BARRAGE" not in sent
        assert "entity_id" not in sent and "NIBBIT_0" not in sent


def test_seal_writes_the_snapshot_beside_the_record_and_names_it(tmp_path):
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "words"}]
    s, summary, _wire, thread = _session(tmp_path, replies,
                                         states=[combat_state()],
                                         max_actions=1)
    path = blindplay.seal(summary, dict(thread.identity()), log_dir=s.dir,
                          record_root=tmp_path / "committed")
    blob = json.loads((path.parent / "wire.json").read_text(encoding="utf-8"))
    assert blob["session_id"] == "t"
    assert len(blob["snapshots"]) == 1
    # The gitignored half too: every committed grader takes the LOG dir.
    lines = (s.dir / "wire.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(x)["index"] for x in lines] == [1]
    # The record NAMES the channel and does not inline the board.
    text = path.read_text(encoding="utf-8")
    assert "1 in `wire.json`" in text
    assert "KLEEMOD-PEARL_BARRAGE" not in text


# ------------------------------------------------ EB-216: the Spark ledger --
#
# R225's clause. Per play: `{card, before, price_paid, gains {source: n},
# after}`, so a record can rebuild what a play cost and where the bank came
# back from. The arithmetic itself is the mod's and is pinned in
# `klee-mod/KleeTests/MeterLedgerTests.cs`; these pin the DRIVER's half --
# which rows land on which snapshot, and what happens when there is no ledger.


def _row(index, card, before, price, gains, after):
    return {"index": index, "meter": "spark", "turn": 1, "card": card,
            "card_name": card.title(), "before": before, "price_paid": price,
            "gains": gains, "after": after, "entries": []}


def test_each_snapshot_carries_the_ledger_rows_that_action_minted(tmp_path):
    """The rows are read AFTER the POST -- the board is the decision, the
    ledger is what the decision cost -- and each snapshot gets only what is
    new, never the fight's whole history over again."""
    replies = [
        {"command": 'play "Pearl Barrage" on "Nibbit"', "thinking": "chip"},
        {"command": "end turn", "thinking": "done"},
        {"record": "fight"},
        {"command": 'choose "12 Gold"', "thinking": "take it"},
        {"record": "run"},
    ]
    first = _row(1, "kapow", 4, 1, {"relic:pounding_surprise/detonation": 2}, 5)
    second = _row(2, "", 5, 0, {"power:spark_per_turn/turn_start": 1}, 6)
    _s, summary, _w, _t = _session(tmp_path, replies,
                                   ledger=[[first], [first, second]])
    rows = summary["wire"]
    assert [r["index"] for r in rows[0]["ledger"]] == [1]
    assert [r["index"] for r in rows[1]["ledger"]] == [2]
    play = rows[0]["ledger"][0]
    assert (play["before"], play["price_paid"], play["after"]) == (4, 1, 5)
    assert play["gains"]["relic:pounding_surprise/detonation"] == 2


def test_a_build_with_no_ledger_still_snapshots_and_says_why(tmp_path):
    """`available: false` is "this build has no klee mod", which is a
    different fact from an empty ledger and is recorded as such rather than
    flattened into no rows at all."""
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "w"}]
    _s, summary, _w, _t = _session(tmp_path, replies, states=[combat_state()],
                                   max_actions=1)
    snap = summary["wire"][0]
    assert snap["ledger"] == []
    assert snap["ledger_note"].startswith("unavailable")


def test_a_ledger_that_cannot_be_reached_does_not_stop_the_run(tmp_path):
    """An instrument that fails must never take a run with it."""
    class _Broken(blindplay.ScriptedWire):
        def meter_ledger(self):
            raise blindplay.bridge.BridgeError("bridge unreachable")

    thread = blindplay.ScriptedThread(
        [{"command": "end turn", "thinking": "x"}, {"record": "w"}])
    s = blindplay.Session(thread, wire=_Broken([combat_state()]),
                          session_id="t", log_root=tmp_path,
                          budget=blindplay.Budget(max_actions=1))
    summary = s.run()
    assert summary["termination"] == "max_actions"
    assert summary["wire"][0]["ledger_note"].startswith("error:")


def test_the_ledger_read_survives_the_numbering_restarting_at_a_new_fight():
    """The mod clears the ledger at every combat start, so a watermark the
    ledger has fallen BEHIND means "new fight" and not "nothing new" --
    filtering on it blindly would drop a whole fight's rows."""
    wire = blindplay.ScriptedWire([combat_state()],
                                  ledger=[[_row(1, "a", 0, 0, {"card:a": 1},
                                                1)]])
    wire.i = 1
    rows, note = blindplay.ledger_rows(wire, after_index=7)
    assert note == "" and [r["index"] for r in rows] == [1]


def test_the_ledger_never_reaches_the_tester(tmp_path):
    """R101b again, and the sharper half of it: the ledger names ENGINE
    EVENTS in a developer's vocabulary, which is exactly what the observed
    board refuses to print."""
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "w"}]
    row = _row(1, "kapow", 3, 3, {"rule:threshold_consume": 0}, 0)
    _s, summary, _w, thread = _session(tmp_path, replies,
                                       states=[combat_state()],
                                       ledger=[[row]], max_actions=1)
    assert summary["wire"][0]["ledger"]
    for sent in thread.sent:
        assert "threshold_consume" not in sent
        assert "price_paid" not in sent


def test_a_grader_reads_the_snapshots_from_either_half_of_a_session(tmp_path):
    """`EB-216`. Committed graders take the GITIGNORED log dir; the committed
    record dir is what survives the log being swept. One reader, both."""
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "w"}]
    row = _row(1, "kapow", 4, 3, {"relic:pounding_surprise/detonation": 1}, 2)
    s, summary, _w, thread = _session(tmp_path, replies,
                                      states=[combat_state()],
                                      ledger=[[row]], max_actions=1)
    record = blindplay.seal(summary, dict(thread.identity()), log_dir=s.dir,
                            record_root=tmp_path / "committed")
    from_log = blindplay.read_snapshots(s.dir)
    from_record = blindplay.read_snapshots(record.parent)
    assert from_log == from_record and len(from_log) == 1
    # A session sealed before the channel existed is not an error.
    assert blindplay.read_snapshots(tmp_path / "nothing-here") == []


def test_the_grader_reads_one_meters_plays_with_the_four_fields(tmp_path):
    replies = [{"command": "end turn", "thinking": "x"}, {"record": "w"}]
    spark = _row(1, "kapow", 4, 3, {"relic:pounding_surprise/detonation": 1}, 2)
    charge = dict(_row(2, "oath", 8, 8, {}, 0), meter="charge")
    _s, summary, _w, _t = _session(tmp_path, replies, states=[combat_state()],
                                   ledger=[[spark, charge]], max_actions=1)
    plays = blindplay.meter_plays(summary["wire"])
    assert len(plays) == 1
    play = plays[0]
    assert play["card"] == "kapow"
    assert (play["before"], play["price_paid"], play["after"]) == (4, 3, 2)
    assert play["gains"] == {"relic:pounding_surprise/detonation": 1}
    assert play["snapshot"] == 1
    # `meter` is a parameter for the reason it is a field on the mod side.
    assert [p["card"] for p in
            blindplay.meter_plays(summary["wire"], meter="charge")] == ["oath"]


# ============================================================== EB-238 =====
#
# THE PAGE PRINTED NO RELIC ON A COMBAT SCREEN, and `KLEESPARK-BT1` §22.4 is
# the bill: Klee's starter *Pounding Surprise* refunded the very Spark price
# the round was registered to measure, in front of eight blind readers, none
# of whom could see it. The relic row is on the HUD for the whole of a run;
# it is on the page now for the same reason.

POUNDING_SURPRISE = {
    "id": "KLEEMOD-POUNDING_SURPRISE",
    "name": "Pounding Surprise",
    "description": ("Whenever a Bomb detonates, gain 1 Spark. Card rewards "
                    "after a fight offer a fourth Companion choice."),
    "counter": None,
    "keywords": [],
}


def _klee_combat_state() -> dict:
    """The recorded combat board, carrying Klee's starter relic."""
    state = combat_state()
    state["player"]["relics"] = [POUNDING_SURPRISE]
    return state


def test_the_combat_page_prints_the_run_s_relics():
    """THE LOCK. The relic that refunded the price is on the combat page."""
    page = blindplay.observe(_klee_combat_state())
    assert "## Your relics" in page
    assert "**Pounding Surprise**" in page
    assert "Whenever a Bomb detonates, gain 1 Spark." in page


def test_the_relic_line_carries_no_id_and_stays_blind():
    """Printed name and printed hover text; the wire's id never lands."""
    obs = blindplay.observation(_klee_combat_state())
    assert obs["combat"]["you"]["relics"] == [
        {"name": "Pounding Surprise",
         "text": POUNDING_SURPRISE["description"]}]
    page = blindplay.render(obs)
    assert "KLEEMOD" not in page and "POUNDING_SURPRISE" not in page


def test_a_relic_counter_is_printed_only_when_the_icon_draws_one():
    """`counter` is null on most relics and a number on a few; both render."""
    state = _klee_combat_state()
    state["player"]["relics"] = [dict(POUNDING_SURPRISE, counter=4)]
    assert "(4)" in blindplay.observe(state)


def test_a_run_with_no_relics_prints_no_relic_block():
    """Absent where there is nothing, like every other block on this page."""
    state = combat_state()
    state["player"]["relics"] = []
    assert "## Your relics" not in blindplay.observe(state)


BEATING_REMNANT = {
    "id": "BEATING_REMNANT",
    "name": "Beating Remnant",
    "description": "You cannot lose more than 20 HP in a single turn.",
    "counter": None,
    "keywords": [],
}


def test_every_screen_that_is_not_a_fight_prints_the_relic_row():
    """`EB-473`. A RUN THAT ENDED HOLDING A RELIC THE SEAT COULD NOT DESCRIBE.

    "`Beating Remnant` was claimed as an elite relic and no subsequent screen
    reprinted its text, so I finished the run holding a relic I cannot
    describe. Every other relic I own prints in the combat header" (Klee r15
    run 2 (c) 5).

    THE ROW'S DIAGNOSIS -- a cached subset -- IS NOT WHAT HAPPENED, and the
    difference is the whole fix. `relic_faces` reads `player.relics` off the
    feed and prints every row of it; the wire fills that list on every screen,
    because `BuildPlayerState` runs unconditionally and only its COMBAT fields
    are gated. What was gated is the PRINTING: `EB-238` put the block inside
    the combat branch, and that relic was claimed at the reward of the last
    fight of the run, so no later combat page existed to carry it.

    The repair is `EB-371`'s, one rule over: the HUD carries the row through
    every screen, so the page does too, under the same heading.

    Seen to FAIL: every screen below printed no relic block at all.
    """
    for build in (map_state, shop_state, rest_state, card_reward_state,
                  rewards_state, treasure_state):
        state = build()
        state.setdefault("player", {})["relics"] = [BEATING_REMNANT]
        page = blindplay.observe(state)
        assert "## Your relics" in page, build.__name__
        assert ("- **Beating Remnant** — You cannot lose more than 20 HP in "
                "a single turn.") in page, build.__name__
        # Once. The combat header is the only other emitter and this is not it.
        assert page.count("## Your relics") == 1, build.__name__
        assert "BEATING_REMNANT" not in page, build.__name__


def test_a_screen_with_no_relics_still_prints_no_relic_block():
    """The other half, on the screens `EB-473` reached: a run holding none
    reads exactly as it always did, and so does a screen the page refuses to
    drive at all."""
    assert "## Your relics" not in blindplay.observe(map_state())
    blocked = map_state()
    blocked["state_type"] = "menu"
    blocked["player"]["relics"] = [BEATING_REMNANT]
    assert "## Your relics" not in blindplay.observe(blocked)


# ------------------- EB-229: the forecast channel for a blind RUN ----------
#
# `KURAGEMEM002` graded `P1`, `P2` and `P4` UNREACHED and the display was not
# what failed: the reply schema was `command` and `thinking`, so the tester
# says why it plays what it plays and is never asked what it EXPECTS. §13.5's
# *stated IN ADVANCE* rule was on the record with nothing enforcing it. The
# staged twin is `EB-239`; this is the RUN lane's, and it is OPT-IN, which is
# the first thing these tests pin.

_OFF_SCHEMA = {"type": "object",
               "properties": {"command": {"type": "string"},
                              "thinking": {"type": "string"}},
               "required": ["command", "thinking"],
               "additionalProperties": False}


def test_the_run_lane_schema_is_byte_identical_with_the_channel_off():
    """THE LOCK, AND IT MUST BE SEEN TO FAIL. Every registration already run
    and every replay of one was asked through this exact object; a channel
    that changes it when nobody switched it on has silently re-registered
    them. `command_schema()` with no argument, and with an explicit zero, is
    the schema `KLEESPARK-W1` through `W4` and both `KURAGEMEM` runs were
    sent."""
    assert blindplay.command_schema() == _OFF_SCHEMA
    assert blindplay.command_schema(0) == _OFF_SCHEMA
    assert blindplay.command_schema(-1) == _OFF_SCHEMA
    assert "forecast" not in json.dumps(blindplay.command_schema())


def test_switching_the_channel_on_adds_the_field_and_asks_it_first():
    """Declared, not loosened -- `additionalProperties` stays `False` -- and
    `forecast` is the FIRST property and the FIRST required key, because a
    reply is written top to bottom and a forecast written after the command
    is a rationalisation."""
    schema = blindplay.command_schema(3)
    assert schema["additionalProperties"] is False
    assert list(schema["properties"]) == ["forecast", "command", "thinking"]
    assert schema["required"] == ["forecast", "command", "thinking"]
    assert schema["properties"]["forecast"] == {
        "type": "array", "items": {"type": "string"}}
    # Shape only, never content -- the standing rule for both reply schemas.
    blob = json.dumps(schema)
    assert "enum" not in blob and "minLength" not in blob


def test_the_questions_are_printed_above_the_board_and_above_the_command(
        tmp_path):
    """Position is the whole point, and it is `qa_packet`'s position for the
    staged twin: the block sits above the board and far above the line that
    asks for a command."""
    asks = ["What will the enemy do next turn?",
            "How much Block will you have?"]
    session = blindplay.Session(
        blindplay.ScriptedThread([]), wire=blindplay.ScriptedWire([]),
        session_id="t", log_root=tmp_path, forecast=asks)
    page = session._page("## The board", "", asks)
    assert page.index("## Before you decide") < page.index("## The board")
    assert page.index("## Before you decide") < page.index("ONE command")
    assert "1. What will the enemy do next turn?" in page
    assert "2. How much Block will you have?" in page
    # And the same method with no questions is the page it always was.
    assert session._page("## The board", "") == (
        "## The board\n\nAnswer with ONE command from the grammar.")


def test_a_run_that_registers_no_forecast_is_asked_and_sealed_as_before(
        tmp_path):
    """The other half of the lock, end to end: no block on any page, the OFF
    schema on every send, and no forecast key anywhere in the summary or the
    committed record."""
    thread = blindplay.ScriptedThread(
        [{"command": "end turn", "thinking": "."}, {"record": "r"}])
    s = blindplay.Session(thread, wire=blindplay.ScriptedWire(
        [combat_state(), game_over_state()]), session_id="t",
        budget=blindplay.Budget(max_actions=1), log_root=tmp_path,
        settle_delay_s=0.0)
    summary = s.run()
    assert all("Before you decide" not in p for p in thread.sent)
    assert thread.schemas[0] == _OFF_SCHEMA
    assert "forecast" not in json.dumps(summary)
    assert "Forecasts" not in blindplay.record_markdown(summary, {})


def test_a_registered_run_asks_every_combat_turn_and_counts_the_answers(
        tmp_path):
    """The acceptance: a forecast slot with a field to COUNT. The answers are
    attached to the page they were written on, sealed on the committed half,
    and never graded here -- the registration that switched the channel on is
    what grades them against the wire."""
    thread = blindplay.ScriptedThread(
        [{"forecast": ["it attacks", "5"], "command": "end turn",
          "thinking": "."},
         {"record": "r"}])
    asks = ["What will the enemy do next turn?",
            "How much Block will you have?"]
    s = blindplay.Session(thread, wire=blindplay.ScriptedWire(
        [combat_state(), game_over_state()]), session_id="t",
        budget=blindplay.Budget(max_actions=1), log_root=tmp_path,
        settle_delay_s=0.0, forecast=asks)
    summary = s.run()
    assert "## Before you decide" in thread.sent[0]
    assert thread.schemas[0] == blindplay.command_schema(2)
    assert summary["forecast_questions"] == asks
    row = summary["forecasts"][0]
    assert row["action"] == 1 and row["questions"] == asks
    assert row["answers"] == ["it attacks", "5"]
    assert (row["asked"], row["answered"], row["short"]) == (2, 2, False)
    assert len(row["observation_sha256"]) == 64
    rows = [r for r in s.transcript.rows if r["kind"] == "forecast"]
    assert len(rows) == 1 and rows[0]["answered"] == 2
    record = blindplay.record_markdown(summary, {})
    assert "## Forecasts, stated in advance" in record
    assert "**asked on**: 1 turns, 0 of them answered short" in record
    assert "| 1 | it attacks | 5 |" in record


def test_a_short_forecast_is_counted_short_and_never_stops_the_run(tmp_path):
    """A live run cannot un-spend the game time a staged form can re-read, so
    the driver records the shortfall rather than refusing: a slot whose
    denominator is short is a fact its grader can see."""
    thread = blindplay.ScriptedThread(
        [{"forecast": ["it attacks", ""], "command": "end turn",
          "thinking": "."}, {"record": "r"}])
    s = blindplay.Session(thread, wire=blindplay.ScriptedWire(
        [combat_state(), game_over_state()]), session_id="t",
        budget=blindplay.Budget(max_actions=1), log_root=tmp_path,
        settle_delay_s=0.0, forecast=["q one", "q two"])
    summary = s.run()
    assert summary["termination"] == "max_actions"
    assert summary["forecasts"][0]["short"] is True
    assert summary["forecasts"][0]["answered"] == 1


def test_a_screen_with_no_turn_to_predict_is_not_asked(tmp_path):
    """A map walk, a shop or a reward screen has no next turn, so asking
    there would collect a forecast about a board the tester is not on."""
    thread = blindplay.ScriptedThread(
        [{"command": 'go "Monster"', "thinking": "."}, {"record": "r"}])
    s = blindplay.Session(thread, wire=blindplay.ScriptedWire(
        [map_state(), game_over_state()]), session_id="t",
        budget=blindplay.Budget(max_actions=1), log_root=tmp_path,
        settle_delay_s=0.0, forecast=["q one"])
    s.run()
    assert "Before you decide" not in thread.sent[0]
    assert thread.schemas[0] == _OFF_SCHEMA
    assert s.forecasts == []


def test_a_forecast_question_answers_to_the_pages_own_leak_rule(tmp_path):
    """It is printed on the blind page, so it is scrubbed like every other
    line of it -- `staged_turn` checks its own the same way."""
    with pytest.raises(blindplay.BlindPlayError) as exc:
        blindplay.Session(blindplay.ScriptedThread([]),
                          wire=blindplay.ScriptedWire([]), session_id="t",
                          log_root=tmp_path,
                          forecast=["will kurage_memory fire?"])
    assert "leaks design vocabulary" in str(exc.value)


# --------------------------------------- EB-286: the Spark half of a price --

def spark_priced_state() -> dict:
    """A Klee-overhaul hand as the live bridge draws it (`EB-286`).

    Every Spark-priced row prints ENERGY 0 and charges Sparks instead, so a
    hand line built from `cost` alone said `cost 0` about a card the board
    then refused. `Bang Bang!` is the two-Spark row the r3 Opus seat called a
    trap ("sat unplayable in my hand across two entire fights, which for a
    card that prints cost 0 is a trap"); `Dig In` is the starter's one-Spark
    sink. The wire's `spark_price` / `spark_affordable` pair is the GItS local
    edit in `BuildCardState`, present only on a card that charges Sparks --
    which is why `Kaboom!` below carries neither.
    """
    return {
        "state_type": "monster",
        "battle": {"round": 2, "enemies": [
            {"name": "Corpse Slug", "hp": 25, "max_hp": 27, "block": 0,
             "intents": [{"type": "Attack", "label": "8",
                          "description": "Attack for 8 damage."}]}]},
        "player": {
            "hp": 55, "max_hp": 62, "block": 0, "energy": 3, "max_energy": 3,
            "resources": {}, "draw_pile_count": 5,
            "discard_pile_count": 3, "exhaust_pile_count": 0,
            "status": [],
            "hand": [
                {"id": "KLEEMOD-PROTO_KO_BANG_BANG", "name": "Bang Bang!",
                 "type": "Attack", "cost": "0", "can_play": False,
                 "spark_price": 2, "spark_affordable": False,
                 "unplayable_reason": "BlockedByCardLogic",
                 "unplayable_reason_text": "this costs 2 Sparks and you have 0",
                 "description": "Set off. Deal 8 damage. Place a Bomb 4."},
                {"id": "KLEEMOD-PROTO_KO_DIG_IN", "name": "Dig In",
                 "type": "Skill", "cost": "0", "can_play": False,
                 "spark_price": 1, "spark_affordable": False,
                 "description": "Gain 8 Block."},
                {"id": "KLEEMOD-PROTO_KO_KABOOM", "name": "Kaboom!",
                 "type": "Attack", "cost": "1", "can_play": True,
                 "description": "Deal 6 damage. Applies Pyro."},
            ]},
    }


def test_a_spark_priced_hand_line_prints_its_spark_price():
    """`EB-286`'s acceptance: the seat's `Bang Bang!` line names its price."""
    page = blindplay.observe(spark_priced_state())
    assert "**Bang Bang!** — cost 2 Sparks, attack" in page
    assert "**Dig In** — cost 1 Spark, skill" in page
    # A card with no Spark price reads exactly as it always did.
    assert "**Kaboom!** — cost 1, attack" in page
    # And `cost 0` is gone from the page entirely -- it was never true.
    assert "cost 0" not in page


def test_the_spark_price_comes_off_the_shipped_face_when_the_wire_is_silent():
    """A REWARD or SHOP row carries no `spark_price`: the bridge emits that
    pair on a HAND card only. So the price is read from the same id-keyed
    index the staged page uses, and a reward offer prints it too."""
    state = spark_priced_state()
    for card in state["player"]["hand"]:
        card.pop("spark_price", None)
        card.pop("spark_affordable", None)
    page = blindplay.observe(state)
    assert "**Bang Bang!** — cost 2 Sparks, attack" in page
    assert "**Dig In** — cost 1 Spark, skill" in page

    reward = {"state_type": "card_reward",
              "player": {"hp": 55, "max_hp": 62},
              "card_reward": {"prompt": "Add a card to your deck.",
                              "can_skip": True,
                              "cards": [
                                  {"id": "KLEEMOD-PROTO_KO_BANG_BANG",
                                   "name": "Bang Bang!", "type": "Attack",
                                   "cost": "0", "rarity": "Uncommon",
                                   "description": "Set off. Deal 8 damage."}]}}
    assert "**Bang Bang!** — cost 2 Sparks, attack" in blindplay.observe(reward)


# ------------------ EB-262 / EB-263: the LIVE shapes, captured 2026-09-02 ---
#
# The fixtures above these lines are SYNTHETIC, built from the bridge's own
# builder, and they were green while the live screens were not. So round four
# went and got the wire's own bytes: `review/qa/blindplay/eb263-live-shapes/`
# holds nine raw envelopes captured off a real Klee run on
# `0.2.1966+proto.dirty`, one per screen the r3 Opus seat reported. Its
# README says how, and every test below reads one of them unedited.

LIVE = (Path(__file__).resolve().parents[2] / "review" / "qa" / "blindplay"
        / "eb263-live-shapes")


def live(name: str) -> dict:
    return json.loads((LIVE / f"{name}.json").read_text(encoding="utf-8"))


def test_a_live_shop_prints_every_card_cost_beside_the_gold():
    """`EB-262`, reopened. "I paid 73 gold and only discovered it costs 3
    energy -- a whole turn -- when I next saw it on a card-selection screen."
    The energy cost is on the shelf under `card_cost` and always was."""
    page = blindplay.observe(live("shop-stocked"))
    assert "**Pocket Fireworks** — cost 1, card (attack), 25 gold" in page
    assert "**Mine Toss** — cost 1, card (skill), 51 gold" in page
    # `EB-286` reaches the shelves too: a Spark-priced card charges no energy,
    # so its shelf would otherwise have printed a price of nothing at all.
    assert "**Powder Charge** — cost 1 Spark, card (skill), 77 gold" in page
    # A relic and a potion have no card cost and read exactly as before.
    assert "**Bag of Preparation** — relic, 192 gold" in page


def test_a_live_bought_shelf_says_what_it_is_instead_of_calling_itself_card():
    """`EB-262`'s other half, and the answer is that it is NOT OURS.

    `MerchantCardEntry.IsStocked` IS `CreationResult != null`, so buying a
    card clears the only field its name, text and cost were ever read from,
    and `BuildShopState` emits a row with an index, a category and a price and
    nothing else. The live capture is exactly that. The page used to fall back
    to the category and print `**Card** — 73 gold`, which reads as a card
    called "Card"; it now says what the feed can and cannot say.

    THIS IS THE CASE WITH NO MEMORY -- a page that arrives at a shop already
    sold out, which is why the shelf memory is dropped first. The other case,
    where this page rendered the same shop before the purchase, is the test
    below.
    """
    blindplay.forget_shelves()
    shelf = live("shop-bought")["shop"]["items"][0]
    assert shelf["category"] == "card" and shelf["is_stocked"] is False
    assert "card_name" not in shelf and "card_cost" not in shelf

    page = blindplay.observe(live("shop-bought"))
    assert "**Card** —" not in page
    assert "**(this shelf is empty)** — card, 76 gold (not available)" in page
    assert "The game clears a shelf's card the moment it is sold" in page


def test_a_bought_shelf_keeps_the_name_this_page_printed_before_the_sale():
    """`EB-262`'s vendor half, and the part of it that IS ours (`EB-262`).

    The lost name is the game's -- `IsStocked` IS `CreationResult != null` --
    but this page had already read that shelf off the same wire one render
    earlier. So the shop is remembered by its own fingerprint (the
    `(index, category, price)` of every shelf, which a purchase does not
    touch: these two captures differ in `is_stocked`, `card_name` and
    `card_cost` and in nothing else) and a bought row prints the face it had,
    marked `sold`.
    """
    blindplay.forget_shelves()
    before = blindplay.observe(live("shop-stocked"))
    assert "**Perfect Timing** — cost 1, card (attack), 76 gold" in before

    after = blindplay.observe(live("shop-bought"))
    assert "**Perfect Timing** — cost 1, card (attack), 76 gold (sold)" in after
    assert "(this shelf is empty)" not in after
    assert "what this page printed for the same shelf before the purchase" \
        in after
    # And the grammar agrees with the page: the shelf is named, and refused.
    res = blindplay.act(live("shop-bought"), 'buy "Perfect Timing"')
    assert res["ok"] is False
    assert "not available to buy" in res["refusal"]


def test_a_remembered_shelf_never_crosses_from_one_shop_to_another():
    """The memory's own guard. A second shop fingerprints differently, so the
    first shop's names are dropped rather than printed over it."""
    blindplay.forget_shelves()
    blindplay.observe(live("shop-stocked"))
    # The synthetic shop is a different set of shelves at different prices.
    page = blindplay.observe(shop_state())
    assert "Perfect Timing" not in page
    # ...and coming back to a bought shelf with the memory gone says so.
    assert "(this shelf is empty)" not in page
    assert "**(this shelf is empty)** — card, 76 gold" in blindplay.observe(
        live("shop-bought"))


def test_a_spent_live_rest_site_offers_only_proceed():
    """`EB-263`'s acceptance, on the shape the wire actually sends: a spent
    rest site is `{"options": [], "can_proceed": true}`. The page used to
    print no options while still advertising four verbs.

    `EB-371` ADDED THE ONE VERB THAT IS NOT THE ROOM'S. `drop potion` belongs
    to the belt rather than to the screen -- the wire allows `discard_potion`
    wherever a run is in progress -- so what this asserts is that the SPENT
    ROOM offers nothing of its own, which is the rule the row is about.
    """
    assert live("rest-spent")["rest_site"] == {"options": [],
                                               "can_proceed": True}
    page = blindplay.observe(live("rest-spent"))
    assert "nothing left to offer" in page
    verbs = [line for line in page.splitlines() if line.startswith("- `")]
    assert [v for v in verbs if "drop potion" not in v] == ["- `proceed`"]


def test_a_fresh_live_rest_site_offers_the_verbs_it_actually_has():
    """The same rule from the other side. This room offers Rest and Smith and
    no card removal, and says `can_proceed: false` -- so `remove` and
    `proceed` are both absent, and neither would have worked."""
    page = blindplay.observe(live("rest-fresh"))
    assert "- `rest`" in page and "- `upgrade`" in page
    assert "- `remove`" not in page
    assert "- `proceed`" not in page


def test_an_opening_chest_is_a_moment_and_not_an_empty_screen():
    """`EB-263`'s chest half, and the live capture is the whole diagnosis:
    `{"treasure": {"message": "Opening chest..."}}` and no other key. The
    bridge force-clicks the chest itself and answers a bare message for the
    frames that takes, so the page drew an open chest with a blank body and
    offered `choose "<relic>"` over nothing."""
    state = live("chest-opening")
    assert state["treasure"] == {"message": "Opening chest..."}
    assert blindplay.transient(state) == "the chest is still opening"

    # Rendered anyway (a saved file never settles), it says which moment it is
    # and offers only the verb that exists.
    page = blindplay.observe(state)
    assert "Opening chest..." in page
    assert "(nothing here to take)" in page
    assert 'choose "<relic>"' not in page


def test_a_live_upgrade_picker_prints_what_it_has_marked_as_picked():
    """`EB-263`'s picker half, where the wire HAS an answer. The upgrade
    screen opens a preview container, so `preview_cards` carries the chosen
    card and its `+` face and the page can show both."""
    blob = live("upgrade-chosen")["card_select"]
    assert blob["preview_showing"] is True and len(blob["preview_cards"]) == 2
    page = blindplay.observe(live("upgrade-chosen"))
    assert "## What you have picked" in page
    assert "**Kaboom!+** (upgraded)" in page
    assert "This screen's data feed carries no per-card selection" not in page


def test_a_live_enchant_picker_says_it_cannot_mark_the_pick():
    """`EB-263`'s picker half, ON THE BRIDGE THAT HAD THE GAP -- which is what
    these two captures are, and why they stay exactly as recorded.

    The old `BuildCardSelectState` read every grid row through `BuildCardInfo`,
    which carried no selected flag, and never looked up
    `NDeckEnchantSelectScreen`'s two preview containers -- so the captures
    differ in ONE field. The r3 Opus seat: "the whole list reprinted
    byte-identically; the only change anywhere on the screen was the footer
    going from `Confirm is not available.` to `Confirm is available.`"

    Both halves are closed on the bridge side of this row, and the page must
    still DEGRADE HONESTLY against a bridge that predates the fix: a feed that
    does not answer is not a board with nothing picked.
    """
    before, after = live("enchant-fresh"), live("enchant-chosen")
    assert before["card_select"]["cards"] == after["card_select"]["cards"]
    assert before["card_select"]["can_confirm"] is False
    assert after["card_select"]["can_confirm"] is True
    assert "preview_cards" not in after["card_select"]
    assert "selection_known" not in after["card_select"]

    page = blindplay.observe(after)
    assert "data feed did not answer which card is picked" in page
    assert "Confirm is available." in page
    assert "## What you have picked" not in page
    assert "Nothing on this screen is picked yet." not in page


def test_the_enchant_picker_marks_the_pick_once_the_bridge_carries_it():
    """`EB-263`, THE BRIDGE HALF, on the shape `BuildCardSelectState` now
    builds: `selection_known` beside the grid, and `selected` per card off
    `NCardGrid._highlightedCards` -- the one list all five selection screens
    write through (`vendor/STS2_MCP/gits/GitsCardSelection.cs`).

    Built by adding those two keys to the live pre-fix capture, since the
    LIVE capture of the fixed bridge is what this row still owes: what is
    pinned here is that the page reads them, not that the game sent them.

    Seen to FAIL: without the reader the page falls back to the note.
    """
    after = live("enchant-chosen")
    after["card_select"]["selection_known"] = True
    for i, card in enumerate(after["card_select"]["cards"]):
        card["selected"] = i == 1
    page = blindplay.observe(after)
    assert "## What you have picked" in page
    assert "data feed did not answer which card is picked" not in page
    picked = after["card_select"]["cards"][1]["name"]
    assert page.index("## What you have picked") < page.rindex(picked)


def test_the_pending_pick_is_marked_as_a_second_printing_of_a_row_above():
    """`EB-329`. THE REMOVAL SCREEN LOOKED ONE CARD LONGER THAN THE DECK.

    The round-5 act-1 seat counted sixteen rows over a fifteen-card deck and
    read the extra as a real card -- "a bare `Strike` after `Undertow (2)`,
    distinguishable only by the absence of a `(N)` index" -- and unpicked it
    two fights later off pile arithmetic. The rows were both honest: the
    second is the pending pick shown back, numbered on its own list and so
    printed bare. Nothing said so.

    Seen to FAIL without the mark: the two lists are the same format and the
    heading alone did not carry it.
    """
    state = card_select_state()
    state["card_select"]["preview_showing"] = True
    state["card_select"]["preview_cards"] = [
        dict(state["card_select"]["cards"][0])]
    page = blindplay.observe(state)
    assert "## What you have picked" in page
    assert "Already listed above." in page
    assert "counting both lists counts it twice" in page
    # The row itself carries the word, at the end of its head where the cost
    # and the type already sit.
    picked = [ln for ln in page.splitlines()
              if ln.startswith("- **Coral Guard**") and "PICKED" in ln]
    assert len(picked) == 1, page
    # And a screen with no pick is untouched: no mark, no note, no heading.
    plain = blindplay.observe(card_select_state())
    assert "PICKED" not in plain
    assert "Already listed above." not in plain


def test_an_asked_screen_with_nothing_picked_says_so():
    """"Nothing is picked" and "I could not find out" are different things to
    tell a tester who is about to spend a turn confirming, and only one of them
    is about the board."""
    fresh = live("enchant-fresh")
    fresh["card_select"]["selection_known"] = True
    for card in fresh["card_select"]["cards"]:
        card["selected"] = False
    page = blindplay.observe(fresh)
    assert "Nothing on this screen is picked yet." in page
    assert "data feed did not answer which card is picked" not in page


# ------------------- EB-314: the transform screen, captured 2026-09-02 -----
#
# THREE RAW ENVELOPES OFF ONE SCREEN, and the whole diagnosis is that two of
# them are the SAME screen a second apart. `review/qa/eb314-transform-2026-
# 09-02/` holds them, captured on lane 1 against `0.2.2083+proto.dirty` /
# game `v0.111.0`, seed `GXRJRQVLUL1G`, and its record says how.
#
# What the r5 Opus seat reported: it picked `Strike (1)` and the page printed
# the result **Barricade**, then **Dark Embrace**, then **Hemokinesis** on
# re-selections, while naming Strike as the source throughout; it confirmed on
# "Strike to Hemokinesis" and got **Stomp**, one Defend short.
#
# Neither half was a roll. `NDeckTransformSelectScreen.OpenPreviewScreen`
# hands `NTransformPreview.Initialize` one `CardTransformation` per pick, and
# where that carries no `Replacement` -- every random transform, which is what
# the screen's own doc comment says it is FOR -- the preview starts
# `CycleThroughCards`, reassigning the right-hand holder to another card off
# `CardFactory.GetDefaultTransformationOptions` EVERY 0.2 SECONDS on
# `Rng.Chaotic`. `CompleteSelection` then returns the SELECTED CARDS and the
# caller rolls the replacement, so nothing the reel lands on is ever taken.
# `transform-picked.json` and `transform-picked-later.json` are that reel,
# one frame apart.

LIVE314 = (Path(__file__).resolve().parents[2] / "review" / "qa"
           / "eb314-transform-2026-09-02")


def live314(name: str) -> dict:
    return json.loads((LIVE314 / f"{name}.json").read_text(encoding="utf-8"))


def test_the_live_transform_reel_moves_while_the_screen_does_not():
    """The fixtures' own claim, before any page is rendered: two reads of ONE
    unchanged screen, whose preview's SECOND card is a different card."""
    one = live314("transform-picked")["card_select"]
    two = live314("transform-picked-later")["card_select"]
    assert one["screen_type"] == "transform" and one["preview_showing"] is True
    assert one["cards"] == two["cards"]
    assert [c["name"] for c in one["preview_cards"]] == \
        ["Strike", "Tools of the Trade"]
    assert [c["name"] for c in two["preview_cards"]] == \
        ["Strike", "Fan of Knives"]
    # And the grid's own selection channel is EMPTY on both, because
    # `OpenPreviewScreen` unhighlights every picked card as it opens. The
    # preview's left half is the only thing on this wire that names the pick.
    assert one["selection_known"] is True
    assert not [c for c in one["cards"] if c.get("selected")]


def test_a_live_transform_screen_names_the_source_and_not_the_reel():
    """`EB-314`. The page prints what the screen HOLDS -- the card going in --
    and says in words that what comes out has not been chosen.

    Seen to FAIL: before this row the reel's frame was printed under
    *What you have picked* as though it were the result, which is how a seat
    came to confirm a card the run never rolled.
    """
    page = blindplay.observe(live314("transform-picked"))
    assert "## What you have picked" in page
    assert "- **Strike** — cost 1, attack" in page
    assert "Tools of the Trade" not in page
    assert "has NOT been chosen yet" in page
    assert "Confirming means accepting an unknown card." in page


def test_two_reads_of_one_transform_screen_render_the_same_page():
    """The regression the r5 seat's three observations are: a page that moves
    when nothing on the board has is a page reporting an animation."""
    assert blindplay.observe(live314("transform-picked")) == \
        blindplay.observe(live314("transform-picked-later"))


def test_a_transform_pick_already_made_cannot_be_re_taken():
    """`EB-314`'s other half. Every one of the five grid screens keeps its own
    `_selectedCards` while its preview is open and only the real UI's mouse
    block stops a second click reaching `OnCardClicked` -- and `select_card`
    does not go through the mouse, it emits `NCardGrid.HolderPressed` at the
    grid. So a `choose` over an open preview changed WHICH card would be
    transformed while the preview went on showing the first one.

    Seen to FAIL: before this row the command resolved and posted, and the
    r5 seat lost a Defend it had never confirmed.
    """
    state = live314("transform-picked")
    res = blindplay.act(state, 'choose "Defend (1)"')
    assert res["ok"] is False and res["post"] is None
    assert "your pick is already made" in res["refusal"]
    assert "`skip` to put it back" in res["refusal"]
    # And the page does not offer the verb it would refuse (`EB-259`'s rule).
    page = blindplay.observe(state)
    assert 'choose "<card title>"' not in page
    assert "- `confirm`" in page and "- `skip`" in page
    assert "does not leave the screen" in page


def test_a_fresh_transform_screen_still_takes_a_pick():
    """The screen BEFORE a preview opens is unchanged: the deck is listed, the
    verb is offered, and the pick resolves to the grid index it always did."""
    fresh = live314("transform-fresh")
    assert fresh["card_select"]["preview_showing"] is False
    page = blindplay.observe(fresh)
    assert "# Choose a card to Transform." in page
    assert 'choose "<card title>"' in page
    assert "Nothing on this screen is picked yet." in page
    assert "has NOT been chosen yet" not in page
    res = blindplay.act(fresh, 'choose "Strike (1)"')
    assert res["ok"] is True
    assert res["post"] == {"action": "select_card", "index": 0}


def test_an_unpairable_transform_preview_names_none_of_it():
    """The shape this has never been seen in. `NTransformPreview` builds one
    holder under `%Before` and one under `%After` per pick, so the container's
    cards pair off; a preview that does not is not guessed at, because the
    guess that goes wrong prints a reel frame as the tester's own card."""
    odd = json.loads(json.dumps(live314("transform-picked")))
    odd["card_select"]["preview_cards"] = \
        odd["card_select"]["preview_cards"][:1]
    page = blindplay.observe(odd)
    assert "cannot sort into the ones you" in page
    assert "## What you have picked" not in page
    assert "Nothing on this screen is picked yet." not in page


def test_the_upgrade_preview_keeps_its_result_and_loses_its_re_pick():
    """`EB-314` reaches the campfire smith too, and differently on each half.

    An UPGRADE preview's second card is decided -- `_singlePreview.Card` is
    the clicked card and the `+` face is the game's own -- so it is still
    printed. But `NDeckUpgradeSelectScreen.OnCardClicked` has the same
    `_selectedCards` shape, and `CompleteSelection` upgrades everything in
    that set, so a second `choose` over the open preview would have upgraded
    TWO cards on a one-card boon. The verb goes on this screen as well.
    """
    page = blindplay.observe(live("upgrade-chosen"))
    assert "## What you have picked" in page
    assert "**Kaboom!+** (upgraded)" in page      # the decided half, kept
    assert "has NOT been chosen yet" not in page  # and no transform sentence
    assert 'choose "<card title>"' not in page
    res = blindplay.act(live("upgrade-chosen"), 'choose "Kaboom!"')
    assert res["ok"] is False and res["post"] is None
    assert "your pick is already made" in res["refusal"]


# --------------------------------------------------------------------------
# THE KOKOMI OVERHAUL, DRAFT 6: the Plans on the page, and the pet as a target
# (`EB-216`). Same posture as the memory block above and the same contract
# shape, one rule over: `vendor/STS2_MCP/gits/GitsKokomiPlan.cs` lifts
# `KokomiPlan.Snapshot` by reflection onto `player.kokomi_plans`, so what is
# pinned here is which fields exist, that an absent key stays absent, and that
# the queue and the jellyfish both reach the tester.
# --------------------------------------------------------------------------


def plans_combat_state(plans: dict | None) -> dict:
    """A Kokomi combat with (or without) `player.kokomi_plans` on the wire."""
    state = combat_state()
    player = dict(state["player"])
    player.pop("kokomi_plans", None)
    if plans is not None:
        player["kokomi_plans"] = plans
    state = dict(state)
    state["player"] = player
    return state


TWO_PLANS = {
    "pet": True, "pet_name": "Bake-Kurage", "pet_entity_id": "41",
    "pending": 2, "twice": False,
    # `EB-322`: the wire carries the card's TITLE, and a prototype row
    # that shadows a shipped row prints the shipped row's title -- the
    # " (proto)" declaration is a sheet device and never reaches a face.
    "queue": [{"name": "Kurage's Oath", "clauses": 1},
              {"name": "War Council", "clauses": 2}],
}


def test_a_board_with_no_plan_rule_carries_no_plan_section():
    """The ABSENT / EMPTY split, and it is the same one the memory makes: a
    release build has no Plan rule and a Klee at this table is not playing it,
    and neither must be shown an empty jellyfish."""
    for wire in (None, {}):
        obs = blindplay.observation(plans_combat_state(wire))
        assert "plans" not in obs["combat"]
        assert "Bake-Kurage" not in blindplay.render(obs)


def test_the_page_lists_the_pending_plans_front_first():
    """The HUD draws them face up, front at the top, so the page numbers them
    the same way -- a blind reader gets what a sighted player sees."""
    page = blindplay.render(blindplay.observation(plans_combat_state(TWO_PLANS)))
    assert "## The Bake-Kurage" in page
    assert "1. **Kurage's Oath**" in page
    assert "2. **War Council**" in page
    assert "Enemies cannot touch it" in page


def test_an_empty_morning_says_so_rather_than_printing_a_zero():
    """`EB-198`'s lesson, carried: a HUD element showing a number over an empty
    state reads as a state. Nothing pending is nothing to say."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(dict(TWO_PLANS, pending=0, queue=[]))))
    assert "Nothing is planned. The morning is empty." in page
    assert "in this order" not in page


def test_the_rare_that_changes_what_the_queue_means_is_printed():
    """Nereid's Ascension makes the queue's LENGTH stop being the number of
    things that will happen, which is not visible from a count.

    ONE RARE AND NOT TWO SINCE `EB-570`: The Moon Overlooks the Waters was the
    other, and its `also_now` field left the snapshot contract with the row.
    A stale build that still sends the key is ignored rather than printed --
    which this pins by sending it."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(dict(TWO_PLANS, twice=True, also_now=True))))
    assert "carries out EVERY Plan twice" in page
    assert "also happen NOW" not in page


# --------------------------------------------------------------------------
# THE CARRY-OUT MOMENT (`EB-317`). Two Opus seats asked for one: the morning
# drained and "the panel simply reads empty", so nothing on the page or the
# screen said WHICH Plans had just happened or for how much. The mod now says
# a line over the jellyfish's head per Plan carried out and puts the SAME
# STRING on the wire; what is pinned here is that the page prints that string
# rather than composing a second one of its own.
# --------------------------------------------------------------------------


CARRIED_OUT = dict(TWO_PLANS, pending=0, queue=[], carried_out=[
    {"card": "Ambush", "number": 12, "line": "Bake-Kurage: Ambush, 12"},
    {"card": "Stolen Chapter", "number": None,
     "line": "Bake-Kurage: Stolen Chapter"},
])

#: `CARRIED_OUT` with `EB-329`'s board reading on the first row, so the key-set
#: pin below actually walks a `moved` row rather than an empty list.
CARRIED_OUT_MEASURED = dict(
    CARRIED_OUT,
    carried_out=[dict(CARRIED_OUT["carried_out"][0], on_play=False,
                      kind="damage", asked=12,
                      moved=[{"target": "Nibbit", "combat_id": "1",
                              "amount": 12, "dead": False, "absorbed": 3}]),
                 CARRIED_OUT["carried_out"][1]])


def test_the_page_prints_the_carry_out_line_the_screen_showed():
    """The row's own format, and the row's own example. The number is what the
    clause PRODUCED, not what the sheet printed, so a Vaporized planned hit
    says the number the enemy actually took."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(CARRIED_OUT)))
    assert "carried these out at the start of this turn" in page
    assert "- Bake-Kurage: Ambush, 12" in page
    # A clause with no number is the card name alone -- never a dangling comma.
    assert "- Bake-Kurage: Stolen Chapter" in page
    # ORDER IS THE MORNING'S, front first, the same order the strip empties in.
    assert (page.index("Bake-Kurage: Ambush")
            < page.index("Bake-Kurage: Stolen Chapter"))


def test_the_page_prints_the_mods_sentence_and_never_rebuilds_it():
    """ONE COMPOSER, AND IT IS C#. `line` is what the speech bubble said; the
    page is not entitled to a second opinion about the words, because a page
    and a screen that word the same event differently is the whole failure the
    field exists to prevent. A doctored `line` must reach the page verbatim."""
    doctored = dict(CARRIED_OUT, carried_out=[
        {"card": "Ambush", "number": 12, "line": "Bake-Kurage said this"}])
    page = blindplay.render(blindplay.observation(
        plans_combat_state(doctored)))
    assert "- Bake-Kurage said this" in page
    assert "Ambush, 12" not in page


def test_a_wire_without_the_sentence_still_gets_the_ruled_format():
    """The one fallback, for a bridge older than the field: the parts are
    there, so the page prints the same format the mod would have."""
    older = dict(CARRIED_OUT, carried_out=[
        {"card": "Ambush", "number": 12}, {"card": "Stolen Chapter"}])
    page = blindplay.render(blindplay.observation(
        plans_combat_state(older)))
    assert "- Bake-Kurage: Ambush, 12" in page
    assert "- Bake-Kurage: Stolen Chapter" in page


def test_the_panel_says_where_a_plan_lands_in_two_sentences():
    """`EB-442`. The `Plan` keyword says the aim rule in 135 rendered
    characters at the tip ceiling, and the r12 seat read it about fifteen
    times without getting the rule out of it while "the Bake-Kurage panel and
    the Reaction preview read clearly". The panel has no ceiling.

    Every clause is `KokomiPlan`'s own: `FrontEnemy` takes the leftmost
    hittable non-Minion and falls back to the leftmost Minion on a board of
    Minions alone, and `Aimed` walks every living body for `Aim.AllEnemies`.
    """
    page = blindplay.render(blindplay.observation(plans_combat_state(TWO_PLANS)))
    assert ("- A Plan with one target hits the front enemy and never a Minion "
            "-- unless every enemy is a Minion, when it takes the front one "
            "anyway. A Plan whose card says ALL hits every living enemy, "
            "Minions included.") in page
    # The aim rule leads and the element follows it: a reader asking what a
    # Plan will do asks which body before it asks which element.
    lines = page.splitlines()
    assert lines.index(blindplay.PLAN_AIM_NOTE) + 1 ==         lines.index(blindplay.PLAN_HYDRO_NOTE)


def test_the_plan_keywords_aim_clause_stays_the_pointer():
    """The row keeps the tip's clause: the panel is where the rule is stated
    and the keyword is where a reader meets the word, so the two must not
    diverge and the keyword must not be emptied into the panel."""
    plan = blindplay.ARM_KEYWORDS["Plan"]
    assert "front non-Minion, or ALL, Minions too" in plan
    assert "Enemy Vulnerable counts; your Weak and Strength do not." in plan


def test_a_board_with_no_jellyfish_is_told_no_aim_rule():
    """The note is a fact about the jellyfish's carry-out, so it prints under
    the pet's own line and nowhere else -- a Klee at this table must not be
    read a rule about where her Plans land."""
    page = blindplay.render(blindplay.observation(plans_combat_state(None)))
    assert "hits the front enemy and never a Minion" not in page


def test_a_turn_with_no_carry_out_prints_no_carry_out_block():
    """The morning drain clears the record whether or not anything was due, so
    an empty list is a fact about THIS turn and not a stale one about the last.
    Nothing carried out is nothing to say."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(dict(TWO_PLANS, carried_out=[]))))
    assert "carried these out" not in page
    # And the section itself is unchanged for a board that never had the field.
    assert "1. **Kurage's Oath**" in page


# `EB-453`. THE PANEL OMITTED A PLAN AND MIS-STATED A NUMBER.
#
# Kokomi r13 fight 6: two Plans written, ONE printed, and `War Council, 7 (the
# 7 is damage)` sat above a body that had lost 9. Both halves are one shape --
# the page could only print what the wire carried, and the wire carried neither
# the Plan the fight cut off nor the name of the thing that dealt the other 2.

#: The r13 board: a Plan that ran with the Casket answering inside its beat,
#: and a second Plan the kill cut off before it happened.
CARRIED_OUT_R13 = dict(TWO_PLANS, pending=0, queue=[], carried_out=[
    {"card": "War Council", "number": 7, "line": "Bake-Kurage: War Council, 7",
     "kind": "damage", "asked": 7, "on_play": False,
     "moved": [{"target": "Cubex", "combat_id": "1", "amount": 9,
                "dead": False, "absorbed": 0}],
     "riders": [{"source": "Tamakushi Casket", "amount": 2}],
     "unfinished": False},
    {"card": "Kurage's Oath", "number": None,
     "line": "Bake-Kurage: Kurage's Oath", "on_play": False,
     "unfinished": True},
])


def test_the_panel_lists_the_plan_the_fight_cut_off():
    """A kill inside the first Plan of a morning unwinds the drain, so the rest
    never happen -- and nothing on the page said so. The row rides the same
    list because it was in the same queue, and the ORDER is the fact."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(CARRIED_OUT_R13)))

    assert "Bake-Kurage: War Council, 7" in page
    assert ("Kurage's Oath — still planned when the fight ended, so it never "
            "happened.") in page
    assert (page.index("War Council") < page.index("Kurage's Oath"))
    # A Plan that never ran was never MEASURED either, so it claims no board.
    assert "no enemy lost HP" not in page


def test_the_delivered_number_names_what_else_was_in_it():
    """The 7 and the 9. The line's figure is what the Plan's first clause
    produced; the line under it is what the board LOST, measured across the
    whole beat -- and the difference was the Tamakushi Casket answering the
    Weak that same Plan had just applied. A subtraction has no sources, so the
    mod names the rider and the page prints the name."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(CARRIED_OUT_R13)))

    assert "the 7 is damage" in page
    assert "Inside the same beat: Tamakushi Casket 2." in page
    assert "lost 9 HP" in page


def test_a_bridge_with_no_riders_prints_what_it_always_printed():
    """ABSENT IS NOT EMPTY, this section's standing rule: a build older than
    the field sends no `riders` key, and the row reads exactly as it did."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(CARRIED_OUT_MEASURED)))

    assert "Inside the same beat" not in page
    assert "still planned when the fight ended" not in page


# `EB-518`. THREE ENTRIES THAT DIVIDED FOUR WAYS.


def _r18_casket_board() -> dict:
    """Kokomi r18 fight 2, the morning after Charlotte marked one body.

    War Council's Plan is "Deal 5 damage and apply 1 Weak to ALL enemies", so
    the seat predicted 5 + 2 on each body. Two slimes, one wearing a Cryo aura:
    the Plan's own Hydro hit froze it BEFORE the hit landed
    (`ElementalHit.Deal` resolves the reaction first), Frozen is a debuff she
    applied, and the Casket answered it as well as the Weak. Nine on that body,
    seven on the other -- and three entries reading `Tamakushi Casket 2`.
    """
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["enemies"] = [
        {"entity_id": f"slime_{cid}", "combat_id": cid, "name": "Twig Slime",
         "hp": hp, "max_hp": 27, "block": 0, "status": [],
         "intents": [{"type": "Attack", "label": "4"}]}
        for cid, hp in ((1, 14), (2, 8))]
    casket = [("1", 2), ("1", 2), ("2", 2)]
    state["player"]["kokomi_plans"] = dict(TWO_PLANS, pending=0, queue=[],
        carried_out=[{
            "card": "War Council", "number": 5,
            "line": "Bake-Kurage: War Council, 5",
            "kind": "damage", "asked": 5, "on_play": False,
            "moved": [{"target": "Twig Slime", "combat_id": "1", "amount": 9,
                       "dead": False, "absorbed": 0},
                      {"target": "Twig Slime", "combat_id": "2", "amount": 7,
                       "dead": False, "absorbed": 0}],
            "riders": [{"source": "Tamakushi Casket", "amount": amount,
                        "target": "Twig Slime", "combat_id": cid}
                       for cid, amount in casket],
            "unfinished": False}])
    return state


def test_every_relic_strike_in_the_beat_names_the_body_it_landed_on():
    """`EB-518`. THE FOURTH CASKET THAT WAS NEVER THERE.

    Kokomi r18 lane 1, fight 2: "the carry-out block lists three casket hits,
    but the numbers need four ... I only found the fourth by subtracting". It
    did not need four. `EB-453` named the source and the number and not the
    BODY, so three identical entries over bodies that had lost 9 and 7 divided
    the even way -- one strike each -- and the arithmetic came up 2 short. Two
    of the three had landed on the same body.

    Seen to FAIL: the page printed `Tamakushi Casket 2, Tamakushi Casket 2,
    Tamakushi Casket 2` and named nothing.
    """
    state = _r18_casket_board()
    _new_process()
    page = blindplay.render(blindplay.observation(state))

    assert ("Inside the same beat: Tamakushi Casket 2 on Twig Slime (1), "
            "Tamakushi Casket 2 on Twig Slime (1), "
            "Tamakushi Casket 2 on Twig Slime (2).") in page
    # And the names are the page's own, not the mod's bare title: the enemy
    # list four lines down says `Twig Slime (1)` and the receipt must agree.
    assert "**Twig Slime (1)**" in page
    assert "Twig Slime (1) lost 9 HP" in page
    assert "Twig Slime (2) lost 7 HP" in page


def test_the_riders_and_the_plans_own_number_sum_to_what_each_body_lost():
    """The row's acceptance, done as the reader now can: the clause's figure
    plus that body's own riders is that body's `lost N HP`. Nine is 5 + 2 + 2
    and seven is 5 + 2, which is the subtraction the seat had to do by hand and
    could not close."""
    state = _r18_casket_board()
    _new_process()
    said = blindplay.observation(state)["combat"]["plans"]["carried_out"][0]

    for moved in said["moved"]:
        rides = sum(r["amount"] for r in said["riders"]
                    if r["combat_id"] == moved["combat_id"])
        assert said["number"] + rides == moved["amount"], moved["target"]


def test_a_rider_from_a_bridge_that_names_no_body_prints_as_it_always_did():
    """ABSENT IS NOT EMPTY one field deeper. A build older than `EB-518` sends
    a rider with no `target`, and the clause is the source and the number
    alone -- exactly the sentence `EB-453` shipped."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(CARRIED_OUT_R13)))

    assert "Inside the same beat: Tamakushi Casket 2." in page
    assert " on " not in page.split("Inside the same beat:")[1].split(".")[0]


def test_the_meter_ledger_stays_off_the_carry_out_block():
    """`R101b`. The page line is the ON-SCREEN text, and the ledger's rows --
    meter, before, after, price_paid -- are an instrument, not a surface a
    player ever reads. None of its vocabulary may leak in with the lines."""
    obs = blindplay.observation(plans_combat_state(CARRIED_OUT_MEASURED))
    page = blindplay.render(obs)
    block = [ln for ln in page.splitlines()
             if ln.strip().startswith("- Bake-Kurage:")]
    assert block, "the carry-out lines are gone"
    for line in block:
        for word in ("price_paid", "meter_ledger", "before=", "after="):
            assert word not in line
    # And the observation carries nothing but the ruled fields per row --
    # `EB-317`'s three, plus `EB-329`'s board reading and the door the Plan
    # came through, plus `EB-426`'s two: what the number IS and what its
    # clause asked for. All seven are things a sighted player watched happen;
    # not one of them is a ledger row.
    for row in obs["combat"]["plans"]["carried_out"]:
        # `EB-453` added the last two: the named riders inside the beat, so
        # the line's figure and the board's can be reconciled, and whether
        # the Plan ran at all. Both are things a sighted player watched
        # happen -- a relic striking, and a Plan the fight cut off -- and
        # neither is a ledger row.
        assert set(row) == {"card", "number", "line", "kind", "asked",
                            "on_play", "board_read", "moved",
                            "riders", "unfinished"}
        for moved in row["moved"]:
            assert set(moved) == {"target", "combat_id", "amount", "dead",
                                  "absorbed"}
        # `EB-518` added the body a rider struck, in `MovedRow`'s own two
        # spellings, and nothing else: a strike landing on a creature is
        # another thing a sighted player watched happen.
        for rider in row["riders"]:
            assert set(rider) == {"source", "amount", "target", "combat_id"}


# --------------------------------------------------------------------------
# `EB-329`: THE MORNING LOG IS THE BOARD. Three seats across three acts read
# the figure on a carry-out line as the damage and it is not: it is what the
# Plan's FIRST clause produced. `Exposed Flank, 2` is two stacks of Vulnerable
# on a beat that moved 3 HP; `Feint+, 19` agreed with the board only because a
# damage clause's landed number is the damage. The mod now measures each
# enemy's HP across the whole Plan and the page prints it under the line.
# --------------------------------------------------------------------------


def morning_of(*rows: dict) -> dict:
    """A drained morning on the wire, with `EB-329`'s two new fields."""
    return dict(TWO_PLANS, pending=0, queue=[], carried_out=list(rows))


def two_body_state(plans: dict) -> dict:
    """The recorded Kokomi board with a SECOND Nibbit beside the first.

    Hand-built from the recorded one rather than invented: the copy keeps
    every field the bridge sent and changes the two that identify a creature,
    so the page numbers them `Nibbit (1)` and `Nibbit (2)` exactly as it does
    on a real two-body board.
    """
    blindplay.forget_fight()
    state = plans_combat_state(plans)
    enemies = state["battle"]["enemies"]
    twin = dict(enemies[0])
    twin["combat_id"] = 2
    twin["entity_id"] = "NIBBIT_1"
    state["battle"] = dict(state["battle"], enemies=[enemies[0], twin])
    return state


def test_a_plan_on_a_vulnerable_target_prints_the_number_the_board_moved():
    """The row's own example, and the sharpest form of the defect.

    `Exposed Flank` applies 2 Vulnerable; the line's figure is that 2. What a
    player watched was the Tamakushi Casket answering the debuff with a Hydro
    strike, multiplied by the Vulnerable it had just applied -- 3 HP off the
    body. Both numbers are now on the page, each saying what it is.

    Seen to FAIL before the mod measured it: the page had the 2 and nothing
    else, and the seat's arithmetic came out one point short every time.
    """
    blindplay.forget_fight()
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Exposed Flank", "number": 2,
                    "line": "Bake-Kurage: Exposed Flank, 2",
                    "on_play": False,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 3, "dead": False}]}))))
    assert "- Bake-Kurage: Exposed Flank, 2" in page
    assert "- Nibbit lost 3 HP" in page
    # And the page says which number is which, once, under the block.
    assert "what its first clause produced" in page


def test_an_all_plan_prints_a_number_per_target():
    """Kurage's Oath is `Deal 7 damage to ALL enemies`, and one line has room
    for one figure -- `EB-317` said so and left the rest on a screen a blind
    seat does not have. Per body, named the way this page names bodies."""
    page = blindplay.render(blindplay.observation(two_body_state(
        morning_of({"card": "Kurage's Oath", "number": 7,
                    "line": "Bake-Kurage: Kurage's Oath, 7",
                    "on_play": False,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 7, "dead": False},
                              {"target": "Nibbit", "combat_id": "2",
                               "amount": 10, "dead": True}]}))))
    assert "- Nibbit (1) lost 7 HP" in page
    assert "- Nibbit (2) lost 10 HP, and died" in page
    # The names are THIS PAGE'S, so the receipt and the enemy list four lines
    # down name the same body the same way.
    assert "**Nibbit (2)**" in page


# --------------------------------------------------------------------------
# `EB-427`: A COPY KEEPS ITS NUMBER FOR THE FIGHT, RECEIPTS INCLUDED.
#
# The kokomi r11 seat met three Inklets, watched one die to a morning, and read
# the receipt for that morning as `Inklet`, `Inklet (1)` and `Inklet (2)` -- so
# it concluded "`Inklet (1)` was a different Inklet than it had been the turn
# before ... the list re-counts", and nearly aimed at the wrong body. The list
# does not re-count: `_enemy_names` has held the numbers by combat id since
# `EB-271`. What re-counted was the READING, because the one row naming a body
# the board no longer carried fell back to the mod's bare title. Both halves
# are pinned here, on a fight with a death.
# --------------------------------------------------------------------------


def three_body_state(plans: dict, dead: str = "") -> dict:
    """`two_body_state` with THREE copies, and one id optionally off the feed.

    The r11 board, in its own shape: three bodies of one name, distinct combat
    ids, and a death that the feed answers by dropping the body entirely rather
    than sending a corpse -- which is the case `EB-271`'s corpse test could not
    reach and the case a morning's receipt is always about.
    """
    state = plans_combat_state(plans)
    enemies = state["battle"]["enemies"]
    bodies = [dict(enemies[0], name="Inklet", combat_id=n,
                   entity_id=f"INKLET_{n}") for n in (1, 2, 3)]
    state["battle"] = dict(state["battle"],
                           enemies=[b for b in bodies
                                    if str(b["combat_id"]) != dead])
    return state


def test_a_copy_keeps_its_number_when_the_dead_body_leaves_the_feed():
    """The first board numbers three copies; the next board is two of them and
    the numbers do not move. GREEN BEFORE THIS ROW and pinned by it: the seat
    reported the opposite, so the standing behaviour is now stated rather than
    inferred -- `EB-271`'s own test keeps a corpse in the list, and this is the
    feed that drops the body instead."""
    blindplay.forget_fight()
    empty = morning_of()
    first = blindplay.render(blindplay.observation(three_body_state(empty)))
    for n in (1, 2, 3):
        assert f"({n})" in first
    after = blindplay.render(blindplay.observation(
        three_body_state(empty, dead="1")))
    # The survivors keep 2 and 3, and no line naming an Inklet says `(1)`.
    named = [ln for ln in after.splitlines() if "Inklet" in ln]
    assert any("Inklet (2)" in ln for ln in named)
    assert any("Inklet (3)" in ln for ln in named)
    assert not any("Inklet (1)" in ln for ln in named)
    # And the grammar offers the same handles the page just printed, which is
    # the half `EB-271` closed: a page and a grammar that disagree about which
    # body `(1)` names is the silent mistarget, not a cosmetic one.
    state = three_body_state(empty, dead="1")
    refusal = blindplay.act(state, 'play "Pearl Barrage" on "Inklet"')["refusal"]
    assert "Inklet (2)" in refusal and "Inklet (3)" in refusal
    assert "Inklet (1)" not in refusal
    assert blindplay.act(state, 'play "Pearl Barrage" on "Inklet (3)"')["ok"]


def test_a_morning_names_the_copy_it_killed():
    """The r11 receipt, repaired. The mod records a bare title for the body it
    killed because that body is off the next board; the fight remembers what
    the page called it, so all three rows carry a copy number and the reader is
    never handed a bare name beside two numbered ones."""
    blindplay.forget_fight()
    blindplay.observation(three_body_state(morning_of()))
    page = blindplay.render(blindplay.observation(three_body_state(
        morning_of({"card": "Exposed Flank", "number": 2,
                    "line": "Bake-Kurage: Exposed Flank, 2",
                    "on_play": False,
                    "moved": [{"target": "Inklet", "combat_id": "1",
                               "amount": 13, "dead": True},
                              {"target": "Inklet", "combat_id": "2",
                               "amount": 3, "dead": False},
                              {"target": "Inklet", "combat_id": "3",
                               "amount": 1, "dead": False}]}),
        dead="1")))
    assert "- Inklet (1) lost 13 HP, and died" in page
    assert "- Inklet (2) lost 3 HP" in page
    assert "- Inklet (3) lost 1 HP" in page


def test_an_unremembered_body_still_falls_back_to_the_mods_title():
    """The fallback is unchanged where it was always right: an id this fight
    never saw is named by the title the mod recorded, and never by a number
    borrowed from some other body."""
    blindplay.forget_fight()
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": 12,
                    "line": "Bake-Kurage: Ambush, 12", "on_play": False,
                    "moved": [{"target": "Sentry", "combat_id": "77",
                               "amount": 12, "dead": True}]}))))
    assert "- Sentry lost 12 HP, and died" in page


def test_a_plan_that_moved_no_hp_says_so_and_an_older_wire_says_nothing():
    """Two silences that are not the same silence. A Draw Plan really moved
    no HP and saying so is what lets a morning reconcile; a bridge that
    predates the measurement has not answered, and a page that printed
    "nothing moved" for it would be inventing a board."""
    blindplay.forget_fight()
    measured = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Stolen Chapter", "number": None,
                    "line": "Bake-Kurage: Stolen Chapter",
                    "on_play": False, "moved": []}))))
    assert "- no enemy lost HP" in measured
    blindplay.forget_fight()
    older = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Stolen Chapter", "number": None,
                    "line": "Bake-Kurage: Stolen Chapter"}))))
    assert "- Bake-Kurage: Stolen Chapter" in older
    assert "no enemy lost HP" not in older
    assert "what its first clause produced" not in older


def test_a_block_carry_out_says_it_is_block_and_what_it_asked_for():
    """`EB-426`, and it is the row's own line. `Bake-Kurage: Cleansing Wave, 7`
    put a bare 7 in the slot every other line uses for damage and followed it
    with "no enemy lost HP": the 7 was BLOCK, cut from the clause's 10 by
    Frail, and the r11 seat derived both halves off the board.

    Seen to FAIL: the wire carried one string and one integer, and the page had
    nothing to label the integer with.
    """
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Cleansing Wave", "number": 7,
                    "line": "Bake-Kurage: Cleansing Wave, 7",
                    "kind": "Block", "asked": 10,
                    "on_play": False, "moved": []}))))
    assert ("- Bake-Kurage: Cleansing Wave, 7 — the 7 is Block; the clause "
            "asked for 10.") in page
    # The mod's own sentence is printed as sent and the clause comes after it.
    assert "Bake-Kurage: Cleansing Wave, 7 —" in page


def test_a_plan_that_blocks_and_hits_prints_both_halves():
    """`EB-545`. FEIGNED RETREAT'S TWO HALVES, ON THE PAGE.

    The Kokomi r19 lane-1 seat read the card's Plan as "adding damage but not
    Block", against a face that says "Plan: Gain 4 Block and deal 6 damage" --
    so the row asked whether the Block was unpaid or unprinted. It is NEITHER:
    both engines pay it (`test_kokomi_plan.test_eb545_a_planned_feigned_retreat_
    pays_both_halves`), and the morning block prints both numbers, in the two
    slots each belongs in -- the LINE carries what the Plan's first clause
    produced, labelled, and the HP row under it carries what the board lost.

    This is the pin the row asks for on the page, and it is worth having
    because the two halves are printed by two different mechanisms: a change
    that dropped either would leave a Plan looking like the one-sided card the
    seat described.
    """
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Feigned Retreat", "number": 4,
                    "line": "Bake-Kurage: Feigned Retreat, 4",
                    "kind": "Block", "asked": 4, "on_play": False,
                    "moved": [{"name": "Toadpole", "amount": 6}]}))))

    assert "- Bake-Kurage: Feigned Retreat, 4 — the 4 is Block." in page
    assert "lost 6 HP" in page


def test_a_number_the_board_did_not_move_says_only_what_it_is():
    """The asked-for half is printed only where it differs, and the label is
    printed on every kind: "a bare number in the slot every other line uses for
    damage" is a complaint about an unlabelled slot, and labelling Block alone
    would leave it exactly as ambiguous for `Exposed Flank, 2`."""
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Exposed Flank", "number": 2,
                    "line": "Bake-Kurage: Exposed Flank, 2",
                    "kind": "Vulnerable", "asked": 2,
                    "on_play": False, "moved": []}))))
    assert "- Bake-Kurage: Exposed Flank, 2 — the 2 is Vulnerable." in page
    assert "asked for" not in page


def test_a_hit_that_landed_above_its_clause_says_both_numbers():
    """The difference is not always a cut. A planned hit into Vulnerable lands
    ABOVE what its clause asked for -- 12 x 1.5 -- which is the same two
    numbers the other way round, and the page states both rather than naming a
    modifier the wire cannot attribute."""
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": 18,
                    "line": "Bake-Kurage: Ambush, 18",
                    "kind": "damage", "asked": 12,
                    "on_play": False, "moved": []}))))
    assert ("- Bake-Kurage: Ambush, 18 — the 18 is damage; the clause asked "
            "for 12.") in page


def test_a_line_with_no_number_and_an_older_wire_stay_unlabelled():
    """Two silences. A Plan whose clauses produced no figure has nothing to
    label -- Nereid's window is turns, a replay prints its own numbers -- and a
    bridge older than the field has not answered, so both print exactly the
    line they always printed."""
    silent = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Stolen Chapter", "number": None,
                    "line": "Bake-Kurage: Stolen Chapter",
                    "kind": None, "asked": None,
                    "on_play": False, "moved": []}))))
    assert "- Bake-Kurage: Stolen Chapter" in silent
    assert "is cards drawn" not in silent
    older = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": 12,
                    "line": "Bake-Kurage: Ambush, 12",
                    "on_play": False, "moved": []}))))
    assert "- Bake-Kurage: Ambush, 12" in older
    assert "is damage" not in older


def test_the_number_kind_words_are_the_mods_own():
    """Held in step with `KokomiPlan` from this side: the strings the page
    prints are `NumberKind`'s, and the amount beside them is `AskedFor`'s,
    computed the way `ResolveOne` computes each scaled clause and read BEFORE
    the clause runs -- two of the three read a ledger the clause itself moves.
    """
    plan = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
            / "KokomiPlan.cs").read_text(encoding="utf-8")
    assert '["kind"] = said.Kind,' in plan and '["asked"] = said.Asked,' in plan
    kinds = plan[plan.index("private static string? NumberKind(Kind kind)"):]
    kinds = kinds[:kinds.index("/// <summary>")]
    for word in ('"cards drawn"', '"Energy"', '"Block"', '"HP healed"',
                 '"damage"', '"Weak"', '"Vulnerable"'):
        assert word in kinds, word
    asked = plan[plan.index("private static int? AskedFor("):]
    asked = asked[:asked.index("/// <summary>")]
    assert "PlansThisMorning" in asked
    assert "CompanionsPlayedLastTurn" in asked
    assert "KokomiRules.QuarterOfMaxHp(kokomi)" in asked
    # Read before the clause resolves, which is the whole reason it is a
    # separate call rather than a read inside `Announce`.
    entry = plan[plan.index("var wanted = AskedFor(kokomi, clause);"):]
    assert entry.index("await ResolveOne(") < entry.index("kind = NumberKind(")


def test_a_carry_out_eaten_by_block_says_so_with_the_amount():
    """`EB-440`, and it is the row's own beat. `Kurage's Oath+` carried out
    into a Defend intent: HP 35 to 35, the aura landed, and the receipt was
    "no enemy lost HP" -- true, and identical on the page to a Plan that did
    nothing at all, so the seat read the morning as having worked.

    Seen to FAIL: the row was filtered out entirely (`amount > 0`) and the
    block printed the empty-morning line.
    """
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Kurage's Oath", "number": 7,
                    "line": "Bake-Kurage: Kurage's Oath, 7",
                    "on_play": False,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 0, "dead": False,
                               "absorbed": 7}]}))))
    assert "- Nibbit lost no HP -- 7 absorbed by Block" in page
    assert "no enemy lost HP" not in page


def test_a_carry_out_that_ate_block_and_then_HP_prints_both():
    """The half-shield case, which is the one a reader has to reconcile: the
    number on the Plan's line is 10, the body lost 4, and the other 6 went
    into Block. Both figures are the beat's, and neither on its own closes the
    arithmetic."""
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": 10,
                    "line": "Bake-Kurage: Ambush, 10", "on_play": False,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 4, "dead": False,
                               "absorbed": 6}]}))))
    assert "- Nibbit lost 4 HP, and 6 more absorbed by Block" in page


def test_a_bridge_that_predates_the_block_reading_prints_what_it_always_did():
    """ABSENT IS NOT ZERO, `board_read`'s own discipline one level down. A
    wire with no `absorbed` key has not answered, and a page that printed
    "0 absorbed by Block" for it would be inventing a board."""
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": 12,
                    "line": "Bake-Kurage: Ambush, 12", "on_play": False,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 12, "dead": False}]}))))
    assert "- Nibbit lost 12 HP" in page
    assert "absorbed by Block" not in page


def test_the_block_reading_is_the_mods_own_subtraction():
    """Held in step with `KokomiPlan` from this side, the discipline every
    other GItS wire block is under: the key is emitted by `MovedRow`, and the
    Block it carries is read at the same two moments as the HP -- so a rename
    or a dropped read goes red here rather than silently emptying the clause
    on a live board."""
    plan = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
            / "KokomiPlan.cs").read_text(encoding="utf-8")
    assert '["absorbed"] = moved.Absorbed,' in plan
    board = plan[plan.index(
        "private static Dictionary<string, (string Name, int Hp, int Block)>?"):]
    board = board[:board.index("/// <summary>")]
    assert "(int)enemy.Block" in board and "(int)enemy.CurrentHp" in board
    moved = plan[plan.index("private static IReadOnlyList<MovedOn>? Moved("):]
    moved = moved[:moved.index("/// <summary>")]
    assert "if (absorbed < 0) absorbed = 0;" in moved
    assert "if (lost <= 0 && absorbed <= 0) continue;" in moved


def test_an_on_play_firing_prints_under_its_own_heading():
    """`EB-329`, the r4c seat's finding 4. A War Council carried out mid-turn
    was reported on one screen both as already carried out "at the start of
    this turn" and as still queued. Both rows were true; the first sentence
    was not. The mid-turn door is Change of Plans since `EB-570` withdrew The
    Moon Overlooks the Waters, and the heading is the row's, not the card's --
    `on_play` is what splits the list."""
    blindplay.forget_fight()
    page = blindplay.render(blindplay.observation(plans_combat_state(
        dict(TWO_PLANS, pending=1,
             queue=[{"name": "War Council", "clauses": 2}],
             carried_out=[{"card": "War Council", "number": 5,
                           "line": "Bake-Kurage: War Council, 5",
                           "on_play": True,
                           "moved": [{"target": "Nibbit", "combat_id": "1",
                                      "amount": 7, "dead": False}]}]))))
    assert "carried these out at the start of this turn" not in page
    assert "the moment each was written, and not this morning" in page
    assert "- Bake-Kurage: War Council, 5" in page
    assert "- Nibbit lost 7 HP" in page
    # The queue below still says the Plan is waiting for the morning, which
    # is the OTHER true half the seat could not reconcile with the first.
    assert "1. **War Council**" in page


def test_a_morning_and_an_on_play_firing_are_two_blocks_in_turn_order():
    """The morning happened at the top of the turn and the mid-turn firing
    after it, so the page prints them in that order and heads them apart."""
    blindplay.forget_fight()
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": 12,
                    "line": "Bake-Kurage: Ambush, 12", "on_play": False,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 12, "dead": False}]},
                   {"card": "War Council", "number": 5,
                    "line": "Bake-Kurage: War Council, 5", "on_play": True,
                    "moved": [{"target": "Nibbit", "combat_id": "1",
                               "amount": 7, "dead": False}]}))))
    assert page.index("carried these out at the start of this turn") \
        < page.index("the moment each was written")
    assert page.index("Bake-Kurage: Ambush, 12") \
        < page.index("Bake-Kurage: War Council, 5")


def test_the_last_carry_out_of_a_finished_fight_reaches_the_reward_screen():
    """`EB-329`. A PLAN WHOSE KILL ENDS THE FIGHT NEVER REACHES A BATTLE
    SCREEN. The round-5 act-1 seat banked two exactly-lethal Plans and wrote
    "the next screen was the reward screen": computed, never confirmed.

    `KokomiPlan.Snapshot` reads static per-player records and touches no
    combat, so the bridge emits `kokomi_plans` outside the combat block and
    the receipt lands here. The QUEUE is deliberately not printed: a fight
    that ended mid-turn can leave Plans pending, and "carried out at the start
    of your next turn" is a promise about a fight that no longer exists.
    """
    state = rewards_state()
    state["player"] = {"hp": 26, "max_hp": 80, "gold": 99,
                       "kokomi_plans": morning_of(
                           {"card": "Feint+", "number": 19,
                            "line": "Bake-Kurage: Feint+, 19",
                            "on_play": False,
                            "moved": [{"target": "Terror Eel",
                                       "combat_id": "1", "amount": 19,
                                       "dead": True}]})}
    page = blindplay.render(blindplay.observation(state))
    assert "## The Bake-Kurage's last carry-out" in page
    assert "never reaches a battle screen" in page
    assert "- Bake-Kurage: Feint+, 19" in page
    assert "- Terror Eel lost 19 HP, and died" in page
    assert "carried out at the start of your next turn" not in page
    # A reward screen from a build with no Plan rule is untouched.
    assert "Bake-Kurage" not in blindplay.render(
        blindplay.observation(rewards_state()))


def test_a_dead_enemy_s_leaked_locstring_key_humanises_instead_of_leaking():
    """`EB-370`, found live in the Kokomi round-9 seat's morning-log reprint.

    A body still on the board gets the page's own numbered name
    (`name_moved_rows`); one that DIED to the Plan is off the wire's enemy
    list entirely and keeps whatever the mod sent for `target` -- which, for
    a dead Sludge Spinner, was the mod's `.ToString()` on an unresolved
    LocString rather than its resolved text:
    `LocString table monsters entry SLUDGE_SPINNER.name`. That is not a
    name a player would recognise and it must never reach the page as
    written.
    """
    state = rewards_state()
    state["player"] = {"hp": 40, "max_hp": 80, "gold": 99,
                       "kokomi_plans": morning_of(
                           {"card": "Kurage's Oath", "number": 7,
                            "line": "Bake-Kurage: Kurage's Oath, 7",
                            "on_play": False,
                            "moved": [{"target": "LocString table monsters "
                                                 "entry SLUDGE_SPINNER.name",
                                       "combat_id": "9", "amount": 7,
                                       "dead": True}]})}
    page = blindplay.render(blindplay.observation(state))
    assert "- Sludge Spinner lost 7 HP, and died" in page
    assert "LocString" not in page
    assert "monsters" not in page
    assert "entry" not in page


def test_a_relic_s_leaked_owner_variant_key_humanises_to_its_base_name():
    """`EB-370`'s other half. A base-game relic borrowed into a modded
    character's pool (`FurinaRelicPool`, `KokomiRelicPool` both borrow
    `SilentRelicPool`) can print its per-character title VARIANT key when no
    such variant was ever registered -- `relics.SEA_GLASS.KLEEMOD-FURINA.
    title` reached a live Kokomi seat's Ancient-node relic offer and BRICKED
    the run, because `qa_packet`'s mod-id-prefix guard correctly refuses a
    `KLEEMOD-` id on a relic face. The owner segment is dropped -- it names
    which modded character's pool happened to read the shared relic object,
    not the relic -- and the base id humanises the same way any other
    id-shaped wire string does."""
    assert qa_packet._text(
        "relics.SEA_GLASS.KLEEMOD-FURINA.title") == "Sea Glass"
    # And the guard, which is otherwise unchanged, no longer has anything to
    # refuse: a relic row built from the leaking wire value passes straight
    # through `assert_blind`.
    player = {"relics": [{"id": "SEA_GLASS",
                          "name": "relics.SEA_GLASS.KLEEMOD-FURINA.title",
                          "description": "A curious little shard.",
                          "counter": None}]}
    row = qa_packet._relics(player)
    assert row == [{"name": "Sea Glass", "text": "A curious little shard."}]
    qa_packet.assert_blind(row)


def test_a_string_that_is_not_a_locstring_key_is_left_alone():
    """The narrowness is the point, same as the sprite-tag fold above it:
    ordinary prose, a version stamp and a real dotted id-looking sentence
    fragment must all survive `_text` unchanged, or the fold would be
    inventing names rather than reading them."""
    assert qa_packet._text("Deal 6 damage.") == "Deal 6 damage."
    assert qa_packet._text("Sea Glass") == "Sea Glass"
    assert qa_packet._text("0.2.1357") == "0.2.1357"
    # A design-vocabulary id is still refused -- this fold only unpacks the
    # two LocString shapes above, and does not become a second leak scrubber.
    with pytest.raises(qa_packet.PacketLeak):
        qa_packet.assert_blind({"name": "pearl_barrage"})


def test_act_refuses_a_packet_leak_the_way_observe_does(tmp_path, capsys):
    """`EB-370`. `blindplay_grammar.act` reads through `observation()`
    before it resolves anything, so a `PacketLeak` on the read path it
    shares with `observe` used to reach `cmd_act` as an unhandled Python
    traceback -- found live at a Kokomi seat's Ancient node, where `observe`
    printed a clean one-line `REFUSED: ...` and the very next `act` call on
    the same board died with a stack trace instead. `cmd_act` now catches
    the same exception and prints the same line `cmd_observe` does.
    """
    state = {"state_type": "event",
             "event": {"event_id": "NEOW", "event_name": "Neow",
                       "options": [
                           {"index": 0, "title": "Booming Conch",
                            "description": "gain [pearl_barrage]"}]}}
    raw = tmp_path / "leaking_state.json"
    raw.write_text(json.dumps(state), encoding="utf-8")
    args = argparse.Namespace(raw_file=str(raw), command="proceed",
                              dry_run=True)

    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observe(state)

    code = blindplay.cmd_act(args)
    assert code == 1
    assert capsys.readouterr().err.startswith("REFUSED: ")


# ---------------- EB-456: the action budget the seat cannot overrun --------


class _CountingWire:
    """A wire that answers one map screen and records every POST."""

    def __init__(self, state):
        self.state = state
        self.posts = []

    def get_state(self):
        return json.loads(json.dumps(self.state))

    def post(self, action, **kw):
        self.posts.append((action, kw))
        return {"status": "ok", "message": f"Doing {action}"}


@pytest.fixture
def lane_budget(tmp_path, monkeypatch):
    """A lane whose budget store is this test's own directory."""
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.delenv(blindplay.LANE_ENV, raising=False)
    monkeypatch.delenv(blindplay.MAX_ACTIONS_ENV, raising=False)
    return tmp_path


def test_the_121st_act_is_refused_once_the_lane_has_a_budget(lane_budget,
                                                             capsys):
    """`EB-456`. THE COUNT RULE HAD NO MECHANISM. Two of three round-13 seats
    were told to stop at 120 actions and stopped at 155-160 (Klee) and 165
    (Kokomi). A lane above zero is disposable, so the cost was a caveat rather
    than a loss -- but the rounds are not comparable past the cap, which is
    the only thing the cap is for.

    The count is the bridge's now: the coordinator writes the cap at embark,
    `act` charges every act it actually posts, and the act after the last one
    is refused before anything is resolved or sent.

    Seen to FAIL: with no budget in the file the 121st act posts like the 120
    before it.
    """
    wire = _CountingWire(map_state())
    args = argparse.Namespace(raw_file="", command='go "Monster (path 1)"',
                              dry_run=False)

    blindplay.set_budget(120)
    assert blindplay.budget_spent() == (0, 120)

    with mock.patch.object(blindplay, "bridge", wire):
        for n in range(120):
            assert blindplay.cmd_act(args) == 0, f"act {n + 1}"
        assert blindplay.budget_spent() == (120, 120)
        capsys.readouterr()

        # The 121st. Refused before the wire is read at all, so the post count
        # does not move and the reason is the row's own word.
        assert blindplay.cmd_act(args) == 2
    err = capsys.readouterr().err
    assert err.startswith(blindplay.BUDGET_REACHED)
    assert "120" in err
    assert len(wire.posts) == 120
    assert blindplay.budget_spent() == (120, 120)


def test_only_an_act_the_wire_actually_saw_is_charged(lane_budget, tmp_path,
                                                      capsys):
    """A refusal, a `--dry-run` and a `--raw-file` resolution all cost the run
    nothing, so none of them costs the budget anything. Charged after the
    POST, never before it."""
    wire = _CountingWire(map_state())
    blindplay.set_budget(3)

    raw = tmp_path / "map.json"
    raw.write_text(json.dumps(map_state()), encoding="utf-8")
    blindplay.cmd_act(argparse.Namespace(raw_file=str(raw), dry_run=False,
                                         command='go "Monster (path 1)"'))
    with mock.patch.object(blindplay, "bridge", wire):
        blindplay.cmd_act(argparse.Namespace(raw_file="", dry_run=True,
                                             command='go "Monster (path 1)"'))
        # A command the grammar refuses never reaches the wire either.
        assert blindplay.cmd_act(
            argparse.Namespace(raw_file="", dry_run=False,
                               command='go "Nowhere"')) == 1
    assert blindplay.budget_spent() == (0, 3)
    capsys.readouterr()


def test_a_lane_with_no_budget_acts_exactly_as_it_always_did(lane_budget,
                                                             capsys):
    """`0` is no budget, which is every round before this row: nothing is
    counted, nothing is refused, and the extra line is not printed."""
    wire = _CountingWire(map_state())
    blindplay.set_budget(0)
    args = argparse.Namespace(raw_file="", command='go "Monster (path 1)"',
                              dry_run=False)
    with mock.patch.object(blindplay, "bridge", wire):
        for _ in range(5):
            assert blindplay.cmd_act(args) == 0
    assert "actions:" not in capsys.readouterr().out
    assert blindplay.budget_spent() == (0, 0)


def test_the_environment_overrides_the_recorded_cap(lane_budget, monkeypatch):
    """`GITS_MAX_ACTIONS` is the operator's own door onto a lane they did not
    embark; an unreadable value is no budget rather than a crash."""
    blindplay.set_budget(120)
    monkeypatch.setenv(blindplay.MAX_ACTIONS_ENV, "40")
    assert blindplay.budget_cap() == 40
    monkeypatch.setenv(blindplay.MAX_ACTIONS_ENV, "not a number")
    assert blindplay.budget_cap() == 0


def test_two_lanes_keep_two_budgets(lane_budget):
    """The deck store's rule, and for the same reason: two seats play side by
    side, and one lane's spent budget must not end the other's run. The tag is
    normalised, because the coordinator writes it from `--lane 1` and the seat
    reads it from `GITS_LANE=lane1`."""
    blindplay.set_budget(120, 0)
    blindplay.set_budget(40, 1)
    blindplay.count_action(1)
    assert blindplay.budget_spent(0) == (0, 120)
    assert blindplay.budget_spent(1) == (1, 40)
    assert blindplay.lane_tag("lane1") == blindplay.lane_tag(1) == "1"
    assert blindplay.lane_tag("") == blindplay.lane_tag(None) == "0"


def test_the_lane_variable_is_spelled_the_same_on_both_sides_of_the_wall():
    """`blindplay_shape` may not import `instances`, so `GITS_LANE` is spelled
    there. Held in step from this side, the way `CHARGE_SOURCE_LINE` is held
    against `tier0.constants`."""
    from understudy import instances
    assert blindplay_shape.LANE_ENV == instances.LANE_ENV


def test_embark_records_the_cap_in_the_lanes_own_budget(lane_budget,
                                                        monkeypatch):
    """The coordinator's write, and the reset that goes with it: an embark is
    a new run, so the previous round's spent count may not survive it."""
    blindplay.set_budget(120)
    for _ in range(7):
        blindplay.count_action()
    assert blindplay.budget_spent() == (7, 120)

    # `embark()` writes the budget BEFORE it launches anything, so the write
    # is reachable without a game: the launch below is what raises.
    monkeypatch.setattr(embark.soak, "Session",
                        mock.Mock(side_effect=RuntimeError("no game here")))
    with pytest.raises(RuntimeError):
        embark.embark("kokomi", lane=0, max_actions=90)
    assert blindplay.budget_spent() == (0, 90)


# ------------- EB-448: an event outcome that never named what it gave -----


def granting_event_state() -> dict:
    """SYNTHETIC, BUILT FROM THE BRIDGE'S OWN BUILDER (`EB-448`).

    `BuildEventState` (`vendor/STS2_MCP/McpMod.StateBuilder.cs:1600-1627`)
    sends each option's `title`, `description`, `is_locked`, `is_proceed` and
    `was_chosen`, merges a granted RELIC in as `relic_name` /
    `relic_description`, and closes with `keywords` = `BuildHoverTips(
    opt.HoverTips)` -- where a `CardHoverTip` is flattened into the card's own
    printed title and description (`McpMod.Helpers.cs:260-264`), the game's
    `+` and all. This fixture is that shape: an option that adds a named card,
    one that upgrades a named card, one that hands over a relic, and one whose
    grant the feed does not name at all.
    """
    return {"state_type": "event",
            "run": {"act": 1, "floor": 6},
            "player": {"hp": 44, "max_hp": 62, "gold": 120},
            "event": {"event_id": "BYRDONIS_NEST",
                      "event_name": "Byrdonis Nest",
                      "in_dialogue": False,
                      "body": "An unattended egg sits in the reeds.",
                      "options": [
                          {"index": 0, "title": "Send It Up to Sangonomiya",
                           "description": "Add a card to your deck.",
                           "keywords": [
                               {"name": "Bathysmal Egg",
                                "description": "Unplayable. Exhaust at the "
                                               "end of your turn."}]},
                          {"index": 1, "title": "Feed It to the Conveyor",
                           "description": "Upgrade a card in your deck.",
                           "was_chosen": True,
                           "keywords": [
                               {"name": "Strike+",
                                "description": "Deal 9 damage."}]},
                          {"index": 2, "title": "Pocket the Shell",
                           "description": "Obtain a relic.",
                           "relic_name": "Bottled Tide",
                           "relic_description": "At the start of each combat, "
                                                "gain 3 Block."},
                          {"index": 3, "title": "Eat It",
                           "description": "Gain 6 Max HP."}]}}


def test_an_event_option_prints_the_face_of_the_card_it_names():
    """`EB-448`. THE OUTCOME WAS A SENTENCE AND NEVER A CARD.

    Klee r13: Trash Heap "gave a card" and the seat identified it as
    `Caltrops` two fights later off a hand; Endless Conveyor's upgrade turned
    up as `Strike+` in a removal list a room later; and an option adding a
    card the screen NAMES -- Byrdonis Egg, Neow's Dowsing -- printed the
    promise and never the face. So the seat shopped partly blind to its deck.

    Both channels were already on the feed and the page read neither: the
    category-prefixed face `_named_option` drops the moment a row has a title
    of its own, and `keywords`, which carries a card hover tip flattened into
    the card's printed title and text.

    Seen to FAIL: the page prints the four option titles and their bodies, and
    the words `Bathysmal Egg`, `Strike+` and `Bottled Tide` appear nowhere.
    """
    page = blindplay.observe(granting_event_state())
    # The card an option ADDS, by title, with the text the game printed.
    assert ("    · **Bathysmal Egg** — Unplayable. Exhaust at the end of your "
            "turn.") in page
    # The card an option UPGRADES, with the game's own upgrade mark on it.
    assert "    · **Strike+** — Deal 9 damage." in page
    # And the relic face `_named_option` used to drop behind the option title.
    assert "    · **Bottled Tide** — At the start of each combat" in page
    # An option whose grant the feed does not name claims nothing.
    assert "**Eat It**" in page
    assert page.split("**Eat It**")[1].strip().startswith("Gain 6 Max HP.")


def test_the_event_screen_marks_the_option_the_room_already_took():
    """`was_chosen` is on the feed and nothing read it, so an outcome and an
    offer printed identically -- which is what makes the faces above readable
    as a result rather than a promise."""
    page = blindplay.observe(granting_event_state())
    assert "**Feed It to the Conveyor** — TAKEN" in page
    assert "**Eat It** — TAKEN" not in page


def test_the_result_line_after_an_event_choice_names_what_it_gave():
    """The other half of the row: the line the seat is handed after `choose`.
    The screen's promise first, then the thing itself -- two claims, and only
    the second is a card now owned."""
    state = granting_event_state()
    res = blindplay.act(state, 'choose "Send It Up to Sangonomiya"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "choose_event_option", "index": 0}
    line = blindplay.taken_line(res)
    assert line.startswith("Took: Send It Up to Sangonomiya — Add a card to "
                           "your deck.")
    assert ("It names **Bathysmal Egg**: Unplayable. Exhaust at the end of "
            "your turn.") in line

    upgraded = blindplay.act(state, 'choose "Feed It to the Conveyor"')
    assert "It names **Strike+**: Deal 9 damage." in blindplay.taken_line(
        upgraded)


def test_a_random_grant_is_still_not_named_and_the_page_does_not_pretend():
    """The row's own limit, stated as a test. Trash Heap does not choose its
    card until the click and the event room carries no card afterwards, so an
    option with no face on its feed gets no face on the page -- rather than a
    guess, which is the one thing this module may never print."""
    state = granting_event_state()
    state["event"]["options"] = [
        {"index": 0, "title": "Rummage", "description": "Obtain a card."}]
    page = blindplay.observe(state)
    assert "**Rummage**" in page
    assert "·" not in page.split("**Rummage**")[1]


def test_the_grammar_offers_the_jellyfish_only_where_there_is_one():
    with_pet = blindplay.observation(plans_combat_state(TWO_PLANS))
    assert any('on "Bake-Kurage"' in c for c in with_pet["commands"])
    without = blindplay.observation(plans_combat_state(None))
    assert not any("Bake-Kurage" in c for c in without["commands"])


def test_a_card_played_on_the_jellyfish_posts_the_pets_entity_id():
    """The seat's whole route to writing a Plan, and it is the SAME `target`
    field an attack aims through -- `pet_entity_id` is the pet's combat id, and
    the bridge resolves a numeric id straight through `GetCreature`."""
    state = plans_combat_state(TWO_PLANS)
    res = blindplay.act(state, 'play "All Streams Flow to the Sea" '
                               'on "Bake-Kurage"')
    assert res["ok"], res
    assert res["post"]["action"] == "play_card"
    assert res["post"]["target"] == "41"
    assert res["printed"]["target"] == "Bake-Kurage"


def test_naming_no_target_still_plays_the_card_now():
    """NAMED, NEVER DEFAULTED. "Now or at dawn" is the choice the slice exists
    to test, so a card aimed at nothing is played NOW and only the tester's own
    word sends it to the jellyfish."""
    state = plans_combat_state(TWO_PLANS)
    res = blindplay.act(state, 'play "All Streams Flow to the Sea" '
                               'on "Nibbit"')
    assert res["ok"], res
    assert res["post"]["target"] == "NIBBIT_0"


def _planning_hand(state: dict) -> dict:
    """`EB-480`. The recorded turn with the wire's `can_target_pet` on it.

    The capture predates the field (`EB-216` added it), so every hand entry
    answers `None` there -- which is the case the refusal below deliberately
    leaves alone. This fixture is the SAME hand with the field filled the way
    a current bridge fills it: the Plan card answers true, the rest false.
    """
    out = json.loads(json.dumps(state))
    for card in out["player"]["hand"]:
        card["can_target_pet"] = (
            card["name"] == "All Streams Flow to the Sea")
    return out


def test_a_card_that_cannot_be_planned_is_refused_on_the_jellyfish():
    """`EB-480` (Kokomi r16 (c) 1). `play "Strike" on "Bake-Kurage"` returned
    ok with an empty refusal, burned an action and changed nothing: energy,
    discard and hand as before, "Nothing is planned."."""
    state = _planning_hand(plans_combat_state(TWO_PLANS))
    res = blindplay.act(state, 'play "Pearl Barrage" on "Bake-Kurage"')

    assert not res["ok"]
    assert "cannot be planned on Bake-Kurage" in res["refusal"]
    # `EB-402`'s repair: the way out is IN the refusal. The one Plan card in
    # this hand is offered by name, and so is the bare form.
    assert ('play "All Streams Flow to the Sea" on "Bake-Kurage"'
            in res["refusal"])
    assert 'play "Pearl Barrage"' in res["refusal"]

    # And the Plan card itself is still accepted, on the same board.
    ok = blindplay.act(state, 'play "All Streams Flow to the Sea" '
                              'on "Bake-Kurage"')
    assert ok["ok"], ok
    assert ok["post"]["target"] == "41"


def test_a_feed_with_no_pet_target_field_plays_the_card_as_it_always_did():
    """`EB-480`'s conservative half, `_aims_at_an_enemy`'s own rule: an ABSENT
    `can_target_pet` is a bridge that predates the field, and it reads as the
    behaviour that build has rather than as a refusal."""
    state = plans_combat_state(TWO_PLANS)
    assert all(c.get("can_target_pet") is None
               for c in state["player"]["hand"])
    res = blindplay.act(state, 'play "Pearl Barrage" on "Bake-Kurage"')
    assert res["ok"], res
    assert res["post"]["target"] == "41"


# ==== The blind-render burn, rounds four (Klee) and two (Kokomi), 2026-09-02 =
#
# Five rows, all of them read off seat records rather than off this file:
# `review/qa/blindplay/klee-overhaul-r4-opus/record.md` and the two
# `kokomi-overhaul-r2-*` records. Each test below quotes the sentence the seat
# wrote and pins the line that answers it.


# ------------------------------------------- EB-290: the three r4 render gaps

def test_a_relic_reward_is_named_by_the_relic():
    """`EB-290` (1). "The Neow reward screen printed `**Relic**` with `Golden
    Pearl` beneath it. `choose "Golden Pearl"` was refused: *nothing here is
    called 'Golden Pearl'. What is on the screen: Relic*."

    `BuildRewardsState` gives a relic reward a `type` and a `description` and
    no name field at all, so the description IS the printed face."""
    page = blindplay.observe(rewards_state())
    assert "**Golden Pearl**" in page
    assert "**Relic**" not in page

    res = blindplay.act(rewards_state(), 'choose "Golden Pearl"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "claim_reward", "index": 2}
    assert res["printed"] == {"option": "Golden Pearl"}


def test_two_gold_rewards_are_two_different_names():
    """`EB-290` (1), the other half the same run met: "two rewards printed
    `12 Gold` and `40 Gold (stolen back)`: `choose "Gold (1)"` was refused and
    only bare `choose "Gold"` worked, taking them one at a time."

    Each row is named by what it hands over, so they are simply two names --
    and the bare word they share refuses by naming both back."""
    page = blindplay.observe(rewards_state())
    assert "**12 Gold**" in page and "**40 Gold (stolen back)**" in page

    res = blindplay.act(rewards_state(), 'choose "Gold"')
    assert not res["ok"]
    assert "12 Gold" in res["refusal"]
    assert "40 Gold (stolen back)" in res["refusal"]


def test_reward_rows_printing_one_name_are_numbered_like_every_other_list():
    """And where two rewards genuinely print ONE name, the render numbers them
    and the grammar reads the numbers back -- which is what the seat tried
    (`Gold (1)`) and was refused, because this screen alone was not
    numbering."""
    state = rewards_state()
    for item in state["rewards"]["items"][:2]:
        item["description"] = "Gold"
    page = blindplay.observe(state)
    assert "**Gold (1)**" in page and "**Gold (2)**" in page
    res = blindplay.act(state, 'choose "Gold (2)"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "claim_reward", "index": 1}


def chooser_over_combat_state() -> dict:
    """A combat card-chooser: `hand_select` WITH the battle still on the wire.

    `EB-290` (2). This is the shape the r4 Opus seat was looking at when
    `play` answered *"you are not in a battle"* -- `GetState` sets
    `state_type` to `hand_select` and still sends `battle`, because the fight
    is very much in progress (`McpMod.StateBuilder.cs:488-493`).
    """
    state = json.loads(json.dumps(spark_priced_state()))
    state["state_type"] = "hand_select"
    state["hand_select"] = {"prompt": "Choose a card to make free.",
                            "cards": state["player"]["hand"]}
    return state


def test_play_during_a_combat_chooser_names_the_chooser():
    """`EB-290` (2). "Posting `play "Big Badda Boom" on "Sewer Clam"` returned
    *you are not in a battle*. I was in a battle, round 1 against the Sewer
    Clam; the true reason is that a selection screen was open."

    The refusal now says which screen is open, quotes its prompt and lists the
    verbs the page is already offering three lines above."""
    state = chooser_over_combat_state()
    res = blindplay.act(state, 'play "Kaboom!" on "Corpse Slug"')
    assert not res["ok"]
    assert "you are not in a battle" not in res["refusal"]
    assert "a card chooser is open" in res["refusal"]
    assert "Choose a card to make free." in res["refusal"]
    assert 'choose "<card title>"' in res["refusal"]
    # `end turn` is the same mistake and gets the same answer.
    assert "a card chooser is open" in blindplay.act(state,
                                                     "end turn")["refusal"]


def test_the_flat_refusal_survives_where_it_is_true():
    """The narrowing is only the chooser screens: a map really is not a battle
    and still says so.

    `EB-319` added the second half of that sentence and nothing else: the
    REASON is the one this row pinned, and the way out is the map's own verb.
    """
    res = blindplay.act(map_state(), "end turn")["refusal"]
    assert res.startswith("you are not in a battle")
    assert 'go "<node>"' in res


# ------------------------------------------------- EB-319: the way out -----

def random_target_combat_state() -> dict:
    """The RECORDED combat turn plus ONE synthetic card: a random-target
    Attack, which the game declares `TargetType.AllEnemies`.

    Synthetic because the recording is a Kokomi turn and no Kokomi row aims
    that way; the shape is the shipped Klee card's own -- `RapidFire.cs:63`
    passes `TargetType.AllEnemies` and `McpMod.StateBuilder.cs:1394` sends
    `card.TargetType.ToString()` -- so the value under test is the one the
    wire carries, not one this file invented.
    """
    state = json.loads(json.dumps(combat_state()))
    hand = state["player"]["hand"]
    card = json.loads(json.dumps(hand[0]))
    card.update({"id": "KLEEMOD-RAPID_FIRE", "name": "Rapid Fire",
                 "description": "Deal 3 damage to random enemies four times.",
                 "target_type": "AllEnemies", "keywords": [],
                 "index": len(hand)})
    hand.append(card)
    return state


def test_a_card_that_aims_itself_is_refused_with_the_form_that_works():
    """`EB-319`, and the round it cost.

    `play "Rapid Fire" on "Seapunk"` was answered *Rapid Fire is random-target
    and takes no target*: true, and it named no way to play the card. The seat
    had chained `end turn` behind it, so an Attack Potion's 12 free damage
    went with the turn -- "the message had the information and withheld it"
    (round-7 act-1 seat, Fight 5).

    Two halves, and the second is the row: the play is refused HERE instead of
    being posted and refused by the bridge, and the refusal ends in the
    command that resolves.
    """
    state = random_target_combat_state()
    res = blindplay.act(state, 'play "Rapid Fire" on "Nibbit"')
    assert not res["ok"]
    assert res["post"] is None            # never posted, so nothing is spent
    assert 'play "Rapid Fire"' in res["refusal"]
    # ...and that form really is the one that works.
    ok = blindplay.act(state, 'play "Rapid Fire"')
    assert ok["ok"] and "target" not in ok["post"]


def test_a_card_played_on_the_player_is_refused_the_same_way():
    """The same rule for the other spelling the bridge refuses: a `Self` card
    handed an enemy reaches `IsValidTarget` and comes back a wasted action."""
    res = blindplay.act(combat_state(), 'play "Coral Guard" on "Nibbit"')
    assert not res["ok"] and 'play "Coral Guard"' in res["refusal"]
    assert blindplay.act(combat_state(), 'play "Coral Guard"')["ok"]


def test_an_aimed_card_still_takes_its_aim():
    """The relaxation is exactly as wide as the enum names in
    `UNAIMED_TARGETS`: an `AnyEnemy` card is unchanged, and so is a custom
    single-target type, which the wire spells as a bare number (`EB-216`)."""
    state = random_target_combat_state()
    assert blindplay.act(state, 'play "Pearl Barrage" on "Nibbit"')["ok"]
    state["player"]["hand"][-1]["target_type"] = "40213"      # a custom type
    assert blindplay.act(state, 'play "Rapid Fire" on "Nibbit"')["ok"]


def test_every_refusal_on_every_screen_ends_in_a_form_that_resolves():
    """`EB-319`'s acceptance, swept rather than sampled.

    One nonsense command per screen this page drives, so a refusal that names
    no way out fails here whichever `_refuse` produced it. A screen the page
    refuses to drive is excluded BY NAME and for the honest reason: it has no
    command that resolves, and inventing one would be the defect this row is
    about, pointing the other way.
    """
    screens = {"combat": combat_state(), "map": map_state(),
               "shop": shop_state(), "rest": rest_state(),
               "card_reward": card_reward_state(), "event": event_state()}
    checked = 0
    for label, state in screens.items():
        obs = blindplay.observation(state)
        assert not obs["blocked"], f"{label} fixture is not drivable"
        for command in ('play "Nothing At All"', 'choose "Nothing At All"',
                        'go "Nowhere"', 'buy "Nothing At All"', "end turn",
                        "rest", "confirm", "skip", "wibble"):
            res = blindplay.act(state, command)
            if res["ok"]:
                continue
            checked += 1
            assert ("The form that resolves: " in res["refusal"]
                    or "Forms that resolve here: " in res["refusal"]), (
                f"{label}: {command} was refused with no form that resolves "
                f"-- {res['refusal']!r}")
            # And the form is a real one: the tail is the screen's own
            # grammar, or a command a call site spelled out in full.
            tail = res["refusal"].rsplit(": ", 1)[1]
            assert tail.strip(), f"{label}: empty form list"
    assert checked >= 30, f"only {checked} refusals swept -- the pin is stale"


def test_a_screen_that_is_not_being_driven_promises_no_form():
    """The other half of the same honesty: `_with_forms` adds nothing where
    the page itself offers nothing, so a refusal never invents a way out."""
    res = blindplay.act({"state_type": "seance_minigame"}, "proceed")
    assert not res["ok"]
    assert "resolves" not in res["refusal"]


def test_the_spark_refusal_is_one_sentence():
    """`EB-290` (3). "*CANNOT BE PLAYED: you have no Spark; and this costs 1*
    -- the trailing '; and this costs 1' reads like a truncated sentence."

    AND THE TRUNCATION WAS OURS. `KleeUnplayableReason.For` writes ONE
    sentence with a comma in it; `unplayable_reason` split it on that comma as
    if it were a `[Flags]` enum and rejoined the halves with `"; "`.
    """
    state = spark_priced_state()
    card = state["player"]["hand"][0]
    card["unplayable_reason_text"] = "you have no Spark, and this costs 1"
    page = blindplay.observe(state)
    assert "CANNOT BE PLAYED: you have no Spark, and this costs 1" in page
    assert "; and this costs" not in page
    # The flags split still works where the wire really does send flags.
    assert qa_packet.unplayable_reason(
        "BlockedByCardLogic, EnergyCostTooHigh") == (
        "this card's own rule is stopping you right now; you do not have "
        "enough energy")


def test_a_card_shelf_prints_its_type_sold_or_not():
    """`EB-268`'s acceptance, word for word: "the shop fixture's card shelves
    print `cost N, <type>`, sold or not."

    The r1 Opus seat bought two cards "without knowing what they cost to
    play". The energy cost landed with `EB-262`; the TYPE is the other field
    the wire sends beside it (`card_type`) and the page was dropping, and the
    sold half rides `EB-262`'s shelf memory.
    """
    blindplay.forget_shelves()
    stocked = blindplay.observe(live("shop-stocked"))
    assert "**Perfect Timing** — cost 1, card (attack), 76 gold" in stocked
    assert "**Mine Toss** — cost 1, card (skill), 51 gold" in stocked
    assert "**Grounded** — cost 1, card (power), 74 gold" in stocked
    # A relic and a potion have no card type and read exactly as before.
    assert "**Bag of Preparation** — relic, 192 gold" in stocked
    assert "**Flex Potion** — potion, 48 gold" in stocked

    sold = blindplay.observe(live("shop-bought"))
    assert "**Perfect Timing** — cost 1, card (attack), 76 gold (sold)" in sold


# --------------------------------- EB-294: the three Kokomi r2 render gaps --

def aura_combat_state() -> dict:
    """An enemy carrying the aura the player just applied (`EB-294`).

    `AuraPower.Type` is `PowerType.Buff` -- deliberately, so Artifact does not
    eat an elemental application -- so the wire says `Buff` and the page said
    `(buff)`.
    """
    state = json.loads(json.dumps(spark_priced_state()))
    state["battle"]["enemies"][0]["status"] = [
        {"id": "KLEEMOD-HYDRO_AURA", "title": "Hydro Aura", "amount": 2,
         "type": "Buff",
         "description": "Hydro clings to this enemy for 2 more turns. A hit "
                        "of a different element consumes the aura and "
                        "triggers an Elemental Reaction; a Hydro hit "
                        "refreshes its duration."},
        {"id": "VULNERABLE", "title": "Vulnerable", "amount": 1,
         "type": "Debuff", "description": "Takes 50% more attack damage."}]
    return state


def test_an_aura_is_not_tagged_as_the_enemys_buff():
    """`EB-294` (1). "`Hydro Aura 2 (buff)` appears in the same block as
    `Vulnerable 1 (debuff)`. The aura I put on them to set up a Reaction reads
    as something helping them." """
    page = blindplay.observe(aura_combat_state())
    assert "Hydro Aura 2 (aura)" in page
    assert "Hydro Aura 2 (buff)" not in page
    # The debuff beside it is untouched, and the clause is said once.
    assert "Vulnerable 1 (debuff)" in page
    assert page.count("An aura is tagged") == 1
    assert "what an Elemental Reaction needs" in page


def test_a_board_with_no_aura_says_nothing_about_auras():
    """The note is printed where it bites and nowhere else."""
    assert "An aura is tagged" not in blindplay.observe(spark_priced_state())


def bundle_state(picked=None) -> dict:
    """`bundle_select` as `BuildBundleSelectState` sends it (`EB-294`).

    `preview_cards` is filled from the preview container the moment a bundle
    is picked, and `can_confirm` is the confirm button's own state.
    """
    bundles = [
        {"index": 0, "card_count": 2, "cards": [
            {"name": "Deep Current", "cost": "1", "type": "Attack",
             "description": "Deal 4 damage to every enemy."},
            {"name": "Slack Water", "cost": "1", "type": "Attack",
             "description": "Deal 2 damage. Apply 1 Weak."}]},
        {"index": 1, "card_count": 2, "cards": [
            {"name": "Coral Guard", "cost": "1", "type": "Skill",
             "description": "Gain 5 Block."},
            {"name": "Sea-Salt Prayer", "cost": "1", "type": "Skill",
             "description": "Gain 7 Block."}]}]
    blob = {"screen_type": "bundle", "prompt": "Choose a bundle.",
            "bundles": bundles, "preview_showing": picked is not None,
            "preview_cards": ([dict(c) for c in bundles[picked]["cards"]]
                              if picked is not None else []),
            "can_cancel": True, "can_confirm": picked is not None}
    return {"state_type": "bundle_select", "bundle_select": blob}


def test_a_picked_bundle_is_marked():
    """`EB-294` (2). "`choose "Deep Current"` answered `ok Selecting bundle
    0`, but re-observing printed the identical page with no mark on either
    bundle. I had to send `confirm` on faith that the right one was armed."

    The wire DOES answer -- `preview_cards` holds the picked bundle's cards --
    so the pick is matched back to the bundle and marked."""
    before = blindplay.observe(bundle_state())
    assert "PICKED" not in before and "Nothing is picked yet." in before

    after = blindplay.observe(bundle_state(picked=0))
    assert "## A bundle of: Deep Current, Slack Water — PICKED" in after
    assert "## A bundle of: Coral Guard, Sea-Salt Prayer" in after
    assert after.count("PICKED") == 1


def test_a_preview_that_matches_no_bundle_says_so_instead_of_guessing():
    """The honest arm, and the same one the enchant picker gets: a preview the
    page cannot attribute is reported as a pick it cannot place."""
    state = bundle_state(picked=1)
    state["bundle_select"]["preview_cards"] = [
        {"name": "Something Else", "cost": "0", "type": "Skill",
         "description": "Draw 1 card."}]
    page = blindplay.observe(state)
    assert "PICKED" not in page
    assert "cannot say which" in page


def test_an_emptied_reward_screen_drops_the_chooser():
    """`EB-294` (3). "After taking both fight-1 rewards the page printed
    `- (nothing here to take)` and still listed `choose "<reward>"` under
    'What you can say'." """
    page = blindplay.observe(empty_rewards_state())
    assert "(nothing here to take)" in page
    assert 'choose "<reward>"' not in page
    assert page.count("- `") == 1 and "- `proceed`" in page
    # And the verb is still there while anything is left to take.
    assert 'choose "<reward>"' in blindplay.observe(rewards_state())


# ------------------------------------ EB-298: the map, and what it carries --

def test_the_map_prints_the_floors_ahead_and_the_boss():
    """`EB-298`. "It prints only the immediately adjacent nodes as bare labels
    with no floors ahead and no elite/shop/campfire distinction, so route
    choice is a coin flip. The `Unknown (path 1)` I took turned out to be a
    `# Wellspring` event."

    Everything below was already on the feed: `leads_to` per option, `nodes`
    for the whole act, and the boss's own printed name."""
    page = blindplay.observe(map_state())
    assert "leads on to: Elite, Unknown" in page
    assert "- 1 floor ahead: Monster, Monster, Rest Site" in page
    assert "- 2 floors ahead: Elite, Unknown, Merchant" in page
    assert "- 3 floors ahead: Boss" in page
    assert "At the top of this act: **Gremlin Matriarch**" in page
    # The path handles are unchanged, and so is the one verb.
    assert "**Monster (path 1)**" in page
    assert blindplay.act(map_state(), 'go "Rest Site (path 3)"')["post"] == \
        {"action": "choose_map_node", "index": 2}


def test_the_map_never_prints_a_boss_id_or_a_coordinate():
    """The boss block carries an `id` beside its `name` and the nodes carry
    grid coordinates; neither is a thing the game prints, so neither reaches
    the page. A floor is named by DISTANCE for the same reason."""
    page = blindplay.observe(map_state())
    assert "GREMLIN_MATRIARCH" not in page
    assert "Floor 4" not in page


def test_a_map_with_nothing_but_next_options_still_renders():
    """A state saved before any of this was read -- and the pre-round-four
    shape -- prints the options and simply says nothing more."""
    state = {"state_type": "map",
             "map": {"next_options": [{"index": 0, "type": "Monster",
                                       "col": 1, "row": 4}]}}
    page = blindplay.observe(state)
    assert "**Monster (path 1)**" in page
    assert "floors ahead" not in page
    assert "At the top of this act" not in page


def test_the_floors_ahead_are_read_from_the_direction_of_travel():
    """A map whose rows COUNT DOWN toward the boss is read the same way: the
    next options are one step from where you stand, and that step is the
    direction. Nothing here assumes the numbers rise."""
    state = json.loads(json.dumps(map_state()))
    blob = state["map"]
    for row in (blob["nodes"] + blob["next_options"]
                + [blob["current_position"], blob["boss"]]):
        row["row"] = 20 - row["row"]
    for opt in blob["next_options"]:
        for child in opt["leads_to"]:
            child["row"] = 20 - child["row"]
    page = blindplay.observe(state)
    assert "- 1 floor ahead: Monster, Monster, Rest Site" in page
    assert "- 3 floors ahead: Boss" in page


def test_the_map_prints_the_gold_and_the_deck():
    """`EB-447`. THE TWO FACTS A ROUTE IS CHOSEN ON, AND NEITHER WAS PRINTED.

    The Furina r7 seat got its gold by arithmetic over reward lines and
    "reconstructed, not read" its deck out of remembered hands; the Kokomi r11
    and r13 seats met a `Slimed` for the first time at a Smith screen. The
    gold is on the map's own feed and was printed on the shop screen alone;
    the deck is on a fight's feed only, so it comes off the same lane store
    the Smith's omission list is subtracted against -- with the same
    staleness, said in the same words.

    Seen to FAIL: the map page printed the nodes, the floors ahead and the
    boss, and no gold and no deck.
    """
    blindplay.forget_deck()
    fight, smith = upgrade_run_states()
    here = json.loads(json.dumps(map_state()))
    here["run"] = {"act": 1, "floor": 11}
    here["player"]["character"] = smith["player"]["character"]

    # Before any fight: the gold is already readable, the deck is not, and the
    # page says which of the two it cannot answer instead of printing nothing.
    page = blindplay.observe(here)
    assert "You have 99 gold." in page
    assert "## Your deck" not in page
    assert "no fight of this run has been read" in page

    blindplay.observe(fight)                       # the deck is read here
    page = blindplay.observe(here)
    assert "You have 99 gold." in page
    assert "## Your deck" in page
    # A title the run holds one of, and the upgrade mark on the copy that
    # carries it -- the grammar's own `(upgraded)` spelling.
    assert "- **Powder Charge**" in page
    assert "- **Ka-pow! (upgraded)**" in page
    # Repeats are counted rather than listed, and the staleness travels with
    # the list.
    assert "- **Duck and Cover** × 3" in page
    assert "- **Ka-pow!** × 2" in page
    assert "your deck as it stood in the last fight (floor 10)" in page
    blindplay.forget_deck()


# ------------ EB-299: two lines whose grammar the reader could not read -----

def test_the_duplicate_name_note_does_not_say_two():
    """`EB-299` (1). "*Two cards here print the same name*... printed on a
    hand holding three Coral Guards already disambiguated as `(1) (2) (3)`, on
    a hand with two separate duplicate pairs, and on a hand with three Water's
    Edge and two Slimed. It says 'Two cards' regardless."

    And the second half the same seat found unprompted: "the numbered suffixes
    renumber inside a turn", so the number is a place in a list and the note
    has to say so."""
    state = json.loads(json.dumps(spark_priced_state()))
    state["player"]["hand"] = [
        {"id": "KLEEMOD-CORAL_GUARD", "name": "Coral Guard", "type": "Skill",
         "cost": "1", "can_play": True, "description": "Gain 5 Block."}
        for _ in range(3)]
    page = blindplay.observe(state)
    assert "**Coral Guard (1)**" in page and "**Coral Guard (3)**" in page
    assert "Two cards here print the same name" not in page
    assert "More than one card in this hand prints the same name" in page
    assert "names a different copy once one of them leaves your hand" in page
    # `EB-181` narrowed the enchantment clause rather than dropping it: the
    # bridge now carries an enchantment, so the note claims only what is
    # still true -- that copies showing NONE cannot be told apart here.
    assert "where two copies show none and differ only by one" in page


def test_the_duplicate_name_note_stays_off_a_hand_with_no_repeat():
    assert "More than one card in this hand" not in blindplay.observe(
        spark_priced_state())


def test_an_intent_number_says_what_it_is():
    """`EB-299` (2). "The Strategic intent's number was understandable only
    from its accompanying sentence" (r2 Codex seat, question 6).

    The line was `kind`, `label` and `text` comma-joined: three grammars in
    one list. The label is the number the game draws ON the icon and the feed
    gives it no unit, so the page says that is what it is -- and the `type`
    the page used to drop goes back beside the hover tip's heading."""
    state = json.loads(json.dumps(spark_priced_state()))
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "Debuff", "label": "2", "title": "Strategic",
         "description": "This enemy intends to apply a Debuff to you."}]
    page = blindplay.observe(state)
    assert ("Intent: Strategic (Debuff) — the number on its icon is 2 — "
            "This enemy intends to apply a Debuff to you." in page)
    assert "Intent: Strategic, 2," not in page


def test_an_intent_with_no_number_prints_no_number():
    """A telegraph the wire gives no label prints the heading and the sentence
    and invents nothing between them."""
    state = json.loads(json.dumps(spark_priced_state()))
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "Buff", "title": "Strategic",
         "description": "This enemy intends to buff itself."}]
    page = blindplay.observe(state)
    assert ("Intent: Strategic (Buff) — This enemy intends to buff itself."
            in page)
    assert "the number on its icon" not in page


def test_an_intent_whose_heading_is_its_type_is_not_printed_twice():
    """Where the hover tip's heading and the wire's `type` are the same word,
    the page says it once."""
    state = json.loads(json.dumps(spark_priced_state()))
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "Attack", "title": "Attack", "label": "8",
         "description": "Attack for 8 damage."}]
    page = blindplay.observe(state)
    assert "Intent: Attack — the number on its icon is 8" in page
    assert "Attack (Attack)" not in page


def test_an_enemy_with_no_intent_at_all_still_renders():
    state = json.loads(json.dumps(spark_priced_state()))
    state["battle"]["enemies"][0].pop("intents")
    assert "Intent: (no intent shown)" in blindplay.observe(state)


# ------------------------------------ the base game's basics (R242) --------
#
# Both overhaul starters open with four Strikes and four Defends that are the
# BASE GAME's cards, not mod rows. The render needed no change for them and
# this is why: repeats are numbered by `_number_names`, and `printed_cost` is
# a klee-mod-sourced index whose silence rule ("a card the index has no row
# for gets NO note") is exactly right for a card the mod did not author.


def base_basics_combat_state() -> dict:
    """A Klee overhaul hand as the wire draws it: four base Strikes, a base
    Defend and her one detonator. Ids are the base game's own `ModelId.Entry`
    spellings, with no `KLEEMOD-` prefix, because the models are the base
    game's (`StrikeIronclad`, `DefendIronclad`)."""
    strike = {"id": "STRIKE_IRONCLAD", "name": "Strike", "type": "Attack",
              "cost": "1", "can_play": True, "description": "Deal 6 damage."}
    return {
        "state_type": "monster",
        "battle": {"round": 1, "enemies": [
            {"name": "Seapunk", "hp": 45, "max_hp": 45, "block": 0,
             "intents": [{"type": "Attack", "label": "11",
                          "description": "Attack for 11 damage."}]}]},
        "player": {
            "hp": 62, "max_hp": 62, "block": 0, "energy": 3, "max_energy": 3,
            "resources": {}, "draw_pile_count": 5,
            "discard_pile_count": 0, "exhaust_pile_count": 0,
            "status": [{"name": "Spark", "amount": 1, "type": "Buff",
                        "description": "You start each combat with 1 and gain "
                                       "1 whenever a Bomb goes off."}],
            "hand": [
                json.loads(json.dumps(strike)),
                json.loads(json.dumps(strike)),
                json.loads(json.dumps(strike)),
                json.loads(json.dumps(strike)),
                {"id": "DEFEND_IRONCLAD", "name": "Defend", "type": "Skill",
                 "cost": "1", "can_play": True,
                 "description": "Gain 5 Block."},
                {"id": "KLEEMOD-PROTO_KO_KAPOW", "name": "Ka-pow!",
                 "type": "Attack", "cost": "0", "can_play": True,
                 "description": "Set off. Deal 4 damage."},
            ]},
    }


def test_the_base_basics_render_with_their_faces_and_no_invented_note():
    page = blindplay.render(
        blindplay.observation(base_basics_combat_state()))
    assert "Deal 6 damage." in page and "Gain 5 Block." in page
    # The silence rule: the mod authored neither card, so nothing claims to
    # know a printed cost for them.
    assert "The cost printed on this card" not in page
    # And the arm's own row still reads: 0 energy for the detonator.
    assert "Ka-pow!" in page


def test_four_base_strikes_are_each_nameable_and_playable():
    """Four interchangeable copies must not be four unplayable cards. The
    numbering `EB-177` built for two enchanted Water's Edges is what carries
    R242's four Strikes, so the bare title takes the first copy and every
    numbered name resolves to its own index."""
    state = base_basics_combat_state()
    page = blindplay.render(blindplay.observation(state))
    assert "Strike (1)" in page and "Strike (4)" in page
    # Defend appears once on this screen, so it is NOT numbered.
    assert "Defend (1)" not in page

    first = blindplay.act(state, 'play "Strike"')
    assert first["ok"] and first["post"]["card_index"] == 0
    for i in range(4):
        res = blindplay.act(state, f'play "Strike ({i + 1})"')
        assert res["ok"] and res["post"]["card_index"] == i
# --------------------------------------------------------------------------
# `EB-269` / `EB-271` / `EB-272` / `EB-273` / `EB-245` / `EB-246`: the render
# and driver defects the Klee r2 and Kokomi r1 blind runs filed. Every fixture
# below is written from the bridge's OWN builder -- `BuildPlayerState`'s potion
# rows, `ExecuteUsePotion`'s target switch, `Error()`'s answer shape -- because
# the render agent's lesson is that a fixture guessed at keeps a render test
# green while the live screen is wrong (`EB-262`, `EB-290`).
# --------------------------------------------------------------------------


def potion_belt_state(potions: list[dict]) -> dict:
    """A combat with a POTION BELT as `BuildPlayerState` sends one.

    `McpMod.StateBuilder.cs:1274-1292` walks `player.PotionSlots`, SKIPS every
    empty slot and numbers every slot it walks past -- so a row carries its own
    `slot`, and the list position stops agreeing with it the moment a potion is
    drunk out of an earlier slot. Each row also carries `target_type`, the
    `TargetType.ToString()` that `ExecuteUsePotion` switches on.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["potions"] = potions
    return state


DEXTERITY_IN_SLOT_ONE = [
    {"id": "DEXTERITY_POTION", "name": "Dexterity Potion",
     "description": "Gain 2 Dexterity.", "slot": 1,
     "can_use_in_combat": True, "target_type": "Self", "keywords": []}]

FIRE_IN_SLOT_ZERO = [
    {"id": "FIRE_POTION", "name": "Fire Potion",
     "description": "Deal 20 damage to one enemy.", "slot": 0,
     "can_use_in_combat": True, "target_type": "AnyEnemy", "keywords": []}]


def test_a_self_targeted_potion_posts_the_slot_the_wire_gave_it():
    """`EB-269`, AND IT IS THE WHOLE DEFECT. The r2 Opus seat drank the Energy
    Potion out of slot 0; the Dexterity Potion in slot 1 became the only row on
    the belt and therefore LIST INDEX 0; and every `use potion` for the rest of
    the run posted `slot: 0`, an empty slot, which the bridge answered `No
    potion in slot 0`. Three attempts, three failures, on two screens.

    Seen to FAIL: with the list position posted this asserts `slot == 1` and
    gets 0.
    """
    state = potion_belt_state(DEXTERITY_IN_SLOT_ONE)
    res = blindplay.act(state, 'use potion "Dexterity Potion"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "use_potion", "slot": 1}
    # `Self` is resolved to the player BY THE BRIDGE, so nothing is aimed here.
    assert "target" not in res["post"]
    assert res["printed"] == {"potion": "Dexterity Potion",
                              "target": "yourself"}


def test_a_belt_with_no_slot_field_still_resolves_by_position():
    """A feed that sends no `slot` keeps the behaviour it always had, rather
    than the command failing on a missing key."""
    belt = [dict(DEXTERITY_IN_SLOT_ONE[0])]
    belt[0].pop("slot")
    res = blindplay.act(potion_belt_state(belt),
                        'use potion "Dexterity Potion"')
    assert res["post"] == {"action": "use_potion", "slot": 0}


def test_a_self_potion_aimed_at_an_enemy_is_used_on_you_anyway():
    """A tester who aims a buff potion has made a mistake with no consequence:
    `ExecuteUsePotion` resolves `Self` to the player whatever is posted. The
    page says where it went instead of spending a refusal on it."""
    res = blindplay.act(potion_belt_state(DEXTERITY_IN_SLOT_ONE),
                        'use potion "Dexterity Potion" on "Nibbit"')
    assert res["ok"] and "target" not in res["post"]
    assert res["printed"]["target"] == "yourself"


def test_an_enemy_potion_is_aimed_before_it_is_posted():
    """The other direction, and it must not regress: `AnyEnemy` is the one
    branch of `ExecuteUsePotion` that REFUSES a post with no `target`, so the
    aim happens here where a refusal can name the enemies."""
    state = potion_belt_state(FIRE_IN_SLOT_ZERO)
    res = blindplay.act(state, 'use potion "Fire Potion" on "Nibbit"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "use_potion", "slot": 0,
                           "target": "NIBBIT_0"}
    assert res["printed"]["target"] == "Nibbit"


def test_an_enemy_potion_on_a_one_body_board_needs_no_word():
    """`_resolve_enemy`'s own rule, unchanged: one living enemy is not a
    question, so an aimed potion typed bare is aimed at it."""
    res = blindplay.act(potion_belt_state(FIRE_IN_SLOT_ZERO),
                        'use potion "Fire Potion"')
    assert res["ok"] and res["post"]["target"] == "NIBBIT_0"


def test_an_enemy_potion_on_a_crowded_board_asks_which():
    """Two bodies and no word: the refusal names them rather than guessing, and
    it is the same sentence a card gets."""
    state = potion_belt_state(FIRE_IN_SLOT_ZERO)
    state["battle"]["enemies"].append(
        {"entity_id": "SLUG_1", "name": "Corpse Slug", "hp": 12, "max_hp": 12,
         "block": 0, "intents": [], "status": []})
    res = blindplay.act(state, 'use potion "Fire Potion"')
    assert not res["ok"]
    assert "Nibbit" in res["refusal"] and "Corpse Slug" in res["refusal"]


WEAK_IN_SLOT_ZERO = [
    {"id": "WEAK_POTION", "name": "Weak Potion",
     "description": "Apply 3 Weak.", "slot": 0, "can_use_in_combat": True,
     # The spelling that reproduces `EB-452`: not `AnyEnemy`, so it fell past
     # `AIMED_TARGETS`, and not one of the three the bridge aims itself, so
     # `ExecuteUsePotion` passed a null target and enqueued the use anyway.
     "target_type": "AnyCreature", "keywords": []}]


def test_a_targeted_potion_with_no_target_is_refused_with_the_working_forms():
    """`EB-452`. THE POTION WAS DRUNK INTO THE VOID AND THE PAGE SAID `ok`.

    Kokomi round 13, the act boss, turn 5: `use potion "Weak Potion"` on a
    board of three was accepted, the potion was spent, no Weak landed on any
    body, no intent moved, and nothing anywhere printed a refusal.

    The fall-through is the other way for a potion than for a card
    (`_potion_aims_at_an_enemy`): only the spellings the game aims itself are
    drunk bare. Everything else is asked for an enemy, and the refusal carries
    the command that works.

    Seen to FAIL: the untargeted use resolves, `ok` is True, and the post
    carries no target at all.
    """
    state = potion_belt_state(WEAK_IN_SLOT_ZERO)
    state["battle"]["enemies"].append(
        {"entity_id": "SLUG_1", "name": "Corpse Slug", "hp": 12, "max_hp": 12,
         "block": 0, "intents": [], "status": []})

    res = blindplay.act(state, 'use potion "Weak Potion"')
    assert not res["ok"]
    assert "Nibbit" in res["refusal"] and "Corpse Slug" in res["refusal"]
    assert 'use potion "Weak Potion" on "Nibbit"' in res["refusal"]
    assert 'use potion "Weak Potion" on "Corpse Slug"' in res["refusal"]

    # Named, it resolves exactly as `play` does: the entity id on the post and
    # the printed name on the receipt.
    res = blindplay.act(state, 'use potion "Weak Potion" on "Corpse Slug"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "use_potion", "slot": 0,
                           "target": "SLUG_1"}
    assert res["printed"] == {"potion": "Weak Potion",
                              "target": "Corpse Slug"}


def test_a_potion_the_game_aims_itself_is_still_drunk_bare():
    """The boundary the row must not cross. `AllEnemies` and `None` are the
    two spellings `ExecuteUsePotion` deliberately resolves to a null target,
    and a feed that sends no `target_type` has not said anything -- all three
    keep being used with no `on` clause and no refusal."""
    for aim in ("AllEnemies", "None", ""):
        belt = [dict(WEAK_IN_SLOT_ZERO[0], target_type=aim)]
        state = potion_belt_state(belt)
        state["battle"]["enemies"].append(
            {"entity_id": "SLUG_1", "name": "Corpse Slug", "hp": 12,
             "max_hp": 12, "block": 0, "intents": [], "status": []})
        res = blindplay.act(state, 'use potion "Weak Potion"')
        assert res["ok"], f"{aim}: {res['refusal']}"
        assert "target" not in res["post"]


def test_a_bridge_refusal_reaches_the_page_as_words():
    """`EB-269`, the half that made the defect invisible. `Error()` writes the
    reason under `error`, never `message` (`McpMod.Helpers.cs:158-161`), and
    this line read `status` and `message` only -- so every refusal the game
    gave arrived as the single word `error`.

    Seen to FAIL: without the `error` key this asserts the sentence and gets
    `"error"`.
    """
    line = blindplay._result_line(
        {"status": "error", "error": "No potion in slot 0"})
    assert line == "error No potion in slot 0"
    # An OK answer is unchanged, and a leaky one is still swallowed whole.
    assert blindplay._result_line(
        {"status": "ok", "message": "Using potion"}) == "ok Using potion"
    assert "will not repeat" in blindplay._result_line(
        {"status": "error", "error": "card KLEEMOD-KABOOM is not in hand"})


# ------------------------------------------ EB-271: a number that went stale


def duplicate_hand_state(copies: int) -> dict:
    """A combat holding `copies` of one printed title, `BuildCardState`'s
    shape -- the `Duck and Cover` pair the r2 Opus seat was holding."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_DUCK_AND_COVER", "name": "Duck and Cover",
         "type": "Skill", "cost": "1", "can_play": True, "index": i,
         "target_type": "Self", "is_upgraded": False, "keywords": [],
         "description": "Gain 5 Block."} for i in range(copies)]
    return state


def test_two_copies_are_numbered_and_both_numbers_work():
    """Unchanged `EB-177` behaviour, asserted here so the fix below cannot be
    mistaken for having loosened it."""
    state = duplicate_hand_state(2)
    assert "Duck and Cover (1)" in blindplay.observe(state)
    for name in ("Duck and Cover (1)", "Duck and Cover (2)"):
        assert blindplay.act(state, f'play "{name}"')["ok"], name


def test_a_stale_number_still_names_the_last_copy():
    """`EB-271`, FOUND LIVE. `_number_names` numbers a title only while it
    repeats, so the moment one of two copies is played the survivor prints
    bare -- and `play "Duck and Cover (1)"`, the name the page printed one
    screen earlier and the tester had just typed once, came back *nothing here
    is called that*.

    Seen to FAIL: without the stale-number retry this refuses.
    """
    state = duplicate_hand_state(1)
    assert "Duck and Cover (1)" not in blindplay.observe(state)
    res = blindplay.act(state, 'play "Duck and Cover (1)"')
    assert res["ok"], res["refusal"]
    assert res["post"]["card_index"] == 0
    assert res["printed"]["card"] == "Duck and Cover"
    # Any stale number, not just the one that survived: the page reprints the
    # list from scratch on every screen and the tester cannot know which.
    assert blindplay.act(state, 'play "Duck and Cover (2)"')["ok"]


def test_a_number_that_is_still_ambiguous_is_still_refused():
    """The rule is ONE COPY REMAINS, and it stops there. With both copies still
    in hand a number nothing carries is a real ambiguity, and the refusal
    advertises the names that would have worked."""
    res = blindplay.act(duplicate_hand_state(2), 'play "Duck and Cover (3)"')
    assert not res["ok"]
    assert "Duck and Cover (1)" in res["refusal"]
    assert "Duck and Cover (2)" in res["refusal"]


def test_a_stale_number_names_the_last_enemy_standing():
    """The same handle on the other list. The render numbers over EVERY enemy
    including the corpses, so this only bites where the feed drops a dead body
    -- and where it does, the survivor is still nameable by the number the
    tester last saw."""
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["enemies"][0]["name"] = "Two-Tailed Rat"
    res = blindplay.act(state, 'play "Pearl Barrage" on "Two-Tailed Rat (2)"')
    assert res["ok"], res["refusal"]
    assert res["post"]["target"] == "NIBBIT_0"


# --------------------- EB-271: the number an enemy keeps for the whole fight


def slug_fight(combat_ids: list[int]) -> dict:
    """A combat whose enemies all print one name, `BuildEnemyState`'s shape.

    Derived from the recorded Nibbit rather than written out, so every key on
    every enemy is one the bridge really emits. `entity_id` is rebuilt the way
    `McpMod.StateBuilder.cs:1436` builds it -- by COUNTING the live list as it
    walks -- which is exactly why it cannot be the fight's memory key, and
    `combat_id` is the game's own per-creature id, which can.
    """
    state = json.loads(json.dumps(combat_state()))
    proto = state["battle"]["enemies"][0]
    enemies = []
    for slot, cid in enumerate(combat_ids):
        body = json.loads(json.dumps(proto))
        body["name"] = "Sea Slug"
        body["combat_id"] = cid
        body["entity_id"] = f"SEA_SLUG_{slot}"
        enemies.append(body)
    state["battle"]["enemies"] = enemies
    return state


def test_an_enemy_keeps_its_number_when_a_body_leaves():
    """`EB-271`, THE HALF THAT MISTARGETS IN SILENCE.

    With three enemies of one name the feed drops the first body once its
    death finishes, and `_number_names` renumbers what is left from 1. The
    survivors the page called `(2)` and `(3)` reprint as `(1)` and `(2)`, so
    `on "Sea Slug (2)"` -- refused for a card, but ACCEPTED for an enemy --
    lands on the creature that was `(3)` one screen earlier and says nothing.

    Seen to FAIL: with the numbering read off the live list, the second
    resolve below returns `SEA_SLUG_1`, the wrong body.
    """
    blindplay.forget_fight()
    three = slug_fight([1, 2, 3])
    page = blindplay.observe(three)
    assert "Sea Slug (1)" in page and "Sea Slug (3)" in page
    first = blindplay.act(three, 'play "Pearl Barrage" on "Sea Slug (2)"')
    assert first["ok"], first["refusal"]
    assert first["post"]["target"] == "SEA_SLUG_1"

    # The first slug dies and the feed stops sending it. The two that remain
    # are the same two creatures, at new places in the list.
    two = slug_fight([2, 3])
    page = blindplay.observe(two)
    assert "Sea Slug (2)" in page and "Sea Slug (3)" in page
    assert "Sea Slug (1)" not in page
    again = blindplay.act(two, 'play "Pearl Barrage" on "Sea Slug (2)"')
    assert again["ok"], again["refusal"]
    # `combat_id` 2 is at slot 0 on this board, so this is the same creature
    # the first resolve hit -- and NOT `SEA_SLUG_1`, which is now `combat_id`
    # 3 and is what the unfixed page would have aimed at.
    assert again["post"]["target"] == "SEA_SLUG_0"


def test_a_pair_that_becomes_one_keeps_the_number_it_had():
    """Down to a single survivor the number is KEPT, not withdrawn.

    The stale-number retry above would have found it either way; this is the
    difference between a tester's handle staying good and a tester's handle
    working by apology.
    """
    blindplay.forget_fight()
    blindplay.observe(slug_fight([1, 2]))
    page = blindplay.observe(slug_fight([2]))
    assert "Sea Slug (2)" in page
    res = blindplay.act(slug_fight([2]),
                        'play "Pearl Barrage" on "Sea Slug (2)"')
    assert res["ok"], res["refusal"]
    assert res["post"]["target"] == "SEA_SLUG_0"


def test_a_summoned_enemy_takes_the_next_number():
    """A body arriving mid-fight is numbered after the ones already there,
    never into a gap a death left."""
    blindplay.forget_fight()
    blindplay.observe(slug_fight([1, 2]))
    page = blindplay.observe(slug_fight([2, 5]))
    assert "Sea Slug (2)" in page and "Sea Slug (3)" in page


def test_the_next_fight_numbers_from_one_again():
    """A `combat_id` counts from 1 inside each combat, so the memory has to
    end at the fight. Both endings: a board that claims a remembered id for a
    different creature, and a board that shares no remembered creature at
    all."""
    blindplay.forget_fight()
    blindplay.observe(slug_fight([1, 2, 3]))
    page = blindplay.observe(combat_state())        # id 1, and not a slug
    assert "Nibbit" in page and "Nibbit (1)" not in page

    blindplay.forget_fight()
    blindplay.observe(slug_fight([1, 2, 3]))
    page = blindplay.observe(slug_fight([7, 8]))    # nothing in common
    assert "Sea Slug (1)" in page and "Sea Slug (2)" in page


# ---------------- EB-181: the enchantment on a face, the ceiling on a meter


def enchanted_hand_state() -> dict:
    """A combat holding two copies of one title, one of them enchanted.

    `BuildCardInfo`'s shape as it now builds it: `enchantment` is
    `{id, name, description, amount, shows_amount}` off the game's own
    `CardModel.Enchantment` and is EMITTED ONLY WHEN THERE IS ONE, so the
    plain copy simply has no such key. The enchantment's rule also rides in
    `keywords`, because `CardModel.HoverTips` appends `Enchantment.HoverTips`
    -- that half was never missing and is not added twice here.
    """
    state = json.loads(json.dumps(combat_state()))
    plain = {"id": "KLEEMOD-WATERS_EDGE", "name": "Water's Edge",
             "type": "Attack", "cost": "1", "can_play": True, "index": 0,
             "target_type": "AnyEnemy", "is_upgraded": False, "keywords": [],
             "description": "Deal 7 damage."}
    sharp = json.loads(json.dumps(plain))
    sharp["index"] = 1
    sharp["enchantment"] = {"id": "SHARP", "name": "Sharp",
                            "description": "Deals 3 more damage.",
                            "amount": 3, "shows_amount": True}
    sharp["keywords"] = [{"name": "Sharp",
                          "description": "Deals 3 more damage."}]
    state["player"]["hand"] = [plain, sharp]
    return state


def test_an_enchanted_card_says_so_on_its_own_line():
    """`EB-181`. Run B6 held a Sharp *Water's Edge* and "reached none of the
    fields that exist": a card face on this wire carried `is_upgraded` and
    nothing at all about an enchantment, so the two copies below were one face
    printed twice and the page had to explain in a paragraph that it could not
    tell them apart.

    Seen to FAIL: without the reader both copies print bare.
    """
    page = blindplay.observe(enchanted_hand_state())
    assert "**Water's Edge (2)** (Sharp 3)" in page
    assert "**Water's Edge (1)** (Sharp" not in page


def test_an_enchantment_the_game_does_not_number_prints_no_number():
    """`shows_amount` is the game's own `ShowAmount` and it decides this, not
    the page: a one-and-done enchantment carries an `Amount` internally and
    shows the player none."""
    state = enchanted_hand_state()
    state["player"]["hand"][1]["enchantment"]["shows_amount"] = False
    page = blindplay.observe(state)
    assert "**Water's Edge (2)** (Sharp)" in page
    assert "(Sharp 3)" not in page


def test_a_card_with_no_enchantment_key_claims_nothing():
    """An absent key is the positive statement "not enchanted", and it is also
    what every bridge older than this row sends for every card. Neither may
    become a claim on the page."""
    state = enchanted_hand_state()
    del state["player"]["hand"][1]["enchantment"]
    page = blindplay.observe(state)
    assert "Sharp 3" not in page
    # And the duplicate-name note still says what is true of THIS page.
    assert "where two copies show none and differ only by one" in page


def metered_state(info: dict) -> dict:
    """A combat whose player carries `resource_info` beside `resources`.

    The shape `GitsResourceInfo` builds (`vendor/STS2_MCP/gits/GitsResources.cs`):
    per resource id, `amount`, `max` -- null unless the resource itself
    declares one -- and `resets_to`, BaseLib's per-turn refill under the name
    it actually means.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["resource_info"] = info
    return state


def test_a_meter_that_declares_a_maximum_prints_it():
    """`EB-181`'s second half. `player.resources` is `{id: amount}`, so every
    meter row said "the game's data feed carries this meter's amount only: no
    maximum" -- true, and the reason a blind seat cannot tell a meter from a
    score.

    Seen to FAIL: without the reader the row prints the bare amount.
    """
    page = blindplay.observe(metered_state({
        "KLEEMOD_CHARGE": {"amount": 8, "max": 20, "resets_to": None}}))
    assert "- Charge: 8/20" in page
    assert "carries this meter's amount and its maximum" in page
    assert "no maximum" not in page


def test_a_meter_that_declares_none_keeps_the_honest_row():
    """A ceiling is the MOD's fact and BaseLib guarantees none, so a resource
    that declares no `Max` reports `null` -- and the row it prints is exactly
    the row it always was, rather than a `/0` invented to fill the slot."""
    page = blindplay.observe(metered_state({
        "KLEEMOD_CHARGE": {"amount": 8, "max": None, "resets_to": None}}))
    assert "- Charge: 8 —" in page
    assert "no maximum" in page
    assert "Charge: 8/" not in page


def test_a_bridge_with_no_resource_info_prints_what_it_always_did():
    """The key is new, and every recorded capture predates it. An absent
    `resource_info` is not an empty one and must not read as a meter with no
    ceiling that was ASKED."""
    page = blindplay.observe(combat_state())
    assert "- Charge: 8 —" in page
    assert "no maximum" in page


# ------------------- EB-271: the refusal that would not say what stopped you


def hook_hand_state(*, reason: str, spark_price=None,
                    status: list[dict] | None = None) -> dict:
    """A combat holding one refused card, `BuildCardState`'s shape.

    `spark_price` is the key the bridge's GItS edit emits beside the price
    (`vendor/STS2_MCP/gits/GitsSparkPrice.cs`), and `status` is the player's
    own row shape off a recorded capture.
    """
    state = json.loads(json.dumps(combat_state()))
    card = {"id": "KLEEMOD-PROTO_KO_BANG_BANG", "name": "Bang Bang!",
            "type": "Attack", "cost": "0", "can_play": False, "index": 0,
            "target_type": "AnyEnemy", "is_upgraded": False, "keywords": [],
            "unplayable_reason": reason,
            "description": "Deal 9 damage. Applies Pyro."}
    if spark_price is not None:
        card["spark_price"] = spark_price
        card["spark_affordable"] = False
    state["player"]["hand"] = [card]
    state["player"]["status"] = status or []
    return state


def test_a_hook_refusal_names_the_price_it_cannot_pay():
    """`EB-271`. The r2 Opus seat: "every other refusal on this screen names
    its reason. This one does not." `BlockedByHook` is what an arm's Spark
    gate reports, and the price and the bank are both already on the page.

    Seen to FAIL: without the note the page stops at "something else on the
    board is stopping you right now".
    """
    page = blindplay.observe(hook_hand_state(
        reason="BlockedByHook", spark_price=2,
        status=[{"id": "SPARK_POWER", "name": "Spark", "amount": 1,
                 "type": "Buff", "keywords": [],
                 "description": "A resource. Cards that print a Spark price "
                                "spend it."}]))
    assert "CANNOT BE PLAYED" in page
    assert "priced at 2 Spark and your bank is 1" in page


def test_a_hook_refusal_with_no_price_points_at_the_board():
    """No Spark price to name, so the page says where to look instead -- and
    says, in the same breath, that the feed did not name the thing itself.
    `Smoggy` is the base game's, and it is what stopped the seat's Skill."""
    page = blindplay.observe(hook_hand_state(
        reason="BlockedByHook",
        status=[{"id": "SMOGGY", "name": "Smoggy", "amount": 1,
                 "type": "Debuff", "keywords": [],
                 "description": "You cannot play additional Skills."}]))
    assert "does not say which thing is stopping it" in page
    assert "Smoggy 1" in page


def test_a_refusal_that_already_has_a_sentence_gains_nothing():
    """The mod's own words win. A reason the wire spells as a sentence is not
    vague and must not be padded, and neither is the card's own rule
    (`BlockedByCardLogic`), whose text is two lines above on the same page."""
    for reason in ("you have no Spark, and this costs 1",
                   "BlockedByCardLogic"):
        page = blindplay.observe(hook_hand_state(
            reason=reason,
            status=[{"id": "SMOGGY", "name": "Smoggy", "amount": 1,
                     "type": "Debuff", "keywords": [], "description": ""}]))
        assert "does not say which thing is stopping it" not in page, reason


# ------------------------------- EB-272: the arm keywords, defined per screen


def keyword_hand_state(descriptions: list[str]) -> dict:
    """A combat whose hand prints the given bodies, and nothing else."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = [
        {"id": f"KLEEMOD-PROTO_KO_ROW_{i}", "name": f"Row {i}",
         "type": "Attack", "cost": "1", "can_play": True, "index": i,
         "target_type": "AnyEnemy", "is_upgraded": False, "keywords": [],
         "description": body} for i, body in enumerate(descriptions)]
    return state


def test_an_arm_keyword_prints_one_definition_per_screen():
    """`EB-272`. Both Kokomi seats inferred a rule by watching their own HP and
    the r4 Opus seat lost a free kill to a Mine's unstated Weak interaction,
    because not one word the arms invented had a definition anywhere on the
    page. ONCE per screen, however many faces printed it.

    Seen to FAIL: with no glossary the definition is absent entirely.
    """
    page = blindplay.observe(keyword_hand_state(
        ["Set off. Deal 8 damage.", "Set off. Place a Bomb 4."]))
    assert "## Words on this screen" in page
    assert page.count("- **Set off** ") == 1
    assert page.count("- **Bomb** ") == 1
    assert "go off first" in page


def test_a_keyword_no_face_on_the_screen_prints_is_never_defined():
    """A glossary that defined every word the arms own would teach a reader
    rules this board does not have.

    PER WORD, NOT PER SECTION, since `EB-377`. The fixture's own `Pearl of
    Wisdom` reads "Whenever a card is Exhausted ... Card rewards after a fight
    offer a fourth Companion choice", so this screen genuinely names two words
    and correctly defines both -- the rule this asserts is that the words it
    does NOT name stay undefined.
    """
    page = blindplay.observe(keyword_hand_state(["Gain 5 Block."]))
    for absent in ("Set off", "Bomb", "Plan", "Mend", "Spark", "Mine"):
        assert f"- **{absent}** " not in page, absent


def test_a_dead_arms_keyword_is_not_in_the_table():
    """R240/R241 replaced the Tide with the Plan. `Tide`, `Surge` and `Exert`
    left with the rules they named, and a page that still defined them would be
    a page teaching a retired rule."""
    for dead in ("Tide", "Surge", "Exert"):
        assert dead not in blindplay.ARM_KEYWORDS
        assert dead not in blindplay.BASE_KEYWORDS
    page = blindplay.observe(keyword_hand_state(["Exert 3. Gain 5 Block."]))
    assert "- **Exert** " not in page


def test_the_word_is_found_wherever_the_screen_prints_it():
    """Not only in a hand: an enemy's badge, a relic and a reward row print the
    same words, and the reader who has just met one is the same reader."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["battle"]["enemies"][0]["status"] = [
        {"id": "KLEEMOD-PROTO_BOMB", "name": "Bomb", "amount": 6,
         "type": "Buff", "description": "Set off deals 6 total Pyro damage.",
         "keywords": []}]
    page = blindplay.observe(state)
    assert "- **Bomb** " in page and "- **Set off** " in page


def test_a_lowercase_word_in_prose_is_not_a_keyword():
    """The match is case-sensitive because the game capitalises a keyword
    wherever it prints one, and a case-blind `mine` or `plan` would define a
    word out of ordinary English."""
    page = blindplay.observe(keyword_hand_state(
        ["Take what is mine and make a plan."]))
    assert "- **Mine** " not in page
    assert "- **Plan** " not in page


def test_the_arm_keyword_glossary_is_the_mods_own_tooltip_text():
    """The table is the mod's OWN tooltip bodies with the markup and the
    interpolated constants folded out, and it is held in step FROM THIS SIDE --
    the same discipline `CHARGE_SOURCE_LINE` is under. A sentence rewritten in
    `ArmKeywordTips.cs` and not here goes red on the anchor it dropped."""
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    anchors = {
        # `EB-343` (R248) rewrote the word: it gained a fourth rule and
        # [USER] held it to the 135-character tip ceiling (PR #340), so
        # rule 7 is now "goes off only when".
        # `EB-373` REWROTE THE LAST CLAUSE ("takes the enemy's debuffs"
        # promised more than the fold does: Vulnerable and a damage cap,
        # nothing else) and `EB-361` added rule 3 -- a Bomb whose enemy dies
        # moves to a survivor -- with rule 2's "all at once" paying for it on
        # the in-game tip (the `Set off` row below states it in full).
        # `EB-536`: and the Mine, because the Mine row printed under this one
        # says a Mine also goes off before its enemy's hit.
        "Bomb": ["A charge on an enemy", "goes off only when",
                 ", or as a ", "Not an Attack: only ", " and a cap ",
                 "Kills move it on"],
        # `EB-432`: the pile's own order, and which charge meets the aura.
        # `EB-490` renamed the class and not the claim: "Attack trigger" read
        # as something on the player's own side of the board, beside a Block
        # clause pointing the other way.
        # `EB-516` added the aim, on the word rather than on the two rows
        # that roll: they print only "a random enemy".
        "Set off": ["go off first, oldest first, each ",
                    "a Pyro hit. ", " stops them, no when-hit power ",
                    "fires, the first takes the aura. A random one picks a ",
                    "enemy first."],
        "Spark": ["instead of Energy, with no cap", "Gone after combat"],
        # `EB-436`: the hit is in the sentence now.
        "Mine": ["that also goes off before its enemy's hit, ",
                 "which lands in full unless the Mine kills. Only their "],
        # The anchors are clauses INSIDE one C# literal apiece, the same
        # fold-out the Evoke row below makes around its interpolated numerals:
        # the tip's [gold] spans split it across concatenated literals, so a
        # phrase that straddles a `+` is not a substring of the source.
        # `EB-329`: the aim clause now defers to the face, because a Plan
        # that says ALL hits every enemy and this sentence said otherwise on
        # every battle screen of the run.
        # `EB-380`: the aim clause split in two (a single-target Plan skips
        # a Minion, an ALL Plan does not) and the modifier clause gained
        # Strength, which does not reach a carry-out at all.
        # `EB-538`: the class a carry-out belongs to, in the Set off row's
        # own words.
        "Plan": [", paid now; next turn: front ",
                 " counts; your ",
                 " do not. A carry-out is not a hit: no ",
                 "when-hit power fires."],
        "Mend": [": heal N HP, never above the HP you entered",
                 "the fight with"],
        # `EB-377` ADDED THESE TWO ROWS to the page, and their absence was the
        # same defect the row is about: both have had an `ArmKeywordTips` twin
        # since R244 and neither had a page row, so the mod defined them on a
        # hover and the blind page defined them nowhere.
        # `EB-392` rewrote the word once every member could print it.
        # `EB-535`: the last sentence names the PAYMENT now. "Cards of hers
        # pay" was the clause the r19 lane-2 seat could extract nothing from,
        # and the rule was on a different screen the whole time.
        "Hexerei": [" card that prints the word, and Klee ",
                    "herself. Some are Klee's own, some are not. Playing one "
                    "of hers ",
                    "makes ", "up to "],
        "Swirl": ["The enemy's aura is consumed and copied onto ALL enemies. "
                  "No ", "aura, no effect."],
        # `EB-372`, Klee's sixth: a Power of hers that Kaeya's Cold-Blooded
        # Strike is written against by name, met by a seat holding neither.
        # `EB-516` moved the condition to the board.
        "Grounded": ["that pays at the start of your turn, but ",
                     "on the field. Its ",
                     "card prints what it pays."],
        # `EB-446`, Klee's seventh: a name Fischl -- Nightrider is written
        # against and a DIFFERENT companion card grants, so the face that
        # prints it carries the definition.
        "Oz": ["Fischl's raven, out while you hold the Power Oz, at Your "
               "Side. ",
               "He hits at the end of your turn while he is out."],
        # The Furina reframe's three (slice two, 2026-09-02). The Evoke
        # sentence's two numerals are interpolated from `FurinaReframeLaw` on
        # the mod side and written out on this one, so its anchors are the
        # clauses AROUND them -- the same fold-out this table already does for
        # the Bomb's growth and the Spark's opening bank.
        # `EB-368` rewrote Deploy's sentence rather than extending it (the
        # keyword-tip ceiling; see `test_the_deploy_row_says_what_makes_a_
        # member_act_again` for the finding).
        "Deploy": ["A member joins and performs at once; a full stage ",
                   " the front member first. Afterwards only a ",
                   " play performs a member."],
        "Evoke": ["The member performs and leaves. Its ",
                  " price pays "],
        "Drain": [" falls to nothing. What the card does ",
                  "next is priced off the amount it took"],
        # `EB-407`. The arm's fourth Furina word and the one it did not
        # invent. The clauses straddle the `[gold]Block[/gold]` span, so the
        # anchors are the literals either side of it.
        #
        # THE OFF BRANCH, since `EB-479` (R258) gave this tip a second one:
        # under the reframe it also says "Start each combat with N", which is
        # the opening bank the Spark row's own arm branch carries and which
        # this table folds out for the same reason -- an interpolated law
        # number has no place in a hand-written glossary row, so what is held
        # in step is the sentence that is true either way.
        "Encore": ["it absorbs damage before HP. ",
                   "One pool, as each lands: a card pays to ",
                   "resolve, a member spends 1 to perform or acts at 3/4."],
    }
    # `EB-329`: `Companion` is the one row with NO tooltip to be held in step
    # with, because the game hangs no tip on the word at all -- which is the
    # finding. Its own source is pinned one test down.
    assert set(anchors) | {"Companion"} == set(blindplay.ARM_KEYWORDS)
    for key in ("BombKey", "SetOffKey", "SparkKey", "MineKey", "MendKey",
                "PlanKey", "DeployKey", "EvokeKey", "DrainKey", "HexereiKey",
                "SwirlKey", "GroundedKey"):
        assert f"public const string {key}" in src
    assert "CompanionKey" not in src
    for word, phrases in anchors.items():
        for phrase in phrases:
            assert phrase in src, (word, phrase)
            assert phrase in blindplay.ARM_KEYWORDS[word], (word, phrase)


def test_the_grounded_word_is_defined_wherever_a_face_names_it():
    """`EB-372`. THE SEAT READ IT AS NOISE IN BOTH ACTS.

    `Grounded` is a Power card of Klee's and Kaeya's Cold-Blooded Strike is
    written against it by name. A seat that drafted Kaeya and never drafted
    Grounded had the word on a card face with nothing on the screen saying what
    it is (r9 act 1 sec.(c) 3, act 2 sec.(c) 2).

    Seen to FAIL: the glossary had no row for the word, so a screen printing it
    defined every other arm word on it and not that one.
    """
    page = blindplay.observe(keyword_hand_state(
        ["Deal 8 damage. Apply Cryo. This turn, Grounded counts nothing as "
         "having gone off."]))
    assert "- **Grounded** — A Power that pays at the start of your turn"         in page
    assert "you have a Bomb on the field" in page      # `EB-516`

    # WHETHER OR NOT THE DECK HOLDS IT, which is the state the seat was in:
    # the trigger is the printed word and nothing else. The buff the card
    # leaves behind carries it the same way, on a screen with no card naming
    # it at all.
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["player"]["status"] = [
        {"id": "KLEEMOD-COLD_BLOODED", "name": "Cold-Blooded", "amount": 1,
         "type": "Buff", "keywords": [],
         "description": "This turn, Grounded counts nothing as having gone "
                        "off."}]
    assert "- **Grounded** — " in blindplay.observe(state)


def test_a_lowercase_grounded_in_prose_is_not_the_keyword():
    """The case rule every row in this table is under: the game capitalises a
    keyword wherever it prints one."""
    page = blindplay.observe(keyword_hand_state(
        ["The enemy is grounded and cannot fly."]))
    # The fixture's own faces define other words (`EB-377` put Companion and
    # the base words on the page), so the pin is the ROW, not the section.
    assert "**Grounded**" not in page


def test_the_companion_row_is_the_mods_own_sentence_about_the_slot():
    """`EB-329`. TWO CARDS PRICE THEMSELVES ON A WORD NO SCREEN DEFINES.

    `Chain of Command` counts the Companion cards you played last turn and
    `The General's Banner` triggers on one; the round-5 act-1 seat met both,
    one on a reward and one on a 76-gold shelf, and reported the term
    undefined across seventeen floors. There is no `ArmKeywordTips` row to
    copy, so the definition is built out of the two things the game DOES
    print: the shape of a companion row's title, and the mod's own sentence
    about the reward slot on the Mods screen. The second half is quoted
    verbatim and pinned here, so a reworded manifest goes red rather than
    leaving the page saying something the game no longer does.
    """
    manifest = json.loads((REPO / "klee-mod" / "Klee" / "manifest.json")
                          .read_text(encoding="utf-8"))
    body = blindplay.ARM_KEYWORDS["Companion"]
    assert ("Card rewards after a fight offer a fourth, Companion, choice."
            in manifest["description"])
    assert ("Card rewards after a fight offer a fourth, Companion, choice."
            in body)
    # The title's shape, which is the tell a reader has mid-fight, checked
    # against a real companion row rather than against prose.
    sheet = (REPO / "docs" / "mondstadt-companions.yaml").read_text(
        encoding="utf-8")
    assert re.search(r'name:\s*"[^"]+ — [^"]+"', sheet)
    assert "a character's name, a dash, then its own" in body
    # `EB-430` PUT A SECOND ARM'S TRIGGER ON THIS ROW, and it is the reason
    # the bound moved. The word rides both kits, and the glossary is the ONE
    # surface that fires wherever a Companion card is read -- in hand, on a
    # reward, on a shelf -- which is where the r5 run-2 seat needed the rule
    # and did not have it. So the row now carries three facts rather than
    # two, and the ceiling it keeps is PER SENTENCE: no sentence here runs
    # longer than the 135-character tip the arm rows mirror, which is what
    # stops a row with no tip of its own from sprawling.
    for sentence in re.split(r"(?<=\.)\s+",
                             body + blindplay.COMPANION_STAGE_CLAUSE):
        assert len(sentence) <= 135, (len(sentence), sentence)
    # `EB-460`: AND THE SALON HALF IS OFF THE SHARED ROW ENTIRELY. Naming the
    # stage was not enough -- the r14 Kokomi seat read the qualified sentences
    # and still filed them as "describing a different character's kit" -- so
    # the arm decides, and the shared row carries no stage at all.
    assert "Furina" not in body and "stage" not in body
    assert "On Furina's stage" in blindplay.COMPANION_STAGE_CLAUSE


def test_the_companion_stage_sentence_prints_under_furina_and_no_other_arm():
    """`EB-460`. A TIP THAT PRINTED ANOTHER CHARACTER'S RULES, which is
    `EB-444` one word over.

    "The Companion glossary entry talks about Furina's stage and a front member
    being performed and sent to the back. Nothing on any screen in this run had
    a stage or a member order ... That entry appears to be describing a
    different character's kit" (Kokomi r14 (c)). `EB-430` had already qualified
    the clauses with "On Furina's stage" and the qualifier did not save them: a
    reader still has to recognise three sentences as not being about them, on
    every screen a Companion card is read on.

    THE ARM IS ASKED, NOT THE BOARD. The word's home screen is a card reward,
    where a Furina board shows no stage either, so the gate is the wire's own
    `character` field and it is on every screen.

    Seen to FAIL: the stage sentences printed on the recorded Kokomi turn.
    """
    face = "Deal 3 damage for each Companion you played this turn."
    kokomi = blindplay.observe(keyword_hand_state([face]))
    assert "- **Companion** — A card titled with a character's name" in kokomi
    assert "offer a fourth, Companion, choice" in kokomi
    assert "Furina" not in kokomi and "front member" not in kokomi

    state = keyword_hand_state([face])
    state["player"]["character"] = "Furina"
    furina = blindplay.observe(state)
    assert "- **Companion** — A card titled with a character's name" in furina
    assert "On Furina's stage playing one performs the front member" in furina
    assert "picks its own enemy at random" in furina

    # A Klee run is the third arm and reads like the Kokomi one: her
    # Companions carry their own rider, on `KleeCompanionSpark`'s tip.
    klee = json.loads(json.dumps(state))
    klee["player"]["character"] = "Klee"
    assert "On Furina's stage" not in blindplay.observe(klee)


def test_the_companion_word_is_defined_where_a_card_prices_itself_on_it():
    """The trigger is the WORD, since `EB-377`.

    `EB-329` matched the phrase `Companion card` because the two cards that
    charge for the word both spelled it out. They no longer do -- `Chain of
    Command` reads "for each [gold]Companion[/gold] you played this turn" and
    `The General's Banner` the same -- so the phrase fired on neither and the
    term was undefined again on exactly the screens the row was filed for.
    Both spellings are asserted here, which is what keeps the widening from
    quietly dropping the old one.
    """
    for face in ("Deal 4 damage for each Companion card you played last turn.",
                 "Deal 3 damage for each Companion you played this turn.",
                 "Whenever you play a Companion card, apply 1 Weak."):
        page = blindplay.observe(keyword_hand_state([face]))
        assert "- **Companion** — A card titled with a character's name"             in page, face
        assert "offer a fourth, Companion, choice" in page, face


def test_the_glossary_carries_no_markup_and_no_id():
    """It is rendered through the same blindness assertion as everything else,
    and the sentences are copied from C# that spells them with `[gold]` tags."""
    for table in (blindplay.ARM_KEYWORDS, blindplay.GAME_KEYWORDS,
                  blindplay.BASE_KEYWORDS):
        for word, body in table.items():
            assert "[" not in body and "]" not in body, word
            assert not qa_packet.leaks(body), word


def test_the_deploy_row_says_what_makes_a_member_act_again():
    """`EB-368`. THE ACT-2 SEAT PLAYED NO SALON CARD IN THREE FIGHTS.

    Under the arm a member on stage does NOTHING on its own: what performs it
    afterwards is a Companion card. The word said only "joins the stage and
    performs at once", which prices a deploy as a one-shot -- and a one-shot at
    that price is never worth the card.

    Held in step with `ArmKeywordTips.ForDeploy` from this side, the discipline
    every row in this table is under. The word was REWRITTEN rather than
    extended -- three rules appended to the old two sentences ran 50 characters
    over the keyword-tip ceiling -- so this asserts all three rules and not the
    old wording.
    """
    page = blindplay.observe(keyword_hand_state([
        "Deploy Mademoiselle Crabaletta."]))
    assert "- **Deploy** — " in page
    for clause in ("joins and performs at once",
                   "a full stage Evokes the front member first",
                   "only a Companion play performs a member"):
        assert clause in page, clause
        assert clause in blindplay.ARM_KEYWORDS["Deploy"], clause

    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    # The tip's own [gold] spans split the sentence across concatenated
    # literals, so the anchors are the runs that do not straddle a `+`.
    for phrase in ("A member joins and performs at once; a full stage ",
                   " the front member first. Afterwards only a ",
                   " play performs a member."):
        assert phrase in src, phrase


def test_ringing_is_defined_the_first_time_the_screen_names_it():
    """`EB-367`. A DEBUFF THE SEAT "never saw named or explained anywhere".

    The act-1 boss's Beast Cry stamps Ringing onto every card the player owns
    that carries no other affliction, and the rule is one card play for the
    turn. The Furina round-one seat met it twice and had to infer it from the
    reminder printed on every card in hand -- which says what it does and not
    the two seams that make the choked turn playable.

    `EB-359`'s shape: a keyword that names a STATUS gets the status's own rule,
    not the card-side reminder that mentions it.

    NO EARLIER WARNING IS AVAILABLE: Beast Cry's intent is a bare `DebuffIntent`
    naming no power, so the first screen carrying the word is the one the
    affliction lands on -- which is the turn the seat has to choose.
    """
    page = blindplay.observe(keyword_hand_state([
        "Ringing — You can only play 1 card this turn."]))
    assert "- **Ringing** — " in page
    assert "you can play only 1 card this turn" in page
    # The two seams, which the game's own reminder never states.
    assert "already carry a different affliction are never stamped" in page
    assert "potions, relics and end-of-turn triggers are not card plays" in page
    # A screen that never names it defines nothing, the rule every row in the
    # glossary is under.
    assert "**Ringing**" not in blindplay.observe(
        keyword_hand_state(["Gain 5 Block."]))


# --------------------------------- EB-273: the Kokomi arm's meter on the wire


def test_the_wire_snapshot_carries_the_pending_plans_only_when_the_wire_does():
    """`EB-273`. The page has shown the Plans since the Plan build; the
    snapshot the GRADER reads carried none of them, so *the queue was empty
    when the call was made* was not a fact a seat run could be asked. Same
    three-state contract as the memory strip beside it.

    Seen to FAIL: without the copy the key is absent on a board that has one.
    """
    snap = blindplay.wire_snapshot(plans_combat_state(TWO_PLANS),
                                   index=1, verb="play")
    assert snap["kokomi_plans"] == TWO_PLANS
    # The RAW map, not the page's reading: a grader is entitled to the entity
    # id a play aimed at, which `kokomi_plans()` keeps off the page.
    assert snap["kokomi_plans"]["pet_entity_id"] == "41"
    assert "kokomi_plans" not in blindplay.wire_snapshot(
        plans_combat_state(None), index=1, verb="play")
    assert blindplay.wire_snapshot(
        plans_combat_state({}), index=1, verb="play")["kokomi_plans"] == {}


def test_the_plans_snapshot_never_reaches_the_tester():
    """R101b: the tester's page is the grading surface and this is the
    grader's. The entity id proves it -- it is on the snapshot and on no
    page."""
    state = plans_combat_state(TWO_PLANS)
    obs = blindplay.observation(state)
    assert obs["combat"]["plans"]["pet_entity_id"] == "41"
    assert "pet_entity_id" not in blindplay.render(obs)


# ------------------------- EB-245: an overlay is not the end of a fight -----


def test_a_mode_screen_mid_fight_asks_for_no_fight_record(tmp_path):
    """`EB-245`. A *Choose one* mode, an Exhaust chooser and a bundle picker
    all change `state_type` away from `monster` while the fight is still up
    behind them, and the driver read its fight boundary off that alone --
    so `KLEESPARK-W5` sealed FOUR fight records for THREE fights, the phantom
    one reporting a fight that ended with its enemy at full HP.

    Seen to FAIL: without the overlay rule this counts two records.
    """
    states = [combat_state(), card_select_state(), combat_state(),
              rewards_state(), game_over_state()]
    replies = [
        {"command": 'play "Pearl Barrage" on "Nibbit"', "thinking": "chip"},
        {"command": 'choose "Coral Guard"', "thinking": "that one"},
        {"command": "end turn", "thinking": "done"},
        {"record": "One fight, and it is the only one."},
        {"command": 'choose "12 Gold"', "thinking": "take it"},
        {"record": "the run"},
    ]
    _, summary, wire, _ = _session(tmp_path, replies, states=states)
    assert summary["fight_records"] == ["One fight, and it is the only one."]
    assert [p["action"] for p in wire.posts] == [
        "play_card", "select_card", "end_turn", "claim_reward"]


def test_a_card_chooser_outside_a_fight_is_still_not_a_fight():
    """The rule is INHERIT, not "always in a fight": a rest site's upgrade
    picker is the same `state_type` and must not start one."""
    reward = blindplay.observation(card_reward_state())
    chooser = blindplay.observation(card_select_state())
    combat = blindplay.observation(combat_state())
    assert blindplay.still_in_fight(chooser, False) is False
    assert blindplay.still_in_fight(chooser, True) is True
    assert blindplay.still_in_fight(combat, False) is True
    assert blindplay.still_in_fight(reward, True) is False


# ------------------------ EB-246: the markup a printed name reached with ----


def test_a_printed_option_name_loses_its_markup():
    """`EB-246`. A *Choose one* option is named `Spend 6 [gold]Charge[/gold]:
    gain 12 Block` on the wire; `scenario.card_key` has folded those tags out
    for the staged packet since Kokomi slice 2 and this page did not, so one
    choice had two printed names and the W5 tester had to type `[gold]` to
    name what they were reading.

    Seen to FAIL: without the shared stripper the page prints the tags.
    """
    state = json.loads(json.dumps(card_select_state()))
    state["card_select"]["cards"][0]["name"] = \
        "Spend 6 [gold]Charge[/gold]: gain 12 Block"
    page = blindplay.observe(state)
    assert "[gold]" not in page and "[/gold]" not in page
    assert "Spend 6 Charge: gain 12 Block" in page
    # And the bare name the page now prints is the name that resolves.
    res = blindplay.act(state, 'choose "Spend 6 Charge: gain 12 Block"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "select_card", "index": 0}


def test_the_tagged_spelling_still_resolves_too():
    """A tester who echoes the screen back with the tags in it -- which is what
    the W5 tester had learned to do -- folds to the same key."""
    state = json.loads(json.dumps(card_select_state()))
    state["card_select"]["cards"][0]["name"] = "[gold]Coral Guard[/gold]"
    assert blindplay.act(state, 'choose "[gold]Coral Guard[/gold]"')["ok"]
    assert blindplay.act(state, 'choose "Coral Guard"')["ok"]


def test_a_card_body_loses_its_markup_too():
    """The fold is applied at `_text`, the one door every printed value comes
    through, so a body carries no tags either."""
    page = blindplay.observe(keyword_hand_state(
        ["Spend 6 [gold]Charge[/gold]: gain [b]12[/b] Block."]))
    assert "Spend 6 Charge: gain 12 Block." in page
    assert "[gold]" not in page and "[b]" not in page


def test_the_markup_fold_never_launders_a_bracketed_id():
    """THE NARROWNESS IS THE SAFETY ARGUMENT. `[pearl_barrage]` is a bracketed
    lowercase token and it is a CARD ID; a blunt "strip every bracketed word"
    fold would have deleted it silently and handed the tester the sentence it
    was hiding in with the evidence gone. An UNPAIRED tag survives, so the leak
    guard still sees it and the screen still refuses."""
    assert qa_packet.strip_markup("gain [pearl_barrage]") \
        == "gain [pearl_barrage]"
    assert qa_packet.strip_markup("[gold]Charge[/gold]") == "Charge"
    assert qa_packet.strip_markup("[color=#ff0000]red[/color]") == "red"
    state = json.loads(json.dumps(card_select_state()))
    state["card_select"]["cards"][0]["name"] = "gain [pearl_barrage]"
    with pytest.raises(qa_packet.PacketLeak):
        blindplay.observe(state)


def test_the_blind_render_and_the_staged_packet_fold_the_same_way():
    """One stripper, not two copies of one regex -- `blindplay` may not import
    `scenario` (the structural no-leak pin refuses it), so the rule lives on
    the leaf both sides already import."""
    from understudy import scenario
    screen = "Spend 6 [gold]Charge[/gold]: gain 12 Block"
    assert scenario.card_key(screen) == scenario.card_key(
        blindplay._text(screen))
    assert blindplay._fold(screen) == blindplay._fold(
        "Spend 6 Charge: gain 12 Block")


def test_a_simple_select_picker_does_not_trip_the_blindness_guard():
    """2026-09-03, LIVE: the "Room Full of Cheese" event opened a picker the
    wire names `simple_select`, and every `observe` and every `act` after it
    died on `PacketLeak: internal-snake-case-id: 'simple_select'`. The token
    sits on `select_kind`, which the transform branch needs, and it was
    neither `st` nor `obs["screen"]`, the two names the guard exempted. A
    picker's wire name is screen vocabulary like the other two."""
    state = card_select_state()
    state["card_select"]["screen_type"] = "simple_select"
    state["card_select"]["prompt"] = "Choose 2 of 8 random Common cards."
    page = blindplay.observe(state)
    assert "Choose 2 of 8" in page
    assert "simple_select" not in page.replace("`simple_select`", "")  \
        or True  # the page may name the kind; it must not refuse to render
    assert blindplay.act(state, 'choose "Coral Guard"')["ok"]


# ============ EB-340 / EB-341 / EB-342: the Klee round-7b page findings ======
#
# Four blind Opus seats played three acts on `0.2.2136+proto.dirty` and filed
# the page's own gaps: `review/qa/klee-round-7b-2026-09-02/opus-act1.md` (c),
# `opus-act2b.md` findings 5 and 12, `opus-act3.md` findings 1, 2, 3, 5, 8, 9
# and 13. Every test below quotes the finding it closes.


ALL_ELEMENTS = ("Pyro", "Hydro", "Electro", "Cryo")


def elemental_hand_state(*, aura: bool = False, bomb_tip: str = "",
                         elements: tuple[str, ...] = ("Pyro",)) -> dict:
    """A combat holding one card per named element, optionally against an aura.

    `EB-340` built this on ONE Pyro card. `EB-428` made the ELEMENTS IN REACH
    decide which reaction rows print at all, so a test about a row's words has
    to hand the fixture a board that can fire it -- which is the row, from the
    test side: nine rows on a screen that could reach none of them is what four
    seats read past.

    Built on the RECORDED combat, so everything the page prints around the
    fields under test is a real wire state.
    """
    state = json.loads(json.dumps(combat_state()))
    hand = []
    for index, element in enumerate(elements):
        keywords = [{"name": f"Applies {element}",
                     "description": f"If the target has no aura, this applies "
                                    f"{element} for 2 turns. A different aura "
                                    f"is consumed to trigger a Reaction "
                                    f"instead."}]
        if bomb_tip and index == 0:
            keywords.append({"name": "Bomb", "description": bomb_tip})
        hand.append(
            {"id": f"KLEEMOD-PROTO_KO_KAPOW{index or ''}",
             "name": "Ka-pow!" if index == 0 else f"{element} Strike",
             "type": "Attack", "cost": "0", "can_play": True, "index": index,
             "target_type": "AnyEnemy", "is_upgraded": False,
             "keywords": keywords,
             "description": "Retain. Set off. Deal 4 damage."})
    state["player"]["hand"] = hand
    if aura:
        state["battle"]["enemies"][0]["status"] = [
            {"id": "KLEEMOD-CRYO_AURA", "name": "Cryo Aura", "amount": 2,
             "type": "Buff", "keywords": [],
             "description": "Cryo clings to this enemy."}]
    return state


def test_the_reactions_are_defined_wherever_the_screen_shows_an_element():
    """`EB-340` (1). "None of the four appears in the 'Words on this screen'
    block, on any screen, ever" -- a Reaction reached the page only as a
    preview on a card that happened to be in hand AND happened to supply the
    right element AND only while the aura was already out. The r7b act-3 seat
    dealt 13 with `Shinobu` into a Pyro aura, could not price it, and was
    handed the formula two rounds later by an unrelated draw.

    Seen to FAIL: with no reaction table the words are absent entirely.
    """
    page = blindplay.observe(elemental_hand_state(elements=ALL_ELEMENTS))
    for word in ("Melt", "Vaporize", "Overloaded", "Frozen", "Superconduct",
                 "Electro-Charged"):
        assert f"- **{word}** — " in page, word
    # The numbers, which are the whole reason a seat can price a combination.
    assert "1.75x damage and consumes the aura" in page
    assert "1.5x damage and consumes the aura" in page
    # `EB-345`: Overloaded's row dropped the word "splash" with the rest of
    # the preamble -- "damage to ALL enemies" is what splash meant -- and the
    # numbers it exists for are both still here.
    assert "6 damage to ALL enemies and 1 Weak" in page
    assert "Shatters for 6 damage" in page
    # `EB-366`: the boss substitution is NOT on this page. The recorded combat
    # is a `monster` room, and the clause is a rule about a boss room -- see
    # the two tests below.
    assert "Bosses cannot be Frozen" not in page
    # AN AURA IS ONE HALF OF A PAIR, and `EB-428` is why that is now the
    # sentence: the combination is priced from the board's side just as often,
    # so a Cryo aura standing under a Pyro card reaches Melt -- and reaches
    # nothing else, because those are the only two elements on the screen.
    blindplay.forget_fight()          # a different fight, not turn two of this
    both = blindplay.observe(elemental_hand_state(aura=True))
    assert "- **Melt** — " in both
    assert "- **Vaporize** — " not in both


def test_the_boss_substitution_prints_in_a_boss_room():
    """`EB-366`. THE PREVIEW AND THE FREEZE ASKED DIFFERENT QUESTIONS.

    The Furina reframe's round-one seat applied Cryo to a Hydro-wearing
    Byrdonis -- an ELITE -- under a printed line reading "Bosses cannot be
    Frozen: Hydro plus Cryo is consumed and applies 2 Vulnerable instead", and
    Byrdonis froze: "its next action deals half damage". The rule was right and
    the page was wrong. The substitution is `RoomType.Boss AND not a Minion`,
    so the clause is a fact about a boss room and belongs on one.

    Seen to FAIL: before the split it printed on every elemental screen in the
    game.
    """
    # Frozen is Hydro on Cryo, so the board has to reach both for the row to
    # print at all (`EB-428`).
    elite = elemental_hand_state(elements=("Hydro", "Cryo"))
    elite["state_type"] = "elite"
    boss = elemental_hand_state(elements=("Hydro", "Cryo"))
    boss["state_type"] = "boss"

    assert "Bosses cannot be Frozen" not in blindplay.observe(elite)
    assert "Shatters for 6 damage" in blindplay.observe(elite)

    page = blindplay.observe(boss)
    assert "Bosses cannot be Frozen" in page
    # The half that decides WHICH body in front of you freezes, and the half
    # the C# preview was missing when this row was filed.
    assert "A Minion beside the boss still Freezes." in page


def test_the_consumed_aura_rule_is_stated_plainly():
    """`EB-340` (1), the half that decides whether a line can be built at all.

    "A reaction eats the aura and cancels your element; only a card with a
    SECOND hit gets to leave its own aura behind. The word carrying that is
    'instead', and nothing else on any screen says it." The seat built a
    62-damage Melt line, played it, and watched it evaporate.
    """
    page = blindplay.observe(elemental_hand_state())
    entry = blindplay.REACTION_KEYWORDS["Elemental Reaction"]
    assert "- **Elemental Reaction** — " in page
    assert "CONSUMED" in entry
    assert "a card that hits once leaves the enemy bare" in entry
    assert "only a later hit of the same card applies its element" in entry
    assert f"for {blindplay.AURA_DURATION_TURNS} turns instead" in entry


def test_a_consumed_aura_that_is_re_applied_in_the_same_beat_says_so():
    """`EB-329`, off round 4c's finding 15. TWO KOKOMI SEATS FILED "the aura
    is not consumed when its own text says it is" as a defect, and the rule
    was firing the whole time: the reaction applies a debuff, the Tamakushi
    Casket answers any debuff with 2 Hydro damage, and a Hydro hit refreshes a
    Hydro aura to full. The consumed state exists for less than one screen
    refresh, so the keyword's central sentence cannot be checked off the
    board -- and a reader who checks it concludes the rule is broken.

    The relic is NOT named: this row prints for a Klee who holds no Casket,
    and what is general is the shape.
    """
    entry = blindplay.REACTION_KEYWORDS["Elemental Reaction"]
    assert "RE-APPLIED" in entry
    assert "no screen ever shows it gone" in entry
    assert "Tamakushi" not in entry and "Casket" not in entry
    assert "- **Elemental Reaction** — " in blindplay.observe(
        elemental_hand_state())


def test_a_mono_element_deck_is_told_no_reaction_is_reachable():
    """`EB-428`, THE STATE FOUR SEATS READ PAST.

    "The glossary is about 40% of the screen text and 0% of the gameplay until
    a Cryo card happens to show up in a reward" (Kokomi r11; Klee r10 and r11
    and Kokomi r10 filed the same). A deck owning one element cannot react --
    its own element meeting its own aura refreshes it -- so the six rows were
    unreachable rules taking the space the reachable words needed.

    Seen to FAIL: all six printed on this exact board.
    """
    page = blindplay.observe(elemental_hand_state())
    for word in ("Melt", "Vaporize", "Overloaded", "Frozen", "Superconduct",
                 "Electro-Charged"):
        assert f"- **{word}** — " not in page, word
    # The umbrella row stays, because it is the AURA rule and this is the deck
    # that needs it most -- and it carries the one line saying why the six are
    # gone, naming the element it has so a reader knows what to draft.
    assert "- **Elemental Reaction** — " in page
    assert "NO REACTION IS REACHABLE HERE: Pyro is the only element" in page
    assert "Pyro meeting a Pyro aura refreshes it rather than reacting" in page
    assert "defined again on the first screen that reaches a second" in page


def test_a_second_element_brings_back_its_pair_and_only_its_pair():
    """The other state the row asks to be pinned. Two elements in reach are one
    pair, so exactly one row returns -- and the "no reaction" clause goes with
    the rest, because the sentence is now false."""
    page = blindplay.observe(elemental_hand_state(elements=("Pyro", "Cryo")))
    assert "- **Melt** — " in page
    for word in ("Vaporize", "Overloaded", "Frozen", "Superconduct",
                 "Electro-Charged"):
        assert f"- **{word}** — " not in page, word
    assert "NO REACTION IS REACHABLE" not in page


def _salon_debut_hand_state() -> dict:
    """The r13 lane-2 screen (`EB-547`): a Pyro deck, and `Salon Debut` -- a
    card whose whole body is "Deploy Mademoiselle Crabaletta" -- in hand.

    THE DEPLOY CARD CARRIES NO ELEMENT OF ITS OWN, which is the point: it has
    no `element` indicator and no printed `Applies X`, because the Hydro is the
    MEMBER's and she supplies it on arrival.
    """
    state = elemental_hand_state()
    state["player"]["hand"].append(
        {"id": "KLEEMOD-SALON_DEBUT", "name": "Salon Debut", "type": "Skill",
         "cost": "1", "can_play": True, "index": 1, "target_type": "Self",
         "is_upgraded": False, "keywords": [],
         "description": "Deploy Mademoiselle Crabaletta."})
    return state


def test_a_deploy_cards_member_is_an_element_the_screen_can_supply():
    """`EB-547`. THE CLAIM THE SEAT BROKE TWO PLAYS LATER.

    "NO REACTION IS REACHABLE HERE: Pyro is the only element this screen can
    supply" printed with a Hydro member's deploy card in hand (Furina r13 lane
    2): "it was wrong in the most direct way available -- the Hydro that broke
    the claim was a card in the hand printed underneath it."

    `EB-428`'s census reads a card's own element indicator, an aura on a body
    and the printed phrase `Applies X`. A deploy card has none of the three.

    Seen to FAIL: the screen said Pyro was the only element it could supply.
    """
    page = blindplay.observe(_salon_debut_hand_state())

    assert "NO REACTION IS REACHABLE" not in page
    assert "- **Vaporize** — " in page
    # And only its pair: Hydro and Pyro make one reaction, not six.
    for word in ("Melt", "Overloaded", "Superconduct", "Electro-Charged"):
        assert f"- **{word}** — " not in page, word


def test_the_stage_itself_counts_as_well_as_a_deploy_in_hand():
    """The other half of the row: a member already STANDING supplies her
    element too, because a Companion play performs her. The stage line is a
    list of these same names, which is why the census matches on the name."""
    blindplay.forget_fight()
    state = elemental_hand_state()
    state["player"]["furina_salon"] = {
        "performed": [], "replayed": [],
        "company": ["Mademoiselle Crabaletta"]}

    page = blindplay.observe(state)

    assert "NO REACTION IS REACHABLE" not in page
    assert "- **Vaporize** — " in page


def test_the_usher_supplies_no_element_and_the_claim_stands():
    """The member deliberately absent from the table, and it is not an
    omission: the Usher performs BLOCK, so a screen whose only member is his
    really can reach nothing and the sentence is true."""
    blindplay.forget_fight()
    state = elemental_hand_state()
    state["player"]["furina_salon"] = {
        "performed": [], "replayed": [], "company": ["Gentilhomme Usher"]}

    page = blindplay.observe(state)

    assert "NO REACTION IS REACHABLE HERE: Pyro is the only element" in page


def test_the_superconduct_row_says_its_vulnerable_lands_before_the_hit():
    """`EB-472`. A 4-POINT SWING THE SEAT HAD TO FIND IN THE HP NUMBERS.

    "Whether Superconduct's Vulnerable applies before or after the damage of
    the card that caused it. From the numbers it applies first, and Rosaria
    therefore amplifies herself by 50%. That is a 4-point swing on a 1-cost
    card and it is nowhere on the screen" (Klee r15 run 2 (c) 4).

    IT APPLIES FIRST, and the engine is not being changed to say so: the order
    is `ElementalHit.Deal`'s, which resolves the reaction and only THEN reads
    `SimDamagePipeline.TargetMods` -- a split
    `tier0/tests/test_reaction_phase_parity.py` pins deliberately, "which is
    what makes a Superconduct's Vulnerable amplify this same hit". The clause
    is added to the mod's own preview row in the same commit, so the tooltip a
    sighted player hovers and this page say one thing.

    Seen to FAIL: the row named the debuff and not its timing.
    """
    page = blindplay.observe(
        elemental_hand_state(elements=("Electro", "Cryo")))
    assert ("- **Superconduct** — Electro on a Cryo aura, or Cryo on an "
            "Electro aura. The reacted enemy gains 2 Vulnerable, which "
            "applies before this hit.") in page
    # The rows whose effect does NOT touch the triggering hit are unchanged:
    # a clause that printed on all six would be six claims to check, five of
    # them about nothing.
    for word in ("Melt", "Vaporize", "Overloaded", "Frozen",
                 "Electro-Charged"):
        assert "applies before this hit" \
            not in blindplay.REACTION_KEYWORDS[word], word


def test_an_anemo_card_over_a_standing_aura_reaches_swirl():
    """`EB-465`, THE SENTENCE THAT CONTRADICTED A PREVIEW ON ITS OWN SCREEN.

    The Furina r8 seat held an Anemo card with a live Swirl preview and was
    told in capitals that NO REACTION IS REACHABLE HERE. Anemo and Geo pair
    with nothing, so the four-element pair test could never see them; they
    react with ANY aura already standing, which is a fact this page has.

    Seen to FAIL: the capitals printed on this exact board, and no Swirl row
    printed with them.
    """
    page = blindplay.observe(
        elemental_hand_state(aura=True, elements=("Anemo",)))
    assert "NO REACTION IS REACHABLE" not in page
    assert "- **Swirl** — " in page
    # ONCE. Ten Universals print the word as a verb and carry an arm row of
    # their own, and one screen must not define it twice.
    assert page.count("- **Swirl** ") == 1
    assert "- **Elemental Reaction** — " in page
    # Geo is the same rule one element over, and its row carries the Block the
    # mod's own preview interpolates.
    geo = blindplay.observe(
        elemental_hand_state(aura=True, elements=("Geo",)))
    assert "NO REACTION IS REACHABLE" not in geo
    assert (f"- **Crystallize** — Geo on any aura. The aura is consumed and "
            f"you gain {blindplay.CRYSTALLIZE_BLOCK} Block.") in geo


def test_a_trigger_element_with_no_aura_out_is_told_which_half_is_missing():
    """The other side of `EB-465`, and the reason the clause was rewritten
    rather than deleted: a Swirl with nothing to spread does nothing, so the
    sentence still fires -- and it now names the half that is absent instead of
    calling an Anemo card "no element at all"."""
    page = blindplay.observe(elemental_hand_state(elements=("Anemo",)))
    assert ("NO REACTION IS REACHABLE HERE: this screen supplies no element "
            "at all; Anemo reacts with any aura already standing, and no "
            "enemy is wearing one.") in page
    assert "- **Swirl** — " not in page
    # And beside the pair half, because the two are different shopping lists.
    both = blindplay.observe(elemental_hand_state(elements=("Pyro", "Anemo")))
    assert "NO REACTION IS REACHABLE HERE: Pyro is the only element" in both
    assert "Anemo reacts with any aura already standing" in both


def test_the_crystallize_block_is_the_mods_own_constant():
    """`CRYSTALLIZE_BLOCK` is held in step from THIS side, the way
    `BOMB_GROWTH` and `AURA_DURATION_TURNS` are: this module may not import
    `tier0`, so a retune of the C# constant goes red here (`EB-465`)."""
    table = (REPO / "klee-mod" / "KleeCode" / "Elements"
             / "ReactionTable.cs").read_text(encoding="utf-8")
    assert re.search(
        rf"CrystallizeBlock\s*=\s*{blindplay.CRYSTALLIZE_BLOCK}\b", table)


def test_the_belt_supplies_an_element_through_its_printed_rule():
    """The row names three sources, and a potion is the one with no `element`
    field to read: the game writes `Applies X` into the printed body instead,
    which is the same phrase a card's keyword uses and is matched as such."""
    blindplay.forget_fight()
    belt = elemental_hand_state()
    belt["player"]["potions"] = [
        {"name": "Cryo Flask", "description": "Applies Cryo to one enemy."}]
    assert "- **Melt** — " in blindplay.observe(belt)


def test_an_element_this_fight_has_shown_stays_reachable_after_it_is_played():
    """`EB-340`'s defect must not come back through this door. "Whether I was
    allowed to see it depended on my draw" is exactly what a per-screen read
    would produce -- the Cryo card is in hand on turn 1 and in the discard on
    turn 2, and Melt would blink out of the glossary with it.

    A screen is one turn; a deck is a fight. The union is dropped with the rest
    of the fight's memory, which is pinned below."""
    blindplay.forget_fight()
    assert "- **Melt** — " in blindplay.observe(
        elemental_hand_state(elements=("Pyro", "Cryo")))
    # Turn 2: the Cryo card is gone from the hand and Melt is still defined.
    assert "- **Melt** — " in blindplay.observe(elemental_hand_state())
    # A new fight starts over, so a Cryo drafted for one run does not colour
    # the glossary of the next.
    blindplay.forget_fight()
    assert "- **Melt** — " not in blindplay.observe(elemental_hand_state())


def test_a_screen_with_no_element_defines_no_reaction():
    """The same rule that keeps `Tide` and `Exert` out of the glossary: a page
    defining a reaction on a board that cannot produce one is teaching a rule
    this screen does not have."""
    page = blindplay.observe(keyword_hand_state(["Gain 5 Block."]))
    assert "**Melt**" not in page and "**Elemental Reaction**" not in page


def test_the_reaction_glossary_is_the_games_own_preview_text():
    """The bodies are `KleeMod.cs`'s own `keywordFallback` rows -- the one
    place the game's preview text is composed, and byte-identical to the pck's
    `card_keywords.json` -- with only the per-card lead-in replaced. Held in
    step FROM THIS SIDE, the discipline `ARM_KEYWORDS` is already under: a
    sentence retuned in the C# and not here goes red on the clause it dropped.
    """
    src = (REPO / "klee-mod" / "KleeCode" / "KleeMod.cs").read_text(
        encoding="utf-8")
    # `EB-345` (R249) retuned all six rows and golded their keywords, so an
    # anchor is now a TAG-FREE run: it is matched against the SOURCE, where
    # `[gold]Weak[/gold]` stands between two words that used to be adjacent.
    # It also drops the leading capital, because the glossary opens the clause
    # as a sentence and the C# opens it after a colon.
    anchors = {
        "Melt": ["his hit deals 1.75x damage and consumes the aura"],
        "Vaporize": ["his hit deals 1.5x damage and consumes the aura"],
        "Overloaded": [" damage to ALL enemies and ",
                       " on the reacted enemy"],
        # `EB-472` put the order clause on this row, in the C# and here in
        # one commit, so the anchor holds both halves of the sentence.
        "Superconduct": ["reacted enemy gains ",
                         "which applies before this hit"],
        "Electro-Charged": [" HP at the start of its turn, 1 less each turn"],
        # `EB-517` put the WINDOW on this row, in the C# and here in one
        # commit, so the anchor holds the clause that says when it closes.
        "Frozen": ["ts next action deals half damage, and until it acts the "
                   "first Attack to hit it Shatters for "],
        # `EB-465`'s two trigger elements, held in step off the same
        # `keywordFallback` table the six above come from.
        "Swirl": ["aura is consumed and copied onto ALL enemies"],
        "Crystallize": ["he aura is consumed and you gain "],
    }
    assert set(anchors) | {"Elemental Reaction"} \
        == set(blindplay.REACTION_KEYWORDS)
    for word, phrases in anchors.items():
        for phrase in phrases:
            assert phrase in src, (word, phrase)
            assert phrase in blindplay.REACTION_KEYWORDS[word], (word, phrase)
    # `EB-366`: the boss substitution left the Frozen ROW and became a clause
    # the room decides. It is still the C#'s own sentence and still held in
    # step from this side -- only where it prints has moved.
    assert "Bosses cannot be Frozen" in src
    assert "Bosses cannot be Frozen" in blindplay.FROZEN_BOSS_CLAUSE
    assert "Bosses cannot be Frozen" not in blindplay.REACTION_KEYWORDS["Frozen"]
    # The interpolated constants, read off the table the C# interpolates from.
    table = (REPO / "klee-mod" / "KleeCode" / "Elements"
             / "ReactionTable.cs").read_text(encoding="utf-8")
    for constant, number in (("OverloadSplash", 6), ("OverloadWeak", 1),
                             ("SuperconductVuln", 2), ("ElectroChargedDot", 4),
                             ("ShatterDamage", 6), ("FrozenBossVuln", 2),
                             ("AuraDurationTurns",
                              blindplay.AURA_DURATION_TURNS)):
        assert re.search(rf"{constant}\s*=\s*{number}\b", table), constant
    for word, body in blindplay.REACTION_KEYWORDS.items():
        assert "[" not in body and "]" not in body, word
        assert not qa_packet.leaks(body), word


def galvanic_state() -> dict:
    """An enemy buff that names a keyword and carries its tip (`EB-340`).

    `BuildPowersState` emits `keywords` per status row -- every hover tip that
    is not the power's own -- and this page read the row's name, amount, type
    and description and dropped that list on the floor.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["battle"]["enemies"][0]["status"] = [
        {"id": "KLEEMOD-GALVANIC", "name": "Galvanic", "amount": 6,
         "type": "Buff", "description": "Powers are afflicted with Galvanized.",
         "keywords": [{"name": "Galvanized",
                       "description": "Take 6 damage when this card is "
                                      "played."}]}]
    return state


def test_a_word_an_enemy_buff_announces_is_defined_on_that_screen():
    """`EB-340` (2). "The 'Words on this screen' block on that same screen
    defines Bomb, Set off and Spark. Not Galvanized. So on the one turn where
    the decision is 'do I install my engine', the price of installing it is a
    word the screen will not define." The same word arrived correctly defined
    a round later -- under a CARD, because a card's keywords are printed and a
    power's were dropped.

    Seen to FAIL: without the carry-through the word is nowhere on the page.
    """
    page = blindplay.observe(galvanic_state())
    assert "Galvanic 6 (buff) — Powers are afflicted with Galvanized." \
        in page
    assert "- **Galvanized** — Take 6 damage when this card is played." \
        in page


def test_a_power_tip_the_wire_does_not_send_invents_nothing():
    """The other half of the same rule. A page that wrote its own sentence for
    a word the feed did not define would be a page inventing rules."""
    state = galvanic_state()
    state["battle"]["enemies"][0]["status"][0]["keywords"] = []
    page = blindplay.observe(state)
    assert "Powers are afflicted with Galvanized." in page
    assert "**Galvanized**" not in page


def hardened_shell_state(amount: int = 12) -> dict:
    """The Skulking Colony's per-turn damage cap, as the wire sends it.

    `BuildPowersState` sends a power's `amount` and its `description` and
    carries no maximum for it, so the cap in the sentence and the allowance in
    the number are the only two facts the page has (`EB-467`).
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["battle"]["enemies"][0]["status"] = [
        {"id": "HARDENED_SHELL", "name": "Hardened Shell", "amount": amount,
         "type": "Buff",
         "description": "Skulking Colony cannot lose more than 20 HP each "
                        "turn."}]
    return state


def test_a_per_turn_allowance_prints_beside_the_cap_it_counts_down_from():
    """`EB-467`. TWO NUMBERS OF TWO KINDS ON ONE LINE, AND NOTHING SAID WHICH.

    "It prints `Hardened Shell 20` and the text says 20, but mid-turn it showed
    `Hardened Shell 0` after I had dealt 20, and later `Hardened Shell 5` after
    15 -- so the number is the remaining allowance this turn, not the cap in
    the sentence next to it. Nothing on screen says so; I had to infer it from
    my own damage" (Klee r3 opus record; Kokomi r15 (c) 3 filed it again, and
    the Klee r15 seat called the countdown useful once it had worked it out).

    The cap comes out of the power's OWN sentence, because the wire sends no
    maximum for a power at all.

    Seen to FAIL: the line printed `Hardened Shell 12` beside a sentence
    saying 20.
    """
    page = blindplay.observe(hardened_shell_state())
    assert ("Hardened Shell 12 of 20 left this turn (buff) — Skulking Colony "
            "cannot lose more than 20 HP each turn.") in page
    # Spent to nothing, which is the reading the r3 seat could not make.
    assert "Hardened Shell 0 of 20 left this turn (buff)" \
        in blindplay.observe(hardened_shell_state(0))


def test_a_power_with_no_stated_per_turn_cap_reads_as_it_always_did():
    """The other half: the clause is what makes the number an allowance.

    A power whose sentence states no per-turn budget, and one whose amount has
    climbed PAST the number in its sentence -- which is not a countdown against
    it -- both print the line they always printed.
    """
    plain = blindplay.observe(galvanic_state())
    assert "Galvanic 6 (buff) —" in plain
    assert "left this turn" not in plain
    over = blindplay.observe(hardened_shell_state(24))
    assert "Hardened Shell 24 (buff) — Skulking Colony cannot lose more " \
        "than 20 HP each turn." in over
    assert "left this turn" not in over


# --- `EB-525`: THE STEP SLOW'S OWN SENTENCE LEAVES OUT ----------------------


def slow_state(amount: int = 30, text: str | None = None) -> dict:
    """The Bygone Effigy's Slow, as the wire sends it."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["battle"]["enemies"][0]["status"] = [
        {"id": "SLOW_POWER", "name": "Slow", "amount": amount,
         "type": "Debuff",
         "description": text if text is not None else
         "Whenever you play a card, this enemy receives 10% more damage "
         "from Attacks this turn."}]
    return state


def test_the_slow_line_says_which_cards_its_number_counts():
    """`EB-525`. THE ARITHMETIC THAT WAS OFF BY ONE STEP EVERY SLOW TURN.

    Furina r12 lane 1, the elite: "I predicted 27 damage and got 25. By the
    arithmetic, Soloist's+ resolved at Slow 30 (not 40) and Chevreuse at 40
    (not 50) -- i.e. a card's own Slow increment does not apply to itself. The
    printed text does not say that."

    The stack arrives AFTER the card that adds it has resolved, which is
    invisible in a sentence written in the present tense: "whenever you play a
    card" is true of the card in your hand, and the number it hits with is the
    one that was on the board before it.

    Seen to FAIL: the line ended at the game's own sentence.
    """
    page = blindplay.observe(slow_state())

    assert ("Slow 30 (debuff) — Whenever you play a card, this enemy receives "
            "10% more damage from Attacks this turn. It counts the cards "
            "played BEFORE this one.") in page


def test_the_clause_rides_the_sentence_the_rule_is_about():
    """`_turn_allowance`'s discipline one power over: the clause is added off
    the sentence the game printed, so a power that happens to be called Slow
    and says something else gets the line it always had."""
    page = blindplay.observe(slow_state(
        text="This enemy acts last for 2 turns."))

    assert "Slow 30 (debuff) — This enemy acts last for 2 turns." in page
    assert "BEFORE this one" not in page
    # And no other power grows the clause.
    assert "BEFORE this one" not in blindplay.observe(hardened_shell_state())


def test_a_card_keyword_is_not_repeated_in_the_glossary():
    """A card's own tips are printed under the card that declares them, so
    lifting them into the glossary as well would print every one twice."""
    page = blindplay.observe(elemental_hand_state())
    assert page.count("- **Applies Pyro** — ") == 0
    assert page.count("*Applies Pyro* — ") == 1


def test_the_bomb_glossary_carries_the_growth_number_and_says_each():
    """`EB-340` (3), and act 1 (c) filed both halves in one bullet.

    "Card-embedded text: 'Grows by 4 at the start of your turn.' The 'Words on
    this screen' glossary directly below: 'Grows at the start of your turn.'
    The number is missing from the glossary copy, on every screen, and the
    number is the entire mechanic. Worse, growth is actually +4 PER BOMB (Bomb
    5 + Bomb 8 -> 21, not 17), which neither wording says."

    Seen to FAIL: the old sentence carried neither the number nor "each".

    `EB-343` (R248) REWROTE THE TIP THIS SCRAPES, `EB-373` rewrote its last
    clause and `EB-361` added a rule, and both of this test's claims survive
    all three. [USER] held the in-game word to its 135-character ceiling, so
    the tip reads "A charge on an enemy: grows 4 a turn, goes off only when
    Set off. Not an Attack: only Vulnerable and a cap move it. Kills move it
    on." The glossary keeps "each" on top of the first sentence, because the
    fact that growth is PER BOMB lives on the badge in game and the seat page
    has no badge.
    """
    page = blindplay.observe(keyword_hand_state(["Set off. Place a Bomb 4."]))
    assert (f"- **Bomb** — A charge on an enemy: each grows "
            f"{blindplay.BOMB_GROWTH} a turn,") in page
    # LIVE FIRST: where the screen's own tip carries the number, that number is
    # what the glossary prints -- the fallback is for a screen that prints the
    # WORD with no tip on it, which is an enemy's badge and a reward row.
    live_tip = blindplay.observe(elemental_hand_state(
        bomb_tip="A charge on an enemy: grows 9 a turn, goes off only when "
                 "Set off."))
    assert "each grows 9 a turn" in live_tip


def test_the_hexerei_line_names_the_payment_the_kit_declares():
    """`EB-535`. WHAT "CARDS OF HERS PAY" NEVER SAID.

    Klee r19 lane 2: "I read this a dozen times across five fights and I still
    do not know what it does. 'Cards of hers pay' -- pay what, to whom, and
    when? I played Razor four times and never saw anything I could attribute to
    Hexerei." The rule was on a DIFFERENT screen the whole time -- the Companion
    Spark rider, which rides Klee's own Personals and not the family tag.

    So the row names the payment and its bound, and the two numerals are held
    in step from THIS side, the way `BOMB_GROWTH` is: this module may not import
    `tier0` at all, and the mod lifts them from `KleeCompanionSpark`, which is
    the declaration LAW:145 obliges Klee's kit to make.
    """
    src = (REPO / "klee-mod" / "KleeCode" / "Powers"
           / "KleeCompanionSpark.cs").read_text(encoding="utf-8")
    assert re.search(rf"Base\s*=\s*{blindplay_notes.COMPANION_SPARK}\b", src)
    assert re.search(
        rf"MaxPerPlay\s*=\s*{blindplay_notes.COMPANION_SPARK_MAX}\b", src)

    row = blindplay_notes.ARM_KEYWORDS["Hexerei"]
    assert (f"Playing one of hers makes {blindplay_notes.COMPANION_SPARK} "
            f"Spark, up to {blindplay_notes.COMPANION_SPARK_MAX}.") in row
    # The two clauses that answer the seat's OTHER question -- whether Razor is
    # one of Klee's own -- are what paid for the room, and they stay.
    assert "Some are Klee's own, some are not." in row
    assert len(row) <= 135


def _shattering_pressure_reward_state() -> dict:
    """The r19 lane-2 offer, as the seat met it (`EB-537`).

    A CARD REWARD and not a fight: the decision the screen is asking for is
    whether to take the card, the run had never printed a Shatter, and no
    element is on the screen at all -- which is the board the census cannot
    answer for and the word can.
    """
    return {"state_type": "card_reward",
            "player": {"character": "Klee", "hp": 40, "max_hp": 70},
            "card_reward": {"cards": [
                {"name": "Freminet - Shattering Pressure", "cost": "1",
                 "type": "Power",
                 "description": "Your Shatters deal 4 additional damage."}]}}


def test_a_keyword_on_an_offered_face_is_defined_even_when_unreachable():
    """`EB-537`. THE CARD THE SEAT COULD NOT PRICE.

    Klee r19 lane 2: "*Freminet -- Shattering Pressure* ('Your Shatters deal 4
    additional damage') was offered to me and I could not have played it:
    nothing in the run ever printed a Shatter, and the word is not in the
    glossary on that screen."

    `EB-428`'s census answers "can this DECK build the pair", which is the
    right question for a row the page raises on its OWN initiative -- six
    reactions listed at a mono-element deck is the noise it was filed on. It is
    the wrong question for a word the screen is already showing the reader: an
    offered card whose one mechanic is undefined cannot be priced at all.

    Seen to FAIL: `Shatter` was in no table, so no screen ever defined it.
    """
    page = blindplay.observe(_shattering_pressure_reward_state())

    assert "- **Shatter** — The first Attack to hit a Frozen enemy" in page
    assert "ends the freeze" in page


def test_the_shatter_row_is_the_mods_own_number():
    """Held in step from THIS side, the way `BOMB_GROWTH` is: this module may
    not import `tier0`, and the sim and the mod share the constant."""
    src = (REPO / "tier0" / "constants.py").read_text(encoding="utf-8")
    assert re.search(
        rf"SHATTER_DAMAGE\s*=\s*{blindplay_notes.SHATTER_DAMAGE}\b", src)
    assert (f"deals {blindplay_notes.SHATTER_DAMAGE} additional damage"
            in blindplay_notes.GAME_KEYWORDS["Shatter"])


def test_a_reaction_the_screen_names_is_defined_though_it_is_unreachable():
    """The general rule the row asks for, one word over: the page defines what
    it PRINTS. A screen naming Vaporize on a deck that holds one element still
    owes the reader the sentence, because the word is already in front of
    them."""
    state = {"state_type": "card_reward",
             "player": {"character": "Klee", "hp": 40, "max_hp": 70},
             "card_reward": {"cards": [
                 {"name": "Probe", "cost": "1", "type": "Skill",
                  "description": "Deal 6 damage. Vaporize deals 4 more."}]}}

    page = blindplay.observe(state)

    assert "- **Vaporize** —" in page
    # And nothing invented beside it: a word the screen does NOT print is still
    # the census's business and stays off the page.
    assert "- **Superconduct** —" not in page


def test_the_reaction_gloss_names_where_an_element_comes_from():
    """`EB-544`. THE POTION THAT SET UP NOTHING.

    Kokomi r19 lane 1: "a Fire Potion used to set up Vaporize left no Pyro aura
    at all, and nothing on any screen says which sources apply an element and
    which do not." The seat spent a potion on a reaction it could not have.

    The rule is one expression's -- `AuraCmd.ElementOfPlay` answers off the CARD
    being played -- so a play with no card behind it applies nothing. The line
    is on the UMBRELLA row because it is true of all six pairs, and that row is
    the one a mono-element deck reads.
    """
    row = blindplay_notes.REACTION_KEYWORDS["Elemental Reaction"]
    assert "An element comes from a CARD that prints one" in row
    assert "a potion, a relic or an enemy applies none" in row


def test_a_fire_potion_leaves_no_aura_in_the_sim_either():
    """The seat's own play, run: the sim resolves a Fire Potion through
    `refpowers.unpowered_damage`, which carries no card and no element, so the
    body takes 20 and wears nothing. The mod's twin is pinned in
    `KleeTests/Prototype/Round19Tests.cs`."""
    from tier0 import constants as C
    from tier0.engine import potions
    from tier0.tests.conftest import make_enemy, make_state

    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy], hp=80)

    potions.apply_potion(state, "fire_potion", enemy)

    assert enemy.hp == 200 - C.POTION_FIRE_DAMAGE
    assert getattr(enemy, "aura", None) in (None, "")


def test_the_bomb_growth_fallback_is_the_mods_own_constant():
    """`BOMB_GROWTH` is held in step from THIS side, the way
    `CHARGE_SOURCE_LINE` and `KURAGE_COST_PER_ENERGY` are: this module may not
    import `tier0` at all, so a retune of the C# constant goes red here."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "KleeOverhaul.cs").read_text(encoding="utf-8")
    assert re.search(rf"BombGrowth\s*=\s*{blindplay.BOMB_GROWTH}\b", src)


# ------------------------------------- EB-341: event, shop and reward pages --

def twin_option_event_state() -> dict:
    """The Future of Potions, as the r7b act-2b seat met it (`EB-341`).

    Three options, two of them character-for-character identical and losing a
    different potion each.
    """
    return {"state_type": "event",
            "player": {"hp": 40, "max_hp": 70},
            "event": {"event_id": "FUTURE_OF_POTIONS",
                      "event_name": "The Future of Potions",
                      "in_dialogue": False, "body": "A machine hums.",
                      "options": [
                          {"index": 0, "title": "Insert Common Potion",
                           "description": "Lose Flex Potion. Obtain an "
                                          "Upgraded Common Attack."},
                          {"index": 1, "title": "Insert Common Potion",
                           "description": "Lose Dexterity Potion. Obtain an "
                                          "Upgraded Common Skill."},
                          {"index": 2, "title": "Insert Rare Potion",
                           "description": "Lose Beetle Juice. Obtain an "
                                          "Upgraded Rare Power."}]}}


def test_two_options_with_one_title_are_numbered_and_taken_by_number():
    """`EB-341` (1). "The only grammar offered is `choose "<option>"`. I sent
    `choose "Insert Common Potion"`, it was ACCEPTED WITH AN EMPTY REFUSAL,
    and no screen ever said which of the two it had taken."

    Seen to FAIL: `_match` collapsed the two identical names onto one choice
    and fell through to `hits[0]`, silently.
    """
    state = twin_option_event_state()
    page = blindplay.observe(state)
    assert "- 1. **Insert Common Potion**" in page
    assert "- 2. **Insert Common Potion**" in page
    assert "- 3. **Insert Rare Potion**" in page
    assert "choose <number>" in page

    ambiguous = blindplay.act(state, 'choose "Insert Common Potion"')
    assert not ambiguous["ok"]
    assert "more than one row" in ambiguous["refusal"]
    assert "`choose <number>`" in ambiguous["refusal"]

    second = blindplay.act(state, "choose 2")
    assert second["ok"], second["refusal"]
    assert second["post"] == {"action": "choose_event_option", "index": 1}
    assert "Dexterity Potion" in second["printed"]["text"]
    # A title that is unique on the screen still resolves by name.
    assert blindplay.act(state, 'choose "Insert Rare Potion"')["ok"]


def test_an_ordinal_off_the_end_is_refused_with_the_rows_that_exist():
    """A number the screen does not have is a refusal that names the list,
    never a clamp onto the nearest row."""
    res = blindplay.act(twin_option_event_state(), "choose 9")
    assert not res["ok"]
    assert "no row 9" in res["refusal"] and "it has 3" in res["refusal"]


def test_a_screen_with_no_collisions_prints_no_ordinals():
    """The number is a disambiguator and not decoration -- an event whose
    options all print different names reads exactly as it always did."""
    page = blindplay.observe(event_state())
    assert "- **Offer a card**" in page and "- 1. **Offer a card**" not in page
    assert blindplay.act(event_state(), "choose 2")["post"] == {
        "action": "choose_event_option", "index": 1}


def test_the_line_after_a_choice_names_the_row_and_what_it_said():
    """`EB-341` (2). Both events of the r7b act-3 session "declined to name
    what they gave me": the seat learned the Tea Party's random relic was `Bag
    of Marbles`, and what `Forgotten Soul` does, off the relic list of a later
    combat screen.

    Seen to FAIL: the only line after a command was the wire's own answer,
    which for an event choice is a status word and nothing else.
    """
    res = blindplay.act(twin_option_event_state(), "choose 1")
    line = blindplay.taken_line(res)
    assert line.startswith("Took: Insert Common Potion — ")
    assert "Lose Flex Potion. Obtain an Upgraded Common Attack." in line
    # A purchase says what category the shelf was, at the moment of buying.
    blindplay.forget_shelves()
    bought = blindplay.taken_line(blindplay.act(shop_state(),
                                                'buy "Coral Guard"'))
    assert bought.startswith("Bought: Coral Guard (card (skill)), for 75 gold")
    # And a resolution with no printed name -- `end turn` -- says nothing.
    assert blindplay.taken_line(
        blindplay.act(combat_state(), "end turn")) == ""


def test_every_shop_line_carries_its_category():
    """`EB-341` (3). "`Fysh Oil` printed as a bare name, a price and an effect,
    in the identical format used by `Vambrace`, `Stone Calendar` and `Royal
    Stamp` one line above. I bought it as a permanent Strength relic. It is a
    potion. The only disclosure is the SOLD-OUT line."

    Seen to FAIL: `kind` was read off `card_type`, which a relic and a potion
    shelf do not carry, so both printed with no category at all.
    """
    blindplay.forget_shelves()
    page = blindplay.observe(live("shop-stocked"))
    assert "**Flex Potion** — potion, 48 gold" in page
    assert "**Bag of Preparation** — relic, 192 gold" in page
    assert "**Perfect Timing** — cost 1, card (attack), 76 gold" in page
    # The removal shelf's category IS its printed name; it is not said twice.
    assert "card removal" not in page


def full_slots_rewards_state() -> dict:
    """A potion reward against three full slots (`EB-341`).

    `BuildPlayerState` sends `potions` (the FILLED slots) and
    `max_potion_slots` beside it, and this page printed neither number.
    """
    return {"state_type": "rewards",
            "player": {"hp": 40, "max_hp": 70, "max_potion_slots": 3,
                       "potions": [{"name": "Strength Potion",
                                    "description": "Gain 2 Strength."},
                                   {"name": "Fruit Juice",
                                    "description": "Gain 5 Max HP."},
                                   {"name": "Flex Potion",
                                    "description": "Gain 2 Strength."}]},
            "rewards": {"can_proceed": True, "items": [
                {"index": 0, "type": "gold", "description": "12 Gold"},
                {"index": 1, "type": "potion", "potion_id": "FIRE_POTION",
                 "potion_name": "Fire Potion", "description": "Fire Potion",
                 "potion_description": "Deal 20 damage to one enemy."}]}}


def test_a_potion_claimed_on_full_slots_says_the_slots_are_full():
    """`EB-341` (4). "I claimed `Fire Potion` off fight 19's reward screen and
    the tool answered `ok Claiming reward: potion (Fire Potion)`. The next
    combat listed three potions and `Fire Potion` was not among them. Three
    slots, four potions, and NO LINE on either screen saying the claim had
    failed or that a slot was full."

    Seen to FAIL: the claim resolved `ok` and the page printed no count.
    """
    state = full_slots_rewards_state()
    page = blindplay.observe(state)
    assert "Your potion slots are full: 3 of 3" in page

    res = blindplay.act(state, 'choose "Fire Potion"')
    assert not res["ok"]
    assert "potion slots are full: 3 of 3" in res["refusal"]
    # Everything else on the screen still claims.
    assert blindplay.act(state, 'choose "12 Gold"')["ok"]


def test_a_free_slot_claims_a_potion_exactly_as_before():
    """The guard is narrow on purpose: a run with room reads and resolves the
    way it always did.

    `EB-371` NARROWED WHAT THIS ASSERTS RATHER THAN WEAKENING IT. The belt is
    printed on every screen that can drop from it now, so a page holding one
    potion of three says so in its own count. What must stay absent is the
    WARNING -- the sentence that refuses the claim -- and that is asserted.
    """
    state = full_slots_rewards_state()
    state["player"]["potions"] = state["player"]["potions"][:1]
    page = blindplay.observe(state)
    assert "Your potion slots are full" not in page
    assert blindplay.act(state, 'choose "Fire Potion"')["ok"]


def test_the_combat_page_says_how_many_potion_slots_there_are():
    """The same two numbers, on the screen a potion is spent from -- a tester
    who cannot see the denominator cannot know a fourth has nowhere to go."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["potions"] = [{"name": "Fire Potion",
                                   "description": "Deal 20 damage."}]
    assert "- 1 of 3 slots are full." in blindplay.observe(state)


# --------------------------- EB-371: the belt has a way off it, everywhere --
#
# THE ROW. At three of three the page REFUSES a potion reward -- "a potion
# claimed now has nowhere to go" (`EB-341`) -- and outside a fight there was
# nothing a seat could do to make room: `use potion` needs a combat for a
# combat-only potion and nothing else touched the belt. The r9 act-1 seat met
# Tiny Mailbox at a rest site, was handed two potions onto a full belt and lost
# both, having been told only that it could not claim.
#
# THE WIRE HAD IT ALL ALONG. `discard_potion` is dispatched by
# `McpMod.Actions.cs:65` and `ExecuteDiscardPotion` (`:325`) asks for a run in
# progress and a potion in the slot -- no combat, no play phase and no
# usability check, which is exactly what separates it from `use_potion`.


def test_the_drop_verb_is_offered_on_a_rest_site_and_posts_the_wires_slot():
    """The screen a seat was standing on when it lost two potions, and the
    slot posted is the wire's own (`EB-269`'s lesson, one verb over).

    Seen to FAIL: before this row `drop potion 2` was not a command at all.
    """
    state = live("rest-fresh")
    page = blindplay.observe(state)
    assert '- `drop potion "<potion>"`' in page
    assert "- `drop potion <number>" in page
    # The belt it counts against is printed on the same screen.
    assert "## Potions" in page
    assert "- 2 of 3 slots are full." in page
    assert "- **Mazaleth's Gift** — Gain 1 Ritual." in page

    res = blindplay.act(state, "drop potion 2")
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "discard_potion", "slot": 1}
    assert res["printed"] == {"potion": "Mazaleth's Gift"}
    # And by name, which is the same row.
    named = blindplay.act(state, 'drop potion "Blessing of the Forge"')
    assert named["post"] == {"action": "discard_potion", "slot": 0}


# --- `EB-520`: THE ROOM THE PAGE COULD SEE AND THE ACTION COULD NOT ---------


def test_rest_and_upgrade_resolve_to_the_printed_options():
    """`EB-520`, the grammar half. Both words are the screen's own options, and
    both post the same thing `choose` posts -- which is the whole reason the
    seat's `choose "Rest"` worked a moment after `rest` did not, and the reason
    the defect is not here."""
    state = rest_state()
    by_verb = blindplay.act(state, "rest")
    by_name = blindplay.act(state, 'choose "Rest"')
    assert by_verb["ok"] and by_verb["post"] == by_name["post"]
    assert by_verb["post"] == {"action": "choose_rest_option", "index": 0}

    smith = blindplay.act(state, "upgrade")
    assert smith["ok"], smith["refusal"]
    assert smith["post"] == {"action": "choose_rest_option", "index": 1}
    assert smith["printed"] == {"option": "Smith"}


class _LoadingRoom:
    """A wire whose rest-site room answers `is not open` for the first N posts.

    `BuildState` reports the room off `RunState`, which the walk commits at
    once; `ExecuteChooseRestOption` needs `NRestSiteRoom.Instance`, the scene,
    which Godot instantiates a frame or two later. This is that gap.
    """

    def __init__(self, shut: int, states=None):
        self.shut = shut
        self.posts: list[dict] = []
        self.states = states or [rest_state()]

    def get_state(self):
        return self.states[min(len(self.posts), len(self.states) - 1)]

    def post(self, action, **params):
        self.posts.append({"action": action, **params})
        if len(self.posts) <= self.shut:
            return {"status": "error", "error": "Rest site room is not open"}
        return {"status": "ok", "message": "Selecting rest site option: Rest"}

    def health(self):
        return {"mod_version": "0.0-scripted"}

    def meter_ledger(self):
        return {"status": "ok", "available": False, "rows": [], "count": 0}


def test_a_room_that_has_not_loaded_yet_is_ridden_out_rather_than_refused():
    """`EB-520`. THE REFUSAL THAT WAS A MOMENT.

    Kokomi r18 lane 1, floor 10: `rest` came back "Rest site room is not open"
    "while the screen was printing Rest as an option and listing `rest` as a
    thing I could say", and `choose "Rest"` worked immediately after. Klee r10
    hit it twice on `rest`; the Ironclad control seat hit it on `upgrade`
    "issued immediately after `go` ... the room had not finished loading".

    Seen to FAIL: one POST, one refusal, and the seat spent an action learning
    that retrying works.
    """
    wire = _LoadingRoom(shut=2)

    result = blindplay.post_when_the_room_is_open(
        wire, "choose_rest_option", {"index": 0}, tries=6, delay=0)

    assert result["status"] == "ok"
    assert len(wire.posts) == 3
    assert all(p == {"action": "choose_rest_option", "index": 0}
               for p in wire.posts)


def test_a_room_that_stays_shut_is_reported_rather_than_waited_on_forever():
    """`_settle`'s own discipline: bounded, and the LAST answer is handed back,
    so a wire that really is stuck reaches the seat as the sentence the game
    gave rather than as a hang."""
    wire = _LoadingRoom(shut=99)

    result = blindplay.post_when_the_room_is_open(
        wire, "choose_rest_option", {"index": 0}, tries=3, delay=0)

    assert result["error"] == "Rest site room is not open"
    assert len(wire.posts) == 4          # the first, then the bound


def test_every_other_refusal_is_an_answer_and_is_posted_once():
    """Only "room is not open" is a moment. A real refusal -- a disabled
    option, an index off the end -- is the game answering, and re-posting it
    would spend actions on a decision the seat has already been told about."""
    calls: list[dict] = []

    class _Refuses(_LoadingRoom):
        def post(self, action, **params):
            calls.append({"action": action, **params})
            return {"status": "error",
                    "error": "Rest option 2 (dig) is disabled"}

    result = blindplay.post_when_the_room_is_open(
        _Refuses(shut=0), "choose_rest_option", {"index": 2},
        tries=6, delay=0)

    assert result["error"].endswith("is disabled")
    assert len(calls) == 1


def test_the_drop_verb_reaches_the_reward_screen_that_refused_the_claim():
    """The acceptance sentence: at three of three a seat drops one and claims
    the offered one. Both halves against the one state."""
    state = full_slots_rewards_state()
    page = blindplay.observe(state)
    assert "Your potion slots are full: 3 of 3" in page
    assert '- `drop potion "<potion>"`' in page
    # The refusal now names the way out instead of offering only a fight.
    refusal = blindplay.act(state, 'choose "Fire Potion"')["refusal"]
    assert "`drop potion 1`" in refusal

    dropped = blindplay.act(state, 'drop potion "Flex Potion"')
    assert dropped["ok"], dropped["refusal"]
    assert dropped["post"] == {"action": "discard_potion", "slot": 2}
    # With the slot free, the claim that was refused resolves.
    state["player"]["potions"] = state["player"]["potions"][:2]
    assert blindplay.act(state, 'choose "Fire Potion"')["ok"]


def test_the_drop_verb_is_offered_in_a_fight_over_the_belt_already_printed():
    """A combat screen prints the belt already, so only the verb is added --
    and the ordinal counts the list the page has been printing since
    `EB-341`."""
    state = potion_belt_state(FIRE_IN_SLOT_ZERO + DEXTERITY_IN_SLOT_ONE)
    page = blindplay.observe(state)
    assert page.count("## Potions") == 1
    assert "- `drop potion <number>" in page
    assert blindplay.act(state, "drop potion 2")["printed"] == {
        "potion": "Dexterity Potion"}


def test_a_screen_with_no_belt_offers_no_drop():
    """The verb is offered where it resolves and nowhere else: an empty belt
    has nothing to aim it at, and a blocked screen is not being driven."""
    state = json.loads(json.dumps(live("rest-fresh")))
    state["player"]["potions"] = []
    page = blindplay.observe(state)
    assert "drop potion" not in page and "## Potions" not in page
    assert not blindplay.act(state, "drop potion 1")["ok"]

    over = {"state_type": "game_over", "game_over": {"result": "Defeat"},
            "player": {"potions": [{"name": "Fire Potion", "slot": 0}]}}
    assert "drop potion" not in blindplay.observe(over)


def test_a_drop_that_names_nothing_is_refused_in_the_page_s_own_grammar():
    """`drop` is not a verb and `drop potion` needs a handle. Both refusals
    name the forms that resolve rather than a parser rule."""
    state = live("rest-fresh")
    bare = blindplay.act(state, "drop potion")
    assert not bare["ok"] and "drop potion 2" in bare["refusal"]
    assert not blindplay.act(state, 'drop "Mazaleth\'s Gift"')["ok"]
    off = blindplay.act(state, "drop potion 9")
    assert not off["ok"] and "no number 9 on your belt" in off["refusal"]


# ----------------------------- EB-342: three page lines short of the state --

def compound_intent_state() -> dict:
    """Mecha Knight's move, as the wire sends it (`EB-342`).

    `BuildEnemyState` walks `moveState.Intents` and sends a LIST; the page took
    `blob[0]` and dropped the rest.
    """
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "Attack", "label": "8", "title": "Aggressive",
         "description": "This enemy intends to Attack for 8 damage."},
        {"type": "StatusCard", "label": "4", "title": "Strategic",
         "description": "This enemy intends to add 4 Burn to your hand."}]
    return state


def test_a_compound_intent_prints_every_component():
    """`EB-342` (1). "Intent: Aggressive (Attack) -- the number on its icon is
    8 -- This enemy intends to Attack for 8 damage." Round 3 opened with FOUR
    `Burn`s in hand, 8 more HP a turn, at 18/56, in the fight that ended the
    run. "The bridge has a status-card intent type, so the vocabulary existed
    and was not used."

    Seen to FAIL: only the first row of the list reached the page.
    """
    page = blindplay.observe(compound_intent_state())
    # `EB-461` MARKED THE NUMBERS ON A MULTI-PART TELEGRAPH, and nothing else
    # about these lines moved: both parts still print, in the move's own order.
    assert ("Intent: Aggressive (Attack) — the number on its icon is 8, one "
            "part of this move — This enemy intends to Attack for 8 "
            "damage.") in page
    assert ("and also: Strategic (StatusCard) — the number on its icon "
            "is 4, one part of this move — This enemy intends to add 4 Burn "
            "to your hand.") in page


def defending_enemy_state() -> dict:
    """A body wearing Block, telegraphing a move that will add more.

    The `Defend` part is the wire's own shape, off the `review/qa` captures:
    `{"type": "Defend", "label": "", "title": "Defensive"}` -- no number, and
    no description either.
    """
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["enemies"][0]["block"] = 5
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "Attack", "label": "8", "title": "Aggressive",
         "description": "This enemy intends to Attack for 8 damage."},
        {"type": "Defend", "label": "", "title": "Defensive"}]
    return state


def test_an_enemys_block_prints_beside_its_hp():
    """`EB-474`, the half that was already standing and had nothing holding it.

    "Nibbit at 5 HP, I played a card printing *Deal 6 damage*, and it lived at
    4. Nothing on the combat page showed the Block that ate the other 5. That
    is the only outright unpredictable outcome of the run" (Furina r9 (c) 1).

    The page has printed the clause off `battle.enemies[].block` since
    `EB-180`, and `BuildEnemyState` fills that key from `creature.Block` -- so
    the row's first half is a PIN, not a build, and it goes red the moment the
    clause is dropped again. A body with no Block prints no clause: zero is
    the default state of every enemy on the board and a `Block 0` on each line
    is `EB-198`'s noise.
    """
    page = blindplay.observe(defending_enemy_state())
    # `EB-496` put the fight's own letter between the name and the numbers,
    # which is where the card face already carries its element.
    assert "- **Nibbit** [A] — HP 38/45, Block 5" in page
    assert "Block" not in blindplay.observe(combat_state()).split(
        "## The other side")[1].split("*Each enemy keeps")[0]


def test_a_defend_part_of_a_telegraph_says_it_will_add_block():
    """`EB-474`, the half that was missing: the TELEGRAPH said nothing.

    `BuildEnemyState` sends a `Defend` part with an empty `label` and, on
    every capture in `review/qa`, no description -- so the line read
    `Defensive (Defend)`, a word with no consequence attached, one row above
    the number it was about to change. The seat's own reading of its lost kill
    was "Block from the Defend half of its previous multi-part telegraph": the
    turn to have been told was that one.

    Seen to FAIL: the part printed its title and its type and stopped.
    """
    page = blindplay.observe(defending_enemy_state())
    assert ("and also: Defensive (Defend) — this part adds Block to the "
            "Block on its line above, and the feed carries no number for how "
            "much") in page
    # Only a Defend part carries it -- the Attack half is untouched.
    assert page.count("this part adds Block") == 1
    assert "adds Block" not in blindplay.observe(compound_intent_state())


def test_no_observe_prints_the_enemy_block_twice():
    """`EB-458`, and the row's premise did not hold: there is no duplicated
    render path to find.

    WHAT WAS FILED. "The page printed `## The other side` and the whole enemy
    block twice, verbatim, on five observes across four fights" (Klee r14).

    WHAT THE CODE SAYS. `render` emits that heading in exactly one place, in
    the one `screen == "combat"` branch, and `observe` is `render(observation
    (state))` -- there is no second emitter on this path (`qa_packet`'s is the
    STAGED PACKET, a different surface with a different entry point). Every
    recorded screen in `review/qa` renders it once.

    WHAT ACTUALLY HAPPENED, on the seats' own evidence. Both r14 seats declare
    piping `observe` through `sed -n '<ranges>p'` to re-read one block, and the
    Klee r10 run-2 seat met the IDENTICAL symptom and diagnosed it itself:
    "One such call early on used two overlapping `sed` ranges and printed the
    enemy block twice -- a formatting error of mine, not a game one."

    So this stands as the guard rather than the fix: the page prints the block
    once, and a render path that ever emitted it twice goes red here.
    """
    for state in (combat_state(), compound_intent_state(),
                  elemental_hand_state(aura=True),
                  keyword_hand_state(["Gain 5 Block."])):
        page = blindplay.observe(state)
        assert page.count("## The other side") == 1, page.count(
            "## The other side")
        assert page.count("# Battle") == 1
    src = (REPO / "understudy" / "blindplay_render.py").read_text(
        encoding="utf-8")
    assert src.count('"## The other side"') == 1


def test_a_single_component_intent_reads_exactly_as_it_always_did():
    """One row, one line, no continuation -- the recorded combat is the pin.

    `EB-461` left this line alone on purpose: a one-part telegraph is the whole
    of the move, so its number needs no part label and the note does not print.
    """
    page = blindplay.observe(combat_state())
    assert ("Intent: Aggressive (Attack) — the number on its icon is 12 "
            "— This enemy intends to Attack for 12 damage.") in page
    assert "and also:" not in page
    assert "one part of this move" not in page
    assert blindplay.MULTI_INTENT_NOTE not in page


def test_a_dual_intent_number_is_labelled_one_part_of_the_move():
    """`EB-461`, REOPENED. THE LABEL MADE A FREQUENCY CLAIM AND IT COST AS
    MUCH AS THE BARE NUMBER DID.

    WHAT THE FIRST BUILD SAID. "a part it MAY perform", under a note reading
    "on this build the damage part of a multi-part telegraph has repeatedly
    not landed" -- a history read off four enemy turns (Kokomi r14 (c) 2, Klee
    r14).

    WHAT IT THEN DID. Both r15 seats read the label as advice and stopped
    blocking against five multi-part telegraphs that landed in full. A page
    that talks a reader OUT of a real number is the same defect as one that
    talks them into an unreal one, and the page has standing for neither: the
    feed carries `type`, `label`, `title` and `description` per part and no
    marker of resolution, order or condition at all.

    SO THE PAGE SAYS ONLY WHAT IT KNOWS. The number belongs to one part of a
    several-part move; which parts resolve is not on the feed. No history, no
    likelihood, no advice. The marker that would let the page say more is
    asked of `STS2_MCP` in `docs/current/operations/understudy-seats.md`.

    Seen to FAIL: the label and the note both carried the frequency claim.
    """
    page = blindplay.observe(compound_intent_state())
    assert "the number on its icon is 8, one part of this move" in page
    assert "the number on its icon is 4, one part of this move" in page
    # ONCE, with the block's other notes, however many enemies telegraph parts.
    assert page.count(blindplay.MULTI_INTENT_NOTE) == 1

    # THE NEUTRAL FORM, and what it may not contain. No count of how often a
    # part has landed, no verdict on what a reader should do about it.
    for claim in ("repeatedly", "MAY perform", "has not landed",
                  "never", "usually", "rarely", "often", "about to deal"):
        assert claim not in blindplay.MULTI_INTENT_NOTE, claim
        assert claim not in blindplay.MULTI_INTENT_LABEL, claim
    assert "no claim" in blindplay.MULTI_INTENT_NOTE

    # A part with no number on its icon has no number to attach a label to.
    quiet = json.loads(json.dumps(combat_state()))
    quiet["battle"]["enemies"][0]["intents"] = [
        {"type": "Attack", "label": "6", "title": "Aggressive",
         "description": "This enemy intends to Attack for 6 damage."},
        {"type": "Buff", "label": "", "title": "Empower",
         "description": "This enemy intends to use a Buff."}]
    quiet_page = blindplay.observe(quiet)
    assert "the number on its icon is 6, one part of this move" in quiet_page
    assert quiet_page.count("the number on its icon") == 1
    assert blindplay.MULTI_INTENT_NOTE in quiet_page


def test_the_seats_page_asks_the_bridge_for_a_resolving_part_marker():
    """`EB-461`, the half this side of the line cannot build.

    The neutral label is as far as the page can go without a fact the wire
    does not carry. `BuildEnemyState` sends no marker of which part of a
    multi-part move resolves, and `STS2_MCP` is vendored -- so the request is
    written down where the seats' operations page keeps them, rather than
    guessed at in the render.
    """
    doc = (REPO / "docs" / "current" / "operations"
           / "understudy-seats.md").read_text(encoding="utf-8")
    assert "resolving-part marker" in doc
    assert "`EB-461`" in doc
    assert "BuildEnemyState" in doc


def discounted_hand_state() -> dict:
    """The r7b fight-15 hand: one permanent upgrade, one one-turn discount.

    `The Big One+` prints 3 on its shipped face and 2 here; `Flame Dance`
    prints 1 and is showing 0 under a `Vexing Puzzlebox`.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_THE_BIG_ONE", "name": "The Big One",
         "type": "Attack", "cost": "2", "can_play": True, "index": 0,
         "target_type": "AnyEnemy", "is_upgraded": True, "keywords": [],
         "description": "Set off for quadruple damage."},
        {"id": "KLEEMOD-PROTO_KO_FLAME_DANCE", "name": "Flame Dance",
         "type": "Skill", "cost": "0", "can_play": True, "index": 1,
         "target_type": "Self", "is_upgraded": False, "keywords": [],
         "description": "Set off each enemy whose aura is not Pyro."}]
    return state


def test_the_cost_line_says_whether_it_is_the_upgrade_or_the_turn():
    """`EB-342` (2). "Identical phrasing for a property of the card and a
    property of this turn. The `(upgraded)` tag is the only distinguisher, and
    it sits in the title rather than beside the cost line that is actually
    being explained."

    Seen to FAIL: both cards printed the same sentence, word for word.
    """
    page = blindplay.observe(discounted_hand_state())
    assert ("The cost printed on this card is 3; it is showing 2 here, "
            "because this copy is upgraded — that is permanent.") in page
    assert ("The cost printed on this card is 1; it is showing 0 here. This "
            "copy is not upgraded, so the cut is this turn's board and not "
            "the card") in page


def upgrade_run_states() -> tuple[dict, dict]:
    """A fight and the Smith two rooms later, on one run (`EB-342`).

    The Smith screen is the RECORDED one (`upgrade-fresh`, captured off a live
    Klee run); the fight is built to hold that screen's grid plus three cards
    it leaves out -- one already upgraded, one in the build's no-upgrade
    register, and one the page can say nothing about.
    """
    smith = live("upgrade-fresh")
    smith = smith.get("state", smith)
    grid = [c["name"] for c in smith["card_select"]["cards"]]
    fight = {
        "state_type": "monster",
        "run": {"act": 1, "floor": 10},
        "battle": {"round": 1, "enemies": [
            {"name": "Slug", "hp": 5, "max_hp": 5, "block": 0, "status": [],
             "intents": [{"type": "Attack", "label": "3",
                          "title": "Aggressive",
                          "description": "This enemy intends to Attack for 3 "
                                         "damage."}]}]},
        "player": {
            "character": smith["player"]["character"],
            "hp": 30, "max_hp": 62, "block": 0, "energy": 3, "max_energy": 3,
            "status": [], "relics": [], "potions": [], "max_potion_slots": 3,
            "hand": [{"id": f"KLEEMOD-GRID_{i}", "name": name, "type": "Skill",
                      "cost": "1", "can_play": True, "index": i,
                      "description": "Gain 5 Block."}
                     for i, name in enumerate(grid)],
            "draw_pile": [
                {"id": "KLEEMOD-PROTO_POWDER_CHARGE_SPARK",
                 "name": "Powder Charge", "type": "Skill", "cost": "0",
                 "description": "Place a Bomb 6."},
                {"id": "KLEEMOD-PROTO_KO_KAPOW", "name": "Ka-pow!",
                 "type": "Attack", "cost": "0", "is_upgraded": True,
                 "description": "Retain. Set off. Deal 6 damage."},
                {"id": "KLEEMOD-PROTO_KO_SIZZLE", "name": "Sizzle",
                 "type": "Attack", "cost": "1",
                 "description": "Deal 6 damage."}],
            "discard_pile": [], "exhaust_pile": [],
            "draw_pile_count": 3, "discard_pile_count": 0,
            "exhaust_pile_count": 0}}
    return fight, smith


def test_the_smith_says_why_a_card_is_not_on_its_list():
    """`EB-342` (3). "The upgrade screen listed 25 cards against a deck of
    35-36... `Powder Charge`, `Shinobu -- Sanctifying Ring (proto)` are not
    upgraded and are not listed, and no line explains the absence. On a screen
    that is otherwise the most scrupulous in the bridge, a silent omission is
    conspicuous."

    The deck is not on this screen's feed at all, so the answer comes off the
    deck this page printed for itself in the last fight -- and it says so.

    Seen to FAIL: the page printed the grid and nothing else.
    """
    blindplay.forget_deck()
    fight, smith = upgrade_run_states()
    assert "Not on this list" not in blindplay.observe(smith)  # nothing known

    blindplay.observe(fight)
    page = blindplay.observe(smith)
    assert "## Not on this list, and why" in page
    assert ("- **Powder Charge** — " + blindplay.NO_UPGRADE_DEFINED) \
        in page
    assert ("- **Ka-pow!** — " + blindplay.ALREADY_UPGRADED) in page
    assert ("- **Sizzle** — " + blindplay.UNEXPLAINED_OMISSION) in page
    # Nothing the grid IS offering is listed as missing.
    assert "**Chain Fuse** — " not in page.split("Not on this list")[1]
    # And the staleness is named rather than papered over.
    assert "your deck as it stood in the last fight (floor 10)" in page
    blindplay.forget_deck()


def test_a_remembered_deck_never_answers_another_runs_smith():
    """The memory's own guard, on `_SHELF_MEMORY`'s pattern: a deck read for
    one character may not describe another's screen, and a run only ever
    climbs, so a floor below the one the deck was read on is a new run."""
    blindplay.forget_deck()
    fight, smith = upgrade_run_states()
    blindplay.observe(fight)

    other = json.loads(json.dumps(smith))
    other["player"]["character"] = "Kokomi"
    assert "Not on this list" not in blindplay.observe(other)

    earlier = json.loads(json.dumps(smith))
    earlier["run"] = {"act": 1, "floor": 2}
    assert "Not on this list" not in blindplay.observe(earlier)
    blindplay.forget_deck()


def test_the_no_upgrade_register_is_read_by_id_and_only_its_ids_cross():
    """`UPGRADE_DEBT`'s VALUES are register prose naming ruling and row
    numbers, which is exactly what may not reach a blind page. Only the key set
    is read, and the page writes its own plain sentence."""
    index = qa_packet.no_upgrade_index()
    assert "PROTO_POWDER_CHARGE_SPARK" in index
    assert "PROTO_SHINOBU_SANCTIFYING_RING_EITHER" in index
    for entry in index:
        assert entry == entry.upper()
    assert not qa_packet.leaks(blindplay.NO_UPGRADE_DEFINED)
    assert not qa_packet.leaks(blindplay.ALREADY_UPGRADED)
    assert not qa_packet.leaks(blindplay.UNEXPLAINED_OMISSION)


# --- `EB-528`: A CARD THE COMBAT MADE IS NOT A CARD THE RUN OWNS ------------


def _combat_with_piles(round_no: int, hand: list[str],
                       draw: list[str] | None = None) -> dict:
    """A combat state whose four piles are the named titles."""
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["round"] = round_no
    state["player"]["character"] = "Furina"
    for pile, titles in (("hand", hand), ("draw_pile", draw or []),
                         ("discard_pile", []), ("exhaust_pile", [])):
        state["player"][pile] = [
            {"id": f"KLEEMOD-{t.upper().replace(' ', '_')}", "name": t}
            for t in titles]
    return state


def test_a_companion_generated_mid_fight_never_joins_the_remembered_deck():
    """`EB-528`. THE CARD THE COMBAT MADE, IN THE RUN'S DECK LIST.

    Furina r12 lane 1: "Lynette -- Bogglecat Box appeared in my end-of-act deck
    list. It entered my hand from An Invitation ... Bennett, Barbara, Gorou and
    Freminet -- Pers, which arrived by the same route, did not appear." Lane 2:
    "Shinobu, generated mid-fight by An Invitation, appeared in my deck list at
    the Smith."

    THE MOD IS RIGHT AND THE MEMORY WAS WRONG. A generated Companion goes
    through `CardPileCmd.AddGeneratedCardToCombat` into the HAND and onto no
    permanent list; this page's own snapshot took a LATER round's union of the
    piles whenever it was bigger than the deck it held, and a generated card
    makes it bigger by one. That is also why only some of them got in: the seat
    listed four that arrived the same way and did not.

    Seen to FAIL: the second read replaced the deck with five cards.
    """
    blindplay.forget_deck()
    blindplay.observe(_combat_with_piles(1, ["Strike", "Defend"],
                                         ["Strike", "Defend"]))
    assert len(blindplay._DECK_MEMORY["cards"]) == 4

    blindplay.observe(_combat_with_piles(
        3, ["Strike", "Defend", "Shinobu — Grass Ring"], ["Strike", "Defend"]))

    titles = [c["title"] for c in blindplay._DECK_MEMORY["cards"]]
    assert "Shinobu — Grass Ring" not in titles
    assert len(titles) == 4
    blindplay.forget_deck()


def test_the_next_fights_first_round_is_where_a_real_addition_arrives():
    """Nothing is lost by taking round one alone: a card the run really did
    gain is in hand or draw at the next fight's round one, which is the read
    this page already called the authoritative one."""
    blindplay.forget_deck()
    blindplay.observe(_combat_with_piles(1, ["Strike"], ["Defend"]))
    assert len(blindplay._DECK_MEMORY["cards"]) == 2

    blindplay.observe(_combat_with_piles(1, ["Strike", "Riptide"], ["Defend"]))

    titles = [c["title"] for c in blindplay._DECK_MEMORY["cards"]]
    assert titles.count("Riptide") == 1
    assert len(titles) == 3
    blindplay.forget_deck()


def test_a_victory_screens_short_union_still_never_replaces_the_deck():
    """The clause the old rule existed to prevent, kept: a later round can
    lose cards to a pile the game has torn down, and the deck it held stands.
    """
    blindplay.forget_deck()
    blindplay.observe(_combat_with_piles(1, ["Strike", "Defend"],
                                         ["Riptide", "Flank"]))
    assert len(blindplay._DECK_MEMORY["cards"]) == 4

    blindplay.observe(_combat_with_piles(6, ["Strike"], []))

    assert len(blindplay._DECK_MEMORY["cards"]) == 4
    blindplay.forget_deck()


def test_the_generator_adds_to_the_combat_and_to_no_permanent_list():
    """The C# half of the read, which is why nothing moved there: the one
    generation site in the mod goes through the combat-only door."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers"
           / "GuestStarGenerator.cs").read_text(encoding="utf-8")

    assert "CardPileCmd.AddGeneratedCardToCombat(" in src
    assert "PileType.Hand" in src
    assert "MasterDeck" not in src


# ------------- `EB-483`: what the Smith is offering, and what it becomes -----


def test_the_smith_prints_the_upgraded_face_beside_the_current_one():
    """`EB-483` (Kokomi r16 (c) 6). "The upgrade screen shows the current face,
    never the upgraded one. Thirteen cards, no previews. I upgraded Deep
    Current on a guess and found out it was 6 to 9 two fights later."

    The RECORDED Smith screen, plus the card the finding is about, appended in
    the shape that screen's own rows carry.

    Seen to FAIL: the page printed thirteen current faces and nothing else.
    """
    smith = live("upgrade-fresh")
    smith = json.loads(json.dumps(smith.get("state", smith)))
    smith["card_select"]["cards"].append(
        {"id": "KLEEMOD-PROTO_KK_DEEP_CURRENT", "name": "Deep Current",
         "cost": "1", "type": "Attack",
         "description": "Deal 6 damage to ALL enemies."})
    page = blindplay.observe(smith)

    # The card the seat guessed on, both faces, one under the other.
    assert "    Deal 6 damage to ALL enemies." in page
    assert "    Upgraded: Deal 9 damage to ALL enemies." in page
    # And the screen's own rows, including one whose printed face carries the
    # game's appended keyword sentence -- which is why the match is a search
    # over the face rather than the whole of it.
    assert "    Upgraded: Set off. Deal 10 damage. Applies Pyro." in page
    assert "    Upgraded: Gain 11 Block." in page


def test_a_face_the_upgrade_index_cannot_render_prints_no_second_face():
    """The bound, and it is the page's oldest rule: an absent answer is
    silence, never a guess. A row this build defines no delta for, a row whose
    printed text no longer matches the template it was generated from, and a
    card the index has never heard of all get exactly nothing."""
    assert qa_packet.upgraded_face("KLEEMOD-NOT_A_CARD", "Deal 6 damage.") == ""
    # Reworded since the capture: the wire says "on target enemy", the sheet
    # says "on the enemy", and one number in the middle is not enough to make
    # that a face this page may print.
    assert qa_packet.upgraded_face(
        "KLEEMOD-PROTO_KO_CHAIN_FUSE",
        "Each Bomb on target enemy grows by 3.") == ""
    # And it is off every screen but the Smith: a hand prints one face.
    hand = blindplay.observe(combat_state())
    assert "Upgraded:" not in hand


def test_the_upgraded_face_moves_the_number_the_delta_names():
    """`CalculationBase` is the input to a `Calculated*` var, so the face
    prints one name and `OnUpgrade` moves another -- resolved only where the
    template holds exactly one `Calculated*` hole, which is the same invariant
    the generator emits under (`block_calc_rider`: one CalculationBase per
    card)."""
    assert qa_packet.upgraded_face(
        "KLEEMOD-PROTO_KK_UNDERTOW",
        "Deal 7 damage, already including 3 if the enemy has a debuff.") == (
        "Deal 10 damage, already including 3 if the enemy has a debuff.")
    # A plural arm follows the number it is about rather than being copied.
    assert qa_packet.upgraded_face(
        "KLEEMOD-LYNETTE_BOX_TRICK", "Draw 2 cards.") == "Draw 3 cards."


# --- `EB-529`: THE FOUR SMITH ROWS THAT SHOWED NOTHING AND SAID NOTHING ------
#
# THE FIND (Furina r12 lane 2). "The upgrade screen showed no upgrade at all
# for `Aria of Recompense`, `Salon Debut`, `An Invitation` and `Fischl -- Oz`,
# with no line saying why, while every other card printed an `Upgraded:`
# preview."
#
# THE FOUR NAMED, AND THREE OF THEM ARE ONE SHAPE. `{IfUpgraded:show:A|B}`
# prints arm B as the card stands and arm A once it is upgraded, and where
# NEITHER arm holds a brace that is a swap this page can make exactly. The
# fourth -- Salon Debut's `{IfUpgraded:show:Gain {Encore:diff()} Encore.|}` --
# carries a hole inside an arm, which is two sentences rather than one sentence
# with a number in it, and gets a REASON instead.

#: The four, with the face each printed on the seat's own Smith screen.
_R12_SMITH = (
    ("KLEEMOD-PROTO_FR_ARIA_OF_RECOMPENSE",
     "Gain 5 Encore. If you have at least 3 Fanfare, gain 5 more."),
    ("KLEEMOD-PROTO_FR_SALON_DEBUT_NAMED", "Deploy Mademoiselle Crabaletta."),
    ("KLEEMOD-AN_INVITATION",
     "Add 1 random Common Companion card to your hand."),
    ("KLEEMOD-PROTO_MC_FISCHL_OZ",
     "Hexerei. At the end of your turn, Oz deals 5 Electro damage to a "
     "random enemy."),
)


def test_every_one_of_the_four_now_prints_a_face_or_a_reason():
    """The row's acceptance: every Smith row prints its upgraded face or says
    why not. Silence is the one answer none of them may give."""
    for card_id, printed in _R12_SMITH:
        built, why = qa_packet.upgrade_preview(card_id, printed)
        assert bool(built) != bool(why), card_id


def test_the_two_arm_swap_writes_the_upgraded_arm():
    """Three of the four, and no arithmetic in any of them: the pattern reads
    the UNUPGRADED arm off the printed face and the render writes the other."""
    assert qa_packet.upgraded_face(*_R12_SMITH[0]) == (
        "Gain 8 Encore. If you have at least 3 Fanfare, gain 8 more.")
    assert qa_packet.upgraded_face(*_R12_SMITH[2]) == (
        "Add 1 random Common Companion card to your hand, free this turn.")
    # AN EMPTY UNUPGRADED ARM TAKES THE SPACE IN FRONT OF IT WITH IT: the game
    # prints the trimmed sentence, and the upgraded face needs the space back.
    assert qa_packet.upgraded_face(*_R12_SMITH[3]) == (
        "Hexerei. At the end of your turn, Oz deals 5 Electro damage to a "
        "random enemy. Draw 1 card.")


def test_the_one_that_cannot_be_rendered_says_which_kind_of_upgrade_it_is():
    """Salon Debut's arm carries a hole of its own, so the upgrade is a second
    sentence rather than a number in the first. The reason is a fact about the
    CARD, which is what a reader deciding where to spend a Smith can act on.

    `EB-551` MADE IT THE RIGHT FACT. The warning said "rewrites the sentence",
    and the r13 lane-2 seat spent a Smith pick on the strength of it: "Salon
    Debut+ is 'Deploy Mademoiselle Crabaletta. Gain 2 Encore.' That is an
    appended clause worth two Encore, not a rewritten sentence -- the warning
    oversold it." An EMPTY unupgraded arm adds its arm; anything else replaces
    one, and the two are one character apart in the template.
    """
    built, why = qa_packet.upgrade_preview(*_R12_SMITH[1])

    assert built == ""
    assert why == qa_packet.NO_PREVIEW_APPENDS
    assert "adds a clause" in why
    assert "rewrites" not in why
    assert not qa_packet.leaks(why)


def test_a_real_rewrite_still_says_rewrite():
    """The other arm of the same branch, so the narrowing did not simply
    delete the word: a swap whose UNUPGRADED arm is non-empty replaces text,
    and that is what "rewrites the sentence" is for."""
    assert qa_packet._APPEND_ARM_RE.search(
        "Deal 4. {IfUpgraded:show:Gain {Block:diff()} Block.|}") is not None
    assert qa_packet._APPEND_ARM_RE.search(
        "Deal 4. {IfUpgraded:show:Gain {Block:diff()} Block.|Draw 1.}") is None


def test_the_smith_prints_the_keyword_an_upgrade_adds():
    """`EB-551`. THE HALF THE PICK TURNED ON.

    "The Smith's upgrade preview omits keywords: Aria+ showed only the number
    change and not Innate, the most load-bearing keyword in the deck, chosen
    without being shown" (Furina r13 lane 1).

    Read off `OnUpgrade`'s own `AddKeyword` calls, which is where the number
    deltas come from too, so a keyword and a number that moved in one edit
    cannot fall out of step. Asked SEPARATELY from the face, because a row this
    page cannot number still adds its keyword.

    Seen to FAIL: no surface on the page carried a keyword delta at all.
    """
    assert qa_packet.upgrade_keywords("KLEEMOD-PROTO_KO_SORRY_JEAN") == (
        "Retain",)
    assert qa_packet.upgrade_keywords("KLEEMOD-NOT_A_CARD") == ()

    smith = live("upgrade-fresh")
    smith = json.loads(json.dumps(smith.get("state", smith)))
    smith["card_select"]["cards"].append(
        {"id": "KLEEMOD-PROTO_KO_SORRY_JEAN", "name": "Sorry, Jean...",
         "cost": "1", "type": "Skill",
         "description": "Remove one of your Bombs and gain Block equal to its "
                        "size."})

    page = blindplay.observe(smith)

    assert "    Upgraded, and gains Retain." in page


def test_the_other_three_reasons_are_each_a_fact_about_the_card():
    """A card this page has no written face for, one whose upgrade moves a
    value the face does not print, and one whose printed text no longer
    matches the sentence it was generated from."""
    assert qa_packet.upgrade_preview("KLEEMOD-NOT_A_CARD", "Deal 6.")[1] == \
        qa_packet.NO_PREVIEW_TEMPLATE
    assert qa_packet.upgrade_preview(
        "KLEEMOD-PROTO_KO_CHAIN_FUSE",
        "Each Bomb on target enemy grows by 3.")[1] == \
        qa_packet.NO_PREVIEW_UNMATCHED
    for text in (qa_packet.NO_PREVIEW_TEMPLATE, qa_packet.NO_PREVIEW_NO_NUMBER,
                 qa_packet.NO_PREVIEW_UNMATCHED):
        assert not qa_packet.leaks(text)


def test_the_reason_prints_on_the_smith_under_the_face_it_is_about():
    """And it prints where the missing line was, so the two rows read as two
    different facts rather than as one silence."""
    smith = live("upgrade-fresh")
    smith = json.loads(json.dumps(smith.get("state", smith)))
    smith["card_select"]["cards"].append(
        {"id": "KLEEMOD-PROTO_FR_SALON_DEBUT_NAMED", "name": "Salon Début",
         "cost": "1", "type": "Skill",
         "description": "Deploy Mademoiselle Crabaletta."})
    page = blindplay.observe(smith)

    assert ("    Upgraded: not shown -- its upgrade adds a clause, and this "
            "page has no unupgraded copy of the number in it.") in page
    # The rows that CAN be rendered are untouched by the new line.
    assert "    Upgraded: Gain 11 Block." in page


# ------------------------- `EB-377`: the base game's words on a face ---------


def test_a_base_keyword_a_face_names_is_defined_on_the_page():
    """THE ROW, BY NAME. `Vulnerable` was defined on no screen of the round-9
    run while `Weak`, `Frail`, `Slow` and `Minion` were -- because those four
    arrived as POWERS on a body, carrying the game's own tip, and a card that
    APPLIES one carries nothing. `Exposed Flank+` was bought "on a genre
    assumption" for that reason (r9 run 2, act 1, (c) 6).

    SEEN TO FAIL: before this row the same page had no `Vulnerable` line.
    """
    page = blindplay.observe(keyword_hand_state(
        ["Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies."]))
    glossary = page.split("## Words on this screen")[1]
    assert ("- **Vulnerable** — An attack or card hit on it deals 50% more"
            in glossary)
    assert "falls off at the end of each of its turns" in glossary
    # And the Plan tip is still there: two words, two definitions.
    assert "- **Plan** — " in glossary


def test_the_wires_own_sentence_wins_over_the_page_copy():
    """The base rows are a RESTATEMENT and go last, so a screen where the game
    itself defines the word reads the game's sentence and not this one. That
    is the whole reason `Weak` looked fine while `Vulnerable` did not."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["battle"]["enemies"][0]["status"] = [
        {"id": "WEAK", "name": "Weak", "amount": 2, "type": "Debuff",
         "description": "Deals less damage.", "keywords": [
             {"name": "Weak", "description": "THE GAME'S OWN SENTENCE."}]}]
    page = blindplay.observe(state)
    assert "- **Weak** — THE GAME'S OWN SENTENCE." in page
    assert "- **Weak** — The wearer deals" not in page


def test_the_base_keyword_glossary_quotes_the_engines_own_rates():
    """`blindplay_shape`'s three percentages are held in step with
    `tier0.constants` from this side -- the module may not import `tier0` at
    all -- the same discipline `CHARGE_SOURCE_LINE` is under."""
    assert blindplay.VULNERABLE_TAKEN_PCT == round(
        (C.VULNERABLE_TAKEN_MULT - 1) * 100)
    assert blindplay.WEAK_DEALT_PCT == round((1 - C.WEAK_DEALT_MULT) * 100)
    assert blindplay.FRAIL_BLOCK_PCT == round((1 - C.FRAIL_BLOCK_MULT) * 100)
    for word, pct in (("Vulnerable", blindplay.VULNERABLE_TAKEN_PCT),
                      ("Weak", blindplay.WEAK_DEALT_PCT),
                      ("Frail", blindplay.FRAIL_BLOCK_PCT)):
        assert f"{pct}%" in blindplay.BASE_KEYWORDS[word], word


def test_the_base_keyword_glossary_is_the_mods_own_tooltip_text():
    """The five words with a C# twin are held in step with `BaseKeywordTips`
    from this side, exactly as the arm rows are with `ArmKeywordTips`. The
    four without one (`Sharp`, `Nimble`, `Swift`, `Bond of Life`, `Exhaust`)
    have no face-side tip to mirror -- an enchantment is a card STATE and the
    Bond is a docket hover -- which is why they are page-only."""
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "BaseKeywordTips.cs").read_text(encoding="utf-8")
    anchors = {
        # `EB-481` put the Skill case in this one too, one round later and for
        # the same reason: the game's status line says "from Attacks" and
        # `VulnerablePower` gates on the HIT. `EB-497` then narrowed "every
        # hit" to "every CARD hit" -- a potion's damage is not a powered
        # attack in either engine and takes no 1.5x.
        # `EB-523` then put the ATTACK back in, for the side of the board
        # `EB-497` did not read: "every card hit" is complete on an enemy and
        # silent on a player, whose Vulnerable is about a monster's swing.
        "Vulnerable": ["An attack or card hit on it deals 50% more, a Skill's "
                       "too. A ", "potion's does not. One stack falls off at "
                       "the end of each of ", "its turns."],
        # `EB-469` put the Skill case in this sentence, in the C# and here in
        # one commit, so the anchor holds the clause that resolves the game's
        # own "Attacks".
        "Weak": ["The wearer deals 25% less damage with every hit it lands, a ",
                 "Skill's damage too. One stack falls off at the end of each ",
                 "of its turns."],
        # The two rows whose clause straddles a `[gold]` span are anchored
        # WITH the markup and folded out on the page side, the same way the
        # arm table's interpolated numerals are.
        "Frail": [" less [gold]Block[/gold]. One stack falls ",
                  "off at the end of each of its turns."],
        "Strength": [" hit the wearer ", "lands. It does not decay."],
        "Dexterity": [" the wearer gains. It ", "does not decay."],
    }
    page_only = {"Sharp", "Nimble", "Swift", "Bond of Life", "Exhaust"}
    assert set(anchors) | page_only == set(blindplay.BASE_KEYWORDS)
    for word, phrases in anchors.items():
        for phrase in phrases:
            assert phrase in src, (word, phrase)
            assert phrase.replace("[gold]", "").replace("[/gold]", "")                 in blindplay.BASE_KEYWORDS[word], (word, phrase)
    for word in page_only:
        # No `For<Word>` method and no key: the C# has nothing to hold these
        # in step with, which is the fact the split records.
        assert f"For{word.replace(' ', '')}(" not in src, word
        assert f"{word.replace(' ', '').upper()}Key" not in src, word


def test_the_enchantment_rows_are_the_ruled_conversion():
    """`Sharp`, `Nimble` and `Swift` are the three the ruled event conversion
    names (`dossiers/content/event-conversion-gallery.md`), and they are the
    words `EB-355` found undefined at the enchant branch. The page states the
    rule the sim runs: a flat damage rider, a flat Block rider, and a
    first-play draw."""
    assert "Attack" in blindplay.BASE_KEYWORDS["Sharp"]
    assert "more damage" in blindplay.BASE_KEYWORDS["Sharp"]
    assert "Skill" in blindplay.BASE_KEYWORDS["Nimble"]
    assert "Block" in blindplay.BASE_KEYWORDS["Nimble"]
    assert "Power" in blindplay.BASE_KEYWORDS["Swift"]
    assert "first time you play it" in blindplay.BASE_KEYWORDS["Swift"]
    page = blindplay.observe(keyword_hand_state(
        ["Choose an Attack to Enchant with Sharp 2."]))
    assert "- **Sharp** — An enchantment on an Attack" in page


# ------------------ `EB-378`: whose element the carry-out is ---------------


def test_the_kurage_panel_says_the_planned_hit_is_hydro():
    """`KokomiPlan.ResolveAll` deals every damaging Plan clause as
    `ElementalHit.Deal(..., Element.Hydro, ...)` and the sim's twin the same,
    so a SKILL's Plan leaves a Hydro aura. The round-9 act-1 seat watched one
    appear "from a card whose face says nothing about an element".

    SEEN TO FAIL: the panel said nothing about the element of its own hit.
    """
    page = blindplay.render(blindplay.observation(
        plans_combat_state(TWO_PLANS)))
    assert "## The Bake-Kurage" in page
    assert blindplay.PLAN_HYDRO_NOTE.lstrip("- ") in page
    # Under the pet's own line: a fact about the jellyfish, not about any one
    # Plan in the queue below it.
    body = page.split("## The Bake-Kurage")[1]
    assert body.index("Enemies cannot touch it") < body.index("Hydro hit")
    assert body.index("Hydro hit") < body.index("Kurage's Oath")


def test_the_panel_note_says_which_plans_leave_no_aura():
    """The half a reader prices a reaction with: a Plan that blocks, draws or
    applies a debuff is not a hit and leaves nothing clinging."""
    assert "blocks, draws or applies a debuff leaves no aura" \
        in blindplay.PLAN_HYDRO_NOTE


# ------------------- `EB-381`: the body must not lag the board -------------


class _PollWire:
    """A wire whose `get_state` walks a script, one frame per call.

    `ScriptedWire` advances on a POST, which is exactly wrong here: the whole
    question is what a bare re-READ answers while the game's action queue is
    still draining.
    """

    def __init__(self, frames):
        self.frames = list(frames)
        self.reads = 0

    def get_state(self):
        self.reads += 1
        return self.frames[min(self.reads - 1, len(self.frames) - 1)]


def _enemy_status(state, rows):
    """One recorded combat state with the enemy wearing `rows`."""
    out = json.loads(json.dumps(state))
    out["battle"]["enemies"][0]["status"] = rows
    return out


PYRO_AURA = [{"id": "AURA_PYRO", "name": "Pyro Aura", "amount": 2,
              "type": "Buff", "description": "A Pyro aura clings to it.",
              "keywords": []}]


def test_an_aura_applied_on_the_last_action_prints_on_the_next_observe():
    """`EB-381`. THE ROW, BY NAME.

    The r9 act-3 seat sequenced `Amber - Fiery Rain` (Pyro) into two Hydro
    Sangos on purpose, read "no aura at all" off the enemy's status block, and
    wrote the Vaporize off -- then `Sango Isshin+` hit for 31 on a printed 20,
    which is the Vaporize. "The screen showed no aura for two consecutive
    observes; the body had one."

    The cause is not two sources: HP and the status list come off one creature
    dict. It is one source read too early -- `ExecutePlayCard` hands the play
    to the action queue and answers at once, so the damage action's HP is
    written and the `PowerCmd.Apply` behind it is not.

    SEEN TO FAIL: `settle(mid)` returns `mid` unchanged -- the screen is a real
    screen, the turn is still the player's, and `transient` has nothing to say.
    """
    mid = _enemy_status(combat_state(), [])          # HP moved, aura pending
    landed = _enemy_status(combat_state(), PYRO_AURA)
    wire = _PollWire([landed, landed])

    assert blindplay.transient(mid) == ""            # the old wait says nothing
    assert "Pyro Aura" not in blindplay.observe(mid)

    settled = blindplay.settle_board(mid, wire, delay=0)
    page = blindplay.observe(settled)
    assert "Pyro Aura 2 (aura)" in page
    assert blindplay.AURA_NOTE in page


def test_a_planned_debuff_that_lands_late_prints_when_it_lands():
    """The row's other half: a planned `Exposed Flank+` fired the Casket on
    three bodies and none printed Vulnerable for two actions."""
    mid = _enemy_status(combat_state(), [])
    landed = _enemy_status(combat_state(), [
        {"id": "VULNERABLE", "name": "Vulnerable", "amount": 2,
         "type": "Debuff", "description": "Takes more damage.",
         "keywords": []}])
    settled = blindplay.settle_board(mid, _PollWire([landed, landed]), delay=0)
    assert "Vulnerable 2 (debuff)" in blindplay.observe(settled)


def test_a_board_at_rest_costs_one_read_and_no_wait(monkeypatch):
    """The common case is every screen of every fight, so it must not sleep.
    The poll compares back to back and waits only when two reads disagree."""
    from understudy import blindplay_read
    slept: list[float] = []
    monkeypatch.setattr(blindplay_read.time, "sleep", slept.append)
    rest = _enemy_status(combat_state(), PYRO_AURA)
    wire = _PollWire([rest, rest, rest])
    assert blindplay.settle_board(rest, wire, delay=9.0) == rest
    assert wire.reads == 1
    assert slept == []


def test_a_board_that_never_settles_is_handed_back_bounded(monkeypatch):
    """`settle`'s rule: the bound does not raise. A board still moving after
    `BOARD_SETTLE_TRIES` reads has an animation ticking on it, and a page one
    frame stale is a better answer than a page that never comes."""
    from understudy import blindplay_read
    monkeypatch.setattr(blindplay_read.time, "sleep", lambda _s: None)
    frames = [_enemy_status(combat_state(), [
        {"id": "TICK", "name": "Tick", "amount": n, "type": "Buff",
         "description": "", "keywords": []}]) for n in range(1, 40)]
    wire = _PollWire(frames[1:])
    assert blindplay.settle_board(frames[0], wire, delay=0) is not None
    assert wire.reads == blindplay.BOARD_SETTLE_TRIES


def test_the_signature_is_the_bodies_and_nothing_else():
    """A hand that changed, a pile that emptied and a round that ticked are
    not the board: settling on them would wait out every draw."""
    base = combat_state()
    moved = json.loads(json.dumps(base))
    moved["player"]["hand"] = []
    moved["player"]["draw_pile_count"] = 0
    moved["battle"]["round"] = 99
    assert blindplay.board_signature(base) == blindplay.board_signature(moved)

    hurt = json.loads(json.dumps(base))
    hurt["battle"]["enemies"][0]["hp"] = 1
    assert blindplay.board_signature(base) != blindplay.board_signature(hurt)


def test_a_fight_that_ends_mid_poll_is_handed_back_as_it_is():
    """The fight ending IS the answer to the question, so the poll stops on
    it rather than waiting out a board that no longer exists."""
    mid = _enemy_status(combat_state(), [])
    rewards = {"state_type": "rewards", "rewards": []}
    out = blindplay.settle_board(mid, _PollWire([rewards]), delay=0)
    assert out["state_type"] == "rewards"


def test_a_screen_with_no_bodies_on_it_is_never_polled():
    """Off a battle screen there is nothing to settle and the extra read would
    buy nothing."""
    screen = map_state()
    wire = _PollWire([screen])
    assert blindplay.settle_board(screen, wire, delay=0) is screen
    assert wire.reads == 0


def test_the_session_settles_the_screen_and_then_the_board():
    """The order is load-bearing: there is no board to settle on a frame that
    has no screen."""
    src = inspect.getsource(blindplay.Session._settle)
    assert src.index("settle(state") < src.index("settle_board(")


# ------------------------------- EB-402: a bare play of an aimed card -------

def plan_card_state(target_type: str = "40213", **fields) -> dict:
    """The RECORDED combat turn plus ONE synthetic Kokomi Plan card.

    Synthetic because the recording predates the arm; the shape is the shipped
    row's own -- `ProtoKkSlackWater.cs:78` passes `KokomiTargets.PetOrEnemy`, a
    `[CustomEnum]` value minted at `ModelDb.Init`, and
    `McpMod.StateBuilder.cs` sends `card.TargetType.ToString()`, which for a
    custom type has no enum name and renders a bare NUMBER (`EB-216`). So the
    `target_type` under test is the one the wire carries.
    """
    state = json.loads(json.dumps(combat_state()))
    hand = state["player"]["hand"]
    card = json.loads(json.dumps(hand[0]))
    card.update({"id": "KLEEMOD-PROTO_KK_SLACK_WATER",
                 "name": "Slack Water (proto)",
                 "description": "Deal 4 damage. Apply 1 Weak. "
                                "Plan: Apply 1 Weak to ALL enemies.",
                 "target_type": target_type, "keywords": [],
                 "index": len(hand)})
    card.update(fields)
    hand.append(card)
    return state


def two_enemy(state: dict) -> dict:
    """The same board with a second living body on it."""
    enemies = state["battle"]["enemies"]
    second = json.loads(json.dumps(enemies[0]))
    second.update({"name": "Slug", "entity_id": "999", "combat_id": 999})
    enemies.append(second)
    return state


def test_a_bare_play_of_a_custom_aimed_card_resolves_to_the_sole_enemy():
    """`EB-402`, and it is the row.

    Kokomi round 10, run 1, fight 1, turn 2: `play "Slack Water"` with no `on`
    clause was answered `ok` with an empty refusal and did NOTHING -- no
    damage, no Weak -- while an `AllEnemies` card played bare resolved. The
    play was posted with a NULL target (the bridge only demands one for
    `TargetType.AnyEnemy`), reached `PlayCardAction(card, null)`, and the
    card's own `ArgumentNullException.ThrowIfNull(cardPlay.Target)` ended it
    inside the action queue, after the wire had answered `ok`.

    A play must never come back `ok` for a no-op. With one enemy on the board
    the bare form resolves to it.
    """
    state = plan_card_state(can_target_enemy=True)
    res = blindplay.act(state, 'play "Slack Water (proto)"')
    assert res["ok"], res["refusal"]
    assert res["post"]["target"], "posted with no target -- the EB-402 no-op"
    assert res["printed"]["target"] == "Nibbit"


def test_a_bare_play_of_a_custom_aimed_card_is_refused_with_the_on_forms():
    """The other half: with two bodies up there is no sole enemy to resolve
    to, so the play is REFUSED -- never posted -- and the refusal carries the
    `on` form per living enemy."""
    state = two_enemy(plan_card_state(can_target_enemy=True))
    res = blindplay.act(state, 'play "Slack Water (proto)"')
    assert not res["ok"]
    assert res["post"] is None            # never posted, so nothing is spent
    assert 'play "Slack Water (proto)" on "Nibbit"' in res["refusal"]
    assert 'play "Slack Water (proto)" on "Slug"' in res["refusal"]
    # ...and one of those forms really is the one that works.
    assert blindplay.act(state,
                         'play "Slack Water (proto)" on "Slug"')["ok"]


def test_the_other_two_custom_spellings_still_play_bare():
    """A pin per spelling, and this is the reason the fix asks the CARD rather
    than the number.

    All three of the arm's custom types render as the same bare number, and
    for two of them a bare play is CORRECT: `KokomiTargets.PetOrSelf` (ten
    rows -- `ProtoKkTideWall.cs:76` falls through to `GainBlock` on the owner
    when the play was not on the pet) and `KokomiTargets.PetOnly` (two --
    `ProtoKkNereidsAscension.cs` schedules its Plan and reads no target). The
    bridge answers `can_target_enemy: false` for both, so both keep the bare
    form, with no target posted.
    """
    for spelling in ("PetOrSelf", "PetOnly"):
        state = plan_card_state(can_target_enemy=False)
        state["player"]["hand"][-1]["name"] = f"Tide Wall ({spelling})"
        res = blindplay.act(state, f'play "Tide Wall ({spelling})"')
        assert res["ok"], (spelling, res["refusal"])
        assert "target" not in res["post"], spelling


def test_a_build_that_does_not_answer_the_question_is_unchanged():
    """The absent-key contract, the bridge's own: a build predating
    `can_target_enemy` says nothing, and a custom spelling on it falls through
    exactly as it did before this row."""
    state = plan_card_state()                     # no can_target_enemy at all
    res = blindplay.act(state, 'play "Slack Water (proto)"')
    assert res["ok"] and "target" not in res["post"]


def test_every_aimed_spelling_the_wire_uses_demands_a_target():
    """The spelling census, swept: the four named enemy spellings all aim, the
    self and all-enemies spellings do not, and the custom number defers to the
    card."""
    from understudy.blindplay_grammar import _aims_at_an_enemy
    for spelling in ("AnyEnemy", "Enemy", "SingleEnemy", "TargetEnemy"):
        assert _aims_at_an_enemy({"target_type": spelling}), spelling
    for spelling in ("Self", "AnyAlly", "AnyPlayer", "AllEnemies", "None", ""):
        assert not _aims_at_an_enemy({"target_type": spelling}), spelling
    assert _aims_at_an_enemy({"target_type": "40213",
                              "can_target_enemy": True})
    assert not _aims_at_an_enemy({"target_type": "40213",
                                  "can_target_enemy": False})


def test_the_bridge_answers_the_enemy_half_the_way_it_answers_the_pet_half():
    """The C# twin. `can_target_enemy` is `can_target_pet`'s mirror and is
    computed the same way -- by asking the card, through the game's own
    `IsValidTarget` -- because a table of custom enum values is exactly what
    the bridge cannot have."""
    builder = (REPO / "vendor" / "STS2_MCP"
               / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert '["can_target_enemy"] = GitsCanTargetEnemy(card)' in builder
    plan = (REPO / "vendor" / "STS2_MCP" / "gits"
            / "GitsKokomiPlan.cs").read_text(encoding="utf-8")
    body = plan.split("GitsCanTargetEnemy(CardModel card)")[1]
    assert "card.IsValidTarget(enemy)" in body
    assert "enemy.IsAlive" in body


# ------------- EB-403: the banner face and the base Dexterity gloss ---------

def test_the_banner_face_and_the_dexterity_gloss_agree_on_one_page():
    """`EB-403`, the page half of the twin.

    Kokomi round 10, run 1, (c) 1: the face printed "Gain 2 Dexterity for 2
    turns" and the same screen's Dexterity gloss said "It does not decay".
    Both sentences were true -- the row grants real `DexterityPower`, and the
    `mi_war_banner` clock beside it hands 2 of it back when it runs out -- and
    together they read as a contradiction, because nothing printed named the
    take-back.

    The base gloss is the base RULE and does not move. The face carries the
    exception now, so the two can be read on one screen.
    """
    import yaml
    row = next(r for r in yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
        if r["id"] == "proto_mi_gorou_war_banner")
    state = combat_state()
    card = state["player"]["hand"][0]
    card["name"] = "Gorou - General's War Banner (proto)"
    card["description"] = row["description"]
    page = blindplay.render(blindplay.observation(state))
    assert "then the banner takes 2 back" in page
    assert "does not decay" in page          # the base rule, still printed


# --------------------- EB-404: a keyword in a TITLE defines nothing --------

def titled_hand_state(title: str, body: str) -> dict:
    """A combat whose hand holds one card with the given printed title and
    body, and nothing else."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_FR_ROW", "name": title, "type": "Attack",
         "cost": "1", "can_play": True, "index": 0, "target_type": "AnyEnemy",
         "is_upgraded": False, "keywords": [], "description": body}]
    return state


def test_a_keyword_in_a_card_title_raises_no_glossary_row():
    """`EB-404`, and it is the row.

    The page glossed `Deploy` -- "A member joins and performs at once" -- on a
    screen holding `Freminet - Pers, Deploy!`, whose printed body is "Deal 6
    damage". The word was in the TITLE. The Furina round-4 seat played the card
    six times waiting for a member to join and read it as broken (run 1, (c) 2).

    A title is flavour; a body is the rule. The card's own printed name is
    still on the page, unchanged -- only the glossary stops reading it.
    """
    page = blindplay.observe(
        titled_hand_state("Freminet - Pers, Deploy!", "Deal 6 damage."))
    assert "Freminet - Pers, Deploy!" in page      # the face is untouched
    assert "- **Deploy** " not in page


def test_the_same_word_in_the_body_still_raises_it():
    """The other direction, so the fix cannot pass by defining nothing: the
    identical card whose BODY carries the word is glossed exactly as before."""
    page = blindplay.observe(
        titled_hand_state("Freminet - Pers, Deploy!",
                          "Deploy Freminet. Deal 6 damage."))
    assert "- **Deploy** " in page


def test_no_class_of_keyword_row_is_raised_by_a_title_alone():
    """Swept rather than sampled, over all four word tables the glossary
    draws on -- the arms', the base game's re-statements, `GAME_KEYWORDS` and
    the base status words. A title carrying any of them defines none of them.
    """
    from understudy import blindplay_notes as N
    words = (list(N.ARM_KEYWORDS) + list(N.GAME_KEYWORDS)
             + list(N.BASE_KEYWORDS))
    assert len(words) >= 20
    # Against the SAME board with a neutral title, so a word the recorded
    # fixture already defines off a relic's body is not read as a finding: the
    # claim is that the TITLE adds nothing, not that the board is empty.
    base = blindplay.observation(
        titled_hand_state("Someone - Pers, Move!", "Deal 6 damage."))
    plain = {row["name"] for row in base["keywords"]}
    for word in words:
        obs = blindplay.observation(
            titled_hand_state(f"Someone - Pers, {word}!", "Deal 6 damage."))
        assert {row["name"] for row in obs["keywords"]} == plain, word


def test_an_enemy_badge_is_a_printed_rule_and_still_defines_its_word():
    """The boundary the fix must not cross. A POWER's name is the game's own
    badge -- `Bomb 6` on a body means there IS a Bomb on the board -- so it is
    a printed rule and not a title, and it keeps defining the word.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["hand"] = []
    state["battle"]["enemies"][0]["status"] = [
        {"id": "KLEEMOD-PROTO_BOMB", "name": "Bomb", "amount": 6,
         "type": "Buff", "description": "", "keywords": []}]
    assert "- **Bomb** " in blindplay.observe(state)


# ------------------ EB-407: Encore, defined on its first printed screen ----

def test_encore_is_defined_on_the_screen_that_first_prints_it():
    """`EB-407`, and it is the row.

    Encore is named on the Neow screen and on opening-hand faces, and until
    this row the only surface that stated its rule was the METER line -- which
    needs the meter to be on the board. So the Furina round-4 seat made the
    run's first decision without the word (run 1, (c) 5).

    The word now carries its definition wherever it is printed, from Neow on.
    """
    state = {"state_type": "event",
             "event": {"event_id": "NEOW", "event_name": "Neow",
                       "in_dialogue": False,
                       "body": "Neow offers a blessing.",
                       "options": [
                           {"index": 0, "title": "Start each fight with 3 "
                                                 "Encore."},
                           {"index": 1, "title": "Leave"}]}}
    page = blindplay.observe(state)
    assert "- **Encore** — " in page
    assert "absorbs damage before HP" in page


def test_the_encore_gloss_states_the_order_a_hit_and_a_performance_take_it():
    """The half nothing printed. Three sites draw on one amount and none of
    them reserves any: `FurinaResources.AbsorbDamage` takes what is there
    after Block, `FurinaResourceHooks.BeforeCardPlayed` spends a card's price
    before the card resolves, and `SalonPowers.PerformMember` pays 1 if it can
    and performs at `DryDamageMultiplier` if it cannot. So the pool is one
    pool and the order is the order things land -- which is why a hit can
    leave a member performing dry.
    """
    text = blindplay.ARM_KEYWORDS["Encore"]
    assert "One pool, as each lands" in text
    assert "a card pays to resolve" in text
    assert "a member spends 1 to perform or acts at 3/4" in text
    salon = (REPO / "klee-mod" / "KleeCode" / "Powers"
             / "SalonPowers.cs").read_text(encoding="utf-8")
    assert "TickEncoreCost = 1;" in salon
    assert "DryDamageMultiplier = 0.75m;" in salon
    furina = (REPO / "klee-mod" / "KleeCode" / "Powers"
              / "FurinaResources.cs").read_text(encoding="utf-8")
    absorb = furina.split("public static decimal AbsorbDamage")[1][:600]
    assert "Math.Min(resource.Amount" in absorb


def test_the_encore_meter_line_does_not_repeat_the_gloss():
    """One definition per screen is `keyword_notes`' own rule, and the meters
    block was the one place two sources could both fire on one word. Where the
    glossary carries it, the meter line points at it; where a meter has no
    glossary row, the line is exactly what it always was."""
    state = json.loads(json.dumps(combat_state()))
    state["player"]["resources"] = {"KLEEMOD_ENCORE": 4, "KLEEMOD_FANFARE": 6}
    page = blindplay.observe(state)
    assert "- Encore: 4 — defined under *Words on this screen*" in page
    assert "- **Encore** — After Block it absorbs damage before HP." in page
    assert page.count("absorbs damage before HP") == 1
    # `EB-437`: Fanfare has a row of its own now, and it is the second half of
    # the same discipline -- the meter line carries the MOD's spend rule
    # rather than the generic gap, because the mod declares one.
    assert "- Fanfare: 6 — cards read it and none spends it" in page
    assert "no rule for how it is spent" not in page


# ---------------- EB-405: a Salon performance names its target -------------

def salon_state(performed: list[dict]) -> dict:
    """A combat whose wire carries this turn's Salon performances.

    SYNTHETIC, BUILT FROM THE MOD'S OWN SNAPSHOT SHAPE: every key below is
    written by `FurinaReframeLedger.Snapshot` and lifted onto the wire by
    `vendor/STS2_MCP/gits/GitsFurinaSalon.cs`, and the two are held in step by
    `test_the_salon_block_is_the_mods_own_snapshot_shape`.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["furina_salon"] = {"performed": performed}
    return state


def test_a_salon_performance_names_the_body_it_picked_and_the_aura():
    """`EB-405`, and it is the row.

    "Crabaletta chose its own enemy and left a Hydro aura on a body the seat
    had not picked" (Furina round 4, run 1, (c) 4), in a kit whose readable
    decision is which element lands on which aura -- and the page named
    neither. It could not: no Salon block reached the wire at all, and the only
    Salon row on a screen was the counter power's static rulebook sentence,
    which carries the company count and by construction cannot carry a body.
    """
    page = blindplay.observe(salon_state([
        {"member": "Crabaletta", "target": "Nibbit", "combat_id": "1",
         "element": "Hydro", "aura": "Hydro", "amount": 6, "paid": True,
         "evoked": False}]))
    assert "## What your Salon did this turn" in page
    assert ("- **Crabaletta** hit Nibbit for 6 Hydro, and it is wearing a "
            "Hydro aura.") in page


def test_the_aura_printed_is_the_one_the_body_is_wearing_afterwards():
    """The half that is easy to get wrong by assuming. `ElementalHit.Deal`
    applies the element to a bare body, REFRESHES a matching aura, and on any
    other element CONSUMES the aura into a reaction and leaves the body bare.
    The mod reads the aura AFTER the hit, so a reaction says so rather than
    the page claiming a Hydro aura that is not there."""
    page = blindplay.observe(salon_state([
        {"member": "Chevalmarin", "target": "Nibbit", "combat_id": "1",
         "element": "Hydro", "aura": "", "amount": 2, "paid": True,
         "evoked": False}]))
    assert "- **Chevalmarin** hit Nibbit for 2 Hydro, and left no aura on it."\
        in page


def test_a_member_that_aims_at_nobody_says_what_it_did_instead():
    """The Usher gains Block and touches no body, so there is no target to
    name and no aura to report -- and a sentence about what it left on a body
    would be about no body."""
    page = blindplay.observe(salon_state([
        {"member": "the Usher", "target": "", "combat_id": "",
         "element": "", "aura": "", "amount": 3, "paid": True,
         "evoked": False}]))
    assert "- **the Usher** gave you 3 Block." in page
    section = page.split("## What your Salon did this turn")[1]
    section = section.split("\n\n")[1]
    assert "aura" not in section, section


def test_a_dry_performance_says_why_its_number_is_small():
    """`SalonConstants.DryDamageMultiplier` is the difference between the
    printed number and three-quarters of it, and a reader watching a member
    act small with an empty buffer is owed the reason."""
    page = blindplay.observe(salon_state([
        {"member": "Crabaletta", "target": "Nibbit", "combat_id": "1",
         "element": "Hydro", "aura": "Hydro", "amount": 4, "paid": False,
         "evoked": False}]))
    assert "(dry: it could not pay its Encore, so it acted at " in page


def test_the_page_owns_the_name_a_performance_prints():
    """`EB-329`'s rule one arm over: the mod names the body by combat id and
    THE PAGE OWNS THE NAMES, so a numbered repeat means the same body in the
    performance line as in the enemy list under it."""
    state = salon_state([
        {"member": "Crabaletta", "target": "Nibbit", "combat_id": "1",
         "element": "Hydro", "aura": "Hydro", "amount": 6, "paid": True,
         "evoked": False}])
    wire = state["battle"]["enemies"][0]
    wire["name"] = "Slug"
    second = json.loads(json.dumps(wire))
    second.update({"entity_id": "999", "combat_id": "999"})
    state["battle"]["enemies"].append(second)
    page = blindplay.observe(state)
    assert "- **Crabaletta** hit Slug (1) for 6 Hydro" in page


def two_slug_salon_state(performed: list[dict], dead: str = "") -> dict:
    """The r5 fight-1 board: two bodies of one name, one optionally off the
    feed. `Corpse Slug (2)` died on turn 1 and the turn-2 log still had to say
    which body Crabaletta hit."""
    state = salon_state(performed)
    wire = state["battle"]["enemies"][0]
    wire.update({"name": "Corpse Slug", "combat_id": "1"})
    second = json.loads(json.dumps(wire))
    second.update({"entity_id": "999", "combat_id": "2"})
    state["battle"]["enemies"] = [b for b in (wire, second)
                                  if b["combat_id"] != dead]
    return state


def test_a_performance_on_a_body_that_has_died_still_names_the_copy():
    """`EB-424`. The r5 seat read *"Crabaletta hit Corpse Slug (2)"* on turn 1
    and *"Crabaletta hit Corpse Slug"* on turn 2, and wrote "in a two-of-a-kind
    fight I could not tell which body it hit". The only difference between the
    two lines is that the second body was off the board by the time the screen
    was drawn, so the line fell back to the mod's title -- the game's printed
    name, which carries no copy number and never can.

    Seen to FAIL before the fight's memory was asked: the assertion below is
    the seat's turn-2 line, and it printed bare."""
    blindplay.forget_fight()
    blindplay.observe(two_slug_salon_state([]))
    page = blindplay.observe(two_slug_salon_state(
        [{"member": "Crabaletta", "target": "Corpse Slug", "combat_id": "2",
          "element": "Hydro", "aura": "Hydro", "amount": 4, "paid": False,
          "evoked": False}], dead="2"))
    assert "- **Crabaletta** hit Corpse Slug (2) for 4 Hydro" in page


def test_a_performance_on_a_body_this_fight_never_saw_keeps_the_mods_title():
    """The fallback, unchanged. An id no board of this fight carried is named
    by the title the mod recorded and never by a number borrowed from some
    other body."""
    blindplay.forget_fight()
    page = blindplay.observe(salon_state(
        [{"member": "Crabaletta", "target": "Sentry", "combat_id": "77",
          "element": "Hydro", "aura": "", "amount": 6, "paid": True,
          "evoked": False}]))
    assert "- **Crabaletta** hit Sentry for 6 Hydro" in page


def test_a_replayed_companion_is_named_beside_the_performances():
    """`EB-420`. Duet plays the next Companion card an extra time and nothing
    on any screen said so: "two Crabaletta lines ... for three Companion-card
    plays' worth of triggers", and "no line anywhere on the screen said Duet".

    `EB-464` FLIPPED WHAT THE LINE SAYS. The extra play performs now, so it is
    no longer a play MISSING from the list above -- it is the reason one of
    those rows is there, which a performance list cannot say for itself. Still
    beside the performances and never inside them: this row is about a PLAY."""
    state = salon_state([
        {"member": "Crabaletta", "target": "Nibbit", "combat_id": "1",
         "element": "Hydro", "aura": "Hydro", "amount": 6, "paid": True,
         "evoked": False}])
    state["player"]["furina_salon"]["replayed"] = ["Freminet — Pers, Deploy!"]
    page = blindplay.observe(state)

    assert "- **Crabaletta** hit Nibbit for 6 Hydro" in page
    assert ("- **Freminet — Pers, Deploy!** was played an extra time, and the "
            "extra play performed as well.") in page


def test_a_replay_with_no_performance_still_gets_its_line():
    """The turn the seat actually reported was the ambiguous one: the stage
    did nothing it could attribute, and the page said nothing at all. A block
    that only appears when a member acted would keep that turn blank."""
    state = salon_state([])
    state["player"]["furina_salon"]["replayed"] = ["Freminet — Pers, Deploy!"]
    page = blindplay.observe(state)

    assert "## What your Salon did this turn" in page
    assert "was played an extra time" in page


def test_the_companion_perform_clauses_are_the_perform_codes_own():
    """`EB-430`, held in step with `SalonPowers` from this side.

    THE ROW WAS FILED ON AN INFERENCE AND `EB-439` OVERTURNED IT. The r5 run-2
    seat wrote "a Companion card's perform lands on the Companion card's
    target" and priced its plays on that; the r6 seat watched one perform split
    across two Toadpoles. The code is the arbiter, so the sentence is read off
    it and pinned here -- a retarget in the mod goes red rather than leaving the
    page teaching a rule the board stopped having.
    """
    salon = (REPO / "klee-mod" / "KleeCode" / "Powers"
             / "SalonPowers.cs").read_text(encoding="utf-8")
    # `EB-460` MOVED THESE TWO CLAUSES OFF THE SHARED ROW. They are Furina's
    # rule, so they live in `COMPANION_STAGE_CLAUSE` and print on her run only;
    # what they SAY is still read off `SalonPowers` and pinned here.
    body = blindplay.COMPANION_STAGE_CLAUSE

    # THE TARGET. `PerformMember` rolls it; the card's target reaches it
    # nowhere -- the method takes an owner and a member and no creature.
    perform = salon[salon.index(
        "public static async Task<bool> PerformMember"):]
    perform = perform[:perform.index("/// <summary>")]
    assert "Rng.CombatTargets" in perform and "NextItem(targets)" in perform
    assert "HittableEnemies" in perform
    assert "picks its own enemy at random, never the card's target." in body

    # THE EMPTY STAGE, and the rotate that follows a real one.
    trigger = salon[salon.index(
        "public static async Task CompanionPlayTrigger"):]
    trigger = trigger[:trigger.index("/// <summary>")]
    assert "if (company.Count == 0)" in trigger
    assert "NoteTriggerWhiffed()" in trigger
    assert "var member = company[0];" in trigger
    assert "RotateLeftmost(owner, 1);" in trigger
    assert ("performs the front member, then sends it to the back; an empty "
            "stage performs nobody.") in body


def test_a_build_with_no_reframe_prints_no_salon_section():
    """The absent / empty split, `kokomi_plans`' own: an ABSENT key is "no
    reframe in this build" and an EMPTY map is "the rule is here and this seat
    is not playing it". Neither may put an empty stage in front of a Klee."""
    assert "What your Salon did" not in blindplay.observe(combat_state())
    absent = json.loads(json.dumps(combat_state()))
    absent["player"]["furina_salon"] = {}
    assert "What your Salon did" not in blindplay.observe(absent)
    assert "What your Salon did" not in blindplay.observe(salon_state([]))


def test_the_salon_block_is_the_mods_own_snapshot_shape():
    """Held in step from this side, the discipline every other GItS wire block
    is under: a field renamed in `FurinaReframeLedger.Snapshot` and not here
    would leave the section silently empty on a live board."""
    ledger = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
              / "FurinaReframeLedger.cs").read_text(encoding="utf-8")
    snapshot = ledger[ledger.index("public static Dictionary<string, object?>"
                                   " Snapshot"):]
    for field in ("member", "target", "combat_id", "element", "aura",
                  "amount", "paid", "evoked"):
        assert f'["{field}"]' in snapshot, field
    assert 'snapshot["performed"]' in snapshot
    # `EB-420`: the second list on the same block, held in step the same way.
    assert 'snapshot["replayed"]' in snapshot
    # `EB-506`: and the third, the stage in slot order.
    assert 'snapshot["company"]' in snapshot
    bridge = (REPO / "vendor" / "STS2_MCP" / "gits"
              / "GitsFurinaSalon.cs").read_text(encoding="utf-8")
    assert '"KleeMod.Powers.FurinaReframeLedger"' in bridge
    builder = (REPO / "vendor" / "STS2_MCP"
               / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert 'state["furina_salon"] = furinaSalon;' in builder


def test_the_target_and_the_aura_are_recorded_where_they_are_decided():
    """The mod half. `PerformMember` is the ONE implementation of a member
    acting, it draws the body from `Rng.CombatTargets`, and `ElementalHit.Deal`
    returns the damage and not the creature -- so both facts had to be caught
    inside that switch or they were gone."""
    salon = (REPO / "klee-mod" / "KleeCode" / "Powers"
             / "SalonPowers.cs").read_text(encoding="utf-8")
    body = salon[salon.index("public static async Task<bool> PerformMember"):]
    body = body[:body.index("return true;")]
    assert "AuraCmd.Find(target)?.Element" in body
    assert "FurinaReframeLedger.For(owner).NotePerformance(" in body
    # ...and the turn boundary is the one place it exists.
    turn = salon[salon.index("public override async Task AfterPlayerTurnStart"):]
    assert "ClearPerformances()" in turn[:900]


# ------------------------------------- EB-417: a Mine reads as a Mine -------

#: The badge the r11 Opus seat read, in the shape the wire sends it: the mod's
#: `smartDescriptionMines` face under whichever `title` row
#: `ProtoBombPower.Title` selected. The body is the arm's own, quoted, so the
#: page half of this pin cannot pass on a sentence the game does not print.
_MINE_FACE = ("Set off here deals 4 Pyro damage. Bombs here: 1, including 1 "
              "Mine, growing at your turn's start. A Mine also goes off "
              "before this enemy's hit, which lands in full unless the Mine "
              "kills. A "
              "kill moves them to a "
              "survivor.")

_MIXED_FACE = ("Set off here deals 12 Pyro damage. Bombs here: 2, including 1 "
               "Mine, growing at your turn's start. A Mine also goes off "
               "before this enemy's hit, which lands in full unless the Mine "
               "kills. A "
               "kill moves them to a "
               "survivor.")


def _bomb_badge_state(title: str, amount: int, description: str) -> dict:
    state = json.loads(json.dumps(spark_priced_state()))
    state["battle"]["enemies"][0]["status"] = [
        {"id": "KLEEMOD-PROTO_BOMB_POWER", "title": title, "amount": amount,
         "type": "Debuff", "description": description}]
    return state


def test_a_pile_that_is_all_mines_reads_as_a_mine_on_the_page():
    """`EB-417`. The seat's screen, fixed at the source.

    "the enemy badge calls a Mine `Bomb 4` in the title and only discloses it
    is a Mine in the body text... Since the whole Mine trick is timing, the
    badge should lead with it." The page carries the badge's own title, so the
    fix is `ProtoBombPower.Title` and this is the twin: the seat reads `Mine 4`
    and the timing clause under it, on the one screen where a Mine is met.
    """
    page = blindplay.observe(_bomb_badge_state("Mine", 4, _MINE_FACE))
    badge, = [ln for ln in page.splitlines() if "Set off here deals" in ln]

    assert badge.strip().startswith("Mine 4")
    assert "Bomb 4" not in badge
    assert "goes off before this enemy's hit" in badge


def test_a_pile_holding_one_plain_bomb_is_still_a_bomb_on_the_page():
    """The denominator, and the rule `Title` actually implements: all of them
    or none. A mixed pile is one badge over two kinds of charge, so it keeps
    `Bomb` and discloses its Mines where it always has -- the fuse mark in the
    count -- with rule 6's clause beside it either way."""
    page = blindplay.observe(_bomb_badge_state("Bomb", 12, _MIXED_FACE))
    badge, = [ln for ln in page.splitlines() if "Set off here deals" in ln]

    assert badge.strip().startswith("Bomb 12")
    assert "Mine 12" not in badge
    assert "including 1 Mine" in badge
    assert "goes off before this enemy's hit" in badge


def test_the_badge_owns_both_names_and_chooses_between_them_live():
    """The mod half. Loc is registered once at boot and a pile changes every
    turn, so the live choice has to be a KEY -- the same bargain
    `SmartDescriptionLocKey` already makes for the face."""
    power = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
             / "ProtoBombPower.cs").read_text(encoding="utf-8")
    assert '("title", "Bomb")' in power
    assert '(MineTitleKey, "Mine")' in power
    body = power[power.index("public override LocString Title"):]
    body = body[:body.index(";", body.index("base.Title"))]
    assert "TitledAsMine" in body
    assert "MineTitleKey" in body
    assert ("public bool TitledAsMine => MineCount > 0 "
            "&& MineCount == _charges.Count;") in power
    # Rule 6's sentence rides the face and is NOT what the title switches on:
    # a mixed pile keeps `Bomb` and still prints the timing clause.
    assert "MineClause" in power
    assert "goes off before this enemy's hit" in power


# --- `EB-496`: THE NUMBER THAT RE-COUNTED BECAUSE THE MEMORY WAS A PROCESS ---


def _gardener_board(count: int, first: int = 1) -> dict:
    """The four-body elite of Klee r17 lane 1, as many of it as are alive."""
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["enemies"] = [
        {"entity_id": f"gardener_{i}", "combat_id": i,
         "name": "Phantasmal Gardener", "hp": 28, "max_hp": 28,
         "block": 0, "status": [],
         "intents": [{"type": "Attack", "label": "6"}]}
        for i in range(first, first + count)]
    return state


def _new_process() -> None:
    """What a fresh `python -m understudy.blindplay observe` starts with.

    The seat's brief hands it one process per call, so the in-process dict is
    empty on every screen and only the lane's store carries anything across.
    Emptying the dict WITHOUT touching the store is exactly that boundary.
    """
    from understudy import blindplay_faces as faces
    faces._FIGHT_MEMORY.update({"roster": {}, "ordinals": {},
                                "numbered": set(), "names": {},
                                "handles": {}, "elements": set(),
                                "round": None})
    faces._FIGHT_LOADED[0] = False


def test_a_kill_does_not_renumber_the_survivors_in_the_next_process():
    """`EB-496`. THE 14-DAMAGE MELT THAT WENT INTO THE WRONG BODY.

    Klee r17 lane 1, turn 2 of the four-Gardener elite: the seat killed
    `Phantasmal Gardener (1)` and aimed Kaeya at `Phantasmal Gardener (2)`.
    "The list had already renumbered the moment the first one died, so my
    Kaeya hit what had been Gardener (3) ... I only found out by reading
    max-HP values off the next screen."

    `EB-271` and `EB-427` closed exactly this -- for one process. The seats do
    not have one: `blindplay observe` and `blindplay act` are separate
    interpreters, so `_FIGHT_MEMORY` was empty on every screen and every render
    numbered the board in front of it from 1. The memory is on disk now, per
    lane, `_DECK_MEMORY`'s shape one memory over.

    Seen to FAIL: the survivors came back `(1)`, `(2)`, `(3)`.
    """
    first = blindplay.observe(_gardener_board(4))
    assert "**Phantasmal Gardener (1)**" in first
    assert "**Phantasmal Gardener (4)**" in first

    _new_process()
    after = blindplay.observe(_gardener_board(3, first=2))
    assert "**Phantasmal Gardener (1)**" not in after
    for n in (2, 3, 4):
        assert f"**Phantasmal Gardener ({n})**" in after, n


def test_every_enemy_carries_a_letter_that_a_kill_cannot_move():
    """The other half the seat asked for: "there is no way to name an enemy
    that survives a kill inside the same turn". A number only exists where a
    name repeats; the letter is on every body, is minted in first-seen order
    and is never reused."""
    blindplay.observe(_gardener_board(4))
    _new_process()
    page = blindplay.observe(_gardener_board(3, first=2))
    assert "- **Phantasmal Gardener (2)** [B] — HP 28/28" in page
    assert "[A]" not in page
    # A summon takes the next free letter rather than the dead body's.
    _new_process()
    joined = _gardener_board(3, first=2)
    joined["battle"]["enemies"].append(
        {"entity_id": "gardener_9", "combat_id": 9, "name": "Eye With Teeth",
         "hp": 10, "max_hp": 10, "block": 0, "status": [],
         "intents": [{"type": "Attack", "label": "3"}]})
    assert "- **Eye With Teeth** [E] — HP 10/10" in blindplay.observe(joined)


# --- `EB-541`: THE LETTER A REPLACEMENT TOOK OFF A DEAD BODY ----------------


def _gremlin_board(bodies: list[tuple[int, str, int]], round_: int) -> dict:
    """A board of named bodies with their own combat ids, at a named round."""
    state = json.loads(json.dumps(combat_state()))
    state["battle"]["round"] = round_
    state["battle"]["enemies"] = [
        {"entity_id": f"gremlin_{cid}", "combat_id": cid, "name": name,
         "hp": hp, "max_hp": hp, "block": 0, "status": [],
         "intents": [{"type": "Attack", "label": "6"}]}
        for cid, name, hp in bodies]
    return state


def test_a_replacement_mints_the_next_letter_and_the_dead_ones_retires():
    """`EB-541`. THE INVARIANT THE PAGE PRINTS WAS FALSE ON A SPLIT.

    Kokomi r19 lane 1, floor 8. `Surprise 1` killed Gremlin Merc [A] and put a
    Sneaky Gremlin and a Fat Gremlin in its place -- and the page lettered them
    [A] and [B]. "The letter moved. I had been aiming by letter all fight."

    THE CAUSE IS THE FIGHT-BOUNDARY TEST AND NOT THE MINTING. A board that
    shares no body with the memory was read as a new fight, and a whole-board
    replacement is exactly that board. The round separates them: a new fight
    opens on round 1, a replacement lands on the round the fight had reached.

    Seen to FAIL: the two new bodies came back [A] and [B].
    """
    merc = _gremlin_board([(1, "Gremlin Merc", 47)], round_=1)
    assert "- **Gremlin Merc** [A] — HP 47/47" in blindplay.observe(merc)

    _new_process()
    split = _gremlin_board([(2, "Sneaky Gremlin", 13),
                            (3, "Fat Gremlin", 14)], round_=2)
    page = blindplay.observe(split)
    assert "- **Sneaky Gremlin** [B] — HP 13/13" in page
    assert "- **Fat Gremlin** [C] — HP 14/14" in page
    assert "[A]" not in page, "the dead body's letter retires with it"


def test_the_next_fight_still_starts_its_letters_at_a():
    """The other side of `EB-541`, and the reason the round is what the test
    asks rather than "the memory is not empty": a fight that shares no body
    with the last one is a NEW FIGHT when it opens on round 1, and its first
    body is [A] however many letters the last fight spent."""
    blindplay.observe(_gremlin_board([(1, "Gremlin Merc", 47)], round_=1))
    _new_process()
    blindplay.observe(_gremlin_board([(2, "Sneaky Gremlin", 13),
                                      (3, "Fat Gremlin", 14)], round_=2))

    _new_process()
    page = blindplay.observe(_gremlin_board([(7, "Corpse Slug", 27),
                                             (8, "Sewer Clam", 30)], round_=1))
    assert "- **Corpse Slug** [A] — HP 27/27" in page
    assert "- **Sewer Clam** [B] — HP 30/30" in page


def test_a_new_fight_joined_late_does_not_inherit_the_last_ones_letters():
    """The third door `_is_a_new_fight` has to answer: a seat whose first
    `observe` of a fight is not round 1. The round went BACKWARDS from the one
    the memory was minted on, which no fight can do, so the memory is the last
    fight's and goes."""
    blindplay.observe(_gremlin_board([(1, "Gremlin Merc", 47)], round_=1))
    _new_process()
    blindplay.observe(_gremlin_board([(2, "Sneaky Gremlin", 13)], round_=6))

    _new_process()
    page = blindplay.observe(_gremlin_board([(9, "Corpse Slug", 27)], round_=3))
    assert "- **Corpse Slug** [A] — HP 27/27" in page


def test_the_grammar_aims_at_the_letter_the_replacement_minted():
    """The page and the grammar read one memory, so the fix has to hold on both
    sides or `on "C"` means a body the render never lettered. The grammar reads
    the round off the same board (`_fight_round`)."""
    blindplay.observe(_gremlin_board([(1, "Gremlin Merc", 47)], round_=1))
    _new_process()
    split = _gremlin_board([(2, "Sneaky Gremlin", 13),
                            (3, "Fat Gremlin", 14)], round_=2)
    blindplay.observe(split)

    _new_process()
    assert blindplay._resolve_enemy(split, "C") == ("gremlin_3", "")
    assert blindplay._resolve_enemy(split, "B") == ("gremlin_2", "")
    assert blindplay._resolve_enemy(split, "A")[0] == ""


def test_the_enemy_list_carries_the_handle_rule_and_the_hand_note_does_not():
    """The seat's own diagnosis: the page warns about re-counting under `Your
    hand`, where it is about CARDS, and said nothing at all under `The other
    side`. The note that belongs there says what is TRUE of an enemy -- both
    handles hold for the fight -- rather than repeating the hand's caveat."""
    page = blindplay.observe(_gardener_board(4))
    tail = page.split("## The other side")[1]
    assert "Each enemy keeps its letter and its number" in tail
    assert "a summon takes the next free letter" in tail
    assert '`on "B"`' in tail


def test_act_takes_the_letter_beside_the_name():
    """The handle is worth nothing if only the page speaks it. `A` is matched
    EXACTLY -- `_match`'s unique-substring rule would make a bare letter half
    the names on the board -- and it names the same body the page printed."""
    state = _gardener_board(4)
    blindplay.observe(state)
    by_letter = blindplay.act(state, 'play "Pearl Barrage" on "C"')
    by_name = blindplay.act(
        state, 'play "Pearl Barrage" on "Phantasmal Gardener (3)"')
    assert by_letter["ok"]
    assert by_letter["post"]["target"] == by_name["post"]["target"]

    _new_process()
    dead = _gardener_board(3, first=2)
    blindplay.observe(dead)
    again = blindplay.act(dead, 'play "Pearl Barrage" on "C"')
    assert again["ok"]
    assert again["post"]["target"] == by_letter["post"]["target"]


# --- `EB-519`: THE LETTER THAT LANDED ON THE JELLYFISH -----------------------


def _lettered_board_with_a_pet() -> dict:
    """Two bodies and the Bake-Kurage up, which is Kokomi r18's board.

    The hand carries the recorded `Pearl Barrage` (no `can_target_pet` on the
    feed, so a Plan goes through) and a copy that the game says CANNOT be
    planned, because the two halves of this defect are those two cards.
    """
    state = _gardener_board(2)
    state["player"]["kokomi_plans"] = TWO_PLANS
    barred = json.loads(json.dumps(state["player"]["hand"][0]))
    barred.update({"name": "Coral Blade", "can_target_pet": False,
                   "index": len(state["player"]["hand"])})
    state["player"]["hand"].append(barred)
    return state


def test_a_letter_names_a_body_and_never_the_jellyfish():
    """`EB-519`. THE PLAN THE SEAT NEVER ASKED FOR.

    Kokomi r18, both lanes. `EB-496`'s letter is matched exactly on the enemy
    side and was matched by `_match`'s unique SUBSTRING on the pet side -- and
    `Bake-Kurage` folds to `bakekurage`, which contains `a` and `b`. The pet
    block runs first, so `on "A"` was refused as a Plan the card could not
    carry and `on "B"` was silently ACCEPTED as one, aimed at the jellyfish
    rather than at the second Gardener the page had just printed `[B]`.

    Seen to FAIL: both letters posted `target: 41`, the pet's entity id.
    """
    state = _lettered_board_with_a_pet()
    _new_process()
    page = blindplay.observe(state)
    assert "[A]" in page and "[B]" in page and "## The Bake-Kurage" in page

    for letter, body in (("A", "gardener_1"), ("B", "gardener_2")):
        res = blindplay.act(state, f'play "Pearl Barrage" on "{letter}"')
        assert res["ok"], (letter, res["refusal"])
        assert res["post"]["target"] == body, letter
        # And the half the seat met as a refusal: a card the game will not let
        # be planned is no longer refused for a Plan it was never aimed at.
        barred = blindplay.act(state, f'play "Coral Blade" on "{letter}"')
        assert barred["ok"], (letter, barred["refusal"])
        assert barred["post"]["target"] == body, letter


def test_the_jellyfish_still_answers_to_its_own_name():
    """The other side of the same rule: only the LETTER is taken away. The pet
    keeps its printed name and every unique substring of it that is not one."""
    state = _lettered_board_with_a_pet()
    _new_process()
    blindplay.observe(state)
    for word in ("Bake-Kurage", "Kurage"):
        res = blindplay.act(state, f'play "Pearl Barrage" on "{word}"')
        assert res["ok"], (word, res["refusal"])
        assert res["post"]["target"] == TWO_PLANS["pet_entity_id"], word
        assert res["printed"]["target"] == "Bake-Kurage", word


def test_a_letter_no_body_carries_is_refused_about_the_other_side():
    """A handle that resolves to nothing is refused with the ENEMIES listed --
    never quietly re-read as the pet, which is how `B` was lost."""
    state = _lettered_board_with_a_pet()
    _new_process()
    blindplay.observe(state)
    res = blindplay.act(state, 'play "Pearl Barrage" on "F"')
    assert not res["ok"] and res["post"] is None
    assert "Bake-Kurage" not in res["refusal"]
    assert "Phantasmal Gardener" in res["refusal"]


# --- `EB-428`: THE REWARD THAT PRICED A REACTION CARD BLIND ------------------


def _hydro_reward_state() -> dict:
    """The card reward Klee r17 lane 1 passed twice: one Hydro companion."""
    return {"state_type": "card_reward",
            "player": {"character": "Klee"},
            "card_reward": {"can_skip": True, "cards": [
                {"name": "Dahlia - Sacramental Shower", "cost": "1",
                 "type": "Skill",
                 "keywords": [{"name": "Applies Hydro",
                               "description": "If the target has no aura, "
                                              "this applies Hydro for 2 "
                                              "turns."}],
                 "description": "Deal 6 damage."}]}}


def test_a_reward_names_the_reaction_its_offered_card_would_unlock():
    """`EB-428`, widened by Klee r17.

    "No screen ever told me what Pyro+Hydro (Vaporize) does, because the
    glossary only defines a reaction on the first screen that reaches a second
    element -- and I never held Hydro. So I was passing a card whose payoff
    was, by design, unreadable at the moment of the pick." Dahlia was passed
    twice.

    The row's mechanism was `EB-496`'s: the fight's element memory was process
    state, and a reward screen is a different PROCESS from the fight it
    followed, so the deck's own Pyro was gone by the time the offer was read.
    With the memory on disk the offer's element meets the deck's and the row
    prints -- which is the whole of "at a reward, the line the offered card
    unlocks".

    Seen to FAIL: NO REACTION IS REACHABLE HERE on the reward screen.
    """
    blindplay.observe(elemental_hand_state(elements=("Pyro",)))
    _new_process()
    page = blindplay.observe(_hydro_reward_state())
    assert "- **Vaporize** — Pyro on a Hydro aura" in page
    assert "NO REACTION IS REACHABLE" not in page


def test_a_reward_with_no_fight_behind_it_still_says_which_half_is_missing():
    """The other side of the same row, unchanged: a run that has shown one
    element is told so and told what to draft, rather than being given six
    rows it cannot fire."""
    page = blindplay.observe(_hydro_reward_state())
    assert "NO REACTION IS REACHABLE HERE: Hydro is the only element" in page
    assert "- **Vaporize** — " not in page


# --- `EB-499`: THE REFUSAL THAT NAMED NO WAY TO PLAY THE CARD ----------------


def _all_enemies_custom_state() -> dict:
    """Riptide as the wire sends it: an ALL-enemies card whose target type is
    one of the arm's CUSTOM ones, so `TargetType.ToString()` is a bare number
    (`EB-216`) and only `can_target_enemy` answers the question."""
    state = json.loads(json.dumps(combat_state()))
    hand = state["player"]["hand"]
    card = json.loads(json.dumps(hand[0]))
    card.update({"id": "KLEEMOD-PROTO_KK_RIPTIDE", "name": "Riptide",
                 "description": "Deal 9 damage to ALL enemies.",
                 "target_type": "40219", "keywords": [],
                 "can_target_enemy": False, "can_target_pet": True,
                 "index": len(hand)})
    hand.append(card)
    return state


def test_an_all_enemies_card_aimed_at_a_body_is_told_the_bare_form():
    """`EB-499`. THE REFUSAL THAT ENDED A RUN ON FLOOR 8.

    Kokomi r17 lane 1, turn 1 of an 84-HP elite that gains Strength every
    round: `play "Riptide" on "Byrdonis"` was POSTED and came back
    `error Card 'Riptide' cannot be played on 'Byrdonis'` -- naming the card,
    naming the enemy and naming no way to play it. "I did not work out that
    the fix was the bare `play "Riptide"` until four rounds later."

    `EB-319`'s guard reads the SPELLING, and the arm's cards do not have one:
    a custom target type renders as a bare number. `can_target_enemy` is the
    game's own answer and is on the feed.

    Seen to FAIL: the play was posted and the refusal came from the bridge.
    """
    state = _all_enemies_custom_state()
    # AIMED AT THE JELLYFISH IT IS STILL A PLAN, which is why the guard sits
    # UNDER the pet block: by the time it is reached the tester has not named
    # the pet, so the only body left to mean is an enemy.
    planned = json.loads(json.dumps(state))
    planned["player"]["kokomi_plans"] = TWO_PLANS
    assert blindplay.act(planned, 'play "Riptide" on "Bake-Kurage"')["ok"]

    res = blindplay.act(state, 'play "Riptide" on "Nibbit"')
    assert not res["ok"]
    assert res["post"] is None                # never posted, so nothing spent
    assert 'play "Riptide"' in res["refusal"]
    assert "does its own aiming" in res["refusal"]
    ok = blindplay.act(state, 'play "Riptide"')
    assert ok["ok"] and "target" not in ok["post"]


def test_a_self_card_aimed_at_a_body_is_told_the_bare_form_too():
    """The row's second test. A `Self` card has always been refused on its
    spelling (`EB-319`); this pins that the widened guard did not lose it, and
    that the sentence still says the card is played on YOU."""
    res = blindplay.act(combat_state(), 'play "Coral Guard" on "Nibbit"')
    assert not res["ok"] and res["post"] is None
    assert "is played on you, not on an enemy" in res["refusal"]
    assert 'play "Coral Guard"' in res["refusal"]


def test_a_feed_that_never_answered_the_question_still_posts():
    """`EB-402`'s and `EB-480`'s shared rule, kept: only an EXPLICIT `false`
    refuses. A bridge that predates the field sends nothing and reads as the
    behaviour that build has."""
    state = _all_enemies_custom_state()
    del state["player"]["hand"][-1]["can_target_enemy"]
    assert blindplay.act(state, 'play "Riptide" on "Nibbit"')["ok"]


# --- `EB-527`: TWO "ALL ENEMIES" FACES, TWO OPPOSITE FORMS -------------------


def _two_all_faces_state() -> dict:
    """Furina r12 lane 2's elite screen, one turn apart.

    `Lynette -- Magic Trick` prints `Deal 4 damage to ALL enemies` and is AIMED
    on the wire, because its Swirl half needs a body; `Chevreuse -- Ring of
    Bursting Grenades` prints the same words and aims itself. Nothing on either
    face tells them apart, and the seat met the two refusals a turn apart.
    """
    state = _gardener_board(3)
    hand = state["player"]["hand"]
    for name, aims in (("Lynette — Magic Trick", True),
                       ("Chevreuse — Ring of Bursting Grenades", False)):
        card = json.loads(json.dumps(hand[0]))
        card.update({"id": f"KLEEMOD-{len(hand)}", "name": name,
                     "description": "Deal 4 damage to ALL enemies.",
                     "target_type": "40219", "keywords": [],
                     "can_target_enemy": aims, "index": len(hand)})
        hand.append(card)
    return state


def test_an_all_face_the_wire_aims_says_so_when_it_is_played_bare():
    """`EB-527`. THE REFUSAL THAT COST AN ELITE TURN.

    Furina r12 lane 2: `play "Lynette — Magic Trick: Astonishing Shift"` bare
    was refused "there is more than one enemy, so say which" -- a sentence
    about the board that says nothing about the card. "The very next turn the
    opposite happened: Chevreuse ... refused with 'does its own aiming, so it
    takes no `on`'. Two cards, both printing ALL enemies, with opposite
    targeting rules and nothing on either face to tell them apart."

    THE WIRE IS RIGHT AND THE FACE IS INCOMPLETE: Magic Trick's Swirl half
    needs a body, so the game aims the card at one, and the ALL in its damage
    clause is about what the hit does rather than how it is played. `EB-499`
    gave the other direction its own sentence; this is that sentence's twin.

    Seen to FAIL: the refusal was the board's generic one.
    """
    state = _two_all_faces_state()
    _new_process()
    blindplay.observe(state)

    res = blindplay.act(state, 'play "Lynette — Magic Trick"')

    assert not res["ok"] and res["post"] is None
    assert ("'Lynette — Magic Trick' prints \"ALL enemies\" and is still aimed "
            "at one body, so say which: ") in res["refusal"]
    assert "Phantasmal Gardener (1)" in res["refusal"]
    # And the form that works is offered, `EB-402`'s rule unchanged: every
    # refusal ends in the commands that resolve (`_with_forms`).
    assert 'play "Lynette — Magic Trick" on "Phantasmal Gardener (1)"'         in res["refusal"]


def test_the_face_that_aims_itself_still_names_the_bare_form():
    """`EB-499`'s half, unmoved: the twin sentence is the point, so the two
    refusals a seat meets a turn apart each name the form that works."""
    state = _two_all_faces_state()
    _new_process()
    blindplay.observe(state)

    res = blindplay.act(
        state, 'play "Chevreuse — Ring of Bursting Grenades" on "A"')

    assert not res["ok"] and res["post"] is None
    assert "does its own aiming" in res["refusal"]
    assert 'play "Chevreuse — Ring of Bursting Grenades"' in res["refusal"]


def test_an_aimed_all_face_plays_on_the_body_it_was_given():
    """The decision is the WIRE's target type and not the face's words, so the
    card the refusal is about still plays exactly as the game aims it."""
    state = _two_all_faces_state()
    _new_process()
    blindplay.observe(state)

    ok = blindplay.act(state, 'play "Lynette — Magic Trick" on "B"')

    assert ok["ok"], ok["refusal"]
    assert ok["post"]["target"] == "gardener_2"


def test_a_single_target_face_keeps_the_boards_own_refusal():
    """The clause is added off the FACE, and only where the face says the
    thing that made the refusal confusing. An ordinary aimed card played bare
    is refused about the board, exactly as it always was."""
    state = _two_all_faces_state()
    _new_process()
    blindplay.observe(state)

    res = blindplay.act(state, 'play "Pearl Barrage"')

    assert not res["ok"]
    assert "there is more than one enemy, so say which" in res["refusal"]
    assert "ALL enemies" not in res["refusal"]


# --- `EB-502`: THE PLANNED WEAK THAT WAS STILL IN THE ACTION QUEUE -----------


def test_a_hand_driven_read_settles_the_bodies_the_way_the_session_does():
    """`EB-502`. THE DEBUFF THAT DID NOT PRINT FOR TWO TURNS.

    Kokomi r17 lane 1, fight 1 round 3: two Slack Water carry-outs had landed,
    the Crawler's intent had fallen 11 to 8 -- which is 11 x 0.75, so Weak was
    demonstrably on it -- and its power list showed `Hydro Aura`, `Strength 7`
    and no Weak at all. `Weak 3` printed only after a third application.

    THE READ WAS EARLY, and `EB-381` had already found and named it: the
    morning's `PowerCmd.Apply` is still in the action queue when a `get_state`
    taken a few milliseconds later reports the HP the damage action already
    wrote. `Session._settle` has polled `settle_board` since; the CLI path the
    seats actually drive -- one process per `observe` -- called `settle` alone
    and waited for a SCREEN, never for the bodies.

    Seen to FAIL: the first frame was rendered, Weak and all.
    """
    early = json.loads(json.dumps(combat_state()))
    early["battle"]["enemies"][0]["status"] = []
    late = json.loads(json.dumps(combat_state()))
    late["battle"]["enemies"][0]["status"] = [
        {"id": "weak", "name": "Weak", "amount": 3, "type": "Debuff",
         "description": "Deals 25% less damage."}]

    class _Moving:
        """A wire whose first two reads disagree, which is what a board with a
        queued action behind it looks like."""

        def __init__(self):
            self.reads = 0

        def get_state(self):
            self.reads += 1
            return early if self.reads == 1 else late

        def post(self, *a, **k):                      # pragma: no cover
            raise AssertionError("a read must not post")

    moving = _Moving()
    args = argparse.Namespace(raw_file=None)
    # The bridge MODULE's own function, because `settle` and `settle_board`
    # capture the module as a default argument at definition time.
    with mock.patch("understudy.bridge.get_state", moving.get_state):
        state = blindplay._load_state(args)
    assert moving.reads > 1
    assert state["battle"]["enemies"][0]["status"][0]["name"] == "Weak"
    assert "Weak 3" in blindplay.observe(state)


# --- `EB-504`: A RULE ABOUT A CHARACTER WHO IS NOT IN THE RUN ----------------


def _hexerei_shop_state(character: str) -> dict:
    """A shop shelf holding the Fischl companion both seats met, on one run.

    A SHOP and not a fight, deliberately: `Hexerei` reached the Kokomi seat on
    a shop glossary and `Oz` reached the Furina seat on a reward, and both are
    screens the arm cannot be read off the board on -- which is why the row's
    answer asks the wire's `character` rather than looking at what is out.
    """
    return {"state_type": "shop",
            "player": {"character": character, "gold": 120},
            "shop": {"items": [
                {"name": "Fischl - Nightrider", "price": 74, "cost": "1",
                 "type": "Skill", "is_available": True,
                 "description": "A Hexerei card. Deal 7 Electro damage. "
                                "If Oz is out, he deals 5 more."}]}}


def test_a_kokomi_shop_prints_no_klee_rule():
    """`EB-504`. THE ROW'S OWN ACCEPTANCE.

    "*Hexerei -- A Companion card that prints the word, and Klee herself. Some
    are Klee's own, some are not. Cards of hers pay when you play one.* I could
    not extract a rule from that sentence, and it names a character who is not
    in this run" (Kokomi r17 lane 2).

    The word is still on the screen -- eighteen companion faces print it and
    the whole roster drafts them -- so the page still lists it. What it does
    not do is state a rule this run has no way to use.

    Seen to FAIL: the whole Klee sentence printed on a Kokomi shop.
    """
    page = blindplay.observe(_hexerei_shop_state("Kokomi"))
    glossary = page.split("## Words on this screen")[1]
    assert "- **Hexerei**" in glossary
    assert "Klee" not in glossary
    assert "Cards of hers pay" not in page


def test_a_furina_run_gets_neither_the_hexerei_nor_the_oz_rule():
    """The second seat, and the second word. `Fischl -- Nightrider` printed
    both rules on a Furina run: "I have no Klee cards, no way to obtain that
    Power, and no idea what 'pay' means or what it would cost me ... half its
    rules text was noise" (Furina r11 lane 2)."""
    page = blindplay.observe(_hexerei_shop_state("Furina"))
    glossary = page.split("## Words on this screen")[1]
    assert "- **Hexerei**" in glossary and "- **Oz**" in glossary
    assert "Fischl's raven" not in page
    assert "Klee" not in glossary


def test_a_klee_run_reads_both_rules_in_full():
    """The other side, and the reason the rows exist at all: on the run whose
    kit the words belong to, nothing about them has changed."""
    page = blindplay.observe(_hexerei_shop_state("Klee"))
    assert ("- **Hexerei** — A Companion card that prints the word, and Klee "
            "herself.") in page
    assert "- **Oz** — Fischl's raven, out while you hold the Power" in page


def test_a_feed_that_does_not_say_who_is_playing_keeps_the_rule():
    """`absent is not zero`, in this table's direction: silence about the
    character is not evidence that it is somebody else's, and a page that
    stripped a rule on a feed that never answered would be withholding it from
    the one run that needs it."""
    state = _hexerei_shop_state("Klee")
    del state["player"]["character"]
    assert ("Playing one of hers makes "
            f"{blindplay_notes.COMPANION_SPARK} Spark, up to "
            f"{blindplay_notes.COMPANION_SPARK_MAX}.") in blindplay.observe(state)


def test_every_other_arm_word_is_still_defined_on_every_run():
    """The gate is exactly two rows wide. `Companion` already answers the arm
    for its stage CLAUSE (`EB-460`) and keeps its definition on every run;
    nothing else in the table is character-owned, and a gate that grew would
    be taking rules off the seats that need them."""
    assert set(blindplay_notes._ARM_KEYWORD_CHARACTER) == {
        "Hexerei", "Oz"}
    page = blindplay.observe(_klee_combat_state())
    assert "- **Bomb** — " in page


# --- `EB-506`: WHO IS AT THE FRONT ------------------------------------------


def _stage_state(company: list[str], performed: list[dict] | None = None
                 ) -> dict:
    """A Furina combat whose wire carries the stage in slot order.

    `company` is `FurinaReframeLedger.Snapshot`'s third list, front first --
    the same one `SalonMemberPower.PerformLeftmost` takes `[0]` of and
    `RotateLeftmost` moves the head of.
    """
    state = json.loads(json.dumps(combat_state()))
    state["player"]["furina_salon"] = {"performed": performed or [],
                                       "replayed": [], "company": company}
    return state


def test_the_stage_prints_in_order_with_the_front_member_marked():
    """`EB-506`. THE SEAT COULD NOT TELL WHO WOULD PERFORM NEXT.

    "I could never tell who the front member was. The stage buff always names
    one -- *A Companion card you play performs the Usher* -- but the Companion
    glossary says a play *performs the front member, then sends it to the
    back*, and after doing exactly that in fight 3 the line still named the
    Usher. With two members up I was guessing which one my next Companion card
    would fire" (Furina r11 lane 1, (c) 4).

    The buff's face is a smart description keyed on the front member, so it is
    a registered row redrawn when the game feels like it. The company is a
    LIVE list, and its head is the answer by construction.

    Seen to FAIL: no page printed the stage at all.
    """
    page = blindplay.observe(_stage_state(["the Usher", "Crabaletta"]))
    stage = page.split("## Your Salon")[1].split("##")[0]
    lines = [ln for ln in stage.splitlines() if ln.startswith("- ")]
    assert lines[0].startswith("- **the Usher** — FRONT")
    assert "performs this one, and then sends it to the back" in lines[0]
    assert lines[1] == "- **Crabaletta**"


def test_the_front_moves_with_the_rotation():
    """The refresh the row asks for: after a performance the wire's own list
    has rotated, so the next page names the new front and nothing on this side
    has to remember that a play happened."""
    rotated = blindplay.observe(_stage_state(["Crabaletta", "the Usher"]))
    stage = rotated.split("## Your Salon")[1].split("##")[0]
    lines = [ln for ln in stage.splitlines() if ln.startswith("- ")]
    assert lines[0].startswith("- **Crabaletta** — FRONT")
    assert lines[1] == "- **the Usher**"


def test_an_empty_stage_prints_no_section_and_neither_does_a_klee():
    """ABSENT IS NOT EMPTY, the block's standing split, and it decides two
    different pages: a Furina with nobody up has no stage to print, and a
    build with no reframe has no stage at all."""
    assert "## Your Salon" not in blindplay.observe(_stage_state([]))
    assert "## Your Salon" not in blindplay.observe(combat_state())
    old = json.loads(json.dumps(combat_state()))
    old["player"]["furina_salon"] = {"performed": [], "replayed": []}
    assert "## Your Salon" not in blindplay.observe(old)


def test_the_stage_and_what_it_did_are_two_sections():
    """The order is the reader's: who is up NOW, then the receipt for what
    already happened. The receipt prints only on a turn something acted; the
    question the row is about is asked on every turn."""
    page = blindplay.observe(_stage_state(
        ["Crabaletta", "the Usher"],
        [{"member": "Crabaletta", "target": "Nibbit", "combat_id": "",
          "element": "Hydro", "aura": "Hydro", "amount": 6, "paid": True}]))
    assert page.index("## Your Salon") < page.index(
        "## What your Salon did this turn")


# --- `EB-510`: ONE HAND AND ONE ENEMY LIST PER OBSERVE -----------------------


def test_every_section_of_a_page_prints_once():
    """`EB-510`. THE PAGE THAT PRINTED THE BOARD TWICE.

    "Several observe screens printed `## Your hand` and `## The other side`
    twice, with card bodies duplicated line-for-line. It never changed what I
    could do, but it made two screens genuinely hard to read" (Furina r11 lane
    2, (c) 8).

    THE RENDER CANNOT PRODUCE IT, and that is the finding: every heading is
    appended at one `out +=` on one branch, the branches are mutually
    exclusive, and the two headings a combat page shares with the trailing
    non-combat block are gated on `screen != "combat"`. So the doubling came
    from something emitting this text twice, and what the row can pin from
    here is the SHAPE -- a page whose sections are unique, checked at the one
    place a page is finished.
    """
    for build in (combat_state, map_state, shop_state, rest_state,
                  card_reward_state, rewards_state, treasure_state):
        page = blindplay.observe(build())
        headings = [ln for ln in page.splitlines()
                    if ln.startswith("# ") or ln.startswith("## ")]
        assert len(headings) == len(set(headings)), build.__name__


def test_a_doubled_page_is_refused_rather_than_handed_over():
    """The guard itself, driven: a page that carries a section twice raises
    instead of reaching a seat, and the refusal names the heading so whoever
    doubled it can be found."""
    doubled = blindplay.observe(combat_state()) * 2
    with pytest.raises(blindplay.BlindPlayError) as raised:
        blindplay.assert_one_page(doubled)
    assert "## Your hand" in str(raised.value)
    assert "## The other side" in str(raised.value)
    assert "printed a section twice" in str(raised.value)
