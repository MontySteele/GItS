Status: OPEN (no pick; the defaults in §5 are applied; six rows through the audit door)

# Kokomi pool pass one: Plans on the Attacks, and a doubler that is an engine instead of a tax

Written 2026-09-05 from the readings rounds 10 to 16 carried to "the pool
pass" (`review/ruled/kokomi-overhaul-round-10-2026-09-04.md`,
`review/active/kokomi-overhaul-round-12-2026-09-04.md` to `-16-`), read
against the brief (`review/active/kokomi-brief-2026-09-01.md`) and the pool
as it stands (`docs/prototype-surface.yaml`, 32 `proto_kk_` rows).
Prototype stage: no slate, no stamp, no number here is quotable. Every row
went through the doctrine audit before a tester sees it
(`review/records/card-audit-2026-09-04.md` §5.4); all six are FOLLOWS after
three were re-priced off shipped cards, and they build C# first for round
17 on.

## 1. What the rounds said

**The deck is two cards deep, seven rounds running.** The starter stands
(R254, R257) and this pass does not touch it. The reading that is the
pool's: the seats drafted Attacks, and the pool's Attacks mostly carry no
Plan line. Of the pool's Attacks, one Common (Feint) has a Plan; Deep
Current and Undertow do not, and Slack Water is the basic. A seat that
takes the damage it is offered ends up with a deck that plans on five
turns in sixteen (round 14) and reads "Nothing is planned" sixteen times
(round 10). Density in the offer, not the starter, is this pass's job.

**Nereid's Ascension "reads like the kit's payoff and behaves like a
tax"** (round 14). Two energy, Exhaust, and a Plan slot for two turns of
doubling, in a deck with two Plan cards to double. Written as a Plan it
also spends the morning it is meant to pay. The brief names it the one
Rare that breaks rule 3's "once, in order"; it can break that rule as a
Power and stop taxing the morning.

