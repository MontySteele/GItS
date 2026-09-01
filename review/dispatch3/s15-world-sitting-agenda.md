# World-track sitting agenda — compiled 2026-08-26 (dispatch 3, S15)

> ## This document decides nothing.
>
> It is a **walking order**, not a register. `docs/current/QUEUE.md` stays the
> single source of truth for open [USER] decisions, and nothing below changes,
> supersedes, or adds to it. No item here carries a recommendation, a default,
> or a proposed answer. No identifier (`M-`, `EB-`, `R-`) is minted anywhere in
> this file. Where a gallery already orders its own candidates, that order is
> reproduced **unchanged** and is the drafting pass's ordering, not an
> endorsement from this agenda.
>
> Every item gives you one sentence of context, the exact file and line to
> read, and the **shape** of the answer it wants (pick-one / yes-no / open).
> Nothing more.

---

## How to read this

The sitting is in three passes, easiest first.

- **§A — one-word calls (items 1–12).** Each one is a yes/no or a choice
  between two named options. You should be able to answer from the context
  sentence plus a glance at the cited line.
- **§B — short calls (items 13–47).** Each one is a pick from a list the
  gallery already wrote down. Reading is one entry or one paragraph.
- **§C — discussions (items 48–58).** Structural questions with no crisp pick.
  Several of them gate items in §A and §B, and each says which.
- **§D — the gap appendix.** Which items above have a QUEUE row waiting for
  them (almost none do), plus citation problems found while compiling.

