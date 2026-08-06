# Animation — Sprint 2 Plan ("Furina Takes the Stage")

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

> Verbatim record of the governing sprint doc from the 2026-07-24 planning
> discussion (house rule: no chat-side-only artifacts). Execution log:
> docs/animation-sprint-2-log.md. Predecessor: docs/archive/animation-sprint-1-plan.md
> (architecture now in production) + docs/archive/animation-sprint-1-log.md (CLOSED
> 2026-07-24).

Date: 2026-07-24. Inputs: animation-sprint-1-plan.md + animation-sprint-1-log.md (architecture now in production), the 2026-07-24 [USER] look-pass verdicts (recorded below as CLOSED inputs, not open questions), user-supplied Furina full-body art (design chat, 2026-07-24 — 227×440 preview; see B1 on sourcing the full-res original), Furina kit redesign IN FLIGHT in a parallel stream (see Funnel Contract).

Sprint goal: Furina's visual layer reaches Klee parity and then her own identity: recut character model on properly centered full-body art with a theatrical layered rig; Salon members rebuilt as silhouette-first mini-sprites on a stage assembly that absorbs the Encore gauge; the overhead gauge slot standardized as the cross-character Burst position with per-character skins; Furina's badge strip decluttered with her own icon set. Plus one Klee stretch item (spark motes). No kit mechanics change in this sprint; visuals read state.

## Look-pass verdicts (2026-07-24) — CLOSED, these are law for this sprint

