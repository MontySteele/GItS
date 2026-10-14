# Furina visuals: the model pass, phase A, 2026-10-13

This is phase A, as Varka's was (`review/active/varka-visual-paper-2026-10-13.md`): the renders, the pipeline changes, and the review sheets. Nothing is wired into the game. Phase B wires it (BACKLOG). Everything Klee and Varka ruled carries over: style H1 + H3 lite, a ground shadow, scale by real height, each frame trimmed and packed, and sheets imported VRAM-compressed at 2x. In battle she stands on the left, facing right, a little tilted.

## What is built

**The pipeline, generalized** (`tools/char_render/`). `build.py --char furina` renders, paints and packs her in one command, as it does Varka:
- `furina_clips.py` is her pose library;
- `render.py --guests` renders the guest stars;
- `fx.py` adds her stage effects and a thrust streak;
- `pack.py` packs per character (`COMBAT_CLIPS`, `STAGE_FILES`, `GUEST_FILES`).

The body is `【芙宁娜】.pmx`, not the 荒 variant. The packs stay in the scratchpad, and only rendered PNGs leave it.

**No sword.** Her official pack has the Salon trio, cakes, a statue and a scene, but no weapon. So she fights as the performer: the far arm swept toward the enemy palm-open, the near hand at her hip (the stance already in `chars.py`). Her rapier is a phantom. `render.py` records a line from her far hand's knuckles along her hand (0.72 units, about a rapier's blade) as if it were a blade, and `fx.py` draws the attack's trail and streak from it.

**References first.** Before animating I pulled stills of her own moves from the wiki (scratch `furina-art/reference/`, with `NOTES.md` listing each URL and what it shows; never committed):
- Character Details 3, frames 24 and 48: the thrust. The sword arm is locked out level at the target, she is side-on, and the rear foot is lifted, with a long golden line along the blade. This set the attack.
- Let the People Rejoice preview, frames 24 to 30: up on one toe, back arched, one arm flung high and the other wide. This set the signature clip.
- Salon Solitaire preview: the raised calling hand. This set the cast.
- Menu idles: upright and poised, a heel lifted and her weight on one leg. With her splash art's hand on the hip, this set the idle.

**Clips** (`furina_clips.py`). Every combat clip starts and ends in stance A.

| Clip | What it does | Length | Frames |
|---|---|---|---|
| idle | Stance A, a diva at ease: the near hand on her hip, elbow out; the far hand held low and loose at her waist, palm up, presenting; the rear heel up. The chest and the open hand breathe, her weight drifts onto the front foot, she blinks, and the coat tails sway. No arm rises above the chest. | 2.8 s loop | 34 at 12 fps |
| idle_low | The performance flags: head and shoulders low, the far hand fallen to her chest, a sad brow. | 3.0 s loop | 30 at 10 fps |
| attack | The empty-handed thrust. From the idle's low open hand, the far hand draws up to her shoulder and flicks a small circle (the flourish). Then it drives straight out at the enemy as she lunges onto the front foot, with the near arm flung back and up. The hit lands at full extension (frame 8). On the recovery the arm sweeps down and in, the palm turning up, straight back to her waist. | 1.0 s | 20 |
| cast | Salon Solitaire's call. She rises onto her toes with the far hand lifted high, palm up, and the near hand to her heart. | 1.0 s | 20 |
| hurt | She flinches back, hands to her chest, wincing. | 0.8 s | 16 |
| death | A swoon played to the house: the back of her hand to her brow, a sway back, then she sinks to her knees and folds forward. Holds from 1.6 s. | 2.2 s | 25 |
| rejoice | Let the People Rejoice. She gathers, spins once on the spot with her arms drawn in, and opens into the flourish (frame 12): up on the front toe, rear leg lifted, both arms flung up and wide, delighted. She holds it, then settles. | 1.5 s | 30 |
| merchant | Stance B: upright and pleased with herself, the near hand on her hip, the far hand turned palm up below her chest as if presenting the wares. It breathes. | 3.0 s loop | 30 at 10 fps |

**Stills:**
- rest site: sitting on the ground facing the fire, knees drawn up, hands on them;
- select close-up: confident and theatrical, waist-up. Chin up, shoulders open, a small open smile, the near hand on her hip and the far hand open at hip height, palm up;
- roster tile and the locked tile, cut from the same pose;
- the ground shadow;
- `stand`, used only for the height measure.

