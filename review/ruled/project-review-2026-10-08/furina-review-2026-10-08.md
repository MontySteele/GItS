# Furina kit review (2026-10-08)

Read against main at 5f9d0628, revised after a fact-check (log at the end). Every number is from a named file or a computation whose method is stated; sim numbers are instrument readings, not sheet values. Telemetry scripts: `scratchpad/fanout/furina_tel.py`, `fc_furina/t3-t8.py`, `fc_furina_rev/v1.py`.

**Summary.** The brief's premise is out of date: Furina is not frozen. The v1 Stage was frozen on 2026-10-04 (tag `furina-stage-frozen-2026-10-04`), the v2 Stage was played once by [USER] ("Honestly, not very engaging") and discarded, and the Salon's Tab replaced it on 2026-10-05 as the release kit (`STATE.md:47,224`). She is at Prototype with 34 reward cards, deployed, read by two Sonnet seat rounds (four runs, four seeds, A0), and waiting on [USER]'s first Tab run, which the ruled pool-40 paper already put next. The core holds: Drain-for-power beats Strike from fight one, hits print Fanfare, a Bravura finale closes fights, and one of two seats won a full run where the base-five Sonnet baseline went 0 of 5. Three things do not hold yet. Act 3 is where she bleeds: both seats left the Soul Nexus elite at 10 to 12 HP where the Ironclad control lost 7, and the HP she carries between fights is HP minus hits whatever she Repays, because the curtain call already returns every drained HP. The Pneuma (Repay) archetype has never been drafted as a plan; the rules cap it (Repay never returns more than Drain lent), but the sim says Drain outruns Repay by 3 to 5 HP a fight, so Repay cards have room, and the record's own cause is legibility. Drain is a reflex: in round 1's four acts no seat declined one for any reason but the line, and the sim's pilot takes 99 to 100%. The text is clean against the lint, but the Guest Star faces say only "Summon X." outside combat, and several documents still describe the retired Stage. Reaching 78 is 44 cards, four of them written. The picks are Pneuma's shape, the act-3 lever, co-op, the Ancients and one LAW wording.

## 1. Power and balance

**Seat results (the only Tab-era play).** Four Sonnet runs across two rounds, each on its own seed; per-act seats with a state handoff; A0.

| Round, build, pool | Lane | Act 1 | Act 2 | Act 3 |
|---|---|---|---|---|
| 1, 0.2.4423, 29 cards | TNB6 | Vantom*, 78/85 | Kaiser Crab, 27/85 | not in scope |
| 1 | VD4Y | Ceremonial Beast, 43/78 | lost to Kaiser Crab, floor 33 | |
| 2, 0.2.4437, 34 cards | JF39 | Vantom, 50/90 | Kaiser Crab, 44/90 | died floor 46, entered at 13/84 after the Soul Nexus elite |
| 2 | WDET | Vantom, 59/78 | The Insatiable, 57/78 | **won**, Aeonglass turn 8 |
| 2, Ironclad control | PPW4 | Vantom, 58/80 | The Insatiable, 45/80 | **won**, the Queen turn 5 |

Sources: `review/records/furina-tab-round-2026-10-05.md:8-11`, `furina-pool40-round-2026-10-05.md:8-12`. *The round-1 record says Ceremonial Beast for TNB6; telemetry has TNB6's floor-17 boss as `VANTOM_BOSS` and VD4Y's as `CEREMONIAL_BEAST_BOSS`. The base-five Sonnet baseline at A0 is 0 of 5, all dead in act 3 (`base-five-baseline-2026-10-05.md`). Two caveats: the control ran before #924, so its Ironclad pool lacked epochs 3 to 7 (`base-five-baseline-2026-10-05.md:3`), and 1-of-2 against 0-of-5 crosses seeds, builds and seat-page versions. Round 2's verdict, "Furina's pool is at a base character's level", is fair on two full runs.

**Telemetry.** `tools/telemetry_report.py` `load_fights(default_dirs())`, won fights only (a lost fight writes no row). Round 1 ran a build where Universal Revelry still counted hits, so only round 2 (JF39, WDET; 42 fights) shares a build with the control. The control's run id also carries 30 act-1 rows from the three effort-test runs on the same seed (`sonnet-effort-test-2026-10-05.md:3`); the column below keeps only the control run proper (`run_instance` 20261005-003125, 21 fights).

