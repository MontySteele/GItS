#!/usr/bin/env python3
"""One blind seat, end to end: embark the lane, play the run, tear the lane down.

THE RITUAL. A seat round is three commands and one environment variable that is
easy to forget and expensive to forget:

    python -m understudy.embark --character <X> --lane <N>
    GITS_LANE=<N> python -m understudy.blindplay session --backend <B> ...
    python -m understudy.embark --teardown --lane <N>

`GITS_LANE` is how the three design-blind `blindplay` commands find the lane --
they take no flag, because that module may not import `instances` or `soak` at
all. Get it wrong and the seat plays lane 0's game, which is the owner's.
`GITS_LOCAL_PLAY_TOKENS=12000` is the other one: without it the local backend's
answer ceiling is 4096, the reply truncates mid-thought against the server's
reasoning budget, and the round dies on `answer_truncated` after the game is
already up.

And the teardown must run even when the session fails, or the lane's game
outlives the round and the next `deploy_proto.ps1` refuses on its pid.

    python tools/seat.py --lane 1 --character KLEEMOD-KLEE --backend local
    python tools/seat.py --lane 2 --character KLEEMOD-KOKOMI --backend codex \\
        --max-actions 70 --max-wall-s 5400
    python tools/seat.py --lane 2 --character X --dry-run      # print the three
    python tools/seat.py --opus-brief --lane 2 --character KLEEMOD-KLEE

`--opus-brief` prints `docs/current/operations/seat-brief.md`'s brief with the
lane filled in and runs nothing. Before the brief, on stderr so the pasted
stdout stays the brief alone, it prints the embark command the coordinator
runs first, with an explicit `--max-actions` (120 for an Opus seat by default;
`--max-actions 1500` for a Sonnet seat). `--scratch DIR` adds the seat's own
notes path, `DIR/seat-lane<N>/notes.md`, to the line that names the lane, and
(2026-10-08) writes two lane scripts into that folder -- `o` (observe --brief)
and `a` (act --brief --observe, which acts and then prints the new page)
-- with the lane, the absolute interpreter, `--brief`
and a `cd` to this repo root baked in, and the brief itself as
`brief-lane<N>.md`, UTF-8 with LF line ends. The brief's lane line names the
scripts. 21 of 43 seat transcripts on 2026-10-06/07 showed a failed command
after the seat had changed directory; 35 of 37 seats wrote such a wrapper for
themselves, and one shared wrapper drove another seat's lane.
That is for the OTHER kind of seat -- an Opus
subagent playing by hand through `blindplay observe` / `act` -- where the thing
that must not be re-improvised is the blindness rules, not the commands.

A LANE ABOVE ZERO IS NEVER A RUN OF RECORD (understudy/instances.py): its
profile is disposable, seeded once from lane 0's settings, and nothing in it is
ever read back. `--lane 0` is the owner's own game and this tool refuses it
unless `--allow-lane-0` is given.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path, PurePath

REPO = Path(__file__).resolve().parent.parent
BRIEF = REPO / "docs" / "current" / "operations" / "seat-brief.md"

#: What `blindplay session` prints when it finishes.
RECORD = re.compile(r"^record:\s*(.+)$", re.MULTILINE)
TRANSCRIPT = re.compile(r"^transcript:\s*(.+)$", re.MULTILINE)
OUTCOME = re.compile(r"^actions:\s*(\d+)\s+stopped:\s*(.+)$", re.MULTILINE)

#: The endpoint the local backend talks to. REQUIRED and with no default in
#: `local_model.py` on purpose -- a run that silently picked a server would be
#: a record that cannot say which model played it.
LOCAL_URL_ENV = "GITS_LOCAL_MODEL_URL"
DEFAULT_LOCAL_URL = "http://localhost:8010/v1"
#: EB-... the answer ceiling. 4096 is the shipped default and it truncates a
#: whole-run reply against this box's 4K reasoning budget; 12000 is what the
#: live-proven runs used (STATE.md).
PLAY_TOKENS = "12000"


def commands(args) -> list[tuple[str, list[str], dict[str, str]]]:
    """`[(label, argv, extra env)]` -- the three steps, in order."""
    py = sys.executable
    lane = str(args.lane)
    session_env = {"GITS_LANE": lane}
    if args.backend == "local":
        session_env[LOCAL_URL_ENV] = (os.environ.get(LOCAL_URL_ENV)
                                      or args.local_url)
        session_env["GITS_LOCAL_PLAY_TOKENS"] = args.play_tokens
    session = [py, "-m", "understudy.blindplay", "session",
               "--backend", args.backend,
               "--max-actions", str(args.max_actions),
               "--max-wall-s", str(args.max_wall_s)]
    if args.session_id:
        session += ["--session-id", args.session_id]
    if args.model:
        session += ["--model", args.model]
    return [
        ("embark", [py, "-m", "understudy.embark",
                    "--character", args.character, "--lane", lane], {}),
        ("session", session, session_env),
        ("teardown", [py, "-m", "understudy.embark",
                      "--teardown", "--lane", lane], {}),
    ]


def _run(argv: list[str], extra: dict[str, str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(extra)
    env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
    return subprocess.run(argv, capture_output=True, text=True,
                          cwd=str(REPO), env=env, errors="replace")


#: `EB-678`. The interpreter in the brief's own commands, RESOLVED. On this box
#: a bare `python` is the Windows Store alias: it opens the store rather than
#: running, the seat's Bash call never returns, and both r26 seats lost time to
#: it before either had played a card. The brief is the only place a seat reads
#: a command from, so the brief is where the absolute path belongs --
#: `sys.executable` is the interpreter `seat.py` is itself running under, which
#: is by construction the environment the round was launched in.
BARE_PYTHON = re.compile(r"(?<![-\w./\\])python(?=\s+-m\s+understudy\b)")


def interpreter() -> str:
    """`sys.executable` as the brief must print it: forward slashes, double
    quoted. The seat runs the brief's lines in bash, where the backslashes of
    a Windows path are escapes and the command is mangled silently; forward
    slashes are what the Windows interpreter itself accepts either way, and
    the quotes survive a space in the path and the shell's word splitting."""
    return f'"{PurePath(sys.executable).as_posix()}"'


