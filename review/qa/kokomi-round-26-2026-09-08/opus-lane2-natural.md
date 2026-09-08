# Kokomi round 26 — Opus blind seat, lane 2, natural draft

## Identity

- **Model and seat:** Opus (claude-opus-5), blind TESTER seat, lane 2.
- **Run seed:** never printed. No screen the bridge showed me carried a seed.
- **Character:** Kokomi (never named on any screen; identified only by the
  starting relic **Tamakushi Casket** and the **Bake-Kurage**).
- **Ascension the run opened at:** never printed.
- **Act, floor and boss:** Act 1, floor 17 — the boss room. The map printed
  **"At the top of this act: Soul Fysh"**, and I reached it: **Soul Fysh,
  211/211**, left at **136/211** when the budget ran out.
- **Actions accepted:** **240 of 240 — budget reached.** The bridge's own
  counter; the last two acts returned `actions: 239 of 240` and
  `actions: 240 of 240`.
- **Termination reason:** **the action budget**, mid-turn, in round 7 of the
  boss fight. I stopped on the cap rather than spending the last acts on an
  `end turn` that would have taken a telegraphed 18 (against my 17 HP while
  carrying Vulnerable 2) and ended the run — a budget stop is a complete
  round; a death is a different thing and I was not asked to reach one.
  **I did not tear the lane down.**
- **A mid-round interruption, declared:** for roughly half an hour the bridge
  appeared to hang — six consecutive calls returned nothing. I wrote a first
  version of this record on the belief the lane had stalled. It had not: the
  shell's bare `python` resolves to the Windows Store alias and had begun
  blocking on launch. The coordinator identified this and supplied the venv
  interpreter; every call from that point used it. No game state was lost and
  no act was wasted — my count and the bridge's agreed on resumption once a
  late-arriving `play "Defend (1)"` from the stalled window landed. This file
  is the **second** Write, replacing the first at the same path.
- **HP trajectory:** 64/80 → 56 → 53 → 44 → 32 → 29 → 25 → 21 → 17 → 16 → 15 →
  10 (end fight 5) → **rest 34** → 8 (end elite) → 5 (Slippery Bridge) →
  **rest 29** → 18 (end fight 7) → 18 (through fight 8, taking 0 for three of
  its four turns) → **rest 42** → 35 → 29 → 23 → **17** at the cap.
- **Gold:** 68.
- **Potions held:** Stable Serum, Radiant Tincture (never used). Spent: Block
  Potion and the first Radiant Tincture in fight 5; Swift Potion and Energy
  Potion in fight 8.
- **Relics:** Tamakushi Casket, Fishing Rod, Gremlin Horn, Rainbow Ring,
  Sword of Stone.
- **Deck at the end** (reconstructed from hands and pile counts — the bridge
  never prints a deck list outside a fight): 4 Strike, 3 Defend, 1 Defend+
  (Fishing Rod), Slack Water, Night Watch, Feint, Battle Plan, War Council,
  Cleansing Wave, Read the Field, Mika — Starfrost Swirl, Riptide, Treatise,
  Second Wave. Kurage's Oath was **removed** at the Slippery Bridge.
  Starting deck was 10: 4 Strike, 4 Defend, Kurage's Oath, Slack Water.

**Neow pick:** **Fishing Rod** ("Every 3 normal combats, Upgrade a random card
in your Deck"). *Why:* of the three rows, the page said of both others that
"this option's own words promise a card and the feed carried no face for it" —
I would have been buying names I could not read, and Neow's Bones also printed
a Curse. Fishing Rod was the only option whose whole effect was on the screen.

**What I was offered and what I took** (natural draft — nothing was added to my
starting deck before play):

| Fight | Offered | Took |
|---|---|---|
| 1 | Stolen Chapter, **Night Watch**, Shell Guard, Gorou — Crystal Collapse | Night Watch |
| 2 | Ripple, **Feint**, Undertow, Thoma — Blazing Barrier | Feint |
| 3 | Song of Pearls, The General's Banner, **Battle Plan**, Bennett — Fantastic Voyage | Battle Plan |
| 4 | **War Council**, Tide Chart, Well Laid, Freminet — Pressurized Floe | War Council |
| 5 | The Moon A Ship O'er the Seas, Second Thoughts, **Cleansing Wave**, Kujou Sara — Crowfeather Cover | Cleansing Wave |
| Elite | Stolen Chapter, The Moon, War Council (2nd), **Mika — Starfrost Swirl** | Mika |
| 7 | **Riptide**, The General's Banner, War Council (3rd), Shinobu — Grass Ring | Riptide |
| Shop | (full list under fight 7) | **Treatise** 37g, **Second Wave** 51g, Energy Potion 48g, Swift Potion 49g |
| 8 | Salt Line, Stolen Chapter, **Read the Field**, Shinobu — Sanctifying Ring | Read the Field |

I passed a second and third **War Council**, once for Mika (to reach an
Elemental Reaction, which no screen had yet let me see) and once for Riptide
(the only large AoE on offer). Mika was the pick I was least sure of and it
turned out to be the most load-bearing card in the deck; see fights 7 and the
boss.

---

## Fight 1 — Sludge Spinner (38/38)

**Turn 1** (HP 64; incoming Attack 8 *and also* a Debuff). Wrote **Kurage's
Oath** on the Bake-Kurage as a Plan (7 to ALL next turn) and played two Strikes
(12). *Rejected:* three Strikes for 18 now. Oath-as-a-Plan buys 7 for one
energy against Strike's 6. That one-point premium, for a turn of delay, is the
whole decision — thin, but real, and it is the kit's central question stated on
turn one. 38→26, exactly 12.

**Turn 2** (HP 56, Weak 1 on me; enemy telegraphing 11). Plan carried out for 7
(26→19). Played **Slack Water** face-up, then Strike, then Defend. *Rejected:*
writing Slack Water as a Plan — its Plan line is "Apply 1 Weak to ALL enemies",
which would arrive a turn after the blow it was meant to soften. Face-up, the
Weak landed now and the printed intent fell 11 → 8. Sharpest decision of the
fight, made on the turn. The Casket answered the Weak with 2 Hydro; the enemy
lost 9 (19→10). Every number matched its face.

**Turn 3.** 10 left, two Strikes for 12. No rejected alternative — but this was
the two-turn plan paying off, not a dead turn.

---

## Fight 2 — Corpse Slug (1) 27/27 [A], Corpse Slug (2) 25/25 [B]

Both carried **Ravenous 4** — "When an enemy dies, Corpse Slug immediately eats
it, becoming Stunned and gaining 4 Strength." That printed line shaped the
fight.

**Turn 1.** Wrote Kurage's Oath (7 to ALL is 14 points across two bodies for one
energy) and Struck A twice. *Rejected:* Oath face-up for 3 to ALL. Against two
enemies the Plan's premium doubles; this is the first place the mechanic reads
as plainly correct rather than marginal. Took 8.

