# N1 attribution pass — the two engineering legs

Branch `n1-engineering-legs`, worktree `../GItS-n1`, off `main` @ `986da95`.
Backlog row: `EB-53`. Source of the ask:
`git show pre-simplification-2026-08-06:docs/archive/playtest4-triage-2026-08-04.md` §N1.

Two of N1's four legs are [USER]-gated and were **not touched**: Furina summon
damage numbers (awaits the R89 countersign) and Klee bomb variety
(rework-scoped design). This packet covers the other two.

---

## 1. What was built

Both engineering legs landed as **one widget**, because the ask says they
should: *"whatever the pass does for summons should carry burst attribution
too."*

### The end-of-turn docket

A creature-tracked display, **one per player seat**, carrying a slot per
end-of-turn source standing on that creature, in the order they fire. Each
slot shows the source's entity or badge, the number it is about to produce,
the turns it has left, and a hover that explains it.

| leg | how the docket answers it |
|---|---|
| **Kokomi Bake-Kurage** — "render the summon entity … and preview the pulse's damage before end of turn" | The jellyfish's slot renders the summon art as a standing entity, and its chip prints `KurageSummonPower.PulseDamage(owner)` — the *same static the hit calls* — refreshed on every Charge gain, card play and turn boundary. |
| **Burst visibility (all seats)** — "off-seat bursts are invisible inside the same end-of-turn noise" | The docket is anchored to the creature that OWNS the source and is spawned for every `state.Players` entry. A partner's Sparks 'n' Splash is announced over the partner, counts down over the partner, and **flashes over the partner as it fires**. Position is the attribution. |

### Files

| file | what |
|---|---|
| `klee-mod/KleeCode/Powers/TurnEndAttribution.cs` | **new.** The ordered table of the four end-of-turn sources: presence, preview number, "is this above its printed rate", hover copy, and the `Resolve` delegate. |
| `klee-mod/KleeCode/Powers/TurnEndSequencer.cs` | rewritten to **walk that table** instead of carrying four hand-written statements. Plus three pure-redraw funnels (card played / turn start / turn end). |
| `klee-mod/KleeCode/Vfx/TurnEndPreviewBridge.cs` | **new.** The display. Registry + tracking + slot row + chips + per-slot hovers + the fire flash. |
| `klee-mod/pck-src/shared/turn_end_docket.tscn` | **new.** Script-less scene: 4 slots, `RESET` + `fire1..4`. |
| `tools/cut_kurage_summon.py` | **new.** Cuts `ImageGen/images/kokomi/summon/bake_kurage.png` (64×128) from `art/raw/Bake-Kurage_Summon.png` (420×720). Hand polygon, `--check` byte-pin twin. |
| `tools/build_pck.ps1` | stages `kokomi\summon`, mirroring the `furina\salon` block. |
| `tools/art_lint.py` | registers the new out-path in the L11 producer table. |
| `tools/lint_constant_parity.py` | three geometry constants declared UNMIRRORED (see §4). |
| `tier0/tests/test_reaction_phase_parity.py` | the order gate re-pointed at the table + a new gate that the sequencer walks it; two new co-tenancy ledger rows. |
| `klee-mod/KleeCode/Cards/KokomiRiderTips.cs` | `PulseBody` gains a **public creature overload** so the docket hover and the card tip are one paragraph. |
| `KleeMod.cs`, `Diagnostics/KleeSceneTelemetry.cs`, `Powers/KokomiResources.cs`, `Vfx/GaugeBridge.cs` | loc titles, scene telemetry, the Charge refresh funnel, the Activate postfix. |
| `docs/current/atlas/klee-mod-runtime.md`, `tools/README.md`, `docs/current/BACKLOG.md` | doc updates. |

**The art is produced.** `ImageGen/images/kokomi/summon/bake_kurage.png` was
generated on the main checkout (gitignored, regenerable, nothing committed), so
the next `build_pck.ps1` there will not report a SKIP for it.

---

## 2. Idioms followed, with citations

Nothing below is a new pattern. Every one of these is a decision the repo had
already made and written down.

