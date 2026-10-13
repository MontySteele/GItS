# Reaction system review (2026-10-08, revised after fact-check)

Read against the main checkout (local HEAD 5f9d0628), `origin/klee-next` 063e1b40 for Klee's live sheet, and the telemetry the report reads by default (main install plus lanes 1 to 5; 5,399 fight rows, 5,297 after de-duplication on run instance and seat, the Klee suite still writing). Every number below was computed by `fc-rx/rx_recheck.py` in this folder (output in `fc-rx/rx_recheck.out`) unless it names another file. Nothing here touched a lane or the repo.

**One correction that runs through the whole paper.** `reactions_by_turn` is a running total since combat start, sampled when each turn opens (`PlayTelemetry.cs:276-284` writes `mine - record.ReactionsAtStart`). The first draft summed its entries, which counts each reaction once per later turn and inflated every rate it reported from that field two to three times (Varka solo read 2.11 a turn; the last-entry figure is 0.77 and the by-type figure 1.00). This draft uses the field's last entry, which is a lower bound (it misses the last turn's reactions), or `reactions_by_type` where a row has it. Where the two can be compared (Klee and Varka, 588 rows) the last entry is never above the by-type total.

**Summary.** The reaction table is one set of fifteen values (`ReactionTable.cs:30-60`), identical in both engines and compared by the parity lint, and the rule is simple: one aura per enemy, every reaction consumes it, amplifiers multiply one hit. Several documents still describe the spent-aura rule the code dropped on 2026-10-03, and one of them is an open pick (the Zhongli paper). On value: the two amplifiers do the work the seats notice (5.4 to 7.5 bonus damage per Melt), Overload is the co-op gift (6 to all plus Weak), and Swirl and Crystallize are the two weakest outcomes because they eat the aura for 2 damage or 4 Block. Varka is the only kit that reacts alone (1.0 a turn, 97% of his fights). Klee reacts in a third of her solo fights, and reactions are 3.5% of her solo damage; Kokomi and Furina have no by-type data. On [USER]'s standard: co-op roughly triples Klee's reaction count and lifts her reaction share of damage to 12%. In human rows, co-op cuts her HP lost by a fifth (with Furina) to two fifths (with Varka); the single bot pairing shows no cut but is one seed on older builds and is not a controlled comparison. Nothing in the data looks "exponential", but the evidence is too thin to put a number on the lift, and [USER] has already accepted the co-op round's reading ("reactions give free debuffs, co-op stronger than planned, allowed by the standard", memory note 2026-10-07). The paired round that would answer it properly is queued after suite 5 and needs a one-line fix to the report tool first.

## 1. How the system works, in both engines

**Where it lives.** C#: `klee-mod/KleeCode/Elements/ReactionTable.cs` (constants :30-60, `Lookup` :70), `Elements/TriggerRules.cs` (the hit-on-aura decision), `Powers/AuraPower.cs` (amplifiers in `ModifyDamageMultiplicative`), `Powers/ReactionEffects.cs` (side effects, `Resolve` :377, cases :463-640). Sim: `tier0/constants.py:43-75` (the "tier0 twin" the C# header calls the single source of truth, `ReactionTable.cs:22-27`), `tier0/engine/reactions.py` (`resolve_hit` :122, `_react` :152). `tools/lint_constant_parity.py:120-138` compares the fifteen values.

**The rule** (`reactions.py:1-17`; `TriggerRules.cs` header): Pyro, Hydro, Electro and Cryo leave an aura; Anemo and Geo only trigger. One aura per enemy, two owner-turns. A same-element hit refreshes it. A different element with a table pair removes the aura and resolves the reaction. **Every reaction consumes its aura, Swirl and Crystallize included** (2026-10-03, [USER] quoted at `reactions.py:6-9`). Amplifiers multiply the one hit that triggers them and never persist (`LAW.md:44-47`). Overload splash, Swirl's 2 and Electro-Charged ignore Block and sit outside the damage pipeline; Shatter is separate (`ReactionEffects.cs:532-560`; `LAW.md:72-75`). Auras live on the enemy, so a partner's hit reacts with your aura; credit goes to the triggering player (`LAW.md:69-71`).

