# S17 — disjoint batches and the deduped [USER] question list

> **This document decides nothing and recommends nothing.** It orders work into
> batches that do not overlap, and it deduplicates the questions the five family
> files and lane B raised into one numbered list. **No batch is scheduled,
> priced, or ranked against another.** No rights verdict, no taste call, no
> scope call, and no id is minted — every batch either lands on an existing
> register row or is explicitly blocked on a numbered question below.

**Date:** 2026-08-27. Re-run of the output deferred by the 2026-08-26 usage
limit (`review/dispatch3/BLOCKERS.md` §3 row 2). Companion to
`s17-joined-ledger-proposal.md`; read that first for the column set and the
reconciled totals.

**Disjointness rule used here (charter §5, §6):** every batch names **exactly
one owner** — one family, or one tool file — and **no id, surface, column or
file appears in two batches.** Where two batches touch adjacent populations the
boundary is stated in the row, because that is where a race would happen.

---

## 0. Three facts that change what the overnight files said

1. **`art/candidates/` was re-materialised 2026-08-27** — 297 directories, all
   27 contact sheets resolve. `BLOCKERS.md` §1.1 is **CLOSED**. The R212(1) veto
   route is open again, so every batch below that was blocked on "the sheet
   cannot be walked" is unblocked on that ground. No batch here is a sheet
   revival.
2. **Lane B's ledger is merged** (`tools/art_ledger.py`, 26 tests). The tooling
   batches below are *changes to a merged tool*, not proposals for a new one.
3. **`EB-153`, `EB-162` and `EB-163` were minted on 2026-08-27**
   (`docs/current/BACKLOG.md:85`, `:117`, `:118`). This file mints nothing and
   cites those.

### One observation that lands on somebody else's open question

`s17-kokomi.md` §7 Q1 asks which fallback the Pearl of Wisdom relic icon really
takes: the code declares `IconBaseName => "snake_ring"`
(`PearlOfWisdomRelic.cs:90-96`) while the `EB-67` capture recorded `NOPE`. Read
read-only from `…\SlayTheSpire2\logs\`: the 2026-08-26 20:55 session — running
the **pre-icon** pack, `pck build id: 20260826-180802+190e598` — carries both
`pck resource missing: res://kokomi/relics/pearl_of_wisdom.png` **and**
`[WARN] AtlasResourceLoader: Missing sprite 'snake_ring'`. So the declared
fallback **did** engage and the base game has no `snake_ring` sprite either;
both observations are true and there is no contradiction. **This is evidence for
Q1, not an answer to it** — the question is Kokomi's owner's and [USER]'s, and
the 20:56 session on the post-icon pack no longer asks for either path.

---

## 1. Production batches — one owner family each, no shared ids

