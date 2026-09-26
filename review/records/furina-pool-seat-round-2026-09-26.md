# Furina's supporting pool: seat round, 2026-09-26

**Why this round:** a new card batch (the 29 of `review/active/furina-supporting-pool-2026-09-26.md`, built in #692 and #694, with art in #693). [USER] asked for "many Opus agents to test the deck at different points (acts 1 / 2 / 3, different deck strategies, etc)". The build was 0.2.3859+proto, at A0. Seven blind Opus seats played; their records are gitignored in `review/qa/seats-2026-09-26/furina-*.md`.
- Two seats played whole runs from Neow.
- Five started from a deck the coordinator dressed for one plan (`skip_act` plus grants). Those runs are not comparable to anything (Guardrail-7).

Caveat: the seats are Opus, and Claude authored the kit (R217 C). [USER] asked for Opus seats; read this as the user's instrument, not a blind grade.

## How far each got

| Seat | Start and plan | End |
|---|---|---|
| Full run, lane 1 | From Neow. Back-bank and Spend, then Full House, then Neuvillette and Navia | 24 of 25 fights won. Beat The Kin and Kaiser Crab. Died to Aeonglass with it on about 386/512 |
| Full run, lane 2 | From Neow. Reactions, then churning the stage, then Escoffier and Lyney | Beat The Kin. Died in act 2 to the elite Decimillipede |
| Act 2, Solo | Dressed Solo; drafted into it (3 Soliloquy, 2 One-Woman Show) | **Won**: The Insatiable, then Test Subject #C33 |
| Act 2, guests | Dressed guests and reactions | Beat The Insatiable. Died to Aeonglass with it at 40/512 |
| Act 2, bank | Dressed bank and Spend; drafted two Wriothesleys | Beat The Insatiable and three act-3 elites. Died to a fourth |
| Act 3, Bows | Dressed Bow engine | Died on act 3 floor 13, at an elite reached on 6 HP |
| Act 3, shield | Dressed shield with Sold Out and Full House | Died on act 3 floor 4 to Devoted Sculptor. My deck had no damage |

## What played well

- **Every plan has a real turn.** Each seat named a MOST WANTED turn built on a different mechanic:
  - Bows: Let the People Rejoice bowed the stage, then Da Capo cashed eight Bows for 31.
  - Solo: Bravura emptied the stage mid-turn, and Soliloquy turned Crashing Waves into a wipe.
  - Guests: Regina's Hydro plus a Cryo companion froze a 40-damage hit.
  - Wriothesley: two copies turned a lethal 26 into 0 damage taken and a 69-Cryo hit.
  - Churn: a stage-churn turn ended in an exact doubled kill.
- **The Solo path works**, from the Stage's opposite end. A seat drafted into it unprompted and won.
- **The decisions seats named** were who stands in front, spending the bank now versus keeping it as a tank, summon order, and when to play the second copy of a guest.
- **Reactions do appear** in a guest deck: Crystallize, Frozen, Vaporize and Melt. Regina of All Waters with Escoffier re-freezes every enemy each turn.

## What did not

1. **Take the Stage** (a starter card) was a NEVER AGAIN for three seats. On a full stage it Bows the front performer, and it switches off every Solo payoff. See the pick below.
2. **Stage Whisper** was a NEVER AGAIN for two seats: the back performer is nearly always at 1–2 after the fade and Spends. It has been reworked, see below.
3. **Lyney's** end-of-turn swap kept undoing the front a seat had built. Reworked.
4. **Echoing Hall** only ever gave +1. **Full House** with Sold Out can never fill four seats in a race; that deck was my dressing, and a seat that drafted Full House itself used it well. Both are watched.
5. **Thin Block at the front seat** cost both full runs. That is the intended weakness: a big single hit rips through the front (rule 6). Watch it in [USER]'s run.

## Defects, fixed

- **#696:** Lynette's forecast target was an internal id and bricked a lane. Enemy names are now formatted.
- **#698:**
  - The forecast now counts hand damage (Burn, Wither and the rest). It had said "you take 13" at 15 HP, and the seat died.
  - Performers returned by A Five-Century Act after an enemy-turn Bow sat out a turn. They now act.
  - The Crystal Sphere stall is fixed: the page offers `reveal`.
  - Bring the House Down no longer carries the Spend tip.
  - Star Billing now carries the Guest Star tip.
  - The lone-performer tip is clearer.
  - Wriothesley's face now says a full stage Bows the back performer.
  - Numbered potions work.
  - The log's direction and repeat lines are fixed, and enemy letters stay put.
- **Hydro rides the hit (#699):** Furina's "deal N and apply Hydro" modes now deal Hydro damage, so Vaporize multiplies them and Courtroom Drama's debuffs land before the hit. The seat that saw Vaporize "listed but at face value" was right.
- **BACKLOG:** the enemy side of the forecast (Frozen, Stun, Superconduct, minions the acts kill first), Soumetsu's ticks, Bravura's preview with Soliloquy, and the Trial page.

## Changed by Claude (prototype rows)

- **Lyney:** "If he is not in front, he swaps places with your front performer." Once in front, he stays.
- **Stage Whisper:** cost 1 (upgraded 0). "Your other performers give all but 1 of their Fanfare to your front performer. Draw 1 card." It pulls the whole stage into the shield.

## Pick for [USER]

1. **Take the Stage** (starter; "Summon a random performer"). Three seats named it NEVER AGAIN: it Bows your front performer on a full stage, and it breaks the Solo path.
   - **(a, default)** Keep it. Starter cards stay bad, and removal and transforms are the answer.
   - **(b)** On a full stage it summons nobody and draws 1 card instead. That is a starter change, which only [USER] can make.
