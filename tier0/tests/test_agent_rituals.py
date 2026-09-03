"""The seven ritual scripts: their decisions, on fixtures, touching nothing live.

`docs/current/operations/agent-rituals.md` is the page; these are its gates.
Every test here is a DRY RUN, a pure function, or a hermetic temp repository.
Nothing in this file launches the game, deploys a package, calls GitHub, or
creates a worktree in the real tree — the whole point of the scripts is that
their expensive half is a decision, and a decision is testable.

The shape follows `test_purge_worktree_guard.py`: a test for a tool whose
mistakes are destructive must not itself be capable of the destruction.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools"

GIT_ID = ["-c", "user.name=Test", "-c", "user.email=test@example.invalid"]


def _module(name: str, where: Path = TOOLS):
    """Load one tool by path. `tools/` is a namespace package and these
    scripts are run as `python tools/x.py`, so a path load is the honest
    import."""
    path = where / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_ritual_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _run(argv: list[str], cwd: Path = REPO) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    return subprocess.run([sys.executable, *argv], capture_output=True,
                          text=True, cwd=str(cwd), env=env, errors="replace")


SCRIPTS = ("gates", "row", "mint_row", "agent_worktree", "open_pr", "land_pr",
           "seat", "deploy_round")


# --- the contract every one of them owes ----------------------------------

@pytest.mark.parametrize("name", SCRIPTS)
def test_every_ritual_takes_help_and_a_one_line_mode(name):
    """`--help` and `--oneline` are the two switches the page promises.

    `--oneline` is not decoration: it is what makes a ritual quotable in a
    report without pasting its output, which is the thing this whole set of
    scripts exists to stop.
    """
    res = _run([f"tools/{name}.py", "--help"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "--oneline" in res.stdout, res.stdout


@pytest.mark.parametrize("name", SCRIPTS)
def test_every_ritual_has_a_docstring_naming_the_ritual_it_replaces(name):
    text = (TOOLS / f"{name}.py").read_text(encoding="utf-8")
    assert text.startswith('#!/usr/bin/env python3\n"""'), name
    head = text.split('"""')[1]
    assert len(head) > 400, f"{name}: a ritual script owes its reader the WHY"


# --- gates.py: the summariser, on real output shapes ----------------------

def test_gates_summarises_a_pytest_run_and_names_only_the_failures():
    gates = _module("gates")
    green = "....\n4940 passed, 47 skipped, 12 xfailed, 48 warnings in 58.39s"
    summary, failures = gates.summarise(gates.Gate("pytest", []), green, 0)
    assert summary == "4940 passed, 47 skipped, 12 xfailed"
    assert failures == []

    red = ("FAILED tier0/tests/test_x.py::test_one - AssertionError: boom\n"
           "FAILED tier0/tests/test_y.py::test_two - ValueError\n"
           "2 failed, 4938 passed in 60.0s")
    summary, failures = gates.summarise(gates.Gate("pytest", []), red, 1)
    assert summary == "4938 passed, 2 failed"
    assert failures == ["tier0/tests/test_x.py::test_one",
                        "tier0/tests/test_y.py::test_two"]


def test_gates_summarises_the_lint_battery_both_ways():
    gates = _module("gates")
    ok = "run_lints: 35 tool(s)\n\nOK: 35 lint(s) passed\n"
    assert gates.summarise(gates.Gate("lints", []), ok, 0) == ("35 passed", [])
    bad = "FAILED: register-ids, register-shape\n"
    summary, names = gates.summarise(gates.Gate("lints", []), bad, 1)
    assert summary == "2 FAILED"
    assert names == ["register-ids", "register-shape"]


def test_gates_default_lane_is_fast_and_says_so(tmp_path):
    """A green `--fast` line must never read as a pre-push gate."""
    res = _run(["tools/gates.py", "--only", "lints",
                "--log-dir", str(tmp_path)])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "--fast" in res.stdout and "did NOT run" in res.stdout
    logs = list(tmp_path.glob("gates-*.log"))
    assert len(logs) == 1, logs
    assert "run_lints" in logs[0].read_text(encoding="utf-8")
    assert logs[0].name in res.stdout.replace("\\", "/").split("/")[-1] or \
        str(logs[0]) in res.stdout or logs[0].name in res.stdout


def test_gates_optional_lanes_are_off_by_default():
    gates = _module("gates")

    class Args:
        fast, full, serial, dotnet, codegen, only = True, False, False, False, False, set()

    names = [g.name for g in gates.gates(Args())]
    assert names == ["lints", "pytest", "dotnet-test"]
    Args.dotnet = Args.codegen = True
    assert [g.name for g in gates.gates(Args())] == [
        "lints", "pytest", "codegen-roster", "codegen-prototype",
        "dotnet-build", "dotnet-test"]


