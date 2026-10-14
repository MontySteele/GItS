# Klee and Varka: story chains, 2026-10-14

**Why.** [USER], 2026-10-14: "as our characters hit release-readiness
(currently meaning Klee and Varka), we should try to give multiple unique events
... that expand on their lore and characterization in a direct way." And:
"Rather than one event per act, we're probably looking at multiple possible
events per act, with no more than one firing per act - which one you do get in
act 1 (if any) determines which you get in act 2, etc, with a branch for if you
managed to skip an act. The events should be balanced around existing ones - so
some are overall bad, some are overall good, and anything strong should be
counterbalanced with a price." On framing: "the characters are all currently
in the Spire, so any event that clearly happens outside of it needs to be
framed as a recollection or memory of some kind."

## 1. The shape

- **Act 1** offers one of three events, chosen at random. Each starts a
  different thread.
- **Act 2** follows the thread. If no act-1 event fired, act 2 offers the
  **home thread** (Jean's letter for Klee, the Wolf for Varka).
- **Act 3** closes the thread. Two threads share the familiar finale, and one
  thread gets its own. If act 2 was skipped, act 3 offers the familiar finale.
- **Each character keeps the existing three events** and gains five new ones,
  so 8 per character.
- **Every option gets a short result line** in the character's voice. The
  current events reshow their page instead (`StoryEvents.cs:67`).
- **Starsnatch Cliff becomes a memory**, as you ruled.

**Balance against the base game** (a census of all 57 StS2 events,
`scratchpad/sts2-event-census.md`):
- 14 events are good, 42 mixed and 1 bad.
- A relic usually costs about 8 HP, about 125 Gold, or a mild curse.
- Gold rewards run from 35 to 150.
- About one event in five offers a curse.

Each chain below has one event that leans bad, one that leans good, and the
rest mixed.

| | Act 1 (random) | Act 2 | Act 3 |
|---|---|---|---|
| **Klee** | Starsnatch Cliff (a memory) | A Letter from Jean | The Knights Come Looking |
| | Dodoco Goes Missing *(new)* | Dodoco's Trail *(new, leans bad)* | The Knights Come Looking |
| | Mom's Marks *(new)* | Alice's Cache *(new, strong with a price)* | Mom Drops In *(new)* |
| | none | A Letter from Jean | The Knights Come Looking |
| **Varka** | Dispatch from Mondstadt | The Second Satchel *(new, leans bad)* | The Acting Grand Master *(new)* |
| | The Rearguard *(new)* | The Wolf of the North | The Long Way Home |
| | A Song on the Wind *(new, a memory)* | The First Exam *(new, a memory)* | The Long Way Home |
| | none | The Wolf of the North | The Long Way Home |

## 2. Klee

**Starsnatch Cliff, now a memory.** The options and effects are as they are
today. The page now reads:

> A still pool in the Spire's stone is full of fat, silver fish. It looks just like the pond below Starsnatch Cliff, back home. Klee has three bombs left and nobody is watching. She remembers Jean's face the last time.

| Option | Effect | Result |
|---|---|---|
| Blast the pond! | Gain 75 Gold. Add **Confinement**. | KABOOM! Fish everywhere. Klee hopes the Spire doesn't tell Jean. |
| Just one little bomb. | Add **Fish Blasting**. | Just a little one. Klee keeps the biggest fish for Dodoco. |
| Leave them be. | Remove a card. | Klee puts the fuse away. Jean would be proud. Probably. |

**Dodoco Goes Missing** (act 1, good):

> Klee reaches into her backpack. Snacks, bombs, a shiny pebble... no Dodoco! Small, round tracks lead off into a dark side passage.

| Option | Effect | Result |
|---|---|---|
| Follow the tracks into the dark. | Lose 8 HP. Gain a random relic. | Something bites. But Dodoco was sitting on a treasure the whole time! |
| Call for Dodoco really loud. | Add an upgraded **Dodoco Tag**. | "Dodoco! Dodo-co!" It hops back, a little dusty. |
| Make a new Dodoco from spare parts. | Transform a card. | It's a bit lopsided. Klee loves it anyway. |

**Dodoco's Trail** (act 2, leans bad):

> The round tracks again, fresher now. They end at a crack in the floor. Something down there is giggling.

| Option | Effect | Result |
|---|---|---|
| Squeeze through the crack. | Lose 12 HP. Upgrade 3 random cards that place a Bomb. | Klee gets stuck twice and finds a whole stash of fuses. |
| Drop a bomb down first. | Gain a random relic. Add **Confinement**. | KABOOM! Whatever was giggling isn't anymore. Jean will hear about this. |
| Leave a snack and wait. | Lose 50 Gold. Remove a card. | Klee waits a long time. She eats the snack herself. |

**Mom's Marks** (act 1, good):

> Scratched into a pillar, at exactly Klee's height: a little bomb, a star, and "Alice was here! ♪". More marks lead upward.

| Option | Effect | Result |
|---|---|---|
| Follow Mom's marks. | Gain 100 Gold. | The marks lead to a little pouch of Mora. Mom always leaves snacks money. |
| Copy down the recipe beside them. | Add **Alice's Recipe**. | Klee copies it very carefully, with only one smudge. |
| Add a mark of her own. | Upgrade 2 random cards. | A bomb, a star, and "Klee was here too!" |

**Alice's Cache** (act 2, strong with a price):

> At the end of Mom's marks is a little chest with a note. "For my darling Klee. Open in an emergency only! And don't tell Jean. ♪"

| Option | Effect | Result |
|---|---|---|
| Is this an emergency? Yes! | Gain a random rare relic. Add **Confinement**. | It's amazing. Jean is going to find out. |
| Save it for a real emergency. | Gain 2 random potions. | Klee carries the chest very, very carefully. |
| Leave it for the next adventurer. | Transform 2 cards. | Klee swaps in two of her own bombs. Fair's fair. |

**Mom Drops In** (act 3):

> "There's my little spark!" Alice drops onto the landing, her cloak all pockets and not a speck of dust on her. "Did you open the emergency chest? Of course you did."

| Option | Effect | Result |
|---|---|---|
| Show Mom your best bomb. | Upgrade every card that places a Bomb. Lose 8 Max HP. | Alice: "That's my girl! A little lopsided, but that's how you know it's yours." |
| Ask Mom for a new trick. | Add an upgraded **Alice's Introduction Magic**. | Alice: "Watch closely. I'll only show you twice." |
| Hug. | Heal to full. | Alice: "Go on, finish your climb. I'll see you in Mondstadt." |

Klee answers each one: "Mom! Can you stay? ...No? Okay. I'll be careful!"

**A Letter from Jean** and **The Knights Come Looking** keep their options
and effects. Each Jean option gets a result line:
- Read it twice: "Klee reads it twice, then a third time. She tucks it in next
  to Dodoco."
- Write back: "Dear Jean, I will be good. Mostly. Love, Klee."
- Paper bomb: "It folds into a perfect little bomb. Jean won't mind.
  Probably."

## 3. Varka

His results show what he does, as GPT suggested: he gives orders, checks on
people, and makes room.

**The Rearguard** (act 1, good):

> Three Favonius knights sit against the wall of the landing, bandaged and grey with dust. They straighten when they see him. "Grand Master. We fell behind. We can still fight, sir."

| Option | Effect | Result |
|---|---|---|
| Take the rear yourself. | Lose 10 HP. Choose 1 of 3 random Knights. | "You lot walk in front. I'll keep the stairs behind us." |
| Share out the rations. | Heal 15 HP. | He splits his own last loaf three ways and calls it a feast. |
| Send them down with a message. | Gain 2 random potions. | "Tell Jean we're fine. Then tell her again, she won't believe you." |

**A Song on the Wind** (act 1, a memory):

> The wind on this landing carries an old Mondstadt tune about a young man who failed his knight's exam, then ambushed the Grand Master to argue about it. Varka knows the song. He was the young man.

| Option | Effect | Result |
|---|---|---|
| Hum along. | Heal 15 HP. | He gets the second verse wrong. He always does. |
| Toast absent friends. | Lose 75 Gold. Gain a random relic. | He pours out the good wine, a little for each of them. |
| Remember Valentine's advice. | Remove a card. | "A knight needs a reason of his own." He's had his for a long time. |

**The First Exam** (act 2, a memory):

> Practice dummies line the landing, the way they line the yard behind Favonius Headquarters. Varka remembers failing his first exam there, and the speech he had ready for Grand Master Valentine.

| Option | Effect | Result |
|---|---|---|
| Pass it this time. | Lose 6 Max HP. Add an upgraded **Four Winds' Ascension**. | Every dummy down in one pass. Only a few years late. |
| Give the speech anyway. | Upgrade 2 random cards. | It's a better speech than he remembered. |
| Walk past. He has nothing to prove. | Heal 20 HP. | He gives the nearest dummy a friendly pat on the way by. |

**The Second Satchel** (act 2, leans bad):

> Another courier, another satchel, heavier than the first. "The Acting Grand Master says these are the urgent ones, sir. She underlined *urgent*."

| Option | Effect | Result |
|---|---|---|
| Sign them on the spot. | Lose 10 HP. Remove every **Overdue Reports**. | Writer's cramp is a battle wound. He's sure of it. |
| Hand them to the courier. | Lose 75 Gold. Remove a card. | "Consider it a promotion. And a raise." |
| Lose them on the stairs. | Gain 100 Gold. Add **Overdue Reports**. | He loses them very carefully. |

**The Acting Grand Master** (act 3):

> Jean is waiting on the landing, alone, a ledger under her arm. "Five years, Grand Master. I came up to collect." She almost manages not to smile.

| Option | Effect | Result |
|---|---|---|
| Let her lead the last stretch. | Add an upgraded **Jean: Dandelion Breeze**. | "Lead on, Acting Grand Master." "Just Jean, today." |
| Promise a full report at Angel's Share. | Remove every Curse. Lose 25 Gold for each. | "Every word. Diluc's paying." |
| Hand her the seal for the day. | Upgrade 3 random cards. Lose 5 Max HP. | He carries her ledger the rest of the way. |

**Dispatch from Mondstadt**, **The Wolf of the North** and **The Long Way
Home** keep their options and effects. Each option gets a result line. The
Long Way Home has one variant opening for the Rearguard thread: "The three
from the rearguard march at the front of the column, grinning."

**Lore check.** Varka's exam story (failing his first exam, then arguing with
Grand Master Valentine) comes from one user-edited source
(`varka-lore-census-2026-10-13.md`, "verify"). If it does not hold up in game,
A Song on the Wind and The First Exam change to his Knight of Boreas years.

## 4. The build

- **New effects:** random relic, random rare relic, potions, transform, Max HP
  loss, heal to full, and "remove every X". The existing effect types cover the
  rest.
- **Routing:** the chosen event is saved per act on the run, and act 2 and
  act 3 read it.
- **Act 3 in co-op:** this is unchanged. Each character's event goes only to
  its owner.
- **Cards named here that already exist:** Dodoco Tag, Alice's Recipe, Alice's
  Introduction Magic, Fish Blasting, Four Winds' Ascension, and Jean: Dandelion
  Breeze.

## Picks

1. **The chains as written** (two threads plus home, 8 events each).
   - **(a, default)** Yes, as written. You can edit any line.
   - (b) Fewer: two act-1 events per character.
2. **Alice in person.** Klee's mother appearing on screen is a big lore
   step.
   - **(a, default)** Yes: "Mom Drops In".
   - (b) Keep Alice to notes and marks. Act 3 of that thread becomes a last
     note.
3. **Numbers.**
   - **(a, default)** As above, matched to the census.
   - (b) You name the ones to change.
