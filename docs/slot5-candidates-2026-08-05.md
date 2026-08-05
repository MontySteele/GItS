# Slot-5 candidate dossiers — registration status, canon, open questions

**Date:** 2026-08-05 · **Track J2 of the "Last Call, Round Two" addendum.
Findings-only RESEARCH.** No game process was launched. No design content
appears in this document.

> **Iron rule, restated:** *dossiers contain zero design content. A dossier that
> proposes is a failed dossier.* This document names **no** candidate of its
> own. Where the repo registers a name, it is reported with a citation. Where
> the repo registers nothing, that silence is reported as the finding and **is
> not filled in.**

Companion document: `docs/zhongli-dossier-2026-08-05.md` (Track J1), which
covers slot 4. Cross-references to it are marked **[J1]**.

---

## 0. The headline finding: slot 5 is registered to no one

**This section corrects a premise in the task that commissioned this dossier.**
The brief described Columbina as "the registered north-star" for slot 5. The
repository supports neither half of that phrase.

### 0.1 There is no slot 5

A repo-wide search for `slot 5`, `slot-5`, `slot5`, `slot five`, `fifth
character`, `fifth slot`, `fifth playable` and `5th character` returns **zero
substantive hits.** The only `Slot5` matches in the tree are Godot node names
in the Furina salon stage scene
(`klee-mod/pck-src/furina/ui/salon_stage.tscn:68, 142-148, 517-529`) and a
related C# comment (`klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs:265`) — UI
geometry, unrelated to the roster.

The roster registry stops at three built characters:

- `tier0/roster.py:110` — `ROSTER: tuple[Character, ...]` contains exactly
  `klee` (`:111`), `furina` (`:118`), `kokomi` (`:125`). No fourth entry, no
  fifth.
- `tier0/roster.py:12-14` — *"**This registry is the pre-Zhongli gate.** Slot 4
  does not open until a character can be declared once and have every consumer
  either read it or fail loudly."*

**The highest slot the repo registers by ruling is 4 (Zhongli), and that ruling
is itself an unsigned DRAFT** (`tier0/DECISIONS.md:2913-2946`; see **[J1] §0**).
There is no mechanism in the repo that would register a slot 5 before slot 4
closes.

### 0.2 Columbina is registered — but not as slot 5, and not as a "north star"

Columbina **is** registered, substantially and in multiple places. What she is
registered *as* is a **design space**, not a roster index:

> *"v1.2: Added Appendix A (support-protagonist design space / Columbina). No
> changes to v1 systems; **Columbina explicitly targets the §4.4 High-appetite
> slot.**"*
> — `docs/teyvat-spire-design-principles.md:241`

That is the strongest slot-language about her anywhere in the repo, and **"the
§4.4 High-appetite slot" is a companion-appetite tier**
(`docs/teyvat-spire-design-principles.md:108-109`), not a roster position.

