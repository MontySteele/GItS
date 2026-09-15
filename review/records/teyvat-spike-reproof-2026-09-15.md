Status: RECORD (spike re-proof after EB-759/760/761; feasibility only, nothing measured)

# The three fixes against the real game

Follows `review/records/teyvat-spike-proofs-2026-09-15.md`. **Nothing here is measured or
quotable** — no pre-registration, no blind grading, no slate. Loadout unchanged and
untouched: BaseLib, `klee`, `STS2_MCP` on, the two content mods off.

**Installed.** `deploy_bridge.ps1` (the bridge mod moved: `STS2_MCP.dll` 301,056 bytes),
then `deploy_round.py --arms klee,companion,kokomi,furina-stage,teyvat`. Read back:
**`0.2.3258+proto.dirty`**, bridge present, 406 staged card png(s). **The arm is ON in
the installed build** — the next calibration deploy must turn it off.

**Soak (R225).** `--runs 1 --character KLEEMOD-KLEE --max-fights 3` →
**`bounded seed=55KV5Z1VM4Z9 actions=64 fights=3 defects=0`**, first try.

**Boot greps, scoped by build.** Every `loc merge failed` line in the log directory
belongs to `Version=0.2.3248.0`; on `0.2.3258.0` there is none. On this build:

- `[INFO] [klee] teyvat: loc merged (1 dressed enemy name(s), 0 dressed intent word(s)).`
- `[INFO] [BaseLib] Registered scene 'res://teyvat/creature_visuals/hilichurl_guard.tscn'
  for auto-conversion to NCreatureVisuals`
- `[INFO] [BaseLib] Auto-converted '…hilichurl_guard.tscn' from Node2D to NCreatureVisuals`
- no NRE from `TeyvatLoc`; **one** music ERROR per run
  (`res://teyvat/music/mondstadt`) — EB-758, counted and not chased.

## Item 3 — Nibbit dressed and drawn: PROVEN

Two complete Mondstadt Nibbit fights: the soak's (won, `ENCOUNTER.NIBBITS_WEAK`) and one
driven by hand (lost). In both, `Auto-converted` fires at combat-room creation and:

- **Bridge state:** `{"entity_id": "NIBBIT_0", "name": "Wooden Shield Hilichurl Guard",
  "hp": 45, "max_hp": 45, "intents": [{"type": "Attack", "label": "12",
  "title": "Aggressive"}]}`. Every log line targets `Wooden Shield Hilichurl Guard`.
- **Zero** `InvalidCastException`, **zero** "Falling back to error scene", **zero**
  raw-key warnings for `NIBBIT.name@MONDSTADT` or `MONDSTADT.title`.
- **The two ungated Spine doors do not fire.** `GetCurrentAnimationLength` and
  `GetCurrentAnimationTimeRemaining` appear nowhere across both fights, including the
  player-death sequence. That is the answer EB-760 asked the record to give.
- **Frame:** `understudy/logs/frames/frame-20260915-004421-teyvat-guard-still.png`
  (gitignored, not committed). The placeholder draws in the enemy slot; the intent
  marker (sword, "12") sits centred above the body, the name plate below it, and the HP
  bar at the body's foot, overlapping the rectangle's lower edge by a few pixels; nothing
  is placed so as to hide a number. **MATERIAL, not evidence** (Guardrail-7).

## Item 2 — the Springvale Cheese Cellar: the route works, the event does not

**The op does its job.** `force_next_event` was called on a map in two Mondstadt runs
(Ironclad `HJ89E2MKQTKN`-line and Klee), logged as
`[STS2 MCP][GItS] debug_state: force_next_event MONDSTADT ROOM_FULL_OF_CHEESE index 5 ->
slot 1 | why: EB-761 item-2 re-proof`, and the next `?` room opened on it both times.
**The substitution is real and the loc row renders:** the bridge reports
`{"event_id": "SPRINGVALE_CHEESE_CELLAR", "event_name": "The Springvale Cheese Cellar"}`
where the base game would have had Room Full of Cheese.

**And the event cannot be played.** Its page comes up with `body: null` and
`options: []`, because two separate things throw while it is built — both times, under
**both** characters, so this is not a control-character artifact:

1. `System.NullReferenceException at CharacterModel.AddDetailsTo(LocString)` ←
   `EventOption.AddLocVars(EventModel)` ← `EventOption..ctor` ←
   `KleeMod.Teyvat.Events.SpringvaleCheeseCellar.GenerateInitialOptions()`. No option is
   ever constructed.
2. `AssetLoadException: Asset previously failed to load:
   res://images/events/springvale_cheese_cellar.png` ←
   `EventModel.CreateInitialPortrait()` ← `NEventLayout.InitializeVisuals()`. The event
   has no portrait in the pack and `EventModel` derives that path from the id.

So **neither option was taken and The Chosen Cheese was never granted**; the relics after
the visit were the run's own (`Burning Blood, Precise Scissors`; `Pounding Surprise,
Golden Pearl`). Both throws are new findings and want their own rows.

**The refusals are correct**, checked live. Unknown id: `No event 'NOT_A_REAL_EVENT'
pending in act 'MONDSTADT' (31 events). Pending: …`. Already visited:
`'ROOM_FULL_OF_CHEESE' has already been visited in this run. RoomSet.EnsureNextEventIsValid
skips a visited event BEFORE the read, so forcing it would write the list, answer ok, and
open the next '?' room on something else. Force it in a fresh run.` One wrinkle:
`understudy/force_event.py`'s CLI prints both as `FAILED: the bridge refused the force:
None` — it reads `message` where the bridge returns `error`, so the reason is lost to a
caller who does not go to the wire themselves.

## Item 1 — nothing new asked, nothing new broken

Acts seen this session: **MONDSTADT** and **LIYUE**, both by name, none by the base
zones'. **Zero** `BackgroundAssets` throws in any combat entered, as expected.

## What the evidence closes

- **EB-759 — closes.** Acceptance is "Nibbit reads Wooden Shield Hilichurl Guard in a
  Mondstadt run; no NRE from TeyvatLoc in godot.log". Both met verbatim, above.
- **EB-760 — closes.** Acceptance is "The Guard placeholder draws in a Mondstadt Nibbit
  fight and the record says whether the two doors fire". The placeholder draws; the two
  doors do not fire.
- **EB-761 — does NOT close.** Acceptance is "A scenario reaches Room Full of Cheese on
  demand in a Mondstadt run and observes the substituted text, both options and The
  Chosen Cheese". Reaching it on demand and the substituted *title* are proven; **both
  options and the relic are not**, blocked by the two throws above. The op itself is
  sound — what is left is the event, not the route.

No row is retired here.