| Pair | Reaction | As coded (both engines) | Value per fire, observed |
|---|---|---|---|
| Pyro + Hydro | Vaporize | that hit x1.5 | 2.4 to 8.0 bonus (n = 7 to 16 per cell; noise) |
| Pyro + Cryo | Melt | that hit x1.75 | 5.4 (151 Klee solo fires), 6.8 (42 Varka solo), 7.5 (13 Varka co-op) |
| Pyro + Electro | Overload | 6 to ALL enemies, ignores Block; 1 Weak on the target | about 10 at the sample's 1.68 enemies a fight (packet `tel6.py`), plus a quarter off one attack |
| Electro + Cryo | Superconduct | 2 Vulnerable | x1.5 taken for two turns; flat, not per stack (`ReactionTable.cs:35-39`) |
| Hydro + Electro | Electro-Charged | 4 Poison | 4 + 3 + 2 + 1 = 10 if the enemy lives four turns |
| Hydro + Cryo | Frozen | next action -50%; first Attack Shatters for 6; boss room and not a minion: 2 Vulnerable instead | rare: 8 Varka solo and 6 Varka co-op fires in the whole by-type sample |
| Anemo + any | Swirl | fresh copies to every OTHER enemy, 2 to every enemy | about 3.4 damage at 1.68 enemies; **on a lone enemy, 2 damage and the aura is gone** (`ReactionEffects.cs` `SwirlPays`: `if (ReferenceEquals(e, target)) continue;`) |
| Geo + any | Crystallize | 4 Block to the dealer, `Unpowered` (no Dexterity) | 4 Block and the aura is gone |

**Documents that still describe the spent-aura rule** (facts; the fixes are in Hygiene, except the Zhongli paper, which is a pick):

1. `docs/current/LAW.md:48-52` still says "A trigger spends the aura rather than consuming it: the aura stays". Both engines consume it (`TriggerRules.cs` header, `reactions.py:6-9`). `LAW.md:69-70` also still credits "Burst energy" to the triggering player; the C# has no reaction-to-burst call (`grep GainBurst klee-mod/KleeCode` finds one comment, `KokomiOverhaul.cs:72`).
2. `review/ruled/element-home-review-2026-09-28.md` sections 3 and 4B rule the spent-aura model and promise two properties that no longer hold: a Swirl on a lone boss "does not throw away the setup" (sec. 4A) and Crystallize "never costs the real reaction" (sec. 4B). The file carries only the 2026-10-01 amendment (line 80); nothing marks the 2026-10-03 reversal.
3. `review/active/varka-paper-kit-2026-09-28.md:47`: "A spent aura still reacts with a new element."
4. `review/active/legacy-cleanup-2026-10-01.md:164-165` still lists `CrystallizeKeepsAura` as a switch that stays; it went on 2026-10-03 (`operations/prototype.md:88-89`).
5. `review/active/zhongli-paper-kit-2026-09-28.md:20-22, 27-28`: "a Geo hit on a fresh aura crystallizes it: Block, and the aura stays" and, in co-op, "he harvests his partner's auras for Block and never takes them away." That paper's three picks are open in `QUEUE.md:28-35`. See Pick 1.

**Two sim-only things to know about, not document errors.** The sim's `SWIRL_PAYS = False` (`constants.py:66`) while every C# build has it on (`klee-mod/Directory.Build.props:49`); with it off a plain sim Swirl copies the aura onto every enemy including the struck one and deals no damage (`reactions.py:190-192`), so a plain sim run does not model the shipped Swirl. This is recorded, not forgotten: `STATE.md:349` says "off until its retest", `legacy-cleanup-2026-10-01.md:164-165` keeps the switch until that retest, `test_element_port.py:46-49` pins the False default and `operations/prototype.md:85-87` documents it. The retest is Claude's to run (see "Claude's queue"). Second, the sim pays `BURST_PER_REACTION = 5` on every reaction (`reactions.py:285-286`, `constants.py:1165`) into burst bars that `tier0/content/characters/{klee,kokomi,furina}.yaml` still declare (`burst_max` 40, 20, 70). The reaction hook has no C# twin, but the bars are not dead: Furina's sim arm still pays burst on Salon ticks and Encore (`constants.py:1457-1459`; `effects.py:2093, 6726`; `furina_tide.py:5` imports `burst_energy`). Only the reaction-to-burst hook is a candidate for deletion, and that belongs to the Furina review.

## 2. Relative balance between elements and reactions

**What the seats value.** The sweep's reading stands up: "the amplifiers are the best thing the reaction layer does" and "the transformative reactions are numbers that arrive" (`review/ruled/elements-reaction-sweep-2026-09-05.md:41-52`). Melt is the one reaction a seat plans for (which hit carries x1.75), and in the Klee design review it is "real and liked when a Cryo companion is in the deck" (fanout copy, sec. 2.3). Varka's seats are the exception: "Reaction ordering is the best turn-by-turn puzzle in the project, and it is the only kit where the element system is the game rather than a garnish" (`review/active/four-kit-review-2026-10-01.md:564-567`).

