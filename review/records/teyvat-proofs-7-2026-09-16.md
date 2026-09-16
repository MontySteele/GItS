Status: RECORD (deploy proofs phase ten; feasibility only, nothing measured)

# The act-skip op works, and all four act-2/3 dressings are looked at

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
Nothing was deployed, rebuilt or committed to the main checkout; the owner's game profile,
the Steam userdata and the run-history store were not touched, and `settings.save` was not
edited. **Twice over, nothing here is comparable to anything.** `skip_act` is the one op on
this route that is not rng-neutral and says so: the floors it skips never roll, so every
act-scoped stream is read from a different position afterwards, including this run's own
earlier floors. On top of that, every tour below wrote the board by hand — `set_hp` on the
player to keep an act-1 starter deck alive on an act-3 map, and `set_hp` on the living
enemies to end the fights it had to walk through. Those writes are counted per section. A
run here reaches a FACE — an act's art, its name, its music, its events — and never a
number.

**Other agents were building and running C# and pytest suites in sibling worktrees on this
machine throughout**, so every boot wall below was measured under concurrent build load.

**Installed, off `mods\klee\manifest.json`:** `0.2.3384+proto.dirty`, `min_game_version`
`0.111.0`, BaseLib `3.4.7`. Banner `[v0.111.0] (2026.08.14) MODDED (3)` in every frame,
`TeyvatFrame` arm ON. Every launch was lane 1 (the disposable profile), as proofs-6
established; lane 0 is still parked behind its unrevealed epoch.

**PASS / FAIL, one line each.** Item 1 **PASS**. Item 2 **PASS on all four faces** — (a)
4/4, (b) 4/4, (c) 4/4, (d) 2 or 3 dressed events on each of the four. Item 3 **PARTIAL** —
four pages reached, four not. Item 4 **NOT DONE**. Item 5 **NOT DONE**. Item 6 **NOT DONE
live**. Item 7 below.

## The launch table

**39 embarks, all Ironclad, all lane 1**, from a scratch driver (`drive7.py` / `drive7b.py`
/ `drive7c.py` / `drive7d.py`, kept out of the tree — it is scratch) that reuses
`soak_driver.RunDriver`'s own screen loop, as proofs-6's did. "Boot wall" is the whole
`Session.setup`, so it is an upper bound on boot-to-menu.

| # | boot | act list (act 1 / 2 / 3) | seed | what it was for |
|---|---|---|---|---|
| 1 | 26.4 s | LIYUE / NATLAN / FONTAINE | `8JV1ZFVVRRW7` | item 1: **both skips, 0.7 s and 0.6 s** |
| 2 | 32.1 s | MONDSTADT / INAZUMA / SUMERU | `XUKSKEZJ48UK` | item 1: the other two faces |
| 3–6 | 23.9–37.0 s | 4 × NATLAN / FONTAINE | — | item 1: the roll tally |
| 12 | 33.1 s | MONDSTADT / NATLAN / FONTAINE | `R7H4D4R8LWPP` | item 2: **Natlan combat** |
| 16 | 29.0 s | LIYUE / INAZUMA / SUMERU | `EV04WSD2HDDX` | item 2: **Inazuma, 3 dressed events** |
| 20 | 23.5 s | LIYUE / NATLAN / SUMERU | `V1ZMXA3B5KVT` | item 2: **Natlan, 2 dressed events** |
| 26 | 35.0 s | LIYUE / INAZUMA / FONTAINE | `3GBFZBU87EFE` | item 2/3: **Fontaine, TRIAL + the dummy fight** |
| 30 | 23.5 s | LIYUE / NATLAN / SUMERU | — | item 2/3: **Sumeru, the workbench + the cage** |
| 31–39 | 23.4–35.0 s | — | — | **blocked at the menu** (see item 7) |

The other embarks were approach runs: a seed whose act-2 or act-3 face was the other one, or
the bot dying before the event.

**Boot: median 31.8 s, max 40.1 s, over 39 launches. Zero stalls, zero fuse firings, zero
`DIAG` lines, zero truncated log archives.** `EB-766`'s fuse was never needed this round —
which is a weaker reading than proofs-6's (6 of 6 caught) and not a contradiction of it.

## 1. EB-771 live — PASS, and it is fast

From a fresh embark, standing on the act-1 map, `skip_act` landed the run on the act-2 map
**every time it was asked, in under a second**. Six timed embarks:

