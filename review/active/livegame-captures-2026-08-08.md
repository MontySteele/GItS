<!--
lifecycle: active
owner: EB-53, EB-52
exit_when: the capture rows close and the eyes-on (17a) is given
-->
# Live-game capture packet — 2026-08-08

> **Lifecycle: REFERENCE** — a capture manifest, not a maintained page. It says
> where the files are and what each one is for; the judgements it feeds are
> [USER]'s.

**Session:** overnight live-game pass, sole driver of the running game.
**Build under capture:** deployed package `0.2-589`, built and deployed from the
main checkout at `51f673a` (`tools\build_pck.ps1` then `klee-mod\build\deploy.ps1`;
`validate: OK`, S7 suite included). Game `v0.107.1`, mods loaded = 3
(klee, STS2_MCP, STS2AutoSlayMod), PCK contract `roster-pck-v3`.
**Bridge:** vendored STS2MCP pin `55e0648`, `localhost:15526`.

**Second session, 2026-08-08b** (the residuals of the above). Rebuilt and
redeployed from the main checkout at `6d352d7` — package **`0.2-612`**,
`validate: OK`, PCK contract `roster-pck-v3`, game `v0.107.1`, mods loaded = 3.
Everything below marked `0.2-612` is from that session; the `0.2-589` captures
are unchanged. Runs: Furina `UGFHVXH64P`, `LPR6SNKX0Z`, `VDWNEQHLAV`; Klee
`3SS1V6YP07`, `UJY6VYPURT`. No seed was chosen (`set_seed` never called — the
seed endpoint read back `chosen: null, route: none` at teardown), the
understudy speed override stayed OFF, and `steam_appid.txt` was created at
launch and removed at teardown.

**Where the files are.** `art/eb52_captures/` in the **main checkout**, and
**gitignored** for the same reason `art/g12_captures/` is
(`docs/archive/g12-review-2026-08-05.md` §3/§5): every frame is the running
game with Tier F illustration in it, and the repo is public. Absolute path:

```
C:\Users\Monty\Documents\GitHub\GiTS\art\eb52_captures\
```

Every capture is the full 4K primary screen. The game's own debug corner is in
frame on all of them, so each file carries its build, its seed and its content
hash without a caption.

---

## 1. `AS2-B5` — motion look pass (BACKLOG `EB-52`(c), feeds QUEUE `S4-G17`)

Furina's rebuilt rig, captured at the **user's own animation setting**
(`fast_mode: Fast`, `time_scale: 1` — the understudy speed override was OFF for
all three bursts, so what is on screen is the pacing a player sees, not a
stepped-through one). Frame bursts rather than video: a burst is readable by
tooling and by eye, and it needs no codec.

| file pattern | frames | interval | what it shows |
|---|---|---|---|
| `b5_idle_f000..f029.png` | 30 | 130 ms | ~3.9 s of the idle loop — one full cycle of B3's poised sway / hat tilt / sword glow-pulse / coat counter-sway |
| `b5_attack_f000..f025.png` | 26 | 90 ms | the attack flourish on `Soloist's Solicitation`, plus the settle back to idle |
| `b5_hurt_f000..f044.png` | 45 | 70 ms | an enemy turn landing on Furina: the recoil, the hydro-blue flash, the Blocked/Frail popups, and the return to idle |

**One mechanical fact, not a taste claim** (Guardrail-7 and the no-fun rule
still hold — nothing here is evidence about how it *feels*): the idle burst is
not a still. Frame-differenced over the rig's bounding box, consecutive idle
frames differ by 3.5·10⁵ – 3.4·10⁶ summed luma across the crop, i.e. the loop is
running and the sprite layers are moving independently. That answers "is it
animating at all", and nothing else.

The attack burst caught the settle rather than the contact frame: at
`fast_mode: Fast` the flourish resolves inside roughly one 90 ms sample. If the
pass wants the contact pose specifically, the capture has to step the animation,
which changes the pacing being judged — a trade [USER] should make, not this
session.

## 2. `AS2-D5` — salon stage layout / composition (BACKLOG `EB-52`(b), feeds `S4-G17`)

