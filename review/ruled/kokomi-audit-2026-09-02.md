Status: RULED R240 2026-09-02

# Kokomi, draft 5: a fresh audit
Ruled by R240 (2026-09-02): the Plan is the chassis; the exhaust replay and Mend step down to payoff cards. The picks below are answered by brief draft 6.

Written 2026-09-02 by a Fable session with no prior context, on your
question: is this the best version of the character, and can we do better.
I read the brief (draft 5, uncommitted), the slice (draft 4), the two ruled
packets, both seat records, your Kurage's Memory spec, the shipped sheet,
the Inazuma companion workshop, the Klee brief, and the C# arms. Where a
claim comes from the source game rather than the repo, it says so.

**The short verdict.** Draft 5 is a sound skeleton with the right anti-spam
controls, and it is buildable on what exists. It is not yet a kit with a
decision every turn or a payoff moment: the starter does not put the loop
on the table, the replay is priced twice so its arithmetic ties the basic
cards, holding has no value so "when to Surge" is not a decision, and the
best thing the jellyfish can ever do is a card you already played. All four
are fixable without leaving your constraints. Amend it; do not replace it.

## 1. Draft 5 as written

**What it gets right.** The trap is closed, five ways, exactly as §10 says:
no random door, one card per Surge, every replay paid in Tide, the once-only
tag, and Moon's Reflection as the only second chance at full energy. First
in, first out is the right shape for the anti-spam job: a card cannot come
back the turn it went in unless the row was empty, which is a natural delay
no keyword has to enforce. Rule 8 (Strength becomes Tide) is the right
translation of no-crit. The relic teaches Surge on turn two of fight one.
And it is buildable: `KurageMemory.cs` already keeps a first-in first-out
queue with a price at 3 per energy, a stored target with random fallback,
and the affordability walk the strip draws (`Queue`, `Price`, `Enrol`,
`Fire`, `Affordability`); `KokomiPlan.cs` keeps a separate Plan queue that
resolves at turn start; the Tide arm carries Mend at entry HP, Garment,
Strength to Tide, Treatise, Art of War and the Banner. The slice's §5 build
list is accurate except that its rule 3 still says "top of the exhaust
pile" and must be re-pointed at the queue, and its Uncommon Power named
*Orders* collides with the row's name (the brief already renamed it Chain
of Command in §6.3).

**Where it fails, specifically.**

1. *The starter has no loop in it.* Ten cards (§9): one Salt Line is the
   only card that can become an Order, one Rising Tide is the only Surge,
   and Stolen Chapter is a Plan that fires by itself. Fight one's total Tide
   demand is at most 3 (one Salt Line replay), and the relic pays that. Two
   Oaths supply 8 per deck cycle for nothing. Your own script says so at
   §12 turn 4: "the Tide at 10 and the list empty ... a fed Tide with
   nothing to spend it on was wasted." That is the Codex seat's draft-2
   finding again: "Kurage's Oath and Rising Tide became mostly dead after
   the first combo" (`review/qa/blindplay/kokomi-overhaul-r1-codex/record.md`).
   The lesson §12 draws, "next fight the Salt Line goes on late," is not a
   fix; one Salt Line still replays once.
2. *The replay is priced twice, so it ties the basics.* A Surge costs a
   card, an energy, and 3 Tide (three quarters of an Oath) for one play of a
   card you already paid for, and Rising Tide's other half is 4 damage.
   Priestess turn: Salt Line, Oath, Rising Tide = 3 energy and 3 cards for
   14 Block and 4 damage. Basics: Coral Guard twice and Water's Edge =
   3 energy and 3 cards for 10 Block and 6 damage. A wash. The Opus seat's
   sentence on draft 2 will return word for word: "every time I did the
   arithmetic honestly the boring line won" (`...r1-opus/record.md`). The
   §5 calibration is the cause: Ironclad's Exhume (source game, my
   knowledge) is a Rare that Exhausts itself, not a repeatable Common, so
   anchoring Surge to "Exhume plus half a Strike" prices a Common as if it
   were a Rare's effect.
3. *Holding has no value, so "Surge now or wait" is not a decision.* §5's
   third bullet says wait to "feed first," but a front Order is the same
   card at the same price whenever you Surge it. Once affordable and
   useful, Surge now is always right. Klee's cook-or-cash works because
   waiting grows the bomb and cashing pays Sparks; Kokomi's row pays
   nothing for patience and nothing extra for haste. The only live
   decisions are drafting Surge density and the order you exhaust in, and
   exhaust order is mostly dictated by the hand and the intent, not chosen.
