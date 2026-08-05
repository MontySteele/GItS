# Playtest 4 notes — three-seat co-op, full roster (2026-08-04)

Build `0.2-247` (`e0097bd`, the bug-fix pass deploy), mod `klee-v0.2.0`,
weekend of 2026-08-01/02. Three seats: [USER] = Furina, guest = Kokomi,
guest = Klee. Run completed through act 3.

Firsts, so the observations are read against the right baseline: first time
all three characters sat at one table; first Kokomi table time on her own
character shell (playtest 2 had her wearing Klee's); first co-op exercise of
the `29f5ce6` bug pass — including the Courtroom Drama per-dealer window,
which was flagged **unexercisable without a second seat** when it landed.

This file is RAW INPUT for the triage at
`docs/playtest4-triage-2026-08-04.md`. Nothing here is ruled.

---

## 1. The end of turn is unreadable

> "Between the bombs, the Furina summons, and Kokomi's Charge, we'd typically
> end a turn and then a bunch of random stuff would happen where enemies lost
> a lot of health and we could never get a clear vibe for 'how much.'"

Asked for by name: a UI pass on Furina (make the summons' damage numbers
visible) and on Kokomi (**actually render the jellyfish**, and preview what
the pulse will do), and — folded into her rework rather than a UI fix —
Klee's bombs becoming more varied effects than "delayed damage."

Note the Kokomi half is a rendering gap, not an asset gap: `Bake-Kurage
Summon` (420×720) exists and the art-pass requirements already call it "the
only kit art that works." The pulse currently fires with no entity on screen.

A second-order casualty of the same noise, from the follow-up round: bursts.
Furina's burst fired regularly and read fine from the pilot's seat; nobody at
the table noticed the other two seats' bursts at all —

> "Klee's burst in particular would have just blended in with the rest of the
> end of turn nonsense."

So Q2-shaped questions (cadence, window) are currently unanswerable from the
next seat over, which is itself the finding.

## 2. The difficulty valley

> Act 1 very easy → act 2 quite hard (near-wipe against the centipede elite,
> one seat alive at the end) → act 3 very easy again.

[USER]'s own shape-hypothesis, recorded as hypothesis: the frontload is very
strong (consistent with salon sitting at 10.8% against its ruled 7.8% anchor,
attributed ~⅓ to the starter rider's act-1 points); the scaling powers
confuse people mid-run and then come together; the decks are again very
strong by endgame. The n=3000 anchor table (`4ee6881`) independently found
that **only act-1** winrates move under any arm — the sim can see the
frontload but has no instrument aimed at a mid-run spike, and it models one
seat besides.

## 3. Fanfare is structurally mistimed — the R87 deferred question, answered

> "The game expects you to have upfront numbers in the early game and
> gigantic multipliers in the late game, so Fanfare (which adds a flat
> amount) is too slow to generate in the early game (and you might not have a
> payoff card anyway) and underwhelming as a damage source by lategame (good
> for blocking though)."

R87 deferred ruling-queue items 1–3 pending exactly this playtest, and posed
the question as: *is the pilot simply better at Salon, or does everything
feed Salon by construction?* This is the second answer, with a mechanism the
sim table could not supply. The demand curve of the game is upfront numbers
early, multipliers late; Fanfare's supply curve is the inverse — slow flat
accrual early (possibly with no payoff card drafted yet), flat payout late.
It agrees with the sharpest number in `4ee6881`: fanfare at 2.10% against
`real_silent`'s 2.10%, same point estimate, same interval — the archetype IS
the no-kit floor. Fanfare-as-block is the one role [USER] rates.

Also recorded plainly: Furina card spread feels wide ("some cards seem wildly
better than others"), Fanfare and companion options read strictly weaker than
Salon spam, and — the part worth keeping — **"she 'works' now."**

## 4. Follow-up round: the five items queued for this table

Asked 2026-08-04, answered same day:

| Item | Answer |
|---|---|
| Corpse detonation (open since 07-21) | **Nobody checked.** Still open; still invalidates every sim bomb number if it fails. §1's bomb illegibility suggests it could not have been *seen* even if watched — the UI pass now sequences ahead of this check. |
| Kokomi Garment tip vs the hit (priority check 1) | **Nobody checked.** Still the open item most likely to hide a real defect. |
| Q2/Q6/Q7 counts | Bursts: Furina regular, others unnoticed (§1). Deck sizes: Furina deliberately small ("only a dozen or so non-power non-exhaust cards per combat" under power stacking); **the other two seats normal-sized the whole way** — for Kokomi that is a soft flag, since LAW 4's intent is a deck rotation keeps *thin*, and "normal" from the next seat means the reward screen may be winning. No companion-offer counts (Q7 unanswered). |
| Hover targets vs targeting arrows | **"No issues found." CLOSED** after two unanswered cycles — three seats, two of them new pilots, nobody snagged on target picking. |
| B5 motion look / facing flip | **"Not noticed."** Nothing jarring at the table, which is what a facing flip ruled "passes for a first-pass attempt" wants to hear — but it is an absence of complaint, not the deliberate look-judgment B5 asks for. D5's capture (three-of-one-member, Encore > 0 in frame) was likewise not taken. Both stay open, urgency down. |

## 5. What did NOT go wrong

Recorded because the absence is evidence. Three seats, three acts, no black
screen, no desync, no crash report: the `29f5ce6` NRE-guard class held in the
exact multi-seat conditions that used to produce black-screen-not-crash
losses, and lockstep survived a full run on matched builds. Not formal
verification — there is still no C# test project — but it is the first
play-derived evidence the pass holds, and the anchor-sweep suspect
(`TrackedDisplayBridge` — "if a gauge or the Salon stage stops tracking its
creature") produced no sightings.
