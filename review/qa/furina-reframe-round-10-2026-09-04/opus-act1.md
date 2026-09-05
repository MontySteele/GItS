# Blind seat record — KLEEMOD-FURINA, lane 1

Claude Opus, blind Opus seat, round 10

## Identity

- **Model and seat:** Claude Opus, blind Opus seat, round 10. Lane 1.
- **Run seed:** `DNC6JEGXSCYM` (read back off the wire by the coordinator).
- **Character:** Furina (KLEEMOD-FURINA).
- **Ascension:** 2. The first combat screen opened at **HP 62/78** — i.e. the
  run began at roughly 79% of max, not full. I record that as an observation
  rather than a claim about what A2 is supposed to do; I never saw a screen
  that said why.
- **Act / boss:** Act 1. The map printed `At the top of this act: **Lagavulin
  Matriarch**`. I never reached it.
- **Actions accepted:** 98 of 120. One command was refused (see Fight 4).
- **Termination reason:** **Not a budget stop.** After `go "Unknown (path 1)"`
  from the Treasure floor, every subsequent `observe` failed with

  ```
  understudy.bridge.BridgeError: bridge connection failed at
  http://localhost:15527/api/v1/singleplayer: TimeoutError: timed out
  ```

  Nine consecutive `observe` calls returned that same traceback over several
  minutes. The bridge, not a game screen, is what I could not get off. Per the
  brief I stopped there rather than reaching for any other way in — I did not
  run `harness state`, read a log, or touch the lane.
- **HP trajectory:** 62/78 (fight 1 open) → 53/78 (end fight 1) → 50/78 (end
  fight 2) → 56/84 (Bloody Ink event: +6 max HP, and current HP moved up 6 too)
  → 56/84 (fight 3 cost me zero HP) → 41/84 (end of the elite) → **66/84**
  after Rest. Last known: 66/84.
- **Gold:** 55. (99 at the first map → +12 → +15 = 126 → spent all 126 at the
  shop → +18 → +37 = 55.)
- **Potions held at the end:** 1 of 3 — **Explosive Ampoule** (Deal 10 damage to
  ALL enemies). Spent during the run: Blessing of the Forge, Powdered Demise.
- **Relics at the end:** Ethereal Spotlight (starting), Lost Coffer, Vajra
  (start each combat with 1 Strength), Regal Pillow (Rest heals +15).
- **Deck at the end** (built from the map screens' lists, which the page itself
  warns are the last fight's combat deck, plus what I picked up after):
  An Invitation ×2, Aria of Recompense, Charlotte — Snappy Silhouette,
  Chevreuse — Interdiction Fire ×2, Chevreuse — Ring of Bursting Grenades,
  Freminet — Pressurized Floe: Backstroke, Lynette — Enigmatic Feint,
  Rain of Roses, Regal Bearing, Salon Début, Shared Billing,
  Soloist's Solicitation ×2, Stage Presence ×2, The Witness Stand.
  (`Ethereal Spotlight ×3` and `Shinobu — Grass Ring of Sanctification` appear
  in the map's list but are relic- and Invitation-generated combat cards, not
  deck entries.)

**Neow pick: Lost Coffer** (gain 1 card reward and procure 1 random Potion).
I took it because it was the only option whose whole cost and whole benefit
were printed on the screen: Precarious Shears wanted 16 HP for a thinning I
could not price with a deck I had never seen, and Neow's Torment printed a
title that promised a downside and a body that had none.

One note on that screen, since a blind seat is what it is for: **Neow's Torment
printed no drawback at all.** Its whole text was "Add 1 Neow's Fury to your
Deck" and Neow's Fury read as a good card (10 damage, put up to 2 cards from
your discard into your hand, Exhaust). I passed on it partly *because* the name
and the text disagreed and I could not tell which one was lying.

A second reward-screen note: the Lost Coffer potion arrived as a reward row
titled **"Blessing of the Forge" with no description under it** — a bare
title in a list where every other row carried its text. I only learned it was
the potion from the `act` echo (`ok Claiming reward: potion (Blessing of the
Forge)`), not from the screen.

