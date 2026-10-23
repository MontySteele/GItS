# Yae text audit, 2026-10-23

The writing review, kit four (ruled 2026-10-23, `localization-2026-10-19.md`:
"her English pass happens now with the others, but her translation waits
for her Balance"; format: `kokomi-text-audit-2026-10-22.md`).

Read: every Yae card face, Ancient card, Annotation, relic, potion, power
badge and keyword tip, from `tools/player_text_census.py`, against
`docs/current/text-conventions.md`. Her shrine display and annotation
captions are code-built and go with the translation keying. The preview
misreads already on BACKLOG (Superconduct timing, Tenko's total, Pael's
Legion) are not repeated here.

## 1. Length

80 cards, none over the lint's 80 target list (the census flags none of
hers). Her faces are short; the drift is in words, not length.

## 2. Fixes (no number or rule changes)

1. **"Hand" is a capitalised pile** (the conventions' pile row). Ten faces
   print "in your hand": Proofread, Galley Proof, Footnote, Manuscript Pile,
   Margin Note, Reborn as Guuji Yae, Rewrite, Royalties, Sakura Seal, The
   Seven Glamours, and the Recall prompt ("Choose an Annotated card to put
   into your hand"). All become "Hand". (The lint's `hand-plain` rule misses
   the phrase before a colon; it is widened so it holds.)
2. **A bonus has its noun** (rule 8).
   - Kitsune Pounce: "deal 5 more" becomes "deal 5 additional damage".
   - Sesshou Fang: "deal 6 [8] more" becomes "deal 6 [8] additional damage".
   - Edict of Cleansing: "deal 3 [4] more" becomes "deal 3 [4] additional
     damage" (its badge already says so).
   - Fox's Shade: "gain 4 more" becomes "gain 4 additional Block".
   - Hide Behind the Shrine: "gain 5 more" becomes "gain 5 additional
     Block".
   - Red Ink: "deals 3 more damage and gives 3 more Block" becomes "deals 3
     additional damage and gives 3 additional Block".
3. **No parentheses or semicolons on a face** (rule 14).
   - Author's Copy: "Add a copy of an Annotated card in your Hand (not an
     Author's Copy) to your Hand." becomes "Add a copy of an Annotated card
     in your Hand to your Hand, other than an Author's Copy."
   - Fallen Petals: "withers (it acts once, its Last Bloom)" becomes
     "withers and acts once". "Last Bloom" is printed nowhere else.
   - Hide Behind the Shrine: "withers; if one did, gain 5 more." becomes
     "withers. If one did, gain 5 additional Block."
4. **One spelling of a Sakura's strikes.** Edict of Cleansing's "Your Sakura
   strikes deal" becomes "Your Sakura's strikes deal", as Electroculus
   reads. Thunderbolt Tithe's "for each Sakura standing" becomes "for each
   Sakura", as Petal Storm and Offertory Box read.
5. **Late Night Reading's "3 Sakura"** reads as exactly 3 once Sakura
   Channeling and Fox Ofuda let her hold 5. It becomes "3 or more Sakura"
   if the code's `three_sakura` test is "at least 3" (checked at build); if
   the test is "exactly 3", the face keeps its words and this goes to the
   next Yae card pass instead.
6. **Badge plurals.** Sakura Grove's badge "gains X Level", Fox's Mooncall's
   "X Level higher" and Serial Novel's "X random Annotated card" print the
   singular at any amount; each takes the plural hole the base uses
   (`Level{Amount:plural:|s}`).
7. **The Tenko tip.** "Every Sakura acts now. Refresh them to at least 3
   turns." becomes "Every Sakura acts now and goes back to at least 3 turns
   left."
8. **A stale Sakura line.** The census finds a third Sakura tip, "A totem
   that stays at your side all combat. At most 3 fire each turn.", which no
   longer matches the rules (Sakura last 3 turns; the shrine can hold more
   than 3). If a player can see it, it goes; the build finds its source.

## 3. Annotation rules in parentheses, on three Edit cards

Footnote, Royalties and Sakura Seal print their Annotation's rule in
parentheses: "Edit up to 2 [3] cards in your Hand: Footnote (when played,
draw 1 card)." Proofread and Margin Note do not ("Edit a card in your Hand:
Reprint."), and the Annotation's own face is its hover (`Footnote`: "When
this card is played, draw 1 card."). Without them: "Edit up to 2 [3] cards
in your Hand: Footnote."

## 4. Arithmetic signs in the Sakura tips

The Sakura tips read "strikes an enemy for 1 + 2 per Level", "hits ALL
enemies for 1 + its Level", "you gain 2 + its Level Block". The base game
prints no "+" in prose. In words: "deals 1 damage plus 2 for each Level to
an enemy", "deals damage equal to 1 plus its Level to ALL enemies", "gain
Block equal to 2 plus its Level". Each grows by 5 to 10 characters; all
stay under the 135 tip ceiling.

## Picks

1. **Section 2's eight fixes.** (a, default) build them all. (b) all but
   named ones.
2. **Annotation rules in parentheses.** (a, default) they go; the
   Annotation's hover carries the rule, as Reprint's and Red Ink's do. (b)
   keep them, since a new player reads the effect without hovering.
3. **"+" in the Sakura tips.** (a, default) words, as above. (b) keep the
   signs, which are shorter.

## Ruling, 2026-10-23

[USER]: "Agreed on all Varka, Furina, Yae and Shared fixes - these makes
sense to me!"

1. **Pick 1 (a), built.** All eight fixes. Fix 1 caught an eleventh face,
   Inked Branches' upgrade ("and a card in your [gold]Hand[/gold]"), and the
   Recall prompt now reads "put into your Hand". The lint gap was scope, not
   the colon: `proto_ym_*` faces were outside `IN_SCOPE`, so
   `tools/lint_text_conventions.py` now holds them to the pile spellings and
   the no-parentheses rule (`YAE_SPELLINGS`), with a self-test fixture for
   "in your hand:". Fix 4 also took Edict of Cleansing's badge to "Your
   Sakura's strikes".
   - Fix 5: `three_sakura` is `YaeShrine.Count(Owner.Creature) >= 3` in C#
     and `sakura_count(...) >= 3` in the sim, so Late Night Reading reads
     "If you have 3 or more Sakura".
   - Fix 8: the totem line is `ArmKeywordTips.ForSakura`'s branch for a
     card that is not Yae's, and the one card it reaches is the universal
     Inazuma Companion "Yae Miko, Sesshou Sakura" (every kit can draft it).
     It describes that card's `SesshouSakuraPower` correctly (lasts all
     combat, at most 3 fire each turn), not Yae's shrine, so it stays.
2. **Pick 2 (a), built.** Footnote, Royalties and Sakura Seal print "Edit
   up to 2 [3] cards in your Hand: <Annotation>."; each already hovered its
   Annotation's tip, and codegen now owes Sakura Seal the Sakura tip the
   parenthesis used to carry.
3. **Pick 3 (a), built.** Foxfire and Kitsune as the paper gives them. The
   Sakura tip in the paper's words was 109 characters, over the
   100-character player hover cap, so it reads "At the end of your turn,
   deals 1 damage plus 2 for each Level. Lasts 3 turns, then strikes again."
   (the main session's wording). `lint_hover_tips.py` now measures the
   `@YaeSakuraTip` placeholder by its text, so the cap is held in the lint.
