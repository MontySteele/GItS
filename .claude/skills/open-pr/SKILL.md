---
name: open-pr
description: Open a pull request with the mandatory attribution footer, calling gh at its real path, and get back only the number and the URL. Use whenever a branch is pushed and needs a PR.
---

# open-pr — the footer, the gh path, the two lines back

`gh` is NOT on PATH on this machine (`C:\Program Files\GitHub CLI\gh.exe`), and
every PR body must end with the robot line and the session URL. Both are
handled:

```sh
export CLAUDE_SESSION_URL=https://claude.ai/code/session_...
python tools/open_pr.py --title "<title>" --body-file <body>.md
python tools/open_pr.py --title "<title>" --body-file <body>.md --dry-run
```

It prints the PR number and URL and nothing else. `--dry-run` prints the body it
would send, so you can check the footer without opening anything.

## Before you call it

1. **Push first.** This tool does not push — a push goes through
   `git push -u origin <branch>` so `tools/hooks/push_gate.py` sees it.
2. **Write the body to a file**, not inline. The footer is appended to a copy;
   your file on disk is not edited.
3. **The body says what changed and what did not** — the scripts or rows
   touched, the gates with their counts, and a Not-done list. A PR body that
   only names files is a diff with a title.

## Who merges

Claude merges every PR that asks nothing of [USER] itself on green CI
(`tools/land_pr.py`, or `gh pr merge <n> --merge`) and says so in the turn
(R259). **A PR is [USER]'s only when it carries an open A/B/C pick, amends
`LAW.md` / `EXPERIMENTS.md` text, or moves a shipped-sheet number** — open it
and stop; do not end a turn waiting on the merge, stack the next branch and
keep going.
