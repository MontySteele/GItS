"""The soak harness's judgment, tested without launching a game.

The parts of `understudy/soak.py` that can be wrong in a way that costs a night
are not the HTTP calls -- they are the WATCHDOG (does a stall look like a
stall?), the READINESS rule (R97/5a), the TELEMETRY attribution, and the
REVERSIBILITY ledger. All four are pure functions of dicts, so all four are
tested here and the game is never involved.

What is deliberately NOT tested here: the live loop. A test that mocks the
bridge deeply enough to drive a run would be testing the mock. The live loop
is validated by running it (H4, `docs/sprint-understudy-p1-log-2026-08-04.md`).
"""

import json

from understudy import report, soak


def _combat(hp=50, round_=1, enemies=(("JAW_0", "Jaxfruit", 30, 40),),
            hand=("Strike",), energy=3):
    return {
        "state_type": "monster", "run": {"act": 1, "floor": 3},
        "battle": {"round": round_, "enemies": [
            {"entity_id": e[0], "name": e[1], "hp": e[2], "max_hp": e[3],
             "block": 0, "intents": [{"type": "Attack", "label": "7"}],
             "status": []} for e in enemies]},
        "player": {"hp": hp, "max_hp": 71, "block": 0, "energy": energy,
                   "hand": [{"id": f"X-{n}", "name": n, "cost": 1,
                             "target_type": "Enemy", "can_play": True}
                            for n in hand],
                   "draw_pile": [], "discard_pile": [], "exhaust_pile": []},
    }


# ------------------------------------------------------------- readiness ---

def test_readiness_is_the_options_key_and_never_the_health_endpoint():
    """R97/5a, made structural. The HTTP server answers ~20 s before the main
    menu has buttons; a launcher that trusts `GET /` acts into an empty menu
    and then someone spends an evening diagnosing the game for it."""
    src = (soak.Path(soak.__file__)).read_text(encoding="utf-8")
    body = src.split("def wait_for_menu", 1)[1].split("\n    def ", 1)[0]
    assert '"options"' in body or "options" in body
    assert "health" not in body, "readiness must not consult GET /"
    # And the module must not call it at all outside its own docstring.
    code = "\n".join(line for line in src.splitlines()
                     if not line.strip().startswith("#"))
    assert "bridge.health(" not in code


# -------------------------------------------------------------- watchdog ---

def test_a_repeated_fingerprint_is_a_stall():
    d = _driver()
    state = _combat()
    for _ in range(soak.NO_PROGRESS_ACTIONS - 1):
        d._check(state)
    try:
        d._check(state)
    except soak.Defect as e:
        assert e.kind == "no_progress"
    else:
        raise AssertionError("a frozen state must file a defect")


def test_two_plays_in_a_row_are_not_a_stall():
    """Combat legitimately repeats a screen type -- which is why the
    fingerprint is not just `state_type`. Enemy HP falling is progress."""
    d = _driver()
    for hp in range(30, 30 - soak.NO_PROGRESS_ACTIONS - 2, -1):
        d._check(_combat(enemies=(("JAW_0", "Jaxfruit", hp, 40),)))


def test_an_overlay_is_a_softlock():
    d = _driver()
    try:
        d._check({"state_type": "overlay"})
    except soak.Defect as e:
        assert e.kind == "overlay_softlock"
    else:
        raise AssertionError("state_type 'overlay' must file a defect")


def test_the_harness_side_defect_list_excludes_game_side_failures():
    """A crash or a soft-lock is the soak WORKING. Only instrument failures
    trip the two-of-a-shape stop rule; if `process_died` ever joined this set,
    the soak would halt on the very thing it exists to find."""
    assert "process_died" not in soak._HARNESS_SIDE
    assert "overlay_softlock" not in soak._HARNESS_SIDE
    assert "no_progress" not in soak._HARNESS_SIDE
    assert "bridge_unreachable" in soak._HARNESS_SIDE


