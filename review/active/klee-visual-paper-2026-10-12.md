# Klee visuals: matching the base game 1:1, 2026-10-12

[USER]:
- "What's the best we could possibly do here to get Klee to match the level of graphics and animation effort in the base game's characters? ... we'd want to see if we can get them completely 1 to 1."
- "left side of the field, right-facing ... a very slightly tilted pose so their chest is off-center (so you can see their front) while the head faces right."
- "We should also do a scale check ... reasonably sized for a small child compared to existing characters, and that she's not weirdly scaled horizontally or vertically."
- On the art route: "1 and 2 both work for me - let's see if the official model is portable, else we'll look into option 1."
- Keep the current floating splash "as an alt-art for something like bomb Set Off attacks."

**Evidence.** The census is `scratchpad/visual-census/census.md`, with render sheets `grid_combat.png`, `grid_merchant.png` and `grid_rest.png` beside it. All five base characters' Spine skeletons were read from the game's pack and posed at each screen's own scale.

## What the base game does

- **Skeletons.** Every base character uses a Spine 4.2 skeleton of 86 to 141 bones, heavily mesh-weighted, on four screens:
  - combat;
  - merchant: the combat skeleton at about 1.7 times its combat size, with a sharper texture;
  - rest site: its own seated skeleton, with three act variants;
  - character select: a close-up that bleeds off the bottom of the screen.
- **Animation.** It runs idle, low-HP idle, attack, cast, hurt and die. Crossfades between clips last 0.02 to 0.1 s. Every loop plays at a random 0.9 to 1.1 speed from a random start, so two characters never idle in sync. One-shots are slow and weighty: attack 0.9 to 1.5 s, hurt 0.7 to 1.0 s, die 1.9 to 4.2 s.
- **Pose.** Ironclad, Silent, Necrobinder and Regent turn their chest toward the viewer with the head facing right. Defect is the one frontal figure.

## Where Klee stands

**Combat.**
- The rig from #1158 (41 bones, 5 skinned meshes) is the right kind of tool. Godot's own Skeleton2D is what the Navia mod uses too, and it needs no Spine license.
  - We don't need Spine: its license asks every user to own an editor, at $379 for meshes.
- But she is frontal and airborne, and her one-shots are half the base length.
- Her clips snap between each other, except idle to low-HP idle.

**Scale.**
- **Combat:**
  - Her body is about 182 px. That's 0.74 of Ironclad, 0.94 of Silent and 0.66 of Regent.
  - A small child next to adults should be about 0.60 to 0.65, so she reads too tall next to Silent and Necrobinder.
  - Her box is the same 240×280 as Kokomi, Furina and Varka. The splash's Jumpy Dumpty and smoke fill the space above her head.
- **Merchant:** she's drawn at combat size, so she is 0.38 to 0.49 of the base figures. Her feet sit about 140 px below where the others stand.
- **Rest site:** she stands at half her combat size (body about 91 px) among seated figures twice her height.
- **Character select:** she's a small full-body figure in the middle of the screen. Base select art is a close-up crop.
- **Small UI:** her map marker fills only the lower two-thirds of its box, so it reads about 0.7 the size of the others.
- **No Klee asset is stretched.** Every one is within 2% of its source.

**One bug outside Klee.** **Furina's combat sprite is stretched about 1.66 times wide.** Her 227×440 source was resized to 240×280 with no padding (`tools/combat_layer_fences/furina.yaml`, `cut_combat_layers.py:429`). It's a fix, my call, built with this pass.

## The art source

**Option 2 works: the official Klee model exists, and we have it.**
- Your HoYoLAB link lists Klee on two official pages. One of them, Bilibili's Mondstadt model page (`activity-c_fu2inm-`), hosts 17 model packs on Bilibili's own servers.
- One pack is `可莉2.0.pmx` ("Klee 2.0"), 1.2 MB, with face, hair, outfit and expression textures. It's downloaded to the scratchpad (`klee-model/dl/`) and not committed.
- Its terms file (`使用规则.txt`), translated:
  - "Modification permitted: optimizing bones and rigid bodies, and redoing UVs."
  - "Do not redistribute."
  - "Do not use in R18 works, extreme religious propaganda, gore, horror or grotesque works, or personal attacks."
  - "Do not use for commercial purposes."
  - "All consequences of others' use of this model are not borne by the model editor or miHoYo; the user bears full responsibility."
  - "Model editor: 神帝宇. Model copyright belongs to miHoYo."
