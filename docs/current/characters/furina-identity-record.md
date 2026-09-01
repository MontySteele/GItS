# Furina — identity record

**A record of what LAW used to pin, not law.** These lines were `LAW.md`
§*Character identity — Furina* (lines 182 to 223) until 2026-09-01, when the
machinery review's change 6 moved character identity out of LAW. They are moved
verbatim. They are revised by a sentence in Furina's brief when that brief is
written, not by a LAW amendment; until then this file is where they are read.

---

- **Hydro, skill-grade support-protagonist:** modest numbers, scaling routes
  through others (elite A4 sustain + A6 utility; weak A1 + A7). (furina §1, §2)
- **Spotlight runs in exactly two modes** (the retired self-Spotlight model is
  not law): **CENTER STAGE** designates Furina — her cards generate Fanfare, no
  numeric bonus; **GUEST CAST** designates the Companion *category* — companion
  cards get the +50% multiplier and Spotlight texture, generate no Fanfare. The
  `character:` field, invalid-target rule, freely-movable persisting designation,
  inert duplicate selectors, per-player registry, and the per-turn Spotlighted-card
  cap stay live. (R41; principles §4.5 v1.14; furina §3)
- **Encore is an unbounded per-combat buffer** absorbing after Block and before
  HP (overdraw drains true HP); **Encore absorption credits A4, never A3.**
  (principles v1.10; furina §2, §4)
- **Fanfare is capped at %maxHP; generation is activity-based, never passive**
  *(Encore's per-turn-trickle ban carries the same Ancient carve-out: R127)*.
  Design invariant: **every point of damage past Block prints exactly 1 Fanfare.**
  Live legs: HP lost / Encore spent / Encore absorbed / Spotlighted card played.
  Cards use printed `Fanfare Cap +X` (raises cap) and `Fanfare +X` (full grant,
  rare POWER payoff only); cards raise a permanent floor (`gain_fanfare_floor`),
  not the cap. **`Fanfare Cap +X` is an AVAILABLE EXPLICIT VERB, not a rider
  every Power carries** — a card prints it when raising the ceiling is that
  card's job. The incidental carriers were removed along with the register
  lint that required one on every Power (`EB-118` §5.2, 2026-08-24; lint `R7`
  retired, `R6` untouched — the full grant is still a rare-POWER payoff).
  Fanfare is a global pool on Furina surviving Spotlight moves.
  (principles v1.12 RATIFIED; furina §4; R41; R114 FLAG-3; EB-118 §5.2)
- **Delete-test applies unmodified, no detector carve-outs:** deleting Furina's
  cards from a winning Spotlight deck must gut it; companions winning anyway is
  `SUPPORT_CARRY`. **Self-carry must not be the median-best plan** (Salon and
  Spotlight beat self-carry at median draft quality; self-carry owns the ceiling
  only on cracked-Rare draws). The Ethereal Spotlight selector is kit machinery
  and does not count toward A5. (furina §8, §2; R61)
- **Guest Star generators — four guardrails:** this-combat-only; generators
  Exhaust; equal-rarity (sub-Rare cannot create 5-star Rares); pull only from the
  shared companion pool + purpose-built Guest Star sets, never playable pools.
  Guest cameos are Furina-personal-pool only. (furina §9; principles §4.5; D2)
- **Fontaine Cryo-convergence is managed in kit, not roster exclusion:**
  Charlotte and Freminet each get one Cryo-applying card; Chevreuse is the
  authored Overload/Vaporize counterweight (buff other routes, never nerf
  freeze); Fontaine's zero 4-star Electro is scarce by construction, not a bug.
  Freminet is one applier + one defensive/trigger + one enabler — no fake-support
  reflavor of a DPS kit. (furina §10)

---

**Live tension to carry into the brief.** `review/active/furina-reframe-2026-08-29.md`
(countersigned R220 A) and R228 already supersede parts of the Spotlight and
Fanfare bullets above on paper: Center Stage retires, one mode priced, Fanfare
becomes the Salon's Focus and Burst. Nothing above was rewritten to match,
because this file is a record of the LAW text as it stood. Which of these lines
survives is the brief's question, and the brief has not been written.

**Consumers that cited the LAW line number.** `LAW.md:189`'s headline "Fanfare
is capped at %maxHP" is cited from `tools/lint_constant_parity.py`,
`tier0/engine/combat.py`, `tier0/engine/state.py` and `tier0/tests/test_furina.py`.
Those citations now point here.
