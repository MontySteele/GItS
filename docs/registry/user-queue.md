# The [USER] queue — single source of truth

**Status: REGISTER.** Opened 2026-08-06 by the housekeeping sweep (Track X) of
the "Strike the Set" batch. **Zero design authority.** Nothing here is decided,
scheduled, graded or priced. Every row is copied from the document that owns it;
where two documents disagree about a status, the later ruling wins and is named.

**What this file replaces.** Before it, "what is open for [USER]" was spread
across at least eight registers: `review/ledger-audit/hygiene-report.md` §3,
`docs/backlog-2026-07-29.md` §3/§4/§5, `docs/open-playtest-items.md` §1/§3/§6,
`docs/surplus-week-manifest-2026-08-05.md` §4 and its Second Wind addendum,
`docs/sitting-prep-2026-08-05.md` §8/§10, `docs/awaiting-user-slots-2026-08-06.md`,
`docs/dockets/`, and the DRAFT rulings themselves. Each of those keeps its own
full text — **this file is an index, not a replacement.** Their "open items"
sections now point here.

**Standing discipline this file obeys.** HELD flags are copied in as held
(FLAG-1…FLAG-4). The R102 escrow stays frozen. Awaited one-liners are recorded
as awaited; recording is not answering.

---

## 1. AWAITING a one-word reply — the cheapest items in the repo

Each of these unblocks written, tested work with a single word. Landing text is
pre-drafted where noted, so the reply is the only cost.

| # | Ask | Reply shape | Unblocks | Full text |
|---|---|---|---|---|
| ~~Q1~~ | ~~**F6 / `NT-G5`:** is the 2026-08-01/02 three-seat session "playtest three" for the pre-registered Kokomi fork?~~ | ~~YES / NO~~ | **ANSWERED 2026-08-06 — YES** (Track Y / Y-1): *"YES — the 08-01/02 session is playtest three; the current Kokomi build was played."* Slot 1's YES form landed verbatim in `klee-mod/DECISIONS.md` beneath the fork block. **The fork's evaluation is now row `Q5` below** | ~~`docs/awaiting-user-slots-2026-08-06.md` slot 1~~ → landed; slot marked ANSWERED |
| ~~Q2~~ | ~~**X2 audit venue:** does `docs/dockets/companion-pricing.md` own X2 rarity work going forward?~~ | ~~YES / NO~~ | **ANSWERED 2026-08-06 — YES** (Track Y / Y-2): *"YES — companion-pricing docket owns X2 rarity work"*. Assignment line landed in that docket's §2 and the "unrouted" marker is cleared. The `Star`-vs-`rarity` C# enforceability question rides with the work and is now that docket's | ~~`docs/awaiting-user-slots-2026-08-06.md` slot 2~~ → landed |
| ~~Q3~~ | ~~**F14's siblings:** approve the staged repair of four further `R91/1c` misattributions + a new citation lint?~~ | ~~MERGE / SEND BACK~~ | **ANSWERED 2026-08-06 — MERGE** (Track Y / Y-3). `staged/f14-siblings` (`eaa83e5`) merged into `findings/track-y`; one conflict in `.github/workflows/repo.yml` (two lint steps added to the same job on both sides) resolved by keeping both. Suite green on the merge commit. **Still live and deliberately unlinted:** the same misattribution in `tools/lint_role_tempo_coverage.py` (3 occurrences) — widening the lint's scope is a separate decision, not taken | ~~`docs/awaiting-user-slots-2026-08-06.md` slot 3~~ → merged |
| ~~Q4~~ | ~~**`SW2-S-1`'s stopped deletion:** does deleting `copy_cost_override: 0` from Encore Performance's upgrade now proceed?~~ | ~~YES / NO~~ | **ANSWERED 2026-08-06 — YES** (Track Y / Y-4). Deleted from `docs/furina-upgrades.yaml`; the `SHEET_EXEMPT` entry is now load-bearing (verified in both directions); the C# card and manifest regenerated; `gen_roster_cards.py --check` green. Two follow-on registers were needed and are twins of the exemption, not new judgments: `CODEGEN_DEBT` (layer 2) and `FURINA_UPGRADE_GAP_PENDING_FB1` in `tier0/tests/test_roster_codegen.py`. All three delete together when FLAG-2 is ruled. **One pin transitioned — see `Q6`** | ~~`docs/surplus-week-manifest-2026-08-05.md`~~ → executed |
| Q6 | **The X6 exploit line can no longer be run — repair it, or retire it? NEW, opened 2026-08-06 as a consequence of `Q4`.** Plainly: one of the recorded exploit recipes drafts an *upgraded* Encore Performance, and that upgrade no longer exists, so the replay harness cannot build the deck and the test now skips instead of running | REPAIR / RETIRE / LEAVE | `tier0/tests/test_s13_exploit_pins.py::test_x6_salon_displacement_is_priced` went **xfail → SKIP**. The skip is the harness saying "I could not execute", never "this is fixed" — the X6 mechanism (Salon FIFO displacement paying free final bows) is untouched and is still R111's WATCH ITEM. **REPAIR** = drop the `+` from the line's `upgraded` set and re-verify at the card's now-printed 0 cost; **RETIRE** = keep the line as the record of a recipe a ratified change made unbuildable; **LEAVE** = accept a permanently skipping pin. Editing a verified exploit corpus is an instrument decision, so Track Y took none of the three | `review/redteam/exploit-lines.json`, line `furina_salon_3_gala_bow_storm`; the pin's own docstring carries the full note |

