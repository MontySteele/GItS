Status: RULED R237 2026-09-02

# Klee overhaul, rounds one and two: what the seats found

Ruled R237 by [USER]'s own act-one run of 2026-09-02: the four answers are in that commit's message; pick 2 took option 1, the rules stand and the starter changes (draft 3 in the slice document, round three).

Written 2026-09-01, the night the prototype first ran, and extended the
same night with round two on the fix build. This is the Prototype stage, so
nothing here is a measurement (R217 G): the seats' words are feedback for
iteration, the defect rows are the deliverable, and your act-one run is the
gate (`review/active/klee-overhaul-slice-1-2026-09-01.md` §6).

## 1. What ran

- Build `0.2.1879+proto.dirty`, the Klee overhaul arm on (PR #247, merged as
  plumbing), deployed with the full validation gate green; the three-fight
  soak read `fights=3 defects=0`.
- Two seats played act-one runs blind, seeing printed faces only. The Codex
  seat (gpt-5.6-sol, seed `UFVNPES9TRM4`, 100 actions, five fights, stopped
  at its action budget) and an Opus seat (the author's own model family, so
  not an independent read; seed `0Y3S8YZLLQD2`, 106 actions, five fights,
  stopped at its budget with the run alive at 51/62 HP). Records:
  `review/qa/blindplay/klee-overhaul-r1-codex-b/record.md` with the per-turn
  wire in `wire.json` beside it, and
  `review/qa/blindplay/klee-overhaul-r1-opus/record.md`.
- Thirteen fights closed across the soak and both runs: no crash, no
  soft-lock, no stalled screen. The Qwen seat is staged turns only under the
  standing condition (R224, `M64`), and nothing was staged tonight, so it did
  not play.

**Round two, same night.** The arm fixes (EB-260, 261, 265, 266), the
render fixes and the Mondstadt companion prototype were merged onto the round
branch and deployed as `0.2.1911+proto.dirty` with both arms on; the soak
read `fights=3 defects=0` on its second run (the first ended with the bot
dead on floor three after two clean fights, a bot outcome, not a defect).
Codex played again (seed `JHZ4W7H7M9KM`, 80 actions, three fights, zero
command errors against round one's two; record in
`review/qa/blindplay/klee-overhaul-r2-codex/`) and so did the Opus seat (94
actions, four fights won including the Living Fog elite, alive at 3/62 at
the budget; `klee-overhaul-r2-opus/`, seed not read back at embark, the
EB-191 race). Both drafted Mondstadt prototype companions from the reward
slot and the shop, and the shop, the chest and the Mine clause on the Bomb
face all read correctly live.

## 2. What the testers said

Subjective, and the four gate questions are yours to answer, not theirs.

1. **The bet.** Codex found it and played it once: "whether to detonate
   immediately for damage and Spark or let Bombs grow while risking enemy
   attacks", and it held a Bomb through a Wurm's buff turn to cash a bigger
   one. Opus found the same tension "printed on the cards but not present in
   the fights": nothing lived long enough for holding to beat detonating, so
   "the answer was always detonate". Read together: holding pays only on a
   turn the enemy is not attacking, and act-one hallway fights end in two or
   three turns. Question 1 is about this.
2. **Sparks.** Codex felt a second tension, a free Ka-pow! now or the Spark
   held for Powder Charge, Fwoosh!, Quick Fuse or Dig In next turn, and said
   Spark "already had too many competing uses". Opus saw Ka-pow! "repeatedly
   free because detonations refund Sparks" and folded it into a script. That
   is question 2 exactly, and the two reads disagree.
3. **Repetition.** Both said play settled into one script by the third
   fight: place every Bomb, Kaboom!, Ka-pow! with the refunded Spark, Duck
   and Cover with what is left. Opus: "I was not choosing, I was checking
   whether the pieces were in hand."
4. **Dead cards.** Both called the four Duck and Cover copies dead or an
   energy sink, and Opus called Run Away! (0 cost, 3 Block, 7 if a Bomb went
   off) strictly better. Codex's other dead card was Quick Fuse with nothing
   to set off; Opus's were Jumpy Dumpty ("never once had the 2 energy") and
   Sparks 'n' Splash. Codex called Jumpy Dumpty "the early engine". Question
   4 material, and the two disagree on Jumpy Dumpty.
