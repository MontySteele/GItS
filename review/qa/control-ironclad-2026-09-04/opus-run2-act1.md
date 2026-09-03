# Blind seat record — CONTROL Ironclad, lane 2, run 2

## Identity

- **Model / seat:** Claude Opus 5 (`claude-opus-5[1m]`), blind TESTER seat, lane 2.
- **Run:** CONTROL run 2 — base-game Ironclad, no mod kit.
- **Seed:** never printed. No screen the bridge showed me named a seed, so I cannot
  report one.
- **Character:** Ironclad. **Act 1.** The map named the act boss from the first map
  screen onward: **Waterfall Giant**.
- **Actions accepted:** 213 `act` calls (cap 250). No refusals at all — every command
  I issued was accepted. No stalls, no `TOOL-BLOCKED` until the end.
- **Termination:** **Death.** Not a budget stop. I killed the Waterfall Giant on
  round 7 of the boss fight; its corpse's Death Blow hit for 30 at the end of round 8
  against 16 HP and 13 block. `observe` then printed
  `TOOL-BLOCKED: game_over` / "The run ended on floor 17."
- **HP trajectory:** 80 start → 73 → 69 → 66 → 63 → 57 → 41 → 47 → 35 → 41 →
  **rest 65** → 71 → 53 → 41 → 33 → 16 → **rest 46** → 38 → 27 → 26 → 16 → dead.
  Lowest before the boss: 16/80 (end of the second elite).
- **Gold at death:** 11 (I emptied the shop deliberately).
- **Potions held at death:** Explosive Ampoule (unused — it was a damage potion and
  the thing that killed me could not be damaged).
- **Relics at death:** Burning Blood; Hefty Tablet; Venerable Tea Set; Juzu Bracelet;
  Art of War; Anchor.
- **Deck at death (20 cards):** Strike ×5, Defend ×3, Defend+ ×1, Bash, Conflagration,
  Setup Strike, Breakthrough, Shrug It Off ×2, Unrelenting, Fight Me!, Taunt, Tremble,
  Inflame. (Injury was removed at the shop for 75 gold.)

**Neow pick: Hefty Tablet** — "Choose 1 of 3 Rare cards to add to your Deck. Add 1
Injury to your Deck." I took it over +11 max HP because a *chosen* rare is the only
option with a ceiling, and a single unplayable curse is the one drawback money can
delete later (it was: 75 gold at the act-1 shop). From the three rares I took
**Conflagration** ("Deal 2 damage to ALL enemies 4 times") over Fiend Fire and Primal
Force: four separate hits is the best Strength multiplier on offer, and I could not
tell what Primal Force's Giant Rock *cost*, which made its ceiling unreadable.

---

## Fight 1 — Toadpole (22 HP) + Toadpole (21 HP)

**Turn 1.** Hand: Defend ×2, Conflagration, Strike ×2. Played Conflagration (8 to
both), then Strike + Strike into Toadpole (2). *Rejected:* Defend + 2 Strikes. Neither
line killed anything — 20 into the 21 HP one leaves it at 1 — so I compared "6 damage"
against "5 damage blocked", and picked damage because leaving Toadpole (2) at 1 HP
meant a single 1-energy card would finish it next turn instead of two. That saved a
whole energy, which is worth more than 5 block. Took 7.

**Turn 2.** Toadpole (1) had come back with `Thorns 2` and a 3x3 intent. Bash (8, +2
Vulnerable) then Strike (6 × 1.5 = 9) = 17 into its 14 HP — dead before it swung.
*Rejected:* killing the 1 HP one first and Defending. Killing the 14 HP attacker
outright removed 9 incoming damage; killing the 1 HP one removed 0 (it was buffing).
The thorns charged me 4 HP for the two hits, which was the correct price.

**Turn 3.** One Strike into the 1 HP survivor. **No alternative** — one card, one
target, thorns unavoidable. A non-decision.

Reward: 16 gold, and **Setup Strike** ("Deal 7 damage. Gain 3 Strength this turn.")
over Feel No Pain and Headbutt — it is a Conflagration multiplier, and I had no
exhaust deck for Feel No Pain.

---

## Fight 2 — Sludge Spinner (37 HP)

**Turn 1.** Setup Strike (7, +3 Str) → Conflagration → Defend. The order was the whole
decision: Setup Strike *first* made Conflagration read 4 × 5 = 20 instead of 8. 27
damage for 2 energy. *Rejected:* the all-out line (Setup Strike + Conflagration +
Strike = 36) which would have left it at 1 HP and cost me 8 more HP for nothing, since
I could prove from the draw pile's contents that any 5-card draw would finish 10 HP
next turn. It did.

