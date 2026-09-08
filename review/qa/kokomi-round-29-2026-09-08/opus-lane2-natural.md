# Kokomi round 29 — Opus blind seat, lane 2, natural draft

## Identity

- **Model and seat:** Claude Opus 5 (1M), blind TESTER seat, lane 2, natural draft.
- **Run seed:** not printed on any screen the bridge showed me. I never saw a seed line, so I cannot report one.
- **Character:** Kokomi (never named on a screen either — I am inferring it from the starting relic **Tamakushi Casket** and the **Bake-Kurage** that shows up in every combat; the bridge never printed a character name).
- **Ascension the run opened at:** not printed. The first battle screen read `HP 64/80`, i.e. 80% of max on floor 1 before I had taken a hit, which is the A3 opening HP; the screens never said so.
- **Act and boss:** act 1. The floor-1 map printed **"At the top of this act: Soul Fysh"** — I never reached it.
- **Actions accepted:** 54 of 240.
- **Termination reason:** **not a budget.** After act 54 (`go "Unknown (path 1)"`, accepted as `ok Traveling to Unknown at (2,6)`) the bridge stopped answering. Every subsequent `observe` — sixteen of them across roughly fifteen minutes — died with
  `understudy.bridge.BridgeError: bridge connection failed at http://localhost:15528/api/v1/singleplayer: TimeoutError: timed out`.
  The move onto floor 7's Unknown room was accepted and then no screen ever rendered. This is not the documented `TOOL-BLOCKED: <state_type>` refusal — it is the bridge going silent — so I stopped rather than diagnose further, as the brief requires. I did not tear the lane down.
