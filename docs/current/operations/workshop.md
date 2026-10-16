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
`--skip-build`, `--pck`, `--images-root`, `--out` and (beta only)
`--telemetry-endpoint` are the options.

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

**Opt-in run stats (beta only, 2026-10-16).** [USER]: "go ahead and try to
build the opt-in upload now in the beta release so we can test drive the
telemetry before we spread it further." Add the deployed Worker's URL
(`telemetry-worker/README.md`, Deploy):

```sh
.venv/Scripts/python.exe tools/package_workshop.py --variant beta --version 0.3.0 \
    --telemetry-endpoint https://gits-telemetry.<account>.workers.dev
```

That builds with `-p:GitsTelemetryEndpoint=<URL>/v1/run` (the route is
appended if absent), which compiles `klee-mod/KleeCode/RunStats/`, and adds
the privacy paragraph to the description. Without the option the beta has
no uploader; `--variant public` refuses it, and dev, seat and test builds
never name the property, so they compile no RunStats file at all. The dll
check fails a `--skip-build` whose dll does not match (endpoint missing, or
present when not asked for). Every build now also carries
`-p:GitsVariant=<variant>`, read back as `WorkshopRelease.Variant`.

What the player sees: one tickbox, "Share anonymous run stats with the
Teyvat Spire developers", off by default, under Settings, Mod Configuration
(BaseLib), Open Config, Teyvat Spire Roster (BaseLib's config screen; it is
also on the main menu when BaseLib's own setting shows it there). It is
stored in `%APPDATA%/SlayTheSpire2/mod_configs/KleeMod.cfg` with the install
id, a random UUID v4 made the first time a run is sent and kept through
Restore Defaults. A run goes up only when the game calls
`ModManager.OnMetricsUpload` (its "Upload data" setting on, not abandoned,
not a first run, not a debug build) and the tickbox is on; the game setting
is read once more as a second belt. The record is schema v1, trimmed on the
game thread and posted on a pool thread: one try, 10 s timeout, failures
logged (`run stats:` in godot.log) and dropped, no retry queue.
`KleeTests/RunStatsTests.cs` and `tier0/tests/test_run_stats_record.py` are
the pins; `tools/telemetry_remote.py` reads what arrived.

**What [USER] runs**, after editing the description in `workshop.json`
(delete its DRAFT line) and checking `image.png`:

```
ModUploader.exe upload -w .workshop\public
```

The first upload creates the item and writes `mod_id.txt`; later uploads
update it. Co-op needs both players on the same version and the same variant.
Rebuild and re-upload after each game patch (the page names the branch).
