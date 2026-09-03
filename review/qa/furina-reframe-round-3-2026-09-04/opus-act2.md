# Furina round 3, act 2 — blind seat record

## Identity

- **Model / seat:** Opus (Claude Fable 5.1), blind TESTER seat, KLEEMOD-FURINA, **lane 1**.
- **Run seed:** not printed on any screen I saw. The bridge never showed a seed; I did not go looking for one.
- **Character:** Furina (inherited mid-run).
- **Act:** 2. Boss named on the act-2 map: **Knowledge Demon**. I never reached it.
- **Neow pick:** none, inherited. This was the second of chained seats: I took the lane on the act-2 map with the previous seat's deck, relics and potions, and made no Neow pick.
- **Actions accepted:** **126** `act` calls (counter kept in scratchpad `count.txt`; hand recount of the transcript agrees).
- **Termination reason:** **not a budget** — the run ended. `end turn` on round 3 of the act-2 Elite returned
  `TOOL-BLOCKED: game_over` / `the run is over; there is nothing left to play` / `The run ended on floor 25.`
  I stopped there, as instructed. Budget remaining at death: 124 actions of 250, well inside the wall clock.
- **HP trajectory:** 77/85 (first fight, act-2 floor 1 — the lane had healed off the 45/85 handover) → 72 → 67 (Doll Room, −5) → 66 → 54 → 41 → 40 → 37 → 36 → 17 (Bowlbugs turn 2) → 8 → 7 → **dead** on floor 25.
- **Gold:** never printed on any screen the bridge showed me. Collected during my leg: 15 + 19 + 19 + 12 + 100 (Lantern Key) = **165 gained**; starting total unknown, and I never reached a shop.
- **Potions held at death:** none. Belt over the leg: Shackling (inherited, spent on the Bowlbugs), Swift (spent on the Thieving Hopper), Colorless (spent on the Bowlbugs), Cunning (spent on the Elite).
- **Relics at the end:** Ethereal Spotlight (start of turn, add an Ethereal Spotlight to hand), Silver Crucible (first 3 card rewards Upgraded; first Treasure Chest empty), Tiny Mailbox (2 potions on Rest), Nutritious Soup (on pickup, enchant all Strikes with Tezcatara's Ember), Daughter of the Wind (play an Attack → 1 Block).
- **Deck at the end:** the bridge has no "show deck" screen, so this is what I saw pass through hands, not an authoritative list. Soloist's Solicitation ×3 (one carrying *Tezcatara's Ember*, one carrying *Slither*, a third that showed sometimes as Ember and sometimes as Slither), Chevreuse — Interdiction Fire+ ×2 and one unupgraded Interdiction Fire, Chevreuse — Ring of Bursting Grenades+, Charlotte — Framing: Freezing Point Composition+, Lisa — Lightning Rose, Lynette — Enigmatic Feint, Navia — Cannon Fire Support, Thoma — Blazing Barrier, Gorou — General's War Banner, Diona — Icy Paws (picked up), Amber — Fiery Rain (picked up), Stage Presence, Stage Combat, Regal Bearing, Macaron Break+, Aria of Recompense, The Crowd Answers, Suffering for Art (picked up), Duet+ (picked up), An Invitation, Salon Début, Casting Call.
- **Picks I made:** Nutritious Soup (Tezcatara event); Doll Room "Take Some Time" → Daughter of the Wind; card rewards Suffering for Art, Duet+, Diona — Icy Paws, Amber — Fiery Rain; Lantern Key → Return the Key (100 gold).

---

## Fight 1 — Exoskeleton (1) 26/26, Exoskeleton (2) 24/24, Exoskeleton (3) 25/25

All three carried `Hard To Kill 9 — Reduce all damage taken and HP lost by Exoskeleton to 9`. I read that as a hard cap of 9 per instance, and the fight bore it out: two 9-damage cards each removed exactly 9.

**Turn 1** (3 energy; incoming 1×3 and 8). Played Soloist's Solicitation (showing cost 0, 9 damage) on Exo (2), then Chevreuse — Interdiction Fire+ (9) on the same target, then Lisa — Lightning Rose, then Stage Presence.
*Rejected:* Regal Bearing instead of Stage Presence. Weak on the 8-damage attacker saves 2, so 3 Block + Weak = 5 prevented against Stage Presence's 6. A real, small, arithmetic choice — the first turn did present one.
*Rejected:* holding Lisa for a turn with more targets. I kept it because a 3-turn end-of-turn tick is worth more the earlier it starts in a 75-HP-across-three-bodies fight.
The cap made the interesting call the *reverse* of normal: **Vulnerable is worthless here** (9 × 1.5 caps back to 9), so Lisa's value was its flat 5 and its Electro, not its debuff.

