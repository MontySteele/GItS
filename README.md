# GItS — Teyvat Spire

An unofficial, free fan mod for **Slay the Spire 2** that adds Genshin Impact
characters as playable heroes, plus a Spiral Abyss run mode. It is not made by
or affiliated with HoYoverse or Mega Crit.

## What's in it

| Character | Element | Plays like | Stage |
|---|---|---|---|
| Klee | Pyro | Places Bombs that grow each turn, then sets them off for big hits | Balance |
| Sangonomiya Kokomi | Hydro | Writes Plans that resolve next turn; jellyfish Stings and Wards | Prototype |
| Furina | Hydro | Spends her own HP for power; guest stars act at the end of her turn | Prototype |
| Varka | Anemo | A knight of every element who Swirls auras and builds Oath | Prototype |

Every character has a 78-card pool, their own relics and potions, and two
Ancient cards. All four share these systems:

- **Elemental reactions:** Pyro, Hydro, Cryo and Electro auras react the way
  they do in Genshin; Anemo Swirls them and Geo Crystallizes them.
- **Companion cards:** other Genshin characters show up as cards.
- **Spiral Abyss mode:** a fourth main-menu mode. Before each act's Ancient
  you take one of three Blessings, and the enemies take one of the Shadows
  you passed.

Co-op works. Everyone in the lobby must run the same build.

Characters move from Paper (a design brief) to Prototype (playable, being
tuned) to Balance (numbers settled). `docs/current/STATE.md` has each
character's current rules and next step.

## Repo layout

- `klee-mod/`: the C# mod. The name is historical; it holds every character.
  Cards are generated from `docs/prototype-surface.yaml` by
  `tools/gen_klee_cards.py`.
- `tier0/` and `tier05/`: a Python combat and run simulator that mirrors the
  mod's rules. It checks rules parity; balance is judged in the real game.
- `understudy/`: the harness that lets AI playtest seats play the real game.
- `tools/`: build, deploy, art and codegen scripts.
- `docs/` and `review/`: design docs and records. Start from `CLAUDE.md`,
  which routes each task to the one document it needs; `docs/README.md` is
  the index.

Tests: `python -m pytest -q` from the repo root runs the simulator suite, and
`python tools/gates.py --full --dotnet` runs everything, the C# tests
included.

## Building the mod

One-time setup:

1. The .NET SDK (the pinned version is in `docs/current/STATE.md`).
2. Slay the Spire 2, installed through Steam.
3. [BaseLib](https://steamcommunity.com/sharedfiles/filedetails/?id=3737335127),
   subscribed on the Steam Workshop. It is the mod's only dependency; the
   minimum version is in `klee-mod/Klee/manifest.json`.
4. Copy `klee-mod/local.props.example` to `klee-mod/local.props` and set
   `GameDir` (your game install) and `BaseLibDll` (the Workshop BaseLib.dll).
5. Art is not in the repo. The art pipeline writes it under
   `ImageGen/images/` (the art docs are in `docs/current/operations/`).
   Without it, cards fall back to placeholders.

Build and install with the game closed, since it locks the dll:

```powershell
python tools\deploy_round.py --dry-run   # shows what it will do
python tools\deploy_round.py             # rebuild the pck if stale, deploy, verify
```

This builds the `.pck` and stages a validated package under
`klee-mod/dist/klee/`. It copies the package to `<GameDir>/mods/klee/` and
installs the playtest bridge. Then it prints the installed version.

## Sharing a build

```powershell
cd klee-mod
.\build\deploy.ps1 -Package
```

This makes `klee-mod/dist/klee-v<version>.zip`, the validated package with art
and pck, rooted at `klee/`. Recipients:

1. Extract it into `<game>/mods/` so it lands as `mods/klee/`.
2. Subscribe to BaseLib (the version is in the manifest).
3. Be on at least the manifest's `min_game_version`.

Builds are shared privately for now. `docs/current/LAW.md` allows a free,
clearly unofficial public build with official art and no audio. When that
happens is still an open decision
(`review/active/distribution-readiness-2026-10-12.md`).
