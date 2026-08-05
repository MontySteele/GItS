# Spine probe (Track M, M-Q3) — throwaway

One question: **does a `.tscn` naming `SpineSprite` / `SpineSkeletonFileResource`
/ `SpineAtlasResource` survive our pack build and load in-game, when the MegaDot
4.5.1 editor that builds the pack has no spine support at all?**

Findings live in `docs/animation-downfall-investigation-2026-08-05.md`. This
directory is the apparatus, kept so the result is reproducible and so the undo
is a script rather than a memory. It is wired into nothing: no lint, no gate, no
`build_pck.ps1` change, no CI.

## Rules this probe obeys

- **The rig is borrowed, never committed.** `make_probe_project.py` copies one
  base-game rig out of `SlayTheSpire2.pck` into a scratch directory and
  *refuses* to write anywhere inside the repo. `cleanup_probe.ps1` deletes it.
- **One new folder in the game directory, ever**: `<GameDir>\mods\spineprobe`.
  Nothing existing is edited. `deploy_probe.ps1` records a reversibility
  baseline first; `cleanup_probe.ps1` checks it.
- **The probe adds nothing to a run.** It loads three scenes, prints, and
  parents one node to the menu root so a human can say whether anything drew.

## Phase 1 — offline (no game process)

```
$SCRATCH = "<somewhere outside the repo>\probe"
.venv\Scripts\python.exe tools\probe_spine_pck\make_probe_project.py --out $SCRATCH
powershell -File tools\probe_spine_pck\build_probe_pck.ps1 -ProjectDir $SCRATCH
```

Exports the same scratch project twice: `strict` (the preset
`tools/build_pck.ps1` writes, verbatim) and `wide` (same plus
`include_filter="*.skel,*.atlas,*.spskel,*.spatlas"`), then lists both packs.
The difference between the two is the whole experiment at the packing layer.

## Phase 2 — in-game (needs the game window)

```
dotnet build tools\probe_spine_pck\SpineProbe\SpineProbe.csproj -c Release
powershell -File tools\probe_spine_pck\deploy_probe.ps1 -ProjectDir $SCRATCH
start steam://rungameid/2868840     # NEVER SlayTheSpire2.exe directly
# reach the main menu, quit
#   %APPDATA%\SlayTheSpire2\logs\godot.log  ->  lines tagged [spineprobe]
powershell -File tools\probe_spine_pck\cleanup_probe.ps1 -ProjectDir $SCRATCH
```

**Launch through Steam.** Running the exe directly makes it write
`steam_appid.txt` into the install root. That file does **not** ship with the
game, and a killed session leaves it behind for the next one to mistake for
pre-existing state. `cleanup_probe.ps1` removes any copy it finds, whoever made
it; the correct end state is absent.

**Runs park under `steam\<id>\profileN\saves`**, not `default\1`. The cleanup
check walks every profile, and distinguishes run files from
`settings`/`prefs`/`progress`/`profile` state — the game rewrites
`settings.save` on every quit, and calling that "a run was left behind" is a
false alarm on a clean session.

### Observables, decided in advance

| Line | Meaning if false/absent |
|---|---|
| `EXISTS=` | the pack build dropped the file — a packing failure, not a type failure |
| `LOADED=` | the scene did not parse — type resolution failed at load |
| `ROOT=SpineSprite` | the type resolved but the node is not what the scene said |
| `SKELETON data_loaded=` | types resolved, data did not — the silent no-render mode |
| `ATTACHED` + eyes on screen | everything resolved but nothing draws |

Three arms make the answer attributable: `probe_control.tscn` (plain `Sprite2D`)
fails only if the pack or the mount is broken; `probe_raw.tscn` uses
`.skel`/`.atlas`; `probe_imported.tscn` uses `.spskel`/`.spatlas`.
