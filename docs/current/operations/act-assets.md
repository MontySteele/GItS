## Act assets (a zone dressing's own background, rest site and map art)

Scope: the files an `ActModel` needs so the game's own loaders are satisfied
without borrowing another zone's. Read this when a dressing is added, when an
act asset moves, or when a dressed run throws out of `BackgroundAssets`.

```powershell
# regenerate the whole placeholder set (art-bearing main checkout)
.venv\Scripts\python.exe tools\gen_act_placeholders.py
.venv\Scripts\python.exe tools\gen_act_placeholders.py --check   # staleness gate
.venv\Scripts\python.exe tools\gen_act_placeholders.py --list    # the res:// rows
powershell -File tools\build_pck.ps1                             # then the pack
```

### The shape

Every path derives from `ActModel.FilePathIdentifier`, which is
`Id.Entry.ToLowerInvariant()` — `MONDSTADT` → `mondstadt`. The five properties
over it are **non-virtual** (`ActModel.cs:52-64`, `:248`), so a subclass cannot
move a single one of them: the file is at the derived path, or it is nowhere.

| What | Path (`<id>` = the lowercased `Id.Entry`) | Count | Size | Root node the engine casts to | Fallback if missing |
|---|---|---|---|---|---|
| Background layer scene | `res://scenes/backgrounds/<id>/layers/<id>_bg_NN_x.tscn` | 5 groups × ≥1 variant | — | `Control` (ours: `TextureRect`) | **none — throws** |
| Foreground layer scene | `res://scenes/backgrounds/<id>/layers/<id>_fg_x.tscn` | ≥1 | — | `Control` | none (fg may be absent, but a *badly named* file throws) |
| Layer plate | `res://teyvat/backgrounds/<id>/<id>_bg_NN.png`, `…_fg.png` | 6 | 1382×648 | — | dangling `ExtResource` |
| Background root scene | `res://scenes/backgrounds/<id>/<id>_background.tscn` | 1 | — | **`NCombatBackground`** | **none — cast throws** |
| Rest-site scene | `res://scenes/rest_site/<id>_rest_site.tscn` | 1 | — | `Control`, must carry `%RestSiteLighting` | **none — throws** |
| Rest-site plate | `res://teyvat/rest_site/<id>_rest_site_bg.png` | 1 | 1382×648 | — | dangling `ExtResource` |
| Map backgrounds | `res://images/packed/map/map_bgs/<id>/map_{top,middle,bottom}_<id>.png` | 3 | 2035×1440 | — | **none — throws** |
| Act title | loc table `acts`, key `<Id.Entry>.title` | 1 row | — | — | renders the raw key |
| Map colours | `MapTraveledColor` / `MapUntraveledColor` / `MapBgColor`, `abstract` on `ActModel` | 3 | — | — | compile error |

Eighteen files a dressing, plus one loc row and three colours that live in C#.

**The five rules underneath the table**, each of them a throw if broken:

1. `BackgroundAssets`'s constructor (`Rooms/BackgroundAssets.cs`) opens
   `res://scenes/backgrounds/<id>/layers` with `DirAccess` and throws
   `InvalidOperationException` if the directory is absent, if it holds a
   subdirectory, or if **any** file there matches neither `_bg_` nor `_fg_`.
2. It groups the `_bg_` files by the segment after `_bg_` (`00`, `01`, …),
   sorts the groups by that key, and draws **one file per group** with
   `rng.NextItem`, then makes **one further draw** over the `_fg_` list. The
   number of draws is therefore the number of groups plus one, whatever the
   variant count — so a dressing that keeps the base zone's **group count**
   consumes the base zone's rng identically. Overgrowth and Underdocks both
   ship `bg_00`..`bg_04` plus a foreground; so do both dressings.
3. `NCombatBackground.Create` instantiates the background root and **casts** it
   to `NCombatBackground`, then calls `GetNodeOrNull("Layer_00")` ..
   `Layer_{n-1}` for the chosen layers and `"Foreground"` for the fg, throwing
   on a miss. The root scene needs those six child nodes by plain name.
