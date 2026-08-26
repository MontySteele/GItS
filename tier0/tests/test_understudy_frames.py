"""The window-capture leg: off by default, window-only, and never a judgment.

No picture is taken in this file. What is pinned is everything around the
picture -- the refusal, the target, the naming, and the sentence that has to
ride on every row of the manifest -- because those are the parts that would let
a bot's output quietly become a claim about how the game looks.
"""

from __future__ import annotations

import json

import pytest

from understudy import frames, harness


# -------------------------------------------------------- off by default ----

def test_capture_is_off_unless_the_env_variable_says_otherwise():
    assert frames.enabled({}) is False
    assert frames.enabled({"GITS_UNDERSTUDY_CAPTURE": ""}) is False
    assert frames.enabled({"GITS_UNDERSTUDY_CAPTURE": "0"}) is False
    assert frames.enabled({"GITS_UNDERSTUDY_CAPTURE": "1"}) is True


def test_a_disabled_capture_runs_nothing_and_says_which_switch_it_wants():
    """Off must cost nothing: no subprocess, no file, no directory created.
    `GITS_ILSPY_TREE` is the precedent -- a leg whose output is material on
    somebody's disk is env-only and never a default."""
    def _must_not_run(_script, timeout=0):
        raise AssertionError("a disabled capture spawned a process")

    report = frames.capture("x", env={}, runner=_must_not_run)
    assert report["status"] == "disabled"
    assert frames.CAPTURE_ENV in report["message"]


def test_the_disabled_report_still_carries_the_guardrail():
    assert frames.GUARDRAIL in frames.capture("x", env={})["guardrail"]


# ------------------------------------------------------------ the target ----

def test_the_script_targets_a_window_handle_and_never_the_desktop():
    """A whole-screen grab would sweep in whatever else the machine happens to
    be showing. That is somebody's private business and it is not the material
    anybody asked for, so the rectangle comes from the game process's own
    MainWindowHandle or there is no capture."""
    out = frames.Path("C:/out.png")
    script = frames.build_script("SlayTheSpire2", out)
    assert "MainWindowHandle" in script
    assert "GetWindowRect" in script
    assert "PrimaryScreen" not in script
    assert "VirtualScreen" not in script
    assert "SlayTheSpire2" in script and str(out) in script


def test_the_script_is_sent_encoded_and_not_typed_at_a_prompt():
    """`-Command -` feeds a script to the host line by line, so the
    here-string that carries the P/Invoke declaration does not survive: the run
    exits 0 having printed nothing, which is a silent no-op wearing a success.
    A live probe produced exactly that before this was changed."""
    script = frames.build_script("X", frames.Path("C:/o.png"))
    decoded = frames.encoded_command(script)
    import base64
    assert base64.b64decode(decoded).decode("utf-16-le") == script


# ------------------------------------------------------------- the names ----

def test_the_stamp_leads_so_a_directory_listing_is_chronological():
    p = frames.frame_path("salon-stage", stamp="20260812-010203")
    assert p.name == "frame-20260812-010203-salon-stage.png"


def test_a_label_cannot_reach_the_filesystem_or_the_shell():
    p = frames.frame_path("../../etc/pwn; rm -rf", stamp="S")
    assert p.name == "frame-S-etc-pwn--rm--rf.png"
    assert p.parent == frames.FRAME_DIR


def test_an_empty_label_still_produces_a_usable_name():
    assert frames.frame_path("", stamp="S").name == "frame-S-frame.png"


# ------------------------------------------------------------ the reading ----

class _Runner:
    def __init__(self, code, out, err=""):
        self.code, self.out, self.err = code, out, err
        self.scripts = []

    def __call__(self, script, timeout=60.0):
        self.scripts.append(script)
        return self.code, self.out, self.err


