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

import ast
import json
import time
from pathlib import Path

import pytest

from tier0 import constants as C
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
    named = _imported(Path(blindplay.__file__))
    banned = {"harness", "policy_v0", "policy_v1", "soak", "scenario",
              "adapter", "naming", "staged_turn", "replay", "embark"}
    assert not [m for m in named
                if m.split(".")[0] in ("tier0", "tier05")], named
    assert not [m for m in named if m.rsplit(".", 1)[-1] in banned], named


def test_soak_never_imports_blindplay():
    """The other direction, and the same rule `scenario.py` lives under: an
    unattended soak may not reach a tool whose whole job is to hand a screen to
    a third party's model."""
    named = _imported(Path(soak.__file__))
    assert not [m for m in named if "blindplay" in m], named


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
    assert not [m for m in _imported(Path(blindplay.__file__))
                if "embark" in m], "blindplay reached the operator side"


def test_embark_expands_a_roster_id_to_a_select_screen_option():
    """EB-117's cheap half: `--character kokomi` must not reach `soak._embark`,
    which compares against the screen's own option strings and would embark on
    whatever was highlighted."""
    assert embark.option_id("kokomi") == "KLEEMOD-KOKOMI"
    assert embark.option_id("KLEEMOD-KOKOMI") == "KLEEMOD-KOKOMI"
    with pytest.raises(embark.EmbarkError):
        embark.option_id("")


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
    teardown that silently keeps a mod in somebody's game directory."""
    slots = [attr for attr, _ in embark._LEDGER_SLOTS]
    for attr in ("_seed_entry", "_speed_entry", "_launch_entry",
                 "_bridge_entry", "_appid_entry"):
        assert attr in slots, attr
    assert len(slots) == len(set(slots))


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
    assert "**Coral Guard** — cost 1, skill, 75 gold" in page
    # `EB-268`: and the card TYPE beside it, which the wire sends as
    # `card_type` and the hand line has always printed.
    assert "**Bottled Tide** — 160 gold" in page
    assert "At the start of each combat, gain 3 Block." in page
    # The card-removal shelf has no model and therefore no title; the wire's
    # own word for it is rendered rather than a label invented here.
    assert "**Card Removal** — 90 gold" in page
    # And a shelf already bought says so rather than offering a refused buy.
    assert "**Fire Potion** — 50 gold (not available)" in page

    res = blindplay.act(shop_state(), 'buy "Coral Guard"')
    assert res["ok"] and res["post"] == {"action": "shop_purchase", "index": 0}
    assert res["printed"] == {"item": "Coral Guard", "price": 75}
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
    assert "**Pocket Fireworks** — cost 1, attack, 25 gold" in page
    assert "**Mine Toss** — cost 1, skill, 51 gold" in page
    # `EB-286` reaches the shelves too: a Spark-priced card charges no energy,
    # so its shelf would otherwise have printed a price of nothing at all.
    assert "**Powder Charge** — cost 1 Spark, skill, 77 gold" in page
    # A relic and a potion have no card cost and read exactly as before.
    assert "**Bag of Preparation** — 192 gold" in page


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
    assert "**(this shelf is empty)** — 76 gold (not available)" in page
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
    assert "**Perfect Timing** — cost 1, attack, 76 gold" in before

    after = blindplay.observe(live("shop-bought"))
    assert "**Perfect Timing** — cost 1, attack, 76 gold (sold)" in after
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
    assert "**(this shelf is empty)** — 76 gold" in blindplay.observe(
        live("shop-bought"))


