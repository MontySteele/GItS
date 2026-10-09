# Furina Drain-line round, with an Ironclad control, 2026-10-09

**What ran.**
- **Build 0.2.4662+next** (#996, staged from `klee-next`):
  - The Drain line sits at ¾ of the HP she entered the fight with. A Drain may go past it.
  - HP drained past the line is lost for good unless it is repaid. Repay returns that part first.
  - Most Repay cards pay a card-by-card payout for any HP they could not Repay. Soothing Waters, Pneuma Refrain and the Repay-reading cards have none.
  - Endless Waltz is cut, so the pool is 74.
- **[USER]'s ruling:** "Let's try it. It feels like we're making a mechanics change to accomodate the agents' poor play, but we can see how changing it looks in practice first", then "Yes - let's test it with a seat".
- **Seats:** ascension 0, Sonnet 5.5 seats, full runs. Lane 1's first seat stopped at the end of act 1, so a second seat finished the run. The seeds are the ones from the pool-75 round (`furina-pool75-round-2026-10-09.md`), so each row compares directly.

| Run | Seed | This build | Pool-75 round (½ line) |
|---|---|---|---|
| Furina | JF391WG2NN0X | Died on floor 24 to the act-2 elite Decimillipede | Died on floor 24 to Decimillipede |
| Furina | WDETA8RRGH98 | Died on floor 42 to the act-3 Owl Magistrate, after both act bosses and four elites | **Won** |
| Ironclad control | PPW4N6WX70LS | Died on floor 44 to the act-3 three-Knight elite | Died to the Queen on floor 48 |

**Verdict.** The new line did not help on these seeds:
- **One run went the same way:** the same floor and the same elite as before.
- **One run went backwards:** a win became an act-3 death. Lane 2's seat finished the act-2 elite at 5/78 HP, and HP drained past the line did not come back after the fight.
- **The control also died four floors sooner,** so part of the drop is seat variance. Two runs cannot separate the rule from the seat.

What the round does show is how the rule reads to a player:
- The Drain lock is gone. No seat reported a refused Drain.
- Seats now weigh real HP before draining past the line. Lane 1 skipped a Drain "because HP 31 was under my Drain line of 41". That is the intended choice.
- Lane 2 drained past it and paid in HP that did not come back after the fight.

## What played well

- **The Drain choosers became real decisions:** HP for damage, Block or Energy, "at a stated HP line" (lane 2).
- **The Fanfare cash-out carried both runs.** The standouts:
  - Bravura+ for exactly 122 into The Insatiable.
  - Rising Applause for 76 into a Vulnerable Vantom.
  - Tidal Flourish's Spend 6 as an exact kill.
- **Guests keyed on damage were the engine:**
  - Lyney's Pyro fed Vaporize.
  - Freminet summoned before The Deluge, so that one Drain also paid Block.
  - Critics' Darling with Salon's Tab took the Strangler from 54 to 3.
- **No loops.** The loop probe found none after the Soothing Waters fix.

## What did not

- **The payout is invisible.**
  - Fountain of Lucine was both runs' NEVER AGAIN: "Repays only what is drained and did nothing when I wasn't."
  - Its card does promise "Gain 1 Block for any HP it could not Repay". But its in-fight preview line prints only "(Repays 0)", and the seats read that line and not the text.
  - The same preview sits on every Repay card with a payout.
- **The curtain-call wording misleads.** "Drained HP returns after combat" read as a contradiction when 5/78 HP stayed at 5 (lane 2). Only the "past your line is lost" clause explained it.
- **Lyney's act drains past the line on its own.** His act is "Drain 2" at the end of every turn. Once Furina is below the line, that costs real HP every turn with no choice. Lane 1 lost 40 HP across one fight partly to it and blamed his line, which in fact helps.
- **Block is still short.** Both deaths came with no Block in hand:
  - Lane 1: 24 incoming, so the seat took a potion gamble.
  - Lane 2: a 4-card hand at 21 HP.
- **Smaller points:**
  - Grand Absolution's number is tiny unless a lot is drained.
  - Critics' Darling's damage does not show in the play log.
  - Hydro Lance previewed 18 and dealt 14 after All In. The preview is live, so the seat most likely read it before All In. This needs one check by hand.

## What to change (Claude ships these without a pick)

1. **Every Repay preview names its payout** when the Repay would return less than its full amount, for example "(Repays 0, +3 Block)".
2. **A guest act's Drain stops at the line.** A guest acts with no choice from the player, so it should never cost real HP. The player's own Drains keep the new rule.
3. **The curtain-call text reads "Drained HP above your line returns after combat."**
4. **Critics' Darling's damage gets a play-log line.**

## Picks

**Drain-line round, pick 1: the line. Ruled 2026-10-09.**
The line is the HP she entered the fight with, minus ¼ of her max HP (rounded down), so 50/80 gives a line of 30. This is not one of the listed options; it came from [USER]'s question about how the line works. Every fight then gives the same room to Drain safely, whatever her HP.
In [USER]'s words: "Yeah, let's build it that way. That also rewards max HP stacking, which seems fair on a character designed for it, and punishes some event choices which cost max HP that are usually auto-picks."
The rerun follows the build: the same three seeds plus two fresh Furina seeds.

**Drain-line round, pick 2: Block.** Should Furina's pool get more Block, or is the shortfall the seats skipping it because Fanfare pays for hits?
- (a) **Default:** no change yet. Decide on the rerun, with the base five's Block counts beside hers (a census first).
- (b) Add Block now.
