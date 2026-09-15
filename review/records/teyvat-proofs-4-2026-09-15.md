Status: RECORD (deploy proofs phase six and seven; feasibility only, nothing measured)

# Act 1 plays, two dressed events break it, and act 2 has no door

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
Loadout and profile untouched; nothing deployed or rebuilt.

**Installed, read off the wire.** `0.2.3314+proto`, arm ON, banner `[v0.111.0]
(2026.08.14) MODDED (3)` in every frame. Boot line, every launch: `[INFO] [klee] teyvat:
loc merged (1 dressed enemy name(s), 0 dressed intent word(s), 477 converted-event
row(s))`. All six dressings register a background factory at boot (`[BaseLib] Registered
scene 'res://scenes/backgrounds/<act>/<act>_background.tscn' for auto-conversion to
NCombatBackground` — mondstadt, liyue, natlan, inazuma, fontaine, sumeru).

**Eight runs, all Ironclad, one embark each** (`understudy.embark`, FastMode=Instant,
TimeScale=3.0 — the harness's standard soak speed). Seed / act:

| # | seed | act | what it was for |
|---|---|---|---|
| 1 | `VAV1Z554HR7Z` | LIYUE | SELF_HELP_BOOK — softlocked the run |
| 2 | `YFL1S1J597KN` | LIYUE | two incidental dressings; died to an elite, floor 7 |
| 3 | `03GNYEUFSYA5` | LIYUE | cheese, scriptorium, bridge, two rest sites; died to the act-1 boss |
| 4 | `67GP8H9Y49BY` | MONDSTADT | cheese cellar read in full; rest site |
| 5 | `PU2LR21QLSC6` | MONDSTADT | tea master |
| 6 | `D70E99HBXK2M` | MONDSTADT | PUNCH_OFF not in this act's pool; died floor 7 |
| 7 | `BN0E74EEWYV5` | LIYUE | PUNCH_OFF — **hung the game** |
| 8 | `JTL7CHWLLM9W` | MONDSTADT | map-header and combat frames |

## PHASE SIX

### 1. The six dressed act-1 events — 4 PASS, 2 FAIL

**ROOM_FULL_OF_CHEESE — PASS.** Mondstadt, run 4: *The Springvale Cheese Cellar*.
`frame-20260915-171237-teyvat-room_full_of_cheese.png` shows the dressed title, a dressed
body paragraph ("A collapsed stair below Springvale opens onto a dairy cellar the Guild's
commission board never got around to delisting…"), a drawn portrait (the base event's
cellar art — the acceptable fallback), and both options dressed: *Taste the Racks* /
"Choose 2 of 8 random Common cards… The eight wheels offered are never duplicates", and
*Haul Out the Back Wall* / "Lose 14 HP… Obtain The Anointed Wheel (The Chosen Cheese)…".
Taste the Racks completed to the card-select screen. Liyue's dressing also opened (run 3,
option *Gorge*, completed). **The wire's `body` is null while the body is on the screen** —
that is the bridge read, not the content, as reproof-2 read it for Neow.

**WATERLOGGED_SCRIPTORIUM — PASS.** Liyue, run 3: *The Flooded Ledger-Room*, floor 8.
Three dressed options — *Bloody Ink* "Gain 6 Max HP", *Tentacle Quill* "Pay 55 Gold.
Enchant a card with Steady.", *Prickly Sponge* "Pay 99 Gold. Enchant 2 cards with Steady."
— each with keyword tips. Bloody Ink completed to Proceed and back to the map.

**TEA_MASTER — PASS.** Mondstadt, run 5: *The Angel's Share's Tasting Flight*, floor 15.
Three dressed options, and the dressing reaches the price line — "Pay 50 Gold (Mora)",
"Pay 150 Gold (Mora)". Bone Tea completed to Proceed.

**SLIPPERY_BRIDGE — PASS, with a text defect.** Liyue, run 3: *The Rope Bridge Below Dunyu
Ruins*, floor 14. Both options present, *Hold On* carrying its full dressed paragraph. But
**option 0 reads `" is removed from your deck."` — the card name is missing, leaving a
leading space** — while its keyword tip names Headbutt correctly. It still completed to
Proceed. New defect, below.

