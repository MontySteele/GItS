Status: OPEN (two picks, §4)

# Kokomi: why Plan plays itself, and the fix in the cards

Written 2026-09-23 by Claude (Opus 5.5), from the brief (draft 7), your run
(`review/ruled/kokomi-user-run-1-2026-09-07.md`), rounds 24 to 32, R265 to
R268, and a census of the live build (39 draftable cards, 22 of them with a
Plan line, read off the generated C#).

## 1. What is working

Plan is a good mechanic and worth keeping. No base-game character has a
delayed cast. It fits her lore (Watatsumi's strategist, the jellyfish
carrying out her orders), and the Bake-Kurage as an untouchable pet
reads well. The starter's Slack Water is a real fork on turn one: Weak
now against this hit, or Weak on everyone tomorrow. The relic (every debuff
she applies is also a 2 Hydro hit) ties her debuffs to her element, and
the seats liked it.

## 2. Why it plays itself

You said the central loop feels too auto-pilot: on a turn the enemy isn't
attacking, you write every Plan. Pool passes two to five added order
riders, Dusk and queue verbs, and round 32 still found that the best turns
came from enemy rules, not from the queue. I think the cause is visible in
the cards themselves:

**On 12 of the 22 Plan cards in her pool, and on the starter's Kurage's
Oath, the Plan line is the now-line made bigger.** Ambush is 5 now or 12
tomorrow. Stolen Chapter is draw 2 or draw 4. Coral Bulwark is 6 Block, or 8
Block and Weak. Kurage's Oath is 3 to ALL or 7 to ALL. The same holds for
Feint, Riptide, Pincer, Exposed Flank, Vanguard, Feigned Retreat, War
Council, Battle Plan and The Moon, A Ship. When
"later" is the same thing but bigger, the only reason to play now is this
turn's incoming damage. On a safe turn there is no reason at all, so the
right play is always "write everything". The payoff cards then reward
exactly that. Treatise, Song of Pearls, Well Laid, Tide Wall and Feint all
pay per Plan carried out.

Klee does not have this problem, because her "later" is not simply bigger.
Waiting risks the bomb jumping or the enemy dying, and it switches which
of her defences is live. That is what makes waiting a bet for her.

The cards where Kokomi's decisions do happen prove the point. Read the
Field (look at 3 cards now, or 10 Block tomorrow), Slack Water (Weak this
hit, or Weak on everyone tomorrow), Chain of Command, Flank and Opening
Gambit all have halves that do different jobs. Those are the cards the
seats argued about.

## 3. The fix: every Plan card's two halves do different jobs

You ruled in R266 that you would rather fix this through card design than
through a cap, and I agree. The design rule I'd write into the brief:

> **The now-line answers this turn; the Plan line buys something only a
> head start can buy.** The two halves are never the same effect at two
> sizes.

In practice:

- **Now-lines** do what matters this turn: draw or filter, a debuff that
  multiplies this turn's other plays, Block, a kill.
- **Plan lines** do what is worth more for being early: Energy or cards
  for tomorrow, Vulnerable landing before tomorrow's attacks, Block that
  is up before the enemy's *next* action, or a board-reading effect like
  Flank's ("each enemy that intended to attack when you wrote this").

On a safe turn the question then becomes "develop this turn, or buy
tomorrow", and that tradeoff is not free: writing a Plan spends this
turn's card and Energy on tomorrow. On an attack turn, the intent still
prices waiting, as now.

**The pass:** I rewrite those 13 cards to this rule. Kurage's Oath is
included because it is her own card, not a basic.
I also re-aim the five per-Plan payoffs so at least half of them reward
something other than volume, such as a Plan carried out onto a debuffed
enemy, or the first Plan each turn. The pool size stays at 39. Two seats
read it, and because it changes how her central rule plays, you play it
after that.

**Hygiene, without asking** (the Hydro question is pick 2, not hygiene):

- Her Ancient card grants Charge, a resource the prototype turns off, so
  it is a dead pick.
- Old compiled rows include a second card named "Kurage's Oath".
- Stale comments remain.

## 4. Picks

**Pick 1: the fix.**
1. **(default)** The rewrite pass above: every Plan card's halves do
   different jobs, the payoffs are re-aimed, and the rule goes into the
   brief. Two seats, then your run.
2. The same pass, plus one rule: unblocked damage Kokomi takes knocks
   the last-written Plan off the queue. This makes "write everything"
   under a telegraphed attack a real bet. It is a vulnerability, not a
   throughput cap. It is also the most invasive option, and I would try
   the cards first.
3. Pivot: Plan becomes a supporting mechanic and the jellyfish becomes a
   pet that acts every turn, closer to her Genshin kit. I don't recommend
   it. It overlaps Furina's performers, and Plan is the more distinctive
   idea.

**Pick 2: her own damage applies Hydro.** Five of her Skills deal damage
but put no Hydro on the target: Ambush, War Council, Opening Gambit, Chain
of Command, and Kurage's Oath's now-line. Her Attacks do apply it, and
that split is a trap when reading a card.
1. **(default)** Every damaging card of hers applies Hydro, Skills
   included. The base Strike and Defend still apply nothing.
2. Attacks only, as now. The Skills' faces say so.