| Act | Furina round 2: fights; HP lost (% of max); Block per turn; damage per turn | Control: the same |
|---|---|---|
| 1 | 16; 11.9 (14.1%); 4.3; 26.6 | 8; 13.8 (17.2%); 3.8; 18.2 |
| 2 | 15; 21.0 (24.9%); 5.8; 42.1 | 7; 16.4 (20.5%); 8.8; 29.9 |
| 3 | 11; 26.1 (32.1%); 12.5; 54.2 | 6; 16.7 (20.8%); 10.6; 56.0 |

Read: she out-damages the control by 46% in act 1 and 41% in act 2 and matches it in act 3. Block is a little above the control's in act 1 and two-thirds of it in act 2. HP loss is below the control's in act 1 and above it from act 2 on; the four-run pool reads the same way. The two Soul Nexus fights: 67 to 10 (JF39) and 73 to 12 (WDET); the control 74 to 67. Act 3 rests on 11 Furina fights from two runs and 6 control fights from one. One caveat: `hp_lost` is `hp_start` minus the last in-fight reading (`PlayTelemetry.cs:985-997`), and the curtain call returns drained HP in `AfterCombatEnd` (`FurinaStageHooks.cs:128-137`), after it, so the figure includes HP still drained at the end: 3 to 5 HP a fight in the sim (`furina_curtain.txt`, `unrepaid_per_fight` 5.1 draft, 3.2 balanced). JF39 shows the size: 67 to 10 at the Soul Nexus, then 13 entering floor 46, so the curtain call returned 3 and the other 54 were hits.

**Sim (`tier0/harness/furina_tide_probe.py`, 400 runs, re-run 2026-10-08; "not a balance number").** Starter wins 4.53 act-1 fights and 79% of first elites against the reference Ironclad starter's 3.59 and 33%. The drafted deck clears the act-1 route 62% with Drain, 17.5% with Drain off, 35% with the curtain call off. Drain is taken 99.3 to 100% of the time offered. The drafted deck spends 38% of its Fanfare, under the proposal's 40% bar (`furina-research-proposal-2026-10-05.md:470`); the balanced deck 70%. The boss gauntlet gives every hand-built deck 0 to 9% against the act-2 boss while seats beat it in three of four runs, and the draft probe rates Standing Ovation 0%, Let the People Rejoice 0% and Critics' Darling 3% while seats won with all three: those two probes cannot price spend-all cards or Powers (`furina-pool-40-2026-10-05.md:186-193`). Treat them as unread for this kit.

**Card comparisons against the base game.** Base values from `game_ref/*.json` `vars`; a 1-cost base Common attack averages 6.2 to 9.2 by class (Ironclad 6.8, Silent 6.2, Defect 6.9, Necrobinder 8.6, Regent 9.2), the 0-cost ones 6 (Anger, Slice), 3 (Defect) and 8 (Regent). Plays count both forms of a card over the four runs; damage shares are of all 9,842 damage dealt, of which 940 (9.6%) is uncredited.

| Furina card | Base yardstick | Read |
|---|---|---|
| Soloist's Solicitation (C, 0): Drain 2, deal 8 [11] | Anger 6 [8], Slice 6 [9]; Hemokinesis (U, 1): lose 2 HP, 15 | Top of the 0-cost band for a loaned 2 HP. Sim pick 92%; 56 plays, the most played card; the auto-pick at Common. |
| Mademoiselle Crabaletta (C, 2): Drain 5, deal 24 [30] | Cinder 18 [24] Exhaust; Predator 15 [20]; Reap 27 for 3 | Above every base 2-cost Common; 9.8% of damage, 44 plays. The line gates it near the floor. |
| Curtain Rise (starter): 7 / Drain 3: 12 | Strike 6 | Deliberate act-1 overshoot (K1). 55 plays. Stays. |
| Chevalmarin (C, 1): 4 Hydro ALL / Drain 3: 8; Usher (C, 1): 7 Block / Drain 3: 13 | Thunderclap 4 ALL; Shrug It Off 8 + draw; Blood Wall (2): lose 2 HP, 16 | Fair; 6 and 36 plays. |
| Salon's Tab (U, 1): draw 2 [3] / Drain 4: also 2 Energy next turn | Bloodletting (U, 0): lose 3 HP, 2 Energy; Offering (R, 0) | Between the two; cost 1 since the 0-cost infinite (fa4b8315). 29 plays. |
| Grand Deluge (U, 2): Drain 6, 16 Hydro ALL [22] | Howl From Beyond 18 ALL for 3, Exhaust; Echoing Slash 10 ALL for 1 | Strong; 20 plays (17 upgraded), 6.1% of damage. The +6 upgrade is large. |
| Bravura (U, 1): spend all, 6 + 2 per point [3] | Body Slam (1 per Block) | **27.9% of all damage, 30.8% of credited** (2,744); 48 plays, 20 upgraded. Hits of 114 to 131 after the Revelry fix. The engine card. |
| Let the People Rejoice (R, 2 [1]): 2 ALL per point | Hyperbeam 24 ALL; Grand Finale 60 ALL | Killed both Kaiser Crab arms in one turn; 12 plays, 9.1% of damage. Fine as a Rare. |
| Standing Ovation (C, 1): spend all, that much to ALL [Retain] | none at Common | 2.5% of damage, 9 plays; Bravura dominates it. Closed the winning run off Bis!. |
| Rising Applause (starter): 5 Block, spend all as damage | Defend 5 | "Never again" in two acts (round 1); 26 plays. Stays. |