- **What that allows us:**
  - We render pictures from the model and ship the pictures, never the model file. That is what the pack is for, since the page is a creator video campaign.
  - Our build is free, so it isn't commercial. A battle pose is none of the excluded content.
  - The pack must never go into the repo or the release.

**What rendering buys:** the 3D model can be posed into exactly the base pose (chest toward the viewer, head right, feet planted) and rendered toon-shaded in her official look. The same model gives every pose we need: idle, attack, cast, hurt, death, Set Off, a seated rest-site pose and a merchant pose. None of it is painted by hand or invented by an image model.

**The tools are free:**
- Blender and its MMD importer (mmd_tools) pose and render;
- the renders are cut into the layers our existing Godot rig skins, or rendered as frame sequences for the one-shots.

Blender isn't installed on this machine yet. Installing it is a one-time step I'd do, and it costs nothing.

**Option 1, AI inpainting,** stays the fallback if the renders don't read well next to the painted base characters.

## The plan

1. **New stance art,** rendered from the official model in the base pose. The existing rig is re-skinned on it: same bones, new layers. Slow one-shots such as death can be rendered as frame sequences.
2. **Scale to 0.62 of an adult.**
   - Her body shrinks from about 182 to about 150 px. The box stays, with headroom for the Set Off pose.
   - The merchant gets her own higher-resolution sprite at the base 1.7 times, with feet on the anchor.
   - The rest site gets a seated pose from the same art, at the base 0.38 scale.
   - Character select gets a close-up crop like the base five.
   - The map marker is refit to its box.
3. **Animation to the base clock** (my calls):
   - crossfades of 0.05 s, 0.1 s from idle into an attack;
   - a random 0.9 to 1.1 loop speed and start;
   - attack about 1.0 s, cast about 1.0 s, hurt about 0.8 s, death about 2.0 s;
   - a Set Off clip that swaps to the floating splash for her Set Off cards;
   - an idle loop at the merchant and the rest site, not a still.
4. **Furina's stretch fix.**

## Ruled 2026-10-12

[USER]: "On the Klee art pass - agreed with your first picks. Sounds like a plan!"

- **Pick 1 (a):** render from the official Klee model. Ship the renders only.
- **Pick 2, corrected the same evening.** [USER]: "I feel like Klee's scaling is off. She's estimated to be around 4'2" tall (50 inches); the scale you're proposing only makes sense if the other characters are 80 inches tall, which sounds wrong?"
  - He is right. The 0.62 figure came from my census brief, not from her height.
  - At 50 inches against adults of 5'6" to 5'10", she is 0.71 to 0.76 of an adult.
  - The base adults' bodies average about 235 px at 1080p: Ironclad 245 in a crouch, Silent 193 to 224, Necrobinder 206 hovering, Regent 276 with his hat.
  - **New target: about 170 px of body, 0.72 of an adult.** Today she is 182, so she shrinks only a little.
  - She still reads small next to Silent, whose figure is drawn short (a hood, not a hat).
- **Pick 3 (a):** all five screens.
- **First milestone:** stance renders for your eyes before the rig is re-skinned.

## Milestone 1 ruled, 2026-10-12

[USER], on the stance renders: "On Klee - the toon shading works well at a glance but probably needs an in-game look to be sure. I feel like it's not 'quite' the same as the art style of the existing characters, but it's hard to say without seeing it in motion how much of that is 2D vs 3D. Stance B is definitely 'cuter' but A probably makes more sense as a battle pose."

- **Stance A (bomb held low) is the battle idle.** Stance B (bomb cradled) went where she isn't fighting: the shop and character select.
- **Toon shading stays for now.** The verdict waits for an in-game look in motion.

## Milestone 2, built 2026-10-12

**What is built.** Everything below is rendered from the official model, and only the renders ship. The pose library is `tools/klee_render/clips.py`. One command renders and packs it all (`tools/klee_render/build.py`). The model file stays in the scratchpad.

- **Combat.** Six frame sheets: idle, low-HP idle, attack, hurt, death and cast (power reuses cast with a glow). The `combat.tscn` that `tools/klee_rig` generates plays them.
  - Idle loop: 2.0 s at 20 fps, with breathing, a pigtail sway and one blink.
  - Attack: 1.0 s. Wind-up, an overarm throw of a bomb that flies off toward the enemy, then a fresh bomb pops back into her hand.
  - Hurt: 0.8 s. A flinch with her eyes squeezed shut.
  - Death: 2.0 s. A stagger, her knees buckle, she sits down hard with a small bounce and slumps; the bomb rolls away; then she fades out.
  - Cast: 1.0 s. A little hop with her free hand raised.
  - Low-HP idle: 2.4 s at 15 fps, slumped and tired.
