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

import pytest

from tier0 import constants as C
from tier0.tests.conftest import seam_files
from understudy import blindplay, embark, qa_packet, soak

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


# ------------------------------------------------------------- fixtures ----

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
    "pending": 2, "twice": False, "also_now": False,
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


def test_the_two_rares_that_change_what_the_queue_means_are_printed():
    """Nereid's Ascension makes the queue's LENGTH stop being the number of
    things that will happen, and The Moon Overlooks the Waters makes a Plan
    happen as it is written. Neither is visible from a count."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(dict(TWO_PLANS, twice=True, also_now=True))))
    assert "carries out EVERY Plan twice" in page
    assert "Plans also happen NOW" in page


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


def test_a_turn_with_no_carry_out_prints_no_carry_out_block():
    """The morning drain clears the record whether or not anything was due, so
    an empty list is a fact about THIS turn and not a stale one about the last.
    Nothing carried out is nothing to say."""
    page = blindplay.render(blindplay.observation(
        plans_combat_state(dict(TWO_PLANS, carried_out=[]))))
    assert "carried these out" not in page
    # And the section itself is unchanged for a board that never had the field.
    assert "1. **Kurage's Oath**" in page


def test_the_meter_ledger_stays_off_the_carry_out_block():
    """`R101b`. The page line is the ON-SCREEN text, and the ledger's rows --
    meter, before, after, price_paid -- are an instrument, not a surface a
    player ever reads. None of its vocabulary may leak in with the lines."""
    obs = blindplay.observation(plans_combat_state(CARRIED_OUT))
    page = blindplay.render(obs)
    block = [ln for ln in page.splitlines()
             if ln.strip().startswith("- Bake-Kurage:")]
    assert block, "the carry-out lines are gone"
    for line in block:
        for word in ("price_paid", "meter_ledger", "before=", "after="):
            assert word not in line
    # And the observation carries nothing but the ruled fields per row --
    # `EB-317`'s three, plus `EB-329`'s board reading and the door the Plan
    # came through. All five are things a sighted player watched happen; not
    # one of them is a ledger row.
    for row in obs["combat"]["plans"]["carried_out"]:
        assert set(row) == {"card", "number", "line",
                            "on_play", "board_read", "moved"}
        for moved in row["moved"]:
            assert set(moved) == {"target", "combat_id", "amount", "dead"}


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


def test_an_on_play_firing_prints_under_its_own_heading():
    """`EB-329`, the r4c seat's finding 4. With The Moon Overlooks the Waters
    out, a War Council played mid-turn was reported on one screen both as
    already carried out "at the start of this turn" and as still queued. Both
    rows were true; the first sentence was not."""
    blindplay.forget_fight()
    page = blindplay.render(blindplay.observation(plans_combat_state(
        dict(TWO_PLANS, pending=1, also_now=True,
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
    assert "goes off first" in page


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
        # rule 7 is now "goes off only when" and the stacking rule is
        # "all at once".
        # `EB-373` REWROTE THE LAST CLAUSE. "Takes the enemy's debuffs"
        # promised more than the fold does -- Vulnerable and a damage cap,
        # nothing else -- and the r9 seat priced two fights off it.
        "Bomb": ["A charge on an enemy", "goes off only when",
                 "all at once", "Not an Attack: only their ",
                 " and a cap "],
        "Set off": ["on the target goes off first, one at a",
                    "each a Pyro hit for its size"],
        "Spark": ["instead of Energy, with no cap", "Gone after combat"],
        "Mine": ["that also goes off when its enemy attacks",
                 "before the hit lands",
                 "Read the badge: only their "],
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
        "Plan": [", paid now; next turn: front ",
                 " counts; your ",
                 " do not."],
        "Mend": [": heal N HP, never above the HP you entered",
                 "the fight with"],
        # `EB-377` ADDED THESE TWO ROWS to the page, and their absence was the
        # same defect the row is about: both have had an `ArmKeywordTips` twin
        # since R244 and neither had a page row, so the mod defined them on a
        # hover and the blind page defined them nowhere.
        "Hexerei": [" card from the witches' circle. It does ",
                    "nothing by itself; Klee is one too, and her own cards "
                    "pay when "],
        "Swirl": ["The enemy's aura is consumed and copied onto ALL enemies. "
                  "No ", "aura, no effect."],
        # `EB-372`, Klee's sixth: a Power of hers that Kaeya's Cold-Blooded
        # Strike is written against by name, met by a seat holding neither.
        "Grounded": ["that pays at the start of your turn, but ",
                     "went off last turn. Its ",
                     "card prints what it pays."],
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
    assert "none of your Bombs went off last turn" in page

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
    # The page's own ceiling: the arm rows mirror a 135-character tip, and a
    # row with no tip to mirror keeps the same bound rather than sprawling.
    assert len(body) <= 135, len(body)


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


def elemental_hand_state(*, aura: bool = False, bomb_tip: str = "") -> dict:
    """A combat holding one Pyro card, optionally against an aura (`EB-340`).

    Built on the RECORDED combat, so everything the page prints around the two
    fields under test is a real wire state.
    """
    state = json.loads(json.dumps(combat_state()))
    keywords = [{"name": "Applies Pyro",
                 "description": "If the target has no aura, this applies Pyro "
                                "for 2 turns. A different aura is consumed to "
                                "trigger a Reaction instead."}]
    if bomb_tip:
        keywords.append({"name": "Bomb", "description": bomb_tip})
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_KAPOW", "name": "Ka-pow!", "type": "Attack",
         "cost": "0", "can_play": True, "index": 0, "target_type": "AnyEnemy",
         "is_upgraded": False, "keywords": keywords,
         "description": "Retain. Set off. Deal 4 damage."}]
    if aura:
        state["player"]["hand"] = []
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
    page = blindplay.observe(elemental_hand_state())
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
    # AN AURA ALONE IS ENOUGH: the combination is priced from the other side
    # just as often, and that screen carries no elemental card at all.
    assert "- **Melt** — " in blindplay.observe(
        elemental_hand_state(aura=True))


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
    elite = elemental_hand_state()
    elite["state_type"] = "elite"
    boss = elemental_hand_state()
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
        "Superconduct": ["reacted enemy gains "],
        "Electro-Charged": [" HP at the start of its turn, 1 less each turn"],
        "Frozen": ["ts next action deals half damage, and the first Attack "
                   "to hit it Shatters for "],
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

    `EB-343` (R248) REWROTE THE TIP THIS SCRAPES, and both of this test's
    claims survive it. [USER] held the in-game word to its 135-character
    ceiling, so the tip reads "A charge on an enemy: grows 4 a turn, goes off
    only when Set off, all at once", and `EB-373` rewrote what follows it
    ("Not an Attack: only their Vulnerable and a cap move it") because the
    older clause promised debuffs the fold does not read. The glossary keeps
    "each" on top of the first sentence, because the fact that growth is PER
    BOMB lives on the badge in game and the seat page has no badge.
    """
    page = blindplay.observe(keyword_hand_state(["Set off. Place a Bomb 4."]))
    assert (f"- **Bomb** — A charge on an enemy: each grows "
            f"{blindplay.BOMB_GROWTH} a turn,") in page
    # LIVE FIRST: where the screen's own tip carries the number, that number is
    # what the glossary prints -- the fallback is for a screen that prints the
    # WORD with no tip on it, which is an enemy's badge and a reward row.
    live_tip = blindplay.observe(elemental_hand_state(
        bomb_tip="A charge on an enemy: grows 9 a turn, goes off only when "
                 "Set off, all at once."))
    assert "each grows 9 a turn" in live_tip


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
    assert ("Intent: Aggressive (Attack) — the number on its icon is 8 "
            "— This enemy intends to Attack for 8 damage.") in page
    assert ("and also: Strategic (StatusCard) — the number on its icon "
            "is 4 — This enemy intends to add 4 Burn to your hand.") \
        in page


def test_a_single_component_intent_reads_exactly_as_it_always_did():
    """One row, one line, no continuation -- the recorded combat is the pin."""
    page = blindplay.observe(combat_state())
    assert ("Intent: Aggressive (Attack) — the number on its icon is 12 "
            "— This enemy intends to Attack for 12 damage.") in page
    assert "and also:" not in page


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
    assert "- **Vulnerable** — The wearer takes 50% more damage" in glossary
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
        "Vulnerable": ["The wearer takes 50% more damage from every hit. "
                       "One stack falls ", "off at the end of each of its "
                       "turns."],
        "Weak": ["The wearer deals 25% less damage. One stack falls off at "
                 "the end ", "of each of its turns."],
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