**Turn 2** (HP 45, Frail 2). The fight's real decision: **which slug to kill
first.** A sat on 8 and only applied debuffs; B was on 18 and attacking.
Killing A would hand B +4 Strength. I put everything into B (Slack Water 4 +2
Casket, Strike 6) and wrote **Night Watch** for its Dusk Plan. *Rejected:*
killing A, which was cheap and would have fed the healthy body. Ravenous turns
"kill the low one" into a trap and the card said so before I acted.

**Here the screen and the outcome disagreed.** Night Watch prints "Dusk Plan:
Gain 4 Block and apply 1 Weak." After the Dusk resolve, **A** — the front body,
which was *not* attacking — lost exactly 2 HP, i.e. the Casket answering a Weak
that landed on A. But B's attack was 3×2 = 6 and I lost only **1** while
carrying Frail 2, which should have cut a printed 4 Block to 3: 6 − 3 = 3, not
1. The two readings each explain half: Weak-on-B makes the damage exact
(2×2 − 3 = 1) but leaves A's 2 HP unexplained; Weak-on-A explains the 2 HP but
not the Block. In the same situation in fight 3 turn 1 (no Frail) the card gave
exactly 4 Block and 7 − 4 = 3, dead on. So Night Watch's Block is 4 and
behaves; what I cannot account for is that one turn.

**Turn 3.** Both on 6. Strike A, Strike B; B ate A, was Stunned, and died in the
same beat. No alternative — but it was turn 2's focus decision paying off.

---

## Fight 3 — Toadpole (1) 21/21 [A], Toadpole (2) 22/22 [B]

**Turn 1.** Night Watch written, Strike B, Feint B. *Rejected:* holding Feint
for a turn on which a Plan resolves. This is where I learned the timing by
losing it: **Night Watch's Dusk Plan resolves at the *end* of my turn, so it
cannot switch on a Feint played earlier in the same turn.** Feint printed 5 and
dealt 5. To power Feint you must write a *non-Dusk* Plan on turn N and play
Feint on turn N+1. That is a genuine two-turn structure, and it is legible from
the two keyword boxes — but only if you read them against each other, which I
did not do until after I had spent the card.

**Turn 2** (HP 41). B had gained **Thorns 2** off A's Empower and A was
attacking 3×3. Wrote Kurage's Oath and put both Strikes into B to kill it.
*Rejected:* Oath face-up plus a Defend, which keeps me above 40. I took the full
9 to remove the *buffer* rather than the attacker, because B was the body
handing A Thorns. Right call, and a fight-level decision rather than a
turn-level one.

**Turn 3.** Plan for 7 (19→12), two Strikes for the kill. The kill screen
printed "The Bake-Kurage's last carry-out ... printed here because a Plan whose
kill ends a fight never reaches a battle screen" — a piece of care I noticed and
appreciated, since otherwise the jellyfish's last act is invisible.

---

## Fight 4 — Calcified Cultist 41/41 [A], Seapunk 46/46 [B]

Eight rounds, 87 enemy HP against my 32. The fight that taught me the kit.

**Turn 1** (incoming 11). Slack Water face-up on B (Weak the attacker),
**Battle Plan** written, one Defend. *Rejected:* Slack Water as a Plan, same
reasoning as fight 1. Took 3.