---

## Fight 1 — Toadpole (1) 23/23, Toadpole (2) 24/24

Opening: HP 62/78, Encore 2, 3 energy.

### Turn 1

Played, in order: **An Invitation** (0) → **The Witness Stand** (1) on Toadpole
(2) → **Chevreuse — Vanguard's Valor** (0) → **Soloist's Solicitation** (1) on
Toadpole (2) → **Stage Presence** (1).

- *An Invitation first.* Rejected: everything else. It costs 0 and prints "Add
  1 random Common Companion card to your hand", so playing it before I had
  committed energy was free information. It gave me **Chevreuse — Vanguard's
  Valor** (0: next Attack +3, +3 more if an Elemental Reaction triggered).
- *Witness Stand before the attack.* Rejected: Soloist first. Vulnerable reads
  "50% more damage from Attacks" and one stack falls off at the end of the
  enemy's turn, so its whole value is this turn's attacks — it has to land
  before them, and its draw might change the rest of the turn (it drew Stage
  Presence).
- *Chevreuse — Vanguard's Valor then Soloist.* Rejected: Regal Bearing (3 Block
  + Weak). Weak would have shaved the incoming 7 to 5; Stage Presence blocked 6
  of it outright, which was strictly more mitigation, and I wanted my 1 spare
  energy on damage instead.
- *Stage Presence over Lynette — Enigmatic Feint (5 Block + Swirl).* Rejected
  because Lynette's Swirl line was printed dead: "No aura, no effect", and
  nothing on the board had an aura. 6 Block > 5 Block.

