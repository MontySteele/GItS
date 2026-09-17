Status: RECORD (deploy proofs phase eleven; feasibility only, nothing measured)

# The dressed Ancient speaks, and a still enemy moves

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.
Lane 1 only (disposable profile); the user's profile and the run-history store were not
touched. Frames are gitignored under `understudy/logs/frames/`.

## Build

`0.2.3642+proto` (main after #618) for the Ancient proof; `0.2.3647+proto` (main after
#620, pck contract 539 resources, five `teyvat/motion/*.tres` packed) for the motion proof.
Arms `klee,companion,kokomi,furina-stage,teyvat`.

## 1. Moon Carver on the act-1 Ancient screen (R275 pass one, #618)

Frame `frame-20260917-164651-p14-ancient-neow.png`: banner **MOON CARVER**, epithet
"Adeptus of Mt. Aocang", the face's first-visit line in the speech bubble, the game's own
whale figure behind it (art bill pending), the three boons unchanged and reading from the
game's relic rows ("Neow's Torment" keeps its base name — a boon row, frozen by R275).
Boot line: `teyvat: loc merged (149 dressed enemy name(s), … 834 dressed-Ancient row(s)
across 18 bodies)`. The boon was taken and the run reached the map; no ERROR line.

## 2. A still enemy animates after BaseLib's conversion (EB-816, #620)

Mondstadt first fight, Sternshield Crab (dresses Shrinker Beetle; motion `bounce`).
Boot line `Auto-converted 'res://teyvat/creature_visuals/sternshield_crab.tscn' from Node2D
to NCreatureVisuals`. Two frames 2 s apart on the idle board
(`frame-20260917-173303-p15-idle-a.png`, `…173305-p15-idle-b.png`): the crab's silhouette
differs (squash-and-stretch), 19,490 px changed above threshold in the enemy region while the
background is static. This settles the known unknown: `%AnimationTree` survives the
factory's reparent and the tree ticks. A Strike landed (`…173323-p15-hit.png`, 40 → 34);
the crab was then set to 1 HP through the bridge's `set_hp` (logged with its reason) and
killed with Ka-pow!. The fight ended cleanly (`has won against encounter
ENCOUNTER.SHRINKER_BEETLE_WEAK`), no exception in the lane log, rewards screen reached.
The death fade itself was not caught on a frame (frame latency exceeds the 1.2 s clip), so
the dressed-body death length is proven not to throw, not proven to be waited on.

## Not proven here

stand / hover / loom / mech sets on a body; the hurt flash (0.05 s); the death wait; how the
amplitudes read at elite and boss scale. Those are the user's eyes-on look.