# ------------------------------------------------------------- telemetry ---

def test_damage_is_attributed_to_the_card_that_was_named():
    d = _driver()
    before = _combat(enemies=(("JAW_0", "Jaxfruit", 30, 40),))
    after = _combat(enemies=(("JAW_0", "Jaxfruit", 18, 40),))
    d._observe(before, before, {}, {"action": "noop"})     # opens the fight
    d._observe(before, after, {"card_name": "Big Swing"},
               {"action": "play_card", "card_index": 0})
    assert d.fight.damage_by_source["Big Swing"] == 12
    assert ["Big Swing" in c for c in d.fight.cards_played]


def test_hp_loss_is_counted_as_damage_taken():
    d = _driver()
    before = _combat(hp=50)
    d._observe(before, before, {}, {"action": "noop"})
    d._observe(before, _combat(hp=41), {}, {"action": "end_turn"})
    assert d.fight.damage_taken == 9


def test_incoming_is_read_off_the_telegraph_before_block():
    total, n = soak._telegraphed(_combat(
        enemies=(("A", "One", 10, 10), ("B", "Two", 10, 10))))
    assert (total, n) == (14, 2)


def test_a_multi_hit_label_multiplies():
    state = _combat()
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "Attack", "label": "8 x 3"}]
    assert soak._telegraphed(state) == (24, 1)


def test_a_non_attack_intent_contributes_nothing():
    state = _combat()
    state["battle"]["enemies"][0]["intents"] = [
        {"type": "DebuffStrong", "title": "Strategic"}]
    assert soak._telegraphed(state) == (0, 0)


def test_a_fight_closes_when_combat_ends_and_records_its_ledger():
    d = _driver()
    start = _combat(hp=50)
    d._observe(start, start, {}, {"action": "noop"})
    d._observe(start, {"state_type": "rewards", "run": {"act": 1, "floor": 3},
                       "player": {"hp": 44, "max_hp": 71}}, {},
               {"action": "end_turn"})
    assert d.fight is None
    assert len(d.fights) == 1
    rec = d.fights[0].as_record()
    assert rec["hp_start"] == 50 and rec["hp_end"] == 44 and rec["hp_lost"] == 6
    assert rec["outcome"] == "survived"


def test_the_fight_record_carries_every_key_the_readme_documents():
    """The schema is a shared surface to be. A key that silently vanishes
    would take Track B's reader with it."""
    d = _driver()
    s = _combat()
    d._observe(s, s, {}, {"action": "noop"})
    rec = d.fight.as_record()
    for key in ("act", "floor", "kind", "enemies", "hp_start", "hp_end",
                "max_hp", "hp_lost", "turns", "outcome", "hp_trajectory",
                "incoming_by_turn", "cards_played", "n_cards_played",
                "potions_used", "damage_by_source", "damage_dealt",
                "damage_taken"):
        assert key in rec, f"the README documents `{key}` and the record lacks it"


# ------------------------------------------------------- mechanical walk ---

def test_a_decision_screen_is_never_walked_mechanically():
    for st in ("monster", "map", "card_reward", "rest_site", "shop",
               "card_select"):
        assert soak._mechanical_action({"state_type": st}) is None, st


def test_dialogue_and_reward_piles_are_walked():
    assert soak._mechanical_action(
        {"state_type": "event", "event": {"in_dialogue": True}}
    ) == {"action": "advance_dialogue"}
    assert soak._mechanical_action(
        {"state_type": "rewards", "rewards": {"items": [{"name": "gold"}]}}
    ) == {"action": "claim_reward", "index": 0}


def test_the_state_dump_collapses_the_piles_but_keeps_the_screen():
    trimmed = soak._trim_state({
        "state_type": "monster", "battle": {"round": 2},
        "player": {"hp": 5, "draw_pile": [1, 2, 3], "hand": [{"name": "x"}]}})
    assert trimmed["player"]["draw_pile"] == "<3 cards>"
    assert trimmed["player"]["hp"] == 5
    assert trimmed["battle"] == {"round": 2}
    json.dumps(trimmed)                       # a defect record must serialise


