# Co-op paired round: Klee + Varka against Ironclad + Silent, 2026-10-08/09

**What ran.** This is the stage gate's co-op check
(`docs/current/operations/stage-gate.md`): the reaction pair plays three
shared seeds against a base pair, Ironclad and Silent.
- Ascension 0, `embark --coop` over `--fastmp`.
- One Sonnet seat (medium effort) per player.
- Builds: 0.2.4590+next for seeds 1–2, and 0.2.4626+next for seed 3, which
  carries the Varka payoff fix (#983).
- Seed 3 was stopped once for [USER]'s own play, then rerun from the start
  with both pairs at once, on ports 33772 and 33774 (#985).
- Raw seat records are in the session scratchpad and are gitignored. A co-op
  run is not a run of record.

| Seed | Klee + Varka | Ironclad + Silent |
|---|---|---|
| 0558NNX1JRCB | Lost at the act-2 boss, Knowledge Demon, floor 31. 14 fights won | Lost in an act-2 fight on floor 23 (Bowlbugs and a Slumbering Beetle). 13 fights won |
| CYHZM9S0VPW6 | Lost at the act-3 boss, the Queen and Torch Head Amalgam, floor 45. 22 fights won | Lost to the Decimillipede elite, floor 23. 10 fights won |
| DJCAV76ZKAUN | Lost at the Queen, floor 45. Klee fell on turn 7 and Varka on turn 9. About 21 fights won | Lost at the Queen, floor 45. 21 fights won |

**Verdict: the co-op check passes.**
- Klee and Varka went at least as far as the base pair on every seed, and
  further on two.
- Neither pair won. The Queen beat all three pairs that reached her. Her
  Frail, Weak and Vulnerable 99, together with Chains of Binding, left no
  survivable turn.
- The reaction pair is stronger in co-op, but not runaway. The standard asks
  only that co-op not be "exponentially easier" than solo, and this round
  shows a modest gap, not a collapse. Solo judging stays with the solo suites.

## What played well

- **Partner reactions were real, and both seats could read them.**
  - Varka: "Klee's auras, Shrapnel (+50%) and Pass the Match let me do far
    more per turn than my own kit would have."
  - Klee: a BoomBoom Strike into Varka's Electro aura was an Overloaded kill.
- **Two-seat kill turns.** Klee's Stoke the Fuse and Pass the Match+ on
  Varka's attack set off a 63-damage Bomb. Boom Badge stacked on Bombs took
  the Owl Magistrate down by 177 with one Sizzle.
- **Varka's Four Winds' Ascension at high Oath** hit for 48, 72 and 227 in
  single cards. With the payoff fix, Lisa set up Electro and the Swirl chain
  followed. One seat called the Pulsating Witch play into Klee's Pyro "the
  single best turn of the run".
- **The base pair played as base cards do.** The Silent's Poison carried
  most fights. Concoct timed before the Ironclad's multi-hit turn was the
  standout play. Exact Block to stun the Bowlbug (Rock) was a decision the
  seats enjoyed.
- **Parallel pairs work.** Two co-op runs went at once on one machine with no
  crosstalk.

## What did not

- **Klee and Varka have little Block between them.** "No real Block in hand
  turns 4-6 cost 40 HP." Klee fell to single-digit HP in act 2 on all three
  seeds. That matches the "fast and fragile" ruling for Klee. In co-op the
  partner covers by finishing fights.
- **Pass the Match is dead once the partner has ended their turn.** Three
  seats, on two seeds, called it their nothing turn. The partner's
  turn-ended state shows on the page, but the card does not say it needs the
  partner still acting.
- **Weak cards named more than once:**
  - Little Hexenzirkel: "a Power that does nothing until a Companion card
    follows".
  - Pocket Match.
  - Toric Toughness: "two energy for a few Block".
  - Whisper of Water, which eats Klee's aura for no damage.
  - Empty Cage, and Pandora's Box removing Defends. The latter applies to
    both pairs.

## Defects (BACKLOG)

Each counts the seats that reported it, across all three seeds. Lines go in
`docs/current/BACKLOG.md`. Where a line already exists, it is widened rather
than repeated.
1. **Mend at rest sites (about 10 seats).** Mend does not use up the rest
   action, so Smith or Rest is still accepted after it. Sometimes the heal
   does not show. This is an existing line, now widened.
2. **Treasure chest (7 seats).** The page says "Took X" while the relic list
   shows a different relic. When both players pick at once, one pick loses,
   and the page reports it as taken. This widens the existing "contested
   chest pick" line.
3. **Partner cards in "What you played this turn" (9 or more seats).** This is
   already in BACKLOG.
4. **Reattach.** The page note says the segment returns at 25 HP, but the game
   returns it at about 60 (3 seats). This joins the existing Decimillipede
   line.
5. **Revival.** A downed player comes back after the fight at 1 or 13 HP, and
   the page never warns of it (4 seats).
6. **Klee's glossary reads the checkout, not the installed build.** "Bomb
   grows 4" was shown where the `+next` build grows by 2 (8 seats on Klee +
   Varka). The page itself warns of this.
7. **`proceed` refuses until the partner acts.** It answers "No proceed
   button" at rest sites, chests and rewards, then works on a retry (4 seats).
8. **A fight that ends partway through a batch of commands** produced a run of
   REFUSED lines past three, and the stall stop did not fire (1 seat).

These also showed up once each, with no cause found yet: a Power Potion lost
at a full hand, the Blade of Ink+ preview printing 13 on every Shiv, Block
not reconciling with Barricade, an elite reward with no relic, and
Acrobatics+ missing from the deck list. Most are probably base-game
behaviour, so they stay here and do not go to BACKLOG.

## What to change

1. **Fix the four co-op page defects:** Mend, the chest report, revival, and
   `proceed`. They cost every seat time.
2. **Pass the Match:** add a line to its tip saying the partner must still be
   acting. Text only, on `klee-next`.
3. **No kit change from this round.** The co-op standard is met. Klee's Block
   is ruled as intended, and Varka's payoffs are graded by their own round
   (`review/active/varka-payoff-fix-2026-10-08.md`).

**Process.** Four first seats on seed 3 stopped near the 90-minute wall
clock, mostly waiting on their partners. Continuation seats then took over
from the notes. Next time, give co-op seats a longer wall clock, since `wait`
time counts against it. Every seat reports "Repo files read: none". Most
declared a `grep` on their own observe output.