- **B4 / E4 (Klee motion, VFX timing): APPROVED.** Close in the sprint-1 log with this date. One deferred nice-to-have extracted as Track F2.
- **D4 (Salon): FAILED as styled, concept partially validated.** Card-art portraits in framed squares are too indistinct to carry identity. Ghost-frames-for-empty DID read and survives into the redesign.
- **C4 Encore (gauge): FAILED placement.** Upper-left overhead collides conceptually with Klee's Burst position. Ruling: overhead = COMMON Burst indicator across characters; Encore relocates (Track D integrates it into the Salon stage).
- **Badges: FAILED legibility.** Furina's status-strip badges borrow Klee-register icons and there are too many of them. Track E.
- **Character art: REPLACE.** Current model + select art are off-center. New source: the user-supplied full-body render (this doc's governing art input). Selection criterion for any further candidates remains separability-for-layer-cut alongside taste, but the pick is made.
- **Gauge skins: unique per character** (not one shared look).
- **UI overhaul scope: re-layout approved, not just restyle** — the stage concept below was pitched and accepted in design chat.

## Funnel Contract (kit redesign is live — this is the interface freeze)

Ratified safe by [USER] 2026-07-24. Visuals may bind ONLY to:

1. **Salon = exactly three slots.** Deploy is BY CARD and duplicates are legal (three of the same member is a valid stage). Therefore the UI is slot-INDEX-keyed with per-slot member identity read from state — no assumption of in-order deploy, no assumption of distinct members. (This retires sprint-1 D1's fixed member→slot portrait assignment.)
2. **Encore absorbs damage before HP** (gain/spend/absorb funnels in FurinaResources.cs remain the mutation surface).
3. **Spotlight is a designation event** (single designation funnel).

Anything else in Furina's kit is OUT OF CONTRACT and may change under the redesign without visual-layer breakage. If the redesign stream needs to move any of the three contracted points, that is a shared-surface change: cross-session note BEFORE landing, per standing rule. Write this contract into DECISIONS.md at sprint open and drop the note pointer in the Furina stream's channel.

## Ordering law

A (ledger + contract + art intake) → B (model) and C (gauge re-layout) in either order or parallel → D (stage, consumes C's Encore relocation) → E (badges) → F (VFX + stretch). D depends on C only for the Encore ribbon; D's sprite work can start once A's member-art intake clears. The sprint-1 bridge-extraction debt item unlocks NOW (second bridge survived its playtest, even though the styling failed — the plumbing passed: tracking, staleness, spawn guards all held) and is scheduled as G.

## Track A — Ledger, contract, art intake

- **A1.** Close B4/E4 in animation-sprint-1-log.md (verdict + date); record D4/C4-Encore/badge verdicts there with a pointer here. Attach the Klee capture(s) if any exist; if none were taken, note "approved live, no capture" — do not backfill.
- **A2.** DECISIONS.md: Funnel Contract entry + cross-session note to the redesign stream.
- **A3.** Art intake. (a) Resolve the user-supplied Furina render to its canonical full-resolution source for the SOURCES.tsv ledger (the supplied file is a 227×440 preview — the cut needs the full-res original; same provenance discipline as every prior asset, F/high). (b) Pull candidate renders for the three Salon members (Gentilhomme Usher / Surintendante Chevalmarin / Mademoiselle Crabaletta) — full-body creature renders, NOT card-art crops; the redesign's entire premise is silhouette legibility. Contact sheet to [USER] for the pick (art picks stay [USER]-gated).

## Track B — Furina model rebuild (new art, layered rig)

- **B1.** Recut on the new render. Generalize the cutter first: `tools/cut_combat_layers.py` with per-character fence-config files (Klee's fences become config #1; Kokomi's kickoff is already in the tree, making this the third-instance-incoming signal — generalize now, per house pattern). Furina layer proposal (validate against the full-res alpha; her render is a clean cutout, so expect fence work to dominate and the free-floater pass to find little): coat-back / sword / body / hat (z back→front). The glowing blade at her side is the Dodoco-analog — an independently moving accent that sells "alive" cheapest. Ahoge rides the hat layer or body; decide at the fence, not in this doc.
- **B2.** `combat.tscn` in pck-src (`furina/model/combat.tscn`), migrating her OFF the build_pck.ps1 heredoc channel (delete the heredocs; the static `combat_visuals.tscn` and `combat_model.png` PNG path in `Furina.CreateCustomVisuals` become the loud-fallback chain exactly as Klee.cs ships). Registry gets her path; the animation router is already character-agnostic and needs ZERO changes (sprint-1 architecture paying out).
- **B3.** Motion identity — theatrical, not bouncy. idle ~3.5s loop: poised sway, hat micro-tilt, sword glow-pulse + slight drift, coat-back counter-sway. attack: flourish lunge (contact at AttackAnimDelay — start at Klee's 0.15f, tune). hurt: recoil + hydro-blue flash on Body only (NOT Klee's red). death: stage-exit — fade with a slight bow/fall, terminal, no auto-return.
- **B4.** Re-centered stills from the same render: select portrait, locked portrait, char-select backdrop framing, rest/merchant scenes (static body layer now; gentle idle is F-track stretch). This closes the off-center complaint at every surface, not just combat.
- **B5.** [USER] motion look pass (same protocol as Klee's B4).

## Track C — Gauge re-layout + per-character skins

- **C1.** Overhead slot = Burst, everywhere. Klee's Burst stays at its C4-fixed centered-overhead anchor. Furina's Burst meter gets a gauge at the same creature-space slot (her rig's height measured post-B2, same clearance method as Klee's smoke-top measurement). Encore's overhead instantiation is REMOVED (relocates in D).
- **C2.** Skins under the script-less constraint. `gauge.tscn` stays one scene; GaugeSpec grows skin parameters the bridge applies at Setup (textures/nine-patch styleboxes/colors, per character). Klee skin: fuse-and-bomb (fill burns toward a bomb cap = Burst ready). Furina skin: hydro ribbon/banner treatment shared with the D-track stage ribbon so the visual language matches. If parameter-driven skinning fights the scene format, the sanctioned fallback is per-character scene variants (`gauge_klee.tscn` / `gauge_furina.tscn`) — same bridge, path chosen by spec; note the decision either way.
- **C3.** Refresh funnels unchanged (contract §2; Burst funnels already enumerated in sprint 1). Acceptance: both characters, overhead Burst reads identically positioned; no Encore display anywhere until D lands.

## Track D — Salon stage (the D4 redesign)

- **D1.** `salon_stage.tscn` replaces `salon.tscn`: a shallow stage arc beside Furina (side per layout pass), three slot POSITIONS on the arc, each holding a freestanding member mini-sprite — full silhouette, no frame, no square crop. Slot-index-keyed per the contract; duplicates render as duplicates. Empty slot = ghost outline on the stage floor (the surviving sprint-1 idea, restyled to the stage language).
- **D2.** States. Active member: spotlight pool (soft ellipse + subtle beam) under the sprite. Dry (Encore below tick cost): pool dims, sprite desaturates — same semantics as sprint 1, silhouette-first rendering. Deploy: per-slot pop; the sprint-1 cascade queue survives (one AnimationPlayer, queued pops).
- **D3.** Encore ribbon. The Encore gauge lives beneath the stage arc as a horizontal ribbon fill (C2's Furina skin): members visibly stand ON their fuel. Overdraw moment (drain to 0) plays the flash pulse + the whole stage dims — the causality the old layout could not show. Refresh funnels: contract §2 trio + the meter-sync site from sprint 1.
- **D4.** Bridge update. `SalonVisualsBridge` reworked for slot-indexed identity + ribbon; still GaugeBridge-skeleton, still RemoteTransform2D tracking, still the `NCombatUi.Activate` postfix. Non-Furina guard stays.
- **D5.** [USER] layout/composition pass — explicitly re-opened since D4 failed; silhouette legibility at glance distance is the acceptance question. **Capture required this time.**

## Track E — Badge diet + Furina icon register

- **E1.** Inventory. Enumerate every Furina-applied power badge and its current icon source. Classify: (a) has an ambient home after C/D (Encore → ribbon, Salon states → stage) → RETIRE, Burst-badge precedent, save-compat pattern already established; (b) no ambient home (Fanfare and whatever the redesign keeps) → KEEP with a Furina-register icon.
- **E2.** Icon set for the keepers: her own register (hydro/theater language), through the existing art pipeline + register rules; no Klee-register borrowing anywhere in her strip. Icon picks ride the standard art register flow.
- **E3.** Acceptance: her strip in a busy turn is glanceable — count after diet recorded in the log; naming/lore audit for anything player-visible, per standing rule.

## Track F — VFX + stretch

- **F1.** `spotlight_shine.tscn`: beam-from-above on the Spotlight DESIGNATION event (contract §3) — the kit's signature moment currently has zero visual. Self-freeing scene, sprint-1 E-recipe verbatim.
- **F2.** (stretch, [USER]-flagged nice-to-have) Klee spark motes: spark count as literal sparks above Klee's head — small pooled sprite row, count-driven from the Sparks funnel, replacing nothing (numbers stay wherever they live today). Only if tracks A–E are green.
- **F3.** (stretch) rest/merchant gentle idles for both characters.

## Track G — Sprint-1 debt (now unlocked)

> **IDENTIFIER NOTE, 2026-08-06 (housekeeping sweep, Track X).** This plan's
> task-ids are the **animation sprint 2** mint: qualified forms `AS2-A1`…`AS2-G2`.
> `AS2-G1`/`AS2-G2` below are not S4's `S4-G1`/`S4-G2` and not Curtain Call's
> `CC-G1`/`CC-G2`; `AS2-D5` (the layout pass) is not the DECISIONS D-series
> `DEC-D5` (Kokomi stability band). Resolver: `docs/registry/identifiers.md`
> §2.1 and §2.2.

- **G1.** Extract the common bridge base (GaugeBridge + SalonVisualsBridge → one skeleton) — D4's plumbing survived its playtest, which was the ratified trigger; do it AFTER D4's rework lands so the extraction covers the new shape, not the dead one.
- **G2.** Rename `KleeAnimationRouter` to its true generic scope (`AnimationRouter` or `CreatureAnimationRouter`); comment updated to state it serves every modded creature with an `%AnimationTree`.

## Non-goals

- Kit mechanics, numbers, or any funnel beyond the contract trio.
- Kokomi visuals (but B1's cutter generalization and C2's skin machinery are built expecting her).
- Spine (unchanged verdict from sprint 1).
- Klee model/VFX changes beyond F2 (his layer is approved and frozen).

## Gates & rulings

- [USER] gates: A3b member-art pick; B5 motion; D5 stage layout (capture mandatory); E2 icon picks; F2 is [USER]-optional by origin.
- Funnel Contract breach = stop-work on the affected track + cross-session note; visuals never chase an unlanded kit change.
- Downfall remains reference-reading only (standing license note).

## Risks & mitigations

- **Kit redesign drift** — the top risk this sprint. Mitigation: the contract freeze + the rule that visuals bind to funnels, not values; anything out-of-contract that badges depended on gets caught in E1's inventory rather than assumed.
- **Full-res art availability (A3a).** The supplied render is a preview; if no full-res canonical source resolves, the cut quality caps out and [USER] picks between accepting softness or choosing a different render. Surface this at intake, not mid-cut.
- **Duplicate-member rendering was never exercised** (old UI assumed distinct members). D acceptance must include a three-of-one-member stage on purpose.
- **Skin-parameter ceiling (C2):** script-less scenes limit what a spec can restyle; the scene-variant fallback is pre-authorized to prevent mid-track architecture debates.
- **Stage width vs. combat layout:** a three-sprite arc + ribbon is wider than the old flank; verify against enemy intent positions and targeting arrows before D5, not during it.

## Definition of done

Furina enters combat centered, layered, and moving with theatrical identity; her Burst sits in the standardized overhead slot in her own skin; the Salon stage reads member identity by silhouette at a glance, shows dry/active/empty states, and carries the Encore ribbon whose drain visibly dims the stage; her badge strip is dieted to keepers with her own icons; Spotlight designation has its beam. Klee is untouched except (stretch) spark motes. Contract recorded, debt items G1/G2 closed, [USER] captures attached for B5 and D5.
