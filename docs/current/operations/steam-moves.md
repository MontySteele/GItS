## When Steam moves the game

It will, without warning, on any branch. It did on 2026-08-28: a co-op session
had switched the app to `public-beta`, the install went v0.107.1 → v0.111.0,
and nothing C# compiled. [USER]'s reading of it is the reason this section
exists — *"This implies a patch update could also brick us."*

**Symptoms.** `dotnet build` fails with `CS0115` (an override overrides
nothing) or `CS1061` / `CS7036` on a game type; the game refuses the mod at
boot; `godot.log` records a version you did not pin. Confirm with
`release_info.json` in the install root, `BetaKey` and `buildid` in
`appmanifest_2868840.acf`, and `BaseLib.json` in the Workshop item — the four
facts `STATE.md`'s pin block carries.

**Keep building (`EB-172`).** The four referenced assemblies are mirrored to
the OneDrive vault beside `game_ref`:

```
python -m tools.backup_game_assemblies [--dry-run]   # mirror + write PIN.json
python tools/lint_game_assemblies_backup.py          # is it there and honest
dotnet build klee-mod/KleeCode/KleeCode.csproj -p:UsePinnedAssemblies=true
```

The switch is opt-in and never a default: a build silently taking a stale copy
while the machine has moved on is the failure this makes VISIBLE, not one it
should cause. It keeps the BUILD alive, not the game — a live run needs the
game, and no local copy fixes that.

**Do not opt the Steam branch back over on your own.** Which way the break is
repaired is a [USER] call (`M46`, ruled by R218): revert the branch, port and
re-pin, or keep a frozen copy.

**The port checklist**, in the order `EB-171` found them to matter:

1. **Decompile the new assembly first, do not guess from the error text.**
   `ilspycmd -p -o <outdir> "<GameDataDir>\sts2.dll"` (`~/.dotnet/tools`).
2. **Distrust the error count.** `CS0115` is a DECLARATION-stage diagnostic
   and Roslyn does not bind method bodies while declarations are broken. The
   0.111.0 port reported 15 errors, and fixing them revealed 123. Read "N
   errors" as "at least N".
3. **Hook signatures** — every `public override` against a game virtual.
4. **Threaded parameters** — a new trailing argument on one game API is
   usually the same argument on twenty (0.111.0 threaded `CardPlay?` through
   `ModifyDamage*`, `AttackCommand.FromCard` and the `CreatureCmd.Damage`
   family). Fix the GENERATOR (`tools/gen_klee_cards.py`) and regenerate, or
   `codegen-staleness` will bite.
5. **The vendored bridge** — `klee-mod\build\deploy_bridge.ps1 -BuildOnly`.
   Upstream STS2MCP may have no commit for the new game, in which case the
   repairs are MARKED LOCAL EDITS: `GItS LOCAL EDIT` in-file, a row in
   `vendor/STS2_MCP/PROVENANCE.md` "What we changed", then
   `python tools/lint_vendor_pin.py --write` and **read the diff** — only the
   files you touched may change.
6. **Re-verify live, do not infer.** Deploy (`klee-mod\build\deploy.ps1`),
   then run every `understudy/scenarios/` file and check the prototype
   quarantine still refuses a `KLEEMOD-PROTO_…` grant from outside.
7. **Move the pin deliberately** — `STATE.md`'s "Mod build environment
   (pinned)" block (version, commit, buildid, branch, `main_assembly_hash`,
   BaseLib, MegaDot, .NET SDK, ilspycmd), `min_game_version` in
   `klee-mod/Klee/manifest.json`, the environment table in
   `vendor/STS2_MCP/PROVENANCE.md`, and re-run the assembly mirror. Any
   decompile-sourced comment claiming a fact about the OLD build is a
   statement about that build: **re-sweep and keep both readings, never
   overwrite one** (`Diagnostics/SelectionTelemetry.cs` is the worked
   example). LAW R70: *latest is not a version.*

**Mod enablement.** The game's own on/off switches live in
`mod_settings.mod_list` inside
`%APPDATA%\SlayTheSpire2\steam\<steamid>\settings.save` (JSON, with a
`.backup` beside it). `[INFO] Skipping loading mod klee, it is set to disabled
in settings` in `godot.log` is what a disabled mod looks like. `klee` stays
ENABLED.