- **The clock** follows the plan's section 3:
  - cross-fades of 0.05 s, 0.1 s from idle into the attack, 0.03 s into a hurt;
  - one-shots as listed above;
  - a random 0.9 to 1.1 loop speed and start. Her scene opts in to the existing per-creature desync (`IdleDesync`, metadata `idle_desync`).
  - The old scene's transitions were disabled, so every clip used to snap. Its travel transitions are now enabled, so they cross-fade.
- **Set Off.** Her Set Off cards (`ISetOffCard`) send a new `SetOff` trigger. The new `setoff` clip cross-fades to the old floating-bombs splash, plays its lunge, and fades back. While it plays, the router absorbs the card's own attack and cast triggers; a hit or a death still interrupts it.
- **Milestone 1's rough edges, fixed:**
  - **The flat palm.** The finger curl never ran, because the model spells its finger bones with full-width digits (`人指１`). Her hands now close.
  - **The backpack.** She now faces 14 degrees off the camera instead of 30, and the pack's root bone is tucked. Her chest reads toward the viewer and her head faces right.
  - **The bomb.** A new Jumpy-Dumpty-like bomb modelled from primitives: a red round body, ears, a cap, a lit fuse, eyes, a mouth and blush. Nothing is copied from another asset.
- **Merchant.** Stance B at 1.7 times her combat size with her feet on the anchor, breathing on a 2.4 s loop (`pck-src/klee/model/merchant_character.tscn`).
- **Rest site.** She crouches by the fire at the base rest scale, with the bomb beside her. The texture is padded so her seat lands on BaseLib's anchor.
- **Character select.** A waist-up close-up of stance B over her backdrop, bleeding off the bottom like the base five.

**The near arm, fixed 2026-10-13.** [USER], on the contact sheet: "why do the idle loop ones have no right arm (Left side)?"

- **The cause.** Stance A placed her right hand from her chest. It swung across her belly and hid the upper arm behind the coat.
- **The fix.** The hand is now placed from her right hip (`clips.py`, `NEAR_HANG`). The sleeve, cuff and glove hang at her screen-left side, and the bomb is held by her hip.
- **Same fix elsewhere:** low-HP idle, cast, the start and end of the attack, and the death sit, where the hand now props her up on the ground.
- **Left alone:** the hurt flinch (the arm raised to guard her face) and the merchant/select cradle. Both read as intended.

**Scale, measured** (`tools/klee_rig/klee_frames.json`, `measure`):

- **Height at 1080p:** 164.8 px from hat to boot, and 176.8 px to the tip of the hat's feather.
- **Against the base adults:** about 235 px, so she is 0.70 hat-to-boot and 0.75 to the feather tip. That brackets the ruled 0.72.
- **No stretch.** The renders are orthographic with square pixels, and the game draws them at one uniform scale, 0.5. Her bomb in flight measures 38 by 41 px. That is round, allowing for its ears, its cap and a sphere flattened to 0.94.

**Checked:**

