#!/usr/bin/env python3
"""Open a pull request with the mandatory footer, and print the number and URL.

THE RITUAL. `gh` is not on PATH on this machine and never has been -- it lives
at `C:\\Program Files\\GitHub CLI\\gh.exe`, which is a memory every agent has to
carry or rediscover. Every PR body must end with the two-line attribution
footer. And `gh pr create` prints a paragraph where the useful answer is one
number and one URL.

    export CLAUDE_SESSION_URL=https://claude.ai/code/session_...
    python tools/open_pr.py --title "..." --body-file body.md
    python tools/open_pr.py --title "..." --body-file body.md --draft
    python tools/open_pr.py --title "..." --body-file body.md --dry-run

THE FOOTER IS APPENDED, NEVER DUPLICATED. If the body already ends with the
robot line the footer is left alone -- an agent that pasted it by hand and one
that let this tool do it produce the same PR. The session URL comes from
`--session-url` or `$CLAUDE_SESSION_URL`; with neither, the robot line still
goes on and the URL line is omitted rather than invented.

WHAT IT DOES NOT DO. It does not push. A push goes through the branch's own
`git push -u origin <branch>`, where `tools/hooks/push_gate.py` sees it; a
wrapper that pushed would be a wrapper that routed around the gate.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: The one path `gh` is installed at on this machine, and the fallbacks in the
#: order they are worth trying. `shutil.which` first, so a machine that DOES
#: have it on PATH is not second-guessed.
GH_CANDIDATES = (
    r"C:\Program Files\GitHub CLI\gh.exe",
    r"C:\Program Files (x86)\GitHub CLI\gh.exe",
)

ROBOT = ("\U0001F916 Generated with "
         "[Claude Code](https://claude.com/claude-code)")

PR_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/pull/(\d+)")


def gh_path() -> str:
    import shutil
    found = shutil.which("gh")
    if found:
        return found
    for candidate in GH_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise SystemExit(
        "gh not found. It is installed at "
        r"'C:\Program Files\GitHub CLI\gh.exe' on this machine and is not on "
        "PATH; pass --gh <path> if it has moved.")


def with_footer(body: str, session_url: str = "") -> str:
    """`body` plus the mandatory footer, or `body` if it already carries it."""
    body = body.rstrip("\n")
    if ROBOT in body:
        return body + "\n"
    lines = [body, "", ROBOT]
    if session_url:
        lines += ["", session_url]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", required=True,
                    help="a markdown file; the footer is appended to a COPY, "
                         "the file on disk is not edited")
    ap.add_argument("--base", default="main")
    ap.add_argument("--head", default="",
                    help="the branch (default: whatever is checked out here)")
    ap.add_argument("--session-url",
                    default=os.environ.get("CLAUDE_SESSION_URL", ""),
                    help="default: $CLAUDE_SESSION_URL")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--gh", default="", help="path to gh.exe")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the body that would be sent, call nothing")
    ap.add_argument("--oneline", action="store_true")
    args = ap.parse_args(argv)

    source = Path(args.body_file)
    if not source.exists():
        print(f"REFUSED: no body file at {source}")
        return 1
    body = with_footer(source.read_text(encoding="utf-8"), args.session_url)

    if args.dry_run:
        print(f"title: {args.title}")
        print(f"base:  {args.base}   head: {args.head or '(current branch)'}")
        print("-" * 60)
        print(body, end="")
        return 0

    staged = source.with_suffix(source.suffix + ".footer")
    staged.write_text(body, encoding="utf-8")
    argv_gh = [args.gh or gh_path(), "pr", "create",
               "--title", args.title, "--body-file", str(staged),
               "--base", args.base]
    if args.head:
        argv_gh += ["--head", args.head]
    if args.draft:
        argv_gh.append("--draft")
    try:
        res = subprocess.run(argv_gh, capture_output=True, text=True,
                             cwd=str(Path.cwd()))
    finally:
        staged.unlink(missing_ok=True)

    text = (res.stdout or "") + (res.stderr or "")
    m = PR_URL.search(text)
    if res.returncode or not m:
        print(f"gh pr create failed (exit {res.returncode}):")
        print(text.strip())
        return res.returncode or 1
    number, url = m.group(1), m.group(0)
    if args.oneline:
        print(f"open_pr: #{number} {url}")
    else:
        print(f"#{number}")
        print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
