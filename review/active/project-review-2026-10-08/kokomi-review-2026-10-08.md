# Kokomi kit review (Prototype), 2026-10-08 (revised after fact-check)

Written from the fact packet (`fanout/packet-kokomi.md`), the brief (`review/active/kokomi-brief-2026-09-01.md`), the seat records of 2026-10-01 to 10-05, the sheet (`docs/prototype-surface.yaml`, 86 `kokomi` rows) and the fight telemetry (`tools/telemetry_report.py`; my scripts are in `fanout/kkrev/`, the confirmation pass is `kkrev/verify6.py`). Kokomi's sheet and code are identical on local main and origin/main. Nothing here was played; the game was not touched.

**Summary.** Kokomi is no longer undercooked; she is unfinished at the boss. Part of the "half a base character's damage per turn" reading is an instrument fault: the Bake-Kurage's hits were not credited to her until the 2026-10-02 credit rule, first present in a Kokomi round on 10-05, so every Kokomi telemetry figure before 10-05 omits her Plans. In the one clean window (two runs, 37 fights) her hallway damage per turn is in family with the base five (act 1: 18.0 against 18.7; act 2: 26.6 against 33.0). But the window is small, and the save files, which never had the fault, still show the gap at bosses: on the same seed she needs about twice the Ironclad control's turns (The Insatiable 7 against 4, from a lower door; Knowledge Demon lost in 10 against won in 6), and her act-1 hallways cost more HP than the control's on both 10-02 seeds. The two bosses that punish slow decks (the Queen's one-card turns, The Insatiable's clock) killed two of her last four runs. The kit's best turns are the ones the brief promised (Strength into a morning of three Plans; Opening Gambit into a damage Plan), seats find them every run, and [USER]'s last verdict on a build he played was "I like it!" (2026-09-29, the 48-card pool). He has not played the 78-card build; STATE says that run is next and the damage paper follows it. Below: balance, archetypes, fun, co-op, text, hygiene, six picks.

## 1. Power level and balance

### 1.1 Runs on the 78-card pool (all Sonnet, A0, one seat per act with handoff)