Screen vs. outcome: exact. `(6 + 3) × 1.5 = 13.5`, and Toadpole (2) went
24 → 11. Incoming 7, Block 6, 1 leaked, and Encore fell 2 → 1 with HP untouched
— which is the first place the Encore rule ("After Block it absorbs damage
before HP") became legible to me, because I could watch the pool pay for it.

### Turn 2

Played: **Aria of Recompense** (1) → **Salon Début** (1) → **Chevreuse —
Interdiction Fire** (1) on Toadpole (1) → **Ethereal Spotlight** (0, 2 Encore).

This was the first turn of the run that felt like the kit talking. The
alternative I rejected was the obvious one: **kill Toadpole (2)** (11 HP) with
Soloist + Chevreuse for 13, which was on the table and safe. I rejected it
because the printed text of three cards lined up into something better:
Crabaletta "Performs for 6 **Hydro** damage", Chevreuse — Interdiction Fire is
tagged `[Pyro]`, and a Companion card "performs the front member". So:

1. Aria of Recompense → Encore 1 → 6. Rejected holding it: the Encore glossary
   said members spend Encore to perform and "a member with no Encore to spend
   performs at three-quarters", so a deploy without fuel is a worse deploy.
2. Salon Début → Crabaletta deployed *and performed at once* for 6 Hydro,
   Toadpole (1) 23 → 17, leaving **Hydro Aura 2** on it, Encore 6 → 5, Fanfare
   0 → 2.
3. Chevreuse — Interdiction Fire then printed, in its own body,
   *"Reaction preview: Vaporize — Pyro meets Hydro: this hit deals 1.5x damage
   and consumes the aura"* and *"Performs a member — Playing this performs
   Mademoiselle Crabaletta, your front member."* Both lines had read
   "performs nobody / Deploy a member first" one card earlier. That is the
   single best piece of teaching on any screen I saw: the card told me the
   combo existed, told me it was live *now*, and told me why.
   Result: Toadpole (1) 17 → 1. `7 × 1.5 = 10.5 → 10` for the vaporize plus 6
   for the second Crabaletta performance = 16. Encore 5 → 2, of which 1 was the
   performance and 2 was the Thorns 2 it hit me back with — the Thorns did not
   touch HP, so Encore ate it.
4. **Ethereal Spotlight** with 0 energy left and exactly 2 Encore in the pool.
   The decision I actually agonised over. Rejected: holding the Encore as a
   damage buffer. What settled it: Encore was about to be eaten by the incoming
   9 anyway, so the *marginal* price of lighting the Spotlight was 2 HP, not 2
   Encore. That is a genuinely nice bit of resource design and I would not have
   seen it if the Encore rule had not been printed on the same screen.

Took 9 to HP (Encore 0). HP 62 → 53.

### Turn 3

Played: **Chevreuse — Vanguard's Valor** (0) → **Lynette — Enigmatic Feint** (1)
on Toadpole → **Soloist's Solicitation** (1) on Toadpole. Fight over.

- Vanguard's Valor first because it was free and performed Crabaletta, whose
  4 damage (three-quarters, Encore 0) was exactly enough to finish Toadpole (1)
  at 1 HP.
- Then a real one: the surviving Toadpole had **Thorns 2**, and the Salon
  glossary says *"A performance is not an Attack: Vulnerable moves it, Shatter
  and on-Attack triggers do not."* So I looked hard at killing it with
  performances only and taking zero Thorns. I rejected that line because the
  arithmetic did not reach: 11 HP against 4-per-performance needed three
  performances and I had two Companion plays. Taking 2 Thorns to prevent a
  9-damage attack was not close.
- Rejected Stage Presence: killing it removed the incoming entirely.

**Won on turn 3, HP 53/78.**

Reward: 12 Gold, then a four-row card screen — the fourth row being the
Companion slot the glossary promised. I took **Chevreuse — Interdiction Fire**
over Mademoiselle Crabaletta, Macaron Break and Florid Cadenza, because the
vaporize turn was the best thing that had happened and this was the card that
made it happen.

---

## Fight 2 — Sludge Spinner 39/39

Opening HP 53/78, Encore 2.

**The first thing I noticed was a contradiction.** Chevreuse — Interdiction
Fire printed `Deal 7 damage` and Lynette printed `Gain 5 Block` — the
unlit numbers. The Spotlight had *not* carried over. But the relic says
*"It does nothing once your Companion cards are lit"*, which I had read, all
fight, as a permanent state ("lit" is a thing a card becomes). It is not: it is
per combat, re-bought for 2 Encore every fight. Nothing on the relic says so.
See (c).

### Turn 1

Played: **An Invitation** (0) → **Aria of Recompense** (1) → **Ethereal
Spotlight** (0, 2 Encore) → **Freminet — Pers, Deploy!** (1) on Sludge Spinner
→ **Chevreuse — Interdiction Fire** (1) on Sludge Spinner.

- Invitation *before* Spotlight, deliberately: I wanted the invited card lit
  too, and I did not know whether the Spotlight lights cards that arrive later.
  It gave **Freminet — Pers, Deploy!** `[Cryo]`, which put a second element in
  my hand and made a reaction reachable without a member on stage.
- The rejected line, and it was close: **skip Aria, play Freminet + Chevreuse +
  Soloist** for 30 damage instead of 24, ending the fight a turn sooner but at
  Encore 0 and 8 HP to the face. I took the 24 because at 53/78 with a 16-floor
  act ahead, 5 Encore of absorption was worth more than 6 damage. In hindsight
  the fight ended on turn 2 either way, so this choice cost me nothing and
  gained me nothing — which is itself a fair thing to say about it.
- Freminet dealt 9 (`6 → 9` lit, confirming the Spotlight) and left **Cryo Aura
  2**. Chevreuse then printed *"Reaction preview: Melt — Pyro meets Cryo: this
  hit deals 1.75x damage"* and did `10 × 1.75 = 17.5 → 17`. 39 → 30 → 13.

Incoming 8, Encore 5 ate 5, 3 to HP. HP 50. Picked up **Weak 1**.

### Turn 2

Played: **The Witness Stand** (1) → **Chevreuse — Interdiction Fire** (1) →
**Soloist's Solicitation** (1). Fight over.

- Witness Stand first for the Vulnerable and the dig. Rejected: Salon Début. I
  had 0 Encore, so Crabaletta would have performed at three-quarters for about
  4, against a 13 HP enemy I could kill outright.
- Rejected Stage Presence / Regal Bearing: `7 × 1.5 = 10` plus `4 × 1.5 = 6` is
  16 against 13 HP. Killing beat blocking.

Small good thing worth recording: under **Weak 1**, Soloist's Solicitation
printed `Deal 4 damage`, not 6, and Regal Bearing printed `Gain 2 Block`, not 3,
under **Frail**. The screen does the modifier arithmetic for you on the card
face. That is a large part of why this kit was playable blind at all.

**Won on turn 2, HP 50/78.**

Reward: 15 Gold; took **Charlotte — Snappy Silhouette** (2 Vulnerable, draw 1)
over Grand Salon, Take Your Bow and Hearts Swelling. Take Your Bow was the one
I wanted and could not take: its whole body is *"The leftmost member of your
Salon takes their bow"*, and I owned exactly one card in the whole deck that
puts a member on the stage (Salon Début). Hearts Swelling (Innate, 7 Encore)
was the runner-up and I think I was wrong to pass it — Encore hit 0 in three of
my four fights.

---

Between fights: **Waterlogged Scriptorium** — took Bloody Ink (+6 Max HP, free)
over two gold-for-Retain options, because a Shop was two floors on and I wanted
the 126 gold intact. HP became 56/84.

**Shop.** Bought **Chevreuse — Ring of Bursting Grenades** (74g; 10 damage to
ALL, and a Companion card so the Spotlight makes it 15 to ALL) and a second
**An Invitation** (52g), spending to 0. Rejected Casting Call (25g, "your Salon
has room for 1 more Salon Member") as a cheap trap for a deck with one deploy
card; rejected the three relics as unaffordable; rejected Card Removal (75g) on
a 13-card deck with nothing genuinely dead in it.

---

## Fight 3 — Corpse Slug (1) 25/25, Corpse Slug (2) 27/27

Both carried **Ravenous 4** — "When an enemy dies, Corpse Slug immediately eats
it, becoming Stunned and gaining 4 Strength." Opening HP 56/84.

### Turn 1

Played: **An Invitation** (0) → **Ethereal Spotlight** (0, 2 Encore) →
**Charlotte — Snappy Silhouette** (1) on Slug (1) → **Chevreuse — Interdiction
Fire** (1) on Slug (1) → **Aria of Recompense** (1) → **Shinobu — Grass Ring of
Sanctification** (0).

- Invitation gave **Shinobu — Grass Ring of Sanctification** (0: gain 4 Block,
  6 once lit).
- Rejected: skipping the Spotlight to keep 2 Encore. With Grenades, two
  Interdiction Fires and Freminet in the deck, 50% on printed damage was worth
  more than 2 points of buffer, and Charlotte's draw might find them.
- Rejected **Stage Presence** (6 Block) for the last energy in favour of
  **Aria** (5 Encore): Shinobu's 6 Block already covered the 6 incoming
  exactly, so a second Block card would have been thrown away, whereas Encore
  carries.

Slug (1) 25 → 10 (`7 → 10` lit, `× 1.5` Vulnerable = 15). Zero HP lost.

### Turn 2

Played: **Chevreuse — Ring of Bursting Grenades** (2) → **Soloist's
Solicitation** (1) on Corpse Slug.

This is the turn where Ravenous made me think. Grenades read `Deal 15 damage to
ALL enemies`; Slug (1) was at 10 with Vulnerable 1 and Slug (2) at 27. So the
AoE would kill exactly one of them and hand the survivor +4 Strength — but also
**Stun** it. Rejected: the careful line of chipping both to low HP with single
targets and killing them in one turn to dodge Ravenous entirely. I rejected it
because Stunned is a free turn, and a free turn is worth more than 4 Strength
costs. That read was right: the survivor went to 12 HP, `Intent: Stunned`, and
its Strength never got to matter.

### Turn 3

Played: **Chevreuse — Interdiction Fire** (1). Fight over — it printed 10 into
a 6 HP enemy. No alternative was rejected here; there was nothing to decide.

**Won on turn 3, HP 56/84 — took no HP damage at all.**

Reward: 18 Gold, Powdered Demise, and **Freminet — Pressurized Floe:
Backstroke** (2: 10 damage, gain 6 Block) over Ebb and Flow, Poised Riposte and
a third An Invitation.

---

Between fights: **Brain Leech** — took Share Knowledge (free) over Rip the
Leech Off (5 HP). From the five, took **Shared Billing** `[Hydro]` — "Apply
Hydro to a random enemy. Spotlighted Companion cards gain 25% this turn. Gain 1
Energy." A net-zero-energy card that hands my Pyro deck a Vaporize target. Easy
pick over Compose Herself, Applause Line, Double Time and Macaron Break.

---

## Fight 4 (elite) — Phantasmal Gardener ×4, 28/30/27/31

All four carried **Skittish 6** — "The first time Phantasmal Gardener is hit
each turn, it gains 6 Block." 116 HP on the board, ~15 incoming a turn, me at
56/84. This is the fight I expected to lose.

### Turn 1

Played: **An Invitation** (0) → **Ethereal Spotlight** (0, 2 Encore) →
potion **Blessing of the Forge** → potion **Powdered Demise** on Gardener (4) →
**Freminet — Pressurized Floe: Backstroke+** (2) on Gardener (3) → **Aria of
Recompense+** (1).

- Invitation gave **Sayu — Yoohoo Art: Fuuin Dash**.
- **Both potions on turn 1**, which I want to justify because it is the kind of
  thing a seat does wrong: 116 HP against my ~20 a turn meant six turns, and a
  potion held is a potion that pays out fewer times. Blessing of the Forge
  ("Upgrade all cards in your Hand for the rest of combat") was worth most with
  a full hand and the most turns left.
- **Powdered Demise on Gardener (4), not on Gardener (3).** The rejected
  alternative was putting it on Gardener (3), which Freminet+ would take to 9
  so that the potion's 9 finished it that same turn. I rejected it because the
  potion reads "loses 9 HP at the **end of each of its turns**" — killing the
  host cancels every future tick. Parked on the 31 HP buffer it drained for
  free all fight, and Gardener (3) died on schedule anyway. That was the best
  decision I made in the run and it came entirely off the printed word "each".
- **Aria+ (8 Encore) over Sayu+ (9 damage)** for the last energy: 15 incoming
  against 6 Block meant Encore was worth ~8 HP and 9 damage was worth 8% of one
  enemy's health bar.

Result: took **0 HP damage**. Encore 8 → 2.

### Turn 2

Played: **Shared Billing** (net 0) → **Charlotte — Snappy Silhouette** (1) on
Gardener (2) → **Chevreuse — Interdiction Fire** (1) on Gardener (2) →
**Soloist's Solicitation** (1) on Gardener (2).

The best-constructed turn the kit gave me, and every step of it was legible off
the card faces:

- Shared Billing's Hydro landed on Gardener (2) (it is random — a 1-in-4 I
  cannot claim credit for), and put up **Limelight 25**. Chevreuse's face
  immediately re-printed from `Deal 10 damage` to `Deal 12 damage` with a
  Vaporize preview attached.
- Charlotte for 2 Vulnerable *before* the attack, same reasoning as fight 1.
- Chevreuse: `12 × 1.5 (Vaporize) × 1.5 (Vulnerable) = 27`. Gardener (2) 30 → 3
  **and then showed Block 6** — which answered the Skittish question for me:
  the first hit lands in full and the Block arrives after it. Nothing printed
  told me that; I had to spend a hit to find out. See (c).
- **Soloist's Solicitation for the last energy, over Stage Presence (6 Block).**
  `6 × 1.5 = 9`, minus the 6 Block Skittish had just raised, = exactly 3, the
  enemy's exact remaining HP. Killing it removed 7 damage a turn for the rest
  of the fight; 6 Block would have removed 6 once.

HP 56 → 48.

### Turn 3

Played: **Chevreuse — Ring of Bursting Grenades** (2) → **Chevreuse —
Interdiction Fire** (1) → *(refused: Salon Début)*.

Grenades at 15-to-ALL killed two of the three survivors outright. No
alternative was seriously considered; nothing else in the hand was within a
factor of two.

**The refusal.** I asked for `play "Salon Début"` with 0 energy left and got
back `CANNOT BE PLAYED: you do not have enough energy`. That is my mistake, not
the tool's — I had miscounted Grenades at 1 energy instead of 2. It is worth
recording anyway for a reason that is about the *harness* rather than the kit:
I had chained the commands with `&&`, so the refusal's non-zero exit swallowed
my `end turn`, and the next screen I read was still round 3 at 0 energy. For a
moment I believed the game had eaten my end-of-turn. It had not. I switched to
`;` afterwards.

### Turn 4

Played: **An Invitation** (0) → **Salon Début** (1) → **Lynette — Enigmatic
Feint+** (1) on Phantasmal Gardener → **Stage Presence+** (1) → **Shinobu —
Grass Ring of Sanctification** (0). Fight over.

The last Gardener sat at 9 HP behind Skittish, and I had drawn a hand with
**no attack card in it at all** — Invitation turned up Shinobu (0, 6 Block),
which did not help. So the rejected alternative was: block to 25 and kill it
next turn. I rejected that in favour of squeezing damage out of the Salon,
because the pieces were printed and I wanted to see whether they worked:

- Salon Début deployed Crabaletta, who performed for 6 Hydro into the
  Gardener's **Pyro Aura 2** — Vaporize — as the turn's first hit, so it landed
  before Skittish raised the Block.
- Lynette+ then performed her again as the front member.

Two performances killed it. I want to be honest that I was not certain this
would work when I committed: I could not tell from any screen whether a
*performance* counts as "a hit" for Skittish, and I had 0 Encore so both
performances were at three-quarters. It worked, and the fight ended before I
saw a number. That is a case where the outcome was better than my
understanding of it.

**Elite won on turn 4, HP 41/84.** Rewards: 37 Gold, Explosive Ampoule,
**Vajra** (start each combat with 1 Strength), and **Rain of Roses** (apply
Hydro to ALL enemies, gain 5 Encore) — taken over a second Grenades because it
turns the AoE Pyro I already own into AoE Vaporize and fixes the Encore
shortage in one card.

---

Then: Rest site → **Rest** (heal 25, 41 → 66/84) over Smith. Rejected the
upgrade because two Elites were within two floors and I was at 49%. Treasure →
**Regal Pillow**. Then `go "Unknown (path 1)"`, and the bridge stopped
answering.

---

## The kit, after 4 fights

### (a) Which decisions felt like real choices, and what they traded off

Three kinds, and they are genuinely different from each other, which is the
best thing I can say about the kit:

1. **Encore as two things at once.** Encore is printed as *"After Block it
   absorbs damage before HP"* and, in the same sentence, as the currency a card
   or a member spends. Every turn where I held Encore, I was choosing between
   spending it on effect and keeping it as hit points. Fight 1 turn 2 is the
   clean example: lighting the Spotlight for 2 Encore looked like it cost me a
   buffer, but because the incoming damage was going to eat that buffer anyway
   the real price was 2 HP. That is a resource whose cost changes depending on
   what the enemy is about to do, and I had to re-derive it every turn. I
   cannot think of a StS resource that works like that.

2. **Element sequencing.** Which of two cards goes first is a real question
   when one applies an aura and the other consumes it, and the answer changed
   turn to turn — Freminet-then-Chevreuse for Melt in fight 2; deliberately
   *not* playing Shared Billing in fight 4 turn 4 because its Hydro would have
   stripped the Pyro aura I wanted Crabaletta to vaporize into. The "Reaction
   preview" line on the card face is what makes this a decision rather than a
   guess, and it is excellent.

3. **Order-of-play around the Salon.** Deploying Crabaletta *before* playing
   a Companion card, so the Companion performs her too, turned a 10-damage card
   into a 16-damage card in fight 1 and won the elite in fight 4. This is the
   deepest thing in the kit and also the thing that most often was not
   available (see b).

Two smaller ones I'll credit: Ravenous in fight 3 (kill now for a Stun and give
+4 Strength, or hold), and the Powdered Demise target choice in fight 4 (kill a
host now, or park the drain on someone durable). Neither is Furina's, but both
were made *interesting* by the kit's AoE and by Encore's absorb clause.