The acceptance question is silhouette legibility at glance distance, so these
are deliberately un-cropped full-screen frames: a crop would answer a question
nobody asked.

| file | stage state |
|---|---|
| `d5_salon_1member.png` | one member deployed (`Salon Début`, random member), two empty slots, Encore ribbon at 0 |
| `d5_salon_stage_2members_encore5.png` | two members deployed with their live per-member numbers (7 and 4), one empty ghost slot, Encore ribbon at 5, Fanfare badge at 13 |
| `_crop_stage.png` | a 2× enlargement of the stage arc from the frame above — provided only so the slot geometry can be seen without a zoom tool |

A three-member stage was not reached: the members come one card at a time and
the run did not draw a third deploy while a fight was still running. `Full
Ensemble` (all three in one play) exists in the pool and is the cheap way to
stage that frame if the pass wants it.

## 3. A defect the D5 frame caught

`_crop_badges.png` (2× enlargement of Furina's power strip in
`d5_salon_stage_2members_encore5.png`). **One badge in the strip renders the red
`NOPE` missing-texture placeholder instead of an icon.** The badge carries
amount 5, which in that frame matches both `Encore` (5) and the
`Fanfare Cap +5` bonus, so the capture alone does not name which power owns it.
Filed as a BACKLOG defect; it is an asset/coverage gap, not a taste call.

**Named 2026-08-08b on `0.2-612`: it is `Fortissimo Guard`
(`SalonDeployBlockPower`), and the missing key is
`res://furina/powers/fortissimo_guard.png`.** The naming is by elimination and
the elimination is measured. `KleePowerIcons.PathFor` wires seven Furina paths
ahead of their art; `KleePck.Path` returns null while a file is absent, the
prefix falls through, and the base getter renders `NOPE`. Of those seven only
`salon_bow_block` (Stagehands) and `salon_deploy_block` (Fortissimo Guard) are
printed at 5. Stagehands was reproduced live and applies BOTH its halves from
one card, so it always renders a NOPE **pair** at 5 and 2 —
`eb65_nope_pair_combat.png`, with the hover tooltip naming it in
`eb65_nope_tooltip_stagehands.png` / `_crop_eb65_tooltip.png`. The `0.2-589`
frame has ONE NOPE at 5 beside a correctly-rendered `salon_member` badge at 2,
so it is not Stagehands. See BACKLOG `EB-65`; the art production is `EB-54`'s
"A7 + six Curtain Call power sigils", which is exactly these seven keys.

## 4. `EB-1` Punch Off — the observation

See BACKLOG `EB-1` for the finding. The raw evidence is
`eb1_punchoff_godot_log_excerpt.txt` in the same directory (a trimmed tail of
the 2.4 GB `godot.log` the hang produced) and
`eb1_hang_event_room_1JFQM9N1DJ.png` (the frozen frame: an empty event room,
no dialogue, no options).

## 5. The `EB-18` corpse-detonation smoke

The counter is **live and does record a nonzero**, which is what the previous
wave could not show:

```
run_id K16Y9XGT1Y  run_instance 20260808-041957#1  fight_index 3
encounter FOSSIL_STALKER_NORMAL  detonations 7  corpse_detonations 2  outcome won
```

(`%APPDATA%/SlayTheSpire2/gits_telemetry/play-20260808-041957.jsonl`, schema
`"1"`, `feed: "bot"`, `source: "mod"` — the session drove the game from outside,
so it labelled itself `bot` and left the human feed alone.)

**That record is the FINAL-enemy case, not the one that was owed.** Its
`enemies` array has one entry, so the payload's later bombs landed on the body
the fight ended on. Across 35 fight records written that night it was the only
nonzero.

### The non-final case — LANDED 2026-08-08b on `0.2-612`

```
run_id UJY6VYPURT  run_instance 20260808-122551#4  fight_index 1
encounter TOADPOLES_WEAK  enemies [TOADPOLE 25, TOADPOLE 22]
detonations 3  corpse_detonations 1  turns 5  outcome won
character Klee  act 1  floor 3  schema "1"  feed "bot"  source "mod"
```