4. *The payoff is never bigger than a card.* The Priestess's moment (§6.1)
   is Watatsumi's Blessing a second time: a heal, capped at entry HP, the
   payoff type you like least. The Commander's "Raiden again" is the only
   moment bigger than a Strike, and §6.3 admits it is companion-gated. The
   Klee brief gives each loop a moment only Klee can produce; draft 5's
   loops give "a good card, twice."
5. *Over-complication.* Seven keywords (§10, pick 7) against LAW:225's
   two; two of them, Order and Tactics, are bookkeeping the player never
   acts on. Rule 6 puts Plans in the row but lets them skip it (fires
   "wherever it stands"), and lets a Surge collect a Plan for 0 Tide, so
   Plan plus Surge with an empty row is 12 damage now for 1 energy and a
   card (Ambush), which dissolves the Strategist's "written last turn"
   identity into a two-card combo. Three gates sit on one replay (draw the
   Surge, the front is the card you want, the Tide covers it); the
   jam-and-eject rule and Change of Plans exist to patch the jam the three
   gates create. The old memory's queue ran p95 9 and worst 31 under
   one-a-turn auto-fire (`BACKLOG.md` EB-234); with no auto-fire and three
   draftable Surge cards in 28 (Breaker, Undertow, War Council) against
   eight feeders, the row will be longer, not shorter.
6. *Two laws are crossed without saying so.* Rule 7 puts Mend on Uncommon
   cards; `LAW.md:198` says true healing is Rare and Exhausts, and her
   identity record (`docs/current/characters/kokomi-identity-record.md`,
   Law 2) says "no healing amendment, ever." R238's pick 3 took that
   default without a LAW line moving. Pick 7's seven keywords rest on
   Klee's ruling, which `LAW.md:225` also does not yet carry.

## 2. Three ways to do better

Each is at most eight rules, a starter, a payoff moment, and a judgement
against your constraints: nothing free, no random companion spam, one
replay per card unless a card returns it, a fuel you build and spend on
purpose, the first-in first-out row kept or replaced with a reason.

### Design 1. Draft 5, tightened (recommended, with pick 2's addition)

1. The Bake-Kurage is always out. It holds the **Tide** (a number, never
   resetting by itself) and her **Tactics**: a row of cards in the order
   they were exhausted, each with its target.
2. **Tide** is added by her cards, and by 1 whenever a card of hers Exhausts.
3. Exhaust is the only door: a card she owns that Exhausts joins the back
   of the row, unless it is Spent.
4. **Surge**: the jellyfish carries out the front card at no energy for
   3 Tide per printed energy (0-cost free), one card per Surge; if the Tide
   is short it does nothing and the rest of the card still happens. A Surge
   card's other half is a whole card (Rising Tide: Deal 6. Surge), and one
   Common is the bare verb (Say the Word: 0 energy, Surge).
5. **Spent**: a card the jellyfish has carried out goes to the exhaust pile
   marked, and never joins the row again; Moon's Reflection may still
   return it to hand.
6. **Plan**: "at the start of your next turn, X." A Plan card goes to the
   discard pile like any card; it is not in the row and pays no Tide. The
   Art of War: it also happens now.
7. **Mend**: heal, never above entry HP, on Rare Exhaust cards, as LAW has
   it (pick 6 can widen this). The Garment is retired as a keyword.
8. **Flawless Strategy**: she cannot gain Strength; Strength becomes Tide.

Starter, ten cards: Water's Edge x2 (1: Deal 6), Coral Guard x2 (1: Block 5),
Salt Line x2 (1: Exhaust. Block 7), Kurage's Oath x1 (1: Tide +4), Rising
Tide x2 (1: Deal 6. Surge), Stolen Chapter (1: Plan: draw 2). Relic,
**Tamakushi Casket**: the jellyfish never leaves, and the first card it
carries out each combat costs no Tide. Tide supply per cycle is 6 (the Oath
and two Exhausts); demand is 6 (two Salt Line replays); the relic pays the
first, so the second waits on the Oath, and "feed or spend" is on the table
by turn three of fight one. The Priestess turn is now 3 energy for 14 Block
and 6 damage against the basics' 10 and 6: four Block for the sequencing
and the Tide, never a wash, never busted.

**The payoff moment** is her Burst. *Nereid's Ascension* (Rare, 2 energy,
Exhaust): "For 2 turns, at the start of your turn the jellyfish carries out
your front Tactic at no Tide." The one time the list runs by itself, paid in
2 energy and the card, bounded to two plays, and Nereid's Ascension itself
Exhausts, so it can come back once for 6 Tide. It is the Rare that breaks
rule 4, the way Sparks 'n' Splash breaks Klee's rule 7.