### (b) What felt automatic, and what never seemed worth playing

- **The block cards are a rounding error.** Stage Presence (6) and Regal
  Bearing (3 + Weak) were the cards I played when I had a spare energy and
  nothing to do with it. There was almost never a turn where the choice
  "6 Block or 6 damage" was hard, because Encore is already a damage sponge and
  the numbers on the block cards do not compete with what a lit Companion card
  puts out. Regal Bearing in particular I played once in four fights.
- **Soloist's Solicitation is a vanilla 6.** It closed two fights by exactly
  the right amount, so I am glad it exists, but no turn was ever *about* it.
- **Lynette — Enigmatic Feint's Swirl half never once did anything.** Every
  time I read it, either there was no aura, or swirling would have destroyed an
  aura I was about to react with. I played her three times, always for the
  Block and the performance, never for the printed effect at the top of the
  card. Sayu — Yoohoo Art: Fuuin Dash has the same problem.
- **The Salon was mostly furniture.** I owned one deploy card in a 19-card
  deck. That means the "Performs a member" line on every Companion card read
  *"No member on stage: performs nobody"* for the great majority of my card
  plays — most of a Companion card's printed body was inert most of the time.
  This may be a draft accident rather than a design one (I passed on
  Mademoiselle Crabaletta at the fight-1 reward and on Casting Call in the
  shop), but I want to flag how it *felt*: for three fights the kit's headline
  mechanic was a paragraph of rules text explaining why nothing was happening.

