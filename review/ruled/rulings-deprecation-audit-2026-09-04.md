Status: RULED R256 2026-09-04

# Rulings deprecation audit: what the overhauls left behind

Written 2026-09-04 on [USER]'s word at R255 ("the R188 ruling sounds like a
legacy artifact of the old build ... do an audit pass of what rules we can
deprecate"). Striking law is a C pick, so this packet changes nothing and
ends in four numbered picks.

## 1. What was read, and against what

Every ruling cited in `docs/current/LAW.md` (52 distinct), `EXPERIMENTS.md`
(40), `watch-register.md` (6), `kit-checklist.md` (2), the four identity
records under `docs/current/characters/`, `QUEUE.md` and the active
registrations, read against the rulings that replaced the shipped kits:

- **R213** (2026-08-26): the freeze and the quarantined prototype surface.
- **R219** (2026-08-29): Sparks become a price with no cap; Bake-Kurage
  becomes the Kokomi kit.
- **R220** (2026-08-29): the Salon becomes an orb board; the shared Burst
  meter retires roster-wide.
- **R228** (2026-08-30): one-mode priced Spotlight; Center Stage retires.
- **R240 / R241** (2026-09-02): Kokomi's chassis is the Plan. The Kokomi
  brief (`review/active/kokomi-brief-2026-09-01.md`) contains the word
  "Charge" zero times and "Muster" zero times.
- **R251** (2026-09-03): the shipped Burst retires under the Furina arm.

A ruling is sorted three ways. **Dead now:** it governs machinery no kit,
shipped or prototype, will carry forward, and it still has a live pointer
in HEAD. **Dies at the Balance landing:** it governs the shipped sheet,
which ships until the overhaul replaces it, so it is struck with that
sheet and not before. **Standing:** roster law that the overhauls do not
touch. Of 254 rulings, most rule one card or one sitting and never became
a rule; they leave with the sheet and need no act.

## 2. Dead now (six pointers, all Kokomi Charge or Burst)

1. **W9 and R188 / R163.** R163 asked for a Charge read budget, R188 ruled
   none, W9 watched the bank, R255 discharged the trigger. The Plan kit has
   no Charge bank to read. The watch entry and the `X9READ-S2` active
   registration in `EXPERIMENTS.md` (drafted 2026-08-31, unrun, never
   countersigned) point at a resource the overhaul deleted.
2. **W6, `gyorin_formation`:** pre-emptive Block scaled "+1 per 2 Charge"
   on a bank "never spent (R80)". Shipped-kit card, Charge-keyed trigger.
3. **W8, `send_the_runner`:** Burst-particle cadence against "the ratified
   meter-20 cadence (R139)". The meter R139 ratified was retired by R220.
4. **`EB183-MF`, Muster's Charge subsidy asked at the funnel** (R213 E1):
   drafted 2026-08-30, unrun, not countersigned. The Plan kit has neither
   Muster nor Charge, so R213 E1 has nothing left to ask.
5. **The Kokomi stability band (D5)** rides DARK on a declaration, `S4-G6`,
   that R250 closed as OVERTAKEN. Its grading protocol,
   `docs/current/playtest/kokomi-playtest-protocol.md`, is the shipped
   kit's twelve-card starter protocol.
6. **The Furina reframe staged-board slate** (countersigned R233, UNRUN):
   written when the reframe had simulator code only and "the C# arm does
   not exist". The arm has since been built and played by seats in six
   rounds, under the stage-gate rule that a Prototype arm gets no slate
   (`operations/stage-gate.md`). Nothing was run, so nothing published
   is struck; R101b is not touched.

R80 itself ("Charge is never spent") and R226's prospective amendment live
only in the Kokomi identity record, which is already marked "a record of
what LAW used to pin, not law". They need no act.

## 3. Dies at the Balance landing (no act now; a list for each landing)

These lines in `LAW.md` bind the shipped sheets, which still ship. Each
overhaul's Balance slate strikes its own:

- *Economy:* "Burst-meter (`burst_energy`) generation stays
  character-kit-scoped" (all three Bursts retire: Klee's is a Rare Power in
  the brief, Furina's under R251, Kokomi's under the Plan).
- *Combat:* "Reaction credit — damage attribution and Burst energy — goes
  to the triggering player" loses its Burst half.
- *Engineering:* the meter list "(bounded: salon_member 3, fanfare;
  unbounded: encore, charge, burst, exhaust_pile, spark)". The rule stays;
  the list is rewritten per landing.
