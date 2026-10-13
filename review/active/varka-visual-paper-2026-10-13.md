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
| idle | Stance A: a tight, ready battle stance. Knees bent, feet wide, weight forward. Both blades are held in a low guard, angled down and back at his sides with the tips off the ground, mirrored so they read as one pair. Only the chest breathes; the blades stay fixed in his hands. A blink, the coat skirt and belt tails sway. | 2.8 s loop | 34 at 12 fps |
| idle_low | The same guard, worn down: shoulders and head low, both tips lowered together, still clear of the ground. | 3.0 s loop | 30 at 10 fps |
| attack | One continuous spin-to-slam. From a short wind-up, one turn on the spot carries both blades up a rising helix: level behind him, a little raised as they pass the enemy's side (light impact, frame 7), overhead as the last fifth of the turn begins, and on down in front of him as the turn brings him back to face the enemy (main impact, frame 12). A settle, then back to the guard. | 1.05 s | 21 |
| cast | Both blades rise together beside him, then cross before him: the salute. | 1.0 s | 20 |
| hurt | His body snaps back; the guard holds, both blades lifted together a little in his fixed grip. | 0.8 s | 16 |
| death | He drives both blades into the ground either side, sinks to one knee between them, lets go and bows his head. It holds from 1.6 s. | 2.2 s | 25 |
| ascension | For Four Winds' Ascension. He crouches and jumps straight up (hips 0.80 units, 0.39 of his height), the lead blade swung up over his head and the other held back for balance. Coming down, the lead blade chops over the top and is driven point-first, near vertical, into the ground in front of him as he lands (impact, frame 10). A hard landing, low beside the planted blade; he pulls it out and is back in the guard. No turn. The ground burst is a separate effect clip (see Round 3). | 1.3 s | 26 |
| merchant | Stance B: upright, both claymores planted either side, his hands on the hilts. It breathes. | 3.0 s loop | 30 at 10 fps |

**Stills:**
- rest site: sitting upright on the ground facing the fire, knees up and forearms on them, both blades planted upright behind him;
- select close-up: stance B waist-up, bleeding off the bottom;
- roster tile: a face close-up, 132x195, plus the locked tile;
- the ground shadow;
- `stand`: an upright still used only for the height measure.

**The element layer** (`fx.py`). The body is rendered with no element colour. A separate colourless layer is cut from the blades' own swept arcs:
- render.py records each blade's base and tip four times per frame;
- one tapered crescent trail per blade: on the attack one ribbon per blade, the two over the same window, spiralling up through the spin and down into the slam; on the ascension one ribbon for the driven blade;
- impact bursts at the attack's marked frames, centred between the two blades: a flash, a ring and streaks;
- the ascension's ground burst, a separate effect clip placed at the blade's point and, mirrored, under the target (Round 3).

R=G=B is "heat" (1 is the white core, about 0.5 the glow), and A is coverage. A flat `modulate` tints it. The sheets use a two-line shader look: `mix(element, white, smoothstep(0.72, 1, heat))`. The element colours are the mod's own `ReactionFx.ElementFlashHex` (`klee-mod/KleeCode/Vfx/ReactionFx.cs`):

| Element | Colour |
|---|---|
| Anemo | #8fffd6 |
| Pyro | #ff9a5c |
| Hydro | #5cb8ff |
| Electro | #c08cff |
| Cryo | #a8f0ff |

**Data for phase B** (committed): `tools/char_render/varka_frames.json`. It holds each clip's logical cell and per-frame rects (page, rect, offset in the cell), pages, counts, times, feet anchors, the impact frames (`impact_frames`, `main_frame`), the fx layers' first frame and anchor, the effect clips and where each is placed (`effects`), the shadow placement, the rest seat and the select framing.

## Measured

- **Height.** Standing (`stand`), he is 265.5 px from hair to boot and 270.5 px in full at 1080p. The target is 269.6 (78 in over a 68 in adult, times 235 px). That is 1.13 to 1.15 of the base adults. In stance A his neck sits at 218.8 px against 238.7 standing (the crouch), and the figure with both blades is 255.5 px wide (294.5 in the reviewed take, 473 in the first). Nothing rises over his head: the guard's full height is 249.9 px.
- **Style** (L* p90 / C* p90, opaque pixels at 1080p):