1. **Preview-truth on the resolution's own accessor** — the Furina legibility
   sprint's law, restated in `KokomiRiderTips`'s header: *"a preview and an
   effect that compute separately will eventually disagree, and the player
   believes the preview."* Every number the docket prints comes from the code
   that resolves it: `KurageSummonPower.PulseDamage`,
   `KitBurstConstants.Volley*`, `CompanionConstants.OzDamage`,
   `CompanionConstants.MasqueBondBlock`. `TurnEndAttribution` re-derives no
   arithmetic.

2. **One list, not two.** The four sources' ORDER used to live only in
   `TurnEndSequencer`'s body. A display naming them would have been a second
   hand-written copy — the exact drift shape (1) legislates against. So the
   order moved into `TurnEndAttribution.Order` and the sequencer walks it. The
   sequence itself is unchanged and still tier0
   `effects.player_turn_end_triggers`, top to bottom (EB-19/races-a + races-c).

3. **Salon-member rendering, verbatim** (`Vfx/SalonVisualsBridge.cs`, animation
   sprint 2 Track D): identity read **per slot from state on every refresh**;
   a live number on a chip from the same expression the upkeep resolves
   through (`SalonMemberPower.TickValue` → here `PulseDamage`); a buffed value
   in the game's modified-value colour `#b7f79b`; per-slot hover sharing its
   copy source **verbatim** with the cards (D1 §4 — which is why
   `KokomiRiderTips.PulseBody` grew a creature overload rather than being
   re-typed); layout computed from the live count rather than authored (D1 §5);
   sprite fitted at runtime under the amendment D1 made to the pre-scaled-art
   house rule.

4. **`TrackedDisplayBridge` skeleton** (sprint 2 G1) unchanged: keyed registry
   with `IsInstanceValid` staleness, spawn-into-`CombatVfxContainer` with one
   loud warning per missing scene, `RemoteTransform2D` tracking, **no
   `_Process` polling**, lazy re-Setup on a stale display.

5. **`GaugeBridge`'s spec array and its overhead-row convention** (sprint 2
   C1): a table of specs with `AppliesTo` / `ReadValue`, and rows that mean the
   same thing for every character.

6. **StS2 creature visual invariants, decompile-settled.** The docket is
   overhead, never under the feet: *the band below a creature is
   `NCreatureStateDisplay`'s* — the HP bar spans the full bounds width and
   `NHealthBar.UpdateLayoutForCreatureBounds` pins the block badge to the left
   edge of the 240-wide box. The Salon stage's Encore label was drawn there
   once and simply covered. No facing concept is used or assumed; the display
   is a `RemoteTransform2D` child of the creature node.

7. **Preview purity as a co-op safety rule** (`PreventExhaustWardPower`, the
   2026-07-27 `StateDivergence` disconnect): previews run a different number of
   times on each peer, so a preview may not latch, mutate, or draw from
   `Rng.CombatTargets`. Nothing in `TurnEndAttribution` or the bridge does.

8. **Wiring a pck path ahead of its asset is blessed** (`KleePowerIcons`), but
   **EB-65's failure mode is respected**: a null path there falls through to a
   base getter and renders the red NOPE placeholder. Here there is no base
   getter — an absent file leaves the sprite hidden and the chip still prints
   its number.

9. **Degrade, never take the run down** (`KleePck.Path` returns null on a miss;
   bridges are inert when a node is absent). Missing scene → one warning,
   feature off. Missing node → `GetNodeOrNull`, skip. `NoteFiring` returns
   quietly on every failure path, because it runs inside turn-end resolution.

10. **`NHoverTipSet` keys its live set by owner and ADDS** — so `ShowHover`
    removes first, the bug `SalonVisualsBridge` already ate.

---

## 3. Taste calls made by precedent, reversible

These are the places the spec under-determines a visual choice. Each names the
precedent it copied. **[USER] reviews them from the captures in §6**; every one
is a constant or a scene offset and reverses in one edit.