def test_the_csharp_suite_is_in_both_lanes_with_the_prototype_switch():
    """The mod's C# suite is a GATE, and it is the LOCAL one.

    KleeTests references four assemblies out of a Steam install, so no GitHub
    runner can hold this check -- which is how two pins stayed red on main for
    days with CI green. It is therefore not optional here, it runs in `--fast`
    as well as `--full`, and it carries `-p:PrototypeCards=true`: without the
    property the whole `Prototype/` tree is `Compile Remove`d and the arms
    every live workstream builds against are pinned by nothing.
    """
    gates = _module("gates")

    class Args:
        fast, full, serial, dotnet, codegen, only = True, False, False, False, False, set()

    for lane in (True, False):
        Args.fast, Args.full = lane, not lane
        picked = [g for g in gates.gates(Args()) if g.name == "dotnet-test"]
        assert len(picked) == 1, f"fast={lane}: the C# suite is not in the lane"
        assert picked[0].optional == ""
        assert "-p:PrototypeCards=true" in picked[0].argv

    # And it says which gate it is, on its own line, green or red.
    out = ("Passed!  - Failed:     0, Passed:   563, Skipped:     0, "
           "Total:   563, Duration: 2 s")
    summary, _ = gates.summarise(gates.Gate("dotnet-test", []), out, 0)
    assert summary.startswith("563 passed, 0 failed, 0 skipped")
    assert "local-only" in summary


def test_a_machine_without_the_game_skips_the_csharp_gate_rather_than_passing(
        tmp_path, monkeypatch):
    """A skip is a skip, and it is not a block.

    A checkout with no `local.props` cannot resolve `sts2.dll`, so the gate has
    nothing to run against. Refusing that machine's pushes over a check it
    structurally cannot run is the fastest way to get the gate turned off; the
    honest answer is a SKIP carrying its reason, which `Result.ok` treats as
    passing and the summary line still names.
    """
    gates = _module("gates")
    monkeypatch.setattr(gates, "dotnet_unavailable",
                        lambda: "no local.props -- no game assemblies")
    gate = [g for g in gates.gates(_FastArgs()) if g.name == "dotnet-test"][0]
    res = gates.run(gate, tmp_path / "log.txt")
    assert res.skipped and res.ok and res.code == 0
    assert "skipped" in res.summary and "local.props" in res.summary


class _FastArgs:
    fast, full, serial, dotnet, codegen, only = True, False, False, False, False, set()


# --- row.py and mint_row.py ------------------------------------------------

