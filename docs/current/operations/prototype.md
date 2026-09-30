## Prototype surface (`EB-147`) — the current kits, in every build

`docs/prototype-surface.yaml` is ONE staging sheet for the cards of the current
kits, for every character at once (each row names its owner with
`character:`, and every id starts `proto_`). A separate generator builds it;
the default roster generator run does not touch it.

**THE CURRENT KITS ARE THE RELEASE BUILD (2026-09-28).** [USER]'s ruling, in
his words: "The current character builds are much more progressed than the old
prototypes were, even though it's still a work in progress. Let's go ahead and
make all 3 current builds the active release builds to avoid this confusion."
Until then the surface and the arms were quarantined out of every release
build and reached the game only through a `+proto` dev deploy; sessions kept
reading the old shipped kits as current, and a plain `deploy.ps1` installed
them. Now `klee-mod/Directory.Build.props` sets five properties whenever the
build names none of them: `PrototypeCards` (compiles the surface), and the four
kit arms `KleeOverhaul`, `CompanionOverhaul`, `KokomiOverhaul` and
`FurinaStage`. So a plain `dotnet build`, `dotnet test`, `deploy.ps1`,
`validate.ps1` and the `-Package` handoff zip all carry the current kits,
unmarked. `TeyvatFrame` is not defaulted: the frame is on hold (`STATE.md`).
Stage 2, later, deletes the old shipped kits' code; until then they build
under one opt-out:

```sh
dotnet build klee-mod/KleeCode                               # the current kits
dotnet build klee-mod/KleeCode -p:ShippedKits=true           # the old kits, whole
dotnet build klee-mod/KleeCode -p:FurinaStage=false          # one arm off
```

**C# FIRST, sim at Balance.** A new kit rule is implemented in the C# mod
(`klee-mod/`) behind the prototype switch and nowhere else, and the Python sim
(tier0 / tier0.5) is brought up only once the rule survives the Prototype gate.
The switch is the MSBuild property `PrototypeCards`, which defines the
`PROTOTYPE_CARDS` compile constant (`klee-mod/KleeCode/KleeCode.csproj`,
mirrored for the headless tests in `klee-mod/KleeTests/KleeTests.csproj`), on
by default since the ruling. **The tier0 sim still runs the SHIPPED kits:** its
twins (`C.KLEE_OVERHAUL`, `C.COMPANION_OVERHAUL`, `C.KOKOMI_OVERHAUL`,
`tier0/engine/furina_stage.FURINA_STAGE`) stay `False`, because the
calibration bands are measured on the shipped world. The sim's job before
Balance is degenerate-loop and dead-card detection off the sheet draft, which
needs no engine mirror; a two-engine build before the rule is settled is a tax
on the stage that wants taste, not numbers.

```sh
.venv/Scripts/python tools/gen_prototype_cards.py           # emit the C#
.venv/Scripts/python tools/gen_prototype_cards.py --check   # staleness gate (CI lane, and validate.ps1 S6a)
```

**THERE ARE TWO GATED TEST CONFIGURATIONS**, and `tools/gates.py` runs both on
every push (`dotnet-test`, `dotnet-test-shipped`):

```sh
dotnet test klee-mod/KleeTests                                          # the current kits
dotnet test klee-mod/KleeTests -p:ShippedKits=true -p:PrototypeCards=true  # the old kits, arms compiled and off
```

(`-p:ShippedKits=true` alone, no prototype surface at all, still builds and
passes; it is not gated.) **The second is a gate because a configuration no
gate runs goes red quietly** (`EB-781`: nine shipped meter pins stood red under
the Stage for a week). A pin about a shipped rule that the default arms change
says which world it is about in one line, through
`KleeTests/Harness/ArmScope.cs`: `ArmScope.ShippedMetersLive()` (no Stage) and
`ArmScope.ShippedKlee()` (no Klee overhaul). The pin keeps running in both
configurations rather than being `#if`'d out of one.

