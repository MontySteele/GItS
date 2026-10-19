## Prototype surface (`EB-147`) — the current kits' one sheet

`docs/prototype-surface.yaml` is the card sheet for every current kit: each
row names its owner with `character:`, and every id starts `proto_` (ids are
kept: renaming breaks saves, art paths and the seat bridge). There is one
build and one sim world, the current kits; the old kits' sheets and C# are
gone (`review/ruled/legacy-cleanup-2026-10-01.md`). Regenerate with
`tools/gen_prototype_cards.py [--check]` (`OPERATIONS.md`).

**THE BUILD.** There is no switch: the surface compiles in every build, so a
plain `dotnet build`, `dotnet test klee-mod/KleeTests`, `deploy.ps1`,
`validate.ps1` and the `-Package` zip all carry the current kits, unmarked.
`TeyvatFrame` stays off (`operations/teyvat-frame.md`).

**THE SIM RUNS THE SAME KITS.** tier0 and tier 0.5 read the surface:
`loader.pool_replacement` is each kit's offerable pool (the C# pools'
`GenerateAllCards`), `loader._starter_ids` its ten, and
`loader.companion_roster_replacement` the companion roster
(`CompanionPool.All`). The surface stays out of `_card_index`, which holds the
reference characters' cards. The calibration bands are retired until a kit
reaches Balance (`tier0/tests/retired_calibration.py`); before Balance the
sim's job is degenerate-loop and dead-card detection off the sheet draft.

**C# FIRST, sim at Balance.** A new kit rule lands in the C# mod first; the sim
twin follows once the rule survives the Prototype gate. Klee, Kokomi, Furina's
Stage, the companion roster, Varka's Oath and Yae's Shrine are built in both
engines today.

**Deploying.** `tools/deploy_round.py` from the art-bearing main checkout,
game closed (`operations/build-deploy.md`). `klee-mod\build\deploy_proto.ps1`
is only for a build that differs from the release, today only `-TeyvatFrame`,
stamped `MAJOR.AUTO+proto`; **restore the release with
`tools/deploy_round.py`**, confirmed by no `+proto` in the in-game version. A
dev build stays installed only when its arm is the subject of what happens
next and the handover packet names the version string (`EB-257`). **After
every deploy a round will play on, run `python -m understudy.soak --runs 1
--character KLEEMOD-KLEE --max-fights 3` and read `fights=3 defects=0` before
any registered run (R225).**

**A face may be on the ROW** (`EB-215`): `description:` states the row's own
face; otherwise `gen_klee_cards` renders it from the body.

**KEYWORD TIPS ARE DERIVED FROM THE FACE** (`EB-272`). A row printing a kit
keyword as `[gold]Keyword[/gold]` gets its hover tip from codegen. Adding a
keyword means a row in `gen_klee_cards.ARM_KEYWORDS`, a `For<Word>` method in
`Cards/Prototype/ArmKeywordTips.cs` and a title in `KleeMod.InjectLocStrings`;
`tier0/tests/test_arm_keyword_tips.py` fails on any of the three missing.

**An upgrade is on the ROW** (`EB-213`): `upgrade: {<key>: <delta>}`, read by
both engines (`gen_prototype_cards.py` and `tier0/content/upgrades.py`). A
delta the emitter cannot express STOPS the run. **Every row has one, or says
why not** (`EB-315`): a row with none takes
`upgrades.prototype_default_delta` (which reads `effects:` and `plan:`); a row
that cannot upgrade carries `no_upgrade: <reason>`, refused empty by both
engines. `gen_prototype_cards.UPGRADE_DEBT` is the checked exemption register
(empty).

**Staging a row** — edit the sheet, regen, build, then grant it by id from a
scenario (`give: {card: KLEEMOD-PROTO_..., pile: hand}`); template
`understudy/scenarios/eb147-prototype-grant.yaml`.

**THE ELEMENT PORT'S SWITCH** is not a kit arm: `SwirlPays`, an MSBuild
property defaulted on in `Directory.Build.props`, moves the shared
`KleeMod.Elements.TriggerRules.SwirlPays`
(`review/ruled/element-home-review-2026-09-28.md` §4 A). The sim twin
`C.SWIRL_PAYS` defaults `True` to match; `tools/lint_constant_parity.py`
compares the defaults, and `tier0/tests/test_element_port.py` and
`KleeTests/ElementPortTests.cs` pin both settings. Every reaction consumes
its aura.

