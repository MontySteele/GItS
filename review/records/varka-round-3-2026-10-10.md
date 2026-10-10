# Varka round 3, 2026-10-10

This is the third Varka round tonight. It ran natural Knights on the same five seeds, with the Amber round's changes (#1025, #1026):
- Ashen Oath (2 Pyro Oath per Exhaust)
- Frost Ward's aura floor
- Oath Unto Death at cost 2
- the Wildfire line on the seat page
- Frozen's new text

**How it ran**
- Staging 0.2.4719+next. Per-act Sonnet seats, embark `20261010-0626xx`.
- The fact packet and records are in the session scratchpad (`varka-r3/`), gitignored.
- A Fable reviewer reviewed it. The main session accepted the review with one change: **Converging Winds is held, not re-aimed.** The reviewer proposed replacing the Rare's whole effect ("Your Swirls deal 4 additional damage to ALL enemies"). The house rule is that a Rare bends but keeps its core decision, so the replacement goes to [USER] after his run.

## Result

| Seed | Starting Knight | Round 3 | Amber (forced) | Payoff (natural) | Base character |
|---|---|---|---|---|---|
| 30KMHAVG9SMQ | Kaeya | floor 40, Slimed Berserker | floor 44 | floor 33 | floor 48 |
| CYHZM9S0VPW6 | Kaeya | **won** | floor 38 | won | floor 48 |
| DJCAV76ZKAUN | Barbara | floor 48, Test Subject phase 3 | floor 48 | won | floor 48 |
| YEWA0B7AVE45 | Amber | floor 40, Soul Nexus | floor 33 | floor 33 | floor 46 |
| R41TX5Q0ZQYN | Kaeya | **won** (5 HP) | won | won | floor 48 |

He won 2 of 5 this round and 6 of 15 tonight. On these seeds the base five won 0 of 5.

**Normal fights against base, by act:**

| Act | Damage a turn | HP lost | Block a turn (base) |
|---|---|---|---|
| 1 | 1.04 | 0.50 | 3.9 (2.2) |
| 2 | 1.02 | 0.70 | 6.4 (2.9) |
| 3 | 0.96 | 0.99 | 10.3 (7.5) |

Act-3 elites and bosses cost him more HP than base: 37.6% against 23.3%, and 68.6% against 30.2% (n = 4 and 3).

**The verdict:** above the base five for these seats on survivability, and at base on damage. He has two strong first acts and an ordinary third. The win counts (3, 1, 2) are inside five-seed noise.

**Settled:**
- The Oath, Four Winds and Knight core.
- Stoke the Flames.
- The Cryo line.
- Kindled Edge.
- Frozen's text: 0 misreads, the grading line met.
- Oath Unto Death at cost 2.
- Windborne Resolve as a Block engine through element switches. Two seats found it independently (31- and 37-Block turns). This bears on the Hydro pick.

**Sonnet draft taste is now stable over four rounds:**
- Seats draft their starting element.
- They skip Block (Hydro 7% to 9%).
- They skip Exhaust build-arounds (Ashen or Pyre Oath taken once in 34 offers).
- They rate slow Powers as dead.

Take-rate grading lines now measure that taste, not the cards, so they stop here.

## What changes (Claude ships)

1. **Sturm und Drang** (a Klee-pool companion, on `klee-next`). Its rider replaces the Attack's element with the Swirled element (`CompanionOverhaulHooks.cs:280-285`). For Varka, every Swirl arms a rider that cancels the next Swirl, and that killed one run. Fix: the rider deals its 6 [7] as a separate hit of the Swirled element after the Attack resolves. The text is unchanged.
2. **Stormward Stance:** "Your Anemo Attacks deal 3 [5] additional damage." Drop the 4-Oath gate. Every holder called it dead because of the gate.
3. **Sworn Brotherhood:** "At the start of your turn, gain 2 Oath of your current element." Upgrade: 3. One Oath a turn "never paid for the slot".
4. **Frost Ward:** "Gain 5 [6] Block. For each enemy with an aura, apply 1 Weak and gain 3 [4] more Block." The floor is now a Defend.
5. **Seat page:**
   - The "Knight" tag carries the Knight's element ("Knight, Electro").
   - The Oath note adds that a Swirl also gives 1 Oath of the element it Swirls.
   - The "would take N" preview folds a power's plain end-of-turn Block, or names the power.
   - While Fiddle is held, hand cards that draw are tagged "(no draw: Fiddle)".
   - Kaiser Crab's Surrounded: check in the decompile what turns you. If any card targeting an enemy turns you, the page says "Playing a card on an enemy turns you to face it."
6. **Held:**
   - Ashen Oath: accepted as niche, no third rework.
   - Wolfpack.
   - Storm Battery.
   - Dawn Wind's March: part of the Hydro question.
   - Rally to the Banner.
   - Converging Winds: see above.

**Seat error or by design:**
- Lisa switches to Electro because Knights switch.
- Windbound's Swirl gives 1 Oath of the element it Swirled.
- Soar does not touch a Power's damage.
- Withering Presence counts 0-cost cards (base game).

## For [USER]

1. **Converging Winds** ("The elements your Swirls spread set off Elemental Reactions") does nothing against a single enemy, so it is blank in every boss fight.
   - (a) Re-aim it: cost 1, "Your Swirls deal 4 [6] additional damage to ALL enemies."
   - (b) "Whenever you Swirl, gain 1 more Oath of the element Swirled."
   - (c) Keep it as a multi-enemy Rare.
   - **Default: (c) until your run.**
2. **Hydro's job** is already queued (#1017). Read it together with the Windborne Resolve finding above.

## Next

The five-seed Sonnet rounds stop here. Three rounds gave the same answer.

After this batch, Varka goes to [USER]'s own run. If the batch needs a check, run two seats on fresh seeds alongside his run, not ahead of it, and only to catch a reworked card that turns out to be a trap.
