# Roster card codegen

The mod has one character-aware card generator. Klee remains the compatibility
baseline and Furina is active as the second playable character.

## Commands

Generate every configured character:

```text
.venv/bin/python tools/gen_roster_cards.py
```

Check committed output without writing:

```text
.venv/bin/python tools/gen_roster_cards.py --check
```

The historical `tools/gen_klee_cards.py` entry point still defaults to Klee.
It also accepts `--character klee`, `--character furina`, or
`--character all`.

## Character profiles

Each profile declares:

- canonical card sheet;
- output directory and manifest;
- C# namespace;
- native element and elemental-application cadence;
- art loader;
- whether generated cards carry playable-character identity.

Furina uses Skill-grade Hydro cadence: a damaging Skill, `skill_tag` card, or
`burst_tag` card applies Hydro. A plain Attack does not. Non-damaging Skills
do not become elemental cards.

`ICharacterCard.CharacterId` is the stable ownership seam for mechanics such
as Spotlight. Companion cards continue to use `ICompanionCard`; the guest's
identity is not the playable character's identity.

## Honesty rules

The generator rejects unknown card-level fields as well as unknown effects.
This is load-bearing: `encore_cost` or `fanfare_cost` changes playability even
though it is not an effect, so ignoring it would produce a compilable but
incorrect card.

Partial upgrades are forbidden. A card either receives its complete ruled
upgrade from the authoritative upgrade sheet or appears under
`upgrades.no_upgrade_path` in its manifest.

Generated Furina classes use `autoAdd: false`; `FurinaCardPool` owns their
membership. `FurinaCardRoster` is generated from the personal sheet, while
Guest Stars, the selector tokens, and the hand-written kit Burst are pool
members filtered out of rewards.

## Current Furina coverage

`klee-mod/KleeCode/Cards/Furina/Generated/manifest.json` is the live coverage
ledger. It emits 75 of 76 personal cards plus all three Neuvillette Guest
Stars. The sole blocked row is `let_the_people_rejoice`, intentionally
hand-written because its full-meter grant/spend lifecycle is kit machinery.

The active runtime includes Encore/Fanfare/Burst resources and meters, Salon
slots and replacement bows, Spotlight selection and numeric transforms,
Guest Star generation, healing, Fanfare-cap changes, the kit Burst, Furina's
starting relic/deck, and deterministic Fontaine starter substitutions.

## Build paths

`klee-mod/Directory.Build.props` discovers the game data directory beneath a
machine-local `GameDir` for Windows x86_64, macOS arm64, or macOS x86_64.
`GameDataDir` can be set explicitly for unusual layouts. `BaseLibDll` remains
an explicit machine-local path because the Workshop location is not reliably
derivable from the game install.

The Windows deployment script stages Klee, Furina, and Companion card-art
directories into the roster mod's flat `images/cards` package.

`tools/build_pck.ps1` builds one character-aware resource pack. Klee keeps its
historical `ImageGen/images/{ui,powers,relics,model}` inputs; Furina reads
`ImageGen/images/furina/{ui,powers,relics,model}`. Until the Furina art pass
fills those directories, the builder copies missing required UI/model files
from Klee into the `res://furina/` namespace. The namespace is still distinct:
combat visuals, icon, rest, merchant, character-select background, and
transition material all have Furina-owned scene paths.

Every `CustomCharacterModel` must override the four otherwise id-derived run
preload paths: `CustomVisualPath`, `CustomIconPath`,
`CustomEnergyCounterPath`, and `CustomTrailPath`. Rest and merchant conversion
paths must also remain distinct. Validation gate S6c checks the source
contract, and runtime self-check R9 verifies that every evaluated character
asset path resolves after the PCK merges.

The PCK builder emits `klee.pck.contract.txt` with a contract version, resource
inventory, and SHA-256. Deployment stages it with the pack and rejects a
missing, stale, or mismatched contract. After pulling a roster-resource change,
run `tools\build_pck.ps1` before `klee-mod\build\deploy.ps1`; an old Klee-only
PCK cannot pass validation.

Deployment validation treats `game_ref/` as an optional, atomic local
reference. When all required Ironclad layers exist, it runs
`tools.build_ironclad_sheet --verify` and includes those tests. When the
directory is absent or incomplete, it runs pytest with
`GITS_REFERENCE_MODE=committed-only`: every repository-owned test still runs,
while the local-reference modules skip exactly as on a fresh clone. Normal
simulation loading remains fail-closed for partial references.