Never played in four runs: Fountain of Lucine, Guest Star: Lyney, A Five-Century Act (0% in the sim too), Tidal Flourish, Guest Star: Charlotte (the "Charlotte — Snappy Silhouette" plays are a Klee-pool companion, `prototype-surface.yaml:2322`). Barely played: Endless Waltz 1, Sigewinne 1, Clorinde 1, Singer 2, Hold the Stage 4, Ousia Surge 5, Thunderous Applause 7. So 5 of 34 cards are unread by play and 7 barely read. The two Ancients appear in no record.

**Where the power sits.** The act-1 frontload is the design (proposal sec.5) and lands; both round-2 seats "called act 1 easy". Act 3 is the problem: "HP is the bottleneck in act 3", "Furina's only sustain is Salon Solitaire's Repay 2 a turn", lever "a Pneuma card that seats can read, not more Block", held until [USER]'s run (`furina-pool40-round-2026-10-05.md:30-33,57`). The rules qualify that lever. Repay returns only drained HP (`FurinaStage.cs:27`, rule 2) and the curtain call returns all of it when combat ends, so her HP after a won fight is entering HP minus hits, whatever she Repaid. Repay is an in-fight buffer (it keeps her alive and above the line while the fight runs), not sustain between fights. JF39's 54 HP of hits at the Soul Nexus is the number a Repay card cannot touch.

## 2. Archetype structure and the play it rewards

**Intent.** "Furina is the actress who spends herself on the show... strong while she gambles with her HP above the line, and she wins by turning the fight's ups and downs into a finale" (proposal lines 25-36). The turn's decision is two-part: how much HP to lend, and cash Fanfare now or bank it. Three archetypes (sec.4): Ousia (Drain for frontload, Drain readers), Pneuma (Drain a little, Repay a lot, Repay readers), the Crowd (bank Fanfare from every swing, hits included, and cash it).

**What the seats played.** Round 1: one deck in both lanes, Revelry plus take hits plus Bravura, with Revelry reading hits (21 of its 26 plays are from that build). Round 2, on the live text: "Drain with payoffs" (Critics' Darling 9 plays and Salon's Encore 16 in WDET, Wriothesley 5: "one Drain card... pops four hits") and a Fanfare bank cashed by Bravura or Rejoice. Revelry was played 5 times in JF39, which lost, and never in WDET, which won; so "Drain or Repay readers are the shape that works" rests on Darling and Encore in one winning run. "Repay never became a plan" in either round.

**Why Pneuma has not formed.** Two causes, and the evidence favours the first.
- *Legibility.* The record's cause: seats "could not tell the payoff of Fountain of Lucine, Pneuma Refrain or Endless Waltz from the page", guests went undrafted because the face said only "Summon Lyney", and its order is "once guest and Repay faces print in full, see whether seats draft Pneuma before any number moves" (`furina-pool40-round-2026-10-05.md:34,58`). The guest lines reached the seat page after round 2 (7b8e2ff7), so that test has not run. The sim, which reads rules and not faces, picks the pure-Repay readers readily: Clorinde 100%, Lyney 95%, Endless Waltz 52%, Sigewinne 29% (`furina_picks.txt`), against 1, 0, 1 and 1 seat plays. Seats did take the Repay bodies (Surging Waters 23 plays, Hymn 17, Pneuma Refrain 14): Repay as an effect is drafted; Repay as a plan is not.
- *The rules cap it.* Repay's ceiling in a fight is what Drain lent, the Drain cards lend 2 to 6, and Salon Solitaire repays 2 every end of turn (`FurinaStageLaw.cs:24`). The proposal knew it ("every Pneuma deck needs a few Drains"; Weakness: "needs some Drain to have anything to Restore", lines 141-148). But the cap does not bind at today's numbers: the sim's drafted deck drains 12.0 and repays 6.9 a fight, 5.1 unrepaid; the balanced deck 9.8, 6.7 and 3.2. A Repay card played after a Drain also resolves before the end-of-turn relic. Repay cards have room; the readers lack a visible payoff.