**"North star" is a review-governance phrase in this repo, and it has never
been applied to Columbina.** Its uses are:
`review/enemy-atlas/atlas.md:7` (*"Candidates only, never verdicts:
RESKIN/REDESIGN is [USER]'s call per north-star"*),
`docs/surplus-week-manifest-2026-08-05.md:39, 115`, and
`docs/animation-capability-memo.md:1` (a doc title, "north-star v0.2").
**Columbina is never called a north star.**

### 0.3 What she IS registered as — the complete list

She is registered by **design space** and by **forward inheritance**: parts of
the engine already carry her name so that she inherits them when she arrives.

| Registration | Text | Path |
|---|---|---|
| The design space | Appendix A, "The support-protagonist design space (the Columbina problem)" — six numbered template extensions | `docs/teyvat-spire-design-principles.md:227-237` |
| Amendment log | *"Columbina explicitly targets the §4.4 High-appetite slot"* | `:241` |
| Keyword-budget pressure | *"the amendment sanctions *one* extra, not open season; **Columbina will pressure even this budget**"* | `:210` |
| Furina's strategic purpose | *"she beta-tests Columbina's driver machinery one character early… **If it works for Furina, Columbina inherits proven parts**"* | `docs/furina-kickoff-v0.1.md:11-17` |
| Schema field | the `character:` field is *"not Furina-private — **Columbina inherits it**"* | `docs/furina-kickoff-v0.1.md:60` |
| Keyword budget, again | *"Columbina will pressure even the amended budget (she touches every Nod-Krai mechanic); her kickoff fights that fight"* | `docs/furina-kickoff-v0.1.md:161-163` |
| Replay grammar | Encore Performance is *"the archetype's kit-deepener and **Columbina's replay grammar on schedule**"* | `docs/furina-kickoff-v0.1.md:205-206`; card note `docs/furina-cards.yaml:672` |
| Small-bench inheritance | *"inherited by Columbina (Nod-Krai's bench is similarly small)"* | `docs/furina-kickoff-v0.1.md:248` |
| `register` column | *"`register` joins the SHARED card schema (state.py) — **Columbina and every future character inherit the column**"* | `tier0/DECISIONS.md:2730-2732`; also `docs/curtain-call-sprint-log-2026-07-27.md:213`, `tier0/engine/state.py:135`, `tools/lint_register_isolation.py:7` |
| Bricking mitigation | *"generation is Spotlight's bricking mitigation (the soft form of Appendix A.3; **Columbina gets the hard guarantee**)"* | `docs/fontaine-companions.yaml:184` |
| Draft-sim forward-compat | companion-slot modes exist *"so **Columbina's bricking-mitigation relic** and the v2 Wish banner test on this rig without rework"* | `docs/archive/tier05-draft-sim-spec.md:25` |
| Co-op engineering | Appendix A.4 cross-player engineering *"then arrives with **Columbina**, which is where the charter originally said it belonged"* (WAIVED on the record) | `docs/brief-coop-charter-items.md:172-176` |
| A measurement term | *"the Columbina shape"* = a null hypothesis about card-mediated boosting | `tier0/DECISIONS.md:344-347`; `docs/archive/furina-sheet-pass-1-report.md:109, 190`; `docs/archive/furina-sprint-1-redpen.md:87` |

**Reading of the above, offered as an observation about the record and not as a
proposal:** the repo has invested more forward machinery in Columbina than in
any unbuilt character — including Zhongli, who *has* a slot ruling — while
never giving her a slot number. Those two facts are both true and are recorded
here together because a future session will need to reconcile them.

### 0.4 Appendix A in full, since everything above depends on it

> **Appendix A — The support-protagonist design space (the Columbina problem)**
>
> Flagged for v0.2+ planning: characters whose Genshin identity is *support*
> (Columbina being the motivating case: Nod-Krai's universal support,
> functioning either as the super-buffer for any of the region's team
> archetypes or as a "driver" who steals the supports and triggers their kits
> herself — the best support or the worst carry, by choice). "5-star support as
> playable character" is a different design space from "5-star carry" and needs
> its own template extensions:
>
> 1. **The precedent already exists in StS2.** Necrobinder proves
>    driver+carried-unit works as a solo archetype (she pilots Osty). A
>    support-protagonist generalizes this: her "carry" is whatever she drafts.
> 2. **Solo mode = the Driver.** She is the sanctioned **High companion-appetite**
>    character (§4.4). Her personal pool is deliberately thin on damage; her
>    cards act ON companion cards… Companions are her chips; she is the mult.
> 3. **Bricking mitigation is mandatory.** … Her starting relic must guarantee
>    acquisition… zero-companion runs must remain *possible* — Pillar 4: "worst
>    carry" must still clear solo, worst ≠ nonviable. **Her floor is the
>    design's hardest tuning problem.**
> 4. **Co-op mode = the Buffer.** First character to need **ally-targeted cards**…
>    Every ally-target card needs a solo fallback line…
> 5. **Statline shape:** A1≈1, A5/A6 = 4–5, everything else borrowed…
> 6. **Region coupling:** she ships with the Nod-Krai companion pool by
>    necessity (a driver needs a garage). **Nod-Krai's lunar-reaction family is
>    deferred alongside Dendro — do not couple her release to a new reaction
>    subsystem; her v1 drives the base six elements.**
>
> — `docs/teyvat-spire-design-principles.md:227-237` (abridged only where
> marked; A.1–A.6 headings and the load-bearing clauses are verbatim)

---

## 1. Columbina — canon status

### 1.1 The task premise was stale, in two ways

The brief instructed that Columbina's "canon facts are sparse/speculative" and
asked for speculation to be marked as such. **That instruction is out of date,
and this is the most consequential finding in J2.**

**C-1 `[CONFIRMED]` — Columbina is playable.** Full name **Columbina
Hyposelenia**. Released in Version **Luna IV (6.3)**, *"A Traveler on a Winter's
Night"*, **14 January 2026** — roughly seven months before this dossier's date.
— `https://www.hoyoverse.com/en-us/news/162178` (official; only the article
title was extractable, and the title itself confirms the version/character
pairing); `https://esports.gg/news/genshin-impact/columbina-playable-luna-iv/`

**C-2 `[CONFIRMED]` — She is 5-star, Hydro, Catalyst**, affiliated with
**Nod-Krai**.
— `https://game8.co/games/Genshin-Impact/archives/382106`;
`https://genshin.gg/characters/columbina/`;
`https://www.icy-veins.com/genshin-impact/columbina-profile-talents-constellations`

**C-3 `[CONFIRMED]` — She is the THIRD Harbinger, not the First.** The official
ranking is 1 Il Capitano, 2 Il Dottore, **3 Columbina**, 4 Arlecchino,
5 Pulcinella, 6 Scaramouche, 7 Sandrone, 8 La Signora, 9 Pantalone, 10
unknown/vacant, 11 Tartaglia; Pierro sits above as Director. Codename
**"Damselette."**
— `https://game8.co/games/Genshin-Impact/archives/381760`

**C-4 `[CONFIRMED]` — She is currently mid-rerun.** Banner *"Somnias a Luna"*,
Luna VIII / 6.7 Phase 2, **21 Jul – 11 Aug 2026**.
— `https://game8.co/games/Genshin-Impact/archives/572610`

**C-5 `[CONFIRMED]` — She is the third Harbinger to become playable**, after
Wanderer/Scaramouche and Arlecchino.
— `https://esports.gg/news/genshin-impact/columbina-playable-luna-iv/`

**Version mapping, for a reader checking dates:** Luna I = 6.0 (30 Sep 2025) →
Luna IV = 6.3 (Jan 2026) → Luna VIII = 6.7 (current). One consulted source
(Icy Veins) states "Patch 6.6" for her release; **that is an error**,
contradicted by every other source and by the Luna numbering.
— `https://keqingmains.com/misc/nod-krai-guide/`

### 1.2 Her released kit

**Provenance caveat, and it is a real limitation.** Every line in this
subsection is **guide-site paraphrase, not verbatim game text**.
`genshin-impact.fandom.com` returned **HTTP 402 on every access route tried**,
including the MediaWiki API workaround that succeeded for Zhongli in **[J1]**
(`action=query&prop=revisions`, `prop=extracts`, `action=parse&prop=wikitext`,
`Special:Export`, and `?action=raw` all failed; the 402 is domain-wide through
this proxy, not path-specific). Only search-snippet extraction got through.
**If exact wording or numbers become load-bearing, they need a fresh pull.**

| Element | Name | Behavior as documented |
|---|---|---|
| **Normal Attack** | *Moondew Cascade* | Summons Moonlit Tides, up to 3 attacks dealing Hydro DMG. **With ≥1 Verdant Dew the Charged Attack is replaced by *Moondew Cleanse*** — no stamina cost, 3 instances of AoE Dendro DMG treated as **Lunar-Bloom DMG**. Plunge deals AoE Hydro |
| **Elemental Skill** | *Eternal Tides* | AoE Hydro DMG, summons **Gravity Ripple** — which **follows the active character** rather than being stationary — dealing continuous AoE Hydro DMG. When nearby party members trigger Lunar reactions, Columbina accrues **Gravity**; at cap it discharges as **Gravity Interference**, whose damage type is set by **whichever Lunar reaction contributed the most Gravity** |
| **Elemental Burst** | *Moonlit Melancholy* | Transforms surrounding terrain into a **Lunar Domain**, dealing AoE Hydro DMG. Inside it, **all party members' Lunar Reaction DMG Bonus is increased** |
| **A1** | *Lunacy's Lure* | Gravity Interference grants *Lunacy*: +5% CRIT Rate, 10s, up to 3 stacks (self) |
| **A4** | *Law of the New Moon* | Inside the Lunar Domain each Lunar reaction gains a rider: Lunar-Charged → extra lightning strikes; Lunar-Bloom → additional Verdant Dew; Lunar-Crystallize → extra damage instances |
| **Conversion passive** | *Moonsign Benediction* (name disputed — see §1.5) | Converts party-triggered **Electro-Charged → Lunar-Charged, Bloom → Lunar-Bloom, Hydro-Crystallize → Lunar-Crystallize**; party Lunar Reaction Base DMG +0.2% per 1,000 Max HP, **capped at 7%**; *"when Columbina is in the party, the party's Moonsign will increase by 1 level"* |
| **Utility passive** | *Lunar Vigil* | Revives an incapacitated party member **while in Nod-Krai**, once per 100s, healing scaled by friendship |

— `https://keqingmains.com/q/columbina-quickguide/`;
`https://www.icy-veins.com/genshin-impact/columbina-profile-talents-constellations`;
`https://genshin.gg/characters/columbina/`

**Constellations** (numbering disputed — see §1.5): C1 *Radiance Over Blossoms
and Peaks* (casting Eternal Tides immediately triggers a
Gravity-Interference-equivalent, once/15s, with Moonsign-specific riders:
energy / interruption resistance / shield); C2 *Not in Lone Splendor* (Gravity
accumulation +34%; Gravity Interference grants *Lunar Brilliance*, +40% Max HP,
8s); C3 Skill level +3; C4 *Cloudveiled Ridges in Floral Mists* (Gravity
Interference restores 4 Energy; adds Max-HP-scaled DMG per reaction type —
Lunar-Charged 12.5%, Lunar-Bloom 2.5%, Lunar-Crystallize 12.5% of Max HP);
C5 Burst level +3; C6 *Through Darkness Led by Moonlight* (after a Lunar
reaction in the Lunar Domain, +80% CRIT DMG to the corresponding elemental
damage, 8s).
— `https://www.icy-veins.com/genshin-impact/columbina-profile-talents-constellations`

### 1.3 Nod-Krai and the Lunar reaction family — released, not deferred

This is the second consequential finding, because **Appendix A.6 explicitly
assumes the opposite.**

**C-6 `[CONFIRMED]` — Nod-Krai is released**, Version **Luna I (6.0), 30
September 2025**; southern Snezhnaya; Archon Quest chapter *Song of the Welkin
Moon*. — `https://keqingmains.com/misc/nod-krai-guide/`

**C-7 `[CONFIRMED]` — Lunar Reactions are live.** They **can CRIT** and scale on
Elemental Mastery, and they only occur when a party member with the Moonsign
Benediction passive is present.
— `https://gamewith.net/genshin-impact/article/show/69296`

| Reaction | Pair | Added | Behavior | Enablers |
|---|---|---|---|---|
| **Lunar-Charged** | Electro + Hydro | Luna I (6.0) | Replaces Electro-Charged. **Snapshots the stats of every character who applied Electro/Hydro into a single instance** of reaction damage; produces a cloud dealing periodic damage; **can CRIT** | Ineffa, Flins, Columbina |
| **Lunar-Bloom** | Dendro + Hydro | Luna I (6.0) | Replaces Bloom. Grants the **team Verdant Dew** (one per 2.5s, max 3) rather than dealing damage itself; does not change Dendro Core / Hyperbloom / Burgeon | Lauma, Nefer, Columbina |
| **Lunar-Crystallize** | Geo + Hydro | **Luna IV (6.3)** — Columbina's own version | Replaces Hydro-Crystallize. Deals no damage on trigger; spawns **3 Moondrifts**, which **count as Geo constructs**. After three triggers the Moondrifts resonate (**Moondrift Harmony**), each firing a tracking projectile for Geo DMG that **can CRIT** | Columbina, Zibai, later Linnea |

— `https://keqingmains.com/misc/nod-krai-guide/`;
`https://gamewith.net/genshin-impact/article/show/69296`;
`https://gamewith.net/genshin-impact/article/show/72020`;
`https://game8.co/games/Genshin-Impact/archives/572603`

**C-8 `[CONFIRMED]` — Moonsign is a team-state system, not a stat buff.** Two
levels only: **Nascent Gleam** (1 Moonsign character) and **Ascendant Gleam**
(2+). **There is no third level.** It grants no flat numbers; it **changes the
behavior of Nod-Krai skills, talents, constellations, weapons and artifacts**,
and effects stack rather than overwrite. At Ascendant Gleam, non-Nod-Krai
teammates contribute team-wide Lunar Reaction DMG% on Skill/Burst cast, scaled
off their own stats. **Only 5-star Moonsign characters can *enable* Lunar
reactions**; 4-stars only raise the level.
— `https://keqingmains.com/misc/nod-krai-guide/`;
`https://game8.co/games/Genshin-Impact/archives/549654`

**C-9 `[CONFIRMED]` — The Nod-Krai / Moonsign roster is 10 characters:** Aino
(4★ Hydro Claymore, free via Archon Quest), Ineffa, Flins (5★ Electro
Polearm), Lauma (5★ Dendro Catalyst), Nefer, Jahoda, **Columbina**, Zibai,
Linnea, Illuga. — `https://game8.co/games/Genshin-Impact/archives/549654`

**C-10 — cross-reference to [J1].** The Moondrift clauses that **[J1]** found on
the Genshin wiki's *Geo Construct* and *Elemental Resonance* pages (**[J1]**
C19, C21) **trace to Lunar-Crystallize**: Moondrifts are Geo constructs produced
by a Columbina-enabled reaction, and they are explicitly **exempt from the
3-construct player cap** (**[J1]** C21).
— `https://gamewith.net/genshin-impact/article/show/72020`

