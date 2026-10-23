## Steam Workshop packages

Ruled 2026-10-14 (`review/active/workshop-readiness-2026-10-14.md`, all (a)):
[USER] runs the uploader from his own Steam account, friends-only first, Yae
held back from the first upload. Claude prepares the workspace; nothing in
the repo uploads.

**The name (2026-10-22).** In game (mod list, config page, manifest name) the
mod is "Teyvat Spire". The Workshop titles are "Teyvat Spire: Genshin Impact
Characters" (public, so search finds "Genshin") and "Teyvat Spire (Beta)".
[USER]: "let's do 1) as a quick cleanup for "Teyvat Spire" and then leave
the others alone", then, on putting Genshin in the public title: "Let's do
that". A bare "Genshin Spire" was passed over: it reads as official and sits
next to an existing mod, GenshinSpire2. The mod ids (`klee`, `klee-beta`),
the `KLEEMOD-` keys and the repo name GItS stay, because saves, run history,
co-op matching and run stats hold them. The titles may change again after
the beta testers weigh in ("I'll ask the beta testers for their opinions").

**Two variants.** `public`: mod id `klee`, Klee, Kokomi, Furina and Varka.
`beta`: mod id `klee-beta`, every kit (Yae included), title "(Beta)". Both
register the same card and character ids, so a player enables one. With both
enabled the loader fails the second one at its dll load (same assembly name)
and the first plays (seen on lane 1, 2026-10-22: the beta loads first, the
dev `klee` fails "already loaded", and the menu shows red "Loaded 3 mods
WITH ERRORS!").
The beta's pck keeps `res://klee/`: the mod adds its own loc table, and its
Mods-screen badge shows blank.

**Save safety (ruled 2026-10-22).** Lane tests found two ways to lose a
run: turning the mod off with a run open (BaseLib hides it and the next new
run overwrites it), and a package that does not register a character (a beta
Yae run under the public package). [USER]: "1) I think it's the user's
responsibility to know you can't turn a mod off and still play the game. If
we can back up the run save, that would be ideal (the same way the public vs
beta branches of the game would do it). 2) As above, can we separate the save
files somehow? 3) Beta testers need to just be careful about this and we can
put a reminder on the beta page; public users shouldn't need a warning."
Built (`klee-mod/KleeCode/Saves/`, pinned by `KleeTests/SaveSafetyTests.cs`):

- **The beta's own save folder.** The game keeps modded play in
  `steam/<id>/modded/` (vanilla at the account root). The beta package
  renames that one folder to `modded-teyvat-beta/` (a postfix on
  `UserDataPathProvider.GetAccountDir`, which every save path and every Steam
  cloud path goes through). Public, dev and seat builds keep `modded/`. On the
  first beta boot, after the cloud sync and before profile.save is read, the
  mod copies profile.save, progress, prefs, run saves and run history across
  once; the `modded/` folder is never written. With cloud sync on, the copy
  goes through the game's own store (local and cloud, history under the
  game's 5 MB / 100-file quota), because the next sync deletes any local
  save file the cloud lacks. Turning the beta off simply puts the game back
  on `modded/`.
- **The Teyvat run backup.** Each run save that holds one of our characters
  is copied, local only, to `current_run.teyvat.save` (or
  `current_run_mp.teyvat.save`) beside it. With the mod on again and no run
  open, the backup goes back as the run save, unless the run is in the run
  history or this build does not register one of its characters. It never
  writes over an open run. When the game deletes a run save (run ended or
  abandoned, history already written), the backup goes with it if it is the
  same run (start time); if it was another run, the backup is restored then.
  Limit: the mod-off run still rewrites progress.save and drops our
  characters' rows in ancient, encounter and enemy stats; those do not come
  back.
- **The beta page** says to enable it or the main release, never both, and
  that it keeps its own save folder. The public page carries no save warning.

Seen on lane 1 (2026-10-22): a Furina run backed up on Continue; with `klee`
off, a new Ironclad run overwrote and then abandoned the run save; with
`klee` on, the log read "restored the Teyvat run" and Continue loaded the
Furina run at act 2 floor 8. Abandoning it with the mod on removed the
backup. A beta-variant dll copied 265 files into `modded-teyvat-beta/`, the
profile path read `modded-teyvat-beta/profile1`, the next save landed there
and `modded/` was byte-identical. Not seen: the cloud-on copy (lanes run with
Steam cloud off for the app) and a co-op host's restore.

**Make them.** On the main checkout (it has the pck and the card art), after
`tools/build_pck.ps1` if the pck is stale. It builds; it does not deploy, so
it is safe while the game runs.

```sh
.venv/Scripts/python.exe tools/package_workshop.py --variant public --version 0.3.0 --telemetry-endpoint https://gits-telemetry.gits-telemetry-worker.workers.dev --dry-run
.venv/Scripts/python.exe tools/package_workshop.py --variant public --version 0.3.0 --telemetry-endpoint https://gits-telemetry.gits-telemetry-worker.workers.dev
.venv/Scripts/python.exe tools/package_workshop.py --variant beta   --version 0.3.0 --telemetry-endpoint https://gits-telemetry.gits-telemetry-worker.workers.dev
```

