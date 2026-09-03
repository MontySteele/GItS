# Control round — base-game Ironclad, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, CONTROL round (base Ironclad), run 1, act 1
- **Lane:** 1
- **Seed:** `MYYWMW9VDSV0`
- **Character:** Ironclad (base game, not a mod character)
- **Ascension:** 0
- **Act:** 1. The map named the act boss on the first map screen: **Waterfall Giant**.
- **Actions accepted:** 173 accepted `act` calls (cap 250). 2 refusals, never consecutive.
- **Termination reason:** **Not a budget stop.** The run ended in death on floor 17. I killed the
  Waterfall Giant, but its printed `Steam Eruption` rider resolved as a **Death Blow for 33** and I
  was at 12 HP with 10 block. The next `end turn` returned `TOOL-BLOCKED: game_over` — "the run is
  over; there is nothing left to play. The run ended on floor 17." Per the brief I stopped there and
  did not go looking for another way through.
- **HP trajectory:** 80/80 start → 66 (fight 1) → 53 (fight 2) → 53 (fight 3) → **rest to 80** →
  72 (fight 4) → 51 (elite) → **rest to 80** → 12 (boss, turn 8) → **dead** to the 33 Death Blow.
  Burning Blood healed 6 after each combat; the two rests are the only other healing I saw.
- **Gold at end:** 5 (I spent 178 of 183 at the only shop).
- **Potions held at end:** none. Powdered Demise spent in the elite, Flex Potion and Glowwater
  Potion spent in the boss fight.
- **Deck at end (16 cards):** 4× Strike, Strike+, 4× Defend, Bash+, 2× Pommel Strike,
  Unrelenting (Steady), Headbutt, Rampage, Tremble. Spoils Map was removed at the shop.
- **Relics at end:** Burning Blood, Fishing Rod, Red Mask, Bone Tea, Juzu Bracelet.

**Neow pick: Fishing Rod** ("Every 3 normal combats, Upgrade a random card in your Deck").
Why: it was the only one of the three whose text I could actually read end-to-end. "Neow's Torment"
adds a card called *Neow's Fury* whose text is never printed, and "Cursed Pearl" pays 333 gold to
"Receive Greed" — *Greed* is likewise never printed anywhere. Blind, I took the one option with no
unnamed component.

---

## Fight 1 — Seapunk, 46 HP

**Turn 1.** Hand: 2× Strike, 3× Defend, 3 energy. Enemy intent printed "Attack for 11 damage."
Played Strike, Strike, Defend (12 damage, 5 block, took 6).
*Rejected:* triple Defend — 15 block would have zeroed the 11, but it deals nothing and buys a
fourth turn of taking 11. Trading 6 HP for 12 damage is the better side of that.

**Turn 2.** Drew Bash ("Deal 8 damage. Apply 2 Vulnerable"). Intent 2×4.
Played **Bash first, then Strike** — 17 damage, not 14.
*Rejected:* Strike-then-Bash, and Bash+Defend. This was the first turn with a real decision, and the
decision was **ordering**: Bash's Vulnerable applies inside the same turn, so the Strike after it hit
for 9 instead of 6. The screen makes that inferable (Vulnerable's keyword text is printed inline
under the card) but never says it outright.

**Turn 3.** Enemy at 17 with Vulnerable 1, intent "Empower (Buff) … and also: Defensive (Defend)".
Played Strike, Strike (9 each) — dead.
*Rejected:* nothing. The enemy was not attacking, so my three Defends were dead cards and 27
potential damage into 17 HP was not a choice. **A turn with no rejected alternative.**

**Refusal #1 (a finding).** I had batched a third Strike. It came back:
`"you are not in a battle. Forms that resolve here: choose "<reward>" …"`. Correct behaviour, and the
refusal listed the working forms — but it is the first sign of the batching hazard that later cost me
a card (see the elite).

**Reward legibility problem.** The screen offered `17 Gold`, `Powdered Demise`, and a card. Claiming
the potion printed only `"text": "Powdered Demise"` — **the potion's name as its own description.**
I did not learn what it did until it appeared in the Potions block of the next combat screen
("Enemy loses 9 HP at the end of each of its turns"). Taking it was therefore not a decision; it was
a free pick of an unknown.

