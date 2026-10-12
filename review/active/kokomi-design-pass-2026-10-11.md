# Kokomi: what she does besides writing Plans (2026-10-11)

**Why.** From [USER]'s run (`review/records/kokomi-user-run-2026-10-11.md`): "I won the Kokomi run, but honestly... it felt clunky. Not difficult, but clunky. The early game was slow and the late game was Plan Spam." After the first diagnosis:

> "lots of small plans" vs "one really big plan" is not actually compelling as an archetype split, so the runs devolve into one note builds.
>
> I think this calls for a deeper design pass first to figure out what Kokomi should actually do.
>
> The Plan mechanic is fine; I just don't think it can carry a character by itself with no other archetype options.

This paper sets the direction only. The card-by-card list follows the ruling, as its own paper.

**Source.** A census of her 78-card pool on `main` (session scratchpad, `kokomi-archetype-census.md`): every card tagged from its text, with offers and takes from `tools/offer_report.py` over five lanes (2026-10-08 to 2026-10-11; the pool changed during the window) and plays from fight telemetry.

## 1. What the pool does today

**Plans are the whole pool.** 34 of 78 cards carry a Plan line, 24 read a Plan count, 15 cost 0, and 20 draw or give Energy. Only 4 cards carry none of those tags.

**The other archetypes exist on paper, but nobody drafts them.**

| Theme | Cards that build it | Cards that pay it off | Payoffs taken |
|---|---|---|---|
| Plans and the Casket | 34 | 24 | Flood Tide 76%, Grand Design 78%, Masterstroke 75%, Surging Shoal 82% |
| Block | 15 (11 are Plans) | 5: 1 Common, 1 Uncommon, 3 Rare | 4 of 59 offers (7%) |
| Weak and Vulnerable | 11 (8 are Plans) | 6 | 16%; Ceremonial Garment, Sea's Reproach, At Water's Edge never taken |
| Statuses | 2 | 4 | 14% |

Watatsumi's Grace, Tidal Rebuke and Tidal Riposte have also never been taken. Coral Crash was taken 2 of 30 times, and Drowning Pressure 1 of 20.

## 2. Why every run is the same deck

1. **The Casket feeds every deck.** Every Plan adds a point and every point is Strength, so a Block deck and a debuff deck both end up as Strength decks. Their own payoffs never beat that.
2. **The other payoffs are Rare only.** Block has one Common and one Uncommon payoff; the debuff payoffs are mostly Rare Powers. There is nothing in acts 1 and 2 to start those decks with.
3. **Too many things to count.** Her cards read eight different Plan numbers: the Casket; Plans carried out this turn; Plans waiting; Plans written this turn; Energy paid for waiting Plans; "only" or "exactly one" Plan; the first Plan, or the Plan after this one; 0-cost Plans written. The base characters each track one or two.
4. **The engine is free.** 15 cards cost 0, and Kurage Swarm, Kurage School and Shoal Call multiply the 0-cost Plans. A late turn is clicking Plans.
5. **The start is slow.** A Plan pays next turn, and an act-1 fight lasts about 3 turns. The seats lost a median 12.5% of max HP in each act-1 normal fight.

## 3. The proposal: Plans are her verb, and the archetypes split on what they buy

Like the Watcher's Stances, Plans are what every Kokomi deck does. **What the Plans buy** is the draft. Each archetype has Commons that start it, an Uncommon payoff and a Rare finisher, and each pays off from its own number, never from a Plan count:

- **The Tactician: Plans that hit.** Attack Plans fill the Casket, which becomes Strength. This is today's deck, narrowed: Grand Design, Flood Tide, Masterstroke and Surging Shoal stay here.
- **The Warden: Plans that guard.** Block sized to the next attack (Tide Wall), Block kept between turns (Watatsumi's Grace) and Block turned into damage (Coral Crash, Tidal Rebuke, Tidal Riposte). It pays off from the Block she holds. The four Dusk Plans live here, because Dusk is when Block matters.
- **The Undertow: Plans that weaken.** Weak and Vulnerable land before the swing, and the payoffs count debuffs (Drowning Pressure, Ceremonial Garment, Sea's Reproach). This is the strategist reading the enemy, as GPT's review put it.
- **Small component: the flotsam.** Statuses she adds and turns into Sea Glass, as now.

What changes for all three:
- **The Casket counts only Plans that deal damage** (pick 2). A Warden or Undertow deck no longer gets Strength for free. It needs its own payoffs, which this pass moves down to Common and Uncommon.
- **One count per archetype.** Cards read the Casket, the Plans waiting, or their own archetype's number (Block, debuffs). The other counters go, including Sango Isshin's new per-combat count, which moves to the Casket.
- **The engine is trimmed.** Kurage Swarm and Kurage School go, and the 0-cost Plan Commons are cut down so that writing a Plan has a price. Draw moves toward a base character's density.
- **A faster start.** Each archetype's Commons get a now-line that pays this turn, so act 1 is not a turn behind.

The pool stays at 78 and the starter is untouched. Kurage's Oath (Block now, or damage to ALL) already belongs to both the Warden and the Tactician, and Slack Water to the Undertow.

## 4. The alternative: the Bake-Kurage as an engine

A second engine beside Plans: the jellyfish grows and acts on its own (a Hydro hit each turn, sized by cards that feed it), closer to her Genshin kit. Her brief's rule 4 ("Nothing happens by itself. No bank, no pulse") ruled this out in an earlier draft, so it needs your pick. It would also sit close to Furina's guests and the Necrobinder's Osty.

## 5. Next

After the ruling: a card paper (what each of the 78 cards becomes, kept, moved or cut, with take rates), then the build, a seat round and your run.

## For [USER]

1. **Her direction.**
   - **(a) Default:** Plans stay her verb, and three archetypes split on what the Plans buy (Tactician, Warden, Undertow), with the flotsam as a small component.
   - (b) The jellyfish as a second engine beside Plans (reopens rule 4).
   - (c) Something else (say what).
2. **The Casket.**
   - **(a) Default:** it counts only Plans that deal damage.
   - (b) It counts every Plan, and the Warden and Undertow payoffs are made strong enough to beat Strength.
3. **Dusk.**
   - **(a) Default:** Dusk stays only on Warden cards, where its end-of-turn timing changes the Block.
   - (b) Retire Dusk; those cards become ordinary Block cards.
