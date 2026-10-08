# Project review, 2026-10-08: what the nine reviews found, and your picks

Status: RULED 2026-10-08, all ten picks at the defaults. [USER]: "Overall, agreed with all paper defaults. You're good to merge it."

Overnight, nine review papers each went through four steps:
- a Sonnet agent gathered the facts;
- a reviewer wrote the paper (Fable for the kits, conventions and reactions; Opus for the rest);
- a separate agent tried to refute every number;
- the writer revised, with a fact-check log at the end of each paper.

The papers sit beside this one in `review/active/project-review-2026-10-08/`. Treat them as input.
This page is the main session's reading of them.

## What the reviews found

1. **Klee's grading used a contaminated baseline.** The base-five window (2026-10-05 before 16:50) held
   220 rows, but only 115 are the five counted runs. The rest are:
   - an off-seed Ironclad run;
   - the stopped reduced-pool attempt;
   - doubled rows.

   Re-graded on the counted runs, suite 4's act 1 was outside the bar too (HP lost 1.19, not 0.70).
   Suite 5 (PR #965) is the first suite graded the new way. Tonight's base control re-runs the five
   on today's page, for a second baseline.
2. **Suite 5 is inside the bar on matched seeds.** The first reading put act 3 at 0.70 of base
   damage, with the gap all on turn one. Tonight's base control and a matched-seed read
   (PR #965) show that was seed mix: Klee died in act 2 on the two seeds whose base decks deal
   about 60 a turn in act 3.
   - On the seeds both sides reached, HP lost is 0.69 / 0.98 / 0.93 of the two base runs by act,
     and damage is at or above theirs.
   - Turn one is still about half the base characters', and her Block is above theirs in every act.
   - Two Sonnet runs of the same base character on the same seed differed more than Klee differs
     from either.

3. **The telemetry has three readers' traps:**
   - `reactions_by_turn` is a running total, and I misread it the same way myself last night.
   - Every bot co-op row is written twice.
   - Reports grouped two runs on one seed together.

   Each first draft of the reactions and Klee reviews made a co-op claim from these traps, and the
   fact-check withdrew it. The telemetry PR fixes all three.
4. **The ruled Balance text never reached main.** PR #929, ruled 2026-10-05, conflicts with main.
   Main's own Balance paragraph points at sheets deleted on 10-02.
5. **The documents grew back.**
   - STATE is 387 lines against about 80.
   - BACKLOG went from 70 to 147 lines.
   - About half of `review/active` is ruled or superseded.
6. **LAW.md still describes the "spent aura" rule** that the code dropped on 2026-10-03. The open
   Zhongli paper is built on it.
7. **The sim does not pay Swirl damage; the game does.** This affects any sim of a non-Varka deck
   with Anemo cards. It is the only real code defect found.
8. **Reactions:** Varka is the only kit that reacts alone, about 1 reaction a turn. Klee reacts in a
   third of her solo fights, and reactions are 3.5% of her damage. In your own runs, co-op cuts HP
   lost by a fifth to two fifths. That is a lift, not a multiple, and it sits inside the 10-06
   standard.
9. **The kits:**
   - **Kokomi** is no longer "undercooked". She loses long boss fights on length, but some of her
     "half damage" reading came from Bake-Kurage hits that went uncredited before 10-02.
   - **Furina's** Tab is at a base character's level in two seat runs and bleeds in act 3. Under the
     curtain call, a Repay card cannot fix the HP she carries between fights. The act-3 lever is
     tempo.
   - **Varka** is at base damage and well above base survival. All three Cryo starts died, and no
     Pyro or Cryo payoff was ever played.
   - **Three kits are waiting on your run**, the next step each one's plan names: Klee on the
     build that passes suite 5, Kokomi on the 78-card build, and Furina's first Tab run.

## Fixes in flight that need no ruling

These are being built tonight as PRs I merge once every check passes:
- **Telemetry:** run instance in the fight key, the co-op double write, and the report's header.
- **Bridge:**
  - lane state kept per lane, not per checkout, which is the bug that split suite 5's state;
  - lane scripts baked into each seat folder;
  - the brief's budget line;
  - "the fight is over" in place of a refusal;
  - page trims.
- **Card-text conventions, every kit but Klee:** Klee is frozen at Balance, so her text changes are
  queued for `klee-next`. The pass covers:
  - bare element words;
  - "N additional damage";
  - Swirl wording;
  - the Frozen tip;
  - lint scope widened to Varka and the Fontaine companions.
- **Documents:** STATE cut toward 150 lines; BACKLOG regrouped; ruled papers filed; `land_pr`
  refusing a PR with no checks reported.
- **Sim and tools:** Swirl parity, with a before-and-after table; dead shipped-kit sim code and dead
  tools deleted.

## Your merges (no decision, just your signature)

- **#929:** the ruled Balance measurement text, rebased onto main. It amends EXPERIMENTS.md.
- **LAW.md wording fix:** the consuming-aura rule in place of the spent-aura sentence, and "Burst
  energy" dropped from the reaction credit rule.
- **#965:** Klee suite 5's record, with three picks of its own.

## Picks

Each pick names its source paper in brackets.

1. **Replication before reversal** [process].
   - **Default:** a smaller Balance call is reverted or replaced only when a second suite on the
     same build agrees, unless the gap is plainly outside the 2-to-6-floor spread suites show
     between themselves. Big structural findings are exempt. A replication costs about 12M tokens.
   - Alternative: one suite per change, as now.
2. **How often the co-op check runs** [process].
   - **Default:** three shared seeds, at a kit's finish line and after any reaction-rule change.
   - Alternative: after every card batch as well.
3. **Dead code and branches** [tech debt], as one block.
   - **Default:**
     - delete the empty companion stand-in seam;
     - delete the discarded Furina v2 sim slice, tagging its last commit;
     - delete the 220 merged remote branches (every commit stays reachable through main's merges);
     - fold the paused Teyvat frame's docs into a pointer;
     - drop Furina's motion-look pick from QUEUE until her finish line.
   - Say which of these to keep, if any.
4. **The Zhongli paper** [reactions].
   - **Default:** amend it to the consuming rule now. Crystallize stays at 4 Block until a Geo
     character is picked.
   - Alternative: make Crystallize the one reaction that leaves the aura standing.
5. **Swirl on a lone enemy** [reactions].
   - **Default:** leave it. It does 2 damage for the aura, Prune's re-colour is its payoff, and no
     seat has called it a waste.
6. **Klee's brief, Sparks sentence** [Klee].
   - **Default:** with three opening Sparks, Sparks are a bank that gates the turn-one Set off and
     the all-in payoffs, not "the second contest". Edit sec.4 in your words ("only really matter if
     you're trying to let your bombs cook").
7. **Klee's unplayed fifth** [Klee]. 16 of 78 cards have no plays in 344 seat fights.
   - **Default:** after your run, a cut-and-replace paper, starting with the Companion line.
     Kitchen Alchemy and Blast Shield stay.
8. **Kokomi** [Kokomi]. **Default:** hold every Kokomi change for your run on the 78-card build.
   After it, in this order:
   - the boss-length damage paper;
   - two "plan the reaction" cards replacing the two least-played status cards;
   - her own relics and potions, with the heal on the Common relic as ruled;
   - one paired co-op round.

   The opening Plan stays held: it is the free combat-start setup you turned down for Klee.
9. **Furina** [Furina]. **Default:** your Tab run first. After it:
   - print guest Lines and Acts on the faces, and run one seat round before any Pneuma change;
   - if act 3 still bleeds, the lever is tempo (a Rare or two that scale), not Block or Repay;
   - keep both Ancients;
   - co-op cards in the last batch toward 78.

   Also, LAW.md:41 should say a guest "pays for it with a seat and a card", not "and Fanfare". This
   is a wording fix only.
10. **Varka** [Varka].
    - **Default:** leave his sturdiness until a Balance suite reads several seeds per start.
    - Run the Pyro/Cryo round with card offers logged. Payoffs offered and passed means fix the
      cards; payoffs never offered means move one payoff per element to Common.
    - Leave the Knight-payoff shelf until offers are logged.

Where the evidence is thin:
- every Balance ratio rests on five single runs a side;
- the co-op comparisons rest on one bot pair and your own runs;
- no human has played Furina's Tab or Kokomi's 78-card build.
