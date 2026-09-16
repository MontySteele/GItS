Status: RECORD (deploy proofs phase nine; feasibility only, nothing measured)

# The boot fuse fires, the Punch-Off is half fixed, and the DONE page reads

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
Nothing was deployed, rebuilt or committed to the main checkout; the game profile, the Steam
userdata and the run-history store were not touched, and `settings.save` was not edited.
**Five other agents were building and running the C# and pytest suites in sibling worktrees
on this machine throughout**, so every boot wall and every stall below was measured under
concurrent build load; where a stall coincides with visible build work that is said rather
than counted as clean evidence either way.

**Installed, off `mods\klee\manifest.json`:** `0.2.3352+proto.dirty`, `min_game_version`
`0.111.0`, BaseLib `3.4.7`. Banner `[v0.111.0] (2026.08.14) MODDED (3)` in every frame, arm
ON. The installed `klee.dll` is byte-identical to `klee-mod/dist/klee/klee.dll`
(md5 `57189e50a77da0c9d10d204c62fd51b5`), so #528's Punch-Off work is in the build under test.

**45 launches, all Ironclad.** Three were `understudy.soak`; 36 were embarks from a scratch
driver that reuses `soak_driver.RunDriver`'s own screen loop (kept out of the tree — it is
scratch, and it is not clean enough to commit); six were the boot fuse's own relaunches.
"Boot wall" is the whole `Session.setup`, so it is an upper bound on boot-to-menu.

| # | lane | boot wall | face | seed | what it was for |
|---|---|---|---|---|---|
| 1 | lane0 | 17.3 s | — | — | item 1: **no embark path** |
| 2 | lane0 | 16.7 s | — | — | item 1: the same, reproduced |
| 3 | lane1 | 85.0 s to run end | — | `PC80B6AJEZXP` | item 1: **`bounded`, 3 fights, 0 defects** |
| 12 | lane1 | 25.5 s | MONDSTADT | `Z95RHVMQXA4J` | item 4: Confiscation page opens dressed |
| 16 | lane1 | 18.6 s | LIYUE | `X8RL75G8YKLG` | item 4: Bureau page opens dressed |
| 24 | lane1 | 22.3 s | LIYUE | `Q5K31FFWRLHB` | item 3a: **66 MB log, bridge timed out** |
| 25 | lane1 | 26.7 s | LIYUE | `Y4JVUBG99SJS` | item 3a: **process gone inside 20 s** |
| 27 | lane1 | 24.6 s | LIYUE | `B26Z8R0ZURKD` | item 3a: **512 MB log, bridge timed out** |
| 31 | lane1 | 79.7 s | MONDSTADT | `RG26KZ19VN38` | item 4: **DONE page, dressed** |
| 36 | lane1 | 81.5 s | LIYUE | `FUZRJT9P65EP` | item 3b: **sparks, 0 errors, floor 9** |
| 45 | lane1 | 15.9 s | MONDSTADT | `TYSRRE1UPP1N` | item 5: Guild Desk opens dressed |

The other 28 embarks were approach runs: a face that does not carry the event, a floor below
its gate, a `?` that turned out to be a monster, or the bot dying. Their boot walls are in
the distribution below.

**PASS / FAIL:** item 1 **PASS on lane 1, FAIL on lane 0** (a profile blocker, not a build
defect); item 2 **PASS**, 6 stalls met and 6 caught; item 3 **(a) FAIL, (b) PASS**; item 4
**PASS**; item 5 **PASS**.

## 1. R225 soak — the lane-0 profile will not let a run start

`python -m understudy.soak --runs 1 --max-fights 3`, twice, both identical, verbatim:

```
    defect  seed=None  actions=0  fights=0  defects=1
```

and in `soak-20260916-010650-index.json` the detail is
`no_embark_path: menu_screen 'main' offers none of the embark options; saw ['settings', 'quit']`,
with `blocked_options` carrying
`{"name": "timeline", "enabled": false, "reason": "manual_epoch_reveal_required", "pending_epoch_ids": ["IRONCLAD2_EPOCH"]}`.
Continue, singleplayer, multiplayer and compendium were not merely disabled — they were not
enabled-and-visible at all, which is what `McpMod.StateBuilder.cs:340` counts. **The profile
is sitting on an unrevealed epoch and the main menu is parked behind it.** Nothing here
touched it; the fix is a person clicking the reveal once, and until then lane 0 cannot embark.

The same command on lane 1's disposable profile, verbatim:

```
    bounded  seed=PC80B6AJEZXP  actions=85  fights=3  defects=0
```

So **the install is sane and R225 passes on this build**; the whole rest of this record runs
on lane 1 for that reason, which is also why no run here is a run of record.

