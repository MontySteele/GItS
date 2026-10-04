Status: OPEN, draft 3 (direction ruled 2026-10-04; three picks at the end)

# Furina: re-founding the Stage (paper, draft 3)

**Where it comes from.** [USER], after the co-op run, 2026-10-03: "Furina
'technically works' in the sense that no individual component is broken,
but they do not play well with one another, and getting this any cleaner
requires fundamental design work."

**What is ruled.** [USER], 2026-10-04: "Let's go with 1a) and the rest of
your defaults, then draft a new paper for review." That rules:
- Fanfare is a currency on Furina;
- stage scaling is a separate drafted stat;
- directing is a card family;
- the 2026-09-07 "not a Defect with Fanfare for Focus" line is reopened,
  only for a stat that is not Fanfare;
- guests keep their seat against Salon summons;
- stars pay their acts from Fanfare;
- the front shield is retired;
- the starter pair is decided together.

**Draft history.** Draft 1 merged scaling and currency; Fable and GPT showed
that holding always won. Draft 2 went back to both. Both said build from
it, after the fixes listed in sec.7. Draft 3 takes them.

## 1. The rules

1. **Three seats, performers with no bars.** Performers take no hits and
   cannot be emptied. At the end of Furina's turn they act **front to
   back**. Combat opens with Usher on stage (Salon Solitaire).
2. **Two kinds of performer.**
   - The **Salon trio** (Usher, Chevalmarin, Crabaletta) is the cycling
     floor: cheap and cloneable.
   - A **Guest Star** is the cast you keep. One of each; a second copy
     Bows it and returns it.
3. **The Bow.** A performer that leaves acts once more, and that last act
   is **free**: a star does not pay for it. **Every Bow then gives 1
   Fanfare, after its act**, including Grand Finale's Bows, which do not
   remove anyone.
4. **Overflow: Salon summons never evict guests.**
   - A summon onto a full stage Bows your front-most Salon member.
   - A Salon summon when every seat holds a guest is a **walk-on**: that
     member acts once and Bows at once, without taking a seat. The card is
     never dead.
   - A guest summon when every seat holds a guest Bows the front guest.
5. **Fanfare is one number on Furina.** It has no cap and no fade, and
   hits never touch it.
   - **Filled by:** her Raise cards, the support guests, reactions, and
     Bows.
   - **Drained by:** Spend N on her cards, and the stars' acts. A star that
     cannot pay skips the act and stays; nothing is spent.
   - Acting front to back makes **seat order matter**: Charlotte in front
     of Neuvillette funds him the same turn, and behind him she does not.
