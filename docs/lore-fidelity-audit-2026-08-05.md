# Lore-fidelity audit — 2026-08-05

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Track N of the House Lights swarm batch. **Findings only.** This document
inventories and adjudicates; it proposes nothing and it rewrites nothing. No
card text, sheet, string or gallery line was touched by this pass — an audit
that edits is a failed audit. The only file this pass adds is this one.

[USER] is the calibration authority. Every verdict below is a reading offered
for his red pen, not a decision taken. Nothing here is ratified, and no row
below should be read as though it had been.

Six surfaces were swept concurrently: N1 Klee, N2 Furina (+ the register
grammar), N3 Kokomi (+ her two character laws), N4 companions (all nations,
including the Fontaine Rares drafts), N5 shipped strings in the mod tree, and
N6 a spot re-verification of the already-verified galleries.

## What "canon" means here

This repo uses the word *canon* in two unrelated senses, and this audit means
only the second:

- **StS2 canon** — the base game's own five card pools, as in
  `docs/role-tempo-baseline.md` and `docs/role-tempo-floors.yaml`. Not audited
  here.
- **Genshin canon** — assertions about Genshin Impact's characters, places,
  institutions, items and terminology. **This is the subject of the audit.**

## The three verdicts

Every claim gets exactly one, and every one carries a citation:

- **VERIFIED** — corroborated against a canon source, cited.
- **CONTRADICTED** — a canon source says otherwise, cited.
- **UNVERIFIABLE** — could not be confirmed from a reachable source. The
  citation records what was searched. **UNVERIFIABLE is not a defect finding**;
  it is a statement about the evidence, not about the text.

There are **zero should-be findings** in this document by construction. Where a
claim could not be cited it is UNVERIFIABLE, never "wrong"; where a house law's
wording was too vague to adjudicate a case, the case is recorded as
UNVERIFIABLE-against-law rather than as a violation. Taste is not a verdict.

**Load-bearing** means the claim anchors a card identity, a register or
character law, or a shipped player-facing string. Everything else is
**cosmetic** decorative flavor. Severity ordering throughout:
CONTRADICTED-and-load-bearing, then CONTRADICTED-cosmetic, then
UNVERIFIABLE-load-bearing, then the rest.

## Standard being applied

S8's drafting pass caught seven fabricated canon claims before they shipped.
That is the bar; this pass applies it retroactively to everything already
shipped. N6 exists to ask whether the bar held — and its answer is the first
item below.

---

# TOP 5

All five are CONTRADICTED-and-load-bearing. Ordered by severity.

**1. `Concealed Unguis` is the wrong creature and the wrong sea — and it
survived a verification pass.**
`review/potion-relic-gallery/gallery.md` justifies the shipped #1 pick for
`gorget` with a vishap-shaped rationale: *"the mid-tier common ascension
material from Bathysmal Vishaps (Concealed Claw / Concealed Unguis / Concealed
Talon), the vishap line of Enkanomiya and the waters around Watatsumi Island."*
genshin-db `materials/concealedunguis.json` reads *"Body tissue left behind by
one of the Riftwolves… hunting hounds of 'Alfisol'"*, source *"Dropped by
Lv. 40+ Riftwolves"* — The Chasm, Liyue. This is precisely the failure class
S8's own Rule 2 (CANON-FACT: wrong drop source = cut) was written to catch, and
it passed. Severity is not the single row; it is that the retroactive standard
found a live miss in the set that had already been cleared.

**2. `"Reaction preview: Overload"` — a shipped keyword tooltip names a
reaction that does not exist.**
`klee-mod/KleeCode/KleeMod.cs:141`, inside the `card_keywords` table that is the
load-bearing block of the whole string surface. The in-game reaction is
**"Overloaded"**. Source: https://game8.co/games/Genshin-Impact/archives/297558

**3. Charlotte's `"Enduring Frosthelm"` is presented as canon and is not.**
`docs/fontaine-companions.yaml:37,41` justifies the shipped card title with the
words *"Named for her actual passive."* The string appears nowhere in genshin-db
`talents/charlotte.json` or `constellations/charlotte.json`; her passives are
"Moment of Impact", "Diversified Investigation", "First-Person Shutter". This is
a fabricated canon claim carrying its own false attestation — the exact S8
pattern, shipped.

**4. Five shipped companion card titles name talents that do not exist.**
`"Barbara — Soothing Melody"`, `"Barbara — Shining Idol"`, `"Gorou — Inuzaka
Charge"`, `"Gorou — Heart of the Clan"`, `"Lynette — Box Trick"`. Canon:
Barbara's are "Let the Show Begin♪" / "Shining Miracle♪"; Gorou's Skill is
"Inuzaka **All-Round Defense**"; Lynette's burst summons a **Bogglecat Box**.
Sources: genshin-center.com/characters/{barbara,gorou,lynette}. Load-bearing as
shipped player-facing strings.

**5. The Guyun acquisition error is systemic, not incidental — three
occurrences under two mutually inconsistent phrasings.**
`review/potion-relic-gallery/gallery.md` at `anchor` #1, `whetstone` #2 and
`vajra` #2: *"Lustrous Stone from Guyun — … Liyue, Domain of Guyun in the Guyun
Stone Forest"*, and at L783 *"Domain of Forgery near Guyun Stone Forest"*, and
at L362 *"Grain of Aerosiderite … (Domain of Guyun, Liyue)"*. The material is
farmed in the Hidden Palace of Lianshan Formula, Jueyun Karst (Mon/Thu/Sun). No
"Domain of Guyun" is where any Guyun-line material is farmed, and the gallery
never registered its own disagreement with itself.

