## Build & deploy (Windows, art-bearing main checkout only)

**The sequence is the `deploy` skill** — pre-deploy checks, `build_pck.ps1`,
`deploy.ps1` (which runs `validate.ps1` itself before copying), and the opt-in
C# suite. From a worktree the one legal command is
`klee-mod\build\deploy_bridge.ps1 -BuildOnly` (`EB-142`).
