#!/usr/bin/env python3
"""PreToolUse/Bash|PowerShell: refuse a deploy or a pck build from a WORKTREE.

WHAT WENT WRONG, TWICE THIS WEEK. `build_pck.ps1` and the two deploy scripts
read two things a linked worktree does not have: `klee-mod/local.props`, which
names this machine's Steam install and is gitignored, and `ImageGen/images/**`,
the Tier F art the pck is built from and the card portraits the package stages.
Run from a worktree, `build_pck` builds a pck out of nothing and `deploy.ps1`
stages a package whose `images/cards` is empty -- and the deploy PRINTS SUCCESS,
because a missing art directory is a WARNING in those scripts and not a failure
(`deploy_proto.ps1`: `WARNING: no card art at $artSrc`). A build was shipped
with no art twice this week and neither time did anything say so.

`local.props` is the one that fails loudly (`throw "local.props not found"`),
which is why the failure mode is worse than it looks: an agent that has copied
`local.props` into its worktree -- which `tools/agent_worktree.py` does, so the
C# build works there -- has removed the only loud half and kept the silent one.

THE RULE, AS OPERATIONS STATES IT. Deploys and art passes happen on the
art-bearing primary checkout only. **One command is legal in a worktree** and
is allowed here by name: `deploy_bridge.ps1 -BuildOnly`, which lints the vendor
pin, compiles into `klee-mod\\dist\\STS2_MCP`, touches no game directory and
holds no lock. Bare `deploy_bridge.ps1` INSTALLS, so it is refused with the
rest.

HOW "MAIN CHECKOUT" IS DECIDED. `git -C <dir> rev-parse --git-common-dir`: in
the primary tree that is `<root>/.git`, and in a linked worktree it is the
primary tree's `.git` while the worktree sits somewhere else entirely. So the
test is "is the common dir's parent this directory", which is exactly the
question, needs no configuration, and cannot be fooled by a copied
`local.props`. **A directory git cannot answer for is ALLOWED**, deliberately:
this hook exists to catch a known-wrong place, not to be a second opinion on
every shell command in the session.

    python tools/hooks/deny_deploy_outside_main.py               # hook mode
    python tools/hooks/deny_deploy_outside_main.py --self-test   # prove it bites
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _hooklib import (ALLOW, bash_command, bash_payload, cd_target,  # noqa: E402
                      deny, native_path, payload_cwd, read_payload,
                      run_self_test, simple_commands, tool_name)

#: The three scripts, by basename, however they are spelled on the line --
#: `klee-mod\build\deploy_proto.ps1`, `.\deploy_proto.ps1`,
#: `& "C:\...\deploy_proto.ps1"`. Matched on the basename because the path in
#: front of it is exactly what varies.
GUARDED = {"deploy_proto.ps1", "deploy.ps1", "deploy_bridge.ps1",
           "build_pck.ps1"}

#: The one legal invocation in a worktree, and the flag that makes it legal.
BUILD_ONLY = {"-buildonly", "--buildonly"}

#: Programs that RUN their script argument, so a guarded basename anywhere in
#: THEIR arguments is still an execution: `powershell -File <path>`,
#: `pwsh -NoProfile -File <path>`, `bash <path>`, `cmd /c <path>`.
INTERPRETERS = {"powershell", "powershell.exe", "pwsh", "pwsh.exe",
                "cmd", "cmd.exe", "bash", "bash.exe", "sh", "sh.exe",
                "zsh", "dash", "start", "start-process"}


def normalise(command: str) -> str:
    """Backslashes to forward slashes, before the line is lexed.

    THE DEFECT THIS FIXES, caught by the self-test on its first run.
    `_hooklib.simple_commands` lexes with `shlex(posix=True)`, where a
    backslash is an ESCAPE -- so the unquoted Windows path every one of these
    scripts is documented with, `klee-mod\\build\\deploy_proto.ps1`, lexes to
    the single token `klee-modbuilddeploy_proto.ps1` and its basename matches
    nothing. The quoted spelling worked and the bare one did not, which is the
    worst possible split for a deny hook. Windows accepts either separator, so
    normalising first costs nothing and makes both spellings one case.
    """
    return command.replace("\\", "/")


def _joined(base: Path, raw: str) -> Path:
    target = native_path(raw)
    if not target.is_absolute() and ":" not in str(target)[:2]:
        target = base / target
    return Path(os.path.normpath(target))


def _basename(token: str) -> str:
    """The lowercased basename of a path token, quotes and `&` stripped."""
    text = str(token).strip().strip('"\'').lstrip("&").strip().strip('"\'')
    return Path(text).name.lower()


def guarded_script(tokens: list[str]) -> str:
    """The guarded script this simple command EXECUTES, or `""`.

    THE DEFECT THIS FIXES (`EB-812`). This used to scan EVERY token for a
    guarded basename, so a guarded path that was merely an ARGUMENT --
    `git add tools/build_pck.ps1`, `cat tools/build_pck.ps1`,
    `grep -n Tier tools/build_pck.ps1` -- was refused as a deploy from a
    worktree, which is exactly where that `git add` has to happen. A file is
    not a deploy; RUNNING it is. So only the execution positions count:

      * the command word itself, after `VAR=value` prefixes and PowerShell's
        `&` call operator -- `tools/build_pck.ps1`, `./tools/build_pck.ps1`,
        `& "C:/.../deploy_proto.ps1"` (shlex splits `&` off as punctuation,
        so the script lands in the command position either way);
      * any argument of a program that runs its argument --
        `powershell -File <path>`, `pwsh -NoProfile -File <path>`,
        `bash <path>`, `cmd /c <path>` (`INTERPRETERS`).

    Everything the old scan denied by execution it still denies; what changes
    is a path handed to git, cat, grep, sed or ls.
    """
    index = 0
    while index < len(tokens):
        token = tokens[index].strip()
        # PowerShell's call operator, and `VAR=value` environment prefixes,
        # are not the command word.
        if token.strip('"\'') in ("&", "call"):
            index += 1
            continue
        if "=" in token and not token.startswith("-") and "/" not in token:
            index += 1
            continue
        break
    if index >= len(tokens):
        return ""

    head = _basename(tokens[index])
    if head in GUARDED:
        return head
    if head in INTERPRETERS:
        for token in tokens[index + 1:]:
            name = _basename(token)
            if name in GUARDED:
                return name
    return ""


def is_main_checkout(directory: Path) -> bool | None:
    """True / False / `None` when git cannot answer for this directory."""
    try:
        res = subprocess.run(
            ["git", "-C", str(directory), "rev-parse",
             "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode or not res.stdout.strip():
        return None
    common = Path(res.stdout.strip())
    if common.name != ".git":
        return None
    try:
        return common.parent.resolve() == Path(directory).resolve()
    except OSError:
        return None


def decide(payload: dict) -> int:
    if tool_name(payload) not in ("Bash", "PowerShell"):
        return ALLOW
    command = bash_command(payload)
    if not command.strip():
        return ALLOW

    running = payload_cwd(payload)
    for tokens in simple_commands(normalise(command)):
        script = guarded_script(tokens)
        if script:
            lowered = {t.lower() for t in tokens}
            if script == "deploy_bridge.ps1" and lowered & BUILD_ONLY:
                return ALLOW
            if is_main_checkout(running) is False:
                return deny(
                    f"REFUSED: {script} runs from the ART-BEARING MAIN "
                    f"CHECKOUT only, and {running} is a linked worktree. A "
                    f"worktree has no ImageGen/images, so the pck and the "
                    f"staged package come out with NO ART and the script "
                    f"prints a warning and succeeds -- that has shipped twice "
                    f"this week. cd to the primary checkout, or use "
                    f"`deploy_bridge.ps1 -BuildOnly`, which is the one deploy "
                    f"script legal here (docs/current/operations/"
                    f"build-deploy.md).")
            return ALLOW
        moved = cd_target(tokens)
        if moved:
            running = _joined(running, moved)
    return ALLOW


def self_test() -> int:
    """Synthetic payloads: a real worktree path and a real main-checkout path.

    Both are read off THIS repo rather than invented, because the whole rule
    is a question git answers about a directory -- a fixture that faked the
    answer would be testing the fixture.
    """
    here = Path(__file__).resolve().parents[2]
    main = here
    res = subprocess.run(["git", "-C", str(here), "rev-parse",
                          "--path-format=absolute", "--git-common-dir"],
                         capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        common = Path(res.stdout.strip())
        if common.name == ".git":
            main = common.parent
    worktree = here if main != here else None

    cases = [
        (bash_payload("klee-mod\\build\\deploy_proto.ps1 -KleeOverhaul",
                      cwd=str(main)), ALLOW,
         "deploy_proto from the main checkout is allowed"),
        (bash_payload("tools\\build_pck.ps1", "PowerShell", cwd=str(main)),
         ALLOW, "build_pck from the main checkout is allowed"),
        (bash_payload("git status", cwd=str(main)), ALLOW,
         "an unrelated command is allowed"),
        (bash_payload("git add tools/build_pck.ps1", cwd=str(main)), ALLOW,
         "staging the script from the main checkout is allowed"),
        (bash_payload("python tools/gates.py", cwd=str(main)), ALLOW,
         "a python command naming no script is allowed"),
        (bash_payload("klee-mod\\build\\deploy_bridge.ps1 -BuildOnly",
                      cwd=str(main)), ALLOW,
         "the bridge BUILD is allowed anywhere"),
        ("not json at all", ALLOW, "an unparseable payload never denies"),
    ]
    if worktree is not None:
        cases += [
            (bash_payload("klee-mod\\build\\deploy_proto.ps1",
                          cwd=str(worktree)), 2,
             "deploy_proto from a worktree is refused"),
            (bash_payload("& '.\\tools\\build_pck.ps1'", "PowerShell",
                          cwd=str(worktree)), 2,
             "build_pck from a worktree is refused, however it is spelled"),
            (bash_payload("klee-mod\\build\\deploy_bridge.ps1",
                          cwd=str(worktree)), 2,
             "the bridge INSTALL from a worktree is refused"),
            (bash_payload("klee-mod\\build\\deploy_bridge.ps1 -BuildOnly",
                          cwd=str(worktree)), ALLOW,
             "the bridge BUILD from a worktree is the one legal command"),
            (bash_payload(f"cd {main} && klee-mod\\build\\deploy_proto.ps1",
                          cwd=str(worktree)), ALLOW,
             "an inline cd to the main checkout is honoured"),
            # EB-812: a guarded path as an ARGUMENT is a file, not a deploy.
            (bash_payload("git add tools/build_pck.ps1",
                          cwd=str(worktree)), ALLOW,
             "git add of the script from a worktree is allowed"),
            (bash_payload("git add tools\\build_pck.ps1",
                          cwd=str(worktree)), ALLOW,
             "git add of the script, Windows spelling, is allowed"),
            (bash_payload("cat tools/build_pck.ps1",
                          cwd=str(worktree)), ALLOW,
             "reading the script from a worktree is allowed"),
            (bash_payload("grep -n Tier tools/build_pck.ps1",
                          cwd=str(worktree)), ALLOW,
             "grepping the script from a worktree is allowed"),
            (bash_payload("ls -l tools/build_pck.ps1 klee-mod/build/deploy.ps1",
                          cwd=str(worktree)), ALLOW,
             "listing the guarded scripts from a worktree is allowed"),
            (bash_payload("git commit -m 'tools/build_pck.ps1: a fix'",
                          cwd=str(worktree)), ALLOW,
             "the script named in a commit message is allowed"),
            # ... and every EXECUTION shape is still refused.
            (bash_payload(".\\tools\\build_pck.ps1", "PowerShell",
                          cwd=str(worktree)), 2,
             "`.\\tools\\build_pck.ps1` from a worktree is refused"),
            (bash_payload("& tools/build_pck.ps1", "PowerShell",
                          cwd=str(worktree)), 2,
             "`& tools/build_pck.ps1` from a worktree is refused"),
            (bash_payload("powershell -File tools/build_pck.ps1",
                          cwd=str(worktree)), 2,
             "`powershell -File` from a worktree is refused"),
            (bash_payload("pwsh -File .\\tools\\build_pck.ps1", "PowerShell",
                          cwd=str(worktree)), 2,
             "`pwsh -File .\\tools\\build_pck.ps1` from a worktree is refused"),
            (bash_payload("tools/build_pck.ps1", "PowerShell",
                          cwd=str(worktree)), 2,
             "the bare leading token from a worktree is refused"),
            (bash_payload("git status && .\\tools\\build_pck.ps1", "PowerShell",
                          cwd=str(worktree)), 2,
             "an execution after a separator is still refused"),
        ]
    return run_self_test(cases, decide)


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    return decide(read_payload())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
