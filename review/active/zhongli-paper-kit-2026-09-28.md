# Zhongli: the God of Contracts (paper kit)

**Ask ([USER], 2026-09-28):** paper kits for Nahida, Zhongli and Varka that
assume the element changes, "what each of these characters would do with each
element and what core changes to that element would be required". On Zhongli:
"The Zhongli debt angle ... does sound interesting as long as we can avoid
breaking the game in the process." `LAW.md` §Roster already holds "Zhongli
holds slot 4 (countersigned, unscheduled)".

**Stage:** Paper. A concept, not yet a brief. Card numbers are placeholders
for the sim.

## 1. The promise

Everything has a price, and Zhongli always pays, eventually. You can afford
any turn you need; the bill arrives when the fight ends.

## 2. His element: Geo, the quiet one

Geo leaves no aura. Under the element review
(`review/ruled/element-home-review-2026-09-28.md`), a Geo hit on a fresh aura
**crystallizes** it: Block, and the aura stays, spent for triggers.

- **Solo:** his Geo is incidental, the way Klee's Pyro is. His kit does not
  need a reaction to work, so he needs **no starter companion** (the element
  review's pick 3 asks this per character).
- **In co-op:** he harvests his partner's auras for Block and never takes them
  away. That is Genshin's Zhongli: the support who fits any team.
- **Element changes he needs:** only the review's shared rule and change B.
  Nothing new.

## 3. The signature: the Tab

Some of his cards have a **Mora price** printed beside, or instead of, an
Energy cost. Mora is your run's gold.

- **On the Tab:** when you cannot pay, the price goes on the **Tab**. The Tab
  has a **credit limit**, placeholder 40 in act 1, 80 in act 2, 120 in act 3.
  At the limit, Mora-priced cards cannot be played.
- **Settling the bill:** after a fight's rewards, the Tab is paid from your
  gold. What you cannot pay becomes **Unpaid Invoices**: one curse card per
  20 owed, Unplayable. An Invoice is removed by paying it off at a merchant.
- **The tension:** spend now or shop later. Gold spent in fights is gold not
  spent on removals, cards and relics. A Zhongli who never shops wins fights,
  and a frugal one buys power. None of our three kits touches gold, so this is
  new ground.

**Guardrails against breaking the game.** These are rules of the kit, not
tuning:
1. **One source of in-combat gold:** Contracts (§4), each paying a fixed sum
   at most once per fight.
2. **The Tab never outlives a fight** except as Invoices.
3. **Prices are pegged** to what the base game charges for gold. The sim sets
   the exchange rate, placeholder 1 Energy ≈ 20 Mora.
4. **An audit before the build** of every base-game gold source (events,
   relics, potions) for what it becomes in his hands.

## 4. Core verbs

- **Put it on the Tab.** Cards that trade Mora for Energy, draw or Block.
- **Sign a Contract.** A Contract card sets a term for this fight, with a fixed
  reward and a breach penalty. Example: *Contract of Stone: take no unblocked
  damage this turn. Kept: gain 25 Mora. Broken: add 25 to the Tab.* The line
  "those who break a contract shall face the wrath of the rock" is the flavour.
- **Raise the Stele.** The Stone Stele is a Power: at the end of each turn it
  deals 3 Geo to every enemy. Solo, that is plain damage to all. In co-op,
  every fresh aura on the board crystallizes into his Block.

## 5. The three archetypes

1. **On the Tab (default).** Mora-priced cards as extra Energy: big turns now,
   fewer shops later. Signposts: a Common that lowers Mora prices, and an
   Uncommon that pays part of the Tab.
2. **Contracts (the ceiling, draft-gated).** Sign and keep Contracts; their
   Mora funds the Tab. The Rare payoff reads Contracts kept this run, with a
   flat bonus at the start of each fight, never a multiplier.
3. **The Rock.** Jade Shield (Block that lasts through your next turn, like
   Blur), the Stele, and in co-op the partner's auras crystallizing every turn.
   The finisher is **Planet Befall** (Rare): Petrify one enemy so it skips its
   next action, once per fight, Exhaust. That sits inside `LAW.md`'s "hard CC
   is payoff-tier only".

**Bridges:** Contract rewards fund the Tab; Jade Shield keeps you alive while
you keep a no-damage Contract; the Stele's Block pays for defence you would
otherwise buy with Mora.

## 6. Starter (sketch)

Strike ×4, Defend ×4, and two of his own:
- **Dominus Lapidis** (1): gain 5 Block, and raise a Stele that lasts 2 turns.
- **A Price for Everything** (0, Mora 15): draw 2, gain 1 Energy. It teaches
  the Tab in fight one.

**Starting relic: Wangsheng Account.** It opens the Tab with its credit limit.
The subsystem lives on the relic, so it is visible from turn one.

## 7. Intended weakness and failure modes

- **Weakness:** thin damage. His damage is Stele ticks and cards bought on
  credit. Elites that race him punish a deck that saved its gold.
- **Failure mode, the gold loop:** a relic or event turns gold into more gold
  in his hands. Guardrail 4 is the answer.
- **Failure mode, the Tab as free Energy:** if Invoices hurt too little, the
  Tab is a second Energy bar. The first round must read the settlement screen.
- **Failure mode, the shop as a trap:** if Mora prices are too cheap, shopping
  is never right. The sim should show that both halves of the tension win runs.

## 8. What it costs to build

Medium. The Tab needs a counter power, a settlement step on the reward screen,
the Invoice curse and a merchant action, and the sim needs gold in combat.
Geo needs only the element review's change B. No new element work.

## Picks

1. **The bill.** (1) *Invoices: a curse per 20 unpaid, removed by paying at a
   merchant* [default]. (2) Lose max HP per 20 unpaid. (3) Interest: the Tab
   carries into the next fight at +25%.
2. **Contracts.** (1) *An archetype in the pool* [default]. (2) Part of the
   starter: every fight offers one Contract. (3) Leave them out.
3. **Petrify.** (1) *One Rare, once per fight, Exhaust* [default]. (2) None.
