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
import shlex
import sys
from pathlib import Path

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


def git_subcommand(tokens: list[str]) -> tuple[str, list[str]]:
    """`(subcommand, its arguments)` for a git invocation, else `("", [])`.

    Handles the leading global options (`git -C ../GItS-foo worktree remove`)
    and env-prefixed invocations (`GIT_PAGER=cat git push`), both of which a
    naive `tokens[0] == "git"` test reads as "not git at all".
    """
    index = 0
    while index < len(tokens) and "=" in tokens[index] and not tokens[index].startswith("-"):
        index += 1                      # VAR=value prefixes
    if index >= len(tokens) or Path(tokens[index]).name.lower() not in ("git", "git.exe"):
        return "", []
    index += 1
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


def bash_payload(command: str) -> str:
    """A synthetic `Bash` hook payload, for the self-tests."""
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def edit_payload(path: str, tool: str = "Edit") -> str:
    """A synthetic `Edit` / `Write` hook payload, for the self-tests."""
    return json.dumps({"tool_name": tool, "tool_input": {"file_path": path}})
