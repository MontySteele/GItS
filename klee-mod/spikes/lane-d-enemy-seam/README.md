# Lane D — neutral enemy presentation seam (spike)

> **Decides nothing.** Whether any base enemy should ever be re-presented,
> which one, and what it should look like are [USER]'s calls. This directory
> establishes only that the *seam exists and behaves*. It is not wired into any
> build, deploy or pack script, and nothing in it reaches a playable build.

## What is here

| Path | What it is |
|---|---|
| `EnemySeamSpike/NeutralEnemySeam.cs` | The seam: two Harmony prefixes on `MonsterModel`, gated on one monster id. |
| `EnemySeamSpike/SeamBootstrap.cs` | Per-type patch application + report, same shape as `KleeCode/KleePatchBootstrap.cs`. |
| `bitecheck/Program.cs` | Offline evidence harness. Runs the seam against the real `sts2.dll` outside Godot. |
| `pck-src/laned/creature_visuals/proof_prism.tscn` | The proof art: original geometry, drawn as `Polygon2D` vertices in the file. No texture, no import, no script. |
| `BUILD-PCK-PATCH-NOTE.md` | The shared-file change this spike would need, written down instead of made. |

The automated half of the gate is `tier0/tests/test_lane_d_enemy_seam.py`,
which runs everywhere. This harness is the manual half, because it needs the
Steam install and the Workshop BaseLib — the same split as
`klee-mod/build/bitecheck`.

## Commands

```sh
# build the spike assembly
cd klee-mod/spikes/lane-d-enemy-seam/EnemySeamSpike && dotnet build

# build and run the offline evidence harness
cd klee-mod/spikes/lane-d-enemy-seam/bitecheck && dotnet build
./bin/Debug/laned-seam-bitecheck.exe

# the half that runs without a game install
PYTHONPATH=. python -m pytest tier0/tests/test_lane_d_enemy_seam.py -q
```

`local.props` must exist under `klee-mod/` (gitignored; copy
`local.props.example`). Both projects inherit `GameDataDir` and `BaseLibDll`
from it through `klee-mod/Directory.Build.props`, so no Steam path appears in
either `.csproj`.

## What the harness proves, and what it cannot

It loads the real game assembly, arms **BaseLib's own** `VisualsPath` and
`CreateVisuals` patch classes, then arms the spike's, and reads
`MonsterModel.VisualsPath` back on **every concrete monster in the base game**.

Expected on an unmodified tree:

```
monsters swept        120
  claimed by seam     1
  base path intact    119
  UNEXPECTED value    0
declare own getter    6 (BigDummy, MockArtifactMonster, ...)
RESULT: all checks passed.
```

`120 / 1 / 119 / 0` is the number to compare against.

It **cannot** render anything. No `PackedScene` is parsed, no
`NCreatureVisuals` is built, no pack is loaded. Godot is not running. Every
claim it makes is about strings and method dispatch. The visual half is the
live procedure in `review/dispatch3/tooling-laned-handoff.md`.

## Running an actual bite-check

Break exactly one thing, rebuild, re-run, read the report. Two cases run on
2026-08-26:

| Break | Expected | Observed |
|---|---|---|
| Drop the id term from `Claims` (`&& string.Equals(model.Id.Entry, TargetEntry, …)`) | the sweep flips to 1 claimed / 0 intact / 119 UNEXPECTED, each casualty named, exit 1 | as expected |
| Point `ProofScenePath` at `res://scenes/creature_visuals/nibbit.tscn` | the namespace check fails; the Python gate fails first, on two tests | as expected |

The first is the important one. A prefix that forgets its id guard re-skins the
entire bestiary and **still boots, still fights, and logs nothing** — it is a
defect with no symptom short of looking at every enemy. The sweep is the
symptom.

## Design notes worth keeping

- **Two patches, not one.** `VisualsPath` (S13-a4) is what the combat
  *preloader* reads, so patching it is what gets the replacement scene warmed
  with the rest of the fight's assets. `CreateVisuals` (S13-a5) is what builds
  the node; it is patched as well so the result does not depend on BaseLib's
  path-keyed scene-conversion registry having been primed.
- **`Priority.Low` on both prefixes.** BaseLib patches the same two members at
  default priority and falls through for anything that is not a
  `CustomMonsterModel`. Harmony stops running prefixes once one returns false,
  so running last is what makes another mod's monster resolve to its owner and
  never to this spike. The harness reads the prefix owners off
  `Harmony.GetPatchInfo` and asserts both are present.
- **Six base monsters are unreachable this way.** `BigDummy` and the five
  `Mock*` monsters declare their own `VisualsPath` override, so virtual
  dispatch never reaches the patched base getter. A seam that had to cover them
  would need a per-type patch, not a base-type one. None of the six is an
  ordinary encounter enemy.
- **Everything degrades to base art.** No pack, unresolvable path, or a throw
  while building the node all end with the original method running. The engine
  then has its own `try/catch` that falls back to
  `res://scenes/creature_visuals/fallback.tscn` — a visible error scene and a
  `Log.Error`, not a crash.