So: Pneuma's ceiling is structural, Pneuma's absence is not yet shown to be. The pure-Repay readers (Endless Waltz U, Sigewinne U, Clorinde R) and volume cards (Fountain, Refrain) are weak until a deck already Drains, and the proposal's payoff, "every repaid HP pays twice", is untested in play.

**Where the real decision is.** Round 1's clearest finding: "Banking Fanfare against your own HP was the decision, every fight" (lane 2 "ate 17 and 3 x 7 on purpose with Revelry and Lynette up, Fanfare 16 to 84, then a 176 Bravura"; holding 81 to 113 Fanfare for two turns at the Kaiser Crab also killed that run). Whether Drain is a decision (K3) reads no on round 1's four acts (`furina-tab-round-2026-10-05.md:31`; round 2 is silent) and in the sim; sec.14 already called a Drain "close to a well-priced cost, like Ironclad's HP cards", with the decision at the draft, at the line and at the killing turn, and the curtain call removed the killing-turn trade-off (sec.16). The live decision is Block-or-take-the-hit, which Fanfare-from-hits creates: on-theme, and the lever the Revelry fix had to blunt. The pattern rewarded today: Drain everything early, let hits fill the bank, finish with Bravura; Repay is a body-card effect. "The Singer gives it back" is not felt. The ruled position is "no change until your run" (pool-40 pick 3), and nothing here reopens it.

## 3. Fun

**Seats.** Round 1: "the core works, but the deck converges"; "Taking a hit or Blocking it is a real choice, and it shows on the enemy's intent"; the nothing-turn, "Bravura at 86 on a 19 HP enemy" (pre-fix). Round 2: "at a base character's level, and it now plays more than one way"; hits of "131 and 121 into bosses and elites, banked over several turns"; act 1 easy. Dead reads: Rising Applause "never again" twice, Wriothesley "never worth a slot" in round 1 (then in a winning deck in round 2), A Five-Century Act "no hint of what it does at 1 HP".

**[USER].** He has not played the Tab. His three Furina runs are Stage-era and differ: 2026-09-26 (v1, won A2): "the core concept is sound", "Aeonglass was a decent struggle", Fanfare "ran away" (memory `furina-first-solo-run-2026-09-26.md`); 2026-09-28 (v1): "extremely easy" until an act-3 elite killed him, "the block is so high that you just don't feel pressure in act 1" (memory `furina-stage-run-2026-09-28.md`); 2026-10-05 (v2): an act-1 slog, "plenty of block but no damage", "no way to scale" (`review/active/furina-design-layer-2026-10-05.md:5-12`). The Tab's curve (act-1 HP loss under the control's, act-3 over it) matches his second run, but the act-1 ease is now damage, not Block (26.6 a turn against 18.2; Block 4.3 against 3.8), which is the job he asked for. Whether act 3 reads as a wall or as the finale is the thing only his run answers.

## 4. Solo and co-op

