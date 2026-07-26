# Sprint addendum — art vibe-check outcomes (2026-07-20, chat → Code, USER-RATIFIED)

Rides alongside the standing GO (bomb ops → codegen widening → companions);
nothing here blocks that sequence. Source: chat art review with the user's
eyes on the fetched sources (contact-sheet method; the two Bomb-Tastic
board crops were reviewed on the user's screen, not chat's).

## 1. Two renames (display name ONLY — ids stay stable)

The user ruled: rename to fit the chosen art rather than rehunt it.

- `elemental_ecstasy` → **"Sweet Dreams"**. The effect (refresh_all_auras
  + draw per aura) makes the sleeping Birthday-2025 art a natural fit —
  the nap IS the refresh, the draws are the dreams. The old name implied
  reaction-rapture the card never delivers.
- `clockwork_toy` → **"Imaginary Friend"**. Straight from the chosen
  item's own name (Imaginary Friend Dodoco); block 5 + 3 Burst Energy
  reads as a friend who shields and encourages. Nothing was clockwork
  about it.

Execution: sheet `name:` fields + the hand-written C# display names;
ids, tags (skill_tag stays on clockwork_toy), upgrades, art-plan keys,
and manifest all keyed by id — untouched. Parity lint should confirm the
pairing post-rename. Rationale for keeping ids stable is on record:
id-renames churn class files, manifest, upgrade sheet, and DECISIONS
references for zero player-visible gain; if codegen makes a full rename
genuinely cheap, the session may propose it, but it is not required.
Note in DECISIONS that display names and ids now diverge for these two —
future greps should try both.

## 2. Art dedupe lint (catch → lint; this batch's instance of the pattern)

New plan.tsv lint: **fail when one source (wiki_title) lands as the
EFFECTIVE pick in two or more card-register slots** (out-paths under
/cards/). Rules:
- "Effective pick" = auto rank 1, or shortlist rank 1 unless the red-pen
  has resolved otherwise.
- Register-crossing reuse is LEGAL (a card sharing its OWN power icon's
  source is natural; splash/model/select reuse doesn't collide with
  cards).
- Known collisions to resolve or bless when the lint lands:
  a. Jumbo Sparks 'n' Splash Statue: catalytic_conversion card + burst
     meter badge → RESOLVED by §3 (statue keeps the badge only).
  b. Imaginary Friend Dodoco: clockwork_toy r1 + duck_and_cover r3 →
     bless (duck_and_cover's effective pick is r1; r3 is dead unless the
     red-pen revives it — the lint's effective-pick rule handles this).
  c. Sparkling Steps Emoji 3: rapid_fire r1 + da_da_da r2 → real
     potential collision; resolve at the red-pen session (rapid_fire's
     "softness" flag may retire its r1 anyway).
  d. Klee Wish: big_badda_boom r1 + selection_splash → register-crossing
     (card vs splash), LEGAL under the rules; document as the worked
     example.

## 3. Asset changes (the replace list, user-passed)

- `spark_knight_style` ← **Klee Character Card.png** (the regular TCG
  card; currently only a model source, no card-space collision). Forms
  the deliberate pairing: regular card = the Style, golden card
  (true_spark_knight, unchanged) = the True. Retire Glimmering Firework
  (teal Fontaine flora; wrong color, wrong everything — confirmed by
  eyes).
- `catalytic_conversion` ← **Item Dodoco's Marvelous Magic.png**,
  promoted from its power icon (which keeps it — same-referent sharing
  is legal). The plan's own justification comment already argued
  "Marvelous Magic = conversion." The Jumbo statue stays EXCLUSIVELY the
  Burst meter badge.
- `bright_idea`: REHUNT. Both current candidates confirmed weak (r1
  generic cheer, r2 reads as crying/panic — the opposite of the card).
  Hunt term: a realization gesture — exclamation, lightbulb,
  raised-finger — across the emoji/sticker sets. r1 stays placeholder
  (null-safe already governs) until the hunt lands.
- `dahlia_*`: hunt for a **Dahlia Equipment Card** first (register
  consistency with the five auto companions, all frameless talent art).
  If none exists, take r1 (Character Card — legible, accept the frame
  clash) over r2 (Wish render floats small at card scale).
- Passed as-is by the user's review: crackle r1 (spark VFX), playtime
  forever, true_spark_knight, vermillion_pact, and the icon queue
  (element SVGs; constellation sigils correctly living as power icons).
- The elemental_ecstasy crop question is DEAD — the rename makes the
  uncropped art correct.

## Reminder riding along
The tier05 M7 stale assertion (catalytic_conversion hard-coded as
unappliable) still needs its fix if not already landed: derive the
unappliable set from the upgrade engine; hot_hands is the sole member
now. And the pre-deploy gate runs the FULL suite, scope named.