4. `NRestSiteRoom._Ready` does `control.GetNode<Control>("%RestSiteLighting")`
   — `GetNode`, not `GetNodeOrNull` — so the rest-site scene must carry a node
   with that name and `unique_name_in_owner = true`.
5. `ActModel.AssetPaths` hands the background scene and all three map PNGs to
   `PreloadManager.LoadActAssets`, so a missing one fails the act's preload
   rather than the screen that draws it.

### The root scene is the only one that needs BaseLib

A mod pck cannot carry an `ext_resource type="Script"` row (the `SD-SCRIPT`
rule; scripts do not ship in a mod pack, and `NCombatBackground`'s own script
is the game's, at `res://src/Core/Nodes/Rooms/NCombatBackground.cs`). So the
background root is a script-less `Control` and BaseLib's scene conversion turns
it into an `NCombatBackground` on instantiation — the EB-760 mechanism the
still portrait already uses, with one extra step: **BaseLib ships six node
factories and none of them is for this type**, so
`klee-mod/KleeCode/Teyvat/NCombatBackgroundFactory.cs` supplies the missing one
and `TeyvatActAssets.RegisterActBackgrounds` builds it and registers the two
scenes at `[ModInitializer]` time. Everything else in the table — layer scenes,
the rest site — is instantiated as a plain `Control` and needs no conversion at
all.

### The placeholder recipe

`tools/gen_act_placeholders.py` writes two-stop vertical gradients in the
nation's colours (Mondstadt sky-blue over meadow green, Liyue amber over
stone), darkening each layer toward the foreground so five flat plates read as
five planes. It writes **only** under `ImageGen/images/teyvat/` (gitignored,
Tier F) and `klee-mod/pck-src/scenes/` (committed, because a `.tscn` is text
and because `pck-src` overlays the export work directory verbatim, which is the
only thing that can put a file at `res://scenes/...`). `git status --short
ImageGen` prints nothing after a run; the sixteen scene sources are committed
and `--check` fails if one drifts from what the generator would write.

Sizes are the engine's, not a taste. The layer `TextureRect`'s rect is
2764.8 × 1296 with `expand_mode = 1`, which **scales** the texture to the rect,
so the plate is authored at half that on exact aspect. The map screen's three
`TextureRect`s are `expand_mode = 1`, `stretch_mode = 5`
(KEEP_ASPECT_CENTERED), so **aspect** is what must be right and the plate
matches the base game's own 2035 × 1440 exactly.

### Real art later: the raw/out rule

A real act asset is a media-ledger item, not a code change.
`docs/current/operations/media.md` §1 is the layout and §3 the formats; act
plates take the same `media/raw/…` → `media/out/…` route as music and
portraits, with `<act-or-scene>` already reserved as `act1_mondstadt` /
`act1_liyue`. Drop the file, add the row, and `build_pck.ps1`'s Teyvat act
blocks copy it in at the same `res://` path the placeholder occupied — one
producer per out-path, exactly as `art/plan.tsv` requires. Nothing in
`klee-mod/KleeCode` changes and no scene is re-authored: the scene names the
path, the ledger names the file.

### The alias patch, and when it still fires

`KleeCode/Teyvat/Patches/ActFilePathIdentifierPatch.cs` rewrites the identifier
so a dressing wears the base zone's clothes. With this set landed it **stands
down for act 1**: `TeyvatActAssets.HasDressedAssetsCached` asks
`ResourceLoader.Exists` for the first layer scene, the background root and the
rest-site scene, and the postfix returns untouched when all three are there.
It still fires — and must — for a dressing with no set of its own and for a
build whose pck predates one, because the set is **all-or-nothing**: there is
no engine state in which two of the three files are used and the third falls
back. (A directory is not a resource, which is why the probe asks for the first
layer *scene* rather than for the `layers` path.)
