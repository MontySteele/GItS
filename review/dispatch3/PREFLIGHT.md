# Surplus-dispatch-3 — preflight record (charter §0), 2026-08-26 evening

Recorded by the orchestrator from the LIVE primary checkout before any agent was dispatched.

| Check | Result |
|---|---|
| `git rev-parse --short HEAD` (primary) | `223a4ff` — merge of PR #106 (EB-146 closed) |
| `git status --short` (primary) | clean — no [USER]-owned modifications or untracked files |
| Charter's claimed `f38cd90` | RESOLVES here: it is the merge of `hook-selftest-posix` into main (PR before #106). It is NOT HEAD. Not used as evidence. |
| `review/active/full-mod-roadmap-2026-08-26.md` | ABSENT |
| BACKLOG `EB-147`–`EB-155` | ABSENT (BACKLOG ceiling is `EB-146`, now retired) |
| QUEUE `M46` | ABSENT (`M45` is the highest, open) |
| `review/dispatch3/` | did not exist; created on this branch |
| `S11` | issued — `docs/current/atlas/README.md` present. This dispatch starts at **S12**. |
| Deployed mod during this dispatch | `0.2-1155`, build id `20260826-193602+223a4ff`, [USER] is playtesting on it. NO agent may launch, deploy to, or touch the game installation tonight. |
| Downfall reference | pinned `lamali292/Downfall@32e61132052ae58e32cd33342d24136ffe18be12`, fetched read-only OUTSIDE the repo at `C:\Users\Monty\AppData\Local\Temp\claude\C--Users-Monty-Documents-GitHub-GItS\4bcbd91a-df34-44cb-b01a-d84ef13d2f24\scratchpad\Downfall` (405 MB, depth-1). Reference-reading only (charter §3.7). |
| Runner | local Windows machine, 16 CPUs, shares the machine with the playtest — tooling lanes run tests without `-n auto`. |

**Version skew to report (charter §0.4):** the roadmap the charter calls "attached" and the ids `EB-147`–`EB-155` / `M46` are not in this checkout. The charter text itself (`CHARTER.md`, verbatim) is the planning context. No replacement ids were minted; the charter's `EB-1xx` labels are used only as the charter's own names for the lanes.

**Rails and worktrees (charter §2):**
- Research rail: this worktree, `../GItS-dispatch3`, branch `dispatch3-2026-08-26`. Research agents write ONLY their assigned file(s) under `review/dispatch3/` and run no git commands; the integrator commits.
- Tooling rail: `../GItS-laneA` (`dispatch3-laneA-animation-bakeoff`), `../GItS-laneB` (`dispatch3-laneB-art-ledger`), `../GItS-laneC` (`dispatch3-laneC-visual-qa`); lane D's worktree is created only if S13 finds a credible socket.
