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
   **5a done, PR #822** (2026-10-01): the shipped card classes
   (`Cards/Generated`, `Cards/Kokomi/Generated`, `Cards/Furina/Generated`,
   Klee's hand-written seven) and `Cards/Retired` with its alias register
   (`docs/retired-card-ids.yaml`, `gen_retired_card_aliases.py`,
   `retired_ids.py`, `lint_retired_card_ids.py`); the four kit arms'
   `Enabled` switches, their `#if`s and MSBuild properties, `ShippedKits` and
   `dotnet-test-shipped`; the Salon, the Spotlight's state and powers, Encore,
   the shipped Fanfare meter, all three Burst meters and kit Burst cards,
   Kokomi's Charge, the Kurage Memory, the Muster transform, the shipped
   Sparks free-Attack rule and the Companion Spark (`KleeCompanionSpark`, and
   its `ForCovenSpark` rider in the codegen); the starting-companion roll;
   `gen_roster_cards.py` and the shipped plan builders in `gen_klee_cards.py`.
   Kept and trimmed because current cards call them: `SpotlightSystem` (the
   generated print fold, now the identity), `CurtainCallHooks` (Quick Change,
   Courtroom Drama), `KitGrant.NotKitCard` (now always true), the shipped
   `BombPower` and companion powers the ported rows apply. The twelve
   retired-arm prototype rows (`proto_spark_*`, the Shinobu, Thoma and Itto
   twins, `proto_kurages_oath_memory`, `proto_muster_subsidy_funnel`) emit no
   C# (`gen_prototype_cards.SIM_ONLY_ROW_IDS`); the sim still reads them.
   **Moved to stage 6:** the shipped sheets (`docs/*-cards.yaml`,
   `*-upgrades.yaml`, the three companion sheets), because the sim's
   flags-off world and its tests still load them; the twelve retired-arm
   rows; the codegen's spotlight wrap and `NotKitCard` filter; the
   `MetersByTurn` zero columns in `PlayTelemetry`.
   **5b done, PR #824** (2026-10-01): the engine pieces only cut cards
   used, in C#, the sim and the codegen (the two BACKLOG lines). Klee:
   `SplitLargest` / `split_largest_bomb`, Flame Dance's non-Pyro Set off
   filter, `FriendshipBraceletPower`, `TectonicTidePower`. Kokomi: eight Plan
   kinds no row spelled (`DamagePerCompanionLastTurn`,
   `BlockPerPlanThisMorning`, `DrawPerPlanAfter` and Scout Ahead's drain
   rate, `NextAttackDamage`, `DamageIfUnhurt`, `AttackDamageThisTurn`,
   `FirstCompanionFree`, `CasketGain`), their powers (Song of Pearls, Moon
   Signal, Rally's discount, Battle Plan's rider, Chain of Command's free
   Companion), the cancels and their give-back (`CancelLast`,
   `CancelAllForNext`, `GiveBack`, `all_streams`), the morning-damage rider,
   the second-number upgrade path, and the three rule constants (Moon Signal,
   Rally, Battle Plan). No current card's behaviour moved; the regenerated
   cards differ only in Tinder Toss and Windblume Fireworks dropping a
   `nonPyroAuraOnly: false` argument. **Also for stage 6:** the codegen's
   `KokomiRiderTips` branches (shipped-only, no prototype row reaches them)
   and `KokomiPlan.NoteRider`, which no rider calls now.
6. **Python flag removal and docs:** the arm-flag reads, `operations/
   prototype.md` and `codegen.md`, STATE's build paragraph, stale skills.
   **6a (the sim's flags-off world and the sheets), 2026-10-02:** the arm
   flags are gone from the sim (`KLEE_OVERHAUL`, `COMPANION_OVERHAUL`,
   `KOKOMI_OVERHAUL`, `FURINA_STAGE` always on; `SPARK_ALT_COST_ENABLED` and
   `KURAGE_MEMORY` deleted with the Spark alternative cost, the Kurage Memory
   and the Muster subsidy), with the `shipped_world` fixture and the arm
   residue guard. The nine shipped sheets are deleted
   (`docs/{klee,kokomi,furina}-{cards,upgrades}.yaml`, the three companion
   sheets; `ancient-upgrades.yaml` and `ref-ironclad-upgrades.yaml` stay,
   because the Ancients and the base Strike/Defend read them), and so are the
   twelve retired-arm rows; their fourteen `KNOWN_STALE` art entries stay. The
   sim's Furina pool is now `pool_replacement` (her 78, matching C#: the stray
   shipped Overflowing Hospitality is gone), her shipped Ethereal Spotlight
   relic hook and the three kit Bursts left the character yamls, and the
   yamls' battery packages and winrate bands went with the sheets.
   Shipped-only tests, five shipped-only lints (`lint_sheet_stamp`,
   `lint_role_tempo_coverage`, `lint_strict_domination`,
   `lint_sheet_comments`, `lint_kokomi_decksize`) and
   `lint_starter_pool_overlap` are deleted; tests of engine, tool and seat
   machinery that used a shipped card as a fixture are ported to current rows
   or inline cards. Regenerated C# is byte-identical (the manifest loses the
   deleted row's upgrade entry). **PR #832, merged.** Left for 6b: the C# dead code, the codegen's
   spotlight wrap and shipped-sheet readers, the understudy ports, the docs.
   **6b (dead code and docs), 2026-10-02:** `KitGrant.NotKitCard` and
   `Powers/KitBurst.cs` are deleted, and the codegen passes `null` for the
   selector filter (the one regenerated diff: Short Circuit's dead argument).
   Also deleted: the codegen's dead rider-tip branches
   (`KokomiRiderTips`, `FurinaRiderTips`, `SalonMemberTips`,
   `KleeCardTooltips.ForBurst`, whose classes went in stage 5) and their
   helpers; its shipped upgrade and companion sheet readers; the `cost_mod`
   op; `KokomiPlan.NoteRider` and its collector; `PlayTelemetry`'s
   `MetersByTurn`; `ExplosiveFrags.OpeningSparks`; and the five shipped
   companion powers no row applies (Oz, Witch's Flame, Solar Isotoma,
   Celestial Gift, Friendly Visit's `CompanionCostThisTurnPower`), with
   `SparkAttackCostPower` and its sim constant. `BombPower`,
   `ReplayNextCompanionPower`, `AttackUpThisTurnPower`, `NextAttackUpPower`,
   `ShatterBonusPower` and the Fontaine and Curtain Call powers stay: current
   rows apply them. `lint_keyword_meters` now treats Charge and Burst as
   retired words. Docs: `operations/prototype.md` and `codegen.md`
   rewritten, STATE's build paragraph, the deploy skill. **Left over (BACKLOG
   lines):** the codegen's spotlight wrap and the generated header's
   upgrades-sheet line, both of which would change the C# emitted for
   current rows; the sim's shipped-kit machinery. **PR #833, merged.**
   **6c (the understudy ports), 2026-10-02:** of the thirteen understudy
   tests stage 5 deleted with the shipped faces, nine still tested something
   real and are back on current rows: the generated-text fallback, the
   printed cost and Spark indices (cross-checked against the surface), the
   by-id cost key and its discount note (`test_staged_turn.py`), and the
   upgraded-face, two-arm swap and folded "Written:" face
   (`test_understudy_blindplay.py`; the folded tests had been passing
   vacuously on a deleted id). Four stay deleted: the shipped Sparks
   free-Attack rule on two pages, the Encore gloss and the Spotlight token
   classes. **Left over (a BACKLOG line):** the seat page's Kurage memory and
   Salon panels and the bridge files that fed them
   (`vendor/STS2_MCP/gits/GitsKurageMemory.cs`, `GitsFurinaSalon.cs`), which
   need a bridge deploy to retire.

Out of scope: the Teyvat frame ([USER]: nothing deleted). Element switches
`SwirlPays` and `CrystallizeKeepsAura` stay until the open retest of each
switch alone is done.