6. **Rehearsal** is the stage's scaling, from drafted cards and one relic
   (sec.3). A performer's damage and Block acts deal 1 more per stack.
   Energy, draw and Fanfare never scale (`LAW.md`: "empowerment boosts
   numbers only, never turn-economy effects"). It shows as an ordinary
   Power badge with its total.
7. **Cue.** "Cue a performer" makes it act now, as it would at the end of
   the turn; a star pays as usual. A short star skips the act, and the
   card's other effects still happen. **The player chooses the
   performer** if the game can target one. If it cannot, the prototype
   falls back to "your front performer", and Step Forward stays as the
   one way to rearrange the stage.
8. **Retired:**
   - performer bars, absorption and the front shield;
   - the shield and bank seats;
   - the fade;
   - Wriothesley's "always front";
   - the leaver's Fanfare passing to the newcomer.

## 2. The cast (opening values; the sim sets them)

| Performer | Kind | Act |
|---|---|---|
| Usher | Salon | 4 Block |
| Chevalmarin | Salon | 2 damage to ALL |
| Crabaletta | Salon | 5 damage to a random enemy |
| Neuvillette | Star | pay 2: 7 Hydro to ALL |
| Clorinde | Star | pay 1: 8 Electro to a random enemy |
| Lyney | Star | pay 1: 5 Pyro to a random enemy, twice |
| Escoffier | Star | pay 2: 3 Cryo to ALL, then your Salon members act |
| Navia | Star | Geo to a random enemy equal to half your Fanfare, up to 8 (reads, never pays) |
| Chevreuse | Support | the first time each turn: pay 2, next turn gain 1 Energy |
| Charlotte | Support | gain 2 Fanfare |
| Sigewinne | Support | 3 Block, plus 2 for each time you lost HP since her last act |
| Wriothesley | Support | 4 Cryo to a random enemy, plus 1 per damage your Block stopped since his last act |
| Lynette | Support | 3 Anemo to a random enemy, one with an aura if any |

- **Guest cards give Fanfare on arrival.** "Neuvillette joins with 6"
  becomes "Summon Neuvillette. Gain 4 Fanfare."
- **Sigewinne is the second Block act.** Genshin's healer becomes
  protection; Usher no longer carries the cast's whole defence.
- **Chevreuse acts once a turn,** so Cue cannot turn her into an Energy
  engine.

## 3. The pool: what moves

The pool stays 78. About 30 rows change:

- **In: Gentilhomme Usher** (Common, 1): "Summon Usher. Gain 4 Block."
  Usher could not be summoned by name since the card left the pool on
  2026-09-28. **Out: Leading Lady**, which on one pool is Ousia Surge.
- **Directing.** Plot Twist, Revolving Stage and Stage Whisper become Cue
  Commons; Step Forward stays (rule 7). Bis!, Tutti! and Oratrice's
  Verdict already belong here.
- **Raise.** "Your back performer gains N" becomes "Gain N Fanfare" on Warm
  Reception, Hold Your Places, Cheered On, Opening Number, Season Tickets,
  Groundswell and Singer of Many Waters.
- **Readers.**
  - **Finale readers spend what they read.** Bravura and Bring the House
    Down are reset down from their per-point rates, which were raised
    twice to pay off starved bars of 1 to 8.
  - **Bank readers that do not spend read "up to 10".** That covers Ousia
    Surge and Pneuma Refrain. Without a cap, 20 Fanfare made Pneuma Refrain
    23 Block for 1 Energy every draw.
  - **Navia** stays the banking specialist, capped too.
- **Bow cards need new designs,** not a word swap. Final Bow, Intermission
  and A Five-Century Act read a single performer's bar today. Grand
  Finale, Da Capo and Thunderous Applause carry over.
- **Rehearsal:** an Uncommon Power (+1, +2 upgraded), a second Uncommon on
  a condition, and a Rare. Each replaces a row whose premise is gone
  (Counterclaim, Interposition, Guest of Honor's shield half). A relic is a
  fourth source. That is three or four sources, so most drafts meet one.
- **Defence:** Usher at 4, Sigewinne, Gentilhomme Usher. Regal Bearing and
  two Block rows are raised once the sim reads damage.
- **Critics' Darling** ([USER]'s idea): "Whenever your Fanfare changes,
  deal that much damage to a random enemy."
- **Co-op:** Share the Spotlight and The Crowd Roars are rewritten on the
  one number.

## 4. The starter pair

- **Curtain Rise** (Basic Attack, 1): "Deal 7 damage. Spend 3: deal 17
  instead." Unchanged; it teaches the currency.
- **Rising Applause** (Basic Skill, 1): **pick 1.**
  - **(a) "Gain 3 Fanfare."** Fable's view. With a Cue it is 4 Block plus
    3 Fanfare for 1 Energy, against Defend's 5. Once a guest stands in
    front, it becomes "Neuvillette acts again", most of the Uncommon
    Bis!. The Cue Commons teach directing instead.
  - **(b) "Gain 3 Fanfare. Cue a performer."** GPT's view. It teaches both
    verbs on turn one, and its preview must show the net Fanfare a paid Cue
    leaves.

## 5. How it gets proven

1. **The sim slice.** The rules, plus the starter pair, the trio,
   Gentilhomme Usher, Take the Stage, three Cue Commons, Neuvillette,
   Charlotte, Navia, Sigewinne, Bravura, Pneuma Refrain and the Uncommon
   Rehearsal Power. GPT's probes are its questions:
   - one Salon seat against three guests;
   - Charlotte and Navia banking, with Pneuma Refrain;
   - a draft that finds no Rehearsal;
   - a Wriothesley defence cast against paying stars;
   - a low-Fanfare turn where a Cue competes with the end-of-turn acts.

   The bar is that banking and spending both make real decisions, not that
   the bank stays low.
2. **Then the C#**, including whether the game can target a performer
   (rule 7), and the rest of the ~30 rows.
3. **A rule change,** so [USER] plays it and a two-seat round reads it.

## 6. Picks

1. **Rising Applause:** (a) "Gain 3 Fanfare." or (b) "Gain 3 Fanfare.
   Cue a performer." Default: (a).
2. **The scaling stat is named Rehearsal** and shown as a Power badge with
   its total (GPT), rather than left unnamed (Fable). Default: named. A
   total needs a badge, and a badge needs a name.
3. **The walk-on** (rule 4): a Salon summon onto a stage of three guests
   acts once and Bows, never evicting a guest. Default: yes. (Or the
   summon is refused.)

## 7. What draft 3 took from the second reviews

- **From Fable:**
  - Usher's card comes back, and Sigewinne becomes the second Block act;
  - bank readers are capped and finale readers reset down;
  - Chevreuse acts once a turn;
  - performers are chosen, not seated;
  - three or four Rehearsal sources;
  - Leading Lady is cut;
  - a short star's Cue is defined.
- **From GPT:**
  - acts resolve front to back, so seat order matters for funding and one
    rearranger stays;
  - overflow no longer contradicts guest protection (draft 2 let a Salon
    summon evict a guest);
  - free Bows, and their Fanfare timing, are written down;
  - the Bow cards that read a single bar get real redesigns;
  - Rehearsal shows its total;
  - the probes list.