## 2. EB-766 — the fuse caught 6 of 6, and the archive cap earned its keep

**45 launches, 6 stalls, 6 caught, 6 recovered.** Each stall printed the same line the row
asks for and then relaunched:

```
WARN lane lane1: boot looks STALLED after 48s -- the root endpoint answers, the state
endpoint has been silent for 44s, godot.log is 184328 bytes and the profile marker is
ABSENT (last 48s without growth). Killing and relaunching (EB-766).
lane lane1: waited 9.4s after the previous kill before launching
```

All six stalled boots are archived (`understudy/logs/godot/20260916-*-stall1.log`, 22,125 to
22,973 bytes each), and all six are the textbook shape: `Profile-scoped data path initialized`
count **0**, the log frozen part-way through the run-history writeback. Every one of the six
relaunches reached the menu — those sessions' total boot walls were 73.8, 79.7, 81.5, 82.2,
82.4 and 84.7 s, which is the 48 s fuse plus a ~9 s dead gap plus a clean ~25 s boot. **No
`DIAG` line was printed all round**, so the fuse never once declined a boot it was watching.
This is the acceptance proofs-5 could not meet, met.

The 36 timed embarks: median **24.5 s**, 30 of 36 at or under 33 s, one 43.0 s, and the six
fuse-recovered ones above. Nothing over 90 s except a fuse recovery.

**The bounded archive fired twice and it is the difference between a night and a disk.**
Launch 24 wrote a 66,379,144-byte `godot.log` and launch 27 a 511,869,703-byte one; both
archived as `WARN: godot.log was N bytes; archived TRUNCATED to the first 1000000 and the
last 4000000 bytes`. proofs-5 defect 2 is closed by observation.

## 3. EB-769 — the spark cap works and the Punch-Off still dies at harness speed

**(b) At the game's own speed: PASS.** Launch 36, Liyue, seed `FUZRJT9P65EP`, **floor 9**.
`POST /api/v1/gits/speed {"enabled": false}` answered `fast_mode: "Fast", time_scale: 1,
original_fast_mode_source: "process"` — the owner's own values. The page is
`GUYUN_STONE_CONSTRUCTS`, *The Guyun Stone Constructs*, with the dressed body and both dressed
options (*Nab* / "Add Injury (curse) to Deck. Obtain a random Relic." and *I Can Take Them*).
`frame-20260916-020753-p6-punch-slow-sparks-20s.png` and `…-sparks-40s.png` **show the hit
spark drawn on the right-hand construct mid-swing**, which is what the 24-per-visit cap is
there to preserve. Over **120 s on that page**: `Responding` **True** at every 20 s sample,
`godot.log` **did not grow one byte** (204,565 throughout), and **0** `Element limit reached`,
**0** `Parameter "particles" is null`, **0** `NHitSparkVfx` lines.

*Not obtained:* the combat itself. The page narrows to a single confirming *I Can Take Them*
click after the first answer, the driver did not make it, and the one follow-up launch spent
six consecutive `?` nodes on monster rooms (EB-767 again) and never reached the page. So
"finish that combat" is **unproven at the game's own speed**, and it is a driver shortfall,
not a game reading.

**(a) At Instant / 3x: FAIL, three times.** Launches 24, 25 and 27, all Liyue, all floor 6 or
later. Every one entered the room and none survived it:

- **24** (`Q5K31FFWRLHB`): `godot.log` reached **66,379,144 bytes**, the bridge stopped
  answering, the process had to be torn down.
- **25** (`Y4JVUBG99SJS`): the log **stops dead** on
  `[INFO] Creating NCombatRoom with mode=VisualOnly encounter=PUNCH_OFF_EVENT_ENCOUNTER.`
  with no error at all; `Responding` was `(gone)` at the first 20 s sample and the bridge
  answered `WinError 10061`.
- **27** (`B26Z8R0ZURKD`): **511,869,703 bytes** in about two minutes.

**The fix landed and it is not the whole spawn.** In launch 24's archived log the errors
are `Element limit reached at _allocate_rid` and `Parameter "particles" is null`, exactly as
in proofs-5 — but the top frame has **changed**:

```
[0] Godot.Node <unknown>.Godot.PackedScene.Instantiate_Patch1(...)
[1] void KleeMod.Teyvat.Events.Mirrors.PunchOffMirror+<PunchEachOther>d__17.MoveNext()
[4] System.Threading.Tasks.Task KleeMod.Teyvat.Events.Mirrors.PunchOffMirror.PunchEachOther()
```

