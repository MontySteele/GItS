Status: OPEN (picks 1 to 2)

# Klee overhaul, round one: what the seats found

Written 2026-09-01, the night the prototype first ran. This is the Prototype
stage, so nothing here is a measurement (R217 G): the seats' words are
feedback for iteration, the defect rows are the deliverable, and your act-one
run is the gate (`review/active/klee-overhaul-slice-1-2026-09-01.md` §6).

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

## 3. Defects, filed

Nine rows, EB-259 to EB-267 in `docs/current/BACKLOG.md`. Two are lies on
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

Two Opus agents are fixing them now, one per group. Each lands as a plumbing
PR, then the dev build redeploys with the fixes and, once its own PR is
green, the Mondstadt companion prototype.

## 4. What is installed right now

The dev build with the overhaul arm, not the release build, on purpose, so
your run needs no deploy. `mods\klee\manifest.json` says
`0.2.1879+proto.dirty`. To put the release build back at any time:
`klee-mod\build\deploy.ps1`. Do not hand this build to a co-op partner.

## 5. Picks

1. **Which build you play.** (1) *The fix build (EB-260, 261, 265, 266 and
   the render fixes), which redeploys as soon as its PR is green* [default,
   APPLIED as a process call: the two lying faces are the very numbers your
   four questions ask about]. (2) The installed build now, reading those
   two numbers with the correction in mind.
2. **Rule 2, Bombs grow at the start of your turn.** The seats say holding
   never paid in act-one hallway fights. (1) *Leave the rule; your run and
   question 1 decide, as the gate says* [default]. (2) Send rule 2 back to
   the brief now, before your run.

Then: one act-one run, three or four fights including an elite, and the four
answers from §6 of the slice document, a sentence each.