### 1.4 Lore facts (independent of playable status)

**C-11 `[CONFIRMED]` — She is a Moon Goddess.** Known as the **Moon Goddess of
Nod-Krai**, called **Kuutar** by the **Frostmoon Scions**, and revealed to be
the **fourth Moon Goddess** across the *Song of the Welkin Moon* Archon Quest
(including Act VIII, "True Moon").
— `https://game8.co/games/Genshin-Impact/archives/381760`;
`https://genshin-impact.fandom.com/wiki/Song_of_the_Welkin_Moon` (search
extraction)

**C-12 `[CONFIRMED]` — She is now described as a *former* Harbinger.** Current
descriptions read *"formerly The Damselette, Third of the Fatui Harbingers."*
Backstory: she left the Frostmoon Scions after disillusionment and joined the
Fatui.
— `https://www.sportskeeda.com/esports/columbina-genshin-impact-everything-know-far`
(search extraction)

**C-13 `[CONFIRMED]` — Behavior: eyes closed, quietly singing or humming; calm,
soft-spoken, unsettlingly filterless.** Documented beats: teasing Dottore about
looking young; telling Sandrone to drink oil instead of coffee. At La Signora's
funeral the melody she sang is a rendition of *Chrysalis Suspirii* and
*Saltatio Favillae*, Signora's themes.
— `https://hero.fandom.com/wiki/Columbina_Hyposelenia` (search extraction)

