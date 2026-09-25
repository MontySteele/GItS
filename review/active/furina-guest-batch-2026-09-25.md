Status: RULED 2026-09-25 evening (picks at the end); build after the draft-3 fixes land. Guests are Furina's own cards, separate from the Companion pool.

# Furina: the Guest Cast batch (paper, 2026-09-25, draft 2)

**What this is.** The first batch of the Stage's pool expansion: Fontaine characters step onto the Stage as performers.

**Where it comes from.** [USER]: "my vision on Furina is to move away from merely summoning her Hydro summons and allow for character-effect cards to reach the Stage as well."

**What it builds on.** The draft-3 rules in `furina-stage-brief-2026-09-08.md`, now on this branch:
- rule 9: the Bow is the act, once more;
- rule 10: no act applies Hydro;
- rule 12: performers behind the front lose half their Fanfare above 5 at the end of the turn.

**What changed in draft 2.** It answers [USER]'s notes and GPT's read of draft 1:
- the Bow promise;
- the payment order on replacement;
- repeated acts;
- a Fanfare-hungry stars against Fanfare-neutral support split;
- guests that do more than "5 damage of X";
- a visible forecast;
- the LAW question on elements;
- an outline of the supporting pool.

## The kit's shape

[USER]: "Similarly to Defect, the most common thrust of a run might generally revolve around what the Stage is doing, with additional paths for Furina-focused gameplay … if you happen to draw into them."

- Guests are the Stage's power path.
- The Salon trio (Usher, Chevalmarin, Crabaletta) is the floor.
- Furina's own paths (below) are the side routes, as Claw and status decks are for Defect.

## The frame

1. **A guest card is titled "Guest Star: <name>"**, for example "Guest Star: Neuvillette". [USER], pick 1: "I did actually mean the card's title (so you can see at a glance if the card is summoning someone or if it's a regular companion card)". The face says what arrives, "Neuvillette joins the stage with 6 Fanfare.", and the guest's act lives on its performer tip, the way Defect's orb cards leave the orb's effect to the orb. The Guest Star tip: "A performer who joins the stage, one of each. A second copy makes it Bow, then return with the new Fanfare added."
2. **It summons to the back-most empty seat.** On a full stage it is a recast: the front performer Bows and leaves, and the guest arrives at the back holding its own Fanfare plus what the front performer had left. The same holds for the trio's summons.
   - **No guest cap** (2026-09-25; [USER]: "why not just let the Stage be filled with guest stars if the player wants? If they put 3 in there and there's no Fanfare generation, then the player will struggle, but that's a skill issue").
   - **One of each guest:** a second copy makes that guest Bow (free), then return to its seat with the new Fanfare added.
   - **Guest Star: Wriothesley joins at the front instead,** and the others shift back one. From the guest seat round, 2026-09-25: "he joins at the back, where hits never reach him, so his act lands nothing". On a full stage, the back performer is the one that makes room: it Bows and leaves, and he arrives at the front holding his 8 plus what it had left. A second copy still Bows him and returns him to his own seat.
   - **The trio can be cloned** ([USER]: "Let's allow for copies and then check the balance"). A named trio card always summons.
3. **Guests are performers in every other way.** A guest's Fanfare is its health. It takes hits in front, fades behind the front, and counts for Full House and the rest.
4. **Every act pays.** A repeated act (Full House, Tutti!, Bis!) pays again. So Full House makes Neuvillette burn out twice as fast for the same total output, and Tutti! taxes the cast through Clorinde a second time. That is a tempo choice, and it is meant.
5. **The Bow is free.** A guest's Bow is its act without the payment. For a guest with a Spend mode, the Bow gets the paid version free. The promise "acts one last time" therefore always delivers, and burning a guest out ends in a finale.
   - This settles the replacement order: the leaver's Bow costs nothing, so the newcomer inherits all of the leaver's remaining Fanfare. The Bow happens first, then the arrival.
6. **A guest that reads something resets it when it acts.** Wriothesley reads the Fanfare he lost since his last act, so a repeated act reads 0 and Full House does not double him. His Bow on a hit reads the hit that took him down.
7. **You can see the end of the turn before you end it.** In game and on the seat page, the Stage strip shows each performer's bar after the acts, the payments and the fade. The enemy's intent shows how much reaches Furina.
   - Both seat rounds today misjudged the damage that reached her, and guests add two more moving parts.
   - This ships with the batch, not after it. GPT: "A report helps the designer; a visible forecast helps the player."

## Two kinds of guest

[USER]: "make the premium 5 star guest cards relatively Fanfare-hungry but with powerful outputs … a natural challenge between 'keep up your Fanfare generation to make sure they stay fed' vs 'do I draft somewhat-weaker Guests which might be Fanfare-neutral or positive?'"

- **Stars (Rare)** tax Fanfare for high-impact acts.
- **Supports (Uncommon)** arrive with plenty of Fanfare, or make it, and do something other than damage.

On the Defect comparison [USER] drew (Lightning, Frost, Glass, Dark, Plasma), each guest has a different job, not a different element on the same hit:

| Guest | Kind | Arrives with | Act (end of your turn) | Pays by | Defect's cousin |
|---|---|---|---|---|---|
| **Neuvillette** (Hydro) | Star | 6 | Pay 3 of his Fanfare: deal 8 [gold]Hydro[/gold] damage to ALL enemies. | himself; he burns out | Glass |
| **Clorinde** (Electro) | Star | 4 | Take 1 Fanfare from each other performer: deal 8 [gold]Electro[/gold] damage to a random enemy. | the rest of the cast | Lightning, taxed |
| **Navia** (Geo) | Star | 4 | Deal [gold]Geo[/gold] damage to a random enemy equal to her Fanfare. | nothing; she wants feeding, and behind the front she fades | Dark |
| **Chevreuse** (Pyro) | Support | 4 | [gold]Spend[/gold] 2: next turn, gain 1 [gold]Energy[/gold]. | the back performer | Plasma |
| **Wriothesley** (Cryo) | Support | 8 | Deal [gold]Cryo[/gold] damage to a random enemy equal to twice the Fanfare he lost since his last act. | nothing; he wants the front | none: retaliation |
| **Sigewinne** (Hydro) | Support | 8 | Give 3 of her Fanfare to the performer behind her, or to your front performer if she is at the back. | herself | Frost, for the shield |
| **Charlotte** (Cryo) | Support | 4 | Each other performer gains 1 Fanfare. | free | Frost, spread thin |
| **Lynette** (Anemo) | Support | 8 | Swirl a random enemy: its aura spreads to ALL enemies. | free | none: a reaction enabler |

- **Navia's fade tension.** Her damage grows with her bar, and behind the front the fade caps her near 5. So she wants to be the shield, or to be fed every turn.
- **Wriothesley and Sigewinne answer the Necrobinder problem as a pair.** GPT: "Wriothesley makes taking a hit productive … Sigewinne moves existing Fanfare into the shield." Wriothesley is Uncommon so ordinary drafts meet him, rather than Rare as in draft 1.
- **Lynette** is [USER]'s example of a guest who "arrives with extra Fanfare on deck".

## The supporting pool: where the depth lives

[USER]: "we need to make sure that the supporting pool has enough depth that the overall effect is not just 'do 5 damage of x element.'"

About 30 cards, in seven families. This batch names the families; their cards follow the seat round on the guests.

1. **Arranging the stage.** Swap two seats, bring a guest forward, send the shield back. Which seat a guest stands in now decides who pays, who fades and who is hit.
2. **Feeding.** Refills that name a guest, commons that leave a net gain of Fanfare, "each guest gains".
3. **Bending the fade.** "This turn, nothing fades." "Fanfare that fades goes to your front performer."
4. **Cashing out.** Expend cards that cash any seat, not only the back. A card that calls a guest's Bow without it leaving.
5. **Encores, now priced.** Bis!, Tutti! and Full House: with rule 4 a repeat is a tempo decision, not free damage.
6. **Hydro and reactions.** Furina's own Hydro cards and the payoffs that read an aura (Crashing Waves).
7. **Furina's side paths,** found when drawn into:
   - **the Spend deck:** attacks that grow with what they Spend;
   - **the Solo:** no one on stage, grown from Improvised Number and Between Acts;
   - **Arkhe:** Ousia and Pneuma.

## The LAW question

`LAW.md`, elements: "No character card applies an off-element aura; off-element access comes only from companions or a co-op partner." Seven of the eight guests are off-element for Furina. The amendment would read: "…from companions, a co-op partner, or a guest on Furina's stage, which pays for it with a seat and Fanfare." GPT: "Stage setup can provide a meaningful price … but it changes the role of the Companion pool." That amendment is [USER]'s (pick 5).

## Measuring it

The Stage report (`tools/furina_stage_report.py`, which has the economy columns since #673) adds three measures before the first guest round. GPT: "A healthy-looking bank can coexist with an underfunded shield or a guest that rarely performs."
- how often each guest could not pay for its act;
- how many turns each guest lasted;
- damage that reached Furina, per fight.

The three dials [USER] expects to tune over a few rounds:
- drain: the fade line, and the stars' prices;
- restore: Refill, and the supports' gifts;
- spend: the Spend cards.

## Ruled, 2026-09-25 evening

1. **Titles: "Guest Star: <name>".** [USER]: "'Summon' doesn't sound quite right here - I think 'Guest Star' is better", then: "I did actually mean the card's title (so you can see at a glance if the card is summoning someone or if it's a regular companion card)."
2. **Sigewinne gives to the performer behind her. From the back seat, "behind" wraps to the front.** [USER]: "I'd say 'the one behind her' and if she's in the back then the one 'behind' is the frontmost one. But I think that might make for confusing card text... might need a clearer explanation." The face spells the wrap out instead of leaning on the word: "Give 3 of her Fanfare to the performer behind her, or to your front performer if she is at the back." From the middle she feeds the bank; from the back she feeds the shield. Where she stands is the choice.
3. **No Companion bonus for now.** [USER]: "we can revisit if that becomes an interesting idea later (e.g. grabbing all of the cards related to a specific character to chase some mini-payoff)."
4. **Two guests at once.** [USER]: "Sounds good." Superseded the same evening: no guest cap, one of each guest, and the trio can be cloned (frame rule 2).
5. **Amend LAW so guests carry their elements.** [USER]: "I think amending is fine." The elements clause in `docs/current/LAW.md` is amended in this PR.
6. **Build the eight after the current seat round.** The draft-3 round has run (`review/records/seat-round-2026-09-25c.md`). Its fixes land first, then this batch builds on them.
