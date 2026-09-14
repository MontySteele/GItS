Status: RECORD (the doctrine door on R271 stage one, EB-749; read before the build reached a tester)

# Klee stage one (EB-749): the four changed faces at the doctrine door

Written 2026-09-14 on branch `klee-stage-one-2026-09-14` (PR #481). The
build is R271 §8 stage one: Fwoosh! and Fireworks Show cut, Powder Charge
redesigned as Booby Trap, Grounded on "no Set off card last turn", Return
to Sender capped at the Block it granted, Tinder Toss as Set off ALL then 3
to ALL at 1 Spark. Both engines, tests in both, gates green (pytest 7337,
dotnet 1499 with the prototype switch on). Prototype stage; nothing here is
a number anyone may quote (R215 B).

## 1. The door

One Codex read of the four faces against charter C1 to C6
(`review/qa/klee-stage-one-2026-09-14-prompt.txt`, reply `-reply.md`),
comparisons pasted from the sheet.

| face | verdict | clause | the line |
|---|---|---|---|
| Booby Trap | FOLLOWS | C2, C3, C5, C6 | the 1 Spark it costs over Pop! is the whole turn-one bank; against a lone non-attacking enemy the Mine adds nothing and the Spark was Dig In's |
| Tinder Toss | REQUIRES_MODIFICATION | C6 | "gives the Common the entire Uncommon effect for one fewer Spark plus 3 damage per enemy", read against Fireworks Show |
| Grounded | FOLLOWS | C2, C6 | pays nothing the turn it is played and nothing after a Set off turn, where Metallicize pays 3 on both |
| Return to Sender | FOLLOWS | C2, C6 | zero Bomb on a non-attacking turn against Dodoco Cover's 4; on turn one the 1-Spark bank cannot buy it at all |

Closing sentences: no Common on the pool is a strictly better Pop!; a Cook
deck holding Grounded plays a Set off card when the accumulated Bombs kill
before an otherwise lethal attack, at the price of next turn's 4 Block and
1 Spark.

## 2. Tinder Toss: the verdict is recorded and not acted on

The breach the seat names is against Fireworks Show, and Fireworks Show
leaves the pool in this same build. C6 reads a row against "a pool row or a
base-game card", and the prompt (mine) invited the comparison against a row
the build deletes; that is a defect in the prompt, not in the face. Read
against the rows that survive, Tinder Toss is not strictly better than any:
Pocket Match keeps Retain and 5 single-target damage at the same price;
Quick Fuse grows before it cashes; Bombs Away! and Rapid Fire are Energy
cards; Cleave is a different currency. The 1-Spark price was disclosed as a
D default in the ruled packet (§5.3: "early access is what the round should
read") and R271 took it. So the price stands, and round 27's natural lane
carries one question for this face in place of a second door call: **is
Tinder Toss ever declined on a multi-enemy board when the bank holds 1**
(C5). A seat that never declines it is the modification signal.

## 3. Two things the build found beside the spec

- **Kaeya, Cold-Blooded Strike** (companion stand-in, `proto_mc_kaeya_cold_blooded_strike`)
  still printed "This turn, Grounded counts a Bomb as on the field", a
  condition Grounded no longer has. Its built effect is a force-pay:
  Grounded pays at the next start of turn whatever its condition says. The
  face is corrected in this PR to say that; no rule moves.
- **The superseded KLEESPARK arm's rows** (`KLEE_SPARK_ALT_ROWS`) are still
  on the surface and still compiled, unreachable under the overhaul arm.
  `EB-750`, hygiene.

## 4. What follows

Deploy `+proto`, then the calibration's build one
(`review/records/klee-fun-calibration-2026-09-14.md` §5): the seed is
written there before any seat plays, three seats play act 1 on it and
their three lines are committed, then [USER] plays the same seed. Round
27's hypotheses are the packet's (§8): a natural lane, and a Cook lane
holding Grounded, Return to Sender and Sparks 'n' Splash, plus the Tinder
Toss question above.