Judged: nothing is free (energy or Tide on every play; the Burst is a paid
Rare); no random door (Rally chooses, Exhaust companions enter themselves,
one per Surge); one replay (Spent); the fuel is built by Skills and Exhausts
and spent only when a Surge card says so; the row is kept. To build: a
Surge op that calls `KurageMemory.Fire`, the fired copy routed to the pile
with a flag instead of removed, the Burst as a power that calls `Fire` with
the price waived at turn start; Plans stay in `KokomiPlan.cs` untouched.
Removed: the Plans-in-row merge, Exert, the pulse, the Garment power.

### Design 2. Prepared Tactics (Design 1 plus a reason to wait)

Rules as Design 1, with rule 4 amended: **a card in the row is Prepared: it
gains +1 damage and +1 Block for each of her turns it has waited, and the
jellyfish carries it out at that size.** The strip already shows the front
card and its price; it shows the preparation count beside it.

Same starter. The payoff moment is the Burst again, but now the list
unspools at prepared sizes: a Salt Line that waited three turns is 10
Block, a Blessing that waited four is Mend 16. The every-turn decision
becomes real: Surge the front now at 7, or hold for 9 while the enemy's
wind-up, the Surge card in hand, and everything queued behind it argue for
now. First in first out serves the most-prepared plan first, which is the
strategist's story: she wins the fight before it starts.

Judged: as Design 1, and "watch it rise" is answered by the row (waiting
delays everything behind the front), the intent, and the fight ending. The
honest risk is overlap: this is Klee's rule 1 (a number that grows per
turn) on cards instead of enemies. The mechanics differ (a queue with one
front and a sequencing decision versus bombs on bodies with a targeting
decision), but two kits that "grow while they wait" may read as one idea
twice. If that overlap bothers you, the alternative that still gives
holding a value is your own R226 pulse fused with the row: the front card
has a small passive by type while it waits (an Attack: the jellyfish deals 3
to its target at end of turn; a Skill: 3 Block at turn start; a Power: Tide
+1), lost when it is Surged. That is the Defect's orb passive, the source
game's interval-acting jellyfish, and it is a pick, because your B3 note
wanted the memory to replace the jellyfish's own action, not sit beside it.
To build either: a fire-time modifier in `Fire` (the Block seam is already
there), or one power reading the front entry's type.

### Design 3. The Battle Plan (no row; for comparison, not for tonight)

1. The Bake-Kurage is always out and holds her **Plans**: cards she has paid
   for and not yet carried out, in the order she made them.
2. Any of her cards may be **Planned** instead of played: pay its energy
   now, choose its target; at the start of her next turn, before the draw,
   the jellyfish carries it out at the bonus printed after "Plan:" (Water's
   Edge: Deal 6. Plan: Deal 9). It then goes to the discard pile.
3. Nothing is carried out twice and nothing carries over.
4. Some cards read the plan's turn: "Plan: if you took damage this turn,
   +X" (Contingency), "Plan: if the enemy Blocked, ignore Block" (Feint).
5. Companions can be Planned like any card; a Planned Raiden is the
   Commander's moment.
6. **Mend**: Rare, Exhaust, never above entry HP.
7. She cannot gain Strength; a Strength gain adds 1 to each Plan she holds.
8. Nothing fires by itself except a Plan she paid for the turn before.

Starter: Water's Edge x4 (Deal 6 / Plan: Deal 9), Coral Guard x4 (Block 5 /
Plan: Block 8), Kurage's Oath (Plan only: draw 2, gain 1 energy), Stolen
Chapter (Draw 1 / Plan: draw 3). Relic: the first Plan each combat also
happens now. Payoff: three planned Attacks land for 27 on the boss's wind-up
before she draws a card; the Rare "The Moon Overlooks the Waters" carries
every Plan out twice.

Judged: nothing free (every Plan is paid a turn early; the bonus is interest
on the delay); no random door; no replay at all; no bank, and no row. That
last is the reason it is here: the Tide and the row are the two things every
draft has struggled to make readable, and this puts the whole decision on
the card face. Why not tonight: it throws away the memory you like more than
the Tide, its failure mode is the "delayed Strike" the Klee brief names, and
it is the largest build (the `KokomiPlan.cs` seven fixed clauses would
become the general enrol-and-replay `KurageMemory.cs` already does, with a
bonus). Keep it as the fallback if the row fails your next play.

## 3. Lore

**Right.** The always-out jellyfish (in the source game, Tamakushi Casket
keeps the Bake-Kurage fielded through her Burst); no Strength for no crit;
the biggest HP bar; Plan as the strategist raised on treatises; Gorou
executing what she writes; C1, C2 and C6 mapped sensibly; retiring her
"energy" as a price. All of that is the repo's audit and my knowledge agrees.

