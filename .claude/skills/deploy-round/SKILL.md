---
name: deploy-round
description: Decide and drive one round's deploy - rebuild the pck only if its sources moved, deploy the release build (the current kits) plus the bridge, then verify the installed version, the bridge and the staged image count off disk. Use before any round or play session that needs the current build in the game.
---

# deploy-round — pck if stale, deploy, then read it back

```sh
python tools/deploy_round.py --dry-run        # decide
python tools/deploy_round.py                  # do it
python tools/deploy_round.py --pck            # force the pck rebuild
python tools/deploy_round.py --arms teyvat    # a +proto dev build (frame on hold)
python tools/deploy_round.py --staging        # a +next build of a <kit>-next branch
```

**Always `--dry-run` first**: it prints the pck decision and its reason, the
arms, whether the game is up, the commands, and the three verification lines.

**The current kits are the release build** (2026-09-28; [USER]: "make all 3
current builds the active release builds"). With no `--arms` this runs
`klee-mod\build\deploy.ps1` (Klee's overhaul, the companion overhaul, Kokomi's
overhaul and Furina's Stage, unmarked), then `deploy_bridge.ps1`, the harness a
seat needs. The old arm names (`klee`, `companion`, `kokomi`, `furina-stage`)
are accepted and dropped with a note. Only `teyvat` goes through
`deploy_proto.ps1` and a `+proto` stamp.

- **Is the pck stale?** It is built from `ImageGen/images/**` and
  `klee-mod/pck-src/**`, both invisible to `git status`; mtimes are compared
  and the answer is printed with its reason.
- **Refuses outside the main checkout** (no art there; the hook
  `deny_deploy_outside_main.py` is the hard stop) and **while any game process
  runs** (one install is one deployed build for every lane; tear lanes down).

Verify by the three printed lines, not by the script's own success message: the
installed version from `mods\klee\manifest.json`, whether `mods\STS2_MCP` is
there, and the staged card-image count. A `+proto` version marks a dev build
that differs from the release; go back with `python tools/deploy_round.py`.

**Staging (2026-10-05).** A Balance kit is frozen on `main` between suite runs; its changes are played from `<kit>-next`. `--staging` refuses unless the main checkout is on a `*-next` branch with a clean tracked tree, then deploys the release build stamped `+next`; the verify lines name the branch.
