## Prototype surface (`EB-147`) — the current kits' one sheet

`docs/prototype-surface.yaml` is the card sheet for every current kit, every
character at once: each row names its owner with `character:`, and every id
starts `proto_` (ids kept, legacy cleanup pick 1: renaming breaks saves, art
paths and the seat bridge). The old shipped kits' sheets
(`docs/*-cards.yaml`, `*-upgrades.yaml` and the three companion sheets), their
C# and the arm switches are deleted (legacy cleanup stages 5 and 6, 2026-10-01,
`review/active/legacy-cleanup-2026-10-01.md`). There is one build and one sim
world: the current kits.

```sh
.venv/Scripts/python.exe tools/gen_prototype_cards.py           # emit the C#
.venv/Scripts/python.exe tools/gen_prototype_cards.py --check   # staleness gate (CI lane, and validate.ps1 S6a)
```

**THE BUILD.** There is no switch: the surface compiles in every build (the
`PrototypeCards`, kit-arm and `ShippedKits` properties left at legacy cleanup
stage 5), so a plain `dotnet build`, `dotnet test`, `deploy.ps1`,
`validate.ps1` and the `-Package` handoff zip all carry the current kits,
unmarked. `TeyvatFrame` stays off: the frame is on hold (`STATE.md`). There is
one C# test configuration (`dotnet test klee-mod/KleeTests`, the `dotnet-test`
gate).

**THE SIM RUNS THE SAME KITS.** tier0 and tier 0.5 read the surface for every
kit: `loader.pool_replacement` is each kit's offerable pool (the C# pools'
`GenerateAllCards`), `loader._starter_ids` its ten, and
`loader.companion_roster_replacement` the companion roster
(`CompanionPool.All`). The surface stays out of `_card_index`, which holds the
reference characters' cards (`tier0/content/cards/`) and feeds their pools,
digests and balance reports. The calibration bands were measured on the old
kits and are retired until a kit reaches Balance (legacy cleanup pick 5;
`tier0/tests/retired_calibration.py`). The sim's job before Balance is
degenerate-loop and dead-card detection off the sheet draft.

**C# FIRST, sim at Balance.** A new kit rule lands in the C# mod first; the sim
twin follows once the rule survives the Prototype gate. Klee, Kokomi, Furina's
Stage, the companion roster and Varka's Oath are built in both engines today.

**Deploying.** `tools/deploy_round.py` from the art-bearing main checkout, game
closed: it rebuilds the pck if stale, runs `klee-mod\build\deploy.ps1` (the
release build, `MAJOR.AUTO`, no mark), then `deploy_bridge.ps1`, and reads the
result back off disk. **`klee-mod\build\deploy_proto.ps1` is for a build that
differs from the release**, and today that is only `-TeyvatFrame` (on hold): a
package stamped `MAJOR.AUTO+proto`. **To restore the release build run
`tools/deploy_round.py`**; the absence of `+proto` in the in-game version is
the confirmation. A dev build stays installed only when its arm is the subject
of what happens next and the handover packet names the version string
(`EB-257`). **After every deploy a round will play on, run `python -m
understudy.soak --runs 1 --character KLEEMOD-KLEE --max-fights 3` and read
`fights=3 defects=0` before any registered run (R225).**

**A face may be on the ROW** (`EB-215`). `gen_klee_cards` renders a card's
text from its body, and a Power's per power id; a row may state its own face
with `description:`, emitted into the same `Localization` list.

**KEYWORD TIPS ARE DERIVED FROM THE FACE** (`EB-272`). A row that prints a kit
keyword as `[gold]Keyword[/gold]` gets that keyword's hover tip attached by
codegen. The table is `gen_klee_cards.ARM_KEYWORDS` (Klee: `Bomb`, `Set off`,
`Spark`, `Mine`; Kokomi: `Mend`, `Plan`; companions: `Swirl`), the sentences
are `Cards/Prototype/ArmKeywordTips.cs`, and their titles are registered in
`KleeMod.InjectLocStrings`. Adding a keyword means a table row, a `For<Word>`
method and a title row; `tier0/tests/test_arm_keyword_tips.py` fails on any of
the three missing.