**Turn 2** (Exo(1) 21 with Electro Aura, Exo(2) 6 with Pyro Aura, Exo(3) 25 with Strength 2). Played Chevreuse — Ring of Bursting Grenades+ (12 to ALL → 9 each after the cap), which reacted **Overloaded** off Exo(1)'s Electro for 6 more to all. That killed Exo(2) and left 6 and 10. Then Charlotte — Framing on the 6-HP body to kill it.
*Rejected:* Charlotte first on the Strength-2 body, so the Pyro AoE would land as Melt. Melt's 1.75× is **entirely eaten by the cap** (12 × 1.75 = 21 → 9), so the reaction I could have set up was worth literally nothing, and killing the 8-damage attacker was worth 8. This was the best decision of the fight and it came from reading two printed rules against each other.
End of turn, Lightning Rose's Electro hit the last Exoskeleton's Pyro aura → Overloaded → 5 + 6 killed it. Fight over in two turns, 8 HP lost.

**Reward:** took Suffering for Art (0 cost, lose 1 HP, gain 3 Encore) over Mademoiselle Crabaletta, Standing Ovation and Freminet. Reason: I had spent the whole fight with `Ethereal Spotlight — CANNOT BE PLAYED: you have no Encore` in hand every single turn, and this was the only card offered that unblocked it. **At that point I still did not know what Encore was** — the card and the relic both spend it and neither says what it is.

## Fight 2 — Thieving Hopper 79/79 (Escape Artist 5)

**Turn 1** (3 energy; incoming 17 plus a card-debuff). Hand was entirely Encore generation and block: no attack but Stage Combat. Played Suffering for Art, Stage Combat, Aria of Recompense, The Crowd Answers, then Ethereal Spotlight, then Stage Presence.
The screen then told me the thing the whole act turned on:
> `Encore: 10 — a buffer and not a bank: after Block it absorbs incoming damage before HP.`
That reframed every Encore card from "resource" to "second health bar", and it is printed **only on the combat header once you hold some** — never on the cards that grant it.
*Rejected:* holding Ethereal Spotlight rather than paying 2 Encore for it. I paid because it Exhausts at end of turn regardless (Ethereal) and the relic re-adds one every turn, so 2 Encore was the standing price of a permanent buff. It resolved into `Guest Cast 1 — Companion cards are Spotlighted: 50% stronger printed damage and Block`, and Chevreuse — Ring of Bursting Grenades+ in my hand visibly went **12 → 18**. That is the clearest, most satisfying feedback the kit gave me all act.
Took 0 HP damage: 10 Block plus Encore ate the 17.

**Turn 2** (Hopper 76, buff intent, so a free turn). Played An Invitation (0) for a random Common Companion — it produced a second Chevreuse — Interdiction Fire — then Soloist (9), Interdiction Fire+ (13), Interdiction Fire (10), then Lisa. Pyro landed, then Lisa's Electro reacted Overloaded for 6 to all. 79 → 33.
*Rejected:* Regal Bearing for block. The enemy was buffing, so block was strictly wasted; the escape timer (5 turns to deal 79) made damage the only currency.

**Turn 3** (Hopper 33, now `Flutter 5 — Receives 50% less damage from Attacks. Deal attack damage 5 times to Stun it`, incoming 21). Played Navia — Cannon Fire Support first (a power: +3 Block per Companion play), then Charlotte (Cryo), then Chevreuse (Pyro on Cryo → **Melt**, 1.75×).
*Rejected:* Lynette — Enigmatic Feint for 7 Block. Navia first turns each of the two Companions into block *and* damage, which beat Lynette's flat 7 by 1 and left the power up for the rest of the fight.
The order mattered and paid: 33 → 18, which is 15, i.e. Charlotte's halved 4 plus Chevreuse's halved-Melt 11. Sequencing Cryo-then-Pyro was a genuine +5.

**Turn 4** (Hopper 13, Flutter 3, Escape Artist 2). Played both Soloists (13 → 6, Flutter down to 1), then spent **Swift Potion** to dig for a finisher, drew Chevreuse — Interdiction Fire+ and killed it.
*Rejected:* holding the potion and finishing next turn. I judged the escape timer plus Flutter's halving made "next turn" a coin flip, and the kill returned the stolen card. Correct in hindsight.