**Turn 2.** Its "Strategic (Debuff)" resolved as **Weak 2** and my Strikes silently
re-printed as `Deal 4 damage`. My guaranteed-kill arithmetic had been built on 6s.
Three Strikes (4 each) = 12 into 10. **The screen and my plan disagreed here and the
screen was right** — but only *after* the fact: the intent line said "intends to apply
a Debuff" and never named which one, so there was no way to price it in advance.

Reward: **Breakthrough** ("Lose 1 HP. Deal 9 damage to ALL enemies") over Feel No Pain
and Sword Boomerang. 9 AoE for 1 energy beats a Strike even single-target.

---

## Fight 3 — Seapunk (46 HP)

**Turn 1.** Bash (8, Vulnerable 2) + Breakthrough (9 × 1.5 = 13). *Rejected:*
Conflagration + Breakthrough + Defend, which dealt 17 and took 6 instead of dealing 21
and taking 11. I paid 5 extra HP for two turns of Vulnerable because Vulnerable
multiplies the *next* turn too, and 50% of a ~20-damage turn is worth more than 5 block.

**Turn 2.** Setup Strike (10) + Strike (13) + Strike (13) = 36 into 25. Dead before it
acted. *Rejected:* blocking anything — a lethal turn makes block worth zero, and I
could verify lethality from the printed numbers before committing.

Reward: **Shrug It Off** over Second Wind and Tremble — 8 block that replaces itself
with a draw is nearly free to include.

---

## Fight 4 — Gremlin Merc (48 HP), with `Surprise 1` and `Thievery 20`

The one fight I would replay differently.

**Turn 1.** Strike, Strike, Defend. *Rejected:* double Defend. Roughly a wash on paper
(each Strike shortens the fight by about as much as a Defend absorbs), so I broke the
tie toward damage because `Thievery 20` charged me 20 gold per landed attack — fewer
turns meant less theft.

**Turn 2.** Shrug It Off (draw) then Bash. *Rejected:* Setup Strike + Strike + Shrug
It Off, which dealt 16 instead of 8. I took the lower number because Vulnerable 2 on a
36 HP enemy is worth ~16 extra damage across two turns, more than the 8 I gave up.

**Turn 3.** Its debuff had landed as **Weak 2**; every card re-printed lower
(Conflagration read `Deal 1 damage to ALL enemies 4 times` — four hits of *one*).
Breakthrough (9) + Strike + Strike = 21. *Rejected:* Conflagration, which Weak had
reduced to near-zero. This is the clearest case in the run of a card's text moving
under a debuff and the display making the right call obvious.

**Turn 4.** Setup Strike + Strike finished it — and `Surprise 1`, printed all fight as
"*Something is off about this creature…*", resolved: **the Merc split into a Sneaky
Gremlin (12 HP) and a Fat Gremlin (13 HP) carrying `Heist 60` — "When killed, returns
all the stolen Gold."** Both stunned. I had 1 energy and only a 2-cost Bash: **a turn
with no legal play and therefore no decision.**

**Turn 5.** Fat Gremlin's intent: **Escape**, with my 60 gold. It had 13 HP. I had two
Strikes at 6 = **12**. I played Shrug It Off purely to dig for the missing point of
damage (8 block was wanted anyway, so it was free to try); it drew a third Strike but
left me at 2 energy — still 12. **One damage short.** I killed Sneaky Gremlin instead
to end the fight cleanly and let 60 gold walk. The fight's reward screen paid no gold.

This is the run's sharpest "screen vs outcome" moment, and the screen was honest
throughout — 13 HP and 6-damage Strikes were both printed. The trap was arithmetic,
not information, and I walked into it by spending energy on Bash a turn earlier.

Reward: **Unrelenting** ("Deal 14 damage. The next Attack you play costs 0") over
Havoc and Ashen Strike.

---

## Fight 5 — Fossil Stalker (53 HP), `Suck 3`

`Suck 3` — "Whenever Fossil Stalker deals unblocked attack damage, it gains 3
Strength" — framed the fight as: block perfectly, or end it fast.