- **HP trajectory:** 64/80 (floor 1, pre-fight) → 61 → 53 after fight 1 → 48 → 44 after fight 2 → 40 after fight 3 → **40/80 at the hang**. Total 24 HP lost over three fights, none of it to a fight I mismanaged badly.
- **Gold:** 99 start → 109 (fight 1) → 117 (fight 2) → 45 (spent 72 in the shop) → **60** after fight 3's 15.
- **Potions held:** **Duplicator** (taken from fight 3's rewards, never used — I never saw its text, only the reward row).
- **Deck at the end** (as far as the bridge ever showed it — no screen prints a deck list, so this is assembled from what I drew and what I took):
  starting 4× Strike, 4× Defend, **Slack Water**, **Kurage's Oath**; added **Riptide** (fight 1 reward), **War Council** (fight 2 reward), **Opening Gambit** (fight 3 reward), **Sango Isshin** (shop, 72g); plus **Clumsy** (curse, from the This-or-That event).
- **Relics at the end:** **Tamakushi Casket** (starting), **Winged Boots** (Neow, spent to 0 charges), **Unceasing Top** (This-or-That event).

**Neow pick: Winged Boots.** The other two both wrote on my deck — Kaleidoscope hands you two card rewards *from other characters*, and Neow's Sacrifice staples a Guilty in — and I was told this run is a natural draft, so the one option that leaves the deck alone was the one to take. In hindsight it did almost nothing: the three charges bought me nothing the map wasn't offering anyway.

---

## Fight 1 — Seapunk [A], 46 HP

Opening hand: Strike, Defend ×3, Slack Water. 3 energy. The jellyfish is already on the field on turn one with nothing written on it.

**Turn 1** (enemy: Attack 11). Played **Slack Water** on A, then **Strike**, then **Defend**.
The decision here was face-up versus written, and the screen actually let me settle it by reading: Slack Water prints `Deal 4 damage. Apply 1 Weak. Dusk Plan: Apply 1 Weak to ALL enemies.` Against one body the written line drops the 4 damage and keeps only the Weak, and Dusk means it lands at end of turn either way — so face-up is strictly the same Weak plus 4 more damage. **Rejected: writing Slack Water's Dusk Plan**, because with a single enemy "ALL" buys nothing. Second choice was Strike-plus-Defend versus Defend×2: I took 3 unblocked to land 6 more, at 64/80 that was cheap.
Screen and outcome agreed exactly: 46 → 34 = 12, i.e. Slack Water's 4 plus **Tamakushi Casket's 2** (the Weak set it off) plus Strike's 6. And 11 damage at Weak became 8, minus 5 Block = the 3 I lost.

**Turn 2** (enemy 34 HP, intent `2x4`). Wrote **Kurage's Oath** on the Bake-Kurage, then two Strikes.
This was the fight's real decision and it was a genuine one: Oath prints `Deal 3 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.` One energy buys 3 now or 7 next turn. **Rejected: three Strikes for a flat 18**, and **rejected: Oath face-up for 15 now.** 12 now + 7 banked beat 18 now by a point and, more to the point, put the 7 on the far side of the enemy's turn where I could see whether the jellyfish paid out. It did.

**Turn 3** (enemy 15 HP, intent Empower + Defend). The carry-out fired first — 22 → 15, exactly the 7 written — and then I played Strike, Strike, Slack Water for 18 and killed it.
This is the case the brief warns about: turn 3 had no rejected alternative worth the name, because the enemy was telegraphing **Block** and everything in hand was lethal on the total. But it was not a dead turn — it was **the turn-2 Plan paying off**, and specifically it beat the enemy's Block by arriving before it. The end-of-fight screen printed the carry-out ledger cleanly:
`Bake-Kurage: Kurage's Oath, 7 — the 7 is damage. / Seapunk lost 7 HP.`

Reward: 10 gold and a card. Offered **Sea-Salt Prayer / Rally / Riptide / Gorou — Crystal Collapse**; took **Riptide** (`Deal 9 damage to ALL enemies, and 4 more to each enemy with a debuff. Plan: Deal 13 damage to ALL enemies`), because I already had two Weak sources and the +4 rider reads as free.

---

## Fight 2 — Toadpole (1) [A] 23 HP, Toadpole (2) [B] 24 HP

**Turn 1** (A buffs, B attacks 7). Played **Slack Water on B**, then **Riptide** face-up.
The decision was which body to Weak, and it decided both the damage and the damage I'd take: Riptide's rider keys off *having a debuff*, so the Slack Water target eats 13 instead of 9, and Weak on the attacker also shaves its 7. Putting the Weak on B did both jobs at once. **Rejected: Slack Water on A** (Weak wasted on a buffer), and **rejected: writing Riptide's 13-to-ALL Plan**, because the Plan line drops the +4 rider entirely and I wanted the bodies low now. The screen confirmed the arithmetic to the point: B 24 → 5 (4+2 casket, then 13), A 23 → 14 (9), and B's printed intent visibly re-rendered from **7** to **5** once the Weak landed. That re-print is the single most useful thing the bridge does.
**Then I hit my own refusal.** I asked for `play "Strike" on "B"` to finish B off at 5 HP and got
`'Strike' cannot be played right now: you do not have enough energy.`
That is my miscount, not the tool's — Slack Water 1 + Riptide 2 is the whole 3 — and the refusal named the reason precisely. B lived and hit me for 5.

**Turn 2** (A 14 HP with **Thorns 2** and intent `3x3`, B 5 HP buffing). Wrote **Kurage's Oath** on the jellyfish, **Strike** on B (killing it), **Defend**.
Best decision of the run, and it came straight off printed text. Thorns 2 reads `When hit by an attack, deal 2 damage back. Every card hit is one, a Skill's too` — and the Plan glossary reads **`A carry-out is not a hit: no when-hit power fires.`** So routing Oath's damage through the Bake-Kurage dodges Thorns entirely, where playing it face-up would have cost me 2. **Rejected: Oath face-up plus two Strikes** (28-ish damage but 4 back off Thorns and A still alive), and **rejected: Oath written plus two Defends for a zero-damage turn**, because that left B alive to buff a second time and it was B's Empower that had handed A its Thorns in the first place. Killing the buffer and banking the Plan was worth taking 4.
The screens backed the rule: 48 → 44 is exactly the 9-damage attack minus 5 Block, with **no Thorns tick anywhere** — the carry-out genuinely is not a hit.

**Turn 3.** Carry-out printed `Kurage's Oath, 7 — Toadpole (1) lost 7 HP`, A at 7, and I killed it with two Strikes. No rejected alternative on the turn; again, that is the turn-2 Plan landing, not a hollow turn.

Reward: 8 gold and a card. Offered **Shell Guard / War Council / Vanguard / Gorou — Juuga**; took **War Council** (`Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies`) — one energy that debuffs every body *and* fires the casket once per body, which is Riptide's rider turned on for the whole row.

---

## Interlude — event and shop

**This or That?** (floor 4). Took **That**: a **Clumsy** into the deck for a random relic. Clumsy is Unplayable **Ethereal**, so it exhausts itself out of the fight the turn it appears; at 44/80 the six HP the other option wanted mattered more than a card that deletes itself. Got **Unceasing Top**. (I noted at the time that this puts a non-drafted card in a "natural draft" deck; it is an event, not a draft, and Clumsy cost me nothing in fight 3 — it sat in hand one turn and exhausted.)

**Shop** (floor 5), 117 gold. Bought **Sango Isshin** for 72: `Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.` That is 8 or **20 to every body**, and the switch is a thing I control by having written something the turn before — the exact shape of decision the kit seems to be built around. Rejected **Feint** (same idea, half the payoff), **Treatise** (draw engine I couldn't yet feed), **Change of Plans** and **Second Thoughts** (both interesting — one pulls a Plan forward, one takes one back — but I had no Plan density to abuse yet), and the relics on price. **I never got to play Sango Isshin.** It sat in my hand for one turn of fight 3 with no Plan written and therefore read as a 2-cost, 8-damage card, which is the worst version of it.

---

## Fight 3 — Corpse Slug (1) [A] 25 HP, Corpse Slug (2) [B] 26 HP

Both printed `Ravenous 4 — When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength.` That one line reframed the whole fight before I played a card.

**Turn 1** (A debuffs, B attacks `3x2`). Played **War Council**, then **Riptide**, both face-up.
The order was the decision: War Council's Weak-to-ALL makes both bodies "an enemy with a debuff", so Riptide reads 13 apiece instead of 9, and the casket adds 2 apiece on top of that for the debuff itself. 15 to each body for three energy. **Rejected: writing War Council's Plan** (5 + Weak to all next turn) — it is more raw damage across two turns, but it leaves this turn at 9-and-9 and I wanted both slugs under half before Ravenous became a question. Screen agreed exactly: 25 → 10, 26 → 11.

**Turn 2** (A 10 HP `3x2`, B 11 HP attacking for 8; I had **Frail 2** on me, `Gain 25% less Block`, and my Defends printed **3** instead of 5 — nice, the card face itself re-rendered). Played **Slack Water on A**, **Strike on A** to kill it, then Defend.
This was the fight's real decision and it was a strange, good one: killing A *deliberately fed it to B*. Ravenous says the survivor eats the corpse and becomes **Stunned** — `Prevent the enemy from acting on its next turn` — so the price of handing B four Strength was that B skipped the turn it was going to hit me for 8 with. **Rejected: Sango Isshin on B for 8** (no Plan written, so it was the small half of its own text) and **rejected: spreading damage to keep both alive**, which just eats 14 to the face. The screens confirmed it: I ended the enemy turn on **40 HP, unchanged**, and B came back at 11 HP with `Strength 4` and an intent of **12**. I traded 8 damage now for a bigger number later and then never had to pay it —

**Turn 3.** — because two Strikes for 12 killed B at 11 before it swung. Again a turn with no live alternative, and again it was the previous turn's choice cashing out rather than an empty turn.

**One printed-text defect, worth writing down:** on the round-2 battle screen of this fight, the entire `## The other side` block rendered **twice**, every line duplicated — both slugs, both intents, both Ravenous lines, and the trailing italic note. It was cosmetic and the numbers agreed with each other, but a seat reading fast could easily miscount bodies off that screen.

Reward: 15 gold, **Duplicator**, and a card. Offered **Flank / Tide Wall / Opening Gambit / Gorou — Inuzaka All-Round Defense**; took **Opening Gambit** (`Deal 5 damage. Plan: Apply 1 Vulnerable to ALL enemies. The next Plan carried out with this one deals double damage.`) — the doubler is the first card I'd seen that makes writing *two* Plans in a turn better than writing one, and with Riptide's 13-to-all sitting in the deck that is a 26-to-all line I wanted to try. **The hang took the fight where I'd have tried it.**

---

## The kit, after 3 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three shapes, and all three are the same underlying question — *do I take this now or write it on the jellyfish?*

1. **On the turn — face-up versus written, priced in tempo.** Kurage's Oath is 3 now or 7 next turn for the same energy (fight 1 turn 2, fight 2 turn 2). Riptide is 9-to-all-plus-4-per-debuff now, or a flat 13-to-all next turn (fight 2 turn 1, fight 3 turn 1). These are not close calls dressed up as choices; they genuinely swap depending on how many bodies are up, whether anything is debuffed yet, and whether I can afford to be down damage for one enemy turn. That is a good axis.
2. **On the turn — written to dodge a rule, not to bank damage.** Fight 2 turn 2, where `A carry-out is not a hit: no when-hit power fires` turned the Plan into a Thorns-eraser. This was the moment the kit stopped feeling like "delayed damage" and started feeling like it had a second dimension. It traded a turn of tempo for taking zero retaliation.
3. **Earlier in the fight, and at the draft — sequencing debuffs so a later card's rider turns on.** War Council before Riptide, Slack Water onto the body Riptide is about to hit, every Weak also firing Tamakushi Casket for 2. Each of these was decided one card earlier than it paid, which is the good kind of decision. And the draft carried it: taking Riptide at fight 1 is *why* fight 3's opening turn had a decision at all, and taking War Council is why the Riptide rider was on for both bodies instead of one.

The Corpse Slug turn (fight 3, turn 2) was the best decision of the run and it belongs to the enemy design as much as the kit: killing on purpose to buy a Stun.

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend is automatic and slightly embarrassing.** 5 Block, 3 under Frail, on a character whose whole apparatus is about pre-committing. It never interacted with the Bake-Kurage, it never had a Plan line, and every time I played one it was because I had a spare energy and nothing to spend it on. **Tide Wall**, which I was offered and passed, prints `Plan: Gain 3 Block for each Plan carried out with it` — that is the Defend this kit wants, and the fact that the *basic* Defend has no relationship to the jellyfish at all is the flattest thing in the deck.
- **Strike is Strike.** Fine, but three of my five turns of "lethal maths" were Strike-Strike, and those are the turns with nothing in them.
- **Slack Water's written line never once looked worth it** — see the Debrief.
- Nothing else read as unplayable. **Sango Isshin** never got to be worth playing, which is a different complaint (b/c boundary): the card is 8 damage or 20-to-all and I drew it on the one turn of the run with nothing written, so it presented as the dead half of itself.

**(c) What I could not understand, or that contradicted its printed text.**

- **Nothing contradicted its text.** Every number I predicted off a card face came out right to the point: the casket's 2 on every debuff, Riptide's 13-vs-9, Oath's 7, Weak turning an 11 into an 8 and a 7 into a 5, Frail turning Defend's 5 into a printed 3. That is a real compliment and I want it on the record.
- **What I could not resolve:** the **Elemental Reaction** block is the longest thing on every combat screen and it ends, every single time, with `NO REACTION IS REACHABLE HERE`. Across three fights I read several hundred words about auras being consumed and reactions being hidden by a relic re-applying the same element inside one beat, and not one of it ever applied. Hydro aura ticked up and down on bodies for the whole run and did **nothing I could observe**. I could not tell you what an aura is *for* in a Kokomi-only deck. The two Geo companion cards I was offered would presumably have shown me; passing on them meant the entire elemental layer stayed decorative.
- **Second uncertainty:** whether a **Dusk** Plan (Slack Water's, which resolves at *end* of the turn it was written) counts as "the Bake-Kurage carried out a Plan this turn" for **Sango Isshin**. Reading the two faces together I concluded it does not fire in time to matter, since Sango would have to be played before the Dusk resolves — but I never got to test it, and nothing on either card says.
- **Third:** the multi-part intent note (`this page makes no claim about which of them the enemy will perform`) is honest but it made the Seapunk's Empower+Defend turn unreadable. I planned around "it will block" and got lucky.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted: Defend.** Not because it is weak but because it is inert — the only card in the deck that the Bake-Kurage cannot see.
- **Happiest to draw: War Council.** One energy, every body Weak, the casket fires once per body, and Riptide's rider comes on for the whole row. It made the other cards better, which Riptide (happiest to *have*) does not.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a real one, though a small one.** Turn one of fight one I had Slack Water in hand with a Bake-Kurage already on the field and a printed Dusk Plan line, so the very first card I played was a face-up-versus-written question. It resolved obviously — one enemy, so "ALL" is worth nothing and the written line just discards 4 damage — but I had to read two card faces and a keyword to know that, and the second question on the same turn (Strike + Defend, taking 3, versus Defend + Defend, taking 0) was a live tempo call. Compare that to a Strike-Strike-Defend opening and the kit is ahead on the first turn it gets.

---

## Debrief

> Name every turn where you held Breakwater or Slack Water. For Breakwater: how many Plans the Bake-Kurage was holding when the turn ended, by your own count, and the Block it paid, checked against each other; and whether you wrote the other Plans before or after it. For Slack Water: whether you played it face-up or wrote it, the number of bodies, what was telegraphed, and when the Weak landed relative to the enemy's attack.

**Breakwater: never. I never held it, never drew it, never saw it printed on any screen** — not in a hand, not in a card reward, not on the shop shelf. It was not in my starting deck and none of the three reward screens or the shop offered it. So there is nothing to check a Block payment against, and the question's whole second half is unanswerable from this seat. Recording that as the answer rather than dressing it up.

**Slack Water: four turns. I held it on four turns and played it on all four, face-up every single time. I never once wrote it on the Bake-Kurage.**

1. **Fight 1 (Seapunk), turn 1.** Face-up, on A. **One body.** Telegraphed: `Aggressive (Attack) — the number on its icon is 11`. The Weak landed **before** the attack — I played it first in the turn, and the enemy's swing came in at 8 (11 × 0.75, rounded down), of which 5 was eaten by Defend, so I lost 3. Face-up because with one body the Dusk line's "Weak to ALL" is the same single Weak minus 4 damage.
2. **Fight 1 (Seapunk), turn 3.** Face-up, on A, as the third card of a lethal 18. **One body.** Telegraphed: `Empower (Buff)` + `Defensive (Defend)`. The Weak here was **irrelevant** — the enemy died on that same turn and never attacked again, so the Weak never met an attack at all. The 2 damage the casket paid for applying it, however, was part of the lethal.
3. **Fight 2 (Toadpoles), turn 1.** Face-up, on **B**. **Two bodies** — the only turn where the Dusk "Weak to ALL" line had anything to say, and I still played it face-up, deliberately: I needed a debuff on a body *before* Riptide resolved so Riptide's `4 more to each enemy with a debuff` would turn on, and Dusk resolves at end of turn, which is too late for that. Telegraphed: A `Empower (Buff)`, B `Aggressive (Attack) — 7`. So I put the Weak on the one body that was actually going to hit me. It landed **before** B's attack and the screen visibly re-printed B's intent from **7** to **5**; that 5 is what I took, having spent my last energy elsewhere. Writing it instead would have Weaked the buffer too — worth nothing that turn — and cost me 4 damage and Riptide's whole rider.
4. **Fight 3 (Corpse Slugs), turn 2.** Face-up, on **A**, as the first half of a kill (4 + 2 casket = 6, then Strike for 6 into A's 10). **Two bodies alive when I played it, one after.** Telegraphed: A `Aggressive (Attack) — 3x2`, B `Aggressive (Attack) — 8`. The Weak landed on A **before** A's attack but A **died on that same turn**, so the Weak again never met a swing — and B, the body whose 8 I actually cared about, was Stunned by eating A and did not attack either. So the Weak was pure casket fuel: its only contribution was the 2 damage that applying it produced.

**The pattern, stated plainly:** on three of the four turns the Weak was either wasted (the body died first) or was worth less than the 4 damage the written line gives up, and on the fourth — the one turn with two bodies where the Dusk line was live — writing it would have actively cost me Riptide's rider. **Slack Water's Dusk Plan never once looked like the right half of the card**, and I want to be clear that this is not me failing to consider it: I priced it on all four turns and it lost all four. The card's real job in my run was "cheapest way to make the Tamakushi Casket fire", which is a rider on a relic, not a decision.

---

## Non-blindness declaration

**Repo files read: none.**

- Tools used: **Bash** (for every game command and for one scratch call), **Read** (once, on my own brief at `C:\Users\Monty\AppData\Local\Temp\claude\C--Users-Monty-Documents-GitHub-GItS\913fe618-57ea-4814-a6fd-395408534019\scratchpad\r29-seat-lane2.md`, which the brief itself permits and which is not a repo file), and **Write** (once, this file).
- Every game command was one of the two allowed forms, `GITS_LANE=2 "C:/Users/Monty/Documents/GitHub/GItS/.venv/Scripts/python.exe" -m understudy.blindplay observe` and `... act "<command>"`, and nothing else. I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no bare `python`.
- **Commands run outside the two allowed ones — the complete list:**
  1. `mkdir -p ".../scratchpad/lane2" && echo "neow: winged boots (keep deck natural)" >> ".../scratchpad/lane2/notes.md"` — one scratch note in the scratchpad, written before fight 1 and never read back.
  2. Shell wrappers around the allowed commands, which ran nothing new: `for c in ...; do ... done` loops issuing several `act` calls in sequence, and `| sed -n '...'` / `| tail -n` / `| sort -u | head` pipes to re-read one block of an `observe` I had already been shown. The `sort -u` on fight 3's round-2 enemy block is how I confirmed the duplicated `## The other side` render described above rather than a copy in my own pipe — the duplication is in the bridge's output, since an unpiped `observe` on that screen printed it twice as well.
- I did not tear the lane down. The lane is left as it was when the bridge stopped answering: floor 7 of act 1 entered, no screen rendered, 54 acts of 240 spent.