def test_a_missing_window_is_a_named_refusal_not_a_stack_trace(tmp_path):
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=_Runner(2, "NO_WINDOW"))
    assert report["status"] == "error"
    assert "not be running" in report["message"] or "must be running" in report["message"]
    assert not (tmp_path / "m.jsonl").exists(), "a failed capture wrote a row"


def test_a_zero_size_window_is_its_own_refusal(tmp_path):
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=_Runner(3, "EMPTY_RECT"))
    assert report["status"] == "error" and "zero-size" in report["message"]


def test_a_minimised_window_is_refused_rather_than_captured(tmp_path):
    """A minimised window keeps its handle and reports a positive w/h -- it is
    just parked at a -32000 origin. Copying that rectangle would grab the
    top-left of the desktop, which is the one capture this leg refuses."""
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=_Runner(4, "MINIMISED"))
    assert report["status"] == "error" and "minimised" in report["message"]
    assert not (tmp_path / "m.jsonl").exists(), "a failed capture wrote a row"
    # and the script really carries the guard the runner is standing in for
    assert "-30000" in frames.build_script("x", tmp_path / "f.png")


def test_the_size_is_read_off_stdout_alone(tmp_path):
    """A non-interactive host writes progress records to STDERR as CLIXML, and
    the first `Add-Type` emits one. Folded into stdout, that blob became the
    `size` on the manifest row."""
    runner = _Runner(0, "OK 1920 1080", err="#< CLIXML <Objs>...</Objs>")
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=runner)
    assert report["status"] == "ok"
    assert report["row"]["size"] == "1920 1080"


def test_a_runner_that_raises_is_a_report_not_an_exception(tmp_path):
    def boom(_script, timeout=60.0):
        raise OSError("powershell is not on this machine")
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, runner=boom)
    assert report["status"] == "error" and "OSError" in report["message"]


# ---------------------------------------------------------- the manifest ----

