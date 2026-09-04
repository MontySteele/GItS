# Klee round 10, run 3, act 1 — blind seat record

## Identity

- **Model / seat:** Claude Opus 5 (1M), blind TESTER seat, lane 1 (`GITS_LANE=1`).
- **Run seed:** not printed on any screen I saw; the bridge never showed a seed line.
- **Character:** Klee (inferred only from the printed cards — "Klee is one too" in the
  *Hexerei* keyword text on `Coven Errand`; nothing else named her).
- **Act:** 1. The map's header printed **"At the top of this act: Vantom"** from the first
  map screen, so the boss was named before I ever walked toward it.
- **Actions accepted:** 215 accepted `act` calls (cap was 250). Two `act` calls were
  refused, both the same refusal (see below); refusals are not counted in the 215.
- **Termination reason:** the stop condition, not a budget. Vantom died, its reward screen
  was handled, and the lane is now sitting on the act-2 map (first node: `Ancient`). I did
  not enter act 2.
- **HP trajectory:** 62/62 start → 62 after fight 1 → 54 after fight 2 → **13/62** at the
  worst point (end of elite 1, Bygone Effigy) → rest → 36/67 → 32/67 → rest → 57/72 →
  36/72 after the Wriggler swarm → 33/72 → rest → 59/77 into the boss → **17/77** at the
  end. Max HP 62 → 77 across three rests (Stone Humidifier).
- **Gold:** the last figure the game printed to me directly was **"You have 129 gold"** on
  the shop screen; I spent 76 there and then collected 36 + 12 + 17 + 41 + 20 + 100 = 226
  more, so I finished on roughly **279**. Only the 129 and the individual pickups were
  printed; the total is my arithmetic, not the screen's.
- **Potions held:** `Attack Potion` (choose 1 of 3 random Attacks into hand, free this
  turn) and `Colorless Potion`. I spent `Explosive Ampoule` on the Wriggler swarm.
- **Relics at the end:** `Pounding Surprise` (Bomb goes off → 1 Spark), `Stone Humidifier`
  (+5 Max HP per Rest), `Kusarigama` (3 Attacks in a turn → 6 damage to a random enemy),
  `Lizard Tail` (once, survive lethal at 50% Max HP — never triggered), `Prayer Wheel`
  (normal enemies drop an extra card reward).
- **Deck at the end** (as the Smith/Enchant screens printed it, plus everything I added):
  4× `Strike`, 4× `Defend`, `Ka-pow! (Sharp 2)`, `Jumpy Dumpty+`, `Big Badda Boom` ×2,
  `Dodoco Cover`, `Fwoosh!`, `Mine Toss`, `Bang Bang!`, `Razor — Claw and Thunder`,
  `Run Away!`, `Powder Charge`, `Perfect Timing`, `Careful Now`, `The Big One`, plus the
  Status cards the two elites and the boss shovelled in (I saw `Infection` and `Wound` in
  hand; the exact count is not something any screen told me — the enemies announced
  "3 Status cards" three separate times and "1 Status card" twice).

