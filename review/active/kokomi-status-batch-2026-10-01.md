# Kokomi: the status batch, and saying "or"

Paper, 2026-10-01. Main session design. **Ruled 2026-10-01.** [USER]: "Agreed
on the Plan text change"; "the 7 removals are good"; three cards revised on his
notes (§2), the rest as drafted.

## 1. Why

Both Kokomi seats on the 78-card build died at the act-1 boss
(`review/records/kokomi-pool-round-2026-10-01.md`). Two of the causes were
the same in both runs. The first: status cards (Beckon, Slimed, Dazed)
clogged hands she had no way to clear. The second: the card face makes
the two halves read as both.

[USER]: "On Kokomi, I feel like our current design pretty much dumped discard
and exhaust synergies, which also feels like a mistake. Unlike Furina or
Klee, she doesn't get a ton of free effects per turn that auto-fire, so she
would need to actually deal with these things through pre-prepared Plans or
from cards in-hand." And: "Agreed that we can make very strong Status-related
cards that rely on the one-turn delay for balancing."

**The idea.** Rule 2 resolves a Plan after the next turn's draw. A Plan can
therefore deal with the hand you are about to be dealt, which no card in hand
can do. That is the head start buying something only waiting can buy. The
price is the delay: the Plan is written a turn early, and this turn's
now-line is given up for it.

**The yardstick** is Defect's Compact (Uncommon, 1: "Gain 6 Block. Transform
all Status cards in your Hand into Fuel"; Fuel is 0, "Gain 1 Energy.
Exhaust.", 2 upgraded). [USER]: it is "extremely strong against specific
matchups or in a status-engine combo" and a brick otherwise. Fuel used to
draw a card as well and was nerfed for it, so this batch keeps Energy and
draw on separate cards.

## 2. The cards (7 in, 7 out; the pool stays 78 at 21 / 36 / 21)

| Card | Type, cost, rarity | Text |
|---|---|---|
| Kelp Wall | Skill, 1, C | Draw 1 card. Plan: Gain 7 [10] Block, plus 3 for each status or curse in your hand. |
| Tidecleanse | Skill, 0, C | Apply 1 Weak. Plan: Exhaust up to 2 [3] statuses or curses in your hand. |
| Sea Glass Harvest | Skill, 1, U | Gain 6 [7] Block. Plan: Transform every status and curse in your hand into Sea Glass [Sea Glass+]. |
| Turning Tide | Skill, 0, U | Draw 1 card. Plan: Discard any number of cards, then draw that many. |
| Flotsam Surge | Attack, 1, U | Deal 13 [17] damage to ALL enemies. Shuffle 2 Dazed into your draw pile. |
| Abyssal Salvage | Power, 1, U | Whenever a status or curse is exhausted, the Casket gains 1 [and you gain 2 Block]. |
| Coral Sanctuary | Power, 1, R | You can play your statuses and curses on the Bake-Kurage for 0. When it carries one out, exhaust it and draw 1 card [and gain 3 Block]. |

**Sea Glass** (token): 0, "Gain 1 [2] Energy. Exhaust."

- **Sea Glass Harvest is Compact on the next hand, curses included.** Played
  now it is only 6 Block, so it is weaker than Compact in the hand you hold
  and stronger in the one you draw.
- **Turning Tide** brings back discard as a mulligan of the coming hand: dud
  draws go, fresh ones come.
- **Flotsam Surge is the self-status engine.** Its damage is well above rate
  for a 1-cost AoE (a Common's going rate is 5 to 6), and it pays in Dazed.
  The Plans above turn the Dazed into Block, Energy and Casket.
- **Abyssal Salvage** feeds the Casket from exhausted statuses, so enemies'
  junk and Flotsam's Dazed both count. It also feeds her existing exhaust
  readers (Moon's Reflection, What the Tokoyo Returns).
- **Coral Sanctuary** is the Rare engine, and it bends a rule: a status
  becomes a 0-cost Plan. The junk sits in this hand and turns into a fresh
  card in the next one, so the delay is the price. It draws and gives no
  Energy (the Fuel lesson), and it has no cap: the statuses you hold are the
  limit. [USER] on the first draft ("exhaust every status ... gain 1 Energy
  for each, up to 2"): "reads too strong (basically - always have no statuses
  and possibly extra energy, and I dislike capping cards anyway)".
- **Revised on [USER]'s notes.** Kelp Wall: "too situational ... if picked
  early, it's probably a brick", so its Plan now carries a flat 7 [10] Block
  and statuses add 3 each. Tidecleanse: "needs a power lift (make it 0
  cost?) - the cost is you drew a card that's not doing much this turn", so
  it now costs 0.

**Readings, so the builder does not choose:**
- "In your hand" on a Plan means the hand just drawn, before you act. Plans
  resolve in the order written, so a card drawn by one Plan is seen by the
  next.
- Dazed counts as a status while it is in hand.
- Coral Sanctuary: a status played this way is a Plan with no lines, written
  in order like any other. Unplayable statuses (Dazed, Wound) become
  playable only onto the Bake-Kurage. A curse played this way is exhausted
  for the rest of the combat, not removed from the deck.
- Sea Glass is a token and never enters the pool.

**Out** (from the census, 600 seeds and five pilots, plus the seat records;
cards the pilot cannot play were not cut on its numbers):

| Card | Rarity | Why |
|---|---|---|
| Rally | C | Picked from 7% of offers; a Weak plus a companion discount |
| Pearl Diver | C | Seat: "too small to matter"; one of four draw cards |
| Battle Plan | U | Picked from 5% of offers, played 0.10 a fight |
| Feigned Retreat | U | Seat: the bonus "almost never held"; played 0.09 a fight |
| Moon Signal | U | Duplicates Kurage Swarm (both trickle the Casket) |
| Chain of Command | U | Played 0.05 a fight |
| All Streams Flow to the Sea | R | Reworked twice, played 0.04 a fight; Spring Tide now carries out the whole queue |

## 3. The face says "or" (pick 2)

Both seats planned a card expecting its now-line too. Rule 2's layout prints
the Plan line under the now-line with nothing between them. The keyword
becomes **"Or plan:"** (and **"Or dusk plan:"**) on every card, the starter's
Kurage's Oath and Slack Water included, and the Plan tip begins "Instead of
the line above". This changes starter text, so it is your pick.

## 4. Not in this batch

- The Casket's one cash-out (Open the Casket exhausts). Watch it through
  this batch, since Abyssal Salvage makes the count grow faster.
- Plans that read next turn's intents. Tide Wall and Flank already do. More
  intent-reading Plans can follow if this batch confirms that reading ahead
  is what makes the delay pay.

## 5. The sim, before the build

Run the census wrapper over the new pool. Expect the stock pilot to be unable
to read Plans that look at the next hand: mark those cards unread, as was
done for Coral Tithe, and do not tune the pilot to flatter them. The seats
decide.

## Picks (ruled)

1. **The seven cards in, as revised, and the seven out (§2).** Ruled.
2. **"Or plan:" on every Plan card, the starter included (§3).** Ruled:
   "Agreed on the Plan text change."