**C-14 `[CONFIRMED, second-hand only]` — Power-level statements are other
characters' opinions.** Tartaglia and Scaramouche treat her as dangerous and
enigmatic; Arlecchino regards her as interesting and special. **There is no
numeric or explicit in-game power ranking.** — same source

**C-15 `[CONFIRMED]` — Moon cosmology.** Nod-Krai is tied to the **Three Moons**
(Eternal, Iridescent, Frost) and the prophecy of a **rising New Moon**; the
trinity of Moon Goddesses *"steered the primordial celestial sphere."*
Nod-Krai itself is described as the remnant of a **fourth moon that failed to
materialize.**
— `https://genshin-impact.fandom.com/wiki/Nod-Krai` (search extraction);
`https://www.sportskeeda.com/esports/genshin-impact-song-welkin-moon-archon-quest-interlude-recap`

**C-16 `[UNKNOWN]` — No confirmed Abyss / Celestia / Descender tie was found.**
Her confirmed cosmological attachment is the **moons and Nod-Krai**. Any
Abyss/Celestia/Descender claim should be treated as fan theory until a primary
quest transcript is produced.

**C-17 `[SPECULATIVE]` — the "sleeping / dreaming" motif.** The *closed eyes*
and the *singing* are confirmed (C-13). **An explicit "sleeping" or "dreaming"
designation in official text was not found.** Marked speculative.