| seed | act 1 → 2 | act 2 → 3 | wall to act 2 from setup start | excluding boot |
|---|---|---|---|---|
| `8JV1ZFVVRRW7` | 0.7 s | 0.6 s | 36.2 s | 9.8 s |
| `XUKSKEZJ48UK` | 0.7 s | 0.7 s | 41.5 s | 9.4 s |
| `K0CFRBV7RU0M` | 0.7 s | 1.0 s | 32.9 s | 9.0 s |
| `H63T13AATXYU` | 0.7 s | 0.7 s | 41.3 s | 9.4 s |
| `WUULPHBDNAYR` | 0.7 s | 0.6 s | 44.7 s | 11.3 s |
| `1KBX3BBT34F2` | 0.8 s | 0.7 s | 50.9 s | 13.9 s |

**Acceptance met on both readings.** Boot INCLUDED, act 2 is reached in **32.9 s to 50.9 s**
from the moment `Session.setup` starts — under a minute on every one of the six. Boot
EXCLUDED, it is **9.0 s to 13.9 s**, and nearly all of that is the embark walk (Neow, the
character pick, the first map), not the skip; the skip itself is the 0.6–1.0 s column.

`run.act` moved 1 → 2 and 2 → 3 on the wire on every call, and the op's own report predicted
the number it arrived at. **The vote resolved from a map screen every single time** — the
fallback case PR #534's body describes was not reached once in fourteen skips, and no
`SkipActError` for a transition that never landed was raised.

**The last-act refusal fires by name.** Asked a third time, standing on act 3, both embarks
answered, verbatim:

> This run is already in its last act, and skip_act adds no act-4 path.
> RunManager.EnterNextAct would not advance from here — it opens The Architect's room instead
> — so the op refuses rather than landing the run somewhere it was not asked to go.

**The face tally: 30 embarks whose act list was read.**

| act | face | count |
|---|---|---|
| 1 | Mondstadt | 16 of the 26 act-1 faces recorded |
| 1 | Liyue | 10 of the same 26 |
| 2 | **Natlan** | 18 |
| 2 | **Inazuma** | 12 |
| 3 | **Fontaine** | 16 |
| 3 | **Sumeru** | 14 |

All four act-2/3 faces were seen, and all four act-2 × act-3 combinations appeared
(Natlan/Fontaine, Natlan/Sumeru, Inazuma/Fontaine, Inazuma/Sumeru), so the two rolls are
independent of each other and of act 1. **Both act-2 faces and both act-3 faces were in hand
after the first two embarks** — the op's whole promise.

Frames: `frame-20260916-024426-p7-skip-act2-map.png` (Natlan),
`…-024509-…` (Inazuma), `…-024427-p7-skip-act3-map.png` (Fontaine), `…-024510-…` (Sumeru).

## 2. The four act-2/3 dressings — PASS on all four

**(a) The map header draws on all four.** Each frame shows the band with `Act 2` / `Act 3`
over the face's own name in the face's own palette: Natlan orange, Inazuma purple, Fontaine
pale blue, Sumeru sand. Frames `p7-<face>-map` and the four `p7-skip-act*-map` above.

**(b) A combat background and a full fight on all four.** The log line this build writes is
`Creating NCombatRoom with mode=ActiveCombat encounter=<ID>` — **`SetUpCombat` does not
appear in this build's `godot.log` at all**, so that is the line the counts below are read
off, and the acceptance is met on it rather than on the string the round asked for.

| face | fights created | encounters | act preload | `AssetLoadException` |
|---|---|---|---|---|
| Natlan | 4 | `BOWLBUGS_WEAK`, `THIEVING_HOPPER_WEAK`, `DECIMILLIPEDE_ELITE`, … | `Preloading 'Act=NATLAN' … assets=8 time_elapsed=49ms` | **0** |
| Inazuma | 4 | `TUNNELER_WEAK`, `THIEVING_HOPPER_WEAK`, `CHOMPERS_NORMAL`, `INFESTED_PRISMS_ELITE` | `Preloading 'Act=INAZUMA' … assets=8 time_elapsed=60ms` | **0** |
| Fontaine | 8 | `DEVOTED_SCULPTOR_WEAK`, `TURRET_OPERATOR_WEAK`, `AXEBOTS_NORMAL`, `CONSTRUCT_MENAGERIE_NORMAL`, `KNIGHTS_ELITE`, `SOUL_NEXUS_ELITE`, `GLOBE_HEAD_NORMAL`, `BATTLEWORN_DUMMY_EVENT_V1_ENCOUNTER` | `Preloading 'Act=FONTAINE' … assets=8 time_elapsed=50ms` | **0** |
| Sumeru | 8 | `TURRET_OPERATOR_WEAK`, `DEVOTED_SCULPTOR_WEAK`, `FABRICATOR_NORMAL`, `FROG_KNIGHT_NORMAL`, `SOUL_NEXUS_ELITE`, `AXEBOTS_NORMAL`, `QUEEN_BOSS`, `BATTLEWORN_DUMMY_EVENT_V1_ENCOUNTER` | `Preloading 'Act=SUMERU' … assets=6 time_elapsed=66ms` | **0** |

