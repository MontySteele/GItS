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

- Co-op seat page: the "What you played this turn" log lists the partner's cards as your own; players are named "Test Host"/"Test Client 1"; the reaction glossary ignores the partner's element; a contested chest pick is not announced; `wait` after a finished fight reports nothing while the reward is up; a play at an enemy the partner just killed is silently retargeted (co-op round, 2026-09-27).
- Seat page: the play log prints "Put Bomb 1" where the badge shows the placed size, and the Weak gloss says it cuts a Bomb's damage (it does not: a Bomb carries the target's modifiers only) (co-op round, 2026-09-27).
- Co-op rest site: Mend on the partner did not end the rest action, so Smith was still offered (co-op round, 2026-09-27).
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- Seat page: a companion's end-of-turn hit (Kaeya, Oz) names its body only when it reacts; a plain hit is on no wire, because `ResolutionLedger` files card plays and a power's damage is not one (wave-3 Klee lane 2b, 2026-09-26).
- Furina Stage: a hit from a debuff on her (Knowledge Demon's Disintegration) reaches the stage log as "damage no enemy dealt"; `ModifyHpLostBeforeOsty` hands no power source, so only a card in hand (Burn, Wither) is named (wave-3 Furina lane 4, 2026-09-26).
- Furina Stage: Soliloquy's bonus is missing from the preview of a Spend that empties the stage (Bravura "(Deals 7 damage)" hit for 14); the preview would have to know the Spend takes the last seat and that no Bow reader (Thunderous Applause's summon, A Five-Century Act's return) refills it (Solo seat, 2026-09-26).
- Furina Stage: the end-of-turn forecast ("you take N") folds nothing the acts will cause on the enemy side -- a Frozen or Superconduct from an act, a stun from stripped Block (Tunneler's Burrowed) -- so it overstates; it needs the acts' reactions predicted per body (lane 2, 2026-09-26).
- Once More! spends its Sparks and returns nothing, with no message, when the last Set off card has been shuffled back into the draw pile (the spend is by design, `KleeOverhaulLedger.ReturnLastSetOff`); the miss prints nowhere a seat can read (Klee full run lane 1, 2026-09-26).
- Big Badda Boom's "what your Bombs dealt" counts Block the Bombs removed in C# (`ElementalHit.Deal` returns the pre-Block hit) but HP only in the sim (`deal_damage_to_enemy` returns `hp_dmg`); the two engines disagree whenever the target has Block (found 2026-09-26).
- Shipped Furina's Encore buffer (FurinaResources.AbsorbDamage) rounds a fractional HP loss up; the engine truncates (found 2026-09-25).
- Beetle Juice's Shrink on an enemy prints "While is alive, you deal 30% less damage": the name is blank and it speaks in the player's voice (Klee seat, 2026-09-23).
- Rosaria's Melt on Klee's board printed "Deal 15" from a written 9, which no printed multiplier explains; show the reaction's factor on the face.
- Kokomi: engine pieces the halves rewrite left unused (`NextAttackDamage` with `NextAttackDamagePower`, which Battle Plan stopped using at R276 and no row applies, per the 2026-09-25 text pass; `BlockPerPlanThisMorning`, `plans_carried_out_this_morning`, the morning-damage tip); delete them in C# and the sim.
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
