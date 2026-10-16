## Steam Workshop packages

Ruled 2026-10-14 (`review/active/workshop-readiness-2026-10-14.md`, all (a)):
[USER] runs the uploader from his own Steam account, friends-only first, Yae
held back from the first upload. Claude prepares the workspace; nothing in
the repo uploads.

**Two variants.** `public`: mod id `klee`, Klee, Kokomi, Furina and Varka.
`beta`: mod id `klee-beta`, every kit (Yae included), title "(Beta)". Both
register the same card and character ids, so a player enables one. With both
enabled the loader fails the second one at its dll load (same assembly name)
and the first plays; that is read off the decompile, not yet seen live.
The beta's pck keeps `res://klee/`: the mod adds its own loc table, and its
Mods-screen badge shows blank.

**Make them.** On the main checkout (it has the pck and the card art), after
`tools/build_pck.ps1` if the pck is stale. It builds; it does not deploy, so
it is safe while the game runs.

```sh
.venv/Scripts/python.exe tools/package_workshop.py --variant public --version 0.3.0 --dry-run
.venv/Scripts/python.exe tools/package_workshop.py --variant public --version 0.3.0
.venv/Scripts/python.exe tools/package_workshop.py --variant beta   --version 0.3.0
```

`--version` is required and plain (`0.3.0`), never the dev `0.2.N+dirty`.
`--visibility` (private, public, unlisted, friends_only; default
friends_only), `--change-note`, `--image` (preview png, under 1 MB),
`--skip-build`, `--pck`, `--images-root` and `--out` are the options.

**What it writes**, under `.workshop/<variant>/` (gitignored):
`workshop.json` (title, the DRAFT description, visibility, changeNote, tags,
BaseLib's item 3737335127 as the dependency, minBranch/maxBranch null),
`image.png` (today the Mods-screen badge, which lacks Varka; a placeholder if
absent) and `content/<id>/` holding only `<id>.dll`, `<id>.pck`,
`manifest.json` and `images/cards/`. Never the seat bridge, never an
auto-play mod. A left-out kit's own card art stays out. `mod_id.txt`, which
ModUploader writes on the first upload, is kept by every later run.

**The release build.** `dotnet build -c Release -p:WorkshopRelease=true
-p:GitsKits=<kits joined by +>` into `.workshop/_build/<variant>/`, so the
dev `bin/Release` is untouched. `WorkshopRelease` defines `WORKSHOP_RELEASE`:
play telemetry writes only when `GITS_TELEMETRY_FEED` is set (seat lanes set
it), so a player gets no `gits_telemetry` folder. Dev and seat deploys name
neither property and keep writing, [USER]'s own play included (the `human`
feed). `GitsKits` leaves a kit's character unregistered, and with it its pool,
relics, starter and Ancients; its code still compiles, so saves holding its
ids still load. Universal Companions stay. `klee-mod/KleeCode/ReleaseVariant.cs`
and `Patches/ReleaseKitsPatch.cs` are the code; `KleeTests/ReleaseVariantTests.cs`
and `tier0/tests/test_package_workshop.py` the pins.

**What [USER] runs**, after editing the description in `workshop.json`
(delete its DRAFT line) and checking `image.png`:

```
ModUploader.exe upload -w .workshop\public
```

The first upload creates the item and writes `mod_id.txt`; later uploads
update it. Co-op needs both players on the same version and the same variant.
Rebuild and re-upload after each game patch (the page names the branch).