**Zero `AssetLoadException` in any of the four logs**, and one base-game `ERROR` line per log
(the `Progress parse: ValidationError … IsFatal = False` block that every boot writes).
Frames `p7-<face>-combat`. The Sumeru tour reached and fought `QUEEN_BOSS`, so an act-3 boss
room loads under the dressing too.

**(c) The rest site draws on all four.** Frames `p7-<face>-rest`. Inazuma, Natlan and Sumeru
offer `Rest` / `Smith`; the Fontaine one also offered `Dig` (`Dig for a Relic.`), which is the
base game's shovel relic and not a dressing difference.

**(d) Dressed events by base id, each opened and one option completed.** Every page below was
forced by its BASE id through `force_next_event` and arrived under its DRESSED id, and every
printed title and description matches its face file word for word (checked against
`docs/current/dossiers/content/event-faces/`). No raw loc key appeared on any page.

| face | base id forced | page that opened | face file line checked |
|---|---|---|---|
| Inazuma | `COLORFUL_PHILOSOPHERS` | `WAR_COUNCIL_AT_SANGONOMIYA`, *The War Council at Sangonomiya* | `hive-inazuma` :129 `**Ash-Pink Banner (Pink)** — Obtain 3 Necrobinder cards.` |
| Inazuma | `DOLL_ROOM` | `HITOGATA_STOREHOUSE`, *The Hitogata Storehouse* | `hive-inazuma` :181 `**Draw Blind From the Basket** — Obtain a random effigy charm (random Doll Relic).` |
| Inazuma | `COLOSSAL_FLOWER` | `WISTERIA_WELL_OF_CHINJU_FOREST`, *The Wisteria Well of Chinju Forest* | `hive-inazuma` :137 |
| Natlan | `DOLL_ROOM` | `TOTEM_SHELF`, *The Totem Shelf* | `TeyvatEventsGenerated.cs` :3993 `"The Totem Shelf"`, options *Take One Blind* / *Sort Through Two* / *Read Every Totem on the Shelf* |
| Natlan | `COLOSSAL_FLOWER` | `BLOOM_OF_TEQUEMECAN`, *The Bloom of Tequemecan* | `hive-natlan` :82–83 `**Tap the Nectar** — Gain 35 Gold.` / `**Reach Deeper** — Lose 5 HP. Advance to the next level.` |
| Fontaine | `BATTLEWORN_DUMMY` | `PRESSURE_TRIAL_AT_THE_INSTITUTE`, *Pressure Trial at the Institute* | `glory-fontaine` :42–44 `**First Valve** — Fight a 75 HP dummy. Procure 1 random Potion.` |
| Fontaine | `TRIAL` | `EMPTY_SEAT_IN_THE_GALLERY`, *The Empty Seat in the Gallery* | `glory-fontaine` :247 |
| Sumeru | `TINKER_TIME` | `KSHAHREWAR_WORKBENCH`, *The Kshahrewar Workbench* | `glory-sumeru` :308, :310, :312 |
| Sumeru | `BATTLEWORN_DUMMY` | `KSHAHREWAR_PROVING_CAGE`, *The Kshahrewar Proving Cage* | `glory-sumeru` :40 `**Setting 1** — Fight a 75 HP dummy. Procure 1 random Potion.` |

That is **three dressed events on Inazuma and two on each of Natlan, Fontaine and Sumeru**,
so item 2(d)'s bar is met on all four faces. An option was clicked and completed on every one
of the nine.

### The finding this round paid for: the first `?` after a skip is an ANCIENT event

**A forced event does NOT open in the first `?` room of an act entered by `skip_act`.** It was
seen five times, on three faces, with the force reporting `ok` and the walk reporting
`node 0 (? room) of 1`:

| face | forced | page that actually opened |
|---|---|---|
| Natlan | `DOLL_ROOM` | `PAEL`, *Pael*, `is_ancient: true` |
| Natlan | `COLORFUL_PHILOSOPHERS` | `TEZCATARA`, *Tezcatara*, `is_ancient: true` |
| Inazuma | `COLORFUL_PHILOSOPHERS` | `TEZCATARA`, then on a second run `PAEL` |
| Fontaine | `TINKER_TIME` | `DARV` and, on the next embark, `NONUPEIPE` and `TANX`, all `is_ancient: true` |

These are the game's own Ancient relic-choice events, and they take the act's first `?` room
ahead of the act's event list. The forced event is **not consumed** by this — it stays at the
cursor, and the next `?` room serves it. Every one of the nine dressed pages in the table
above was reached by walking past the ancient and re-forcing. **This is not a defect in
`force_next_event` and not a defect in the dressings**, but it is a cost a driver must pay:
it is at minimum one extra `?` room, one extra fight and one extra map step per event, and a
driver that does not check the page id it arrived at will file a false negative — proofs-7's
first two Natlan embarks did exactly that before the check was added. The check that fixed it
is three lines: read `event_id` off the page and compare it with the face's dressed id (from
`force_event.dressed_to_base()`), and if it does not match, answer the page and force again.
**A note in `understudy-seats.md`'s `skip_act` section would save the next round the same two
embarks**; no row is minted here for it.

### What the driver had to write to get there

`set_hp`, on the debug route, disclosed: **an act-1 starter deck put on an act-3 map dies in
the first elite.** Two lines were used. (1) Player life support: whenever a combat state read
the player below 65 HP, `set_hp player 300` (the endpoint clamps to `MaxHp`, so in practice
it is a top-up to full) — **299 writes over the five tours**. (2) Enemy softening: once per
floor, `set_hp <enemy> 1` on every living enemy the debug route listed — **16 enemies over
five tours**. The first Natlan and first Fontaine tours ran without the second line and both
died before reaching their events, which is why it exists. Nothing on these runs is a reading
of difficulty, of a fight, or of anything else.

## 3. The unparked events (#529) — PARTIAL, four pages of eight

All at the game's own speed (`POST /api/v1/gits/speed {"enabled": false}` before every tour).
**`PUNCH_OFF` was not forced at all this round**, as asked.

**REACHED, word for word against the face files:**

- **TRIAL, the initial page and the verdict page, on Fontaine.**
  `frame-20260916-041003-p7-fontaine-trial.png` and `…-041006-…-after.png`. The page is
  *The Empty Seat in the Gallery*, and its body is `glory-fontaine`'s `@pages.INITIAL`
  exactly:
  > The Opera Epiclese is packed to the rafters, and the Oratrice Mecanique d'Analyse
  > Cardinale hums cold above the dock. A gardes usher finds you in the aisle: a juror has
  > fainted, and the Chief Justice will not open a docket a seat short. The Oratrice weighs
  > the gallery's conviction — so tonight your opinion is evidence. The bailiff calls one
  > case only. The Merchant's Case (Merchant Trial):

  with both options printed as the file writes them —
  **Take the Empty Seat** / "Sit on the jury. One case is called, and you deliver its
  verdict." (`@pages.INITIAL.options.ACCEPT`) and **Decline the Summons** / "Try to leave the
  gallery." (`@pages.INITIAL.options.REJECT`). Taking the seat served the Merchant verdict
  page, **VERDICT: Guilty** / "Add Regret (curse) to your Deck. Obtain 2 random Relics." and
  **VERDICT: Innocent** / "Add Shame (curse) to your Deck. Upgrade 2 cards.", both carrying
  their keyword tips for Regret, Shame, Frail and Unplayable.
- **TINKER_TIME, the two-chassis page, on Sumeru.**
  `frame-20260916-…-p7-sumeru-tinker_time.png`. *The Kshahrewar Workbench* opened on
  **Choose a Frame** / "Pick one of the two frames on the bench."
  (`glory-sumeru` :308 `@pages.INITIAL.options.CHOOSE_CARD_TYPE | Choose a Frame — Pick one of
  the two frames on the bench.`), and the click served the two chassis:
  **Calibrated Striker** / "Create an Attack. (Deal 12 damage.)" (:310) and **Field Array** /
  "Create a Power." (:312), each with its *Mad Science* keyword tip.
- **COLOSSAL_FLOWER, the first reach, on Natlan.** *The Bloom of Tequemecan* printed
  **Tap the Nectar** / "Gain 35 Gold." and **Reach Deeper** / "Lose 5 HP. Advance to the next
  level." — `hive-natlan` :82–83 exactly.
