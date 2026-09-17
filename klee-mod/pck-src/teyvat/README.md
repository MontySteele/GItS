# pck-src/teyvat — the run frame's own pck namespace

The Teyvat run frame spike (R272, `review/records/teyvat-spike-build-2026-09-15.md`).
Everything here is behind `-p:TeyvatFrame=true` and reaches nothing in a
release build.

`res://teyvat/` and not `res://klee/` deliberately: a dressed enemy body, a
nation's background or an act's music track belongs to the FRAME, not to one
character, and the C# names these paths in full
(`klee-mod/KleeCode/Teyvat/TeyvatFrame.StillPortraits`, `TeyvatMusic.Root`).

## creature_visuals/*.tscn — GENERATED, 123 of them for 122 plates

**Do not hand-edit a file in this directory.** Every `.tscn` under
`creature_visuals/` is written by `tools/gen_teyvat_creature_scenes.py` from
one table, `docs/current/dossiers/content/enemy-dressings.tsv`, which says per
row which Genshin body dresses which base-game `Id.Entry` on which face, under
which display name, at which size class, moving in which motion set. The same
run emits the five motion libraries under `motion/` and the two C# tables
(`klee-mod/KleeCode/Teyvat/TeyvatCreaturesGenerated.cs`) that `TeyvatFrame`
exposes as `StillPortraits` and `MonsterNames` — so a body cannot get its
picture without its name, or the reverse. `--check` fails on any drift and
`tier0/tests/test_teyvat_creature_scenes.py` rides it (`EB-811`).

    .venv\Scripts\python.exe tools\gen_teyvat_creature_scenes.py
    .venv\Scripts\python.exe tools\gen_teyvat_creature_scenes.py --check

**Sizing.** A 240x280 plate at scale 1 is a small body, so the row's size class
scales the sprite and, with it, `%Bounds`, `%IntentPos` and `%CenterPos` — the
health bar, the block badge, the selection reticle, the intent marker and every
hit VFX are placed off those, and a plate that grew while its bounds did not
would put the intent inside the body. The three numbers, and the base-game
`%Bounds` medians they land on, are derived in the generator's docstring:
`regular` 1.0 (280 tall), `elite` 1.3 (364), `boss` 1.6 (448).

A size class belongs to the **row**, not to the plate: the Golden Wolflord
dresses Overgrowth's Ceremonial Beast (a boss) and Sumeru's Fabricator (a
regular) and is the same picture either way. A scene fixes one scale, so such a
body gets `<body>_<class>.tscn` per class over the same `<body>.png` — today
that is `golden_wolflord` alone, which is why there are 123 scenes for 122
plates. The `motion` column splits a body the same way and for the same reason;
the suffix names only the axis that actually varies.

**`Visuals.Scale` is never written** — `NCreature` owns it — so the scale rides the `Sprite2D`
under `%Visuals`, and `%Visuals` itself stays an identity `Node2D`.

## motion/*.tres — GENERATED, five shared AnimationLibraries

`stand`, `bounce`, `hover`, `loom`, `mech`, each five clips
(`RESET`/`idle`/`attack`/`hurt`/`death`), written by the same generator run.
A scene loads one of them through `%AnimationPlayer`'s
`libraries = { "": ExtResource(...) }`, which is why the clips live here once
rather than inlined in 123 scenes.

Every generated scene carries a `Rig` (`Node2D`, identity) between `%Visuals`
and the `Sprite2D`, and **the clips key `Rig` and nothing else** —
`Visuals/Rig:position`, `:scale`, `:rotation`, plus `Visuals/Rig/Body:modulate`
for the hit flash and the death fade. That list is not stylistic:
`%Visuals.Scale` is `NCreature`'s and `Body`'s transform IS the size class, so
a clip touching either would fight the engine or flatten every elite and boss
to regular size the first time it played. The pins are in
`tier0/tests/test_teyvat_creature_scenes.py`; the shape and the state machine
are documented in `docs/current/operations/codegen.md`.

`build_pck.ps1` overlays this whole directory verbatim, so the `.tres` files
pack and the derived pck contract lists them with no change to the script.

The rest of this section is the mechanism, written when the directory held one
hand-made file (Nibbit's, `hilichurl_guard.tscn`, retired into
`wooden_shield_hilichurl_guard.tscn` when its real plate was cut). It is
unchanged by the generalisation, and every generated scene is the same four
nodes it describes.

