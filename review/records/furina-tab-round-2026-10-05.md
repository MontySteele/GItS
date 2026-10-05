# Furina (the Salon's Tab kit) seat round, 2026-10-05

**What ran.**
- Build 0.2.4423, the ruled slice (`review/active/furina-research-proposal-2026-10-05.md`): 29 cards, ascension 0.
- Two lanes, with a Sonnet seat for each act and only a state handoff between acts. Scope was acts 1 and 2.
- Raw records are in the session scratchpad and are gitignored.

| Lane | Seed | Act 1 | Act 2 |
|---|---|---|---|
| 1 | TNB6SGF1S94N | Ceremonial Beast, ended 78/85 | Kaiser Crab, ended 27/85. Fell to 8 HP, and Fairy in a Bottle fired |
| 2 | VD4YYMH1U0JR | Ceremonial Beast, ended 43/78 | lost to Kaiser Crab, floor 33 |

Both lanes took Arcane Scroll at Neow and got Universal Revelry. That is one of the slice's four Rares, so both runs played the same deck: Revelry plus Bravura.

**Verdict: the core works, but the deck converges.** Taking a hit or Blocking it is a real choice, and it shows on the enemy's intent. One run cleared act 2 and one lost there. Both played the Crowd archetype only.

## What played well
- **Banking Fanfare against your own HP was the decision, every fight.**
  - Lane 2, act 2, fight 6, turn 2: "ate 17 and 3 x 7 on purpose with Revelry and Lynette up, Fanfare 16 to 84, then a 176 Bravura."
  - Lane 1, act 2, fight 9: two Soloist's Solicitation into Spiny Toad thorns gave 14 Fanfare each, and a turn-2 Bravura killed it.
- **Banking can lose the run, and it did.** Lane 2 held 81 to 113 Fanfare for two turns at the Kaiser Crab, waiting for Let the People Rejoice. Then Bravura+ (261) killed Crusher, Crab Rage gave Rocket 99 Block, and Rocket killed the seat. The seat said this itself.
- **Act 1 frontload holds.** Drain modes beat Strike from fight 1, and both seats cleared act 1 without trouble.
- **Repay ordering was felt, once per lane.** Drain before Pneuma Refrain netted 0 HP for 10 Fanfare (lane 2, act 1, fight 8).

## What did not
- **Revelry plus hits is the loop the paper warned about.** Sec.15 named it: about 6 damage per HP lost, "so Blocking worked against her own plan". Sec.17 put hits back into Revelry to fix the act-2 boss read. The seats then played that loop exactly:
  - Bravura 86 on a 19-HP enemy, and 258 on the act-1 boss (lane 1);
  - 252 on Rocket, 134 more than needed (lane 1);
  - 261 on Crusher (lane 2).
  Lane 1 named "Bravura at 86 on a 19 HP enemy, nothing to decide" its nothing turn.
- **Drain is a reflex (K3).** In four acts, no seat declined a Drain for any reason except the Drain line. "HP returns after combat."
- **Pneuma never formed.**
  - Repay changed one turn per lane.
  - Salon Solitaire's Repay 2 was "background".
  - Singer of Many Waters, Endless Waltz and Clorinde were never played.
- **The Drain line is unreadable when it bites.**
  - The chooser just vanishes below the line (lane 1, boss turn 3).
  - Below the line, most of lane 2's attacks and Salon's Tab's Energy went grey. "I was never told."
- **Rising Applause** was the never-again card in two acts ("1 per point when Bravura gives 2"). It is a starter card, so it stays.
- **Guest Star: Wriothesley** and **Diona — Signature Mix** were never worth a slot.

## Screen bugs (to fix, no design needed)
1. Rising Applause and Bravura preview damage at 0 Fanfare: "Deals 113" (lane 2, act 2, fight 8, turn 6), 18 and 6 (lane 1).
2. Bravura's preview leaves out Vulnerable's 1.5x (lane 1, act 2, boss).
3. A Drain mode below the line vanishes from the chooser. It should stay, greyed, with the line in its hover.
4. Salon's Tab's chooser reads "Draw" against "Drain", though Drain also draws (both lanes).
5. Surging Waters' Repay with nothing drained does nothing, and prints no warning.

## What to change
1. **Revelry stops doubling hits.** It returns to sec.15's text ("Whenever you Drain or Restore, gain that much additional Fanfare"). The act-2 boss was cleared once without the sim's K6 fix, so the reason for sec.17's edit is weaker. This goes into the pool paper, not a hotfix.
2. **Drain as a reflex:** the paper's pick 6 lever comes first (the Singer rests on a turn with a Drain), before any price change.
3. **The pool to about 40**, so that Ousia and Pneuma can be drafted as plans and not just as side cards. This goes in a paper for [USER].

Not ours: Thieving Hopper stealing Bravura, Hard To Kill 9 capping Fanfare hits, and Crab Rage. These are base-game behaviours.