`--version` is required and plain (`0.3.0`), never the dev `0.2.N+dirty`.
`--visibility` (private, public, unlisted, friends_only; default
friends_only), `--change-note`, `--image` (preview png, under 1 MB),
`--skip-build`, `--pck`, `--images-root` and `--out` are the options. Every
run, dry runs and `--skip-build` included, needs exactly one of
`--telemetry-endpoint URL` or `--no-telemetry` (Run stats, below).

**What it writes**, under `.workshop/<variant>/` (gitignored):
`workshop.json` (title, the DRAFT description, visibility, changeNote, tags,
BaseLib's item 3737335127 as the dependency, minBranch/maxBranch null),
`image.png` (`ImageGen/images/workshop_preview.png`, the five idle renders,
made by `tools/make_workshop_preview.py`; a placeholder if absent) and `content/<id>/` holding only `<id>.dll`, `<id>.pck`,
`manifest.json` and `images/cards/`. Card portraits go up as lossless WebP
(same pixels, about 29% smaller, checked file by file; a file that fails the
check ships as its png), and `RosterArt.CardPortrait` tries `<id>.webp`, then
`<id>.png`. Verified encodes are cached in `.workshop/_webp_cache/` by the sha256 of the source png, and misses encode on every core, so a repackage with no new art copies instead of re-encoding (2026-10-17). The dev deploy and the art tools stay on png. Never the seat
bridge, never an auto-play mod. A left-out kit's own card art stays out. `mod_id.txt`, which
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

**Run stats (beta 2026-10-16; default on 2026-10-18; public too 2026-10-21).** [USER]: "go ahead and try to
build the opt-in upload now in the beta release so we can test drive the
telemetry before we spread it further." On 2026-10-21 he ruled the public
variant in: "Include the telemetry as opt-out." Both variants take the same
option and ship the same tickbox, on by default. Add the deployed Worker's URL
(`telemetry-worker/README.md`, Deploy; today
`https://gits-telemetry.gits-telemetry-worker.workers.dev`). It stays an
option, never a constant in the code, but the choice is required: the tool
refuses to run unless it gets either `--telemetry-endpoint URL` or
`--no-telemetry`, because beta 0.3.11 and 0.3.12 went out with the option
left off and no run uploaded:

```sh
.venv/Scripts/python.exe tools/package_workshop.py --variant beta --version 0.3.0 \
    --telemetry-endpoint https://gits-telemetry.gits-telemetry-worker.workers.dev
.venv/Scripts/python.exe tools/package_workshop.py --variant public --version 0.3.0 \
    --telemetry-endpoint https://gits-telemetry.gits-telemetry-worker.workers.dev
```

The upload sends `User-Agent: TeyvatSpire/<mod version> (+telemetry)`:
Cloudflare's bot screen in front of the Worker answers 403 to some library
defaults (`Python-urllib`) and 204 to a named client. A 403, like any other
failure, is logged and dropped.

That builds with `-p:GitsTelemetryEndpoint=<URL>/v1/run` (the route is
appended if absent), which compiles `klee-mod/KleeCode/RunStats/`, and adds
the privacy paragraph to the description. With `--no-telemetry` a package has
no uploader, and dev, seat and test builds never name the property, so
they compile no RunStats file at all. The dll
check fails a `--skip-build` whose dll does not match (endpoint missing, or
present when not asked for). Every build now also carries
`-p:GitsVariant=<variant>`, read back as `WorkshopRelease.Variant`.

What the player sees: one tickbox, "Share anonymous run stats with the
Teyvat Spire developers", **on by default** since 2026-10-18 ([USER], asked
whether the page's disclaimer was enough instead of opt-in: "Let's go default
on."), switchable off in the same place, under Settings, Mod Configuration
(BaseLib), Open Config, Teyvat Spire (BaseLib's config screen; it is
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
the pins; `tools/telemetry_remote.py` reads what arrived. A record names its
variant (`beta` or `public`, `schema/run-v1.json`), so the two can be read
apart.

Existing beta installs keep their saved choice ([USER]: "2) is fine on the
telemetry flip - we currently only have 2 people testing it."). BaseLib keeps
a saved value over a changed default (`ModConfig.Init` captures the code
default, then `Load` applies the file), so the new default reaches new
installs only; an install that ran the opt-in beta stays at its saved
`"ShareAnonymousRunStats"` value until the player changes it. Restore
Defaults now restores on.

The page's run-data paragraph (default on), as `PRIVACY_PARAGRAPH` in
`tools/package_workshop.py` writes it (paste it over the old "Run data
(optional)" paragraph in the saved description). The public page gets the
same text with "This mod sends" for "This beta sends" (`privacy_paragraph`):

> Run data. This beta sends a short summary of each finished run to the Teyvat Spire developers: your character, ascension, result, the cards and relics you ended with, which cards you were offered and took, and your HP floor by floor. It holds no Steam id, name, chat or other personal details, and your IP address is not stored. Runs are tied only to a random id made by the mod on your machine. Data is used to balance the mod and deleted after a year. It is on by default; turn it off any time with "Share anonymous run stats with the Teyvat Spire developers" under Settings, Mod Configuration (BaseLib), Open Config, Teyvat Spire. It only sends when the game's own "Upload data" setting is on.

**What [USER] runs**, after editing the description in `workshop.json`
(delete its DRAFT line) and checking `image.png`:

```
ModUploader.exe upload -w .workshop\public
```

The first upload creates the item and writes `mod_id.txt`; later uploads
update it. Co-op needs both players on the same version and the same variant.
Rebuild and re-upload after each game patch (the page names the branch).
