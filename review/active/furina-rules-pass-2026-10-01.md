# Furina: the rules pass

Paper, 2026-10-01. Main session design, from an Opus audit of her rules, pool,
text and lore (2026-10-01, read-only; its findings are cited below). **All
picks RULED 2026-10-01.**

## 1. Why

[USER], on the project check-in: "she finally has a good design to stand
around, but let's do a similar audit (rules, card pool, lore) to look for what
we can improve upon." The audit's main finding: two rules account for most of
what seats learn from the combat log, not from the cards. They are the
front/back split for paying a Spend, and a gain on an empty stage summoning
someone. Its clearest sign: two cards exist mainly to soften rule 8, Palais
Ledger and the new Ancient, Center of Attention.

## 2. The rule changes (brief §3)

1. **Rule 8: a Spend pays from the back performer first, then forward.** If
   the whole stage holds less than N, the Spend mode cannot be chosen.
   [USER]: "Agreed, spending start back-forwards." The front-is-the-shield,
   back-is-the-bank split stays: the bank empties first. Center of Attention
   (the new Ancient) keeps its job, the first Spend each turn is free, and
   drops its "even when your back performer has too little" clause. **Palais
   Ledger** was exactly this rule, so it needs a new job: "Your Spends cost 1
   less Fanfare." (Rare relic, unchanged rarity.)
2. **Rule 5's empty-stage summon: only what you play summons.** A card or
   potion you play that gives Fanfare, on an empty stage, summons a random
   performer holding it (Rising Applause, Cheered On, Warm Reception, Bottled
   Applause). A gain from a Power, a relic or a reaction trigger does nothing
   on an empty stage (Season Tickets, Thunderous Applause, Tide of Applause,
   the Ancient's turn-start Raise). A gain naming "each performer" has nobody
   to land on (Grand Deluge). The Fanfare tip says it in one line: "If no one
   is on stage, a card that gives Fanfare summons a random performer holding
   it." [USER] on the original rule: "When you Summon on Necrobinder with Osty
   dead, it re-summons him... there's also no way to resurrect the dead Usher
   in the starter deck, so the Fanfare card becomes a brick"; on this split:
   "This makes sense - agreed on your split." The Solo deck stops being
   refilled behind its back; the starter's Fanfare card is never dead.
   Pneuma's "regains, not gains" wording can go back to plain "gains" only
   if Pneuma is a played-card effect; the builder checks and records it.
3. **Rule 4 is cut: the front no longer regains 1 each turn.** [USER]:
   "Agreed, remove the freebie. The Ancient relic can give it back, as
   planned." The Curtain Never Falls (her Ancient relic: "Your front performer
   regains 2") now gives the only regain. The fade (rule 12) stops being
   cancelled on the front, which a seat had called "only a number".
4. **Wriothesley: "Always your front performer."** [USER]: "Yes on
   Wriothesley - it's much cleaner." One sentence on his face replaces his
   five exceptions. Any summon or seat move works as normal around him, and
   he is never moved from the front. The Summon tip loses its Wriothesley
   caveat.

## 3. The old-kit cards (pool-completion pick 3, now decided)

The legacy cleanup moves every surviving old-kit row onto the prototype sheet
(cleanup pick 3). Under the Stage:

| Card | Was | Now |
|---|---|---|
| Singer of Many Waters (R, 1, Exhaust) | Heal 6 HP (breaks rule 11; Pneuma's healer in the lore) | "Your front performer gains 6 [9] Fanfare. Exhaust." |
| An Invitation (C) | adds a Companion card | replaced: **Opening Number** (Attack, 1, C): "Deal 9 [12] damage. If this is the first card you played this turn, your back performer gains 2 Fanfare." |
| The Guest List (U) | adds a Companion card and Energy | replaced: **Leading Lady** (Attack, 1, U): "Deal 6 [9] damage, plus 1 for each Fanfare on your front performer." |
| Command Performance (R) | adds 2 Companion cards | replaced: **Endless Waltz** (Attack, 2, R): "Deal 14 [18] damage to ALL enemies. Each performer with 5 or more Fanfare acts." |
| the rest (Commanding Gaze, Undercurrent, Stage Combat, Courtroom Drama, Crashing Waves, Duet, Quick Change, The Witness Stand) | | ported as they are |

The three replacements are Attacks, because over half her pool is Skills (37
Skills, 21 Attacks); a co-op friend found "no path to actually do decent
damage". Leading Lady is a second front reader, beside Pneuma Refrain.
Endless Waltz is named for her passive. The audit counted about 15
survivors, not 12; the builder lists the exact set it finds.

## 4. Main-session calls (balance, hygiene, text)

- **Quick Cue** (Common, 0): Spend 3 deals 11 [13] and applies Hydro (was 14
  [16]). At 0 cost it beat the starter's Curtain Rise (1 cost, 17 [21]) for
  the same Spend.
- **Tips:** the Bow tip and Grand Finale ("Bow without leaving") agree, the
  Bow tip covering "or, if a card says so, stays". Bring the House Down adds
  "If it empties, it Bows."
- **Overlong faces** (about 150 characters) trimmed: Grand Deluge, Bravura,
  Guest of Honor, Pneuma Refrain, Stage Whisper.
- **"Act" is the only verb** for what performers do; today's batch builds
  Star Turn as "it acts at once".
- **The brief is brought up to date** (§12's A Five-Century Act numbers, the
  power-sweep costs, §6's "performs at once").

Not changed, noted for a later pass: the Guest Cast is the largest deck;
Regal Bearing and Commanding Gaze are near-duplicates; Crabaletta and
Chevalmarin have swapped roles against the lore; Usher has no card.

## 5. What the build checks

Both engines; the seat page states the new rules. The sim reruns Furina's
decks after the build (Solo, Spend, Guest Cast within 10 points of the
default), read as a smoke test, not a gate, given the pilot's limits.