| # | call | precedent it mirrors | reverse it by |
|---|---|---|---|
| T1 | **Position: a third overhead row at `(0, -380)`, the SAME height for every seat.** | `GaugeBridge`'s C1 convention argument — the −300 slot means "Burst" for everybody and may not be shifted; −340 is Kokomi's Charge; −380 is the next clear band. A per-character height would make a partner's docket something you hunt for. | `TurnEndPreviewBridge.AnchorOffset` |
| T2 | **Overhead rather than beside the creature** (the Salon stage sits low-left). | The decompile-settled invariant that the band below a creature belongs to the state display. Beside-the-creature was available but would collide with the Salon stage on Furina and with targeting arrows generally. | `AnchorOffset` |
| T3 | **Chip, not ribbon.** The number is a small dark chip with an accent edge under the entity. | `SalonVisualsBridge`'s role chip (D1 §2): "glyph answers what does this one do, the number answers how much, right now." The Encore *ribbon* is a runway measuring turns of fuel — there is no fuel here to be a runway of. | scene `Chip*` nodes |
| T4 | **The whole docket disappears when nothing is standing.** | `KokomiRiderTips`'s silence rule: a tip that advertises a window it is not in is noise on 90% of appearances, and noise trains players to stop reading. | `RefreshDisplay`'s `display.Visible` |
| T5 | **A "1" in the turns corner is suppressed; only 2+ prints.** | Same rule. At `KurageDuration 1` every jellyfish would carry a permanent "1" the player cannot act on. | `RefreshSlot`'s `left > 1` |
| T6 | **A small `END OF TURN` header, and no backing plate.** | The gauges are bare (`shared/gauge.tscn` is a track + label); a fixed-width plate would sit mostly empty at one slot. The header only ever appears when the docket does (T4), so it is not permanent chrome. | scene `Header` node |
| T7 | **The row is compacted and centre-justified** — only standing sources get a slot, and the row re-centres. | `SalonVisualsBridge` D1 §5: layout from the live count, so a docket of one does not sit where the leftmost of four sits. | `LayOutSlots` |
| T8 | **Firing is a flash on the existing slot, not a new floating callout.** | `KleeCombatVfx.SpawnSpotlightShine` fires once per funnel with no spam guard needed; and the slot is already the surface the player learned to read. A second surface would have to be re-learned. | scene `fire*` animations |
| T9 | **The volley chips quote the SOURCE number (`4x5`, `8`), not a resolved one.** | There is no target before the turn ends — the volleys pick randomly and `ElementalHit` applies Strength/Weak/Vulnerable per target. The hover says so explicitly rather than the chip implying precision it cannot have. The Kurage chip IS exact, because its only variable is the Charge bank. | `TurnEndAttribution` `Preview`/`Body` |
| T10 | **The Bond-of-Life slot prints what it will actually take (`-3` at 3 Block), not the flat 5.** | Same honesty rule as T9 in the other direction: the constant would promise a payment a 2-Block creature cannot make. | its `Preview` |
| T11 | **The Bake-Kurage silhouette is bell + tapering skirt; the wide translucent side-wings are cut off.** | `cut_salon_members.py`'s Crabaletta note — ship the readable part rather than a polygon that encloses more dark card than creature. Verified by eye at 3× before shipping. | `KURAGE` polygon in `cut_kurage_summon.py` |
| T12 | **Four scene slots, excess logged not hidden.** | `SalonVisualsBridge`'s known-gap rule: nothing today can stand a fifth source, and if one ever can, the log says so instead of it going invisible. | `SceneSlots` |
| T13 | **The redraw funnels live on `TurnEndSequencer` rather than in a new hooks model.** | It already owns the end-of-turn concept and is already registered; a second `AbstractModel` would be one more subscription to keep alive for a display. Both new broadcast tenancies are registered in the co-tenancy ledger with "pure redraw, no ordering stake". | move to a new `AbstractModel` |

**One thing that is NOT a taste call and should not be quietly reverted:** the
docket names Arlecchino's Bond of Life as a fourth source. It is a tenant of
the same sequence and the same shared Block, and leaving it out would make the
docket's account of the turn incomplete in exactly the case (Kokomi +
Arlecchino) where EB-19/races-a says the order matters most.

---

## 4. Sim twin: none owed, and why

**This is presentation-only.** The classification is not asserted, it is
declared where the repo declares such things:

- Every number the docket prints is produced by an accessor the resolution
  already calls; the widget computes nothing the sim does not already compute.
  Nothing it does is visible to the combat model.