| Figure | L* p90 | C* p90 |
|---|---|---|
| Varka idle f0 | 68.1 | 24.6 |
| Varka attack f12 | 67.0 | 23.3 |
| Ironclad | 71.4 | 41.4 |
| Silent | 68.9 | 24.9 |
| Ironclad + Silent mean | 70.1 | 33.2 |

His black coat and grey trousers sit him under the pair on both measures, near Silent. H3 lite is the ruled fixed squeeze and was not retuned.
- **Cost.** After Round 3: 16 files, 85.4 Mpx (75.3 after the motion redo, 98.5 after the review, 174 in 21 files at first). That is 342 MB of RGBA uncompressed at 2x, or about 85 MB VRAM-compressed (1 byte per texel), and 46 MB of PNG on disk. Klee's whole set is about 55 MB. Every combat clip now fits one 4096 page.

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

## Revised after [USER]'s look (2026-10-13)

[USER], on the reviewed sheets: "I think that the model and shading is mostly excellent! But the pose and the atack animations look... a little lame. Varka's a highly acrobatic character who tends to do spins and attack with both claymores in sync at the same time using spins and flips, rather than just raising them one after the other. I think that trying to go overboard here would make him stand out too much, but we can look for an edit that is less... 'floppy'"

The model, the shading, the scale (78 in), the element trail layer, the texture pipeline, the select close-up and the roster tile are unchanged. The motion was redone:
- **Both claymores move in sync,** mirrored or parallel, never one raised after the other. In code (`pair()` in `varka_clips.py`) the near blade is the far blade reflected about his body, unless a pose names a crossed pair. The test `test_the_two_blades_move_in_sync` checks that between any two keys of every combat clip both blades turn through the same angle, within 15 degrees, in the world and in his body's frame.
- **Rigid, not floppy.** The blades stay fixed in the grip: through the spin and the leap they hold one pose relative to his body. `render.py` now interpolates the blades in the root's own frame, so a turn carries them round with him instead of cutting the chord. Moves are short snaps between held poses (hard ease into each impact, a small settle after), not slow even blends.
- **Stance A** is a low guard: both blades down and back at his sides, tips off the ground, knees bent, weight forward. 255.5 px wide at 1080p.
- **The attack** is one compact spin and a double cleave (see the clip table). His feet stay inside the guard's footprint; the spin's hop is 0.10 units, and they are planted for the main impact.
- **The ascension** is a modest leaping spin, not a flip: a flip with blades this long drives them through the ground when he is upside down. His hips rise 0.66 units at the top (a third of his 2.05), and the impact frame is kept in the manifest.
- **Cast, hurt, death and merchant** keep their beats with the blades in the same rigid, synced grip. The rest site leaned back a little; his upper body now leans 14 degrees toward the fire (it was 6), so he sits upright with his forearms on his knees.
- **The trail layer** follows the new arcs: the spin's two trails are a ring segment, the cleave's two run parallel, and the slash bursts sit between the two blades.

## Round 3: after [USER]'s second look (2026-10-13)

[USER], on the round-2 sheets: "Much better! But there is one odd note - he half-twirls once, then instantly flips to slam them down. Could we make this smoother, with the twirl also raising the blades and the slam showing him spinning back, so it reads as one continuous animation rather than two halves? For the Four Winds' Ascension - let's drop the twirl and instead show him jumping up and then driving one blade into the ground, with a mirrored ground particle effect on him and the target enemy."

Only the attack and the ascension changed. Idle, cast, hurt, death, the shop, the rest site, the model, shading, scale, trail colours and texture pipeline are as they were.

