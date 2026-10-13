# Klee kit review, 2026-10-08 (revised after fact-check)

Build read: `origin/klee-next` 063e1b40 (growth 2, three opening Sparks, drafted placers +2, Fire! Fire! and Blasting Spree in; `tier0/constants.py` lines 148 and 160). Papers and records from `origin/main`. **Klee is at Balance** (`STATE.md` line 45: "ruled 2026-10-03; measurement plan being drafted"; `QUEUE.md`: "Her measurement plan comes to [USER] as a paper"), so measurement law binds: a sheet number or a new grading measure is [USER]'s, and the picks below are written for that plan. The design review of 2026-10-08 is ruled and in test; this paper takes it as given.

Fight numbers: `tools/telemetry_report.load_fights`, bot feed, one seat, normal fights unless a boss or elite row is named, medians unless "mean" is said. Windows are drawn **by `run_instance`, not clock time**: base five = the five counted baseline runs (`20261005-1055xx` and Regent `20261005-113940`, 115 rows); suite 4 = `20261007-2048xx` (92 rows); suite 5 = `20261007-2357xx`, snapshot 2026-10-08 01:04 (94 rows, live). Script `kr_rev/snap.py`, output `kr_rev/snap.out`, beside this file.

**Summary.** The suite records and the design review graded Klee against a base window (10-05 before 16:50, 220 rows) of which only 115 rows are the counted same-seed runs; the rest are an off-seed Ironclad run, the stopped reduced-pool attempt (`base-five-baseline-2026-10-05.md` line 3: "stopped and is not counted"), a duplicate run and 7 doubled rows. On the counted runs: **act 1 is outside the 15% bar** (HP lost ratio 1.31), act 2 inside (0.78), act 3 outside (1.65), and the act-3 gap is at **every** enemy count. She does not take less damage a turn than the base five (1.99 / 2.45 / 2.80 against 1.77 / 3.27 / 2.80, mean); she Blocks more in every act (3.9 / 7.4 / 9.8 against 2.7 / 4.0 / 7.6) and her act-3 fights run longer (4.7 turns to 3.5), which is where the HP goes. Suite 5 at 01:04: act-1 turn one has not moved (11.5 damage; suite 4 12.1; base 21.3), acts 2 and 3 have (18.5 and 24.8 from 10.6 and 5.3), the act-2 boss killed 2 of 5 runs, Blasting Spree is at 0 fights of 94, Block a turn is up again (4.4 / 6.3 / 11.6). Structurally, 16 of 78 cards have zero plays in 344 clean seat fights and the brief's loops, boards and scripts still run on five cut cards. Fun is good where measured. Co-op: the paired Klee + Varka round does **not** show Klee as the soft target (194 HP lost to Varka's 225 over 24 fights), every bot co-op row is written twice, and ally shields exist on the partner side; the first draft's co-op pick is withdrawn.

---

## 1. Power level and balance

### 1.1 Where she stands, on the counted baseline

| Act | Suite 4: damage/turn ratio, HP lost ratio (n) | Base five HP lost (n) | Bar |
|---|---|---|---|
| 1 | 0.97, **1.31** (34) | 4.7% (36) | outside |
| 2 | 0.95, 0.78 (21) | 12.8% (24) | inside |
| 3 | 0.80, **1.65** (18) | 12.1% (28) | outside |

Klee won 0 of 5 in each of suites 1 to 4; the Common test arm won 2 of 5 (`klee-suite-3-2026-10-07.md`, result table, "Test arm"); **the base five also won 0 of 5** (`base-five-baseline-2026-10-05.md` line 5), so "0 wins" is level with the control. End floors, suite 4: 48 / 48 / 39 / 9 / 33 against 48 / 48 / 48 / 46 / 48. Act-1 and act-2 bosses at or better than the base five (38.7% and 46.4% HP lost to 52.9% and 50.0%); the act-3 boss lost on both suite-4 visits (61.3%) and the one suite-3 visit (`packet-klee.md` T2, n=1).

