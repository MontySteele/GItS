# Kokomi text audit, 2026-10-22

[USER]: "Given how many changes we did, can you please do an audit of
Kokomi's text surfaces? I want to make sure we're still following common
conventions with the other new characters and the base game where possible,
that cards don't have unnecessarily long text, etc."

Read: every Kokomi card face, power badge, relic, potion, keyword tip and
story event, from `tools/lint_text_conventions.py --census` and
`klee-mod/localization/reference/eng.json`, against
`docs/current/text-conventions.md` (rules measured on the base game).
Lengths are rendered characters, as the lint counts them.

## 1. Length

| Kit | cards | median | over 80 (target) | over 100 |
|---|---|---|---|---|
| Kokomi | 84 | 77 | 39 | 17 |
| Klee | 85 | 61 | 20 | 8 |
| Varka | 88 | 63 | 18 | 4 |
| Furina | 80 | 58 | 13 | 2 |
| Base game | 624 | 47 | | 1 |

None is over the 120 ceiling. Most of the gap is structural: 45 of her
cards print two modes ("X. Or plan: Y."), and the base game has no modal
card. A two-mode card with two short halves (Kurage's Oath, 58; Spearhead,
64) reads fine. The fat is in about ten cards, listed in section 3, and in
one clause repeated across ten carriers (section 2).

Her upgrades follow the base: add-clauses are short (" Draw 1 card.",
" and draw 1 card"). Three Powers upgrade only to Innate (Treatise, Kurage
Bloom, Endless Shoal), the pattern [USER] has flagged before; that is for
the next card pass, not this one.

## 2. "Stings and Wards don't count", three spellings on ten carriers

- "Stings and Wards don't count." Riptide Ruin, Battle Formation, Kurage
  Canopy, Watatsumi's Grace.
- ", not Stings or Wards" Feint, Turning Tide, Tideturn, Ayato (Companion).
- "a Plan that is not a Sting or Ward" Endless Shoal.

And the counting is not uniform: Breakwater, Shoal of Spears, Sango Isshin,
Following Current, Resolve and the Casket do count Stings and Wards. A
player reads the exception card by card.

## 3. Convention breaks (fixes; no design change)

1. **"written" is the retired verb** (rule table: plan is "the one verb").
   Opening Gambit: "The next Plan written this turn deals double damage." to
   "The next card you plan this turn deals double damage." Second Wave:
   "The Plan written after it this turn is carried out twice." to "The next
   card you plan this turn is carried out twice."
2. **"the front enemy" on a card line** (rule 3; a Plan already hits the
   front enemy). Undertide Lance's Plan: "Deal 22 Hydro damage to the front
   enemy." to "Deal 22 Hydro damage."
3. **A repeating trigger is "Whenever"** (rule 17). Resolve of Watatsumi:
   "When a Plan is carried out" to "Whenever a Plan is carried out".
4. **A bonus has its noun** (rule 8). Riptide: "Debuffed enemies take 3
   additional." to "Deals 3 additional damage to debuffed enemies."
5. **"for each", never "per"** (base wording). Turning Tide: "per Plan
   carried out this turn" to "for each Plan carried out this turn".
6. **One spelling of "intends to attack"**: Evening Watch's "for each enemy
   intending to attack" to "for each enemy that intends to attack", as on
   four other cards and Sea's Reproach.
7. **A Plan line happens when it is carried out, so it says "this turn"**.
   Coordinated Strike's Plan says "Next turn, each other player's Attacks
   deal 3 additional damage", but the bonus lands on the turn it is carried
   out (`KokomiPlan.cs`, the Coordinated Strike note): "Each other player's
   Attacks deal 3 additional damage this turn." Pincer's "that turn" to
   "this turn".
8. **Plan lines don't restate when they are read.** Flank's and Tide Wall's
   "when this is carried out" go (every Plan line is read then; Coral Crash
   already omits it): Flank 112 to 87, Tide Wall 103 to 78.
9. **A card says what, not why** (rule 15). At Water's Edge's trailing
   "Plans count." goes (108 to 95): a Plan hit is Hydro damage you deal, and
   the Plan tip says so.
10. **American English** (rule 16). Coral Light: "the colour of the reefs"
    to "color"; Report from Gorou: "her favourite" to "favorite"; Tide Comes
    In: "towards the sea" to "toward".
11. **The defence pass dropped "to your Hand"** from Kurage Canopy ("add a
    Ward.") to fit the ceiling; every other card says "add ... to your Hand".
    Dropping "of your" from the condition fits it back: "if 2 or more Plans
    were carried out, add a Ward to your Hand." Battle Formation shares the
    condition, so it changes the same way.
12. The docs' own Tamakushi Casket line (`text-conventions.md`) still quotes
    the retired "if a Plan is waiting, gain 3 Block"; it is updated to the
    shipped face.

## 4. Two near-duplicates (design, not text)

- **Flank** (Uncommon, 8 damage; Plan 11 to each enemy that intends to
  attack) and **Coral Crash** (Common, 8; Plan 8, the same) print the same
  card. Coral Crash came from the taste audit yesterday; Flank is now its
  bigger copy.
- **Steady Tide** (Uncommon, 9 Block; Plan draw 3) and **Tidal Screen**
  (Common, 7 Block; Plan draw 2), the same again.

Sting, Tidal Surge and Tamakushi's Wrath share a template ("Deal X. Or plan:
Deal Y to ALL enemies.") at three costs and rarities; that one is fine, as
Strike and its upgrades are.

## Picks

1. **Section 3's twelve fixes.** (a, default) build them all; no number or
   rule changes. (b) build them except named ones.
2. **The Stings and Wards clause.** (a, default) one spelling everywhere,
   the ruled "Stings and Wards don't count." as its own sentence; Endless
   Shoal becomes "Whenever the Bake-Kurage carries out a Plan, add a Sting
   to your Hand. Stings and Wards don't count." (b) one spelling, the short
   ", not Stings or Wards" (saves about 8 characters on six cards but
   re-words Battle Formation and Canopy, which you ruled). (c) a rule
   change: Stings and Wards never count as Plans for other cards (the Casket
   excepted, as you ruled), said once on their tip, and the clause leaves
   every card; Breakwater, Shoal of Spears, Sango Isshin, Following Current
   and Resolve would stop counting them (a balance change).
3. **The duplicates.** (a, default) a BACKLOG line for the next Kokomi card
   pass: rework Flank and Steady Tide into something Coral Crash and Tidal
   Screen don't already print. (b) rework them now.

## Ruling, 2026-10-22

[USER]: "Agreed on all defaults for 1534!"

1. (a) Section 3's twelve fixes are built.
2. (a) One spelling, "Stings and Wards don't count." as its own sentence,
   on every carrier; Endless Shoal reads as written in pick 2.
3. (a) Flank and Steady Tide go to BACKLOG for the next Kokomi card pass.