**Reward:** took Duet+ over Breathless+, The Final Verdict and Lisa — Violet Arc. Duet+ doubles a Companion and draws 2 in a deck that is mostly Companions. I rejected The Final Verdict flatly — see (c).

## Fight 3 — Spiny Toad 117/117

**Turn 1** (buff intent, free turn). Charlotte (Cryo) → Chevreuse+ (Pyro → Melt) for 21, then Lisa.
*Rejected:* Salon Début to start the salon engine. `a member with no Encore to spend performs at three-quarters` and I had 0 Encore, so the engine's own text told me it would be running at a discount for nothing.

**Turn 2** (Toad 91, `Thorns 5`, incoming 23). Chevreuse+ into the Electro aura → Overloaded (6 to all, 1 Weak, 23 → 17), then The Crowd Answers, which paid its **reaction clause** (4 Encore + draw 2) because I had sequenced the reaction first. Then Ethereal Spotlight (2 Encore) and Macaron Break+.
*Rejected:* Stage Combat, my free 3-damage attack. Under Thorns 5 it deals 3, gains 4 Block and costs me 5 — a **0-cost card that is actively negative**. Thorns turning the free filler into a trap was one of the two moments the board rewrote my hand's value.
*Rejected:* skipping Spotlight to keep 2 Encore of shield. I paid it because 117 HP is a long fight and 50% on every Companion compounds.

**Turn 3** (Toad 71, incoming 17). An Invitation → Thoma — Blazing Barrier. Duet+ → Study Buddy, then **Thoma doubled: 14 Block**. Then Soloist (9), Suffering for Art, Aria. Ended on 15 Block + 8 Encore against 17 → took **0**.
*Rejected:* Stage Presence + Aria without Duet (15 mitigation, not 23). This was the turn the kit's pieces genuinely clicked: a draw-2 skill, a random-Companion generator and a doubler combined into an exact-fit defensive turn. It felt built, not drawn.

**Turn 4** (Toad 57, buff intent). Navia (power) → Chevreuse+ → Soloist.
*Rejected:* Aria for 5 Encore with the spare energy. Navia is permanent and I expected 3+ more Companion plays; Encore is one-shot.

**Turn 5** (Toad 32, Thorns 5 back, incoming 23). Regal Bearing (Weak → 17), Chevreuse+ (13, eating 5 thorns), Macaron Break+. 10 Block + 9 Encore vs 17 → took 0 HP, minus 5 to thorns.
*Rejected:* the pure-defence line (Regal + Macaron + Crowd Answers, 0 damage dealt). Paying 5 HP for 13 damage was worth it against a 32-HP body.

**Turn 6** (Toad 19, Pyro aura). Charlotte's Cryo into Pyro → Melt for 15, then Soloist for 9. Dead.

**Reward:** took Diona — Icy Paws over Blocking Notes+, Double Time and Stage Lights. Diona is a *Companion*, so it is 9 Block under Spotlight and pulls Navia's 3 on top — 12 for one energy. Double Time was dead (I had no Salon Member and no reliable way to get one).

## Fight 4 — Bowlbug (Rock) 45/45, Bowlbug (Silk) 41/41, Bowlbug (Egg) 22/22

I entered at 37/85 against 108 HP and 22 incoming. This is the fight that lost the run.

**Turn 1.** Spent **Shackling Potion** (all enemies −7 Strength), dropping the turn's incoming from 22 to 8, then Chevreuse — Ring of Bursting Grenades+ (12 to all) and Diona (6 Block).
*Rejected:* saving the potion for the boss. At 37 HP with three bodies I judged the run would not reach a boss otherwise. I still think that was right; it is also the reason I had nothing left for the Elite.

**Turn 2** (Rock 33, Silk 29 4×2, Egg 10 + 7 block, incoming 30, and I was **Weak**). Salon Début (rolled Mademoiselle Crabaletta, which performed on arrival), Stage Combat, Soloist, Stage Presence, then Lisa as the Companion that makes Crabaletta perform.
*Rejected:* an all-block line (Stage Presence + Stage Combat + Salon) which mitigates 11 of 30 and deals nothing. I had no line that mitigated 30 and said so to myself at the time: **the turn presented no good option, only least-bad ones.** Took 19. 36 → 17.

