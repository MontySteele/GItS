Status: OPEN (picks 1 to 4)

# Kokomi goes back in the oven: what failed, and three ways out

Written 2026-09-02, the night you played her prototype. The slice's own gate
says a fail on question 1 goes back to the brief's rules, not to the card
numbers, and you failed it in plain words: you never wanted to play a hold
or a surge card. This is the Paper stage again. Nothing here is built.

## 1. What the run and the seats said

Three players, three readings, one arithmetic.

- You: "exert 2, tide +5 seems strictly worse than just playing a basic
  attack"; Salt Line "barely better than basic defend and exhausts"; the
  pulse "incomprehensible"; Exert "a tax on cards I don't want to play";
  "I didn't really like any of the cards"; and Tide "less interesting than
  Memory was, but perhaps that's because these cards don't really seem
  to... work."
- The Opus seat, a night earlier: "Kurage's Oath is 1 energy + 2 HP for 5
  stored damage, and Water's Edge is 1 energy for 6 immediate damage ...
  every time I did the arithmetic honestly the boring line won"
  (`review/qa/blindplay/kokomi-overhaul-r1-opus/record.md`).
- The Codex seat: Oath and Rising Tide "became mostly dead after the first
  combo" (`review/qa/blindplay/kokomi-overhaul-r1-codex/record.md`).

Nobody misread the kit. They read it correctly and it lost.

## 2. Why Tide failed, in four sentences

The payoff is a number: Surge deals the Tide once, to one enemy, and the
Tide is spent. Every step toward it costs something felt now (energy, HP,
a turn not attacking) and the number it buys is smaller than the basic
attack it displaced, so the "bet" has no side worth taking. The thing that
was meant to make holding feel good, a 2 HP pulse capped at 8, is too small
to change a decision even when it can be seen, and it could not be seen.
Klee's loop works because its payoff is a moment (a 22 goes off); Kokomi's
was a ledger.

Re-pricing Oath would have fixed the arithmetic and not the shape. I staged
that re-price this evening and pulled it when your verdict came in.

## 3. Three ways out

### Direction A. Memory is the core, Tide is its fuel [recommended]

Your Kurage's Memory (`review/ruled/kokomi-kurage-memory-2026-08-29.md`
§11.1, your words) already exists in both engines behind a flag:
`klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs` and tier0's
`C.KURAGE_MEMORY`, with the memory strip live-accepted on `0.2.1506+proto`
(EB-198) and a drafted-deck cadence read (EB-234: the memory fired on 61% of
turns, rising by act). What made it point at "companion spam" was that only
Companion cards could enter it, and the companions were weak. Both of those
have moved: the Mondstadt and Inazuma Universals are rebuilt (R236), and the
rule below lets her own cards in.

The rules, one line each, a draft for the brief and not the brief:

1. The Bake-Kurage is always out. It holds **Tide** (a number) and a
   **Memory** (a row of card faces, in order).
2. Her cards add Tide. Any card that Exhausts adds 1.
3. When one of her cards or a Companion card **Exhausts**, the jellyfish
   remembers it, with its target and choices. (Your rule; one door, since
   Muster is gone.)
4. At the start of her turn, if the Tide covers the front memory's price
   (three per energy of its cost, your number), the jellyfish pays and
   plays it. One a turn.
5. **Surge**: the jellyfish plays everything it remembers, now, in order,
   paying nothing; then it forgets them all and the Tide is 0. The wave.
6. **Plan**: a card that says it goes straight into the Memory when played,
   unplayed. The Strategist's whole loop becomes "write it, the jellyfish
   does it next turn," on the same queue, with no second machinery.
7. Flawless Strategy: no Strength; Strength becomes Tide. Unchanged.
8. Nothing fires by itself except the jellyfish's one replay a turn.

What this does to the cards you named. Salt Line (Exhaust, 7 Block) stops
being a worse Coral Guard: it is 7 Block now and 7 Block again next turn
for 3 Tide, and a third time if you Surge. Every Exhaust card in her pool
reads the same way, so Exhaust is her upside rather than her drawback, and
Mend cards (Uncommon and up, all Exhaust, bounded at entry HP as before) come
back once for free. Kurage's Oath is "Tide +4," no HP, and it is the fuel
the replay needs. Exert leaves the base loop (pick 2). The pulse is gone;
the relic is the jellyfish itself plus one thing a new player can read,
"the first memory each combat costs nothing" (pick 3).

Fight one, turn one: Salt Line (7 Block, remembered), Oath (Tide 4), Water's
Edge. Turn two opens with the jellyfish paying 3 and playing Salt Line
again, and the player has seen the whole kit: do a thing, the jellyfish
does it again, feed it so it can. The bet is which cards you let it
remember and when you Surge the row. The three loops keep their names:
Priestess feeds and Surges, Strategist Plans, Commander puts companions in
the row (Gorou's Personal, "play a copy of the last Companion," is the
Memory in miniature and may simply become a Plan).

Costs: the Tide arm's Surge and Plan code is reused with new meanings; the
Memory arm is reused as is; the keyword budget stays at six (Tide, Memory,
Surge, Plan, Mend, Garment). The known risk is the one EB-234 measured, a
long queue (p95 of 9, one run of 31); Surge is the answer to it, and a cap
is a Balance number.

### Direction B. Keep Tide, change the payoff's shape

Surge scales instead of paying once: it hits every enemy, or it halves the
Tide instead of zeroing it, or it deals the Tide plus half again. Exert
leaves the starter. The pulse becomes Block, not healing, so it is visible
and matters to the hit coming in. Cheapest to build (numbers and three
ops), but it keeps the mechanic you called less interesting, and the seats'
arithmetic only moves, it does not go away.

### Direction C. Both banks

Memory as in A, and Surge stays a damage number equal to the Tide, so the
Tide has two spends: fund replays or dump it as a wave of water. Two sinks
on one bank is the shipped Charge problem in a new coat (a bank with two
doors is a bank the player has to price every turn), so I would not.

## 4. What happens next, under A

The brief's §4 rules and §6 loops are rewritten as draft 3 (mine, two
pages, the same format), you rule its picks, the slice is rebuilt on the
existing Memory arm with the Tide arm's Plan and Surge code repurposed, the
seats play, and you play once more because the rules changed. The tooltip
pass (EB-272) and the Tide-on-the-wire fix (EB-273) are being built now and
carry over whatever you pick; the round-one defect rows stay open until the
rebuild says which still apply.

## 5. Picks

1. **Direction.** (1) *A: Memory is the core, her own Exhaust cards enter
   it, Plan is a door into it, Surge plays the row* [default]. (2) B: keep
   Tide, reshape the payoff. (3) C: both banks.
2. **Exert.** (1) *Leaves the base loop; at most one Rare ritual keeps it*
   [default]. (2) Stays on two or three Uncommons as the price of the
   biggest Tide gains. (3) Stays as ruled in the brief.
3. **Healing.** (1) *The pulse is gone; Mend stays only on Uncommon-and-up
   Exhaust cards, bounded at entry HP, and those cards replay once through
   the Memory* [default]. (2) Keep the pulse but make it Block. (3) No
   healing at all.
4. **The starter's plan under A.** (1) *Salt Line as the first memory and
   one Surge card: Water's Edge x3, Coral Guard x2, Salt Line, Kurage's
   Oath x2, Surge card x1, Stolen Chapter as a Plan* [default]. (2) A
   Plan-first starter: two Plan cards, no Surge card.

Then: the brief's draft 3, and the picks it raises.
