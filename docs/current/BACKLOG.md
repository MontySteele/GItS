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
is `git show bf073df4:docs/current/BACKLOG.md`; the last copy before lines were
cut to about 350 characters is `git show 3ce4f8c35:docs/current/BACKLOG.md`.

## Kits and display (the mod)

- Yae round 9 (2026-10-17): "Replay 2" beside "Reprint: used this combat" left lane 5 unsure what the next play does.
- Yae round 10 (2026-10-17): Second Printing's chooser said it closes after one pick but needed two (lane 2). Not reproducible headless: the base pile screen closes on one pick with these prefs; a Reprinted Second Printing would open a second chooser at once. Needs a live look.
- Bennett's Passion Overload and Kujou Sara's Crowfeather Cover do not say that an Attack carries one element, or that Sara's Electro lands when both are up (`CompanionOverhaulRiders.ElementFor`, fixed order, not newest); the sentence does not fit the 125-character power ceiling (116 and 119 now). Kokomi review r4, item 4.
- Kokomi, Nereid's Ascension: the Plan-line version to try next is a card with only a Plan line, like Masterstroke: "Plan: This turn, your Attacks deal double damage." It needs a no-stacking clause, or Second Wave makes it quadruple (`review/active/kokomi-cards-2026-10-18.md` sec.2, change 2). Not in the v2 build.
- Yae round 2026-10-19b (lane 1): "refreshes and gains a Level" left a refreshed Sakura at Level 1 when the shrine was not full (seat report, not reproduced). Needs a live look.
- Kokomi, Exhaust: "salvage a failed Plan", Exhausting a waiting Plan for an immediate effect (a flip changes which line fires, not when). Held by the v2 paper (pick 2 (a)) for a later look (`review/active/kokomi-cards-2026-10-18.md` sec.3).
- Kokomi, Draft the Orders: the discount and its take-back on a normal play are seen (2026-10-18); unseen: a card the cut alone made affordable is refused when played normally (`KokomiPlanCost`).
- Kokomi round 3 (2026-10-11): check whether Thieving Hopper's Flutter ("50% less damage from Attacks") should halve Opening Gambit's doubled Plan (a Skill); lane 5, fight 11.
- Kokomi round 3: Iron Club ("every 4 cards you play, draw 1") never visibly drew in lane 4; read `cards_drawn_by_turn` in her next round, or check the relic in game.
- Kokomi off-character (2026-10-18, `KokomiOffCharacterSweepTests`), unseen in game: on a non-Kokomi seat the Bake-Kurage appears beside them when a Plan card is first drawn or played (a mid-draw summon), the strip appears on their first Plan, and a Plan carries out next turn; check placement beside a non-Kokomi model and in co-op.
- Klee's model frames (`tools/klee_render` + `tools/klee_rig`): seen in a game 2026-10-16 (lane 1, `python -m tools.klee_rig verify --godot` OK) except the facing flip (needs a creature behind her: Surrounded or the Kaiser Crab), the cast on a mod Skill, and style G by eye.
- Power badges borrowing another power's icon (`KleePowerIcons.cs`), counts: Klee (17), Kokomi (26), Furina (31), Varka (~25), Yae (Serial Novel), Mondstadt companions (21), co-op (10), three debuff riders. Each needs its own `art/plan.tsv` power_ row (borrowed badge as fallback); upgraded starter relics share their starters' icons. Names: `git show 3ce4f8c35:docs/current/BACKLOG.md`.
- Klee's map marker is still the wiki side-icon in the lower two-thirds of its 49x64 box (visual paper, pick 3 (a)): refit it with an `art_process` pass in the main checkout, or draw a base-style pin.
- Varka's model art (`tools/varka_rig`): seen in a game 2026-10-16 except the facing flip, the 0.6 s hit timing on multi-hit cards (1 s captures too coarse), Four Winds' Ascension's two ground bursts and the target copy under each enemy (not picked out in the frames: only one teal ring at his blade), and the VRAM-compressed import in the build log.
- Furina's model art (`tools/furina_rig`): seen in a game 2026-10-16 except the facing flip, the four-guest line (a 4th summon pushed Freminet off, so the line stays at 3), the 0.4 s hit timing on multi-hit cards, and the VRAM-compressed import of her sheets and guest stills in the build log.
- Furina's guest-star effects (`tools/furina_rig/guest_fx.py`, `review/active/furina-guest-fx-2026-10-16.md`) are unseen in a game: each of the eleven plays once per act with the lunge on its own target, again on Showstopper and Bottled Encore, sits right on small and large enemies, and leaves no node behind.
- The hit number may land before the slam on Four Winds' Ascension and Let the People Rejoice: lanes run at Instant speed, which skips the delay; look at Normal speed (`CardPlayMotion.AscensionDelay` / `RejoiceDelay`).
- A pale bar behind a summoned Freminet needs a live look.
- Furina's Spend confetti (edge alpha 151) and the Navia and Wriothesley guest effects (163) are cut at their canvas edge, as Repay's bloom was (pale box in game): widen their canvas in `tools/char_render/fx.py` and drop them from `EFFECT_EDGE_KNOWN` (`tier0/tests/test_char_render.py`).
- Kokomi's story (`klee-mod/KleeCode/Story/KokomiStory.cs`, 2026-10-16): unseen in game. Watch the Gorou pick grid, the Rare pick grid after Doubt on "Concede and study its opening.", the 4 Max HP loss at The Serpent's Bones, the pearl and stake locks under 50 Gold, Public Address's two-line text, and her co-op story room showing her own event.
- Furina's story (`klee-mod/KleeCode/Story/FurinaStory.cs`, 2026-10-16): unseen in game. Watch the Guest Star pick grid, the Oratrice lock under 50 Gold, Doubt leaving on "Break it.", and her Let the People Rejoice line.
- Story chains (`klee-mod/KleeCode/Story/`): unseen in game: routing after save and reload, Doubt leaving as The Knights Come Looking opens, and the potion reward mid-event. The co-op story room's routed pages all read "A Quiet Landing" (`review/records/coop-story-rooms-2026-10-16.md`).
- Kokomi's three potions and Furina's two potions (#1324, #1325) were not met in a seat; check them with `understudy.embark --relic` or in a play (the relics are seen).
- Klee's rest-site pose is a still: BaseLib rebuilds the rest sprite from the texture alone, so an idle loop there needs code.
- Durin, Principle of Purity's turn-start Pyro hit (`PurityStrikePower`) shares `AfterPlayerTurnStart` with Melody Loop's Hydro, Herald of Frost's Cryo and Surprise Dispatch's roll, so the mod gives it no order where the sim runs it after Melody Loop; stage it into its own broadcast if a seat sees the two disagree.
- Neuvillette's turn-start Hydro hit (`AncientSeaAuthorityPower`) and Varka's turn-start Swirl (`SturmUndDrangPower`) share `AfterPlayerTurnStart` with Durin's line above, so the mod gives them no order where the sim runs Neuvillette before the companion block and the Swirl right after Durin's hit; stage them if a seat sees the two disagree.
- Navia's turn-start Geo hit on ALL enemies (`CannonFireSupportPower`) and Sigewinne's turn-start Hydro (`ReboundHydrotherapyPower`), new in the Fontaine pool rework (2026-10-19), share `AfterPlayerTurnStart` with the tenants on the two lines above (Durin, Neuvillette), so the mod gives them no order where the sim runs them right after Neuvillette's hit; stage them if a seat sees the two disagree.
- Klee finish-line batch, pinned headless only; watch in game and through the bridge: Dodoco Tales' opening Sparks (and the Spark row naming the relic), Finders Keepers' draw trigger, Confiscated playing as a Status (drag-to-play, frame, Klee Can Explain! / Kitchen Alchemy taking it), Mine, All Mine!'s Mine landing on the enemy its hit killed.
- Pool completion: Center of Attention's free Spend (a seat misread it on "Spend all your Fanfare") and the two co-op cards (Tactical Relay, Kurage's Mercy) are pinned headless only; watch them in game.
- Varka's Whisper of Water went ungraded in seats; it is read in [USER]'s run.
- Varka's All Four Winds (Darv's Tome) and his "(Makes Pyro current)" line are pinned headless only (Dandelion Gale is seen); watch them in game.
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- The tooltip trim (2026-10-14) is unseen in game: the aimed reaction preview (`Cards/ReactionAim.cs`, set while dragged onto an enemy, cleared on unhover, cancel and finish), the base game's Weak/Vulnerable/Strength tips on the trimmed cards, and the bridge still serving full tips (`gits/GitsSeatTips.cs`).
- Varka's element-switch hover, the left-element icon (`OathLeftPower`) and Weathervane's start-of-turn grid (also in co-op) are unconfirmed in game; the Fang's turn-one element and Windborne Resolve are seen.
- Card reward card off screen but still selectable by controller (user, co-op). `Diagnostics/RewardRowProbe.cs` fires on every card not yet drawn ("NotDrawn card_rect 0x0", 8,448 lines by 2026-10-19): skip undrawn rows so a real sighting stands out.
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning (a Swirl or Crystallize on a burning enemy consumes the held Pyro; Burning keeps ticking) and Dendro as ruled, tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Show the amplifier on a hit whose element is chosen at play (Four Winds' Ascension, Northwind Avatar): no preview (the seat page names Melt and Vaporize factors since 2026-10-19).
- Furina: rename the four mismatched guest ids in one regen, moving their art keys with them, after [USER]'s run and never mid-save.
- `EB-53` end-of-turn docket: capture the co-op half (`C6`) on the two-seat runtime (`embark --coop`) and isolate the electro (Oz) leg.
- `EB-296` / `EB-300` controller: a live walk that the Kokomi pet is targetable by D-pad and mouse, and that the hand is reachable after a custom-target card.
- Kokomi's Plans view (`Vfx/Prototype/KokomiPlanView.cs`) is unseen in game: with a controller the left stick opens the grid, captions sit under the cards, A flips a two-line Plan, a Plan-only card says why, B and Confirm return focus to the hand, and the peek glyph shows under the strip.
- Furina screen: Hymn's "(Repays 0)" after a Drain, and a boss showing "Frozen 1" (a boss-room non-minion gets Vulnerable instead, `ReactionEffects.cs:557-575`); both need a live look.
- Furina, Lynette's badge says "aura first", her card "one with an aura if able"; the card's wording is 138 of the 135-character tip ceiling (`FurinaStageBadges.cs:104`).
- Kaiser Crab (Varka wave 2026-10-13, lane 5 fight 16): when Baron Bunny's turn-start hit killed Rocket, Crab Rage's 99 Block never reached Crusher. The base game grants it in `CrabRagePower.AfterDeath` and no mod code was found that removes it; reproduce live (`set_hp` Rocket low, Baron Bunny).

### Klee faces (under the freeze: fix on `klee-next`)

- Durin's start-of-turn tick skipped one fight (Fogmog, trace); `RandomEnemy` may pick the Eye With Teeth illusion (`CompanionOverhaulPowers.cs:51`). Live look. (Chained Reactions is QUEUE, backlog wrap-up pick 3.)
- Wait For It... printed "Nothing ... landed" on paying turns: the ledger records only powers put on enemies (`ResolutionLedger.cs:733-739`), not the Skill's power on her (Weak and the Melt preview are fixed).

## Seat page (the blind seat's view: `blindplay_*` render and the bridge)

- `observe` refuses ("this page printed the enemy list twice") when two Decimillipede segments wait to Reattach; both seats of the Fontaine round hit it (`review/records/fontaine-round-2026-10-19.md`).
- The Colorless Potion offers Beat Down (play 3 Attacks from the discard) with no note when the Discard Pile has no Attacks (Fontaine round, lane 1).


- Copy numbers renumber after a play, so seats pick the wrong copy ("Frantic Escape (2)"; Kokomi round 3 lane 5 wasted The Shape of Water on a renumbered Sting). Numbers now hold until the next `observe` (`resolve_shown_card`); stable handles for a whole turn need a per-card id on the wire.
- The Neow bundle page printed one pack's rows jumbled (a line missing, its text under another card). Not reproduced; needs the raw `bundle_select` state from such a screen.
- The Trial's first page printed only "Proceed", and `proceed` was then refused against its Accept / Reject options (the page read the event mid-transition).
- Co-op: a play at an enemy the partner just killed is silently retargeted; a queued play at an enemy the partner killed mid-turn comes back "Skipped" or "not found" (`review/records/furina-coop-check-2026-10-16.md`).
- Live repro, no change before it: Wax Lizard Tail did not fire after Toy Box (base relics; `review/records/furina-fullrun-round-2-2026-10-10.md`). Check whether a melted relic stays in `player.Relics` unflagged, so the page still lists it (bridge `McpMod.StateBuilder.cs:1471-1488`).

- Furina: Frozen on a boss, and whether a guest's act ends a freeze, are not printed (round 2026-10-12, lane 2; the Freminet Block half is built, #1223). Needs the game.

## Harness, bridge and tools

- Mawler died at end of turn with no printed cause: a kill with no card behind it (a Mine answer, an end-of-turn power) has no ledger row to print under (`gits/GitsResolutionLedger.cs:27`); add a non-card damage row.
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- `EB-193` `game_ref/role_tempo_canon.json` predates the int-var reader fix; the writer is fixed (2026-10-19), but the regen moves 25 of 110 package floors in `docs/role-tempo-floors.yaml` (QUEUE, backlog wrap-up pick 6).
- `EB-71` no committed sheet prints `sly_autoplay`, so the `CardKeyword.Sly` rail has never run in game; whoever prints the first one checks it live.

## Sim

- `tools/gen_klee_cards.py` still emits `BombPower.*` calls for place_bomb, detonate, modify_bombs, move_bombs and chance_bomb_per_detonation; no row uses them, but a new one would fail the build (BombPower.cs is gone).

- Delete the sim's dead Fanfare meter in `tier0/engine/resources.py` (still wired into the engine; left by #1224).
- Legacy cleanup stage 6: the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, codegen `spotlight_calc_rider` / `spotlight_block_rider`) stays in every generated card because removing it changes current rows' C#. Drop it in one regen with a deploy check, riding Klee's next promotion PR.
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).

