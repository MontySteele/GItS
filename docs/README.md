# docs/

The governing surface lives in **[`docs/current/`](current/)** — start from the
repo-root `CLAUDE.md`. The loose files in this directory are **machine-adjacent
artifacts** (tool outputs and tool-cited references — role/tempo, art, patch
sentinel, upgrade grammar), not governing prose, and stay where their tools
read and write them.

Everything from before the 2026-08-06 simplification is in git, tagged. To read
an old path:

```
git fetch --depth=1 origin tag pre-simplification-2026-08-06
git show pre-simplification-2026-08-06:<old-path>
```
