## Prototype surface (`EB-147`) — quarantined, dev-only

`docs/prototype-surface.yaml` is ONE staging sheet for cards being TRIED, for
every character at once (each row names its owner with `character:`, and every
id starts `proto_`). A separate dev-only generator builds it; the default
generator run does not touch it.

**C# FIRST, sim at Balance.** A new kit rule is implemented in the C# mod
(`klee-mod/`) behind the prototype switch and nowhere else, and the Python sim
(tier0 / tier0.5) is brought up only once the rule survives the Prototype gate.
The switch is the MSBuild property `PrototypeCards`, which defines the
`PROTOTYPE_CARDS` compile constant
(`klee-mod/KleeCode/KleeCode.csproj:30-31`, mirrored for the headless tests at
`klee-mod/KleeTests/KleeTests.csproj:36-37`), driven by
`-p:PrototypeCards=true` on the build and by `klee-mod\build\deploy_proto.ps1`.
The sim's job before Balance is degenerate-loop and dead-card detection off the
sheet draft, which needs no engine mirror; a two-engine build before the rule
is settled is a tax on the stage that wants taste, not numbers.

```sh
.venv/Scripts/python tools/gen_prototype_cards.py           # emit the dev-only C#
.venv/Scripts/python tools/gen_prototype_cards.py --check   # staleness gate (CI lane)
dotnet build klee-mod/KleeCode -p:PrototypeCards=true       # the DEV build
```

**Deploying a dev build** — `klee-mod\build\deploy_proto.ps1`, from the
art-bearing main checkout, game closed. It is `deploy.ps1` plus three things:
`gen_prototype_cards.py --check` first, `-p:PrototypeCards=true` on the build,
and a package stamped `MAJOR.AUTO+proto` (`+proto.dirty` when dirty) so a dev
build is identifiable on sight. It runs the SAME `validate.ps1`, whole;
`-PrototypeBuild` relaxes exactly one rule — S3 accepts the `+proto` mark,
which every other path refuses by name. Prototype rows are off-pool, so
ordinary play is unchanged. **To restore the release build run
`klee-mod\build\deploy.ps1`**: it overwrites the same `mods\klee`, and the
absence of `+proto` in the in-game version is the confirmation. Do that before
any measured run, handoff or co-op session. No `-Package` switch, deliberately
— a dev build is never handed to a peer.
**After every dev deploy, run `python -m understudy.soak --runs 1 --character
KLEEMOD-KLEE --max-fights 3` and read `fights=3 defects=0` before any
registered run (R225).**

**A face may be on the ROW too** (`EB-215`). `gen_klee_cards` renders a card's
text from its BODY, and a Power's per POWER ID, which is what stops a shipped
face drifting from what the card does — so a prototype that rewrites a shipped
power's clause could not say so without moving the shipped card's face with
it. A row states its own face with `description:`, emitted into the same
`Localization` list every shipped row uses. There is no loc merge and no
second channel; `description:` is the prototype surface's field alone and no
`docs/*-cards.yaml` row may carry it.

