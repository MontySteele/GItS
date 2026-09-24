# Seat round, 2026-09-23: R276 rules and the new batches

Builds: `0.2.3715+proto` (Furina, Kokomi) and `0.2.3719+proto` (Klee, with Sit Tight and Spark Knight
fixed). Five seats, all act 1: a GPT seat and a Claude seat on Furina and Kokomi, and a Claude seat on Klee.
GPT's Klee seat waits for the Codex usage reset; GPT's Kokomi seat stopped at 70 actions on the usage limit.
Raw records are in `review/qa/blindplay/` (gitignored): `20260924-000448`, `furina-stage-r4-opus`,
`20260924-002456`, `kokomi-r276-opus`, `klee-r276-opus`.

Caveats:
- Claude's Furina seat ran uncapped (about 279 actions, died to the act-1 boss on floor 17), because the lane
  was embarked without `--max-actions`. Only its first four fights are inside the budget.
- Claude's seats received CLAUDE.md and the memory index in their context, and they declared it.

## Furina, the Stage

**What played well.** Both seats found the kit's decision unprompted: the same Fanfare is the shield and the
ammunition, so spend the back performer or keep it. The seats cited these turns:
- spending exactly the back performer's bar on Curtain Rise for the burst and the Bow, then rebuilding;
- Raise one turn and Bravura the next ("(Deals 33 damage)");
- summon order before Bravura;
- Ousia Surge before Bravura for an exact 56 lethal.

GPT's seat would never draft again: "none".

**What did not.**
- Enemies that hit several times clear the stage, and an empty stage turns Rising Applause, Gala Dinner,
  Hold Your Places' Raise, Bravura and Ousia Surge into blanks (both seats).
- Tutti! was never worth 2 Energy (Claude's NEVER AGAIN).
- Six display contradictions, listed under "What changed".

**What changed (PR #651).**
- A Raise on an empty stage summons a random performer holding that Fanfare.
- Tutti! costs 1, and 0 upgraded.
- Display fixes:
  - Fanfare has one definition under the Stage.
  - The Raise tip says "where the card says, else the back performer".
  - The back-seat text says hits reach it once the seats ahead are empty.
  - Chevalmarin's act log reads "2 to every enemy".
  - The Ousia and Pneuma tips appear only on Arkhe Alignment.

Soloist's Solicitation carries the Strike tag, so Strike Dummy boosts it. It is a starter card and stays
as it is.

## Kokomi, the halves rewrite

**What played well.** Both seats treated "play it now or write it as a Plan" as a real choice on most cards.
The Plan rules made timing matter:
- a Plan's carry-out is not a hit, so it gets past Thorns and Skittish;
- Kokomi's own Weak does not reduce the jellyfish's hits;
- a Plan cannot strip Block the enemy is already standing in.

The seats' best turns:
- leaving a Corpse Slug at 2 HP so the Plan would kill it after its partner;
- turning down a certain two-Plan lethal for the Block line;
- Opening Gambit before Kurage's Oath for a doubled, Vulnerable-boosted hit.

**What did not.**
- Claude's seat said the trade "was always Block this turn against damage next turn".
- GPT's seat wrote Plans automatically on turns its Defends already covered (Ripple "automatic").
- The rewritten cards whose halves do different jobs (Vanguard, Stolen Chapter, Battle Plan) barely came
  up, so GPT's review question is still open: on a safe turn, does a useful now-half compete with another
  Plan?
- Slack Water's Plan half loses to its now-half against one enemy. Slack Water is a starter card and stays.
- Sea-Salt Prayer, which has one half, was "never a decision".
- Hydro auras never mattered in six fights: nothing reacted with them without a companion.

**What changed (PR #649).** Pincer, Stolen Chapter and Battle Plan now say "Next turn, ...". A seat had
skipped Pincer because it could not tell which turn "This turn" meant.

## Klee, the 78-card pool

**What played well.** Every fight was won, the elite included.
- Mines killing enemies before they hit was the clearest payoff.
- The seat found real order puzzles:
  - Pyro, then Rosaria's Cryo, for Melt;
  - Hiding Spot before Ka-pow!, so one Mine strips Artifact and a second applies Vulnerable.
- Explosive Frags made the hold-or-fire question decide fights.

**What did not.**
- **Sparks pile up.** The seat ended fights holding 6, 5 and 6 unspent. It was offered two Spark-cost
  cards in six rewards. The pool has 16 of them in 78 (6 Common, 8 Uncommon, 2 Rare), almost all costing
  1 Spark, while supply grew in R276 (1 to 3 Sparks for every Companion card played).
- Without Frags, hold-or-fire was a wash, because Jumpy Dumpty's Mines make firing now and next turn
  come to about the same.
- Shinobu's Grass Ring clause, "if you lost HP this turn", never pays on her own turn (NEVER AGAIN).
- The Bomb tip, "a second Bomb joins the first", read as one charge.

**What changed (PR #652).** The Bomb tip now reads "a second Bomb stacks beside the first, and a Mine among
them goes off alone".

## Klee, GPT's seat (added 2026-09-24)

Build `0.2.3730+proto`, which has no Companion Sparks. The seat ran on `gpt-6-sol` (`20260924-045324`): 150 actions and
seven fights through the act-1 elite, and it stayed inside the usage window.

**What played well.** "When to detonate" came back in almost every fight, and it had outside pressures:
- enemies gaining Block;
- the Colony's 20-HP-per-turn Shell, which made Bomb timing exact;
- Mines killing enemies in range before they hit.

Barbara's Vaporize Bomb plus Block was its best turn.

**What did not.**
- Hair Trigger was dead in every fight (NEVER AGAIN): nobody spent 1 Energy turning a Bomb into a Mine.
- The opening was the same most fights: Jumpy Dumpty, wait, Ka-pow!.
- Grounded never paid, because it Set off every turn.

**Sparks without the Companion income.** It went both ways: once it held 3 Sparks with nothing to spend them
on, and once it could not pay Bang Bang!+ (1 of 2). Pop! into Bang Bang!+ spent them well. That is closer to
a constraint, as intended.

**What changed.** Hair Trigger now costs 0 and draws a card (2 upgraded).

## The tester's page (PR #650)

Three seats misread intents under Weak, which printed two possible numbers. The game's intent number already
counts Weak and Strength, so the page now prints that one number. Killing hits now log as "killed" instead of
"nothing this page can count".

## Ruled (2026-09-23)

1. **Spark supply.** Companion plays mint no Sparks under the arm. [USER]: "It sounds like we've massively
   increased the Spark generation and it's worth decreasing now to go back to the old levels and then see if
   play is Spark-constrained."
2. **Shinobu, Grass Ring of Sanctification.** a), "agreed on a)": the clause now reads "if you lost HP since
   your last turn".
3. **Kokomi's safe turns.** a), "a) is fine for now".
