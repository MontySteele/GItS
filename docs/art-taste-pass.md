# Art Taste Pass — Full Candidate Sweep (chat-side, all 113 card tiles reviewed)

**Date:** 2026-07-20. Method: fetched the full plan via art_fetch.py, rendered
every candidate at its actual plan crop (mode/focus applied), reviewed on
labeled contact sheets. Verdicts are TONAL-FIT calls per card intent; the
user's "random collection of Klee pictures" diagnosis is confirmed and has a
specific cause: **six art registers mixed with no register→card-class rule.**

## The register rules (the systemic fix — adopt these and most rows fix themselves)

1. **Sticker/emoji art (Paimon's Paintings, Sparkling Steps)** → cards whose
   identity is a Klee EMOTION or antic. These read wonderfully at card size
   — but the emotion must match the card (a crying Klee on a cheerful card
   is the tonal gap in miniature).
2. **Item renders (bombs, fireworks, toys, food)** → cards about an OBJECT.
   Charming and coherent. PROCESS BUG: small transparent renders under
   `cover` crop produce smeared edge-extension bands (visible on
   pocket_fireworks, endless_fireworks r1, spirited_away r1). Item renders
   must use `contain` on a flat card-frame background, never `cover`.
3. **VFX-dominant gameplay frames** → big attack cards — ONLY when the
   explosion fills the frame. HARD RULE: **no visible damage numbers, UI,
   or tiny-Klee-in-a-field frames, ever.** (Currently shipping: 814 on
   jumpy_dumpty, 143/60 on big_badda_boom r2, 60 on mine_toss r3.)
   Preview GIFs are salvageable by picking a different frame_pct and
   punching the crop into the blast.
4. **TCG equipment-card art** → COMPANION cards. Already coherent
   (Barbara/Bennett/Fischl/Kaeya/Sucrose all use their own TCG talent
   art) — this register is the art sprint's quiet success. Keep.
5. **Official splash/birthday/character-card art** → identity moments and
   rares. Working where used (blazing_delight r1, warm_glow).
6. **Constellation sigils (128px dark discs)** → **BANNED from card
   portraits entirely.** They are flat, upscaled, and read as UI. But they
   are literally icon-shaped: **REDIRECT the whole set to power icons and
   relic/upgrade badges**, where 128px native is the correct size and the
   style is perfect. This retires ~10 bad picks and fills a real need
   (.pck-gated power/relic icon slots) in one move.

## Per-asset verdicts (r1 = current pick; ✓ keep, ✗ replace)

### Clean keeps (register-correct as picked)
- **kaboom r1** ✓ (character card), **blazing_delight r1** ✓ (golden card),
  **warm_glow r1** ✓ (Birthday 2023 — warm, sunny, exact),
  **run_away r1** ✓ (panicked sticker — flavor-perfect),
  **da_da_da r1** ✓, **eager_to_help r1** ✓ (beaming chibi),
  **duck_and_cover r1** ✓ (Klee sheltering — made for this card),
  **all_my_treasures r1** ✓ (collection cupboard), **ammo_scavenging r1** ✓
  (travel bag), **pop r1** ✓ (Kaboom Box with the face — delightful),
  **fish_flavored_bait r1** ✓ (Fish-Flavored Toast — the literal item),
  **sizzle r1** ✓ (Dodo Stove), **sparkly_treasure r1** ✓ (Sparkly Shiny
  Dodoco), **explosives_workshop r1** ✓, **hide_and_seek r1** ✓ (namecards),
  **sparks_n_splash r1** ✓ (burst VFX frame, Klee amid fire — Burst card
  earns the action shot; nudge frame/crop if any UI shows),
  **gleeful_barrage → r2** ✓ (the full-frame spark bloom; r1 statue ✗).
- **All five companion TCG picks** ✓: barbara_melody, bennett_passion,
  fischl_nightrider, kaeya_frostgnaw, sucrose_gust.

### Replacements (with the fix)
- **big_badda_boom** ✗✗✗ (r1 wrong-card sigil / r2 damage numbers / r3
  minigame grid): use a VFX-dominant Charged-preview blast frame (register
  3), crop punched into the explosion.
- **blast_radius** ✗ (r1 is a checkerboard): Bomb-Tastic **AoE** renders
  exist in raw/ (Krash-Kaboom Mine AoE, Tomato Pepper AoE — the ring-blast
  tiles); use one, contain-mode. Else a wide blast frame.
- **jumpy_dumpty** ✗ (gameplay + '814'): Bomb-Tastic "Tomato Pepper Jumpy
  Dumpty" bouncing-bomb render — the toy IS the card. (jumpy_dumpty_mk2
  keeps the JTP fish-encounter art ✓ — but note it currently collides with
  fish_flavored_bait r3's alternate; mk2 owns it.)
- **mine_toss** ✗ (r1 is the mine TOY on cream bg — passable, but r2 grid ✗
  and r3 numbers ✗): keep r1 IF re-processed contain-mode; else Krash-Kaboom
  Mine AoE render.
- **bombs_away, flame_on_the_wick, quick_fuse, rapid_fire, crackle,
  sizzle-r3-class frames** ✗ (all tiny-Klee-in-grass): re-pick frame_pct
  into the blast or reassign register: **crackle ← the Pounding Surprise
  spark-clover VFX** (currently on remote_detonator — a small bright spark
  for a small bright card); **rapid_fire** ← a multi-explosion Normal-preview
  frame punched in; **quick_fuse r2** (mid-blast, no UI) acceptable after
  crop punch-in.
- **remote_detonator** ✗ (spark clover reassigned to crackle): **Kaboom
  King ride-on toy** (quick_fuse r1's current source — a detonator-toy
  reading) or Marvelous Magic bomb render.
- **boom_goes_the_dynamite ← r3** (Supersized Firework — the huge shell) ✓;
  this resolves its collision with crackle r1 sharing the same file.
- **endless_fireworks ← r3** (Fireworks Dance shell render; r1 smeared,
  r2 is a PLANT — "Mountain Fireworks" is a flower, classic wiki-title trap).
- **pocket_fireworks ← r1** (Fizzy Fireworks) but contain-mode re-process
  (currently smeared).
- **skip_and_hop** ✗✗ (r1 AND r2 are CRYING Klee on a cheerful 0-cost
  block+spark card — the single worst tonal gap in the set): ← Birthday
  2020 water-jump art (currently duck_and_cover r2 / spirited_away r3 —
  the joyful leap belongs HERE).
- **perfect_timing** ✗ (r2 sigil, r3 crying): r1 sticker acceptable;
  better: a winking/finger-guns sticker if one exists in Paintings set.
- **sorry_jean ← r2** (the sheepish pout — apology energy; r1's proud
  pointing Klee is the opposite of sorry).
- **cant_catch_me ← r1** ✓ (Birthday 2021) or the excited-dash sticker r2;
  fine either way.
- **spirited_away ← r1** (Summertime floater, re-processed contain) or
  keep r3 if skip_and_hop doesn't take the water-jump.
- **no_holding_back** ✗ (Multi Wish cropped to fabric): refocus the crop
  to her face/action (focus: top) or use Wish full art with top focus.
- **flame_dance** ✗ (r1 sleeping Klee on an aggressive card; r2 sigil):
  ← r3 Sparks-'n'-Splash bloom frame (distinct frame_pct from
  gleeful_barrage's pick to avoid a twin).
- **alchemical_curiosity, cluster_charge, hot_hands, snap** ✗ (sigil
  register, banned): re-pick per class — alchemical_curiosity ← an
  alchemy-table/item render; cluster_charge ← a multi-bomb Bomb-Tastic
  render; hot_hands ← the ouch/blowing-on-fingers sticker if present,
  else a close flame VFX; **snap** ← Sparkling Steps VFX close-up or a
  firecracker item (the C4-sigil choice was mine by precedent and it was
  the wrong precedent — sigils go to icons now).
- **dahlia_sacramental_shower, prune_witch_hunt** ✗✗✗ (all ranks are dark
  talent-demo screenshots, tiny figures, illegible at card size): these
  need NEW sources — their official character cards / splash art
  (register 5, matching how other companions use character-specific art).
  Search: "Dahlia Character Card", "Prune Character Card" wiki titles.

### Redirected to power/relic icon slots (out of card portraits, into the .pck queue)
Constellation Exquisite Compound, Blazing Delight, Nova Burst, Explosive
Frags, Chained Reactions, Sparkly Explosion (+ the rest of the
constellation set): native 128px, icon-shaped, thematically mapped to
Klee's constellations = the power/relic icon set almost authors itself
(e.g. spark_knight_style power ← Nova Burst; blazing_delight power ← its
own constellation). This turns ten rejects into a filled backlog item.

## Process directives (for the art tool, not the plan)
1. Item renders: `contain` on flat background — never `cover` (smear bug).
2. GIF picks: frame_pct is now a TASTE parameter — pick frames with zero
   UI/damage numbers; punch crops into the action.
3. Add a plan lint: no source file may be rank-1 for two assets (the
   big_badda_boom/blazing_delight and boom/crackle collisions were both
   this).
4. Register column: add `register: sticker|item|vfx|tcg|splash|icon` to
   plan.tsv rows so future picks declare their class and the lint can
   check class-appropriateness mechanically.
