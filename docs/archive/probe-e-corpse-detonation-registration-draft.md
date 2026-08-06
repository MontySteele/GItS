> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/probe-e-corpse-detonation-registration-draft.md` — new path: `docs/archive/probe-e-corpse-detonation-registration-draft.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Probe (e) — corpse detonation: does a killing blow early-detonate the bombs? — REGISTRATION

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

> **COUNTERSIGNED 2026-08-06 (Q11 / R118) — REGISTERED, STILL NOT RUN.**
> [USER], verbatim: *"Countersign."* The registration converts from draft to
> **registered work**: it runs under its own terms below — two tells,
> negative-control arm, nine confounders, cost ceiling, stop-and-re-register
> tripwire. The run itself is Track M's and, per the wave-8 sequencing note,
> happens after the v6 code lands. `S4-G15` stays open until the probe
> reports; the table check survives as fallback. The draft banner below is
> struck, not deleted (R101b).

> ~~**DRAFT — FOR [USER] COUNTERSIGN. NOT RUN.**~~ Nothing below is a measurement.
> No game was launched, no run was taken, no number in this file was read off
> any wire. This document exists so that the question, the method, the
> confounder list and the licensing limits are fixed **before** any reading is
> taken — the same discipline probes (a) and (b) were run under, and the same
> form probe (d) was registered in. ~~The probe is neither scheduled nor
> resourced; countersign converts it into work, and until then it is paper.~~
> *(Countersigned 2026-08-06 — see the banner above.)*

Date drafted: 2026-08-06. Cold Reading, Track AC (`AC-4`). Input: the standing
open question at `klee-mod/DECISIONS.md`, "Corpse detonation — OPEN parity
question, awaiting playtest (2026-07-21)", tracked as `S4-G15`. Sibling
registrations by structure: `docs/probe-d-registration-draft.md`,
`docs/probe-a-block-offset.md`, `docs/probe-b-fanfare-residual.md`.

**Zero design authority is claimed or exercised.** No constant, card, sheet or
rule is touched by this document, and none may be touched by the probe it
registers. Nothing here re-grades any ratified result, and no outcome of this
probe is a balance finding (Guardrail 7 unchanged).

---

## The pre-registered question, verbatim

> "Does a killing blow on a bombed enemy early-detonate that enemy's bombs?"

That is the question `klee-mod/DECISIONS.md` has carried, unanswered, since
2026-07-21. It is quoted rather than reworded so the answer lands on the
question that was actually asked.

---

## Why this is a registration and not a table item

**It has been a table item for five playtests and it has not closed.** Recorded
plainly, because the pattern is the finding: the settlement was written as
*"~10 seconds at the table"* — bombed enemy plus Pounding Surprise, land the
kill, watch for the Spark — and across at least five sessions nobody has been
holding the relic, on the bombed enemy, on the killing turn, while remembering
to look. [USER] on the odds of that changing on its own: ***"who knows when it
closes."***

**So the instrument changes rather than the question.** A scripted
bridge-driven fight can arrange the exact state the question needs, on demand,
in one sitting — the same conversion probes (a) and (b) made when S7's
questions turned out to need a declared script rather than a soak. Ten minutes
of agent time replaces waiting for an interaction to occur naturally.

**The table item survives, as fallback only.** If the probe is declined, or if
it stops short of an answer, `S4-G15` is still the ~10-second eyes-on check and
still closes the question the moment somebody happens to be holding the relic.
Nothing about this registration retires it.

## What is actually at stake

**The sim detonates unconditionally.** If the game suppresses detonation on a
creature the blow just killed and the sim does not, then **every sim
bomb-damage measurement taken against a killable enemy overcounts at the margin
on the killing-blow turn.** Low probability, broad blast radius — it touches
bomb numbers generally rather than one card. That is the whole reason a
low-probability question is worth an instrument.

**The evidence, as the ledger records it, on both sides:**

