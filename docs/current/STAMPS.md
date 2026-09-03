# STAMPS

> **Stamp history — ON DEMAND, never always-read.** One section per stamp
> letter of the run cell (`RT` / `D` / `P` / `C`), newest level first: what each
> level covers, what it archives, and the ruling that carried it. A stamp's
> history lives here and in the commit that bumped it — [`STATE.md`](STATE.md)
> carries only the live value, its source file and one sentence. Stamp law,
> citability and when a standing baseline is owed are in
> [`EXPERIMENTS.md`](EXPERIMENTS.md).

Live cell **`RT13 / D18 / P11 / C21`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **6**. Numbers are never comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable.

**Naming.** The `EB-118` richness-pass CONTENT windows are `Win1` / `Win2` /
`Win2b` / `Win3`, and the two deferred ones `Win10` / `Win11`. Older packets
spell them `W1`–`W3` / `W10` / `W11`; in `STATE.md` and here, `W1`–`W9` are the
watch register and `W4` is separately the pilot-weight sweep (EXPERIMENTS `W4`).

## `RT` — `RUNTEMPLATE_VERSION` (`tier0/constants.py`), live **13**

### `RT13` — `EB-83`: Wood Carvings, the last unconverted event

`EB-83`, 2026-09-02. ONE change, and the same shape `RT9`'s single act-2
addition and `RT11`'s single act-3 addition were: **Wood Carvings joins the
act-1 pool** (12 own → 13 own; 16 → 17 reachable with the four all-acts
events), so act-1 event odds move for every character and **no `RT12` act-1
event number carries across.** It closes `EB-68`'s conversion sweep — the skip
list in `tier05/content/events.yaml` now holds no event that was blocked on an
enchantment or on a colorless card.

