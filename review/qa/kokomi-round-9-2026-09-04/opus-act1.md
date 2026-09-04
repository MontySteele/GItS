# Blind seat record — KLEEMOD-KOKOMI, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, Kokomi round 9, run 1, act 1.
- **Lane:** 1. **Seed:** `F3BMW33EX9H6`. **Ascension:** 2. **Character:** KLEEMOD-KOKOMI.
- **Act:** 1. **Boss named by the map:** Lagavulin Matriarch (222 HP).
- **Actions accepted:** ~214 accepted `act` calls (cap 250). **Zero refusals** — every command I issued came back `ok: true`. No `TOOL-BLOCKED` screen appeared.
- **Termination reason:** the coordinator's stop condition (1) — act-1 boss resolved, its reward screen handled, lane left standing on the act-2 map (`Ancient (path 1)` offered). Not a budget stop.
- **HP trajectory:** 64/80 (start, A2) → 62 (f1) → 62 (f2) → 56 (f3) → 55 (f4) → 45 (Terror Eel elite) → 42 (Fossil Stalker) → **rest 66** → 53 (Skulking Colony elite) → 50 (Living Fog) → 41 (Gardener elite) → **rest 65** → **40/80 after the boss**.
- **Gold at end:** 195. **Potions held:** none (all five slots empty; Attack, Weak, Blessing of the Forge and Colorless were all spent).
- **Relics:** Tamakushi Casket (starter), Small Capsule, Strike Dummy, Potion Belt, Joss Paper, Bronze Scales, Permafrost.
- **Deck at end (20):** Strike ×4, Defend ×3, Kurage's Oath, Slack Water, Vanguard, Exposed Flank, Stolen Chapter, Undertow, Bennett — Fantastic Voyage, Kujou Sara — Tengu Stormcall *(Steady)*, Thoma — Crimson Ooyoroi, Shinobu — Grass Ring of Sanctification, Chiori — Fluttering Hasode ×2, Kamisato Ayaka — Soumetsu. (One Defend was removed at the shop for 75g.)

**Neow pick: Small Capsule** (obtain a random relic → Strike Dummy). I took it because it was the only option whose value I could price: Phial Holster's two potions are one fight's worth of tempo, and Silken Tress asked for *all* my gold in exchange for "Glam", a word the screen never defined — I refused to pay for an undefined keyword at floor zero.

---

## Fight 1 — Sludge Spinner, 39 HP

**Turn 1** (hand: Defend ×2, Strike ×2, Slack Water). Played **Slack Water** (7 dmg, 1 Weak) → **Strike** → **Defend**.
*Rejected:* Slack Water + Strike + Strike (33 damage, leaves it on 6 and eats a full 8-damage hit). I worked out that both lines kill on turn 2 — 39 HP against two Strikes at 12 — so the block line wins on HP and costs nothing. **This was a real decision and the first turn presented it.**
*Also rejected:* writing Slack Water's Plan ("apply 1 Weak to ALL enemies") onto the Bake-Kurage — against one enemy the Plan is strictly the immediate half, delayed.
Screen and outcome agreed exactly: 39 → 30 is 7 (card) + 2 (Tamakushi Casket firing off the Weak), and the intent redrew from 8 to 6 under Weak.

**Turn 2** (Weak 1 on me; Strikes printed 6). Played **Kurage's Oath onto the Bake-Kurage** (Plan: 7 damage to ALL) → Defend → Defend.
*Rejected:* Strike + Strike + Defend (12 damage, 5 block, take 6). The Plan line took 1 damage instead of 6 and still killed on the same turn, because the Plan is paid now and lands before my next turn's cards. This is the first turn where the pet did something a normal card could not: **it moved damage across the turn boundary and out from under my own Weak** ("your Weak does not" count, exactly as the keyword promises — Oath printed 2 in hand under Weak but the Plan resolved for the full 7).

**Turn 3.** Strike + Strike (18 into 14). No rejected alternative — the kill was arithmetic.

**Reward-screen defect.** On the post-fight screen the Bake-Kurage's last carry-out printed:

> `- LocString table monsters entry SLUDGE_SPINNER.name lost 7 HP`

An unresolved localisation key leaking into player-facing text. Note the *same* line printed correctly ("Sludge Spinner lost 7 HP") on the in-combat screen one action earlier — so it is specifically the end-of-fight reprint that loses the name.

---

## Fight 2 — Toadpole 23 HP + Toadpole 21 HP

