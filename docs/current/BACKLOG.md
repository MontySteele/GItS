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

- Varka has no Ancient card: Darv's Dusty Tome hands him an upgraded Four Winds' Ascension through BaseLib's `ITomeCard` (the row's `dusty_tome` tag) until one is designed; delete the tag with it.
- Verify Boreas's Fang saved starter element survives save/reload (`Relics/VarkaStarterKnight.cs`, a BaseLib `SavedSpireField`; no test exercises a real serialize/deserialize, so Knight's Commission keeps its deck fallback until then).
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- Varka's element-switch hover (`ArmKeywordTips.ForElementSwitch`) rides only his own `proto_vk_` rows; a Universal or another kit's card he drafts that applies an Oath element switches him too (the open Oath) and says nothing. Varka element identities, 2026-10-01.
- The Varka sim pilot (`tools/varka_expansion_sim.py`, the stock `generic` scorer) plays Short Circuit last at 0 Energy and never plays Chain Lightning after a discard (0 of 167, element identities' probe), and does not price the cards Violet Storm throws away; until it sequences discard into Energy and the discount, the sim cannot read Electro's middle.
- Varka's element-switch hover and the left-element icon (`OathLeftPower`) are untried in game and through the bridge: watch both at the next Varka seat round.
- `tools/retired_ids.py` has no Varka owner, so the five rows element identities retired (Updraft, Pressure Front, Unfurled Banner, Four Winds' Accord, Unbroken Tide) are aliased into Klee's pool in `docs/retired-card-ids.yaml`; give Varka an owner and pool there (`gen_retired_card_aliases.POOLS`) once `VarkaCardPool` builds in every configuration the aliases do.
- Weathervane's start-of-turn element grid is untried through the bridge and in co-op: watch it at the expansion's first seat round.
- Varka's Oath tip says "1 of each, per card", which a seat read as one per element; both engines credit applying and Swirling separately (`VarkaOathLedger.TryCredit`, `varka_oath.credit`), so Northwind Avatar on an aura of the current element gains 2. The tip wants to say applying and Swirling each count once per card (Varka Oath round, lane 2 act 2).
- Seat page: the Neow bundle page printed one pack's rows jumbled (Oathsworn Strike's line missing, its text under Rising Gale; Varka Oath round, lane 2 act 1). Not reproduced: the bridge strips newlines from each face and the render prints each bundle's cards in wire order; it needs the raw `bundle_select` state from such a screen.

- Furina Stage: the end-of-turn preview listed a trio act twice ("Crabaletta: 10 to a random enemy, twice", fight 4 turn 2 after Double Casting+ gave two Ushers under Ousia; "Chevalmarin 2 to ALL" twice, fight 5 turn 1 after Gala Premiere and a front-seat Wriothesley) while the log shows one act; both on a full stage, which is when `Forecast` and `EndOfTurnActs` add Full House's repeats. Not reproduced: `FurinaStage.Forecast` on both boards, built headless ([Crabaletta, Usher, Usher] and [Wriothesley, Usher, Chevalmarin]), lists one act each, so something live adds the repeat; it needs the `furina_stage.forecast` snapshot and her powers from such a turn (Furina seat, 2026-09-28). A third sighting 2026-09-29 (Furina run FS3EL3M3NTS4, act 1): the preview said Neuvillette "8 Hydro to ALL, twice" and the second act "could not pay" Not a skipped payment: both forecasts pay each Full House repeat on the copy before counting it (pinned 2026-09-29, board "full house, the repeat cannot pay"); the record's bars (Neuvillette 11, then 3 paid each sweep) put him at 5, where the forecast lists one act, so the doubled line came from somewhere else.
- Reward screen: `proceed` with an unclaimed gold row drops the gold with no warning (two seats, 2026-09-28/29).
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning, where a Swirl or Crystallize on a burning enemy spends the held Pyro and Burning keeps ticking; and Dendro ported as ruled (the non-reacting pairs, the Core rules and their previews), tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Co-op seat page: the "What you played this turn" log lists the partner's cards as your own; players are named "Test Host"/"Test Client 1"; the reaction glossary ignores the partner's element; a contested chest pick is not announced; `wait` after a finished fight reports nothing while the reward is up; a play at an enemy the partner just killed is silently retargeted (co-op round, 2026-09-27).
- Seat page: the play log prints "Put Bomb 1" where the badge shows the placed size, and the Weak gloss says it cuts a Bomb's damage (it does not: a Bomb carries the target's modifiers only) (co-op round, 2026-09-27).
- Kokomi text: the Neow bundle's Plan gloss omits "instead of playing it now"; the Casket tip does not say it ignores a debuff from a reaction set off by its own hit (Kokomi core seat, 2026-09-27).
- Co-op rest site: Mend on the partner did not end the rest action, so Smith was still offered (co-op round, 2026-09-27).
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- Seat page: a companion's end-of-turn hit (Kaeya, Oz) names its body only when it reacts; a plain hit is on no wire, because `ResolutionLedger` files card plays and a power's damage is not one (wave-3 Klee lane 2b, 2026-09-26).
- Furina Stage: a hit from a debuff on her (Knowledge Demon's Disintegration) reaches the stage log as "damage no enemy dealt"; `ModifyHpLostBeforeOsty` hands no power source, so only a card in hand (Burn, Wither) is named (wave-3 Furina lane 4, 2026-09-26).
- Furina Stage: Soliloquy's bonus is missing from the preview of a Spend that empties the stage (Bravura "(Deals 7 damage)" hit for 14); the preview would have to know the Spend takes the last seat and that no Bow reader (Thunderous Applause's summon, A Five-Century Act's return) refills it (Solo seat, 2026-09-26).
- Furina Stage: the Summon keyword tip still says "the front one Bows first", which is untrue while Wriothesley holds the front (the performer behind him Bows); his card face covers only his own arrival (#769, 2026-09-29).
- Furina Stage: the end-of-turn forecast ("you take N") folds nothing the acts will cause on the enemy side -- a Frozen or Superconduct from an act, a stun from stripped Block (Tunneler's Burrowed) -- so it overstates; it needs the acts' reactions predicted per body (lane 2, 2026-09-26).
- Furina Stage: killing a reviving boss mid-turn (Test Subject) makes it vanish from the page with no notice, and the end-of-turn acts print "nothing landed" (fade round, 2026-09-29).
- Furina Stage: the end-of-turn "you take N" ignores the player's own reduced damage under an enemy's Intangible turn, and a Spend card silently plays its plain side when the back performer cannot pay (fade round, 2026-09-29).
- Frozen: the tip says the next action deals 50% less, but a Shatter ends the freeze first, so the player's own Shatter spends the halving (Furina seat, 2026-09-29: Rosaria then Chevreuse's Ring, and the Beetle hit for 18); the tip wants one clause on Shatter.
- Furina Stage: after Thorns killed the lone front Usher, Grand Deluge "summoned Chevalmarin" on the emptied stage; nothing on the card or the stage says a Fanfare gain on an empty stage summons (Furina seat, 2026-09-29, Spiny Toad).
- Furina Stage: a seat read the stage text as if back performers soak damage and spent Bottled Applause on the back one; only the front performer soaks (Furina seat, 2026-09-29).
- Kokomi: Smoggy ("you can only play 1 Skill per turn") refuses writing a Plan once a Skill is played; neither Smoggy's line nor the Bake-Kurage tip says writing a Plan counts as playing the card (Kokomi seat, 2026-09-29, Living Fog).
- `test_local_tester` is flaky: it failed once and passed on re-run with no change (2026-09-28).
- Once More! spends its Sparks and returns nothing, with no message, when the last Set off card has been shuffled back into the draw pile (the spend is by design, `KleeOverhaulLedger.ReturnLastSetOff`); the miss prints nowhere a seat can read (Klee full run lane 1, 2026-09-26).
- Big Badda Boom's "what your Bombs dealt" counts Block the Bombs removed in C# (`ElementalHit.Deal` returns the pre-Block hit) but HP only in the sim (`deal_damage_to_enemy` returns `hp_dmg`); the two engines disagree whenever the target has Block (found 2026-09-26).
- Shipped Furina's Encore buffer (FurinaResources.AbsorbDamage) rounds a fractional HP loss up; the engine truncates (found 2026-09-25).
- Beetle Juice's Shrink on an enemy prints "While is alive, you deal 30% less damage": the name is blank and it speaks in the player's voice (Klee seat, 2026-09-23).
- Rosaria's Melt on Klee's board printed "Deal 15" from a written 9, which no printed multiplier explains; show the reaction's factor on the face.
- Kokomi: engine pieces the halves rewrite left unused (`NextAttackDamage` with `NextAttackDamagePower`, which Battle Plan stopped using at R276 and no row applies, per the 2026-09-25 text pass; `BlockPerPlanThisMorning`, `plans_carried_out_this_morning`, the morning-damage tip; Song of Pearls' power and Scout Ahead's `DrawPerPlanAfter`, both cards cut 2026-09-29; Second Thoughts' `CancelLast` / `cancel_last_plan` and its `CancelledLine` bubble, cut 2026-10-01); delete them in C# and the sim.
- `EB-809` `KurageMemory.PriceText` prints bare `free` at price 0; print the derivation (`cost 0 x 3`) like every other price.
- `EB-808` a create-mode Muster never stamps its recruit's discount (`KokomiConscript.cs` `NoteMusterRecruit` is in the sacrifice branch only); stamp both branches.
- `EB-807` `Unknown RelicModel ID: RELIC.KLEEMOD-TAMANOOYAS_CASKET` once per boot: widen the retired-id alias register from cards to relics and arm-gated ids.
- `EB-805` a mode card's option title prints the sheet literal while the body folds the board (two numbers for one option); the title carries no number or folds through the same vars.
- `EB-801` six shipped power faces are over the 125-char ceiling (`BurstMeterPower`, `EncoreMeterPower`, `FanfareMeterPower`, `FurinaBurstMeterPower`, `SalonMemberPower` x2); a text pass (design work, main session) until `lint_text_conventions --shipped` names none.
- `EB-798` `ProtoKkBreakwater` is offered Nimble but Nimble pays it nothing (its only Block is the Plan's); planned-only Block is not `GainsBlock`, in both engines and `lint_enchant_parity`.
- `EB-677` Glam's Replay on a timed card (Kyouka) runs it 4 turns at +4, not 2 at +8, and no face says which; needs an emitter change that gives the rule a tip surface, plus a taste call on which rows carry it.
- `EB-65` the four Furina power badges draw shrunk card portraits; they want badge-kind icons like Klee's (art bill, rank 1 applied).
- `EB-803` `proto_mc_kaeya_frostgnaw` wears Cold-Blooded Strike's named art (swap the two Kaeya picks); confirm `klee/relics/dodoco_tales.png` is packed on the next pck build.
- `EB-53` end-of-turn docket: capture the co-op half (`C6`) and isolate the electro (Oz) leg. The two-seat runtime now exists (`embark --coop`, `operations/understudy-seats.md`); what remains is running the capture on it, and the Oz leg.
- `EB-296` / `EB-300` controller: a live walk that the Kokomi pet is targetable by D-pad and mouse, and that the hand is reachable after a custom-target card.
- `EB-159` [USER] at the machine: listen for the modded player's death sound (`set_hp player 1`, end turn into a hit).
- `EB-38` [USER] at a shop: the spine-less character portrait idles (the rest-site half is seen).
- `EB-160` verify a live locale switch: the injected loc tables survive it, or a `LocException` names the seam.
- The Big One's x4 stays armed when its Set off finds no Bomb, so a later Mine on the enemy turn can spend it.
- Kokomi pool extension ([USER] agreed 2026-09-29, defence census): move some Plan Block to Dusk or immediate Block (five of her nine Block cards are Plans, three land next turn), and replace The Clouds Like Waves Rippling with a real defensive Power.
- Klee: defence left as is ([USER] agreed 2026-09-29, defence census) unless [USER]'s next run says otherwise.
- Kokomi text (feed round 2026-09-29): the Tamakushi Casket does not say Open the Casket pays once a fight (it exhausts); cards with a now line and a Plan line (Shell of Sanctuary, Current Read, Kurage's Oath) read as doing both; template them with "or".
- Feigned Retreat's carry-out does not say which number paid: with Strength folded in at writing, the hurt 9 read as the printed 14 (Flex, Str 5) and a Kokomi seat reported the unhurt hit firing after a 9-HP loss (2026-09-29). Also, "lost no HP" is read as net HP (`KokomiPlan.UnhurtAmount`, sim twin `kokomi_plan` `damage_if_unhurt`), so a Mend between writing and morning reads unhurt.
- A reaction amplifier's payout is not printed: the seat log reads "Vaporize on X" with no x1.5 (Varka seat, 2026-09-29: Weak 4 -> 3 printed, 4 landed). A hit carrying an element chosen at play (Four Winds' Ascension and Northwind Avatar's current-element hit) previews no amplifier either; the multiplier is pinned by `A_current_element_hit_amplifies_like_any_hit`.

## Harness, bridge and tools

- Bridge: the enchant chooser (relic Kifuda, 'Choose 3 cards to Enchant') never closes; `confirm_selection` appends the picks again (3→6→9→12), and cancel is refused — a seat stalls in the shop (seat round 2026-09-26, wave3-furina-lane2).
- The Opus-seat path embarks with no action cap (`embark --max-actions` defaults to 0), so a hand-driven seat ran 279 actions; make `seat.py --opus-brief` print or run the embark with `--max-actions 120`.
- Seat page: the Tainted per-hit note still gives two readings for a multi-hit, the same double count the Weak note had before #650.
- Seat page: Pocket Match's play log listed 3 and left out its own 5 damage.
- Seat page: a Companion summon's ticks (Kamisato Ayaka's Soumetsu) print only inside Kokomi's Plan block (`summon_hits`); a Furina or Klee page shows them nowhere, and the stage's "acts will deal" preview leaves them out (Furina lane 2, 2026-09-26).
- Seat page: The Trial's first page printed only "Proceed", and `proceed` was then refused against its Accept / Reject options -- the page read the event mid-transition (Furina Solo seat, 2026-09-26).
- Furina Stage: the sim's `furina_stage.forecast` (tests only) does not count the cards in her hand that hurt her as her turn ends; the mod's forecast does since 2026-09-26 (`FurinaStage.HandTurnEndHits`).
- Soak: `soak_screens._escape` answers the Crystal Sphere with `crystal_sphere_proceed`, which the game refuses while divinations are owed; spend them first as the seat page's `reveal` does (`blindplay_shape.sphere_reveal_action`).
- Seat page: no screen prints the run seed or the ascension.
- Seat page: a dead Decimillipede segment waiting to Reattach is not on the wire (`BuildBattleState` sends only living enemies), so no page shows its revive countdown; send the body and its countdown (control seats, Ironclad and Necrobinder, 2026-09-26).
- Seat page: orb passives and evokes at the start and end of a turn are narrated nowhere (a Frost evoked by a Lightning Rod channel read as unexplained Block); `ResolutionLedger` files card plays only (control seat, Defect, 2026-09-26).
- `EB-802` `understudy/twolane_frames.py` may carry the PrintWindow clip `frames.py` fixed; route it through the same capture, and make a frame-reading row refuse `complete: false`.
- `EB-799` `vendor/STS2_MCP/STS2_MCP.csproj` ignores `klee-mod/local.props`, so a bare `dotnet build` of the bridge fails in a worktree; read `local.props` (until then pass `-p:STS2GameDir=...`).
- `EB-800` the five arm test properties disagree on `The_arm_ships_off` (four `Skip`, `FurinaStage` an `#if`); pick one convention and say which in `operations/prototype.md`.
- `EB-489` bound the bridge's main-thread hop so one stalled frame cannot hang `/api/v1/singleplayer` for the life of the process.
- `EB-391` the `rest` verb sometimes fails its first call on an open rest site ("Rest site room is not open"); game-side race.
- Blind seat: the first rest at a rest site printed "Took: Rest." with "error Rest site room is not open" and still counted an action (Furina seat, 2026-09-25).
- `EB-208` the seed ledger ships empty: run the Klee three-body seed hunt and record the first entries.
- `EB-212` stage and seal real matched-telegraph pairs (identical but for the enemy intent) under `understudy/battery/pairs/`.
- `EB-193` `role_tempo_canon.json` predates the int-var reader fix; regenerate it (46 cards gain `has_body`).
- `EB-667` the Smith shows no upgrade for Ultimate Strike; its numbers are published nowhere the repo reads.
- `EB-71` no committed sheet prints `sly_autoplay`, so the `CardKeyword.Sly` rail has never run in game; whoever prints the first one checks it live.
- Seat page: Ka-pow!'s own damage is not printed when its target dies to its Bombs, and the hits of a fight-ending Rapid Fire are skipped.
- Seat glossary: the Bomb entry's "Only Vulnerable and the HP cap move it" and the Set off entry's "A random one picks a Bombed enemy first" read as unclear to a seat.
- Seats share the coordinator's scratchpad, so a seat's notes file can hold an earlier seat's notes; give each seat its own notes path.
- Two lanes embarked at the same moment: the second lane's game never came up (its port refused every call) until a teardown and re-embark (2026-09-25 round).
- `scenario run` cannot start on a lane whose profile holds a saved run: the relaunched game resumed the old boss fight and the menu never became ready (lane 1, 1336 run-history files, 447 s wait).
- Lane 1 embark `20260929-145523` was never reverted (all its ledger rows APPLIED, pid 27116 still up at `game_over`) although the seat's teardown was run; find why before relying on `seat.py` teardown. `embark` now refuses a lane with a live un-reverted launch.
- A ? room printed a shop with no shelves and the bridge refused `buy` (Varka round 2026-10-01, lane 1, act 3, 364 gold); find whether the room or the bridge's read is wrong.
- `play` asked which enemy while the only enemy was dead with its revive pending (Test Subject, Varka round 2026-10-01); the target check should skip the dead.

## Sim and measurement (Balance stage; nothing here runs on a prototype)

- `EB-195` the next re-baseline window: one twelve-arm table carrying the HP moves, the `POLICY_VERSION` bump for `PILOT_BURST_DIVISOR`'s removal, `EB-255` and `EB-810`.
- `EB-255` `archetype_shares` excludes starters by rarity, so 13 starter rows read back as drafts; exclude by membership inside `EB-195`'s bump.
- `EB-810` the sim's act-2 Louse has no Curl Up 14; wire it inside `EB-195`'s bump.
- `EB-241` `Card.is_junk` is rarity-only; make it type- and namespace-aware at the Kokomi fold, with that fold's re-baseline.
- `EB-32` the pilot block-panic rung; lands under its own `POLICY_VERSION` bump and window.
- `M13` `ROUTE_REGRET_MARGIN` has no derivation (Option D, no margin, stands); draft the slate and build `C2` (`review/records/regret-margin-registration-2026-08-12.md`).
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).
- The pilot heuristic (`tier0/pilot/policy.py`) does not price the full-stage Bow, and it still counts an arrival act.

## Parked: start only when the named trigger fires

- `EB-70` the starter-offer retune (`EB-27p`); wakes when a kit's design sweep reaches the Wings / Little Hexenzirkul class (R134).
- `EB-80` Kokomi prevention-on-curve review; wakes if a Kokomi playtest shows she needs more warding.
- `EB-33/34/35` repricing exhibits (The Gallery Stirs 0.0 at offer, Vulnerable as a flat debuff, no defensive term in `_reaction_value`); wake when the `_static_power` repricing session convenes.
- `EB-198` the Kurage HUD strip's blind read (half discharged, KURAGECAD-W1); wakes with the next blind round on the shipped Kokomi kit.
- `EB-651` a doubled `The other side` heading seen once and not reproduced; wakes on a sighting carrying the page sha.
- `EB-12` `bridge_unreachable` with the game alive, seen once; wakes on a second observation (`hangwatch` now classifies it).
- `EB-15` the seed's `lobby` route is unreachable in standard singleplayer; wakes with a Custom run or a hosted lobby.
- `SKIP-10.9` mechanics the sim does not model, promoted only on demand. Enemy: Back Attack, untargetable Burrow, Ethereal/Hex auras, pick-your-poison curses, damage caps (Hard to Kill, Plating, Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor powers, Soul Siphon stat theft, Blessed Antler, Philosopher's Stone. C# with no sim twin: the deferred-settle machinery (`SpotlightSystem`, `CurtainCallPowers`, `FurinaResources`) and per-dealer reaction windows (R1).