**Facts.** The Tab has no co-op cards ("No co-op tier: the v2 Stage's five went with it", `FurinaStageRoster.cs:55-58`) and no co-op round; Kokomi has five. All 121 Furina co-op telemetry rows are Stage-era. Her reaction rate is measured: `reactions_by_turn` is on all 78 Tab rows, 9 reactions in 253 turns (0.036 per turn), against Klee solo 0.23, Kokomi 0.30, Varka solo 2.1 in the same window; `damage_by_source` credits (Swirl) 13 and (Shatter) 12. (`reactions_by_type` is empty on every Furina row; it landed in #945 after her last run.) The standard (`stage-gate.md:80-88`): judged solo against the base five; co-op checked by a paired round on shared seeds against Ironclad + Silent; not "dependent on reactions in a way that makes co-op exponentially easier."

**What the rules predict (untested).**
- Drain, Repay, the line and Fanfare are hers alone; the line is per-player.
- Fanfare from hits: if attacks split across two players she is hit less and the bank fills slower; unchecked against how StS2 multiplayer targets attacks and scales HP. The Stage-era complaint was the reverse ("Klee took every attack-everyone hit... while Furina sat at 74 to 78", `coop-seat-round-2026-09-27.md`); the Tab wants the hits.
- Guests are pets enemies cannot target (7b8e2ff7). Four of seven carry an element: Wriothesley Cryo, Lynette Anemo (her Act needs "an enemy with an aura"), Clorinde Electro, Lyney Pyro; Charlotte and Sigewinne Repay, Chevreuse deals plain damage (`FurinaStageBadges.cs:46-85`). No guest deals Hydro, so a guest hit on a partner's Pyro aura makes Melt, Overload or Swirl, not Vaporize. Her own Hydro is on 4 of 34 cards (Chevalmarin, Tidal Flourish's Spend mode, Quick Flourish, Grand Deluge). A Klee + Furina pair gets Vaporize from Klee's Pyro onto those four, plus the guests' off-element reactions: the "co-op easier" direction the standard tolerates, and she is not weak solo.
- `LAW.md:39-43` allows guests off-element access that "pays for it with a seat and Fanfare". Tab guests pay a seat and 1 Energy; none Spends. The intent holds, the wording does not (Pick 5).

**To check near 78:** one paired round (Klee + Furina against Ironclad + Silent, shared seeds), reading Fanfare per turn in co-op against solo (`meters_by_turn` is null on her rows, so the gauge comes first) and whether the guests are the pair's main reaction source.

## 5. Card text, tooltips and conventions

Lint: `tools/lint_text_conventions.py` prints no Furina line (`scratchpad/fanout/lint_text.txt`). Rendered face lengths: the longest are Let the People Rejoice 92 and Standing Ovation 90 with their in-combat "(Deals N damage)" line, Bravura 85, Tidal Flourish 82; all under the 120 ceiling. Drain's two forms match `text-conventions.md:121` exactly. Element words and gems follow the 2026-10-02 rule; Tidal Flourish's Hydro gem is correct under it (the gem is "the first aura element its face declares", `text-conventions.md:118`; its Spend mode declares Hydro), though a player may read the gem as both modes.

1. **Guest Star faces say only "Summon X." out of combat** (`Cards/Prototype/Generated/ProtoFsGuestStar*.cs`); in combat they add the Bow line, "(X will act again)" or "(Y will act and leave)" (`FurinaStageBowPreview.cs:41-53`). The Line and Act are a hover tip from `StagePerformerBadge.ActText` (`FurinaStageBadges.cs:46-85`); 7b8e2ff7 printed them on the **seat page**, not the card, so the record's "Guest Stars went undrafted... the face says only 'Summon Lyney'" is fixed for seats and open for a human at the reward screen ([USER]'s 2026-09-24 co-op friend hit the same wall). "Summon X." plus Line plus Act renders at 73 (Sigewinne), 80 (Charlotte), 94 (Lyney), 113 (Chevreuse), 128 (Wriothesley), 137 (Clorinde) and 149 (Lynette) against the 120 ceiling (badge texts plus `FurinaStageLaw` constants). Four fit, three do not; the Varka Knight pattern (one shared rail word, one shared tip, `text-conventions.md:124`) cannot carry seven different Lines, so the fix is per-card wording.
2. **Spend and Fanfare have no row in `text-conventions.md`.** Spend's three shapes (fixed, mode, spend-all) are consistent; the only Spend text in the file is the retired "Spend 2 Encore" in the Evoke row.
3. **Deploy, Evoke, Encore and Bow rows (`text-conventions.md:119-120`) describe the retired Salon trio**; no live face uses the words. BACKLOG:15 still says "Furina's Stage and Fanfare".
4. **Four id/name mismatches**: `proto_fs_standing_ovation` is Rising Applause while `_standing_ovation_all` is Standing Ovation; `_leading_lady` is Gentilhomme Usher; `_quick_cue` is Quick Flourish. The ids are the generated class names and so the ModelDb ids; a rename splits telemetry and seat-record names and may break a saved run holding the cards. Hygiene, timed after [USER]'s run.
5. **A Five-Century Act** reads "You can Drain down to 1 HP." Correct; seats could not tell what it buys. The Drain tip is the place to say the line moves.
6. **Repay with nothing drained** is fixed: since #916 (124b2deb, item 5) a Repay card prints "(Repays N)", and a below-line Drain prints "(Too close to your Drain line)" because the chooser cannot grey an option (`FurinaStageBowPreview.cs:62-70`). Still open: BACKLOG:50, a Spend card silently playing its plain side, from the fade round and unverified against the Tab's chooser.
7. **Chevreuse's end-of-turn preview** is settled by source: `FurinaStage.CueOf` maps her to `StageCueKind.Damage` (`FurinaStage.cs:494-496`).
8. **STATE.md:318-326** says Klee and Furina each have "seven relics and three potions". Furina's own reward relics are two, Opera Glasses and Grand Theater Program; Salon Solitaire is the starter and The Curtain Never Falls its Orobas upgrade at Ancient rarity, never rolled (`FurinaRelicPool.cs:25-45`, `UpgradedStarterRelics.cs:367`); one potion, Bottled Applause (`ArmPotions.cs:39-42`). `STATE.md:224` has this right. The layer is thin against the ruled shape of one Common, one Uncommon and one Rare potion per character (`ArmPotions.cs:22-24`) and the relics the proposal kept (Palais Ledger, Guest Book, Opening Night; sec.8 lines 374-381): work on the way to 78, not only a STATE fix.
9. Shared words are clean: Heal (base), Mend (Kokomi), Repay (Furina), one owner each, as sec.16 ruled.