What it puts into a run that `RT12` could not: two colorless event cards no
other door can reach (`tengu_flurry`, `chinju_ward` — the R184 reskins of
*Peck* and *Toric Toughness*, named at R231), a NINTH enchantment
(`slither`, the first to touch a card's cost at all), and the **first printed
carrier of `block_at_turn_start`**, the delayed-Block power that had been inert
since 2026-08-26. All three engine surfaces predate this bump and none was
invented inside the conversion (`EB-82`'s admission rule); what moved is the
content that reaches them. The event layer gained one key,
`transform_starter_into`.

No drafter or pilot code moved — enchantments are still post-draft only, and
both new cards are `rarity: event`, so no reward, shop, Neow or Ancient roll
can see them — so `DRAFTER_VERSION` and `draft.POLICY_VERSION` are untouched
and the payoff-reach `D14` pin stands. `CONSTANTS_VERSION` did not move: no
tier0 engine rule changed. **RE-BASELINE OWED, not taken in this window:** the
standing twelve-arm table (`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`)
is an `RT12` read and every arm's act-1 numbers are now stale under R68.

### `RT12` — the run-layer half of the window-2 correctness batch

`EB-104`, 2026-08-13. Five fixes batched into one bump for the same reason v8
batched two — all `RUNTEMPLATE` content, one window, none quotable alone.
`EB-102`: `resolve_shop` finally receives the run's **Featured Banner**, so the
shop can no longer sell a 5-star the banner excluded from every reward screen;
it changes which card `rng.choice` lands on, so every §4.7 shop-channel figure
taken under `C9` renumbers, and it lands **before** the `M14` shop rerun as that
row required. `EB-103`: potion capacity is derived from held relics **on read**,
so a mid-run Potion Belt is visible to `resolve_event` and its grant is no
longer dropped unlogged. `EB-110`: the rest-site heal **floors** where it
rounded, matching the authority's truncation through `SetCurrentHpInternal` —
2.39 HP/run of one-directional sim-generous bias removed from the HP ledger.
`EB-111`: Book of Five Rings counts **event** deck-adds through a single
`note_add` door, not only shop buys and reward picks (88 uncounted adds across
64 book-holding runs in 300). `EB-112`: event card-reward screens roll rarity
through **`RARITY_ODDS`** like any other reward screen — 20.0% Rare per offer
becomes 5.0% on three shipped options in acts 1 and 2 for every character;
**`RARITY_ODDS` itself is unmoved**, only the site that failed to consult it.
No drafter or pilot code moved, so `D` and `P` were untouched and the
payoff-reach `D14` pin stood; `C` moved in the same window on its own ground.
**No v11 run-layer number carries across.** **Re-baselined at the bump** — the
twelve-arm standing table `review/records/sitting-reads-2026-08-13.md`.

`RT11` beneath it was the coordinated 2026-08-13 window (`EB-82` + `EB-85`),
batched into one bump because both are `RUNTEMPLATE` content and neither was
quotable alone: `grave_of_the_forgotten` joining the **act-3** event pool (2 own
→ 3 own) with an Accept branch granting `forgotten_soul`, an event relic no
reward, Neow or Ancient roll can reach; and five places where tier0 modelled an
enchantment differently from what `sts2.dll` v0.107.1 ships.

## `D` — `DRAFTER_VERSION` (`tier0/constants.py`), live **18**

### `D18` — `EB-28`: the Salon deploy stops pricing at zero

Cross-plan the members were invisible. ONE new dial,
`STATIC_SALON_MEMBER_VALUE = 1.5` per member, at the conservative bottom of a
derived 1.5–4.0 band; **[USER]-overridable, one constant**. **NINE rows, all
Furina salon, nothing else moves:** `salon_debut`, `gentilhomme_usher`,
`surintendante_chevalmarin`, `mademoiselle_crabaletta`, `full_ensemble`,
`dress_rehearsal`, `overflowing_hospitality`, `endless_waltz`, `grand_gala`,
each by `members × 1.5 ÷ cost` on both faces.

### `D17` — `Win3`'s two new pricing terms

`EB-118` Phase-3 `Win3` (R211, [USER] 2026-08-25), and the first bump in the
series where the drafter learns a **cost** rather than a value.
**(a) `STATIC_SPARK_SPEND_COST = 2.5`** — the `spend_spark` branch of `_op_price`
stops reading the dead GAIN dial with the sign flipped and reads its own live
one. The bump is **UNCONDITIONAL and was owed in writing**: that branch carried
an explicit no-bump licence naming what would spend it — "the first sink card
that prints it" — and `powder_charge` is that card. The value is **DERIVED, not
picked** (three routes; two converge on 2.50 from opposite directions) and taken
at the TOP of the convergent range under R194's direction rule, so the residual
error under-values the sink rather than over-valuing it.
**(b) `spotlight_moved_this_turn` joins `STATIC_STATE_CONDITIONS`** at share
**`STATIC_SPOTLIGHT_MOVED_SHARE = 0.167`**, the measured spotlight-arm rate;
R211 ratified the rider but not the share, and 0.167 is the conservative end of
the defensible band (0.167–0.5). **BOTH VALUES ARE [USER]-OVERRIDABLE and each
lives in exactly one constant.**

**The archive scope is unusually small and that is the point: FOUR ROWS, three
of them new.** The spend dial re-prices the three new sinks (`powder_charge`
7.0000/10.0000 → **2.0000/5.0000**, `hold_the_line` 5.0000/8.0000 →
**0.0000/3.0000**, `smoke_and_sparks` 6.0000/8.0000 → **1.0000/3.0000**) and
NOTHING ELSE — R211 kept `STATIC_SPARK_VALUE` at 0.0, so all eleven shipped Klee
Spark rows and `prune_witch_hunt` are unchanged to four decimals. The rider
re-prices `take_it_from_the_top` (5.0000/5.0000 → **6.6700/7.3380**, which is
the whole reason it was taken: the upgrade was invisible on both faces) and
`curtain_cue` (0.0000 → **0.4002**). **`directors_cut` does NOT move at any
share** — both its branches pay in dead dials — which corrects an expectation
the `EB-118` row carried.

### `D16` — Phase 2's two formerly-inert drafter terms go live

`EB-118` Phase 2: `STATIC_ETHEREAL_SHARE` now prices a shipped card
(`big_badda_boom` 8.0000 → 4.8000 base, 8.0000 upgraded), and `choose_one`'s
`MAX(modes)` arbitration is reachable but moves no number. The share is
**RATIFIED at 0.6 (R205)**; the read and the rank plateau are recorded at the
constant in `tier05/draft.py`.

### `D15` — `EB-43`

The spotlight limb of `core_complete` / `_core_progress` requires a machinery
payoff.

## `P` — `POLICY_VERSION` (`tier05/draft.py`), live **11**

### `P11` — the scorer-literacy window (R207)

FOUR items, nothing printed moves. **`EB-143`**: the Spark hold-versus-spend
term — the ONE new weight, `SPARK_HOLD_VALUE_WEIGHT = 1.0`, inert at 0.0.
**`EB-144`** reads five predicates over ten rows at score time (seven predate
`Win3`); `reaction_triggered_by_this` and `killed_target` stay blind by design;
both Salon verbs read the resolver's `salon_tick_amount` — no new dial.
**`EB-145`**: the score forecasts its own selection — Tide of Names, Pearl
Barrage. **`EB-129`** pays the Book of Five Rings chunk at event valuation
(R205's own-window gate set aside by [USER], null scratch). **Archive: roster
combat + tier-0.5. `EB-144` provably cannot move the `ref_*` anchors (they
print no conditional — asserted by test); `EB-129`'s event valuation is
generic, and the anchor ARMS did move by a few runs in 3000, inside interval
(§4.2 of the read below).** **The re-baseline was TAKEN at
`RT12/D18/P11/C20`** (`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`,
`main` = `190e598`, 2026-08-26) **and its caveat check graded all three of the
standing read's diagnostic caveats CLEARED against code** — the hold-versus-spend
term is subtracted inside `_score`, both blind predicates and both Salon verbs
are read at score time, and `_formula_amount` runs in the score seam and not
only the chooser — **so that table publishes as the standing re-baseline AND as
the Phase-4 milestone table (R211 item 7), with zero interval separations; its
§4.2 records that the anchor arms' own tier-0.5 counts and `deck` means did move
by a few runs, inside interval on every rate column.**

### `P10` — `Win3`'s exhaust-chooser repair (R211)

**Not a flip — no switch was staged for it.** `policy.exhaust_victim`'s DEFAULT
payout hook changes from `identity_blind_payout` to **`formula_aware_payout`**,
which pays a candidate the MARGINAL contribution it would make to the exhausting
card's OWN printed `exhaust_selection_*` count, times that card's own printed
`per`, times the board its own printed `target` names — R211's **multiplicity
clause**: an `all_enemies` formula multiplies by `len(state.living_enemies)`. It
is derived from what the card prints, never a hardcoded prefer-expensive: change
the slope and the chooser changes with it, delete the card and the chooser is
identity-blind again. `PILOT_WEIGHTS_VERSION` **5** labels the weight that
arrives with it, **`EXHAUST_FORMULA_PAYOUT_WEIGHT = 1.0`** — and unlike v2/v3/v4
this is a genuinely NEW weight rather than an existing one entering the read
set. **What re-baselines is narrower than the stamp suggests, and it is asserted
rather than argued:** the hook returns 0.0 for any card printing no selection
formula, exactly TWO rows on any sheet print one (`pearl_barrage`,
`the_tide_remembers`), and the chooser is deterministic given the pool — so
every other chosen-Exhaust carrier's pick is provably unchanged, all twelve of
them, Sly riders included. That sweep is a test, and it exists BECAUSE it
replaces a fourth scratch run that would have been provably bit-identical to
baseline. The **Rare-rotation trade is ACCEPTED and paired with retrieval**
(`shell_of_sanctuary`'s `Win3` body loans a rotated Rare back out of the Exhaust
pile).

### `P9` — the `EB-118` Phase-2C mode-chooser flip

`MODE_CHOOSER_ENABLED` is `True` and `effects._chosen_mode` asks
`policy.choose_mode` — argmax of the pilot's per-op valuations over the live
board, minus the TRUE HP an overdrawing `spend_encore` costs, ties to the lowest
index. `PILOT_WEIGHTS_VERSION` 4 labels the weight set now that
`MODE_OVERDRAW_HP_VALUE` is read; no weight VALUE moved from the hand-picked
vector.

### `P8` — the `EB-118` Phase-2A pilot-policy flip

The FIRST of Phase 2's two activation windows, CLOSED at the landing
2026-08-24. `PILOT_POLICIES_ENABLED` `False` → `True`, with
`C.PILOT_WEIGHTS_VERSION` 2 → 3 in the SAME edit because the pair's eleven
`BOMB_*` / `EXHAUST_*` weights are read for the first time and so ENTER the set
that stamp labels — one edit, three integers, no fourth, and NO weight value
moved. Klee's bomb placement (concentration form) and Kokomi's chosen exhaust
stop being heuristics and become decisions, so **every Klee tier-0.5 number and
every Kokomi number touching a chosen exhaust is archive from this bump**. `RT`
(12), `D` (16) and `C` (13) did not move with it. **The gate that held it was
RETIRED, not satisfied:** it was staged on `staged/eb118-2a-policy-flip` against
one red test — `test_pass3::test_per_deck_a2_bands`, `klee/reaction_weighted`
`A2_scaling` 3.4898 → 3.5290 against a ratified 3.5 — and **R204 (2026-08-24)
retired the live per-axis deck-band system as acceptance law roster-wide**,
deleting that test with the system it read and closing `QUEUE` `M40` with no
replacement number. The probe is what the ruling acted on: the band did not hold
pre-flip either (3.5810 at seed 7, 3.7735 at n=1000), so the gate was passing on
one lucky cell by 0.0102 against a 0.21 seed spread. The landing is an
integration act and mints no R-number. The pilot-weight sweep (EXPERIMENTS `W4`)
RAN inside this window and adopted nothing (78 points, all INSEPARABLE), so v3
labels the hand-picked vector. The tier-0 anchor, the frozen calibration battery
and the v0.1 errata medians are byte-identical across the flip, checked.

### `P7` and below

`P7` was R176 — the pilot values `copy_companion_in_hand` /
`replay_next_companion` (`EB-17p`'s 40,396 draws / 0 plays was pilot scoring,
not an unreachable condition). `P6` was `EB-29t`'s Enrage/Intangible reads; `P5`
was `EB-24p`'s `reaction_triggered_this_turn` read; `P4` was R124's
both-Spotlight-modes read.

## `C` — `CONSTANTS_VERSION` (`tier0/constants.py`), live **21**

### `C21` — `EB-219`: Prune's Spark grant becomes Klee's kit declaration

**Entry owed, and this is a hygiene note rather than that entry.**
`tier0/constants.py` has read **21** since `EB-219` landed, and
[`STATE.md`](STATE.md) carries the one-line summary — Prune's printed
`gain_spark` ops leave the sheet, her Spark grant becoming Klee's own kit
declaration (`KLEE_COMPANION_SPARK_*`, `LAW.md:145`). This heading and the live
cell at the top of the file were both left at **20** by that bump and are
corrected here (`EB-83`, 2026-09-02); the window's own account stays `EB-219`'s
to write, because nothing in this file may restate a window second-hand.

### `C20` — `EB-139`'s Swirl aura-aware bind (R211; built 2026-08-26)

An engine AIM change of `C18`'s class — no printed number, label, upgrade delta
or dial moves. When a card carrying an aimed Swirl is played and any living
enemy holds an aura, the whole card binds to the lowest-HP aura-bearer; with no
aura, the normal lowest-HP bind. Forced-random autoplay is untouched. Six
companion rows carry an aimed Swirl and five already swirled at that body, so
the only number that moves is `sayu_yoohoo_windwheel`'s damage, on the nine
character arms. **The anchor does NOT move** — verified identical — unlike
`C18`. No standing baseline owed (R207); a second `C`-class change (the ruled
Sweet Dreams body, R189/R205) may join this window.

**Joined the same window 2026-08-26 (R207): the ruled Sweet Dreams (`elemental_ecstasy`) body** — R189 direction, R205 sub-shape. The Block branch moves from `target_has_nonpyro_aura` to a NEW any-aura predicate `target_has_aura` and the Block moves 8 → 5, so Klee's own Pyro turns on the card's biggest clause for the first time. One sheet row; drafter price 2.5000 → 1.7500 base and 5.0000 → 3.5000 upgraded; upgrade row untouched; `D` and `P` unmoved because the predicate's drafter/pilot entries preserve the pricing and scoring the row already had. Hand-written card (R23), so codegen is byte-identical; `ElementalEcstasy.cs` hand-edited. Disclosure: a 200-run commit-hash scratch on `klee/reaction` read flat (5.5% either side). M17's blind grade preceded it (4 PREDICTED / 1 SPLIT / 0 MISS; the card's own trigger silent by 0.17 pp — a candidate, not a verdict). Landed as `a49bf20`.
### `C19` — the `EB-118` Phase-3 `Win3` card-body pass

R211, [USER] 2026-08-25 — the `Win3` ratification slate. ONE window, **EIGHT
sheet rows, all three characters**: five NEW rows and three **REWRITES THAT KEEP
THEIR CARD IDS**.

**Klee** gains the three ratified Spark sinks, the first rows on any sheet to
print `spend_spark` — `powder_charge` (spend 2, `detonate bonus: 4`, upgrade
`{bonus: +3}`), `hold_the_line` (spend 2, Block 5, `enemy_intends_attack` →
Block 6, upgrade `{conditional_block: +3}` raising both halves) and
`smoke_and_sparks` (spend 2, Vulnerable 3, upgrade `{vulnerable: +1}`). The 3–4
sink floor is met AT THREE. **All three are `role: glue`, so no payoff count
moves anywhere**; what moves is sub-pool size, and `klee/spark`'s payoff DENSITY
falls 24% → 21% — a disclosure, not a breach (that arm is not on R199's priority
list), and the second consecutive window in which it thins. The Spark price is
at TOP LEVEL on all three, which is structural: a `spend_spark` in a branch is
invisible to the playability gate and the payoff would fire unpaid.

**Furina** gains `change_the_bill` (`salon_rotate` + `salon_perform` + Block 3,
upgrade `{block: +3}`) — the first sheet row in the repo to print EITHER Salon
verb, both built and unused since Phase 2 — and `take_it_from_the_top` (Block 5
+ `spotlight_moved_this_turn` → 10 damage, upgrade `{conditional_damage: +4}`),
which takes `furina/spotlight` payoff supply 5 → 6 over a sub-pool 17 → 18:
**fourth in the ruled priority order, so a disclosure item**.

**Kokomi's pool stays at 76 rows AND at the same 76 ids**: `pearl_barrage` stops
reading the exhaust PILE and reads the CARD YOU CHOSE (`exhaust_from 1 chosen` +
`5 + 3 per exhaust_selection_cost`, delta `{formula_per: +1}` →
`{formula_base: +3}`, ladder 5/8/11 over the whole live range because her sheet
has no card above cost 2); `shell_of_sanctuary` keeps its id and becomes
**"Salvage the Line"** (cost 2 → 1, `block 11` → draw → **recall from exhaust**
→ Charge 2 → Block 4, `exhaust: true`, `[generic]` → `[priest, assist]`, upgrade
sheet UNTOUCHED because `{block: 4}` was already the ruled 4 → 8);
`the_tide_remembers` keeps its id and becomes **"Tide of Names"**
(`exhaust_from 1 chosen` + `5 + 2 per cost` to ALL, delta `{damage: +3}` →
`{formula_base: +2}`, tags and role unmoved so `kokomi/priest` holds at 12).

**The effect order on Salvage the Line is the ruled correction and it is
load-bearing** — recall-then-draw puts the rescued card at draw-pile index 0 and
the draw pops index 0, so it would land straight in hand, defeating the rule
that a retrieved card goes to the TOP of the draw pile and never to hand. It is
also the repo's FIRST Exhaust-retrieving row, so `lint_recall_exhaust`'s
card-shape leg stops being vacuous.

**Two standing debts move, measured:** the flat-Block clone cluster 8 → 7, and
the exhaust-pile reader family 5 → 3 (which completes R208's `damage@one~`
five-to-two). `kokomi` near-duplicates hold at 29 against an untouched limit of
30; distinct signatures `kokomi` 57% → 59%, `klee` 62% → 63%, `furina` 76% →
76%.

**The standing read this window owed is TAKEN and PUBLISHED**
(`review/records/sitting-reads-2026-08-25-c19-d17-p10.md`), **DIAGNOSTIC-SCOPED
and NOT the Phase-4 milestone table** (R211 item 7): the pilot has no
hold-versus-spend term for Sparks, and its scorer reads neither Furina row's
state nor Tide of Names' payout, so those numbers are floors and a null result
on them is not evidence.

### `C18` — `EB-136`'s same-target binding (R210, [USER] 2026-08-25 — full parity)

Not a sheet window and not a card-body pass: no printed number, label, upgrade
delta or dial value moves. What moves is how the resolver AIMS. A card's
`target: enemy` ops used to re-resolve INDEPENDENTLY PER OP to the lowest-HP
living enemy; they now bind to ONE creature picked at card-play construction and
held for the whole play, which is C#'s `init`-only `cardPlay.Target`. `times`
binds in the same pass (hits after the aim dies fizzle, no re-pick);
`force_random_targeting` rolls once per card and only for a card that aims; and
the dead-target rule is reproduced op by op AND IS NOT UNIFORM — aimed damage
FIZZLES (`AttackCommand` breaks), aimed powers LAND ON THE CORPSE
(`PowerCmd.Apply` guards only `CanReceivePowers`), and `place_bomb`,
`move_bombs`, `detonate`, `apply_aura` and `swirl` land there too, each on the
decompiled evidence recorded in the blast-radius audit.

**Archive: every combat AND tier-0.5 number for every character, INCLUDING THE
ANCHOR'S** — the ruled scope is 28 live cards plus 7 more for `times`, and it
reaches `ref_ironclad`'s starter `bash`, `ref_silent` and both `real_*` pools.
The anchor renormalises to 3.0 on every axis by construction, which is exactly
why its moved combat behaviour is declared: it is the DIVISOR in
`axes.normalize`, and `bash`'s Vulnerable now lands on the body its 8 killed
instead of walking to a living bystander — a live debuff removed, not a rounding
difference.

Named consequences: `sparkly_explosion`'s `C17` DIAGNOSTIC caveat is
**CLEARED**; `EB-118` (1)'s bomb-placement chooser is superseded for
`target: enemy` (nothing in `policy.py` edited, and the pilot-weight sweep's
(EXPERIMENTS `W4`) source-derived scope narrows behind it); and ONE question is
left open on purpose — `_op_swirl`'s aura re-aim, which Q1(b) and the row's
destination-scoring severance answer differently, pinned as unruled by a strict
xfail. **No standing baseline is owed (R207 as agreed at the ruling): `Win3`'s
single public read absorbs the movement and this landed before it; the
disclosure is a commit-hash scratch in PR text.**

### `C17` — the `EB-118` Phase-3 `Win2b` card-body pass (R208)

Five ratified bodies across all three sheets, the first window since `C13` to
archive all three characters at once: `sparkly_explosion` becomes `move_bombs` +
`detonate bonus: 3` + `damage 14` in that order (upgrade `{damage: +5}`
unchanged, so 14 → 19; `spark` tag dropped); `standing_room_only` becomes Block
3 plus an `encore_at_least_5` branch paying Block 3 else a draw, retyped attack
→ skill with `role` payoff → glue and upgrade `{block: +2}`;
`dramatic_entrance` becomes Deal 7 plus a `fanfare_at_least_12` 7-to-ALL branch,
no label moving; `undertow` takes exactly two changes (formula base 4 → 5, an
appended `exhaust_pile_at_least_3` draw) and keeps everything else;
`depths_judgment` becomes Deal 14 plus a Block 8 branch, upgrade
`{formula_per: +1}` → `{damage: +4}`, and its bar reads
**`exhaust_pile_at_least_8`** — item (f) of that window, ruled late into it by
R209 ([USER] 2026-08-25, pre-merge), which moved the bar 6 → 8 on both faces
against clean fire rates of 38.4% and 24.2%; under R58 the bar may rise again
and may never come down. **Archive: every tier-0.5 AND combat number for Klee,
Furina and Kokomi** — all five are draftable rows. `sparkly_explosion`'s
simulated number was DIAGNOSTIC here until `EB-136`'s same-target repair landed
at `C18`, which cleared it.

### `C16` — the `EB-118` Phase-3 `Win2` card-body pass (R202)

Three ratified Kokomi bodies and their upgrade deltas: `moon_signal` becomes a
chosen discard plus `recall_to_draw` with the draw moved onto a Sly rider
(upgrade `{retain: true}`), `crane_wing` printed Block 6 → 4 with `{block: +2}`
unchanged, and `tighten_the_cords` Block 3 → 5 with its Metallicize gated on
`exhaust_pile_at_least_3`, upgrade corrected to `{block: +2}` (R58) and labels
moved `[generic]` / `glue` → `[priest]` / `payoff`, which reaches R202's LAW
amendment a second time. `encore_performance`'s ruled `{retain: true}`
(ex-`M27`, R205) rides the same landing on its own provenance. **Archive: every
Kokomi tier-0.5 and combat number, and every Furina tier-0.5 number** — the Rare
that had no upgrade path is now a rest-site smith candidate. Klee is untouched.

### `C15` — the `EB-118` Phase-3 `Win1` label pass

Metadata only: sixteen `role` conversions and five `archetypes` changes over
nineteen cards, the three `tempo_band.run` values the classifier re-derives off
`role`, and `SecretStash.cs` dropping Big Badda Boom from the derived
`demolition_commons` pool (8 members → 7, a combat outcome-distribution change).
**The first bump taken under R202's LAW amendment** — `role` / `archetypes` are
material card-sheet edits — so **every tier-0.5 drafted number for all three
characters is archive**; the combat archive is only Klee numbers that depend on
what `secret_stash` produces.

### `C14` — `deep_breath`'s mode 2

`spend_encore 3` + `draw 3` (R205); mode 1 and every frame field are unchanged.

### `C13` — the `EB-118` Phase-2 sheet-and-engine integration window

`big_badda_boom` (Ethereal carrier, R201's kill rider), the twelve `place_bomb`
rows leaving `target: random_enemy`, `bomb_damage_per_rotation` as a new engine
power with a once-per-turn latch, `lasting_impression`'s `{encore: +2}`, and
`deep_breath`'s conversion to `choose_one`. `C13` is the world
`review/records/sitting-reads-2026-08-24-c13-d16.md` was read in; that table is
superseded by the `C19` read and stands as published (R101b).