### (c) What I could not understand, or that contradicted its own printed text

Five, in descending order of how much they cost me.

1. **The Spotlight relic says "once", and means "once per combat."** Ethereal
   Spotlight reads *"It does nothing once your Companion cards are lit."* I
   played fight 1 believing I had bought a permanent upgrade — I even weighed
   whether to spend 2 Encore on it "while I only own one Companion card", which
   is a calculation that only makes sense if the buff is permanent. Fight 2
   opened with Chevreuse printing 7 again. Nothing on the relic, and nothing on
   the card, says the lighting is per combat. This is the one place where the
   printed text actively misled me.

2. **Freminet — Pressurized Floe: Backstroke's Block does not obey either the
   Spotlight or the upgrade.** The card reads `Deal 10 damage. Gain 6 Block`.
   Under the Spotlight, whose text promises *"Their printed damage **and Block**
   are 50% stronger"*, it printed `Deal 15 damage. Gain 6 Block`. Then Blessing
   of the Forge upgraded it and it printed `Deal 18 damage. Gain 6 Block`. The
   damage moved twice; the Block never moved at all. On the same screen,
   Lynette — Enigmatic Feint's Block *did* move (5 → 7 lit, → 10 upgraded), so
   this is not a rule about Block in general. I think this is a defect.

