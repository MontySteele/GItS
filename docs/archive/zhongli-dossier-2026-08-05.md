> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/zhongli-dossier-2026-08-05.md` — new path: `docs/archive/zhongli-dossier-2026-08-05.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Zhongli dossier — canon kit, precedent scan, open questions

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Date:** 2026-08-05 · **Track J1 of the "Last Call, Round Two" addendum.
Findings-only RESEARCH.** No game process was launched. No design content
appears in this document.

> **The iron rule this document is written under, restated so the next reader
> can hold it to account:** *dossiers contain zero design content. A dossier
> that proposes is a failed dossier.* Nothing below names a card, prices a
> number, proposes a keyword, or picks between options. §3 is a list of
> **questions**, not a list of recommendations. Where this document has an
> opinion, it is an opinion about *what is true* — never about what should be
> built.
>
> **The Crystallize fence holds.** `docs/fontaine-companions.yaml:94-96` and
> `docs/fontaine-rares-banner-sprint-log.md:49-51` both record that Zhongli's
> slot-4 archetype owns the Crystallize space and that **nothing shipped so
> far pre-commits how Crystallize scales**. This document does not
> pre-commit it either.

---

## 0. Status of the thing this dossier is about

**The Zhongli deep dive is BLOCKED, and this dossier does not unblock it.**

| Fact | Where |
|---|---|
| Slot 4 is Zhongli — **RULING, but DRAFT and uncountersigned** | `tier0/DECISIONS.md:2913-2946` (R88) |
| R88 is the *stated* blocker on the deep dive | `docs/axis-validity-session-charter.md:19` — "Zhongli deep dive — R88 sits in DRAFT on this session, so this is the blocker." |
| The deep dive additionally unblocks on **A4 + B3** | `docs/axis-validity-session-charter.md:207-209` |
| A4 ("Kit in the keywords, verbs in the cards") is **binding on Zhongli before he authors a card** | `docs/axis-validity-session-charter.md:171-174` |
| Sequencing fence: the axis-validity session sits **before the Zhongli deep dive**, "because slot 4 must not declare elite axes against a framework nobody trusts" | `tier0/DECISIONS.md:2433-2436`; `docs/tech-debt-audit-2026-07-26.md:531` |
| The roster registry is **the pre-Zhongli gate**; slot 4 does not open until a character can be declared once and every consumer reads it or fails loudly | `tier0/roster.py:12-14` |
| Registering a slot-4 Zhongli with nothing else wired produces **18 findings**, each naming a file to edit | `docs/serenitea-sweep-log-2026-07-26.md:819-840` |
| One of those 18 findings is: *archetype registry "declares 'geo', which no card carries"* | `docs/serenitea-sweep-log-2026-07-26.md:837` |
| R88 countersign is tracked as an OPEN gate item | `review/ledger-audit/hygiene-report.md:142`; `docs/backlog-2026-07-29.md` §3 item 9 |

**This dossier is written to wait.** It contains no ruling, pre-empts no
ruling, and is safe to read before or after R88 lands.

**One defect surfaced while establishing the above, reported not resolved.**
R88's reconstructed text states the reserved-character rule as *"a character
reserved for a playable slot may not appear as a companion… Neuvillette is the
forward instance of the same rule"* (`tier0/DECISIONS.md:2932-2936`). That is
**in tension with ratified R52**, which rules that *"playable characters MAY
also exist as Rare companion cards, and may appear in Kokomi's conscript pool
— but only as a Rare payoff"* (`tier0/DECISIONS.md:1348-1351`, ratified
2026-07-24). It is also in tension with what shipped: Neuvillette appears as a
shared-pool Rare companion plus three Guest Star cards
(`docs/fontaine-companions.yaml:128, 203, 206, 210`), and what is actually reserved
for him is his **Burst name**, not his person
(`docs/fontaine-companions.yaml:201`). R88 is unsigned; R52 is ratified. **A
countersigning pass should decide which text governs.** This dossier takes no
position.

---

## 1. Canon kit inventory (wiki-verified)

**Provenance, stated up front because it is load-bearing.** Direct fetches of
`genshin-impact.fandom.com` returned HTTP 402 through the fetch proxy for this
session, so Fandom content below was obtained by search-engine extraction of
the named Fandom pages. **Verbatim talent and constellation text was
independently corroborated against the `genshin-db` English game-text dump**
(raw.githubusercontent.com, fetched successfully), which is a direct dump of
the game's own strings. Where a number could not be verified from a primary
source, it is marked. Where a claim is community inference rather than wiki
text, it is marked **[COMMUNITY]**.

**Version note (applies to the whole section):** everything below describes
**post-Version-1.3 Zhongli**. Version 1.3 changed Geo shields globally from
"250% Geo DMG Absorption" to "150% Physical and Elemental DMG Absorption" and
added the Jade Shield's 20% all-RES shred. Pre-1.3 Zhongli is a different kit.
— `https://genshin.hoyoverse.com/en/news/detail/7524` (official notice; full
change text corroborated at
`https://gamewith.net/genshin-impact/article/show/23982` and
`https://www.dualshockers.com/genshin-impact-1-3-zhongli-geo-characters-buffs-explained/`);
`https://genshin-impact.fandom.com/wiki/Dominus_Lapidis/Change_History`

### 1.1 Normal Attack — "Rain of Stone"

**C1.** Verbatim game text: *"Normal Attack: Performs up to 6 consecutive
spear strikes. Charged Attack: Consumes a certain amount of Stamina to lunge
forward, causing stone spears to fall along his path. Plunging Attack: Plunges
from mid-air to strike the ground below, damaging opponents along the path and
dealing AoE DMG upon impact."*
— `https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/talents/zhongli.json`;
corroborated `https://genshin-impact.fandom.com/wiki/Zhongli`

**C2.** The talent's attribute labels are: 1-Hit through 6-Hit DMG, Charged
Attack DMG, Charged Attack Stamina Cost, Plunge DMG, Low/High Plunge DMG. The
exact stamina cost is **NOT VERIFIED** — the game-text dump stores it as a
`{param}` placeholder and the numeric table could not be extracted this
session.
— same URL as C1

### 1.2 Elemental Skill — "Dominus Lapidis"

**C3.** Verbatim: *"Press — Commands the power of earth to create a Stone
Stele. Hold — Causes nearby Geo energy to explode, causing the following
effects: ·If their maximum number hasn't been reached, creates a Stone Stele.
·Creates a shield of jade. The shield's DMG Absorption scales based on
Zhongli's Max HP. ·Deals AoE Geo DMG. ·If there are nearby targets with the
Geo element, it will drain a large amount of Geo element from a maximum of 2
such targets. This effect does not cause DMG."*
— `https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/talents/zhongli.json`

The tap/hold split is therefore: **tap = construct only; hold = construct +
shield + AoE damage + a Geo-aura drain on up to 2 targets.**

**C4 — Stone Stele, verbatim:** *"When created, deals AoE Geo DMG.
Additionally, it will intermittently resonate with other nearby Geo
constructs, dealing Geo DMG to nearby opponents. The Stone Stele is considered
a Geo construct that can both be climbed and used to block attacks. Only one
Stele created by Zhongli himself may initially exist at any one time."*
— same URL. The hedge word *"initially"* is the game text's own, and exists
because C1 (the constellation) overrides the cap — see C15.

**C5 — Stele duration and resonance cadence.** Maximum duration **30s**; from
2s after creation it resonates with itself and nearby Geo Constructs **every 2
seconds**, dealing Geo DMG.
— `https://genshin-impact.fandom.com/wiki/Dominus_Lapidis`;
`https://genshin-impact.fandom.com/wiki/Stone_Stele_(Summon)`
*Caveat:* the 30s figure appears in wiki notes, **not** in the in-game talent
description, and is not in the talent's attribute table.

**C6 — Jade Shield, verbatim:** *"Possesses 150% DMG Absorption against all
Elemental and Physical DMG. Characters protected by the Jade Shield will
decrease the Elemental RES and Physical RES of opponents in a small AoE by
20%. This effect cannot be stacked."*
— `https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/talents/zhongli.json`;
corroborated `https://genshin-impact.fandom.com/wiki/Dominus_Lapidis`

**C7 — what "150% DMG Absorption" structurally is.** It is a multiplier on the
shield's own absorption pool, applied against **every** damage type (all
Elemental and Physical) — *not* a Geo-only bonus. This is the 1.3 change.
— `https://genshin.hoyoverse.com/en/news/detail/7524` and the two corroborating
URLs in the version note above

**C8 — Skill numeric attributes (base → max talent level).** Stone
Stele/Resonance DMG 16%/32% → 34%/68%; Hold DMG 80% → 170%; **Shield Base
Absorption 1232 → 3389 (flat)**; **Additional Shield Absorption 12.8% Max HP →
27.2% Max HP**; Shield Duration **20s**; Press CD **4s**; Hold CD **12s**.
— `https://genshinimpact.wiki.fextralife.com/Dominus+Lapidis`
*Caveat:* only the **endpoints** are verified. The Fextralife per-level table
is unpopulated (placeholder markup, page last edited Dec 2021) and the
game-text dump carries labels without numeric arrays. **Level-10 exact values
are NOT independently verified here.**

**C9 — the shield is a two-term pool.** The attribute label set confirms
absorption is `Shield Base Absorption` (flat) **plus** `Additional Shield
Absorption … Max HP` (percentage) — two separate terms, not one.
— same URL as C3

**C10 — interruption resistance.** While *holding* the Elemental Skill,
Zhongli's interruption resistance is greatly increased.
— `https://genshin-impact.fandom.com/wiki/Dominus_Lapidis`

### 1.3 Elemental Burst — "Planet Befall" (the petrify)

**C11.** Verbatim: *"Brings a falling meteor down to earth, dealing massive
Geo DMG to opponents caught in its AoE and applying the Petrification status
to them. Petrification: Opponents affected by the Petrification status cannot
move."*
— `https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/talents/zhongli.json`

Note the canon effect is stated narrowly: **"cannot move."** The game text
does not say "cannot act."

**C12 — Burst numbers.** Skill DMG 401.88% → 1138%; **Petrification Duration
3.1s → 4s**; CD **12s**; **Energy Cost 40**.
— `https://genshinimpact.wiki.fextralife.com/Planet+Befall`; the 3.1s
talent-1 figure corroborated at
`https://genshin-center.com/characters/zhongli`

**C13 — the petrify is also an aura application.** Planet Befall applies a
**persistent Geo aura for the duration of the Petrification**; the Geo gauge
is 0.04 units and **does not decay over time**.
— `https://genshin-impact.fandom.com/wiki/Planet_Befall`

**C14 — petrification immunity: the documented cases, and the limit of what is
documented.** The wiki documents *specific* immune cases rather than a blanket
rule: the Unusual Hilichurl cannot be rendered immobile by Frozen, Mona's
Stellaris Phantasm, or Petrification; and prior to Version 1.2 it was possible
to petrify the boss Andrius if Zhongli's level exceeded his.
— `https://genshin-impact.fandom.com/wiki/Unusual_Hilichurl`;
`https://genshin-impact.fandom.com/wiki/Andrius`
**The general claim "petrify doesn't work on bosses" is community shorthand —
no single consolidated wiki statement of it was found.** Independently, this
repo's own enemy atlas records a canon case of acquired petrify immunity:
Kairagi elites, on Final Frenzy, *"gain immunity to Frozen and
petrification"* (`review/enemy-atlas/atlas.md:694, 696`).

### 1.4 Passives

**C15 — A1 "Resonant Waves":** *"When the Jade Shield takes DMG, it will
Fortify: Fortified characters have 5% increased Shield Strength. Can stack up
to 5 times, and lasts until the Jade Shield disappears."*
— `https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/talents/zhongli.json`

**C16 — A4 "Dominance of Earth":** *"Zhongli deals bonus DMG based on his Max
HP: Normal Attack, Charged Attack, and Plunging Attack DMG is increased by
1.39% of Max HP. Dominus Lapidis' Stone Stele, resonance, and hold DMG is
increased by 1.9% of Max HP. Planet Befall's DMG is increased by 33% of Max
HP."*
— same URL. **This is the whole of Zhongli's damage-scaling identity: HP is
the offensive stat as well as the defensive one.**

**C17 — Utility passive "Arcanum of Crystal":** *"Refunds 15% of the ore used
when crafting Polearm-type weapons."* (Out-of-combat crafting utility; no
combat behavior.)
— same URL

### 1.5 Constellations (behavioral)

| # | Name | Verbatim effect |
|---|---|---|
| **C1** | Rock, the Backbone of Earth | *"Increases the maximum number of Stone Steles created by Dominus Lapidis that may exist simultaneously to 2."* |
| **C2** | Stone, the Cradle of Jade | *"Planet Befall grants nearby characters on the field a Jade Shield when it descends."* |
| **C3** | Jade, Shimmering through Darkness | *"Increases the Level of Dominus Lapidis by 3. Maximum upgrade level is 15."* |
| **C4** | Topaz, Unbreakable and Fearless | *"Increases Planet Befall's AoE by 20% and increases the duration of Planet Befall's Petrification effect by 2s."* |
| **C5** | Lazuli, Herald of the Order | *"Increases the Level of Planet Befall by 3. Maximum upgrade level is 15."* |
| **C6** | Chrysos, Bounty of Dominator | *"When the Jade Shield takes DMG, 40% of that incoming DMG is converted to HP for the current character. A single instance of regeneration cannot exceed 8% of that character's Max HP."* |