**Tide Chart is the density payoff and one card.** Nine natural rounds
have not drawn it; round 17 grants it. The pool-pass half of that
reading (rounds 12 and 13: "a second copy, or a Common that reads the
memory") is answered below with a Common payoff that reads the morning
from the other side, on an Attack.

**Not this pass.** Ripple's "always plan it" stands on round 10's default
until a seat needed the now-line. The reaction table printed for a
one-element deck is the bridge page's (`EB-428`). Shop prices past reach
are rarity, not rows.

## 2. The six rows, as audited

Rarity, energy; the pool row each is priced against. The jellyfish's hits
are Hydro; a planned single-target line is aimed when written (R250).

**Tactician: Attacks with a Plan line**

1. **Riptide** — Common Attack, 2. *Deal 9 damage to ALL enemies. Plan:
   Deal 13 damage to ALL enemies.* Upgrade: 12 and 17. The heavy AoE.
   First written at 1 energy (5 and 9) and ruled REQUIRES_MODIFICATION on
   C6 with no comparison named; the comparison this packet's author
   derived, not the reviewer's, is Kurage's Oath (basic, 1: 3 and 7),
   which that version dominated on both lines; re-priced at 2, where Deep Current
   (1: 6 to ALL) is the cheaper now-line and the Plan premium is the
   brief's usual four.
2. **Pincer** — Common Attack, 1. *Deal 3 damage twice. Plan: Deal 3
   damage three times.* Upgrade: 4 per hit. First written at 4s (8 and
   12) and ruled REQUIRES_MODIFICATION on C6 with no comparison named;
   the author's derived comparison is Feint (1: 6, Plan 10), which that
   version dominated on both lines; re-priced at
   3s: 6 now in two hits, 9 planned in three, worse into Block, better
   under Vulnerable, three Casket-sized hits the morning after.
3. **Flank** — Uncommon Attack, 1. *Deal 8 damage. Plan: Deal 8 damage to
   each enemy that intends to attack.* Upgrade: 11. The set of enemies is
   fixed when the Plan is written, from the intents on the screen, which
   is the rule for aimed Plans (R250) applied to a set. Against Feint: 2
   less planned on one enemy, and everything on a board of attackers.

**The morning's payoff, on a Common**

4. **Well Laid** — Common Attack, 0. *Deal 2 damage. Deals 3 more for
   each Plan the Bake-Kurage carried out this morning.* Upgrade: 3 and 4.
   Tide Wall's count on a hit instead of Block, 0 energy, a floor of 2.
   With no Plan carried out it is a worse Strike; with three, 11 for
   free, the morning paid a second time.

**Priestess**

5. **Feigned Retreat** — Common Skill, 1. *Gain 4 Block. Plan: Gain 4
   Block and deal 6 damage.* Upgrade: 6 Block, 6 and 8. Against Read the
   Field (1: 5 Block, Plan 10 Block) and Ambush (1: 5 damage, Plan 12):
   less of either, both at once, and only when planned.

**The Rare, redesigned**

6. **Nereid's Ascension** — Rare Power, 2. *The Bake-Kurage carries out
   every Plan twice.* Upgrade: cost 1. From "Exhaust. Plan: for 2 turns,
   the Bake-Kurage carries out every Plan twice." The same rule broken
   (rule 3), for the whole fight instead of two mornings, and no longer a
   Plan itself, so it never spends the morning it doubles. Its price is
   two energy on a turn that writes no Plan, and every turn after that it
   pays only what the deck plans. The reviewer's first read ruled it
   REQUIRES_MODIFICATION on C6 with no comparison named; the author's
   reading of that verdict was that it was held against the printed row
   it replaces, which was still on the census. The fourth read, with that
   row struck as replaced and The Moon Overlooks the Waters (Rare Power,
   2: Plans also happen now) named as the standing reference, is FOLLOWS
   on C5 and C6. Which comparison the first verdict rested on is not
   recorded, because the seat's protocol at the time did not ask for it
   (amended 2026-09-05, `understudy/seat.py`). The
   brief's §5 sentence is edited to match in this packet's commit.

Pool after the pass: 37 rows; Common Attacks with a Plan line 3 (from 1),
Plan-count payoffs 3 (Tide Wall, Tide Chart, Well Laid).

## 3. What the pass does not do

No starter change (R254, R257). No Commander row: the companion layer is
the workshop's (R234, R236) and Rally, The General's Banner and Chain of
Command already stand. No Mend below Rare (LAW). No second Tide Chart
copy: Well Laid is the second reader, on the damage side. Nothing here is
a number pick.

## 4. The audit and the build

Four reads (record §5.4). The first passed Flank, Well Laid and Feigned
Retreat and ruled the other three on C6 with no line; two follow-ups
asking for the comparison came back as bare verdicts, because the seat's
protocol (`understudy/seat.py`, `REVIEW_PROTOCOL`) forbids it a remedy
and it read the ask as one. The comparisons were derived here by lifting
values off shipped cards, and the fourth read passed all three. Lesson
for the record: ask a C6 verdict for its comparison row in the first
prompt, in the form the Klee read used, and never for a modification.
FOLLOWS rows build C# first, then the tier0 twin, then the surface; new
engine work: a multi-hit Plan clause, an intent-keyed set aim fixed at
writing, a Plans-carried-out count on a now-line, and the doubler as a
power.

## 5. Defaults applied (D and E), disclosed

- **E:** six rows, the density the reads asked for and no more; the next
  pass writes against what these do.
- **D:** Nereid's Ascension becomes a Power at 2 (1 upgraded); the number
  and the shape move on the seats' word, and the brief's §5 sentence is
  edited in this packet's commit.
- **D:** Riptide at 2 energy and Pincer at 3 per hit, lifted off Deep
  Current and Feint after the C6 reads.
- **E:** one register row for the build (`EB-492`).
