# C-Milestones — Klee In-Game Build Spec (Boots → Playtest Slice)

**Audience:** Claude (in Claude Code), running ON THE USER'S MACHINE with access rights to triage and debug setup issues directly. That changes the rules from the sim work: you're touching a real Steam install and real save data now. Read §0 before running anything.

---

## 0. Commentary + local-machine safety rails

You're no longer in a disposable sandbox. Non-negotiables:
1. **Back up saves before the first modded boot.** StS2 keeps modded and unmodded saves separate (`%APPDATA%\SlayTheSpire2\<store>\<id>\` with a `modded` subfolder; macOS under `~/Library/Application Support/`). Copy the whole profile tree to a dated backup dir first — a Workshop commenter lost progress to exactly this, and "the mod ate my saves" is not a bug report we want from our own user.
2. **Pin the game version if Steam allows a beta branch; record the exact build in DECISIONS.md.** EA patch churn is the #1 schedule risk; a mid-cycle game update that breaks the build should be a *known event*, not a mystery.
3. **Never commit machine-local files:** `local.props`, extracted game assets, decompiled sources (`sts2_decompiled/`), anything under the Steam dir. Extend .gitignore before first commit. Decompiled base-game code is reference-only and stays out of the repo entirely.
4. Ask the user before anything destructive or account-touching (Steam operations, deleting dirs outside the repo). Routine build/debug within the project: just proceed — that's the access grant.

Design inputs are frozen upstream: sheet v0.3.1, principles v1.5 (Frozen v2 table), round-3/errata rulings. If implementation reality contradicts a design doc, that's a finding for chat triage, not a local edit.

## C1 — "Boots" (target: modded game launches with a selectable blank Klee)
1. Install/verify: StS2, MegaDot v4.5.1 (megadot.megacrit.com), .NET 9 SDK, GDRE (gdsdecomp) for base-asset extraction.
2. Clone the Downfall fork (lamali292/Downfall) as the structural template; run their documented flow: `local.props` from example → `build/link-assets.ps1` → `build/setup.ps1` → `dotnet publish` (macOS/Linux: the ps1 scripts have thin logic — port if needed; jiegec/STS2FirstMod is the minimal fallback template if the big fork misbehaves).
3. **Prove the template builds unmodified first.** Do not strip anything until stock Downfall compiles, packs, and loads. This isolates "environment problem" from "our problem" forever after.
4. Strip to a single module: new `Klee/` + `KleeCode/` following the Hexaghost layout (it's the completed reference). Character class per the Downfall `Hexaghost.cs` pattern: HP 62, colors (Klee red #E85A4F-ish, artist's call later), starting deck = 4× Kaboom / 4× Duck and Cover / Jumpy Dumpty / Pop as reskinned strike/defend stubs, placeholder select art (programmatic colored frame + name).
5. Acceptance: game boots modded, Klee appears in character select, a fight starts and completes with the stub starter deck. Commit as `c1-boots`.

## Spikes — run BOTH before any systems work; each is ≤2 sessions, findings to chat either way
**S1 — Damage-pipeline hook (the reaction resolver's home).**
Question: where's the clean interception point for "damage event with element tag → check target aura → modify amount / append effects"? Method: decompile the game dll with ilspycmd (auto-spire precedent: ~3,300 files; start in `MegaCrit.Sts2.Core.Combat` and the damage/`Commands` flow), then look at how Downfall's powers modify damage (their `MetallicizePower`, Champ's stance mods). Success: a proof-of-concept Harmony patch or hook where a test attack against a test-aura enemy deals ×1.5 and clears the aura, correctly ordered w.r.t. Strength/Vulnerable. **Fallback if no clean central hook:** invert ownership — auras become self-managing enemy powers using the standard `on_take_damage` power hook (Downfall proves those exist); resolver logic lives in the aura power. Slightly uglier, fully sufficient.
**S2 — Reward-screen companion slot.**
Question: can the card-reward screen take a 4th, visually distinct, separately-pooled offer? Method: find reward generation in decompiled source; check whether Downfall or BaseLib already patches reward contents anywhere. Success: any fight reward showing 3 normal cards + 1 companion-pool card with our weighting. **Fallback:** companion acquisition via shop integration (Pengo's Tarot pack proves shop-draw UI is fully moddable) and/or an event-style offer; the reward slot then becomes a v0.2 goal rather than a blocker.
Everything downstream re-plans on spike results; that's why they're first.

## C2 — "Slice" (target: THE PLAYTEST BUILD)
**Systems, in dependency order, every effect through the multiplayer-safe Cmd APIs** (`MegaCrit.Sts2.Core.GameActions.Multiplayer`, `PlayerChoiceContext` — Downfall's pattern everywhere; co-op is the actual use case and retrofitting sync is the classic mod death-march):
1. Aura powers (6) + reaction resolver per principles v1.5 — **Frozen v2**: −50% next action + Shatter (first attack vs Frozen: +6, removes it); boss Frozen → Vulnerable 2. Amp cap assertion from the sim carries over as a debug-log warning.
2. Bombs: enemy-side power; start-of-owner-turn detonation + attack-triggered early pop; detonation event bus (Pounding Surprise and Blazing Delight subscribe).
3. Sparks: player counter + the at-3-next-attack-free cost hook; Pounding Surprise starting relic.
4. Burst meter: counter power MVP (+5 on skill_tag, +5 per reaction), Sparks 'n' Splash gated on it, Retain flag per principles v1.4. Custom UI later; a number is fine for playtesting.
5. Companion pool: colorless-style `CustomCardPoolModel`, S2's acquisition path, nation-weighting constant (inert at single nation, mechanism present).
**Slice card list (31 + 7 companions + 1 relic)** — enough to feel every loop, nothing more:
- Starter: kaboom, duck_and_cover, jumpy_dumpty, pop
- Demolition: mine_toss, fish_flavored_bait, quick_fuse, ammo_scavenging, bomb_voyage, big_badda_boom, blast_radius, sorry_jean, remote_detonator, explosives_workshop
- Spark: sparkly_treasure, pocket_fireworks, crackle, spark_collection, skip_and_hop, rapid_fire, eager_to_help, cant_catch_me, endless_fireworks, gleeful_barrage
- Reaction: sizzle, combustion_study, perfect_timing, boom_goes_the_dynamite (v0.3 rework), flame_dance
- Rares: sparks_n_splash, blazing_delight
- Generic block: hide_and_seek, spirited_away
- Companions: xingqiu_raincutter, fischl_nightrider, kaeya_frostgnaw, sucrose_gust, bennett_passion, barbara_melody (Exhaust, v0.3.1), prune_witch_hunt
- Relic: pounding_surprise
**Codegen (build it during C2, not after):** emitter script reading the canonical YAML sheets → C# card classes for the mechanical 60% (damage/block/bomb/spark/draw combinations map straight onto the 20-line Downfall card pattern) + localization JSON for all cards. Hand-finish conditionals, companion ops, power rares. Generated files carry a DO-NOT-EDIT header; hand-finished ones are listed in a manifest. The sheet stays the single source of truth through implementation.
**Telemetry (in the slice from day one):** JSON-lines per fight to a local log — per-fight: reactions by type, detonations, sparks gained/spent, burst energy at end, burst cast y/n, damage by source category, HP delta, turns. Plus an `analyze.py` that aggregates a play session and prints the comparison against Tier 0's frozen predictions (reactions/fight, reaction damage share, burst cast rate). This is the first real sim-vs-reality calibration and directly prices how much to trust the harness for Furina.
Acceptance: full solo run start→boss with the slice, no crashes, telemetry captured, companion slot (or fallback path) functional. Commit `c2-slice`, tag a build for the user.

## C3 — Full pool: codegen the remaining ~44 cards, remaining companions incl. the three 5-star Rares, character relics/potions v0.1, signature-companion event (or defer per S2 findings), full localization, AutoSlay soak (Nexus STS2AutoSlayMod) — hundreds of automated runs hunting crashes before humans do.
## C4 — Co-op hardening: 2-player sessions with the user's group; desync/replication bug hunt (Cmd discipline should prevent most; the hunt finds the rest); cross-player reaction credit verified live; duration honestly unestimatable — it's done when their game night doesn't crash.

## Playtest checklist (each observation maps to the premise it validates)
| Session observation | Premise under test |
|---|---|
| Does place→detonate feel like a satisfying rhythm or homework? | Demolition's setup/payoff loop (Tier 0 could only prove it wins, not that it's fun) |
| Does the first Vaporize read as an earned spike? | Reactions-are-earned (Pillar 2) as *experience*, not just mechanics |
| "Ooh, Xingqiu" moment at the companion slot? | Companion pool as excitement generator vs noise |
| Do free Spark attacks feel like flow or like bookkeeping? | Spark economy legibility |
| Is Burst charge visible/anticipated without real UI? | Whether C3 needs the meter UI urgently |
| Do you *notice* being fragile (62 HP) during act play? | Run-level fragility (the thing no fight metric could express) |
| Telemetry vs Tier 0 deltas | Global sim trust level for Furina's design cycle |

## Standing risks
Game-patch churn (pinned version mitigates; expect one forced rebase anyway), BaseLib API drift, S1/S2 spike failure (fallbacks above), Workshop-publish IP posture (private builds only until the art pass — principles §9).