| Q5 | **`NT-G5` fork evaluation — NEW, opened 2026-08-06 by Q1's YES.** Did Neap Tide (Kokomi) **read weak at the table** during the 2026-08-01/02 playtest? Plainly: playing her, did she feel underpowered, or did she feel fine? | WEAK / FINE | **WEAK** → lever 2 is pulled in an isolated cell (one knob, its own arm, measured alone). **FINE** → lever 3 is pulled **and** the sim-calibration offset for exhaust-loop kits is finally written down as a number — it has been asserted three times and never quantified. Until this word arrives no lever moves and `S4-G13`'s fork half stays open | `klee-mod/DECISIONS.md`, "PRE-REGISTERED FORK for playtest three (G5, confirmed)" + its 2026-08-06 [USER] annotation |

**Why `Q5` is not a repeat of `Q1`.** `Q1` asked whether the trigger fired;
`Q5` asks what the hands said. The pre-registration is explicit that **the hand
is the tiebreaker, not the sim**, so Code cannot answer `Q5` by measuring — it
is a memory of play, and it is the only input the fork accepts.

### Already answered — recorded so they are not re-asked

| Ask | Reply (verbatim where quoted) | Executed |
|---|---|---|
| Encore Performance's upgrade: replacement delta or curated exemption? | *"CURATED EXEMPTION now; the replacement delta is deferred behind FLAG-2."* | Register entry in `tools/lint_upgrade_coverage.py::SHEET_EXEMPT` (Track W). **Q4 above is the residue.** |
| `CONSTANTS_VERSION` 4→5? | **APPROVED** | `CONSTANTS_VERSION = 5`; archive banners on six documents publishing Furina tier-0.5 numbers. No number rewritten (R101b). |
| X7 limb (a) reading: broad or strict? | *"infinite sparks must not be achievable at Common"* — some Common spark generation is fine | Dated annotation on R109; six candidates re-read → **3 VIOLATION / 3 CLEARED** (`docs/dockets/klee-rework.md` §2c) |

---

## 2. The S4 gate queue, reconciled

Twenty gates from `review/ledger-audit/hygiene-report.md` §3, carried forward
with their discharges named. **Qualified as `S4-G<n>`** (see
`docs/registry/identifiers.md` §2.1 — six other namespaces mint `G1`).