**Turn 2 — the payoff turn, and the clearest thing the kit does.** Battle Plan's
carry-out drew 2 and left "**Battle Plan 1 — The next Attack you play face-up
this turn deals 4 additional damage**". Every attack redrew with the rider
folded in: Strike printed 10, Feint printed **9 / 14**. Feint's condition ("If a
Plan was carried out this turn") was satisfied by Battle Plan's own carry-out,
so one card was worth 14 for one energy. Feint on the Cultist for exactly 14
(41→27), then Defend+ and Defend for 13 against 17. *Rejected:* writing Kurage's
Oath and eating 9 for a bigger turn 3. At 29 HP I took the 4. Note the display
quirk: **both** attacks printed the rider though only the first can consume it.

**Turn 3 — a SAFE turn with three Plan-capable cards.** See the Debrief.

**Turn 4.** Two Plans resolved: Oath 7 to ALL, Battle Plan's draw-2 plus rider.
The Cultist sat on 18 with Ritual 2 and Strength 4; Seapunk was **untouched at
40 because it had spent the previous turn Blocking** — the carry-out landed in
Block it had raised on its own turn, exactly as the Bake-Kurage panel warns
("A Plan is carried out before you play anything, so it lands in whatever Block
the enemy is still standing in from its own turn — you cannot strip that Block
first"). That warning is not decoration; it cost me 7 damage and I had read it
and still walked into it. Then Feint at 14 + Strike at 6 killed the Cultist
exactly, and Defend+ covered most of Seapunk. *Rejected:* spreading damage,
which leaves the Ritual body alive. The decision was made two turns earlier.

**Turns 5–8.** A grind. Turn 5's decision was defensive and real: Slack Water
and Night Watch both apply Weak, and the Casket answers *each* application, so
two Weak-appliers is 4 free damage plus a blunted swing — I took 0. Turn 6 the
Seapunk telegraphed Buff + Defend, i.e. **no incoming**, and I dumped 17
damage; *rejected:* writing a Plan, precisely because the Block it was about to
raise would eat the carry-out. That is the sharpest Plan decision in the run,
and the screen gave me everything needed to make it. Turn 7 it stood in 7
Block, so I chewed through with Slack Water then Strike; turn 8, two Strikes
for the kill against a 16-point swing into my 16 HP.

---

## Fight 5 — Haunted Ship (63/63)

**Turn 1** (no attack; intent read Debuff *and* "give you 5 Status cards").
Wrote Kurage's Oath, two Strikes. Took the debuff: **Weak 3**, and the draw pile
went 9 → 14.

**Turn 2** (HP 16, incoming 13). Feint (7, powered by the carry-out and cut by
my own Weak), Night Watch, Defend+. Block 12 against a telegraphed 13 — and I
took **0**, because the Dusk Weak landed before the ship acted. First time I
trusted Dusk in advance, and it held.

**Turn 3.** War Council face-up (Weak to ALL, so the Casket fires and the swing
shrinks), Battle Plan written, Defend+. Took 1.

**Turn 4** (HP 15, three unplayable **Dazed** in a seven-card hand). Spent
**both potions** — Radiant Tincture for a fourth energy and three turns of it,
Block Potion for 12 — and played Slack Water (carrying the rider), two Strikes
and a Defend for 16 damage and nothing taken. *Rejected:* saving them for the
boss. At 15 HP against a 33-HP body hitting for 13, the boss was not somewhere
hoarding would get me.

**Turns 5–6.** Wrote Oath, Struck, Night Watch; took 5; the Plan brought the
ship to 2 and a Strike ended it.

The Status cards were legible: "Unplayable. Ethereal" with a plain
`CANNOT BE PLAYED` line, and Ethereal cleaned them up.

---

## Fight 6 (Elite) — four Phantasmal Gardeners, 30/28/26/31

Each carried **Skittish 6** — "The first time Phantasmal Gardener is hit each
turn, it gains 6 Block." 115 HP against my 34. The fight the kit is built for,
and the one where the draft, not the turns, did the deciding.

**Turn 1.** Slack Water on C (the 7-damage body — Weak where it mattered),
Night Watch, Cleansing Wave face-up. 9 Block, took **1**. Also learned: C took
Slack Water's 4 and *then* raised 6 Block, which ate the Casket's answering 2 —
so Skittish's Block lands **after** the hit that triggers it.

**Turn 2.** Wrote Kurage's Oath, two Defends. *Rejected:* Oath face-up for 3 to
ALL — 7 to ALL is 28 points across four bodies against 12. Took 7.

**Turn 3.** The Plan hit all four for exactly 7 — **Skittish did not blunt it**,
because the four hits arrive in one beat. Then the real decision: I wrote **War
Council** (Plan: "Deal 5 damage and apply 1 Weak to ALL enemies" — the Casket
answers each of the four Weaks, so 7 a body, 28 in total, *plus* a quarter off
every incoming attack) and took 6 behind 13 Block. *Rejected:* War Council
face-up, which is 8 damage and 0 taken. I paid 6 HP for +20 damage.

**Turn 4 — the turn the fight was won on.** Four bodies on 14/14/8/17 = 53. I
wrote **both** Kurage's Oath and War Council (56 points of scheduled damage for
two energy) and played one Defend, dropping to 8 HP behind 5 Block against 17.
*Rejected:* one Plan and two Defends — HP 14 and three more turns against bodies
that scale. The two Plans resolved next turn and killed three of the four
outright, leaving the last on 3. This is the Bake-Kurage as an engine rather
than a gimmick, and it is the best moment of the run: I could compute the whole
thing off the printed faces before committing, and it came out to the number.

