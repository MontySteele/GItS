# Klee art red-pen — round 2 (2026-07-21, chat → Code, USER-RATIFIED)

Eyes-on vibe check of the 20 portraitless Klee cards, plus a name-collision
fix and a new validation lint. Sources fetched from the wiki and reviewed on
a contact sheet (`docs/klee-art-hunt-contactsheet.png`). Effect text pulled
per card so art matches mechanic, not just name.

## A. Name-collision fix + new lint (the "Grand Finale" catch)

**USER CATCH:** "Grand Finale" is also a Silent card (base game / Downfall).
Confirmed real; the repo has NO base-game card list to check against, so
this class of collision can only be caught by a hand-maintained list.

Landed:

- Renamed `grand_finale`'s display name **"Grand Finale" → "The Big One"**
  (id `grand_finale` UNCHANGED, per the id-stability convention). Klee's
  cheerful-demolition voice; still reads as the +2-per-detonation scaling
  finisher.
- New lint: `tools/lint_unique_names.py`, wired into
  `test_sheet_lints.py::test_card_names_are_unique` (runs every deploy).
  Two guarantees:
  - **INTERNAL:** no two cards across the four mod sheets share a display
    name (automatic; currently 183 names, all unique).
  - **RESERVED:** `docs/reserved-card-names.txt` lists names taken by
    content OUTSIDE the repo (base game, other mods). Seeded with the
    user-confirmed "Grand Finale | base game / Downfall Silent". A mod card
    matching a reserved name fails the lint. This list is the ONLY defense
    against cross-mod clashes (the engine resolves them unpredictably) —
    curate it as playtest / cross-mod testing surfaces more.

Treat the reserved list as **append-only lore**: add names as found, never
prune without a reason on record.

## B. Card art verdicts (the 20 portraitless Klee cards)

### KEEP — strong fits, lock these

- `spooked` ← Icon Emoji Paimon's Paintings 07 Klee 2 (startled chibi; also
  the sticker Klee's Spooked!-parity was measured against — closes a loop).
- `patched_dress` ← Klee Birthday 2023 (autumn-leaf dress; block card,
  literal + warm).
- `secret_stash` ← Item Kaboom Box (treasure box you crack open for 2 free
  commons; near-perfect object match).
- `sugar_rush` ← Klee Birthday 2024 Shorts (energetic; energy+Spark burst).
- `fish_blasting` ← Item Fish-Flavored Toast (her fish dish; the fish-bomb
  AoE; unmistakable).
- `tail_of_flame` ← Klee Vision (the Pyro Vision itself; a pyro damage card
  — literal element).

### KEEP with a dedupe note

- `the_big_one` (`grand_finale`) ← Klee Multi Wish (fireworks-celebration
  finale; the more specific claim on this source — see collision below).
- `trip_wire` ← Krash-Kaboom Mine sticker (correct object: 7-dmg bomb +
  Weak). Third card drawing on the Krash-Kaboom Mine family (`mine_toss`,
  `explosive_frags` are the others) — OK because this is the STICKER vs
  their board crops, but the dedupe lint should confirm distinct files.

### ACCEPTABLE but samey — ship as placeholder, upgrade later

- `dodge_roll` ← Klee Expression 1, `surprise_visit` ← Klee Expression 3:
  plain expression busts. The deck is already chibi-face heavy; these read
  placeholder. Fine to ship, flagged for a later pass.

### REJECT — wrong source TYPE, redirect the hunt

- `chain_fuse`, `chained_reactions`, `controlled_demolition` ← event BANNERS
  (Boom-Bastic / Bomb-Nanza wide title cards with baked-in text). At
  500x380 they crop to a text smear. **REJECT.** Redirect: these
  bomb-manipulation cards should draw from individual Jumpy Dumpty item
  sprites (Tomato Pepper / Mint Jelly / Caramel Cookie / Berry Cake Jumpy
  Dumpty .pngs) — clean single objects, the same idiom the shipped bomb
  cards already use.
- `careful_arrangement` ← Board (a game-board photo). Same wrong-shape
  problem; move-bombs is hard to depict, so shortlist a Jumpy Dumpty crop
  and accept it's abstract.
- `study_of_explosions` ← Stage 6 Complete (a victory-screen UI panel, not
  art). **REJECT**; rehunt an emoji or a Klee-studying image
  (scry/discard Burst — a "reading the blast" beat).

### DEFER to the companion art pass (these should depict COMPANIONS)

Their mechanics are about companions, so their art should show one — which
lives in companion art not yet loaded here:

- `best_friends_forever` (copies all companions played — wants a
  Klee+companion group shot; ALSO collides with `the_big_one` on Multi
  Wish, so it needs its own source anyway).
- `borrowed_brilliance` (copy a companion card in hand).
- `study_buddy` (replay next companion).
- `friendly_visit` (companion cards cost less; the source tried 404'd).

Park all four; hunt them WITH the 9 Mondstadt + 12 Fontaine companion
portraits in the dedicated companion pass. Chat can't vibe-check companion
art — Prune/Dahlia sources already showed those postdate chat's knowledge;
that pass needs the user's eyes or a session that can load the companion
lore.

### STILL OPEN from round 1 (carried)

- `bright_idea` rehunt (both candidates weak: r1 generic, r2 reads as
  crying/panic).
- The two `PENDING_RED_PEN` dedupe collisions from the sprint addendum.

## C. Dedupe lint — new collisions this pass surfaced

Feed these to the art dedupe lint (from the sprint addendum) so they're
caught mechanically, not by memory:

- **Klee Multi Wish:** `the_big_one` (keep) vs `best_friends_forever`
  (defer → gets its own source). Resolves once BFF moves to companion art.
- **Krash-Kaboom Mine family:** `mine_toss` / `explosive_frags` (board
  crops) vs `trip_wire` (sticker) — confirm distinct files, then bless.
- Round-1 collisions still stand (statue, Imaginary Friend, Sparkling Steps
  Emoji 3, Klee Wish) — see `sprint-addendum-art.md`.

## Sequencing

None of this blocks the build (bomb ops / codegen / companions). The rename
+ lint land now (cheap, and the lint protects every future card). The
bomb-card redirects and `study_of_explosions` rehunt are a small art-fetch
task; the four companion-synergy cards wait for the companion pass by
design.