* **For a defect:** `BombPower.AfterDamageReceived` lacks the `target.IsDead`
  guard that both of its siblings carry. If the engine broadcasts
  `AfterDamageReceived` on a creature the hit just killed, the bombs resolve
  one turn early on the death turn.
* **Against:** one refuter in the original bug-hunt panel claimed the engine
  suppresses `AfterDamageReceived` on a killed creature, which would make the
  missing guard harmless. **That claim is UNVERIFIED** — no decompile site was
  produced for it, and the finding survived the panel on a contested premise
  rather than a clean one.

**Neither side is assumed here.** The probe is designed to separate them, and
its write-up must state which one the reading supports.

**One adjacent fact, carried so it is not re-discovered mid-probe.** S14's
`NC-18` reports that the ledger entry above *"states the sim's behavior
backwards, inverting the stakes of the only open bomb parity test."* Whether
that entry needs correcting is **[USER]'s to rule and is not this probe's**
(`docs/sitting-prep-2026-08-05.md` §4b). The probe therefore reads the sim's
behaviour **off the sim**, not off the prose, and says what it found either
way. If the reading contradicts the ledger's description, that is a second
finding and it is reported as one.

## The candidate layers this probe must separate

Stated in advance, with what a YES on each would mean. The probe is designed so
that at most one of these can be left standing.

| # | layer | what YES would mean |
|---|---|---|
| 1 | **the engine suppresses the broadcast on death** | the refuter was right, the missing guard is harmless, sim and game agree, `S4-G15` closes with no code change |
| 2 | **the engine broadcasts on death and the bombs resolve early** | the missing guard is live; the game detonates on the death turn. Sim and game *agree in outcome* but for a reason nobody wrote down — and the guard's absence becomes a deliberate behaviour rather than an oversight |
| 3 | **the engine broadcasts but the bombs are cleaned up with the corpse before they resolve** | a third behaviour neither side of the panel predicted; the sim's unconditional detonation is then the divergence, and its size is the marginal killing-blow damage |
| 4 | **the state is unreachable as scripted** | an instrument limit, to be declared as such rather than folded into an answer. The fallback table item is then still the only route |

## Method

**Nothing new is built if the existing instruments suffice.** The probe is a
scripted fight on the P1.5 bridge, in the shape `understudy/probe_block.py`
already established: a fixed script with no policy in it, a declared seed, a
turn bound, and readings flushed as they are taken.

1. **Arrange the state.** One fight, chosen seed, Klee, against an encounter
   containing an enemy that can be reduced to a killable HP total in one
   scripted turn. Apply bombs to that enemy; then land a blow that kills it.
   The two halves must be separable in the log: the bomb application and the
   killing blow are distinct scripted actions with a reading between them.
2. **Read the tell twice, on two independent channels**, because a single tell
   is a single point of failure:
   * **the relic tell** — Pounding Surprise's spark-on-detonation, which is the
     settlement the ledger already names. Spark appears → the hook fired on
     death;
   * **the damage tell** — the other enemies' or the player's HP deltas across
     the killing blow, read off the wire, which does not depend on a relic
     being held or a visual being noticed.
   **If the two tells disagree, the probe reports the disagreement and stops.**
   It does not pick one.
3. **Run the negative control.** The same script, the same seed, with the blow
   sized to leave the enemy **alive** at 1 HP. Bombs must then resolve on their
   normal schedule. Without this arm, "the bombs did not resolve early" is not
   distinguishable from "the bombs were never applied".
4. **Read the sim's own behaviour on the identical scripted sequence**, so that
   the comparison is sim-vs-game on one script rather than game-vs-prose. This
   is the half that answers `NC-18`'s claim about the ledger text as a
   side-effect, without ruling on whether the text gets amended.
5. **Output** is the three-part shape the sibling probes published: the raw
   per-action table with both tells, the sim-vs-engine comparison per action,
   and the layer table above with exactly one row marked.

### Instruments

