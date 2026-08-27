# BACKLOG

> **Only OPEN executable engineering work** — confirmed defects, mechanical /
> parity fixes, measurement instruments, refactors, and test-writing that need
> **no [USER] design call to start** — **plus one marked exception, the
> dormant / no-spend class below.** One of six governing files, no overlap:
> [USER] design / taste / behavior / money calls live in **QUEUE.md**, settled
> rules in **LAW.md**, shipped facts in **STATE.md**, commands in
> **OPERATIONS.md**. Identifiers are preserved from their source registers;
> closed items are in git history (tag `pre-simplification-2026-08-06`).

> **Every row is four things: current scope / next action / gate / acceptance.**
> How a row reached its current state — earlier numbers, superseded SHAs,
> landed-substep narratives, re-told rulings — lives in the commit messages
> that carry it, under the closed-items-leave-HEAD norm (CLAUDE.md §Norms).

> **DORMANT / NO-SPEND rows (ratified 2026-08-12, R183).** A minority of rows
> here are not work waiting for capacity. They exist so that budget is never
> spent on them unasked, or so that a hazard is not rediscovered from scratch.
> They are marked **`DORMANT / NO-SPEND`** in their own text, and two rules
> govern them:
>
> 1. **Every dormant row names its WAKE TRIGGER** — the observation, ruling or
>    downstream event that makes it live. A dormant row without one is
>    malformed.
> 2. **Capacity-driven work on a dormant row is PROHIBITED.** "There was time"
>    is never a reason to start one. Only the named trigger starts it.
>
> Blessing the class **retains** these rows; nothing is bulk-closed and no
> reserved ruling is pre-empted. The members are `EB-12`, `EB-15`, `EB-41`,
> `EB-70`, `EB-80`, `SKIP-10.9`, and the combined `EB-33/34/35` row.
> **`EB-70` joined the class after the blessing, at R195 (2026-08-23)** — the
> starter-offer retune was paused with the wake trigger R134 had named, so the
> class gains members by ruling and this list is where that is recorded.
> **`EB-38` is deliberately NOT in the class** — it is real capacity-deferred
> production work (the idle-animation polish sprint) and stays a normal row.

> **Resolving a provenance identifier.** `eng-backlog`, `dockets/…`,
> `user-queue` and the retired sprint docs read at
> `git show pre-simplification-2026-08-06:<path>`. The two recap registers —
> `missed-requirements` and `open-playtest-items` — left HEAD after their
> rows migrated here; read them at
> `git show aa09b97:docs/current/backlog/missed-requirements.md` and
> `git show aa09b97:docs/current/playtest/open-playtest-items.md`.
> **`aa09b97` is NOT fetchable from `origin`** — it is a merge commit that no
> ref points at any more, so `git fetch --depth=1 origin aa09b97` fails.
> It is present in the local object store of any clone that has it, and
> `git show aa09b97:<path>` works there directly; on a clone that lacks it,
> fetch the tag instead and read the pre-migration copy.

---

## tier0 — engine, pilot, constants

| ID | Item | Provenance |
|---|---|---|
| `EB-71` | **Scope:** Sly grammar is landed in both engines and deployed; `Card.sly` is the one field and the base-game keyword rides it as the reserved `{op: sly_autoplay}` rider. The `CardKeyword.Sly` rail has never been exercised in game and cannot be — **no committed sheet prints `sly_autoplay`**, so there is no card to play. **Next action:** whoever prints the first `sly_autoplay` row owns the in-game check. **Gate:** a committed sheet printing the marker. **Acceptance:** it plays on a real card | R174; `tools/lint_sly_grammar.py` (pinned by `tier0/tests/test_eb71_cs_parity.py`) |

## tier0.5 — draft / run layer / measurement