- The three constants it adds are geometry, declared in
  `tools/lint_constant_parity.py`'s `UNMIRRORED` alongside
  `SalonVisualsBridge.SceneSlots` / `SpriteScaleMax` / `SlotSpacingMax` and
  `GaugeBridge.BarFullWidth` — the same classification, for the same reason.
- The atlas invariant this rides is **"Visuals read state, never own it"**
  (`klee-mod-runtime.md` §3, `Vfx/GaugeBridge.cs:34-38`).
- `lint_op_parity` is clean and unaffected: no new op, no op pricing change.

**The `TurnEndSequencer` refactor is behaviour-identical.** Each of the four
statements moved verbatim into a `Resolve` delegate — same power type, same
method, same `ToList()` re-read across the await, same per-creature grouping.
The order gate (`test_the_turn_end_sequence_is_the_sims_order`) now reads the
table, and a **new** gate (`test_the_sequencer_walks_the_table`) fails if the
sequencer ever stops walking it — so the pair is strictly stronger than the
single gate it replaces: it now pins the order the player is SHOWN as well as
the order that fires.

---

## 5. Verification run

| check | result |
|---|---|
| `dotnet build -c Debug` (klee-mod/KleeCode) | **succeeded** |
| `dotnet build -c Release` | **succeeded** |
| Harmony bite-check (`klee-mod/build/bitecheck`) | **`14 patch class(es) armed.`** |
| `pytest tier0/tests tier05/tests -q` | **2288 passed, 41 skipped, 12 xfailed** |
| `gen_roster_cards.py --check` | up to date (all three profiles; no generated surface touched) |
| `lint_handwritten_parity` / `lint_constant_parity` / `lint_op_parity` | OK — 73 mirrored, 19 declared unmirrored; 56 ops, 301 cards |
| `lint_pool_membership` / `lint_ancient_coverage` / `lint_roster_registry` / `lint_vendor_pin` | OK |
| `suggest_role_tempo_tags --check` / `lint_role_tempo_coverage --gate` | current; 18 findings against 18 pinned |
| `lint_text_encoding` / `lint_generated_structure` / `art_lint` | 0 undeclared encodings; 209 generated cards clean; plan OK (two pre-existing allowlisted red-pen items) |
| `art_coverage` | 0/274 — the worktree has no art tree, which is the documented worktree condition and what CI sees |
| `card_distinctness_report --gate` | no `game_ref/` in the worktree (expected) |

The gate wall caught three real things on the first run, all now closed: the
order gate reading the old location, two unregistered broadcast tenancies, and
three unclassified constants.

---

## 6. OWED to the next live session — DISCHARGED IN PART 2026-08-08

**§7 below is the live session's record.** Six of the nine captures are taken
and the widget is run-verified; three (`C5`, `C6`, `C7`) are still owed, and one
of them is **structurally unreachable as written** — see §7.4.

The game was owned by another agent when this packet was drafted, so nothing
below was run *then*. `deploy.ps1` has since been invoked; see §7.

### Build steps (main checkout, in order)

1. `tools\build_pck.ps1` — **required**, the pck carries a new scene
   (`shared/turn_end_docket.tscn`) and a new resource
   (`kokomi/summon/bake_kurage.png`). Confirm neither appears in the SKIPPED
   block at the end.
2. `klee-mod\build\deploy.ps1`, then `klee-mod\build\validate.ps1` — S6c is the
   one that matters: it checks C# pck references against the contract, and this
   change adds two.
3. In `godot.log`, confirm the scene telemetry line for
   `shared/turn_end_docket.tscn` reads **found**, with `ChipLabel1` present.

### Captures [USER] needs to judge §3