**KEYWORD TIPS ARE DERIVED FROM THE FACE** (`EB-272`). A row that prints an arm
keyword as `[gold]Keyword[/gold]` gets that keyword's hover tip attached by
codegen — nothing to remember, no per-row field. The table is
`gen_klee_cards.ARM_KEYWORDS` (Klee: `Bomb`, `Set off`, `Spark`, `Mine`;
Kokomi: `Mend`, `Plan`; companions:
`Swirl`), the sentences are `Cards/Prototype/ArmKeywordTips.cs`, and their
titles are registered under `#if PROTOTYPE_CARDS` in
`KleeMod.InjectLocStrings` — so a release build carries neither. The tip
renders in game under the card and on the blind-play page under the card face,
because the bridge builds `keywords` from `card.HoverTips`, which is the list
`ExtraHoverTips` feeds. **Scoped to this sheet on purpose:** on a shipped sheet
the same word means the SHIPPED rule (a shipped Bomb detonates by itself, the
arm's never does), and a row that places a shipped Bomb keeps `KLEEMOD-BOMB`
and takes no arm Bomb tip. Adding a keyword means a table row, a `For<Word>`
method and a title row; `tier0/tests/test_arm_keyword_tips.py` fails on any of
the three missing.

**An upgrade is on the ROW** (`EB-213`). Shipped deltas live in
`docs/<character>-upgrades.yaml` keyed by shipped id; a `proto_` key there
would give the deletion rule below a second file to remember, so a prototype
row carries `upgrade: {<key>: <delta>}` itself. `gen_prototype_cards.py`
registers it into the merged delta index before emitting, and everything after
that is the shipped path — same expressibility check, same `OnUpgrade`, same
campfire — with `tier0/content/upgrades.py` merging the same block so both
engines read one place. A declared delta the emitter cannot express STOPS the
run, like an inexpressible body.

**AND EVERY ARM ROW HAS ONE, OR SAYS WHY NOT** (`EB-315`). A row that declares
nothing takes the Prototype-stage rule (`upgrades.prototype_default_delta`),
which reads **both** printed lines — `effects:` and `plan:` — so a Plan-only
row's upgrade is its Plan line's delta and a two-line row moves both halves,
under `plan_*` keys bound clause by clause in `upgrades.PLAN_DELTA_OPS` (the
one table `gen_klee_cards.plan_var_effects` imports, so the two engines cannot
upgrade different clauses of one Plan). A moved plan clause is emitted as its
own `DynamicVar` that the card's `PlanClauses` PROPERTY reads back, which is
what makes `KokomiPlan.ResolveAll` carry out the upgraded number and the `+`
face print it green. **A row that genuinely cannot upgrade carries
`no_upgrade: <reason>`** — a sentence, prototype-surface only, refused empty by
both engines — and `tier0/tests/test_prototype_surface.py` fails on any
`proto_ko_` / `proto_kk_` / `proto_mc_` / `proto_mi_` row that has neither. The
opt-out is checked both ways: one the rule has since caught up with is a
finding, exactly as a paid `UPGRADE_DEBT` entry is.

**Staging a row** — edit the sheet, regen, dev-build, then grant it by id from
a scenario (`give: {card: KLEEMOD-PROTO_..., pile: hand}`); template and
preconditions in `understudy/scenarios/eb147-prototype-grant.yaml`. A row the
emitter cannot express STOPS the run by name: a prototype that cannot be
printed cannot be tried.

**A dev build also MIGRATES three shipped rows (`EB-218`, R224).** Under the
same flag pair — `C.SPARK_ALT_COST_ENABLED` in sim, `-p:PrototypeCards=true`
in C# — Klee's three hybrid Spark spenders (`powder_charge`, `hold_the_line`,
`smoke_and_sparks`) are swapped out of the offerable pool for Spark-only twins:
0 Energy, the same printed Spend 2, same rarity, same body. It rides
`C.SPARK_ALT_POOL_SUBS` like the other substitutions, so a dev build shows the
twins and a release build cannot reach them; flag off, the pool is
byte-identical to shipped (`tier0/tests/test_eb218_hybrid_migration.py`).

**A dev build can also REPLACE THE COMPANION POOL OF TWO NATIONS.** Third arm,
third property, same terms as the second:

```sh
dotnet build klee-mod/KleeCode -p:PrototypeCards=true -p:CompanionOverhaul=true
klee-mod\build\deploy_proto.ps1 -KleeOverhaul -CompanionOverhaul   # both arms
```

