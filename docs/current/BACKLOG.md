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

- Power badges borrowing another power's icon (`KleePowerIcons.cs`), counts: Klee (17), Kokomi (26), Furina (31), Varka (~25), Yae (Serial Novel), Mondstadt companions (21), co-op (10), three debuff riders. Each needs its own `art/plan.tsv` power_ row (borrowed badge as fallback); upgraded starter relics share their starters' icons. Names: `git show 3ce4f8c35:docs/current/BACKLOG.md`.
- Klee's map marker is still the wiki side-icon in the lower two-thirds of its 49x64 box (visual paper, pick 3 (a)): refit it with an `art_process` pass in the main checkout, or draw a base-style pin.
- Kokomi's three potions and Furina's two potions (#1324, #1325) were not met in a seat; check them with `understudy.embark --relic` or in a play (the relics are seen).
- Klee's rest-site pose is a still: BaseLib rebuilds the rest sprite from the texture alone, so an idle loop there needs code.
- Turn-start order: Durin's Pyro hit, Neuvillette's Hydro, Varka's Swirl, Navia's Geo and Sigewinne's Hydro all share `AfterPlayerTurnStart`, so the mod gives them no order where the sim does; stage them into one ordered broadcast if a seat sees the two disagree.
- Story chains (`klee-mod/KleeCode/Story/`), unseen in game: Kokomi's and Furina's stories (pick grids, Gold locks, Doubt's exits), routing after save and reload, the potion reward mid-event; the co-op story room's routed pages all read "A Quiet Landing" (`review/records/coop-story-rooms-2026-10-16.md`).
- Varka's Architect finale lines in `tools/build_pck.ps1` are placeholders for a writing pass, like the other three characters'.
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning (a Swirl or Crystallize on a burning enemy consumes the held Pyro; Burning keeps ticking) and Dendro as ruled, tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Show the amplifier on a hit whose element is chosen at play (Four Winds' Ascension, Northwind Avatar): no preview (the seat page names Melt and Vaporize factors since 2026-10-19).
- Kaiser Crab (Varka wave 2026-10-13, lane 5 fight 16): when Baron Bunny's turn-start hit killed Rocket, Crab Rage's 99 Block never reached Crusher. The base game grants it in `CrabRagePower.AfterDeath` and no mod code was found that removes it; reproduce live (`set_hp` Rocket low, Baron Bunny).
- Furina: whether a guest's act ends a Frozen is not printed; needs the game (Frozen itself prints since 2026-10-19).
- Durin's start-of-turn tick skipped one fight (Fogmog, trace); `RandomEnemy` may pick the Eye With Teeth illusion (`CompanionOverhaulPowers.cs:51`). Live look. (Chained Reactions is QUEUE, backlog wrap-up pick 3.)

## Harness, bridge, tools and sim

- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- `EB-193` `game_ref/role_tempo_canon.json` predates the int-var reader fix; the writer is fixed (2026-10-19), but the regen moves 25 of 110 package floors in `docs/role-tempo-floors.yaml` (QUEUE, backlog wrap-up pick 6).
- Legacy cleanup stage 6: the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, codegen `spotlight_calc_rider` / `spotlight_block_rider`) stays in every generated card because removing it changes current rows' C#. Drop it in one regen with a deploy check, riding Klee's next promotion PR.
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).

## Parked: start only when the named trigger fires

- A new `EB-489` hang shape: the game thread froze (a native hang; `dotnet-stack` showed no managed main thread), every bridge call timed out, and embark abandons the save so the run is lost. Seen Yae r5 lane 4 (2026-10-15, godot.log ending on "FocusIn received") and a co-op host in a boss fight (2026-10-16). Wakes on a second sighting.
- Before the Workshop release: check The First Exam and A Song on the Wind against Varka's in-game character story text (`review/active/klee-varka-story-chains-2026-10-14.md`, "Exam lore"); move both to his Knight of Boreas years if it differs.
- Wakes on a sighting: the Neow bundle page printed one pack's rows jumbled (a line missing, its text under another card). Not reproduced; needs the raw `bundle_select` state from such a screen.
- Wakes on a sighting: Wax Lizard Tail did not fire after Toy Box (base relics; `review/records/furina-fullrun-round-2-2026-10-10.md`). Check whether a melted relic stays in `player.Relics` unflagged, so the page still lists it (bridge `McpMod.StateBuilder.cs:1471-1488`).
