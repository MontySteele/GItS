# Kokomi: after the finish round, 2026-10-19

The finish round (`review/records/kokomi-finish-round-2026-10-19.md`) had
two wins in five seats with a 46.2 mean, her best round so far. She lost
less HP than the base characters in every act's normal fights, so the
defence trigger did not fire and Ward stays a draw. The losses were act-3
bosses and an act-3 elite, each to a Block shortfall after damage-first
drafting.

## What I'll do without a pick

**Check and fix the eight screen and bug items in the record**, each
verified in code first:
- Tamakushi Casket's text against Stings; ruled 2026-10-20: it pays only
  when a card is Planned or a Companion is played ("2 was definitely the
  intent, and we should figure out a different Block solution if needed");
- Tide Wall and Flank naming when they read intent ("when carried out");
- At Water's Edge showing it is spent;
- Ripple Basin's Block when an Attack is planned;
- Red Mask and Bag of Marbles at combat start.

A wording fix lands as text; a real bug gets fixed. Neither changes a number.

## The weak cards: shown, not cut

The seats called four cards dead. Their texts and evidence:

| Card | Text | Evidence |
|---|---|---|
| Sea Glass Harvest (U Skill, 1) | Gain N Block. Or plan: Transform every Status and Curse you have into Sea Glass. | taken 2 of 4; "never worth it" (lane 1) |
| Sangonomiya's Orders (U Power, 2) | At the start of your turn, add a random Common Inazuma Companion to your Hand. It costs 0 and is Ethereal. | taken 2 of 7; "automatic" (lane 1) |
| War Council (U Skill, 1) | Apply N Weak to ALL enemies. Or plan: Gain 2 Energy. | taken 2 of 3; "worst card" (lane 2) |
| Gorou — Crystal Collapse (U Skill, 1) | Play on the Bake-Kurage. Plan: Play a copy of the last Companion card you played. | taken 1 of 7; dead until a Companion is played (lane 4) |

Battle Formation was offered twice and never taken, and Grand Design was
taken once (played six times). That is too few sightings to judge either.

Five seats is thin, and [USER]'s own play judges fun. The four cards wait
for that play, not for this paper.

## Rulings

Ruled 2026-10-19. Pick 2 went (b): [USER], "let's review the weak cards now
for any obvious fixes." Pick 1 takes its default (a). The weak-card review
became the table below ([USER]: "This table looks good. Ship it").

## The weak-card and upgrade pass (ruled, built next)

[USER], 2026-10-19: "can we make sure that if you upgrade a Plan card, both
the Plan and non-Plan sides get upgrades where possible?", "Sea Glass
Harvest's block rate sounds quite high", and "make sure Sea Glass Harvest has
a tooltip that shows what Sea Glass does, the same way Defect's Compact shows
what Fuel does".

- **War Council:** Weak 2 [3] to ALL; Plan: 2 Energy [and draw 1].
- **Sangonomiya's Orders:** the upgrade makes the Companion upgraded,
  instead of Innate.
- **Gorou — Crystal Collapse:** "Plan: Play a copy of the last Companion
  card you played. If you haven't, play a random Common Inazuma Companion."
- **Sea Glass Harvest:** 8 [11] Block (was 10 [13]). Its face gains a Sea
  Glass card preview, as Compact previews Fuel.
- **Steady Tide:** 9 [12] Block (was 11 [14]); Plan: draw 3 [4].
- **Both sides upgrade:**
  - Ambush: Vulnerable 2 [3], Plan 12 [15].
  - Read the Field: Plan's fetched card costs 1 less this turn [upgraded].
  - Pincer and Second Wave: Plan [and draw 1].
  - Opening Gambit: Plan Vulnerable 1 [2] to ALL.
  - Tidal Screen: Plan draw 2 [3].
  - Kelp Wall: Plan [+4] damage.
  - Kurage's Wake: Plan 3 [4] Stings.
  - Spearhead: Plan Vulnerable 2 [3] to ALL.
  - Joint Orders: Plan ally draws 2 [3].
  - Coordinated Strike: Plan +3 [+4].
- **Turnabout:** the cost-only upgrade becomes Plan damage +5.
- **The two Gorou cards with no upgrade** (Inuzaka All-Round Defense, Juuga)
  get one on both sides if the generator gives them none.
- **Kept:** Ward (a two-draw 0-cost would beat anything base) and the
  Plan-only cards.
- **The Shape of Water** counts Brine Sting (pick 1 (a)).

## Kokomi balance audit, 2026-10-21 (ruled, built)

From her run's telemetry: Princess of Watatsumi dealt 17% of the run's
damage with Strength 8 (War Banner+ and Nicole), and Sea Glass Harvest
reached Statuses in the draw pile. [USER], 2026-10-21: "Agreed all around".

- **Princess of Watatsumi:** Plan: Deal 5 [8] Hydro damage to ALL enemies 3
  times (was 3 [5] five times). The now-line is unchanged. Expected in the
  Balance suite: her damage share falls, since Strength now counts 3 times,
  not 5.
- **Gorou — General's War Banner:** the upgrade adds Block only: "Gain 10
  Block. Plan: Gain 1 Strength." (was 2). Expected: Strength per play halves
  when upgraded.
- **Sea Glass Harvest:** Plan: Transform every Status and Curse in your Hand
  into Sea Glass [+] (was the hand, draw pile and discard pile). Tidecleanse
  is unchanged. Expected: its Energy from Statuses falls in Status-heavy
  fights.

## Act-3 tempo, 2026-10-21 (ruled, built)

The suite after the audit (`review/records/kokomi-balance-suite-2026-10-21.md`)
was under base on damage in every act, 0.76 in act 3 (0.68 the round before).
The seats' HP gap was read as drafting: they skipped every planned-Block card
offered and planned Kurage's Oath for damage 71 times of 81. [USER]: "Let's go
with your proposed defaults and see how we land." Built:

- **Watchful Shoal:** Stings deal 5 [7] more (was 4 [6]). The paper offered
  "+3 [5]" from a misread of the sheet; +1 on both sides was the intent.
- **Following Current:** 4 [5] per Plan carried out (was 3 [4]).
- Tide Wall stays Uncommon; no Block change.

Expected effect, graded by the next suite: act 3 damage a turn up about 3 to 5
in decks holding either power; acts 1 and 2 barely move.

## Picks (as offered)

1. **The Shape of Water and Brine Sting.** The card says "for each Sting you
   played this turn"; only the token Sting counts, not Brine Sting.
   - **(a, default)** Count Brine Sting too: the face says Sting, and a
     player will read it that way.
   - (b) Keep the rule and say so on the card: "for each Sting token".
2. **What comes next.**
   - **(a, default)** [USER]'s play of Kokomi at her finish line, once the fixes
     above are in. A card pass on the four weak cards follows, from that play
     and this round together.
   - (b) The weak-card pass first, then [USER]'s play.