**Turn 1.** **Kurage's Oath** immediately (3 to all) → **Strike** → **Strike**, both into Toadpole (2).
*Rejected:* planning Oath for 7-to-all next turn. The immediate 3 was worth more than the delayed 4 because 21 − 3 = 18 is exactly two Strikes: the AoE turned "kill one of them" into "kill the one that was about to hit me for 7". A genuine sequencing choice.
*Rejected:* focusing Toadpole (1), the 23 HP one — it was buffing, not attacking, so it was the safer thing to leave alive.

**Turn 2** (one Toadpole left, 20 HP, **Thorns 2**, hitting 3×3). **Defend** first → **Vanguard** (0-cost Vulnerable) → **Slack Water** → **Strike**.
*Rejected:* leading with Vanguard. I played Defend first specifically so the Thorns retaliation would eat block rather than HP — and it did: block went 5 → 3 on the Slack Water hit. That is a small, real, sequencing decision the screen supported.
*Rejected:* planning Vanguard for Vuln+Weak next turn — I wanted the ×1.5 on this turn's two attacks.

---

## Fight 3 — Seapunk, 44 HP

**Turn 1.** **Bennett — Fantastic Voyage** (I was at 62/80 = 77.5%, above the 70% line → 3 Strength) → **Vanguard** → **Strike** → **Defend**.
*Rejected:* skipping Bennett for a second block card. Bennett is Exhaust, and the branch it takes is decided by an HP threshold I could only fall *below* as the run went on, so the turn I was above 70% was the turn to spend it. **This is the best-designed card I saw all act: the choice is "when", not "whether", and the condition is legible.**
Arithmetic checked out to the point: 44 → 23 is 3 (relic hit ×1.5 Vulnerable) + 18 ((9+3)×1.5).

**Turn 2.** Strike + Strike into 23. **No decision** — three Strikes in hand, 24 ≥ 23, block irrelevant against a corpse. A turn with no rejected alternative.

---

## Fight 4 — Calcified Cultist 41 HP + Damp Cultist 52 HP

Both opened on Buff intents, and the buffs were **Ritual 2** and **Ritual 5** — the Damp Cultist gains 5 Strength *every turn*. That reframed the fight as a race on sight, which is good intent design.

**Turn 1.** **Vanguard onto the Bake-Kurage** (Plan: 1 Vulnerable + 1 Weak) → Strike → two dead Defends.
*Rejected:* Vanguard immediately for +4 on one Strike. Nothing was attacking me this turn, so block was worthless and immediate Vulnerable would have expired unused; the Plan converted a wasted turn into a loaded one. This is the clearest case in the act of the Plan mechanic paying for itself — **the pet gives an idle turn something to do.**
*Honest note:* I still had 2 energy with nothing worth buying. The kit did not offer me a way to bank that energy.

**Turn 2.** Plan landed (Vuln + Weak + 6 HP off the relic double-proc). **Strike + Strike** killed Calcified Cultist for exactly 26. Then **Exposed Flank onto the Bake-Kurage** with the last energy (Plan: 2 Vulnerable to ALL).
*Rejected:* Exposed Flank immediately. Vulnerable applied on my own turn is gone by my next one (I had watched that happen to Seapunk), whereas the Plan version lands *at the start* of my turn and is live for every card I then play. **That asymmetry is the single most interesting rule in the kit and it is not stated anywhere on the card.** I only knew it because I had watched a Vulnerable expire two fights earlier.

**Turn 3.** Slack Water (Weak, cutting the Ritual-inflated hit) → Strike → Defend. **Turn 4.** Strike + Strike for the kill at 23.

---

## Fight 5 — ELITE: Terror Eel, 140 HP, Shriek 70

`Shriek 70 — The first time Terror Eel's HP reaches 70 or below, it becomes Stunned.` A printed, checkable threshold. Excellent: it turned the whole fight into "arrange to cross 70 on a turn where its intent is expensive".

**Turn 1.** Kujou Sara → Strike → **Bennett for 10 Block** (I was at 55/80 = 68.75%, *below* the line).
*Rejected:* holding Bennett for a Strength turn — impossible, HP only falls, so 10 block now was its whole remaining value. The threshold card correctly locked me out, and I could see why.

**Turn 2.** **Vanguard immediately** → Strike → Strike → Defend.
*Rejected:* planning Vanguard. Kujou Sara's +5-this-turn buff was live, so this was the turn to multiply. Vanguard's relic proc (Hydro) hit the Electro aura Sara had left and fired **Electro-Charged**. 21 damage off one Strike, from `9 → (9+5)×1.5`.

