# Furina Spend round, 2026-10-10

This round grades the Spend paper (`review/active/furina-spend-paper-2026-10-10.md`, PR #1014). The build (#1016) is at the paper's defaults:
- "Spend up to X" on Tidal Flourish, Spirited Aria, Crashing Waves and Hold the Stage;
- Navia's act Spends half the bank;
- Freminet's act Spends a quarter (ruled 2026-10-10).

**How it ran**
- Staging 0.2.4700+next, branch `spend-next`. Per-act Sonnet seats, embark `20261010-0249xx`.
- The same four Furina seeds as before, plus the Ironclad control.
- The fact packet and seat records are in the session scratchpad (`furina-spend-r1/`), which is gitignored.
- The review below is by a Fable reviewer after one exchange with the main session on the High Stakes sizing.

## Result

| Seed | This round | Block round | Quarter line |
|---|---|---|---|
| JF391WG2NN0X | floor 48, Test Subject (112/300, form 3) | won | floor 48 |
| WDETA8RRGH98 | floor 17, Vantom at 1 HP | floor 33 | floor 25 |
| 0J427L1YQV15 | floor 33, Kaiser Crab | won | floor 33 |
| TYXJLVY31QN7 | floor 24, Infested Prism (at 7 HP) | floor 17 | won |
| Ironclad control PPW4N6WX70LS | floor 17, Kin Priest | floor 48 | floor 48 |

- Furina won 0 of 4. The Block round won 2 of 4.
- The control fell from floor 48, three rounds running, to floor 17 on the same seed and character. One seat on one seed swings about two acts, so four runs say nothing about strength.
- Per fight (n = 54), damage a turn on normals is 0.99 / 0.92 / 0.86 of base. Act-1 elites: 36.8 against base 25.7.
- The up-to cards pay their way. Per play: Spirited Aria 17.1, Tidal Flourish+ 12.6 to ALL, Crashing Waves+ 24.0. Strike is 5.2 and Bravura 22 to 33.

**The deaths name their own causes:**
- Lane 3: a Kaiser Crab facing error, plus Draining past the line.
- Lane 4: Tainted turned every Skill off.
- Lane 1: entered the 300-HP form at 30 HP.
- Lane 2 is the one the change touches. Tidal Flourish+ auto-spent 10 Fanfare for 1 damage under Slippery, and Vantom ended at 1 HP.

**Overflow is fixed where an up-to card was drafted.**
- Unspent at fight end: median 13, max 35 (n = 7 seat quotes). The census had 12 to 45 commonly, with extremes of 57, 59 and 81.
- The 35s all came from a deck with no up-to card.
- Spend events roughly doubled. Cash-outs held: median 23, max 73, against 24 and 76.

**HP lost on normals (1.5 to 1.9 times base) is mostly measurement.**
- Telemetry stamps HP before the curtain call returns drained HP (`PlayTelemetry.cs:1005`). Lane 4's act-1 normals: telemetry 23 lost, records 4.
- On elites and bosses the two agree, and there the seats name the cause: they take hits on purpose for Fanfare, and Drain past the line at low HP.

## What changes (Claude ships)

1. **Auto-max stays.** The base game's X-cost cards spend all Energy with no chooser, and ordering is the player's control. If [USER] wants a choice back, the shape is opt in or out, not an amount.
2. **Hold the Stage, Navia, Freminet:** no change. Freminet's Block engine is his line stacking with The Masquerade (every Drain pays Block twice), not the quarter act. If she overshoots later, the dial is The Masquerade.
3. **High Stakes is reworked.** The old card was NEVER AGAIN three times over two rounds; the line band punished the play the kit teaches.
   - New text: "Your Attacks deal 1 additional damage for every 5 HP you have Drained and not Repaid." Upgrade: every 4.
   - It reads the net Drained counter already on screen, and adds per hit like Strength.
   - Sized against Inflame and Rupture: about +2 in a normal fight, +6 late in a boss.
4. **A Five-Century Act becomes visible.** With the power up:
   - the face tag reads "(Past your Drain line: returns after combat)";
   - the counter drops "lost unless you Repay";
   - the curtain-call line names the past-line part.

**Defects to fix:**
- Hold the Stage and The Show Must Go On preview Block without Frail (18 shown, 13 given). They need a folding wrapper like `FrontFoldedDamageVar`.
- The curtain call shows only HP returned. New line: "Drained 2 HP returned; 6 past your line lost (the fight ended)."
- Eleven fixed-Drain cards still give "it would take you below your Drain line" as the refusal reason. It becomes "it would take you to 0 HP".
- Bubble Aria's chooser label becomes "Gain 6 Block. Spend 3: draw 2 cards."

**Seat error:** "Usher+ Drained at HP 2" did not happen; the log shows HP 4 and 5. Bravura under Flutter is unverified and needs a live read.

## Next round

- **Telemetry first:**
  - Fanfare per fight: peak, at end or death, and each Spend with its bank before.
  - HP after the curtain call.
- **Same five seeds.** Read per-fight numbers, not wins.
- **Questions for that round:**
  - Is unspent Fanfare at death under 20?
  - What share of damage comes from Thunderous Applause?
  - How much Block a turn do Freminet and The Masquerade give together?
  - How much damage does High Stakes add?
- Then [USER]'s own run. "Spend up to X" is a keyword rule change and ships after his play.
