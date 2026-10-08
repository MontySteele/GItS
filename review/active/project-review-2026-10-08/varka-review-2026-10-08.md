# Varka kit review, 2026-10-08

Stage: Prototype, combo pass built (`docs/current/STATE.md` roster row). His 84 sheet rows (78 pool, 6 basic) are identical on `main` (5f9d0628) and `origin/klee-next` (063e1b40). Nothing here binds: measurement law starts at Balance. Paths are relative to `C:\Users\Monty\Documents\GitHub\GItS`. Telemetry: `tools/telemetry_report.py --character Varka --since 2026-10-05`, the base window `--character base5 --since 2026-10-05 --until 2026-10-05T16:50`, and `telemetry_report.load_fights(default_dirs())` filtered to `character == 'Varka'`; the counting scripts are beside this paper (`fc_vk_confirm.py`, `fc_vk_confirm2.py`).

**Summary.** On the r6 and solo-check builds (136 solo fights, 7 runs) Varka's damage a turn is 1.05 / 1.05 / 0.90 of the base five's by act, his HP lost 0.57 / 0.34 / 0.49 of theirs, his Block a turn 1.9 / 2.6 / 1.4 times theirs. On the base-five seeds he won 1 of 5 where the base five won 0, matched the base floor on two, and fell well short on two; both short runs were Cryo starts, and all three Cryo starts died. The loop [USER] called fun (apply, Swirl, cash Four Winds' Ascension) is what every seat plays; Ascension made 10 to 23% of his damage. Not seen solo: a mid-fight switch bought with Switch cards, and Pyro or Cryo as decks. Three Cryo starts and one Pyro start played none of the five Pyro/Cryo payoffs; 28 of 78 pool cards, all Uncommon or Rare, were never played. Text is lint-clean but has 12 bare element words on 10 faces, three Oath phrasings and four rule-14 slips. Three picks; the rest is hygiene.

## 1. Power level and balance

### 1a. Results, newest first

| Round (record) | Build | Result | Base on the same seeds |
|---|---|---|---|
| Solo check 10-07 (`review/records/varka-solo-check-2026-10-07.md`) | klee-next 0.2.4516+next | 1 win of 5 at A0; deaths f48 Test Subject, f17 The Kin, f46 Mecha Knight elite, f33 Kaiser Crab | 0 of 5 |
| r6 10-05 (`varka-r6-round-2026-10-05.md`) | 0.2.4456 | lane 1 lost the act-2 Knowledge Demon; lane 2 lost the Queen | Ironclad control died at f48 again |
| Combo 10-05 (`varka-combo-round-2026-10-05.md`) | 0.2.4423 | lane 3 lost the Knowledge Demon; lane 4 cleared act 2 | acts 1-2 only |

The baseline record (`review/records/base-five-baseline-2026-10-05.md`, "Next") says a kit that ends in act 3, mostly at the final boss, "is playing at a base character's level". Seed by seed: Varka won on DJCA (Hydro start) where the base character died at f48; matched the base floor on 30KM (f48) and YEWA (f46); fell short on CYHZ (f17 against f48) and R41 (f33 against the Regent's f48, baseline line 13). Two matches, one beat, two misses. Both misses were Cryo starts (Kaeya: Hidden Strength).

### 1b. Telemetry, solo, 136 fights

The window is the two r6 runs (10-05) and the five solo-check runs (10-07). It leaves out the combo round itself (10-04 22:47, two runs, 30 fights, build 0.2.4423); "since the combo pass" would be 9 runs and 166 fights.

| Act | n | Varka dmg/turn | base | ratio | Varka HP lost % | base | ratio | Varka Block/turn | base | ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 52 | 19.5 | 18.5 | 1.05 | 5.0 | 8.8 | 0.57 | 4.2 | 2.2 | 1.9 |
| 2 | 31 | 34.7 | 33.0 | 1.05 | 4.3 | 12.6 | 0.34 | 7.5 | 2.9 | 2.6 |
| 3 | 22 | 43.4 | 48.0 | 0.90 | 6.2 | 12.7 | 0.49 | 10.5 | 7.5 | 1.4 |

Normal fights, medians, from the two report runs above; the bar is within 15% and prints OUTSIDE in every act, on the survival side. Bosses still hurt: median HP lost 39% / 55% / 80% of max at the act bosses (n = 7 / 5 / 2). Three of the four 10-07 deaths were at bosses; the fourth was the Mecha Knight elite.

Caveats. Death fights before 10-07 were not logged: both r6 boss losses are absent (C83Y ends at Chompers f31, Z2M at Scrolls f45, every row "won"), and the base window logs 0 losses though all five base runs died (`lost` column). The boss medians are from survived fights plus 10-07. Seven runs, one seed each, Sonnet seats; the 10-07 window alone gives HP ratios 0.61 / 0.43 / 0.69 (solo-check record), the same reading.

Damage by source (`damage_by_source`): his own cards 57 / 65 / 66% by act, Ascension 23 / 12 / 10%, reactions 13 / 13 / 11%; he makes 1.00 reactions a turn alone against Klee's 0.05. Per card: Ascension 20.9 / 24.4 / 25.9 a play; Thundering Verdict 39 to 59 a play in acts 2-3 across upgrade states, one upgraded act-3 fight at 104 (3 plays, 313 damage, DJCA, the win); Kindled Edge+ 16 to 23.

### 1c. Card by card against the base game

Base pools `game_ref/{ironclad,silent,defect,necrobinder,regent}.json`. Base medians: 1-cost Common plain Attack 8 (n = 26); 1-cost Common Block Skill 6 (n = 17); 2-cost Uncommon plain Attack 13 (n = 10). Plays from the 136 fights.

| Varka card | Base twin | Reading |
|---|---|---|
| Windbound Execution (basic, 0): 4 [6] Anemo | Slice (Silent C, 0: 6 [9]); Neutralize (basic, 0: 3 [4], Weak) | Right for a basic. In 113 of 136 fights; the Swirl trigger. |
| Charged Lunge (C, 1): 6 [9] Electro, draw 1 | Pommel Strike (C, 1: 9 [10], draw 1) | 3 under; the aura is the difference. Most-played pool card, 78. |
| Ember Cleave (C, 1): 9 [12] Pyro, Exhaust a card | True Grit prices Exhaust-as-cost about +2 (combo paper sec.3) | 18 plays in 4 of 5 solo-check runs; "Pyro Exhaust was passed" (combo record) is stale. |
| Noelle: Steadfast Maid (U, 1, Geo Knight): 9 [12] Block, draw 1 | Leap (Defect C, 1: 9 [12]); Shrug It Off (C, 1: 8 [11], draw 1) | A Common's numbers plus a draw at Uncommon. 26 plays. Watch at Balance. |
| Favonius Cut (U, 2): 14 [19] Anemo | Uppercut (U, 2: 13, Weak, Vulnerable) | At rate, no rider. 0 plays. |
| Thundering Verdict (R, X): 6 [8] plus Electro Oath to ALL, X times | Hyperbeam (Defect R, 2: 24 to ALL, lose Focus) | At Oath 10, X = 2: 32 to ALL for 2, above Hyperbeam. Price at Balance. |
| Four Winds' Ascension (basic, 2 [1], Retain, created each combat): 10 Anemo, then 3 per Oath of the current element | Bludgeon (U, 3: 32 [42]) | The upgrade cuts the cost to 1 and leaves the numbers (`docs/prototype-surface.yaml:2959-2963`). Bludgeon for 2 at Oath 7, Retained, 1 cost upgraded. Carried every run. [USER]'s card. |
| Cycle of Seasons (U, 1 Power): 7 [10] to a random enemy on each element change | none | Raised from 4 [6] in the r6 record (dbb95c0d, an ancestor of klee-next). 8 of its 9 solo plays were at 7 (30KM 4, R41 3, YEWA 1); only Z2M's one was at 4. 18 rows in the 10-06 co-op bot run. No NEVER AGAIN at 7 yet. |
| Crosscurrent (U, 1): Swirl an aura, it pays twice | none | NEVER AGAIN on lane 3 both acts (combo record). 1 play. |
| Short Circuit (U, 0): discard 2, draw 2 [3], 1 Energy, Electro | Calculated Gamble (Silent U, 0, Exhaust: discard your hand, draw that many) | 0 plays. [USER]'s friend "never saw any of the Electro payoffs for discarding cards" (`review/active/coop-notes-2026-10-02.md:8`). |

Never played (28 of 78): Absolute Zero, Blazing Charge, Boreas Unbound, Chain Lightning, Charge of the Knights, Converging Winds, Dawn Wind's March, Deep Freeze, Eye of the Storm, Favonius Cut, Grand Master's Order, Grand Master's Verdict, Knights' Roll Call, Pyre Oath, Rally to the Banner, Retaliating Tide, Short Circuit, Storm Battery, Stormward Stance, Sworn Brotherhood, The Order Answers, Tidal Bulwark, Twin Gales, Unwavering Banner, Violet Storm, Weathervane, Wildfire Oath, Wolfpack. 14 Uncommon, 14 Rare, no Common. Telemetry logs plays, not offers. The one round with offer counts is r6 (record lines 32-39): Deep Freeze not offered in three rounds; Stoke the Flames, Ember Cleave, Icebreaker offered 2, taken 0; Absolute Zero 1 and 0; Unwavering Banner 3 and 0. The solo-check transcripts could give the same table.

## 2. Archetype structure and what play rewards

**The promise** (`review/active/varka-paper-kit-2026-09-28.md` sec.2): one element at a time, from the Knights he has, charged by applying and Swirling. **Archetypes** (sec.7): Focus, Switch, Gale. **Intended weakness** (sec.8): nothing to Swirl at first; no Ascension before the first Oath.

What seats play: Focus on one element, Gale on whatever auras are up, Ascension as the cash-in. Both r6 lanes "opened on their starter Knight's element and never left it". The solo check was less uniform (Knight-row plays by sheet `element`, per run): three of five stayed on the starter's element (30KM Cryo 31 of 45; YEWA Pyro 41 of 93; CYHZ Cryo 12 of 23); R41 (Cryo start) spread Pyro 15, Cryo 12, Electro 12, Hydro 5, never cashed an Ascension above 18, and died at the act-2 boss; DJCA (Hydro start) played Electro 24 against Hydro 13 and won on Thundering Verdict. The only win changed element mid-run, by drafting, not by Switch cards.

- **Not seen solo:** the Switch cards. Boreas Unbound, Weathervane, Rally to the Banner, Unwavering Banner 0 plays; Change of Guard 13, Shifting Gale 13, Windborne Resolve 6. The decision seats name is "which element is current when Ascension lands" (r6; combo record). In co-op Switch was drafted: Boreas Unbound 10 (09-30 run) and 12 (10-04), Rally to the Banner 4 (09-30), Change of Guard 4 (10-04), from `cards_played` on `seats == 2` rows.
- **The Knights are not displaced.** Since the open Oath (2026-09-30) the shared companions are played (Kaeya — Frostgnaw 54, Mika 25, Jean — Gale Blade 20, Itto 14, Gorou 14; the last two are Inazuma rows, `ProtoMi*`), but his own 17 Knights (`personal_pool: varka`, `VarkaRules.cs:55`) were played 320 times solo against 234 for all other companions, and 470 against 265 in 89 deduplicated co-op fights. What idles is the payoff shelf: of six cards whose text names Knights, five had 0 plays (Grand Master's Order U, Knights' Roll Call U, Unwavering Banner U, Charge of the Knights R, The Order Answers R); Knightly Strike (C) had 16. Roll Call+ was "the best card on lane 3 in both acts" one round earlier (combo record): rarity and offers, not a dead deck. Pick 3.
- **Pyro and Cryo.** The solo check ran the Pyro/Cryo-start round by accident: Kaeya (Cryo) on CYHZ, R41, 30KM; Amber (Pyro) on YEWA; Barbara (Hydro) on DJCA. Hydro won; Pyro died at the f46 elite where the Necrobinder died; the Cryo starts died at the act-1, act-2 and act-3 bosses. Cryo Knights were played (Heart of the Abyss 42) and 30KM built Icebreaker (10) with Kindled Edge (27) for Melt, yet no run played Deep Freeze, Absolute Zero, Blazing Charge, Pyre Oath or Wildfire Oath, all Uncommon or Rare. The on-ramp was present four times and the payoffs did not arrive: offers and rarity, more than the on-ramp. The Cryo start is the weak start on this evidence. Pick 2.
- **Block.** [USER] (10-04): "Varka still seems to have too much Block, but the basic loop is fun." His pool holds 17 Block cards of 78 against 11 or 12 of 80 in the base pools (combo paper sec.2). By plays the Block is Defend 114, Barbara: Gleeful Songs 35, Kaeya: Hidden Strength 34, Crosswind 27, Jean — Wind Companion 27, Noelle 26, Glorious Season 24, Precise Shot 24. The Rare Oath-to-Block engines the combo paper named (Oathbound Aegis 3 plays, Dawn Wind's March 0) are not the source. Pick 1.

## 3. Fun

[USER]: 10-02 Varka "seemed very fun, and had a trivial time generating massive amounts of block and card draw" (`coop-notes-2026-10-02.md:7-9`); 10-04 "the basic loop is fun! I want to come up with something for Pyro and Cryo" (combo paper header). His friend piloted Varka in at least the 10-02 and 10-04 runs (`coop-notes-2026-10-02.md:8`; `varka-combo-pass-2026-10-04.md:3-4`); the human co-op starts were Pyro, Hydro and Electro, never Cryo.

Seats liked: Ascension, "the happiest draw in all five Varka seats" (r6); "Swirl spread was the best turn of the round" (Gale Sweep+, r6); hold-or-fire on the retained Ascension (starter record); Knights' Roll Call+ (combo). Seats did not: Cycle of Seasons twice at 4 (unread at 7); Crosscurrent twice; "three Strikes and no Knight in hand" (starter record); act-3 HP with no healing; readability (Oath invisible at source, fixed by #867; Ascension read as joining the deck, r6 item 4).

## 4. Solo versus co-op

The standard (`docs/current/operations/stage-gate.md:80-86`, 2026-10-06): judged solo against the base five; [USER]'s co-op runs "read fun and feel, not strength"; the co-op check is a paired seat round. Varka meets the solo half. The co-op strength question is already an open pick in the reply of 2026-10-07 (`review/records/coop-reaction-round-2026-10-07.md`, last paragraph), so it is not re-asked here.

Co-op facts (that record; Klee + Varka, 28 fights, 115 turns): the team made 1.81 reactions a turn, Varka 1.30 of them, against his 1.00 alone; the free x1.5 / x1.75 was "about 1.5 damage a turn to the team: not a driver". The structural asymmetry: his intended weakness, "nothing to Swirl" (sec.8), is solo-only; in co-op the partner's auras are Swirl fuel from turn one (sec.7). The numbers do not yet show it as strength. Human co-op act-3 monster fights (12 rows, 09-30 to 10-04, Varka mostly the friend's) lost a median 0% HP, but the standard excludes those runs. The one Sonnet co-op run (10-06, 30KM; 4 unique act-3 monster fights after removing duplicate lane rows) lost 0, 25, 27 and 2 HP of 87: median 13.5, about 15%, above his 6.2% solo. One run a side; the paired round with several seeds the 10-07 record asks for is the right next read.

His open co-op defects: BACKLOG line 30 (a universal or other-kit card switches him silently), line 31 (switch hover and left-element icon untried), line 37 (Weathervane's grid untried through the bridge and in co-op).

## 5. Card text and tooltips

The five text lints pass on main. A regex pass over his 84 rows (`fc_vk_confirm2.py`; `docs/current/text-conventions.md` rules 6, 13, 14) finds:

1. **12 bare element words on 10 faces.** Rule 6 golds elements; Wildfire Oath prints "[gold]Pyro[/gold] [gold]Oath[/gold]" but these print bare: Stormward Stance, Blazing Charge, Tidal Bulwark, Glacial Edict, Retaliating Tide, Absolute Zero, Thundering Verdict, Pyre Oath (one each); Eula: Icetide Vortex and Stoke the Flames (two each).
2. **Three phrasings for one count:** "Oath of your current element" on 8 rows; "your current element's Oath" (Grand Master's Verdict); "for each Oath, as your current element" (Northwind Avatar). Use the eight-row form.
3. **Four rule-14 slips the lint passes:** Pathfinder's Mark "(a random one of the four if you have none)" (`prototype-surface.yaml:3375`); Weathervane "you have Oath in; it becomes" (:3633); the Knight tip "(except Geo)" (`klee-mod/KleeCode/Cards/Prototype/ArmKeywordTips.cs:706`, quoted again in `text-conventions.md:124`); the Oath tip "Element cards read their own; others, the current." (:653). `lint_text_conventions.py:219` has the parenthesis rule and lines 714-718 apply it to these rows, so the clean report is unexplained.
4. **The Oath tip is too terse:** a seat with it still asked whether Ascension's Oath hit credits (r6 item 3; BACKLOG line 35). Ceiling 135 rendered characters.
5. **Three starters omit the target** ("Apply [gold]Hydro[/gold] to an enemy." on 12 rows): Barbara: Glorious Season, Lisa: Induced Aftershock, Kaeya: Hidden Strength. Text only; the effect already targets an enemy; flagged because they are starters.
6. Cross-character: the Knight line and golding are done (17 rows); "Deal N <Element> damage" uniform; "ALL enemies" on all 7. `VarkaOath.cs:1122` still says Ascension's hit is "3 [4]"; the sheet upgrades cost, not damage.

## Hygiene Claude can just do

- Text: gold the 12 bare element words; one "<Element> Oath" spelling in `text-conventions.md`; "Oath of your current element" on Grand Master's Verdict and Northwind Avatar; drop the parentheses from Pathfinder's Mark and the Knight tip (and `text-conventions.md:124`) and the semicolons from Weathervane and the Oath tip, then find out why the parenthesis lint passed them; "to an enemy" on the three starters (text only; the commit says they are starters).
- Oath tip under 135 characters saying Ascension's own hit credits none; the Fang's hover says Ascension is created each combat; close BACKLOG line 35 and r6 item 4; fix the `VarkaOath.cs:1122` comment.
- Telemetry: log offers beside plays; log the death fight (both r6 boss losses and all five base deaths are missing); stop duplicating bot co-op rows across lanes (124 raw against 89 fights). Until then, tabulate offers from the solo-check transcripts as the r6 record did.
- BACKLOG: lines 31, 36, 37 point at "the next Varka seat round" or "the expansion's first seat round", and r6, the expansion and the solo check have run since. File the combo record's screen items 4-6 (Artifact not named when it eats a reaction debuff; Bottled Gale silent on an empty board; Diluc 9 against 6). Line 33 names Kaeya — Frostgnaw, the shared Mondstadt card (`ProtoMcKaeyaFrostgnaw.cs`), not Varka's Heart of the Abyss; trace both printed-number mismatches before Balance.
- The main session's card desk, not a cut list: Favonius Cut (0 plays), Crosscurrent (1), Short Circuit (0) have the least play evidence; show texts and offer counts before any rider, rarity move or cut.
- STATE "Next": the solo check already ran three Cryo starts and one Pyro start; the next record lists each seat's starter Knight.

## Picks

1. **How sturdy Varka is allowed to be.** Block a turn 1.4 to 2.6 times the base five's; HP lost 34 to 57% of theirs; 17 Block cards of 78. The Block comes from Defend and the Block Knights, not the Rare engines.
   - (a) **Default: leave it until a Balance suite reads him on several seeds a start.** The combo record said leave Block alone; one run a seed; bosses still take 39 to 80% of his HP; death fights are under-logged.
   - (b) Trim the Hydro Block numbers now (Gleeful Songs, Rippling Guard, Whisper of Water, Tidal Bulwark); starters untouched.
2. **Pyro and Cryo, and the Cryo start.** Knights played, payoffs never; all three Cryo starts died, two short of the base floor.
   - (a) **Default: run the planned Pyro/Cryo round with offers tabulated. Offered and passed: fix the cards. Not offered: move one payoff per element to Common** (the combo record's item 5 for Cryo) before any number moves. Read the Cryo starts separately.
   - (b) Add the on-ramp Common the r6 record's item 2 proposes (a Common that makes the element current) instead of moving a payoff.
   - (c) Accept Pyro and Cryo as starter-plus-Knight flavours (Melt, Superconduct) and stop adding payoffs.
   - A change to Kaeya: Hidden Strength's numbers would be a separate starter pick; not proposed here.
3. **The Knight-payoff shelf.** Knights are played (320 against 234 companion plays solo); five of the six Knight-text cards had 0 plays, all Uncommon or Rare.
   - (a) **Default: leave it and read again at Balance with offers logged.** Roll Call+ was a seat's best card one round ago.
   - (b) Widen "Knight" to every companion he drafts (rule change: tag, tip, `text-conventions.md:124`, `VarkaRules.IsKnight`), so the payoffs count Frostgnaw, Mika, Itto, Gorou. "Mondstadt" would miss the last two.
   - (c) Move Knights' Roll Call to Common so the shelf is seen; keep the Rares.

## Fact-check log

Each point below was confirmed against the named file or recounted from `load_fights` before the change.

- Ascension: upgrade is cost 2 to 1, damage 10 plus 3 per Oath (`prototype-surface.yaml:2959-2963`; `ProtoVkFourWindsAscension.cs:60-61, 84`). Row fixed; stale `VarkaOath.cs:1122` added as hygiene.
- "Starter element dominates every run": false for R41 and DJCA (the win: Electro 24 against Hydro 13). Rewritten with per-run counts; "7 solo-check runs" is 5 plus two r6 runs. The 762-to-323 split was dropped: it compared Knight rows against rows with no `element` field (Charged Lunge, Kindled Edge, Ember Cleave, Verdict, Icebreaker among them).
- Knights displaced: false. Recount 320 against 234 solo; 470 against 265 on 89 deduplicated co-op fights (checker: 471/267 on 90; my dedup key differs by one fight, same reading). Pick 3 rewritten; Itto and Gorou marked Inazuma.
- Cycle of Seasons: dbb95c0d is an ancestor of klee-next (`git merge-base --is-ancestor`; count 4464 under build 4516), so 8 of 9 solo plays were at 7. Fixed in 1c and sec.3.
- Never-played: 14 U, 14 R, no Common. Knight-text cards: six, five at 0, Knightly Strike 16. Fixed; pick 3(c) rewritten.
- Co-op Switch plays (Rally 4, Change of Guard 4, Boreas 10 and 12) and co-op act-3 HP (12 human rows median 0%; Sonnet run 0/25/27/2 of 87, median 13.5) recounted. Stage-gate excludes [USER]'s co-op runs from strength; the friend piloted (`coop-notes-2026-10-02.md:8`, `varka-combo-pass-2026-10-04.md:3-4`). Sec.3-4 rewritten; pick 4 removed as already open in the 10-07 reply with no new admissible fact.
- "Is the payoff" is not in the repo; replaced with the friend's words at `coop-notes-2026-10-02.md:8`.
- Deaths: four, three at bosses plus the Mecha Knight elite; r6 boss deaths absent from telemetry. Fixed; logging caveat added.
- Window: 136 fights are r6 plus solo check; the combo round (30 fights) is outside it. Stated.
- Base floors: two matches, one beat, two misses, both Cryo. Fixed; the Cryo-start reading added to 1a, sec.2 and pick 2.
- Base Block in the same window 2.2 / 2.9 / 7.5, ratio 1.9 / 2.6 / 1.4, not "double". Table and pick 1 fixed.
- Verdict 39 to 59 a play with 104 marked as one fight; Kindled Edge+ 16 to 23. Fixed.
- Pick 2(a) source is the combo record's item 5; the r6 item 2 (on-ramp Common) added as option (b).
- Starters omitting the target: three (Kaeya: Hidden Strength added). Counts: 10 faces / 12 words, four rule-14 slips.
- Compile Driver draws per orb (`defect.json`: `CardPileCmd.Draw`, Damage 7 flat), dropped. No Concentrate in `silent.json`; Short Circuit's twin is now Calculated Gamble (U, 0, Exhaust, `CardCmd.DiscardAndDraw`).
- "No reason to exist" softened; seat verdicts are not cut lists. Pick 1(b) (Oathbound Aegis 3 plays, Dawn Wind's March 0) removed for the played Block sources.
- Length: 4,119 words to about 3,200 before this log, of which the three tables and the never-played list are about a third; the out-of-repo memory citation removed. Gaps added: Cryo start, Ascension's 1-cost upgrade, telemetry under-logging and lane duplication, stale BACKLOG lines and unfiled screen items, the r6 offer table, the Knight tip's second home, which Frostgnaw line 33 names.

Rejected or qualified: no checker claim was wrong on substance. Two counts differ by one on recount (co-op 470/265 on 89 fights); the paper uses the recount. The checker's guess that the lint "does not read these rows" is not borne out: `lint_text_conventions.py:714-718` applies the parenthesis rule to prototype rows and tips, so why the report is clean stays an open hygiene item.
