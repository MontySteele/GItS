# BACKLOG

Open engineering work, one line each. No required fields and no new ids: add
an item as a plain line, and delete it in the commit that builds it. An item
that already had an `EB-` id keeps it so old citations resolve. Picks for
[USER] go in `QUEUE.md`; kit design work is in each kit's brief and `STATE.md`.
Keep a line to the defect and its file; the reasoning goes in the commit that
closes it.

Closed items are in git. The last copy in the old four-field form, with
every built row, is `git show 2b73880a:docs/current/BACKLOG.md`; the rows that
closed on 2026-09-08 are at tag `backlog-archive-2026-09-08`; older ones at tag
`pre-simplification-2026-08-06`. The dated, round-cited copy of the lines below
is `git show bf073df4:docs/current/BACKLOG.md`; the last copy before lines were
cut to about 350 characters is `git show 3ce4f8c35:docs/current/BACKLOG.md`.

## Kits and display (the mod)

- Yae's art QA (one pass, never reviewed): her character-select image has black smudges near the mouth; check her model frames, select, rest and merchant art for the same.
- Kokomi and Yae have still character-select images; Klee, Varka and Furina have animated ones. Kokomi's waits for her prototype to settle.
- Upgraded starter relics share their starters' icons (Pounding Surprise II, the Watatsumi Casket, Yae's Enlightened Blessing). Power badges: the 2026-10-19 badge pass gave every shared badge its own icon (`art/plan.tsv` power badge pass); the pairs that share on purpose (a power and its upgraded form, an Oath and its Left twin) stay shared. Check the three Reaction-icon badges (Aftershock, Grand Strategist, All Four Winds) read at game size; they are wide and render small.
- Klee's map marker is still the wiki side-icon in the lower two-thirds of its 49x64 box (visual paper, pick 3 (a)): refit it with an `art_process` pass in the main checkout, or draw a base-style pin.
- Kokomi's three potions and Furina's two potions (#1324, #1325) were not met in a seat; check them with `understudy.embark --relic` or in a play (the relics are seen).
- Klee's rest-site pose is a still: BaseLib rebuilds the rest sprite from the texture alone, so an idle loop there needs code.
- Turn-start order: Durin's Pyro hit, Neuvillette's Hydro, Varka's Swirl, Navia's Geo and Sigewinne's Hydro all share `AfterPlayerTurnStart`, so the mod gives them no order where the sim does; stage them into one ordered broadcast if a seat sees the two disagree.
- Story chains (`klee-mod/KleeCode/Story/`), unseen in game: Kokomi's and Furina's stories (pick grids, Gold locks, Doubt's exits), routing after save and reload, the potion reward mid-event. In co-op the story room is the placeholder event "A Quiet Landing" (`Story/StoryCoop.cs`) routing each player to their own page; the seat bridge reads the placeholder's title instead of the routed page's (`BuildEventState`; `review/records/coop-story-rooms-2026-10-16.md`), so check whether the in-game screen shows the right title.
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning (a Swirl or Crystallize on a burning enemy consumes the held Pyro; Burning keeps ticking) and Dendro as ruled, tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Show the amplifier on a hit whose element is chosen at play (Four Winds' Ascension, Northwind Avatar): no preview (the seat page names Melt and Vaporize factors since 2026-10-19).
- Kaiser Crab (Varka wave 2026-10-13, lane 5 fight 16): when Baron Bunny's turn-start hit killed Rocket, Crab Rage's 99 Block never reached Crusher. The base game grants it in `CrabRagePower.AfterDeath` and no mod code was found that removes it; reproduce live (`set_hp` Rocket low, Baron Bunny).
- Furina's Archaic Tooth: All the World's a Stage+ replaces Rising Applause+ and must keep its Retain ([USER], 2026-10-19: "the Ancient card should keep Retain as long as the starter does"; `furina-next`).
- Furina's starter, Rising Applause, made 117 of 268 Spends (`review/active/furina-next-2-2026-10-16.md`, pick 2 left it unchanged for that test). A starter change is [USER]'s pick; it comes back with her HP-legibility pass.
- Furina: whether a guest's act ends a Frozen is not printed; needs the game (Frozen itself prints since 2026-10-19).
- Kujou Sara's Electro rider prints "Applies Electro — Applies Hydro for 2 turns" (newcomer round 1, lane 4); its keyword tip reuses the Hydro text.
- Yae's planting rule: two Yakan Evocations made two separate Level 1 Sakura, against "Same kind: it refreshes and gains a Level" (newcomer round 1, lane 5); check live, then fix the text or the code. Dawn Prayer's "newest" lands on Twin Sakura's Kitsune, an order the page never shows.
- Durin's start-of-turn tick skipped one fight (Fogmog, trace); `RandomEnemy` may pick the Eye With Teeth illusion (`CompanionOverhaulPowers.cs:51`). Live look. (Chained Reactions is QUEUE, backlog wrap-up pick 3.)

## Harness, bridge, tools and sim

- Newcomer page (`understudy/blindplay_newcomer.py`): show a reviving enemy (Test Subject's revive left the enemy list blank for a turn); the Ancient's full heal and the run-over deck are not printed on any page; a stale reward screen showed after the Potions event (newcomer round 1, lane 5).
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- `EB-193` `game_ref/role_tempo_canon.json` predates the int-var reader fix; the writer is fixed (2026-10-19), but the regen moves 25 of 110 package floors in `docs/role-tempo-floors.yaml` (QUEUE, backlog wrap-up pick 6).
- Legacy cleanup stage 6: the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, codegen `spotlight_calc_rider` / `spotlight_block_rider`) stays in every generated card because removing it changes current rows' C#. Drop it in one regen with a deploy check, riding Klee's next promotion PR.
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).

## Parked: start only when the named trigger fires

- A new `EB-489` hang shape: the game thread froze (a native hang; `dotnet-stack` showed no managed main thread), every bridge call timed out, and embark abandons the save so the run is lost. Seen Yae r5 lane 4 (2026-10-15, godot.log ending on "FocusIn received") and a co-op host in a boss fight (2026-10-16). Wakes on a second sighting.
- Wakes on a sighting: the Neow bundle page printed one pack's rows jumbled (a line missing, its text under another card). Not reproduced; needs the raw `bundle_select` state from such a screen.
- Wakes on a sighting: Wax Lizard Tail did not fire after Toy Box (base relics; `review/records/furina-fullrun-round-2-2026-10-10.md`). Check whether a melted relic stays in `player.Relics` unflagged, so the page still lists it (bridge `McpMod.StateBuilder.cs:1471-1488`).
