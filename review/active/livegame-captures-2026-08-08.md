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
the fight ended on. Across 35 fight records written tonight it is the only
nonzero. The non-final case was attempted three times and not landed; the recipe
and the live calibration are written down in the session's scratch arms so the
next attempt is short rather than exploratory:

- The shape needs **two bombs on one enemy inside one payload**, the enemy at or
  under the first bomb's damage, and a second enemy left alive.
- Bomb placers that carry attack damage (`Fish-Flavored Bait`, `Jumpy Dumpty`)
  detonate the payload early and can kill the victim before the payload exists;
  the usable placers are the damage-free ones (`Pop!` targeted, `Double Pop`
  targeted ×2, `Mine Toss` / `Ammo Scavenging` / `Sorry, Jean...` / `Chain Fuse`
  random). `Quick Fuse` fires a chosen enemy's payload on command, which keeps
  the whole shape inside one observed turn.
- **Measured, not printed:** a `Fish-Flavored Bait` printed at 5 damage landed
  exactly 5, but a printed 5+5 two-bomb payload landed **7 total**, so a single
  bomb lands nearer 3–4 than 5. Size the victim off that, not off the card face.
- `Double Pop+` (two bombs, one chosen target, no attack damage) collapses the
  whole arrangement into one card and is the thing to draft for.
