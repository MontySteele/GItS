# Seat round, 2026-09-25 (night): the first Guest Stars

**Why this round ran:** a new card batch and rule changes on 0.2.3794+proto (#677):
- eight Guest Star cards, with no guest cap and one of each guest;
- the Salon trio can be cloned;
- every act pays, and the Bow is free;
- a recast adds the leaver's Fanfare;
- hit-Bows are immediate again.

The card art (#678) was merged after this build, so the seats played without it. Blind seats read text only, so the art could not change their results.

**The seats:**

| Seat | Budget reached | How far it got |
|---|---|---|
| GPT-6 Sol (Codex), lane 1 | 86 acts, stopped by "Selected model is at capacity" | 4 fights won |
| Opus, lane 2 | 120 acts | 4 fights won without losing HP, stopped in the Byrdonis elite at 51/78 |

The GPT record is `review/qa/blindplay/20260925-221903`; the Opus record is in the session scratchpad.

## What played well

- **Let the People Rejoice at twice the Fanfare.** It was an Opus never-again card earlier today. GPT's best turn is now "three performers bowed as Let the People Rejoice cleared both small slimes".
- **GPT's stage held with Block**, as [USER] said it should: "the Ushers and Toric Toughness covered its attacks". Its lesson: "avoid adding more plain Block cards. Once the stage was established, I often had enough defense." GPT had no never-again card.
- **Spend again carried the Opus seat's real choices:**
  - paying from a lone Usher who is both the front and the back ("spending my tank");
  - playing Spend before Summon, because a newcomer arrives unable to pay;
  - banking on a quiet turn for two Spends the next turn.

## What did not

- **Only one guest was drafted: Opus's Wriothesley, and he failed.** He joined at the back. After the front died, the overflow went to Furina, and his act read "nothing landed".
  - The back performer's tip said "Hits reach it last", which is false: rule 6 sends overflow to Furina, never to the next seat.
  - He was the Opus seat's never-again card.
- **Undefined on the seat page:** Elemental Reaction (Courtroom Drama), Swirl and aura (Guest Star: Lynette), Cryo, and Companion.
- **Screen and outcome disagreed:**
  - under Shrink and Vulnerable, Soloist's Solicitation and Curtain Rise previewed damage differently;
  - an arrival line put Usher in the front seat when the stage line had him at the back;
  - an event transform screen did not print a card's cost.
- **GPT's repetitive fight:** the crawler, where the stage covered everything and the turns were basic attacks.

## What to change

The guest fixes PR:
1. **The back performer's tip becomes "Hits never reach it."** Every other surface that says otherwise is fixed too.
2. **Wriothesley joins at the front.** On a full stage the back performer Bows to make room, and he takes its Fanfare on top of his own.
3. **The seat page gets fixes:**
   - the arrival line's seat;
   - every glossary word attaches where it is printed;
   - the damage previews go through the same modifiers;
   - event screens print card costs.

Seven of the eight guests are still unseen by a seat. The next round should grant a guest deck, or [USER] plays one, before any guest number moves.
