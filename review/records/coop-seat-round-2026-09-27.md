# First two-seat co-op round, 2026-09-27

Two blind Opus seats played one co-op run on build 0.2.3883: Klee as host on
lane 2, Furina on lane 3, at A0. They used `embark --coop` (#705, #712), the
game's own `--fastmp` localhost transport, on one machine and one Steam
account.

The round was cut at act 2, floor 29, after an elite win, to save budget
([USER], 2026-09-27: "Let's be sparing about them for now"). The raw records
are gitignored in `review/qa/seats-2026-09-27/coop-lane2.md` and
`coop-lane3.md`.

**The runtime works.** Across both seats' 16 fights there were:
- two-player embark, votes, simultaneous turns and `wait`;
- an act 1 boss win (Waterfall Giant);
- three elites.

No crossed lanes and no stalls that stopped the run.

## What played well

- **Reactions across players are the best co-op turns, in both directions.**
  - Furina's Hydro set up Klee's cooked Bombs, and the Bomb badge printed the
    Vaporized total ("43 with Vaporize"). A Seapunk Bomb went from 12 to 18,
    and the boss took 41 and 72 from Perfect Timing.
  - Furina's Hydro also reacted off Klee's Pyro: Tidal Flourish Vaporized on
    four Gardeners.
  - Their hits combined on Block: Furina's Hydro sized Klee's Bomb to strip a
    Tunneler's 64 Block exactly, and the pop Stunned it.

  This was read from the code in `review/active/coop-concepts-2026-09-27.md`,
  and it is now seen in play.
- **Shared tools** felt like helping each other: The Ball (10 → 45, passed back
  and forth), and Rally.

## What did not

- **Furina cannot protect Klee without her co-op cards.** Her Stage absorbs hits
  on Furina only. Klee took every attack-everyone hit, down to 28/66, while
  Furina sat at 74 to 78. Neither ally shield (Guest of Honor, Share the
  Spotlight) was offered in 16 fights, since co-op cards are a small slice of a
  78-card pool.
- **Hydro-only cards spend Klee's Pyro for nothing.** Chevalmarin+ and Tidal
  Flourish's Hydro-only mode react with Klee's fresh Pyro aura and deal no
  damage, so the Vaporize is wasted. Furina's seat learned to time them onto
  bare enemies.
- **Barbara (Front Row Seat) is redundant beside Furina.** Klee's Hydro
  companion duplicates her partner. The Klee seat called it NEVER AGAIN.
- **Turns are simultaneous, so a seat commits before seeing its partner's
  play.** Klee twice ended her turn just before Furina's Hydro landed. Human
  players talk; seats cannot. This is a seat limit, not a design fault.

## What to change

- **Design (no pick yet):**
  - The four new co-op cards (#713, installed in 0.2.3903) add a damage buff
    and The Crowd Roars, which feeds on the partner's HP loss. None adds a
    shield.
  - If later co-op play keeps showing Klee exposed, the fix belongs in
    Furina's co-op set, not in her Stage rules.
  - The Hydro-for-nothing interaction is worth a line in the Furina balance
    pass.
- **Page fixes (hygiene, to batch):**
  - the "What you played this turn" log lists the partner's cards as your own;
  - players are named "Test Host" and "Test Client 1";
  - the reaction glossary says no reaction is reachable although the partner
    applies the second element;
  - "Put Bomb 1" is logged while the badge shows 8;
  - the Weak gloss wrongly says it reduces a Bomb's damage;
  - a contested chest pick is not announced;
  - `wait` after a finished fight reports nothing while the reward screen is
    up;
  - a play aimed at an enemy the partner just killed is retargeted silently;
  - Mend at a rest site did not end the rest action.
- **Tooling:** the dev card grant is refused in co-op, by design: it would
  desync the peers. A synced grant would let a round be set up to test named
  co-op cards.