## 6. What it takes to reach 78

**The gap.** 34 reward cards (12 / 15 / 7) to 78: 44 cards. On Kokomi's shape (21 / 36 / 21, `STATE.md:171`): +9 Common, +21 Uncommon, +14 Rare. The pool-40 paper added no Commons on purpose (`furina-pool-40-2026-10-05.md:27-31`), so the next batches are Uncommon and Rare build-arounds, plus co-op cards, two potions and relics.

**Already written.** The proposal's sec.8 "kept" list names cards not in the 34: Casting Call, Bring the House Down, Grand Entrance, Tutti!, Final Bow, Star Billing, Star Turn, Sold Out, Crashing Waves, Bubble Aria, Regina of All Waters, Navia, Neuvillette. Sec.7 gives texts for four (Casting Call line 293, Tutti! 309, Neuvillette 331, Navia 337); the other nine are names of v2 cards, several on v2-only mechanics. The list is not authoritative either: it cut Bis! and Thunderous Applause (lines 387-393), which pool-40 then added. So: four written, nine to re-think, 31 new, all the main session's.

**Beyond cards.** (a) Art: seven pool cards and one Ancient are unpainted (A Five-Century Act, Fountain of Lucine, Hold the Stage, Hymn of Many Waters, Salon's Encore, Salon's Tab, Surging Waters, Center of Attention; `tools/art_coverage.py:549-559`); painted v2 assets are kept on disk for Bring the House Down, Bubble Aria, Final Bow, Grand Entrance, Navia, Neuvillette, Regina, Sold Out, Star Billing, Star Turn and Tutti (orphan list, lines 401-539), so the reuse cards arrive with art and about 30 new cards need paintings. (b) Code: the 11 `FurinaStage*.cs` files are the live Tab (`FurinaStage.cs:16-18`: "THE SALON'S TAB... the sim twin is `tier0/engine/furina_tide.py`"). `tier0/engine/furina_v2.py` is the discarded v2 rules but is imported by `combat.py:18` (called at 376, 852, 990, 1145), `effects.py:747,5993`, `furina_tide_probe.py:266` (its `ref:v2` row) and `tests/test_furina_v2_slice.py`; removing it is an engineering change with a test to retire. BACKLOG:144's three C# classes: `SpotlightSystem.cs` is live (Hymn, Standing Ovation, `ModalChoice.cs`), `FurinaResources.cs` is live (`FurinaStage.cs`, `DrainedCounter.cs`), `CurtainCallPowers` no longer exists. (c) The sim cannot price spend-all cards or Powers, so every new Crowd card is read by seats. (d) Furina's `uniq` and `maxclu` are on the distinctness debt list (`tier0/tests/test_distinctness_gate.py:34-39`) because seven guests and seven two-mode cards share a shape; 44 more cards widen it unless the metric learns the shapes. (e) `meters_by_turn` is null on her rows, so Fanfare banked and Drain per fight are measured only in the sim.

