# Blind play session `kleespark-w4`

**R217 G — subjective feedback from an independent model playing the real game. Useful for iteration; not human validation, not balance evidence, not approval. It never enters an Understudy report, a win-rate table or a measurement register.**

## Identity

- **model_requested**: gpt-5.6-sol
- **model_observed**: gpt-5.6-sol
- **codex_version**: codex-cli 0.150.1
- **build_version**: 0.2.1676+proto.dirty
- **build_version_source**: the deployed `mods\klee\manifest.json` `version`
- **game_version**: v0.111.0
- **game_version_source**: the game's own `release_info.json` `version`
- **run_seed**: KGU5LKM77PB5
- **arms_granted**: KLEEMOD-PROTO_POP_SPARK, KLEEMOD-PROTO_POP_SPARK, KLEEMOD-SKIP_AND_HOP, KLEEMOD-WARM_GLOW, KLEEMOD-SNAP, KLEEMOD-HOT_HANDS, KLEEMOD-ALL_MY_TREASURES, KLEEMOD-DA_DA_DA, KLEEMOD-PROTO_KABOOM_SINK, KLEEMOD-PROTO_POWDER_CHARGE_SPARK, KLEEMOD-PROTO_HOLD_THE_LINE_SPARK, KLEEMOD-PROTO_SMOKE_AND_SPARKS_SPARK, KLEEMOD-PROTO_SPARK_PRICED_DRAW, KLEEMOD-PROTO_TRUE_SPARK_KNIGHT
- **arms_granted_source**: the embark sidecar `embark-20260830-131412.json`, matched by run seed
- **prompt_sha256**: 5dd16d9e02d6c11ae717749d2e1fd7926510f16d882d779a30557973112f7e0a
- **actions**: 80
- **termination**: max_actions

- **guardrail**: you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval

- **wire snapshots**: 48 in `wire.json` beside this file — one row per play and per end turn, machine-written off the API and never shown to the tester (`EB-216`, R101b)

## Fight 1, in the tester's own words

1. I played both Powder Pops first, spent the resulting Sparks on Powder Smoke, then attacked with Kaboom! and Snap!. That stacked the Bomb damage, reduced the first incoming attack, and made both attacks benefit from Vulnerable. On round two, Jumpy Dumpty was enough to finish the 11 remaining HP.

2. I considered attacking after the first Powder Pop instead of setting the second Bomb. That would have detonated sooner, but given up a free Spark, 5 Burst Energy, another 5 Bomb damage, and immediate access to Powder Smoke.

3. A defensive or much larger enemy intent could have made blocking more important, though round one offered no block cards. A weaker second-round draw might have required Powder Pop followed by Set It Off; with Jumpy Dumpty and Vulnerable, the kill was straightforward.

4. The zero-cost Powder Pops were automatic, and Powder Smoke became automatic once I reached 2 Sparks. Kaboom! and Snap! were also automatic while energy remained. Set It Off and both Duck and Covers were dead in the final hand because Jumpy Dumpty could kill immediately.

5. The plan did not change much: build Bombs and Sparks, apply Vulnerable, then attack. After round one left Seapunk at 11 HP, the plan simplified from managing damage and defense to taking the direct lethal attack.

6. The Bomb interaction was initially a little ambiguous: I had to infer that multiple Bombs would stack and detonate together. The intent dropping from 11 to 8 while Bombed, then returning to 11 after detonation, made the mitigation readable. The duplicated-card enchantment warning added uncertainty, but there was no visible basis for choosing between the copies.

## Fight 2, in the tester's own words

1. I played Skip and Hop and both Powder Pops for free, then spent all three energy on All of My Treasures!. The plan was to stack 46 Bomb damage, absorb most of the incoming hit, and let the Bombs end the fight next turn; when they left 7 HP, I finished with the free Da-da-da!.

2. I considered playing Prune for 5 more Block, but that would have prevented All of My Treasures! because both competed for the same three energy. Giving up 36 Bomb damage was not worth preventing a few points of damage.

3. A much larger attack might have pushed me toward Prune and a slower line. A draw without All of My Treasures! would have relied on smaller Bombs and later attacks, while a stronger round-two attack could also have finished what the Bombs left behind.

