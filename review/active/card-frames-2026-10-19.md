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

- **Energy orbs.** An orb is a base texture picked by name, not a hue, so every
  kit keeps the one it borrows (Klee Ironclad, Furina/Kokomi/Varka Silent, Yae
  Defect). The number outline on the orb does follow the kit's hue.
- **Starter Strike and Defend** keep their base character's frame, so a kit
  hand now shows two frame colours. Starter basics are never changed.
- `NTinyCard` (deck-list chips) gets the tint and chip colour but no pip.

## Stage 2 (next, an art job for [USER])

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