3. **Encore vanishes from the status block when it is 0.** The header prints
   `- Encore: 5` when the pool has something in it and prints **no Encore row
   at all** when it is empty. Twice I had to reason "the row is gone, so it
   must be zero, so my member will perform at three-quarters" — inferring a
   load-bearing number from the absence of a line. Fanfare behaves the same way
   (it appeared only once a member had performed). A zero is information; a
   missing row is a puzzle.

4. **Skittish's ordering is not printed anywhere.** *"The first time Phantasmal
   Gardener is hit each turn, it gains 6 Block"* does not say whether the Block
   arrives in time to blunt the hit that triggered it. Against an elite where
   that is the difference between a 27-damage vaporize and a 21-damage one, I
   had to burn a card to learn the answer (it does not; the first hit lands in
   full). Not the kit's card, but the kit's screens are otherwise so good at
   printing the arithmetic that this stood out.

5. **"Salon Member numbers" is used before it is defined.** Grand Salon
   ("Salon Member numbers are 1 higher") was offered to me as the *first* card
   reward of the run, on a screen whose glossary defined Companion and
   Vulnerable and said nothing about Salon Members. I had not yet seen a
   member, a Salon, or a number. I passed on it partly because I could not
   price it. By the time the Salon glossary appeared — attached to Salon Début
   in fight 1, and it is very thorough — the reward was gone.

