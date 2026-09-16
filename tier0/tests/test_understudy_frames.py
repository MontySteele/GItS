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
    from tier0.tests.conftest import seam_source
    from understudy import soak
    assert not hasattr(soak, "frames"), "the soak imported the capture leg"
    # The FAMILY, not the facade: `EB-180` moved the driver next door.
    assert "frames.capture" not in seam_source("soak")


# ------------------------------------------------------------- the route ----
#
# EB-142, 2026-08-25, and what EB-788 found it had actually been looking at.
# The symptom EB-142 named was real -- PrintWindow returned a surface with no
# hand, no enemies and no prompt caption -- but its diagnosis, a Godot/Vulkan
# window that renders only some of its layers, was WRONG. The window renders
# every layer. It renders them at 1.5x its own client rectangle, and a
# client-sized bitmap clips the overflow, which on a 16:9 screen is exactly the
# bottom (the hand) and the right (the enemies). Measured on lane 1,
# 2026-09-16: a 3841x2160 client, a 5762x3240 render. The escape hatch EB-142
# added is kept -- an env-chosen route is still the honest answer to a route
# question -- but the default no longer needs it.

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


# ------------------------------------ EB-788: the whole client area, or not --
#
# THE CHECK A FRAME IS VERIFIED BY, and it is arithmetic on two pairs of
# integers so that the suite can run it on a machine with no game and no
# display. What it pins is the sentence this defect cost: a frame that is the
# size the manifest claims, is not blank, and is two thirds of a picture.


def test_a_render_that_covers_the_client_area_is_complete():
    g = frames.capture_geometry((3841, 2160), (5762, 3240))
    assert g["complete"] is True
    assert g["scale"] == (1.5001, 1.5)


def test_a_one_to_one_render_is_complete_and_scales_at_one():
    g = frames.capture_geometry((1920, 1080), (1920, 1080))
    assert g["complete"] is True and g["scale"] == (1.0, 1.0)


def test_a_render_that_stopped_short_of_the_client_area_is_a_crop():
    """`live-looks-8c`'s frames, in the shape the apparatus could not see. The
    bitmap was 3841x2160 and so was the client rect, so SIZE agreed with
    itself the whole time -- what disagreed was how far the window had drawn."""
    g = frames.capture_geometry((3841, 2160), (3841, 1440))
    assert g["complete"] is False
    assert "CROP" in g["note"] and "3841x1440" in g["note"]


def test_a_capture_that_reported_no_extent_is_not_called_complete():
    """Silence is not a pass. An old script, or a route that cannot measure,
    leaves the question open and the row says so rather than claiming a yes."""
    for drawn in (None, (0, 0), (5762, 0)):
        assert frames.capture_geometry((3841, 2160), drawn)["complete"] is False
    assert frames.capture_geometry(None, (10, 10))["complete"] is False
    assert frames.capture_geometry((0, 0), (10, 10))["complete"] is False


def test_the_manifest_row_carries_the_client_size_and_the_measured_scale(
        tmp_path):
    runner = _Runner(0, "OK 3841 2160 printwindow 5762 3240")
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=runner)
    row = json.loads((tmp_path / "m.jsonl").read_text(
        encoding="utf-8").splitlines()[0])
    # The size the image was written at IS the client size -- that is the
    # acceptance, and it is on the row rather than in somebody's memory.
    assert row["size"] == "3841 2160" == row["client_size"]
    assert row["render_extent"] == "5762 3240"
    assert row["render_scale"] == [1.5001, 1.5]
    assert row["complete"] is True
    assert report["complete"] is True


def test_an_incomplete_frame_says_so_in_the_report_and_on_the_row(tmp_path):
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=_Runner(0, "OK 3841 2160 printwindow 2560 1440"))
    assert report["status"] == "ok", "an incomplete frame is still a frame"
    assert "INCOMPLETE" in report["message"]
    row = json.loads((tmp_path / "m.jsonl").read_text(
        encoding="utf-8").splitlines()[0])
    assert row["complete"] is False


def test_an_old_success_line_without_an_extent_still_reads_back(tmp_path):
    """Manifests are concatenated across months. A row the old script wrote
    must not turn into a crash in the reader that replaced it."""
    report = frames.capture("x", env={"GITS_UNDERSTUDY_CAPTURE": "1"},
                            out_dir=tmp_path, manifest=tmp_path / "m.jsonl",
                            runner=_Runner(0, "OK 1920 1080 printwindow"))
    assert report["status"] == "ok" and report["complete"] is False
    assert report["row"]["render_extent"] is None


def test_the_script_measures_the_render_instead_of_assuming_a_factor():
    """A factor this apparatus guessed would be a factor that is wrong on the
    next monitor, and a wrong guess here looks exactly like a right one. So the
    canvas is oversized, pre-filled with a sentinel, and the extent is read
    back off the pixels."""
    script = frames.build_script("X", frames.Path("C:/o.png"))
    assert "Measure-Extent" in script
    assert "255, 0, 255" in script          # the sentinel fill
    assert "GetClientRect" in script        # what the frame is OF
    assert "SetResolution(96, 96)" in script
    # and nothing anywhere multiplies by a hard-coded 1.5
    assert "1.5" not in script


def test_the_probe_factor_is_floored_at_one_and_never_interpolated_raw():
    """It reaches the script as a number, through `float()` and a floor: a
    canvas smaller than the client area would clip before it measured."""
    assert "2.0000" in frames.build_script("X", frames.Path("C:/o.png"))
    assert "1.0000" in frames.build_script("X", frames.Path("C:/o.png"),
                                           probe=0.25)


def test_a_render_that_filled_the_probe_canvas_is_reported_not_guessed():
    """If the overflow overflowed the canvas too, the measurement is a floor
    and not the answer, and the route name says which."""
    script = frames.build_script("X", frames.Path("C:/o.png"))
    assert "printwindow-overflow" in script


# --------------------------------------- EB-788: the length of the script ----

def test_whole_line_comments_are_dropped_on_the_way_to_the_wire():
    """`-EncodedCommand` is base64 of UTF-16LE: every character of prose costs
    four on a command line Windows caps near 32767. Adding EB-788's
    explanation to the script pushed the encoded form to 34524 characters and
    the capture died with `WinError 206` -- a length limit wearing the costume
    of a missing file."""
    src = 'Write-Output 1\n  # a comment\n$x = "a # b"   # trailing\n'
    out = frames.strip_ps_comments(src)
    assert "# a comment" not in out
    assert '$x = "a # b"   # trailing' in out, "a mid-line # is not a comment"
    assert "Write-Output 1" in out


def test_the_csharp_here_string_survives_stripping_untouched():
    """What is inside `@" ... "@` is not PowerShell and its comment syntax is
    not `#`. A stripper that walked into it would eat a preprocessor line or a
    string and the P/Invoke block would stop compiling."""
    src = '$t = @"\n#define X 1\n// kept\n"@\n# gone\n'
    out = frames.strip_ps_comments(src)
    assert "#define X 1" in out and "// kept" in out
    assert "# gone" not in out


def test_the_encoded_command_fits_on_a_windows_command_line():
    """The live failure, pinned as a number. 32767 is the cap; the script is
    checked with room for the flags that precede it."""
    script = frames.build_script("SlayTheSpire2",
                                 frames.Path("C:/understudy/logs/frames/f.png"))
    assert len(frames.encoded_command(script)) < 30000


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