**Order and pace.** The order is ruled: build to 39, deploy, "Then your run" (`furina-pool-40-2026-10-05.md:106`; [USER]: "40ish ahead of my first run"), and `STATE.md:224` names his play next; stage-gate's "pool near 78, two seats, one full run" is the finish line after it. Not a pick. Then two batches of about 22, each with a seat round and a loop-probe run; re-run today on the 34, the probe finds PRODUCTIVE 0, INERT 2 (Interval Bell on an empty stage; `fc_furina_rev/loop_probe.txt`; fa4b8315's run predates pool-40).

## Hygiene Claude can just do

- Print each Guest Star's Line and Act on the face for the four that fit under 120 (Sigewinne, Charlotte, Lyney, Chevreuse); for Wriothesley, Clorinde and Lynette print the Line and keep the Act in the tip, or shorten both. Keep the tip and the in-combat Bow line.
- Add Spend and Fanfare rows to `text-conventions.md`; retire the Deploy, Evoke, Encore and Bow rows; reword BACKLOG:15 to "Drain, Repay and Fanfare".
- Rename the four mismatched ids in one regen, moving art keys and `KNOWN_MISSING` entries with them, after [USER]'s run and never mid-save.
- Verify BACKLOG:50 against the Tab's Spend chooser; close or keep it.
- Extend the Drain tip with one clause: "Lyney and A Five-Century Act move the line."
- Add Fanfare and drained HP to `meters_by_turn` on her telemetry rows; filter the PPW4 control on `run_instance`, not `run_id`, in any future control column.
- Correct STATE.md:318-326 for Furina (two reward relics, the starter and its Ancient upgrade, one potion); drop `CurtainCallPowers` from BACKLOG:144; sweep BACKLOG lines 50, 51, 58, 82 against the Tab build.
- Rename `furina_stage.py` to match the engine it twins (`tier0/engine/furina_stage.py:6-7`); leave `furina_v2.py` until its callers and test are retired in a planned change.
- Paint the seven pool cards and Center of Attention; clear the five power icons.
- When a lane is free: confirm the two Ancients draft and resolve on the Tab, and that the guest hover tip shows at the reward screen.

## Picks

1. **Pneuma's shape, after your run.** **Default: the record's order.** Print the guest Lines and Acts on the faces, run one seat round, and see whether Pneuma is drafted before any card changes. If it still does not form: Option 2, Repay cards that also Drain a little ("Drain 2. Repay 5."), so a Pneuma deck lends and returns in one card. Option 3, fold the readers into "Drain or Repay" like Darling; Endless Waltz would then be Critics' Darling word for word at Uncommon, so it needs a different number or role. Option 4, drop Pneuma to the relic plus Rares. If your run finds Repay fun as it stands, none fires.

2. **The act-3 lever, if your run confirms the seats.** The record's lever, a readable Pneuma card, cannot change the HP she carries between fights (Section 1): the curtain call already returns drained HP, and JF39's 54 HP at the Soul Nexus were hits. **Default: tempo, not Block or Repay.** Her damage lead over the control is 46% in act 1 and 0% in act 3; a Rare or two that scale into act 3 (the sim's drafted deck ends fights with 21.7 Fanfare unspent) end fights before the hits land. Option 2: in-fight Repay volume at Common or Uncommon, which keeps her alive inside a fight and buys more Drain, not carried HP. Option 3: Block from Repay (Sigewinne's line as a card). Option 4: no lever; let 78 cards answer it.

3. **Co-op cards and the paired check.** **Default: three to five co-op cards in the last batch, then one paired round (Klee + Furina against Ironclad + Silent, shared seeds)**, reading her Fanfare per turn in co-op against solo. Option 2: no co-op cards before Balance; the paired round only.

4. **The Stage-era Ancients.** Both run on Fanfare and Spend; neither has been seen in play. **Default: keep both** and read them in the 78 round. Option 2: give one a Drain read (new text), so an Ancient belongs to Ousia.

5. **LAW.md:41 wording.** It says a guest "pays for it with a seat and Fanfare"; Tab guests pay a seat and 1 Energy. Amending LAW is yours. **Default: "pays for it with a seat and a card"**, no rule change. Option 2: leave it until Balance.

**Where the evidence is thin.** Four seat runs on four seeds, Sonnet at medium effort, A0; two reached act 3 (11 fights) against one control run (6 act-3 fights) on a reduced Ironclad pool. No human has played the Tab. The sim's draft and gauntlet probes do not read this kit's finishers. Every co-op statement is from the rules, not play.