**Turn 3 — the turn the kit justified itself.** Eel on 77, threshold at 70, intent 22 + Vigor 6.
Played **Thoma** → **Strike** (crossed 70 → **Stunned**, 22 damage cancelled) → **Slack Water**.
*Rejected:* Slack Water before Strike. I worked the order out on paper first:
- Slack-Water-first: SW applies Hydro, relic refreshes it, Thoma's Pyro Vaporizes → 30 total.
- Strike-first: Thoma's Pyro lands on a bare body and *leaves a Pyro aura*, so Slack Water's Hydro then Vaporizes (10), the relic re-applies Hydro (2), and Thoma's second Pyro Vaporizes that (7) → 33.
I played Strike-first and it produced exactly 19 on the Slack Water beat, as predicted. **This is the best decision the kit gave me all act, and it came from card order alone.**

**Turn 4.** **Kujou Sara first**, deliberately: Electro onto a bare body, then Thoma's Pyro fires **Overloaded** (6 to all + Weak), and the Weak fires the relic for 2 more. Predicted 18, got 18 (41 → 23). Then two Strikes for the kill.
*Rejected:* Strike-first for the bigger single number. Sara's 5 damage plus the reaction chain beat a 14-damage Strike, and the reaction table on screen was enough to compute that in advance.

**Elite cost: 10 HP.**

---

## Fight 6 — Fossil Stalker, 53 HP, Suck 3

`Suck 3 — Whenever Fossil Stalker deals unblocked attack damage, it gains 3 Strength.` A legible "block or lose" clause.