| # | capture | why |
|---|---|---|
| C1 | Kokomi, jellyfish fielded, mid-turn — **whole creature**, so the docket's height against her rig and against the Burst/Charge gauges is visible. | T1, T2 |
| C2 | The same board after banking Charge — the chip number should have **moved** without a card being played. | the whole Bake-Kurage leg |
| C3 | Kokomi holding **Before Sun and Moon** — the chip should read the AMPED number and render **green**. | closes the legibility gap `KurageAmpPower`'s own summary flagged |
| C4 | Hover over the jellyfish slot — the tip body must be **word-for-word** the paragraph a fielding card prints. | idiom 3 (D1 §4) |
| C5 | Klee with Sparks 'n' Splash up: docket at **turns 3, 2, 1**, then absent. | T5, T12 |
| C6 | **Co-op, both seats on screen, at the moment of end of turn** — the partner's slot flashing as their volley resolves. This is the burst-visibility leg and the only capture that can confirm it. | T8, the second leg |
| C7 | A creature with **all four** sources standing (Kokomi + Arlecchino + a fielded Oz + a Burst), and a creature with exactly one — the row must re-centre between them. | T7 |
| C8 | The docket **absent** on a creature whose end of turn does nothing. | T4 |
| C9 | A Bake-Kurage slot at final render scale, screenshot un-zoomed — does the silhouette read as a jellyfish at glance distance? | T11 |

### Known unknowns a Godot run has to answer

- Whether the docket's hover `Control` fights enemy intents or targeting
  arrows. It sits above the creature rather than inside its bounds, which
  should be better than the Salon stage's position — but `SalonVisualsBridge`
  recorded the same question as unverifiable without a run, and so does this.
- Whether −380 clears every rig at every combat zoom. Both rigs were measured
  for the −300 convention; −380 is inferred from that, not measured.
- Whether four slots plus a header at 46px pitch reads as one row or as clutter
  at combat scale. Only C7 can answer it.

### Then, and only then

`EB-53` can close its two engineering legs, and QUEUE `S4-G14` / `OT-1` — the
Kokomi protocol playtest, whose Q1/Q4 this gates — becomes askable. The
corpse-detonation check (`EB-66`) was sequenced behind a legible end of turn
for the same reason.

---

## 7. Live session record — 2026-08-08

**Build under capture:** package **`0.2-634`**, built and deployed from the main
checkout at `cee2f60` (branch `sitting-prep-2026-08-08`). `validate: OK`, S7
suite included, 272 card images, `klee.pck` 9 094 976 bytes. **No `build_pck`
rerun was needed** — the pck at `cee2f60` already carries both new resources
(`resource=res://shared/turn_end_docket.tscn` and
`resource=res://kokomi/summon/bake_kurage.png` are both in
`klee.pck.contract.txt`; pck build id `20260808-192339+a8e6f38`). Game
`v0.107.1`, mods loaded = 3 (klee, STS2_MCP, STS2AutoSlayMod). Bridge: vendored
STS2MCP pin `55e0648` on `localhost:15526`, deployed at session start and
**removed at teardown**; `steam_appid.txt` created at launch and **removed at
teardown**; the speed override was never enabled, so every frame is the pacing a
player sees.

**Boot telemetry (packet §6 step 3):** `godot.log` reads
`[INFO] [klee] convention scene ok: res://shared/turn_end_docket.tscn
root=Node2D`. The telemetry line reports the ROOT only and never names a child,
so "`ChipLabel1` present" is not a claim this line can carry — the chips were
verified on screen instead (C1/C2/C3).

**Runs:** three, all singleplayer, all dead in act 1 under bot-grade play —
Kokomi `YYR035ECBH` (ascension 3, died floor 6), Klee `GQ0AFG1W7L` (died act 1),
Klee `A5QGDZKHXZ` and `A23BBXC8RH` (burst-farming attempts, died floor 2 and
floor 1). No `?` room was entered blind where another route existed; the four
that were entered were `THIS_OR_THAT`, `SUNKEN_STATUE`,
`WATERLOGGED_SCRIPTORIUM` and `TRASH_HEAP` — **Punch Off was never reached and
the game never hung** (`godot.log` finished the session at 171 KB).

### 7.1 Capture manifest

All in the gitignored `art/eb52_captures/` (the precedent this packet is silent
about — same directory, same reason: Tier F art in a public repo). Every frame
is the game's full 4K screen with the debug corner (build, seed, content hash)
in it.