| Batch | Owner family | Ids / surfaces (exhaustive) | Register row | Blocked on |
|---|---|---|---|---|
| **B-P1** | **Kokomi** | the 14 `EB-69`/`EB-121` fill faces: `the_gunbai_turns`, `all_hands`, `what_the_tokoyo_took`, `gyorin_formation`, `council_at_bourou`, `open_the_stores`, `wheel_the_ranks`, `what_the_tokoyo_returns`, `raise_the_sashimono`, `crane_wing`, `send_the_runner`, `massed_volley`, `hold_the_narrows`, `tighten_the_cords` | `EB-69` / `EB-121`; sheet `art/contact_sheet_eb121_kokomi_fill.html` (walkable again) | nothing — rank 1 exists for all 14, R212(1) applies |
| **B-P2** | **Kokomi** | `watch_of_the_shallows`, **alone** | `EB-26`; sheet `art/contact_sheet_run9_watch_of_the_shallows.html` | **[USER]** — no rank 1 exists **by design** (`art/plan.tsv:1145-1151`); `art_process` cannot promote anything. Deliberately split from B-P1 so the 14 are not held by the 1. |
| **B-P3** | **Furina** | the 7 `EB-65` sigils: `courtroom_drama`, `fortissimo_guard`, `quick_change`, `stagehands`, `stagehands_encore`, `the_gallery_stirs`, `unheard_confession` | `EB-65` (`BACKLOG.md:80`) | **[USER]** — Q1 below. No rank-1 row exists, so R212(1) has nothing to apply (`BLOCKERS.md` §1.3). |
| **B-P4** | **Furina** | `change_the_bill`, `take_it_from_the_top`, `grand_gala`, `spotlight_center_stage`, `spotlight_guest_cast` | Art debt (`QUEUE.md:53`, `grand_gala` r6 provisional) | **[USER]** — Q2 below |
| **B-P5** | **Klee** | `hold_the_line`, `powder_charge`, `smoke_and_sparks`, `confiscated` | — | **[USER]** — Q3 below. `s17-klee.md` §3.2: the locally fetched pool holds **zero** unclaimed Klee card faces, so this needs a fetch, a reuse, or a Tier P frame. |
| **B-P6** | **Klee** | the `Dodoco Tales` relic icon, **alone** | **`EB-162`** (`BACKLOG.md:117`) | nothing — hunt a shortlist, apply rank 1 under R212(1), commit the sheet |
| **B-P7** | **Klee** | `power_friendly_visit`, `power_study_buddy` — the two AS2-E2 "weak marks" | `S4-G17` / Art debt | **[USER]** — Q4 below. Incumbent r1 **stands** by R212(1) default if no pick lands. |
| **B-P8** | **companions** | **EMPTY — no production work is owed.** 51/51 card faces rendered, staged, deployed, provenance-recorded, lint-clean; 7/7 badges present; zero stale files; zero duplicates; zero effective collisions. | — | — |

**B-P8 is recorded as an empty batch on purpose.** An absent row reads as an
oversight; an empty batch reads as a measurement. The companion family's only
open items are a taste pass that is already the QUEUE Art-debt row, and the five
iconless powers — which are a **tooling and design** matter (B-T3, Q5), not a
production one.

**Boundary note (B-P1 ↔ B-P3):** both are "apply a shortlist rank 1", and both
are R212(1) shaped — but B-P1 *has* rank-1 rows and B-P3 does not. They must not
be run as one batch, because the second would silently invent a pick.

---

## 2. Tooling batches — one owner file each, no shared columns or populations

| Batch | Owner | Content (exhaustive) | Register row | Blocked on |
|---|---|---|---|---|
| **B-T1** | `tools/art_ledger.py` | **Column 9, `provenance_shape`, and the rights reader that depends on it.** `_rights_for` (`:655-664`) keys on the rendered out-path only, so the 46 shortlist companion cards — and every other shortlist-provenanced card in the repo — read `unclassified` while carrying a tier-`F` row against `art/candidates/<id>/r<n>.png`. Arithmetic proof in `s17-joined-ledger-proposal.md` §3c. **Population: ids that HAVE a `SOURCES.tsv` row under a non-out-path key.** | `EB-148` (lane B) | nothing — a reader change plus tests; no design content |
| **B-T2** | `tools/art_ledger.py` | **The other eight proposed columns:** `expectation_class` (5), `source_key` (8), `source_group` (10), `register` (11), `crop` (12), `ship_route` (17), `rights_derivation` (21), `review_route` (23). Reasons per column in `s17-joined-ledger-proposal.md` §2. **Disjoint from B-T1 by column**, same owner file — sequence them, do not parallelise them. | `EB-148` | `expectation_class`'s `undeclared` value needs B-T3's curated list to populate; the other seven do not |
| **B-T3** | a new curated list + lint (**not** `art_ledger.py`) | The `EB-153` population: the 7 `PowerModel` subclasses with no `PathFor` case and no `IconExempt` entry — `AncientSeaAuthority`, `CannonFireSupport`, `ExplosivesWorkshop`, `MasqueRedDeath`, `Metallicize`, `NightVigil`, `SalonCapUp` — **and** the concatenated `klee/powers/aura_*` prefix (`KleePowerIcons.cs:142-143`). Five of the seven are companion-family (`s17-companions.md` §3d, correcting the "four" in `s17-kokomi.md` §2c). | **`EB-153`** (`BACKLOG.md:85`) | nothing to build the lint; its *disposition* is Q5 |
| **B-T4** | `art/SOURCES.tsv` + `tools/art_fetch.py` | The `EB-163` backfill. **Population: ids with NO row at ANY key** — the 22 Kokomi asset ids (`s17-kokomi.md` §4) and the icons family's 37 of 113 non-card outputs (`s17-icons-ui-models-vfx.md` §10). **Explicitly disjoint from B-T1**, which touches only ids that already have a row somewhere. Running B-T4 first would hide B-T1's defect; running B-T1 first shrinks B-T4's real population to its true size. | **`EB-163`** (`BACKLOG.md:118`) | nothing |
| **B-T5** | `tools/art_lint.py` | Register the 3 unregistered producers' 12 packed out-paths in `GENERATOR_OWNED`: `cut_combat_layers.py` (9 files), `cut_salon_members.py` (3 files). No row for the `*_cutout.png` caches, which have no plan row and no packed path. `s17-icons-ui-models-vfx.md` §8. | — (hygiene-shaped) | nothing |
| **B-T6** | `KleeSelfCheck` / one instrumented boot | **Explain R13's silence.** `CheckPowerIcons` (`Diagnostics/KleeSelfCheck.cs:407-440`) fails on any constructible iconless `PowerModel`, yet the same session logs `[klee] SELFCHECK passed`, with five iconless powers present. Only escape in the code is the `catch (Exception) { continue; }` at `:423-429`, and none of the five declares an explicit constructor. **UNKNOWN from source alone** — `game_ref/` on this machine holds no C# decompile. | feeds **`EB-153`** acceptance | **needs the game.** This dispatch's rail may not launch, deploy, or write to the installation. |
| **B-T7** | one named integrator | The one-line `tools/run_lints.py` wiring for `art_ledger`, per lane B §7 — a **shared file** with lane C, deliberately not raced. | `EB-148` D6 | **[USER]** — Q9 and Q10 below |

