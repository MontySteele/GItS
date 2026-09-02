Status: RULED R243 2026-09-02

# Klee overhaul, round five: the canonical starter, two seats

2026-09-02. Round five is the R242 build: Strike x4, Defend x4, Jumpy
Dumpty (1: a Bomb 8 on the enemy you choose, a Mine 3 on every enemy
when it goes off) and Ka-pow! (0: Set off, 4 damage; Retain when
upgraded), with Klee opening every combat on 1 Spark. Deployed from main
3f6157c0 as 0.2.2083+proto.dirty and played on lanes 1 and 2 while the
lane-0 seat was yours.

| Seat | Seed | Actions | Fights | Stopped by |
|---|---|---|---|---|
| Opus | GXRJRQVLUL1G | 44 | 3, all won in two turns; 62 to 51 HP | its own budget (three fights) |
| Local (Qwen3.8-27B) | XS5XPGWVA80H | 60 | 4 or 5, at 40 to 55 percent HP | its action budget |

Records: `review/qa/blindplay/klee-overhaul-r5-opus/record.md` and
`review/qa/blindplay/klee-r5-local-b/record.md`. Seat numbers are
floors, not fun claims (Guardrail 7). The Codex seat is still owed on
the GPT budget.

## 1. What both seats saw

1. **Every fight had the same shape.** Plant Jumpy Dumpty on turn one,
   Strike, play Ka-pow! the turn it turns up, finish with a Strike. The
   local seat: "the pattern was always: turn one place bomb and strike,
   turn two Ka-pow and strike, turn three finish," and it called the run
   repetitive by the third or fourth fight. Opus played the same three
   fights in two turns each.
2. **Ka-pow! is automatic, and so is Jumpy Dumpty.** Opus: Ka-pow! at
   cost 0 "never competes with another card for energy, so the only
   question it asks is 'this turn or next', and with exactly one Bomb
   source in the deck the answer was 'now' both times." The local seat
   said the same in its own words in all three fights: "Ka-pow became
   automatic the moment a bomb was on the enemy."
3. **The wait never happened, and the reason is structural.** The one
   time Opus weighed popping against growing, it popped: "gave up 3
   damage and bought a lethal turn." Ka-pow! does not Retain, so holding
   the Bomb means discarding the only detonator and hoping to redraw it,
   and growth 3 is half a Strike. The brief's contested thing (section
   4: the Bomb she wants two ways at once) is on the sheet but not on
   the table.
4. **The Spark counter was decoration.** Opus finished every fight
   holding 1 or 2 Sparks with nothing to spend them on; Tinder Toss was
   the only Spark-priced card it was offered, once. The local seat:
   the relic "presumably powers some cards I haven't seen yet." Draft 4
   disclosed this price; both seats paid it.
5. **The reward screen resolved the same way three times.** Opus was
   offered Bomb-engine cards (Explosives Workshop, Mine Toss, Careful
   Arrangement, Fish-Flavored Bait, Tinder Toss) against Gorou and Kujou
   Sara every time, and took the Companion every time on rate: Gorou is
   8 damage and 4 Block for 1 energy, and the engine cards all want a
   second Bomb source the starter does not have. Defend was played once
   in three fights next to that Gorou.
6. **The decisions that did feel real** were tempo, not Bombs: the
   third energy on turn one (Defend to take 1, or Strike to kill a turn
   sooner, decided by counting the five-card draw pile); Stomp's
   discount and card order; the Ravenous slug (kill one and the other is
   stunned but gains Strength). The local seat's tension was "block or
   attack" at half HP, and in two-enemy fights "which enemy gets the
   Bomb," which it got right both times by picking the harder hitter.

## 2. Surface finds, triaged

- **A plain Strike applies Pyro and says nothing** (rule 5 is the
  catalyst cadence; the base game's Strike carries no tip). Opus then
  read Gorou's "supplies Geo" preview against that Pyro aura and could
  not make the two screens agree. Ruled: the base game's Strike applies
  no element for any character, since the basic cards are supposed to
  be bad; `EB-313` is that removal, built in the balance PR.
- **The Neow transform screen re-rolls on re-select and names the wrong
  source card.** Opus confirmed "Strike to Hemokinesis" and the deck came
  out with Stomp and one Defend short. `EB-314`, the blind render.
- **The Bomb badge reads as one number for two things** ("2, after
  Weak"; "2, including 2 Mines"; whether a Mine's part goes off on the
  enemy's attack). PR #291 rewrote the badge faces after this build;
  re-read on the next one, no row.
- Duplicate copy numbering on the page is `EB-271`'s other half. Weak
  shrinking Klee's own Strike, Stunned's intent line and the unplayable
  Spoils Map are the base game.

## 3. Applied as the default (D), disclosed

**Bombs grow by 4 a turn, not 3** (`KLEE_OVERHAUL_BOMB_GROWTH`, the
brief's "placeholder"). Round three moved it 2 to 3; round five says 3
is under the free pop. The first draft of this packet applied 5; you
read that as a free Strike every turn per Bomb per enemy, so it is 4:
Jumpy Dumpty reads 8, 12, 16, and its Mine 3, 7, 11, two dawns' wait
worth a Strike and a bit. The balance pass
(`review/ruled/prototype-balance-2026-09-02.md`) was priced at growth
3 and its Rares scale with it: Alice's Recipe doubles to 8 a turn,
Explosives Workshop adds 1. Round six reads growth 4 with the balance
numbers in one build.

Routed, not applied: Gorou at 8 and 4 for 1 energy sits two above Iron
Wave; whether the Companion Commons should be a notch above Strike or
level with it is the companion workshop's, and it is noted there.

## 4. Picks, ruled R243 (2026-09-02)

1. **Ka-pow! keeps its card when held.** RULED at the default
   ([USER], 2026-09-02: "I'm fine with the default on Ka-Pow!"): Ka-pow!
   has Retain at base and the upgrade adds damage, 4 to 7, built in the
   balance PR. The new fact that reopened R242 pick 3: both seats popped
   the Bomb the turn Ka-pow! appeared, because holding the Bomb meant
   discarding the only detonator.
2. **The opening Spark with nothing to spend it on.** RULED at the
   default ([USER]: "4-4-2 is correct"): the starter keeps its shape and
   the draft supplies the Spark sinks (four of the twelve Commons cost
   Sparks). The new fact that reopened it: both seats finished every
   fight with unspent Sparks and no Spark card.
3. **Your play.** RULED at the default ([USER]: "let's do round 6 after
   all of these edits"): round five is not played by [USER]; round six
   carries the balance pass, growth 4, Ka-pow!'s Retain and the base
   Strike's exemption in one build, seats first on the lanes, then
   [USER].