# --------------------------------------------------------- reversibility ---

def test_the_ledger_is_written_before_the_change_lands(tmp_path):
    """A ledger written after the change is empty exactly when the process
    dies mid-change, which is the one moment anybody needs it."""
    led = soak.Reversibility(tmp_path / "rev.json")
    led.record("created steam_appid.txt", "delete it")
    on_disk = json.loads((tmp_path / "rev.json").read_text(encoding="utf-8"))
    assert on_disk[0]["state"] == "APPLIED"


def test_reverting_and_failing_are_both_recorded(tmp_path):
    led = soak.Reversibility(tmp_path / "rev.json")
    a = led.record("deployed the bridge", "-Remove")
    b = led.record("set the speed", "enabled:false")
    led.revert(a, "mods/STS2_MCP removed")
    led.fail(b, "bridge unreachable")
    table = led.table()
    assert "**REVERTED**" in table and "**NOT REVERTED**" in table
    assert "bridge unreachable" in table


# -------------------------------------------------------------- reporting --

def test_the_report_leads_with_defects_and_carries_the_guardrail(tmp_path,
                                                                 monkeypatch):
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    stamp = "20260804-000000"
    (tmp_path / f"soak-{stamp}-index.json").write_text(json.dumps({
        "stamp": stamp, "character": "KLEEMOD-FURINA", "policy": "policy_v1",
        "requested_runs": 2, "stopped_on": None,
        "runs": [{"run": 1, "seed": "AAA", "outcome": "died", "final_act": 1,
                  "final_floor": 6, "fights": 3, "actions": 120, "wall_s": 90},
                 {"run": 2, "seed": "BBB", "outcome": "defect", "final_act": 1,
                  "final_floor": 2, "fights": 1, "actions": 30, "wall_s": 20}],
    }), encoding="utf-8")
    (tmp_path / f"soak-{stamp}-run002.jsonl").write_text(json.dumps({
        "record": "defect", "kind": "no_progress", "run": 2, "seed": "BBB",
        "act": 1, "floor": 2, "state_type": "monster",
        "detail": "fingerprint identical across 12 actions"}) + "\n",
        encoding="utf-8")
    out = report.render(stamp)
    assert out.index("## 1. Defects") < out.index("## 2. Runs")
    assert out.index("## 2. Runs") < out.index("## 3. Aggregate")
    assert "BOT-LIMITED FLOOR" in out
    assert "no_progress" in out and "BBB" in out


def test_a_clean_soak_says_so_rather_than_printing_nothing(tmp_path,
                                                           monkeypatch):
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    stamp = "20260804-111111"
    (tmp_path / f"soak-{stamp}-index.json").write_text(json.dumps({
        "stamp": stamp, "character": "KLEEMOD-FURINA", "policy": "policy_v1",
        "requested_runs": 1, "stopped_on": None,
        "runs": [{"run": 1, "seed": "AAA", "outcome": "died", "final_act": 1,
                  "final_floor": 6, "fights": 1, "actions": 40, "wall_s": 30}],
    }), encoding="utf-8")
    out = report.render(stamp)
    assert "None. No crash" in out


def test_the_report_never_prints_a_winrate():
    """There is no winrate here that means anything, and a page that prints
    one invites it to be read. Structural, not a matter of discipline."""
    src = soak.Path(report.__file__).read_text(encoding="utf-8")
    body = src.split('"""', 2)[-1]        # everything past the module docstring
    assert "winrate" not in body.lower()


# ------------------------------------------------------------------ util ---

class _FakeSession:
    def alive(self):
        return True


