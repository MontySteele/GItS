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

- **Option 2, the official 3D model.** It can't be confirmed from here.
  - HoYoverse's 2020 model release lists 14 characters, and Klee isn't one.
  - A 2020 blog says a Klee model went to their account on the Chinese site Model House (aplaybox.com), but that site needs an account and I couldn't reach it.
  - Those models' terms allow modifying the model and forbid redistributing it or using it commercially. So we could ship pictures rendered from it, never the model file.
- **Option 1, AI inpainting of her official art.** The fallback you named. From the official splash and character portrait, generate a right-facing three-quarter stance:
  - chest toward the viewer, head right;
  - feet on the ground;
  - painted in her official style.
  
  Then cut it into the same layers the rig already skins. The current splash stays as the Set Off pose.
  - Which image model to use is open. If it costs money, that comes to you as its own pick.

## The plan

1. **New stance art,** from whichever route pick 1 chooses. The existing rig is re-skinned on it: same bones, new layers.
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

## For [USER]

1. **The art route.**
   - **(a) Default:** go to option 1 (AI inpainting) now.
   - (b) You check Model House first. If an official Klee model is there, we render her from it. It needs an account, and I can't make one for you.
2. **Her size.**
   - **(a) Default:** 0.62 of an adult (about 150 px of body in combat).
   - (b) 0.70: smaller than now, but still close to Silent.
3. **Which screens get the pass.**
   - **(a) Default:** combat, merchant, rest site, character select and map marker.
   - (b) Combat and merchant first, the rest after you've seen them.
