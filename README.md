# GItS — Teyvat Spire

A Genshin-flavored playable roster (Klee, Furina, elemental reactions,
Companion cards) for **Slay the Spire 2**, designed simulation-first:

- `tier0/` — Python combat simulator (engine, card DSL, 7-axis scorecard).
  Run the full test suite from the repo root: `python -m pytest -q`.
- `tier05/` — draft/run-layer simulator on top of tier0.
- `klee-mod/` — the actual C# mod. Design sheets in `docs/*.yaml` are the
  single source of truth; the sims read them directly.

## Building the mod

Prerequisites (one-time):

1. .NET SDK (the mod targets the game's bundled runtime; `dotnet build` is
   driven for you by the deploy script).
2. Slay the Spire 2 installed (Steam).
3. [BaseLib](https://steamcommunity.com/sharedfiles/filedetails/?id=3737335127)
   subscribed on the Steam Workshop (the mod's only dependency — see
   `klee-mod/Klee/manifest.json` for the minimum version).
4. Copy `klee-mod/local.props.example` to `klee-mod/local.props` and set
   `GameDir` (your game install) and `BaseLibDll` (the workshop BaseLib.dll).
5. Card art is not in the repo (see `.gitignore` — Tier F art never ships
   publicly). The art pipeline's output is expected under
   `ImageGen/images/cards/`; without it, cards fall back to placeholders.
6. The character-select `.pck` is also built locally:
   `klee-mod/tools/build_pck.ps1`.

Build, validate, and deploy into the game's `mods/` folder (game must be
closed — it holds a lock on the dll):

```powershell
cd klee-mod
.\build\deploy.ps1
```

This stages a clean package under `klee-mod/dist/klee/` (manifest + dll +
card art + pck), runs the static conformance checks in `build/validate.ps1`
against exactly that staged package, and only then copies it to
`<GameDir>/mods/klee/`.

## Packaging a handoff zip (co-op / friends)

```powershell
cd klee-mod
.\build\deploy.ps1 -Package
```

This produces `klee-mod/dist/klee-v<version>.zip` — the exact validated
package, art and pck included, with `klee/` as the archive root. The version
in the filename is read from the staged manifest.

Recipients:

1. Extract the zip into `<game>/mods/` so it lands as `mods/klee/`.
2. Subscribe to BaseLib on the Steam Workshop (version per the manifest).
3. Be on a game build at least the manifest's `min_game_version`.

Rules of the road:

- **Co-op is deterministic lockstep.** Everyone in a lobby must run the
  *same* zip (and the same BaseLib) or the game will detect state
  divergence. Bump the `version` in `klee-mod/Klee/manifest.json` before
  every handoff so mismatches are visible in the filename.
- **Hand the zip off privately** (DM, drive share). It contains the scraped
  Tier F art, which is never distributed publicly — same reason
  `ImageGen/images/`, `dist/`, and `*.zip` are all gitignored.
