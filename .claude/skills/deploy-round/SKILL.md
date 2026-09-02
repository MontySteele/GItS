---
name: deploy-round
description: Decide and drive one dev deploy - rebuild the pck only if its sources moved, run deploy_proto with the arm switches, then verify the installed version, the bridge and the staged image count off disk. Use before any round that needs a +proto build in the game.
---

# deploy-round — pck if stale, deploy_proto, then read it back

```sh
python tools/deploy_round.py --arms klee,companion,kokomi --dry-run   # decide
python tools/deploy_round.py --arms klee,companion,kokomi             # do it
python tools/deploy_round.py --arms klee --pck        # force the pck rebuild
```

**Always `--dry-run` first**: it prints the pck decision and its reason, the
arms, whether the game is up, the commands, and the three verification lines.

## The two decisions it takes for you

- **Is the pck stale?** It is built from `ImageGen/images/**` and
  `klee-mod/pck-src/**`, both invisible to `git status` — so deploying without
  rebuilding ships a package one art build behind and nothing says so. Mtimes
  are compared and the answer is printed with its reason.
- **Which arms?** `klee` / `companion` / `kokomi` / `furina` map to
  `deploy_proto.ps1`'s own switches; they are independent and the supported dev
  build carries all of them.

## What it refuses

- **Not the main checkout.** A worktree has no `ImageGen/images`, so the deploy
  succeeds with a WARNING and stages no art. The hook
  `deny_deploy_outside_main.py` is the hard stop; this explains it.
- **A game process running**, by image name: one install means one deployed
  build for *every* lane, so a second lane's game holds the same lock on
  `klee.dll`. Tear the lane down, never deploy around it.

Verify by the three printed lines, not by the script's own success message: the
installed version from `mods\klee\manifest.json`, whether `mods\STS2_MCP` is
there, and the staged card-image count. A `+proto` version string is how a dev
build is identified on sight; go back with `klee-mod\build\deploy.ps1`.
