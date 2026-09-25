Status: PAPER, open picks at the end. Ruled so far: the guests are Furina's own cards, separate from the Companion pool.

# Furina: the Guest Cast batch (paper, 2026-09-25)

**What this is.** This is the first batch of the Stage's pool expansion. Fontaine characters step onto the Stage as performers.

**Where it comes from.** [USER]: "my vision on Furina is to move away from merely summoning her Hydro summons and allow for character-effect cards to reach the Stage as well … you could play a 'Neuvillette' card and Neuvillette would actually be summoned to the stage, with some stronger effects than the normal minions."

**What it builds on.** It rests on the draft-3 rules (brief `furina-stage-brief-2026-09-08.md`, rules 9 to 12):
- the Bow is the performer's act, once more;
- no act applies Hydro;
- the applause fades.

It waits for the seat round on those rules before it is built.

## How [USER] framed the kit

"Similarly to Defect, the most common thrust of a run might generally revolve around what the Stage is doing, with additional paths for Furina-focused gameplay … if you happen to draw into them."

Guests are the Stage's power path. The Salon trio (Usher, Chevalmarin, Crabaletta) are the Stage's floor.

## The frame: seven rules

1. **A guest card** is a Furina Skill titled with the guest's name alone, such as "Neuvillette". A Companion card's title is a name, a dash, then its own. So the two read apart on sight, and the Companion tip already says so.
2. **Playing it summons the guest to the back-most empty seat,** holding the Fanfare the card prints. On a full stage it is a recast (rule 3): the front performer Bows and leaves, and the guest arrives at the back holding that performer's Fanfare. This recast is where the carry-over ruled this morning pays off. Your shield becomes your star's fuel.
3. **One guest at a time.** A second guest replaces the first. The first Bows and leaves, and the newcomer takes its seat and its Fanfare. The trio fill the other seats.
4. **A guest is a performer in every other way.** Fanfare is its health. It takes hits at the front and fades behind it. It Bows (acts once more) when it leaves. Full House, Ensemble Piece and the rest count it.
5. **Each guest's act says who pays.** [USER]: "We could also let different Guests pay in different ways … a big DPS card only drains themself, one drains a trickle from all members, Healers actually restore the member behind them." There are five ways to pay:

   | Way | Who pays | Guests |
   |---|---|---|
   | Self | the guest's own Fanfare; it burns out | Neuvillette |
   | Bank | an ordinary Spend from the back performer | Navia, Chevreuse |
   | Tithe | 1 from each other performer | Clorinde |
   | Wound | nothing; the act reads the Fanfare it lost to hits | Wriothesley |
   | Gift | it gives its own Fanfare away | Sigewinne, Charlotte |

6. **A guest pays at the end of the turn if it can, and never asks.** Guests act before the fade, so a guest is the natural answer to a fat bank.
7. **Guests bring the elements.** Since draft 3 the trio apply none, so reactions come from guests and from Furina's cards.

## The first seven guests (opening numbers, for seats and the sim)

| Guest | Rarity, cost | Arrives with | Act (end of your turn) | Pays by |
|---|---|---|---|---|
| **Neuvillette** (Hydro) | Rare, 2 | 6 | Pay 3 of his Fanfare: deal 8 [gold]Hydro[/gold] damage to ALL enemies. | Self |
| **Clorinde** (Electro) | Rare, 2 | 4 | Take 1 Fanfare from each other performer. Deal 4 [gold]Electro[/gold] damage to a random enemy for each point taken. | Tithe |
| **Wriothesley** (Cryo) | Rare, 1 | 6 | Deal [gold]Cryo[/gold] damage to a random enemy equal to twice the Fanfare he lost to hits since your last turn. | Wound |
| **Navia** (Geo) | Uncommon, 1 | 4 | Deal 5 [gold]Geo[/gold] damage to a random enemy. [gold]Spend[/gold] 3: deal 14 instead. | Bank |
| **Sigewinne** (Hydro) | Uncommon, 1 | 6 | Give 3 of her Fanfare to your front performer. | Gift |
| **Charlotte** (Cryo) | Uncommon, 1 | 3 | Each other performer gains 1 Fanfare. | Gift, free |
| **Chevreuse** (Pyro) | Uncommon, 1 | 3 | [gold]Spend[/gold] 2: deal 5 [gold]Pyro[/gold] damage to ALL enemies. | Bank |

**What each one is for:**
- **Neuvillette is the burst star.** He arrives at 6: two acts, then his Bow. A recast of a thick front performer gives him more. His rate (8 to every enemy per 3 Fanfare) is above a Spend card's 2 per Fanfare because he pays with his own body.
- **Clorinde drains the cast.** She costs the shield 1 a turn, which its own regain of 1 covers, and the bank 1. She fits a deck that Refills.
- **Wriothesley wants the front.** He turns the Necrobinder problem inside out: the more the shield is hit, the harder he answers. Behind the front he does nothing, so Step Forward and Scene Change decide his turn.
- **Navia is the plain Spend guest.** Her Geo on an aura Crystallizes, which is Block.
- **Sigewinne heals the shield by draining herself.** This is the Fontaine healer's own shape (her bubbles cost her HP). It is also the Block-poor answer the Osty problem needs.
- **Charlotte is the small, free healer.**
- **Chevreuse is the second element for reactions.** Her Pyro with Clorinde's Electro Overloads, and with the Hydro cards it Vaporizes.

**Every guest's Bow is its act, once more.** A self-paying guest spent to exactly 0 therefore acts one last time as it leaves. When its Bow cannot pay, the act does nothing.

## Tuning: three dials, several rounds

[USER] expects "a few rounds of tuning" between how much Fanfare drains, how much is restored and how much is spent. The Stage report (`tools/furina_stage_report.py`) should print these per fight before the first guest round:
- the bank's size at the end of each turn;
- Fanfare lost to the fade;
- Fanfare paid by Spend cards and by guests;
- Fanfare restored.

The dials are:
- the fade line (5);
- each guest's price and arrival number;
- the Refill amount (5).

## Not in this batch

The rest of the expansion toward 78 cards, about 30 Stage-management commons and uncommons, is written after the seats read the guests. Cards that play with the fade, move Fanfare between seats or read a guest are wanted, but only once there is play to fit them to.

## Picks for [USER]

1. **Guest card titles.**
   - (a) *Default:* the bare name ("Neuvillette").
   - (b) A prefix ("Guest Star: Neuvillette").
2. **Where Sigewinne's Fanfare goes.**
   - (a) *Default:* the front performer, the one taking hits.
   - (b) The performer behind her, as you first put it. That refills the bank rather than the shield.
3. **A guest's own Companion cards.** Neuvillette, Navia, Clorinde, Charlotte and Chevreuse already have "Name — ability" Companion cards in the shared pool.
   - (a) *Default:* no interaction in this batch, to keep it readable.
   - (b) A Companion card of the guest on stage gets a bonus, for example "costs 0".
4. **How many guests at once.**
   - (a) *Default:* one.
   - (b) Two, still one per character.
5. **The seven.**
   - (a) *Default:* build these seven as written, after the draft-3 seat round.
   - (b) Change the list, by name.
