# Agent rituals — the seven things every sitting does by hand

A sitting of twelve parallel agents does the same seven things twelve times
each, and every one of them costs its raw output in tokens: a 35-row lint
table, four hundred lines of pytest, a `gh` paragraph, a 170-line register
opened to read one row. **The work was never the expensive part; reading the
output was.** Each ritual below now has a script that runs it exactly as before
and prints the answer instead of the transcript.

Every script takes `--help`, and every one takes `--oneline` — one line, for
when the answer goes in a report rather than on the screen. The `.claude/skills/`
entry named beside each is the short version an agent loads instead of this
page.

| Ritual | Script | Skill | What it saves |
|---|---|---|---|
| run the gates | `tools/gates.py` | `gates` | ~400 lines of pytest / lint / dotnet output → one line per gate plus the failing test names; the rest goes to `.gates/<stamp>.log` |
| read one register row | `tools/row.py` | `mint-row` | opening a 170-line register, or a truncated grep, to read one of ~100 rows |
| mint a register row | `tools/mint_row.py` | `mint-row` | the id lookup, the pipe syntax, the character count against the 600 gate, and both lints — and since the ceiling is derived, the edit to `lint_register_ids.py` is gone entirely |
| open a worktree | `tools/agent_worktree.py` | `agent-worktree` | the fetch + add + `local.props` copy, and re-deriving CLAUDE.md's read order for the task by hand |
| open a PR | `tools/open_pr.py` | `open-pr` | the `gh` full path, the mandatory footer, and a paragraph of output for one number |
| land a plumbing PR | `tools/land_pr.py` | `land-pr` | the check-run read, the merge, the purge, the fast-forward, and the untracked-file trap that stopped two lands this week |
| run a blind seat | `tools/seat.py` | `seat` | the three commands, `GITS_LANE`, `GITS_LOCAL_PLAY_TOKENS=12000`, and a teardown that runs even when the session fails |
| deploy a round | `tools/deploy_round.py` | `deploy-round` | the pck-staleness decision (mtimes against two trees `git status` cannot see) and the three verification lines read off disk |

## The one hook

`tools/hooks/deny_deploy_outside_main.py` (`PreToolUse`, `Bash|PowerShell`,
registered in `.claude/settings.json`) refuses `deploy_proto.ps1`, `deploy.ps1`,
`deploy_bridge.ps1` and `build_pck.ps1` when the directory they would run in is
a **linked worktree**. A worktree has no `ImageGen/images`, so those scripts
build a pck out of nothing and stage a package with no card art — and they
print a WARNING and succeed. That shipped twice in one week. The one legal
invocation in a worktree, `deploy_bridge.ps1 -BuildOnly`, is allowed by name.

The hook decides "main checkout" from `git rev-parse --git-common-dir`, so it
cannot be fooled by a copied `local.props`, and a directory git cannot answer
for is ALLOWED — this catches a known-wrong place, it is not a second opinion
on every command.

## Two rules the scripts do not replace

- **A dry run first, on anything that touches the game or GitHub.**
  `--dry-run` on `deploy_round`, `land_pr`, `seat` and `agent_worktree` prints
  the decision and does nothing. The decision is the part worth reading.
- **`--fast` is never the pre-push gate.** `gates.py --fast` drops the
  calibration bands; `operations/test.md` is explicit that a band that was not
  run is not a band, and the tool says so in its own output.