**Turn 5.** Strike for the last 3.

---

## Fight 7 — Calcified Cultist 38/38 [A], Damp Cultist 53/53 [B]

B carried **Ritual 5** — five Strength a turn, compounding.

**Turn 1** (both Empower, no incoming). Battle Plan written, Feint face-up (5,
unpowered), Night Watch written for its 2 points of Casket damage. *Rejected:*
Defends, worthless on a turn with no attack.

**Turn 2.** Wrote **War Council**, Struck A for 10 under the rider, Defended.

**Turn 3 — the Elemental Reaction, and a face that lied.** Both bodies wore
Hydro Aura from my own Hydro cards. I played **Mika — Starfrost Swirl** (Cryo,
5 to ALL). Both took 7 (5 + the Casket's 2, since **Frozen** is a debuff) and
both came out **Frozen 1** — "Its next action deals 50% less damage. Until it
acts, an Attack Shatters it for 6 unblockable damage and removes Frozen."
Their printed intents halved on the spot (9 → 4, 4 → 2). And the Hydro Aura
read **2** afterwards rather than gone — precisely the case the Elemental
Reaction box spends a sentence warning about: "the aura is consumed and
RE-APPLIED inside the same beat, so no screen ever shows it gone and the
reaction looks as though it did not happen." I would have filed that as a bug
if the screen had not told me first. It is the best piece of writing on any of
these pages.

**But:** on that same screen **Feint printed "Deal 5 damage. If a Plan was
carried out this turn, deal 10 damage instead"** — showing 5 — even though War
Council's Plan *had* carried out at the start of that turn (it is what took A
from 31 to 14). I played Feint into the Frozen Damp Cultist and it went
**39 → 23**, i.e. **16 = 10 + 6 Shatter**. The card did the right thing; the
face under-reported by 5. In fights 4 and 5, and again on the boss (below), the
same card previewed correctly, so this is not "Feint never previews" — it is a
face that got it right four times and wrong once. **A blind player trusting the
face there would mis-sequence a lethal.**

