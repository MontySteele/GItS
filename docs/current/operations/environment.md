## Environment

- Python 3.12. The suite's actual imports are `pytest pyyaml pillow numpy`,
  plus `pytest-xdist`. Since 2026-08-29 those five live in
  `.github/requirements-ci.txt` and all three CI jobs install from it — that
  file exists so `setup-python`'s pip cache has a key, and nothing outside CI
  reads it. Locally, `pytest-xdist` is still optional (the push gate falls
  back to a serial fast lane without it) but CI now runs the parallel arm.
- Most sim entry points need `PYTHONPATH=.`. Codegen and tools run as
  `.venv/bin/python tools/<x>.py` (Windows: `.venv/Scripts/python`).
- `tools/` is an implicit namespace package: both `python3 tools/x.py` and
  `from tools import x` work.
- **The GitHub CLI IS installed** (`gh` 2.98.0, `C:\Program Files\GitHub CLI`,
  installed 2026-09-01; the older note that it was missing is retired). Auth is
  interactive and is [USER]'s one-time step: `gh auth login`. Once authed,
  Claude merges **plumbing** PRs itself on green CI with
  `gh pr merge <n> --merge` (merge commits, which is what this repo's history
  carries) and says so in the turn; a plumbing PR is defined in `CLAUDE.md`
  §Norms. Everything else is still PR = [USER]. `gh` never pushes to `main`,
  which stays rule-protected.