**Each arm's suite opens with `The_arm_ships_on`,** asserting its
`DefaultEnabled` is `true`. In a build that opts the arm out
(`-p:ShippedKits=true` or `-p:<Arm>=false`) that pin cannot say anything true:
green would mean the opt-out did nothing, and red is the opt-out working. So it
is **skipped there by an `#if`, not left to fail**, because a red that means
"the switch works" teaches everyone to ignore reds.

The arms' rules are exercised in both directions without any property:
`Enabled` is a settable static, so one build asserts both sides of every
switch. That is the only reason `KleeTests.csproj` mirrors the arm properties
at all, and not because any pin needs one.

**Deploying.** `tools/deploy_round.py` from the art-bearing main checkout, game
closed: it rebuilds the pck if stale, runs `klee-mod\build\deploy.ps1` (the
release build: the current kits, `MAJOR.AUTO`, no mark), then
`deploy_bridge.ps1`, and reads the result back off disk. The release gate
checks the surface too: `validate.ps1` S6a runs `gen_prototype_cards.py
--check` since the ruling.

**The dev deploy, `klee-mod\build\deploy_proto.ps1`, is now for a build that
DIFFERS from the release**, and today that is only `-TeyvatFrame` (on hold). It
refuses without it, because a `+proto` package whose contents equal the
release is the confusion the ruling removed. It is `deploy.ps1` plus the
frame, a package stamped `MAJOR.AUTO+proto` (`+proto.dirty` when dirty), a
codegen check first and the bridge last. It runs the SAME `validate.ps1`,
whole; `-PrototypeBuild` relaxes exactly one rule, S3 accepting the `+proto`
mark, which every other path refuses by name. **To restore the release build
run `tools/deploy_round.py`** (or `deploy.ps1`): the absence of `+proto` in
the in-game version is the confirmation. No `-Package` switch, deliberately: a
dev build is never handed to a peer.

**WHEN A DEV BUILD STAYS, AND WHEN THE RELEASE BUILD GOES BACK (`EB-257`).**
`+proto` exists so that "which build is installed" has an answer on screen when
both paths write the same `mods\klee` directory (R217 D). The rule is stated by
what the NEXT session is:

- **A dev build stays** only when its dev arm is the SUBJECT of what happens
  next (a seat round, a scenario, a soak, or [USER] playing it), **and the
  packet handing the machine over names the version string** in its "What is
  installed right now" section.
- **The release build goes back at teardown** in every other case: before a
  measured run or a registered cell, before any handoff or co-op session, and
  before any play the dev arm is not the subject of.

A session that finds a `+proto` build installed and no packet naming it
restores before playing rather than reports on it.
**After every deploy a round will play on, run `python -m understudy.soak
--runs 1 --character KLEEMOD-KLEE --max-fights 3` and read `fights=3
defects=0` before any registered run (R225).**

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
`KleeMod.InjectLocStrings` — so a `-p:ShippedKits=true` build carries neither. The tip
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

**Staging a row** — edit the sheet, regen, build, then grant it by id from
a scenario (`give: {card: KLEEMOD-PROTO_..., pile: hand}`); template and
preconditions in `understudy/scenarios/eb147-prototype-grant.yaml`. A row the
emitter cannot express STOPS the run by name: a prototype that cannot be
printed cannot be tried.

**The prototype switch also MIGRATES three shipped rows (`EB-218`, R224).** Under the
same flag pair — `C.SPARK_ALT_COST_ENABLED` in sim, `-p:PrototypeCards=true`
in C# — Klee's three hybrid Spark spenders (`powder_charge`, `hold_the_line`,
`smoke_and_sparks`) are swapped out of the offerable pool for Spark-only twins:
0 Energy, the same printed Spend 2, same rarity, same body. It rides
`C.SPARK_ALT_POOL_SUBS` like the other substitutions, so a default build shows the
twins and a `-p:ShippedKits=true` build cannot reach them; flag off, the pool is
byte-identical to shipped (`tier0/tests/test_eb218_hybrid_migration.py`).