### 1.5 Where the sources disagree, and what is genuinely unknown

| # | Gap | Status |
|---|---|---|
| a | **Verbatim talent text.** Everything in §1.2 is guide-site paraphrase; Fandom was 402 on every route | Needs a fresh pull if exact wording matters |
| b | **Passive name collision.** KQM / GameWith / Game8 call the conversion passive **"Moonsign Benediction"**; genshin.gg calls it **"Moonlight, Lent Unto You."** "Moonsign Benediction" may be the *generic category* shared by all Nod-Krai units rather than her personal talent name | Unresolved |
| c | **Constellation numbering.** Icy Veins puts the +34% Gravity / Lunar Brilliance effect at **C2** and Skill Lv+3 at **C3**; a search-extracted summary puts Skill Lv+3 at **C2**. One is wrong | Unresolved |
| d | **Moonsign arithmetic.** Her passive says "+1 Moonsign level", implying **solo Columbina reaches Ascendant Gleam**. Game8's Moonsign page explicitly denies this — but that page appears to predate her release | Contradiction unresolved; the passive text is the likelier truth |
| e | *Lunar Vigil* exact friendship-scaled healing values | Not captured |
| f | Whether she formally resigned the Harbinger post, and by what mechanism | Descriptions say "formerly"; primary quest text not retrieved |
| g | Post-Luna-IV kit changes (any 6.4–6.7 adjustments) | Not checked |

### 1.6 Auditing the repo's own description against released canon

Appendix A describes Columbina as *"Nod-Krai's universal support, functioning
either as the super-buffer for any of the region's team archetypes or as a
'driver' who steals the supports and triggers their kits herself"*
(`docs/teyvat-spire-design-principles.md:229`). That sentence was written before
her release. Checked against the shipped kit:

**A-1 `[CONFIRMED]` — "super-buffer for any of the region's team archetypes"
holds.** She is the **only** character who enables all three Lunar reactions:
the conversion passive covers Electro-Charged, Bloom **and** Hydro-Crystallize
simultaneously (§1.2); the Burst buffs party-wide Lunar Reaction DMG; A4 adds a
rider to all three; C6 covers all three. One source states outright that *"
Columbina's kit lets any character on her team activate any of the main Lunar
reactions."*
— `https://game8.co/games/Genshin-Impact/archives/572610`;
`https://gamewith.net/genshin-impact/article/show/69296`

**A-2 `[CONFIRMED]` — the "driver who steals the supports and triggers their
kits herself" reading has a real mechanical basis, in two distinct places.**
(a) **Gravity Interference** — teammates' Lunar reactions charge *her* meter,
and *she* discharges damage of whichever reaction type her teammates fed most:
she is literally paid in their reactions and outputs the effect herself.
(b) **Moondew Cleanse** — she consumes **Verdant Dew produced by Lauma's or
Nefer's Lunar-Bloom** to fire stamina-free attacks that count as **her**
Lunar-Bloom damage. KQM confirms she *"can become an on-field driver in
Lunar-Bloom teams through her special charged attacks."*
— `https://keqingmains.com/q/columbina-quickguide/`

**A-3 `[OVERSTATEMENT]` — "universal" is wrong if read literally.** KQM is
explicit that she is **not** universal: she is scoped to Lunar-reaction teams and
has *"severely limited functionality in cases where Lunar Reactions cannot be
reliably triggered."* She is universal *within Nod-Krai's lunar archetypes*, not
a general-purpose Hydro support.
— `https://keqingmains.com/q/columbina-quickguide/`

**A-4 — Appendix A.6's factual premise has expired.** It reads: *"Nod-Krai's
lunar-reaction family is deferred alongside Dendro — do not couple her release
to a new reaction subsystem; her v1 drives the base six elements"*
(`docs/teyvat-spire-design-principles.md:236`). Two canon facts now bear on it:
the lunar family **shipped** (C-7), and **Lunar-Bloom requires Dendro** — which
this repo defers to v2 (`docs/teyvat-spire-design-principles.md:34`). The
instruction itself may well still be correct as a *scoping decision*; what has
changed is that it can no longer be justified by "the subsystem doesn't exist
yet." **Recorded as a fact about the record. Not re-decided here.**

**A-5 — three further collisions between released canon and repo state, all
recorded without resolution.**
1. **Element.** Columbina is **Hydro** (C-2). The repo already carries two Hydro
   playables, and accepted that spread deliberately — *"Element spread accepted
   (second Hydro)"* (`docs/kokomi-kickoff-v1.md:26`). A third Hydro is a fact
   about the roster, noted only.
2. **Crystallize.** **Lunar-Crystallize is Columbina-enabled and produces Geo
   constructs** (C-7, C-10). The repo's Crystallize fence assigns that space to
   **slot 4**: *"CRYSTALLIZE, deliberately avoided (kickoff Track A note —
   Zhongli's slot-4 archetype owns that space)"*
   (`docs/fontaine-companions.yaml:94-96`). Canon now has the two characters
   sharing one mechanic. **The fence holds in this document; this is a fact, not
   a proposal.**