- *Art:* "the centered-overhead creature-space slot is the cross-character
  Burst indicator", and the Funnel Contract's "Salon = 3 slot-index-keyed
  slots" and "Spotlight-is-a-designation-event" (an orb board since R220,
  one priced mode since R228).
- *Card-sheet rules:* "Muster's definition attaches from the card's OP"
  (R78); the Ancient carve-out's two examples, "Kokomi's no-passive-accrual
  Charge; Furina's no-per-turn-Encore trickle" (R127 keeps its shape).
- *Watch register:* W1, W2, W4 (Furina's shipped Guest Cast, Salon and
  Fanfare floor) and W7 (`what_the_tokoyo_took`, shipped Kokomi).
- The three identity records, by their own rule: each leaves HEAD when its
  brief is the identity. Klee's brief already is; the Kokomi brief is;
  the Furina brief is the reframe packet.

## 4. Two rules the prototypes already break

**R56, "No card starts the game with AoE; never in any starter."** Written
2026-07-26 for the shipped Kokomi's twelve-card starter. The Plan kit's
starter card Kurage's Oath (`docs/prototype-surface.yaml`,
`proto_kk_kurages_oath`, rarity basic) reads "Deal 3 damage to ALL enemies.
Plan: Deal 7 damage to ALL enemies." R241 approved the brief and R254 kept
the starter at two kit cards with this one in it. Two rulings on the row
now contradict a roster rule nobody re-read. Pick 2.

**R58, "lowering a threshold is forbidden"**, which R212 item 7 names as a
one-way door outside Claude's derived-number authority. Furina round 6
(`review/active/furina-reframe-round-6-2026-09-04.md` §4) moved Aria of
Recompense's Fanfare bar from 6 to 3 as a D default, on a quarantined
prototype row. On a strict reading of R58 that was [USER]'s pick, not
mine; it is disclosed here rather than left in the round packet's
defaults. The stage-gate page says measurement law does not bind at
Prototype and says nothing about LAW's card-sheet rules, which is the gap
pick 3 closes either way. Aria stays at 3 until pick 3 is ruled, since
[USER] plays the first build of the starter card either way (R254).

## 5. Standing, read and kept

R8 (healing law), R26/R77 (domination), R109 X2 (cycling engines), R144
(co-op as cards), R127's shape, R68 (stamps), R101b, R206/R207, R212 (the
ladder), R213 B / R215 (no prototype number is quotable), R217 (the
checklist), R221 to R223 (the local seat's funnel rules: dormant while the
Opus seats play by hand, not legacy, since the funnel and the seat exist).

## 6. Picks

**Pick 1 (C, measurement law and the watch register): strike the six dead
pointers of §2.**
1. Strike all six: W6, W8, W9 leave the watch register; `X9READ-S2`,
   `EB183-MF`, the D5 band and the reframe slate leave EXPERIMENTS' active
   list; the Kokomi playtest protocol leaves HEAD; R213 E1 closes as
   overtaken. **Default.**
2. Strike the five Kokomi pointers; keep the Furina reframe slate
   registered against a later Balance-stage run.
3. Strike nothing; they wait for each Balance landing with §3.

**Pick 2 (C, LAW): R56, the no-AoE-starter rule.**
1. Retire R56. A starter's shape is the brief's (R241 for Kokomi, R242 for
   Klee, R254 for Furina) and the kit checklist's. **Default.**
2. Keep R56 as roster law and re-author Kurage's Oath without ALL at base.

**Pick 3 (C, LAW): how far R58's threshold clause reaches.**
1. Balance sheets only. A bar on a prototype row is a number the seats
   test, taken as a D default and disclosed; the one-way door closes when
   the row is re-authored onto the shipped sheet. Aria stays at 3.
   **Default.**
2. Every row. Aria returns to 6, and the bar comes back as a pick in the
   Furina round-6 packet.

**Pick 4 (C, LAW): when §3 is struck.**
1. At each overhaul's Balance landing, as part of that landing's slate.
   **Default.**
2. Now, for the Burst lines only, since all three Bursts are retired on
   paper.

## 7. Ruled

R256, 2026-09-04: all four picks at their defaults. [USER]'s words are in the
ruling commit. Executed in the same commit: W6, W8, W9 struck; the four
active pointers and the Kokomi playtest protocol left HEAD; EB-183 retired;
R56 struck from LAW; R58 scoped to Balance sheets; the stage-gate page carries
§3 for each landing.