`NHitSparkVfx` appears **nowhere** in any of the three logs, where proofs-5 had it under every
one. So `ShouldSpawnHitSpark` is doing its job — and the loop's **other** per-swing spawn,
`VfxCmd.PlayOnCreatureCenter(..., "vfx/vfx_attack_blunt")` at `PunchOffMirror.cs:217`, is
unbounded for the same reason the spark was, and is now the whole flood. The file says so
itself: *"the same anims, the same `vfx_attack_blunt`, the same waits"* — nothing moved
there, deliberately, and that is the half that is still open. **EB-769's acceptance is not
met on this build**, and the next action is the same shape as the last one, applied to the
blunt VFX rather than to the spark.

(Also learned, cheaply: `PunchOffMirror.IsAllowed` is `TotalFloor >= 6`, so a force on an
early floor comes back *"not allowed in this run right now"* and is not a defect. And
`PUNCH_OFF` is dressed on **Liyue only** — `TeyvatEventsGenerated.cs:5493` — so roughly three
runs in four cannot serve it at all.)

## 4. THE_FUTURE_OF_POTIONS — the DONE page reads, in the Mondstadt register

**PASS.** Launch 31, Mondstadt, seed `RG26KZ19VN38`, at the game's own speed. The page opened
as `CONFISCATION_WITH_COMPENSATION`, *Confiscation, With Compensation*, with the dressed body
and two dressed, potion-specific options (*Surrender the Contraband Flask* / "Lose Snecko Oil.
Obtain an Upgraded Rare Power card reward."). No potion had to be granted — the driver simply
waits until the run's own play has two in the belt, which is also what the base event's
`IsAllowed` wants; a run holding one is refused. After the option, the card reward is claimed
and **then** the DONE page is served:
`options: [{"title": "Proceed", "is_proceed": true}]`.
`frame-20260916-014018-p6-potions-slow-done1.png` shows it, word for word:

> The quartermaster signs the confiscation slip and slides the technique across the trestle.
> "Regulations satisfied. Courtesy too."

which is `overgrowth-mondstadt-2026-09-14.md` `@pages.DONE.description` exactly.

**The Liyue face's page is proved; its DONE page is not.** Launches 16 and 17 opened
`BUREAU_OF_RECLAIMED_MEDICINE`, *The Bureau of Reclaimed Medicine*, with its dressed body and
*Insert Common/Uncommon Potion* options (`frame-20260916-012801-p6-potions-slow-page.png`),
but both were spent learning that the DONE page only appears **after the card reward is
taken** — `skip_card_reward` loops back to the reward screen and `proceed` does nothing there;
`select_card_reward card_index=0` is the click that releases it. That is worth writing down,
because it cost three launches. No launch reached a Liyue DONE page afterwards.

**The four new lines of #530 are on act-2 and act-3 faces** (Inazuma, Natlan, Fontaine,
Sumeru) and there is still no act-skip op, so none of them was reachable this round. What is
proved is that the DONE page exists on the wire, is served at the right moment, and prints
its face's own register.

## 5. SELF_HELP_BOOK — the slug fix still holds

**PASS**, one sentence as asked: launch 45, Mondstadt, seed `TYSRRE1UPP1N`, the base id opened
as `GUILD_DESKS_RETURNED_COPY`, *The Guild Desk's Returned Copy*, with two dressed options
carrying their keyword tips, *Read the Back* completed to card-select, and that launch's log
has zero `Element limit`, zero `particles is null` and one base-game ERROR line
(`frame-20260916-022440-p6-selfhelp-x-page.png`).

## What this earns

- **EB-766 — acceptance met on this evidence.** 6 stalls, 6 caught, 6 recovered, no silent
  deadline, every stalled log archived, and the size cap proved on a 512 MB log. The row's
  own bar is "30 consecutive launches with none over 90 s", and this round is 45 launches
  with none over 90 s that was not a fuse recovery. Under concurrent build load, which makes
  it a harder read rather than an easier one.
- **EB-769 — half met, and the remaining half is named.** The spark cap works. The blunt VFX
  is the same defect one call down and wants the same guard.
- **EB-767 — the cost is now numbered twice.** One launch this round burned six consecutive
  `?` nodes on monster rooms without ever reaching the forced event.
- **A new, non-build blocker:** the lane-0 profile's unrevealed `IRONCLAD2_EPOCH` stops every
  harness embark on the owner's profile. Nothing in this tree may clear it.
- **proofs-4 defect 3 (the Dunyu rope bridge's missing card name) — not re-tested.** No run
  reached `SLIPPERY_BRIDGE`.

Frames are in `understudy/logs/frames/`, which is gitignored for the reason
`understudy/frames.py` gives; they are cited by name above, as proofs-4 and proofs-5 cited
theirs. No row is retired here, and no C# was changed.
