# STS2_MCP — provenance

upstream: https://github.com/Gennadiyev/STS2MCP
pin: 55e0648
pin-subject: Fix game API compatibility with STS2 v0.107 (#123)
pin-date: 2026-07-29
license: MIT
license-holder: Yikun Ji (Kunologist)
vendored: 2026-08-04
vendored-by: Understudy sprint, work item W1
ruling: docs/archive/understudy-p0-findings.md ruling 1, RATIFIED by [USER] 2026-08-04

## Why this pin and not a release

The latest tagged release is **0.4.0, dated 2026-05-05**, and it predates our
game build. The pin above is the commit that carries the v0.107 compatibility
fix. As of EB-171 (2026-08-29) we ship against **v0.111.0**, which upstream has
no commit for at all — its tip IS this pin — so the four game-API repairs live
here as marked local edits and the pin does not move. Installing the release
binary instead of building this snapshot is the one way to reproduce the
version-pin failure the kickoff brief worried about — P0 stop-and-surface
item 2 says so, and this paragraph is where a hurried session is meant to
read it.

The in-tree `mod_manifest.json` still says `"version": "0.4.0"` and
`McpMod.Version` still says `0.4.0`; upstream did not bump either on this
commit. Neither string is a version pin. **This file is the pin.**

## Environment it was verified against

| Thing | Value |
|---|---|
| Game | **v0.111.0, commit 41cef1ea, dated 2026-08-13** (`public-beta`, buildid 24724944). Ported and re-verified 2026-08-29 under R218 / EB-171; it was v0.107.1, commit 59260271, dated 2026-06-18, through the vendoring and up to that day. |
| main_assembly_hash | **222455745** (was -1555940892 on v0.107.1) |
| Toolchain | .NET SDK 9.0.316, `net9.0` |
| Build | `dotnet build -c Release` against `data_sts2_windows_x86_64` — 0 warnings, 0 errors, re-verified on v0.111.0 |

## What was pruned from the snapshot

Carried: the C# mod (11 `McpMod.*.cs` files), `STS2_MCP.csproj`,
`mod_manifest.json`, `LICENSE`, `README.md`, and `docs/raw-simplified.md` +
`docs/raw-full.md` — the wire protocol, which is the contract `understudy/`
codes against and the thing a future session will actually need to read.

Dropped, and why:

- `mcp/` (the optional Python MCP server, `server.py` + `pyproject.toml` +
  `uv.lock`). We speak the HTTP API directly from `understudy/`; an MCP
  wrapper is a second client we would have to keep working for no gain.
- `build.ps1`. Superseded by `klee-mod/build/deploy_bridge.ps1`, which reads
  `GameDir` from our `local.props` like every other build path in this repo
  instead of an `STS2_GAME_DIR` environment variable, and which owns the
  install and uninstall steps upstream leaves to the reader.
- `STS2_MCP.sln`, `.github/`, `.claude/`, `AGENTS.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `.gitignore`, `docs/teaser.png` — upstream project
  furniture, not code we build or run.

Pruning is recorded rather than hidden: `UPSTREAM_MANIFEST.tsv` lists exactly
what we carry, and `tools/lint_vendor_pin.py` fails if the tree and the list
disagree in either direction.

## What we changed

**Five lines across two upstream files, EB-92's two guards in a third,
EB-171's four game-API repairs in that same third, EB-210's save-root
resolution in a fourth, and EB-184's mode-aware targeting in a fifth.**
Everything of substance lives in `gits/`, which the pin lint excludes from
the upstream hash list entirely.

**On EB-171's four in particular.** They are here rather than upstream because
upstream has no 0.111 commit to take: STS2MCP's tip IS our pin `55e0648`, whose
subject is the v0.107 compatibility fix. When a 0.111 fix lands upstream, the
refresh procedure below applies and these four are the first thing to compare
against it.

| File | Status | Change |
|---|---|---|
| `McpMod.cs` | `gits-modified` | **(a) the port's SOURCE (2026-08-29, `EB-206`).** `LoadPort` consults `STS2_MCP_PORT` from the ENVIRONMENT before the conf file, then the conf, then 15526, and prints which of the three won. The decision itself lives in `gits/GitsPort.cs`; the conf half here is upstream's byte for byte, including the write-a-default-conf side effect, and with the variable absent the behaviour is upstream's exactly. `DefaultPort` now aliases `GitsPort.DefaultPort` so the fallback the resolver uses and the value the written conf carries cannot drift. WHY: two `SlayTheSpire2.exe` processes launched from ONE install share one `STS2_MCP.conf`, because the conf lives beside the dll inside the game directory — one conf is one port and the second listener loses. An environment variable is per-PROCESS, so the funnel's second lane gets its own bridge with no second copy of the game. **(b)** Five `else if` arms on the `HandleRequest` route chain — `/api/v1/gits/speed` (W2), `/api/v1/gits/seed` (P1.5), `/api/v1/gits/give_card` (EB-52), `/api/v1/gits/debug_state` (EB-142) and `/api/v1/gits/meter_ledger` (EB-216) — marked in-file with `GItS LOCAL EDIT`. Nothing else in the file is touched. |
| `McpMod.Compendium.cs` | `gits-modified` | **`EB-210` (2026-08-29) — where a save file is looked for, and it is four lines plus a candidate.** `BuildCurrentRunContext` reads the run's seed by OPENING `current_run.save`, and `ResolveCurrentRunPath` asks `GetSaveDirectoryFromProgressPath` first. That method required `Path.IsPathRooted`, but `ProgressSaveManager.GetProgressPathForProfile` answers a GODOT path (`user://steam/<id>/modded/profile1/saves/progress.save`, exactly as godot.log prints it) — so it returned null on every call and every resolution fell through to `EnumerateSteamDataRoots`, which builds its candidates from `Environment.GetFolderPath(SpecialFolder.ApplicationData)`. **That API reads the SHELL's roaming folder and ignores the `APPDATA` environment variable**, which is the one and only thing separating two lanes' user trees (`understudy/instances.py`). Godot honours the variable and this does not, so with two game processes up BOTH read lane 0's save: `KLEESPARK-R2`'s two-lane attempt asked for one seed, was answered with the other lane's, and filed `seed_not_honoured` against a game whose own log shows it embarking on the seed it was given. The fix is to GLOBALIZE a `user://` path through Godot before the rooted check — which is what the method always meant, and resolves against the running process's own user directory — with the `APPDATA` variable added FIRST among the enumerator's candidates as the belt. Both marked in-file with `GItS LOCAL EDIT`. Upstreamable as-is: any second instance of the game does this to upstream's compendium. |
| `McpMod.Wiki.cs` | `gits-modified` | EB-92 (2026-08-13) — two guards in the result formatter, marked in-file with `GItS LOCAL EDIT`. Every mod-card query answered `500 ... Canonical model of type <generated class> used in incorrect place`, a different class each time: the formatter walks `ModelDb.AllCards` (where mod cards live) and reads properties off the CANONICAL instance, and one throwing card took the whole search down — including the base-game rows that had formatted fine. `BuildWikiResultSafely` degrades a throwing candidate to one row carrying id/name/score/`error`, and the hover-tip read degrades to empty. Neither guard fixes the throwing card, and the degraded row names it. Upstreamable as-is: any mod's custom model can do this. |
| `McpMod.StateBuilder.cs` | `gits-modified` | **(a)** One line in `BuildPlayerState`, inside the live-combat block: `state["resources"] = GitsResourceSnapshot(combatState)`. Marked in-file with `GItS LOCAL EDIT`. P1.5 spec item 2. **(a2) `EB-181` (2026-08-29):** one guarded block beside it emitting `state["kurage_memory"]` when the build carries the quarantined Kurage-memory rule, marked the same way; see `gits/GitsKurageMemory.cs`. **(b) EB-171 (2026-08-29), the v0.111.0 lobby port — four reads and one helper, all marked.** `StartRunLobby.MaxPlayers` was REMOVED and has no public replacement: the number survives only as the private readonly `_maxPlayers` the constructor stores, which the lobby's own code compares `Players.Count` against, so `max_players` is now a guarded reflection read (`StartRunLobbyMaxPlayers`) returning `int?` — null where it once could not fail, so a reader can tell "the game stopped exposing it" from "one seat". `LoadRunLobby.ConnectedPlayerIds` was also removed, and there the replacement is exact rather than inferred: the lobby now holds `List<LoadRunLobbyPlayer> Players`, populated by the join-response handler and `OnConnectedToClientAsHost` and emptied on disconnect — i.e. the connected set, by construction — with `PlayerCount` and `PlayerIds` over it. The three reads take those: the count becomes `lobby.PlayerCount`, the readiness derivation takes `lobby.PlayerIds`, and the per-player `is_connected` becomes a membership test on `Players`. No wire key changed name or meaning. **(c) the Klee Sparks arm (2026-08-29) -- two lines in `BuildCardState`, marked.** A hand card carrying a Spark price gains `spark_price` and `spark_affordable`. Nothing already on the wire stood in: `cost` is the ENERGY cost and is 0 for every Spark-priced card, and `can_play` folds every refusal into one boolean, so a seat could not tell a short bank from a missing target. The pair is OMITTED for a card that charges nothing, so an absent key means "charges none" and no existing board grew. |
| `McpMod.Actions.cs` | `gits-modified` | **`EB-184` (2026-08-30) — who is asked whether a play needs a target.** `ExecutePlayCard` decided that with one test, `card.TargetType == TargetType.AnyEnemy`, and refused a play carrying no `target` with *"Card requires a target"*. On a `choose_one` card that is the wrong witness: the game aims a card BEFORE its mode is chosen (`TargetType` is the CardModel's, the choose-a-card screen opens inside `OnPlay`, and the 0.111.0 decompile has no mid-play enemy picker), so an Attack-typed modal MUST declare `AnyEnemy` for the sake of the mode that aims — and the targetless Block half of `proto_thoma_crimson_ooyoroi_either` was then refused too. Kokomi slice 1 round 4 `t02` ended UNTESTED on exactly that and the pair read RETURNED the arm. The edit reads an OPTIONAL `mode` off the play, matches it against the card's own printed mode labels (`gits/GitsModalTargeting.cs`), and derives the refusal from THAT mode: an aiming mode with no target is refused exactly as before, a targetless mode is played at the inert aim the game's own play path wants and the mode discards, and a play naming no mode reaches upstream's rule untouched. Marked in-file with `GItS LOCAL EDIT`. An edit rather than a Harmony patch for EB-92's reason: the decision is three statements inside one private method, and a patch would have to re-implement the whole of `ExecutePlayCard` to reach them. |
| `gits/GitsPort.cs` | GItS addition | `EB-206` — the port resolver, `env > conf > default`, returning the port AND the source that won so the game log can say where the bridge is actually listening. Deliberately free of Godot, Harmony and game types: it is the one piece of the two-instance story that must be right the first time and can be exercised headlessly, and `klee-mod/KleeTests/GitsPortPrecedenceTests.cs` compiles THIS file (not a fork of it) to do so. An unparseable or out-of-range environment value falls through to the conf and NAMES itself in the note rather than binding a default silently — a lane quietly landing on the other lane's port is the failure the whole file exists to prevent. Reads nothing from disk; `McpMod.LoadPort` does the file I/O and hands the text in. |
| `gits/GitsSpeed.cs` | GItS addition | Work item W2 — the speed affordance. EB-87 (2026-08-12): the captured original `FastMode` is persisted to `GitsSpeed.original.conf` in the mod directory (next to the `STS2_MCP.conf` this file's neighbours already write — JSON content under a `.conf` name, because ModManager parses every `*.json` under `mods/` as a manifest), a later process restores from that sidecar instead of re-capturing, and a successful disable deletes it. `PrefsSave.FastMode` persists to `prefs.save` (not `settings.save` — corrected 2026-08-13 by the round-2 correctness audit, along with the mechanism: prefs are flushed only by `NGame.Quit()` or `NSettingsScreen.OnSubmenuClosed`, neither reachable from a `TerminateProcess` kill, and `NGame` demotes a persisted `Instant` to `Fast` on every non-editor boot, so no second process can read `Instant` back. The reproducible laundering is one step narrower: after a flush, a second process captures the demoted `Fast` and "restores" a `Normal` user to `Fast`. The sidecar is the right fix for that; only its stated justification was wrong). `TimeScale` is deliberately not persisted — `Engine.TimeScale` starts at its default in every process, so the live capture is already the right original. |
| `gits/GitsSeed.cs` | GItS addition | P1.5 item 1 — the chosen-seed endpoint. Documents in-file why upstream's own `charSelect.Lobby == null` refusal does not describe the game. |
| `gits/GitsSparkPrice.cs` | GItS addition | The Klee Sparks arm -- a reflection-only reader for `KleeMod.Powers.SparkCost`, feeding `BuildCardState`'s `spark_price` / `spark_affordable`. Same posture as `GitsResources.cs` and for the same reason: a compile-time reference would make this bridge refuse to load with no klee mod present, and reflection makes "no klee mod" mean "no Spark prices", which is the truth. Probed once, the null cached with the hit, every failure swallowed -- a state read must never throw. It reads the SAME expression the card's `IsPlayable` gate and the in-game cost badge read, so the wire, the face and the charge are one number by construction. Read-only. |
| `gits/GitsKurageMemory.cs` | GItS addition | `EB-181`, the Kokomi half (2026-08-29) - a reflection-only reader for the klee mod's QUARANTINED Kurage-memory rule (`KleeMod.Powers.KurageMemory.Snapshot`, compiled only under `-p:PrototypeCards=true`). No compile-time klee reference: the type is absent from a release `klee.dll` and a hard reference would refuse to load against one. A missing type yields a NULL snapshot, and `BuildPlayerState` then omits the key entirely - so an absent `player.kurage_memory` means "this build has no memory rule" and an empty map means "the rule is here and this player is not Kokomi". Read-only; the field names are documented on the mod-side method and are read by `understudy/blindplay.py`. |
| `gits/GitsMeterLedger.cs` | GItS addition | `EB-216` / R225 (2026-08-30) — a reflection-only reader for `KleeMod.Diagnostics.MeterLedger.Snapshot`, served at `/api/v1/gits/meter_ledger`, GET only. The per-play meter ledger: bank before, price paid, gains BY SOURCE, bank after. It is a SEPARATE ROUTE and not a key on `player` because the state payload is what the blind driver builds the TESTER'S PAGE from, and the ledger names engine events in a developer's vocabulary (`relic:pounding_surprise/detonation`, `rule:threshold_consume`) — the shortest way to keep it off a grading surface (R101b) is for it never to arrive on the same payload. Same reflection posture and same failure mode as `GitsResources.cs` and `GitsKurageMemory.cs`; `available: false` with an empty list means "no klee mod in this build", which is a different fact from "nothing has moved a meter yet". `meter` is a field, so Charge and Encore take the same rows later. Read-only. |
| `gits/GitsModalTargeting.cs` | GItS addition | `EB-184` — the per-mode aiming reader. Reflection-only, on the same posture as `GitsResources.cs`: the bridge holds no compile-time reference to the klee mod, so it reads `ModeLabels` and `ModeAimsAtChosenEnemy` by NAME off the played card's runtime type (`KleeMod.Cards.IModalCard`, emitted for every `choose_one` row by `tools/gen_klee_cards.mode_aims`). A card from another mod, or from the base game, answers "not modal" and the card-type rule stands. It also owns the label match — exact first, then a unique substring, and ambiguity is REPORTED rather than guessed at, because guessing which mode a form meant is choosing a line for the reader. Read-only; decides nothing about the play beyond whether a target is owed. |
| `gits/GitsForceEvent.cs` | GItS addition | `EB-761` — the arithmetic behind `force_next_event`, and nothing else: given the act's pending event ids, `eventsVisited` and a target id, where the target sits and which slot `ActModel.PullNextEvent` reads next. Deliberately free of Godot, Harmony and game types, on `GitsPort.cs`'s terms and for the same reason — the one decision the op makes has exactly one way to look right and be wrong (`RoomSet.NextEvent` is `events[eventsVisited % events.Count]`, NOT `events[0]`, and an op writing index 0 would answer ok, move a real entry, change nothing about the next room, and still pass a smoke on floor 1 where the cursor happens to be 0). `klee-mod/KleeTests/GitsForceEventTests.cs` compiles THIS file, not a fork. It also owns the SWAP: a swap and never an insert, because the list's length is what the cursor's modulo divides by and an insert would renumber every slot behind it, changing which event every later `?` room in the act opens. Knows nothing about a run; the two run-dependent refusals are `GitsDebugState`'s. |
| `gits/GitsSkipAct.cs` | GItS addition | `EB-771` — the decision behind `skip_act`, and nothing else: given the run's act ids, its `CurrentActIndex`, whether a combat is up, whether the current room is the victory room and how deep the room stack is, whether the run may leave its act right now and which act it lands in. Deliberately free of Godot, Harmony and game types, on `GitsPort.cs`'s and `GitsForceEvent.cs`'s terms and for the same reason — three of its four refusals are states that are expensive to reach deliberately with a live game (a run inside an event's own sub-combat, a run in its victory room, a run in its last act), which is to say they are exactly the refusals that would otherwise be discovered by an attended session losing its run to them. The fourth, THE LAST ACT, is the one that would not look like a failure at all: `RunManager.EnterNextAct` does not refuse there, it opens The Architect's room, so an op without the check would answer ok and land the run somewhere nobody asked for. EB-771 adds no act-4 path. `klee-mod/KleeTests/GitsSkipActTests.cs` compiles THIS file, not a fork. Knows nothing about a run; reading the live one and making the native call are `GitsDebugState`'s. |
| `gits/GitsResources.cs` | GItS addition | P1.5 item 2 — a reflection-only reader for BaseLib's custom-resource registry. No compile-time BaseLib reference; a missing BaseLib yields an empty map. |
| `gits/GitsGiveCard.cs` | GItS addition | EB-52 — the dev-only card-injection route. Selects a card out of `ModelDb.AllCards` and hands it to the game's own acquisition path; mints nothing. **EB-91 (2026-08-13): the CARD SCOPE now follows the pile.** Deck grants are created in `player.RunState`; combat-pile grants in `player.Creature.CombatState`, which is what every in-combat generator does (`CollisionCourse`, `CardFactory.GetForCombat`). A run-scoped card handed to `AddGeneratedCardToCombat` arrived in hand and read back fine, then threw `must be added to a CombatState before playing it` out of `CardPileCmd.AddDuringManualCardPlay` and wedged the fight. The `route` field, which reported the static string `card_pile_cmd` for both branches, now names the branch that ran (`run_state_create+card_pile_add` / `combat_state_create+add_generated_to_combat`) and a `scope` field says `run`/`combat`. |
| `gits/GitsDebugState.cs` | GItS addition | EB-142 — the dev-only board-setup route, and the second half of the targeted-scenario door `GitsGiveCard` opened. **Ten ops** (`set_resource`, `set_energy`, `set_hp`, `set_block`, `set_power` since EB-146, `clear_hand` since EB-165, and `hover` / `unhover` since EB-652), singleplayer and in-combat only, each going through the game's OWN mutator for that number: `CreatureCmd.SetCurrentHp`, `PlayerCmd.SetEnergy`, the registered `CustomResource`'s own `Amount` setter, `Creature.LoseBlockInternal`/`GainBlockInternal` (the one hook-free write — there is no `CreatureCmd.SetBlock`, and routing a debug set through `GainBlock` would run the `ModifyBlockGained` chain over the number the caller asked for), and `PowerCmd.Apply`/`ModifyAmount`/`Remove`. `why` is a REQUIRED field, logged with every write. **EB-142's header refused power application** — `PowerCmd.Apply` wants a `PlayerChoiceContext` and an applier, and inventing an applier is minting rather than selecting. **EB-146 answered both without inventing anything:** the context is the game's own `ThrowingPlayerChoiceContext` (what `PowerCmd.Decrement` passes, for the case where no player choice can open below), and the applier is **null** — `SparkPower.Spend`'s own precedent, which keeps a bookkeeping write out of the `ModifyPowerAmountGiven` chain so nothing can inflate or shrink the exact number. The cost is stated in-file: a power that reads its `Applier` sees null, and an `InstancedPerApplier` power gets a pile owned by nobody, which is why more than one instance of the named power on the creature is a REFUSAL rather than a guess. Enemy spawning is the one follow-up left, and the file header still names it. **EB-165 adds `clear_hand`, the one op that moves a CARD rather than a number:** it empties the local player's hand to the BOTTOM of the draw pile through `CardPileCmd.Add(card, PileType.Draw, CardPilePosition.Bottom)` — the pile move that sits underneath both `CardCmd.Discard` (which is that same call plus `History.CardDiscarded` plus `Hook.AfterCardDiscarded` plus the Sly collection) and `CardCmd.Exhaust`, so no on-discard and no on-exhaust trigger fires and no combat-history row is written. `Hook.AfterCardChangedPiles` still fires, stated rather than hidden, because every pile move in the game runs it and there is no route out of hand beneath it. Draw rather than discard because a discard pile is READ by cards; nothing is destroyed, and `CardPile.Clear` is deliberately not used because a card in no pile at all is the wedged-fight shape. It takes no `who` and no `amount`; an already-empty hand answers `queued: false` rather than an error. **EB-652 adds `hover` and `unhover`, the only two ops here that write no game state at all:** they call `RunManager.Instance.HoveredModelTracker.OnLocalCardHovered(card)` and `OnLocalCardUnhovered()` -- the pair `NPlayerHand` itself calls on every hand hover and release, and the pair `KleeCode/Vfx/Prototype/SalonPanel.cs` patches (`EB-637`) -- so a panel reacts to the route exactly as it reacts to a mouse and there is no second "debug hover" path to keep in step. They exist because Furina's Salon panel says something different while a card is under the cursor (FRONT becomes PERFORMS for a Companion, LEAVES with a bright footer for a Deploy onto a full stage, ENTERS for one onto a stage with room, tinted pips for the Spotlight) and a scenario could set up the BOARD that panel draws but not the HOVER, so half of its words were unreviewable except at the machine with a mouse. `hover` names its card by wire id or printed Title and takes the FIRST match in hand -- three copies of one Deploy is the ordinary case and they paint the same panel -- and `unhover` takes no card because the tracker's own release takes none. The guardrail rides on both answers unchanged: not writing state does not buy a hand-set board back its comparability. `GitsResources.cs` stays a read-only serialiser; the resource WRITE lives here and reuses that file's cached registry probe. **EB-761 adds `force_next_event`, the ONE op here that is not a combat write and the one that runs with no combat up:** it puts a named event at the current act's event cursor so the next `?` room opens on it. The seam is `RoomSet.events` — shuffled ONCE by `RunManager.GenerateRooms` at run start, then read at a moving cursor (`events[eventsVisited % events.Count]`) by `ActModel.PullNextEvent` — so the op swaps two entries in a list that was already this run's and CONSUMES NO RNG: every later room, reward and encounter is still the one the seed would have produced, and nothing is minted, because the event was already pending in this act. It exists because the Teyvat spike could not reach one named event at all (`review/records/teyvat-spike-proofs-2026-09-15.md`, item 2): there was no event op, and `understudy/scenario.py` wakes on a COMBAT screen so it cannot stand on a map. The cursor is NOT index 0 and that is the one error that would look like it had worked; the arithmetic therefore lives in `gits/GitsForceEvent.cs`, which `klee-mod/KleeTests/GitsForceEventTests.cs` compiles. Four refusals: no run, an id this act has no event for, an event this run has already visited, and one whose own `IsAllowed` is false — the last two because `EnsureNextEventIsValid` walks the cursor past both BEFORE the read, so the write would land, answer ok, and the room would open on something else. The act's `RoomSet` is reached by a cached reflection read of the protected `ActModel._rooms` (the class exposes `PullNextEvent` and the boss, never the event list); a null answer is a refusal naming the moved field, not a guess. The GET now also reports `events`, `events_visited` and `next_event` whenever a run is up, combat or not. **EB-771 adds `skip_act`, the second RUN op and the first op on this route that MOVES THE RUN'S RNG:** it ends the current act at the next map step and lands the run on the next act's map. The whole write is `RunManager.Instance.ActChangeSynchronizer.SetLocalPlayerReady()` — exactly what `NRewardsScreen.OnProceedButtonPressed` calls on a terminal BOSS rewards screen — so in a singleplayer run the vote is unanimous at once and the game runs `RunState.ActFloor++` and `RunManager.EnterNextAct()`, which is `EnterAct(CurrentActIndex + 1)`: fade, clear screens, exit rooms, `SetActInternal` (index, visited coords, odds reset, `PreloadManager.LoadActAssets`, `GenerateMap`, music, rich presence), then a `MapRoom` and `Hook.AfterActEntered`. Nothing is faked: no boss clear is simulated, no `ActModel` is constructed, `CurrentActIndex` is never written by hand and no map is invented — and NO ACT ROLL IS RE-TAKEN, because `RunState.Acts` was built once at embark by `ActModel.GetRandomList`, so `Acts[CurrentActIndex + 1]` is the DRESSED Teyvat face this seed already chose (Natlan or Inazuma at the Hive's index, Fontaine or Sumeru at Glory's). It exists because the Teyvat frame's four act-2/3 dressings could otherwise only be seen by a bot surviving act 1 and beating its boss (`review/records/teyvat-proofs-5-2026-09-15.md`). **Unlike `force_next_event` it is NOT rng-neutral and says so instead of claiming otherwise:** the floors it skips are floors whose rolls — room types, encounters, rewards, card offers, the act boss itself — never happen, so every act-scoped stream is read from a different position afterwards; the acts and their room sets were generated up front and are untouched, and the new act's map is generated at the transition, which is when the game would have generated it anyway. Four refusals: a combat in progress (the transition would tear the room stack down under a live combat state), a room stack deeper than one (the run is inside a sub-room it still expects to return to), the victory room (the game calls `WinRun` there, not `EnterNextAct`), and THE LAST ACT — where `EnterNextAct` does not advance at all but opens The Architect's room. **There is no act-4 path.** The decision lives in `gits/GitsSkipAct.cs`, which `klee-mod/KleeTests/GitsSkipActTests.cs` compiles; the answer is `queued: true`, because the transition resolves over frames. The GET now also reports `acts`, `act_index`, `act` and `next_act` whenever a run is up. |

Everything else is byte-identical to `55e0648`.

The route arms are edits rather than Harmony patches because upstream's
routing is a plain if/else chain in one method: patching it would mean
rewriting the same chain from outside, in more code, less legibly, to protect
a purity we can simply record instead. The `BuildPlayerState` line is an edit
for the same reason and one more: a resources map attached out-of-band by a
patch would not be ATOMIC with the state read it belongs to, and a meter read
a frame after the hand it describes is a different measurement.

## The additions, and what they do NOT change

**No addition changes a rule.** Each one SELECTS state the game's own
generators can produce, or reports state the game already holds:

- `GitsSeed` selects which run the game's own generators produce, through the
  game's own `StartRunLobby.SetSeed` / `NGame.DebugSeedOverride`.
- `GitsResources` is a serialiser that never writes an `Amount`.
- `GitsGiveCard` selects a card that is already in `ModelDb.AllCards` — the
  same registry `McpMod.Wiki.cs` enumerates — and hands it to the game's own
  acquisition machinery: `RunState.CreateCard(canonical, player)` then
  `CardPileCmd.Add(card, PileType.Deck)`, which is exactly what
  `CardReward.OnSelected` and `CardPileCmd.AddCursesToDeck` run. It never
  constructs a card object of its own, and in-combat grants take the
  combat scope's `CreateCard` then `AddGeneratedCardToCombat`, which is the
  pair every in-combat generator in the game runs and which writes the
  combat-history row too.

- `GitsDebugState` writes five combat numbers, moves one pile of cards and
  reorders one list the run already held, and
  does each one through
  the mutator the GAME already uses for it — `CreatureCmd.SetCurrentHp`,
  `PlayerCmd.SetEnergy`, the resource's own `Amount` setter (the property
  BaseLib's own gain and spend paths write), the creature's own
  block-internal pair, and `PowerCmd.Apply` / `PowerCmd.ModifyAmount` /
  `PowerCmd.Remove`, which are the three commands every card in the game
  applies, stacks and clears a power with, and `CardPileCmd.Add` for
  `clear_hand`, the pile move that sits underneath the game's own discard and
  exhaust routes. It adds no mutator the game does
  not have and spawns no enemy. It DOES now apply a power (EB-146) — out of
  `ModelDb.AllPowers`, which is the same registry `McpMod.Wiki.cs` and
  `KleeSelfCheck` already enumerate, so the power selected is one the game
  already holds and nothing is constructed here either.

  Since `EB-761` it also writes the ACT rather than a combat, once:
  `force_next_event` swaps two entries of `RoomSet.events` so the named event
  is the one at the cursor `ActModel.PullNextEvent` reads. That list was
  shuffled once at run start by `RunManager.GenerateRooms` and is read at a
  moving index thereafter, so the swap takes no roll — the rng stream does not
  move and every later room is still the seed's — and selects rather than
  mints: the event was already pending in this act. The act's `RoomSet` is
  reached by a cached reflection read of the protected `ActModel._rooms`, the
  one binding here that is not a public member, because the class exposes
  `PullNextEvent` and the boss and never the event list itself.

No constant, generator, reward table or pilot is touched by any of them.

**`GitsDebugState` is dev-only on the same terms, and says so in the same
field.** A combat whose board was set by hand is not a board the game's own
play produced, so nothing measured on it is comparable to any other run; every
successful write carries the `guardrail` field saying so, `why` is a required
request field rather than an optional one, and the write is printed to the
game log with its reason beside it. It refuses multiplayer for `GitsGiveCard`'s
reason verbatim (no action-queue synchronizer, so peers diverge), refuses when
no combat is in progress (every op writes combat state, so out of combat the
write would be a silent no-op wearing an `ok`), and refuses `set_hp` at zero or
below — `SetCurrentHp(0)` leaves a creature at zero without running the death
path, which is a wedged fight wearing an `ok`, EB-91's exact shape. `set_power`
adds five refusals of the same kind and for the same reason — an unknown power
id (no fuzzy match, the resource arm's rule one badge over), a printed TITLE two
registered powers share, a creature whose `CanReceivePowers` is false (PowerCmd
would return early, which is the silent no-op again), a negative amount on a
power that does not allow negatives (the game removes such a power at 0 or
below, so the write would land as a REMOVAL wearing the number that was asked
for), and a creature carrying more than one instance of the named power (an
`InstancedPerApplier` power keeps one pile per applier and a debug set cannot
choose which pile).

**`GitsGiveCard` is dev-only in a way the wire says out loud.** A run that
used it is no longer a run the generators produced, so nothing measured on it
is comparable to anything; every successful grant carries a `guardrail` field
saying so, and `understudy/bridge.py` stamps the same sentence on the harness
log. It refuses multiplayer outright (the pile add does not go through the
action-queue synchronizer, so peers would diverge) and refuses a combat pile
when no combat is in progress (the game's own path would return an empty list,
i.e. a silent no-op wearing an `ok`).

## Refreshing the pin

1. `git clone https://github.com/Gennadiyev/STS2MCP && git checkout <new sha>`
2. Copy the carried files over this directory (the list is
   `UPSTREAM_MANIFEST.tsv`, `status == upstream`).
3. Re-apply the `McpMod.cs` route arms above — there are **four** of them now
   (speed, seed, give_card, debug_state), all inside one marked block. A refresh that
   re-applies two of three leaves a handler in `gits/` that nothing routes to,
   and the pin lint cannot see that: it checks hashes and markers, not whether
   a route exists. Grep the refreshed `McpMod.cs` for `gits/` and count.
   **Re-apply `LoadPort` too**, and it is the easier one to lose because it
   looks like upstream's: the environment must be read BEFORE the conf, and
   `GitsPort.Resolve` must be what decides. A refresh that drops it leaves
   `--lanes 2` silently binding one port for both games, which reads as the
   second lane's bridge simply never coming up.
4. Update `pin`, `pin-subject`, `pin-date` and the environment table here.
5. `python tools/lint_vendor_pin.py --write`, and **read the diff** — if it
   touches more than you meant, that is the finding.
6. Rebuild and re-verify against the game version in the table.

**What a refresh may break in `gits/`, which the lint also cannot see.** These
files name game APIs by hand, and upstream STS2MCP is not what would move them
— the GAME is. `GitsGiveCard` binds `ModelDb.AllCards`, `ICardScope.CreateCard`
on both `RunState` and `Creature.CombatState`, `CardPileCmd.Add` /
`AddGeneratedCardToCombat`, `CardCmd.Upgrade` and `LocalContext.GetMe`
(note `ICombatState` declares `CreateCard` itself and does not derive from
`ICardScope`, so the combat scope is reached with `as` — a game-side merge of
those two interfaces would silently turn the grant into the refusal branch); `GitsSeed` binds `StartRunLobby.SetSeed`,
`NGame.DebugSeedOverride` and `SeedHelper.CanonicalizeSeed`; `GitsDebugState`
binds `CreatureCmd.SetCurrentHp`, `PlayerCmd.SetEnergy`,
`Creature.LoseBlockInternal`/`GainBlockInternal`, and — since EB-146 —
`ModelDb.AllPowers`, `AbstractModel.Id.Entry`, `PowerModel.Title`,
`PowerModel.AllowNegative`, `PowerModel.ToMutable`, `Creature.CanReceivePowers`,
`Creature.GetPowerInstances`, `PowerCmd.Apply` (the NON-generic overload, which
is the only one reachable when the type is resolved at runtime),
`PowerCmd.ModifyAmount`, `PowerCmd.Remove` and
`ThrowingPlayerChoiceContext`; and — since EB-761 — `RunState.Act`,
`RunState.VisitedEventIds`, `EventModel.IsAllowed`, `RoomSet.events`,
`RoomSet.eventsVisited` and the protected `ActModel._rooms` (by reflection,
cached, and a null answer is a refusal naming the moved field rather than a
guess); and `Creature.Monster.Id.Entry`
(the last of which it uses to re-synthesise the wire's `entity_id` the way
`McpMod.StateBuilder.BuildEnemyState` does — if those two spellings ever
diverge, a scenario's target is a creature nobody chose, and the build will not
say so). A game-version bump is the event that invalidates those, and the check
is the build: it fails loudly, which is the good case. **The 0.111.0 bump is the
first time that actually happened, and `gits/` came through it untouched** — all
four errors were in `McpMod.StateBuilder.cs`, none in any file above, and the
whole directory recompiled clean against the new assemblies (EB-171).

Upstreaming the speed endpoint stays open; MIT does not require it and this
sprint did not spend time on it.
