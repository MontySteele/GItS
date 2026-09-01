## Briefing an agent — what it reads before it works

Measured 2026-08-29 on a tool-fix agent: ~31k tokens of reading before its
first edit, a quarter of it `STATE.md`, most of the rest orientation — paging
2,000-line modules in ranges to find where something lives. Three rules:

1. **Inline the load-bearing facts** (the pin, the installed build, the branch,
   the row's acceptance) in the brief itself. `STATE.md` is the snapshot for a
   fresh session, not a brief; point at it for the register edit at the end.
2. **Map first, then one definition.** `python tools/module_map.py <file|dir>
   [--grep <name>]` prints every class/function with its line range and first
   docstring line — 5% of the module's size — so the agent reads exactly the
   definition it will change (`sed -n '<start>,<end>p'`) and its neighbours,
   never the file. Files in a brief are "consult as needed", never "read".
3. **The atlas answers "how must this behave"** (entry points, invariants,
   traps); the map answers "which lines". Neither replaces reading the code
   you change.