One thing I could not resolve either way, so I flag it rather than assert it:
I could not confirm that Companion cards added mid-combat by An Invitation get
lit by a Spotlight that is already up. Sayu arrived before I lit the Spotlight
in fight 4 and printed 6, where 9 would have been the lit number if her base is
6 — but I never saw her unlit base, so 6 is equally consistent with "she is lit
and her base is 4". Shinobu did visibly go 4 → 6. I mention it because I made a
play-order decision (Invitation before Spotlight, twice) on an assumption I
never verified.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted: Regal Bearing** (1: gain 3 Block, apply 1 Weak). Three Block
  is not a turn, and one Weak on one enemy for one turn is not either. It was
  in my hand in every fight and I played it zero times. Lynette — Enigmatic
  Feint is a close second on the *printed effect* alone, but she survives on
  her Block and her performance, so she never felt dead the way Regal Bearing
  did.
- **Happiest to draw: Chevreuse — Interdiction Fire.** It is the card that
  three separate systems all pay off through — the Spotlight makes it bigger,
  an aura makes it multiply, and the Salon makes it hit twice — and, crucially,
  it *tells you* which of those are live right now, on its own face, before you
  commit. `Deal 12 damage` + `Reaction preview: Vaporize` + `Playing this
  performs Mademoiselle Crabaletta` is three sentences that turn a 1-cost
  common into a decision.