3. **Weapon.** She is a **Catalyst** user (C-2), and the repo's cadence dial
   makes Catalyst-grade mean *"every attack applies"*
   (`docs/teyvat-spire-design-principles.md:60`) — the Klee grade. Noted only.

---

## 2. The adjacency category: Fontaine Rares

**The category exists and is registered. It registers names, but no slots.**

### 2.1 What the mechanism actually is

Four Fontaine 5-star Rare companions each carry an explicit reservation of their
Genshin Burst name *"for a future playable kit-Burst"*. This is the repo's only
mechanism that records forward playable intent for a named character short of a
slot ruling. It follows from v1.9, under which Bursts are kit rather than loot
(`docs/teyvat-spire-design-principles.md:66`).

| Character | Reserved Burst name | Path |
|---|---|---|
| **Navia** | *"As the Sunlit Sky's Singing Salute"* | `docs/fontaine-companions.yaml:101` |
| **Clorinde** | *"Last Lightfall"* | `:126` |
| **Arlecchino** | *"Balemoon Rising"* | `:165` |
| **Neuvillette** | *"O Tides, I Have Returned"* — *"RESERVED for **his future playable kit-Burst**"* | `:201` |

**These are the only four.** No Mondstadt or Inazuma companion carries a
reservation (`grep "RESERVED for"` across all three companion sheets returns
exactly these four lines, all in `fontaine-companions.yaml`).

**What the reservation does and does not do.** It fences a *name*. It does not
allocate a slot, does not rank the four against each other, and does not commit
that any of them will ever be built. Neuvillette demonstrates the limit: his
Burst name is reserved and *"was NOT taken"* by his companion card
(`docs/fontaine-companions.yaml:143`), yet he simultaneously ships as a
shared-pool Rare **and** three Guest Star cards (`:128, 203, 206, 210`). His
sheet note says the card *"Seeds his future playable identity"* (`:180`).
Reservation and companion presence coexist.

### 2.2 The one name with an explicitly open playable disposition — and it is closed

**Raiden Shogun.** The Kokomi kickoff logged her as genuinely undecided:

> *"Open disposition ([USER]-gated): Raiden Shogun. Options: reserve (future
> playable / act antagonist), or admit as apex 5★ Rare. Lore cuts both ways
> (Shogunate vs resistance; post-canon allies). **No draft position taken.**"*
> — `docs/kokomi-kickoff-v1.md:202-204`

**Closed against playable by ratified R52:** *"Ask 9 Raiden: playable characters
MAY also exist as Rare companion cards, and may appear in Kokomi's conscript
pool — but only as a Rare payoff… (User notes the playable-as-companion ruling
may not have been formally ratified before; it is ratified here for this case.)"*
(`tier0/DECISIONS.md:1348-1351`). She shipped as an Inazuma Rare companion.

### 2.3 Itto — the name that lost a slot