**Neow pick: Stone Humidifier** ("Whenever you Rest at a Rest Site, raise your Max HP
by 5"). I took it because it was the only one of the three that did not distort what I was
there to read: `Kaleidoscope` would have filled my deck with two other characters' cards,
and `Precarious Shears` would have deleted two of the kit's own cards and cost 16 HP up
front. It turned out to be the right call for survival too — three rests bought +15 Max HP
and I finished act 1 with 17 HP, so those 15 mattered.

---

## Fight 1 — Fuzzy Wurm Crawler, HP 56/56

**Turn 1.** Hand: `Ka-pow!`(0), `Strike`×2, `Defend`×2. Enemy intent: Attack for 4.
Played `Strike`, `Strike`, `Defend`. **Rejected:** also playing `Ka-pow!`, which is free.
The reason is the only interesting thing about this turn: `Ka-pow!` prints *"Retain. Set
off. Deal 4 damage."* and `Set off` is dead text while the enemy has no Bombs, so its 4
damage now trades against a bigger Set off later — and because it Retains, holding it
costs nothing. I held it. **But 3 energy covered every card in hand that wanted energy
AND left one for Defend, so the turn presented no energy decision at all.** The only
decision was about a card that costs zero.

**Turn 2.** Drew `Jumpy Dumpty` — *"Place a Bomb 8. When it goes off, place a Mine 3 on
ALL enemies."* Enemy intent: Empower (Buff), so no incoming damage. Played
`Jumpy Dumpty`, then `Ka-pow!`, then `Strike`, `Strike`.
**Rejected:** placing the Bomb and *not* setting it off, to let it grow. The badge after
`Jumpy Dumpty` read *"Bomb 8 … Each grows at the start of your turn"*, so holding was
worth exactly +4 next turn, which is the same 4 damage `Ka-pow!` deals right now — a wash
— and setting it off also bought a `Mine 3` and a Spark from `Pounding Surprise`. Screen
and outcome agreed exactly: 44 → 32, Spark 1 → 2, `Mine` badge appeared.

**Turn 3.** Enemy at 20, intent Attack 11, Strength 7, `Bomb 7` (the Mine) on it.
Played `Strike`, `Strike`, `Defend`. **Rejected:** `Jumpy Dumpty`-style aggression with no
block, and rejected a second `Defend` over the second `Strike`. This was the first turn
with a real arithmetic decision: 12 damage put it at 8, one short of the 7 the Mine would
deal on its own attack, so the kill was **exactly one point out of reach** and I could see
that from the printed numbers. I took the 5 block and the 6 damage instead.

**Turn 4.** Enemy at 1 HP (Mine had gone off for 7 before its hit, as printed). Played
`Ka-pow!` for the kill. **No alternative rejected — a free card killed a 1-HP enemy.**

**Reward:** `Big Badda Boom` over `Chain Fuse`, `Grounded`, `Dahlia — Favonian Favor`.
`Grounded` pays *"if none of your Bombs went off last turn"*, which is an anti-synergy with
the only engine the character had shown me; `Chain Fuse` grows Bombs I did not yet have
enough of; `Big Badda Boom` prints *"Set off. Deal 12 damage. Then deal damage equal to
what the Bombs dealt"* — i.e. it doubles the Bomb pile — and works as a plain 12-damage
attack when there are no Bombs. Easy pick, and it defined the rest of the run.

---

## Fight 2 — Shrinker Beetle, HP 40/40

**Turn 1.** Played `Big Badda Boom` then `Strike` (18 damage, 3 energy, no Bombs in play).
**Rejected:** `Strike`+`Strike`+`Defend` (12 damage + 5 block). The enemy's intent was
"Strategic (DebuffStrong)", so block was worthless and damage was free.

**Turn 2.** I now had `Shrink -1` — *"While Shrinker Beetle is alive, your Attacks deal 30%
less damage."* `Strike`'s face changed from "Deal 6 damage" to **"Deal 4 damage"**, which
is good: the debuff is visible on the card, not just in a status line. Played
`Jumpy Dumpty` → `Ka-pow!` → `Strike` → `Defend`.
**Rejected:** holding `Ka-pow!` to grow the Bomb. The reason I set off immediately is the
best-designed interaction I found all run: the Bomb keyword prints *"Not an Attack: only
their Vulnerable and a cap move it"*, so **Shrink does not touch Bomb damage.** The
badge confirmed it — the Bomb 8 landed for the full 8 while my 6-damage Strike landed for
4. Under an attack-damage debuff, the kit's Bombs are the answer, and the screen told me
so before I played.

**Turn 3.** Enemy at 3. Played `Ka-pow!`. **No alternative — a free card killed it.**

**Reward:** `Dodoco Cover` (Bomb 4 + 5 Block for 1) over `Dig In` (8 Block for 1 Spark),
`Coven Errand`, `Razor — Lightning Fang`. I had exactly one Bomb source in the deck and
the payoff cards were piling up, so the card that is both a Bomb and a Defend won.

**Event (`Self-Help Book`).** Took `Read the Back` → Sharp 2 on `Ka-pow!`.
**Legibility problem, recorded as I hit it:** the event screen names the enchantments
`Sharp 2` and `Nimble 2` and **defines neither**. I picked blind on the word "Sharp". The
definition (*"Increases damage on this card by 2"*) only appeared later, on the card face
in combat.

**Shop (129 gold).** Bought `Fwoosh!` (24g — Set off + 6, priced in 1 Spark, not energy)
and `Mine Toss` (52g). Rejected `Card Removal` at 75g: a second Bomb source was worth more
than thinning one Strike out of a 12-card deck.

**Event (`Brain Leech`).** `Share Knowledge` → took `Bang Bang!` (2 Sparks: Set off, 8
damage, place a Bomb 4) over `Sizzle`, `Run Away!`, `Mine Toss`, `Fwoosh!`. I wanted a
second Spark-priced Set off that refills the Bomb it consumes. This pick is the one I would
take back — see (c).

**Rest site.** Took **Smith** over Rest at 54/62, upgrading `Jumpy Dumpty` → `Jumpy
Dumpty+` (Bomb 8 → **Bomb 11**, Mine 3 → Mine 4). **Rejected:** resting. The reasoning was
that only 8 HP were missing, so a heal of 18 would waste half itself, and `Big Badda Boom`
echoes Bomb damage, so +3 on the biggest Bomb is worth +6 on a combo turn. This decision
nearly killed me two rooms later.

---

## Fight 3 (ELITE) — Bygone Effigy, HP 127/127

The enemy printed `Slow 0` — *"Whenever you play a card, this enemy receives 10% more
damage from Attacks this turn."* Note the two words that mattered and that I had to derive
myself: **from Attacks**. Bombs are not Attacks, so Slow never touched them.

**Turn 1** (enemy Sleeping, no damage incoming). Played `Dodoco Cover` → `Strike` →
`Fwoosh!`, holding `Ka-pow!`. **Rejected:** playing `Fwoosh!` before `Dodoco Cover` so the
Bomb would survive and grow. I set off instead because `Fwoosh!` does not Retain — it would
have been discarded unplayed — and setting off refunded the Spark it cost.
**Screen vs outcome, worth flagging:** 17 damage landed, not the 18 I expected. Working
backwards, `Slow` increments *after* the card resolves, so the first card played gets no
bonus. Nothing on the screen says that, and the badge only ever shows the running total
(`Slow 30 … Receives 30% more damage`).

**Turn 2** (enemy Empower). Played `Mine Toss` → `Strike` → `Strike`.
**Rejected:** both `Defend`s, because the intent line said Buff and block expires.

**Turn 3 — the decision turn.** Enemy at 97, `Mine 8` on it, Strength 10, intent Attack 23,
me at 54. Hand had `Jumpy Dumpty+`(1), `Big Badda Boom`(2), `Defend`×2, `Strike`.
Played `Jumpy Dumpty+` then `Big Badda Boom`, using all 3 energy and taking the hit bare.
**Rejected:** `Jumpy Dumpty+` + `Defend` + `Defend` (10 block, take 13, but `Big Badda
Boom` is discarded unplayed because it does not Retain). The trade was ~19 extra damage
against 10 block. **52 damage landed in one card** (97 → 45): Bomb 8 + Bomb 11 = 19, then
12, then the echo of 19. This is the best turn the kit produced and I could compute it
exactly from the printed faces beforehand. I then took 23 to the face and dropped to 31.

**Turn 4.** Enemy 41, me 31, another 23 incoming. Played `Mine Toss` → `Defend` →
`Ka-pow!` → `Fwoosh!` → `Strike`, in that order.
**Rejected:** `Defend`+`Defend`+`Strike` (22 damage, 10 block, HP 18, enemy 19). I chose
26 damage and 5 block (HP 13, enemy 15) because the real constraint was killing it on the
following turn, and the ordering mattered: I front-loaded the two skills so the three
attacks each caught a bigger `Slow` stack. Predicted 26, got exactly 26.

**Turn 5.** Me at 13 with 23 incoming; a miss meant death. Enemy 15. Played
`Jumpy Dumpty+` (Bomb 11) → `Dodoco Cover` (Bomb 4) → `Strike` → `Bang Bang!`, which set
off 15 of Bomb on its own Spark price. **Rejected:** nothing — this was a forced lethal
check, and the only judgement was whether the numbers reached. They did, twice over.

**Reward:** `Explosive Ampoule`, `Kusarigama`, and I picked `Razor — Claw and Thunder`
(Electro, 8 damage) over `Run Away!`, `Fwoosh!`, `Bang Bang!`. Reason: **every screen in
this game devotes about fifteen lines to Elemental Reactions and after three fights not one
had ever fired**, because the whole kit is Pyro and a Pyro hit on a Pyro aura just
refreshes it. One Electro card turns my permanent self-applied Pyro aura into a guaranteed
`Overloaded` (6 damage to all + 1 Weak). I wanted to see whether that block of text was
real.

**Rest.** Rested: 13 → **36/67**. The screen said *"Heal for 30% of your Max HP (18). Raise
your Max HP by 5"* and I gained **23** HP and 5 Max HP. Reading it charitably, `Stone
Humidifier`'s +5 Max also granted +5 current, and only one of the two "+5 Max HP" sources
actually moved the maximum. Either way **the printed heal number and the delivered heal
disagreed by 5** and no line on the screen accounts for the difference.

---

## Fight 4 — Nibbit, HP 45/45

**Turn 1.** The turn that sold me the kit. Played `Dodoco Cover` (Bomb 4, 5 block) →
`Ka-pow!` (set off 4, +1 Spark from `Pounding Surprise`, now 2 Sparks) → `Bang Bang!`
(now affordable at 2 Sparks, 8 damage, places a fresh Bomb 4) → `Defend` → `Defend`.
18 damage and 15 block for 3 energy. **Rejected:** holding `Ka-pow!` — which would have
left `Bang Bang!` **unplayable**, because the Spark that paid for it came from the Bomb
`Ka-pow!` set off. That dependency (place → set off → the Spark refunds → the Spark-priced
card unlocks *within the same turn*) is the best sequencing puzzle the kit gave me, and
nothing prints it; you have to notice it.

**Turn 2.** Enemy 27, `Bomb 8` on it, `Pyro Aura 1`, intent Attack 6 **and** Defend.
`Razor — Claw and Thunder` now printed an extra line: ***"Reaction preview: Overloaded —
Pyro meets Electro: 6 damage to ALL enemies and 1 Weak on the reacted enemy."*** That is a
genuinely good piece of UI — the reaction was previewed on the card face before I committed.
Played `Razor` → `Strike` → `Jumpy Dumpty+`. 20 damage, `Weak 1` landed, the intent number
visibly dropped 6 → 4, the aura was consumed exactly as the keyword said.
**Rejected:** `Defend` — the enemy intended to Block, and I had worked out from the Bomb
keyword that its Block would not stop Bomb damage anyway.

**Turn 3.** Enemy 7 HP behind 5 Block, `Bomb 27` on it. Played `Big Badda Boom`.
**Rejected:** `Strike`×3 (18 damage − 5 block = 13, also lethal, and would have fired
`Kusarigama`). I picked the Bomb line because it was one card instead of three. Honest
caveat: I wanted this to be a clean test of whether Block stops Bomb damage and it was not
one — 27 kills through 5 Block either way, so **I still do not know the answer**.

**Reward:** `Run Away!` (0-cost, 3 Block, 7 if a Bomb went off) over `Coven Errand`,
`Mine Toss`, `Bennett`. A free block card in a deck that wants all three energy on Bombs.

---

## Fight 5 — Cubex Construct, HP 65/65 (`Artifact 1`)

**Turn 1** (enemy Empower). Played `Ka-pow!` → `Mine Toss` → `Strike`, 12 damage.
**Rejected:** holding `Ka-pow!` again. I played it *first*, deliberately, so its Set off
would find no Bomb and I could still place the Mine afterwards and let it grow. That
"play the Set off card before the Bomb card" inversion is a real, if fiddly, decision.
One energy went unspent — the hand's only remaining card was a `Defend` and the enemy
was buffing.

**Turn 2.** Played `Jumpy Dumpty+` (Bomb 11) → `Dodoco Cover` (Bomb 4) → `Fwoosh!` (set
off all 23) → `Defend`. 33 damage total (23 Bombs + 6 + the Mine 4 that `Jumpy Dumpty+`
leaves behind, which then went off on the enemy's attack), 10 block, zero damage taken.
**Rejected:** banking the 23 Bomb for one more turn to reach ~35 and hoping to draw a
`Big Badda Boom` to echo it. I declined because `Fwoosh!` does not Retain: not playing it
is not "saving" it, it is discarding it. **This is the kit's central tension and it is a
good one** — every Set off card except `Ka-pow!` forces you to cash in on the turn you draw
it, so the Bomb pile almost never gets to grow to the size the cards imply.

**Turn 3.** Enemy 20. Played `Strike`×3 for 18 + `Kusarigama`'s 6 = 24. Kill.
**Rejected:** `Big Badda Boom` + `Strike` = 18, which does not kill with no Bombs down.

**Reward:** `Powder Charge` (1 Spark: place a Bomb 6, no energy) over a second
`Dodoco Cover`, `Pocket Fireworks`, `Razor`. Energy, not Bombs, was the bottleneck on the
big turn, so a Bomb that costs no energy was the right shape.

---

## Fight 6 (ELITE) — Phrog Parasite, HP 61/61 (`Infested 4`), then 4× Wriggler

**Turn 1** (enemy giving Status cards, no damage). Played `Dodoco Cover` (Bomb 4) →
`Big Badda Boom` (set off 4 → 4 + 12 + echo 4 = 20) → `Run Away!`.
**Rejected:** `Mine Toss` + `Dodoco Cover` to bank 8 Bomb and let `Big Badda Boom` be
discarded. 20 guaranteed beat a bank I might not get to spend. **Worth stating plainly:
`Big Badda Boom` on a 4-Bomb is a 2-energy 20-damage card, and on a 19-Bomb it is a
2-energy 50-damage card. The card is the same; only the setup differs. That is the
character.** Also: block was strictly wasted this turn (the intent was Status cards), so
`Run Away!` and `Dodoco Cover`'s block did nothing, and I played them anyway because there
was nothing else to do with the cards.

**Turn 2.** Played `Powder Charge` (1 Spark → Bomb 6) → `Ka-pow!` (set off 6, +1 Spark) →
`Bang Bang!` (now affordable again, 8 + a fresh Bomb 4) → `Strike` → `Defend`.
Three Attacks fired `Kusarigama` for 6. Predicted 32, got exactly 32 (41 → 9).
**Rejected:** holding `Ka-pow!`, which would again have left `Bang Bang!` stranded.

**Turn 3.** Enemy at 9 with `Bomb 8` on it and `Pyro Aura 1`. Played `Razor` alone (8 +
`Overloaded` 6). **Rejected:** `Strike`×2, which also kills, and rejected setting off the
Bomb 8 first — no Set off card was in hand, so the 8 Bomb on the corpse was simply wasted.
`Infested 4` then spawned four Wrigglers (20/17/19/21), all Stunned. **The `Bomb 8`
transferred onto Wriggler (1).** Nothing printed said it would; that is a pleasant surprise
rather than a defect, but it is undocumented.

**Turn 3 (cont).** 2 energy left, all four spawns Stunned, so block was worthless. Played
`Strike`×2 into the smallest Wriggler (17 → 5). **Rejected:** spreading the damage, since
nothing in hand was AoE.

**Turn 4.** Used `Explosive Ampoule` (10 to ALL — 3 targets, its best moment) → placed
`Jumpy Dumpty+`'s Bomb 11 on Wriggler (3) → `Strike` → `Defend`.
**Rejected:** putting the Bomb 11 on Wriggler (1), which already carried Bomb 16 against
only 20 HP. Spreading lethal Bombs across two bodies was the right call and the badges made
it computable.

**Turn 5 — the one that exposed the engine's failure mode.** Spark **0**. Both Set off
cards in my hand (`Fwoosh!` 1 Spark, `Bang Bang!` 2 Sparks) printed **"CANNOT BE PLAYED:
you have no Spark"**, while a `Bomb 12` sat on Wriggler (1) with no way to detonate it. The
Spark economy only refills when a Bomb goes off, and a Bomb only goes off if I can pay for
a Set off. **That is a genuine dead-end loop and it happened to me twice.** Played
`Ka-pow!` on Wriggler (1) — its Bomb 16 killed it and refunded a Spark — then `Razor` to
kill Wriggler (2), then `Mine Toss`. **Rejected:** spending that recovered Spark on
`Powder Charge`; I deliberately held it so `Fwoosh!` would be playable next turn as a Set
off. That is the most interesting resource decision the run produced, and it exists only
because the economy can strand you.

**Turn 6 never happened.** The last Wriggler attacked, its Mine went off before the hit
"as printed" — and it died. Working backwards from a Wriggler that had 11 HP and carried
`Bomb 15` plus a `Mine 4`: **the Mine's trigger appears to set off every Bomb on that
enemy, not just the Mine.** The `Bomb` keyword does say Bombs go off "all at once", but the
`Mine` keyword reads *"A Bomb that also goes off when its enemy attacks you"* — singular —
so the two texts point in different directions and only the outcome disambiguates them.
Same thing happened in fight 7, so I am fairly confident, but I could not test it cleanly.

**Rewards:** `Prayer Wheel`, and `Perfect Timing` (1 energy: Set off, 8 damage, replays
itself if a Bomb triggered a reaction) over `Safety Lesson`, `Alice's Introduction Magic`,
`Lynette`. Picked specifically to fix the Spark dead-end: it is an energy-priced Set off,
and I had exactly one other (`Big Badda Boom` at 2).

---

## Fight 7 — Mawler, HP 72/72

**Turn 1.** Played `Dodoco Cover` (Bomb 4) → `Big Badda Boom` (set off 4 → 4 + 12 + echo 4
= 20) → `Fwoosh!` (6) → `Ka-pow!` (6), three Attacks firing `Kusarigama` for 6. **38
damage, exactly as predicted.** **Rejected:** letting `Fwoosh!` do the setting off instead
of `Big Badda Boom` — worth 4 less, because only `Big Badda Boom` echoes the Bomb.

**Turn 2** (enemy Debuff intent). Played `Powder Charge` (Bomb 6) → `Mine Toss` (Mine 4) →
`Razor` (8 + `Overloaded` 6) → `Strike`. 20 damage, 10 Bomb banked.
**Rejected:** `Defend`, since the intent was a debuff, not damage.

**Turn 3.** I was `Vulnerable 3` (*"Receive 50% more damage from Attacks"*), Mawler had 14
HP and intended 21 — i.e. **31 to me at 33 HP**. Spark 0 again, so `Bang Bang!` was
unplayable and I had **no way to set off the Bomb 18 sitting on it.** Played `Strike`
(14 → 8) → `Jumpy Dumpty+` → `Defend` → `Run Away!` for 8 block.
**Rejected:** any line that tried to win by damage, because there wasn't one. The play was
to get Mawler below the Mine's value so that its own attack would kill it before the hit
landed. It did — the fight ended during the enemy's turn with **zero damage taken.** That
is a genuinely delightful outcome and it is the second confirmation that a Mine detonates
the whole stack.

**Rewards** (two cards, `Prayer Wheel`): a second `Big Badda Boom`, and `Careful Now`
(Retain; Block equal to your largest Bomb, up to 10) over `Witches' Circle`, `Chain Fuse`,
`Lisa — Lightning Rose`. Rejected `Lisa` reluctantly: the Bomb keyword says *"only their
Vulnerable and a cap move it"*, so a repeating source of Vulnerable is a **Bomb damage
multiplier**, which is a lovely piece of design — but I was one bad turn from dying and
took the block instead.

---

## Fight 8 (BOSS) — Vantom, HP 173/173

`Slippery 8` — *"The next 8 times Vantom loses HP, it only loses 1 HP instead."* This is a
direct, deliberate counter to exactly what my deck does, and reading it inverted my whole
playbook: for four turns I wanted **as many separate, tiny HP-loss events as possible**,
which is the opposite of every other turn in the run. Best boss-vs-kit interaction I saw.

**Turn 1.** Played `Dodoco Cover` (Bomb 4) → `Razor` (applies an Electro aura) →
`Perfect Timing` (its Set off detonated a Pyro Bomb into that Electro aura → **`Overloaded`
fired**, and because *"a Bomb triggered an Elemental Reaction this turn"*, `Perfect Timing`
**played itself again**). Five separate HP-loss events for five total damage — but
`Slippery 8 → 3` and `Weak 1` on the boss. **Rejected:** opening with a Bomb bank, which
would have fed a 25-point Bomb into the Slippery counter for 1 damage. Then played
`Ka-pow!` for one more free charge burn. **Rejected:** holding `Ka-pow!` for a free Set off
later; with 0 energy left it was a charge burned for nothing.

**Turn 2.** `Slippery 1`. Played `Strike` (burning the last charge with my *smallest* hit,
deliberately) → `Jumpy Dumpty+` (Bomb 11) → `Powder Charge` (Bomb 6). 17 Bomb banked.
**Rejected:** `Mine Toss`, and this was the sharpest decision of the fight — having learned
in fights 6 and 7 that a Mine detonates the entire stack when the enemy attacks, placing a
Mine would have **prematurely blown my whole Bomb bank on the boss's turn**, at 1× instead
of through `Big Badda Boom`'s echo. So I let one energy go unspent on purpose. I don't
think any printed text would have told me that; I only knew it from two accidents.

**Turn 3.** `Bomb 25` on the boss, 26 incoming. Played `Big Badda Boom` → **66 damage**
(165 → 99), then `Run Away!` for 7 (its Bomb condition satisfied) and `Defend` for 5.
**Rejected:** banking another turn, which was not available — the second `Big Badda Boom`
was in hand and would have been discarded, so "waiting" meant throwing away the payoff card.

**Turn 4** (boss Empower). `Strike`, `Strike`, `Fwoosh!` = 18 + `Kusarigama` 6 = 24.
**Rejected:** `Careful Now`, which prints Block equal to my largest Bomb — and I had no
Bombs, so it would have given **0**. Held it (it Retains).

**Turn 5.** `Razor` (8 + `Overloaded` 6 + `Weak`) → `Strike` → `Strike`, `Kusarigama` for
6. 32 damage. **Rejected:** blocking; I was racing.

**Turn 6.** The Spark chain again: `Powder Charge` (Bomb 6) → **`Careful Now` for 6 block,
played at the exact moment the Bomb was largest** → `Ka-pow!` (set off 6, refunding the
Spark) → `Bang Bang!` (now affordable) → `Strike`. 32 damage (43 → 11), 6 block.
**Rejected:** holding the Bomb to make `Careful Now` worth its full 10 — the boss was at 43
and I was at 27, so tempo won. This turn is the clearest example of the kit's sequencing
mattering: the same five cards in a different order give less damage, less block, or leave
`Bang Bang!` unplayable.

**Turn 7.** Boss at 11 with 28 incoming; I was at 17, so it was kill-or-die. Played
`Jumpy Dumpty+` (Bomb 11) → `Dodoco Cover` (Bomb 4) → `Fwoosh!` set off 23. Dead.
**Rejected:** `Fwoosh!` alone, which was already lethal (8 + 6 vs 11) — I overkilled on
purpose because a miscount meant losing the run.

**Boss reward:** `The Big One` (3 energy, *"Set off for quadruple damage"*) over
`Chained Reactions`, `Sparks 'n' Splash`, `Mona`. Also took 100 gold and a
`Colorless Potion`.

---

## The kit, after 8 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Four kinds, and they are all genuinely good:

1. **Bank or cash in.** Every turn with a Bomb on the board asks whether to set it off now
   or let it grow 4. It is a real question because the answer keeps changing: growth is
   worth +4/Bomb/turn, `Big Badda Boom` doubles whatever is on the board, and every Set off
   card except `Ka-pow!` is use-it-or-lose-it. Elite 1, turn 3 — 52 damage from two cards —
   was the payoff for two turns of restraint, and it felt earned.
2. **Sequencing inside a turn.** This is the kit's best feature and it is almost invisible.
   Placing a Bomb, setting it off, collecting the Spark from `Pounding Surprise`, and
   *then* affording a Spark-priced card **in the same turn** is a real combo. So is playing
   a Set off card *before* a Bomb card, so the Bomb survives to grow. So is playing skills
   first when the enemy has `Slow`. The same five cards produce noticeably different turns
   in different orders.
3. **Which body gets the Bomb.** With four Wrigglers up, splitting Bomb 11 and Bomb 16
   across two enemies instead of overloading one was a clean, computable decision straight
   off the badges.
4. **Boss-inverted play.** `Slippery 8` turned "one huge hit" into a liability and made me
   deliberately play my *weakest* attacks first. Being asked to play the deck backwards for
   two turns was the most interesting thing that happened.

**(b) What felt automatic, and what never seemed worth playing.**

- **`Strike` and `Defend` are pure filler**, and they are 8 of the 22 cards. About a third
  of my turns were "spend the leftover energy on a Strike". Fight 1 turn 1 had *no*
  decision at all: 3 energy covered every card that wanted energy and still left one for
  Defend.
- **Leftover energy with nothing to spend it on happened repeatedly** (fight 3 turn 1,
  fight 5 turn 1, boss turn 2, boss turn 4). The Bomb-and-payoff cards cost 1 or 2, and the
  hand often has neither, leaving a 1-energy stub.
- **`Careful Now` never seemed worth playing.** It prints Block equal to your largest Bomb,
  and the turns when you have a big Bomb are exactly the turns you are about to set it off,
  so its good and bad states are anti-correlated with what you want to be doing. It gave me
  6 block once and 0 the rest of the time.
- **`Run Away!` and the block half of `Dodoco Cover` were dead** on every turn where the
  enemy's intent was Buff, Debuff, or Status — which was about a third of all turns.
- **The 15-line Elemental Reaction block on every single screen was inert for three whole
  fights**, because the kit is monochrome Pyro and Pyro-on-Pyro just refreshes. It only
  became live because I *chose* an off-colour card out of a reward screen. That is a lot of
  permanent screen real estate for a system a Klee deck may never touch.

**(c) What I could not understand, or that seemed to contradict its own printed text.**

- **The `Mine` text contradicts what a Mine does.** *"A Bomb that also goes off when its
  enemy attacks you"* reads as "the Mine goes off". Twice, what actually happened is that
  **every Bomb on that enemy went off** — a 15-Bomb plus a 4-Mine killed an 11-HP Wriggler,
  and an 18-Bomb stack killed Mawler through a Mine trigger. The `Bomb` keyword's "all at
  once" can be read to cover it, but the two keywords point opposite ways and I had to
  learn the truth by accident. This is load-bearing: it is the difference between "place a
  Mine for free chip damage" and "never place a Mine while banking".
- **`Sharp 2` did nothing visible under `Shrink`.** `Ka-pow! (Sharp 2)` printed *"Deal 4
  damage"* — the same 4 the unenchanted card printed. The arithmetic works out ((4+2)×0.7 =
  4), but on the face it reads as "your enchantment is not applied". `Strike` in the same
  hand had visibly dropped 6 → 4, so the display is honest; it just happens to be
  indistinguishable from a bug.
