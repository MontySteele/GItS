Status: BUILDING (Prototype pass; ruled 2026-09-27)

# Kokomi core pass, 2026-09-27

This is pick 1a of `review/active/kokomi-design-review-2026-09-27.md`, which
was ruled at its defaults. [USER]: "Also - agreed on Kokomi's defaults." It
changes eight cards and no rule. Her starter, Kurage's Oath included, is not
touched.

## Goal

On a turn with no incoming attack, playing a Plan card now should be worth
something, so writing it is not automatic.

- Before this pass, 8 of her 22 pool Plan cards had Block as their only
  now-half.
- After it, 3 do: Tide Wall, Coral Bulwark, and The Moon, A Ship. Their whole
  job is defence.
- Two payoffs now reward something other than "a Plan was carried out":
  - one rewards an empty queue;
  - one rewards playing a Plan card's now-line.

## The eight cards

| Card | Was | Now |
|---|---|---|
| Ambush (C, 1) | Gain 5 Block. Plan: Deal 12 damage. | Apply 2 Vulnerable. Plan: Deal 12 damage. (Upgrade: Plan 15.) |
| Cleansing Wave (U, 1) | Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block. | Remove one of your debuffs. Draw 1 card. Plan: Gain 10 Block. (Upgrade: Plan 13.) |
| Ripple (C, 0) | Gain 2 Block. Plan: Gain 1 Energy and 4 Block. | Draw 1 card. Plan: Gain 1 Energy. (Upgrade: draw 2.) |
| Feigned Retreat (C, 1) | Gain 6 Block. Plan: Deal 9, or 14 if you lost no HP since playing this. | Draw 2 cards, then discard 1. Plan unchanged. (Upgrade: Plan 12 / 18.) |
| Second Wave (C, 1) | Gain 4 Block. Plan: the Plan after this one is carried out twice. | Deal 5 damage. Plan unchanged. (Upgrade: 7 damage.) |
| Chain of Command (U, 1) | 3 per Companion now; Plan: 6 per Companion. | 3 per Companion now. Plan: Next turn, the first Companion card you play costs 0. (Upgrade: 4 per Companion.) |
| Song of Pearls (U, 1, Power) | Once per turn, when a Plan is carried out, gain 3 Block. | At the start of your turn, if no Plan waits, the Bake-Kurage deals 4 damage to ALL enemies. (Upgrade: 6.) |
| Treatise (U, 1, Power) | Once per turn, when a Plan is carried out, draw 1. | Once per turn, when you play a card with a Plan line normally, draw 1 card. (Upgrade: Innate.) |

Why each card changed:

- **Ambush, Ripple, Feigned Retreat, Second Wave.** Each now-half now does
  something on a quiet turn:
  - Ambush: Vulnerable, which multiplies this turn's Attacks and also fires
    the Casket;
  - Ripple and Feigned Retreat: cards;
  - Second Wave: damage.

  Their Plan halves are kept, so each card now asks "develop now, or buy
  tomorrow".
- **Cleansing Wave, Ripple, Chain of Command.** These were the three breaches
  of the halves rule: the same effect at two sizes. Each now has two different
  jobs. Chain of Command's Plan buys tempo for tomorrow's Companion. Its full
  rebuild belongs to the "plan the reaction" batch (review pick 2).
- **Song of Pearls.** This is the empty-queue payoff. A turn with nothing
  written pays out tomorrow, as the Bake-Kurage's own strike: the jellyfish
  hitting on its own, as it does in Genshin.
  - Her damaging cards apply Hydro, so this strike does too (R276 pick 2).
  - It is a Power you played, so rule 4 ("nothing happens by itself")
    stands.
- **Treatise.** It pays for playing a Plan card now, the other side of the
  choice. It is once per turn, so it cannot become a draw engine.

## After the build

One short seat of one act (about 150 actions) reads whether quiet turns now
ask a question. Then [USER] plays, since the change is to how her central
rule plays.