- The repo gates (lints, the full pytest run, the C# build and tests) are green. A headless MegaDot probe steps the tree at 60 Hz and finds the right sheet, frame and figure in every state. It also finds the shop loop playing.
- **Not yet seen in a game.**

**Cost.** The seven sheets take about 55 MB of video memory, uncompressed at 2x. That keeps them sharp at 4K.

**Left:**

- **The map marker.** It is still the wiki side-icon. It needs either an `art_process` refit in the main checkout, or a base-style pin drawn for her; it is listed in `BACKLOG.md`.
- **The rest site is a still,** not an idle loop. BaseLib rebuilds the rest sprite from its texture alone, so a loop there needs code.
- ~~The toon-shading verdict~~: ruled 2026-10-13, below.

## Style G ruled, 2026-10-13

[USER], on the style-match variant sheet: "Agreed - I like G as well! Let's go with your pick (a)." Pick (a) was G, plus a ground shadow under her.

**What G is, as built** (`tools/klee_render/`):

- **The shader** (`render.py`, `STYLE`):
  - a three-step constant toon ramp: deep (0.66, 0.52, 0.62) at 0, half (0.90, 0.80, 0.82) at 0.22, light at 0.40;
  - the light/shadow boundaries wobbled by plus or minus 0.26 by stretched noise in her UV space (scale 22, stretch 4, turned 28 degrees);
  - plus or minus 10% value grain in UV space;
  - each body material's outline is its own texture times (0.42, 0.33, 0.35), not one flat brown.
- **The 2D pass** (`post.py`, new; numpy and Pillow only), run on every frame and still between render and pack, in this order:
  - the interior thin-line fade, at 0.6;
  - the grade: Lab chroma soft-knee at 38, max 54; L* top compressed from 97 to 88; whites +4 b*; a soft posterise, step 9, strength 0.3;
  - anisotropic Kuwahara at radius 2.0;
  - brush grain at 1.0 L*.
- **The protect mask.** The line fade and the Kuwahara skip her face and the bomb, grown 2 px and feathered. Without it her eyes vanish at game scale. The mask comes out of the same render as a `style` pass (an EEVEE AOV), so there is no second render. The face's own outline hull and the drawn-eyes overlay (the 表情 material, rendered dithered because EEVEE writes no AOV from a blended surface) are in the mask too; before that, her squeezed-shut "> <" in hurt and death fell into a hole in the mask and faded out (2026-10-13). The eye-swap morphs (はぅ, なごみ, はちゅ目) step between keys instead of blending, because part-way their drawn eyes sit behind the skin and the face reads blank.
- **The grain moves with her.** The grain is noise in her own surface space. The shader writes it into the `style` pass, and `post.py` smears it into short strokes. Measured on idle and attack, the grain changes from frame to frame exactly as much as her own texture does (frame-to-frame correlation at a fixed pixel: idle 0.96 against 0.98 for the texture; attack 0.56 against 0.59). The prototype's screen grain stayed at 1.00 while she moved, which is the crawl.
- **Scale.** Every pixel length in the 2D pass is tuned at the combat scale and grows with the render, so the shop, rest site and select close-up carry the same strokes on screen.
- **The thrown bomb** (`klee_bomb.png`) is cut from the painted attack sheet, so it carries the same look.

**The ground shadow.** Every base character's combat and shop skeleton carries a `shadow` region in its own Spine atlas. The game does not add shadows itself, so Klee's sprite scene had none. Hers is the same thing done for sprites:

- **The look.** A soft black ellipse with a flat alpha of about 0.39 and a ragged, brushy rim, like the base atlases' own shadows (Ironclad 101/255, Silent 100/255).
- **The size.** 102 by 24 px at 1080p, 1.9 times her boot span in stance A. At the shop it is 1.7 times that.
- **Where.** `pack.py` draws it (`klee_shadow.png`). The `combat.tscn` that `tools/klee_rig` generates places it first under `%Facing`, at the feet anchor, so it draws behind her and mirrors with her. The merchant scene places it the same way.
- **Nothing animates it,** so it holds through the attack, the death sit and the facing flip, as the base shadows do on their root bone.
- **The rest site has none yet.** The base rest-site skeletons carry shadows too, but the brief named combat and the shop. Her rest still is one BaseLib sprite, so a shadow there would be painted into `klee_rest.png`. It is listed in `BACKLOG.md`.

**Set Off and the roster tile, 2026-10-13.** [USER]: "I tried doing a Set off that triggered the old splash art, and I regret keeping that around - let's pivot to animations based on the new model instead." and "Let's update Klee's small character cutout in the Character Select screen ... to be a face zoom-in like the base game characters." Set Off now plays its own 0.85 s clip of the model (a hop with both fists up, eyes squeezed happy, back to stance A); the splash rig and its four cut layers are gone (Dodoco stays for `dodoco_pop.tscn`). The roster tile (`select_portrait.png`, 132x195, + locked) is a head-and-shoulders close-up rendered from the model and packed by `pack.py`.

**Left:** [USER]'s look at her in motion on the next build.

## Style H1 + H3 lite and the new stance, ruled 2026-10-13

[USER], on the style sheet: "On Klee - yeah, that looks geally good! Let's do H1 + H3 lite." And on the silhouette: "Agreed on the Silhouette change". Style G is replaced by H1 + H3 lite; stance A is replaced by the stance below.

**H1, the shader half** (`render.py`, `STYLE`). G's ramp with a deeper shadow band: deep (0.52, 0.37, 0.40), a warm purple-brown, at 0; half (0.84, 0.71, 0.70) at 0.30; light capped at (0.94, 0.92, 0.91) from 0.52, so no highlight reaches white. G's noise, grain and outlines are unchanged.

**H3 lite, the 2D half** (`post.py`, step 5, after G's four steps, on the whole finished frame). In CIELAB, chroma above C* 20 is squeezed by a fixed 0.808 (hue and L* untouched). Full H3's 0.616 pulled her 90th-percentile chroma onto the Ironclad + Silent pair's; lite takes half that pull, and keeps H3's red hue shift and cream change out.

**Measured** (idle frame 0 and attack frame 9 at 1080p, opaque pixels): L* p90 81.3, C* p90 44.7 (shipped G: 85.1 and 49.8; the H1 + H3 lite prototype on the old stance: 81.2 and 43.6; the bigger red bomb adds a little chroma).

**The stance** (`clips.py`, stance A):

- **Wider and lower.** Feet 0.17 forward and 0.15 back (were 0.11 and 0.10), hips dropped 0.12 (were 0.055).
- **Leaning toward the enemy.** The upper body leans 13 degrees toward screen right (was 4); the head takes 4 of it back. Her chest stays turned a little off-centre toward the viewer (yaw 14, twist -14), as the base cast's are.
- **A bigger bomb, held out in front.** Jumpy Dumpty is now radius 0.115 (was 0.052), about the size of her head (superseded below: the held bomb is 0.065, and 0.115 is Jumpy Dumpty's clip). Her near hand holds it out toward the enemy and the far hand steadies it from beyond.
- **Every combat clip plants her feet where stance A does,** so attack, hurt, cast, Set Off and the low-HP idle blend out of and back into idle without sliding. Cast and the low-HP idle keep the bomb in her hand in front of her; Set Off raises it overhead; the dropped bomb in death and beside her at the rest site sits on the ground at its new size. The shop and select cradle (stance B) are unchanged.
- **Her scale is unchanged.** The scale check now measures an upright still (`clips.STAND`, the old stance A without the bomb): 165.9 px hat to boot and 177.4 px to the feather at 1080p (were 164.8 and 176.8). Stance A itself is 153.9 px hat to boot and 92.0 px wide (standing: 77.5).

## Two bomb sizes, ruled 2026-10-13

[USER], on the stance above: "Actually - the new attack is probably too big. ... It's noticeably smaller than her head. I think the increased size would be fitting for her Jumpty Dumpty skill usage." In his reference shot from Genshin, her normal-attack bomb is about 60% of her head's width.

- **Her head is 0.217 model units wide at render** (`clips.HEAD_W`): the hair and face the head bone carries, across the screen in stance A, measured on the model in Blender. Her hat brim spans 0.294 and her face alone 0.166. At 1080p that is about 33 px.
- **The normal bomb is radius 0.065** (`clips.BOMB_R`, 60% of the head across; was 0.115). It is the one she holds in idle, throws in the attack, holds in cast and the low-HP idle, drops in death, sets beside her at the rest site, and cradles at the shop and on character select (that one was 0.064, so it barely moves). Her near hand closes in a little around it (finger curl 34, was 22). The attack's thrown sprite, `klee_bomb.png`, is 46 by 51 texture px.
- **Jumpy Dumpty's bomb keeps radius 0.115** (`clips.JUMPY_R`), and has its own clip, `jumpy` (1.2 s; the attack is 1.0). The small bomb goes away and the big one appears between both hands; she swings it back past her near shoulder, then heaves it two-handed from her chest toward the enemy; a fresh small bomb pops back into her hand as she settles into stance A. Its thrown sprite, `klee_bomb_big.png` (76 by 87), is cut from the release cell (0.70 s) and flown by the game from a new `%JumpyProjectile` node, slower, higher and with a bigger pop than the attack's.
- **Which cards play it.** Jumpy Dumpty, Jumpy Dumpty Mk.III and Jumpy Dumpty Mk.Omega send a `Jumpy` trigger instead of their cast (or, for Mk.Omega, instead of the attack lunge), the way the Set Off cards send `SetOff`. While the clip plays the router absorbs the card's own attack and cast, so it plays once; a hit or a death still cuts in. The big bomb aims at the card's target, or the middle of the enemy side for Mk.Omega.
- **Not changed:** the stance, H1 + H3 lite, her scale (165.9 px hat to boot standing).

## For [USER] (ruled above)

1. **The art route.**
   - **(a) Default:** render from the official Klee model (Blender + mmd_tools, free); ship renders only.
   - (b) AI inpainting of her official art.

2. **Her size.**
   - **(a) Default:** 0.62 of an adult (about 150 px of body in combat).
   - (b) 0.70: smaller than now, but still close to Silent.
3. **Which screens get the pass.**
   - **(a) Default:** combat, merchant, rest site, character select and map marker.
   - (b) Combat and merchant first, the rest after you've seen them.
