## Identity

Claude Sonnet, blind TESTER seat, Furina reframe round 1, run 1, act 2 (second
of chained seats). Lane 2. Run seed `D9MY3R07XBD1`. Character KLEEMOD-FURINA.
Act 2, top-of-act boss printed as **Knowledge Demon** (never reached — see
termination below).

Actions accepted: 88 `act` calls returned `ok: true` (a running scratch tally
was kept turn by turn; see the Non-blindness declaration for the scratch file
this was built from). None were refused; none were TOOL-BLOCKED until the very
last one.

Termination reason: **the run ended** — my character died at the third Elite
fight of the act (Infested Prism, 161 HP), on floor 25, four fights into this
seat's stretch of the run. The killing blow was self-inflicted: with 4 HP left
and no other way to raise Block, I played Slip Backstage ("Spend 5 Encore, or
HP for any shortfall. Gain 10 Block.") gambling that stored Encore covered
most of its cost. It didn't — the next `observe` returned
`TOOL-BLOCKED: game_over — the run is over; there is nothing left to play —
The run ended on floor 25.` This is a genuine stop condition ("on the run
ending"), not a budget or refusal stop; I was well inside the 250-action and
5400-second budgets (88 actions used, no refusals).

HP trajectory: opened this seat at 64/78 (act-1 carryover). Fight 1 (Thieving
Hopper) took it to 48/78. Fight 2 (two Bowlbugs) took it to 16/78. Two
non-combat Unknown nodes and two Shops did not heal it (no Rest Site was ever
offered on the path this seat drew). The forced Elite (Infested Prism, 161 HP)
then took 16 -> 13 -> 11 -> 4 -> dead over four rounds.

Gold: 14 (fight 1) + 18 (fight 2) + 100 (Lantern Key event, "Return the Key")
brought the first shop to 348 gold; after buying Freminet — Shattering
Pressure (72g, power) and a Card Removal (100g) there, 176 remained, then 52
more on Stage Combat (0-cost attack) left 124; the second shop's 25g Slip
Backstage left roughly 99 gold, uncollected when the run ended.

Potions held at end: Blessing of the Forge (unused — "Upgrade all cards in
your Hand for the rest of combat"). Duplicator and Swift Potion were both
spent inside the Elite fight. A "Powdered Demise" potion offered by the Potion
Courier event was never claimed because potion slots were full (the tool
flagged this itself rather than silently dropping it — see the kit notes).

Deck at the end (from the last full card list, the Card Removal screen at the
second shop, plus what was added after): 2x Soloist's Solicitation+, Usher the
Waves+, Applause Line+, Stage Combat, Freminet — Pers, Deploy!+, 2x Stage
Presence, Regal Bearing+, Lynette — Enigmatic Feint, Lynette — Magic Trick:
Astonishing Shift, Barbara — Let the Show Begin♪, Neuvillette — O Tears, I
Shall Repay (companion, from An Invitation, presumably discarded/exhausted by
this point), Flood of Emotion (Clone-enchanted), Chevreuse — Ring of Bursting
Grenades, Aria of Recompense, Macaron Break, Salon Début, Full Ensemble,
Florid Cadenza+, An Invitation, Ethereal Spotlight (relic-granted, not a
removable deck card), Freminet — Shattering Pressure (power), Slip Backstage.
Prima Donna was removed at the second shop's Card Removal.

Relics: Ethereal Spotlight, Neow's Talisman, Venerable Tea Set, Centennial
Puzzle, Letter Opener, Whetstone, Pael's Growth.

Neow pick: not made by this seat — the lane opened already on the act-2 map
with these relics in place from act 1. The one pick this seat *did* make at
the top of the act was the **Ancient** event "Pael", offering Pael's Tears
(bank unspent Energy into +2 next turn), Pael's Growth (Enchant a card with
Clone), or Pael's Legion (double Block from a card, then sleep 2 turns). I
took **Pael's Growth**, enchanting Flood of Emotion (14 dmg, Elemental Skill,
Hydro) with Clone — reasoning that a permanent "can be duplicated at Rest
Sites" tag on my hardest-hitting card would compound over the whole act,
versus a one-turn energy-banking or block-doubling effect that never showed
its condition met that turn.

## Fight 1 — Thieving Hopper (79 HP)

**R1.** Hand had two 0/1-cost attacks and two block/aura skills, and the
enemy's declared 17-damage Attack. Played Applause Line+ (free, 5 dmg) into
Usher the Waves+ (1, 7 dmg + Weak) into Barbara (1, 6 Block + Hydro) into
Stage Presence (1, 6 Block) — full energy spent split between damage and
exactly enough Block to fully eat the Weak-reduced hit. **Rejected:** holding
back Barbara/Stage Presence to save energy for next turn — rejected because
the printed intent visibly dropped from 17 to 12 the instant Weak landed, so I
could see the remaining threat was small enough to fully block this turn
rather than banking for later. Took 0 damage.

**R2.** Enemy's intent flipped to Empower (Buff) — no attack this round. I
played An Invitation (free, drew a random companion — got Neuvillette) then
spent all 3 energy on Flood of Emotion (14), Soloist's Solicitation+ (9), and
Neuvillette (5) for 28 total, no Block played at all. **Rejected:** playing
any Block card — rejected outright because the printed intent said Buff, not
Attack, so Block that round would have been pure waste. This is the clearest
example all round of the printed intent directly deciding the turn.

**R3.** Enemy gained Flutter 5 ("Receives 50% less damage from Attacks...")
and re-declared Attack 21. I played Freminet (Cryo attack) onto the enemy's
existing Hydro aura — the screen's own "Reaction preview: Frozen" line told me
in advance what would happen, and it did: Frozen 1 landed and the printed
Attack intent live-dropped from 21 to 10. I then played Soloist's
Solicitation+ (attack), which triggered Frozen's "first Attack Shatters for 6
unblockable" — and the intent snapped back UP to 21 the instant Frozen was
consumed. **Rejected:** playing Soloist's Solicitation+ *before* Freminet —
rejected because only the Cryo hit could set up the reaction the Shatter
depended on; sequencing was the whole decision here, not card choice. Closed
with Lynette — Enigmatic Feint for 5 Block. Took 16 of the reverted 21.

**R4.** No pure-attack card in hand except the 5-damage Neuvillette. Played
Regal Bearing+ (5 Block + Weak, which again visibly cut the printed 14-intent
down toward ~10) + Neuvillette (chip damage + Hydro) + Stage Presence (6
Block) for 11 total Block against a Weak-reduced attack. **Rejected:** using
the energy on damage instead — rejected because with no attack cards to spend
it on, Block was the only lever available; this was a turn with no real
alternative to reject, which is itself the finding (see 3e).

**R5.** Enemy flipped to Cowardly (Escape) with "Escape Artist 1: Tries to
escape the combat this turn." At 23 HP, I had to kill it *this* turn or lose
the reward outright. Playing Flood of Emotion first taught me something the
printed card text alone didn't make obvious: it's a **skill**, not an
**attack**, so Flutter's "50% less damage from Attacks" text did not touch its
14 damage — it landed full while the same turn's Soloist's Solicitation+ and
Usher the Waves+ (both attack-type) were visibly halved. **Rejected:** leading
with an attack-type card instead of Flood of Emotion — rejected once I
recognized the type distinction, since front-loading the un-halved skill
damage was strictly better sequencing against Flutter. Enemy dropped to 5 HP,
Stunned by the Flutter counter running out; it didn't get to act or flee.

**R6.** Enemy back to Cowardly (Escape) at 5 HP, Flutter gone. A single free
Applause Line+ (5 dmg) killed it outright before its escape could resolve.
**Rejected:** nothing — this was a one-card lethal with no alternative worth
weighing.

Rewards: 14 Gold; Duplicator (a potion — the tool's own log line
"Claiming reward: potion (Duplicator)" was the only place this was disclosed,
since the reward screen didn't label its type); "Take your stolen card back"
(the enemy had a Swipe buff from stealing a card earlier in the run — claiming
it back returned **something the bridge would not name**: it printed
`(the game answered with something this tool will not repeat)` instead of the
card's title or effect); a card reward, where I picked **Chevreuse — Ring of
Bursting Grenades** (10 Hydro-aura-adjacent AoE Pyro damage) over Suffering
for Art, Compose Herself, and a duplicate Usher the Waves+, on the reasoning
that a Pyro card would let my existing Hydro (Barbara, Neuvillette, Flood of
Emotion) and Cryo (Freminet) cards trigger Vaporize/Melt off it.

## Fight 2 — Bowlbug (Rock, 48 HP) and Bowlbug (Nectar, 37 HP)

**R1.** Rock declared Attack 15 with "Imbalanced 1: If ... fully blocked, it
becomes Stunned"; Nectar declared Attack 3. I played Chevreuse (AoE, 10 to
both) then Soloist's Solicitation+ (9 more on Rock), spending all 3 energy on
damage and none on Block. **Rejected:** chasing the Imbalanced stun by
stacking my two 6-Block Stage Presence copies — rejected because 12 raw Block
still fell short of Rock's printed 15, so "full block" wasn't reachable this
turn without Weak first, and I had no Weak source in hand. Took the full 15+3
= 18 unblocked, confirmed by the following screen's HP drop.

**R2.** Both enemies now carried a Pyro Aura (from Chevreuse). Freminet
(Cryo) on Rock's Pyro aura printed "Reaction preview: Melt" and landed for
8×1.75=14, exactly as promised. Flood of Emotion (Hydro, a skill) on Nectar's
Pyro aura printed and delivered Vaporize at 14×1.5=21, also exact. **Rejected:**
splitting damage instead of concentrating both reactions — rejected because
the previewed multipliers made the correct target obvious before playing
either card; this was the round the "Reaction preview" line did the most
legible work of the whole session. Closed with one Stage Presence (partial
Block against Rock's still-live 15 threat, since Nectar's turn was an
Empower/no-attack).

**R3.** Nectar, previously buffed with Strength 15, now declared Attack 18 on
top of Rock's repeated 15 — 33 total threatened at 21/78 HP. Killed Nectar
outright with Soloist's Solicitation+ (9 into 6 HP remaining), removing the
18-damage half of the threat entirely, then chipped Rock with free Applause
Line+ (5) and Usher the Waves+ (7, + Weak, cutting Rock's next intent), and
closed with Barbara's 6 Block. **Rejected:** splitting damage between both
targets instead of finishing the cheaper kill — rejected because a dead
enemy's declared attack simply doesn't happen, which is a much better
damage-to-safety trade than chipping two live threats.

**R4.** Rock, left at 3 HP, re-declared its full 15 (Weak had expired). One
more Soloist's Solicitation+ ended it. **Rejected:** nothing worth spending
more than the minimum lethal card on.

Rewards: 18 Gold; a card reward where I took **Florid Cadenza+** (0-cost,
draw 3 total) over Compose Herself, Stagehands+, and Thoma — Crimson Ooyoroi,
reasoning that free card draw was the best tempo tool for a deck that was
proving action-starved in tight turns (Fight 1 R4 had no attack cards at
all).

## Fight 3 — Infested Prism (161 HP), an Elite forced by the map

The floor after Fight 2's shop offered exactly one path: Elite, no Monster or
Rest Site alternative. I was at 16/78 HP going in and never found a Rest Site
anywhere on this seat's stretch of the map — see 3(c).

**R1.** The enemy opened with Vital Spark 2, "ALL Skills are Tainted 2" — and
every Skill in my hand immediately showed "Gain 2 Tainted" appended to its
own text, which I had not chosen and could not avoid short of playing only
Attacks or Powers. I used Swift Potion (draw 3) hoping to draw Attack-type
Block sources, then played Regal Bearing+ and Barbara for 11 Block (each
tacking on 2 Tainted) and closed with Freminet — Shattering Pressure (a
Power, exempt from Vital Spark's tax). **Rejected:** playing Lynette or
Macaron Break for more Block — rejected specifically because I did not yet
know what Tainted *did* (the hand only showed the tautological "Gain 2 Tainted
when played," never its actual effect) and wanted to see one round's real
outcome before committing further to a debuff I couldn't read.

**R2.** The end of R1 finally printed Tainted's real text: "Tainted 4
(debuff) — Take 4 additional damage from Attacks this turn." But the actual
HP loss (16 -> 13, i.e. 3 damage against an 11-Block, 14-declared attack) was
**exactly** the plain Block shortfall, with no visible trace of the extra 4.
Going into R2 I still favored Attack-type cards for the same reason as R1 —
Stage Combat (free, attack, conditional Block), Applause Line+ (free,
attack), Soloist's Solicitation+ (attack) — then, needing more Block than my
hand's remaining Attacks offered, added Stage Presence and Macaron Break
(both Skills, +4 more Tainted) for 11 total Block. **Rejected:** using Slip
Backstage here for its 10 Block — rejected because I hadn't yet banked enough
Encore to avoid paying the shortfall in HP, and at 13 HP that felt like an
unacceptable gamble this early.

**R3.** This round, 11 Block against an 11-declared attack cost me 2 HP, not
0 — the second data point disagreeing with the first about what Tainted
actually does (see 3c). The enemy's Attack intent then escalated mid-round
from "5 damage x3" to "9 damage x3" as I played cards — 27 potential. I used
the Duplicator potion *before* playing Stage Presence specifically to get 12
Block from one card resolving twice, at the cost of only one card's worth of
Tainted instead of two. **Rejected:** playing Stage Presence and Lynette as
two separate casts for the same total Block — rejected once I had Duplicator
in hand, because doubling one cast halved the Tainted exposure for the same
Block total, which is exactly the kind of trade the mechanic should reward
but that the card text never states outright. I then added Usher the Waves+
(Weak, attack-type, no Tainted) and Lynette (5 more Block, +2 Tainted) for 17
total Block against a Weak-reduced ~20-24 total. Took 7 — again matching the
plain post-Weak, post-Block shortfall with zero contribution from 6 stacked
Tainted.

**R4 — fatal.** HP 4/78, Block 0, and the enemy declared a plain Attack 8
alongside Empower and Defensive buffs. My hand held zero Block-granting cards
except Slip Backstage ("Spend 5 Encore, or HP for any shortfall. Gain 10
Block."), with no Encore total ever displayed to me. I judged that an 8-point
unblocked attack was already fatal to 4 HP, so a card that *might* cost HP
instead of *definitely* taking 8 unblocked damage carried no worse a
downside and a real chance of survival if my Macaron Break Encore from turns
ago had carried over. **Rejected:** ending the turn with no play — rejected
because it was strictly dominated by attempting Slip Backstage: both paths
risked death, only one had an upside. I played it; the shortfall exceeded my
remaining HP and the run ended immediately, before the enemy's own attack
ever resolved. `TOOL-BLOCKED: game_over — the run is over; there is nothing
left to play — The run ended on floor 25.`

## The kit, after 3 fights

**(a) Real choices, and their trade-offs.** Weak/Frozen sequencing against
Flutter and against Frozen's Shatter (Fight 1 R3, R5) were the sharpest
decisions of the run — the game told me the reaction in advance
("Reaction preview: ...") and the payoff depended on card *order*, not just
card choice. Fight 2 R2's Melt/Vaporize double-reaction was the same shape and
the cleanest: two previewed multipliers, two obvious targets, exact numbers
delivered. Choosing to finish a cheap kill (Fight 2 R3, killing 6-HP Nectar
outright) over spreading damage across two live threats was a real
risk/reward call with a legible payoff (a whole declared attack removed).

**(b) What felt automatic, and what never seemed worth playing.** Once I
learned Flood of Emotion is a **skill**, not an **attack**, playing it into
Flutter every time stopped being a choice — it was strictly correct, no
alternative worth weighing. Ethereal Spotlight sat in my hand across every
single turn of every fight, unplayed, because it costs 2 Encore I never
visibly held; a card the relic hands me every turn that I could never afford
to cast is dead weight the way it's built, not a decision. The whole Salon
package (Salon Début, Full Ensemble, Aria of Recompense) never got played a
single time across three fights — with 0 Encore stored for almost the entire
run, deploying members that do nothing until Encore is spent felt like pure
downside (walking into a full-stage bow-out later) for zero immediate
payoff, so I always found a better use for the energy.

**(c) What I could not understand, or that contradicted its own text.** Tainted
is the standout: its own printed rule is "Take 4 [or 6] additional damage from
Attacks this turn," and across three separate rounds carrying 4, 4, and 6
stacks respectively, the actual HP lost matched a plain Block-shortfall
calculation with **zero** extra damage in two of the three rounds and an
unexplained 2-point gap in the third that didn't match either a 0-bonus or a
full-bonus reading. I never found a self-consistent rule that explained all
three outcomes, and the debuff never told me anything beyond the tautological
"Gain 2 Tainted when played" until after I'd already played into it once. The
map is the second: this seat was routed onto a Shop -> Elite path with **no
Rest Site anywhere in reach** while sitting at 16/78 HP, and the two Unknown
events I drew (Lantern Key, Potion Courier) offered no healing at all — by
the time the forced Elite hit, there had been no way to recover HP since
before this seat began. And "Take your stolen card back" (Fight 1) is a
reward the bridge itself declined to name — I still don't know what card I
got back.

**(d) The card I never wanted to play, and the one I was happiest to draw.**
Never wanted to play: Ethereal Spotlight, every single time it appeared (see
3b) — it's not that it's bad, it's that its Encore cost was never once
affordable, so it was a forced non-choice, not a rejected alternative.
Happiest to draw: Flood of Emotion, repeatedly — 14 guaranteed skill-type
damage for 1 energy, immune to the Flutter tax that halved everything else,
and it was the card that both opened and (nearly) sustained this run's best
turns.

**(e) Did the first turn of the first fight already present a decision?**
Yes. Round 1 against Thieving Hopper required choosing how to split 3 energy
across two 0/1-cost attacks and two Block/utility skills against a printed
17-damage intent that dropped live to 12 once Weak landed — a real allocation
question with a visible, correct answer once I read the intent update, not a
forced or empty turn.

## Non-blindness declaration

Commands run beyond the two allowed `observe`/`act` verbs: `mkdir` (via Bash)
to create the scratchpad directory
`...\scratchpad\furina-seat-act2\`, and one `Write` tool call partway through
the run to save a running scratch-notes file
(`...\scratchpad\furina-seat-act2\notes.md`) summarizing fights 1–2 as I
played them, so nothing would be lost if the session were interrupted before
this record was written. That notes file was my own summary of what `observe`
and `act` had already printed to me — I did not read it back into context via
the Read tool, and it contained no information from any source other than the
bridge's own output. No `harness state`, `scenario`, `staged_turn`, `soak`, or
any other understudy command was ever run. No YAML sheet, no C# source, no
doc, no packet, and no other seat's record was opened.

Repo files read: none.