The P1.5 bridge; a scripted driver in the shape of `understudy/probe_block.py`;
`tier0`'s bomb resolution as the sim side, read-only. **No mod rebuild, no
deploy, no wire change, no new soak corpus.** If any of those turn out to be
required, the probe **stops and re-registers** rather than growing — the same
tripwire probe (d) carries.

## Confounders that must be logged

Declared in advance; each is to appear in the write-up with its disposition,
present or absent.

1. **Relic dependence of tell 1.** Pounding Surprise must actually be held, and
   the run must be seeded or granted so that it is. If it cannot be arranged,
   tell 1 is absent and the probe runs on tell 2 alone — and says so, rather
   than reporting a one-tell result as a two-tell one.
2. **AoE and splash attribution.** A killing blow that also damages other
   creatures makes the damage tell ambiguous. The script must land the killing
   blow as a **single-target** action, or the tell is unreadable.
3. **Enemy death animations and turn boundaries.** "One turn early" is a claim
   about ordering; if the reading cannot distinguish the death turn from the
   turn after it, that is an instrument limit and not an answer.
4. **Which bomb.** `_op_modify_bombs` adds bonuses per bomb with no per-card or
   per-turn limit (S13 `X8`). The script must apply a **known, stated** bomb
   count and magnitude so the expected detonation damage is arithmetic rather
   than inference.
5. **Bot-limited (Guardrail 7).** Every engine number will come from a fixed
   script. Nothing this probe produces is a balance finding.
6. **One character, one encounter, one seed.** Breadth is not the point and no
   breadth claim may be drawn from it.
7. **The `NC-18` prose.** The ledger's description of the sim's behaviour is
   under question and must not be used as the sim-side reading. Method step 4
   exists for exactly this reason.
8. **Wire freeze.** If the P1.5 wire moves between this registration and the
   run, that is logged, not smoothed over.

## Expected cost

Stated as a class, on probe (d)'s pattern.

* **Floor — one scripted fight, one seed, two arms.** Comparable to probe (a)'s
  measurement half, which is the closest precedent in kind and size. [USER]'s
  own estimate of the agent time is **ten minutes**; that is recorded as the
  intent, not as a promise the write-up must honour.
* **Ceiling, and the tripwire.** If neither tell reads cleanly — layer 4 — the
  remaining question is a **C#-side decompile or hook read** on
  `AfterDamageReceived`'s broadcast conditions, which is a different and larger
  instrument. That is explicitly **out of scope here**: the probe reports
  "layer 4, unreachable as scripted" and stops. It does not grow into that read
  without a fresh countersign.

## What each answer would license, and what it would not

**If the engine SUPPRESSES on death (layer 1):**
* *Licensed:* closing `S4-G15` as "sim and game agree"; recording that
  `BombPower`'s missing `IsDead` guard is harmless **for this hook**, with the
  measurement as the citation the original panel never had.
* *NOT licensed:* any claim about the guard's absence being harmless on other
  hooks or other powers; any bomb balance statement; adding the guard, which
  would be a code change nobody asked for.

**If the engine DETONATES on death (layers 2 or 3):**
* *Licensed:* filing a **named, bounded parity item** with the marginal
  overcount stated per killing blow, and routing it as a candidate; and
  answering `NC-18`'s factual half by stating what the sim actually does.
* *NOT licensed:* changing `tier0`'s detonation rule, re-grading any bomb
  number already published, amending the `klee-mod/DECISIONS.md` entry (that
  is `NC-18`'s ask and it is [USER]'s), or treating a one-encounter reading as
  a roster property.

**In either case, and stated so it cannot be inferred later:** this probe
grades nothing, prices nothing, and moves no number. It answers one sentence
about one interaction.

---

**Status: DRAFT — FOR [USER] COUNTERSIGN, NOT RUN.** New probes are
pre-registered questions per standing law, so this document is the ask. The
queue row is `docs/registry/user-queue.md` §1. The `S4-G15` table item survives
as **fallback only** and is not retired by this registration.