## Fact-check log

Changed (each point confirmed against the named source first):
- Control column: the 30 effort-test act-1 rows dropped (`run_instance` 20261005-015157/015159); act 1 is 17.2% / 3.8 / 18.2. Control's pre-#924 pool and the cross-seed caveat added.
- Telemetry table compares round 2 with the clean control. "Same 3 Block" and "act-2 HP loss below the control" corrected (4.3 vs 3.8; 24.9% vs 20.5%).
- Unplayed list: Fountain, Lyney, A Five-Century Act, Tidal Flourish, Charlotte. Hold the Stage, Endless Waltz, Sigewinne moved to "barely played".
- Grand Deluge 20 plays, 17 upgraded, 6.1%; Bravura 27.9% of all, 30.8% of credited; Soloist 56, Crabaletta 44, Usher 36, Rejoice 12, upgraded plays counted throughout.
- Repay warning and Chevreuse preview: already fixed (#916 item 5; `FurinaStage.cs:494-496`); both hygiene items removed.
- Act-3 lever: a Repay card cannot change carried HP under the curtain call; default moved to tempo, Repay kept as an option with its limit stated.
- "Structural, not tuning" softened: the ceiling is structural, the absence is not shown to be; sim unrepaid HP, relic order, the record's legibility-first order and sim pick rates added.
- Old Pick 2 default (readers read "Drain or Repay") demoted to an option with the Darling-duplicate warning; default is the record's legibility test.
- "Ten seat-acts" → round 1's four acts (`furina-tab-round-2026-10-05.md:31`).
- Reaction rate: measured by `reactions_by_turn`, 0.036 per turn, with the comparison set.
- Guests: four carry an element; Lynette needs an aura; no Hydro guest, so no guest Vaporize; the LAW wording mismatch became Pick 5.
- STATE correction rewritten (two reward relics, Ancient upgrade never rolled, one potion); thin relic/potion layer added as work.
- Reuse list: four texts, nine names; sec.8 not authoritative (Bis!, Thunderous Applause).
- Pick 1 (order) removed: ruled by `furina-pool-40-2026-10-05.md:106` and `STATE.md:224`; a decided question is not re-asked.
- Ancients option 2 re-attributed: "a quarter of your starting HP" is sec.8's relic text for The Curtain Never Falls.
- [USER]'s three runs: three shapes, only 2026-09-28 was "easy, then act 3".
- Sec.6(b): `FurinaStage*.cs` is the live Tab; `furina_v2.py` deletion removed from hygiene (imported by `combat.py`, `effects.py`, the probe, a test); `SpotlightSystem` and `FurinaResources` live, `CurtainCallPowers` gone.
- Art: seven unpainted pool cards plus Center of Attention; painted v2 orphans listed; "long pole" softened.
- Tidal Flourish hygiene item removed: the gem is correct under the 2026-10-02 rule; either change is a rules or rule-text change.
- Guest faces: Bow line noted; lengths 73 to 149; the Knight pattern rejected as a fix.
- TNB6's act-1 boss: record says Ceremonial Beast, telemetry says Vantom; both shown.
- Loop probe re-run on the 34: PRODUCTIVE 0, INERT 2; fa4b8315 cited as the earlier run only.
- Gaps added: control pool, relic/potion layer, rename risk, Fanfare row, Repay bodies vs readers, sim picks vs seat plays, co-op targeting unverified, act-3 sample sizes.

Rejected or amended:
- "Hold the Stage 7 plays": the per-form counts are 1 plain and 3 upgraded, 4 plays (`fc_furina_rev/v1.py`, same method as `fc_furina/t6.py`); the fact-check's 7 adds the upgraded count twice. The card was played, which is the point; the paper says 4.
- "The table copies the round-1 record's Ceremonial Beast": true, and the record is the cited source, so the paper keeps the record's figures and adds the telemetry name rather than silently overwriting a cited document.
- Everything else was confirmed against source (124b2deb, `FurinaStageBowPreview.cs`, `FurinaStageBadges.cs:46-85`, `FurinaRelicPool.cs`, `UpgradedStarterRelics.cs:367`, `ArmPotions.cs:22-42`, `art_coverage.py:549-559`, `text-conventions.md:118`, the sheet rows for Endless Waltz, Critics' Darling, the guests and Charlotte, the records and proposal lines, the memory notes, the `furina_v2` import sites, the class greps, the guest-face lengths and the loop probe).
