# Story text audit: the four character chains (2026-10-23)

The writing review's story pass, first part. It covers the 32 character
story events (Klee, Kokomi, Furina, Varka: eight each, about 6,200 words,
`klee-mod/localization/reference/eng.json`, `events` table), then the rest of the story text: the Ancients' lines, the
run lines, the Spiral Abyss and the nation events (last section). Yae has no
chain yet (see pick 3).

**The verdict: the prose is good and stays.** Every chain has a voice of its
own, and the callbacks work: Klee's Mom's notes answer what she did with the
chest, and Kokomi's Endgame remembers how she played the Other Commander.
Furina's Understudy sends a note to Curtain Call. Nothing reads as
an essay, and no line needs the game to explain it. What follows is
small: option lines that word the same reward two ways, and a few repeats you
would notice inside one run.

Prose rules, so the pass has a line to hold: **story prose keeps
contractions, parentheses and the characters' own punctuation** (Mom's
"(It always is.)" stays). The card-face rules apply only to the option's
reward line, the mechanical text under each choice.

## Fixes taken at their default (text only, no reward changes)

1. **Two option lines are missing "to add to your deck".** Every other
   "Choose 1 of 3" line has it.
   - Kokomi, The Other Commander, *Concede*: "Add Doubt. Choose 1 of 3 random
     Rare cards." → "...Rare cards to add to your deck."
   - Furina, A Steambird Clipping, *Cast the sequel*: "Choose 1 of 3 random
     Guest Stars." → "...Guest Stars to add to your deck."
2. **"Remove every Overdue Reports"** (Varka, The Second Satchel, *Sign
   them by lamplight*) reads wrong because the card's name is plural. →
   "Remove all [Overdue Reports]."
3. **Title case:** "A Room with No One In It" → "A Room with No One in It".

## Picks

1. **One wording for adding a named card.** Fourteen option lines say "Add
   [Doubt]." (or "Add an upgraded [Four Winds' Ascension].") and two say
   "Add [Confinement] to your deck." Klee uses both.
   (a) "Add [X] to your deck." everywhere, the same frame as "Choose 1 of 3
   ... to add to your deck", so a new player sees where the card goes.
   (b) "Add [X]." everywhere, shorter.
   **Default (a).**

2. **"Reads it twice" turns up five times across the four chains.** Some of
   those you would see twice in one run: Klee can draw both A Letter from
   Jean ("reads it twice, then a third time") and Mom's Last Note ("Klee
   reads it twice"), and Furina both A Steambird Clipping and A Letter from
   the Court. (a) Keep it where the option itself says so (Klee's *Read it
   twice*, Furina's *Read it aloud, twice*) and vary the other three:
   - Klee, Mom's Last Note, *Read it out loud to Dodoco*: "...and I'll see you
     in Mondstadt. Love, Mom." → keep the line, then "Dodoco listens to the
     whole thing again."
   - Furina, A Letter from the Court, *Keep it*: "She reads it twice more on
     the way up." → "She reads it again on every landing."
   - Kokomi, A Report from Gorou, rested opening: "Rested, she reads it
     twice." → "Rested, she reads it properly this time."

   (b) Leave all five as they are.
   **Default (a).**

3. **Yae's story writing.** Yae is in Prototype and has no story events,
   no run lines (boss entry, low HP, run won or lost) and no lines for the
   Ancients (Neow, Pael and the rest), so the game falls back to its own.
   (a) Write all of it when she reaches Balance, the way her translation
   waits for it, so it is not written twice if her kit moves. (b) Write it
   now.
   **Default (a).**

4. **Yae's character-select text** is the only one that explains mechanics.
   The other four give a title line, then two sentences of who they are and
   why they climb: "The Pearl of Wisdom. / Watatsumi's priestess and
   strategist..." Yae's reads: "Guuji of the Grand Narukami Shrine and
   editor-in-chief of the Yae Publishing House. Her Sakura strike at the end
   of every turn, and her edits make good cards better."
   (a) Match the others: "The Guuji of the Grand Narukami Shrine. / She runs
   the shrine, a publishing house and most of Inazuma's gossip. A tower full
   of strangers sounded like an excellent story." (b) Keep it.
   **Default (a).**

## What the rest of the story text turned out to be

- **The 123 nation events (23,500 words) are not in the release build.**
  They belong to the Teyvat run frame, which is switched off
  (`TeyvatFrame.Enabled`, `docs/current/operations/teyvat-frame.md`). With it
  off, not one of their rows is merged, and the same goes for the
  nation-named Ancients (Alice, Apep, Dvalin and the rest). Their reward lines
  are rough: some still name the base event they copy, as in "Obtain Bulging
  Cap (Big Mushroom, relic)", and one prints a pipeline note to the player.
  They need a full pass before the frame is ever switched on, not before
  launch. The English reference lists them because its test turns the frame
  on, so **the translation leaves them out.** That takes more than a third of the
  words off the job.
- **The Spiral Abyss (18,000 words) is about 50 distinct sentences.** Each
  Blessing is listed once for every Shadow and act it can pair with. The
  shared text audit already went over those sentences. One small fix taken
  here: Elemental Mark says "an enemy attack" where Blood in the Water says
  "an enemy's attack". Both now say "an enemy's attack".
- **The Ancients' lines and the run lines for the four Balance kits** (Neow,
  Pael, Tanx, Orobas, Vakuu, Darv, Nonupeipe, Tezcatara; boss entry, low HP,
  the pair exchanges, run won or lost) read in character and need nothing.
