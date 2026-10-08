# BACKLOG

Open engineering work, one line each. No required fields and no new ids: add
an item as a plain line, and delete it in the commit that builds it. An item
that already had an `EB-` id keeps it so old citations resolve. Picks for
[USER] go in `QUEUE.md`; kit design work is in each kit's brief and `STATE.md`.
Keep a line to the defect and its file; the reasoning goes in the commit that
closes it.

Closed items are in git. The last copy in the old four-field form, with
every built row, is `git show 2b73880a:docs/current/BACKLOG.md`; the rows that
closed on 2026-09-08 are at tag `backlog-archive-2026-09-08`; older ones at tag
`pre-simplification-2026-08-06`. The dated, round-cited copy of the lines below
is `git show bf073df4:docs/current/BACKLOG.md`.

## Kits and display (the mod)

- Off-character kit cards, base-game faithful (resources work for anyone and their gauge appears on first gain, like the Regent's Stars and Osty): Furina's Drain, Repay and Fanfare, Kokomi's Plans and Kurage, Varka's Oath. Each is done when its kit reaches Balance; Klee is done.
- Art owed, Klee: Forbidden Fun, It Wasn't Me!, Lisa's Treats, Red Knight, Finders Keepers, Klee Can Explain!, Damage Report, Albedo — Dust of Purification (its plan row is re-pointed from Tectonic Tide's Albedo Wish splash, not yet fetched), Up in Smoke!, Behind Jean's Desk, Kitchen Alchemy, Cover Your Ears!; the two status-package Powers borrow Party Poppers' and Spark Knight's badges.
- Art owed, Kokomi: Kelp Wall, Tidecleanse, Sea Glass Harvest, Turning Tide, Flotsam Surge, Abyssal Salvage and the Sea Glass token; Abyssal Salvage borrows the Princess of Watatsumi badge.
- Art owed, pool completion: the 14 new rows and the three new Ancients (Alice's Masterpiece, Divine Strategy, Center of Attention).
- Art owed: Durin — Principle of Purity wears Binary Form's picture (`art_of`); the three Purity powers borrow Binary Form's badge.
- Durin, Principle of Purity's turn-start Pyro hit (`PurityStrikePower`) shares `AfterPlayerTurnStart` with Melody Loop's Hydro, Herald of Frost's Cryo and Surprise Dispatch's roll, so the mod gives it no order where the sim runs it after Melody Loop; stage it into its own broadcast if a seat sees the two disagree.
- Klee finish-line batch, pinned headless only; watch in game and through the bridge: Dodoco Tales' opening Sparks (and the Spark row naming the relic), Finders Keepers' draw trigger, Confiscated playing as a Status (drag-to-play, frame, Klee Can Explain! / Kitchen Alchemy taking it), Mine, All Mine!'s Mine landing on the enemy its hit killed.
- Pool completion: Divine Strategy's now-line, Center of Attention's free Spend and the two co-op cards (Tactical Relay, Kurage's Mercy) are pinned headless only; watch them in game and through the bridge.
- Varka has no Ancient card: Darv's Dusty Tome hands him an upgraded Four Winds' Ascension through BaseLib's `ITomeCard` (the row's `dusty_tome` tag) until one is designed; delete the tag with it.
- Verify Boreas's Fang saved starter element survives save/reload (`Relics/VarkaStarterKnight.cs`, a BaseLib `SavedSpireField`; no test exercises a real serialize/deserialize, so the Fang and Knight's Commission keep their deck fallback until then).
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- Varka's element-switch hover (`ArmKeywordTips.ForElementSwitch`) rides only his own `proto_vk_` rows; a Universal or another kit's card he drafts that applies an Oath element switches him too and says nothing.
- Varka's element-switch hover, the left-element icon (`OathLeftPower`), the Fang's turn-one element, Windborne Resolve and Weathervane's start-of-turn grid (also in co-op) are still unconfirmed in game and through the bridge; the next Varka seat record says whether each was seen.
- Varka's screen: Artifact silently eats Frozen, Weak and Electro-Charged's Poison, and the reaction text should say "blocked by Artifact"; Bottled Gale with no aura on the board does nothing and nothing warns; Diluc printed 9 against the card's 6 with no reason shown (`review/records/varka-combo-round-2026-10-05.md`, items 4-6).
- Kaeya — Frostgnaw (`ProtoMcKaeyaFrostgnaw.cs`, the shared Mondstadt card) printed 12 against a written 8, and its own Superconduct's Vulnerable (the tip says it "applies before this hit") did not multiply the hit; trace the order and the printed number.
- Four Winds' Ascension's Oath hit leaves an aura but gains no Oath, where Barbara's hit does; nothing printed says whether that is the rule.
- Card reward card off screen but still selectable by controller (user, co-op). Cause not found; `Diagnostics/RewardRowProbe.cs` writes a "reward row OFF SCREEN" WARN to godot.log naming the card and where its holder and body are; read that line after the next sighting and fix from it.
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning, where a Swirl or Crystallize on a burning enemy consumes the held Pyro and Burning keeps ticking; and Dendro ported as ruled (the non-reacting pairs, the Core rules and their previews), tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Show the amplifier: a Melt or Vaporize prints no factor on the face or in the seat log (Rosaria's Melt printed "Deal 15" from a written 9; "Vaporize on X" with no x1.5; Klee's log printed "nothing to amplify" beside a hit multiplied by 1.75); a hit carrying an element chosen at play (Four Winds' Ascension, Northwind Avatar) previews no amplifier either (multiplier pinned by `A_current_element_hit_amplifies_like_any_hit`).
- Kokomi text: the Neow bundle's Plan gloss omits "instead of playing it now"; the Casket tip does not say it ignores a debuff from a reaction set off by its own hit.
- Kokomi's Plan list prints a waiting Plan's damage without the target's Vulnerable: a queued card is in no pile, so its numbers never refresh; `KokomiPlan.QueueRow` could send the front-target-folded number (`PlannedDamage(FrontEnemy, ...)`) for front-aimed Plans; `WrittenFrontDamage` has the same gap.
- Kokomi: Smoggy ("you can only play 1 Skill per turn") refuses writing a Plan once a Skill is played; neither Smoggy's line nor the Bake-Kurage tip says writing a Plan counts as playing the card.
- Kokomi: the cut cards' engine clauses (Tide Chart's, Song of Pearls' power, Scout Ahead's clause) stay in both engines with nothing granting them; delete them (the brief's cleanup pass says BACKLOG lists them).
- Furina: a Spend card silently plays its plain side when her Fanfare cannot pay the Spend.
- Furina: rename the four mismatched guest ids in one regen, moving their art keys and `KNOWN_MISSING` entries with them, after [USER]'s run and never mid-save.
- Co-op rest site: Mend on the partner did not end the rest action, so Smith was still offered.
- `EB-807` `Unknown RelicModel ID: RELIC.KLEEMOD-TAMANOOYAS_CASKET` once per boot is the owner's `progress.save` DiscoveredRelics list naming the retired relic (non-fatal); no alias is left in code. Harmless; drop the id from the save or let it be.
- `EB-798` `ProtoKkBreakwater` is offered Nimble but Nimble pays it nothing (its only Block is the Plan's); planned-only Block is not `GainsBlock`, in both engines and `lint_enchant_parity`.
- `EB-677` Glam's Replay on a timed card (Kyouka) runs it 4 turns at +4, not 2 at +8, and no face says which; needs an emitter change that gives the rule a tip surface, plus a taste call on which rows carry it.
- `EB-65` the four Furina power badges draw shrunk card portraits; they want badge-kind icons like Klee's.
- `EB-803` `proto_mc_kaeya_frostgnaw` wears Cold-Blooded Strike's named art (only Frostgnaw's own pick is owed); confirm `klee/relics/dodoco_tales.png` is packed on the next pck build.
- `EB-53` end-of-turn docket: capture the co-op half (`C6`) on the two-seat runtime (`embark --coop`) and isolate the electro (Oz) leg.
- `EB-296` / `EB-300` controller: a live walk that the Kokomi pet is targetable by D-pad and mouse, and that the hand is reachable after a custom-target card.
- `EB-159` [USER] at the machine: listen for the modded player's death sound (`set_hp player 1`, end turn into a hit).
- `EB-38` [USER] at a shop: the spine-less character portrait idles (the rest-site half is seen).
- `EB-160` verify a live locale switch: the injected loc tables survive it, or a `LocException` names the seam.

### Klee faces (under the freeze: fix on `klee-next`)

- The printed Bomb number leaves out Boom Badge's doubling (also after Boom Badge+ is played), Weak, Durin's Dark +6 and Hardened Shell's cap; the test relic's "Bomb 6" shows as 10 on her first turn with no word why.
- Big Badda Boom: "then damage equal to what your Bombs dealt" does not say whether Bombs set off earlier in the turn count, counts only damage past Block, and it is unclear whether Boom Badge doubles it.
- Treasure Map plays and spends its Energy with no Set off card in the discard pile, and its face does not say it needs one.
- Jumpy Dumpty prints "place a Mine 3 on ALL enemies" but refuses to play without a named target (it aims the first Bomb); the face does not say a target is needed.
- Ka-pow!'s Set off reaches only the targeted enemy's Bombs and seemed to set off only the oldest Bomb once (check the code); nothing on the card says so.
- Mine text does not say whether the enemy's other Bombs go off with it, or that it consumes the aura set for the big Bomb.
- Jean+ is switched off when Dodoco+'s Mine goes off on the enemy's turn ("a Bomb went off last turn"); the face does not say so.
- Perfect Timing's replay did not visibly fire when its first Set off killed the target.
- Return to Sender turns only its own Block into a Bomb; check the face says so.
- "Sorry, Jean..." removes the oldest Bomb without saying so.
- Boom Badge's Retain reads as if the doubling carries over; "Witch's Homework" and "Witch's Homework II" read alike in hand lists.
- Chained Reactions' +3 missed a two-Bomb Ka-pow! set-off (trace); Durin's start-of-turn tick skipped one fight (Fogmog, trace).
- The Spark line vanishes at 0, and Snecko Oil's added Spark costs are unexplained; a Mine going off printed "gives 1 Spark" plus Pounding Surprise's "+1 Spark" but the seat counted +1.
- Wait For It... printed "Nothing ... landed" on paying turns; Weak shows different Pyro numbers on card and board; the Melt preview reads as if the whole Bomb pile multiplies.

## Seat page (the blind seat's view: `blindplay_*` render and the bridge)

- No receipt says what a Set off detonated, so a Set off that kills reads as a vanished Bomb. Needs a detonation log in the mod like ReactionLog, a bridge read and a page line such as "Sizzle set off Corpse Slug: Mine 3 (3), Bomb 16 (2, killed it). Nothing jumped."
- Incoming ignores Mines that fire first and Look Out!'s Block from them; the "Put Mine N on ..." lines after Big Badda Boom read as five Mines from one Bomb.
- Ka-pow!'s own damage is not printed when its target dies to its Bombs, and the hits of a fight-ending Rapid Fire are skipped.
- The glossary's Bomb entry ("Only Vulnerable and the HP cap move it") and Set off entry ("A random one picks a Bombed enemy first") read as unclear.
- The resolution rows do not say which hit was which (Four Winds' Ascension+ read "2, 3, 9, 36" unlabelled); needs a source label per hit on `ResolutionLedger`'s wire and in `blindplay_render`'s hit rows.
- Draws made by effects print nothing (Eye of Stormterror on a Swirl, Static Field, Tempest Charge); list cards drawn outside the turn's draw in "Since last page".
- Cycle of Seasons' trigger damage prints on the line of the card that changed Varka's element, and Cycle's own line reads "Nothing this page can count landed off it".
- Oathsworn Strike's line printed "Deals 29" and hit 31 on a Vulnerable target; the hand preview folds no target's Vulnerable, and the page does not say so.
- An autoplaying relic (the Earring) plays the first turn with no line saying what it will play or played.
- Copy numbers renumber after a play, so "Frantic Escape (2)" picked the other copy; name copies by something stable (cost or upgrade) or warn on renumber.
- Open the Casket was tried from hand while it sat in the discard pile; the page should print the pile it is in.
- The Tamakushi Casket printed "(1)" between fights; its counter is combat-only (`TamakushiCasket.ShowCounter`), so the page reads `DisplayAmount` before combat state clears.
- A Furina seat never saw her own Frail or Dexterity loss printed, so Defend at 1-2 was unexplained; check the brief page lists the player's debuffs.
- The Weak gloss says it cuts a Bomb's damage (it does not: a Bomb carries the target's modifiers only).
- The Tainted per-hit note still gives two readings for a multi-hit, the same double count the Weak note had before #650.
- Pocket Match's play log listed 3 and left out its own 5 damage.
- Tender prints only "Tender 3"; Fireworks Finale's "Written: 5" does not name the Strength loss that lowered it; Spiny Toad's Thorns showed on turn 1 only.
- A Companion summon's ticks (Kamisato Ayaka's Soumetsu) print only inside Kokomi's Plan block (`summon_hits`); a Furina or Klee page shows them nowhere.
- A companion's end-of-turn hit (Kaeya, Oz) names its body only when it reacts; a plain hit is on no wire, because `ResolutionLedger` files card plays and a power's damage is not one.
- Orb passives and evokes at the start and end of a turn are narrated nowhere; `ResolutionLedger` files card plays only.
- The Neow bundle page printed one pack's rows jumbled (a line missing, its text under another card). Not reproduced; needs the raw `bundle_select` state from such a screen.
- The Trial's first page printed only "Proceed", and `proceed` was then refused against its Accept / Reject options (the page read the event mid-transition).
- The first rest at a rest site printed "Took: Rest." with "error Rest site room is not open" and still counted an action (see `EB-391`).
- Co-op: the "What you played this turn" log lists the partner's cards as your own; players are named "Test Host"/"Test Client 1"; the reaction glossary ignores the partner's element; a contested chest pick is not announced; `wait` after a finished fight reports nothing while the reward is up; a play at an enemy the partner just killed is silently retargeted.
- Enemy rules not on the page: Surrounded (which arm turns you; the debuff text only says "use targeting cards to change your orientation").
- Enemy rules not on the page: Flutter's "50% less damage from Attacks" halved Bomb damage in one run and not in two others; say whether it applies to a Bomb.
- Enemy rules not on the page: the final boss's Enrage (Strength per Skill), which the page does not warn about.
- Enemy rules not on the page: a boss curse's duration and growth.
- Owl Magistrate's "Soar" intent has no definition on the page, so a lethal turn reads as safe.
- Knowledge Demon's Curse of Knowledge choice shows Disintegration as "cost 0, status"; a seat took it for a card, not a permanent 6-a-turn debuff.
- Louse Progenitor's intent under the player's Weak read "folded Strength and Weak: 14 on the move and 14 after" and the Weak seemed to do nothing; check the fold and the line.
- A dead Decimillipede segment waiting to Reattach is not on the wire (`BuildBattleState` sends only living enemies); send the body and its revive countdown.
- Killing a reviving boss mid-turn (Test Subject) makes it vanish from the page with no notice; between the act-3 boss's forms the board shows no enemy and targeted cards are refused.
- The bridge does not show the order enemies act in; print it when the game exposes it.

## Harness, bridge and tools

- Bridge: the enchant chooser (relic Kifuda, 'Choose 3 cards to Enchant') never closes; `confirm_selection` appends the picks again (3→6→9→12), and cancel is refused, so a seat stalls in the shop.
- Shop card removal: after the first card is picked the screen refuses a re-pick and offers only confirm or skip; check whether the base screen allows a deselect and the bridge lacks the verb.
- Bridge: Jumpy Dumpty refused without a target, a Durin chooser answered "still opening", and Mawler died at end of turn with no printed cause.
- Drowning Beacon's "Bottle" potion reward: trace the bridge on the event's custom reward screen (is it shown, or left behind on `proceed`). The mod matches the base event.
- Bridge `ModeLabels`/`RecordChoice` still carry the sheet's literal numbers for mode faces; read them from the card's vars instead.
- Soak: `soak_screens._escape` answers the Crystal Sphere with `crystal_sphere_proceed`, which the game refuses while divinations are owed; spend them first as the seat page's `reveal` does (`blindplay_shape.sphere_reveal_action`).
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- Fight telemetry: log Witch's Homework II's run-long Bomb size (`HomeworkGrowth`) per fight, so its prediction can be graded.
- `scenario run` cannot start on a lane whose profile holds a saved run: the relaunched game resumed the old boss fight and the menu never became ready.
- An embark was never reverted (all its ledger rows APPLIED, the game still up at `game_over`) although the seat's teardown was run; find why before relying on `seat.py` teardown. `embark` now refuses a lane with a live un-reverted launch.
- `test_local_tester` is flaky: it failed once and passed on re-run with no change.
- `EB-802` `understudy/twolane_frames.py` may carry the PrintWindow clip `frames.py` fixed; route it through the same capture, and make a frame-reading row refuse `complete: false`.
- `EB-799` `vendor/STS2_MCP/STS2_MCP.csproj` ignores `klee-mod/local.props`, so a bare `dotnet build` of the bridge fails in a worktree; read `local.props` (until then pass `-p:STS2GameDir=...`).
- `EB-489` bound the bridge's main-thread hop so one stalled frame cannot hang `/api/v1/singleplayer` for the life of the process.
- `EB-391` the `rest` verb sometimes fails its first call on an open rest site ("Rest site room is not open"); game-side race.
- `EB-208` the seed ledger ships empty: run the Klee three-body seed hunt and record the first entries.
- `EB-212` stage and seal real matched-telegraph pairs (identical but for the enemy intent) under `understudy/battery/pairs/`.
- `EB-193` `game_ref/role_tempo_canon.json` predates the int-var reader fix; regenerate it (46 cards gain `has_body`).
- `EB-667` the Smith shows no upgrade for Ultimate Strike; its numbers are published nowhere the repo reads.
- `EB-71` no committed sheet prints `sly_autoplay`, so the `CardKeyword.Sly` rail has never run in game; whoever prints the first one checks it live.

## Sim

- Kokomi status batch: the stock sim pilot cannot read the next-hand Plans (Kelp Wall's count, Tidecleanse, Sea Glass Harvest, Turning Tide) or plan for statuses it has not drawn; their census rates are unread.
- Pool completion: run paper sec.7's sim checks on the built pools (`review/ruled/pool-completion-2026-10-01.md`): each of Kokomi's four decks within 10 points of Plan volume with the new Rares granted, and no new card taken from over 70% of offers or played in under 5% of the fights where it is held.
- Legacy cleanup stage 6 left the sim's shipped-kit machinery unreachable but in place: the Charge, Burst and Fanfare meters, the Kurage summon pulse, the Garment, Muster (`conscript`), the Salon, Encore, the Spotlight and the shipped Bomb detonation, with their ops, powers and constants (`tier0/engine/*`, `tier0/constants.py`, `tier05/draft.py` pricing, the `burst_max` / `fanfare` fields in `tier0/content/characters/*.yaml`); delete them (the measurement ruling's pick 3(a)).
- `tier05.draft.ROSTER_ARCHETYPES` still names the shipped archetypes (salon, spotlight, ...) and no current row carries an archetype tag, so the drafter's archetype and core-complete terms are inert; retire the terms with the machinery above.
- Legacy cleanup stage 6: one shipped leftover stays in every generated card because removing it changes the emitted C# of current rows: the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, the codegen's `spotlight_calc_rider` / `spotlight_block_rider`). Drop it in one regen with a deploy check, riding Klee's next promotion PR.
- The old shipped `BombPower.cs` is placed by no card (its keyword row, `KleeKeywords.Bomb` and `includesBombRules` went in #972) but 9 C# test files, `PlayTelemetry` and two relics' listener bus still read it; move those readers and delete it.
- `tools/card_connectivity_report.py` does not know the current kits' Plan, Stage and overhaul ops; its row-classification test is `xfail(strict)` until the vocabulary covers them.
- `EB-241` `Card.is_junk` is rarity-only; make it type- and namespace-aware.
- `EB-32` the pilot block-panic rung; lands under its own `POLICY_VERSION` bump and window.
- `M13` `ROUTE_REGRET_MARGIN` has no derivation (Option D, no margin, stands); draft the slate and build `C2` (`review/records/regret-margin-registration-2026-08-12.md`).
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).
- The pilot heuristic (`tier0/pilot/policy.py`) does not price the full-stage Bow, and it still counts an arrival act.

## Parked: start only when the named trigger fires

- Parked by the measurement ruling (2026-10-05: a Balance kit is measured on the real game, so the sim re-baseline is not its gate); they wake only if the sim becomes a gate again:
  - `EB-195` the next re-baseline window: one twelve-arm table carrying the HP moves, the `POLICY_VERSION` bump for `PILOT_BURST_DIVISOR`'s removal, `EB-255` and `EB-810`.
  - `EB-255` `archetype_shares` excludes starters by rarity, so 13 starter rows read back as drafts; exclude by membership inside `EB-195`'s bump.
  - `EB-810` the sim's act-2 Louse has no Curl Up 14; wire it inside `EB-195`'s bump.
  - The tier-0.5 Aeonglass (`tier05/content/act3_pool.yaml`) lacks Withering Presence, the growing Strength ramp, Wither upgrades and Artifact, and its Ebb is a stale 22; port it from `docs/current/dossiers/enemies/aeonglass.md`.
- `EB-70` the starter-offer retune (`EB-27p`); wakes when a kit's design sweep reaches the Wings / Little Hexenzirkul class (R134).
- `EB-80` Kokomi prevention-on-curve review; wakes if a Kokomi playtest shows she needs more warding.
- `EB-33/34/35` repricing exhibits (The Gallery Stirs 0.0 at offer, Vulnerable as a flat debuff, no defensive term in `_reaction_value`); wake when the `_static_power` repricing session convenes.
- `EB-651` a doubled `The other side` heading seen once and not reproduced; wakes on a sighting carrying the page sha.
- `EB-12` `bridge_unreachable` with the game alive, seen once; wakes on a second observation (`hangwatch` now classifies it).
- `EB-15` the seed's `lobby` route is unreachable in standard singleplayer; wakes with a Custom run or a hosted lobby.
- `SKIP-10.9` mechanics the sim does not model, promoted only on demand. Enemy: Back Attack, untargetable Burrow, Ethereal/Hex auras, pick-your-poison curses, damage caps (Hard to Kill, Plating, Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor powers, Soul Siphon stat theft, Blessed Antler, Philosopher's Stone. C# with no sim twin: the deferred-settle machinery (`SpotlightSystem`, `FurinaResources`) and per-dealer reaction windows (R1).