- **`Slow` charges after the card resolves, and nothing says so.** I predicted 18 and got
  17. The first card you play gets no bonus.
- **The rest site's heal number was wrong by 5** — *"Heal for 30% of your Max HP (18)"* and
  I healed 23. Two sources each promise +5 Max HP and only one +5 landed.
- **`Sharp` and `Nimble` are offered by name on the `Self-Help Book` event with no
  definition anywhere on that screen.** I picked blind.
- **The Spark economy can dead-end and never signals it.** Sparks come only from Bombs
  going off; Bombs only go off if you can pay for a Set off; two of my Set off cards are
  priced in Sparks. Twice I sat holding `Fwoosh!` and `Bang Bang!` both stamped **"CANNOT
  BE PLAYED: you have no Spark"** while a fat Bomb sat undetonated on the enemy. Once that
  happened while I was `Vulnerable` against a 31-damage attack. The cards are honest about
  the immediate refusal; nothing warns you that the loop can close.
- **I still do not know whether Block stops Bomb damage.** The Bomb keyword says only
  Vulnerable and a cap move it, which reads like it ignores Block, but I never got a clean
  test.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** `Careful Now`, for the anti-correlation reason above. Runner-up:
  `Defend`, which I played maybe six times in eight fights and always as filler.
- **Happiest to draw:** `Jumpy Dumpty+`. Not `Big Badda Boom` — `Big Badda Boom` is the
  *payoff*, but its value is decided by what `Jumpy Dumpty+` did two turns earlier. Bomb 11
  for one energy, immune to attack-damage debuffs, growing 4 a turn, and doubled on the way
  out, is the card that made every other card in the deck better. `Ka-pow!` deserves a
  mention as the only Set off that Retains, which makes it the only card that lets you bank
  safely.