**THE ELEMENT PORT'S TWO SWITCHES (2026-09-28)** are not arms: they switch
the shared reaction layer every kit reacts through
(`review/ruled/element-home-review-2026-09-28.md` §3, §4). `SwirlPays` and
`CrystallizeKeepsAura` are MSBuild properties defaulted on beside the arms in
`Directory.Build.props`, defining `SWIRL_PAYS` / `CRYSTALLIZE_KEEPS_AURA`,
which move `KleeMod.Elements.TriggerRules.SwirlPays` /
`.CrystallizeKeepsAura` (settable, compiled in every build). One off:

```sh
dotnet build klee-mod/KleeCode -p:SwirlPays=false
dotnet build klee-mod/KleeCode -p:CrystallizeKeepsAura=false
```

`-p:ShippedKits=true` turns both off. The sim twins `C.SWIRL_PAYS` and
`C.CRYSTALLIZE_KEEPS_AURA` ship `False` for the arms' reason and are pinned
both ways by flipping them (`tier0/tests/test_element_port.py`; the C# pins
are `klee-mod/KleeTests/ElementPortTests.cs`). A sim pin about the old
consume rule names that world with the `consume_triggers` fixture.

**VARKA IS A CHARACTER, NOT AN ARM OF ONE** (prototype batch one,
2026-09-29). `VarkaPrototype` is defaulted on beside the arms in
`Directory.Build.props` and defines `VARKA_PROTOTYPE`, which does two things:
it moves `KleeMod.Powers.VarkaPrototype.Enabled` (his rules, in
`Powers/Prototype/Varka*.cs`, compile with the surface either way, so one
build pins both sides), and it compiles `Varka.cs`, `VarkaCardPool.cs` and
`VarkaRelicPool.cs`, which is what puts him on the select screen. Off
(`-p:VarkaPrototype=false`, or `-p:ShippedKits=true`) there is no Varka at
all. His rows are `proto_vk_`, owner `varka`, a prototype-only profile
(`gen_klee_cards.PROTOTYPE_OWNERS`). **The Oath rework (2026-09-29) is built in
both engines:** the C# rules are `Powers/Prototype/VarkaOath.cs`, and the sim
twin is `tier0/engine/varka_oath.py` behind its own switch `VARKA_OATH`, off
like the arms' twins and flipped by `tier0/tests/test_varka_oath.py`. His
cards speak one verb, `{op: varka, kind: ...}`, each kind one
`VarkaCards.<Kind>` call; its numbers are the card's `Vk*` vars and the
upgrade keys `varka_per` / `varka_base` / `varka_amount` move them.

**The companion arm REPLACES THE COMPANION POOL OF TWO NATIONS.** Third arm,
third property, same terms as the second, on by default since 2026-09-28:

```sh
dotnet build klee-mod/KleeCode                                # on
dotnet build klee-mod/KleeCode -p:CompanionOverhaul=false     # off
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

**The Kokomi arm REPLACES KOKOMI'S WHOLE KIT.** Fourth arm, fourth
property, same terms as the others, on by default since 2026-09-28:

```sh
dotnet build klee-mod/KleeCode                                # on
dotnet build klee-mod/KleeCode -p:KokomiOverhaul=false        # off
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

What is left of the quarantine since 2026-09-28: under `-p:ShippedKits=true`
the classes are not compiled at all, so that build cannot reach one; in every
other build (the release included) they go into each character's OFF-POOL list
(in the pool so `CardModel.Pool` resolves, out of `GetUnlockedCards` so no
reward roll or transform can produce one), and the four kit arms, on by
default, put their own rows in the starters and the offerable pools. The rows never enter tier0's card index, so no run
template, digest or balance report sees them, and the sheet is excluded by name
from `lint_sheet_stamp` and `card_distinctness_report` — **staging a row bumps
no stamp**. Still checked: the tier0 schema validators, the codegen,
`lint_generated_structure` and `lint_pool_membership`.
Depth: `docs/current/atlas/klee-mod-cards.md` §7.