def _driver():
    d = soak.RunDriver.__new__(soak.RunDriver)
    d.session = _FakeSession()
    d.character = soak.DEFAULT_CHARACTER
    d.memo = soak.policy_v1.Memo()
    d.run_index = 1
    d.stamp = "test"
    d.seed = "TESTSEED"
    d.actions = 0
    d.started = soak.time.time()
    d.fights = []
    d.fight = None
    d.defects = []
    d._fingerprints = []
    d._last_state = None
    d._forced_defaults = 0
    d.log = soak.Path(soak.LOG_DIR) / "unused-in-tests.jsonl"
    d.emit = lambda record: None
    return d


# ---------------------------------------------------------------- embark ---
#
# The first validation soak filed two `embark_loop` defects and halted itself.
# The cause: `menu_select KLEEMOD-FURINA` is idempotent -- the character stays
# in `options` after it is chosen and the bridge answers "Selected Furina. Use
# 'confirm' to embark." every single time -- so a loop that prefers the
# character over the confirm re-selects her forever. That is a real bug this
# harness had, caught by this harness, and it gets a red test.


class _FakeBridge:
    """The character-select screen's actual behaviour, replayed offline."""

    class BridgeError(Exception):
        pass

    def __init__(self):
        self.posted = []
        self.screen = "main"
        self.picked = False

    def get_state(self):
        if self.screen == "embarked":
            return {"state_type": "map", "run": {"act": 1, "floor": 1},
                    "player": {"hp": 60, "max_hp": 60},
                    "map": {"next_options": [{"index": 0, "type": "Monster"}]}}
        opts = {
            "main": ["singleplayer"],
            "singleplayer": ["standard", "back"],
            "character_select": (["KLEEMOD-FURINA", "IRONCLAD"]
                                 + (["confirm"] if self.picked else [])),
        }[self.screen]
        return {"state_type": "menu", "menu_screen": self.screen,
                "options": opts}

    def post(self, action, **params):
        self.posted.append((action, params))
        opt = str(params.get("option", "")).lower()
        if opt == "singleplayer":
            self.screen = "singleplayer"
        elif opt == "standard":
            self.screen = "character_select"
        elif opt == "kleemod-furina":
            self.picked = True          # idempotent, and the screen does NOT move
        elif opt == "confirm":
            self.screen = "embarked"
        return {"status": "ok", "message": "ok"}

    def current_seed(self):
        return "FAKESEED01"


def test_the_embark_path_confirms_instead_of_re_picking_forever(monkeypatch):
    fake = _FakeBridge()
    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)
    d = _driver()
    state = d._embark(fake.get_state())
    assert state["state_type"] == "map", "the driver never left the menu"
    picks = [p for p in fake.posted
             if str(p[1].get("option", "")).lower() == "kleemod-furina"]
    assert len(picks) == 1, f"the character was selected {len(picks)} times"
    assert any(str(p[1].get("option", "")).lower() == "confirm"
               for p in fake.posted), "nothing ever confirmed"


def test_no_seed_is_ever_passed_on_the_embark_path(monkeypatch):
    """R95: read-back, not chosen. A `seed` parameter here returns "Seeded
    embark is not supported for standard singleplayer from this API", and the
    Custom screen that would take one soft-locks the game."""
    fake = _FakeBridge()
    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)
    d = _driver()
    d._embark(fake.get_state())
    assert not any("seed" in params for _, params in fake.posted)


def test_an_in_combat_overlay_does_not_end_the_fight():
    """Furina's starter relic opens `card_select` every single turn. Treating
    that as the end of combat split one floor-2 fight into five records in the
    first validation soak, each with its own turn count and HP ledger."""
    d = _driver()
    fight = _combat(hp=50)
    d._observe(fight, fight, {}, {"action": "noop"})
    d._observe(fight, {"state_type": "card_select", "run": {"act": 1, "floor": 3},
                       "player": {"hp": 50, "max_hp": 71},
                       "card_select": {"screen_type": "choose", "cards": []}},
               {}, {"action": "play_card", "card_index": 0})
    assert d.fight is not None, "the fight ended at an overlay"
    assert d.fights == []