Mika's "next Attack costs 1 less" also printed **cost 0 on all three attacks in
hand**, with an honest footnote ("it is what this card costs now, not what it
costs"). Same over-display shape as the Battle Plan rider.

**Turns 4–5.** A died to Strike + Shatter; Gremlin Horn refunded the energy and
drew. B's Strength climbed 5 → 10 → 15 while I ground it from 39 to 5, then
killed it on the turn its intent read 16 against my 18 HP. *Rejected* each
turn: writing another Plan — with Ritual 5 on the board, damage a turn from now
is worth less than damage now, the exact inverse of the elite. **That the kit
contains both of those turns is the strongest argument that the Plan is a real
decision and not a tax.**

**Shop** (244 gold): shelves were Pincer 50, Undertow 52, Battle Plan 75, Second
Wave 51, Treatise 37, Gorou — Juuga 75, Durin — Binary Form 149, Bellows 293,
Whetstone 173, Ghost Seed 208, Swift 49, Energy 48, Liquid Bronze 76, Card
Removal 75. Bought **Treatise**, **Second Wave**, Energy Potion, Swift Potion.
*Rejected:* Whetstone and Card Removal — I wanted engine over polish.

---

## Fight 8 — Corpse Slug ×3, 25/27/26

**Turn 1** (HP 18, incoming 14 of my 18 — a threshold). Hand held three
Plan-capable cards; see the Debrief. Wrote **War Council** and **Night Watch**,
played Defend+. Block 12 against 12 after the Dusk Weak → **0 taken**, and 21
points banked. *Rejected:* Riptide face-up for 27 across three bodies, which
would have left me on 4 Block against 14.

**Turn 2.** The Plan hit all three for 7. Then the fight's decision: **kill one
slug on purpose.** Slack Water + Strike + Strike into A. A died — and **both**
survivors ate it: both **Stunned**, both **+4 Strength**. Ravenous fires on
every body, not one. That is a whole free turn bought for +4 Strength on each,
and it is the read of the fight. *Rejected:* spreading damage to keep all three
alive and slow, which the Stun makes strictly worse.

**Turn 3 — where I made my own worst mistake, and it was a reading mistake.**
I had started filtering the screen through `grep` to save room, and my filter
dropped the aura lines. I planned the turn on the belief both slugs still wore
Hydro Aura, played Mika expecting a Frozen reaction and a Shatter, and got
neither: the auras had lapsed, so Mika simply applied Cryo to bare bodies —
5 damage each, no debuff, no Casket, no Shatter for the Feint that followed.
B survived on 2 where I had it dead. **The screen had the line and I had
thrown it away.** The recovery was Treatise + three Defends, which fired
Rainbow Ring (Attack + Skill + Power in one turn) for +1 Strength and +1
Dexterity and produced **exactly 14 Block against exactly 14 incoming**.

**Turn 4.** Now the auras were legible again — B Hydro, C **Cryo** (Mika's).
Slack Water killed B; C ate it and was Stunned; **Feint into C's Cryo aura
reacted to Frozen** and took it 14 → 6; Strike + the 6-point Shatter finished
it. Three cards, no damage taken, and every step of it came off aura lines I
had ignored the turn before.

---

## Fight 9 (Act 1 boss) — Soul Fysh, 211/211

The first boss screen adds a rule to the Frozen box that I had not seen:
"**Bosses cannot be Frozen: Hydro plus Cryo is consumed and applies 2
Vulnerable instead.** A Minion beside the boss still Freezes." Printed before I
could get it wrong, and it converts my accidental Cryo splash into a real
opener.

**Round 1** (intent: 2 Status cards, no attack — SAFE). Treatise, **Mika**
(Cryo aura), **Slack Water** (Hydro into that aura → the reaction → **2
Vulnerable** on the boss, plus Weak, plus the Casket). 211 → 194.
*Rejected:* writing Riptide as a Plan. Setting Vulnerable first is worth more
than 13 scheduled damage, because everything after it is multiplied — that is
a genuine sequencing choice and the boss rule is what creates it.

**Round 2** (incoming 16). Strike under Vulnerable, Night Watch, Defend+.
Block 12 against 12 after the Dusk Weak → **0 taken**. 194 → 182.

**Round 3 — a SAFE turn with three Plan-capable cards.** See the Debrief.
Wrote **Second Wave**, then **Read the Field**, then **Battle Plan**, and took
the telegraphed 7 on the chin. Next turn opened with **Block 20** — Read the
Field's Plan is 10 and Second Wave doubled it exactly, as printed. That combo
is clean, checkable, and it is the one card interaction in the run I could
verify to the point.

**Round 4 — and the one place the screen gave me nothing.** The boss's intent
had read "**Empower (Buff)** — this part strengthens the enemy's own side ...
the feed carries no target for an intent part, so this page cannot say which
body it lands on". No name, no number. I spent the turn I had spent two turns
building: War Council face-up to hang a debuff, then **Riptide** under the
Battle Plan rider — 9 + 4 (debuff) + 4 (rider) = 17 on the faces, 19 with the
War Council hit. The boss went **182 → 180**. It had bought **Intangible 1 —
"Reduce all damage taken and HP loss to 1"**, and every hit was reduced to 1.
**Nineteen points of built-up damage became two, and nothing on the screen
before I committed said it would.** This is the single largest gap between what
the pages told me and what happened, and unlike the Feint face it is not an
arithmetic slip: it is a whole turn of planning with no information to plan
against. Intangible is legible *after* the fact — the buff prints its own text
plainly on the next screen — but the intent that applies it is anonymous.

**Round 5** (Intangible still up, incoming 13). Night Watch + Defend; took 6
and declined to attack into a damage cap, which is the correct play and also a
turn with no decision in it.

**Round 6** (2 Status cards, no attack — SAFE; hand held two Plan-capable
cards). Wrote Second Wave then Battle Plan, played Mika face-up. 179 → 169.

**Round 7 — the budget.** Second Wave had doubled Battle Plan: I drew to a
ten-card hand (5 + 4 from the doubled draw + 1 from Treatise) and the rider
arrived stacked — **Feint printed "Deal 13 damage. If a Plan was carried out
this turn, deal 21 damage instead"**, i.e. base 5 + 8 of rider. I played it and
the boss went **169 → 148: exactly 21**, the face's own conditional number,
correctly pre-computed. Slack Water and War Council followed for another 12,
and the counter read `240 of 240`. Boss left on **136/211**, me on 17 with
Vulnerable 2 and an 18-point swing telegraphed.

---

## The kit, after 9 fights

**(a) Which decisions felt like real choices, and what they traded off.**

1. **Face-up or Plan, on every Plan card you hold.** The kit's spine, and
   genuinely two-sided, because the answer flipped inside one run. At the elite
   (fight 6 turn 4) the Plan was obviously right — 7-to-ALL beats 3-to-ALL by
   16 points across four bodies, and two Plans banked in one turn is 56
   scheduled damage. Against Ritual 5 (fight 7) it was obviously wrong — a turn
   of delay is a turn of +5 Strength on the thing hitting me. Made on the turn,
   informed by the fight.
2. **Weak now versus Weak later** (fights 1, 4, 6). Slack Water and War Council
   both read "apply now" face-up and "apply to ALL next turn" as Plans, and a
   telegraphed number makes that concrete. On the turn.
3. **Do not write a Plan into Block the enemy is about to raise** (fight 4
   turns 4 and 6). The Bake-Kurage panel states it, and it turns an enemy's
   "Defend" intent into an instruction about *this* character.
4. **Sequencing the reaction before the payload** (boss round 1). Cryo, then
   Hydro, then everything else — because the boss rule converts the reaction
   into 2 Vulnerable and multiplies what follows. At the draft *and* on the
   turn.
5. **Killing a body on purpose to buy a Stun** (fight 8 turn 2). Ravenous makes
   a kill a defensive move; the +4 Strength is the price.
6. **The Battle Plan → Feint chain**, and **Second Wave → Read the Field**.
   Both are two-card, two-turn structures that pay exactly what they print
   (14 and 21 on Feint; 20 Block off a printed 10). Drafted, then cashed.

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend and Defend+ are pure arithmetic** — "how much of the printed number
  do I need" — and never once competed with another Defend.
- **Strike was automatic and, past floor 8, embarrassing:** 6 damage against
  bodies of 46, 53 and 211. It only mattered carrying a rider or a Shatter.
- **Night Watch never presented a decision.** Its face says "Play on the
  Bake-Kurage" — there is no face-up mode — so the only question is whether to
  spend the energy, and at 4 Block + a Weak + 2 Casket damage for 1 the answer
  was always yes. A good card that asks nothing.
- **Cleansing Wave's Plan mode (10 Block) I used once and its face-up mode
  three times**; 10 Block a turn from now rarely beats 5 Block and a debuff
  removed now.
- **Attacking into Intangible** (boss round 5) — the one turn where the correct
  play was to do nothing offensive, which is legible but not interesting.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **The boss's anonymous Empower intent, and Intangible** (boss round 4).
   Nineteen points of prepared damage became 2, and the screen carried no
   warning it could. This is the finding I would act on first: the intent for a
   buff that caps damage should be distinguishable from the intent for a buff
   that adds Strength, because a Plan-based kit *commits a turn in advance* and
   cannot re-plan when the cap lands.
2. **Feint's face printed 5 on a turn a Plan had carried out** (fight 7 turn 3)
   and then dealt 10 — verified 39 → 23 with a 6-point Shatter in the same hit.
   The same card previewed correctly four other times, including the boss's
   round 7, where it printed 21 and dealt exactly 21.
3. **The fight-2 turn-2 Night Watch resolve.** The Casket's 2 landed on the
   front body, which says the Weak went there; the damage I absorbed only adds
   up if it went to the other. One of the two must be wrong.
4. **"Next Attack" riders print on every attack in hand.** Battle Plan's +4 and
   Mika's cost cut both redraw every eligible card as though each would get it.
   The buff text is honest and Mika's footnote is scrupulous, but a player
   reading faces will over-count. I did once, and only caught it by arithmetic.
5. **Multi-part intents are unreadable by design** — "Aggressive (Attack) — 8 …
   and also: Strategic (Debuff)", with the page saying its feed "carries nothing
   that says which of those parts resolve, in what order, or on what
   condition". I would rather it said that than guessed, but it means several
   turns were planned against a number I could not fully trust.
6. **Skittish's ordering I had to learn by experiment** (Block lands after the
   triggering hit; a four-body AoE in one beat is not blunted at all). Not the
   kit's card, but it decided the elite.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted: Strike.** Past the first two fights it was 6 damage in a world
  of 40-, 53- and 211-HP bodies.
- **Happiest to draw: War Council.** Its Plan does 5 to every body, the Casket
  answers every Weak with another 2, and the Weak cuts the whole enemy side's
  damage — one energy, offence and defence, scaling with the number of enemies.
  Close second is **Mika**, purely for what it unlocked: the reaction, the
  Shatter, and the boss's Vulnerable rule, all off one 1-cost card I nearly
  passed.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, but a thin one.** Three Strikes, a Defend and Kurage's Oath against a
38-HP body telegraphing 8: "18 damage now" versus "12 now and 7 at the start of
next turn". That is the kit's central question, so opening on it is right. It
is thin because at one enemy the premium is a single point and nothing on that
board punishes either answer — the same choice at fight 2's two bodies (12
versus 14) is the one that actually teaches you. The panel explaining it is
also about 300 words to read before playing a Strike.

