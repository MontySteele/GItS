# Klee art red-pen — round 3 (final verdicts) (2026-07-21, chat + user)

Eyes-on review of the 20 portraitless Klee cards AND the splash-reprocess
set, rendered at true 500x380 card size (the render is what surfaced the
cover-clip failures below). All calls USER-RATIFIED. Feeds plan.tsv +
the cover_autocrop mode from companion-art-plan-addendum.md.

## LOCKED sources (render these)

Splash / cover_autocrop @ 6%:
- **sweet_dreams** (elemental_ecstasy id) <- Klee Birthday 2025.
  cover_autocrop. Renders great; the rename earns it.
- **sparkly_explosion** <- Klee Birthday 2021. cover_autocrop. NOTE faint
  "GENSHIN" promo watermark bottom-right; accepted.
- **sugar_rush** <- Klee Birthday 2024 - Shorts. cover_autocrop.

Contain (cover clipped the FIGURE -- per-card fallback, the mechanism the
companion pass established):
- **the_big_one** (grand_finale id): NEW SOURCE <- **Item Supersized
  Firework** (ornate bomb-orb), cover_autocrop. Replaces Klee Multi Wish,
  which (a) clipped her head under cover and (b) was already a DUPLICATE
  (no_holding_back auto + blazing_delight r2). A big ornate bomb fits a
  rare damage finisher better than any portrait. Dedupe-clean.
- **patched_dress** <- Klee Birthday 2023, **contain** (cover cropped her
  head). Full figure, autumn dress reads. Faint GENSHIN watermark;
  accepted.
- **tail_of_flame**: NEW SOURCE <- **Pounding Surprise Explosive Spark
  Effect** (the glowing clover-spark), cover_autocrop. The old Klee Vision
  source cover-cropped to her shorts (no face, no flame). Abstract pyro
  reads "fire" better than a portrait here; it's her own spark motif.

Item / contain-on-cardbg @ 0.99 fill:
- **secret_stash** <- Item Kaboom Box. Upscaled, punchy.
- **fish_blasting** <- Item Fish-Flavored Toast. Upscaled, clean.
- **trip_wire** <- Krash-Kaboom Mine sticker, **Lanczos upscale accepted**.
  Native source is 132x120 (a ~4x blow-up), but the stylized cartoon bomb
  reads as art-style-soft, not blurry -- user tested and accepted. It'll
  be the smallest-native card; fine.

Sticker / cover:
- **surprise_visit** <- Klee Expression 3. cover. Wide-eyed read works.

## REJECTED this pass (back to portraitless / rehunt)
- **spooked** <- Paimon's Paintings 07 Klee 2: REJECTED. Enough chibi art
  already, and it duplicated the register. Rehunt or leave portraitless.
- **dodge_roll** <- Klee Expression 1: REJECTED. Surprise Visit is the
  better version of basically the same face; no need for both. Rehunt or
  leave portraitless.

## Still needing sources (unchanged from round 2, not re-litigated here)
- Bomb-manipulation cards (chain_fuse, chained_reactions,
  controlled_demolition, careful_arrangement): redirect to individual
  Jumpy Dumpty item sprites -- NOT event banners (banners crop to text
  smear; re-confirmed this pass with the Bomb-Tastic banner reject).
- study_of_explosions: rehunt (Stage-6 UI panel rejected round 2).
- bright_idea: rehunt (both round-1 candidates weak).
- The 4 companion-synergy cards (best_friends_forever, borrowed_brilliance,
  study_buddy, friendly_visit): deferred to companion art (they depict
  companions) -- pair from companion sources per companion addendum.
- spooked, dodge_roll: newly portraitless per above.

## Pipeline lesson (record it)
cover_autocrop is excellent for splash art where the figure is LARGE and
CENTERED, but FAILS on sources where the character is small-in-frame or
off-center -- it zooms into the wrong body part (the_big_one -> torso,
tail_of_flame -> shorts, patched_dress -> chest). So **cover REQUIRES the
per-card contain fallback**, same as companions. Consider a lint/warn:
flag when the cover crop's figure-center sits far from the crop center, or
when the opaque figure occupies <50% of the cover output height -- a
likely head/limb clip. Catch->lint, third instance of the pattern this
week (unique-name, dedupe, now clip-detect).