**Card pick: Pommel Strike** (9 damage, draw 1, cost 1) over Perfected Strike and Rupture.
Perfected Strike scales off cards containing "Strike" and costs 2; Rupture wants self-damage I had no
source of. Pommel Strike is strictly better than the Strike it competes with.

---

## Fight 2 — Sludge Spinner, 39 HP

**Turn 1.** Intent: "Attack for 8" **and also** "Strategic (Debuff)". Played 3× Strike (18 damage),
took 8.
*Rejected:* 2 Strike + Defend. Reason: the printed Debuff intent told me my *later* turns would be
worse than this one, so front-loading damage while unafflicted is worth more than 5 block. That is a
real decision and the screen gave me exactly what I needed to make it.

**Turn 2 — the best legibility moment of the run.** The debuff was Weak, and **every card in my hand
re-printed its own reduced number**: Strike now read "Deal 4 damage", Bash "Deal 6", Pommel Strike
"Deal 6". I never had to do the 25% arithmetic myself. This is the single thing the interface does
best, and it held for Vulnerable, Frail and Strength later too.

Played Pommel Strike first specifically to see its draw before committing the rest, then Bash (2
energy) for 6 damage + 2 Vulnerable.
*Rejected:* 2 Strike for 8 more damage now. I took Bash because Vulnerable multiplies the *whole*
next turn, and the printed enemy HP (15 after Pommel) made a next-turn kill arithmetic-certain with
it and uncertain without.

**Turn 3.** Enemy at 9 with Vulnerable 1. Pommel Strike alone = 13. Dead.
*Rejected:* nothing. **No decision.**

**Card pick: Unrelenting** (2 energy, "Deal 14 damage. The next Attack you play costs 0") over
Armaments and a second Pommel Strike. The rider makes it ~23 damage for 2 energy. This turned out to
be the correct read — Unrelenting carried the whole run.

---

## Fight 3 — Corpse Slug 26 HP + Corpse Slug 25 HP

**This is the best-designed fight I played, and the reason is one line of printed text.**

Both slugs carried `Ravenous 4 — When an enemy dies, Corpse Slug immediately eats it, becoming
Stunned and gaining 4 Strength.`

**Turn 1.** Only 6 damage incoming. Played Pommel Strike + Strike into slug 1, Strike into slug 2 —
deliberately spreading, because my first read of Ravenous was "killing one buffs the other, so try to
kill both on the same turn and deny the meal." No block, since 6 was cheap.

**Turn 2 — where the fight actually happened.** Slugs at 11 and 19, I had Unrelenting (14 + free
attack) and 3 energy. Two lines:

- **Denial line:** Unrelenting into slug 2 (19→5), free Strike into slug 1 (11→5). Both alive at 5,
  neither eats, kill both next turn. Cost: take 14 that turn.
- **Kill line:** Unrelenting kills slug 1 outright; slug 2 eats it, gains 4 Strength, is Stunned.

I re-read the card and noticed the word **"immediately."** The eat happens on my turn, so the Stun
lands *before* the enemy turn — meaning the "punishment" for killing one **eats the incoming turn
entirely.** I took the kill line and **took 0 damage that turn** (HP 53 before, 53 after; confirmed
on the next screen). The clever-looking denial line would have cost 11 HP for nothing.

This is the one fight where reading the printed text carefully changed the play and the screen and
the outcome agreed completely. The rejected alternative was real, was tempting, and was wrong.

**Turn 3.** Slug at 13 with Strength 4. Bash then Strike (8 + 9) — dead.

**Card pick: Headbutt** (9 damage + put a card from Discard on top of Draw) over Ashen Strike and
Vicious. Ashen Strike scales off an exhaust pile I had no way to fill; Vicious draws off Vulnerable I
apply roughly once per shuffle. Headbutt's tutor later became my most-used tool in the boss fight.

---

## Interlude — events, and the gold problem

