#!/usr/bin/env python3
"""Shared plumbing for the Claude Code hooks under `tools/hooks/`.

WHY HOOKS AT ALL. Correction D of the 2026-08-26 governance audit: Claude
treats `CLAUDE.md` and `OPERATIONS.md` as CONTEXT, not as enforced
configuration. A prose rule -- "never `git add -A`", "remove a worktree with
`purge_worktree`" -- is advice that a long session can lose. A `PreToolUse`
hook is the enforcement layer: exit 2 and the tool call does not happen,
whatever the model decided. Everything in this directory exists to move one
rule from prose into that layer.

CONTRACT (Claude Code hooks reference). A command hook is handed a JSON object
on stdin carrying `tool_name` and `tool_input`; for `Bash`,
`tool_input.command` is the command line. Exit 0 allows; **exit 2 blocks the
call and shows this process's stderr to Claude**; any other code is a
non-blocking error. So every deny path here prints ONE line naming the rule
and the legal alternative, and returns 2.

PORTABILITY. The wiring in `.claude/settings.json` is `python tools/hooks/<x>.py`
so it runs from Git Bash and from PowerShell alike, and nothing in here shells
out to a POSIX-only utility. Paths resolve from `__file__`, never from the
process cwd, because a hook's cwd is not something this repo controls.

Usage (every script):
    <script>.py                 # read the hook payload from stdin
    <script>.py --self-test     # prove the rules bite, on synthetic payloads
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path, PureWindowsPath

REPO = Path(__file__).resolve().parents[2]

ALLOW = 0        # the tool call proceeds
BLOCK = 2        # the tool call is refused; stderr is shown to Claude

# Shell operators that end one simple command and start the next. A hook that
# only inspected the FIRST word of the line would wave through
# `echo hi && git push --force`, which is the shape a compound command takes
# in practice.
SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}

# `git`'s own options that consume the NEXT token, so the subcommand scan does
# not mistake `main` in `git -C main-checkout push` for a subcommand.
GIT_OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                     "--exec-path", "--super-prefix"}


def read_payload(text: str | None = None) -> dict:
    """The hook payload, or `{}` when stdin holds nothing parseable.

    Deliberately forgiving: a hook that raises on unexpected stdin is a hook
    that blocks every tool call in the session with a traceback. Unparseable
    input means "I have nothing to say", never "deny".
    """
    if text is None:
        try:
            text = sys.stdin.read()
        except (OSError, ValueError):
            return {}
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or "")


def tool_input(payload: dict) -> dict:
    value = payload.get("tool_input")
    return value if isinstance(value, dict) else {}


def bash_command(payload: dict) -> str:
    return str(tool_input(payload).get("command") or "")


def edited_path(payload: dict) -> str:
    """The path an Edit / Write / NotebookEdit touched, whichever key it used."""
    data = tool_input(payload)
    for key in ("file_path", "notebook_path", "path"):
        if data.get(key):
            return str(data[key])
    return ""


def simple_commands(command: str) -> list[list[str]]:
    """Split a command LINE into one token list per simple command.

    `punctuation_chars=True` makes shlex group `&&` and `||` as single tokens
    instead of emitting two bare `&`s, which is what lets the separator set
    above be written the way a person would write it. Unbalanced quotes are
    common in half-written commands, so a lexing failure degrades to a plain
    whitespace split rather than to an exception.
    """
    if not command.strip():
        return []
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        tokens = command.split()

    out: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in SEPARATORS:
            if current:
                out.append(current)
            current = []
        else:
            current.append(token)
    if current:
        out.append(current)
    return out


def _git_start(tokens: list[str]) -> int | None:
    """The index just past the `git` executable, or `None` if this is not git.

    Skips `VAR=value` prefixes (`GIT_PAGER=cat git push`) and accepts a git
    named by path, both of which a naive `tokens[0] == "git"` test reads as
    "not git at all".
    """
    index = 0
    while index < len(tokens) and "=" in tokens[index] and not tokens[index].startswith("-"):
        index += 1
    if index >= len(tokens) or Path(tokens[index]).name.lower() not in ("git", "git.exe"):
        return None
    return index + 1


def git_subcommand(tokens: list[str]) -> tuple[str, list[str]]:
    """`(subcommand, its arguments)` for a git invocation, else `("", [])`.

    The leading global options are skipped, `-C ../GItS-foo` included -- this
    function answers *what* git is being asked to do. **Where** it is being
    asked to do it is `git_c_dirs`, a separate question and for a while a
    missing one: the push gate ran in the session's checkout while the push
    itself carried `-C` to a sibling worktree.
    """
    start = _git_start(tokens)
    if start is None:
        return "", []
    index = start
    while index < len(tokens):
        token = tokens[index]
        if token in GIT_OPTS_WITH_ARG:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token, tokens[index + 1:]
    return "", []


def git_c_dirs(tokens: list[str]) -> list[str]:
    """Every `-C <dir>` on a git invocation, in order.

    Repeated `-C` COMPOSES -- `git -C a -C b` resolves `b` relative to `a`,
    exactly as git itself does -- so this returns the list and the caller
    folds it, rather than returning a single "the" directory that would be
    wrong for the second one.
    """
    start = _git_start(tokens)
    if start is None:
        return []
    dirs: list[str] = []
    index = start
    while index < len(tokens):
        token = tokens[index]
        if token == "-C" and index + 1 < len(tokens):
            dirs.append(tokens[index + 1])
            index += 2
            continue
        if token in GIT_OPTS_WITH_ARG:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        break                            # the subcommand: global options end
    return dirs


# `cd` and every spelling of it this project's two shells offer. PowerShell's
# `Set-Location` and its `sl` alias are here because BOTH PreToolUse hooks now
# match `Bash|PowerShell`: a rule that only understood Git Bash would be a
# rule with a second shell as its bypass.
CD_ALIASES = {"cd", "chdir", "pushd", "set-location", "sl"}

# A Git-Bash drive path (`/c/Users/...`) is not a path any Windows API
# understands, and it is the spelling that appears in practice.
POSIX_DRIVE = re.compile(r"^/([A-Za-z])(/.*)?$")


def native_path(raw: str) -> Path:
    """A path token as the running platform spells it."""
    text = str(raw).strip().strip('"').strip("'")
    match = POSIX_DRIVE.match(text.replace("\\", "/"))
    if match:
        return Path(f"{match.group(1).upper()}:{match.group(2) or '/'}")
    return Path(text)


def _joined(base: Path, raw: str) -> Path:
    """`raw` resolved against `base`, purely -- no filesystem, no symlinks.

    `normpath` rather than `resolve`: the answer must be the same whether or
    not the directory exists, because the caller's next move is to say so
    when it does not.
    """
    target = native_path(raw)
    if not _absolute(target):
        target = base / target
    return Path(os.path.normpath(target))


def _absolute(path: Path) -> bool:
    """Absolute on THIS platform, or spelled with a Windows drive.

    `native_path` turns `/c/Users/...` into `C:/Users/...` on purpose; on a
    POSIX host (the CI runner) `Path.is_absolute()` does not recognise that
    spelling and `_joined` would glue it under the base -- which is exactly
    what the self-test caught. The conversion's whole meaning is "this is an
    absolute drive path", so it is absolute everywhere.
    """
    return path.is_absolute() or PureWindowsPath(str(path)).is_absolute()


def cd_target(tokens: list[str]) -> str | None:
    """The directory a `cd`-shaped simple command moves to, else `None`.

    `None` also covers the two spellings whose destination cannot be read off
    the command line -- bare `cd` (a home directory) and `cd -` (wherever you
    were before). Those are UNKNOWN rather than "here", and the caller falls
    through to the next resolution source, which is then validated like any
    other.
    """
    if not tokens or tokens[0].lower() not in CD_ALIASES:
        return None
    # PowerShell spells the argument `-Path ../x`; both shells put flags
    # first, so dropping every leading `-token` leaves the destination. `cd -`
    # drops to nothing by the same rule, which is the answer it should give.
    args = [t for t in tokens[1:] if not t.startswith("-")]
    return args[0] if args else None


def payload_cwd(payload: dict) -> Path:
    """The directory Claude was in, per the hook payload's own `cwd` field.

    Documented as *"Current working directory when the hook is invoked"*, and
    it follows Claude: entering a worktree or running `cd` moves it, while
    `CLAUDE_PROJECT_DIR` stays at the session root. So it is the right default
    and the wrong answer on its own -- an in-line `cd` inside the very command
    being judged has not run yet when the hook fires.
    """
    raw = payload.get("cwd")
    return native_path(str(raw)) if raw else Path(os.getcwd())


def push_target(command: str, cwd: str | Path) -> Path:
    """The directory a `git push` in `command` would actually run in.

    THE DEFECT THIS FIXES. Every push in this project is made from a SIBLING
    WORKTREE while the session's directory stays the main checkout --
    `cd ../GItS-gov && git push -u origin gov-2026-08-26`, or
    `git -C ../GItS-gov push`. A gate that ran in the session's checkout
    tested a different branch, usually one behind, and reported GREEN for a
    tree it had never looked at. That is worse than no gate.

    Resolution order, highest first:
      (a) `-C` on the push invocation itself, folded left to right;
      (b) the most recent `cd` BEFORE the push in the same command line --
          `cd ../a && cd ../b && git push` lands in `b`, because each `cd` is
          resolved against the one before it, and a `cd` AFTER the push is
          never reached because this returns at the push;
      (c) `cwd`, the payload's own field.
    """
    running = native_path(str(cwd))
    for tokens in simple_commands(command):
        sub, _ = git_subcommand(tokens)
        if sub == "push":
            for directory in git_c_dirs(tokens):
                running = _joined(running, directory)
            return running
        moved = cd_target(tokens)
        if moved:
            running = _joined(running, moved)
    return running


def deny(reason: str) -> int:
    """Refuse the tool call. ONE line: what fired, and what to type instead."""
    print(reason, file=sys.stderr)
    return BLOCK


def note(message: str) -> None:
    print(message, file=sys.stderr)


def run_self_test(cases: list[tuple[str, int, str]],
                  decide) -> int:
    """`(payload JSON, expected exit code, label)` triples through `decide`.

    A deny hook that has never refused anything is indistinguishable from one
    that CANNOT refuse anything, and the allow cases matter just as much: a
    hook that blocks `git add docs/` blocks the workflow it was meant to
    protect. Both halves are cases here.
    """
    failures: list[str] = []
    for raw, expected, label in cases:
        got = decide(read_payload(raw))
        if got != expected:
            failures.append(f"self-test FAIL [{label}]: expected exit "
                            f"{expected}, got {got} -- payload {raw}")
    for line in failures:
        print(line)
    print(f"self-test: {len(cases)} case(s), {len(failures)} failure(s)")
    return 1 if failures else 0


def bash_payload(command: str, tool: str = "Bash",
                 cwd: str | None = None) -> str:
    """A synthetic shell-tool hook payload, for the self-tests.

    `tool` defaults to `Bash` and is set to `PowerShell` by the cases that
    prove the second shell is not a bypass: both carry the command at
    `tool_input.command`, which is why one parser serves both.
    """
    body: dict = {"tool_name": tool, "tool_input": {"command": command}}
    if cwd is not None:
        body["cwd"] = cwd
    return json.dumps(body)


def edit_payload(path: str, tool: str = "Edit") -> str:
    """A synthetic `Edit` / `Write` hook payload, for the self-tests."""
    return json.dumps({"tool_name": tool, "tool_input": {"file_path": path}})
