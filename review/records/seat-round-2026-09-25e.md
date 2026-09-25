# Seat round, 2026-09-25 (late night): every guest, granted

**Why this round ran:** the guest fixes (#680) on 0.2.3809+proto. The last round saw only one guest (Wriothesley), so this round gave each seat four Guest Stars at the start of the run.

- Lane 1 got Neuvillette, Clorinde, Charlotte and Chevreuse.
- Lane 2 got Wriothesley, Sigewinne, Navia and Lynette.

Because the guests were granted, not drafted, this round cannot say how strong they are. It can only say whether they read and play.

Codex failed to connect (the websocket closed, 0 actions), so both seats were Opus. The records are in the session scratchpad.

**The seats:**

| Seat | Budget reached | How far it got |
|---|---|---|
| Opus, lane 1 | 120 acts, 515 s | 5 fights won; stopped in the Skulking Colony elite at 40/78 |
| Opus, lane 2 | 120 acts, 580 s | 5 fights won; stopped in the Phrog Parasite elite at 42/78 |

## What played well

- **Seven guests were played, and several carried the best turns.** Lynette was the exception.
- **Cashing a guest:**
  - Lane 1's best turn was Clorinde, then Rising Applause, then Bravura, for 35 damage before either cultist acted.
  - A fight later, that seat aimed Bravura at the other enemy on purpose, because it had learnt that the Bow lands before the card's own hit.
- **Wriothesley at the front works.** Lane 2's best turn left him unblocked to charge, then Tutti! fired his Cryo, which set up Superconduct for Clorinde. Sigewinne emptied herself into him, and her Bow opened the seat Clorinde took.
- **Who pays became a decision.**
  - Spend and Chevreuse's upkeep both come from the back seat, so the order guests went down decided whose Fanfare was eaten.
  - Neuvillette went 6 → 0 in one turn with Chevreuse and Clorinde behind him. The forecast said so before the seat committed, and it played him anyway for the free Bow.
- **The full stage is the kit's central question.** Every summon onto a full stage bows the front performer, so both seats weighed which performer to give up and when.
  - Lane 2 also called it a clog: once, four of its five cards would have bowed Wriothesley, and it left 2 energy unspent.
- **Legibility that helped:** Bravura's live number on its face, the Spend chooser appearing only when the back can pay, and the forecast's "Crabaletta 1 → 0 (leaves)".

## What did not

- **Guest Star: Lynette was never played** (lane 2's never-again card): "nothing reliably leaves an aura for her Swirl."
- **Take the Stage** was lane 1's never-again card, a random performer at 1 Fanfare next to guests arriving with 4 to 8. It is a starter basic, so it stays.
- **Usher's Bow Block still protected nothing.** It lands after the killing hit's overflow has already reached Furina (lane 2, fights 2 and 6).
- **The forecast has gaps:**
  - It shows the acts' Block and Fanfare but not the damage they deal. Lane 2 misread the lethal and left the Beetle on 1 HP.
  - The damage split ignored the next performer stepping up once the front empties.
  - On one screen it gave Block as 3 in one line and 6 in the next.
- **The seat log misled:**
  - Wriothesley's act was reported as "1 Cryo" (14 by his text): the log printed the HP the target lost, not the hit's size.
  - An arrival line named the seat a guest was pushed to later, not the one it joined.
  - A reaction line carried over from the previous fight.
  - The reaction glossary said no reaction was reachable, with Neuvillette (Hydro) in hand against an Electro aura.
- **Unclear text:**
  - The Summon tip's "the newcomer adds its Fanfare".
  - Performer acts ignore Furina's Shrink, which the seat read as covering "every hit you land".
- **Dead on quiet turns:** Stage Presence and Regal Bearing when nothing was attacking. This is expected of Block cards.

## What to change

The granted-guest fixes PR:
1. **A performer emptied by a hit Bows before the rest of that hit reaches Furina,** so Usher's Bow Block catches the overflow. The Bow stays immediate, as [USER] ruled.
2. **The forecast:**
   - it shows each act's damage and target;
   - it walks an attack hit by hit;
   - it takes Block from one computation.
3. **The seat log:**
   - act lines print the hit and say when the target had less HP;
   - arrival lines keep the arrival seat;
   - reaction lines clear between fights;
   - the reaction glossary counts guests' elements.
4. **Text:**
   - Summon: "On a full stage, the front one Bows and leaves its Fanfare to the newcomer."
   - The seat page notes that performer acts ignore Strength, Weak and Shrink.
5. **Lynette:** "End of your turn: deal 3 Anemo damage to a random enemy, one with an aura if any." Her act now always lands, and still Swirls an aura when it finds one.

**Not changing:**
- Take the Stage, because it is a starter.
- Thorns hitting the front performer, which the log reported.
- Neuvillette's drain, and Chevreuse's "Spend 2" wording, which the seat learned in one turn.

**Watch in drafted play:** the full-stage clog, and whether guests crowd out the trio's summons.
