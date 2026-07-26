# Pass-3 Ratification — Tier 0 Closeout

From chat-Claude. All three items ruled; Tier 0 is DONE for Klee v0.1. No verification pass this round — the three items are judgment calls sitting on an already-verified trail, and your 8-variant spark investigation is exactly the empirical-trail format that earns trust.

## Item 1 — Demolition 96.8% vs ≤96: RATIFIED, with a process fix.
0.8pt at 400 fights is inside binomial noise (SE ≈ 1.0pt at that winrate). Codify rather than hand-wave: **band checks run at ≥1000 fights**, and the demolition band widens to **85–97**. If it exceeds 97 at 1000 fights, that's real and comes back.

## Item 2 — Spark 56% vs 65–85: RATIFIED as a band revision, 45–65.
Your diagnosis is correct and self-consistent: the 65–85 prediction was measured on the monoculture style round 3 abolished, and your trail (plausible drafts cluster 44–61; removing block riders makes it worse, confirming the block-density mechanism) shows the old band described a deck that shouldn't exist. Revised bands, all plausible-draft basis: **demolition 85–97 (boss specialist), spark 45–65 (act-fight specialist), reaction ≥35 floor.** Design doc updated: matchup texture is now part of each archetype's stated identity.

## Item 3 — Frozen→Vuln overshoot: KEEP 2 STACKS. The framing updates, not the knob.
This is my favorite finding of the entire Tier 0 effort. Reaction at 58% via sustained boss-Vulnerable uptime from the hydro+cryo pair means the archetype found a boss plan through *control* reactions rather than damage ones — which is to say, **the sim independently reinvented Genshin freeze teams**, the actual way reaction comps handle bosses in the source material. That's not an overshoot to correct; that's the design working better than its designer predicted. Two checks before keeping it, both pass: (a) iron-rule audit — sustained Vuln is not laundered persistent amplification; Vulnerable is StS-native, Superconduct already grants it, and the uptime economics (~1 energy per Vuln-turn via applier pairs) sit at Bash-parity, so it's *good*, not degenerate; (b) floors have no ceiling, per your own note. "Co-op-primary, boss-weak" was load-bearing only as a floor justification, and the floors all still hold. New framing (design doc updated): *co-op-primary; solo boss plan = control, not race.*

One watch-item for the C# build: this makes hydro+cryo the premium companion pairing. If Tier 0.5's adaptive drafts show every reaction run converging on xingqiu+kaeya specifically, the diversity lever is buffing the overload/electro-charged routes, not nerfing freeze.

## Process fix (my miss, logged for both of us)
The reaction_burst list existing only in my clone forced you to re-derive it — good recovery, and your 2×Fischl/2×Sizzle tuning improved on my version, but it shouldn't have been necessary. Rule going forward: **any package/config list referenced in a ruling ships verbatim in the handoff doc.** Chat-side artifacts that only exist in a sandbox are not artifacts.

## Closeout
- v0.1 scorecard freezes as the Klee design baseline; regression-lock it.
- `tier05-draft-sim-spec.md` accompanies this doc — M5–M7, the draft-level layer. Sequencing recommendation: **Tier 0.5 M5 before deep C# work** (it re-runs the acceptance grid on emergent decks — cheap insurance before implementation locks the sheet in), but the C# *scaffolding* (character skeleton, pools, module layout from the Downfall template) has no dependency on final numbers and can start in parallel whenever you want a change of pace.
- Standing watch-items entering C#: Vermillion+Durin melt vs the amp cap in real relic contexts (Tier 1), reaction co-op validation (Tier 2, marker already placed), and the freeze-pairing convergence check above (Tier 0.5 M6).

Good work. The distance from "PUNISHER gives the starter a 100% winrate" to "the sim reinvented freeze teams" is the whole story of why we built this thing.
