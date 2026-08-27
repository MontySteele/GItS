# S12 — joined read: what public StS2 mods prove, and what they don't

> **Decides nothing.** This joins the seven S12 subsystem files and S13's engine
> probe. It selects, dedupes and orders; it does not restate any claim more
> strongly than its source did. No design, no mapping, no scope, no ids, no
> recommendations. Written 2026-08-26 by the S12 integrator. **S13 has landed**
> (`review/dispatch3/s13-engine-sockets.md`) and is joined below.

**Read this first, in one sentence:** the charter's suspicion was right — Downfall
answers relics, potions, packaging and localization end to end and answers almost
nothing else, and every other subsystem's proof came from widening to **BaseLib**
(the library we already depend on) and to two or three small mods nobody had opened.

---

## 1. Per-subsystem verdict, with the single strongest citation

| # | Subsystem | Verdict | Strongest single citation | The one line that matters |
|---|---|---|---|---|
| a | Enemy registration, AI, intents | **PROVEN — not by Downfall** | `BaseLib@2275793:Monsters/MoveBuilder.cs:16-304` — actions and their matching intents are built in lockstep into `new MoveState(Id, actions, intents)` | Downfall ships **zero** hostile enemies: all 24 of its `CustomMonsterModel` classes are player-owned pets, and all 3 of its move-machine overrides are the same `NOTHING_MOVE` self-loop. |
| b | Boss and encounter integration | **PROVEN** | `Act4@05c251a:src/Act4Placeholder/Architect/Act4ArchitectRevivalPower.cs:39-42` — "phases" are one hidden `PowerModel` answering `ShouldStopCombatFromEnding()` | Registration is `BaseLib@2275793:Patches/Content/ContentPatches.cs:352-393` (postfix every act's `GenerateAllEncounters`). Downfall: 0 `EncounterModel` subclasses repo-wide. |
| c | Act and map hooks | **PARTIALLY PROVEN** — yes for acts, map generation and node behaviour; **NON-FINDING** for new node *kinds* | `BaseLib@2275793:Abstracts/CustomActModel.cs:158-161,193-203` — prefix `ActModel.CreateMap`; returning `null` falls through to vanilla | Four public mods add or rewrite maps. None mints a new `MapPointType`/`RoomType` value; all re-type existing nodes. |
| d | World-event runtime | **PROVEN (library) / NON-FINDING (released mod)** | `BaseLib@2275793:Abstracts/CustomEventModel.cs` — `abstract class CustomEventModel : EventModel, ICustomModel, ILocalizationProvider`, ctor auto-registers, `virtual ActModel[] Acts => []` (body read verbatim; line numbers uncaptured) | Downfall's 72 `*Code/Events/` files are **combat hooks**, not world events — exactly the false positive the charter warned about. It defines zero "?" events. |
| e | Relic and potion hooks | **PROVEN end to end** | `Downfall@32e6113:HermitCode/Core/Hermit.cs:69,71` — a one-line pool class plus one inherited `[Pool(typeof(HermitRelicPool))]` on an abstract base is the entire registration for 15 relics | Rarity is the **only** dial for pool, shop and reward eligibility. No pricing, no shop slot, no shop screen anywhere. |
| f | Save / version compatibility | **PARTIALLY PROVEN** | `PN-0.107.1` (MegaCrit's own patch notes, Steam gid `1835871199305790`): "The base game no longer deletes progress from mods that are removed or errored" — now corroborated from the engine at `S13 [STS2]Saves\SaveUtil.cs:21-113` | Mod content is keyed by a `ModelId` derived from the **C# class name**. A rename is a save break. No mod declares an explicit stable id anywhere. |
| g | Packaging / localization / distribution | **PROVEN end to end, n = 1** | `Downfall@32e6113:DownfallCode/Localization/BundledSubmodLocRegistry.cs:3-21` + `Patches/GetModdedLocTablesPatch.cs:8-22` — bundling many characters in one package costs a Harmony postfix, because only one `Mod` entry registers | Localization is a committed source tree with a supply chain (nine hosted translation projects, nightly bot commits), not a string table filled in at the end. |

**Counted across the seven files:** 217 cited pattern rows, 70 gotchas, 65 raw
transfer questions (57 after dedupe, §3), and 47 explicit NON-FINDINGS.

---

## 2. Reconciliations — where two S12 files disagreed, and what S13 settled

### 2.1 Inside S12 (resolved here, so the morning read does not carry a stale claim)

1. **S12a's non-finding "no *released* mod registers a hostile enemy" does not
   survive the join.** S12b opened `kphxgames/Act4FinalAscent@05c251a` — MIT, no
   BaseLib dependency at all — which ships a four-phase boss the player fights
   (`Act4ArchitectBoss : MonsterModel`, `…/Act4ArchitectBoss.cs:51`), its own
   `EncounterModel`, and mid-fight summons. S12a's own search boundary records
   that it never opened that repository. **Take S12b's answer.**
2. **BaseLib's licence.** S12b left it UNVERIFIED. S12d and S12f both read
   `LICENSE.txt` directly: **MIT**. Settled.
3. **The BaseLib pin, three agents, three confidence levels.** S12b says the
   encounter API is byte-identical at tag `v3.3.7` so "the pin is not a blocker";
   S12c says whether `CustomActModel` exists at 3.3.6 is UNVERIFIED; S12d says
   `CustomEventModel.cs` exists at `v3.3.7` **by filename only**. S13 then read
   the binary actually installed on this machine (§2.2 item 8) and found
   something none of them assumed. Do not treat the pin as closed.
4. **Downfall's shipped surface is smaller than its tree.** `Collector` and
   `Gremlins` are in the repository but excluded from the default build
   (`Downfall@32e6113:Downfall.csproj:18`) — flagged independently by S12d, S12e
   and S12g. That removes 24 of S12e's 107 relic classes and two of S12a's three
   pet-monster families from the shipped assembly. **A class in the tree is not
   shipped content.**
5. *Minor, unresolved, not load-bearing:* S12a's headline count of 24
   `CustomMonsterModel` classes and its named families (Torchhead, 6 Gremlins,
   16 Slimes) differ by one. Neither number carries any claim.

### 2.2 Where S13 **agrees** with S12 (engine confirms a mod-source reading)

1. **No `BossModel`.** A boss is an `EncounterModel` with `RoomType.Boss` listed
   in an act's `BossDiscoveryOrder` — `S13 §5.1.1`. Confirms S12b NF3.
2. **No declarative data format** for enemies, encounters, acts or events; content
   is C# classes and loc strings are the only externalized part — `S13 §5.1.2`.
   Confirms S12b NF4 and S12a.
3. **`MegaCrit.Sts2.Core.Hooks` is the combat/run callback bus, not world events**
   — `S13 §5.1.5`, which names it as exactly the charter §7 error. Confirms
   S12d's central finding.
4. **Pool injection by postfix on each act's `GenerateAllEncounters`, across base
   *and* modded acts** — `S13 S13-b2`, `[BL]Patches\Content\AddActContent.cs:444-451`.
   Confirms S12a and S12b.
5. **The class name is the save id** — `ModelDb::GetEntry` = `Slugify(type.Name)`,
   `S13 S13-f1`; BaseLib prefixes `ICustomModel` ids via `PrefixIdPatch`,
   `S13 S13-f2`. Confirms S12f's central finding, and matches this repo's own R69.
6. **The monster presentation seams are real and BaseLib already patches them** —
   `VisualsPath`, `CreateVisuals`, `GenerateAnimator`, the three SFX getters
   (`S13 S13-a4…a7`). Confirms S12a's reading of `CustomMonsterModel`.
7. **Encounter slots are `Marker2D` children read off the encounter scene** —
   `S13 S13-b4`. Confirms S12a/S12b.
8. **A missing loc line warns and falls back; it does not fail** —
   `S13 S13-g5`, `[STS2]Models\MonsterModel.cs:474-481`. Confirms S12d/S12g.

### 2.3 Where S13 **answers** something S12 marked UNVERIFIED or routed to it

| S12 open item | S13's answer |
|---|---|
| S12a NF3 — how a `MonsterModel` acquires its `ModelId` and enters `ModelDb` | `ModelDb::Init` reflects every `AbstractModel` subtype and instantiates one canonical each; `InitIds()` stamps ids afterwards; `Inject(Type)`/`Remove(Type)` are documented "should only be used in tests **and mods**" — `S13 §1.7`, `[STS2]Models\ModelDb.cs:389,404,418,429` |
| S12a gotcha 6 — the shipped creature scene (`Node2D` root, `IntentPos`) contradicts the BaseLib wiki (`Control` root, `IntentPosition`) | The **engine** hard-requires `%Visuals`, `%Bounds`, `%IntentPos`, `%CenterPos` — `S13 §4.3`, `[STS2]Nodes\Combat\NCreatureVisuals.cs:219-223`. The shipped spelling is right and the wiki page is wrong. The **root type** is still unstated. |
| S12f NON-FINDING — nothing public says what happens to modded *cards/relics* when the mod goes away | `SaveUtil.XOrDeprecated` × 11 turns an unresolvable id into a `Deprecated*` tombstone model rather than corrupting the save — `S13 §1.7`, `[STS2]Saves\SaveUtil.cs:21-113`. S13 calls this "the entire modded-content-removal story". |
| S12e Q8 — is there a shop-pricing seam at all, or is rarity the whole dial? | `RelicModel::MerchantCost` (by rarity) and `IsAllowedInShops` are both **`virtual`** on the model — `S13 S13-e2`, `[STS2]Models\RelicModel.cs:205,305`. A seam exists; no mod uses it. |
| S12d Q8 — what act types does v0.107.1 actually expose? | Four live acts plus a tombstone: `Overgrowth` (Index 0, default), `Underdocks`, `Hive`, `Glory`, `DeprecatedAct` — `S13 §1.3`. |
| S12b NF5 — where does the engine consume encounter `Tags`? | `EncounterTag` + `EncounterModel::SharesTagsWith` exist (`S13 §1.2`, `[STS2]Models\EncounterModel.cs:280`). The member is found; the **selection path that consumes it is not traced**. |
| S12f NF1 — "no save-schema version number anywhere" | **Narrowed.** The base game has `ISaveSchema.schema_version` plus a `MigrationManager`/`MigrationRegistry`/`MigrationAttribute` registry across seven save families (`S13 §1.7`). What stays true is the mod-side half: S13 found nothing letting a mod register its own migration (`S13 §5.1.3`). |
| Three files' version-skew flag | S13 read the **installed** Workshop folder `2868840/3737335127`: its `BaseLib.json` says `"version": "v3.4.5"` (`BaseLib.dll` MD5 `4380fd038fda7ca92708fd09a8aebf39`) — against our manifest floor `≥3.3.6` and STATE.md's recorded `3.3.7.0`. See §5 item 2. |

**One S13 finding no S12 file could have reached, flagged because it changes the
shape of the art question:** BaseLib's `NCreatureVisualsFactory` will build a
complete `NCreatureVisuals` **from a bare `Texture2D`**, generating the missing
required children with defaults and warning rather than throwing for the one it
cannot invent (`S13 §4.5`, `[BL]Utils\NodeFactories\NCreatureVisualsFactory.cs:25-88`).
A monster whose body is an ordinary `Node2D`/`Sprite2D` — no Spine — is a fully
supported engine state (`S13 §4.4`); it loses animation, the death clip and
skeleton-accurate fade bounds, and keeps everything else. S13 states plainly that
whether that trade is acceptable is a taste call and [USER]'s.

### 2.4 Where S13 is **silent** (still open after the join)

- `MapPointType` / `RoomType` **membership** — so S12c's flag on `(MapPointType)7`
  and `(MapPointType)8` in `Act4FinalAscent` stays UNVERIFIED. S13 names the types
  but does not enumerate them.
- Whether **`RelicRarity.Boss`** exists — S12e routed this to S13 explicitly and
  S13 does not enumerate the enum.
- Whether `MegaCrit.Sts2.Core.Hooks.Hook` has a **supported listener registration**
  rather than a method to Harmony-patch (S12c Q4).
- The **per-key language fallback** rule (S12g N1). S13 covers a missing loc *key*,
  not a missing *language*.
- Whether any **released mod consumes** `CustomEventModel` / `CustomEncounterModel`
  — out of S13's lane, and GitHub code search was auth-walled for every agent.
- **Multiplayer.** S13 left `[STS2]Multiplayer\` unread; no S12 agent observed two
  clients agree about anything.
- BaseLib's **reward and shop patches** (`CustomRewardPatches.cs`,
  `RewardSynchronizerPatches.cs`) and `ActModelGenerateRoomsPatch.cs` were read at
  **file level only** (`S13 §5.2`) — which is precisely S12b Q7, S12e Q7 and
  S12c's "node mutation inside a base act" row.

---

## 3. Transfer questions — deduped and numbered

65 raw questions across seven files → **57 after dedupe**. Every one is a question
about something we would have to learn or decide. None is a proposal.

### A. Dependency pin and game version

| # | Question | Raised by |
|---|---|---|
| 1 | What is our **true BaseLib floor**, and who signs off raising it? Four numbers are in play: manifest `≥3.3.6`, STATE.md `3.3.7.0`, the installed Workshop manifest `v3.4.5` (S13), and Downfall's `3.4.5`. Every pattern in these seven files was read at 3.4.5. | a1, c2, e, f, g10 |
| 2 | Is a dll inside a **Steam Workshop content folder** — which Steam updates underneath us — a reproducible dependency at all? What would we have to decide to get one? | d1 |
| 3 | For a named API (`CustomEncounterModel`, `CustomActModel`, `CustomEventModel`, `CustomRestSiteOption`, `TryModifyRestSiteOptions`), what do we run **against the installed binary** to prove it is there? Source at a tag is not the dll we link. | b1, c2, d2 |
| 4 | Do we have a **game-version compatibility posture** beyond one hand-written canary? Public mods carry reflection shims, runtime feature detection, or one DLL per game version. | f5 |

### B. Two engines — sim vs mod

| # | Question | Raised by |
|---|---|---|
| 5 | Which **act identity** would a Teyvat encounter key from — the game's `ActModel`, or our sim's `RUN_ACTS`? Does anything reconcile the two? | a2 |
| 6 | Can our sim's six frozen **encounter ids** and the mod's `EncounterModel.Id.Entry` be made to line up, or are they deliberately separate id spaces? | b2 |
| 7 | Our sim declares a 16-floor map with fixed treasure/rest/boss floors; the C# side generates a grid. Are they supposed to agree, and would a map-side change move `RUNTEMPLATE_VERSION`? (A **stamp** question, not an engineering one.) | c3 |
| 8 | `tier05/events.py` already interprets a full event grammar and the mod has **no events at all**. If events ever ship mod-side, which layer is the source of truth, and does the constant-parity gate extend to event bodies? | d4 |
| 9 | Are BaseLib's `Acts` and our `also_acts` the same idea, and what is the base rule about events already seen in a run, before our "Unknown resolves to an event 55% of the time" is comparable to the game's? | d5 |

### C. Save, identity, removal

| # | Question | Raised by |
|---|---|---|
| 10 | Which of our per-run quantities must **survive a save and reload** — Spark, Charge, Burst meter, Fanfare cap, Salon membership, Companion slots, Artifact/Aura/Bomb state — and which are combat-scoped by design? We persist nothing of our own today. | f1 |
| 11 | What is our answer to a **class rename**, given the class name *is* the save id? Downfall's answer is never rename, retire in place as `[Obsolete]`. Does that become a lint against the YAML sheets rather than a convention? | f2 |
| 12 | If we ever register a `SavedSpireField`, what is our **key convention**, and can `tools/` lint it? Nothing enforces a prefix and Downfall's live keys carry none. | f3 |
| 13 | What do we owe a player who **removes our mod mid-run**? The engine tombstones unresolvable ids (S13), but nothing public covers our off-pool cards, relics, or companion cards sitting in a base character's deck. | f4, d9 |
| 14 | Which of our cards have per-instance state that must persist (`[SavedProperty]`-shaped), and does `AssertMutable()` interact with how codegen builds canonical instances? | f8 |
| 15 | Is `SaveManager.SaveRun` a seam we would ever want (capture, Understudy harness), and does touching it collide with a player's save-manager mod? | f6 |
| 16 | Should the playtest protocol record whether a **save-unifying mod** is installed, since it changes which directory the run came from? | f9 |
| 17 | Would any act / map / event change of ours have to be **save-compatible with a run already in progress**, and is that a LAW-level answer? | c7, d9 |
| 18 | Does our identifier registry already cover **encounter and monster ids**, or is that an unallocated namespace? | a10 |

### D. Co-op

| # | Question | Raised by |
|---|---|---|
| 19 | Who owns the **seat-count scaling rule** for enemy numbers, and can it be tested at all before play? `MoveBuilder.HealSelf` scales by `Players.Count` by default, and `ScaleMonsterHpForMultiplayer` runs inside `CreateCreature` *before* any entry hook. | a9, b4 |
| 20 | Extended saves are written **positionally, in sorted-ID order**, over the packet path. Two seats on different builds of our mod would misread the stream. Does that argue for registering the full set at once rather than growing it per window? | f7 |
| 21 | What would we need before we could claim any map / event / enemy change is **co-op-safe** — is there a test seam short of two live seats? | c5, d6 |

### E. Testability

| # | Question | Raised by |
|---|---|---|
| 22 | What could actually be asserted **headlessly** about an encounter or boss lifecycle — registration, id stability, pool predicate — versus what is necessarily play-only or Understudy-only? `KleeTests` cannot construct a live `CombatState`. | b5 |

### F. Registration route

| # | Question | Raised by |
|---|---|---|
| 23 | If we ever wanted a map-side behaviour, which of the **three proven routes** — BaseLib `CustomActModel`/`CustomCreateMap`, `Hook.ModifyGeneratedMap`, or a `StandardActMap` ctor postfix — and who decides? They are not interchangeable. | c1 |
| 24 | **Library or no library.** `Act4FinalAscent` proves an encounter and a four-phase boss with raw Harmony and zero library dependency. What do we need to know about the trade — version exposure vs. patch maintenance — before that can even be put to [USER]? | b6 |
| 25 | Is there a **supported listener registration** for `MegaCrit.Sts2.Core.Hooks.Hook`, or is patching the hook method itself the only route? Both public mods patch the method. *(S13 silent.)* | c4 |
| 26 | How stable is **per-act-type patching** across game updates? BaseLib patches only acts that *declare* `GenerateAllEncounters`; an act that inherits it is never patched. | d8, b |
| 27 | Do we adopt **`[Pool]`-attribute registration** or keep hand-enumerated pools? `KleeRelicPool` enumerates by hand and therefore bypasses `CustomRelicPoolModel` entirely (no `IsShared`, no `SeenByDefault`). Does `KleeSelfCheck` R7 still hold under the attribute route? | e1 |
| 28 | What does **`autoAdd: false`** actually leave registered? `PoundingSurprise` asserts one thing while also being hand-appended to the pool — which is doing the work, and is one redundant? | e2 |
| 29 | Do we already have a run-scoped `CustomSingletonModel(HookType.Run)`, or would adopting one be new BaseLib surface we do not currently use? | c6 |
| 30 | Adopting a **new model kind** (`CustomEventModel`) introduces something our codegen, manifests and coverage ledgers have never carried. What does that do to `gen_roster_cards`-shaped tooling and to the manifest coverage figures STATE.md quotes? | d3 |

### G. Content-shape unknowns

| # | Question | Raised by |
|---|---|---|
| 31 | Would a Teyvat enemy be a **new `CustomMonsterModel`** (new type, new `ModelId`, new save identity) or a **presentation swap** on an existing base monster? Those differ sharply in save and version consequence. | a3 |
| 32 | Is `CustomPetModel` — proven, no AI, no encounter, no act — a **different question from enemy remapping entirely**, for a Klee bomb, a Salon member, or a Kokomi ally on the board? | a8 |
| 33 | Does an enemy we author need to carry **auras**, and what does an aura-bearing hostile creature do to the Swirl aura-aware bind (R211)? | a5 |
| 34 | What does **`PlayTelemetry`** owe an enemy we control? It already walks `move.Intents` and regex-parses the rendered label — would it double-count or mis-parse a label we wrote ourselves? | a4, b3 |
| 35 | **Is `RelicRarity.Boss` real?** `KleeRelicPool`'s header says relic rewards roll "…Shop/Boss"; Downfall uses Starter/Common/Uncommon/Rare/Shop/Ancient/Event and never Boss. Does our reward-safety argument survive the answer? *(S13 silent.)* | e3 |
| 36 | **Potions:** do we want any, and whose pool? All three characters currently point at the vanilla `SilentPotionPool`. Does owning a pool remove the Silent potions we currently inherit? | e4 |
| 37 | Which of the 30+ relic **trigger names** does our surface actually need, and does anything we want require the `PlayerChoiceContext` wrapper that `HookedRelicModel` exists to provide? | e6 |
| 38 | Does the **companion-reward slot** want a `CustomReward` (a first-class reward row at the cost of a hand-written co-op sync protocol and a save serializer), and who pays the multiplayer test bill? | e7, b7 |
| 39 | **Shop:** is rarity the whole dial for us too, or would a priced-out / discounted item use `MerchantCost` (which S13 found is `virtual`)? | e8 |
| 40 | Do we owe a **base-relic compatibility sweep** — which vanilla relics make assumptions our aura/bomb/artifact machinery breaks, and is that a lint, a test, or play-only? | e9 |
| 41 | Where would an enemy or boss **live** — a new `EncounterModel` inside an existing act's pool, or a new act with its own `BossDiscoveryOrder`? S12b reads that as a design direction; does it belong on QUEUE rather than in research? | b8 |

### H. Localization

| # | Question | Raised by |
|---|---|---|
| 42 | **Where should our English strings live?** Today they are three surfaces: a C# dictionary merged at boot, a PowerShell here-string in `build_pck.ps1`, and the ruled selection prompts. Which can even become a file, given the code-side copy exists deliberately so a code-only rebuild never renders raw keys? | g1, e5 |
| 43 | Is anything about our loc layout **incompatible with a multi-language tree**, or is it only that `eng` is the sole folder? | g2 |
| 44 | Do we want any **language but English** before a public build, and is owning an account on a hosted translation platform something [USER] will own? Downfall's answer costs nine platform projects, an API secret, a deploy key and a nightly bot pushing to `main`. | g3 |
| 45 | What is the **fallback when a key is missing in the player's language**, and do strings injected at runtime by `MergeWith` participate in it the same way file strings do? *(S13 silent.)* | g4 |
| 46 | Where would our **intent and monster strings** live, and does `InjectLocStrings` reach those tables today? | a6 |
| 47 | What would a lint of ours have to assert so a **renamed handler cannot ship an untranslated option**? BaseLib derives option keys from method names and only warns when the row is missing. | d7 |
| 48 | Would a **compile-time missing-localization analyzer** catch anything our manifests do not — and would it be a gate or a report (R204 makes that distinction load-bearing)? | g11 |

### I. Art, PCK, packaging, distribution

| # | Question | Raised by |
|---|---|---|
| 49 | What does an **encounter add to package size and build time** — a 1920×1080 scene with `Marker2D` slots, optional layered backgrounds, two boss run-history icons — and does `roster-pck-v3` have to move? | a7 |
| 50 | Do our **relic/potion art sizes** match theirs, and is a silent `todo` placeholder acceptable to us or exactly the thing `art_lint` should bite? | e10 |
| 51 | Is our **PCK packing** doing the same thing theirs is — they pack the imported `.ctex` from each `.import` remap and skip the raw image; we drive the MegaDot editor. | g12 |
| 52 | Do we ever want a **per-character build switch**, and what would break — ship order, generated manifests, save identity, co-op version matching? | g5 |
| 53 | Do we want an **"in the tree, not in the build" lane** for a written-but-unreleased character, and would that read as a coverage hole or as a gate? | g6 |
| 54 | Which **version number** does a public manifest carry? Ours is MAJOR-AUTO so two co-op seats can see who is behind; Downfall's is semver from a tag. Do we need both, and which one goes in `manifest.json`? | g7 |
| 55 | Do we want **CI**, of which shape, and does any of it work without `gh` on this machine? | g8 |
| 56 | Is a **Steam Workshop item** something [USER] intends to own? Credentials and a TOTP secret in CI is a one-way door, not an engineering choice. | g9 |
| 57 | What is a **non-developer player told to install**, and what changed between the BaseLib versions in play? | g10 |

---

## 4. Union of search boundaries

**Date: 2026-08-26** for every retrieval in all seven files. Runner: local Windows,
read-only. No agent ran a git command, wrote outside its one assigned file, or
touched the primary checkout. **Nothing was launched, deployed, built, compiled or
observed at runtime anywhere in S12.**

**Primary source, all seven agents:** `lamali292/Downfall` @
`32e61132052ae58e32cd33342d24136ffe18be12` — depth-1 read-only clone in the
scratchpad, 5,209 tracked files / 1,858 C# files. MIT (`LICENSE`, read directly).

**Widened once each, per charter §7** — six of seven agents. S12g did not need to
widen: Downfall implements its subsystem end to end.

| Repository / source | Pin | Licence | Opened by |
|---|---|---|---|
| `Alchyr/BaseLib-StS2` | `22757933…` (= tag `v3.4.5`), plus tag `v3.3.7` = `f7db6b5…` | MIT (read) | a, b, c, d, e, f |
| `Alchyr/BaseLib-Wiki` (source of the docs site) | `5558d898…` | — | a, f |
| `alchyr.github.io/BaseLib-Wiki` (rendered pages) | retrieval-dated only, no commit URL | — | e |
| `kphxgames/Act4FinalAscent` | `05c251a…` | MIT | b, c |
| `leddele/act-4-Template` | `13abfb25…` | **no LICENSE file** | c |
| `ing-gom/sts2-random-map` | `f9266eb…` | MIT | c |
| `ing-gom/sts2-concept-map` | `c0072b39…` | MIT | c |
| `spencerqfox/sts2-custom-mods` | `5a39417…` | MIT | c |
| `BAKAOLC/STS2-RitsuLib` | `a7c809b6…` | MIT | a (NON-FINDING) |
| `Alchyr/ModTemplate-StS2` | `master`, README only — **unpinned**, API rate limit | — | a |
| `fresh-milkshake/Modding-Tutorial` ch.13 | `dea5acc…` | documentation, not a shipped mod | d |
| `JaydenLiang/slay-the-spire-2-mods` | `b2cae7b…` | MIT | f |
| `luojiesi/SLS2Mods` | `3de9d08…` | **no LICENSE** | f |
| `nyaoouo/sts-2-saves` | `2c58c2f…` | **no LICENSE** | f |
| `megacrit/sts2-mod-uploader` | `d7b7e6b…` | — | f |
| StS2 patch notes, 6 announcements | Valve `ISteamNews`, appid `2868840`, pinned by Steam `gid` | MegaCrit's own publication | f |
| `nuget.org` pages: `Alchyr.Sts2.ModAnalyzers 0.1.9`, `Alchyr.Sts2.BaseLib 3.4.5` | retrieval-dated, not commit-pinned | publisher pages | g |

**Named in search results and deliberately NOT opened** (recorded so the next pass
does not re-search them): `jiegec/STS2FirstMod`, `jiegec/STS2RouteSuggest`,
`lamali292/sts2_example_mod`, `lamali292/WatcherMod`, `visist16/BaseLib-StS2`,
`freude916/sts2-quickRestart`, `bwbear0412/slay_the_spire_2`,
`1r1di0us/OuterSteppes`, `FullLifeGames/SlayTheSpire2RandomizerMapMod`,
`Kziz3988/ActsFromThePastMultiplayerBalance`, `leddele/slay-the-spire-2-more-bosses`,
`ing-gom/sts2-blind-map`, `ing-gom/sts2-map-legend-count`, `daviscook477/BaseMod`
(StS1), the `sts2` / `sts2-mods` GitHub topic listings, Nexus *BetterSaves*
(`mods/372`) and *More Saves* (`mods/225`), and every Steam Workshop listing page.

**Shared limits of the whole widen:**

- **GitHub code search is behind an auth wall for this runner**, so no agent could
  enumerate mods that *consume* a given BaseLib API. "No released consumer found"
  is a limit of the search, not a proof of absence.
- The GitHub REST core API rate-limited two agents (a, c) partway; both fell back
  to `raw.githubusercontent.com` and source tarballs extracted to scratch.
- `nexusmods.com` returned HTTP 403 to fetch.
- The Downfall clone is depth-1, so **no commit message is available as evidence**.
- **No wiki, forum, Nexus page, Steam page, video or search-result summary was used
  as evidence by any agent.** Searches were used only to find URLs.
- One search-result summary claimed `ModTemplate-StS2` "shows folder structure for
  custom monsters and encounters". That is a filename claim about a repo nobody
  opened. It is recorded as a **lead, not evidence**.

---

## 5. What this joined read does NOT establish

1. **Nothing was run.** No game launched, no PCK built, no DLL compiled, no mod
   installed, no playtest touched — across all seven S12 files and S13. Every claim
   is source-reading.
2. **Not that any pattern works on our stack.** Everything in S12 was read at
   BaseLib **3.4.5**; our manifest floor is `≥3.3.6`, STATE.md records `3.3.7.0`,
   and S13's read of the installed Workshop folder says `v3.4.5`. Three numbers,
   unreconciled. Nothing here says which is right.
3. **Not base-engine truth from S12.** Where an S12 file says "the engine does X",
   the evidence is a mod's source comment or its observable workaround. S13 read
   the decompile and **S13 wins** on every such point.
4. **Not that Downfall's shipped behaviour matches its source**, and not that a
   class in its tree is shipped content (`Collector` and `Gremlins` are excluded
   from the default build).
5. **Not a completeness claim about `Act4FinalAscent`'s boss** — roughly 200 KB of
   it (state machine, mechanics, presentation, save patches) was not read. The
   lifecycle *seams* are cited; the behaviour hanging off them is not.
6. **Not co-op verified anywhere.** The map mods *claim* seed determinism; nobody
   observed two clients agree. S13 left `[STS2]Multiplayer\` unread.
7. **Not a rights or reuse finding.** Licences are recorded as facts: MIT where
   read; `act-4-Template` and two save mods ship none. Downfall's MIT covers
   Downfall's own code — **not** the base-game assets its build junctions in, its
   art, its audio banks, or its translations. Reference-reading only throughout
   (charter §3.7): no code, scene, art, audio or text was copied into anything.
8. **`n = 1` on packaging.** S12g is one mod by one author who also publishes the
   surrounding tooling and works alongside BaseLib's author. Its conventions may be
   house style rather than platform norms.
9. **No estimate.** No effort figures, no ordering, no batch, no ids minted, no
   BACKLOG or QUEUE row, no dormant row touched.
10. **No measurement.** No stamp moved, no window opened, no experiment run, no
    playtest interpreted.
11. **No design, mapping, taste, scope, money or ship verdict.** Nothing here says
    Teyvat Spire should have an enemy, a boss, an act, an event, a potion, a
    translation, CI, or a Workshop item. All 57 questions in §3 are questions.

### Still UNVERIFIED after the join (16 items)

`MapPointType`/`RoomType` membership · whether `RelicRarity.Boss` exists · whether
`Hook` has a supported listener registration · the per-key language fallback rule ·
whether `[CustomEnum]` values are stable across mod sets despite being persisted ·
whether an empty custom potion pool falls back to vanilla · whether relic/potion
image paths need a `res://` prefix · how an act at a *contested* `Index` is chosen
over the base act · whether any released mod uses the event or encounter API · the
BaseLib pin (four numbers) · the creature-visuals scene **root** type · ~200 KB of
`Act4FinalAscent`'s boss · BaseLib's reward/shop patches (file-level only) ·
`ActModelGenerateRoomsPatch` body · `NodeFactory::ConvertScene` body · the whole of
`[STS2]Multiplayer\`.
