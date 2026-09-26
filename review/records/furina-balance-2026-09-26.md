# Furina balance review, 2026-09-26

**Why this review:** [USER]'s first solo Stage run, on 0.2.3820+proto, beat Ascension 2 ("Aeonglass was a decent struggle"). His verdict was "Overall I think the core concept is sound". His notes, in his words:

- "some of her powers probably create absurd levels of Fanfare under the right conditions, such as stacking multiple copies of A Rapt Audience, and I didn't notice any Fanfare decaying"
- "Some cards definitely need a balance review, such as Tutti! against the other 'performer acts now' cards I saw"
- "unused boxes to her left" crowd the UI. That is a separate cleanup PR.
- "The overhead turn predictor is a decent start, but we should think of how to rework the element to be less mechanical and more flavorful" (pick 2)

His run, from his game log: 550 card plays. The most-played Stage cards were Step Forward (33), Rising Applause (33), Curtain Rise (33, Spend mode most of the time), Tidal Flourish (25), Let the People Rejoice (23), Lynette (20), Full House (18) and Thunderous Applause (17). He played A Rapt Audience 7 times.

## Yardsticks

- **One act is worth about 0.6 Energy.** Usher's is 3 Block, Chevalmarin's 2 damage to ALL, Crabaletta's 5 damage to a random enemy. A full stage acting is about 2 Energy.
- **One Fanfare is worth 2 to 3 damage.** Curtain Rise turns Spend 3 into 6 more damage, and Bravura pays 3 per point. That makes a Fanfare about a third of an Energy.
- Base-game rates: an Attack pays 6 to 9 damage per Energy, and Block pays 5 to 8.

## Why the Fanfare ran away

- **A Rapt Audience scales with copies.** Each copy adds half the Fanfare the front loses (all of it when upgraded). Two upgraded copies turn every hit on the front into twice its size in Fanfare at the back: a printer, not a conversion.
- **The fade has an exit.** Rule 12 fades only the seats behind the front. Step Forward (0 cost, played 33 times) moves the bank to the front, where it never fades and regenerates. Rapt Audience's gains also arrive on the enemy's turn, after that turn's fade. So a big bank never met the fade. That is why he "didn't notice any Fanfare decaying". The fade also has no animation in game; the cleanup PR adds one.

## Changes (Claude ships these; prototype rows only)

| Card | Was | Now | Why |
|---|---|---|---|
| Tutti! (U) | 1 (upg 0): all performers act now | **2 (upg 1)** | Three acts are worth about 2 Energy, more with guests. At 1, and free when upgraded, it beat every other card that makes a performer act. |
| Bis! (U) | 1 (upg 0): your front performer acts now | **1 (upg 0): your front performer acts twice** | One act for 1 Energy was the worst card in its family. Twice is the single-performer version of Tutti!, aimed at the shield or a Wriothesley. |
| Full House (U) | 2 (upg 1) power: full stage at end of turn, acts twice | **3 (upg 2)** | Every turn it is worth about 2 Energy on a full stage, copies stack, and the simulator ranked it with the strongest decks. It keeps its condition. |
| A Rapt Audience (U) | back gains half (upg all) of the Fanfare the front loses | **back gains 2 (upg 3) Fanfare whenever an enemy hits your front performer; needs 2 performers** | A fixed amount per hit. Copies still add up, but by the number of hits, not the size of the bank. |
| Ousia Surge (U) | 1 (upg 0): damage = back's Fanfare | **1; upgrade +4 damage** | It doesn't spend the Fanfare. At 0 cost two copies hit a big bank twice for free. |
| Pneuma Refrain (U) | 1 (upg 0): Block = front's Fanfare | **1; upgrade +4 Block** | The same fault, on the front seat. |
| Grand Entrance (U) | 2: 10, or Spend 5 for 20 | **2: 12, or Spend 5 for 24** (upgrade +4 each, unchanged) | 10 for 2 Energy was under a Strike's rate. |

## Left alone, and watched

- **Thunderous Applause** (draw 1 and +2 Fanfare per Bow) with **A Five-Century Act** (every Bow returns at the back). Together they are the Bow engine, and he played the pair a lot. It is a Rare, so it bends rather than being removed, and the fade now governs its Fanfare.
- **Repeat Guest Star copies:** the 8-Fanfare guests (Lynette, Sigewinne, Wriothesley) give 8 Fanfare, a free act and a body for 1 Energy. That is more than Rising Applause's 5. He played Lynette 20 times. If the fade change (pick 1) doesn't rein it in, the repeat copy is the next lever.
- **Gala Dinner** (+3 to each performer). It is spread across the seats, and two of them fade.
- **Let the People Rejoice.** The Rapt Audience fix and the fade take away its absurd case, so its number stays.
- **Starter cards** (Take the Stage, Curtain Rise, Rising Applause) are never changed.

## Picks for [USER]

1. **The fade and the front seat.**
   - **(a, default)** The front fades too, but only above 10. The seats behind it keep the line at 5. The shield can hold twice what the bank does, but not without limit, and a lone performer uses the front's line. The front tip gains "At the end of your turn, it loses half its Fanfare above 10."
   - **(b)** One line of 5 for every seat, front included.
   - **(c)** The front stays exempt; the Rapt Audience fix alone.
2. **The turn predictor.**
   - **(a, default) Cues on the performers.** Each performer shows its act over its head the way an enemy shows its intent: an icon and a number, such as a sword 5, a shield 3, a wave 2 for ALL, or a coin for a payment. Fade and incoming hits show as chips on its bar. The text box goes. StS2 players already read intents at a glance.
   - **(b) A playbill.** The box stays, restyled as a theatre programme: a billing line per performer ("Crabaletta … 5 to a random enemy"), the fade as "the applause fades", and the damage split as "the critics". Same information, more flavour, still text.
   - **(c)** Both: cues on the performers, and a one-line playbill for the damage split only.