#: The page's co-op section heading. Everything from it on is printed only
#: with `--coop`, so a singleplayer seat's brief is the brief it always was.
COOP_HEADING = "\n## CO-OP"

#: The action cap an Opus seat's embark gets when the coordinator names none.
#: `embark --max-actions` defaults to 0 (no cap), and a hand-driven seat once
#: ran 279 actions on it. The brief tells the seat its cap is the lane's own,
#: printed on every page, so this number is set in one place.
OPUS_MAX_ACTIONS = 120
#: What a backend seat's session is capped at when the coordinator names none.
BACKEND_MAX_ACTIONS = 60


def notes_path(scratch: str, lane: int) -> str:
    """The seat's own notes file, `<scratch>/seat-lane<N>/notes.md`. Seats
    running at once share the coordinator's scratchpad, and a shared notes
    file once held an earlier seat's notes; one folder per lane is the
    brief's own rule, with the path filled in."""
    return (PurePath(scratch) / f"seat-lane{lane}" / "notes.md").as_posix()


def lane_scripts(lane: int) -> dict[str, str]:
    """The seat's two lane scripts, `o` and `a`, as bash text. Each `cd`s to
    the repo root this tool runs from, so a seat that has changed directory
    still runs this checkout's bridge; the lane and `--brief` are fixed, and
    the interpreter is the absolute one the brief names (`EB-678`)."""
    root = PurePath(REPO).as_posix()
    py = interpreter()
    head = ("#!/usr/bin/env bash\n"
            f"# Lane {lane} seat script, written by tools/seat.py. "
            "Do not edit.\n"
            f'cd "{root}" || exit 1\n'
            f"export GITS_LANE={lane} PYTHONIOENCODING=utf-8\n")
    return {
        "o": head + f'exec {py} -m understudy.blindplay observe --brief "$@"\n',
        # 2026-10-09: `--observe` prints the new page after the act, so a
        # move is one call (subagents may not chain `a ... && o`).
        "a": head + (f"exec {py} -m understudy.blindplay act --brief "
                     '--observe "$@"\n'),
    }


