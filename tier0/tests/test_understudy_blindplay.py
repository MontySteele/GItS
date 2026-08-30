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
    """SYNTHETIC. `map.next_options`, named by room type (`naming.py:170`)."""
    return {"state_type": "map",
            "run": {"act": 1, "floor": 3},
            "player": {"hp": 40, "max_hp": 70, "gold": 99},
            "map": {"next_options": [
                {"index": 0, "type": "Monster", "col": 1, "row": 4},
                {"index": 1, "type": "Monster", "col": 2, "row": 4},
                {"index": 2, "type": "rest_site", "col": 3, "row": 4}]}}


def shop_state() -> dict:
    """SYNTHETIC. `items` with `name`/`type`/`price` (`naming.py:202`)."""
    return {"state_type": "shop",
            "player": {"hp": 40, "max_hp": 70, "gold": 120},
            "items": [{"name": "Coral Guard", "type": "card", "price": 75},
                      {"name": "Bottled Tide", "type": "relic", "price": 160,
                       "description": "At the start of each combat, gain 3 "
                                      "Block."}]}


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
    """SYNTHETIC. `rewards.items` (`naming.py:218`)."""
    return {"state_type": "rewards",
            "rewards": {"items": [{"name": "Gold", "description": "25 gold"},
                                  {"name": "Card"}]}}


def treasure_state() -> dict:
    """SYNTHETIC. `relics` (`naming.py:212`)."""
    return {"state_type": "treasure",
            "relics": [{"name": "Pearl Diver's Charm",
                        "description": "Start each combat with 1 Charge."}]}


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
    assert "[silent energy icon]" in page
    assert ".png" not in page

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
    assert "Intent: Aggressive, 12" in page
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
        (rewards_state(), 'choose "Gold"',
         {"action": "claim_reward", "index": 0}),
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
        {"command": 'choose "Gold"', "thinking": "take it"},
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
         {"command": 'choose "Gold"', "thinking": "."},
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
        {"command": 'choose "Gold"', "thinking": "take it"},
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
        {"command": 'choose "Gold"', "thinking": "take it"},
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