**Wrong or missing.**

- *The relic's name.* "Tamanooya's Casket" is not a Kokomi talent. Her first
  ascension passive is **Tamakushi Casket** (repo: `kokomi-kickoff-v1.md`
  §2.5 and `docs/notes/kokomi-cards-provenance.md:20`; source game agrees).
  It was built under the wrong spelling (`klee-mod/KleeCode/Relics/TamanooyasCasket.cs:64`).
  Under draft 5 the relic does what the passive does, so the name fits once
  spelled right; the brief should also say it reverses the earlier ruling
  that put "Pearl of Wisdom" on the relic (`tier0/constants.py`, Charge block).
- *Rare names.* `LAW.md:193`: constellations for Rares. The Art of War, The
  General's Banner and Watatsumi's Blessing are not. Unused constellations:
  C3 *The Moon, A Ship O'er the Seas* (the Blessing), C4 *The Moon
  Overlooks the Waters* (Art of War), C5 *All Streams Flow to the Sea* (the
  Banner). Sango Isshin and The Clouds Like Waves are right.
- *The jellyfish does nothing by itself.* In the source game it heals and
  hits on an interval; here it is a bookkeeper. Design 2's passive variant
  restores a trace; your B3 note argues against it. A pick, not a defect.
- *HP scaling.* Her Burst and jellyfish scale off Max HP (source game).
  Nothing in draft 5 reads her HP. One Rare could ("deal damage equal to a
  fifth of your Max HP to all enemies," 16 at 80) and would be a payoff
  number that is hers, legal under the no-self-damage law.
- *Small ones.* §3's "highest base HP in the source game" is not right (Hu
  Tao, Zhongli and Yelan are higher; she is top-tier); Song of Pearls in
  the source is a Garment damage bonus, borrowed here for an unrelated
  effect; the R236 companion document §2 and Shinobu's row still say Exert
  is her rule.
- *"Orders."* The Bake-Kurage takes no orders in the source; the Resistance
  does. Your word, **Tactics**, is what a strategist writes and is the
  better name for the row. The used-card tag then cannot also be Tactics;
  **Spent** says exactly what it is in one plain word, and only two cards
  print it (Moon's Reflection, the Banner). Keep Surge, Plan and Tide.

## 4. Recommendation

Keep draft 5's skeleton and amend it before the build, in this order: the
starter becomes two Salt Lines, two Rising Tides at Deal 6, one Oath; Surge
cards carry a whole card and one 0-cost Surge enters at Common, with Surge
density near eight of 28 and feeders cut to five; Plans leave the row and
become delayed effects on ordinary cards; the Garment becomes the Burst
window (Nereid's Ascension, Rare, the rule-breaker); the row gains a reason
to wait (pick 2); Mend follows LAW at Rare unless you amend it; the printed
keywords are Tide, Surge and Plan, with the row and the tag living in the
strip; the relic is Tamakushi Casket and the Rares take constellations; and
the slice re-points its rule 3 at the queue `KurageMemory.cs` already keeps.
That is a rule change, so it is a play by you, once, after the seats. If
that play still finds the row a ledger, Design 3 is the way out.

## 5. Picks

1. **Direction.** (1) *Amend draft 5 as §4 says* [default]. (2) Build draft
   5 unchanged. (3) Replace with Design 3.
2. **A reason to wait.** (1) *Prepared: +1 damage and Block per turn a card
   waits in the row* [default; the payoff moment and the every-turn
   decision come from it; the Klee overlap is the cost]. (2) The front
   card's passive by type (your R226 pulse on the row). (3) None; draft 5
   as written.
3. **Plans and the row.** (1) *Out of the row: a delayed effect on a normal
   card, no Exhaust, no Tide* [default]. (2) Draft 5's rule 6. (3) In the
   row, and a Surge pays a Plan's Tide like any card.
4. **The Surge price.** (1) *A Surge card's other half is a whole card, and
   one 0-cost Surge at Common* [default]. (2) Draft 5's half-cards at 1
   energy.
5. **Her Burst.** (1) *Nereid's Ascension is the Rare that lets the
   jellyfish run the list for two turns* [default]. (2) Keep the Garment
   (Attacks Mend 2) at Uncommon. (3) Both.
6. **Mend and LAW.** (1) *Keep `LAW.md:198`: Mend on Rare Exhaust cards
   only; the Uncommon heals become Block* [default; the standing law and
   your "no healing amendment, ever"]. (2) Amend LAW to draft 5's rule 7.
7. **Names.** (1) *Row Tactics, tag Spent, relic Tamakushi Casket, Rares by
   constellation* [default]. (2) As drafted: Orders, Tactics, Tamanooya's.