def write_lane_scripts(scratch: str, lane: int) -> list[Path]:
    """Write `o` and `a` into `<scratch>/seat-lane<N>/`, LF line ends."""
    folder = Path(notes_path(scratch, lane)).parent
    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in lane_scripts(lane).items():
        path = folder / name
        path.write_bytes(text.encode("utf-8"))
        try:
            path.chmod(0o755)
        except OSError:
            pass
        out.append(path)
    return out


def embark_line(lane: int, character: str, max_actions: int,
                coop: bool = False) -> str:
    """The embark the coordinator runs before handing over the brief, with
    the cap explicit. A co-op pair is embarked once for both lanes, so its
    line leaves the pair for the coordinator to name."""
    py = interpreter()
    if coop:
        return (f"{py} -m understudy.embark --coop --lanes <HOST>,<CLIENT> "
                f"--characters <HOST>,<CLIENT> --max-actions {max_actions}")
    return (f"{py} -m understudy.embark --character {character} "
            f"--lane {lane} --max-actions {max_actions}")


def brief_text(lane: int, character: str, coop: bool = False,
               scratch: str = "") -> str:
    """The brief, with the lane and the interpreter filled in.

    `coop` appends the page's co-op section (its own heading line dropped):
    a seat sharing a run with another seat is told so, and nobody else is.
    `scratch` adds the seat's own notes path to the line that names its
    lane; the brief's body is never reworded.
    """
    text = BRIEF.read_text(encoding="utf-8")
    _, _, body = text.partition("## THE BRIEF")
    body, _, coop_part = (body or text).partition(COOP_HEADING)
    if coop and coop_part:
        body = body.rstrip() + "\n\n" + coop_part.split("\n", 1)[1].lstrip()
    body = body.replace("<LANE>", str(lane))
    py = interpreter()
    body = BARE_PYTHON.sub(lambda _m: py, body)
    head = f"You are the blind seat for **{character}** on lane {lane}."
    if scratch:
        notes = notes_path(scratch, lane)
        folder = PurePath(notes).parent.as_posix()
        head += (f" Your scratch folder is `{folder}`"
                 f" and your notes file is `{notes}`."
                 f" Play through your two lane scripts, which carry your lane,"
                 f" the interpreter, `--brief` and the repo folder:"
                 f" `bash {folder}/o` to observe (`bash {folder}/o --define"
                 f' "<Word>"` for a definition) and'
                 f' `bash {folder}/a "<command>"` to act, which also prints'
                 f' the new page.')
    return f"{head}\n{body.rstrip()}\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lane", type=int, default=1)
    ap.add_argument("--character", default="KLEEMOD-KLEE")
    ap.add_argument("--backend", choices=("local", "codex"), default="codex")
    ap.add_argument("--model", default="")
    ap.add_argument("--session-id", default="")
    ap.add_argument("--max-actions", type=int, default=None,
                    help=f"the action cap: the session's for a backend seat "
                         f"(default {BACKEND_MAX_ACTIONS}), the embark's for "
                         f"--opus-brief (default {OPUS_MAX_ACTIONS}; a Sonnet "
                         f"seat uses 1500)")
    ap.add_argument("--max-wall-s", type=float, default=3600.0)
    ap.add_argument("--local-url", default=DEFAULT_LOCAL_URL,
                    help=f"only used with --backend local, and only when "
                         f"${LOCAL_URL_ENV} is unset")
    ap.add_argument("--play-tokens", default=PLAY_TOKENS,
                    help="GITS_LOCAL_PLAY_TOKENS for the local backend")
    ap.add_argument("--allow-lane-0", action="store_true",
                    help="lane 0 is the owner's own game; this is the door")
    ap.add_argument("--opus-brief", action="store_true",
                    help="print the blindness brief for an Opus seat and exit")
    ap.add_argument("--coop", action="store_true",
                    help="with --opus-brief: add the co-op paragraph (the "
                         "run is shared with another seat; `wait`)")
    ap.add_argument("--scratch", default="",
                    help="with --opus-brief: the coordinator's scratchpad; "
                         "the brief names <scratch>/seat-lane<N>/notes.md as "
                         "the seat's own notes file")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the three commands and their env, run nothing")
    ap.add_argument("--oneline", action="store_true")
    args = ap.parse_args(argv)

    if args.opus_brief:
        cap = (OPUS_MAX_ACTIONS if args.max_actions is None
               else args.max_actions)
        # THE COORDINATOR'S LINES GO TO STDERR: stdout is the brief, pasted
        # whole, and the embark is not one of the seat's two commands.
        print("Embark first (coordinator only; not part of the brief):",
              file=sys.stderr)
        print("  " + embark_line(args.lane, args.character, cap,
                                 coop=args.coop), file=sys.stderr)
        if args.scratch:
            notes = Path(notes_path(args.scratch, args.lane))
            if notes.exists():
                print(f"  WARNING: {notes.as_posix()} already exists (an "
                      f"earlier seat's notes?); move it before this seat "
                      f"starts.", file=sys.stderr)
        text = brief_text(args.lane, args.character, coop=args.coop,
                          scratch=args.scratch)
        if args.scratch:
            for path in write_lane_scripts(args.scratch, args.lane):
                print(f"  wrote {path.as_posix()}", file=sys.stderr)
            brief = (Path(notes_path(args.scratch, args.lane)).parent.parent
                     / f"brief-lane{args.lane}.md")
            brief.write_bytes(text.encode("utf-8"))
            print(f"  wrote {brief.as_posix()} (UTF-8, LF)", file=sys.stderr)
        print(file=sys.stderr)
        # UTF-8 with LF, whatever the console's code page: a coordinator who
        # redirected this in PowerShell got cp1252 with CRLF (an em dash came
        # out as byte 0x97).
        sys.stdout.flush()
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
        sys.stdout.flush()
        return 0
    if args.max_actions is None:
        args.max_actions = BACKEND_MAX_ACTIONS

    if args.lane == 0 and not args.allow_lane_0:
        print("REFUSED: lane 0 is the machine's own game and its profile is "
              "the one runs of record are played on. Use --lane 1 or 2 (a "
              "disposable profile, understudy/instances.py), or "
              "--allow-lane-0 if this really is the owner's game.")
        return 2

    steps = commands(args)
    if args.dry_run:
        for label, cmd, extra in steps:
            env = " ".join(f"{k}={v}" for k, v in extra.items())
            print(f"{label:<9} {env + ' ' if env else ''}{' '.join(cmd)}")
        return 0

    embark = _run(*steps[0][1:])
    if embark.returncode:
        print(f"seat: EMBARK FAILED (exit {embark.returncode})")
        print((embark.stdout + embark.stderr).strip()[-2000:])
        return 1

    try:
        session = _run(*steps[1][1:])
    finally:
        teardown = _run(*steps[2][1:])

    text = session.stdout + session.stderr
    record = RECORD.search(text)
    transcript = TRANSCRIPT.search(text)
    outcome = OUTCOME.search(text)
    actions = outcome.group(1) if outcome else "?"
    stopped = outcome.group(2).strip() if outcome else "unknown"

    if args.oneline:
        print(f"seat lane {args.lane} {args.character} ({args.backend}): "
              f"{actions} actions, stopped {stopped}; "
              f"record {record.group(1).strip() if record else 'NONE'}; "
              f"teardown {'ok' if teardown.returncode == 0 else 'FAILED'}")
        return 0 if session.returncode == 0 else 1

    print(f"record:     {record.group(1).strip() if record else 'NONE WRITTEN'}")
    print(f"transcript: "
          f"{transcript.group(1).strip() if transcript else '(gitignored)'}")
    print(f"actions:    {actions}   stopped: {stopped}")
    print(f"teardown:   "
          f"{'reverted' if teardown.returncode == 0 else 'FAILED -- the lane may still be up'}")
    if session.returncode:
        print(f"\nsession exited {session.returncode}:")
        print((session.stdout + session.stderr).strip()[-2000:])
        return 1
    if args.lane:
        print(f"\nLane {args.lane} is a DISPOSABLE profile: this is not a run "
              f"of record (understudy/instances.py LANE_GUARDRAIL).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
