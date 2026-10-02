# Legacy cleanup: deleting the shipped kits

Plan, 2026-10-01, from an Opus read-only inventory. **All five picks RULED at
their defaults, 2026-10-01**, [USER]: "On the new 5 picks, I agree all
around." The direction, [USER]: "let's wipe out old legacy items / tech
debt."

## The shape of the problem

The current kits are not built beside the shipped kits; they are laid over
them. The current cards are `proto_*` rows in `docs/prototype-surface.yaml`,
generated into `KleeCode/Cards/Prototype/Generated/` and swapped in for the
shipped rows at `FilterThroughEpochs` (`KleeCardPool.cs`, `KokomiCardPool.cs`,
`FurinaStageRoster.SwapOfferedRows`). The tier0 sim runs the shipped world by
default. Deleting the shipped kits therefore re-founds what a pool is, in both
engines.

Size: about 290 shipped card classes (`Cards/Generated/`, `Cards/Kokomi/`,
`Cards/Furina/`), the Salon, Spotlight, Encore, Burst and Kurage Memory
systems, six shipped sheets, the `ShippedKits` property and the
`dotnet-test-shipped` gate, 97 C# `Enabled` branches plus about 156 `#if`s,
and about 390 Python arm-flag reads.

## The picks (ruled)

1. **Keep the `proto_*` ids.** Renaming breaks saves, art paths and the seat
   bridge.
2. **Saves from the 0.2.1357 package are declared dead** (alpha). No aliases
   for the deleted ids; `Cards/Retired` goes in stage 5.
3. **Furina's surviving old-kit rows move to the prototype sheet,** as the
   Furina rules pass decides (`furina-rules-pass-2026-10-01.md` §3).
4. **The 19 Fontaine companion rows move to the prototype sheet as they
   are.** A Fontaine rework is its own paper.
5. **tier0 calibration is retired until a kit reaches Balance,** then
   re-measured on the current kits. `EXPERIMENTS.md` binds nothing before
   Balance.

## The stages (each PR green on its own)

1. **Hygiene, no behaviour change:** dead tools, stale `docs/` root files,
   retired `tier05` experiments and telemetry, stale worktrees. (In flight.)
2. **Collapse `VarkaPrototype`:** he has no shipped kit. After the Varka
   element build lands.
3. **The sim flips to the current world:** every tier0 arm default on, the
   `_ARM_FLAGS` residue guard and calibration bands retired (pick 5).
4. **C# pools re-founded:** the `proto_*` rows become each pool's
   `GenerateAllCards`; Furina's survivors and the Fontaine companions ported
   (picks 3 and 4; Furina's twelve were ported by the Furina rules pass,
   2026-10-01); `SwapOfferedRows`, `DropRetiredRows` and the off-pool swap
   deleted. Verify with a pool-count pin and one deploy plus a seat smoke run.
   **Done, PR #818** (2026-10-01): every pool lists its `proto_` rows first
   and offers its arm's roster; Furina's offer is a list
   (`FurinaStageRoster.Pool`); Kokomi's Oath swap is gone; the 19 Fontaine
   rows are `proto_mf_` rows and the companion roster holds no shipped row;
   `PoolCountTests` pins 78 per kit (Klee 24 / 33 / 21, Kokomi 21 / 36 / 21,
   Furina 23 / 35 / 20, Varka 20 / 35 / 23), two Ancients and five co-op cards
   each for the first three, and the companion roster's 34 / 24 / 16. The
   shipped rows remain members only (so a held shipped card still resolves
   its pool) until stage 5. The deploy and seat smoke run are owed.
5. **The big delete:** shipped card folders, sheets, `Cards/Retired`, the
   retired systems, the `Enabled` branches and `#if`s, `ShippedKits` and its
   gate, shipped-only lints, shipped emission in `gen_klee_cards.py` (shared
   with the prototype emitter: trim, do not delete).
6. **Python flag removal and docs:** the arm-flag reads, `operations/
   prototype.md` and `codegen.md`, STATE's build paragraph, stale skills.

Out of scope: the Teyvat frame ([USER]: nothing deleted). Element switches
`SwirlPays` and `CrystallizeKeepsAura` stay until the open retest of each
switch alone is done.