**Boundary note (B-T3 ↔ B-T2):** B-T3 produces the curated list; B-T2 consumes
it to populate `expectation_class=undeclared`. One produces, one reads. They must
not both edit the list.

**Boundary note (B-T1/B-T2 ↔ lane C):** the stable contract lane C consumes is
`SCHEMA_VERSION = "art-ledger-v1"` and the `Row` field names
(`tooling-laneb-handoff.md` merge risk 2). Nine added fields and one changed
reader are a **schema bump**, not a compatible edit. Whoever runs B-T1/B-T2 owns
telling lane C.

---

## 3. Deduped, numbered questions for [USER]

**Twelve questions.** Every one is a pick list; none is a blank; none carries a
recommendation. Sources are named so a cold read can trace each back. Where a
question is **already an open register row**, it is *cited, not re-asked* — it
appears here only so the sitting can walk one list.

**Q1 — the seven Furina sigils have no rank 1 (`EB-65`).**
*Raised by:* `s17-furina.md` §11.1, lane B Q1, `BLOCKERS.md` §1.3 — **one
question, three files.**
(a) Claude promotes each shortlist r2 to r1 and lands the seven under R212(1),
veto on the (now walkable) sheet — reading "apply rank 1" as "apply the
top-ranked candidate"; (b) [USER] picks r2-or-r3 per row off the sheet;
(c) leave `EB-65` deferred and re-hunt first, accepting that
`art-runs-2026-08-08.md:197-200` says the free pool is exhausted for this brief;
(d) accept the base-game placeholder for all seven and record the acceptance so
the ledger stops billing them; (e) re-scope `EB-65` to say what it actually
needs.

**Q2 — the Furina card bill (B-P4).** *Raised by:* `s17-furina.md` §11.2 and
§11.5 (Art debt pick 3, `grand_gala` r6 provisional).
(a) hunt all five now and accept whatever the thin pool returns; (b) hunt and
accept an empty result as a recorded zero; (c) leave them until a Tier O pass;
(d) reuse an existing Furina crop deliberately and record the reuse.