(`%APPDATA%/SlayTheSpire2/gits_telemetry/play-20260808-122551.jsonl`.) The
`enemies` array has **two** entries — it is snapshotted at fight start from
`combat.Enemies.Where(e => e.IsAlive)` — and the second Toadpole was alive at
9 HP at the moment the corpse detonation resolved, so no flush and no
final-enemy race is anywhere near this reading. **The owed smoke is
discharged.**

The arrangement, in four moves, on `TOADPOLE_1`:

| turn | move | victim HP after |
|---|---|---|
| 1 | `Kaboom!` (7) then `Pop!` (bomb 5, no attack damage) | 22 -> 15, bomb armed |
| 2 | payload fires at turn start (5) ; `Kaboom!` (7) | 10 -> 3 |
| 3–4 | block only; the other Toadpole whittled to 9, never killed | 3 |
| 4 | **`Double Pop`** — two bombs, one chosen target, no attack damage | 3, `Bomb 8` |
| 5 | payload fires at turn start: bomb 1 (4) kills, bomb 2 (4) lands on the body | dead |

Frames: `eb18_payload_armed_2bombs.png` (the `Bomb 8` badge on a 3-HP Toadpole
with the second Toadpole at 9) and
`eb18_after_payload_second_enemy_alive.png` (victim gone, second enemy alive).

**Three calibration facts this run fixes, replacing last session's guesses.**

1. **Bombs land their printed damage.** A printed 7 + printed 5 payload showed
   a `Bomb 12` badge and took a Twig Slime (M) from 28 to 16 — exactly 12. The
   earlier "a printed 5+5 payload landed 7, so size the victim off 3–4" note
   was reading something else (block or a Weak on the applier); **size the
   victim off the printed number**, and off the FIRST bomb in the payload, not
   the sum.
2. **Order inside the payload is placement order,** so the victim must be at or
   under the damage of the bomb placed *first*. `Double Pop` (4+4) collapses
   that to one card and one decision and is the thing to draft; two `Trip Wire`
   plays (7+7) is the uncommon alternative.
3. **The bomb schedule is "start of your next turn, or early on unblocked
   Attack damage"** (`BombPower.BeforeSideTurnStart` / `AfterDamageReceived`,
   and the in-game Bomb keyword says so verbatim). Both bombs therefore have to
   be placed **in the same turn** — a bomb placed on turn N is gone by turn
   N+1 and can never share a payload with one placed later.

### The route that does NOT work, and why it matters

The obvious shape — bomb an enemy, then kill it with an Attack so its own
`AfterDamageReceived` early-detonation fires on the corpse — **does not count**.
Measured twice on `0.2-612` (Klee run `3SS1V6YP07`, `NIBBITS_WEAK` and
`SLIMES_WEAK`): an exactly-lethal `Kaboom!` on a bombed enemy gives
`detonations 1 / corpse_detonations 0` each time, because `RecordDetonation`
tests `target is { IsDead: true }` and inside `AfterDamageReceived` the creature
that just reached 0 HP is not yet flagged dead. That is the *exact* case
`BombPower`'s own docstring names as the definition of a corpse detonation, so
the counter and its documentation disagree. Filed as BACKLOG `EB-66`; it is a
measurement-semantics call, not a typo, and nothing but `PlayTelemetry` reads
the number.

---

## 6. `EB-64` — the CompanionKey loc row, run-verified

**VERIFIED, and the row is closed.** The build that produced `0.2-612` is the
compile verification; `eb64_companion_rider_tip.png` is the run verification —
`Blocking Notes` hovered on a live card-reward screen (Furina run
`UGFHVXH64P`, act 1 floor 6), the same surface that showed the raw key on
`0.2-589`. The tip renders **"Companion scaling / +2 Block per Companion card
you have played this turn, including Guest Stars."** — prose, no
`card_keywords.KLEEMOD-COMPANION_RIDER.title` anywhere on screen.
`_crop_eb64_tip.png` is the 1.4k-wide crop of the tip alone;
`eb64_card_reward_no_hover.png` is the same screen un-hovered, for the
before/after.

