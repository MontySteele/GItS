# Bot Playtest Apparatus — Kickoff Brief ("Understudy")

For: local Code agent. From: chat session 2026-08-04. Status: PROPOSED.
Worktree-per-session (G4). Suite green at every phase boundary. New mod
component — cross-session note required before anything touches shared
schema (none expected in P0/P1).

## Purpose

Move jank-filtering off [USER]'s play hours. Scripted bots soak new builds
overnight through the REAL game (not the tier-0.5 sim); LLM tiers add
judgment sparingly; [USER]'s table time becomes design evaluation only.
Secondary purpose, ledger-level: this creates a third C#-side instrument
class (D4 currently allows only pins and play). "Bot play" becomes
registrable for mod-side predictions once P1 is validated.

## P0 — Evaluate existing bridges (build nothing yet)

Three community artifacts to evaluate against a GItS build, in order:

1. State/action bridge: the community mod exposing STS2 game state and
   operations as a local HTTP API / MCP server (found via GitHub
   slay-the-spire-2 topic; identify the repo, pin the version). Also
   evaluate the Nexus "STS2 Modding Assistant MCP" (mod 345) for overlap.
2. Multi-client: LocalCoop (github.com/Bahnerbd/STS2CouchCoop, Nexus mod
   1314) — multi-instance launcher + loopback broker bridging native
   multiplayer traffic. Alpha, v0.103.3-era, Windows x64.
3. Speed: whatever headless / animation-skip / turbo affordances exist
   (engine flags, the toolkit mod's debug hooks, or Harmony-patch the
   animation timers ourselves).

P0 acceptance questions (stop-and-surface on each):

- Does the state bridge expose MODDED content (GItS cards/powers/summons)
  or only base-game vocabulary? If schema-driven, what do our custom ops
  look like on the wire?
- Can it INJECT actions (play card X targeting Y, choose reward, pick
  path), or is it read-only? Read-only → we fork and add injection.
- Does LocalCoop boot 2 clients with GItS + the bridge loaded, and does a
  bot-driven client work with no controller attached?
- Fallback if bridges are unusable: write our own bridge component inside
  GItS (Harmony hooks on the action queue + JSON state dump + local HTTP).
  Downfall repo for architecture reference. Estimate before building.

P0 deliverable: a findings doc with a BUILD / FORK / ADOPT ruling proposal
per artifact. No ruling is self-issued — [USER] countersigns direction.

## Phase 0 measurement — pre-registered (D4-compliant)

Protocol ([USER]-approved in session):

1. Code agent (Opus) ports tier05 pilot heuristics to the bridge protocol
   → understudy/policy_v0. Deterministic, seeded, logs every decision.
2. Opus plays ONE full solo run through the bridge, making every decision
   itself. Harness logs per decision: tokens in/out, wall-clock, chosen
   action, AND policy_v0's counterfactual action at the same state.
3. Divergence report, categorized: draft picks / targeting / sequencing /
   resource timing / path choice. Opus proposes policy_v1 revisions ONLY
   for divergence classes that look like judgment, not noise. Revisions
   are listed with rationale; [USER] skims before soak (cheap gate — this
   is the "what did I do vs what did my policy do" review).

Pre-registered predictions. Instrument: the Phase-0 logs themselves.

- M1: tokens/decision and decisions/run — MEASUREMENT, no prediction;
  these two numbers SET the Phase-2 tier boundaries (they are why this
  run exists).
- M2: policy_v0 agrees with Opus on >60% of decisions by count, with
  disagreement concentrated in draft picks. If agreement is far lower,
  the pilot port is buggy before it is dumb — debug first, revise second.
- M3: one full LLM-driven run completes in a single Code session without
  hitting usage limits. If false, Phase 2's sampled-decision tier drops
  to draft-picks-only by default.

## P1 — Soak harness (the burnout killer)

- understudy/soak.py: N seeded solo runs of policy_v1 through the real
  game, animation-accelerated. Per-fight telemetry (damage by source, HP
  trajectory, incoming attacks/turn, cards played, turn count) to local
  JSONL — this is the same telemetry surface Track B wants; share the
  schema, write the cross-session note if Track B has started.
- Crash/softlock/NRE detection: process watchdog + state-progress timeout.
  Any hang or exception = a filed defect with seed + state dump. THIS is
  the acceptance bar for P1: a broken build is caught by the soak, not by
  [USER]'s evening.
- Morning report generator (no LLM required for v1): defects first, then
  outlier runs, then aggregate curves. LLM-written narrative reports are
  Phase 2.
- New stochastic surface → dedicated RNG stream (standing rule). Policy
  seeds never share a stream with game seeds.

## P2 (deferred) — LLM tiers

Sampled decisions (Haiku/Sonnet per M1 economics; draft picks first) and
batch-telemetry narrative reports. Not designed further until M1 exists.

## P3 (deferred) — Two-seat co-op soak

Gated on P0's LocalCoop findings. If viable: the first-ever automated
co-op instrument; support cells and party-curve claims become gradeable
without booking the table. Design after P1 is stable.

## Non-goals (hard)

- No balance conclusions from bot winrates: every number produced is a
  bot-limited floor (Guardrail-7 discipline, same as pilot-limited).
- Bots file defects and telemetry; they author NO design decisions.
- No fun/legibility claims from bots ever — JSON-state agents cannot see
  the screen; that instrument remains [USER]-only.
- Nothing here touches the tier-0.5 sim, the drafter, or any sheet.

## Stop-and-surface

Bridge mods requiring game-version pins that conflict with the current
GItS build target; any Steam-networking dependency that loopback cannot
bypass; any P0 finding that makes "write our own bridge" the cheaper path
(estimate, surface, wait).
