Status: RECORD (deploy proofs phase eight; feasibility only, nothing measured)

# The slug fix holds, the Punch-Off is a speed bug, and the boot fuse did not fire

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
Nothing was deployed, rebuilt or committed to the main checkout; the profile and the
run-history store were not touched.

**Installed, off `mods\klee\manifest.json`:** `0.2.3333+proto.dirty`, banner `[v0.111.0]
(2026.08.14) MODDED (3)` in every frame, arm ON. Boot line every launch: `[INFO] [klee]
teyvat: loc merged (1 dressed enemy name(s), 0 dressed intent word(s), **1387**
converted-event row(s))` — up from proofs-4's 477, which is #518 and #520 arriving.

**Eight launches, all Ironclad, `understudy.embark` plus a scratch driver that reuses
`soak_driver.RunDriver`'s own screen loop.** "Boot wall" is the whole `embark` command, so
it is an upper bound on boot-to-menu.

| # | boot wall | act | seed | what it was for |
|---|---|---|---|---|
| 1 | 27 s | MONDSTADT | `7G0W51TPMT2H` | item 1, Mondstadt dressing; died act 1 |
| 2 | 21 s | LIYUE | `X88M6EUKPWEY` | item 1, **Six Contracts**; died act 1 |
| 3 | 21 s | LIYUE | `E8BUP3RVQVLT` | item 2 attempt; died act 1 floor 5 |
| 4 | 22 s | LIYUE | `SUHD1LK63W33` | item 2 attempt; died to the row-11 elite |
| 5 | 21 s | MONDSTADT | `PMTX7Z4ELVH3` | item 4 attempt; died act 1 floor 6 |
| 6 | **447 s** | — | — | **STALLED; the fuse never fired** |
| 7 | 21 s | LIYUE | `KBG5J3D99K69` | item 2 — the Punch-Off, both ways |
| 8 | 23 s | MONDSTADT → **NATLAN** | `VZ9E7RXYJVQC` | item 4; reached act 2, died floor 25 |

**PASS / FAIL:** item 1 **PASS**; item 2 **PASS** at default speed and the harness-speed
hang **reproduced**; item 3 **FAIL** — the fuse caught 0 of the 1 stall it met; item 4
**PARTIAL**.

## 1. SELF_HELP_BOOK — PASS, in both dressings

**Liyue, launch 2, seed `X88M6EUKPWEY`, floor 3.** `force_next_event LIYUE SELF_HELP_BOOK:
index 27 -> slot 1`. The page opened as `SIX_CONTRACTS_TO_A_BETTER_YOU`, `event_name`
**"Six Contracts to a Better You"** — *the dressed string, not the raw loc key
`events.SIX_CONTRACTS_TO_A_BETTER_YOU.title` proofs-4 got*.
`frame-20260915-181425-teyvat5-six-contracts.png` shows the dressed title, the full dressed
body ("A Feiyun pamphleteer has set up a folding stall on the Harbor steps…"), the base
event's book portrait (the acceptable fallback), and **three** dressed options with titles,
descriptions and keyword tips: *Read the Back* / "Choose an Attack to Enchant with Sharp 2.",
*Read a Random Passage* / "…Nimble 2.", *Read the Entire Book* / "…Swift 2." (greyed, no
Power in deck). **`Read the Back` completed** to card-select. That launch's `godot.log` has
**no** `No loader found … six_contracts…png`, **no** `NullReferenceException at
SelfHelpBookMirror.GenerateInitialOptions`, **no** `AssetLoadException` — two ERROR-class
lines in the whole log, both base-game noise. **#521 re-proved.**

**Mondstadt, launch 1, seed `7G0W51TPMT2H`, floor 3.** The same base id opened as
`GUILD_DESKS_RETURNED_COPY`, *The Guild Desk's Returned Copy*
(`frame-20260915-181018-teyvat5-guild-desk.png`) — dressed title, dressed Katheryne body,
portrait, the same three dressed options; *Read the Back* completed. Both faces proved. (Not
a defect, but worth knowing: the wire returns `options: []` for a second after a page opens,
then fills. Ask twice.)

## 2. PUNCH_OFF — PASS at default speed, and the harness-speed hang REPRODUCED