---

## Debrief

> List every turn that was SAFE (no lethal, no threshold, incoming covered or
> absent) where you held three or more Plan-capable cards. For each: what you
> wrote, what you played face-up, and whether anything other than Block
> competed with writing another Plan. Name the card that competed and what it
> bought, or say nothing did.

Taking "Plan-capable" to mean a card whose face carries a `Plan:` or `Dusk
Plan:` line — Kurage's Oath, Slack Water, Night Watch, Battle Plan, War
Council, Cleansing Wave, Read the Field, Riptide, Second Wave. Not Strike,
Defend, Feint, Mika, Treatise.

Across the 41 turns I played I held **three or more** Plan-capable cards on
**seven** turns, and only **three** of those were SAFE. The rest of the time
the hand was Strikes and Defends. That scarcity is itself an answer about the
shape of the deck.

**1. Fight 4, turn 3 — SAFE.** HP 25, Block 0. The Cultist telegraphed 11; the
Seapunk telegraphed Empower + Defend, i.e. nothing. 11 was comfortably
coverable (Defend, Defend, and Night Watch's 4 in hand). Hand: **Night Watch,
Kurage's Oath, Battle Plan**, Defend, Defend.
- **Wrote:** Kurage's Oath (7 to ALL) and Battle Plan (draw 2 + the rider).
- **Played face-up:** nothing. Night Watch is forced onto the jellyfish by its
  own text, so it is a Dusk *write*, not a face-up play. Zero Defends.
- **Did anything other than Block compete?** **Nothing did.** The only other
  cards were two Defends, and I declined both — I chose to take 4 rather than
  spend an energy on Block. There was no attack in hand at all. The turn's real
  question was "two Plans, or one Plan and a Defend", which is Plan-versus-Block
  and nothing more.

**2. Fight 6 (elite), turn 1 — SAFE, marginally.** HP 34, incoming 15 across
three attackers; I covered all but 1 point. Hand: **Cleansing Wave, Night
Watch, Slack Water**, Strike, Strike.
- **Wrote:** Night Watch only.
- **Played face-up:** Slack Water on the 7-damage body (4 damage, 1 Weak, +2
  Casket) and Cleansing Wave (5 Block).
- **Did anything other than Block compete?** **Yes — Slack Water competed and
  won.** As a Plan it is "apply 1 Weak to ALL enemies" next turn; face-up it
  applied Weak *before* three telegraphed attacks landed and switched on the
  Casket. What it bought was the difference between 15 incoming and about 11,
  on a turn where 9 Block was everything I had. This is the one SAFE turn where
  the competition was not Block but *the same card's own face-up half*, and the
  tempo beat the 4 extra scheduled damage. Cleansing Wave's Plan (10 Block next
  turn) I declined for the same reason: Block that arrives after the punch is
  not Block.

