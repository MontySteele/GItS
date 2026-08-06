# The [USER] queue — single source of truth

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

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

> **UPDATED 2026-08-06 (docs diet, Track Z / Z-3).** The five registers listed
> above are now **REFERENCE**: frozen in place, nothing deleted, every word
> still readable at its own path. Their still-open rows were migrated — the
> ones needing [USER] into **§10** of this file, the ones needing only
> engineering into **`docs/dockets/engineering-backlog.md`**. From here on an
> open item lives in exactly two places, **this file or a docket**, and
> `tools/lint_identifier_registry.py` RULE 3 fails a new document that mints
> one anywhere else. The rule and its escape hatches:
> `docs/registry/identifiers.md` §16.

> **HOW TO READ A ROW, 2026-08-06 (docs diet, Track Z / Z-5).** Every open row
> now opens with **one plain sentence saying what is being asked**, and where it
> is not obvious, a second saying why it matters. The identifiers (`S4-G6`,
> `NC-7`, `AB-s2`…) come *after* that sentence, never instead of it: they are
> the keys you hand the resolver at `docs/registry/identifiers.md`, not the
> meaning. **A row you have to open another file to understand is a defect in
> the row** — that lesson is `AC-6`'s, and it is why this pass happened.
>
> Nothing about *what is asked* was changed by that pass — only how it reads.
> Verbatim [USER] verdicts stay verbatim and are quoted, never paraphrased.

**Standing discipline this file obeys.** HELD flags are copied in as held
(FLAG-1…FLAG-4). ~~The R102 escrow stays frozen.~~ Awaited one-liners are recorded
as awaited; recording is not answering.

