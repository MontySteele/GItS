# Countersign Package — Track A Null Direction + Tag Review (A-G1)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Filed verbatim, as signed.** House convention for a signed package (cf.
`docs/a2-gate-ratification-2026-07-27.md`): the text [USER] signed is committed
unedited, and the repo's own commentary lives elsewhere — the R-numbers in
`tier0/DECISIONS.md` (R90/R91/R92), the execution record in
`docs/sprint-axis-validity-track-a-log-2026-08-04.md`. Nothing below this
heading was written by Code.

---

Countersign Package — Track A Null Direction + Tag Review (A-G1)

Date: 2026-08-04. One sitting closes everything in this file. How to use it: read top to bottom, edit anything you disagree with, then sign at the bottom. Each item says what it decides and what happens next. R-numbers get assigned when this lands in DECISIONS.md.

Ruling 1 — What the P1 null means, and what we do about it

Background, in one paragraph. The coverage lint's first run was predicted to fail Furina's fanfare cells. It didn't — Furina passed everything, while Klee and Kokomi failed 30 cells. Per the charter, that null was binding: work stopped and the branch is waiting on a direction. The diagnosis: the playtest found a size and timing problem ("Fanfare is too slow early and too small late"), but the lint can only count cards. The Fanfare payoff cards exist — they just pay too little. We tested a size problem with a counting tool. That was a mistake in how the prediction was registered, not a flaw in the taxonomy: the same tool correctly found 30 real gaps in the other two pools.

The ruling, in three parts:

1a. The coverage lint stays, as a counting tool. Its job is to answer "does a card for this job exist at this point in the fight?" — nothing more. The 30 Klee/Kokomi findings are real and stay pinned in the debt list. The debt list is deleted once those gaps are addressed in the reworks; until then, the lint fails only on NEW findings.

1b. The Fanfare question moves to Track B, where it belongs. Track B measures how much damage and block each archetype actually produces per turn, against how much the game demands per turn. That is the tool that can see "too slow early, too small late." The prediction is re-registered there, in the same words as the playtest verdict. P1's record in the ledger reads: "prediction aimed at the wrong instrument; withdrawn and re-registered, not failed."

1c. The floors are re-derived from fair comparisons. Today's floors compare a GItS archetype (11–32 cards, all aimed at one plan) against a whole canon character (88 cards spread across everything). That's why Furina cleared some floors by 40+ points — the bar was set from the wrong population. Fix: derive floors from canon packages instead — Silent's poison cards, Defect's orb cards, Necrobinder's summon cards. An archetype gets compared to the canon thing that is shaped like it. The extractor already has the data to do this.

What happens next: Code repairs the branch under 1c, re-runs the lint, refreshes the debt list, and merges. No balance number moves. No card changes. Estimated scope: floors file + one derivation function + a re-run.

Ruling 2 — The tag review (A-G1), four decisions

These close the review column so tags can land on the sheets.

2a. The seven entity payoff lines — confirm or edit each. These say what each summoned thing actually does, which decides what the card that summons it gets credit for. Machine-proposed; your call:

entity	proposed payoff	plain meaning
Salon: Chevalmarin	sustain	she heals
Salon: Crabaletta	frontload	she hits
Salon: Usher	block	he shields
Klee's bomb	frontload (mid/late)	it explodes, later
Klee's spark	frontload + velocity	small hit + feeds economy
Bake-Kurage	block, frontload, scaling	jellyfish does all three
Spotlight	scaling (mid/late)	designated target takes more

Recommendation: these match the sheets' own text; confirm as-is unless one reads lore-wrong to you.

2b. Salon member double-credit — KEEP, with one amendment. Deploying a member creates two real things: the member (who acts) and a higher member count (which other cards read). Crediting both is honest. Amendment ([USER], in review): the Salon caps at three, so count-reading cards may really be "frontload after a setup tax" rather than true scaling — that depends on how fast the Salon fills, which is currently unmeasured. Resolution: every meter in the tag-through table gains a bounded/unbounded property with its cap (read from constants — Salon 3, Fanfare capped, Strength unbounded; canon's orb slots are the bounded precedent, Focus the unbounded one). Tags stay as proposed. Track B pre-registers the fill-time measurement (turn the Salon first fills; fraction of fight-turns it sits full); if bounded-meter readers plateau early on the output curves, the scaling tag for those readers gets revisited with data in hand.

2c. Damage cards that read a meter — tag as scaling; also frontload only if they deal damage with the meter at zero. Example: "deal 6, plus 1 per 4 Fanfare" is frontload AND scaling. "Deal 1 per 4 Fanfare" is scaling only. This is checkable straight off the sheet and settles the choice that most of the 135 tag divergences ride on.

2d. Sustain means in-combat healing and prevention — nothing else. Clarified in review ([USER] asked where damage reduction lives): effects that reduce ENEMY output (Weak, Frail) are already covered — they are disrupt. The boundary: your own HP ledger = sustain (heals, max HP, Buffer-style prevention); the enemy's output = disrupt; absorbing a hit this turn = block. Kept separate because they play differently — in co-op, one player's Weak protects the whole party, while block and heals protect one seat. Silent is the worked example: zero sustain, excellent mitigation via 0-cost Weak, and that is her identity, not a gap. The overall "how well does a character preserve HP" question is a derived outcome across all three mechanisms and is measured directly by Track B's HP-trajectory telemetry, not by a tag. Under this definition canon barely has sustain (0–2.3%), so no sustain cell is ever linted; zero sustain is a legal identity. The charter's earlier "Ironclad 15%" figure counted between-fight healing, which a combat taxonomy rightly ignores.

Ruling 3 — Housekeeping, bundled

3a. The charter's "402 canon cards" was an arithmetic slip. Correct figures: 439 in the DLL, 410 draftable. Fix the header on next touch.

3b. Before tempo_band: lands on any sheet: write the cross-session note. The sheet schema is read by both the sim loader and the C# codegen, so this is a shared-surface change. Note first, field second.

3c. The support finding (0% on all three of our sheets vs 2.3% in every canon pool) is carried into the Kokomi rework brief. Her Assist archetype is where support cards should live, and right now none exist anywhere. Not linted (the sim can't see co-op); tracked as rework input.

Signature
 Ruling 1 (a–c) — COUNTERSIGNED as written ([USER], 2026-08-04)
 Ruling 2a — entities CONFIRMED as proposed
 Ruling 2b — countersigned WITH AMENDMENT (bounded-meter property + Track B fill-time measurement; see 2b text)
 Ruling 2c — COUNTERSIGNED as written
 Ruling 2d — countersigned WITH CLARIFICATION (disrupt/sustain/block boundary; see 2d text)
 Ruling 3 (a–c) — ACKNOWLEDGED

[USER], 2026-08-04 — recorded from review conversation. Ready for DECISIONS.md entry and branch hand-back.