**3. Act-1 boss, round 3 — SAFE.** HP 42, incoming 7 (one printed part of a
multi-part move), trivially coverable. Hand: **Battle Plan, Read the Field,
Second Wave**, Feint, Defend.
- **Wrote:** all three — Second Wave first, then Read the Field, then Battle
  Plan. Order was the decision: Second Wave's Plan is "the next Plan carried
  out with this one is carried out twice", so writing it *ahead* of Read the
  Field turned a printed 10 Block into **20**, which is what the next screen
  showed.
- **Played face-up:** nothing. I spent all three energy on writes and took the
  7 rather than Defending.
- **Did anything other than Block compete?** **Yes — Feint competed, and it
  lost.** Face-up it was worth 5 that turn (no Plan had carried out at the start
  of it), against a 211-HP boss. What writing the third Plan bought instead was
  20 Block plus a doubled draw, which is what let the following two turns
  happen at all. Naming it properly: the competition was a 5-damage attack, and
  5 damage into 211 is not a competitor.

**The four non-SAFE turns on which I held three Plan-capable cards**, for
completeness: **fight 6 turn 3** (19 incoming against 13 available Block — not
covered; I wrote War Council anyway and ate 6), **fight 6 turn 4** (17 incoming,
HP 26 → 8), **fight 7 turn 5** (16 against 18 HP — a threshold; I killed instead
of writing), and **fight 8 turn 1** (14 against 18 HP — a threshold by the
letter of the definition, though I did cover it to zero; hand was Night Watch,
Riptide and War Council, I wrote War Council and Night Watch, played Defend+
face-up, and **Riptide competed** — 27 points across three bodies face-up
against 21 scheduled plus the Weak that made the block hold. The Weak won,
because 4 Block against 14 was not survivable twice).

> for every turn where you played an Attack after a "next Attack" rider was
> showing, say whether you planned the turn around it and what it added

Five turns. The rider came only from Battle Plan, always as a Plan carried out
at the start of the turn.

1. **Fight 4, turn 2.** Played **Feint** first, for **14** (41 → 27, exact).
   **Planned:** entirely — I wrote Battle Plan the turn before for this, and
   sequenced Feint ahead of the Strikes so the +4 sat on top of Feint's
   Plan-doubled 10 rather than on a 6-damage Strike. **Added:** +4 raw, but the
   real gain was stacking with Feint's own condition, which the same carry-out
   satisfied — one Plan turned one card from 5 into 14.
2. **Fight 4, turn 4.** **Feint for 14** into an 18-HP Cultist, then a Strike
   for the last 4. **Planned:** yes; the Feint-first ordering is why the body
   died that turn instead of taking another Ritual tick. **Added:** it made an
   18-HP kill cost two energy.
3. **Fight 7, turn 2.** **Strike** for **10** (31 → 21). **Planned:** weakly — I
   had written Battle Plan mainly for the draw. **Added:** +4 on a 6-damage
   card, i.e. it made my worst card briefly acceptable. That is the honest read
   on this rider: on Feint it is a combo, on Strike it is a patch.
4. **Act-1 boss, round 4.** **Riptide** under the rider — 9 + 4 (I played War
   Council first precisely to hang a debuff on the boss) + 4 = 17 on the face.
   **Planned:** yes, over two turns, and it is the most carefully planned turn
   of the run. **Added: two points of HP.** The boss was **Intangible** and
   every hit was capped at 1. The rider added nothing because nothing could.
