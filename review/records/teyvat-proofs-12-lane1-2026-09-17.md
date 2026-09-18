Status: RECORD (deploy proofs phase twelve; feasibility only, nothing measured)

# The campfire crash, bisected and closed; a base character rests on a Teyvat face

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
Lane 1 only (disposable profile); the user's profile and the run-history store were not
touched. Frames are gitignored under `understudy/logs/frames/`.

## The defect

The user, playing the Silent on `0.2.3656+proto`, hard-crashed at the first campfire
(2026-09-17): `godot.log` ends at `Preloading 'RestSite Room' Complete`, no managed trace.

## The bisect (each step: a deploy from main, then a scripted walk to the first Rest node)

| build | change | Silent | Klee |
|---|---|---|---|
| 0.2.3656 | as shipped | crash | — |
| 0.2.3672 | our rest scenes replaced by the game's zone scene + plate (#629) | crash | crash |
| 0.2.3672 | rest track parked out of the pack | crash | — |
| 0.2.3672 | Teyvat arm OFF | — | rests |
| 0.2.3674 | #631: FMOD event kept legal (guards on the campfire and boss parameter calls) | **rests** | — |

So: not the character, not the rest scene, not the track. The music arm's `StopMusic()`
released the game's FMOD music event; `UpdateTrack()` on rest-room entry then set
`update_campfire_ambience` on the released instance (EB-821, #631 has the proxy facts).

## Proven on 0.2.3674 (Silent, Mondstadt, act 1)

- `frame-20260917-213748-p16-map.png`: the game's own parchment map is back, nodes and
  paths at their designed contrast; the location still shows only as a dark band in the
  outer margin (#628).
- `frame-20260917-213750-p16-fight.png`: the Silent and a Hydro Slime stand ON the Windrise
  meadow, feet on the ground plane (#630's feet line, plate row 425).
- `frame-20260917-213817-p17-rest.png`: the campfire room loads; the game's own logs, fire
  and lighting draw over the Mondstadt tavern plate; `slot 'rest' -> playing packaged track
  …music_scene_mengde_saloon.ogg` in the lane log; Rest taken (56 → 38 HP display aside, the
  heal applied); Proceed returned to the map; the game stayed up.

## Not proven here

An act-1 boss through its phase changes (`UpdateMusicParameter`, guarded by the same flag);
the hurt flash and the bespoke boss rigs in motion; the Glory faces' rest-site hide list.
The tavern plate under a campfire is a taste question for the user (a campfire indoors).
