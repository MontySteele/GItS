# BACKLOG

Open engineering work, one line each. No required fields and no new ids: add
an item as a plain line, and delete it in the commit that builds it. An item
that already had an `EB-` id keeps it so old citations resolve. Picks for
[USER] go in `QUEUE.md`; kit design work is in each kit's brief and `STATE.md`.

Closed items are in git. The last copy in the old four-field form, with
every built row, is `git show 2b73880a:docs/current/BACKLOG.md`; the rows that
closed on 2026-09-08 are at tag `backlog-archive-2026-09-08`; older ones at tag
`pre-simplification-2026-08-06`.

## Kits and display (the mod)

- Off-character kit cards, base-game faithful (resources work for anyone and their gauge appears on first gain, like the Regent's Stars and Osty): Furina's Stage and Fanfare, Kokomi's Plans and Kurage, Varka's Oath. Each is done when its kit reaches Balance; Klee done 2026-10-05.
- Klee status package: art for Forbidden Fun, It Wasn't Me!, Lisa's Treats, Red Knight, Finders Keepers, Klee Can Explain!, Damage Report and Albedo — Dust of Purification (placeholders; Dust's plan row is re-pointed from Tectonic Tide's Albedo Wish splash, not yet fetched); the two Powers borrow Party Poppers' and Spark Knight's badges.
- Klee defence in the status pile (2026-10-01): art for Up in Smoke!, Behind Jean's Desk and Kitchen Alchemy (placeholders).
- Klee final pass (2026-10-02): art for Cover Your Ears! (placeholder).
- AoE trim (2026-10-03): Durin, Principle of Purity's turn-start Pyro hit (`PurityStrikePower`) shares `AfterPlayerTurnStart` with Melody Loop's Hydro, Herald of Frost's Cryo and Surprise Dispatch's roll, so the mod gives it no order where the sim runs it after Melody Loop (a reaction and an rng race); stage it into its own broadcast if a seat sees the two disagree.
- AoE trim (2026-10-03): art for Durin — Principle of Purity (wears Binary Form's picture, `art_of`); the three Purity powers borrow Binary Form's badge.
- Klee finish-line batch (2026-10-03): pinned headless only, so watch at the next Klee seat round and through the bridge: Dodoco Tales' opening Sparks (5 on turn one after Touch of Orobas, and the Spark row naming the relic), Finders Keepers' draw trigger (a Bomb per status drawn, Dazed and Confiscated alike), Confiscated playing as a Status (the drag-to-play, the frame, and Klee Can Explain! / Kitchen Alchemy taking it), and Mine, All Mine!'s Mine landing on the enemy its hit killed.
- Kokomi status batch: art for Kelp Wall, Tidecleanse, Sea Glass Harvest, Turning Tide, Flotsam Surge, Abyssal Salvage and the Sea Glass token (placeholders); Abyssal Salvage borrows the Princess of Watatsumi badge.
- Kokomi status batch: the stock sim pilot cannot read the next-hand Plans (Kelp Wall's count, Tidecleanse, Sea Glass Harvest, Turning Tide) or plan for statuses it has not drawn; their census rates are unread, as Coral Tithe's were.
- Pool completion (2026-10-01): run paper sec.7's sim checks on the built pools (`review/active/pool-completion-2026-10-01.md`): each of Kokomi's four decks within 10 points of Plan volume with the new Rares granted, and no new card taken from over 70% of offers or played in under 5% of the fights where it is held.
- Pool completion (2026-10-01): art for the 14 new rows and the three new Ancients (Alice's Masterpiece, Divine Strategy, Center of Attention); all render the placeholder.
- Pool completion (2026-10-01): Divine Strategy's now-line, Center of Attention's free Spend and the two co-op cards (Tactical Relay, Kurage's Mercy) are pinned headless only; watch them in game and through the bridge at the first seat round.
- Varka has no Ancient card: Darv's Dusty Tome hands him an upgraded Four Winds' Ascension through BaseLib's `ITomeCard` (the row's `dusty_tome` tag) until one is designed; delete the tag with it.
- Verify Boreas's Fang saved starter element survives save/reload (`Relics/VarkaStarterKnight.cs`, a BaseLib `SavedSpireField`; no test exercises a real serialize/deserialize, so the Fang and Knight's Commission keep their deck fallback until then).
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- Varka's element-switch hover (`ArmKeywordTips.ForElementSwitch`) rides only his own `proto_vk_` rows; a Universal or another kit's card he drafts that applies an Oath element switches him too (the open Oath) and says nothing. Varka element identities, 2026-10-01.
- Varka's element-switch hover and the left-element icon (`OathLeftPower`) are untried in game and through the bridge: watch both at the next Varka seat round.
- The seat page's resolution rows do not say which hit was which: Four Winds' Ascension+ read "2, 3, 9, 36" with its Swirl payout, base hit and Oath hit unlabelled (Varka element identities round, 2026-10-01). Needs a source label per hit on `ResolutionLedger`'s wire and in `blindplay_render`'s hit rows.
- Kaeya — Frostgnaw printed 12 against a written 8, and its own Superconduct's Vulnerable (the tip says it "applies before this hit") did not multiply the hit on the Ceremonial Beast; trace the order and the printed number (Varka r6 round, lane 2 act 1, 2026-10-05).
- Seat page: draws made by effects print nothing (Eye of Stormterror on a Swirl, Static Field, Tempest Charge), so seats cannot tell whether they fired; list cards drawn outside the turn's draw in "Since last page" (Varka r6 round, 2026-10-05).
- Four Winds' Ascension's Oath hit leaves an aura but gains no Oath, where Barbara's hit does; nothing printed says whether that is the rule (Varka r6 round, lane 1, 2026-10-05).
- Varka defence (2026-10-01): the Fang's turn-one element and Windborne Resolve are pinned headless and in the sim only; watch them in game and through the bridge at the next Varka seat round.
- Weathervane's start-of-turn element grid is untried through the bridge and in co-op: watch it at the expansion's first seat round.
- Card reward card off screen but still selectable by controller (user, co-op run 2026-10-02). Cause not found: the base row (350 px apart, centred) keeps four and five cards on a 16:9 canvas, and the run's rewards were four cards. `Diagnostics/RewardRowProbe.cs` now writes a "reward row OFF SCREEN" WARN to godot.log naming which card, where its holder is and where its body is drawn; read that line after the next sighting and fix from it.
- Seat page: the Neow bundle page printed one pack's rows jumbled (Oathsworn Strike's line missing, its text under Rising Gale; Varka Oath round, lane 2 act 1). Not reproduced: the bridge strips newlines from each face and the render prints each bundle's cards in wire order; it needs the raw `bundle_select` state from such a screen.

- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning, where a Swirl or Crystallize on a burning enemy spends the held Pyro and Burning keeps ticking; and Dendro ported as ruled (the non-reacting pairs, the Core rules and their previews), tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Co-op seat page: the "What you played this turn" log lists the partner's cards as your own; players are named "Test Host"/"Test Client 1"; the reaction glossary ignores the partner's element; a contested chest pick is not announced; `wait` after a finished fight reports nothing while the reward is up; a play at an enemy the partner just killed is silently retargeted (co-op round, 2026-09-27).
- Seat page: the Weak gloss says it cuts a Bomb's damage (it does not: a Bomb carries the target's modifiers only) (co-op round, 2026-09-27).
- Kokomi text: the Neow bundle's Plan gloss omits "instead of playing it now"; the Casket tip does not say it ignores a debuff from a reaction set off by its own hit (Kokomi core seat, 2026-09-27).
- Kokomi's Plan list prints a waiting Plan's damage without the target's Vulnerable (Surging Shoal 50 there, 75 in hand and landed): a queued card is in no pile, so its numbers never refresh; `KokomiPlan.QueueRow` could send the front-target-folded number (`PlannedDamage(FrontEnemy, ...)`) for front-aimed Plans; `WrittenFrontDamage` has the same gap (Kokomi review round, 2026-10-05).
- Co-op rest site: Mend on the partner did not end the rest action, so Smith was still offered (co-op round, 2026-09-27).
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- Seat page: a companion's end-of-turn hit (Kaeya, Oz) names its body only when it reacts; a plain hit is on no wire, because `ResolutionLedger` files card plays and a power's damage is not one (wave-3 Klee lane 2b, 2026-09-26).
- Seat page: killing a reviving boss mid-turn (Test Subject) makes it vanish from the page with no notice (Furina fade round, 2026-09-29).
- Furina: a Spend card silently plays its plain side when her Fanfare cannot pay the Spend (fade round, 2026-09-29).
- Frozen: the tip says the next action deals 50% less, but a Shatter ends the freeze first, so the player's own Shatter spends the halving (Furina seat, 2026-09-29: Rosaria then Chevreuse's Ring, and the Beetle hit for 18); the tip wants one clause on Shatter.
- Kokomi: Smoggy ("you can only play 1 Skill per turn") refuses writing a Plan once a Skill is played; neither Smoggy's line nor the Bake-Kurage tip says writing a Plan counts as playing the card (Kokomi seat, 2026-09-29, Living Fog).
- `test_local_tester` is flaky: it failed once and passed on re-run with no change (2026-09-28).
- Rosaria's Melt on Klee's board printed "Deal 15" from a written 9, which no printed multiplier explains; show the reaction's factor on the face.
- `EB-807` `Unknown RelicModel ID: RELIC.KLEEMOD-TAMANOOYAS_CASKET` once per boot is the owner's `progress.save` DiscoveredRelics list naming the retired relic (non-fatal `Progress parse` warning, godot.log 2026-10-01); no alias is left in code. Harmless; drop the id from the save or let it be.
- `EB-798` `ProtoKkBreakwater` is offered Nimble but Nimble pays it nothing (its only Block is the Plan's); planned-only Block is not `GainsBlock`, in both engines and `lint_enchant_parity`.
- `EB-677` Glam's Replay on a timed card (Kyouka) runs it 4 turns at +4, not 2 at +8, and no face says which; needs an emitter change that gives the rule a tip surface, plus a taste call on which rows carry it.
- `EB-65` the four Furina power badges draw shrunk card portraits; they want badge-kind icons like Klee's (art bill, rank 1 applied).
- `EB-803` `proto_mc_kaeya_frostgnaw` wears Cold-Blooded Strike's named art (that card was cut 2026-10-03, so only Frostgnaw's own pick is owed); confirm `klee/relics/dodoco_tales.png` is packed on the next pck build.
- `EB-53` end-of-turn docket: capture the co-op half (`C6`) and isolate the electro (Oz) leg. The two-seat runtime now exists (`embark --coop`, `docs/current/operations/understudy-seats.md`); what remains is running the capture on it, and the Oz leg.
- `EB-296` / `EB-300` controller: a live walk that the Kokomi pet is targetable by D-pad and mouse, and that the hand is reachable after a custom-target card.
- `EB-159` [USER] at the machine: listen for the modded player's death sound (`set_hp player 1`, end turn into a hit).
- `EB-38` [USER] at a shop: the spine-less character portrait idles (the rest-site half is seen).
- `EB-160` verify a live locale switch: the injected loc tables survive it, or a `LocException` names the seam.
- A reaction amplifier's payout is not printed: the seat log reads "Vaporize on X" with no x1.5 (Varka seat, 2026-09-29: Weak 4 -> 3 printed, 4 landed). A hit carrying an element chosen at play (Four Winds' Ascension and Northwind Avatar's current-element hit) previews no amplifier either; the multiplier is pinned by `A_current_element_hit_amplifies_like_any_hit`.