`-p:CompanionOverhaul=true` defines `COMPANION_OVERHAUL`, which moves
`KleeMod.Powers.CompanionOverhaul.Enabled`; the sim twin is
`C.COMPANION_OVERHAUL`. With it on, the companion reward slot, the shop channel
and the Featured Banner all read the approved workshops' rewritten Universals —
Mondstadt's 34 (`proto_mc_` rows, `C.MONDSTADT_OVERHAUL_POOL_IDS`) and
Inazuma's 24 (`proto_mi_` rows, `C.INAZUMA_OVERHAUL_POOL_IDS`) — and the 17
shipped Mondstadt rows and 15 shipped Inazuma rows cannot be offered. Fontaine
is untouched: it has no workshop yet, and `C.COMPANION_OVERHAUL_NATIONS` is the
one list that decides. The seam is ONE property in each engine —
`CompanionPool.All` and `loader.companion_roster_replacement` — because the
banner and the slot must never read different rosters (R64). Flag off, both are
byte-identical to shipped (`tier0/tests/test_companion_overhaul.py`,
`tier0/tests/test_inazuma_companion_overhaul.py`,
`klee-mod/KleeTests/Prototype/CompanionOverhaulTests.cs`). **Unlike the Klee
overhaul this arm is built in BOTH engines**, because it needed almost no new
op: every Mondstadt row is written in the grammar the sheets already speak, and
Inazuma adds exactly one verb (`block_half_damage`).

**A dev build can also REPLACE KOKOMI'S WHOLE KIT.** Fourth arm, fourth
property, same terms as the others:

```sh
dotnet build klee-mod/KleeCode -p:PrototypeCards=true -p:KokomiOverhaul=true
```

`-p:KokomiOverhaul=true` defines `KOKOMI_OVERHAUL`, which moves
`KleeMod.Powers.KokomiOverhaul.Enabled`; the sim twin is `C.KOKOMI_OVERHAUL`.
With it on, her starter is the slice's ten cards on four ids
(`C.KOKOMI_OVERHAUL_STARTER_IDS`), her starting relic is **Tamakushi Casket**
instead of the Pearl of Wisdom, and her whole offerable pool is the slice's 26
rows plus the Ancient tail (`C.KOKOMI_OVERHAUL_POOL_IDS`, `EB-284`). Flag off,
all three are byte-identical to shipped
(`tier0/tests/test_kokomi_overhaul.py`,
`klee-mod/KleeTests/Prototype/KokomiOverhaulRuleTests.cs`).

**DRAFT 6 IS ONE RULE, AND IT NEEDED A CREATURE.** The **Bake-Kurage** is a
real PET (`Powers/Prototype/BakeKuragePet.cs`): a `CustomPetModel` on her side
of the field that enemies cannot target — free by construction, because an
enemy move only ever sees `CombatState.PlayerCreatures` and a pet has no
`Player`. A card with a **Plan** line is played ON it, and at the start of her
next turn the jellyfish carries that line out. The queue is
`Powers/Prototype/KokomiPlan.cs`: typed clauses, per player, one ENTRY per
card, drained on the marker power's `AfterPlayerTurnStart`.

**THE SHEET GAINED ONE KEY.** A row's Plan line is a TOP-LEVEL `plan:` list in
the same op vocabulary `effects:` speaks, with the targets `front_enemy` /
`all_enemies` / `self`; the codegen emits it as typed `KokomiPlan.Planned`
records on the card plus the one-`if` play-on-the-jellyfish branch at the top
of `OnPlay`, and it decides the row's TargetType — `CustomTargetType.Pet` for a
Plan-only row, the arm's own `KokomiTargets.PetOrEnemy` when the now-line aims,
`CustomTargetType.PetOrSelf` otherwise. The base library ships the predicates
and every targeting patch for two of the three.

**WHAT DRAFT 6 RETIRED, and it is deleted rather than switched off:** Tide,
Surge, Exert, the pulse and its budget, the Garment, Strength-to-Tide, Orders
and Tactics. Their ops are gone from both engines' vocabularies, their
constants from both sides of `lint_constant_parity`, and their C# from
`Powers/Prototype/`. One SHIPPED hook changes behaviour under the arm rather
than stopping: `KokomiResourceHooks.TryModifyPowerAmountReceived` skips its
Strength refusal, because draft 6's rule 3 is "your Strength and Dexterity
count, since the plans are hers".

**ONE FLAG FOR BOTH NATIONS, deliberately.** There is no `InazumaOverhaul`
property: the arm means "the companion pool is the approved workshops' pool",
and a second property would let a build offer one nation's rewrites beside the
other nation's shipped rows — a state no document describes and no seat would
be asked to grade.