- **BATTLEWORN_DUMMY, a WIN, twice.** On Fontaine, *Pressure Trial at the Institute*'s
  **First Valve** opened the fight — `Creating NCombatRoom with mode=ActiveCombat
  encounter=BATTLEWORN_DUMMY_EVENT_V1_ENCOUNTER` — and the run came out the other side and
  kept climbing. On Sumeru, *The Kshahrewar Proving Cage*'s **Setting 1** did the same, with
  the same encounter id in the log. **How the win was forced: the round's per-floor enemy
  softening had already set the dummy to 1 HP through `set_hp`**, so both wins are the debug
  route's, not the deck's, and they prove the room loads and closes and nothing else.

**NOT REACHED, and why:**

- **TRIAL's Reject page and its Double Down popup.** The Fontaine tour clicked *Take the Empty
  Seat*; the branch behind *Decline the Summons* — `@pages.REJECT.description` and its
  **Walk Out of the Opera** option, which ends the run — was never opened. A scripted page
  walker was built for exactly this (`drive7d.py`, which takes a `|`-separated list of option
  titles) and the lane went down before it was pointed at TRIAL.
- **TINKER_TIME to DONE.** The chassis page was reached and not clicked through.
- **COLOSSAL_FLOWER's third reach, either way.** Only the first level was seen on Natlan. On
  Inazuma the page arrived already past its INITIAL screen — the wire showed a single option
  printed `title: "Proceed"` with `is_proceed: true, was_chosen: true`, and the click came
  back `Choosing event option: Skim the Petals`. **The printed title and the option actually
  chosen disagreed**, which is worth a look on its own; it is recorded here as an observation
  and no row is minted for it, because it was seen once and not reproduced.
- **BATTLEWORN_DUMMY as a LOSS.** Forcing a loss wants `set_hp player 1` inside the dummy
  fight; the driver's own life-support line writes the player UP, and the two were never
  reconciled before the lane went down.

## 4. THE_FUTURE_OF_POTIONS DONE page on the act-2/3 faces — NOT DONE

No launch reached it. The event needs the run to hold **two** potions and the DONE page is
only served **after the card reward is taken** (proofs-6 §4 paid three launches to learn
that). A tour that skips into act 2 or 3 starts with an empty belt and the potions arrive
from fights, so the shape needed is proofs-6's potion driver plus a skip, and the lane went
down before it was built. **#530's four new lines (Inazuma, Natlan, Fontaine, Sumeru) remain
unproven live**, exactly as they were after proofs-6.

## 5. EB-770 live — NOT DONE

`SLIPPERY_BRIDGE` was forced on Mondstadt across two embarks and **refused every time**:

> 'SLIPPERY_BRIDGE' is not allowed in this run right now (EventModel.IsAllowed is false — an
> act, a relic or a deck condition it asks about).

Four fights were walked first on the second attempt to move the run off the early floors, and
the refusal did not change. Whatever `SlipperyBridgeMirror.IsAllowed` asks for, a fresh
Ironclad on the first third of act 1 does not have it — the same shape as proofs-6's finding
that `PunchOffMirror.IsAllowed` is `TotalFloor >= 6`. **The card-name fix is still untested
live**, and the next round should learn the predicate from the source before spending
launches on it. This is proofs-4 defect 3, now not re-tested for a second round running.

## 6. EB-767 live — NOT DONE live, but the table is right

No launch forced an event by its dressed id this round. What WAS confirmed, read-only out of
`klee-mod/KleeCode/Teyvat/TeyvatEventsGenerated.cs` through
`understudy.force_event.dressed_to_base()`, is that the substitution table resolves every id
this round needed and resolves them to the faces the mapping ruling gives — `SELF_HELP_BOOK`
to six dressed names, `SLIPPERY_BRIDGE` to six, `THE_FUTURE_OF_POTIONS` to six,
`BATTLEWORN_DUMMY` / `TINKER_TIME` / `TRIAL` to Fontaine and Sumeru only, and
`WELCOME_TO_WONGOS` / `DOLL_ROOM` / `COLORFUL_PHILOSOPHERS` / `COLOSSAL_FLOWER` to Inazuma and
Natlan only. **The nine live pages in item 2(d) each arrived under the dressed id that table
predicts**, which is the same fact from the other end, but the translation LINE that EB-767's
acceptance asks for was never printed because no dressed id was passed in.

## 7. Boot tally, and the blocker that ended the round

