# Klee — blind seat, round 11, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat. Lane 1.
- **Run seed:** `N4VANPNUBCTU` (as the embark printed it back off the wire).
- **Character:** Klee (`KLEEMOD-KLEE`). **Ascension the run opened at:** 0.
- **Act / boss:** Act 1. The map named the act boss as **Waterfall Giant**; I did
  not reach it.
- **Floor reached:** node (3,5) — the fifth combat node, five fights in.
- **Actions accepted:** 80 of 80. **Termination:** the action budget, spent mid
  fight 5 (I stopped on a clean turn boundary at the start of round 4).
- **HP trajectory:** 62/62 → 62 (fight 1, took nothing) → 55 (fight 2 start) →
  51 → 49 → 45 → 33 (fight 4 cost 16) → 33 through fight 5 round 2 → **13/62**
  after fight 5 round 3. Nearly all of the loss is fights 4 and 5, both of which
  I entered with no block in hand.
- **Gold:** 68 (11 + 20 + 18 + 19), unspent — no shop or rest was reachable
  inside the budget.
- **Potions held:** Attack Potion, Gambler's Brew, Potion of Binding (3/3 full,
  none used — see (b), this is itself a finding).
- **Relics:** Pounding Surprise ("Whenever a Bomb goes off, gain 1 Spark"),
  Lost Coffer (from Neow).
- **Deck at the stop** — 15 cards. Inferred starter (10): 4× Strike, 4× Defend,
  Jumpy Dumpty, Ka-pow!. I never saw the deck listed on a screen, so the 4/4
  split is inference from hands, not something printed to me. Added in this act:
  Perfect Timing, Fish-Flavored Bait, Diona — Shaken Not Purred, Dodoco Cover,
  Powder Charge.

**Neow pick: Lost Coffer** ("Gain 1 card reward and procure 1 random Potion") —
blind, the pick that shows me the most of the kit is the one that deals me an
extra card *choice*, and a potion is a free out in a fight I misread. Pomander
(upgrade a card) upgrades a card I have not seen yet; Leafy Poultice wanted 12
max HP before I knew whether this character can block at all.

Card taken from it: **Perfect Timing** over Rapid Fire and Chain Fuse — 1 cost
that both detonates and hits, where Chain Fuse only grows bombs I did not yet
have and Rapid Fire's random targeting is a liability with two enemies up.

---

## Fight 1 — Corpse Slug 25 HP + Corpse Slug 27 HP

Both wore `Ravenous 4 — When an enemy dies, Corpse Slug immediately eats it,
becoming Stunned and gaining 4 Strength.` Intents: 3×2 and 8.

**Round 1** — Jumpy Dumpty on Slug (1) → Perfect Timing on Slug (1) → Strike on
Slug (1).

The read: `Jumpy Dumpty — Place a Bomb 8. When it goes off, place a Mine 3 on
ALL enemies` plus `Set off — Every Bomb on the target goes off first, one at a
time, each a Pyro hit for its size` means Perfect Timing on the same target is
8 (bomb) + 8 (card) = 16, and the bomb going off seeds a Mine on both slugs. I
then Struck the same slug to leave it at exactly 3, because `Mine — a Bomb that
also goes off when its enemy attacks you, **before the hit lands**` meant a
Mine 3 would kill it *instead of* letting it swing.

**Alternative rejected:** Defend (5 block against 14 printed incoming) and
spreading the Strike onto Slug (2). Rejected because the mine line converts the
last 3 HP into a prevented attack, and because splitting damage kills nothing.

Outcome, and it is worth stating that this was the single most satisfying beat
of the round: the mine killed Slug (1) before it acted, Slug (2) ate the corpse,
took its Stun, and **I took zero damage on a turn where the screen printed 14
incoming**. The screen and the outcome agreed exactly.

**Round 2** — enemy now 27 HP, Strength 4, intent 12, wearing my grown Mine
(`Bomb 7`). Hand: Ka-pow! (0 cost, Retain), 2 Strike, 2 Defend.

Played Strike, Strike, Defend and **held Ka-pow!**.

**Alternative rejected:** Ka-pow! + both Strikes (23 damage, leaving it at 4,
taking the full 12). I rejected it *because the Mine detonates itself*: holding
the set-off card meant the Mine 7 went off for free on the enemy's own attack
and Ka-pow! (Retain) cost me nothing to keep. Same fight length, 5 more HP. This
is the best decision the kit offered me all round and it is entirely legible
from the two keyword blocks.

Result: took 12−5 = 7; the Mine went off for 7 unprompted. HP 55.

**Round 3** — enemy at 8. Ka-pow! (4) + Strike (6). No alternative worth the
name; it was a cleanup turn.

---

## Fight 2 — Toadpole 25 HP + Toadpole 23 HP