**SELF_HELP_BOOK — FAIL, and it softlocks the run.** Liyue, run 1: *Six Contracts to a
Better You*. The page opened with **no title** (the wire returned the raw loc key
`events.SIX_CONTRACTS_TO_A_BETTER_YOU.title`), **no body, no portrait and zero options**;
`frame-20260915-162857-teyvat-six-contracts-no-options.png` is a blank screen below the
HUD. `proceed` answered "No proceed button available or enabled" and `advance_dialogue`
"No ancient dialogue active" — **the run cannot leave the room.** Three stacks, in the
archived `godot2026-09-15T16.29.37.log`:

```
ERROR: No loader found for resource: res://images/events/six_contracts_to_a_better_you.png
[ERROR] System.NullReferenceException … at CharacterModel.AddDetailsTo(LocString str)
        at EventOption..ctor … at SelfHelpBookMirror.GenerateInitialOptions()
[ERROR] AssetLoadException: Asset previously failed to load: …six_contracts…png
        at EventModel.CreateInitialPortrait() … at NEventLayout.SetEvent_Patch1
```

**Cause,** handed over by the main session and matching what I read on disk: the
generator's slug rule split only lower-to-upper boundaries, so `TeyvatEventsGenerated.cs`
keys the rows `SIX_CONTRACTS_TO_ABETTER_YOU.*` while the game's `StringHelper.Slugify`
underscores every capital and asks for `SIX_CONTRACTS_TO_A_BETTER_YOU.*`. Every row for
this dressing misses, the option constructor NREs on the absent LocString, and no option is
built. `SixWeeksToABetterYouIlluminated` (Sumeru) and `CoralMirrorRorriMLaroCEhT`
(Fontaine) are keyed wrong the same way. **The fix is on branch `teyvat-slug-fix`**; it is
not in the installed build, so I did not retry this event.

**PUNCH_OFF — FAIL, and it hangs the process.** Liyue, run 7, floor 6. The force was
accepted (`force_next_event LIYUE PUNCH_OFF: index 11 -> slot 1`) and the room entered —
`[INFO] Creating NCombatRoom with mode=VisualOnly encounter=PUNCH_OFF_EVENT_ENCOUNTER.` —
and then the engine ran out of RIDs inside the mirror's own animation loop:

```
ERROR: Element limit reached.   at: _allocate_rid (./core/templates/rid_owner.h:132)
   [0] Godot.PackedScene.Instantiate_Patch1
   [1] KleeMod.Teyvat.Events.Mirrors.PunchOffMirror+<PunchEachOther>d__12.MoveNext()
```

That launch's `godot.log` carries **374,858 `Parameter "particles" is null`** and 21,317
each of `Element limit reached` / `Parameter "mem" is null`; the process went to
`Responding = False` and the bridge timed out. `PunchEachOther` spawns
`NHitSparkVfx.Create(...)` into `CombatVfxContainer` once per swing, throttled only by
`Cmd.Wait(1.2f)` — and under FastMode=Instant / TimeScale=3.0 those waits collapse, so the
container fills every frame until the RID pool is gone. **Caveat, stated rather than
buried:** I did not reproduce this at default speed, so this record does not claim a human
at 1× hangs. It claims the event is unreachable and unsoakable at the harness's own
standard speed, and that nothing bounds the spark spawn.

Two incidental Liyue dressings opened perfectly on the way (run 2): *The Tide-Warmed Pools
of Yaoguang Shoal* and *The Tales of Guyun Were True* — dressed titles, two dressed options
each, both completing. The pipeline works; the two failures are specific breaks.

### 2. The rest site — PASS

Reached four times (runs 3 ×2, 4, 5), in both dressings.
`frame-20260915-171358-teyvat-rest-site.png` shows the dressed placeholder scene drawn —
flat field, the kneeling Ironclad, "What shall I do?", both buttons — and **no error
scene**. `klee-mod/pck-src/scenes/rest_site/liyue_rest_site.tscn:25-26` is the
`RestSiteLighting` node with `unique_name_in_owner = true`; the room loaded with `[INFO]
Preloading 'RestSite Room' Complete: assets=5 time_elapsed=116ms` and **zero ERROR lines in
the whole launch** — an unresolved `%RestSiteLighting` would have thrown there. **Smith**
works (`choose_rest_option index 1` opened the upgrade card-select on the deck); **Rest**
works (`index 0`, HP **21 → 46**, the printed "Heal for 30% of your Max HP (25)" paid
exactly).