Launch 7, Liyue, seed `KBG5J3D99K69`. `POST /api/v1/gits/speed {"enabled": false}` was made
before the run left floor 3, so the whole approach and the event ran at the game's own
settings — the endpoint answered `fast_mode: "Fast", time_scale: 1,
original_fast_mode_source: "process"`, [USER]'s own values, not Instant/3.0. **At default
speed it works.** `force_next_event LIYUE PUNCH_OFF: index 5 -> slot 5` at
floor 9, then `[INFO] Creating NCombatRoom with mode=VisualOnly
encounter=PUNCH_OFF_EVENT_ENCOUNTER.` The page is `GUYUN_STONE_CONSTRUCTS`, *The Guyun Stone
Constructs* (`frame-20260915-184006-teyvat5-punchoff-default.png`): the two Geo constructs
animating mid-punch, the dressed body ("Two Geo constructs stand half-buried in the Guyun
Stone Forest… Millelith posted this as a hazard, not a commission"), and both dressed
options — *Nab* / "Add Injury (curse) to Deck. Obtain a random Relic." and *I Can Take Them*
/ "Enter combat against 2 Punch Constructs for greater rewards…". Over roughly **90 s on
that page**: **0** `Element limit reached`, **0** `Parameter "particles" is null`,
`(Get-Process SlayTheSpire2).Responding` **True**, and **`Nab` completed** to rewards.

**Then the harness speed was POSTed, and the process died the way proofs-4 said.** Same room,
same run: with the event already answered and the run on that room's rewards screen,
`set_speed(True, 3.0)` → `fast_mode: Instant, time_scale: 3`. Within about two minutes,
`Responding = False`, the state endpoint timing out, **34,501** `ERROR: Element limit
reached. at: _allocate_rid (./core/templates/rid_owner.h:132)` and **613,190** `ERROR:
Parameter "particles" is null`, every one under

```
[1] NHitSparkVfx NHitSparkVfx.Create(Creature, bool)
[2] void KleeMod.Teyvat.Events.Mirrors.PunchOffMirror+<PunchEachOther>d__12.MoveNext()
```

Killed by hand. **One variable changed, so this is a tighter reading than proofs-4 could
give.** The bug is not "the Punch-Off is broken"; it is that `PunchEachOther` spawns one
hit-spark per swing bounded only by `Cmd.Wait(1.2f)`, and the harness's TimeScale collapses
that wait — and it keeps punching after the option is answered, so it burns on the rewards
screen too. A human at the game's own speed is not hitting this; every soak that reaches a
Liyue `?` past floor 6 is.

## 3. The boot-stall fuse — 7 of 8 clean, and the one stall walked straight past it

Seven launches reached the menu in **21–27 s**. The eighth (launch 6) printed
`WARN lane lane0: menu never became ready within 444s; last read: bridge connection failed
at http://localhost:15526/api/v1/singleplayer: TimeoutError: timed out`.

**No `boot looks STALLED` line was printed, and no relaunch happened** — the whole 444 s of
the first attempt was spent, then `SystemExit`, so `BOOT_STALL_RETRIES` was never reached.
And it was the exact shape the row describes: I left the process up and checked by hand —
`GET /` answered `{"message": "Hello from STS2 MCP v0.4.0", "status": "ok"}`, `grep -c
"Profile-scoped data path initialized"` on that log was **0**, and the log had stopped at
21,753 bytes on a run of `Wrote N bytes to … in steam remote store` lines. That is
`health_ok` true and the marker absent, which is `boot_stall_verdict` returning True — yet
the fuse never fired inside the watch. **FAIL for this launch;** mechanism unsettled (defect
1 below).

**What #517's other halves did do.** Every teardown archived its log — eight files under
`understudy/logs/godot/20260915-*-<pid>.log`, including the stalled boot's 21 KB one, which
is the evidence the fairness read had none of. The 10 s dead gap is inside every timing
above. Across this record the store grew 1316 → 1322 files; nothing here deleted from it.

## 4. Acts 2 and 3 — PARTIAL: act 2 is NATLAN and it plays; no map plate, no forced event

Launch 8, Mondstadt, seed `VZ9E7RXYJVQC`. There is no act-skip op (proofs-4 §PHASE SEVEN),
and the bot died in act 1 on four of the first five runs of this record, so the run was kept
alive with in-combat `set_hp` — **a dev route, disclosed: this run is not one the game's own
play produced, and no number off it means anything.** With that, it cleared the act-1 boss.

- **The act is NATLAN**, the first of R273's second pair: `Preloading 'Act=NATLAN'` twice in
  that log, against four `Act=MONDSTADT` before it. And `[INFO] [BaseLib] Auto-converted
  'res://scenes/backgrounds/natlan/natlan_background.tscn' from Control to
  NCombatBackground` — the act-2 factory fires in play, not just at registration.
- **The combat draws and is playable.** `frame-20260915-190647-teyvat5-natlan-combat.png`,
  **floor 19**: the flat ochre Natlan placeholder field, the hero, a live enemy at 64/87,
  the hand, energy 0/3, End Turn. `frame-20260915-191302-teyvat5-natlan-map.png` is **floor
  25**, the fight the run died in. **Zero `ERROR` lines in that whole launch's log**, and
  zero `AssetLoadException` / `.tscn.remap` / `SetUpCombat` matches, across both acts.

**Not obtained, and the 40-minute cap is why:** the run died on floor 25 before a map screen
could be captured, so there is **no act-2 map plate frame, no on-screen act title, and no
forced `WELCOME_TO_WONGOS` / `DOLL_ROOM` / `COLORFUL_PHILOSOPHERS`**. Act 3 was never
approached. The bot's act-1 death rate (4 of 5 unaided runs here) is what makes this item
expensive; the next pass should budget the dev-route heal from the start.

## What this earns

- **EB-767 — re-proved, and the cost is now numbered.** Every page above was reached by
  forcing the **base** id. The row should also carry what a `--list` would save: a `?` node
  is not an event node. Three times here, forcing a base id and walking to the first `?`
  landed on **treasure**, **shop** and **monster** instead — wasted floors on a run the bot
  may not survive.
- **EB-766 — half met, acceptance not met.** 7 of 8 boots inside 27 s is the behaviour the
  row wants, and the archiving works. But the acceptance is "30 consecutive launches with
  none over 90 s", and launch 6 was 447 s **with the fuse armed**. The next action changes:
  not "detect a stall early" — that code is written — but "find out why the detector was
  silent on a stall that matches its own verdict function".
- **proofs-4 defect 2 (the Punch-Off spark) — confirmed and narrowed to speed.** Not a
  defect of the dressed event: it renders, animates and completes at the game's own settings
  with zero RID errors. It is an unbounded VFX spawn only the harness's TimeScale reaches.
  A sharper acceptance is now writable: *bound the spawn (or free the spark), then run the
  same event at Instant/3.0 and see 0 `Element limit reached`*. (Neither this row nor
  proofs-4 defect 3 is in `docs/current/BACKLOG.md` on `origin/main` as of this record, so
  both are named here by their proofs-4 numbers.)
- **proofs-4 defect 3 (the Dunyu rope bridge's missing card name) — not re-tested.** No run
  reached `SLIPPERY_BRIDGE`.
- **EB-768 stays retired, now through act 2** — roughly thirty combats across eight runs and
  three dressings (Mondstadt, Liyue, Natlan) with no `.tscn.remap`, no `AssetLoadException`
  and no `SetUpCombat` throw anywhere.

**New defects, described and not minted:**

1. **The EB-766 fuse did not fire on a textbook stall.** Launch 6 spent the full 444 s with
   `fuse=BOOT_STALL_AFTER_S` armed and printed no WARN. Two candidates, neither proved here:
   (a) `boot_stall_verdict` returns False whenever `ever_state` is true, and `ever_state`
   latches for the life of the watch, so one early answer from `/api/v1/singleplayer`
   disables the fuse permanently; (b) `_health_ok()` read False during the watch although
   `GET /` answered fine a minute later. Either way the cheap fix is to print the three
   signals once at the fuse deadline, so the next stall says which guard refused.
2. **The Punch-Off spin writes a 2.5 GB `godot.log` in about two minutes** — 2,561,687,155
   bytes, 613,190 repeated `particles is null` lines. A disk hazard on its own, and EB-766's
   teardown archiver dutifully **copies** it; an unattended batch hitting this twice writes
   5 GB of log and 5 GB of archive. Worth a size cap on `archive_log`.
3. **A teardown after a hand-killed process cannot revert the speed row** — launch 7's ledger
   shows entry 4 `NOT REVERTED … [WinError 10061]`. Harmless here: the endpoint persists its
   own capture (EB-87), launch 8 read back `original_fast_mode: "Fast"` ([USER]'s value) and
   the final teardown restored it. But the ledger says NOT REVERTED and a reader cannot tell.

No row is retired here, and no C# was changed.