| Gate | What is asked | Where the full text lives | Status |
|---|---|---|---|
| `S4-G1` | R88 countersign — Zhongli slot 4 / Itto eligibility | `tier0/DECISIONS.md` R88 | **DISCHARGED by R108** (2026-08-06). Rider still open: §5 row 10.8. |
| `S4-G2` | R89 countersign — Furina legibility sprint record | `tier0/DECISIONS.md` R89 (DRAFT) | OPEN |
| `S4-G3` | Principles **v1.12** ratification (Fanfare single-leg + printed cap/grant X values) | `docs/teyvat-spire-design-principles.md`, "Amendment DRAFTS" | OPEN — shipped in code, law text unratified |
| `S4-G4` | Principles **v1.13** ratification (bounded runtime art fitting) | same, drafts section | OPEN |
| `S4-G5` | **`B-G1`** — per-axis disposition of the seven-axis scorecard; carries the re-registered Fanfare P1 | `docs/axis-validity-session-charter.md` §4/§7; R90/1b | OPEN. Until it rules, axis numbers stay *"reportable, not load-bearing"* (`DEC-D3` clause 3). **Now also the governing condition on §3's Furina items 1–3 and the fanfare STOP** (R107/F1). |
| `S4-G6` | **Kokomi stability-band declaration** — from design intent, before the confirmatory playtest; may not be revised against it | `tier0/DECISIONS.md` `DEC-D5` clauses 2–4; backlog §3 item 5 | OPEN — gates grading her protocol playtest |
| `S4-G7` | Furina items 1–3 (strength lever + legibility; dead-archetype; salon leak) | backlog §3 items 1–3 | OPEN. **Re-fenced 2026-08-06** — was "mis-fenced"; R107/F1 re-pointed the condition to `B-G1`. |
| `S4-G8` | DRAFTER 13 repricing ledger entry / number ratification | `docs/sprint-sim-hygiene-log-2026-07-29.md` | **DISCHARGED by R107(a)** (2026-08-06) |
| `S4-G9` | The ratification batch — ~14 sub-items (fanfare-rework X values; conversion clauses; `lasting_impression`; negative-floor semantics; D6 bow space; `kurages_oath`=12 re-file; pulse 2-vs-3; Curtain Call's four follow-ons; `scattering_spray` 7→6; Spotlight ten-icons-vs-family; Klee dead-card reworks) | backlog §3 item 9 | OPEN |
| `S4-G10` | Shop channel §7 close-out — `SHOP-P1…P3` grading; does the purse ever bind; the 1.15× surcharge; Track A pool migration; **R60 phase-2 fantasy-leak grading** | R60/R63; principles §4.7 notes 2–3 | OPEN — R60's stated trigger has been satisfied since 2026-07-25 |
| `S4-G11` | **R29d** naming/lore eyes-on pass (Furina); plus Kokomi R58 fill block AUTHORED-NOT-AUDITED and kickoff ask 10 | `tier0/DECISIONS.md` entry 75 + R29d banner; R58 | OPEN |
| `S4-G12` | = **`CC-G1` + `CC-G2`** (R86): contact-sheet eyes-on (four REHUNT picks + `standing_room_only` overturn) and in-game screenshot review of the twelve Curtain Call cards + the A0 smoke run | `tier0/DECISIONS.md` R86 | OPEN — **materials ready**: `docs/g12-review-2026-08-05.md` (contact sheets verified, all 24 captures). See also §5 row 10.1: five of nineteen art candidates fail lint if picked. |
| `S4-G13` | Neap Tide standing question — Kokomi below the Ironclad-anchored floor; three levers, *"none is Code's to pull"*; plus the `NT-G5` fork | `klee-mod/DECISIONS.md` E2/E2b + addendum | OPEN. ~~the fork half turns on **Q1**~~ **Updated 2026-08-06:** Q1 answered YES, so the fork has **fired** and its half of this gate is now the scheduled sitting item **Q5** (weak-or-fine). The standing question itself is unchanged |
| `S4-G14` | Kokomi protocol playtest (Q1–Q7 + three priority checks; Answers blank) | `docs/kokomi-playtest-protocol.md` | OPEN — blocked on `S4-G6`, and (per backlog §4) on the N1 attribution pass |
| `S4-G15` | **Corpse detonation settlement** — ~10 s at the table; failure invalidates every sim bomb number vs killable enemies | `klee-mod/DECISIONS.md` "Corpse detonation — OPEN" | OPEN since 2026-07-21, through ≥5 playtests (*nobody checked in playtest 4*) |
| `S4-G16` | **`G-A5(b)`** fourth shape — one capture of a Power play raising the Fanfare floor | `docs/red-pen-2026-07-26.md` Part 3 | OPEN |
| `S4-G17` | **Table looks** — `AS2-D5` salon capture (now unblocked by the sprite-scale fix); `AS2-B5` motion pass + facing taste; `AS2-E2` icon picks (4 REHUNT); hover-targets question | `docs/open-playtest-items.md` §3; backlog §4/§5 | OPEN, urgency reduced: hover-targets **CLOSED at playtest 4**; B5 "not noticed" |
| `S4-G18` | Klee pass-4 **ask A3** — 28/21/14 archetype-band deviation vs principles' 15–20, never amended or accepted | `docs/missed-requirements.md` Tier 5 | OPEN (ask A5 is *deliberately* deferred by `DEC-D3` — distinct) |
| `S4-G19` | **Sly unification** design ruling — two mechanics, one word | `docs/tech-debt-audit-2026-07-26.md` §5 | OPEN |
| `S4-G20` | Standing Ovation boost expiry; sim-vs-C# salon RNG divergence acceptance; taste passes (Kokomi 58 faces + 15 companions, L12 duplicate pairs, `kaboom == spark_knight_style`); infra (branch protection / `gh`); manifest MAJOR bump (R70, dormant by design) | backlog §1 P3-cluster + §5 | OPEN |

---

## 3. Held flags — not to be built against

Four clarifications carried out of the sitting of 2026-08-06 **unresolved**.
`docs/dockets/README.md` house rule 3: nothing may be built against a held flag.
Full questions: `docs/registry/identifiers.md` §6, and R110/R111 verbatim.

| Flag | Family | One-line |
|---|---|---|
| FLAG-1 | `S13-X1` | The accumulator's second enabler (Kokomi `honor_guard`) / a structural disposition for the shared uncapped state |
| FLAG-2 | `S13-X3` | Two adjacent closures: copy-outruns-Exhaust (design call) and unscoped `cost_override` (reads as a straight bug) |
| FLAG-3 | `S13-X5` | Does "seems fine" cover decay-proof fanfare-floor stacking, or only the cantrip leg? |
| FLAG-4 | `S13-X14` | Legs (a) `curse_poor_sleep` retain-jam and (c) all-Power deck self-erasure |

---

## 4. Sittings owed on landed review artifacts

| Item | What is asked | Unblocks | Full text |
|---|---|---|---|
| **R102 escrow release** | Strike the four PROVISIONAL fanfare marks as instrument-vindicated, **or** formally re-open any of them. One clean ledger operation either way. **Both probes have now reported** — direction: tier0 is NOT pessimistic on fanfare, so R102's stated worry is unsupported. | Four fanfare conclusions currently frozen: the threshold-reach table, the 1.8% STOP, the early-half grade, and the R91/2b posture | `tier0/DECISIONS.md` R102; `docs/sitting-prep-2026-08-05.md` §10.11; `docs/probe-a-block-offset.md`, `docs/probe-b-fanfare-residual.md`. **FROZEN pending this ruling — Track X did not touch it.** |
| **S2 event-gallery checkboxes** | Curation sitting: 47 events, 141 drafted variants → 130 kept / 11 cut, 4 demotions | The event layer's conversion pass | `review/event-gallery/gallery.md` |
| **S14 canonicity rulings** | Four named questions: **NC-1** (companion/power damage skipping the damage pipeline in C#), **shop slot 1** (`NC-10`, can never roll a Rare in the mod), **Frozen** (`NC-7`, two different mechanics), **`spend_potion`** (`NC-8`, never paid) | The rest of the 174-finding S14 triage | `review/parity-sweep/noncard-triage-memo.md`; restated by R112 |
| **S13 residual sitting items** | The four HELD flags above; plus paperwork one-liner 4 in §6 (do S13's 71 lines need re-verification against `S7-C1`/`S7-C2` and the S14 routings before any family is treated as a game fact?) | Treating any exploit family as a game fact | `review/redteam/exploit-ledger.md`; `docs/sitting-prep-2026-08-05.md` §8 item 4 |
| **N and O TOP-5 reviews** | Read the two severity-ordered ledgers top-5-first. Includes **N-1** (routed by R112) and the standing caveat that the reactions corpus is PROVISIONAL until ruled | The lore-repair and instrument-repair queues | `docs/lore-fidelity-audit-2026-08-05.md`, `docs/instrument-redteam-2026-08-05.md`; `docs/sitting-prep-2026-08-05.md` §10.14 |
| **S8's 8 flagged items** and **S10's reskin candidates** | Candidates, not verdicts. RESKIN/REDESIGN remains [USER]'s call per north-star | content conversion | `review/potion-relic-gallery/gallery.md`, `review/enemy-atlas/reskin-gallery.md` |
| **Ancients + boss-pool galleries** | *Inspiration-optional — no review obligation.* Curated best-first, checkbox per entity | nothing is blocked on these | `review/ancients-gallery/gallery.md`, `review/boss-pool-gallery/gallery.md` |
| **X10 pricing** (`gorou_heart_of_the_clan`) | A **CANDIDATE, explicitly not ratified**: Uncommon promotion + power adjustment, priced at a sitting | the companion-pricing docket's §1 | `docs/dockets/companion-pricing.md` §1 |
| **R1–R38 resolvability** *(surfaced by this sweep)* | Early R-numbers exist only inside prose entries and archived ruling docs; several (R8, R13, R14, R24, R25, R29d) are cited as standing law and no index maps them to a dated entry. Is a back-index worth building, or are they historical? | Any citation audit of pre-R39 law | S4 §4 lead 3; `docs/registry/identifiers.md` §3 |

---

## 5. The Last Call batch's own asks (sitting-prep §10)

Each is a yes/no or a pick-one. Full text: `docs/sitting-prep-2026-08-05.md` §10.
None was ruled at the 2026-08-06 sitting except where noted.

| # | Ask | Shape |
|---|---|---|
| 10.1 | `S4-G12` changed shape: five of nineteen art candidates fail `art_lint` if picked; `standing_room_only`'s recommended r3 fails `ART-L1` | pick one of four |
| 10.2 | Roster-anchor **v14** table (`RA-G1`): designate the quotable successor to the D13 n=3000 standing table, or hold. Rider: should `ref_ironclad`'s `archetype_package` carry `Card.archetypes` tags? | yes/no + a design-shaped rider |
| 10.3 | Spotlight limb definition — extend payoff-presence to the spotlight limb? Blast radius: exactly one card (`limelight`) | yes/no |
| 10.4 | `unmodelled_starting_relics` spelling in `tools/patch_sentinel.py` — keep it? | yes/no |
| 10.5 | Which module did `UND-P1.5`'s acceptance clause mean? Both `understudy/replay.py` and `understudy/trace_replay.py` exist and are complementary | confirm/correct |
| 10.6 | Punch Off reclassification: SUSPECTED-OURS → game-side. Note either way: the crash log has rotated out | yes/no |
| 10.7 | Payoff-reach fence adjacency: (a) where does the payoff-reach/`RARITY_ODDS` registration document live — it could not be found in the repo; (b) quarantine `RA-G1`/`RA-G2` core-attainment columns until (a) is answered? | two asks |
| 10.8 | **R88's draft conflicts with ratified R52 and shipped content** — the reserved-character rule vs Neuvillette. **Read before signing.** R108 countersigned the slot; this conflict is not thereby resolved | pick one of four |
| 10.9 | §2.2a's stated evidence does not exist (the act-3 Ancient stun reward). Authorize a later citation repair? Rule untouched either way | yes/no |
| 10.10 | Columbina has shipped; Appendix A.6's premise expired | awareness only, no ask |
| 10.11 | **The C2 escrow is now rulable** — see §4, R102 escrow release | strike or re-open |
| 10.12 | Family-A dependency hits in the S13 ledger: **none found**. Accept the null as closing the C-c order, or order a wider derivation test? | yes/no |
| 10.13 | **Probe (d) registration** — `docs/probe-d-registration-draft.md`, drafted and unsigned; nothing has been run | countersign yes/no |
| 10.14 | N + O ledgers, read top-5-first — see §4 | read |

---

## 6. Paperwork one-liners (the four the merge train carried)

Four corrections that need a yes/no and nothing else; each leaves a false or
ambiguous statement in a live artifact if declined. Full text:
`docs/sitting-prep-2026-08-05.md` §8. Restated as still-open by R112.

1. **S15 pin-table sum mismatch** — headline 111 vs a counted 133 test functions; the per-module table lists 0 for four files that carry tests. Authorise correcting the table and headline, or leave.
2. **S8 header 42-vs-51 miscount** — one preamble line in `review/potion-relic-gallery/gallery.md`. Authorise correcting to 51, or leave.
3. **`review/enemy-dossiers` stale branch pointer** — points at `e07fb4c`; the content landed via `ec15028` + `28759f0`. Delete / repoint / leave.
4. **S13 re-verification against `S7-C1`/`S7-C2`** — re-verify all 71 lines, only the block- and fanfare-dependent families, or proceed on the caveat as written.

---

## 7. Table time (not desk work)

| Item | Note |
|---|---|
| **Kokomi protocol playtest** (`S4-G14`) | Q1–Q7 + three priority checks. Blocked on `S4-G6` and the N1 attribution pass. PARTIAL at playtest 4: priority check 3 closed; Q1/Q4 "unjudgeable — the pulse has no visual"; Q6 a second-hand soft flag |
| **Corpse detonation** (`S4-G15`) | ~10 s. Nobody checked in playtest 4; now sequenced behind the N1 attribution pass |
| **`CC-G1` / `CC-G2`** (`S4-G12`) | Contact-sheet eyes-on + nine empty evidence slots incl. does-Crescendo-reset. Materials ready |
| **`AS2-D5` salon capture** | Unblocked by the playtest-3 sprite-scale fix. **Capture required this time** |
| **`AS2-B5` motion pass** | "Not noticed" at playtest 4 — urgency down, deliberate judgment still owed |
| **Build 0.2-296 distribution + telemetry notice** | To the table (`docs/surplus-week-manifest-2026-08-05.md` §4 item 6) |
| **R105 fact-sheet item** | Carried in the Last Call Track E work (`docs/surplus-week-manifest-2026-08-05.md` §4 item 7) |

---

## 8. Art debt (mostly taste)

`docs/backlog-2026-07-29.md` §5 holds the full list and remains its own
register: Kokomi 58 faces + 15 companions awaiting picks; four missing Kokomi
portraits; `curtain_cue` wordmark; `breathless` mood; A7 + six Curtain Call
power sigils on placeholder; `AS2-E2` icon re-hunt (4 of 7); two `ART-L12`
duplicate crops allowlisted + the unledgered `kaboom == spark_knight_style`
collision; three energy counters pointing at `ironclad_energy_counter.tscn`;
`_outline` char icons never produced.

---

## 9. AWAITING — facts this sweep could not supply

Recorded rather than guessed, per the no-supplied-assumptions norm.

1. ~~**Is the 2026-08-01/02 session "playtest three"?** (Q1.) Everything about
   `NT-G5`, `S4-G13`'s fork half, and the unwritten exhaust-loop calibration
   offset turns on this one word.~~ **SUPPLIED 2026-08-06 (Track Y): YES.** The
   fact this sweep could not supply has been supplied. What it unblocked is not
   an answer but a second question, `Q5` — the fork evaluation — and the
   calibration offset is still unwritten, now owed by that evaluation.
2. **Do R1–R38 need a back-index, or are they historical?** (§4.) This sweep
   could not resolve them mechanically and did not invent a mapping.
3. **Where does the payoff-reach / `RARITY_ODDS` registration document live?**
   (§5 row 10.7(a).) Greps over `docs/`, `review/` and all branches found
   nothing; the document may not be in the repo.
4. **Does the S13 pin corpus need re-verification** before any family is
   treated as a game fact? (§6 item 4.)