4. Skip and Hop and both Powder Pops were automatic because they were free and supported the Bomb/Spark engine. All of My Treasures! was automatic once drawn against a 37-HP enemy. Prune became dead because its energy cost conflicted with the decisive play; Hot Hands, Set It Off, and Kaboom! were unnecessary once Da-da-da! showed lethal.

5. The initial plan was a one-turn Bomb setup followed by automatic lethal. It changed at the start of round two when the displayed 46 Bomb damage only reduced the enemy from 37 to 7, so I switched to finding the cheapest immediate finisher.

6. The biggest confusion was that Bomb 46 did only 30 visible damage between turns, despite saying it would deal 46 total. Spark also rose from 5 to 13 without an explanation on the screen. I was therefore guessing about an unprinted enemy effect or per-Bomb interaction, though the final lethal calculation was clear.

## Fight 3, in the tester's own words

1. I used the Regen Potion immediately, then put six Bombs from All of My Treasures! on the debuffing Corpse Slug and detonated them with Quick Fuse. Killing it stunned the attacking slug through Ravenous. I applied Vulnerable during that safe turn, then used Powder Pop, Set It Off, and a Melt-triggering Kaeya — Frostgnaw to finish the survivor.

2. I seriously considered Bomb Voyage or Jumpy Dumpty for a more distributed line, but either would have given up the guaranteed first-turn kill and stun created by All of My Treasures! plus Quick Fuse. I also considered saving the potion, but using it early maximized the turns of healing.

3. If neither slug had been attacking, target priority would have mattered less. A stronger attack or no Quick Fuse would have made the first turn riskier, while a draw without All of My Treasures! would have required spreading smaller Bombs and accepting a longer fight.

4. All of My Treasures! into Quick Fuse was automatic because it killed one enemy and disabled the other. Powder Smoke was automatic once the survivor was safely Stunned. Bomb Voyage and Jumpy Dumpty became dead after spending all energy, while Spark Knight's Oath and Kaboom! were unnecessary once Melt showed lethal.

5. The main plan—kill one slug to stun the other—worked as intended. On round two I initially expected the Bomb plus two ordinary attacks to finish, but Set It Off unexpectedly left a Pyro aura and exposed a Melt preview, so I switched to Frostgnaw for immediate lethal.

6. Set It Off was confusing: it spent only 1 net Spark according to the displayed totals, dealt 13 damage from a single 5-damage Bomb despite saying detonations deal 4 more, and appeared to leave Pyro Aura even though the card prints no Pyro application. The new reaction preview made the final choice clear, but the preceding state change was not explained.

## Fight 4, in the tester's own words

1. I used Fysh Oil immediately, then spent the safe first turn on Snap!, Kaeya — Frostgnaw, and Kaboom!, using Pyro into Cryo for Melt. On the attack turn I fully blocked with both Duck and Covers and used Kaboom! to strip most of the Construct’s Block. Finally, I stacked both Powder Pops and All of My Treasures!, used Dig In as insurance, and detonated everything with Flame on the Wick for lethal.

2. I considered using Warm Glow on the first turn, but the enemy was only blocking, so it would have traded away damage for temporary Block that was about to expire unused. On round two I considered Prune, but its Swirl offered little against one enemy and would have left some incoming damage uncovered.

3. An opening attack intent would have made Warm Glow worthwhile and reduced the all-out damage line. A round-three draw without Flame on the Wick or another detonator would have required waiting for the Bombs, making Dig In and Bomb mitigation important rather than merely insurance.

4. Fysh Oil was automatic because its bonuses improved the entire fight. The two Duck and Covers were automatic against 10 incoming damage, and the free Powder Pops plus Flame on the Wick became an automatic Bomb setup and detonation package. Warm Glow was dead on the non-attacking turn, Prune was dead against a lone Pyro-affected enemy, and Set It Off was dead whenever there were no Bombs or insufficient Sparks.

5. The plan began as efficient attack sequencing around Melt, shifted to full defense when the Construct attacked behind Block, and then became a direct Bomb-combo kill once both Powder Pops, All of My Treasures!, and Flame on the Wick appeared together.

6. Artifact was confusing because the Construct kept Artifact 1 even after repeated aura applications; it was unclear what counted as a debuff for Artifact. Otherwise the reaction preview, dynamically adjusted Strength and Dexterity values, Bomb mitigation, and final detonation were readable.