| Date, record | Build | Kokomi result | Other seats that round |
|---|---|---|---|
| 10-01 `kokomi-pool-round-2026-10-01.md` | 78 cards, Casket Exhausts; game-rolled seeds | both died at the act-1 boss | the same build's Varka and Furina seats cleared act 1 on all three of their lanes (line 15) |
| 10-01 `three-kit-round-2026-10-01.md` | status batch (0.2.4162); game-rolled seeds | both died at the act-1 boss (4 of 4 that day) | Varka 1 and 2, Furina 1 and 2 all cleared act 1; no base character ran |
| 10-01 `klee-kokomi-round-2026-10-01.md` | open-Plan rule | K1 reached the Queen (211/400 left); K2 died at the act-1 boss | Klee 1 and 2 died in act 2 |
| 10-02 `casket-and-klee-defence-round-2026-10-02.md` | Casket repeats at 1 Energy, click-to-flip (0.2.4204); fixed seeds | lane 3 **won**, with 5 HP left; lane 4 died to Knowledge Demon (boss at 92/379) | Ironclad control, same seeds: won lane 3's run at 60 HP; died to the Queen on lane 4's seed. It played the reduced pools (22 epochs missing until #924; `base-five-baseline-2026-10-05.md` line 3) |
| 10-05 `kokomi-review-round-2026-10-05.md` | Rare pass (0.2.4463); baseline seeds | lane 1 lost to the Queen (238/400 left); lane 2 lost to The Insatiable (118/321), 1 Block short at 9 HP | Silent on lane 1's seed: lost to the Queen at 38/400; Defect on lane 2's seed: lost to Test Subject in act 3 |

Ten runs over five builds (the two lanes of a round share a build), nine deaths, one win. The base-five Sonnet baseline on the same harness is 0 of 5 at A0, four dying at the final boss (`base-five-baseline-2026-10-05.md`). Her one win does not put her above the base five: the Ironclad control won the same run on her 10-02 seed from a 90-HP door at the act-2 boss against her 39, on a smaller pool. Evidence is thin everywhere: one seed-pair per round, a different build each round.

### 1.2 Telemetry: the instrument fault, then the corrected read

`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:549-563` dates the damage-credit rule to 2026-10-02 (commit f8081b16, 23:20): before it "a hit counted only when the engine named the seat's own creature as the dealer", so a pet's hit (every carried-out Plan) was dropped. The 115 Kokomi fights logged on 10-01 and 10-02 carry 0 damage under `(Bake-Kurage)`; the 37 fights of 10-05 carry 1,083 of 4,642, 23.3% (`kkrev/verify3.py`). So:

- The 10-05 record's "about half a base character's" rests on figures that omit her Plans. So does the Klee measurement paper's Kokomi line that the record cites (`review/active/klee-balance-measurement-2026-10-05.md` sec.3); that paper is only on branch `klee-measure` (commits 5be3b382, 0fefc6be; not an ancestor of origin/main), so the record on main cites a file main lacks. The 10-02 record's boss numbers came from the save files and have no fault.
- Any Kokomi report must use `--since 2026-10-05`. A date does not isolate a build: run 5JNWQ9G4YNV7 (the 10-02 round's winning seed) starts at 10-01 22:36 in telemetry.
- Losses were not filed for any character before commit fc05aa88 (2026-10-05 19:23; `--help` says "written since 2026-10-05"). Her last logged fight is 10-05 14:25, so all 152 of her rows since 10-01 are wins and every Kokomi boss row below is a survivor's. The base five's 10-05 baseline has the same hole (five deaths, 6 base `died` rows in the window, all 10-03 or later). Nothing to fix; her boss rows just read high.

Medians over fights, solo, since 10-05 (`kkrev/verify4.py`; Kokomi = two runs; base five = 270 fights across 10-05 to 10-08, Klee-suite control lanes included):

| act, kind | Kokomi n | dmg/turn | HP lost % | turns | cards/turn | base five n | dmg/turn | HP lost % | turns | cards/turn |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 hallway | 13 | 18.0 | 8.8 | 4 | 3.2 | 117 | 18.7 | 7.1 | 3 | 2.8 |
| 1 elite | 2 | 23.8 | 6.9 | 6 | 3.1 | 18 | 27.3 | 21.7 | 4 | 3.0 |
| 1 boss | 2 | 29.7 | 76.9 | 10 | 3.2 | 15 | 26.4 | 42.5 | 7 | 3.1 |
| 2 hallway | 10 | 26.6 | 8.4 | 4 | 3.5 | 44 | 33.0 | 11.1 | 3 | 3.5 |
| 2 boss | 1 | 80.2 | 21.6 | 4 | 3.2 | 9 | 53.5 | 57.5 | 7 | 3.4 |
| 3 hallway | 7 | 38.2 | 0.0 | 5 | 4.0 | 44 | 48.0 | 12.1 | 3 | 4.0 |

Read: hallway damage is in family (ratios 0.96, 0.81, 0.80). HP is mixed: act-1 hallways cost her more than the base five (8.8% against 7.1%), acts 2 and 3 less. Her fights run one turn longer. Two caveats cut against her: the hallway cells are 13, 10 and 7 fights from two runs, and the base comparator may read low (`telemetry_report.py` lines 57-59: base Poison and orb damage is credited only when the engine names the seat's creature), so 0.96 and 0.81 are generous.

### 1.3 Where the gap is: boss length

Save-file numbers, same seed, Kokomi against the Ironclad control (`casket-and-klee-defence-round-2026-10-02.md`, results table and "Kokomi against the control"):

| Fight | Kokomi | Ironclad control |
|---|---|---|
| The Insatiable (321), seed 5JNWQ9G4YNV7 | door 39, 7 turns, about 46 a turn, won | door 90, 4 turns, about 80 a turn, won |
| Knowledge Demon (379), seed LURXU1TGSM38 | door 92, 10 turns, about 29 a turn, lost | door 104, 6 turns, about 63 a turn, won |
| HP lost per normal fight, the two seeds | 10.2 and 18.1 | 4.6 and 14.3 |

The one same-HP boss comparison is the four-kit review's (`four-kit-review-2026-10-01.md` lines 308-309): Lagavulin Matriarch from a 71-HP door against the Ironclad's 74, where she lost 5.5 HP a turn to his 6.2 and dealt about half his damage. Its sentence stands: "She does not lose these fights on Block. She loses them on length" (sec.2.8). The 10-05 lanes died to the Queen (Chains of Binding, one card a turn, which starves a kit whose damage is Plans written from several cards) and to The Insatiable's Sandpit clock. Her scaling is Casket count into Strength into Plans, and the one win and the 135-damage act-2 turn both came from exactly that (10-02: Nereid's+ at Strength 15 to 21; 10-05: Strength 14, three Plans for 135). Nothing else in her pool scales with fight length; the base five bring Demon Form, Noxious Fumes, Creative AI, Doom.

### 1.4 Card by card against the base game (same rarity, cost, type; unupgraded; base numbers from `game_ref/*.json`, packet sec.5)

Commons, 1-cost Attacks: base median 9 (range 3 to 13, 29 cards).

| Card | Now | Plan | Read |
|---|---|---|---|
| Massed Volley | 3x3 targeted | none | Sword Boomerang's 9 without the random target: at rate |
| Deep Current | 8 to ALL | none | Sow 8, Flick Flack 7, Breakthrough 9: at rate; the 10-05 seats' happiest draw |
| Undertow | 7, or more if debuffed | none | Setup Strike 7, Sucker Punch 8 plus Weak: at rate with Slack Water in deck |
| Press the Advantage | 7, or 11 if a Plan waits | none | Headbutt 9, Momentum Strike 11: at rate only while planning |
| Feint | 6 plus 3 per Plan carried out this turn | 1 Vulnerable | below the 9 median; needs one carry-out; 43 plays, 395 credited (9.2 a play) |
| Driftglass | 6 plus 1 per Casket point | none | below rate until the Casket holds 3 |
| Coral Crash | Body Slam | none | Body Slam, same slot |

Commons, Skills: base 1-cost Block median 6 (Leap 9, Shrug It Off 8 plus draw, Backflip 5 plus draw 2).

| Card | Now | Plan | Read |
|---|---|---|---|
| Coral Bulwark | 8 Block | none | Leap minus 1: at rate |
| Tidal Screen | 7 Block | draw 2 | each half alone is under Backflip's both-at-once; the either/or is the price |
| Shell of Sanctuary | draw 1 | Dusk 9 Block | now-line is Prepared (a 0-cost card) at cost 1; the Plan is Leap. The now-line exists to be legal, not chosen |
| Kelp Wall | draw 1 | 7 Block plus 3 per status in hand | same shape; 4 plays in 152 fights |
| Breakwater | none | Dusk 5 Block plus 3 per Plan waiting | a Defend that grows with the queue |
| Shell Guard | 5 plus 1 per Casket point | none | a Defend until the Casket is 2. Sheet: Common; brief line 239 records the demotion, its 09-28 note (line 393) still says "Uncommon Skill" |
| the five 0-cost feeders | none | Nip 5; Bubble Ward 4 Block; Jellyfish Drift 2 to ALL; Current Read draw 1; Brine Sting 1 Weak | Nip, Bubble Ward and Current Read are a base 0-cost Common (Slice 6, Deflect 4, Prepared) a turn late. Brine Sting's model Neutralize is a Basic (the Silent's starter); Jellyfish Drift's 2 to ALL is a third of Astral Pulse's 6. Their wage is one Casket point and a Treatise, Canopy or Swarm trigger. They are 9.5% of card plays since 10-02 (125 of 1,320; the eight Plan-only cards together 10.3%), by [USER]'s design ("lower-impact feed") |

Uncommons: 1-cost Attacks sit at the base median 8 (Flank 8 plus a Plan, Signal Arrow 7 plus a Plan, Pearl Current 2x4, Pincer 4x2). Flotsam Surge 13 to ALL plus 2 Dazed sits above Echoing Slash (10 to ALL, no price). 2-cost Attacks: base median 13; Surging Shoal 14 now or 22 later, Riptide 11 to ALL with an Energy Plan, Undertide Lance 6 to ALL or 12 (24 alone). The formula Attacks (Tideturn 4 per Plan waiting, Weight of the Plan 5 plus 3 per Energy paid, Drowning Pressure 4 per debuff) each need two of their thing to reach rate. Powers: Kurage Canopy 2 Block per carry-out is Afterimage priced to the queue; Treatise draws when you play a Plan card *normally*, the one card that prices the halves rule from the other side.

Rares: Masterstroke (3, Plan 30, Strength three times) is above the 3-cost Rare median 20 on paper, but does nothing this turn; a seat holding two wrote NEVER AGAIN (10-05). Riptide Ruin 18 to ALL plus 3 Dazed for 2 is under Hyperbeam (24) and Seven Stars (49); its 613 credited damage (493 upgraded, 120 base) includes 74 to both bodies at 13 Strength (10-05 record), so Strength is where its big turns come from, though telemetry cannot split the card's number from the Strength on it. Ceremonial Garment (Power, 1, Rare: 2 per debuff on the target) is an Inflame that needs a debuff, at Rare. Sango Isshin and Shoal of Spears are at rate from two Plans. Eleven of her 21 Rares are Powers and seven cost 1 (cost sweep #780); none scales with turns the way the base five's Rare Powers do, which is where sec.1.3 lands.

Verdict on numbers: the sheet is mostly priced where [USER] asked ("5 to 7 damage per 1 energy ... on AoE commons", Plan at the going rate); the exceptions are two feeders under their base model (Jellyfish Drift, Brine Sting) and a Rare Power priced as an Uncommon. The gap is not a number on a Common; it is that the kit's only long-fight engine is the Casket, and it needs the Plans written first.

## 2. Archetype structure and what play actually rewards

**Intent (brief sec.1, 3, 6).** "Kokomi wins the fight before it starts." Three loops: the Tactician (Plans, per-carry-out payoffs, order riders), the Priestess (Block through the jellyfish, Dusk, Mend only at Rare), the Commander (Gorou and the Inazuma companions). Plus the Casket readers and one replay card. The halves rule: the now-line answers this turn, the Plan line buys what only a head start can buy.

**What seats do** (`cards_played` and `damage_by_source`, 152 solo fights since 10-01, any upgrade form counted, `kkrev/verify6.py`; shares are confounded by six runs' drafts and there is no offer or pick data, packet sec.7):

- Strike is in 96% of fights (139 of 152 with the unupgraded name alone); Slack Water 55%; Open the Casket 65%. Her own pool's best-played: Surging Shoal 36%, Feint 23%, Nip 22%, then Shell of Sanctuary and Tidal Screen. Strike's damage share is 15.1% in the clean window (702 of 4,642); the 29.4% over all 152 fights is inflated by the 115 fights that omit Plans.
- Plans are 23.3% of her damage in the clean window and land in 34 of 37 fights: the Tactician loop is in use every fight.
- Companions did the shattering: Kaeya's Frostgnaw (24% of fights, 720 damage), Clorinde (647). 10-01 record: "Every best turn came from these, not from choosing a line."
- The flip decides little. Chooser build (10-01 klee-kokomi record): 2 flips in about 69 screens, "one a mistake, one sound but unlucky". Click build (10-02): "No seat flipped a Plan across the whole round." 10-05: once, on Kurage's Oath+.
- The Casket is read correctly since it repeats: seats open it at 4 or more, before writing Plans (10-02 record, "The Casket is now a decision").

**Where the loops stand.**

1. *Tactician*: built and rewarded. Order riders (Opening Gambit, Second Wave) were named as best turns in three records. Order is the decision the kit has.
2. *Priestess*: eight now-line Block cards in 78 (`kkrev/census.py`) plus nine rows with Block on the Plan line (Read the Field, Tide Wall, Breakwater, Shell of Sanctuary, Bubble Ward, Current Read+, Evening Watch, Brace for the Tide, Kelp Wall). Block is no longer the headline complaint: at the one same-HP boss she took less a turn than Ironclad (10-01 klee-kokomi record line 33; the Matriarch fight), and her 10-05 act-2 and act-3 hallway HP losses are under the base five's. But her 10-02 normal fights cost more HP than the control's on both seeds (sec.1.3), so "Block is fixed" is not the record's verdict either. Mend sits on two Rares. Dusk is on five rows; Evening Watch and Brace for the Tide are among the least-played cards.
3. *Commander*: Gorou (one row), The General's Banner, Watatsumi Resistance; the Inazuma companions are shared-roster rows. Played, but the loop has three cards.
4. *The Big Plan and the "alone" cards.* Lull, The Long Game, Undertide Lance and Measured Breath are the Big Plan deck [USER] ruled (`kokomi-expansion-2026-09-29.md` lines 50-68; brief line 303, "The defaults work here"). They pay for exactly one or no Plan waiting, in a pool whose Commons are five 0-cost feeders (four-kit review sec.4 point 3). None has a logged play, but with no offer data "never drafted" cannot be told from "drafted and bad". The expansion sim had the Big Plan 10 points behind volume before and after the big-Plan pass (STATE: "the sim's gap has another cause"). Weight of the Plan and Grand Design read Energy paid, which the feeders never add to.
5. *The status sub-theme* (seven cards, ruled 10-01): Flotsam Surge 11% of fights, Riptide Ruin 5%; Kelp Wall 4 plays, Sea Glass Harvest 3, Turning Tide 6, Tidecleanse 2, Abyssal Salvage 0. Two NEVER AGAINs on Sea Glass Harvest led to its 8 [11] Block (prediction on file). Thin evidence, but seven slots for the least-drafted cards in the pool.
6. *Plan the reaction* (ruled 2026-09-27, pick 2a, "as the first growth batch"; never built): her Hydro is the half of every Frozen and Vaporize the seats praised, and the pool reached 78 without a card that plans one. At Water's Edge is her only reaction reader.

**Kit checklist** (`docs/current/kit-checklist.md`): check 2 (player-controlled leverage) yes since the Casket repeats; check 3 (binding prices) yes, the either/or is the price on every two-line card; check 4 (visible and live) has three open BACKLOG lines (sec.5); check 5 (simple surfaces) is the weak one, Uncommon median 72 rendered characters against the base's 48, nine faces over 100; check 8 (distinct play patterns) asks whether archetypes differ in route and cadence, and volume, Big Plan and Dusk Guard do, so yes. Whether the Big Plan also wins is a balance question (pick 3), not a check-8 failure.

## 3. Fun

**[USER], in order.** 2026-09-07: "the central loop feels too auto-pilot." 2026-09-23: "generally not a choice so much as a math problem." 2026-09-28 (39 to 46 cards): "Kokomi feels... weird", "undercooked at this stage." 2026-09-29 (48 cards, after the feed pass): "My initial reaction to the new Kokomi version is that I like it! ... the numbers tweak and addition of 0-cost cards makes this much more playable." 2026-10-01: "Interesting idea! Yes, I think this makes sense" (the open Plan). The friend's solo run of 2026-10-04 is the last human voice: every Rare "bad" next to 0-cost Plans under Casket Strength (that produced the big-Plan and Rare passes). STATE records no [USER] run on the 78-card build; the 09-28 "undercooked" quote lives only in the memory file.

**Is "undercooked" still true?** No, on the evidence. It named a now-line worse than Defend (fixed: Oath 6 Block), hard-to-read two-line faces (fixed: "Or plan:" on its own line), duplicates (Tide Chart and Scout Ahead cut), Riptide undertuned (now 11 to ALL plus Energy and draw), and a 39-card pool. All five are gone. The seats now report the opposite failure: a kit that produces its promised turn and still loses long boss fights.

**Seat-reported highs:** "11 AoE for 1" (Deep Current); "Strength before writing Plans was the best line in the round"; "Plan or play now, and the order Plans are written in, were real decisions in every act" (10-05); "Planned turns were the best turns in both runs" (10-01); Frozen through Kaeya, chosen over attacking to keep the freeze. **Lows:** NEVER AGAIN on Sea Glass Harvest (twice), Tide Wall, Coral Tithe ("needs 3 in the Casket"), a second Masterstroke; "Open the Casket was tried from hand while it sat in the discard pile, three times"; hidden turns (Soul Fysh's Intangible) voiding the Plans written into them (10-01); Smoggy's one-Skill turns shutting off a kit that is 38 of 78 Skills (BACKLOG line 52).

## 4. Solo and co-op

- **Two human co-op runs, one on this kit.** JPDNY5JWA7 (2026-08-16, 23 fights, the retired kit) and 025GJP88JJEC (2026-09-30, A0, 19 fights; [USER] on Varka, a friend on Kokomi; both died at Aeonglass). In the 09-30 run Kokomi's seat is credited 2,476 to Varka's 2,283 over 126 turns, but both totals predate the 10-02 credit rule: her Plans were uncredited and so were element and reaction hits, Varka's main source (`PlayTelemetry.cs:551-555`: credited damage then covered 36% of enemy HP plus Block). Two numbers undercounted in different ways say nothing about which seat was weak. What the row does show: her top credited sources were Sow (671), Slack Water++ (449) and Shiv (417), a Necrobinder card and Silent relics on a 69-card pool. The friend's "no payoff for playing lots of Plans" and "short on block" produced Kurage Canopy and Coral Tithe.
- **The five co-op cards have zero logged plays in any Kokomi fight, all time** (`kkrev/verify.py`): Joint Orders, Coordinated Strike, Tactical Relay, Sangonomiya's Counsel, Kurage's Mercy. BACKLOG line 26 marks two (Tactical Relay, Kurage's Mercy) "pinned headless only".
- **No paired round under the 2026-10-06 bar** (`operations/stage-gate.md` line 80; packet sec.7). Her solo reaction rate is 0.30 a turn (packet sec.4.4); Klee's is 0.32, Furina's 0.46, Varka's 2.18, so she sits with the Pyro kit, not apart. The risk is a prediction: beside a Pyro, Cryo or Electro kit her Hydro enables every reaction while only At Water's Edge reads one, the shape [USER]'s bar warns about from the enabling side. Only a paired round can say whether it happens.
- Off-character use of her Plan cards is handled (Kurage-only targets, no-target auto-play refused, #898) and tested (`KokomiOffCharacterTargetTests.cs`).

## 5. Text and tooltips

Lint passes (`tools/lint_text_conventions.py`, 509 strings). Against `docs/current/text-conventions.md`:

- **Length (target 80, ceiling 120).** Common median 49, Uncommon 72, Rare 71, against base 33 / 48 / 56. Nine faces over 100: Suffocating Deep 120, Nereid's Ascension 114, Undertide Lance 112, Read the Field 111, Opening Gambit 106, Flank 105, Kurage School 103, Moon's Reflection 102, Feint 101. Second-longest sheet after Klee (Furina's median is 38).
- **Rule 8** ("a bonus is N additional damage"): Riptide says "{n} more to debuffed ones". Breakwater's Plan says "and 3 more for each Plan waiting" (Block; the rule has no Block form). Grand Design and Kurage Swarm say the Casket "gains 1 more", a count, not a bonus.
- **Rule 13** (Exhaust is a rail, never a sentence): nine sheet rows type "Exhaust." and rely on the codegen strip (The Moon, Vanguard, Change of Plans, Moon's Reflection, Suffocating Deep, Brace for the Tide, Spring Tide, Kurage School, Kurage's Mercy).
- **Named tokens:** Open the Casket is golded on the sheet; Nip, Nips and Sea Glass are not. The conventions table has no row for a token card's name.
- **The Plan tip** (`klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs:361-366`): "Instead of the line above, play the card on the Bake-Kurage: it happens next turn. Click it to flip lines. Plans go in the order made." 134 characters against a 135 ceiling (`lint_text_conventions.py:68`), shortened to fit (comment, line 354), opening ruled (status batch pick 2). It also prints on Plan-only cards, where there is no line above and no flip; those could carry a shorter tip of their own.
- **Open the Casket:** the token's tip omits the upgrade's "draws 1" (provenance, "Kokomi kit review"). The relic text does not say the count keeps growing after it is opened, which surprised a seat (09-29 record).
- **Visibility (check 4), already on BACKLOG:** line 44 (the Neow bundle's Plan gloss; the Casket tip and a reaction debuff), line 45 (the Plan list prints a waiting Plan's damage without Vulnerable: Surging Shoal 50 there, 75 landed), line 52 (Smoggy refuses writing a Plan and nothing says why).
- **Tide Wall** reads the front enemy's intent while the face says "the enemy". The main session dropped that wording item on 2026-10-05 on purpose (`docs/notes/prototype-surface-provenance.md:6613-6619`: the Plan tip already says a Plan hits the front enemy; lint forbids "front enemy" on a Plan line). Not re-raised.
- **Cross-character:** Kokomi's "Or plan:", Furina's Drain mode ("Drain 3: deal 12 instead") and Varka's Knight rail are three ways to print a choice; each is in the conventions table and none conflicts. "Play on the Bake-Kurage." as a first line matches the Knight rail's shape.

## Hygiene Claude can just do

- Records: one line in `review/records/kokomi-review-round-2026-10-05.md` saying its per-turn figures omit Plan damage (credit rule `PlayTelemetry.cs:549-563`, 10-02) and that the file it cites, `klee-balance-measurement-2026-10-05.md`, is on branch `klee-measure`, not main; carry the caveat into that paper's sec.3 when the branch lands.
- Telemetry: re-run her report `--since 2026-10-05`; add to `telemetry_report.py --help` that a per-character window should start at a build, not a date (run 5JNWQ9G4YNV7 spans 10-01 22:36 to 10-02 10:00).
- Sheet: delete the typed "Exhaust." from the nine rows that declare `exhaust: true` (rule 13; no face changes).
- Sheet: Riptide "N more to debuffed ones" to "N additional damage to debuffed ones" (rule 8); decide in `text-conventions.md` whether Block bonuses take the same word, and apply to Breakwater if so.
- Text-conventions: add a row for a token card's name on a face (gold it) and apply to Nip, Nips, Sea Glass.
- Tips: a Plan-only tip (no "line above", no flip; room for "carried out in the order written" there without touching the ruled two-line tip); Open the Casket's tip gains "draws 1" for the upgrade; the Casket relic tip says the count keeps counting after it is opened.
- Shorten the nine faces over 100 toward 80 where a word can go without a rule change (Flank "when you wrote this" to "when written"; Suffocating Deep's "to each" is implied by ALL; Read the Field's scry phrasing, check `game_ref` for the shorter form).
- Generated code: all 85 `Generated/ProtoKk*.cs` files say "Upgrade deltas come from docs/kokomi-upgrades.yaml", a file that does not exist; point the comment at the sheet. (Change of Plans+ and Tidal Resonance+ both work: `ProtoKkChangeOfPlans.cs:84-87` removes Exhaust; `ProtoKkTidalResonance.cs:70-73` gates the draw on upgrade.)
- BACKLOG lines missing: Open the Casket tried from hand while in the discard pile (the seat page should print its pile); the cut cards' engine clauses (Tide Chart, Song of Pearls, Scout Ahead), which the brief says BACKLOG lists (lines 255-257) and it does not.
- Brief: carry [USER]'s 09-28 verdict in one line (sec.4 or 6) so "undercooked" exists in the repo; line 393's "Uncommon Skill" for Shell Guard gets "(Common since 2026-09-29, line 239)".
- STATE's Kokomi bullet is about 120 lines of pass history; cut it to what ships and what is next (the tech-debt lane's item).

## Picks

1. **The boss gap: when the paper is written.** STATE says after your run; the seats have added evidence since.
   - **(a, Default)** Your full run on the 78-card build first, as the finish line requires (a central rule changed); STATE lets a friend's co-op run stand in. The damage paper follows, with sec.1.3 as its evidence.
   - (b) Write the paper now from the seat evidence, with two named candidates: a long-fight engine she does not have to draft (on the relic or the Casket, growing with Plans carried out across the fight), and the Rare Powers' wage.
   - (c) No paper; a paired co-op round first, then read both together.
2. **The opening Plan** (four-kit review pick 2, held "until pick 1's round is read"; it has been). Two new facts pull apart. For it: the sim's gain was at the act-1 boss (72% to 89%), still where she dies most. Against it: on 2026-10-05 you turned down a combat-start Bomb on Klee's starter relic ("I'm not really a fan of that relic redesign"); a Bake-Kurage that starts every combat with a Plan written is the same kind of free setup, and you preferred a drafted card earning the gain.
   - **(a, Default)** Keep holding; read it again after your run.
   - (b) Build it as a trial rule (the Bake-Kurage starts each combat with Kurage's Oath's Plan written, upgraded if yours is) so your run tests both. The option your Klee stance argues against.
   - (c) Drop it; if the act-1 boss stays the wall, answer with a drafted card (pick 3 or 4).
3. **The "alone" cards and the Big Plan.** Lull, The Long Game, Undertide Lance and Measured Breath are the Big Plan deck you ruled on 2026-09-29; none has a logged play, but no offer data exists; the Big Plan trails volume by 10 points in the sim.
   - **(a, Default)** Keep the four through your run; the next seat round logs offers and picks per card, so "never offered" and "offered and passed" can be told apart before any re-aim.
   - (b) Re-aim the four onto Energy paid for the Plans waiting (Weight of the Plan, Grand Design), so the feeders neither help nor hurt them. A main-session card pass; re-opens the 09-29 ruling.
   - (c) Cut the four and give the slots to "plan the reaction" (pick 4).
4. **"Plan the reaction" and the status sub-theme.** You ruled on 2026-09-27 that "plan the reaction" is the first growth batch (pick 2a) and set the order core, seat, run, team batch, growth to 78, relics (pick 4a). The pool reached 78 with seven status cards instead; the four-kit review (sec.4 point 4) said freeze at 78 and swap status cards out for it. Any option but (a) re-opens that ruling.
   - **(a, Default)** After your run, swap the two least-played status cards (Abyssal Salvage, 0 plays; Tidecleanse, 2) for two cards that plan a reaction on her Hydro; Sea Glass Harvest keeps its slot while its prediction is open. The batch earns the seat round in pick 6.
   - (b) Keep the status batch; build the reaction cards only if the paired round (pick 6) shows her a pure enabler. Demotes the 09-27 ruling to conditional.
   - (c) Build the reaction batch as additions and let the pool sit above 78. Against the four-kit freeze.
5. **Her own relics and potions.** She still borrows the Silent's roster (`klee-mod/KleeCode/KokomiRelicPool.cs:10`). Klee and Varka have seven relics and three potions each (STATE.md lines 262-264, 318-322); Furina's re-founded kit carries three (line 224). The heal is ruled onto "the Common relic of her own set" (four-kit pick 3a), and your 09-27 order puts relics after growth. A new relic pool changes what your run draws, which breaks the one-variable reason for holding pick 2.
   - **(a, Default)** Design and build her set after your run, main session, heal on the Common relic as ruled; it ships with the pick-4 batch into one seat round.
   - (b) Build it now, before your run, and accept the run tests two changes.
   - (c) Wait until she is ruled to Balance.
6. **The paired co-op round.** Seat rounds run only on a rule change or a new card batch (CLAUDE.md); the 2026-10-06 bar wants a paired round on shared seeds before Balance; the five co-op cards have never been played, so the decks need them placed.
   - **(a, Default)** Run it on the pick-4 batch: Kokomi plus a Pyro or Cryo kit against Ironclad and Silent on shared seeds, the five co-op cards placed, one one-page record.
   - (b) Run it now on the current build, before your run.
   - (c) Defer to the Balance gate.

## Fact-check log

Every point was checked against the records, sheet, code and telemetry (`kkrev/verify6.py`). Changed:

- Summary, sec.1.2: "better on HP in hallways" and "delay shows up as a turn, not HP" replaced with the act-by-act read (act 1 8.8% against 7.1%; 10-02 normal fights 10.2 and 18.1 against 4.6 and 14.3). "Mostly an instrument fault" softened to "part of", with the two-run window and the base undercount caveat stated.
- Summary, sec.1.3: "same door HP" removed (doors 39 against 90, 92 against 104); the same-HP fight is the four-kit review's Matriarch (71 against 74), now cited as such; the "less a turn than Ironclad" line re-attributed to the 10-01 klee-kokomi record, line 33.
- Sec.1.1: ten runs over five builds, nine deaths; the slow-deck bosses killed two of her last four, not three; "one more win than the base five" qualified by the control's win on her seed and its reduced pools; the Varka/Furina sentence moved to the pool-round row where it lives, column renamed (game-rolled seeds); "Queen at 5 HP" to "won with 5 HP left".
- Sec.1.2, hygiene: the "her losses are never logged, a defect of her arm" item removed; no character's losses were filed before fc05aa88 (10-05 19:23), her last fight was 10-05 14:25, `--help` documents it. The Klee measurement paper item redirected: that paper is only on `klee-measure`; the defect on main is the 10-05 record's citation.
- Sec.1.4: feeders 9.5% (125 of 1,320), not 10.3% (the eight Plan-only cards); Neutralize is a Basic; Jellyfish Drift is a third of Astral Pulse; Ceremonial Garment moved to the Rares; Riptide Ruin 613 total, "came from Strength" marked an inference; verdict softened with the exceptions named.
- Sec.2: any-form shares (Strike 96%, Surging Shoal 36%), Strike's clean damage share 15.1%; flip history corrected (2 in about 69 screens on the chooser build, none on the click build, once on 10-05); Tidecleanse 2 plays; the four "alone" cards named as the ruled Big Plan deck with the no-offer-data caveat; check 8 re-read as route and cadence; nine Block Plans.
- Sec.4: two human co-op runs; "not the weak seat" withdrawn (both totals predate the credit rule); Klee's 0.32 beside her 0.30; "pure enabler" marked a prediction; BACKLOG line 26 only.
- Sec.5, hygiene: Tide Wall not re-raised (dropped on purpose, provenance 6613-6619); the Plan-tip rewording dropped (134 of 135 characters, ruled opening) in favour of a Plan-only tip; "confirm two upgrades" replaced by the fact that both work plus the stale `kokomi-upgrades.yaml` comment; `GITS_KOKOMI_PLAN_CAP` and Second Thoughts removed (the brief names neither); relic pool path added; Shell Guard's stale brief line, BACKLOG 44/45/52, Breakwater's "more" and the calendar-split caveat added.
- Picks: 1 names the friend's stand-in; 2 names the 2026-10-05 "no free setup on the starter" stance; 3's default is hold and log offers, the re-aim marked as re-opening the 09-29 ruling; 4's default is the ruled swap after the run, (b) marked as demoting the 09-27 ruling, (c) as against the freeze; 5 corrected on who has relics and moved after the run; the paired round moved from hygiene to pick 6.

Rejected or qualified:

- "Klee and Furina have seven relics and three potions each" is out of date only for Furina's current kit: STATE.md lines 318-322 still say both sets are built behind the arms; line 224 gives the re-founded Furina three. Both facts are in pick 5.
- "The brief calls Shell Guard an Uncommon Skill" is true of line 393, but line 239 records the demotion to Common, so the brief is not in conflict with the sheet; only its 09-28 note is stale. One-line hygiene, not a cross-file disagreement.
- "All 86 generated Kokomi card files": the count is 85 (`git ls-files | grep Generated/ProtoKk`). The point stands.
- Rule 8 and "more": of the four Kokomi rows with "more", Grand Design and Kurage Swarm describe a Casket count, not a bonus, so only Riptide and Breakwater are listed.
- The death counts the draft quoted for other kits (Klee 26, Varka 4, base 2) have since moved (30, 6, 6, as the Klee suite logs); the paragraph that used them is gone.