def test_row_prints_one_row_and_finds_its_register():
    """Against a live id, chosen from the register rather than hard-coded --
    a row closes and leaves HEAD, and this test must not close with it."""
    register_io = _module("register_io")
    cid = sorted(register_io.defined_ids("BACKLOG"))[0]
    res = _run(["tools/row.py", cid, "--oneline"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert cid in res.stdout and "BACKLOG.md:" in res.stdout


def test_row_exits_1_on_an_id_that_defines_nothing():
    res = _run(["tools/row.py", "EB-99999"])
    assert res.returncode == 1
    assert "no row" in res.stdout


def test_mint_row_derives_the_next_id_above_the_ceiling_and_writes_nothing():
    lint = _module("lint_register_ids")
    register_io = _module("register_io")
    series, number = register_io.next_free("BACKLOG")
    assert series == "EB"
    ceiling, _ = lint.derive(lint._committed())
    assert number == ceiling["EB"] + 1

    res = _run(["tools/mint_row.py", "BACKLOG", "tools", "--scope", "s.",
                "--next-action", "n.", "--gate", "none.",
                "--acceptance", "a.", "--oneline"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert f"EB-{number}" in res.stdout and "dry run" in res.stdout
    # and the register is untouched
    assert register_io.next_free("BACKLOG") == (series, number)


def test_mint_row_refuses_a_backlog_row_missing_one_of_the_four_fields():
    res = _run(["tools/mint_row.py", "BACKLOG", "tools", "--scope", "s.",
                "--gate", "none.", "--acceptance", "a."])
    assert res.returncode != 0
    assert "--next-action" in (res.stdout + res.stderr)


def test_mint_row_counts_the_row_against_the_shape_lint_s_own_limit():
    mint = _module("mint_row")
    shape = _module("lint_register_shape")
    assert mint._shape_limits() == {"BACKLOG": shape.BACKLOG_MAX,
                                    "QUEUE": shape.QUEUE_MAX}
    res = _run(["tools/mint_row.py", "BACKLOG", "tools", "--scope",
                "x" * 700, "--next-action", "n.", "--gate", "none.",
                "--acceptance", "a."])
    assert res.returncode == 1
    assert "TOO LONG" in res.stdout


def test_register_io_finds_a_table_by_prefix_and_refuses_an_ambiguous_one():
    register_io = _module("register_io")
    text = register_io.read("BACKLOG")
    assert register_io.find_table(text, "tools").section.startswith("tools")
    with pytest.raises(KeyError):
        register_io.find_table(text, "no such section")


# --- agent_worktree.py -----------------------------------------------------

def test_agent_worktree_dry_run_creates_nothing():
    # `--allow-live-lane` because the claim under test is about the DRY RUN and
    # the live-lane refusal is about the MACHINE: this checkout's seat lanes
    # come and go while other work runs, so without the switch the test passes
    # or fails on whether a game happens to be up -- and it failed for exactly
    # that reason in the pre-push gate on 2026-09-02, blocking every push from
    # a checkout with a seat in it. The switch weakens nothing here: a dry run
    # creates no worktree, so there is no second checkout to own the profile,
    # and the refusal keeps its own coverage below.
    res = _run(["tools/agent_worktree.py", "pytest-should-not-exist",
                "--task", "build", "--dry-run", "--allow-live-lane"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert not (REPO.parent / "GItS-pytest-should-not-exist").exists()
    assert "would create" in res.stdout


def test_agent_worktree_read_lists_are_real_files_or_named_shapes():
    """Every entry either names a path that exists, or is a described shape
    ('the ONE yaml sheet the task touches'). A read list pointing at a file
    that moved is worse than no read list."""
    aw = _module("agent_worktree")
    for task in aw.READ_LISTS:
        for entry in aw.read_list(task):
            candidate = entry.split(" -- ")[0].split(" and ")[0].strip()
            if candidate.endswith(".md"):
                assert (REPO / candidate).exists(), (task, candidate)


def test_agent_worktree_sees_a_live_lane_only_with_both_halves(tmp_path):
    """A sidecar alone is not a live lane, and neither is an open port."""
    aw = _module("agent_worktree")
    logs = tmp_path / "understudy" / "logs"
    logs.mkdir(parents=True)
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps([{"state": "APPLIED"}]), encoding="utf-8")
    (logs / "embark-1.json").write_text(
        json.dumps({"ledger": str(ledger), "instance": "lane1",
                    "port": 1}), encoding="utf-8")
    # port 1 answers nowhere: the sidecar alone must not fire.
    assert aw.live_lanes(tmp_path) == []

    ledger.write_text(json.dumps([{"state": "REVERTED"}]), encoding="utf-8")
    assert aw.live_lanes(tmp_path) == []


# --- open_pr.py ------------------------------------------------------------

def test_open_pr_appends_the_footer_once_and_only_once():
    open_pr = _module("open_pr")
    body = open_pr.with_footer("A body.", "https://example.invalid/s")
    assert body.count(open_pr.ROBOT) == 1
    assert body.rstrip().endswith("https://example.invalid/s")
    assert open_pr.with_footer(body, "https://example.invalid/s") == body


def test_open_pr_omits_the_session_line_rather_than_inventing_one():
    open_pr = _module("open_pr")
    body = open_pr.with_footer("A body.", "")
    assert open_pr.ROBOT in body
    assert "session" not in body


def test_open_pr_dry_run_calls_no_gh(tmp_path):
    body = tmp_path / "body.md"
    body.write_text("The change.\n", encoding="utf-8")
    res = _run(["tools/open_pr.py", "--title", "t", "--body-file", str(body),
                "--dry-run"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "Generated with" in res.stdout
    assert body.read_text(encoding="utf-8") == "The change.\n"


# --- land_pr.py: the untracked-file trap, in a hermetic repository ---------

def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    (root / "kept.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", *GIT_ID, "add", "kept.txt"], cwd=root, check=True)
    subprocess.run(["git", *GIT_ID, "commit", "-qm", "base"], cwd=root,
                   check=True)
    return root


def test_land_pr_separates_identical_untracked_files_from_differing_ones(
        tmp_path):
    land = _module("land_pr")
    root = _repo(tmp_path)
    # A branch that commits two new files, pushed to a fake `origin`.
    subprocess.run(["git", *GIT_ID, "checkout", "-qb", "feature"], cwd=root,
                   check=True)
    (root / "same.txt").write_text("identical\n", encoding="utf-8")
    (root / "different.txt").write_text("theirs\n", encoding="utf-8")
    subprocess.run(["git", *GIT_ID, "add", "same.txt", "different.txt"],
                   cwd=root, check=True)
    subprocess.run(["git", *GIT_ID, "commit", "-qm", "two files"], cwd=root,
                   check=True)
    subprocess.run(["git", *GIT_ID, "branch", "-f", "origin/feature",
                    "feature"], cwd=root, check=True)
    subprocess.run(["git", *GIT_ID, "checkout", "-q", "main"], cwd=root,
                   check=True)
    # ... and the main checkout has both sitting UNTRACKED, one byte-identical.
    (root / "same.txt").write_text("identical\n", encoding="utf-8")
    (root / "different.txt").write_text("MINE\n", encoding="utf-8")

    same, different = land.blocking_untracked("feature", root)
    assert same == ["same.txt"]
    assert different == ["different.txt"]


def test_land_pr_ignores_untracked_files_the_merge_would_not_touch(tmp_path):
    land = _module("land_pr")
    root = _repo(tmp_path)
    subprocess.run(["git", *GIT_ID, "branch", "origin/main"], cwd=root,
                   check=True)
    (root / "scratch.log").write_text("mine\n", encoding="utf-8")
    assert land.blocking_untracked("main", root) == ([], [])


def test_land_pr_knows_the_main_checkout_from_a_worktree():
    land = _module("land_pr")
    primary = land.main_checkout()
    assert (primary / ".git").exists()
    assert (primary / "CLAUDE.md").exists()


# --- seat.py ---------------------------------------------------------------

def test_seat_sets_the_lane_and_the_token_ceiling_for_the_local_backend():
    seat = _module("seat")

    class Args:
        lane, character, backend, model, session_id = 2, "KLEEMOD-KLEE", "local", "", ""
        max_actions, max_wall_s = 70, 5400.0
        local_url, play_tokens = "http://localhost:8010/v1", "12000"

    labels = [label for label, _, _ in seat.commands(Args())]
    assert labels == ["embark", "session", "teardown"]
    _, session_argv, session_env = seat.commands(Args())[1]
    assert session_env["GITS_LANE"] == "2"
    assert session_env["GITS_LOCAL_PLAY_TOKENS"] == "12000"
    assert session_env[seat.LOCAL_URL_ENV]
    assert "--backend" in session_argv and "local" in session_argv
    assert "--lane" in seat.commands(Args())[0][1]
    assert "--teardown" in seat.commands(Args())[2][1]


def test_seat_leaves_the_local_env_off_the_codex_backend():
    seat = _module("seat")

    class Args:
        lane, character, backend, model, session_id = 1, "X", "codex", "", ""
        max_actions, max_wall_s = 60, 3600.0
        local_url, play_tokens = "u", "12000"

    _, _, env = seat.commands(Args())[1]
    assert env == {"GITS_LANE": "1"}


def test_seat_refuses_lane_0_without_the_door():
    res = _run(["tools/seat.py", "--lane", "0", "--dry-run"])
    assert res.returncode == 2
    assert "machine's own game" in res.stdout


def test_seat_opus_brief_is_the_committed_page_with_the_lane_filled_in():
    res = _run(["tools/seat.py", "--opus-brief", "--lane", "2",
                "--character", "KLEEMOD-KLEE"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "GITS_LANE=2 python -m understudy.blindplay observe" in res.stdout
    assert "<LANE>" not in res.stdout
    assert "Non-blindness declaration" in res.stdout
    assert "KLEEMOD-KLEE" in res.stdout


def test_the_seat_brief_page_exists_and_names_both_allowed_commands():
    page = REPO / "docs" / "current" / "operations" / "seat-brief.md"
    text = page.read_text(encoding="utf-8")
    assert "blindplay observe" in text and "blindplay act" in text
    assert "## THE BRIEF" in text


# --- deploy_round.py -------------------------------------------------------

def _fake_tree(tmp_path: Path, pck_newer: bool) -> Path:
    root = tmp_path / "tree"
    (root / "klee-mod" / "assets").mkdir(parents=True)
    (root / "klee-mod" / "pck-src").mkdir(parents=True)
    (root / "ImageGen" / "images").mkdir(parents=True)
    (root / "ImageGen" / "images" / "a.png").write_bytes(b"x")
    (root / "klee-mod" / "pck-src" / "a.tscn").write_text("s", encoding="utf-8")
    pck = root / "klee-mod" / "assets" / "klee.pck"
    pck.write_bytes(b"p")
    when = time.time() + (600 if pck_newer else -600)
    os.utime(pck, (when, when))
    return root


def test_deploy_round_rebuilds_the_pck_when_a_source_tree_is_newer(tmp_path):
    deploy = _module("deploy_round")
    rebuild, why = deploy.pck_decision(_fake_tree(tmp_path / "a", False))
    assert rebuild and "changed since" in why
    rebuild, why = deploy.pck_decision(_fake_tree(tmp_path / "b", True))
    assert not rebuild and "newer than both" in why


def test_deploy_round_rebuilds_when_there_is_no_pck_at_all(tmp_path):
    deploy = _module("deploy_round")
    root = _fake_tree(tmp_path / "c", True)
    (root / "klee-mod" / "assets" / "klee.pck").unlink()
    rebuild, why = deploy.pck_decision(root)
    assert rebuild and "does not exist" in why


def test_deploy_round_maps_the_arms_to_the_scripts_own_switches():
    deploy = _module("deploy_round")
    script = (REPO / "klee-mod" / "build" / "deploy_proto.ps1").read_text(
        encoding="utf-8")
    for arm, switch in deploy.ARMS.items():
        assert f"[switch]${switch[1:]}" in script, (arm, switch)


def test_deploy_round_refuses_from_a_worktree_or_names_the_main_checkout():
    deploy = _module("deploy_round")
    res = _run(["tools/deploy_round.py", "--arms", "klee", "--dry-run"])
    if deploy.is_main_checkout(REPO):
        assert res.returncode == 0, res.stdout + res.stderr
        assert "pck:" in res.stdout and "would run" in res.stdout
    else:
        assert res.returncode == 2
        assert "not the main checkout" in res.stdout


def test_deploy_round_refuses_an_unknown_arm():
    res = _run(["tools/deploy_round.py", "--arms", "nosuch", "--dry-run"])
    assert res.returncode == 2
    assert "unknown arm" in res.stdout


# --- the hook --------------------------------------------------------------

def test_the_deploy_hook_refuses_a_worktree_and_allows_the_bridge_build():
    hook = _module("deny_deploy_outside_main", TOOLS / "hooks")
    payload = hook.bash_payload("klee-mod\\build\\deploy_proto.ps1",
                                cwd=str(REPO))
    expected = 0 if hook.is_main_checkout(REPO) else 2
    assert hook.decide(hook.read_payload(payload)) == expected
    allowed = hook.bash_payload("klee-mod\\build\\deploy_bridge.ps1 -BuildOnly",
                                cwd=str(REPO))
    assert hook.decide(hook.read_payload(allowed)) == 0


def test_the_deploy_hook_is_registered_in_settings():
    settings = json.loads(
        (REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"]
                for group in settings["hooks"]["PreToolUse"]
                for h in group["hooks"]]
    assert "python tools/hooks/deny_deploy_outside_main.py" in commands
    matchers = [g["matcher"] for g in settings["hooks"]["PreToolUse"]]
    assert "Bash|PowerShell" in matchers


def test_the_deploy_hook_self_test_passes():
    res = _run(["tools/hooks/deny_deploy_outside_main.py", "--self-test"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0 failure(s)" in res.stdout


# --- the skills and the page ----------------------------------------------

SKILLS = ("gates", "open-pr", "land-pr", "mint-row", "agent-worktree", "seat",
          "deploy-round")


@pytest.mark.parametrize("skill", SKILLS)
def test_every_ritual_skill_is_short_and_declares_itself(skill):
    page = REPO / ".claude" / "skills" / skill / "SKILL.md"
    lines = page.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---" and lines[3] == "---", skill
    assert lines[1].startswith(f"name: {skill}"), skill
    assert lines[2].startswith("description: "), skill
    assert len(lines) < 40, f"{skill}: {len(lines)} lines, the ceiling is 40"


def test_the_rituals_page_names_every_script_and_is_in_the_index():
    page = (REPO / "docs" / "current" / "operations"
            / "agent-rituals.md").read_text(encoding="utf-8")
    for name in SCRIPTS:
        assert f"tools/{name}.py" in page, name
    for skill in SKILLS:
        assert f"`{skill}`" in page, skill
    index = (REPO / "docs" / "current" / "OPERATIONS.md").read_text(
        encoding="utf-8")
    assert "operations/agent-rituals.md" in index
    assert "operations/register-ids.md" in index
    assert "operations/seat-brief.md" in index
