# Seat round, 2026-09-25 (afternoon)

**Why this round ran:**
- **Klee:** the numbers from the balance review (#658) had never been read by a seat on the text-pass build (0.2.3766+proto).
- **Furina:** a rule change on 0.2.3768+proto (#667). [USER]: "Stage members bow out when they are destroyed or replaced, not just when you deliberately spend them down to 0."

**The seats:** four, two per character, on the arms klee, companion, kokomi and furina-stage. The raw records are gitignored:
- GPT's: `review/qa/blindplay/20260925-165117` (Klee) and `20260925-171756` (Furina);
- Opus's: the session scratchpad.

| Seat | Character | Budget reached | How far it got |
|---|---|---|---|
| GPT-6 Sol (Codex), lane 1 | Klee | 150 acts | 6 fights, all won |
| Opus, lane 2 | Klee | 120 acts | 6 fights, floor 9, all won including the Phrog Parasite elite |
| GPT-6 Sol (Codex), lane 1 | Furina | 150 acts | 6 fights, stopped in the 7th |
| Opus, lane 2 | Furina | 120 acts | 5 fights won, stopped in the Terror Eel elite at 61/140 |

## Klee

**What played well:**
- **Both seats found the core decision on their own:** set off now, or let the Bombs grow a turn, timed against the enemy's intent.
  - GPT's best turn: one Strike carried Ka-pow! past the Terror Eel's stun threshold and stopped a 22-damage hit.
  - Opus's best turn: three stacked Bombs set off twice for exact lethal.
- **Planned turns from the smaller rules:** Mine timing, a Bomb jumping to a new enemy when its enemy died, and placing a Bomb just before a Set off card.

**What did not:**
- **Sparks still sit idle, for the third seat running.**
  - Opus ended fights with 2, 2, 4, 6 and 4 Sparks unspent. Its only Spark sink was Tinder Toss, and it judged every sink it was offered (Boom Badge, Sparkling Burst, Party Poppers) weaker than a card that places Bombs.
  - GPT held Bottomless Bag dead in two opening hands, with 1 Spark against a price of 2.
  - The price cuts in #658 did not change what the seats drafted.
- **Sparks 'n' Splash** was Opus's never-again card. It fires at the end of the turn, when the Bombs have usually been set off already.
- **Favonius Escort** was GPT's never-again card: it spends a Bomb the deck wants for damage.
- **Unclear on screen:**
  - "Companion" is never defined, and three offered cards trigger on it.
  - A revived Eye with Teeth showed "Bomb 0", though no Bomb was ever placed on it.
  - Shrink printed a reduced Ka-pow! hit but a full-size Bomb. That is the base game's rule for non-Attack damage; not changed.
- **Openings repeat.** Jumpy Dumpty opened every GPT fight. It is an innate starter card; not changed.

**What to change** (Klee seat-fixes PR):
- Sparks 'n' Splash fires at the start of the turn, after the Bombs grow, and leaves the Bomb in place. Upgraded, it costs 1.
- Bottomless Bag costs 1 Spark, down from 2.
- Every face that prints "Companion" gets a Companion tooltip.
- The empty Bomb badge is fixed.
- **Unspent Sparks go to [USER] as a pick.** Three seats and one round of price cuts say this is structural, not a matter of numbers.

## Furina

**What played well:**
- **The new Bow rule shows in play.**
  - GPT: "Thorns emptied the stage and Crabaletta's Bow dealt eight damage".
  - GPT also played Take the Stage on a full stage on purpose, to set off Usher's Bow.
  - This is the first seat to reach a full stage, so the orb-style summon (#659) is now seen working in the game.
- **Fanfare as a shield against Fanfare to Spend was the real decision.**
  - Opus held back a Spend to keep Crabaletta thick against a Strength-stealing enemy.
  - Opus's best turn: Fanfare banked the turn before paid for a double kill.
- **Performer acts as a damage plan.** GPT timed the end-of-turn acts to reach the Eel's stun threshold exactly, and built a Double Casting plus Full House deck.

**What did not:**
- **Usher's Bow wasted its Block.** Opus: it "never did anything" six times. A hit now makes him Bow on the enemy's turn, and his 4 Block expired before it could be used.
- **Neither seat could predict how much damage reached Furina.**
  - GPT: "I repeatedly misjudged how much damage would reach my HP after Block and Fanfare."
  - The log never showed the part of a hit that lands on her.
  - One Weakened hit on Usher was logged 1 higher than the seat's math.
- **Let the People Rejoice** was Opus's never-again card. It paid 1 damage per Fanfare, half the rate Spend pays.
- **Display nits:**
  - The Stage badge prints a "1" that never changes.
  - Right after Full House, the "after the acts" preview showed 3 Block, but Usher gave 6.
- **Automatic plays:** Double Casting then Full House, and Crabaletta+ at cost 0.

**What to change** (Furina seat-fixes PR):
- **Usher's Bow:** his front performer gains 4 Fanfare instead of Furina gaining 4 Block. Fanfare does not expire. On an empty stage it summons a performer at 4.
- **Let the People Rejoice:** deals twice the Fanfare.
- **The damage to Furina is shown:** the log gets a beat for the part of each hit that reaches her, and the Weakened-hit number is checked.
- **The display nits are fixed:** the Stage badge's number and the Full House preview.

## Tooling

- Embarking the lanes one at a time, after lane 1's game was up, worked all four times.
- The first `rest` at a rest site printed an error but still counted as an act. That goes to BACKLOG.
