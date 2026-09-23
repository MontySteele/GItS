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

- Furina, round three: the Spend mode chooser needs `choose` twice; one call should resolve it (a scenario asserts one choose closes it).
- Furina, round three: reader faces print a literal 0 outside combat (Let the People Rejoice at Neow, Ousia Surge at a reward); print the rule outside combat, the number inside.
- Furina, round three: the Companion glossary alternates between the Stage's sentence and the shipped one on consecutive screens; hold one sentence per arm for the whole run.
- Furina, round three: mode-chooser option faces print sheet literals (unupgraded, unfolded under Weak); they should read the parent's folded, upgraded numbers, and the chooser should accept the hand's wording.
- Furina, round three: two copies of one arm card in hand print with no (1)/(2) numbering.
- Furina, round three: Let the People Rejoice's forecast can show a stale earlier spend; read the live bars at hand time.
- `EB-809` `KurageMemory.PriceText` prints bare `free` at price 0; print the derivation (`cost 0 x 3`) like every other price.
- `EB-808` a create-mode Muster never stamps its recruit's discount (`KokomiConscript.cs` `NoteMusterRecruit` is in the sacrifice branch only); stamp both branches.
- `EB-807` `Unknown RelicModel ID: RELIC.KLEEMOD-TAMANOOYAS_CASKET` once per boot: widen the retired-id alias register from cards to relics and arm-gated ids.
- `EB-805` a mode card's option title prints the sheet literal while the body folds the board (two numbers for one option); the title carries no number or folds through the same vars.
- `EB-801` eight shipped power faces are over the 125-char ceiling (`AuraPower`, `BurstMeterPower`, `EncoreMeterPower`, `FanfareMeterPower`, `FurinaBurstMeterPower`, `SalonMemberPower` x2); a text pass (design work, main session) until `lint_text_conventions --shipped` names none.
- `EB-798` `ProtoKkBreakwater` is offered Nimble but Nimble pays it nothing (its only Block is the Plan's); planned-only Block is not `GainsBlock`, in both engines and `lint_enchant_parity`.
- `EB-677` Glam's Replay on a timed card (Kyouka) runs it 4 turns at +4, not 2 at +8, and no face says which; needs an emitter change that gives the rule a tip surface, plus a taste call on which rows carry it.
- `EB-65` the four Furina power badges draw shrunk card portraits; they want badge-kind icons like Klee's (art bill, rank 1 applied).
- `EB-803` `proto_mc_kaeya_frostgnaw` wears Cold-Blooded Strike's named art (swap the two Kaeya picks); confirm `klee/relics/dodoco_tales.png` is packed on the next pck build.
- `EB-53` end-of-turn docket: capture the co-op half (`C6`) and isolate the electro (Oz) leg; needs a two-seat runtime.
- `EB-296` / `EB-300` controller: a live walk that the Kokomi pet is targetable by D-pad and mouse, and that the hand is reachable after a custom-target card.
- `EB-159` [USER] at the machine: listen for the modded player's death sound (`set_hp player 1`, end turn into a hit).
- `EB-38` [USER] at a shop: the spine-less character portrait idles (the rest-site half is seen).
- `EB-160` verify a live locale switch: the injected loc tables survive it, or a `LocException` names the seam.

## Harness, bridge and tools

- `EB-802` `understudy/twolane_frames.py` may carry the PrintWindow clip `frames.py` fixed; route it through the same capture, and make a frame-reading row refuse `complete: false`.
- `EB-799` `vendor/STS2_MCP/STS2_MCP.csproj` ignores `klee-mod/local.props`, so a bare `dotnet build` of the bridge fails in a worktree; read `local.props` (until then pass `-p:STS2GameDir=...`).
- `EB-800` the five arm test properties disagree on `The_arm_ships_off` (four `Skip`, `FurinaStage` an `#if`); pick one convention and say which in `operations/prototype.md`.
- `EB-489` bound the bridge's main-thread hop so one stalled frame cannot hang `/api/v1/singleplayer` for the life of the process.
- `EB-391` the `rest` verb sometimes fails its first call on an open rest site ("Rest site room is not open"); game-side race.
- `EB-208` the seed ledger ships empty: run the Klee three-body seed hunt and record the first entries.
- `EB-212` stage and seal real matched-telegraph pairs (identical but for the enemy intent) under `understudy/battery/pairs/`.
- `EB-193` `role_tempo_canon.json` predates the int-var reader fix; regenerate it (46 cards gain `has_body`).
- `EB-667` the Smith shows no upgrade for Ultimate Strike; its numbers are published nowhere the repo reads.
- `EB-71` no committed sheet prints `sly_autoplay`, so the `CardKeyword.Sly` rail has never run in game; whoever prints the first one checks it live.

## Sim and measurement (Balance stage; nothing here runs on a prototype)

- `EB-195` the next re-baseline window: one twelve-arm table carrying the HP moves, the `POLICY_VERSION` bump for `PILOT_BURST_DIVISOR`'s removal, `EB-255` and `EB-810`.
- `EB-255` `archetype_shares` excludes starters by rarity, so 13 starter rows read back as drafts; exclude by membership inside `EB-195`'s bump.
- `EB-810` the sim's act-2 Louse has no Curl Up 14; wire it inside `EB-195`'s bump.
- `EB-241` `Card.is_junk` is rarity-only; make it type- and namespace-aware at the Kokomi fold, with that fold's re-baseline.
- `EB-32` the pilot block-panic rung; lands under its own `POLICY_VERSION` bump and window.
- `M13` `ROUTE_REGRET_MARGIN` has no derivation (Option D, no margin, stands); draft the slate and build `C2` (`review/records/regret-margin-registration-2026-08-12.md`).
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).

## Parked: start only when the named trigger fires

- `EB-70` the starter-offer retune (`EB-27p`); wakes when a kit's design sweep reaches the Wings / Little Hexenzirkul class (R134).
- `EB-80` Kokomi prevention-on-curve review; wakes if a Kokomi playtest shows she needs more warding.
- `EB-33/34/35` repricing exhibits (The Gallery Stirs 0.0 at offer, Vulnerable as a flat debuff, no defensive term in `_reaction_value`); wake when the `_static_power` repricing session convenes.
- `EB-198` the Kurage HUD strip's blind read (half discharged, KURAGECAD-W1); wakes with the next blind round on the shipped Kokomi kit.
- `EB-651` a doubled `The other side` heading seen once and not reproduced; wakes on a sighting carrying the page sha.
- `EB-12` `bridge_unreachable` with the game alive, seen once; wakes on a second observation (`hangwatch` now classifies it).
- `EB-15` the seed's `lobby` route is unreachable in standard singleplayer; wakes with a Custom run or a hosted lobby.
- `SKIP-10.9` mechanics the sim does not model, promoted only on demand. Enemy: Back Attack, untargetable Burrow, Ethereal/Hex auras, pick-your-poison curses, damage caps (Hard to Kill, Plating, Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor powers, Soul Siphon stat theft, Blessed Antler, Philosopher's Stone. C# with no sim twin: the deferred-settle machinery (`SpotlightSystem`, `CurtainCallPowers`, `FurinaResources`) and per-dealer reaction windows (R1).
