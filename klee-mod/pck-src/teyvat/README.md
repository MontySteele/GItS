# pck-src/teyvat — the run frame's own pck namespace

The Teyvat run frame spike (R272, `review/records/teyvat-spike-build-2026-09-15.md`).
Everything here is behind `-p:TeyvatFrame=true` and reaches nothing in a
release build.

`res://teyvat/` and not `res://klee/` deliberately: a dressed enemy body, a
nation's background or an act's music track belongs to the FRAME, not to one
character, and the C# names these paths in full
(`klee-mod/KleeCode/Teyvat/TeyvatFrame.StillPortraits`, `TeyvatMusic.Root`).

## creature_visuals/hilichurl_guard.tscn

Nibbit's still portrait in the Mondstadt dressing, and the spike's proof that a
picture can stand where the base game has a Spine rig.

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

Pixels are Tier F. `res://teyvat/creature_visuals/hilichurl_guard.png` is
produced into the gitignored `ImageGen/images/teyvat/creature_visuals/` on the
art-bearing main checkout, and `tools/build_pck.ps1`'s Teyvat block copies it
in; the block `Note-Skip`s when the directory is absent, so a build without it
stays green and prints the gap.

The spike's placeholder is a solid-colour **240x280 RGBA PNG** — the size
`docs/current/operations/media.md` §3 fixes for portraits, and the size the
roster's own combat surface already uses. To make one:

```powershell
# on the main checkout only
New-Item -ItemType Directory -Force ImageGen\images\teyvat\creature_visuals
.venv\Scripts\python.exe -c "from PIL import Image; Image.new('RGBA',(240,280),(96,120,72,255)).save(r'ImageGen\images\teyvat\creature_visuals\hilichurl_guard.png')"
```

A real portrait takes a `media/PORTRAITS.tsv` row and goes through the media
pipeline; this one is scaffolding and takes neither.
