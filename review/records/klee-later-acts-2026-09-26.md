# Klee in acts 2 and 3: seat round, 2026-09-26

**Why this round:** [USER] asked for Opus seats "to test the deck at different points (acts 1 / 2 / 3, different deck strategies, etc)": "I think that we've only tested Klee in Act 1". Build 0.2.3841+proto, A0. Six blind Opus seats played; their records are gitignored under `review/qa/seats-2026-09-26/klee-*.md`.
- Two played whole runs from Neow and drafted their own decks.
- Four started from a coordinator-dressed deck: `skip_act`, then `give_card`/`give_relic` grants, per `understudy-seats.md`'s attended drivers. Dressed starts are not comparable to anything (Guardrail-7). They skip act 1's max-HP, relics and potions, so they die earlier than real runs would.

Caveat: the seats are Opus and the kit's author is Claude. The seat rule (R217 C) forbids a seat from the author's model family. [USER] asked for Opus seats this time, so treat these as the user's instrument, not a blind grade.

## How far each got

| Seat | Start and deck | End |
|---|---|---|
| Full run, lane 1 | Neow, drafted a Spark engine (Chained Reactions, Spark Knight, Fireworks Finale) | **Won**: Vantom, Knowledge Demon, Queen |
| Full run, lane 2 | Neow, drafted Cook (one big Bomb; The Big One, Big Badda Boom, Stoke the Fuse) | Beat both act bosses; died act 3 floor 7 to elite Soul Nexus |
| Act 2, lane 1 | dressed Cook (too few Bomb placers: my deck) | Died act 2 floor 15, Entomancer elite |
| Act 2, lane 4 | dressed Mines + Companion | Beat Knowledge Demon; died to Test Subject's third form |
| Act 3, lane 2 | dressed Spray | 6/6 act-3 fights won; lost Aeonglass on turn 7 (172/512) |
| Act 3, lane 3 | dressed React + Mines | Died act 3 floor 8 (took potions over +31 max HP at the Ancient) |

## The third wave (0.2.3868+proto, after the fixes)

Three more full runs from Neow. A fourth was void: its commands crossed lanes. See the caveat below.

| Seat | Plan | End |
|---|---|---|
| Wave 3, lane 1 | Sparks pay for cards (Dig In, Bottomless Bag, Blazing Delight) | Died to the act-1 boss, Ceremonial Beast (66/252 left) |
| Wave 3, lane 2 | Stacked Bombs, a retained Ka-pow!, Blast Shield on Sparks; Spark Knight and Chained Reactions in act 2 | **Won**: beat Aeonglass at 13 HP |
| Wave 3, lane 1 (second) | Many small Bombs into Sparks into Spark Knight; the Blast Shield and Party Poppers loop | Beat The Kin and Kaiser Crab; died to Test Subject's second form |

In total: five whole runs, two wins, two deaths at the act-3 boss or an elite, one death at the act-1 boss.

**Caveat on every parallel round today:** the seats shared one scratchpad. On lane 2 a wrapper script with the same name drove the wrong lane (its seat stopped and reported "another driver"). Earlier seats also wrote same-named wrappers, so any earlier record may carry a stray command. Each seat now gets its own folder and names its lane on every command, and the seat brief says so (#701).

## What played well

- **Cook and Spray both scale into act 3.** Planned two-turn setups hit 100 to 166 in one turn; bombs held three turns grew 58 to 203 and killed an act-2 boss. Every seat named a turn it wanted to repeat, and every one was a setup paying off.
- **Order is the real decision.** When to Set off versus let Bombs grow; Once More! choosing which Set off card comes back; Careful Arrangement moving a stunned enemy's bomb onto the one about to swing.
- **Spark engines are real** once a payoff is drafted: Chained Reactions + Spark Knight + Tinder Toss ("killed four capped Exoskeletons"), Fireworks Finale, Stoke the Fuse.

## What did not

1. **Defence runs out in act 3.** Both deaths in real runs came from a single big hit with no Block in hand. The full-run Cook seat said: "the drafts offered almost no block after act 1".
2. **Sparks pile up with nothing to spend them on.** Four seats ended fights holding 6 to 20 unspent. Pounding Surprise pays a Spark per Bomb, and only a few cards cost them.
3. **The React loop never came online.** One full run saw "NO REACTION IS REACHABLE" all game and won anyway. The React seat held Vermillion Pact and Aftershock for four fights and never cast them. They need a non-Pyro aura, which only a Companion card supplies, and Klee's own Pyro attacks overwrite it.
4. **Cards named NEVER AGAIN:** One More Charge (its 20 threshold never landed), Careful Now (reads the largest Bomb, which is small or just spent), Run Away!, Favonius Escort (deletes the deck's own bomb), Boom Badge (2 Sparks for a doubling that was never big), Vermillion Pact, Alice's Recipe (a Set-off-every-turn deck never lets a Bomb live), Playdate, Where Did I Put It?+. Patience, Klee! was drawn about five times and never played.

## Defects, fixed (#697, merged; reaches the game at the next deploy)

- Transforms (Pandora's Box, Kill with Fire) gave Klee and Kokomi Ironclad cards, because their borrowed basics transformed from Ironclad's pool. Fixed.
- Sizzle+ previewed "18 additional" and landed 10: the preview counted an aura the card's own hit uses first. Fixed.
- Big Badda Boom's second hit applied Vulnerable twice. Fixed.
- Bang Bang!'s Bomb vanished when the hit killed its target. It now jumps, as the Bomb rule says. Fixed.
- Coven Errand asked for a target in its ALL case. Fixed.
- Seat page: the Bomb header now says "deals 19 (sizes 13)"; Knowledge Demon's heal is no longer a "NEW body"; Sit Tight's status says when it will not pay; Sloth's counter reads the right way round.
- Two BACKLOG lines: Big Badda Boom's Block counting differs between mod and sim, and Once More! is silent when it finds nothing.
- Countdown and Sucrose target correctly: "Set off" reads "on the enemy".

## What to change

Claude's calls (Prototype stage):
- **Defence in act 3.** Klee's intended weakness is defence (brief section 6), and one full run won through it. Watch it in [USER]'s run; no card change yet.
- **Idle Sparks.** Spark sinks exist at Common (Dig In, Bottomless Bag). The seats that sat on Sparks had not drafted them. Watch it.
- **The single NEVER AGAIN cards** (Favonius Escort, Boom Badge, Alice's Recipe, Playdate, Where Did I Put It?+) each came from one seat. Watch them.

## Pick for [USER] (ruled)

**Ruled 2026-09-27, (a).** [USER]: "For #700, I'm fine with both defaults. We can keep an eye on this as we go and look at the Take the Stage card more carefully during the balance phase, but it sounds like these might be out of date complaints after our other changes."

The new fact, in one line: in acts 2 and 3, three of six seats never set off an Elemental Reaction with Klee's own cards. The React Rares (Vermillion Pact, Aftershock) went unplayed, because every Klee Attack applies Pyro (rule 5) and only a Companion card brings the other element. This is the path [USER] chose in draft 4 ("Off-element bombs arrive through a companion").

1. **The React loop's aura supply.**
   - **(a, default)** Keep rule 5 and the companion supply. React stays the companion-dependent third plan, and [USER]'s own run is the next read of it.
   - **(b)** Klee's Attacks stop applying Pyro; only her Bombs do. A companion's aura then survives until a Bomb goes off on it.
   - **(c)** Keep rule 5, and move Vermillion Pact and Aftershock from Rare to Uncommon, so that React is a cheaper side bet.