**(e) Did the first turn of the first fight already present a decision?**

**Not really — and this is the one I'd fix.** The opening hand was `Ka-pow!`, `Strike`×2,
`Defend`×2 against a 4-damage attack, and 3 energy paid for *everything worth paying for*
with a spare left over for the Defend. There was no cost to weigh. The only judgement
available was whether to spend the free, Retaining `Ka-pow!` now or hold it — a real
question, but one about a 0-cost card with `Set off` printed on it that could not set
anything off, i.e. a decision whose entire content is invisible until you have seen a Bomb.
The kit's first genuine decision arrived on **turn 2**, when `Jumpy Dumpty` appeared and
the bank-or-cash-in question became askable. One Bomb source in the starting hand would
have moved that decision to turn 1 where it belongs.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed `observe` / `act` forms, all through the Bash tool:

- `mkdir -p "$TMPDIR"` and `echo <n> > .../scratchpad/actcount.txt` (and one `cat` of it) —
  the running accepted-action counter the coordinator asked for, kept in the session
  scratchpad. Roughly 40 such `echo` calls, one per batch of actions.
- `sed -n '<range>p'` and `grep -E` piped over the output of `observe`, used throughout to
  re-read just the HP block, the hand list, or the enemy block instead of reprinting the
  whole screen. These filter the bridge's own output and add nothing to it.
- `for c in ...; do ... done` shell loops wrapping several `act` calls in one Bash
  invocation. Each iteration is one ordinary `act`; the loop is only batching.
- `tail -N` / `head -N` on `act` and `observe` output, to trim the JSON echo.

Tools used: **Bash** (as above) and **Write** (once, for this file). No other tool was
called. I did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any other
understudy subcommand.

**Refusals (2, non-consecutive, both identical):** `act "rest"` issued immediately after
`act 'go "RestSite (path N)"'` returned **`error Rest site room is not open`** at two
different rest sites, while `observe` at that same moment printed the rest site with both
`Rest` and `Smith` available. Re-issuing the identical command straight after succeeded
both times. It looks like a race between the map transition and the room becoming
drivable, not a refusal of the command itself. No `TOOL-BLOCKED` and no `REFUSED: ...leak...`
line appeared at any point in the run.

One thing that looked like a bridge defect and was not: partway through I saw the
"The other side" block printed twice. That was my own `sed` invocation supplying two
overlapping ranges, not the bridge duplicating output.