## Harness, bridge and tools

- Bridge: the enchant chooser (relic Kifuda, 'Choose 3 cards to Enchant') never closes; `confirm_selection` appends the picks again (3→6→9→12), and cancel is refused — a seat stalls in the shop (seat round 2026-09-26, wave3-furina-lane2).
- Seat page: the Tainted per-hit note still gives two readings for a multi-hit, the same double count the Weak note had before #650.
- Seat page: Pocket Match's play log listed 3 and left out its own 5 damage.
- Seat page: a Companion summon's ticks (Kamisato Ayaka's Soumetsu) print only inside Kokomi's Plan block (`summon_hits`); a Furina or Klee page shows them nowhere (Furina lane 2, 2026-09-26).
- Seat page: copy numbers renumber after a play, so "Frantic Escape (2)" picked the other copy after the first was played (Kokomi review round, lane 2 act 2, 2026-10-05); name copies by something stable (cost or upgrade) or warn on renumber.
- Seat page: The Trial's first page printed only "Proceed", and `proceed` was then refused against its Accept / Reject options -- the page read the event mid-transition (Furina Solo seat, 2026-09-26).
- Soak: `soak_screens._escape` answers the Crystal Sphere with `crystal_sphere_proceed`, which the game refuses while divinations are owed; spend them first as the seat page's `reveal` does (`blindplay_shape.sphere_reveal_action`).
- Shop card removal: after the first card is picked the screen refuses a re-pick and offers only confirm or skip, so a mis-pick removed a Strike instead of a Defend (Varka starter round, lane 2 act 1, floor 14); check whether the base screen allows a deselect and the bridge lacks the verb.
- Seat page: Oathsworn Strike's line printed "Deals 29" and hit 31 on a Vulnerable target (Varka starter round, lane 1 act 3); the hand preview folds no target's Vulnerable, and the page does not say so.
- Seat page: an autoplaying relic (the Earring, Varka starter round, lane 2 act 3) plays the first turn with no line saying what it will play or played.
- Treasure Map plays and spends its Energy with no Set off card in the discard pile, and nothing warns (Klee w20 round, lane 2, 2026-10-04).
- Seat page: Tender (each card played costs 1 Strength and 1 Dexterity this turn) prints only "Tender 3"; Fireworks Finale's "Written: 5" does not name the Strength loss that lowered it; Spiny Toad's Thorns showed on turn 1 only (Klee final-pass round, 2026-10-02).
- Big Badda Boom's "then damage equal to what your Bombs dealt" does not say whether Bombs set off earlier in the turn count (Klee final-pass round, lane 1, 2026-10-02).
- Seat page: a Furina seat never saw her own Frail or Dexterity loss printed, so Defend at 1-2 was unexplained (smoke round, 2026-10-02); check the brief page lists the player's debuffs.
- Seat page: the Tamakushi Casket printed "(1)" between fights; its counter is combat-only (`TamakushiCasket.ShowCounter`), so the page reads `DisplayAmount` before combat state clears (smoke round, 2026-10-02).
- Louse Progenitor's intent under the player's Weak read "folded Strength and Weak: 14 on the move and 14 after" and the Weak seemed to do nothing; check the fold and the line (Opus seat, 2026-10-02).
- A Mine going off printed "gives 1 Spark" plus Pounding Surprise's "+1 Spark" but the seat counted +1, not +2; check the Spark accounting or the wording (Opus seat, 2026-10-02).
- Klee reaction log: "Melt ... No hit came with it, so there was nothing to amplify" printed beside a hit multiplied by 1.75, on three fights (Opus check round, lane 2, 2026-10-02).
- Klee suite 1 page and text problems (`review/records/klee-suite-1-2026-10-05.md`, items 1-7): Incoming ignores Mines that fire first and Look Out!'s Block from them; the Melt preview reads as if the whole Bomb pile multiplies; Big Badda Boom counts only damage past Block; Chained Reactions' +3 missed a two-Bomb Ka-pow! set-off (trace); the Spark line vanishes at 0 and Snecko Oil's added Spark costs are unexplained; Wait For It... printed "Nothing ... landed" on paying turns; Weak shows different Pyro numbers on card and board.
- Klee scaling round 1 page and text problems (`review/records/klee-scaling-round-1-2026-10-05.md`, items 1-6): the test relic's "Bomb 6" shows as 10 on her first turn with no word why; Boom Badge's Retain reads as if the doubling carries over; Durin's Dark +6 is missing from printed card numbers; Durin's start-of-turn tick skipped one fight (Fogmog, trace); "Witch's Homework" and "Witch's Homework II" read alike in hand lists; the "Put Mine N on ..." lines after Big Badda Boom read as five Mines from one Bomb.
- Fight telemetry: a boss that comes back in a new form (Test Subject) closes its fight line as `won` when the first form dies, so the later forms and a death in them are never written (Klee scaling round 1, arm 3; both base Ironclad baseline runs log a won Test Subject).
- Fight telemetry: log Witch's Homework II's run-long Bomb size (`HomeworkGrowth`) per fight, so its prediction can be graded (Klee scaling round 1).
- Jumpy Dumpty prints "place a Mine 3 on ALL enemies" but refuses to play without a named target (it aims the first Bomb); the face does not say a target is needed (w19 lane 1, 2026-10-03).
- The Bomb's damage number ignores Boom Badge+'s doubling after Boom Badge+ is played (Opus check round, 2026-10-02).
- Jean+ is switched off when Dodoco+'s Mine goes off on the enemy's turn ("a Bomb went off last turn"); the face does not say so (Opus check round, 2026-10-02).
- Perfect Timing's replay did not visibly fire when its first Set off killed the target (Opus check round, 2026-10-02).
- Mine text does not say whether the enemy's other Bombs go off with it, or that it spends the aura set for the big Bomb (Opus check round, 2026-10-02).
- Return to Sender turns only its own Block into a Bomb ("8 Block left"); check the face says so (Opus check round, 2026-10-02).
- Ka-pow!'s Set off reaches only the targeted enemy's Bombs, and nothing on the card says so; a seat aimed it at a Gas Bomb expecting the Fog's Bomb to go off (w18 lane 2, 2026-10-03).
- Between the act-3 boss's forms, the board shows no enemy and targeted cards are refused ("every enemy is dead or waiting to revive") (Opus check round, 2026-10-02).
- Seat page: Cycle of Seasons' trigger damage prints on the line of the card that changed Varka's element, and Cycle's own line reads "Nothing this page can count landed off it" (Varka smoke seat, 2026-10-02).
- Seat page: a dead Decimillipede segment waiting to Reattach is not on the wire (`BuildBattleState` sends only living enemies), so no page shows its revive countdown; send the body and its countdown (control seats, Ironclad and Necrobinder, 2026-09-26).
- Seat page: orb passives and evokes at the start and end of a turn are narrated nowhere (a Frost evoked by a Lightning Rod channel read as unexplained Block); `ResolutionLedger` files card plays only (control seat, Defect, 2026-09-26).
- `EB-802` `understudy/twolane_frames.py` may carry the PrintWindow clip `frames.py` fixed; route it through the same capture, and make a frame-reading row refuse `complete: false`.
- `EB-799` `vendor/STS2_MCP/STS2_MCP.csproj` ignores `klee-mod/local.props`, so a bare `dotnet build` of the bridge fails in a worktree; read `local.props` (until then pass `-p:STS2GameDir=...`).
- `EB-489` bound the bridge's main-thread hop so one stalled frame cannot hang `/api/v1/singleplayer` for the life of the process.
- `EB-391` the `rest` verb sometimes fails its first call on an open rest site ("Rest site room is not open"); game-side race.
- Blind seat: the first rest at a rest site printed "Took: Rest." with "error Rest site room is not open" and still counted an action (Furina seat, 2026-09-25).
- `EB-208` the seed ledger ships empty: run the Klee three-body seed hunt and record the first entries.
- `EB-212` stage and seal real matched-telegraph pairs (identical but for the enemy intent) under `understudy/battery/pairs/`.
- `EB-193` `game_ref/role_tempo_canon.json` predates the int-var reader fix; regenerate it (46 cards gain `has_body`).
- `EB-667` the Smith shows no upgrade for Ultimate Strike; its numbers are published nowhere the repo reads.
- `EB-71` no committed sheet prints `sly_autoplay`, so the `CardKeyword.Sly` rail has never run in game; whoever prints the first one checks it live.
- Seat page: Ka-pow!'s own damage is not printed when its target dies to its Bombs, and the hits of a fight-ending Rapid Fire are skipped.
- Seat glossary: the Bomb entry's "Only Vulnerable and the HP cap move it" and the Set off entry's "A random one picks a Bombed enemy first" read as unclear to a seat.
- `scenario run` cannot start on a lane whose profile holds a saved run: the relaunched game resumed the old boss fight and the menu never became ready (lane 1, 1336 run-history files, 447 s wait).
- Lane 1 embark `20260929-145523` was never reverted (all its ledger rows APPLIED, pid 27116 still up at `game_over`) although the seat's teardown was run; find why before relying on `seat.py` teardown. `embark` now refuses a lane with a live un-reverted launch.
- Drowning Beacon's "Bottle" option promised a Glowwater Potion that a base Ironclad seat never received with a slot free (2026-10-01 baseline, `review/records/base-sonnet-baseline-2026-10-01.md`). Not the mod: `DrowningBeaconMirror` matches the decompiled base event clause for clause (a `RewardsCmd.OfferCustom` potion reward), and Glowwater has no pickup or ethereal behaviour; the Varka seat's "vanished" Power Potion and Glowwater were drunk by the act-1 seat in the Waterfall Giant fight (godot log 20261001-203053, `using potion POWER_POTION` / `GLOWWATER_POTION`). Left: trace the bridge on the event's custom reward screen (is it shown, or left behind on `proceed`).
- The bridge does not show the order enemies act in; it decided a base Silent win at 18 HP (same record). Print it when the game exposes it.
- Bridge `ModeLabels`/`RecordChoice` still carry the sheet's literal numbers for mode faces; read them from the card's vars instead.