```sh
dotnet build klee-mod/KleeCode -p:SwirlPays=false
```

**VARKA.** Rows `proto_vk_`, owner `varka`; C# `Powers/Prototype/VarkaOath.cs`,
sim `tier0/engine/varka_oath.py`. His cards speak one verb,
`{op: varka, kind: ...}`, each kind one `VarkaCards.<Kind>` call; numbers are
the card's `Vk*` vars, moved by upgrade keys `varka_per` / `varka_base` /
`varka_amount`.

**YAE MIKO**, Varka's arrangement. Rows `proto_ym_`, owner `yae`; C#
`Powers/Prototype/YaeShrine.cs` (the Sakura ledger, strikes, Tenko,
`YaeCards`), `YaeAnnotations.cs` (the five Annotations, Edit, Publish, the
per-card draft as a BaseLib saved field) and `YaePowers.cs`; sim
`tier0/engine/yae_shrine.py`; parity `tier0/tests/test_yae_parity.py`. Verb
`{op: yae, kind: ...}`, `Ym*` vars, upgrade keys `yae_per` / `yae_base` /
`yae_amount`. `kind: rite` names its Rite (`rite:` thunder / warding /
wildfire / offering, C# `YaeRite`); `kind: edit_sakura` names its end
(`which:` newest / oldest / every, C# `YaeSakuraEnd`) and a Sakura reading
(red_ink, fox_fire, deadline). Meditations of a Yako adds a Publish row to the
reward screen after an elite or boss fight
(`Relics/MeditationsOfAYako.cs`, `YaePublishReward`).

**KOKOMI'S PLAN.** The **Bake-Kurage** is a pet enemies cannot target
(`Powers/Prototype/BakeKuragePet.cs`). A card with a Plan line is played ON
it, and at the start of her next turn it carries the line out
(`Powers/Prototype/KokomiPlan.cs`; sim `tier0/engine/kokomi_plan.py`). A
row's Plan line is a top-level `plan:` list in the `effects:` vocabulary with
targets `front_enemy` / `all_enemies` / `self`; codegen emits typed
`KokomiPlan.Planned` records and decides the row's TargetType.

**THE COMPANION ROSTER** is Mondstadt's (`proto_mc_`,
`C.MONDSTADT_OVERHAUL_POOL_IDS`), Inazuma's (`proto_mi_`,
`C.INAZUMA_OVERHAUL_POOL_IDS`) and Fontaine's (`proto_mf_`,
`C.FONTAINE_OVERHAUL_POOL_IDS`). The seam is one property in each engine,
`CompanionPool.All` and `loader.companion_roster_replacement`, because the
reward slot and the shop must never read different rosters. There is no
Featured Banner: every companion in the pool is offerable in every run.
Per-row reasoning: `docs/notes/prototype-surface-provenance.md`.

**POOL WIRING.** Each character's pool lists its `proto_` rows in
`GenerateAllCards` and offers its roster (`*Roster.OfferablePool`,
`FurinaStageRoster.Pool`, `VarkaRoster.Pool`). Shared companions are in no
character's pool: they are `CompanionCardPool`'s, a BaseLib shared pool with
the base Colorless frame and orb ([USER] 2026-10-18, legacy review pick 4).
The codegen routes a row there by what it is (`loader.is_shared_companion_row`:
a Companion row with no `personal_pool:` that no kit claims in
`C.KIT_OWN_COMPANION_IDS`), not by its `character:` field, which still reads
`klee` and still picks the emitting profile (art path, text). It answers
`IsColorless` true (Heirloom Hammer copies companions), sits under the
library's Colorless tab (`Patches/CompanionLibraryFilter.cs`), and a transform
offers only companions the player could be offered
(`Patches/CompanionTransformFilter.cs`). Counts are pinned by
`KleeTests/Prototype/PoolCountTests.cs`: 78 per kit. Also checked: the tier0
schema validators, the codegen, `lint_generated_structure` and
`lint_pool_membership`. Depth: `docs/current/atlas/klee-mod-cards.md` §7.