**Q3 — the Klee card bill, with an exhausted local pool (B-P5).** *Raised by:*
`s17-klee.md` §10 Pick 3.
(a) spend a fresh `art_hunt` on Klee; (b) ship them on the Tier P programmatic
frame (`docs/art-asset-manifest.md:78`, "art never blocks the build");
(c) re-crop an already-claimed Klee source into a second face, accepting a
deliberate motif reuse.

**Q4 — the two Klee "weak mark" badges (B-P7).** *Raised by:* `s17-klee.md` §10
Pick 2.
(a) keep both incumbents — the R212(1) default if no pick lands; (b) take a
staged r2 for one or both (`Item Gift` / `Trifolium`; `Book Ragged Notebook` /
`Trifolium Shape`); (c) re-hunt both. The sheet route is open again as of
2026-08-27.

**Q5 — disposition of the seven iconless powers (`EB-153`).** *Raised by:*
`s17-icons-ui-models-vfx.md` §11(3), lane B Q4, `s17-companions.md` §3d — **one
question, three files.** Five of the seven are companion-family; only
`Metallicize` produces any runtime evidence (8 `Missing sprite
'metallicize_power'` lines in `godot.log`), so the other four are silent to every
instrument.
(a) build the curated list + lint (B-T3) and then commission icons for all
seven; (b) lint them and accept the base-game placeholder, recording the
acceptance; (c) rule them out of scope as companion/base-mirror powers that
should not carry our sigils; (d) split — icons for the four with a named
companion identity, acceptance for the three generic ones.

**Q6 — the source-uniqueness rule, unwritten in two families.** *Raised by:*
`s17-kokomi.md` §7 Q2 and `s17-companions.md` §9 Q1 — **one question, two
files.** Furina's rule is rarity-scoped and ratified
(`furina-art-pass-requirements.md:100-116`); Kokomi's is character-wide and
unwritten; companions' is per-Genshin-character and unwritten, and is what the
`source_group` column was **built for** (`tools/art_fetch.py:66-74`).
(a) write each family's rule down as it stands, in its own requirements doc;
(b) write **one** source-uniqueness law with the per-family scoping as clauses;
(c) adopt Furina's rarity split roster-wide, accepting that re-crops are owed on
up to 12 Kokomi identity faces; (d) leave all three unwritten and keep the
column as the only authority.

**Q7 — latent card ↔ badge source pairs.** *Raised by:* `s17-companions.md` §9
Q2, `s17-klee.md` §8 (12 instances), `s17-icons-ui-models-vfx.md` §9(a) — and
already on [USER]'s plate once as Art debt pick (1), the
`ovation_trickle`/`stagehands_encore` sigil collision (`QUEUE.md:53`). **None of
them bites today; all sit on an r2 or r3.**
(a) leave them all — effective picks differ, and promoting an r2 is a decision
someone will make with eyes open; (b) move one rank off the shared file in each
pair so no promotion can collide; (c) rule card↔badge source reuse **legal by
construction** the way `art_lint.py:44-49` already rules register-crossing reuse
legal, and stop tracking it; (d) add the `source_key` column (B-T2) so they are
at least reportable, and defer the policy.