def test_a_spent_live_rest_site_offers_only_proceed():
    """`EB-263`'s acceptance, on the shape the wire actually sends: a spent
    rest site is `{"options": [], "can_proceed": true}`. The page used to
    print no options while still advertising four verbs."""
    assert live("rest-spent")["rest_site"] == {"options": [],
                                               "can_proceed": True}
    page = blindplay.observe(live("rest-spent"))
    assert "nothing left to offer" in page
    assert page.count("- `") == 1 and "- `proceed`" in page


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
    """`EB-263`'s picker half where the wire has NO answer, and it is the
    vendored bridge's gap rather than ours.

    `BuildCardSelectState` reads every grid row through `BuildCardInfo`, which
    carries no selected flag, and `NDeckEnchantSelectScreen` opens no preview
    container -- so the two live captures below differ in ONE field. The r3
    Opus seat: "the whole list reprinted byte-identically; the only change
    anywhere on the screen was the footer going from `Confirm is not
    available.` to `Confirm is available.`"
    """
    before, after = live("enchant-fresh"), live("enchant-chosen")
    assert before["card_select"]["cards"] == after["card_select"]["cards"]
    assert before["card_select"]["can_confirm"] is False
    assert after["card_select"]["can_confirm"] is True
    assert "preview_cards" not in after["card_select"]

    page = blindplay.observe(after)
    assert "This screen's data feed carries no per-card selection state" in page
    assert "Confirm is available." in page
    assert "## What you have picked" not in page

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
    "queue": [{"name": "Kurage's Oath (proto)", "clauses": 1},
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
    assert "1. **Kurage's Oath (proto)**" in page
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
    and still says so."""
    assert blindplay.act(map_state(), "end turn")["refusal"] \
        == "you are not in a battle"


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
    assert "**Perfect Timing** — cost 1, attack, 76 gold" in stocked
    assert "**Mine Toss** — cost 1, skill, 51 gold" in stocked
    assert "**Grounded** — cost 1, power, 74 gold" in stocked
    # A relic and a potion have no card type and read exactly as before.
    assert "**Bag of Preparation** — 192 gold" in stocked
    assert "**Flex Potion** — 48 gold" in stocked

    sold = blindplay.observe(live("shop-bought"))
    assert "**Perfect Timing** — cost 1, attack, 76 gold (sold)" in sold


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
    assert "does not report a card's enchantment" in page


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
    assert "before the rest of the card" in page


def test_a_keyword_no_face_on_the_screen_prints_is_never_defined():
    """A glossary that defined every word the arms own would teach a reader
    rules this board does not have."""
    page = blindplay.observe(keyword_hand_state(["Gain 5 Block."]))
    assert "## Words on this screen" not in page


def test_a_dead_arms_keyword_is_not_in_the_table():
    """R240/R241 replaced the Tide with the Plan. `Tide`, `Surge` and `Exert`
    left with the rules they named, and a page that still defined them would be
    a page teaching a retired rule."""
    for dead in ("Tide", "Surge", "Exert"):
        assert dead not in blindplay.ARM_KEYWORDS
    page = blindplay.observe(keyword_hand_state(["Exert 3. Gain 5 Block."]))
    assert "## Words on this screen" not in page


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
    assert "## Words on this screen" not in page


def test_the_arm_keyword_glossary_is_the_mods_own_tooltip_text():
    """The table is the mod's OWN tooltip bodies with the markup and the
    interpolated constants folded out, and it is held in step FROM THIS SIDE --
    the same discipline `CHARGE_SOURCE_LINE` is under. A sentence rewritten in
    `ArmKeywordTips.cs` and not here goes red on the anchor it dropped."""
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    anchors = {
        "Bomb": ["A numbered charge on an enemy", "goes off by itself",
                 "joins it there", "pops them all"],
        "Set off": ["on the target goes off, one at a time",
                    "before the rest of the card"],
        "Spark": ["instead of energy. No cap;", "gone at the end of combat"],
        "Mine": ["that also goes off when its enemy attacks",
                 "before the hit lands",
                 "the enemy's badge prints the number"],
        "Plan": ["The cost is paid now either way",
                 "land on the front enemy unless the line says every enemy",
                 "the jellyfish, and says so"],
        "Mend": [": heal N HP, never above the HP you entered",
                 "the fight with"],
    }
    assert set(anchors) == set(blindplay.ARM_KEYWORDS)
    for key in ("BombKey", "SetOffKey", "SparkKey", "MineKey", "MendKey",
                "PlanKey"):
        assert f"public const string {key}" in src
    for word, phrases in anchors.items():
        for phrase in phrases:
            assert phrase in src, (word, phrase)
            assert phrase in blindplay.ARM_KEYWORDS[word], (word, phrase)


def test_the_glossary_carries_no_markup_and_no_id():
    """It is rendered through the same blindness assertion as everything else,
    and the sentences are copied from C# that spells them with `[gold]` tags."""
    for word, body in blindplay.ARM_KEYWORDS.items():
        assert "[" not in body and "]" not in body, word
        assert not qa_packet.leaks(body), word


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