5. **Act-1 boss, round 7.** The rider arrived **doubled** by Second Wave —
   Feint printed "13 / 21" against its usual "5 / 10", i.e. +8 rather than +4.
   Played Feint for exactly **21** (169 → 148). **Planned:** yes. **Added:** 8
   of the 21, and a confirmation that Second Wave doubles a Plan's *effect*
   (the rider's size), not merely its trigger.

> if you drafted a card that counts Plans against a fixed number, show your own
> count of how many Plans it needed and check it against the face

I drafted one, and I can now check it.

- **Treatise** (bought, 37g, power): "**Once per turn**, when the Bake-Kurage
  carries out a Plan, draw 1 card." The fixed number is the cap: one, however
  many Plans resolve. **My count against the face, twice:**
  - Boss round 4, with **two** Plans carrying out (Second Wave and Read the
    Field): standard draw 5 + Battle Plan's Plan-draw 2 + Treatise **1** = **8**
    cards. The screen showed **8**. Not 9 — so the cap held against two Plans.
  - Boss round 7, with **two** Plans carrying out (Second Wave and the doubled
    Battle Plan): 5 + 4 (the doubled draw-2) + Treatise **1** = **10**. The
    screen showed **10**. Cap held again, and it held even when Second Wave was
    doubling the other Plan in the same beat.
  So Treatise's fixed number is 1 and the game pays exactly 1. **Face and
  outcome agree, checked twice.**
- **Well Laid** was the card that counts *upward* — "Deal 2 damage" with
  "*Damage from carried-out Plans* — 2, plus 3 for each Plan the Bake-Kurage
  carried out at the start of this turn." I was offered it after fight 4 and
  **skipped it** for War Council, so I never got to audit it. Had I taken it,
  my count on boss round 4 (two Plans) predicts 2 + 3 + 3 = **8**, and **5** on
  the many single-Plan turns. Unverified — I did not draft it.
- **Second Wave** multiplies rather than counting against a fixed number, so it
  is not the card the question asks about; its own claim ("the next Plan
  carried out with this one is carried out twice") I did verify — 10 Block
  became 20, and a draw-2 became a draw-4.

---

## Non-blindness declaration

**Repo files read: none.**

Caveats on this round, both declared rather than hidden:

- **This is the second Write to this path.** I wrote a complete record earlier
  in the session, in good faith, believing lane 2 had stalled unrecoverably.
  It had not. This file replaces it and covers the whole run; nothing in the
  first version was based on anything I did not see, and its factual content
  is carried forward here.
- **I changed the Python interpreter mid-round.** Calls up to act 183 used the
  bare `python` on PATH. That binary resolves to
  `…/AppData/Local/Microsoft/WindowsApps/python` (the Windows Store alias) and
  began failing with "Permission denied" while producing no output, which I
  misread as a hung lane. I then ran the same two allowed commands through
  `…/AppData/Local/Python/bin/python`, and after the coordinator's instruction
  through `C:/Users/Monty/Documents/GitHub/GItS/.venv/Scripts/python.exe`,
  which is what every call from that point used. **Only the interpreter path
  changed; the commands did not.**

Tools used:

- **Read tool**, three times: once on my brief at
  `…\scratchpad\r26-seat-lane2.md` (which the brief permits), and twice on the
  harness's own background-task output files under `…\913fe618-…\tasks\`
  (`b5gfwl346.output`, `b24l1ewhc.output`), to recover the stdout of bridge
  calls the shell had moved to the background. Both held only
  `understudy.blindplay observe` output — the same text the tool would have
  printed to me — or were empty.
- **Write tool**, twice: the superseded record, and this file.
- **Bash tool.** Every game action was one of the two allowed commands, always
  `GITS_LANE=2 <python> -m understudy.blindplay observe` or
  `GITS_LANE=2 <python> -m understudy.blindplay act "<command>"`, run from
  `C:/Users/Monty/Documents/GitHub/GItS`. I ran **no** other understudy
  subcommand — no `harness state`, no `scenario`, no `staged_turn`, no `soak`.

Commands I ran in Bash **outside** the two allowed ones — all shell plumbing
over the bridge's own output or over the harness's task files, none of them
touching the repository:

- `cd`, on every call.
- `head`, `sed -n`, `awk`, `grep`, `tail`, `wc -c`, `cat` — to trim or re-read
  text an `observe`/`act` had just printed, and (`cat`/`wc`) to read the two
  task-output files named above. **This filtering cost me a fight-8 turn:** my
  `grep` dropped the aura lines and I planned a reaction that could not happen.
  Recorded under fight 8 as my error, not the game's.
- `>/dev/null` redirects, to suppress the JSON echo of an `act` already decided.
- A `for i in …; do … done` loop, once, to issue four `buy` commands in order.
- `which -a python python3 py` and `ls …/AppData/Local/Programs/Python`, to
  find a working interpreter during the apparent stall.
- `timeout 90 env GITS_LANE=2 python -m understudy.blindplay act 'end turn'` —
  an attempt to bound the blocked call; it produced no game output.
- One failed `… > "$TMPDIR/obs.txt"` redirect (`$TMPDIR` unset). No file created.
- `sleep 1`, once.

I did not look at any YAML sheet, C# source, doc, packet, review material, or
another seat's record. Everything above comes from what the bridge printed.

The lane was **not** torn down.