**Q8 — rights classification (`EB-163` and the derived-asset disagreement).**
*Raised by:* lane B Q5, `s17-kokomi.md` §4, `s17-icons-ui-models-vfx.md` §10,
`s17-klee.md` §2 vs `s17-icons-ui-models-vfx.md` §7 (which disagree on where a
*derived* asset goes: private-placeholder or UNKNOWN).
(a) backfill `SOURCES.tsv` rows for every shipped output so the tier column
answers for all of them; (b) add a separate rights declaration file the ledger
reads, leaving `SOURCES.tsv` as the fetch ledger; (c) leave them unclassified
until a public release is on the table; **and, separately,** for derived assets:
(i) inherit the input's category, (ii) mark them UNKNOWN, (iii) record the
derivation in its own column (B-T2's `rights_derivation`) and decide later.

**Q9 — wiring `art_ledger` into a lint lane.** *Raised by:* lane B Q6.
(a) `local` lane with the D1 contract-absent skip mode, after Q1–Q3 and Q11 are
dispositioned; (b) `ci` lane (needs D1 **and** those dispositions first, or it is
red on day one); (c) no lane — run it by hand when the art question comes up.

**Q10 — who owns the shared `tools/run_lints.py` edit (B-T7).** *Raised by:*
lane B Q7. (a) lane B; (b) lane C; (c) a named integrator at merge time.

**Q11 — the four rendered-but-unreferenced files.** *Raised by:* lane B Q2 and
Q3, `s17-icons-ui-models-vfx.md` §11(1), `s17-klee.md` §7.3, `s17-furina.md` §6a
— **one question, four files.** `energy_icon_22/74.png` for Klee and Furina are
packed and unreachable (all three characters point `CustomEnergyCounterPath` at
the base game's counter scene); `character_klee_full_wish.png` and
`klee_character_card.png` are source plates that ship because the `model` copy
block is a blanket `*.png`.
(a) delete them and let them leave the pack; (b) keep them and add a recorded
`KNOWN_STALE`-style reason so they read as deliberate; (c) build our own
energy-counter scene, which is a real feature and would also give `M19`'s orb
layer set somewhere to land; (d) rename the two plates to match `$pckExclude`.
**Note:** `M19` (`QUEUE.md:51`) is **cited, not re-asked** — its pick list is
already written, and `s17-furina.md` F8 records that the layer set does nothing
until an energy-counter scene exists.

**Q12 — the companion badge namespace and the missing requirements docs.**
*Raised by:* `s17-companions.md` §9 Q4 and Q5. Seven companion badges ship as
`res://klee/powers/*`; no path in the repo says "companion" for a non-card
surface; and `docs/current/art/` has requirements docs for Furina and Kokomi
only — none for Klee, none for companions.
(a) leave the paths and write the two missing requirements docs; (b) introduce
`companions/powers/` and move the seven, accepting one `build_pck.ps1` copy-block
change and one `KleePowerIcons` edit; (c) leave the paths and add a **registry**
(a curated id → family list) so tools can answer family questions without a path
glob; (d) change nothing and let the `owner` column in the ledger be the only
answer.

### Retired from this list

| item | why it is not a question any more |
|---|---|
| "The Furina / Klee / EB-65 contact sheets are unrenderable" (`s17-furina.md` §11.3, `s17-klee.md` §7.1, `BLOCKERS.md` §1.1) | **CLOSED 2026-08-27** — `art/candidates/` re-materialised, 297 directories, all 27 sheets resolve |
| "Which fallback does the Pearl of Wisdom relic icon take" (`s17-kokomi.md` §7 Q1) | **not retired — evidence added.** See §0; both the declared `snake_ring` fallback and the `NOPE` observation are true, in the same pre-icon session. The question of what to do stays Kokomi's owner's. |
| `M19`, `S4-G17`, `M16`, `M26`, Art debt picks (1)–(3) | already open QUEUE rows with written pick lists; cited above where they are touched, and **no existing ranking is changed by this file** |
| Doc drift in `furina-art-pass-requirements.md` §8 (`s17-furina.md` §11.6) | hygiene-shaped under `CLAUDE.md`'s norm; routed to the morning hygiene list by `CURATION.md` §S17, not re-asked here |

---

## 4. What this document does **NOT** establish

It does not rank, price, schedule, or recommend any batch — the batches are
**disjoint**, not ordered, and "B-P1" is a label, not a priority. It does not
establish that any batch should be run at all. It makes no rights verdict: the
only rights content here is Q8, which is a pick list, and no asset is called
safe or unsafe. It makes no taste call: every "apply rank 1" above is the
existing R212(1) mechanism with [USER]'s veto intact, and every alternative is
offered without preference. It does not establish that the seven iconless powers
need art, that the badge namespace should move, that any requirements doc is
owed, or that any latent collision matters. It does not establish why
`KleeSelfCheck` R13 is silent — B-T6 exists precisely because that is UNKNOWN
and needs the game, which this rail may not launch. It mints no id; every batch
lands on `EB-65`, `EB-69`/`EB-121`, `EB-26`, `EB-148`, `EB-153`, `EB-162`,
`EB-163`, `S4-G17`, `M19` or the QUEUE Art-debt row, or is explicitly blocked on
one of the twelve questions above.
