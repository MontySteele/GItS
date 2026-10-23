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

- Power badges: check the three Reaction-icon badges (Aftershock, Grand Strategist, All Four Winds) read at game size; they are wide and render small.
- Icon declutter leftovers (2026-10-19): Courtroom Drama and Quick Change are gone from both engines. Study Buddy (`ReplayNextCompanionPower`) stays: the generator's `replay_next_companion` op emits it, and that op is live in the sim, the pilot and the tier05 draft model, so retiring it is a sim change, not a repoint. The sim also keeps twins of the powers deleted on 2026-10-19 (`furina_stage.py`, `kokomi_plan.py`, `klee_overhaul.py`, `varka_oath.py`), and nothing applies them; left while the Furina and Kokomi passes are open.
- Before the first translation, key the rest of the English built in code with `CodeText` (`docs/current/operations/localization.md`, "Code-built text"): Yae's Tenko face token, Kokomi's and Yae's live captions (Yae's Annotation tips with them), the Abyss and the group 6 leftovers (`review/records/localization-code-text-census-2026-10-23.md`, groups 2, 4, 5 and 6; step 1 closed groups 1 and 3, step 2 Varka's and Furina's halves of groups 2 and 4 and the reaction riders). The Abyss strip title's key is built from the display name (`AbyssChoicePage.cs:110`); build it from the enum so a rename keeps its translation.
- Mark the Teyvat frame's rows in the English reference (its test turns the frame on; nation events, nation Ancients) so the translation and `tools/lint_loc_translations.py` skip them while the frame is off (`review/active/story-text-audit-2026-10-23.md`).
- Klee's rest-site pose is a still: BaseLib rebuilds the rest sprite from the texture alone, so an idle loop there needs code.
- Turn-start order: Durin's Pyro hit, Neuvillette's Hydro, Varka's Swirl, Navia's Geo and Sigewinne's Hydro all share `AfterPlayerTurnStart`, so the mod gives them no order where the sim does; stage them into one ordered broadcast if a seat sees the two disagree.
- Element port, phase two (`review/ruled/element-home-review-2026-09-28.md` §7.2, §7.4): Burning (a Swirl or Crystallize on a burning enemy consumes the held Pyro; Burning keeps ticking) and Dendro as ruled, tested on Kirara and Emilie. Neither engine has Burning or Dendro today.
- Kaiser Crab (Varka wave 2026-10-13, lane 5 fight 16): when Baron Bunny's turn-start hit killed Rocket, Crab Rage's 99 Block never reached Crusher. The base game grants it in `CrabRagePower.AfterDeath` and no mod code was found that removes it; reproduce live (`set_hp` Rocket low, Baron Bunny).
- Upgrades that only cut cost or add Innate: Yae's half is built (2026-10-23, `review/active/yae-block-edit-pass-2026-10-19.md`, "Upgrade census (2026-10-23)"). At Furina's next card pass, count their cost-only and Innate-only upgrades against the base five and replace the excess with a real upgrade, as Kokomi's finish pass (`review/active/kokomi-cards-2026-10-18.md` sec. 7, upgrade census) and Varka's powers pass (`varka-fang-next`) did ([USER], 2026-10-19: "You do have a habit of making too many powers just decrease their cost by 1 on upgrade").
- Durin's start-of-turn tick skipped one fight (Fogmog, trace); `RandomEnemy` may pick the Eye With Teeth illusion (`CompanionOverhaulPowers.cs:51`). Live look.

- Yae previews the 2026-10-23 suite misread: Superconduct's "Vulnerable, which applies before this hit" (does the card's printed number already include it?); "Tenko (Sakura: 15 damage)" is the total over every Sakura, not each; Pael's Legion shows doubled Block on every Block card in hand though only the first played doubles.
- Kokomi: a Strike planned by Grand Design carried out with no HP loss against a sleeping Bygone Effigy (suite 1 lane 5, fight 5); replay in a scenario to tell a sleep/Slow interaction from a dropped hit.

## Harness, bridge, tools and sim

- Seat page: "Nothing this page can count landed off it" printed under Dawn Prayer and Twin Sakura plays whose Sakura strike landed (Yae suite 2026-10-23, lanes 4 and 5).
- Co-op dev grant: `give_card` is refused in multiplayer because the pile add bypasses the action-queue synchronizer; a synced grant would let a co-op seat round be dressed with named co-op cards.
- Legacy cleanup stage 6: the Spotlight print fold (`SpotlightSystem.PrintedDamage/PrintedBlock*`, `SpotlitBlockVar`, codegen `spotlight_calc_rider` / `spotlight_block_rider`) stays. The identity wraps could go alone, but the calc rider is how 40 companion cards get `FrontFoldedDamageVar` (and 24 a `CalculatedBlockVar`), with a 0 multiplier; dropping it moves those cards to plain Damage/Block vars and their `{CalculatedDamage}` face tokens, which changes previews. Drop it in one regen with a deploy check, riding Klee's next promotion PR.
- `EB-84` enchant eligibility live smoke: three of four shapes watched; the `souls_power` to local Exhaust shape still needs a door (an Exhaust-enchant grantor with a Power in the deck).

## Parked: start only when the named trigger fires

- A new `EB-489` hang shape: the game thread froze (a native hang; `dotnet-stack` showed no managed main thread), every bridge call timed out, and embark abandons the save so the run is lost. Seen Yae r5 lane 4 (2026-10-15, godot.log ending on "FocusIn received") and a co-op host in a boss fight (2026-10-16). Wakes on a second sighting.
- Wakes on a sighting: the Neow bundle page printed one pack's rows jumbled (a line missing, its text under another card). Not reproduced; needs the raw `bundle_select` state from such a screen.
- Wakes on a sighting: Wax Lizard Tail did not fire after Toy Box (base relics; `review/records/furina-fullrun-round-2-2026-10-10.md`). Check whether a melted relic stays in `player.Relics` unflagged, so the page still lists it (bridge `McpMod.StateBuilder.cs:1471-1488`).
- Lane boots log "OVERWRITING cloud saves with local saves.": each lane pushes its saves to the account's shared Steam cloud store (save tests, 2026-10-22). The real profile's local saves win on its own boot; check whether lanes can run with Steam cloud off so a cloud restore never brings back a lane's save.