Four events, and a pattern worth stating plainly.

- **Drowning Beacon:** "Bottle — Procure Glowwater Potion" vs "Climb — Obtain Fresnel Lens. Lose 13
  Max HP." Neither item's effect is printed. I took the free one purely because 13 Max HP is a
  printed cost and *Fresnel Lens* is not a printed anything.
- **The Legends Were True:** "Nab the Map — Receive the Spoils Map" (free) vs 8 HP for a random
  potion. I took the free one. **This was a trap I could not see.** *Spoils Map* turned out to be an
  **unplayable card shuffled into my deck** ("Unplayable. Marks a site of 600 extra Gold in the next
  Act"). Nothing on the event screen said I was being handed a card, let alone a dead one. It clogged
  my hand twice during the elite and I eventually paid 75 gold to remove it.
- **Sunken Treasury:** 54 gold vs "303 Gold. Receive Greed." *Greed* is still never printed — second
  time this run. Having just been burned by the last unlabeled freebie, I took the 54.
- **Waterlogged Scriptorium:** "Bloody Ink — Gain 6 Max HP" (free) vs 55 gold or 99 gold to "Enchant
  a card with **Steady**." *Steady* is not printed on this screen either. I paid the 55 partly as a
  tester, to find out what it was. **Steady is revealed only inside the picker**, which does a genuine
  before/after preview: `Unrelenting (Steady) — Retain. Deal 14 damage…` plus `*Steady* — This card
  gains Retain.` The preview is excellent. The purchase screen that asks you to pay for it is not.

**The gold defect.** At the Tea Master I reasoned I had 39 gold and could afford only the strictly-bad
free option ("shuffle 2 Dazed into your Draw Pile"). I tried the 50-gold Bone Tea expecting a refusal
**and it went through.** I had far more gold than I could account for, because **no screen in this run
ever printed my gold total until I reached the shop** ("You have 183 gold"). Rewards print gold
*gains*; events print gold *prices*; nothing prints the *balance*. I mispriced at least two decisions
on that — I declined the 303-gold chest and skipped the 99-gold double enchant while holding 138.

**Rest sites.** Rested at 59/80 (heal is 30% of Max HP = 24, so resting below ~56 is the efficient
window). Later took Smith at 80/80 where the heal was worthless. The upgrade screen carried its own
oddity: a **"Not on this list, and why"** block naming `Spoils Map` and `Strike` as
*"on the screen's list nowhere, and nothing on the feed says why"*, plus a note that the list is my
deck "as it stood in the last fight (floor 6)". The missing Strike was the copy Fishing Rod had
silently upgraded — I only confirmed that two floors later when a different picker showed me
`Strike+`. **I upgraded Bash without being able to see my own current deck.** (I picked Bash because
its Vulnerable multiplies every other attack I own; Bash+ = 10 damage / 3 Vulnerable, which was
correct.)

Also: `choose` on these pickers **toggles** rather than commits, and the screen says
"Confirm is not available" until after you toggle, then flips to "Confirm is available". Fine once
learned, mildly alarming the first time.

---

## Fight 4 — Calcified Cultist 39 HP + Seapunk 46 HP

Bone Tea fired and upgraded my whole starting hand: **Unrelenting+ = "Retain. Deal 20 damage. The
next Attack you play costs 0."** Red Mask had already applied Weak 1 to both enemies.

**Turn 1.** Only 6 damage incoming after Weak. Played Unrelenting+ (20) → free Strike+ (9) →
Defend+ (8 block). **29 damage, 0 taken.**
*Rejected:* holding Unrelenting+ behind its Retain and triple-blocking. With 85 HP of enemies on the
board and 6 damage incoming, spending a turn on defence is strictly worse.

**Turn 2.** Killed the Cultist (Empower had resolved into `Ritual 2 — At the end of its turn, gains 2
Strength`, which compounds) with Pommel Strike + Strike, then spent the last energy on **Headbutt into
Seapunk specifically to put Unrelenting+ back on top of my draw pile.**
*Rejected:* Defend for 5 block. The tutor was worth ~20 damage next turn; 5 block was worth 5.

**Turn 3.** The tutor worked — Unrelenting+ came straight back. Seapunk was blocking and buffing, so
zero incoming. Max damage was 35 against its 37 HP: Unrelenting+ (20) → free Strike+ (9) → Strike (6).
Left it on 2.
*Rejected:* spending Powdered Demise to close a 2 HP gap. With an elite two floors away and no
incoming damage that turn, the potion was worth more later. (It was — see the elite.)

**Turn 4.** Seapunk at 2 behind 7 Block. Pommel Strike's 9 is exactly lethal. **No decision.**

**Card pick: a second Pommel Strike**, over Forgotten Ritual (1 energy → gain 3, Exhaust) and Taunt.
*In hindsight this was probably my worst pick of the run.* Forgotten Ritual is a once-per-combat +2
energy, and the boss fight I lost was lost by roughly one turn of damage. I chose consistency over
burst against a boss I had not seen.

---

## Fight 5 (Elite) — four Phantasmal Gardeners, 29 / 30 / 31 / 26 HP (116 total)

Each carried `Skittish 6 — The first time Phantasmal Gardener is hit each turn, it gains 6 Block.`

That rule makes spreading damage actively bad: every new target you touch taxes you 6. So the whole
fight is one repeated decision — **focus one target and pay the tax once, or block and wait for a
hand big enough to be worth paying it.**

**Turn 1.** 8 damage incoming, so no block. Focused Gardener (4) (lowest HP, and the one buffing):
Unrelenting (14) + free Pommel Strike (9) + Strike (6) = 29 raw → **23 net, exactly 29 − 6.** Left it
on 3/26.
*Rejected:* splitting across two targets, which would have cost 12 to Skittish instead of 6.

**Turn 2.** Pommel Strike (9 − 6 block = 3) killed Gardener (4) exactly. Then, with a weak remainder
(2× Strike = 12 raw = 6 net after the tax), I **used Powdered Demise on Gardener (3)** and played
2× Defend for 10 block against exactly 10 incoming — **took 0.**
*Rejected:* 2 Strikes for 6 net damage while taking 10. Under Skittish, small attacks are worth less
than the block they displace; the right shape is *block on weak hands, burst on strong ones.*
Powdered Demise landed as a permanent `Demise 9 — At the end of Phantasmal Gardener's turn, it loses
9 HP` and ticked every single turn thereafter, **ignoring Skittish block entirely.** It was the best
card I played all fight and I only had it because I declined to waste it in fight 4.

**Turn 3.** Strong hand. Bash+ **first** (10 damage, 3 Vulnerable) so the Vulnerable multiplied the
Headbutt after it (9 × 1.5 = 13). 17 net into Gardener (1). Headbutt's tutor gave **no prompt** this
time — there was only one card in the discard, so it auto-chose. (Last time it opened a picker. The
inconsistency is minor but I noticed it.)

**Turn 4 — my mistake, and it is worth writing down properly.**

I batched two commands: `play "Pommel Strike" on "Phantasmal Gardener (1)"` then
`play "Strike" on "Phantasmal Gardener (1)"`. I expected Pommel (13 with Vulnerable, −6 Skittish = 7
net) to leave Gardener (1) on 5, and the Strike to finish it.

**My model of Skittish was wrong.** The block is granted *after* the first hit resolves, not before —
so Pommel Strike's 13 landed **in full** against 12 HP and killed it outright. The survivors were then
**renumbered**, and my second command hit a completely different enemy — the 30 HP gardener I had not
touched, which took 6 and promptly gained its own 6 Block. I wasted a card and opened a second
Skittish tax in the same turn.

The tool does warn about renumbering, but the warning it prints is about **cards in hand** ("`(1)`
names a different copy once one of them leaves your hand"). Nothing on the screen says the same
re-counting applies to **enemies between two `act` calls.** It does. I should have observed between
the two commands; the interface makes batching feel safe and it is not.

Two useful facts fell out of the error: (a) the net damage over a turn is still `raw − 6`, so
ordering does not change totals, but (b) **a first hit large enough to kill ignores Skittish
completely**, which is why single big hits beat two medium ones here.

**Turns 5–6.** Recovered by using the printed numbers properly: struck the Demise-marked gardener down
to 7 so the 9-tick would finish it (it did — killing an enemy with a damage-over-time effect I paid
for two turns earlier was the most satisfying moment of the run). Then on the last gardener I found a
genuine decision: max damage was 23 net against its 24 HP — **one short** — so the kill was going to
take two turns either way. Given that, I swapped the third card from Strike to Defend, because the
extra 6 damage bought nothing while 5 block was real. Finished it next turn with Strike+ (9, first
hit, full).

**Cleared at 51/80.** Rewards: 41 gold, Juzu Bracelet, and a card. The relic again printed **no
effect text on the reward screen** — I did not learn what Juzu Bracelet did ("Regular enemy combats
are no longer encountered in ? rooms") until the relic list of the boss fight, two floors later.

**Card pick: Rampage** ("Deal 10 damage. Increase this card's damage by 5 this combat") over Rupture
and Thunderclap, on the reasoning that the act boss would be a single large target and a 1-cost card
that grows every replay is the best rate available. It ended the run at **30 damage.** Correct pick.

---

## Interlude — the shop

183 gold, and the map showed no further shop, so gold was dead weight. Bought **Tremble** (51: 1
energy, apply 3 Vulnerable, Exhaust), **Flex Potion** (52), and **Card Removal** (75) to cut Spoils
Map. 178 of 183 spent.

*Rejected:* War Paint (154) — it upgrades 2 random **Skills** and my only skills were four Defends;
Fiend Fire, which would have exhausted the hand I needed; Kunai at 274, unaffordable.

Removing Spoils Map over a basic Strike: Strike at least deals 6, Spoils Map is unplayable and had
already cost me two hand slots in the elite.

Then rested 57 → 80 rather than taking a second upgrade. *Rejected:* Smith. Against an unknown boss,
23 HP is close to a full extra turn of survival and an upgrade is worth ~6 damage a play. **Given how
the fight went, this was the wrong call** — I lost the race by about one turn of damage, and
Unrelenting+ (20 vs 14) would have been roughly that. I do not think it was unreasonable blind, but
it was wrong.

---

## Fight 6 (Boss) — Waterfall Giant, 240 HP

**Turn 1.** Intent was Empower only — a free turn. Rampage (10) → Unrelenting (14) → free Pommel
Strike (9) = **33 damage, 0 taken.** Rampage went to 15.
*Rejected:* any block at all. Nothing was incoming.

**Turn 2.** The hidden clock appears: `Steam Eruption 15 — When killed, deals 15 damage at the end of
your next turn.` Weak hand (Strike+, 2× Strike, 2× Defend). Played all three attacks for 21, took 15.
*Rejected:* Defend lines. A 240 HP boss that Empowers **every turn** cannot be out-blocked by four
5-block Defends; the only path is compressing turns.

**Turn 3.** I was Weak (cards re-printed at 4 / 6 / 7). **This is the turn the printed numbers earned
their keep** — because attacking at 75% was bad and Tremble is a *skill*, unaffected by Weak, I spent
the turn on setup: Tremble (3 Vulnerable) + Headbutt (9 × 1.5, tutoring Rampage to the top).
*Rejected:* attacking through Weak for ~15. Also noted Steam Eruption had grown 15 → 18 → 21: it
scales ~3 per turn, so **the longer I take, the more the kill itself costs me.**

**Turn 4 — the peak.** Intent was **Heal** + Empower: another free turn, with Vulnerable live. Spent
**Flex Potion** (+5 Strength) and dumped: Rampage (15+5)×1.5 = 30, Pommel Strike (9+5)×1.5 = 21,
Strike (6+5)×1.5 = 16. **67 damage in one turn**, 170 → 103, nothing taken. Every one of those
numbers was predictable from the screen beforehand, which is the strongest thing I can say about this
interface.
*Rejected:* saving Flex. A free turn with Vulnerable already up is the best window it will ever get.

**Turn 5.** It healed 10 (103 → 113 — worth stating plainly: **the boss heals, so stalling loses**).
Vulnerable on its last turn. Played Pommel Strike first to see the draw, then Headbutt (tutoring
Rampage) + Strike+ for 39 total.
*Rejected:* tutoring Bash+ to renew Vulnerable instead of Rampage. With Steam Eruption climbing I
judged raw damage now beat a multiplier later. I still think that was right.

**Turns 6–7.** 40 damage (Unrelenting → free Rampage(20) → Strike), then a considered 24. On turn 7 I
worked out the trap explicitly: at 22 HP with the Giant on 34 and Steam Eruption at 30, **I could not
kill it and I could not out-heal the blast** — it grew 3 a turn while I lost 10–15 a turn. So I took
the line that guaranteed the kill and banked the most HP: Headbutt tutoring Rampage (guaranteeing
lethal next turn regardless of the Weak it was about to apply) plus a Defend, rather than four more
points of damage.

**Turn 8.** Rampage (18 after Weak) into 16 HP. **Killed it.**

**And then the screen did something I could not read.** The Giant did not die — it became:

```
Waterfall Giant — HP 999999999/999999999
Intent: Stunned (Stun) — This enemy can't act on its next turn.
Steam Eruption 33 (buff) — When killed, deals 33 damage at the end of your next turn.
```

`HP 999999999/999999999` is a sentinel, not a number a player can act on. The turn after, it
clarified into an honest and rather good piece of text —
`Intent: Death Blow — This creature is trying to take you down with it. It will attack you for 33
damage before being destroyed.` — but for one whole turn the boss was an invulnerable object with a
nine-digit health bar and no stated way to interact with it.

**The last turn.** I needed 22+ block on 12 HP and had one Defend. Used Glowwater Potion — and here
the screen and the outcome disagreed outright:

> **Glowwater Potion — "Exhaust your Hand. Draw 10 cards."**
> After playing it: hand = **4 cards**. Piles printed `0 in the draw pile, 0 discarded, 6 exhausted`.

Four cards, not ten. And the piles account for only 10 cards of a 16-card deck — 4 in hand + 6
exhausted, with draw and discard both empty. **Six cards are unaccounted for on the printed screen.**
I do not know whether the potion under-drew, whether the pile counts are wrong, or both; I only know
the card promised 10 and the screen showed 4.

Played my two Defends (10 block), ended the turn, took the 33, and the tool returned
`TOOL-BLOCKED: game_over — the run ended on floor 17`.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Four stand out, and all four were legible *from the screen alone*:

1. **Corpse Slugs' Ravenous.** Kill one and the survivor eats it — Stunned, +4 Strength. The trade is
   "hand the enemy a permanent buff" against "delete an entire enemy turn," and the word that decides
   it (*immediately*) is printed. I read it, took the kill, and took zero damage. The tempting wrong
   line was fully available.
2. **Skittish 6 on four gardeners.** A tax on breadth. It converts every turn into "is this hand big
   enough to be worth opening a target, or do I block and wait?" — and it makes big single hits
   qualitatively better than two medium ones, which is a genuinely interesting thing for a rule to do.
3. **Steam Eruption on the boss.** A death-blast that grows ~3 per turn is a real clock: it makes
   *winning slowly* into a losing condition, and it is visible from turn 2. I lost to it, and I lost
   fairly — I could see it coming for five turns.
4. **Ordering within a turn.** Bash-before-Strike, Tremble-before-Headbutt, Flex-before-everything.
   The 67-damage turn was entirely a sequencing result.

**(b) What felt automatic, and what never seemed worth playing.**

Roughly a third of my turns had no decision in them: fight 1 turn 3, fight 2 turn 3, fight 4 turn 4,
and every "the enemy is at 9, this card does 9" turn. These cluster at the *ends* of fights — once
the arithmetic is settled the remaining turns are bookkeeping.

Never worth playing: **Spoils Map**, which is unplayable by design and which I was given without being
told it was a card. **Defend** was close behind — 5 block is so far below the curve that against
Skittish it was often the *best* use of energy purely because attacking was worse, which is a strange
thing to be able to say. And the base **Strike** at 6 damage was a card I was always disappointed to
draw by act 1's end.

**(c) What I could not understand, or that contradicted its own printed text.**

- **`HP 999999999/999999999`.** A sentinel value shown to the player as a health total.
- **Glowwater Potion: "Draw 10 cards" drew 4**, and the pile counts afterwards account for 10 of my
  16 cards. Screen and outcome disagree; this is the clearest defect I found.
- **My Skittish model was wrong and the text did not settle it.** "The first time it is hit each turn,
  it gains 6 Block" does not say whether the block applies to that hit. It does not — the first hit
  lands full. I only learned it by killing something I expected to survive, and the lesson arrived as
  a mis-targeted card.
- **Enemies are renumbered between `act` calls**, and the on-screen warning about renumbering talks
  only about cards in hand. This cost me a card in the elite.
- **Named things with no text at the point of decision:** *Greed* (offered twice, never explained),
  *Neow's Fury*, *Fresnel Lens*, *Spoils Map* (an unplayable card, presented as a free reward),
  *Steady* (paid for before its text is visible; the picker's before/after preview is genuinely good
  and arrives one screen too late), and every potion and relic on a reward screen — *Powdered Demise*,
  *Glowwater Potion*, *Juzu Bracelet* all printed as bare names and only became readable in a later
  combat's sidebar.
- **My gold total is never printed outside the shop.** I made two purchase decisions with a number I
  had to reconstruct by arithmetic, and got it wrong — I tried to buy something I expected to be
  refused, and it succeeded.
- Minor: `upgrade` issued immediately after `go` returned `error Rest site room is not open` while
  simultaneously echoing `Took: Smith` — the room had not finished loading. Retrying worked. Also
  `choose` on pickers toggles rather than commits, and "Confirm is not available" flips to available
  only after the toggle.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Spoils Map** — literally unplayable, and I paid 75 gold to delete it.
Happiest: **Unrelenting**. "Deal 14 damage. The next Attack you play costs 0" turns 2 energy into
three cards' worth of a turn, and once it carried Steady (Retain) I could hold it for the turn it
mattered. **Rampage** is the honourable mention — watching a 1-cost card climb 10 → 15 → 20 → 25 → 30
across a boss fight was the most fun thing in my deck, and it landed the killing blow.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, but a thin one.** Hand of 2 Strike / 3 Defend into a printed "Attack for 11": the real choice
was race-vs-turtle (12 damage and take 6, or 15 block and take 0), and it resolves the same way
essentially every time, so it is a decision in form more than in substance. The *first genuinely
interesting* turn was turn 2 of the same fight — drawing Bash and noticing that playing it **before**
the Strike was worth 3 extra damage. That is one turn later than ideal, but it is early.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, always as
`GITS_LANE=1 python -m understudy.blindplay observe` or
`GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run from the repo root with the Bash
tool. I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no other understudy
subcommand.

Commands and tools used outside those two:

- **Bash**, for scratch and for shaping output only:
  - `mkdir -p …/scratchpad/control-seat` and `mkdir -p …/review/qa/control-ironclad-2026-09-04`
  - `cat >> …/scratchpad/control-seat/notes.md <<'EOF' … EOF` — twice, my own notes, no repo content
  - `cd` into the repo root, chained with `&&`, to run the two allowed commands
  - `| tail -N`, `| head -N`, `| sed -n '…p'` piped over the output of `observe`/`act` to re-read
    single blocks (hand, enemies, available commands) instead of reprinting whole screens
  - one `for i in 1 2 3; do … done` loop that issued three identical allowed `act` calls
  - `echo ok`
- **Write**, once, for this record at
  `C:\Users\Monty\Documents\GitHub\GItS\review\qa\control-ironclad-2026-09-04\opus-act1.md`.

I read no YAML sheet, no C# source, no doc, no packet, no other seat's record, and no `review/`
material. Nothing in this record comes from anywhere but the bridge's printed output.
