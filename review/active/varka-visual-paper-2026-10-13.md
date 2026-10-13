# Varka visuals: the model pass, phase A, 2026-10-13

[USER]:
- "Can we do a similar job for Varka that we did for Klee, creating a new model with all animations and updating anywhere the base game uses character graphics? In his case, I think we'd want special animations (effect colors) for the element of his attack - anemo, pyro, hydro, electro or cryo."
- Correction, the same day: "Varka is a dual wielder, carrying TWO claymores, one in each hand."

This is phase A: the art pipeline, every render, and the review sheets. Phase B wires it into the game: the scenes, the new animation trigger, and the element tint. Klee's paper (`review/active/klee-visual-paper-2026-10-12.md`) is the template. Everything Klee ruled carries over: style H1 + H3 lite, a ground shadow, scale by real height, and stance A for battle with stance B where he isn't fighting.

## What is built

**One pipeline for every kit** (`tools/char_render/`):
- `toon.py` is the Blender half that both renderers now import: the H1 shader, the outline hull, the protect/grain pass, posing and framing. Klee's `render.py` was moved onto it, so there is one STYLE. A Klee re-render with the old and new code differs no more than two runs of the old code do. Blender's EEVEE is not bit-exact from run to run (max 6/255 either way), and her clip timings and anchors are identical.
- `render.py` renders any kit with a pose library. It is Furina's and Kokomi's next step too.
- `post.py` (Klee's H1 + H3 lite 2D half) is shared unchanged.
- `pack.py` packs. `fx.py` draws the element layer.
- `build.py` runs the whole chain in one command. The model packs never leave the scratchpad, and no .blend is saved.

**The blades.** Both claymores from his official pack are PMX props, one per hand:
- The near hand holds 武器 ("Claymore", 1.57 units from grip to tip).
- The far hand leads with 剑 ("Varka_Sword", 1.86 units).
- They are two different blades, so neither is mirrored.
- Each hand closes on its handle by IK every frame, so the grip never slips in a blend.

**Clips** (`varka_clips.py`). Every clip plants his feet where stance A does.

| Clip | What it does | Length | Frames |
|---|---|---|---|
| idle | Stance A: knees a little bent, feet wide, weight forward. The near blade rests on his shoulder, up and back behind his head. The lead blade is low and forward toward the enemy. Slow breathing, a blink, the coat skirt and belt tails sway. | 2.8 s loop | 34 at 12 fps |
| idle_low | Shoulders down, head low. The shoulder blade has slid down, and both tips drag on the ground before him. | 3.0 s loop | 30 at 10 fps |
| attack | An X cut at the enemy. The lead blade is hauled up and back over his head and cleaves down to low front-right (impact 1, frame 6). The near blade comes off his shoulder, from behind over the top and down in front of him, crossing the first cut (impact 2, frame 11, the main one). He puts it back on his shoulder. | 0.95 s | 19 |
| cast | Both blades raised and crossed before him: the salute. | 1.0 s | 20 |
| hurt | He flinches back behind the crossed blades. | 0.8 s | 16 |
| death | He drives both blades into the ground either side, sinks to one knee between them, lets go and bows his head. It holds from 1.6 s. | 2.2 s | 25 |
| ascension | For Four Winds' Ascension. He crouches, leaps straight up with both blades overhead, and crashes down driving both into the ground before him (impact, frame 13). Then he rises back into stance A. | 1.3 s | 26 |
| merchant | Stance B: upright, both claymores planted either side, his hands on the hilts. It breathes. | 3.0 s loop | 30 at 10 fps |

**Stills:**
- rest site: sitting upright on the ground facing the fire, knees up and forearms on them, both blades planted upright behind him;
- select close-up: stance B waist-up, bleeding off the bottom;
- roster tile: a face close-up, 132x195, plus the locked tile;
- the ground shadow;
- `stand`: an upright still used only for the height measure.

**The element layer** (`fx.py`). The body is rendered with no element colour. A separate colourless layer is cut from the blades' own swept arcs:
- render.py records each blade's base and tip four times per frame;
- one tapered crescent trail per blade: two arcs on the attack, a twin arc on the ascension;
- impact bursts at the marked frames: a flash, a ring and streaks on the attack, and a flattened shock ring with rising streaks on the ground for the ascension.

R=G=B is "heat" (1 is the white core, about 0.5 the glow), and A is coverage. A flat `modulate` tints it. The sheets use a two-line shader look: `mix(element, white, smoothstep(0.72, 1, heat))`. The element colours are the mod's own `ReactionFx.ElementFlashHex` (`klee-mod/KleeCode/Vfx/ReactionFx.cs`):

| Element | Colour |
|---|---|
| Anemo | #8fffd6 |
| Pyro | #ff9a5c |
| Hydro | #5cb8ff |
| Electro | #c08cff |
| Cryo | #a8f0ff |

**Data for phase B** (committed): `tools/char_render/varka_frames.json`. It holds each clip's logical cell and per-frame rects (page, rect, offset in the cell), pages, counts, times, feet anchors, the impact frames (`impact_frames`, `main_frame`), the fx layers' first frame and anchor, the shadow placement, the rest seat and the select framing.

## Measured

- **Height.** Standing (`stand`), he is 265.5 px from hair to boot and 270.5 px in full at 1080p. The target is 269.6 (78 in over a 68 in adult, times 235 px). That is 1.13 to 1.15 of the base adults. In stance A his neck sits at 222.8 px against 238.7 standing (the crouch), and the figure with both blades is 294.5 px wide (it was 473). The shoulder blade's tip rises over his head, to 316 px.
- **Style** (L* p90 / C* p90, opaque pixels at 1080p):

| Figure | L* p90 | C* p90 |
|---|---|---|
| Varka idle f0 | 69.7 | 24.4 |
| Varka attack f11 | 66.7 | 23.9 |
| Ironclad | 71.4 | 41.4 |
| Silent | 68.9 | 24.9 |
| Ironclad + Silent mean | 70.1 | 33.2 |

His black coat and grey trousers sit him under the pair on both measures, near Silent. H3 lite is the ruled fixed squeeze and was not retuned.
- **Cost.** After the review: 15 files, 98.5 Mpx (it was 174 Mpx in 21 files). That is 376 MB of RGBA uncompressed at 2x, or about 94 MB VRAM-compressed (1 byte per texel), and 48 MB of PNG on disk. Klee's whole set is about 55 MB. Every combat clip now fits one 4096 page.

## Where his graphics appear (the surface list for phase B)

From `klee-mod/KleeCode/Varka.cs`, `tools/build_pck.ps1` and Klee's wiring:

| # | Surface | Today | Phase A art |
|---|---|---|---|
| 1 | **Combat** | `pck-src/varka/model/combat.tscn`, the layer-cut rig (Varka.cs L117-143; states idle, idle_low, attack, cast, power, hurt, death). Fallback is `varka/model/combat_model.png`, used by `combat_visuals.tscn` (build_pck L1151). | **Yes:** the seven clips, the shadow, and the attack and ascension fx layers. Phase B generates the scene from the manifest, as `tools/klee_rig` does for Klee. The pages need one Sprite2D or region per page. |
| 2 | **Ascension trigger** | None. | **Yes, the clip.** Phase B adds `Ascension -> ascension, attack` to `Vfx/CreatureAnimationRouter.cs` TriggerToStates (L58-77) and to AbsorbedBy. It sends the trigger from `Vfx/CardPlayMotion.cs` (L104) for Four Winds' Ascension, the way Jumpy is sent. It mirrors the state in `tools/visual_qa/scene_deps.py` and `tools/animation_bakeoff/spec.py`. |
| 3 | **Element tint** | None. | **Yes, the neutral layer.** Phase B draws it over the body from `first_frame`, tinted by the element the attack deals. |
| 4 | **Merchant** | `merchant_character.tscn`, a still Sprite2D of combat_model.png (build_pck L1169-1176). | **Yes:** `varka_merchant.png`, the stance B loop, and its shadow. |
| 5 | **Rest site** | `rest_character.tscn`, combat_model.png (build_pck L1160-1167). | **Yes:** `varka_rest.png`, padded so his seat sits on the anchor. It needs Klee's `$kleeRestArt` switch (L1024-1031). |
| 6 | **Select close-up** | `char_select_bg_varka.tscn`, the select_bg backdrop plus selection_splash (build_pck L1094-1131). | **Yes:** `ui/select_closeup.png` replaces the splash. The backdrop stays. |
| 7 | **Roster tile** | `ui/select_portrait.png` and the locked tile, from `gen_varka_stills.py`. | **Yes.** Their producer moves to `char_render/pack.py` in `art_lint.GENERATOR_OWNED` (L571-577). |
| 8 | Map marker | `ui/map_marker.png` (gen_varka_stills). | No. Klee's pipeline makes none either. |
| 9 | Top-bar icon and outline | `ui/char_icon.png`, `char_icon_outline.png`. | No. |
| 10 | Transition wipe, energy counter, co-op hands | Their own art, Ironclad's counter, Ironclad's arm. | No. |
| 11 | Telemetry | `KleeSceneTelemetry.cs` L52-59 and L86/88 need `%Facing` and `%AnimationTree` in the new scene. | No art needed. |

`build_pck`'s `Copy-VarkaFallback` (L755-779) still copies Klee's files wherever Varka's are missing. The art itself is packed in the scratchpad (`varka-art/artroot`), not in ImageGen. Copying it across is phase B's first step.

## Couldn't, or chose

- **The blades are as long as he is tall,** at 0.77 and 0.91 of his height. Three poses bend because of it:
  - With his hands at chest height, a planted blade's tip sits about 0.1 to 0.3 units in the ground. `pack.py` cuts every pixel under the ground line (anchor + 6 px), so the tips read as driven in.
  - "Hands on the pommels" became hands on the hilts. The pommels would sit at his collarbone.
  - Laid flat, a blade is a hairline from the game's 5-degree camera, so at the rest site both blades stand planted behind him instead.
- **The blades' flats are turned 25 to 30 degrees off the viewer** in combat. Edge-on they read as wires at 1080p.
- **Secondary motion** is a swing of the coat skirt's twelve chains, the belt tails and the shoulder cape. There is no cloth simulation.

## Revised after review (2026-10-13)

The main session reviewed phase A's sheets. Five notes; four changed the art.

- **The attack aimed the wrong way.** The second strike rose and ended with the blade pointing up behind him, and its trail swept over his back. The enemy is to his right. It is now an X cut at the enemy:
  - Strike 1: the lead blade goes up and back over his head and cleaves down to low front-right (frame 6).
  - Strike 2, the main one: the near blade comes off his shoulder, from behind over the top and down in front of him, crossing the first cut steeper from a higher hand (frame 11). It ends low in front, then goes back on his shoulder.
  - At both impacts the striking blade points right, between chest and knee height. Both trails sweep from above and behind into the hit on his right. The impact bursts are placed from the blade's own position at the impact frame, so they moved with it.
- **The idle was too wide.** The rear blade trailed far behind him. The near blade now rests on his shoulder, up and back behind his head, and the lead blade stays low and forward. His knees bend a little less, his feet are a little wider and his weight is forward. Stance A went from 473 to 294.5 px wide at 1080p (with both blades; his body alone is about 112). idle_low, the crouch before the ascension leap, and every clip that starts or ends in stance A were reworked to match. Their feet stay where idle plants them.
- **The rest site read as lying down,** and the ground line cut him. He now sits upright on the ground facing the fire, knees up and forearms on them. Both blades are planted upright behind him, and only their tips and his coat tail go under the ground line.
- **Texture budget:** pick 1's default, plus a tighter trim. Each frame is now cut to its own pixels and shelf-packed, rather than every frame taking the clip's widest box. In Godot that is an AtlasTexture whose margin restores the cell. With the narrower idle, the set went from 174 to 98.5 Mpx.
- Unchanged and approved: stance B (the shop), the select close-up, the roster tile, the element trail layer and its colours, and the scale.

## For [USER]

1. **Texture budget.** Taken at the default in the design review: keep 2x like Klee, and phase B imports his sheets VRAM-compressed (`texture_import` in the manifest). With the per-frame trim that is about 94 MB.
2. **The look,** on these sheets: `scratchpad/varka-art/sheets/`.
   - **(a) Default:** go to phase B as is.
   - (b) Change the poses first: the blade angles, the trail width, the rest pose.