## Fight 5, in the tester's own words

1. I opened with free Block from Skip and Hop, then used Jumpy Dumpty and Kaboom! to kill the debuffing slug; both survivors ate it and became Stunned. Next I used Bomb Voyage plus Flame on the Wick to reduce one survivor to 5 HP and blocked what I could. On round three, Da-da-da! killed that weak slug, stunning the last one, and All of My Treasures! supplied a safe lethal Bomb total.

2. I considered Hot Hands on round one, but it would have replaced Kaboom! and prevented the immediate kill-and-stun sequence. On round two I considered Prune instead of Duck and Cover; it would have spread Pyro through Swirl but, because it triggered a reaction, apparently given up the 5 Block while offering no printed direct damage.

3. If the survivors had actually remained Stunned on round two, I could have attacked freely and avoided 21 damage. A draw with a small targeted attack on round two would have killed the 5-HP slug and stunned its partner; a stronger defensive draw would also have made that turn much safer.

4. Skip and Hop was automatic for free value, and Jumpy Dumpty plus Kaboom! became automatic once both random hits landed on the intended first target. Bomb Voyage into Flame on the Wick was an automatic combo, as was All of My Treasures! against the final Stunned slug. Hot Hands, Spark Knight's Oath, Prune, and the round-three Block cards were dead in their respective hands.

5. The plan began by focusing one slug to exploit Ravenous. It changed on round two when the prior Stunned display did not prevent both survivors from showing attack intents; I accepted a large hit to nearly kill one. Da-da-da! then hit well enough to restore the original kill-and-stun plan, after which the fight was settled.

6. The Stunned timing was the main confusion. At the end of round one both survivors said they could not act on their next turn, but at the start of round two they immediately intended attacks. Also, both survivors appeared to eat the same corpse and each gained Strength, which may be intended but made Ravenous read less literally than expected.

## The run, in the tester's own words

1. The character builds Sparks and Bombs with cheap setup cards, then converts them into Vulnerable, Block, card draw, or enhanced detonations. The strongest turns stack several Bombs and trigger them immediately with a free attack or Quick Fuse, while elemental auras create occasional reaction multipliers and Burst Energy works toward another payoff.

2. The repeated tension was spending energy and Sparks on defense versus committing them to a Bomb combo. Bombs softened the first incoming attack, but waiting for automatic detonation was risky; immediate detonation dealt damage safely but removed that mitigation. Multi-enemy fights added a second tension between focusing one enemy for a Ravenous stun and spreading random damage.

3. Powder Pop, Powder Smoke, All of My Treasures!, Quick Fuse, and Flame on the Wick defined the run. Powder Pop was the reliable free starter, Powder Smoke made attack turns explosive, All of My Treasures! supplied overwhelming Bomb totals, and Quick Fuse or Flame on the Wick turned those totals into immediate damage. Jumpy Dumpty and Da-da-da! also mattered in the Corpse Slug fights because their random multi-hits sometimes created decisive kills.

4. Play became repetitive once the standard line was established: play every free Spark/Bomb card, spend Sparks on Vulnerable or Block, place the largest Bomb package available, then use a free detonator. Reward collection also repeated mechanically, and several fights were largely decided whenever All of My Treasures! appeared with a detonator.

5. Next time I would avoid narrow powers such as Spark Knight's Oath or True Spark Knight unless the deck already had enough compatible attacks; the Oath repeatedly sat dead while costing too much tempo. I would also be cautious about more random-target attacks and extra expensive Bomb cards, since the deck already had ample damage but sometimes lacked reliable defense, draw, or a specific small finisher. The run ended unexpectedly immediately after playing Powder Pop at 31 HP, so I cannot tell from the final screen whether that choice caused the loss or whether an unprinted effect resolved.

## Turn by turn, in the tester's own words

One line per answered turn: the command the tester gave and the sentence it gave for it, verbatim, off `turn-*/reply.json`. The same R217 G label rides on it as on the fight records — it is one model's account, not a measurement.