| ID | Item | Provenance |
|---|---|---|
| `EB-83` | **Scope:** Wood Carvings, `EB-68`'s last unconverted event. Both engine ops are built; R184: RESKIN — *Peck* → `tengu_flurry`, *Toric* → `chinowa_ward`, provisional (R212). **Next action:** build the missing `transform_starter_into` key and `GAME_RULES`' `slither` row (decompile-only), then convert. **Gate:** an `RT` batch; eye-read at `S4-G11`; a printed carrier takes its stacking rule to QUEUE. **Acceptance:** all three options convert exact; `slither` leaves `UNEXPRESSED` | R184; `enchantments.UNEXPRESSED`; `dossiers/…/event-conversion-gallery.md`; `atlas/tier0-engine.md` §7 |
| `EB-84` | **Scope:** the owed live smoke on enchant eligibility: one deck-screen check per `GAME_RULES` shape. The four: `nimble` → `card.GainsBlock` (`block_next_turn` NOT offered); `souls_power` → local Exhaust; the attack trio → `CanEnchantCardType == attack` on a mod attack, no mod code; the no-override trio. **Next action:** hunt an enchant event live. **Gate:** reachability — enchant events are `?`-node events, five bot runs found none, `give_card` grants CARDS not EVENTS; cost is run survival. **Acceptance:** all four watched | R159; R82; `tools/lint_enchant_parity.py` `GAME_RULES` |
| `EB-70` | **DORMANT / NO-SPEND. Wake trigger:** the Klee rework's design sweep opening — the Wings / Little Hexenzirkul class R134 names. **Scope:** `EB-27p`'s starter-offer retune, paused at R195, with the engineering half deliberately unbuilt: R160's placement clause is permissive and obliges no build, and the four `M29` picks were never made. **Next action:** none. **Gate:** the trigger above. **Acceptance:** when it is taken up it moves `RT` — and `P` if the pilot gains an accept/decline valuation — in whatever world then exists | R195 ([USER] 2026-08-23); R134; R160 |
| `EB-74` | **Scope:** lever 2 is BUILT AND STAGED — `B-alone`: `CHARGE_PER_EXHAUST` 1→2, `KOKOMI_BURST_PER_EXHAUST` untouched, on `staged/eb74-lever2-b-alone` (`5f09864`). Four numbers ride it (the rate, its C# mirror, Pearl's upgraded rate in both) plus a PROPOSED `C` bump. **Next action:** none; **merging that branch IS the pull.** Never merge it for a lint or a tidy-up; any `C` mover landing first re-baselines it. **Gate:** R213 freeze; R199 forbids moving `kokomi/assist` supply. **Acceptance:** n/a until the pull | R190; R154; R199; `review/active/eb74-lever2-options-2026-08-13.md` |
| `EB-78` | **Scope:** both `X9` remnants are discharged (R188: no Charge read budget). A `strict=True` xfail stops the suite if a cap, a dedupe or a late budget lands (each a [USER] act); `note_charge_read` instruments reads-per-turn, emit-only. **Next action:** draft §5's slate — §5.1's number for *dominant* included — and commit it DRAFTED (R212(2)). **Gate:** the batch countersign. **Watch trigger (`W9`):** `X9` returns to [USER] only if reads read as dominant. **Acceptance:** it runs, slate first | R188; R163; R212; `review/active/charge-reads-per-turn-registration-2026-08-13.md` |
| `M13` | **Scope:** `ROUTE_REGRET_MARGIN` and its `+1.0` twin (`draft.py:1694`) have no derivation; R164 left it unratified and R181 settled the scope — `C2` authorised (build owed first), `C3` declined so `Q5` drops, **Option D, no margin, stands**. **Next action:** draft §7's predictions — four `Q` slots, the `C2` half, `n`/seed, `T4`/`T5`, the trigger — commit DRAFTED (R212(2)); build `C2`. **Gate:** the batch countersign; only margin-free reads quote until then. **Acceptance:** it runs, slate first | R164; R181; R212; ex-QUEUE; `review/active/regret-margin-registration-2026-08-12.md` |
| `EB-80` | **DORMANT / NO-SPEND. Wake trigger:** the post-wave Kokomi playtest shows she needs more warding. **Scope:** Kokomi P4/P3 prevention-on-curve design review — `EB-26`'s long-unowned `D7(b)` P3, now with an owner and a trigger. **Next action:** none until the trigger fires. **Gate:** the trigger above. **Acceptance:** the review convenes | R172; `review/active/eb26-lesser-ward-draft.md` §5 |
| `EB-32` | **Scope:** the pilot block-panic rung — a pilot behaviour change that "would move every tier-0.5 number on one observation". **Next action:** build the rung. **Gate:** lands under a `POLICY_VERSION` bump and its own window. **Acceptance:** the bump and a re-baseline | eng-backlog; routed from QUEUE 2026-08-08 (R136) |
| `EB-33/34/35` | **DORMANT / NO-SPEND. Wake trigger:** the `_static_power` / reactions-promotion repricing session convenes. **Scope:** three repricing exhibits filed as inputs — The Gallery Stirs scores 0.0 at offer, Vulnerable is priced as a flat debuff, `_reaction_value` has no defensive term. **Next action:** none until the trigger. **Gate:** the trigger; its pricing calls go to [USER] as a pick list. **Acceptance:** `EB-33`'s R96 criterion is undischarged and two bumps stale — restate it against the live drafter | eng-backlog; routed from QUEUE 2026-08-08 (R136); R96 |
| `SKIP-10.9` | **DORMANT / NO-SPEND. Wake trigger:** a pass needs one of the listed mechanics — entries are promoted on demand, never swept. **Scope:** the living skip-backlog of un-modelled mechanics. **Enemy:** Back Attack, untargetable Burrow, Ethereal/Hex auras, pick-your-poison curse choice, damage caps (Hard to Kill / Plating / Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards cadence intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor-power list, the Soul Siphon stat-theft class, Blessed Antler and Philosopher's Stone. **C# structures with no sim twin (`EB-19`):** the deferred-settle machinery (`SpotlightSystem` / `CurtainCallPowers` / `FurinaResources`), which fails two ways — a stranded flush site, and the RESOLUTION POINT, which bites even when every flush site is reached (`EB-101`); plus per-dealer reaction windows (ruled co-op divergence, R1). **Next action:** none until the trigger. **Gate:** the trigger above. **Acceptance:** an entry leaves this list only by being modelled | run-model-rework-plan §10.9; `EB-29` audit |

## klee-mod — C# implementation & parity

| ID | Item | Provenance |
|---|---|---|
| `EB-53` | **Scope:** the N1 end-of-turn attribution pass is built and live-verified. The docket is per SEAT, one slot per source, and `Powers/TurnEndAttribution.cs` holds the four sources and their firing order once, so the display cannot misname it. **Next action:** capture `C6`'s co-op half. **Gate:** a two-seat runtime; the bridge drives singleplayer only. **Acceptance:** `C6` co-op captured and the electro (Oz) leg isolated, or `M16` re-specs them | `git show pre-simplification-2026-08-06:docs/archive/playtest4-triage-2026-08-04.md` §N1; refiled 2026-08-08 (R136); eyes-on `M26` |
| `EB-65` | **Scope:** seven Furina power badges render the `NOPE` placeholder — `KleePowerIcons.PathFor` wires seven paths ahead of their art and `KleePck.Path` returns null. The seven: `res://furina/powers/{fortissimo_guard, stagehands, stagehands_encore, courtroom_drama, the_gallery_stirs, quick_change, unheard_confession}.png`. The art exists. **Next action:** apply rank 1, land the PNGs, commit the sheet. **Gate:** none — R212(1): Claude picks, [USER] vetoes on the sheet. **Acceptance:** all seven render | R212; live-game session 2026-08-08; `review/active/art-runs-2026-08-08.md` |
| `EB-116` | **Scope:** the extra-turn reaction window is fixed and shipped (`EB-113` moved `MarkTurnStart()` to `AfterTakingExtraTurn`, pinned headless) but never WATCHED live. One live look is owed: an extra turn with `ReactionTriggeredThisTurn` false at its start and Courtroom Drama's Vulnerable applying. Adjacent: `FrozenPower.cs:112` shares the clock. **Next action:** hunt the relic. **Gate:** reachability — the only extra-turn source is Pael's Eye, so it costs a run and a relic roll. **Acceptance:** the window seen reopening | `EB-113` close-out 2026-08-13; correctness audit r2 (R2-2) |

## tools — codegen, lint, scripts, refactors

| ID | Item | Provenance |
|---|---|---|
| `EB-128` | **Scope:** `game_ref/` was destroyed a fourth time and RESTORED; both pools VERIFY OK and the guards are built. **Next action:** [USER]'s three hand-authored `*_char_facts.yaml` (`defect`, `necrobinder`, `regent`), not tool-regenerable. **Gate:** that upload. **Acceptance:** the three files land. **Standing:** `--verify` checks CONSISTENCY, not CURRENCY — a backup predating the last field retirement passes and will not load; never stub a missing layer, stub floors are not floors | restored 2026-08-24; `tools/build_official_sheet.py` docstring; `EB-71`/R174; 3 prior losses |
| `EB-137` | **Scope:** the salon verbs are in `BRANCH_OPS` with no `BRANCH_FIELDS` entry, so `_branch_op_reason` raises `KeyError` at `gen_klee_cards.py:527` instead of blocking by name, taking the sheet. TWO tables: patched, `build_description` exits at `:5120` for a missing text arm. **Next action:** add both `BRANCH_FIELDS` entries and both `_branch_text` arms, copy provisional (R212(7)); pin both shapes emitting and bad fields blocking. **Gate:** none. **Acceptance:** no raise; `--check` stays clean | `EB-118` `Win3` verification 2026-08-25; `eb136-audit-2026-08-25`; `EB-133` class |
| `EB-41` | **DORMANT / NO-SPEND. Wake trigger:** [USER] rules on either question. **Scope:** no executable bullet remains; three mechanical refactors landed, the two below want a ruling first. **(1) Telemetry dedupe:** the eight `*_telemetry.py` share a shape, not code; folding `encore`/`fanfare` asks if the meters are one, and a shared base moves REGISTERED definitions. **(2) `exp_*` move:** R68's criterion selects none of the 21; which records stop being re-runnable is [USER]'s. **Next action:** none. **Gate:** the trigger. **Acceptance:** the ruling arrives | eng-backlog §7; R68; R136 |

## tests — pins & filed-not-fixed

| ID | Item | Provenance |
|---|---|---|
| `EB-12` | **DORMANT / NO-SPEND. Wake trigger:** a second observation of this failure. **Scope:** Understudy Defect 14 — `bridge_unreachable` by timeout with the process alive; one observation, no reproduction, FILED NOT FIXED, and no second one since. `hangwatch.py` now files a live-but-spinning game as `unresponsive_spin`, so a recurrence is labelled by which failure it is — the evidence this row lacks. **Next action:** none until the trigger. **Gate:** the trigger. **Acceptance:** a second, classified observation | eng-backlog §2; `review/active/traversal-pass-2026-08-08.md` |
| `EB-15` | **DORMANT / NO-SPEND. Wake trigger:** a Custom run or a hosted lobby. **Scope:** the seed's `lobby` route is unreachable for standard singleplayer. `StartRunLobby.SetSeed` refuses on the **GameMode** (*Seed should not be changed in standard mode!*), not `NetService.Type`; `InitializeSingleplayer` builds `GameMode.Standard` and `debug_override` is the route. The arm is KEPT: deleting a correct-but-unreachable arm is taste. **Next action:** none until the trigger. **Gate:** the trigger. **Acceptance:** the arm fires | eng-backlog §2; `review/active/traversal-pass-2026-08-08.md` |

## art — production work

| ID | Item | Provenance |
|---|---|---|
| `EB-38` | **Scope:** Animation Track F3 plus the sprint-1 polish deferral — rest/merchant gentle idles for both characters; the in-combat layer is approved and frozen but no polish sprint has opened. **Next action:** open the polish sprint. **Gate:** capacity (deliberately NOT in the dormant class — this is real deferred production work). **Acceptance:** rest/merchant idles ship for both characters | eng-backlog §6; missed-requirements §4.5 |
| `EB-40` | **Scope:** Furina's energy-counter SCENE, engineering half; icons SHIPPED. No precedent: all three characters return the base `ironclad_energy_counter.tscn`. From the assembly: `NEnergyCounter.cs:168` hard-casts `Instantiate<NEnergyCounter>`, so the root must carry that script, and `_Ready` makes five non-null `GetNode`s (`Label`, `%Layers`, `%RotationLayers`, `%EnergyVfxBack`, `%EnergyVfxFront`). **Next action:** author it when the art lands. **Gate:** QUEUE `M19`. **Acceptance:** all five `GetNode`s resolve | eng-backlog §6; furina-art-pass-requirements §8; split 2026-08-11 |