Itto was a **slot-4 candidate** in roster amendment A1 (*"the Itto-vs-Zhongli
open item in A1"*, `docs/kokomi-kickoff-v1.md:18`), **lost**, and was released
to the companion pool by the reserved-character rule read in reverse
(`tier0/DECISIONS.md:2929-2936`; `docs/inazuma-companions.yaml:4, 76`). He is
now a companion only.

**Carry the [J1] caveat:** that reserved-character rule sits in **unsigned draft
R88** and is **in tension with ratified R52** (§2.2 above). See **[J1] §0**.

### 2.4 Names that are NOT playable-slot candidates

Recorded so a future reader does not mistake a companion sheet for a roster.
**All of the following are companion-pool only, with no playable registration of
any kind:**

- **Mondstadt** (`docs/mondstadt-companions.yaml`): Albedo, Barbara, Bennett,
  Dahlia, Diona, Durin, Fischl, Kaeya, Nicole, Prune, Sucrose.
- **Inazuma** (`docs/inazuma-companions.yaml`): Gorou, Itto, Kujou Sara, Raiden
  Shogun, Sayu, Shinobu, Thoma. Later companion scope (`:21`): Kazuha, Heizou,
  Ayaka, Ayato, Yoimiya, Yae Miko.
- **Fontaine** (`docs/fontaine-companions.yaml`): Arlecchino, Charlotte,
  Chevreuse, Clorinde, Freminet, Lynette, Navia, Neuvillette. Later scope
  (`:190`): Sigewinne, Lyney, Wriothesley.
- **Venti** is **not** a registration. He appears once, as an illustrative
  hypothetical for the appetite lever — *"a hypothetical Venti/swirl-themed
  character designed to fish the companion pool"*
  (`docs/teyvat-spire-design-principles.md:108`).
- **Nod-Krai has no companion sheet in the repo.** It is referenced only as
  Columbina's necessary future pool
  (`docs/teyvat-spire-design-principles.md:236`) and as a lore/enemy region.

### 2.5 The complete registration picture

| Name | Registered as | Slot | Status |
|---|---|---|---|
| Klee | Playable | 1 | Built (`tier0/roster.py:111`) |
| Furina | Playable | 2 | Built (`:118`) |
| Kokomi | Playable | 3 | Built (`:125`; `docs/kokomi-kickoff-v1.md:9`) |
| Zhongli | Playable | **4** | **Ruled but DRAFT/uncountersigned**; not built; gated (`tier0/DECISIONS.md:2925`; `tier0/roster.py:12`) |
| **Columbina** | **Design space only** (Appendix A / §4.4 High-appetite) | **none** | Extensive forward inheritance; **no slot number anywhere** |
| Navia, Clorinde, Arlecchino, Neuvillette | **Burst-name reservation** — "a future playable kit-Burst" | **none** | Soft, name-level, slotless |
| Raiden Shogun | Playable option offered | — | **Closed against playable** by ratified R52 |
| Itto | Was a slot-4 candidate | — | **Lost**; released to companion pool |
| ~30 others | Companion pools | — | No playable registration |

**Slot 5 appears in no row of this table, because it appears nowhere in the
repo.** This dossier adds no name to it.

---

## 3. Open questions

Same rules as **[J1] §3**: questions with facts attached, **none decided**.
Tags: `[BLOCKED]` `[FACTUAL]` `[RULING]` `[SCOPE]`.

**Q1 `[BLOCKED]` — Can any slot-5 conversation legitimately open before slot 4
closes?**
Facts: the registry gate is explicit — *"Slot 4 does not open until a character
can be declared once and have every consumer either read it or fail loudly"*
(`tier0/roster.py:12-14`) — and slot 4's own ruling is unsigned
(`tier0/DECISIONS.md:2913`). There is no precedent in the repo for registering a
slot ahead of its predecessor.

**Q2 `[RULING]` — Does Columbina's forward machinery amount to a registration,
and should it be recorded as one?**
Facts: eight separate systems already name her (§0.3), including a **live schema
column** (`tier0/engine/state.py:135`), a **lint** (`tools/lint_register_isolation.py:7`),
a **waived charter item deferred to her** (`docs/brief-coop-charter-items.md:172-176`),
and a **whole character built to beta-test her machinery**
(`docs/furina-kickoff-v0.1.md:11-17`). She still has no slot number. **Whether
that is an omission or a deliberate posture is not recorded anywhere**, and this
dossier does not decide it.

**Q3 `[FACTUAL]` — Does Appendix A need a canon refresh before it is used
again?**
Facts: it was written when she was unreleased. Since then: she shipped (C-1),
her rank was different from the common assumption (C-3), the lunar family
shipped (C-7), and A.6's "deferred alongside Dendro" premise expired as a
*justification* (A-4). Its **design content** — driver archetype, bricking
mitigation, ally-target requirement, statline corner — is untouched by any of
this and may be entirely sound. **What is stale is the factual preamble.**

**Q4 `[SCOPE]` — Does the Crystallize fence need re-stating now that canon has
Columbina enabling Lunar-Crystallize?**
Facts: the fence assigns Crystallize to slot 4
(`docs/fontaine-companions.yaml:94-96`;
`docs/fontaine-rares-banner-sprint-log.md:49-51`); canon has Columbina enabling
**Lunar-Crystallize**, which spawns **Moondrifts that count as Geo constructs**
and are **exempt from the player construct cap** (C-7, C-10, **[J1]** C21).
Two registered characters now touch one mechanic in canon. **The fence holds in
this document.**

**Q5 `[SCOPE]` — What does the keyword budget look like for a support-protagonist
who now has a *known* kit?**
Facts: Guardrail 5 allows a support-protagonist **one** extra keyword via logged
amendment with compensating cuts, and warns *"Columbina will pressure even this
budget"* (`docs/teyvat-spire-design-principles.md:210`); the furina kickoff
repeats it, *"she touches every Nod-Krai mechanic"*
(`docs/furina-kickoff-v0.1.md:161-163`). Her released kit contains at minimum:
a **Gravity meter**, **Gravity Interference** (a type-selecting discharge), a
**Lunar Domain**, **Verdant Dew** consumption, a **following summon** (Gravity
Ripple), and a **three-way reaction conversion**. **The arithmetic is the
question. This dossier does not do it.**

**Q6 `[FACTUAL]` — Is the Necrobinder precedent in Appendix A.1 still the right
one?**
Facts: A.1 grounds the whole design space in *"Necrobinder proves
driver+carried-unit works as a solo archetype (she pilots Osty)"*
(`docs/teyvat-spire-design-principles.md:231`). **[J1] §2.3–§2.5** confirms Osty
is the **only** summon verb in official StS2 and characterises it precisely
(HP-based, no timer, in the HP-loss pipeline), and **[J1] §2.4** adds a second
mod-side precedent (Downfall's Torchhead). Meanwhile canon Columbina's *Gravity
Ripple* **follows the active character** — a different relationship from a
carried unit. **Whether the precedent still matches the subject is open.**

**Q7 `[RULING]` — Does the four-name Burst reservation mean anything for slot
allocation, and does it expire?**
Facts: four Fontaine names are fenced *"for a future playable kit-Burst"*
(§2.1), all four are simultaneously **shipped companions**, and Neuvillette
demonstrates that the two states coexist. **No document says what a reservation
obliges, how it is discharged, or whether it lapses.**

**Q8 `[FACTUAL]` — Which reserved-character rule governs, and does it bear on
these four?**
Facts: R88 (DRAFT) says a character reserved for a playable slot may not appear
as a companion, naming Neuvillette as the forward instance
(`tier0/DECISIONS.md:2932-2936`); R52 (ratified) says the opposite
(`:1348-1351`); the shipped content follows R52. **Whichever way this lands, it
governs the status of all four Fontaine reservations.** Same item as **[J1] Q1**.

**Q9 `[SCOPE]` — Does a Nod-Krai companion sheet precede or follow a Columbina
kickoff?**
Facts: A.6 says *"she ships with the Nod-Krai companion pool by necessity (a
driver needs a garage)"* (`docs/teyvat-spire-design-principles.md:236`); **no
Nod-Krai companion sheet exists** in the repo; her bench is flagged as small
(`docs/furina-kickoff-v0.1.md:248`); and canon now gives Nod-Krai a **10-character
roster** (C-9). **Ordering undecided.**

**Q10 `[FACTUAL]` — Does the co-op waiver still point where it did?**
Facts: Appendix A.4's cross-player engineering was **waived on the record** and
*"then arrives with Columbina"* (`docs/brief-coop-charter-items.md:172-176`).
**[J1] §2.4** finds that Downfall puts **pets and co-op allies in one `Allies`
list**, and that official StS2 ships genuinely multiplayer-only cards — i.e. the
ally-targeting surface has more precedent than the waiver assumed. Note also
there is **no sim backstop for co-op**: tier 0.5 models one seat.

**Q11 `[FACTUAL]` — Do the canon gaps in §1.5 need closing before anything
opens?**
Facts: seven open items (a–g), of which two are direct contradictions between
sources (passive name, constellation numbering) and one is a rules contradiction
(Moonsign arithmetic). All are resolvable by a single successful Fandom pull —
**which failed on every route this session** (§1.2).

**Open questions catalogued: 11 (Q1–Q11). Decided: 0. Names proposed: 0.**

---

## 4. What this dossier deliberately does not contain

- **No candidate names of my own.** The registered set is Columbina (design
  space) plus the four Fontaine Burst reservations. Nothing was added, and the
  empty slot-5 row was left empty.
- **No design content**: no cards, keywords, numbers, archetypes, statlines, or
  appetite declarations.
- **No ranking** of the four Fontaine names, and no ranking of Columbina against
  them.
- **No re-decision of Appendix A.** §1.6 audits its *factual preamble* against
  released canon and flags what expired; its design content is untouched.
- **No Crystallize scaling**, and no relaxation of the slot-4 fence — see Q4.
- **No position on R88**, which governs Q8 and is [J1]'s Q1.

---

## 5. External sources consulted

**Fetched successfully:** `https://keqingmains.com/misc/nod-krai-guide/` ·
`https://keqingmains.com/q/columbina-quickguide/` ·
`https://game8.co/games/Genshin-Impact/archives/382106` ·
`https://game8.co/games/Genshin-Impact/archives/381760` ·
`https://game8.co/games/Genshin-Impact/archives/572610` ·
`https://game8.co/games/Genshin-Impact/archives/549654` ·
`https://gamewith.net/genshin-impact/article/show/69296` ·
`https://gamewith.net/genshin-impact/article/show/72020` ·
`https://www.icy-veins.com/genshin-impact/columbina-profile-talents-constellations` ·
`https://genshin.gg/characters/columbina/`

**Referenced via search-snippet extraction only (page itself blocked):**
`https://genshin-impact.fandom.com/wiki/Columbina` · `.../Columbina/Storyline` ·
`.../Nod-Krai` · `.../Song_of_the_Welkin_Moon` · `.../Lunar_Reaction` ·
`.../Lunar-Crystallize` · `https://hero.fandom.com/wiki/Columbina_Hyposelenia` ·
`https://www.sportskeeda.com/esports/columbina-genshin-impact-everything-know-far` ·
`https://www.sportskeeda.com/esports/genshin-impact-song-welkin-moon-archon-quest-interlude-recap` ·
`https://game8.co/games/Genshin-Impact/archives/572603` ·
`https://esports.gg/news/genshin-impact/columbina-playable-luna-iv/`

**Blocked, and how** (recorded so a re-verification pass does not repeat the
attempt): `genshin-impact.fandom.com/api.php` — **HTTP 402 on all five routes
tried** (`action=query&prop=revisions`, `prop=extracts`, `action=parse&prop=wikitext`,
`Special:Export`, `?action=raw`); the 402 is **domain-wide through this proxy,
not path-specific**, and the MediaWiki-API workaround that succeeded for
Zhongli in **[J1]** did **not** work here. ·
`https://tvtropes.org/pmwiki/pmwiki.php/Characters/GenshinImpactColumbina` (403) ·
`https://esports.gg/...` (403 on direct fetch; title/snippet used) ·
`https://www.sportskeeda.com/...` (405 on direct fetch; snippets used) ·
`https://www.hoyoverse.com/en-us/news/162178` (fetched but returned an empty
JS-rendered shell; **only the article title was usable** — it does confirm the
Luna IV / Columbina pairing).