| turn | command | the tester's sentence |
|---|---|---|
| `turn-001` | `go "Monster (path 1)"` | All four visible choices are equivalent monster nodes, so I’m taking the first path without further distinguishing information. |
| `turn-002` | `play "Powder Pop (1)" on "Seapunk"` | The free Bomb gains Spark and Burst Energy, and the next unblocked attack can detonate it while reducing Seapunk’s first attack. |
| `turn-003` | `play "Powder Pop" on "Seapunk"` | This free play reaches 2 Sparks, adds another Bomb, and enables Powder Smoke before spending energy on attacks. |
| `turn-004` | `play "Powder Smoke" on "Seapunk"` | Applying Vulnerable before detonating the Bombs and making both attacks should maximize this turn’s damage. |
| `turn-005` | `play "Kaboom!" on "Seapunk"` | This is the stronger attack, benefits from Vulnerable, and detonates the stacked Bombs immediately. |
| `turn-006` | `play "Snap!" on "Seapunk"` | Snap deals boosted damage under Vulnerable and gains another Spark; there is no reason to leave usable damage in hand. |
| `turn-007` | `end turn` | The hand is empty, so there is no further action available despite the remaining energy. |
| `turn-008` | `play "Jumpy Dumpty" on "Seapunk"` | Its first Vulnerable-boosted hit should already finish the 11-HP enemy, making defense unnecessary. |
| `turn-009` | `` |  |
| `turn-010` | `choose "Gold"` | Gold is immediately available and can be collected before deciding whether to add a card. |
| `turn-011` | `choose "Card"` | I want to inspect the card choices before deciding whether adding one improves the deck. |
| `turn-012` | `choose "Bomb Voyage"` | Three Bombs strongly reinforce the deck’s detonation and Vulnerable plan while also providing Burst Energy and attack mitigation. |
| `turn-013` | `proceed` | All available rewards have been claimed, so it is time to continue. |
| `turn-014` | `go "Monster (path 1)"` | This is the only available route. |
| `turn-015` | `play "Skip and Hop"` | This free play adds Block and a Spark without interfering with the full-energy All of My Treasures! setup. |
| `turn-016` | `play "Powder Pop (1)" on "Sludge Spinner"` | The free Bomb adds damage, Spark, and Burst Energy while preserving all three energy for the large Bomb play. |
| `turn-017` | `play "Powder Pop" on "Sludge Spinner"` | The second free Bomb raises the pending total to 10 damage and preserves all energy for All of My Treasures!. |
| `turn-018` | `play "All of My Treasures!" on "Sludge Spinner"` | This adds 36 Bomb damage, making the total more than enough to kill at the start of the next turn while retaining Bomb mitigation now. |
| `turn-019` | `end turn` | The pending 46 Bomb damage will kill Sludge Spinner at the start of the next turn, and no remaining card is playable. |
| `turn-020` | `play "Da-da-da!" on "Sludge Spinner"` | With only one enemy, all three hits land on it for 9 total damage, enough to finish its 7 HP at no energy cost. |
| `turn-021` | `` |  |
| `turn-022` | `choose "Gold"` | Gold can be collected immediately without preventing the other visible rewards. |
| `turn-023` | `choose "Potion"` | The Regen Potion should help recover health lost across these early fights, and claiming it does not appear to exclude the card reward. |
| `turn-024` | `choose "Card"` | I want to inspect the available cards before deciding whether any are worth adding. |
| `turn-025` | `choose "Quick Fuse"` | A free, reliable detonation strongly complements the deck’s growing Bomb package and avoids waiting a turn or needing an unblocked attack. |
| `turn-026` | `proceed` | All rewards have been collected, so there is nothing left to do on this screen. |
| `turn-027` | `go "Monster (path 1)"` | This is the only available map node. |
| `turn-028` | `use potion "Regen Potion"` | At 15 HP below maximum, using Regen now gives it time to restore health across the fight before setting up a Bomb kill. |
| `turn-029` | `play "All of My Treasures!" on "Corpse Slug (1)"` | Six Bombs can kill the debuffing slug via Quick Fuse, which should force the attacking slug to eat it and become Stunned. |
| `turn-030` | `play "Quick Fuse" on "Corpse Slug (1)"` | Detonating 36 damage now kills the first slug and should stun the second before it can carry out its attack. |
| `turn-031` | `play "Powder Smoke" on "Corpse Slug"` | The slug is safely Stunned, and spending 2 of the abundant Sparks now sets up three turns of boosted attack damage. |
| `turn-032` | `end turn` | No cards are playable at zero energy, and the remaining slug is Stunned, so ending the turn safely advances the setup and triggers Regen. |
| `turn-033` | `play "Powder Pop" on "Corpse Slug"` | This free Bomb adds damage and Spark before the Vulnerable-boosted attacks, which can detonate it immediately. |
| `turn-034` | `play "Set It Off" on "Corpse Slug"` | Spending 2 of 7 Sparks upgrades the Bomb detonation from 5 to 9 damage, leaving the two Vulnerable-boosted attacks well positioned to finish the slug. |
| `turn-035` | `play "Kaeya — Frostgnaw" on "Corpse Slug"` | Frostgnaw triggers Melt against the Pyro aura, and that multiplied hit also benefits from Vulnerable, making it sufficient for the remaining 13 HP. |
| `turn-036` | `` |  |
| `turn-037` | `choose "Gold"` | Gold can be claimed without giving up the potion or card reward. |
| `turn-038` | `choose "Potion"` | Claiming Fysh Oil preserves a potentially useful consumable without preventing inspection of the card reward. |
| `turn-039` | `choose "Card"` | I want to inspect the offered cards before deciding whether to add one or skip. |
| `turn-040` | `choose "Flame on the Wick"` | A free targeted attack can detonate Bombs immediately, apply Pyro, and add damage without competing for energy. |
| `turn-041` | `proceed` | All available rewards have been collected. |
| `turn-042` | `go "Monster (path 1)"` | This is the only available route. |
| `turn-043` | `use potion "Fysh Oil"` | Using the potion early lets Strength improve every attack and Dexterity improve every block card throughout the fight. |
| `turn-044` | `play "Snap!" on "Punch Construct"` | The enemy is not attacking, so all energy can go to damage; Snap also gains a Spark and can consume the Construct’s Artifact with its Pyro application. |
| `turn-045` | `play "Kaeya — Frostgnaw" on "Punch Construct"` | Frostgnaw can consume the current Pyro aura for a 1.75× Melt hit before Kaboom! uses the final energy. |
| `turn-046` | `play "Kaboom!" on "Punch Construct"` | The Construct is only blocking, so dealing 8 more damage now is more useful than gaining temporary Block with Warm Glow. |
| `turn-047` | `end turn` | No cards are playable at zero energy, and the Construct is not attacking this turn. |
| `turn-048` | `play "Duck and Cover (1)"` | The Construct is attacking for 10 total, so two Duck and Covers can fully block it while leaving one energy for Kaboom!. |
| `turn-049` | `play "Duck and Cover"` | Another 6 Block fully covers the incoming 10 damage, with one energy still available for an attack. |
| `turn-050` | `play "Kaboom!" on "Punch Construct"` | With the incoming damage fully covered, Kaboom! can remove 8 of the Construct’s 10 Block and refresh Pyro. |
| `turn-051` | `end turn` | No cards are playable at zero energy, and the 12 Block fully covers the incoming 10 damage. |
| `turn-052` | `play "Powder Pop (1)" on "Punch Construct"` | This free Bomb adds damage, Spark, and Burst while preserving all energy for All of My Treasures! and setting up Flame on the Wick as a detonator. |
| `turn-053` | `play "Powder Pop" on "Punch Construct"` | The second free Bomb raises the pending damage and Spark total while still preserving all energy for the six-Bomb setup. |
| `turn-054` | `play "Dig In"` | This converts spare Sparks into Block at zero energy, protecting against the attack if the Bomb detonation behaves unexpectedly. |
| `turn-055` | `play "All of My Treasures!" on "Punch Construct"` | Adding 36 more Bomb damage makes the pending total overwhelming, and Flame on the Wick can detonate it afterward for immediate lethal. |
| `turn-056` | `play "Flame on the Wick" on "Punch Construct"` | The free attack immediately detonates 46 Bomb damage, easily exceeding the Construct’s remaining 28 HP. |
| `turn-057` | `` |  |
| `turn-058` | `choose "Gold"` | Gold can be collected without preventing the card reward from being inspected afterward. |
| `turn-059` | `choose "Card"` | I want to inspect the card options before deciding whether any improve the deck. |
| `turn-060` | `choose "Alchemical Curiosity"` | Block plus drawing two cards improves defense and helps assemble the deck’s Bomb-and-detonator combinations more consistently. |
| `turn-061` | `proceed` | All available rewards have been collected. |
| `turn-062` | `go "Shop (path 2)"` | After collecting gold from several fights, the shop is the best opportunity to convert it into a targeted deck improvement. |
| `turn-063` | `proceed` | Every shelf item is unnamed and has no rules text, so there is no informed way to distinguish purchases; I will preserve the gold. |
| `turn-064` | `go "Monster (path 1)"` | This is the only available map node. |
| `turn-065` | `play "Skip and Hop"` | This free card reduces incoming damage and gains a Spark without consuming energy needed for Jumpy Dumpty and Kaboom!. |
| `turn-066` | `play "Jumpy Dumpty" on "Corpse Slug (1)"` | Targeting the debuffing slug places the Bomb there while the two random hits soften the group; Quick Fuse and Kaboom! can then help focus a kill. |
| `turn-067` | `play "Kaboom!" on "Corpse Slug (1)"` | Kaboom! deals 7 and triggers the 6-damage Bomb, guaranteeing the kill on the 9-HP debuffing slug with the remaining energy. |
| `turn-068` | `end turn` | Both surviving slugs are Stunned, and there are no Bombs for Quick Fuse or energy for Hot Hands. |
| `turn-069` | `play "Bomb Voyage" on "Corpse Slug (2)"` | Stacking 15 Bomb damage on the 12-damage attacker lets Flame on the Wick heavily soften it while also reducing that enemy’s first attack. |
| `turn-070` | `play "Flame on the Wick" on "Corpse Slug (2)"` | The free attack detonates all 15 Bomb damage immediately, leaving the stronger single attacker at only 5 HP. |
| `turn-071` | `play "Duck and Cover"` | Prune would trigger Swirl and therefore provide no Block, so Duck and Cover is the reliable way to reduce the large incoming total. |
| `turn-072` | `end turn` | No cards remain playable, so I must accept the incoming damage after the available Block. |
| `turn-073` | `play "Da-da-da!" on "Corpse Slug (2)"` | The free three-hit attack has a strong chance to finish the 5-HP slug, which would Stun the surviving attacker before I commit energy. |
| `turn-074` | `play "All of My Treasures!" on "Corpse Slug"` | The survivor is Stunned, and 36 Bomb damage exceeds its remaining 23 HP, setting up a safe start-of-turn kill. |
| `turn-075` | `end turn` | The slug is Stunned and the pending 36 Bomb damage exceeds its 23 HP, so ending the turn should finish the fight safely. |
| `turn-076` | `` |  |
| `turn-077` | `choose "Gold"` | Gold can be claimed now without preventing inspection of the card reward. |
| `turn-078` | `choose "Card"` | I want to inspect the offered cards before deciding whether to add one. |
| `turn-079` | `choose "Kaboom Beetle Swarm"` | Its three enhanced hits strongly reward the deck’s frequent Bomb setups and provide another way to trigger Bomb detonations. |
| `turn-080` | `proceed` | All available rewards have been collected. |
| `turn-081` | `go "Elite (path 1)"` | This is the only available route. |
| `turn-082` | `play "Duck and Cover"` | Blocking 5 while preserving two energy for Kaboom Beetle Swarm balances survival against the elite’s 16-damage attack with necessary damage progress. |
| `turn-083` | `play "Kaboom Beetle Swarm" on "Terror Eel"` | With only one enemy, all three hits land on the Eel for 15 total damage while applying Pyro for later reactions. |
| `turn-084` | `end turn` | No remaining card is playable, so I must take the partially blocked attack and move to the next draw. |
| `turn-085` | `play "Powder Pop" on "Terror Eel"` | The free Bomb generates the Spark needed for Ka-pow!, reduces the Eel’s first Bombed attack, and can be detonated immediately for extra damage. |
| `turn-086` | `` |  |

## Leak audit

Every observation the tester was actually shown — `turn-*/prompt.md`, the exact bytes handed to `codex exec` — scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary rules and this run's seed.

- **observations scanned**: 86
- **total hits**: 1

| rule | hits |
|---|---|
| `pilot-vocabulary-score` | 1 |

Offenders (first 40):

- `turn-001` — `pilot-vocabulary-score` matched `score` in: guide, no card list, no score, no recommendation, and no way to ask for one.