## Sim and measurement (Balance stage; nothing here runs on a prototype)
- The tier-0.5 Aeonglass (`tier05/content/act3_pool.yaml`) lacks Withering Presence, the growing Strength ramp, Wither upgrades and Artifact, and its Ebb is a stale 22; it cannot test this boss (Aeonglass audit, 2026-10-01). Port from `docs/current/dossiers/enemies/aeonglass.md` when a kit reaches Balance.

- `EB-195` (waits for a kit at Balance, legacy cleanup pick 5; on the current kits) the next re-baseline window: one twelve-arm table carrying the HP moves, the `POLICY_VERSION` bump for `PILOT_BURST_DIVISOR`'s removal, `EB-255` and `EB-810`.
- `EB-255` `archetype_shares` excludes starters by rarity, so 13 starter rows read back as drafts; exclude by membership inside `EB-195`'s bump.
- `EB-810` the sim's act-2 Louse has no Curl Up 14; wire it inside `EB-195`'s bump.
- `EB-241` `Card.is_junk` is rarity-only; make it type- and namespace-aware at the Kokomi fold, with that fold's re-baseline.
- `EB-32` the pilot block-panic rung; lands under its own `POLICY_VERSION` bump and window.
- `M13` `ROUTE_REGRET_MARGIN` has no derivation (Option D, no margin, stands); draft the slate and build `C2` (`review/records/regret-margin-registration-2026-08-12.md`).
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).
- The pilot heuristic (`tier0/pilot/policy.py`) does not price the full-stage Bow, and it still counts an arrival act.
- Legacy cleanup stage 6: two shipped leftovers stay in every generated card because removing them changes the emitted C# of current rows, which the stage ruled byte-identical: the header line `Upgrade deltas come from docs/<character>-upgrades.yaml` (deltas come from the row now; `gen_klee_cards` source header), and the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, the codegen's `spotlight_calc_rider` / `spotlight_block_rider`), the identity since stage 5. Drop both in one regen with a deploy check.
- Legacy cleanup stage 6 left the sim's shipped-kit machinery unreachable but in place: the Charge, Burst and Fanfare meters, the Kurage summon pulse, the Garment, Muster (`conscript`), the Salon, Encore, the Spotlight and the shipped Bomb detonation, with their ops, powers and constants (`tier0/engine/*`, `tier0/constants.py`, `tier05/draft.py` pricing, the `burst_max` / `fanfare` fields in `tier0/content/characters/*.yaml`); delete them at Balance with a re-baseline.
- `tier05.draft.ROSTER_ARCHETYPES` still names the shipped archetypes (salon, spotlight, ...) and no current row carries an archetype tag, so the drafter's archetype and core-complete terms are inert on the current kits; tag the rows or retire the terms at Balance.
- `tools/card_connectivity_report.py` does not know the current kits' Plan, Stage and overhaul ops; its row-classification test is `xfail(strict)` until the vocabulary covers them.