| # | file | verdict |
|---|---|---|
| C1 | `n1_c1_kokomi_docket_whole_creature.png` (+ `_crop_n1_c1_docket.png`) | **VERIFIED.** Whole creature in frame; the docket sits clear above the Charge (`6`) and Burst (`7/20`) gauges, no collision with the rig, the HP bar or the state display |
| C2 | `n1_c2_chip_moved_after_charge.png` (+ `_crop_n1_c2_chip.png`) | **VERIFIED.** Chip moved `22 → 25` as Charge went `6 → 7`. Honest caveat: the Charge came from Pearl of Wisdom's *exhaust* hook during a card play, not from a play-free source — a play-free Charge gain was never offered |
| C3 | `n1_c3a_chip_unamped.png` / `n1_c3_chip_amped_green.png` | **VERIFIED.** `10` white → `12` in the modified-value green after `Before Sun and Moon`. `n1_extra_chip_two_amps.png` is the two-copy case: chip `14` green while `KurageSummonPower`'s own badge text still says "4 plus 3 per Charge" — i.e. the exact gap `KurageAmpPower` flagged, closed on the chip and still open on the power text |
| C4 | `n1_c4_kurage_slot_hover.png` (+ `_crop_n1_c4_tip.png`) and `n1_c4b_bake_kurage_card_hover.png` | **VERIFIED word-for-word.** Both read "The pulse deals 4 damage plus 3 per Charge you hold, at the END of your turn. You hold N Charge: the next pulse hits for X. Charge banked before the pulse counts, so the number can still move." The docket hover appends "Lasts 1 more turn(s)." — which a card in hand cannot say — and titles itself `Bake-Kurage` where the card tip titles itself `Bake-Kurage pulse` |
| C5 | — | **OWED.** See §7.3 |
| C6 | — | **OWED (co-op).** The solo half of T8 is proven: `n1_c6a_solo_fire_flash_frame.png` / `_decay` / `_after` (frames 3–5 of the 34-frame burst `n1_fire_solo_f000..033.png`, 100 ms pitch) show a bright plate flashing behind the jellyfish slot at the instant the pulse resolves, gone two frames later. Whether the same flash reads over a PARTNER'S creature is untestable in singleplayer |
| C7 | — | **OWED, and unreachable as written.** See §7.4 |
| C8 | `n1_c8_docket_absent_no_sources.png` | **VERIFIED.** Kokomi turn 1, nothing standing: both gauges render and the docket band above them is empty. T4 also confirmed at the other end — the whole docket vanishes the moment the summon wears off (`n1_fire_solo_f006+`) |
| C9 | `n1_c9_kurage_slot_final_scale.png` | **VERIFIED, un-zoomed.** At final render scale the silhouette reads as a jellyfish: dome + bright core + tapering skirt. T11's crop call holds |
| bonus | `n1_bonus_char_select_outlines.png` | The freshly shipped character-icon outlines on the character-select strip: Kokomi's selected icon carries its halo, Furina's and Klee's unselected icons are the greyed variants |
| extra | `n1_extra_shop_screen.png` | The shop screen carrying the `MUSTER` raw-loc-key defect (§7.5) |

### 7.2 Run-verification verdict, per leg

| check | verdict |
|---|---|
| **the docket renders** | **PASS.** Spawns into the combat container, tracks the creature, `END OF TURN` header, one slot, no warning in `godot.log` |
| **the jellyfish renders from the 420×720 art with a live chip** | **PASS.** The cut sprite renders as a standing entity and the chip prints `PulseDamage` exactly: `4 + 3×6 = 22`, `4 + 3×7 = 25`, `4 + 4×2 = 12`, `4 + 5×2 = 14` — four readings, four exact matches, including both amp levels |
| **the four sources fire in `TurnEndAttribution`'s order** | **NOT VERIFIED — not verifiable in the runs played.** Only ever ONE source stood at a time. The order gate is pinned in tests; the *displayed* order was never exercised against two or more live slots. See §7.4 for why this is harder than it looks |
| **burst attribution / countdown / flash over a partner** | **PARTIAL.** The flash mechanism is proven on the owner's own slot (C6 note above). Position-as-attribution and the partner countdown need a second seat and were not reachable — the bridge drives singleplayer only |
| **T5 (a "1" in the turns corner is suppressed)** | **PASS,** unintentionally decisive: `KURAGE_DURATION` is 1, so every jellyfish captured this session was a `1` and none of them printed one |
| **T1/T2 (−380 clears the rig at combat zoom)** | **PASS on Kokomi.** Untested on Furina's rig and on the Salon stage |
| **hover vs enemy intents / targeting arrows** | **NO COLLISION OBSERVED** on the one rig tested. Not a general answer |