**Terms.** *Gallery* = one of the five finished conversion documents named in
the dedupe log. *Variant* = one drafted Genshin identity offered for one base
body. *Register* = a per-faction voice rule ("Melusines always keep a written
record"). *Base body / base mechanics* = the shipped Slay the Spire 2 entity
and its numbers, which every gallery treats as **frozen** — no item below
proposes changing a number, a hook, or a stat block.

---

## §0. Dedupe log — done first, before anything was written

The charter's first instruction was to check this agenda against four things
so that nothing already ruled or already agendized is re-listed. Result:

| Checked against | Result |
|---|---|
| `docs/current/QUEUE.md` (all 5 sections, 14 open rows) | **One overlap only** — the row `S8 + S10 galleries` in §3. Nothing else in QUEUE touches the enemy, boss, Ancient, or event galleries. That row is **linked below, not re-listed**. |
| The 2026-08-08 sitting agenda | **Present in HEAD** at `review/ruled/sitting-agenda-2026-08-08.md`; it carries a `2026-08-10 — HISTORICAL` banner at line 3. Its item 19 walked S8 + S10 (`:470-476`) and its item 26 walked `M7` / the Enchant op (`:570-579`). Both are covered by the link block below. |
| `review/records/sitting-reads-2026-08-26-c20-d18-p11.md` (the current sitting reads) | **No overlap.** That packet is a twelve-arm measurement re-baseline at `RT12/D18/P11/C20` — its sections are the caveat check, the cell, the three number tables, and the blast-radius discussion. It contains no world-track, lore, enemy, boss, or conversion item. |
| `M46` | **ABSENT in this checkout.** `grep -rn "M46" docs/ review/` returns nothing; the highest live id in `QUEUE.md` is `M45` (§5, "ratify the pass's seven open calls as ONE slate"). Recorded here as the charter's §0.4 asks, and treated as non-existent for dedupe purposes. |

### Already ruled or already agendized — LINKED, not re-listed

Read these from their existing homes. Nothing below re-opens them.

| Subject | Where it already lives | Status |
|---|---|---|
| The eight flagged potions/relics (**S8**) and the reskin-vs-redesign call (**S10**) | `docs/current/QUEUE.md` §3, row `S8 + S10 galleries` | **OPEN** in QUEUE; walked once already as item 19 of the 2026-08-08 agenda. Navigation pointers only in §B below. |
| The Orobas starter-relic **boon-family naming convention** (`R-Q1.5`) | This is the eighth S8 flag — `dossiers/content/potion-relic-conversion-gallery.md:1031`, item `touch_of_orobas_klee` | Inside the linked QUEUE row above. The Ancients gallery raises the *identical* question independently at `dossiers/content/ancients-gallery.md:243`; both point at one call. |
| **Wood Carvings** (the last unconverted event) | `RULINGS.md` R184 (2026-08-12, "M23 ruled RESKIN"); engineering in `BACKLOG.md` `EB-83`; the eye-read on *Tengu Flurry* / *Chinowa Ward* is QUEUE `S4-G11` | **SETTLED as a design call.** The gallery's own entry at `event-conversion-gallery.md:1485` records it. Two engineering gaps remain open there (`transform_starter_into`, the `slither` row) — engineering, not a sitting call. |
| **Stone of All Time** and the Enchant op | `RULINGS.md` R159 (2026-08-10, "M7. R82's closed scope reopened"); the event's own entry is ticked `[x]` at `event-conversion-gallery.md:897-899`; live-smoke follow-through is `BACKLOG.md` `EB-84` | **SETTLED.** The FLAG that the 2026-08-08 agenda item 26 pointed at is gone from the gallery. |
| The **dormant / no-spend** class, `SKIP-10.9` included | `RULINGS.md` R183 (2026-08-12); rows marked `DORMANT / NO-SPEND` in `BACKLOG.md` | Blessed and off-limits. No item below targets one. |
| **Ancient-rarity cards** (`JumpyDumptyMkOmega`, `AllTheWorldsAStage`, `PrincessOfWatatsumi`) | LAW's Ancient carve-out (R127); `klee-mod/KleeCode/RosterAncientCards.cs` | A **different object** from the eight Ancient *beings* below — the Ancients gallery says so explicitly at `ancients-gallery.md:920-924` and did not re-draft them. Not on this agenda. |
| **Childe / Tartaglia** as a boss body | `dossiers/bosses/candidates.md:77-84` and §Assembly notes 6 (`:803`) | Recorded as a **fixed point** per north-star v0.2, deliberately not re-drafted. Not a question. |

### The five source galleries, and what each is

All five are in HEAD in the primary checkout, all `git ls-files`-tracked.

| Gallery | Path | Size | What it holds |
|---|---|---|---|
| **Q1 — Ancients** | `docs/current/dossiers/content/ancients-gallery.md` | 924 lines | 8 Ancient beings × 2–3 canon-sourced Genshin identities each, curated 2026-08-05 |
| **Q2 — Act bosses** | `docs/current/dossiers/bosses/candidates.md` | 831 lines | 6 base boss bodies × 3–4 Genshin weekly-boss identities (19 variants), curated 2026-08-05 |
| **S2 — Events** | `docs/current/dossiers/content/event-conversion-gallery.md` | 1,760 lines | 47 events, 130 kept variants, per-faction register rules, 14 FLAG blocks |
| **S8 — Potions + relics** | `docs/current/dossiers/content/potion-relic-conversion-gallery.md` | 1,313 lines | 51 items (9 potions + 42 relics), 79 kept mappings, 8 flags |
| **S10 — Enemy reskins** | `docs/current/dossiers/remap/reskin-gallery.md` | 164 lines | the curated cross-family pairing table; the reference volume behind it is `dossiers/remap/atlas.md` (721 KB) |

Supporting reference, **not** a source of agenda items: the eleven weekly-boss
dossiers (`dossiers/bosses/dossiers.md`), the cross-boss pattern memo
(`dossiers/bosses/pattern-memo.md`), the 111 per-enemy behaviour dossiers
(`dossiers/enemies/`), and `docs/current/research/` — all three research files
carry a `Lifecycle: REFERENCE — frozen record` banner and none of them raised a
live [USER] question that is not already covered above or in §D.

---

# §A — One-word calls (items 1–12)

Twelve questions that resolve to a yes, a no, or one of two named words. Seven
are Ancients-side, three are boss-side, two are enemy-atlas-side.

### 1. Apep's pronoun, gallery-wide — *she* or *it*
**Context.** Apep appears in two galleries at once (as an Ancient candidate for
Pael, and as the top boss candidate for Test Subject) and the canon sources are
genuinely split — the Chinese baike uses "it", the English search summaries use
"her" — so every draft that mentions her is currently inconsistent with some
other draft.
**Read.** `ancients-gallery.md:837` (also `:292`, `:324`).
**Shape.** pick-one of two.

### 2. Does `type = Upcoming` disqualify an Ancient candidate?
**Context.** Dainsleif was the Darv drafter's strongest thematic match and was
dropped only because his wiki infobox reads `Upcoming` and the article calls him
an upcoming playable character; the existing rule bans `type = Playable` and
says nothing about announced-but-unreleased.
**Read.** `ancients-gallery.md:709` (rule `RQ1-A2`), rejection recorded at
`:454`.
**Shape.** yes-no.

### 3. Does being a playable character's combat companion disqualify an Ancient?
**Context.** Marchosius / Guoba is `type = Quest and Event NPC` and so passes the
playable-character ban on its face, but he is also Xiangling's Elemental Skill
summon — and he is the top-ordered variant for Tezcatara and the third for
Nonupeipe, so the answer moves two entries.
**Read.** `ancients-gallery.md:713` (rule `RQ1-A3`), the test case at `:520`,
the open note at `:533`.
**Shape.** yes-no.

### 4. May a remnant appear wearing a living faction's shape?
**Context.** The Neow variant that uses Elynas has him appear in a Melusine
shape; the drafters propose that the borrowed faction's register then applies on
top of the remnant's own, and if shape-borrowing is ruled out that whole variant
goes with it.
**Read.** `ancients-gallery.md:834` (also `:130`, `:180`).
**Shape.** yes-no.

### 5. Open a Natlan register block?
**Context.** The event gallery's per-faction register covers ten factions and
Natlan appears in none of them; the Tezcatara Chanca variant is the first
Natlan-sited draft in the project, and the fragment proposes the block's content
if one is opened.
**Read.** `ancients-gallery.md:820` (also `:393-395`); the existing ten blocks
are `event-conversion-gallery.md:28-77`.
**Shape.** yes-no.

### 6. Does Darv's second meeting acknowledge the first, in text?
**Context.** Darv is the only Ancient present in **both** act pools, so a player
meets him twice in one run in two different zones; the drafters ruled his name
and voice must stay identical across both, and left the "does he remember you"
half explicitly to you.
**Read.** `ancients-gallery.md:813` (rule `RQ1-D5`), also `:405` and `:467`.
**Shape.** yes-no.

### 7. May a canonically mute body be personified as an Ancient?
**Context.** The Neow fragment logs the Statue of the Seven as mechanically the
most literal Ancient in Teyvat — it heals, revives and dispenses — but it does
not speak, so giving it a voice would be invented content and the drafters
deliberately did not draft it.
**Read.** `ancients-gallery.md:166-170`, and §Assembly notes 5 at `:911`.
**Shape.** yes-no.

### 8. The boss-pool nation predicate — does "nation" read **faction** or **staging**?
**Context.** The proposed rule says an act's boss pool never draws every entry
from one nation, but La Signora and Magatsu Mitake Narukami are Snezhnayan and
Inazuman *by faction* while both fights are *staged* in Inazuma — so a
staging-based predicate fails a pair that a faction-based predicate passes.
**Read.** `candidates.md:694` (inside rule `RQ2-C1` at `:685`).
**Shape.** pick-one of two. *Gates item 54.*

### 9. Fatui bosses — does the boss register override the faction register, or are Harbinger bodies excluded from the Fatui block?
**Context.** The gallery's Fatui register is "silky contractual menace, threat
never overt", and a Harbinger fought as an act boss is overt by construction, so
the two rules cannot both hold for the same body.
**Read.** `candidates.md:731` (rule `RQ2-D5`); the Fatui register itself is
`event-conversion-gallery.md:74-77`.
**Shape.** pick-one of two.

### 10. Double-booked Genshin bodies — one home per body per act, or repeats across acts accepted?
**Context.** Nine Genshin bodies are claimed by three or more base rows in the
enemy atlas (Large Dendro Slime ×5, Whopperflower bodies ×6+, Kairagi ×4, and
six more), and the gallery states this as a call you make once rather than a
per-row question.
**Read.** `reskin-gallery.md:126-128` (§5).
**Shape.** pick-one of two.

### 11. Does the tier0 calibration battery stay unthemed?
**Context.** Nine enemy families proposed Genshin skins for the frozen
measurement fixtures (`swarmling`, `grinder`, `sleeper`, `tank_boss`,
`punisher`); every proposing agent also flagged the file's own
`*** FROZEN — do not retune ***` header, and the curation pass cut all of them
on the ground that reskinning a measuring instrument makes diagnostic fixtures
look like content.
**Read.** `reskin-gallery.md:130-134` (§6) and the cut record at `:138-148`.
**Shape.** yes-no.

### 12. May one Genshin body be claimed by **both** the boss gallery and the enemy atlas, or does one stream yield?
**Context.** Azhdaha is listed as a candidate for Act 3's Test Subject in both
documents independently, which the boss gallery calls agreement rather than
collision — but it still needs a rule before either list can be spent.
**Read.** `candidates.md:486`; the atlas row is `reskin-gallery.md:72`.
**Shape.** pick-one of two. *Related to, but narrower than, item 48.*

---

# §B — Short calls (items 13–47)

Each item is a pick from a list the gallery already wrote. Variants are listed
in the gallery's own curated order, unchanged.

## B1 — the eight Ancients (items 13–20)

Each is one checkbox: tick a variant, or none. The gallery's own instruction is
at `ancients-gallery.md:72-76`.

| # | Ancient | Variants, in the gallery's order | Read | Shape |
|---|---|---|---|---|
| 13 | **Neow** (Act 1, always) | Orobashi · Egeria · Elynas | `ancients-gallery.md:97-185` | pick-one-or-none. *Elynas is gated on item 4.* |
| 14 | **Orobas** (Act 2) | Azhdaha · King Deshret · Rhinedottir | `:186-248` | pick-one-or-none |
| 15 | **Pael** (Act 2) | Durin · Apep · Azhdaha (marked CUT) | `:249-331` | pick-one-or-none |
| 16 | **Tezcatara** (Act 2) | Marchosius/Guoba · Madame Ping · Chanca | `:332-401` | pick-one-or-none. *Gated on items 3 and 5.* |
| 17 | **Darv** (both pools) | Katayoun · Hirayama · Langqing | `:402-471` | pick-one-or-none. *Gated on item 6.* |
| 18 | **Nonupeipe** (Act 3) | Remus · Rukkhadevata · Marchosius (CUT) | `:472-537` | pick-one-or-none |
| 19 | **Tanx** (Act 3) | Lawachurl · Azhdaha (CUT) · Andrius (CUT) | `:538-603` | pick-one-or-none. *The curation pass records at `:58-60` that no strong variant survives; gated on item 21.* |
| 20 | **Vakuu** (Act 3) | Liloupar · Osial · Nibelung | `:604-688` | pick-one-or-none |

### 21. The hilichurl *lawa* carve-out
**Context.** The event gallery's register binds **all** hilichurl speakers to
untranslated hilichurlian, which forbids a faithful Tanx — canon Tanx shouts in
translated all-caps — so the drafted Tanx variant obeyed the rule and came out
permanently muted.
**Read.** `ancients-gallery.md:827-833`; the binding rule is
`event-conversion-gallery.md:56-57`; the variant-level flags are at `:573` and
`:598`.
**Shape.** pick-one of three, as the gallery states them: grant a *lawa*
carve-out · accept a permanently muted Tanx · send the entity back for a redraft
round.

### 22. The cross-gallery single-spend allocation
**Context.** Four Genshin bodies are claimed by both galleries and can only be
spent once; the curation pass spent them (Azhdaha → Orobas, Apep → the boss
gallery's Test Subject, Andrius → the boss gallery's Vantom, Marchosius →
Tezcatara) and recorded the alternative for each.
**Read.** `ancients-gallery.md:25-31` and the contention map at §Assembly notes 2
(`:852-861`); the boss-side mirror is `candidates.md:34-52` and §Assembly notes 2
(`:746-766`).
**Shape.** pick-one per body (accept the curated spend, or name the other home),
or open.

### 23. How wide is the "no mercantile voice" rule for Liyue Ancients?
**Context.** The Ancients' core rule ("an offer is always an unpriced gift,
never a priced transaction") is the exact inverse of the Liyue mercantile
register ("everything is always a contract"), and the drafters split: four wrote
the wide reading (no Liyue Ancient outside the god/adeptus register) and one
filed a dissent for the narrow one (never voice an Ancient in the *mercantile
register*; the nation is not itself disqualifying).
**Read.** `ancients-gallery.md:745-755` (wide) and `:756-763` (the dissent); the
mercantile register is `event-conversion-gallery.md:70-73`.
**Shape.** pick-one of two.

### 24. Adopt the Ancients register set as written?
**Context.** The Ancients gallery proposes a lint-able rule set — eligibility
(`RQ1-A1`–`A5`), voice (`RQ1-B1`–`B3`), and family naming (`RQ1-D1`–`D5`) —
and states in its own words that these are proposed, not ratified, and that only
you can amend an existing block.
**Read.** `ancients-gallery.md:689-817`.
**Shape.** open (the gallery's own framing is adopt / amend / decline, per rule).

### 25. Open the three new faction blocks the Ancients gallery proposes?
**Context.** Three drafters proposed genuinely new register blocks that nothing
in the event gallery currently covers — **Dead gods & divine remnants**,
**Ancient dragons & Sovereigns**, and **Archives & Keepers of Record** — each
with its headline predicate written out.
**Read.** `ancients-gallery.md:768-793`.
**Shape.** yes-no per block (three sub-answers).

## B2 — the six act-boss slots (items 26–31)

One checkbox per base boss: tick a variant, or none. Instruction at
`candidates.md:85-88`.

| # | Base boss (slot) | Variants, in the gallery's order | Read | Shape |
|---|---|---|---|---|
| 26 | **Vantom** (Act 1, A) | Andrius · La Signora · The Knave | `candidates.md:109-170` | pick-one-or-none |
| 27 | **Lagavulin Matriarch** (Act 1, B) | Magatsu Narukami · Azhdaha · All-Devouring Narwhal · Stormterror Dvalin | `:171-274` | pick-one-or-none. *Gated on items 50 and 51.* |
| 28 | **Knowledge Demon** (Act 2, A) | Shouki no Kami · Guardian of Apep's Oasis · Azhdaha | `:283-348` | pick-one-or-none. *Gated on item 32.* |
| 29 | **Kaiser Crab** (Act 2, B) | Apep-as-two-Wardens · La Signora · Magatsu Narukami | `:349-438` | pick-one-or-none. *Gated on items 48 and 52.* |
| 30 | **Test Subject** (Act 3, A) | Guardian of Apep's Oasis · Azhdaha · La Signora | `:447-510` | pick-one-or-none. *Gated on items 48 and 53.* |
| 31 | **Aeonglass** (Act 3, B) | Shouki no Kami · Lord of Eroded Primal Fire · Stormterror Dvalin | `:511-597` | pick-one-or-none. *Gated on items 48 and 51.* |

### 32. May a playable character's body be used as a boss body at all?
**Context.** Two of the six slots' top-ordered variants are playable characters
in Genshin — Shouki no Kami is Scaramouche / the Wanderer, and Magatsu Mitake
Narukami is the Raiden Shogun — which the Ancients gallery bans outright on its
side (`RQ1-A1`) but which the boss gallery has no rule for; the drafters flagged
it three separate times and made no call.
**Read.** `candidates.md:306`, `:414`, `:531`; the Ancients-side ban is
`ancients-gallery.md:703-708`.
**Shape.** yes-no. *Gates items 28 and 31, and half of 27 and 29.*

### 33. Adopt the boss register set as written?
**Context.** The boss gallery proposes its own lint-able rules — naming
(`RQ2-A1`–`A6`), the memory-framing rule for canonically dead bodies (`RQ2-B1`),
pool composition (`RQ2-C1`–`C4`), and honesty (`RQ2-D1`–`D5`) — stated as
proposed, not ratified.
**Read.** `candidates.md:612-737`.
**Shape.** open (adopt / amend / decline, per rule).

## B3 — the live event FLAGs (items 34–46)

The event gallery carries fourteen FLAG blocks. One is settled (Wood Carvings,
linked in §0). The remaining thirteen are below. Each FLAG's own wording is at
the cited line; the context sentence here does not restate the full flag.

| # | Event | What resists | Read | Shape |
|---|---|---|---|---|
| 34 | **Byrdonis Nest** | The Take-the-Egg branch needs an unplayable quest-card type the sim does not have, so the event currently ships with a one-option floor | `event-conversion-gallery.md:238` | pick-one of two: wait for the quest-card hook · ship Eat-only |
| 35 | **Room Full of Cheese** | The sim substitutes a plain random relic for The Chosen Cheese, so every variant's end-of-combat +1 Max HP promise overstates what ships | `:749` | pick-one of two: a `post_fight max_hp` op · ship with the substitution note attached |
| 36 | **Tablet of Truth** | Stage 5's "lose all but 1 Max HP" both defies in-scene voicing and is deliberately omitted from the sim today | `:962` | pick-one of three: verbatim · a capped floor · continued omission |
| 37 | **Reflections snoitcelfeR** | Whole-deck duplication has no plausible Teyvat agent, and the mirrored-title gimmick is an English-text joke | `:693` | yes-no: do the reversed titles ship as transliterations |
| 38 | **Welcome to Wongo's** | Wongo Points are profile-level, cross-run meta-currency with a cosmetic badge; no in-world ledger can honestly track them | `:1390` | pick-one of two: the "filed under your name" conceit suffices · the event waits |
| 39 | **Crystal Sphere** | The event wraps an 11×11 spatial uncover minigame whose reward geometry lives in art and grid maths, not text | `:340` | pick-one of two: the sim grows a grid UI · the event waits |
| 40 | **Doll Room** | The Doll Relic family is a Slay the Spire 2-specific relic subpool with no Teyvat naming hook | `:409` | pick-one of two: rename the family's members (a pool-level call) · the event text gestures generically |
| 41 | **War Historian, Repy** | Hard-gated on the Lantern Key quest card from a second unshipped event, so the two must ship as a pair | `:1361` | open |
| 42 | **Brain Leech** | The mod deleted the base colorless pool, and the harvested "Colorless 2 card reward" line is template-lossy — all three drafts read it as *two* cards | `:184` | open (pick a companion-reward channel) **plus** yes-no (confirm the two-card reading against the wiki) |
| 43 | **Colorful Philosophers** | The payload is five other Slay the Spire 2 characters' card pools, which have no Teyvat referent and do not exist in this mod | `:266` | open |
| 44 | **Ranwid the Elder** | The third base option `[Give ]` lost its offered item to template-stripping | `:662` | open — blocked on a targeted wiki re-harvest before any answer is possible |
| 45 | **Relic Trader** | Template-stripping ate the traded relic names on all three base options (`Trade for .`) | `:718` | open — blocked on a targeted wiki re-harvest |
| 46 | **The Merchant___** | The harvest has no options section at all (`<<NO OPTIONS SECTION ON PAGE>>`) | `:1177` | open — blocked on a namespace-prefixed re-harvest |

Items 42 and 43 both turn on the same shipped fact — design principles §4.7
deleted the base colorless pool. The one prior ruling in that class is R184
(Wood Carvings, ruled RESKIN with §4.7 held unamended), linked in §0; whether
it reaches these two is part of what each item asks.

### 47. The per-event variant tick — 41 open checkboxes
**Context.** The event gallery is a checkbox document: 47 events, one box each,
tick a variant or none. Six are already ticked `[x]` — Field of Man-Sized Holes,
Grave of the Forgotten, Sapphire Seed, Self-Help Book, Stone of All Time,
Symbiote — leaving 41 open.
**Read.** `event-conversion-gallery.md:80-1560`; every event heading is a
`## - [ ]` line, so `grep -n "^## - \[" ` gives the walking list with line
numbers. The register rules that govern all of them are at `:24-77`.
**Shape.** pick-one-or-none, ×41.

**Also in that file, not an item:** Appendix A (`:1562-1710`) collects every
drafter's NOT-APPLIED redesign temptation, and states in its own words that it
is inventory, not endorsement. Appendix B (`:1712-1760`) is the raw
mapping-resistance notes. Both are reading material for the sitting; neither
carries a question.

## B4 — linked, not re-listed

### S8 (eight flagged potions/relics) and S10 (reskin vs redesign)
**The ask is the QUEUE row** `S8 + S10 galleries` in `docs/current/QUEUE.md` §3.
It is not restated here. Navigation only:

- The eight S8 flags, in checklist order, with the line each flag sits on:
  `fire_potion` `:125` · `strength_potion` `:172` · `swift_potion` `:191` ·
  `weak_potion` `:218` · `fear_potion` `:250` · `energy_potion` `:280` ·
  `strike_dummy` `:626` · `touch_of_orobas_klee` `:1031` — all in
  `dossiers/content/potion-relic-conversion-gallery.md`. The 51-item checklist
  with the ⚑ marks is at `:22-74`; the nine lint-able naming rules are at
  `:78-88`.
- The S10 material: the candidate pairing table
  `dossiers/remap/reskin-gallery.md:13-86`, the redesign-pressure list `:90-100`,
  the resolved verification flags `:107-120`, and the Globe Head silhouette —
  still unresolved, `:120`.

**One fact worth knowing before you walk that row, recorded and not resolved:**
the QUEUE row's pick list reads "per flagged body: (1) RESKIN … (2) REDESIGN",
which is S10-shaped. Each of the eight S8 flags asks a *different* question
(accept a category-mismatched mapping, accept a frame inversion, re-candidate,
pick a naming convention), so the row's stated pick list does not fit them
one-for-one. Whether the S10 §1 redesign-pressure list also sits inside that row
is likewise unclear from the row's wording — it says "five of six", which
matches the §3 verification flags, not the §1 list. Stated as an observation
about the register; not settled here.

---

# §C — Discussions (items 48–58)

No crisp pick. Several gate items above and say so.

### 48. THE FORK — do the act-boss slots take weekly-boss bodies at all?
**Context.** The enemy atlas already carries curated top picks for the same six
base boss bodies from the *normal-enemy* families, three of them rated **S** and
argued to beat every weekly-boss draft on the merits — Coral Defenders for
Kaiser Crab (natively a two-body boss, which no weekly boss is), Iniquitous
Baptist for Test Subject, Abyss Lector: Fathomless Flames for Aeonglass — so the
two galleries compete for the same slots rather than extending each other.
**Read.** `candidates.md:27-31` (the fork stated), `:271` (the same collision on
both Act 1 slots), `:602`, and §Assembly notes 4 at `:777-794`; the atlas rows
are `reskin-gallery.md:29-30`, `:54`, `:72`, `:73`.
**Shape.** open, or pick-one per slot. **This is the item that outranks the
rest of §B2** — the gallery says so in its own words at `:27` and `:777`.
*Gates items 29, 30, 31, and both halves of 12.*

### 49. The stature ceiling
**Context.** All nineteen boss-gallery candidates are Trounce-tier — the top of
Genshin's enemy-stature ladder — so filling act slots from that tier sets a
ceiling every other mapping must sit below, and an **Act 1** spend is the
sharpest version: Andrius and Dvalin are Genshin's two launch weekly bosses.
**Read.** `candidates.md:603` and §Assembly notes 5 at `:796-802`.
**Shape.** open.

### 50. Lagavulin Matriarch's ratified identity
**Context.** The Lagavulin base row is recorded in the enemy atlas as a ratified
[USER] pick whose signature drain is backlogged, and the atlas's own note is that
"touching her identity is a bigger call than any other row" — so any boss-gallery
variant on that slot is a re-opening, not a fill.
**Read.** `candidates.md:39` and `:271`; the atlas row is
`reskin-gallery.md:30`.
**Shape.** open. *Gates item 27.*

### 51. Stormterror Dvalin — two separate problems on one body
**Context.** Dvalin fails the proposed memory-framing rule (Confront Stormterror
is a live domain and he is a redeemed friend of Mondstadt by the end of the
Prologue), and separately his is the **only** Trounce domain in Genshin that
cannot be run in co-op — attributed to its fixed camera — on a mod that ships
co-op.
**Read.** `candidates.md:675-678` (the fiction half) and `:571` (the co-op half);
the carried flag is at `:47-49`.
**Shape.** open, or yes-no on whether he is spendable at all. *Gates items 27
and 31.*

### 52. Kaiser Crab and pair-hood
**Context.** No Genshin weekly boss is a matched pair — a third of the pool is
strict 1v1 and the rest run add waves around a single boss — so every weekly
candidate for the two-body Kaiser Crab must either convert a *sequential*
two-form boss into a *simultaneous* one, or promote adds to co-boss stature.
**Read.** `candidates.md` §Assembly notes 3 at `:767-775`, and `:41`.
**Shape.** open. The gallery records that this dissolves if item 48 lands on the
atlas side.

### 53. La Signora's canon death and the memory framing
**Context.** She is the only candidate in the boss gallery with an on-screen,
irreversible canon death, and her domain is explicitly subtitled a memory — so a
rotating pool that re-draws her every run either commits the act to a
recollection framing or quietly de-canonizes the execution.
**Read.** `candidates.md:506-507`, and the proposed rule `RQ2-B1` at `:661-680`.
**Shape.** open. *Touches items 26, 29 and 30.*

### 54. Nation concentration in the boss pools
**Context.** The proposed no-single-nation rule has three live breaches under the
current ordering — Andrius + Dvalin would commit Act 1 entirely to Mondstadt,
and Shouki + Apep would do the same to Sumeru in both Act 2 and Act 3.
**Read.** `candidates.md:604`, `:327`, `:532`, and rule `RQ2-C1` at `:685-700`.
**Shape.** open. *Gated on item 8 — the predicate's field has to be settled
before the breaches can even be counted.*

### 55. The redesign-pressure list — shipped bodies with no reskin cover
**Context.** Seven base enemies came back with no plausible candidate across all
sixteen surveyed families; two of them are **shipped content today** — the
Decimillipede, whose Reattach mechanic has no analogue anywhere in the surveyed
roster, and the Entomancer / Knowledge Demon pair, whose only cover is
plausible-at-best with an inverted-incentive caveat.
**Read.** `reskin-gallery.md:90-100` (§1).
**Shape.** open. See the note at the end of §B4 about whether this sits inside
the existing QUEUE row.

### 56. Three shipped encounters need family-coherent multi-body picks
**Context.** `construct_gang`, `bowlbug_pod` and `shield_and_turret` are
multi-body encounters, and taking the per-body best fit for each would produce
mixed-faction fights.
**Read.** `reskin-gallery.md:128`.
**Shape.** open.

### 57. Structural family gaps to plan an act around
**Context.** From the family atlases themselves: Abyss Order, Ruin Machines and
Consecrated Beasts have **no fodder rung**; Fatui Skirmishers and Specters have
**no boss rung**; Eremites and Specters have no summoner below elite/boss tier —
so any act themed to a single family needs a sibling family for the missing rung.
**Read.** `reskin-gallery.md:104-105` (§2).
**Shape.** open.

### 58. The Ancients' pure-upside model versus canon Vakuu — reading, no ask attached
**Context.** The repo models Ancients as pure upside, and the sim's sampling rule
("only boons that map 1:1 onto EXISTING hooks") is deliberate and ratified — but
the drafters' wiki work found that canon Vakuu is "The First Demon" whose ten
real boons all weld a permanent cost to the gift, so a faithful Vakuu is a
tempter and the shipped sample contains none of that half.
**Read.** `ancients-gallery.md:890-896` (§Assembly notes 3, final bullet), and
`:65-66`.
**Shape.** open. The gallery states plainly that nothing there proposes changing
the model; it is carried so a curator knows the flavour gap exists.

---

# §D — Gap appendix

## D1. Which items have a QUEUE row waiting for them

The charter asked for this appendix explicitly. **This agenda mints nothing** —
it records the gap and stops.

| Items | QUEUE row | BACKLOG row |
|---|---|---|
| **1–12** (all one-word calls) | **NONE** | none |
| **13–25** (Ancients picks and register calls) | **NONE** | none |
| **26–33** (boss picks and register calls) | **NONE** | none |
| **34–47** (event FLAGs and per-event ticks) | **NONE** | `EB-83` and `EB-84` cover the enchant follow-through only, and neither is one of these items |
| **48–58** (all discussions) | **NONE** | none |
| *S8 + S10* (linked in §0 and §B4, not numbered) | `S8 + S10 galleries`, QUEUE §3 | none |
| *Wood Carvings* (linked in §0, not numbered) | the eye-read half rides `S4-G11` | `EB-83` |

So: **all 58 numbered walking items are without a register row of their own.**
The only QUEUE row anywhere in the world track is the linked `S8 + S10
galleries`. `docs/current/STATE.md:239` lists "**Enemy remapping** — planned" as an
active workstream, which is the nearest thing to a home for §B2/§C, but it is a
status line, not a decision row, and it does not cover the Ancients or the event
gallery at all.

## D2. Citation problems found while compiling

Recorded, not fixed — this agenda writes only itself.

1. **Two stale line pointers, boss gallery → enemy atlas.** `candidates.md`
   cites `reskin-gallery.md:117` for the unimplemented-mechanic warning in three
   places (`:139`, `:148`, and inside rule `RQ2-D1` at `:719`), and
   `reskin-gallery.md:100` for the Knowledge Demon "plausible-only, soft cover"
   note once (§Assembly notes 4, `:792`). Neither target resolves any more: the
   reskin gallery grew a verification-flags section on 2026-08-13, and the
   current lines are **`:122-124`** and **`:98`** respectively. The other
   cross-references from that file (`:29-30`, `:53`, `:54`, `:72`, `:73`) still
   resolve correctly.
2. **A file renamed without its citers being updated.** The Ancients gallery
   cites the event gallery as bare `gallery.md` in three places — `:325`,
   `:598`, `:827`. No `gallery.md` exists anywhere in HEAD (the other citations
   in that file already use the full path).
   The **line numbers are all still correct** against
   `docs/current/dossiers/content/event-conversion-gallery.md` — I checked
   `:49`, `:56-57`, `:70-73` and `:74-77` and every one lands on the rule the
   citer describes. Only the filename is wrong.
3. **A cited path that is not in HEAD.** `ancients-gallery.md:243` cites
   `docs/sitting-prep-2026-08-05.md:215` as the record of the boon-family naming
   question. That file is not tracked; retrieve it with
   `git show pre-simplification-2026-08-06:docs/sitting-prep-2026-08-05.md` if
   the sitting wants the original wording.
4. **A research correction the Ancients gallery surfaced and nobody booked.**
   `ancients-gallery.md:876-880` records that the wiki attributes three boons
   which `docs/current/research/act2-act3-roster-research.md:215-224` lists as
   *unattributed* — Meat Cleaver, Sai, and the transform/enchant family — to
   Tanx specifically. That is a research correction, not a mechanical one, and
   it has **no QUEUE row and no BACKLOG row in HEAD**. It is not a [USER]
   decision and is recorded here only so it stops being invisible.

## D3. What this agenda does NOT establish

- It does not decide, recommend, default, or rank anything. Every ordering
  reproduced above is the source gallery's own.
- It does not verify any canon claim. Every gallery states its own sourcing
  quality, and several state it as uneven — the Ancients gallery records four
  `[UNVERIFIED]` claims on Tanx and one entirely search-summary-sourced Azhdaha
  variant (`:897-910`), and the boss pattern memo lists six figures its dossiers
  deliberately hedge (`pattern-memo.md:160-162`). None of that was re-checked
  tonight, and no web fetch was made.
- It does not touch mechanics. Every gallery freezes the base numbers, and this
  agenda proposes no change to a stat block, a hook, a boon, an act pool, or a
  YAML row.
- It does not establish that any of these questions is ripe, urgent, or worth a
  sitting slot. It establishes only that the material is finished, that the
  questions are written down, and where each one lives.
- It does not cover the potion/relic and reskin galleries' own asks, which are
  linked to their existing QUEUE row rather than repeated. Walking that row
  needs the row, not this file.
- **Item count is not a workload estimate.** Items 47 (41 event ticks), 13–20
  and 26–31 are checkbox curations that can be walked in a batch; items 48–58
  are not.

---

*Compiled 2026-08-26 from HEAD of the primary checkout. Sources: the five
finished galleries named in §0, `docs/current/QUEUE.md`,
`docs/current/BACKLOG.md`, `docs/current/RULINGS.md`, `docs/current/STATE.md`,
`docs/current/LAW.md`, `review/ruled/sitting-agenda-2026-08-08.md`, and
`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`. No file outside
`review/dispatch3/` was modified.*