def test_every_manifest_row_carries_the_guardrail(tmp_path):
    """On EVERY row, not once at the top of the file. A manifest gets read in
    slices and concatenated with other manifests; a guardrail that lives in a
    header survives exactly one copy-paste."""
    manifest = tmp_path / "m.jsonl"
    for i in range(3):
        frames.capture(f"take{i}", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                       out_dir=tmp_path, manifest=manifest, stamp=f"S{i}",
                       runner=_Runner(0, "OK 800 600"))
    rows = [json.loads(l) for l in
            manifest.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 3
    assert all(r["guardrail"] == frames.GUARDRAIL for r in rows)
    assert all("[USER]-only" in r["guardrail"] for r in rows)


def test_the_context_is_copied_from_the_caller_and_never_inferred(tmp_path):
    """This module does not read the wire. A frame labelled with a screen it
    guessed at afterwards is worse than a frame labelled with nothing."""
    manifest = tmp_path / "m.jsonl"
    frames.capture("x", context={"state_type": "monster", "floor": 7},
                   env={"GITS_UNDERSTUDY_CAPTURE": "1"}, out_dir=tmp_path,
                   manifest=manifest, runner=_Runner(0, "OK 800 600"))
    row = json.loads(manifest.read_text(encoding="utf-8").splitlines()[0])
    assert row["context"] == {"state_type": "monster", "floor": 7}


def test_the_guardrail_refuses_the_four_words_it_exists_to_refuse():
    for word in ("look", "legibility", "readability", "fun"):
        assert word in frames.GUARDRAIL
    assert "MATERIAL, not evidence" in frames.GUARDRAIL


# -------------------------------------------------------------- the verb ----

def _args(label="frame", note=""):
    ns = type("A", (), {})()
    ns.label, ns.note = label, note
    return ns


def test_the_verb_refuses_before_it_touches_the_bridge(monkeypatch, capsys):
    """A disabled leg should reach nothing. Asking the wire first would make
    an off switch depend on a running game."""
    monkeypatch.setattr(frames, "enabled", lambda env=None: False)

    def _no(*_a, **_k):
        raise AssertionError("the disabled verb read the bridge")

    monkeypatch.setattr(harness.bridge, "get_state", _no)
    assert harness.cmd_frame(_args()) == 2
    assert frames.CAPTURE_ENV in capsys.readouterr().out


def test_a_captured_frame_is_logged_against_the_run_with_its_guardrail(
        monkeypatch):
    written: list = []
    monkeypatch.setattr(frames, "enabled", lambda env=None: True)
    monkeypatch.setattr(harness, "_session", lambda: {"seed": "SEEDTEST01"})
    monkeypatch.setattr(harness, "append",
                        lambda seed, rec: written.append((seed, rec)))
    monkeypatch.setattr(harness.bridge, "get_state",
                        lambda: {"state_type": "monster",
                                 "run": {"act": 2, "floor": 9}})
    monkeypatch.setattr(
        harness.frames, "capture",
        lambda label, note="", context=None: {
            "status": "ok", "path": "frames/x.png", "guardrail": frames.GUARDRAIL,
            "message": "captured", "row": {}})

    assert harness.cmd_frame(_args("salon-stage", "third take")) == 0
    seed, rec = written[0]
    assert seed == "SEEDTEST01"
    assert rec["event"] == "frame_captured"
    assert rec["context"]["floor"] == 9
    assert rec["guardrail"] == frames.GUARDRAIL


def test_an_unreachable_bridge_records_the_missing_context_as_missing(
        monkeypatch):
    seen: dict = {}
    monkeypatch.setattr(frames, "enabled", lambda env=None: True)
    monkeypatch.setattr(harness, "_session", lambda: {})
    monkeypatch.setattr(harness, "append", lambda seed, rec: None)
    monkeypatch.setattr(
        harness.bridge, "get_state",
        lambda: (_ for _ in ()).throw(harness.bridge.BridgeError("down")))
    monkeypatch.setattr(
        harness.frames, "capture",
        lambda label, note="", context=None: seen.update(context=context) or {
            "status": "ok", "path": "p", "guardrail": "", "message": "",
            "row": {}})
    harness.cmd_frame(_args())
    assert "unreachable" in seen["context"]["bridge"]


# --------------------------------------------------------- where it lives ----

def test_the_frame_directory_is_gitignored():
    """A frame of the running game has Tier F art in it, so committing one
    distributes exactly what principles section 9 refuses to -- the same rule
    `art/g12_captures/` and `art/eb52_captures/` already carry."""
    ignore = frames.FRAME_DIR / ".gitignore"
    assert ignore.exists(), f"{frames.FRAME_DIR} has no .gitignore"
    body = ignore.read_text(encoding="utf-8")
    assert body.splitlines()[-2:] == ["*", "!.gitignore"]


def test_the_soak_cannot_take_pictures():
    """Same fence as `give-card`: the unattended loop does not produce material
    nobody asked for on somebody's disk overnight."""
    from understudy import soak
    assert not hasattr(soak, "frames"), "the soak imported the capture leg"
    src = soak.Path(soak.__file__).read_text(encoding="utf-8")
    assert "frames.capture" not in src


# ------------------------------------------------------------- the route ----
#
# EB-142 hygiene, 2026-08-25. The auto route's blank test cannot catch this
# window's failure mode -- PrintWindow returns a surface that is varied and
# INCOMPLETE (no hand, no enemies, no prompt caption) -- so the route is an
# explicit env choice rather than a smarter heuristic.

def test_the_route_is_env_only_and_defaults_to_auto():
    assert frames.route({}) == frames.ROUTE_AUTO
    assert frames.route({frames.ROUTE_ENV: "copyfromscreen"}) == "copyfromscreen"
    assert frames.route({frames.ROUTE_ENV: "PrintWindow"}) == "printwindow"


def test_an_unknown_route_costs_a_caveat_and_never_the_frame():
    """A typo must not fail a capture, and must never be interpolated into the
    script it would then be a hole in."""
    assert frames.route({frames.ROUTE_ENV: "nonsense"}) == frames.ROUTE_AUTO
    script = frames.build_script("X", frames.Path("C:/o.png"), "nonsense")
    assert "'auto'" in script and "nonsense" not in script


def test_the_forced_screen_route_skips_printwindow_entirely():
    """The partial surface exists because PrintWindow RAN. Pinning the screen
    route has to mean not asking it, not asking it and discarding the answer."""
    script = frames.build_script("X", frames.Path("C:/o.png"), "copyfromscreen")
    assert "$forced = 'copyfromscreen'" in script
    assert "$route = 'copyfromscreen-forced'" in script


def test_the_screen_route_raises_the_game_and_puts_it_back():
    """`CopyFromScreen` photographs whatever is on top, and something always
    is -- the console driving the capture. Both screen-route arms foreground
    the window, and both drop the topmost flag again in a `finally`, so a
    failed grab cannot leave the game pinned over everything the user owns."""
    script = frames.build_script("X", frames.Path("C:/o.png"), "copyfromscreen")
    assert "SwitchToThisWindow" in script
    assert "Set-Foreground $hwnd" in script
    assert "finally { Clear-Foreground $hwnd }" in script
    # HWND_TOPMOST (-1) going up, HWND_NOTOPMOST (-2) coming back down.
    assert "[IntPtr](-1)" in script and "[IntPtr](-2)" in script
    # Z order only: never a move, never a resize.
    assert "0x0013" in script


def test_the_manifest_row_records_the_route_that_ran_and_the_one_asked_for(tmp_path):
    runner = _Runner(0, "OK 1920 1080 copyfromscreen-forced")
    report = frames.capture("x",
                            env={"GITS_UNDERSTUDY_CAPTURE": "1",
                                 frames.ROUTE_ENV: "copyfromscreen"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=runner)
    assert report["status"] == "ok"
    assert report["row"]["route"] == "copyfromscreen-forced"
    assert report["row"]["route_requested"] == "copyfromscreen"
    # The guardrail rides on this row like every other one.
    assert report["row"]["guardrail"] == frames.GUARDRAIL
    assert "copyfromscreen" in runner.scripts[0]


def test_the_guardrail_still_rides_a_forced_route_row(tmp_path):
    """Every row, on every route. A route override is not a way out of it."""
    for env_route, ran in (("copyfromscreen", "copyfromscreen-forced"),
                           ("printwindow", "printwindow-forced")):
        report = frames.capture("x",
                                env={"GITS_UNDERSTUDY_CAPTURE": "1",
                                     frames.ROUTE_ENV: env_route},
                                out_dir=tmp_path,
                                manifest=tmp_path / "m.jsonl",
                                runner=_Runner(0, f"OK 1 1 {ran}"))
        assert report["row"]["guardrail"] == frames.GUARDRAIL


# ------------------------------------------------- the state renderer -------

def test_the_renderer_names_the_character_actually_being_played():
    """It printed "Furina" unconditionally, so every Kokomi and Klee soak
    transcript read "Furina 56/70 HP" beside the right numbers. The wire's own
    `player.character` is the display name and is what `policy_v1._plan_for`
    already resolves the run's plan off."""
    state = {"state_type": "monster", "run": {"act": 1, "floor": 3},
             "player": {"character": "Sangonomiya Kokomi", "hp": 56,
                        "max_hp": 70, "gold": 99, "energy": 3, "hand": []},
             "battle": {"round": 1, "turn": "player"}}
    out = harness.render(state)
    assert "Sangonomiya Kokomi 56/70 HP" in out
    assert "Furina" not in out


def test_a_state_with_no_character_renders_a_neutral_label():
    state = {"state_type": "map", "run": {"act": 1, "floor": 3},
             "player": {"hp": 56, "max_hp": 70, "gold": 99}}
    out = harness.render(state)
    assert "Player 56/70 HP" in out