**Turn 3** — the best turn of the leg, and the one that showed the kit at its ceiling. At 17 HP with 22 incoming and **no block card in hand**: An Invitation → Gorou — General's War Banner; Duet+ (draw 2, and Gorou queued to double); **Colorless Potion** → Dramatic Entrance (11 to ALL, free this turn); then Gorou doubled, Macaron Break+, Dramatic Entrance.
Result: 12 Block, 3 Encore, Egg **dead**, Rock 23 → 6, Silk 25 → 4. Crabaletta performing twice off the doubled Gorou did far more than the three-quarters I had budgeted for.
*Rejected:* Flash of Steel and Nostalgia from the potion. Dramatic Entrance's AoE was the only card that changed the enemy count.
Then the printed rule paid off exactly: `Imbalanced 1 — If Bowlbug (Rock)'s attacks are fully blocked, it becomes Stunned`, and 12 Block + 3 Encore against 15 **counted as fully blocked** — Rock came up Stunned. Worth flagging: **Encore spent as buffer satisfied "fully blocked"**, which I would not have predicted from the printed text of either.

**Turn 4.** Lynette (a Companion) made Crabaletta perform and killed the 3-HP Rock. Silk had already died to Lightning Rose.

**Reward:** Amber — Fiery Rain over Deep Breath, Crescendo and The Guest List+. A Companion that is 4×3 AoE, triggers Navia and Crabaletta, and reads 6×3 under Spotlight.

Then the map gave me exactly one node — Unknown → Elite — with no alternative. The Unknown was the Lantern Key; I took the 100 gold rather than "Fight to obtain the Key" at 17/85. The Elite was then **forced**.

## Fight 5 — Infested Prism 161/161 (Elite) — the run ends

`Vital Spark 2 — ALL Skills are Tainted 2`, and every skill in my hand grew the line `Gain 2 Tainted`, whose keyword gloss reads, in full: *"Tainted — Gain 2 Tainted when played."* **The card never says what Tainted does.** I played the first one blind and only then did the header explain it: `Tainted 2 (debuff) — Take 2 additional damage from Attacks this turn.`

**Turn 1** (17 HP, 161 enemy, incoming 15). Amber (Pyro, 12) → Charlotte (Cryo into Pyro → Melt, 10) → Macaron Break+. 5 Block + 3 Encore against an intent that had risen 15 → 17 because of the one skill I played. Took 9. **17 → 8.**
*Rejected:* Chevreuse — Ring of Bursting Grenades+ for 12 at 2 energy; Amber + Charlotte gave 22 for the same 2 and set up the Melt.

**Turn 2** (8 HP, incoming 11). Diona + Stage Presence (12 Block, 4 Tainted → intent 11 → 15) + Soloist + Chevreuse (2 Block off Daughter of the Wind, 18 damage). Took exactly 1. **8 → 7.** Enemy 139 → 121.
This turn is the clean statement of the Elite's problem: my defensive cards are all Skills, and every one I play hands the enemy back a third of what it gives me.

**Turn 3** (7 HP, intent `5 damage 3 times`, enemy 121 with 11 block). I had no block card in hand — only Aria (Encore), Salon Début, Lisa, and two attacks. I spent Cunning Potion for three 0-cost Shivs (3 Block off the relic), played Salon Début hoping to roll **Gentilhomme Usher** — the one line I could construct that survived, since Usher performing twice plus Aria's 5 Encore came to 13 mitigation against a 19 intent. It rolled **Mademoiselle Crabaletta**.
With Usher off the table I checked every remaining line and none of them mitigated the 15–21 incoming from 7 HP: attacks-only left me at 5 Block against 15; adding Aria bought 5 Encore for +2 Tainted on each of three hits. I said so at the time and played the highest-damage line — Chevreuse and Soloist — rather than pretend a survival line existed.
`end turn` → `TOOL-BLOCKED: game_over`. **The run ended on floor 25.**

The honest verdict on the death: I lost the run three rooms earlier, at 37 HP going into a three-Bowlbug fight I had to spend a potion to survive, and then the map offered one node and it was an Elite. The Elite itself was legible and I do not think I misplayed its three turns; I think I arrived at it dead already.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit's best decisions were all *sequencing* decisions, and there were more of them than I expected:

- **Element order.** Charlotte-then-Chevreuse is Melt (1.75×); Chevreuse-then-Charlotte is nothing. Same two cards, same two energy, +5 damage for reading the aura line. Against the capped Exoskeletons the same reasoning inverted and told me the reaction was worth *zero* — which is a better teaching moment than the reaction being good.
- **Reaction-before-payoff.** `The Crowd Answers` doubles (4 Encore + draw 2 vs 2 + draw 1) if a reaction has already fired this turn. That single clause turned a filler card into a card I had to plan a turn around.
- **Spotlight as a purchase.** Paying 2 Encore — i.e. 2 points of my own damage buffer — for a permanent 50% on every Companion is a clean, real trade, and it is legible the instant you play it because the numbers in hand visibly change.
- **Encore vs Block.** Once the header told me Encore is a buffer, "5 Encore" and "6 Block" became comparable in a way that made every skill choice a small arithmetic problem. Encore carries between turns, Block does not; Block satisfies "fully blocked" checks and, as it turned out, so does Encore.
- **Duet+ on the right Companion.** Doubling Thoma for 14 Block on a turn I needed exactly 14, then doubling Gorou on a turn with no block cards at all, were the two most satisfying plays of the leg.
- **Board rules rewriting the hand.** Thorns 5 made my 0-cost attack a negative card. Hard To Kill 9 made my big AoE and all Vulnerable worthless and my small hits perfect. Flutter halved attacks but not Lightning Rose's tick. Tainted punished exactly the half of my deck that keeps me alive. Four different enemies each re-ranked my hand in a different direction, and that is the strongest thing I can say about this act.

**(b) What felt automatic, and what never seemed worth playing.**

- **Soloist's Solicitation** is close to automatic: when it shows cost 0 you play it, and there is no turn where you would not.
- **Casting Call** ("Your Salon has room for 1 more Salon Member") I drew four or five times and **never once played**. With 0 or 1 members on stage it does nothing at all, and I never got to 3.
- **Salon Début** I played twice and both times it was a shrug: the member is random, it performs at three-quarters without Encore, and it only acts again when I happen to play a Companion. The one time it mattered was the Elite, where I needed a specific roll and got a 1-in-3.
- **Stage Combat** was automatic-good (free damage + block) right up until Thorns, and then automatic-bad. Nice.
- **Aria of Recompense** became automatic once I understood Encore: with spare energy and no better target, 5 Encore is never wrong.
- **Ethereal Spotlight arriving every turn with `CANNOT BE PLAYED: you have no Encore`** was the dead weight of the first two fights — a relic that hands you an unusable card until the deck happens to give you an Encore source.

**(c) What I could not understand, or that seemed to contradict its own printed text.**