## Parked: start only when the named trigger fires

- `EB-70` the starter-offer retune (`EB-27p`); wakes when a kit's design sweep reaches the Wings / Little Hexenzirkul class (R134).
- `EB-80` Kokomi prevention-on-curve review; wakes if a Kokomi playtest shows she needs more warding.
- `EB-33/34/35` repricing exhibits (The Gallery Stirs 0.0 at offer, Vulnerable as a flat debuff, no defensive term in `_reaction_value`); wake when the `_static_power` repricing session convenes.
- `EB-651` a doubled `The other side` heading seen once and not reproduced; wakes on a sighting carrying the page sha.
- `EB-12` `bridge_unreachable` with the game alive, seen once; wakes on a second observation (`hangwatch` now classifies it).
- `EB-15` the seed's `lobby` route is unreachable in standard singleplayer; wakes with a Custom run or a hosted lobby.
- `SKIP-10.9` mechanics the sim does not model, promoted only on demand. Enemy: Back Attack, untargetable Burrow, Ethereal/Hex auras, pick-your-poison curses, damage caps (Hard to Kill, Plating, Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor powers, Soul Siphon stat theft, Blessed Antler, Philosopher's Stone. C# with no sim twin: the deferred-settle machinery (`SpotlightSystem`, `CurtainCallPowers`, `FurinaResources`) and per-dealer reaction windows (R1).
