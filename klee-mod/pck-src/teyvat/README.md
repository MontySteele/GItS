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

`MonsterModel.CreateVisuals` instantiates whatever is at `VisualsPath` as an
`NCreatureVisuals`, and `NCreatureVisuals._Ready` looks up `%Visuals`,
`%Bounds`, `%IntentPos` and `%CenterPos` with `GetNode` — not
`GetNodeOrNull` — so a scene missing any one of the four throws before the
picture is ever drawn. `%OrbPos` and `%TalkPos` are the optional pair and are
omitted: the first falls back to `%IntentPos`, the second to null.

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