**Turn 1.** **Thoma → Slack Water → Kujou Sara**, for 34 damage off three cards.
*Rejected:* Thoma → Slack Water → **Strike** (14 damage on the third card instead of Sara's 5). I chose Sara because Slack Water's Vaporize would leave the body bare, so Sara's Electro would stick and Thoma's Pyro would then Overload it — 18 from the Sara beat, not 5 — *and* Sara buffs next turn's attacks by 5. Predicted 34, got 34 (53 → 19).
I still leaked 3 unblocked damage and it took its 3 Strength. I had no energy left to prevent it and I record that as a loss I could not have avoided from that hand.

**Turn 2.** One Strike (14 + Thoma's 7 Vaporize) for 21 into 19. Automatic.

---

## Fight 7 — ELITE: Skulking Colony, 75 HP, Hardened Shell 20

`cannot lose more than 20 HP each turn` — a cap, which inverts the usual problem: **surplus damage is waste, so the interesting question becomes how cheaply I can reach 20 and what I buy with the change.** This was the most tactically distinctive enemy of the act.

**Turn 1.** **Weak Potion** (3 Weak, 14 → 10 incoming for three turns) → Bennett (66/80 = 82.5%, **3 Strength**) → Strike → Kujou Sara. Exactly 20, cap reached, `Hardened Shell` displayed as `0`.
*Rejected:* holding the potion for the boss. Against a cap the fight length is fixed at four turns minimum, so the incoming total was knowable (three attacks) and Weak was worth ~12 HP right there.

**Turn 2.** **Thoma → Slack Water** hit the cap on two cards; **Shinobu** free for 4 block; **third energy deliberately unspent**.
*Rejected:* Kurage's Oath with the spare energy — it would have been pure waste against a filled cap. **This is the only turn in the act where the correct play was to hold energy, and the kit gave me nothing to bank it into.** The cap creates the interesting question and then the deck has no answer.

**Turn 3.** Undertow (capped, 28 → 8) + Defend. **Turn 4.** Strike for the kill.
**Elite cost: 13 HP.**

---

## Fight 8 — Living Fog, 80 HP (+ Gas Bomb minion)

**Turn 1.** Chiori → Strike → Defend. Little choice; hand was three Defends.
It answered with `Smoggy 1 — You can only play 1 Skill per turn`, which is a sharp constraint against a kit whose good cards are mostly skills.

**Turn 2.** Vanguard (spending my one skill on the Vulnerable) → Strike → Strike → Slack Water, for 54.
*Rejected:* Thoma or Chiori — Smoggy allowed exactly one skill and Vanguard at 0 cost with a ×1.5 attached to three attacks beat both.

**Turn 3.** It summoned a **Gas Bomb** (7 HP, Death Blow 8) with `Minion 1 — Minions abandon combat without their leader`. One Strike into the 8 HP leader ended the fight and the bomb never resolved. **Rejected:** killing the bomb first, which the minion text explicitly told me was the wrong order. Good, readable interaction.

---

## Fight 9 — ELITE: 4× Phantasmal Gardener, 26 / 31 / 29 / 30

`Skittish 6 — The first time Phantasmal Gardener is hit each turn, it gains 6 Block.`

**Observed inconsistency.** Kujou Sara hit Gardener (3) for 5 and it gained Block 6, as printed. In the *same beat* Thoma's 5 Pyro hit Gardener (2) for 5 and it gained **no block at all**. Either Thoma's rider is not "a hit" for Skittish's purposes, or Skittish did not fire; nothing on either screen distinguishes the two cases. I could not resolve it from printed text.

**Turn 1.** Thoma → Sara into (3) → Strike into (2).
*Rejected:* focusing one Gardener down. With Skittish charging a 6-block toll on the first hit per target per turn, and Thoma's rider firing at a *random* enemy, I could not aim my way out of the toll anyway. I record that as the kit's weakest moment: **the fight wanted precise targeting and Thoma took the targeting away from me.**

**Turn 2.** Strike into the 14 HP one — it died, and the list **immediately renumbered**, so "(2)" now named a different creature with different HP. The screen warns about this in a footer, and the warning is earned: my next two commands had to be re-planned from a fresh `observe`. Then Strike into (1) and Undertow into (2).

**Turn 3.** Strike killed the 3 HP one; Slack Water Vaporized into the last; Shinobu + Defend for 9 block, which zeroed the incoming.

**Turn 4.** **Vanguard first, then Undertow.** This is the one place Undertow's own text made the decision: `Deal 7 damage. If the enemy has a debuff, deal 10 instead.` Vanguard's Vulnerable *is* the debuff, so 0 energy converted Undertow from 7 into 10×1.5 = 15 against a 9 HP body. Clean, legible, and entirely readable off the two cards.
**Elite cost: 9 HP.**

---

## Fight 10 — BOSS: Lagavulin Matriarch, 222 HP

Opening state: `Block 12`, `Plating 12 — At the end of your turn, gain 12 Block. Plating is reduced by 1 at the start of your turn.`, `Asleep 3 — Awakens upon losing HP or after 3 turns.`

**Turn 1.** Thoma → Slack Water → Strike → Shinobu, for 30 raw into 12 block = 18 HP, which woke it.
*Rejected, and this was the hardest call of the run:* stalling two turns without damaging it, to play Bennett for permanent Strength on a free turn and let Plating tick down. I rejected it on a guess I could not check — that Plating's block would **accumulate** across sleeping turns and I would face 36+ block on the turn it woke. **That guess was never resolvable from the screen: nothing printed says whether an enemy's block persists between turns.** I broke the tie by attacking, and got lucky: waking it deleted `Plating` outright (it vanished from the power list), so the block problem simply ended. A player who stalled would have learned something different, and neither of us could have known in advance.

**Turn 2.** It woke **Stunned** — a free turn I had not paid for. Spent **Blessing of the Forge** on a five-card hand, then **Vanguard+ → Exposed Flank+ → Strike+ → Strike+** for **61 damage** (204 → 143) and Vulnerable 3.
*Rejected:* Defend+ over the second Strike+ (8 block for 18 damage) — with 222 HP on the board and 65 on mine, the arithmetic said the fight was a race I could only win by shortening.

**Turn 3.** **Kujou Sara first** for Overloaded off the standing Pyro aura, which also applied Weak and cut the incoming 18 to 12 — then Undertow, then Strike. 44 damage.
*Rejected:* Undertow first for the bigger single Vaporize. Sara-first bought the Weak, and the Weak was worth about 5 HP a turn in a fight I expected to last four more.
*Rejected:* spending both potions here. I held them one turn deliberately, because Sara's +5 lands on the *following* turn and Vulnerable still had a turn to run — a real, and correct, patience decision.

**Turn 4.** Hand came up all skills. **Attack Potion** → took **Undertow** over Deep Current and Feint (10-if-debuffed beat 6, and Vulnerable was live). **Colorless Potion** → **skipped all three**: Eternal Armor cost my whole turn, Purity did nothing, and **Panic Button's** 30 block came with "you cannot gain Block from cards for 2 turns", which against 19-a-turn with 40 HP is a delayed loss. Then Undertow → Chiori → Bennett (10 block, below the line again) → Defend, for 15 block against 12 incoming: **zero damage taken.**

**Turn 5.** It went Debuff+Buff — no attack — so I spent everything on damage: Undertow → Sara (Electro-Charged off my own Hydro) → Strike+. It answered with **Strength −2 and Dexterity −2 on me**.

**Turn 6.** Boss on 32, me on 40, its intent 21. **Exposed Flank+ → Strike → Strike.** Predicted 3 + 18 + 18 = 39 against 32, killed it with the second Strike.
*Rejected:* Slack Water for Weak, which would have shaved the 21 — unnecessary once I had checked that the kill was on.

**Boss cost: 25 HP. Cleared at 40/80.**

---

## The kit, after 10 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three kinds, and they are genuinely different from each other:

1. **Card order inside a turn**, because of the aura rules. Fight 5 turn 3 (Strike-first for 33 rather than Slack-Water-first for 30) and fight 6 turn 1 (Sara-third for 18 rather than Strike-third for 14) were both decided purely by which element would be clinging to the body when the next hit landed. **This is the kit's best idea.** It is computable in advance from the on-screen keyword table, it rewards reading, and it made two otherwise routine turns interesting.
2. **Now versus at the start of next turn**, via the Plan. The trade is legible — you pay full price this turn for a bigger effect that lands before your next hand. It won three separate turns for me (fight 1 turn 2, fight 4 turns 1 and 2), and it wins hardest on turns where nothing is attacking me, because it converts an idle turn into a loaded one. The Vulnerable case is the sharpest: `Exposed Flank` planned gives Vulnerable that is *live during my whole next turn*, where the same card played directly gives Vulnerable that expires before I can use it.
3. **Threshold timing.** Bennett's 70% line and Terror Eel's Shriek 70 both made me schedule a turn around a number. Both were checkable on screen. Both were satisfying.

**(b) What felt automatic, and what never seemed worth playing.**

- **Roughly a third of my turns had no decision in them.** Fight 3 turn 2, fight 6 turn 2, fight 8 turn 3, fight 10 turn 6 were all "the arithmetic says the kill is on, play the attacks". That is normal for the genre, but it is worth saying that every one of those turns was a *Strike* turn: the basics are where the decisions aren't.
- **Defend is close to dead weight in this kit.** With Thoma, Shinobu and Bennett all producing block as riders, I played a bare Defend for its own sake maybe four times in ten fights, and I spent 75 gold to delete one.
- **Kurage's Oath's immediate half** (3 damage to all) was never worth a card outside fight 2; the Plan half was worth it three times. A card whose two halves are that far apart in value is really one card and one trap.
- **Vanguard's Plan mode** I used once. Its 0-cost immediate mode is almost always better, because the whole point of a free card is that it multiplies the *rest of this turn*.

**(c) What I could not understand, or that contradicted its own printed text.**

This is the longest section, and I think the most useful.

1. **Card damage previews are inconsistent about which buffs they include.** Strength shows up (Strike printed 12 under Strength 3). Vulnerable never does. Kujou Sara's +5 sometimes does and sometimes does not: in fight 5 round 2 the screen showed `Fantastic Voyage 5` active and Strike printing **9**, and that Strike dealt **21**; four fights later, the same buff active, Slack Water printed **15**, which *does* include the +5. I cannot construct a rule that fits both.
2. **`Undertow` ignores Strength in its preview entirely.** With Strength 3 up it printed `Deal 7 damage` — its unmodified base — and then dealt 20+ (capped). Strike, in the same hand, printed its Strength correctly.
3. **The Plan half of a card previews Vulnerable; the immediate half does not.** Kurage's Oath printed `Deal 3 damage to ALL enemies. Plan: Deal 10 damage to ALL enemies` against a Vulnerable target — the 10 is 7×1.5, so the Plan line is doing the multiplication and the immediate line above it is not. Two numbers on one card, computed under different rules.
4. **`Strike Dummy` says "Cards containing 'Strike' deal 3 additional damage", and it is buffing Slack Water.** On the deck/removal screen Slack Water prints `Deal 4 damage`; in combat it prints `Deal 7`. Strike prints 6 and 9 respectively — the same +3. Kujou Sara prints 5 on both screens, so the relic is *not* simply hitting every attack. "Slack Water" contains no "Strike". Either the relic's matching rule or its printed text is wrong.
5. **Powers are displayed under the wrong card's name.** Kujou Sara's rider consistently appears as `Fantastic Voyage 5 (buff) — Your Attacks deal 5 additional damage this turn` — Bennett's card name — including in fights where **Bennett was never played**. (On the turn it is granted it correctly reads `Tengu Stormcall 1`; it is renamed when it becomes active.) Likewise Chiori — Fluttering Hasode's power displays as `Tamoto`.
6. **Elemental-Charged displays as `Poison`.** The keyword box says `Electro-Charged — The reacted enemy loses 4 HP at the start of its turn, 1 less each turn`; the body shows `Poison 4 (debuff) — At the start of its turn, loses 4 HP, then reduce Poison by 1`. Same effect, two names, and a player reading the keyword box will look for "Electro-Charged" on the body and not find it.
7. **Debuffs on me are tagged `(buff)`.** `Strength -2 (buff)` and `Dexterity -2 (buff)`.
8. **`Steady` is sold before it is defined.** The Waterlogged Scriptorium charged me 55 gold for "Enchant a card with Steady" and the *card-selection screen that followed* still did not define it. The word only resolved — `Steady — This card gains Retain` — in the "what you have picked" preview *after* I had paid and chosen a target. I paid for an effect I could not read.
9. **`Skittish` did not fire for Thoma's rider** (see fight 9), and nothing on screen says why.
10. **`The Moon Overlooks the Waters` — "Plans also happen when played"** — I could not parse. Does a Plan card played normally also do its Plan half, or does a card written onto the Kurage also resolve immediately? Those are very different cards. I declined it twice for that reason.
11. **Nothing on any screen says whether an enemy's Block persists between turns**, which is exactly the fact the boss's opening asks you to bet on.

Against all of that, one thing was **unusually good**: the reaction previews that started appearing on cards mid-run (`*Reaction preview: Vaporize* — Pyro meets Hydro: this hit deals 1.5x damage and consumes the aura`) are the single most useful line the interface printed, and the long Elemental Reaction keyword — including its warning that a re-applied aura can hide a reaction that did happen — let me predict five separate multi-step beats to the exact HP. **Where this kit explains itself, it explains itself better than most games do. The problem is that it does not do it consistently.**

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** **Defend**. In a kit where Thoma, Shinobu and Bennett all hand you block as a rider on something else, a card that only gains 5 block is the card you play when the turn has already gone wrong. Runner-up: Kurage's Oath's immediate half.
- **Happiest to draw:** **Kujou Sara — Tengu Stormcall**, without much competition. It is 1 energy for damage, an element that sets up next turn's reaction, and a +5 that makes the following turn the big one — so it is simultaneously a play *now* and a decision about *next* turn. It was the card that made card order matter. **Thoma — Crimson Ooyoroi** is a close second for the same reason: it turns every attack into an elemental question.

**(e) Did the first turn of the first fight already present a decision?**

**Yes.** Hand was Defend ×2, Strike ×2, Slack Water against a 39 HP Sludge Spinner intending 8. Slack Water's Weak visibly redrew the intent from 8 to 6, and the choice — third card Strike (33 damage, take 6, kill turn 2) versus third card Defend (21 damage, take 1, still kill turn 2) — was a genuine trade I had to do arithmetic to settle, and settling it correctly saved 5 HP. The Bake-Kurage was on the field and legible from turn one, and the "play a card on it to write its Plan instead" line was on screen before I needed it. **The kit opens with a decision, and it opens with its centrepiece visible.**

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, run through the Bash tool from the repo root with `GITS_LANE=1`:
- `GITS_LANE=1 python -m understudy.blindplay observe`
- `GITS_LANE=1 python -m understudy.blindplay act "<command>"`

No other `understudy` subcommand was run — no `harness state`, no `scenario`, no `staged_turn`, no `soak`.

Other tool use, in full:
- **Bash**, for my own scratch and for trimming output only: one `mkdir -p` creating the scratchpad directory `…/scratchpad/kokomi-r9-seat/` (which I ultimately never wrote into); and shell plumbing around the two allowed commands — `cd` to the repo root, `&&` chaining of several `act` calls into one invocation, `>/dev/null` to discard `act` receipts I did not need, and `| sed -n '…p'`, `| grep -n`, `| head -N` to re-read one block of an `observe` rather than the whole page. No command read, wrote or searched any repo file.
- **Write**, once, for this record.

No other tools were used. No repo file, YAML sheet, C# source, doc, packet, or other seat's record was opened at any point.