**39 launches. 0 stalls. 0 fuse firings. 0 `DIAG` lines. 0 truncated archives. Boot wall
median 31.8 s, max 40.1 s, nothing over 90 s.** Under concurrent C# build load throughout.
`EB-766`'s fuse was never exercised, so this round neither confirms nor weakens proofs-6's
6-of-6 reading of it.

**Launches 31–39 all failed identically, and the cause is not the build.** Every one came back

> `no_embark_path: menu_screen 'main' offers none of the embark options; saw ['settings', 'quit']`

with `blocked_options` carrying
`{"name": "timeline", "enabled": false, "reason": "manual_epoch_reveal_required",
"pending_epoch_ids": ["IRONCLAD5_EPOCH"]}` and then, after a profile reset,
`["IRONCLAD2_EPOCH"]`. **The tours' own progress unlocked an epoch on lane 1 and parked its
main menu behind the reveal** — the same blocker proofs-6 found on lane 0, now reproduced on
the disposable lane by ordinary play. This is a fair thing for a round of tours to trip: the
Sumeru tour beat `QUEEN_BOSS`.

**And the documented recovery no longer recovers.** `understudy-seats.md`'s standing rule is
that lane 1's profile is disposable and may be deleted; it was, and
`instances.seed_profile` then re-seeded it from lane 0's tree — which copies `progress.save`,
and **lane 0's `progress.save` is the one sitting on the unrevealed `IRONCLAD2_EPOCH`**. So a
fresh lane-1 profile now inherits lane 0's blocker on its first boot, and the "delete the
lane" escape hatch is closed for as long as lane 0 is parked. The two repairs that would
reopen it — marking the epoch revealed in **lane 1's own scratch `progress.save`**, or copying
lane 0's *vanilla* `progress.save` (which has no pending epoch) over lane 1's *modded* one —
were both **refused by this session's permission guard** as writes to a save file, correctly
and by design, and were not worked around. The bridge will not do it either:
`McpMod.Actions.cs` :1331 answers a timeline advance with *"Epoch unlocks are obtained but not
revealed; not forcing timeline reveal from automation"* and `manual_action_required: true`.

**So: a person clicking the reveal once, on lane 0, unblocks both lanes.** Nothing in this
tree may do it, and items 3 (the four remaining pages), 4, 5 and 6 wait on it.

## Could not do

- **TRIAL's Reject page and Double Down popup** — the page walker existed, the lane did not.
- **TINKER_TIME to DONE** — the chassis page was reached, the walk was not run.
- **COLOSSAL_FLOWER's third reach, either way** — only level 1 seen.
- **BATTLEWORN_DUMMY as a loss** — needs `set_hp player 1` inside the dummy fight, which
  fights the driver's own life-support line.
- **THE_FUTURE_OF_POTIONS' DONE page on any of the four act-2/3 faces** — needs two potions
  in the belt after a skip, and the driver for it was never built.
- **EB-770 / `SLIPPERY_BRIDGE`** — `IsAllowed` refused it on every attempt.
- **EB-767's translation line live** — no dressed id was passed in.
- **The `RELIC_TRADER`, `RANWID_THE_ELDER` and `WELCOME_TO_WONGOS` dressings** — all three
  answered `IsAllowed is false` on every force, on both act-3 faces and on Natlan and Inazuma
  respectively. Their predicates are worth reading out of the mirrors before the next round
  spends launches on them.

## What this earns

- **`EB-771` — acceptance met, and comfortably.** The op is sub-second, the arrival check
  never missed, the last-act refusal fires by name, and two embarks are enough to see all four
  act-2/3 faces. The four dressings are now reviewable on demand, which is the whole reason
  the row exists.
- **All four act-2/3 dressings are proven live for the first time** — header, combat
  background and a real fight, rest site, and two or three dressed events each, with zero
  `AssetLoadException` across four faces and 24 combats.
- **One new, cheap fact for the next driver:** the first `?` room of a skipped-into act is an
  Ancient event, so a forced event needs a second `?`.
- **One new blocker, and it is procedural rather than a build defect:** lane 1 can be parked
  behind an epoch reveal by its own play, and re-seeding it from lane 0 now inherits lane 0's
  park. A person clicking the reveal on lane 0 clears both.

Frames are in `understudy/logs/frames/`, which is gitignored for the reason
`understudy/frames.py` gives; **63 were captured this round** and the ones the sections above
rest on are cited by name. No row is retired here, no register was edited, and no C# was
changed.