**An upgrade is on the ROW** (`EB-213`): `upgrade: {<key>: <delta>}`.
`gen_prototype_cards.py` registers it into the codegen's delta index before
emitting, and `tier0/content/upgrades.py` merges the same block, so both
engines read one place. A declared delta the emitter cannot express STOPS the
run. **Every row has one, or says why not** (`EB-315`): a row that declares
nothing takes the Prototype-stage rule (`upgrades.prototype_default_delta`),
which reads both printed lines (`effects:` and `plan:`); a row that genuinely
cannot upgrade carries `no_upgrade: <reason>`, refused empty by both engines.
`gen_prototype_cards.UPGRADE_DEBT` is the checked register of any other
exemption (empty since stage 6).

**Staging a row** — edit the sheet, regen, build, then grant it by id from a
scenario (`give: {card: KLEEMOD-PROTO_..., pile: hand}`); template in
`understudy/scenarios/eb147-prototype-grant.yaml`. A row the emitter cannot
express STOPS the run by name.

**THE ELEMENT PORT'S SWITCH (2026-09-28)** is not a kit arm: it switches the
shared reaction layer (`review/ruled/element-home-review-2026-09-28.md` §4 A).
`SwirlPays` is an MSBuild property defaulted on in `Directory.Build.props`,
defining `SWIRL_PAYS`, which moves `KleeMod.Elements.TriggerRules.SwirlPays`.
The sim twin `C.SWIRL_PAYS` defaults `True` to match (2026-10-08, after the
retest of the switch alone); `tools/lint_constant_parity.py` compares the two
defaults, and both sides are pinned both ways by flipping it
(`tier0/tests/test_element_port.py`; C# `KleeTests/ElementPortTests.cs`).
Its twin, `CrystallizeKeepsAura`, went with spent auras on 2026-10-03: every
reaction consumes its aura.

```sh
dotnet build klee-mod/KleeCode -p:SwirlPays=false
```

**VARKA** has no switch (legacy cleanup stage 2). His rows are `proto_vk_`,
owner `varka`; the C# rules are `Powers/Prototype/VarkaOath.cs` and the sim
twin `tier0/engine/varka_oath.py`. His cards speak one verb,
`{op: varka, kind: ...}`, each kind one `VarkaCards.<Kind>` call; its numbers
are the card's `Vk*` vars and the upgrade keys `varka_per` / `varka_base` /
`varka_amount` move them.

**KOKOMI'S PLAN.** The **Bake-Kurage** is a real pet
(`Powers/Prototype/BakeKuragePet.cs`) enemies cannot target. A card with a
Plan line is played ON it, and at the start of her next turn the jellyfish
carries that line out (`Powers/Prototype/KokomiPlan.cs`; sim
`tier0/engine/kokomi_plan.py`). A row's Plan line is a top-level `plan:` list
in the `effects:` vocabulary with the targets `front_enemy` / `all_enemies` /
`self`; the codegen emits typed `KokomiPlan.Planned` records plus the
play-on-the-jellyfish branch, and it decides the row's TargetType.

**THE COMPANION ROSTER** is the approved workshops' Universals: Mondstadt's
(`proto_mc_`, `C.MONDSTADT_OVERHAUL_POOL_IDS`), Inazuma's (`proto_mi_`,
`C.INAZUMA_OVERHAUL_POOL_IDS`) and Fontaine's sixteen ported as they are
(legacy cleanup pick 4, `proto_mf_`, `C.FONTAINE_OVERHAUL_POOL_IDS`). The seam
is one property in each engine, `CompanionPool.All` and
`loader.companion_roster_replacement`, because the banner and the reward slot
must never read different rosters (R64). The per-row reasoning is in
`docs/notes/prototype-surface-provenance.md`.

**POOL WIRING** (legacy cleanup stage 4): each character's pool lists its
`proto_` rows in `GenerateAllCards` and offers its roster
(`*Roster.OfferablePool`, `FurinaStageRoster.Pool`, `VarkaRoster.Pool`).
Counts are pinned by `KleeTests/Prototype/PoolCountTests.cs`: 78 per kit. Still checked:
the tier0 schema validators, the codegen, `lint_generated_structure` and
`lint_pool_membership`. Depth: `docs/current/atlas/klee-mod-cards.md` §7.
