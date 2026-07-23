# Roster card codegen

The mod now has one character-aware card generator. Klee remains the shipping
compatibility baseline; Furina is staged behind an explicit activation gate
until her runtime systems and character pool are complete.

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

Generated Furina classes use `autoAdd: false`. They are excluded from the
shipping assembly until a Furina character pool can give every active card
valid pool membership. They can still be compiler-checked with:

```text
dotnet build klee-mod/KleeCode/KleeCode.csproj \
  -p:EnableFurinaGenerated=true
```

## Current Furina coverage

`klee-mod/KleeCode/Cards/Furina/Generated/manifest.json` is the live coverage
ledger. The first tranche emits 16 of 76 cards: the cards whose complete
damage, Block, draw, debuff, Energy, aura, and existing Companion-replay
semantics are already implemented.

The other 60 remain blocked and grouped by runtime cluster. The implementation
order is:

1. Encore and Fanfare resource lifecycle, costs, spend timing, predicates, and
   meter UI.
2. Salon member slots, paid/dry ticks, final-bow replacement effects, and
   related powers.
3. Spotlight selector, character/category designation, numeric transforms,
   texture powers, and copy/replay hooks.
4. Guest Star generation and the selector token.
5. Furina healing conversion, Fanfare cap changes, and the hand-written kit
   Burst lifecycle.
6. Furina character, starting relic/deck randomization, full card pool, and
   removal of the shipping compile gate.

## Build paths

`klee-mod/Directory.Build.props` discovers the game data directory beneath a
machine-local `GameDir` for Windows x86_64, macOS arm64, or macOS x86_64.
`GameDataDir` can be set explicitly for unusual layouts. `BaseLibDll` remains
an explicit machine-local path because the Workshop location is not reliably
derivable from the game install.

The Windows deployment script stages Klee, Furina, and Companion card-art
directories into the roster mod's flat `images/cards` package.