5. **Reactions.** Opus: everything Klee owns is Pyro, so a reaction happens
   only with an off-element companion, and "the moment I did the damage
   roughly doubled"; one Kujou Sara card was "the sole point of failure for
   the best thing the character does". That is slice one by design (§7 left
   Personals and stand-ins out), and the Mondstadt companions now being
   built carry the targeted appliers. Know it before reading your own run:
   the React loop is not reachable from her own pool in this build.
6. **Squishiness.** Codex fell to 14 HP against Fogmog and went "strict
   survival" with Dig In and Duck and Cover; Opus never dropped below 37/62
   and deleted 44 HP in one turn on three energy. Bot-limited, not evidence,
   but question 3 will be about this.
7. **Round two, on the fix build.** The bet got played this time. Codex
   blocked instead of detonating in fight 3, watched the stack grow "from 13
   to 17", and cashed 23 with one Kaboom!; it named the tension as "whether
   to detonate immediately or block and let Bombs grow", with the added cost
   that waiting risks drawing no set-off card. Opus banked a Bomb on an
   enemy's Empower or Stunned turn and cashed 22 with one card, "the best
   moment in the run". Both again said play flattened into a fixed rotation
   by the third fight. Two card-level reads for question 4: Quick Fuse never
   fired in four fights (its two gates, a Spark in hand and a live Bomb, are
   nearly exclusive, since the ordinary way to get the Spark is to set off
   the Bomb it wants), and Sparks 'n' Splash "reads as an engine and is a
   tax", because its forced end-of-turn set-off deletes the growth that makes
   holding interesting. One read for question 3: the Living Fog's Smoggy,
   which stops a second Skill, is a precise counter to a deck whose every
   Block card is a Skill, and turned a survivable elite into a 3 HP finish.

## 3. Defects, filed

Twelve rows, EB-259 to EB-271 in `docs/current/BACKLOG.md`. Round one's
nine first. Two are lies on
the arm's own faces and matter for your run: the Bomb badge says "never goes
off by itself" while a Mine goes off when its enemy attacks (EB-260), and
the badge's damage total leaves Strength out, so it printed 10 and dealt 14
(EB-265). Two more on the arm: Quick Fuse is playable as a no-op that eats a
Spark (EB-261), and a reaction feeds the shipped Burst meter, which nothing
in the arm reads (EB-266). Five are in the blind render, not the game: bare
`proceed` on events and `confirm` when unavailable (EB-259), shop items
print unnamed and cannot be bought (EB-262), a chest prints no relic
(EB-263), raw enums and icon tokens reach the page (EB-264), and the
printed-cost map keys by title and misreads a prototype row that shares a
shipped name (EB-267). Known and unchanged: enchantments missing from the
battle hand (EB-181); the "(proto)" in Sparks 'n' Splash's name is the
surface's collision suffix and goes away at Balance.

All nine were built the same night (PRs #249 and #251, merged onto the round
branch as plumbing) and are in the installed build; the live reads in round
two confirmed the Mine clause, the shop, the chest, the Spark gate's "you
have no Spark" and Quick Fuse's "no enemy is holding a Bomb". Round two
added three: the Dexterity Potion cannot be used through the render while
the Energy Potion can (EB-269); the Bomb badge now prints two numbers that
disagree under Weak, the stack's 17 in bold and the face's 12 after the
modifier, a consequence of the EB-265 fix (EB-270); and a numbered card name
goes stale mid-turn plus one arm gate still refuses without a sentence
(EB-271). None blocks your run; EB-270 is the one to read around, since the
face's number is the true one.

## 4. What is installed right now

The dev build with both arms on (Klee overhaul, Mondstadt companions), not
the release build, on purpose, so your run needs no deploy.
`mods\klee\manifest.json` says `0.2.1911+proto.dirty`. To put the release
build back at any time: `klee-mod\build\deploy.ps1`. Do not hand this build
to a co-op partner.

## 5. Picks

1. **Which build you play.** APPLIED and done: the fix build is the
   installed one (`0.2.1911+proto.dirty`), so the two lying faces your four
   questions depend on are corrected before you play. Nothing to pick.
2. **Rule 2, Bombs grow at the start of your turn.** The seats say holding
   never paid in act-one hallway fights. (1) *Leave the rule; your run and
   question 1 decide, as the gate says* [default]. (2) Send rule 2 back to
   the brief now, before your run.

Then: one act-one run, three or four fights including an elite, and the four
answers from §6 of the slice document, a sentence each.
