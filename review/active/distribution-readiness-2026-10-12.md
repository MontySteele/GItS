# How close is a public release? (2026-10-12)

**Why.** [USER] relaxed the art rule ("If Hoyo is openly tolerant of people using official assets, I wonder if we're going overboard on this."), then: "let's go with a) and then debate how close we are to a distribution point." This page is the debate's starting point. The art rule's new wording is in `LAW.md`, amended in this PR.

**Where things stand:**
- Every image in the build is official HoYoverse art: the 1,725 rows of `art/SOURCES.tsv`, from the Genshin wiki's official images and Wikipedia's Furina image. There is no fan art.
- The music is already out of the build.
- The installed mod is 0.2.5032: `klee.dll` 2.8 MB, `klee.pck` 15 MB and 98 MB of card images. It depends on BaseLib 3.4.7 and StS2 0.111.0.

## 1. The kits

| Kit | Stage | Latest seat results (A0) |
|---|---|---|
| Klee | Balance (ruled 2026-10-03) | Waiting on your A3 to A5 runs |
| Varka | Prototype; you said the design is "almost but not quite at 'balance'" | 1 win of 5; 4 of 5 reached the final boss (`furina-varka-wave-2-2026-10-12.md`) |
| Furina | Prototype; "a little more tentative" | 1 win of 6 |
| Kokomi | Prototype; the jellyfish rework is being built now | 0 of 30 across the four rounds before it |

All four are playable start to finish, and none of them crashes the game in seat play. The open question is fun and balance, not whether they work.

## 2. What a public build needs that a private one doesn't

1. **A release build without the harness.** Today's install includes the seat bridge (`mods/STS2_MCP`) and an auto-play mod. A public package ships only `mods/klee`.
2. **Telemetry off or opt-in.** `Diagnostics/PlayTelemetry.cs` writes fight logs. Whether it writes for every player or only on the seat lanes needs a check. A public build should not write anything unasked.
3. **A clean version stamp.** The build reads `0.2.5032+dirty`; a release reads `0.3.0` or similar.
4. **Art gaps:**
   - 30 cards wear a neighbour's painting (`tools/art_coverage.py`: 393 of 423 covered).
   - New cards from the Kokomi rework add more. A card wearing the wrong art reads as a bug to a stranger.
5. **A mod page:**
   - A short description and the four characters.
   - "Fan-made, not affiliated with HoYoverse or Mega Crit."
   - Free, with no donation links.
   - BaseLib as a dependency.
   - Co-op needs both players on the same mod version.
6. **Updates.** Each StS2 beta patch can break BaseLib mods, so a public release means a commitment to rebuild after patches.

## 3. Ways to do it

- **(a) A closed beta now.** A zip for your co-op friend's circle and a few people they trust, no public listing. It costs items 1 to 3, and the feedback comes from people who don't know Genshin, which is what the lore work needs.
- **(b) A public early-access listing** (Nexus or a GitHub release; Workshop later) once Varka and Furina are at Balance and the art gaps are filled. It is labelled early access, with Kokomi marked as in progress.
- **(c) Wait until all four kits are at Balance,** then list publicly, with the lore layer (introductions, story events) in.

## For [USER]

1. **The distribution point.**
   - **(a) Default:** a closed beta now (items 1 to 3), then a public early-access listing once Varka and Furina reach Balance.
   - (b) A public early-access listing as soon as items 1 to 6 are done, all four kits included.
   - (c) No release until all four kits are at Balance.
2. **Where it lists, when it does.**
   - **(a) Default:** a GitHub release first (no account friction, easy to pull), with Nexus and the Workshop later.
   - (b) The Steam Workshop first: the most players and one-click co-op, but uploading vouches to Valve that you hold the rights.

**Ruled 2026-10-18.** The user: "On distribution readiness - we're already in closed beta, and we're going
public once one more character hits balance."
- Pick 1 is (a) in substance. The closed beta is the friends-only Steam Workshop item, live since 2026-10-16.
  The public listing follows once one more kit reaches Balance; Varka has been at Balance since 2026-10-13.
- Pick 2 is settled by what was done: the Workshop came first, as the friends-only beta.
