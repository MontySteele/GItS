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

- Bennett's Passion Overload and Kujou Sara's Crowfeather Cover do not say that an Attack carries one element, or that Sara's Electro lands when both are up (`CompanionOverhaulRiders.ElementFor`, fixed order, not newest); the sentence does not fit the 125-character power ceiling (116 and 119 now). Kokomi review r4, item 4.
- Kokomi has no loop probe (Furina's is `tier0/harness/furina_loop_probe.py`). Its known set, when one is built: Shoal Call x2 + Watchful Shoal+ + The Shape of Water (review r3), Kurage Canopy + a planned Ward, a 0-cost Weak and 3 Block a turn (review r4), and Jellyfish Current + Stings, bounded because each reaction consumes the aura (pool overhaul 2026-10-13).
- Kokomi round 3 (2026-10-11): check whether Thieving Hopper's Flutter ("50% less damage from Attacks") should halve Opening Gambit's doubled Plan (a Skill); lane 5, fight 11.
- Kokomi round 3: Iron Club ("every 4 cards you play, draw 1") never visibly drew in lane 4; read `cards_drawn_by_turn` in her next round, or check the relic in game.
- Off-character kit cards, base-game faithful (resources work for anyone and their gauge appears on first gain, like the Regent's Stars and Osty): Furina's Drain, Repay and Fanfare, Kokomi's Plans and Kurage, Varka's Oath. Each is done when its kit reaches Balance; Klee is done.
- Klee's model frames (`tools/klee_render` + `tools/klee_rig`, milestone 2, 2026-10-12) are probed headless in MegaDot but not yet seen in a game: on the next deploy check combat (idle, throw, hurt, death, cast, a Set Off card's splash swap, low-HP cross-fade, facing flip, style G and the ground shadow under her), the merchant loop, the rest-site seat and the select close-up; and run `python -m tools.klee_rig verify --godot` (it opens a MegaDot window) when the game is free.
- Klee's map marker is still the wiki side-icon in the lower two-thirds of its 49x64 box (visual paper, pick 3 (a)): refit it with an `art_process` pass in the main checkout, or draw a base-style pin.
- Klee's rest-site still has no ground shadow (the base rest-site skeletons carry one): paint a soft ellipse under her seat into `klee_rest.png` in `tools/klee_render/pack.py` (visual paper, "Style G ruled").
- Art owed, Klee: Forbidden Fun, Lisa's Treats, Red Knight, Finders Keepers, Klee Can Explain!, Damage Report, Albedo — Dust of Purification (its plan row is re-pointed from Tectonic Tide's Albedo Wish splash, not yet fetched), Up in Smoke!, Behind Jean's Desk, Kitchen Alchemy, Cover Your Ears!; the two status-package Powers borrow Party Poppers' and Spark Knight's badges.
- Varka's model art (`tools/varka_rig`, phase B, 2026-10-13) is wired but not yet seen in a game: on the next deploy check combat (idle, attack spin-to-slam with its element trail in each of the five colours, hurt, death, cast, low-HP idle, facing flip, shadow), Four Winds' Ascension (the clip, both ground bursts, the target copy under each enemy shape and its draw order), the 0.6 s hit timing on multi-hit cards, the merchant loop, the rest seat, the select close-up and the roster tile; and confirm in the build log that his sheets import VRAM-compressed.
- Furina's model art (`tools/furina_rig`, phase B, 2026-10-13) is wired but not yet seen in a game: on the next deploy check combat (idle, the thrust with its Hydro trail, hurt, the swoon, cast, low-HP idle, facing flip, shadow), Let the People Rejoice (the clip, the gold burst during the spin, the hit on the flourish), the Drain and Repay runs to the nearest guest at one, three and four seats, the guests' heights and widths in the line (Freminet no longer Osty), the 0.4 s hit timing on multi-hit cards, the merchant loop, the rest seat, the select close-up and the roster tile; and confirm in the build log that her sheets and the guest stills import VRAM-compressed.
- Klee's rest-site pose is a still: BaseLib rebuilds the rest sprite from the texture alone, so an idle loop there needs code.
- Yae Miko's model art, phase A (`tools/char_render/yae_clips.py`, `tools/yae_rig`, 2026-10-14, a temporary model) is built but not rendered: run `tools/char_render/build.py --char yae` when the machine is free, review the sheets (the robe laid over her lap in the seiza rest seat and the death kneel, her sleeves, the flick's streak, the select close-up), then `python -m tools.yae_rig gen`, and in that commit delete build_pck's static Yae merchant heredoc, set `Yae.AttackAnimDelay` to the flick (0.4 s, frame 8), add `yae/model/combat.tscn` to `KleeSceneTelemetry`, and check her Bounds/IntentPos (Kokomi's x 1.11) against the intent row.
- Art owed, Kokomi: Kelp Wall, Tidecleanse, Sea Glass Harvest, Flotsam Surge and the Sea Glass token; and the pool overhaul's six (Turning Tide, Brine Spray, Jellyfish Current, Prepared Retreat, Battle Formation, Turnabout; `art_coverage.KNOWN_MISSING`).
- Art owed, Spiral Abyss mode (2026-10-12): the menu emblem and The Ley Line are 64px wiki sources upscaled 4x, and seven are nearest-official stand-ins (Abyssal Moon = Iridescent Moon, Moonlit Rest = Sweet Madame, First Strike = Sword Unaligned, Elemental Burst = Battle-Line Detonation, Crystallize = Crystallize Shield Hydro, Sheer Cold = Element Cryo, Elemental Mark = Element Pyro).
- Art owed, Spiral Abyss round two (2026-10-12): the ten new entries borrow the first eight's icons until their own are fetched (Overflow = Elemental Burst, Vigor of the Abyss = First Strike, Moonlit Spring = Moonlit Rest, Battle Rhythm = Resonance, Wavering Moon = Abyssal Moon, Starfell Draft = Fateful Fortune; Thorny Ground = Abyss Herald, Bulwark = Fatui Skirmishers, Frenzy = Rally, Withering = Sheer Cold), so two cards on one page can share an icon.
- Art owed, pool completion: the 14 new rows and the three new Ancients (Alice's Masterpiece, Divine Strategy, Center of Attention).
- Art owed: Durin — Principle of Purity wears Binary Form's picture (`art_of`); the three Purity powers borrow Binary Form's badge.
- Durin, Principle of Purity's turn-start Pyro hit (`PurityStrikePower`) shares `AfterPlayerTurnStart` with Melody Loop's Hydro, Herald of Frost's Cryo and Surprise Dispatch's roll, so the mod gives it no order where the sim runs it after Melody Loop; stage it into its own broadcast if a seat sees the two disagree.
- Neuvillette's turn-start Hydro hit (`AncientSeaAuthorityPower`) and Varka's turn-start Swirl (`SturmUndDrangPower`), both new in the 2026-10-11 Companion pass, share `AfterPlayerTurnStart` with the same tenants as Durin's line above, so the mod gives them no order where the sim runs Neuvillette before the companion block and the Swirl right after Durin's hit; stage them if a seat sees the two disagree.
- Klee finish-line batch, pinned headless only; watch in game and through the bridge: Dodoco Tales' opening Sparks (and the Spark row naming the relic), Finders Keepers' draw trigger, Confiscated playing as a Status (drag-to-play, frame, Klee Can Explain! / Kitchen Alchemy taking it), Mine, All Mine!'s Mine landing on the enemy its hit killed.
- Pool completion: Divine Strategy's now-line, Center of Attention's free Spend and the two co-op cards (Tactical Relay, Kurage's Mercy) are pinned headless only; watch them in game and through the bridge.
- Varka Hydro cards (Tidal Bulwark, Whisper of Water) went ungraded in two seats (each offered once, passed); they are read in [USER]'s run.
- Varka's Ancients (All Four Winds from Darv's Tome, Dandelion Gale from Orobas's Archaic Tooth on Four Winds' Ascension) and his "(Makes Pyro current)" line are pinned headless only; watch them in game and through the bridge.
- Verify Boreas's Fang saved starter element survives save/reload (`Relics/VarkaStarterKnight.cs`, a BaseLib `SavedSpireField`; no test exercises a real serialize/deserialize, so the Fang and Knight's Commission keep their deck fallback until then).
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- Varka's element-switch hover, the left-element icon (`OathLeftPower`), the Fang's turn-one element, Windborne Resolve and Weathervane's start-of-turn grid (also in co-op) are still unconfirmed in game and through the bridge; the next Varka seat record says whether each was seen.
- Varka's screen: Artifact silently eats Frozen, Weak and Electro-Charged's Poison, and the reaction text should say "blocked by Artifact"; Bottled Gale with no aura on the board does nothing and nothing warns; Diluc printed 9 against the card's 6 with no reason shown (`review/records/varka-combo-round-2026-10-05.md`, items 4-6).
- Kaeya — Frostgnaw (`ProtoMcKaeyaFrostgnaw.cs`, the shared Mondstadt card) printed 12 against a written 8, and its own Superconduct's Vulnerable (the tip says it "applies before this hit") did not multiply the hit; trace the order and the printed number.
- Card reward card off screen but still selectable by controller (user, co-op). Cause not found; `Diagnostics/RewardRowProbe.cs` writes a "reward row OFF SCREEN" WARN to godot.log naming the card and where its holder and body are; read that line after the next sighting and fix from it.
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning, where a Swirl or Crystallize on a burning enemy consumes the held Pyro and Burning keeps ticking; and Dendro ported as ruled (the non-reacting pairs, the Core rules and their previews), tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Show the amplifier: a Melt or Vaporize prints no factor on the face or in the seat log (Rosaria's Melt printed "Deal 15" from a written 9; "Vaporize on X" with no x1.5; Klee's log printed "nothing to amplify" beside a hit multiplied by 1.75); a hit carrying an element chosen at play (Four Winds' Ascension, Northwind Avatar) previews no amplifier either (multiplier pinned by `A_current_element_hit_amplifies_like_any_hit`).
- Kokomi round 2 (0.2.5212, lane 3): Grand Design+ printed "no card in your hand can be planned" on most turns of a deck about two-thirds Plan cards and Companions, but headless the gate matches the Bake-Kurage's drop target for every card class, printed and upgraded (`KokomiRoundTwoFixesTests`), and the sim matches every row; the cause is not found. The gate now fails open and writes its first throw to godot.log ("Grand Design gate:"): after the next Kokomi round read that line, and have the seat record the hand on any Grand Design refusal. Grand Design+ Retains, so a refusal after the turn's Plans were played is correct and may be what the seat saw.
- Furina: rename the four mismatched guest ids in one regen, moving their art keys with them, after [USER]'s run and never mid-save.
- `EB-65` the four Furina power badges draw shrunk card portraits; they want badge-kind icons like Klee's.
- `EB-803` `proto_mc_kaeya_frostgnaw` wears Cold-Blooded Strike's named art (only Frostgnaw's own pick is owed).
- `EB-53` end-of-turn docket: capture the co-op half (`C6`) on the two-seat runtime (`embark --coop`) and isolate the electro (Oz) leg.
- `EB-296` / `EB-300` controller: a live walk that the Kokomi pet is targetable by D-pad and mouse, and that the hand is reachable after a custom-target card.
- `EB-159` [USER] at the machine: listen for the modded player's death sound (`set_hp player 1`, end turn into a hit).
- `EB-38` [USER] at a shop: the spine-less character portrait idles (the rest-site half is seen).
- `EB-160` verify a live locale switch: the injected loc tables survive it, or a `LocException` names the seam.
- Furina screen (wave 2026-10-12): Hymn's "(Repays 0)" preview is wrong after a Drain; Spend damage never shows Vulnerable; a boss shows "Frozen 1".
- Kaiser Crab (Varka wave 2026-10-13, lane 5 fight 16): when Baron Bunny's turn-start hit killed Rocket, Crab Rage's 99 Block never reached Crusher (telemetry: 18 enemy Block all fight, Crusher's own Guarded Strike; Crusher then died to Tidal Bulwark and Blazing Charge). The base game grants it in `CrabRagePower.AfterDeath` and no mod code was found that removes it; reproduce live (`set_hp` Rocket low, Baron Bunny).
- Kokomi round 3 (lane 4 F6): Change of Plans was refused "no Energy" with four Plans waiting. Not reproduced: it costs 0, its gate reads only the queue, and the sim plays it at 0 Energy with four waiting (`test_kokomi_round3_alist_2026_10_13`). The game's refusal enum ("EnergyCostTooHigh") is what prints "not enough energy"; have the next seat record the hand and Energy on any such refusal.
- Varka text (ascension check 2026-10-12): a Knight Companion's element switch (Team Effort) shows only after the play; Kindled Edge switched him to Pyro with no "Element switch" line; Four Winds' Ascension returns after a mid-fight reshuffle, unprinted.

### Klee faces (under the freeze: fix on `klee-next`)

- The printed Bomb number leaves out Hardened Shell's cap (its own badge shows the cap) and The Big One's x4; the test relic's "Bomb 6" shows as 10 on her first turn (turn-start growth; grant-only relic). Boom Badge and Durin's Dark are folded since #1226.
- Mine text does not say it consumes the aura set for the big Bomb (the Mine tip is at its 135-character ceiling; the plain-Bombs half is in the tip since #1226).
- Perfect Timing's replay did not visibly fire when its first Set off killed the target.
- "Witch's Homework" and "Witch's Homework II" read alike in hand lists (a naming pick for [USER]; the Retain half is a tip since #1226).
- Chained Reactions' +3 missed a two-Bomb Ka-pow! set-off (trace); Durin's start-of-turn tick skipped one fight (Fogmog, trace).
- The Spark line vanishes at 0, and Snecko Oil's added Spark costs are unexplained; a Mine going off printed "gives 1 Spark" plus Pounding Surprise's "+1 Spark" but the seat counted +1.
- Wait For It... printed "Nothing ... landed" on paying turns; Weak shows different Pyro numbers on card and board; the Melt preview reads as if the whole Bomb pile multiplies.

## Seat page (the blind seat's view: `blindplay_*` render and the bridge)


- The enemy-fold note names "(Deals N damage)" faces, but base Body Slam prints one too and does not fold (#1223).
- The hand-full discard line for generated Stings and Wards prints only after the Plans resolve (Kokomi round 4, lane 1, fight 16).
- No receipt says what a Set off detonated, so a Set off that kills reads as a vanished Bomb. Needs a detonation log in the mod like ReactionLog, a bridge read and a page line such as "Sizzle set off Corpse Slug: Mine 3 (3), Bomb 16 (2, killed it). Nothing jumped."
- Incoming ignores Mines that fire first and Look Out!'s Block from them; the "Put Mine N on ..." lines after Big Badda Boom read as five Mines from one Bomb.
- Ka-pow!'s own damage is not printed when its target dies to its Bombs, and the hits of a fight-ending Rapid Fire are skipped.
- The resolution rows do not say which hit was which (Four Winds' Ascension+ read "2, 3, 9, 36" unlabelled); needs a source label per hit on `ResolutionLedger`'s wire and in `blindplay_render`'s hit rows.
- Cycle of Seasons' trigger damage prints on the line of the card that changed Varka's element, and Cycle's own line reads "Nothing this page can count landed off it".
- Copy numbers renumber after a play, so "Frantic Escape (2)" picked the other copy; name copies by something stable (cost or upgrade) or warn on renumber. The bridge renumbers mid-turn too ("Sting (3)" vanished after a play and the next command was refused; Kokomi jellyfish round 2026-10-12, lane 1). Numbers now hold until the next `observe` (`resolve_shown_card`), but Kokomi round 3 lane 5 F6 still wasted The Shape of Water on a renumbered Sting; stable handles for a whole turn need copy identity across observes (a per-card id on the wire).
- Pocket Match's play log listed 3 and left out its own 5 damage.
- Tender prints only "Tender 3"; Fireworks Finale's "Written: 5" does not name the Strength loss that lowered it; Spiny Toad's Thorns showed on turn 1 only.
- A Companion summon's ticks (Kamisato Ayaka's Soumetsu) print only inside Kokomi's Plan block (`summon_hits`); a Furina or Klee page shows them nowhere.
- A companion's end-of-turn hit (Kaeya, Oz) names its body only when it reacts; a plain hit is on no wire, because `ResolutionLedger` files card plays and a power's damage is not one.
- Orb passives and evokes at the start and end of a turn are narrated nowhere; `ResolutionLedger` files card plays only.
- The Neow bundle page printed one pack's rows jumbled (a line missing, its text under another card). Not reproduced; needs the raw `bundle_select` state from such a screen.
- The Trial's first page printed only "Proceed", and `proceed` was then refused against its Accept / Reject options (the page read the event mid-transition).
- The first rest at a rest site printed "Took: Rest." with "error Rest site room is not open" and still counted an action (see `EB-391`).
- Co-op: players are named "Test Host"/"Test Client 1"; the reaction glossary ignores the partner's element; `wait` after a finished fight reports nothing while the reward is up; a play at an enemy the partner just killed is silently retargeted.
- Enemy rules not on the page: Flutter's "50% less damage from Attacks" halved Bomb damage in one run and not in two others; say whether it applies to a Bomb.
- Louse Progenitor's intent under the player's Weak read "folded Strength and Weak: 14 on the move and 14 after" and the Weak seemed to do nothing; check the fold and the line.
- Co-op: a downed player is revived after the fight (at 1 or 13 HP) with no warning on the page.
- Co-op: `proceed` answers "No proceed button" at rest sites, chests and rewards until the partner acts, then works on a retry; the page should say it is waiting on the partner.
- A dead Decimillipede segment waiting to Reattach is not on the wire (`BuildBattleState` sends only living enemies); send the body and its revive countdown.
- The bridge does not show the order enemies act in; print it when the game exposes it.
- Live repro, no change before it: Wax Lizard Tail did not fire after Toy Box (base relics; `review/records/furina-fullrun-round-2-2026-10-10.md`). Check whether a melted relic stays in `player.Relics` unflagged, so the page still lists it (bridge `McpMod.StateBuilder.cs:1471-1488`).
- Live repro, no change before it: Fairy in a Bottle may not have saved the Ironclad control at death (base potion; `review/records/kokomi-fullrun-round-2026-10-10.md`). No klee-mod hook touches death or HP loss, so check the base game's own path in a live run.

- Furina: Frozen on a boss, and whether a guest's act ends a freeze, are not printed (round 2026-10-12, lane 2; the Freminet Block half is built, #1223). Needs the game.
- Seat page: an Ancient's greeting text is not printed, only "(the scene is still being told)"; print the dialogue lines so seats read the story.

## Harness, bridge and tools

- Telemetry: Plan damage is credited to the writing card since #1222, so `damage_by_source` no longer has a "(Bake-Kurage)" key; update any analysis that reads it.
- Shop card removal: after the first card is picked the screen refuses a re-pick and offers only confirm or skip; check whether the base screen allows a deselect and the bridge lacks the verb.
- Bridge: Jumpy Dumpty refused without a target, a Durin chooser answered "still opening", and Mawler died at end of turn with no printed cause.
- Drowning Beacon's "Bottle" potion reward: trace the bridge on the event's custom reward screen (is it shown, or left behind on `proceed`). The mod matches the base event.
- Bridge `ModeLabels`/`RecordChoice` still carry the sheet's literal numbers for mode faces; read them from the card's vars instead.
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- An embark was never reverted (all its ledger rows APPLIED, the game still up at `game_over`) although the seat's teardown was run; find why before relying on `seat.py` teardown. `embark` now refuses a lane with a live un-reverted launch.
- The seat harness sometimes sends end-turn twice in a row (seat rounds); find which path repeats it.
- `EB-391` the `rest` verb sometimes fails its first call on an open rest site ("Rest site room is not open"); game-side race.
- `EB-208` the seed ledger ships empty: run the Klee three-body seed hunt and record the first entries.
- `EB-212` stage and seal real matched-telegraph pairs (identical but for the enemy intent) under `understudy/battery/pairs/`.
- `EB-193` `game_ref/role_tempo_canon.json` predates the int-var reader fix; regenerate it (46 cards gain `has_body`).
- `EB-667` the Smith shows no upgrade for Ultimate Strike; its numbers are published nowhere the repo reads.
- `EB-71` no committed sheet prints `sly_autoplay`, so the `CardKeyword.Sly` rail has never run in game; whoever prints the first one checks it live.

## Sim

- Delete the sim's dead Fanfare meter in `tier0/engine/resources.py` (still wired into the engine; left by #1224).
- Legacy cleanup stage 6: one shipped leftover stays in every generated card because removing it changes the emitted C# of current rows: the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, the codegen's `spotlight_calc_rider` / `spotlight_block_rider`). Drop it in one regen with a deploy check, riding Klee's next promotion PR.
- The old shipped `BombPower.cs` is placed by no card (its keyword row, `KleeKeywords.Bomb` and `includesBombRules` went in #972) but 9 C# test files, `PlayTelemetry` and two relics' listener bus still read it; move those readers and delete it.
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).

## Parked: start only when the named trigger fires

- `EB-70` the starter-offer retune (`EB-27p`); wakes when a kit's design sweep reaches the Wings / Little Hexenzirkul class (R134).
- Yae's Ancient gap: design her two Ancient cards (one Darv's Dusty Tome adds, one Orobas's Archaic Tooth makes from a starter, as Varka's do) in the next Yae card pass. Until then a stopgap guard (`Patches/YaeDustyTomeGuardPatch.cs`: Darv offers her no Dusty Tome while her pool holds no Ancient) stands against LAW's "real content" line, ruled by [USER] 2026-10-13: "(a). Yeah, I think that's fine." Delete the guard in the commit that lands her two Ancients, with a `RosterAncientCards.Yae` ledger and a `lint_ancient_coverage.py` row.
- `EB-80` Kokomi prevention-on-curve review; wakes if a Kokomi playtest shows she needs more warding.
- `EB-651` a doubled `The other side` heading seen once and not reproduced; wakes on a sighting carrying the page sha.
- `EB-12` `bridge_unreachable` with the game alive, seen once; wakes on a second observation (`hangwatch` now classifies it).
- `EB-15` the seed's `lobby` route is unreachable in standard singleplayer; wakes with a Custom run or a hosted lobby.
- `SKIP-10.9` mechanics the sim does not model, promoted only on demand. Enemy: Back Attack, untargetable Burrow, Ethereal/Hex auras, pick-your-poison curses, damage caps (Hard to Kill, Plating, Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor powers, Soul Siphon stat theft, Blessed Antler, Philosopher's Stone. C# with no sim twin: the deferred-settle machinery (`SpotlightSystem`, `FurinaResources`) and per-dealer reaction windows (R1).
- Yae pool expansion: several Tenko cards that carry their own scaling (paper pick 1 (b): +1 a strike per Tenko; (c): a bonus when a strike reacts), per [USER] 2026-10-13.