def test_a_reward_screen_does_end_the_fight():
    d = _driver()
    fight = _combat(hp=50)
    d._observe(fight, fight, {}, {"action": "noop"})
    d._observe(fight, {"state_type": "rewards", "run": {"act": 1, "floor": 3},
                       "player": {"hp": 44, "max_hp": 71}}, {},
               {"action": "end_turn"})
    assert d.fight is None and len(d.fights) == 1


# ------------------------------------- the crash that skipped the teardown ---
#
# A soak died when the game vanished mid-request. `bridge.set_speed(False)`
# raised `ConnectionResetError`, which is an OSError and NOT a `BridgeError`,
# so it escaped the first line of `teardown` and the remaining three steps
# never ran -- leaving `steam_appid.txt` and `mods/STS2_MCP` in the game
# directory. Both halves of that get a test.


def test_a_socket_failure_is_a_bridge_error(monkeypatch):
    """Every failure to reach the bridge is a BridgeError, including the ones
    the stdlib does not spell that way."""
    from understudy import bridge as b

    def boom(*a, **k):
        raise ConnectionResetError(10054, "forcibly closed")

    monkeypatch.setattr(b.urllib.request, "urlopen", boom)
    try:
        b.get_state()
    except b.BridgeError as e:
        assert "ConnectionResetError" in str(e)
    else:
        raise AssertionError("a reset socket must surface as BridgeError")


def test_every_teardown_step_runs_even_when_an_earlier_one_raises(tmp_path):
    """A teardown that abandons its own ledger is worse than no teardown."""
    sess = soak.Session.__new__(soak.Session)
    sess.ledger = soak.Reversibility(tmp_path / "rev.json")
    sess.dir = tmp_path
    appid = tmp_path / "steam_appid.txt"
    appid.write_text("2868840", encoding="ascii")

    sess._speed_entry = sess.ledger.record("speed", "enabled:false")
    sess._launch_entry = sess.ledger.record("launch", "terminate")
    sess._bridge_entry = sess.ledger.record("bridge", "-Remove")
    sess._appid_entry = sess.ledger.record("appid", "delete")

    def explode():
        raise ConnectionResetError("the game went away")

    sess._restore_speed = explode
    sess._stop_game = lambda: "process terminated"
    sess._remove_bridge = explode
    sess.teardown()

    states = [e["state"] for e in sess.ledger.entries]
    assert states[0] == "NOT REVERTED"          # speed, honestly recorded
    assert states[1] == "REVERTED"              # and the rest still ran
    assert states[2] == "NOT REVERTED"
    assert states[3] == "REVERTED"
    assert not appid.exists(), "the appid file survived a failing teardown"
    assert "ConnectionResetError" in sess.ledger.table()


def test_an_uncancellable_screen_is_answered_not_cancelled():
    """The bridge rejects `cancel_selection` on a screen reporting
    `can_cancel: false` / `can_skip: false`, so cancelling as a last resort is
    a guaranteed loop -- and it produced one."""
    forced = {"state_type": "card_select",
              "card_select": {"can_cancel": False, "can_skip": False,
                              "can_confirm": False, "cards": [{"name": "x"}]}}
    assert soak._last_resort(forced) == {"action": "select_card", "index": 0}
    skippable = {"state_type": "card_select",
                 "card_select": {"can_cancel": True, "cards": []}}
    assert soak._last_resort(skippable) == {"action": "cancel_selection"}


def test_every_walkable_screen_has_an_exit_verb():
    """A forced action that changes nothing is not mechanical. With a full
    potion belt `claim_reward` returns ok and does nothing, so the walker
    re-claimed the same Fire Potion until the cycle watchdog stopped the run.
    Each of these screens advertises a way out; the walker now knows them."""
    for st in ("rewards", "treasure", "relic_select", "hand_select",
               "crystal_sphere"):
        assert soak._escape({"state_type": st}) is not None, st
    assert soak._escape({"state_type": "monster"}) is None