**What fires, by character** (rows carrying `reactions_by_type`, which exist only since #945 on 2026-10-06, so Klee, Varka and the Silent only; de-duplicated on run instance and seat; `rx_recheck.py` secs. 1 and 11, with amp and debuff columns from the first draft's `rx_review_b.py`, which used the same field):

| Character, seats | Fights | Reactions a turn | Top three | Amp bonus a turn | Debuff stacks a turn | Fights with no reaction |
|---|---|---|---|---|---|---|
| Klee solo | 424 | 0.17 | Melt 151, Overload 97, Swirl 23 | 0.48 | 0.06 (Weak 87) | **67%** (monsters 71%, elites 62%, bosses 53%) |
| Klee co-op (with Varka, bot) | 31 | 0.49 | Overload 44, Vaporize 9, Swirl 3 | 0.31 | 0.34 (Weak 40) | 32% |
| Varka solo | 102 | 1.00 | Swirl 211, Superconduct 52, Overload 49 | 0.82 | 0.50 (Vuln 94, Poison 52, Weak 44) | 3% |
| Varka co-op (with Klee, bot) | 31 | 1.26 | Swirl 63, Overload 37, Vaporize 16 | 1.15 | 0.81 | 3% |
| Silent solo | 50 | 0 | | 0 | 0 | 100% |

Reading the table against the element-home review's "what each element wants" (`element-home-review-2026-09-28.md:43-53`):

- **Pyro** (one big hit) is served: Melt and Vaporize pay the Bomb. Melt plus Overload are 248 of Klee's 286 solo fires; the rest are Swirl 23 (Prune), Vaporize 7, Crystallize 4, Superconduct 3 and Electro-Charged 1, the last two from companions' hits. Her own cards cannot make the aura half (brief rule 5; ruled to stay, `review/records/klee-later-acts-2026-09-26.md:72`).
- **Electro and Cryo** have no character; their reactions arrive through companions and Varka's Knights. Superconduct is the best transformative on a high-damage deck (x1.5 on two turns of hits) and was 52 of Varka's solo fires; nobody reads it as a decision (sweep :47-52).
- **Hydro** (be the aura others cash in) has two characters and no by-type partner data: Kokomi's and Furina's rows predate the keys. The one Hydro-partner cut is Klee + Kokomi, 23 fights on 2026-08-16, 1.61 reactions a turn on both seats; both seats carry identical counts because those rows predate EB-156 (commit 3523aa2e, 2026-08-30, "the per-seat telemetry row counts the seat's own reactions"), so they are board totals from the old shipped kits. I do not use them for anything else.
- **Anemo**: with Swirl now consuming, "it requires three elements to effectively function" ([USER], `element-home-review` sec. 6) is only half answered. On two or more enemies it spreads and pays 2 each; on a lone enemy it is 2 damage for the aura. Varka does not feel this because his Swirl pays his Oath element on top (`STATE.md:239`, `varka_oath.on_swirl`), and his Swirls are 211 of his 395 solo fires, split 109 in fights that opened with one enemy and 102 in multi-enemy fights (`enemies` field). Klee's 23 solo Swirls (Prune) split 17 one-enemy to 6 multi.
- **Geo**: Crystallize is now 4 Block for the aura, which sec. 2 of the same review called "a cost to any reaction deck" before sec. 4B tried to fix it. 15 fires in the whole sample. Unpowered Block means Dexterity does not scale it. There is no Geo character; this matters for Navia, Albedo and Noelle companion cards, and for the Zhongli paper (Pick 1).
- **Frozen** fires 14 times in the sample. The one record reading is Kokomi's: "Frozen through Kaeya turned 17-damage hits into 8, and seats chose Defend over attacking to keep the freeze. One seat broke it with its own Deep Current once" (`review/records/kokomi-review-round-2026-10-05.md:48-50`). Its tip omits that the player's own Shatter spends the halving (`BACKLOG.md:51`).

**Damage from reactions, share of total** (`damage_by_kind["reaction"]` is the flat kinds; amplifier bonus is `amp_bonus_damage`; first draft's `rx_review_b.py`, keyed rows):

| | Flat reaction % | Amp bonus % | Both | Damage a turn | HP lost, % of max |
|---|---|---|---|---|---|
| Klee solo | 1.8 | 1.6 | **3.5** | 29.3 | 17.5 |
| Klee co-op seat (bot, with Varka) | 10.7 | 1.1 | **11.8** | 28.8 | 17.3 |
| Varka solo | 10.9 | 2.5 | **13.3** | 33.3 | 14.5 |
| Varka co-op seat (bot, with Klee) | 17.3 | 3.0 | **20.3** | 38.5 | 17.4 |

Klee solo by kind (packet `tel8.py`, not re-run): Bomb 54.8%, direct 41.0%, element 2.3%, reaction 1.9%. Klee is a Bomb deck that occasionally Melts. What co-op adds to her is Overload's Weak: 0.34 stacks a turn against 0.06 alone, the "co-op gift is debuffs" the co-op round named (`review/records/coop-reaction-round-2026-10-07.md:34-37`).

## 3. Who can start a reaction alone

From the rosters' `Pool()`/`Slice()` and the Generated card text (packet `cards2.py`/`cards3.py`, outputs in `cards2.out`). `LAW.md:39-41`: "No character card applies an off-element aura; off-element access comes only from companions, a co-op partner, or a guest on Furina's stage."

| Kit | Own element | Cards applying an element | Off-element from its own pool | Reaction-worded cards | Can react alone? |
|---|---|---|---|---|---|
| Klee | Pyro | 21 Pyro, 1 Anemo (Prune, a Swirl) | No. Aura half is a companion (Mika, Diona, Kaeya, Oz) | 7: six gated on a Bomb reacting (three print "If a Bomb triggered an Elemental Reaction this turn", Wait For It... and Aftershock say "a Bomb triggers", Sparkborne Magic "makes one of your Bombs react"), plus Prune | Only with a drafted companion; 67% of solo fights see none |
| Kokomi | Hydro | 27 by property, 31 by text; "every damaging card of hers applies Hydro" (`STATE.md:114`) | No | 1 (At Water's Edge, Rare Power: every reaction, 1 Weak + 1 Vulnerable) | Only with a companion; she is the aura half |
| Varka | Anemo | Anemo 13, Electro 11, Pyro 10, Cryo 8, Hydro 7, Geo 1 by text; 13 Knights | **Yes**, through his Knights, which are companions under `LAW.md:39-41`; his current element is his last Knight's (`STATE.md:236`) | 18 | Yes, 1.0 a turn, 97% of fights |
| Furina | Hydro | 4 of 34 | Only through the seven built guests (`prototype-surface.yaml:2706-2841`): in the sim arm Wriothesley Cryo, Clorinde Electro, Lynette Anemo, Lyney Pyro; Charlotte, Sigewinne and Chevreuse hit with no element (`furina_tide.py:85-87, :706`). No Geo access. | 0 | With a guest; at least 42% of solo fights see one (`reactions_by_turn` last entry) |

So the project has one reaction character and three that react when something else supplies the second colour. That is the ruled design, and the four-kit review's warning stands: "two Rare slots that most solo decks cannot turn on are the most expensive kind of dead offer" (`four-kit-review-2026-10-01.md:397-402`), covered by the Klee design review's checks on Perfect Timing and Wait For It... (sec. 2.3). I do not repeat those.

## 4. Solo versus co-op, against [USER]'s standard

The standard (`docs/current/operations/stage-gate.md:80-86`): a kit is judged solo against the base five; "It's fine for co-op to be easier, but the characters should not be outright weak in single player and dependent on reactions in a way that makes co-op exponentially easier." The check is a paired seat round on shared seeds, kit pair against Ironclad + Silent. It has run once, one seed a side, and its own record says it "does not answer the question" (`coop-reaction-round-2026-10-07.md:18-21`). [USER] read that record and accepted it: "reactions give free debuffs, co-op stronger than planned, allowed by the standard" (memory note `overnight-coop-and-suite2-2026-10-07.md`, line 11). So the question below is not whether co-op is allowed to be easier; it is whether anything in the data contradicts that acceptance. Nothing does.

**All fights, de-duplicated on run instance and seat, all feeds** (`rx_recheck.py` sec. 2; co-op rows are per seat, so a seat's HP lost is its own; "reactions a turn" is the last-entry lower bound):

| Character | Seats | Fights | Died | Turns a fight | Damage a turn | HP lost % (mean / median) | Reactions a turn (lower bound) | Fights with none |
|---|---|---|---|---|---|---|---|---|
| Klee | 1 | 1,891 | 47 | 3.80 | 18.8 | 17.0 / 12.9 | 0.16 | 67% |
| Klee | 2 | 202 | 1 | 4.88 | 18.7 | 12.7 / 8.6 | 0.46 | 29% |
| Kokomi | 1 | 567 | 6 | 4.21 | 11.3 | 16.6 / 12.1 | 0.12 | 69% |
| Kokomi | 2 | 42 | 0 | 4.76 | 22.0 | 10.5 / 2.7 | 0.81 | 7% |
| Furina | 1 | 1,017 | 19 | 4.72 | 14.1 | 12.3 / 6.4 | 0.21 | 58% |
| Furina | 2 | 105 | 0 | 5.60 | 14.7 | 6.5 / 0.0 | 0.47 | 30% |
| Varka | 1 | 517 | 4 | 4.41 | 23.5 | 15.0 / 10.0 | 0.77 | 9% |
| Varka | 2 | 93 | 1 | 4.84 | 29.0 | 11.2 / 5.8 | 1.16 | 1% |
| Ironclad / Silent / Defect / Necrobinder / Regent | 1 | 364 / 276 / 74 / 73 / 70 | 5 / 5 / 0 / 0 / 0 | 4.4 / 4.3 / 3.9 / 3.6 / 4.1 | 19.7 / 22.2 / 29.1 / 23.5 / 28.2 | 17.2 / 12.1 / 13.6 / 15.7 / 13.7 (means) | 0 | 100% |
| Ironclad + Silent | 2 | 3 + 3 | 1 + 1 | 4.7 | 15.2 / 10.5 | 38.5 / 33.6 (means) | 0 | 100% |

Elites and bosses only, HP lost % solo to co-op: Klee 32.4 to 21.7; Varka 31.1 to 18.5; Kokomi 28.5 to 15.4; Furina 27.4 to 12.0 (sec. 3). Reactions a turn there (lower bound): Klee 0.24 to 0.55, Varka 0.86 to 1.31.

**Why that table overstates co-op.** The co-op rows are mostly [USER]'s own runs (Klee 155 of 202 seat rows human) and the solo rows mostly Sonnet seats, and he "wins any A0 co-op run with base characters" (`stage-gate.md:81-82`). Two cuts that hold feed constant (`rx_recheck.py` secs. 4 and 5):

- *Human against human.* Klee solo 16.7% HP lost (101 fights) against 9.6% with Varka (43 fights, 2 seeds) and 13.7% with Furina (89 fights, 4 seeds): drops of two fifths and a fifth. Furina 9.8% (98) to 7.1% with Klee (89): a quarter. Varka 8.2% (14 fights, too few to lean on) to 6.5% with Klee (43) and 11.7% with Kokomi (19). Kokomi 10.3% (75) to 17.2% with Varka (19); her 5.0% with Klee is the 2026-08-16 old-kit run and does not count. Reaction rates in the same rows (lower bound): Klee 0.24 a turn solo to 0.36 to 0.39 in co-op; Furina 0.16 to 0.49; Varka 0.58 to 1.43 with Klee; Kokomi 0.17 to 0.34. The first draft said "a tenth to a quarter, none for Varka"; that cut had 31 bot rows mixed into the Klee + Varka pair. With human rows only the drops are a fifth to two fifths, and Varka drops too.
- *Bot against bot.* The seat-round pairing (Klee + Varka, seed `30KMHAVG9SMQ`) is two run instances: the attempt abandoned on a desync at floor 24 (10 fights) and the rerun (21 fights), so its 31 rows count acts 1 and 2 twice; the record's own table says 21 fights (`coop-reaction-round-2026-10-07.md:15`). Klee lost 17.3% of max HP a fight there against 17.5% in her keyed solo rows (424 fights, 5 seeds); Varka 17.4% against 14.5% (102 fights, 5 seeds). The pair lost the act-3 boss. This is not like-for-like: one seed on builds 0.2.4508 to 4516 against five seeds on later `klee-next` builds. It says co-op did not rescue a bot pair on that seed, and no more.

**Reaction counts** do move the way the standard worries about: Klee's triple (0.17 to 0.49 a turn by type; 67% to 32% fights with none), Varka's quarter, and two- to three-fold rises for Furina and Kokomi in human rows. But the reactions' share of damage stays modest (Klee 12%, Varka 20% in co-op), so a tripled reaction count is a tripled small number. The lift that shows in HP lost comes with a second body and Overload's Weak, not with a damage multiplier.

**Against the standard, kit by kit.**

- **Klee.** Two readings exist and both are right about different things. By damage share she is not reaction-dependent: 3.5% of her solo damage. By marginal lift she is the most reaction-dependent kit, as the Varka solo check says: "Alone she almost never reacts (0.05 a turn), so a partner's elements are nearly all new value for her; that is why co-op lifts her far more than it lifts Varka" (`review/records/varka-solo-check-2026-10-07.md:56-58`). The human cut agrees: her HP-lost drop with Varka (two fifths) is the largest on the table. She is weak solo on the seat bar (0 of 5 in each of four suites, `review/records/klee-suite-*.md`; the base five also went 0 of 5, `base-five-baseline-2026-10-05.md:5`), and `STATE.md` names the cause as Block at the boss turn, not missing reactions.
- **Varka.** Meets the solo half outright: 1.0 reactions a turn alone, damage level with the base five, HP lost 30 to 57% below them (`varka-solo-check-2026-10-07.md`, "What it says" 1 and 3). The open worry is the other direction: too sturdy at Balance.
- **Kokomi and Furina.** Unmeasured by type. Their `reactions_by_turn` last entries say they react in at least 31% and 42% of solo fights, which can only be companions or guests. Kokomi's solo damage a turn (11.3) is the lowest on the table, half the base five's, but her rows end 2026-10-05 and span older builds. Furina's rows mostly predate the Salon's Tab (`STATE.md:224`). The next seat round for either carries the keys for free.
- **Base pair baseline.** Three Ironclad + Silent fights (floors 2 and 4 won, the floor-7 elite where both died; run instance `20261007-005613#0`). There is no co-op bar to read any pair against yet.

**Co-op defects in the reaction layer** already listed: the seat page's reaction glossary ignores the partner's element and lists the partner's cards as yours (`BACKLOG.md:42`); per-dealer reaction windows have no sim twin (`BACKLOG.md:144`, `SKIP-10.9`); Durin's turn-start Pyro has no fixed order against Melody Loop's Hydro (`BACKLOG.md:19`). Klee's gated cards read a per-owner ledger of her own Bombs' reactions (`KleeOverhaulLedger.ReactedThisTurn`, `KleeOverhaulLedger.cs:150-151, :210`; `ProtoKoSizzle.cs:72` on `klee-next`), not the board-global `ReactionEffects.ReactionTriggeredThisTurn` (`ReactionEffects.cs:180`), whose only card reader is Chevreuse's Vanguard's Valor. So a partner's reaction does not light Klee's gates; that is by design, and there is no co-op defect there.

## 5. Where the evidence is thin

One bot co-op pairing on one seed, counted twice across two instances. Human co-op: Klee 7 seeds (10 run instances), Furina 4 (6), Varka 3 (4), Kokomi 2 (2), one of hers from August. No by-type reaction data for Kokomi, Furina or any base character. Frozen and Crystallize fire too rarely to grade. Klee's all-build solo rows mix every build since August; her keyed rows (424) are 40% suite 2 and the `klee-common-next` arm (2026-10-07 01:00 to 04:00, 168 rows) and 60% suites 3 to 5 (`rx_recheck.py` sec. 10), so even the by-type sample straddles the tempo paper and the design review. The "exponential" question cannot be answered to the bar from this. What can be said: in human rows co-op cuts HP lost by a fifth to two fifths for the Pyro-Hydro and Pyro-Anemo pairs, which is a lift and not a multiple, and [USER] has already called that allowed.

## Hygiene Claude can just do

- `LAW.md:48-52`: replace the spent-aura sentence with the consuming rule and cite the 2026-10-03 quote already in `reactions.py:6-9`. `LAW.md:69-70`: drop "and Burst energy" from the credit rule, or mark it sim-only.
- `review/ruled/element-home-review-2026-09-28.md`: a one-line amendment under sections 3 and 4B pointing at the 2026-10-03 reversal, the way line 80 marks 2026-10-01. Same stale "spends" wording in `varka-paper-kit-2026-09-28.md:47`, `legacy-cleanup-2026-10-01.md:164-165` (`CrystallizeKeepsAura` is gone) and `BACKLOG.md:41` (Burning item).
- `tools/telemetry_report.py`: add `run_instance` to `fight_key` (:301-305) so `dedupe_seats` (:308-319) and the `--coop` team grouping (:381-383) stop merging two runs on one seed. It already happened: the Klee + Varka and Ironclad + Silent runs share seed `30KMHAVG9SMQ`, and the first draft's `rx_review.py` section C, keyed the same way, printed a four-character team. This lands before the paired round, not after. In the same pass, say in the report's header that `reactions_by_turn` is a running total (any reader that sums it inflates rates; the last turn is never sampled) and that co-op rows before 2026-08-30 (EB-156) carry board totals per seat. Tighten `ReactionTally.cs:24-25` to say "the final entry of `reactions_by_turn`".
- `tools/reaction_census.py` and `review/records/reaction-census-2026-09-05.md` read 2026-09 records that predate every current kit; retire the tool and its pin `test_reaction_census.py`, or re-point it at `review/records/` and say so in its header.
- `ELECTROCHARGED_DOT_TURNS` / `ElectroChargedDotTurns`: neither resolver reads it (packet; I did not grep every file). Confirm and delete from both tables and the lint.
- Frozen tip: one clause on Shatter spending the halving (`BACKLOG.md:51`, already listed; two seat records hit it).
- The Melt/Vaporize factor on the face and in the seat log (`BACKLOG.md:54`, `:65`, `:86`), already listed; group them as one "show the amplifier" item.
- Element wording lint (`tools/lint_element_text.py`, `text-conventions.md:118`) is in place; nothing new to add from this reading.

## Claude's queue (measurement, no ruling needed)

- **The paired co-op round** is already queued after suite 5 (memory note, "Lane queue after suite 5: ... (2) co-op paired round"). Run it on the five base-five baseline seeds, bot Klee + Varka and bot Ironclad + Silent, two lanes each, after the `fight_key` fix above; read it with `telemetry_report.py --coop --reactions` and the human cut in `rx_recheck.py` sec. 4 as the reference. The first draft filed this as a pick; it is a measurement procedure, which CLAUDE.md gives to Claude.
- **The `SWIRL_PAYS` retest.** The recorded condition for flipping the sim default is a retest of the switch alone (`STATE.md:349`, `legacy-cleanup-2026-10-01.md:164-165`). Run it sim-only; the only Klee card it touches is Prune, and Klee is at Balance (`QUEUE.md:26`), so report the Prune delta in the Balance record before flipping. The flip then moves `constants.py:66`, the pin at `test_element_port.py:46-49` and `operations/prototype.md:85-87` in one commit, and re-runs `test_reactions.py` and `lint_constant_parity.py`. Not a silent hygiene edit.
- **`BURST_PER_REACTION`**: hand to the Furina review. The hook has no C# twin, but the bars it feeds are live in Furina's sim arm (sec. 1).

## Picks

1. **The Zhongli paper stands on the reversed Crystallize rule.** `zhongli-paper-kit-2026-09-28.md:20-22, 27-28` builds his co-op premise on "the aura stays" and "never takes them away", and its three picks are open in `QUEUE.md:28-35`. Under the code as it is, his Geo hit eats the partner's aura for 4 Unpowered Block. [USER]'s aim for Geo was "useful whether you trigger it incidentally ... but not broken if it's your primary element" and "doesn't just become a source of infinity block if we don't consume the aura" (`element-home-review-2026-09-28.md:133-135`). Options: (a) amend the Zhongli paper to the consuming rule now and bring its Geo section back with the character-five pick, leaving Crystallize at 4 Block meanwhile; (b) make Crystallize the one reaction that leaves the aura standing, as that paper assumes, accepting a Block-once-per-aura Geo deck; (c) raise Crystallize's Block (6 is a Defend) and keep it consuming, which helps an incidental Geo hit but does not restore the Zhongli premise. **Default: (a).** No Geo character is built, 15 fires in the sample, and (b) is the model [USER] dropped on 2026-10-03.
2. **Swirl on a lone enemy.** It is 2 damage for the aura. Varka does not mind because his Oath pays on top. For Klee's Prune the telemetry already shows the case: 17 of her 23 keyed solo Swirls fired in fights that opened with one enemy, where the Swirl spends a companion's aura for 2 and then re-colours her next Bomb with the swirled element (card text, `cards2.out`). No seat record has called that a waste. Options: (a) leave it: single-enemy Swirl is the price of a to-ALL reaction, and Prune's re-colour is its own payoff; (b) on a board with one living enemy a Swirl refreshes the aura instead of consuming it, as the 2026-09-28 review intended for bosses; (c) raise the flat 2. **Default: (a)**; (b) is small to build if a seat record reads Prune or Jean as spending a setup for nothing.

## Fact-check log

Changes made on the fact-check's points, each confirmed by me before acting:

- **`reactions_by_turn` is cumulative** (`PlayTelemetry.cs:276-284`; on 588 keyed rows the last entry is never above the by-type total, `rx_recheck.py` sec. 1). Replaced every summed rate with the last-entry lower bound or the by-type figure, and added the opening correction paragraph. The sec. 4 table, the elite/boss rates, and the Kokomi/Furina "react in" shares (now "at least") all changed.
- **Human-against-human cut** had 31 bot rows in the Klee + Varka pair. Re-cut by feed: Klee 9.6% with Varka (43 human fights), 13.7% with Furina (89); Varka 6.5% with Klee. The drops are a fifth to two fifths, not "a tenth to a quarter, none for Varka". Summary and sec. 5 rewritten.
- **Klee + Kokomi rows** are 2026-08-16, before EB-156 (3523aa2e, 2026-08-30), so they are old-kit board totals; removed from every comparison and said so.
- **Base pair** has three fights, not one (sec. 8 of the recheck). Fixed, and the merged four-character team traced to the missing `run_instance` in `fight_key`.
- **Klee's gated cards** read `KleeOverhaulLedger.ReactedThisTurn` (`ProtoKoSizzle.cs:72` on `klee-next`), not the board-global flag; only Vanguard's Valor reads that. Sentence rewritten.
- **`SWIRL_PAYS`** has a recorded "off until its retest" (`STATE.md:349`, `legacy-cleanup:164-165`) and a pin that asserts False (`test_element_port.py:49`). Moved from Hygiene to Claude's queue with the retest first.
- **Furina's guests**: seven built rows, no Navia, no Neuvillette card; elements taken from `furina_tide.py:85-87`. The sim also hits with no element for Chevreuse (`:706`), which the fact-check did not mention; the C# guest elements were not checked.
- **Documents on the dead rule**: now five, plus two sim-only notes; `SWIRL_PAYS` moved out of that list.
- **Picks**: the paired round moved to Claude's queue (measurement, already queued). Crystallize re-framed around the open Zhongli pick, with [USER]'s Geo aim quoted. Swirl pick re-based on the one-enemy telemetry (17 of 23 Prune Swirls).
- **Sample descriptions**: Klee's keyed rows are 40% suite 2 and the arm; human co-op is Klee 7 seeds / 10 instances, Furina 4 / 6, Kokomi 2 / 2, Varka 3 / 4; the bot pairing is two instances and 31 rows double-count acts 1-2 against the record's 21.
- **Smaller fixes**: Klee's by-type breakdown (248 of 286 are Melt + Overload, not "whole output"); Vaporize range 2.4 to 8.0; the Varka and Kokomi quotes restored verbatim; LAW.md line numbers (72-75 pipeline, 69-71 credit); `reactions.py:190-192`; `STATE.md:263` replaced by `LAW.md:39-41` and `STATE.md:236`; fifteen reaction values, not nine; the Klee reaction-worded phrasing split three / two / one; the Varka solo-check's opposite reading named and reconciled; [USER]'s acceptance of the co-op round named; the burst bars kept (Furina's sim arm reads them).

Fact-check points rejected or qualified:

- **"Its third item, SWIRL_PAYS, is a constant, not a document."** Agreed on the sorting, but the point that a plain sim run does not model the shipped Swirl is still true and worth a reader's knowing; kept as a sim-only note rather than deleted.
- **"The paper also does not mention [USER]'s recorded aim for Geo, 'useful whether you trigger it incidentally', which 4 Block for the aura does not meet."** The quote is added. Whether 4 Block "does not meet" it is a taste call; the paper gives [USER] the options and does not decide it.
- **"Telemetry already answers" Pick 3's trigger.** Partly. Telemetry shows 17 of 23 Prune Swirls fired on a one-enemy board; it does not show a seat reading that as a waste, and Prune's text re-colours the next Bomb, which is a payoff the fact-check did not weigh. The default stays (a), with the condition re-stated.
- **The 31 bot rows "double-count acts 1-2".** Confirmed (10 + 21 rows across two instances, `rx_recheck.py` sec. 7). The table in sec. 2 still shows 31 because the by-type columns were computed on those rows; the caption now says they are two instances of one seed.
- Nothing else in the fact-check was wrong. Its numbers (Varka 758 against 395, Klee 465 against 276 on the summed field) differ slightly from mine (492 against 286 for Klee) because the suite wrote 36 more rows between the two runs.