**Inazuma's twenty-four (2026-09-02)** are the approved workshop
`companion-workshop-inazuma-2026-09-01.md` sec.3 — fifteen re-authored shipped
rows and nine characters given their first. Twelve of them spend a hook the
Mondstadt second wave already built (the end-of-turn volley, the start-of-turn
payout, the Block-absorption mark, the next-Attack element override, the
reaction event, a power hosted on a chosen body, `AfterCardPlayed`); FOUR
things are new — a per-play damage total (Gorou's "Block equal to half the
damage dealt"), a hit that ignores Block (Chiori's Tamoto), a per-turn Swirl
count (Heizou) and a companions-played count that needed no new state at all
(Raiden). **Mend became character-agnostic** in the same change and by one
line: Mizuki's Rare is a Universal that prints the Kokomi arm's keyword, so
`KokomiRules.Mend` asks `MendIsLive` — either arm, any player's creature —
while the rule under it ("never above the HP you entered the fight with") stays
written once. Six shipped paths carry a flag-guarded branch or a defaulted
parameter for the arm — the damage tail, the card-play loop, the turn-start
counter clear, the combat-start Mend ceiling, `ElementalHit.Deal` and
`KokomiRules` — and each is pinned byte-identical with the flag off rather than
assumed. The per-row reasoning and the fourteen ambiguities the printed text
left open are in `docs/notes/prototype-surface-provenance.md`.

**All thirty-four MONDSTADT Universals, in two waves.** The first twenty-one rode the two
turn hooks the engine already ran. The other THIRTEEN were held back because
their printed text wanted a hook that existed in neither engine, and those
hooks are now built — a per-instance Block-absorption trigger, a
pre-enemy-attack trap (the hook Klee's Mine already uses,
`BeforeDamageReceived`), a next-Attack element override behind ONE element
funnel per engine, a Swirl event that remembers its element, an
Attacks-played-this-turn counter, a next-Attack cost discount, a Block-reading
damage formula, a power hosted on its chosen target, a counting delayed blade,
and two damage-pipeline modifiers behind a modal Power. **Still no new op and
no new target spelling:** the thirteen rows are `apply_power`, `damage` and
`conditional`, plus one new predicate (`nth_attack_this_turn_<N>`) and one new
C# reader for a count tier0 already had (`player_block`). Sim
`tier0/tests/test_companion_overhaul_hooks.py`, mod
`klee-mod/KleeTests/Prototype/CompanionOverhaulHookTests.cs`; the per-row
reasoning is in `docs/notes/prototype-surface-provenance.md`. Five shipped
paths carry a flag-guarded branch for it — the enemy-attack loop, `card_cost`,
`_element_for`, `deal_damage_to_enemy` and `_react` — and each is pinned
byte-identical with the flag off rather than assumed.

**THE DELETION RULE (R213 B).** *Once a slice is accepted or rejected, its rows
LEAVE the surface.* Accepted rows are re-authored onto the owning character's
real sheet — ruled numbers, stamp bump, art — and deleted here in the same
commit; rejected rows are deleted outright, with the reasoning in the slice's
packet under `review/`, never as a commented-out row. **This is never a second
permanent pool**, and an empty file is the healthy state.

What the quarantine is: without `-p:PrototypeCards=true` the classes are not
compiled at all, so no release build, no pck and no ordinary run can reach one;
under the flag they go into each character's OFF-POOL list (in the pool so
`CardModel.Pool` resolves, out of `GetUnlockedCards` so no reward roll or
transform can produce one). The rows never enter tier0's card index, so no run
template, digest or balance report sees them, and the sheet is excluded by name
from `lint_sheet_stamp` and `card_distinctness_report` — **staging a row bumps
no stamp**. Still checked: the tier0 schema validators, the codegen,
`lint_generated_structure` and `lint_pool_membership`.
Depth: `docs/current/atlas/klee-mod-cards.md` §7.