**Turn 1.** Flex Potion (+5 Strength) → Conflagration → Strike → Strike = **50 damage
in one turn** (Conflagration alone was 4 × 7 = 28). *Rejected:* the defensive line —
Ship in a Bottle + Defend for 15 block, fully denying the Strength gain, then grinding
53 HP down over four turns. I chose the race: 50 of 53 in one turn meant it got exactly
one attack off, and one Strength gain on a corpse is free. Took 12.

**Turn 2.** One Strike into 3 HP. No decision.

I mention this because it is the run's best turn and it came entirely from *stacking a
temporary Strength source onto a four-hit card*. That interaction is the Ironclad's
real engine here, and nothing on any screen taught it to me — I inferred it from
Setup Strike in fight 2 and then went looking for it.

Reward: **Fight Me!** ("Deal 5 damage twice. Gain 3 Strength. The enemy gains 1
Strength") over Perfected Strike and Burning Pact — permanent Strength for the long
elite/boss fights ahead.

---

## Fight 6 — Two-Tailed Rat ×3 (20 / 18 / 17 HP)

**Turn 1.** Unrelenting into Rat 1 (14), then the **free** Setup Strike finished it
(7 into 6), then Shrug It Off blocked the survivor's 8 exactly. Took 0. *Rejected:*
killing the 17 HP rat instead — same energy, same kill, but killing the 20 HP one
removes more total HP from the board for identical damage. The genuine choice was
which rat, and it turned on a comparison of remaining board HP (35 vs 38) against
incoming (8 vs 6).

**Turn 2.** Frail 1 on me (Defends re-printed as `Gain 3 Block`). Conflagration (8 to
both) + Strike + Strike killed the attacking rat before it swung. Took 0.
*Rejected:* dumping into the 17 HP rat — but only the *attacker* dying prevents damage.

**Turn 3.** Two Strikes into 9 HP. No decision.

Reward: **Taunt** ("Gain 6 Block. Apply 1 Vulnerable") over Perfected Strike and Stoke.
6 block *plus* a damage multiplier for one energy beats the Defends it competes with.

Treasure: **Venerable Tea Set**.

---

## Fight 7 — ELITE: Phantasmal Gardener ×4 (26 / 29 / 30 / 31 = 116 HP), `Skittish 6`

`Skittish 6` — "The first time Phantasmal Gardener is hit each turn, it gains 6 Block."
**I did not know whether the block landed before or after the triggering hit, and the
text does not say.** So I spent one Strike as an experiment: 26 → 20 HP *and* Block 6.
Damage first, block after. That single test rewrote the whole fight — it meant
Conflagration (four hits of 2) would deal 2 and then be eaten, while one big hit lands
in full. **Best decision I made all run, and it was forced on me by ambiguous text.**

**Turn 1 (rest of).** Ship in a Bottle (10 block now, 10 next turn) + two spread
Strikes. *Rejected:* focusing both Strikes on one Gardener, which the Skittish rule
would have reduced to 6 real damage instead of 12. Took 5 of 15.

**Turn 2.** **Taunt first** (Vulnerable), *then* Unrelenting — 14 × 1.5 = 21 into 20 HP,
an exact kill that Unrelenting alone could not reach. *Rejected:* Unrelenting first
(14, leaving 6 HP behind a fresh 6 block = unkillable that turn). Then Unrelenting's
free attack made **Bash** cost 0, so I took the 8 + Vulnerable over a 6-damage Strike.
Blocked to 16 vs 17 incoming.

Here the display bit: killing Gardener (1) **renumbered the survivors**, so
`Phantasmal Gardener (1)` now named a different creature than it had thirty seconds
earlier. The bridge warns about this for cards; for enemies it is a live hazard.

**Turn 3.** Setup Strike into the Vulnerable one (10), then a Strength-boosted
Breakthrough (12 base × 1.5 = 18) killed it *through* its fresh 6 block while also
putting 12 into the other two. Shrug It Off blocked the rest. *Rejected:* Breakthrough
first — 9 unboosted would have left it alive. Sequencing again.

**Turn 4.** Setup Strike (7 → 5 HP + 6 block) then Bash (11 − 6 = 5) for an exact kill.
*Rejected:* Setup Strike + Strike, which arrives at 2 HP and lets a ramping enemy live.

**Turns 5–6.** Taunt + Breakthrough + Strike on its buff turn (free window), then one
Strike into 3 HP.

Cost: 18 HP and a potion. Rewards: 35 gold, Vulnerable Potion, **Juzu Bracelet**,
**Tremble**.

---

## Fight 8 — Calcified Cultist (41) + Seapunk (45)

**Turn 1.** Bash into the Cultist (Vulnerable 2) + Breakthrough (13 to it, 9 to the
Seapunk). *Rejected:* Breakthrough + 2 Strikes — identical 30 total, but Bash leaves
lingering Vulnerable. Then the Cultist revealed `Ritual 2` ("At the end of its turn,
gains 2 Strength"), which retroactively justified focusing it.

**Turn 2.** Two Vulnerable Strikes (9 each) into the Cultist + a Defend. 18 into 20 —
**two short again**, leaving it at 2. *Rejected:* double Defend for 7 fewer damage
taken; I paid 5 HP to guarantee the ramping enemy died next turn rather than at higher
Strength.

**Turn 3.** The Seapunk was blocking *on its own turn*, so damage now was unblocked:
Setup Strike into the Seapunk (7), Unrelenting into the Seapunk (17 with Strength),
then the **free** attack killed the 2 HP Cultist. Three targets, one turn, 0 damage
taken. *Rejected:* killing the Cultist first with a paid card, which wastes the free
attack on a 2 HP target.

**Turn 4.** Seapunk at 12 behind 7 block. I played Fight Me! and **stopped to observe**
rather than assume: it read `Deal 8 damage twice`, stripped the block, left 9 HP, and
re-printed Conflagration as `Deal 5 damage to ALL enemies 4 times`. Then Conflagration
for 20. *Rejected:* Tremble — I refused to spend the boss's Vulnerable card on a
trash fight.

Reward: a second **Shrug It Off**.

Event, Endless Conveyor: paid 40 gold for a random upgrade (it hit a **Defend →
Defend+**), then **left** rather than buy 10 HP for 40 gold with two rest sites still
on the path. Held ~184 gold for the shop.

---

## Fight 9 — ELITE: Skulking Colony (75 HP), `Hardened Shell 20`

"Skulking Colony cannot lose more than 20 HP each turn." This is the most interesting
rule in the run: it makes excess damage *worthless* and therefore converts every
surplus energy into a defensive decision. It also sets a hard floor of four turns, and
at 41 HP against a 14-damage attacker I could not afford four turns of full hits.

**Turn 1.** Taunt (Vulnerable + 6 block) then Bash (12). *Rejected:* pure blocking,
which loses the attrition race outright against a 75 HP wall.

**Turn 2.** Held Unrelenting and reached the cap with the *cheapest* cards instead:
Setup Strike (10) + Strike (13) = 23, capped to 20, for **2 energy**. The shell counter
then re-printed as `Hardened Shell 0` — genuinely good feedback, it tells you exactly
how much allowance is left. My third energy was dead (all-attack hand, no block).
*Rejected:* Unrelenting for the same 20 — spending a 2-cost bomb to hit a cap two
1-costs already reach is pure waste.

**Turn 3.** Conflagration (12 under Vulnerable) left the shell at 8; one Strike (9)
filled it; Defend+ blocked 8 of 9. *Rejected:* Breakthrough for the same job — it costs
1 HP and Conflagration doesn't, and at 19 HP that mattered.

**Turn 4 — the turn the fight turned on.** 18 HP, exactly 18 incoming (9x2), enemy at
23 with a 20 cap, so it **could not be killed that turn**. Both Shrug It Offs (16
block), then the real choice for the last energy: Defend (5 more block, take 0, enemy
stays at 23) versus **Strike** (take 2, enemy to **17**). I took the 2 damage, because
23 is above the cap and 17 is below it — putting it under 20 meant next turn it would
die *before acting*. *Rejected:* the safer 21-block turn, which buys 2 HP now and pays
another full 18-damage round later.

**Turn 5.** Unrelenting (14) + its free Strike (6) = exactly 20 into 17. Dead before
it swung, at 16 HP.

Rewards: 45 gold, Explosive Ampoule, **Art of War**, **Inflame**.

Shop (311 gold): **Card Removal 75** (deleted Injury), **Anchor 174** ("Start each
combat with 10 Block"), **Weak Potion 51**. Left with 11 gold. Then rested 22 → 46,
which also armed Venerable Tea Set for +2 energy on the boss's first turn.

---

## Fight 10 — BOSS: Waterfall Giant (240 HP)

Opened with 5 energy (Tea Set) and 10 block (Anchor).

**Turn 1.** It buffs — a free window. Shrug It Off (for the draw), Unrelenting (14) +
free Strike (6) = 20. *Rejected:* holding for Art of War's +1 energy; 20 damage now
beats 1 energy later.

**Turn 2.** `Steam Eruption 15` appeared: "**When killed, deals 15 damage at the end of
your next turn.**" I read it, understood it, and wrote down that I would need ~16 HP or
block in hand at the moment of the kill. Played Fight Me! (10, **+3 permanent
Strength**, +1 Strength to it) + Shrug It Off. *Rejected:* Tremble + Fight Me! for 4
more damage and 8 less block — at 46 HP against a 15-per-turn boss I bought the block.

**Turn 3.** Weak on me, so a poor damage turn — which made it the right turn for a
*power*. Inflame (+2 Str, unaffected by Weak) → Setup Strike (+3 more) → Conflagration
at 10 per hit = **37 damage**. *Rejected:* skipping Inflame for 3 more damage now;
+2 permanent Strength is +8 per future Conflagration.

**Turn 4.** It **healed** (141 → 151) on a no-attack turn. Vulnerable Potion (3 turns)
+ two Strikes (16 each) + Taunt, which stacked Vulnerable to **4**. *Rejected:*
Explosive Ampoule — I held it as a finisher, which turned out to be the wrong instinct
for reasons below.

**Turn 5.** It swung for **21** into my 27 HP. Weak Potion cut it to 15; two Shrug It
Offs made 16 block; **took 0**; Breakthrough for 21. This is the turn the kit felt
best — three resources combining to erase a boss hit entirely.

**Turn 6.** The payoff turn: Setup Strike (18) → Conflagration at 15 **per hit** = 60
→ Strike (21). **99 damage in one turn**, 130 → 31.

**Turn 7.** Two Strikes at 16 = 32 into 31. **The Waterfall Giant died.** Its HP then
re-printed as `999999999/999999999`, Stunned, still carrying `Steam Eruption 30`.

**Turn 8 — the kill that killed me.** Intent: `Death Blow — 30 damage`. I had 16 HP and
3 energy, and needed 15 block. My hand held exactly one block card. Shrug It Off (8)
drew a Strike, not block; Defend added 5. **13 block against 30.** 17 damage into 16 HP.

Dead on floor 17, having killed the boss.

The mechanic was fully disclosed — Steam Eruption was printed from round 2 and visibly
grew +3 every round (15 → 18 → 21 → 24 → 27 → 30). What I did not price correctly is
that **it scales with fight length, so every turn I spent blocking made my eventual
victory more lethal**, and that the block I could raise on the single turn between the
kill and the blow was capped by what a 5-card draw happened to contain. I read the
warning, planned for it two turns out, and still lost to it because the answer was a
draw I did not get. That is the finding, and I am not dressing it up: at 16 HP the
correct play was probably to *stop attacking on round 7*, spend that turn on block, and
kill on round 8 — but Steam Eruption growing +3/turn punishes that too. I am not sure
the fight was winnable from 46 HP with this deck.

---

## The kit, after 10 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three kinds recurred, and all three were genuine:

1. **Sequencing temporary Strength into multi-hit cards.** Setup Strike → Conflagration
   is a different card than Conflagration → Setup Strike (20 vs 8 in fight 2; 60 vs 28
   at the boss). Same energy, same cards, triple the output. Likewise Taunt → Unrelenting
   converted a non-kill into an exact kill. This is the Ironclad's best decision space
   here and it is entirely player-side knowledge — no screen hints at it.
2. **Damage versus block, priced against fight length.** Almost every turn I could
   compute both sides: "6 damage shortens the fight by X" against "5 block saves 5".
   The interesting cases were where they came apart — fight 4 turn 2 (took 8 fewer
   damage to gain 2 turns of Vulnerable), fight 9 turn 4 (took 2 *extra* damage to push
   the enemy under a cap).
3. **Enemy rules that invert normal play.** `Skittish 6` made my best AoE card nearly
   worthless and single big hits correct. `Hardened Shell 20` made surplus damage
   worthless and turned spare energy into a defensive resource, and created the sharpest
   decision of the run (block for 2 HP, or damage to cross a threshold). `Suck 3` made
   speed a defensive stat. These are the fights I would call well-designed.

Kill-target selection was also real whenever enemies differed — which rat, which
Gardener — and it turned on comparing board HP against incoming damage, not on gut.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend.** The vanilla cards decided nothing; on all-Strike hands the
  "decision" was only which target. Turn 3 of fight 1, turn 2 of fight 3, turn 3 of
  fight 6 and several others were single-legal-line turns.
- **Conflagration after any Strength card** became automatic once I understood it —
  correct, but not a choice.
- **Injury** was never playable by definition; it cost me 75 gold to delete.
- **Conflagration against block or Weak** was the one card that swung between "best in
  deck" (60 damage) and "unplayable" (four hits of 1), which is more interesting than
  a flat card but meant several draws were dead on arrival.
- **Fight 4 turn 4** had literally no legal play (1 energy, cheapest card cost 2).

**(c) What I could not understand, or that contradicted its own printed text.**

- **`Surprise 1 — "Something is off about this creature…"`** told me nothing. It
  resolved as a two-body split on death. Deliberate mystery is defensible, but it made
  turn-4 planning guesswork and I had no way to know a `Heist 60` gold-carrier was
  about to appear with an Escape intent.
- **`Skittish 6` does not say whether the block lands before or after the triggering
  hit** — the difference between a hard fight and an impossible one. I had to burn a
  card to find out.
- **Unnamed debuff intents.** "Strategic (Debuff) — This enemy intends to apply a
  Debuff to you" twice broke damage plans I had built on unmodified numbers (Weak in
  fights 2 and 4). The intent tells you a debuff is coming but not which, so it cannot
  be priced.
- **Raw asset filenames leaked into card and relic text:** Unrelenting's reward-screen
  text printed `The next Attack you play costs 0 [ironclad_energy_icon.png]`, and
  Venerable Tea Set printed `[ironclad_energy_icon.png][ironclad_energy_icon.png]`.
  The same cards later printed `[Energy]` correctly in combat. Cosmetic, but it is a
  defect visible to a player.
- **Relics arrived with no text.** Claiming Juzu Bracelet and Art of War printed only
  `ok Claiming reward: relic` — I learned what Juzu Bracelet did one fight later, from
  the combat relic list. Potions were worse at first (`Ship in a Bottle — Ship in a
  Bottle`) though they read correctly once held.
- **The Sunken Statue offered "the Sword of Stone" with no description**, so the choice
  was a named unknown against a concrete 103 gold. I took the gold for that reason.
- **Enemy renumbering after a kill** — `Phantasmal Gardener (1)` naming a different
  creature after the first one died. The bridge warns about this for *cards*; for
  enemies it silently re-points a name I was targeting by.
- **`999999999/999999999`** as the dead boss's HP is the engine's internals showing
  through. It did communicate "unkillable", but by accident.

Nothing contradicted its own text outright. The boss's Steam Eruption in particular was
scrupulously honest — printed early, numerically explicit, visibly growing every round.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted: Injury** (unplayable by printing). Among cards I could actually play,
  **Defend** — 5 block never once changed an outcome, and I would rather have drawn
  almost anything else.
- **Happiest to draw: Conflagration**, but only *after* Inflame and Fight Me! were down.
  Turning "Deal 2 damage 4 times" into "Deal 15 damage 4 times" for one energy is the
  single most satisfying thing this deck did — 60 damage from a 1-cost card. Honourable
  mention to **Unrelenting**, whose free attack repeatedly turned 2 energy into an exact
  kill (fights 6, 8, 9) and made Bash cost 0 once.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, but a thin one.** With Conflagration, two Strikes and two Defends against a
22/21 pair, I had a real damage-versus-block split and a real target question, and I
did reject an alternative (Defend + 2 Strikes) for a stated reason. But the decision was
small: no line killed anything, and the honest driver was "leaving a target at 1 HP
saves an energy next turn", which is a bookkeeping insight rather than a kit one. The
first turn that presented a *characterful* decision was fight 2's — ordering Setup
Strike ahead of Conflagration — and that is the second fight.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed ones — every one of them, in full:

1. `mkdir -p "<scratchpad>/lane2" && echo "notes start" > "<scratchpad>/lane2/notes.md"`
   — created a scratch notes file in the session scratchpad. I never wrote to it again
   and never read it.

Tools used:

- **Bash** — for all `GITS_LANE=2 python -m understudy.blindplay observe` and
  `... act "<command>"` calls, plus the single `mkdir`/`echo` above.
- **Write** — once, to create this record file, as permitted.

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no other
understudy subcommand. I did not read any YAML sheet, C# source, doc, packet, review
material, or any other seat's record. Everything above comes from what the bridge
printed to me during play.
