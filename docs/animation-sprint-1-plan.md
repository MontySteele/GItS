# Animation — Sprint 1 Plan ("Bring Them to Life")

> Verbatim record of the governing sprint doc from the 2026-07-23 planning
> discussion (house rule: no chat-side-only artifacts). Execution log:
> docs/animation-sprint-1-log.md.

Date: 2026-07-23. Inputs: design-chat animation feasibility analysis (this sprint's governing doc), Downfall @ lamali292/Downfall main (reference implementation — clone locally, do not vendor), decompiled game v0.107.1, DECISIONS findings 21/23/27 (CustomCharacterModel base-type law, loc-key prefixing, pool resolution), existing pck pipeline (KleePck.cs + tools/build_pck.ps1, MegaDot editor).

Sprint goal: replace static placeholder character presentation with animated in-combat models and mechanic-bound UI: Klee layered-PNG idle/attack/hurt/death, a shared tracked-gauge scene serving Klee's Burst meter and Furina's Encore gauge, onscreen Salon members for Furina, and per-card bomb/Dodoco VFX for Klee. Spine rigs are explicitly OUT of scope (see Non-goals). No gameplay/sim changes in this sprint — visuals read state; they never own it.

Feasibility basis (verified against both repos, 2026-07-23): every deliverable below has a production precedent in Downfall. Scene binding is convention-based (res://{ModId}/scenes/character/*.tscn, see DownfallCode/Abstract/DownfallCharacterModel.cs). Hexaghost proves the non-Spine animated character (hexaghost2.tscn: TextureRect layers + AnimationPlayer + AnimationTree with idle/attack/hurt/death, driven through NCreatureVisuals + IAnimatedVisuals.OnAnimationTrigger). HexaghostVisualsBridge proves the tracked-mechanic-UI pattern (instantiate scene into NCombatRoom.CombatVfxContainer, Track() to creature node, Refresh() from the command layer). GhostflameModel.SpawnVfx proves the fire-and-forget per-effect VFX recipe. The pck prerequisite is already solved in our tree.

## Ordering law for this sprint

Tracks land in order A → B → C → D → E. A is a proof-of-binding gate: nothing in B–E starts until A's boot telemetry shows the convention scenes loading from our pck. Rationale: every later track ships scenes through the same binding; a silent path miss falls back to static and looks like nothing happened — we prove the channel first, with logging, so later tracks debug their own content instead of the plumbing.

## Track A — Scene binding proof (gate)

- A1. Convention folder. Create klee-mod/Klee/scenes/character/ with a static combat.tscn: Node2D root, script extending the game's NCreatureVisuals, single TextureRect using existing splash art, plus the auxiliary Marker2D/Bounds nodes mirroring Hexaghost's combat.tscn layout (Center, CenterPos, IntentPos, Bounds — copy the node inventory, not the art). Build into klee.pck via tools/build_pck.ps1.
- A2. Model wiring. Override the custom-scene path properties on Klee (CustomCombatScenePath analog — confirm exact override names against decompiled CharacterModel v0.107.1 / BaseLib rather than assuming Downfall's DownfallCharacterModel names; Downfall wraps them in their own abstract). The existing "GenerateAnimator deliberately NOT overridden" comment in Klee.cs must be updated to state the new regime and why.
- A3. Boot telemetry (house pattern, KleePck precedent). One godot.log line per convention scene at load: path, found/missing, and the loaded root node type. A missing scene must log loudly and fall back to base behavior — never throw, never silently no-op. This telemetry is permanent, not scaffolding.
- A4. Gate check. Boot the game, enter combat as Klee, confirm the static scene renders at correct position/scale and telemetry shows pck provenance. Screenshot into the sprint log. Only then open B–E.

## Track B — Klee layered-PNG character (Hexaghost tier)

- B1. Layer cut. From the current Klee splash: body, head, backpack, Dodoco as its own layer (Dodoco bobbing independently is the single cheapest "she's alive" signal we can buy). Export layers at splash resolution; document the cut in docs/art-asset-manifest.md.
- B2. klee2.tscn (name mirrors hexaghost2.tscn): layered TextureRects under a Node2D, AnimationPlayer + AnimationTree with exactly the four states idle, attack, hurt, death (+ RESET). Idle = slow sway + Dodoco bob (loop). Attack = short lunge/recoil. Hurt = flinch + brief tint. Death = fade/slump. Optional GPUParticles2D spark motes on idle, budgeted last.
- B3. Trigger routing. Combat-scene script implements Downfall's IAnimatedVisuals-equivalent surface against our own interface (we do not depend on DownfallCode): OnAnimationTrigger(string) forwards to the AnimationTree. Set AttackAnimDelay / CastAnimDelay on the Klee model to sync damage numbers to the lunge contact frame (Hexaghost ships 0.15f / 0.25f — start there, tune by eye).
- B4. Acceptance. In live combat: idle loops without hitching; playing an attack card fires the lunge with damage synced; taking a hit fires hurt; dying fires death exactly once. No animation plays during non-combat rooms.

## Track C — Shared tracked gauge (Burst meter + Encore)

- C1. One scene, parameterized. gauge.tscn in a shared location: fill bar/orb, label, threshold flash. Exposed knobs: max value, fill color, threshold value, anchor offset relative to tracked creature. Build once; instantiate twice (Klee Burst, Furina Encore). If the energy-orb slot turns out to be the right home for one of them, the convention override scenes/character/energy_counter.tscn is the supported alternative (Downfall precedent incl. energy_vfx_back/front) — decide per-gauge during layout, log the decision.
- C2. Bridge. GaugeBridge static class following HexaghostVisualsBridge line-for-line: Player→display dictionary with IsInstanceValid staleness checks, Setup(combatRoom, player) instantiates into CombatVfxContainer and Track()s the creature node, Refresh(player) re-reads the authoritative value (Burst energy / Encore) and redraws, DiscardDisplay on combat end. Visuals read state only — the gauge is a view of Player fields the command layer already owns; no game state lives in the scene.
- C3. Refresh call sites. Burst: every energy gain/spend/reset path. Encore: gain, spend, absorb, overdraw. Enumerate call sites from the ops that mutate these fields (grep the command layer; list them in the PR description). A missed call site = stale gauge = playtest bug report, so the enumeration is part of review, not optional hygiene.
- C4. Acceptance. Gauges track their creature through position changes, survive room transitions cleanly (no orphaned displays — the staleness dictionary is the regression surface), and visually flash at threshold (Burst ready / Encore empty→overdraw).

## Track D — Onscreen Salon members (Furina)

- D1. salon.tscn. Three member slots flanking Furina (layout mirrors ghostflames.tscn's wheel-around-creature composition; our shape is a flank line, not a wheel). Each slot: portrait, active/inactive state, small state badge. Placeholder portraits acceptable this sprint — the slots and states are the deliverable; art register handles portraits per existing pipeline.
- D2. SalonVisualsBridge. Same bridge skeleton as C2 (consider extracting the common bridge into one generic base after both exist — refactor after the second concrete instance works, not before). Refresh reads Salon membership/state from the Furina command layer.
- D3. State transitions animated minimally: member activate = scale pop + brighten; deactivate = desaturate. AnimationPlayer inside salon.tscn; no per-member scenes yet.
- D4. Acceptance. Salon composition changes in combat are reflected within the same action resolution; displays never survive into the next combat; non-Furina players never spawn the scene (guard mirrors player.Character is not Hexaghost check in the reference bridge).

## Track E — Per-card VFX (bomb lob, Dodoco pop)

- E1. Recipe (GhostflameModel.SpawnVfx precedent). Small PackedScenes, fire-and-forget: instantiate → CombatVfxContainer.AddChildSafely → position at target → self-free on animation end. No bridge, no registry — these are stateless.
- E2. bomb_lob.tscn: arc tween from Klee to target + explosion particles on land. Trigger from the bomb detonation op, synced to the pending-damage badge resolving — the badge shows total pending damage (prior ruling), so the arc-and-detonate is the payoff frame for a number the player has been watching. One VFX per detonation event, not per bomb stack (spam guard).
- E3. dodoco_pop.tscn: short pop/sparkle on Sparks-spend events. Same spam guard: cap concurrent instances (suggest 3) — Sparks can spend in bursts and we will particle-storm the screen otherwise.
- E4. Acceptance. Effects never outlive combat, never leak nodes (verify with remote scene tree after a long fight), and respect the concurrency cap under a worst-case spark-dump turn.

## Non-goals (explicit)

- Spine rigs. MegaDot ships the spine-godot runtime and Champ proves the integration is trivial (champ.tscn is one SpineSprite node), but authoring requires the Spine editor + rigging skill we don't have on the bench. Layered-PNG is the shipping tier; Spine is a future upgrade that slots into the same combat.tscn binding with no code changes. Do not build "Spine-ready" abstractions speculatively.
- selection_screen / merchant / rest-site / card_trail scenes. Same convention slots, pure content; deferred to a polish sprint after the in-combat layer proves out.
- Furina character model animation. Klee first (art layers exist); Furina's combat model gets the B-track treatment next sprint using the scene/script skeleton B produces.
- Any gameplay, sim, or sheet change. If a Refresh call site is missing because an op doesn't emit a usable event, add the event, not gauge logic inside the op. Flag cross-cutting event additions in the shared-loader/cross-session note per standing rule.

## Gates & rulings

- Track A completion is a hard gate on B–E (see Ordering law).
- [USER] gate: final look approval of B (Klee motion), D (Salon layout/composition), and E timing feel. Ship behind the existing playtest flow; screenshots + a short capture clip per track in the sprint log for the eyes-on pass. Per standing rule, only the user closes [USER]-gated items.
- Naming/lore check (standing rule): scene and node names are internal, but any player-visible label on gauges/Salon UI goes through the lore/naming audit before ship.
- License note: Downfall is reference-reading only. Patterns and node inventories may be mirrored; do not copy scene files, art, or code verbatim into our tree. Record this in DECISIONS.md when the sprint opens.

## Risks & mitigations

- Override-name drift. Downfall's path properties live on their abstract (DownfallCharacterModel), wrapping base-game virtuals whose exact names we must confirm in decompiled v0.107.1. Mitigation: A2 verifies against the decompile, and A3's telemetry catches a bad bind at boot rather than mid-run. (This is the finding-21 lesson again: wrong-but-compiling base wiring fails silently.)
- pck staleness during iteration. Scene edits require an editor re-export; a stale pck silently shows old art. Mitigation: build_pck.ps1 stamps a build id into the pck; A3 telemetry logs it at boot.
- Per-frame cost. All new displays are event-driven (Refresh on mutation), never _Process polling — same reason KleeArt caches textures: these surfaces sit on hot UI paths.
- Bridge divergence. Two hand-rolled bridges (C2, D2) will drift. Mitigation: the post-hoc extraction in D2 is a named cleanup item, and a lint-shaped check (grep for IsInstanceValid + dictionary pattern) can be minted if a third bridge ever appears — catch → lint, per house pattern.

## Definition of done

Klee visibly idles, lunges, flinches, and dies; her Burst gauge and bomb/Dodoco VFX read correctly in a full act-1 fight with no leaked nodes. Furina shows her Salon flank and Encore gauge with correct state through a full combat. All convention scenes log pck provenance at boot. [USER] look-approval items are open in the sprint log with captures attached.