### The root is not an `NCreatureVisuals`, and it has to become one

The first version of this file said `MonsterModel.CreateVisuals` "instantiates
whatever is at `VisualsPath` as an `NCreatureVisuals`". **That is backwards, and
it is EB-760.** `CreateVisuals` does
`GetScene(VisualsPath).Instantiate<NCreatureVisuals>()` — it **casts** the
instantiated root, it does not adapt it. A script-less scene's root is whatever
type the `.tscn` names, here a plain `Node2D`, so the cast threw
`InvalidCastException`, `CreateVisuals`'s own catch swallowed it, and the game
drew the pink error creature
(`review/records/teyvat-spike-proofs-2026-09-15.md` item 3).

What makes the cast succeed is **BaseLib's auto-conversion**, the same
mechanism our character combat scenes ride. `SceneConversionPatch` postfixes
`PackedScene.Instantiate(GenEditState)` and calls `NodeFactory.TryAutoConvert`,
which converts only scenes whose path has been **registered**.
`KleeCode/Teyvat/TeyvatVisuals.RegisterStillPortraits` is that registration —
one `RegisterSceneForConversion<NCreatureVisuals>()` per row of
`TeyvatFrame.StillPortraits`, made at `[ModInitializer]` time. Two log lines are
the proof it happened: `Registered scene '…' for auto-conversion to
NCreatureVisuals` at boot, and `Auto-converted '…' from Node2D to
NCreatureVisuals` the first time the scene is instantiated.

Klee's, Kokomi's and Furina's scenes get this for free because
`PostModInitPatch.RegisterSceneConversions` asks every model in `ModelDb`
`as ISceneConversions` and a `CustomCharacterModel` answers. A **dressed
base-game monster is not our model** — the arm only rewrites the path a shipped
`MonsterModel` returns — so its scene has to be registered by hand, exactly as
`BakeKuragePet` and `FurinaStagePets` already do for their injected pets.

The conversion is a **reparent, not a reshape**: `NCreatureVisualsFactory`
builds a bare `NCreatureVisuals`, moves every child across, copies the root's
`Node2D` properties, and generates only the named nodes the scene does not
already carry.

### The four nodes the scene must carry

`NCreatureVisuals._Ready` looks up `%Visuals`, `%Bounds`, `%IntentPos` and
`%CenterPos` with `GetNode` — not `GetNodeOrNull` — so a scene missing any one
of the four throws before the picture is ever drawn, and this one carries all
four. `%OrbPos` and `%TalkPos` are the optional pair and are omitted: the first
falls back to `%IntentPos`, the second to null; the factory's `GenerateNode`
switch has no case for either, nor for `%PhobiaModeVisuals`, so they stay
absent. `%FormVfx` is the one node the factory does add for us.

`_Ready` builds a `MegaSprite` **only** when the `%Visuals` node's `GetClass()`
is literally `"SpineSprite"`. A `Node2D` holding a `Sprite2D` therefore leaves
`SpineBody` null and `HasSpineAnimation` false, which is the whole mechanism by
which a still body draws at all — and the reason
`MonsterModel.GenerateAnimator(MegaSprite)` and `SetupSkins(MegaSprite,
MegaSkeleton)`, whose signatures demand a spine object, are never reached for
one (`NCreature.cs:509` gates the animator build on that flag).

**No script**, per `pck-src/README.md`'s standing rule: behaviour attaches from
C#, never from an `ext_resource type="Script"` line.

## The texture is NOT in this repository

Pixels are Tier F. Every `res://teyvat/creature_visuals/<body>.png` is produced
into the gitignored `ImageGen/images/teyvat/creature_visuals/` on the
art-bearing main checkout, and `tools/build_pck.ps1`'s Teyvat block copies the
whole directory in; the block `Note-Skip`s when it is absent, so a build
without it stays green and prints the gap. Both readers ask
`ResourceLoader.Exists` of the SCENE first, so a missing plate costs a body its
dressing and nothing else.

Each plate is a **240x280 RGBA PNG** — the size `docs/current/operations/media.md`
§3 fixes for portraits, and the size the roster's own combat surface already
uses. The 122 are produced by `art/plan.tsv`'s portrait block and recorded one
row each in `media/PORTRAITS.tsv`, per the media pipeline's "the plan produces
and the ledger records" rule (`operations/media.md` §1).