1. **`Tainted` is defined circularly on the card.** The keyword gloss says *"Tainted — Gain 2 Tainted when played."* You cannot learn what it costs you without paying it once. The real definition appears only on the combat header afterwards. In a fight where every defensive card is Tainted and I was at 17 HP, this is not a small thing.
2. **The Burst meter never moved.** `Burst Energy: … every Elemental Reaction grants 5 … You hold 0 of 70 Burst Energy.` I triggered Overloaded, Melt and Overloaded again across three fights and it read **0 of 70 every single time I saw it**, including on turns after two reactions. Either reactions do not in fact grant it, or the number shown is not the meter. I never once saw a Burst card. A 70-point meter that never moves is a system I played five fights without meeting.
3. **Lightning Rose's Vulnerable never appears.** The buff prints *"deal 5 Electro damage and apply 1 Vulnerable to a random enemy"*. The 5 damage always landed and was always visible. **A Vulnerable stack never once showed on any enemy** across three separate castings. If it is being applied and expiring before I can see it, the screen never says so.
4. **The Soloist's Solicitation cost note contradicts itself.** The card prints `*Tezcatara's Ember* — Costs 0, deals 3 additional damage, and gains Eternal` and then, immediately below, *"The cost printed on this card is 1; it is showing 0 here. This copy is not upgraded, so the cut is this turn's board and not the card: it is what this card costs now, not what it costs."* The enchantment says the 0 is permanent; the note says the 0 is this turn's board. Both cannot be right, and the note is the one that is wrong.
5. **Nutritious Soup claimed to enchant "all Strikes"**, but I then drew Soloist copies carrying *Slither* (randomised cost 0–3) instead of *Ember*, and one copy that showed Ember at one point and Slither at another. Either the relic did not do what it said, or a card can only hold one enchantment and the screen never says which copy has what.
6. **The Doll Room offered "Bing Bong" and "Daughter of the Wind" with no effect text at all** — names only. An event whose whole point is choosing between two relics is a coin flip through this bridge. (Daughter of the Wind turned out to be "play an Attack, gain 1 Block", which I would have taken anyway.)
7. **A Pyro aura printed "2 more turns" and was gone the next turn** on Bowlbug (Rock), while its two neighbours correctly showed 1. Possibly its attack consumed it; nothing on the screen said so.
8. **The Final Verdict** (card reward) prints `Deal 0 damage, already including Fanfare. Your Fanfare falls to its baseline, and that baseline falls by 30.` A card offered to me that deals zero and permanently *lowers* my own scaling floor. It may be correct for a Fanfare deck; offered to a player whose active buff literally reads "no Fanfare", it reads as a joke.
9. **Fanfare itself** I never understood. `Fanfare 2 (buff) — Only a member performing makes it … It fades 20% a turn. Cards read it and none spends it.` It ticked 2 → 5 → 4 → 3 and I never found a card in hand that read it. Meanwhile Guest Cast — the Spotlight I wanted up permanently — prints "**no Fanfare**", i.e. the kit's headline buff suppresses the kit's other meter. Whether that is a real tension or a dead branch, I could not tell from five fights.
10. **Encore satisfying "fully blocked."** Rock's Imbalanced stunned it when my 12 Block + 3 Encore covered a 15-damage hit. Good outcome, but nothing printed says a buffer counts as blocking.
11. One reward line printed `(the game answered with something this tool will not repeat)` when I claimed "Take your stolen card back." No error, and the card came back; recording it as an unexplained line.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** **Casting Call**. One energy, a power, and it does nothing on its own — it enlarges a stage I could not fill. I drew it repeatedly across three fights and did not play it once. Runner-up: **Salon Début**, whose whole apparatus (three members, front-member ordering, Evoke, Deploy, three-quarters without Encore) is more rules text than any other card in the deck and produced, in two castings, one random damage tick and one 1-in-3 miss that ended the run.
- **Happiest to draw:** **Duet+**. Cost 1, draw 2, and it doubled exactly the card I needed twice — 14 Block off Thoma, then a doubled Gorou on the turn I had no block at all. It is the card that made the Companion package feel like a deck rather than a pile. Honourable mention to **Chevreuse — Interdiction Fire+**, which was the right answer to more boards than anything else I owned.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, though a small one.** Three of the four cards I played were forced (a 0-cost 9-damage attack, a 9-damage attack against a 9-damage cap, and a 3-turn engine on a three-body board are all obvious). The actual choice was the fourth energy: Stage Presence's 6 Block against Regal Bearing's 3 Block + 1 Weak, where the Weak on the 8-damage attacker prevents 2, so 5 against 6. That is a genuine decision decided by arithmetic off the printed intents, and I got there by reading the screen. But it is a *marginal* decision — one point of prevented damage — and the turn's three interesting cards played themselves. The kit's real first decision came on **turn 2**, when Hard To Kill 9 forced me to work out that Melt and Vulnerable were both worth nothing and killing the 8-damage body was worth everything.

---

## Non-blindness declaration

**Repo files read: none.**

Every game command was one of the two allowed forms, all through the Bash tool, all prefixed `cd C:/Users/Monty/Documents/GitHub/GItS &&` and `GITS_LANE=1 python -m understudy.blindplay observe` / `... act "<command>"`. I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no other understudy subcommand.

Commands run outside the two allowed forms:

- `mkdir -p <scratchpad>` and `echo "actions=N" > <scratchpad>/count.txt` — creating and overwriting my own action counter in the session scratchpad, once after most `act` calls. `cat` of that same file once, at the start.
- `sed -n '<ranges>p'` and `head -30` piped off my own `observe` output, to re-read one block of a screen I had just been shown. Twice this cut off part of the screen I then had to re-read (the relic list, and the three Shiv cards).
- `grep -i "shiv"` piped off one `observe`, to find the three Shiv cards a `head -30` had truncated.
- `for i in 1 2 3; do ... done` around three identical `act 'play "Shiv+ (1)"'` calls, and `| tail -2` on several `act` calls to trim the JSON echo. In every such case the following `observe` was read in full.

Tools used: **Bash** (all of the above), and **Write** once, for this record. No Read, no Grep, no Glob against the repo; no agent, no web, no other tool.

Two caveats on the round, both declared above rather than smoothed over: I never saw a run seed or a gold total on any screen, so both are reported as unknown; and the end-of-run deck list is reconstructed from cards I watched pass through my hand, because the bridge exposes no deck view.