The rest site is a still because BaseLib draws the rest site from one texture (Klee's backlog line).

**The attack's effect layer.** It is neutral (R=G=B heat, A coverage) and tinted per element like Varka's. The flourish leaves a ribbon from near her hand out to the phantom point. The thrust itself sweeps no area, because it runs along the blade, so it gets a new burst kind, `thrust`: a long thin streak along the blade from her hand out past the point, flashing at the point. On the sheets it is tinted Hydro.

**The stage effects** (`fx.STAGE_EFFECTS`). Spend, Drain and Repay have no look of their own today: the Fanfare number drops, and the base damage and heal numbers play. Each is now an effect sprite clip in the same neutral heat format. Each is recorded in the manifest under `effects` with its frames, cell, origin and intended tint. Its `uses` list is empty: no clip places it, and phase B plays it on the stage event.

| Effect | What it shows | Length | Anchor | Tint |
|---|---|---|---|---|
| spend | A golden burst thrown up from her: a flash, a ring, forty spinning confetti slips flung out and falling, and sparkles winking round her. | 0.8 s, 16 frames | her chest | #ffd36b (Fanfare gold) |
| drain | Hydro droplets drawn out of her and pulled along a shallow arc to the stage, speeding as they go. | 0.9 s, 18 frames | her chest, to the first guest seat (`to`) | #5cb8ff (Hydro) |
| repay | The droplets come back from the stage and slow into her, then a soft heal glow blooms on her: a bloom, a widening ring, rising motes. | 1.0 s, 20 frames | the first guest seat, to her chest | #5cb8ff |

The chest anchor is recorded as `stance_a.chest_px` (an offset from her feet).

## The guest stars

Each of the eleven is rendered in one calm rest, standing easy and facing right like Furina. Each has a small variation of their own (`furina_clips.GUEST_POSES`), so no two stand alike, and no arm is held out at shoulder height. They get her shading and outline, and each is trimmed to a single still (`model/guests/guest_<name>.png`). Attacks are left out until their abilities settle.

| Guest | Pose |
|---|---|
| Neuvillette | Upright, the near hand at his chest on his lapel, the far arm easy at his side. |
| Wriothesley | Arms crossed, a slight smirk. |
| Clorinde | Upright and poised: leaning back a little, chin up, the near hand on her hip with the elbow out. |
| Navia | Hand on hip, leaning back, smiling. |
| Lyney | The far hand raised to his hat brim. |
| Lynette | Arms loose, head tilted, half-lidded and deadpan. |
| Freminet | Shy: head down, hands together low in front. |
| Charlotte | Both hands up before her face, framing a photo, a wink. |
| Chevreuse | Weight settled on the rear leg, the far hand on her hip, stern. |
| Sigewinne | Hands clasped in front at the waist, held clear of her body, head tilted, beaming. |
| Escoffier | The far hand lifted at waist height, palm up, as if presenting a dish. |

**Scale.** Every guest is drawn at Furina's px per inch (`chars.guest_ppu`). A guest's head bone stands at (its `GUEST_HEIGHTS_IN` over 63 in) times Furina's head-bone height. The head bone is measured from the lowest vertex, so hats, ears and Sigewinne's antennae do not count. The packs are not at one common scale, so each is solved from its own measured head height (research packet, sec. 8).

The manifest records each guest's file, size, feet anchor, ppu and px. A test holds every guest's head px to its height over 63 in times Furina's neck px, within 4%. The px column below is head to foot with hats at 1080p. Today every guest is a flat 224 px sprite. Bounds today are 71 to 96 px wide; the new widths run 56 to 114.

| Guest | Height (in) | Full px at 1080p | Head-bone px | Width px |
|---|---|---|---|---|
| Furina (for scale) | 63.0 | 220.2 | 169.9 | 93.5 |
| Sigewinne | 52.0 | 189.3 | 138.7 | 79.0 |
| Escoffier | 62.9 | 213.5 | 168.0 | 105.0 |
| Chevreuse | 63.0 | 212.1 | 168.3 | 111.0 |
| Charlotte | 63.1 | 210.8 | 168.5 | 68.0 |
| Lynette | 63.3 | 202.5 | 168.8 | 98.0 |
| Freminet | 66.0 | 208.3 | 176.1 | 56.0 |
| Lyney | 66.7 | 222.5 | 177.2 | 67.5 |
| Clorinde | 69.2 | 229.1 | 184.3 | 92.5 |
| Navia | 70.0 | 228.7 | 186.8 | 90.5 |
| Wriothesley | 76.1 | 236.4 | 204.0 | 114.0 |
| Neuvillette | 76.4 | 237.8 | 204.6 | 90.0 |

The lineup sheet (`f_guest_lineup.png`) lays them out as `FurinaStagePlacement` does: from her hitbox edge, a 20 px gap, then each body by its own width with 20 px between. It shows a three-seat line and two four-seat lines (Ensemble Cast).

**Rig notes** (each pack probed before posing; `render.py` warns and skips a guest that lacks a posed bone). No rig failed.
- All eleven are 观海 adaptations on the shared bone set. Every bone `chars.py` and `toon.py` pose is present, and none has a 手先 bone, so the middle finger stands in as the hand tip, as for Furina.
- Clorinde, Lyney and Wriothesley lack the 真面目 morph. The guest pose does not use it.
- **The black face (fixed).** Sigewinne, Escoffier and Navia carry a `颜+` blush overlay. Hidden the way Furina's `+` shells are, it still rendered as a solid black mask over the whole face. `render.py drop_overlays` now deletes the overlay and hidden-material faces outright for the guests, and the faces read. This is probably the same family as Kokomi's black hand. It is not changed for Furina, Kokomi or Varka.
- **Freminet** wears his diving helmet in the pack (four overlapping 头盔表情 face-screen materials). The guest still hides the helmet (`GUESTS["freminet"]["hide"]`), which shows his face and cap.
- **Sigewinne's** tail and fin ears are mesh, not chains. In a still they need nothing; her antennae are left out of the height measure.
- Wriothesley and Neuvillette have a 眉影 brow-shadow material, added to their face (unlit, unlined) set.
- **Escoffier's black thighs (fixed).** The two solid black patches on her thighs were the `肌2` material: a skin layer over her stocking tops, whose lace cut-outs rendered black. It is now hidden (`GUESTS["escoffier"]["hide"]`), and her white lace stocking tops and the skin above them read. Every guest was checked at full size for other black patches; none remain.

## Measured

- **Height.** Standing (`stand`), she is 213.2 px from hat to boot and 220.2 px in full at 1080p. The target is 217.7 (63 in over a 68 in adult, times 235 px; her model's rest height with the hat is 1.72 units). In stance A her neck sits at 164.4 px against 169.9 standing, and the figure is 110.5 px wide.
- **Style** (L* p90 / C* p90, opaque pixels at 1080p):

| Figure | L* p90 | C* p90 |
|---|---|---|
| Furina idle f0 | 76.2 | 31.6 |
| Furina attack f8 | 75.9 | 32.0 |
| Ironclad | 71.4 | 41.4 |
| Silent | 68.9 | 24.9 |

  Her white hair and shorts sit her lighter than the base pair. Her chroma is between them. H3 lite is the ruled fixed squeeze and was not retuned.
- **Cost.** 13 frame sheets, 29.7 Mpx, 20.1 MB of PNG (Varka's are 92.1 Mpx). That is about 30 MB VRAM-compressed. The guest stills add 0.9 Mpx.

## Where her graphics appear (the surface list for phase B)

| # | Surface | Today | Phase A art |
|---|---|---|---|
| 1 | Combat | `pck-src/furina/model/combat.tscn` (Bounds -120..120 x -280) | The seven combat clips, the shadow and the attack's effect layer. Phase B generates the scene from the manifest, as `tools/varka_rig` does. |
| 2 | Signature trigger | None | The `rejoice` clip. Phase B adds a trigger for Let the People Rejoice, as Varka's Ascension. |
| 3 | Guests | `guest_<name>.tscn`, 224 px flat sprites cut from wiki screenshots (`tools/cut_guest_bodies.py`); Freminet has no scene (Osty fallback) | Eleven trimmed stills at her px per inch. Bounds are re-cut per width, and Freminet gets a scene. |
| 4 | Spend, Drain, Repay | Numbers only | The three effect clips, played from `FurinaStageDirector`'s Spend, Drain and Repay beats. |
| 5 | Merchant, rest, select, roster | Her current stills | Stance B loop, rest still, select close-up, roster tile and locked tile. |

## Couldn't, or chose

- **No sword prop** in the pack, so the attack is an empty-handed thrust with a phantom rapier in the effect layer. Taking a sword from another pack is ruled out: the packs' terms forbid moving parts between models.
- **The death clip's last frames** fold her forward on her knees, and her long back hair swings out level with the head's tilt. It reads as a collapse at game scale, but it is the weakest clip.
- **The roster tile** frames her head small, because her tall hat sets the tile's top line. Klee's tile frames hers larger.
- **The coat tails** swing on three chains (HB2 to HB4). There is no cloth simulation.

## Revised after [USER]'s first look (2026-10-13)

[USER]: "Uhh, ok, I don't want to be mean, but Furina's idle looks like she's doing a Nazi salute. Her character select pose is also a little weird, as though she's scared of something. The rest of her animations look good, though! The guest stars are all in the exact same poise (arms to the side) - they could use slightly more differentiated poses so they don't look like they're all doing the exact same stance, but the models look good!"
- **The idle.** The far arm held straight out at shoulder height, palm down, is gone from every frame of idle and idle_low. It is also gone from the stance every clip starts and ends on, so from the attack's wind-up, hurt, death frame 0 and the stage-effect sheets. The new stance A has her near hand on her hip and the far hand low and open at her waist, palm up, with a breathing sway. The attack's recovery used to pass the arm forward at shoulder height; it now sweeps the arm straight down to her waist. The thrust, cast, Let the People Rejoice, hurt and the effects are otherwise unchanged. The test `test_her_idle_never_holds_an_arm_out_and_her_open_hand_is_low` fails on the old pose.
- **The select close-up.** It is now confident: chin up, shoulders open, a small open smile, the near hand on her hip and the far hand open at hip height. The roster tile and the locked tile are cut from the same pose.
- **The guest stars.** Each has a pose of their own (the table above). The test `test_every_guest_star_stands_in_a_pose_of_their_own` holds that no two hold their hands alike and none holds an arm out. Escoffier's black thighs are fixed (rig notes).

## Phase B: wired into the game (2026-10-13)

[USER]: "Furina looks good!" Built as the default (pick 1 (a)), on the sheets above unchanged. Surface by surface, against the table above:

1. **Combat.** `pck-src/furina/model/combat.tscn` is generated by `tools/furina_rig` from `furina.yaml` and the manifest (`python -m tools.furina_rig gen`), on Varka's generator. States: idle, idle_low, attack, hurt, death, cast, power (the cast with a blue glow) and rejoice, at the rendered lengths, with Klee's cross-fades and her shadow. Her Bounds stay the old rig's 240 x 280, because the guest line is laid out from that box's edge.
2. **Signature trigger.** `CardPlayMotion` sends `Rejoice` for Let the People Rejoice, and only that card. The router maps it to `rejoice`, falling back to `attack`, and absorbs the card's own lunge while the clip runs.
3. **The rapier's trail.** `%AttackFx` draws the attack's heat layer from frame 3, on the same shader as Varka's. `ElementTrail` colours it from the played card's element; a card with no element keeps her Hydro (the node's `rest_element`), not his Anemo.
4. **Guests.** Each `guest_<name>.tscn` is generated from the manifest's `guests` by `tools/furina_rig/guests.py`: the rendered still at the combat scale, its feet on the ground line, so each stands at the height in the table above. Bounds are its own width (56 to 114 px), and `FurinaStagePlacement` packs the line by those. The motion is the trio's, scaled by each guest's height. Freminet has his scene and literal now, so he no longer stands as Osty. The flat cutouts no longer ship, and `tools/cut_guest_bodies.py` no longer writes scenes.
5. **Spend, Drain, Repay.** `StageDirector` asks the board for an effect on each Spend (any shape), each Drain that lost HP, and each Repay that returned HP; never on a refused Drain or the curtain call. `KleeMod.Vfx.FurinaStageFx` plays it on her body without waiting: each effect has its own AnimationPlayer, so a Repay right after a Spend does not cut the burst short. Drain and Repay are stretched along x (0.6 to 2.5 times) so their run of 192 px lands on the nearest seated guest.
6. **Merchant.** `merchant_character.tscn` is generated too: stance B on a 3.0 s loop at the shop scale.
7. **Rest site, select close-up.** `build_pck.ps1` uses `furina_rest.png` and `ui/select_closeup.png` when they exist.
8. **Roster tile.** Same path. Its producer is `char_render/pack.py` now (`art_lint.GENERATOR_OWNED`), and `gen_furina_stills.py` no longer writes it.

Two numbers moved:
- Her **AttackAnimDelay** went from 0.15 to 0.4 s, so a hit lands on the thrust at full extension (frame 8). Let the People Rejoice waits 0.2 s more after its trigger, so its hit lands on the flourish (frame 12, 0.6 s).
- Her sheets and the guest stills are imported **VRAM-compressed**, as Varka's.

Her layer-cut rig's four layers and the ten flat guest cutouts no longer ship. The contract fixture went from 455 to 467.

**Only the game can show:**
- whether the guests' new heights and widths read well in a three-seat line and a four-seat line;
- whether the Drain and Repay runs land on the guest at every line length;
- whether the Spend burst reads over her during the Rejoice spin;
- the 0.4 s hit timing on multi-hit cards;
- whether the hand-written `.import` really compresses (the build log and VRAM say).

## For [USER]

Sheets: `scratchpad/furina-art/sheets/`.
- `a_compare_1080p.png`: her beside Ironclad, Klee, Varka (82 in) and Silent, at 1080p and 2x.
- `b_strip_*.png`: every clip.
- `c_idle.gif`, `c_attack_hydro.gif`, `c_rejoice.gif`: moving.
- `d_stage_effects.png` and `d_spend.gif`, `d_drain.gif`, `d_repay.gif`: the three effects on her.
- `e_shop_rest_select_roster.png`.
- `f_guest_lineup.png`: the eleven at game scale and on stage.

1. **Phase B.**
   - **(a) Default:** wire it into the game as it is: her scenes, the Rejoice trigger, the guests' stills and the three stage effects.
   - (b) Change the motion first: the stance, the thrust, the swoon, or the flourish.
   - (c) Change the guests first: their pose, their scale, or Freminet's helmet.

## Three guests re-posed (2026-10-13)

[USER]: "Furina looks good! For the guest stars - where are Siegwinne and Neuvillette's arms? And Clorinde looks weird as though she's hnched over. But the rest are good!"

- **Neuvillette.** His hands were clasped behind his back, which hid both arms from the front. His near hand now rests at his chest on his lapel, and his far arm hangs easy at his side.
- **Sigewinne.** Her clasped hands sat against her front, and her forearms sank behind it. Her hands are now clasped at waist height, about twice as far in front of her, with the elbows a little out.
- **Clorinde.** Her near hand reached across to her far hip, which rounded her near shoulder, and her head was bowed under the hat. She now leans back 6 degrees, her neck and head are lifted (10 and 14 degrees), and her near hand rests on her own hip with the elbow out.
- The other eight are unchanged: re-rendered, their manifest entries differ only by the new measure below.

**How it is held.** `render.py` `forearms_visible` casts a ray toward the camera from every forearm and hand vertex. It counts the share that meets nothing, or only that same forearm, on the way. The manifest keeps the share per side for every guest (`forearms_visible`). `test_every_guest_shows_both_forearms_to_the_camera` requires every guest's forearms to show at least 2%, so none is hidden whole. It requires both of Neuvillette's, Sigewinne's and Clorinde's to show at least 25%, and it holds the new poses. Measured: Neuvillette 74% near, 27% far; Sigewinne 74% and 88%; Clorinde 43% and 26%. The lowest shares are the far arms that hang behind the body at this camera angle: Lynette 2%, Navia 6%, Chevreuse 17%. You called those guests good, so they are unchanged.

**Black patches.** Every guest was checked again: no 9 by 9 px block of near-black (all channels under 28) appears on any of the eleven, before or after.

Sheet: `scratchpad/furina-art/sheets/f_guest_lineup.png`.
