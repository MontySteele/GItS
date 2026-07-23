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
