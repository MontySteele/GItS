# Card frames, stage 1 (2026-10-19)

[USER], 2026-10-19: "we need a quick way of distinguishing the character
cards". Ruled: "agreed on all of the above!"

## What stage 1 does

- **Each kit tints its own frame.** The base game draws every character card
  from one crimson frame per card type and recolours it with a per-pool
  material on `res://shaders/hsv.gdshader` (`h` rotates the hue, `s` scales
  the saturation, `v` the brightness). The five kit pools now derive BaseLib's
  `CustomCardPoolModel` through `KitCardPool`, which builds that material from
  each kit's numbers. Ids are pinned with `[CustomID]`, and members and offer
  are unchanged. The numbers live in one table,
  `klee-mod/KleeCode/CardFrameColors.cs`.
- **Companions keep the Colorless frame and get a nation pip.** It is a round
  pip in the nation's element colour with the nation's initial, to the right
  of the type plaque (the element gem sits to its left). It shows on every
  `NCard` through the same hook as the element gem
  (`klee-mod/KleeCode/Vfx/NationEmblem.cs`). No crest art exists, so it is a
  drawn pip. Kit-own companions (Klee's three, Gorou's four, Varka's Knights)
  get it as well.

| frame | h | s | v | renders about | deck chip |
|---|---|---|---|---|---|
| Ironclad (base) | 0.025 | 0.85 | 1.0 | #953E2E | D62000 |
| Regent (base) | 0.12 | 1.5 | 1.2 | #BA6600 | E36600 |
| Silent (base) | 0.32 | 0.45 | 1.2 | #50802B | 5EBD00 |
| Defect (base) | 0.55 | 0.9 | 1.0 | #1A6A93 | 3EB3ED |
| Necrobinder (base) | 0.965 | 0.55 | 1.2 | #9B4E6A | CD4EED |
| **Klee** red-orange | 0.065 | 1.3 | 1.15 | #C44A00 | F0600F |
| **Furina** deep blue | 0.63 | 1.1 | 0.85 | #2348B7 | 2F5BE0 |
| **Kokomi** pearl coral | 0.03 | 0.38 | 1.55 | #B27768 | E89A86 |
| **Varka** Anemo teal | 0.47 | 0.9 | 1.05 | #12805B | 1FB585 |
| **Yae** magenta | 0.9 | 0.9 | 1.15 | #AD33A0 | D63CC8 |

The base numbers come from the shipped `materials/cards/frames/*_mat.tres`.
"Renders about" is the frame border from a numpy copy of the shader applied
to the shipped attack frame. It is not a screenshot from the game.

Nation pips: Mondstadt 3FB894 "M", Liyue D9A62E "L" (no Liyue companion
yet), Inazuma 9A5FD9 "I", Fontaine 3A86D9 "F".

## What does not change yet

- **Energy orbs.** (Superseded by stage 2 below: every kit now has its own.)
- **Starter Strike and Defend** keep their base character's frame, so a kit
  hand now shows two frame colours. Starter basics are never changed.
  (Superseded 2026-10-20: the borrowed pair now draws in its owner's kit pool.)
- `NTinyCard` (deck-list chips) gets the tint and chip colour but no pip.

## Stage 2 (2026-10-20), ruled

[USER], 2026-10-20: "Agreed on all of the card / orb / energy mockup picks,
including Kokomi's (b) - great work on that!"

1. **Companion frames split, soft blend.** A shared companion's frame is
   Colorless on the left 40%, blends over 20%, and wears its nation's tint on
   the right 40%. The nation pip stays. Kit-own companions keep their kit's
   frame; the deck-list chip stays plain Colorless (its back is neutral grey,
   which the hsv shader cannot colour).
2. **Nation tints M-A, I-A, F-A.** Mondstadt pale sky-aqua 0.52/0.45/1.45,
   Inazuma Electro violet 0.77/1.0/1.15, Fontaine pale steel blue
   0.66/0.40/1.45, in `CardFrameColors.cs` and held apart from every base and
   kit frame by `CardFrameTests.No_two_frames_share_a_look`.
3. **Procedural combat orbs in Furina's style.** Klee Pyro with a scalloped
   ring, Varka Anemo teal with a three-lobe swirl, Yae Electro violet with a
   pink rim and five petals, from `tools/gen_energy_orb_layers.py` (`KIT_SETS`),
   each in its own `<kit>/ui/energy_counter.tscn`.
4. **Kokomi option B.** Pearl-coral body, sea-blue swirls.
5. **Tinted cost orbs.** Each kit's card cost orb and inline text orb is the
   base Ironclad one recoloured through the kit's frame numbers
   (`tools/gen_kit_energy_icons.py`), served through BaseLib's custom
   energy-icon hook; the kit's relic and potion pools use the same orb, and a
   borrowed Strike or Defend outlines its cost number in the kit's colour.

## Stage 2 options not taken

Give each kit its own frame textures (attack / skill / power, 598x844 like the
base `card_frame_*_s`) through BaseLib's pool-level `CustomFrame(card)` hook.
This applies only to `CustomCardModel` cards in a `CustomCardPoolModel` pool,
which the kit pools now are. A nation crest image can replace the pip in the
same slot.

## Unconfirmed

1. Not seen in game: the colours were chosen on the numpy render, and the
   in-game read under the game's lighting and card glow is unknown.
2. Whether the BaseLib material, one shared instance per pool rather than the
   base `.tres`'s `resource_local_to_scene`, behaves the same in every place
   that reads it. The deck-view background and sort buttons read the
   character pool's material and should now take the kit's tint.
3. The pip's label uses the default theme font, which may not match the
   card's font.
4. Co-op: a teammate without this build sees the old frames (same as any
   change to the mod).
5. Card library tabs: BaseLib keys its custom filter tabs on
   `CustomCharacterModel`, not on the pool type, so no tab should change;
   not checked.
6. Stage 2, not seen in game: the split-frame shader compiling and reading
   atlas UVs as computed; the five kit counters instancing (same scene shape
   as Furina's, which works); the kit cost and text orbs appearing on cards,
   in energy hover tips and in relic, potion and card text; the cost-number
   outline on borrowed Strikes and Defends.