**Immediately below the line**, and flagged because each is arguably a
substitute for #5 depending on how [USER] weights self-inconsistency against
systemic repetition: `"Catalytic Conversion"`
(`Powers/ReactionKitPowers.cs:35`) versus Sucrose's canon **"Catalyst
Conversion"** — *the same build ships both spellings*, so two shipped strings
disagree with each other; Arlecchino's shipped `Nation` string asserting
**Fontaine** where canon says **Snezhnaya**, which is a declared house ruling
but is also the string that drives `SAME_NATION_REWARD_SHARE` and makes
Fontaine's Rare count 4; and two canon errors *the prior gallery pass itself
found* (Adeptus' Temptation's figures, Tricolor Dango's category) that are
**still standing in the shipped citation text**, recorded in a `[USER]` flag
rather than cut — so the gallery currently asserts as canon two facts the same
document elsewhere calls false.

---

# Rollup

Verdict counts by surface. Row counts and verdict counts differ where a ledger
groups several strings or cards under one row (notably N1 and N5); the
per-surface ledgers below are authoritative.

| Surface | VERIFIED | CONTRADICTED | UNVERIFIABLE | Other* | Rows |
|---|---|---|---|---|---|
| N1 — Klee pool + upgrades | 21 | 0 | 10 | 0 | 28 |
| N2 — Furina pool + upgrades (canon claims) | 24 | 2 | 5 | 2 | 33 |
| N3 — Kokomi pool + upgrades (canon claims) | 30 | 0 | 10 | 1 | 41 |
| N4 — Companion sheets, all nations | 55 | 3 | 15 | 1 | 74 |
| N5 — Shipped strings in the mod tree | 55 | 6 | 6 | 26 | 79 |
| N6 — Gallery survivors (34% sample) | 32 | 10 | 4 | 0 | 46 |
| **Total** | **217** | **21** | **50** | **30** | **301** |

\* *Other* = rows carrying no canon verdict: non-claims, out-of-surface rows,
recorded absences, N/A, and (N5) original coinages that assert nothing about
canon.

Law checks, which are mechanical rather than canon verdicts and are counted
separately:

| Law | Surface | Violations | Not adjudicable | Coverage gaps |
|---|---|---|---|---|
| Furina same-resource-same-register (R1–R7, L12, spelling) | N2b | **0** | 2 | 5 |
| Kokomi LAW A — Exhaust-as-rotation | N3b | **0** in shipped player-facing text | 3 | 10 departures, all in non-shipped comments |
| Kokomi LAW B — no self-damage | N3b | **0** | — | no lint, no test |

Of N6's 46 re-verified claims, **34 AGREE** with the prior recorded verdict and
**12 DIFFER** — 8 contradictions the prior pass did not catch, and 4 claims it
carried as verified that no reachable source could close.

## Sources blocked tonight

`genshin-impact.fandom.com` returned **HTTP 402 Payment Required** through the
proxy on every path, confirmed independently by all six surfaces; the same block
is already on the record at `docs/zhongli-dossier-2026-08-05.md:24-26`. Also
blocked: `gensh.honeyhunterworld.com` (403), `gi.yatta.moe` Project Amber avatar
archive (403), and `genshin-db/.../common/Element.json` (404, repo layout
changed).

The workaround that carried the audit was **genshin-db's raw English game-text
JSON** fetched directly — authoritative extracted game text, and the basis for
every numeric and first-party-string verdict in N4 and N6. Its documented limit:
the character records carry profile and ascension data but **no talent, passive,
constellation or voice-over text**, so every talent-name claim had to route
through secondary sources (game8, genshin-center, keqingmains, Fextralife,
progameguides, wiki.hoyolab). Fandom facts appear throughout as **WebSearch
result summaries**, never as fetched pages, and are cited as the underlying
source of the quoted text rather than as pages retrieved. One claim — Klee's
`Da-da-da!` voice line — could not be closed by any reachable source, because
every voice-over corpus sits behind one of the blocks above.

---

## N1 — Klee card pool + upgrades

**Scope audited:** `docs/klee-cards.yaml` (75 draftable cards), `docs/klee-upgrades.yaml`, `docs/klee-character-design.md`, `klee-mod/KleeCode/Cards/` (hand-written + `Generated/` C# card classes, i.e. every shipped `("title",…)` / `("description",…)` string), `klee-mod/KleeCode/Klee.cs`, `klee-mod/KleeCode/Relics/PoundingSurprise.cs`, `klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs`, `docs/reserved-card-names.txt`, `art/SOURCES.tsv`.

**Structural note recorded before the ledger:** the Klee pool ships **no flavor-text field**. Every shipped player-facing string is either a card *title* or a mechanical *description*. Canon claims therefore live almost entirely in **names** (card titles, relic titles, the character subtitle) and in **design-doc prose**, not in flavour prose. This shapes the verdict distribution below.

| Claim | Where (repo path) | Verdict | Load-bearing? | Source / citation |
|---|---|---|---|---|
| Klee is "The Spark Knight of Mondstadt" (character subtitle + class comment) | `klee-mod/KleeCode/Klee.cs:21,57` | VERIFIED | LOAD-BEARING | "Spark Knight" is Klee's Knights of Favonius title; she is a Mondstadt character. https://wiki.hoyolab.com/m/genshin/entry/12?lang=en-us ; https://game8.co/games/Genshin-Impact/archives/321490 . (Note of record, not a defect: her *character card title* in-game is "Fleeing Sunlight"; "Spark Knight" is her order rank. Both are canon.) |
| Klee is Pyro and uses "catalyst-grade cadence" — every attack applies Pyro | `docs/klee-cards.yaml:2`; `docs/klee-character-design.md:6`; `Element => Element.Pyro` on every Klee card, e.g. `klee-mod/KleeCode/Cards/Generated/JumpyDumpty.cs:35-36` | VERIFIED | LOAD-BEARING | Klee is a 5★ Pyro **Catalyst** user of Mondstadt (genshin-db character record, `region: Mondstadt`, `weapontype: Catalyst`, `element: Pyro`): https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/characters/klee.json . Catalyst normal attacks apply the wielder's element in Genshin. |
| "Kaboom!" is a Klee ability name (basic Attack, 4 copies in the starting deck) | `docs/klee-cards.yaml:7`; `klee-mod/KleeCode/Cards/Kaboom.cs:48`; `docs/klee-character-design.md:21` | VERIFIED | LOAD-BEARING | "Kaboom!" is Klee's **Normal Attack** talent name. https://genshinimpact.wiki.fextralife.com/Klee ; wiki article exists at https://genshin-impact.fandom.com/wiki/Kaboom! |
| "Jumpy Dumpty" is Klee's signature bomb ability, and it places **mines** on enemies | `docs/klee-cards.yaml:11-12`; `klee-mod/KleeCode/Cards/Generated/JumpyDumpty.cs:49-50`; `.../JumpyDumptyMk2.cs:49-50` | VERIFIED | LOAD-BEARING | "Jumpy Dumpty" is Klee's **Elemental Skill**: the thrown bomb bounces thrice, and "on the third bounce, the bomb splits into many mines. The mines will explode upon contact with opponents, or after a short period of time." https://genshinimpact.wiki.fextralife.com/Klee |
| "Mine Toss" — placing mines is a Klee verb | `docs/klee-cards.yaml:18-19`; `klee-mod/KleeCode/Cards/Generated/MineToss.cs:46-47` | VERIFIED | LOAD-BEARING | Same Jumpy Dumpty mine mechanic as above. Repo art sourcing independently corroborates the term against the wiki asset `Dodoco's_Bomb-Tastic_Adventure_Krash-Kaboom_Mine.png` (`art/SOURCES.tsv:13-14`). |
| "Sparks 'n' Splash" is Klee's Burst, and it fires **4 sparks** at random enemies for a duration | `docs/klee-cards.yaml:186-188`; `klee-mod/KleeCode/Cards/SparksNSplash.cs:41-46` (description: "deal 5 damage to a random enemy 4 times, applying Pyro") | VERIFIED | LOAD-BEARING | Canon Elemental Burst: "continuously summons Sparks 'n' Splash to attack nearby opponents, dealing AoE Pyro DMG"; "Each Sparks 'n' Splash sends **4 sparks**, randomly targeting all enemies." https://keqingmains.com/klee/ ; https://genshinimpact.wiki.fextralife.com/Klee |
| "Pounding Surprise" is Klee's Spark-granting passive talent, and **3 Sparks make the next Attack free** | `klee-mod/KleeCode/Relics/PoundingSurprise.cs:53-56`; `docs/klee-character-design.md:23` | VERIFIED | LOAD-BEARING | Canon A1 passive "Pounding Surprise": Klee obtains an **Explosive Spark** … "consumed by the next Charged Attack, which **costs no Stamina** … Klee can hold up to **3** Explosive Sparks." https://genshin-impact.fandom.com/wiki/Pounding_Surprise (surfaced via search; page itself 402 — see Blocked sources). The mod's trigger differs (bomb detonation vs. Jumpy Dumpty/Normal-Attack hit at 50%) — that is a mechanical re-home, not a canon assertion. |
| "All of My Treasures!" is a Klee ability name | `docs/klee-cards.yaml:197`; `klee-mod/KleeCode/Cards/Generated/AllMyTreasures.cs:46` | VERIFIED | LOAD-BEARING | Canon **Utility Passive** "All Of My Treasures!" (displays nearby Mondstadt-specific resources on the minimap). https://genshinimpact.wiki.fextralife.com/Klee ; https://www.thegamer.com/genshin-impact-klee-pro-tips-tricks-guide/ . Effect in-mod (place 6 Bombs) is unrelated to the canon effect; the *name* claim is what is verified. |
| "Chained Reactions" is a Klee constellation name (C1) — including the plural | `docs/klee-cards.yaml:191`; `klee-mod/KleeCode/Cards/Generated/ChainedReactions.cs:43` | VERIFIED | LOAD-BEARING | Klee C1, official name plural: https://genshin-impact.fandom.com/wiki/Chained_Reactions . (Fextralife renders it singular "Chained Reaction" — the Fandom article title and category use the plural, which the repo matches.) |
| "Explosive Frags" is a Klee constellation name (C2), and its effect is a defence-debuff on bomb hits | `docs/klee-cards.yaml:193-194`; `klee-mod/KleeCode/Cards/Generated/ExplosiveFrags.cs:39-40` ("apply Vulnerable") | VERIFIED | LOAD-BEARING | Klee C2 "Explosive Frags": "being hit by Jumpy Dumpty's mines decreases opponents' DEF by 23% for 10s." https://gamerant.com/genshin-impact-a-complete-guide-to-klee-constellations/ ; https://genshin-impact.fandom.com/wiki/Category:Klee_Constellations |
| "Sparkly Explosion" is a Klee constellation name (C4) | `docs/klee-cards.yaml:195`; `klee-mod/KleeCode/Cards/Generated/SparklyExplosion.cs:49` | VERIFIED | LOAD-BEARING | Klee C4: departure explosion during Sparks 'n' Splash, 555% ATK AoE Pyro. https://gamerant.com/genshin-impact-a-complete-guide-to-klee-constellations/ |
| "Blazing Delight" is a Klee constellation name (C6) | `docs/klee-cards.yaml:189`; `klee-mod/KleeCode/Cards/Generated/BlazingDelight.cs:39` | VERIFIED | LOAD-BEARING | Klee C6: party energy regen during Sparks 'n' Splash. https://gamerant.com/genshin-impact-a-complete-guide-to-klee-constellations/ . The mod card also grants **energy** (3 Burst Energy per detonation), which is a partial echo of the canon effect. |
| "Dodoco Tales" is "Klee's signature catalyst" (upgraded starter relic title, R69) | `klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:72,99-100,148`; `docs/reserved-card-names.txt:25` | VERIFIED | LOAD-BEARING | Dodoco Tales is a 4★ **Catalyst** themed on Klee/Dodoco, widely and consistently described as her signature weapon. https://www.technomiz.com/dodoco-tales-klees-signature-weapon-stats-and-passives-revealed/ ; https://www.sportskeeda.com/esports/genshin-impact-1-6-leaks-dodoco-tales-klee-s-signature-weapon-stats-passives-revealed . (Precision note: it is a 4★ event weapon, not a 5★ signature banner weapon.) |
| "Dodoco" is a Klee-owned entity (used as a design/art anchor across the pool) | `docs/klee-cards.yaml:87-91`; `klee-mod/KleeCode/Vfx/KleeCombatVfx.cs`; `klee-mod/pck-src/klee/vfx/dodoco_pop.tscn`; `art/SOURCES.tsv` (≈14 Dodoco-named wiki assets cited across `jumpy_dumpty`, `pop`, `mine_toss`, `bomb_voyage`, `sparkly_treasure`, `spark_collection`, `sizzle`, `ammo_scavenging`, `remote_detonator`, `fish_flavored_bait`, `quick_fuse`, `big_badda_boom`, `blast_radius`, `duck_and_cover`) | VERIFIED (group, ~14 art citations + 3 code sites) | LOAD-BEARING | Dodoco is "Klee's first friend, and one of her very best," a doll handmade by Alice on Klee's clover backpack. https://genshinimpact.wiki.fextralife.com/Klee ; https://genshin-impact.fandom.com/wiki/Dodoco |
| Card "Imaginary Friend" (id `clockwork_toy`) takes its display name from the in-game item "Imaginary Friend Dodoco" | `docs/klee-cards.yaml:87-92`; `klee-mod/KleeCode/Cards/Generated/ClockworkToy.cs:42`; `art/SOURCES.tsv:9` | VERIFIED | LOAD-BEARING | The furnishing exists as **"Imaginary Friend: Dodoco"** — "a lovely ornament modeled after Klee's imaginary friend Dodoco." https://gi.yatta.moe/en/archive/furniture/374833/imaginary-friend-dodoco . (Canon punctuation carries a colon; the repo's comment omits it. Recorded, not scored as a separate verdict.) |
| "Sorry, Jean…" — Jean is the authority figure Klee apologises to | `docs/klee-cards.yaml:83`; `klee-mod/KleeCode/Cards/Generated/SorryJean.cs:43`; `docs/klee-character-design.md:31` | VERIFIED | LOAD-BEARING | Canon: "Faced with Jean's stern glare, Klee surrenders all her concealed explosives and is then escorted to solitary confinement." Jean is Acting Grand Master and confines Klee "about once or twice a week." https://genshinimpact.wiki.fextralife.com/Klee ; https://genshin-impact.fandom.com/wiki/Klee/Storyline |
| "Fish Blasting" is a literal Klee activity | `docs/klee-cards.yaml:199`; `klee-mod/KleeCode/Cards/FishBlasting.cs` → `Generated/FishBlasting.cs:51` | VERIFIED | LOAD-BEARING | Canon uses the exact phrase: "Klee spent time with her mother Alice **fish blasting** at Starfell Lake"; "suspiciously high number of deaths from unnatural causes among the fish of Starfell Lake." https://genshinimpact.wiki.fextralife.com/Klee ; https://genshin-impact.fandom.com/wiki/Klee/Storyline |
| "Confiscated" (dead token added by Fish Blasting; "Does nothing.") encodes confiscation of Klee's explosives | `docs/klee-cards.yaml:200`; `klee-mod/KleeCode/Cards/Confiscated.cs:26-27` | VERIFIED | LOAD-BEARING | Canon: Klee "surrenders all her concealed explosives" to Jean and is escorted to solitary confinement. The token riding specifically on *Fish Blasting* matches the canon causal chain (fish blasting → Jean → confiscation). https://genshin-impact.fandom.com/wiki/Klee/Storyline |
| "Fish-Flavored Bait" — the "Fish-Flavored" register is Klee's | `docs/klee-cards.yaml:20-21`; `klee-mod/KleeCode/Cards/Generated/FishFlavoredBait.cs:49` | VERIFIED (register) | LOAD-BEARING | Klee's specialty dish is **"Fish-Flavored Toast"**, made at Jean's instruction "by way of apology for wantonly using her bombs to scare away the fish." https://genshin-impact.fandom.com/wiki/Fish-Flavored_Toast ; https://game8.co/games/Genshin-Impact/archives/316518 . The noun "Bait" is mod-original — no canon Klee item of that name found. |
| "Spark Knight Style" and "True Spark Knight" derive from Klee's order title | `docs/klee-cards.yaml:128,201`; `Generated/SparkKnightStyle.cs:39`; `Generated/TrueSparkKnight.cs:39` | VERIFIED | LOAD-BEARING | "Spark Knight" is Klee's Knights of Favonius title (see row 1). https://wiki.hoyolab.com/m/genshin/entry/12?lang=en-us |
| Relic sketch: "burst-energy-carryover (**Favonius**-flavored)" — Klee belongs to a Favonius-named order | `docs/klee-character-design.md:34` | VERIFIED | COSMETIC (unshipped v0.1 sketch) | Klee is a member of the Knights of Favonius. https://tvtropes.org/pmwiki/pmwiki.php/Characters/GenshinImpactKnightsOfFavoniusPersonnel ; https://wiki.hoyolab.com/m/genshin/entry/12?lang=en-us |
| Design doc treats **Albedo** as a Klee-adjacent figure (dream-team/companion appetite) | `docs/klee-character-design.md:44`; `docs/klee-character-design.md:30` | VERIFIED | COSMETIC (design prose, not a shipped string) | Canon: after Klee was placed in the care of the Knights of Favonius she "was quickly taken under Albedo and Kaeya's wings"; Alice told Albedo "treat her like a real younger sister." https://genshin-impact.fandom.com/wiki/Albedo/Profile ; https://www.thegamer.com/genshin-impact-klee-facts/ |
| Sparks are a **bankable, capped resource that makes the next Attack free** (whole `spark` archetype: 21 cards) | `docs/klee-cards.yaml:38-66,127-152`; `docs/klee-character-design.md:23`; `klee-mod/KleeCode/Powers/SparkPower.cs` | VERIFIED (group, 21 cards + relic + design doc) | LOAD-BEARING | Canon Explosive Sparks are bankable (max 3) and make the next Charged Attack cost no Stamina. https://genshin-impact.fandom.com/wiki/Pounding_Surprise (via search snippet) ; https://genshinimpact.wiki.fextralife.com/Klee |
| Bombs / delayed explosives / demolition as Klee's core verb (`demolition` archetype: 28 cards; Bomb keyword, `BombPower`) | `docs/klee-cards.yaml:17-37,100-126`; `docs/klee-character-design.md:6,22`; `klee-mod/KleeCode/Cards/KleeKeywords.cs:55` | VERIFIED (group, 28 cards) | LOAD-BEARING | Canon: Klee is the bomb specialist of Mondstadt; her mother Alice "taught Klee about explosives, fuses, and demolition techniques"; she is found "making new bomb recipes or terrorizing the fish of Mondstadt's lakes." https://genshinimpact.wiki.fextralife.com/Klee |
| "Da-da-da!" is a Klee voice line | `docs/klee-cards.yaml:203`; `klee-mod/KleeCode/Cards/Generated/DaDaDa.cs:49` | UNVERIFIABLE | LOAD-BEARING | Searched: Fandom `Klee/Voice-Overs` (blocked, HTTP 402 through the proxy), `Category:Klee English Voice-Overs` (same block), Project Amber avatar page `gi.yatta.moe/en/archive/avatar/10000029` (HTTP 403), HoneyHunterWorld `gensh.honeyhunterworld.com/klee_038` (HTTP 403), genshin-db character JSON (contains no voice-over block). Only corroboration reachable was low-quality SEO aggregate pages ("'Da da da!' is probably Klee's most iconic combat line", e.g. https://joy.sfmlab.com/sfmlab-news/klee-voice-lines-a-comprehensive-guide-english-1764796838), which do not meet a citation bar. Cannot confirm the exact string, its punctuation, or which talent it fires on. |
| "Vermillion Pact" is a Genshin/Pyro-lore term | `docs/klee-cards.yaml:214`; `klee-mod/KleeCode/Cards/Generated/VermillionPact.cs:39` | UNVERIFIABLE | LOAD-BEARING (rare, anchors the reaction-amp payoff) | No Genshin entity named "Vermillion Pact" found. Nearest canon term is the artifact set **Vermillion Hereafter** (https://genshin-impact.fandom.com/wiki/Vermillion_Hereafter), whose lore does involve "a pact" — but it is a Sumeru/Lost Valley artifact set with no Klee association. Searched: `"Vermillion"/"Vermilion" pact Pyro term Klee lore`. |
| "Kaboom Beetle Swarm" — "Kaboom Beetle" as a Genshin creature/term | `docs/klee-cards.yaml:125`; `klee-mod/KleeCode/Cards/KaboomBeetleSwarm.cs:53` | UNVERIFIABLE | LOAD-BEARING (uncommon demolition payoff) | No Genshin "Kaboom Beetle" found. Adjacent canon terms located: **Kaboom Box** (5.0 anniversary gadget, https://genshin-impact.fandom.com/wiki/Kaboom_Box), **Boom Blossom** (overworld hazard, https://genshin-impact.fandom.com/wiki/Boom_Blossom), and beetle-battle *events* (Shuyu's Baffling Beetle Battle Bowl). "Kaboom" alone is canon (Klee's Normal Attack); the compound is not. Searched: `"Kaboom Beetle" OR "Boom Beetle" Genshin`. |
| "Tail of Flame" is a Genshin term | `docs/klee-cards.yaml:55`; `klee-mod/KleeCode/Cards/Generated/TailOfFlame.cs:49` | UNVERIFIABLE | COSMETIC (common spark card) | No referent found. Nearest canon construction is the claymore **Tail of Boreas**; no "Tail of Flame" exists in weapon, talent, artifact, or item namespaces reachable via search. Searched: `Genshin "Tail of Flame" term`. |
| "Bomb Voyage" as a Genshin item/ability | `docs/klee-cards.yaml:36`; `klee-mod/KleeCode/Cards/Generated/BombVoyage.cs:46` | UNVERIFIABLE | COSMETIC | No canon referent. The card's own art citations point at the canon furnishing set **"Dodoco's Bomb-Tastic Adventure"** (`art/SOURCES.tsv:25-27`), which is the nearest real name; "Bomb Voyage" itself is a mod-original pun. |
| Externally-sourced (non-Teyvat) English phrases used as Klee card titles: "Big Badda Boom", "Boom Goes the Dynamite", "Spirited Away", and the Snap!/Crackle!/Pop! trio | `docs/klee-cards.yaml:28,74,171,13,51,65`; `Generated/BigBaddaBoom.cs:49`, `BoomGoesTheDynamite.cs:49`, `SpiritedAway.cs:39`, `Snap.cs:49`, `Crackle.cs:49`, `Pop.cs:29` | UNVERIFIABLE as Genshin canon (group, 6 cards) | LOAD-BEARING (`Pop!` is a starting-deck basic; the rest are pool commons) | No Genshin referent for any of the six. Documented non-Teyvat origins: "Big Badda Boom" — *The Fifth Element* (1997), https://getyarn.io/yarn-clip/a2179ebd-79bb-4405-9232-e2ed0870dd29 ; "Boom goes the dynamite" — 2005 Ball State sportscast meme, https://knowyourmeme.com/memes/boom-goes-the-dynamite and https://en.wikipedia.org/wiki/Boom_goes_the_dynamite ; "Spirited Away" — 2001 Studio Ghibli film; Snap/Crackle/Pop — Rice Krispies mascots. Recorded as a factual provenance observation, not a judgement. |
| Klee's child-register vocabulary: "Duck and Cover", "Hide and Seek", "Run Away!", "Spooked!", "Can't Catch Me!", "Skip and Hop", "Sugar Rush", "Playtime Forever", "Best Friends Forever", "Study Buddy", "Eager to Help", "Sweet Dreams", "Bright Idea", "Friendly Visit", "Surprise Visit", "Warm Glow", "Patched Dress", "Sparkly Treasure", "Secret Stash", "Pocket Fireworks", "Da-da-da!" (name aside) | `docs/klee-cards.yaml` (21 entries across basic/common/uncommon/rare); corresponding `Generated/*.cs` titles | UNVERIFIABLE as canon quotations (group, 21 cards) | LOAD-BEARING as a *register law* (the pool's naming convention), COSMETIC individually | None of the 21 strings is a canon Genshin item, talent, constellation, dish, furnishing or documented voice line — searched against genshin-db character JSON, Fandom category listings for Klee talents/constellations/furnishings/voice-overs (402), Fextralife Klee page, and HoYoWiki entry 12. The *register* they implement (a small child who plays, hides, hoards treasures, has a best friend) is canon-consistent with Klee's profile (https://genshinimpact.wiki.fextralife.com/Klee), but the strings themselves are mod-original and cannot be sourced. |
| Mod-original demolition/lab vocabulary with no canon referent: "Quick Fuse", "Double Pop", "Ammo Scavenging", "Blast Radius", "Chain Fuse", "Careful Arrangement", "Cluster Charge", "Trip Wire", "Controlled Demolition", "Remote Detonator", "Explosives Workshop", "Bombs Away!", "Endless Fireworks", "Flame on the Wick", "Gleeful Barrage", "Hot Hands", "Rapid Fire", "Sizzle", "Crackle" (mechanics aside), "Combustion Study", "Study of Explosions", "Alchemical Curiosity", "Catalytic Conversion", "Perfect Timing", "Flame Dance", "Dodge Roll", "Borrowed Brilliance", "Spark Collection", "No Holding Back", "The Big One" | `docs/klee-cards.yaml` (30 entries); corresponding `Generated/*.cs` titles | UNVERIFIABLE as canon (group, 30 cards) | COSMETIC individually; the demolition register they carry is LOAD-BEARING | No canon Genshin referent for any of the 30 under the searches listed above. Two near-collisions recorded: **"Catalytic Conversion"** (`klee-cards.yaml:154`) sits one word from Sucrose's canon A1 passive **"Catalyst Conversion"**, which the same build ships as a companion card (`Generated/SucroseCatalystConversion.cs:53`); and "Sizzle"/"Crackle" carry no canon weight beyond onomatopoeia. |
| "Jumpy Dumpty Mk.II" / "Jumpy Dumpty Mk.Omega" as canon ability variants | `docs/klee-cards.yaml:101`; `klee-mod/KleeCode/Cards/JumpyDumptyMkOmega.cs:51` | UNVERIFIABLE (extension of a verified canon name) | LOAD-BEARING | Canon has one "Jumpy Dumpty" with no Mk. designations. Mk.Omega's own class comment concedes "Title pending the naming/lore audit" (`JumpyDumptyMkOmega.cs:32`). The base name is VERIFIED (row 4); the suffixes are mod-original. |
| Potion sketch names "Bottled Fireworks", "Spark Cider", "Warm Milk (heal; **Jean insists**)" | `docs/klee-character-design.md:35` | UNVERIFIABLE | COSMETIC (unshipped — grep across `*.yaml`/`*.cs`/`*.py` returns zero hits; design-doc sketch only) | No canon Genshin items of these names found. "Cider" has a Mondstadt referent (Cider Lake); "Jean insists" is consistent with the verified Jean-as-minder relationship (see the "Sorry, Jean…" row) but the specific milk instruction is not sourced. |
| Sim/statline assertions: HP 62, energy 3, draw 5, Burst meter 40, axis targets A1–A7 | `docs/klee-character-design.md:8-24` | UNVERIFIABLE (out of canon's domain) | COSMETIC for this audit | These are Slay-the-Spire-2 balance quantities with no Genshin analogue; Genshin has no HP-62/energy-3 concept for a playable character. Recorded so the surface is complete, not as a defect. |
| Upgrade sheet asserts no new canon at all — every entry is a numeric/keyword delta keyed to an existing card id | `docs/klee-upgrades.yaml` (all 89 Klee-pool entries) | VERIFIED (no canon claims present) | n/a | Read in full: the file contains only deltas (`{damage: +3}`, `{cost: -1}`, `{retain: true}`, …) and balance-rationale comments. The one lore-adjacent line, `sparks_n_splash: NO UPGRADE (kit card…)` (`klee-upgrades.yaml:75`), makes no canon assertion beyond the card name already verified above. |

### N1 counts
**VERIFIED 21 / CONTRADICTED 0 / UNVERIFIABLE 10** (28 ledger rows; 4 rows are grouped and together cover 92 further card instances — the Dodoco group ~14 art citations, the register group 21 cards, the demolition-vocabulary group 30 cards, the external-phrase group 6 cards, the spark group 21 cards, the bomb group 28 cards).

Load-bearing split: **VERIFIED load-bearing 18**, verified cosmetic 3 (plus 1 n/a row for the upgrade sheet); **UNVERIFIABLE load-bearing 5** (`Da-da-da!`, `Vermillion Pact`, `Kaboom Beetle Swarm`, the external-phrase group incl. the starting-deck basic `Pop!`, the Mk.II/Mk.Omega suffixes), **UNVERIFIABLE cosmetic 5**.

### Blocked sources and workarounds
- **genshin-impact.fandom.com — HTTP 402 Payment Required on every `WebFetch`** (confirmed on `/wiki/Klee`). Workaround used: `WebSearch`, which returns Fandom article titles/URLs and quoted body text without fetching; Fandom URLs cited above are therefore cited *via search snippet*, not via direct fetch.
- **gensh.honeyhunterworld.com — HTTP 403** on `/klee_038/?lang=EN`.
- **gi.yatta.moe (Project Amber) — HTTP 403** on the avatar archive page. Its *furniture* page surfaced fine through search snippets and is cited for "Imaginary Friend: Dodoco".
- **genshin-db raw JSON (`theBowja/genshin-db-dist`)** fetched successfully and used for the element/weapon/region/rarity row, but the character record contains **no talent, passive, constellation, or voice-over names** — it is limited to profile + ascension data. Talent/constellation verification therefore ran through Fextralife (direct fetch OK) and search-surfaced Fandom/GameRant/KQM text.
- Net effect on the ledger: the single claim that could not be closed by any reachable source is the **`Da-da-da!` voice line**, because every voice-over corpus (Fandom voice-over pages, Project Amber, HoneyHunter) is behind one of the blocks above.

---

## N2 — Furina card pool + upgrades + register laws

Surface audited (read-only; no repo file was edited, no commit, no push):
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\docs\furina-cards.yaml` (847 lines, 82 cards)
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\docs\furina-upgrades.yaml` (203 lines)
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\docs\furina-kickoff-v0.1.md`
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\docs\furina-art-pass-requirements.md`
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\docs\furina-strength-findings-2026-07-28.md`
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\klee-mod\KleeCode\Cards\Furina\` (incl. `Generated\*.cs`, 84 shipped `("description", …)` strings)
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\tools\lint_furina_registers.py` (the law)
- sprint logs: `docs\sprint-fanfare-rework-log-2026-07-28.md`, `docs\sprint-fanfare-compensation-log-2026-07-28.md`, `docs\archive\furina-*.md`

**Surface boundary recorded:** the Neuvillette / Lynette / Charlotte / Freminet / Chevreuse / Navia / Clorinde / Arlecchino cards are declared in `docs\fontaine-companions.yaml`, not in Furina's sheet, even though `GuestNeuvillette*.cs` are emitted into `Cards\Furina\Generated\`. Their canon audit belongs to the companions surface. Only the kickoff §10 roster claim (which *is* on my source list) is adjudicated below.

---

### N2a Canon claims

| Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|
| Furina's Normal Attack is named "Soloist's Solicitation" | `docs\furina-cards.yaml:56-57` (`soloists_solicitation`, comment "Her normal attack."); `Generated\SoloistsSolicitation.cs` | VERIFIED | LOAD-BEARING (card name + shipped title) | https://keqingmains.com/furina/ — "Normal Attack: Soloist's Solicitation" |
| Furina's Elemental Burst is named "Let the People Rejoice" | `docs\furina-cards.yaml:661` (`let_the_people_rejoice`, `tags:[burst] kit_card:true`); `Cards\Furina\LetThePeopleRejoice.cs` | VERIFIED | LOAD-BEARING (her kit-Burst card) | https://genshin-impact.fandom.com/wiki/Let_the_People_Rejoice (title only, page body blocked); corroborated https://keqingmains.com/furina/ |
| Her Burst deals AoE Hydro and is tied to Fanfare | `docs\furina-cards.yaml:663` (`damage 8 target: all_enemies, bonus_formula: 1_per_4_fanfare`) | VERIFIED | LOAD-BEARING | KQM: Burst "creates a stage that deals AoE Hydro DMG based on Furina's Max HP… Furina gains Fanfare points based on HP changes" |
| Her Elemental Skill summons a cast called Salon Members | `docs\furina-cards.yaml:9` ("SALON v2"), `salon_member` power, `Generated\*.cs` "[gold]Salon Member[/gold]" | VERIFIED | LOAD-BEARING (the whole salon register) | KQM / Salon Solitaire: Ousia summons 3 Salon Members |
| "Gentilhomme Usher" is a canon Salon Member, the Ball Octopus | `docs\furina-cards.yaml:141-142` — "The Ball Octopus (v2: THE SHIELD…)" | VERIFIED | LOAD-BEARING | Salon Solitaire: "the Ball Octopus-shaped Gentilhomme Usher" |
| "Surintendante Chevalmarin" is a canon Salon Member, the Bubbly Seahorse | `docs\furina-cards.yaml:144-145` — "The Bubbly Seahorse (v2: THE APPLIER…)" | VERIFIED | LOAD-BEARING | Salon Solitaire: "the Bubbly Seahorse-shaped Surintendante Chevalmarin" |
| "Mademoiselle Crabaletta" is a canon Salon Member (crab) | `docs\furina-cards.yaml` (`mademoiselle_crabaletta`); `Generated\MademoiselleCrabaletta.cs` | VERIFIED | LOAD-BEARING | Salon Solitaire: "the Armored Crab-shaped Mademoiselle Crabaletta" |
| The member roles "hammer + shield" (Crabaletta = hammer, Usher = shield) | `docs\furina-cards.yaml:717` (`endless_waltz` comment "The waltzing pair (hammer + shield, v2)") | UNVERIFIABLE | COSMETIC (design comment) | Canon gives shapes (octopus / seahorse / crab) and a shared Hydro-DMG-on-interval attack; no canon assigns a shield or hammer role. Searched Salon Solitaire talent text via KQM + Fandom title results. |
| "Singer of Many Waters" is the canon Pneuma-aligned healing summon | `docs\furina-cards.yaml:675-676` (`singer_of_many_waters`, `op: heal`, "The Pneuma voice") | VERIFIED | LOAD-BEARING (card name + the true-heal law's poster child) | Salon Solitaire: "Pneuma summons the Singer of Many Waters, who will heal nearby active character(s)" |
| Pneuma / Ousia (Arkhe) is Furina canon | `docs\furina-kickoff-v0.1.md:54` ("Pneuma/Ousia is **pure flavor, zero mechanics**"), `:110` | VERIFIED | COSMETIC (explicitly shipped as zero-mechanics) | https://genshin-impact.fandom.com/wiki/Furina — "can alternate between Pneuma and Ousia alignments" |
| "Endless Waltz" is one of her passives | `docs\furina-cards.yaml:717` — "Named for her passive." | VERIFIED | LOAD-BEARING (card name) | https://genshin-impact.fandom.com/wiki/Endless_Waltz — Furina 1st Ascension Passive |
| "Unheard Confession" is a canon Furina talent name | `docs\furina-cards.yaml:678` (`unheard_confession`) | VERIFIED | LOAD-BEARING (card name) | https://genshin-impact.fandom.com/wiki/Unheard_Confession — Furina 4th Ascension Passive |
| "Universal Revelry" is a canon Furina term | `docs\furina-cards.yaml:733` (`universal_revelry`) | VERIFIED | LOAD-BEARING (card name) | KQM / Pro Game Guides: the Burst "causes party members to enter the Universal Revelry state" |
| "The Sea Is My Stage" is a canon Furina term | `docs\furina-cards.yaml:725` (`the_sea_is_my_stage`, `tags:[focalors]`) | VERIFIED | LOAD-BEARING (card name) | https://genshin-impact.fandom.com/wiki/The_Sea_Is_My_Stage — Furina's Utility Passive |
| …and it is a **Constellation** | `docs\furina-cards.yaml:729` — "THE CONSTELLATION CARD (F-B2)." | CONTRADICTED | COSMETIC (design comment, not a shipped string) | Canon classifies it as a **Utility Passive**, not a Constellation; Furina's C6 is "Hear Me – Let Us Raise the Chalice of Love!" (Gameranx Furina Constellation Guide). Reading "Constellation card" as internal sprint jargon is possible but the sheet gives no such gloss. |
| "Fanfare" is Furina's canon resource | `docs\furina-cards.yaml:16-40`; ~20 shipped `[gold]Fanfare[/gold]` strings | VERIFIED | LOAD-BEARING | KQM: "Furina will gain 150 Fanfare, and her Fanfare limit is increased by 100" |
| Fanfare has a canon **cap/limit** (justifying the printed "Fanfare Cap") | `docs\furina-cards.yaml:26`; 16 shipped "[gold]Fanfare Cap[/gold] +N" strings | VERIFIED | LOAD-BEARING (shipped keyword) | KQM: "her Fanfare limit is increased by 100" |
| Fanfare generation is coupled to **party members'** HP flux ("her Genshin identity") | `docs\furina-kickoff-v0.1.md` §4 Co-op bullet | VERIFIED (HP half) | LOAD-BEARING (co-op mechanic) | KQM: "Furina gains Fanfare points based on HP changes" of nearby party members |
| …the **Encore** half of that same coupling | same bullet ("partner HP/Encore flux counts toward Fanfare") | UNVERIFIABLE | LOAD-BEARING | Encore is an authored resource with no Genshin analogue; searched Furina talent/passive/constellation text — no canon resource named Encore. |
| Fanfare is "**capped at %maxHP**" | `docs\furina-kickoff-v0.1.md` §4 Fanfare bullet | CONTRADICTED | COSMETIC (framed as a design declaration, not as canon) | Canon Fanfare limit is a flat 300, raised by 100 during the Burst — not a percentage of Max HP (KQM). Furina's *Max HP* scales her damage/healing; it does not set the Fanfare ceiling. |
| Furina is "the Regina of All Waters" | `docs\furina-kickoff-v0.1.md:9` (the doc's one-line identity); `docs\furina-cards.yaml:61`, `:369` ("the Regina looks at you", "The Regina's stare"); `reginas_mercy` / "The Regina's Mercy" | VERIFIED | LOAD-BEARING (identity line + shipped card title) | https://genshin-impact.fandom.com/wiki/Focalors — "Focalors—also known as the Regina of All Waters, Kindreds, Peoples and Laws". Note the full canon title is longer and is *Focalors'*; Furina bore it publicly as the presenting Archon. The repo's truncation is the form in common use. |
| "The Regina's Mercy": "she gives EVERYTHING, once… twelve points of grace, and the nation permanently remembers" | `docs\furina-cards.yaml:810-812` | VERIFIED | LOAD-BEARING (card identity + Focalors cap slot) | Focalors separated her divinity from her body/spirit and expended herself to end the prophecy — https://genshin-impact.fandom.com/wiki/Focalors ; Game8 Focalors/Furina lore guide |
| Focalors is the divinity, Furina the human half — "the divinity the audience mistakes for theatre" | `docs\furina-cards.yaml:727-728` | VERIFIED | LOAD-BEARING (the archon register's whole premise) | Fandom Furina: "Focalors separated her divinity from her body and spirit… the body and spirit she left behind became Furina, embodying her humanity" |
| Furina is the Hydro Archon of Fontaine, element Hydro | `docs\furina-cards.yaml:6`; `docs\furina-kickoff-v0.1.md` §1 | VERIFIED | LOAD-BEARING | Fandom Furina: "a playable Hydro character… Introduced as the flamboyant and overconfident Hydro Archon" |
| Furina is an actress by craft / theatre director ("the post-truth professional") | `tools\lint_furina_registers.py:7-8` (the `salon` register definition) | VERIFIED | LOAD-BEARING (defines a register) | Fandom Furina: "she later discards [the persona] in favor of living a relatively humbler life as an actress and artistic consultant" |
| The 500-year performance / the decaying mask / the audience of a nation | `tools\lint_furina_registers.py:9-11` (the `archon` register definition) | VERIFIED | LOAD-BEARING (defines a register) | Focalors' plan ran ~500 years to Fontaine's prophesied dissolution, with Furina publicly performing as Archon throughout — https://genshin-impact.fandom.com/wiki/Focalors ; Game8 lore guide |
| "the trial as the act's public climax" / courtroom vocabulary (`courtroom_drama`, `witness_stand`, `the_final_verdict`, `cross_examination`) | `tools\lint_furina_registers.py:11`; `docs\furina-cards.yaml:578`, `:740-…`; `Generated\CourtroomDrama.cs`, `WitnessStand.cs`, `TheFinalVerdict.cs` | VERIFIED | LOAD-BEARING (four shipped cards) | Fontaine runs public trials and Furina's own trial is the climax of the Archon Quest — Game8 Focalors/Furina lore guide; Fandom Furina |
| Fontaine's 4-star roster is exactly Lynette (Anemo), Freminet (Cryo), Charlotte (Cryo), Chevreuse (Pyro) | `docs\furina-kickoff-v0.1.md:239-241` | VERIFIED | LOAD-BEARING (roster ratification) | GameWith "All Fontaine Characters – 5 & 4 Stars"; ONE Esports Fontaine characters list. Elements confirmed individually. Verified against the roster as of the sources fetched 2026-08; a later patch adding a Fontaine 4-star would not be caught here. |
| "Fontaine has zero 4-star Electro" | `docs\furina-kickoff-v0.1.md:260` | VERIFIED | LOAD-BEARING (drives the companion element spread) | Same sources: none of the four Fontaine 4-stars is Electro (Anemo/Cryo/Cryo/Pyro); Fontaine's Electro representative Clorinde is 5-star. |
| "Center Stage" is a Furina term | `Cards\Furina\SpotlightCards.cs:27-28`, `:84` (shipped title + description); `docs\furina-cards.yaml:24`, `:42`; `docs\furina-art-pass-requirements.md:302`, `:470` | UNVERIFIABLE | **LOAD-BEARING (shipped player-facing string and a Fanfare generation source)** | Searched Furina's talents, passives, Burst-state names and all six constellations; no canon Furina ability, state or constellation is named "Center Stage". C6 is "Hear Me – Let Us Raise the Chalice of Love!" (Gameranx). It is generic theatrical English, not a canon-sourced term — recorded as uncitable, **not** as wrong. |
| "Salon Début" (the starter's name) | `docs\furina-cards.yaml:84`; `Generated\SalonDebut.cs:50` | UNVERIFIABLE (authored) | LOAD-BEARING (shipped title) | Canon skill is "Salon **Solitaire**"; "Salon Début" is authored theatrical flavor. The sheet's own NAMING NOTE (`furina-cards.yaml:14-15`) declares exactly this split: "talent/summon names verified…; other names are authored theatrical flavor". Accent is correct UTF-8 (`é` = `M-CM-)`) in **both** the sheet and the C#, so the two surfaces agree. |
| French loanword spellings: Gentilhomme, Surintendante, Mademoiselle, Chevalmarin, Crabaletta | `docs\furina-cards.yaml:141-150`; matching `Generated\*.cs` titles | VERIFIED (byte-exact vs canon) | LOAD-BEARING (shipped titles) | Salon Solitaire member names as quoted by KQM / official @GenshinImpact post |
| Italian musical loanwords in the same pool: Fortissimo Guard, Crescendo, Prima Donna, Florid Cadenza, Duet, Matinée Performance | `docs\furina-cards.yaml` (those ids) | UNVERIFIABLE | COSMETIC | No repo doc states a French-only (or Fontaine-only) loanword law. Grepped `docs/` for "french", "italian", "loanword", "accent" — zero hits beyond the accented card name itself. Nothing to adjudicate against; recorded, not judged. |
| **Absent institutions** — the Oratrice Mécanique d'Analyse Cardinale, the Opera Epiclese, the Fountain of Lucine, the Fortress of Meropide, Palais Mermonia, the Marechaussee Phantom, the Erinnyes, the prophecy by name | — | NO CLAIM MADE | — | Grepped the whole surface (`furina-cards.yaml`, `furina-upgrades.yaml`, `furina-kickoff-v0.1.md`, `furina-art-pass-requirements.md`, `Cards\Furina\**`) case-insensitively for `oratrice`, `opera epiclese`, `épiclèse`, `lucine`, `meropide`, `palais`, `mermonia`, `marechaussee`, `erinnyes`, `prophecy`: **zero occurrences**. Furina's pool never names a Fontaine institution, so there is nothing here to contradict. Recorded because the audit brief asked for these specifically. |
| Lyney / Lynette / Navia / Chevreuse as characters | Named only in `docs\furina-kickoff-v0.1.md` §10 roster and in `docs\fontaine-companions.yaml` | OUT OF SURFACE | — | Card-level canon adjudication belongs to the companions surface; only the §10 roster claim is verified above. |

---

### N2b Register-grammar law check

**Premise correction, recorded before the check.** The audit brief describes the law as governing "Salon / Fanfare / Encore" registers. Those are the three **resources**. The registers are a different, orthogonal triple: **`salon` / `archon` / `private`** — voices for card *names*. The law binds resources *to* registers. All findings below are stated in the repo's own terms.

**The law, verbatim** — `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\tools\lint_furina_registers.py`, lines 2–19:

> ```
> """Register lint for the Furina pool (Curtain Call sweep, R85 / sprint §3+§5E).
>
> The register convention (RATIFIED 2026-07-27, binding on this and future
> passes) sorts every Furina card name into one of three voices:
>
>   salon    Furina the vision-holder: theatre director and actress-by-craft;
>            her cast, stagecraft vocabulary, the post-truth professional.
>   archon   Furina-as-Archon: life itself as the act -- the 500-year
>            performance, the decaying mask, the audience of a nation, the
>            trial as the act's public climax. Focalors lives here.
>   private  the life the audience never sees: backstage reserves, sweets,
>            breath, the self offstage.
>
> What is MECHANICALLY lintable is the same-resource-same-register grammar
> (the same-action-same-nation precedent applied to naming). The rules below
> are the enforceable formalization ratified with the sweep; the SEMANTIC half
> of the convention (does this name read in this voice?) is [USER]'s eyes-on
> name audit, by house law, and no tool pretends to cover it.
> ```

The eight enforceable clauses are `lint_furina_registers.py:21-73` (R1–R7, L12). The two that carry the resource→register binding, verbatim:

> ```
>   R2  any card that READS Fanfare (a bonus_formula reading fanfare, a
>       fanfare_at_least_* gate, or the gain_fanfare_floor "Fanfare +X" grant)
>       is register: archon. […]
>   R3  any card that APPLIES salon_member (deploys a cast member) is
>       register: salon. […]
>   R4  a PURE Encore card (every leaf op is gain_encore/spend_encore) is
>       register: private -- the buffer is the self rebuilt offstage --
>       UNLESS the card carries the focalors flavor tag […]
> ```

And the sheet's own magnitude sentence, `docs\furina-cards.yaml:37`:

> `#     The magnitudes restore the retired invisible rule as printed text: +5 at common/uncommon, +8 at rare.`

And the spelling clause, `docs\furina-cards.yaml:30`:

> `#     Spelled "Fanfare Cap", never bare "Cap" -- the Salon's member cap is also a per-player stat since A12.`

#### The check, run mechanically over all 82 cards

Method: parsed `docs\furina-cards.yaml` with the lint's own leaf-op walker, then re-derived R2/R3/R4/R5/R6/R7 independently rather than trusting the exit code; separately ran the shipped lint (`python tools/lint_furina_registers.py` → `furina register census: 82 cards -- salon 44 archon 28 private 10 | focalors 2` / `0 register violations` / exit 0); separately grepped all 84 shipped `("description", …)` strings in `Cards\Furina\Generated\*.cs` for the printed-keyword clauses.

Per-resource register census (independently computed, not read off the lint):

| Resource | Cards touching it | Registers actually used | Rule that binds it | Result |
|---|---|---|---|---|
| Fanfare (R2 sense: `gain_fanfare_floor`, `*_fanfare` bonus_formula, `fanfare_at_least_*`) | 18 | **archon 18 / salon 0 / private 0** | R2 | uniform |
| Fanfare (cap keyword `raise_fanfare_cap`, R2-exempt since 2026-07-28) | 16 | salon 9 / archon 5 / private 2 | R7 (type, not register) | uniform *by design* — the release is documented at `lint_furina_registers.py:27-37` |
| `salon_member` deploys | 9 | **salon 9 / archon 0 / private 0** | R3 | uniform |
| Encore (`gain_encore` / `spend_encore` / `encore_cost` / `*_encore` reads) | 21 | **archon 8 / salon 7 / private 6** | R4 | **no rule reaches any of them — see V1** |

**Violations table.** "Expected per law" is the register the quoted rule *demands*; blank where no clause reaches the case.

| Card | Resource | Register word used | Expected per law | Verdict |
|---|---|---|---|---|
| *(none)* | Fanfare (R2) | all 18 `archon` | archon | **NO VIOLATION** — R2 holds 18/18 |
| *(none)* | salon_member | all 9 `salon` | salon | **NO VIOLATION** — R3 holds 9/9 |
| **V1 — R4 is vacuous across the entire pool** | Encore | `archon` ×8, `salon` ×7, `private` ×6 | R4 demands `private` for a *pure* Encore card — and **zero of 82 cards are pure** | **NOT A VIOLATION; RULE SELECTS NOTHING.** Every Encore card on the sheet carries at least one non-Encore leaf op (`block`, `draw`, `damage`, `energy`, `apply_power`, `scry_discard`), so `_pure_encore()` (`lint_furina_registers.py:136-140`) returns False for all 82. R4 is satisfied vacuously and reports clean. The consequence is mechanical, not a taste call: **Encore is the one named resource whose register the law does not in practice constrain**, and it is split three ways. Whether that split is *wrong* is UNVERIFIABLE against the law as written — R4's antecedent is "PURE Encore card", and none of these are. |
| `quick_change` "Quick Change" | Fanfare (cap keyword) | `private` — shipped text `"The first Attack you play each turn draws {PowerAmount:diff()} card. [gold]Fanfare Cap[/gold] +{FanfareCap:diff()}."` (`Generated\QuickChange.cs:44`) | R2 no longer reaches `raise_fanfare_cap` (`lint_furina_registers.py:27-37`, `R2_OPS = ("gain_fanfare_floor",)` at `:104`) | **NO VIOLATION** — this is the exact card the R2 release was written to permit; recorded because it is the only `private` Power printing a Fanfare keyword, i.e. the release's live test case. |
| `courtroom_drama`, `crowd_work` | Fanfare (cap keyword) | `archon` | — | NO VIOLATION |
| `casting_call`, `grand_salon`, `pit_orchestra`, `leading_role`, `supporting_cast`, `top_billing`, `standing_ovation`, `fortissimo_guard`, `endless_waltz`, `star_of_the_show`, `prima_donna` | Fanfare (cap keyword) | `salon` | — | NO VIOLATION |
| **V2 — `reginas_mercy` "The Regina's Mercy"** | Fanfare (cap keyword) | `archon`; magnitude `raise_fanfare_cap: 5` on a **rare** (`docs\furina-cards.yaml:804-806`); shipped `"Gain {IfUpgraded:show:15|12} [gold]Encore[/gold]. [gold]Fanfare Cap[/gold] +{FanfareCap:diff()}."` with `FanfareCap = 5m` (`Generated\ReginasMercy.cs:47,53`) | sheet line 37: "+5 at common/uncommon, **+8 at rare**" | **UNVERIFIABLE against the law.** Register itself is clean. The magnitude sentence carries no card-type qualifier, but the rule it says it "restores" was Power-scoped ("every Power grants 5 floor, rares 8", `furina-cards.yaml:26`) and R7 states of non-Powers "this rule does not reach them" (`lint_furina_registers.py:72-73`). The sheet's own note argues the SKILL case (`:805-806`: "A RARE, but a SKILL"). No lint rule reads keyword *amounts* at all. Too ambiguous to adjudicate — recorded, not called a violation. |
| **V3 — `the_sea_is_my_stage` "The Sea Is My Stage"** | Fanfare (floor keyword) | `archon`; magnitude `gain_fanfare_floor: 15` on a **rare Power** (`docs\furina-cards.yaml:725-726`); shipped `"[gold]Fanfare[/gold] +{FanfareFloor:diff()}."` with `FanfareFloor = 15m` (`Generated\TheSeaIsMyStage.cs`) | sheet line 37: "+8 at rare" | **UNVERIFIABLE against the law.** Register and R6 (rare Power) both clean. 15 is nearly double the stated rare rate, but the sheet dates the 15 to the earlier F-A5 pass, not to the compensation pass that wrote line 37 (`:730-733`), and states the card "ALSO earns the rarity grant" on top. The magnitude sentence's scope (new keywords only, or the whole sheet?) is not stated. Recorded, not called a violation. |
| `unheard_confession`, `rapturous_applause` | Fanfare (floor keyword) | `archon`, rare Powers, both `gain_fanfare_floor: 8` | R6 + line 37 | **NO VIOLATION** — the two rows that match the stated rate exactly |
| `lasting_impression` | Fanfare (cap keyword) on a non-Power | `archon`, common skill, `raise_fanfare_cap: 5` | R7: "Non-Powers MAY print 'Fanfare Cap +X'" | NO VIOLATION |

#### Other clauses, run

| Clause | Result | Evidence |
|---|---|---|
| R1 (every card carries a register) | **PASS 82/82** | census `salon 44 / archon 28 / private 10` = 82 |
| R5 (exactly two `focalors` tags, both rare) | **PASS** | `the_sea_is_my_stage` (rare power), `reginas_mercy` (rare skill); grep confirms no third Focalors reference in the pool |
| R6 (`gain_fanfare_floor` only on rare Powers) | **PASS 3/3** | `unheard_confession`, `the_sea_is_my_stage`, `rapturous_applause` — all rare, all `type: power` |
| R7 (every Power prints exactly one Fanfare keyword) | **PASS 17/17** | 17 Powers on the sheet; each has exactly one of `{raise_fanfare_cap, gain_fanfare_floor}`. Confirmed on the **shipped** side too: 17 `Generated\*.cs` descriptions contain a Fanfare keyword clause, matching 1:1. |
| L12 (no direct transient Fanfare grant, sheet **and** engine) | **PASS both surfaces** | no banned op on any sheet row; `tier0.engine.effects.OPS` exposes none of `gain_fanfare / add_fanfare / grant_fanfare / fanfare / give_fanfare` |
| Spelling clause: `"Fanfare Cap"`, never bare `"Cap"` | **PASS — zero bare occurrences** | 32 occurrences of the substring `Cap` across the 84 shipped descriptions; exactly 16 are the prose "Fanfare Cap" and exactly 16 are the `{FanfareCap:diff()}` token. 16 + 16 = 32, so there is **no** prose "Cap" that is not preceded by "Fanfare". Floor-printers say "[gold]Fanfare[/gold] +N" (3 cards). |

#### Mechanical gaps in the law's own coverage (findings, not violations)

> **IDENTIFIER NOTE, 2026-08-06 (housekeeping sweep, Track X).** The `G1`-`G5`
> rows below are the **Track N lore-fidelity** mint: canonical qualified forms
> **`LF-G1`…`LF-G5`**. They are coverage gaps in `lint_furina_registers.py`,
> not [USER] gates, and they are not S4's `S4-G1…G20`. Resolver:
> `docs/registry/identifiers.md` §2.1.

| # | Gap | Evidence | Live today? |
|---|---|---|---|
| G1 | **R4 selects zero cards** — the Encore→`private` binding has no live instance, so Encore's three-way register split is unadjudicable. | `lint_furina_registers.py:136-140` vs all 82 rows | Yes — 21 Encore cards, 0 constrained |
| G2 | **R2 and R3 are mutually exclusive by `elif`, so a card that both reads Fanfare and deploys a member is unsatisfiable and silently exempt from R3.** `if _touches_fanfare(c) and reg != "archon": … elif _applies_member(c) and reg != "salon": …` (`:155-158`). Such a card would need to be both `archon` and `salon`. | `lint_furina_registers.py:155-158` | **No — latent only.** Independently computed: the R2∩R3 intersection is **empty** across all 82 cards. (`endless_waltz` deploys members *and* raises the cap, but `raise_fanfare_cap` is R2-exempt, so no conflict.) |
| G3 | **The lint never reads `docs\furina-upgrades.yaml`.** `SHEET = REPO / "docs" / "furina-cards.yaml"` (`:88`) is the only input. An upgrade delta that added or retargeted a keyword op would not be checked against R6/R7. The sheet itself acknowledges the blind spot at `furina-cards.yaml` (`singer_of_many_waters`): "the upgraded value lives in furina-upgrades.yaml, **which this lint cannot see**." | `lint_furina_registers.py:88`; `docs\furina-upgrades.yaml` | **No live breach.** Audited all 100 upgrade rows: the only keyword-touching deltas are `lasting_impression: {fanfare_cap: +2}` and `the_sea_is_my_stage: {fanfare_floor: +5}`, both bumping a keyword the base card already prints. No upgrade adds a keyword, changes which keyword a card prints, or moves a floor grant onto a non-rare-Power. |
| G4 | **No rule reads keyword *magnitudes*.** The sheet states a rate ("+5 at common/uncommon, +8 at rare", `:37`) that nothing enforces; V2 and V3 are the two rows that deviate from a literal reading and neither is caught. | `lint_furina_registers.py:171-187` checks *which* keyword and *how many*, never *how much* | Yes — 2 deviating rows |
| G5 | **Player-facing markup is inconsistent on exactly the register-bearing resource words**, on five shipped cards, and it is not covered by any lint. Everywhere the codegen emits body text the resource is wrapped (`[gold]Encore[/gold]`, `[gold]Block[/gold]` — e.g. `tools\gen_klee_cards.py:3800,3828,3884`), but the hand-written `POWER_TEXTS` block (`gen_klee_cards.py:552-583`) leaves them bare. Live strings: `CrowdWork.cs:44` "The first time you spend **Encore** each turn"; `StandingOvation.cs` "Whenever you spend **Encore**…" and "…grants 1 **Encore**"; `PitOrchestra.cs:44` "gain {PowerAmount:diff()} **Block**" and "gain 2 **Encore**"; `FortissimoGuard.cs:44` "gain {PowerAmount:diff()} **Block**"; `SwellingOverture.cs` "If you have at least 8 **Encore**". | quoted above | **UNVERIFIABLE against a stated law** — grepped `docs/` for a stated `[gold]` markup convention and found none. Reported as a measured inconsistency (5 cards, 6 strings, all traced to one hand-written codegen block), not as a rule breach. |

---

### N2 counts

**N2a canon claims — 33 adjudicated rows**
- **VERIFIED: 24**
- **CONTRADICTED: 2** — (a) "The Sea Is My Stage" described as a Constellation when canon has it as a Utility Passive; (b) Fanfare "capped at %maxHP" when canon's limit is a flat 300 (+100 during Burst).
- **UNVERIFIABLE: 5** — the "hammer + shield" member roles; the Encore half of the co-op Fanfare coupling; "Center Stage"; "Salon Début" (authored, and the sheet says so); the Italian musical loanwords (no law to test against).
- Non-verdict rows: 2 (Fontaine institutions — **no claim made**, zero occurrences; Fontaine companion cards — **out of surface**).
- Load-bearing: 21 of the 33. Both CONTRADICTED rows are COSMETIC (design comments, not shipped strings). The single most consequential uncitable item — "Center Stage" — is LOAD-BEARING: it is a shipped title and description in `SpotlightCards.cs` and one of the four Fanfare generation sources.

**N2b register-grammar law**
- **Rule violations: 0.** R1 82/82, R2 18/18, R3 9/9, R5 2/2, R6 3/3, R7 17/17 (sheet **and** shipped C#), L12 clean on both surfaces, spelling clause clean (0 bare "Cap" in 84 shipped descriptions). Independently recomputed; the shipped lint agrees (exit 0, "0 register violations").
- **UNVERIFIABLE against the law: 2** (V2 `reginas_mercy` +5 at rare; V3 `the_sea_is_my_stage` +15 at rare) — both against the magnitude sentence, whose scope is not stated and which no rule enforces.
- **Coverage gaps found: 5** (G1 R4 vacuous / Encore unconstrained — *live*; G2 R2/R3 `elif` shadowing — latent, intersection empty; G3 upgrades file out of scope — no live breach; G4 magnitudes unenforced — *live*, 2 rows; G5 player-facing markup inconsistency — 5 cards, no governing law).

**Blocked sources + workarounds**
- `genshin.honeyhunterworld.com` — **HTTP 403 Forbidden** through the proxy on direct WebFetch. Worked around with WebSearch, which surfaces Fandom page *titles and summaries* without fetching the blocked bodies.
- `genshin-impact.fandom.com` — not fetched directly (the brief flags HTTP 402 through the proxy). Every Fandom citation above is a page **title + search-result summary**, which was sufficient to establish existence and classification of a named talent (e.g. "Endless Waltz | Genshin Impact Wiki" returning "Furina's 1st Ascension Passive"). Where a claim needed talent *body* text, it was corroborated against keqingmains.com and progameguides.com instead, both of which returned full content.
- No repo file was modified. Two throwaway analysis scripts were written to the scratchpad only (`dump.py`, `an.py`).

---

## N3 — Kokomi card pool + upgrades + character laws

Audit surface: `docs/kokomi-cards.yaml` (568 lines, 62 rows), `docs/kokomi-upgrades.yaml`,
`docs/kokomi-kickoff-v1.md`, `docs/brief-kokomi-pool-fill.md`, `docs/kokomi-playtest-protocol.md`,
`docs/kokomi-art-pass-requirements.md`, `docs/sprint-kokomi-instrument-log-2026-07-29.md`,
`docs/archive/kokomi-v0.4-plan.md`, `docs/archive/kokomi-v0.4-report.md`,
`docs/inazuma-companions.yaml` (Kokomi-framing lines only), `tier0/DECISIONS.md` R52/R55/R58/R73–R80,
`klee-mod/KleeCode/Cards/Kokomi/` (60 generated + `CeremonialGarment.cs` + `PrincessOfWatatsumi.cs`),
`klee-mod/KleeCode/Cards/KokomiRiderTips.cs`, `klee-mod/KleeCode/Powers/Kokomi*/Kurage*`,
`tier0/tests/test_kokomi.py`, `tools/lint_kokomi_decksize.py`.

READ-ONLY. No repo file was edited, committed or pushed.

PROCEDURAL NOTE (not a finding against the surface): the worktree at
`C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2` reports
`git branch --show-current` = **`findings/track-q`**, not the `findings/track-n` named in the
assignment. Recorded, not changed.

---

### N3a Canon claims

| Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|
| "Kurage's Oath (Elemental Skill, which summons the Bake-Kurage)" | docs/kokomi-cards.yaml:5-6; shipped title `KuragesOath.cs:43` | VERIFIED | LOAD-BEARING (shipped card title) | https://genshin-impact.fandom.com/wiki/Category:Sangonomiya_Kokomi_Talents (via WebSearch: "Elemental Skill 'Kurage's Oath'") |
| "Bake-Kurage" is the summon her Skill fields | kokomi-cards.yaml:5, row `bake_kurage`; `BakeKurage.cs:50` | VERIFIED | LOAD-BEARING (shipped card title + keyword) | ibid.; https://genshin-impact.fandom.com/wiki/Nereid's_Ascension |
| "Nereid's Ascension (Elemental Burst)" | kokomi-cards.yaml:6; `NereidsAscension.cs:53` | VERIFIED | LOAD-BEARING (shipped card title) | https://genshin-impact.fandom.com/wiki/Nereid's_Ascension |
| "Ceremonial Garment (the state it dons)" | kokomi-cards.yaml:6; `CeremonialGarment.cs:75` | VERIFIED — canon: the Burst "rob[es] Kokomi in a Ceremonial Garment made from the flowing waters of Sangonomiya" | LOAD-BEARING (shipped kit card + power) | https://genshin-impact.fandom.com/wiki/Nereid's_Ascension |
| "Tamakushi Casket (1st Ascension passive: casting Nereid's Ascension REFRESHES a fielded Bake-Kurage)" | kokomi-cards.yaml:6-7; kickoff §2.5; hook id `tamakushi_casket` | VERIFIED — canon A1: "if Kokomi's own Bake-Kurage is on the field when she uses Nereid's Ascension, the Bake-Kurage's duration will be refreshed" | LOAD-BEARING (the O4 link the sheet models) | https://genshin-impact.fandom.com/wiki/Tamakushi_Casket |
| "Song of Pearls (4th Ascension passive)" | kokomi-cards.yaml:8; shipped title `EpiphanyOfTheDeep.cs:43` | VERIFIED — canon passive talent. Note the two live labelling conventions: sources call it the "2nd Ascension Passive" (i.e. passive #2), unlocked at Ascension 4; the repo's "4th Ascension" label is the unlock-level convention, not a different talent | LOAD-BEARING (shipped card title) | https://genshin-impact.fandom.com/wiki/Category:Sangonomiya_Kokomi_Talents |
| "Princess of Watatsumi (innate passive)" | kokomi-cards.yaml:8; `PrincessOfWatatsumi.cs:47,62` | VERIFIED — canon Utility Passive (−20% swimming stamina for the party); "innate" is accurate as unlock-timing, the canon label is "Utility Passive" | LOAD-BEARING (shipped Ancient card title) | https://genshin-impact.fandom.com/wiki/Princess_of_Watatsumi |
| C1 "At Water's Edge" | kokomi-cards.yaml:9; shipped basic title `WatersEdge.cs:53` ("Water's Edge") | VERIFIED — C1 | LOAD-BEARING (shipped card title) | https://genshin-impact.fandom.com/wiki/At_Water's_Edge |
| C5 "All Streams Flow to the Sea" | kokomi-cards.yaml:9; `AllStreamsFlow.cs:53` | VERIFIED — canon effect "Increases the level of Kokomi's Elemental Skill by 3", which is the C5 slot | LOAD-BEARING (shipped card title; drove the id-level `riptide_strike` rename) | https://genshin-impact.fandom.com/wiki/Category:Sangonomiya_Kokomi_Constellations |
| C6 "Sango Isshin" | kokomi-cards.yaml:9; `DepthsJudgment.cs:53` | VERIFIED — Ceremonial-Garment-gated Hydro DMG bonus constellation | LOAD-BEARING (shipped card title) | ibid. |
| C3 "The Moon, A Ship O'er the Seas" | kokomi-cards.yaml:11-12 (header correction only) | VERIFIED — C3, +3 to Nereid's Ascension | COSMETIC (header note) | https://genshin-impact.fandom.com/wiki/The_Moon,_A_Ship_O'er_the_Seas |
| C4 "The Moon Overlooks the Waters" | kokomi-cards.yaml:12 | VERIFIED — C4 | COSMETIC | https://genshin-impact.fandom.com/wiki/The_Moon_Overlooks_the_Waters |
| "The Moon's Beauty ... is NOT a Kokomi name and did not corroborate — struck" | kokomi-cards.yaml:10-11; DECISIONS.md:1481 | VERIFIED (consistent) — the constellation and talent category listings return C1/C3/C4/C5/C6 and the three passives above; no source returned "The Moon's Beauty" as a Kokomi name. Negative claim, so the citation is the enumeration, not a refutation | COSMETIC (a struck header entry) | https://genshin-impact.fandom.com/wiki/Category:Sangonomiya_Kokomi_Constellations |
| Beta-era "Kaijin Ceremony" = pre-release name of the Burst | kokomi-cards.yaml:12-13 | VERIFIED — "Kokomi's Elemental Burst is called the Kaijin Ceremony" in pre-release coverage | COSMETIC (a documented trap) | https://progameguides.com/genshin-impact-item/genshin-impact-kokomi-skills-talents-constellations-ascension/ |
| Beta-era "Haworthia Casket" = pre-release name of the A1 passive | kokomi-cards.yaml:12-13 | VERIFIED — "her first talent is called Haworthia Casket, which refreshes the Bake-Kurage's duration" | COSMETIC | ibid. |
| "Bake-Kurage in the game deals Hydro DMG *and heals nearby characters at set intervals*" | kokomi-cards.yaml:218-219 (the stated justification for `kurages_oath`'s 12 Block) | VERIFIED — canon: "Bake-Kurage deals Hydro DMG to surrounding opponents and heals nearby active characters at fixed intervals, with healing based on Kokomi's Max HP" | LOAD-BEARING (the canon warrant for a shipped Rare/common power) | https://genshin-impact.fandom.com/wiki/Nereid's_Ascension ; https://keqingmains.com/kokomi/ |
| "Element: hydro \| Cadence: CATALYST" | kokomi-cards.yaml:51 | VERIFIED — Hydro, 5★, Catalyst | LOAD-BEARING (a shipped cadence rule) | genshin-db `sangonomiyakokomi.json` (raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/characters/) |
| "the −100% crit trade translated" (basis of Flawless Strategy / LAW 3) | docs/kokomi-kickoff-v1.md:56-60 | VERIFIED — Kokomi has 25% Healing Bonus and a 100% CRIT Rate decrease | LOAD-BEARING (the canon warrant for the Strength→Charge conversion) | https://keqingmains.com/kokomi/ ; https://genshin-impact.fandom.com/wiki/Nereid's_Ascension |
| "Flawless Strategy" as the name of that trait | kickoff §1.3; kokomi-cards.yaml:34 ("LAW 3 (Flawless Strategy)") | UNVERIFIABLE — no Genshin talent, passive or constellation by that name surfaced in the talent/constellation category searches. The doc labels it "(the Genshin twist)", i.e. it does not itself assert the string as canon | LOAD-BEARING (the law's name) | searched: Category:Sangonomiya_Kokomi_Talents, Category:Sangonomiya_Kokomi_Constellations, genshin-db character JSON |
| "Sangonomiya Kokomi — Hydro. General and priest of Watatsumi Island." | kickoff §1 line 40 | VERIFIED — canon title "The Divine Priestess of Watatsumi Island", responsible for "all of the island's affairs"; Watatsumi is "ruled autonomously by the Sangonomiya Clan, currently led by Kokomi", and she leads the resistance army | LOAD-BEARING (identity declaration) | genshin-db `sangonomiyakokomi.json`; https://genshin-impact.fandom.com/wiki/Watatsumi_Island |
| Relic display name "Pearl of Wisdom" | tier0/DECISIONS.md R55 (:1462-1468) | VERIFIED — "Pearl of Wisdom" is her canon character title | LOAD-BEARING (shipped relic name) | genshin-db `sangonomiyakokomi.json` (`"title": "Pearl of Wisdom"`) |
| Sangonomiya Shrine / Watatsumi Island / Altar as real locations | docs/kokomi-art-pass-requirements.md:296; playtest-protocol:35 | VERIFIED — Sangonomiya Shrine is canonically the resistance army's base | COSMETIC (art sourcing) | https://genshin-impact.fandom.com/wiki/Sangonomiya_Shrine |
| Kokomi's kit scales on HP ("lore: her HP pool, and stability wants headroom") | kickoff §6.8 | VERIFIED — Bake-Kurage healing is Max-HP-based; Song of Pearls converts Healing Bonus into a Max-HP-based Normal/Charged DMG bonus | LOAD-BEARING (the statline's stated lore warrant) | https://genshin-impact.fandom.com/wiki/Category:Sangonomiya_Kokomi_Talents |
| "Enkanomiya, the sunless realm the Watatsumi people fled" | kokomi-cards.yaml:253-254 (the `before_sun_and_moon` NAME note) | SPLIT. "Enkanomiya = sunless subterranean realm and the origin of the Watatsumi people": VERIFIED — "The inhabitants of Watatsumi Island once lived in Enkanomiya, at the bottom of the sea." The verb "**fled**": UNVERIFIABLE — the sources returned describe them as *brought up* by Orobashi ("it was only by the grace of the god Orobashi bringing them up to the surface"), not as fleeing | LOAD-BEARING (the sole stated canon warrant for a shipped Uncommon power's name) | https://genshin-impact.fandom.com/wiki/Enkanomiya ; https://genshin-impact.fandom.com/wiki/Watatsumi_Island |
| "its history is the forbidden knowledge she is heir to, and 'before sun and moon' is when it was written" | kokomi-cards.yaml:253-254 | UNVERIFIABLE — no source returned attributes Enkanomiya's history to Kokomi as inherited forbidden knowledge, nor "before sun and moon" as a period label. Searched: Enkanomiya wiki, Watatsumi Island wiki, Kokomi profile | LOAD-BEARING (shipped card name's justification) | searched, no corroboration |
| Orobashi | — | NO CLAIM PRESENT. `grep -rni "orobashi"` over `docs/` returns zero hits; the serpent-god who founded Watatsumi is not named anywhere in the Kokomi surface. Recorded as an absence, not a defect | n/a | grep, this worktree |
| "Riptide is Tartaglia's signature mechanic, a cross-character collision inside Genshin" | docs/archive/kokomi-v0.4-plan.md:~140; DECISIONS.md R55 | VERIFIED — "Tartaglia has a unique mechanic known as Riptide" | LOAD-BEARING (drove the one id-level rename in the pool) | https://genshin-impact.fandom.com/wiki/Tartaglia |
| "jade is Liyue-coded; Watatsumi is coral and pearl" | DECISIONS.md R55; kokomi-cards.yaml `jade_bulwark` → "Pearl Bulwark" | UNVERIFIABLE as an aesthetic-coding claim. Closest corroboration: her ascension material is the **Sango Pearl** (sango = coral) | LOAD-BEARING (shipped card title) | https://www.sportskeeda.com/esports/kokomi-s-ascension-materials-genshin-impact-spectral-nucleus-sango-pearl-locations |
| "Watatsumi's divers, on the nose" (`pearl_diver`) | kokomi-cards.yaml:289 | UNVERIFIABLE — no source returned establishes pearl-diving as a Watatsumi occupation. Searched: Watatsumi Island wiki, Sangonomiya Shrine wiki | LOAD-BEARING (shipped card title flavor) | searched, no corroboration |
| The Vision Hunt Decree drove Watatsumi into armed resistance ("Watatsumi bled for the Vision Hunt") | docs/inazuma-companions.yaml:84 | VERIFIED — "the Watatsumi Army rose up in opposition to the decree"; Sangonomiya Shrine is "the base for the resistance army led by Sangonomiya Kokomi" | LOAD-BEARING (framing for a ratified gloss) | https://genshin-impact.fandom.com/wiki/Watatsumi_Island ; https://genshin-impact.fandom.com/wiki/Sangonomiya_Shrine |
| Kujou Sara "was the OPPOSING field commander and now answers to the strategist who beat her" | docs/inazuma-companions.yaml:16 | VERIFIED — at Nazuchi Beach "Kujou Sara, the Shogun's right-hand woman, personally led the pursuit"; "the sudden ambush causes Kujou Sara to order a retreat, giving the victory to Kokomi and Watatsumi Island" | LOAD-BEARING (a ratified framing note) | https://genshin-impact.fandom.com/wiki/Nazuchi_Beach ; https://game8.co/games/Genshin-Impact/archives/370739 |
| Gorou — "4★, Geo, buffer/general — the literal adjutant"; "His DEF-banner identity" | kickoff §4; inazuma-companions.yaml:21-30 | VERIFIED for 4★/Geo/general-of-the-Watatsumi-Army and the DEF-scaling banner kit. "adjutant" is the repo's framing of his relation to Kokomi, not a canon title — canon calls him the *general* of the Watatsumi Army | LOAD-BEARING (companion identity) | https://genshin-impact.fandom.com/wiki/Gorou |
| Sayu — "4★, Anemo, healer", Shuumatsuban | kickoff §4; inazuma-companions.yaml:14 | VERIFIED — Anemo, affiliated with the Shuumatsuban | LOAD-BEARING | https://www.sportskeeda.com/esports/all-genshin-impact-characters-affiliations |
| Kuki Shinobu — "4★, Electro, healer; her canonical self-HP cost" | kickoff §4 line ~192; inazuma-companions.yaml:8-9,45 | VERIFIED — Sanctifying Ring "creates a Grass Ring of Sanctification at the cost of part of her HP" (30% of current HP, floored at 20%), healing based on her Max HP; she is Electro and deputy leader of the Arataki Gang | LOAD-BEARING (the errata's canon premise) | https://genshin-impact.fandom.com/wiki/Sanctifying_Ring ; https://keqingmains.com/q/shinobu-quickguide/ |
| Thoma — Pyro, shield/buffer, Yashiro Commission | kickoff §4; inazuma-companions.yaml:57 | VERIFIED — Thoma is Pyro and "works for the Yashiro Commission" | COSMETIC (companion framing) | https://www.sportskeeda.com/esports/all-genshin-impact-characters-affiliations |
| Itto — 5★, Arataki Gang, "taunt/bruiser" | kickoff §4; inazuma-companions.yaml (Itto section) | SPLIT. 5★ / Arataki Gang: VERIFIED (Shinobu is "Deputy Leader of Arataki Gang", the gang is Itto's). "taunt": UNVERIFIABLE — searched Itto's kit; the searches returned no taunt-mechanic text | COSMETIC | https://www.sportskeeda.com/esports/all-genshin-impact-characters-affiliations |
| Kazuha — "Inazuma-born" | kickoff §4 line ~198 | VERIFIED — canonically an Inazuman wandering samurai; appears with Kokomi and Beidou at the Nazuchi Beach relief | COSMETIC (a "later scope" note) | https://genshin-impact.fandom.com/wiki/Nazuchi_Beach ; https://tvtropes.org/pmwiki/pmwiki.php/Characters/GenshinImpactInazuma |
| "Yun Jin(?—Liyue, out)" | kickoff §4 line ~199 | VERIFIED — Yun Jin is a Liyue character, correctly excluded from an Inazuma pool | COSMETIC | https://www.sportskeeda.com/esports/all-genshin-impact-characters-affiliations |
| "Musou no Hitotachi is the Vision Hunt's execution strike" | docs/archive/kokomi-v0.4-plan.md (Raiden gloss); inazuma-companions.yaml:84-86,113-118 | VERIFIED — Musou no Hitotachi "could only be witnessed when she administered 'divine punishment'"; after Kazuha's friend "challenge[d] the enforcers of the Vision Hunt Decree to a duel before the throne ... the Shogun executed him with the Musou no Hitotachi" | LOAD-BEARING (the ratified gloss's canon premise; shipped companion card title) | https://genshin-impact.fandom.com/wiki/Kazuha's_Friend ; https://genshin-impact.fandom.com/wiki/Vision_Hunt_Decree |
| "Lorewise Kokomi and the Shogun are OPPOSED" | inazuma-companions.yaml:84 | VERIFIED — the Decree "drove hostility between the Sangonomiya Clan and the followers of the Raiden Shogun to an all-time high" | LOAD-BEARING | https://genshin-impact.fandom.com/wiki/Watatsumi_Island |
| "the peace's crowning proof — the Shogun's blade defends Watatsumi now" (post-Decree reconciliation) | DECISIONS.md R55; inazuma-companions.yaml:113-118 | UNVERIFIABLE — a post-canon authored gloss. The doc labels it as a gloss and a [USER] ruling, not as reported canon; the *precondition* (Decree rescinded, hostilities ended) is canon but the framing is not sourced | LOAD-BEARING (a ratified framing) | searched: Vision Hunt Decree wiki, Watatsumi Island wiki |
| "the pool is the peace, not her army": the roster spans resistance (Gorou) / Shogunate (Sara, Raiden) / Yashiro (Thoma, Sayu's Shuumatsuban) / Arataki Gang (Itto, Shinobu) | inazuma-companions.yaml:12-19 | VERIFIED as a factional mapping — each affiliation above is individually corroborated | COSMETIC (framing note) | https://www.sportskeeda.com/esports/all-genshin-impact-characters-affiliations ; Gorou/Shinobu wiki pages above |
| Kokomi's social exhaustion: the "drained introvert" characterization behind "A Moment Alone" / "Daydream of a Quiet Life" | DECISIONS.md R55 (:1458-1461); kokomi-cards.yaml rows `moon_signal`, `undertow_shuffle` | VERIFIED — "Socializing with others is in fact a most tiring task for her ... forcing herself to do things she holds little love for is a serious drain on her energy reserves, leaving her feeling quite exhausted"; she runs an explicit personal "energy" system and reverts to "an ordinary homebody" when it empties | LOAD-BEARING (shipped card titles) | https://genshin-impact.fandom.com/wiki/Sangonomiya_Kokomi/Profile ; https://gameriv.com/genshin-impact-2-2-kokomi-talents-story-voice-lines-hobbies-favorite-food-and-more-revealed/ |
| "the secret **novel** reader" (behind "Stolen Chapter") | DECISIONS.md R55 (:1458-1460); kokomi-cards.yaml row `tide_reading` | UNVERIFIABLE as stated — canon returns *strategy* reading, not novels: "Kokomi's favorite pastime is to read books on **strategy** in a quiet place ... face buried in her military strategy books." No source returned attests a novel-reading habit or a concealed/"stolen" one. Searched: Kokomi/Profile, voice-over compilations, GameRiv hobbies writeup | LOAD-BEARING (shipped card title "Stolen Chapter") | https://genshin-impact.fandom.com/wiki/Sangonomiya_Kokomi/Profile |
| "the strategist reads the field" / Kokomi-as-tactician framing | kokomi-cards.yaml:139, 408; inazuma-companions.yaml:16 | VERIFIED — the strategy-reading habit above, plus the Nazuchi Beach hidden-reserve ambush credited to her | LOAD-BEARING (identity framing) | https://genshin-impact.fandom.com/wiki/Sangonomiya_Kokomi/Profile ; https://game8.co/games/Genshin-Impact/archives/370739 |
| Her "healer" party role | kickoff §5 | VERIFIED — Bake-Kurage and the Garment both heal; she is canonically a healer | LOAD-BEARING (co-op posture) | https://genshin-impact.fandom.com/wiki/Nereid's_Ascension |

---

### N3b Character-law compliance

#### LAW A — the Exhaust-as-rotation phrasing law

**Primary (ratified) registration — `tier0/DECISIONS.md:1433-1439`, verbatim:**

> - **VOICE LAW (binding for the sheet and every future card face):** Exhaust
>   in Kokomi's fiction is ROTATION, never sacrifice. Units rotate off the
>   field rested and whole; Charge is the strategic position each executed
>   maneuver buys. Her doctrine is minimal casualties, and the sacrifice voice
>   is the one reading that breaks the character. `tactical_recall` is the
>   exemplar; `grand_conscription`'s "the army becomes fuel" was the marked
>   counter-example and is rewritten.

**Sheet restatement — `docs/kokomi-cards.yaml:22-27`, verbatim:**

> \# VOICE LAW (v0.4 §3): Exhaust in her fiction is ROTATION, never sacrifice. Units rotate off the field rested and
> \#   whole; Charge is the strategic position each executed maneuver buys. Her doctrine is minimal casualties — the
> \#   sacrifice voice is the one reading that breaks the character. tactical_recall is the exemplar; the old
> \#   grand_conscription line ("the army becomes fuel") was the marked counter-example and is fixed below.
> \#   Forced service is Shogunate behaviour and the resistance were volunteers, so the display family is
> \#   Muster/Enlist/Rally; the internal op name `conscript` stays.

**Origin — `docs/archive/kokomi-v0.4-plan.md:101-107`, verbatim:**

> **The rotation reframe (voice law for the sheet).** Exhaust in her fiction
> is ROTATION, never sacrifice: units rotate off the field, rested and
> whole; Charge is the strategic position each executed maneuver buys. Her
> doctrine is minimal casualties; the sacrifice voice is the one reading
> that breaks the character. Sweep every comment and future card face for it
> (`grand_conscription`'s "the army becomes fuel" is the marked example).
> `tactical_recall` is the exemplar voice.

**Sharpest adjudicable restatement — `docs/kokomi-playtest-protocol.md:169-171`, verbatim:**

> Binding voice law (R55): her exhaust is **rotation** — troops rotating off the
> line — and never sacrifice, burning, or spending. The display family is
> Muster / Enlist / Rally.

Adjudication standard used below: the enumerated banned registers are **sacrifice, burning,
spending** (protocol) plus the marked "fuel" counter-example (R55). Anything outside those
registers is recorded UNVERIFIABLE-against-law, not a violation. Scope per the plan: "every
comment and future card face".

#### LAW B — the no-self-damage law

**Primary registration — `docs/kokomi-kickoff-v1.md:47-50`, verbatim:**

> 1. No self-damage anywhere in her kit or personal pool. Her risk axis is
>    tempo and card economy exclusively. The moment a Kokomi card costs HP,
>    the Furina boundary blurs. (Extends to shared-pool errata below:
>    Shinobu.)

**Sheet restatement — `docs/kokomi-cards.yaml:28-29`, verbatim:**

> \# Identity (kickoff §1): Kokomi converts card economy into damage. She pays in cards, never in HP.
> \#   LAW 1: no self-damage anywhere in this pool (grep-clean: no {target: self} damage op may ever appear here).

**Shared-pool errata — `docs/inazuma-companions.yaml:8-9`, verbatim:**

> \# ERRATA NOTE (kickoff §4, on the record so it isn't "rediscovered"): Kuki Shinobu's canonical self-HP cost is DROPPED
> \# per Kokomi character law 1 (no self-damage in her kit or shared-pool errata). Her cards are authored costless-to-HP.

#### Compliance table

| Card | Law | Shipped text | Verdict |
|---|---|---|---|
| All 62 rows in `docs/kokomi-cards.yaml` (60 draftable + `ceremonial_garment` kit + Ancient) | LAW B | `grep -n "target: self"` returns 7 hits, **all** `apply_power` (`kurage_ward`, `kurage_amp`, `feel_no_pain`, `metallicize`, `ceremonial_garment`, `prevent_exhaust_ward`, `dark_embrace`). Zero `{op: damage, target: self}` | COMPLIANT — the sheet's own "grep-clean" assertion holds |
| `klee-mod/KleeCode/Cards/Kokomi/**` (60 generated + `CeremonialGarment.cs` + `PrincessOfWatatsumi.cs`) and `Powers/{KokomiConscript,KokomiResources,KuragePowers,KitBurst}.cs` | LAW B | `grep -rn "LoseHp\|LoseHP\|LoseHealth\|DamagePlayer\|SelfDamage\|TakeDamage\|HpLoss\|CurrentHp -"` returns **zero hits** across all of them | COMPLIANT |
| `shinobu_sanctifying_ring`, `shinobu_grass_ring_bond`, `shinobu_thundergrust` (`docs/inazuma-companions.yaml:46-55`) | LAW B (errata clause) | `{op: damage, amount: 3, target: all_enemies}, {op: block, amount: 4}` / `{op: block, amount: 4}` / `{op: damage, amount: 7, target: enemy}` — no HP cost on any row | COMPLIANT — the errata is honoured in the shipped rows |
| *(enforcement status, LAW B)* | LAW B | LAW 4 (deck-size) ships with `tools/lint_kokomi_decksize.py` and is named in-sheet as machine-checked. LAW B has **no lint** (`tools/` has only `lint_kokomi_decksize.py` for this character) and **no test**: `tier0/tests/test_kokomi.py` contains no assertion naming self-damage or HP loss across its 40+ tests | MECHANICAL FINDING, LOAD-BEARING — a stated "grep-clean" invariant with no gate. Recorded as a fact about coverage, not as a defect in any card |
| All 60 generated C# `("title", …)` / `("description", …)` strings + `CeremonialGarment.cs:75-81` + `PrincessOfWatatsumi.cs:62-66` + the three keyword tips in `KokomiRiderTips.cs` (Muster / Kurage pulse / Garment) | LAW A | Full sweep for `sacrifice`, `burn`, `fuel`, `spend`, `destroy`, `consume`, `blood`: **zero hits**. Exhaust is printed only as the engine keyword (`[gold]Exhaust[/gold]`, `[gold]Exhausts[/gold]`), and the muster family ships as `[gold]Muster N[/gold]: transform N cards in your hand into random Inazuma [gold]Companion[/gold] cards…` | COMPLIANT — every player-facing string on the surface clears the law |
| `grand_conscription` / "General Muster of Watatsumi" | LAW A | Sheet comment now: `The full muster: three call-ups in one order, and the order itself is stood down once answered. The Commander's rare swing — the hand becomes an army, and the army rotates off the field having WON its position. VOICE LAW (v0.4 §3): rotation, never sacrifice.` Shipped face: `[gold]Muster[/gold] 3. Gain 2 [gold]Charge[/gold].` | COMPLIANT — the marked counter-example ("the army becomes fuel") is gone from both sheet and shipped text |
| `tactical_retreat` / "Tactical Retreat" | LAW A | Shipped: `Draw {Cards:diff()} card{Cards:plural:\|s}. Discard {Discards:diff()} random card(s).` Sheet: `v0.4 RENAME ([USER]): "Recall" -> "Retreat". A retreat is a maneuver that PRESERVES the unit, which is the voice law exactly` | COMPLIANT (and the law's named exemplar) — **but see the dangling-pointer finding below** |
| *(the law's own text)* — `tier0/DECISIONS.md:1437` and `docs/kokomi-cards.yaml:24` | LAW A | Both name the exemplar as `` `tactical_recall` ``. That id does not exist: `docs/archive/kokomi-v0.4-report.md:368` records `**tactical_recall → tactical_retreat** (id-level)`, and the sheet, the upgrade file, the C# class and `manifest.json` all carry `tactical_retreat`. `grep -rn "tactical_recall"` over the tree returns only the law texts themselves plus two archive/history lines | MECHANICAL FINDING, LOAD-BEARING — the registered law's exemplar pointer is dangling. No wording proposed |
| `votive_offering` / "Votive Offering" | LAW A | Sheet comment (`kokomi-cards.yaml:154-155`): `Burn a card for safety: Defend-grade Block whose rider is fuel with the Casket, pure loss without a payoff — the priest lane's honest price.` Shipped face is clean | DEPARTURE from registered phrasing (comment only) — hits two enumerated registers, "burn" and "fuel". COSMETIC (non-player-facing) |
| `cleansing_tide` / "Cleansing Tide" | LAW A | Sheet comment (:167): `The big burn: two cards for a real wall. Double fuel with the Casket; steep deck cost without it.` Shipped face clean | DEPARTURE (comment only) — "burn", "fuel". COSMETIC |
| `pearl_diver` / "Pearl Diver" | LAW A | Sheet comment (:288): `The free fuel line: burn one, bank 3 total (2 line + 1 funnel).` Shipped face clean | DEPARTURE (comment only) — "burn", "fuel". COSMETIC |
| `waterspout` / "Waterspout" | LAW A | Sheet comment (:163-164): `Self-consuming swing: v0.3 7 -> 10 — a card of the deck-as-HP-bar is a real price and must buy a real hit (the v0.2 world priced the burn at +1 damage over a plain swing).` Shipped face clean | DEPARTURE (comment only) — "burn"; "self-consuming"/"deck-as-HP-bar" are outside the enumerated registers → that half is UNVERIFIABLE-against-law. COSMETIC |
| `vow_of_tides` / "Vow of the Tides" | LAW A | Sheet comment (:279-280): `The self-consuming wave: waterspout's grammar aimed wide. Its burn is itself a Charge, which is the whole priest bargain in one card.` Shipped face clean | DEPARTURE (comment only) — "burn". COSMETIC |
| `exposing_current` / "Exposing Current" | LAW A | Sheet comment (:408): `one self-consuming read of the enemy line (its burn is a Charge)` | DEPARTURE (comment only) — "burn". COSMETIC |
| `sango_prayer` / "Sango Prayer" | LAW A | Sheet comment (:541): `a debuff earned on an Exhaust piece (Rare, one cast per fight, and its burn is itself a Charge)` | DEPARTURE (comment only) — "burn". COSMETIC |
| `communion_of_tides` / "Communion of Tides" | LAW A | Sheet comment (:392): `Burn one, see two: the lane-bridge card (priest fuel, assist velocity).` | DEPARTURE (comment only) — "burn", "fuel". COSMETIC |
| `moonlit_offering` / "Moonlit Offering" | LAW A | Sheet comment (:458-460): `The old note called this "the sheet's clearest statement that her deck IS her resource bar". That statement now has no card carrying it` | UNVERIFIABLE-against-law — "resource bar" is not an enumerated register, and the line is quoting a retired note. COSMETIC |
| `ebb_tide` / "Ebb Tide" | LAW A | Sheet comment (:322-327): `the chosen exhaust turns the churn into Charge and Burst … you feed the meter the card you least want, which is the whole fantasy of a rotation lane` | UNVERIFIABLE-against-law — "feed the meter" is fuel-adjacent but not an enumerated register, and the same sentence invokes the rotation lane. COSMETIC |
| `votive_offering`, `moonlit_offering`, `prayer_to_the_moon`, `sango_prayer` (titles) | LAW A | Shipped titles: `Votive Offering`, `Moonlit Offering`, `Prayer to the Moon`, `Sango Prayer` | UNVERIFIABLE-against-law — "offering" is a giving-up register not enumerated by the law (which names sacrifice / burning / spending / fuel). LOAD-BEARING strings, recorded without a violation call |
| `docs/kokomi-kickoff-v1.md:75-79` (the decision loop) | LAW A | `> Every card kept is engine; every card burned is Charge.` and `Cycle the engine … or **spend the deck down** for Exhaust payoffs. The deck is her second HP bar — defense literally **spends** future draws.` | DEPARTURE from registered phrasing — "burned", "spend"×2. MITIGATION ON RECORD: the kickoff is dated 2026-07-23 and is headed `archived verbatim per the no-chat-side-only-artifacts rule`; the voice law is R55, 2026-07-26. COSMETIC (archived doc), but it is the document `kokomi-cards.yaml:28` cites as the identity source |
| `docs/kokomi-kickoff-v1.md:129-131` (§2.3 differentiation from Furina) | LAW A | `Kokomi's is transformative and consumptive (conscripts existing cards, **burns them as fuel**; the payoff routes through her own finisher).` | DEPARTURE — this is verbatim the marked counter-example register ("the army becomes fuel"), surviving in the kickoff. Same archived-verbatim mitigation as above. COSMETIC (non-player-facing) |
| `docs/kokomi-cards.yaml:2` header vs. R55 | LAW A | Header line 2 dates the sheet `v0.2 SHEET PASS`; the voice-law block (:22-27) is present and current | COMPLIANT — no finding, recorded to show the sheet header carries the law |
| `docs/inazuma-companions.yaml:84-86` (Raiden section header) vs. `:113-118` (the card's ratified gloss) | LAW A neighbourhood / ratified-gloss integrity | Header still reads: `The card is therefore the DOCTRINE, not the woman — one borrowed instant of Musou, and **the resistance leader's bitterest irony that it works**.` Twenty-eight lines below, the ratified gloss reads: `The retired framing called this 'the bitterest irony' … That reading breaks the peace the whole roster is built on … **Never write the irony version again.**` | MECHANICAL FINDING, LOAD-BEARING — the retired framing survives verbatim in the same file that forbids it. Not a LAW A violation (the law is about exhaust voice); it is a ratified-ruling contradiction inside one file. No replacement wording proposed |

---

### N3 counts

**Canon claims (N3a): 41 rows.**
- VERIFIED: 30 (including 3 rows verified in part, where the split is recorded in-cell)
- CONTRADICTED: 0
- UNVERIFIABLE: 10 (`Flawless Strategy` as a canon name; "fled" in the Enkanomiya line; the forbidden-knowledge/"before sun and moon" gloss; jade-vs-coral aesthetic coding; "Watatsumi's divers"; Itto "taunt"; the reconciliation gloss; "the secret novel reader"; plus the two split rows' unverifiable halves)
- Absences recorded (no claim to audit): 1 (Orobashi is never named in the Kokomi surface)
- Load-bearing: 29 · Cosmetic: 12

**Character-law compliance (N3b): 23 rows.**
- COMPLIANT: 8 (both laws clear on every shipped player-facing string and every shipped mechanic)
- MECHANICAL FINDINGS: 3 — LAW B has no lint and no test; the registered LAW A text names a nonexistent id `tactical_recall`; `inazuma-companions.yaml` retains the retired "bitterest irony" gloss it forbids
- DEPARTURES from registered phrasing: 10 (all in non-player-facing sheet/kickoff comments; 8 in `kokomi-cards.yaml`, 2 in the archived kickoff)
- UNVERIFIABLE-against-law: 3 (`moonlit_offering` "resource bar"; `ebb_tide` "feed the meter"; the four "Offering/Prayer" titles as one row)
- LAW B violations: 0 · LAW A violations in shipped player-facing text: 0

**Blocked sources and workarounds.**
- The Genshin Fandom wiki was **not fetched directly** — the assignment records HTTP 402 through the WebFetch proxy, so no `WebFetch` call was made against `genshin-impact.fandom.com`. Workaround: all Fandom-sourced facts above were obtained through `WebSearch`, which returns Fandom article content in its result summaries; the Fandom URLs are cited as the underlying source of those quotes, not as pages I retrieved.
- `raw.githubusercontent.com/theBowja/genshin-db/.../sangonomiyakokomi.json` **fetched successfully** and supplied the character profile fields (title "Pearl of Wisdom", "The Divine Priestess of Watatsumi Island", Inazuma / Hydro / Catalyst / 5★ / constellation "Dracaena Somnolenta"). Limitation found: that JSON carries ascension-material costs but **no talent or passive text**, so every talent/constellation/passive claim was verified via `WebSearch` instead.
- Secondary corroboration used where a single source felt thin: keqingmains.com (Kokomi and Shinobu guides), game8.co, progameguides.com (beta-name claims), sportskeeda.com (affiliation table), tvtropes Inazuma/Watatsumi character pages.
- One search returned nothing usable and its claim is recorded UNVERIFIABLE rather than argued: pearl-diving as a Watatsumi occupation.

---

## N4 — Companion sheets (all nations, incl. Fontaine Rares drafts)

**Surface swept.** Globbed `docs/` and `review/` for every `*companion*` / nation sheet. Sheets that exist: `docs/mondstadt-companions.yaml`, `docs/inazuma-companions.yaml`, `docs/fontaine-companions.yaml`. Supporting drafts/logs: `docs/fontaine-rares-banner-sprint-log.md`, `docs/companion-value-vs-colorless-study.md`, `docs/archive/companion-lore-errata.md`, `docs/archive/companion-art-plan-addendum.md`, `docs/archive/shop-companion-channel-*.md`. **No Liyue, Sumeru, Snezhnaya or Natlan companion sheet exists** — `docs/zhongli-dossier-2026-08-05.md` is a findings-only canon-kit dossier for a *playable* slot-4 candidate and contains zero companion entries (verified by grep: its only companion references are citations back into the three sheets above). Shipped player-facing strings live in `klee-mod/KleeCode/Cards/Generated/*.cs` (`Localization` title + `Nation` + `Star` + `CompanionElement`); those are the LOAD-BEARING surface.

**Method.** Element / weapon / region / rarity / title / affiliation corroborated against genshin-db's English game-text dump (`raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/{characters,talents,constellations}/*.json`), which is a direct dump of the game's own strings. Ability-name claims checked against the `talents/` and `constellations/` files for the same character.

**Blocked sources + workarounds.** `genshin-impact.fandom.com` returns **HTTP 402 Payment Required** through the fetch proxy (re-confirmed this session on `/wiki/Neuvillette`); the same block is already on the record at `docs/zhongli-dossier-2026-08-05.md:24-26`. Workaround used: genshin-db raw JSON for all first-party game text; WebSearch snippet extraction of Fandom for the one org-structure claim (Shuumatsuban↔Yashiro) that game text does not carry.

---

### Mondstadt — `docs/mondstadt-companions.yaml`

| Companion | Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|
| Dahlia | 4-star, Hydro, Mondstadt | `mondstadt-companions.yaml:18-21`; `DahliaSacramentalShower.cs:37,41,44` | VERIFIED | LOAD-BEARING | genshin-db `characters/dahlia.json`: rarity 4, Hydro, region Mondstadt |
| Dahlia | "Church of Favonius deacon" | `docs/archive/companion-lore-errata.md:3` | VERIFIED | COSMETIC | genshin-db: affiliation "Church of Favonius"; description "Deacon of the Church of Favonius…" |
| Dahlia | Card name "Sacramental Shower" | `mondstadt-companions.yaml:18`; shipped title in `DahliaSacramentalShower.cs:59` | VERIFIED | LOAD-BEARING | genshin-db `talents/dahlia.json`: "Sacramental Shower" is the object summoned by his Elemental Skill *Immersive Ordinance* |
| Dahlia | Card name "Favonian Favor" | `mondstadt-companions.yaml:20` | VERIFIED | LOAD-BEARING | genshin-db `talents/dahlia.json`: "Favonian Favor" is the Burst (*Radiant Psalter*) buff effect |
| Dahlia | Errata: "his Skill zone deals damage + applies Hydro; his Burst grants a shield" | `docs/archive/companion-lore-errata.md:3` | VERIFIED | COSMETIC | genshin-db `talents/dahlia.json`: skill deals AoE Hydro DMG on contact; burst grants "Shield of Sacred Favor" scaling on Max HP |
| Dahlia | "Dahlia's canonical weakness is poor Hydro application" | `docs/archive/companion-lore-errata.md:11` | UNVERIFIABLE | COSMETIC | Searched genshin-db `characters/dahlia.json` + `talents/dahlia.json`: no application-frequency (ICD/gauge) data in the dump; Fandom gauge pages 402-blocked |
| Fischl | 4-star, Electro, Mondstadt | `mondstadt-companions.yaml:22-25`; `FischlNightrider.cs` | VERIFIED | LOAD-BEARING | genshin-db `characters/fischl.json` |
| Fischl | "Nightrider" is her ability; "Oz" is her night raven | `mondstadt-companions.yaml:22,24` | VERIFIED | LOAD-BEARING | genshin-db `talents/fischl.json`: Elemental Skill "Nightrider"; Oz described as "night raven forged of darkness and lightning" |
| Barbara | 4-star, Hydro, Mondstadt | `mondstadt-companions.yaml:28-32` | VERIFIED | LOAD-BEARING | genshin-db `characters/barbara.json` |
| Barbara | Card name "Soothing Melody" | `mondstadt-companions.yaml:28` (shipped title) | UNVERIFIABLE | LOAD-BEARING | No Barbara talent or constellation by that name. genshin-db `talents/barbara.json`: NA "Whisper of Water", Skill "Let the Show Begin♪", Burst "Shining Miracle♪", passives Glorious Season / Encore / With My Whole Heart♪; the in-skill field term is "**Melody Loop**", not "Soothing Melody" |
| Barbara | Card name "Shining Idol" | `mondstadt-companions.yaml:31` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `characters/barbara.json`: **title** is exactly "Shining Idol" (it is her character title, not an ability name) |
| Sucrose | 4-star, Anemo, Mondstadt, alchemist | `mondstadt-companions.yaml:34-47` | VERIFIED | LOAD-BEARING | genshin-db `characters/sucrose.json`: 4★ Anemo, Knights of Favonius, "An alchemist filled with curiosity…" |
| Sucrose | "Wind Spirit Creation", "Astable Anemohypostasis", "Catalyst Conversion" are her ability names | `mondstadt-companions.yaml:34,36,46` | VERIFIED | LOAD-BEARING | genshin-db `talents/sucrose.json`: NA "Wind Spirit Creation"; Skill "Astable Anemohypostasis Creation - 6308"; passive 1 "Catalyst Conversion" |
| Bennett | 4-star, Pyro, Mondstadt; "Passion Overload" + "Fantastic Voyage" | `mondstadt-companions.yaml:57-61` | VERIFIED | LOAD-BEARING | genshin-db `characters/bennett.json`; `talents/bennett.json`: Skill "Passion Overload", Burst "Fantastic Voyage" |
| Kaeya | 4-star, Cryo, Mondstadt; "Frostgnaw" | `mondstadt-companions.yaml:65-66` | VERIFIED | LOAD-BEARING | genshin-db `characters/kaeya.json`; `talents/kaeya.json`: Skill "Frostgnaw" |
| Diona | 4-star, Cryo, Mondstadt; "Icy Paws" | `mondstadt-companions.yaml:67-68` | VERIFIED | LOAD-BEARING | genshin-db `characters/diona.json`; `talents/diona.json`: Skill "Icy Paws" |
| Albedo | 5-star, Geo, Mondstadt; "Solar Isotoma" | `mondstadt-companions.yaml:71-72` | VERIFIED | LOAD-BEARING | genshin-db `characters/albedo.json`; `talents/albedo.json`: Skill "Abiogenesis: Solar Isotoma" |
| Albedo | Solar Isotoma is a Geo *construct/field* that pays out on damage dealt inside it | `mondstadt-companions.yaml:72` | VERIFIED | COSMETIC | genshin-db `talents/albedo.json`: deployable Geo construct; enemies damaged in the field generate Transient Blossoms |
| Durin | 5-star, Pyro, Mondstadt | `mondstadt-companions.yaml:73-74`; `DurinWitchsFlame.cs:44` | VERIFIED | LOAD-BEARING | genshin-db `characters/durin.json`: rarity 5, Pyro, region Mondstadt |
| Durin | Card name "Witch's Flame" | `mondstadt-companions.yaml:73` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Phrase absent from genshin-db `talents/durin.json` (NA "Radiant Wingslash", Skill "Binary Form: Convergence and Division", Burst "Principle of Purity/Darkness…"; in-kit terms are "Dragon of White Flame" / "Dragon of Dark Decay"). The *witch* association is separately supported: affiliation "Hexenzirkel", description "A dragon born from M's pen" |
| Nicole | 5-star, Pyro | `mondstadt-companions.yaml:75-76` | VERIFIED | LOAD-BEARING | genshin-db `characters/nicole.json`: rarity 5, Pyro, affiliation "Hexenzirkel" |
| Nicole | **Nation = Mondstadt** | `mondstadt-companions.yaml` (placement); `NicoleCelestialGift.cs:44` `Nation => "mondstadt"` | UNVERIFIABLE | LOAD-BEARING | genshin-db `characters/nicole.json` has **no `region` field at all**; `associationType` is `ASSOC_HVISION`, not `ASSOC_MONDSTADT` (contrast Durin, same Hexenzirkel affiliation, which *does* carry `region: Mondstadt`). Fandom region page 402-blocked. Nation drives `SAME_NATION_REWARD_SHARE` and the Mondstadt Rare count (sheet says Mondstadt "sits at exactly 3", one card from turning the banner on — `fontaine-rares-banner-sprint-log.md:246-249`) |
| Nicole | Card name "Celestial Gift" | `mondstadt-companions.yaml:75` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Phrase absent from genshin-db `talents/nicole.json` (NA "Allegoria", Skill "Revelation: Uncreated Light", Burst "Revelation: Ladder of Divine Ascent", passives Methexis / Philokalia / Nepsis) |
| Prune | 4-star, Anemo, Mondstadt | `mondstadt-companions.yaml:90`; `PruneWitchHunt.cs:45` | VERIFIED | LOAD-BEARING | genshin-db `characters/prune.json`: rarity 4, Anemo, affiliation Mondstadt, region Mondstadt |
| Prune | Witch-hunt framing ("Little Witch's Hunt", Klee's designated teammate) | `mondstadt-companions.yaml:90` | VERIFIED (theme) / UNVERIFIABLE (name) | LOAD-BEARING | Theme: genshin-db `characters/prune.json` — "A diminutive Witch Hunter who has journeyed all the way from Nod-Krai with the singular purpose of rooting out a witch… including bullying little kids!". Name: "Little Witch's Hunt" does not appear in `talents/prune.json` (NA "Badaboom! Hexbuster Hammer", Skill "Ring-A-Ding-Ding! Hexhunter Chime", Burst "The Bell Tolls! The Hunt Is On!") |
| Prune | "Klee — designated teammate" pairing | `mondstadt-companions.yaml:89` | UNVERIFIABLE | COSMETIC | The witch Prune hunts is not named in the genshin-db description; no first-party text ties her to Klee or Alice. Fandom story pages 402-blocked |
| — | Sheet header claim: `xingqiu_*` ids fully retired | `docs/archive/companion-lore-errata.md:5-9` | VERIFIED | LOAD-BEARING | Tree-wide case-insensitive grep for `xingqiu`: **zero** surviving companion-roster references. Remaining hits are all self-labelled historical/negative: `docs/teyvat-spire-design-principles.md:88,103,245` (prose examples + the v1.7 changelog entry recording the correction), `docs/archive/csharp-build-spec.md:59`, `docs/archive/pass3-ratification.md:14`, `docs/furina-art-pass-requirements.md:53,499` (stale art output, flagged as such), and `tools/art_coverage.py:74-75` + `tier0/tests/test_art_coverage.py:74,126` which explicitly assert Xingqiu is *not* a roster row. No Xingqiu row exists in any `*-companions.yaml` or any `klee-mod` generated card |

### Inazuma — `docs/inazuma-companions.yaml`

| Companion | Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|
| Gorou | 4-star, Geo, Inazuma, Watatsumi resistance | `inazuma-companions.yaml:22-32`, `:13` | VERIFIED | LOAD-BEARING | genshin-db `characters/gorou.json`: 4★ Geo, affiliation "Watatsumi Island", region Inazuma |
| Gorou | "General's War Banner" is his | `inazuma-companions.yaml:27` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/gorou.json`: "General's War Banner" is the field created by his Skill *Inuzaka All-Round Defense* |
| Gorou | "Inuzaka Charge" | `inazuma-companions.yaml:23` (shipped title) | VERIFIED (stem) | LOAD-BEARING | "Inuzaka" is canonical (Skill "Inuzaka All-Round Defense"); the "Charge" suffix is mod-authored |
| Gorou | Card name "Heart of the Clan" | `inazuma-companions.yaml:30` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Phrase absent from genshin-db `talents/gorou.json` (passives: "Heedless of the Wind and Weather", "A Favor Repaid", "Seeker of Shinies") |
| Gorou | Framed as "the literal adjutant" | `inazuma-companions.yaml:22` | UNVERIFIABLE | COSMETIC | genshin-db gives title "Canine Warrior" and description "The **great general** of Watatsumi Island's forces." Neither "adjutant" nor a rank subordinate to Kokomi is stated in first-party text; both readings are compatible with "answers to the Divine Priestess". YAML comment only, not shipped |
| Gorou | DEF-scaling / defensive-banner identity | `inazuma-companions.yaml:29` | VERIFIED | COSMETIC | genshin-db `talents/gorou.json`: General's War Banner grants DEF/Geo bonuses scaling with the Geo character count |
| Sayu | 4-star, Anemo, Inazuma, Shuumatsuban ninja, sleepy | `inazuma-companions.yaml:34-44` | VERIFIED | LOAD-BEARING | genshin-db `characters/sayu.json`: 4★ Anemo, affiliation "Shuumatsuban", region Inazuma, "A pint-sized ninja attached to the Shuumatsuban, who always seems sleep-deprived" |
| Sayu | Shuumatsuban is under the **Yashiro** Commission | `inazuma-companions.yaml:13` | VERIFIED | COSMETIC | Fandom (via WebSearch extraction, direct fetch 402): "The Shuumatsuban is a secret Inazuman organization under the Yashiro Commission… led by the head of the Kamisato Clan and Yashiro Commissioner" — https://genshin-impact.fandom.com/wiki/Shuumatsuban |
| Sayu | "Yoohoo Art: Fuuin Dash", "Muji-Muji Daruma", "Windwheel" | `inazuma-companions.yaml:35,38` + id `sayu_yoohoo_windwheel` | VERIFIED | LOAD-BEARING | genshin-db `talents/sayu.json`: Skill "Yoohoo Art: Fuuin Dash"; "Fuufuu Windwheel" in the skill text; Burst *Yoohoo Art: Mujina Flurry* summons the "Muji-Muji Daruma" |
| Sayu | Muji-Muji Daruma is a **healing** identity (hence the Block conversion) | `inazuma-companions.yaml:40-41` | VERIFIED | COSMETIC | genshin-db `talents/sayu.json`: the Daruma restores HP to the active character |
| Kuki Shinobu | 4-star, Electro, Inazuma, Arataki Gang deputy leader, medic | `inazuma-companions.yaml:46-56` | VERIFIED | LOAD-BEARING | genshin-db `characters/kukishinobu.json`: 4★ Electro, affiliation "Arataki Gang", region Inazuma, title "Mender of Tribulations", "capable and reliable Arataki Gang deputy leader" |
| Kuki Shinobu | "Sanctifying Ring" and "Grass Ring of Sanctification" are hers | `inazuma-companions.yaml:47,51` (shipped titles) | VERIFIED | LOAD-BEARING | genshin-db `talents/kukishinobu.json`: Skill "Sanctifying Ring"; its text — "Creates a **Grass Ring of Sanctification** at the cost of part of her HP" |
| Kuki Shinobu | Errata: her canonical kit costs her own HP | `inazuma-companions.yaml:8-9` | VERIFIED | COSMETIC | Same source: skill consumes HP (capped so it cannot take her below 20%). The sheet's decision to drop it is a design ruling, not a canon claim |
| Kuki Shinobu | Card name "Thundergrust" | `inazuma-companions.yaml:54` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Word absent from genshin-db `talents/kukishinobu.json` and `constellations/kukishinobu.json`. Nearest canonical term is "**Thundergrass** Mark" (C4) |
| Thoma | 4-star, Pyro, Inazuma, Yashiro Commission, "fixer", shield specialist | `inazuma-companions.yaml:58-64` | VERIFIED | LOAD-BEARING | genshin-db `characters/thoma.json`: 4★ Pyro, affiliation "Yashiro Commission", region Inazuma, "The Kamisato Clan's housekeeper. A well-known 'fixer' in Inazuma" |
| Thoma | "Blazing Barrier" and "Crimson Ooyoroi" are his | `inazuma-companions.yaml:59,62` (shipped titles) | VERIFIED | LOAD-BEARING | genshin-db `talents/thoma.json`: Burst is literally "Crimson Ooyoroi"; "Blazing Barrier" is the shield created by Skill *Blazing Blessing* and re-generated by the Burst's Fiery Collapse |
| Thoma | "Flaming collapse" flavor | `inazuma-companions.yaml:64` | VERIFIED | COSMETIC | genshin-db `talents/thoma.json`: the Burst's effect is named "Fiery Collapse" |
| Kujou Sara | 4-star, Electro, Inazuma, Shogunate/Tenryou, ATK-buffer | `inazuma-companions.yaml:66-74`, `:13` | VERIFIED | LOAD-BEARING | genshin-db `characters/kujousara.json`: 4★ Electro, affiliation "Tenryou Commission", region Inazuma, "A general of the Tenryou Commission" |
| Kujou Sara | "Crowfeather Cover" and "Tengu Stormcall" are hers; "Tengu" framing | `inazuma-companions.yaml:67,70` (shipped titles) | VERIFIED | LOAD-BEARING | genshin-db `talents/kujousara.json`: Skill "Tengu Stormcall"; its text grants "**Crowfeather Cover** for 18s"; NA "Tengu Bowmanship"; character title "Crowfeather Kaburaya" |
| Kujou Sara | She was the opposing field commander; "now answers to the strategist **who beat her**" | `inazuma-companions.yaml:17-18` | UNVERIFIABLE | COSMETIC | The opposition is supported (Tenryou general vs Watatsumi's Divine Priestess — genshin-db `characters/{kujousara,sangonomiyakokomi}.json`). The *outcome* claim ("who beat her") is an Archon Quest narrative reading; no first-party text in the game-text dump states a defeat of Sara by Kokomi, and Fandom quest pages are 402-blocked |
| Arataki Itto | 5-star, Geo, Inazuma, Arataki Gang head, oni bloodline | `inazuma-companions.yaml:76-81` | VERIFIED | LOAD-BEARING | genshin-db `characters/aratakiitto.json`: 5★ Geo, affiliation "Arataki Gang", region Inazuma, "The first and greatest head of the Arataki Gang"; `talents/aratakiitto.json` passive "Bloodline of the Crimson Oni" |
| Arataki Itto | "Superlative Superstrength" is his | `inazuma-companions.yaml:77` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/aratakiitto.json`: Superlative Superstrength is his core stack resource across NA/Skill/Burst |
| Arataki Itto | He has a canonical taunt (the sheet logs the DSL gap rather than approximating) | `inazuma-companions.yaml:79-80` | VERIFIED | COSMETIC | genshin-db `talents/aratakiitto.json`, Skill *Masatsu Zetsugi: Akaushi Burst!* — Ushi "Taunts surrounding opponents and draws their attacks" |
| Raiden Shogun | 5-star, Electro, Inazuma | `inazuma-companions.yaml:87` | VERIFIED | LOAD-BEARING | genshin-db `characters/raidenshogun.json` |
| Raiden Shogun | "Musou no Hitotachi" is a single massive opening slash of her Burst | `inazuma-companions.yaml:87,108-110` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/raidenshogun.json`: Burst *Secret Art: Musou Shinsetsu* opens with "Musou no Hitotachi" dealing AoE Electro DMG scaled by consumed Resolve, then enters the "Musou Isshin" state |
| Raiden Shogun | Vision Hunt Decree opposed Watatsumi | `inazuma-companions.yaml:84-85` | VERIFIED | COSMETIC | Consistent with genshin-db `characters/sangonomiyakokomi.json` (Divine Priestess of Watatsumi Island) and the Tenryou/Watatsumi split above; Decree narrative itself is Archon Quest text not in the dump — treat the specific "Watatsumi bled for the Vision Hunt" wording as UNVERIFIABLE in the same sense as the Sara row |

### Fontaine — `docs/fontaine-companions.yaml` + `docs/fontaine-rares-banner-sprint-log.md`

#### 4-star bench

| Companion | Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|
| Chevreuse | 4-star, Pyro, Fontaine | `fontaine-companions.yaml:9-19` | VERIFIED | LOAD-BEARING | genshin-db `characters/chevreuse.json`: rarity 4, Pyro, region Fontaine |
| Chevreuse | Musket identity ("Musket shot") | `fontaine-companions.yaml:12` | VERIFIED | COSMETIC | genshin-db description: "Her **musket** shall only ever point at the guilty"; NA "Line Bayonet Thrust EX" (weapon type is Polearm — the sheet does not claim otherwise) |
| Chevreuse | "Interdiction Fire" and "Ring of Bursting Grenades" are hers | `fontaine-companions.yaml:10,17` (shipped titles) | VERIFIED | LOAD-BEARING | genshin-db `talents/chevreuse.json`: Skill "Short-Range Rapid Interdiction Fire"; Burst "Ring of Bursting Grenades" |
| Chevreuse | Card name "Vanguard's Valor" | `fontaine-companions.yaml:13` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Phrase absent from genshin-db `talents/chevreuse.json`; nearest canonical name is passive 1 "**Vanguard's Coordinated Tactics**" |
| Chevreuse | "Her Genshin 'trigger reaction → party ATK up' identity, universalized" (canon is Overload-only) | `fontaine-companions.yaml:15-16` | VERIFIED | COSMETIC | genshin-db `talents/chevreuse.json` passive "Vanguard's Coordinated Tactics" is Overloaded-triggered with a Pyro/Electro-only party requirement; the sheet states the generalization explicitly rather than asserting canon |
| Chevreuse | *Organization (Special Security and Surveillance Patrol) is never stated in the sheet* | `fontaine-companions.yaml:9-19` | UNVERIFIABLE (coverage gap) | COSMETIC | No org attribution present to check. Canon for reference: genshin-db affiliation "Special Security and Surveillance Patrol"; description "The **captain** of the Special Security and Surveillance Patrol" |
| Lynette | 4-star, Anemo, Fontaine, magic-assistant/cat framing | `fontaine-companions.yaml:21-31` | VERIFIED | LOAD-BEARING | genshin-db `characters/lynette.json`: 4★ Anemo, region Fontaine, affiliation "Hotel Bouffes d'ete", "A magic assistant of few words, her emotions are as inscrutable as any cat's" |
| Lynette | "Enigmatic Feint" and "Magic Trick: Astonishing Shift" are hers | `fontaine-companions.yaml:22,28` (shipped titles) | VERIFIED | LOAD-BEARING | genshin-db `talents/lynette.json`: Skill "Enigmatic Feint"; Burst "Magic Trick: Astonishing Shift" |
| Lynette | Card name "Box Trick" | `fontaine-companions.yaml:25` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Phrase absent from genshin-db `talents/lynette.json` and `constellations/lynette.json`; the canonical box term is "**Bogglecat Box**" (summoned by her Burst) |
| Charlotte | 4-star, Cryo, Fontaine, *Steambird* reporter | `fontaine-companions.yaml:33-45` | VERIFIED | LOAD-BEARING | genshin-db `characters/charlotte.json`: 4★ Cryo, region Fontaine, affiliation "The Steambird", "Indefatigable reporter of The Steambird" |
| Charlotte | "Framing: Freezing Point Composition" is hers | `fontaine-companions.yaml:34` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/charlotte.json`: Elemental Skill, exact name |
| Charlotte | "Snappy Silhouette" is hers | `fontaine-companions.yaml:43` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/charlotte.json`: "Snappy Silhouette" is the status her Skill's Tap applies |
| Charlotte | **"Named for her actual passive"** — "Enduring Frosthelm" | `fontaine-companions.yaml:37,41` (shipped title + inline justification) | **CONTRADICTED** | LOAD-BEARING | "Enduring Frosthelm" appears **nowhere** in genshin-db `talents/charlotte.json` or `constellations/charlotte.json`. Her three passives are "Moment of Impact", "Diversified Investigation", "First-Person Shutter"; her constellations are "A Need to Verify Facts", "A Duty to Pursue Truth", "An Imperative to Independence", "A Responsibility to Oversee", "A Principle of Conscience", "A Summation of Interest" |
| Charlotte | Sustain/healing identity being converted to Block | `fontaine-companions.yaml:39-42` | VERIFIED | COSMETIC | genshin-db `talents/charlotte.json`: Burst *Still Photo: Comprehensive Confirmation* creates a Newsflash Field that "restores HP for all nearby party members" |
| Freminet | 4-star, Cryo, Fontaine, diver, reserved demeanor | `fontaine-companions.yaml:47-62` | VERIFIED | LOAD-BEARING | genshin-db `characters/freminet.json`: 4★ Cryo, region Fontaine, affiliation "Hotel Bouffes d'ete", title "Yearning for Unseen Depths", "well-versed in diving" |
| Freminet | "Pers" is his companion device; "Pressurized Floe" and "Shattering Pressure" are his | `fontaine-companions.yaml:48,53,58` (shipped titles) | VERIFIED | LOAD-BEARING | genshin-db `talents/freminet.json`, Skill *Pressurized Floe*: "causes Freminet to enter **Pers Timer**… his Elemental Skill will turn into **Shattering Pressure**" |
| Freminet | Card-name suffix "Backstroke" | `fontaine-companions.yaml:53` (shipped title) | UNVERIFIABLE | LOAD-BEARING | Word absent from genshin-db `talents/freminet.json`; his Burst is "Shadowhunter's Ambush", NA "Flowing Eddies" |
| Freminet | Shatter/Frozen synergy is his canonical space | `fontaine-companions.yaml:58-62` | VERIFIED | COSMETIC | genshin-db `talents/freminet.json`: Shattering Pressure's Levels 1–4 deal Cryo + Physical DMG scaling on Pressure Level; the Cryo/Physical break identity is in-text |

#### 5-star Rares (the newest, least-reviewed drafts)

| Companion | Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|
| Navia | 5-star, Geo, Fontaine | `fontaine-companions.yaml:89`; `fontaine-rares-banner-sprint-log.md:21` | VERIFIED | LOAD-BEARING | genshin-db `characters/navia.json`: rarity 5, Geo, region Fontaine |
| Navia | "President of the Spina di Rosula" | `fontaine-companions.yaml:95` | VERIFIED | COSMETIC | genshin-db `characters/navia.json`: affiliation "Spina di Rosula"; description "The current **President** of Spina di Rosula" |
| Navia | "Cannon Fire Support" is hers | `fontaine-companions.yaml:89-90` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/navia.json`, Burst *As the Sunlit Sky's Singing Salute*: "…providing **Cannon Fire Support** for a duration afterward, periodically dealing Geo DMG" |
| Navia | Burst name "As the Sunlit Sky's Singing Salute" reserved for her future playable kit | `fontaine-companions.yaml:101` | VERIFIED | COSMETIC | genshin-db `talents/navia.json`: that is exactly her Elemental Burst name |
| Navia | Crystallize is deliberately avoided — "she applies no Geo, collects no shards" (as a design fence, not a canon claim) | `fontaine-companions.yaml:94-96` | VERIFIED (canon side) | COSMETIC | The canon shard mechanic exists and is named "**Crystal Shrapnel**" (genshin-db `talents/navia.json`, Burst text); the sheet correctly treats it as a facet it is not taking |
| Clorinde | 5-star, Electro, Fontaine, Champion Duelist | `fontaine-companions.yaml:103`, `:116` | VERIFIED | LOAD-BEARING | genshin-db `characters/clorinde.json`: rarity 5, Electro, region Fontaine, affiliation "Trial Court", description "An undefeated **Champion Duelist**. Sword in hand, she defends justice in the Court of Fontaine" |
| Clorinde | "Impale the Night" is hers | `fontaine-companions.yaml:103` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/clorinde.json`, Skill *Hunter's Vigil*: "Using her Elemental Skill will transform it into '**Impale the Night**': Perform a lunging attack, dealing Electro DMG" |
| Clorinde | Power name `night_vigil` | `fontaine-companions.yaml:105,118` | VERIFIED | LOAD-BEARING | genshin-db `talents/clorinde.json`: "**Night Vigil**" is the skill's state name; passive 3 is "Night Vigil's Harvest" |
| Clorinde | Burst name "Last Lightfall" reserved for her future playable kit | `fontaine-companions.yaml:126` | VERIFIED | COSMETIC | genshin-db `talents/clorinde.json`: Elemental Burst "Last Lightfall" |
| Neuvillette | 5-star, Hydro, Fontaine, the **Iudex** | `fontaine-companions.yaml:128`, `:73-74` | VERIFIED | LOAD-BEARING | genshin-db `characters/neuvillette.json`: rarity 5, Hydro, region Fontaine, affiliation "Court of Fontaine", description "The Chief Justice of Fontaine, known as the **Iudex**" |
| Neuvillette | "Heir to the Ancient Sea's Authority" is his | `fontaine-companions.yaml:128` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/neuvillette.json`: passive talent, exact name |
| Neuvillette | "O Tides, I Have Returned" is his Burst (hence reserved) | `fontaine-companions.yaml:143,201` | VERIFIED | LOAD-BEARING | genshin-db `talents/neuvillette.json`: Elemental Burst, exact name |
| Neuvillette | "O Tears, I Shall Repay" is his Skill | `fontaine-companions.yaml:203-205` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/neuvillette.json`: Elemental Skill, exact name |
| Neuvillette | "Sourcewater Droplets" is his | `fontaine-companions.yaml:206` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/neuvillette.json`: "Sourcewater Droplet" appears in-kit |
| Neuvillette | Sourcewater Droplets are a **sustain/heal** identity (hence the Block conversion) | `fontaine-companions.yaml:208` | VERIFIED | COSMETIC | genshin-db `talents/neuvillette.json`: absorbing Sourcewater Droplets restores his HP |
| Neuvillette | "Equitable Judgment" is his **charged attack**, and it "draws on his own life" | `fontaine-companions.yaml:210,212` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/neuvillette.json`: Charged Attack "Equitable Judgment" — "If Neuvillette's HP is above 50%, he will continuously **lose HP** while using this attack" |
| Neuvillette | "he is the **Hydro Sovereign**" | `fontaine-companions.yaml:73-74`, `:130-131`; `fontaine-rares-banner-sprint-log.md:178` | UNVERIFIABLE | COSMETIC | Neither "Sovereign" nor "Dragon" appears anywhere in genshin-db `talents/neuvillette.json`, and `characters/neuvillette.json` gives only "Chief Justice of Fontaine, known as the Iudex". The Sovereign identity is Archon-Quest narrative; Fandom pages 402-blocked. (Corroborating hint only, not a verdict: `characters/sigewinne.json` title "Wondrous Dragonheir") |
| Arlecchino | 5-star, Pyro | `fontaine-companions.yaml:145` | VERIFIED | LOAD-BEARING | genshin-db `characters/arlecchino.json`: rarity 5, Pyro |
| Arlecchino | **Nation = Fontaine** | `fontaine-companions.yaml:145,147` (R65 placement); `ArlecchinoMasqueRedDeath.cs:44` `Nation => "fontaine"` | **CONTRADICTED** | LOAD-BEARING | genshin-db `characters/arlecchino.json`: **region "Snezhnaya"**, affiliation "Fatui". The sheet states the placement is a house ruling ("Snezhnaya is not a designed sheet"), so the *intent* is on the record — but the shipped `Nation` string asserts Fontaine, and it is the string that drives `SAME_NATION_REWARD_SHARE` and makes Fontaine's Rare count **4**, which is precisely what "turns the banner on" (`fontaine-companions.yaml:68-70`) |
| Arlecchino | "House of the Hearth" is in Fontaine | `fontaine-companions.yaml:147` | VERIFIED | COSMETIC | genshin-db `characters/arlecchino.json` description: "To the children in the **House of the Hearth**, she is their feared yet dependable 'Father.'" (the House's Fontaine location is narrative; the affiliation term itself is first-party) |
| Arlecchino | "The Knave", Fourth of the Fatui Harbingers | implied by `fontaine-companions.yaml:145-165` framing | VERIFIED | COSMETIC | genshin-db `characters/arlecchino.json`: "'The Knave,' Fourth of the Fatui Harbingers" |
| Arlecchino | "Masque of the Red Death" is hers | `fontaine-companions.yaml:145` (shipped title) | VERIFIED | LOAD-BEARING | genshin-db `talents/arlecchino.json`: "Masque of the Red Death" appears as a mechanic within her Normal Attack *Invitation to a Beheading* |
| Arlecchino | "Bond of Life" is canonically hers | `fontaine-companions.yaml:146,152` | VERIFIED | LOAD-BEARING | genshin-db `talents/arlecchino.json`: "Bond of Life" appears extensively across her skill descriptions |
| Arlecchino | Burst name "Balemoon Rising" reserved for her future playable kit | `fontaine-companions.yaml:165` | VERIFIED | COSMETIC | genshin-db `talents/arlecchino.json`: Elemental Burst "Balemoon Rising" |
| Arlecchino | First-draft drawback "you can no longer be healed" (replaced for balance) | `fontaine-companions.yaml:151`; `fontaine-rares-banner-sprint-log.md:66-73` | VERIFIED (canon-accurate as written) | COSMETIC | Bond of Life canonically suppresses healing until repaid — genshin-db `talents/arlecchino.json`. The replacement was a buildability/balance decision, not a lore correction |
| — | "No Fontaine Electro exists" | `fontaine-companions.yaml:6` | **CONTRADICTED** | COSMETIC (in context) | genshin-db `characters/clorinde.json`: **Electro, region Fontaine**. The line is self-scoped to the 4-star bench (Chevreuse/Lynette/Charlotte/Freminet) and predates the Rares block added at `:64`, where Clorinde is authored as Fontaine Electro 47 lines later. As a standing sheet assertion it is now false on its own file |
| — | Deferred names Sigewinne / Lyney / Wriothesley labelled "later scope" — no canon claims attached | `fontaine-companions.yaml:190` | VERIFIED (as scope note) | COSMETIC | No Melusine, Marechaussee Phantom, Special Security and Surveillance Patrol, Fortress of Meropide, or Sigewinne/Wriothesley lore assertion exists anywhere in the three sheets — nothing to audit. Canon for reference: `characters/sigewinne.json` "A **Melusine** and the **Fortress of Meropide's** head nurse", Hydro, Bow, Fontaine; `characters/wriothesley.json` "**Duke** of the Fortress of Meropide", Cryo, Catalyst, Fontaine |

### N4 prior-errata follow-through (`docs/archive/companion-lore-errata.md`)

| Companion | Claim | Where | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|
| Xingqiu | "Xingqiu is Liyue (Feiyun Commerce Guild), not Mondstadt" | `companion-lore-errata.md:3` | VERIFIED (nation) / UNVERIFIABLE (guild) | LOAD-BEARING | genshin-db `characters/` index lists `xingqiu.json` under the Liyue set; the guild-name string could not be read this session and Fandom is 402-blocked. Nation is corroborated in-repo by `docs/teyvat-spire-design-principles.md:245` |
| Xingqiu→Dahlia | The rename landed "everywhere" (yaml, packages, C2 slice list, generated C#/localization, telemetry ids, art SOURCES) | `companion-lore-errata.md:5-9` | VERIFIED | LOAD-BEARING | Tree-wide `grep -i xingqiu`: no roster row, no generated card, no companion yaml entry, no localization string. See the Mondstadt table's last row for the full residue list — all of it is historical prose or a negative assertion in `tools/art_coverage.py:74-75` / `tier0/tests/test_art_coverage.py:126` |
| — | Process law: "lore audit (nation checked against wiki) is now on the companion checklist" | `companion-lore-errata.md:13` | VERIFIED (law exists) | LOAD-BEARING | Also recorded at `docs/teyvat-spire-design-principles.md:245` (v1.7). **Coverage result of running it mechanically:** every one of the 48 generated companion cards carries a non-null `Nation` string (`grep -n "Nation =>" klee-mod/KleeCode/Cards/Generated/*.cs` → 48/48, no `null`). Nation matches canon on 46/48; the two exceptions are Arlecchino (canon Snezhnaya) and Nicole (no canon region exists) — both rowed above |
| — | Fontaine Rares lore audit itself | `fontaine-companions.yaml:190-191` ("Lore audit per v1.7 is [USER] and NOT yet done"); `fontaine-rares-banner-sprint-log.md:227` ("Lore/naming eyes-on audit (v1.7, non-delegable, not yet done)") | VERIFIED (still open) | LOAD-BEARING | Both files state the audit is outstanding; this ledger is the first sweep of that surface and finds the Charlotte and Arlecchino rows above |
| Mona / Jean / Diluc | "Mondstadt Rare rotation bench (principles v1.7)" | `companion-lore-errata.md:11` | N/A — not shipped | COSMETIC | None of the three appears in `docs/mondstadt-companions.yaml` or `klee-mod/KleeCode/Cards/Generated/`. Mondstadt's three shipped Rares are Albedo, Durin, Nicole. Explicitly logged as future scope; no canon claim to grade |

### N4 counts

| Verdict | Count |
|---|---|
| VERIFIED | 55 |
| CONTRADICTED | **3** |
| UNVERIFIABLE | 15 |
| N/A (not shipped, no claim) | 1 |
| **Total claim rows** | **74** |

**Companions covered: 26** — Mondstadt 11 (Dahlia, Fischl, Barbara, Sucrose, Bennett, Kaeya, Diona, Albedo, Durin, Nicole, Prune), Inazuma 7 (Gorou, Sayu, Kuki Shinobu, Thoma, Kujou Sara, Arataki Itto, Raiden Shogun), Fontaine 8 (Chevreuse, Lynette, Charlotte, Freminet, Navia, Clorinde, Neuvillette — shared Rare plus 3 Guest Star cameos — Arlecchino). 48 shipped companion cards inspected in `klee-mod/KleeCode/Cards/Generated/`.

**Element / weapon-adjacent / rarity / region mechanical block: 26/26 companions' element and star-rank check out against genshin-db with zero mismatches.** All divergence is in region attribution (2) and ability naming (1 contradicted, 9 unverifiable).

---

## N5 — Shipped event/UI/tooltip text and pck-src lore strings

Audit surface N5, findings-only. Worktree `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2` (branch `findings/track-n`). **No repo file was edited, committed, or pushed.**

### N5 method

Swept the mod source tree for player-facing string literals. Directories actually read: `klee-mod/KleeCode/` (`Elements/`, `Powers/`, `Relics/`, `Patches/`, `Vfx/`, `Diagnostics/`, and the root `Klee.cs` / `Furina.cs` / `Kokomi.cs` / `KleeMod.cs` / `CompanionPool.cs` / `CompanionBanner.cs`), `klee-mod/Klee/manifest.json`, `klee-mod/pck-src/` (all of `furina/`, `klee/`, `shared/` — every `.tscn` in the tree), `klee-mod/build/`, and `tier0/` `tier05/` `tier1/` `tools/` for string tables. Grep patterns used: `(Name|Title|Description|Text|Flavor|Tooltip|Keyword)\w*\s*(=>|=)\s*"`; `\("(title|description|name|flavor|subtitle)",`; a proper-noun sweep `"[^"]*(Mondstadt|Liyue|Inazuma|Sumeru|Fontaine|Natlan|Snezhnaya|Khaenri|Celestia|Teyvat|Fatui|Archon|Vision|Adventurers|Guild|Ley Line|Statue of the Seven|Mora|Primogem|Knights of Favonius|Qixing|Pyro|Hydro|Electro|Cryo|Anemo|Geo|Dendro)[^"]*"`; `ShowText|FloatingText|Banner|Toast|SpeechBubble|Dialogue`; `Nation =>`; `CompanionElement => Element\.`; and a per-file extraction of every `("title", …)` in `KleeCode/Cards/Generated/`.

Coverage notes and scope boundaries:
- **No shipped event text exists.** There are no mod-authored events, rooms, map nodes, run-summary or achievement strings anywhere in `klee-mod/`. The generated 16-floor map / route / event work (RUNTEMPLATE v6/v7) lives in `tier05/maps.py` and `tier05/events.py`, which are the Python simulator — **dev-only, never reaches a player**. `tier0/` and `tier05/` contain no player-facing string tables at all.
- **No pck-src lore strings.** Every `.tscn` under `klee-mod/pck-src/` is a texture/particle/layout scene. The only `text =` properties are in `furina/ui/salon_stage.tscn` and are empty strings plus one numeral `"5+"`. There is no `.po`, `.csv`, `.json` or `.tres` localization table in `pck-src/`. All shipped loc rows live in C#: `KleeMod.cs`'s `card_keywords` fallback table plus per-model `ILocalizationProvider.Localization`.
- Card names/descriptions for the Klee, Furina and Kokomi **kit** pools were left to their auditors. The Companion card titles are included below because they are player-facing strings that make dense canon claims and sit outside those three characters' identities; if another surface claims them, treat that table as duplicate coverage rather than contradictory.
- The words `Vision`, `Mora`, `Primogem`, `Ley Line`, `Statue of the Seven`, `Adventurers' Guild`, `Fatui`, `Archon`, `Celestia`, `Teyvat` (outside the mod title), `Liyue`, `Sumeru`, `Natlan`, `Snezhnaya`, `Khaenri'ah` and `Dendro` **do not appear in any shipped string**. No claim is made about them, so there is nothing to verify.

**Blocked sources:** `genshin-impact.fandom.com` returns **HTTP 402 Payment Required** through the proxy (confirmed on `/wiki/Elemental_Reaction`). Workaround used: `game8.co`, `genshin-center.com` (per-character talent/constellation listings), `honeyhunterworld`, `keqingmains.com`, `icy-veins.com` and `wiki.hoyolab.com` via WebSearch/WebFetch. `raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/common/Element.json` returned **HTTP 404** (path no longer valid in that repo layout); not pursued further since the tertiary sources answered every question.

---

### Events

No rows. See method note above — the mod ships zero event/room/map-node/run-summary strings. Recorded here so the absence is auditable rather than assumed.

---

### UI + character-select chrome

| String (quoted) | Where | Shipped? | Claim | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|---|
| `"Teyvat Spire Roster"` | `klee-mod/Klee/manifest.json:3` | SHIPPED (mod list) | "Teyvat" is the world of Genshin Impact | VERIFIED | COSMETIC (mod chrome, not in-fiction) | https://wiki.hoyolab.com/m/genshin/entry/4023/?lang=en-us |
| `"Playable Genshin roster for Slay the Spire 2. Includes Klee, Furina, elemental reactions, and Companion cards."` | `klee-mod/Klee/manifest.json:6` | SHIPPED (mod list) | "elemental reactions" is the Genshin system name | VERIFIED | COSMETIC | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"The Spark Knight of Mondstadt."` | `klee-mod/KleeCode/Klee.cs:57` | SHIPPED (character select) | Klee's title is Spark Knight; she is of Mondstadt | VERIFIED | LOAD-BEARING (character identity) | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ ("Knights of Favonius Spark Knight") |
| `"The Regina of All Waters, Kindreds, Peoples and Laws."` | `klee-mod/KleeCode/Furina.cs:26` | SHIPPED (character select) | Furina's full styled title | VERIFIED | LOAD-BEARING | https://hoyodex.miraheze.org/wiki/Furina_de_Fontaine_(YS-MU) ; https://tvtropes.org/pmwiki/pmwiki.php/Characters/GenshinImpactFurina |
| `"Divine Priestess of Watatsumi Island, and the strategist who wins by spending everything except lives."` | `klee-mod/KleeCode/Kokomi.cs:41-42` | SHIPPED (character select) | Kokomi is Divine Priestess of Watatsumi Island | VERIFIED | LOAD-BEARING | https://genshin-center.com/characters/sangonomiyakokomi ; https://library.keqingmains.com/characters/hydro/sangonomiya-kokomi |
| `"5+"` | `klee-mod/pck-src/furina/ui/salon_stage.tscn:701` | SHIPPED (Salon stage HUD) | none (numeral) | n/a — no canon claim | COSMETIC | repo path above |
| `"mondstadt"` / `"fontaine"` / `"inazuma"` as `HomeNation` for Klee / Furina / Kokomi | `klee-mod/KleeCode/CompanionPool.cs:136-143` | NOT shipped (internal weighting key; never rendered) | Klee→Mondstadt, Furina→Fontaine, Kokomi→Inazuma | VERIFIED | COSMETIC (dev-only string) | https://genshin-center.com/characters/sangonomiyakokomi ; https://genshin.gg/characters/furina/ |
| `"[{ModId}] Initializing Teyvat Spire roster..."` and all `Log.Warn/Error` copy in `Patches/MerchantCompanionSlots.cs:89-215` | `KleeCode/KleeMod.cs:31`, `KleeCode/Patches/MerchantCompanionSlots.cs` | **DEV-ONLY** (godot.log) | none — no Teyvat proper nouns beyond the mod's own name | n/a | COSMETIC | repo paths above |

---

### Keywords + powers text

The `card_keywords` fallback table in `KleeCode/KleeMod.cs:110-196` is the highest-value block on this surface: it is the shipped hover-tooltip law for every elemental reaction.

| String (quoted) | Where | Shipped? | Claim | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|---|
| `"Reaction preview: Overload"` | `KleeMod.cs:141` (`KLEEMOD-OVERLOAD_PREVIEW.title`) | SHIPPED (keyword tooltip title) | The Pyro×Electro reaction is named "Overload" | **CONTRADICTED** — the in-game reaction name is **"Overloaded"** | **LOAD-BEARING** (keyword law, shipped tooltip) | https://game8.co/games/Genshin-Impact/archives/297558 ("**Overloaded** — Target explodes, knocking back enemies in proximity and deals AoE Pyro damage") |
| `"Reaction preview: Vaporize"` + body `"…triggering hit deals 1.5x damage…"` | `KleeMod.cs:135-137` | SHIPPED | "Vaporize" is the Hydro/Pyro amplifying reaction | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"Reaction preview: Melt"` | `KleeMod.cs:138-140` | SHIPPED | "Melt" is the Pyro/Cryo amplifying reaction | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"Reaction preview: Superconduct"` | `KleeMod.cs:143-145` | SHIPPED | "Superconduct" is the Electro×Cryo reaction (one word, no hyphen) | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"Reaction preview: Electro-Charged"` | `KleeMod.cs:146-148` | SHIPPED | "Electro-Charged" — hyphen and capital C | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"Reaction preview: Frozen"` / `"Reaction preview: Frozen (Boss)"` + `"Bosses cannot be Frozen."` | `KleeMod.cs:149-154` | SHIPPED | "Frozen" is the Hydro×Cryo reaction, and bosses are exempt from the freeze | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 ("Target is temporarily frozen in place and stopping all enemy actions **except Bosses**") |
| `"Reaction preview: Swirl"` + `"This card supplies Anemo to an existing aura. The aura is consumed and copied onto all enemies."` | `KleeMod.cs:155-157` | SHIPPED | "Swirl" is the Anemo trigger reaction and spreads the element | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 ("spreads that element to nearby enemies") |
| `"Reaction preview: Crystallize"` + `"…you gain 4 Block."` | `KleeMod.cs:158-160` | SHIPPED | "Crystallize" is the Geo trigger reaction and yields a shield | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 ("Creates a crystal shard … which provides a shield") |
| `"The first Attack that hits it Shatters for unblockable damage and removes Frozen."` | `KleeCode/Powers/FrozenPower.cs:35-37`; mirrored `KleeMod.cs:151` | SHIPPED (power tooltip) | "Shatter" is the reaction that breaks a Frozen target | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 ("**Shatter** — Triggered when frozen enemies are hit by Geo or claymore attacks") |
| `"Applies Pyro"` / `"Applies Hydro"` / `"Applies Electro"` / `"Applies Cryo"` (+ bodies) | `KleeMod.cs:116-127` | SHIPPED | Pyro/Hydro/Electro/Cryo are the element names, initial-capital, not "Fire/Water/Electric/Ice" | VERIFIED | LOAD-BEARING (terminology spelling) | https://genshin.gg/elements/ |
| `"{Element} Aura"` → renders `"Pyro Aura"`, `"Hydro Aura"`, `"Electro Aura"`, `"Cryo Aura"` | `KleeCode/Powers/AuraPower.cs:49` | SHIPPED (enemy debuff tooltip) | same six element spellings, and only Pyro/Hydro/Electro/Cryo leave auras | VERIFIED | LOAD-BEARING | https://genshin.gg/elements/ ; Anemo/Geo trigger-only is consistent with the Swirl/Crystallize definitions at https://game8.co/games/Genshin-Impact/archives/297558 |
| `"…triggers an [gold]Elemental Reaction[/gold]…"` | `KleeCode/Powers/AuraPower.cs:51-58`, `CurtainCallPowers.cs:356`, `ReactionKitPowers.cs:37` | SHIPPED | "Elemental Reaction" is the system's canonical name, capitalized | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"Elemental Skill"` (keyword title) + `"Playing this card grants 5 Burst Energy."` | `KleeMod.cs:113-115` | SHIPPED | "Elemental Skill" is the canonical ability-slot name | VERIFIED | LOAD-BEARING | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Burst Energy"` (power title, and used throughout keyword bodies) | `KleeCode/Powers/BurstResource.cs:255`; `KleeCode/Powers/FurinaResources.cs:1065` | SHIPPED (resource tooltip) | implies "Burst Energy" is a Genshin resource term | **UNVERIFIABLE** — Genshin names the resource **"Energy"** and the ability **"Elemental Burst"**; no source consulted (game8 reaction/talent pages, genshin.gg, genshin-center character pages) uses the compound "Burst Energy" | LOAD-BEARING (shipped resource name) | searched: https://game8.co/games/Genshin-Impact/archives/297558 ; https://genshin.gg/elements/ ; https://genshin-center.com/characters/klee — term absent from all three |
| `"Catalytic Conversion"` — `"[gold]Elemental Reactions[/gold] grant {Amount} extra [gold]Spark[/gold]…"` | `KleeCode/Powers/ReactionKitPowers.cs:35`; card `KleeCode/Cards/Generated/CatalyticConversion.cs:39` | SHIPPED (power tooltip + card title) | names a Genshin talent | **CONTRADICTED** — Sucrose's Ascension passive is **"Catalyst Conversion"**, not "Catalytic Conversion". The same build ships the correct spelling on the companion card `"Sucrose — Catalyst Conversion"` (`Cards/Generated/SucroseCatalystConversion*`), so the two shipped strings disagree with each other | **LOAD-BEARING** | https://genshin-center.com/characters/sucrose (Passive Talents: "Catalyst Conversion") |
| `"Vermillion Pact"` — `"[gold]Vaporize[/gold] and [gold]Melt[/gold] amplify {Amount}% more."` | `KleeCode/Powers/ReactionKitPowers.cs:58`; card `Cards/Generated/VermillionPact.cs:39` | SHIPPED | "Vermillion" spelling (double-L) as a Genshin-flavoured proper noun; Vaporize/Melt are the amplifying reactions | VERIFIED (reaction half; the "Vermillion" spelling matches the in-game artifact set **Vermillion Hereafter**, but "Vermillion Pact" itself is an original name making no canon claim) | LOAD-BEARING (reaction names) / COSMETIC (the title) | https://game8.co/games/Genshin-Impact/archives/297558 |
| `"Oz, at Your Side"` — `"…Oz deals N damage and applies [gold]Electro[/gold] to a random enemy."` | `KleeCode/Powers/CompanionPowers.cs:200-206` | SHIPPED (power tooltip) | Oz is Fischl's Electro companion | VERIFIED | LOAD-BEARING | https://genshin-center.com/characters/fischl (Oz summoned by "Nightrider", Electro) |
| `"Solar Isotoma"` | `KleeCode/Powers/CompanionPowers.cs:291` | SHIPPED | names Albedo's Elemental Skill construct | VERIFIED | LOAD-BEARING | https://genshinimpact.wiki.fextralife.com/Abiogenesis:_Solar_Isotoma |
| `"Fantastic Voyage"` | `KleeCode/Powers/CompanionPowers.cs:375` | SHIPPED | Bennett's Elemental Burst | VERIFIED | LOAD-BEARING | https://genshinimpact.wiki.fextralife.com/Fantastic+Voyage ; https://genshin.honeyhunterworld.com/s_323901/?lang=EN |
| `"Passion Overload"` | `KleeCode/Powers/CompanionPowers.cs:414` | SHIPPED | Bennett's Elemental Skill | VERIFIED | LOAD-BEARING | https://genshin-center.com/characters/bennett |
| `"Shattering Pressure"` | `KleeCode/Powers/CompanionPowers.cs:484` | SHIPPED | Freminet's Elemental Skill recast | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/417207 ; https://keqingmains.com/q/freminet-quickguide/ |
| `"Masque of the Red Death"` + `"Each turn your [gold]Bond of Life[/gold] consumes the first N [gold]Block[/gold] you gain."` | `KleeCode/Powers/FontainePowers.cs:170-176` | SHIPPED | Arlecchino's state name, and "Bond of Life" as the Fontaine resource | VERIFIED (both) | LOAD-BEARING | https://keqingmains.com/q/arlecchino-quickguide/ ; https://bittopup.com/article/Bond-of-Life-Guide-Arlecchino-Clorinde-Build-Tips |
| `"Heir to the Ancient Sea's Authority"` | `KleeCode/Powers/FontainePowers.cs:124` | SHIPPED | Neuvillette's passive talent | VERIFIED | LOAD-BEARING | https://keqingmains.com/q/neuvillette-quickguide/ ; https://game8.co/games/Genshin-Impact/archives/447530 |
| `"Night Vigil"` | `KleeCode/Powers/FontainePowers.cs:88` | SHIPPED | Clorinde's Elemental Skill state | VERIFIED | LOAD-BEARING | https://game8.co/games/Genshin-Impact/archives/417218 ; https://keqingmains.com/q/clorinde-quickguide/ |
| `"Cannon Fire Support"` | `KleeCode/Powers/FontainePowers.cs:49` | SHIPPED | names a Navia mechanic | VERIFIED — it is not a talent *title* but is the named mechanic inside Navia's Elemental Burst and C2 | LOAD-BEARING | https://genshin-center.com/characters/navia |
| `"Witch's Flame"` | `KleeCode/Powers/CompanionPowers.cs:245` | SHIPPED | names a Durin ability | **UNVERIFIABLE** — not among Durin's talents, passives or constellations. His passives are "Light Manifest of the Divine Calculus", "Chaos Formed Like the Night", "Echoes of the Surging Earth", "Witch's Eve Rite: Ode to Ascension"; constellations "Adamah's Redemption", "Unground Visions", "Flame Mirror's Revelation", "Emanare's Source", "Scouring Flame's Sundering", "Dual Birth". No source found for "Witch's Flame" as a Genshin string | LOAD-BEARING | searched: https://genshin-center.com/characters/durin ; https://keqingmains.com/q/durin-quickguide/ ; https://www.icy-veins.com/genshin-impact/durin-profile-talents-constellations |
| `"Celestial Gift"` | `KleeCode/Powers/CompanionPowers.cs:334` | SHIPPED | names a Nicole ability; "Celestial" gestures at Celestia | **UNVERIFIABLE** — Nicole is confirmed a real 5★ Pyro Catalyst character (Version 6.6, 2026-05-20), but no source found naming any talent, passive or constellation "Celestial Gift" | LOAD-BEARING | searched: https://gamewith.net/genshin-impact/article/show/38300 ; https://www.gamsgo.com/blog/genshin-nicole-preview ; https://gamerant.com/genshin-impact-nicole-release-date/ |
| `"Bake-Kurage"` — `"…the jellyfish deals … damage and applies [gold]Hydro[/gold]…"` | `KleeCode/Powers/KuragePowers.cs:34-41` | SHIPPED | Kokomi's Elemental Skill summon, a Hydro jellyfish | VERIFIED | LOAD-BEARING | https://genshin-center.com/characters/sangonomiyakokomi |
| `"Ceremonial Garment"` | `KleeCode/Powers/KuragePowers.cs:276` | SHIPPED | the state Kokomi's Burst grants | VERIFIED | LOAD-BEARING | https://library.keqingmains.com/characters/hydro/sangonomiya-kokomi ("robing Kokomi in a Ceremonial Garment") |
| `"Princess of Watatsumi"` | `KleeCode/Powers/KokomiResources.cs:425` | SHIPPED | Kokomi's passive talent name | VERIFIED (name) — note the mod's effect (turn-start Charge) is unrelated to canon's swimming-stamina utility passive, but the audit records name fidelity only | LOAD-BEARING | https://genshin-center.com/characters/sangonomiyakokomi |
| `"Salon Member"` + `"…Crabaletta deals 6 Hydro damage, the Usher gains 3 Block, Chevalmarin deals 2 Hydro damage."` | `KleeCode/Powers/SalonPowers.cs:69-93` (both plain and `smartDescription`) | SHIPPED | Furina's Salon Solitaire members are Crabaletta, the Usher and Chevalmarin, and they deal Hydro | VERIFIED | LOAD-BEARING | https://genshin.honeyhunterworld.com/s_893201/?lang=EN ; https://library.keqingmains.com/characters/hydro/furina |
| `"Mademoiselle Crabaletta"` / `"Gentilhomme Usher"` / `"Surintendante Chevalmarin"` | `KleeMod.cs:180-184` (member hover-tip titles) | SHIPPED (hover tooltips) | the three canonical Salon Member full names and honorifics | VERIFIED — exact spelling and honorific match | **LOAD-BEARING** | https://genshin.honeyhunterworld.com/s_893201/?lang=EN ; https://x.com/GenshinImpact/status/1721016373672071406 |
| `"Fanfare"` (title) + `"Let the People Rejoice is added to your hand."` | `KleeCode/Powers/FurinaResources.cs:1031`; `SpotlightSystem`/kit strings | SHIPPED | "Fanfare" as a Furina mechanic; "Let the People Rejoice" as her Elemental Burst | VERIFIED | LOAD-BEARING | https://library.keqingmains.com/characters/hydro/furina |
| `"Sparks 'n' Splash"` — `"At 40, [gold]Sparks 'n' Splash[/gold] is added to your hand"` | `KleeCode/Powers/BurstResource.cs:256-259`; `KleeCode/Powers/KitBurst.cs:61` | SHIPPED | Klee's Elemental Burst name incl. the `'n'` punctuation | VERIFIED | LOAD-BEARING | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Jumpy Dumpty"` | `KleeMod.cs:100` (`JUMPY_DUMPTY.title`) | SHIPPED | Klee's Elemental Skill | VERIFIED | LOAD-BEARING | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Explosive Frags"` (power title) | `KleeCode/Powers/DemolitionPowers.cs:134` | SHIPPED | Klee's Constellation 2 | VERIFIED | LOAD-BEARING | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Blazing Delight"` | `KleeCode/Powers/DemolitionPowers.cs:76` | SHIPPED | Klee's Constellation 6 | VERIFIED | LOAD-BEARING | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Spark Knight Style"` / `"True Spark Knight"` | `KleeCode/Powers/SparkKitPowers.cs:59, 89` | SHIPPED | derives from Klee's canonical Knights of Favonius title | VERIFIED (the "Spark Knight" element) | LOAD-BEARING | https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Encore"`, `"All the World's a Stage"`, `"Rising Ovation"`, `"Unheard Confession"`, `"Grand Salon"`, `"Casting Call"`, `"Fortissimo Guard"`, `"Stagehands"`, `"Stagehands (Encore)"`, `"Courtroom Drama"`, `"The Gallery Stirs"`, `"Quick Change"`, `"Kurage's Oath"`, `"Before Sun and Moon"`, `"Vigil of the Deep"`, `"Endless Fireworks"`, `"Playtime Forever"`, `"Explosives Workshop"`, `"Friendly Visit"`, `"Study Buddy"`, `"Metallicize"`, `"Spark"`, `"Bomb"`, `"Confiscated"` | `KleeCode/Powers/*.cs`, `KleeMod.cs` | SHIPPED | none — original mod coinages; they assert no Genshin proper noun, place, organisation, reaction or item name | n/a — no canon claim to verify | COSMETIC | repo paths above |

---

### Relics + potions text

No mod potions exist (`tier0/engine/potions.py` is simulator-side, dev-only). Four shipped relics plus three upgraded variants:

| String (quoted) | Where | Shipped? | Claim | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|---|
| `"Pounding Surprise"` — `"Whenever a [gold]Bomb[/gold] detonates, gain 1 [gold]Spark[/gold]."` | `KleeCode/Relics/PoundingSurprise.cs:53-55` | SHIPPED (starter relic) | Klee's Ascension-1 passive talent, and its Spark association | VERIFIED — canon "Pounding Surprise" grants Klee **Explosive Sparks** off Jumpy Dumpty / Normal Attacks | LOAD-BEARING | https://x.com/GenshinUniverse/status/1980477023198847487 ; https://progameguides.com/genshin-impact-item/genshin-impact-klee-skills-talents-constellations-ascension/ |
| `"Dodoco Tales"` | `KleeCode/Relics/UpgradedStarterRelics.cs:148` | SHIPPED (Ancient relic) | a Klee-associated Genshin item name | VERIFIED — 4★ Catalyst introduced in 1.6, named for Klee's doll Dodoco | LOAD-BEARING | https://gamewith.net/genshin-impact/article/show/28804 ; https://www.icy-veins.com/genshin-impact/weapons/14413 |
| `"Pearl of Wisdom"` / `"Pearl of Insight"` | `KleeCode/Relics/PearlOfWisdomRelic.cs:48`; `UpgradedStarterRelics.cs:253` | SHIPPED (Kokomi starter + Ancient) | reads as a Watatsumi/Kokomi item name | **UNVERIFIABLE** — no Genshin item, weapon, talent or constellation by either name found. The repo's own comment at `PearlOfWisdomRelic.cs:16` records that the slot originally drafted the (real) catalyst **"Everlasting Moonglow"** and that **"Tamakushi Casket"** was moved elsewhere, so the current names appear to be original coinages | LOAD-BEARING (shipped relic name) | searched: https://genshin-center.com/characters/sangonomiyakokomi ; https://library.keqingmains.com/characters/hydro/sangonomiya-kokomi ; https://gensh.honeyhunterworld.com/p_542101/?lang=EN — no "Pearl of Wisdom"/"Pearl of Insight" |
| `"Ethereal Spotlight"` — `"At the start of each turn, add an [gold]Ethereal Spotlight[/gold] to your hand."` | `KleeCode/Relics/EtherealSpotlightRelic.cs:43-45` | SHIPPED (Furina starter) | none — original coinage, no Teyvat proper noun | n/a — no canon claim | COSMETIC | repo path above |
| `"The Curtain Never Falls"` — `"[gold]Center Stage[/gold] and [gold]Guest Cast[/gold] are both always active…"` | `KleeCode/Relics/UpgradedStarterRelics.cs:360-364` | SHIPPED (Ancient relic) | none — original coinage | n/a | COSMETIC | repo path above |
| `"Tamakushi Casket"` | `KleeCode/Cards/Kokomi/CeremonialGarment.cs:111,122`; `KleeCode/Powers/KuragePowers.cs:265` | **DEV-ONLY** (code comments; the string is not in any `Localization` row) | Kokomi's Ascension-1 passive, which refreshes Bake-Kurage on Burst | VERIFIED (and the comment's mechanical description matches canon exactly) | COSMETIC (comment, not shipped) | https://genshin-center.com/characters/sangonomiyakokomi ; https://gensh.honeyhunterworld.com/p_542101/?lang=EN |
| `"Everlasting Moonglow"` | `KleeCode/Relics/PearlOfWisdomRelic.cs:16` | **DEV-ONLY** (comment) | Kokomi's signature 5★ Catalyst | VERIFIED | COSMETIC | https://genshin-center.com/characters/sangonomiyakokomi |

---

### pck-src resources

| String (quoted) | Where | Shipped? | Claim | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|---|
| `text = ""` ×6 | `pck-src/furina/ui/salon_stage.tscn:282,357,432,507,582,687` | SHIPPED (empty at runtime; filled from C#) | none | n/a | COSMETIC | repo path |
| `text = "5+"` | `pck-src/furina/ui/salon_stage.tscn:701` | SHIPPED | none | n/a | COSMETIC | repo path |
| texture paths only (`furina_combat_coat_back.png`, `klee_combat_dodoco.png`, `bomb.png`, `spark.png`, …) | all `.tscn` under `pck-src/` | not text | none | n/a | COSMETIC | repo paths |

**No lore strings exist in `pck-src/`.** The whole directory is 8 scenes: `furina/model/combat.tscn`, `furina/ui/salon_stage.tscn`, `furina/vfx/spotlight_shine.tscn`, `klee/model/combat.tscn`, `klee/vfx/bomb_lob.tscn`, `klee/vfx/dodoco_pop.tscn`, `shared/gauge.tscn`, plus `pck-src/README.md`.

---

### Companion card titles (adjacent surface — see method note)

Included because these are shipped card faces outside the Klee/Furina/Kokomi kit identities and they carry the densest per-string canon load in the build. Element assignments were checked for all 48 and **all 48 are correct** (Albedo Geo, Navia Geo, Charlotte Cryo, Chevreuse Pyro, Dahlia Hydro, Lynette Anemo, Prune Anemo, Nicole Pyro, Durin Pyro, Clorinde Electro, etc.).

| String (quoted) | Where | Shipped? | Claim | Verdict | Load-bearing? | Source |
|---|---|---|---|---|---|---|
| `"Barbara — Soothing Melody"` | `Cards/Generated/BarbaraMelody.cs:44` area | SHIPPED (card title) | names a Barbara talent | **CONTRADICTED** — Barbara's talents are "Whisper of Water", "Let the Show Begin♪", "Shining Miracle♪"; passives "Glorious Season", "Encore", "With My Whole Heart♪"; no "Soothing Melody" at any constellation | **LOAD-BEARING** | https://genshin-center.com/characters/barbara |
| `"Barbara — Shining Idol"` | `Cards/Generated/BarbaraShiningIdol.cs:45` area | SHIPPED | names a Barbara talent | **CONTRADICTED** — same listing; the canonical Burst is "Shining Miracle♪" | **LOAD-BEARING** | https://genshin-center.com/characters/barbara |
| `"Gorou — Inuzaka Charge"` | `Cards/Generated/GorouInuzakaCharge.cs` | SHIPPED | names a Gorou talent | **CONTRADICTED** — Gorou's Elemental Skill is "Inuzaka **All-Round Defense**"; no "Inuzaka Charge" exists | **LOAD-BEARING** | https://genshin-center.com/characters/gorou |
| `"Gorou — Heart of the Clan"` | `Cards/Generated/GorouHeartOfTheClan.cs` | SHIPPED | names a Gorou talent | **CONTRADICTED** — passives are "Heedless of the Wind and Weather", "A Favor Repaid", "Seeker of Shinies"; constellations are the six "…Hound" names | **LOAD-BEARING** | https://genshin-center.com/characters/gorou |
| `"Gorou — General's War Banner"` | `Cards/Generated/GorouWarBanner.cs:50` | SHIPPED | names a Gorou construct | VERIFIED — the General's War Banner is the field created by "Inuzaka All-Round Defense" | LOAD-BEARING | https://genshin-center.com/characters/gorou |
| `"Lynette — Box Trick"` | `Cards/Generated/LynetteBoxTrick.cs` | SHIPPED | names a Lynette talent | **CONTRADICTED** — Lynette's abilities are "Rapid Ritesword", "Enigmatic Feint", "Magic Trick: Astonishing Shift"; the burst summons a **"Bogglecat Box"**, and no talent or constellation is called "Box Trick" | **LOAD-BEARING** | https://genshin-center.com/characters/lynette |
| `"Lynette — Enigmatic Feint"` / `"Lynette — Magic Trick: Astonishing Shift"` | `Cards/Generated/Lynette*.cs` | SHIPPED | Lynette's Skill and Burst | VERIFIED | LOAD-BEARING | https://genshin-center.com/characters/lynette |
| `"Sucrose — Catalyst Conversion"` | `Cards/Generated/SucroseCatalystConversion.cs` | SHIPPED | Sucrose's Ascension passive | VERIFIED — and note this is the *correct* spelling the power tooltip `"Catalytic Conversion"` diverges from | **LOAD-BEARING** | https://genshin-center.com/characters/sucrose |
| `"Sucrose — Astable Anemohypostasis"` | `Cards/Generated/SucroseAnemohypostasis.cs` | SHIPPED | Sucrose's Elemental Skill | VERIFIED (truncated — canon full name is "Astable Anemohypostasis Creation - 6308"; the shipped prefix is exact) | LOAD-BEARING | https://genshin-center.com/characters/sucrose |
| `"Sucrose — Wind Spirit Creation"` | `Cards/Generated/SucroseWindSpirit.cs` | SHIPPED | a Sucrose talent | VERIFIED — it is her **Normal Attack** talent name | LOAD-BEARING | https://genshin-center.com/characters/sucrose |
| `"Durin — Witch's Flame"` | `Cards/Generated/DurinWitchsFlame.cs:50` | SHIPPED | names a Durin ability | **UNVERIFIABLE** — see the power row above; Durin is a real 5★ Pyro Sword character (V6.2, 2025-12-03) but no ability of his is called "Witch's Flame" in any source consulted | **LOAD-BEARING** | searched: https://genshin-center.com/characters/durin ; https://keqingmains.com/q/durin-quickguide/ ; https://game8.co/games/Genshin-Impact/archives/462478 |
| `"Nicole — Celestial Gift"` | `Cards/Generated/NicoleCelestialGift.cs:50` | SHIPPED | names a Nicole ability | **UNVERIFIABLE** — Nicole confirmed real (5★ Pyro Catalyst, V6.6, 2026-05-20) but no talent by this name found | LOAD-BEARING | searched: https://gamewith.net/genshin-impact/article/show/38300 ; https://gamerant.com/genshin-impact-nicole-release-date/ |
| `Nation => "mondstadt"` on `NicoleCelestialGift.cs:43` | same file | **NOT shipped** (internal weighting key) | Nicole's home nation is Mondstadt | **CONTRADICTED** — Nicole is listed **without a region** (grouped with Traveler, Aloy, Skirk); she is affiliated to the Hexenzirkel, not to Mondstadt | COSMETIC (dev-only string; no player ever reads it) | https://skycoach.gg/blog/genshin-impact/articles/all-characters-list ; https://www.gamsgo.com/blog/genshin-nicole-preview |
| `"Prune — Little Witch's Hunt"` | `Cards/Generated/PruneLittleWitchsHunt.cs` | SHIPPED | names a Prune talent | **UNVERIFIABLE** — Prune is real (Anemo, Banehunter Oathhammer / Witchlure Bell) but her named abilities are "Ring-A-Ding-Ding! Hexhunter Chime", "Clang Clang! Witch-tribution Comes!" and "The Bell Tolls! The Hunt Is On!"; "Little Witch's Hunt" was not found | LOAD-BEARING | searched: https://wiki.hoyolab.com/pc/genshin/entry/10624 ; https://genshin-center.com/characters/prune ; https://keqingmains.com/q/prune-quickguide/ |
| `"Navia — Cannon Fire Support"` | `Cards/Generated/NaviaCannonFireSupport.cs:50` | SHIPPED | a Navia mechanic | VERIFIED — named mechanic in her Burst / C2, though not a talent title | LOAD-BEARING | https://genshin-center.com/characters/navia |
| `"Clorinde — Impale the Night"`, `"Neuvillette — Heir to the Ancient Sea's Authority"`, `"Arlecchino — Masque of the Red Death"`, `"Freminet — Pressurized Floe: Backstroke"`, `"Freminet — Shattering Pressure"`, `"Freminet — Pers, Deploy!"`, `"Charlotte — Framing: Freezing Point Composition"`, `"Charlotte — Snappy Silhouette"`, `"Chevreuse — Ring of Bursting Grenades"`, `"Albedo — Solar Isotoma"`, `"Bennett — Fantastic Voyage"`, `"Bennett — Passion Overload"`, `"Fischl — Nightrider"`, `"Kaeya — Frostgnaw"`, `"Diona — Icy Paws"`, `"Thoma — Blazing Barrier"`, `"Thoma — Crimson Ooyoroi"`, `"Sayu — Muji-Muji Daruma"`, `"Sayu — Yoohoo Art: Fuuin Dash"`, `"Raiden Shogun — Musou no Hitotachi"`, `"Kujou Sara — Tengu Stormcall"`, `"Kujou Sara — Crowfeather Cover"`, `"Itto — Superlative Superstrength"`, `"Shinobu — Sanctifying Ring"`, `"Shinobu — Grass Ring of Sanctification"` | `Cards/Generated/*.cs` | SHIPPED | each names a canonical talent, construct or state of that character | VERIFIED | LOAD-BEARING | https://genshin-center.com/characters/{albedo,bennett,fischl,navia,neuvillette,sangonomiyakokomi} ; https://keqingmains.com/q/{clorinde,arlecchino,freminet}-quickguide/ ; https://game8.co/games/Genshin-Impact/archives/417207 ; https://genshinimpact.wiki.fextralife.com/Abiogenesis:_Solar_Isotoma |
| `"Dahlia — Favonian Favor"`, `"Dahlia — Sacramental Shower"`, `"Charlotte — Enduring Frosthelm"`, `"Chevreuse — Interdiction Fire"`, `"Chevreuse — Vanguard's Valor"`, `"Fischl — Oz, at Your Side"`, `"Sayu — Naptime"`, `"Shinobu — Thundergrust"`, `"Gorou — …"` (remainder) | `Cards/Generated/*.cs` | SHIPPED | each reads as a talent name | **UNVERIFIABLE** — a per-character talent listing was fetched for Barbara, Gorou, Sucrose, Lynette, Durin, Navia, Bennett, Albedo, Neuvillette, Clorinde, Freminet, Arlecchino, Kokomi and Furina only; the remaining characters' full talent lists were not retrieved within this pass, so these strings are neither confirmed nor refuted. (Note: Chevreuse's Skill is canonically "Short-Range Rapid Interdiction Fire", of which the shipped string is a truncation; "Favonian"/"Favonius" is a canonical Mondstadt root) | LOAD-BEARING | not fetched — declared as a coverage gap rather than asserted |

---

### N5 counts

- **Strings examined:** 118 distinct player-facing string literals across 5 areas, plus 48 companion card titles and 48 element assignments.
- **Rows in the ledger:** 79.
- **VERIFIED:** 55 (of which 44 LOAD-BEARING).
- **CONTRADICTED:** 6 — `"Reaction preview: Overload"`, `"Catalytic Conversion"`, `"Barbara — Soothing Melody"`, `"Barbara — Shining Idol"`, `"Gorou — Inuzaka Charge"`, `"Gorou — Heart of the Clan"`, `"Lynette — Box Trick"`, `Nation => "mondstadt"` on Nicole. (7 shipped + 1 dev-only = 8 raw; 6 distinct LOAD-BEARING shipped defects after grouping the two Barbara and two Gorou rows as pairs.)
- **UNVERIFIABLE:** 6 — `"Burst Energy"`, `"Pearl of Wisdom"` / `"Pearl of Insight"`, `"Witch's Flame"` (power + card, one claim), `"Celestial Gift"` (power + card, one claim), `"Prune — Little Witch's Hunt"`, and the 9-string residual companion-title block.
- **No canon claim to verify (original coinage):** 26 strings.
- **SHIPPED vs dev-only:** 71 ledger rows are SHIPPED; 8 are dev-only (log lines, code comments, internal `Nation`/`HomeNation` keys) and are COSMETIC at most.
- **Areas with zero findings because zero content exists:** events (0 strings), pck-src lore (0 strings), potions (0 mod potions), map/node/room/run-summary names (0 strings).
- **Blocked sources:** 2 — `genshin-impact.fandom.com` (HTTP 402 through the proxy, every path), `raw.githubusercontent.com/theBowja/genshin-db/.../common/Element.json` (HTTP 404). Both worked around via game8, genshin-center, honeyhunterworld, keqingmains, fextralife, icy-veins and wiki.hoyolab.

---

## N6 — Gallery survivors (S2 events, S8 potions/relics) — spot re-verification

Surfaces audited (read-only, nothing edited):
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\review\event-gallery\gallery.md` (S2, 1752 lines, 47 events / 130 surviving variants)
- `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\land2\review\potion-relic-gallery\gallery.md` (S8, 1306 lines, 51 items / 106 surviving mappings)

### N6 sampling rule

**Load-bearing** = a claim that anchors a shipped item/event identity, a keyword, or a player-facing string. Operationally:
- S8: every `*Canon source: …*` line is load-bearing by construction — it is the sole justification for the `teyvat_name` that would ship. **106 such lines** (1 per surviving mapping; verified 106 headers = 106 canon-source lines, i.e. citation-shaped coverage is complete).
- S2: the drafted event prose carries no canon-source apparatus at all. The only extractable load-bearing canon claims are the **12 named-entity / register rulings** in the "Per-Faction Register Rules" block, because those rulings *caused cuts and demotions* of shipped text (Merusea spelling, Fontaine Research Institute, Marechaussee Phantom vs Hunter, Kokomi's titles, Aranara "Nara"/third person, hilichurlian quoted words, Melusine ledger/warning norms, Katheryne/Guild voice, darshan attributions, Wangsheng solemnity, one-hilichurl-stall, Chinju youkai etiquette).

**Population of load-bearing claims: 118** (106 + 12).

**Sample = 40 population entries** (34 of the 106 S8 canon-source lines + all 6 sampled S2 rulings of the 12), decomposed into **46 individually-verdicted claims** (several canon-source lines assert more than one checkable fact — effect vs rarity, category vs ingredients, drop vs geography — and each gets its own verdict). Chosen by this rule, applied in order:
1. All claims whose citation is **missing, vague, or self-referential** (S2's entire canon layer; S8 acquisition/recipe-source clauses with no external anchor).
2. All **numeric / mechanical canon assertions** (dish effect figures, quality tiers, DEF/HP/ATK/stamina values, ingredient lists, rarity stars).
3. All **drop-source / domain / geography assertions** (which the gallery's own Rule 2 CANON-FACT makes cut-worthy when wrong).
4. All **verbatim-quoted in-game strings** and **causal lore identity claims** (X is Y's specialty / X is Y's guise / X gates Y).
5. Named canon entities where the gallery's ruling *itself* is the load-bearing artifact (the S2 register rules).
Decorative flavor prose (the `>` item-voice blocks, the drafter's resistance notes) was **excluded** as cosmetic.

Sources: Genshin Fandom wiki returns **HTTP 402 through the proxy** (confirmed on `genshin-impact.fandom.com/wiki/Sweet_Madame`). Workaround used: **genshin-db raw game-text JSON** (`raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/{foods,materials}/*.json`) — this is the extracted game text itself, the strongest available substrate — plus WebSearch summaries of game8 / HoYoWiki / Fandom result snippets where genshin-db has no field (recipe vendors, quest gating, org lore).

### N6 re-verification table

| Claim | Gallery / where | Prior verdict | My verdict | Agrees? | Load-bearing? | Source |
|---|---|---|---|---|---|---|
| Chili-Mince Cornbread Buns: 4★ Liyue, Shield Strength 25/30/35% + DEF 165/200/235 for 300s | S8 `block_potion` #1, L91 | kept; named "verified-good" in preamble | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/chilimincecornbreadbuns.json` (effect string matches exactly) |
| Chili-Mince Cornbread Buns recipe from Moonchase Tales / Moonlight Merriment event | S8 `block_potion` #1, L91 | kept (implicitly verified) | UNVERIFIABLE | DIFFERS | LOAD-BEARING (acquisition, Rule 2) | genshin-db food JSON carries no recipe-source field; no recipe-source page reachable (Fandom 402); not resolved by search |
| Fontainian Foie Gras: Fontaine DEF dish, DEF 200 / 300s, flat not percentage | S8 `block_potion` #2, L98 | kept, "verified-good" | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/fontainianfoiegras.json` (normal-quality = DEF 200; full range 165–235) |
| Lotus Flower Crisp: Liyue snack, recipe from Ms. Yu at Liyue Reputation Lv.4, DEF 165/200/235 | S8 `block_potion` #3, L105 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/lotusflowercrisp.json`; game8 archives/  (Ms. Yu, Liyue Rep 4) |
| Fish-Flavored Toast is Klee's specialty variant of Fisherman's Toast | S8 `fire_potion` #1, L121 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/fishflavoredtoast.json` (`baseDishName: Fisherman's Toast`, `characterName: Klee`, DEF 151) |
| Fisherman's Toast: 2★ Mondstadt, DEF 88/107/126, Flour×3 Tomato×2 Onion×1 Milk×1; Klee variant DEF 151 | S8 `weak_potion` #1, L214 | kept, "verified-good" | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/fishermanstoast.json` |
| Fisherman's Toast is a "default recipe (every traveler starts with it)" | S8 `weak_potion` #1, L214 | kept | UNVERIFIABLE | DIFFERS | LOAD-BEARING (acquisition) | genshin-db has no recipe-unlock field; Fandom blocked (402); no confirming source found |
| Sweet Madame restores 20/22/24% Max HP + 900/1,200/1,500 HP; 2×Fowl + 2×Sweet Flower | S8 `blood_potion` #1, L138 | kept; preamble singles out "Sweet Madame's 20% Max-HP figure" as verified-good | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/sweetmadame.json` |
| Sweet Madame is a **1-star** dish | S8 `blood_potion` #1, L138 (rarity carries the "COMMON-tier drop" argument at L142) | kept | CONTRADICTED | DIFFERS | LOAD-BEARING | genshin-db `foods/sweetmadame.json` → `"rarity": 2` |
| Apple Cider: bought from Charles at Angel's Share, 1,500 Mora, max 2/day, restores 26% Max HP + regen over 30s | S8 `blood_potion` #2, L145 | kept | VERIFIED | AGREES | LOAD-BEARING | game8 archives/304698; Fandom snippet (26% Max HP + 570 HP/5s for 30s) |
| Dango Milk: Tomoki, Inazuma City, 1,500 Mora, 2/day, gated behind Imperatrix Umbrosa Ch. Act I; 26% Max HP + regen | S8 `blood_potion` #3, L152 | kept | VERIFIED | AGREES | LOAD-BEARING | Fandom/progameguides snippets — Tomoki, 1,500 Mora, max 2, "Reflections of Mortality" gate |
| Adeptus' Temptation quoted effect: "ATK by 160/194/228 and CRIT Rate by 6/8/10%" | S8 `strength_potion` #1, L168 | curation FLAG states the draft misquotes (actual 260/316/372, 8/10/12%) — but the wrong figures were left standing in the shipped canon_source line | CONTRADICTED | AGREES (on verdict) | LOAD-BEARING (quoted string) | genshin-db `foods/adeptustemptation.json`: "ATK by 260–372 and CRIT Rate by 8–12% for 300s" |
| Adeptus' Temptation ingredients: "ham, crab, matsutake, bamboo shoot" | S8 `strength_potion` #1, L168 | kept, not flagged | CONTRADICTED | DIFFERS | LOAD-BEARING | genshin-db: Ham×4, Crab×3, **Shrimp Meat×3**, Matsutake×3 — no bamboo shoot |
| Tricolor Dango is "a travel/stamina food, not a healing one" | S8 `swift_potion` #1, L187 | curation FLAG says it is in fact a 30/32/34% Max-HP healing dish — but the contradicted canon_source line remains as the #1 survivor's sole citation | CONTRADICTED | AGREES (on verdict) | LOAD-BEARING | genshin-db `foods/tricolordango.json`: `filterText: "Recovery Dish"`, restores 30–34% Max HP + 600–1,900 HP |
| Tricolor Dango "cooked from rice and berries" | S8 `swift_potion` #1, L187 | kept, not flagged | CONTRADICTED | DIFFERS | LOAD-BEARING | genshin-db: Milk×2, Snapdragon×2, Sakura Bloom×2, Rice×1 |
| Northern Smoked Chicken: Mondstadt dish, instantly restores 40/50/60 Stamina | S8 `energy_potion` #1, L276 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/northernsmokedchicken.json` ("Restores 40–60 stamina", Adventurer's Dish) |
| Northern Smoked Chicken recipe "found in a chest near the top of the central tower at Stormterror's Lair" | S8 `energy_potion` #1, L276 | kept | UNVERIFIABLE | DIFFERS | LOAD-BEARING (acquisition) | genshin-db has no recipe-location field; Fandom blocked (402); not confirmed by search |
| Noodles with Mountain Delicacies: canon Liyue dish, 40/50/60 Stamina, Mushroom×3 Raw Meat×2 Flour×2 | S8 `energy_potion` #3, L290 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/noodleswithmountaindelicacies.json` (id 2108) |
| Teyvat Charred Egg: Bennett's specialty upgrade of Teyvat Fried Egg; revives + 10% Max HP + 150 HP; "burnt around the edges" description | S8 `fairy_in_a_bottle` #1, L304 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/teyvatcharredegg.json` (all four clauses match, incl. verbatim description) |
| Poissonchant Pie: Fontaine 3★ revive dish, 900/1,200/1,500 HP, fish heads arranged to gaze upward | S8 `fairy_in_a_bottle` #2, L311 | kept, "verified-good" | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/poissonchantpie.json` |
| Konda Cuisine: Inazuma revive dish, 900/1,200/1,500 HP; description dwells on Konda Village at night and a villager abroad missing home | S8 `fairy_in_a_bottle` #3, L318 | kept, "verified-good" | VERIFIED | AGREES | LOAD-BEARING | genshin-db `foods/kondacuisine.json` (delicious-tier description matches the paraphrase clause for clause) |
| Konda Cuisine recipe "from Madarame Hyakubei at Inazuma Reputation Level 1" | S8 `fairy_in_a_bottle` #3, L318 | kept | UNVERIFIABLE | DIFFERS | LOAD-BEARING (acquisition) | no recipe-vendor field in genshin-db; Fandom blocked (402); not confirmed by search |
| Lustrous Stone from Guyun is farmed from "the Domain of Guyun in the Guyun Stone Forest" (same error class at L783 "Domain of Forgery near Guyun Stone Forest" and L362 Aerosiderite "(Domain of Guyun, Liyue)") | S8 `anchor` #1 L332; `whetstone` #2 L783; `vajra` #2 L362 | kept (3×) | CONTRADICTED | DIFFERS | LOAD-BEARING (acquisition, Rule 2) | game8 archives/301712 + genshin-db: farmed in **Hidden Palace of Lianshan Formula** (Jueyun Karst, NW of the Statue south of Mingyun Village), Mon/Thu/Sun |
| Guyun line order: Luminous Sands → Lustrous Stone → Relic → Divine Body from Guyun | S8 `anchor` #1, L332 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/lustrousstonefromguyun.json` (rarity 3 of the 4-rung line) |
| Grain of Aerosiderite is the tier-1 rung of the Aerosiderite weapon-ascension line | S8 `vajra` #2, L362 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/grainofaerosiderite.json` (`rarity: 2`, lowest rung; Liyue lore text) |
| Basalt Pillar: dropped by the Geo Hypostasis (Liyue), used to ascend Noelle | S8 `anchor` #2, L339 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/basaltpillar.json` ("Dropped by Lv.30+ Geo Hypostases"; shell-of-a-Geo-Hypostasis text) |
| Sango Pearl: Inazuma local specialty from Watatsumi coral, Kokomi's ascension material | S8 `blood_vial` #1, L378 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/sangopearl.json` ("grows in the coral of Watatsumi", Local Specialty (Inazuma)) |
| Onikabuto is "gathered on Watatsumi Island and Yashiori Island" | S8 `bag_of_marbles` #3, L455 | kept | CONTRADICTED | DIFFERS | LOAD-BEARING (geography, Rule 2) | genshin-db `materials/onikabuto.json` sources: **Narukami Island** and **Tatarasuna** |
| Onikabuto is Arataki Itto's ascension material | S8 `bag_of_marbles` #3, L455 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db material record + Itto ascension listings |
| Concealed Unguis is "the mid-tier common ascension material from **Bathysmal Vishaps** … the vishap line of **Enkanomiya and the waters around Watatsumi Island**" | S8 `gorget` #1 (the shipped top pick), L524 | kept | **CONTRADICTED** | DIFFERS | LOAD-BEARING | genshin-db `materials/concealedunguis.json`: *"Body tissue left behind by one of the **Riftwolves**… hunting hounds of 'Alfisol'"*, source "Dropped by Lv. 40+ Riftwolves" (The Chasm, Liyue) |
| Mask of the One-Horned: Mask-series weapon ascension material, Wed/Sat/Sun, Torachiyo an oni lieutenant of the Shogun | S8 `red_mask` #2, L480 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/maskoftheonehorned.json` (`daysOfWeek: Wed/Sat/Sun`; Torachiyo / "beloved lieutenant of the Shogun" text) |
| Mechanical Spur Gear: dropped by Clockwork Meka in Fontaine | S8 `pendulum` #1, L580 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/mechanicalspurgear.json` ("Clockwork meka gear"; "Dropped by Lv. 40+ Clockwork Meka") |
| Ashen Heart: one of three La Signora trounce drops alongside Molten Moment and Hellfire Butterfly | S8 `red_skull` #1, L860 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/ashenheart.json` ("Lv. 70+ Signora Challenge Reward"; Signora lore text) |
| Everflame Seed: Pyro Regisvine drop that gates Klee's Ascension 1, where Pounding Surprise unlocks | S8 `touch_of_orobas_klee` #1, L1027 | kept | VERIFIED | AGREES | LOAD-BEARING (causal) | genshin-db `materials/everflameseed.json` ("Dropped by Lv. 30+ Pyro Regisvines"); Fextralife/Fandom: Pounding Surprise = Klee 1st Ascension Passive |
| Amakumo Fruit: Inazuma local specialty on Seirai Island; quoted description "The fruit of the Amakumo Grass, which grows on Seirai Island. You can hear it crackling…" | S8 `looming_fruit` #1, L1152 | kept | VERIFIED | AGREES | LOAD-BEARING (quoted string) | genshin-db `materials/amakumofruit.json` (verbatim match) |
| Dragon Lord's Crown: Azhdaha trounce drop alongside Bloodjade Branch and Gilded Scale | S8 `diamond_diadem` #1, L1203 | kept | VERIFIED | AGREES | LOAD-BEARING | genshin-db `materials/dragonlordscrown.json` ("Lv. 70+ Azhdaha Challenge Reward") |
| Fossilized Bone Shard, "Canon in-game text: *Geovishap Hatchlings all dream of growing into great dragons one day…*" | S8 `ossified_relic` #1, L945 | kept | CONTRADICTED | DIFFERS | LOAD-BEARING (quoted string) | genshin-db `materials/fossilizedboneshard.json`: actual text is "**Geovishaps** all dream of growing into great dragons one day" (drop sources Geovishap Hatchlings / Geovishaps / Bathysmal Vishaps, Lv.60+ — that half is correct) |
| Nutritious Meal (V.593) is Sucrose's "alchemically-iterated variant of **Satisfying Salad**" | S8 `yummy_cookie` #1, L1061 | kept | CONTRADICTED | DIFFERS | LOAD-BEARING (causal identity) | genshin-db `foods/nutritiousmealv593.json`: `baseDishName: "**Crab, Ham & Veggie Bake**"` |
| Teyvat Travel Guide: in-game book series authored by Alice, Klee's mother, published/stocked by the Adventurers' Guild | S8 `bag_of_preparation` #1, L418 | kept | VERIFIED | AGREES | LOAD-BEARING | game8 archives/376143 + Fandom snippet (Alice = author, founder of the Hexenzirkel, Klee's mother; Guild-published magazine series) |
| "Yakshas: The Guardian Adepti" names five yakshas — Alatus/Xiao, Bosacius, Indarias, Bonanus, Menogias — who served Rex Lapis | S8 `book_of_five_rings` #1, L804 | kept | VERIFIED | AGREES | LOAD-BEARING | Fandom/teyvat-library snippets: book of the "Wonders and Folklore of Liyue" set; five names match exactly; followed Rex Lapis into battle |
| "Marechaussee Phantom" is Fontaine's Melusine force; "Marechaussee Hunter" is an artifact-set name (ruling that CUT *The Tanglewood of Erinnyes*) | S2 register rules, Fatui/Fontaine block | ruling recorded as canon | VERIFIED | AGREES | LOAD-BEARING (drove a cut) | HoYoWiki Melusines entry + game8 archives/408920: Phantom = Neuvillette's Melusine detective force; Hunter = the 4.0 artifact set |
| "Fontaine Research Institute (of Kinetic Energy Engineering)" is the canon institute name (ruling that CUT *Specimen 14, Flooded Annex* and demoted *The Clogged Pump of Elynas*) | S2 register rules, Melusine block | ruling recorded as canon | VERIFIED | AGREES | LOAD-BEARING (drove a cut + a demotion) | game8 archives/426297; HoYoLab 22328180 — canon name confirmed, "Fontaine Research Institute" the accepted short form |
| Hilichurls speak quoted hilichurlian, e.g. "Mosi mita," "Valo" | S2 register rules, Hilichurl block | ruling recorded as canon | VERIFIED | AGREES | LOAD-BEARING (register rule; drove a cut) | Fandom Hilichurlian / game8 archives/332454: "Mosi mita" = eat meat / expression of happiness; "Valo" = goodbye/thanks |
| Amurta = the Akademiya's biology-and-medicine darshan; Kshahrewar = the technology darshan | S2 register rules + Amalgamator #1 (L87) + `strike_dummy`-adjacent S8 L818 | ruling recorded as canon | VERIFIED | AGREES | LOAD-BEARING | game8 archives/404031: Amurta = biology/ecology/medicine; Kshahrewar = technology |
| "Merusea Village," never "Merusee" (drove a demotion of *Two Gifts from the Fontemer*) | S2 register rules, Melusine block | ruling recorded as canon | VERIFIED | AGREES | LOAD-BEARING (drove a demotion) | Fontaine Melusine settlement is canonically **Merusea Village** (HoYoWiki Melusines entry, reached via search; Fandom page 402-blocked) |
| Aranara call humans "Nara" and themselves "Aranara," speaking in third person (drove a demotion of *Nilotpala Dreamseed*) | S2 register rules, Aranara block | ruling recorded as canon | VERIFIED | AGREES | LOAD-BEARING (drove a demotion) | Aranara speech convention in the Aranyaka questline — "Nara" as the Aranara term for humans, third-person self-reference |

### N6 uncited claims

This is a coverage finding, not a canon verdict. **Neither gallery contains a single URL** (`grep -c http` = 0 in both files).

1. **All 130 surviving variants in the S2 event gallery carry their canon claims with no citation of any kind.** The only sources cited anywhere in that file are repo-internal: `docs/sts2-events-harvest.txt` (mechanics only, cited per event) and `tier05/content/events.yaml` (scope). Every named canon entity in the 130 variants — Merusea Village, Musoujin Gorge, the Kujou patrols, Chinju Forest, Dharma Forest, Elynas, Erinnyes, Feiyun Slope, Wangsheng, the Northland Bank, the Grand Bazaar, Katheryne, the Divine Priestess — is asserted uncited.
2. **The 12 S2 "Per-Faction Register Rules" canon rulings are themselves uncited**, including the two that cut shipped drafts (Marechaussee Phantom/Hunter; Fontaine Research Institute) and the two that demoted them (Merusee spelling; Aranara second-person). They read as canon adjudications with no source attached. (All four sampled above; all four independently VERIFIED — the finding is the missing citation, not the content.)
3. **S8's 106 `*Canon source:*` lines are self-attesting prose, not citations** — they assert wiki content ("real Liyue dish", "canon effect: …") without naming which wiki, page, or version. The curation preamble names its sources only in aggregate ("Fandom / game8 / HoYoWiki / Honey Hunter") and only for the seven fabrications it caught, never per claim.
4. Within S8, the sub-class with **no anchor even in principle** — recipe vendors, reputation levels, chest locations, quest gates — is asserted in at least these places and is exactly where my three UNVERIFIABLE verdicts landed: L91 (Moonchase Tales), L214 ("default recipe"), L276 (Stormterror's Lair chest), L318 (Madarame Hyakubei, Rep 1), L105 (Ms. Yu, Rep 4 — this one I *was* able to confirm), L290 (Ms. Bai, 2,500 Mora — unconfirmed clause on an otherwise verified claim), L1152 (Kirara as a second Amakumo Fruit consumer — unconfirmed clause on an otherwise verified claim).
5. The 12 S8 entries whose canon_source opens "**In-style invention**" (L260, L425, L636, L790, L818, L846, L891, L1182, and the partial at L696, L713, L1295) are *correctly* self-labelled under the gallery's own Rule 1 and are **not** counted as uncited — they claim no canon record to cite.

### N6 counts

- Load-bearing population: **118** (106 S8 canon-source lines + 12 S2 register rulings)
- Population entries sampled: **40** (34 S8 + 6 S2) = 34% of population
- Individually-verdicted claims: **46** (40 S8 + 6 S2)
- VERIFIED: **32**
- CONTRADICTED: **10**
- UNVERIFIABLE: **4**
- AGREES with prior recorded verdict: **34**
- DIFFERS from prior recorded verdict: **12** (8 CONTRADICTED not caught by the prior pass, 4 UNVERIFIABLE previously carried as verified)
- Of the 10 CONTRADICTED, **2 were already identified by the prior pass** (Adeptus' Temptation figures, Tricolor Dango category) — but in both cases the false text is **still standing** in the shipped canon_source line; the prior pass recorded the error in a `[USER]` flag rather than correcting or cutting the citation.
- Cosmetic claims sampled: 0 (excluded by the sampling rule)
- Blocked sources: `genshin-impact.fandom.com` → HTTP 402 through the proxy (direct WebFetch). Workaround: genshin-db raw English game-text JSON (authoritative extracted text) + WebSearch result summaries surfacing game8 / HoYoWiki / HoYoLab / Fextralife content.

---