## Parked: start only when the named trigger fires

- `EB-70` the starter-offer retune (`EB-27p`); wakes when a kit's design sweep reaches the Wings / Little Hexenzirkul class (R134).
- `EB-651` a doubled `The other side` heading seen once and not reproduced; wakes on a sighting carrying the page sha.
- `EB-12` `bridge_unreachable` with the game alive, seen once; wakes on a second observation (`hangwatch` now classifies it).
- A new `EB-489` hang shape: the game thread froze (a native hang; `dotnet-stack` showed no managed main thread), every bridge call timed out, and embark abandons the save so the run is lost. Seen Yae r5 lane 4 (2026-10-15, godot.log ending on "FocusIn received") and a co-op host in a boss fight (2026-10-16). Wakes on a second sighting.
- `EB-15` the seed's `lobby` route is unreachable in standard singleplayer; wakes with a Custom run or a hosted lobby.
- `SKIP-10.9` mechanics the sim does not model, promoted only on demand: many enemy mechanics (Back Attack, Burrow, damage caps, Artifact, Thorns and more) and C# with no sim twin (`SpotlightSystem`, `FurinaResources`, per-dealer reaction windows). Full list: `git show 3ce4f8c35:docs/current/BACKLOG.md`.
- Yae pool expansion: several Tenko cards that carry their own scaling (paper pick 1 (b): +1 a strike per Tenko; (c): a bonus when a strike reacts), per [USER] 2026-10-13.
- Before the Workshop release: check The First Exam and A Song on the Wind against Varka's in-game character story text (`review/active/klee-varka-story-chains-2026-10-14.md`, "Exam lore"); move both to his Knight of Boreas years if it differs.
- Yae's Sakura display: unseen in game; check placement, overlap with the guest/plan views, controller focus (`Vfx/Prototype/YaeSakuraDisplay.cs`).