---

## EXECUTION REPORT (Code session, 2026-07-21) — 7 of 10 locked picks are double-booked

Landed clean: the `cover_autocrop` mode, the lint work, and the splash
re-sweep. **The locked source list did not land**, because the lint caught
that almost all of it is already spoken for.

### The blocker: round 2/3 hunted a source pool that was NOT free

Every source below is ALREADY the effective (rank-1 or auto) pick of a
shipped card. L1 flagged all six on the first run; a seventh came from
round 2's own trip_wire note:

| card | ratified source | already owned by |
|---|---|---|
| grand_finale (The Big One) | Item Supersized Firework | **boom_goes_the_dynamite r1** (also crackle r2) |
| tail_of_flame | Pounding Surprise Explosive Spark Effect | **crackle r1** |
| patched_dress | Klee Birthday 2023 | **warm_glow (AUTO)** |
| sparkly_explosion | Klee Birthday 2021 | **cant_catch_me r1** |
| secret_stash | Item Kaboom Box | **pop r1** (power icon reuse is legal, ignore) |
| fish_blasting | Item Fish-Flavored Toast | **fish_flavored_bait r1** |
| trip_wire | Krash-Kaboom Mine *sticker* | **mine_toss r1** |

trip_wire's premise was explicitly "the STICKER vs their board crops --
the dedupe lint should confirm distinct files." It cannot: the family has
only TWO files (`...Krash-Kaboom Mine.png`, 132x120, = mine_toss r1; and
`...Krash-Kaboom Mine AoE.png`, 200x200, = explosive_frags r1). There is
no third distinct image for a third card.

The six rows are written, mode/fit/register verified, and render correctly
— they sit **commented out** in art/plan.tsv under a PARKED banner, one
uncomment away. USER RULING NEEDED per row: which card keeps the source,
and does the loser re-point or go portraitless? (Note patched_dress's
rival, warm_glow, holds an AUTO pick — mechanically assigned, never
eyes-on — so it is the weakest claim in the table.)

### Sources not present locally (cannot render regardless)
- **sugar_rush** <- "Klee Birthday 2024 - Shorts": not fetched. The similar
  `Klee Birthday 2024.png` IS present but is gleeful_barrage's r1, so it is
  not a substitute.
- **surprise_visit** <- "Klee Expression 3": not fetched.

### Pipeline lesson, confirmed and narrowed
`cover_autocrop` is a large win where the figure floats in a void
(Klee Wish: content is 35% of a 2048x1024 canvas — the figure goes from a
blob to card-filling) and a **no-op where the source is full-bleed** (the
Birthday renders are 100% opaque, so autocrop crops nothing and the result
is byte-identical to `cover`). So §4's "re-process all Klee splash keeps"
only actually changes big_badda_boom.

### Lints
- **L6 clip-detect landed as a WARN** (round 3's ask). `tcg` is excluded:
  trading-card sources are portrait-shaped, so a landscape crop always
  trims ~56% by construction and they buried the real signal in nine false
  ones. It currently flags exactly one card: **no_holding_back trims 76% of
  Klee Multi Wish** — the same source round 3 rejected for the_big_one
  because it clips Klee's head. That card is already shipped; worth a look.
- **L4 relaxed** to allow `cover_autocrop` on `item`, but only with fit
  `contain`. Rationale: L4 exists because cover smears an item's
  transparent edges, and autocrop removes that margin by construction —
  while cover-FILLING a small item still crops it (Item Supersized
  Firework would lose 37% of its height that way).
- **BUG FOUND, PRE-EXISTING: art_lint's register rules have never run.**
  `read_plan` split on `"\n"` while the file is CRLF, so the last column
  kept a trailing `\r` and every register compared as `"item\r"`. L2 was
  shouting "unknown register 'item'" about a register plainly in the
  allowed set (61 rows), and **L3 and L4 were dead code** — they test
  `reg == "icon"` / `== "item"` and never matched. Fixed in art_fetch.
  With the parser repaired, no L3/L4 violations exist in the current plan.