**The act-3 gap is at every enemy count.** Suite 4, HP lost and mean turns: one enemy 28.6%, 5.4 turns (9 fights); two 20.0%, 4.3 (4); three 7.2%, 3.8 (5). Base five: one 14.8%, 4.2 (16); two 4.3%, 2.8 (5); three 0.0%, 2.6 (7). The single-enemy fight is the largest in HP and the most frequent, but the ratio is wider on two and three. Suite 5 so far: 24.2% / 0.0% / 4.9% on 9 / 1 / 4. One gap, one lever (fight length); read it by enemy count, not as three problems.

**Mines are two fifths of her explosion events and a seventh of her damage.** Suite 4: 171 of 373 detonations in normal fights were Mines (46%), 27 of 63 in elites, 38 of 112 in bosses; suite 5 41% / 41% / 39%. The counter (`ProtoBombPowerTelemetry.cs` lines 46 to 63, from `ProtoBombPower.cs` line 1381) records every charge that goes off, whatever set it off, and counts events, not damage (Jumpy Dumpty's Mine 3 on ALL is one event per enemy). By damage, Mines are 12% / 17% / 13% of normal-fight damage in acts 1 / 2 / 3, Bombs 33% / 29% / 45% (`packet-klee.md` T6). The "when do I cash" decision governs the damage. One fight in 92 had zero detonations.

**Slower, not sturdier per turn, and more Block.** Damage taken a turn (mean): act 1 1.99 to the base five's 1.77, act 2 2.45 to 3.27, act 3 2.80 to 2.80. Block a turn (mean) 3.9 / 7.4 / 9.8 to 2.7 / 4.0 / 7.6. Act 3: 4.7 turns to 3.5, and 4.7 × 2.80 is the 13.4 HP a fight she loses to their 10.9; the tempo paper's lever is right for act 3. Act 1 is a different shape: same length (3.06 to 3.03), more damage taken a turn, more Block. The review's sec.5 measures "Block gained a turn at or below the base five's" (line 573) and names Blast Shield at 3 Sparks as a risk (line 532); it does not say what to do when Block stays high while fights shorten. Pick 2.

**Suite 5 at 01:04 (live; not a grade).** Act 1, 35 fights: 21.7 damage a turn (suite 4 19.0; base 19.6), 4.3% HP lost (6.1; 4.7), 2.80 turns (3.06; 3.03), Block 4.4 a turn (3.9; 2.7), turn-one damage 11.5 (12.1; 21.3), a Set off on turn one in 7 of 35 (4 of 34). Act 2, 23 fights: turn-one 18.5 (10.6; 32.1), Set off on turn one 11 of 23 (5 of 21), 7.8% HP lost (10.0; 12.8). Act 3, 14 fights: turn-one 24.8 (5.3; 53.2), 14.2% HP lost (20.0; 12.1), 4.1 turns (4.7; 3.5), Block 11.6 (9.8; 7.6). Bosses: act 1 won 5 of 5 at 29.9%; act 2 **lost 2 of 5**, 55.8% (suite 4 46.4%; base 50.0%). Uptake: Fire! Fire! 13 fights, Explosive Spark 24, Blast Shield 16, Blasting Spree 0. Turn one moved in acts 2 and 3 as intended and not in act 1; the act-2 boss and act-3 Block are the numbers to watch.

### 1.2 Card by card against the base at the same rarity and cost

Base from `game_ref/<char>.json` (`base-pools-compact.md`); Klee from the klee-next sheet. "Spark" means the card also costs Sparks.

| Klee card | Nearest base cards | Read |
|---|---|---|
| Explosive Spark, C, 0 + 1 Spark: 12 [16] | Slice 6 [9]; Collision Course 10 [14] **and a Debris**; Anger 6 | [USER]'s price: Slice plus 6 for the Spark. 12 for 0 Energy on turn one at 3 Sparks; 24 suite-5 fights. Top of its slot. |
| Fire! Fire!, C, 1: Bomb 7 [10], Set off | Strike 6; Solar Strike 9 + Star; Pommel Strike 9 + card; Guiding Star 12 + 2 cards | Below the Regent Commons plain, above them with a Bomb cooking. Right for tempo. 13 fights. |
| Fish Blasting, C, 1: 8 [11] ALL, a Confiscated | Thunderclap 4 [7] ALL + Vulnerable; Dagger Spray 4 [6] ×2 ALL | Double Thunderclap for a dead card. 54 fights, never NEVER AGAIN. Leave. |
| Blasting Spree, C, 1: Bomb 4 [6] ALL, a Dazed | same row | 4 to ALL a turn late plus a Spark an enemy. Fair. 0 fights of 94. |
| Dig In, C, 0 + 1 Spark: 8 [11] Block | Deflect 4 [7]; Boost Away 6 [9] **and a Dazed**; Cloak of Stars 7 [10]; Shrug It Off 8 + card for 1 | Shrug It Off's Block for 0 Energy and a Spark, no drawback. Pick 2's lever. |
| Blast Shield, C, 0 + 1 Spark: 4 [6] Block, returns to hand | Deflect 4; nothing returns itself | 12 Block for 0 Energy on turn one at 3 Sparks (review line 532). The review states the stack (line 524: "Dodoco Tales adds 4, so 7 with it"); unstated is 7 × 4 = **28 Block** turn one through this card. 16 suite-5 fights. |
| Bombs Away!, C, 1: Bomb 6 [8], Block 4 + 2 per enemy with a Bomb | Iron Wave 5 + 5 | Iron Wave deferred, Block to 10 on three. Second most-played drafted card (102 fights; Booby Trap 138). Fair. |
| Behind Jean's Desk, U, 1: 11 [14] Block, a Confiscated | Leap 9; Leg Sweep 11 + Weak for 2 | Leg Sweep's Block at half the Energy. Generous; 21 fights. Leave this round. |
| Countdown, C, 1: Set off, draw 2 [3] | Pommel Strike 9 + card | The only Common detonator that draws. 49 fights. Fair. |
| Lisa's Treats, U, 0: +2 [3] Energy, 2 Confiscated | Turbo +2 [3] + a Void, C | Turbo with two dead cards, one rarity up. Slightly under; 7 fights. Watch. |
| Dodoco Tag, U, 1: 7 [10] + 5 [7] Block, a Dazed | Iron Wave 5 + 5, C | Two more damage, the same Block, a Dazed, one rarity up. Fair. |
| Cover Your Ears!, U, 0 + 2 Sparks, Exhaust: ALL lose 6 Strength this turn | Piercing Wail, C, 1, Exhaust | Piercing Wail for 2 Sparks. Dead at 1 opening Spark (three NEVER AGAIN records); live at 3. Read first. |
| Big Badda Boom, U, 2: Set off, 12 [16], then the Bombs' damage again | Uppercut 13; Dash 10 + 10 Block | Uppercut plus the pile twice. Best-played payoff (99). Two text defects, not balance (`BACKLOG.md` 81, 87). |
| Red Knight, R, 2: 34 [40], 2 Confiscated | Hyperbeam 24 [30] ALL **and lose Focus**; Bludgeon 32 [42] for 3, U | Bludgeon's number for 2 Energy and two dead cards. 7 fights. Fair. |
| The Big One, R, 3 [2]: Set off, Bombs ×4 | Mangle 20 [26]; Ice Lance 19 ×3 | 172 on a 43 Bomb (suite 4); a 43 Bomb now takes twice the turns. The review reads it in suite 5. |
| Klee's Secret Base, U Power, 1: Bomb 6 [8] a turn | Noxious Fumes, U, 1: 2 Poison ALL a turn | Fair; 88 fights. |

Cook's growth cards keep their numbers under growth 2 (Chain Fuse +6, Witch's Homework +8, Stoke the Fuse +5 a Spark, Exquisite Compound +5, Alice's Guidebook +3 a turn, Dodoco Charm +1; `packet-klee.md` sec.5.3), so in turns of growth they are now worth 3, 4, 2.5, 2.5, 1.5 and 0.5 (before: half that). Intended ("Cook becomes the plan you draft into", review sec.3); the review's sec.5 item 5 and the act-2 boss deaths above are where to look.

---

## 2. Archetype structure against the identity

Plays from 344 clean solo fights, suites 2 to 4 plus the test arm, 19 runs (`kr_rev/snap.out`). Taste Test and Tinkering entered with suite 4 and had 92 fights to be played in (`klee-suite-4-2026-10-08.md` lines 4 to 6). The telemetry counts plays, not drafts or offers.

| Line | Cards | Played (fights) | Zero plays |
|---|---|---|---|
| Cook | 16 | Big Badda Boom 97, Quick Fuse 65, Chain Fuse 30, The Big One 25, Stoke 12 | Taste Test, Albedo Dust, Jean Lion's Fang |
| Spray | 30 | Booby Trap 132, Bombs Away! 97, Secret Base 88, Mine, All Mine! 68, Dig In 63 | Sparks 'n' Splash, Dodoco (6 suite-5 fights now), Tinkering |
| React | 7 | Perfect Timing 25 (suite 4: 13 of 19 fights with a reaction), Sizzle 14, Flash Point 14, Wait For It... 3 | Sparkborne Magic, Aftershock |
| Companion | 7 | Coven Errand 59, Team Effort 8 | Little Hexenzirkel, Tag Along, Come Back and Play!, Adventure Club, Alice's Introduction Magic |
| Status | 16 | Fish Blasting 54, Forbidden Fun 52, Dodoco Tag 23, Damage Report 3 | Kitchen Alchemy, Klee Can Explain! |

Sixteen of 78 have zero plays (the fifteen above plus All of My Treasures!). Kitchen Alchemy was kept by [USER] for his own play and stands. **Companion is one Common and five slots**; the brief calls it "a bridge, not a loop" (sec.7), and it depends on which companions the run offers. **React is three companions** (suite 4: Oz 21 fights, Mika 14, Diona 13); the ruling keeps it companion-fed, nothing to change. Pick 4.

**Sparks: "the second contest" (brief line 165) is half true, and a rule just changed under it.** The reads are mixed. [USER], 2026-09-08: a Spark-paid defence "did not quite have the consistency I needed" (`klee-user-run-2-2026-09-08.md` line 19), read beside round 23's "deadlocked on a deck of Spark cards" (line 38). [USER], 2026-10-01: "I never really felt pressed for them" (STATE.md). Seats: Spark cards dead at 1 opening Spark; Sparks idle otherwise (later-acts round line 62, ruled "watch"; STATE.md line 61); one suite-3 death from a mid-fight shortage ("Fireworks Finale spent every Spark on the form-2 kill, so both Dig Ins were dead against a 45 hit", `klee-suite-3-2026-10-07.md` line 61). Short on turn one and on all-in decks, idle between. Idle-vs-short stays ruled "watch". **New fact, one line: opening Sparks went 1 to 3 on 2026-10-08, removing the turn-one shortage the brief's sentence leaned on.** Pick 3 asks only whether the sentence still describes the kit.

**Fast and fragile, against the numbers.** Fast: moving in acts 2 and 3, not act 1. Fragile: 70 HP, but damage taken a turn is not below the base five's and Block a turn is above theirs in every act and rising. The kit survives by Block and length; the lore's answer is Mines and running away (brief line 99: "Klee does not block"). Pick 2.

---

## 3. Fun, as reported

**[USER], three runs, positive on the loop.** 2026-09-08: "good concept ... the loop was fun" (`klee-user-run-2-2026-09-08.md` sec.1). 2026-09-24 co-op: "Klee was very fun, and I think that the loop basically works!" (`klee-balance-2026-09-25.md`). 2026-10-01: "the core gameplay loop was indeed fun and interesting, with a challenge around bomb management" (STATE.md). One run does not grade fun.

**Seats name the same two things every suite.** The wanted turn is a setup paying off ("Boom Badge + Big Badda Boom = 232", suite 3; "The Big One on a 43 bomb (172)", suite 4; "every one was a setup paying off. Order is the real decision", `klee-later-acts-2026-09-26.md` lines 36 to 37). The hated turn is a dead hand: no Set off with Bombs cooking, a Spark card at 1 Spark, "turn one is still setup" (`packet-klee.md` sec.6.2). The review's three changes aim at those three. NEVER AGAIN lists are **not** a stable set: the nine names (sec.6.2) come from suite 1, scaling round 1 and the Opus round; only Sparkling Burst and Cover Your Ears! recur; the Opus record says its single-seat names "each came from one seat. Watch them" (line 63). Five of the nine are Spark-priced, all named at 1 opening Spark; suite 5 is the first read at 3.

**The three-line fun gate is retired, not unrun.** `stage-gate.md` lines 62 to 63: "The old three-line calibration gate (...) is retired." Build one ran on two Opus seats (`klee-fun-calibration-2026-09-14.md` sec.5, "Seats' three lines, attempt two"); only [USER]'s lines were never collected. The fun read at Balance is his post-suite-5 run (review sec.5 item 6).

---

## 4. Solo against co-op

**The rule and the one reading.** A kit is judged solo; co-op is a paired round against Ironclad + Silent on shared seeds (`stage-gate.md` lines 80 to 86). The one round (`coop-reaction-round-2026-10-07.md` line 15): Klee + Varka died at the act-3 boss, floor 45, over two run instances (the first abandoned on a desync, the rerun played by several seats); Ironclad + Silent died at an act-1 elite on floor 7. The record: "One run a side is routing noise, not a strength reading."

**The partner is logged, and the rows are doubled.** Each fight has a Klee row (`seat_index` 0) and a Varka row (`seat_index` 1) in the same `run_instance`, joinable on `run_instance` and `floor`. Every bot co-op row is written **twice**: 62 Klee rows are 31 fights, 62 Varka rows are 31, each floor exactly two identical copies (`kr_rev/snap.out`). Means survive; every count in the first draft and in `packet-klee.md` T7 was doubled, and the reaction round's `--coop` counts should be checked. Deduplicated: 10 / 10 / 4 normal fights by act, HP lost 5.0% / 11.4% / 14.4% against solo suite 4's 6.1% / 10.0% / 20.0%; reactions 4.32 a fight against solo 2.08 (all kinds). Not "exponentially easier"; act 3 is easier with a partner, as for anyone.

**Klee is not the soft target in the logged pair.** 24 paired normal fights: Klee lost 194 HP (median 9.6% of 70), Varka 225 (7.2% of 80); Klee lost more in 12 fights, Varka in 9. Elites 76 to 66; bosses 160 to 161. The one record that showed her exposed (Klee + Furina, `coop-seat-round-2026-09-27.md` line 39, "down to 28/66, while Furina sat at 74 to 78") named Furina's Stage (hits on Furina only), the two ally shields never offered, and put the fix on Furina's side (lines 59 to 60). Ally protection exists where expected: Ironclad's Demonic Shield and Tank, Regent's Constellation (`game_ref`, `mp_only`, AnyAlly); Kokomi's Joint Orders ("Another player gains 6 Block") and Sangonomiya's Counsel (`prototype-surface.yaml` lines 2904 to 2923). Only 2 of Klee's 14 Block cards cost Sparks (`packet-klee.md` line 44). The first draft's guard-card pick is withdrawn.

**The co-op tier is reached and played.** Pass the Match 27 plays in 24 of 31 fights across both Klee + Varka instances; Hide Here! 21 and Knights of Favonius 13 in one human run each; Shrapnel and Sparks for Everyone never. **One interaction to log apart, not reopen:** the Furina round's "Hydro-for-nothing" note is the partner's Hydro-only cards reacting with Klee's fresh Pyro aura "and deal no damage" (lines 43 to 46), not Klee's Attacks spending a partner's aura; Klee's own amplifier bonus in the Varka round was 0.30 damage a turn. Log Bombs' and Attacks' reactions apart next round.

---

## 5. Card text, tooltips, conventions

The lint is clean: 509 prototype-arm strings meet the ceilings; the carried exceptions are the Bomb badge rider, two Kokomi cap faces and Durin's two-mode Power (`lint_text.txt` lines 2 to 5). 19 of 78 descriptions are over the 80 target, none over 120 (`packet-klee.md` line 50). Of the five longest only Flash Point (118) and Sizzle (117) carry "If a Bomb triggered an Elemental Reaction this turn,"; Taste Test and Simmer have no reaction clause, Aftershock says "triggers an". Writing "reacted" saves 24 characters, brings only Wait For It... under 80 and drops the golded keyword and its hover (`fc_klee/a11.py`); that is for the conventions review, not this paper. Sheet scan (`text-conventions.md` rules in brackets):

| Finding | Cards | Rule |
|---|---|---|
| One placement, three spellings ("Place a Bomb 8." / "on an enemy" / "on the enemy" / "on that enemy") | bare: Jumpy Dumpty, Booby Trap, Boom-Boom Strike, Lizard-Tail, Shrapnel; "on an enemy": Mine Toss, Coven Errand, Bombs Away!; "on the enemy": Fire! Fire!; "on that enemy": Mine, All Mine! | [3] |
| "Set off" as prose three ways | Pass the Match, Knights of Favonius; Sparkborne Magic; Prune | mod words: the event is "goes off" |
| "6 more" for a bonus; a semicolon; lowercase "status" as a type | Team Effort; Kitchen Alchemy; Finders Keepers, Klee Can Explain!, Damage Report, Kitchen Alchemy, Albedo Dust | [8], [14], [6] |
| A dead tooltip stating the old Bomb rule | `KleeMod.cs` 282 to 286 (`KLEEMOD-BOMB.description`, "Detonates at the start of your turn..."); `card_keywords.json`; `text-conventions.md` says twice the shipped kit keeps "detonates". The keyword is still declared (`KleeKeywords.cs` 88 to 90) and `KleeCardTooltips.ForCard` can raise it (`includesBombRules`, line 100); `ArmKeywordTipTests.cs` 157 asserts the arm never emits it | the shipped kit is gone; the arm's tip is `KLEEMOD-ARM_BOMB` (`ArmKeywordTips.cs` 68) |
| Seven rows take the generator's default upgrade with no `upgrade:` block (`gen_prototype_cards.py` 199): Sizzle +3, Perfect Timing +3, Run Away! +3 Block, Boom-Boom Strike +3 / Bomb +2, Alice's Recipe cost -1, Chained Reactions +1, **and the starter Ka-pow! +3**, while brief line 615 says Ka-pow! retains "when upgraded" and the row has Retain on the base face | a sheet reader cannot see them | write the delta on the row; Ka-pow!'s upgrade is a starter fact and stays |
| The brief is stale outside its rules section | sec.4 (Grounded, line 153), 5.1 (Fish-Flavored Bait, Grounded, Sorry, Jean..., 188 to 203), 5.4 (257), 6 (358 to 367), 9 (648), 10's boards and 11's scripts (Kaboom!, Duck and Cover, Sorry, Jean..., Grounded, Pop!, 659 to 710); the lore row reads Sparks 'n' Splash as "set off a random enemy" | edited in place (CLAUDE.md) |

Tips (`ArmKeywordTips.cs` 163 to 245) read the law constants, so the rule change printed itself. "Companion card" is consistent across Klee and Kokomi and differs from the Knight rule; write it into the conventions table once.

---

## Hygiene Claude can just do

- **Grade by `run_instance`:** a run-instance filter in `telemetry_report.py`; name the five counted baseline runs in the suite records; append suites 2 to 4 re-stated on the counted baseline to the suite 5 record (numbers only; the ruled review's act-3 direction holds at 1.65).
- **Dedupe co-op telemetry:** find the second writer (62 rows, 31 floors, both characters) or dedupe on read; re-check the reaction round's `--coop` counts.
- Log Bombs' and Attacks' reactions apart; record what fired each Mine beside `mine_detonations`.
- Placement text to "Place a Bomb N." (Mine Toss, Coven Errand, Bombs Away!, Fire! Fire!) and "Place a Mine 6 on it." (Mine, All Mine!); the four prose "Set off" faces to "goes off"; Team Effort "6 additional damage"; Kitchen Alchemy as three sentences; "Status" capitalised on five readers; regen.
- Retire the old Bomb keyword in one change: loc row, `KleeKeywords.Bomb`, the `includesBombRules` path, the line-157 assertion, the two "detonates" sentences in `text-conventions.md`.
- Write the seven default upgrade deltas onto their rows (or a `default_upgrade` line).
- Edit the brief for the cut cards in secs.5.1, 5.4, 6, 9, 10, 11 and the Sparks 'n' Splash row (names and scripts only; which cards are "her defences" in sec.6 is the main session's). Sec.4's Spark sentence waits on pick 3.
- "Companion card" into the conventions table beside Knight.
- STATE.md's Klee entry (line 88 still says "won 0 of the 9 seat runs since the status package"; suites 1 to 5, the tempo paper and the design review are absent).
- Read Dodoco Tales' stack in the suite-5 records (7 Sparks, 28 Block turn one through Blast Shield).
- Backlog lines still right: 79, 81, 87, 92, 94, 145 to 147.

---

## Picks

1. **The read, and the instrument.** On the five counted baseline runs, act 1 is outside the bar (1.31), act 2 inside (0.78), act 3 outside (1.65) at every enemy count; she takes as much or more damage a turn as the base five in acts 1 and 3, Blocks more in every act, and loses her act-3 HP to fight length. The suite records and the design review used a 220-row base window with 105 off-seed, stopped or doubled rows. **Default: agree; the measurement plan grades suite 5 and after against the five counted runs by `run_instance`, with act 3 by enemy count and by kind.** Alternative: keep the time window for comparability and note the contamination once.

2. **What "fragile" measures once fights are short.** Suite 5's Block a turn is above suite 4's in acts 1 and 3 (4.4 and 11.6 to 3.9 and 9.8); suite 3 found "the deaths are Block, not damage" (`klee-suite-3-2026-10-07.md` line 51); suite 5's act-2 boss has killed 2 of 5. Trimming Block before those deaths are read is the wrong order.
   - **Default (a):** read suite 5's boss and elite deaths first; then, if Block a turn is still above the base five's with normal-fight HP lost at or below theirs, the lever is the Spark-priced Block, Dig In 8 to 6 [9] and Blast Shield 4 to 3 [5], as a numbered change in the measurement plan.
   - (b) Trim now and read on the next suite.
   - (c) Cut a Block card (Bombs Away! or Behind Jean's Desk); the review withdrew this once (sec.4.4).
   (The first draft's "accept fast and sturdy" is withdrawn: it re-asked the identity [USER] set on 2026-10-07, `klee-tempo-paper-2026-10-07.md` lines 5 to 12.)

3. **The brief's Spark sentence.** Opening Sparks went 1 to 3 on 2026-10-08; the reads are mixed (sec.2); idle-vs-short stays "watch".
   - **Default (a):** edit brief sec.4 to say Sparks are a bank gating the turn-one Set off and the all-in payoffs, in [USER]'s words where he has them ("only really matter if you're trying to let your bombs cook"); grade Spark sinks, not scarcity, in the plan.
   - (b) Keep "the second contest" and give the bank a Rare sink worth hoarding for (a main-session paper).
   - (c) Leave it; re-read after [USER]'s run.

4. **The unplayed fifth.** Sixteen cards at zero plays in 344 clean fights over 19 runs (plays, not drafts; Taste Test and Tinkering had 92 eligible fights; Dodoco has 6 in suite 5).
   - **Default (a):** after suite 5 and [USER]'s run, a cut-and-replace paper on the cards still at zero, Companion first. Kitchen Alchemy and Blast Shield are [USER]'s and stay.
   - (b) Keep all 78: a Sonnet seat not playing a card is not evidence [USER] would not.
   - (c) Shrink Companion now to the two cards with plays (Coven Errand, Team Effort) and give five slots to Spray and React Commons.

(The first draft's pick 5, a co-op guard card for Klee, is withdrawn: the paired round shows Klee and Varka losing HP alike, ally shields exist on the partner side, and the one record that showed her exposed placed the fix with Furina.)

---

## Fact-check log

Every point in the fact-check was re-run (`kr_rev/snap.py`, `fc_klee/a1.py` to `a16.py`) or re-read in the cited file before acting. **Rejected: none; all 24 held.**

**Changed.** Base window → the five counted runs by `run_instance` (act 1 now outside at 1.31; "same seeds" claim corrected). Suite 5 → drawn from 23:57, its 19 rows removed from suite 4, turn-one read corrected (act 1 unmoved, acts 2 and 3 moved), snapshot re-taken at 01:04 with the act-2 boss deaths, Block and Blasting Spree 0. Act-3 gap → every enemy count, base two-enemy row added, "no Mine cover" dropped. Mines → counter does not record the cause; event and damage shares both given. "Less damage a turn in every act" → withdrawn (1.99 to 1.77 act 1; level act 3). Fun gate → retired; build one ran; hygiene item removed. Co-op → partner rows joined, "one-eyed" withdrawn, the doubling added as a defect, counts halved (Pass the Match 27 in 24; acts 10 / 10 / 4), two instances and several seats, ally shields named, Hydro quote's direction corrected, pick 5 withdrawn. Sparks → reads given as mixed with the deadlock and the suite-3 shortage; "watch" ruling named; the one-line new fact stated. React clause → only Flash Point and Sizzle; 24 characters; moved to the conventions review. Suite 3 act-3 boss n=1; test arm cited to the suite-3 record; base five's 0 of 5 added. Booby Trap the most-played drafted card. Blast Shield → the review states the 7-Spark stack; 28 Block is what it leaves implicit. NEVER AGAIN → not stable; five of nine Spark-priced. 366 / 20 → 344 / 19; "never drafted" → "zero plays"; Wait For It... out of the zero column; Taste Test and Tinkering's 92 fights. Dodoco Tag → +2 damage, same Block. Comparators carry Debris, Dazed and Focus loss. Cook growth → per-card turns. Pick 2(b) and pick 4(c)'s Little Hexenzirkel withdrawn. Hygiene → brief sec.4 under pick 3, sec.6's defence choice to the main session, the act-3 measure into pick 1 (Balance), the `KLEEMOD-BOMB` item names the enum, tooltip path and test. Lint exceptions → Durin added. Gaps added: Balance stage and the owed plan; the instrument fix; the co-op doubling; suite 5's movement; brief secs.5.1 / 9 / 10 / 11; Ka-pow! as the seventh default-upgrade row; the Block-trim tension with the boss deaths; STATE.md's stale entry.

**Qualified.** "Reactions 2.08 not 1.70": 2.08 is all suite-4 fight kinds on the clean window (normal only 1.33); the paper now says which. "Suite 5 has moved": it moved again during this revision (84 rows at the check, 94 at 01:04; act-2 boss 2 of 5 lost, not 2 of 3); every suite-5 number is from 01:04 and labelled live. Brief sec.6: removing cut-card names stays hygiene; choosing her defences is handed to the main session.