### (e) Did the first turn of the first fight already present a decision?

**Yes, but a thin one, and not the kit's decision.** I had a real choice — hold
Ethereal Spotlight or spend my entire 2-Encore pool on it with only one
Companion card in the deck — and I got it wrong, in the sense that I deferred
it for a reason (the buff is permanent, so I can wait) that turned out to be
false. So the first turn asked me something real.

But everything that makes this kit *itself* was unreachable on turn 1 of fight
1. The stage was empty, so both Companion cards in my hand printed "performs
nobody"; no enemy had an aura, so Lynette's Swirl was dead text and no reaction
preview existed; Fanfare was not on the screen. What I actually did on turn 1
was Vulnerable-then-attack-then-block, which is the opening turn of any deck in
any Spire. **The kit's first real turn was turn 2 of fight 1** — Aria into
Salon Début into a vaporizing Chevreuse that performed the member I had just
deployed. That turn is very good. It is one turn later than it should be, and
it needed me to have drawn my single copy of Salon Début.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed ones, all of them my own scratch or
shell plumbing:

- `mkdir -p …/scratchpad/lane1` and `mkdir -p …/review/qa/furina-reframe-round-10-2026-09-04` (created the scratch directory and the record's directory).
- `echo "acts=0 | Neow screen seen" >> …/scratchpad/lane1/notes.txt` and `cat` of that same file — one scratch note, written once at the start. I kept my action count in-context afterwards rather than in the file.
- `sed -n`, `grep`, `head`, `tail` used as filters on the output of `observe`, to re-read one block of a screen without reprinting the whole page. I used non-overlapping `sed -n` ranges throughout, per the brief.
- `for i in 1 2 3 4; do … done` around `observe`, four times, to retry the bridge after it stopped answering. The loop wrapped nothing but `observe`.
- Shell chaining with `&&`, `;` and `>/dev/null` around `act`/`observe` calls. The `&&` form caused the one swallowed `end turn` described in Fight 4 turn 3; I switched to `;` after that.

Tools used: **Bash** (for every game command and the scratch/filter work above)
and **Write**, once, for this file. I did not run `harness state`, `scenario`,
`staged_turn`, `soak`, or any other understudy subcommand; I did not read
`godot.log` or any other log; I did not open a YAML sheet, C# source, doc,
packet, review file, or any other seat's record; I did not tear down the lane.
