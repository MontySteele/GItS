---
name: deploy
description: Build and ship the Klee mod package - pre-deploy checks, build_pck, deploy (which validates before copying), and the opt-in C# suite. Use when staging a package into the game directory on the art-bearing main checkout.
---

# Deploy — build_pck, validate, deploy

PowerShell, from the repo root of the **art-bearing main checkout**.

1. **Check you are allowed to deploy from here.** A worktree has no art and no
   game paths; `build_pck`, `deploy` and art passes happen on the primary
   checkout only. From a worktree the one legal command is the bridge build,
   which lints the vendor pin, compiles into `klee-mod\dist\STS2_MCP`, touches
   no game directory, and skips the running-game refusal (a build holds no
   lock):

   ```
   klee-mod\build\deploy_bridge.ps1 -BuildOnly
   ```

2. **Close the game.** `deploy.ps1` refuses while the game holds the mod DLL.
   Machine paths come from `klee-mod/local.props` / `Directory.Build.props`.

3. **Prove the generated C# still matches the sheets** — a stale generator
   makes the pack disagree with the YAML it was built from:
   `.venv\Scripts\python tools\gen_roster_cards.py --check`

4. **Gate the tree before shipping it:**
   `.venv\Scripts\python -m pytest tier0/tests tier05/tests -q -n auto --dist
   loadscope` then `.venv\Scripts\python tools\run_lints.py --lane ci`. The
   `ci` lane is the real gate — it is exactly what `tools/hooks/push_gate.py`
   runs. A bare `run_lints.py` also runs the `local` lane, whose
   `card-distinctness --gate` exits 1 on `main` by construction (three curated
   known-failing breaches, carried in
   `tier0/tests/test_distinctness_gate.py`), so it can never read as a pass.

5. **Build the pack, ALWAYS before deploying.** After any roster-resource
   change an old Klee-only PCK cannot pass validation, and `deploy.ps1` rejects
   a missing, stale or mismatched contract. This writes the one
   character-aware pack plus `klee.pck.contract.txt`:

   ```
   tools\build_pck.ps1
   ```

6. **Deploy. `deploy.ps1` runs `validate.ps1` itself, before it copies
   anything** — the S-gate is not a step you can forget, only one you can skip
   by not deploying:

   ```
   klee-mod\build\deploy.ps1
   ```

7. **Validate alone** for the S-gate without shipping, and add the C# suite
   when the change is C#-side (opt-in, never a deploy gate):

   ```
   klee-mod\build\validate.ps1
   klee-mod\build\validate.ps1 -RunCsharpTests
   ```

8. **If S7 complains about `game_ref/`**, an incomplete local reference has
   failed validation by design. Do not stub it — restore it and run
   `python -m tools.backup_game_ref`. `-AllowIncompleteGameRef` is an
   acknowledgement, not a fix.