**References.** Before animating, stills of his own moves were pulled from the wiki's talent demos and kit explainers. They stay in the scratch folder (`varka-art/reference/`, with `NOTES.md` listing each URL and beat) and are never committed.
- Talent Demo 2 (his 5-hit string) and Talent Demo 3 (Windbound Execution): the blades held level through a spin, then rising cuts and an overhead arc down in front. This set the attack's helix: level, then up, then down in front.
- Character Details 3, right panel (the special charged attack): a low crouch with both blades at his sides, then a spin with both out level. This set the wind-up.
- Character Details 3, left panel (Four Winds' Ascension itself): a straight jump with the blades raised and knees tucked, then one claymore driven point-first, near vertical, into the ground, and a low crouch beside it with the other blade swept back. This set the whole ascension.
- Talent Demo 1 (frames 15, 60, 63) and Character Details 3 (frames 16 to 34): radial cracks, a flat ring, and a column of light rising from the point. This set the ground burst.

**The attack is one motion.** The turn and the blades' pitch are smooth curves of one parameter, keyed every half frame (`varka_clips.py`: `spin_turn`, `spin_pitch`, `helix`).
- The turn eases in from the wind-up and eases out into the slam.
- The pitch climbs the whole way, from level behind him (-18 degrees), over the top (90), to down in front (200), and speeds up over the top. Nothing holds at the top.
- The overhead comes at about 300 degrees of the turn. The last 60 degrees bring him back to face the enemy as the blades come down.
- Both blades stay mirrored and rigid in his grip.
- One ribbon per blade runs the whole way (`trails`, `age` 0.22 s), spiralling up and coming down into the slam.
- The new test `test_the_attack_is_one_continuous_motion` checks the join. From one half-frame step to the next, the yaw speed may change by at most a quarter of its peak, and each tip's vertical speed by at most 0.35 of its peak. The overhead must be passed while the yaw is still turning.
- Impacts: the light one at frame 7, as the rising blades pass the enemy's side. The main one at frame 12, low and to the right.

**The ascension drives one blade.**
- The lead (far, left-hand) blade goes in at frame 10. Its grip is 1.42 units up, it leans 16 degrees toward the enemy, and its point is about a fifth of its length under the ground line, where `pack.py` cuts it. The other blade is held back for balance.
- The jump's peak is 0.80 units at the hips, under half his 2.05 units of height.
- The test `test_the_ascension_jumps_and_drives_one_blade_into_the_ground` checks: no turn, the jump under half his height, landed on the impact, the point at the ground line in front of him, and the other blade back.

**The ground burst** is its own sprite clip, `fx.ground_burst()`, packed as `varka_ground_burst.png`: 11 frames at 20 fps (0.55 s).
- What it draws: radial jagged cracks and an expanding flattened ring on the ground, plus a column of streaks rising from the point.
- It uses the same neutral heat format as the trails, so the same element tint applies.
- The manifest records it under `effects.ground_burst`, with its cell, origin (the ground point) and frames, and one `uses` entry: `clip` ascension, `start_frame` 10, `mirror` true, `both_positions` true. That entry has two `places`:
  - `blade_tip`: the blade's crossing of the ground line, offset (273, 0) texture px from his feet anchor, `flip_h` false;
  - `target`: the target's feet anchor, `flip_h` true.
- Phase B places both copies from frame 10. The review sheets preview both, with a dummy target marker drawn 550 px to his right at 1080p.

**Cost.** 16 files, 85.4 Mpx (the burst adds 4.1). That is about 85 MB VRAM-compressed and 46 MB of PNG.

The sheets were regenerated in place: `b_strip_attack`, `b_strip_ascension`, `c_attack.gif`, `c_attack_anemo.gif`, `c_ascension.gif`, `c_ascension_pyro.gif`, `d_elements_attack`, `d_elements_ascension` and `a_compare_1080p`.

## For [USER]

1. **Texture budget.** Taken at the default in the design review: keep 2x like Klee, and phase B imports his sheets VRAM-compressed (`texture_import` in the manifest). With the per-frame trim and the tighter guard that is about 85 MB.
2. **The motion,** redone after your second look (Round 3), on these sheets: `scratchpad/varka-art/sheets/` (`c_attack_anemo.gif` and `c_ascension_pyro.gif` show it moving).
   - **(a) Default:** go to phase B as is.
   - (b) Change the poses first: the guard, the spin-to-slam, the jump and drive, or the ground burst.