## 7. Capture manifest — files added 2026-08-08b

All in the same gitignored `art/eb52_captures/`, all full 4K primary screen
with the game's debug corner (build, seed, content hash) in frame.

| file | what it is |
|---|---|
| `eb64_card_reward_no_hover.png` | the card-reward screen, `Blocking Notes` un-hovered |
| `eb64_companion_rider_tip.png` | the same screen with the Companion rider tip open — the `EB-64` verification |
| `_crop_eb64_tip.png` | crop of the tip alone |
| `eb65_nope_pair_combat.png` | Stagehands live: the NOPE **pair** at 5 and 2 in Furina's power strip |
| `eb65_nope_tooltip_stagehands.png` | the same, with the badge hovered — the tooltip names the power and shows NOPE in its own icon slot |
| `_crop_eb65_tooltip.png` | crop of that tooltip |
| `eb18_before_killing_blow.png` / `eb18_after_killing_blow.png` | the route that does NOT count: a bombed 7-HP Twig Slime and the exactly-lethal `Kaboom!` |
| `eb18_payload_armed_2bombs.png` | `Double Pop` armed: `Bomb 8` on a 3-HP Toadpole, second Toadpole at 9 |
| `eb18_after_payload_second_enemy_alive.png` | the payload fired, victim gone, second enemy alive |

## 8. `EB-52`(a) — Fanfare-floor acquisition attempts (moved from the BACKLOG row under R177)

The target: one of the three RARE `gain_fanfare_floor` Powers
(`unheard_confession`, `the_sea_is_my_stage`, `rapturous_applause`) in a deck,
played on camera. The instrument is confirmed present on both sessions: the
bridge publishes `KLEEMOD_FANFARE`, `KLEEMOD_FANFARE_FLOOR` and
`KLEEMOD_FANFARE_CAP_BONUS` on every singleplayer GET (`player.resources`), so
the before/after read is one request either side of the play. The wall is
acquisition — the same one `docs/archive/g12-review-2026-08-05.md` §4 hit.

**Doors tried and measured 2026-08-08:** shops — three visited, seven cards
each, zero rares in two of the three (the "a shop always stocks rares"
assumption is wrong); card rewards — fifteen screens, no rare Power among
them; Neow — `Hefty Tablet` (choose 1 of 3 Rares) is the one readable 3-draw
door, ~1 Neow screen in 5, and a 3-draw from a 19-rare pool hits one of the
three targets ~42% of the time. **The reroll loop needs a game restart per
attempt**: the bridge cannot leave a run (`menu_select` answers "Not on a menu
screen" in-run), so abandon-and-retry only works from the main menu at launch
— eight restarts in a row read back one seed and one Neow offer before that
was understood.

**Second attempt 2026-08-08b, package `0.2-612`: still not acquired.** Three
fresh Furina runs (`UGFHVXH64P`, `LPR6SNKX0Z`, `VDWNEQHLAV`) drew six cards
from the 19-card rare pool and hit none of the three: Neow `Arcane Scroll`
(1 draw → The Final Verdict), two rares across eleven card-reward screens
(Flood of Emotion, Endless Waltz), and Neow `Hefty Tablet` (3 draws →
Showstopper / Rain of Roses / The Regina's Mercy). At 3/19 per draw that is
P(0 hits) = 0.842^6 = **36%** — an ordinary miss, not evidence the door is
shut.

**Two door facts the first session did not have.** (i) `Arcane Scroll`
(obtain 1 random Rare) is a second readable Neow rare door, worth ~15.8%
against Hefty Tablet's ~42%; a Neow screen carried a rare door 2 times in 3.
(ii) Card rewards do offer rares — 2 in 11 screens that session, 2 in 26
combined (~8%/screen); none was a Power, so "no rare Power among them" stands
as an observation about which rares appear, not whether rares appear at all.

**Shops remain unmeasured on the second session** — zero shop nodes were
reached in three runs, all dead in act 1 under the bot policy. The acquisition
cost is bounded below by run survival, which is the real obstacle.