— all six: `https://raw.githubusercontent.com/theBowja/genshin-db/main/src/data/English/constellations/zhongli.json`

Note that the repo's own naming convention is *"constellations for
rares/upgrades"* (`docs/teyvat-spire-design-principles.md:83`), so this table
is name-source material as well as behavior.

### 1.6 Shield uptime — the number everyone quotes, and its actual status

**C18 — [COMMUNITY].** The wiki states only **shield duration 20s** and **hold
CD 12s** (C8). The widely repeated *"permanent / ~150% uptime"* framing is a
**community inference from 20s > 12s**, not wiki text. Community sources:
`https://keqingmains.com/q/zhongli-quickguide/`, `https://keqingmains.com/zhongli/`.
Likewise KQM's note that the stele's limited range makes consistent resonance
difficult in practice is a community judgment, not wiki text (same URLs).

**Recorded because the task brief cited "150% uptime" as a canon fact: it is
not one.** The verified facts are the 150% *absorption multiplier* (C6/C7) and
the 20s-vs-12s duration/cooldown relationship (C8). The uptime characteristic
is a consequence a reader derives, and the derivation is community-owned.

### 1.7 Geo Resonance and the Geo Construct system

**C19 — Elemental Resonance "Enduring Rock"** (two Geo characters in a party
of four): increases shield strength by 15%; characters protected by a shield
additionally have DMG dealt increased by 15%; and dealing DMG to enemies
decreases their Geo RES by 20% for 15s.
— `https://genshin-impact.fandom.com/wiki/Elemental_Resonance:_Enduring_Rock`
*Version drift:* one extraction includes a Moondrift/Lunar-Crystallize clause
and notes the older wording was "increases Attack DMG by 15%" (now "DMG dealt
increased by 15%"). The Moondrift clause is a recent addition.
— `https://genshin-impact.fandom.com/wiki/Team_Bonus/Change_History`

**C20 — Geo Constructs are a first-class named game system with its own wiki
page.** They are structures comprised of Geo energy, created by certain Geo
characters' talents, by the Lunar-Crystallize reaction, and by certain
enemies.
— `https://genshin-impact.fandom.com/wiki/Geo_Construct`

**C21 — the construct cap.** A total of **3 player-made Geo Constructs** can
exist simultaneously in a player's world, *including in Co-Op Mode*. The limit
does not apply to Geo Traveler's Burst, Kachina's Turbo Twirly, enemy-made
constructs, or Moondrifts.
— same URL

**C22 — constructs have HP and can be destroyed.** Most player-made Geo
Constructs **inherit 100% of the creator's HP and DEF** unless otherwise
specified, and are **destroyed when their HP is fully depleted by enemy
attacks**.
— same URL

**C23 — constructs differ in what they afford.** Starfell Sword and the Stone
Stele can be climbed; Abiogenesis: Solar Isotoma elevates the player;
Ningguang's Jade Screen blocks certain attacks but cannot be climbed.
— `https://genshin-impact.fandom.com/wiki/Geo_Construct`;
`https://genshin-impact.fandom.com/wiki/Jade_Screen`

**C24 — resonance is construct-count-dependent, not Zhongli-specific.** The
Stele resonates with *other nearby Geo Constructs* and makes them periodically
deal AoE Geo DMG while the Stele is active. The mechanic reads on the number
of constructs on the field, from any source.
— `https://genshin-impact.fandom.com/wiki/Geo_Construct`;
`https://genshin-impact.fandom.com/wiki/Dominus_Lapidis`

**C25 — enemies interact with constructs, and this repo already recorded it.**
The repo's own Genshin-side research documents three separate canon
construct-interaction behaviors:
- Geo Constructs **physically block** Dvalin's Tempestuous Barrage Pulse Bombs
  — "an explicit environment-object counter to a specific attack"
  (`review/boss-dossiers/dossiers.md:107`), described there as "a physics
  collision between a player-placed object and a projectile… a positional
  interception, not a damage-reduction effect" (`:131`).
- La Signora's Phase 2 whip **one-shots Geo constructs on contact**, "deleting
  the standard 'hide behind a wall' answer" (`review/boss-dossiers/dossiers.md:275,
  297, 324`).
- Kairagi elites' Sword Charge **destroys player Geo Constructs in its path**
  (`review/enemy-atlas/atlas.md:694, 696`).

**C26 — vertical space.** Constructs are used to gain elevation and thereby
sidestep attacks that lack vertical AoE — the repo's boss dossiers flag this as
"a third-axis exploit with no turn-based representation"
(`review/boss-dossiers/dossiers.md:168, 195`).

### 1.8 Ambiguities and version drift, consolidated

| # | Ambiguity | Consequence for a future reader |
|---|---|---|
| A | Per-level talent tables not verified (only base→max endpoints) | Do not quote a level-10 shield/petrify number from this document |
| B | "Petrify doesn't work on bosses" has no consolidated wiki statement | Treat as community shorthand; the *documented* cases are C14 |
| C | Enduring Rock wording changed ("Attack DMG" → "DMG dealt"); Moondrift clause is new | Cite the current page, note the drift |
| D | Whole kit is post-1.3 | Pre-1.3 Zhongli (250% Geo-only absorption, no RES shred) is a different character |
| E | "Only one Stele … may **initially** exist" | The cap is constellation-dependent by design; there is no version-independent hard cap statement |
| F | Stele 30s duration is wiki-notes-only | Not in the in-game talent text or attribute table |

**Kit facts catalogued: 26 (C1–C26), plus 6 constellation rows.**

**Sources blocked this session** (recorded so a re-verification pass does not
repeat the attempt): `genshin.honeyhunterworld.com` (403), `gi.yatta.moe`
(403), `api.ambr.top` (DNS), `prydwen.gg` (403), `r.jina.ai` (401),
`genshin-builds.com` (no tables), `game8.co` (404), and
`genshin-impact.fandom.com` direct fetch (402 — search extraction used
instead).

---

## 2. Precedent scan

**Why this section exists.** The task brief called this the *"no new mechanics
without StS2 precedent"* rule. **That rule does not exist in the repo under
that phrasing** — I searched for it and every near-variant. What exists are
four weaker instruments that together do that job, and a future design session
should cite these rather than the strong phrasing:

1. **Pillar 1 — "Spire first."** *"StS2 mechanical conventions (energy,
   rarity, intents, keyword style) win over Genshin fidelity when they
   conflict."* — `docs/teyvat-spire-design-principles.md:22`
2. **The subsystem budget.** *"One Ghostflames-scale subsystem… `Rejected:` two
   novel subsystems per character; Downfall's data says the subsystem is 70%
   of the engineering."* — `docs/teyvat-spire-design-principles.md:79`
3. **The check-if-solved norm.** *"Engineering directive — check-if-solved
   FIRST: audit Necrobinder/Osty and BaseLib summon machinery before building
   anything. Salon ships on existing rails or it ships smaller."* —
   `docs/furina-kickoff-v0.1.md:146-149`
4. **§2.2a — the hard-CC pricing rule (v1.5), which is specifically about
   Shape A** and is quoted in full at §2.1 below.

Additionally binding on any Zhongli card: **Guardrail 5**, keyword budget ≤2
beyond the shared element system (`docs/teyvat-spire-design-principles.md:210`),
and **A4 "Kit in the keywords, verbs in the cards"**
(`docs/axis-validity-session-charter.md:171-174`).

### 2.0 Provenance of the official-StS2 evidence

The precedent scan below rests on sources of very different reliability. This
table is part of the finding.

| Source | Kind | Reliability |
|---|---|---|
| `game_ref/{ironclad,silent,defect,necrobinder,regent}.json` | **Machine-extracted from the local `sts2.dll`** via `tools/extract_base_game_pool.py`. 87/88/88/88/88 cards. Structural only (`name, cost, type, rarity, vars, upgrades, cmds, powers, orbs, keywords, exhaust, innate, target, body_lines, mp_only`). **No printed card text.** | Highest — ground truth for *which verbs a card invokes* |
| `game_ref/*_char_facts.yaml` | Decompiled via `ilspycmd`, hand-annotated; starting relics with literal hook chains | High |
| `game_ref/{ironclad,silent}-cards.yaml` | Extractor output in tier0-DSL shape + an `excluded:` list naming cards the DSL cannot express. Carries **printed numbers** | High, lossy coverage |
| `tier0/engine/refpowers.py` (1378 lines, **in-tree**) | Hand-written re-implementation quoting decompiled method names verbatim (`ShouldClearBlock`, `ModifyDamageCap`, `AfterBlockGained`, `ModifyHpLostAfterOsty`); self-flags its divergences | High for *semantics*, second-hand |
| `docs/enemy-dossiers/*.md` (112 files) | Hand-written behavioral dossiers from decompiled source; header states "Behavioral notes only — no decompiled source is reproduced here" | High; the richest prose in the repo |
| `tier05/content/relics.yaml`, `potions.yaml` | "Real StS2 wiki numbers" — a **curated subset** for the sim, not the complete official list | Medium; incomplete **by design** |
| `docs/reserved-card-names.txt` | The Silent's 88 base-game **names only**; the Ironclad's 87 explicitly NOT covered (`:36`) | Names only |

**Two structural caveats that bound every claim in §2.1–§2.3:**

- **`game_ref/` is gitignored and machine-local.** The strongest evidence below
  is **not visible to a clone of this repository**. A cloud session cannot
  reproduce it. (Same class as the standing note at
  `docs/axis-validity-session-charter.md:22-25`.)
- **The repo contains no official card *text* anywhere.** Anything requiring
  exact printed wording is **not answerable from this repo**.

### 2.1 Shape A — petrify-shaped (stun / enemy-skip)

#### The governing rule, quoted in full before any precedent

> **§2.2a — Hard-CC pricing rule (v1.5).** Base StS2 deliberately makes
> reliable stun scarce (an act-3 Ancient reward at 3 energy + Exhaust; looping
> it is a known degenerate win). No reaction, and no companion card, may
> produce an intent-skip at repeatable-common economics. Frozen's base effect
> is soft control (above); **full stun is payoff-tier design space only** (rare
> character cards, artifact sets, 5-star kits), priced at or above the base
> game's stun scarcity, with per-combat diminishing returns (an enemy that
> thaws gains Freeze Resist). Detector: `control_uptime` — % of enemy actions
> negated by companion-sourced effects; winning fights above threshold flag
> SUPPORT_CARRY.
>
> — `docs/teyvat-spire-design-principles.md:44`

Plus the v1.10 extension: *"Spotlight empowerment applies to numbers only —
**never turn-economy effects**"* (`:46`), and §4.3's control-axis clause:
*"companions never source hard CC, and the SUPPORT_CARRY detector enforces
it"* (`:106`).

#### THE HEADLINE FINDING — a negative

**Official StS2 has no player-applied enemy stun, skip, intent-delay, or
intent-scramble. None, in any of the five characters.**

This is a census, not an inference. Every `cmds` + `generic_cmds` string across
all **440 extracted cards** was enumerated. The complete verb vocabulary is
**48 commands**: `CardCmd.*`, `CardPileCmd.*`, `CardSelectCmd.*`,
`CreatureCmd.{Damage,GainBlock,GainMaxHp,Heal,Kill,LoseBlock,TriggerAnim}`,
`DamageCmd.Attack`, `ForgeCmd.Forge`, `OrbCmd.*`, `OstyCmd.Summon`,
`PlayerCmd.{EndTurn,GainEnergy,GainStars}`, `PowerCmd.*`, `SfxCmd/VfxCmd`.
**There is no stun, skip, delay, or intent command in the vocabulary.**

A case-insensitive sweep for `stun|skip|intent|daze|sleep|confus|petrif|freeze|entangl`
across all of `game_ref/*.json` + `*.yaml` returns **4 hits, all false
positives** (`frozen` in two prose headers; `skip` twice in a review-pass
comment).

**Note the tension this creates with the repo's own §2.2a text**, which cites
*"an act-3 Ancient reward at 3 energy + Exhaust"* as the base game's stun. The
nearest Ancient-tier card the extraction actually shows is **Wraith Form**
(Silent, 3c **Ancient**, Intangible 2 with a permanent self-Dexterity drain —
see §2.2), which is damage-immunity, **not** an enemy stun. **Flagged as an
unreconciled discrepancy between the principles doc and the extraction.** A
future session should determine whether §2.2a was written against StS1's
Ancient stun or against a card the extractor does not surface. This dossier
does not resolve it.

#### Near-hits, and why each one is not a stun

| Card | Character | What it actually is | Path |
|---|---|---|---|
| **Taunt** | Ironclad, 1c Uncommon Skill, `target: AnyEnemy` | Gain 7 Block (+1 upg) + Vulnerable. **Despite the name, no aggro/redirect/intent effect** | `game_ref/ironclad.json:1934` |
| **VoidForm** | Regent, 3c Rare Power, Ethereal | `PlayerCmd.EndTurn` + `VoidFormPower` — ends **your own** turn | `game_ref/regent.json:2202` |
| **Expose** | Silent, 0c Uncommon | `CreatureCmd.LoseBlock` + Artifact + Vulnerable — removes enemy **Block**, not an action | `game_ref/silent.json:789` |

No relic or potion in the repo's reference stuns either — but the relic/potion
pools are **curated subsets**, so that is "none found in a partial list", which
is materially weaker than the card finding.

#### Stun DOES exist — as an enemy self-state the player *provokes*

The engine has a real `Stun` intent and a `STUNNED` move that **overwrites a
telegraphed intent mid-player-turn**. It is never applied by the player; it is
a threshold payoff the enemy inflicts on itself when a condition is met.

| Enemy | Trigger | Behavior | Path |
|---|---|---|---|
| **Terror Eel** | Shriek: self-counter at exactly half max HP (70/140; 75/150 Tough); unblocked damage to/below it | Intent replaced on the spot (a queued 22-damage Crash is **erased**), next turn Terror (Vulnerable 99, no damage), Shriek removed. Once per fight; killing from above half HP skips the phase entirely | `docs/enemy-dossiers/terror-eel.md:106-129` |
| **Ceremonial Beast** | Plow: HP-threshold marker at 150 of 252 (= 102 unblocked damage) | Loses **all** Strength (permanent and temporary), **stunned a full turn**, marker dropped. Once only | `ceremonial-beast.md:38-54, 135` |
| **Tunneler** | Breaking its persistent Block to zero | Stunned **immediately, mid-player-turn**; strips Burrowed, wipes remaining Block, force-sets next move to Bite. **The stun overwrites the displayed intent — breaking the shield cancels an already-telegraphed From Below** | `tunneler.md:26, 58-59` |
| **Thieving Hopper** | Last stack of the Flutter 5 hit-count shield removed | Stunned; wastes its next turn, which delays its escape | `thieving-hopper.md:90-96` |
| **Corpse Slug** | Ravenous: any ally on its side dies | Each survivor **Stunned** (telegraph replaced with a Stun intent) + permanent Strength equal to the counter (4; 5 Deadly). **A delay, not a skip** — the Stun move's follow-up is the slug's last logged move, so cycle order is preserved | `corpse-slug.md:54-55` |
| **Lagavulin Matriarch** | Unblocked damage while Asleep | Plating removed outright, **stunned that turn** (a STUNNED move replaces the queued Sleep, so she loses nothing), next move forced to Slash, Asleep removed | `lagavulin-matriarch.md:47-58` |
| **Slumbering Beetle** | Slumber 3 ticks on enemy turn end *and* on every not-fully-blocked damage instance | Damage path → **stunned** turn then Rollout; timer path → wakes with **no** stun. **The player chooses which** | `slumbering-beetle.md:60-76` |
| **Bowlbug (Rock)** | Self-stuns after its own Headbutt when off-balance | `DIZZY_MOVE` is a Stun intent that does nothing. Fully blocking the Headbutt halves its output over two turns | `bowlbug-rock-.md:30-31, 53-60` |
| **Spawn grace** | On spawn | Sneaky Gremlin and Fat Gremlin both spawn on a Stun intent; Phrog Parasite's four death-spawned Wrigglers all telegraph a stun and do nothing on turn 1 | `sneaky-gremlin.md:26`, `fat-gremlin.md:27`, `phrog-parasite.md:29, 78-79` |

#### The single strongest "designed-for but not shipped" datum in the repo

**Bygone Effigy has a dead re-sleep hook.** A second sleep state exists in the
machine, is registered, carries a sleep intent, and has its follow-up wired to
Slash — **but nothing reaches it.** The dossier's own words:

> "an obvious hook for a cut 'knock it back to sleep' mechanic, or for a
> card/relic that could re-sleep an enemy. Treat 'the Effigy can be put back to
> sleep' as *designed-for but not implemented*."
> — `docs/enemy-dossiers/bygone-effigy.md:24`

#### Enemy-side sleep/stasis, as adjacent precedent

- **Lagavulin Matriarch** — Asleep 3 + Plating 12. **Sleep breaks on *unblocked*
  damage only**; chip into Block is pure waste. Never sleeps again.
  (`lagavulin-matriarch.md:26-67`)
- **Slumbering Beetle** — Slumber 3 + Plating 15. (`slumbering-beetle.md:60-90`)
- **Bygone Effigy** — Sleep → Wake → Slash; two free turns front-loaded, and the
  sleep is genuinely consumed (the state machine will not transition until a
  move has been performed). (`bygone-effigy.md:15-24, 57`)
- **Eye With Teeth / Parafright — Illusion.** On death: **not removed from
  combat**; plays a stun animation, sits dead for the turn, then heals to full
  next turn via a forced one-shot Revive. Untouchable while reviving (refuses
  powers). Killing buys exactly one clean turn, **forever repeatable**.
  (`eye-with-teeth.md:47`, `the-obscura.md:72-74`, `fogmog.md:96-99`)

#### Effects that constrain the PLAYER (no true player-stun found)

**No enemy ability skips or removes a player turn.** The closest three:

- **Ringing** (Ceremonial Beast, Beast Cry, 1 stack per player) — a **card
  lock**, not a turn skip: a Ringing card *"can be played only if that player
  has not yet started any card play this turn."* The moment any card starts
  resolving, every Ringing card in hand goes unplayable. Cards already carrying
  a different affliction are never stamped. (`ceremonial-beast.md:137-152`)
- **Dazed** — cost −1 (uncastable), **Unplayable + Ethereal** Status card. Costs
  draws and tempo; never permanent in-combat deck rot. Sources are *all*
  enemies: Chomper Screech (3/player to discard, `chomper.md:31, 55`), Eye With
  Teeth Distract (3/player, bottom, every turn, `eye-with-teeth.md:15, 41`),
  Haunted Ship Haunt (5/player + Weak 3, `haunted-ship.md:34, 56`), Entomancer
  Personal Hive (**N per damage instance** into the dealer's draw pile — a
  4-hit card at Hive 3 injects 12, `entomancer.md:85-100`), Noisebot
  (2/player/turn, `fabricator.md:70`). **No player card in any official pool
  creates Dazed.**
- **Confused** — exists; the Merchant sells a knock-off "Snecko" applying
  Confused *"with none of the draw upside."* (`the-merchant-.md:71`)

#### What this repo already ships that is Shape-A-adjacent

Recorded because the check-if-solved norm will demand it, and because it
changes what a future session would be building *from*:

- **The mod's own engine already has a turn-skip.** `tier0/engine/combat.py:5`
  states the rule — *"Asleep enemies skip; frozen enemies act at −50% damage
  (Frozen v2, principles v1.5)"* — and it is implemented at `:606-608`
  (`sleep_turns` decrements and emits `enemy_sleep`, the enemy's action being
  skipped entirely). It is exercised by the frozen calibration battery's
  `sleeper` fixture, `sleep_turns: 3`
  (`tier0/content/encounters/battery.yaml:32-34`).
  **But it is scripted enemy state, never player-applied** — there is no op in
  the `OPS` table that sets `sleep_turns`, exactly mirroring the official-StS2
  finding above.
- **The `control_uptime` detector that §2.2a names as its enforcement mechanism
  currently has exactly ONE input.** It is computed at
  `tier0/harness/metrics.py:349` as *"fraction of enemy actions negated by
  companion control"*, and the only event that ever increments
  `control_negated` is `frozen_action` with `by_companion` true, crediting
  `1 − FROZEN_DAMAGE_MULT` (`:258-261`, provenance flag at
  `tier0/engine/state.py:427`). Scripted sleep is **explicitly excluded** — the
  in-code comment reads *"scripted self-sleep: an action, but never
  companion-sourced negation"* (`:255-257`).
- **Frozen v2 itself is the repo's soft-control precedent**: the enemy still
  acts, at `FROZEN_DAMAGE_MULT` damage, and the state is consumed on use
  (`tier0/engine/combat.py:632-637, 656-657`). Bosses take Vulnerable 2 instead
  (`docs/teyvat-spire-design-principles.md:48`).

### 2.2 Shape B — shield-shaped (block retention / barrier / damage reduction)

#### Block retention across turns

| Name | What it is | Exact behavior | Path |
|---|---|---|---|
| **Barricade** | Ironclad 3c Rare Power | `ShouldClearBlock => Owner != creature` — block is **never** cleared, permanently | `game_ref/ironclad.json:106`; semantics `tier0/engine/refpowers.py:1356-1366` |
| **Blur** | Silent 1c Uncommon, 5 Block (+3) | The **same** `ShouldClearBlock` suppression, but on a counter that decrements at the owner's turn *start*, **after** the block clear it just suppressed — so N stacks carry block through exactly N turn boundaries | `game_ref/silent.json:312`; `refpowers.py:1196-1200, 1356-1366` |
| **Burrowed** (enemy) | The Tunneler's Barricade | Block not cleared at turn boundaries: a **one-time persistent 32-point lock per cycle**, chippable across several turns | `tunneler.md:58` |

**Negative: no Calipers-equivalent (partial block decay) exists anywhere.**

**Note:** Barricade is **excluded from the tier0 sheet as unimplemented**
(`game_ref/ironclad-cards.yaml:88`) — i.e. the precedent exists in the game but
**not** in this repo's simulator.

#### Block that does something extra

- **Body Slam** — Ironclad 1c Common Attack, `vars: {CalculationBase: 0,
  ExtraDamage: 1}`: damage scales off runtime Block. **Excluded from tier0 for
  exactly that reason** (`ironclad.json:266`; `ironclad-cards.yaml:89`).
- **Juggernaut** — Ironclad 2c Rare Power, amount **6**.
  `AfterBlockGained(creature == Owner, amount > 0)` → damage. Fires on **every**
  block gain including Plating's, Rage's and its own; once per BlockGained row.
  (`ironclad.json:1258`; amount `ironclad_pool.yaml:740`; `refpowers.py:225-233`)
- **Unmovable** — Ironclad 2c Rare Power, amount **1**.
  `ModifyBlockMultiplicative -> 2`, but **only for card-sourced block**, with a
  per-CardPlay allowance that every prior row consumes. Passive block (Plating,
  CrimsonMantle, Rage, FeelNoPain, Metallicize) is granted **Unpowered** and is
  **not** doubled. (`ironclad.json:2125`; amount `ironclad_pool.yaml:1234`;
  `refpowers.py:183-219`)
- **Afterimage** — Silent 1c Rare Power, Innate, amount 1: block per card
  played, granted Unpowered (so Unmovable does not double it).
  (`silent.json:129`; `refpowers.py:693-695`)
- **Pillar of Creation** — Regent 1c Uncommon Power, `vars: {Block: 3}` (+1).
  (`regent.json:1583`)

#### Damage reduction that is not Block

- **Intangible — a CAP, not a multiplier**, and the last word in the pipeline:
  `ModifyDamageCap` returns 1 and `ModifyHpLostAfterOsty` clamps HP loss to 1
  on top. Damage already below 1 is untouched — *"Intangible does not round a 0
  up."* (`tier0/engine/refpowers.py:1075-1090`; `tier0/constants.py:12`)
  - **Wraith Form** — Silent 3c **Ancient** Power: `DexterityPower +
    IntangiblePower + WraithFormPower`. Intangible **2** up front; the
    WraithForm half applies **−Amount Dexterity to its own owner every turn,
    forever** — a Debuff on the owner that never expires.
    (`silent.json:2236`; amounts `silent_pool.yaml:1450-1454`;
    `refpowers.py:1206-1215`)
  - **Eidolon** — Necrobinder 2c Rare Skill, Exhaust: `IntangiblePower` +
    `CardCmd.Exhaust`. (`necrobinder.json:696`)
- **Buffer** — Defect 2c Rare Power, `BufferPower`. **The only Buffer anywhere
  in the official pools.** (`defect.json:215`)
- **Plating — StS2's Metallicize.** **There is no card or power named
  Metallicize in the extracted data**; Plating is the shape. Grants Block equal
  to its *current amount* at `BeforeSideTurnEndEarly` (the decompiled source
  comment — *"so that it triggers before end-of-turn damage effects"* — is
  quoted in-tree), and decrements at turn start, **skipped on turn 1**
  (`TurnNumber != 1`).
  - **Stone Armor** — Ironclad 1c Uncommon Power (`ironclad.json:1840`);
    **excluded from tier0** (`ironclad-cards.yaml:128`)
  - **Neutron Aegis** — Regent 1c **Rare** Power, same `PlatingPower`
    (`regent.json:1406`)
  - Semantics: `refpowers.py:1186-1189` (decrement), `:1232-1240` (grant)
- **Colossus** — Ironclad 1c Uncommon, 5 Block (+3), `ColossusPower +
  VulnerablePower`. `ModifyDamageMultiplicative -> 0.5` when the target is the
  owner, the hit is a **powered attack**, **and the dealer has Vulnerable**.
  **The card does not apply Vulnerable** — that entry is a hover tip only, so it
  never self-enables. (`ironclad.json:481`; `refpowers.py:1044-1050`)
- **Feel No Pain** — Ironclad 1c Uncommon Power, Exhaust, amount **3**: block on
  each card exhausted, granted **Unpowered** (bypasses Unmovable).
  (`ironclad.json:876`; amount `ironclad-cards.yaml:46`; `refpowers.py:306-308`)
- **Crimson Mantle** — Ironclad 1c Rare Power, amount **8**: at player turn
  start take Unblockable+Unpowered self-damage equal to `SelfDamage` (a counter
  incremented once per copy played), **then** gain Amount block.
  (`ironclad.json:561`; amount `ironclad-cards.yaml:44`; `refpowers.py:1146-1155`)
- **Flame Barrier** — Ironclad 2c Uncommon, 12 Block (+4) + retaliate for amount
  against an enemy dealer on a **powered attack**; **expires at enemy turn
  end**. (`ironclad.json:957`; `refpowers.py:500-504`)
- **Thorns** — the same shape with a different lifetime: `BeforeDamageReceived`,
  **no side check, no "unblocked > 0" requirement** (a fully blocked hit is
  still thorned), and it **does not expire**. (`refpowers.py:507-509`)
  - **Abrasive** — Silent 3c Rare Power, Sly: `DexterityPower 1` + `ThornsPower
    4`. (`silent.json:3`; amounts `silent-cards.yaml:36`)
- **Powers that exist with no in-repo semantics:** **Coolant** (Defect 1c Rare
  Power, `defect.json:504`), **Shroud** (Necrobinder 1c Uncommon Power,
  `DoomPower + ShroudPower`, `vars: {Block: 2}` +1, `necrobinder.json:1905`),
  **Parry** (Regent 1c Uncommon Power, `regent.json:1478`), **Reflect** (Regent
  1c Uncommon, 15 Block +5, `regent.json:1707`).
- **Tank** — Ironclad 1c Rare Power, **`CardMultiplayerConstraint.MultiplayerOnly`
  — the base game never offers it in a single-player run.**
  (`ironclad.json:1910`; ruling `ironclad-cards.yaml:141`;
  `refpowers.py:94` — `MULTIPLAYER_ONLY_CARDS = ("Tank", "DemonicShield")`).
  **This is the official precedent for a co-op-only card existing as a
  first-class thing.**

#### Pre-emptive / delayed block

- **`BlockNextTurnPower`** is the official pre-emptive-block primitive:
  **Dodge and Roll** (Silent 1c Common, 4 Block +2, `silent.json:665`) and
  **Glitterstream** (Regent 2c Common, 11 Block +2, `regent.json:863`).
- **Convergence** — Regent 1c Uncommon: `EnergyNextTurnPower + RetainHandPower +
  StarNextTurnPower`, Retain. `RetainHandPower` is **the only hand-retention
  *power* in the data.** (`regent.json:435`)
- This repo already groups the class the same way — *"Block (including
  pre-emptive/delayed Block) or character-specific buffer"*
  (`docs/archive/m7-rulings.md:179`) — and the mod's own `block_next_turn` op is
  at `tier0/engine/effects.py:640`.

#### Big flat / conditional block, for scale reference

Impervious 30(+10) Exhaust (`ironclad.json:1135`); Blood Wall 16(+4) for 2
self-HP (`:185`); Reflect 15(+5) (`regent.json:1707`); Melancholy 13(+4)
(`necrobinder.json:1184`); Fight Through 13(+4) (`defect.json:771`); Bulwark
12(+3)+Forge (`regent.json:206`); **Sacrifice** — Necrobinder 1c Rare, Retain,
`CreatureCmd.Kill + GainBlock` scaling off a calculation (**kills your own Osty
for block**, `necrobinder.json:1721`).

#### Enemy-side shield-shaped

- **Plating (enemy)** — grants Block equal to current amount at combat start
  *and* at the end of every one of its turns, then decays 1/turn (**per player**
  in co-op). Frog Knight **15** (19 Tough) → a hard per-turn damage floor: any
  turn dealing under 15 *"literally did not happen"* (`frog-knight.md:51,
  76-79`); Lagavulin Matriarch **12** (`lagavulin-matriarch.md:33`); Mysterious
  Knight **6**, self-applied on spawn (`mysterious-knight.md:53-64`); Flail
  Knight **6** ≈21 block over six turns (`flail-knight.md:87`); Slumbering
  Beetle **15**; Sewer Clam **8** (`act2-act3-roster-research.md:160`). **Co-op:
  applied amount ×((seats−1)×2+1)** — 6 → 18/30/42 — with decay rising to the
  player count (`mysterious-knight.md:119`). The block is granted **Unpowered**,
  so it dodges the player's block modifiers *and* the multiplayer block scaler.
- **Rampart** — Living Shield, **25** on itself, at the start of each *player*
  turn, granting Block **only to Turret Operators** (filter is by monster type —
  never itself, never "allies"). 25 Block vs a 41 HP body is a lockout, not a
  tax. Suppressed during player extra turns. Co-op: the counter scales ×(players
  × 1.2) → 25/60/90. (`living-shield.md:23-30, 78`)
- **Guardbot** — one self-looping move, **15 Block to every Fabricator on its
  side, never to itself**. Zero lifetime damage. (`guardbot.md:17-20`)
- **Flutter** (Thieving Hopper, 5 stacks) — flat **×0.5** against **powered
  attacks only**; loses one stack **per damage instance** landing ≥1 unblocked
  (per instance, not per point — five 1-damage pokes strip it as fast as five
  30s). Unpowered/non-attack damage is unaffected *and* does not break it.
  (`thieving-hopper.md:90-96`)
- **Slippery** (Inklet, 1 stack each, 3 bodies) — **any single instance of HP
  loss is clamped to exactly 1**, stack consumed by the first hit that lands. A
  20-damage strike deals 1; a 3×2 attack deals 1+2+2. (`inklet.md:64-65`)
- **Soar** (Owl Magistrate) — powered attack damage dealt *to the Owl* ×**50%**,
  single stack, covering exactly the one player turn between Judicial Flight and
  Verdict. (`owl-magistrate.md:42`)
- **Intangible (enemy)** — Soul Fysh's Fade, Intangible 2 once per 5-move lap
  (`soul-fysh.md:42, 117-119`); Test Subject phase 3's Nemesis toggles
  Intangible 1 on/off at every enemy turn end (`test-subject.md:203-216`).
- **Thorns (enemy)** — Spiny Toad's Protruding Spikes grants itself **Thorns 5**
  live for exactly the one following player turn; Spike Explosion removes the 5
  as part of spending them. Never stacks, never exceeds 5. (`spiny-toad.md:35-56`)
  Toadpole carries Thorns 2 (`act2-act3-roster-research.md:154`).

### 2.3 Shape C — geo-construct-shaped (persistent battlefield object / summon)

#### The core precedent: Osty (Necrobinder)

Osty is a persistent summoned pet **wired into the core damage pipeline**. The
engine's HP-loss hooks are literally named `ModifyHpLostBeforeOsty` /
`ModifyHpLostAfterOsty` (`tier0/constants.py:12`,
`tier0/engine/refpowers.py:360, 1077`; the mod mirrors the pattern at
`klee-mod/KleeCode/Powers/FurinaResources.cs:972`). **Damage passes *through*
Osty before it becomes player HP loss** — which is what makes it, in this
repo's own words, *"a persistent, non-Block damage buffer that's mechanically
legal in this ecosystem"* (`docs/archive/furina-predesign-notes.md:27`).

**`OstyCmd.Summon` is the only summon verb in all 440 official cards.** It
appears **9 times**. `Summon: N` is HP *added* to Osty — summoning is
additive/topping-up, **not** re-placing:

| Card | Cost / rarity | Summon (upg) | Rider | Path |
|---|---|---|---|---|
| **Bodyguard** | 1c **Basic** (starting deck) | 5 (+2) | — | `necrobinder.json:82` |
| **Afterlife** | 1c Common | 6 (+3) | Exhaust | `:3` |
| **PullAggro** | 2c Common | 4 (+1) | + 7 Block (+2) — **the only "aggro" verb in the game's card data** | `:1480` |
| **Cleanse** | 1c Uncommon | 3 (+2) | exhaust a card from a combat pile; Exhaust | `:265` |
| **Dirge** | 0c Uncommon | 3 (+1) | generate + upgrade cards into combat; Exhaust | `:614` |
| **Spur** | 1c Uncommon | 3 (+2) | Heal 5 (+2); Retain | `:2091` |
| **LegionOfBone** | 2c Uncommon | 6 (+2) | `target: AllAllies`, **`mp_only: true`** — co-op only | `:1131` |
| **NecroMastery** | 2c **Rare Power** | 5 (+3) | + `NecroMasteryPower` | `:1237` |
| **Reanimate** | 3c Rare | **20** (+5) | Exhaust | `:1589` |
| **Invoke** | 1c Common | 2 (+1) | **delayed**: `SummonNextTurnPower` + `EnergyNextTurnPower` | `:1101` |

**Eight more cards *read* the entity** via an `OstyDamage` var (damage routed
through / scaled by the pet): Poke 6(+3) 0c (`:1431`), Flatten 12(+4) 2c
(`:860`), Snap 7(+3) (`:1986`), Rattle 7(+2) with a calculation term (`:1563`),
SicEm 5(+1) + `SicEmPower` (`:1934`), Fetch 3(+3) 0c + draw (`:835`),
RightHandHand 4(+2) 0c (`:1696`), HighFive 11(+2) AoE + Vulnerable (`:1072`).

**Two cards *consume* the entity:** BoneShards — 1c Uncommon, `CreatureCmd.Kill`
+ AoE attack + 9 Block (+3) (`:107`); Sacrifice — 1c Rare, Retain,
`CreatureCmd.Kill` + scaling Block (`:1721`).

Osty-adjacent powers with no in-repo semantics: `DemesnePower` (3c Rare,
Ethereal, `:564`), `SentryModePower` (2c Rare, `:1829`), `FriendshipPower`
(+Strength, `:910`), `DanseMacabrePower` (`:534`), `ForbiddenGrimoirePower` (2c
**Ancient**, Eternal, `:884`).

**Starting relic — Bound Phylactery**, hook chain verbatim from the decompile:

```
BeforeCombatStart              -> OstyCmd.Summon(Summon=1)
AfterEnergyResetLate, turn > 1 -> OstyCmd.Summon(Summon=1)
```

i.e. **Osty is present from combat start and gains 1 HP every turn after the
first, for free.** Necrobinder starts at **66 HP** — the lowest of the five
canon characters — with starting deck `4× strike, 4× defend, ne_bodyguard,
ne_unleash`. (`game_ref/necrobinder_char_facts.yaml`)

**Three cross-references that matter to a future design session:**

- The repo's own tagger classifies **every** Osty summon as `solve: [block,
  frontload]` with **both tags *inherited*** — the summon card itself does
  neither; the pet does both. (`game_ref/role_tempo_canon.json`, Necrobinder
  block.) This is the machinery by which a persistent entity's contribution is
  attributed.
- *"Osty attacks AND shields, visibly, with numbers on screen"* — the legibility
  argument (`docs/axis-validity-session-charter.md:65`; the Track C principle at
  `:186-193`).
- The standing caveat: **Osty's HP can go DOWN with bad play**, unlike a
  monotone meter. (`tier0/DECISIONS.md:1517-1522`)

**Osty is a first-class creature to the rest of the game:** the Entomancer's
Hive re-attributes pet damage to the owner so *"a pet cannot launder the tax"*
(`entomancer.md:99`), and The Insatiable's devour kills *"that player's pets and
Osty"* along with the seat (`the-insatiable.md:95, 155`).

#### The second player-side persistent entity: Defect Orbs

Orbs exist and are **Defect-exclusive** (zero `orbs` entries on the other four
characters). Five types: **LightningOrb** (9 cards), **FrostOrb** (7),
**DarkOrb** (5), **PlasmaOrb** (3), **GlassOrb** (3) — GlassOrb and PlasmaOrb
are new relative to StS1. Verbs: `OrbCmd.Channel` ×21, `OrbCmd.EvokeNext` ×4,
`OrbCmd.Passive` ×2, `OrbCmd.AddSlots` ×2, `OrbCmd.RemoveSlots` ×1.

Notable rows: Dualcast 1c Basic EvokeNext (`defect.json:675`), MultiCast 0c Rare
(`:1435`), Quadcast 1c **Ancient** (`:1513`), Shatter 1c Rare AoE + EvokeNext
(`:1728`), Chaos 1c Uncommon Channel with `upgrades: {Repeat: +1}` (`:291`),
Rainbow 2c Rare channels Dark+Frost+Lightning (`:1534`), Capacitor 1c Uncommon
AddSlots (`:268`), Modded 0c Rare AddSlots + draw (`:1387`), **BulkUp** 2c
Uncommon **RemoveSlots + Str/Dex — trades slots for stats** (`:239`), Darkness
1c Uncommon `OrbCmd.Passive` DarkOrb (`:579`), TeslaCoil 0c Uncommon attack +
Passive (`:2084`), Voltaic 3c Rare Exhaust with a Calculation term (`:2214`).

Starting relic **Cracked Core**: `BeforeSideTurnStart -> if TurnNumber <= 1:
OrbCmd.Channel<LightningOrb>() x1`. Defect starts at **75 HP**, deck `4/4 +
de_zap + de_dualcast`. (`game_ref/defect_char_facts.yaml`)

**tier0 has no orb system at all** — no hook in `tier0/engine/relics.py` can
express "channel an orb", and the repo deliberately refused to invent one.

#### Regent's Forge — unresolved

`ForgeCmd.Forge` appears on **10** Regent cards: BeatIntoShape (`regent.json:77`),
BigBang (`:128`), Bulwark (`:206`), Conqueror (`:408`), Furnace (`:735`),
RefineBlade (`:1680`), SeekingEdge (`:1810`), SpoilsOfBattle (`:1937`),
**SummonForth** (`:2008` — 1c Uncommon, Retain, `CardPileCmd.Add +
ForgeCmd.Forge`; **the name says summon, the verbs say card generation**),
TheSmith (`:2129`, upgrade `Forge: +10`), WroughtInWar (`:2229`). Plus
`PillarOfCreationPower`, `OrbitPower` (`:1428`), `GenesisPower` (`:815`).
Regent's other resource is **Stars** (`PlayerCmd.GainStars`; relic Divine Right
= +3 Stars per combat room, `game_ref/regent_char_facts.yaml`).

**Whether Forge produces a battlefield object or is a pure meter could not be
confirmed from this repo.** Flagged as unresolved rather than guessed.

#### Player-side negatives

1. **Ironclad and Silent have zero summons, zero orbs, zero persistent
   entities.** Ironclad's Shape-C regex hit count is 0. Silent's single hit was
   **StormOfSteel** (`silent.json:1900`) — a discard-and-upgrade skill,
   name-only false positive.
2. **No totem, no trap, no timed-expiry entity, and no decoy anywhere in the
   player card data.** Osty has HP, not a timer; orbs have slots, not a timer.
3. **No taunt / aggro-redirect power exists.** `PullAggro` is the only card that
   names the concept, and it is `Summon 4 + Block 7` — the "aggro" is flavour
   for the pet body. *(This matches the repo's own logged gap: "No taunt verb
   exists in the DSL (implement-or-log: LOGGED as out of v0.1 scope — a
   taunt/redirect op is a later design conversation, not silently
   approximated)" — `docs/inazuma-companions.yaml:79-80`.)*

#### Enemy-side summoners

| Enemy | Behavior | Path |
|---|---|---|
| **Fabricator** (Act 3 elite) | **Fabricate** spawns **two** bots (one defensive then one aggressive); **Fabricating Strike** attacks *and* spawns one aggressive bot. Population cap **4**, gate reads *living* creatures — **so clearing the board re-arms the summoner**, inverting the normal swarm instinct. Anti-repeat excludes the last spawn but the pools are disjoint so it almost never binds. **Fabricating Strike is hidden from the bestiary**, so a player consulting the codex under-reads the summon rate. Killing the Fabricator kills every bot outright. Cap is seat-count independent | `fabricator.md:18-24, 39, 56-58, 86-91, 104-108` |
| **Ovicopter** | Deterministic 3-beat cycle whose beat 1 is either **Lay up to 3 Tough Eggs** or +3 Strength. Six slots (`egg1`–`egg5` + parent) | `ovicopter.md:20-30` |
| **Living Fog** | **Bloat** summons exactly **1** Gas Bomb per cast into the next free bomb slot, then attacks. Five reserved bomb slots; **the summon silently does nothing if no slot is free** (the attack still resolves). Two-turn metronome | `living-fog.md:27, 43-45` |
| **Fogmog** | Turn 1 is a **pure summon** (Eye With Teeth into the reserved `illusion` slot), and the machine never routes back, so **exactly one Eye exists per fight, forever**. Turn 1 is a free player turn | `fogmog.md:26, 37, 43` |
| **Two-Tailed Rat** | **Call for Backup** requires **all four**: ≥2 non-summon moves resolved (earliest telegraph is its 3rd turn), shared call-count < 3, an empty slot, **and no living ally already telegraphing a summon** — so the board grows by at most one per turn. Once per rat. When eligible the branch is taken **75%** of the time | `two-tailed-rat.md:37-44, 90` |
| **Gremlin Merc** | Carries a "surprise" buff that (a) prevents combat resolving and (b) on its death spawns a **Sneaky Gremlin + Fat Gremlin** onto the empty board | `gremlin-merc.md:60` |
| **Phrog Parasite** | **Infested (4)**, self-applied on room entry: prevents combat ending; on death spawns **four Wrigglers** into four reserved slots, all stunned turn 1. The visible HP bar is *"a lie about fight length"* | `phrog-parasite.md:78-79` |
| **Axebot** | **Self-respawn.** Enters with 2 stacks acting as spare bodies; on death a brand-new Axebot is added to the same slot with one fewer stack. The buff also prevents combat ending. Boot Up's Strength gain is `base × (2 − remaining stock)`, so body 1 is routed away from it and bodies 2/3 get ×1 and ×2. Every respawn is HP-scaled at creation | `axebot.md:26, 52, 68, 86` |

#### Enemy-side: things that ARE objects

- **Gas Bomb** — 7 HP, created during the enemy turn so it never acts on spawn;
  sits with **Explode** telegraphed through exactly one player turn, then
  detonates for 8. No block, no debuff, no other move. The exchange rate (spend
  7 to deny 8) is set *"just barely in the player's favour so that neither line
  is obviously wrong"* — but damage into it **does not shorten the fight**: it
  is a **recurring toll, not an objective**. HP scales with seats (~15 at 2p,
  ~23 at 3p) — **worse than proportional**. (`gas-bomb.md:19, 43-54, 69`)
- **Tough Egg** — opening state is `HATCH` (a **summon intent**). 14–18 HP with
  a one-turn fuse. **On hatching it clears every power it carries except
  Minion** — so all Poison/Vulnerable/Weak invested in the shell is wiped and HP
  is re-rolled as a Hatchling (19–22 HP, 4 damage/turn forever). **Chip damage
  into an unhatched egg is refunded to the enemy**; eggs must be killed outright.
  (`tough-egg.md:30, 46`; `ovicopter.md:70-76`)
- **Eye With Teeth** — 6 HP, Illusion-tagged, unkillable (see §2.1). Killing it
  buys exactly one Dazed-free turn for 6 damage, repeatable indefinitely, with
  no kill count at which it stops. **It does not scale with seats at all** —
  created mid-combat, so at higher seat counts its relative cost *falls*.
  (`eye-with-teeth.md:47-57`; `fogmog.md:146`)
- **Parafright** (The Obscura) — 21 HP Illusion, same revive loop, **21 HP at
  every ascension**. Refuses to receive powers while reviving.
  (`the-obscura.md:72-74`; `parafright.md:117`)
- **Living Shield** — a 55 HP body with no attack worth naming and **no death
  SFX**; its damage-SFX category reads as *armor* rather than flesh.
  *"Cosmetically it is a piece of equipment, not a creature."*
  (`living-shield.md:44`)
- **Bygone Effigy** — a statue; damage feedback is stone-flavoured, *"the tell
  that this is a statue that will eventually move."* (`bygone-effigy.md:49`)

#### The `Minion` power — the load-bearing engine concept for Shape C

`Minion` marks its owner a **secondary enemy**: its death is not fatal to the
encounter, the flag **survives its applier's death**, and **when the last
non-minion enemy dies, every surviving minion is killed outright.** Carriers:
Fabricator's bots (`fabricator.md:87`), Kin Followers (`kin-priest.md:32,
131-133`), Gas Bombs (`gas-bomb.md:50`), Tough Eggs (`tough-egg.md:46`), Eye
With Teeth (`eye-with-teeth.md:49`), Torch-Head Amalgam
(`torch-head-amalgam.md:23-31`). It is also what makes Illusion bodies immune to
"doom"-style add-removal (`fogmog.md:98`, `rocket.md:98`).

#### What this repo already ships that is Shape-C-adjacent

Recorded because the check-if-solved norm will demand it:

- **`summon_kurage`** — Kokomi's Bake-Kurage, *"a persistent summon… The
  jellyfish holds the field for KURAGE_DURATION turns and pulses at the owner's
  turn end. Stacks ARE turns remaining — **the oz_summon grammar** — so this
  REFRESHES to the full duration rather than adding to it."*
  (`tier0/engine/effects.py:1979-1996`; constants at `tier0/constants.py:375,
  401, 403, 479`). Note this is a **timer**, where Osty is **HP** — the two
  in-ecosystem persistent-entity grammars differ.
- **The drafter prices it** at one pulse via `STATIC_PERSISTENT_PROC_SHARE = 1.0`
  *"because the bank read is invisible at offer time"* (`tier05/draft.py:47`;
  rationale `tier0/constants.py:856-861`).
- **`albedo_solar_isotoma`** — a **shipped Geo defensive engine**: `apply_power
  solar_isotoma 3`, *"3 turns: your attacks vs aura'd enemies grant 3 block
  (Crystallize engine)"* (`docs/mondstadt-companions.yaml:71-72`; live in both
  engines — `tier0/engine/effects.py:359, 2573` and
  `klee-mod/KleeCode/Cards/Generated/AlbedoSolarIsotoma.cs`). **The repo has
  already flagged the collision risk itself**: *"OVERLAP FLAGGED, NOT RESOLVED:
  Albedo's solar_isotoma is already 'Geo defensive engine'"*
  (`docs/fontaine-companions.yaml:97`).
- **The mod has no summon/entity op besides `summon_kurage`**, and **no stun,
  skip, intent, or taunt op at all** — the complete `OPS` table is at
  `tier0/engine/effects.py:2152-2211`. `block_next_turn` (`:640`) is the
  pre-emptive-block op.

### 2.4 The Downfall mod

#### There are two Downfalls, and they diverge mechanically

This distinction is load-bearing and is the first thing a future session needs.

| | **StS1 Downfall** | **StS2 Downfall** |
|---|---|---|
| Source | `slaythespiredownfall.wiki.gg` (StS1 expansion, Steam app 1865780) | **`github.com/lamali292/Downfall`** — C#/Godot, MIT, actively updated |
| Characters | Hermit, Slime Boss, Guardian, Hexaghost, Champ, Automaton, Collector, Awakened, Gremlins, Snecko | same folder set; `{Char}Code/` + `{Char}/localization/eng/*.json` |

Terminology diverges (StS1 Automaton "Encoding Queue" vs StS2 "Sequence"/"Stash
Pile"), and at least one mechanic **changed shape entirely** across the port
(Collector's Torchhead — see C9 below). **StS1 wiki text is not StS2
precedent.** Every row below is labelled.

**This repo already names the right one.** `docs/archive/csharp-build-spec.md:19`
directs "Clone the Downfall fork (lamali292/Downfall) as the structural
template", and `docs/archive/animation-sprint-1-plan.md:7,11` treats it as the
reference implementation. The standing license posture is **reference-reading
only**: *"Downfall is reference-reading only. Patterns and node inventories may
be mirrored; do not copy scene files, art, or code verbatim into our tree."*
(`docs/archive/animation-sprint-1-plan.md:64`; restated
`docs/animation-sprint-2-plan.md:93`). Accordingly this section records
behavior and names only.

**A further fact that reframes the whole scan:** several of these shapes exist
in **vanilla StS2**, so Downfall did not have to invent them — it reused
first-party frameworks. Where that is true it is stated, because it changes
which precedent a design session should cite.

#### Shape A in Downfall — a true player-applied enemy stun exists

**`Cheap Shot` — The Champ, StS2 Downfall.** This is the single most
decision-relevant precedent in this document, because it is the thing official
StS2 does **not** have.

- **Card text:** *"Deal {Damage} damage. If the enemy is a Boss, deal damage
  two more times. If not, **Stun** it."*
- **Literals from `ChampCode/Cards/Rare/CheapShot.cs`:** Rarity **Rare**. Cost
  **2**, `WithCostUpgradeBy(-1)` → **1 upgraded**. Damage **5**. Boss branch:
  `CardAttack(this, cardPlay, 3)` → 3 hits, **15 total, and the stun is skipped
  entirely**. Non-boss branch: `CreatureCmd.Stun(cardPlay.Target)`, 1 stack.
- **How it was balanced** — the whole guardrail, stated plainly: **rarity
  (Rare) + cost (2) + tiny damage (5) + a hard boss exclusion.** Against a Boss
  the card converts into a damage card. *Stun does not exist against bosses.*
- `https://github.com/lamali292/Downfall/blob/main/ChampCode/Cards/Rare/CheapShot.cs`;
  `https://github.com/lamali292/Downfall/blob/main/Champ/localization/eng/cards.json`

**`StunnedPower` — the implementation.** On the affected creature's turn start,
sets its **energy to 0** and prevents it drawing cards; blocks automatic card
plays. `PowerStackType.Single` — **does not stack**. Removes itself at the end
of that side's turn: **exactly one turn**. **No immunity check exists in the
code** (the boss carve-out lives on the card, not the power). A TODO notes
potion-use prevention is unimplemented.
— `https://github.com/lamali292/Downfall/blob/main/DownfallCode/Powers/StunnedPower.cs`

**`NextTurnStunnedPower` — a delayed stun.** On `BeforeSideTurnEnd` it applies
1 stack of StunnedPower **to its owner**, then removes itself. A one-turn fuse.
— `https://github.com/lamali292/Downfall/blob/main/DownfallCode/Powers/NextTurnStunnedPower.cs`

**`EntangledPower` — "cannot attack", pointed at the player.** Blocks the
owner playing **Attack** cards; `Single`; auto-removes on `BeforeSideTurnEnd`.
— `https://github.com/lamali292/Downfall/blob/main/DownfallCode/Powers/EntangledPower.cs`

**Vanilla StS2 already defines Stun — and it is unkeyworded card text.** The
Spire Codex states *"Stun prevents an enemy from acting on its next turn."*
There is **no keyword page**; it is card text. Vanilla powers referencing it:
`Burrowed` (*"Block is not removed at the start of this creature's turn.
**Stunned if all Block is removed.**"*), plus `Plow`, `Shriek`, `Skittish`,
`Strangle` — which is exactly the enemy-self-state set §2.1 found in the
extraction, seen from the other side.
— `https://spire-codex.com/guides/keywords-guide`;
`https://spire-codex.com/powers/burrowed`; `https://spire-codex.com/powers`
Consistent with this, **no Downfall character ships a "Stun" hover-tip** in its
`static_hover_tips.json`.

**Intent-*reading* is a recurring Downfall idiom — intent-*altering* is not.**
The Gremlins condition on intent without touching it: `BELLOW` (*"Gain
{Strength} Strength for each enemy that does not intend to Attack"*),
`COUNTER_STRIKE` (*"If the enemy intends to attack, trigger your current
Gremlin's Bonus"*), `FEEL_THE_AUDIENCE`, `PROPER_TOOLS`.
— `https://github.com/lamali292/Downfall/blob/main/Gremlins/localization/eng/cards.json`

**Player-side self-skip:** `GUARDIAN-GIGA_BEAM` — *"Deal damage to ALL enemies.
Strength affects X times. **Skip next turn.**"* The Guardian skips **its own**
turn: a self-cost, not enemy denial — the boss's signature move ported as a
player drawback.
— `https://github.com/lamali292/Downfall/blob/main/Guardian/localization/eng/cards.json`

**StS1-lineage stun (secondary).** The StS1 Downfall wiki's Cards List contains
*"Deal 13 damage to ALL enemies. Stun any that don't intend to attack.
Exhaust."* (18 upgraded). **The card's name and owning character could not be
established** — a search engine attributed it to the Automaton; that
attribution is unsourced. **HEARSAY, recorded as such.** Independently, StS1
bosses `Defect (Energy Thief)` and `Defect (Ancient Construct)` carry the trait
**"Can't be Stunned"** — confirming StS1 Downfall's stun is real *and that
boss-level stun immunity is the balancing lever there too*, the same shape as
Cheap Shot's carve-out.
— `https://slaythespiredownfall.wiki.gg/wiki/Cards_List`;
`.../Defect_(Energy_Thief)`; `.../Defect_(Ancient_Construct)`

**Shape A negatives in Downfall.** No taunt/redirect debuff anywhere —
`CHAMP-TAUNT` is titled **"Provoke"** and is only *"Apply Weak and Vulnerable
(to ALL enemies)"*, a pure debuff with no aggro mechanic; `CHAMP-REDIRECT` is
card manipulation (*"Put the next card you play this turn on top of your Draw
Pile"*). No intent scramble, cancellation, or rerolling in any StS2 Downfall
character. Card-text scans of **Awakened, Hermit, Automaton, SlimeBoss,
Hexaghost, Snecko, Gremlins, Guardian** returned **zero** stun/skip/taunt
cards. **Stun in StS2 Downfall is one card on one character.**

#### Shape B in Downfall — the Guardian's Mode Shift / Defensive Mode

**`Mode Shift`** — printed: *"When you lose HP gain 16 Block, enter Defensive
Mode until next turn, and increase the amount required to trigger this effect
again by 10, up to a maximum of 50."* Implementation
(`GuardianCode/Powers/ModeShiftPower.cs`):

- `CurrentLimit` initializes to **20**; the live counter starts there.
- The counter decrements by `result.UnblockedDamage` in `AfterDamageReceived`.
  **Blocked damage does not advance it.**
- On counter ≤ 0 → `Reset`: grant **16 Block**; apply **1 stack
  DefensiveModePower** (**2 stacks** if it is the enemy's turn and the owner
  currently has 0 — the fix for being shifted mid-enemy-turn);
  `CurrentLimit = Math.Min(CurrentLimit + 10, 50)`; counter refills to the new
  limit.
- Ramp: **20 → 30 → 40 → 50 → 50 → …**

— `https://github.com/lamali292/Downfall/blob/main/GuardianCode/Powers/ModeShiftPower.cs`

**`Brace` — the accelerator, and the design's key move.** Keyword text:
*"Brace: Reduce the HP loss required to trigger **Mode Shift**."* Rather than
"gain Block", roughly **15 Guardian cards pay into the defensive trigger**:
`Gear Up` (starter, from relic Bronze Gear), `Curl Up` (starter), `Priming
Shot`, `Recharge`, `Recover`, `Resilient Plate`, `Spheric Shield`, `Shield
Spikes`, `Piercing Hide`, `Orb Support` (*"Brace for unblocked damage dealt"*),
`Roll Attack`, `Evasive Protocol`, `Revenge Protocol`, `Spiker Protocol`,
`Shield Charger`.
— `https://github.com/lamali292/Downfall/blob/main/Guardian/localization/eng/static_hover_tips.json`

**`Defensive Mode` — a Stance, and the Barricade-shaped piece.** Keyword:
*"**Stance.** While in Defensive Mode you have **3 Thorns** and your **Block
does not expire**."* Implementation (`DefensiveModePower.cs`): genuinely
registered as a stance (`GuardianCmd.EnterDefensiveMode` / `LeaveDefensiveMode`);
`WithPower<ThornsPower>(3)` granted on enter, stripped on exit; overrides
`ShouldClearBlock(Creature)` returning true for **all creatures except the
owner** (so the owner's Block survives); auto-decrements one stack in
`AfterEnergyReset` — **one turn per stack**.
— `https://github.com/lamali292/Downfall/blob/main/GuardianCode/Powers/DefensiveModePower.cs`

Note this is **the same `ShouldClearBlock` override route** that official StS2's
Barricade and Blur use (§2.2) — a third consumer of one first-party hook.

**Guardian payload cards keyed off the stance:** `ROLL_ATTACK` (*"In Defensive
Mode: affects ALL"*), `SHIELD_SPIKES` (*"Gain Thorns if Defensive Mode"*),
`SPIKER_PROTOCOL` / `REVENGE_PROTOCOL` / `EVASIVE_PROTOCOL` (on **entering**
the stance: Thorns / Strength / `Polish 1`), `GUARDIAN_WHIRL` (*"If Block ≥
threshold, deal 2 more times"* — block-scaling attack), `BODY_CRASH` (*"Gain
Block. Deal damage equal to Block."* — the canonical block→damage converter),
`SERRATE` (*"additional damage = X times Thorns"*), `HARDEN` (*"Gain
Metallicize."*).
— `https://github.com/lamali292/Downfall/blob/main/Guardian/localization/eng/cards.json`

**Block retention outside the Guardian — always as Blur stacks, never
Barricade:**
- `CHAMP-HOLD_FIRM` — *"Gain Block. Gain Counter. Block is not removed at the
  start of your next turn."* Cost **2**, `WithBlock(10, 3)` → **10 / 13
  upgraded**, `WithPower<CounterPower>(10, 3)`; retention is
  `WithPower<BlurPower>(1, false)` — **1 stack of vanilla Blur**, not a bespoke
  power. (`ChampCode/Cards/Rare/HoldFirm.cs`)
- `HEXAGHOST-GHOST_SHIELD` — *"[Afterlife] Gain Block. Block is not removed at
  the start of your next turn."*
- `HERMIT-DISSOLVE` — *"Block is not removed at the start of your next {Blur}
  turns."*

**Non-Block damage reduction in StS2 Downfall:** `HERMIT-UNYIELDING` (*"If you
are **Vulnerable**, receive **50% less damage** this turn"* — reduction gated on
holding a debuff); `SNECKO-SERPENTSCALE` (Plated Armor, with an Overflow
rider); `HERMIT-DIVE` / `HERMIT-SCAVENGE` (Plated Armor on a "Dead On" trigger);
`AUTOMATON-PROTO_SHIELD` (*"Gain {Plating} Plating"*, `PlatingPower`);
`AUTOMATON-THUNDER_WAVE` (*"Prevent the next time you would lose HP"* —
Buffer-shaped); `SLIMEBOSS-ROLL_THROUGH`; `GUARDIAN-CONSTRUCTION_FORM` (*"Gain
Buffer. At start of turn with Buffer, gain Strength."*); and
`SLIMEBOSS-PROTECT_THE_BOSS` — *"Prevent the next time you would be damaged by
an enemy attack, **Absorbing your leading Slime instead**"* — **the one place a
summon acts as a damage sink in StS2 Downfall.**

**StS1 cross-check (secondary):** the StS1 wiki gives Mode Shift identically
(16 Block, start 20, +10, cap 50) and Defensive Mode as *"Guardian has 3 Thorns
and doesn't lose Block while active"*, plus Plated Armor / Blur / Buffer /
Intangible and a Hermit-exclusive **`Rugged` — "Reduces the next instance of
attack damage to 2"** with **no StS2 equivalent found**.
— `https://slaythespiredownfall.wiki.gg/wiki/Buffs`; `.../Mode_Shift`; `.../Guardian`

**Shape B negatives.** **No Barricade-granting player card in either Downfall** —
Barricade appears only on an *enemy* (StS1 boss `Ironclad (Bastion)`). Guardian's
Defensive Mode is **not** "gain Barricade"; it is a stance with a
`ShouldClearBlock` override — a distinct implementation route. No shield/barrier
*entity* in Shape-B form.

#### Shape C in Downfall — one true construct, and it is inherited from vanilla

**`Torchhead` — Collector, StS2 Downfall.** The direct precedent for a
persistent, HP-bearing, destroyable, player-owned battlefield object.

- **Keyword:** *"**Kindle**: Summon a **Torchhead**. If one is already
  summoned, **increase its Max HP for this combat**."*
- **The entity** (`CollectorCode/Core/TorchheadMonsterModel.cs`):
  `TorchheadMonsterModel : CustomMonsterModel`. `MinInitialHp = MaxInitialHp =
  **1**`. Health bar visible only while alive. `DeathAnimLengthOverride =
  0.2f`, no hurt SFX, no death SFX. **`AfterDamageReceivedLate` sets Max HP
  down to current HP** — every hit permanently ratchets its ceiling down, and
  it never heals back up.
- **Spawn** (`DownfallCode/Commands/DownfallCmd.Summon<T>`): added to
  **`CombatState.Allies`** — the player's side, **not** the enemy list. If an
  instance owned by the summoner is **alive** → `CreatureCmd.GainMaxHp()`
  instead of a second body; if **dead** → revived via `AddPetInternal()`; if
  **absent** → `PlayerCmd.AddPet<T>(summoner)`. Positioned at
  `playerNode.Position + Vector2(250f, -75f)`. Max HP set, then healed to full.
  `ToggleIsInteractable(true)` + `TrackBlockStatus()`. **Every summon receives
  `DieForYouPower` at 1 stack.**
- **`DieForYouPower` is vanilla StS2, not a Downfall file** — *"Osty absorbs all
  unblocked attack damage."* So the Torchhead **soaks all unblocked attack
  damage aimed at its owner**. It does not occupy an enemy slot; it persists
  across turns; **there is no timer** — it expires only by dying or by combat
  ending.
- **Cards that Kindle:** `TORCHBEARER` (Common, cost **2**, Exhaust,
  `new SummonVar(10).WithUpgrade(4)` → **10 Max HP base / 14 upgraded**);
  `WHOMP` (*"Deal damage. Kindle."*); `RAGING_CALL` (*"After you play an Attack,
  **Torchhead deals damage to ALL enemies**"*); `PROTECTING_CALL` (*"…**Torchhead
  gives you Block**"*); `BINDING_CALL` (*"…**Torchhead applies Doom to a random
  enemy**"*).
- **The construct's existence is readable game state:** relic power
  `THIMBLE_HELM_POWER` — *"**While Torchhead is alive**, gain additional Block
  from cards."*

— `https://github.com/lamali292/Downfall/blob/main/CollectorCode/Core/TorchheadMonsterModel.cs`;
`.../DownfallCode/Commands/DownfallCmd.cs`;
`.../CollectorCode/Cards/Common/Torchbearer.cs`;
`.../Collector/localization/eng/{cards,powers,static_hover_tips}.json`

**C9 — the divergence that matters most.** The **StS1** wiki describes Torchhead
as a **Temp HP power**, not a creature: *"Torchhead cards are power abilities
that gain bonus effects whenever the Collector plays an attack while possessing
Temp HP"*, Temp HP being *"Until end of combat, prevents damage to HP"* (gains
range 3 → 15). **The StS2 port converted a shield-shaped power into an
entity-shaped summon.** If the precedent rule is StS2-scoped, Torchhead is
Shape C; if StS1-scoped, it is Shape B. **The same name is two different
shapes in the two games.**
— `https://slaythespiredownfall.wiki.gg/wiki/Temp_HP`; `.../Collector`

**Vanilla StS2 underneath it — Osty again.** `Summon`: *"Summons Osty, her
skeletal companion; repeat Summons raise his Max HP for the combat."*
`Die for You`: *"Osty absorbs all unblocked attack damage."* `Summon Next Turn`:
*"At the start of your next turn, Summon 2."* `Sic 'Em` (Debuff/Counter):
*"Whenever **Osty hits this enemy** this turn, Summon 3"* — proof the pet
attacks and that enemies carry pet-interaction debuffs.
— `https://spire-codex.com/guides/keywords-guide`;
`https://spire-codex.com/powers/die_for_you`
*(Community-reported and therefore secondary: Bound Phylactery summons Osty each
turn; Osty starts at 1 HP; on death the next Summon restarts it at 1 HP with
accumulated Max HP lost; Osty is its own unit for debuff purposes. Fextralife /
StratGG tier — **treat as secondary**, and note it conflicts in emphasis with
the decompiled `necrobinder_char_facts.yaml` hook chain quoted in §2.3.)*

**The other four "summon-looking" systems are NOT entities.** This is the most
useful negative in §2.4:

| System | Character | What it actually is |
|---|---|---|
| **Slimes** | Slime Boss | **Slot-based, orb-style.** *"**Command**: Your leading Slime attacks."* Slimes live in Slime Slots; `GROW` costs *"Lose 1 Slime slot"*; `Absorb` is the removal verb (`PROTECT_THE_BOSS` absorbs the leading Slime as a one-shot damage sink). Scaling via `POTENCY_POWER` / `MINION_MASTER_POWER`. **No HP, cannot be targeted, not creatures.** The StS1 wiki explicitly compares them to **Defect Orbs** (max 4 slots, start 3, leftmost attacks first, overflow auto-absorbs oldest for 1 Strength) |
| **Gremlins** | Gremlins | **Forms, not summons.** `TAG_TEAM` (*"Swap to a living Gremlin of your choice"*), `CONGA_LINE_POWER`, `SCATTER_POWER`, `NOB_POWER`. **Only one gremlin is on the field at a time**; the other four are not battlefield objects and cannot be hit. *(StS1 detail, secondary: five units at 16 max HP, shared energy and buffs, a gremlin at 0 HP is removed and revived at the end of an Act; the run ends only when all 5 die.)* |
| **Ghostflames** | Hexaghost | **A positional track.** Six positions the character Advances/Retracts along; *"Moving onto a Ghostflame **Extinguishes** it."* The four flame types are **states on track slots**, not creatures. No HP, not targetable |
| **Function / Summon Orb / Bronze Orb** | Automaton | **Misleading names, no entities.** `SUMMON_ORB_POWER` = *"The first Attack or Skill you play each turn is placed in your Stash Pile"*; `BRONZE_ORB_POWER` = *"Stash the next card you play this turn."* Both are **card-routing powers. Nothing is summoned.** Functions are cards placed in hand |

**`Stasis` — the nearest thing to "a placed object with a timer", and it is
cards.** Guardian keyword: *"A card in **Stasis** stays for turns equal to its
**cost +1**. When it exits, it returns to your **Hand** and is **free until
played**."* **`Tick`**: *"Tick effects activate whenever this card's Stasis
counter is reduced."* **`Accelerate`**: *"Reduce the turn counter of the
right-most card in Stasis."* Stasis cards fire effects **from the zone while
waiting**: `LASER_TURRET` (*"Place into Stasis (4 turns). Tick: deal damage
randomly"*), `SHIELD_CHARGER` (*"Tick: Brace X & gain Block"*), `ORBWALK`
(*"Tick: Gain 1 Strength"*), `SENTRY_BLAST` ⇄ `SENTRY_WAVE` (each places the
other into Stasis — a self-sustaining loop). **It is the closest structural
analogue to a placed construct with an expiry clock — but it has no HP, is not
on the battlefield, and cannot be destroyed by enemies.**
— `https://github.com/lamali292/Downfall/blob/main/Guardian/localization/eng/static_hover_tips.json`

**Allies are a real first-class targeting surface, and pets share it.** StS2
Downfall's Guardian and Automaton carry co-op cards addressing **allies**:
`OVERBLOCK` (*"Entering Defensive Mode: lowest Block ally gains Block &
Thorns"*), `BASTION_POWER` (*"Whenever you Brace, all allies gain Block"*),
`AUTOMATON-SHARE_POWER`, `REFRACTED_LIGHT` (*"Gems affect ALL players"*),
`MULTI_TROPS`, plus a whole `ChampCode/Cards/Multiplayer/` directory. **The
Torchhead lives in the same `Allies` list — pets and co-op partners share one
slot space.** *(Directly relevant to this repo's Appendix A.4 ally-target
engineering, `docs/teyvat-spire-design-principles.md:234`.)*

**Shape C negatives in Downfall.** **Awakened, Hermit, Champ, Snecko, Hexaghost,
Automaton, Guardian, Gremlins: zero summon/minion/persistent-entity cards** in
StS2 Downfall (confirmed by full card-text scans of each `cards.json`). No
player construct occupies an enemy slot, and **no construct is something
enemies can choose to target** — Torchhead sits on the ally side and soaks via
`DieForYouPower`; it is not selected by enemy targeting logic. **No expiry timer
on any construct** (Torchhead persists until killed or combat ends; Slimes until
Absorbed; only Stasis — cards, not objects — has a turn counter). **No construct
can be created at a player-chosen board position** — `DownfallCmd.Summon`
hard-codes the offset `Vector2(250f, -75f)` from the summoner.

#### §2.4 coverage gap, stated

Shape A/B/C card-level scans ran against each character's English localization
`cards.json` (complete card text, but numbers appear as `{Var:diff()}`
placeholders); where an exact number mattered the C# was read and the literals
reported. **Relic and potion JSONs were not systematically scanned.** If relics
matter to a future pass, that is the remaining gap. Also unreachable this
session: `sts-downfall.fandom.com` (HTTP 402).

### 2.5 Precedent scan — the summary table

| Shape | Official StS2 | StS2 Downfall | This repo today |
|---|---|---|---|
| **A — player-applied enemy stun / skip** | **NONE.** Census of all 440 cards / 48 verbs. No stun, skip, delay or intent command exists | **`Cheap Shot`** (Champ): Rare, 2c→1c, 5 damage, **boss-excluded** (converts to 3 hits vs Boss). `StunnedPower` = energy to 0, no draw, Single, one turn, **no immunity check in the power** | **NONE.** No op in the `OPS` table. `sleep_turns` exists but is scripted enemy state only |
| **A — enemy self-stun on a provoked threshold** | **Rich.** 8+ enemies; the STUNNED move overwrites a telegraphed intent mid-player-turn | `Burrowed` (vanilla) is the same shape | `sleep_turns` + `enemy_sleep` event; excluded from `control_uptime` by design |
| **A — soft control** | Frozen not present as a player verb | `EntangledPower` (no Attacks, one turn) | **Frozen v2** — enemy still acts at `FROZEN_DAMAGE_MULT`; the *only* input to `control_uptime` |
| **B — block retention** | **Barricade** (permanent), **Blur** (N turn-boundaries); both via `ShouldClearBlock`. No partial-decay (Calipers) analogue | **Defensive Mode** stance — same `ShouldClearBlock` route, one turn per stack, +3 Thorns. Retention elsewhere is always **Blur stacks**; no player card grants Barricade | Not modelled (Barricade **excluded** from the tier0 sheet) |
| **B — damage reduction that isn't Block** | Intangible (a **cap**, not a multiplier), Buffer, Plating, Colossus (×0.5, conditional), Thorns, Flame Barrier | Plated Armor, Plating, Buffer, `UNYIELDING` (50%, gated on being Vulnerable), `Rugged` (StS1 only) | Block only; no reduction primitive |
| **B — pre-emptive / delayed block** | `BlockNextTurnPower` (Dodge and Roll, Glitterstream) | — | `block_next_turn` op |
| **C — persistent HP-bearing entity** | **Osty** — the only summon verb in the game (`OstyCmd.Summon`, 9 cards, 8 readers, 2 consumers); HP-based, no timer; sits in the HP-loss pipeline | **Torchhead** — `CustomMonsterModel` on `CombatState.Allies`, built on vanilla `DieForYouPower`; Max HP ratchets down on every hit; no timer | **`summon_kurage`** — a **timer**, not HP; refreshes rather than stacks |
| **C — slot-based non-entity** | **Defect Orbs** (5 types, Defect-exclusive) | **Slimes** (Slime Boss), explicitly orb-compared | None — tier0 has no orb system, deliberately |
| **C — taunt / redirect / decoy** | **NONE.** `PullAggro` is `Summon 4 + Block 7` | **NONE.** `CHAMP-TAUNT` is titled "Provoke" and is Weak+Vulnerable | **NONE**, and the gap is already logged (`docs/inazuma-companions.yaml:79`) |
| **C — construct placed at a chosen position** | — | **NONE** — offset is hard-coded | — |
| **co-op-only card as a first-class thing** | **Tank**, **DemonicShield** (`MultiplayerOnly`); Necrobinder's `LegionOfBone` is `mp_only` | `ChampCode/Cards/Multiplayer/`, ally-targeted Guardian/Automaton cards | — |

---

## 3. Open-questions inventory

**What this section is.** Every item is a **question** a future design session
must answer, with the relevant facts attached and **no answer given**. Where
options exist they are listed as *options that exist*, never ranked. Nothing
here is a recommendation. The Crystallize fence holds: no item below
pre-commits how Crystallize scales.

**How to read the tags.** `[BLOCKED]` = cannot be opened until a named gate
lands. `[FACTUAL]` = resolvable by looking something up, not by deciding.
`[RULING]` = needs a [USER] decision. `[SCOPE]` = a budget/boundary question.

### 3.1 Questions that precede the deep dive itself

**Q1 `[BLOCKED]` — Does R88 countersign as written, and if so, which text
governs the reserved-character rule?**
Facts: R88 is DRAFT and unsigned (`tier0/DECISIONS.md:2913`), is the stated
blocker (`docs/axis-validity-session-charter.md:19`), and its reserved-character
clause conflicts with ratified R52 (`tier0/DECISIONS.md:1348-1351`) and with
shipped Neuvillette content (`docs/fontaine-companions.yaml:128, 201, 203, 206,
210`). **Nothing in this dossier depends on the answer; the dossier waits.**

**Q2 `[BLOCKED]` — Are A4 and B3 satisfied, and does the seven-axis framework
carry load again before slot 4 declares axes?**
Facts: the deep dive unblocks on **A4 + B3**
(`docs/axis-validity-session-charter.md:207-209`); A4 ("Kit in the keywords,
verbs in the cards") is binding on Zhongli **before he authors a card**
(`:171-174`); axis numbers are currently *"reportable but not load-bearing"*
(`tier0/DECISIONS.md:2440-2442`); and the fence exists precisely because *"slot
4 must not declare elite axes against a framework nobody trusts"*
(`tier0/DECISIONS.md:2433-2436`). The alternative (A4 only) *"was offered and
stands rejected unless [USER] says 'A only'"* (`:208-209`).

**Q3 `[FACTUAL]` — Which 18 registry findings must close, and in what order?**
Facts: the enumerated list is at
`docs/serenitea-sweep-log-2026-07-26.md:819-840`. One of them is
self-referential to this dossier's subject matter — *archetype registry
"declares 'geo', which no card carries"* (`:837`) — i.e. **the gate cannot close
until Geo cards exist, and Geo cards cannot be authored until the gate opens.**
A future session must decide how that ordering resolves; this dossier only
records that it is circular as written.

### 3.2 Questions about the petrify (Shape A)

**Q4 `[RULING]` — Does §2.2a's stated premise survive contact with the
extraction?**
Facts: §2.2a justifies its scarcity rule by citing *"an act-3 Ancient reward at
3 energy + Exhaust; looping it is a known degenerate win"*
(`docs/teyvat-spire-design-principles.md:44`). The extraction of all 440
official cards finds **no player-applied stun of any kind** (§2.1), and the
nearest Ancient-tier card is Wraith Form — Intangible, not stun. Either §2.2a
was written against StS1, or against a card the extractor does not surface.
**The rule may be correct while its stated evidence is wrong.** Which it is,
this dossier does not decide.

**Q5 `[RULING]` — Is Downfall's `Cheap Shot` an admissible precedent under this
repo's rules, or does it fall outside them?**
Facts: the repo's actual instruments are Pillar 1 ("Spire first"), the subsystem
budget, and check-if-solved (§2 preamble) — **none of which says "official
first-party only"**. Downfall is treated as the structural reference
(`docs/archive/csharp-build-spec.md:19`) but is **reference-reading only**
(`docs/archive/animation-sprint-1-plan.md:64`). Meanwhile §2.2a's own text
locates full stun in *"payoff-tier design space only (rare character cards,
artifact sets, 5-star kits)"* — and Cheap Shot is exactly a Rare character card.
**Whether a mod precedent counts is undecided in the repo and is decided
nowhere in this document.**

**Q6 `[FACTUAL]` — What is the boss carve-out's status as a pattern?**
Facts: it appears **twice, independently**: StS2 Downfall's Cheap Shot converts
to damage against a Boss, and StS1 Downfall bosses carry *"Can't be Stunned"*.
Canon Genshin does **not** state a general boss-immunity rule — only specific
documented cases (C14). This repo already has a boss carve-out **in the same
place**: Frozen gives bosses *"Vulnerable 2 instead"*
(`docs/teyvat-spire-design-principles.md:48`). Question: is that three
independent arrivals at one answer, or one answer copied twice?

**Q7 `[FACTUAL]` — Which of the two canon petrify readings is the subject?**
Facts: the canon text says *"Opponents affected by the Petrification status
**cannot move**"* (C11) — narrowly, movement, not action. Official StS2's stun
family is *action* denial. Downfall's `StunnedPower` is energy-to-zero. **These
are three different verbs sharing one English word.** Which one "petrify" means
here is undecided.

**Q8 `[FACTUAL]` — Does the `control_uptime` detector actually detect
anything?**
Facts: §2.2a names it as the enforcement mechanism
(`docs/teyvat-spire-design-principles.md:44`). It is computed at
`tier0/harness/metrics.py:349` and its **only** input is `frozen_action` with
`by_companion` true (`:258-261`). Scripted sleep is explicitly excluded
(`:255-257`). So the detector as built measures *companion-sourced Frozen and
nothing else*. **Whether it would see a character-sourced turn-denial at all is
an open engineering question**, and §2.2a's threshold is stated against a
quantity the instrument may not currently compute.

**Q9 `[FACTUAL]` — Is the Bygone Effigy's dead re-sleep hook usable, and does
using it mean anything?**
Facts: the hook is registered, carries a sleep intent, and has its follow-up
wired to Slash, but **nothing reaches it**; the dossier's ruling is *"treat 'the
Effigy can be put back to sleep' as designed-for but not implemented"*
(`docs/enemy-dossiers/bygone-effigy.md:24`). Question for a session: does an
unreached first-party hook count as precedent, as anti-precedent (they built it
and cut it), or as neither?

### 3.3 Questions about the shield (Shape B)

**Q10 `[RULING]` — Which of the three retention routes is the reference, and
does this repo have any of them?**
Facts: official StS2 has **Barricade** (permanent) and **Blur** (N boundaries),
both via `ShouldClearBlock`; Downfall adds a **stance** using the same override.
**This repo models none of them** — Barricade is excluded from the tier0 sheet
as unimplemented (`game_ref/ironclad-cards.yaml:88`), and the mod's only
block-timing op is `block_next_turn` (`tier0/engine/effects.py:640`).

**Q11 `[FACTUAL]` — Is the canon shield one term or two, and does the
distinction survive translation?**
Facts: canon Jade Shield is **flat base absorption + %Max-HP** (C8/C9), the
150% is a **multiplier on the pool against all damage types** (C6/C7), and A4
"Dominance of Earth" makes **Max HP the offensive stat too** (C16). Whether a
Block-shaped translation can carry a two-term pool, a universal multiplier, and
an HP-scaling offense simultaneously is undecided.

**Q12 `[SCOPE]` — Does the healing law bind here, and how?**
Facts: Guardrail 6 — *"True in-combat healing is Rare-tier AND Exhausts; below
Rare, sustain routes through Block or character-specific buffer pools"*
(`docs/teyvat-spire-design-principles.md:211`). Canon **C6 (Chrysos)** converts
40% of shield-absorbed damage into HP, capped at 8% Max HP per instance — i.e.
canon's constellation-six *is* repeatable in-combat healing. This is a known
collision between a canon fact and a standing law, **flagged and not resolved.**

**Q13 `[FACTUAL]` — What does the 20% RES shred become?**
Facts: canon's Jade Shield decreases enemy Elemental and Physical RES by 20% and
*"cannot be stacked"* (C6); Geo Resonance adds a separate 20% Geo-RES shred
(C19). This repo **deliberately does not adopt elemental resistance matrices** —
*"Genshin's stat sheet stays home"*
(`docs/teyvat-spire-design-principles.md:27`). So the canon effect has **no
referent** in the mod's stat model. Whether it maps to something else, or is
dropped, is undecided.

**Q14 `[FACTUAL]` — Is there a Genshin-side object precedent for a shield
item?**
Facts: this repo already answered a neighbouring question and recorded a
negative: *"Genshin has no object that grants a shield: shielding is a character
mechanic (Geo constructs, Crystallize, Zhongli's jade shell), never a carried
trinket, so no canon item is a one-to-one for '10 Block at combat start'"*
(`review/potion-relic-gallery/gallery.md:347`). Relevant to relic-slot work, not
to cards.

### 3.4 Questions about geo constructs (Shape C)

**Q15 `[RULING]` — HP or timer?**
Facts: the two available grammars differ. **Osty is HP** — no timer, additive
summons, and its HP *"can go DOWN with bad play"*
(`tier0/DECISIONS.md:1517-1522`). **Bake-Kurage is a timer** — *"Stacks ARE
turns remaining… so this REFRESHES to the full duration rather than adding to
it"* (`tier0/engine/effects.py:1979-1996`). Downfall's Torchhead is **HP with a
downward-ratcheting ceiling**. Canon geo constructs are **both**: 30s duration
(C5) *and* creator-inherited HP that enemies destroy (C22, C25). **Which grammar
the repo would be building in is undecided, and only one of the two exists in
the engine today.**

**Q16 `[SCOPE]` — Does the construct need to be targetable, and by whom?**
Facts: **no player construct in official StS2 or in StS2 Downfall occupies an
enemy slot or is selected by enemy targeting logic** — Torchhead sits on the
ally side and soaks via `DieForYouPower` (§2.4). Canon is the opposite: enemies
actively destroy constructs (C25 — Dvalin's bombs are blocked by them, La
Signora's whip one-shots them, Kairagi charges destroy them). **The canon
behavior has no precedent in either codebase.**

**Q17 `[FACTUAL]` — What does resonance read, and is that quantity available?**
Facts: canon resonance is **construct-count-dependent, from any source** (C24),
with a 3-construct player cap that is shared **including in co-op** (C21). The
repo has exactly one persistent-entity op and it is single-instance by
construction (`summon_kurage` refreshes rather than stacks). **A count-reading
mechanic has nothing to count today.**

**Q18 `[SCOPE]` — Is the Albedo overlap a collision, and who moves?**
Facts: `albedo_solar_isotoma` is a **shipped Geo defensive engine** in both
engines (`docs/mondstadt-companions.yaml:71-72`). The repo has already flagged
this itself twice: *"OVERLAP FLAGGED, NOT RESOLVED"*
(`docs/fontaine-companions.yaml:97`) and *"if red-pen reads two as one too many,
Navia is the one to move, because Albedo predates her and anchors Mondstadt"*
(`docs/fontaine-rares-banner-sprint-log.md:49-53`). **That precedent names
Navia, not Zhongli — the same reasoning has never been run against slot 4.**

**Q19 `[FACTUAL]` — Does the taunt gap need to close?**
Facts: **no taunt/redirect/decoy exists in official StS2, in StS2 Downfall, or
in this repo's DSL.** The gap is already logged as a deliberate deferral: *"a
taunt/redirect op is a later design conversation, not silently approximated"*
(`docs/inazuma-companions.yaml:79`), and Itto — the character who lost slot 4 to
Zhongli — is the one carrying that unbuilt verb (`:76`).

**Q20 `[SCOPE]` — What does the co-op surface owe?**
Facts: Downfall puts **pets and co-op allies in the same `Allies` list** (§2.4),
official StS2 ships genuinely multiplayer-only cards (`Tank`, `DemonicShield`,
`LegionOfBone`), and this repo's Appendix A.4 ally-target engineering is
**waived and deferred to Columbina** (`docs/brief-coop-charter-items.md:172-176`;
`docs/teyvat-spire-design-principles.md:234`). Whether a slot-4 construct
touches that surface early — the exact deviation Furina was criticised for — is
undecided. Note also there is **no sim backstop for co-op**: tier 0.5 models one
seat.

### 3.5 Budget and template questions

**Q21 `[SCOPE]` — What is the keyword census, against a budget of ≤2?**
Facts: Guardrail 5 — *"New keywords per character: ≤2 beyond the shared element
system"*, with a support-protagonist exception that does **not** apply to a
carry (`docs/teyvat-spire-design-principles.md:210`). Precedent census: Klee 2
(Bombs, Sparks); Furina 3, ratified as an amendment paid for *"with flavor-only
stances, zero new reaction content, and Salon riding existing rails"*
(`docs/furina-kickoff-v0.1.md:150-159`). The canon kit presents **at least three
candidate systems** (shield pool, construct, petrify) plus Crystallize, which is
shared-system. **The arithmetic is the question; this dossier does not do it.**

**Q22 `[SCOPE]` — Which one thing is the Ghostflames-scale subsystem?**
Facts: *"One Ghostflames-scale subsystem… `Rejected:` two novel subsystems per
character; Downfall's data says the subsystem is 70% of the engineering"*
(`docs/teyvat-spire-design-principles.md:79`). Of the three canon candidates,
**at most one can be it.**

**Q23 `[FACTUAL]` — What does check-if-solved return?**
Facts: the norm is *"audit Necrobinder/Osty and BaseLib summon machinery before
building anything… ships on existing rails or it ships smaller"*
(`docs/furina-kickoff-v0.1.md:146-149`), scored 4-for-4
(`docs/archive/furina-sprint-1-redpen.md:112`). §2.3 and §2.4 of this dossier
**are** that audit for the summon half. **The stun half returns nothing in
first-party StS2** (§2.1), and the block-retention half returns a hook this repo
has never modelled (Q10).

**Q24 `[FACTUAL]` — What is the cadence grade, and does it interact with
Crystallize?**
Facts: §2.3 requires each character declare Catalyst-grade or Skill-grade
(`docs/teyvat-spire-design-principles.md:60-62`); Geo *"leaves no aura"* and only
triggers (`:36`), Crystallize **consumes**
(`docs/inazuma-companions.yaml:25`) and grants `CRYSTALLIZE_BLOCK = 4`
(`tier0/constants.py:52`, `tier0/engine/reactions.py:101-102`). A Geo character
therefore **cannot fuel its own reactions** — Pillar 2 by construction (`:23`).
What that implies for companion appetite (§4.4) is undecided.

**Q25 `[FACTUAL]` — What are the statline asymmetry picks?**
Facts: Pillar 3 requires 4–5 on exactly two axes and ≤2 on at least one, *"the
weakness is load-bearing"* (`docs/teyvat-spire-design-principles.md:24`) — and
this is the exact declaration Q2's gate forbids until the framework is trusted
again.

**Q26 `[FACTUAL]` — Which names are burned?**
Facts: `docs/reserved-card-names.txt` fences the Silent's 88 base-game names and
records that **the Ironclad's 87 are NOT covered** (`:36`) — so a green lint
means "no collision with the Silent", not "no collision with the base game".
Constellation names (§1.5) are the repo's designated source for rare/upgrade
names (`docs/teyvat-spire-design-principles.md:83`). No collision check has been
run against them.

**Open questions catalogued: 26 (Q1–Q26). Decided: 0.**

---

## 4. What this dossier deliberately does not contain

- **No proposed cards, keywords, numbers, archetypes, or statlines.**
- **No ranking of the options in §3.** Where two or three routes exist, all are
  listed and none is preferred.
- **No position on R88**, and nothing that depends on how it lands.
- **No Crystallize scaling.** The fence at `docs/fontaine-companions.yaml:94-96`
  and `docs/fontaine-rares-banner-sprint-log.md:49-51` is intact.
- **No decompiled source.** §2's `game_ref/` citations are behavioral notes and
  path:line references only; nothing was copied into the tree, and `game_ref/`
  remains gitignored.
- **No Downfall code.** §2.4 records behavior, class names, and printed card
  text only, per the reference-reading-only posture
  (`docs/archive/animation-sprint-1-plan.md:64`).
