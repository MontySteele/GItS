# Spiral Abyss round 3 (v2 numbers), 2026-10-18

The first round on Abyss v2: numbers fixed by the act an entry is taken in, Riptide and Elemental Mark limited to
once per turn, and Mage Shield 6 hits deep (`review/active/abyss-act-scaling-2026-10-18.md`). Asked by the user:
"Makes sense! ... let's do both."

The seats were blind Sonnet seats at A0 on build 0.2.5880. There were five solo seats, three of them on base
characters as controls, and one co-op pair. Raw transcripts are not kept. The seat records are in the session
scratchpad.

## Results

| Seat | End | Blessing / Shadow that applied, by act |
|---|---|---|
| Silent (control) | Lost to the act-1 boss (Lagavulin Matriarch), floor 17 | Overflow / Mage Shield |
| Ironclad (control) | Lost to the act-1 boss (Matriarch), floor 17 | Moonlit Rest / Riptide |
| Defect (control) | **Won**, floor 48, 10/95 HP | Spring / Mage Shield; Battle Rhythm / Withering; Resonance / Sheer Cold |
| Klee | Lost to the act-1 boss (Matriarch), floor 17 | Resonance / Elemental Mark |
| Furina | Lost to the act-3 boss (Queen), floor 48 | Abyssal Moon / Riptide; Spring / Mage Shield; Battle Rhythm / Thorny Ground |
| Co-op Varka + Yae | Lost to the act-3 boss (Test Subject), floor 45 | Battle Rhythm / Rally; Ley Line / Riptide; First Strike / Thorny Ground |

The co-op pair was taken over by fresh seats on floors 42 and 44. Varka's seat had tripped the three-refusal
stop after the partner ended a fight under its queued commands. Yae's seat ran out of wall clock.

The act-1 boss killed three of the six runs. In all three, the Matriarch's Soul Siphon drained the seat's Strength
and Dexterity to between -3 and -6. That is the base game. No Shadow fed her more than 3 Strength.

## What the v2 changes did

- **Riptide is tame.** The cap held: Terror Eel stopped at 3 Strength from Riptide. No enemy took more than 3
  from it in any run, against 14 on Insatiable in the 2026-10-14 round. It still shaped play: the Ironclad and Varka
  spent whole turns blocking fully to deny it.
- **Mage Shield costs one to three turns.** It cost about one turn on most elites, so the 6 against 2 narrowing
  worked:
  - the Defect cleared 5 hits with one Quadcast;
  - the Silent cleared 5 with Shivs on turn 1;
  - Furina, holding the counter element in act 2, stripped it with Hydro.

  The exception is the act-2 Decimillipede: three segments each wear a shield, which cost Furina about 3 turns.
- **Pricing by the act taken works in play.** The Defect took Sheer Cold in act 3 and lost 5 HP to it, the act-3
  number. The Shadows relic lists every Shadow still in force across acts.

## What did not

1. **Thorny Ground is now the most expensive Shadow.** It costs a seat that attacks a lot 30 to 60 HP in act 3:
   - Varka: 35 to 45;
   - Yae: about 30;
   - Furina: 50 to 60;
   - the Varka takeover seat: 40 to 50 over two fights.

   Every seat learned to Block first, so the Thorns hit Block. The act-3 number is 3 (`AbyssNumbers`).
2. **Moonlit Spring heals 70 to 80 HP an act.** The Defect healed about 70 in act 1 and Furina 70 to 80 in act 2.
   That is GPT's warning come true: 8 a fight erases the attrition of an ordinary fight. Moonlit Rest (4) gave
   the Ironclad about 40 over ten fights.
3. **Overflow and Wavering Moon are offered to characters without reactions.** The Silent took Overflow and it did
   nothing. `AbyssDraft.Offer` (`AbyssDraft.cs:67`) never reads the character. **Fixed** in #1425:
   both are offered only when someone in the run can trigger a reaction.
4. **Shadows that hit you show on the enemies.** Withering ("You start each combat with 1 Weak") and Sheer Cold
   sit on the enemy badges. The Defect could not tell who Withering targets. **Fixed** in #1425: they show
   on the player.
5. **A rest healed 35 when the page said 24 (Varka).** No mod effect heals at a rest site. The likeliest cause is
   a base rest-heal relic. Not a mod bug.

## Picks for the user

1. **Thorny Ground act 3:** **(a, default)** 3 → 2, the same as acts 1 and 2. (b) Keep 3.
2. **Moonlit Spring:** **(a, default)** 8 → 5, still more than Rest's 4 but not a full fight's healing.
   (b) Keep 8.

**Ruled 2026-10-18.** The user: "1) Let's leave it at 3 for act 3. 2) Agreed on (a), and Moonlit Rest might need
a look as well." So Thorny Ground keeps 3 in act 3, and Moonlit Spring goes to 5. Moonlit Rest goes back to the
user as a pick, below.

## Moonlit Rest (pick)

Rest heals 4 / 6 / 8 per combat for the rest of the run, by the act it is taken in. There are about 15 fights an
act. Spring at 5 then heals about 75 HP in its one act. Rest's totals:

| Taken in | Rest now | Rest at 2 / 3 / 5 |
|---|---|---|
| Act 1 | 4 × 45 ≈ 180 | 2 × 45 ≈ 90 |
| Act 2 | 6 × 30 ≈ 180 | 3 × 30 ≈ 90 |
| Act 3 | 8 × 15 ≈ 120 | 5 × 15 ≈ 75 |

Ironclad's Burning Blood heals 6 per combat, and it is the base game's only steady healing. Rest at 4 gives any
character two-thirds of it from act 1 on.

3. **Moonlit Rest:**
   - **(a, default)** 2 / 3 / 5. Its whole-run total comes to about Spring's one act. The difference is spread
     against burst.
   - (b) Keep 4 / 6 / 8.

**Ruled 2026-10-18: 3 (a).** The user: "Agreed on (a)!" Moonlit Rest becomes 2 / 3 / 5.
