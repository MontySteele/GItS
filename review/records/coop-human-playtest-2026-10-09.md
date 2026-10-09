# Human co-op playtest: Klee + Furina, 2026-10-09

**What ran.** Build 0.2.4626+next (`klee-next` 5a940457), two humans in
co-op: [USER] on Klee, a friend on Furina. The notes below are theirs,
lightly ordered. The checks against the sheet are Claude's. Rows are in
`docs/prototype-surface.yaml`, and the rules are in
`review/active/furina-research-proposal-2026-10-05.md` sec.16.

## Furina: what the players said

- **The loop is good.** Fanfare did not matter in act 1, was felt in act 2,
  and dominated act 3. The drain-to-spend ratio was a real drafting choice.
- **She was very strong.** "The numbers on all of the cards seemed kinda
  high." Furina carried the game.
- **Drain rarely took her into danger.** She may need less max HP and more
  Repay cards. The friend suggested making "Drain down to 1" the standard
  rule instead of a Power.
- **There was no scaling apart from Fanfare.** Guest Stars were "insane" in
  act 1 and faded by act 3. The friend wants them to be a real archetype that
  scales, perhaps by spending Fanfare.
- **The small pool was noticeable.** It is 34 cards, against 78 for the
  other kits.
- **Card notes:**
  - Salon Solitaire gives too much free Repay.
  - Interval Bell is too good for a Common.
  - Gentilhomme Usher gives too much Block.
  - There are too many Common AoE cards.
  - Fanfare and Spend both work like a second Energy, which may be fine.
- **Guests seemed to act several times in a row.** This is not a code bug.
  The end-of-turn hook fires once and each guest acts once
  (`FurinaStageHooks.cs`, `StageDirector.EndOfTurn`). Two designed effects
  read as repeats:
  - **Lines trigger without a lunge.** With Clorinde and Sigewinne on stage,
    Sigewinne's Repay and Salon Solitaire's Repay each fire Clorinde's line.
    That is three Electro hits under her name from one act.
  - **A repeat Guest Star play** makes the guest act at once, and it acts
    again at end of turn. The friend played Lyney 31 times, Clorinde 24 and
    Sigewinne 22.

  Two questions go to the guest paper (pick 4): should a line trigger get
  its own cue, and should Clorinde's line read the relic's Repay?

## Checking the notes against the sheet

| Note | What the sheet says | Read |
|---|---|---|
| Free Repay | Salon Solitaire: "At the end of your turn, Repay 2." Each HP repaid also prints 1 Fanfare, so the relic gives 2 HP and 2 Fanfare every turn for nothing | **Agreed.** It is her only passive sustain and her only free Fanfare |
| Drain never dangerous | Drain stops at half the HP she entered combat with, and every drained HP comes back when combat ends | **Agreed, and it explains Usher too.** A Drain costs HP she gets back, so "Drain 3: +6 Block" is close to free. The line also means she can never Drain herself into danger |
| Interval Bell | 0-cost Common: "Draw 1 card. Spend 3: draw 1 card and gain 1 Energy next turn instead." | **Agreed.** A free cantrip that turns Fanfare into Energy is Uncommon work |
| Gentilhomme Usher | 1-cost Common: 7 Block, or Drain 3 for 13 [9 / 17] | **Agreed.** Base Defend is 5 [8]. 13 Block for HP that comes back is above any Common in the base game |
| Common AoE | Three Common attacks hit ALL enemies: Chevalmarin (4, or Drain 3 for 8, Hydro), Tidal Flourish (5, or Spend 6 for 12 Hydro) and Standing Ovation (spend all). Grand Deluge and Let the People Rejoice add two more above Common | **Agreed.** Most base characters have one or two Common AoE attacks |
| Hydro mismatch | Chevalmarin applies Hydro in both modes. Tidal Flourish applies it only when you Spend | **By design, but it reads like an error.** Spending is what makes Tidal Flourish Hydro. If the rarity moves (pick 2), the plain mode can apply Hydro too |
| Second Energy | Interval Bell and Salon's Tab turn Fanfare or HP into next-turn Energy | **Fine for now.** Two cards out of 34 |

**Seats against humans.** The solo seat rounds found the opposite problem:
HP was the bottleneck in act 3. Both seats fell to 10–12 HP at the Soul Nexus
elite, and one died with every Drain card shut off
(`review/records/furina-pool40-round-2026-10-05.md`). Co-op does not explain
the gap, since every enemy hits every player. Skilled human piloting and a
partner who shortens fights are the likelier causes. So the trims are small,
and a solo seat round with an Ironclad control will read them.

## Klee

[USER] drafted several cards that make Sparks but never found a payoff for
them. He then built a support engine instead: statuses and card draw, to fire
Set Off and Pyro reactions at the right moment. "She felt fine," but with
Furina carrying, her balance is hard to judge. **Follow-up, no pick needed:**
the card-offer log (`tools/offer_report.py`) already runs on seat lanes.
The next Klee suite will show whether Spark payoffs are offered and passed,
or never offered, the same question the Varka round answered.

## Picks

**Ruled 2026-10-09, all defaults.** [USER]: "Good on the defaults for now - we
can start with these trims and readjust after the card pool expands."

1. **Salon Solitaire: Repay 2 → Repay 1** (the Orobas upgrade 3 → 2). **Default: yes.**
2. **Common trims:**
   - Interval Bell becomes Uncommon.
   - Gentilhomme Usher: 7 / Drain 3: 13 → 6 / Drain 3: 11 [8 / 14].
   - Tidal Flourish becomes Uncommon, and its plain mode applies Hydro.
     That leaves two Common AoE attacks.

   **Default: all three.**
3. **The Drain line.**
   - (a) Keep the line at half her entering HP and see whether picks 1 and 2
     are enough.
   - (b) The friend's idea: she can always Drain down to 1 HP. A Five-Century
     Act would then be replaced by a different Rare.

   (b) makes Drain dangerous and removes her one cap. It also gives every
   deck more power, and the solo seats were already short of HP in act 3.
   **Default: (a) on the build. Claude also sims (b) against (a) on the
   solo instrument and brings back the numbers before any build.**
4. **Guests become an archetype, in the pool-growth paper.** Her pool grows
   from 34 toward 78 after her Tab play, and this was that play. The paper
   gives Guests a way to scale, such as cards that spend Fanfare to make a
   guest act harder or again, and adds scaling outside Fanfare. **Default:
   yes, Claude writes the paper next.**
5. **Max HP stays 78** until a solo round shows she never reaches her
   line. **Default: yes.**