### 7.3 Why C5 is still owed

`Sparks 'n' Splash` is granted to hand only when Klee's Burst meter fills at 40,
and the meter **resets to 0 at the start of every fight**. Measured live: an
Elemental Skill pays 4–5, `Imaginary Friend` pays 8 (5 tag + 3 printed), and
`Duck and Cover` pays nothing. Three Klee runs reached **24**, **32** and
**37** of 40 before the run died — the last one three points short, in round 17
of a single fight, at 4 HP. Reaching the Burst is a deck-quality problem, not a
widget problem: it wants a run that survives to draft two or three
skill-tagged cards, which bot-grade play did not deliver in the session's time
box. Nothing about the leg is blocked; it needs one better Klee run.

### 7.4 C7 is not reachable as written, and that is a finding

C7 asks for "a creature with **all four** sources standing (Kokomi + Arlecchino
+ a fielded Oz + a Burst)". The four sources are `MasqueRedDeathPower`
(Arlecchino, a companion card), `SparksNSplashPower` (**Klee's** kit Burst),
`OzSummonPower` (Fischl, a companion card) and `KurageSummonPower`
(**Kokomi's** basic `Bake-Kurage`).

Sparks 'n' Splash is granted only to Klee, and Bake-Kurage is only in Kokomi's
pool. **No single creature can ever hold both**, so the four-slot row cannot be
staged at all — in singleplayer or in co-op. The reachable maximum is **three**:
Masque + Oz + (Kurage on Kokomi, or Sparks on Klee). T12's fourth scene slot is
therefore unreachable by construction rather than merely rare, and the
"does four slots plus a header read as one row or as clutter" question in §6 has
no experiment behind it. Either the capture is re-specified as a three-slot row,
or `SceneSlots` is a deliberate 3+1 headroom decision — a [USER] call, not this
session's.

The three-slot row itself remains capturable; it needs a run that drafts both
companion cards, which the three runs did not offer (the companion channel
rolled Sayu, Gorou, Lynette, Kujou Sara, Dahlia, Barbara, Prune, Shinobu,
Kaeya, Albedo and Sucrose — never Fischl or Arlecchino).

### 7.5 Defects the session caught

One filed to BACKLOG, one fixed in place as hygiene, one observation that is
deliberately filed nowhere.

1. **`EB-67` — Kokomi power/relic icons render the red `NOPE` placeholder.**
   Two instances captured: `Pearl of Wisdom` in the relic strip (character
   select AND in-run, beside a correctly-rendered `Lost Coffer`) and the
   `Bake-Kurage` power badge under Kokomi's HP bar. `KleePck.Path` returns null
   for `kokomi/relics/pearl_of_wisdom.png` — the pck's `kokomi/` block carries
   `model/`, `ui/` and now `summon/`, and **no `relics/` or `powers/` entries at
   all** — so the base getter renders `NOPE`. Exactly `EB-65`'s mechanism, one
   character over. Frames: `n1_bonus_char_select_outlines.png`,
   `n1_c1_kokomi_docket_whole_creature.png`.
2. **Filed nowhere, on purpose:** the companion channel never offered Fischl or
   Arlecchino across three runs (Sayu, Gorou, Lynette, Kujou Sara, Dahlia,
   Barbara, Prune, Shinobu, Kaeya, Albedo, Sucrose did come up). Eleven draws is
   not evidence of anything about a pool, so this is a note about why the
   three-slot capture did not happen, not a defect.
3. **Fixed in place (hygiene, `EB-64`'s shape one key over):**
   `card_keywords.KLEEMOD-MUSTER.title` had no row in `KleeMod.cs`'s keyword
   fallback and shipped as the **raw key**, rendered live as the keyword name on
   `Reinforcements` in a shop (`n1_extra_shop_screen.png`). One dictionary line
   added: `"Muster"`. **Compile-verified only** — the deployed `0.2-634` that
   produced these captures does NOT carry it, deliberately, so the capture build
   and the manifest above stay one artifact.