> **UPDATED 2026-08-06 (Cold Reading, R113–R116).** The R102 escrow is
> **released** (R113) and all four HELD flags are **ruled** (R114), so this
> file's two standing postures above have both been discharged by [USER] rather
> than by a track. Struck rather than rewritten, per R101b. What is still held
> is listed as held; §1 and §3 say which.

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
| Q5 | ~~**`NT-G5` fork evaluation — NEW, opened 2026-08-06 by Q1's YES.** Did Neap Tide (Kokomi) **read weak at the table** during the 2026-08-01/02 playtest?~~ **REWRITTEN 2026-08-06 (`AC-1` REVISED, R115): the playtest could not answer this, because the card was never played.** Verbatim: *"I don't remember seeing the card during the playtest, so it did not stand out one way or another."* So the remaining ask is **not** the evaluation — it is **where the evaluation should happen.** Plainly: do we (default) put an explicit "draw and play Neap Tide, then say whether she felt weak" task on the next Kokomi playtest, or (candidate) fold the whole question into the queued Kokomi pool-rework session instead? | PLAYTEST / POOL-REWORK | **The default is already in place and costs nothing to confirm:** observation task `OT-1` is written into `docs/kokomi-playtest-protocol.md` with its own Answers row, and the fork is re-anchored to the next Kokomi playtest. **POOL-REWORK** moves it to the rework session instead — a real option, recorded so the choice is visible rather than defaulted into. Either way **no lever moves**, `S4-G13`'s fork half stays open, and the fine-branch's exhaust-loop calibration offset stays unwritten and owed by whichever venue evaluates | `klee-mod/DECISIONS.md`, "PRE-REGISTERED FORK for playtest three (G5, confirmed)" + its two 2026-08-06 [USER] annotations (the first struck, the second operative); `docs/kokomi-playtest-protocol.md` `OT-1` |
| Q6 | **The X6 exploit line can no longer be run — repair it, or retire it? NEW, opened 2026-08-06 as a consequence of `Q4`.** Plainly: one of the recorded exploit recipes drafts an *upgraded* Encore Performance, and that upgrade no longer exists, so the replay harness cannot build the deck and the test now skips instead of running | REPAIR / RETIRE / LEAVE | `tier0/tests/test_s13_exploit_pins.py::test_x6_salon_displacement_is_priced` went **xfail → SKIP**. The skip is the harness saying "I could not execute", never "this is fixed" — the X6 mechanism (Salon FIFO displacement paying free final bows) is untouched and is still R111's WATCH ITEM. **REPAIR** = drop the `+` from the line's `upgraded` set and re-verify at the card's now-printed 0 cost; **RETIRE** = keep the line as the record of a recipe a ratified change made unbuildable; **LEAVE** = accept a permanently skipping pin. Editing a verified exploit corpus is an instrument decision, so Track Y took none of the three | `review/redteam/exploit-lines.json`, line `furina_salon_3_gala_bow_storm`; the pin's own docstring carries the full note |
| Q7 | **Close six of the seven axis scorecards permanently as "numbers are informational only"?** Keep only the Fanfare axis, which the Furina work already depends on. Plainly: six of the seven axes have never decided anything and are already marked non-binding; this makes that permanent and shrinks the gate to the one question people are actually waiting on. *(Still AWAITING as of 2026-08-06 — `AC-3` had no reply; wording verified against the sitting's own plain-language form and left unchanged.)* | YES / NO | **`S4-G5`/`B-G1` narrowed.** YES closes six axes forever (no number retired or deleted — they stay publishable as description and may never be an acceptance target) and re-points the `R107/F1` fence to the narrowed gate, which unfences Furina backlog items 1–3 and the fanfare STOP from six questions they do not depend on. NO leaves all seven open and the Furina work waits on them. **Full landing text drafted in both forms** | `docs/awaiting-user-slots-2026-08-06.md` **slot 4** (Y-9(a)) |
| ~~Q8~~ | ~~**Re-anchor Kokomi's stability band and her protocol playtest to the post-rework build?**~~ | ~~YES / NO~~ | **ANSWERED 2026-08-06 — YES** (Track AC / `AC-2`, R115): *"deferral APPROVED — land staged slot (b): stability band + protocol playtest re-anchor to the post-rework Kokomi build; declare-before-playtest law intact."* Slot 5's YES form landed verbatim at `DEC-D5` (annotation beneath clause 4), the protocol's header, and this file. **"Deferral APPROVED" approved the re-anchor, not a postponement of the band:** no band was declared, nothing was graded, `DEC-D5` clauses 2–4 are intact, and neither gate is discharged | ~~`docs/awaiting-user-slots-2026-08-06.md` **slot 5**~~ → landed; slot marked ANSWERED |

| Q9 | **Should the shipped game stop letting Encore Performance copy a kit card? NEW, opened 2026-08-06 by `AB-s1`.** Plainly: Furina's Encore Performance copies a card. The design sheet says it must never copy a *kit* card — the big signature cards a character starts with — and the simulation obeys that. The shipped mod does not, so in a real game you can end up holding a copied kit Burst that cannot be discarded and occupies a hand slot for the rest of the fight | YES / NO | **Sheet-vs-mod parity, fixed on the mod side.** YES makes the game match the sheet and the sim. NO makes the mod canonical, which means the *sheet and sim* are the defect and get repaired instead. Staged rather than landed because it is a **mod behaviour change**, and those are blessed explicitly, never inferred from a parity table. Blast radius either way: one card's copy pool, no sim number, no test flip. **Full landing text drafted in both forms** | `docs/awaiting-user-slots-2026-08-06.md` **slot 6**; R114 (FLAG-2); NC-12 |
| Q10 | **How should the never-flushed curse stop jamming the hand? NEW, opened 2026-08-06 by `AB-s2`.** Plainly: `curse_poor_sleep` is marked two ways at once — it is a **status** (so it can never be played) and it is **retained** (so it is never discarded). A card that can neither be played nor discarded sits in your hand forever. Ten copies fill the hand, every draw bounces, and the fight cannot proceed | ALPHA / BETA (or NEITHER) | **The fallback you described is already shipped** (`S-3`, the spotlight path, R110 leg (b)) and does not reach this: **the jam is the typing, not the spotlight.** **ALPHA** = drop `retain` from that one curse — a data repair; any future card typed the same way reproduces the jam. **BETA** = a law: status-typed cards always flush at end of turn, engine-wide, `status` beats `retain` wherever they collide — fixes this curse as a consequence and every future instance in advance. **NEITHER** is also an answer and is drafted, with its cost stated. **Full landing text drafted in all three forms** | `docs/awaiting-user-slots-2026-08-06.md` **slot 7**; R114 (FLAG-4 leg (a)); `S13-X14` |

| Q11 | **Countersign a ten-minute scripted probe that settles the corpse-detonation question, instead of waiting for it to happen at a table? NEW, opened 2026-08-06 by `AC-4`.** Plainly: we have never answered whether killing a bombed enemy sets its bombs off early. The settlement was written as a ten-second eyes-on check and has survived five playtests unanswered, because nobody has happened to be holding the right relic on the right turn. A scripted fight can arrange that state on demand | COUNTERSIGN / DECLINE | **Why it matters:** the sim detonates unconditionally, so if the game suppresses on death, **every sim bomb-damage number taken against a killable enemy overcounts on the killing-blow turn** — low probability, broad blast radius. The registration is written in full (question, two independent tells, a negative-control arm, nine confounders, a cost ceiling and a stop-and-re-register tripwire) and **nothing has been run**: a new probe is a pre-registered question under standing law, so it is paper until signed. **DECLINE costs nothing structural** — the table item survives as fallback and closes the question whenever somebody is holding Pounding Surprise on the right turn | `docs/probe-e-corpse-detonation-registration-draft.md`; `klee-mod/DECISIONS.md` "Corpse detonation — OPEN"; `S4-G15` |
| ~~Q12~~ | ~~**Errata Batch 2 — PENDING WORK, not an ask.** Eight ratified fixes are queued and none has been written.~~ | *(no reply needed)* | **WRITTEN 2026-08-06** (`db3318e`): seven of the eight landed in full and the eighth stopped half-done on purpose. Contents, in order: (1) term-3 fanfare credit, sim; (2) `NC-8` potions consumed, sim; (3) `NC-1` companion-power damage through the pipeline, mod; (4) `NC-11` power-sourced block raw, mod; (5) `NC-7` Frozen unified, both — **the sim half landed, the mod half STOPPED, see `Q13`**; (6) `NC-10` shop slot spec, both; (7) `FLAG-1` accumulator turn-scoped, both; (8) `FLAG-2` (i)/(ii). Parity vectors, all lints and the S13 characterization ran after; the corpus did not move. **Two questions the batch deliberately left open rather than answering silently are now their own rows: `Q13` and `Q14`** | R113 (item 1), R114 (items 7–8), R116 (items 2–6 + the batch table); `db3318e` |
| Q13 | **Which enemies should a Frozen boss-substitution treat as "not the boss"? NEW, opened 2026-08-06 by Errata Batch 2.** Plainly: the ruling said Frozen should be swapped for Vulnerable on bosses **per creature**, so a boss's *helpers* can still be frozen. The simulation knows which creature is the boss because we authored that fact ourselves. **The shipped game keeps no such fact**, so the mod half of the fix stopped rather than guess. Two readings are available and they disagree about the ruling's own example | ALPHA / BETA | **(α) minions only** — a boss-room creature carrying the game's `MinionPower` gets Frozen, everything else gets Vulnerable. Mechanical, uses the only per-creature "secondary enemy" concept in the assembly, and **does not** make Kaiser Crab's second claw freezable — so it contradicts the consequence R116 stated. **(β) a named non-boss roster** — mirror the sim's own `is_boss` data as a monster-id list; matches R116's example exactly, and is new authored content data covering every base-game boss room. Verified by reflection over `sts2.dll`: `MonsterModel`, `Creature` and `EncounterModel` carry no boss/rank/tier member. Surfaced, not chosen — picking one is a design call the ruling did not make | `review/parity-sweep/noncard-triage-memo.md` `NC-7`, the 2026-08-06 EXECUTION NOTE; R116 |
| Q14 | **Does the world stamp go up? NEW, opened 2026-08-06 by Errata Batch 2.** Plainly: the batch changed how Frozen works in the simulator, and Frozen appears in a lot of fights — so every combat number measured before the batch was measured under different rules. House precedent is that a change of this class gets a version stamp, which marks the older numbers as archive rather than rewriting them. The batch **recommended the stamp and declined to take it**, because bumping a world stamp is [USER]'s call | YES / NO | **YES** = `CONSTANTS_VERSION` 5 → 6, and every published number below the stamp gets an archive banner where it is published — nothing is rewritten (R101b). **NO** = the pre-batch numbers stay quotable as-is, and the reason is recorded. **`NC-10` rides the same row:** the shop-slot spec changed tier-0.5 shop maths in both engines, so whether the pre-batch shop numbers stay comparable is the same question asked about a second surface. **A third, smaller question rides with it and is not answered by either word:** `NC-10`'s rarity-odds renormalization inside the new Uncommon-or-higher pool — condition the existing `SHOP_COMPANION_RARITY_ODDS` on ≥Uncommon, or state a fresh split. Surfaced, not chosen | `review/parity-sweep/noncard-triage-memo.md` `NC-7`/`NC-10`; R116; `db3318e` |
| Q15 | **Should the citation lint also cover the tool that still carries the same wrong citation? NEW, opened 2026-08-06 as a consequence of `Q3`.** Plainly: four documents cited a ruling that did not say what they claimed; those four were repaired and a lint now stops it happening again. The same wrong citation is still live in one **tool**, three times over, and the merge deliberately did not widen the lint to reach it — widening a lint's scope is a decision, not a repair | WIDEN / REPAIR-ONLY / LEAVE | **WIDEN** = the citation lint sweeps `tools/*.py` as well as documents, and the three occurrences in `tools/lint_role_tempo_coverage.py` are repaired to satisfy it. **REPAIR-ONLY** = fix the three occurrences and leave the lint's scope where it is. **LEAVE** = the tool keeps the misattribution, which is the only option that leaves a false statement in a live artifact. Blast radius: comments and docstrings; no behaviour, no number, no test | `Q3` above (Track Y / Y-3); `tools/lint_role_tempo_coverage.py` (3 occurrences) |

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
| `S4-G1` | R88 countersign — Zhongli slot 4 / Itto eligibility | `tier0/DECISIONS.md` R88 | **DISCHARGED by R108** (2026-08-06). **Itto half now ruled outright (Track Y / Y-5, 2026-08-06):** *"Itto enters as a COMPANION CARD, not a character."* — R108 gained a dated addendum clause; cross-noted in `docs/slot5-candidates-2026-08-05.md` §2.3/§2.5 and `docs/inazuma-companions.yaml`. No card drafted. Rider still open: §5 row 10.8 (the R88-vs-R52 conflict *in general*; it is no longer load-bearing for Itto). |
| ~~`S4-G2`~~ | ~~R89 countersign — Furina legibility sprint record~~ | `tier0/DECISIONS.md` R89 (~~DRAFT~~ **SIGNED**) | **DISCHARGED 2026-08-06** (Track Y / Y-6): R89 **SIGNED as an audit-trail reconstruction of the shipped 07-24 sprint**. Nothing was decided by the signature — the sprint shipped and deployed on 2026-07-24; only its record was missing. DRAFT banner dropped with a dated banner, not silently |
| ~~`S4-G3`~~ | ~~Principles **v1.12** ratification (Fanfare single-leg + printed cap/grant X values)~~ | `docs/teyvat-spire-design-principles.md`, the amendment section (no longer headed "DRAFTS") | **DISCHARGED 2026-08-06** (Track Y / Y-7): **RATIFIED**, banner dropped with a dated banner. Verified against shipped code first — four live generation legs in `tier0/constants.py`, `FANFARE_PER_ENCORE_GAINED` and `FANFARE_FLOOR_PER_POWER`/`_RARE` absent from both engines, printed keywords enforced by R6. **Ratifying the text did NOT ratify the X values** — those stay PROPOSED in `S4-G9`, and the 1.8% fanfare STOP is untouched |
| ~~`S4-G4`~~ | ~~Principles **v1.13** ratification (bounded runtime art fitting)~~ | same section | **DISCHARGED 2026-08-06** (Track Y / Y-7): **RATIFIED**, banner dropped the same recorded way. Verified: `SalonVisualsBridge.cs` declares `SpriteScaleMax = 0.5f` and takes `Mathf.Min(SpriteScaleMax, spacing / width)` — bound written down and answering to the pitch, which is the amendment's own condition — with all three facts asserted in `tier0/tests/test_visual_contract_gaps.py` |
| `S4-G5` | **Say, axis by axis, what the seven scorecard numbers are allowed to do.** They describe today and decide nothing; this makes that permanent or ends it. **`B-G1`** — per-axis disposition of the seven-axis scorecard; carries the re-registered Fanfare P1 | `docs/axis-validity-session-charter.md` §4/§7; R90/1b | OPEN. Until it rules, axis numbers stay *"reportable, not load-bearing"* (`DEC-D3` clause 3). **Now also the governing condition on §3's Furina items 1–3 and the fanfare STOP** (R107/F1). **A narrowing disposition is STAGED, not landed (Track Y / Y-9a): see `Q7`** — close six axes permanently, keep the Fanfare axis, re-point the R107/F1 fence to the narrowed form. |
| `S4-G6` | **Write down, before her playtest, how steady Kokomi's HP is supposed to be.** It has to be declared from what she is *meant* to do, because a band chosen after the fact grades nothing. **Kokomi stability-band declaration** — from design intent, before the confirmatory playtest; may not be revised against it | `tier0/DECISIONS.md` `DEC-D5` clauses 2–4; backlog §3 item 5 | OPEN — gates grading her protocol playtest. ~~A re-anchor to the post-rework build is STAGED, not landed (Track Y / Y-9b): see `Q8`~~ **RE-ANCHORED 2026-08-06** (`AC-2` / R115): the confirmatory playtest is the protocol run against the **post-rework** build; 08-01/02 and playtest 4 are EXPLORATORY. **The gate is NOT discharged** — no band is declared, and `DEC-D5` clauses 2–4 survive intact |
| `S4-G7` | **Three Furina decisions that every other Furina number waits on:** how strong her hidden Power bonus should be and whether to print it, whether she gets three viable plans or one, and what to do about her strongest plan running above its anchor. Furina items 1–3 (strength lever + legibility; dead-archetype; salon leak) | backlog §3 items 1–3 | OPEN. **Re-fenced 2026-08-06** — was "mis-fenced"; R107/F1 re-pointed the condition to `B-G1`. |
| `S4-G8` | DRAFTER 13 repricing ledger entry / number ratification | `docs/sprint-sim-hygiene-log-2026-07-29.md` | **DISCHARGED by R107(a)** (2026-08-06) |
| `S4-G9` | **One sitting that turns about fourteen proposed numbers and small design calls into ratified ones.** None is big; together they are the reason a lot of shipped content is still marked PROPOSED. The ratification batch — ~14 sub-items (fanfare-rework X values; conversion clauses; `lasting_impression`; negative-floor semantics; D6 bow space; `kurages_oath`=12 re-file; pulse 2-vs-3; Curtain Call's four follow-ons; `scattering_spray` 7→6; Spotlight ten-icons-vs-family; Klee dead-card reworks) | backlog §3 item 9 | OPEN |
| `S4-G10` | **Close out the companion shop: grade what it did, and settle whether money is ever actually the constraint.** Runs end with roughly 220 unspent gold, which decides whether "pricing is the balance governor" can be true at all. Shop channel §7 close-out — `SHOP-P1…P3` grading; does the purse ever bind; the 1.15× surcharge; Track A pool migration; **R60 phase-2 fantasy-leak grading** | R60/R63; principles §4.7 notes 2–3 | OPEN — R60's stated trigger has been satisfied since 2026-07-25 |
| `S4-G11` | **Read the card names and lore text with your own eyes before they ship.** Ruled as having no substitute; also covers Kokomi's twenty authored-but-unaudited fill cards. **R29d** naming/lore eyes-on pass (Furina); plus Kokomi R58 fill block AUTHORED-NOT-AUDITED and kickoff ask 10 | `tier0/DECISIONS.md` entry 75 + R29d banner; R58 | OPEN |
| `S4-G12` | **Look at the art, and look at the cards in the running game.** Two eyes-on reviews whose materials are already prepared. = **`CC-G1` + `CC-G2`** (R86): contact-sheet eyes-on (four REHUNT picks + `standing_room_only` overturn) and in-game screenshot review of the twelve Curtain Call cards + the A0 smoke run | `tier0/DECISIONS.md` R86 | OPEN — **materials ready**: `docs/g12-review-2026-08-05.md` (contact sheets verified, all 24 captures). See also §5 row 10.1: five of nineteen art candidates fail lint if picked. |
| `S4-G13` | **Kokomi measures below the floor the roster is anchored to, and the three ways to fix that are all yours to pick.** Code may build any of them and may choose none. Neap Tide standing question — Kokomi below the Ironclad-anchored floor; three levers, *"none is Code's to pull"*; plus the `NT-G5` fork | `klee-mod/DECISIONS.md` E2/E2b + addendum | OPEN. ~~the fork half turns on **Q1**~~ **Updated 2026-08-06:** Q1 answered YES, so the fork has **fired** and its half of this gate is now the scheduled sitting item **Q5** (weak-or-fine). The standing question itself is unchanged |
| `S4-G14` | **Play Kokomi once, deliberately, against a written list of questions.** Everything she has had so far was exploratory and cannot be graded. Kokomi protocol playtest (Q1–Q7 + three priority checks; Answers blank) | `docs/kokomi-playtest-protocol.md` | OPEN — blocked on `S4-G6`, and (per backlog §4) on the N1 attribution pass. ~~Re-anchor STAGED with `S4-G6`: see `Q8`~~ **RE-ANCHORED 2026-08-06** (`AC-2` / R115) to the post-rework build; content unchanged, blockers unchanged. **Gained one item:** observation task `OT-1` — Neap Tide deliberately drawn, played and reported (`AC-1` / R115) |
| `S4-G15` | **Find out whether killing a bombed enemy sets its bombs off.** Ten seconds of looking; if the answer is no, every simulated bomb number taken against a killable enemy is too high on the killing-blow turn. **Corpse detonation settlement** — ~10 s at the table; failure invalidates every sim bomb number vs killable enemies | `klee-mod/DECISIONS.md` "Corpse detonation — OPEN"; `docs/probe-e-corpse-detonation-registration-draft.md` | OPEN since 2026-07-21, through ≥5 playtests (*nobody checked in playtest 4*). **Instrument change STAGED 2026-08-06** (`AC-4` / R115): a bridge-driven scripted probe is registered and **awaits countersign — see `Q11`**. The table item **survives as FALLBACK ONLY** and is not retired |
| `S4-G16` | **One screenshot: a Power being played and the Fanfare floor going up because of it.** The last of four evidence shapes; three are captured. **`G-A5(b)`** fourth shape — one capture of a Power play raising the Fanfare floor | `docs/red-pen-2026-07-26.md` Part 3 | OPEN |
| `S4-G17` | **Four things that can only be judged by looking at the running game**, none of which needs a full playtest. **Table looks** — `AS2-D5` salon capture (now unblocked by the sprite-scale fix); `AS2-B5` motion pass + facing taste; `AS2-E2` icon picks (4 REHUNT); hover-targets question | `docs/open-playtest-items.md` §3; backlog §4/§5 | OPEN, urgency reduced: hover-targets **CLOSED at playtest 4**; B5 "not noticed" |
| `S4-G18` | **Klee's three archetypes carry more cards each than the design constitution allows, and nobody has either fixed it or amended the rule.** Klee pass-4 **ask A3** — 28/21/14 archetype-band deviation vs principles' 15–20, never amended or accepted | `docs/missed-requirements.md` Tier 5 | OPEN (ask A5 is *deliberately* deferred by `DEC-D3` — distinct) |
| `S4-G19` | **Two mechanics in the game do nearly the same thing; say whether they become one.** **Sly unification** design ruling — two mechanics, one word | `docs/tech-debt-audit-2026-07-26.md` §5 | OPEN |
| `S4-G20` | **A bundle of small leftovers: one card-text-vs-intent ruling, one divergence to accept or fix, three taste passes, and two pieces of repo infrastructure only you can turn on.** Standing Ovation boost expiry; sim-vs-C# salon RNG divergence acceptance; taste passes (Kokomi 58 faces + 15 companions, L12 duplicate pairs, `kaboom == spark_knight_style`); infra (branch protection / `gh`); manifest MAJOR bump (R70, dormant by design) | backlog §1 P3-cluster + §5 | OPEN |

---

## 3. Held flags — ~~not to be built against~~ **ALL FOUR RULED 2026-08-06 (R114)**

~~Four clarifications carried out of the sitting of 2026-08-06 **unresolved**.~~
`docs/dockets/README.md` house rule 3: nothing may be built against a held flag.
Full questions: `docs/registry/identifiers.md` §6, and R110/R111 verbatim.

> **DISCHARGED 2026-08-06 (Cold Reading, Track AB / R114).** This section is
> kept, struck rather than deleted, because the flags are part of the record of
> how these families were decided. **Nothing here is held any more.** Two
> *new* questions were raised by the answers and are open — `AB-s1` and
> `AB-s2`, rows `Q9` and `Q10` of §1 — and they are not these flags.

| Flag | Family | One-line | Ruling |
|---|---|---|---|
| ~~FLAG-1~~ | `S13-X1` | ~~The accumulator's second enabler (Kokomi `honor_guard`) / a structural disposition for the shared uncapped state~~ | **RATIFIED CHANGE** — *"Limit the cost discount to the current turn? Yes."* Scoped to the writing turn, both engines; the engine-wide fix closes both enablers at once. Errata Batch 2 item 7 |
| ~~FLAG-2~~ | `S13-X3` | ~~Two adjacent closures: copy-outruns-Exhaust (design call) and unscoped `cost_override` (reads as a straight bug)~~ | **BOTH FIXES RATIFIED** — *"Yes."* (i) copies inherit printed bounds; (ii) `cost_override` = "this turn" (sim-only; C# is already correct). Errata Batch 2 item 8. Residue staged as `AB-s1` |
| ~~FLAG-3~~ | `S13-X5` | ~~Does "seems fine" cover decay-proof fanfare-floor stacking, or only the cantrip leg?~~ | **INTENDED, both legs** — the floor is a deliberate strength-style scaling effect. X5 closes; watch item `W4` takes the power level; the X5 pin converted from xfail to a documented-behaviour test |
| ~~FLAG-4~~ | `S13-X14` | ~~Legs (a) `curse_poor_sleep` retain-jam and (c) all-Power deck self-erasure~~ | **(c) RULED INTENDED** — *"You deck out... don't do that."* No guard; documented in `refpowers.result_pile`. **(a) clarified, root staged as `AB-s2`** — the jam is the typing, not the spotlight |

---

## 4. Sittings owed on landed review artifacts

| Item | What is asked | Unblocks | Full text |
|---|---|---|---|
| ~~**R102 escrow release**~~ | ~~Strike the four PROVISIONAL fanfare marks as instrument-vindicated, **or** formally re-open any of them.~~ | **ANSWERED 2026-08-06 — SIGNED, STRUCK** (Track AA / R113): *"agreed - signed."* All four marks struck; the grades stand exactly as ratified and no number moved. Companion clauses C-a…C-d landed: term 3 (+2 Fanfare per combat, tier0-optimistic) filed to `docs/s7-classification.md` as bounded/direction-known with its fix **queued** as Errata Batch 2 item 1; the blind-replay column re-read rule stated once; S13 re-verification **NO** with the Family-A grep null attached; the probes' standing limits carried onto every struck banner | ~~`tier0/DECISIONS.md` R102~~ → `tier0/DECISIONS.md` **R113** |
| ~~**S2 event-gallery checkboxes**~~ | ~~Curation sitting: 47 events, 141 drafted variants → 130 kept / 11 cut, 4 demotions~~ | **RECLASSIFIED 2026-08-06 — INSPIRATION-OPTIONAL** (`AC-5` / R115). Leaves the active-ask section; joins the Ancients and boss-pool galleries below. **Nothing is blocked on it** — the event layer's conversion pass no longer waits on a checkbox sitting. Nothing was cut, kept or demoted by the reclassification, and the gallery is not retired. Rider: `NC-15`'s Brain Leech mismatch is the same event, so answering either answers both | `review/event-gallery/gallery.md` |
| ~~**S14 canonicity rulings**~~ | ~~Four named questions: **NC-1**, **shop slot 1** (`NC-10`), **Frozen** (`NC-7`), **`spend_potion`** (`NC-8`)~~ | **ALL FIVE RULED 2026-08-06 (R116).** `NC-1` sim canonical (companions scale with the player); `NC-7` each engine adopts the other's half (sim takes the timer, mod takes per-creature); `NC-10` both engines defective against a stated slot spec; `NC-8` ruled by inclusion in the batch (potions are consumed); and `NC-11` — minted new by the fourth sitting, ruled by the dispatch — power-sourced block stays **raw**, sim canonical. **Five of the memo's questions closed; all five fixes are Errata Batch 2 items and none is written.** The rest of the 174-finding triage (the lint candidates, the LOW cluster, `NC-18`, `NC-19`) is untouched and still owed | `review/parity-sweep/noncard-triage-memo.md`; R116 |
| **S13 residual sitting items** | ~~The four HELD flags above;~~ **all four RULED 2026-08-06 (R114).** ~~plus paperwork one-liner 4 in §6~~ **answered 2026-08-06 (R113/C-c): no re-verification.** Two *new* staged questions replaced the flags — `AB-s1` and `AB-s2`, rows `Q9`/`Q10` | Treating any exploit family as a game fact | `review/redteam/exploit-ledger.md`; R113, R114 |
| **N and O TOP-5 reviews** | **Read the top five findings of two audits — one about whether the game's lore is faithful, one about whether our own instruments are honest.** Both are ordered worst-first, so the top five is most of the value. Read the two severity-ordered ledgers top-5-first. Includes **N-1** (routed by R112) and the standing caveat that the reactions corpus is PROVISIONAL until ruled | The lore-repair and instrument-repair queues | `docs/lore-fidelity-audit-2026-08-05.md`, `docs/instrument-redteam-2026-08-05.md`; `docs/sitting-prep-2026-08-05.md` §10.14 |
| **S8's 8 flagged items** and **S10's reskin candidates** | **Two galleries of proposals waiting on taste:** eight flagged potions/relics, and a list of enemies that could be reskinned rather than redesigned. Candidates, not verdicts. RESKIN/REDESIGN remains [USER]'s call per north-star | content conversion | `review/potion-relic-gallery/gallery.md`, `review/enemy-atlas/reskin-gallery.md` |
| **Ancients + boss-pool galleries — and, since 2026-08-06, the S2 event gallery** | *Inspiration-optional — no review obligation.* Curated best-first, checkbox per entity | nothing is blocked on these | `review/ancients-gallery/gallery.md`, `review/boss-pool-gallery/gallery.md`, `review/event-gallery/gallery.md` (joined 2026-08-06 by `AC-5` / R115) |
| **X10 pricing** (`gorou_heart_of_the_clan`) | **One companion card looks underpriced for what it does; a proposal exists to move it up a rarity and adjust its power, and nobody has priced it.** A **CANDIDATE, explicitly not ratified**: Uncommon promotion + power adjustment, priced at a sitting | the companion-pricing docket's §1 | `docs/dockets/companion-pricing.md` §1 |
| **R1–R38 resolvability** *(surfaced by this sweep)* | **The project's first thirty-eight rulings cannot be looked up.** Several are cited as standing law but exist only inside prose and archived documents, with no index from the number to a dated entry. The ask is whether building that index is worth it. Early R-numbers exist only inside prose entries and archived ruling docs; several (R8, R13, R14, R24, R25, R29d) are cited as standing law and no index maps them to a dated entry. Is a back-index worth building, or are they historical? | Any citation audit of pre-R39 law | S4 §4 lead 3; `docs/registry/identifiers.md` §3 |

---

## 5. The Last Call batch's own asks (sitting-prep §10)

Each is a yes/no or a pick-one. Full text: `docs/sitting-prep-2026-08-05.md` §10.
None was ruled at the 2026-08-06 sitting except where noted.

| # | Ask | Shape |
|---|---|---|
| 10.1 | **Five of the nineteen art candidates would fail the art lint if you pick them.** Pick a way forward. `S4-G12` changed shape: five of nineteen art candidates fail `art_lint` if picked; `standing_room_only`'s recommended r3 fails `ART-L1` | pick one of four |
| 10.2 | **Name the table of numbers that everything is now quoted against, or say we keep quoting the old one.** Roster-anchor **v14** table (`RA-G1`): designate the quotable successor to the D13 n=3000 standing table, or hold. Rider: should `ref_ironclad`'s `archetype_package` carry `Card.archetypes` tags? | yes/no + a design-shaped rider |
| 10.3 | **One definitional call about a Furina mechanic, affecting exactly one card.** Spotlight limb definition — extend payoff-presence to the spotlight limb? Blast radius: exactly one card (`limelight`) | yes/no |
| 10.4 | **A name in a tool reads as if something is unmodelled when it is not. Keep it or rename it.** `unmodelled_starting_relics` spelling in `tools/patch_sentinel.py` — keep it? | yes/no |
| 10.5 | **Two files with almost the same name both exist and both work; say which one the acceptance clause meant.** Which module did `UND-P1.5`'s acceptance clause mean? Both `understudy/replay.py` and `understudy/trace_replay.py` exist and are complementary | confirm/correct |
| 10.6 | **A crash we assumed was ours may be the base game's. Confirm the reclassification.** Punch Off reclassification: SUSPECTED-OURS → game-side. Note either way: the crash log has rotated out | yes/no |
| 10.7 | **A rule is fenced by a registration document that cannot be found in the repo.** Authorise a search-and-repair, and decide whether to quarantine the two columns that depend on it meanwhile. Payoff-reach fence adjacency: (a) where does the payoff-reach/`RARITY_ODDS` registration document live — it could not be found in the repo; (b) quarantine `RA-G1`/`RA-G2` core-attainment columns until (a) is answered? | two asks |
| 10.8 | **A signed ruling contradicts an older ratified one about who may be a character rather than a companion.** The Itto half is settled; the general conflict is not. **R88's draft conflicts with ratified R52 and shipped content** — the reserved-character rule vs Neuvillette. **Read before signing.** R108 countersigned the slot; this conflict is not thereby resolved | pick one of four |
| 10.9 | **A ruling cites evidence that does not exist. The ruling is fine; the citation is not.** Authorise fixing the citation later. §2.2a's stated evidence does not exist (the act-3 Ancient stun reward). Authorize a later citation repair? Rule untouched either way | yes/no |
| 10.10 | **No ask — just a heads-up that one appendix's premise expired when a card shipped.** Columbina has shipped; Appendix A.6's premise expired | awareness only, no ask |
| ~~10.11~~ | ~~**The C2 escrow is now rulable** — see §4, R102 escrow release~~ | **RULED 2026-08-06 — STRUCK** (R113). *"agreed - signed."* |
| ~~10.12~~ | ~~Family-A dependency hits in the S13 ledger: **none found**. Accept the null as closing the C-c order, or order a wider derivation test?~~ | **RULED 2026-08-06 — null ACCEPTED** (R113 clause C-c). No wider derivation test is ordered; the null is attached to the ruling as its evidence |
| 10.13 | **A written, unrun experiment is waiting for your signature.** Under standing law a new probe is a pre-registered question, so it stays paper until signed. **Probe (d) registration** — `docs/probe-d-registration-draft.md`, drafted and unsigned; nothing has been run | countersign yes/no |
| 10.14 | N + O ledgers, read top-5-first — see §4 | read |

---

## 6. Paperwork one-liners (the four the merge train carried)

Four corrections that need a yes/no and nothing else; each leaves a false or
ambiguous statement in a live artifact if declined. Full text:
`docs/sitting-prep-2026-08-05.md` §8. Restated as still-open by R112.

1. **S15 pin-table sum mismatch** — headline 111 vs a counted 133 test functions; the per-module table lists 0 for four files that carry tests. Authorise correcting the table and headline, or leave.
2. **S8 header 42-vs-51 miscount** — one preamble line in `review/potion-relic-gallery/gallery.md`. Authorise correcting to 51, or leave.
3. **`review/enemy-dossiers` stale branch pointer** — points at `e07fb4c`; the content landed via `ec15028` + `28759f0`. Delete / repoint / leave.
4. ~~**S13 re-verification against `S7-C1`/`S7-C2`** — re-verify all 71 lines, only the block- and fanfare-dependent families, or proceed on the caveat as written.~~ **ANSWERED 2026-08-06 — proceed on the caveat as written** (R113 clause C-c: re-verification **NO**, with the Family-A dependency null attached as evidence). Both C1 and C2 have since been reclassified away from tier0 infidelity anyway — C1 is family B, C2 is written off — so the caveat's premise has weakened in the direction that made re-verification cheapest to decline.

---

## 7. Table time (not desk work)

| Item | Note |
|---|---|
| **Kokomi protocol playtest** (`S4-G14`) | Q1–Q7 + three priority checks. Blocked on `S4-G6` and the N1 attribution pass. PARTIAL at playtest 4: priority check 3 closed; Q1/Q4 "unjudgeable — the pulse has no visual"; Q6 a second-hand soft flag. **Re-anchored 2026-08-06 to the post-rework build, and gained observation task `OT-1`** — draw and play Neap Tide deliberately, then say weak or fine. That row is the `NT-G5` fork's only accepted input |
| **Corpse detonation** (`S4-G15`) | ~10 s. Nobody checked in playtest 4; now sequenced behind the N1 attribution pass. **A scripted probe is staged to replace the waiting** — see `Q11`; this table item survives as **fallback only** |
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
4. ~~**Does the S13 pin corpus need re-verification** before any family is
   treated as a game fact? (§6 item 4.)~~ **SUPPLIED 2026-08-06 (R113/C-c):
   NO.** The caveat stands as written and no line is re-run.

---

## 10. Migrated here 2026-08-06 by the docs diet (Track Z)

Five documents used to carry open [USER] items of their own:
`docs/backlog-2026-07-29.md`, `docs/open-playtest-items.md`,
`docs/missed-requirements.md`, `docs/sitting-prep-2026-08-05.md` and
`docs/surplus-week-manifest-2026-08-05.md`. All five are now **REFERENCE** —
frozen in place, nothing deleted, every word still readable at its own path —
and the rows below are the ones that were still open and had **no row anywhere
in this file**. Each is quoted in its source document's own words, with the
citation that carries the full text and the evidence.

The engineering half of the same migration — work that needs no [USER] ruling
to start — went to `docs/dockets/engineering-backlog.md` instead. Nothing was
dropped; §8 of that docket lists every row that did *not* come across and names
what discharged it.

| # | Ask, plainly | Shape | The row as its source wrote it | Full text |
|---|---|---|---|---|
| `M1` | **Furina's charter promises a co-op mechanic that was never built. Build it, or write down that we are not building it.** Two halves: partner damage and Encore swings feeding Furina's Fanfare meter, and the audit that stops Klee farming Fanfare by hurting herself. It was deferred to a "Tier 2" that does not exist; co-op has since shipped and been played, so the deferral condition has lapsed | BUILD / WAIVE | *"`furina-kickoff-v0.1.md` §4 declares partner HP/Encore flux counting toward Fanfare as 'the first ally-coupled mechanic', with a mandatory audit: 'exclude or discount self-inflicted partner damage (Klee's Hot Hands) or Fanfare farms itself.' … deferred to 'Tier 2' … **There is no Tier 2**"* | `docs/missed-requirements.md` §1.1; brief `docs/brief-coop-charter-items.md`; backlog §3 item 8 |
| `M2` | **Same question, second mechanic: can co-op players pass a Spotlight to each other?** Declared in Furina's charter, deferred with "solo path first", and the solo path shipped long ago | BUILD / WAIVE | *"`furina-kickoff-v0.1.md` §3.1 and §11.5 … deferred with 'solo path first' in the sprint-1 docs. Co-op is live, so the deferral condition has lapsed; no implementation and no tracking anywhere."* | `docs/missed-requirements.md` §1.2; same brief |
| `M3` | **You asked for one Furina card to become Innate when upgraded. It was measured, it was fine, and it was never shipped.** The idea was to fix "I have no Encore, so half my cards don't work." Nothing later waived it — the document holding the directive went stale and took it down | SHIP / DROP | *"one Encore card should upgrade to Innate, to solve 'I have no Encore, so half my cards don't work.'"* (verbatim [USER] directive, 2026-07-24). Measured green: +0.4pt, A1 flat, no first-fire domination | `docs/missed-requirements.md` §1.5; `docs/archive/furina-sheet-pass-4-plan.md` |
| `M4` | **Klee pass-4 ask A5: how should the scorecard's two invariants be enforced — as test failures, or as report flags?** The ask was always *which*, never *whether*. Today neither exists, and the invariant passes by coincidence | SUITE FAILURE / REPORT FLAG | *"encode the ≤4.0 A2 ceiling and the 'exactly two elite axes, specifically A1+A6' pairing (as suite failures or report flags; the ask was **which**, not **whether**) … The invariant currently passes by coincidence (A1 4.77, A6 4.05), so the regression risk is live."* | `docs/missed-requirements.md` §2.5; `docs/archive/klee-pass-4-plan.md` §3.4 |
| `M5` | **One of Furina's two declared elite axes has measured short for two weeks and nobody has said what to do about it.** Three routes were put to red-pen and none was picked | pick one of three | *"A6 median 3.5 vs declared 4.2, mechanism decomposed, three routes put to red-pen … no subsequent ruling touches Furina's A6; one of her two declared elite axes has been measurably short since 2026-07-20 with no disposition."* | `docs/missed-requirements.md` §3.7; `docs/archive/furina-sheet-pass-3-report.md` §8; `tier0/DECISIONS.md` entry 93 |
| `M6` | **A ratified card's printed text now describes something the card no longer does. Approve the rewording.** Nothing mechanical rides on it; the sheet is ratified, so the words need your countersign | APPROVE / LEAVE | *"Kaboom Beetle Swarm's printed text, after R72. The bonus now snapshots bombed-state at cast, so an enemy whose bombs hit 1 detonated keeps paying the +3 on hits 2–3 — but the card still reads '**Bombed enemies take X more per hit**', which a player will read as live state."* | `docs/open-playtest-items.md` §6.2; R72 item 4 |
| `M7` | **Should the simulator model enchantments at all?** An enchantment is state that lives on a *card*, and every modifier the sim has attaches to a *creature* — so this is a data-model decision, not a missing feature. Exactly one card in the Silent's remaining 27 needs it, which is the argument against, and the anchor is honest without it either way | MODEL / DON'T | *"Enchantments: a design pass, not a card. Directed 2026-07-27 … The pass decides whether tier0 models them at all, and whether this is a parity feature or one our own characters want."* | `docs/open-playtest-items.md` §6.2; `docs/silent-anchor-sprint-log-2026-07-27.md` §13; `docs/enchantments-design-2026-07-27.md` |
| `M8` | **Three rulings about Kokomi's card art, all cheap, all blocked on taste.** How much crop re-use is allowed; whether Watatsumi scenery counts as a card face (Furina's pass rejected an empty corridor as "a random hallway"); whether to hand-crop one banned source for a rare | three picks | *"the crop-reuse budget; whether Watatsumi environment art counts as a card face given Furina's pass rejected an empty corridor as 'a random hallway'; whether to hand-crop the banned `Character Details 1` for a rare."* | `docs/open-playtest-items.md` §6.2; `docs/kokomi-art-pass-requirements.md` §6 |
| `M9` | **Three leftovers from Kokomi's v0.4 pass.** A number to ratify, a card to rename, and a watch to keep or drop | ratify / rename / keep-or-drop | *"meter-20 ratification on the 500-run confirm; `epiphany_of_the_deep` → 'Song of Pearls'; whether to keep watching commander Garment uptime (still 50%, 58.7% in long fights)."* | `docs/open-playtest-items.md` §6.2; `docs/archive/kokomi-v0.4-report.md` §6 |
| `M10` | **The Fontaine Rares sprint closed in code and left four items owned by you, on no tracker until now.** Companion art picks, a lore/naming pass that cannot be delegated, a grading countersign, and the close-out ratification | four items | *"the companion art picks (`art/contact_sheet_companions.html` — Navia / Clorinde / Neuvillette / Arlecchino, provisional rank-1 live), the v1.7 lore/naming eyes-on audit (non-delegable), the C2 grading countersign, and close-out ratification."* Design note parked with them: Neuvillette graded WEAK/DEFERRED with the "different facet" question open | `docs/missed-requirements.md` §4.4; `docs/fontaine-rares-banner-sprint-log.md` § "Open, and owned by [USER]" |
| `M11` | **Two shop close-out items were tracked nowhere, and one of them is a gate.** §7.6 blocks a whole deferred sprint; §7.7 is small | grade / accept | *"**§7.6, the R60 phase-2 fantasy-leak grading**, is the gate on the deferred full-base-colorless-removal sprint (principles §4.7 amendment 2 records it as 'Deferred, not rejected', blocking on this grading), and §7.7 is the Track D fallback taste check (low stakes; recorded as a mod/sim divergence)."* | `docs/missed-requirements.md` Tier 5. Related but distinct from `S4-G10`, which carries the other five §7 items |
| `M12` | **A measurement you already ordered should be built over four cards, not three — and a fifth card may belong on a different watchlist.** Cheap to confirm, expensive to discover after the cell has run | confirm | *"the owed cell (tracked in `red-pen-2026-07-26.md`) is defined over three cards, but `docs/furina-cards.yaml:127` added `standing_room_only` to the watchlist — whoever builds the cell should build it over four. Similarly, catalyst Kokomi was never added to the hydro-convergence watchlist after R52 ruled her a catalyst."* | `docs/missed-requirements.md` Tier 5; `docs/red-pen-2026-07-26.md` |

**Already covered elsewhere in this file, so not duplicated as `M` rows** (named
here because a reader of the husks will look for them): the Kokomi stability
band (`S4-G6`), Klee pass-4 ask A3 (`S4-G18`), R29d's naming/lore pass
(`S4-G11`), `kurages_oath` = 12, the ten-Spotlight-icons question, Klee's two
dead-card reworks, the `scattering_spray` 7→6 and the rest of the ratification
batch (all `S4-G9`), the shop channel's other five §7 items (`S4-G10`), the
Standing Ovation boost expiry and the sim-vs-C# salon RNG divergence
(`S4-G20`), the art debt (§8), and the table agenda (§7).
