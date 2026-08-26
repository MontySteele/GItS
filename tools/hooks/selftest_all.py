#!/usr/bin/env python3
"""Run every hook's `--self-test`, so the enforcement layer is itself gated.

The hooks under `tools/hooks/` are the only code in this repo that no test
imports and no lint reads: they run in the harness, out of process, on stdin
JSON. A refusal that silently stopped refusing -- a rename, a shlex edge, a
`git` flag spelled a new way -- would look exactly like a session that simply
never tried the forbidden thing. This wrapper is what puts them under the same
gate as everything else: it is registered in `tools/run_lints.py`'s `ci` lane,
which is the lane `push_gate.py` itself runs, so the hooks are re-proved on
every push.

    python tools/hooks/selftest_all.py

Exit 1 if any hook's self-test fails, or if a hook script has no self-test.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
REPO = HOOKS.parents[1]


def hook_scripts() -> list[Path]:
    """Every hook script. Globbed, not listed: a hook added without a
    self-test must FAIL here rather than be quietly skipped."""
    return sorted(p for p in HOOKS.glob("*.py")
                  if p.name not in ("_hooklib.py", "selftest_all.py"))


def main() -> int:
    scripts = hook_scripts()
    if not scripts:
        print("VACUOUS: no hook scripts found at all. This is reporting "
              "nothing, not health.")
        return 1

    failed: list[str] = []
    for script in scripts:
        proc = subprocess.run(
            [sys.executable, str(script), "--self-test"],
            cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="replace")
        summary = next((line for line in proc.stdout.splitlines()
                        if line.startswith("self-test:")), "")
        if not summary:
            failed.append(f"{script.name}: NO SELF-TEST -- every hook must be "
                          f"able to prove it still bites")
            continue
        status = "ok  " if proc.returncode == 0 else "FAIL"
        print(f"  [{status}] {script.name:<32} {summary}")
        if proc.returncode != 0:
            failed.append(f"{script.name}: {proc.stdout.strip()}")

    print(f"\nhook self-tests: {len(scripts)} hook(s), {len(failed)} failing")
    for line in failed:
        print(f"  {line}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
