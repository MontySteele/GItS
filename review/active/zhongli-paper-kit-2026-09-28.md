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
- **The tension:** spend now or shop later. Gold spent in fights is gold not
  spent on removals, cards and relics. A Zhongli who never shops wins fights,
  and a frugal one buys power. None of our three kits touches gold, so this is
  new ground.

**The rules that stop farming.** [USER]'s worry was that gold, like HP,
carries between fights, so "farm a fight for money" could become the best
play. Two rules answer it, and GPT's second audit (2026-09-28) showed that the
first alone is not enough:
1. **Zhongli never gains gold in a fight.** Nothing in his kit adds gold
   during combat. The only inflow is the base game's own rewards.
2. **Nothing he does in a fight lowers what he owes at settlement.** The
   first revision let a kept Contract clear the Tab. Then keeping the last
   enemy alive to fulfil one more Contract saved real gold at settlement: no
   gold created, but a profit from stalling. So a kept Contract now **raises
   the credit limit for the rest of this fight** instead. It lets you borrow
   more now and never forgives debt, so prolonging a fight only ever raises
   the bill.

Under both rules, a fight's net gold is between minus the Tab and zero, and it
is lowest when the fight runs long. Entering a fight broke gains nothing
either. Debt is never forgiven, so borrowing only moves the payment to
settlement, and a shortfall there becomes an Invoice. Being broke is never
better than paying up front.

**The bill, step by step** (these answer GPT's audit of 2026-09-28):
1. **When the fight ends,** after its rewards, the Tab is paid from your gold,
   down to 0.
2. **Anything left becomes one Unpaid Invoice** carrying its exact amount. It
   is a curse card, Unplayable. A shortfall of 13 is an Invoice for 13: no
   rounding in either direction.
3. **An Invoice leaves only by being paid,** at a merchant, for its amount.
   Card removal skips it and curse prevention does not stop it, the way the
   base game's unremovable curses work.
4. **Invoices count against the credit limit.** An insolvent Zhongli cannot
   borrow again until he pays.
5. **In the last fight** debt is nearly free, because there is no later shop
   and no later deck. The credit limit is the only bound there. That is
   accepted: a last-fight splurge is capped, like a held potion.

**Guardrails, as rules of the kit and not tuning:**
1. **No gold enters during combat** (above).
2. **Prices are pegged** to what the base game charges for gold. The sim sets
   the exchange rate, placeholder 1 Energy ≈ 20 Mora.
3. **An audit before the build** of every base-game gold source and gold rule
   (events, relics, potions, the merchant) for what it becomes in his hands.

## 4. Core verbs

- **Put it on the Tab.** Cards that trade Mora for Energy, draw or Block.
- **Sign a Contract.** A Contract card pays well now and sets a term. Keep the
  term and your credit limit rises for the rest of the fight. Break it and you
  take **Statuses**. Example: *Contract of Stone (1): gain 12 Block. Term:
  take no unblocked damage this turn. Kept: +20 credit this fight. Broken:
  shuffle 2 Wounds into your draw pile.*
  - **Each Contract card pays out at most once per fight.** A copy is its own
    card and pays once too.
  - **Breaking with Statuses** is [USER]'s "status merchant" idea (like the
    Defect's backup plan), used as the penalty channel.
  - **A Contract against a harmless enemy is an easy keep, and that is fine:**
    extra credit is only worth something while the fight is still going.
  - **The flavour** is the line "those who break a contract shall face the
    wrath of the rock".
- **Raise the Stele.** The Stone Stele is a Power: at the end of each turn it
  deals 3 Geo to every enemy. Solo, that is plain damage to all. In co-op,
  every fresh aura on the board crystallizes into his Block.

## 5. The three archetypes

1. **On the Tab (default).** Mora-priced cards as extra Energy: big turns now,
   fewer shops later. Signposts: a Common that lowers Mora prices, and an
   Uncommon that pays part of the Tab.
2. **Contracts (the ceiling, draft-gated).** Sign and keep Contracts; keeping
   them extends your credit, so defence this turn funds a bigger turn next
   turn. The Rare payoff reads the **Contract cards in your deck** (for
   example, 3 Block per Contract at the start of each fight). It never reads
   Contracts kept, because a run-long "kept" counter could be farmed on easy
   enemies (GPT's second audit).
3. **The Rock.** Jade Shield (Block that lasts through your next turn, like
   Blur), the Stele, and in co-op the partner's auras crystallizing every turn.
   The finisher is **Planet Befall** (Rare): Petrify one enemy so it skips its
   next action, once per fight, Exhaust. That sits inside `LAW.md`'s "hard CC
   is payoff-tier only".

**Bridges:** kept Contracts extend your credit; Jade Shield keeps you alive while
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
  in his hands. Guardrail 3 is the answer. If the audit cannot close it, the
  fallback is [USER]'s: Zhongli as a pure status merchant, with no gold at all.
- **Failure mode, the Tab as free Energy:** if Invoices hurt too little, the
  Tab is a second Energy bar. The first round must read the settlement screen.
- **Failure mode, the shop as a trap:** if Mora prices are too cheap, shopping
  is never right. The sim should show that both halves of the tension win runs.

## 8. What it costs to build

Medium. The Tab needs a counter power, a settlement step on the reward screen,
the Invoice curse and a merchant action, and the sim needs gold in combat.
Geo needs only the element review's change B. No new element work.

## Picks

1. **The bill.** (1) *One Invoice per fight for the exact amount, removed only
   by paying it, and counted against the credit limit* [default]. (2) Lose max
   HP instead of taking an Invoice. (3) Interest: the Tab carries into the
   next fight at +25%.
2. **Contracts.** (1) *Draftable: keeping one raises this fight's credit,
   breaking one shuffles Statuses into your deck, and each card pays at most
   once per fight* [default]. (2) Part of the starter: every
   fight offers one. (3) Leave them out.
3. **Petrify.** (1) *One Rare, once per fight, Exhaust* [default]. (2) None.
