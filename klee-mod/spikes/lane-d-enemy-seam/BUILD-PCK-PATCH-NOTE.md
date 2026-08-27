# Patch note — what this spike would need from shared files

Lane D owns its own directory and nothing else. `tools/build_pck.ps1`,
`klee-mod/build/*.ps1`, `klee-mod/KleeCode/` and `docs/current/` were **not
touched**. This is the change a single named owner would make later, written
down rather than made.

## 1. Packing the proof scene: no script edit is required

`tools/build_pck.ps1:730-737` overlays the git-tracked scene sources with a
wildcard:

```powershell
$pckSrc = Join-Path $repo 'klee-mod\pck-src'
Copy-Item (Join-Path $pckSrc '*') -Destination $work -Recurse -Force -Exclude 'README.md'
```

and the export preset is `export_filter="all_resources"`
(`tools/build_pck.ps1:101`). So the whole change is a **move**:

```
klee-mod/spikes/lane-d-enemy-seam/pck-src/laned/  ->  klee-mod/pck-src/laned/
```

After that the scene imports and exports with everything else and appears in
the derived `klee.pck.contract.txt` on its own. No line is added to
`build_pck.ps1`, no `resource=` literal is written (the contract is derived —
`test_the_pck_contract_is_derived_from_the_build_not_written_by_hand`), and
`validate.ps1`'s S6c stays satisfied because the change is additive.

**It is deliberately not done.** That move is the step that puts the proof art
into a shipped pack, and the pack is what a playtester sees. It waits on
[USER]'s answer to question 1 in the handoff note.

## 2. Loading the spike at runtime: also not done

The seam is a separate assembly (`laned-enemy-seam.dll`) and the game loads
exactly one DLL per mod (`ModManager`). To run it in game, one of:

- **(a)** move the two `.cs` files into `klee-mod/KleeCode/Patches/` so they
  build into `klee.dll`, and add the two classes to whatever `KleePatchBootstrap`
  already walks (it walks the assembly, so this is a file move plus nothing);
- **(b)** keep the assembly separate and load it as its own mod with its own
  manifest and pck.

**(a)** is smaller but immediately makes the spike a shipped feature and moves
it inside `klee-mod/KleeCode/`, which four gates scan
(`lint_constant_parity`, `lint_pool_membership`,
`test_roster_runtime_contracts`, and the codegen manifests). **(b)** keeps the
spike isolated but needs a second mod id, a second manifest, and a second pack.

Neither is a technical toss-up dressed as a preference: (a) is a scope
decision, so it is question 2 in the handoff note.

## 3. Nothing else is shared

- The bite-check is a new project under `klee-mod/spikes/`, not an edit to
  `klee-mod/build/bitecheck/`. That harness's `17 patch class(es) armed.`
  expectation is untouched, precisely because the spike's classes are in a
  different assembly.
- `tier0/tests/test_lane_d_enemy_seam.py` is a new file. It edits no existing
  test.
- `klee-mod/local.props` was created in this worktree (gitignored, machine
  local, `.gitignore:46`). It is not committed.