### 3. The combat background — PASS

`frame-20260915-175305-teyvat-combat-bg.png` (run 8, Mondstadt) shows the placeholder
layers drawn as a flat green field, with the hero, the enemy (the brown GUARD
placeholder), the hand, the intent, energy 3/3 and End Turn — a live, playable combat. The
log carries `[BaseLib] Auto-converted
'res://scenes/backgrounds/mondstadt/mondstadt_background.tscn' from Control to
NCombatBackground` and **no `SetUpCombat` exception, no `AssetLoadException`, no
`.tscn.remap` line anywhere**. Runs 2, 3, 4, 5, 6 and 8 fought roughly twenty-five combats
including elites and an act-1 boss with **zero ERROR lines in their launch logs**.

**A bonus, closing a proofs-3 unknown:** `frame-20260915-175302-teyvat-map-header.png`
shows the map header reading **"Act 1 / Mondstadt"** on screen, with the map plates behind
it. proofs-3 could only say the loc row resolved.

## PHASE SEVEN — STOPPED, no debug op exists

`understudy/bridge.py:578` `DEBUG_OPS` is `set_resource, set_energy, set_hp, set_block,
set_power, clear_hand, hover, unhover, force_next_event`, and the live route's own reply
lists exactly those nine (`GET /api/v1/gits/debug_state`; `GitsDebugState.cs:431` is the
same allow-list). `McpMod.Actions.cs` offers no act or floor verb — its menu-level actions
are `continue / abandon_run / quit`, all main-menu only. Grepping `vendor/STS2_MCP` for
`act_skip|skip_act|set_floor|goto|teleport|jump_to|debug_act|unlock_act` returns nothing.
**There is no act-skip or floor-jump op, so acts 2 and 3 were not entered and the four
dressings (Natlan, Inazuma, Fontaine, Sumeru) are untested in the running game.** The one
fact this record adds is that all four register their background factory at boot, on the
lines quoted above.

## What this earns

- **EB-767 — confirmed, and the workaround is proved.** Every proof above was reached by
  forcing the **base** id. The row also earns a clause it does not have: **a base id is
  refused two further ways** — `No event 'PUNCH_OFF' pending in act 'MONDSTADT'` (the
  dressing exists for one nation only) and `'TEA_MASTER' is not allowed in this run right
  now (EventModel.IsAllowed is false)`, which is the event's own gate rather than the run's
  state machine (TEA_MASTER wants 150 gold, PUNCH_OFF `TotalFloor >= 6`). A useful `--list`
  says which ids are pending in *this* act and which are gated right now.
- **EB-768 — stays retired, reconfirmed in play.** Roughly twenty-five combats across six
  runs and both dressings, no `.tscn.remap` line, no `AssetLoadException`, no `SetUpCombat`
  throw, and a drawn background in the frame. proofs-3's blocking DEFECT 1 is gone.
- **EB-766 — worse than the row records.** 13 launch attempts, **5** blew the 442-443 s
  menu-ready wait (16:29, 17:03, 17:14, 17:27, 17:38) and were killed and relaunched. That
  is 38%, not the 20% the fairness read saw. The store grew 1308 → 1315 across this record;
  nothing here touched it.

**New defects, described and not minted:**

1. **`SixContractsToABetterYou` softlocks the run** (two more dressings are keyed the same
   way). Blank page, zero options, no exit. Cause and fix named above; it wants a row only
   if `teyvat-slug-fix` does not close it.
2. **`PunchOffMirror.PunchEachOther` exhausts Godot's RID pool and hangs the process.** The
   hit-spark spawn is bounded only by `Cmd.Wait`, which the harness's speed setting
   collapses. Blocking for any soak that can reach floor 6 in Liyue. Wants a bound on the
   spawn (or a freed spark), and a re-check at default speed.
3. **`RopeBridgeBelowDunyuRuins` option 0 prints `" is removed from your deck."`** with no
   card name — the dressed row's card var does not substitute, though the option's keyword
   tip resolves the same card. Cosmetic, non-blocking.
