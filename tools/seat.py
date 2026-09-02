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
lane filled in and runs nothing. That is for the OTHER kind of seat -- an Opus
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
from pathlib import Path

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


def brief_text(lane: int, character: str) -> str:
    """The brief, from `<LANE>` on, with the lane substituted."""
    text = BRIEF.read_text(encoding="utf-8")
    _, _, body = text.partition("## THE BRIEF")
    body = (body or text).replace("<LANE>", str(lane))
    return (f"You are the blind seat for **{character}** on lane {lane}.\n"
            f"{body.rstrip()}\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lane", type=int, default=1)
    ap.add_argument("--character", default="KLEEMOD-KLEE")
    ap.add_argument("--backend", choices=("local", "codex"), default="codex")
    ap.add_argument("--model", default="")
    ap.add_argument("--session-id", default="")
    ap.add_argument("--max-actions", type=int, default=60)
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
    ap.add_argument("--dry-run", action="store_true",
                    help="print the three commands and their env, run nothing")
    ap.add_argument("--oneline", action="store_true")
    args = ap.parse_args(argv)

    if args.opus_brief:
        print(brief_text(args.lane, args.character))
        return 0

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