**Round 1** — Fish-Flavored Bait on Toadpole (2) → Ka-pow! on Toadpole (2) →
Strike → Strike. Arithmetic from the printed faces: 4 + (bomb 4 + 4) + 6 + 6 =
24 against 23 HP, an exact-lethal on the *attacking* toadpole while the other
was on Buff intent.

**Alternative rejected:** planting the Bomb 4 and letting it grow to 8 for a
bigger detonation next turn. Rejected because a bomb that is not Set off does
nothing at all this turn, and killing the only attacker is worth more than 4
banked damage. That is a genuine tension the kit prints clearly: **bombs are a
loan at 4 interest per turn, and detonating early is always paying it off
early.**

**Round 2** — the survivor buffed itself to `Thorns 2 — When hit by an attack,
deal 2 damage back.` This is where the kit's own keyword paid off: `Bomb — ...
**Not an Attack**: only Vulnerable and a cap move it.` So a detonation should
not wake Thorns, while my Strike will.

Played Jumpy Dumpty → Perfect Timing → Strike, leaving it on 3 for the Mine to
finish before it swung, exactly as in fight 1.

**Alternative rejected:** Defend instead of the third card, taking two more
turns and eating 9. Rejected for the same mine-kill reason.

I took 4 thorns damage across two attack cards and 0 from the toadpole. Where
screen and outcome disagreed: nowhere — but I could not verify from any printed
line that the bomb detonation *skipped* Thorns, because no screen itemises
recoil. I believe it did (the arithmetic works out) and I could not prove it.

---

## Fight 3 — Sludge Spinner 39 HP

**Round 1** — Jumpy Dumpty → Diona — Shaken, Not Purred → Strike. No set-off
card in hand, so the Bomb 8 was a deliberate loan: leave it, let it grow to 12,
and put the Cryo aura on now so that next turn's Pyro detonation is a Melt.

**Alternative rejected:** Defend + Diona for 11 block and no engine. Rejected
because the bomb has to be planted a turn before it pays, and I would rather
eat 2 than fall a turn behind on a 39 HP body.

Two findings from this turn:

1. Diona printed `If a Bomb goes off this turn, gain 5 Block`, and the buff it
   left on me read `Shaken, Not Purred 5 — The next time one of your Bombs goes
   off **this turn**, gain 5 Block.` No bomb could go off — nothing in hand
   could Set off — so that half of the card was dead on arrival. **Diona is a
   1-cost 6-block card unless a set-off card is in the same hand**, and nothing
   on the card warns you of that before you commit the energy.
2. **My Spark went 1 → 2 with no bomb going off.** Pounding Surprise says Sparks
   come from bombs going off, and the Spark keyword says "Start each combat with
   1. Pounding Surprise grants more." Neither explains this gain. I could not
   account for it from anything printed. It happened again later (Spark reached
   3 in fight 4 and 5 with fewer detonations than that implies), so either Spark
   ticks up per turn or something silent grants it. **This is the one number in
   the kit I could not read off the screen.**

**Round 2** — and here the interface did something genuinely good. Every Pyro
card in hand now printed `*Reaction preview: Melt* — Pyro meets Cryo: this hit
deals 1.75x damage and consumes the aura`, and every printed damage number had
already been *reduced* for the Weak 1 I was wearing (Ka-pow! read 3, not 4;
Perfect Timing read 6, not 8). I did not have to do either piece of arithmetic.

Played Ka-pow! → Perfect Timing. The read: Ka-pow!'s Set off sends the Bomb 12
in as a Pyro hit against a Cryo aura → Melt → 21. That detonation is a Bomb
triggering an Elemental Reaction, which is exactly the clause on Perfect
Timing — `If a Bomb triggered an Elemental Reaction this turn, play this again`
— so Perfect Timing plays twice. 21 + 3 + 6 + 6 = 36 against 33. Dead, from
full-ish HP, in one 1-energy turn.

**Alternative rejected:** Bait first for another bomb, then set off. Rejected —
nothing beats a kill.

This is the kit at its best and the strongest thing I can report: **a three-card
sequence I assembled myself out of three separate printed clauses (aura → Melt →
"a Bomb triggered a Reaction"), where the payoff was roughly triple a fair
turn.** It felt earned, not given.

---

## Fight 4 — Fossil Stalker 51 HP (`Suck 3 — Whenever Fossil Stalker deals unblocked attack damage, it gains 3 Strength`)

**Round 1** — intent 12. Hand was 3 Defend, Bait, Diona. Played Diona + Defend +
Defend for 16 block and took nothing.

**Alternative rejected:** Bait + Diona + Defend (11 block, 4 damage, one bomb
planted) — 1 point would have leaked and Suck would have banked +3 Strength
permanently. Against a Suck body the block threshold is a cliff, not a slope,
so the whole turn goes to clearing it. Real decision, and an unpleasant one:
**the correct turn was to play no Klee card at all.**

**Round 2** — Dodoco Cover → Ka-pow! → Strike → Strike. Dodoco plants a Bomb 4
under the Cryo aura Diona left; Ka-pow! melts it (4 × 1.75 = 7) and adds 4;
2 Strikes add 12. Printed 51 → observed 28, i.e. exactly 23. Screen and outcome
agreed to the point.

**Alternative rejected:** hold Ka-pow! and let the Bomb 4 grow to 8. I did the
arithmetic both ways and detonating now was ~5 damage ahead over two turns
because the Cryo aura expires. **The aura clock, not the bomb clock, is what
decides the timing** — that is a nice, readable tension.

Block that turn was 5 against 9; the 4 that leaked bought it Strength 3, which
is the design working as printed.

**Round 3** — Jumpy Dumpty → Perfect Timing → Strike, 22 damage, no reaction
available (it was wearing my own Pyro aura, so Pyro on Pyro just refreshed).
**Alternative rejected:** blocking with a Frail-reduced Defend (3) against a 12
hit — not worth an energy. Took 12, HP 33. The Mine finished off all but 3.

**Round 4** — Ka-pow! for the kill.

The honest read of this fight: it cost me 16 HP and the reason is that **my only
real block in four card rewards was Diona and Dodoco Cover's 5.** Every offer
screen kept putting bomb-placers in front of me; the kit's defensive cards
(Careful Now, Dig In) appeared once each, late.

---

## Fight 5 — Corpse Slug 25 + Corpse Slug 26 + Corpse Slug 27 (stopped here)

**Round 1** — Powder Charge (Spark, no energy) on Slug (3) → Diona on Slug (3)
→ Ka-pow! on Slug (3) → Defend → Strike. That is 16 block *and* 20 damage from
3 energy: Powder Charge costs a Spark rather than energy, Ka-pow! is free, and
the melted Bomb 6 both did 10 and turned Diona's dead clause on (`+5 Block`).
27 → 7 exactly, block 16 against 14 incoming.

**Alternative rejected:** the same turn without Diona (more damage, no block) —
at 33 HP with three bodies up I wanted the turn to do both, and the kit let it,
which is the first turn all round where the *defensive* half of the deck was
also the *engine* half.

**Round 2** — Fish-Flavored Bait + Strike killed Slug (3); Perfect Timing on
Slug (1) set off the Bomb 4 that had **moved to it** off the corpse
(`Kills move it on`) for 12.

**Alternative rejected:** dumping everything into the healthy Slug (2). Rejected
because of Ravenous — and here is the round's second real finding. The card says
"**Corpse Slug** immediately eats it, becoming Stunned and gaining 4 Strength",
singular. What actually happened is that **both** surviving slugs went to
`Intent: Stunned` and **both** gained Strength 4. Killing one body stunned the
entire remaining group for a turn. That is a much bigger effect than the
singular phrasing suggests; I got it by accident and only understood it after
reading the result screen. (This is base-game enemy text, not a Klee card, but
it decided my turn, so it belongs here.)

**Round 3** — I was at the budget's edge with a hand of three Frail-reduced
Defends (3 each), Jumpy Dumpty and a Strike against 26 printed incoming. Played
Defend, Defend, end turn: 6 block, took 20, **HP 33 → 13**.

**Alternative rejected:** Jumpy Dumpty to plant a Bomb 8 for a turn I would not
be here to play. With three actions left the honest play was the defensive one.

Termination: budget. The fight was live, both slugs up (13 and 26), me at 13/62
with a full hand and 3 potions unspent.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three kinds, and all three are genuinely interesting:

1. **Detonate now, or let the bomb grow.** `grows 4 a turn, goes off only when
   Set off` is a clean loan mechanic. Every turn with a bomb standing and a
   set-off card in hand is a real question, and the answer changed fight to
   fight (fight 2 round 1: detonate, because a kill; fight 4 round 2: detonate,
   because the *aura* expires first; fight 1 round 2: hold, because a Mine
   detonates itself for free).
2. **Leave the enemy on exactly Mine-lethal HP.** Because a Mine goes off
   *before the hit lands*, arranging the last 3 HP to be taken by the mine
   converts a kill into a prevented attack. I did this in fights 1 and 2, and it
   is the most "Klee" thing in the kit — the reward is for arithmetic and
   ordering, not for a bigger number.
3. **Element ordering.** Diona's Cryo has to land on a body *before* the Pyro
   detonation, and the aura expires in 2 turns, so it sets a deadline on the
   bomb. Melt (1.75×) on a big bomb, plus Perfect Timing's replay clause firing
   off the reaction, was a 36-damage turn out of two cards.

The Spark economy is a fourth, softer one — Powder Charge and Ka-pow! cost no
energy, so a "3-energy turn" is routinely 4 or 5 cards. That felt good and I
never once felt the energy bar was the whole game.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend were pure filler and I resented every one.** By fight 4 I
  had turns whose only legal content was "3 Defends". Fight 4 round 1 — the
  correct play was three basic cards and no Klee card at all — is the low point
  of the round.
- **Cleanup turns are automatic.** Once an enemy is under ~10 the kit has
  nothing to say; Ka-pow! + Strike, no thought.
- **I never used a potion in five fights.** Three sat in the belt through the
  turn that took me from 33 to 13. That is partly my fault, but it is also
  because the bomb plan always *looked* like it was one turn from paying and I
  kept spending my reading on the bomb arithmetic instead of on my outs.
- **Perfect Timing's replay clause only fired once in five fights.** In a
  mono-Pyro hand it is dead text: my own detonations leave a Pyro aura and Pyro
  on Pyro just refreshes, so nothing reacts. It needs a foreign element in the
  deck to be a card rather than a vanilla 1-for-8.

**(c) What I could not understand, or that contradicted its printed text.**

1. **Spark gains I could not account for.** Fight 3 round 1: Spark went 1 → 2
   with no bomb going off (Diona's `The next time one of your Bombs goes off
   this turn` buff was still sitting on me unspent, so I know none had). Nothing
   printed on Pounding Surprise, on the Spark keyword, or on any card I played
   explains it. Sparks appear to accrue for a reason the screen never states.
2. **Diona's conditional block is a trap in printed form.** `If a Bomb goes off
   this turn, gain 5 Block` reads as a rider you will usually get; in practice
   it needs a set-off card in the *same hand*, and there is no way to tell
   before spending the energy. The buff it leaves behind rewords itself to "the
   next time ... this turn", which is clearer than the card is.
3. **The Elemental Reaction keyword block is enormous, and 90% of it was
   unreachable.** Nine keyword paragraphs (Melt, Vaporize, Overloaded,
   Superconduct, Electro-Charged, Frozen, Swirl…) printed on every screen for a
   character who can only make Pyro. In five fights I triggered exactly one
   reaction type, Melt, and only because a card reward happened to offer a Cryo
   companion. The one paragraph inside that block warning that a reaction "can
   hide the first ... no screen ever shows it gone and the reaction looks as
   though it did not happen" is a written admission that the system has a state
   the UI cannot display; I never hit that case, but I would not have known if
   I had.
4. **I could not verify from any screen that a bomb detonation skips Thorns**,
   even though `Bomb — Not an Attack` implies it and my HP arithmetic is
   consistent with it. Nothing itemises recoil.
5. Minor: the enemy badge calls a Mine `Bomb 4` in the title and only discloses
   it is a Mine in the body text ("Bombs here: 1, including 1 Mine"). Since the
   whole Mine trick is timing, the badge should lead with it.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** Defend. Five block, no interaction with anything the kit
  does, and it was the card I had most of at exactly the moments the kit had
  nothing else to offer. (Among Klee's own cards, the closest to unwanted is
  Fish-Flavored Bait — 4 damage and a Bomb 4 is fine but never decided a turn.)
- **Happiest to draw:** **Ka-pow!** — 0 cost, Retain, Set off. It is free, it is
  the detonator, and Retain means holding it is never a cost, which is what
  makes the "detonate now or let it grow" question a real one rather than a
  use-it-or-lose-it. Jumpy Dumpty is a close second for the Mine.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** The opening hand held Jumpy Dumpty, Perfect Timing, two
Strikes and a Defend against two slugs with 14 printed incoming, and the
question — plant-and-detonate for 16 on one body, or Defend and take the hit —
was answerable only by reading Bomb, Set off and Mine together. Better still,
the *right* answer (Strike down to exactly 3 so the Mine kills it before it
swings) needed all three keywords at once and paid with a zero-damage round. If
the goal was "the first turn should teach the mechanic and reward reading it",
this opening does it.

---

## Non-blindness declaration

- Commands run outside the two allowed ones: **one**, the coordinator-mandated
  embark, exactly as instructed —
  `python -m understudy.embark --character KLEEMOD-KLEE --lane 1`.
- All game interaction was `GITS_LANE=1 python -m understudy.blindplay observe`
  and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, nothing else.
  No `harness state`, no `scenario`, no `staged_turn`, no `soak`.
- Shell scratch used inside Bash calls: `mkdir -p` for the record directory,
  `for` loops to issue several `act` calls in one shell invocation, and
  `sed -n`/`head`/`tail` to trim the printed output of `observe` and `act`.
  No file was read.
- Tools used: **Bash** (as above) and **Write** (once, for this record). No Read,
  Grep, Glob, or Agent call was made at any point.
- **Repo files read: none.**
- Model note: this seat is **Opus (Claude)**. The kit under test was authored by
  a different Claude model, so this is not an independent-vendor read.
